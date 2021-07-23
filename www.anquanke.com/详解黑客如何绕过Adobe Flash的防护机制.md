> 原文链接: https://www.anquanke.com//post/id/99918 


# 详解黑客如何绕过Adobe Flash的防护机制


                                阅读量   
                                **148070**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Hardik Shah，文章来源：securingtomorrow.mcafee.com
                                <br>原文地址：[https://securingtomorrow.mcafee.com/mcafee-labs/hackers-bypassed-adobe-flash-protection-mechanism/](https://securingtomorrow.mcafee.com/mcafee-labs/hackers-bypassed-adobe-flash-protection-mechanism/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t014ec043b9202b6039.png)](https://p1.ssl.qhimg.com/t014ec043b9202b6039.png)



## 一、前言

由于Adobe采取了各种措施来加强Flash的安全性，因此最近Flash Player的漏洞数量有所下降，然而Flash Player偶尔还是会有新的漏洞冒出来。1月31日，Kr-Cert[报告](https://www.krcert.or.kr/data/secNoticeView.do?bulletin_writing_sequence=26998)了该领域新出现的一个漏洞，漏洞编号为CVE-2018-4878（Adobe已经公布了一个[安全更新](https://blogs.adobe.com/psirt/?p=1522)修复了此漏洞）。经过分析后，我们发现漏洞利用技术可以绕过Flash引入的字节数组（byte array）缓解功能，而这种功能可以阻止针对Flash的“长度损坏（length corruption）”攻击。本文将重点讨论漏洞利用技术如何绕过这种长度检查机制。



## 二、利用原理

[![](https://p0.ssl.qhimg.com/t0179f9486ec7895e62.png)](https://p0.ssl.qhimg.com/t0179f9486ec7895e62.png)

攻击者已经在[针对性攻击活动](https://helpx.adobe.com/security/products/flash-player/apsa18-01.html)中用到了这种漏洞，当时攻击者使用了嵌有Flash文件的Microsoft Office Excel文件。一旦用户打开Excel文件，Flash文件则会与服务器建连，请求密钥。收到密钥后，该文件会解码另一个内嵌的Flash文件，而该文件是真正的漏洞利用文件。

[![](https://p2.ssl.qhimg.com/t01e52dde2eaa4dc201.png)](https://p2.ssl.qhimg.com/t01e52dde2eaa4dc201.png)

密钥大小为100字节。恶意程序使用`loader.loadbyte`函数来解码并加载内嵌的文件：

[![](https://p5.ssl.qhimg.com/t01546340b1a4b3bf4f.png)](https://p5.ssl.qhimg.com/t01546340b1a4b3bf4f.png)

由于密钥所使用的URL地址已经下线，我们无法获取该密钥，然而各种网站上都存在样本的哈希值。本文所分析样本的SHA-256哈希值为`1a3269253784f76e3480e4b3de312dfee878f99045ccfd2231acb5ba57d8ed0d`。

这个Adobe `.SWF`文件包含多个ActionScript 3文件，也在BinaryData区中包含2个嵌入式文件，这些文件共同构成了最终的shellcode（如下图红色方框所示）：

[![](https://p3.ssl.qhimg.com/t018d79eb55f21e50a3.png)](https://p3.ssl.qhimg.com/t018d79eb55f21e50a3.png)



## 三、开始利用

漏洞利用程序启动时会检查所运行的系统是否为Windows系统，如果满足条件就会触发漏洞。

[![](https://p5.ssl.qhimg.com/t01d4f863d56de9f7f5.png)](https://p5.ssl.qhimg.com/t01d4f863d56de9f7f5.png)

漏洞利用程序会执行如下几个步骤：

1、创建一个mediaplayer对象；

2、将mediaplayer的drmManager属性初始化为基于DRMOperationCompleteListener对象nugamej的一个精心构造的类；

3、虽然nugamej对象已经被“释放”，但drmManager会指向nugamej之前所使用的那一个内存地址。

如果我们仔细观察nugamej，我们可以看到它源自于Rykim类，而该类实现（implement）了DRMOperationCompleteListener类。Rykim类中有各种“uint”类型的变量，这些变量的值分别为0x1111、0x2222等：

[![](https://p5.ssl.qhimg.com/t0166c18b87971ac898.png)](https://p5.ssl.qhimg.com/t0166c18b87971ac898.png)

这些变量稍后将用来访问进程空间以及其他操作所对应的各种地址。

漏洞利用程序随后会使用`Localconnection().connect`来触发异常，创建Rykim类的一个新变量“katyt”，并且实现了DRMOperationCompleteListener类，通过计时器（timer）来调用“cysit”方法：

[![](https://p1.ssl.qhimg.com/t01911eedf63b04f7ce.png)](https://p1.ssl.qhimg.com/t01911eedf63b04f7ce.png)

Cysit函数会检查新分配对象的`a1`变量值是否为`0x1111`，如果不相等，则cysit函数会停止计时器，继续漏洞利用过程。

漏洞利用程序会创建另一个对象，即“Qep,”类型的“kebenid”，该对象会扩展字节数组类。kebenid的大小为512字节。程序稍后会修改这个大小，通过“读-写”方法获得进程内存的无限制访问权限。



## 四、检查字节数组避免损坏

我们可以查看[https://github.com/adobe/avmplus/blob/master/core/ByteArrayGlue.h了解字节数组的结构。](https://github.com/adobe/avmplus/blob/master/core/ByteArrayGlue.h%E4%BA%86%E8%A7%A3%E5%AD%97%E8%8A%82%E6%95%B0%E7%BB%84%E7%9A%84%E7%BB%93%E6%9E%84%E3%80%82)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0131acfb1dc255979c.png)

可以看到，字节数组类存在数组（array）、容量（capacity）以及长度（length）等特性。之前我们曾见到过攻击者通过破坏长度变量实现对某个内存地址的任意读取及写入。因此，代码中部署了额外的检查过程来确保字节数组的完整性。检查过程会创建一个密钥，这个值会与数组/容量/长度进行异或（XOR）处理，然后分别保存在check_array/check_capacity/check_length变量中。

当访问这些变量时，程序会将这些变量与密钥进行异或处理，然后将变量的值与存储在check_array/check_capacity/check_length中的值进行比较。如果匹配成功，则属于正确的数据，否则就会抛出异常，如下图所示：

[![](https://p1.ssl.qhimg.com/t015dde0e189125113a.png)](https://p1.ssl.qhimg.com/t015dde0e189125113a.png)



## 五、绕过检查过程

根据前面的代码，我们可以使用如下计算过程来提取密钥，即：

```
Array ^ check_array = key
Capacity ^ check_capacity = key
Length ^ check_length = key
```

[https://github.com/adobe/avmplus/blob/master/core/ByteArrayGlue.h还提到一种方法，如下所示：](https://github.com/adobe/avmplus/blob/master/core/ByteArrayGlue.h%E8%BF%98%E6%8F%90%E5%88%B0%E4%B8%80%E7%A7%8D%E6%96%B9%E6%B3%95%EF%BC%8C%E5%A6%82%E4%B8%8B%E6%89%80%E7%A4%BA%EF%BC%9A)

[![](https://p5.ssl.qhimg.com/t019ca53b6447b749a0.png)](https://p5.ssl.qhimg.com/t019ca53b6447b749a0.png)

如果copyOnWrite的值为0，那么密钥就等于check_copyOnWrite。

如果我们仔细观察，我们会发现katyt以及kebenid对象变量指向的是同一块内存地址。如果我们打印出这些信息，比较两个对象的变量，我们就能证实这一点。

将如下变量与字节数组结构进行对比，我们可以得到如下结果：

[![](https://p5.ssl.qhimg.com/t01330b73537a056a5c.png)](https://p5.ssl.qhimg.com/t01330b73537a056a5c.png)

因此，如果我们修改`katyt.a24`以及`katyt.a25`，实际上修改的是字节数组的容量以及字节数组的长度。接下来来我们只需要找到XOR的密钥，就能将数组长度设置为任意长度。

在这个利用程序中，攻击者通过`Array ^ check_array = key`算出了密钥值。

得到密钥后，我们很容易就能将字节数组的容量以及长度修改为`0xFFFFFFFF`以及check_length，这样就能绕过字节数组的安全机制，也就能读取或写入进程空间中的任意地址。

[![](https://p2.ssl.qhimg.com/t01e871671d1e303a8b.png)](https://p2.ssl.qhimg.com/t01e871671d1e303a8b.png)



## 六、代码执行

漏洞利用程序通过字节数组对象的这种“读-写”方法成功读取了内存数据，搜索`kernel32.dll`以及类似`VirtualProtect`、`CreateProcessA`之类的函数。一旦定位到这些函数的地址，就可以在目标系统上执行shellcode。这种技术网上已经有很多公开文档。恶意程序搜索`kernel32.dll`、定位VirtualProtect API地址（即0x75ff2c15）的代码片段如下所示：

[![](https://p1.ssl.qhimg.com/t013f9ab7c652bea328.png)](https://p1.ssl.qhimg.com/t013f9ab7c652bea328.png)

随后，漏洞利用程序会执行shellcode，连接到某个URL地址：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0160c6003364b17159.png)

也会通过`CreateProcessA`函数启动`cmd.exe`：

[![](https://p2.ssl.qhimg.com/t01df2c3c44c29b3f46.png)](https://p2.ssl.qhimg.com/t01df2c3c44c29b3f46.png)

shellcode同时也会检查某些反恶意软件产品：

[![](https://p2.ssl.qhimg.com/t01508576e25792a378.png)](https://p2.ssl.qhimg.com/t01508576e25792a378.png)



## 七、总结

攻击者会不断寻找绕过新型防护机制的各种办法。本文分析的这个漏洞利用程序给我们提供了一个鲜活的案例。与往常一样，我们建议大家在打开电子邮件中的未知附件和文档时要格外小心。

McAfee网络安全平台（Network Security Platform）的客户已经得到保护，可以免受这种漏洞的影响（特征ID为0x45223900）。



## 八、IoC

**哈希值（SHA-256）**

```
1a3269253784f76e3480e4b3de312dfee878f99045ccfd2231acb5ba57d8ed0d
```

**URL**

```
hxxp://www.korea-tax.info/main/local.php
hxxp://www.1588-2040.co.kr/conf/product_old.jpg
hxxp://1588-2040.co.kr/conf/product.jpg
```

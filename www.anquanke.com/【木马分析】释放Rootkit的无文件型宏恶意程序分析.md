
# 【木马分析】释放Rootkit的无文件型宏恶意程序分析


                                阅读量   
                                **99492**
                            
                        |
                        
                                                                                                                                    ![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****

[![](./img/85527/t01162da88ebc4414cd.jpg)](./img/85527/t01162da88ebc4414cd.jpg)

作者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**介绍**

正当海湾合作委员会（GCC，Gulf Cooperation Council）成员国疲于应付Shamoon恶意软件时，他们的服务器又遭受了一种全新的垃圾邮件的攻击。这种VB宏形式恶意文档看起来是像是经过全新编写或改造的，至少在本文成稿时，还没在任何地方发现它的活动踪迹。

有多个GCC成员国组织收到过几封嵌有恶意文档附件的垃圾邮件，该文档能够躲避所有的安全检测并成功投递到受害者收件箱中，一个样本信息如下图所示：

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e371c9d61d616625.png)

即使不打开该文档，通过文档的属性信息我们还是可以猜测出它是一份恶意文件。文档属性信息如下图：

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017af7a4953fa54420.png)

打开文档后，Word提示文档宏已经被禁用，而文档内容则诱骗用户启用Word宏功能，如下图：

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010d03875087b9236a.png)

<br>

**恶意文档分析**

我们直接跳到宏代码分析部分：

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c43aeb9b197249a4.png)

其中“Document_Open ()”函数使得宏脚本在用户打开文档时就会自动运行。

当我们对代码进行静态分析时，我们发现一些有用的代码片段，细查这些片段，可以看到一些经过编码的字符串会被传递给“RraiseeventR”函数，返回结果会存放在另一个变量中。

我们还可以看到许多这样的变量，而“RraiseeventR”函数往往一同出现。因此我们猜测函数与解密流程有关。

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01317fc58191577b03.png)

“RraiseeventR”函数的部分代码如下所示：

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d5295d79da3c0758.png)

经过进一步的静态分析，我们可以发现所有的变量会拼接汇聚起来。脚本调试的主要优点就在于可以利用代码自身来对编码部分进行解码或解密。

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018769e0992b943712.png)

对这些变量值进行解码后，它们的功能也逐步清晰起来。整体看来，它们应该是PowerShell脚本，其中还包含“URL”信息。

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bc57c3de1980af23.png)

所有的变量拼接起来形成“inEmptyMe”变量，内容是一个完整的PowerShell脚本。

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01598503f49933f1ab.png)

将PowerShell脚本从变量中提取出来，规范化格式以便阅读。分析该PowerShell代码可知，其功能是文件的下载执行。

进一步分析的话，我们还以发现代码中有个潜在的策略，能够绕过UAC及其他检测。

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b8a34400f405c04f.png)

代码工作过程分析如下：

1） 隐式调用powershell.exe，进行变量的赋值工作。$wscript变量指向WScript.Shell，用于运行带参数的shell命令；

2）定义$webclient变量，用来从给定的URI上传或下载数据。每个web client调用可通过web请求类来实现，如“DownloadFile”类（比如WebClient.DownloadFile 或WebClient.UploadFile）；

3）定义$random变量用来产生1到65535之间的随机数；

4）定义$urls变量，指向一或多个可执行文件的恶意网址。这代表脚本可作为下载器，执行其他文件。

5）下载文件被重命名为随机数字字符串，以.exe后缀名结尾，保存在“temp“文件夹中。

6）定义$hkey变量，值为“HKCUSoftwareClassesmscfileshellopencommand“。

7）接下来，脚本访问指定的URL，下载可执行文件，按步骤5）重命名并保存到临时文件夹中。

至此，该PowerShell脚本使用的策略已跃然纸上，也就是使用无文件形式的UAC绕过方法，利用注册表获得系统最高权限。

仔细研读代码后，读者心里可能会有两个问题：

1）为什么脚本要修改注册表“HKCUSoftwareClassesmscfileshellopencommand“键值，将可执行恶意文件路径添加该键值中？

2）为什么脚本需要利用“eventvwr.exe“？

其实这两者之间存在很大的关联性。让我们将视角聚焦到时间处理器（event viewer）以及该注册表键值上。

打开注册表读取该键值，我们可以看到键值指向了“mmc.exe“（Microsoft Management微Console，软管理控制台）的所在路径。

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01054ed50e4a9d9c62.png)

“mmc.exe“用来打开.msc文件（Microsoft Saved Consoles），比lusrmgr.msc、eventvwr.msc等。

通常我们运行eventvwr.exe时，它首先会访问注册表“HKCUSoftwareClassesmscfileshellopencommand“键值，询问mmc.exe所在地址。

不幸的是，查询结果是值不存在（NAME NOT FOUND）。

在注册表中，“HKEY_CLASSES_ROOT“是”HKEY_LOCAL_MACHINESOFTWAREClasses“和”HKEY_CURRENT_USERSoftwareClasses“两者的结合。

因此，当eventvwr.exe无法从HKCU中获取该值时，它会立刻查询HKCR中对应的键值，并且在第二次查询时成功获取该值。如下所示：

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01956e58095ed3eb0e.png)

eventvwr.exe通过注册表启动mmc.exe，mmc再通过GUI图形界面向用户呈现eventvwr.msc，如下所示：

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018b1c9ec71d9df822.png)

此外，查看eventvwr.exe的manifest信息，可以发现它以最高执行权限运行，并且会自动提升运行权限，如下图所示：

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011bb808799945f01d.png)

现在回到我们的恶意样本分析工作，该恶意PowerShell脚本篡改该HKCU键值，将其修改为已下载的恶意可执行文件路径，然后使用eventvwr.exe触发恶意程序的运行。

该过程最终导致恶意程序得以借助事件查看器以最高权限运行。

我们允许该文档的宏功能，复现以上分析过程。

如我们预期，Power Shell首先被触发，从远程主机下载恶意程序，以随机名保存在临时目录中，通过eventvwr和mmc运行该恶意程序，如下图所示：

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b2a6444018972af6.png)

我们还可以看到恶意软件正以高权限运行，软件的任何操作也会运行在高权限状态下。

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e9dfa8800279bfb6.png)

至此，恶意文档的使命达成，将指挥权交给所下载的恶意软件。

简单小结一下，恶意文档感染后，通过PowerShell脚本下载另一个恶意软件，通过事件查看器和MMC注册表键值成功绕过UAC限制，以高权限运行。

<br>

**恶意软件分析**



经过初步分析，我们发现恶意软件具有高超的环境检测功能，可以检测虚拟机、调试器和其他监控工具是否存在。同时，它也是一个Rootkit形式的信息窃取工具。

恶意软件运行后，会释放一个批处理脚本，当软件检测到自身正在被分析时，脚本会进行自删除操作，防止被取证分析。脚本释放在软件运行的当前临时目录中，同样也是以高权限运行。

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012b4c90115c22674e.png)

脚本内容如下：

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011914693722e6b2dd.png)

恶意软件将一个vb脚本文件释放到启动文件夹中，以达到本地持久化目的。每次机器重启时，恶意软件会借由该脚本重新运行。

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0150058e96be633393.png)

利用调试器分析恶意软件，可以从中找到一些有趣的字符串，比如“Welcome to China!”、“Progman”等。软件采用了结构化异常处理机制（Structured Exception handler）来防止被逆向分析。

[![](./img/85527/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/021317_2318_NewBornMacr24.png)

此外，恶意软件使用了某些防分析的API调用方法，包括GetTickCount、IsDebuggerPresent、CreateToolhelp32Snapshot、FindWindowA等。后续可进一步深入分析该恶意软件的工作过程。

<br>

**总结**



恶意软件的以上所有行为仅在用户允许文档运行宏时才会发生，这也是安全公司和安全顾问始终在讨论恶意软件防范中培养“用户意识”的原因。

现在越来越多的垃圾邮件使用恶意文件、嵌入宏或OLE对象的恶意文档开展攻击，Shamoon APT的第三波垃圾邮件攻击行为也已见诸报道。

培养“用户意识”后，我们还可以在端点部署某些小型安全措施，比如禁止临时文件夹中的任意文件运行，就可以防止很多这种类型的感染。

<br>

**参考资料**

[https://cysinfo.com/](https://cysinfo.com/) 

[https://zeltser.com/analyzing-malicious-documents/](https://zeltser.com/analyzing-malicious-documents/) 

[https://digital-forensics.sans.org/blog/2009/11/23/extracting-vb-macros-from-malicious-documents/](https://digital-forensics.sans.org/blog/2009/11/23/extracting-vb-macros-from-malicious-documents/) 

[https://enigma0x3.net/](https://enigma0x3.net/) 

[https://blog.malwarebytes.com/threat-analysis/2015/10/beware-of-doc-a-look-on-malicious-macros/](https://blog.malwarebytes.com/threat-analysis/2015/10/beware-of-doc-a-look-on-malicious-macros/) 

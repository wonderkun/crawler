> 原文链接: https://www.anquanke.com//post/id/86131 


# 【木马分析】关于Emotet变种的深入分析（一）


                                阅读量   
                                **87044**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p4.ssl.qhimg.com/t0134e61413842993b1.jpg)](https://p4.ssl.qhimg.com/t0134e61413842993b1.jpg)**

****

翻译：[**興趣使然的小胃**](http://bobao.360.cn/member/contribute?uid=2819002922)

**稿费：200RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**传送门**

[**【木马分析】关于Emotet变种的深入分析（二）**](http://bobao.360.cn/learning/detail/3878.html)

**<br>**

**一、背景**

前几天，FortiGuard实验室捕捉到了某个恶意JS文件，该JS文件充当恶意软件下载器功能，用来传播Emotet木马的新变种。JS文件的原始文件名为“Invoice__779__Apr___25___2017___lang___gb___GB779.js”。JS文件就是JavaScript文件，可以通过鼠标双击，使用Windows脚本宿主程序（Windows Sciprt Host，wscript.exe）加以执行。在本文中，我们会按照时间顺序，逐步深入分析这个新型恶意软件变种。

<br>

**二、传播恶意软件的JS文件**

原始的JS代码经过混淆处理，因此难以直接理解。根据我的分析，它的任务是产生一段新的JS代码，存储在数组中，然后再执行这段代码。新生成的代码更容易理解，其代码片段如图1所示。正如我提到的，这段代码充当下载器角色，试图访问5个URL，将恶意软件下载到被感染的设备上。一旦某个下载任务完成，恶意软件会将下载的文件保存为系统临时目录中的“random name.exe”，并加以执行。

[![](https://p1.ssl.qhimg.com/t0122fbe70aa17418fa.png)](https://p1.ssl.qhimg.com/t0122fbe70aa17418fa.png)

图1. 所生成的JS代码的部分片段

<br>

**三、运行下载的EXE文件**

下载的EXE文件运行时，会将自身移动到“%LocalAppData%random namerandom name.exe”，其中“random name”会使用本地文件名生成的随机名进行替换。在我的测试环境中，该样本文件名为“LatnParams.exe”。

为了保护自身运行，LatnParams.exe在运行时，会从自身中提取代码，使用CREATE_SUSPENDED标识调用CreateProcessW函数，将代码插入新创建的LatnParams.exe中，然后再恢复运行第二个进程。这些操作完成后，第一个进程就会退出。接下来，LatnParams.exe会在系统开始菜单的启动目录（Startup folder）中创建指向自己的lnk文件，以便在系统启动时自动运行。如图2所示。

[![](https://p1.ssl.qhimg.com/t01da11b4f6316fe2ef.png)](https://p1.ssl.qhimg.com/t01da11b4f6316fe2ef.png)

图2. 启动目录中的恶意软件

<br>

**四、第二个进程的主函数**

接下来，我们来看看这个代码创建的第二个进程的具体工作流程。第二个进程创建了一个隐藏窗口，它的WindowProc函数功能是处理这个窗口接收的所有Windows消息。这个恶意软件通过调用SetTimer函数，生成WM_TIMER消息来启动第二个进程。

窗口创建完毕后，WindowProc函数会收到一个WM_CREATE消息，然后调用SetTimer函数，使系统每隔200ms发布WM_TIMER消息，再次回调窗口的WindowProc函数。

[![](https://p1.ssl.qhimg.com/t0197f9cc4d8d5b055e.png)](https://p1.ssl.qhimg.com/t0197f9cc4d8d5b055e.png)

图3. 调用SetTimer函数

下面我们来看看这个WindowProc函数。这个函数的伪代码如图4所示。

[![](https://p2.ssl.qhimg.com/t014c51cd352553c5bd.png)](https://p2.ssl.qhimg.com/t014c51cd352553c5bd.png)

图4. WindowProc函数

<br>

**五、Case 6代码分支**

在图4代码的Case 6分支中，恶意软件从目标设备上收集系统信息，包括计算机名、国别名、所有正在运行的进程名以及微软Office Outlook是否安装的相关信息。之后恶意软件将收集到的所有信息存放到某个内存缓冲区中再进行加密。正准备加密的数据如图5所示。

[![](https://p5.ssl.qhimg.com/t01049773bcb0e01504.png)](https://p5.ssl.qhimg.com/t01049773bcb0e01504.png)

图5. 从受害者系统上收集的信息

我们可以看到，这些信息的第一部分是计算机名，后面的“16 00 01 00”代表的是CPU信息。接下来是正在运行的进程名，之后的“Microsoft Outlook”字段表明这台主机中安装了微软Office Outlook软件。你可能还会注意到进程列表中包含“OllyDBG.exe”。根据我的分析，我发现恶意软件的命令控制（C&amp;C）服务器会检查进程名，如果服务器发现受害者主机上正在运行与调试工具有关的进程（如OllyDbg、WinDbg、IDA Pro等），那么它会返回不同的响应。在本文案例中，服务器返回了新版本的恶意软件，使恶意软件自身不断升级，直至这些调试工具退出为止。

加密完成后，恶意软件将加密过的数据、加密密钥以及哈希值一起存放到一个新创建的缓冲区中，之后会进入case 7代码分支中。

<br>

**六、Case 7代码分支**

这个分支的主要功能是连接到C&amp;C服务器，将已收集的数据发送给服务器，同时也会接收C&amp;C服务器返回的数据。

C&amp;C服务器的IP及端口信息都被硬编码在恶意软件中。这个版本的恶意软件中共包含11个相关地址，如下所示：



```
004175D0                ; DATA XREF: WindowProc+257r
004175D0                ;sub_403AE0+Co
004175D0  dd 0D453A62Dh ;212.83.166.45
004175D4  dd 1F90h      ;8080
004175D8  dd 0ADE68843h ;173.230.136.67
004175DC  dd 1BBh       ;443
004175E0  dd 0ADE0DA19h ;173.224.218.25
004175E4  dd 1BBh       ;443
004175E8  dd 68E38922h  ;104.227.137.34
004175EC  dd 1BA8h      ;7080
004175F0  dd 894AFE40h  ;137.74.254.64
004175F4  dd 1F90h      ;8080
004175F8  dd 0BCA5DCD6h ;188.165.220.214
004175FC  dd 1F90h      ;8080
00417600  dd 558FDDB4h  ;85.143.221.180  
00417604  dd 1BA8h      ;7080
00417608  dd 77521BF6h  ;119.82.27.246
0041760C  dd 1F90h      ;8080
00417610  dd 0C258F607h ;194.88.246.7
00417614  dd 1F90h      ;8080
00417618  dd 0CED6DC4Fh ;206.214.220.79
0041761C  dd 1F90h      ;8080
00417620  dd 68EC02FDh  ;104.236.2.253
00417624  dd 1BBh       ;443
```

函数会提取case 6分支中生成的数据，使用base64编码这些数据，然后将编码后的数据作为Cookie值发送给C&amp;C服务器。使用Wireshark抓取的传输报文如图6所示：

[![](https://p5.ssl.qhimg.com/t0177fc22000d0e6b60.png)](https://p5.ssl.qhimg.com/t0177fc22000d0e6b60.png)

图6. 将已收集的系统信息发送给C&amp;C服务器

图6中，C&amp;C服务器返回报文的状态码为“404 Not Found”。服务器使用这种响应报文来迷惑安全分析人员，然而报文的body部分是可用的加密过的数据。服务器返回的数据接收完毕后，恶意软件会进入Case 8代码分支中。

<br>

**七、Case 8代码分支**

这个分支唯一的功能就是解密Case 7中收到的加密数据，然后进入Case 9代码分支中。

<br>

**八、Case 9代码分支**

这个分支用来处理Case 8解密后的数据。该分支对应的伪代码如图7所示：

[![](https://p0.ssl.qhimg.com/t01ac853973418f4131.png)](https://p0.ssl.qhimg.com/t01ac853973418f4131.png)

图7. Case 9的伪代码

Case 9分支中存在一些子分支，其中“v8”分支来自于已解密的数据。以下是已解密数据的两个示例。

图8中，“08 01”代表的是具体的子分支。“08”是某种标识或者C&amp;C命令，“01”指的是子分支编号1。从图8中，你很容易猜到这部分数据是一个.exe文件。在子分支1中，这个文件会被执行，以升级Emotet恶意软件。通常情况下，恶意软件会收到一个升级命令，因为C&amp;C服务器已检测到受害者主机中正在运行的程序名中包含调试相关工具。恶意软件使用这种方法来保护自身不被调试，也用来迷惑安全分析人员。在子分支1中，恶意软件会将.exe文件保存到系统临时目录中，然后调用ShellExecuteW函数执行这个文件。与此同时，父进程会退出以便完成升级流程。

[![](https://p4.ssl.qhimg.com/t01fc3ea186b8de3bce.png)](https://p4.ssl.qhimg.com/t01fc3ea186b8de3bce.png)

图8. 子分支1示例

[![](https://p1.ssl.qhimg.com/t0161ddc43d1f7e92fb.png)](https://p1.ssl.qhimg.com/t0161ddc43d1f7e92fb.png)

图9. 子分支4示例

在加密流程开始前（见图5），我手动将“OllyDBG.exe”修改为另一个程序名。之后服务器返回的报文如图9所示。相应的标识变成了“08 04”，其中“04”指的是子分支4。在我们的分析中，已解密的数据中包含3个模块（.dll文件），这些文件的标识都为“08 04”，表明这些模块都会在子分支4中进行处理。如图7所示，子分支4会调用CreateThread函数，创建线程，并在某个线程函数（ThreadFunction）中运行这些模块，每个线程负责一个模块的运行。

Emotet包含三个模块，目前为止，我们只完成了其中一个模块的分析工作。我们会在另一篇文章中分析其他模块。

接下来，我们可以看一下这个模块的具体功能。

<br>

**九、线程中加载的模块**

根据我的分析，这个模块会窃取受害者主机中的凭证信息，对这些信息进行加密，然后发往C&amp;C服务器。

当该模块在ThreadFunction中加载完成后，会从自身提取代码，并将代码插入到一个新创建的LathParams.exe进程中加以运行。新创建的进程带有一个形如“%temp%A98b.tmp”的命令行参数，“A98b.tmp”是一个临时文件，用来保存已窃取的凭证信息。

该模块可以窃取诸如Google账户、IE中保存的FTP账户、Google Talk、Office Outlook、IncrediMail、Group Mail、MSN Messenger、Mozilla Thunderbird等的凭证信息。部分凭证如下图所示：

[![](https://p1.ssl.qhimg.com/t01a75953fb619effae.png)](https://p1.ssl.qhimg.com/t01a75953fb619effae.png)

图10. 与邮箱有关的凭证信息

出于测试目的，我在微软Office Outlook中添加了一个测试账户，研究该模块如何工作。该账户的凭证如图11所示：

[![](https://p1.ssl.qhimg.com/t012fe0ea0b0cc61dcd.png)](https://p1.ssl.qhimg.com/t012fe0ea0b0cc61dcd.png)

图11. 添加到Outlook中的测试账户

已窃取的数据会保存在命令行参数所指定的临时文件中，并会在ThreadFunction中进行加密、发往C&amp;C服务器。临时文件中的凭证信息、内存中加密前的数据以及发往C&amp;C服务器的数据分别如图12、图13及图14所示：

[![](https://p3.ssl.qhimg.com/t0133f1902af1644811.png)](https://p3.ssl.qhimg.com/t0133f1902af1644811.png)

图12. 已窃取的凭证

[![](https://p1.ssl.qhimg.com/t013f0131d1a5ee5e56.png)](https://p1.ssl.qhimg.com/t013f0131d1a5ee5e56.png)

图13. 加密前的数据

[![](https://p0.ssl.qhimg.com/t0141cdadaa50004d3a.png)](https://p0.ssl.qhimg.com/t0141cdadaa50004d3a.png)

图14. 发往C&amp;C服务器的数据

<br>

**十、解决方案**

FortiGuard反病毒服务已将原始的JS文件标记为JS/Nemucod.F436!tr，该文件下载的Emotet程序已被标记为W32/GenKryptik.ADJR!tr。

**<br>**

**十一、攻击指示器（IoC）**

**URL地址：**



```
"hxxp://willemberg.co.za/TwnZ36149pKUsr/"
"hxxp://meanconsulting.com/K44975X/"
"hxxp://microtecno.com/i17281nfryG/"
"hxxp://thefake.com/Y96158yeXR/"
"hxxp://cdoprojectgraduation.com/eaSz15612O/"
```

**样本的SHA256哈希值：**



```
Invoice__779__Apr___25___2017___lang___gb___GB779.js：
B392E93A5753601DB564E6F2DC6A945AAC3861BC31E2C1E5E7F3CD4E5BB150A4
```





**传送门**

[**【木马分析】关于Emotet变种的深入分析（二）**](http://bobao.360.cn/learning/detail/3878.html)



> 原文链接: https://www.anquanke.com//post/id/86320 


# 【技术分享】针对巴基斯坦的某APT活动事件分析


                                阅读量   
                                **146844**
                            
                        |
                        
                                                                                    



**[![](https://p0.ssl.qhimg.com/t01f7382b1e65a52161.png)](https://p0.ssl.qhimg.com/t01f7382b1e65a52161.png)**

**<br>**

**事件背景<br>**

2017年6月， 360威胁情报中心发现了一份可疑的利用漏洞执行恶意代码的Word文档，经过分析后，我们发现这有可能是一起针对巴基斯坦的政府官员的APT攻击事件，释放出来的载荷会收集受害者的键盘记录和重要软件密码、文档等。本文档对并对此次攻击事件的攻击链条进行梳理，并对使用的木马相关技术进行分析。

<br>

**样本分析**

**漏洞利用Dropper**

**[![](https://p3.ssl.qhimg.com/t0143bed0d2fb127f43.png)](https://p3.ssl.qhimg.com/t0143bed0d2fb127f43.png)**

该文档所利用的漏洞为CVE-2015-2545（关于该漏洞的分析已经有不少详细分析的资料，这里就不再赘述），当受害者点开该文档时，会加载EPS文件从而触发漏洞，这里攻击者使用的漏洞利用代码是已经在野外流传很久的成熟利用，这套利用的特点是通过shellcode注入explorer进程下载木马文件，但shellcode后附加一个DLL文件以利用CVE-2015-2546权限提升漏洞得到系统最高权限。

注入explorer.exe的代码如下：

[![](https://p0.ssl.qhimg.com/t01d06915af20be576e.png)](https://p0.ssl.qhimg.com/t01d06915af20be576e.png)

explorer.exe中下载载荷的代码如下：可以看到下载地址为http://tes[.]sessions4life[.]pw/quiz/WelcomeScrn.exe

[![](https://p0.ssl.qhimg.com/t018d0aed4d6aee851b.png)](https://p0.ssl.qhimg.com/t018d0aed4d6aee851b.png)

CVE-2015-2546权限提升DLL部分代码：

[![](https://p1.ssl.qhimg.com/t01cefd8d4ffadd0aec.png)](https://p1.ssl.qhimg.com/t01cefd8d4ffadd0aec.png)

**WelcomeScrn.exe**

[![](https://p2.ssl.qhimg.com/t018a2b5d3b27dc11d0.png)](https://p2.ssl.qhimg.com/t018a2b5d3b27dc11d0.png)

这是个downloader，功能非常简单，直接连接到内置网址http://185[.]109[.]144[.]102/DistBuild/DefenderReference.exe ，下载并执行文件。

[![](https://p0.ssl.qhimg.com/t01acecf5d22ebb54ae.png)](https://p0.ssl.qhimg.com/t01acecf5d22ebb54ae.png)



**DefenderReference.exe**

[![](https://p3.ssl.qhimg.com/t01aaa8bfb32c7c2215.png)](https://p3.ssl.qhimg.com/t01aaa8bfb32c7c2215.png)

DefenderReference.exe通过HTTP协议与服务器通信的窃密木马，被执行起来后，会先完成一些初始化的工作，释放并加载WER167893459067.dll后创建以下目录：<br>

%Local%SharedFilesLog

% Local % SharedFiles Sys

% Local % SharedFiles Temp

% Local % SharedFiles WinAero

% Local % SharedFiles WinDataShots

% Local % SharedFiles WinInternetData

% Local % SharedFiles WinLog

% Local % SharedFiles WinRM

然后终止cmd.exe、PATHPING.EXE、TRACERT.EXE、net.exe、systeminfo.exe进程,并判断自身进程启动路径是否为% Local % SharedFiles Sys，如果不是，则将自身拷贝到% Local % SharedFiles Sys DefenderReference.exe，释放MSOBuild.exe、AdminNewDll.dll、AdminServerDll.dll等文件，最后启动MSOBuild.exe

 [![](https://p4.ssl.qhimg.com/t0179280ab591e805d2.png)](https://p4.ssl.qhimg.com/t0179280ab591e805d2.png)

[![](https://p2.ssl.qhimg.com/t015493b73ed5e1f1e5.png)](https://p2.ssl.qhimg.com/t015493b73ed5e1f1e5.png)

**MSOBuild.exe**

[![](https://p5.ssl.qhimg.com/t01656b588b1478081e.png)](https://p5.ssl.qhimg.com/t01656b588b1478081e.png)

这个文件其实还是个downloader，在初始化和检查执行环境（虚拟机、沙箱、调试）后，访问http://docs.google.com/uc?id=0Bx9cf6a5Mapaa3g4MlI4T244SlU&amp;export=download,获取C&amp;C的地址185.109.144.102

接着下载以下配置文件：

hxxp://185[.]109.144.102/DistBuild/getAllFiles.php(指明需要下载的组件)

http://185[.]109.144.102/DistBuild/getExecutables.php (指明要执行的组件)

http://185[.]109.144.102/DistBuild/getExtensions_doc.php (指明关心的文档类型文件后缀名)

http://185[.]109.144.102/DistBuild/ getExtensions_nondoc.php (指明关心的非文档文件类型)

http://185[.]109.144.102/DistBuild/getExtensions_rmdrive.php (指明要执行的组件)

[![](https://p4.ssl.qhimg.com/t01394306626bc32c40.png)](https://p4.ssl.qhimg.com/t01394306626bc32c40.png)

接着下载配置文件中指定的组件，再一一启动这些组件：

[![](https://p4.ssl.qhimg.com/t01beb3bad13242bf4a.png)](https://p4.ssl.qhimg.com/t01beb3bad13242bf4a.png)

下表是木马的各个组件信息：

[![](https://p5.ssl.qhimg.com/t01513c4fe51a76cc54.png)](https://p5.ssl.qhimg.com/t01513c4fe51a76cc54.png)

经过以上分析，我们发现这个木马家族有以下功能：上传/下载文件、执行指定文件、键盘记录、屏幕截图、感染U盘、发送感染电脑位置信息等，窃取的文件列表如下：

.doc .docx .ppt .pps .pptx .ppsx .xls .xlsx .pdf .inp .vcf .txt .jpg .jpeg .bmp .gif .png .avi .wmv .mp4 .mpg.mpeg .3gp .mp3 .wav

并且该木马可以通过在线获取新插件的形式迅速方便地扩展更多的功能。木马的代码清晰、结构严谨，受控端通过HTTP请求与控制服务器通信，访问不同的php页面代表执行不同的功能，可能是高度定制的专用木马，或者是专门出售的商业间谍木马。

下面介绍该木马比较有特色的地方：

1. 不同的组件都通过调用同一个AdminServerDll.dll来完成具体功能，高度模块化。例如MSOBuild.exe和DefenderReference.exe中，分别获取AdminServerDll.dll的不同导出函数，然后调用这些导出函数，程序里只有基本的逻辑而没有具体的功能实现，下面左边是MSOBuild.exe,右边是DefenderReference.exe

[![](https://p3.ssl.qhimg.com/t012a017ca81a882473.png)](https://p3.ssl.qhimg.com/t012a017ca81a882473.png)

[![](https://p0.ssl.qhimg.com/t01af372c2d95ab2d09.png)](https://p0.ssl.qhimg.com/t01af372c2d95ab2d09.png)

其中AdminServerDll.dll是主要的功能模块，其每一个导出函数对应一个功能，可以从导出函数名知道其功能，如下：

[![](https://p0.ssl.qhimg.com/t013e2bae42d5ac49eb.png)](https://p0.ssl.qhimg.com/t013e2bae42d5ac49eb.png)

[![](https://p4.ssl.qhimg.com/t010c7d7fa46152c9e7.png)](https://p4.ssl.qhimg.com/t010c7d7fa46152c9e7.png)

[![](https://p1.ssl.qhimg.com/t01f7c93856090c96ca.png)](https://p1.ssl.qhimg.com/t01f7c93856090c96ca.png)

2. 通信控制：

受控端通过HTTP请求与控制服务器通信，通过访问不同的php页面与控制端交互：

[![](https://p5.ssl.qhimg.com/t01d916736ce7ab4ff0.png)](https://p5.ssl.qhimg.com/t01d916736ce7ab4ff0.png)

[![](https://p3.ssl.qhimg.com/t01bdbe4cd0f6dc7221.png)](https://p3.ssl.qhimg.com/t01bdbe4cd0f6dc7221.png)

经过整理后的路径如下：

[![](https://p4.ssl.qhimg.com/t012b18c3d1035a9c0d.png)](https://p4.ssl.qhimg.com/t012b18c3d1035a9c0d.png)

3. 检查VM、沙箱和调试

通过特权指令检查Virtual PC和VMWare：

[![](https://p2.ssl.qhimg.com/t0140a30d0d61c5c04e.png)](https://p2.ssl.qhimg.com/t0140a30d0d61c5c04e.png)

[![](https://p2.ssl.qhimg.com/t01e960ffbff07257f2.png)](https://p2.ssl.qhimg.com/t01e960ffbff07257f2.png)

通过dll来识别Sandboxie和是否调试：

[![](https://p2.ssl.qhimg.com/t01dabd00436eb3ca6c.png)](https://p2.ssl.qhimg.com/t01dabd00436eb3ca6c.png)



**扩展与关联分析**



使用360威胁情报中心的威胁情报平台（[**http://ti.360.com**](http://ti.360.com)）对样本连接的C&amp;C地址（185.109.144.102）做进一步关联，我们发现了更多的信息。

[![](https://p3.ssl.qhimg.com/t014289cfca494312f6.png)](https://p3.ssl.qhimg.com/t014289cfca494312f6.png)

其中有几个样本引起了我们的注意：

1. MD5：a6c7d68c6593b9dd2e9b42f08942a8b0，文件名：isi_report_of_2016.rar

这个样本是一个邮件附件，解压后为Name of Facilitators revealed.scr，这个其实是一个sfx自解压文件，点击后会将explorerss.pub改名为explorerss.exe，注册启动项并执行，然后打开Pakistan army officers cover blown.pdf迷惑受害人。

[![](https://p5.ssl.qhimg.com/t018c3b4352248350dc.png)](https://p5.ssl.qhimg.com/t018c3b4352248350dc.png)

[![](https://p3.ssl.qhimg.com/t01bca2164017b7e091.png)](https://p3.ssl.qhimg.com/t01bca2164017b7e091.png)

而explorerss.exe是由python打包成exe的，功能是窃取指定文件内容并上传到hxxps:// 185[.]109[.]144[.]102/browse.php?folder=%s&amp;%s中。将其中的python代码还原后，部分代码如下：

[![](https://p3.ssl.qhimg.com/t01431b9524f27536a1.png)](https://p3.ssl.qhimg.com/t01431b9524f27536a1.png)

2. MD5：872e7043ee8490db6e455942642c2c86 文件名：Current vacancies.doc

这个样本利用CVE-2012-0158释放一个downloader，downloader会下载执行hxxp://185[.]109[.]144[.]102/DistBuild/DefenderReference.exe，之后的流程就和前面分析的一样，就不再多说了，值得注意的是文档的内容。显示为联合国招聘文件，这明显是对安全相关人员投递的邮件，有明显的政治动机：

[![](https://p3.ssl.qhimg.com/t01981d3637666af0e5.png)](https://p3.ssl.qhimg.com/t01981d3637666af0e5.png)

3. MD5: 1b41454bc0ff4ee428c0b49e614ef56c文件名：Ramadan Mubaraq.rtf

这个样本所利用的漏洞为CVE-2017-0199，olelink的地址为http://138[.]197[.]129[.]94/logo.doc

[![](https://p0.ssl.qhimg.com/t0144e80354bd024245.png)](https://p0.ssl.qhimg.com/t0144e80354bd024245.png)

从以上的分析和其他关联到的样本中，我们注意到一些有趣的事情：这些样本应该都是通过邮件附件的形式传递的，并且使用office Nday漏洞或者社工手段引诱目标点开；从文件名、文档内容来看，都是对政治领域的相关人员进行的钓鱼邮件投递。综合多个样本的来源信息，这很有可能是一起针对巴基斯坦政府人员的定向攻击事件。

<br>

**IOC**

[![](https://p3.ssl.qhimg.com/t01682ca0ac01befb36.png)](https://p3.ssl.qhimg.com/t01682ca0ac01befb36.png)



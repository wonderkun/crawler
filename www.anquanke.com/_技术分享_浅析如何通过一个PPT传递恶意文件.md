> 原文链接: https://www.anquanke.com//post/id/86221 


# 【技术分享】浅析如何通过一个PPT传递恶意文件


                                阅读量   
                                **104492**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：dodgethissecurity.com
                                <br>原文地址：[https://www.dodgethissecurity.com/2017/06/02/new-powerpoint-mouseover-based-downloader-analysis-results/](https://www.dodgethissecurity.com/2017/06/02/new-powerpoint-mouseover-based-downloader-analysis-results/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p5.ssl.qhimg.com/t015a0831c1a37dc32a.jpg)](https://p5.ssl.qhimg.com/t015a0831c1a37dc32a.jpg)

翻译：[**myswsun**](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：80RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**0x00 前言**

本文介绍一种新的恶意下载者，通过PPT传递恶意powershell脚本，可直接通过鼠标悬停事件触发。

<br>

**0x01 分析**

这个PPT文档很有趣。首先这个文档不依赖宏、Javascript或者VBA来作为执行方式。这意味着这个文档不符合常规的利用方式。当用户打开文档，呈现文本“Loading…Please wait”，其对用户来说是一个蓝色的超链接。当用户悬停鼠标到文本之上（很常见的用户检测超链接的方式）将导致执行Powershell。这通过在悬停操作中定义一个元素实现。这个悬停操作是为了当用户鼠标悬停在文本时在PowerPoint中执行一个程序。在slide1的资源定义中，“rID2”被定义为一个超链接，其目标是PowerShell命令。由于它的长度，在下面一步步的截图中可以看到它。

当PowerShell执行时，会从域名“cccn.nl”得到c.php文件，下载它，以“ii.jse”为名称保存在临时目录中。它能通过wscript.exe执行，然后释放出一个文件“168.gop”，然后以-decode为参数执行certutil.exe。certutil.exe将168.gop解码，在临时目录保存为484.exe。然后执行484.exe，它会启动mstsc.exe允许RDP访问系统。484.exe之后被mstsc.exe重命名保存到AppDataRoamingMicrosoftInternet Explorersectcms.exe，然后在新目录重新执行。一个bat文件被写到磁盘。这个bat文件的目的似乎是改变sectcms.exe为隐藏属性（系统文件且只读）。它还会删除临时文件夹下的所有的.txt/.exe/.gop/.log/.jse文件。我在沙箱中执行了8小时，但是没有等到攻击者连接系统。因此我不能看见后门的其他目的。

**截图分析：**

打开文档的呈现文本：

[![](https://p3.ssl.qhimg.com/t01101fbf1ab3894877.png)](https://p3.ssl.qhimg.com/t01101fbf1ab3894877.png)

当悬停文档时的警告消息：

[![](https://p5.ssl.qhimg.com/t01e5a042b39b999ab7.png)](https://p5.ssl.qhimg.com/t01e5a042b39b999ab7.png)

如果用户允许了，将显示下面的PowerShell提示，并很快隐藏：

[![](https://p4.ssl.qhimg.com/t016f004914a5191f69.png)](https://p4.ssl.qhimg.com/t016f004914a5191f69.png)

下面是我为了测试PowerShell是否感知代理修改的callout——通过在PowerPoint Slide中编辑XML文件：

[![](https://p5.ssl.qhimg.com/t01b24125ec2698fc71.png)](https://p5.ssl.qhimg.com/t01b24125ec2698fc71.png)

下面是Slide1元素中定义的rID2元素，很明显看到Powershell命令作为超链接的目标：

[![](https://p5.ssl.qhimg.com/t01ac94de41c87b264d.png)](https://p5.ssl.qhimg.com/t01ac94de41c87b264d.png)

下面是Slide1 XML。红色高亮部分表示怎么定义悬停动作：

[![](https://p2.ssl.qhimg.com/t01dbc4c5e3d3c5a485.png)](https://p2.ssl.qhimg.com/t01dbc4c5e3d3c5a485.png)

**Sysmon 截图分析：**

PowerPoint初始打开时的Sysmon日志：

[![](https://p0.ssl.qhimg.com/t01fabeb28c1fd0e42f.png)](https://p0.ssl.qhimg.com/t01fabeb28c1fd0e42f.png)

Sysmon记录的PowerShell命令的执行：

[![](https://p4.ssl.qhimg.com/t01ddf780e399ccf42a.png)](https://p4.ssl.qhimg.com/t01ddf780e399ccf42a.png)

恶意的payload的初始进程创建：

[![](https://p5.ssl.qhimg.com/t01d70826132ec4269b.png)](https://p5.ssl.qhimg.com/t01d70826132ec4269b.png)

Mstsc.exe的进程创建之后，用于RDP访问系统：

[![](https://p1.ssl.qhimg.com/t014371899771e451c9.png)](https://p1.ssl.qhimg.com/t014371899771e451c9.png)

原始payload进程的终结：

[![](https://p4.ssl.qhimg.com/t016942dac9365d8a69.png)](https://p4.ssl.qhimg.com/t016942dac9365d8a69.png)

原始payload的文件拷贝。重命名为sectcms.exe和在AppData文件夹下隐藏：

[![](https://p2.ssl.qhimg.com/t019a36e70f3ecd030d.png)](https://p2.ssl.qhimg.com/t019a36e70f3ecd030d.png)

新移动的payload的再次执行：

[![](https://p5.ssl.qhimg.com/t01671a77ee1fb66fb4.png)](https://p5.ssl.qhimg.com/t01671a77ee1fb66fb4.png)

在临时文件夹中创建bat文件：

[![](https://p0.ssl.qhimg.com/t018b5ef630396f1a6c.png)](https://p0.ssl.qhimg.com/t018b5ef630396f1a6c.png)

通过cmd.exe执行bat文件。执行源是mstsc.exe：

[![](https://p0.ssl.qhimg.com/t01667d1cd8d506f341.png)](https://p0.ssl.qhimg.com/t01667d1cd8d506f341.png)

Bat的一个功能是添加隐藏、系统和只读属性：

[![](https://p3.ssl.qhimg.com/t012c994b26e3a23dbb.png)](https://p3.ssl.qhimg.com/t012c994b26e3a23dbb.png)

Sectcms.exe的第二次实例创建：

[![](https://p2.ssl.qhimg.com/t01266cff3303876d3a.png)](https://p2.ssl.qhimg.com/t01266cff3303876d3a.png)

最后，sectcms.exe的一个实例的退出：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c77801465ee07ba5.png)

<br>

**0x02 IOCs**

**File: order.ppsx**

MD5: 823c408af2d2b19088935a07c03b4222

SHA1: df99061e8ad75929af5ac1a11b29f4122a84edaf

SHA256: f05af917f6cbd7294bd312a6aad70d071426ce5c24cf21e6898341d9f85013c0

SHA512: 2cc9e87e0d46fdd705ed429abb837015757744783bf1e904f9f22d56288b9554a1bc450142e2b1644a4912c12a522391b354d97956e4cb94890744266249b7f9

**File: C:UsersCurrent UserAppDataLocalTemp168.gop**

MD5: 9B5AC6C4FD5355700407962F7F51666C

SHA: 9FDB4CD70BBFB058D450AC9A6985BF3C71840906

SHA-256: E97B266D0B5AF843E49579C65838CEC113562A053B5F87A69E8135A0A82564E5

SHA-512: AB85132D845437A7900E03C2F3FA773433815A4893E16F7716A5F800558B5F01827F25463EAFF619F804C484A1D23CDD5F2BCCC0F91B4B4D0C117E87D830B1B3

**File: C:UsersCurrent UserAppDataLocalTemp484.exe**

**File: C:UsersCurrent UserAppDataRoamingMicrosoftInternet Explorersectcms.exe**

MD5: 13CDBD8C31155610B628423DC2720419

SHA: 7633A023852D5A0B625423BFFC3BBB14B81C6A0C

SHA-256: 55C69D2B82ADDD7A0CD3BEBE910CD42B7343BD3FAA7593356BCDCA13DD73A0EF

SHA-512: 19139DAE43751368E19C4963C4E087C6295CC757B215A32CB95E12BDD82BB168DB91EA3385E1D08B9A5D829549DFBB34C17CA29BFCC669C7EAE51456FCD7CA49

**File: C:UsersCurrent UserAppDataLocalTempii.jse**

MD5: F5B3D1128731CAC04B2DC955C1A41114

SHA: 104919078A6D688E5848FF01B667B4D672B9B447

SHA-256: 55821B2BE825629D6674884D93006440D131F77BED216D36EA20E4930A280302

SHA-512: 65D8A4CB792E4865A216D25068274CA853165A17E2154F773D367876DCC36E7A7330B7488F05F4EE899E40BCAA5F3D827E1E1DF4915C9693A8EF9CAEBD6D4BFB

**C2 Communications:**

hxxp://cccn.nl/c.php

hxxp://cccn.nl/2.2

**IP Address of C2/Payload Domain:**

46.21.169.110

<br>

**0x03 参考**

[https://www.peerlyst.com/posts/microsoft-office-malware-now-being-delivered-without-macros-but-using-pps-url-mouse-hover-marry-tramp?trk=search_page_search_result](https://www.peerlyst.com/posts/microsoft-office-malware-now-being-delivered-without-macros-but-using-pps-url-mouse-hover-marry-tramp?trk=search_page_search_result) 

[https://www.joesecurity.org/reports/report-823c408af2d2b19088935a07c03b4222.html](https://www.joesecurity.org/reports/report-823c408af2d2b19088935a07c03b4222.html)  

[https://www.hybrid-analysis.com/sample/796a386b43f12b99568f55166e339fcf43a4792d292bdd05dafa97ee32518921?environmentId=100](https://www.hybrid-analysis.com/sample/796a386b43f12b99568f55166e339fcf43a4792d292bdd05dafa97ee32518921?environmentId=100) 

[https://www.virustotal.com/en/file/796a386b43f12b99568f55166e339fcf43a4792d292bdd05dafa97ee32518921/analysis](https://www.virustotal.com/en/file/796a386b43f12b99568f55166e339fcf43a4792d292bdd05dafa97ee32518921/analysis) 

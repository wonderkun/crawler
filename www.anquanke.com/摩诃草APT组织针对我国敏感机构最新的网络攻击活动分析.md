> 原文链接: https://www.anquanke.com//post/id/103277 


# 摩诃草APT组织针对我国敏感机构最新的网络攻击活动分析


                                阅读量   
                                **114777**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    





[![](https://p2.ssl.qhimg.com/t017cba3f861d294297.png)](https://p2.ssl.qhimg.com/t017cba3f861d294297.png)



## 背景

摩诃草组织（APT-C-09），又称HangOver、VICEROY TIGER、The Dropping Elephant、Patchwork，是一个来自于南亚地区的境外APT组织，该组织已持续活跃了8年。摩诃草组织最早由Norman安全公司于2013年曝光，该组织主要针对中国、巴基斯坦等亚洲地区和国家进行网络间谍活动。在针对中国地区的攻击中，该组织主要针对政府机构、科研教育领域进行攻击。

在2018年春节前后，360威胁情报中心与360安全监测与响应中心协助用户处理了多起非常有针对性的鱼叉邮件攻击事件，发现了客户邮件系统中大量被投递的鱼叉邮件，被攻击的单位为某些重要敏感的政府机构。而经过溯源分析与关联，幕后团伙正是摩诃草组织（APT-C-09）。360威胁情报中心在本文中对本次攻击活动的过程与细节进行揭露，希望企业组织能够引起重视，并采取必要的应对措施。



## 鱼叉邮件

2018年春节前后，一些重要敏感的政府机构接连收到一些带有链接的鱼叉邮件，诱导用户点击邮件的链接下载打开带漏洞的Office文档，一旦用户下载并打开文档，则会促发漏洞并继续下载执行远控木马长期控制用户电脑。

攻击者向目标发送与其工作内容相关的邮件信息，并诱导目标通过邮件中的链接下载附件文档，部分鱼叉邮件如下：

[![](https://p3.ssl.qhimg.com/t0122216c6acceef5e4.png)](https://p3.ssl.qhimg.com/t0122216c6acceef5e4.png)

[![](https://p4.ssl.qhimg.com/t010b21874cad4acb41.png)](https://p4.ssl.qhimg.com/t010b21874cad4acb41.png)

而下载回来的文档则是利用了CVE-2017-8570的Office漏洞文档，360威胁情报中心曾在2018年1月首次公开分析了利用CVE-2017-8570进行攻击的野外样本（详见参考 [1]），由于该漏洞弥补了CVE-2017-0199的天生缺陷，可以看到该漏洞Exploit被公开后，马上就被摩诃草APT组织纳入使用。



## 样本分析

### 样本执行过程

目标用户一旦通过邮件中的链接下载并打开带有漏洞的Office文档，则会触发漏洞并执行恶意脚本，恶意脚本会继续下载执行远控木马，并筛选特定目标继续下发执行特定的木马模块，整个样本执行流程如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01329baf4a67f9525a.jpg)

### 漏洞文档（CVE-2017-8570）分析

下载回来的文档为利用CVE-2017-8570的漏洞文档（漏洞详细分析见参考[1]）。漏洞利用样本包含三个Objdata，其中两个为Package对象，一个为包含CVE-2017-8570漏洞的OLE2Link。样本利用RTF文档自动释放Package对象的特性，将包含的两个Package对象释放至%TMP%目录下，最后通过CVE-2017-8570触发执行释放的恶意脚本，再通过脚本执行释放的EXE文件，Objdata对象信息如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015a8090e6a2a969f5.png)

包含漏洞的OLE2Link对象中设置File Moniker对应的文件为Z24UY3F0IYDULRD.sct脚本，漏洞触发后通过COM接口加载并执行：

[![](https://p1.ssl.qhimg.com/t01948fdf0fdccf1bd7.png)](https://p1.ssl.qhimg.com/t01948fdf0fdccf1bd7.png)

Z24UY3F0IYDULRD.sct为Scriptletfile，其主要功能为通过WScript.Shell接口启动执行%TMP%目录下的qrat.exe木马程序：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b51130e4c6995f7c.png)

### qrat.exe

释放的qrat.exe为C#编译的Dropper，使用.NET Reactor 4.x加壳，程序内的Form1.dllcopy函数负责从资源中释放出Microsoft.Win32.TaskScheduler.dll，并释放到同目录下，Form1.Stask函数则设置计划任务，而Form1.execopy负责从资源中释放文件到：%appdata%\Microsoft Network\microsoft_network\1.0.0.0\ microsoft_network.exe，最后删除自身以及Microsoft.Win32.TaskScheduler.dll并退出：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01dc1804d179410e56.png)

[![](https://p0.ssl.qhimg.com/t017a4f6a8252145405.png)](https://p0.ssl.qhimg.com/t017a4f6a8252145405.png)

主控程序会通过Microsoft.Win32.TaskScheduler.dll添加计划任务，使得释放的恶意程序microsoft_network.exe在每天0点启动，每5分钟重复执行一次，持续60天：

[![](https://p4.ssl.qhimg.com/t01d5647a6ca57a2177.png)](https://p4.ssl.qhimg.com/t01d5647a6ca57a2177.png)

Microsoft.Win32.TaskScheduler.dll是一个计划任务的开源项目，带有AirVPN的正常签名，这有可能使得添加计划任务时能躲避杀毒软件的拦截：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01113795426290005e.png)

microsoft_network.exe由C++编译，其会从从资源取数据，每1024字节解密一次：

[![](https://p0.ssl.qhimg.com/t0135dddbc5f82530e2.png)](https://p0.ssl.qhimg.com/t0135dddbc5f82530e2.png)

解密算法：

[![](https://p2.ssl.qhimg.com/t0156646848225ad10d.png)](https://p2.ssl.qhimg.com/t0156646848225ad10d.png)

解密后的数据通过zlib解压：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0119863c6ac362fbe6.png)

解压后的PE为C#编写的DLL文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b12079c85c9efacd.png)

最后通过CLR寄宿在C++的进程空间中加载C# DLL程序，调用类名为”_._”中”___”函数：

[![](https://p3.ssl.qhimg.com/t016ed18bc75db5ddbe.png)](https://p3.ssl.qhimg.com/t016ed18bc75db5ddbe.png)

通过“___” 函数加载资源“_”并运行：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014cf94e6bc623800a.png)

### xRAT

最终被执行的模块为C#编写的远控程序，其代码被严重混淆，去混淆后，发现该木马结构与GitHub上的开源远控项目xRAT的某个版本的代码结构完全一致（2015年xRAT已改名为QuasarRAT）。因此确定主控木马为xRAT：

[![](https://p3.ssl.qhimg.com/t0126a2475a260ea755.png)](https://p3.ssl.qhimg.com/t0126a2475a260ea755.png)

使用GitHub上下载的xRAT客户端源码进行编译，并劫持上线域名到本地成功上线：

[![](https://p1.ssl.qhimg.com/t01f6f293cf9456e099.png)](https://p1.ssl.qhimg.com/t01f6f293cf9456e099.png)

#### 远控功能

样本运行后，首先利用AES算法解密自身的配置文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d3a7710bc1362c02.png)

解密后的配置信息：

[![](https://p5.ssl.qhimg.com/t011c02a7adc04a3532.png)](https://p5.ssl.qhimg.com/t011c02a7adc04a3532.png)

C2地址为：tautiaos.com

上线端口：23558

上线密码：[g00gle@209.58.185.36](mailto:g00gle@209.58.185.36)

解密完成后，获取本机得操作系统信息、IP地址、所属国家地区等信息，然后设置注册表启动项：

[![](https://p4.ssl.qhimg.com/t0129089cfc4b6e74d8.png)](https://p4.ssl.qhimg.com/t0129089cfc4b6e74d8.png)

最后连接到C2服务器，将收集的信息传回C2服务器，并根据服务器端返回的数据进行命令分发，最终实现以下主要远控功能：
- 文件管理
- 屏幕控制
- 上传执行
- 远程SHELL
- 进程管理
- 网站访问
### 筛选目标并下发特定模块

攻击者会筛选感兴趣的目标进一步下发特定模块执行特定功能，通过360威胁情报数据平台的关联分析，捕获到以下特定模块：
<td width="235">**MD5**</td><td width="182">**路径**</td><td width="151">**功能**</td>
<td width="235">e42a8cef2e70d4f3c96c2b8073e7d396</td><td width="182">%appdata% \winfont.exe</td><td width="151">收集文件模块</td>
<td width="235">0fa12f215b8c5cfed492d3c5ee2867b3</td><td width="182">%appdata%\mssctlr.exe</td><td width="151">键盘记录模块</td>
<td width="235">5c3456d5932544b779fe814133344fdb</td><td width="182">%appdata%\vsrss.exe</td><td width="151">下载执行模块</td>
<td width="235">f396b476413558266f3abd336e06cbfc</td><td width="182">%appdata%\winupdate.exe</td><td width="151">下载执行模块[测试版]</td>

#### 文件收集

winfont.exe为文档收集模块，主要功能为遍历计算机目录获取特定文档并发送给远程服务器，该样本会创建一个240000ms间隔的定时器，并每间隔240000ms遍历特定后缀文件：

[![](https://p1.ssl.qhimg.com/t01481e51eef5d53038.png)](https://p1.ssl.qhimg.com/t01481e51eef5d53038.png)

而在定时器函数内部，首先会获取过滤文件的后缀进行解密，解密前的文件夹名称字符串和文件类型字符串存储于TFORM1窗口中不同的TlistBox控件处，并通过发送类型为LB_GETTEXT消息到指定窗口，获取字符串进行解密：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01580c67901217c128.png)

字符串解密算法为将字符串”odsf””qdsd”反转、拼接操作后，和0x1F按位与运算作为密钥，解密字符串：

[![](https://p3.ssl.qhimg.com/t01b56279461cc69687.png)](https://p3.ssl.qhimg.com/t01b56279461cc69687.png)

解密后字符串如下：


<td width="211">       收集的文件类型</td><td width="211">“doc”“docx”“xls”“xlsx”“pdf”“ppt”“pptx”“csv”</td>







“docx”

“xlsx”

“ppt”

“csv”
<td width="211">         排除的文件夹</td><td width="211">“MSOCache”“PerfLogs”“Program Files”“Program Files(x86)”“ProgramData”“Windows”“Windows”“AppData”“Application Data”“$Recycle.Bin”</td>









“PerfLogs”

“Program Files(x86)”

“Windows”

“AppData”

“$Recycle.Bin”

遍历计算机文件夹，排除特定文件夹后，获取特定文件夹中文档文件，并将收集的文件完整路径写入文件%AppData%\Identities\log.dat中：

[![](https://p2.ssl.qhimg.com/t01ec681b27ef76df57.png)](https://p2.ssl.qhimg.com/t01ec681b27ef76df57.png)

再在目录Startup目录下创建快捷方式window updater.lnk指向自身，实现自启动：

[![](https://p1.ssl.qhimg.com/t0101221526a4d4aad5.png)](https://p1.ssl.qhimg.com/t0101221526a4d4aad5.png)

最后构造POST包，将获取的.doc, .docx, .xls, .xlsx, .pdf, .ppt, .pptx, .csv类型文件内容直接通过HTTP表单提交的方式发送至远程服务器（[http://saicgovcn.xyz/systemdb.php](http://saicgovcn.xyz/systemdb.php)）。其中v1字段为字符串“Backup/用户名-计算机名/文件盘符”， Filename字段为发送文件的文件名：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010b91bd597b3a834d.png)

发送的数据包如下：

[![](https://p4.ssl.qhimg.com/t015f179550aabcff8b.png)](https://p4.ssl.qhimg.com/t015f179550aabcff8b.png)

#### 键盘记录

键盘记录的插件使用Dephi编写，其首先会创建一个指向自己的快捷方式，放置到启动目录下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0162603311cc337b0e.png)

然后通过GetKeyboardState记录击键内容，以及焦点窗口的标题，一起记录到本地文件中：

[![](https://p2.ssl.qhimg.com/t01b15b5be081896ffd.png)](https://p2.ssl.qhimg.com/t01b15b5be081896ffd.png)

%AppData%\Identities\version.dat

记录格式如下：

最后把键盘记录的信息通过form的形式提交到服务器：

hxxp://sz81orgcn.com/autoupdate.php?v1=Dwrite/计算机名-用户名，如图：

[![](https://p3.ssl.qhimg.com/t015a1fa68f7fb6556b.png)](https://p3.ssl.qhimg.com/t015a1fa68f7fb6556b.png)

#### 下载执行

vsrss.exe是一个下载执行模块，该模块会先创建自身的快捷方式到启动文件夹，然后设置两个定时器，第一个定时器每隔240秒会请求URL：

[http://ebeijingcn.live/templates/software.php](http://ebeijingcn.live/templates/software.php)

然后通过返回的结果判断是否需要下载执行程序，如果返回的数据里有用于下载的URL，则通过UrlDownLoadToFile下载文件到%AppData%\Microsoft\Network目录并执行，另外一个定时器每隔180秒执行一次，会将机器名和一些杀软信息发送至服务器上。

初始化的时候会解密出一些需要的字符串的路径和URL：

[![](https://p5.ssl.qhimg.com/t01f25271773395d051.png)](https://p5.ssl.qhimg.com/t01f25271773395d051.png)

解密出URL：

[![](https://p3.ssl.qhimg.com/t0179a854ee9fe73597.png)](https://p3.ssl.qhimg.com/t0179a854ee9fe73597.png)

通过WQL查找杀软：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011fb97bb1511453ce.png)

机器码的算法是获取用户名和机器名，用_连接起来，然后和加密密钥{$%^^%$}运算生成256字节的字典，然后数据和生成的字典异或运算后(类RC4算法)，转换成hex值：

[![](https://p3.ssl.qhimg.com/t01357a0a8b8acfa218.png)](https://p3.ssl.qhimg.com/t01357a0a8b8acfa218.png)

下图为生成字典的代码：

[![](https://p1.ssl.qhimg.com/t0119f32ded6965d8b2.png)](https://p1.ssl.qhimg.com/t0119f32ded6965d8b2.png)

下图为和生成的字典运算生成加密数据的代码：

[![](https://p5.ssl.qhimg.com/t018080d935b9c9935d.png)](https://p5.ssl.qhimg.com/t018080d935b9c9935d.png)

定时器的内部的功能为每间隔240000ms执行一次请求URL操作，如果返回的数据是需要下载执行的，就会从返回的数据里取到URL下载文件并执行：

[![](https://p5.ssl.qhimg.com/t0137d9abbbe9286de7.png)](https://p5.ssl.qhimg.com/t0137d9abbbe9286de7.png)

最后通过另外一个定时器每隔180000ms执行一次，触发定时器函数通过POST请求把其他的信息发送到URL： [http://ebeijingcn.live/templates/software.php](http://ebeijingcn.live/templates/software.php)，请求格式为：

[http://ebeijingcn.live/templates/software.php?cx=A44F63F1FFA477BCDB74FE69E54E94C20C2B0A&amp;b=A4457AF1E7A476BDDA35C449E331E0&amp;gt=A4457AF1E7A476BDDA35C449E331E09D48705E5ACACF76511A47C0&amp;tx=D06224ACBCFB41FC91678213A55A909A4E7C282CC0CD6F511847C0C778EA5553](http://ebeijingcn.live/templates/software.php?cx=A44F63F1FFA477BCDB74FE69E54E94C20C2B0A&amp;b=A4457AF1E7A476BDDA35C449E331E0&amp;gt=A4457AF1E7A476BDDA35C449E331E09D48705E5ACACF76511A47C0&amp;tx=D06224ACBCFB41FC91678213A55A909A4E7C282CC0CD6F511847C0C778EA5553)

GET请求中的各参数含义：
<td width="111">GET参数</td><td width="180">含义</td>
<td width="111">b</td><td width="180">机器标识</td>
<td width="111">cx</td><td width="180">杀软信息</td>
<td width="111">gt</td><td width="180">编码后的文件名</td>
<td width="111">tx</td><td width="180">编码后的文件HASH</td>

## 

## 溯源与关联分析

### APT-C-09（摩诃草）

通过对此次攻击中使用的下载者/远控代码结构分析、域名/IP关联分析，以及使用360威胁情报中心分析平台对相关样本和网络基础设施进行拓展，我们有理由相信此次攻击的幕后团伙为摩诃草APT组织（APT-C-09）。

比如使用360威胁情报中心数据平台搜索一下其中一个C&amp;C IP地址：94.242.249.206，可以看到相关IP已经被打上摩诃草的标签，这表明该IP曾经被摩诃草做为网络基础设施使用过：

[![](https://p0.ssl.qhimg.com/t01c5f783a7da8377d1.png)](https://p0.ssl.qhimg.com/t01c5f783a7da8377d1.png)

### 目标范围

通过360威胁情报数据平台的关联分析，在本次攻击活动中，摩诃草APT组织注册了大量与我国敏感单位/机构相关的相似域名，足以说明该团伙正在对我特定的领域进行定向攻击。由于相关信息的特殊性，相关仿冒域名均通过隐藏处理：
<td width="234">www.****-cn.org</td>
<td width="234">relay.****-cn.org</td>
<td width="234">www.*******ple-cn.com</td>
<td width="234">www.*************lysis.org</td>
<td width="234">report.*************lysis.org</td>
<td width="234">www.********icy.net</td>
<td width="234">www.*****mil.info</td>
<td width="234">www.****news.today</td>
<td width="234">***.***.armynews.today</td>
<td width="234">www.****zan.xyz</td>
<td width="234">******dia.xyz</td>
<td width="234">web.******news.com</td>
<td width="234">mail.******news.com</td>
<td width="234">******news.com</td>
<td width="234">******nter.com</td>
<td width="234">mail.******nter.com</td>
<td width="234">*****ovcn.xyz</td>
<td width="234">ohos.******ol.com</td>
<td width="234">news.*******ov-cn.org</td>
<td width="234">mailcenter.******ry</td>
<td width="234">mail.*****fr.top</td>
<td width="234">jacques3b.*****fr.top</td>
<td width="234">e4hjd3eed.*****ee.top</td>
<td width="234">****ail.co</td>

### 攻击时间

根据360网络研究院的大网数据，对于tautiaos.com C&amp;C域名访问在2018年3月16日达到过一个高峰，暗示在这个时间点攻击者曾经发动过一大波攻击：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c6861c6c7fc4e6c1.png)



## 防护建议

### 强化企业信息安全建设

360威胁情报中心和安全监测与响应中心再次提醒各企业用户，加强员工的安全意识培训是企业信息安全建设中最重要的一环，如有需要，企业用户可以建设态势感知，完善资产管理及持续监控能力，并积极引入威胁情报，以尽可能防御此类攻击。

### 补丁修复

针对此次攻击中所使用的Office漏洞CVE-2017-8570，软件厂商微软已经发布了漏洞相应的补丁，360威胁情报中心建议用户及时更新Office补丁修复漏洞：

[https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-8570](https://portal.msrc.microsoft.com/en-US/security-guidance/advisory/CVE-2017-8570)

### 禁用“Package” ActiveX Control

360威胁情报中心监控到利用RTF文档自动释放恶意Package对象到%TMP%目录的特性进行Office漏洞攻击的样本越来越多，包括本次攻击中利用了CVE-2017-8570的攻击样本以及最近的CVE-2017-11882等漏洞利用样本都使用了该技巧，所以360威胁情报中心建议用户如果不需要使用插入Package对象这类功能，可以在注册表中通过设置killbit的方式禁用，以彻底封堵这类攻击入口：


<td width="470">**执行命令行命令**</td><td width="98">**说明**</td>
<td width="470">reg add “HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Office\Common\COM Compatibility\{F20DA720-C02F-11CE-927B-0800095AE340}” /v “Compatibility Flags” /t REG_DWORD /d 0x400</td><td width="98">32位系统版本或64位系统中的64位版本</td>
<td width="470">reg add “HKEY_LOCAL_MACHINE\SOFTWARE\Wow6432Node\Microsoft\Office\Common\COM Compatibility\{F20DA720-C02F-11CE-927B-0800095AE340}” /v “Compatibility Flags” /t REG_DWORD /d 0x400</td><td width="98">64位系统中的32位版本</td>

## 总结

从2009年至今，摩诃草组织针对中国的相关攻击活动几乎没有停止，相反从2015年开始更加活跃，该组织所采用的恶意代码非常繁杂，载荷投递的方式相对传统，主要是以鱼叉邮件进行恶意代码的传播。而防范鱼叉邮件攻击最有效的方式是加强对人的安全意识培训。所以360威胁情报中心再次提醒各单位/企业用户，加强员工的安全意识培训是企业信息安全建设中最重要的一环。

## IOC
<td width="568">**C&amp;C**</td>
<td width="568">tautiaos.com</td>
<td width="568">185.130.212.252</td>
<td width="568">94.242.249.206</td>
<td width="568">**仿冒域名**</td>
<td width="568">www.****-cn.org</td>
<td width="568">relay.****-cn.org</td>
<td width="568">www.*******ple-cn.com</td>
<td width="568">www.***************sis.org</td>
<td width="568">report.***************sis.org</td>
<td width="568">www.********icy.net</td>
<td width="568">www.*****mil.info</td>
<td width="568">www.****news.today</td>
<td width="568">***.***.armynews.today</td>
<td width="568">www.****zan.xyz</td>
<td width="568">******dia.xyz</td>
<td width="568">web.******news.com</td>
<td width="568">mail.******news.com</td>
<td width="568">******news.com</td>
<td width="568">******nter.com</td>
<td width="568">mail.******nter.com</td>
<td width="568">*****ovcn.xyz</td>
<td width="568">ohos.******ol.com</td>
<td width="568">news.*******ov-cn.org</td>
<td width="568">mailcenter.******ry</td>
<td width="568">mail.*****fr.top</td>
<td width="568">jacques3b.*****fr.top</td>
<td width="568">e4hjd3eed.*****ee.top</td>
<td width="568">****ail.co</td>
<td width="568">**URL**</td>
<td width="568">http://sz81orgcn.com/autoupdate.php</td>
<td width="568">http://ebeijingcn.live/templates/software.php</td>
<td width="568">http://ebeijingcn.live/update/software.php</td>
<td width="568">http://saicgovcn.xyz/systemdb.php</td>
<td width="568">**PDB**</td>
<td width="568">C:\Users\Win7\Desktop\spain\qiho\obj\x86\Release\Q360.pdb</td>
<td width="568">C:\Users\TEST-AV\Desktop\RAT\Dual Ip rat\PK\Bin\Release\CryptoObfuscator_Output\Client.pdb</td>



## 参考

[1].[https://ti.360.net/blog/articles/analysis-of-cve-2017-8570/](https://ti.360.net/blog/articles/analysis-of-cve-2017-8570/)

[2].[https://www.anquanke.com/post/id/84333](https://www.anquanke.com/post/id/84333)

[3].[https://archive.codeplex.com/?p=taskscheduler](https://archive.codeplex.com/?p=taskscheduler)

[4].[https://github.com/quasar/QuasarRAT/releases](https://github.com/quasar/QuasarRAT/releases)

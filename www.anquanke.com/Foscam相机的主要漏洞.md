> 原文链接: https://www.anquanke.com//post/id/147415 


# Foscam相机的主要漏洞


                                阅读量   
                                **112734**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://blog.vdoo.com
                                <br>原文地址：[https://blog.vdoo.com/2018/06/06/vdoo-has-found-major-vulnerabilities-in-foscam-cameras/](https://blog.vdoo.com/2018/06/06/vdoo-has-found-major-vulnerabilities-in-foscam-cameras/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t012f7175c28af0ec2b.jpg)](https://p1.ssl.qhimg.com/t012f7175c28af0ec2b.jpg)

过去几个月来，VDOO安全研究团队一直在进行安全和安全领域领先物联网产品的广泛安全研究。在大多数情况下，为了提高效率和透明度，研究与设备供应商一起进行。

作为这项研究的一部分，VDOO的研究人员在几家供应商的设备中发现了零日漏洞。根据负责任的披露最佳实践，这些漏洞向供应商披露，并将在披露期结束后逐步分享。

我们发现易受攻击设备的供应商之一是Foscam，当时我们的团队发现了Foscam安全摄像头中的一个关键漏洞链。结合发现的漏洞，如果对手成功获取相机地址，他可以远程（通过LAN或互联网）获得对受影响相机的root访问权限。VDOO负责任地披露了这些漏洞（CVE-2018-6830，CVE-2018-6831和CVE-2018-6832），并与Foscam安全团队合作解决此事。

VDOO团队享有充分的协作和透明度，并且非常感谢Foscam与安全社区共享以下信息的开放性，以帮助整个物联网行业并为其客户的隐私和安全带来益处。

据我们所知，这些漏洞没有被广泛利用，因此没有导致任何具体的隐私侵犯或对Foscam客户的安全威胁。Foscam团队迅速采取行动修补这些漏洞并将其推向易受攻击的产品。

我们强烈建议未更新相机的Foscam客户立即采取措施或以其他方式降低风险。请参阅下面的FAQ部分

我们还建议其他相机供应商在本报告结尾处遵循我们的建议，以避免和减轻类似的威胁。



## 关于VDOO

VDOO是一家技术驱动的公司，致力于改变未受保护的连接设备的现实。VDOO正在构建一系列产品，以支持设备制造商在开发阶段将安全性嵌入到其连接的设备中，并实现后期开发安全性。<br>
除了开发产品和服务之外，VDOO还在连接设备的广泛研究方面投入了大量精力。安全和安全产品是本研究的两个焦点组。

VDOO的研究目标是贡献知识和工具来降低风险，并鼓励设备供应商为其产品实施正确的安全措施。我们VDOO认为适当实施安全要点将大大降低利用设备漏洞的机会。

这是[一系列博客](https://blog.vdoo.com/2018/06/06/behind-the-research-glass-an-insight-into-our-approach/)中的第一篇，将涵盖技术深度潜水作为我们广泛研究的一部分。敬请关注。



## 技术概述

foscam相机运行在Linux操作系统，所有进程都以root权限运行。Web服务器是一个带有附加供应商代码的lighttpd，它通过使用[FastCGI协议](https://en.wikipedia.org/wiki/FastCGI)将API请求转发到其内部的CGIProxy.fcgi进程。

所述CGIProxy.fcgi可执行转发请求（通过使用一个专有的IPC机构）的web服务方法-用于验证用户的凭证（如果需要）并运行所需的API命令中的处理程序。

根据命令的不同，处理程序可能会调用devMng进程中的其他代码，这些代码通常使用system（）或popen（）函数运行shell命令，库调用来配置系统服务。当一个守护进程重新启动后，它就终止了。<br>[![](https://p3.ssl.qhimg.com/t01ee1e13d4fa866b79.png)](https://p3.ssl.qhimg.com/t01ee1e13d4fa866b79.png)网络可访问摄像头的攻击情况如下：<br>**• 步骤1：**攻击者必须先获取相机的IP地址或DNS名称。它可以通过几种方式实现，其中包括：<br>
• 如果相机和网络由用户配置，以使相机具有与互联网的直接接口，则其地址可能由某些互联网扫描仪显示。<br>
• 如果攻击者获得了未经授权（远程或本地）访问相机所连接的网络，他可能会找到相机的本地地址。<br>
• 如果用户启用了动态DNS，攻击者可能会找到解决设备名称的方法<br>**• 步骤2：** 攻击者随后使用 **CVE-2018-6830**（一种任意文件删除漏洞）来删除某些重要文件，这些文件将在**webService**进程重新加载时导致身份验证绕过。<br>**• 步骤3：攻击者**将崩溃**webservice**通过利用过程**CVE-2018-6832**，在一个基于堆栈的缓冲区溢出漏洞的**webservice**的过程。崩溃后， **webService**进程将自动由看守程序守护进程重新启动，并且在进程重新加载期间，步骤2中的更改将生效。对手现在可以获得管理凭证。<br>**• 步骤4：** 攻击者通过利用**CVE-2018-6831**执行根命令。这是一个需要管理员凭据的shell命令注入漏洞。由于攻击者在前一阶段获得了管理员凭据，因此他现在可以使用此漏洞以root用户身份执行命令以执行特权升级。完整的详细信息在下面的深度技术探究中展示。



## 更深入的技术研究

本节提供每个漏洞的详细信息并说明完整的攻击顺序。

### **CVE-2018-6830 –** 任意文件删除漏洞

此漏洞允许攻击者通过为相机的Web管理界面制作特殊的GET请求来删除相机文件系统中的任意文件; 不需要用户凭证。<br>
此漏洞与添加到开源**lighttpd** Web服务器代码的自定义供应商代码有关。此代码的功能是在从相机上传到用户后立即删除使用snapPicture API命令拍摄的临时**快照**照片（将相同功能分配给**exportConfig** API命令）。

当GET请求发送到Web服务器（通过端口88）时，在处理请求之后，搜索请求的URI路径组件（**con&gt; request.uri-&gt; ptr**）或者搜索字符串**/ configs / export /或/ snapPic /**。如果请求包含这些字符串中的一个，则服务器使用**strncat**函数将文档根路径**/tmp/www**与URI的路径组件组合以形成完整路径。然后验证文件的存在（通过调用**access（path，F_OK**））并继续通过调用**remove（path）**来删除文件。<br>[![](https://p3.ssl.qhimg.com/t015c286fac5502f265.png)](https://p3.ssl.qhimg.com/t015c286fac5502f265.png)

此代码存在路径遍历漏洞攻击，攻击者可以在GET请求中使用**点划线**（’../‘）序列，该请求将以**con&gt; request.uri-&gt; ptr**组件结束。由于**/ snapPic /**目录已存在于服务器的文档根目录中，因此攻击者可以使用**/ snapPic / **URI作为有效路径，该路径也会触发该代码分支的执行。然后，攻击者继续添加**点划线**序列，沿着目录树向上移动，直到到达根目录（’** / **‘），然后添加要删除文件的路径。例如，URI **/snapPic/../../../tmp/abc**表示该文件**/ tmp / abc**，如果存在，将被删除。

**POC**

此PoC显示我们如何使用此漏洞从设备中删除任意文件。该**_FILE_TO_DELETE** shell变量持有文件的绝对路径。<br>[![](https://p2.ssl.qhimg.com/t013ae5864f37b1f5d9.gif)](https://p2.ssl.qhimg.com/t013ae5864f37b1f5d9.gif)

### **CVE-2018-6832 –** 基于攻击的缓冲区溢出漏洞

此漏洞允许攻击者崩溃设备的**webService**进程。它通过向相机的Web管理界面发送特制的GET请求来触发，而不需要任何用户凭据。

相机的网络服务器提供了带有许多命令的**FastCGI** API。可能的命令包括**getSWFlag**命令，该命令通过向**/CGIProxy.fcgi?cmd=getSWFlag**发送未经身份验证的HTTP GET请求来调用。GET请求参数从**CGIProxy.fcgi**进程转发到**webService的getSWFlag函数代码**（我们称之为**getSWFlag_func**）。**getSWFlag_func**可以选择接收名为**callbackJson**的查询字符串参数。

**getSWFlag_func**首先将**callbackJson**参数的值读取到堆栈上大小为0x400字节的本地变量**callbackJson_var**。这是通过引用**callbackJson_var**调用**get_param**函数完成的，最大大小限制为0x400个字符。

之后，**getSWFlag**通过引用**callbackJson_var**来调用**prepare_reply_func**函数。这个函数准备一些将被发回给用户的HTTP响应。

如果**callbackJson_var**不是空字符串 – **prepare_reply_func**使用**strcat**将各种字符串数据附加到位置（在**getSWFlag_func**堆栈的原始位置）的**callbackJson_var**字符串。总共添加了大约0x48个字符。（附加的字符串是：’（`{`“key”：“&lt;CGI_Result&gt; &lt;result&gt; 0 &lt;/ result&gt; &lt;flag&gt; 0011 &lt;/ flag&gt; &lt;/ CGI_Result&gt;”`}`）’）。

因此，如果攻击者设置查询字符串参数的值，**callbackJson**将保留足够多的字符（超过某个阈值），那么由**prepare_reply_func**生成的结果串联将导致**getSWFlag_func**的堆栈中的**callbackJson_var**溢出。写入大量字节将导致覆盖保存的堆栈寄存器（包括PC寄存器）并导致崩溃。因此，攻击者可能会崩溃**webService**进程，这会导致**/usr/bin/<br>**watchdog进程几秒钟后重新启动此进程。

### **CVE-2018-6831 – Shell命令注入漏洞**

此漏洞需要管理员凭据，这在以前的阶段中已经实现。它允许攻击者以root用户的身份执行命令，以提升权限。它绕过了2017年6月由思科Talos披露的一个较旧的漏洞补丁CVE-2017-2879。

[![](https://p1.ssl.qhimg.com/t013abaac73e4ffd575.png)](https://p1.ssl.qhimg.com/t013abaac73e4ffd575.png)

摄像机的Web服务器**FastCGI**的 API包括设置自定义NTP服务器的命令（**/CGIProxy.fcgi?cmd= setSystemTime**）。该命令需要管理员凭证。此命令所需的参数**ntpServer**包含用于设置**NTP_Server_URL**的字符串值 。该参数未被特殊字符过滤，甚至可以包含空格和分号。<br>
当调用API命令**setSystemTime**时，**CGIProxy.fcgi**<br>
将请求转发给**webService**进程，该进程读取其参数并发送调用**devMng**函数**OnDevMngMsgSetSystemTime**（命令0x6034）的IPC消息。<br>
除此之外，**OnDevMngMsgSetSystemTime**在全局结构中设置新的**NTP_Server_URL**。<br>
一个单独的线程，NTP更新线程，内**devMng**，运行**setSystemTimeNTP**功能每秒一次在一个无限循环。<br>**setSystemTimeNTP**采用全局结构（前面设置）中的**NTP_Server_URL**值，并使用此值调用**gethostbyname（NTP_Server_URL）**。如果主机名已成功解析，则继续调用以下易受攻击的代码：**sprintf（buf，“ntpclient -h％s -c 3 -s”，NTP_Server_URL）; 和popen（buf，“r”）;** （请参阅下面的IDA截图）。<br>[![](https://p1.ssl.qhimg.com/t01b55b610ba3a43e37.png)](https://p1.ssl.qhimg.com/t01b55b610ba3a43e37.png)

所述**POPEN**函数运行通过运行外壳命令的sh -c与所提供的字符串参数。如果我们将**NTP_Server_URL**设置为; **SOME_COMMAND** ;,并且可以绕过**gethostbyname（NTP_Server_URL）**调用 – **popen**然后会调用**sh -c“ntpclient -h; SOME_COMMAND; -c 3 -s**“。分号有助于破解shell命令并导致命令注入。由于**devMng**进程以root 身份运行，我们将能够以root用户身份运行任何命令。<br>
如前所述，我们的理解是，只有在成功执行**gethostbyname（）**调用后才会执行代码，以修补**CVE-2017-2879**漏洞。我们的猜测是，补丁作者认为使用**gethostbyname（）**调用将是一个足够的解决方案来净化**NTP_Server_URL**的输入。我们驳斥了这个假设，因为我们观察到**uclibc**（相机的C标准库）**gethostbyname（）**实现不会无法解析包含分号或空格的主机名。<br>
为了绕过**gethostbyname** 调用，我们执行以下步骤（参见下面的’**CVE-2018-6831**步骤’图中相应的步骤编号）：
1. 我们预先设置了我们自己的DNS服务器，并将其配置为响应任何带有预定义静态IP地址（例如1.2.3.4）的DNS查询（即使它包含空格和分号）。
1. 然后，我们用设置相机的DNS服务器地址到我们自己的DNS服务器**/CGIProxy.fcgi?cmd= setIpInfo** API命令。
1. 然后，我们通过使用**NTP_Server_URL** “; **SOME COMMAND**;” 构建对**setSystemTime** API命令的恶意请求来触发此漏洞。
1. 在此阶段，**gethostbyname**运行，导致摄像机发送“; **SOME_COMMAND**;”的DNS查询。
1. 我们的DNS服务器发送一个有效的响应，使得**gethostbyname（）**调用成功。
<li style="text-align: center;">代码继续执行命令注入，使攻击者能够以root身份执行命令。<br>[![](https://p1.ssl.qhimg.com/t01b09d46f83305301c.png)](https://p1.ssl.qhimg.com/t01b09d46f83305301c.png)<br>
PoC</li>
0 此漏洞的准备工作 – 使用以下配置设置Bind9 DNS服务器：<br>[![](https://p3.ssl.qhimg.com/t019ab295b76c9c94f2.gif)](https://p3.ssl.qhimg.com/t019ab295b76c9c94f2.gif)

1 将相机的DNS服务器设置为指向我们的DNS服务器:(使用管理员的用户名和密码）

[![](https://p5.ssl.qhimg.com/t011de0dafc833d6d09.gif)](https://p5.ssl.qhimg.com/t011de0dafc833d6d09.gif)<br>
2 触发漏洞（我们选择执行远程登录服务器，然后连接到它）：<br>[![](https://p0.ssl.qhimg.com/t01ef34b9e3a8b67db2.gif)](https://p0.ssl.qhimg.com/t01ef34b9e3a8b67db2.gif)

以下也是Wireshark的屏幕截图 – 显示整个攻击期间发射的DNS流量。<br>[![](https://p4.ssl.qhimg.com/t018787779f1c4074f8.png)](https://p4.ssl.qhimg.com/t018787779f1c4074f8.png)



## 设备制造商的建议

我们希望涉及本研究中分析的摄像机中发现的一些漏洞，使攻击者能够更轻松地发现和利用漏洞。我们鼓励设备制造商考虑以下建议。<br>
• 所有设备的进程都以root身份运行。这违反了特权分离的概念（[https://en.wikipedia.org/wiki/Privilege_separation），其中规定应该将程序分成若干部分](https://en.wikipedia.org/wiki/Privilege_separation%EF%BC%89%EF%BC%8C%E5%85%B6%E4%B8%AD%E8%A7%84%E5%AE%9A%E5%BA%94%E8%AF%A5%E5%B0%86%E7%A8%8B%E5%BA%8F%E5%88%86%E6%88%90%E8%8B%A5%E5%B9%B2%E9%83%A8%E5%88%86) – 每个部分都被限制为自己所需的特权。虽然系统中的每个进程都以root身份运行，但任何系统进程中的代码执行错误都会使攻击者升级到root权限。另一方面，如果较少的进程使用高权限运行 – 攻击者必须发现更多受限进程中的漏洞才能升级权限，这是一项艰巨的任务。具体而言，面向网络的进程（如Web服务器）应该以最小权限集而不是root身份运行。<br>
• 执行外部进程来执行任务（如配置设备或其操作系统），而不是使用编程语言（库函数）的现有API（如果存在）。执行外部进程，特别是运行shell命令，会给程序带来新的漏洞类型。开发人员应该意识到这些漏洞类型并保护它们。严格的输入校验可以阻止CVE-2018-6831成为shell命令注入漏洞 ，在实际运行shell命令时，要求设备制造商对所有shell控制符号进行过滤。另一个例子是攻击者能够替换程序即将运行的可执行文件 – 使其能够在更加特权的环境中运行代码。<br>
• 未能对正常输入的校验，是导致CVE-2018-6831漏洞产生的成因，主要原因是代码作者未能使用合适的方法对输入进行校验，而开发者依赖gethostbyname库调用 – 更确切的说是由此导致该漏洞的形成。防止不良输入的一种更好的方法是使用白名单 – 只允许在输入字段中找到特定的字符范围。<br>
• 在实践中，供应商固件文件使用短可猜测的模式作为openssl命令的关键字加上aes-128-cbc的事实使我们能够快速掌握固件内容。然后我们可以立即开始分析固件的安全问题。此外，该设备包含具有函数名称之类的符号未经剥离的二进制文件。这有助于我们理解代码如何工作。另一方面，值得注意的是，固件内容的隐匿方式的安全性可能会导致存在问题但由于固件被正确加密而未被发现和修复的情况。供应商应仔细考虑这种权衡。



## 感谢

我们要感谢Foscam的安全团队高效，及时地处理这个安全问题。



## 荣誉

Or Peles（[@peles_o](https://github.com/peles_o)），VDOO



## FAQ部分

### Q1。我如何知道我的设备是否易受攻击？

您需要检查您的相机固件是否至少是下面“表I”中出现的版本以及相关的安全补丁。要查看相机使用的固件版本，可以执行以下操作：<br>
方法1
1. 使用网络浏览器访问您的相机。地址线通常如下所示：192.168.0.1:88（用相机的实际地址替换“192.168.0.1”）。
1. 输入你的用户名与密码
1. 点击“设置”，然后点击“设备信息”
<li>在右侧窗格中，查找“应用程序固件版本”。<br>
方法2<br>
如果您有多个设备，则可能需要通过发出以下命令以编程方式检索固件：<br>**curl“&lt;Camera IP Address&gt;：88 / cgi-bin / CGIProxy.fcgi？cmd = getDevInfo＆usr = admin＆pwd = &lt;Password&gt;**<br>
例如：<br>**curl“192.168.0.200:88/cgi-bin/CGIProxy.fcgi?cmd=getDevInfo&amp;usr=admin&amp;pwd=abc1234**<br>
响应如下所示：<br><strong>&lt;CGI_Result&gt;<br>
&lt;result&gt;0&lt;/result&gt;<br>
&lt;productName&gt;FI9816P+V3&lt;/productName&gt;<br>
&lt;serialNo&gt;0000000000000001&lt;/serialNo&gt;<br>
&lt;devName&gt;Acme&lt;/devName&gt;<br>
&lt;mac&gt;00626E860232&lt;/mac&gt;<br>
&lt;year&gt;2018&lt;/year&gt;<br>
&lt;mon&gt;5&lt;/mon&gt;<br>
&lt;day&gt;25&lt;/day&gt;<br>
&lt;hour&gt;19&lt;/hour&gt;<br>
&lt;min&gt;40&lt;/min&gt;<br>
&lt;sec&gt;19&lt;/sec&gt;<br>
&lt;timeZone&gt;0&lt;/timeZone&gt;<br>
&lt;firmwareVer&gt;2.81.2.29&lt;/firmwareVer&gt;<br>
&lt;hardwareVer&gt;1.12.5.2&lt;/hardwareVer&gt;<br>
&lt;pkgTime&gt;2017-06-15_17%3A21%3A35&lt;/pkgTime&gt;<br>
&lt;/CGI_Result&gt;</strong><br>
Look for the line with “firmwareVer”.<br>**表I – 最新的易受攻击固件版本。**<br>
这些是最新的易受攻击的固件版本。添加相应的补丁可缓解这些漏洞。</li>
<th style="text-align: left;">相机型号</th><th style="text-align: left;">应用程序固件版本</th>
|------
<td style="text-align: left;">C1 Lite V3</td><td style="text-align: left;">2.82.2.33</td>
<td style="text-align: left;">C1 V3</td><td style="text-align: left;">2.82.2.33</td>
<td style="text-align: left;">FI9800P V3</td><td style="text-align: left;">2.84.2.33</td>
<td style="text-align: left;">FI9803P V4</td><td style="text-align: left;">2.84.2.33</td>
<td style="text-align: left;">FI9816P V3</td><td style="text-align: left;">2.81.2.33</td>
<td style="text-align: left;">FI9821EP V2</td><td style="text-align: left;">2.81.2.33</td>
<td style="text-align: left;">FI9821P V3</td><td style="text-align: left;">2.81.2.33</td>
<td style="text-align: left;">FI9826P V3</td><td style="text-align: left;">2.81.2.33</td>
<td style="text-align: left;">FI9831P V3</td><td style="text-align: left;">2.81.2.33</td>
<td style="text-align: left;">FI9851P V3</td><td style="text-align: left;">2.84.2.33</td>
<td style="text-align: left;">FI9853EP V2</td><td style="text-align: left;">2.84.2.33</td>
<td style="text-align: left;">C1</td><td style="text-align: left;">2.52.2.47</td>
<td style="text-align: left;">C1 V2</td><td style="text-align: left;">2.52.2.47</td>
<td style="text-align: left;">C1 Lite</td><td style="text-align: left;">2.52.2.47</td>
<td style="text-align: left;">C1 Lite V2</td><td style="text-align: left;">2.52.2.47</td>
<td style="text-align: left;">FI9800P</td><td style="text-align: left;">2.54.2.47</td>
<td style="text-align: left;">FI9800P V2</td><td style="text-align: left;">2.54.2.47</td>
<td style="text-align: left;">FI9803P V2</td><td style="text-align: left;">2.54.2.47</td>
<td style="text-align: left;">FI9803P V3</td><td style="text-align: left;">2.54.2.47</td>
<td style="text-align: left;">FI9815P</td><td style="text-align: left;">2.51.2.47</td>
<td style="text-align: left;">FI9815P V2</td><td style="text-align: left;">2.51.2.47</td>
<td style="text-align: left;">FI9816P</td><td style="text-align: left;">2.51.2.47</td>
<td style="text-align: left;">FI9816P V2</td><td style="text-align: left;">2.51.2.47</td>
<td style="text-align: left;">FI9851P V2</td><td style="text-align: left;">2.54.2.47</td>
<td style="text-align: left;">R2</td><td style="text-align: left;">2.71.1.59</td>
<td style="text-align: left;">C2</td><td style="text-align: left;">2.72.1.59</td>
<td style="text-align: left;">R4</td><td style="text-align: left;">2.71.1.59</td>
<td style="text-align: left;">FI9900EP</td><td style="text-align: left;">2.74.1.59</td>
<td style="text-align: left;">FI9900P</td><td style="text-align: left;">2.74.1.59</td>
<td style="text-align: left;">FI9901EP</td><td style="text-align: left;">2.74.1.59</td>
<td style="text-align: left;">FI9961EP</td><td style="text-align: left;">2.72.1.59</td>
<td style="text-align: left;">FI9928P</td><td style="text-align: left;">2.74.1.58</td>
<td style="text-align: left;">FI9803EP</td><td style="text-align: left;">2.22.2.31</td>
<td style="text-align: left;">FI9803P</td><td style="text-align: left;">2.24.2.31</td>
<td style="text-align: left;">FI9853EP</td><td style="text-align: left;">2.22.2.31</td>
<td style="text-align: left;">FI9851P</td><td style="text-align: left;">2.24.2.31</td>
<td style="text-align: left;">FI9821P V2</td><td style="text-align: left;">2.21.2.31</td>
<td style="text-align: left;">FI9826P V2</td><td style="text-align: left;">2.21.2.31</td>
<td style="text-align: left;">FI9831P V2</td><td style="text-align: left;">2.21.2.31</td>
<td style="text-align: left;">FI9821EP</td><td style="text-align: left;">2.21.2.31</td>
<td style="text-align: left;">FI9821W V2</td><td style="text-align: left;">2.11.1.120</td>
<td style="text-align: left;">FI9818W V2</td><td style="text-align: left;">2.13.2.120</td>
<td style="text-align: left;">FI9831W</td><td style="text-align: left;">2.11.1.120</td>
<td style="text-align: left;">FI9826W</td><td style="text-align: left;">2.11.1.120</td>
<td style="text-align: left;">FI9821P</td><td style="text-align: left;">2.11.1.120</td>
<td style="text-align: left;">FI9831P</td><td style="text-align: left;">2.11.1.120</td>
<td style="text-align: left;">FI9826P</td><td style="text-align: left;">2.11.1.120</td>
<td style="text-align: left;">FI9805W</td><td style="text-align: left;">2.14.1.120</td>
<td style="text-align: left;">FI9804W</td><td style="text-align: left;">2.14.1.120</td>
<td style="text-align: left;">FI9804P</td><td style="text-align: left;">2.14.1.120</td>
<td style="text-align: left;">FI9805E</td><td style="text-align: left;">2.14.1.120</td>
<td style="text-align: left;">FI9805P</td><td style="text-align: left;">2.14.1.120</td>
<td style="text-align: left;">FI9828P</td><td style="text-align: left;">2.13.1.120</td>
<td style="text-align: left;">FI9828W</td><td style="text-align: left;">2.13.1.120</td>
<td style="text-align: left;">FI9828P V2</td><td style="text-align: left;">2.11.1.133</td>

### Q2。如何判断我的设备是否被破坏？

由于僵尸网络恶意软件通常被制造为不被发现，因此没有简单的方法可以确切知道。对设备的任何可疑更改都可能表示设备上存在僵尸网络恶意软件。<br>
几种检查方法：
<li>
**您的密码不再生效** （而不是因为您忘记了） – 这强烈表示设备已被他人接管。</li>
<li>
**您的设备设置已被修改** – 例如，视频现在被发送到不同的服务器。</li>
<li>
**网络流量中的峰值** – 如果可能，请检查您的路由器网络统计信息。僵尸网络可能会增加摄像头发起的网络流量。任何峰值都应该值得引起你的注意，因为除非你从摄像机传输视频，否则这个数字应该相对较低。</li>
### Q3。如果违规，我的设备是否有补救措施？

在发布时，我们不知道有任何恶意软件在滥用此问题。如果您怀疑设备被破坏，请将相机恢复到出厂设置。这样做会将配置恢复到默认设置，允许您连接和升级固件。请记住，如果您使用的是易受VDOO检测到的漏洞的固件，则该设备可能成为攻击目标，并可能很快再次受到感染。因此，在重置设备之后，请确保在将相机直接连接到互联网之前立即执行固件升级。

### Q4。如果我无法更新相机的固件，如何减轻风险？

为了减少相机的暴露和远程管理的能力，建议将设备置于防火墙阻挡端口88和443（或相机配置中指定的端口）后面，并考虑不允许相机启动任何出站连接（请记住，这可能会影响Foscam云服务）。另一种选择是将设备置于反向代理之后，该代理将阻止我们用于漏洞利用的URL（请参阅上面的其他详细信息）。如果需要额外的帮助，请联系[security@vdoo.com](mailto:security@vdoo.com)。

### Q5。如何升级相机中的固件？

[点击此处查看](https://www.foscam.com/general-statement-for-firmware-update.html) 供应商的固件更新说明。

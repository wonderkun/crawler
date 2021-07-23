> 原文链接: https://www.anquanke.com//post/id/84134 


# 人面狮行动（APT-C-15）


                                阅读量   
                                **179015**
                            
                        |
                        
                                                                                    



目录

一、概述… 3

二、载荷投递… 4

1.社交网络水坑攻击… 4

2.诱饵文档… 5

3.自身伪装… 7

三、ROCK后门分析… 9

1.功能简述… 9

2.功能结构… 9

3.通信方式… 11

4.对抗手法… 12

四、相关线索信息… 15

1.攻击者Facebook帐号信息… 15

2.PDB信息… 15

3.诱饵文档… 15

4.释放的木马… 16

5.IP地理位置… 16

附录A:希伯来语样本来源… 17

附录B:最新样本查杀结果… 18

[![](https://p1.ssl.qhimg.com/t010e50ddeac3e5522e.jpg)](https://p1.ssl.qhimg.com/t010e50ddeac3e5522e.jpg)

一、概述

人面狮行动是活跃在中东地区的网络间谍活动,主要目标可能涉及到埃及和以色列等国家的不同组织,目的是窃取目标敏感数据信息。活跃时间主要集中在2014年6月到2015年11月期间,相关攻击活动最早可以追溯到2011年12月。主要采用利用社交网络进行水坑攻击,截止到目前我总共捕获到恶意代码样本314个,C&amp;C域名7个。

人面狮样本将主程序进行伪装成文档诱导用户点击,然后释放一系列的dll,根据功能分为9个插件模块,通过注册资源管理器插件的方式来实现核心dll自启动,然后由核心dll根据配置文件进行远程dll注入,将其他功能dll模块注入的对应的进程中,所以程序运行的时候是没有主程序的。用户被感染后比较难以发现,且使用多种加密方式干扰分析,根据PDB路径可以看出使用了持续集成工具,从侧面反映了项目比较庞大,开发者应该为专业的组织。

进一步我们分析推测人面狮行动的幕后组织是依托第三方组织开发相关恶意软件,使用相关恶意软件并发起相关攻击行动的幕后组织应该来自中东地区。

二、载荷投递

1.社交网络水坑攻击

我们发现其中一个希伯来语的诱饵文档来自于Facebook以色列军队主页的评论。也就是攻击者通过利用目标所关注的社交网站帐号进行载荷投递,这是一种典型的水坑攻击方式。这与传统的水坑攻击不同,APT攻击中主流的水坑攻击主要分为以下两种:

第一种:目标关注A网站,攻击者将A网站攻陷,并植入恶意代码(一般为漏洞脚本文件,俗称挂马),当目标访问被攻陷的A网站并浏览相关页面时,当目标环境相关应用触发漏洞则有可能被植入恶意代码。

第二种:目标关注A网站,攻击者将A网站攻陷,并将A网站上一些可信应用或链接替换为攻击者所持有的恶意下载链接,当目标访问被攻陷的A网站并将恶意下载链接的文件下载并执行,则被植入恶意代码。这种攻击的典型案例是2014年公开Havex木马[[1]](/Users/zhoufei-s/Desktop/%E4%BA%BA%E9%9D%A2%E7%8B%AE%E8%A1%8C%E5%8A%A8%EF%BC%88APT-C-15%EF%BC%89-20160630.docx#_ftn1),也被称作蜻蜓(Dragonfly)和活力熊(Energetic Bear)和我们在2015年5月末发布的海莲花(OceanLotus)APT组织[[2]](/Users/zhoufei-s/Desktop/%E4%BA%BA%E9%9D%A2%E7%8B%AE%E8%A1%8C%E5%8A%A8%EF%BC%88APT-C-15%EF%BC%89-20160630.docx#_ftn2)。

这两种水坑攻击的共性是攻击者需要获得目标所关注网站的修改权限,而本次攻击行动中攻击者完全是利用目标所关注的第三方社交网络平台进行攻击,攻击者只需简单注册,则具备留言评论等权限。

[![](https://p0.ssl.qhimg.com/t015cd694af61b6216e.png)](https://p0.ssl.qhimg.com/t015cd694af61b6216e.png)

图 1 Facebook样本来源

下表是上图具体恶意下载链接和链接对应的RAR文件MD5。

[![](https://p5.ssl.qhimg.com/t015355ceb66543e487.jpg)](https://p5.ssl.qhimg.com/t015355ceb66543e487.jpg)

RAR压缩包中诱饵文档内容为个人所得税调整,通过修改exe图标为文档来诱导用户点击。

[![](https://p0.ssl.qhimg.com/t014a6a28c64834cd1c.png)](https://p0.ssl.qhimg.com/t014a6a28c64834cd1c.png)

图 2压缩包内诱饵文档截图

[![](https://p4.ssl.qhimg.com/t01b36f7d3884194049.png)](https://p4.ssl.qhimg.com/t01b36f7d3884194049.png)

图 3相关C&amp;C域名被卡巴斯基sinkhole

进一步我们发现相关攻击涉及10个社交网络帐号,具体请参看“附录A:希伯来语样本来源”,相关帐号主要涉及如:以色列国防军、以色列海军等以色列军方和政府的社交网络帐号,相关攻击评论时间主要集中在2015年1月底至2月初期间。攻击者通过在社交网络评论下发表回复诱导用户点击,回复的内容为个人所得税改革。

2.诱饵文档

根据诱饵文档的内容,也可以从体现出攻击者关注的目标领域范围,进一步主要分为以下3类:

(A) 埃及:阿拉伯语

[![](https://p0.ssl.qhimg.com/t0162b0a1a8c154543c.png)](https://p0.ssl.qhimg.com/t0162b0a1a8c154543c.png)

图 4 诱饵文档1

此文档的原始文件[[3]](/Users/zhoufei-s/Desktop/%E4%BA%BA%E9%9D%A2%E7%8B%AE%E8%A1%8C%E5%8A%A8%EF%BC%88APT-C-15%EF%BC%89-20160630.docx#_ftn3),文件末尾有[爱资哈尔大学反对政变的学生]的YouTube主页。

[![](https://p0.ssl.qhimg.com/t0195ea29bb7bc03f17.png)](https://p0.ssl.qhimg.com/t0195ea29bb7bc03f17.png)

图 5 诱饵文档2

annonymous rabaa是一个攻击政府官网以抗议2013年8月Rabaa大屠杀的埃及黑客组织。

(B) 以色列 :希伯来语

[![](https://p5.ssl.qhimg.com/t01013eb95a5e36e503.png)](https://p5.ssl.qhimg.com/t01013eb95a5e36e503.png)

图 6 诱饵文档5

文档内容为:以色列个人税收改革。

3.自身伪装

分为两种方式,一种伪装成文档或图片,一种伪装成安装程序,具体如下图所示:

[![](https://p5.ssl.qhimg.com/t018b5081b0af90fc6a.png)](https://p5.ssl.qhimg.com/t018b5081b0af90fc6a.png)

图 9伪装文档、图片

[![](https://p1.ssl.qhimg.com/t01afe98ba0c4c30cda.png)](https://p1.ssl.qhimg.com/t01afe98ba0c4c30cda.png)

图 8伪装成安装程序

前一种方式用户点击后并不会弹出文档或图片,后一种方式点击后安装成功然后会释放出正常的安装程序。

模块的文件属性为Office组件,早期版本安装目录为 %UserProfile%AppDataRoamingofficeplugin,最近版本的安装目录为 C:Program Files`{`GUID`}`,比如C:Program Files`{`59f0641e-45ac-11e5-af9e-b8ca3af5855f`}`,伪装成系统组件。

[![](https://p0.ssl.qhimg.com/t01cec30e4452111ad6.png)](https://p0.ssl.qhimg.com/t01cec30e4452111ad6.png)

图 9相关文件属性信息

三、ROCK后门分析

1.功能简述

人面狮攻击行动中所使用的恶意代码主要以ROCK木马为主,这类家族属于人面狮幕后组织自行开发或委托第三方订制的恶意程序。另外其中一个样本会释放远控木马,属于njRat的变种,在本章节中暂不对njRat的变种展开详细介绍。

通过将自身图标修改为文档、图片或安装程序图标,会伪装成pdf文件、图片、flash安装程序,诱导用户点击执行。

主要功能是窃取用户信息,比如系统信息、键盘和鼠标记录、skype监控、摄像头和麦克风监控、浏览器保存的账号密码,以及URL、浏览历史记录等敏感信息。收集信息后会加密并发送到指定C&amp;C。

2.功能结构

[![](https://p0.ssl.qhimg.com/t01cec30e4452111ad6.png)](https://p0.ssl.qhimg.com/t01cec30e4452111ad6.png)

图 10 整体结构

    配置文件中存储着每个模块的配置信息,比如模块是否开启、数据文件的加密Key、用户ID(rkuid)、过期日期(未设置)、 C&amp;C、截图和录音的质量及间隔时间,注入的进程名称等。

[![](https://p4.ssl.qhimg.com/t016fb0219fef6b9d5c.png)](https://p4.ssl.qhimg.com/t016fb0219fef6b9d5c.png)

图 11 模块功能

Dropper总共会释放出20个dll,32位和64位各10个,每个功能模块都有32位版和64位版。

[![](https://p0.ssl.qhimg.com/t01df7419d312f44b17.jpg)](https://p0.ssl.qhimg.com/t01df7419d312f44b17.jpg)

部分功能模块介绍:Zcore主模块启动时解密安装目录下的配置文件,根据配置文件是否开启决定是否注入到指定进程。

lZcore.dll核心模块:负责加载其他的功能模块,并注入到指定进程中。以及模块的注册、升级、卸载、日志和消息的派发功能。

lPlgcmd.dll命令模块:负责获取系统信息,删除文件或目录、截图、上传下载文件,启动和结束进程的功能。

lPlgcomm.dll通信模块:负责将其他模块生成的数据文件发送到指定CC,发送过程无加密,加密是其他模块生成数据是完成的。每分钟向服务器发送一次请求,获取远程指令。

模块之间跨进程通过 WM_COPYDATA消息通信,消息头Magic为0x34AB541作为唯一标识识别。消息内容均格式化为json发送。

3.通信方式

通过HTTP POST向服务器80端口发送数据,数据包中的敏感字符串通过查询json配置文件的对应表替换。

[![](https://p1.ssl.qhimg.com/t0158c6ad1b391025f6.png)](https://p1.ssl.qhimg.com/t0158c6ad1b391025f6.png)

图 12 网络通信

[![](https://p5.ssl.qhimg.com/t018e6b5f928ef6a8be.png)](https://p5.ssl.qhimg.com/t018e6b5f928ef6a8be.png)

图 13 网络通信字符串还原

由于网络通信模块注入到浏览器进程中,且使用HTTP POST向C&amp;C的80端口发送数据,使异常流量很难被发现。

4.对抗手法

文件名随机

Dropper释放的文件,文件名来自于json文件,重命名为各种名词,比如gendarme.dll,jerques.dll。

[![](https://p2.ssl.qhimg.com/t01bb4527e2f100b067.png)](https://p2.ssl.qhimg.com/t01bb4527e2f100b067.png)

图 14 模块文件名

字符串加密

所有的字符串都经过加密,且有多个加密算法。

[![](https://p1.ssl.qhimg.com/t01825f19cc3e6f6f4d.png)](https://p1.ssl.qhimg.com/t01825f19cc3e6f6f4d.png)

图 15 字符串加密

API封装

大量的API(300多个)调用被封装在公共库中,干扰静态分析。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f618093bfc6d7c6d.png)

无主进程运行

核心模块作为explorer.exe的扩展启动,其他功能模块根据配置文件注入到指定进程,无主进程,所以比较难发现.即使用户发现异常,没有找到可疑进程,也会放松警惕。

行为隐藏

主模块在explorer中运行,安全软件不会拦截;通讯模块注入到浏览器进程,无浏览器进程不和CC通信;窃取文件模块注入到杀软,遍历文件的行为不容易被用户发现。

PE资源和配置文件加密

    Dropper中的PE文件经过zlib压缩和AES加密,释放出来的json配置文件也经过此方法加密。

从对抗手段来看,可见人面狮攻击行动中恶意代码开发者无论在静态还是动态对抗上面都花了大量功夫,以达到免杀和隐藏行为的效果。



四、相关线索信息

1.攻击者Facebook帐号信息

[![](https://p3.ssl.qhimg.com/t01ce4b02bd5624d567.jpg)](https://p3.ssl.qhimg.com/t01ce4b02bd5624d567.jpg)

2.PDB信息攻击者在进行社交网络水坑攻击时主要使用的两个Facebook帐号。

[![](https://p1.ssl.qhimg.com/t01d39f8551c6312f2b.jpg)](https://p1.ssl.qhimg.com/t01d39f8551c6312f2b.jpg)

l开发者id为zico根据PDB信息我们可以推测以下结论:

l工程名称为 ROCK-RW2-BRW6R

l内部定义为rootkits工具

3.诱饵文档

[![](https://p5.ssl.qhimg.com/t017e47f08e1ee0414d.jpg)](https://p5.ssl.qhimg.com/t017e47f08e1ee0414d.jpg)

4.释放的木马从文件名可以看出,涉及埃及和以色列。

52f461a133e95328ccd9ba7f70e2f3e6(图标为Adobe pdf)样本中释放出一个远控,属于njRat的一个变种,而njRat主要流行于中东地区。

[![](https://p4.ssl.qhimg.com/t01c8dcecada3bb1fc1.png)](https://p4.ssl.qhimg.com/t01c8dcecada3bb1fc1.png)

5.IP地理位置

图 16 样本和CC对应关系

   其中一个样本的C&amp;C:196.205.194.60所属国家为埃及,且此样本运行时释放的njRAT的 C&amp;C为196.205.194.61也是埃及。

[![](https://p2.ssl.qhimg.com/t018678592d06f63aa1.jpg)](https://p2.ssl.qhimg.com/t018678592d06f63aa1.jpg)

附录A:希伯来语样本来源

[![](https://p3.ssl.qhimg.com/t01c6ffb7e6c102345d.jpg)](https://p3.ssl.qhimg.com/t01c6ffb7e6c102345d.jpg)

附录B:最新样本查杀结果

[![](https://p2.ssl.qhimg.com/t0117d7476e98343402.png)](https://p2.ssl.qhimg.com/t0117d7476e98343402.png)

[[1]](/Users/zhoufei-s/Desktop/%E4%BA%BA%E9%9D%A2%E7%8B%AE%E8%A1%8C%E5%8A%A8%EF%BC%88APT-C-15%EF%BC%89-20160630.docx#_ftnref1)“Havex Hunts For ICS/SCADA Systems”,https://www.f-secure.com/weblog/archives/00002718.html

[[2]](/Users/zhoufei-s/Desktop/%E4%BA%BA%E9%9D%A2%E7%8B%AE%E8%A1%8C%E5%8A%A8%EF%BC%88APT-C-15%EF%BC%89-20160630.docx#_ftnref2)海莲花(OceanLotus)APT组织报告,https://ti.360.com/upload/report/file/OceanLotusReport.pdf

[[3]](/Users/zhoufei-s/Desktop/%E4%BA%BA%E9%9D%A2%E7%8B%AE%E8%A1%8C%E5%8A%A8%EF%BC%88APT-C-15%EF%BC%89-20160630.docx#_ftnref3) hxxps://docs.google.com/file/d/0ByavzARTLomhc3hFeFhGN1JOOE0/edit?pli=1

> 原文链接: https://www.anquanke.com//post/id/86461 


# 【木马分析】顺藤摸瓜：一个专黑建筑行业的QQ黏虫团伙现形记


                                阅读量   
                                **85653**
                            
                        |
                        
                                                                                    



**[![](https://p1.ssl.qhimg.com/t01210dbaf3129602ae.jpg)](https://p1.ssl.qhimg.com/t01210dbaf3129602ae.jpg)**

**前言**

QQ粘虫是已经流行多年的盗号木马，它会伪装QQ登陆界面，诱骗受害者在钓鱼窗口提交账号密码。近期，360QVM引擎团队发现一支专门攻击建筑行业人群的QQ粘虫变种，它伪装为招标文档，专门在一些建筑/房产行业聊天群里传播。

由于此木马样本带有其服务器数据库信息，木马生成器和一个小有规模的幕后团伙也因此而暴露出来。

<br>

**传播途径**

[![](https://p5.ssl.qhimg.com/t014c0456eb1923daea.png)](https://p5.ssl.qhimg.com/t014c0456eb1923daea.png)

根据网友举报和样本关联分析，此QQ粘虫木马主要是活跃在建筑/房产行业的聊天群中，从样本信息也可以发现，木马攻击的目标就是建筑房产从业者。

部分样本文件名：

[![](https://p5.ssl.qhimg.com/t0162fdcc51a0b87349.png)](https://p5.ssl.qhimg.com/t0162fdcc51a0b87349.png)

通过网络搜索，部分文件名确实是曾经或正在进行招投标的工程，对相关从业者具有一定迷惑性。

<br>

**样本分析**

[![](https://p1.ssl.qhimg.com/t01b87cc09c017860b0.png)](https://p1.ssl.qhimg.com/t01b87cc09c017860b0.png)

样本双击执行后会弹窗告警，显示“文件已损坏”来迷惑受害者，实际上盗号木马已经在后台默默执行。

[![](https://p3.ssl.qhimg.com/t01dd0cdb86383c9775.png)](https://p3.ssl.qhimg.com/t01dd0cdb86383c9775.png)

连接Mysql

[![](https://p4.ssl.qhimg.com/t0135a1093a12f4be24.png)](https://p4.ssl.qhimg.com/t0135a1093a12f4be24.png)

通过检测窗口类TxGuiFoundation是否存在，如果存在则弹出QQ账号异常的钓鱼窗口。

钓鱼窗口

[![](https://p2.ssl.qhimg.com/t014cf575b153ca43a5.png)](https://p2.ssl.qhimg.com/t014cf575b153ca43a5.png)

通过Mysql语句将盗取的QQ账号、密码、IP、address、UserID插入数据库

[![](https://p4.ssl.qhimg.com/t01510f21e19423f9c0.jpg)](https://p4.ssl.qhimg.com/t01510f21e19423f9c0.jpg)

尽管QQ粘虫木马的拦截查杀难度并不高，但是由于部分网友电脑“裸奔”或是没有使用专业安全软件，从木马程序内置的数据库账号密码访问其数据库可以看到，竟有不少网民中招，截至7月17日下午，该数据库统计的盗号数量已接近3000个： 

[![](https://p2.ssl.qhimg.com/t015ee23f8bb4356289.png)](https://p2.ssl.qhimg.com/t015ee23f8bb4356289.png)

在木马服务器数据库里，还有木马生成器的更新信息，从而可以获取到最新的木马变种下载地址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bf8be27b2168d39c.png)

<br>

**生成器**

**界面**

[![](https://p3.ssl.qhimg.com/t010ab91093d5253de5.png)](https://p3.ssl.qhimg.com/t010ab91093d5253de5.png)

[![](https://p0.ssl.qhimg.com/t01c6e20188182f31d0.png)](https://p0.ssl.qhimg.com/t01c6e20188182f31d0.png)

**压缩格式**

生成器支持将木马程序压缩成：R00、ZIP、TBZ、RAR、TBZ2、TAR、JAR、001、ISO、IMG

**团伙数据**

此木马生成器会根据登录的用户名来管理各自生成的木马盗取的QQ账号密码，支持删除和查看功能。从数据库中的数据来看，该木马团伙目前包括管理员在内，一共有14名成员。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c0f43b3253f29911.png)

**对比**

每个生成出来的木马文件都带有UserID，前面提到木马程序通过Mysql语句将盗取的QQ账号密码插入数据库，语句中api_user就对应着UserID。不同用户生成出来的木马程序唯一的不同就是UserID，每个用户通过自己的ID生成木马，并且各自管理盗取成功的账号密码。

[![](https://p0.ssl.qhimg.com/t01d051d252e5e0bcd7.png)](https://p0.ssl.qhimg.com/t01d051d252e5e0bcd7.png)

**拦截统计**

根据360安全卫士云主防的统计，该QQ粘虫木马对广东、云南、河南、湖南、安徽等地区的用户攻击数量相对较高，用户只要开启360安全卫士即可拦截预防：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01de6ed6b3dfe9fe6c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0195c77bac0dd289fc.png)

<br>

**盗号危害**

从这款伪装成“招标文档”的QQ粘虫木马来看，其大面积对建筑房产行业的QQ群进行投递传播。从文件名上来看，木马团队对投标项目做了相关的准备工作。

1.	木马制作

2.	木马售卖

3.	木马伪装相关“招标文档”打包

4.	潜伏进建筑/房产相关QQ群，上传木马到群文件/发送群邮件

5.	管理盗取到的账号密码

之后，木马团伙很可能会验证账号清洗账号窃取资料，进行撞库攻击建立行业社工库，甚至进一步进行定向攻击黑市贩卖。

说到撞库，这种攻击方式也非常普遍。不法分子把盗取或采集的账号密码以及相关资料整理生成对应的字典表，利用它去批量登录其他网站，从而得到一系列可以登录的用户账号。

[![](https://p1.ssl.qhimg.com/t01e59c805770b8847c.png)](https://p1.ssl.qhimg.com/t01e59c805770b8847c.png)

在此提醒网友，系统设置里不要勾选“隐藏已知文件类型的扩展名”，以免被文档图标的可执行程序蒙骗；如果在打开一些文件后出现了QQ重新登录的提示，应警惕这很可能是木马作祟；在聊天群共享、网盘等非可信来源下载网络资源时，应保持安全软件处于开启状态，对陌生文件进行检测，确认安全后再打开。



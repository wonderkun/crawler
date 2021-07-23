> 原文链接: https://www.anquanke.com//post/id/82371 


# 【译】iOS应用安全-1-搭建测试环境


                                阅读量   
                                **100920**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://resources.infosecinstitute.com/ios-application-security-part-1-setting-up-a-mobile-pentesting-platform/](http://resources.infosecinstitute.com/ios-application-security-part-1-setting-up-a-mobile-pentesting-platform/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01f976779277d36510.png)](https://p1.ssl.qhimg.com/t01f976779277d36510.png)

**介绍**

本系列是关于iOS应用安全的入门教程,间接会学到进行iOS应用安全测试会使用到的工具和测试方法。

**<br>**

**越狱iOS设备**

译者注:一台越狱的iOS设备是进行iOS应用安全测试所必不可少的,原文此处详细介绍了越狱的方法,但鉴于此部分内容相对成就,可参考价值不大,顾在此不做翻译,感兴趣的读者可以前往源网站阅读。

<br>

**设备准备**

现在你已经成功将你的设备越狱,下一步就是安装一下linux命令行工具,如wget,ps,apt-get 以及其他用于iOS应用审计的程序。然而,首要的是安装OpenSSH,以允许我们登陆到我们的设备,以便执行其他操作,见后文。

进入Cydia,搜索OpenSSH



[![](https://p4.ssl.qhimg.com/t01cc538ee25b312920.png)](https://p4.ssl.qhimg.com/t01cc538ee25b312920.png)

点击OpenSSH,选择“安装”,选择“确认”<br>



[![](https://p5.ssl.qhimg.com/t01e5ee55f585da5035.png)](https://p5.ssl.qhimg.com/t01e5ee55f585da5035.png)

OpenSSH就安装完成啦<br>

在登陆之前,先安装点其他工具。BigBoss Recommended tools  包含很多有名的工具,在Cydia中搜索并安装



[![](https://p5.ssl.qhimg.com/t0151cc5ec01d0306c3.png)](https://p5.ssl.qhimg.com/t0151cc5ec01d0306c3.png)

其他需要安装的工具包括:APT 0.6 Transitional, Git, GNU Debugger, less, make, unzip, wget and SQLite 3.x<br>

还需要安装的就是MobileTerminal ,可以让我们直接在设备中使用命令,而不是远程登陆到设备。



[![](https://p4.ssl.qhimg.com/t016bec507c0973f66c.png)](https://p4.ssl.qhimg.com/t016bec507c0973f66c.png)

安装后,会看到多出一个图标Terminal<br>



[![](https://p1.ssl.qhimg.com/t010daacae2c4a420e7.png)](https://p1.ssl.qhimg.com/t010daacae2c4a420e7.png)

点击图标,可点击屏幕软键盘输入命令。<br>



[![](https://p0.ssl.qhimg.com/t010cfb1b212d50ed32.png)](https://p0.ssl.qhimg.com/t010cfb1b212d50ed32.png)

接下来登陆的设备上,首先确实你的电脑跟你的设备在同一网络中,并查看你设备的ip地址。<br>



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d2b96437ee4426df.png)

如上图的ip地址是192.168.2.3.使用root用户登录,默认密码是alpine,如下图。不过建议你登陆后立即修改密码,因为有的恶意软件会使用默认的密码来登陆你的设备窃取信息。修改密码使用passwd命令,然后输入两次新密码。<br>



[![](https://p2.ssl.qhimg.com/t019f242117633dc944.png)](https://p2.ssl.qhimg.com/t019f242117633dc944.png)

注:运行需要root权限的命令之前,请确认Cydia处于后台,这是因为Cydia以root运行,其他进程就无法获得以由cydia获得的锁。<br>

之后,运行apt-get update 更新软件列表



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0130347efaf618a0cd.png)

最好也运行下apt-get upgrade,这会更新所有已经安装的软件包<br>



[![](https://p3.ssl.qhimg.com/t01182a674fa342ab8f.png)](https://p3.ssl.qhimg.com/t01182a674fa342ab8f.png)

下一步需要安装class-dump-z,用了dump app的类信息,前往官方网站([https://code.google.com/p/networkpx/wiki/class_dump_z)下载,本文写作时的最新版本是0.2a](https://code.google.com/p/networkpx/wiki/class_dump_z)%E4%B8%8B%E8%BD%BD,%E6%9C%AC%E6%96%87%E5%86%99%E4%BD%9C%E6%97%B6%E7%9A%84%E6%9C%80%E6%96%B0%E7%89%88%E6%9C%AC%E6%98%AF0.2a)

 

[![](https://p2.ssl.qhimg.com/t012818974377728e9d.png)](https://p2.ssl.qhimg.com/t012818974377728e9d.png)

登陆设备,使用wget下载<br>



[![](https://p5.ssl.qhimg.com/t01d8515f3e2ece5407.png)](https://p5.ssl.qhimg.com/t01d8515f3e2ece5407.png)

或者在电脑上下好,使用sftp上传到设备上,然后使用tar解包<br>



[![](https://p1.ssl.qhimg.com/t01acf71bb5c1e3bbe0.png)](https://p1.ssl.qhimg.com/t01acf71bb5c1e3bbe0.png)

然后,进入iphone_armv6 目录将class-dump-z 可执行文件复制到/usr/bin 目录,这样就可以在任何位置使用class-dump-z了。键入class-dump-z,如果得到类似下图的输出,就证明你的class-dump-z安装成功了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0140bdbe7576f305e8.png)



**深入阅读**

关于iOS应用安全的资源较少,以下是一些不错的:

•SecurityTube has a very detailed course on IOS security.

•Security Learn has some very good articles on penetration testing of IOS Applications.

•Hacking and Securing IOS applications is probably the best book i have read that deals with attacking IOS applications

•Lookout’s blog is also another valuable resource in learning about the latest techniques and exploits in the mobile world.

<br>

**总结**

本文我们介绍了如何在一台越狱iOS设备上搭建应用安全审计环境,下一篇我们将会介绍如何用class-dump-z分析应用。

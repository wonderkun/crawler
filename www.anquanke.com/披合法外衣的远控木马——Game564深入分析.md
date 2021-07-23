> 原文链接: https://www.anquanke.com//post/id/84267 


# 披合法外衣的远控木马——Game564深入分析


                                阅读量   
                                **106034**
                            
                        |
                        
                                                                                    



近期360白名单分析组多次捕获到了假冒正规游戏公司的远控盗号木马，此类木马程序最新变种借助搜索引擎在假冒的游戏下载站中发布,该木马在与杀毒的对抗中不断升级和更新，采用劫持正规软件厂商文件的“白+黑”技术手段，还专门购买使用了某些公司的数字签名，具有较强的隐蔽性。**对此360杀毒和安全卫士第一时间进行了拦截与查杀。**<br>

**一、木马伪装**

Game564木马利用了国内知名的酷狗音乐后台服务主程序TsiService.exe自动加载active_desktop_render.dll的特点，把木马文件与TsiService.exe组装在一起进行传播，也就是俗称的“白+黑”劫持。

通过对比我们发现了两个文件有相同函数名的调用接口,但是每个函数功能完全不同：

[![](https://p1.ssl.qhimg.com/t01dd1e81f927843471.png)](https://p1.ssl.qhimg.com/t01dd1e81f927843471.png)

[![](https://p2.ssl.qhimg.com/t01d212d71efc743c5e.png)](https://p2.ssl.qhimg.com/t01d212d71efc743c5e.png)

为了达到更好的迷惑效果，该木马还使用了名为Jinan Hongyi Ntwork Technology co的数字签名，而酷狗软件真正的数字签名是GuangZhou KuGou Computer Technology Co.：

[![](https://p0.ssl.qhimg.com/t01e4adba6f812cd89f.png)](https://p0.ssl.qhimg.com/t01e4adba6f812cd89f.png)

**二、 木马解密**

TsiService.exe启动之后调用SetDesktopMonitorHook就会读同目录下文件Win.dat解密出木马代码，加载到内存执行。

[![](https://p2.ssl.qhimg.com/t0180f9fa9379f07daa.png)](https://p2.ssl.qhimg.com/t0180f9fa9379f07daa.png)

[![](https://p1.ssl.qhimg.com/t015675735aa8054ff3.png)](https://p1.ssl.qhimg.com/t015675735aa8054ff3.png)

为了避免杀毒的查杀，木马程序隐藏在TsiService.exe内存之中。木马本身的行为看起来就是TsiService.exe的行为了。

**三、 木马的主要功能**

木马在内存里加载，连接c&amp;c地址[www.game564.com](http://www.game564.com/)。

[![](https://p0.ssl.qhimg.com/t0162b1f104375607d2.png)](https://p0.ssl.qhimg.com/t0162b1f104375607d2.png)

**之后会单独开启几个线程，实现下面几个功能：******

1、获取当前机器的操作系统，平台类型等关键信息，并且对外通讯，发送该信息。

[![](https://p5.ssl.qhimg.com/t01ce2973c1c4c38e37.png)](https://p5.ssl.qhimg.com/t01ce2973c1c4c38e37.png)

2、遍历查找主流杀毒软件，试图关闭杀毒进程防止被查杀：

[![](https://p0.ssl.qhimg.com/t01029d61afa84bb983.png)](https://p0.ssl.qhimg.com/t01029d61afa84bb983.png)

[![](https://p1.ssl.qhimg.com/t0125a31eeb01ab0d08.png)](https://p1.ssl.qhimg.com/t0125a31eeb01ab0d08.png)

3、遍历查找游戏进程crossfire.exe，找到该进程之后就会注入该进程，记录键盘消息，并且对外通讯，实现盗号功能。

[![](https://p3.ssl.qhimg.com/t01198c4ce6915b14a4.png)](https://p3.ssl.qhimg.com/t01198c4ce6915b14a4.png)

[![](https://p4.ssl.qhimg.com/t017ab36d99700ea015.png)](https://p4.ssl.qhimg.com/t017ab36d99700ea015.png)

[![](https://p3.ssl.qhimg.com/t01355fc01d61547a80.png)](https://p3.ssl.qhimg.com/t01355fc01d61547a80.png)

4、接受远程指令 主要的功能包括 

    1、增加建立超级隐藏用户账户guest用户，管理员权限，

    2、开启3389远程登录端口

    3、远程自动更新病毒文件

    4、遍历查找本地计算机的所有帐号信息，建立终端服务会话

[![](https://p3.ssl.qhimg.com/t01fe2fe3a858579a96.png)](https://p3.ssl.qhimg.com/t01fe2fe3a858579a96.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e356860b68242313.png)

[![](https://p1.ssl.qhimg.com/t0104b40dbc863a21ec.png)](https://p1.ssl.qhimg.com/t0104b40dbc863a21ec.png)

5、木马为了保证自身存活会替换系统关键服务，重启之后能够以系统服务的方式启动 ：

[![](https://p2.ssl.qhimg.com/t0124280c3d5a04d151.png)](https://p2.ssl.qhimg.com/t0124280c3d5a04d151.png)

木马的所有行为如下所示：

[![](https://p1.ssl.qhimg.com/t016e901f07ed1561fc.png)](https://p1.ssl.qhimg.com/t016e901f07ed1561fc.png)

木马涉及的域名信息（www.game564.com）因为阿里云的隐私保护，无法继续追查。

[![](https://p4.ssl.qhimg.com/t01f82ba90b4de848cd.png)](https://p4.ssl.qhimg.com/t01f82ba90b4de848cd.png)

鉴于该木马程序伪装成正规合法游戏公司的程序，并且有正规的数字签名，通过劫持合法文件注入内存加载等方式，据有较强的隐蔽性，根据全球在线杀毒扫描平台VirusTotal检测，只有四款杀毒软件能够第一时间查杀该木马，360杀毒和安全卫士是目前国内唯一能够全面拦截查杀Game564木马的安全软件。

**360安全中心提醒广大网友，下载软件应通过安全可靠的渠道，不可轻信搜索结果，同时应开启专业安全软件防护，以免木马趁虚而入，危及自身账号和数据安全。**

[![](https://p3.ssl.qhimg.com/t01b92cee2748fa192c.png)](https://p3.ssl.qhimg.com/t01b92cee2748fa192c.png)

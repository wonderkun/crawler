> 原文链接: https://www.anquanke.com//post/id/188175 


# 全球TOP恶意软件分析：HawkEye最新变种


                                阅读量   
                                **524883**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t0157a6ee138c0eebd2.jpg)](https://p1.ssl.qhimg.com/t0157a6ee138c0eebd2.jpg)



Hawkeye Keylogger是一款窃取信息的恶意软件，在地下黑客市场出售，此恶意软件曾在2016年的一次大规模网络攻击活动中被广泛使用，2018年Hawkeye的作者开始出售新版的HawkEye恶意软件，更新后的HawkEye被称为Hawkeye Keylogger-Reborn v8

Hawkeye Keylogger-Reborn v8已经不仅仅是一款普通的键盘记录器，新的变种集成了多个高级功能，同时Hawkeye在地下黑客市场宣传广告，并通过地下黑客论坛进行销售，作者在其网站上发布了HawkEye恶意程序的广告和使用教程，还雇佣了一些中介经销商分销此恶意软件

此前发现的HawkEye(v7)变种将主Payload程序加载到自己的进程中，新的变种HawkEye(v8)变种将恶意Payload注入到其它进程MSBuild.exe、RegAsm.exe、VBC.exe等，通过这些合法的进程执行恶意Payload代码

根据IBM X-Force的报告，HawkEye恶意软件已经将开始攻击全球范围内的企业，攻击者主要通过垃圾邮件的方式，向全球各种不同类型的企业发送相关诱饵邮件，欺骗受害者打开运行恶意软件，盗取受害者相关信息，此恶意软件在各地下黑客论坛和恶意软件市场非常活跃，全球多家企业被黑客利用这款恶意软件进行攻击，国外多家专业的安全公司都曾对此样本进行详细分析与报道

最近国外安全研究人员发布了一款Hawkeye的最新变种样本，此样本将主Payload代码注入到了RegAsm.exe进程，主程序的外壳使用Autoit编写，与此前使用C或其他PowerShell、JS脚本编写的外壳程序略有不同，详细分析如下

1.拷贝自身到相应目录，重命名为taskhostw.scr，如下所示：

[![](https://p0.ssl.qhimg.com/t0177c29f4d6fee007e.png)](https://p0.ssl.qhimg.com/t0177c29f4d6fee007e.png)

2.生成快捷方式到系统启动目录，如下所示：

[![](https://p1.ssl.qhimg.com/t017a88decc38f3cb1c.png)](https://p1.ssl.qhimg.com/t017a88decc38f3cb1c.png)

此快捷方式调用程序，实现开机自启动，如下所示：

[![](https://p0.ssl.qhimg.com/t01524798f2119b0cc8.png)](https://p0.ssl.qhimg.com/t01524798f2119b0cc8.png)

3.主程序运行之后进程信息，如下所示：

[![](https://p4.ssl.qhimg.com/t01f46e26d2090bedcf.png)](https://p4.ssl.qhimg.com/t01f46e26d2090bedcf.png)

4.分析主程序采用AutoIt编译，如下所示：

[![](https://p0.ssl.qhimg.com/t013608238aabab9e20.png)](https://p0.ssl.qhimg.com/t013608238aabab9e20.png)

5.主程序解密数据，并启动系统目录下的RegAsm.exe程序，如下所示：

[![](https://p1.ssl.qhimg.com/t015162ffdd68c1c206.png)](https://p1.ssl.qhimg.com/t015162ffdd68c1c206.png)

6.然后将解密的数据，循环拷贝到内存中，如下所示：

[![](https://p1.ssl.qhimg.com/t01709d2b4c38e813ff.png)](https://p1.ssl.qhimg.com/t01709d2b4c38e813ff.png)

7.将数据写入到RegAsm.exe进程，注入的数据其实就是一个PE文件，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b0ac2c097884aa7c.png)

8.执行注入的代码，如下所示：

[![](https://p1.ssl.qhimg.com/t016640955e693f255e.png)](https://p1.ssl.qhimg.com/t016640955e693f255e.png)

9.DUMP注入到RegAsm进程中的PE数据，是一个NET编写的程序，如下所示：

[![](https://p2.ssl.qhimg.com/t01ffc7b8e4ee2585f1.png)](https://p2.ssl.qhimg.com/t01ffc7b8e4ee2585f1.png)

10.去字符串混淆之后，使用dnSpy打开程序，可以看到是Reborn Stub程序，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0120abaa36b9073920.png)

11.主Payload它会创建子进程vbc.exe，然后将相应的恶意代码注入到子进程vbc.exe中执行，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01483338538ff84ffe.png)

将注入vbc.exe进程的Payload代码，全部DUMP下来进行分析，第一个Payload数据，如下所示：

[![](https://p2.ssl.qhimg.com/t01e912e93e5a6dc936.png)](https://p2.ssl.qhimg.com/t01e912e93e5a6dc936.png)

就是WebBrowserPassView程序，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014d4d69239a9b8be5.png)

然后将收集的凭据通过命令行参数保存到TMP文件中，同时会HawkEye会检测此TMP文件，并在收集完成之后，将TMP文件的全部数据读取到内存中，删除TMP文件

第二个Payload数据，如下所示：

[![](https://p0.ssl.qhimg.com/t01b0ffad83859f23d0.png)](https://p0.ssl.qhimg.com/t01b0ffad83859f23d0.png)

就是MailPassView程序，如下所示：

[![](https://p1.ssl.qhimg.com/t01b6720e31bf22909c.png)](https://p1.ssl.qhimg.com/t01b6720e31bf22909c.png)

收集受害者计算机上安装的电子邮件登录凭据信息、服务器地址、收件人服务器端口、协议类型等，然后将收集的信息通过命令行参数保存到TMP文件中，同时会HawkEye会检测此TMP文件，并在收集完成之后，将TMP文件的全部数据读取到内存中，删除TMP文件

IOC

HASH

343726CD425769DD4FE4037D655A6335

C&amp;C

66.171.248.178

全球大多数网络安全事件都是通过恶意软件进行攻击的，恶意软件的数量每年都在增加，不断有新的变种或新的家族出现，最近几年RAT窃密类的恶意软件在地下黑客论坛非常流行，各企业一定要高度重视,黑产团伙一直在寻找新的攻击目标……

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/CqyLDbdhDAjCyFi-3WPTeQ)

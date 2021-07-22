> 原文链接: https://www.anquanke.com//post/id/83698 


# Petya恶意勒索软件覆写你的MBR和MFT并且加密你的磁盘


                                阅读量   
                                **102807**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://www.bleepingcomputer.com/news/security/petya-ransomware-skips-the-files-and-encrypts-your-hard-drive-instead/](http://www.bleepingcomputer.com/news/security/petya-ransomware-skips-the-files-and-encrypts-your-hard-drive-instead/)

译文仅供参考，具体内容表达以及含义原文为准

通常情况下,当一个用户的电脑被加密勒索软件感染,感染目标也就是受害者电脑中的文件都会被加密,但并不会影响电脑操作系统的正常使用,用户只是无法打开这些文件而已。而现在发现有一个名叫Petya的恶意勒索软件,它会对整个硬盘进行加密,你无法访问驱动器上的任何东西,包括操作系统。在写这篇文章的时候,该勒索软件通常是要求9个比特币才会对驱动器进行解锁。

该勒索软件目前主要是通过电子邮件,针对德国企业的人力资源部门进行发送。这些邮件中会包含Dropbox的链接到一个应用程序,而当用户下载该文件执行后,他们的电脑就会感染Petya勒索软件。举例来说,其中部分受害者下载的是名为Bewerbungsmappe-gepackt.exe的文件安装程序。

值得注意的是,你的电脑被Petya感染后,你能够在网上找到很多如何进行修复的信息。大部分网站提供的方法是通过FIXMBR去修复MBR来清除感染。虽然这种方法能够删除锁屏,但它无法解密你的MFT,因此你仍然无法访问你硬盘上的操作系统和其中的文件。如果你不关心任何数据丢失的话,只需要在修复MBR后重装操作系统就可以了。

其实早在一月份就有一段短暂的勒索攻击事件使用了相同的手法,但当时并没有引起人们注意。现在已经很难找到当时的样本了,但应该是类似于下图这样的情况:

[![](https://p0.ssl.qhimg.com/t011885d6e4dbd3f967.jpg)](https://p0.ssl.qhimg.com/t011885d6e4dbd3f967.jpg)

Petya的加密过程

在第一次安装时,Petya会使用一个恶意程序替换驱动器上的主引导记录(Master Boot Record,即MBR),MBR是一个硬盘驱动器上最开头的一段信息,用于告诉计算机如何引导操作系统。然后它会使电脑重启从而加载替换的恶意软件,这时候屏幕上会显示类似于CHKDSK的界面。在这个伪造的CHKDSK阶段中,Petya会对驱动器上的主文件表(Master File Table,即MFT)进行加密。一旦MFT被损坏或者被加密,在这种情况下,计算机将不知道文件的位置,或者虽然知道文件位置但是不能访问。

[![](https://p4.ssl.qhimg.com/t0114f22ab7ff7fa975.jpg)](https://p4.ssl.qhimg.com/t0114f22ab7ff7fa975.jpg)

一旦假的CHKDSK阶段完成,你将得到一个锁屏显示,上年会显示Tor网站链接以及一个唯一的区分ID,你需要前往网站支付赎金。当你完成支付后,你会得到一个解锁密码,然后回到这个锁屏界面使用得到的密码进行解锁。

[![](https://p0.ssl.qhimg.com/t0196003254152a8f4d.jpg)](https://p0.ssl.qhimg.com/t0196003254152a8f4d.jpg)

在解密网站获取Petya解锁密码的步骤

当受害者访问解锁网站,他会看到类似于下面的界面。在网站首页受害者输入验证码后会看到一些信息,告诉受害者他们的电脑发生了什么。

[![](https://p4.ssl.qhimg.com/t01d918edecbb7c11e2.jpg)](https://p4.ssl.qhimg.com/t01d918edecbb7c11e2.jpg)

如果用户点击“开始解密过程(Start the decryption process)”,他们会一步一步的根据网站引导进行付款并最终获得解锁密码。这些步骤如下所示:

第一步,输入你的设备识别ID

[![](https://p4.ssl.qhimg.com/t019786fa48b7dd0d8b.jpg)](https://p4.ssl.qhimg.com/t019786fa48b7dd0d8b.jpg)

第二步,兑换比特币

[![](https://p1.ssl.qhimg.com/t010c123676d4918934.jpg)](https://p1.ssl.qhimg.com/t010c123676d4918934.jpg)

第三步,进行比特币交易

[![](https://p2.ssl.qhimg.com/t01c00b58abfa034868.jpg)](https://p2.ssl.qhimg.com/t01c00b58abfa034868.jpg)

第四步,等待确认

[![](https://p2.ssl.qhimg.com/t0194201917ab4dcf99.jpg)](https://p2.ssl.qhimg.com/t0194201917ab4dcf99.jpg)

第五步也就是最后一步,应该就是攻击者收到赎金后提供给受害者用于解锁的密码。当受害者使用密码解锁后,会恢复磁盘驱动器中的MFT以及原本的MBR。之后就可以再次开机进入操作系统中并且可以再次正常访问其中的文件。

目前还没有除了支付赎金之外的方法解决这种加密勒索。研究人员正在对其进行分析,也许未来会发现好的解决方案。

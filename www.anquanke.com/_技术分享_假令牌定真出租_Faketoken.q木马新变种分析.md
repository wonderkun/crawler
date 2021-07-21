> 原文链接: https://www.anquanke.com//post/id/86708 


# 【技术分享】假令牌定真出租：Faketoken.q木马新变种分析


                                阅读量   
                                **95292**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securelist.com
                                <br>原文地址：[https://securelist.com/booking-a-taxi-for-faketoken/81457/](https://securelist.com/booking-a-taxi-for-faketoken/81457/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t012c5225512d3d6259.jpg)](https://p1.ssl.qhimg.com/t012c5225512d3d6259.jpg)**



翻译：[trip1e_chee5e](http://bobao.360.cn/member/contribute?uid=2937224120)

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

 

**前言**

恶意程序Trojan-Banker.AndroidOS.Faketoken已经出现超过一年的时间了，在这一年多的时间里，它已经从最开始的mTAN codes（双因素认证）拦截木马进化到了加密器。随着该程序新变种的作者不断改进，它的影响范围也越来越大。有些变种已经覆盖超过了2000款的商用APP。在该程序的最新版本中，我们检测到了一种新的攻击方式——定出租并支付道路交通安全委员会开具的罚单！ 就在不久之前——感谢来自一家大型俄罗斯银行的同事们——我们检测到了一个新的木马样例“Faketoken.q”，它有很多有趣的特性。

** **

**感染**

我们目前还无法重建导致感染的整个事件链，不过程序的图标显示出，恶意程序是通过群发带有图片下载链接的短信传播的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.securelist.com/files/2017/08/faketoken-taxi-ru1.png)

** **

**木马结构**

木马程序经过检测分为两部分，第一部分是经过混淆处理的程序释放器（Trojan-Banker.AndroidOS.Fyec.az）为了防止被检测，其中的文件都在服务器端做了混淆处理，粗略看的话，根本看不出什么。

[![](https://p1.ssl.qhimg.com/t0192802b1abaf4effe.png)](https://p1.ssl.qhimg.com/t0192802b1abaf4effe.png)

然而，这肯定是能正常运行的正确的代码。它会对恶意程序的第二部分进行解密并运行。这是现在最流行的方式，如今已经没多少不经过处理的木马了。 恶意程序的第二部分是DAT格式的文件，它是木马程序的核心功能文件，当然数据已经被加密了。 对数据进行解密后，会得到可读性还不错的代码。

[![](https://p1.ssl.qhimg.com/t019a1d09e01c200e37.png)](https://p1.ssl.qhimg.com/t019a1d09e01c200e37.png)

在木马程序初始化后，它会隐藏自己的图标并监视全部通信和用户启动的程序。每当打一个电话/接到一个电话，它就会把它记录下来并发给攻击者。

[![](https://p4.ssl.qhimg.com/t0168c9bf22fe5ed986.png)](https://p4.ssl.qhimg.com/t0168c9bf22fe5ed986.png)

Faketoken.q的作者对原恶意程序的覆盖面进行了保留与简化，目前木马能够监控几个银行和一些日常应用比如Android Pay，Google Play Store以及支付交通罚单，订机票，宾馆，出粗车的应用。

[![](https://p0.ssl.qhimg.com/t0192a9fb908e835994.png)](https://p0.ssl.qhimg.com/t0192a9fb908e835994.png)

每当用户启动木马监控的程序时，Faketoken.q就会迅速用假界面替换掉真界面，并且假界面与真界面一模一样，诱骗用户输入银行卡账号密码。 这些被攻击的应用为了支付方便通常都绑定了银行卡，有些甚至是强制绑定，这些应用的安装量达到了几百万的规模，Faketoken也因此能造成巨大的危害。 那么，接下来问题就出现了：当诈骗者要完成一次诈骗支付时，他们怎么得到银行发到用户手机上的验证码呢？攻击者通过将用户收到的每一条短信转发到C&amp;C服务器上解决了这个问题。

[![](https://p1.ssl.qhimg.com/t01dddb950950cdd349.png)](https://p1.ssl.qhimg.com/t01dddb950950cdd349.png)

我们目前认为手中的样本是还未完成的程序，它的假界面做的还不够好，不足以让用户受到欺骗。

[![](https://p5.ssl.qhimg.com/t01c77a573ff8cac248.png)](https://p5.ssl.qhimg.com/t01c77a573ff8cac248.png)

现如今大量的App使用屏幕覆盖技术（Windows Managers，Messengers等），这可能会被攻击者利用，并且防范起来非常复杂。 直到现在，我们也没有收到关于Faketoken大量攻击的报告，也就是说，这目前只是一个测试版。通过木马中的俄语界面以及代码中的俄语，我们推测Faketoken.q主要针对的是俄罗斯及独联体国家。



**防范**

为了防范Faketoken以及类似的恶意程序，应坚决不安装第三方的安卓应用，使用手机杀毒软件和应用锁也会有一些帮助。



**MD5**

CF401E5D21DE36FF583B416FA06231D5

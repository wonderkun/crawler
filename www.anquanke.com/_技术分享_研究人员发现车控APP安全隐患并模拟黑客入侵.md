> 原文链接: https://www.anquanke.com//post/id/85570 


# 【技术分享】研究人员发现车控APP安全隐患并模拟黑客入侵


                                阅读量   
                                **81762**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securelist.com
                                <br>原文地址：[https://securelist.com/analysis/publications/77576/mobile-apps-and-stealing-a-connected-car/](https://securelist.com/analysis/publications/77576/mobile-apps-and-stealing-a-connected-car/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01f85567bc9bc9a854.jpg)](https://p4.ssl.qhimg.com/t01f85567bc9bc9a854.jpg)

****

翻译：[金乌实验室](http://bobao.360.cn/member/contribute?uid=2818394007)

预估稿费：260RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**前言**

在过去的几年中，互联网接入汽车越来越受欢迎。互联网接入的形式不仅仅限于多媒体系统（音乐、地图、电影），汽车钥匙系统也越来越流行。车主通过车控APP便能获得汽车GPS坐标、行车路线、解锁车门、发动引擎和打开辅助装置。这样的功能是一把双刃剑，为车主提供方便的同时也埋下了安全的隐患。如果偷车贼入侵了安装有汽车APP的移动设备，那么偷车岂不就是小菜一碟？

为了找到问题的答案，我们接下来将模拟入侵行为，希望车主能够从中学习到能够规避这种风险的方法。

<br>

**潜在的威胁**

车控APP非常流行，应用商店里那些最受欢迎的车控类APP的用户数量可达百万。下面列举了几个：

[![](https://p2.ssl.qhimg.com/t019ce980f2f6a42054.png)](https://p2.ssl.qhimg.com/t019ce980f2f6a42054.png)

我们将选取7个APP作为我们的研究对象，这些APP可以控制来自不同制造商的车辆。我们不会揭露那些APP的名字，但是我们将研究结果通知了实验过程中涉及到的制造商。

我们对每个APP的以下几个方面做了检查：

1. 潜在的危险功能是否可用，是否可以通过APP偷车，或者是使某个系统瘫痪。

2. APP的开发人员是否采用方法来实现APP的逆向工程复杂化（代码混淆或者打包）。否则，偷车贼将很轻易就能看到APP的代码，找到漏洞，并利用漏洞入侵汽车的基础设施。

3. APP是否检查设备的root权限。如果恶意软件感染了有root的设备，那么它将能够做任何事情。在这种情况下，关键是要确定开发人员是否将用户凭证以纯文本的形式保存在设备上。

4. 是否有验证，向用户展示APP的GUI（overlay 保护）。Android允许监视向用户展示的APP，恶意软件可以通过向用户展示具有相同GUI的网络钓鱼窗口并窃取用户凭证来进行拦截。

5. 是否有APP完整性验证，例如APP是否能验证自身代码的更改。这关系到入侵者是否能注入他的代码到APP，然后发布到应用商店，并保持原来APP相同的功能和特征。

不幸的是，实验证明所有的APP总会在某个方面存在容易受到攻击的安全隐患。

<br>

**测试车控APP**

此次实验，我们从知名品牌的汽车APP中选择了7个最受欢迎的，测试了这些APP的能够被利用来访问汽车的基础设施的漏洞。

测试结果如下。此外，我们还审查了每个应用程序的安全功能。

[![](https://p2.ssl.qhimg.com/t01e62aa1105b3df938.png)](https://p2.ssl.qhimg.com/t01e62aa1105b3df938.png)

**APP #1**

汽车注册过程为输入用户名和密码，以及汽车的VIN到APP。之后APP会显示一个PIN，这个PIN必须使用传统方法在车内输入，以便完成将智能手机链接到汽车的过程。这就意味着仅知道VIN不足以解锁车门。

APP不会检查设备是否有root权限 ，并将用户名以及汽车的VIN在accounts.xml文件中作为纯文本存储。如果木马在链接了的智能手机上具有超级用户访问权限，那么窃取数据将会非常容易。

APP #1可以轻松地被反编译，并且代码能被阅读和理解。除此之外，它不会抵消自己重叠的GUI，这就意味着用户名和密码可以被可能仅仅只有50行代码的钓鱼APP获得。如果APP有目标程序包的名称，我们应该能够检测到哪个APP正在运行和启动具有相似GUI的恶意行为。

为了进行完整性验证，我们修改了loginWithCredentials（登录凭证）方法。

[![](https://p5.ssl.qhimg.com/t01b577e603f50974a5.png)](https://p5.ssl.qhimg.com/t01b577e603f50974a5.png)

在这种情况下，用户名和密码就这样简单的显示在智能手机的屏幕上，没有任何措施来阻止嵌入代码并向入侵者的服务器发送凭证。

没有完整性验证就意味着任何感兴趣的人都可以随心所欲的修改APP，并将修改过的APP发给潜在的受害者。签名验证非常缺乏。这样的攻击需要入侵者付出一些努力，因为他们必须能哄骗用户下载修改过的APP。这样的攻击是悄无声息的，所以用户在他的汽车被盗之前不会察觉到任何异常。

但是，好的方面是APP用SSL证书创建连接，这防止了中间人攻击。

**App #2**

该APP提供保存用户凭证，同时建议加密整个设备以防盗。这是可以理解的，但是犯罪者不是要偷电话，只是要“感染”它。在App #2中发现了存在于APP #1中的同样的问题，用户名和密码以纯文本的形式存储在 prefs file.`{`?????????`}`.xml file中（问号表示由APP随机生成的字符）。

[![](https://p3.ssl.qhimg.com/t010603e137d89762ea.png)](https://p3.ssl.qhimg.com/t010603e137d89762ea.png)

VIN存储在下一个文件中。

[![](https://p2.ssl.qhimg.com/t015578fb09c82f691e.png)](https://p2.ssl.qhimg.com/t015578fb09c82f691e.png)

随着实验的深入，我们得到了更多的信息。开发人员甚至没有时间去实施应用程序代码的完整性验证，并且由于某些原因，他们也忘记了做代码混淆。结果就是我们很容易的便能修改LoginActivity代码。

[![](https://p2.ssl.qhimg.com/t012f8f3c0fac79aa1d.png)](https://p2.ssl.qhimg.com/t012f8f3c0fac79aa1d.png)

APP保留了自己的功能性，但是在注册过程中输入的用户名和密码在登录尝试后会立即显示在屏幕上。

**App #3**

与此APP配对的汽车可选择性的配置一个控制模块，控制模块可启动发动机和解锁车门。 由经销商安装的每个模块都有一个带有访问代码的贴纸，贴纸会交到车主手中，这样即便知道VIN也不可能将汽车链接到其他凭证。

但是仍然有其他的攻击可能性：首先，APP很小，它的APK大小为180 KB; 其次，整个APP将其调试数据记录到了保存在SD卡上的文件中。

[![](https://p1.ssl.qhimg.com/t016b27790003210327.png)](https://p1.ssl.qhimg.com/t016b27790003210327.png)

在LoginActivity开始时记录日志

[![](https://p4.ssl.qhimg.com/t013d41910644f9047c.png)](https://p4.ssl.qhimg.com/t013d41910644f9047c.png)

**转储日志文件的位置**

不幸的是日志记录只有在以下标志被设置在APP中时才能被启用：android：debuggable =“true”。 公共版本的APP是没有标志的，但我们可以将它插入到APP中。为此，我们将使用Apktool utility。启动编辑过的APP并尝试登录之后，设备的SD卡将会创建一个带有TXT文件的marcsApp文件夹。在我们的示例中，账户的用户名和密码已经输出到文件中。

[![](https://p3.ssl.qhimg.com/t019c5da593302122e4.png)](https://p3.ssl.qhimg.com/t019c5da593302122e4.png)

当然，说服受害者删除原来的APP，并安装一个相同的带有调试标志的APP并不是那么容易。但是仍然是可以实现的，方法是将受害者诱导到一个网站去下载一个重要的更新，将编辑过的APP和安装手册伪装为更新。从经验上来说，病毒制作者善于使用社工的方法。现在向APP添加将日志文件发送到指定服务器或以SMS消息的形式发送到电话号码的功能并不是难事。

**App #4**

该APP允许将现有的VIN绑定到任何凭证，但是会发送请求到汽车的内置电脑上。因此，不成熟的VIN盗窃将不会有助于黑客入侵车辆。

但是，被测试的APP对于其窗口上的overlays是没有防御力的。如果入侵者获得了系统的用户名和密码，那么他便能够解锁车门。

令人遗憾的是，该APP将系统的用户名以及大量的其他有趣的数据以明文储存，例如汽车的制造、VIN和汽车的号码。所有的这些数据都位于MyCachingStrategy.xml文件中。

**App #5**

为了将汽车连接到安装了该APP的智能手机上，需要知道汽车内置电脑上显示的PIN。这就意味着和App #4的情况一样，知道VIN是不够的，必须从汽车内部攻破。

**App #6**

该APP由俄罗斯的开发人员制作，区别于其同行，该APP使用车主的电话号码作为授权。 这种方法对任何车主都会造成相当程度的风险，只需执行一个Android API函数即可获得系统的用户名，发起攻击。

**App #7**

我们注意到，参与实验的最后一个APP将用户名和密码以纯文本的形式存储在credentials.xml文件中。

[![](https://p5.ssl.qhimg.com/t01b861367f07de827c.png)](https://p5.ssl.qhimg.com/t01b861367f07de827c.png)

如果智能手机被具有超级用户权限的木马病毒感染了，那么该文件的窃取将轻而易举。

<br>

**汽车被盗是如何发生的**

理论上，拿到凭证后，入侵者便能够获得汽车的控制权，但这并不意味着就能够简单的把车开走，必须有钥匙才能启动汽车。因此，偷车贼进入车里之后，会使用编程单元写一个新的密钥放入到汽车的车载系统中。几乎所有的APP都允许解锁车门，这样就绕过了汽车的报警系统。因此，偷车贼便可以在不破坏任何东西的情况下悄悄的将车迅速偷走。

值得注意的是，车控APP带来的风险不仅仅是汽车盗窃，入侵汽车并故意篡改某些元素可能导致交通事故，带来伤害或死亡。

我们检测的这几款APP都没有防御机制。但是值得庆幸的是这些APP中没有一个是通过声音或SMS消息来控制汽车的。这种方法被售后报警系统制造商使用，包括俄罗斯的那款APP，因为移动互联网的质量并不能保证汽车总是在线，而语音呼叫和SMS消息却随时可用。下面我们简单分析一下由此产生的汽车安全威胁。

声控是通过所谓的DTMF命令处理的。车主必须给汽车打电话，汽车的报警系统会响应呼入，并报告汽车状态，然后切换到待机模式，等待车主的命令。然后，车主拨打预设的号码来命令汽车解锁车门并启动发动机，报警系统通过识别这些代码来执行正确的命令。

声控系统的开发者通过白名单来保障安全，只有在白名单上的电话号码才具有控制汽车的权利。但是，如果车主的手机被入侵了呢？入侵者就可以调用报警系统、禁用扬声器和屏幕，这样就可以无声无息的完全控制汽车。当然，入侵也不会这么容易，许多汽车爱好者将报警系统号码保存在一个虚构的名字下。在这种情况下，只有车主频繁地呼叫车辆，入侵者才能在偷来的呼出历史记录中找到报警系统号码。

汽车报警系统SMS消息控制方法的开发者肯定没有阅读过我们关于Android设备安全的文章。卡巴斯基实验室面临的第一个也是最常见的移动木马就是SMS木马，或者是含有用于秘密发送短信的代码的恶意软件，通过常见的木马操作以及由木马发出的远程命令实现。因此，恶意软件的开发者通过以下三个步骤就可以解锁受害者的车门：

1. 浏览智能手机上所有的SMS消息，从中找出汽车命令。

2. 找到所需的SMS消息后，从中提取电话号码和密码以获得访问权限。

3. 向找到的电话号码发送SMS消息，解锁车门。

一个木马便能够无声无息的完成这三步操作，唯一需要做的事情就是感染智能手机。

<br>

**结论**

汽车是昂贵的，值得我们像保护银行账户一样去保护汽车的安全。汽车制造商和APP开发者的态度是明确的，他们致力于快速的填补市场APP空白，为车主提供改变生活质量的新功能APP。但是，当考虑车控APP的安全性时，其基础设施安全（控制服务器）及其交互和基础设施通道并不是唯一值得考虑的事情。客户端安全也值得注意，特别是安装在用户设备上的APP。现在APP很容易便能被用来打击车主，客户端很可能是最薄弱的环节，最有可能成为攻击者的目标。

目前为止，我们没有检测到车控APP攻击，在我们的成千上万个检测恶意软件的实例中也没有发现用于下载车控APP的配置文件的代码。然而，现代的木马是非常灵活多变的，如果某个木马今天持续显示不能被用户自己移除的广告，那么明天它就可以将配置文件从车控APP上传到犯罪者命令和控制的服务器。木马还可以删除配置文件，并用修改过的配置文件覆盖它。一旦所有这些在经济上都变得可行，最常见的移动木马也会增加新的功能。

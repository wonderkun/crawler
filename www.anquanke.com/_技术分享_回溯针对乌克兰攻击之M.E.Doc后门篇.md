> 原文链接: https://www.anquanke.com//post/id/86379 


# 【技术分享】回溯针对乌克兰攻击之M.E.Doc后门篇


                                阅读量   
                                **81046**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：welivesecurity.com
                                <br>原文地址：[https://www.welivesecurity.com/2017/07/04/analysis-of-telebots-cunning-backdoor/](https://www.welivesecurity.com/2017/07/04/analysis-of-telebots-cunning-backdoor/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01ab3dc0c5f9f4e8cf.jpg)](https://p4.ssl.qhimg.com/t01ab3dc0c5f9f4e8cf.jpg)

译者：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：150RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**0x00 前言**



2017年6月27日，一个新的网络攻击攻陷了乌克兰很多计算机系统，在其他国家也是。那次攻击是由ESET产品带头检测出，并命名为Diskcoder.C（或者ExPetr, PetrWrap, Petya, or NotPetya）。这个恶意软件伪装成典型的勒索软件：它加密计算机的数据并需要价值300美金的比特币的勒索金。事实上这个恶意软件的作者的目的是搞破坏，因此他们的做法是使得数据恢复成为不太可能。

在我们之前的博文中，我们将这次攻击归于TeleBot组，没有披露其他类似的针对乌克兰的攻击。本文将揭露在DiskCoder.C攻击期间的一些关于初始目标向量的细节信息。

<br>

**0x01 恶意软件更新分析**



乌克兰国家警察网络部门在它的fackbook帐号上表示，正如ESET和其他信息安全公司分析的一样，合法的乌克兰的会计软件M.E.Doc被攻击者用于推送DiskCoder.C。然而，直到现在没有人提供它如何实现的细节。

在我们研究中，我们确定了一个隐蔽且狡猾的后门被攻击者注入到M.E.Doc合法的模块中。似乎如果攻击者没有M.E.Doc的源代码不太可能做到这点。

后门模块名为ZvitPublishedObjects.dll。它使用.NET框架编写。是一个5M大小的文件，且包含很多被其他组件调用的合法代码（包括M.E.Doc的主执行模块ezvit.exe）。

我们检查了M.E.Doc在2017年的所有更新，发现至少有3次更新包含后门模块：

[![](https://p0.ssl.qhimg.com/t0141c1ae97bbe17477.png)](https://p0.ssl.qhimg.com/t0141c1ae97bbe17477.png)

Win32/Filecoder.AESNI.C事件是在10.01.180-10.01.181更新后3天发生的，DiskCoder.C是在10.01.188-10.01.189更新后5天发生的。有趣的是从2017年4月24日到5月10日的四次更新，和2017.5.17到2017.6.21的7次更新都不包含后门模块。

因为5月15日的更新包含了后门模块，而5月17日的更新没有，这就可以假设解释为什么Win32/Filecoder.AESNI.C低感染率：5月17日的更新是攻击者未预料到的事。他们在5月18日推送了勒索软件，但是大部分M.E.Doc的用户不再包含后门模块（因为他们更新了）。

分析的PE文件中编译时间暗示了这些文件在更新日或之前的同一时间编译。

[![](https://p1.ssl.qhimg.com/t01bf747b5f5dea92dd.png)](https://p1.ssl.qhimg.com/t01bf747b5f5dea92dd.png)

下图中有无后门的两个版本的类的列表的区别（使用ILSpy .NET反编译器）。

[![](https://p2.ssl.qhimg.com/t013a92541c958ae24b.png)](https://p2.ssl.qhimg.com/t013a92541c958ae24b.png)

后门的主类名为MeCom，位于ZvitPublishedObjects.Server命名空间内：

[![](https://p3.ssl.qhimg.com/t01028a2c7f6bf6d402.png)](https://p3.ssl.qhimg.com/t01028a2c7f6bf6d402.png)

MeCom类由ZvitPublishedObjects.Server命名空间下的UpdaterUtils的IsNewUpdate方法调用。IsNewUpdate方法会定期被调用以便检查是否有更新。5月15日实现的后门模块稍微有点不同，比6月22日的特征少。

乌克兰的每个商业组织都有一个名为EDRPOU数字的唯一的合法的识别码(Код ЄДРПОУ)。这对于攻击者非常重要：有了EDRPOU数字，他们能精确识别使用具有后门的M.E.Doc的组织。一旦确定了一个这样的组织，攻击者使用各种策略攻击组织的计算机网络（取决于攻击者的目标）。

因为M.E.Doc在乌克兰是合法的会计软件，EDRPOU值在使用软件的机器上面的应用数据中能找到。因此，在IsNewUpdate中注入的代码从应用数据中收集所有的RDRPOU值：一个M.E.Doc实例能被多个组织用于执行会计操作，，因此后门代码搜集所有可能的EDRPOU数字。

[![](https://p5.ssl.qhimg.com/t019d0916d60e29b158.png)](https://p5.ssl.qhimg.com/t019d0916d60e29b158.png)

后门还会收集代理和电子邮件设置，包括M.E.Doc应用的用户名和密码。

警告！我们推荐修改代理密码，并且修改M.E.Doc软件的所有的电子邮件账户。

恶意代码将收集的信息写入注册表项HKEY_CURRENT_USERSOFTWAREWC键的值Cred和Prx中。因此如果这些值存在于计算机中，很有可能有后门模块运行。

这里有最狡猾的一部分！后门模块不是用外部服务器作为C&amp;C：它使用M.E.Doc软件的常规更新请求（upd.me-doc.com[.]ua.）。和合法请求唯一的不同是后门代码在cookies中发送收集的信息。

[![](https://p5.ssl.qhimg.com/t011b20d4a3b986e6cd.png)](https://p5.ssl.qhimg.com/t011b20d4a3b986e6cd.png)

我们没有在M.E.Doc的服务器上面取证过。然而，正如之前一篇博文中的，有些迹象表明服务器沦陷了。因此我们能推测攻击者部署的服务器软件允许他们区分恶意和合法请求。

[![](https://p4.ssl.qhimg.com/t01125129422bb1d001.png)](https://p4.ssl.qhimg.com/t01125129422bb1d001.png)

并且，攻击者能添加控制受感染的计算机。代码接收一个二进制的官方的M.E.Doc服务器，使用3DES算法解密，再使用GZip解压。结果是一个XML文件，包含服务器命令。远程控制的功能使得后门功能齐全。

[![](https://p0.ssl.qhimg.com/t01a1fd48415f228cd8.png)](https://p0.ssl.qhimg.com/t01a1fd48415f228cd8.png)

下面是可能的命令行的表格：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b38f50d64834d42a.png)

注意command 5，被恶意软件作者命名为AutoPayload，完美的符合了DiskCoder.C在“patient zero”机器上的执行方式。

[![](https://p2.ssl.qhimg.com/t011b2d9023062a78b6.png)](https://p2.ssl.qhimg.com/t011b2d9023062a78b6.png)

<br>

**0x02 总结**



正如我们的分析，这是一次有计划的攻击。我们假设攻击者可以访问M.E.Doc的源代码。他们有时间学习代码并且整合一个非常隐蔽且狡猾的后门。M.E.Doc的全部安装是1.5G，我们没有方法去验证是否还有其他的注入的后门。

有些问题需要回答。这个后门使用了多久？DiskCoder.C或Win32 / Filecoder.AESNI.C以外的哪些命令行和恶意软件通过这个方式推送了？有没有其他的软件更新参与其中？

<br>

**0x03 IOCs**



1. ESET检测名:

MSIL/TeleDoor.A

2. 恶意软件作者使用的合法服务器：

upd.me-doc.com[.]ua

3. SHA-1 hashes:

7B051E7E7A82F07873FA360958ACC6492E4385DD

7F3B1C56C180369AE7891483675BEC61F3182F27

3567434E2E49358E8210674641A20B147E0BD23C



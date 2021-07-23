> 原文链接: https://www.anquanke.com//post/id/83960 


# mana中的mac地址随机化处理


                                阅读量   
                                **86402**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.sensepost.com/blog/2016/handling-randomised-mac-addresses-in-mana/](https://www.sensepost.com/blog/2016/handling-randomised-mac-addresses-in-mana/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01f6c93dfee232c566.jpg)](https://p0.ssl.qhimg.com/t01f6c93dfee232c566.jpg)

mana的发展步伐一直很迅速,但是OffSec团队礼貌地请求我们把mana恢复至之前的合适版本,[1.3.1-Fixy McFixface](https://github.com/sensepost/mana/releases/tag/1.3.1)是我们在2014年10月第一个正式版本之后,推送的许多的更新之中的一个。在之前的发布页面[1.3-WPE &amp; ACLs](https://github.com/sensepost/mana/releases/tag/v1.3)上用很长的篇幅详细说明了更新内容,其中包括WPE扩展功能,该功能受启发于Brad Antoniewicz's从对其的破解工作。

在我们最初发布mana的时候,iOS设备已经开始使用少量探针,他们正准备使用使用随机MAC地址探针(但并未正式使用),而据我们所知,Android在当时已经修复了在低电量模式下的探针泄露漏洞 。这就是我们创建[loud mode](https://www.sensepost.com/blog/2015/improvements-in-rogue-ap-attacks-mana-1-2/)的原因。

从那时起,iOS , OSX ,部分Windows系统系统以及Android设备开始使用随机化MAC地址,用于探寻首选网络列表(PNL)之中的具体网络。当时的loud模式已经可以满足这一点,因为loud模式能够自己记录下使用随机MAC地址探寻到的ESSID,然后对这些网络进行响应,并将它们重新广播至非随机化MAC地址之上,但是这会现一些小问题—均衡性。

从原理上讲,mana在loud模式中能达到最好效果,因为它记下所有设备上的探针,并使用它们对所有设备进行回复。这意味着网络设备保存下来了,当下次再需要时就不用再重新探寻。但是这也意味着你可以对你周围所有的设备进行攻击,不过这个特性只有在你想犯法的时候才看起来吸引人。

有一条很重要的更新内容是mana开始使用MAC地址过滤(MAC ACL)。然而,这个特性只有在关联阶段有效,而且在设备发现或者尝试连接恶意网络时并不发出任何阻止操作。因而我们提供一个可将[MAC ACL扩展为管理封包](https://github.com/sensepost/hostapd-mana/blob/master/hostapd/hostapd.conf)的选项。你可以在自己的设备上有效地将恶意AP设置为不可见状态(我不太明白为什么正常的AP不这样做)。

在这一点上,mana做得相当好,但是从数量上讲,mana可见的网络探针,尤其是从随机MAC地址发出的网络探针数目大大减少了。有时你可能需要允许某个特定厂商的所有MAC地址(例如当目标机构使用戴尔笔记本),这时显式的ACL便成为了一件麻烦事了,因为你只知道这些设备的OUI,为了解决这个问题,我们同时兼容为MAC ACL添加二进制掩码(衍生于airodump-ng的[掩码功能](http://aircrack-ng.org/doku.php?id=airodump-ng))。我们在源码中给出了一些[例子](https://github.com/sensepost/hostapd-mana/blob/master/hostapd/hostapd.accept),你可以在hostapd.accpt/deny文件中添加一些自定义的规则,格式为&lt;MAC地址&gt;&lt;掩码&gt;:

02:00:00:00:00:00 02:00:00:00:00:00

11:22:33:00:00:00 ff:ff:ff:00:00:00

aa:bb:cc:dd:ee:ff

以上例子可匹配所有随机MAC地址(将MAC地址的第一个八位第二位置为1,表示一个本地管理的MAC地址),并且可以匹配OUI为11:22:33的所有设备,以及MAC地址为aa:bb:cc:dd:ee:ff的设备。

如果以上的访问控制列表以白名单模式下,那么你便可以看到所有从随机MAC地址发出的所有网络探针,如果当前处于loud模式中,则会把这些探针重新广播至你的目标设备(而非其他设备),那么,均衡性问题便不会再影响mana的性能了。

正如我上文所介绍的,具体发布内容在[GitHub](https://github.com/sensepost/mana/releases/tag/1.3.1)上,在其中还包括了一些二进制包。

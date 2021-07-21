> 原文链接: https://www.anquanke.com//post/id/85148 


# 【技术分享】30秒内获取macOS的FileVault2密码（含演示视频）


                                阅读量   
                                **96056**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.frizk.net
                                <br>原文地址：[http://blog.frizk.net/2016/12/filevault-password-retrieval.html](http://blog.frizk.net/2016/12/filevault-password-retrieval.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0176bef14f6d3c2413.jpg)](https://p3.ssl.qhimg.com/t0176bef14f6d3c2413.jpg)



**翻译：**[**m6aa8k ******](http://bobao.360.cn/member/contribute?uid=2799685960)

**预估稿费：150RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**前言**

当前，攻击者只要将价值300美元的Thunderbolt设备插入锁屏或休眠中的mac电脑，就能获得macOS的FileVault2明文密码。只要有了这个密码，他们就可以解锁mac电脑并访问机器中的一切东西了。要想保护你的mac的话，需要将它更新至2016年12月的补丁。

任何人，包括但不限于你的同事、警察、邪恶的女佣和小偷，只要能够以物理方式接触你的mac电脑，他们就有机会获取机器中的所有数据，除非你苹果电脑已经处于完全关机的状态。如果你的苹果电脑正好处于休眠状态的话，就会受到这种漏洞的威胁。

攻击者只需要若无其事的走到一台锁屏的mac机器旁边，插入Thunderbolt设备，强制重新启动（ctrl+cmd+power），稍等片刻（不会超过三十秒），密码就会显示出来！

<br>

**演示视频**





**这怎么可能？**

这个安全漏洞主要是由两个独立的问题造成的：

第一个问题是mac在macOS启动之前，无法抵御直接内存访问（DMA）攻击。先于macOS运行的EFI将启用Thunderbolt接口，从而为恶意设备读写内存提供了机会。在这个阶段，macOS尚未启动，它还驻留在加密的磁盘上——要想启动的话，必须先将其解密。macOS一旦启动，就会默认启用DMA保护。

第二个问题是FileVault的密码是以明文形式存储在内存中的，并且在硬盘解锁之后，该密码也不会从内存中自动删除。该密码在内存中的保存地址有多处 ，好像每次重启时其位置都会变，但是无论怎么变，也不会超出一个特定的地址范围。

正是以上原因，导致攻击者只需插入DMA攻击硬件并重新启动mac，就能轻松获取FileVault2的密码。一旦mac重新启动，macOS启用的DMA保护机制将被禁用，但是内存中包括密码所有内容，仍在那里。这些包含密码的内存被新内容覆盖之前，会保留几秒钟的时间。对攻击者来说，这些时间已经够用了。

[![](https://p0.ssl.qhimg.com/t014038a6285e59cc61.jpg)](https://p0.ssl.qhimg.com/t014038a6285e59cc61.jpg)

连接到受害MAC机器上的PCILeech DMA攻击硬件

连接PCILeech硬件后，就可以在攻击者的计算机上运行mac_fvrecover 命令了。

[![](https://p0.ssl.qhimg.com/t01f2b465f00234e820.png)](https://p0.ssl.qhimg.com/t01f2b465f00234e820.png)

利用PCILeech获取FileVault密码。正确的密码为DonaldDuck。

 

**深入分析**

输入的密码将会以unicode编码的形式保存在内存中。如果密码完全由ascii字符组成，那么相应的第二个字节就会都是零。在提示输入密码的时候，请键入一个“随机的”口令，当然在内存中，这个口令肯定不是屏幕上看到的样子。在本示例中，使用的口令为eerrbbnn。在内存中，它被存储为6500650072007200620062006e006e。在使用PCILeech软件搜索这个口令的时候，会找到多个存储位置。

[![](https://p1.ssl.qhimg.com/t01e2465ffc36172548.png)](https://p1.ssl.qhimg.com/t01e2465ffc36172548.png)

在mac内存中搜索测试口令eerrbbnn

找到相应的内存位置后，我们就可以从中查找密码了。如果第一次读取失败，有时候需要将攻击设备重新连接到mac上面。

我们检查一下上面地址中的内容就会发现，密码以明文形式赫然在目。除此之外，这里还可以找到扫描出来的其他签名，例如例下面内存页开头部分的phd0。

[![](https://p5.ssl.qhimg.com/t01f35c941dea5aedf6.png)](https://p5.ssl.qhimg.com/t01f35c941dea5aedf6.png)

保存在某内存位置中的明文密码

**<br>**

**我能亲自试一下吗？**



是的，当然可以。你可以从Github下载PCILeech，并购买相应的硬件。实验证明，这种攻击方法可以在多种macbook和macbook airs（所有支持Thunderbolt 2接口）型号上面奏效。但是，我们还没有对最新的提供USB-C接口的mac进行相应的安全测试。

如果用户在密码中使用特殊字符（非ASCII），则无法直接通过这种攻击方法取得FileVault2密码。在这些情况下，可以将内存中的内容转储到文件上面，然后通过手工的方式查找相应的密码。

请注意，不要在别人mac上面尝试这些事情，这是非法的。

<br>

**其他注意事项**



如果你的mac还没有安装最新的安全补丁的话，除了可能泄露密码之外，还可能受到与这个漏洞有关其他各种攻击。由于EFI内存可以被覆盖，所以攻击者可以利用这个漏洞干更邪恶的……

<br>

**时间轴**

7月底：发现问题。

8月5日：在DEF CON 24大会上发布了PCILeech软件。

8月15日：苹果接到通知。

8月16日：苹果确认问题，要求暂缓披露。

12月13日：苹果发布了包含安全更新的macOS 10.12.2。

<br>

**结束语**



针对这个安全问题，苹果已经推出了一个完整的解决方案——至少在我看来是完整的。目前，攻击者已经无法在macOS引导之前访问内存了。因此，在防御这种攻击向量方面，mac可谓是最安全的平台之一。

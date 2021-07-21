> 原文链接: https://www.anquanke.com//post/id/85293 


# 【技术分享】MM CORE内存型后门回归“BigBoss”和“SillyGoose”


                                阅读量   
                                **113666**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blogs.forcepoint.com
                                <br>原文地址：[https://blogs.forcepoint.com/security-labs/mm-core-memory-backdoor-returns-bigboss-and-sillygoose](https://blogs.forcepoint.com/security-labs/mm-core-memory-backdoor-returns-bigboss-and-sillygoose)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01ce4692f67fe41354.png)](https://p0.ssl.qhimg.com/t01ce4692f67fe41354.png)

****

**翻译：**[**myswsun******](http://bobao.360.cn/member/contribute?uid=2775084127)

**预估稿费：100RMB**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

**<br>**

**0x00 介绍**

在2016年10月Forcepoint安全实验室发现了一个新版本的MM Core后门。也叫做“BaneChant“，MM Core是没有文件形态的APT，通过一个下载组件在内存中执行。在2013年它第一个版本”2.0-LNK“首次被披露，在它的C&amp;C服务器请求中有”BaneChant“特征。第二个版本”2.1-LNK“的网络标记是”StrangeLove“。

在本文中我们我们发现的另两个版本，“BigBoss“（2.2-LNK）和”SillyGoose“（2.3-LNK）。”BigBoss“被发现于2015年中旬，”SillyyGoose“被发现于2016年9月。两个版本都还存活着。

**攻击目标区域和工业**

在2013年的报告中攻击目标是中东和中亚国家。我们发现最近的目标是非洲和美国。下面的列表是一些目标工业：

新闻媒体

政府

石油天然气

通信

**MM Core的功能**

MM Core后门的功能如下：

发送被感染系统的计算机名，Windows版本，系统时间，运行的进程，TCP/IP配置，和C盘到H盘的顶层目录

下载执行文件

下载在内存中执行文件

自我更新

自我卸载

<br>

**0x01 感染方法**

以前MM Core下载组件通过CVE-2012-0158漏洞溢出的shellcode下载执行。然而新的DOC溢出通过CVE-2015-1641漏洞释放嵌入的恶意程序。这个被释放的恶意程序通过Dll side-loading漏洞执行。

我们分析的这个DOC文档（SHA1：d336b8424a65f5c0b83328aa89089c2e4ddbcf72）的名字是“US pak track ii naval dialogues.doc”。这个文档利用CVE-2015-1641并且执行shellcode释放一个绑定了名为“ChoiceGuard.dll”木马DLL的合法的可执行文件。然后shellcode执行这个可执行文件，导致这个恶意的dll通过“side-loading”被加载。这个dll下载和在内存中执行没有文件形态的MM Core后门。后门隐藏在一个JPEG文件中。这个JPEG文件包含代码用[Shikata ga nai](https://www.rapid7.com/db/modules/encoder/x86/shikata_ga_nai)算法解密它自己。

[![](https://p4.ssl.qhimg.com/t01a06ad675f7380708.png)](https://p4.ssl.qhimg.com/t01a06ad675f7380708.png)

一旦在内存中被解密执行，在第一次启动时这个MM Core后门将释放和安装一个嵌入的下载器，同时添加到Windows启动目录实现自启动。这个下载器和第一个木马dll类似，然后再次执行并下载MM Core JPEG，并在内存中执行。这次MM Core将创建后门处理函数发送系统信息并等待更多的命令。

感染过程概述如下：

[![](https://p1.ssl.qhimg.com/t0128460b7eadf7a0fc.png)](https://p1.ssl.qhimg.com/t0128460b7eadf7a0fc.png)

<br>

**0x02 可靠的证书**

我们发现一些下载者组件（如ChoiceGuard.dll）用一个来自俄罗斯组织“BorPort”的有效的证书签名：

[![](https://p3.ssl.qhimg.com/t0171b543190209edbc.png)](https://p3.ssl.qhimg.com/t0171b543190209edbc.png)

我们怀疑这可能是一个被盗证书，因为作者不可能用他们自己的组织的证书。

<br>

**0x03 更新内容**

新版的MM Core版本、互斥量、文件名、如下：

[![](https://p5.ssl.qhimg.com/t0196e0323b3f3419a4.png)](https://p5.ssl.qhimg.com/t0196e0323b3f3419a4.png)

<br>

**0x04 逃逸策略**

MM Core做了很多努力阻止安全研究者跟踪分析。新版本的C&amp;C服务器用需要登记的隐私保护服务。这个使得用WHOIS数据跟踪结构变得困难。

同时在BigRock（流行的网络服务公司）上面注册了他们的域名，这些域名混合在合法的网站中。

<br>

**0x05 总结**

MM Core是一个还存活的攻击多个国家和企业的威胁。有趣的是发现MM Core的版本增加了两次，但是核心后门代码还是保留了几乎相同的文件名和互斥量名。最大的原因可能是由于无文件形态，也解释了为什么主要是更新了传播机制。攻击这很清楚他们要做什么，做了足够的更新来保证这些年攻击的持续有效。

另一方面，MM Core和Gratem分享了代码、技术、网络架构，同时也和最近的一些样本分享了相同的证书。Gratem是从至少2014年来更加活跃。最后我们怀疑MM Core可能还有很多动作没有被发现。

<br>

**0x06 IOCS**

Documents

```
d336b8424a65f5c0b83328aa89089c2e4ddbcf72 (US pak track ii naval dialogues.doc)
```

Dropper/Downloader Samples (SHA1)

```
f94bada2e3ef2461f9f9b291aac8ffbf81bf46ab
ef59b4ffc8a92a5a49308ba98cb38949f74774f1
1cf86d87140f13bf88ede74654e01853bae2413c
415ad0a84fe7ae5b88a68b8c97d2d27de5b3aed2
e8bfa4ed85aac19ab2e77e2b6dfe77252288d89b
f94bada2e3ef2461f9f9b291aac8ffbf81bf46ab
83e7b2d6ea775c8eb1f6cfefb32df754609a8129
b931d3988eb37491506504990cae3081208e1a66
7031f4be6ced5241ae0dd4315d66a261f654dbd6
ab53485990ac503fb9c440ab469771fac661f3cc
b8e6f570e02d105df2d78698de12ae80d66c54a2
188776d098f61fa2c3b482b2ace202caee18b411
e0ed40ec0196543814b00fd0aac7218f23de5ec5
5498bb49083289dfc2557a7c205aed7f8b97b2a8
ce18064f675348dd327569bd50528286929bc37a
3a8b7ce642a5b4d1147de227249ecb6a89cbd2d3
21c1904477ceb8d4d26ac9306e844b4ba0af1b43
f89a81c51e67c0bd3fc738bf927cd7cc95b05ea6
```

MM Core Unpacked DLL Samples (SHA1)

```
13b25ba2b139b9f45e21697ae00cf1b452eeeff5
c58aac5567df7676c2b08e1235cd70daec3023e8
4372bb675827922280e8de87a78bf61a6a3e7e4d
08bfdefef8a1fb1ea6f292b1ed7d709fbbc2c602
```

Related Gratem Samples (SHA1)

```
673f315388d9c3e47adc280da1ff8b85a0893525
f7372222ec3e56d384e7ca2650eb39c0f420bc88
```

Dropper/Downloader Payload Locations

```
hxxp://davidjone[.]net/huan/normaldot.exe
```

MM Core Payload Locations

```
hxxp://mockingbird.no-ip[.]org/plugins/xim/top.jpg
hxxp://presspublishing24[.]net/plugins/xim/top.jpg
hxxp://ichoose.zapto[.]org/plugins/cc/me.jpg
hxxp://presspublishing24[.]net/plugins/cc/me.jpg
hxxp://waterlily.ddns[.]net/plugins/slm/pogo.jpg
hxxp://presspublishing24[.]net/plugins/slm/pogo.jpg
hxxp://nayanew1.no-ip[.]org/plugins/xim/top.jpg
hxxp://davidjone[.]net/plugins/xim/top.jpg
hxxp://hawahawa123.no-ip[.]org/plugins/xim/logo.jpg
hxxp://davidjone[.]net/plugins/xim/logo.jpg
```

MM Core C2s

```
hxxp://presspublishing24[.]net/plugins/cc/mik.php
hxxp://presspublishing24[.]net/plugins/slm/log.php
hxxp://presspublishing24[.]net/plugins/xim/trail.php
```

Gratem Second Stage Payload Locations

```
hxxp://adnetwork33.redirectme[.]net/wp-content/themes/booswrap/layers.png
hxxp://network-resources[.]net/wp-content/themes/booswrap/layers.png
hxxp://adworks.webhop[.]me/wp-content/themes/bmw/s6.png
hxxp://adrev22[.]ddns.net/network/superads/logo.dat
hxxp://davidjone[.]net/network/superads/logo.dat
```

> 原文链接: https://www.anquanke.com//post/id/83561 


# CTB-Locker重出江湖


                                阅读量   
                                **79232**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://securelist.com/blog/research/73989/ctb-locker-is-back-the-web-server-edition/](https://securelist.com/blog/research/73989/ctb-locker-is-back-the-web-server-edition/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p3.ssl.qhimg.com/t01a184f391bd2e0794.jpg)](https://p3.ssl.qhimg.com/t01a184f391bd2e0794.jpg)

现在，Cryptolocker勒索软件已经变得越来越复杂了，它们甚至可以绕过系统的保护措施，然后扫清道路上的全部障碍。TeslaCrypt，CryptoWall，TorrentLocker，Locky以及CTB-Locker等勒索软件只是我们在过去两年时间中所发现的主要几款勒索软件，我们针对这些勒索软件的性质和工作机制进行了分析，并给用户提供了一定程度上的保护。我们已经见识过很多不同类型的勒索软件了，但是这一新型的[CTB-Locker](https://securelist.com/analysis/publications/64608/a-new-generation-of-ransomware/)变种却是一种完全不同的东西。现在，全世界的网络犯罪分子们都在想办法去重塑勒索软件，并利用新型的勒索软件来为自己创造利益。

与其它勒索软件不同的是，CTB-Locker（或者Onion勒索软件）会使用Tor匿名网络来为其操作进行掩护，因为这个勒索软件在控制目标服务器的时候非常依赖静态的恶意软件指令。除此之外，Tor网络还可以帮助它们躲避安全保护系统的检测和屏蔽。最关键的一点是，CTB-Locker的控制器只会接收比特币的交易信息，这也就为CTB-Locker撑起了一把天然的保护伞。

CTB-Locker，即比特币敲诈病毒。2015年5月1日， CTB-Locker在国内爆发式传播，攻击者可以利用该病毒远程加密用户电脑文件，从而向用户勒索赎金，用户文件只能在支付赎金后才能打开。反病毒专家称，目前国内外尚无法破解该病毒。

这一CTB-Locker的新型变种只会针对网站服务器进行攻击，据我们目前所收集到的数据显示，这款勒索软件已经成功地对十个国家的[70多台网站服务器](http://www.kernelmode.info/forum/viewtopic.php?p=27921#p27917)进行了攻击，并对目标网络服务器中的系统文件进行了加密。

[![](https://p1.ssl.qhimg.com/t01ba1f55fa9118f073.png)](https://p1.ssl.qhimg.com/t01ba1f55fa9118f073.png)

在这篇文章中，我将会带你深入“虎穴”，并对这款勒索软件进行详细的分析。在此，我还要向那些愿意向我们提供这款勒索软件攻击实例的受害者们表示感谢。

**篡改网站信息**

这一新型变种的攻击目标主要是网站服务器，它在对服务器中的文件进行了加密之后，会要求受害者支付价值大约为150美金的比特币作为赎金。如果赎金没有按时支付，那么勒索的赎金将会翻倍，所以赎金将会上涨至300美金。当受害者支付了赎金之后，攻击者会生成一个密钥，用户可以使用这个密钥来对网站服务器中的文件进行解锁。

而且很明显，网站服务器之所以会感染这个勒索软件变种，是因为在目标网站服务器中存在一个安全漏洞。当攻击者成功利用了这一漏洞之后，网站信息将会被篡改。而且大多数的黑客组织都会利用这种方法来向攻击目标传递他们所要表达的内容。而就我们目前所观察到的所有此类事件，我们认为这些都并非偶然，因为其中大多数的攻击都是与政治局势和文化冲突等因素有关。

[![](https://p5.ssl.qhimg.com/t012509608bea71937f.png)](https://p5.ssl.qhimg.com/t012509608bea71937f.png)

正如上图所示，网站服务器在受到了攻击之后，其网站主页会被替换。因为攻击者通常会使用网站首页来作为他们传播信息的载体，他们会在首页中添加所有需要表达的内容。我们将会在之后的章节中对这一部分的内容进行深入讨论。

除此之外，我们还需要注意的一点就是，网站的源代码并没有被删除，网站源代码仍然存储在服务器的根目录之中，只是文件名被修改了，而且所有的文件也被加密了。

**攻击者传递的信息**

相比于赎金，用户更关心他们服务器中的数据和内容，而攻击者也明白这一点。这一勒索软件正是抓住了这一关键点，所以攻击者才会愿意将时间花在勒索软件身上。为了让所有用户都能够了解到他们所处的困境，攻击者通常都会在网站首页中留下非常详细的信息。

下图显示的是攻击者留在网站首页中的部分信息：

[![](https://p3.ssl.qhimg.com/t01f1b7042b3285c4a5.png)](https://p3.ssl.qhimg.com/t01f1b7042b3285c4a5.png)

解密密钥存储在一个远程服务器中，但是攻击者会“慷慨地”允许受害者免费对两个文件进行解锁，并以此来说明其真实性。

当服务器被攻击之后，攻击者还会在目标网站中留下另外一个功能。这个功能允许受害者直接与攻击者进行联系，但是这个功能需要一个用户标识码，所以只有这名受害者才可以与攻击者进行交谈。

[![](https://p5.ssl.qhimg.com/t01be91cddc32314f2b.png)](https://p5.ssl.qhimg.com/t01be91cddc32314f2b.png)

**加密过程**

目前我们仍不清楚攻击者到底是如何将CTB-Locker部署至目标服务器之中的，但是所有受到攻击的服务器都有一个共同特点－它们使用了WordPress平台来作为网站的内容管理工具。在未更新的WordPress中包含有大量的安全漏洞，而且在去年也有很多[相关漏洞](http://blog.checkpoint.com/2015/08/04/wordpress-vulnerabilities-1/)被曝光了出来。除此之外，WordPress还有一个致命的弱点，那就是插件。这些插件能够给WordPrss网站添加很多增强功能，而正是这一点，才使得WordPress成为了目前世界上使用人数最多的内容管理系统。但是，如果第三方插件的作者没有在插件中添加必要的安全保护措施，那么安装这类插件也会使得网站更加容易受到黑客的攻击。

当攻击者入侵了WordPress系统之后，他就可以替换掉网站的主要文件，修改网站核心文件的文件名，并对这些文件进行加密处理。

攻击者会使用两个不同的AES-256密钥来对目标服务器中的文件进行加密：

1.     create_aes_cipher($keytest)－用于对那两个可以免费解锁的文件进行加密；

2.     create_aes_cipher($keypass)－用于对网站根目录下其余的文件进行加密；

[![](https://p4.ssl.qhimg.com/t013d81786a5a3cbdd2.png)](https://p4.ssl.qhimg.com/t013d81786a5a3cbdd2.png)

这两个可以免费解锁的文件是由攻击者指定的，它们的文件名会被存储在一个文本文件之中。

create_aes_cipher()能够接收一个参数，并将其用作密钥，然后将信息发送给标准的Crypt_AES()函数进行处理：

```
function create_aes_cipher($key) `{`
         $aes = new Crypt_AES();
         $aes–&amp;gt;setKeyLength(256);
         $aes–&amp;gt;setKey($key);
         return $aes;
`}`
```

当攻击者完成了对网站文件的加密处理之后，恶意脚本会使用测试密钥来对那两个可以免费解锁的文件进行加密。完成之后会生成一个含有对应文件扩展名的文件列表，然后攻击者会使用AES-256加密算法来进行加密。

[![](https://p3.ssl.qhimg.com/t0152dc656365e0d32c.png)](https://p3.ssl.qhimg.com/t0152dc656365e0d32c.png)

在网站首页中，攻击者还会使用JQuery来向代理服务器发送查询请求，并且验证赎金的支付信息。我们在主页的源代码中发现了下图所示的代码段，第一行代码列出的就是代理服务器的信息：

[![](https://p0.ssl.qhimg.com/t017ff625cfd5760cea.png)](https://p0.ssl.qhimg.com/t017ff625cfd5760cea.png)

代理服务器的信息也是解密过程的一部分：

```
http://erdeni.ru/access.php
http://studiogreystar.com/access.php
http://a1hose.com/access.php
```

**免费解锁**

勒索软件允许受害者免费解锁文件，但是可以免费解锁的文件数量不会超过两个。受害者无法选择这两个文件，因为这两个文件是由攻击者事先就已经选定了的，而这一信息也可以从上述的恶意代码中看到。实际上，这两个文件是攻击者在对网站文件进行加密的过程中随机选取的。

下图显示的是免费解密模块的相关内容：

[![](https://p3.ssl.qhimg.com/t01e2fa55a54dc0a4e5.png)](https://p3.ssl.qhimg.com/t01e2fa55a54dc0a4e5.png)

[![](https://p2.ssl.qhimg.com/t01afb206aa480b6763.png)](https://p2.ssl.qhimg.com/t01afb206aa480b6763.png)

**我们的建议**

我们强烈建议用户定期更新网站中的安全软件。除此之外，网站的开发人员应该尽量避免从不信任的来源获取第三方插件。并且建议用户定期备份服务器中所有的重要数据，并且小心所有的电子邮件和广告，因为攻击者也可以通过这些内容来对服务器进行攻击。

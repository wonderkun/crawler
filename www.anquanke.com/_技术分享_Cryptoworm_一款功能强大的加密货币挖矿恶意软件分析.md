> 原文链接: https://www.anquanke.com//post/id/87051 


# 【技术分享】Cryptoworm：一款功能强大的加密货币挖矿恶意软件分析


                                阅读量   
                                **192159**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securityaffairs.co
                                <br>原文地址：[http://securityaffairs.co/wordpress/63488/malware/advanced-memory-cryptoworm.html](http://securityaffairs.co/wordpress/63488/malware/advanced-memory-cryptoworm.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01d3b5c76e27b2a0b0.jpg)](https://p1.ssl.qhimg.com/t01d3b5c76e27b2a0b0.jpg)





译者：[blueSky](http://bobao.360.cn/member/contribute?uid=1233662000)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿 

<br>

**前言**

****

本文我将分享一个关于某“有趣”恶意软件的分析，用“有趣”来形容该恶意软件，是因为该恶意软件拥有巧妙的漏洞利用能力、代码混淆能力以及使用了先进技术来窃取凭据和运行命令。

下图展示了整个攻击路径的总体情况。正如你在图中所看到的，由于整个攻击阶段中包含了很多特定的操作，因此整个攻击流程看起来非常的复杂。初始阶段开始于诱骗缺乏经验的用户点击一个初始阶段文件，我将该文件（在本例中）命名为y1.bat。目前，电子邮件载体是攻击者最喜欢使用的载体，它能轻易地被用来传递恶意内容。一旦初始阶段开始运行，它会下载并运行一个叫做info6.ps1的第二阶段文件，该文件是一个严重混淆过的PowerShell脚本，通过直接在代码体上解码混淆代码，我们可以获取三个内部资源模块：

1. Mimikatz.dll：这个模块用来窃取用户的管理凭据。

2. Utilities：这个模块用来扫描内网从而传播感染，它被用来运行几个内部工具，例如解码混淆例程、数组排序和运行漏洞程序，该模块也被用来生成并执行一个叫做info.vbs的文件。

3. Exploits：这个模块是由一些已知的漏洞程序组成的集合，例如在初始阶段的攻击中，为了感染内部机器用到的[eternalblue7_exploit](https://gist.github.com/worawit/bd04bad3cd231474763b873df081c09a) 和 [eternal_blue_powershell](https://github.com/tevora-threat/eternal_blue_powershell/blob/master/EternalBlue.ps1) 这两款工具。

 [![](https://p3.ssl.qhimg.com/t0188a7ee69378e8584.png)](https://p3.ssl.qhimg.com/t0188a7ee69378e8584.png)

全部阶段的攻击路径

info.vbs文件在运行的过程中会生成另外一个称为XMRig的文件，该文件是一个开源的Monero CPU Miner ，可以在GitHub上找到。XMRig模块会试图通过利用Exploit模块来扫描和攻击内部资源来传播自身，与此同时，该模块采用Monero加密方式，通过窃取受害者的资源来给攻击者提供新的“crypto money”。

<br>

**恶意软件分析**

****

攻击者将一封包含bat文件的email 或 message 传播给受害者，一旦用户点击了这个 bat文件，它将运行以下的命令使得PowerShell 能够下载并运行一个来自http://118.184.48.95:8000/的叫做info6.ps1 的脚本。

 [![](https://p2.ssl.qhimg.com/t01a139b071fbbd2288.png)](https://p2.ssl.qhimg.com/t01a139b071fbbd2288.png)

阶段1：下载并运行

下载的PowerShell文件被清晰地分为两个部分，它们都是被混淆过的。下图显示了两个区域，我将其命名为上半部份（在空行上方），和下半部分（空行下方）。

 [![](https://p4.ssl.qhimg.com/t01ce10a2213d5e6b66.png)](https://p4.ssl.qhimg.com/t01ce10a2213d5e6b66.png)

阶段2：两个待探查的部分

上半部份看起来很像是一个Base64编码的文本文件，下半部份看起来似乎是一个手工编写的编码函数，幸运的是，这个函数似乎是用明文追加到这个文件的尾部的。通过编辑这个函数，能够做到以下事情：能在优化解码过程中让已解码的文本文件直接被存到一个指定文件夹。下图显示了解码后的下半部分内容。

[![](https://p3.ssl.qhimg.com/t01c453c336e1e94fec.png)](https://p3.ssl.qhimg.com/t01c453c336e1e94fec.png)

 解码第二阶段中的下半部分

通过分析这部分的代码，可以很容易得出，该函数通过对当前内容执行子字符串操作，可以很容易地从文件自身动态的提取需要使用的主要功能。



```
$funs=$fa.SubsTrIng(0,406492)
$mimi=$fa.sUBStrInG(406494,1131864)
$mon=$fa.suBstrING(1538360,356352)
$vcp=$fa.sUBStRiNG(1894714,880172)
$vcr=$fa.sUBstrINg(2774888,1284312)
$sc=$fa.sUBsTrinG(4059202)
```

$fa变量的值与之相关的所有函数都是放在上半部分的，它们解码后如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c63a034b4c6d1d79.png)

解码后的上半部分

第二阶段的上半部分代码是从Kevin Robertson (Irken)处复制来的，这个攻击者从Irken那里套用了很多有用的部分，包括Invoke-TheHas例程，它可以通过SMB被用来运行命令或具有特殊权限的代码。

在同一个阶段（第二阶段的下半部分），我们找到了一行非常有趣的代码： NTLM= Get-creds mimi ，此处Get-creds函数（它来自Based64编码的上半部分）的运行采用了反射技术，即一个DLL函数。所以从定义上讲，mimi 变量必须是一个包含在代码中某处的DLL文件。让我们通过运行下列代码来找到它：$fa.sUBStrInG(406494,1131864) ，此处的406494是起始字符，而1131864是结束字符，它们被解读后将指向一个动态链接库中。幸运的是，这个生成的DLL是一个知名的库，它广泛地被用于Mimikatz渗透测试中。所以以下事实是非常清楚的：攻击者使用了Mimikatz库来抓取用户密码（最终会抓取管理员密码）。一旦密码窃取动作完成，Malware会开始扫描内网中的已知漏洞，例如MS17/10。我发现的这个漏洞程序是套用的tevora-thrat 和 woravit，因为它们具有相同的代码、注释和变量名。如果这个恶意软件（Malware）找到了一个本地网络的漏洞，它会试图通过使用EthernalBlue注入其自身(info6.ps1)来感染这台机器，之后它会开始第二阶段的运行。

在同一个线程上恶意软件生成并执行一个.vbs文件（第三阶段），然后它通过服务器中的WMIClass一直留存下去。

[![](https://p2.ssl.qhimg.com/t01addd470f35684ecd.png)](https://p2.ssl.qhimg.com/t01addd470f35684ecd.png)

引入第三阶段

info.vbs 从其自身生成并执行一个编译版本的XMRIG，然后用“mimetic”字符串为其重命名为taskservice.exe. 一旦编译好的PE 文件 (XMRig) 被置于内存中，新的阶段就会通过运行下列命令来启动它。

 [![](https://p5.ssl.qhimg.com/t0156f69dbcbe7a66f6.png)](https://p5.ssl.qhimg.com/t0156f69dbcbe7a66f6.png)

第三阶段Monero Miner 的执行

Monero 的文本地址在上面的代码中清晰可见。但目前这个地址无法追踪，地址信息如下所示： 

46CJt5F7qiJiNhAFnSPN1G7BMTftxtpikUjt8QXRFwFH2c3e1h6QdJA5dFYpTXK27dEL9RN3H2vLc6eG2wGahxpBK5zmCuE

使用的服务器是：stratum+tcp://pool.supportxmr.com:80

```
w.run “%temp%taskservice.exe  -B
 -o stratum+tcp://pool.supportxmr.com:80 -u  46CJt5F7qiJiNhAFnSPN1G7BMTftxtpikUjt8QXRFwFH2c3e1h6QdJA5dFYpTXK27dEL9RN3H2vLc6eG2wGahxpBK5zmCuE 
 -o stratum+tcp://mine.xmrpool.net:80  -u  46CJt5F7qiJiNhAFnSPN1G7BMTftxtpikUjt8QXRFwFH2c3e1h6QdJA5dFYpTXK27dEL9RN3H2vLc6eG2wGahxpBK5zmCuE 
 -o stratum+tcp://pool.minemonero.pro:80   -u  46CJt5F7qiJiNhAFnSPN1G7BMTftxtpikUjt8QXRFwFH2c3e1h6QdJA5dFYpTXK27dEL9RN3H2vLc6eG2wGahxpBK5zmCuE -p x” ,0
```



**IOCs**

****

– URL: http://118.184.48.95:8000/

– Monero Address: 46CJt5F7qiJiNhAFnSPN1G7BMTftxtpikUjt8QXRFwFH2c3e1h6QdJA5dFYpTXK27dEL9RN3H2vLc6eG2wGahxpBK5zmCuE

– Sha256: 19e15a4288e109405f0181d921d3645e4622c87c4050004357355b7a9bf862cc

– Sha256: 038d4ef30a0bfebe3bfd48a5b6fed1b47d1e9b2ed737e8ca0447d6b1848ce309

<br>

**结论**

****

我们目前分析的是最初的且复杂的加密货币挖矿恶意软件的传送过程。所有人可能都知道CryptoMine, BitCoinMiner 和 Adylkuzz 等恶意软件，它们基本上是在目标机器上生成一个BitCoinMiner，其实货币类恶意软件传送的时候是没有传播模块、exploit模块，也没有使用无文件的技术。**但是，这个Monero CPU Miner在传送的时候就包括了针对内存inflation的高级技术，解压后的恶意软件并不存在硬盘上（这是一种绕过某些杀毒软件的技术）而是直接在内存解压，然后直接在内存调用其自身。**我们可以将这个恶意软件视为内存中的最后一代-CryptoWorm。从我个人的角度来看，另一个有趣的发现来自于第一阶段。为什么攻击者要保留这个没有用的阶段呢？看起来这个阶段完全没有用，它就是一个生成器，它既没有控制功能也不释放任何的drop程序。攻击者可以在第一阶段直接传输第二阶段的内容，还能保证网络指纹更隐秘，所以为什么攻击者要通过第一阶段来传送这个CryptoWorm呢？也许第一阶段是某个更大的框架的一部分？或许我们正在面对的是新一代的恶意软件，现在我或许还不能够回答这个问题，反之我希望读者们可以认真来思考这个问题。

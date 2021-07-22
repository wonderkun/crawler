> 原文链接: https://www.anquanke.com//post/id/104456 


# LockCrypt勒索软件：薄弱的恶意代码可导致文件恢复


                                阅读量   
                                **93506**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://blog.malwarebytes.com
                                <br>原文地址：[https://blog.malwarebytes.com/threat-analysis/2018/04/lockcrypt-ransomware/](https://blog.malwarebytes.com/threat-analysis/2018/04/lockcrypt-ransomware/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01ec4a994769fef6af.jpg)](https://p4.ssl.qhimg.com/t01ec4a994769fef6af.jpg)

## 一.写在前面的话

从今年年初开始，各大新闻网站频繁被挖矿木马刷屏。搞得其他恶意软件十分被动.然而，勒索软件并没有这么快就放弃。每隔几个月就会冒出个新的变种，刷刷存在感.

就目前来说，最受欢迎的勒索软件要属GandCrab。然而，自2017年6月以来，一个不太为人所熟知的名为“LockCrypt”的家族一直在暗中监视。但由于它必须通过手动安装RDP的方式来传播，所以它并不是一个巨大的威胁——因此从来没有被详细描述过。

但最近，一些LockCrypt的受害者联系了我们，所以我们决定仔细看看,我们发现软件的作者不滚动更新自己的密码，正因如此。我们可以轻易破解，并发现代码的弱点，找到存在恢复数据的可能性。接下来看看我们是如何分析的吧!



## 二.分析样本

[99a3d049f11474fac6844447ac2da430](https://www.virustotal.com/#/file/67c7b46aed4f9b505b492b700839609c39f05ac60c58fe320eca69316fe3a06c/community)



## 三.行为分析

为了正确运行，恶意软件必须以管理员的身份运行。但因为它是由攻击者手动部署的，所以它不会使用任何操作或漏洞来自动提升它的特权。一旦运行，它将删除原始样本，并将其自己部署在C:Windows名称下wwvcm.exe：

[![](https://p2.ssl.qhimg.com/t01442cad23141009ba.png)](https://p2.ssl.qhimg.com/t01442cad23141009ba.png)

为了增加了持久性它还申请了一个注册表项:

[![](https://p3.ssl.qhimg.com/t01f1fef4a827339ac1.png)](https://p3.ssl.qhimg.com/t01f1fef4a827339ac1.png)

这个勒索软件会对所有扫描到的文件进行加密。在过程中，它不断枚举并试图终止所有运行的应用程序，这样木马在感染其他文件就不会受到打扰了

[![](https://p2.ssl.qhimg.com/t01f53264fd45348d2f.png)](https://p2.ssl.qhimg.com/t01f53264fd45348d2f.png)

从上面的图片可以看出加密文件的名称是经过混淆的,它首先进行加密，然后转换为base64。我们发现名称的ID是随机的。并使用“1btc”的拓展名。<br>
值得注意的是:勒索信竟然是一份TXT文件!!

[![](https://p1.ssl.qhimg.com/t013958daf1cf4e9c25.png)](https://p1.ssl.qhimg.com/t013958daf1cf4e9c25.png)

他将在执行结束时弹出。<br>
在加密的文件中，我们看到它们的熵值相当高。下面的示例显示了加密前后的BMP文件:

[![](https://p4.ssl.qhimg.com/t018ec9f341ea722bc5.png)](https://p4.ssl.qhimg.com/t018ec9f341ea722bc5.png)<br>[![](https://p0.ssl.qhimg.com/t019a256c80e5127296.png)](https://p0.ssl.qhimg.com/t019a256c80e5127296.png)

我们对这幅图像的初步评估是，作者并没有在这里使用简单的XOR运算。它看起来像一个由流密码加密的文件(或CBC模式中的密码)。根据查看注册表，我们发现了勒索软件留下的更多数据，比如受害者的唯一ID：

[![](https://p4.ssl.qhimg.com/t0169628069dc8ff63c.png)](https://p4.ssl.qhimg.com/t0169628069dc8ff63c.png)



## 四.网络通信

恶意软件能够在没有Internet连接的情况下进行文件加密。但是，如果我们用一台联网的机器来运行，它就会向其CnC服务器发送信号。CnC IP为46.32.17.222（位于伊朗）。

下图为通讯的一部分：

[![](https://p3.ssl.qhimg.com/t01e84afc329b3b7c1c.png)](https://p3.ssl.qhimg.com/t01e84afc329b3b7c1c.png)

该bot发送关于攻击机信息的base64编码数据，比如随机ID、用户名、操作系统，以及恶意软件部署的路径。例子:<br>`WThSQVNVNDczUjZUMzVjNycsJ1dpbmRvd3MgNyBQcm9mZXNzaW9uYWx8dGVzdGVyfEM6XFVzZXJzXHRlc3RlclxEZXNrdG9wXGxvY2tjcnlwdC5leGU =`<br>
解码为：

`Y8RASU473R6T35c7','Windows 7 Professional|tester|C:UserstesterDesktoplockcrypt.exe`



## 五.内部代码

样品的外部没有任何加密，也没有被混淆。只要我们打开它，我们就能直接看到它里面的所有东西。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01858392dd80f4d36b.png)<br>
一开始，勒索软件会检查它处在的文件夹的位置。并试图在Windows文件夹里复制一份副本然后重新部署到那个位置。<br>
接着，它将创建一个线程，不断地列举所有正在运行的进程并尝试终止它们。<br>
它还会读取注册表来检查它是否已经正确部署。但是有一点要特别注意:找到合适的密钥可以阻止感染——恶意软件会识别出已经攻击过的机器。否则，它将继续进行下去。



## 六.加密

通过查看函数，我们现在可以理解在行为分析过程中所看到的神秘字节缓冲区的作用。下载的缓冲区通过其CRC32校验和验证。然后，它会设置一个全局变量来进一步运行加密程序。

[![](https://p5.ssl.qhimg.com/t019eea535e5a2dfd17.png)](https://p5.ssl.qhimg.com/t019eea535e5a2dfd17.png)<br>
事实证明，这个缓冲区就像一个用于加密模式的pad。作者可能想要实现类似于一次性的硬盘加密。但是，他们重用了缓冲区，因此，使得他们的算法容易受到攻击。<br>
并且出于某种原因，从Internet上下载缓冲区是不可能的，所以它是由一个简单的伪随机算法生成的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0131a064cbc9715802.png)

作者并没有对随机发生器做出最佳选择。他们也没有使用强大的密码，而是使用GetTickCount函数。<br>
在加密例程中，我们可以看到这个文件只是被一个非常简单的函数打乱了：

[![](https://p4.ssl.qhimg.com/t0191b71d4c235df233.png)](https://p4.ssl.qhimg.com/t0191b71d4c235df233.png)

该算法具有两个不同的回合。两轮的重建代码如下所示。

<a class="reference-link" name="%E7%AC%AC%E4%B8%80%E8%BD%AE"></a>**第一轮**

这一回合只使用XOR操作，但有一种操作使你无法恢复原始的钥匙。虽然输入的DWORD与关键字的DWORD相匹配，但输入也被之前的输出所污染。在每一步中，输入DWORD的前半部分都是从以前的输出中获取的，而只有下半部分是新鲜的。这就是一个简单的流密码。

<a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E8%BD%AE"></a>**第二轮**

这一轮看起来更复杂——不仅是XOR操作，还包括ROL和bitwise交换。但是，这次没有输入污染，所以很容易恢复。<br>
这两个简单的循环，加上一个2500字节的“pad”缓冲区，能够产生相当高的熵值。

<a class="reference-link" name="%E6%96%87%E4%BB%B6%E5%90%8D%E6%B7%B7%E6%B7%86%E3%80%82"></a>**文件名混淆。**

文件的名称首先使用pad缓冲区进行处理，然后使用base64编码。XOR键的偏移是从缓冲器的开始起1111个字符。<br>
负责这个的代码部分:

[![](https://p4.ssl.qhimg.com/t01ec87b0a9cc8f7ce7.png)](https://p4.ssl.qhimg.com/t01ec87b0a9cc8f7ce7.png)



## 七.结论

LockCrypt是由不成熟的攻击者创建和使用的一种简单勒索软件。它的作者忽略了正确使用密码学的指导方针。而且应用程序的内部结构也显不专业,当为手动分发创建勒索软件时，马虎，不专业的代码随处可见。这可能是因为作者不想花太多的时间准备攻击或payload。相反，他们专注于如何快速和轻松的获益，而不是用于长期创造财富。正因为如此，他们很容易被击败。

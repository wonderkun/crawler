> 原文链接: https://www.anquanke.com//post/id/85130 


# 【技术分享】嘿，你的wallet!


                                阅读量   
                                **117807**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t014cb90448615f26ad.jpg)](https://p1.ssl.qhimg.com/t014cb90448615f26ad.jpg)



**前言**



前段时间，Crysis敲诈者的同门——XTBL木马在服务器上的敲诈风波刚刚平息，新的一波Wallet服务器敲诈又再起波澜。Wallet木马最早出现在11月末，虽爆发规模不算大，但是由于是针对服务器的攻击，造成用户的损失着实不可估计。根据360互联网安全中心的分析发现，这次的Wallet虽然也是通过服务器传播，但是入侵者采用了更多样的手法——不再仅仅是对3389端口的简单扫描了，而是更有针对性的对服务器进行系统性攻击。

 

**样本分析**

****

**0x01 多样的加密方式**

首先，Wallet在加密文件的时候还是采用了SHA1算法。下图是SHA1算法的4轮20次循环——比较有代表性。

[![](https://p3.ssl.qhimg.com/t017eaed13569d59348.png)](https://p3.ssl.qhimg.com/t017eaed13569d59348.png)

图1.SHA1算法

不同的是Wallet不仅使用了RC4——还使用了RC4的变形——用来解密字符串和生成密钥。依然是RC4标准初始化方法，但加密的时的算法却有所异同，整体过程变得更为复杂。

[![](https://p2.ssl.qhimg.com/t0154ae8dff98b0af69.png)](https://p2.ssl.qhimg.com/t0154ae8dff98b0af69.png)

图2.RC4与RC4变形

中间还夹杂了一些简单的异或和移位进行字符串变换，如下：

[![](https://p2.ssl.qhimg.com/t013978fd12ab0daba2.png)](https://p2.ssl.qhimg.com/t013978fd12ab0daba2.png)

图3.异或移位

**0x02 加密本地和网络资源**

对网络资源，木马创建了一个单独的线程来枚举网络资源并对网络资源进行加密。

[![](https://p2.ssl.qhimg.com/t019476ff7bffdf3a09.png)](https://p2.ssl.qhimg.com/t019476ff7bffdf3a09.png)

图4.加密网络资源

值得一提的是：Wallet加密网络资源和加密本地资源的时候，采用了相同的密钥。

[![](https://p4.ssl.qhimg.com/t01b0414647d77ed577.png)](https://p4.ssl.qhimg.com/t01b0414647d77ed577.png)

图5.相同密钥

本地和网络采用的解密手法是一样的，先通过函数解密得到加密文件的后缀、敲诈信息文档等。然后生成密钥块，然后通过创建线程来加密文件。

[![](https://p0.ssl.qhimg.com/t0180cf770d65f60169.png)](https://p0.ssl.qhimg.com/t0180cf770d65f60169.png)

图6.加密文件

在对文件进行加密的时候，还是保留了以前的同时创建四个线程。来保证加密文件的效率和成功率、从而避免一个线程出现加密文件失败的情况导致程序不能完整的跑起来。

[![](https://p5.ssl.qhimg.com/t01103b546b8579dd5d.png)](https://p5.ssl.qhimg.com/t01103b546b8579dd5d.png)

图7.多线程

和XTBL不同的是变种Wallet在循环创建的四个线程下还新增加了一个线程，经过分析该线的主要作用遍历文件夹。遍历文件夹用一个单独的线程来做，提高了效率：

[![](https://p1.ssl.qhimg.com/t019f128c4fc53b797f.png)](https://p1.ssl.qhimg.com/t019f128c4fc53b797f.png)

图8.遍历文件夹

**0x03 密钥块的生成**

Wallet增强了密钥的强度，通过两次获取时间来得到随机数，两次得到的随机数分别与423C28处的数据进行异或，然后用SHA1算的其HASH值，并将该HASH值作为RC4的参数来算的加密文件的密钥。采用两次通过获取时间来算取随机数，在本来密钥相同概率极低的情况下变的更加的低了。

[![](https://p3.ssl.qhimg.com/t0121bdeb5edb0b6141.png)](https://p3.ssl.qhimg.com/t0121bdeb5edb0b6141.png)

图9.获取密钥

密钥块在原本184字节大小上增加了6个字节，在其末尾增加了标识位，邮箱，加密后文件的后缀等的地址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0154baf82314db17e6.png)

图10.密钥块

**0x04 其他细节**

1. 动态获取函数地址

[![](https://p3.ssl.qhimg.com/t018277bbfcf1b1b5d0.png)](https://p3.ssl.qhimg.com/t018277bbfcf1b1b5d0.png)

图11.获取函数

2. 删除卷影副卷

用RC4变形来对字符串进行解密得到cmd.exe的环境变量以及获取到删除卷影副卷的命令。然后通过创建管道来向进程cmd中写入命令来执行。不过大部分人都没有给自己的操作系统做备份习惯。所以感觉删除不删除其实影响不大。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016633bf615f2df120.png)

图12.删除卷影副卷

 

3. 关闭指定服务和结束指定进程

对通过解密获取到的服务名和进程名进行查找，如果找到就结束进程和关闭服务。

[![](https://p5.ssl.qhimg.com/t01a37dd682e00b6f10.png)](https://p5.ssl.qhimg.com/t01a37dd682e00b6f10.png)

图13.关闭特定服务和进程

4. 开机启动

用了两种方法来写启动项，但是都是特别直接的方法，第一种是将它直接写在了开启自启动的文件夹下，还有一种方法是写注册表。

**0x05 加密更多类型的文件**

被加密的文件的种类也是琳琅满目的。各种格式都有只有你想不到，没有他做不到。Wallet能加密的文件多达到324中，下图是该敲诈者能加密的文件后缀类型：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01dac17836d25c5df2.png)

图14.被加密文件

 

**0x06 被加密后的服务器**

文件全部被加密，有的程序都不能正常使用。被加密的文件名被修改成原始文件名加上敲诈者的联系邮箱，后缀全部被修改为.wallet。和写注册表一样来的直接。

[![](https://p0.ssl.qhimg.com/t017abcf3467c4dfdf3.png)](https://p0.ssl.qhimg.com/t017abcf3467c4dfdf3.png)

被加密后的桌面背景变成蓝色，桌面显示出一个Good morning ，可是大早上的看到这的真的好么？可想而知他们也是半夜偷偷的搞。

[![](https://p3.ssl.qhimg.com/t01ada555429bba04e7.png)](https://p3.ssl.qhimg.com/t01ada555429bba04e7.png)

 <br>

**总结**



之前国外公布了一批Crysis和XTBL用于解密的私钥，导致很多被中两类敲诈者加密的文件最终都使用安全厂商提供的工具成功解密了。而此次的Wallet木马却显得更加严防死守，截止到发稿时，还没有任何私钥流出的消息——也就是说，一旦中招就只能老老实实的交付赎金。

这也引发了我们对于服务器安全的深思：从数量上来说，服务器的数量可能没有个人电脑那么多；从木马传播量来看，XTBL家族的传播量也远不及同为敲诈者却主攻个人用户的Cerber家族来的泛滥。但服务器是用于公共服务的互联网技术设施，牵一发而动全身的位置——一旦陷落，损失将无法估量。从XTBL到Wallet，都一次次的给所有的服务器管理员和提供互联网服务的企业管理者敲响了警钟——安全，是互联网稳定运行的根本前提。

<br style="text-align: left">

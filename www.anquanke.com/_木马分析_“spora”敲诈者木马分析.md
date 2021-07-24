> 原文链接: https://www.anquanke.com//post/id/85406 


# 【木马分析】“spora”敲诈者木马分析


                                阅读量   
                                **102481**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t016fbb5375e437f30f.jpg)](https://p4.ssl.qhimg.com/t016fbb5375e437f30f.jpg)

**0x1 ****前言**



“spora”敲诈者是今年年初发现的一款新型的敲诈者木马。该类型的敲诈者木马在密钥的处理以及与受害者的交互上有重大的突破。众所周知，过去的敲诈者木马在密钥的获取上一般有两种方式，一是将密钥硬编码在文件中，这种方案的缺点在于同一批放出的敲诈者木马使用相同的RSA公钥，当有一个私钥泄露之后，同一批敲诈者木马的受害计算机也就可以得救；另一种方式是从服务端获取密钥以达到一机一密钥的目的，不过倘若无法成功从服务端获取密钥将加密失败。“spora”敲诈者在密钥获取上进行了改进，利用相关的API生成一组RSA密钥组和一个AES-256密钥，然后使用该AES-256密钥加密RSA密钥组的私钥，最后用硬编码在文件中的RSA公钥加密AES-256密钥。而对于文件的加密，程序会为每个待加密的文件生成一个AES-256密钥，并用该密钥加密文件，最后再使用之前产生的RSA密钥组的公钥加密每个文件独有的AES-256密钥并写入文件中。具体如下图所示。

[![](https://p0.ssl.qhimg.com/t01a2ac3ccd1e1b516d.png)](https://p0.ssl.qhimg.com/t01a2ac3ccd1e1b516d.png)

图1 加密示意图

 

**0x2 ****样本具体分析**



相比较其他敲诈者木马繁琐的运行流程，“spora”敲诈者木马的运行流程相对简洁。首先提取数据段中的数据解密后保存到栈中，作为第一段shellcode。

[![](https://p3.ssl.qhimg.com/t01ead4e350d5ea9ed7.png)](https://p3.ssl.qhimg.com/t01ead4e350d5ea9ed7.png)

图2 解密第一段shellcode

在第一段shellcode中将申请一段内存用于存放第二段shellicode并执行。

[![](https://p1.ssl.qhimg.com/t017b788bd5c345da41.png)](https://p1.ssl.qhimg.com/t017b788bd5c345da41.png)

图3 申请空间并写入shellcode

在第二段shellcode中程序以挂起方式运行一个自身的新实例，并且以进程替换的方式将第三段shellcode注入到新实例中，这次写入的shellcode将执行程序最主要的功能—加密。

[![](https://p3.ssl.qhimg.com/t01ff5cea4537e3a0df.png)](https://p3.ssl.qhimg.com/t01ff5cea4537e3a0df.png)

图4 解除映射以执行进程替换

在傀儡进程中，程序会先判断系统版本。

[![](https://p0.ssl.qhimg.com/t014c7a7b0183d698ed.png)](https://p0.ssl.qhimg.com/t014c7a7b0183d698ed.png)

图5 判断系统版本

完成系统版本的判断后，程序会使用硬编码在程序文件中的AES密钥解密硬编码在程序文件中的加密的RSA公钥以及勒索页面HTML文档。方便起见，后面将称解密得到的RSA密钥为硬编码的RSA密钥。

[![](https://p0.ssl.qhimg.com/t01c76c863bb773ee8d.png)](https://p0.ssl.qhimg.com/t01c76c863bb773ee8d.png)

图6 解密得硬编码的RSA密钥和勒索页面HTML文档

之后程序读取相应的标记文件，该标记文件用于记录加密文件的一些信息。在初次感染该敲诈者时该标记文件是不存在的，程序会自动创建标记文件，并读取文件，由于此时标记文件中并无内容，读取操作会返回-1，程序也就据此确定该计算机是首次感染“spora”敲诈者，并执行加密操作。

[![](https://p3.ssl.qhimg.com/t01bb6c37c4422f348a.png)](https://p3.ssl.qhimg.com/t01bb6c37c4422f348a.png)

图7 读取标记文件内容

之后程序将遍历系统的所有文件以及网络资源中的文件，并选择加密的目标。待加密文件的路径将避开"windows"，"program files"，"program files (x86)"，"games" 四个路径，加密文件的类型包括xls，doc，xlsx，docx，rtf，odt，pdf，psd，dwg，cdr，cd，mdb，1cd，dbf，sqlite，accdb，jpg，jpeg，tiff，zip，rar，7z，backup。加密后将不会修改文件后缀。

[![](https://p0.ssl.qhimg.com/t01bfab8122c088baea.png)](https://p0.ssl.qhimg.com/t01bfab8122c088baea.png)

  图8 不加密的文件路径

[![](https://p4.ssl.qhimg.com/t01d13aa78678aa88f1.png)](https://p4.ssl.qhimg.com/t01d13aa78678aa88f1.png)

图9 选取待加密文件过程

遍历所有文件并获取待加密文件路径之后会将文件路径信息以统一的密码加密后保存到之前的标记文件中。这也方便之后获取赎金后对文件进行解密。

[![](https://p1.ssl.qhimg.com/t017d0cc689a260ea5c.png)](https://p1.ssl.qhimg.com/t017d0cc689a260ea5c.png)

 图10 将文件路径信息写入标记文件中

之后就开始进行加密操作，首先是生成一个RSA密钥组，并将系统信息附到RSA私钥之后。附加的系统信息包括本地时间，位置信息以及用户名。

[![](https://p1.ssl.qhimg.com/t0110858802571e661b.png)](https://p1.ssl.qhimg.com/t0110858802571e661b.png)

图11 产生RSA密钥组

[![](https://p5.ssl.qhimg.com/t012e813f4213f5408f.png)](https://p5.ssl.qhimg.com/t012e813f4213f5408f.png)

图12 RSA私钥后附加系统信息

[![](https://p5.ssl.qhimg.com/t012071ab9239679bfd.png)](https://p5.ssl.qhimg.com/t012071ab9239679bfd.png)

图13附加信息的RSA私钥

之后程序会对附加信息的RSA私钥求哈希，得到的哈希值将作为本机的标识符，用于之后支付赎金的操作。

[![](https://p0.ssl.qhimg.com/t012c91c2a9998740e0.png)](https://p0.ssl.qhimg.com/t012c91c2a9998740e0.png)

图14 对附加信息的RSA私钥求哈希作为本机标识符

[![](https://p5.ssl.qhimg.com/t013522f707a2003752.png)](https://p5.ssl.qhimg.com/t013522f707a2003752.png)

图15 生成的本机标识符

然后程序生成一个AES-256密钥，并用它加密之前产生的RSA密钥组的私钥，然后再使用硬编码在程序中的RSA公钥加密AES密钥，然后将加密后的AES密钥以及RSA私钥存放到KEY文件中。

[![](https://p2.ssl.qhimg.com/t01037be0b4f7359b93.png)](https://p2.ssl.qhimg.com/t01037be0b4f7359b93.png)

图16 密钥的处理

最后就是对待加密文件的加密。对于文件的加密，最大的加密大小为5M。程序会为每个文件配置一个生成的AES-256密钥，并用它加密文件，最后使用之前生成的RSA密钥组的公钥加密该AES密钥，并将加密后的密钥也写入文件中。

[![](https://p3.ssl.qhimg.com/t013ef2ef374e0def96.png)](https://p3.ssl.qhimg.com/t013ef2ef374e0def96.png)

图17 文件的加密

在完成加密工作之后，程序不忘删除卷影，然后将C盘下的重要文件夹隐藏，并生成伪装成相应的快捷方式指向本程序。除外程序还会生成VBS脚本并将脚本复制到启动文件夹下，此处不再赘述。

之后程序将弹出勒索页面，该勒索页面非常“人性化”，受害者只要点击相应按钮就可以跳转到相应的支付页面进行支付，支付方式也是多种多样，包括恢复大小小于25M的文件，恢复所有文件并且移除“spora”敲诈者相关程序等等，每种服务对应的价格也不同。除此之外还可以在线和木马传播者交流，这也是之前从未见过的。由此可以看出，“spora”敲诈者已经进入了勒索即服务的阶段。

[![](https://p3.ssl.qhimg.com/t0182ba31cec6176ef1.png)](https://p3.ssl.qhimg.com/t0182ba31cec6176ef1.png)

图18 勒索展示页面

[![](https://p3.ssl.qhimg.com/t016c02022d76e6ee49.png)](https://p3.ssl.qhimg.com/t016c02022d76e6ee49.png)

图19 支付页面，右下角可见聊天框

 

**0x3 ****总结**



“spora”敲诈者不仅改进了密钥的获取以及传递方式，还开启了勒索软件即服务的先河，不慎感染该敲诈者木马的用户只能通过在“便捷的支付页面”缴纳赎金来恢复文件。从“spora”敲诈者的爆发可以看出，敲诈者木马已经成为一个颇具规模的产业，其作用范围也不仅仅局限于文件的加密，将包含更多的衍生“服务”，而这些“服务”所带来的暴利，将极大的增加敲诈者木马的数量以及类型。<br>

对于普通网民来说，可以从下面几个方面预防这类病毒：

1.  对重要数据及时做备份，将备份存在多个位置，预防数据损坏丢失。

2.  打好系统和软件补丁，预防各类挂马和漏洞攻击。

3.  养成良好的上网习惯，不轻易打开陌生人发来的邮件附件。

4.  最重要的，用户应该选择一款可靠的安全软件，保护计算机不受各类木马病毒侵害。



**360安全卫士还独家提供了“反勒索服务”，并向用户承诺：使用360安全卫士并开启该服务后，如仍然感染敲诈者病毒，360将提供最高3个比特币的赎金帮助用户恢复数据，真正彻底保障用户的数据安全。**



****

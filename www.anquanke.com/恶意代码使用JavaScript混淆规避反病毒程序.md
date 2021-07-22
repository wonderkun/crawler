> 原文链接: https://www.anquanke.com//post/id/172984 


# 恶意代码使用JavaScript混淆规避反病毒程序


                                阅读量   
                                **175494**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者yoroi，文章来源：blog.yoroi.company
                                <br>原文地址：[https://blog.yoroi.company/research/evading-av-with-javascript-obfuscation/](https://blog.yoroi.company/research/evading-av-with-javascript-obfuscation/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01462d7894f1fad19d.png)](https://p1.ssl.qhimg.com/t01462d7894f1fad19d.png)



## 摘要

该文讲述了攻击者如何使用JS混淆的方法来使一个知名远控RevengeRAT的变种躲避杀毒软件检测的。



## 1. 介绍

几天前，Cybaze-Yoroi ZLAB研究团队发现了一个可疑的JavaScript文件，并决定进一步关注这个可疑文件。该JavaScript文件利用了好几种技术去躲避所有反病毒程序的检测，VT上58个反病毒引擎没有一个将此文件检测出来（注：此结果为20190301的检测结果，截止到20190311，已经有5家可以检测出来了，译者在VT上搜索时显示是57家引擎）。因此，我们决定剖析并调查一下这个恶意软件到底使用了哪种技术实现了这种结果。

[![](https://p3.ssl.qhimg.com/t01c28ac230e14feb31.png)](https://p3.ssl.qhimg.com/t01c28ac230e14feb31.png)

**图1:20190311VT检测结果**



## 2. 技术分析

这个文件是使用JavaScript语言编写的，可以使用Windows Script Host系统组件在本地运行该文件，该文件的大小比普通的脚本文件大了很多，大约有1M的随机文字。

**表1：JS文件信息**

|Hash（Sha256）|99b0b24dcfb29291163b66c60355b6e1454c6a3d5dfbc2cd7b86b1ca548761eb
|------
|Thread|Generic
|Description|JS/Dropper
|Ssdeep|6144:+FquQGm+pYEaRFquQGnFquQGHFquQGtFquQG1FquQGrFquQGoFquQGsFquQGRFqa:+y+yTr5RPkYFV21Ge3bN2u8AVQuK6qzH

首先来看一下这个文件显示的第一个有趣的特征：脚本的主体使用了非ASCII字符集。

[![](https://p1.ssl.qhimg.com/t0177b53a6e7831a2e6.png)](https://p1.ssl.qhimg.com/t0177b53a6e7831a2e6.png)

**图2：javascript文件结构**

这些字符看起来没有任何明显的逻辑，但是，仔细观察就会发现恶意软件作者使用的第一种技巧。他使用长字符串声明所有变量，这些长字符串混合了ASCII和UNICODE字符，甚至包括西里尔字母表中的一些字符。

`ыNиpsфбm3nxsцвиеKEсыBLQBеnьVWC`

所有变量明显可见的差异就只有变量在”_“之后的那一部分了。因此，我们可以知道恶意软件作者给所有变量的声明使用了一个共同的前缀。从图2可以看出来，变量的最后一部分都是使用下面的方式来声明的。

`var = […]_0x5e24 var =[...]_0x59ad等`

所以，解混淆的第一步就是使用一个易读的字符替换这些前缀。替换之后结果如下：

[![](https://p1.ssl.qhimg.com/t01455f3c691c51b8c1.png)](https://p1.ssl.qhimg.com/t01455f3c691c51b8c1.png)

**图3：第一层解混淆**

在分析中发现的其他的混淆技巧就是上面脚本中ascii和16进制字符的混合。使用的16进制字符如下所示

`0x27 0x20 0x5c`

解混淆的第二部就是使用这些16进制字符代表的符号替换他们(文件中是x20 x27 x5c，因此替换的是这三个)。

`0x27---&gt;'  0x20---&gt;空格  0x5c---&gt;`

替换之后，结果如下

[![](https://p0.ssl.qhimg.com/t0101e0b6ebb28148c6.png)](https://p0.ssl.qhimg.com/t0101e0b6ebb28148c6.png)

**图4：第二层解混淆**

每个16进制字符之前的反斜线是必要的，JS文件用它来将十六进制字符和ASCII码结合起来。现在我们能够看到清楚的代码和隐藏在javascript dropper中的最初的可执行部分。JS文件中包含的PE文件是以16进制的形式存在的，从图4中可以看到，这些16进制字符中存在‘$’，这是不被允许的。

[![](https://p3.ssl.qhimg.com/t0163b095013f709320.png)](https://p3.ssl.qhimg.com/t0163b095013f709320.png)

**图5：可执行文件的第一部分**

上图中代码的第一行的意思是使用‘5’去替换PE文件中的‘$’。（PE文件头前面是4D5A，代码中是4D$A）,执行完替换操作后，就可以得到一个PE文件了，该PE文件就是释放在受害机器上的最终payload。（读者若是想要复制字符串将其直接存储为PE文件，可以使用sublime 正则表达式匹配来替换PE文件中的$，这样就不会把PE文件前面的JS语句中的$也替换掉了）

[![](https://p2.ssl.qhimg.com/t01947a1d37d8d5e234.png)](https://p2.ssl.qhimg.com/t01947a1d37d8d5e234.png)

**图6：使用5替换PE文件中的$**

可执行文件的前4个字符是‘4D5A’，4D5A是PE文件的标志字，“MZ”。一旦所有的解混淆完成后，为了实现持久化，JS会将payload写入如下注册表键，将其设置为开机自启动。

```
HKCUSOFTWAREMicrosoftRunMicrosoft
```

JS文件中提取的Payload可以被VT上大部分反病毒引擎检测出来。

[![](https://p3.ssl.qhimg.com/t012e441abb58d0e0bc.png)](https://p3.ssl.qhimg.com/t012e441abb58d0e0bc.png)

**图7:2019年2月28日JS中payload的检测结果**

该payload是知名远控木马RevengeRAT的变种，与如下C2服务器通信。

```
networklan[.]asuscomm[.]com
```



## 总结

这个恶意JS脚本的分析向我们展示了攻击者是如何轻松的隐藏恶意代码骗过反病毒引擎检测的。即使是知名的恶意代码家族（如RevengeRAT），攻击者也可以隐藏他们使他们躲过反病毒引擎。由此可见，将恶意代码混淆后隐藏在JS代码中，运行JS代码后释放出恶意代码，这种操作是可以获得0检测率的。

当然，这个例子还有其他的方面值得去深究。在2019年2月28日（该JS文件被发现的几天之后）上传检测该文件，只有2个反病毒引擎检测出来了，这证明了现代化威胁是不可能被单一、自动化工具捕捉到的。（图1为最新的检测结果）

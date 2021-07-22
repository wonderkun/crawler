> 原文链接: https://www.anquanke.com//post/id/86803 


# 【技术分享】U盘拷贝修改MBR勒索木马分析


                                阅读量   
                                **111472**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01b8cbb5bcff473575.jpg)](https://p0.ssl.qhimg.com/t01b8cbb5bcff473575.jpg)

**<br>**

<a></a>**一、概述**

该木马伪装成正常的软件，只有在用户退出软件的时候才会调用恶意代码，将恶意引导代码和原始的**MBR**以及加密后的硬盘分区表**DPT**重新写入硬盘。木马文件并没有加密电脑中的其他数据文档，在系统重启的时候提示勒索信息，并且要求输入密码，密码无效则无法进入系统。具体流程如图所示

[![](https://p4.ssl.qhimg.com/t014f70e0fa2e412e9b.png)](https://p4.ssl.qhimg.com/t014f70e0fa2e412e9b.png)

图1-1 勒索木马运行流程图



**二、样本来源**

样本来自某下载网站，从更新时间来看，是最近发布的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0118c8720742cdee6c.png)

图2-1 勒索木马软件下载站



**三、木马分析**

主程序运行之后没有界面，需要热键激活，激活之后界面如下：

[![](https://p4.ssl.qhimg.com/t01d8887b577bdc95f3.png)](https://p4.ssl.qhimg.com/t01d8887b577bdc95f3.png)

图3-1木马主程序运行界面

该程序的主要恶意行为在用户点击退出按钮的时候激活。通过调用**CreateFileA**打开主硬盘，调用**ReadFile**读入第0扇区原始数据。

[![](https://p0.ssl.qhimg.com/t01ce915e5b6e3c707e.png)](https://p0.ssl.qhimg.com/t01ce915e5b6e3c707e.png)

图3-2 木马读入MBR代码

[![](https://p2.ssl.qhimg.com/t01d3fe25d5907ed687.png)](https://p2.ssl.qhimg.com/t01d3fe25d5907ed687.png)

图3-3读入MBR原始数据

接着程序会在内存中通过**XMM**寄存器，对读入MBR的硬盘分区表进行异或（0x54）加密，具体如下：

[![](https://p4.ssl.qhimg.com/t012c166b87a20bce29.png)](https://p4.ssl.qhimg.com/t012c166b87a20bce29.png)

图3-4 硬盘分区表加密前

[![](https://p0.ssl.qhimg.com/t01a1fd2885ede7a51a.png)](https://p0.ssl.qhimg.com/t01a1fd2885ede7a51a.png)

图3-5硬盘分区表加密后

接着程序会调用CreateFileA打开主硬盘，调用WriteFile将恶意代码和加密过的硬盘分区表写到0扇区和2扇区，可以看到增加了勒索提示信息。

[![](https://p5.ssl.qhimg.com/t01992238142b3a01fa.png)](https://p5.ssl.qhimg.com/t01992238142b3a01fa.png)

图3-6写入MBR的恶意代码。

重启系统后显示了勒索提示，提示的QQ号实际并不存在，无法联系到勒索作者。

[![](https://p0.ssl.qhimg.com/t0190c50fb223190746.png)](https://p0.ssl.qhimg.com/t0190c50fb223190746.png)

图3-7重启系统开机进入勒索提示

通过动态分析勒索木马修改的MBR，可以找到木马密码的验证逻辑如下：

[![](https://p3.ssl.qhimg.com/t01b23ae652e289042b.png)](https://p3.ssl.qhimg.com/t01b23ae652e289042b.png)

图3-8开机输入密码以回车键结束

[![](https://p5.ssl.qhimg.com/t01835c610794b27e83.png)](https://p5.ssl.qhimg.com/t01835c610794b27e83.png)

图3-9判断开始数据是否WWe

[![](https://p5.ssl.qhimg.com/t014008f0f7633dd38c.png)](https://p5.ssl.qhimg.com/t014008f0f7633dd38c.png)

图3-10 将输入的数据作为分区表的解密秘钥

输入数据的前三个字母是“**WWe**”，解密的密钥是“T”，我们在XP系统中输入一组密码“WWeTTTTTTTTT”后成功进入了系统。需要说明的是秘钥“T”的个数根据不同的环境数量可能不同。



**四、杀毒的查杀**

360杀毒已第一时间查杀该木马，对于勒索木马“防”重于“治”，请广大用户不要轻易信任未知来源的软件。

[![](https://p1.ssl.qhimg.com/t016ea084681a6ce621.png)](https://p1.ssl.qhimg.com/t016ea084681a6ce621.png)

图4-1   360查杀国产新型勒索木马

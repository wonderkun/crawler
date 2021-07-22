> 原文链接: https://www.anquanke.com//post/id/182773 


# 虚假Office 365网站传播TrickBot银行木马


                                阅读量   
                                **156584**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01dacd2ac5725b6fc3.png)](https://p4.ssl.qhimg.com/t01dacd2ac5725b6fc3.png)



TrickBot银行木马是一款专门针对各国银行进行攻击的恶意样本，它之前被用于攻击全球多个国家的金融机构，主要通过钓鱼邮件的方式进行传播，前不久还发现有黑产团伙利用它来传播Ryuk勒索病毒，最近MalwareHunterTeam的安全专家发现一个虚拟的Office 365网站，被用于传播TrickBot银行木马，相关的信息，如下所示：

[![](https://p1.ssl.qhimg.com/t013ddeba375da7e731.png)](https://p1.ssl.qhimg.com/t013ddeba375da7e731.png)

黑产团伙创建了一个虚假的Office 365网站，URL地址：[https://get-office365.live](https://get-office365.live), 打开这个网站，如下所示：

[![](https://p4.ssl.qhimg.com/t01b508ebabd7f1e202.png)](https://p4.ssl.qhimg.com/t01b508ebabd7f1e202.png)

然后通过这个网站给受害者分发伪装成Chrome和Firefox浏览器更新的TrickBot银行木马程序，如下所示：

[![](https://p2.ssl.qhimg.com/t014be934f265d11313.png)](https://p2.ssl.qhimg.com/t014be934f265d11313.png)

受害者下载的更新程序其实就是TrickBot银行木马，查看app.any.run网站的链接如下所示：

[![](https://p1.ssl.qhimg.com/t01e22da09f82f72bfd.png)](https://p1.ssl.qhimg.com/t01e22da09f82f72bfd.png)

TrickBot银行木马核心功能剖析

1.银行木马在%appdata%mslibrary目录下生成银行木马模块核心组件模块，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015c28735a64a00b59.png)

2.然后将它自身注册表服务，实现自启动，如下所示：

[![](https://p5.ssl.qhimg.com/t011336461aac238cfa.png)](https://p5.ssl.qhimg.com/t011336461aac238cfa.png)

3.同时调用PowerShell脚本关闭Windows Defender软件，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017c5f70704035793e.png)

使用的PowerShell脚本命令，如下所示：

[![](https://p0.ssl.qhimg.com/t014df84d70cef3d7e3.png)](https://p0.ssl.qhimg.com/t014df84d70cef3d7e3.png)

关闭Windows安全保护功能的开源代码，github地址：

[https://github.com/NYAN-x-CAT/Disable-Windows-Defender](https://github.com/NYAN-x-CAT/Disable-Windows-Defender)

有兴趣的可以研究一下

4.跟之前TrickBot银行木马一样，启动svchost进程，然后将相应的模块注入到svchost进程,如下所示：

[![](https://p4.ssl.qhimg.com/t011e453a3674172c3d.png)](https://p4.ssl.qhimg.com/t011e453a3674172c3d.png)

5.TrickBot银行木马下载的模块如下所示：

[![](https://p0.ssl.qhimg.com/t01b87571bee1177eba.png)](https://p0.ssl.qhimg.com/t01b87571bee1177eba.png)

各个模块的功能：

importDll32：窃取浏览器表单数据、cookie、历史记录等信息

injectDll32：注入浏览器进程，窃取银行网站登录凭据

mailsearcher32：收集邮箱信息

networkDll32：收集主机系统和网络/域拓扑信息

psfin32：对攻击目标进行信息收集，判断攻击目的

pwgrab32：窃取Chrome/IE密码信息

shareDll32：下载TrickBot，通过共享传播

systeminfo32：收集主机基本信息

tabDll32：利用IPC$共享和SMB漏洞，结合shareDll32和wormDll32进行传播感染

wormDll32：下载TrickBot进行横向传播

6.TrickBot银行木马为了免杀，从远程服务器上下载回来的模块都是加密后的数据，再将这些数据解密，然后注入到svchost进程中，通过本地解密脚本，解密出来的模块，如下所示：

[![](https://p1.ssl.qhimg.com/t01ff2ed04ea3a763e0.png)](https://p1.ssl.qhimg.com/t01ff2ed04ea3a763e0.png)

7.再通过解密脚本，解密出相应的配置文件，dinj文件内容如下所示：

[![](https://p4.ssl.qhimg.com/t01d45f1b2d6d89e155.png)](https://p4.ssl.qhimg.com/t01d45f1b2d6d89e155.png)

里面包含了全球各大网上银行网站，这个模块注入的svchost进程中，当受害者访问这些网站的时候，盗取网站登录凭证等，从内存中可以看到这些银行网址等信息，如下所示：

[![](https://p4.ssl.qhimg.com/t01da3a7319ce7aaed5.png)](https://p4.ssl.qhimg.com/t01da3a7319ce7aaed5.png)

8.解密出来的dpost文件内容，如下所示：

[![](https://p3.ssl.qhimg.com/t0104e98080c635a4e4.png)](https://p3.ssl.qhimg.com/t0104e98080c635a4e4.png)

9.解密出来的mailconf文件内容，如下所示：

[![](https://p0.ssl.qhimg.com/t01f16ec1633104a967.png)](https://p0.ssl.qhimg.com/t01f16ec1633104a967.png)

在分析某个模块的时候，发现模块的编译时间为2019年6月14日，如下所示：

[![](https://p2.ssl.qhimg.com/t01f3c839e0abb5cae0.png)](https://p2.ssl.qhimg.com/t01f3c839e0abb5cae0.png)

TrickBot银行木马是一款非常复杂的银行木马，里面涉及到的模块非常之多，每个模块对应不同的功能，笔者曾写过多篇关于银行木马的分析报告，包括：TrickBot、Ursnif、Emotet、Redaman、Dridex等家族，有兴趣可以去查阅，银行木马一直是分析人员研究的重点，每个银行木马家族都是一种复杂的恶意样本，需要花费分析人员大量的时间，有时候可能需要一周，几周或更长的时间进行样本的详细分析，有一些黑产团伙专门从事银行木马的开发运营活动，已经获得了巨大的利润，一款银行木马如果被运营的好少则可以带来上亿美元的收入，多的可以十几亿美元的收入，同时还有一些银行木马最近几年充当其他恶意软件的下载器，用于传播其它恶意软件，就像之前Ryuk勒索病毒就曾发现利用TrickBot银行木马进行传播，事实上高端复杂的攻击样本，都是需要花费分析人员大量的时间进行深入研究的

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/d4TJ7uPEE6ByMcEarzEh5w)

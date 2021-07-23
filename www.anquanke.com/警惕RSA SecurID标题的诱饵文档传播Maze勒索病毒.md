> 原文链接: https://www.anquanke.com//post/id/193032 


# 警惕RSA SecurID标题的诱饵文档传播Maze勒索病毒


                                阅读量   
                                **985907**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01f56721e5713cb472.png)](https://p3.ssl.qhimg.com/t01f56721e5713cb472.png)



Maze勒索病毒，又称Chacha勒索病毒，是今年5月份由Malwarebytes安全研究员首次发现，此勒索病毒主要使用各种漏洞利用工具包Fallout、Spelevo，伪装成合法加密货币交换应用程序的假冒站点或挂马网站等方式进行分发传播，近日笔者监控到一例通过标题为RSA SecurID的诱饵文档传播此勒索病毒的最新样本

捕获到的诱饵文档是一个以RSA SecurID为标题的文档，内容如下所示：

[![](https://p4.ssl.qhimg.com/t018636a9dac5c75015.png)](https://p4.ssl.qhimg.com/t018636a9dac5c75015.png)

文档里面包含恶意宏代码，诱导受害者双击启动宏代码，恶意宏代码，如下所示：

[![](https://p5.ssl.qhimg.com/t01180d48ddba2b6f7a.png)](https://p5.ssl.qhimg.com/t01180d48ddba2b6f7a.png)

动态调试恶意宏代码，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d7f3c794fc244353.png)

读取窗体中的数据，然后进行解析，窗体的数据，如下所示：

[![](https://p2.ssl.qhimg.com/t019589aaa78dabeff9.png)](https://p2.ssl.qhimg.com/t019589aaa78dabeff9.png)

宏代码解密窗体中的数据，然后从远程服务器hxxp://149.56.245.196/wordupd.tmp 下载恶意程序到C:WindowsTempered.tmp,然后执行恶意程序，如下所示：

[![](https://p1.ssl.qhimg.com/t0166db037b4bbcad20.png)](https://p1.ssl.qhimg.com/t0166db037b4bbcad20.png)

下载的ered.tmp就是Maze勒索病毒，外壳程序如下所示：

[![](https://p0.ssl.qhimg.com/t017c79fb34c7d9c245.png)](https://p0.ssl.qhimg.com/t017c79fb34c7d9c245.png)

分配相应的内存空间，然后解密出勒索病毒的核心代码，如下所示：

[![](https://p2.ssl.qhimg.com/t01f1c09182b22b8ba7.png)](https://p2.ssl.qhimg.com/t01f1c09182b22b8ba7.png)

再跳转执行勒索病毒核心代码，如下所示：

[![](https://p2.ssl.qhimg.com/t0103fae9eb47942ecc.png)](https://p2.ssl.qhimg.com/t0103fae9eb47942ecc.png)

此勒索病毒加密后的文件后缀名为随机文件名，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0189ae8dfd562e3f0b.png)

勒索提示信息文件DECRYPT-FILES.txt，内容如下所示：

[![](https://p5.ssl.qhimg.com/t01262b4f0e96485ff7.png)](https://p5.ssl.qhimg.com/t01262b4f0e96485ff7.png)

加密文件之后会修改桌面背景图片，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0169e9eeff338113ab.png)

该勒索病毒解密网站，如下所示：

[![](https://p2.ssl.qhimg.com/t01cec14833e25a643a.png)](https://p2.ssl.qhimg.com/t01cec14833e25a643a.png)

上传勒索提示信息文件之后，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0157f0330cee0adaef.png)

勒索赎金为:0.13967635 BTC，相当于1200美元，过期翻倍，我去！现在搞勒索都这么黑的，上次还是400美元，这次直接1200美元了，黑客的BTC钱包地址：<br>
334yPgzDkqD7vvh2GKMrFSQneWVp2onvUq

文档内容上显示的时间为2019年11月12日，估计是12号制作的诱饵文档,最近一段时间一些流行的勒索病毒家族主要使用漏洞和垃圾邮件两种方式进行传播感染，各企业一定要做好相应的防范措施，大部分流行的勒索病毒暂无公开的解密工具，此勒索病毒之前主要使用漏洞利用工具包，通过假虚网站或垃圾网站挂马的方式进行传播，此次又增加了垃圾邮件文档的方式进行传播，可见勒索病毒黑客团伙不断在更新增加自己的攻击传播方式，以获取最大的利益，未来会不会也会利用无文件的方式传播此勒索病毒呢？

IOC<br>
MD5<br>
a2d631fcb08a6c840c23a8f46f6892dd<br>
a0c5b4adbcd9eb6de9d32537b16c423b

C&amp;C<br>
149.56.245.196<br>
91.218.114.4<br>
91.218.114.25<br>
91.218.114.11<br>
91.218.114.26<br>
91.218.114.31

URL<br>
hxxp://149.56.245.196/wordupd.tmp<br>
hxxp://91.218.114.4/messages/content/appvsgp.html?kakp=2mj&amp;rkjn=koimf<br>
hxxp://91.218.114.11/forum/hhiwoqn.action<br>
hxxp://91.218.114.4/messages/jwt.asp?rgct=dp&amp;gf=m1h&amp;igtu=617lg1ps42&amp;q=0q7r0l6v<br>
hxxp://91.218.114.25/view/check/fvksl.html?dab=a6tud3<br>
hxxp://91.218.114.26/archive/pj.jspx?wi=h1265&amp;hi=e<br>
hxxp://91.218.114.31/support/mkhbm.action?vshw=m627m<br>
hxxp://91.218.114.11/ticket/nsa.jsp?efd=g0xay3bx&amp;mtu=1<br>
hxxp://91.218.114.25/pipkl.cgi?ampf=8613eu&amp;cnp=wc6502gj16&amp;q=5m&amp;ycme=35s4b<br>
hxxp://91.218.114.31/check/s.phtml?uxkv=wjebu46&amp;wmbk=12vc05ja7m<br>
hxxp://91.218.114.26/support/uuxyhvhu.do?ic=wjpr4uy&amp;lpap=2&amp;edem=62i22cgi41&amp;p=dj6

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/E1bqAS8bb6apctul0CvZ0Q)

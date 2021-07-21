> 原文链接: https://www.anquanke.com//post/id/83870 


# 介绍sqlmap中的SQL注入filter逃逸


                                阅读量   
                                **83493**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.gracefulsecurity.com/sql-injection-filter-evasion/](https://www.gracefulsecurity.com/sql-injection-filter-evasion/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0195ef5a12826bb0f3.png)](https://p5.ssl.qhimg.com/t0195ef5a12826bb0f3.png)

每当我发现一个SQL注入漏洞时,我都会在注入点使用sqlmap。这是一个操作简单易于使用的工具,不仅能证实漏洞,而且还可以提取相关数据、获得执行命令,以及执行进一步的实验操作。如果碰到filter或是网络应用防火墙,我会习惯性地打破Burp Suite并且开始手动规避筛选,但是接下来介绍的这种方法更为简便。

规避用户内置filter而试图利用SQL注入的做法往往是试着用不同的字符设置相同载荷。以下面的有效载荷为例:

[![](https://p1.ssl.qhimg.com/t013407d14ae9963f32.png)](https://p1.ssl.qhimg.com/t013407d14ae9963f32.png)

根据被筛选的荷载多少,我可以使用多种方法重写这部分荷载。例如下面这个更大的荷载,我会使用一个已编码的字符来取代它。

[![](https://p2.ssl.qhimg.com/t01bdd4c8f5095c1f8f.png)](https://p2.ssl.qhimg.com/t01bdd4c8f5095c1f8f.png)

另外,我还可以简单地重新设置荷载格式,这样也可以达到同样的效果:

[![](https://p4.ssl.qhimg.com/t01d4d4b357278d02a1.png)](https://p4.ssl.qhimg.com/t01d4d4b357278d02a1.png)

这些简单的重新设置都可以利用一种工具完成自动操作,那就是我们熟知并且乐于使用的sqlmap。如果你不熟悉这个工具,可以先通过sqlmap介绍简单了解一下。当你熟悉了它的界面之后,你会惊喜的发现,这种工具拥有“脚本更改”功能,该功能可以自动更改荷载然后直接发送给服务器,这样就可以规避开筛选。你可以通过当前的更改脚本列表快速查看当前可行的规避方法。每个脚本中都包含了一个简介和示例。通过下列的sqlmap指令实现的是利用URI编码的规避途径:

[![](https://p4.ssl.qhimg.com/t013eaf6fb8c3b2bc22.png)](https://p4.ssl.qhimg.com/t013eaf6fb8c3b2bc22.png)

你还可以在同一行中键入不止一种筛选脚本,就像这样:

[![](https://p1.ssl.qhimg.com/t01401786370c1eddbe.png)](https://p1.ssl.qhimg.com/t01401786370c1eddbe.png)

想要在运行中的应用程序中进行这种类型规避的话,可以查看GracefulSecurity’sVulnVM。只要使用正确的更改脚本你就能够在应用程序中发现两个隐藏着的第二级别的SQL注入漏洞。

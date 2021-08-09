> 原文链接: https://www.anquanke.com//post/id/248898 


# 论0day抓取的姿势


                                阅读量   
                                **38275**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01784309b24b730d69.jpg)](https://p2.ssl.qhimg.com/t01784309b24b730d69.jpg)



**整个过程仅讲思路的实现，因笔者日常工作并不相关，从构思到实现，前前后后大概花了两个月时间，未对数据进行整理，也未列出具体的步骤，仅供研究与参考，思路如有雷同，那真是太好了**

## 0x01 概念

根据维基百科的解释，在电脑领域中，**零日漏洞**或**零时差漏洞**（英语：zero-day vulnerability、0-day vulnerability）通常是指还没有补丁的安全漏洞，而**零日攻击**或**零时差攻击**（英语：zero-day exploit、zero-day attack）则是指利用这种漏洞进行的攻击。提供该漏洞细节或者利用程序的人通常是该漏洞的发现者。零日漏洞的利用程序对网络安全具有巨大威胁，因此零日漏洞不但是黑客的最爱，掌握多少零日漏洞也成为评价黑客技术水平的一个重要参数。



## 0x02 构思

目前大多数漏洞都是以Web为主，那么在HTTP中都是流量都是可见的，那么可以进行流量的入侵检测，入侵检测主要分为两个途径，第一个是网络告警，就是在内外网通信中查找攻击者入侵迹象，第二个是系统告警，就是在系统上查找攻击者存在的迹象，我们从网络层面和系统层面实现捕获0day。

一般攻击路径都是通过互联网进行，那么我们利用属于DMZ区的一台服务器上搭建一个docker漏洞环境，然后通过falco进行CONTAINER内执行命令的监控，在互联网侧通过packetbeat进行HTTP的payload的的捕获。

[![](https://p4.ssl.qhimg.com/t01a596ef6d80df0e63.png)](https://p4.ssl.qhimg.com/t01a596ef6d80df0e63.png)

俗话说，工遇善其事，必先利其器，需要打造自己的捕获利器。



## 0x03 打造属于自己的开源捕获利器

找大佬要了个EXP集合工具，致远的老版本漏洞，运行一下，从流量中可以看到各个payload，那么应该可以将这些HTTP流量中的payload进行捕获，化为己用。

[![](https://p5.ssl.qhimg.com/t0121a495574e7dd327.png)](https://p5.ssl.qhimg.com/t0121a495574e7dd327.png)

先尝试通过packetbeat进行HTTP的payload的捕获，先看能不能捕获到，从流量中是可以看到能够捕获到payload的，那么这个构思初步是可行的。

[![](https://p5.ssl.qhimg.com/t010311801776f7aef6.png)](https://p5.ssl.qhimg.com/t010311801776f7aef6.png)



## 0x04 实战演练

光说不练假把式，通过[vulhub](https://github.com/vulhub/vulhub)进行环境搭建，以tomcat弱口令来进行复现，一直到拿到webshell来看整个过程是否能够捕捉到

搭建环境

[![](https://p0.ssl.qhimg.com/t01b8ab7b16c1cfbe12.png)](https://p0.ssl.qhimg.com/t01b8ab7b16c1cfbe12.png)

tomcat弱口令上传冰蝎木马，执行操作

[![](https://p0.ssl.qhimg.com/t01735acb4ce51e6e7e.png)](https://p0.ssl.qhimg.com/t01735acb4ce51e6e7e.png)

连接冰蝎，执行命令

[![](https://p0.ssl.qhimg.com/t01836e2becc4a96cd9.png)](https://p0.ssl.qhimg.com/t01836e2becc4a96cd9.png)

从流量中我们看到冰蝎的马执行的一些命令是加密的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0133338282c78d5512.png)

我们在es中也只能看到有流量

[![](https://p5.ssl.qhimg.com/t01b563e8a9fb414da1.png)](https://p5.ssl.qhimg.com/t01b563e8a9fb414da1.png)

能够看到一通操作猛如虎，但是HTTP中啥也看不到

[![](https://p1.ssl.qhimg.com/t01384b2a7d56654b5d.png)](https://p1.ssl.qhimg.com/t01384b2a7d56654b5d.png)

通过es语法筛选是能看到整个整个过程的，从过程中能够推断入侵手法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013f171b4850702b00.png)

通过监控容器内执行命令，可以看到能够监控到在冰蝎马里面执行的ls命令，一系列操作都能监控

[![](https://p2.ssl.qhimg.com/t01667c1d6d92d38935.png)](https://p2.ssl.qhimg.com/t01667c1d6d92d38935.png)

看着falco的标准输出有好多种，至于falco的日志可以进行标准化输出（原始输出实在是太难读了），es的也可以进行标准化的输出，找个地方存储起来就构成了自己的”威胁情报”了



## 0x05 小结

安全界大家都说”未知攻，焉知防”，通过从流量侧和系统侧实现攻击者的入侵手法，从威胁情报的角度应该说TTP更合适（手动狗头），其实整个过程更像是蜜罐思路的实现，蜜罐捕获0day应该算是一种常见的操作吧

以上

经过多次实验，对于weblogic等使用T3协议或其他非HTTP协议并不适用(主要因为packetbeat不支持)，只能从系统侧去想办法，感谢各位大佬的阅读与支持

如有疑问，欢迎交流，XzFpc3Rlbg==



## 0x06 参考资料

[https://blog.didiyun.com/index.php/2018/12/12/honeypot/](https://blog.didiyun.com/index.php/2018/12/12/honeypot/)

[https://www.ichunqiu.com/open/62359](https://www.ichunqiu.com/open/62359)

[https://github.com/vulhub/vulhub](https://github.com/vulhub/vulhub)

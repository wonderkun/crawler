> 原文链接: https://www.anquanke.com//post/id/179645 


# 渗透测试实战——born2root:2 + unknowndevice64: 2靶机入侵


                                阅读量   
                                **240679**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01095e48d492ec5c41.jpg)](https://p0.ssl.qhimg.com/t01095e48d492ec5c41.jpg)



## 前言

hello，大家好！最近还是一样工作忙到飞起，但是也挤出时间来更新靶机文章，本次文章，小弟就发4个靶机的writeup了，如果写的不好，烦请各位大佬斧正！



## 靶机安装/下载

born2root:2 下载地址：[https://pan.baidu.com/s/1DPaMqKZDSFA1tcVJCscLew](https://pan.baidu.com/s/1DPaMqKZDSFA1tcVJCscLew)

unknowndevice64: 2下载地址：[https://pan.baidu.com/s/117NQkFfcXdtjHX2WxPExsA](https://pan.baidu.com/s/117NQkFfcXdtjHX2WxPExsA)

[![](https://p4.ssl.qhimg.com/t012594f08f46260a46.png)](https://p4.ssl.qhimg.com/t012594f08f46260a46.png)

[![](https://p2.ssl.qhimg.com/t01661112e97bf9c2ec.png)](https://p2.ssl.qhimg.com/t01661112e97bf9c2ec.png)



## 实战

### <a class="reference-link" name="born2root:2"></a>born2root:2

第一步还是一样，探测靶机IP

[![](https://p5.ssl.qhimg.com/t011f3860d923e25418.png)](https://p5.ssl.qhimg.com/t011f3860d923e25418.png)

靶机IP：172.16.24.88

下一步老规矩，nmap 探测一下端口

[![](https://p5.ssl.qhimg.com/t01bb2d41a7e677b402.png)](https://p5.ssl.qhimg.com/t01bb2d41a7e677b402.png)

可以看到开放了3个端口，我们还是先看80端口

[![](https://p5.ssl.qhimg.com/t01a4919033766885c0.png)](https://p5.ssl.qhimg.com/t01a4919033766885c0.png)

在首页上翻了翻，也看了下源码，没什么突破口和可利用的，

下面我们还继续跑目录

[![](https://p2.ssl.qhimg.com/t015f79f05005eb3a7c.png)](https://p2.ssl.qhimg.com/t015f79f05005eb3a7c.png)

可以看到其开启使用了/joomla 框架

[![](https://p2.ssl.qhimg.com/t012a01312b0cd96588.png)](https://p2.ssl.qhimg.com/t012a01312b0cd96588.png)

我们使用joomscan跑一下看看

[![](https://p4.ssl.qhimg.com/t01e6922b09ea671b0e.png)](https://p4.ssl.qhimg.com/t01e6922b09ea671b0e.png)

可以看到没什么突破口

下一步我们的思路是使用cewl 爬取网站生成一个字典包吧（图中IP是测试时候的，懒就没重新弄了）

[![](https://p2.ssl.qhimg.com/t01243f08b2917981e2.png)](https://p2.ssl.qhimg.com/t01243f08b2917981e2.png)

下一步我们抓包爆破一下吧

[![](https://p4.ssl.qhimg.com/t0118a547595c398c8a.png)](https://p4.ssl.qhimg.com/t0118a547595c398c8a.png)

[![](https://p0.ssl.qhimg.com/t013b77bb2ca7e2474d.png)](https://p0.ssl.qhimg.com/t013b77bb2ca7e2474d.png)

爆破成功，成功拿到账号密码 admin – travel

[![](https://p0.ssl.qhimg.com/t01bdaa04ab0dc291ea.png)](https://p0.ssl.qhimg.com/t01bdaa04ab0dc291ea.png)

成功登陆到后台，

下一步就是拿webshell

步骤如下

1.

[![](https://p4.ssl.qhimg.com/t019d13f16a81245c32.png)](https://p4.ssl.qhimg.com/t019d13f16a81245c32.png)

2.

[![](https://p4.ssl.qhimg.com/t015ed6febb16514015.png)](https://p4.ssl.qhimg.com/t015ed6febb16514015.png)

3.

[![](https://p4.ssl.qhimg.com/t0114b37b61ac4808f8.png)](https://p4.ssl.qhimg.com/t0114b37b61ac4808f8.png)

把webshell 写入保存

4.

[![](https://p2.ssl.qhimg.com/t01115f1a0a1f1fae1d.png)](https://p2.ssl.qhimg.com/t01115f1a0a1f1fae1d.png)

勾选点亮五角星

[![](https://p2.ssl.qhimg.com/t01341592f060e0b925.png)](https://p2.ssl.qhimg.com/t01341592f060e0b925.png)

访问/joomla， 即可拿 shell

[![](https://p4.ssl.qhimg.com/t017a112618e3f646e2.png)](https://p4.ssl.qhimg.com/t017a112618e3f646e2.png)

下一步是提权，我们随便翻翻…

在 /opt/scripts/fileshare.py 看到了这个

[![](https://p4.ssl.qhimg.com/t01877fce63a603501e.png)](https://p4.ssl.qhimg.com/t01877fce63a603501e.png)

拿到ssh 账号密码 tim – lulzlol

使用ssh，成功登陆

[![](https://p1.ssl.qhimg.com/t01dfb4a861b8a3dc85.png)](https://p1.ssl.qhimg.com/t01dfb4a861b8a3dc85.png)

到了这里，我们还不是root权限，然后习惯性 sudo -l

[![](https://p4.ssl.qhimg.com/t01edac34914fdc9092.png)](https://p4.ssl.qhimg.com/t01edac34914fdc9092.png)

不用密码？

[![](https://p3.ssl.qhimg.com/t01a07384c2ff1eaf15.png)](https://p3.ssl.qhimg.com/t01a07384c2ff1eaf15.png)

然后成功拿到root权限，拿到flag

[![](https://p4.ssl.qhimg.com/t01f12da9f96598ecd0.png)](https://p4.ssl.qhimg.com/t01f12da9f96598ecd0.png)

本靶机完！

### <a class="reference-link" name="unknowndevice64:%202"></a>unknowndevice64: 2

通过上面靶机开启界面就可以看出其是一台Android设备

第一步还是一样，探测靶机IP

[![](https://p3.ssl.qhimg.com/t01a6c442299e31b09d.png)](https://p3.ssl.qhimg.com/t01a6c442299e31b09d.png)

靶机IP：172.16.24.73

下面还是nmap 探测一下开放端口

[![](https://p0.ssl.qhimg.com/t01232685b8c13574ae.png)](https://p0.ssl.qhimg.com/t01232685b8c13574ae.png)

可以看到靶机开放了3个端口，分别是 5555 、6465、12345

**第一个解题方法：**

5555端口是安卓的adb服务，我在前面的一篇文章中利用过，文章地址：[https://www.anquanke.com/post/id/158937](https://www.anquanke.com/post/id/158937)

这里这个靶机同样存在该漏洞，我们利用一下

1.先链接adb

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f197c19d53f41097.png)

2.直接连接

[![](https://p3.ssl.qhimg.com/t01bc8e3129bcd652b0.png)](https://p3.ssl.qhimg.com/t01bc8e3129bcd652b0.png)

连接成功，直接su 拿root权限

[![](https://p3.ssl.qhimg.com/t01b1abc72b62c33683.png)](https://p3.ssl.qhimg.com/t01b1abc72b62c33683.png)

**第二个解题方法：**

第一个方法比较简单，下面我们来演示第二种解题方法

我们把目光放在12345端口上，我们先确认一下它是个什么服务，我这里就直接简单的使用 curl 一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01df3ebc8ff879e1bd.png)

可以看到有非常明显的 html标签，我们使用浏览器打开

[![](https://p3.ssl.qhimg.com/t010cb1cbfb144073ed.png)](https://p3.ssl.qhimg.com/t010cb1cbfb144073ed.png)

一个登陆框，我肯定是想到准备抓包的，但是是这样的。。。

[![](https://p4.ssl.qhimg.com/t01e013511802ef0580.png)](https://p4.ssl.qhimg.com/t01e013511802ef0580.png)

没办法…. 只能手工的试一些常见的账号密码，结果一小会，成功试出了账号密码

administrator – password

[![](https://p4.ssl.qhimg.com/t0197b29e7a07af09ee.png)](https://p4.ssl.qhimg.com/t0197b29e7a07af09ee.png)

成功登陆，

继续摸索，有 /robots.txt

[![](https://p1.ssl.qhimg.com/t01ea7355697add065a.png)](https://p1.ssl.qhimg.com/t01ea7355697add065a.png)

继续跟进

[![](https://p4.ssl.qhimg.com/t01469761c4581063d8.png)](https://p4.ssl.qhimg.com/t01469761c4581063d8.png)

如上图中可以看到，该php里是有一个ssh的key文件，我这里单独保存出来

[![](https://p4.ssl.qhimg.com/t01bffb4d6111616d5e.png)](https://p4.ssl.qhimg.com/t01bffb4d6111616d5e.png)

下面直接ssh连接

[![](https://p2.ssl.qhimg.com/t013d52eba1aeab6990.png)](https://p2.ssl.qhimg.com/t013d52eba1aeab6990.png)

但是这里还是需要输入密码否则无法登陆，

小弟在这里卡里一会儿，使了好几个密码，都不行，然后又重新查看下载来的info.php，在最后注释出发现了这个

[![](https://p5.ssl.qhimg.com/t0178ccd5739d08878a.png)](https://p5.ssl.qhimg.com/t0178ccd5739d08878a.png)

最后才成功登陆

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0101404623ce21a390.png)

成功提权并拿到flag

[![](https://p0.ssl.qhimg.com/t01364b85b28387bab6.png)](https://p0.ssl.qhimg.com/t01364b85b28387bab6.png)

本靶机完！

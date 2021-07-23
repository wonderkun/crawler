> 原文链接: https://www.anquanke.com//post/id/146478 


# 360 Marvel Team IOT安全系列第一篇dji mavic破解


                                阅读量   
                                **144291**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t01f3f1fc1fef0ee8cf.jpg)](https://p5.ssl.qhimg.com/t01f3f1fc1fef0ee8cf.jpg)

作者：唐青昊

关于360 Marval Team IOT安全系列文章：该系列包括了多种受众较多并且有趣的设备，我们将在不产生公众影响的前提下将分析报告中的关键部分予以公开。目标是期待在攻防对抗的过程中，提升IOT产品的安全性。

关于DJI Mavic Pro：该机型是大疆无人机产品中的旗舰产品，可使用遥控器配合手机的方式对无人机进行操控。更多介绍请见DJI官网。



小型无人机产品在近几年发展迅速，销量逐年上升。全球各国对无人机的飞行管控也从到有建立起来，并且愈加严格。前几年可以随时飞无人机的户外景点，目前也都贴上了“NO DRONE ZONE”的标识。

[![](https://p2.ssl.qhimg.com/t012d797fe0f7b125bd.jpg)](https://p2.ssl.qhimg.com/t012d797fe0f7b125bd.jpg)

无人机的安全性是整个产业中非常重视的一环。因为一旦无人机可以随意飞行，将可能导致设施损失甚至人员伤亡。并且，跟据新闻报道，在中东战场出现了无人机被改装用来投弹的现象。

[![](https://p5.ssl.qhimg.com/t012b2fe618abd4dea5.jpg)](https://p5.ssl.qhimg.com/t012b2fe618abd4dea5.jpg)

无人机厂商为了保证产品安全性，设计了极为复杂的安全机制。如对无人机的实时GPS信号判断是否禁飞；对遥控器和无人机之间，以及手机和无人机之间的通信进行加密。这些措施保障了无人机在绝大多数情况下的稳定运行。

在国内一些特殊群体中也出现了使用GPS欺骗工具来破解禁飞的方法。这种使用物理设备对抗软件安全算法的尝试通常会导致无人机飞行功能不能充分使用，因此在成熟的无人机解决方案中较少出现。

在我们对DJI Mavic的安全性研究的分析过程中，发现了使用纯软件漏洞破解禁飞的方法。针对最新版无人机固件（V01.04.0300），可以通过usb连接无人机，然后运行我们的禁飞破解工具，即可通过更改无人机系统的方式实现禁飞破解。

以下是对无人机系统运行细节的截图。分别是进程列表信息，和对外监听端口的信息。

[![](https://p5.ssl.qhimg.com/t0156c5a7d5b5357f63.png)](https://p5.ssl.qhimg.com/t0156c5a7d5b5357f63.png)

[![](https://p3.ssl.qhimg.com/t01f046e513e8ea6703.png)](https://p3.ssl.qhimg.com/t01f046e513e8ea6703.png)



当禁飞解除后，可以实现在任意区域的飞行。如图所示：

[![](https://p3.ssl.qhimg.com/t019b971813e974e705.jpg)](https://p3.ssl.qhimg.com/t019b971813e974e705.jpg)

关于360 Marvel Team：Marvel Team是360公司安全研究员唐青昊在2015年成立的安全团队，致力于在互联网前沿业务领域开展信息安全技术研究。在2015至2017的时间中致力于云安全方向的虚拟化系统漏洞挖掘，发现数十枚高危安全漏洞，受邀在5个国际安全会议中进行演讲，并最终完成有安全奥运会之称的PWN2OWN比赛项目。在2018年开始在IOT和区块链领域的新征程。



**360 Marvel Team****历史文章：**

[《360MarvelTeam虚拟化漏洞第一弹 – CVE-2015-6815 漏洞分析》](http://blogs.360.cn/blog/360marvelteam%E8%99%9A%E6%8B%9F%E5%8C%96%E6%BC%8F%E6%B4%9E%E7%AC%AC%E4%B8%80%E5%BC%B9-cve-2015-6815-%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/)

[《360MarvelTeam虚拟化漏洞第二弹 – CVE-2015-5279 漏洞分析》](http://blogs.360.cn/blog/360marvelteam%E8%99%9A%E6%8B%9F%E5%8C%96%E6%BC%8F%E6%B4%9E%E7%AC%AC%E4%BA%8C%E5%BC%B9-cve-2015-5279-%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/)

[《360MarvelTeam虚拟化漏洞第三弹 – CVE-2015-7504 漏洞分析》](https://www.anquanke.com/post/id/83036)

[《360 Marvel Team虚拟化漏洞第四弹：CVE-2015-8567漏洞分析》](https://www.anquanke.com/post/id/83215)

[《360 Marvel Team虚拟化漏洞第五弹 – CVE-2016-3710 Dark Portal漏洞分析》](https://www.anquanke.com/post/id/83899)

[《360 Marvel Team云系统漏洞第六弹 – CVE-2016-8632分析》](https://www.anquanke.com/post/id/84966)



**360 Marvel Team****出版图书：**

《云虚拟化安全攻防实践》



**360 Marvel Team ****招聘信息：**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019b7bb7be3577affb.jpg)

**更多合作和招聘职位可见二维码：**

[![](https://p4.ssl.qhimg.com/t011090df46362baf32.png)](https://p4.ssl.qhimg.com/t011090df46362baf32.png)

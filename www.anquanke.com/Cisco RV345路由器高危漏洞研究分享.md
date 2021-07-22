> 原文链接: https://www.anquanke.com//post/id/237347 


# Cisco RV345路由器高危漏洞研究分享


                                阅读量   
                                **140026**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01faa81b49b4615c0b.jpg)](https://p3.ssl.qhimg.com/t01faa81b49b4615c0b.jpg)



## 0x0 前言

思科公司是全球领先的网络解决方案供应商。依靠自身的技术和对网络经济模式的深刻理解，思科成为了网络应用的成功实践者之⼀。



## 0x1 简介

关键点：upload.cgi中的fileparam参数，可以参考：[https://www.zerodayinitiative.com/advisories/ZDI-20-1100/](https://www.zerodayinitiative.com/advisories/ZDI-20-1100/)

[![](https://p0.ssl.qhimg.com/t01e386e6898104bf3b.png)](https://p0.ssl.qhimg.com/t01e386e6898104bf3b.png)



## 0x2 准备

固件版本 1.0.00.33：[https://software.cisco.com/download/home/286288298/type/282465789/release/1.0.03.20?catid=268437899](https://software.cisco.com/download/home/286288298/type/282465789/release/1.0.03.20?catid=268437899)

[![](https://p1.ssl.qhimg.com/t0120c21ba2c261e1ca.png)](https://p1.ssl.qhimg.com/t0120c21ba2c261e1ca.png)



## 0x3 工具

1.静态分析工具：IDA

2.系统文件获取：binwalk

3.抓包改包工具：Brup Suite



## 0x4 测试环境

Cisco RV345路由器真机测试，可以在某宝上或者某鱼上购买（学到的知识是无价的）。



## 0x5 漏洞分析

1.可以通过binwalk -Me参数进行解包。

[![](https://p4.ssl.qhimg.com/t01aa2f175fa95c8ed9.png)](https://p4.ssl.qhimg.com/t01aa2f175fa95c8ed9.png)

2.find -name “*cgi” 主要目的是搜索根目录在哪，可以看到如下图，路径比较长，所以通过find是最 好找到根目录的办法。

[![](https://p4.ssl.qhimg.com/t0156b0d97f35e5e08b.png)](https://p4.ssl.qhimg.com/t0156b0d97f35e5e08b.png)

[![](https://p3.ssl.qhimg.com/t0128af402c6d6f80b4.png)](https://p3.ssl.qhimg.com/t0128af402c6d6f80b4.png)

3.通过详细的描述可以发现，漏洞点出现在upload.cgi文件中（如果是低版本的1.0.00.33版本的话， 没有这个文件，只有高版本才有），那么漏洞点也出现在fileparam参数中，可以大致推测出漏洞点应该存在于固件更新页面。

[![](https://p0.ssl.qhimg.com/t01d516c347fa5d7caf.png)](https://p0.ssl.qhimg.com/t01d516c347fa5d7caf.png)

4.本人想通过reboot命令对路由器进行探测是否执行命令成功，发现貌似不能执行reboot，执行其他 命令也没什么反应，可能到这里有的兄弟就已经放弃了，就觉得是不是没有这个漏洞，或者漏洞点 不在这，但是…

[![](https://p5.ssl.qhimg.com/t0100ebed078a020744.png)](https://p5.ssl.qhimg.com/t0100ebed078a020744.png)

5.本人将固件版本降低重刷回 v1.0.00.33（官方最低版本）。

[![](https://p2.ssl.qhimg.com/t0197b1b96527590786.png)](https://p2.ssl.qhimg.com/t0197b1b96527590786.png)

6.然后使用我们已经构造好的POC并放到Burp Suite中，并使用reboot命令，发现路由器重启，证明存在命令执行漏洞。但是想查看有什么命令能执行。

[![](https://p2.ssl.qhimg.com/t01049a24925510913f.png)](https://p2.ssl.qhimg.com/t01049a24925510913f.png)

7.本人就想了一个办法，通过重定向符号”&gt;”，将打印的数据重定向到能访问的页面，或者创建一个可以访问的页面(xxx.html)。

[![](https://p1.ssl.qhimg.com/t01a9ce743eb87b2e10.png)](https://p1.ssl.qhimg.com/t01a9ce743eb87b2e10.png)

[![](https://p5.ssl.qhimg.com/t0175a4822a39d021aa.png)](https://p5.ssl.qhimg.com/t0175a4822a39d021aa.png)

8.低版本的Cisco RV345是没有telnetd这个命令的，但是高版本是存在telnetd的，本人便想通过上传高版本的busybox执行telnetd，发现居然不可以（可能是高版本的内核或者其他什么的不兼容低版本吧），那这样只能在网上找一个busybox上传了。最终获取到ROOT权限。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01703fa76f9fb20fe1.png)

9.经过各种测试，发现高版本是存在漏洞的，但是权限是比较低的 www-data 用户权限，和漏洞详细描述的一样，所以不能执行reboot命令，只能执行比较简单的命令。



## 0x6 补丁对比

1.没有补过漏洞的，没有过滤直接通过sprintf 复制给v11，最终执行system。

[![](https://p3.ssl.qhimg.com/t01dceb13da45d610cd.png)](https://p3.ssl.qhimg.com/t01dceb13da45d610cd.png)

2.多了一个match_regex函数的正则表达式，这样便不能输入特殊字符，也就无法导致命令执行漏洞了。

[![](https://p2.ssl.qhimg.com/t01206f0ad991ecefa7.png)](https://p2.ssl.qhimg.com/t01206f0ad991ecefa7.png)



## 0x7 总结

固件为高版本，感觉不能执行命令时，可以切换一下思路，将版本降低，再重试，或许有不同的收获，然后结合低版本的思路，再去灰盒高版本固件。

当漏洞存在时，使用 ls 等命令都无法输出命令结果时，那么此时就可以换一下思维，通过 “&gt;” 重定向符号或者其他方式将数据打印到访问的页面中。

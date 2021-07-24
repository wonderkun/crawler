> 原文链接: https://www.anquanke.com//post/id/83611 


# 最近暴露的几个CVE，可轻松获得安卓系统的ROOT权限


                                阅读量   
                                **93127**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://blog.trendmicro.com/trendlabs-security-intelligence/android-vulnerabilities-allow-easy-root-access/](http://blog.trendmicro.com/trendlabs-security-intelligence/android-vulnerabilities-allow-easy-root-access/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t019164240e8dec63fc.jpg)](https://p2.ssl.qhimg.com/t019164240e8dec63fc.jpg)

如今，美国高通 Snapdragon芯片组系列中的SoC（系统芯片）在智能设备所使用的芯片中占有很大比例。该公司的官方网站指出，有超过十亿的设备使用Snapdragon处理器或调制解调器。不幸的是，这些设备中许多都有可能允许攻击者获得root访问权限的漏洞。在设备上获得root访问权限是非常有利用价值的；它允许攻击者访问时使用其他级别的权限所没有的功能。



我们最近发现了一些基于Snapdragon芯片的安卓设备上的漏洞，这些漏洞可能会被攻击者利用来获得目标设备上的root访问权限，他们只需轻松运行一个恶意APP。现在这些漏洞已经被谷歌修复；我们私下向他们报告了这些问题以便他们打补丁并发布给公众。然而，由于移动端的漏洞和物联网(IoT)端的漏洞修补彼此分离，许多用户将无法收到他们所需要的安全更新，信息泄露等方面的危险可能仍然存在。



随着使用嵌入式系统级芯片（SoC）设备的数量的激增以及物联网的爆炸式增长，我们预计这类漏洞将成为一个更大的问题，会挑战物联网的整体安全状况。



**        CVE-2016-0819**

我们发现这个特别的漏洞，它在内核内的对象被释放时被描述为一个逻辑错误。它被释放前有个节点被删除过两次。这将导致信息泄漏及安卓设备中的Use After Free问题。 （UAF漏洞众所周知，特别是广泛用于Internet Explorer。）



**  CVE-2016-0805**

这种漏洞重点在于函数get_krait_evtinfo。 （Krait和几个Snapdragon处理器使用的处理器内核有关）。该函数返回一个数组的索引；然而，这种函数的输入的验证是不够的。所以，当数组krait_functions被函数krait_clearpmu和krait_evt_setup访问后，会出现一个超出范围的访问结果。这作为多重漏洞组合攻击的一部分十分有用。



**        获得root访问权限**

利用这两个漏洞，可以获得基于的Snapdragon安卓设备上的root访问权限。这可以通过设备上的恶意APP来完成。为了防止针对于已修复的漏洞或者尚未发现的其他漏洞的更多攻击的发生，我们没有透露这次攻击的全部细节。我们将在即将举行的荷兰Hack In The Box 安全会议上的演讲中透露更多的细节，该会议在2016年五月下旬举行。



**        什么样的设备容易被攻击？**

系统调用perf_event_open（此次攻击中使用过的）在大多数智能手机中是公开的。然而，供应商可以高度定制他们设备的内核和SELinux策略，因此很难确定哪些设备容易受到攻击。



据谷歌2月份的安全公告，CVE-2016-0805漏洞影响先于4.4.4到6.0.1的版本。我们不能全面测试所有的安卓设备，但我们自己的测试表明以下设备会受到影响：

Nexus 5

Nexus 6

Nexus 6P

Samsung Galaxy Note Edge



我们认为，所有3.10内核版本的Snapdragon安卓设备被攻击的可能性比较大。正如前面提到的，因为这些设备中许多要么不再进行补丁修复，要么从一开始就从未收到过任何补丁，它们本质上就处在不安全的状态。



**总结**

此次攻击允许攻击者在目标设备上获得最高权限执行任何代码。不过，要想实现仍然需要攻击者把他的恶意程序安装到设备上。用户应该非常小心安装来自不受信任来源的应用，特别是那些Play商店之外的应用 。



我们建议安卓用户和制造商联系查看是否有修复该漏洞的补丁可供使用 。

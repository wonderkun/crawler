> 原文链接: https://www.anquanke.com//post/id/107455 


# SNMP配置文件注入获取shell


                                阅读量   
                                **119424**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01789d72a8bca17b48.jpg)](https://p1.ssl.qhimg.com/t01789d72a8bca17b48.jpg)

## 测试过程

前不久，我在测试一个web应用时，发现可以注入任意内容到SNMP配置文件中，然后利用更新的配置文件来重启服务；我已经能够通过web接口修改社区字符串(community string:人类可读的字符串数据值)并且允许访问任意IP，我个人感觉觉得这个发现虽然挺有意思，但是也很low。我跟我的朋友Sandro Gauci说到这个情况，恰巧他有所了解，并说当以特定方式访问SNMP服务器时可以让服务器执行shell命令。这听起来就很有意思了，比只是向配置文件中写入几行东西好玩多了，于是我开始深挖。



我已经知道服务器是Debian系统(是的，这些低级信息泄露迟早有用)，这就意味着它很可能运行着标准的Net-SNPM软件包，一番搜索之后，我找到了一篇非常有用的博文,博文地址：[http://net-snmp.sourceforge.net/wiki/index.php/Tut:Extending_snmpd_using_shell_scripts](http://net-snmp.sourceforge.net/wiki/index.php/Tut:Extending_snmpd_using_shell_scripts)

初始配置文件非常简单，内容如下：

[![](https://p4.ssl.qhimg.com/t014e2da8b8e11748fb.png)](https://p4.ssl.qhimg.com/t014e2da8b8e11748fb.png)

我可以往里添加新的内容，如写入不同的IP地址或者查找他们的社区字符串，如图：

[![](https://p5.ssl.qhimg.com/t01cfe90f79cf3eb79c.png)](https://p5.ssl.qhimg.com/t01cfe90f79cf3eb79c.png)

通过阅读上面那篇博文，我知道添加的内容的格如下：

[![](https://p2.ssl.qhimg.com/t014c883f1427dd3f02.png)](https://p2.ssl.qhimg.com/t014c883f1427dd3f02.png)

这会告诉SNMP服务当有人向它请求扩展信息时执行echo命令并且返回输出内容，还带有扩展参数名test。由此，我提交了如下内容：

[![](https://p4.ssl.qhimg.com/t013f7b4c50f1c24b09.png)](https://p4.ssl.qhimg.com/t013f7b4c50f1c24b09.png)

中间的%0a%0d会解码成换行和回车，解码后配置文件如下：

[![](https://p0.ssl.qhimg.com/t0191be6505ac63484a.png)](https://p0.ssl.qhimg.com/t0191be6505ac63484a.png)

现在连接服务器看看是否有效：

[![](https://p3.ssl.qhimg.com/t01c296200c2bf33a64.png)](https://p3.ssl.qhimg.com/t01c296200c2bf33a64.png)

完犊子，报错了，报错内容如下：

[![](https://p3.ssl.qhimg.com/t014c2c3c577560677a.png)](https://p3.ssl.qhimg.com/t014c2c3c577560677a.png)

怎么办捏，找原因呗，查找了大量文章后，我看到了这篇文章：

[https://l3net.wordpress.com/2013/05/12/installing-net-snmp-mibs-on-ubuntu-and-debian/](https://l3net.wordpress.com/2013/05/12/installing-net-snmp-mibs-on-ubuntu-and-debian/)

这篇文章解释了出错是因为证书问题，Ubuntu只能处理可用MIBs(管理信息库)的子集合，如果要使用完整MIBs的话，需要安装额外软件包并且更新客户端配置文件。

安装完成后，我又试了一遍，结果如下：

[![](https://p1.ssl.qhimg.com/t011c4b93931834fdc8.png)](https://p1.ssl.qhimg.com/t011c4b93931834fdc8.png)

大功告成，MIB更新后生效，echo命令也得以执行，我也获取到了输出内容。

除了输出内容外，可能还会伴随着报错信息，报错位置如图：

[![](https://p5.ssl.qhimg.com/t015dca67051af2995d.png)](https://p5.ssl.qhimg.com/t015dca67051af2995d.png)

不过不用担心，这并不会影响我们的操作。如果你想让它不报错的话，可以瞅瞅下面这篇文章：

[https://docs.linuxconsulting.mn.it/notes/net-snmp-errors](https://docs.linuxconsulting.mn.it/notes/net-snmp-errors)

万事俱备，只欠东风，现在要做的就是getshell；

恰巧Debian系统中的Netcat包版本中有 –e 参数(再次证明信息泄露的重要性，一些Linux发行版自带的Netcat版本没有 –e 参数，你需要利用其它技巧)；

利用这个参数，我向配置文件中注入了一个简单的反弹shell命令，设置好我的监听器后重新执行snmpwalk命令。最终SNMP配置文件如下：

[![](https://p0.ssl.qhimg.com/t01f5a5728be75939e8.png)](https://p0.ssl.qhimg.com/t01f5a5728be75939e8.png)

Netcat设置监听：

[![](https://p5.ssl.qhimg.com/t01f60e9db23d39249f.png)](https://p5.ssl.qhimg.com/t01f60e9db23d39249f.png)

输入Snmpwalk命令来触发：

[![](https://p4.ssl.qhimg.com/t01181e8ef05e2ce278.png)](https://p4.ssl.qhimg.com/t01181e8ef05e2ce278.png)

这里出现了超时退出，处理请求的SNMP线程阻塞了shell并且没有返回，所以客户端放弃等待，超时退出。

最后一点，SNMP服务并没有设置路径，所以所有命令和文件都必须使用绝对路径，如/bin/nc，而不是直接使用nc命令



## 防御措施

1.因为社区字符串可以使用哪些字符并没有进行正式定义，不过很多公司有他们自己定义的标准。绝大部分都允许字母数字字符集和一些特殊符号。

所以你可以定义自己的字符集，然后写个正则来检查输入就是小菜一碟了。

2.删除或者编码已知恶意字符，比如换行符。这样做比较麻烦，你需要想到所有可能的恶意字符，如果漏掉一个，攻击者便可以利用它来攻击你。

话虽如此，但是增加一个函数调用来删除换行符并不会增加多大开销并且在这个案例中能够保护你的客户端。

文章到此结束，这就是从一个简单的文件注入到getshell的全部过程，希望各位看官喜欢。



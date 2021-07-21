> 原文链接: https://www.anquanke.com//post/id/86728 


# 【安全工具】faraday：协同渗透测试和漏洞管理平台（18:30增加演示视频）


                                阅读量   
                                **157998**
                            
                        |
                        
                                                                                    



**[![](https://p2.ssl.qhimg.com/t017bd15f71009d09c2.png)](https://p2.ssl.qhimg.com/t017bd15f71009d09c2.png)**

**下载链接：**[**https://github.com/infobyte/faraday**](https://github.com/infobyte/faraday)** ******

**前言**

Hi，安全客的小伙伴们大家好，今天给大家介绍一款名叫faraday的安全工具。准确的说**faraday是一个渗透测试协作和漏洞管理平台**。此款工具曾多次入选BlackHat兵工厂及各安全会议。**本文将向大家分享一下使用这款工具的体验报告。**

[![](https://p0.ssl.qhimg.com/t012e7be76cc30d1eb7.png)](https://p0.ssl.qhimg.com/t012e7be76cc30d1eb7.png)

图1：部分会议相关链接



**工具介绍**

**Faraday平台的开发引入了一个全新的概念：IPE（综合渗透测试环境），这是一个多用户的渗透测试协作平台。**专为在安全审计期间生成的数据进行分发，索引和分析而设计。

Faraday的主要目的是结合安全社区中的常用工具，以多用户的方式利用它们。

显而易见的是，作为用户的我们要知道我们在终端中常用的一些安全工具和Faraday包括的工具是没有任何区别的。该平台仅仅是开发了一套专门的功能，帮助用户改进自己的工作。

写过代码的同学都知道，在进行项目开发的时候使用IDE可以极大的提高我们的工作效率。Faraday也一样，甚至说Faraday就是为了提高渗透测试人员的工作效率而生！



**安装指南**

Faraday支持如下几款操作系统：

[![](https://p3.ssl.qhimg.com/t012e6b06bb8c8d9659.png)](https://p3.ssl.qhimg.com/t012e6b06bb8c8d9659.png)

以Linux为例，具体安装方法如下



```
$ git clone https://github.com/infobyte/faraday.git faraday-dev
$ cd faraday-dev
$ ./install.sh
$  service couchdb start
$ ./faraday-server.py
$ ./faraday.py
```

在安装完成后，运行faraday-server.py之前要先启动CouchDB数据库服务，即要先执行service couchdb start否则会报这个错误：



```
root@kali:~/faraday-dev# ./faraday-server.py
2017-08-22 18:05:24,971 - faraday-server.__main__ - INFO - Checking dependencies...
2017-08-22 18:05:24,971 - faraday-server.__main__ - INFO - Dependencies met
2017-08-22 18:05:25,883 - faraday-server.server.couchdb - WARNING - Reports database couldn't be uploaded. You need to be an admin to do it
2017-08-22 18:05:26,953 - faraday-server.server.importer - ERROR - CouchDB is not running at http://localhost:5984. Check faraday-server's configuration and make sure CouchDB is running
```

启动后的界面如下图所示：

[![](https://p3.ssl.qhimg.com/t01d8653dff3b07d8ff.png)](https://p3.ssl.qhimg.com/t01d8653dff3b07d8ff.png)

点击第3个图标即可跳转到

[![](https://p0.ssl.qhimg.com/t012e22def07c60df02.png)](https://p0.ssl.qhimg.com/t012e22def07c60df02.png)

为了简单起见，用户应该注意到他们自己的终端应用程序和Faraday包含的应用程序之间没有区别。开发了一套专门的功能，帮助用户改进自己的工作。你还记得自己编程没有IDE吗？在渗透测试这个领域Faraday就像是在编程时的IDE一样。

更多详情请阅读[**release日志**](https://github.com/infobyte/faraday/blob/master/RELEASE.md)！

**安装演示视频**

**<br>**

**<br>**

**功能展示**

**工作空间**

工作空间为每一个渗透工程师的不同工作环境，Faraday汇总渗透团队全部的渗透成果，并将信息已图表等形式展示出来。

**使用演示视频**

**<br>**

**<br>**

**Faraday插件**



使用Faraday插件，可以使用命令行执行不同的操作，例如：

```
$ cd faraday-dev/bin/
$ ./fplugin create_host 192.154.33.222 Android
1a7b2981c7becbcb3d5318056eb29a58817f5e67
$ ./fplugin filter_services http ssh -p 21 -a
Filtering services for ports: 21, 22, 80, 443, 8080, 8443
192.168.20.1    ssh [22]    tcp open    None
192.168.20.1    http    [443]   tcp open    None
192.168.20.7    ssh [22]    tcp open    Linux
192.168.20.7    http    [443]   tcp open    Linux
192.168.20.11   ssh [22]    tcp open    Linux
```

**通知**

其他Faraday实例上的对象更新之后，Faraday GTK客户端就会收到通知。

[![](https://p1.ssl.qhimg.com/t0127ea546619140d0a.png)](https://p1.ssl.qhimg.com/t0127ea546619140d0a.png)

值得一提的是，如果你使用的是ZSH UI则通过命令行的方式进行通知（没有GUI）

[![](https://p5.ssl.qhimg.com/t0136b55024193f7448.png)](https://p5.ssl.qhimg.com/t0136b55024193f7448.png)

**CSV导出**

Faraday支持从Web端导出CSV格式。为了将内容以CSV的格式导出，可以点击左侧导航栏上数第2个的Status Report（状态报告）。

[![](https://p4.ssl.qhimg.com/t0146b84c0cb532dcf5.png)](https://p4.ssl.qhimg.com/t0146b84c0cb532dcf5.png)

然后单击工作区旁边的绿色下载链接

[![](https://p0.ssl.qhimg.com/t013a99434e5dcfd2d9.png)](https://p0.ssl.qhimg.com/t013a99434e5dcfd2d9.png)

可以在搜索框中过滤留下我们需要的信息。<br>

[![](https://p4.ssl.qhimg.com/t01bcbed9d74901accf.png)](https://p4.ssl.qhimg.com/t01bcbed9d74901accf.png)

更多实用功能还望各位看官自行发掘体验！<br>



**插件**

不要改变你现在的工作方式！不要担心你平常使用的工具会跟Faraday存在兼容性方面的问题。现在Faraday已经支持50款常用安全工具。

**插件主要分为3种类型**

**拦截命令插件**，在控制台中检测到命令时直接触发，这类插件对你来说是透明的，你无需考虑其他内容

**导入文件报告的插件**，你必须将报告复制到，$HOME/.faraday/report/[workspacename]（用工作空间的实际名字替换到这部分。Faraday将自动检测、处理并将其添加到HostTree。）插件connectors或online（BeEF，Metasploit，Burp），这些连接到外部API或数据库，或直接与Faraday的RPC API通信。

**API**

**插件列表**

Faraday诞生的主要用途是重新复用安全社区中的常用工具，以多用户协作的方式利用它们。为了最大限度地发挥Faraday的灵活性，其插件在客户端上运行，这意味着你可以自己提供一些自定义的插件。

Faraday的插件分为3种形式：控制台、报告和API。然而，这些并不是互斥的，而是说在使用安全工具时，有多个插件来处理它们的输出。举个例子，Nmap有一个控制台插件，允许您直接从ZSH运行它，但它也有一个报告插件，以便导入Faraday之外的扫描结果。

**控制台**

拦截命令的插件，在控制台中检测到命令输入时直接触发。该功能是自动进行的，无需采取任何额外的操作。

**报告**

导入文件报告的插件，可以将报告复制到~/.faraday/report/`{`workspacename`}`（使用Workspace的实际名称替换`{`workspacename`}`的内容），Faraday GTK客户端将自动检测，处理并将其添加到HostTree中。如果Faraday无法检测到处理报告所需的插件，则可以在扩展名之前通过在文件名中添加_faraday_pluginName来人工选择将使用哪个插件。

例如，如果未识别名为burp_1456983368.xml的Burp报告，请尝试将其重命名为Burp_1456983368_faraday_Burp.xml。现在将其复制到Workspace目录中，Faraday现在应该运行插件并导入所有漏洞。

请记住，此功能区分大小写。 可用插件的名称是：



```
Acunetix
Arachni
Burp
Core Impact
Maltego
Metasploit
Nessus
Netsparker
Nexpose
NexposeFull
Nikto
Nmap
Openvas
Qualysguard
Retina
W3af
X1
Zap
```

**API**

插件连connectors或online（BeEF，Metasploit，Burp），这些连接到外部API或数据库，或直接与Faraday的RPC API通信。

<br>

**目前Faraday支持的安全工具列表**

Acunetix (REPORT) (XML)

Amap (CONSOLE)

Arachni (REPORT, CONSOLE) (XML)

arp-scan (CONSOLE)

BeEF (API)

Burp, BurpPro (REPORT, API) (XML)

Core Impact, Core Impact (REPORT) (XML)

Dig (CONSOLE)

Dirb (CONSOLE)

Dnsenum (CONSOLE)

Dnsmap (CONSOLE)

Dnsrecon (CONSOLE)

Dnswalk (CONSOLE)

evilgrade (API)

Fierce (CONSOLE)

Fruitywifi (API)

ftp (CONSOLE)

Goohost (CONSOLE)

hping3 (CONSOLE)

Hydra (CONSOLE) (XML)

Immunity Canvas (API)

Listurls (CONSOLE)

Maltego (REPORT)

masscan (REPORT, CONSOLE) (XML)

Medusa (CONSOLE)

Metagoofil (CONSOLE)

Metasploit, (REPORT, API) (XML) XML report

Ndiff (REPORT, CONSOLE)

Nessus, (REPORT) (XML .nessus)

Netcat (CONSOLE)

Netdiscover (CONSOLE)

Netsparker (REPORT) (XML)

Nexpose, Nexpose Enterprise, (REPORT) (simple XML, XML Export plugin (2.0))

Nikto (REPORT, CONSOLE) (XML)

Nmap (REPORT, CONSOLE) (XML)

Openvas (REPORT) (XML)

PasteAnalyzer (CONSOLE)

Peeping Tom (CONSOLE)

ping (CONSOLE)

propecia (CONSOLE)

Qualysguard (REPORT) (XML)

Retina (REPORT) (XML)

Reverseraider (CONSOLE)

Sentinel (API)

Shodan (API)

Skipfish (CONSOLE)

Sqlmap (CONSOLE)

SSHdefaultscan (CONSOLE)

SSLcheck (CONSOLE)

Telnet (CONSOLE)

Theharvester (CONSOLE)

Traceroute (CONSOLE)

W3af (REPORT) (XML)

Wapiti (CONSOLE)

Wcscan (CONSOLE)

Webfuzzer (CONSOLE)

whois (CONSOLE)

WPScan (CONSOLE)

X1, Onapsis (REPORT) (XML)

Zap (REPORT) (XML)

<br>

**参考链接**

[https://github.com/infobyte/faraday](https://github.com/infobyte/faraday)

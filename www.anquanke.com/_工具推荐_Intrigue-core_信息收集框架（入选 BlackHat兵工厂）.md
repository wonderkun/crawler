> 原文链接: https://www.anquanke.com//post/id/85783 


# 【工具推荐】Intrigue-core：信息收集框架（入选 BlackHat兵工厂）


                                阅读量   
                                **121743**
                            
                        |
                        
                                                                                    



**[![](https://p5.ssl.qhimg.com/t01500a3dc62c3a4be5.png)](https://p5.ssl.qhimg.com/t01500a3dc62c3a4be5.png)**

**Github地址：[https://github.com/intrigueio/intrigue-core](https://github.com/intrigueio/intrigue-core) **

**渗透测试的信息收集阶段**

信息收集在渗透测试的过程中起着重要的作用，在这个阶段我们需要尽可能多的收集目标企业的信息。

**一般情况下信息收集的方式主要分为主动收集和被动收集。主动收集的主要方式为爆破、扫描等。被动收集即通过搜索引擎、社交平台、whois查询等方式收集目标企业公开的一些信息。**

两种方法各有优劣，主动收集获得的信息更加详细准确，但由于扫描、爆破是需要与目标网络中的主机通信，会留下踩点的痕迹。被动收集相对隐蔽，但是收集的信息则相对较少。

总之在一次完整的渗透测试中两种方式缺一不可，只有对目标企业的网络信息多次不断的收集，在对方网络环境改变时，才能做到知己知彼，游刃有余。

<br>

**信息收集框架的引入**

随着大家信息安全意识的不断提高，以及现代开发框架的广泛应用、CDN、WAF的普及、各大厂商纷纷建立自己的信息安全团队导致现今漏洞出现点、利用方法、利用难易程度，发生了一些变化。

无论你是一个渗透测试人员想毫不费力的拿下目标站点，还是一个白帽子向在更短的时间内发现更多的漏洞，亦或你是一个企业网络的安全负责人。信息收集在工作进程中都起着相当重要的作用。

目标网络的复杂化、安全团队的专业化，如今渗透测试早已不是一个人可以单枪匹马去ko一个项目的了，那么一个多元化的渗透测试团队如何相互协作，在信息收集阶段避免信息冗余、遗漏、重复收集将会是一个至关重要的问题。

本篇文章中，我们将介绍一款开源信息收集框架Intrigue-core，通过Intrigue-core可以更加方便、全面的侦测到目标企业更多的攻击面，可有效将收集到的信息以点线、图表等方式呈现，直观了解到各主机、域名等信息的相关性。

<br>

**Intrigue-core**

**通过Docker部署Intrigue-core**

使用docker快速安装intrigue-core，首先你要在你的机器上[[安装docker]](https://docs.docker.com/engine/installation/#docker-variants)

接下来，通过git clone将其从[[git仓库]](https://github.com/intrigueio/intrigue-core)中拉下来



```
$ git clone https://github.com/intrigueio/intrigue-core
$ cd intrigue-core
$ docker build .
$ docker run -i -t -p 7777:7777
```

执行完如上命令后将会启动postgres、redis、intrigue-core服务，你将会看到如下输出。



```
Starting PostgreSQL 9.6 database server                                                                                                                                                           [ OK ] 
Starting redis-server: redis-server.
Starting intrigue-core processes
[+] Setup initiated!
[+] Generating system password: hwphqlymmpfrqurv
[+] Copying puma config....
[ ] File already exists, skipping: /core/config/puma.rb
* Listening on tcp://0.0.0.0:7777
Use Ctrl-C to stop
```

**译者注：**

在搭建这个框架的过程中我使用的操作系统是Ubuntu 14.04 x64，安装过程中遇到一些问题，主要是Dockerfile的事，做了一些修改，添加了一些内容，如下图所示：

[![](https://p3.ssl.qhimg.com/t01e1859d4fc07165d8.png)](https://p3.ssl.qhimg.com/t01e1859d4fc07165d8.png)

当它启动时，你可以看到它生成一个密码。你现在可在在你的机器上访问，http://localhost:7777然后通过用户名intrigue和之前随机生成的密码去登陆。

URI: http://localhost:7777

用户名: intrigue

密码: [随机生成，参考上文界面]

现在，尝试一下，创建一个项目：

[![](https://p1.ssl.qhimg.com/t01bd12695e1c9445a6.png)](https://p1.ssl.qhimg.com/t01bd12695e1c9445a6.png)

现在你已经创建了一个新的项目，让我们单独运行一下。

[![](https://p1.ssl.qhimg.com/t016514720081227f78.png)](https://p1.ssl.qhimg.com/t016514720081227f78.png)

可以看到这里有很多有趣的东西。

[![](https://p0.ssl.qhimg.com/t01eb8f1d603b8146c5.png)](https://p0.ssl.qhimg.com/t01eb8f1d603b8146c5.png)

我们可以点击任何一个新的按钮，去开始一个新的任务，首先让我们来查一下DNS的解析记录，sip.microsoft.com。点击这里你将看到所有实体的内容，同时当任务运行后，我们可以在所有的dns记录实体中选择其中一个进行查看。

[![](https://p5.ssl.qhimg.com/t018b750ea46871781b.png)](https://p5.ssl.qhimg.com/t018b750ea46871781b.png)

在本案例中，我们可以选择” nmap scan”,然后点击” Run Task”,允许我们使用这个功能。

[![](https://p1.ssl.qhimg.com/t01fd0a071bf1cd46c6.png)](https://p1.ssl.qhimg.com/t01fd0a071bf1cd46c6.png)

继续执行，你会发现。

我们可有注意到许多任务都需要api key，这个key可以在”Configure”标签中配置，每一个列表都有一个方便处理的链接，你可以在那配置api key

[![](https://p3.ssl.qhimg.com/t0138907963fae6c060.png)](https://p3.ssl.qhimg.com/t0138907963fae6c060.png)

不要忘记查看“Dossier”和“Graph”，向您展示的所有实体的列表，所有实体节点的图示信息：

[![](https://p1.ssl.qhimg.com/t0185e301a683af741b.png)](https://p1.ssl.qhimg.com/t0185e301a683af741b.png)

哦，点击其中的任意一个节点，你可以查看更多的详细信息！

[![](https://p3.ssl.qhimg.com/t01e8aed4102346ded0.png)](https://p3.ssl.qhimg.com/t01e8aed4102346ded0.png)

<br>

**通过扫描发现更多的攻击面（实例演示）**

当你看到这个部分，你已经使用[[Docker]](https://intrigue.io/2017/03/07/using-intrigue-core-with-docker/)创建了一个intrigue-core实例，所以本节将通过一个真实场景来介绍intrigue-core的使用方法。首先创建一个新项目，让我们扫描一下Mastercard（他们在[[Bugcrowd]](https://bugcrowd.com/mastercard)上发布了漏洞悬赏计划）：

[![](https://p5.ssl.qhimg.com/t01dabf96154ee8454a.png)](https://p5.ssl.qhimg.com/t01dabf96154ee8454a.png)

现在，运行“Create Entity（创建实体）”创建一个名称为“mastercard.com”的DnsRecord（DNS记录）查询任务。

此时，设置递归查询深度为3。这将告诉系统运行所有可行的任务，当一个新的实体创建，递归查询，直到我们达到我们的设置的最大深度：

[![](https://p0.ssl.qhimg.com/t012d36248d80c594cc.jpg)](https://p0.ssl.qhimg.com/t012d36248d80c594cc.jpg)

点击“Run Task（运行任务）”你将看到该实体成功创建：

[![](https://p1.ssl.qhimg.com/t01a0300101ba4fae1f.jpg)](https://p1.ssl.qhimg.com/t01a0300101ba4fae1f.jpg)

[![](https://p3.ssl.qhimg.com/t0181f6321c79698b2f.jpg)](https://p3.ssl.qhimg.com/t0181f6321c79698b2f.jpg)

现在，我们看一下“Results（结果）”选项卡，可以看到“Autoscheduled Tasks”的扫描结果已经在我们眼前呈现：

[![](https://p3.ssl.qhimg.com/t011a26057096d00980.jpg)](https://p3.ssl.qhimg.com/t011a26057096d00980.jpg)

请注意，每次刷新加载页面时都重新会生成图表，对于部分信息不能正常显示，你可以多刷新几次试试。 还可以放大和缩小以获取节点上的详细信息：

[![](https://p0.ssl.qhimg.com/t013fddbe55aae41d9c.jpg)](https://p0.ssl.qhimg.com/t013fddbe55aae41d9c.jpg)

浏览下“Dossier（档案）”，你可以看到，在一些公网业务主机下的一些指纹，这里没有任何入侵行为的，仅仅是页面抓取和分析后的结果：

[![](https://p1.ssl.qhimg.com/t01adaa59f446ac61e1.jpg)](https://p1.ssl.qhimg.com/t01adaa59f446ac61e1.jpg)

一个简洁的功能是Core实际上解析Web内容 、包括PDF和其他文件格式，拉出更多的元数据，所有这一切只需几分钟：

[![](https://p5.ssl.qhimg.com/t011a62464943070687.jpg)](https://p5.ssl.qhimg.com/t011a62464943070687.jpg)

<br>

**总结**

工欲善其事，必先利其器。一款好用的信息收集框架可以让我们在渗透测试中快速、准确的定位到薄弱环节，实施有针对性的安全测试。

**<br>**

**参考链接**

[https://github.com/intrigueio/intrigue-core](https://github.com/intrigueio/intrigue-core) 

[https://intrigue.io/](https://intrigue.io/)

[https://intrigueio.files.wordpress.com/2015/08/slides.pdf](https://intrigueio.files.wordpress.com/2015/08/slides.pdf)

[http://www.freebuf.com/articles/system/58096.html](http://www.freebuf.com/articles/system/58096.html)

[https://www.leavesongs.com/PENETRATION/edusoho-debug-user-information-disclose.html](https://www.leavesongs.com/PENETRATION/edusoho-debug-user-information-disclose.html)

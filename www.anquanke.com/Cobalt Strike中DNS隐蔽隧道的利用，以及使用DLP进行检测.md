> 原文链接: https://www.anquanke.com//post/id/99408 


# Cobalt Strike中DNS隐蔽隧道的利用，以及使用DLP进行检测


                                阅读量   
                                **292245**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">11</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t0113858d6436d4ab16.png)](https://p2.ssl.qhimg.com/t0113858d6436d4ab16.png)

> 本系列教程介绍演示常见外部入侵和内部威胁的手法、战术、以及工具，并给出使用现有成熟产品进行检测和响应的实际方法。



## 概述

现在，无论是开源或者商业套装渗透软件的应用已经得到普及。虽然目前各大安全技术网站有很多入门文章，但来源多为境外翻译加入译者想象，且有不少内容错误凸显译者缺乏实际操作经验。同时，如何利用市面现有产品实施检测的指导文章也凤毛麟角。因此，笔者计划编写系列教程，介绍演示常见外部入侵和内部威胁的手段、战术、以及工具，并给出使用现有成熟产品进行检测和响应的实际方法。

恶意利用DNS隧道现象已存在多年，将数据封装在DNS协议中传输已经是高级威胁团伙的标配工具。大部分防火墙和入侵检测设备很少会过滤DNS流量，僵尸网络和入侵攻击可几乎无限制地加以利用，实现诸如远控、文件传输等操作，例如前段时间危害巨大的Xshell木马、PANW刚刚披露的伊朗黑客组织OilRig等。同时，内部恶意员工也逐渐学会了使用类似工具盗取关键数据资产。

DNS隐蔽隧道建立通讯并盗取数据，可轻易绕过传统安全产品，使用特征技术难以检测。广为人知的渗透商业软件Cobalt Strike和开源软件iodine、DNScat2等亦提供了现成模块，可被快速轻易地利用。对进行渗透测试的红军来说，熟练掌握隐蔽通畅的DNS隧道至关重要；而对于甲方安全和风控团队来说，在DNS隐蔽隧道盗取数据的工具和方法得到普及的今天，此类数据泄露渠道须得到应有的重视。

本篇分步详细讲解Cobalt Strike这一广泛应用的商业渗透软件中DNS隐蔽隧道的设置和利用，带领读者成功将目标系统中的数据外传，并简略展示分析其通信数据包，说明检测算法，最后演示使用现有DLP产品实现检测未知威胁。



> 分步骤指导教程尽可能写得简单易上手，希望每位读者都可以学会后日常应用。



## 架设实验环境

让我们先将实际验证环境架设好。笔者选择了一台阿里云服务器安装Ubuntu 16.04系统作为Cobalt Strike Team Server，一台Windows 7 x86虚拟机用作被攻击盗取数据的目标，以及一台本地Kali Linux运行Cobalt Strike管理界面，最后需要一个可以配置的域名。读者可以按照自己喜好自行修改。

[![](https://p3.ssl.qhimg.com/t0140c362d22e6c7168.png)](https://p3.ssl.qhimg.com/t0140c362d22e6c7168.png)

首先，在云服务器(IP: 3*.1**.***.***)上安装Team Server。按照官方手册安装Cobalt Strike十分简单，目前在Ubuntu上安装Java 1.7需要添加apt源，具体操作步骤读者搜索一下即可获取。解压Cobalt Strike后运行命令./teamserver [IP] [password]即可启动Team Server；为防止ssh登录注销后关闭，需要加入nohup或&amp;命令保持后台运行。此外，大部分云服务商需用户自行配置打开服务器端口。一般来说，Team Server的缺省管理端口为50050，至少需要53 UDP供DNS协议使用，还有80和8080端口也常被使用。

然后，在Kali中运行Cobalt Strike，使用IP和password连接Team Server。

[![](https://p4.ssl.qhimg.com/t017660b4f1fd53a4a5.png)](https://p4.ssl.qhimg.com/t017660b4f1fd53a4a5.png)

以上步骤官方手册写得十分清楚，笔者这里就不赘述了。

接下来，我们配置域名cirrus.[domain]用于DNS隐蔽隧道，如下图所示：创建A记录，将自己的域名解析服务器(ns.cirrus.[domain])指向Team Server；再创建NS记录将dnsch子域名的解析交给ns.cirrus.[domain]。

[![](https://p4.ssl.qhimg.com/t0177ec69b7eb7ea915.png)](https://p4.ssl.qhimg.com/t0177ec69b7eb7ea915.png)

之后，在Cobalt Strike中创建一个使用DNS的监听器，如下图所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016bb2b4961fda62ec.png)

[![](https://p5.ssl.qhimg.com/t0179fea53946c0dab9.png)](https://p5.ssl.qhimg.com/t0179fea53946c0dab9.png)

请注意选择payload的模式为windows/beacon_dns/reverse_dns_txt，之后便会利用DNS TXT记录下载payload，避开传统安全产品的检测。

然后会弹窗提示进行监听用域名的配置，将刚才设置NS记录的子域名填入即可。

[![](https://p3.ssl.qhimg.com/t015feb284b795c14a6.png)](https://p3.ssl.qhimg.com/t015feb284b795c14a6.png)

这时我们即可测试域名配置是否正确：nslookup cirrus.dnsch.cirrus.[domain]

[![](https://p4.ssl.qhimg.com/t016fce3cde259f7d42.png)](https://p4.ssl.qhimg.com/t016fce3cde259f7d42.png)

Cobalt Strike自带DNS服务器，如果返回结果为0.0.0.0则配置正确，否则请查询相关DNS配置基本知识进行修正。某些域名解析供应商可能在功能实现上有限制，如果验证始终不成功，读者可以用dig命令尝试发现问题，甚至切换服务商。



## 生成投放artifact并加载

Cobalt Strike提供很多artifact生成方式，一般教程都会使用简单的exe进行说明，笔者日常更喜欢使用PowerShell，没有文件落地的好处显而易见。实际操作也并不复杂，参考如下概述。

使用菜单Attacks -&gt; Web Drive-by -&gt; Scripted Web Delivery

[![](https://p2.ssl.qhimg.com/t01632421e70b68c57f.png)](https://p2.ssl.qhimg.com/t01632421e70b68c57f.png)

现在服务器dnsch路径下已经挂好了用于投放的artifact，让我们去看一眼长什么样子。

[![](https://p3.ssl.qhimg.com/t012d3e062ed40919bc.png)](https://p3.ssl.qhimg.com/t012d3e062ed40919bc.png)

读者马上可以发挥想象，灵活创造更多的场景，在不同的地方保存和发布artifact，并不局限于Cobalt Strike所提供的方式。

随后弹出可供利用的PowerShell命令，拷贝保存。

[![](https://p2.ssl.qhimg.com/t01c8a164dc69b035c8.png)](https://p2.ssl.qhimg.com/t01c8a164dc69b035c8.png)



打开攻击目标Windows 7虚拟机，运行PowerShell，输入此命令并回车。

[![](https://p0.ssl.qhimg.com/t0160ca1f36a930e7de.png)](https://p0.ssl.qhimg.com/t0160ca1f36a930e7de.png)

任务完成，有效载荷已被植入。Artifact的生成与加载有很多技巧，这里只演示主要流程步骤，感兴趣的读者可以自行尝试各种高级方法。



## 远程控制

此时，在Cobalt Strike管理界面中，可以看到我们刚刚植入artifact的目标系统，已经向服务器报告过状态，并自动下载运行所需的payload。

[![](https://p1.ssl.qhimg.com/t01a634e8e3f1f94482.png)](https://p1.ssl.qhimg.com/t01a634e8e3f1f94482.png)

右键点击此台终端，选择Interact，我们可以使用命令行尝试远程控制，例如截屏、查阅进程列表、下载文件等。

[![](https://p3.ssl.qhimg.com/t01a8fb257d97280923.png)](https://p3.ssl.qhimg.com/t01a8fb257d97280923.png)

我们还可以利用mode命令随时改变数据传输通道，例如mode dns使用A记录传输，mode dns6使用AAAA记录，mode http显而易见使用http通道等等。Cobalt Strike的图形化界面菜单也很完善，常见的远控操作任务都可以点几下鼠标完成。

[![](https://p3.ssl.qhimg.com/t0126811339ed6f661f.png)](https://p3.ssl.qhimg.com/t0126811339ed6f661f.png)

读者不妨多尝试一些命令操作。

[![](https://p3.ssl.qhimg.com/t01fd64ff7dd4c3071d.png)](https://p3.ssl.qhimg.com/t01fd64ff7dd4c3071d.png)

远程截屏。

[![](https://p5.ssl.qhimg.com/t015221b3ab7f5b1ce7.png)](https://p5.ssl.qhimg.com/t015221b3ab7f5b1ce7.png)

使用download命令远程下载文件。

有一定基本软件能力的内部恶意员工，按照网上流传的入门教程操作，购买云服务器，几天内便可轻易快捷搭建基础设施，在办公电脑上甚至无需安装软件，就能利用DNS隐蔽隧道长期盗取关键数据，无法被传统安全产品检测，潜在危害巨大，是安全团队必需重视的风险。





## 进阶

有余力的读者可尝试一些高级DNS隐蔽隧道架设技巧。

在进行红队渗透评估时, 许多因素都影响进攻的成败。其中非常重要的因素是，尽力保持C2基础架构的隐藏性，让蓝队难以发现。如果对手发现并阻止了您的C2，即使不会立刻结束战役，至少它会减慢你的速度, 而你重新架设基础设施，浪费大量时间精力。使用DNS是一个办法以隐藏从端点到C2的通信，但如果蓝队能够进行递归DNS查找到Team Server，就会很麻烦。我们可以阻止蓝队进行这些反向查找，或至少建立一些障碍，使用主机重定向进一步隐藏流量。

[![](https://p1.ssl.qhimg.com/t017f5c1c4cc03375c8.jpg)](https://p1.ssl.qhimg.com/t017f5c1c4cc03375c8.jpg)

参考架构如上图所示，感兴趣的进阶读者可以尝试。本篇因为是入门教程，笔者就不赘述了。

只想学习如何使用Cobalt Strike利用DNS隧道外传数据的读者到这里已经达到基本目标，只需翻看官方手册便能顺利操作。接下来，对其背后具体通讯机制感兴趣的读者，可以在Windows虚拟机上安装Wireshark软件，捕获网络流量数据包，进而让我们一起做个简单分析。



## DNS隧道机制

DNS隐蔽隧道基于互联网不可或缺的DNS基础协议，天然具备穿透性强的优势，是恶意团伙穿透安全防护的一把利器。让我们先用一张Cobalt Strike官方示意图理解其通讯框架。

[![](https://p0.ssl.qhimg.com/t019a7b724406fe6a68.jpg)](https://p0.ssl.qhimg.com/t019a7b724406fe6a68.jpg)

被控端和控制端间采取DNS请求和应答机制，即由被控端主动发送DNS请求实现操作输出数据的回传、控制端回复DNS应答实现控制命令的下发。

**木马定期询问服务器**

[![](https://p2.ssl.qhimg.com/t013d8d6f8d8268ca32.jpg)](https://p2.ssl.qhimg.com/t013d8d6f8d8268ca32.jpg)

缺省设置每60秒按格式 [Session ID].dnsch.cirrus.[domain] 发送A记录解析请求，向C2服务器报告上线。

**利用TXT字段从服务器下载模块**

[![](https://p1.ssl.qhimg.com/t01971661a93339d360.png)](https://p1.ssl.qhimg.com/t01971661a93339d360.png)

我们随便选取一条记录，观察TXT记录返回的结果。

[![](https://p1.ssl.qhimg.com/t0190fe0072655583f8.png)](https://p1.ssl.qhimg.com/t0190fe0072655583f8.png)

通常使用TXT类型的数据记录来携带下传数据，TXT记录主要用来保存域名的附加文本信息，为了方便传输一般应用BASE-64进行编码，每个字节编码6个比特的原始数据。

**使用A记录查询向上传数据**

[![](https://p5.ssl.qhimg.com/t01786e03227a316641.png)](https://p5.ssl.qhimg.com/t01786e03227a316641.png)

在一个DNS 查询报文中最多可以携带242个字 符，每个字符可以有37个不同的取值。如果要使用DNS 隐蔽通道传递任意数据，则必须先对要传输的数据进行编码，使其满足DNS协议标准的要求。



## 使用DLP检测通过DNS隧道盗取数据行为

DNS隐蔽隧道检测是识别未知威胁必不可少的关键技术能力。超过90%外部入侵和内部威胁的目标最终就是盗取数据资产。因此，监控数据外泄渠道是安全对抗中十分重要的环节。

由于DNS隧道具有隐蔽性和多变性的复杂特征，传统DLP产品无法检测。实际场景中，加入域名生成算法DGA和改变数据外发编码等技术，大大增加了自动辨认的复杂性，造成基于特征匹配规则的安全产品无法准确识别。即使破解某一特定木马的DNS通讯模式，对未来出现的新格式无效。对于开源软件来说，改变网络通信特征轻而易举，特征匹配技术显然应对不了层出不穷的变种。

合法软件也使用DNS隧道，如果不加处理，则误报数量巨大难以接受。

[![](https://p3.ssl.qhimg.com/t01b22d8cb28f603dd9.png)](https://p3.ssl.qhimg.com/t01b22d8cb28f603dd9.png)有些技术文章提出按照请求量、长子域名统计进行检测，但频繁请求同一域中大量子域名的情况在实际环境中较为常见，极易产生误报，同时又容易忽略低频率低带宽的通道，造成漏报。若使用特殊资源记录类型统计，检测 DNS 隐蔽通道常用的 TXT 和 NULL 资源记录，iodine等使用A记录请求即会使此方法失效。即便采用字符频率统计算法，用于训练的合法流量产自Alexa 排名前百万网站，仅代表Web域名特征，与实际DNS流量特性差异较大，效果并不理想。

[![](https://p2.ssl.qhimg.com/t01178d6a958b18cf0d.png)](https://p2.ssl.qhimg.com/t01178d6a958b18cf0d.png)

思睿嘉得DLP产品应用机器学习算法分析终端等实体的网络流量行为，能准确检测出DNS隐蔽隧道，包括Cobalt Strike所使用的TXT记录等下载payload、A记录上传数据至C&amp;C服务器等手段。检测结果如下图所示。

[![](https://p4.ssl.qhimg.com/t01889491cb68756d45.png)](https://p4.ssl.qhimg.com/t01889491cb68756d45.png)

[![](https://p0.ssl.qhimg.com/t016e4e81b19ef988b4.png)](https://p0.ssl.qhimg.com/t016e4e81b19ef988b4.png)

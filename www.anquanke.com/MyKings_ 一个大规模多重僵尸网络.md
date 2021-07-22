> 原文链接: https://www.anquanke.com//post/id/96024 


# MyKings: 一个大规模多重僵尸网络


                                阅读量   
                                **173699**
                            
                        |
                        
                                                                                    



## 概要

MyKings 是一个由多个子僵尸网络构成的多重僵尸网络，2017 年 4 月底以来，该僵尸网络一直积极地扫描互联网上 1433 及其他多个端口，并在渗透进入受害者主机后传播包括 DDoS、Proxy、RAT、Miner 在内的多种不同用途的恶意代码。我们将其命名为 MyKings，原因之一来自该僵尸网络的一个主控域名 *.mykings[.]pw。

MyKings 并不是一个新的僵尸网络，在我们之前有若干对该僵尸网络组件的分析（详见 &lt;友商披露情况&gt; 一节），但在本次批露之前，各家分析都没有形成完整的拼图，也未见有效行动遏制该僵尸网络的扩散。

2017 年 5 月 23 日，我们第一次联系到新浪安全团队，并随后采取了多轮联合行动。新浪安全团队关闭了 MyKings 的上联 URL，并向我们提供了相关的访问日志。联合行动有效遏制了该僵尸网络的扩散，也希望能为后续其他联合行动扫清障碍。被关闭的这些上联 URL 如下：

```
hxxp://blog.sina.com.cn/s/blog_16****tv.html --&gt; new, blog post title: down  
hxxp://blog.sina.com.cn/s/blog_16****s0.html --&gt; new, blog post title: xmrok  
hxxp://blog.sina.com.cn/s/blog_16****rz.html --&gt; new, blog post title: xmr64  
hxxp://blog.sina.com.cn/s/blog_16*****w.html  
hxxp://blog.sina.com.cn/s/blog_16*****x.html  
hxxp://blog.sina.com.cn/s/blog_16*****4.html  
hxxp://blog.sina.com.cn/s/blog_16*****v.html  
hxxp://blog.sina.com.cn/s/blog_16*****u.html  
hxxp://blog.sina.com.cn/s/blog_16*****2.html
```

Mykings 本身模块化，构成很复杂, 本 Blog 是个概述，具体技术分析的内容见文末的 2 份 PDF 文档。



## MyKings 的感染范围和流行程度

统计 2017 年 5 月底前述被关闭的上联 URL 的访问来源 IP 数可知，独立来源 IP 总数 1,183,911 个，分布在遍布全球 198 个国家和地区。其中来源 IP 超过 100,000 的国家和地区有四个，分别是俄罗斯、印度、巴西和中国。

[![](https://p0.ssl.qhimg.com/t0132c33127a4d30b0a.png)](https://p0.ssl.qhimg.com/t0132c33127a4d30b0a.png)

[![](https://p1.ssl.qhimg.com/t011546bdc00a22f637.png)](https://p1.ssl.qhimg.com/t011546bdc00a22f637.png)

另外，在域名流行程度方面，最为流行的域名是 [up.f4321y.com](http://up.f4321y.com/) ：
- 该域名DNS被请求频率超过 2.5m/每日
- 该域名流行程度排行，历史最高 79753 名，目前稳定在8万～9万之间。
[![](https://p1.ssl.qhimg.com/t01adea6ac8040fc615.png)](https://p1.ssl.qhimg.com/t01adea6ac8040fc615.png)



## MyKings的组成

MyKings 是一组多个子僵尸网络的混合体，其简要结构如下图所示。

[![](https://p1.ssl.qhimg.com/t0166bcabe66702b298.png)](https://p1.ssl.qhimg.com/t0166bcabe66702b298.png)

Mykings 详细的构建过程与结构图如下所示：<br>[![](https://p4.ssl.qhimg.com/t016216c140681a5b96.png)](https://p4.ssl.qhimg.com/t016216c140681a5b96.png)

如上两图：
- 攻击者使用 Scanner(msinfo.exe) 扫描渗透进入受害者主机后，会自动尝试下载恶意代码。下载 URL 中的IP 部分被编码在受控的 Blog 页面中；
- Blog 页面中编码的 IP 地址是指向 Dropper(ups.rar) 的，这个配置项可以由攻击者在云端动态调整；部分 Blog 页面已经被前述联合行动关闭；
- Dropper 服务器上提供了恶意代码和对应的启动脚本的下载，这些内容同样可以由攻击者在云端动态调整；
- 我们观察到所下载的恶意代码有 Mirai, Proxy，RAT 和 Miner。
明确上述结构以后，使得我们可以将整个 MyKings 划分为多个子僵尸网络，并逐一标记各子僵尸网络的特征如下表：

[![](https://p0.ssl.qhimg.com/t01a9bba2e44ae7b5d9.png)](https://p0.ssl.qhimg.com/t01a9bba2e44ae7b5d9.png)

各子僵尸网络相互之间的构建关系如下表所示：

[![](https://p0.ssl.qhimg.com/t01fe2ed8326a980409.png)](https://p0.ssl.qhimg.com/t01fe2ed8326a980409.png)

从上述两个表中我们可以得出以下结论：
- botnet.-1/1/2/3/4 各自拥有独立的上联控制端，仅在构建过程中需要 botnet.0 支撑，构建完成后的运营阶段可以各自独立、不再相互依赖；
- botnet.0 支撑了多数其他子僵尸网络的构建过程。再考虑到我们在 botnet.0 的所有代码中没有看到其他任何恶意行为，我们倾向认为 **botnet.0 是一个专注做恶意代码推广的网络** 。
- botnet.1.proxy 的推广者不是 botnet.0，而是 botnet.-1，这是个例外。不过，上述推广行为仅在早期持续了很少一段时间，主要的恶意代码推广仍然由 botnet.0 完成。


## MyKings.botnet.0.spreader

botnet.0 是居于核心地位的一个僵尸网络，除了传播其他僵尸网络以外，该僵尸网络并没有其他恶意行为，聚焦在扫描资源建设和建立后续其他僵尸网络上。该僵尸网络有以下特点：
- 服务器基础设施规模庞大
- 积极改进感染代码和能力
- 向后继僵尸网络的投入提供了定义良好的编程接口
### botnet.0 的基础设施能力

botnet.0 拥有在几个小时动员 2400 个主机IP地址发起扫描的能力。如果我们假定每个主机 IP 地址需要 30<br>
元人民币（5美元），这就意味着botnet.0一次性投入了超过7万元人民币（12,000美元）。

基于如此强大的服务器基础设施，当前 botnet.0 贡献了整个互联网范围内 1433 端口扫描的主要部分。而全部 1433 端口上的扫描，根据我们的 scanmon系统(scan.netlab.360.com)显示的数据，高峰时期在 30~40m/d，目前稳定在 1.5m/d，与 23 端口（Mirai / Hajime）在伯仲之间。

前面提到一次性动员的 2400+ 个主机IP地址包括：
- 123.207.0.0/16 1150个
- 122.114.0.0/16 1255个
我们检测到上述主机集中发起扫描的时间在 2017.04.25 08:00:00 附近，当时在 [scan.netlab.360.com](http://scan.netlab.360.com/) 上能看到的 1433 端口的扫描情况如下。

[![](https://p0.ssl.qhimg.com/t018e1b49bf4c604708.png)](https://p0.ssl.qhimg.com/t018e1b49bf4c604708.png)

可以观察到当天上午8：00开始，1433端口上的扫描有了一个巨大的暴增。暴增前每日扫描事件约为5m/d，之后突增到30～40m/d。

观察这些活跃IP在C类段（/24）中的排名，前100的C类段中有99个来自前述两个B类段。考虑到这些IP地址段行为规律一致、时间窗口集中，我们将这些IP地址归入 MyKings 的资源池。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01325c89ed45d67bbc.png)

### botnet.0 的扫描和渗透能力

botnet.0 的扫描行为是由于其 msinfo.exe 进程发起的。该进程会拉取云端的 wpd.dat 配置文件，配合云端机制发起扫描，并且随着版本更迭不断改进自身扫描能力。
<li>扫描的端口和服务如下：
<ul>
- 1433 MSSQL
- 3306 MySQL
- 135 WMI
- 22 SSH
- 445 IPC
- 23 Telnet, mirai 僵尸网络
- 80 Web, CCTV设备
- 3389 RDP, Windows远程桌面- 早期版本中， msinfo.exe 用来扫描的目标 IP 只有两种：从云端配置文件 **wpd.dat** 获取、在本地根据外网出口 IP 随机生成；
- 最新样本中，增加了一种更复杂的本地随机生成算法，并且会避开一批保留地址段。- 早期版本中，支持 **TCP Connect** 和 **TCP SYN** 两种扫描方式，分别对应木马中实现的两个扫描模块；
- 早期版本的 msinfo.exe 中，两种扫描方式都是自己编写的，其中 **TCP Connect** 模块用到了The Ultimate TCP/IP 函数库中的 CUT_WSClient 类，而 **TCP SYN** 扫描模块则用到了 RAW Socket 相关的 DLL 文件并自己手动构造数据包；
- 最新样本中，在 **TCP SYN** 模块集成了知名全网端口扫描器 **Masscan** ，并且把目标 IP 配置成 `0.0.0.0/0` ，发起对全网的高速扫描。- 弱口令字典比较丰富，近百条是针对 Telnet 和 MSSQL Server；
- 获得服务权限后，进行进一步攻击入侵的 Palyload 也很强大，其中针对 MSSQL Server 进行注入利用的 SQL 语句格式化后有近千行。
### botnet.0 提供的后继僵尸网络接入界面

botnet.0 向后继僵尸网络提供的接入界面简明清晰，以至于从后继其他僵尸网络的角度来看，只需要按照接入界面要求配置安装包下载地址，以及安装包被下载后需要执行的脚本，安装包就会被下载执行。至于扫描和投入阶段的各种技术细节，可以交由 botnet.0 处理，自己完全不用关注。

上述接入界面包括：
- 灵活的云端配置文件：botnet.0.spreader 的核心木马 msinfo.exe 用到的云端配置文件 **wpd.dat** ，是一个加密的 XML 文档，其中指定了暴破 Telnet 成功后用到来下载 Mirai 样本的 C2 地址、需要扫描的网络服务端口、暴破各个端口所需的口令、入侵各个网络服务时执行的部分命令以及需要扫描的目标 IP 范围等配置。这些配置都可以根据后继僵尸网络的要求灵活更改。
- 模块化编程架构的 msinfo.exe : 主要是其 Crack 模块中通过继承一个基类 `Task_Crack` ，实现其中定义好的一组连接、暴破、执行命令等功能的函数接口即可定义一个 `Task_Crack_XXX` 子类，继而实现针对一个新的网络服务的攻击模块。Crack 模块与 **wpd.dat** 配置文件中定义的待扫描网络服务端口相对应，可以灵活更改针对不同网络服务的 Crack 功能。
- 其他辅助云端配置文件：msinfo.exe 与 botnet.0.spreader 用到的另外一个辅助木马 **ups.exe** ，会涉及其它云端配置文件，如 update.txt、ver.txt、my1.html、test.html、kill.html、clr.txt 等。这些也都可以灵活配置，方便攻击者控制在下一阶段需要下载什么样本、执行什么样的命令。


## 被推广的其他子僵尸网络

botnet.0 推广的其他僵尸网络包括：
- botnet.-1.mirai
- botnet.1.proxy
- botnet.2.rat
- botnet.3.miner
- botnet.4.rat
我们使用序号来标记首次发现的顺序、后缀标识给子僵尸网络的用途。

### botnet.-1.mirai

[cnc.f321y.com](http://cnc.f321y.com/) (123.51.208.155:23) 是一个 mirai 僵尸网络，它与 MyKings 的同源关系在卡巴斯基的早期文章中已经论证。

我们追溯到该C2发出的第一条攻击指令，是在2016-12-20发出的。

[![](https://p0.ssl.qhimg.com/t0121d6e1a60e13709e.png)](https://p0.ssl.qhimg.com/t0121d6e1a60e13709e.png)
- 2016-12-20 20:36 123.51.208.155:23|http_flood|118.193.139.184:54321
值得一提的是指令中受害者IP地址118.193.139.184 上，曾经有若干 C2 域名同属 MyKings 控制：
- 2016-04-01 15:55:56 2016-12-27 19:14:42 [pc.kill1234.com](http://pc.kill1234.com/) 118.193.139.184
- 2016-04-24 13:07:50 2016-12-27 19:02:22 [xq.kill1234.com](http://xq.kill1234.com/) 118.193.139.184
### botnet.1.proxy

botnet.1.proxy 是一个代理网络。这个网络不是由botnet.0.spreader直接创建，而是通过 botnet.-1.mirai 间接建立的。我们观察到以上建立过程发生在 2017.05.05-2017.05.17 之间

这个建立关系可以从以下样本之间的关系示意：

[![](https://p2.ssl.qhimg.com/t0182416ba17370aade.png)](https://p2.ssl.qhimg.com/t0182416ba17370aade.png)
- botnet.0.spreader 在投递一组特殊的 mirai 样本，建立botnet.-1.mirai
- botnet.-1.mirai 除了运行mirai自身的行为，还会下载得到 do.arm 系列样本
- do.arm 系列样本运行起来以后，会在本机建立socks proxy，并将所生成的随机密码发回给 211.23.167.180:9999
- 至此，以 211.23.167.180:9999 为核心的 botnet.2.proxy 就建立起来了。
为了确认上述proxy 网络会被利用，我们模拟了一个 bot 向 botnet.2.proxy C2 提供了一个密码。之后，botnet.2.proxy 向我们模拟的 bot 发出测试请求，要求利用 proxy 获取[www.baidu.com](http://www.baidu.com/) 网页。

[![](https://p4.ssl.qhimg.com/t019d16907466a3970a.png)](https://p4.ssl.qhimg.com/t019d16907466a3970a.png)

图中显示，botnet.2.proxy 执行的动作包括：
- 提供了用户名： 固定为admin
- 提供了口令：???????? 。这个口令是我们之前随机生成、并提供给 botnet.2.proxy 的。这里口令做了掩码处理，以减少我们工作IP的暴露风险
<li>要求访问 [http://www.baidu.com](http://www.baidu.com/)
</li>
- 在得到了回应的页面后， botnet.2.proxy 沉寂不再与我们控制的bot联系。
### botnet.2.rat 一个RAT僵尸网络

botnet.2.rat 在 Cyphort 的文档中已经批露，概要信息如下：
- 是由 botnet.0.spreader 直接建立的
- 投递样本 sha256sum: e6fc79a24d40aea81afdc7886a05f008385661a518422b22873d34496c3fb36b
<li>样本中包含C2 `pc.5b6b7b.info`
</li>
上述情况与我们的观察一致。

### botnet.3.miner 一个挖矿网络

我们观察到的botbet.3.miner 的特征包括：
- MinerPool：pool.minexmr.com:5555
<li>WalletID：
<ol>
<li>47Tscy1QuJn1fxHiBRjWFtgHmvqkW71YZCQL33LeunfH4rsGEHx5UGTPdfXNJtMMATMz8bmaykGVuDFGWP3KyufBSdzxBb2 –&gt; Total Paid: **2000+ xmr**
</li>
<li>45bbP2muiJHD8Fd5tZyPAfC2RsajyEcsRVVMZ7Tm5qJjdTMprexz6yQ5DVQ1BbmjkMYm9nMid2QSbiGLvvfau7At5V18FzQ –&gt; Total Paid: **6000+ xmr**
</li>
</ol>
</li>
- MinerPoolPass：x
在火绒实验室的文档里提及了挖矿僵尸网络，但是未给出特征细节，无法判定是否 botnet.0 仅推广了一个挖矿网络。

### botnet.4.rat 另一个RAT僵尸网络

botnet.4.rat 没有被其他安全厂商批露过。概要信息如下：
<li>下载链接：[http://104.37.245.82:8888/nb.dat](http://104.37.245.82:8888/nb.dat)
</li>
<li>样本中包含C2 `nb.ruisgood.ru`
</li>


## 近况

2018.1.17 开始，针对 1433 端口的扫描流量有明显的下降趋势，从我们对此 Botnet 的跟踪来看，此前支撑该 Botnet 的主要 C2 之一 **67.229.144.218** 停止服务。随后，2018.1.23 凌晨我们发现一个新的 C2 IP 上线： **67.229.99.82**。

另外，我们发现该团伙还在陆续更新 Botnet 后面其他的基础设施
- 新的样本下载 FTP 服务器 `ftp://ftp.ftp0118.info/`，口令 test:1433 ；
- 新的样本&amp;云端配置文件服务器 `down.down0116.info`；
- 新的新浪博客账号以及 3 篇新的新浪博客 Post。
在 2018.1.17~2018.1.21 这段时间，针对 1433 端口的扫描流量有一个明显的波谷，我们怀疑这与该团伙的基础设施变动有直接关系：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017163ec3c4c6c699b.png)



## 友商披露情况

已经有多家友商披露了 MyKings 的部分内容，按照我们观察到的报告时间顺序分别是
- GReAt, Kaspersky, [New(ish) Mirai Spreader Poses New Risks](https://securelist.com/newish-mirai-spreader-poses-new-risks/77621/), 2017.02
- Cyphort, [EternalBlue Exploit Actively Used to Deliver Remote Access Trojans](https://www.cyphort.com/eternalblue-exploit-actively-used-deliver-remote-access-trojans/), 2017.05
- 东巽科技：[Mirai木马“借道”新浪博客攻击windows服务器](https://www.77169.com/html/158742.html), 2017.07
- 火绒实验室：[彻底曝光黑客“隐匿者” 目前作最多的网络攻击团伙](http://www.freebuf.com/news/141644.html) 2017.07
- 360安全卫士：[悄然崛起的挖矿机僵尸网络：打服务器挖价值百万门罗币](https://www.anquanke.com/post/id/86751) 2017.9


## 特别致谢

在整个事件处置过程中，我们得到了来自新浪安全团队([sec.sina.com](http://sec.sina.com/).cn)的帮助，获得了原始访问数据，并联合关闭了该僵尸网络的上联通道，特此感谢。



## 详细技术分析

该 Botnet 相关的主要样本详细分析和具体样本相关的 IoC，可以查看以下两份详细技术分析文档：
- [Mykings-botnet.0 详细分析.pdf](http://blog.netlab.360.com/file/MyKings-botnet.0.pdf)
- [Mykings-botnet.o__ups.rar 详细分析.pdf](http://blog.netlab.360.com/file/MyKings-botnet.0__ups.pdf)


## IoC

### Botnet.0.spreader Configuration

hxxp://down.mykings.pw:8888/my1.html<br>
hxxp://down.mykings.pw:8888/ups.rar<br>
hxxp://down.mykings.pw:8888/item.dat<br>
hxxp://up.mykings.pw:8888/ver.txt<br>
hxxp://up.mykings.pw:8888/ups.rar<br>
hxxp://up.mykings.pw:8888/update.txt<br>
hxxp://up.mykings.pw:8888/wpdmd5.txt<br>
hxxp://up.mykings.pw:8888/wpd.dat<br>
hxxp://down.f4321y.com:8888/kill.html<br>
hxxp://down.f4321y.com:8888/test.html<br>
hxxp://down.f4321y.com:8888/ups.rar<br>
hxxp://down.f4321y.com<br>
hxxp://down.f4321y.com:8888/my1.html<br>
hxxp://js.f4321y.com:280/v.sct<br>
hxxp://up.f4321y.com<br>
hxxp://up.f4321y.com:8888/ver.txt<br>
hxxp://up.f4321y.com:8888/ups.rar<br>
hxxp://up.f4321y.com:8888/update.txt<br>
hxxp://up.f4321y.com:8888/wpdmd5.txt<br>
hxxp://up.f4321y.com:8888/wpd.dat<br>
hxxp://up.f4321y.com:8888/ups.rar<br>
hxxp://down.b591.com:8888/ups.exe<br>
hxxp://down.b591.com:8888/ups.rar<br>
hxxp://down.b591.com:8888/test.html<br>
hxxp://down.b591.com:8888/ups.rar<br>
hxxp://down.b591.com:8888/ups.exe<br>
hxxp://down.b591.com:8888/cab.rar<br>
hxxp://down.b591.com:8888/cacls.rar<br>
hxxp://down.b591.com:8888/kill.html<br>
hxxp://down2.b591.com:8888/ups.rar<br>
hxxp://down2.b591.com:8888/wpd.dat<br>
hxxp://down2.b591.com:8888/wpdmd5.txt<br>
hxxp://down2.b591.com:8888/ver.txt<br>
hxxp://dwon.kill1234.com:280/cao.exe<br>
hxxps://down2.b5w91.com:8443<br>
hxxp://down.mysking.info:8888/ok.txt<br>
hxxp://23.27.127.254:8888/close.bat<br>
hxxp://js.mykings.top:280/v.sct<br>
hxxp://js.mykings.top:280/helloworld.msi<br>
hxxp://wmi.mykings.top:8888/kill.html<br>
hxxp://wmi.mykings.top:8888/test.html<br>
hxxp://209.58.186.145:8888/close2.bat<br>
hxxp://67.229.144.218:8888/update.txt<br>
hxxp://67.229.144.218:8888/ps.jpg<br>
hxxp://67.229.144.218:8888/update.txt<br>
hxxp://67.229.144.218:8888/my1.html<br>
hxxp://67.229.144.218:8888/ver.txt<br>
hxxp://67.229.144.218:8888/test.dat<br>
hxxp://down.down0116.info –&gt; new<br>
hxxp://down.down0116.info/up.rar –&gt; new<br>
hxxp://down.down0116.info/down.txt –&gt; new<br>
fxp://ftp.ftp0118.info/a.exe –&gt; new

### botnet.-1.mirai

hxxp://100.43.155.171:280/mirai/

### botnet.1.proxy

hxxp://100.43.155.171:280/do/

### botnet.2.rat

hxxp://67.229.144.218:8888/test1.dat<br>
hxxp://47.88.216.68:8888/test.dat<br>
hxxp://47.52.0.176:8888/item.dat<br>
hxxp://118.190.50.141:8888/test.dat

### botnet.3.miner

hxxp://104.37.245.82:8888/32.rar<br>
fxp://fxp.oo000oo.me/s.rar<br>
hxxp://198.148.80.194:8888/0121.rar –&gt; new<br>
fxp://ftp.ftp0118.info/s.rar –&gt; new

### botnet.4.rat

hxxp://104.37.245.82:8888/nb.dat

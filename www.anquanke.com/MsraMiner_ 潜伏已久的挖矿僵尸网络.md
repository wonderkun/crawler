> 原文链接: https://www.anquanke.com//post/id/101392 


# MsraMiner: 潜伏已久的挖矿僵尸网络


                                阅读量   
                                **157461**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t013a9d7b5378fe3597.jpg)](https://p3.ssl.qhimg.com/t013a9d7b5378fe3597.jpg)

2017 年 11 月底，我们的 DNSMon 系统监测到几个疑似 DGA 产生的恶意域名活动有异常。经过我们深入分析，确认这背后是一个从 2017 年 5 月份运行至今的大型挖矿僵尸网络（Mining Botnet）。此僵尸网络最新的核心样本压缩包文件名为 MsraReportDataCache32.tlb ，我们将其命名为MsraMiner Botnet。

该僵尸网络的特征包括：
- 运行时间：2017 年 5 月份运行至今
<li>传播方式：
<ul>
- 利用 NSA 武器库来感染，通过 SMB 445 端口传播
- 蠕虫式传播：样本自带 Web Server提供自身恶意代码下载。样本扩散主要靠失陷主机之间的 Web Server 或 Socket 传输，同时提供了 C&amp;C 端获取样本作为后备机制；- 挖矿进程由 XMRig 编译而来；
- 矿池：利用自行注册的域名做掩护，CNAME到知名的 xmr.pool.minergate.com
- 矿池账号：是一批 Protonmail 的邮箱地址，Protonmail 是知名的匿名邮箱供应商
- 部分样本的挖矿行为，可以根据 C&amp;C 域名的解析结果来控制；- C&amp;C 域名形似 DGA 产生，非常随机，其实都硬编码在样本中；
- 主动抑制：C&amp;C 域名大部分时间会解析到保留地址段，会一定程度上抑制样本的传播和更新，历史上解析过的 C&amp;C IP 相关端口也会封闭，只会在短暂的时间内放开 C&amp;C 的正常服务功能。


## 规模与流行度

根据 DNSMon 统计，MsraMiner 相关 C&amp;C 域名中请求量最高的是 d.drawal.tk ，巅峰时期达到 6.7M/天，直 到现在，每天的请求量还在 2M 上下：

[![](https://p3.ssl.qhimg.com/t013f76eada62ad73c0.png)](https://p3.ssl.qhimg.com/t013f76eada62ad73c0.png)

其他 C&amp;C 域名的请求量均低一个数量级，但巅峰时期也能达到 500K+/天，趋势图如下：

[![](https://p3.ssl.qhimg.com/t0182dd34b5272c972f.png)](https://p3.ssl.qhimg.com/t0182dd34b5272c972f.png)

在我们 DNSMon 内部的域名流行度排行中， s.darwal.tk 历史最高流行度排名达到 165417 名。作为对比，我们此前发现的百万级僵尸节点的僵尸网络 MyKings 中，历史流行度排名最高的 C&amp;C 域名 up.f4321y.com 排名为 79753 。



## MsraMiner 的版本与迭代

据我们的追溯分析，MsraMiner 共有 2 个大版本，每个大版本中有 1 版明显的更新，我们将其版本命名为 v1.0/v1.1，v2.0/v2.1(当前最新)，各版本发生的期间和对应的C2 如下表所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016f06c0926d3fe59e.png)

MsraMiner v1.x 组成结构简单，小版本更新主要区别在于 C&amp;C：
- v1.0 起始于 2017.5 月份，2017.7 月份终止，仅靠一个主 C&amp;C 域名 eea.asf3r23.cf 支撑；
- v1.1 起始于 2017.7 月份，2017.11 月份开始逐渐消亡，主要靠 3 个 C&amp;C 域名 s.drawal.tk / d.drawal.tk / z.drawal.tk 支撑。
- v1.0 / v1.1 的更新，通过前面的域名请求趋势图可以清晰地看出来，在 2017.7 月初， eea.asf3r23.cf 的请求量骤降，而 *.darwal.tk 三个域名的请求量骤增。
MsraMiner v2.x 组成相对复杂，小版本更新主要区别在于部分文件名和服务名的变更，以及与 C&amp;C 服务器的交互。细节：
- v2.0 起始于 2017.11 月份，此时， *.darwal.tk 三个域名的请求量骤降，而 swt.njaavfxcgk3.club / rat.kziu0tpofwf.club 等 C&amp;C 域名的请求量骤增；
- v2.1 起始于 2017.12 月底，此时 MsraMiner 上线了一批新的 C&amp;C 域名，并对样本做了小幅更新。
MsraMiner 这些版本相关的域名、样本、IP 等 IoC，在背后都有千丝万缕的联系，通过下图可以直观看出来（箭头所指为 IoC 关联的点）：

[![](https://p4.ssl.qhimg.com/t01233e531146f87ca2.png)](https://p4.ssl.qhimg.com/t01233e531146f87ca2.png)



## 挖矿

第一代 MsraMiner 挖矿行为相对简单，启动参数如下（其他配置则在 iolchxfz32.dat 文件中）：

```
‐o stratum+tcp://xmr.pool.minergate.com:45560‐u dashcoin@protonmail.com ‐t %d
```

第二代 MsraMiner 挖矿的矿池和账户就比较隐蔽。矿池地址和账户以及部分 C&amp;C 域名被硬编码在前一阶段样本 中，并由前一阶段样本保存到注册表中。下一阶段样本会读取注册表中的加密数据，解密之后作为启动矿机的参 数，其中解密出来的矿池域名和挖矿账户：

```
-o p1.mdfr6avyyle.online:45560 -u lqbpyceupn@protonmail.com
-o p3.mdfr6avyyle.online:45560 -u dkeofj3f1e@protonmail.com
-o p5.mdfr6avyyle.online:45560 -u jodkrofar4@protonmail.com

-o p1.qsd2xjpzfky.site:45560 -u odiqldkee2@protonmail.com
-o p3.qsd2xjpzfky.site:45560 -u wvsymvtjeg@protonmail.com
-o p5.qsd2xjpzfky.site:45560 -u dkw1kaxlep@protonmail.com

-o p1.vpccaydoaw.live:45560 -u xsdkedkoap@protonmail.com
-o p3.vpccaydoaw.live:45560 -u a9akdsddje@protonmail.com
-o p5.vpccaydoaw.live:45560 -u rofk4e9dda@protonmail.com
```

MsraMiner 启动矿机（XMRig），还会根据当前 CPU 配置自动调整 -t 参数，即线程数，调整策略如下：

[![](https://p4.ssl.qhimg.com/t010c9a08d7c06c0cea.png)](https://p4.ssl.qhimg.com/t010c9a08d7c06c0cea.png)

而上面那些矿池域名并非自建矿池，它们的 CNAME 都是 xmr.pool.minergate.com ，我们统计到的 CNAME 配置为 xmr.pool.minergate.com 的域名有：

```
p1.jdi1diejs.club  
p1.mdfr6avyyle.online  
p1.qsd2xjpzfky.site  
p1.vpccaydoaw.live  
p3.mdfr6avyyle.online  
p3.qsd2xjpzfky.site  
p3.vpccaydoaw.live  
p4.jdi1diejs.club  
p5.mdfr6avyyle.online  
p5.qsd2xjpzfky.site  
p5.vpccaydoaw.live
```



## V1.x 系列样本行为分析

### 文件构成

第一代 MsraMiner 涉及的原始样本文件如下（注明 zip 的，文件实为 ZIP 压缩包）

[![](https://p1.ssl.qhimg.com/t01bdd57077158c8cda.png)](https://p1.ssl.qhimg.com/t01bdd57077158c8cda.png)

其中的 Crypt 文件实为 NSA Toolkit Zip 压缩包，其解压后的文件列表如下：

[![](https://p4.ssl.qhimg.com/t01afd87f2b3a6d4335.png)](https://p4.ssl.qhimg.com/t01afd87f2b3a6d4335.png)

### 执行流程

第一代 MsraMiner 会利用上述文件完成感染，进而在失陷主机上启动矿机程序来挖矿，其感染的概要过程为（A 与 B 均为失陷主机）：

(A)svchost.exe–&gt;(A)spoolsv.exe–&gt;(payload to crack B)x86.dll/x64.dll–&gt;(B)svchost.exe

流程图如下（假设失陷主机 A 为攻击机，去感染 B 主机，系统均为 32bit，如无注明，均以 v1.1 的样本分析结果进行描述）：

[![](https://p2.ssl.qhimg.com/t0134e7936d8be3e6bf.png)](https://p2.ssl.qhimg.com/t0134e7936d8be3e6bf.png)

首先，A 中启动的 svchost.exe 程序，通过 schtasks.exe /create 命令注册系统服务，开机启动，从而驻留系统：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0127e85438a5640d8b.png)

A 中 svchost.exe 通过 HTTP POST 请求，向 hxxp://d.drawal.tk:443 发送程序运行日志 [*] Hello %d<br>
min…\n ，后续运行过程中还会频繁向该接口发送其他内容的程序运行日志。v1.0 版本中，承载此功能的C&amp;C 域名是 eea.asf3r23.cf ；<br>
A 中 svchost.exe 启动一个线程，从自身 BIN 资源中抽取矿机程序，启动挖矿；<br>
A 中 svchost.exe 启动一个线程，该线程启用了一个 Mongoose 框架实现的 Mini Web Server，端口为<br>
26571 ，该 Web Server 把本机的 dnsclientprovider_userdata.mof 文件对外提供下载，对方通过 HTTP<br>
GET 方式请求此资源，svchost32.exe 就会把该文件推送过去；如果对方通过其他 HTTP Post 访问该 Web 服务，则返回 HTTP 404；如果是其他 HTTP Method 访问该 Web 服务，则返回字符串 Hell World? ；

[![](https://p1.ssl.qhimg.com/t0116f54db9a579843a.png)](https://p1.ssl.qhimg.com/t0116f54db9a579843a.png)

A 中 svchost.exe 启动线程，每隔 900s 运行一次本地的 spoolsv.exe 程序，该程序会先释放自身 BIN 资源中的 Crypt （实为 NSA Toolkit zip 压缩包），将 Crypt 解压，并把其中的文件释放到 %win_dir%\IME\Crypt\ 目录中，然后启动 Crypt 目录中的相关工具程序，对同网段中其他机器（比如机器B）发起感染；

[![](https://p3.ssl.qhimg.com/t019288b61f59d933dd.png)](https://p3.ssl.qhimg.com/t019288b61f59d933dd.png)

A 中 spoolsv.exe 会启动 Crypt\spoolsv.exe 发起感染，如果成功感染机器 B，则会把 Crypt\x86.dll 作为Payload 去机器 B 上执行；<br>
A 中 svchost.exe 每隔 901.5s 左右向 z.drawal.tk:8080 发送一次本机详细配置信息，v1.0 版本中，承载此功能的 C&amp;C 域名为 eea.asf3r23.cf ；

B 中，x86.dll 文件做以下几件事：
- create mutex `{`5EC0AC33D-E23D-C8A2-A92C833`}` ；
- 检测本地是否存在 dnsclientprovider_userdata.mof ，若有，则删除；
<li>从 A 机器的 Mini Web Server 获取 dnsclientprovider_userdata.mof ，将其中的 iolchxfz32.dat / svchost32.exe / spoolsv32.exe 解压出来，放到 %win_dir%\IME\Crypt\ 中，并<br>
分别重命名为 settings7283.dat / svchost.exe / spoolsv.exe</li>
- 将 svchost.exe 通过 schtasks.exe /create 命令注册系统服务，并启动 svchost.exe；
- 至此，通过 (A)svchost.exe–&gt;(A)spoolsv.exe–&gt;(payload to crack B)x86.dll–&gt;(B)svchost.exe 的攻击链完成一轮感染。
[![](https://p2.ssl.qhimg.com/t01b420864f96787ee1.png)](https://p2.ssl.qhimg.com/t01b420864f96787ee1.png)

值的一提的是，svchost.exe 可以通过 s.drawal.tk 域名的解析情况来控制矿机的启动与终止（v1.0 不具有此功能）：
- 如果 s.drawal.tk 解析 IP 的 A 段数字为 1 或 3 ，则不启动矿机，0.3s 后重新检查解析结果；
- 如果 900s 之后 s.drawal.tk 的解析结果有变化，则终止矿机运行。


## V2.x 系列样本行为分析

### 文件构成

第二代 MsraMiner 涉及的原始样本文件如下（注明 zip 的，文件实为 ZIP 压缩包）：

[![](https://p2.ssl.qhimg.com/t012387559d98a278f3.png)](https://p2.ssl.qhimg.com/t012387559d98a278f3.png)

第二代 MsraMiner 会利用上述文件完成感染，进而在失陷主机上启动矿机程序来挖矿。其感染的概要过程为（A 与 B 均为失陷主机）：

(A)srv–&gt;(A)spoolsv.exe–&gt;(payload to crack B)x86.dll/x64.dll–&gt;(B)srv.exe

流程图如下（假设失陷主机 A 为攻击机，去感染 B 主机，系统均为 32bit，如无注明，均以 v2.1 的样本分析结果进行描述）：

[![](https://p4.ssl.qhimg.com/t01f0f20fb45e0d4b32.png)](https://p4.ssl.qhimg.com/t01f0f20fb45e0d4b32.png)
- A 中，srv 是个 DLL 文件，是 MsraMiner 驻留失陷主机的核心服务文件，在失陷主机上会被重命名为 tpmagentservice.dll 。srv 中的 ServiceCrtMain() 函数由 NSA 工具包的 Payload 启动：
- A 中， srv 的 Common 模块检查自身的启动命令，如果不是由 svchost.exe / rundll32.exe / regsvr32.exe 其中之一启动，则结束进程，以此实现一定的反调试功能；
- A 中，srv 的 Common 模块 在 C:\Windows\system32\ 目录下创建 NetTraceDiagnostics.ini 文件；
- A 中， srv 的 Common 模块会杀掉第一代、第二代 MsraMiner 的相关进程，停止旧服务（vmichapagentsrv ）、删除旧文件；
- A 中 srv 的 Common 模块读取注册表项 HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\ 下面 ServicesPixels 键的值，该处保存着变形 XOR 加密后的 C2 Domain、矿池域名和挖矿账号；
- A 中 srv 的 WebHost 模块在 26931 端口启动 Mini WebServer，对任何 HTTP 请求均以 HTTP 404 响应。
- v2.0 的 Mini WebServer 端口是 36215 ，且功能更复杂，既提供压缩包的下载（请求hxxp://[c2**domain]/NrsDataCache.tlb ），也提供注册表数据的下载（请求hxxp://[c2**domain]/d/msdownload/update/others/88ee176ce078def878ee.cab ）；
- v2.0 的 srv 文件 还会通过 Downloader 模块向 C2 请求最新的配置数据（C2 Domain、矿 池域名和挖矿账号）；
- v2.0 的 srv 文件，还会把当前进程的运行日志频繁发送给 hxxp://err.njaavfxcgk3.club:443 ； A 中 srv 的 Job 模块，会从 C:\Windows\system32\MsraReportDataCache32.tlb 中解压出 hash 文件（xmrig 矿机程序），重命名为 TrustedHostServices.exe （v2.0 会重命名为 SecUpdateHost.exe ），并用注册表中读取的配置作为启动参数，启动矿机（矿机的线程数量策略同 v1.x）；
- A 中 srv 主模块会启动一个线程，每隔 1s 向 hxxp://[c2**domain]:4433/uri**path 发送 POST 请求，其中 uri_path 为 5b8c1d | d0a01e | a4c80e 其中之一，疑似可以从 C2 上获取 MsraReportDataCache32.tlb 来更新本地样本；
<li>A 中 srv 的 Infection 模块从 C:\Windows\system32\MsraReportDataCache32.tlb 中解压出 spoolsv32 ，重命名为 spoolsv.exe 并启动，执行感染功能，spoolsv.exe 的具体功能如下：
<ul>
- 从 C:\Windows\system32\MsraReportDataCache32.tlb 中解压出 crypt(.zip)，crypt 是 NSA 工具包，从中取出攻击程序和配置文件，向局域网发起攻击，Payload 为 crypt 压缩包中的 86.dll / x64.dll；
- 入侵成功后，Paylod DLL 在失陷主机 B 那里开 57219 端口，然后从攻击机把MsraReportDataCache32.tlb 上传到失陷主机 B；
- 探测局域网主机 26931（Mongoose WebServer）端口，26931 端口由其他失陷主机的主控模块 srv 开 启；
- 与 C2 交互（功能未明，C2 已失效，以下 C2 仅为举例）：
```
hxxp://acs.njaavfxcgk3.club:4431/f79e53  
hxxp://acs.njaavfxcgk3.club:4433/5b8c1d  
hxxp://rer.njaavfxcgk3.club:4433/a4c80e  
hxxp://rer.njaavfxcgk3.club:4433/d0a01e  
‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐‐
hxxp://ccc.njaavfxcgk3.club:4431/f79e53  
hxxp://ccc.njaavfxcgk3.club:4433/5b8c1d  
hxxp://rer.njaavfxcgk3.club:4433/a4c80e  
hxxp://rer.njaavfxcgk3.club:4433/d0a01e  
```
<li>B 中 x86.dll 有以下主要行为：
<ul>
- 删除旧文件 MsraReportDataCache32.tlb/tpmagentservice.dll/NetTraceDiagnostics.ini ；
- 从 57219 端口接收 A 主机传过来的 MsraReportDataCache32.tlb ；
- 将自身携带的加密数据存储到注册表项 HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\ 下面 ServicesPixels 键中；
- 终止旧的主服务，从 MsraReportDataCache32.tlb 中解压出 srv 文件，重命名为tpmagentservice.dll ，并重新注册服务 tpmagentservice ，启动 tpmagentservice.dll 的ServiceCrtMain() 函数。 至此，第二代 MsraMiner 完成了从失陷主机 A 到失陷主机 B 的感染，并根据配置文件启动矿机程序进行挖矿
[![](https://p2.ssl.qhimg.com/t0181259a20d20d2406.png)](https://p2.ssl.qhimg.com/t0181259a20d20d2406.png)[![](https://p1.ssl.qhimg.com/t014bd2ae32533c1b1f.png)](https://p1.ssl.qhimg.com/t014bd2ae32533c1b1f.png)

## IoC 列表

## #

swt.njaavfxcgk3.club<br>
x1.sk0zda1rmzs.world<br>
x5.sk0zda1rmzs.world<br>
d1d1d1.ftbxedwakc.me<br>
x1x1x1.ftbxedwakc.me<br>
tar.kziu0tpofwf.club<br>
rer.njaavfxcgk3.club<br>
acs.njaavfxcgk3.club<br>
ccc.njaavfxcgk3.club<br>
cf.sk0zda1rmzs.world<br>
cm.sk0zda1rmzs.world<br>
cmcmcm.ftbxedwakc.me<br>
err.njaavfxcgk3.club<br>
rat.kziu0tpofwf.club<br>
p3.njaavfxcgk3.club<br>
s.drawal.tk<br>
d.drawal.tk<br>
z.drawal.tk<br>
eea.asf3r23.cf<br>
p3.qsd2xjpzfky.site<br>
p1.mdfr6avyyle.online<br>
p1.qsd2xjpzfky.site<br>
p5.qsd2xjpzfky.site<br>
p5.mdfr6avyyle.online<br>
p3.mdfr6avyyle.online<br>
p1.vpccaydoaw.live<br>
p5.vpccaydoaw.live<br>
p3.vpccaydoaw.live



## C2 ip asn

AS20473 Choopa, LLC 104.238.149.229<br>
AS20473 Choopa, LLC 107.191.61.152<br>
AS20473 Choopa, LLC 108.61.246.77<br>
AS20473 Choopa, LLC 108.61.247.93<br>
AS4837 CHINA UNICOM China169 Backbone 119.188.68.5<br>
AS20473 Choopa, LLC 207.246.100.220<br>
AS20473 Choopa, LLC 45.32.110.163<br>
AS20473 Choopa, LLC 45.32.121.95<br>
AS20473 Choopa, LLC 45.32.127.108<br>
AS20473 Choopa, LLC 45.32.48.160<br>
AS20473 Choopa, LLC 45.32.51.130<br>
AS20473 Choopa, LLC 45.63.127.197<br>
AS20473 Choopa, LLC 45.63.94.237<br>
AS20473 Choopa, LLC 45.76.103.25<br>
AS20473 Choopa, LLC 45.76.185.56<br>
AS20473 Choopa, LLC 45.76.188.118<br>
AS20473 Choopa, LLC 45.76.199.181<br>
AS20473 Choopa, LLC 45.76.48.72<br>
AS20473 Choopa, LLC 45.76.51.49<br>
AS20473 Choopa, LLC 45.76.55.4<br>
AS20473 Choopa, LLC 45.77.11.148<br>
AS20473 Choopa, LLC 45.77.14.227<br>
AS20473 Choopa, LLC 45.77.20.217<br>
AS20473 Choopa, LLC 45.77.22.234<br>
AS20473 Choopa, LLC 45.77.25.58<br>
AS20473 Choopa, LLC 45.77.29.88<br>
AS20473 Choopa, LLC 45.77.31.21



## 样本 md5

011d6ce51b7806dca26c300e8d26f9bb<br>
1e0022c02030f2b4353b583beffbade9<br>
3aba72d1f87f4372162972b6a45ed8cd<br>
593c0352bda3fee2e0d56d63601fa632<br>
61c49acb542f5fa5ea9f2efcd534d720<br>
6b6dd446403f10f43c33e83946eafa99<br>
74fc7442f54a49875cbd5c3d6398847a<br>
a937565fc52028949d8fca743c05b273<br>
a9ef70160121d3d6ca0692b3081498fd<br>
aa378f3f047acc8838ffd9fe4bd0025b<br>
c24315b0585b852110977dacafe6c8c1<br>
c284767a12c1670f30d3d1fe1cd8aedd<br>
045cb0ab19e900e07f148233762cdff6<br>
2bcd21c4ce8a1a2ff0769cd2aef2ff88<br>
ed0fe346f568d6dff3aaf0077c91df2a<br>
f7cd555799147d509e554b0e585aced0<br>
c899d12ceff6ded5a37335f44356caaf<br>
4b157f03f33cccb7b4182351a5126936<br>
33fe92ae1bb36e7a7b7b7342627bd31e<br>
49f7f7d75021e90761141c5fe76445a6<br>
d92cd7ddb81d2c4a17e1b329ef7a2f1d<br>
dca0d1e613f2ac48e231883870e5b3e9<br>
739ab9250f32e006208f1ff15cd0d772<br>
a8dfb2d7aee89a4b9ad194c7128954c6

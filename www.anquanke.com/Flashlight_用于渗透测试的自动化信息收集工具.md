> 原文链接: https://www.anquanke.com//post/id/83116 


# Flashlight：用于渗透测试的自动化信息收集工具


                                阅读量   
                                **91414**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://github.com/galkan/flashlight](https://github.com/galkan/flashlight)

译文仅供参考，具体内容表达以及含义原文为准

渗透测试人员在信息收集阶段花费了大量的时间。Flashlight(Fener)能够迅速对目标网络提供服务的网络端口进行扫描并收集信息。因此Flashlight可以作为渗透测试中可以使用的一个不错的选择。本文将对Flashlight做一个简单的介绍。

想要知道更多关于Flashlight的信息,可以使用“-h”或者“–help”选项来获取帮助信息。

[![](https://p2.ssl.qhimg.com/t01619b8f33e921958f.jpg)](https://p2.ssl.qhimg.com/t01619b8f33e921958f.jpg)

各个参数的用法如下:



```
-h,--help:显示关于使用Flashlight的相关信息
-p &lt;ProjectName&gt; 或者--project &lt; ProjectName&gt;:设置项目名称。这个选项可以用来保存不同工作区中的不同项目。
-s &lt;ScanType&gt; 或者 –scan_type &lt; ScanType &gt;:设置扫描类型。有四种扫描类型:Active Scan , Passive Scan, Screenshot Scan and Filtering。这些扫描类型会在后面详细解释。
-d &lt; DestinationNetwork&gt;, --destination &lt; DestinationNetwork &gt;:设置要扫描的目标网络或者IP。
-c &lt;FileName&gt;, --config &lt;FileName&gt;:指定配置文件。扫描会根据配置文件中的信息进行。
-u &lt;NetworkInterface&gt;, --interface &lt; NetworkInterface&gt;:指定在被动扫描(passive scan)时要使用的网络接口。
-f &lt;PcapFile&gt;, --pcap_file &lt; PcapFile &gt;:设置用于过滤的pcap文件。
-r &lt;RasterizeFile&gt;, --rasterize &lt; RasterizeFile&gt;:设置用于截屏扫描的JS文件。
-t &lt;ThreadNumber&gt;, --thread &lt;Threadnember&gt;:设置线程数。该参数仅适用于截屏扫描模式。
-o &lt;OutputDiectory&gt;, --output &lt; OutputDiectory &gt;:设置用于保存扫描结果的输出目录。扫描结果会保存在三个字目录中:Nmap扫描结果的nmap子目录,Pcap文件使用的pcap子目录,以及截屏扫描使用的screen子目录。扫描结果会保存在该参数指定的目录中。如果没有指定该参数,扫描结果会保存在Flashlight运行所在的目录中。
-a, --alive:它在进行实际的漏洞扫描前先进行ping扫描去发现存活的IP。适用于主动扫描。
-g &lt;DefaultGateway&gt;, --gateway &lt; DefaultGateway &gt;:设置网关IP地址。
-l &lt;LogFile&gt;, --log &lt; LogFile &gt;:指定保存扫描结果的日志文件。如果没有指定该参数,日志文件会保存在Flashlight运行所在的目录。
-k &lt;PassiveTimeout&gt;, --passive_timeout &lt;PassiveTimeout&gt;:设置超时时间。默认15秒。适用于被动扫描。
-m, --mim:用于执行MITM攻击。
-n, --nmap-optimize:用于优化nmap扫描
-v, --verbose:运行时显示详细输出信息
-V, --version:显示版本信息
```

安装

```
apt-get install nmap tshark tcpdump dsniff
```

为了轻松安装phantomjs,你可以从[https://bitbucket.org/ariya/phantomjs/downloads](https://bitbucket.org/ariya/phantomjs/downloads)下载解压后进行安装。

Flashlight可以执行三种基本扫描类型和一种分析类型。下面将详细介绍。

1) Passive Scan

被动扫描中,不会发送数据包。这种类型的扫描主要时监听网络并且分析数据包。

例如要使用Flashlight进行一次被动扫描,设置一个项目名称,如passive-pro-01。在下面的命令中,由eth0捕获的数据包会保存在“/root/Desktop/flashlight/output/passive-project-01/pcap”目录中,pcap文件和所有的日志文件会保存在“/root/Desktop/log”目录中。

```
./flashlight.py -s passive -p passive-project-02 -i eth0 -g 192.168.74.2 -m -k 50 -v
```

[![](https://p1.ssl.qhimg.com/t01ac89673a72226ae1.jpg)](https://p1.ssl.qhimg.com/t01ac89673a72226ae1.jpg)

通过分析捕获到的pcap文件中的HTTP流量,我们可以看到

[![](https://p5.ssl.qhimg.com/t01c74d01b8ac72b9a6.jpg)](https://p5.ssl.qhimg.com/t01c74d01b8ac72b9a6.jpg)

对基础身份认证消息进行解码,我们将得到用于访问web服务器的凭据。

[![](https://p3.ssl.qhimg.com/t01c5ae9480792facdc.jpg)](https://p3.ssl.qhimg.com/t01c5ae9480792facdc.jpg)

被动扫描的所有参数类似于这样:

```
./flashlight.py -s passive -p passive-pro-03 -i eth0 -g 192.168.74.2 -m -k 50 -o /root/Desktop/flashlight_passive_full -l /root/Desktop/log -v
```

 2) Active Scan

在主动扫描中,NMAP脚本通过读取配置文件进行扫描。在Flashlight的config目录中有一个样例配置文件flashlight.yaml。

[![](https://p0.ssl.qhimg.com/t01ba384df33ea30114.jpg)](https://p0.ssl.qhimg.com/t01ba384df33ea30114.jpg)

根据"flashlight.yaml" 配置文件,执行扫描时会对TCP的“21, 22, 23, 25, 80, 443, 445, 3128, 8080”端口,UDP的"53, 161"端口进行扫描,并且会使用"http-enum" 脚本。

注意:在主动扫描中“screen_ports”选项是无用的。此选项只适用于screenshot扫描。

“-a”选项通过发送ICMP数据包探测存活主机。除此之外,还可以使用“-t”参数增加线程数来提高扫描速度。

```
./flashlight.py -p active-project -s active -d 192.168.74.0/24 –t 30 -a -v
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f166c5f032ab3cc5.jpg)

通过运行此命令,输出文件有三种不同格式 (普通, XML 和Grepable)结合四种不同扫描类型(操作系统扫描,ping扫描,端口扫描和脚本扫描)

[![](https://p2.ssl.qhimg.com/t0171dad4e47a7c117d.jpg)](https://p2.ssl.qhimg.com/t0171dad4e47a7c117d.jpg)

Flashlight内部可能使用了类似这样的命令进行扫描:

操作系统扫描:/usr/bin/nmap -n -Pn -O -T5 -iL /tmp/"IPListFile" -oA /root/Desktop/flashlight/output/active-project/nmap/OsScan-"Date"

Ping扫描:/usr/bin/nmap -n -sn -T5 -iL /tmp/"IPListFile" -oA /root/Desktop/flashlight/output/active-project/nmap/PingScan-"Date"

端口扫描:/usr/bin/nmap -n -Pn -T5 –open -iL /tmp/"IPListFile" -sS -p T:21,22,23,25,80,443,445,3128,8080,U:53,161 -sU -oA /root/Desktop/flashlight/output/active-project/nmap/PortScan-"Date"

脚本扫描:/usr/bin/nmap -n -Pn -T5 -iL /tmp/"IPListFile" -sS -p T:21,22,23,25,80,443,445,3128,8080,U:53,161 -sU –script=default,http-enum -oA /root/Desktop/flashlight/output/active-project/nmap/ScriptScan-"Date"

[![](https://p5.ssl.qhimg.com/t01e46b38f0b15498a6.jpg)](https://p5.ssl.qhimg.com/t01e46b38f0b15498a6.jpg)

如果想运行一个高效优化的主动扫描,可以使用“-n”参数,类似于这样:

```
./flashlight.py -p active-project -s active -d 192.168.74.0/24 -n -a –v
```

[![](https://p2.ssl.qhimg.com/t015243082692c582a6.jpg)](https://p2.ssl.qhimg.com/t015243082692c582a6.jpg)

“-n”参数增加了额外的nmap选项,如下所示:

```
… -min-hostgroup 64 -min-parallelism 64 -host-timeout=300m -max-rtt-timeout=600ms -initial-rtt-timeout=300ms -min-rtt-timeout=300ms -max-retries=2 -min-rate=150 …
```

3) Screen Scan

截屏扫描使用在配置文件(flashlight.yaml)中得到的指令对网站应用进行扫描截屏。文件中“screen_ports: – 80, 443, 8080, 8443 ”,简单的扫描命令类似于这样:

```
./flashlight.py -p project -s screen -d 192.168.74.0/24 -r /usr/local/rasterize.js -t 10 -v
```

[![](https://p0.ssl.qhimg.com/t01fb84f4321ec006ab.jpg)](https://p0.ssl.qhimg.com/t01fb84f4321ec006ab.jpg)

例如,通过运行这条命令检测到三个网站应用程序。这些网站的截图会保存在“screen”子目录中。这些屏幕截图可以用于离线分析。

[![](https://p0.ssl.qhimg.com/t010a3db742fbe824dc.jpg)](https://p0.ssl.qhimg.com/t010a3db742fbe824dc.jpg)

 4) Filtering

Filtering选项主要用于分析pcap文件。举例如下:

```
./flashlight.py -p filter-project -s filter -f /root/Desktop/flashlight/output/passive-project-02/pcap/20150815072543.pcap -v
```

通过运行这条命令,我们可以看到一些文件被创建在了“filter”子目录中。

这个选项通过以下特点对pcap文件进行分析:

Windows主机

排名前10的DNS请求

> 原文链接: https://www.anquanke.com//post/id/87098 


# 【工具分享】moloch：网络流量回溯分析系统


                                阅读量   
                                **227785**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



**[![](https://p2.ssl.qhimg.com/t017b1f95a8b269a088.png)](https://p2.ssl.qhimg.com/t017b1f95a8b269a088.png)**

**<br>**

**0x01 故事背景**

某一天的早上，你怀着愉快的心情来到公司，开始美好的一天工作生活。有个业务后台的同事找到你说 昨天下班后有人反馈说访问他的业务后台有问题，他想分析网络层面的数据包看看，是否能看出什么问题。你微微一笑，作为一个资深网工，抓包这种小事，这不是正是花式秀tcpdump还是tshark的时候么？

突然又觉得那里不对…什么鬼？要抓昨天晚上的数据包，你突然想到的竟然是这货…

[![](https://p1.ssl.qhimg.com/t01072d493401adedb6.png)](https://p1.ssl.qhimg.com/t01072d493401adedb6.png)

既然没有这么逆天的技能的时光鸡小伙伴 那还是搭建一个流量回溯系统吧



**0x02 架构简述**

流量回溯系统首先要面临几个问题：数据包的存取和协议的分析，当数据量很大的时候检索的速度等…

刚开始的想法是使用tshark 设定数据包大小，让tshark在后台一直抓包。用了一下效果不忍直视。

后来又找了一些其它的解决方案比如: [Analyzing Network Packets with Wireshark, Elasticsearch, and Kibana](https://www.elastic.co/blog/analyzing-network-packets-with-wireshark-elasticsearch-and-kibana)之类的，效果都不是很好

直到有一天，老大介绍了一个系统：moloch。

数据的来源是交换机的镜像端口，moloch 系统主要涉及三个组件 Capture，elasticsearch 和 Viewer。

Capture 用来抓取流量会以pcap的格式存储到硬盘上面，还会存一份对应关系到es中，Viewer提供web界面。

**moloch简介**

Moloch是一款由 AOL [开源](https://github.com/aol/moloch)的，能够大规模的捕获IPv4数据包（PCAP）、索引和数据库系统

**环境搭建**

存储数据包对机器的性能要求，moloch 提供了评估页面。

[Moloch Estimators](http://molo.ch/#estimators)

硬件环境：我的测试环境是一台Dell Inc. PowerEdge R720/0T0WRN

**cpu : Intel(R) Xeon(R) CPU E5-2650 0 @ 2.00GHz**

**memory: 100G+**

**disk: 8T**

这是一台配置比较好的机器。所以我的Capture Machines和Elasticsearch Machines都放在一台上面，有条件的强烈推荐把这2个组件分离开来。

[![](https://p5.ssl.qhimg.com/t01dfb3d3bbfbb7357b.png)](https://p5.ssl.qhimg.com/t01dfb3d3bbfbb7357b.png)

根据官方的文档有2个事情注意一下：

**1 Moloch is no longer supported on 32 bit machines.**

moloch不支持32位系统。

**2 Our deployment is on Centos 6 with the elrepo 4.x kernel upgrade for packet performance increases.**

内核4.X 有助于抓包性能提升，我的系统环境 centos7 更新到最新的版本。

```
[root@moloch ~]# cat /etc/redhat-release CentOS Linux release 7.4.1708 (Core)
```

内核版本也更新到4.x。

```
[root@moloch ~]# uname -r4.13.7-1.el7.elrepo.x86_64
```

**moloch 安装**

先去官网下载一下安装包 [Downloads](http://molo.ch/#downloads)。

我选择是Nightly版本，可以体验新的特性 。

[![](https://p1.ssl.qhimg.com/t01ed5a278290fdcb19.png)](https://p1.ssl.qhimg.com/t01ed5a278290fdcb19.png)

moloch安装命令

```
rpm -ivh moloch-nightly.x86_64.rpm
```

**pfring 安装**

moloch的Capture，默认使用libpcap，后面我们会用pfring，提升抓包性能。



```
cd /etc/yum.repos.d/
wget http://packages.ntop.org/centos-stable/ntop.repo -O ntop.repo•wget http://packages.ntop.org/centos-stable/epel-7.repo -O epel.repo•yum erase zeromq3 (Do this once to make sure zeromq3 is not installed)
yum clean all
yum update
yum install pfring
```

**elasticsearch 安装配置**

es可以选择在配置moloch时候安装，也可以自己单独安装，我选择自己单独安装。

安装命令



```
rpm -ivh elasticsearch-5.6.2.rpm
# 优化es[root@moloch elasticsearch]# vim jvm.options# Xms represents the initial size of total heap space# Xmx represents the maximum size of total heap space-Xms32g-Xmx32g
[root@moloch elasticsearch]# vim elasticsearch.yml
#抓包经常会把硬盘用完，当硬盘使用空间到80% es 就开始报警 ，我直接把报警关掉的。
cluster.routing.allocation.disk.threshold_enabled: falsenetwork.host: 10.10.7.7
[root@moloch ~]# curl http://10.10.7.7:9200`{`  "name" : "E2BtdPC",  "cluster_name" : "elasticsearch",  "cluster_uuid" : "EiSTiNE-QGaTt9z0V8HPkw",  "version" : `{`    "number" : "5.6.2",    "build_hash" : "57e20f3",    "build_date" : "2017-09-23T13:16:45.703Z",    "build_snapshot" : false,    "lucene_version" : "6.6.1"`}`,  "tagline" : "You Know, for Search"`}`
```

<br>

**0x03 配置优化**

**配置moloch**



```
# 开始使用脚本配置moloch[root@moloch db]# /data/moloch-nightly/bin/ConfigureFound interfaces: bond0;em1;em2;em3;em4;lo# 选择需要监控的网卡 也就是你的镜像流量对应的网卡Semicolon ';' seperated list of interfaces to monitor [eth1] em4
Install Elasticsearch server locally for demo, must have at least 3G of memory, NOT recommended for prod# 写上es地址Elasticsearch server URL [http://localhost:9200] http://10.10.7.7:9200      
# 输入一个密码
Password to encrypt S2S and other things [no-default] 输密码
Moloch - Creating configuration files
Installing systemd start files, use systemctl
Moloch - Installing /etc/logrotate.d/moloch to rotate files after 7 days
Moloch - Installing /etc/security/limits.d/99-moloch.conf to make core and memlock unlimited
Moloch - Downloading GEO files
# 这个地方等待时间有点长，需要去下载下面的文件
2017-09-27 14:56:46 URL:https://www.iana.org/assignments/ipv4-address-space/ipv4-address-space.csv 
2017-09-27 14:57:02 URL:http://www.maxmind.com/download/geoip/database/asnum/GeoIPASNum.dat.gz 
2017-09-27 15:13:14 URL:http://download.maxmind.com/download/geoip/database/asnum/GeoIPASNumv6.dat.gz 
2017-09-27 15:13:26 URL:http://www.maxmind.com/download/geoip/database/GeoLiteCountry/GeoIP.dat.gz 
2017-09-27 15:13:35 URL:http://geolite.maxmind.com/download/geoip/database/GeoIPv6.dat.gz 
5)  Initialize/Upgrade Elasticsearch Moloch configuration
[root@moloch db]# /data/moloch/db/db.pl http://10.10.7.7:9200 initIt is STRONGLY recommended that you stop ALL moloch captures and viewers before proceeding.
There is 1 elastic search data node, if you expect more please fix first before proceeding.
This is a fresh Moloch install
Erasing
Creating
Finished.  Have fun!Finished#
6) Add an admin user if a new install or after an init
[root@moloch db]# /data/moloch/bin/moloch_add_user.sh admin "输密码" tcitops --admin
7) Start everything
[root@moloch db]# systemctl restart molochcapture.service
[root@moloch db]# systemctl restart molochviewer.service
8) Look at log files for errors
/data/moloch/logs/viewer.log
/data/moloch/logs/capture.log
9) Visit http://molochhost:8005 with your favorite browser.
user: admin
password: password from step #6
```

不要使用弱口令哦！**<br>**

**moloch 登陆**

经过上面的配置，让我们来访问一下moloch。

在浏览器中输入 [http://10.10.7.7:8005](http://10.10.7.7:8005/) 输入账号上面定的密码。

出现如下界面的时候 表示系统已经搭建起来啦。 

[![](https://p1.ssl.qhimg.com/t019146fe14359f89bf.png)](https://p1.ssl.qhimg.com/t019146fe14359f89bf.png)



**0x04 数据删除**

我现在的环境每天都有好几个T的数据包，es每天也有差不多200个G数据产生，所以当系统搭建起来后第一件事情 强烈推荐大家考虑数据的删除保留问题。



```
# 关于pcap的数据包 我是使用moloch来控制删除
[root@moloch ~]# vim /data/moloch-nightly/etc/config.ini
# moloch 默认是freeSpaceG = 5%，也就是磁盘空间会保留5% freeSpaceG = 5%
# es使用moloch自带的脚本来控制删除
[root@moloch db]# vim daily.sh 
#  !/bin/sh
# This script is only needed for Moloch deployments that monitor live traffic.
# It drops the old index and optimizes yesterdays index.
# It should be run once a day during non peak time.
# CONFIGESHOSTPORT=10.100.10.7:9200
RETAINNUMDAYS=1
/data/moloch-nightly/db/db.pl $ESHOSTPORT expire daily $RETAINNUMDAYS
# 在做个定时任务 每天晚上跑一次
[root@moloch ~]# crontab -e01 04 * * * /data/moloch-nightly/db/daily.sh &gt;&gt; /var/log/moloch/daily.log 2&gt;&amp;1
```

**网卡优化**<br>

```
# Set ring buf size, see max with ethool -g eth0ethtool -G eth0 rx 4096 tx 4096# Turn off feature, see available features with ethtool -k eth0ethtool -K eth0 rx off tx off gs off tso off gso off
```

**High Performance Settings**

```
# MOST IMPORTANT, use basic magicMode, libfile kills performancemagicMode=basic
# 官方说 pfring 效果更好 
# pfring/snf might be betterpcapReadMethod=tpacketv3
# Increase by 1 if still getting Input Dropstpacketv3NumThreads=2
# DefaultspcapWriteMethod=simplepcapWriteSize = 2560000
# Start with 5 packet threads, increase by 1 if getting thread dropspacketThreads=5
# Set to number of packets a secondmaxPacketsInQueue = 200000
```

**pfring 配置**

****

```
# 什么鬼 官方又建议 先去尝试tpacketv3  不过我还是建议使用pfring
We suggest you try tpacketv3 first if available on the host
[root@moloch ~]# vim /data/moloch-nightly/etc/config.inirootPlugins=reader-pfring.so
pcapReadMethod=pfring
```

**查看抓包****<br>**

****

```
# 让我们先用命令看看 网卡接收流量
[root@moloch ~]# dstat -n 
-net/total-
 recv  send 115M 1761k 112M 1238k 109M  168k 107M 1111k 110M 1695k 111M 1477k 107M 2305k
```

我们在来看看同一时间moloch中抓包数据量，因为都是动态数值，但是结果如此接近，是不是可以说千兆网卡下已经可以做到100% 数据包抓取，不信你去看[pfring 官方文档](http://www.ntop.org/products/packet-capture/pf_ring/)**<br>**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010ba8af9a3a2603bc.png)



**0x05 功能使用**

看到这里的同学都应该是真爱了，下面开始满满都是福利啦。

**历史数据分析**

你可以写一些search expression自由搭配检索你需要的信息，es作为支持速度就是快。

举个例子：源ip == 10.101.26.60 and 协议是 http 的 信息如下：

[![](https://p5.ssl.qhimg.com/t01c68e0740439d4d02.png)](https://p5.ssl.qhimg.com/t01c68e0740439d4d02.png)

**数据包导出**

你要是更习惯用wireshark分析，没有问题，moloch导出pcap也是很方便的、

推荐time range : “00:00:01”，bounding：“last packet”。moloch显示的是会话信息，bounding就很好理解了。

还有记得点一下“matching items”我的环境一秒钟 大概导出200M的数据量。

先确定一下时间，然后点一下export pcap。

[![](https://p0.ssl.qhimg.com/t015e5f2a64ae8129d1.png)](https://p0.ssl.qhimg.com/t015e5f2a64ae8129d1.png)

然后开始export pcap，就这么简单！ 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017552ab6ced845de6.png)



**0x06 结束语**

流量分析是一个比较复杂的系统工作，moloch在大规模的捕获数据包、索引方面做得相当卓越了。

在数据包的存取问题解决的情况下，随之而来的更多是数据包的分析：tcp的重传，mysql的慢查询，http的响应时间，这些可以从网络层面给业务带来红利的研究，值得大家去深挖研究。

欢迎有兴趣的小伙伴留言一起讨论。

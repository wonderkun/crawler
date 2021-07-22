> 原文链接: https://www.anquanke.com//post/id/149499 


# 安全研究 | Linux 遭入侵，挖矿进程被隐藏案例分析


                                阅读量   
                                **93245**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01dde4ef1afdc03b22.jpg)](https://p0.ssl.qhimg.com/t01dde4ef1afdc03b22.jpg)

本文作者：Fooying、zhenyiguo、murphyzhang



## 一、背景

云鼎实验室曾分析不少入侵挖矿案例，研究发现入侵挖矿行为都比较粗暴简单，通过 top 等命令可以直接看到恶意进程，挖矿进程不会被刻意隐藏；而现在，我们发现黑客开始不断使用一些隐藏手段去隐藏挖矿进程而使它获得更久存活，今天分析的内容是我们过去一个月内捕获的一起入侵挖矿事件。



## 二、入侵分析

本次捕获案例的入侵流程与以往相比，没有特殊的地方，也是利用通用漏洞入侵服务器并获得相关权限，从而植入挖矿程序再进行隐藏。

通过对几个案例的分析，我们发现黑客主要是利用 Redis 未授权访问问题进行入侵，对于该问题的说明可以参考我们过去做的一些分析：

[https://mp.weixin.qq.com/s/inazTPN5mHJYnt2QDliv8w](https://mp.weixin.qq.com/s/inazTPN5mHJYnt2QDliv8w)

在服务器被入侵后，首先可以明显感觉到服务器的资源被占用而导致的操作迟缓等问题，通过一些常规手段可以发现一些异常信息，但又看不到进程信息：

[![](https://p0.ssl.qhimg.com/t01ad77d0982cc3e245.png)](https://p0.ssl.qhimg.com/t01ad77d0982cc3e245.png)

通过 top 命令，可以看到显示的 CPU 使用率较低，但 ni 值为 100 ；同时通过 /proc/stat 计算 CPU 使用率又基本是 100% 。

[![](https://p5.ssl.qhimg.com/t01d83a5bf16db4b0c5.png)](https://p5.ssl.qhimg.com/t01d83a5bf16db4b0c5.png)

通过 netstat 查看端口监听情况，也可以看到异常的连接。

[![](https://p4.ssl.qhimg.com/t01ee5f165a33a39292.png)](https://p4.ssl.qhimg.com/t01ee5f165a33a39292.png)

通过在 Virustotal 查询 IP，可以看到 DNS 指向为矿池域名。

通过 find 命令查找入侵时间范围内变更的文件，对变更文件的排查，同时对相关文件进行分析，基本可以确认黑客使用的进程隐藏手法。

[![](https://p5.ssl.qhimg.com/t016eccd25abe0e4806.png)](https://p5.ssl.qhimg.com/t016eccd25abe0e4806.png)

[![](https://p2.ssl.qhimg.com/t01ffa67aa08cb56a47.png)](https://p2.ssl.qhimg.com/t01ffa67aa08cb56a47.png)

在变更文件里可以看到一些挖矿程序，同时 /etc/ld.so.preload 文件的变更需要引起注意，这里涉及到 Linux 动态链接库预加载机制，是一种常用的进程隐藏方法，而 top 等命令都是受这个机制影响的。

**在 Linux 操作系统的动态链接库加载过程中，动态链接器会读取 LD_PRELOAD 环境变量的值和默认配置文件 /etc/ld.so.preload 的文件内容，并将读取到的动态链接库进行预加载，即使程序不依赖这些动态链接库，LD_PRELOAD 环境变量和 /etc/ld.so.preload 配置文件中指定的动态链接库依然会被装载，它们的优先级比 LD_LIBRARY_PATH 环境变量所定义的链接库查找路径的文件优先级要高，所以能够提前于用户调用的动态库载入。**

**——段落引自《警惕利用 Linux 预加载型恶意动态链接库的后门》**

通过查看文件内容，可以看到加载一个 .so 文件：/usr/local/lib/libjdk.so

[![](https://p2.ssl.qhimg.com/t0130da843125bfdc29.png)](https://p2.ssl.qhimg.com/t0130da843125bfdc29.png)

而这个文件也在文件变更列表里。

我们通过查看启动的相关进程的 maps 信息，也可以看到相关预加载的内容：

[![](https://p4.ssl.qhimg.com/t01df284864bb40f224.png)](https://p4.ssl.qhimg.com/t01df284864bb40f224.png)

通过对 libjdk.so 的逆向分析，我们可以确认其主要功能就是过滤了挖矿进程，具体可见下文分析。

在知道了黑客使用的隐藏手法后，直接编辑 /etc/ld.so.preload 文件去掉相关内容，然后再通过 top 命令即可看到挖矿进程：

[![](https://p2.ssl.qhimg.com/t01619788908c3a65b1.png)](https://p2.ssl.qhimg.com/t01619788908c3a65b1.png)

[![](https://p2.ssl.qhimg.com/t017c6e9bcec6daf73b.png)](https://p2.ssl.qhimg.com/t017c6e9bcec6daf73b.png)

通过查看 /proc/ 下进程信息可以找到位置，看到相关文件，直接进行清理即可：

[![](https://p2.ssl.qhimg.com/t01c62f371094c1f250.png)](https://p2.ssl.qhimg.com/t01c62f371094c1f250.png)

[![](https://p2.ssl.qhimg.com/t01499c309cd4e2a637.png)](https://p2.ssl.qhimg.com/t01499c309cd4e2a637.png)

继续分析变更的文件，还能看到相关文件也被变更，比如黑客通过修改 /etc/rc.d/init.d/network 文件来进行启动：

[![](https://p3.ssl.qhimg.com/t0155c3c03e20e3a4af.png)](https://p3.ssl.qhimg.com/t0155c3c03e20e3a4af.png)

同时修改 /etc/resolv.conf ：

[![](https://p1.ssl.qhimg.com/t019488681523febcf2.png)](https://p1.ssl.qhimg.com/t019488681523febcf2.png)

还修改了 HOSTS 文件，猜测是屏蔽其他挖矿程序和黑客入侵：

[![](https://p3.ssl.qhimg.com/t01932b167ab32a0ec7.png)](https://p3.ssl.qhimg.com/t01932b167ab32a0ec7.png)

同时增加了防火墙规则：

[![](https://p4.ssl.qhimg.com/t016019533790969cb2.png)](https://p4.ssl.qhimg.com/t016019533790969cb2.png)

查询 IP 可以看到是一个国外 IP ：

[![](https://p5.ssl.qhimg.com/t01a66c50413db4a1be.png)](https://p5.ssl.qhimg.com/t01a66c50413db4a1be.png)



## 三、样本分析

通过对样本逆向分析，发现样本 libjdk.so 主要是 Hook 了 readdir 和 readdir64 两个函数：

[![](https://p2.ssl.qhimg.com/t011ec4b0c01424ede7.png)](https://p2.ssl.qhimg.com/t011ec4b0c01424ede7.png)

对应修改后的 readdir 函数结构如下（readdir64 函数也是类似的）：

[![](https://p1.ssl.qhimg.com/t01162dbf2c2ef7a215.png)](https://p1.ssl.qhimg.com/t01162dbf2c2ef7a215.png)

get_dir_name 函数结构：

[![](https://p4.ssl.qhimg.com/t01e2b8d52b9e6cf64a.png)](https://p4.ssl.qhimg.com/t01e2b8d52b9e6cf64a.png)

get_proces_name 函数结构：

[![](https://p5.ssl.qhimg.com/t01e7a27c896d8aaaa3.png)](https://p5.ssl.qhimg.com/t01e7a27c896d8aaaa3.png)

process_to_filter 常量定义如下：

[![](https://p1.ssl.qhimg.com/t01b2b88b774687b5ce.png)](https://p1.ssl.qhimg.com/t01b2b88b774687b5ce.png)

整个函数功能结合来看就是判断如果读取目录为 /proc，那么遍历的过程中如果进程名为 x7，则过滤，而 x7 就是挖矿进程名。

而类似于 top、ps 等命令在显示进程列表的时候就是调用的 readdir 方法遍历 /proc 目录，于是挖矿进程 x7 就被过滤而没有出现在进程列表里。



## 四、附录

### **IOCs：**

样本
1. 4000dc2d00cb1d74a1666a2add2d9502
1. 8bd15b2d48a051d6b39d4c1ffaa25026
1. e2a72c601ad1df9475e75720ed1cf6bf
1. d6cee2c684ff49f7cc9d0a0162b67a8d
矿池地址
1. xmr-asia1.nanopool.org:14433
1. 123.56.154.87:14444
钱包地址

42im1KxfTw2Sxa716eKkQAcJpS6cwqkGaHHGnnUAcdDhG2NJhqEF1nNRwjkBsYDJQtDkLCTPehfDC4zjMy5hefT81Xk2h7V.v7

### **相关链接：**

1.[https://mp.weixin.qq.com/s/inazTPN5mHJYnt2QDliv8w](https://mp.weixin.qq.com/s/inazTPN5mHJYnt2QDliv8w)

2.[https://cloud.tencent.com/product/hs](https://cloud.tencent.com/product/hs)

云鼎实验室主要关注腾讯云安全体系建设，专注于云上网络环境的攻防研究和安全运营，以及基于机器学习等前沿技术理念打造云安全产品。

编辑：少爷

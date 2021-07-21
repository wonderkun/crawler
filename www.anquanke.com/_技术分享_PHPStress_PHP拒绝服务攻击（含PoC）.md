> 原文链接: https://www.anquanke.com//post/id/86100 


# 【技术分享】PHPStress：PHP拒绝服务攻击（含PoC）


                                阅读量   
                                **88707**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：n0where.net
                                <br>原文地址：[https://n0where.net/phpstress/](https://n0where.net/phpstress/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t015ea50a96add3402d.png)](https://p1.ssl.qhimg.com/t015ea50a96add3402d.png)



翻译：[**shan66**](http://bobao.360.cn/member/contribute?uid=2522399780)

**稿费：80RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**前言**

导致这种拒绝服务攻击的根本原因，在于大多数现代Web服务器的配置漏洞。简而言之，简单而稳定的PHP调用将使Web服务器疲于打开PHP进程，而无力顾及其他。对于个人而言，通过耗尽Web服务器所有可用资源来实现拒绝服务攻击，是一种非常简单有效的方法。

使用标准电缆/DSL连接，这种攻击就可以通过标准的HTTP请求来耗尽Linux Web服务器的CPU和RAM资源。同时，这种攻击还会影响使用PHP-CGI或PHP-FPM（包括WordPress网站）处理动态PHP内容的Apache或NGINX Web服务器。此外，这些用于攻击Web服务器配置漏洞的请求，在攻击结束后将继续占用服务器的资源。

要想发动这种攻击，请设置目标URL和时间延迟参数，剩下的事情可以交由脚本来完成。

<br>

**攻击的对象**

需要注意的是，这种攻击与Slowloris有同样的前提要求。主要区别在于，Slowloris专注于消耗HTTP（apache）连接，而这种攻击主要侧重于吞噬PHP-CGI或PHP-FPM连接（在Apache或NGINX中）。

[![](https://p5.ssl.qhimg.com/t0163e90c6b9f068da6.png)](https://p5.ssl.qhimg.com/t0163e90c6b9f068da6.png)

<br>

**为什么PHPStress攻击能够得逞**

在大多数环境中，动态（PHP）内容的处理方法有两种：使用PHP-FPM或PHP FastCGI（mod_fcgid）。虽然Plesk、Cpanel、ISPConfig等共享托管上的现代控制面板已经开始使用PHP-FPM作为动态内容处理的标准，但大多数（默认情况下）情况下还是通过FastCGI来处理PHP内容。

<br>

**FastCGI/Mod_fcgid**

****

FastCGI应用程序在Web服务器（Apache或其他智能）之外执行，并使用套接字等待来自Web服务器的请求。如果FastCGI/ PHP-CGI经过了正确的设置，它将忽略请求，而不是继续分配内存。在此期间，客户会超时。当流量高峰过去后，一切会恢复正常。

需要注意的是：当PHP-CGI耗尽可用进程时，Apache将启动并开始生成其他进程以尝试满足需求。由于这个过程使用了占用大量内存的httpd进程，所以很快就会耗尽服务器（其中包括每个进程中嵌入的完整PHP解释器）的内存资源。生成的Apache进程的最大数量，是由ServerLimit或MaxClients设置中设置的数字（通常为256或512）而定的。启动256个Apache进程的话，将花费Web服务器的很长时间。

<br>

**PHP-FPM（FastCGI进程管理）**

FPM（FastCGI进程管理）是PHP FastCGI的一种替代实现，它提供了一些额外的功能来支持高负载的站点。根据我自己的经验，PHP-FPM在处理PHP方面要快得多。

**攻击过程**

首先，从GitHub下载PHPStress或通过下列的命令克隆repo： 

```
git clone https://github.com/nightlionsecurity/phpstress phpstress
```

要进行攻击，请设置目标URL和时间延迟参数，然后让脚本执行其余操作。同时，脚本需要严格按照如下所示的参数来使用。

```
php phpstress.php www.targeturl.com -d 0 -r 0
```

**攻击结果**

在这两种情况下，FPM和/或CGI进程都被请求全部占用；服务器的内存被填满，一切都会停摆。对于运行PHP-FCGI的Apache或NGINX服务器来说，会有一些有趣的事情要注意。

<br>

**PHP-FPM**

在PHP-FPM服务器上，生成的最大进程数由配置文件中的相关内容决定。如果你的pm.max_children = 25，那么最多产生的进程数将是25。

根据超时的设置情况，进程在攻击后的一段时间内仍保持打开状态（通常最少为两分钟）。

[![](https://p4.ssl.qhimg.com/t01d6498e0b50a08ecc.png)](https://p4.ssl.qhimg.com/t01d6498e0b50a08ecc.png)

<br>

**PHP-FCGI**

FastCGI的结果更加有趣。随着FastCGI缓冲区被填满，Apache会将这些请求排队，等待处理。Apache不再继续生成FastCGI进程，而是根据MaxClients指令启动相匹配的进程。结果是生成数百个Apache进程，致使服务器彻底超载，如下所示 

[![](https://p0.ssl.qhimg.com/t01035a20a466b2e977.png)](https://p0.ssl.qhimg.com/t01035a20a466b2e977.png)

<br>

**缓解措施**

为了防御这种攻击，您要调整的NGINX和FastCGI的一些标准配置。下面的设置是默认值，但是它们不是最佳的，应该根据自己的情况进行调整。我通常将超时设置为1-2秒。

**FCGID.CONF**

/etc/httpd/conf.d/fcgid.conf



```
# Number of seconds of idle time before a process is terminated
FcgidIOTimeout 1000 # maximum period of time the module will wait while trying to read from or write to a FastCGI application
FcgidMaxProcessesPerClass 100 #maximum number of processes per class (user)
FcgidIdleTimeout 240 # application processes which have not handled a request for this period of time will be terminated
FcgidProcessLifeTime 3600 # maximum lifetime of a single process (seconds)
FcgidMaxProcesses 1000 #maximum number of FastCGI application processes which can be active at one time.
```

**Apache – Httpd.Conf**

/etc/httpd/conf/httpd.conf



```
Timeout 60
KeepAliveTimeout 15
KeepAlive Off
MaxKeepAliveRequests 100
StartServers   8
MinSpareServers    5
MaxSpareServers   20
ServerLimit 256
MaxClients 256
```

**Php-Fpm.Conf**

/etc/php-fpm.conf



```
; Time limit for child processes to wait for a reaction on signals from master.
; Available units: s(econds), m(inutes), h(ours), or d(ays)
; Default Unit: seconds
; Default Value: 0
process_control_timeout = 10s
```

/etc/php-fpm.d/domain.conf



```
; By default use ondemand spawning (this requires php-fpm &gt;= 5.3.9)
pm = ondemand
pm.max_children = 50
pm.process_idle_timeout = 60s
```

**PoC下载地址：**[**https://github.com/nightlionsecurity/phpstress**](https://github.com/nightlionsecurity/phpstress)** **

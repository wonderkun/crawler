> 原文链接: https://www.anquanke.com//post/id/234770 


# 实战预演——Redis基于主从复制的RCE


                                阅读量   
                                **255257**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t01f83d5cdb5012110b.jpg)](https://p4.ssl.qhimg.com/t01f83d5cdb5012110b.jpg)



一年一度的HW又将到来。作为参加的单位都开始蓄势待发，做充足的准备。这么大的“阵仗”是因为攻防演练具有重大意义，不仅能通过演练检验单位网络和信息基础设施安全防护水平，还能提高应急处置和指挥调度能力，最终提高信息系统的综合防御能力。

本文主要内容包括模拟红方的角度对“Redis基于主从复制的RCE”进行漏洞复现，并模拟蓝方的角度对受该漏洞攻击的主机进行入侵溯源。“上医治未病”，文中还将对该漏洞的预防方式进行介绍。希望本文的内容能够对致力于甲方安全建设及乙方安全研究的人员有所帮助。



## 一、漏洞复现

本章将从攻击者的角度进行模拟，对攻击利用方式“基于Redis主从复制命令执行方式，生成交互式的bash shell”做复现。

**（1）配置Redis漏洞环境**

首先在kali中，执行命令：wget http://download.redis.io/releases/redis-4.0.11.tar.gz。

[![](https://p5.ssl.qhimg.com/t01d96b7e84b6ad31d4.png)](https://p5.ssl.qhimg.com/t01d96b7e84b6ad31d4.png)

解压该压缩文件，并将之复制三份，分别为redis.master、redis.slave以及redis.slave1。

[![](https://p5.ssl.qhimg.com/t019c8abdc9959d8ff9.png)](https://p5.ssl.qhimg.com/t019c8abdc9959d8ff9.png)

接下来，我们需要分别进入这三个目录中做配置。首先把配置文件各自备份一份，然后对redis.master/redis.conf做配置。我们设置一下日志的路径：logfile “/data/logs/redis.master”。

接着设置redis.salav/redis.conf ，这里需要把服务端口给改了。因为在master中已经占用了默认端口（6379端口）了，所以这里笔者改为6380这个端口，然后设置 slaveof 127.0.0.1 6379，这个端口的服务是本机6379这个端口服务的备份机子。

同理，对redis.salav1也做类似的配置，只是对服务端口号要做类似的更改（此处不做赘述）。

当三台机子都配置好后，就可以开启这三个服务了。通过执行命令“./redis.master/src/redis-server/redis.master/redis.conf”，

这样开启了6379端口的master服务；随后开启salav的服务（执行命令./redis.salav/src/redisserver/redis.salav/redis.conf）；

最后开启salav1的服务（执行令./redis/salav1/src/redis-server /redis.salav/redis.conf ）,这里就是三个终端开的三个服务。

[![](https://p0.ssl.qhimg.com/t010f81ffc7a3eb61bc.png)](https://p0.ssl.qhimg.com/t010f81ffc7a3eb61bc.png)

这里我们看一下每个端口服务的运行状态是怎样的。首先查看的是master，这里可以看到“role”为master，然后连接了两个“slave”。

[![](https://p3.ssl.qhimg.com/t010bf78eb74b936403.png)](https://p3.ssl.qhimg.com/t010bf78eb74b936403.png)

接下来查看slave，这里可以看到“role”为slave，而且master_port为6379。

[![](https://p4.ssl.qhimg.com/t01d0e65de8d7615ace.png)](https://p4.ssl.qhimg.com/t01d0e65de8d7615ace.png)

**（2）模拟攻击**

接下来，我们需要下载和编译恶意代码，其下载地址为git clone https://github.com/n0b0dyCN/RedisModules-ExecuteCommand.git。在编译完成后，src目录下生成了一个.so文件。

[![](https://p2.ssl.qhimg.com/t01bfe6772b6f23396e.png)](https://p2.ssl.qhimg.com/t01bfe6772b6f23396e.png)

接下来我们需要下载利用工具来 getshell，地址为git clone https://github.com/Ridter/redis-rce，然后把module.so复制到 /root/redis-rce/下面。

[![](https://p0.ssl.qhimg.com/t01a36e2f8a078aad0f.png)](https://p0.ssl.qhimg.com/t01a36e2f8a078aad0f.png)

接下来先在本地监听一个用于接受反弹shell的端口，笔者习惯性用8888，这里做出来的效果不明显，所以笔者还是决定去搭建另外一个虚拟机，具体搭建过程不赘述了。主要是要使用不同主机间做主从备份的话，需先在master上的配置文件做一些改变，首先把bind改为0.0.0.0，其次还要把protect-mode 改为no 这样就可以实现不同主机之间的主从备份了，那么现在可以在master上面先监听本地8888端口命令为“nc -lvvp 8888”。

[![](https://p1.ssl.qhimg.com/t01987cc9fc4f37780e.png)](https://p1.ssl.qhimg.com/t01987cc9fc4f37780e.png)

这里可以看到已经返回了slave备份redis的shell了。通过查看命令“ifconfig eth0”的返回结果，确实可以证实是slave的ip。然后笔者去备份redis查看所有网络连接，这里可以看到出了一个与“140 master”主机相连的44942端口，还有一个用于反弹shell的网络连接端口8888。

[![](https://p1.ssl.qhimg.com/t018ca15dc94d1cf2fa.png)](https://p1.ssl.qhimg.com/t018ca15dc94d1cf2fa.png)

接下来就需要通过python3获取一个交互式的shell，具体的命令可以为“python3 -c “import pty;pty.spawn(‘/bin/bash’)”。

[![](https://p1.ssl.qhimg.com/t01b22d6f43dbfcb174.png)](https://p1.ssl.qhimg.com/t01b22d6f43dbfcb174.png)



## 二、入侵溯源

本章将模拟防守者的角度，对上一章节的攻击利用方式做入侵溯源。

首先排查的是备份Redis上面的netstat -antp，在这里笔者发现master有两个连接。一个连接的端口是本机的6379，这个端口是正常的slave连接master端口，但是还有一个连接是笔者本地的38594连接的master的8888端口，这显然是不正常的网络连接。因此，我们可以根据后面的pid去查对应的ppid，查看到pid为1196这个的时候，后面命令跟的是一个[sh]这样的东西，就是又执行了shell。

[![](https://p0.ssl.qhimg.com/t0164da7735ef2a3646.png)](https://p0.ssl.qhimg.com/t0164da7735ef2a3646.png)

[![](https://p0.ssl.qhimg.com/t01b43b1f6613ebf435.png)](https://p0.ssl.qhimg.com/t01b43b1f6613ebf435.png)

一般这个时候可以根据网络连接排查，一般黑客获进入以后会获取反弹shell，那么我们应该排查对应反弹shell的所有可能命令行或者是可疑文件执行的反弹，因此我们应该着重排查。也有可能会执行一些敏感的命令，比如用wget下载一些东西，所以还要注意这种命令。



## 三、总结

很多主从复制导致任意命令执行都是通过Redis的未授权访问漏洞导致了横向移动攻击方式的发生。这里通过对Redis主从复制导致命令执行漏洞的复现，对该漏洞的产生原理有了进一步的了解，也对我们预防和对该漏洞的排查有了更清晰的思路。

**预防方式**
1. 我们可以主动关闭Redis的6379端口不对外开放；
1. 设置密码认证，通过远程访问Redis服务的都要经过密码认证才能访问。
**入侵溯源**
1. 查看redis服务器的网络连接，一般master会与slave通过6379端口进行通信，当redis子进程有未知的端口的网络连接时，多半都是恶意的反弹或者一些网络下载行为；
1. 查看命令历史，很可能攻击者会通过wget，或者curl这些网络工具下载一些恶意脚本到本地可写目录linux，常见的就是/mnt/目录下，所以我们也应着重审查。
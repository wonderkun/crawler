> 原文链接: https://www.anquanke.com//post/id/86318 


# 【技术分享】Windows 7 下使用 Docker 虚拟化秒部署“漏洞靶机”实操详解


                                阅读量   
                                **218140**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p3.ssl.qhimg.com/t011833a9f523215ec0.jpg)](https://p3.ssl.qhimg.com/t011833a9f523215ec0.jpg)**

****

译者：[myles007](http://bobao.360.cn/member/contribute?uid=749283137)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

**1. 学习背景**

一开始本来是想搭建一个有关最近爆出的有关samaba共享的漏洞攻击环境的靶机（号称是linux版本的永恒之蓝），但是最后发现搞着搞着变成了研究docker 虚拟化去了。在整个部署的过程遇到了各种坑，这里我们把个人在学习过程中Get到的各种小技能分享于大家。 

所以这篇文档的核心就是带着大家一起学习下了解怎样在Widows 7 环境下安装一个Doker 的环境，以及如果通过Docker来快速部署一个“漏洞靶机”，并实现外网对docker 容器的正常访问。

**2. 内容概要**

Docker 基础知识

window 7环境安装Docker

Docker 容器部署靶机

实现外网对Docker容器的访问

CVE-2017-7494 Samba 远程代码执行漏洞

MSF框架下攻击演示

<br>

**二、Docker 基础知识**

Docker 是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的容器中，然后发布到任何流行的 Linux 机器上，即可以实现虚拟化。

容器是完全使用沙箱机制，相互之间不会有任何接口（类似 iPhone 的 app）。几乎没有性能开销，可以很容易地在机器和数据中心中运行。最重要的是，他们不依赖于任何语言、框架或包装系统。

**2.1 Docker 三个基本概念**

镜像(Image)

容器(Container)

仓库(Repository)

只要理解了上面这个是三个概念，我们就可以对Docker有个感性的认识了，大家快随我来吧。

**2.2 镜像(Image)**

2.2.1 理论概念

对于操作系统大家可能都很熟悉，操作系统一般分为内核和用户空间两部分。对于 Linux 来说，其内核启动后，会自动挂载 root 文件系统，并为用户空间支持，方便用户进行相应的数据操作。而 Docker 镜像（Image），就相当于是一个 root 文件系统。比如我们说到Docker官方镜像 ubuntu:14.04时,其实它就是一个包含了完整的 Ubuntu 14.04 最小系统的 root 文件系统。

Docker 镜像其实就是一个特殊的文件系统，除了提供容器运行时所需的程序、库、资源、配置等文件外，还包含了一些为运行时准备的一些配置参数（如匿名卷、环境变量、用户等）。镜像是不包含任何动态数据的，其内容在构建之后也不会被改变，也就是说数据与应用是完全分开的。

2.2.2 消化理解

其实技术上了这么多，对于我们这些想用Docker的人来说，我们只要知道Docker镜像就是一个xxx.iso的镜像压缩文件，且知道我们只要有了这个镜像压缩文件，通过Docker我们就可以快速部署一个我们想要的“靶机应用环境”，明确这个就OK了。 

等到你用的很溜的时候，你再回来看这些利用理论概念，你就会发现豁然开朗，一切都是那么的So easy !!!

**2.3 容器(Container)**

2.3.1 理论概念

那么说到容器，我们就要从镜像（Image）和容器（Container）的关系了解下容器，这里为了让大家更好的理解容器，我们就用一个类比来给大家解释下什么是容器。

如果大家对编程有点了解的话，Docker中所说的“镜像”与“容器”的关系就像是面向对象程序设计中的“ 类” 和“实例”的关系，我们知道“类”是静态定义好的，而“实例”是在“类”的基础上创建的动态可操作的对象。

“镜像”对应的就是“类”，其是静态的定义好；

“容器”对应的就是“实例”，其就是之前定义好的类上创建出的一个动态对象。

对于容器，我们是可以被创建、启动、停止、删除、暂停等。

2.3.2 消化理解

那么说的再浅显一点就是：“镜像”是由各种大牛们整理好的“漏洞镜像环境”，然后打的一个包（xxx.iso哦！！！），而“容器”就是我们在获取到漏洞环境镜像后，在Docker引擎跑起来的真实的动态环境，而这个运行起来的“漏洞环境”就是“容器”了，也就是我们日思夜想想要的“漏洞环境靶机”了。

**2.4 Docker 仓库服务器（Docker Registry）**

2.4.1 理论概念

为什么我们能通过Docker可以快熟部署一个“漏洞环境靶机”能，就是因为有各种大牛分享出来的镜像，那这些镜像是不是应用该有一个可以集中存放和分发镜像的服务器呢，对了Docker Registry就是这样一个仓库服务。

我们要明确一个 Docker Registry 中可以包含多个仓库（Repository）；每个仓库可以包含多个标签（Tag）；每个标签它对应才是一个镜像。

通常，一个仓库会包含同一个软件不同版本的镜像，而标签就常用于对应该软件的各个版本。我们可以通过 &lt;仓库名&gt;:&lt;标签&gt; 的格式来指定具体是这个软件哪个版本的镜像。如果不给出标签，将以 latest 作为默认标签。以 Ubuntu 镜像 为例，ubuntu 是仓库的名字，其内包含有不同的版本标签，如，14.04, 16.04。我们可以通过 ubuntu:14.04，或者 ubuntu:16.04 来具体指定所需哪个版本的镜像。如果忽略了标签，比如 ubuntu，那将视为 ubuntu:latest。

仓库名经常以 两段式路径 形式出现，比如 jwilder/nginx-proxy，前者往往意味着 Docker Registry 多用户环境下的用户名，后者则往往是对应的软件名。但这并非绝对，取决于所使用的具体 Docker Registry 的软件或服务。

2.4.2 消化理解

简单的的理解Docker Registry，其它就是一个“服务器”，这个服务器里有很多的“各类镜像仓库”，而每个仓库里又存放着各种“镜像”，同时“镜像”使用不同的“标签”来区别不同的版本信息；

2.4.2 Docker 镜像仓库服务器收集

Docker 仓库其官方库在国外，所以对于我们天朝的小伙伴们来说，是件很痛苦的的事情，还好国内也有个仓库，下面就给大家贴出链接，当然我们想要的是漏洞环境镜像库，所以我也收集了一个，大家如果有什么新的好的镜像仓库，也请分享一下。

Dokcer官方仓库：[https://www.docker.com/](https://www.docker.com/)

Docker国内仓库

网易蜂巢：[https://c.163.com/hub](https://c.163.com/hub)

daocloud：[http://hub.daocloud.io/](http://hub.daocloud.io/)

Dokcer漏洞仓库：[https://github.com/Medicean/VulApps](https://github.com/Medicean/VulApps)

<br>

**三、Windows 7 for Docker 安装**

**3.1 Windows 7 环境选择**

在这里不得不跟大家说下，个人选择使用Window 7 作为安装Docker环境的原因，由于个人PC配置比较低，跑不动Windows 10，所以一直在使用Window 7。我们如果对Dockerd的基础知识有点了解的话，我们知道docker其实使用Go语言在linux系统下开发运行的，也就是说起原始安装环境最好时linux,而如果想用window运行，就只能在window基础上先运行一个linux虚拟机，然后再在这个linux虚拟机下运行docker。

网上放出的比较多的windows 的安装教程，其大大部分都是基于windows 10 的系统进说明的，故我们这里就记录下个人在windows 7 下对于docker环境的部署安装。

**3.2 下载DockerToolbox安装包**

由于Docker 的官方现在地址不在咱们天朝，所以下载起来非常的不方便，这也是我们安装过程中遇到的第一个拦路虎了。在整个安装的过程中我就折腾了很久，后来发现国内有个站做的不错，可以直接进行安装包的下载，速度非常快，这里推荐给大家。 

安装包名称：DockerToolbox.exe 

主网站地址：[http://get.daocloud.io/](http://get.daocloud.io/) 

最新安装包：

http://dn-dao-github-mirror.daocloud.io/docker/toolbox/releases/download/v17.05.0-ce/DockerToolbox-17.05.0-ce.exe 

注： 以上为个人遇到的第一个“坑”哦！！！（安装包的下载与选择）

**3.3 DockerToolbox 安装**

有关于安装包的安装基本没有什么太多需要交代，咱们默认安装一路回车即可。在安装完后会在桌面多出3个软体图片。

Oracle VM VirtualBox ++++&gt;&gt;&gt; 虚拟机

Kitematic (Alpha) ++++&gt;&gt;&gt; 图形化管理工具

Docker Quickstart Terminal ++++&gt;&gt;&gt; 终端管理

[![](https://p0.ssl.qhimg.com/t01ff8e1526c69fb944.png)](https://p0.ssl.qhimg.com/t01ff8e1526c69fb944.png)

**3.4 启动docker**

预告： 前方会有一个“坑”，请大家注意！！！

直接点击运行桌面的“Docker Quickstart Terminal”快捷方式启动docker,不过在启动过程中我们会发现，程序会去目录“C:Usersadmin.dockermachinecache”下寻找boot2docker.iso镜像文件，如果不存在会自动去github上下载，这样的下载的速度我们是可想而知的了，而且我基本上没有成功下载成功过，所以搞到这里我们是不是就很蛋疼呢，反正我是被坑大了。

[![](https://p2.ssl.qhimg.com/t0108b21637c0dba780.png)](https://p2.ssl.qhimg.com/t0108b21637c0dba780.png)

[![](https://p3.ssl.qhimg.com/t0100ded4953f6283c2.png)](https://p3.ssl.qhimg.com/t0100ded4953f6283c2.png)

小秘密：这里告诉大家一个秘密，其实在我们的docker的安装根目录下已经有一个 boot2docker.iso镜像，只是我也不知道为什么启动程序不去这里找。 

那好吧，废话不多说我们就自己手动将这个ISO文件复制到上面截图的目录“C:Usersadmin.dockermachinecache”下（注：以你安装过程中的实际目录位置为准。），然后关闭当前的启动界面，再次启动“Docker”，此时我们会发现启动的非常顺利。至此整个windows 7 环境下的docker 环境我们就部署OK了。

[![](https://p1.ssl.qhimg.com/t01d33867c9366a8e98.png)](https://p1.ssl.qhimg.com/t01d33867c9366a8e98.png)

[![](https://p1.ssl.qhimg.com/t01279429699931b28e.png)](https://p1.ssl.qhimg.com/t01279429699931b28e.png)

注：以上为个人遇到的第二个“坑”哦，因为下载不了，Docker启动会过不去！！！（boot2docker.iso镜像文件）

<br>

**四、 创建Docker容器**

终于来到Docker容器的创建了，接下来我们就进入到通过各种Docker管理工具进行Docker容器的创建了，其实Docker容器的创建真的很简单，基本上两条命令就能搞定了。 

但是这里为了让大家更好的了解Docker的一些使用，我这里给大家简单的说下在Windows 环境下Docker部署的结构和几个管理的工具组件。

**4.1 Windows Docker 环境部署结构**

首先大家可以看看下面这个图，本张图主要是展现在三种操作系统（Linux/Windows/OS X）上 Docker 部署实现的不同结构，其实仔细观察会发现Docker的部署实现有两种结构类型。

直接部署Docker 环境

虚拟机+Linux虚拟主机部署Docker 环境

4.1.1 直接部署Docker 环境

前面有提到Docker 是基于GO语言在Linux平台上开发出来的程序，故Linux环境是其原生运行环境，所以Docker 是可以直接安装在相应的Linxu主机平台上。

4.1.2 虚拟机+Linux虚拟主机部署Docker 环境

那么Windows主机如果想要运行Docker环境怎么办呢？那就要借助于虚拟机环境了，所以从图中我们可以清晰的看到，Windows上安装Docker,其实现实部署了一个Linux虚拟机，然后在这个虚拟机里部署了Docker环境。

预告：这里说的Windows系统部署Docker环境的结构，就引起其后面说到的“外网默认是无法访问docker容器”问题的根源。 

[![](https://p5.ssl.qhimg.com/t01138f0c498916f966.png)](https://p5.ssl.qhimg.com/t01138f0c498916f966.png)

**4.2 Windows 下Docker 环境组件**

Windows 下安装Docker后，其主体上分为两个组件部分，即Docker machine &amp; Docker Client

（1）Docker machine：其实就是虚拟机环境加上其内部的Docker环境；

（2）Docker client：其是为Windows 提供一个管理Docker Machine环境的客户端工具。

**4.3 创建Docker 容器**

其实上面说的这么多，都是为了这里引出使用什么工具与怎么创建一个Docker容器（即靶机环境）。

4.3.1 管理工具

在Windows 环境下可以管理Docker容器的管理工具有多个，我这里了解的不下三个：

（1）Docker Quickstart Terminal

这个工具是个命令行终端管理工具，我们双击它可以打开Docker machine服务，通过这个终端我们可以进行Dcoker容器的创建与管理。

[![](https://p3.ssl.qhimg.com/t0143bfd69f64700b30.png)](https://p3.ssl.qhimg.com/t0143bfd69f64700b30.png)

（2）Git Bash

这个Git Bash 工具是个真正的客户端终端管理工具，我们只要选中桌面，右击鼠标节可以看到Git Bash Here了。不过我们每次使用它连接Docker machine时，需要配置环境变量，后面再创建Docker 容器时，会介绍给大家。 

[![](https://p1.ssl.qhimg.com/t0154bacaf10d714f96.png)](https://p1.ssl.qhimg.com/t0154bacaf10d714f96.png)

（3）Kitmatic(Alpha)

这个工具是一个图像好管理工具，由于其默认只能使用官方的镜像源以及图形化操作的局限性，这里不做过多的说明，大家自行研究。

[![](https://p5.ssl.qhimg.com/t016338c40deb1c0bad.png)](https://p5.ssl.qhimg.com/t016338c40deb1c0bad.png)

（4）Virtual Box

想想，我们的这个Docker环境其实质就是部署在Viritul Box中的一个Linux虚拟机中，那么只要我们能管理这个linxu虚拟，也就可以管理Docker了。

4.3.2 创建容器命令

关于Windows下关于Docker的管理工具说了这么多，个人这里推荐使用Git Bash Docker客户端管理工具，当然前提是下在确认已经启动Docker环境后，所以这也是一种docker的管理方式。 

OK,废话不多说了，直接上干货，各位看官请打起精神来呀，我们进入正题…..

4.3.2.1 初始化工作

（1） 第一步：启动Docker环境 

选择“Docker Quickstart Terminal”，右击鼠标以管理员身份运行；

（2）第二步：开启Git Bash客户端，配置环境变量 

选中桌面，点击鼠标右键，选中“Git Bash Here”启动客户端；接着就是配置Docker Machine环境变量，具体过程分为两步：

查询环境变量要求



```
Administrator@USER-20170106BT MINGW64 ~/Desktop
$ docker-machine env
```

执行环境变量要求语句

直接复制查询环境变量获取的最后一句脚本，执行即可（具体执行语句的内容以每个人的实际获取内容为准，以下语句为我个人环境变量查询后获取的内容）；



```
Administrator@USER-20170106BT MINGW64 ~/Desktop
$ eval $("C:Program FilesDocker Toolboxdocker-machine.exe" env)
```

[![](https://p3.ssl.qhimg.com/t014587165fce2e07e5.png)](https://p3.ssl.qhimg.com/t014587165fce2e07e5.png)

4.3.2.2 下载镜像

使用以下语句，进行镜像的拉取（即下载），这里以快速部署一个ubuntu系统环境为例。



```
$ docker pull ubuntu:latest # 使用pull 命令进行“ubuntu最新版镜像”拉取
$ docker images #已拉取镜像内容查询
REPOSITORY                     TAG IMAGE         ID    CREATED            SIZE
hub.c.163.com/library/ubuntu   latest  7b9b13f7b9c0    9 days ago        118MB
```

[![](https://p0.ssl.qhimg.com/t0135610a83ee1f522b.png)](https://p0.ssl.qhimg.com/t0135610a83ee1f522b.png)

[![](https://p4.ssl.qhimg.com/t01518a027501f1ec77.png)](https://p4.ssl.qhimg.com/t01518a027501f1ec77.png)

注： 截图中以c.163.com网易提供的docker库作为演示，主要是官方下载太慢了，如果大家可以忍受这个速度的话，推荐大家使用c.163.com的镜像库。

4.3.2.3 创建Ubutu系统环境(Docker容器)

别眨眼哦，现在就是见证奇迹的时刻了，秒部署一个ubuntu环境，执行的命令如下



```
Administrator@USER-20170106BT MINGW64 ~/Desktop
$ winpty docker run -it hub.c.163.com/library/ubuntu:latest bash #创建docker容器
root@de0b90c6363d:/#
root@de0b90c6363d:/# cat /etc/issue
Ubuntu 16.04.2 LTS n l
root@de0b90c6363d:/# uname -a
Linux de0b90c6363d 4.4.66-boot2docker #1 SMP Fri May 5 20:44:25 UTC 2017 x86_64 x86_64 x86_64 GNU/Linux
root@de0b90c6363d:/#
```

[![](https://p1.ssl.qhimg.com/t01b80ed1446da2997a.png)](https://p1.ssl.qhimg.com/t01b80ed1446da2997a.png)

看见了，秒建一个ubuntu环境，是不是很神奇呀，就这么一条命令敲下去，我们就有了一个ubuntu环境了。

<br>

**五、实现外网互联访问**

所以接下来，就是要实现外对docker容器的访问了，这里之所以要将“实现外网访问Docker容器”单独拿出来说，实在是因为网上真心没有什么资料说道在Windows 环境实现通过物理网卡来访问Docker宿主机中的Docker容器的方法，个人基本是来回找资料看视频，搞了两天才找到方案,所以这里一定要拿出来分享给大家。

**5.1 Docker Bridge 桥接模式**

5.1.2 四种互联模式

其实Docker容器网络互联有4种网络连接方式。我们在使用docker run 创建 Docker 容器时，可以用 –net 选项指定容器的网络模式，具体内容如下表。

[![](https://p1.ssl.qhimg.com/t014b114ff9a00e832a.png)](https://p1.ssl.qhimg.com/t014b114ff9a00e832a.png)

但是有关于这4中模式的具体工作方式，我这里不做过的介绍，我们只重点关注bridge的工作方式。因为bridge模式是我们默认创建的docker容器的网络互联模式，也是我们将要用到的互联模式，通过bridge模式我们可以实现物理接口与docker容器接口的互联，具体实现配置，实际一个docker 配置参数就能搞定，即“-p”端口映射。

5.1.3 Bridge 网络互联详解

下图是一张Linux原生环境下的docker bridge桥接模式网络互联实现示意图，通过这张图我们可以清晰的看到“container1” &amp; “container2”（即docker容器1 &amp; 2）与物理宿主机的eth0接口是直接桥接在一起的，那么这也就意味着物理主机的网络是可以与docker容器直接互联互通的(当然还要在docker下简单配置下“端口映射”)。 

[![](https://p0.ssl.qhimg.com/t01f8941191284e46dd.png)](https://p0.ssl.qhimg.com/t01f8941191284e46dd.png)

小结：Linux 环境的宿主主机的网络是可以与docker容器接口直接互联的，只要配置好“端口映射”就可以实现docker容器应用的对外发布了。

5.1.4 Windows环境中docker 桥接

5.1.4.1 Windows环境下docker容器不能外网访问题分析

那么问题就来了，为什么Windows环境中docker 桥接会存在问题呢，下面就带大家一起看看问题的究竟。我们也来看看在indows环境中docker 桥接中各个接口是怎样的一个情况。 

如果大家还记得前面4.2章节的“预告”内容，就会很容易看明白下面这一张docker容器网络互联逻辑图了。 

我们可从图中看到在Windows环境中，docker容器是存在于一个linux虚拟机中的，也就说这个虚拟的linux主机才是docker环境的真正宿主主机，那docker容器被创建后，其与宿主机的eth0口可以直接“桥接”互联，但是与我们的物理主机“Windows主机”的“本地接口”并没有与其互联，这就可以理解为什么在Windows中的docker容器，我们无法从外网去访问他们的原因了。

[![](https://p1.ssl.qhimg.com/t014c815b696261b150.png)](https://p1.ssl.qhimg.com/t014c815b696261b150.png)

5.1.4.2 Window环境下实在docker容器的外网互联

预告：全文最干的干货来了，大家请屏住呼吸跟我来…

这次就不卖关子了，简单的告诉大家怎样才能做到Windows环境下实现“docker容器的外网互联访问，具体实现两步即可。

（1）配置docker 容器的“端口映射”

docker容器配置端口映射，其实很简单，只要在创建docker容器时，添加一个“-p”的参数即可，下面以创建一个TCP 445 端口映射的samba容器。



```
$ docker pull medicean/vulapps:s_samba_1   #1、下载samba漏洞镜像
$ docker run -d -p 445:445 samba:lastest   #2、创建镜像，并配置445的端口映射；
```

命令解释

[![](https://p5.ssl.qhimg.com/t015347e326031725f4.png)](https://p5.ssl.qhimg.com/t015347e326031725f4.png)

[![](https://p4.ssl.qhimg.com/t01cae3f8017bd6c461.png)](https://p4.ssl.qhimg.com/t01cae3f8017bd6c461.png)

（2）配置virtualbox的端口转发；

首先打开桌面的virturlbox，然后依次选择“设置”-“网络”-“网卡1”-“高级”-“端口转发”，编辑“端口转发”，具体配置项解释，请见截图。

[![](https://p5.ssl.qhimg.com/t01bc30c894b69d6e74.png)](https://p5.ssl.qhimg.com/t01bc30c894b69d6e74.png)

[![](https://p1.ssl.qhimg.com/t01aba72f1c12923503.png)](https://p1.ssl.qhimg.com/t01aba72f1c12923503.png)

（3）共享外网访问

直接通过物理网卡的接口地址 192.168.31.41进行共享访问，访问成功！！！

[![](https://p4.ssl.qhimg.com/t01e6beb31ecb1e5399.png)](https://p4.ssl.qhimg.com/t01e6beb31ecb1e5399.png)<br>

<br>

**六、Samba远程代码执行漏洞复现**

**6.1 漏洞简介**

漏洞编号：

 CVE-2017-7494

影响版本：

Samba 3.5.0到4.6.4/4.5.10/4.4.14的中间版本

漏洞利用条件： 

攻击者利用漏洞可以进行远程代码执行，具体执行条件如下：

1.  服务器打开了文件/打印机共享端口445，让其能够在公网上访问

2.  共享文件拥有写入权限

3.  恶意攻击者需猜解Samba服务端共享目录的物理路径

满足以上条件时，由于Samba能够为选定的目录创建网络共享，当恶意的客户端连接上一个可写的共享目录时，通过上传恶意的链接库文件，使服务端程序加载并执行它，从而实现远程代码执行。根据服务器的情况，攻击者还有可能以root身份执行。

**6.2 快速部署靶机环境**

预告：前面讲述了这么多的基础知识与操作过程，大家看了可能会觉的非常累，那么我们现在给大家上点真正的“干货”，跟我来…

6.2.1 安装Docker软件包

有关windows 7 下进docker环境的安装准备工作，请参照前面的详解内容逐步安装即可，这只简单个大家归纳下安装步骤和注意事项。

（1）下载docker 安装包

软件包下载地址：

（2）双击默认安装即可；（注意你如果已经安装了virtualbox,请卸载重启后在进行docker环境报的安装）

（3）启动docker环境，注意第一次启动的有关于“boot2docker.iso”的报错内容，具体操作参见章节3.4；

6.2.2 创建靶机容器

（1）Docker启动后,配置 git bash 客户端环境变量，具体内容参见章节4.3.2.1；

（2）拉取 samba 漏洞镜像

镜像拉取命令：docker pull medicean/vulapps:s_samba_1

本地镜像查询：docker images

（3）创建samba 漏洞环境容器，并设置好端口映射(具体相关命令解释参加章节5.1.4.2)

容器创建命令：$ docker run -d -p 445:445 medicean/vulapps:s_samba_1

容器查询命令：$ docker ps -a

注：由于镜像在官方站点，故下载的过程会非常慢，大家实验时请耐心等待（么办法就是这么蛋疼）。

6.2.3 配置virturlbox 端口转发

有关 445 端口的端口转发内容，请参见章节5.1.4.2 的小标题(2)。

6.2.4 samba 共享服务验证

最后手动访问下物理网卡的IP地址共享，测试下看是否可以正常访问共享目录。

**[![](https://p4.ssl.qhimg.com/t01e6beb31ecb1e5399.png)](https://p4.ssl.qhimg.com/t01e6beb31ecb1e5399.png)**

**6.3 MSF 攻击复现**

6.3.1 is_knonw_pipname.rb 攻击脚本下载

网上已经放出了针对CVE-2017-7494漏洞的攻击exp（is_knonw_pipname.rb）,我们直接将其现down下来，放到MSF框架的相应路径下即可。

（1）is_known_pipename.rb POC下载链接： 

[https://raw.githubusercontent.com/hdm/metasploit-framework/0520d7cf76f8e5e654cb60f157772200c1b9e230/modules/exploits/linux/samba/is_known_pipename.rb](https://raw.githubusercontent.com/hdm/metasploit-framework/0520d7cf76f8e5e654cb60f157772200c1b9e230/modules/exploits/linux/samba/is_known_pipename.rb)

（2）is_known_pipename.rb脚本存放MSF路径： 

/usr/share/metasploit-framework/modules/exploits/linux/samba/

对于 is_know_pipename.rb脚本，我们可以直接使用wget进行下载，然后使用命令cp复制到相应的目录。

[![](https://p1.ssl.qhimg.com/t01d1bf982153a15adf.png)](https://p1.ssl.qhimg.com/t01d1bf982153a15adf.png)

6.3.2 开启MSF框架，发起攻击

（1） 进入MSF框架

[![](https://p4.ssl.qhimg.com/t01e1325f75dba10fc1.png)](https://p4.ssl.qhimg.com/t01e1325f75dba10fc1.png)

（2） 调用攻击模块，设定攻击参数

[![](https://p5.ssl.qhimg.com/t0194d5daf57d8319b0.png)](https://p5.ssl.qhimg.com/t0194d5daf57d8319b0.png)

（3） 发起攻击，获取控制权限

[![](https://p4.ssl.qhimg.com/t018571d43d63e79edd.png)](https://p4.ssl.qhimg.com/t018571d43d63e79edd.png)

至此这边篇文档终于扫尾了，太不易了，各位看官如果下学习中遇到什么问题，或者对我的这文档有啥意见希望大家积极给我留言，愿与大家共同学习交流，一起进步…最后拜谢各位看官坚持看完这篇拙文，谢谢！！！

**<br>**

**七、学习参考与资源**

视频学习 

[https://yeasy.gitbooks.io/docker_practice/content/appendix/command/](https://yeasy.gitbooks.io/docker_practice/content/appendix/command/)

docker从入门到实践： 

[https://study.163.com/course/courseLearn.htm?courseId=1002892012#/learn/video?lessonId=1003326200&amp;courseId=1002892012](https://study.163.com/course/courseLearn.htm?courseId=1002892012#/learn/video?lessonId=1003326200&amp;courseId=1002892012)

网络互联知识 

[https://opskumu.gitbooks.io/docker/content/chapter5.html](https://opskumu.gitbooks.io/docker/content/chapter5.html)

网易蜂巢镜像中心 

[https://c.163.com/hub#/m/home/](https://c.163.com/hub#/m/home/)

doccloud镜像市场 

[http://hub.daocloud.io/](http://hub.daocloud.io/)

medicean漏洞镜像库 

[https://hub.docker.com/r/medicean/vulapps](https://hub.docker.com/r/medicean/vulapps)

 



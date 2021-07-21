> 原文链接: https://www.anquanke.com//post/id/246601 


# 基于Linux Namespaces 特性 实现的消音


                                阅读量   
                                **174490**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01747c68446c5948e5.jpg)](https://p1.ssl.qhimg.com/t01747c68446c5948e5.jpg)



## TL;DR
- 这不是什么新技术，仅仅只是一些利用。
- 这是一个减少攻击噪音的工具，但同时也会产生其他噪音，但收益大于支出，属于OPSEC一类。
- 使用Linux Namespaces 一部分特性，遇到了一些坑但有相应的解决方案。
- 主要的功能包括隐藏进程、隐藏文件、隐藏网络、清理痕迹，提供合理的SSH手法。
- 目前这还是个玩具
review by Explorer



## Linux Namespaces 简介

在早些时候通过[Exp](https://github.com/zh-explorer)的文章学习到过一点 Docker 底层运行的一些相关特性和机制

[Docker安全性与攻击面分析](https://mp.weixin.qq.com/s/BaeIGrBimww8SUtePDQ0jA)

那么文中有提到：

> Docker 使用了多种安全机制以及隔离措施，包括 Namespace，Cgroup ，Capability 限制，内核强访问控制等等。

其中得知

Linux Control Group （Cgroup）
- 更多偏向系统资源的约束
内核 Capabilities
- 更多偏向容器权限的约束
在看完文章后和Exp也讨论了（Exp yyds 强的可怕 ）同时产生了一个想法，如果我们可以将部分隔离技术带到 Redteam operation当中，应该可以实现不错的效果。Docker本身就有这让“我们”看不见容器内部发生的事情的特性，那么我们也可以反过来让宿(guan)主(li)机(yuan) 也看不到我们的操作。

所以我们需要了解哪些技术方便我们实现需求，每一种机制都是Docker的组成要素，但我觉得 Namespaces 看起来是个另类的存在。

Linux Namespace 包含了大多数现代容器背后的一些基本技术。比如 PID Namespace 允许隔离进程之间的全局系统资源，这意味着在同一个主机上，运行的两个进程可以出现具有相同PID的情况，但你其实并不能在一个命名空间中通过PS看到这种情况，而是出现在不同PID 命名空间中。

以Docker 为例，当容器启动时会有一系列NS（Namespace 后续简称NS）随之创建。

而这里面就涉及到了 多种 NS 的使用，Linux kernel 为用户态提供了7种 NS 的内核接口使用。

[![](https://p2.ssl.qhimg.com/t01896e5217056f5cf3.png)](https://p2.ssl.qhimg.com/t01896e5217056f5cf3.png)

从描述信息来看，的确是一组很有趣的接口，有一些上层工具实现了部分系统namespace管理接口，比如 unshare, nsenter,ip等，从中我选择了两种 NS 来实现本文要叙述的隐匿实现。

Mount NS/ Net NS, 这两种 NS 最大程度可以帮助我们解决几个问题：
1. 对文件的隐藏
1. 对网络的隐藏
当然，有些师傅会觉得PID NS 为什么不是选择的部分了，关于这个问题，我们后面会知道答案。

举个例子

我们用unshare创建一个 /bin/bash 并让它进入一个新的Net NS,这个时候我们再看自己的网卡发现除了loopback什么也没有了，因为此刻这个bash和它的一系列子进程都在一个崭新的网络栈当中，已经和其他网络互相隔离。

[![](https://p5.ssl.qhimg.com/t016a9e845a1a6f41ae.png)](https://p5.ssl.qhimg.com/t016a9e845a1a6f41ae.png)

你可以在这里发现更多和Namespace相关的细节。

[namespaces(7) – Linux manual page](https://man7.org/linux/man-pages/man7/namespaces.7.html)

那么我们先来看一下最终实现的效果是如何的。



## Silencer Demo

[Silencer](https://asciinema.org/a/Sho4y0wmF1hrq5o71vPJwDRgR)

我们可以看到，Adapter代替了 SSH Client 命令帮助我们进行 SSH，并且我们会得到一个 完整的交互式Shell，在这个空间中，我们执行的操作会有隐匿的效果。当然你看到的这些，都是发生在拥有root权限下的。

其实 Adapter 是帮助我们把主程序 Silencer scp 到目标主机上并运行，我们通过流程图来看看发生了什么。

[![](https://p2.ssl.qhimg.com/t01d80b1668e512589d.png)](https://p2.ssl.qhimg.com/t01d80b1668e512589d.png)

你会看到，当Silencer被传输到目标主机后，会发生一系列调用。
<li>Adapter 会去调用Silencer 并执行相关功能。<br>[![](https://p5.ssl.qhimg.com/t01627af8af7a035f3d.png)](https://p5.ssl.qhimg.com/t01627af8af7a035f3d.png)
</li>
我们进一步看看到底做了什么，这边不会将太多源码的实现，主要以实现思路为主，因为首先代码能力不好，其次实现方式也有很多。

在这之前我们简单看看在Golang中如何去使用NS，你可以在Google上搜索到大量资料。Golang 为我们提供了操作NS的一部分实现接口。

需要使用系统调用（syscall）去完成，简单来讲就是程序直接像内核发起请求接口的过程，比如访问硬件资源，文件系统，创建进程等。

> [https://golang.org/pkg/syscall/](https://golang.org/pkg/syscall/)

这个包，就是Golang官方便编写的标准库 – syscall,已经为我们封装好很多实用接口，比如 syscall.Unshare、syscall.Mount、syscall.Readlink等。 在前面提到的 unshare -n /bin/bash命令中，unshare 实际是使用 Clone()系统调用， 并传递CLONE_NEWNET来完成NetNS的创建,当然可以接受多个CLONE属性。Clone 可以帮助我们创建一个带有隔离属性的进程。

unshare(CLONE_NEWNET)

在Golang中我们可以使用 syscall.SysProcAttr struct 来为我们创建的程序带有相关属性。

[![](https://p5.ssl.qhimg.com/t0181e85bb30ddbdec5.png)](https://p5.ssl.qhimg.com/t0181e85bb30ddbdec5.png)

在结构体中，我们看到了 Cloneflags并且说明 Flags for clone calls (Linux only)。

那么我们在创建进程的时候就可以使用它来帮助我们附加各种NS属性。

举个例子

[![](https://p3.ssl.qhimg.com/t0141201137d2c87f6d.png)](https://p3.ssl.qhimg.com/t0141201137d2c87f6d.png)

如果你想设置多个NS flags 可以这样写。

[![](https://p0.ssl.qhimg.com/t01bdc73b9546ef10a9.png)](https://p0.ssl.qhimg.com/t01bdc73b9546ef10a9.png)

最后达到的效果就是：

[![](https://p3.ssl.qhimg.com/t011e916f42d4a38505.png)](https://p3.ssl.qhimg.com/t011e916f42d4a38505.png)

当进入 New UTS Shell 之后我们修改hostname是不会影响到外界。

通过readlink，我们也可以发现 UTS 的确不一样了。

[![](https://p4.ssl.qhimg.com/t01d14879684e8a78d7.png)](https://p4.ssl.qhimg.com/t01d14879684e8a78d7.png)

这是使用 CLONE_NEWUTS带来的效果，有了这些基础就会使用其他NS，后续的代码就和搭积木差不多了，就是调用各种系统调用和处理相关逻辑即可。



## init (初始化环境)

这里列举一下，在实现init一共做了哪些事情,以及为什么。这仅仅是我这里的做法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015697706a3e5237dc.png)



## 建立隐藏挂载据点

首先我们建立一个隐藏挂载点，我们不需要将整个文件系统隔离，你可以选择任何一个存在的文件夹来做这个操作。目的是为了在此文件夹上设立一个隐藏空间，和宿主机进行相互隔离。从而你可以在此放你任何想放的文件和工具以及运行日志。

[![](https://p0.ssl.qhimg.com/t01254df8243ba3e64f.png)](https://p0.ssl.qhimg.com/t01254df8243ba3e64f.png)

我们将一个 tmpfs 内存文件系统挂载在/tmp/rootfs 上。在执行这一步前，我们已经进入了新的Mnt NS。所以所有的挂载操作都不对外界产生影响。对于外界进程来说，/tmp/rootfs文件夹没有任何变化。



## 配置 resolv.conf 和 .bashrc

我们需要配置隔离空间内的一些基础环境，比如修改.bashrc 加入你想要的一些环境变量，修改resolv.conf是为了规避这种情况。

[![](https://p2.ssl.qhimg.com/t010793ce8789c2e1e7.png)](https://p2.ssl.qhimg.com/t010793ce8789c2e1e7.png)

感觉好像没啥，其实问题很大。

[![](https://p2.ssl.qhimg.com/t01e725c59eb77a0979.png)](https://p2.ssl.qhimg.com/t01e725c59eb77a0979.png)

当你在隔离空间内，由于是新的网络环境，这个时候是访问不到本地 systemd-resolve或其他本地DNS服务。产生的问题就是你无法进行域名解析，所以我们也需要对 resolv.conf 进行调整。

我们可以使用 Bind Mount 来帮助我们实现这一点.

> Creating a bind mount
If mountflags includes MS_BIND (available since Linux 2.4), then perform a bind mount. A bind mount makes a file or a directory subtree visible at another point within the single directory hierarchy. Bind mounts may cross filesystem boundaries and span chroot(2) jails.

通过man手册我们可以看到 bind mount 不光可以作用于文件夹，还可以作用于文件，利用 bind mount 将这两个文件复制到一个暂存点，然后再mount 到原有位置即可。这样对原文件的访问会实际访问我们的暂存文件。并且由于Mnt NS的隔离。Namespace外仍然为访问原来的文件。

以 resolv.conf 为例：

[![](https://p5.ssl.qhimg.com/t01ac1100e267182729.png)](https://p5.ssl.qhimg.com/t01ac1100e267182729.png)

需要设置的flag位就是 syscall.MS_BIND. 我们进行追加的目的是为了不影响原有配置，在部分场景下，这里原有配置里面可能配置了含有内网DNS Nameserver的情况。如果是这种情况，其实我们不操作resolv.conf也不会有太大问题。



## 建立netns网桥

正如你上面看到的，在你调用 CLONE_NEWNET 之后。你会得到一个新的网络空间，此时除了loopback interface 外你一张网卡也没有，更别谈进行网络通信了。所以我们接下去要看看网络问题如何解决。

[![](https://p2.ssl.qhimg.com/t018355d3f516b31d06.png)](https://p2.ssl.qhimg.com/t018355d3f516b31d06.png)

原图：[https://i.loli.net/2019/05/04/5ccda44d1f525.png](https://i.loli.net/2019/05/04/5ccda44d1f525.png)

根据现有资料我们可以知道，想要让容器内的进程和外界通信需要使用 bridge 网桥、以及虚拟网卡来实现通信。
- 在外界网络空间中创建网桥接口并分配IP
- 然后创建veth接口对（默认情况你使用ip命令创建的虚拟网卡也是成对出现的，一个被删除，另一个也会自动消失）
- veth的特点就是它类似一个队列，当流量从一端进入，就必定会从另外一端出去，根据这个特点，我们就可以将一端依附在全局命名空间brg接口上，另外一段依附在隔离空间的新Net NS上。
- 配置好路由以及转发
这些做完，就可以实现隔离空间像外界发起请求，产生通信的能力，好在以及有人实现了这部分代码。

[https://github.com/teddyking/netsetgo/blob/master/cmd/netsetgo.go](https://github.com/teddyking/netsetgo/blob/master/cmd/netsetgo.go)

[![](https://p4.ssl.qhimg.com/t014bddd46d296b86da.png)](https://p4.ssl.qhimg.com/t014bddd46d296b86da.png)

这是封装好的方法体，我们直接拿来用即可，需要注意的是，我们需要传入隔离进程的PID给接口。

[![](https://p4.ssl.qhimg.com/t01285138b04efe6f8b.png)](https://p4.ssl.qhimg.com/t01285138b04efe6f8b.png)

然后你就会发现 外部多了两张网卡，内部多了一张虚拟网卡，和流程图中的逻辑是一样的。



## 配置 iptables

在配置好NetNS网络后，还不完全够，我们还需要配置iptables 转发，因为在这个情况下，你还不能实现从隔离空间的通信到达宿主机之外的网络，因为缺少源地址转换这一层处理。

iptables -t nat -A POSTROUTING -s 10.10.10.0/24-j MASQUERADE

所以我们需要对nat表的POSTROUTING 链加一条转换地址伪装规则。

另外考虑到部分Centos派系的系统和实战情况下，有可能会出现

Forward链默认规则为DROP的情况，或者默认为ACCEPT情况，但是链第一条规则就DROP ANY的问题，我们还可以再添加一条Forward链的规则。

iptables -I FORWARD -j ACCEPT

让这条Any to Any 的规则插入到最顶部。

关于iptables部分目前用的是 exec 实现，你也可以考虑使用cgo去写，因为golang暂时没有发现一个对netfilter封装的像iptables那么好的库。考虑到向下兼容的问题，所以也不会去使用nftables。



## 配置 net.ipv4.ip_forward 转发

在做好iptables之后不要忘记对 net.ipv4.ip_forward内核选项进行修改 ，否则一样是无法达到转发的目的的。

你可以选择 自己写，也可以用一些现成的库，比如：[github.com/lorenzosaino/go-sysctl](http://github.com/lorenzosaino/go-sysctl)



## Persistent Namespaces

持久化的目的是为了方便我们在退出整个隔离环境后下次还能继续进入，在构思持久化 NS 的时候并没有想到很好的方法，就去网上看看并请教Exp，因为自己对整个NS体系的特性掌握的也不熟。

回过头来再看看unshare 的 man手册. 通过搜索关键字发现了相关方法。

[![](https://p1.ssl.qhimg.com/t01a0d9c000edd50bc1.png)](https://p1.ssl.qhimg.com/t01a0d9c000edd50bc1.png)

[http://karelzak.blogspot.com/2015/04/persistent-namespaces.html](http://karelzak.blogspot.com/2015/04/persistent-namespaces.html)

这篇文章很早也有提到。

通过阅读我们发现最关键的一个步骤就是

❯ unshare —uts=/root/ns-uts

所以我们来看看到底是如何实现的。通过最简单的 strace 我们就可以知道底层是如何调用的。

[![](https://p2.ssl.qhimg.com/t01f018a9acd55ed986.png)](https://p2.ssl.qhimg.com/t01f018a9acd55ed986.png)

这部分在源码里位置如下

[https://github.com/karelzak/util-linux/blob/master/sys-utils/unshare.c#L193](https://github.com/karelzak/util-linux/blob/master/sys-utils/unshare.c#L193)

我们发现在unshare 之后调用了一个关键call，就是mount。并且 flag 位设置的 是 MS_BIND 也就是bind mount。

原本情况如果你在主进程退出，相关的NS也会一并跟着销毁，但通过bind mount 持久化的 NS 文件，不会因为主进程退出而销毁，

[![](https://p0.ssl.qhimg.com/t0102c13ea9ac0e80bf.png)](https://p0.ssl.qhimg.com/t0102c13ea9ac0e80bf.png)

通过列出文件的inode号，我们发现的确是持久化成功了。相关实现代码和之前处理 resolv.conf 是一样的，这里就不在赘述。

但是处理持久化mnt也没那么简单，你会发现会返回错误 Invalid argument

❯ unshare —mount=/tmp/.ICE-unix/mnt

unshare:mount /proc/276532/ns/mnt on /tmp/.ICE-unix/mnt failed:Invalid argument

核心原因在于挂载点标志的问题，每个挂载点都有一个propagation type标志。

比如：
- MS_SHARED
- MS_PRIVATE
- MS_SLAVE
- MS_UNBINDABLE
问题原因和解决方案可以在这个issue中找到。

[unshare: Persisting mount namespace no longer working · Issue #289 · karelzak/util-linux](https://github.com/karelzak/util-linux/issues/289)

issue 中有提到，基于[systemd](https://wiki.archlinux.org/title/systemd)启动的系统默认是共享挂载的（可能是/，或其他挂载点并不一定全是）。而想要挂载 mntns 必须是在private filesystemd上（其他NS挂载暂时没发现啥问题）。因为我使用的开发系统是Ubuntu 20.04，默认走的是systemd（高版本Centos也迁移到了systemd），所以会产生这个问题。

[![](https://p5.ssl.qhimg.com/t017723c1201cb61495.png)](https://p5.ssl.qhimg.com/t017723c1201cb61495.png)

解决方案就是先建立一个private 挂载点，然后在里面进行持久化mntns。

[![](https://p1.ssl.qhimg.com/t01cc6fd815b9c1fafa.png)](https://p1.ssl.qhimg.com/t01cc6fd815b9c1fafa.png)

到此位置 init 的相关工作也就做的差不多了。



## nsjoin (进入Namespace环境)

再次进入隔离空间，也没有那么一帆风顺。

> nsenter – run program with namespaces of other processes

通过 nsenter 接口我们可以让当前进程进入指定的NS空间，其中用到的syscall 是setns。

[![](https://p3.ssl.qhimg.com/t01a93fb157451f778b.png)](https://p3.ssl.qhimg.com/t01a93fb157451f778b.png)



## Setns with net and mnt

用代码也很好实现,因为syscall 这个包里面没有直接实现setns（当然外部有），但也可以通过 RawSyscall 的方式通过call 调用号来实现。

[![](https://p5.ssl.qhimg.com/t0151ecd68bbd308259.png)](https://p5.ssl.qhimg.com/t0151ecd68bbd308259.png)

就在这个时候 对mnt的setns出现了问题（又是这该死的 invalid argument）。

❯ ./SetnstMntTest

[-]setns on mnt namespace failed:invalid argument

后来在 golang 的issue 也发现有人遇到过这个问题

[Calling setns from Go returns EINVAL for mnt namespace · Issue #8676 · golang/go](https://github.com/golang/go/issues/8676)

原因是因为go程序默认启动就以多线程的模式运行的，但是setns mnt不能在这种模式下工作，也不太清楚这个限制的原因。解决方案利用的Docker的办法：

[![](https://p4.ssl.qhimg.com/t01e5f21ee63023a072.png)](https://p4.ssl.qhimg.com/t01e5f21ee63023a072.png)

使用 cgo 来提前setns，这个时候 go 的runtime 并还没启动。所以我们可以在 golang 中使用 import “C”的方式来写C，解决这个问题。

[![](https://p3.ssl.qhimg.com/t01f866026d7aa6b83a.png)](https://p3.ssl.qhimg.com/t01f866026d7aa6b83a.png)



## Using busybox anti HIDS

关于Anti的部分现在做的还不算多，我先说一下这里使用busybox 的理由（也是Exp建议并制作的）。

为什么要使用busybox

使用busybox的首要考虑是为了对抗HIDS。HIDS的一个基本功能之一就是记录恶意的命令执行。有关这个功能的实现方式有很多种，在不考虑从ring0层面上进行监控的前提下，很多厂商都会使用修改bash程序，修改libc或者使用全局ld preload方式来监控程序对于命令执行函数(system, popen, execve)的调用。

常见HIDS进行命令监控的方法（不完全,来自网上的一些方法总结）：
- Patch bash/other shell
- PROMPT_COMMAND 监控
- 在ring3通过/etc/ld.so.preload劫持系统调用
- 二次开发glibc加入监控代码(据说某产品就是这么做监控的)
- 基于调试器思想通过ptrace()主动注入
- 遍历/proc目录，无法捕获瞬间结束的进程。
- Linux kprobes/uprobes调试技术，并非所有Linux都有此特性，需要编译内核时配置。
- 修改glic库中的execve函数，但是可通过int0x80绕过glic库，这个之前360 A-TEAM一篇[文章](http://mp.weixin.qq.com/s?__biz=MzUzODQ0ODkyNA==&amp;mid=2247483854&amp;idx=2&amp;sn=815883b02ab0000956959f78c3f31e2b&amp;scene=21#wechat_redirect)有写到过。
- 修改sys_call_table，通过LKM(loadable kernel module)实时安装和卸载监控模块，但是内核模块需要适配内核版本。
- ebpf yyds (目测是最理想的方法)
为了对抗ring3层面上的hook。我们就需要一个单独编译的，不依赖libc，并且全静态编译不调用外部命令执行方法的shell。

除此之外，考虑到部分hids除了hook bash之外，可能还会对一些常用的命令进行修改和检测。所以我们希望能有一个不依赖任何so库，只需要一个文件就能提供shell以及一些常用命令的工具。并且考虑到实际攻防中的网络情况。我们还希望这个文件的大小能够尽量的小。

这样的解决方案在IOT领域还是挺常见的。由于IOT设备的特殊性，上述要求也是IOT设备中对对于shell的常见要求。所以很自然的就可以想到，只要把IOT领域最常见的解决方案busybox稍微做一下定制。就能满足要求了。



## 定制busybox

使用busybox的另外一个好处就是支持定制。结合红队的常见需求，我们对busybox做了如下一些自定义的配置。
- FEATURE_SUID [=n]
出于安全考虑，busybox调用shell时默认会drop掉suid权限。这对红队没必要，很多时候还是个麻烦（需要额外调用setresuid）所以禁用
- FEATURE_PREFER_APPLETS [=y]
默认情况下，busybox的shell优先从环境变量PATH中寻找我们执行的命令。基于上一章的讨论，我们更需要busybox优先使用内建的命令。所以启用该选项
- STATIC [=y]
静态编译busybox。让其不依赖任何so库
- CROSS_COMPILER_PREFIX [=musl-]
我们使用musl-libc而不是常规的glibc编译。使用musl-libc的主要优势是能够显著的减少程序的体积。相比于臃肿的glibc来说，针对嵌入式设备准备musl更加的轻量。
- FEATURE_EDITING_SAVEHISTORY [=n]
我们并不希望shell记录任何历史
- 命令裁剪
默认busybox支持的命令太多了。许多命令并没有什么用。所以这里根据需要只保留了部分对红队有帮助的命令用以减少体积。
- 修改源码以支持任意文件名
默认情况下，busybox根据自身程序来判断执行什么命令。比如把程序命名成ls就执行ls，命名成wget就执行wget。其中特例是如果程序以busybox开头，则会根据命令行参数的第一项来执行对应命令。

但是上传的时候不能耿直的就叫busybox。基本的伪装还是要做的。所以就需要修改一点源码。需要修改 libbb/appletlib.c中的run_applet_and_exit函数。在程序根据自身文件名寻找applet失败的时候，转而使用第一个参数来寻找applet即可

最终编译出来的busybox经过upx压缩，大小在350kb左右。属于可以接受的范围。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c79280ce0200ca2f.png)

对于busybox内置的命令都使用本身来执行，如果没有再调用外部命令，默认情况下也不会记录各种 shell history，省去了你经常敲:

unsetPROMPT_COMMAND HISTORY HISTFILEHISTSAVE HISTZONE HISTORY HISTLOG;exportHISTFILE=/dev/null;

这里使用 go-bindata 的方法将 busybox 打包进自身然后释放到隔离空间内，然后运行，这样外面也是看不到的。



## 隐藏痕迹

### <a class="reference-link" name="Process%20Hide"></a>Process Hide

这是单独启动的一个子进程来完成的操作，目的是为了做进程隐藏，和一些擦屁股的事情。

这里用到的方法 —— 挂载覆盖/proc/pid 目录 ：

[Linux进程隐藏：中级篇 – FreeBuf网络安全行业门户](../articles/system/250714.html)

这是一种成本很低快速可完成的方法，但同时也很容易暴露。

这里回答之前的坑，为什么不使用PID NS来做进程隔离。要使用PID NS 我们需要一个新的rootfs，并且持久化的时候至少需要一个进程保持运行。一个最小的 tiny core rootfs,他的大小大概在16m左右（可进一步缩小）。

[![](https://p1.ssl.qhimg.com/t01b9e5908873b68249.png)](https://p1.ssl.qhimg.com/t01b9e5908873b68249.png)

但设想一下，如果我们深处多层代理的情况要传输包括自身在内接近20m的文件到target主机上，这可能是件很糟糕的事情，所以目前我先用这种方式代替，后面想想方法再切换过去，但不得不说使用新的rootfs 是解决PID hide最佳方式。

代码依然是比较简单的。

[![](https://p4.ssl.qhimg.com/t01d95d66c687a0cc2f.png)](https://p4.ssl.qhimg.com/t01d95d66c687a0cc2f.png)

整个过程会在一个 go 协程内部不断循环，一旦检测到新的进程启动就会保姆级别帮助mount掉。检测方法很简单就是通过PPID来辨别是否属于其子进程。

### <a class="reference-link" name="Hide%20ass"></a>Hide ass

因为我们是使用 SSH terminal 全交互上目标主机的，所以这会有相应的会话记录产生，并被记录到Xtmp文件当中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015995f3c4b4b7b98e.png)

寻找过尝试在此过程中不记录这些信息但比较菜没能解决，后来还是通过简单直接的方式删除对应的日志来进行隐藏。

在 emp3r0r post-exploitation framework 中刚好有实现这部分的代码：

[jm33-m0/emp3r0r](https://github.com/jm33-m0/emp3r0r/blob/c2e5c483e4645958004fea40c1609620391957df/core/internal/agent/xtmp.go#L15)

但是在这作者写错了utmp的日志位置，这里应该是 /var/run/utmp。

xtmpFiles :=[]string`{`“/var/log/wtmp”,”/var/log/btmp”,”/var/log/utmp”`}`

并且作者使用的是字符串包含的方式来进行匹配删除，其实并没有去解析Xtmp二进制文件的各个位的含义，这样带来的问题就是无法精确控制你要删除的条目。

[![](https://p5.ssl.qhimg.com/t0170e624e559390fc0.png)](https://p5.ssl.qhimg.com/t0170e624e559390fc0.png)

但这些问题你可以通过匹配其他特征去解决，或者自行去解析每个bytes。

### <a class="reference-link" name="SSH%20Client"></a>SSH Client

这里写的Adapter其实主要在于 SCP Silencer 到目标主机上（我以为要把卢老板的代码删完，后来发现卢老板写的真香），并执行启动过程的自动化操作。其实你完全可以自己手工搞上去，然后在用标准ssh client 执行命令去启动Silencer（但不建议）。

目前这还是个玩具，还需要进一步改进，欢迎讨论更多降噪→消音→隐匿的手法。

完善后会同步到 [https://github.com/P1-Team/Silencer](https://github.com/P1-Team/Silencer)。



## Reference
<li>[Docker安全性与攻击面分析] [https://mp.weixin.qq.com/s/BaeIGrBimww8SUtePDQ0jA](https://mp.weixin.qq.com/s/BaeIGrBimww8SUtePDQ0jA)
</li>
- [namespaces-in-go] &lt;a href=”https://medium.com/[@teddyking](https://github.com/teddyking)/namespaces-in-go-network-fdcf63e76100″”&gt;https://medium.com/@teddyking/namespaces-in-go-network-fdcf63e76100
<li>[使用golang理解Linux namespace] [https://here2say.com/40/](https://here2say.com/40/)
</li>
<li>
[emp3r0r](https://zhuanlan.zhihu.com/p/387830848/edit)([https://github.com/jm33-m0/emp3r0r/blob/c2e5c483e4645958004fea40c1609620391957df/core/internal/agent/xtmp.go#L15](https://github.com/jm33-m0/emp3r0r/blob/c2e5c483e4645958004fea40c1609620391957df/core/internal/agent/xtmp.go#L15))</li>
<li>[Linux进程隐藏：中级篇] [https://www.freebuf.com/articles/system/250714.html](../articles/system/250714.html)
</li>
<li>[Linux 系统动态追踪技术介绍] [https://blog.arstercz.com/introduction_to_linux_dynamic_tracing/](https://blog.arstercz.com/introduction_to_linux_dynamic_tracing/)
</li>
<li>
[PROMPT_COMMAND](https://zhuanlan.zhihu.com/p/387830848/edit)([https://bzd111.me/2020/01/15/bash-or-zsh-log-commands.html](https://bzd111.me/2020/01/15/bash-or-zsh-log-commands.html))</li>
<li>[如何在Linux下监控命令执行] [https://mp.weixin.qq.com/s?__biz=MzUzODQ0ODkyNA==&amp;mid=2247483854&amp;idx=2&amp;sn=815883b02ab0000956959f78c3f31e2b](https://mp.weixin.qq.com/s?__biz=MzUzODQ0ODkyNA==&amp;mid=2247483854&amp;idx=2&amp;sn=815883b02ab0000956959f78c3f31e2b)
</li>
<li>[「驭龙」Linux执行命令监控驱动实现解析] [https://www.anquanke.com/post/id/103520](https://www.anquanke.com/post/id/103520)
</li>
<li>[namespaces(7) — Linux manual page] [https://man7.org/linux/man-pages/man7/namespaces.7.html](https://man7.org/linux/man-pages/man7/namespaces.7.html)
</li>
<li>[persistent namespaces] [http://karelzak.blogspot.com/2015/04/persistent-namespaces.html](http://karelzak.blogspot.com/2015/04/persistent-namespaces.html)
</li>
<li>[netsetgo] [https://github.com/teddyking/netsetgo/blob/master/cmd/netsetgo.go](https://github.com/teddyking/netsetgo/blob/master/cmd/netsetgo.go)
</li>
<li>[go-interactive-shell] [https://mritd.com/2018/11/09/go-interactive-shell/](https://mritd.com/2018/11/09/go-interactive-shell/)
</li>
- [https://github.com/karelzak/util-linux/issues/289](https://github.com/karelzak/util-linux/issues/289)
- [https://github.com/golang/go/issues/8676](https://github.com/golang/go/issues/8676)
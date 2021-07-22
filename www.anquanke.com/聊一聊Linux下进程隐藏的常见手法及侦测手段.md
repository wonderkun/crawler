> 原文链接: https://www.anquanke.com//post/id/160843 


# 聊一聊Linux下进程隐藏的常见手法及侦测手段


                                阅读量   
                                **442629**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01e215d998377bcd0e.jpg)](https://p2.ssl.qhimg.com/t01e215d998377bcd0e.jpg)

> 严正声明：本文仅限于技术讨论与学术学习研究之用，严禁用于其他用途（特别是非法用途，比如非授权攻击之类），否则自行承担后果，一切与作者和平台无关，如有发现不妥之处，请及时联系作者和平台

## 0x00.前言

进程隐藏是恶意软件隐藏自身痕迹逃避系统管理人员发现的常用伎俩之一，当然，安全防护人员有时候也会使用到，比如隐藏蜜罐中的监控进程而不被入侵者觉察等。笔者也曾在多次安全应急响应经历中遇到过多各式各样的进程隐藏伎俩，了解进程隐藏的常见手法及发现手段是每一位安全运维工程师所应掌握的知识点。本文抛砖引玉，浅谈我所了解的Linux下进程隐藏手段及发现技巧，也希望读者能够积极分享自己相关经验与技巧。



## 0x01.我所了解的 Linux下进程隐藏手段及侦测方法

Linux 下进程隐藏手法大体上分为两种，一种是基于用户态隐藏；一种是直接操控内核进行隐藏。

### <a name="%E4%B8%80%E3%80%81%E5%9F%BA%E4%BA%8E%E7%94%A8%E6%88%B7%E7%A9%BA%E9%97%B4%E8%BF%9B%E7%A8%8B%E9%9A%90%E8%97%8F%E6%89%8B%E6%B3%95"></a>一、基于用户空间进程隐藏手法

#### 1、偷梁换柱型

##### 1）隐藏原理

​ 道理很简单，通过替换系统中常见的进程查看工具（比如ps、top、lsof）的二进制程序，导致原先查看进程相关信息的工具（ps、top、lsof等）都被调包了，当然看不到

##### 2）防护手段

​ I、从干净的系统上拷贝这些工具的备份至当前系统，对比前后的输出是否一致，不一致，则说明被替换了

​ II、检测这些工具的hash值是否与系统初始化的时候值不一致，是，则说明被替换了

​ III、专业一点话，使用一些系统完整性检查工具，比如tripwrie、aide等

​ IV、部署主机入侵检查工具（比如ossec），监控系统文件是否被替换，如有替换，则会报警记录

#### 2、HooK系统调用型

##### 1）隐藏原理

先说下ps、top等工具的工作原理

以ps 工作原理为例说明这些进程信息查看工具的原理

我们知道/proc是一个虚拟文件系统，是VFS的一个实现形式，/proc中包含了内核信息，硬件信息，进程信息等，ps等工具就是通过分析/proc文件系统中进程相关目录的信息获取进程信息汇总。HooK系统调用型的进程隐藏方式都是通过拦截或者迷惑ps等工具从/proc获取分析结果的过程，而不是针对/proc/文件系统生成本身。

ps 首先会调用openat 系统函数获取/proc目录的文件句柄，然后调用系统函数 getdents 递归获取/proc目录下所有文件信息（包括子目录），然后开始open函数打开/proc/进程pid/stat,/proc/进程pid/status, /proc/进程pid/cmdline 文件开始获取进程信息，然后打印给你看

攻击者通过劫持getdents 等系统调用函数或libc中的readdir 函数，实现对特定进程名进程的隐藏，以达到进程隐藏目的

劫持getdents 等系统调用函数或libc中的readdir 函数等系统调用函数一般来说有3个途径

I、修改内核调用，比如getdents 的源码

II、修改libc库中readdir 函数的源码

III、利用环境变量LD_PRELOAD 或者配置ld.so.preload文件 以使的恶意的动态库先于系统标准库加载，以达到架空系统标准库中相关函数的目的，最终实现对特定进程的隐藏

这3个原理类似，III相对于I、II比较简单，在此以III为例进行演示（劫持libc 中的readdir函数）

演示（利用LD_PRELOAD这个环境变量进行进程信息隐藏），比如隐藏ping这个进程：

先在一个窗口执行ping

[![](https://p1.ssl.qhimg.com/t018145903b047d604a.png)](https://p1.ssl.qhimg.com/t018145903b047d604a.png)

在另外一个窗口加载恶意动态库，动态库源码中对指定进程信息进程了过滤

[![](https://p5.ssl.qhimg.com/t0173f1276647ec2016.png)](https://p5.ssl.qhimg.com/t0173f1276647ec2016.png)

[![](https://p1.ssl.qhimg.com/t01a2484d166c1ffbab.png)](https://p1.ssl.qhimg.com/t01a2484d166c1ffbab.png)

上文也提到这种HooK系统调用函数的进程隐藏方式只是hook了ps等工具从/proc 获取信息的过程，而没有修改/proc/文件系统本身，其实相关进程信息的内核映射还在/proc中

[![](https://p1.ssl.qhimg.com/t01f648b4b199eb5740.png)](https://p1.ssl.qhimg.com/t01f648b4b199eb5740.png)

自己写个python小工具，直接读取/proc中的内容，也能发现异常

其实ls 也是调用libc中的readdir函数，如果对上述恶意动态库进行修该也可以实现对ls命令的劫持。

不过对于直接使用cat读取文件（linux下什么东东都是文件）内容获取进程信息的方式，劫持libc的readdir函数是没用的，因为cat调用的是一系列lookup函数（需要对这一系列函数进行劫持，原理类似）

##### 2）防护手段

I、检查LD_PRELOAD环境变量是否有异常

II、检查ld.so.preload 等配置文件是否有异常

III、自己写个python小工具，直接读取/proc中的内容，对于ps等工具的结果，对不上，则存在被劫持可能

IV、使用sysdig（有开源版，可以监控ps等的调用过程，观察是否有恶意动态库被加载。strace有类似功能）或者prochunter（google 上search）

​ sysdig proc.name=ps

[![](https://p1.ssl.qhimg.com/t01526a5b4c63eaccc9.png)](https://p1.ssl.qhimg.com/t01526a5b4c63eaccc9.png)

#### 3、伪造进程名型

##### 1) 隐藏原理

在恶意代码中通过设置具有迷惑性的进程名字，以达到躲避管理员检查的目的

比如 [Tiny Shell文章](http://www.freebuf.com/sectool/138350.html) 中介绍的Tiny shell 这款工具通过在源码中设置PROCESS_NAME为bash，以使得其运行后的进程名显示为bash

[![](https://p3.ssl.qhimg.com/t013102333370d863fe.png)](https://p3.ssl.qhimg.com/t013102333370d863fe.png)

另：也可利用bash的特性来更换进程的名字

exec -a 更换后的进程名 原来的执行命令

比如exec -a sysdig proc.name=ps &amp;执行之后，进程名显示为bash proc.name=ps

[![](https://p5.ssl.qhimg.com/t01ab24bc069c255e5b.png)](https://p5.ssl.qhimg.com/t01ab24bc069c255e5b.png)

如果原来的执行命令没有参数，则非常具有迷惑性

##### 2）防护手段

找到可疑进程所在的/proc目录，查看exe的指向

[![](https://p5.ssl.qhimg.com/t01e01bd84f11b0bf00.png)](https://p5.ssl.qhimg.com/t01e01bd84f11b0bf00.png)<br>
可疑发现真正的进程是sysdig 触发的

#### 4、挂载覆盖型

##### 1）隐藏原理

利用mount —bind 将另外一个目录挂载覆盖至/proc/目录下指定进程ID的目录，我们知道ps、top等工具会读取/proc目录下获取进程信息，如果将进程ID的目录信息覆盖，则原来的进程信息将从ps的输出结果中隐匿。

比如进程id为42的进程信息：mount -o bind /empty/dir /proc/42

案例：[http://www.freebuf.com/articles/network/140535.html](http://www.freebuf.com/articles/network/140535.html)

##### 2）防护手段

cat /proc/$$/mountinfo 或者cat /proc/mounts 查看是否有利用mount —bind 将其他目录或文件挂载至/proc下的进程目录的

### <a name="%E4%BA%8C%E3%80%81%E5%9F%BA%E4%BA%8E%E5%AF%B9%E5%86%85%E6%A0%B8%E7%A9%BA%E9%97%B4%E4%BF%AE%E6%94%B9%E8%BF%9B%E8%A1%8C%E8%BF%9B%E7%A8%8B%E4%BF%A1%E6%81%AF%E9%9A%90%E8%97%8F%E7%9A%84%E6%89%8B%E6%B3%95"></a>二、基于对内核空间修改进行进程信息隐藏的手法

这一类的手法就比较高深了，基本上都算作rootkit了

#### 1、劫持VFS文件系统系列函数实现对/proc动态生成结果的干扰，从而实现对某些进程的隐藏。

我们知道/proc这个内存文件系统是VFS的一个实现，如果在VFS接口层就进行进程过滤的话，我们在/proc目录下根本找不到相关进程的目录信息，更别谈ps 之类工具可以获取了。VFS层中涉及到proc动态生成结果的有inode_operation 和 file_operations等系列函数集，通过劫持这些函数集，可以使得进程信息无法通过文件系统接口输出给proc

#### 2、劫持进程创建模块代码，根据条件设置选择是否隐藏进程

案例：[http://www.cnblogs.com/wacc/p/3674074.html](http://www.cnblogs.com/wacc/p/3674074.html)

大致的意思就是在Linux进程管理之task_struct结构体增加进程隐藏与否标记

进程创建代码模块中根据设置的进程隐藏比较选择是否隐藏进程，如果为隐藏标记，则删除/proc文件系统中该进程的相关目录项，直接在内核中就把指定进程给过滤了，用户态根本查不到

对于1）和2）这两种场景比较棘手，防护手段如下

I、查下内核是否被重新编译替换

II、lsmod是否有新内核模块加入

III、查看机入侵检查系统的相关告警



## 0x02. 总结

Linux下进程隐藏的手法不会仅限于本文提到的这些，本文提到也只是冰山一角，浅谈而已。笔者希望此文能引起更多人的关注与讨论，希望各位大牛多多分享自己的经验与奇淫技巧。笔者水平有限，文中定有不足之处，还望各位斧正。



## 0x03. 参考

[https://github.com/hschen0712/process-hiding](https://github.com/hschen0712/process-hiding)

[http://tcspecial.iteye.com/blog/2361998](http://tcspecial.iteye.com/blog/2361998)

[http://www.techweb.com.cn/network/system/2016-12-21/2457492.shtml](http://www.techweb.com.cn/network/system/2016-12-21/2457492.shtml)

[https://www.jb51.net/LINUXjishu/347787.html](https://www.jb51.net/LINUXjishu/347787.html)

[http://blog.chinaunix.net/uid-26585427-id-5077452.html](http://blog.chinaunix.net/uid-26585427-id-5077452.html)

[http://www.voidcn.com/article/p-yfrjbuvq-pz.html](http://www.voidcn.com/article/p-yfrjbuvq-pz.html)

[https://unix.stackexchange.com/questions/280860/how-to-hide-a-specific-process](https://unix.stackexchange.com/questions/280860/how-to-hide-a-specific-process)

[https://stackoverflow.com/questions/37641695/how-to-hide-change-name-processes-called-in-bash-script-from-ps](https://stackoverflow.com/questions/37641695/how-to-hide-change-name-processes-called-in-bash-script-from-ps)

[http://phrack.org/issues/63/18.html](http://phrack.org/issues/63/18.html)

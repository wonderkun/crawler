> 原文链接: https://www.anquanke.com//post/id/84866 


# 【技术分享】利用Dirty Cow实现docker逃逸（附演示视频）


                                阅读量   
                                **219850**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：paranoidsoftware
                                <br>原文地址：[https://blog.paranoidsoftware.com/dirty-cow-cve-2016-5195-docker-container-escape/](https://blog.paranoidsoftware.com/dirty-cow-cve-2016-5195-docker-container-escape/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t01418ead2c7d0de032.jpg)](https://p1.ssl.qhimg.com/t01418ead2c7d0de032.jpg)**



**翻译：**[**vector******](http://bobao.360.cn/member/contribute?uid=1497851960)

**稿费：120RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆<strong><strong><strong><strong><strong>[<strong>网页版**](http://bobao.360.cn/contribute/index)</strong></strong></strong></strong></strong></strong>**在线投稿**



**前言**

Dirty Cow漏洞是利用Linux内核在处理内存写时拷贝（Copy-on-Write）时存在条件竞争漏洞，导致可以破坏私有只读内存映射。而一个低权限的本地用户能够利用此漏洞获取其他只读内存映射的写权限，有可能进一步导致提权漏洞。

Dirty Cow自发布以来，影响的范围也越来越大。除了影响linux版本之外，近日来有安全研究人员表示也会影响android安全，而现在连docker都不能幸免。

<br>

**正文**

**逃逸**

相较于本地提权，更让我感兴趣的是这个漏洞在容器内核就像docker那种中的利用。

为了利用这个漏洞，我们需要共享所有进程中的资源。为了利用这个漏洞，我们需要找到一个突破点，linux有一个功能，"vDSO"(virtual dvnamic shared object),这是一个小型共享库，能将内核自动映射到所有用户程序的地址空间。听起来很有用？这个库之所以存在，是因为一些系统可以通过调用它来显著地提高整体性能，但是它也适合我们邪恶的需要。

现在，我们有了所有进程共享的library可以执行代码，接下来该怎么做？

**scumjr的dirtycow-vdso**

scumjr放出来一个[POC](https://github.com/scumjr)，利用dirty cow修改vDSO内存空间中的ckock_gettime()函数。该POC修改了这个函数的执行，所有进程调用ckock_gettime都会触发而不是仅仅是运行的进程。一旦竞争条件触发，shellcode执行后，它就会给你一个root权限的shell。  

我在aws上搭建了一个测试环境，在亚马逊上利用ami-7172b611镜像创建一个实例，以我的做例子，我运行的内核是4.4.19-29.55.amzn1.x86_64，但是所有存在漏洞的内核都能满足要求。

创建容器的Docker files和部署scumjr的exploit都上传到了[github](https://github.com/gebl/dirtycow-docker-vdso)上。

**演示视频**



视频首先显示的是EC2实例中操作系统的版本和docker的版本。然后他开始启动一个容器并运行一个shell。在容器中，我编辑payload，将ip改为容器的ip，编译，运行。一旦回连成功，使用id命令可以看出我是root用户，而且能看到容器外宿主机的文件。

我对证实docker逃逸其实很简单非常感兴趣，因为我认为很多人高估其中的技术难度。

内核漏洞虽然比用户权限提升漏洞更稀有，但是不是没有例子、不能被理解。即使是因为内核特性，使得容器的隔离变为可能，我们也可以通过内核漏洞来绕过它。

还有许多使用不同策略的POC exploit值得一看，你可以在github上看到完整的列表 [https://github.com/dirtycow/dirtycow.github.io/wiki/PoCs](https://github.com/dirtycow/dirtycow.github.io/wiki/PoCs)

**vDSO背景**

vDSO是一个优化性能的功能。在vDSO的[帮助页面](http://man7.org/linux/man-pages/man7/vdso.7.html)上以gettimeofday为例进行说明，gettimeofday经常被用户空间的程序和C语言库调用。试想一下，如果一个程序需要立即知道当前的时间，就会频繁的进行定时循环或者轮询。为了减少开销，而且这不是私密信息，所以，它可以轻易并安全地在所有进程中共享。内核就需要负责把时间放在一个所有进程都能访问的内存位置。于是，通过在vDSO中定义一个功能来共享这个对象，让进程来访问此信息。

通过这种方式，调用gettimeofday的花销就大大降低了，速度也就变得更快了。

**漏洞细节**

这个漏洞利用了一个可以映射到所有进程并包含了经常被调用的函数的共享内存块。这个exploit利用dirty cow将payload写到vDSO中的一些闲置内存中，并改变函数的执行顺序，使得在执行正常函数之前调用这个shellcode。

shellcode初始化时会检查是否被root所调用，如果是，就继续，否则返回并执行clock_gettime定期函数。然后，它会检查文件/tmp/.X的存在，如果存在，函数就知道自己已经是root权限。接下来，shellcode会打开一个反向的tcp连接，为shellcode中编码的ip和端口地址提供一个shell。

默认情况下，这是在本地连接，但是我们可以根据自己的需要来修改。shellcode中的17，18行可以修改我们需要的ip和端口，例子如下：



```
IP equ 0x0100007f 
PORT equ 0xd204
```



**更新**

现在有一个更新，你可以在命令行中以"ip:port"的格式来输入IP和端口，这远比修改代码来得轻松。

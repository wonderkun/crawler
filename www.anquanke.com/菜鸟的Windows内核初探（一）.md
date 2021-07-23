> 原文链接: https://www.anquanke.com//post/id/205867 


# 菜鸟的Windows内核初探（一）


                                阅读量   
                                **312681**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01335fe12bff890c38.jpg)](https://p2.ssl.qhimg.com/t01335fe12bff890c38.jpg)



## 0、前言

因为一些原因需要对《漏洞战争》中的某些漏洞进行复现，这个漏洞在书中9.6节。泉哥太过牛逼，我这只菜鸟还是跟不上泉哥的思路，于是挣扎了很久，参阅了很多其他资料，费劲千辛万苦终于算是比较粗浅的了解了这个漏洞的原理以及利用的方法。作为第一次研究windows内核，还是想分享一下过程中的坑点，希望其他人可以少浪费点时间。



## 1、环境配置

### <a class="reference-link" name="1.1%20%E5%AE%9E%E9%AA%8C%E7%8E%AF%E5%A2%83"></a>1.1 实验环境

windows 7 sp1 x86家庭普通版、windbg、VirtualKD-Redux、VS 2010

### <a class="reference-link" name="1.2%20windbg%E7%AC%A6%E5%8F%B7%E8%A1%A8%E9%85%8D%E7%BD%AE"></a>1.2 windbg符号表配置

对于windows内核的相关调试，个人感觉最好用的就是windbg。毕竟windows是不开源的，很多东西无法从源码中获得，就需要间接获取。因为windbg是微软自己开发的调试器，很多内核相关的数据结构可以由windbg获取（**用微软打败微软**）

而为了能够很好的进行调试，获取相关系统的符号表就显得尤为重要，不然分析一个驱动文件，都是诸如sub_xxxx之类的函数，看的头疼。这里提供两种方法进行获取符号表，其中第一种方法对于新版本的windows是不可行的，但是对于文章中的系统还是可行的。

#### <a class="reference-link" name="1.2.1%20%E7%A6%BB%E7%BA%BF%E5%AE%89%E8%A3%85"></a>1.2.1 离线安装

第一种就是离线方法。的确目前来说微软是不支持离线获取符号表的，但是总有一些大佬可以做到，还乐意分享出来。这里引用的是吾爱破解的某个大佬放出的离线包[https://www.52pojie.cn/thread-1146411-1-1.html](https://www.52pojie.cn/thread-1146411-1-1.html)<br>
找到对应版本的系统之后，下载安装。之后安装到本地某个路径下之后，在windbg的symbol path中导入

[![](https://p0.ssl.qhimg.com/t0131e39cabbce007b6.png)](https://p0.ssl.qhimg.com/t0131e39cabbce007b6.png)

之后reload之后就可以成功导入符号表

[![](https://p1.ssl.qhimg.com/t0187086b0f0366530d.png)](https://p1.ssl.qhimg.com/t0187086b0f0366530d.png)

#### <a class="reference-link" name="1.2.2%20%E5%9C%A8%E7%BA%BF%E8%8E%B7%E5%8F%96"></a>1.2.2 在线获取

但是说实话，离线安装的限制太多了。基本不提倡使用，一般来说都是在线获取。在线获取网上很多，但是很多文章都忽略了一个很重要的问题就是——科学上网。<br>
并不是说一定要科学上网，还可以通过配置环境变量等方法获取，但是比较繁琐。一次科学上网之后会在本地目录下缓存相应的符号表，之后就可以直接访问本地的了。不需要再科学上网了。（在线的教程比较多，这里就不详细说了）

### <a class="reference-link" name="1.3%20%E5%8F%8C%E6%9C%BA%E8%B0%83%E8%AF%95"></a>1.3 双机调试

对于windows内核漏洞调试来说，蓝屏是常态，所以对于可能使系统崩溃的漏洞来说，本地内核调试是不方便的，最好的就是使用双机进行调试。这里着重说一下我的环境：**物理机是wind10、vmware 是15.5**（至于为什么要强调环境，主要是大佬们的博客在这方面基本不讲，以至于我们这些萌新复现的时候就会踩很多的坑）

双机调试有两种方法，一种是使用windbg自带的串口通信（没试过，但是可以参考某位大佬：编程难的博客：[https://bianchengnan.gitee.io/articles/vmware-vs2019-win10-kernel-debug-setup-step-by-step/）](https://bianchengnan.gitee.io/articles/vmware-vs2019-win10-kernel-debug-setup-step-by-step/%EF%BC%89)

这里我采用是一种名叫VirtualKD的工具，github上可以下载。使用方法如下：

根据系统版本下载对应的VirtualKD，直接运行exe文件，会自动解压

[![](https://p4.ssl.qhimg.com/t0146431ea07d8a5b0b.png)](https://p4.ssl.qhimg.com/t0146431ea07d8a5b0b.png)

将target文件夹移到需要调试的虚拟机中

[![](https://p3.ssl.qhimg.com/t01a4a799b95706d9c5.png)](https://p3.ssl.qhimg.com/t01a4a799b95706d9c5.png)

运行文件夹中的vminstall.exe

[![](https://p5.ssl.qhimg.com/t01bdfe864290e95a67.png)](https://p5.ssl.qhimg.com/t01bdfe864290e95a67.png)

点击install，在弹出的窗口中选择是，实现虚拟机重启

[![](https://p1.ssl.qhimg.com/t0199ca911b31506403.png)](https://p1.ssl.qhimg.com/t0199ca911b31506403.png)

[![](https://p5.ssl.qhimg.com/t01cd91753d8201c674.png)](https://p5.ssl.qhimg.com/t01cd91753d8201c674.png)

在实体机中运行vmmon.exe，同时重启的虚拟机选择系统调试

[![](https://p0.ssl.qhimg.com/t01b7af384180687dae.png)](https://p0.ssl.qhimg.com/t01b7af384180687dae.png)

可以看到此时这里并不能attach上虚拟机（标红，如果可以attach的话是标绿），查看日志信息，发现是版本的问题

[![](https://p1.ssl.qhimg.com/t01d092af585174ffa8.png)](https://p1.ssl.qhimg.com/t01d092af585174ffa8.png)

经过多方搜索，最终在Github上面找到了答案，原来是因为Vmware的版本过高（我这里是15.5）所以VirtualKD无法进行通信，所以attach不上。所以这里引出一个分支版本的VirtualKD叫做VirtualKD-Redux。这个同样也可以在Github上下载。安装方法相同，就是使用方法有一点不同。<br>
重启之后导入如下页面，选择“禁用程序驱动签名强制”，记住这里不要回车，而是要按F8，之后就可以看到VirtualKD成功attach上了

[![](https://p4.ssl.qhimg.com/t01f1f3438a3c889afa.png)](https://p4.ssl.qhimg.com/t01f1f3438a3c889afa.png)

[![](https://p4.ssl.qhimg.com/t01c4712cf4558734fe.png)](https://p4.ssl.qhimg.com/t01c4712cf4558734fe.png)

在使用之前还需要配置一下调试工具，也就是VirtualKD上面的debugger path。因为VirtualKD还提供其他调试工具来进行双机调试，所以这里为了使用windbg，需要在debug path中设置为windbg的路径。这里的windbg选择32位还是64位是根据物理机来选择的。

[![](https://p2.ssl.qhimg.com/t016c546eb852eb1068.png)](https://p2.ssl.qhimg.com/t016c546eb852eb1068.png)

到此为止，环境相关的配置就到这里了。



## 2、先验知识

为了更好的分析漏洞，一些需要提前知道的知识、数据结构、关键API就先在这里提到。

### <a class="reference-link" name="2.1%20Windows%E7%9A%84Path%E5%AD%90%E7%B3%BB%E7%BB%9F"></a>2.1 Windows的Path子系统

这个PATH系统的作用其实是一个相关于绘制图形曲线的系统。<br>
比如：直线、矩形、省略号、Arcs、多边形、基数样条、贝塞尔自由绘制曲线。在这个子系统中有几个类（Windows的本质其实就是类）。

重点关注下图的数据结构

[![](https://p2.ssl.qhimg.com/t01e1783be47add44ec.png)](https://p2.ssl.qhimg.com/t01e1783be47add44ec.png)

**PATHRECORD** 结构是 path 子系统主要操作的结构，对其直线化操作就是对 PATHRECORD 操作。PATHRECORD 结构构成了一个双向链表，pprnext,pprprev 分别为前后项指针，flags 为 类型比如像 PD_BEZIERS（贝塞尔曲线）。Count 为点的数量。POINTFIX 记录了各种坐标点。

**PATHALLOC** 是分配 PATHRECORD 的容器。当需要新建一个 PATHRECORD 时候，首先从 ppachain-&gt;pprfreestart 指向 的 地址 开 始 ， 判断该 PATHALLOC 是否 还有空 间 分配 一个 PATHRECORD，若有则以 pprfreestart 指向的地址分配新 PATHRECORD，ppfreestart 指针向下移 动；若空间不够，则分配一个新的 PATHALLOC，链入 ppachain 指向链表的链表头，再从新建 的 PATHALLOC 里的 pprfreestart 开始分配内存。由此可见，系统分配 PATHRECORD，实际上 是通过 PATHALLOC 结构实现的。ppanext 后向指针，pprfreestart 指向当前 PATHALLOC 内的空 闲空间。siztPathAlloc 是 PATHALLOC 的大小。当然 PATHALLOC 还有一些非常关键的静态数据 成员，比如 freelist,cFree 等。

**PATH** 结构主要被用在 EPATHOBJ 类中，这个类实现了一些操作 path 的函数，ppachain 指向了 PATHALLOC，pprfirst 指向第一 个 PATHRECORD，pprlast 指向最后一个。漏洞触发 的关键函数 pprFlattenRec 就在这里实现的。

### <a class="reference-link" name="2.2%20HALDISPATCHTABLE"></a>2.2 HALDISPATCHTABLE

简单来说，这实质就是一个函数指针，不过是运行在**内核态**的指针。形象的说是一个表，在不同偏移位置代表的是不同的函数。这里主要用到的是偏移量为4的HalQuerySystemInformation

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0152dbd41bd973a221.png)

通过MSDN也可以知道这个函数的功能。这个函数就是去读取MCA banks’状态的寄存器。（MCA——-Machine Check Architecture）。<br>
对于这个功能不需要关系，但是最重要的是可以通过这个函数作为跳板，从用户态进入内核态，最终达到提权的效果

### <a class="reference-link" name="2.3%20NtQueryIntervalProfile"></a>2.3 NtQueryIntervalProfile

在EXP中使用到了这个函数。通过研究其调用工程，可以知道大佬的高明之处。

首先这个函数的功能其实并没有什么。主要就是返回当前为给定配置文件源设置的配置文件间隔。这个函数的确没有什么作用，但是在内部调用的其他函数就不一样了。

通过反汇编可以知道在其内部调用了KeQueryIntervalProfile

[![](https://p2.ssl.qhimg.com/t01dc5edfdcd792a250.png)](https://p2.ssl.qhimg.com/t01dc5edfdcd792a250.png)

反汇编KeQueryIntervalProfile，发现最后会调用HALDISPATCHTABLE偏移4的函数，在上文中提到是HalQuerySystemInformation。那么利用思路就比较清晰了。<br>**如果能够将shellcode的地址覆盖到HALDISPATCHTABLE偏移量为4的地方。那么在系统调用NtQueryIntervalProfile就可以在内核态中执行我们的shellcode了。**

[![](https://p4.ssl.qhimg.com/t01438c452d03d109df.png)](https://p4.ssl.qhimg.com/t01438c452d03d109df.png)

### <a class="reference-link" name="2.4%20Ring%E6%9C%BA%E5%88%B6"></a>2.4 Ring机制

Intel的x86处理器是通过Ring级别来进行访问控制的，级别共分4层，从Ring0到Ring3（后面简称R0、R1、R2、R3）。R0层拥有最高的权限，R3层拥有最低的权限。按照Intel原有的构想，应用程序工作在R3层，只能访问R3层的数据；操作系统工作在R0层，可以访问所有层的数据；而其他驱动程序位于R1、R2层，每一层只能访问本层以及权限更低层的数据。这样操作系统工作在最核心层，没有其他代码可以修改它；其他驱动程序工作在R1、R2层，有要求则向R0层调用，这样可以有效保障操作系统的安全性。但现在的OS，包括Windows和Linux都没有采用4层权限，而只是使用2层——R0层和R3层，分别来存放操作系统数据和应用程序数据，从而导致一旦驱动加载了，就运行在R0层，就拥有了和操作系统同样的权限，可以做任何事情，而所谓的rootkit也就随之而生了。

### <a class="reference-link" name="2.5%20Windows%20token%E6%9C%BA%E5%88%B6%E4%B8%8E%E5%AE%89%E5%85%A8"></a>2.5 Windows token机制与安全

访问令牌(access token)主要负责描述进程或线程的安全上下文。这包括关联的用户、组和特权。基于这些信息，Windows内核可以根据进程请求的特权操作做出访问控制决策。令牌通常与特定的进程或线程相关联，它们是内核对象。在用户空间中，它们由一个句柄唯一标识。<br>
有两种主要的令牌;主要令牌和模拟令牌。Windows中的所有进程都有一个与它们相关联的主令牌。它们规定了相关进程的特权。创建新流程时，默认操作是让子进程继承与其父进程关联的主令牌。<br>
Windows是一个多线程操作系统，一个进程总是至少有一个相关的线程。默认情况下，线程将使用主令牌，在与其父进程相同的安全上下文中进行操作。然而，Windows也使用了模拟的概念，它允许一个线程临时模拟一个不同的安全上下文，如果给它一个不同的访问令牌的话。这通常使用模拟令牌执行。<br>
在系统的正常操作期间，根据服务器的功能及其当前的使用环境，会出现各种各样的令牌。如果系统被破坏，那么可以通过使用这些令牌来实现某种形式的权限升级，这取决于对系统的访问级别。这种升级通常分为两种主要形式:域特权升级和**本地特权**升级。<br>
因为这个漏洞与本地提权有关，所以只介绍相关概念。如果攻击者破坏了低特权服务，则最有可能发生这种情况。允许客户端通过Windows身份验证进行连接的服务通常会获得对客户端模拟令牌的访问权。服务客户端的线程通常会使用它来模拟客户端的安全上下文。如果连接的客户端是管理员，则攻击者可以使用此令牌升级他们在系统上的特权，以获得管理访问权。<br>
令牌本质上是内核数据结构。在用户空间中，使用句柄引用令牌。然后可以将这些句柄传递给相关的Windows API调用，以便对所需的令牌进行操作。枚举系统上所有令牌的最全面的方法是枚举系统上的所有句柄，然后确定哪些句柄表示令牌。为了做到这一点，有必要使用由ntdll.dll导出的低层API调用。<br>
介绍完这个就要说到这个漏洞的提权机制了。**EXP是通过PsReferencePrimaryToken来获得系统的TOKEN和目标进程的TOKEN，之后利用子自定义的API——-FindAndReplaceMember,将进程的TOKEN替换为系统的TOKEN。达到本地提权的目的**

### <a class="reference-link" name="2.6%20%E7%9C%8B%E9%97%A8%E7%8B%97"></a>2.6 看门狗

看门狗其实就是一个可以在一定时间内被复位的计数器。当看门狗启动后，计数器开始自动计数，经过一定时间，如果没有被复位，计数器溢出就会对CPU产生一个复位信号使系统重启（俗称“被狗咬”）。系统正常运行时，需要在看门狗允许的时间间隔内对看门狗计数器清零（俗称“喂狗”），不让复位信号产生。如果系统不出问题，程序保证按时“喂狗”，一旦程序跑飞，没有“喂狗”，系统“被咬”复位。<br>**这个EXP中利用看门狗就是在遍历链表死循环的时候跳出，Patch上自己创建的ExploitRecord节点。**



## 3、漏洞成因分析

首先我们用IDA载入win32k.sys，搜索 EPATHOBJ::bFlatten这个函数，观察到它调用了EPATHOBJ::pprFlattenRec。这个就是漏洞的关键点

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b3e45af3fa960405.png)

在这个函数中又调用了EPATHOBJ::newpathrec

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0171e9a8e58ee5e435.png)

跟进EPATHOBJ::newpathrec发现其调用了newpathalloc

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0113c1852ef454c3ad.png)

接着就具体分析一下newpathalloc，在newpathalloc中有声明一个结构PATHALLOC，这个在上面也介绍过了。这个函数会优先从freelist空闲链表中找到可用的内存节点，以用于分配PATHRECORD结构。

[![](https://p0.ssl.qhimg.com/t013def18e97b98997e.png)](https://p0.ssl.qhimg.com/t013def18e97b98997e.png)

但是有一个问题就是在使用freelist之前并没有对从freelist获取的内存块中进行初始化，那么使用的时候就不知道这些内存块里存放着一些什么数据。这里就有可能被利用。在具体分析怎么利用之前，为了更好的分析，需要先对IDA的数据结构进行一些修改。在之前已经介绍过了PATHRECORD的结构了，但是IDA并不能很好的进行识别。所以这里需要我们手动进行修改。按shift+f1打开本地类型

[![](https://p0.ssl.qhimg.com/t0156de0976bc59ac47.png)](https://p0.ssl.qhimg.com/t0156de0976bc59ac47.png)

按insert添加自定义结构体PATHRECORD

[![](https://p4.ssl.qhimg.com/t01cf311e9af1a0a1f3.png)](https://p4.ssl.qhimg.com/t01cf311e9af1a0a1f3.png)

[![](https://p5.ssl.qhimg.com/t01646bf47cf38b774a.png)](https://p5.ssl.qhimg.com/t01646bf47cf38b774a.png)

之后重新进行反编译，可阅读性明显提高

[![](https://p2.ssl.qhimg.com/t01f030642b7a711566.png)](https://p2.ssl.qhimg.com/t01f030642b7a711566.png)

为了更好的理解漏洞的原因。接下来就从头开始走一遍。<br>
首先观察bFlatten，这个函数。这里其实是在遍历链表，如果遍历到的PATHRECORD节点的flags有0x10的属性（代表贝塞尔曲线），则对其进行pprFlattenRec操作。

[![](https://p5.ssl.qhimg.com/t0190ff565e0f3c0a56.png)](https://p5.ssl.qhimg.com/t0190ff565e0f3c0a56.png)

[![](https://p2.ssl.qhimg.com/t015861151d964184d2.png)](https://p2.ssl.qhimg.com/t015861151d964184d2.png)

之后进入pprFlattenRec进行分析，这个函数可以分为几个部分进行分析

首先是第一部分通过调用newpahrec创建一个新的PATHRECORD节点

[![](https://p3.ssl.qhimg.com/t01934e1e905df5d6a9.png)](https://p3.ssl.qhimg.com/t01934e1e905df5d6a9.png)

第二部分就是对new_pathrecord的某些成员变量进行赋值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a2d954d62ee31707.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0198174fb97b1eaef5.png)

第三部分就是将新赋值完的节点前向节点加入链表中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018b91ad8d97986d43.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014af21f054bede337.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019b15618e9e89f49e.png)

第四部分是跟贝塞尔曲线有关的代码，下文就统称flatten

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017bc71efa49441892.png)

第五部分是新节点的后向节点链入链表

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0132dce545e51c1b44.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010755216294b42587.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01099276ba18b65074.png)

从这几步来看，好像新生成的这个节点初始化也很好。那么问题出在哪里呢？在以上几步的分析除了第四步以外，其余的分析都比较充分了，那么第四步是否有问题呢？咱们回去看之后发现，的确有点问题，在代码中又调用了一次newpathrec

[![](https://p3.ssl.qhimg.com/t010b0628eb301fff3e.png)](https://p3.ssl.qhimg.com/t010b0628eb301fff3e.png)

[![](https://p2.ssl.qhimg.com/t0127c2507510f15857.png)](https://p2.ssl.qhimg.com/t0127c2507510f15857.png)

那这里到底有什么问题呢？仔细看代码会发现，如果这里创建不成功的话，那么会直接return 0，那么后续节点也就无法链入链表中。

[![](https://p5.ssl.qhimg.com/t01085cd9675d5a0342.png)](https://p5.ssl.qhimg.com/t01085cd9675d5a0342.png)

**总的来说就是这个漏洞的根源在于win32k!EPATHOBJ::pprFlattenRec中对于贝塞尔曲线的一些操作对于内存分配失败的错误。如果新的节点freelist_node是从池中申请的，因为池管理器不会主动内存清零，则该节点的初始内容未知。如果在flatten阶段创建的阶段不成功，那么链表的形态就会被破坏——一个链表连了前向指针，后向指针next不知道要指向什么地方。这就是漏洞的成因。**



## 4、漏洞利用

首先声明一下，POC不是我写的，而是直接用大佬的。阅读完之后不得不感叹，大佬的思路清奇，首先在理论层面解释一些漏洞利用的方法。

### <a class="reference-link" name="4.1%20%E5%85%B3%E9%94%AE%E7%82%B9%E5%88%86%E6%9E%90"></a>4.1 关键点分析

根据上面的漏洞原理，知道要想成功利用漏洞有两个关键。**第一个就是内存池，为了触发在flatten阶段新建PATHRECORD失败，那么就是要让内存池的空间不够；第二个就是next指针的指向位置。**<br>
对于我来说思路很直接，介绍先创建尽可能多的PATHRECORD，让内存池空间不够，之后让next指针指向用户可控制的缓冲区内存。那么设新建多少个PATHRECORD才能把内存池的空间耗尽呢？内存地址改如何设置呢？其中有很多细节需要深究。因为地址设置的不好就只能把程序搞崩，设置的好就能像大佬们一样啊提权。

首先是内存消耗的方法。这里大佬使用的是一种名叫CreateRoundRectRgn的方法。这个函数创建的一个带圆角的矩形区域。当然这不是唯一的方法，只要能够消耗内存都可以，但是对于最先发现的Tavis Ormandy，他认为这是最好的一种方法了。

[![](https://p4.ssl.qhimg.com/t01473dd65214c40d7b.png)](https://p4.ssl.qhimg.com/t01473dd65214c40d7b.png)

接下来就是next的指向问题了，从崩溃到提权都是有一个过程的，先来想想如何让系统崩溃。这个比较好想。**比如说先构造PATHRECORD这个节点，但是填充一些垃圾数据在里面，之后将这些节点压入PATHALLOC的内存池中——-池污染。**

这样在程序执行流程是这样的：**第一次到flatten阶段的时候会构建一个畸形的链表。第二次到flatten阶段的时候，会遍历这个畸形链表，之后就链到了什么不知名的内存地址。这样就会导致程序崩溃**

[![](https://p4.ssl.qhimg.com/t016c3fe519f192880d.png)](https://p4.ssl.qhimg.com/t016c3fe519f192880d.png)

仅仅是让程序崩溃还是不够的，最好是能够利用起来。于是乎就想到能不能在填充PATHRECORD这些节点的时候填充的不是垃圾数据，而是某个用户可控制的用户态的数据，之后再压入PATHALLOC的内存池中。这样在flatten阶段就会访问可控的ring3地址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e6b6a1ce337f63c1.png)

之后就到了最终阶段——-任意地址写。首先还是得介绍一下Tavis Ormandy最强的操作。在构造PATHRECORD点的时候，next不在填写一些垃圾数据，而是指向自己。这样会导致 win32k!EPATHOBJ::bFlatten() 遍历链表时产生死循环。只要节点不是贝塞尔曲线（flag!=PD_BEZIERS），那么死循环就会成立。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eb74c7df483a4790.png)

那么这个死循环有什么用呢？<br>**等。等到不死循环的条件出现**，而这不死循环的条件就是创建的新的节点是贝塞尔曲线的节点(flag==PD_BEZIERS)。这样EPATHOBJ::bFlatten 例程在循环到这个节点时将会以此节点为参数调用 EPATHOBJ::pprFlattenRec（这里新节点填充为CCCC是为了后面调试）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01add3a0698c1e832b.png)

### <a class="reference-link" name="4.2%20%E6%80%BB%E4%BD%93%E6%B5%81%E7%A8%8B%E5%88%86%E6%9E%90"></a>4.2 总体流程分析

接下来完整的走一遍这个利用的流程。

首先还是第一部分，通过调用newpahrec创建一个新的PATHRECORD节点。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0154e30b9b0000a781.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01eb5932c638463dc0.png)

第二部分就是对new_pathrecord的某些成员变量进行赋值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a85f7845c3f6b037.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d157a7d62adba809.png)

第三部分就是将新赋值完的节点前向节点加入链表中，因为ppr-&gt;prev这个时候已经被CCCC覆盖了，所以这里freelist_node-&gt;prev也为CCCC。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01401d42f919257339.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0169a410d49a450bf5.png)

还是这个部分，因为if条件肯定成立，那么就会执行freelist_node-&gt;prev-&gt;next = freelist_node这条语句。在上文的分析中知道,freelist_node-&gt;prev=0xCCCCC，那么freelist_node-&gt;prev-&gt;next就相当于[0xcccc+0]（next在PATHRECORD的偏移量为0）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cf9640d6d602dca0.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c696b52bfc9bdd51.png)

**这样总体流程就清楚了。也就是说将0xCCCCC替换成我们想要的地址，那么就可以实现我们想要的功能。**<br>
那么替换成什么值合适呢？这里就用到先验知识的HALDISPATCHTABLE+4的知识。比如说这里换成HALDISPATCHTABLE+4，如果有call [nt!HalDispatchTable+0x04] 的操作即意味着call到pprNew 处，因为（第一次）任意地址写入的是 pprNew 的基址。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01976f5a5491a9fa30.png)

但是还有一个参数的问题，如何取参数呢。大神真是一点空间都不放过。我们知道PATHRECORD在偏移为4的位置是prev指针，也就是我们任意地址写的位置，那么在0~3的偏移量之间还有4个字节，大神就打算构造一个jmp或者其他跳转语句到栈上去取参数（只要这个跳转语句为4个字节就好了）。不得不说大神就是大神



## 5、POC代码分析

此处分析的POC为《漏洞战争》配套资料中的POC。看雪论坛也有很多大佬发的自己写的POC（我是没有测试过的，不过敢发出来应该是有底气的）

首先是曲线的定义，这些可以在MSDN上找到

[![](https://p3.ssl.qhimg.com/t014c3ee540a5b6b6a8.png)](https://p3.ssl.qhimg.com/t014c3ee540a5b6b6a8.png)

接着是结构体的定义，我们知道需要自己创建一个PATHRECORN节点，所以这个结构的定义是必不可少的

[![](https://p0.ssl.qhimg.com/t01e987d8d279515599.png)](https://p0.ssl.qhimg.com/t01e987d8d279515599.png)

为了消耗内存池，这里的POC使用的是一种名叫创建大量圆角矩形区域（CreateRoundRectRgn），这样必不可少的就需要点来构造贝塞尔曲线

[![](https://p1.ssl.qhimg.com/t0169487349c5f904a0.png)](https://p1.ssl.qhimg.com/t0169487349c5f904a0.png)

接着是一个从来没见过的结构定义，在网上搜一下可以发现类似的定义。这个类的意思是当SystemModuleInformation这个类成功调用ZwQuerySystemInformation 或 NtQuerySystemInformation的时候在返回值的缓冲区开头将会生成这个类

[![](https://p1.ssl.qhimg.com/t015d408206feadf17e.png)](https://p1.ssl.qhimg.com/t015d408206feadf17e.png)

[![](https://p2.ssl.qhimg.com/t0184c8014816c71f6d.png)](https://p2.ssl.qhimg.com/t0184c8014816c71f6d.png)

[![](https://p3.ssl.qhimg.com/t011611b96bf5f41429.png)](https://p3.ssl.qhimg.com/t011611b96bf5f41429.png)

在它下面还有一个很类似的类。

[![](https://p0.ssl.qhimg.com/t0191b9cc3448bdf4f7.png)](https://p0.ssl.qhimg.com/t0191b9cc3448bdf4f7.png)

[![](https://p0.ssl.qhimg.com/t011321eb52c089a864.png)](https://p0.ssl.qhimg.com/t011321eb52c089a864.png)

接着就是一大段函数的声明，这里有一个比较不常见的类型FARPROC，它的定义：typedef (FAR WINAPI *FARPROC)();就是一个远过程函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a2861d5d9cfe4858.png)

稍微看一下这些函数的意思<br>
第一个函数NtQuerySystemInformation用来获得一些只在内核态的系统信息，所有的信息都被定义为SYSTEM_INFORMATION_CLASS类。而SYSTEM_INFORMATION_CLASS这个类也可以找到其定义，其中的SystemModuleInformation是我们要用的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016561eaffe08adcf2.png)

第二个函数NtQueryIntervalProfile在上面已经提到过了；<br>
第三个PsReferencePrimaryToken获取参数中给定进程的primary TOKEN。<br>
第四个PsLookupProcessByProcessId通过进程的进程ID，并返回一个指向进程EPROCESS结构的引用指针。EPROCESS结构式是一个不透明的结构，存在在ring0。但是可以在windbg使用本地内核调试查看它的内容

[![](https://p0.ssl.qhimg.com/t01fb932997b9cf2d58.png)](https://p0.ssl.qhimg.com/t01fb932997b9cf2d58.png)

第五个HalDispatchTable在先验知识里已经提到过了<br>
第六个HalQuerySystemInformation也在先验知识里提到过了<br>
第七个TargetPid是目标进程的ID<br>
第八个PsInitialSystemProcess是一个指向system进程的EPROCESS。所以同样可以用windbg本地内存调试查看

[![](https://p2.ssl.qhimg.com/t01d956b55248227480.png)](https://p2.ssl.qhimg.com/t01d956b55248227480.png)

接着就是FindAndReplaceMember函数，这个函数的注释很清晰了。因为在windows中QWORD指针是需要对齐的，所以可以使用低三位进行快速引用计数。匹配之后就替换新值。

[![](https://p0.ssl.qhimg.com/t01c952d1afb577960b.png)](https://p0.ssl.qhimg.com/t01c952d1afb577960b.png)

接下来分析Shellcode。思路是比较清楚的。第一个红框的内容先记下后面会用到。第二个红框就是获得当前目标进程的primary token和系统进程的primary token。之后调用自己写的FindAndReplaceMember，将目标进程的primary token替换成系统进程的。这也是先验知识里面提到的利用token提权的方法

[![](https://p5.ssl.qhimg.com/t01ebd77c9c7c9ac88d.png)](https://p5.ssl.qhimg.com/t01ebd77c9c7c9ac88d.png)

按照EXP的顺序理论上应该分析看门狗线程和HalDispatchRedirect。但是为了更好的理解它们，应该把三个节点介绍完。<br>
在POC中，主要是构造三个PATHRECORD。<br>**第一个是命名为PathRecord，这个节点的flag取为0，这样就会构成链向自己的无限循环**；<br>**第二个是用于退出的，命名为ExploitRecordExit**；<br>**第三个是用作攻击的，命名为ExploitRecord，它的prev指针将会指向HALDISPATCHTABLE+4的地方**。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f40c086a4a66f85c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016903d631da191e27.png)

节点二，可以看到有个奇怪的赋值，在代码中跟随可以发现一些端倪

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0113b174a2984e2c09.png)

这里是 DispatchRedirect的赋值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01eca96d2866104565.png)

继续跟随HalDispatchRedirect，发现它的定义。那这里到底是什么意思呢？0x40又代表什么呢？HalDispatchRedirect主要是用来产生一个stub地址表。0x40的偏移量是NtQueryIntervalProfile参数的位置。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019fa946a9b9e2e1f3.png)

但是还是不是很很明白有什么用，继续看源码。再回到DispatchRedirect赋值的地方，发现在它下面对Interval进行了赋值，赋值为ShellCode。

[![](https://p5.ssl.qhimg.com/t01923651148b4facb0.png)](https://p5.ssl.qhimg.com/t01923651148b4facb0.png)

那这个Interval有什么用呢。我们在代码中发现，Interval被用作NtQueryIntervalProfile的第二个参数。又因为先验知识里面分析过了<br>
nt!NtQueryIntervalProfile-&gt;nt!KeQueryIntervalProfile-&gt;call [nt!HalDispatchTable+0x4]。因此执行到stub地址的时候，ShellCode 函数的地址总是在栈上，而且只要这几个函数的参数不变，这个偏移也都不会改变，这里是[ebp+0x40]

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c29ce859b0131b31.png)

至于HalDispatchRedirect为什么这么多指令，并且还有inc eax这样的指令。主要是因为下面的节点也就是节点三：ExploitRecord.next= (PPATHRECORD) **DispatchRedirect。在 pprFlattenRec 返回后，会取到 ExploitRecord.next 作为下一个 pathrecord，若 ExploitRecord.next 地址未分配，肯定是各种异常。因此需要以**DispatchRedirect 为地址，分配内存，为了用户态能分配成功，这个地址必须比较合适才行，因此就用到了 inc eax，和 后面的 jmp [ebp+0x40]组成了地址。当然为了防止在 [ebp+0x40] 上内存分配失败， Tavis 又作了其他备选方案，就出现了后面的 inc ecx, inc edx, inc ebx, inc esi….分别为 41， 42，43….

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0133fd2b9f03ce239e.png)

节点三，可以看到prev指向HalDispatchTable的第二个值

[![](https://p0.ssl.qhimg.com/t0128d1f11593f13d4f.png)](https://p0.ssl.qhimg.com/t0128d1f11593f13d4f.png)

跟到HalDispatchTable[1]的定义,HalQuerySystemInformation这个函数上文已经提到了，就是进入内核态的一个关键

[![](https://p1.ssl.qhimg.com/t013d943466ce6a1fd1.png)](https://p1.ssl.qhimg.com/t013d943466ce6a1fd1.png)

这样就理清了三个节点的关系，用下面这张图更好的说明一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b360c4659063f56e.png)

接下来分析看门狗线程，看门狗线程中有两个比较重要的函数。第一个WaitForSingleObject是用来等待互斥体超时。我们知道在上面建立了PathRecord使得链表进入的死循环，所以这个时候程序会一直遍历链表，调用这个函数就可以在一定的时间后跳出，等待下一步操作而不是真正的死循环在那里。第二个函数InterlockedExchangePointer就是在中断死循环之后的后续操作，这里将PathRecord原先指向自己的next指针借助InterlockedExchangePointer这个函数指向ExploitRecord。便于接下来的攻击利用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015ab4d89679f82828.png)

用一张图来说明调用看门狗线程之后三个节点的情况

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015db8f518489b3473.png)

到这对三个节点的分析基本上就快结束了，再回过头看看这个有漏洞的代码，对三个节点之间的关系再进行一次整理。可以根据备注进行理解。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0109d318b54dc92289.png)

这样就能得到三个节点最终的关系了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e3a7178710261dac.png)

接下来就是分析主函数了，首先分析主函数中最简单的一部分就是消耗内存。POC<br>
是通过CreateRoundRectRgn来消耗大量内存。当然这不是唯一方法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0114de711cc6a284d6.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015356087f7e5bed3e.png)

在主函数的起始位置获取DLL中的函数，其中比较特备的就是Interval和SavedInterval，可以看到对Interval进行赋值的时候对Shellcode进行了强制转换，转换成立ULONG类型的指针。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d284d9a99fdaaa6d.png)

通过NtQuerySystemInformation获取SystemModuleInformation信息，SystemModuleInformation这个结构在上文中已经提到了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d7cd69419d1d8d45.png)

根据结构中的偏移量算出需要的信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01475ad588e8f6a0eb.png)

搜索一个返回指令

[![](https://p2.ssl.qhimg.com/t0120566dd4a79aff4a.png)](https://p2.ssl.qhimg.com/t0120566dd4a79aff4a.png)

保存分配的内存可用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f409cbcfd9bc2bde.png)

这里有几个操作，主要说下与攻击有关的。WaitForSingleObject，在POC的前面又创建一个互斥体，之后CreateThread使用看门狗线程，因为死循环需要一定的时间，当超过了一定时间之后，看门狗线程就开始工作，也就是上文提到的，运行完看门狗线程之后三个节点的关系

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c950992ee43e8f73.png)

开始将点进行贝塞尔曲线flatten

[![](https://p3.ssl.qhimg.com/t010c920474ec0d2fbe.png)](https://p3.ssl.qhimg.com/t010c920474ec0d2fbe.png)



## 6、POC代码调试

理解清POC的源码就要动手调一调才能更好的理解

先来验证一些这个漏洞的成因点，在这里运行poc.exe。因为这个漏洞是基于压力测试而发现的，需要将内存池中的空闲内存消耗干净才能触发漏洞，所以这里需要多运行几次。在这里使用双机内核调试，当系统奔溃的时候Windbg捕捉到了

[![](https://p3.ssl.qhimg.com/t01e0d17512362687e1.png)](https://p3.ssl.qhimg.com/t01e0d17512362687e1.png)

通过查看函数调用发现存在漏洞的函数与之前的分析一样，这就可以验证漏洞的成因确实是如上面分析的

[![](https://p5.ssl.qhimg.com/t0196b9d09a8e2884b6.png)](https://p5.ssl.qhimg.com/t0196b9d09a8e2884b6.png)

验证完漏洞之后在内存层面走一下这个过程。可以知道在POC中关键的就是BeginPath开始循环，所以就在BeginPath处下个延迟断点，至于为什么要下延时断点，主要是因为之前下bp断点失败，猜测是win32k.sys此时还未加载

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014e28e69e1a1e8f7e.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0108a15f60caa8920d.png)

运行之后windbg断在此处

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0164a1167c3043ebe6.png)

之后对freepathalloc下断点，运行几步走到这里。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01377712a7f77edb6a.png)

至于为什么要断在这里可以参照IDA（这里地址与IDA的地址不相同，但是偏移量相等，在IDA中freepathalloc的地址是BF877B4A，那是偏移0x41就是BF877B8B）.通过伪C代码可以发现，freelist会将节点（PATHRECORD）回收直接链入链表freelist中。于是乎断在这里就可以查看要链入链表的节点了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01927881c8d59e750a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d1533c17b695f13a.png)

因为这里是通过EAX传值，所以可以直接查看EAX的数据，通过对照PATHRECORD的数据结构的偏移量可以知道各个数值的含义

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ada4784cf68c45de.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010fdc7c2a6e4adf14.png)

分析完BeginPath接着分析PolyDraw，在NtGdiPolyDraw 下个断点。但是要跟到哪里呢？这个时候还得IDA来静态分析一把。经过一波跳转，到了之前分析过的newpathalloc

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015eb9b25834335986.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014ba7b356dca77269.png)

于是乎，在newpathalloc下断点然后运行起来

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0130273bd201274867.png)

之后继续运行，可以在IDA中查看PATHRECORD，通过IDA的分析知道需要运行到的位置，这里还是通过EAX来传值，所以我们可以运行到mov ecx,[eax]这条指令后查看eax的值，或者dec这条指令查看ecx的值，结果都是一样的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cd3db662818c621f.png)

这里有个值得注意的地方，就是这个PATHRECORD的next指针指向的就是自己。（观察ecx）

[![](https://p2.ssl.qhimg.com/t0182d7dbf1681c0fdd.png)](https://p2.ssl.qhimg.com/t0182d7dbf1681c0fdd.png)

之后回到createrec这个函数中，有一个bXformRound函数用作数据复制，可以跟到这个函数中去看看具体的参数数值。先对bXformRound下个断点。通过IDA分析可以知道进行数据复制的操作是在这个函数偏移1B的位置，所以运行到那里即可。但是在实际运行过程中发现运行到0x16的偏移位置其实就可以查看两个拷贝的参数内容了

[![](https://p4.ssl.qhimg.com/t010764dd9924e9c5a9.png)](https://p4.ssl.qhimg.com/t010764dd9924e9c5a9.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015525a78acf3c4cf7.png)

上图中的两个红框就是参数的地址，直接可以查看参数的内容，可以看到对于第二个参数里的数据内容比较杂乱，但是对于从ffa1208f开始的内容就是比较固定的，就是第一个参数左移4位的值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016e63080334a945f1.png)

[![](https://p3.ssl.qhimg.com/t0147a775e61c0e2cbc.png)](https://p3.ssl.qhimg.com/t0147a775e61c0e2cbc.png)

继续往下跟应该可以找到左移的操作指令

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014cd47db2d41bd184.png)

PolyDraw分析到这里就差不多了，接下来应该分析EndPath，还是先从IDA中来看比较方便一些。分析之后觉得这里面应该没有什么值得注意的地方

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d747736e3310a3cc.png)

接着就是FlattenPath这个会触发漏洞的函数了，但是因为这个漏洞是基于压力测试的，需要多运行几次，所以为了跟踪它，选择下一个条件断点。下断点的依据如下。因为绝对地址不大靠谱，所以这里选择相对偏离来下断点。

[![](https://p5.ssl.qhimg.com/t0132a2ba4aeb331b9a.png)](https://p5.ssl.qhimg.com/t0132a2ba4aeb331b9a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01291ed24c7315e0c2.png)

根据偏移下条件断点

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c2bac357dadb2c5b.png)

跑起来，断下。可以发现此时新建的PATHRECORD的值就是0x80000，记住此时的地址ffac3f54

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c140f4277ddf7a08.png)

之后按p开始跟，跟到这个函数运行结束的位置

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012e75e7ca273f76ac.png)

再跟一步就到了bFlatten这个函数，可以发现此时的PATHRECORD节点的next指针还是0x80000。并且可以发现此时的地址也是ffac3f54

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018f30f4104b29b49e.png)

（因为这个调试过程比较长，前面算是一次性调的，从这里开始算是第二次开始，但是基本思路是一样的。）这里可以看到PathRecord指向的就是自己。符合POC中的代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a54f745bfd4d1fb1.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0154633d21c9ea87ef.png)

但是如果继续运行就会报错

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011f77259e83eeced6.png)

再G运行一下系统就奔溃了，到此使得系统崩溃的POC分析完毕。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01eb1da06d7d286547.png)



## 7、漏洞补救

在正式补丁没有出来之前有几个临时方案。<br>
临时补丁方案 A：主动清零池中的数据<br>
优点：逻辑上容易想到；pprNew.next 如果为 NULL 意味着尾节点<br>
缺点：定位 freepathalloc 等相对复杂；PATHRECORD 链表其它节点丢失

临时补丁方案 B：Patch 池计数器比较代码，禁用池机制<br>
优点：不需要 Inline Hook，1字节热补丁<br>
缺点：PATHALLOC 池机制被禁用；PATHRECORD 链表其它节点丢失

正式补丁方案 A：重写错误处理代码<br>
恢复链表正确的形态

正式补丁方案 B：重写链表操作代码<br>
链表操作应保证原子性



## 8、漏洞回顾

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f8ec215b0d08bc76.png)



## 9、总结

这是本菜鸟第一次接触Windows内核的相关漏洞，虽然这个漏洞年代比较久远，但是作为一个菜鸟来说，体验感还是挺好的。

路漫漫其修远兮，吾将继续努力

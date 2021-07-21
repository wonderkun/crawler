> 原文链接: https://www.anquanke.com//post/id/86392 


# 【技术分享】EternalBlue Shellcode详细分析


                                阅读量   
                                **178134**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[]()

译文仅供参考，具体内容表达以及含义原文为准

 **[![](https://p3.ssl.qhimg.com/t01be6e2e2870e16c3f.png)](https://p3.ssl.qhimg.com/t01be6e2e2870e16c3f.png)**

****

译者：[Tmda_da](http://bobao.360.cn/member/contribute?uid=2920174360)

预估稿费：400RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**0x0 前言**



说来很惭愧，EnternalBlue 已经出来很久了，最近才开始分析，漏洞原理和环境搭建网上已经烂大街了，因此这篇文章只分析Shellcode，调试平台如下：

windows 7 sp1  en    32 位

Windbg

Eternalblue

Doublepulsar

Wireshark

断点方法是将Shellcode中的31c0修改为CCCC（int 3）后发送，成功断下来后再通过ew(fdff1f1) c031即可。该Shellcode 大致分为三段： 0x1，hook nt! kiFastCallEntry篇； 0x2， 主要功能篇；0x 3， 后门通信篇，下面来逐一进行介绍。



**0x1 Hook ntdll! kiFastCallEntry篇**



这部分代码功能比较简单， 但还是值得学习：首先是判断系统环境，作者用法比较巧妙，利用了x86和x64系统通过对二进制指令的解析不同来判断系统环境（64位环境没有调试，直接用IDA查看， 如下图。

[![](https://p0.ssl.qhimg.com/t01de52d6d6cb42e8f9.png)](https://p0.ssl.qhimg.com/t01de52d6d6cb42e8f9.png)

1.1   x86环境  

[![](https://p4.ssl.qhimg.com/t01571a82e9b0513197.png)](https://p4.ssl.qhimg.com/t01571a82e9b0513197.png)

1.2  x64位环境

可以发现同样一段二进制代码, 在x86环境下eax=1 ， x64环境下 eax = 0。 紧接着通过读取MSR的176号寄存器（放着nt! kiFastCallEntry函数地址）（这里还有简单的混淆），将其保存在Shellcode的末尾位置（Shellcode末尾空置了0x1d byte），然后再将第二段Shellcode的地址存放在MSR 176号寄存器中实现对nt! kiFastCallEntry函数的hook。

[![](https://p5.ssl.qhimg.com/t011785006bf02d0373.png)](https://p5.ssl.qhimg.com/t011785006bf02d0373.png)

1.3  简单混淆

[![](https://p3.ssl.qhimg.com/t0184f7def20f1d40cf.png)](https://p3.ssl.qhimg.com/t0184f7def20f1d40cf.png)

1.4  hook nt!kiFastCallEntry

[![](https://p1.ssl.qhimg.com/t013a193384a624f503.png)](https://p1.ssl.qhimg.com/t013a193384a624f503.png)

1.5 hook前的情况

[![](https://p4.ssl.qhimg.com/t015d36564af7ac5e75.png)](https://p4.ssl.qhimg.com/t015d36564af7ac5e75.png)

1.6 hook后的情况

为什么要hook kiFastCallEntry?

在Ring3应用程序需要调用ring0函数的时候， 会通过ntdll!kiFastSystemCall 函数，该函数的内容如下：

```
mov edx, esp
      sysenter
      ret
```

Ring3层最终通过 sysenter 调用内核函数 nt!KiFastCallEntry实现空间转换。因此只要存在用户空间需要调用内核函数，都会调用这个函数。



**0x2 主要功能篇**



首先是获取到上一段Shellcode功能中保存末尾的kiFastCallEntry实际地址，然后写入MSR的176号寄存器中，恢复kiFastCallEntry。

 [![](https://p3.ssl.qhimg.com/t01799aba57690717ed.png)](https://p3.ssl.qhimg.com/t01799aba57690717ed.png)

2.1  unhook KiFastCallEntry

接下来获取ntoskrnl.exe 的基地址，fs:[0x38] 指向_KIDTENTRY表结构的开始地址，也指向0号中断，将0号中断的ExtendedOffset 和Offset组合成地址，就是0号中断处理函数地址。而这个函数位于ntoskrnl.exe中，因此该空间在ntoskrnl.exe进程空间中，在这个地址对齐（&amp;0x00F000）处理后只需要每次减0x1000，然后比较前两位的PE(MZ)文件标识，最后一定能找到ntoskrnl.exe的基地址地址。

[![](https://p3.ssl.qhimg.com/t0130376d5b842a0fbe.png)](https://p3.ssl.qhimg.com/t0130376d5b842a0fbe.png)

2.2.  寻找ntoskrnl.exe基地址

[![](https://p0.ssl.qhimg.com/t010309fc8618dbea91.png)](https://p0.ssl.qhimg.com/t010309fc8618dbea91.png)

2.3  0号中断结构信息

    找到ntoskrnl.exe的基地址后，利用应用层常用的查找函数地址方式查找ntoskrnl.exe导出表中的函数地址（此代码中的所有函数名和文件名都采用了hash处理），分别是

1，  ExAllocatePool

2，  ExFreePool

3，  ZwQuerySystemInformationEx

[![](https://p3.ssl.qhimg.com/t018a56410157632356.png)](https://p3.ssl.qhimg.com/t018a56410157632356.png)

2.4  根据hash 获取函数地址

函数寻找完成后，便是将后门程序hook到SrvTransaction2DispatchTable表中的函数SrvTransactionNotImplemented地址上，至于为什么要挑选这个函数我认为主要有以下三个原因：

1， 不增加无关网络协议连接，直接利用SMB协议进行数据传输（可以达到隐藏流量的目的，估计这也是为什么到公布了利用工具后才发现漏洞的原因）。

2， 通过查看SrvTransaction2DispatchTable表结构，我们有两个函数在这个表中出现了两次以上SrvSmbFsct1（3次）和SrvTransactionNotImplemented （2次），因此这两个函数更有利于hook。

3， 如果hook到SMB协议的常用处理函数， 那么这个函数的调用会比较频繁，那么处理过程就相对要复杂很多。而SrvTransactionNotImplemented的调用时在发送非正常Trans2 Request请求时才会调用，在正常情况下执行到这个函数的概率很小。

作者知道SrvTransaction2DispatchTable位于Srv.sys中的.data节中，所以作者采用了如下3个步骤实现寻找SrvTransaction2DispatchTable地址：

1，通过两次调用ZwQuerySystemInformationEx函数来获取所有内核模块的空间结构信息（_SYSTEM_MODULE_INFORMATION_ENTRY）表（第一次调用ZwQuerySystemInformationEx来获取 内核模块信息大小， 然后利用ExAllocatePool创建内存空间，在第二次调用ZwQuerySystemInformationEx来获取模块信息）。

[![](https://p5.ssl.qhimg.com/t0164cd9a7b6a4903d7.png)](https://p5.ssl.qhimg.com/t0164cd9a7b6a4903d7.png)

2.5  获取内核模块信息结构体

2，通过依次对比_SYSTEM_MODULE_INFORMATION_ENTRY中的ImabeName 字符串来查找 srv.sys(此模块是SMB协议的主要模块) 

[![](https://p1.ssl.qhimg.com/t01d0d32d7bd8d3249b.png)](https://p1.ssl.qhimg.com/t01d0d32d7bd8d3249b.png)

2.6 查找srv.sys地址空间

3, 找到srv.sys的基地址后通过PE文件结构信息，最终后定位到.data节。

[![](https://p1.ssl.qhimg.com/t0172cc56396a85c529.png)](https://p1.ssl.qhimg.com/t0172cc56396a85c529.png)

2.7 定位.data节信息

4，找到.data节后，最后进行内存搜索，根据SrvTransaction2DispatchTable的结构特征(见图2.9):

① 根据观察发现 SrvTransaction2DispatchTable[9], SrvTransaction2DispatchTable[11], SrvTransaction2DispatchTable[12]的值都相同， 都指向srv!SrvSmbFsct1；

②SrvTransaction2DispatchTable 中的函数指针跟SrvTransaction2DispatchTable在同一个地址领空， 因此最高8位的地址应该相同；

③SrvTransaction2DispatchTable[18h] = 0；

根据这三个特征来顺序搜索.data节空间，可以定位到SrvTransaction2DispatchTable的基地址。

[![](https://p1.ssl.qhimg.com/t014050736e691b0887.png)](https://p1.ssl.qhimg.com/t014050736e691b0887.png)

2.8查找SrvTransaction2DispatchTable地址

[![](https://p3.ssl.qhimg.com/t011629f9c5ad4b7bc8.png)](https://p3.ssl.qhimg.com/t011629f9c5ad4b7bc8.png)

2.9 SrvTransaction2DispatchTable结构信息

找到SrvTransaction2DispatchTable后开始为hook 后门程序做准备，先重新分配一块0x400大小内存空间bdBuffer，首先将前0x48字节中存放一些地址信息，因此顺序为：

[![](https://p3.ssl.qhimg.com/t01b17959121b29c3b5.png)](https://p3.ssl.qhimg.com/t01b17959121b29c3b5.png)

（此处的ebp+4我猜测是作者的一点小失误，应该是 ebp-14h对应函数地址ZwQuerySystemInformationEx，不过对后边后门程序基本没有影响也就无法验证）。

并且将上述几个地址和空间结束地址进行异或后的值存放在bdBuffer+0x24地址处，作为后门程序首次使用时的异或key的引子（后门程序所使用的异或key是通过这个值变换而来）。接下来便将后门程序拷贝到bdBuffer+0x48处，然后将 bdBuffer + 0x48赋值给SrvTransaction2DispatchTable[14]中， 实现hook后退出。

[![](https://p0.ssl.qhimg.com/t0131798eec8a6f15c0.png)](https://p0.ssl.qhimg.com/t0131798eec8a6f15c0.png)

2.10 保存函数地址，拷贝后门程序

[![](https://p0.ssl.qhimg.com/t015cf34d54bc441508.png)](https://p0.ssl.qhimg.com/t015cf34d54bc441508.png)

2.11 Hook SrvTransactionNotImplemented前后对比



**0x3 后门通信篇**



这个模块需要配合Doublepulsar程序，因此就一起分析了下，本文主要分析EternalBlue中的Shellcode，所以就对Doublepulsar的分析此处就不写了，主要配合Wireshark进行分析。

首先是获取空间起始地址获取给ebp，然后获取到已经够造好的SmbBuffer中。

[![](https://p2.ssl.qhimg.com/t0148a743d6aa215178.png)](https://p2.ssl.qhimg.com/t0148a743d6aa215178.png)

3.1 获取相关信息

在函数85bbd239中，获取最终返回的SMB 返回数据包地址赋值到ebp+0x38。至于这个过程如何得到的，我也没有仔细跟，应该跟SMB协议结构有关系（先将就着用吧）。

[![](https://p0.ssl.qhimg.com/t01e1e876f93f6bef28.png)](https://p0.ssl.qhimg.com/t01e1e876f93f6bef28.png)

3.2 获取SMB 返回数据包地址

接着是计算解码密钥，计算过程在85bbd1a8中，比较简单 key = (A*2)  ^ bswap(A), 然后将结果赋值到ebp+0x28中，具体过程如下：

[![](https://p3.ssl.qhimg.com/t010f0b7524e43acc97.png)](https://p3.ssl.qhimg.com/t010f0b7524e43acc97.png)

3.3 根据解码引子计算解码key

函数85bbd1e9是获取SMB发送数据数据段的相关结构，对SMB数据结构在内存中的表现形式不太了解，我也还没太搞明白。

获取完这些后，接着判断命令类型，计算过程使根据发送的数据包的TimeOut,中的逐字节相加得到：

[![](https://p0.ssl.qhimg.com/t019f1ddc4abb766f1d.png)](https://p0.ssl.qhimg.com/t019f1ddc4abb766f1d.png)

3.4 计算命令类型

[![](https://p5.ssl.qhimg.com/t01ab2b27c2b7e438d7.png)](https://p5.ssl.qhimg.com/t01ab2b27c2b7e438d7.png)

3.5 抓取的Trans2 Request数据包

判断命令类型，主要有三个命令，0x23  -&gt; 检查后门是否存在， 0x77 –&gt; 卸载后门， 0xC8 执行Shellcode。

[![](https://p3.ssl.qhimg.com/t0123cd5b3a27d6f0eb.png)](https://p3.ssl.qhimg.com/t0123cd5b3a27d6f0eb.png)

3.6 命令类型判断

<br>



**0x3.1  检查后门是否存在 0x23**



当接收到的命令是0x23后，做的事情，将ebp+0x24中存放的密钥引子写入到返回数据包的Signature前4个字节中，将系统位数信息存放在Signature的第5个字节中。如下所示：

[![](https://p1.ssl.qhimg.com/t011d7d7e97c7e5d7bf.png)](https://p1.ssl.qhimg.com/t011d7d7e97c7e5d7bf.png)

3.7 后门检测处理过程

然后将返回数据包的Multiplex ID加0x10后 跳转到真正的SrvTransactionNotImplemented地址继续执行。

执行结果如下(两次结果不一样，是因为不是同一个过程里边抓到的数据包，调试过程中，分析太久SMB就自动退出链接)：

[![](https://p5.ssl.qhimg.com/t013b7a62200df5db4f.png)](https://p5.ssl.qhimg.com/t013b7a62200df5db4f.png)

3.8 检测后门反馈数据包

<br>

**0x3.2 卸载后门 0x77**



卸载后门的过程也相对较为简单，清空并释放掉以前分配的空间，然后unhook  SrvTransactionNotImplemented函数后，设置返回数据包的Multiplex ID +=0x10恢复SrvTransactionNotImplemented的相关条件后退出，由系统在调用一次正常的SrvTransactionNotImplemented即可。

[![](https://p0.ssl.qhimg.com/t013d8746b98218e650.png)](https://p0.ssl.qhimg.com/t013d8746b98218e650.png)

3.9 卸载后门过程

<br>

**0x3.3  执行命令 0xc8**



此过程主要包括组装数据（Doublepulsar的攻击数据根据大小拆分成一个或多个Trans2 Request数据包）和执行两个功能，主要流程如下:

Step 1, 解密数据包的SESSION_SETUP Parameters参数,获取当前数据的总长度total_len，当前数据包长度current_len和 当前数据包在整个数据包的位置current_pos；

[![](https://p3.ssl.qhimg.com/t01902f654ce1f2c3dc.png)](https://p3.ssl.qhimg.com/t01902f654ce1f2c3dc.png)

3.10 计算数据包信息

[![](https://p1.ssl.qhimg.com/t0194db446ee70191c8.png)](https://p1.ssl.qhimg.com/t0194db446ee70191c8.png)

3.11 数据包信息存放位置

Step 2, total_len 和存放总长度存放位置（ebp+0x30）的值进行比较，如果不相等则说明这是第一个数据包或者是错误数据包都 需要重新开始转到Step 3, 否则转到Step4；

Step 3, 如果内存空间存放处 ebp + 0x2C 不为这将其空间清零后释放，然后在分配一块长度为（total_len + 4）的空间,地址为buffer_addr，如果内存分配失败则跳转到Step 10, 然后将ebp+0x30 的值设置为total_len +4, ebp+0x2c 的值设置为buffer_addr；

[![](https://p1.ssl.qhimg.com/t01066748dd4ecf3567.png)](https://p1.ssl.qhimg.com/t01066748dd4ecf3567.png)

3.12 分配存放数据包空间

Step 4, 如果current_pos + current_len &gt;total_len，则表示数据包出错， 跳转到Step 9;

Step 5, 将接收到的数据packet_data 拷贝到  buffer_addr + current_pos处， 然后对这段拷贝的数据解码;

[![](https://p1.ssl.qhimg.com/t01f78f8b524ac427f5.png)](https://p1.ssl.qhimg.com/t01f78f8b524ac427f5.png)

3.13 拷贝数据并解码

Step 6, 如果解码完成后的位置pos  &lt; buffer_addr+ total_len 则表示数据包没有接收完成，转到Step 8, 否则转到Step 7;

Step 7 , 直接执行（call）buffer_addr, 执行完成后， 清除并释放掉buffer_addr，并重新计算密钥引子和解密密钥；

[![](https://p1.ssl.qhimg.com/t01be19b3e28fed941c.png)](https://p1.ssl.qhimg.com/t01be19b3e28fed941c.png)

3.14 执行解码后的数据，重新生成解码引子和解码key

Step 8 , 将发送的SMB Reponse 中Multiplex ID + 0x10 （执行成功） ,转到Step 11;

Step 9, 将发送的SMB Reponse 中Multiplex ID + 0x20 （非后门需要的数据包）,转到Step 11;

Step 10, 将发送的SMB Reponse 中Multiplex ID + 0x30 （内存分配失败）,转到Step 11;

Step 11, 跳到真正的SrvTransactionNotImplemented中执行。



**0x4 写在最后**



这是小菜第一次内核调试，查了很多资料，学了很多内核相关知识，也学到了EternalBlue作者的一些奇淫技巧。但是还是有很多不清楚的地方，希望各位大牛不吝赐教



**0x5 参考文献**



【1】NSA Eternalblue SMB 漏洞分析 [http://blogs.360.cn/360safe/2017/04/17/nsa-eternalblue-smb/](http://blogs.360.cn/360safe/2017/04/17/nsa-eternalblue-smb/)

【2】NSA Eternalblue SMB 漏洞分析

[http://www.myhack58.com/Article/html/3/62/2017/85358_4.htm](http://www.myhack58.com/Article/html/3/62/2017/85358_4.htm) 





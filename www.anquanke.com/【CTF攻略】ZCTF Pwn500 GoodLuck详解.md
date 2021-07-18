
# 【CTF攻略】ZCTF Pwn500 GoodLuck详解


                                阅读量   
                                **146837**
                            
                        |
                        
                                                                                                                                    ![](./img/85625/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/85625/t01a7121bd6e4ba7c11.jpg)](./img/85625/t01a7121bd6e4ba7c11.jpg)**

****

<br>

作者：[Ox9A82](http://bobao.360.cn/member/contribute?uid=2676915949)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**关于**

这是这几天刚刚结束的ZCTF中的一道500分Pwn题，在比赛之中我没有能够解出，于是在赛后自己研究了一下，发现这道题有两种解法而且利用过程比较精彩，其中第一种解法参考自飞猪的writeup，第二种解法来自晨升师傅，在复现的过程中感觉开阔了不少思路，受益匪浅，这里不敢独享拿出来分享给大家。

<br>

**题目介绍**

Pwn500-GoodLuck是一个形式比较常见的选单类题目



```
Good Luck To you!
1.add goods
2.delete goods
3.edit goods
4.show goods
5.exit
Now ! your choice:
```

如上所示，程序提供了5个选项。分别是添加、删除、编辑、显示和退出。选择添加功能会新建一个结构，我们把这个结构称为goods，goods的结构如下：



```
goods 40bytes
* 8bytes choice
* 8bytes pointer
* 24bytes name
```

其中前8个字节代表选择的礼物编号，程序中提供3种选择，1-&gt;apple 2-&gt;pear 3-&gt;flower

根据不同的选择会有不同的结构被建立，而goods+0x8处的指针正是指向这个子结构的。其中1、2两种选择建立的结构我们称为gift1,3号选择建立的结构我们称为gift2,我们可以看到gift1和gift2都是16字节但是结构有所不同。gift1的三个域都只是一些简单的char字符，而gift2的两个域都是指针，其中第一个指针指向模块偏移0x1040的地方，第二个指针指向一块堆内存，这块堆内存中也是简单的char字符，并没什么好说的。



```
gift1 16bytes
* 8bytes say_something
* 4bytes many
* 4bytes price
gift2 16bytes
* 8bytes 0x1040
* 8bytes pointer
```

add功能对两类不同的choice进行分别处理，分配内存，并获取输入值，上述的goods结构、gift1、gift2均是通过add功能建立。

当一个goods结构建立后，它的指针会被放入.bss段上的全局数组中统一管理，我们称之为global_goods[]。之后对goods结构的索引基本上都是通过global_goods[]的下标形式进行的，而实际上.bss上存在两个数组彼此相邻，因为其中一个数组是delete功能使用的。

delete功能是题目的重点，如果要进行一次完整的delete操作首先需要在主线程中设置要删除的goods在global_goods[]中的下标index，当然首先会验证这个index中是否有值存在，而删除的效果是会使goods的choice值加1。删除过程是由事件对象控制的（在Windows里类似的东西叫事件对象，Linux不是很清楚叫什么），代码如下



```
pthread_mutex_lock(&amp;mutex);
pthread_cond_wait(&amp;cond, &amp;mutex);
pthread_cond_wait(&amp;stru_2030E0, &amp;mutex);
```

edit功能可以对gift2结构的pointer指向的内存区域的内容进行编辑，但是问题在于edit区分gift1和gift2的方式只是简单的choice是否小于2，结合我们前面的描述你是不是联想到了什么？:)

最后show功能同样是根据gift1、gift2的类型不同进行不同的处理。但是同时又增加一条判断流程，如下：



```
mov     rdi, cs:s1      ; s1
mov     rsi, [r13+8]    ; s2
call    _strcmp
```

其中s1为"0517n"，如果这一条满足又会进行下一个判断



```
cmp     dword ptr [rax+8], 1
jnz     short loc_1558
```

之后会输出一些内容，然后调用read_num和free函数。

最后介绍下题目的保护开启情况：



```
CANARY    : ENABLED
FORTIFY   : disabled
NX        : ENABLED
PIE       : disabled
RELRO     : FULL
```

至此，我们介绍了程序中出现的几种结构，并且大致的梳理了程序的各个流程，下面我们看一下这道题到底是怎样利用的。

<br>

**第一种利用**

程序获取用户的输入数字（比如选项）一直都是通过read_num函数实现的，read_num函数存在一个比较隐蔽的漏洞，我在看writeup之前也并没有能够发现。read_num函数(地址:0x00F80)的大致流程是这样的：首先从参数获取到要读取的字符数量，然后逐个的读取字符存入栈缓冲区中，等到读到'n'或者达到数量上限时就停止读取，然后把读到的字符串使用atoi转成数字返回。如果光看描述可能不会觉得这个函数有什么问题，甚至如果只看F5不看反汇编也很难发现有问题，问题在于从参数获取欲读到的字符数时使用了lea r13d, [rdi-1]，那么如果我们给rdi传0的话就会导致读取数量非常大的字符，从而导致栈溢出。

前面的题目介绍中我们说这道题具有canary保护，但是canary的值实际上在.bss上存有备份



```
push    rbx
push    rax
push    rdx
mov     rbx, 28h
mov     rdx, fs:[rbx]
lea     rax, unk_2031C0
mov     [rax], rdx
pop     rdx
pop     rax
pop     rbx
retn
```

这段代码展示了把canary的值从fs:0x28取出并备份到0x2031C0的.bss段内存上，而0x2031C0恰好在global_goods[]下面，这就提供了一种泄漏栈cookie的可能性，最后也的确是这么做的。

那么利用的第一步的目的就是通过混淆gift1和gift2来实现一些信息的泄漏。为了实现这一点，我们需要使用add功能新建一个goods。因为我们的目的是为了泄漏，而只有gift1才允许进行输出，所以我们要新建gift2然后混淆成gift1。所以我们这里可以选择0或是3，但是绝对不能是1或2。那么泄漏出来的究竟是什么呢？首先我们要知道，show goods会把gift2的16个字节当成字符串输出（但是后8个字节是分别输出的）。其中前8个字节就是主模块0x1040偏移处的地址，因为主模块每次加载的地址都是不同的，因此一但我们获知了主模块0x1040偏移处的地址就可以算出主模块的基地址从而计算出一系列诸如.got、.got.plt的地址。

因为我们已经获得了一个栈溢出，所以我们接下来可以自然而然的想到去泄漏canary，从栈溢出入手拿到shell。 同时因为对于gift2来说show功能中存在这样的代码，我们这个时候又需要新建一个gift1然后混淆成gift2，然后把gift1+0x8的指针指向储存canary的地方就可以实现泄漏。



```
lea     r14, global_pointer
test    eax, eax
mov     rax, [r14+rbp*8]
jnz     short loc_1524
……
cmp     dword ptr [rax+4], 1
jz      short loc_154A
……
lea     rdi, aSorryThisIsAFa ; "Sorry,This is a fake show!"
call    _puts
mov     rdi, [r13+8]    ; s
call    _puts
一但得知了canary，我们接下来就是要想办法的触法栈溢出，因为之前分析过要给read_num传参为0才能触发溢出，而这个参数实际上等于choice的值。
mov     esi, [rax]
mov     ebx, esi
mov     edi, ebx
call    read_num
```

为此我们新建一个choice为0的goods，然后让我们的值为"0517",使strcmp返回1走0x1158处的流程就可以触发溢出了。因为我们已知canary的值，因此这里就是常规的栈溢出利用，通过rop接下来怎么搞就是见仁见智了。

<br>

**第二种利用**

第一步，选择add goods。这里与第一种利用方法相同，因为代码中的验证条件是 if ( (unsigned int)choice &lt;= 3 )(地址:0x1121)，所以我们选择的choice可以是0，虽然并没有给出0的选项，但是输入0依然合法，当然这里的目的仍然是混淆两种结构所以是与第一种相同的。

第二步，使用delete goods功能来混淆两种结构，这也与上一种方法相同。我们之前讲过delete功能是通过一个独立线程实现的。这个功能的效果是

++*global_shuzu[global_jishu]（地址:0x1361），因此会使目标gift的choice值加1。

这样根据上面介绍的情况就可以实现对两种不同的choice结构进行混淆（0、3与1、2），通过混淆进行泄漏。

第三步，show goods。show goods功能本身具有一定的迷惑性，因为这个功能本身具有验证条件，如果条件不满足会输出Sorry,This is a fake show!不会真正的实现Leak。但是如果我们实际经过调试会发现，这里验证的其实就是目标gift结构的choice值，如果为0、3则不满足，如果为1、2则满足，结合第二步中的使目标gift结构choice值+1的操作，我们知道我们是可以实现成功Leak的。

那么泄漏出来的究竟是什么呢？我们在第一种利用中知道了，前8个字节是主模块0x1040偏移处的地址，根据这个地址我们可以求出主模块的基地址。但是上一种方法中我们并没有用到后8个字节，后8个字节保存的是堆缓冲区地址即gitf2+0x8处的堆pointer，因为一直以来的堆分配尺寸我们都是可以进行计算的。因此我们只要能够得到当前分配的堆块的地址就可以算出初始堆的堆基地址，这也就是所谓的堆基地址泄漏。这两步泄漏相当的重要，后续操作之所以能进行就是因为这两步我们成功的获取了地址。



```
mov     rsi, [rsi+8]
lea     rdi, aS1SIi1DIi2D ; "s1-&gt;%s ii1-&gt;%d ii2-&gt;%dn"
xor     eax, eax
pop     r12
pop     r13
pop     r14
mov     ecx, [rsi+0Ch]
mov     edx, [rsi+8]
jmp     _printf
```

第四步，伪造index。这一步是这种利用中最精彩的部分也是与第一种利用方式完全不同的地方。因为根据之前的泄漏我们已经知道了堆基址和模块基址，那么我们就可以通过计算下一次堆分配到的地址与.bss段上数组起始地址的差值来得出一个偏移，通过这个伪造偏移index我们就使得堆上出现了一个内容完全可控的伪造的gift块。如果你没有听懂的话，那么简单的说global_pointer[]本来应该在.bss上(0x2031A0)，但是我们通过泄漏把它“搬”到了堆上，这一步相当的精彩。

看到这里你应该已经明白接下来的步骤了，没错，就是通过伪造gift来控制指针（因为此时地址全部可预测），利用程序中的edit和show功能就可以进行任意地址写和任意地址读了。至此我们已经泄漏出了所需要的一切信息并且具有读写能力，接下来怎么利用就是见仁见智了。

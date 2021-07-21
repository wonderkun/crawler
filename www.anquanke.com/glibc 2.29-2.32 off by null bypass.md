> 原文链接: https://www.anquanke.com//post/id/236078 


# glibc 2.29-2.32 off by null bypass


                                阅读量   
                                **93159**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t014293b5a1bd7f5c57.png)](https://p1.ssl.qhimg.com/t014293b5a1bd7f5c57.png)



## 简介

在glibc2.29以上版本，glibc在unlink内加入了prevsize check，而通过off by null漏洞根本无法直接修改正常chunk的size，导致想要unlink变得几乎不可能。

```
/* consolidate backward */
if (!prev_inuse(p)) `{`
  prevsize = prev_size (p);
  size += prevsize;
  p = chunk_at_offset(p, -((long) prevsize));
  if (__glibc_unlikely (chunksize(p) != prevsize))
    malloc_printerr ("corrupted size vs. prev_size while consolidating");
  unlink_chunk (av, p);
`}`
```

通过这样的检测，使得我们无法使用[house_of_einherjar](https://github.com/shellphish/how2heap/blob/master/glibc_2.31/house_of_einherjar.c?fileGuid=HdcWcwpGpCrQpjXX)的方法进行构造堆重叠，所以在2.29以上版本，off by null 的利用只有唯一的方法 —— 伪造 FD 和 BK。<br>
但是伪造 FD 和 BK也不是容易的事情，我们需要绕过以下检测

```
if (__builtin_expect (FD-&gt;bk != P || BK-&gt;fd != P, 0))      
  malloc_printerr (check_action, "corrupted double-linked list", P, AV);
```

这个检测对于双向链表来说是显然成立的，但是对于我们想要伪造FD和BK来说却成为了一个大麻烦，本文将会根据不同的题目限制条件来讲解绕过方法。<br>
而且为了文章的全面性，我会加入一些老生常谈的绕过方法，如果读者觉得某一部分自己已经掌握则可以选择性的跳过。



## unlink

### <a class="reference-link" name="unlink%E7%9A%84%E7%9B%AE%E7%9A%84"></a>unlink的目的

当目前要 free 的位置旁边有空闲的块，则考虑 unlink 把将要 free 的块，和相邻空闲的块合并。

### <a class="reference-link" name="unlink%20%E7%9A%84%E7%B1%BB%E5%9E%8B"></a>unlink 的类型
1. 向前合并，也就是上面那块是空闲的，我们要 free 后面那一块
1. 向后合并，也就是下面那一块是空闲的，我们要 free 前面那一块。
### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E4%BA%A7%E7%94%9Funlink"></a>如何产生unlink

若本堆块 size 域中的 p 标志位为 0（前一堆块处于释放状态），则利用本块的 pre_size 找到前一堆块的开头，将其中 bin 链表中摘除（unlink），并合并这两个块，得到新的释放块。

也就是说，我们要**让堆块 size 域中的 p 标志位为 0，并设置合适的pre_size**。

### <a class="reference-link" name="%E6%B3%A8%E6%84%8F"></a>注意

当申请size为0xF8，也就是说结构体中size = 0x101的时候，我们如果使用off by null来覆盖，正好可以把该size的p标志位变成0，其他size的情况，可以考虑用off by one来设置。

而pre_size在我们的可控堆块中，可以直接修改。

在以下部分中，会着重于对于堆块FD和BK检测的构造，而**不强调p标志位和prev_size**的修改。（这两者的修改，在不同情况下也会遇到不同的阻碍，但由于篇幅问题，不是本文的重点）



## NO PIE

在NO PIE的情况下绕过对FD和BK的检测是非常容易的，所以这也同样是一种入门的堆题利用方法，是初学者一定要掌握的。

NO PIE意味着我们可以直接劫持程序中用于**储存堆块指针的数组**，因为在这个数组中储存着指向堆块内容部分的指针

### **unlink前的内存排布**

[![](https://p3.ssl.qhimg.com/t019fe35897e8ba4e41.png)](https://p3.ssl.qhimg.com/t019fe35897e8ba4e41.png)

### **构造我们的堆块**

[![](https://p2.ssl.qhimg.com/t0148b1d42979b86f3f.png)](https://p2.ssl.qhimg.com/t0148b1d42979b86f3f.png)

### **unlink后的chunk指针数组**

[![](https://p1.ssl.qhimg.com/t0100db2b4ce84d5c2b.png)](https://p1.ssl.qhimg.com/t0100db2b4ce84d5c2b.png)



## 可泄露堆地址

在可泄露堆地址的题目中，我们也可以使用类似于NO PIE情况时候的方法，在堆块上伪造一个要unlink堆块的指针来绕过判定。

[![](https://p4.ssl.qhimg.com/t0153a93cb2c856157c.png)](https://p4.ssl.qhimg.com/t0153a93cb2c856157c.png)

我们可以在堆上随便找个地址，比如0x20位置(fake_ptr)等等，并且把他的内容设置为chunk，这样fd和bk的内容就可以类似于**NO PIE**的情况时，让fd = fake_ptr – 0x18，bk = fake_ptr – 0x10，即可绕过检测实现unlink。

### <a class="reference-link" name="%E6%B3%84%E9%9C%B2%E5%A0%86%E5%9F%BA%E5%9D%80%E7%9A%84%E6%96%B9%E6%B3%95"></a>泄露堆基址的方法

<a class="reference-link" name="%E5%88%A9%E7%94%A8tcache"></a>**利用tcache**

构造两个相同size的堆块a和b，我们先free(a)让他进入到tcache中，再free(b)也让他进入到tcache中。这时候，在堆块b的next位置就存在着堆块a的地址，我们leak出来就能够得到堆地址。

**在glibc2.32版本中**新加入了一个key会对tcache next的内容进行异或，我们可以申请一个堆块a，并且free(a)，直接leak就可以得到堆地址 &gt;&gt; 12，我们计算一下就可以得到了。

关于这部分改动，想要了解的可以看：[http://blog.wjhwjhn.com/archives/186/](http://blog.wjhwjhn.com/archives/186/?fileGuid=HdcWcwpGpCrQpjXX)

**<a class="reference-link" name="%E5%88%A9%E7%94%A8fastbin"></a>利用fastbin**

类似于tcache的思路，这里不再重复。

**<a class="reference-link" name="%E5%88%A9%E7%94%A8unsorted%20bin"></a>利用unsorted bin**

当unsorted bin链上有两个堆块的时候，其中一个堆块的fd会指向另一个堆块，我们可以直接leak得到，并计算出堆基址。

**<a class="reference-link" name="%E5%88%A9%E7%94%A8largebin"></a>利用largebin**

如果堆块在largebin中，他的**fd_nextsize**和**bk_nextsize**都会指向堆块地址，可以泄露出。



## 不可泄露堆地址

不可泄露堆地址的各种方法归根结底都是通过**部分写入**和**各种堆管理器的性质**来达到目的。

这里会分成三种方法来讲，可以根据使用场景来选择，最好都要了解和掌握。

### <a class="reference-link" name="1.RPISEC%E6%88%98%E9%98%9F%E7%9A%84%E6%80%9D%E8%B7%AF"></a>1.RPISEC战队的思路

这个方法我是从[Ex的博客](http://blog.eonew.cn/archives/1233?fileGuid=HdcWcwpGpCrQpjXX)上看到的，虽然复杂且不实用，但是构造巧妙，这里不得不提及一下。

**<a class="reference-link" name="%E5%9F%BA%E6%9C%AC%E6%80%9D%E8%B7%AF"></a>基本思路**

1.让一个堆块进入到largebin中，这时候他的fd_nextsize和bk_nextsize都是堆地址。我们从这个largebin chunk + 0x10的地方开始伪造堆块叫做fake chunk。

2.利用部分写入来覆盖fake chunk的fd指针（largebin-&gt;fd_nextsize），使其指向一个有堆地址的堆块，并且再用部分写入把那个堆块的堆地址指向fake chunk。

3.利用fastbin或tcache在fd位置（largebin chunk + 0x10）踩出一个堆地址，并且部分写入指向fake chunk。这时候由于fake chunk的bk指针（largebin-&gt;bk_nextsize）是指向这个地方的，所以绕过了检测。

首先我们来看一下large bin chunk是怎么样的

[![](https://p1.ssl.qhimg.com/t01d604d78f4a7aa456.png)](https://p1.ssl.qhimg.com/t01d604d78f4a7aa456.png)

我们要伪造成

[![](https://p4.ssl.qhimg.com/t0179d1b1dd50628027.png)](https://p4.ssl.qhimg.com/t0179d1b1dd50628027.png)

**<a class="reference-link" name="1.%E4%BF%AE%E5%A4%8D%20fake%20fd"></a>1.修复 fake fd**

我们利用部分写入来修改fake fd修改到另一个可控堆块上，这个堆块上需要有一个堆地址（这个堆地址可以通过 unsorted bin、small bin等等来实现）

[![](https://p5.ssl.qhimg.com/t01df192fca8b890c61.png)](https://p5.ssl.qhimg.com/t01df192fca8b890c61.png)

然后我们部分写入，覆盖这个堆地址的低字节，使其指向我们伪造的fake chunk，也就是largebin chunk + 0x10的位置。

**<a class="reference-link" name="2.%E4%BF%AE%E5%A4%8D%20fake%20bk"></a>2.修复 fake bk**

由于fake fd我们要部分写入来覆盖，所以fake bk的内容我们是无法修改的，这时候他指向的位置就是largebin chunk + 0x10，所以我们需要想办法在largebin chunk + 0x10的地方写入一个largebin chunk + 0x10的地址。

**<a class="reference-link" name="%E6%96%B9%E6%A1%881%EF%BC%9A%E4%BD%BF%E7%94%A8tcache"></a>方案1：使用tcache**

我们可以利用off by null将size改小一些，使得这个size在tcache的范围内。

然后先释放a，再释放largebin chunk，这时候再largebin chunk + 0x10的位置就会有一个a的指针。我们再用部分写入将指针改写成largebin chunk + 0x10的地址。

**在glibc 2.29以上版本**加入了一个key结构用于检测doube free，所以tcache的方法不再可行了，因为这个key的位置正好就是在bk（fake size）的位置，这会导致我们的fake size被复写。而我们又因为要用部分写入来改写next指针，所以无法还原fake size的内容。

**<a class="reference-link" name="%E6%96%B9%E6%A1%882%EF%BC%9A%E4%BD%BF%E7%94%A8fastbin"></a>方案2：使用fastbin**

使用fastbin就没有key结构来干扰fake size了，但是由于fastbin的申请size有限，所以如果使用这个方法，需要保证能够申请出fastbin size的堆块。

如果可以申请出堆块，操作方法和tcache一样就可以。

这种方法是早期经常使用的方法，但是犹豫限制条件过多并且比较繁琐。所以现在的题目一般都无法使用这种方法。

### <a class="reference-link" name="2.%E5%88%A9%E7%94%A8unsorted%20bin%E5%92%8Clarge%20bin%E9%93%BE%E6%9C%BA%E5%88%B6"></a>2.利用unsorted bin和large bin链机制

这部分内容如果利用得当，可以在题目的苛刻的条件下（如会在末尾写入\x00等…）也可以无需爆破伪造堆块，属于本文的重头戏。

本部分演示使用的例题是来自NepCTF的由FMYY师傅所出的**NULL_FXCK**，该题目做法多样化且构造堆块技巧性强，是一道非常完美的压轴pwn题，在比赛中也只有cnitlrt师傅（orz）一人完成。

官方wp采用large bin链机制来伪造FD和BK，爆破1/16几率成功，我在这里讲解的做法，不需要爆破就可以成功，大大提高了效率。由于后续部分脱离本篇的主题，故这里只讲解构造unlink的方法。之后的利用部分也是非常的有意思，让我不禁感叹 FMYY YYDS，如果之后有时间的话，也会对后面的内容的多种做法进行讲解。

### <a class="reference-link" name="%E5%9F%BA%E6%9C%AC%E6%80%9D%E8%B7%AF"></a>基本思路

**<a class="reference-link" name="1.%E5%9C%A8fd%E5%92%8Cbk%E5%86%99%E5%A0%86%E5%9C%B0%E5%9D%80"></a>1.在fd和bk写堆地址**

如下图所示，堆块0x55555555bc00是我们要用于构造的堆块地址。

[![](https://p1.ssl.qhimg.com/t01c042b35183da0ed5.png)](https://p1.ssl.qhimg.com/t01c042b35183da0ed5.png)

通过unsorted bin 链表我们让这个堆块的fd和bk都写了一个堆地址

[![](https://p1.ssl.qhimg.com/t01be455787b0c4e2f6.png)](https://p1.ssl.qhimg.com/t01be455787b0c4e2f6.png)

**<a class="reference-link" name="%E6%9E%84%E9%80%A0%E5%9B%BE%EF%BC%9A"></a>构造图：**

[![](https://p1.ssl.qhimg.com/t01cc840229c8cf1cc9.png)](https://p1.ssl.qhimg.com/t01cc840229c8cf1cc9.png)

其中辅助堆块的作用在之后会提及

**构造代码：**

```
add(0x418) #0 fd
add(0x108) #1
add(0x418) #2
add(0x438) #3
add(0x108) #4
add(0x428) # 5 bk 
add(0x108) # 6
delete(0)
delete(3)
delete(5)
```

**<a class="reference-link" name="2.%E5%9C%A8%E4%BC%AA%E9%80%A0%E5%A0%86%E5%9D%97%E9%99%84%E8%BF%91%E7%94%B3%E8%AF%B7%E5%A0%86%E5%9D%97"></a>2.在伪造堆块附近申请堆块**

由于我们要通过部分写入的方法来绕过检测，而在堆空间中，只有低三字节是固定的。

所以我们为了逃避爆破，希望能够找到只需要覆盖最低一字节就可以修改成fake chunk的地址，于是我们应该利用在fake堆块附近0x100内的堆块来作为辅助堆块写地址，**之前申请的辅助堆块就是起到了这个作用，我们可以利用这个堆块来进行重分配，使得分配的地址非常贴近利用堆块**。

**<a class="reference-link" name="%E6%9E%84%E9%80%A0%E5%9B%BE%EF%BC%9A"></a>构造图：**

[![](https://p1.ssl.qhimg.com/t016719e17bae2e7887.png)](https://p1.ssl.qhimg.com/t016719e17bae2e7887.png)

可以发现，我们先让辅助堆块和利用堆块合并之后再对空间进行重新分配，使得堆块2恰好可以覆盖到之前利用堆块的size，且堆块3的0x55555555bc20，十分贴近之前0x55555555bc00，只需要抹去最低一字节即可。

**<a class="reference-link" name="%E6%9E%84%E9%80%A0%E4%BB%A3%E7%A0%81%EF%BC%9A"></a>构造代码：**

```
delete(2) #2 &amp; 3 unlink
add(0x438, 'a' * 0x418 + p64(0xA91))  # 0 set size
add(0x418)  # 2 c20
add(0x428)  # 3 bk 150
add(0x418)  # 5 fd 2b0
```

**<a class="reference-link" name="%E6%B3%A8%E6%84%8F%EF%BC%9A"></a>注意：**

分配完成之后，我们再把全部堆块申请回来，这可能并不是步骤最少的做法，但是全部申请回来可以使得操作有条理，使得我们构造过程中出现的问题减少。

<a class="reference-link" name="3.%E4%BF%AE%E5%A4%8D%20fake%20fd"></a>**3.修复 fake fd**

**<a class="reference-link" name="%E4%BF%AE%E5%A4%8D%E6%80%9D%E8%B7%AF%EF%BC%9A"></a>修复思路：**

我们在之前的状态下，先删除**fake-&gt;FD堆块**，再删除**重分配堆块2（辅助堆块）**。我们就可以在**fake-&gt;FD堆块的BK位置**写入一个**重分配堆块2（辅助堆块）**的值

[![](https://p0.ssl.qhimg.com/t01a1c0c02556e8af23.png)](https://p0.ssl.qhimg.com/t01a1c0c02556e8af23.png)

再用部分写入一字节来覆盖，覆盖成**利用堆块**的指针

[![](https://p0.ssl.qhimg.com/t01a02790aff1de8647.png)](https://p0.ssl.qhimg.com/t01a02790aff1de8647.png)

最后再把bc20这个辅助堆块申请回来，方便下一次使用。

[![](https://p4.ssl.qhimg.com/t0171b376a88d4438bd.png)](https://p4.ssl.qhimg.com/t0171b376a88d4438bd.png)

**<a class="reference-link" name="%E6%9E%84%E9%80%A0%E4%BB%A3%E7%A0%81%EF%BC%9A"></a>构造代码：**

```
# partial overwrite fd -&gt; bk by unsorted bin list
delete(5)
delete(2)
add(0x418, 'a' * 9)  # 2 partial overwrite bk
add(0x418)  # 5 c20
```

<a class="reference-link" name="4.%E4%BF%AE%E5%A4%8D%20fake%20bk"></a>**4.修复 fake bk**

**<a class="reference-link" name="%E4%BF%AE%E5%A4%8D%E6%80%9D%E8%B7%AF%EF%BC%9A"></a>修复思路：**

在我示例的这道题下，使用unsorted bin来修复另外**fake bk**是很难的，这是因为这道题如果要进unsorted bin的堆块，size大小要大于等于0x418，而这个size是在largebin范围内的。

所以如果我使用不同size申请的方法，错开**辅助堆块**去直接申请**fake bk堆块（因为如果要在fake bk-&gt;fd的位置写堆值，那么在遍历的时候一定是先遍历到辅助堆块，所以需要错开辅助堆块先去申请fake bk堆块，我想到的方法就是申请一个辅助堆块无法提供的size来错开。但事实上，错开辅助堆块会使得辅助堆块进入largebin中，从而与原来的fake bk断链，这样原来已经写上的堆地址也不复存在）**，因为这个原因所以这部分我要先让堆块进入largebin再用**类似于修复fake fd的方法进行修复。**

先删除**重分配堆块2（辅助堆块）**，再删除**fake-&gt;BK堆块**（注意：这里和上面顺序不一致，这是因为想要写入堆块地址的位置不一致）

[![](https://p3.ssl.qhimg.com/t01f715d7af388506f4.png)](https://p3.ssl.qhimg.com/t01f715d7af388506f4.png)

再让堆块进入到largebin 中

[![](https://p4.ssl.qhimg.com/t014b3aea130b41654d.png)](https://p4.ssl.qhimg.com/t014b3aea130b41654d.png)

再使用部分写入恢复**fake bk**

[![](https://p5.ssl.qhimg.com/t0167f388aca826b189.png)](https://p5.ssl.qhimg.com/t0167f388aca826b189.png)

构造代码：

```
# partial overwrite bk -&gt; fd by largebin list
delete(5)
delete(3)
add(0x9F8)  # 3 chunk into largebin
add(0x428, 'a')  # 5 partial overwrite fd
add(0x418)  # 7 c20
```

**<a class="reference-link" name="5.%E4%BC%AA%E9%80%A0prev_size%EF%BC%8Coff%20by%20null%E4%BF%AE%E6%94%B9size%E7%9A%84p%E6%A0%87%E5%BF%97%E4%BD%8D"></a>5.伪造prev_size，off by null修改size的p标志位**

这部分内容不是本文重点故略过

**<a class="reference-link" name="%E6%9E%84%E9%80%A0%E4%BB%A3%E7%A0%81%EF%BC%9A"></a>构造代码：**

```
# off by null
add(0x108, p64(0) + p64(0x111))  # 8
edit(6, 'a' * 0x100 + p64(0xA90))
delete(3)  # unlink
```

### <a class="reference-link" name="%E5%B0%8F%E7%BB%93"></a>小结

不可泄露堆块地址伪造的根本思想就是通过部分写入来篡改地址到另一个位置。在这个过程中，应当要灵活应变，不能死板的套代码。在必要的时候，牺牲爆破时间来提高调试速度和exp编写速度也是有必要的。



## 总结

通过对本篇文章的学习，相信各位师傅已经能够对于高版本glibc的构造堆块重叠部分得心应手了，但新版glibc的魅力远远只是这篇文章所描述的那么简单，仍然还有很多方法和技巧值得我们去挖掘，希望可以通过这篇文章来引导各位师傅走向探索新版glibc的道路，也希望各位师傅能够把自己在题目中学到的知识能够总结共享出来，这样既可以加深自己的理解，也可以为对相同内容有疑问的师傅答疑解惑。

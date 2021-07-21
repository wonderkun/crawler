> 原文链接: https://www.anquanke.com//post/id/86286 


# 【技术分享】Linux堆溢出之Fastbin Attack实例详解


                                阅读量   
                                **278831**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****

[![](https://p4.ssl.qhimg.com/t0100572467c52303fc.jpg)](https://p4.ssl.qhimg.com/t0100572467c52303fc.jpg)v

作者：[Elph](http://bobao.360.cn/member/contribute?uid=404360756)

预估稿费：400RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**1. 摘要**

在近几年各大CTF比赛中，看到有很多次pwn类别题中出现**fastbin攻击**的情况，例如今年的defcon，RCTF，胖哈勃杯，0CTF final等等 ，fastbin attack是堆漏洞利用中十分常用、易用且有效的一种攻击方式，在网上的中文资料中，对其原理上进行讲述的文章有一些，但详细讲述如何实际利用的完整例子较少，本文将对该利用方式进行简要原理性阐述，并结合今年Defcon预选赛中的一个实例演示一下具体利用过程，以及一些需要注意的地方。



**2. Linux 堆管理策略**

glibc中对堆的管理使用的是ptmalloc，这种方式以chunk为单位管理堆内存，在物理上使用隐式堆管理结构对堆块进行管理，在逻辑结构上采用显式的双向链表结构对已free的堆块进行管理。关于此部分内容如有不清晰之处推荐阅读《Linux堆内存管理深入分析（上/下）》，在此不再赘述。

本文的重点在于libc对fastbin的管理与操作，其策略具有以下几个特点：首先它并不采用双向链接，而采用单向链表结构，也即chunk结构中fd，bk两个指针只用到的fd指针；在进行堆分配时，采用FILO的顺序从fastbin链表中取下堆块，因此其unlink操作没有unsorted bins那么复杂；如果malloc与free的size未超过某个阈值，则不会触发malloc_consolidate，即free后的fastbin堆块不与相邻堆块进行融合。

由于Linux为了效率而对fastbin管理的验证稍加放松，就导致它拥有一些相对简单的攻击方式。如果我们可以覆盖某个fastbin的堆头，将其fd指向任意地址，下次再申请两次，就可以将这个地址申请回来，这便是最基本的fastbin attack。除此之外对于fastbin还存在double free，house of spirit等攻击方式。



**3. Defcon Qualifier 之 Badint**

**3.1 简介**

此题是Defcon预选赛的一道pwn题，最后解出的队伍不算太多，算是比赛时一道分值比较高的题。前几天legitbs将Defcon预选赛的源码与二进制文件公开在了github上，需者可以自取[https://github.com/legitbs/quals-2017/tree/master/babyint](https://github.com/legitbs/quals-2017/tree/master/babyint)。

以下我们先从其功能开始分析、而后分析它的漏洞点、并一步一步拿到此服务的shell。

**3.2 程序功能逆向分析**

拿到二进制之后首先需要对其进行简单的功能性的分析。包括动态跑一下以及使用IDA静态分析弄清楚程序是干什么的。

此题程序功能可看成是模拟协议数据单元（PDU）的传输与重组，每轮循环需要我们输入seq_num , offset , pdu_data，这三者可组成一个segment，然后提示输入yes/no以选择是否进行segment的重组。示例输入与运行如下图：

[![](https://p3.ssl.qhimg.com/t01968fd891e87850ce.png)](https://p3.ssl.qhimg.com/t01968fd891e87850ce.png)

对于data部分数据只能输入[a-fA-F0-9]，程序在接收到data之后，将它们保存在栈上的一段缓冲区上，然后对将其进行一处unhex操作，将我们输入的12345678变成0x12 0x34 0x56 0x78并保存在从堆上分配的内存中，因而在这个操作中从堆上分配的空间大小为我们输入的字符串长度的1/2。

对于相同seq_num的Data，该程序会将它们保存在一个segmentData结构体中，并通过一个双向链表将其链起来。在选择Assemble之后，按照输入的offset将每一个seg中的data使用memncpy进行组合，然后将之打印输出。

以上即为程序所大概实现的功能。当然现在逆向的过程可以结合上面链接中的github源代码进行分析，这样可相互印证。

**3.3 漏洞点**

本程序可以说一共有三个漏洞点。第一个是一个Memory Leak（不是info leak）。通常做pwn题的时候我们需要关注程序明显不太正常的逻辑，因为这些有可能是出题人觉得不好做特意提供便利的地方或是设置漏洞的地方。

在程序将输入的data unhex之后，先将其保存到了堆上size为len/2大小的堆块上，而在创建segment的时候，又将此数据重新使用memncpy拷贝到了另一个新malloc出来的堆块之中。在选择重组该sequence之时，并未对新malloc的这块地址进行free，导致留下一个memory Leak，因而在多进行几个之后，堆块上将留下很多坑。而实际上并没有必要进行第二次malloc操作，这部分是完全多余的。

实际上这是为了方便fastbin在free之后不与top chunk融合而故意设置的，当然该操作也增加了堆布局的复杂度。

第二个漏洞发生在重组之时，对于seq_num相同的segments，程序会通过遍历将它们的data_ptr进行一一取出，并按照offset的值进行组合。在这个过程中程序未对offset的合法性进行校验,如下图：

[![](https://p0.ssl.qhimg.com/t012cf72153c77f2194.png)](https://p0.ssl.qhimg.com/t012cf72153c77f2194.png)

以我们刚才的输入为例，假如在第二次输入deadbeaf之时，将offset设为了8，或者更大的数值，就会造成越界写，将后面的内容覆盖掉。在我们完全掌握了堆的分配之后，便可以指定算好的offset，利用这个漏洞向指定的堆块写入想要写入的值了。

[![](https://p1.ssl.qhimg.com/t01e5705d208ac57a16.png)](https://p1.ssl.qhimg.com/t01e5705d208ac57a16.png)

第三个漏洞点同样在这段代码中，程序没有对这块存放重组后数据的堆块进行初始化，而后面会将这段缓冲区的内容经过printf输出出来，如果其中有些敏感数据，就可以被用来做信息泄露。后文的漏洞利用过程中也正用到了这个漏洞点。

**3.4 程序的堆操作**

以输入seq_num=0, Offset=0, Data=deadbeaf为例，堆的malloc与free操作应当如下：

1. data1 = malloc(4)# len("deadbeaf")=8, 在unhex函数中为data1分配内存

2. segment_ptr = malloc(0x28) # 创建segment结构体

3. data2 = malloc(4+1)# 为data2分配内存，然后将data1使用memcpy拷贝过去，再在segment结构体中保存data2的位置

4. free(data1)

5. total_data = malloc(4) # 确认重组，为总的数据分配足够容纳所有data的堆块，在这个例子中就是4

6. free(segment_ptr)

7. free(total_data)

以更直观的图表示在完成上述七个过程之后的堆块如下：

[![](https://p3.ssl.qhimg.com/t0120b9b12519cad65c.png)](https://p3.ssl.qhimg.com/t0120b9b12519cad65c.png)

需要注意由于堆分配时的对齐操作，在malloc(4)时它仍然会返回一个size为0x20大小的chunk，在malloc(0x28)时会返回一个0x30大小的chunk，这两者在free之后会被放到fastbins链表下。

其中0x61ac70-0x61ac90为data2的地址，由于未被free因而造成内存泄露，但是如果它被free了，那么就不会有上面的0x20、0x30的fastbin了，它们会全部与top chunk进行融合。

在这个过程中，可以发现total_data与data1所申请的地址是一样的，两者复用了0x61ac20，注意到这点很重要。

**3.5 漏洞利用**

接下来是如何通过这些漏洞去拿到shell。这是我们的最终目的，前面那些都是分析的基础。

对于本程序而言，我们可以想办法劫持控制流执行system("sh")来拿shell。由于可以通过输入控制堆块的大小，也存在溢出漏洞，因而实施fastbin attack是相当方便的，实际利用的时候可以有几种思路：覆盖got表劫持控制流；覆盖栈上函数返回地址，然后ROP劫持控制流； 覆盖malloc_hook、覆盖_IO_FILE等方式劫持控制流。由于本题并没有开FULL RELRO，因而可以考虑直观地覆盖got表中的内容，例如将atol改成system的地址，等到下一次触发atol且参数可控时，便可达到任意命令执行。

上面说的只是理论的利用方法，实际中需要的问题则可以归纳为“Write What Where”,where这个问题上面已经回答了，接下来解决what。

向GOT表中写system的地址首先需要知道system的地址是什么。这时候就需要一个信息泄露漏洞来将libc的基址泄露出来。

在本例子中，可以利用unsorted bin attack来泄露libc的指针，在第一次free一个大于0x80的堆块时，linux会将其加入unsorted bins链表中，并向其fd与bk处填入libc中的指针值。由于重组之后程序会将total_data采用十六进制的形式打印出来，加之上面提到total_data在与我们输入的data1大小一致时，会重新申请到data1的地址，且并进行初始化操作，如果我们发送的请求中offset等于或大于8，那么memcpy时data1中fd与bk指针就不会被覆盖，在进行print时，就可以将这个指向libc的值泄露出来，我们就可以拿到泄露出的信息。

如下，调试时可以看到data1 free后的情况：

[![](https://p2.ssl.qhimg.com/t011cdf2555254ec223.png)](https://p2.ssl.qhimg.com/t011cdf2555254ec223.png)

至此我们便拿到了main_arena+88的值，拿该值减掉main_arena+88在libc中的偏移，便可以得到libc的基址。

在泄露完之后堆的分布是这样的：

[![](https://p1.ssl.qhimg.com/t0130a62295f0077b14.png)](https://p1.ssl.qhimg.com/t0130a62295f0077b14.png)

为了达成fastbin attack，我们需要将某个fastbin的fd指针覆盖为我们可以控制的地址，因而需要继续操作上面的堆。当申请size小于0x80的chunk之时，malloc会先从fastbins中找，如果没有找到合适的，就去unsorted bins中找。例如，如果我们申请一个0x20的chunk，那么堆上0x90的unsorted bin就会被切分掉0x20大小，变成为一个0x70大小的堆块。

按照这些规则，如果我们发送下面这两个请求





```
new_pdu(0, 0, "AA"*0x10, True)
new_pdu(0, 0, "BB"*0x30, True)
```

堆块就会被分为下面这个图的形式。（中间过程请读者自行按照3.3中的规则去画）

[![](https://p2.ssl.qhimg.com/t015d83f5b31c78f7a1.png)](https://p2.ssl.qhimg.com/t015d83f5b31c78f7a1.png)

而在调试时可以发现，实际中堆布局并不如此，libc还有一个细节，在malloc(0x30)时，先发现0x40大小的fastbin是空的，继而去寻找unsorted bins，发现其中有一个0x50大小的chunk，本应该切分0x40的部分给malloc的返回值，而由于剩下的0x10大小会变成一个碎片，因而libc的策略是直接将这0x50的空间全部返回给申请者。因而实际上在进行上述两个new_pdu操作后，堆分布如下：

[![](https://p4.ssl.qhimg.com/t014496cfa0537b6504.png)](https://p4.ssl.qhimg.com/t014496cfa0537b6504.png)

调试状态中可以看到的确如此，

[![](https://p4.ssl.qhimg.com/t0178833ed6681d4399.png)](https://p4.ssl.qhimg.com/t0178833ed6681d4399.png)

至此我们已经成功地在0x40大小的fastbins中成功留下了一个堆块，我们千方百计达成此目的，因为libc在对fastbin的管理中还有一次检查操作，在从0x40大小的fastbin链表中取出堆块时，如果检测到该堆块的size不为0x40-0x4f,则会失败退出，因而我们覆盖的时候随便填一个值是不可行的,必须是伪造好size值的堆块，而在got表中，没有被resolve的函数地址所保存的值为plt表的地址，即0x40xxxx，经过指令对齐操作，便可以将其变成0x00000040，此时内存中便有一个DWORD的值为0x40，可用此绕过libc的检测。此处需注意libc的检查只需要满足低32位是0x4x即可，高32位即使有值也可以通过检查。

直接查看got表中0x604018的地址时，可得其中的值如下：

[![](https://p0.ssl.qhimg.com/t010e6085348dae2e4d.png)](https://p0.ssl.qhimg.com/t010e6085348dae2e4d.png)

但是在手动将其值调整一下时，可以得到这样的结果：

[![](https://p2.ssl.qhimg.com/t01e84938e44e01d6ac.png)](https://p2.ssl.qhimg.com/t01e84938e44e01d6ac.png)

在0x60404a处存储的值即为0x40。接着发送构造好的payload：

```
new_pdu(0, 0, "AA"*0x10, True)
new_pdu(0, 0, "BB"*0x30, True)
fake_fd = convert(0x604042) #0x60404a is 0xxxx00000000040 , 0x604042-&gt;size=0x40
offset  = 0x61adb0-0x61ac20
new_pdu(0, offset, fake_fd, True)
```

这段代码可以将上面构造的0x61adb0处fastbin的fd覆盖掉成0x60404a-8，下次申请两次，即可申请到这个伪造的堆块。此处需要减8，是因为在64位系统下，libc在取chunk-&gt;size的值时，实际上是进行的+8操作。

最后（终于到了最后），我们申请两次0x40大小的串即可向got表(0x60404a+8)。在写的过程中，可以选择将atol函数覆盖为任意地址，比如，system函数的地址。那么下次再输入seq_num等值时，就会触发system("your input")，从而达到任意命令执行的效果。这里需要注意为了使程序运行正常，需要先把got表中已经resolve的地方给换回去，换成plt表中相应的地址，关于这部分的内容可阅读《Linux中的GOT和PLT到底是个啥？》，英文原文《PLT and GOT – the key to code sharing and dynamic libraries》。

```
payload = "66"*6 # libc_start_main
payload += convert(0x400b26)  # resolve fgets 0x400b26
payload += convert(0x400b36)  # resolve strlen 0x400b36
payload += convert(libc_base + libc.symbols['system']) # hijack atol
payload = payload.ljust(0x60, '0')
new_pdu(0, 0, payload , False ) # payload
```

至此已经成功地将atol函数替换成了system的地址，接着，只需要再send("sh")，即可get shell。

```
io.sendlineafter("SEQ #:", "sh")
```

[![](https://p5.ssl.qhimg.com/t01efcd9df38ba86618.png)](https://p5.ssl.qhimg.com/t01efcd9df38ba86618.png)



**4. 总结**

本文所涉及的题目及exp代码已上传至云盘http://pan.baidu.com/s/1dE6wxXn 密码: w22h，若有不当之处恳请斧正。



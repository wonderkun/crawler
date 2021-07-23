> 原文链接: https://www.anquanke.com//post/id/184099 


# ret2dl_resolve解析


                                阅读量   
                                **403420**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t011dc5af98687a08f3.jpg)](https://p0.ssl.qhimg.com/t011dc5af98687a08f3.jpg)



ELF文件利用延迟绑定技术来解决动态程序模块与函数的重定位问题。`ret2dl_resolve`的原理是基于延迟绑定技术而形成的利用技巧，它通过伪造数据结构以及对函数延迟绑定过程的拦截，实现任意函数调用的目的。

本篇文章主要描述延迟绑定的原理、32位以及64位ELF文件的ret2dl_resolve技术。



## 延迟绑定技术

针对动态链接会减速程序运行速度的现状，操作系统实现了延迟绑定（Lazy Binding）的技术：函数第一次被用到时才对函数进行绑定。通过延迟绑定大大加快了程序的启动速度。而ELF 则使用了PLT（Procedure Linkage Table,过程链接表）的技术来实现延迟绑定。

下面根据一个程序具体来跟下程序看延迟绑定的实现，demo程序如下：

```
#include &lt;stdio.h&gt;
// gcc -m32 -g demo.c -o demo
int main()
`{`
    char data[20];
    read(0,data,20);
    return 0;
`}`
```

断点下在read函数调用的地方：

```
0x8048492 &lt;main+39&gt;    call   read@plt &lt;0x8048330&gt;
```

程序先调用`read[@plt](https://github.com/plt)`，查看此时read的plt表的内容：

```
pwndbg&gt; x/3i 0x8048330
   0x8048330 &lt;read@plt&gt;:        jmp    DWORD PTR ds:0x804a00c
   0x8048336 &lt;read@plt+6&gt;:      push   0x0
   0x804833b &lt;read@plt+11&gt;:     jmp    0x8048320
```

可以看到它直接跳转到了read的got表中的地址，此时read的got表中的刚好是`read[@plt](https://github.com/plt)`下一条地址的值`0x08048336`：

```
pwndbg&gt; x/wx 0x804a00c
0x804a00c:      0x08048336
```

如上面代码所示，`0x08048336`地址处的两条指令，将0压入栈中，并跳转到`0x8048320`地址执行：

```
0x8048336 &lt;read@plt+6&gt;:      push   0x0
0x804833b &lt;read@plt+11&gt;:     jmp    0x8048320
```

`0x8048320`为plt表的起始地址，称其为plt0，其指令为：

```
0x8048320                              push   dword ptr [_GLOBAL_OFFSET_TABLE_+4] &lt;0x804a004&gt;
0x8048326                              jmp    dword ptr [0x804a008] &lt;0xf7feed90&gt;
```

可以看到它将`got+4`的值压入到栈中，并跳转到了`got+8`的地方去执行。跟进去到`got+8`中的值`0xf7feed90`，可以看到程序进入到了`_dl_runtime_resolve`，因此`got+8`的地方存储的是`_dl_runtime_resolve`函数的地址。看`_dl_runtime_resolve`的源码，源码在`/sysdeps/i386/dl-trampoline.S`中：

```
0xf7feed90 &lt;_dl_runtime_resolve&gt;       push   eax
0xf7feed91 &lt;_dl_runtime_resolve+1&gt;     push   ecx
0xf7feed92 &lt;_dl_runtime_resolve+2&gt;     push   edx
0xf7feed93 &lt;_dl_runtime_resolve+3&gt;     mov    edx, dword ptr [esp + 0x10]
0xf7feed97 &lt;_dl_runtime_resolve+7&gt;     mov    eax, dword ptr [esp + 0xc]
0xf7feed9b &lt;_dl_runtime_resolve+11&gt;    call   _dl_fixup &lt;0xf7fe85a0&gt;
```

`_dl_runtime_resolve`在源码中是用汇编实现的只是压栈并调用`_dl_fixup`，在跟进去`_dl_fixup`前，先给出一些与动态链接相关的数据结构。

根据《程序员的自我修养》中的描述：动态链接中最重要的结构应该是`dynamic`段，这个段里面保存了动态链接器所需要的基本信息。比如依赖于哪些共享对象、动态链接符号表的位置、动态链接重定位表的位置、共享对象初始化代码的地址等。

使用readelf查看该demo文件中dynamic的信息如下：

[![](https://p0.ssl.qhimg.com/t01c08954bb68779c66.png)](https://p0.ssl.qhimg.com/t01c08954bb68779c66.png)

其是一个结构体数组，结构体的定义为：

```
typedef struct `{`
    Elf32_Sword     d_tag;
    union `{`
        Elf32_Word  d_val;
        Elf32_Addr  d_ptr;
    `}` d_un;
`}` Elf32_Dyn;
extern Elf32_Dyn_DYNAMIC[];
```

`Elf32_Dyn`结构由一个类型值加上一个附加的数值或指针，对于不同的类型，后面附加的数值或者指针有着不同的含义。下面给出和延迟绑定相关的类型值的定义。

<th style="text-align: center;">`d_tag`类型</th><th style="text-align: center;">`d_un`的定义</th>
|------
<td style="text-align: center;">`#define DT_STRTAB    5`</td><td style="text-align: center;">动态链接字符串表的地址，d_ptr表示`.dynstr`的地址 (Address of string table)</td>
<td style="text-align: center;">`#define DT_SYMTAB    6`</td><td style="text-align: center;">动态链接符号表的地址，d_ptr表示`.dynsym`的地址 (Address of symbol table)</td>
<td style="text-align: center;">`#define DT_JMPREL    23`</td><td style="text-align: center;">动态链接重定位表的地址,d_ptr表示`.rel.plt`的地址 (Address of PLT relocs)</td>
<td style="text-align: center;">`#define DT_RELENT    19`</td><td style="text-align: center;">单个重定位表项的大小，d_val表示单个重定位表项大小 (Size of one Rel reloc )</td>
<td style="text-align: center;">`#define DT_SYMENT    11`</td><td style="text-align: center;">单个符号表项的大小，d_val表示单个符号表项大小 (Size of one symbol table entry )</td>

如上图所示，可以看到字符串表`.dynstr`的地址为`0x804822c`，符号表`.dynsym`地址为`0x80481cc`，其单个符号表项的大小为`16`，重定位表`.rel.plt`的地址为 `0x80482d8`，其单个重定位表项的大小为`8`

`.rel.plt`重定位表中包含了需要重定位的函数的信息，其也是一个结构体数组，结构体`Elf32_Rel`定义如下，其中`r_offset`表示got表地址，即动态解析函数后真正的函数地址需要填入的地方，`r_info`由两部分构成，`r_info&gt;&gt;8`表示该函数对应在符号表`.dynsym`中的下标，`r_info&amp;0xff`则表示重定位类型。：

```
typedef struct `{`
    Elf32_Addr        r_offset;
    Elf32_Word       r_info;
`}` Elf32_Rel;
```

我们查看demo程序的重定位表`0x80482d8`:

```
pwndbg&gt; x/6wx 0x80482d8
0x80482d8:      0x0804a00c      0x00000107      0x0804a010      0x00000207
0x80482e8:      0x0804a014      0x00000407
```

以及使用`readelf -r`来查看demo程序的重定位表：

```
$ readelf -r demo
Relocation section '.rel.plt' at offset 0x2d8 contains 3 entries:
 Offset     Info    Type            Sym.Value  Sym. Name
0804a00c  00000107 R_386_JUMP_SLOT   00000000   read@GLIBC_2.0
0804a010  00000207 R_386_JUMP_SLOT   00000000   __stack_chk_fail@GLIBC_2.4
0804a014  00000407 R_386_JUMP_SLOT   00000000   __libc_start_main@GLIBC_2.0
```

可以看到重定位表`.rel.plt`为一个`Elf32_Rel`数组，demo程序中该数组包含三个元素，第一个是`read`的重定位表项`Elf32_Rel`结构体，第二个是`__stack_chk_fail`，第三个是`__libc_start_main`。`read`的重定位表`r_offset`为`0x0804a00c`，为`read`的got地址，即在动态解析函数完成后，将read的函数地址填入到`r_offset`为`0x0804a00c`中。`r_info`为`0x00000107`表示read函数的符号表为`.dynsym`数组中的`0x00000107&gt;&gt;8`（即`0x1`）个元素，它的类型为`0x00000107&amp;0xff`（即0x7）对应为`R_386_JUMP_SLOT`类型。

接着我们去看符号表`.dynsym`节，它也是一个结构体`Elf32_Sym`数组，其结构体的定义如下：

```
typedef struct
`{`
  Elf32_Word    st_name; //符号名，是相对.dynstr起始的偏移
  Elf32_Addr    st_value;
  Elf32_Word    st_size;
  unsigned char st_info; //对于导入函数符号而言，它是0x12
  unsigned char st_other;
  Elf32_Section st_shndx;
`}`Elf32_Sym; //对于导入函数符号而言，其他字段都是0
```

其中`st_name`指向的是函数名称在`.dynstr`表中的偏移。在`dynamic`段中我们知道了符号表`.dynsym`地址为`0x80481cc`，查看它的值：

```
pwndbg&gt; x/20wx 0x80481cc
0x80481cc:      0x00000000      0x00000000      0x00000000      0x00000000
0x80481dc:      0x0000002b      0x00000000      0x00000000      0x00000012
0x80481ec:      0x0000001a      0x00000000      0x00000000      0x00000012
0x80481fc:      0x00000042      0x00000000      0x00000000      0x00000020
0x804820c:      0x00000030      0x00000000      0x00000000      0x00000012
```

以及使用`readelf -s`查看符号表的内容：

```
$ readelf -s demo

Symbol table '.dynsym' contains 6 entries:
   Num:    Value  Size Type    Bind   Vis      Ndx Name
     0: 00000000     0 NOTYPE  LOCAL  DEFAULT  UND
     1: 00000000     0 FUNC    GLOBAL DEFAULT  UND read@GLIBC_2.0 (2)
     2: 00000000     0 FUNC    GLOBAL DEFAULT  UND __stack_chk_fail@GLIBC_2.4 (3)
     3: 00000000     0 NOTYPE  WEAK   DEFAULT  UND __gmon_start__
     4: 00000000     0 FUNC    GLOBAL DEFAULT  UND __libc_start_main@GLIBC_2.0 (2)
     5: 0804853c     4 OBJECT  GLOBAL DEFAULT   16 _IO_stdin_used
```

从重定位表`.rel.plt`中，我们知道了read的`r_info&gt;&gt;8`为0x1，即read的符号表项对应的是`.dynsym`第二个元素，果然可以看到`.dynsym`第一个元素为read函数的`Elf32_Sym`结构体，可以看到它的`st_name`对应的是`0x0000002b`，即`read`字符串应该在`.dynstr`表偏移为`0x2b`的地方，由`dynamic`我们知道了`.dynstr`表的地址为地址为`0x804822c`，去验证下看其偏移`0x2b`是否为`read`字符串：

```
pwndbg&gt; x/s 0x804822c+0x2b
0x8048257:      "read"
```

可以看到，确实如此。

到这里似乎对read函数的解析过程有了一个简单的了解：
- 可以先通过`dynamic`段获取各个表的地址，包括有字符串表`.dynstr`的地址为`0x804822c`，符号表`.dynsym`地址为`0x80481cc`，其单个符号表项的大小为`16`，重定位表`.rel.plt`的地址为 `0x80482d8`，其单个重定位表项的大小为`8`。
<li>
`read`函数为`.rel.plt`表中的第一个元素，定位它的重定位表项，知道了read函数的`r_offset`为`0x0804a00c`，以及它在符号表中的下标为`0x000001`，它的类型为`0x7`，`R_386_JUMP_SLOT`。</li>
- 由`0x000001`知道了`read`函数的符号表是`.dynsym`第二个元素，获取到该结构体，得到了它对应的`st_name`对应的是`0x0000002b`，即获取了`read`字符串应该在`.dynstr`表偏移为`0x2b`的地方。
- 最后调用函数解析匹配`read`字符串所对应的函数地址，将其填至`r_offset`为`0x0804a00c`，即read的got地址中。
有了前面的基础，现在可以跟进去`_dl_fixup`，我们知道在调用`_dl_runtime_resolve`函数之前压入到栈中的参数是0，以及`got+4`中的值，参考下面`_dl_fixup`的源码，根据参数列表，知道了眼乳栈中的`0`为`reloc_arg`，`got+4`中的值为`struct link_map *l`，函数源码在`/elf/dl-runtime.c`中：

```
_dl_fixup (struct link_map *l, ElfW(Word) reloc_arg)
`{`

  //获取符号表地址
  const ElfW(Sym) *const symtab= (const void *) D_PTR (l, l_info[DT_SYMTAB]);
  //获取字符串表地址
  const char *strtab = (const void *) D_PTR (l, l_info[DT_STRTAB]);
  //获取函数对应的重定位表结构地址
  const PLTREL *const reloc = (const void *) (D_PTR (l, l_info[DT_JMPREL]) + reloc_offset);
  //获取函数对应的符号表结构地址
  const ElfW(Sym) *sym = &amp;symtab[ELFW(R_SYM) (reloc-&gt;r_info)];
  //得到函数对应的got地址，即真实函数地址要填回的地址
  void *const rel_addr = (void *)(l-&gt;l_addr + reloc-&gt;r_offset);

  DL_FIXUP_VALUE_TYPE value;

  //判断重定位表的类型，必须要为7--ELF_MACHINE_JMP_SLOT
  assert (ELFW(R_TYPE)(reloc-&gt;r_info) == ELF_MACHINE_JMP_SLOT);

   /* Look up the target symbol.  If the normal lookup rules are not
      used don't look in the global scope.  */
   //需要绕过
  if (__builtin_expect (ELFW(ST_VISIBILITY) (sym-&gt;st_other), 0) == 0)
   `{`
      const struct r_found_version *version = NULL;

      if (l-&gt;l_info[VERSYMIDX (DT_VERSYM)] != NULL)
    `{`
      const ElfW(Half) *vernum =
        (const void *) D_PTR (l, l_info[VERSYMIDX (DT_VERSYM)]);
      ElfW(Half) ndx = vernum[ELFW(R_SYM) (reloc-&gt;r_info)] &amp; 0x7fff;
      version = &amp;l-&gt;l_versions[ndx];
      if (version-&gt;hash == 0)
        version = NULL;
    `}`

   ...

      // 接着通过strtab+sym-&gt;st_name找到符号表字符串
      result = _dl_lookup_symbol_x (strtab + sym-&gt;st_name, l, &amp;sym, l-&gt;l_scope,
                    version, ELF_RTYPE_CLASS_PLT, flags, NULL);

  ...
      // value为libc基址加上要解析函数的偏移地址，也即实际地址
      value = DL_FIXUP_MAKE_VALUE (result,
                   sym ? (LOOKUP_VALUE_ADDRESS (result)
                      + sym-&gt;st_value) : 0);
    `}`
  else
    `{`
      /* We already found the symbol.  The module (and therefore its load
     address) is also known.  */
      value = DL_FIXUP_MAKE_VALUE (l, l-&gt;l_addr + sym-&gt;st_value);
      result = l;
    `}`

...

  // 最后把value写入相应的GOT表条目rel_addr中
  return elf_machine_fixup_plt (l, result, reloc, rel_addr, value);
`}`
```

可以看到`_dl_fixup`函数就如上面描述的过程一般，去定位结构体，最终获取`read`字符串去libc中找到相应的函数地址并填回到got表中。

所以ELF文件的延迟绑定技术总结如下：

调用函数时，`call func[@plt](https://github.com/plt)`，plt表内容如下：

```
func@plt:
jmp *(func@GOT)   //仍然首先进行GOT跳转，尝试是否是第一次链接
push n        //压入需要地址绑定的符号在重定位表中的下标
jmp PLT0    //跳转到 PLT0
```

由于是第一次调用，`func[@GOT](https://github.com/GOT)`got表中的值为`jmp *(func[@GOT](https://github.com/GOT))`指令的下一条地址，即`push n`的地址，接着程序会执行`push n; jmp PLT0`，`n`则为该函数在`.rel.plt`表中的偏移。接着去看PLT0的指令为：

```
push *(got+4)
jmp *(got+8)
```

其中`got+4`存储的是`link_map`的地址，`got+8`存储的是`_dl_runtime_resolve`函数的地址。进入到`_dl_runtime_resolve`函数后，函数会调用`_dl_fixup`函数，根据源码分析，可以看到该函数功能为：
1. 程序先从第一个参数`link_map`获取字符串表`.dynstr`、符号表`.dynsym`以及重定位表`.rel.plt`的地址，
1. 通过第二个参数`n`即`.rel.plt`表中的偏移`reloc_arg`加上`.rel.plt`的地址获取函数对应的重定位结构的位置，从而获取函数对应的`r_offset`以及在符号表中的下标`r_info&gt;&gt;8`。
1. 根据符号表地址以及下标获取符号结构体，获得了函数符号表中的`st_name`，即函数名相对于字符串表`.dynstr`的偏移。
1. 最后可得到函数名的字符串，然后去libc中匹配函数名，找到相应的函数并将地址填回到`r_offset`即函数got表中，延迟绑定完成。


## 32位的ret2dl_resolve

### <a class="reference-link" name="%E5%8E%9F%E7%90%86"></a>原理

`ret2dl_resolve`的适用场景是在无法泄露程序地址时，通过拦截延迟绑定的过程，实现对函数地址解析过程的劫持，使得最终解析出来的函数为特定函数的函数地址，从而实现无泄露达到特定函数调用的目的。

32位ELF程序`ret2dl_resolve`攻击方法，目前最为普遍的是伪造`reloc_arg`，即伪造重定位表的下标实现相关的利用，具体包括如下步骤：
1. 伪造`reloc_arg`，使得`reloc_arg`加上`.rel.plt`的地址指向可控的地址，在该地址可伪造恶意的`Elf32_Rel`结构体。
1. 伪造`Elf32_Rel`结构体中的`r_offset`指向某一可写地址，最终函数地址会写入该地址处；伪造`r_info&amp;0xff`为0x7，因为类型需为`ELF_MACHINE_JMP_SLOT`以绕过类型验证；伪造`r_info&gt;&gt;8`，使得`r_info&gt;&gt;8`加上`.dynsym`地址指向可控的地址，并在该地址伪造符号表结构体`Elf32_Sym`。
1. 伪造`Elf32_Sym`结构体中的`st_name`，使得`.dynstr`的地址加上该值指向可控地址，并在该地址处写入特定函数的函数名入`system`。
1. 最终系统通过函数名匹配，定位到特定函数地址，获取该地址并写入到伪造的`r_offset`中，实现了函数地址的获取。
整个过程看起来比较简单，仍然需要注意一点的是`dl_fixup`中还存在以下一段代码：

```
if (__builtin_expect (ELFW(ST_VISIBILITY) (sym-&gt;st_other), 0) == 0)
   `{`
      const struct r_found_version *version = NULL;

      if (l-&gt;l_info[VERSYMIDX (DT_VERSYM)] != NULL)
    `{`
      const ElfW(Half) *vernum =
        (const void *) D_PTR (l, l_info[VERSYMIDX (DT_VERSYM)]);
      ElfW(Half) ndx = vernum[ELFW(R_SYM) (reloc-&gt;r_info)] &amp; 0x7fff;
      version = &amp;l-&gt;l_versions[ndx];
      if (version-&gt;hash == 0)
        version = NULL;
    `}`
```

如果`reloc-&gt;r_info`伪造不当，会使得`ndx = vernum[ELFW(R_SYM) (reloc-&gt;r_info)] &amp; 0x7fff`偏大，导致`version = &amp;l-&gt;l_versions[ndx]`出现访存错误，因此伪造的`reloc-&gt;r_info`，最好使得ndx为0，即vernum[reloc-&gt;r_info]为0。



## 实践—0ctf2018-babystack

这题只是一个简单的栈溢出，但是由于它是被python将程序运行起来，只是将读入的0x100字节数据给程序并没有将任何数据输出，无法进行泄露，因此想到了使用`ret2dl-resolve`来解这道题。

在bss段上选择一个地址伪造`Elf32_Sym`，使得由它得到的`ndx = vernum[ELFW(R_SYM) (reloc-&gt;r_info)]`为0。并在一个地址填入特定目标函数名称如`system`字符串，将其相对于`.dynstr`的地址的偏移填入到伪造的`Elf32_Sym`结构体中的`st_name`中。再伪造`Elf32_Rel`结构体，将`r_offset`伪造成想要写目标函数的地址，将`r_info&gt;&gt;8`构造成伪造的`Elf32_Sym`相对于`.dynsym`数组的偏移，将`r_info&amp;0xff`伪造成0x7。最后计算出伪造的`Elf32_Rel`结构体相对于`.rel.plt`的偏移，将该偏移压入栈中，最终调用plt0实现函数地址解析。

由于该程序无法输出，因此需要一个远程的vps来反弹shell或接收flag。

目前[roputils](https://github.com/inaz2/roputils)可以较好的支持构造ret2dl_resolve数据，但是它好像对于`ndx`这个没有考虑进去，参考`roputils`，[pwn_debug](https://github.com/ray-cp/pwn_debug)加入了对32位`ret2dl_resolve`数据的构造，提供`ret2dl_resolve`模块，其api`build_normal_resolve`会返回一个构造好的能够实现`ret2dl_resolve`攻击的数据，且其对应的ndx为0。



## 64位ELF程序的ret2dl_resolve

前面描述的是32位程序的ret2dl_resolve，64位程序是否一样可行？对于64位程序而言，理论上而言上述方法也是可行的，但是在实际构造的过程中，有一点是会是程序崩溃的，还是前面提到的那段代码：

```
if (__builtin_expect (ELFW(ST_VISIBILITY) (sym-&gt;st_other), 0) == 0)
   `{`
      const struct r_found_version *version = NULL;

      if (l-&gt;l_info[VERSYMIDX (DT_VERSYM)] != NULL)
    `{`
      const ElfW(Half) *vernum =
        (const void *) D_PTR (l, l_info[VERSYMIDX (DT_VERSYM)]);
      ElfW(Half) ndx = vernum[ELFW(R_SYM) (reloc-&gt;r_info)] &amp; 0x7fff;
      version = &amp;l-&gt;l_versions[ndx];
      if (version-&gt;hash == 0)
        version = NULL;
    `}`
```

因为64位程序构造的数据一般都是在bss段，如`0x601000-0x602000`,导致其相对于`.dynsym`的地址`0x400000-0x401000`很大，使得`reloc-&gt;r_info`也很大，最后使得访问`ElfW(Half) ndx = vernum[ELFW(R_SYM) (reloc-&gt;r_info)] &amp; 0x7fff;`时程序访存出错，导致程序崩溃。

根据代码可以使得`l-&gt;l_info[VERSYMIDX (DT_VERSYM)] != NULL`这句话不成立来绕过该段代码，即使得`l-&gt;l_info[VERSYMIDX (DT_VERSYM)]`等于`NULL`，即使得`(link_map + 0x1c8)` 处为 `NULL`。这就使问题变成了往`link_map`写空值，由于`link_map`在`ld.so`中，还需要泄露地址。因此实现64位的上述方法的ret2dl_resolve，需要泄露与地址写两个漏洞，如果有这两个漏洞我们应该可以使用更轻松的方法来get shell，因此价值不大。

那么是否还有其他方法？可以看到该段代码还有一个条件`if (__builtin_expect (ELFW(ST_VISIBILITY) (sym-&gt;st_other), 0) == 0)`，我们是否可构造`sym-&gt;st_other`使它不为空，从而绕过该段代码，我们看假设`sym-&gt;st_other`使它不为空，`dl_fixup`的代码流程：

```
_dl_fixup (struct link_map *l, ElfW(Word) reloc_arg)
`{`

  //获取符号表地址
  const ElfW(Sym) *const symtab= (const void *) D_PTR (l, l_info[DT_SYMTAB]);
  //获取字符串表地址
  const char *strtab = (const void *) D_PTR (l, l_info[DT_STRTAB]);
  //获取函数对应的重定位表结构地址
  const PLTREL *const reloc = (const void *) (D_PTR (l, l_info[DT_JMPREL]) + reloc_offset);
  //获取函数对应的符号表结构地址
  const ElfW(Sym) *sym = &amp;symtab[ELFW(R_SYM) (reloc-&gt;r_info)];
  //得到函数对应的got地址，即真实函数地址要填回的地址
  void *const rel_addr = (void *)(l-&gt;l_addr + reloc-&gt;r_offset);

  DL_FIXUP_VALUE_TYPE value;

  //判断重定位表的类型，必须要为7--ELF_MACHINE_JMP_SLOT
  assert (ELFW(R_TYPE)(reloc-&gt;r_info) == ELF_MACHINE_JMP_SLOT);
   /* Look up the target symbol.  If the normal lookup rules are not
      used don't look in the global scope.  */


  if (__builtin_expect (ELFW(ST_VISIBILITY) (sym-&gt;st_other), 0) == 0)
   `{`
     ...
    `}`
  else
    `{`
      /* We already found the symbol.  The module (and therefore its load
     address) is also known.  */
      value = DL_FIXUP_MAKE_VALUE (l, l-&gt;l_addr + sym-&gt;st_value);
      result = l;
    `}`

...

  // 最后把value写入相应的GOT表条目rel_addr中
  return elf_machine_fixup_plt (l, result, reloc, rel_addr, value);  
`}`
```

可以看到当`sym-&gt;st_other`不为0时，会调用`DL_FIXUP_MAKE_VALUE`，根据代码的注释，该代码认为这个符号已经解析过，直接调用`DL_FIXUP_MAKE_VALUE`函数赋值。`DL_FIXUP_MAKE_VALUE`函数的定义如下，直接将`l-&gt;l_addr + sym-&gt;st_value`赋值给`value`：

```
#define DL_FIXUP_MAKE_VALUE(map, addr) (addr)
/* Extract the code address from a value of type DL_FIXUP_MAKE_VALUE.
 */
```

也可以看到`sym`等都是从`link_map`中取出来的，如果我们将控制的目标不设定为`reloc_arg`，而是伪造第一个参数`link_map`。如果我们可以控制`sym-&gt;st_value`指向got表中的地址如`__libc_start_main`的got，而`l-&gt;l_addr`为目标地址如`system`到`__libc_start_main`的偏移，则最终得到的value会是`l-&gt;l_addr + sym-&gt;st_value`即system地址，从而实现无需leak地址的利用。

重新整理下利用思路，在利用中我们控制的不再是`reloc_arg`，而是`struct link_map *l`，假设我们可以覆盖`got+4`，即`link_map`的值，指向我们可控的目标。

首先看`link_map`的定义：

```
pwndbg&gt; print sizeof(*l)
$2 = 0x470

pwndbg&gt; ptype l
type = struct link_map `{`
    Elf64_Addr l_addr;
    char *l_name;
    Elf64_Dyn *l_ld;
    struct link_map *l_next;
    struct link_map *l_prev;
    struct link_map *l_real;
    Lmid_t l_ns;
    struct libname_list *l_libname;
    Elf64_Dyn *l_info[76];  //l_info 里面包含的就是动态链接的各个表的信息
    ...
    size_t l_tls_firstbyte_offset;
    ptrdiff_t l_tls_offset;
    size_t l_tls_modid;
    size_t l_tls_dtor_count;
    Elf64_Addr l_relro_addr;
    size_t l_relro_size;
    unsigned long long l_serial;
    struct auditstate l_audit[];
`}` *
```

我们最终的目标是伪造`sym`，使得`sym-&gt;st_value`的地址刚好指向got表中存在libc地址的值，如`__libc_start_main`，而`l-&gt;l_addr`存储的则是目标函数地址（`system`）与`__libc_start_main`的偏移，因此首先伪造`l-&gt;l_addr`为目标地址`system`与`__libc_start_main`的偏移。

接下来看`sym-&gt;st_value`如何构造才能指向`__libc_start_main`的got表的位置。我们看`sym`是如何得到的：

```
//获取符号表地址
  const ElfW(Sym) *const symtab= (const void *) D_PTR (l, l_info[DT_SYMTAB]);

 //获取函数对应的重定位表结构地址
  const PLTREL *const reloc = (const void *) (D_PTR (l, l_info[DT_JMPREL]) + reloc_offset);
  //获取函数对应的符号表结构地址
  const ElfW(Sym) *sym = &amp;symtab[ELFW(R_SYM) (reloc-&gt;r_info)];
```

最终`sym`是通过`&amp;symtab[ELFW(R_SYM) (reloc-&gt;r_info)]`得到的，我们能够控制link_map，为简单起见，我们可以控制`reloc-&gt;r_info`为0，因此现在问题就变成了如何控制`symtab`第一个元素的`st_value`指向`__libc_start_main`的got表的位置。`symtab`是`l_info[DT_SYMTAB]`，根据定义`#define DT_SYMTAB    6`，`symtab`即是`l_info[0x6]`，根据`Elf64_Dyn`以及`Elf64_Sym`的定义，我们可以构造`l_info[0x6]`指向`link_map+0x70`，同时在`link_map+0x78`的位置填入`__libc_start_main`got表地址减8的地址，这样就伪造了`DT_SYMTAB`对应的`Elf64_Dyn`为`link_map+0x70`，它的`d_ptr`为`link_map+0x78`，指向了`__libc_start_main_got-8`，即`symtab`指向了`__libc_start_main_got-8`，它的`st_value`偏移为8，因此实现了`st_value`指向了`__libc_start_main_got`，由于`symtab`指向了`__libc_start_main_got-8`，其地址一般仍然为got表地址，里面中的数据存在值，因此`sym-&gt;st_other`不为0的条件也是成立的。

```
pwndbg&gt; ptype Elf64_Dyn
type = struct `{`
    Elf64_Sxword d_tag;
    union `{`
        Elf64_Xword d_val;
        Elf64_Addr d_ptr;
    `}` d_un;
`}`

pwndbg&gt; ptype Elf64_Sym
type = struct `{`
    Elf64_Word st_name;
    unsigned char st_info;
    unsigned char st_other;
    Elf64_Section st_shndx;
    Elf64_Addr st_value;
    Elf64_Xword st_size;
`}`
```

最后再看写入地址`rel_addr`的由来：

```
//获取函数对应的重定位表结构地址
  const PLTREL *const reloc = (const void *) (D_PTR (l, l_info[DT_JMPREL]) + reloc_offset);
...
//得到函数对应的got地址，即真实函数地址要填回的地址
  void *const rel_addr = (void *)(l-&gt;l_addr + reloc-&gt;r_offset);
```

假设我们要将最终得到的地址写在`link_map+0x28`的位置，它最终是由`l-&gt;l_addr + reloc-&gt;r_offset`得到的，`l-&gt;l_addr`的值已经确定，为目标地址到got表中libc地址的偏移，因此要控制`reloc-&gt;r_offset`使得它加上`l-&gt;l_addr`为`link_map+0x28`的地址。`reloc = (const void *) (D_PTR (l, l_info[DT_JMPREL]) + reloc_offset`，因此要伪造`reloc`，假设将伪造的`reloc`设定在`link_map+0x30`处，其中`reloc_offset`已经确定，由相对应的函数的`reloc_arg`**0x8确定。因此我们要伪造`l_info[DT_JMPREL]`，根据定义`#define DT_JMPREL    23`，我们需要伪造`.rel.plt`表所对应的`Elf64_Dyn`结构体，我们将`l_info[DT_JMPREL]`指向`link_map+0x80-8`，即最后使得它对应的`d_ptr`为`link_map+0x80`，我们在`link_map+0x80`中写入`link_map+0x30-reloc_offset`的值，这样就使得`.rel.plt`表的地址为`link_map+0x30-reloc_offset`，最终经过`reloc = (const void **) (D_PTR (l, l_info[DT_JMPREL]) + reloc_offset`得到了`reloc`指向`link_map+0x30`，我们在`link_map+0x30`中构造伪造的`Elf64_Rela`结构体，并将`r_offset`填入`link_map+0x28`减去`l-&gt;l_addr`的值，最终得到`rel_addr`为`link_map+0x28`，同时将`r_info`填入`0x7`，以绕过前面对类型的判定。

```
pwndbg&gt; ptype Elf64_Rela
type = struct `{`
    Elf64_Addr r_offset;
    Elf64_Xword r_info;
    Elf64_Sxword r_addend;
`}`
```

最终形成了`sym-&gt;st_other`不为0，`rel_addr`指向`link_map+0x30`，`sym-&gt;st_value`地址为`__libc_start_main`got表的地址，`l-&gt;l_addr`为`system`到`__libc_start_main`的偏移，经过`value = DL_FIXUP_MAKE_VALUE (l, l-&gt;l_addr + sym-&gt;st_value);`，我们会得到value为`system`地址，并最后写入到了`rel_addr`即`link_map+0x30`中，实现对system函数的调用。

写的很绕，主要是里面结构体指针指来指去的，感觉自己也不太愿意回头再看一遍。。。。

### <a class="reference-link" name="%E5%AE%9E%E4%BE%8B%E2%80%94hitcon2015%E2%80%94blinkroot"></a>实例—hitcon2015—blinkroot

此题是ELF64程序，在bss段输入了一个0x400字节大小的数据。并给了一个任意地址写，由于使用了`movaps`指令，所以目标指令地址必须要16字节对齐。

由于没有泄露，只存在一次地址写任意值，且程序在读取输入后将输入、输出以及错误句柄都关闭了，所以考虑使用`ret2dl_resolve`攻击。因此考虑覆盖`link_map`指向bss段地址，通过伪造`link_map`实施上述的`ret2dl_resolve`攻击。

最后通过构造好的`link_map`，将`sym-&gt;st_value`地址为`__libc_start_main`got表的地址，`l-&gt;l_addr`为`system`到`__libc_start_main`的偏移，通过后面的`puts`调用实施`ret2dl_resolve`攻击，它所对应的`reloc_offset`为0x18，最终实现调用`system`反弹shell。

我也在`pwn_debug`中加入了伪造`link_map`的api`build_link_map`，方便较快的构造`link_map`。



## 小结

不得不说延迟绑定是一个比较绕的过程。特别是伪造它们的结构，由于指针的指来指去，感觉很绕，但是在理解了以后其实还是比较简单，也是能力不够，表述的比较粗糙，但也是尽力了。

exp和文件在[github](https://github.com/ray-cp/pwn_category/tree/master/stack/ret2dl_resolve)



## 参考链接
1. [ROP之return to dl-resolve](http://rk700.github.io/2015/08/09/return-to-dl-resolve/)
1. [ret2dl_resolve学习笔记](https://veritas501.space/2017/10/07/ret2dl_resolve%E5%AD%A6%E4%B9%A0%E7%AC%94%E8%AE%B0/)
1. [roputils/examples/dl-resolve-i386.py](https://github.com/inaz2/roputils/blob/master/examples/dl-resolve-i386.py)
1. [HITCON 2015 PWN 200 blinkroot](https://ddaa.tw/hitcon_pwn_200_blinkroot.html)
1. [https://gist.github.com/inaz2/fbff517fc639f69a4309f79506771849](https://gist.github.com/inaz2/fbff517fc639f69a4309f79506771849)
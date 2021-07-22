> 原文链接: https://www.anquanke.com//post/id/180280 


# PWN下如何查找函数的加载地址


                                阅读量   
                                **242626**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者uaf，文章来源：uaf.io
                                <br>原文地址：[https://uaf.io/exploitation/misc/2016/04/02/Finding-Functions.html](https://uaf.io/exploitation/misc/2016/04/02/Finding-Functions.html)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p0.ssl.qhimg.com/t011affe1003a645734.png)](https://p0.ssl.qhimg.com/t011affe1003a645734.png)



## 前言

(pwn场景中，译者注)查找某个函数地址的典型方法是:通过计算与同一库中另一个已泄露出地址的函数的偏移量，得到所需函数的地址。然而，要使此方法有效工作，远程服务器的gLibc版本需要与我们本地的版本相同。当然我们也可以通过泄漏一些函数并在libcdb.com中搜索找到匹配的gLibc版本，但有时这种方法会失败。



## DynELF

如果我们有一个函数允许我们在任何给定地址泄漏内存，我们可以通过[pwntools](http://pwntools.readthedocs.org/en/latest/about.html)/[binjitsu](https://github.com/binjitsu/binjitsu)使用类似[DynELF](http://pwntools.readthedocs.org/en/latest/dynelf.html)的工具来找到所需要的函数地址。如文档所述，DynELF主要使用了两种技术。它使用的第一种技术是：找到gLibc的基址，然后使用符号表和字符表解析所有的符号，直到找到我们要查找的函数的符号。

这里有一些细节我想放在一起公布出来，这是写这篇博客文章的真正原因:).



## 查找GNU C库的基本地址

要找到gLibc的基本地址，首先需要在gLibc的地址空间中获取一个地址。我们可以通过查看二进制文件的全局偏移表来获得已经解析的地址。接下来，我们可以使用内存页大小(0x1000)递减该地址，直到找到指示基本加载地址的x7fELF魔法常量。下面是实现这一点的示例代码:

```
# leak func returns n number of bytes from given address
def findLibcBase(ptr):
   ptr &amp;= 0xfffffffffffff000
   while leak(ptr, 4) != "x7fELF":
      ptr -= 0x1000
   return ptr
```



## 找到程序头

程序头包含一个结构体数组，结构体类型依据32/64架构分别为Elf32_Phdr/Elf64_Phdr，每个结构体包含二进制文件中现有段的信息。

要找到程序头的起始位置，只需查看ELF头(模块的基址)中偏移量0x1c(32位二进制)或0x20(64位二进制)的数据。

Elf32_Phdr结构体包含以下成员:

```
typedef struct `{`
        Elf32_Word      p_type;
        Elf32_Off       p_offset;
        Elf32_Addr      p_vaddr;
        Elf32_Addr      p_paddr;
        Elf32_Word      p_filesz;
        Elf32_Word      p_memsz;
        Elf32_Word      p_flags;
        Elf32_Word      p_align;
`}` Elf32_Phdr;
```

找到程序头开始的示例代码:

```
# addr argument is the module's base address or rather the beginning of ELF Header
def findPhdr(addr):
   if bits == 32:
      e_phoff = u32(leak(addr + 0x1c, wordSz).ljust(4, ''))
   else:
      e_phoff = u64(leak(addr + 0x20, wordSz).ljust(8, ''))
   return e_phoff + addr
```



## 找到动态节区

我们的下一个目标是找到满足特定条件的Elf32_Phdr结构，从而找到动态节区。

我们可以通过解析所有的程序头结构来实现这一点，直到找到满足Elf32_Phdr-&gt;p_type == 2的结构体地址。

一旦找到它，该结构体的Elf32_Phdr-&gt;p_vaddr成员就包含动态节区的虚拟地址。

找到动态节区的示例代码:

```
def findDynamic(Elf32_Phdr, bitSz):
   if bitSz == 32:
      i = -32
      p_type = 0
      while p_type != 2:
         i += 32
         p_type = u32(leak(Elf32_Phdr + i, wordSz).ljust(4, ''))
      return u32(leak(Elf32_Phdr + i + 8, wordSz).ljust(4, ''))    # + PIE
   else:
      i = -56
      p_type = 0
      while p_type != 2:
         i += 56
         p_type = u64(leak(Elf32_Phdr + i, hwordSz).ljust(8, ''))
      return u64(leak(Elf32_Phdr + i + 16, wordSz).ljust(8, ''))   # + PIE
```

对于开启了PIE保护(位置独立的可执行区域)的二进制程序，在Elf32_Phdr-&gt;p_vaddr将有一个到模块的基地址的偏移量。对于未开启pie的二进制文件，Elf32_Phdr-&gt;p_vaddr将有一个虚拟地址。

DYNAMIC部分包含一个Elf32_Dyn/Elf64_Dyn结构体数组。每个结构体都包含有关参与动态链接过程的节表的信息。其中包括DT_GOTPLT、DT_HASH、DT_STRTAB、DT_SYMTAB、DT_DEBUG等等。

我们感兴趣的动态节表是DT_SYMTAB aka符号表和DT_STRTAB aka字符串表。



## 查找DT_SYMTAB和DT_STRTAB

符号表包含一个Elf32_Sym/Elf64_Sym结构体数组。每个符号/函数都有一个结构。函数的加载地址可以在Elf32_Sym-&gt;st_value元素中找到。Elf32_Sym-&gt;st_name元素在DT_STRTAB中保存偏移量，DT_STRTAB是有关符号的字符串所在位置。

查找DT_STRTAB和DT_SYMTAB的示例代码:

```
def findDynTable(Elf32_Dyn, table, bitSz):
   p_val = 0
   if bitSz == 32:
      i = -8
      while p_val != table:
         i += 8
         p_val = u32(leak(Elf32_Dyn + i, wordSz).ljust(4, ''))
      return u32(leak(Elf32_Dyn + i + 4, wordSz).ljust(4, ''))
   else:
      i = -16
      while p_val != table:
         i += 16
         p_val = u64(leak(Elf32_Dyn + i, wordSz).ljust(8, ''))
      return u64(leak(Elf32_Dyn + i + 8, wordSz).ljust(8, ''))

DT_STRTAB = findDynTable(libcDynamic, 5, bits)

DT_SYMTAB = findDynTable(libcDynamic, 6, bits)
```



## 寻找函数地址

为了找到目标符号表，我们解析每个Elf32_Sym-&gt;st_name，直到DT_STRTAB[Elf32_Sym-&gt;st_name] == target_symbol。一旦条件成立，我们就找到了目标Elf32_Sym结构，现在我们只需查看Elf32_Sym-&gt;st_value元素来获得目标符号的加载地址。

示例代码片段:

```
def findSymbol(strtab, symtab, symbol, bitSz):
   if bitSz == 32:
      i = -16
      while True:
         i += 16
         st_name = u32(leak(symtab + i, 2).ljust(4, ''))
         if leak( strtab + st_name, len(symbol)+1 ).lower() == (symbol.lower() + ''):
            return u32(leak(symtab + i + 4, 4).ljust(4, ''))
   else:
      i = -24
      while True:
         i += 24
         st_name = u64(leak(symtab + i, 4).ljust(8, ''))
         if leak( strtab + st_name, len(symbol)).lower() == (symbol.lower()):
            return u64(leak(symtab + i + 8, 8).ljust(8, ''))
```



## 完整的例子

这里我们将从/proc/&lt;pid&gt;/mem中读取模拟泄漏函数的数据。使用上面的示例，让我们看看它如何找到系统的地址。

```
#!/usr/bin/env python

from pwn import *
import sys, os

wordSz = 4
hwordSz = 2
bits = 32
PIE = 0

def leak(address, size):
   with open('/proc/%s/mem' % pid) as mem:
      mem.seek(address)
      return mem.read(size)

def findModuleBase(pid, mem):
   name = os.readlink('/proc/%s/exe' % pid)
   with open('/proc/%s/maps' % pid) as maps: 
      for line in maps:
         if name in line:
            addr = int(line.split('-')[0], 16)
            mem.seek(addr)
            if mem.read(4) == "x7fELF":
               bitFormat = u8(leak(addr + 4, 1))
               if bitFormat == 2:
                  global wordSz
                  global hwordSz
                  global bits
                  wordSz = 8
                  hwordSz = 4
                  bits = 64
               return addr
   log.failure("Module's base address not found.")
   sys.exit(1)

def findIfPIE(addr):
   e_type = u8(leak(addr + 0x10, 1))
   if e_type == 3:
      return addr
   else:
      return 0

def findPhdr(addr):
   if bits == 32:
      e_phoff = u32(leak(addr + 0x1c, wordSz).ljust(4, ''))
   else:
      e_phoff = u64(leak(addr + 0x20, wordSz).ljust(8, ''))
   return e_phoff + addr

def findDynamic(Elf32_Phdr, moduleBase, bitSz):
   if bitSz == 32:
      i = -32
      p_type = 0
      while p_type != 2:
         i += 32
         p_type = u32(leak(Elf32_Phdr + i, wordSz).ljust(4, ''))
      return u32(leak(Elf32_Phdr + i + 8, wordSz).ljust(4, '')) + PIE
   else:
      i = -56
      p_type = 0
      while p_type != 2:
         i += 56
         p_type = u64(leak(Elf32_Phdr + i, hwordSz).ljust(8, ''))
      return u64(leak(Elf32_Phdr + i + 16, wordSz).ljust(8, '')) + PIE

def findDynTable(Elf32_Dyn, table, bitSz):
   p_val = 0
   if bitSz == 32:
      i = -8
      while p_val != table:
         i += 8
         p_val = u32(leak(Elf32_Dyn + i, wordSz).ljust(4, ''))
      return u32(leak(Elf32_Dyn + i + 4, wordSz).ljust(4, ''))
   else:
      i = -16
      while p_val != table:
         i += 16
         p_val = u64(leak(Elf32_Dyn + i, wordSz).ljust(8, ''))
      return u64(leak(Elf32_Dyn + i + 8, wordSz).ljust(8, ''))

def getPtr(addr, bitSz):
   with open('/proc/%s/maps' % sys.argv[1]) as maps: 
      for line in maps:
         if 'libc-' in line and 'r-x' in line:
            libc = line.split(' ')[0].split('-')
   i = 3
   while True:
      if bitSz == 32:
         gotPtr = u32(leak(addr + i*4, wordSz).ljust(4, ''))
      else:
         gotPtr = u64(leak(addr + i*8, wordSz).ljust(8, ''))
      if (gotPtr &gt; int(libc[0], 16)) and (gotPtr &lt; int(libc[1], 16)):
         return gotPtr
      else:
         i += 1
         continue

def findLibcBase(ptr):
   ptr &amp;= 0xfffffffffffff000
   while leak(ptr, 4) != "x7fELF":
      ptr -= 0x1000
   return ptr

def findSymbol(strtab, symtab, symbol, bitSz):
   if bitSz == 32:
      i = -16
      while True:
         i += 16
         st_name = u32(leak(symtab + i, 2).ljust(4, ''))
         if leak( strtab + st_name, len(symbol)+1 ).lower() == (symbol.lower() + ''):
            return u32(leak(symtab + i + 4, 4).ljust(4, ''))
   else:
      i = -24
      while True:
         i += 24
         st_name = u64(leak(symtab + i, 4).ljust(8, ''))
         if leak( strtab + st_name, len(symbol)).lower() == (symbol.lower()):
            return u64(leak(symtab + i + 8, 8).ljust(8, ''))

def lookup(pid, symbol):
   with open('/proc/%s/mem' % pid) as mem:
      moduleBase = findModuleBase(pid, mem)
   log.info("Module's base address:................. " + hex(moduleBase))

   global PIE
   PIE = findIfPIE(moduleBase)
   if PIE:
      log.info("Binary is PIE enabled.")
   else:
      log.info("Binary is not PIE enabled.")

   modulePhdr = findPhdr(moduleBase)
   log.info("Module's Program Header:............... " + hex(modulePhdr))

   moduleDynamic = findDynamic(modulePhdr, moduleBase, bits) 
   log.info("Module's _DYNAMIC Section:............. " + hex(moduleDynamic))

   moduleGot = findDynTable(moduleDynamic, 3, bits)
   log.info("Module's GOT:.......................... " + hex(moduleGot))

   libcPtr = getPtr(moduleGot, bits)
   log.info("Pointer from GOT to a function in libc: " + hex(libcPtr))

   libcBase = findLibcBase(libcPtr)
   log.info("Libc's base address:................... " + hex(libcBase))

   libcPhdr = findPhdr(libcBase)
   log.info("Libc's Program Header:................. " + hex(libcPhdr))

   PIE = findIfPIE(libcBase)
   libcDynamic = findDynamic(libcPhdr, libcBase, bits)
   log.info("Libc's _DYNAMIC Section:............... " + hex(libcDynamic))

   libcStrtab = findDynTable(libcDynamic, 5, bits)
   log.info("Libc's DT_STRTAB Table:................ " + hex(libcStrtab))

   libcSymtab = findDynTable(libcDynamic, 6, bits)
   log.info("Libc's DT_SYMTAB Table:................ " + hex(libcSymtab))

   symbolAddr = findSymbol(libcStrtab, libcSymtab, symbol, bits)
   log.success("%s loaded at address:.............. %s" % (symbol, hex(symbolAddr + libcBase)))


if __name__ == "__main__":
   log.info("Manual usage of pwnlib.dynelf")
   if len(sys.argv) == 3:
      pid = sys.argv[1]
      symbol = sys.argv[2]
      lookup(pid, symbol)
   else:
      log.failure("Usage: %s PID SYMBOL" % sys.argv[0])
```

示例输出:

```
➜  ~ python ./DynELF_manual.py 29530 system
[*] Manual usage of pwnlib.dynelf
[*] Module's base address:................. 0x400000
[*] Binary is not PIE enabled.
[*] Module's Program Header:............... 0x400040
[*] Module's _DYNAMIC Section:............. 0x602e08
[*] Module's GOT:.......................... 0x603000
[*] Pointer from GOT to a function in libc: 0x7ffff743ddd0
[*] Libc's base address:................... 0x7ffff741c000
[*] Libc's Program Header:................. 0x7ffff741c040
[*] Libc's _DYNAMIC Section:............... 0x7ffff77d9ba0
[*] Libc's DT_STRTAB Table:................ 0x7ffff742cd78
[*] Libc's DT_SYMTAB Table:................ 0x7ffff741fd28
[+] system loaded at address:.............. 0x7ffff7462640
➜  ~

```



## Link_map结构体

DynELF所使用的另一种查找动态段的方法是使用link_map结构。Link_map是动态链接器的内部结构，用于跟踪加载的库和库中的符号。

```
struct link_map
`{`
   ElfW(Addr) l_addr;                  /* Difference between the address in the ELF
                                       file and the addresses in memory.  */
   char *l_name;                       /* Absolute file name object was found in.  */
   ElfW(Dyn) *l_ld;                    /* Dynamic section of the shared object.  */
   struct link_map *l_next, *l_prev;   /* Chain of loaded objects.  */
`}`;
```

关于上面字段的说明:

1.l_addr:加载共享对象的基本地址。这个值也可以从/proc//maps中找到<br>
2.l_name:指向共享库中动态节区的指针<br>
3.l_next:指向下一个link_map节点的指针<br>
4.l_prev:指向前一个link_map节点的指针

我们可以在GOT表的第二项中找到link_map结构：

[![](https://p5.ssl.qhimg.com/t01c9d0c5f2f2a2bc6c.jpg)](https://p5.ssl.qhimg.com/t01c9d0c5f2f2a2bc6c.jpg)

在运行时，这个地址将由运行时链接器填充，我们可以在这里看到：

```
gdb-peda$ x/4wx 0x804b000
0x804b000:  0x0804af14  0xf7ffd938  0xf7ff04f0  0x080484c6
gdb-peda$
```

GOT表的第一项是模块动态部分的地址。GOT表的第二项是link_map的虚拟地址（上图中箭头所指部分，译者注），GOT表的第三项是运行时解析器函数的地址(我们将在接下来讨论)。

因此，如果我们遍历链表，直到link_map-&gt;l_name包含加载的gLibc库的完整路径，我们就可以在link_map-&gt;l_ld元素中找到gLibc的动态部分，并在link_map-&gt;l_addr中找到gLibc的基本地址。

```
gdb-peda$ x/4wx 0x804b000
0x804b000:  0x0804af14  0xf7ffd938  0xf7ff04f0  0x080484c6
gdb-peda$ x/4wx 0xf7ffd938
0xf7ffd938: 0x00000000  0xf7ffdc24  0x0804af14  0xf7ffdc28
gdb-peda$ x/4wx 0xf7ffdc28
0xf7ffdc28: 0xf7fdd000  0xf7ffde94  0xf7fdb350  0xf7fda858
gdb-peda$ x/4wx 0xf7fda858
0xf7fda858: 0xf7e1e000  0xf7fda838  0xf7fc7da8  0xf7ffd55c
gdb-peda$ x/s 0xf7fda838
0xf7fda838: "/lib/i386-linux-gnu/libc.so.6"
gdb-peda$ vmmap libc
Start      End        Perm Name
0xf7e1e000 0xf7fc6000 r-xp /lib/i386-linux-gnu/libc-2.19.so
0xf7fc6000 0xf7fc8000 r--p /lib/i386-linux-gnu/libc-2.19.so
0xf7fc8000 0xf7fc9000 rw-p /lib/i386-linux-gnu/libc-2.19.so
gdb-peda$
```

在上面的代码片段中，我们在遍历了3个link_map结构之后找到了libc的link_map，它的基址位于link_map-&gt;l_addr == 0xf7e1e000，动态节区位于link_map-&gt;l_ld == 0xf7fc7da8，加载模块的完整路径为link_map-&gt;l_name == “/lib/i386-linux-gnu/libc.so.6”

在开启了RELRO(read only relocation）保护的二进制程序中link_map看起来不在GOT表中了，但是由于多谢这篇[stackoverflow](http://reverseengineering.stackexchange.com/questions/6525/elf-link-map-when-linked-as-relro)上的文章，我才知道我们可以在位于动态节区的DT_DEBUG表中找到它。

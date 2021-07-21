> 原文链接: https://www.anquanke.com//post/id/234437 


# 从零开始学习fuzzing之拥有快照/代码覆盖率指引的Fuzzer


                                阅读量   
                                **141563**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者h0mbre，文章来源：h0mbre.github.io
                                <br>原文地址：[https://h0mbre.github.io/Fuzzing-Like-a-Caveman-4﻿](https://h0mbre.github.io/Fuzzing-Like-a-Caveman-4%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01a26895dd8cd92a0d.png)](https://p5.ssl.qhimg.com/t01a26895dd8cd92a0d.png)



之前看到安全客平台有[zoemurmure](http://www.anquanke.com/member/140346)师傅翻译的《从零开始学习fuzzing》系列文章，但是只翻译到了第三篇。这个系列的文章读着感到酣畅淋漓，从最基础的代码开始，让人很容易理解一个模糊测试器的诞生，使人欲罢不能。然后看到英文原版博客有了第四和第五章，遂尝试翻译引入填坑，也算是和大家一起交流，因为还是个大三的本科生，翻译不好之处，还请各位师傅批评指正。



## 一、前言

在上一篇文章中，我们一起编写了一个简单笨拙的模糊测试器。我们将它用来测了一个容易遭受攻击的程序，这个程序将对文件执行一些检查，如果输入文件通过了检查，它将前进到下一个检查，并且如果输入通过了所有检查，程序将出现段错误。上一篇文章中，我们还发现了代码覆盖率的重要性，以及它如何帮助我们提升我们模拟测试器的效率，将测试过程发现崩溃事件的难度从指数级降为线性级。接下来这篇文章，就让我们现在开始了解如何继续改进我们的愚蠢的模糊测试器！

在此特别感谢[@gamozolabs](https://github.com/gamozolabs)提供的所有内容，是他使我迷上了这个主题。



## 二、性能

首先，我们愚蠢的模糊测试器慢得要命。如果你还记得我们上个文章的测试结果的话，应该回忆起我们愚蠢的模糊测试器平均每秒大约能发起1500次模糊测试样例。而在我的测试过程中，当使用QEMU模式下（用于测试没有源代码的二进制文件）的AFL大约每秒能发起1000次模糊测试样例。这个情况是正常的，因为AFL做的事情远远比我们的愚蠢的模糊测试器要多得多，何况它还是处于使用模拟CPU以给二进制文件测试提供代码覆盖率的QEMU模式下。

我们的目标二进制文件（-&gt; [HERE](https://gist.github.com/h0mbre/db209b70eb614aa811ce3b98ad38262d) &lt;-）将执行以下操作：
- 从磁盘上的文件中提取字节到缓冲区
- 对缓冲区执行3次检查，以查看所检查的索引是否与硬编码值匹配
- 如果所有检查均通过，则触发段错误；如果其中一项检查失败，则退出
我们的愚蠢的模糊测试器将执行以下操作：
- 提取磁盘上的jpeg文件到缓冲区中
- 通过随机字节覆盖来更改缓冲区中2％的字节
- 将变异的文件写入磁盘
- 通过每次fuzzing迭代执行`fork()`和`execvp()`，将修改后的文件提供给目标二进制文件
如你所见，这是大量的文件系统交互和系统调用。让我们在脆弱的二进制文件上使用strace，看看系统调用这个二进制文件做了什么（在这篇文章中，我将.jpeg文件硬编码到脆弱的二进制文件中，这样我们就不必使用命令行参数来方便测试）：

```
execve("/usr/bin/vuln", ["vuln"], 0x7ffe284810a0 /* 52 vars */) = 0
brk(NULL)                               = 0x55664f046000
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
access("/etc/ld.so.preload", R_OK)      = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/etc/ld.so.cache", O_RDONLY|O_CLOEXEC) = 3
fstat(3, `{`st_mode=S_IFREG|0644, st_size=88784, ...`}`) = 0
mmap(NULL, 88784, PROT_READ, MAP_PRIVATE, 3, 0) = 0x7f0793d2e000
close(3)                                = 0
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
openat(AT_FDCWD, "/lib/x86_64-linux-gnu/libc.so.6", O_RDONLY|O_CLOEXEC) = 3
read(3, "\177ELF\2\1\1\3\0\0\0\0\0\0\0\0\3\0&gt;\0\1\0\0\0\260\34\2\0\0\0\0\0"..., 832) = 832
fstat(3, `{`st_mode=S_IFREG|0755, st_size=2030544, ...`}`) = 0
mmap(NULL, 8192, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x7f0793d2c000
mmap(NULL, 4131552, PROT_READ|PROT_EXEC, MAP_PRIVATE|MAP_DENYWRITE, 3, 0) = 0x7f079372c000
mprotect(0x7f0793913000, 2097152, PROT_NONE) = 0
mmap(0x7f0793b13000, 24576, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_DENYWRITE, 3, 0x1e7000) = 0x7f0793b13000
mmap(0x7f0793b19000, 15072, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x7f0793b19000
close(3)                                = 0
arch_prctl(ARCH_SET_FS, 0x7f0793d2d500) = 0
mprotect(0x7f0793b13000, 16384, PROT_READ) = 0
mprotect(0x55664dd97000, 4096, PROT_READ) = 0
mprotect(0x7f0793d44000, 4096, PROT_READ) = 0
munmap(0x7f0793d2e000, 88784)           = 0
fstat(1, `{`st_mode=S_IFCHR|0620, st_rdev=makedev(136, 0), ...`}`) = 0
brk(NULL)                               = 0x55664f046000
brk(0x55664f067000)                     = 0x55664f067000
write(1, "[&gt;] Analyzing file: Canon_40D.jp"..., 35[&gt;] Analyzing file: Canon_40D.jpg.
) = 35
openat(AT_FDCWD, "Canon_40D.jpg", O_RDONLY) = 3
fstat(3, `{`st_mode=S_IFREG|0644, st_size=7958, ...`}`) = 0
fstat(3, `{`st_mode=S_IFREG|0644, st_size=7958, ...`}`) = 0
lseek(3, 4096, SEEK_SET)                = 4096
read(3, "\v\260\v\310\v\341\v\371\f\22\f*\fC\f\\\fu\f\216\f\247\f\300\f\331\f\363\r\r\r&amp;"..., 3862) = 3862
lseek(3, 0, SEEK_SET)                   = 0
write(1, "[&gt;] Canon_40D.jpg is 7958 bytes."..., 33[&gt;] Canon_40D.jpg is 7958 bytes.
) = 33
read(3, "\377\330\377\340\0\20JFIF\0\1\1\1\0H\0H\0\0\377\341\t\254Exif\0\0II"..., 4096) = 4096
read(3, "\v\260\v\310\v\341\v\371\f\22\f*\fC\f\\\fu\f\216\f\247\f\300\f\331\f\363\r\r\r&amp;"..., 4096) = 3862
close(3)                                = 0
write(1, "[&gt;] Check 1 no.: 2626\n", 22[&gt;] Check 1 no.: 2626
) = 22
write(1, "[&gt;] Check 2 no.: 3979\n", 22[&gt;] Check 2 no.: 3979
) = 22
write(1, "[&gt;] Check 3 no.: 5331\n", 22[&gt;] Check 3 no.: 5331
) = 22
write(1, "[&gt;] Check 1 failed.\n", 20[&gt;] Check 1 failed.
)   = 20
write(1, "[&gt;] Char was 00.\n", 17[&gt;] Char was 00.
)      = 17
exit_group(-1)                          = ?
+++ exited with 255 +++
```

你可以看到，在处理目标二进制文件的过程中，我们甚至在打开输入文件之前就运行了大量代码。在运行以下系统调用之前，我们甚至不会打开输入文件:

```
execve
brk
access
access
openat
fstat
mmap
close
access
openat
read
opeant
read
fstat
mmap
mmap
mprotect
mmap
mmap
arch_prctl
mprotect
mprotect
mprotect
munmap
fstat
brk
brk
write
```

在所有这些系统调用执行完毕之后，我们最终从磁盘打开文件，从strace输出中读取以下字节:

```
openat(AT_FDCWD, "Canon_40D.jpg", O_RDONLY) = 3
```

所以请记住，我们愚蠢的模糊测试器在每一次模糊迭代中都将运行这些系统调用。我们愚蠢的模糊测试器（-&gt; [HERE](https://gist.github.com/h0mbre/0873edec8346122fc7dc5a1a03f0d2f1) &lt;-）每次迭代都会将一个文件写入磁盘，并使用`fork() + execvp()`生成目标程序的实例。有漏洞的目标二进制文件将运行所有上述的系统调用，并最终在每次迭代时从磁盘读取文件。这样，每个单次模糊测试迭代就有几十个系统调用和两个文件系统交互，难怪我们愚蠢的模糊测试器运行得这么慢。



## 三、基本的快照机制

我开始考虑如果在模糊测试这样一个简单的目标二进制程序中节省时间加快测试的速度，然后我想到也许我可以找出一种方法，可以获得程序的一个内存快照。这个内存快照的状态是当程序已经读取存在磁盘中的文件，并将文件已经存储在内存的堆上。这样我就可以保存程序运行到此的进程状态，然后手动将存储在内存堆上的文件替换成模糊测试的样例，之后让程序运行直到到达`exit()`调用退出为止。一旦目标程序命中了`exit`调用，我便会将程序状态倒回至捕获快照时的状态，并插入新的模糊测试样例，然后再重新进行一次上述的过程。

你将会看到这样如何提高我们模糊测试的性能。我们将跳过所有目标二进制程序的启动开销，并完全绕过所有文件系统交互。与之前的模糊测试器巨大的不同是，我们将只执行一次`fork()`系统调用，这是一个代价昂贵的系统调用。假设有我们共有100,000次模糊测试迭代，我们原来的模糊测试器将有200,000次文件系统交互（在一次模糊测试迭代中，一次文件系统交互是让愚蠢的模糊测试器在磁盘上创建一个`mutated.jpeg`，一个是让目标二进制程序读取`mutated.jpeg`），而我们改良过的模糊测试器将不会进行任何的文件系统交互，且有初始的`fork()`系统调用，极大的降低了系统的开销。

总之，我们的fuzzing过程应该是这样的：
1. 启动目标二进制文件，但在任何东西运行之前，在第一条指令时中断
1. 设置”开始“和”结束”位置上的断点（“开始”的位置是从磁盘上读取完毕文件后，“结束”的位置将是执行`exit()`后）
1. 运行程序，直到达到“开始”断点
1. 将进程的所有可写内存段收集到一个缓冲区中
1. 捕获所有寄存器状态
1. 将我们的模糊测试样例插入到内存堆中，覆盖程序从磁盘中读取的文件
1. 恢复执行目标二进制文件，直到达到“结束”断点
1. 将程序状态倒退到“开始”的位置
1. 从第6步开始重复
我们仅执行步骤1-5仅一次，所以程序在这个部分不需要非常快。步骤6-9是模糊器将花费99%时间的地方，所以我们需要使得程序在这个部分尽快完成。



## 四、用Ptrace编写一个简单的调试器

为了实现我们的快照机制，我们需要使用非常直观的`ptrace()`接口，尽管看起来很慢而且限制很大。几周前，当我开始编写fuzzer的调试器部分时，我非常依赖[Eli Bendersky](https://twitter.com/elibendersky)的这篇[博客文章](https://eli.thegreenplace.net/2011/01/23/how-debuggers-work-part-1)，这篇文章介绍了`ptrace()`接口并展示了如何通过`ptrace()`创建一个简单的调试器。

### <a class="reference-link" name="4.1%20%E6%96%AD%E7%82%B9"></a>4.1 断点

我们代码的调试器部分实际上并不需要太多功能，实际上只需要能够插入断点和删除断点即可。`ptrace()`设置和删除断点的方法是使用操作码`int3`也就是单字节`\xCC`覆盖目标地址。但是如果我们只是在设置断点时覆盖了目标地址的值，则之后我们将无法删除该断点，因为我们并没有保存目标地址原来的值，所以我们也没办法恢复已经被`\xCC`覆盖的内存

为了开始使用`ptrace()`，我们使用`fork()`生成第二个进程。

```
pid_t child_pid = fork();
if (child_pid == 0) `{`
    //we're the child process here
    execute_debugee(debugee);
`}`
```

现在，我们需要让父进程“跟踪”子进程。这是通过`PTRACE_TRACEME`参数完成的，我们将在`execute_debugee`函数内部使用该参数：

```
// request via PTRACE_TRACEME that the parent trace the child
long ptrace_result = ptrace(PTRACE_TRACEME, 0, 0, 0);
if (ptrace_result == -1) `{`
    fprintf(stderr, "\033[1;35mdragonfly&gt;\033[0m error (%d) during ", errno);
    perror("ptrace");
    exit(errno);
`}`
```

这个函数的其余部分不再涉及`ptrace()`，但我将继续在这里展示它，因为有一个重要的函数可以在debuggee进程中强制禁用ASLR。这一点至关重要，因为我们是一旦确定一个断点的地址，它是一个静态的值，我们无法在每个进程中都动态的更改这个值，所以我们需要关闭ASLR使得每一个进程中的内存布局都是一致的。我们通过调用`personality()`函数并使用参数`ADDR_NO_RANDOMIZE`来禁用ASLR。另外，我们将把`stdout`和`stderr`重定向流到`/dev/null`，以免混淆目标二进制文件的输出。

```
// disable ASLR
int personality_result = personality(ADDR_NO_RANDOMIZE);
if (personality_result == -1) `{`
    fprintf(stderr, "\033[1;35mdragonfly&gt;\033[0m error (%d) during ", errno);
    perror("personality");
    exit(errno);
`}`

// dup both stdout and stderr and send them to /dev/null
int fd = open("/dev/null", O_WRONLY);
dup2(fd, 1);
dup2(fd, 2);
close(fd);

// exec our debugee program, NULL terminated to avoid Sentinel compilation
// warning. this replaces the fork() clone of the parent with the 
// debugee process 
int execl_result = execl(debugee, debugee, NULL);
if (execl_result == -1) `{`
    fprintf(stderr, "\033[1;35mdragonfly&gt;\033[0m error (%d) during ", errno);
    perror("execl");
    exit(errno);
`}`
```

首先，我们需要一种方法在插入断点之前获取地址上的一个字节的值。在这个模糊测试器中，我开发了名字为`ptrace_helpers`的头文件和源文件，以帮助简化开发过程中使用`ptrace()`。我们获取那一个字节的值，我们将在地址处提取64比特长度的值，但只关心最右边（也就是最后一个）字节的值。（因为我正在使用`long long unsigned`类型，这是在`&lt;sys/user.h&gt;`中定义寄存器值的方式，我想使所有内容保持相同）

```
long long unsigned get_value(pid_t child_pid, long long unsigned address) `{`

    errno = 0;
    long long unsigned value = ptrace(PTRACE_PEEKTEXT, child_pid, (void*)address, 0);
    if (value == -1 &amp;&amp; errno != 0) `{`
        fprintf(stderr, "dragonfly&gt; Error (%d) during ", errno);
        perror("ptrace");
        exit(errno);
    `}`

    return value;    
`}`
```

然后，这个函数将使用`PTRACE_PEEKTEXT`参数来读取位于子进程（`child_pid`）中的地址的值，该子进程是我们的目标进程。现在我们有了这个值，我们可以保存它，然后用下面的代码插入断点：

```
void set_breakpoint(long long unsigned bp_address, long long unsigned original_value, pid_t child_pid) `{`

    errno = 0;
    long long unsigned breakpoint = (original_value &amp; 0xFFFFFFFFFFFFFF00 | 0xCC);
    int ptrace_result = ptrace(PTRACE_POKETEXT, child_pid, (void*)bp_address, (void*)breakpoint);
    if (ptrace_result == -1 &amp;&amp; errno != 0) `{`
        fprintf(stderr, "dragonfly&gt; Error (%d) during ", errno);
        perror("ptrace");
        exit(errno);
    `}`
`}`
```

你可以看到，这个函数将取前面函数收集到的原始值，并执行两个按位操作以保持前7个字节不变，然后将最后一个字节替换为`\xCC`。请注意，我们现在正在使用`PTRACE_POKETEXT`。这个`ptrace()`接口令人沮丧的地方之一是我们一次只能读取和写入8个字节！

因此，既然我们可以设置断点，那么我们需要实现的最后一个功能就是删除断点，这将需要`int3`用原始字节值覆盖。

```
void revert_breakpoint(long long unsigned bp_address, long long unsigned original_value, pid_t child_pid) `{`

    errno = 0;
    int ptrace_result = ptrace(PTRACE_POKETEXT, child_pid, (void*)bp_address, (void*)original_value);
    if (ptrace_result == -1 &amp;&amp; errno != 0) `{`
        fprintf(stderr, "dragonfly&gt; Error (%d) during ", errno);
        perror("ptrace");
        exit(errno);
    `}`
`}`
```

再次使用`PTRACE_POKETEXT`，我们可以`\xCC`用原始字节值覆盖。因此，现在我们可以设置和删除断点了。

最后，我们需要一种在被调试进程中恢复执行的方法。这可以通过使用`ptrace()`中的`PTRACE_CONT`参数来实现，如下所示：

```
void resume_execution(pid_t child_pid) `{`

    int ptrace_result = ptrace(PTRACE_CONT, child_pid, 0, 0);
    if (ptrace_result == -1) `{`
        fprintf(stderr, "dragonfly&gt; Error (%d) during ", errno);
        perror("ptrace");
        exit(errno);
    `}`
`}`
```

需要注意的一个重要的事情是，如果我们在地址`0x000000000000000`命中一个断点，`rip`实际上将在`0x0000000000000001`。因此，在将被覆盖的指令恢复到之前的值之后，我们还需要在恢复执行之前从`rip`中减去1，我们将在下一节中通过`ptrace`来学习如何做到这一点。

现在让我们学习如何利用`ptrace`和`/proc`伪文件来创建目标的快照！

### <a class="reference-link" name="4.2%20%E4%BD%BF%E7%94%A8ptrace%E5%92%8C/proc%E7%94%9F%E6%88%90%E5%BF%AB%E7%85%A7"></a>4.2 使用ptrace和/proc生成快照

#### <a class="reference-link" name="4.2.1%20%E4%BD%BF%E7%94%A8ptrace%E5%88%9B%E5%BB%BA%E5%AF%84%E5%AD%98%E5%99%A8%E7%8A%B6%E6%80%81%E5%BF%AB%E7%85%A7"></a>4.2.1 使用ptrace创建寄存器状态快照

`ptrace()`的另一个很酷的特性是能够捕获和设置被调试进程中的寄存器状态。我们可以使用我放在`ptrace_helpers.c`中封装好的`helpe`r函数来做这两件事：

```
// retrieve register states
struct user_regs_struct get_regs(pid_t child_pid, struct user_regs_struct registers) `{`                                                                                     
    int ptrace_result = ptrace(PTRACE_GETREGS, child_pid, 0, &amp;registers);
    if (ptrace_result == -1) `{`
        fprintf(stderr, "dragonfly&gt; Error (%d) during ", errno); 
        perror("ptrace");
        exit(errno);      
    `}`

    return registers;             
`}`
```

```
// set register states
void set_regs(pid_t child_pid, struct user_regs_struct registers) `{`

    int ptrace_result = ptrace(PTRACE_SETREGS, child_pid, 0, &amp;registers);
    if (ptrace_result == -1) `{`
        fprintf(stderr, "dragonfly&gt; Error (%d) during ", errno);
        perror("ptrace");
        exit(errno);
    `}`
`}`
```

结构体`user_regs_struct`定义在`&lt;sys/user.h&gt;`中。你可以看到，我们分别使用`PTRACE_GETREGS`和`PTRACE_SETREGS`来检索寄存器数据和设置寄存器数据。当我们拥有了这两个函数后，我们可以通过创建一个`user_regs_struct`结构体来创建一个寄存器值的快照；当我们到达“结束”断点时，我们将能够还原寄存器状态（`rip`是最重要的），从而恢复快照保存的程序状态

#### <a class="reference-link" name="4.2.2%20%E4%BD%BF%E7%94%A8/proc%E5%88%9B%E5%BB%BA%E5%8F%AF%E5%86%99%E5%86%85%E5%AD%98%E6%AE%B5%E7%8A%B6%E6%80%81%E5%BF%AB%E7%85%A7"></a>4.2.2 使用/proc创建可写内存段状态快照

既然我们已经有了一种捕获寄存器状态的方法，那么我们还需要一种为快照捕获可写内存状态的方法。我通过与`/proc`伪文件交互来实现这一点。我使用GDB在执行检查vuln的第一个函数上设置了断点，因为这个函数很重要，它是在`vuln`从磁盘中读取`jpeg`文件后的地址，将用作我们作为“开始”位置的断点。一旦我们在GDB中设置断点中断，我们可以通过`cat /proc/$pid/maps`，以查看内存是如何在进程中映射的（请注意，在使用GDB调试中也需要采用与我们之前相同的方法来强制禁用ASLR）。我们通过`grep`筛选出可以读写的内存区段（即可以使用我们的模糊测试样例覆盖的地方）：

```
h0mbre@pwn:~/fuzzing/dragonfly_dir$ cat /proc/12011/maps | grep rw
555555756000-555555757000 rw-p 00002000 08:01 786686                     /home/h0mbre/fuzzing/dragonfly_dir/vuln
555555757000-555555778000 rw-p 00000000 00:00 0                          [heap]
7ffff7dcf000-7ffff7dd1000 rw-p 001eb000 08:01 1055012                    /lib/x86_64-linux-gnu/libc-2.27.so
7ffff7dd1000-7ffff7dd5000 rw-p 00000000 00:00 0 
7ffff7fe0000-7ffff7fe2000 rw-p 00000000 00:00 0 
7ffff7ffd000-7ffff7ffe000 rw-p 00028000 08:01 1054984                    /lib/x86_64-linux-gnu/ld-2.27.so
7ffff7ffe000-7ffff7fff000 rw-p 00000000 00:00 0 
7ffffffde000-7ffffffff000 rw-p 00000000 00:00 0                          [stack]
```

这就是内存的七个不同部分。你会注意到，`heap`是其中的一部分。我们的模糊测试样例将被插入到`heap`中，但需要注意的一点是`heap`的地址，在我们模糊测试器中与GDB调试器中看到的地址不同。我认为这可能是由于两个调试器之间的某种环境变量差异所致。如果我们使用GDB在`check_one()`中下断点，我们可以看到`rax`是一个指向输入开头的指针，在本例中是`Canon_40D.jpg`。

```
$rax   : 0x00005555557588b0  →  0x464a1000e0ffd8ff
```

该指针`0x00005555557588b0`位于堆中。因此，我所要做的就是找出这个指针在我们的调试器/模糊测试器中的位置，在同一点上中断并使用`ptrace()`来检索`rax`值。

我在`check_one`上下断点，然后打开`/proc/$pid/maps`，来获得可写内存部分在程序中的偏移量，然后打开`/proc/$pid/mem`并从这些偏移量中读取缓冲区以存储可写内存。这段代码存储在一个名为`snapshot.c`的源文件中，该文件包含一些用于捕获快照和恢复快照的定义和函数。对于这一部分，捕获可写内存，我使用了以下定义和函数：

```
unsigned char* create_snapshot(pid_t child_pid) `{`

    struct SNAPSHOT_MEMORY read_memory = `{`
        `{`
            // maps_offset
            0x555555756000,
            0x7ffff7dcf000,
            0x7ffff7dd1000,
            0x7ffff7fe0000,
            0x7ffff7ffd000,
            0x7ffff7ffe000,
            0x7ffffffde000
        `}`,
        `{`
            // snapshot_buf_offset
            0x0,
            0xFFF,
            0x2FFF,
            0x6FFF,
            0x8FFF,
            0x9FFF,
            0xAFFF
        `}`,
        `{`
            // rdwr length
            0x1000,
            0x2000,
            0x4000,
            0x2000,
            0x1000,
            0x1000,
            0x21000
        `}`
    `}`;  

    unsigned char* snapshot_buf = (unsigned char*)malloc(0x2C000);

    // this is just /proc/$pid/mem
    char proc_mem[0x20] = `{` 0 `}`;
    sprintf(proc_mem, "/proc/%d/mem", child_pid);

    // open /proc/$pid/mem for reading
    // hardcoded offsets are from typical /proc/$pid/maps at main()
    int mem_fd = open(proc_mem, O_RDONLY);
    if (mem_fd == -1) `{`
        fprintf(stderr, "dragonfly&gt; Error (%d) during ", errno);
        perror("open");
        exit(errno);
    `}`

    // this loop will:
    //  -- go to an offset within /proc/$pid/mem via lseek()
    //  -- read x-pages of memory from that offset into the snapshot buffer
    //  -- adjust the snapshot buffer offset so nothing is overwritten in it
    int lseek_result, bytes_read;
    for (int i = 0; i &lt; 7; i++) `{`
        //printf("dragonfly&gt; Reading from offset: %d\n", i+1);
        lseek_result = lseek(mem_fd, read_memory.maps_offset[i], SEEK_SET);
        if (lseek_result == -1) `{`
            fprintf(stderr, "dragonfly&gt; Error (%d) during ", errno);
            perror("lseek");
            exit(errno);
        `}`

        bytes_read = read(mem_fd,
            (unsigned char*)(snapshot_buf + read_memory.snapshot_buf_offset[i]),
            read_memory.rdwr_length[i]);
        if (bytes_read == -1) `{`
            fprintf(stderr, "dragonfly&gt; Error (%d) during ", errno);
            perror("read");
            exit(errno);
        `}`
    `}`

    close(mem_fd);
    return snapshot_buf;
`}`
```

可以看到，我硬编码了所有的偏移量和各节的长度。请记住，这并不需要很快。我们只捕获一次快照，这可以让我们与文件系统交互。所以我们将循环这7个偏移量和长度，并把它们都写进一个名为`snapshot_buf`的缓冲区，它将存储在我们的模糊测试器的内存堆中。所以现在我们有了进程从`check_one`开始时的寄存器状态和内存状态。（我们的`start`断点）

现在让我们弄清楚当到达“结束”断点时如何还原快照。

#### <a class="reference-link" name="4.2.3%20%E6%81%A2%E5%A4%8D%E5%BF%AB%E7%85%A7"></a>4.2.3 恢复快照

为了恢复进程的内存状态，我们可以用同样的方式写入`/proc/$pid/mem` ;但是，由于我们现在正在每次模糊测试中都进行此操作，因此这部分需要快速进行。因为在每次模糊的迭代过程中如果有与对文件系统进行交互都会使我们花费大量时间。幸运的是，从Linux内核3.2版开始，就支持了一种更快的，进程到进程的内存读写API，，我们可以利用这个称为`process_vm_writev()`的API。由于这个进程直接与另一个进程一起工作，不遍历内核，也不涉及文件系统，因此它将大大提高写入速度。

乍一看有点让人困惑，但是手册页示例确实是您了解它如何工作所需要的全部，我选择了硬编码所有的偏移量，因为这个模糊器只是一个POC。我们可以恢复可写内存如下：

```
void restore_snapshot(unsigned char* snapshot_buf, pid_t child_pid) `{`

    ssize_t bytes_written = 0;
    // we're writing *from* 7 different offsets within snapshot_buf
    struct iovec local[7];
    // we're writing *to* 7 separate sections of writable memory here
    struct iovec remote[7];

    // this struct is the local buffer we want to write from into the 
    // struct that is 'remote' (ie, the child process where we'll overwrite
    // all of the non-heap writable memory sections that we parsed from 
    // proc/$pid/memory)
    local[0].iov_base = snapshot_buf;
    local[0].iov_len = 0x1000;
    local[1].iov_base = (unsigned char*)(snapshot_buf + 0xFFF);
    local[1].iov_len = 0x2000;
    local[2].iov_base = (unsigned char*)(snapshot_buf + 0x2FFF);
    local[2].iov_len = 0x4000;
    local[3].iov_base = (unsigned char*)(snapshot_buf + 0x6FFF);
    local[3].iov_len = 0x2000;
    local[4].iov_base = (unsigned char*)(snapshot_buf + 0x8FFF);
    local[4].iov_len = 0x1000;
    local[5].iov_base = (unsigned char*)(snapshot_buf + 0x9FFF);
    local[5].iov_len = 0x1000;
    local[6].iov_base = (unsigned char*)(snapshot_buf + 0xAFFF);
    local[6].iov_len = 0x21000;

    // just hardcoding the base addresses that are writable memory
    // that we gleaned from /proc/pid/maps and their lengths
    remote[0].iov_base = (void*)0x555555756000;
    remote[0].iov_len = 0x1000;
    remote[1].iov_base = (void*)0x7ffff7dcf000;
    remote[1].iov_len = 0x2000;
    remote[2].iov_base = (void*)0x7ffff7dd1000;
    remote[2].iov_len = 0x4000;
    remote[3].iov_base = (void*)0x7ffff7fe0000;
    remote[3].iov_len = 0x2000;
    remote[4].iov_base = (void*)0x7ffff7ffd000;
    remote[4].iov_len = 0x1000;
    remote[5].iov_base = (void*)0x7ffff7ffe000;
    remote[5].iov_len = 0x1000;
    remote[6].iov_base = (void*)0x7ffffffde000;
    remote[6].iov_len = 0x21000;

    bytes_written = process_vm_writev(child_pid, local, 7, remote, 7, 0);
    //printf("dragonfly&gt; %ld bytes written\n", bytes_written);
`}`
```

因此，对于7个不同的可写部分，我们将从我们在`snapshot_buf`中保存的原始快照数据按照规定的偏移量覆写到进程的`/proc/$pid/maps`，从而恢复快照数据，而且这将是一个十分快速的过程！

现在我们已经能够恢复可写内存了，我们现在只需要恢复寄存器状态，就可以完成基本的快照机制了。使用我们编写的`ptrace_helpers`函数将使得这个过程变得很容易，你可以看到我们的模糊测试器循环中的两个函数调用如下：

```
// restore writable memory from /proc/$pid/maps to its state at Start
restore_snapshot(snapshot_buf, child_pid);

// restore registers to their state at Start
set_regs(child_pid, snapshot_registers);
```

这就是我们的快照过程的工作原理，在我的测试中，我们的傻瓜模糊测试器提高了20-30倍的速度！



## 五、让我们愚蠢的模糊测试器变得聪明

到此为止，我们拥有的仍然只是一个简陋的模糊测试器（尽管现在速度变得很快了）。我们使得它变得更聪明，我们需要能够跟踪代码覆盖率。一种非常简单的方法是在`check_one`和`exit`之间的每个’`basic block`处放置一个断点，这样当我们到达新代码时，就会到达一个断点，我们可以在那里执行`do_something()`。

这也正是我之后改进的方法，为了简单起见，我只是在从`check_two`到`check_three`的入口点放置“动态”（用来统计代码覆盖率的）断点。当到达一个“动态”断点时，我们将到达代码的输入保存到一个名为`corpus`的`char`指针数组中，现在我们可以开始对那些保存到`corpus`的输入作为种子进行变异，不仅仅是对我们的“原型”`Canon_40D.jpg`输入进行变异。

因此，我们的代码覆盖率反馈机制将像这样工作：
1. 用原始数据作为种子进行变异作为测试样例插入内存堆中
1. 恢复被测试进程继续运行
1. 如果触发“动态”断点，则将输入保存到语料库中
1. 如果语料库中保存的语料数量大于1，则下一次生成测试样例将从原始数据和语料库中随机选择一个作为变异种子，然后从步骤1开始重复
我们还必须删除“动态”断点，这样我们就不会再重复触发它而引发中断。好在我们已经知道如何做好这件事了！

正如你在上一篇文章中所记得的，拥有代码覆盖率的功能对于我们的模糊测试器测试我们之前编写的测试程序的能力至关重要，因为这个测试程序需要经过三层检测，在它崩溃之前必须通过所有的比较。我们在上一篇文章中计算出通过第一次检查的概率约为1 / 13000，通过前两次检查的概率约为1 / 1.7亿。而当我们保存了通过check_1的输入并进一步修改它，我们可以将通过check_2的概率降低到接近1 / 13000的数值。这也适用于如果我们能保存通过`check_two`的输入并在此上进行变异作下一步操作，这将使得我们可以轻松到达并通过`check_three`然后触发崩溃。



## 六、开始模糊测试

我们的模糊测试器的第一阶段可以收集快照数据并为获得代码覆盖率设置“动态”断点，即使它还不是那么迅速，但相对之前的版本而言也算是非常快速的了。这是因为所有的值都是硬编码的，因为我们的目标非常简单。如果我们的目标是一个复杂的多线程程序，我们就可能需要通过`Ghidra`、`objdump`或其他方式来发现合适的断点地址，并且我们的模糊测试器将能够支持编写配置文件，但我们目前离这个目标还很遥远。但是对于我们目前的POC的情况，这个模糊测试器还是可以很好的进行工作的。

```
h0mbre@pwn:~/fuzzing/dragonfly_dir$ ./dragonfly 

dragonfly&gt; debuggee pid: 12156
dragonfly&gt; setting 'start/end' breakpoints:

   start-&gt; 0x555555554b41
   end  -&gt; 0x5555555548c0

dragonfly&gt; set dynamic breakpoints: 

           0x555555554b7d
           0x555555554bb9

dragonfly&gt; collecting snapshot data
dragonfly&gt; snapshot collection complete
dragonfly&gt; press any key to start fuzzing!
```

你可以看到，我们的模糊测试器可以帮助我们方便的查看”开始”和”结束”断点的地址，并为我们列出测试代码覆盖率的“动态”断点，以便我们可以在进行模糊测试之前检查它们是否正确。模糊测试器暂停并等待我们按任意键开始模糊测试。我们还可以看到快照数据收集已成功完成，至此，我们在”开始“地址下了断点并中断在这里，并拥有了开始进行模糊测试所需的所有数据。

按下回车键后，我们将获得统计信息输出，该信息向我们显示了模糊的进行情况：

```
dragonfly&gt; stats (target:vuln, pid:12156)

fc/s       : 41720
crashes    : 5
iterations : 0.3m
coverage   : 2/2 (%100.00)
```

正如你所看到的，它几乎可以立即找到“动态”断点，并且目前在CPU时间内每秒运行大约41k次模糊测试迭代（这比我们之前的愚蠢的模糊测试器快20-30倍）。

最重要的是，你可以看到我们仅用30万次迭代就已经使二进制文件崩溃了5次！我们以前的模糊测试器永远做不到。



## 七、结论

对我来说，这样做的最大收获之一就是，如果你只是针对一个特定目标定制一个模糊器，你可以定制优化你的模糊器从而获得更多的性能。使用像AFL这样的开箱即用的框架是很棒的，它们是令人难以置信的令人印象深刻的工具，我希望我们的这个模糊器有一天能成长为类似的工具。对于这个简单的目标，我们能够比AFL快20-30倍，并且通过一点逆向工程和定制就能几乎立刻让它崩溃。我觉得这很简洁，很有启发性。将来，当我为一个真正的目标调整这个模糊器时，我应该能够再次优于框架。



## 八、改进的想法

从哪里开始？我们在很多方面需要改进，但可以立即进行以下改进：
- 通过重构代码，更改全局变量的位置来优化性能
- 可以通过Python脚本创建配置文件来使得模糊测试器拥有动态配置的功能
- 采用更多的变异方法
- 采用更多的代码覆盖机制
- 开发可并行化运行实例的模糊测试器，使得多个并行化实例副本共享发现的输入/覆盖数据
也许我们会在随后的文章中看到这些改进，以及使用相同的方法取模糊测试一个真实的目标并获得结果。一定会有那一天的，加油！



## 九、代码

可以在以下位置找到此博客文章的所有代码：[https://github.com/h0mbre/Fuzzing/tree/master/Caveman4](https://github.com/h0mbre/Fuzzing/tree/master/Caveman4)

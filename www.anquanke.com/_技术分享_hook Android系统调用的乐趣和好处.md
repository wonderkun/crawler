> 原文链接: https://www.anquanke.com//post/id/85375 


# 【技术分享】hook Android系统调用的乐趣和好处


                                阅读量   
                                **190724**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：vantagepoint.sg
                                <br>原文地址：[https://www.vantagepoint.sg/blog/82-hooking-android-system-calls-for-pleasure-and-benefit](https://www.vantagepoint.sg/blog/82-hooking-android-system-calls-for-pleasure-and-benefit)

译文仅供参考，具体内容表达以及含义原文为准

****

**[![](https://p5.ssl.qhimg.com/t01be974f663eba3332.jpg)](https://p5.ssl.qhimg.com/t01be974f663eba3332.jpg)**

**翻译：**[**myswsun******](http://bobao.360.cn/member/contribute?uid=2775084127)

**预估稿费：200RMB**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

**<br>**

**0x00 前言**

Android的内核是逆向工程师的好伙伴。虽然常规的Android应用被限制和沙盒化，逆向工程师可以按自己希望自定义和改变操作系统和内核中行为。这给了你不可多得的优势，因为大部分完整性校验和防篡改功能都依赖内核的服务。部署这种可以滥用信任并自我欺骗的内核和环境，可以避免走很多歪路。

Android应用有几种方式和系统环境交互。标准方法是通过安卓应用框架的API函数。然而在底层，很多重要的函数，例如分配内存和访问文件，都是被转化为linux的系统调用。在ARM linux中，系统调用的调用是通过SVC指令触发软件中断实现的。中断调用内核函数vector_swi()，用系统调用号作为一个函数指针表的偏移（如安卓上的sys_call_table）。

拦截系统调用最直接的方法是注入你的代码到内核内存中，覆盖系统调用表中的原始函数地址重定向执行。不幸的是，目前Android内核加强了内存限制阻止了这种操作。具体来说，内核是在启用CONFIG_STRICT_MEMORY_RWX选项的情况下构建的。这阻止了向只读内核内存区写入，意味着任何试图修改系统代码或者系统调用表的操作都将导致崩溃和重启。绕过这个的一个方法就是自己编译内核：能够禁用这种保护，做更多自定义的修改有利于逆向分析。如果你按常规方法逆向Android应用，构建你自己的逆向沙盒是不明智的。

注意：下面的步骤是最好在Ubuntu 14.04环境中用Android NDK 4.8完成。我个人在Mac上面失败了很多次才完成。我推荐用Ubuntu虚拟机，除非你是个受虐狂。

<br>

**0x01 构建内核**

为了hack的目的，我推荐使用支持[AOSP](https://source.android.com/)的设备。Google的Nexus智能手机和平板电脑是最合理的选择，从AOSP构建的内核和系统组件在上面运行没有问题。另外，索尼的Xperia也可以。为了构建AOSP内核，需要一系列[工具](https://developer.android.com/ndk/downloads/index.html)（交叉编译工具）和相应的内核源代码。根据[谷歌的指导](https://source.android.com/source/initializing.html)，确定了正确的git仓库和分支。

例如，获取匹配Nexus 5的Lollipop的内核源码，需要克隆“msm”仓库并检出一个分支“android-msm-hammerhead”。一旦源码下载了，用make hammerhead_defconfig(或者whatever_defconfig，取决于你的设备)命令创建默认内核配置。

```
$ git clone https://android.googlesource.com/kernel/msm.git
$ cd msm
$ git checkout origin/android-msm-hammerhead-3.4-lollipop-mr1 
$ export ARCH=arm 
$ export SUBARCH=arm
$ make hammerhead_defconfig
$ vim .config
```

为了启动系统调用挂钩功能，我推荐增加可加载模块的支持，由/dev/kmem接口支持，同时导出全局内核符号表。不要忘了禁用内存保护。这些选项的值在配置文件中已经存在，只需要简单的设置以下值。

```
CONFIG_MODULES=Y
CONFIG_MODULE_UNLOAD=y
CONFIG_STRICT_MEMORY_RWX=N
CONFIG_DEVMEM=Y
CONFIG_DEVKMEM=Y
CONFIG_KALLSYMS=Y
CONFIG_KALLSYMS_ALL=Y
```

一旦你完成了编辑配置文件。或者，您现在可以创建一个独立的工具链，用于交叉编译内核和以后的任务。为了给Android 5.1创建一个工具链，运行Android NDK包的make-standalone_toolchain.sh：

```
$ cd android-ndk-rXXX
$ build/tools/make-standalone-toolchain.sh --arch=arm --platform=android-21 --install-dir=/tmp/my-android-toolchain
```

设置CROSS_COMPILE环境变量，指向NDK目录，并运行make构建内核。



```
$ export CROSS_COMPILE=/tmp/my-android-toolchain/bin/arm-eabi- 
$ make
```

当构建过程完成后，能在arch/arm/boot/zImage-dtb找到引导内核模块。



**0x02 启动新内核**

在启动新内核前，备份一个你设备的原始引导映像。找到启动分区的位置：

```
root@hammerhead:/dev # ls -al /dev/block/platform/msm_sdcc.1/by-name/         
lrwxrwxrwx root     root              1970-08-30 22:31 DDR -&gt; /dev/block/mmcblk0p24
lrwxrwxrwx root     root              1970-08-30 22:31 aboot -&gt; /dev/block/mmcblk0p6
lrwxrwxrwx root     root              1970-08-30 22:31 abootb -&gt; /dev/block/mmcblk0p11
lrwxrwxrwx root     root              1970-08-30 22:31 boot -&gt; /dev/block/mmcblk0p19
(...)
lrwxrwxrwx root     root              1970-08-30 22:31 userdata -&gt; /dev/block/mmcblk0p28
```

然后，将所有的内容转储到一个文件中：

```
$ adb shell "su -c dd if=/dev/block/mmcblk0p19 of=/data/local/tmp/boot.img"
$ adb pull /data/local/tmp/boot.img
```

接下来，提取ramdisk以及有关引导映像结构的一些信息。有很多工具可以做到这个，我使用Gilles Grandou的[abootimg](https://github.com/gerasiov/abootimg-android)工具。安装工具并执行以下的命令：

```
$ abootimg -x boot.img
```

在本地目录会创建bootimg.cfg、initrd.img和zImage（原始的内核）文件。

能用快速引导测试新内核。“fastboot boot”命令允许测试内核。在fastboot模式下用下面命令汗重启设备：

```
$ adb reboot bootloader
```

然后，用“fastboot boot”命令引导Android的新内核。除了新建的内核和原始ramdisk，还需指定内核偏移量，ramdisk偏移量，标签偏移量和命令行（使用在之前提取的bootimg.cfg中列出的值）。

```
$ fastboot boot zImage-dtb initrd.img --base 0 --kernel-offset 0x8000 --ramdisk-offset 0x2900000 --tags-offset 0x2700000 -c "console=ttyHSL0,115200,n8 androidboot.hardware=hammerhead user_debug=31 maxcpus=2 msm_watchdog_v2.enable=1"
```

现在应该手动重启。为了快速验证内核=正确运行了，通过校验Settings-&gt;About phone中的“内核版本”的值。

[![](https://p0.ssl.qhimg.com/t01fd7a9f87a4d1f700.jpg)](https://p0.ssl.qhimg.com/t01fd7a9f87a4d1f700.jpg)

如果一切运行良好，将显示自定义构建的版本字符串。

<br>

**0x03 用内核模块hook系统调用**

hook系统调用能让我们绕过任何依赖内核提供的反逆向防御措施。在我们自定义的内核中，我们能用LKM加载例外的代码到内核中。我们也可以访问/dev/kmem接口，用来修改内核内存。这是个经典的linux rootkit技术。

[![](https://p4.ssl.qhimg.com/t0190681a042c0cfc46.jpg)](https://p4.ssl.qhimg.com/t0190681a042c0cfc46.jpg)

首先需要的是sys_call_table的地址。幸运的是它被Android内核导出了符号（iOS没这么幸运）。我们在/proc/kallsyms寻找地址：

```
$ adb shell "su -c echo 0 &gt; /proc/sys/kernel/kptr_restrict"
$ adb shell cat /proc/kallsyms | grep sys_call_table
c000f984 T sys_call_table
```

这是我们仅需要写入的内核地址，其他的可以通过便宜计算出来。

我们将使用内核模块隐藏一个文件。让我们在设备创建一个文件，以便我们能在后面隐藏它：

```
$ adb shell "su -c echo ABCD &gt; /data/local/tmp/nowyouseeme"             
$ adb shell cat /data/local/tmp/nowyouseeme
ABCD
```

最后时候写内核模块了。为了文件隐藏，我们需要挂钩用来打开文件的一个系统调用。有很多关于打开open, openat, access, accessat, facessat, stat, fstat,等等。现在我们只需要挂钩openat系统调用，这个系统调用被“/bin/cat”程序访问文件时使用。

你能在内核头文件中（arch/arm/include/asm/unistd.h）找到所有系统调用的函数原型。用下面代码创建一个文件kernel_hook.c:

```
#include &lt;linux/kernel.h&gt;
#include &lt;linux/module.h&gt;
#include &lt;linux/moduleparam.h&gt;
#include &lt;linux/unistd.h&gt;
#include &lt;linux/slab.h&gt;
#include &lt;asm/uaccess.h&gt;
asmlinkage int (*real_openat)(int, const char __user*, int);
void **sys_call_table;
int new_openat(int dirfd, const char __user* pathname, int flags)
`{`
  char *kbuf;
  size_t len;
  kbuf=(char*)kmalloc(256,GFP_KERNEL);
  len = strncpy_from_user(kbuf,pathname,255);
  if (strcmp(kbuf, "/data/local/tmp/nowyouseeme") == 0) `{`
    printk("Hiding file!n");
    return -ENOENT;
  `}`
  kfree(kbuf);
  return real_openat(dirfd, pathname, flags);
`}`
int init_module() `{`
  sys_call_table = (void*)0xc000f984;
  real_openat = (void*)(sys_call_table[__NR_openat]);
return 0;
`}`
```

为了构建内核模块，需要内核资源和工具链，因为之前编译了内核，一切就绪。用以下内容创建makefile文件：

```
KERNEL=[YOUR KERNEL PATH]
TOOLCHAIN=[YOUR TOOLCHAIN PATH]
obj-m := kernel_hook.o
all:
        make ARCH=arm CROSS_COMPILE=$(TOOLCHAIN)/bin/arm-eabi- -C $(KERNEL) M=$(shell pwd) CFLAGS_MODULE=-fno-pic modules
clean:
        make -C $(KERNEL) M=$(shell pwd) clean
```

运行make编译代码，得到文件kernel_hook.ko。复制这个文件到设备并用insmod命令加载它。用lsmod命令验证模块是否加载成功。

```
$ make
(...)
$ adb push kernel_hook.ko /data/local/tmp/
[100%] /data/local/tmp/kernel_hook.ko
$ adb shell su -c insmod /data/local/tmp/kernel_hook.ko
$ adb shell lsmod
kernel_hook 1160 0 [permanent], Live 0xbf000000 (PO)
```

**<br>**

**0x04 修改系统调用表**

现在，我们访问/dev/kmem来用我们注入的函数地址来覆盖sys_call_table中的原始函数的指针（这也能直接在内核模块中做，但是用/dev/kmem更加简单）。我参考了Dong-Hoon You的文章，但是我用文件接口代替nmap()，因为我发现会引起一些内核警告。用下面代码创建文件kmem_util.c：

```
#include &lt;stdio.h&gt; 
#include &lt;stdlib.h&gt;
#include &lt;fcntl.h&gt; 
#include &lt;asm/unistd.h&gt; 
#include &lt;sys/mman.h&gt;
#define MAP_SIZE 4096UL
#define MAP_MASK (MAP_SIZE - 1)
int kmem;
void read_kmem2(unsigned char *buf, off_t off, int sz)
`{`
  off_t offset; ssize_t bread;
  offset = lseek(kmem, off, SEEK_SET);
  bread = read(kmem, buf, sz);
  return; 
`}`
void write_kmem2(unsigned char *buf, off_t off, int sz) `{`
  off_t offset; ssize_t written;
  offset = lseek(kmem, off, SEEK_SET);
  if (written = write(kmem, buf, sz) == -1) `{` perror("Write error");
    exit(0);
  `}` 
  return;
`}`
int main(int argc, char *argv[]) `{`
  off_t sys_call_table;
  unsigned int addr_ptr, sys_call_number;
  if (argc &lt; 3) `{` 
    return 0;
  `}`
  kmem=open("/dev/kmem",O_RDWR);
  if(kmem&lt;0)`{`
    perror("Error opening kmem"); return 0;
  `}`
  sscanf(argv[1], "%x", &amp;sys_call_table); sscanf(argv[2], "%d", &amp;sys_call_number);
  sscanf(argv[3], "%x", &amp;addr_ptr); char buf[256];
  memset (buf, 0, 256); read_kmem2(buf,sys_call_table+(sys_call_number*4),4);
  printf("Original value: %02x%02x%02x%02xn", buf[3], buf[2], buf[1], buf[0]);       
  write_kmem2((void*)&amp;addr_ptr,sys_call_table+(sys_call_number*4),4);
  read_kmem2(buf,sys_call_table+(sys_call_number*4),4);
  printf("New value: %02x%02x%02x%02xn", buf[3], buf[2], buf[1], buf[0]);
  close(kmem);
  return 0; 
`}`
```

构建kmem_util.c并复制到设备中。注意因为是Android Lollipop，所以所有的可执行文件必须是PIE支持编译的。

```
$ /tmp/my-android-toolchain/bin/arm-linux-androideabi-gcc -pie -fpie -o kmem_util kmem_util.c
$ adb push kmem_util /data/local/tmp/
$ adb shell chmod 755 /data/local/tmp/kmem_util
```

在我们开始修改内核内存前，我们需要知道的是系统调用表正确的偏移位置。这个openat调用在unistd.h中定义：

```
$ grep -r "__NR_openat" arch/arm/include/asm/unistd.h
#define __NR_openat            (__NR_SYSCALL_BASE+322)
```

最后一个难题是我们替换openat函数的地址。我们能从/proc/kallsyms得到这个地址：

```
$ adb shell cat /proc/kallsyms | grep new_openat
bf000000 t new_openat    [kernel_hook]
```

现在我们可以覆盖系统调用表的入口了。Kmem_util语法如下：

```
./kmem_util &lt;syscall_table_base_address&gt; &lt;offset&gt; &lt;func_addr&gt;
```

用下面的命令修改系统调用表指向我们的新函数。

```
berndt@osboxes:~/Host/Research/SoftToken/Android/Kernel/msm$ adb shell su -c /data/local/tmp/kmem_util c000f984 322 bf000000
Original value: c017a390
New value: bf000000
```

假设一切正常，/bin/cat应该不能看见这个文件。

```
berndt@osboxes:~/Desktop/Module$ adb shell su -c cat /data/local/tmp/nowyouseeme
tmp-mksh: cat: /data/local/tmp/nowyouseeme: No such file or directory
```

现在通过所有的用户进程已经无法看见隐藏的文件了（但是为了隐藏文件有许多需要做的，包括挂钩stat，access和其他系统调用，还有在文件夹中隐藏）。

文件隐藏的教程只是一个小例子：你可以完成一大堆事，包括绕过启动检测，完整性校验和反调试技巧。

尽管代码覆盖使用符号执行是一个好的方法，但它是个复杂的任务。路径遍历意味着内存消耗，并且一些情况下要计算的表达式太过复杂。目前，判定器非常慢，判定表达式非常慢。

<br>

**0x05 总结**

hook系统调用对于Android逆向分析是一个有用的技术。为了使用它，需要用自定义内核构建自己的逆向工程沙盒。这个文章介绍了如何在Nexus5运行Lollipop，其他AOSP设备也是类似的。

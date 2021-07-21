> 原文链接: https://www.anquanke.com//post/id/217606 


# PSV-2020-0211-Netgear-R8300-UPnP栈溢出漏洞分析


                                阅读量   
                                **167129**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t0175d09c7a562406c4.jpg)](https://p0.ssl.qhimg.com/t0175d09c7a562406c4.jpg)



## 漏洞简介

`PSV-2020-0211`对应`Netgear` `R8300`型号路由器上的一个缓冲区溢出漏洞，`Netgear`官方在2020年7月31日发布了[安全公告](https://kb.netgear.com/000062158/Security-Advisory-for-Pre-Authentication-Command-Injection-on-R8300-PSV-2020-0211)，8月18日`SSD`公开了该漏洞的相关[细节](https://ssd-disclosure.com/ssd-advisory-netgear-nighthawk-r8300-upnpd-preauth-rce/)。该漏洞存在于设备的`UPnP`服务中，由于在处理数据包时缺乏适当的长度校验，通过发送一个特殊的数据包可造成缓冲区溢出。利用该漏洞，未经认证的用户可实现任意代码执行，从而获取设备的控制权。

该漏洞本身比较简单，但漏洞的利用思路值得借鉴，下面通过搭建`R8300`设备的仿真环境来对该漏洞进行分析。



## 漏洞分析

### <a class="reference-link" name="%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>环境搭建

根据官方发布的安全公告，在版本`V1.0.2.134`中修复了该漏洞，于是选取之前的版本`V1.0.2.130`进行分析。由于手边没有真实设备，打算借助`qemu`工具来搭建仿真环境。[文章](https://paper.seebug.org/1311)通过`qemu system mode`的方式来模拟整个设备的系统，我个人更偏向于通过`qemu user mode`的方式来模拟单服务。当然，这两种方式可能都需要对环境进行修复，比如文件/目录缺失、`NVRAM`缺失等。

用`binwalk`对固件进行解压提取后，运行如下命令启动`UPnP`服务。

```
# 添加`--strace`选项, 方便查看错误信息, 便于环境修复
&lt;extracted squashfs-root&gt;$ sudo chroot . ./qemu-arm-static --strace ./usr/sbin/upnpd
```

运行后提示如下错误，根据对应的目录结构，通过运行命令`mkdir -p tmp/var/run`解决。

```
18336 open("/var/run/upnpd.pid",O_RDWR|O_CREAT|O_TRUNC,0666) = -1 errno=2 (No such file or directory)
```

之后再次运行上述命令，提示大量的错误信息，均与`NVRAM`有关，该错误在进行`IoT`设备仿真时会经常遇到。`NVRAM`中保存了设备的一些配置信息，而程序运行时需要读取配置信息，由于缺少对应的外设，因此会报错。一种常见的解决方案是`"劫持"`与`NVRAM`读写相关的函数，通过软件的方式来提供相应的配置。

网上有很多类似的模拟`NVRAM`行为的库，我个人经常使用`Firmadyne`框架提供的`libnvram`库：支持很多常见的`api`，对很多嵌入式设备进行了适配，同时还会解析固件中默认的一些`NVRAM`配置，实现方式比较优雅。采用该库，往往只需要做很少的改动，甚至无需改动，就可以满足需求。

参考`libnvram`的[文档](https://github.com/firmadyne/libnvram)，编译后然后将其置于文件系统中的`firmadyne`路径下，然后通过`LD_PRELOAD`环境变量进行加载，命令如下。

```
&lt;extracted squashfs-root&gt;$ sudo chroot . ./qemu-arm-static --strace -E LD_PRELOAD=./firmadyne/libnvram.so.armel ./usr/sbin/upnpd
```

运行后提示缺少某个键值对，在`libnvram/config.h`中添加对应的配置，编译后重复进行测试，直到程序成功运行起来即可，最终`libnvram/config.h`的变化如下。

```
diff --git a/config.h b/config.h
index 9908414..6598eba 100644
--- a/config.h
+++ b/config.h
@@ -50,8 +50,10 @@
     ENTRY("sku_name", nvram_set, "") \
     ENTRY("wla_wlanstate", nvram_set, "") \
     ENTRY("lan_if", nvram_set, "br0") \
-    ENTRY("lan_ipaddr", nvram_set, "192.168.0.50") \
-    ENTRY("lan_bipaddr", nvram_set, "192.168.0.255") \
+    /* ENTRY("lan_ipaddr", nvram_set, "192.168.0.50") */ \
+    ENTRY("lan_ipaddr", nvram_set, "192.168.200.129") \
+    /* ENTRY("lan_bipaddr", nvram_set, "192.168.0.255") */ \
+    ENTRY("lan_bipaddr", nvram_set, "192.168.200.255") \
     ENTRY("lan_netmask", nvram_set, "255.255.255.0") \
     /* Set default timezone, required by multiple images */ \
     ENTRY("time_zone", nvram_set, "EST5EDT") \
@@ -70,6 +72,10 @@
     /* Used by "DGND3700 Firmware Version 1.0.0.17(NA).zip" (3425) to prevent crashes */ \
     ENTRY("time_zone_x", nvram_set, "0") \
     ENTRY("rip_multicast", nvram_set, "0") \
-    ENTRY("bs_trustedip_enable", nvram_set, "0")
+    ENTRY("bs_trustedip_enable", nvram_set, "0") \
+    /* Used by Netgear router: enable upnpd log */ \
+    ENTRY("upnpd_debug_level", nvram_set, "3") \
+    /* Used by "Netgear R8300" */ \
+    ENTRY("hwrev", nvram_set, "MP1T99")
```

```
# 成功运行
&lt;extracted squashfs-root&gt;$ sudo chroot . ./qemu-arm-static -E LD_PRELOAD=./firmadyne/libnvram.so.armel ./usr/sbin/upnpd
nvram_get_buf: upnpd_debug_level
sem_lock: Triggering NVRAM initialization!
nvram_init: Initializing NVRAM...
# ... &lt;omit&gt;
nvram_match: upnp_turn_on (1) ?= "1"
nvram_match: true
ssdp_http_method_check(203):
ssdp_discovery_msearch(1007):
ST = 20
ssdp_check_USN(212)
service:dial:1
USER-AGENT: Google Chrome/84.0.4147.125 Windows
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

在`upnp_main()`中，在`(1)`处`recvfrom()`用来读取来自`socket`的数据，并将其保存在`v55`指向的内存空间中。在`(2)`调用`ssdp_http_method_check()`，传入该函数的第一个参数为`v55`，即指向接收的`socket`数据。

```
int upnp_main()
`{`
  char v55[4]; // [sp+44h] [bp-20ECh]

  // ...
  while ( 1 )
  `{`
    // ...
    if ( (v20 &gt;&gt; (dword_C4580 &amp; 0x1F)) &amp; 1 )
    `{`
      v55[0] = 0;
      v28 = recvfrom(dword_C4580, v55, 0x1FFFu, 0, (struct sockaddr *)&amp;v63, (socklen_t *)&amp;v71);     // (1)
      // ...
      if ( v29 )
      `{`
        if ( v28 )
        `{`
          // ...
          if ( acosNvramConfig_match("upnp_turn_on", "1") )
            ssdp_http_method_check( v55, (int)&amp;v59, (unsigned __int16)(HIWORD(v63) &lt;&lt; 8) | (unsigned __int16)(HIWORD(v63) &gt;&gt; 8));   // (2)
           // ...
```

在`ssdp_http_method_check()`中，在`(3)`处调用`strcpy()`进行数据拷贝，其中`v40`指向栈上的局部缓冲区，`v3`指向接收的`socket`数据。由于缺乏长度校验，当构造一个超长的数据包时，拷贝时会出现缓冲区溢出。

```
signed int ssdp_http_method_check(const char *a1, int a2, int a3)
`{`
  int v40; // [sp+24h] [bp-634h]

  v3 = a1;
  // ... 
  wrap_vprintf(3, "%s(%d):\n", "ssdp_http_method_check", 203);
  if ( dword_93AE0 == 1 )
    return 0;
  strcpy((char *)&amp;v40, v3);     // (3) stack overflow
  // ...
```



## 漏洞利用

`upnpd`程序启用的缓解措施如下，可以看到仅启用了`NX`机制。另外，由于程序的加载基址为`0x8000`，故`.text`段地址的最高字节均为`\x00`，而在调用`strcpy()`时存在`NULL`字符截断的问题，因此在进行漏洞利用时需要想办法绕过`NULL`字符限制的问题。

```
$ checksec --file ./upnpd
    Arch:     arm-32-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8000)
```

`SSD`公开的[漏洞细节](https://ssd-disclosure.com/ssd-advisory-netgear-nighthawk-r8300-upnpd-preauth-rce/)中给出了一个方案：通过`stack reuse`的方式来绕过该限制。具体思路为，先通过`socket`发送第一次数据，往栈上填充相应的`rop payload`，同时保证不会造成程序崩溃；再通过`socket`发送第二次数据用于覆盖栈上的返回地址，填充的返回地址用来实现`stack pivot`，即劫持栈指针使其指向第一次发送的`payload`处，然后再复用之前的`payload`以完成漏洞利用。`SSD`公开的漏洞细节中的示意图如下。

[![](https://p0.ssl.qhimg.com/t0137c8d44b6804a24e.png)](https://p0.ssl.qhimg.com/t0137c8d44b6804a24e.png)

实际上，由于`recvfrom()`函数与漏洞点`strcpy()`之间的路径比较短，栈上的数据不会发生太大变化，利用`stack reuse`的思路，只需发送一次数据即可完成利用，示意图如下。在调用`ssdp_http_method_check()`前，接收的`socket`数据包保存在`upnp_main()`函数内的局部缓冲区上，而在`ssdp_http_method_check()`内，当调用完`strcpy()`后，会复制一部分数据到该函数内的局部缓冲区上。通过覆盖栈上的返回地址，可劫持栈指针，使其指向`upnp_main()`函数内的局部缓冲区，复用填充的`rop gadgets`，从而完成漏洞利用。

[![](https://p3.ssl.qhimg.com/t01a27e24cde74baa2a.png)](https://p3.ssl.qhimg.com/t01a27e24cde74baa2a.png)

[![](https://p2.ssl.qhimg.com/t01698b827452fb826c.png)](https://p2.ssl.qhimg.com/t01698b827452fb826c.png)

另外在调用`strcpy()`后，在`(4)`处还调用了函数`sub_B60C()`。通过对应的汇编代码可知，在覆盖栈上的返回地址之前，也会覆盖`R7`指向的栈空间内容，之后`R7`作为参数传递给`sub_B60C()`。而在`sub_B60C()`中，会读取`R0`指向的栈空间中的内容，然后再将其作为参数传递给`strstr()`，这意味`[R0]`中的值必须为一个有效的地址。因此在覆盖返回地址的同时，还需要用一个有效的地址来填充对应的栈偏移处，保证函数在返回前不会出现崩溃。由于`libc`库对应的加载基址比较大，即其最高字节不为`\x00`，因此任意选取该范围内的一个不包含`\x00`的有效地址即可。

[![](https://p3.ssl.qhimg.com/t0147afd4d6af01237c.png)](https://p3.ssl.qhimg.com/t0147afd4d6af01237c.png)

在解决了`NULL`字符截断的问题之后，剩下的部分就是寻找`rop gadgets`来完成漏洞利用了，相对比较简单。同样，`SSD`公开的[漏洞细节](https://ssd-disclosure.com/ssd-advisory-netgear-nighthawk-r8300-upnpd-preauth-rce/)中也包含了完整的漏洞利用代码，其思路是通过调用`strcpy gadget`拼接出待执行的命令，并将其写到某个`bss`地址处，然后再调用`system gadget`执行对应的命令。

在给出的漏洞利用代码中，`strcpy gadget`执行的过程相对比较繁琐，经过分析后，在`upnpd`程序中找到了另一个更优雅的`strcpy gadget`，如下。借助该`gadget`，可以直接在数据包中发送待执行的命令，而无需进行命令拼接。

```
.text:0000B764 MOV             R0, R4  ; dest
.text:0000B768 MOV             R1, SP  ; src
.text:0000B76C BL              strcpy
.text:0000B770 ADD             SP, SP, #0x400
.text:0000B774 LDMFD           SP!, `{`R4-R6,PC`}`
```



## 补丁分析

`Netgear` 官方在`R8300-V1.0.2.134_1.0.99`版本中修复该漏洞。函数`ssdp_http_method_check()`的相关伪代码如下，可以看到，在补丁中调用的是`strncpy()`而非原来的`strcpy()`，同时还对局部缓冲区`&amp;v40`进行了初始化。

```
signed int ssdp_http_method_check(const char *a1, int a2, int a3)
`{`

  int v40; // [sp+24h] [bp-Ch]

  v3 = a1;
  // ...
  memset(&amp;v40, 0, 0x5DCu);
  v52 = 32;
  sub_B814(3, "%s(%d):\n", "ssdp_http_method_check", 203);
  if ( dword_93AE0 == 1 )
    return 0;
  v51 = &amp;v40;
  strncpy((char *)&amp;v40, v3, 0x5DBu);        // patch
  // ...
```



## 小结

本文通过搭建`Netgear` `R8300`型号设备的仿真环境，对其`UPnP`服务中存在的缓冲区溢出漏洞进行了分析。漏洞本身比较简单，但漏洞利用却存在`NULL`字符截断的问题，`SSD`公开的漏洞细节中通过`stack reuse`的方式实现了漏洞利用，思路值得借鉴和学习。



## 相关链接
- [Security Advisory for Pre-Authentication Command Injection on R8300, PSV-2020-0211](https://kb.netgear.com/000062158/Security-Advisory-for-Pre-Authentication-Command-Injection-on-R8300-PSV-2020-0211)
- [SSD Advisory – Netgear Nighthawk R8300 upnpd PreAuth RCE](https://ssd-disclosure.com/ssd-advisory-netgear-nighthawk-r8300-upnpd-preauth-rce/)
- [Netgear Nighthawk R8300 upnpd PreAuth RCE 分析与复现](https://paper.seebug.org/1311)
- [Firmadyne libnvram](https://github.com/firmadyne/libnvram)
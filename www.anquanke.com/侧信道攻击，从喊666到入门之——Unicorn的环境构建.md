> 原文链接: https://www.anquanke.com//post/id/187028 


# 侧信道攻击，从喊666到入门之——Unicorn的环境构建


                                阅读量   
                                **538473**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t014621ad7bae863200.jpg)](https://p3.ssl.qhimg.com/t014621ad7bae863200.jpg)



作者：backahasten

Unicorn可以模拟多种指令集的代码，在很多安全研究领域有很强大的作用，但是由于需要从头自己布置栈空间，代码段等虚拟执行环境，阻碍了他的使用，本文将会分析一个实例，并介绍Unicorn虚拟运行环境的构建。

本文的例子是一个白盒实现的DES算法，在riscrue的文章**Unboxing the white box**中介绍了白盒攻击的类侧信道和类错误注入方法，并用这个程序作为例子。在riscure的代码中，由于python2和3对于字符串和bytes关系的变化很大，代码基本不可用。让我们来从头分析这个程序并编写设计Unicorn的代码。

Unicorn虽然可以脱离平台执行，但是在程序虚拟运行环境的设计阶段，逆向甚至动态调试都是不可避免的，Unicorn的运行环境构建分为
- 代码与程序段加载
- 栈配置
- 特殊寄存器配置
- 外部调用patch
- Unicorn中调试


## 代码与程序段加载

在这个过程中，我们需要把代码像正常程序加载一样放进我们的虚拟内存中，一般的步骤是，首先实例化一个CPU对象出来：

```
mu =Uc(UC_ARCH_X86, UC_MODE_32)
```

上面这句话就是实例化了一个x86架构32位的CPU出来，之后就可以开始代码的加载和其他初始化（其他架构的配置请参考Unicorn官方文档）。代码段的加载以及接下来内存栈的初始化都可以使用如下的模板：

```
mu.mem_map(address, size)            #分配一个内存空间，起始地址位address，大小为size
mu.mem_write(address, data)          #在内存地址为address的位置存入data
```

首先进行代码段的载入，我们需要扫描ELF文件，根据程序头找到其中的代码段并进行加载。

```
elf =ELFFile(open("./wbDES",'rb'))
for seg in elf.iter_segments():
    if seg.header.p_type =="PT_LOAD":
        data =seg.data()
        mapsz =PAGE_SIZE*int((len(data) +PAGE_SIZE)/PAGE_SIZE)
        addr =seg.header.p_vaddr -(seg.header.p_vaddr %PAGE_SIZE)
        mu.mem_map(addr, mapsz)
        mu.mem_write(seg.header.p_vaddr, data)
```

在进行内存分配的时候，要注意对齐，按内存页的最小值倍数进行分配。



## 栈配置

接下来需要对栈开始配置，在开始配置栈之前，我们需要动态调试确定一下指定函数调用之前，栈里有什么东西。使用gdb对`main`函数进行调试，在main函数的开始处 `0x80484c4` 设置断点并输入参数，启动GDB：

[![](https://p5.ssl.qhimg.com/t010482cbb9be8b9371.png)](https://p5.ssl.qhimg.com/t010482cbb9be8b9371.png)

我们可以看出，main函数的栈结构是这样的：

|地址|数值|内容|备注
|------
|0xffffce8c——(esp)|0xf7c29637|RET|
|0xffffce90——(esp+4)|9|argc|
|0xffffce94——(esp+8)|0xffffcf24|argv|传入指针

我们继续查看0xffffcf24的内容

```
pwndbg&gt; x/16sx 0xffffcf24
0xffffcf24:    0xffffd125    0xffffd137    0xffffd13a    0xffffd13d
0xffffcf34:    0xffffd140    0xffffd143    0xffffd146    0xffffd149
0xffffcf44:    0xffffd14c    0x00000000    0xffffd14f    0xffffd15a
0xffffcf54:    0xffffd16c    0xffffd19a    0xffffd1b0    0xffffd1bf
```

继续查看0xffffd125的内容，发现

```
pwndbg&gt; x/16wx 0xffffd125
0xffffd125:    0x6d6f682f    0x696d2f65    0x2f62772f    0x45446277
0xffffd135:    0x32310053    0x00343300    0x37003635    0x62610038
0xffffd145:    0x00646300    0x31006665    0x44580066    0x54565f47
0xffffd155:    0x373d524e    0x47445800    0x5345535f    0x4e4f4953
```

如果不够直观，可以选择打印字符串。

```
pwndbg&gt; x/10s 0xffffd125
0xffffd125:    "/home/mi/wb/wbDES"
0xffffd137:    "12"
0xffffd13a:    "34"
0xffffd13d:    "56"
0xffffd140:    "78"
0xffffd143:    "ab"
0xffffd146:    "cd"
0xffffd149:    "ef"
0xffffd14c:    "1f"
0xffffd14f:    "XDG_VTNR=7"
```

到目前为止，我们可以确定栈空间是什么样子的

首先，main函数有两个参数，一个是`argc`为`9`，另一个是一个指针，指向一个指针数组，指针数组的第一个指针指向的是字符串`"/home/mi/wb/wbDES"`，第二个指向`”12“`，第三个指向`”34“`以此类推。

接下来，根据分析所得的信息，开始进行栈空间参数的构建。

首先，先申请一段栈空间

```
STACK = 0xbfff0000
STACK_SIZE = 0x10000
mu.mem_map(STACK, STACK_SIZE)
```

栈的开始地址选择除了0x0附近之外的什么地方都可以，满足对齐即可，大小尽量大一些。

```
SP = STACK +STACK_SIZE - 0x800
```

之后设置SP指针的位置，由于栈是向低地址增长的，所以我们有0x800大小的空间可以部署那些字符串参数。

```
mu.reg_write(UC_X86_REG_ESP, SP)
mu.reg_write(UC_X86_REG_EBP, SP)
```

设置ESP指针，有上图可知，EBP指针为0，表示函数中没有用到EBP寻址，为了安全起见设置程和ESP一样。

接下来开始布置值字符串，代码如下：

```
start =0x100
a = "./wbDESx00"
mu.mem_write(SP+start, a.encode())
argv =[SP+start]
start +=8
for i in range(8):
    argv.append(SP+start)
    mu.mem_write(SP+start, b'ab')
    start +=2
    mu.mem_write(SP+start, bytes('x00','utf-8'))
    start +=1
```

之后开始布置指针数组：

```
i =0
for arg in argv:
    mu.mem_write(SP+0x200+i*4, p32(arg))
    i +=1       
# NULL
mu.mem_write(SP+0x200+i*4, p32(0))
```

最后开始布置函数参数那个区域的栈：

```
RET = STACK
mu.mem_write(SP+0x0, p32(RET)) # Return address @ sp
mu.mem_write(SP+0x04, p32(len(argv))) # argc
mu.mem_write(SP+0x08, p32(SP +0x200)) # argv
```

把返回地址写为栈顶的意义在于，在我们启动unicorn的时候，需要传入程序开始执行的位置和终止的位置，这样写实际上就是让函数返回到栈里，之后把栈顶的指针设置成结束位置，就不用去找函数终止的位置了。



## Unicorn中调试

配置好了栈空间之后，我们还要看一下自己的配置对不对，和调试器中的值进行对比。可以使用：

```
print(mu.mem_read(SP+0x100,64).hex())
```

打印出SP+0x100位置64个字节的值，与GDB进行对比。

现在我们来分别对比一下三个位置布置的对不对。

```
print(mu.mem_read(SP+0x100,64).hex())#字符串
print(mu.mem_read(SP+0x200,64).hex())#数组指针
print(mu.mem_read(SP,64).hex()) #main参数
```

对应得到：

```
2e2f7762444553006162006162006162006162006162006162006162006162000000000000000000000000000000000000000000000000000000000000000000 #字符串
00f9ffbf08f9ffbf0bf9ffbf0ef9ffbf11f9ffbf14f9ffbf17f9ffbf1af9ffbf1df9ffbf00000000000000000000000000000000000000000000000000000000 #数组指针
0000ffbf0900000000faffbf00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000 #main参数
```

```
pwndbg&gt; x/80xb 0xffffce8c
0xffffce8c:    0x37    0x96    0xc2    0xf7    0x09    0x00    0x00    0x00
0xffffce94:    0x24    0xcf    0xff    0xff    0x4c    0xcf    0xff    0xff
0xffffce9c:    0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xffffcea4:    0x00    0x00    0x00    0x00    0x00    0x30    0xdc    0xf7
0xffffceac:    0x04    0xdc    0xff    0xf7    0x00    0xd0    0xff    0xf7
0xffffceb4:    0x00    0x00    0x00    0x00    0x00    0x30    0xdc    0xf7
0xffffcebc:    0x00    0x30    0xdc    0xf7    0x00    0x00    0x00    0x00
0xffffcec4:    0x67    0x1b    0x4d    0xc1    0x77    0xd5    0xfb    0xbb
0xffffcecc:    0x00    0x00    0x00    0x00    0x00    0x00    0x00    0x00
0xffffced4:    0x00    0x00    0x00    0x00    0x09    0x00    0x00    0x00
#0000ffbf0900000000faffbf00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
```

```
pwndbg&gt; x/80xb 0xffffcf24
0xffffcf24:    0x25    0xd1    0xff    0xff    0x37    0xd1    0xff    0xff
0xffffcf2c:    0x3a    0xd1    0xff    0xff    0x3d    0xd1    0xff    0xff
0xffffcf34:    0x40    0xd1    0xff    0xff    0x43    0xd1    0xff    0xff
0xffffcf3c:    0x46    0xd1    0xff    0xff    0x49    0xd1    0xff    0xff
0xffffcf44:    0x4c    0xd1    0xff    0xff    0x00    0x00    0x00    0x00
0xffffcf4c:    0x4f    0xd1    0xff    0xff    0x5a    0xd1    0xff    0xff
0xffffcf54:    0x6c    0xd1    0xff    0xff    0x9a    0xd1    0xff    0xff
0xffffcf5c:    0xb0    0xd1    0xff    0xff    0xbf    0xd1    0xff    0xff
0xffffcf64:    0xfd    0xd1    0xff    0xff    0x2c    0xd2    0xff    0xff
0xffffcf6c:    0x4e    0xd2    0xff    0xff    0x5f    0xd2    0xff    0xff
#00f9ffbf08f9ffbf0bf9ffbf0ef9ffbf11f9ffbf14f9ffbf17f9ffbf1af9ffbf1df9ffbf00000000000000000000000000000000000000000000000000000000
```

```
pwndbg&gt; x/80xb 0xffffd125
0xffffd125:    0x2f    0x68    0x6f    0x6d    0x65    0x2f    0x6d    0x69
0xffffd12d:    0x2f    0x77    0x62    0x2f    0x77    0x62    0x44    0x45
0xffffd135:    0x53    0x00    0x31    0x32    0x00    0x33    0x34    0x00
0xffffd13d:    0x35    0x36    0x00    0x37    0x38    0x00    0x61    0x62
0xffffd145:    0x00    0x63    0x64    0x00    0x65    0x66    0x00    0x31
0xffffd14d:    0x66    0x00    0x58    0x44    0x47    0x5f    0x56    0x54
0xffffd155:    0x4e    0x52    0x3d    0x37    0x00    0x58    0x44    0x47
0xffffd15d:    0x5f    0x53    0x45    0x53    0x53    0x49    0x4f    0x4e
0xffffd165:    0x5f    0x49    0x44    0x3d    0x63    0x32    0x00    0x58
0xffffd16d:    0x44    0x47    0x5f    0x47    0x52    0x45    0x45    0x54
#2e2f7762444553006162006162006162006162006162006162006162006162000000000000000000000000000000000000000000000000000000000000000000
```

对比之后发现正确，如果不正确，需要更改代码进行微调。

接下来，我们需要设置一个调试hook，该hook函数的callback会在每句指令执行之前执行，便于我们发现问题。

```
def hook_code(mu, address, size, user_data):  
    print('&gt;&gt;&gt; Tracing instruction at 0x%x, instruction size = 0x%x' %(address, size))
```

之后注册hook：

```
mu.hook_add(UC_HOOK_CODE, hook_code)
```

开始执行：

```
mu.emu_start(entry, RET)
```

很不幸，程序挂了，Unicorn给出里一个读取未分配空间的异常：

[![](https://p1.ssl.qhimg.com/t0107c73f04c9ec7d3f.png)](https://p1.ssl.qhimg.com/t0107c73f04c9ec7d3f.png)

因为我们有调试，可以发现这个位置是在执行到0x80484e1的时候发生的，我们看下这个地址是什么指令。

[![](https://p3.ssl.qhimg.com/t01311d6d70074a781f.png)](https://p3.ssl.qhimg.com/t01311d6d70074a781f.png)

发现是有关gs:0x14的操作，这个指令应该是栈cookie的操作，我们没分配的寄存器unicorn默认为0，所以我们需要在0x0空间给gs分配一个空间，这句话就可以跑过去了。

```
mu.mem_map(0, 0x1000)
```

之后再运行：

[![](https://p5.ssl.qhimg.com/t01ff253d812700b77e.png)](https://p5.ssl.qhimg.com/t01ff253d812700b77e.png)

发现程序好像跑飞了，往上翻，找到：

[![](https://p1.ssl.qhimg.com/t0111c28c21f8cfe4a7.png)](https://p1.ssl.qhimg.com/t0111c28c21f8cfe4a7.png)

下断点调试，发现是跑到外部函数调用上去了：

[![](https://p3.ssl.qhimg.com/t01d565f377506a566f.png)](https://p3.ssl.qhimg.com/t01d565f377506a566f.png)

分析之后发现，在main函数中有两处外部函数调用，我们直接patch掉他们的plt，让他们直接返回。

```
mu.mem_write(0x80483BC, bytes('xc3','utf-8'))
mu.mem_write(0x80483EC, bytes('xc3','utf-8'))
```

之后再运行就没有问题了。

我还针对栈的读取设置了hook，每次内存的写地址都会被记录，得到如下的图：

[![](https://p5.ssl.qhimg.com/t0136f22cda621ce983.png)](https://p5.ssl.qhimg.com/t0136f22cda621ce983.png)

可以清楚的发现DES算法的轮结构，unicorn的调教到此完成，为下一步的研究做准备。



## 参考

[1][https://www.riscure.com/publication/unboxing-white-box/](https://www.riscure.com/publication/unboxing-white-box/)

[2][https://www.unicorn-engine.org/](https://www.unicorn-engine.org/)

[3][http://www.whiteboxcrypto.com/challenges.php](http://www.whiteboxcrypto.com/challenges.php)

PS：小米安全中心：[https://sec.xiaomi.com/](https://sec.xiaomi.com/)

查看更多文章可关注小米安全中心公众号:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017118ebc50cf6784b.png)

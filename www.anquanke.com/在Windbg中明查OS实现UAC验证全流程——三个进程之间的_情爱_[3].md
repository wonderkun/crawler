> 原文链接: https://www.anquanke.com//post/id/231446 


# 在Windbg中明查OS实现UAC验证全流程——三个进程之间的"情爱"[3]


                                阅读量   
                                **161120**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0133435a43ae81bd1e.png)](https://p2.ssl.qhimg.com/t0133435a43ae81bd1e.png)



## 0、引言

在前一篇《在Windbg中明查OS实现UAC验证全流程——三个进程之间的”情爱”[2]》简短的分析了下AIS的方方面面的细节，这一篇抛开这些，来深入分析下检测的逻辑以及拉起consent进程的逻辑。

整个系列涉及到的知识：

0、Windbg调试及相关技巧；<br>
1、OS中的白名单及白名单列表的窥探；<br>
2、OS中的受信目录及受信目录列表的查询；<br>
3、窗口绘制[对,你没看错,提权窗口就涉及到绘制]；<br>
4、程序内嵌的程序的Manifest；<br>
5、服务程序的调试；<br>
6、归一化路径及漏洞；



## 1、白名单列表

第一处:

具体的代码如下，g_lpAutoApproveEXEList这个全局变量以及AipCompareEXE这个函数值得我们重点关注下，在具体解析前，先来看下bsearch的参数。

[![](https://p2.ssl.qhimg.com/t01e459ffabc27a86a2.png)](https://p2.ssl.qhimg.com/t01e459ffabc27a86a2.png)

下面是 bsearch() 函数的声明。

```
void *bsearch(const void *key, const void *base, size_t nitems, size_t size, int (*compar)(const void *, const void *))

key      ---- 指向要查找的元素的指针，类型转换为 void*。
base     ---- 指向进行查找的数组的第一个对象的指针，类型转换为 void*。
nitems   ---- base 所指向的数组中元素的个数。
size     ---- 数组中每个元素的大小，以字节为单位。
compar   ---- 用来比较两个元素的函数。
```

根据上一篇的分析可知：

```
key      :"taskmgr.exe"
base     :g_lpAutoApproveEXEList,如下所示：
```

[![](https://p5.ssl.qhimg.com/t01f026562c83d173ae.png)](https://p5.ssl.qhimg.com/t01f026562c83d173ae.png)

```
nitems   ---- 0x0A。
size     ---- 8。
compar   ---- AipCompareEXE。
```

[![](https://p2.ssl.qhimg.com/t016bd20e8b74acd43b.png)](https://p2.ssl.qhimg.com/t016bd20e8b74acd43b.png)

第二处：

代码如下：

[![](https://p3.ssl.qhimg.com/t015b08672426e5c1ee.png)](https://p3.ssl.qhimg.com/t015b08672426e5c1ee.png)

[![](https://p1.ssl.qhimg.com/t011a11676dc1ca67d2.png)](https://p1.ssl.qhimg.com/t011a11676dc1ca67d2.png)



## 2、可信路径

关键代码如下：

[![](https://p4.ssl.qhimg.com/t015fa1ea4c1b229e3e.png)](https://p4.ssl.qhimg.com/t015fa1ea4c1b229e3e.png)

```
0:005&gt; du g_wszWow64Dir
00007ffd`b90481c0  "C:\WINDOWS\SysWOW64"
```

AipConvertIndividualWow64Path函数的实现很简单，伪代码如下：

[![](https://p0.ssl.qhimg.com/t01e0e49ad4765a19e0.png)](https://p0.ssl.qhimg.com/t01e0e49ad4765a19e0.png)

其中g_wszWow64Dir数据如下：

```
0:005&gt; du g_wszWow64Dir
00007ffd`b90481c0  "C:\WINDOWS\SysWOW64"
```

紧接着下一行有这么一行代码，如下：

该函数的实现如下：

[![](https://p5.ssl.qhimg.com/t018f4d0bae17d2812f.png)](https://p5.ssl.qhimg.com/t018f4d0bae17d2812f.png)

[![](https://p0.ssl.qhimg.com/t01db995e6d11d5f581.png)](https://p0.ssl.qhimg.com/t01db995e6d11d5f581.png)

回到上边 ，看一下g_Dirs这个全局变量，如下：

```
0:005&gt; dS g_Dirs
0000026a`06c24320  "\??\C:\Program Files\"
```

再来看下AipCheckSecureWindowsDirectory()的内部实现，很精彩。

[![](https://p1.ssl.qhimg.com/t016e670bb0dea8f712.png)](https://p1.ssl.qhimg.com/t016e670bb0dea8f712.png)

先来看下几个关键变量，如下：

```
0:005&gt; dS g_IncludedWinDir
0000026a`06c24460  "\??\C:\Windows\System32"
0:005&gt; dS g_IncludedXmtExe
0000026a`06c30670  "\??\C:\Windows\System32\Sysprep\sysprep.exe"
0:005&gt; dS g_IncludedSysDir
0000026a`06c3d5f0  "\??\C:\Windows\System32\"
0:005&gt; dS g_ExcludedWinDir
0000026a`06c24aa0  "\??\C:\Windows\Debug\"

```

AipMatchesOriginalFileName()函数内部仅仅是简单获取比较下原始文件名，原理很简单，留给大家分析。

AipCheckSecurePFDirectory()的内部实现如下：

```
0:005&gt; dd g_bPFX86Supported
00007ffd`b9047110  00000001 00010101 00000000 00000000
```

[![](https://p4.ssl.qhimg.com/t017671a32a94a02691.png)](https://p4.ssl.qhimg.com/t017671a32a94a02691.png)

g_IncludedPF的数据如下：

```
0:005&gt; dS g_IncludedPF
0000026a`06c3e830  "\??\C:\Program Files\Windows Defender"
```



## 3、对AiLaunchConsentUI()的调用

[![](https://p2.ssl.qhimg.com/t0114c742da591d6bdd.png)](https://p2.ssl.qhimg.com/t0114c742da591d6bdd.png)

该函数的内部实现也很复杂，截取的关键代码如下：

[![](https://p3.ssl.qhimg.com/t01eff1c59fa0b2a488.png)](https://p3.ssl.qhimg.com/t01eff1c59fa0b2a488.png)

我们现在追踪一下AiLaunchConsentUI()的第一个参数，如下;

```
0:008&gt; r
rax=0000000000000001 rbx=0000000000000844 rcx=00000000000008c0
rdx=0000026a06c81eb0 rsi=0000000000000001 rdi=0000000000000000
rip=00007ffdb90224d0 rsp=000000e1059feeb8 rbp=000000e1059fefc0
r8=0000026a0752e4f8  r9=0000000000481b04 r10=0000000000000000
r11=0000000000000246 r12=0000000000000a20 r13=00000000000008c0
r14=0000026a06c81eb0 r15=0000000000000006
iopl=0         nv up ei pl zr na po nc
cs=0033  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000246
appinfo!AiLaunchConsentUI:
00007ffd`b90224d0 48895c2408      mov     qword ptr [rsp+8],rbx ss:000000e1`059feec0=0000000000000004

v6对应的是RDX的值,具体数据如下
0:008&gt; db 0000026a06c81eb0  l12c
0000026a`06c81eb0  2c 01 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ,...............
0000026a`06c81ec0  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
0000026a`06c81ed0  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................
0000026a`06c81ee0  00 00 00 00 74 af 00 00-00 00 00 00 00 00 00 00  ....t...........
0000026a`06c81ef0  70 08 00 00 00 00 00 00-70 00 00 00 00 00 00 00  p.......p.......
0000026a`06c81f00  ac 00 00 00 00 00 00 00-e8 00 00 00 00 00 00 00  ................
0000026a`06c81f10  2a 01 00 00 00 00 00 00-b0 0c 00 00 00 00 00 00  *...............
0000026a`06c81f20  44 00 3a 00 5c 00 4d 00-69 00 63 00 72 00 6f 00  D.:.\.M.i.c.r.o.
0000026a`06c81f30  73 00 6f 00 66 00 74 00-20 00 56 00 53 00 20 00  s.o.f.t. .V.S. .
0000026a`06c81f40  43 00 6f 00 64 00 65 00-5c 00 43 00 6f 00 64 00  C.o.d.e.\.C.o.d.
0000026a`06c81f50  65 00 2e 00 65 00 78 00-65 00 00 00 44 00 3a 00  e...e.x.e...D.:.
0000026a`06c81f60  5c 00 4d 00 69 00 63 00-72 00 6f 00 73 00 6f 00  \.M.i.c.r.o.s.o.
0000026a`06c81f70  66 00 74 00 20 00 56 00-53 00 20 00 43 00 6f 00  f.t. .V.S. .C.o.
0000026a`06c81f80  64 00 65 00 5c 00 43 00-6f 00 64 00 65 00 2e 00  d.e.\.C.o.d.e...
0000026a`06c81f90  65 00 78 00 65 00 00 00-22 00 44 00 3a 00 5c 00  e.x.e...".D.:.\.
0000026a`06c81fa0  4d 00 69 00 63 00 72 00-6f 00 73 00 6f 00 66 00  M.i.c.r.o.s.o.f.
0000026a`06c81fb0  74 00 20 00 56 00 53 00-20 00 43 00 6f 00 64 00  t. .V.S. .C.o.d.
0000026a`06c81fc0  65 00 5c 00 43 00 6f 00-64 00 65 00 2e 00 65 00  e.\.C.o.d.e...e.
0000026a`06c81fd0  78 00 65 00 22 00 20 00-00 00 00 00              x.e.". .....

0:008&gt; du 0000026a`06c81f20
0000026a`06c81f20  "D:\Microsoft VS Code\Code.exe"
```

原来如此，传进去的是待创建的进程的全路径。而consent进程画出来的那个窗口的全路径信息也是来自于此，如下：【原谅我没有双屏，只能手机拍照了。】

[![](https://p0.ssl.qhimg.com/t01f7dff2dc098aaa59.png)](https://p0.ssl.qhimg.com/t01f7dff2dc098aaa59.png)

Procmon抓取的数据如下：

[![](https://p3.ssl.qhimg.com/t01f9565796a805ffa9.png)](https://p3.ssl.qhimg.com/t01f9565796a805ffa9.png)



## 4、总结

简单的带大家分析了下关键API内部的实现原理吗，很多细节还需要大家亲自实验，反复求证才能掌握。后期将会有更为深入的讲解。

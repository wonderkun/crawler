> 原文链接: https://www.anquanke.com//post/id/85156 


# 【技术分享】一款Linux下的键盘记录软件分析


                                阅读量   
                                **140305**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：morphick.com
                                <br>原文地址：[http://www.morphick.com/resources/lab-blog/mikey-linux-keylogger](http://www.morphick.com/resources/lab-blog/mikey-linux-keylogger)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p4.ssl.qhimg.com/t01db6b448a615b7073.png)](https://p4.ssl.qhimg.com/t01db6b448a615b7073.png)**

****

**翻译：**[**shan66******](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：160RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**前言**

当前，Linux恶意软件正在逐渐流行起来了。近几年，已经有好几起重大安全事件中所涉及的Linux后门都是从Windows系统移植过来的。在研究Odinaff报告中的Windows KLRD键盘记录软件的过程中，我们发现了几个新的键盘记录软件。在本文中，我们讨论的焦点是MiKey，这是一个鲜为人知的、之前未曾检测到的键盘记录软件。

在撰写本文时，Virustotal上的引擎仍然检测不出该恶意软件。

[![](https://p3.ssl.qhimg.com/t01fb64c2bec46c6fec.jpg)](https://p3.ssl.qhimg.com/t01fb64c2bec46c6fec.jpg)

<br>

**软件分析 **

这款恶意软件是一个64位的Linux可执行文件： 

```
9c07ed03f5bf56495e1d365552f5c9e74bb586ec45dffced2a8368490da4c829: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=550c58e6a9bc88b8724fd8ab7fd79a6c58c12d28, not stripped
```

同时，它还依赖于以下程序库： 



```
linux-vdso.so.1 (0x00007ffd25123000)
libX11.so.6 =&gt; /usr/lib/x86_64-linux-gnu/libX11.so.6 (0x00007f7f56420000)
libdl.so.2 =&gt; /lib/x86_64-linux-gnu/libdl.so.2 (0x00007f7f5621c000)
libc.so.6 =&gt; /lib/x86_64-linux-gnu/libc.so.6 (0x00007f7f55e7e000)
libxcb.so.1 =&gt; /usr/lib/x86_64-linux-gnu/libxcb.so.1 (0x00007f7f55c56000)
/lib64/ld-linux-x86-64.so.2 (0x00005597839c6000)
libXau.so.6 =&gt; /usr/lib/x86_64-linux-gnu/libXau.so.6 (0x00007f7f55a52000)
libXdmcp.so.6 =&gt; /usr/lib/x86_64-linux-gnu/libXdmcp.so.6 (0x00007f7f5584a000)
```

在分析这个二进制代码的符号表之后，我们找到了一些非常让人感兴趣的函数名。（为了方便阅读，这里就不给出完整的输出了）： 



```
63: 00000000004014b2    79 FUNC    GLOBAL DEFAULT   14 createProccess
64: 0000000000400ed6   128 FUNC    GLOBAL DEFAULT   14 initPlugins
67: 0000000000400f56   105 FUNC    GLOBAL DEFAULT   14 moduleFeed
68: 000000000040102d  1157 FUNC    GLOBAL DEFAULT   14 keylogger
75: 0000000000400dc6   159 FUNC    GLOBAL DEFAULT   14 handleArgs
83: 0000000000400e65   113 FUNC    GLOBAL DEFAULT   14 moduleHandleArgs
85: 00000000004015fc   209 FUNC    GLOBAL DEFAULT   14 addData
87: 0000000000400cd0    42 FUNC    GLOBAL DEFAULT   14 _start
88: 0000000000400fbf   110 FUNC    GLOBAL DEFAULT   14 addParentheses
92: 0000000000401501   126 FUNC    GLOBAL DEFAULT   14 main
103: 0000000000400b00     0 FUNC    GLOBAL DEFAULT   11 _init
```

编译器留下的注释表明，它是在Ubuntu 16.04.2系统上编译的： 

```
9c07ed03f5bf56495e1d365552f5c9e74bb586ec45dffced2a8368490da4c829:     file format elf64-x86-64
```

下面是.comment节中的内容： 



```
0000 4743433a 20285562 756e7475 20352e34  GCC: (Ubuntu 5.4
 0010 2e302d36 7562756e 7475317e 31362e30  .0-6ubuntu1~16.0
 0020 342e3229 20352e34 2e302032 30313630  4.2) 5.4.0 20160
 0030 36303900                             609.
```

该二进制文件中的构建路径给出了进一步的证据︰ 

```
/home/ubuntu/MiKey-64-ubuntu
```

strace工具可以迅速确定函数的高级工作流程并识别潜在的重点对象。其中，一个失败的文件打开，即“mikey-text.so”引起了我们的注意，所以我们不妨从这里开始下手。



```
open("./tls/x86_64/mikey-text.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
open("./tls/mikey-text.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
open("./x86_64/mikey-text.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
open("./mikey-text.so", O_RDONLY|O_CLOEXEC) = -1 ENOENT (No such file or directory)
```

该恶意软件没有在这些目录中显式搜索mikey-text.so。这是dlopen的副作用，根据其手册页的介绍： 

“在程序启动时，如果环境变量LD_LIBRARY_PATH中包含由冒号分隔的目录列表的话，则搜索这些目录。

在搜索片刻后，我们又找到了一个包含字符串“mikey-text.c”的二进制文件（SHA-256 bc6d25dff00dfb68b19b362c409d2cf497e5dd97d9d6e5ce2bde2ba706f2bdb3）。由此，我们可以判断mickey-text.so是这个二进制文件的编译版本。

根据这个判断，我们将第二个二进制文件重命名为mikey-text.so，并将其放在通过strace找到的加载路径中。这样一来，该恶意软件竟然能够成功执行了。其中，输出文件（out.log）用来保存键击动作及相应的时间戳。

[![](https://p1.ssl.qhimg.com/t0149fdc2613fc3a844.jpg)](https://p1.ssl.qhimg.com/t0149fdc2613fc3a844.jpg)

通过静态分析，我们能够知道，当键盘记录软件启动时，它首先会加载插件，然后处理相应的参数，最后生成相应的进程。

当加载插件时，该键盘记录软件会查找一个硬编码的插件（该插件名为“mikey-text.so”），并调用dlopen来获取它的句柄。

[![](https://p5.ssl.qhimg.com/t01836b74334ebf2825.jpg)](https://p5.ssl.qhimg.com/t01836b74334ebf2825.jpg)

一切加载就绪后，就会通过"keylogger"函数来完成该程序的主要功能。

为了更好地理解Linux键盘记录软件和相关的函数调用，掌握基本的X函数的相关知识是至关重要的。下面，我们就对“keylogger”函数用来查询击键信息以及获取原始击键数据的例程进行简要说明。

**XOpenDisplay** 返回用来连接X服务器的display结构。它是通过TCP或IPC进行通信的。

**XQueryKeymap** 该函数用于收集键盘状态方面的信息。此外，也可以使用该函数来收集当前按下了哪些键的信息。

**XkbKeycodeToKeysym** 该函数可以用来显示特定键的keysym。

**XKeysymToString** 将之前捕获到的keysym进行相应的转换。

**XGetInputFocus **获得当前的输入焦点。

一旦检索到键码，它就会与一个大型转换表进行比较，以将每个键码转换为字符串，这与大多数键盘记录软件没有什么两样。

[![](https://p2.ssl.qhimg.com/t011bea56c85ab8650a.jpg)](https://p2.ssl.qhimg.com/t011bea56c85ab8650a.jpg)

然后，找出不可打印的击键，并用人类可读的输出来代替它们。

[![](https://p5.ssl.qhimg.com/t0179486d58a9af0bbb.jpg)](https://p5.ssl.qhimg.com/t0179486d58a9af0bbb.jpg)

如果返回了不可打印的字符，就会调用一个小的函数来格式化括号中的字符串，以便将其输出到日志中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01da587f54f61bbad1.jpg)

一旦完成上述处理，相应的数据就被存储到一个缓冲区中，并传递给一个可加载模块。Linux的dlsym方法提供了与Windows上的“LoadLibrary”类似的功能。来自dlopen的上一个句柄将被传递给dlsym，这样，我们就可以使用它从mikey-text.so调用"getFeed"方法了。

[![](https://p5.ssl.qhimg.com/t01750d4cedef46191b.jpg)](https://p5.ssl.qhimg.com/t01750d4cedef46191b.jpg)

仔细阅读mikey-text.so的“getFeed”函数的代码你会发现它的功能其实非常简单，只是调用_log函数而已。

[![](https://p3.ssl.qhimg.com/t01cbaeda53a3522ec8.jpg)](https://p3.ssl.qhimg.com/t01cbaeda53a3522ec8.jpg)

接下来，_log函数将调用_time和_localtime（获取时间戳），并将它们构建为格式字符串。

[![](https://p4.ssl.qhimg.com/t01abf1553e085d2259.jpg)](https://p4.ssl.qhimg.com/t01abf1553e085d2259.jpg)

此时，该软件会通过"a +"标志打开输出文件，然后使用_fputs方法向文件写入内容。如果没有为mikey-text.so提供–output选项，则会使用默认名称“out.log”。下面的屏幕截图将cs：outputfile_ptr的内容识别为指向输出文件名称的指针。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013de868681e2aefdf.jpg)

除了一个解析参数的小函数外，mikey-text.so没有提供太多的功能。对于MiKey键盘记录软件来说，它只是一个简单的记录插件。Morphick认为，可能还存在其他插件（用于C2通信或挂接到其他文件），但目前尚无法确认。

为了运行键盘记录软件并通过一个定制参数将输出文件命名为keylogged.txt，可以使用如下所示的命令。此外，如果提供“-b”选项的话，它将在“后台”运行。

[![](https://p3.ssl.qhimg.com/t019be18d8f751988ff.jpg)](https://p3.ssl.qhimg.com/t019be18d8f751988ff.jpg)

为了检查主机上的进程，可以使用命令'ps aux'。

[![](https://p2.ssl.qhimg.com/t01749fea39bc8108ae.jpg)](https://p2.ssl.qhimg.com/t01749fea39bc8108ae.jpg)

然后，检查键盘记录文件的输出： 

[![](https://p5.ssl.qhimg.com/t0171242bba43b93031.jpg)](https://p5.ssl.qhimg.com/t0171242bba43b93031.jpg)

<br>

**结束语**

一般来说，为特定目的构建的小型实用程序通常能够轻松绕过杀毒软件。攻击者能够编写一个将内容转储到本地文件的键盘记录软件。通过编写模块化代码，作者可以通过构建插件来完成所需要的任何功能。同时，这个代码的插件性质还能增加逆向工程师的工作难度。由于无法访问每个模块，所以逆向工程师只能给该工具的特定已知功能进行备案。

对于这个键盘记录软件来说，最令人不安的地方在于，它没有提供主动的命令和控制功能，这就意味着攻击者在持续远程访问受害计算机来获取击键记录信息方面信心十足。

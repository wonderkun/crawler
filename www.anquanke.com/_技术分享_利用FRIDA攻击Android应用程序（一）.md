> 原文链接: https://www.anquanke.com//post/id/85758 


# 【技术分享】利用FRIDA攻击Android应用程序（一）


                                阅读量   
                                **318737**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：codemetrix.net
                                <br>原文地址：[https://www.codemetrix.net/hacking-android-apps-with-frida-1/](https://www.codemetrix.net/hacking-android-apps-with-frida-1/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p2.ssl.qhimg.com/t018592f3abec1d77a7.jpg)](https://p2.ssl.qhimg.com/t018592f3abec1d77a7.jpg)**

****

翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

<font face="微软雅黑, Microsoft YaHei">**传送门**</font>

[<font face="微软雅黑, Microsoft YaHei">**【技术分享】利用FRIDA攻击Android应用程序（二）**</font>](http://bobao.360.cn/learning/detail/3634.html)

**<br>**

**前言**

直到去年参加RadareCon大会时，我才开始接触动态代码插桩框架Frida。最初，我感觉这玩意还有点意思，后来发现这种感觉是不对的：应该是非常有意思。您还记得游戏中的上帝模式吗？面对本地应用程序的时候，一旦拥有了Frida，也就拥有了这种感觉。在这篇文章中，我们重点介绍Frida在Android应用方面的应用。在本文的第二篇中，我们将会介绍如何利用Frida来应付Android环境下的crackme问题。

**<br>**

**什么是动态代码插桩？ **

动态二进制插桩（DBI）意味着将外部代码注入到现有的（正在运行的）二进制文件中，从而让它们执行以前没有做过的事情。注意，这并非漏洞利用，因为代码的注入无需借助于漏洞。同时，它不是调试，因为你不必将二进制代码附加到一个调试器上面，当然，如果你非要这么做的好也未尝不可。那么DBI可以用来做什么呢？实际上，它可以用来做许多很酷的事情：

访问进程内存

在应用程序运行时覆盖函数

从导入的类调用函数

在堆上查找对象实例并使用它们

Hook、跟踪和拦截函数等。

当然，调试器也能完成所有这些事情，但是会比较麻烦。例如。在Android平台中，应用程序必须先进行反汇编和重新编译处理，才能进行调试。一些应用程序会尝试检测并阻止调试器，这时你必须先克服这一点，才能进行调试。然而，这一切做起来都会非常麻烦。在DBI与Frida的帮助下，这些事情都不是我们要关心的，所以调试会变得更加便捷。

**<br>**

**FRIDA入门**

[![](https://p1.ssl.qhimg.com/t019a4d94456b72796d.png)](https://p1.ssl.qhimg.com/t019a4d94456b72796d.png)

Frida“允许您在Windows、macOS、Linux、iOS、Android和QNX的本机应用程序中注入JavaScript或自己的库代码。”最开始的时候，它是基于谷歌的V8 Javascript运行时的，但是从版本9开始，Frida已经开始使用其内部的Duktape运行时了。不过，如果你需要V8的话，仍然可以切换回去。Frida可以通过多种操作模式与二进制程序进行交互（包括在非root的设备上给应用程序“插桩”），但是这里我们只介绍最简单的情形，同时也不关心其内部运行原理。

为了完成我们的实验，你需要

Frida

您可以从这里下载frida服务器的二进制代码（截止写作本文为止，最新版本为frida-server-9.1.16-android-arm.xz）

Android模拟器或已经获得root权限的设备。虽然Frida是在Android 4.4 ARM上面开发的，不过应该同样适用于更高的版本。就本文来说，使用Android 7.1 ARM完全没有一点问题。对于第二部分的crackme来说，则需要使用比Android 4.4更高的版本。

这里假设以linux系统作为主机操作系统，所以如果你使用Windows或Mac的话，有些命令可能需要进行相应的调整。

Frida的启动方式花样繁多，包括各种API和方法。您可以使用命令行界面或类似frida-trace的工具来跟踪底层函数（例如libc.so中的“open”函数），以便快速运行。同时，你还可以使用C、NodeJS或Python绑定完成更复杂的任务。但是在其内部，Frida使用Javascript的时候较多，换句话说，你可以通过这种语言完成大部分的插桩工作。所以，如果你像我一样不太喜欢Javascript的话（除了XSS功能），Frida倒是一个让你进一步了解它的理由。

首先，请安装Frida，具体如下所示（此外，您还可以通过查看README了解其他安装方式）： 

```
pip install frida
npm install frida
```

启动模拟器或连接设备，确保adb正在运行并列出您的设备： 

```
michael@sixtyseven:~$ adb devices
List of devices attached
emulator-5556device
```

然后，开始安装frida-server。先进行解压，并将二进制文件放入设备中： 

```
adb push /home/michael/Downloads/frida-server-9.1.16-android-arm /data/local/tmp/frida-server
```

在设备上打开一个shell，切换到root用户，并启动frida： 

```
adb shell
su
cd /data/local/tmp
chmod 755 frida-server
./frida-server
```

（注意事项1：如果frida-server没有启动，请检查当前是否为root用户，以及文件是否在传输过程中发生损坏。当文件传输而导致文件损坏的时候，经常会出现一些让人奇怪的错误提示。注意事项2：如果你想以后台进程的方式启动frida-server的话，则需要使用./frida-server＆）

您可以另一个终端的常规操作系统shell中检查Frida是否正在运行，并列出Android上的进程： 

```
frida-ps -U
```

-U代表USB，允许Frida检查USB设备，同时还可用于仿真器。这时，您将看到一个如下所示进程列表： 

```
michael@sixtyseven:~$ frida-ps -U
 PID  Name
----  --------------------------------------------------
 696  adbd
5828  android.ext.services
6188  android.process.acore
5210  audioserver
5211  cameraserver
8334  com.android.calendar
6685  com.android.chrome
6245  com.android.deskclock
5528  com.android.inputmethod.latin
6120  com.android.phone
6485  com.android.printspooler
8355  com.android.providers.calendar
5844  com.android.systemui
7944  com.google.android.apps.nexuslauncher
6416  com.google.android.gms
[...]
```

您将看到进程标识（PID）和正在运行的进程（名称）。现在，您可以通过Frida挂钩到任何一个进程并对其进行“篡改”了。

例如，您可以跟踪由Chrome使用的特定调用（如果还没有运行该浏览器的话，请首先在模拟器中启动它）： 

```
frida-trace -i "open" -U com.android.chrome
```

输出结果如下所示： 

```
michael@sixtyseven:~$ frida-trace -i open -U -f com.android.chrome
Instrumenting functions...                                              
open: Loaded handler at "/home/michael/__handlers__/libc.so/open.js"
Started tracing 1 function. Press Ctrl+C to stop.                       
           /* TID 0x2740 */
   282 ms  open(pathname=0xa843ffc9, flags=0x80002)
           /* TID 0x2755 */
   299 ms  open(pathname=0xa80d0c44, flags=0x2)
           /* TID 0x2756 */
   309 ms  open(pathname=0xa80d0c44, flags=0x2)
           /* TID 0x2740 */
   341 ms  open(pathname=0xa80d06f7, flags=0x2)
   592 ms  open(pathname=0xa77dd3bc, flags=0x0)
   596 ms  open(pathname=0xa80d06f7, flags=0x2)
   699 ms  open(pathname=0xa80d105e, flags=0x80000)
   717 ms  open(pathname=0x9aff0d70, flags=0x42)
   742 ms  open(pathname=0x9ceffda0, flags=0x0)
   758 ms  open(pathname=0xa63b04c0, flags=0x0)
```

frida-trace命令会生成一个小巧的javascript文件，然后Frida会将其注入到进程中，并跟踪特定的调用。您可以观察一下在__handlers __ / libc.so/open.js路径下面生成的open.js脚本。它将钩住libc.so中的open函数并输出参数。使用Frida的情况下，这非常简单： 

```
[...]
onEnter: function (log, args, state) `{`
    log("open(" + "pathname=" + args[0] + ", flags=" + args[1] + ")");
`}`,
[...]
```

请注意Frida是如何访问Chrome内部调用的open函数的调用参数（args [0]，args [1]等）的。现在，让我们对这个脚本稍做修改。如果我们输出以纯文本形式打开的文件的路径，而不是存储这些路径的内存地址，那不是更好吗？ 幸运的是，我们可以直接访问内存。为此，您可以参考Frida API和Memory对象。我们可以修改脚本，让它将内存地址中的内容作为UTF8字符串输出，这样结果会更加一目了然。现在修改脚本，具体为： 

```
onEnter: function (log, args, state) `{`
    log("open(" + "pathname=" + Memory.readUtf8String(args[0])+ ", flags=" + args[1] + ")");
`}`,
```

（我们只是添加了Memory.readUtf8String函数）我们会得到如下所示输出： 

```
michael@sixtyseven:~$ frida-trace -i open -U -f com.android.chrome
Instrumenting functions...                                              
open: Loaded handler at "/home/michael/__handlers__/libc.so/open.js"
Started tracing 1 function. Press Ctrl+C to stop.                       
           /* TID 0x29bf */
   240 ms  open(pathname=/dev/binder, flags=0x80002)
           /* TID 0x29d3 */
   259 ms  open(pathname=/dev/ashmem, flags=0x2)
           /* TID 0x29d4 */
   269 ms  open(pathname=/dev/ashmem, flags=0x2)
           /* TID 0x29bf */
   291 ms  open(pathname=/sys/qemu_trace/process_name, flags=0x2)
   453 ms  open(pathname=/dev/alarm, flags=0x0)
   456 ms  open(pathname=/sys/qemu_trace/process_name, flags=0x2)
   562 ms  open(pathname=/proc/self/cmdline, flags=0x80000)
   576 ms  open(pathname=/data/dalvik-cache/arm/system@app@Chrome@Chrome.apk@classes.dex.flock, flags=0x42)
```

Frida打印出了路径名。这很容易，对吧？

另一个要注意的是，你可以先启动一个应用程序，然后让Frida注入它的magic，或者传递-f选项给Frida，让它创建进程。

现在，我们来考察Fridas的命令行接口frida-cli： 

```
frida -U -f com.android.chrome
```

这将启动Frida和Chrome应用。但是，仍启动Chrome的主进程。这是为了让您可以在应用程序启动主进程之前注入Frida代码。不幸的是，在我实验时，它总是导致应用程序2秒后自动终止。这不是我们想要的结果。您可以利用这2秒钟时间输入％resume，并让应用程序启动其主进程；或者，直接使用–no-pause选项启动Frida，这样就不会中断应用程序了，并将生成的进程的任务留给Frida。

[![](https://p3.ssl.qhimg.com/t0183c3f5fe61948d58.png)](https://p3.ssl.qhimg.com/t0183c3f5fe61948d58.png)

无论使用哪种方法，你都会得到一个shell（不会被杀死），这样就可以使用它的Javascript API向Frida写命令了。通过TAB可以查看可用的命令。此外，这个shell还支持命令自动完成功能。

[![](https://p0.ssl.qhimg.com/t013d3d85f0a9d0f3da.png)](https://p0.ssl.qhimg.com/t013d3d85f0a9d0f3da.png)

它提供了非常详尽的文档说明。对于Android，请检查JavaScript-API的Java部分（这里将讨论一个“Java API”，虽然从技术上说应该是一个访问Java对象的Javascript包装器）。在下面，我们将重点介绍这个Java API，因为在跟Android应用程序打交道的时候，这是一种更加方便的方法。不同于挂钩libc函数，实际上我们可以直接使用Java函数和对象。

作为使用Java API的第一步，不妨从显示Frida的命令行界面运行的Android的版本开始： 

```
[USB::Android Emulator 5556::['com.android.chrome']]-&gt; Java.androidVersion
"7.1.1"
```

或者列出加载的类（警告：这会输出大量内容，下面我会对代码进行相应的解释）： 

```
[USB::Android Emulator 5556::['com.android.chrome']]-&gt; Java.perform(function()`{`Java.enumerateLoadedClasses(`{`"onMatch":function(className)`{` console.log(className) `}`,"onComplete":function()`{``}``}`)`}`)
org.apache.http.HttpEntityEnclosingRequest
org.apache.http.ProtocolVersion
org.apache.http.HttpResponse
org.apache.http.impl.cookie.DateParseException
org.apache.http.HeaderIterator
```

我们在这里输入了一个比较长的命令，确切地说是一些嵌套的函数代码。首先，请注意，我们输入的代码必须包装在Java.perform（function（）`{`…`}`）中，这是Fridas的Java API的硬性要求。

下面是我们在Java.perform包装器中插入的函数体： 

```
Java.enumerateLoadedClasses(
  `{`
  "onMatch": function(className)`{` 
        console.log(className) 
    `}`,
  "onComplete":function()`{``}`
  `}`
)
```

上面的代码非常简单：我们使用Fridas API的Java.enumerateLoadedClasses枚举所有加载的类，并使用console.log将匹配的类输出到控制台。这种回调对象在Frida中是一种非常常见的模式。你可以提供一个回调对象，形式如下所示 

```
`{`
  "onMatch":function(arg1, ...)`{` ... `}`,
  "onComplete":function()`{` ... `}`,
`}`
```

当Frida找到符合要求的匹配项时，就会使用一个或多个参数来调用onMatch；当Frida完成匹配工作时，就会调用onComplete。<br>

现在，让我们进一步学习Frida的magic，并通过Frida覆盖一个函数。此外，我们还将介绍如何从外部脚本加载代码，而不是将代码键入cli，因为这种方式更方便。首先，将下面的代码保存到一个脚本文件中，例如chrome.js： 

```
Java.perform(function () `{`
    var Activity = Java.use("android.app.Activity");
    Activity.onResume.implementation = function () `{`
        console.log("[*] onResume() got called!");
        this.onResume();
    `}`;
`}`);
```

上面的代码将会覆盖android.app.Activity类的onResume函数。它会调用Java.use来接收这个类的包装对象，并访问其onResume函数的implementation属性，以提供一个新的实现。在新的函数体中，它将通过this.onResume()调用原始的onResume实现，所以应用程序依然可以继续正常运行。

打开您的模拟器和Chrome，然后通过-l选项来注入这个脚本： 

```
frida -U -l chrome.js com.android.chrome
```

一旦触发了onResume——例如切换到另一个应用程序并返回到模拟器中的Chrome——您将收到下列输出： 

```
[*] onResume() got called!
```

很好，不是吗？我们实际上覆盖了应用程序中的一个函数。这就给控制目标应用程序的行为提供了可能性。但是，实际上我们可以继续发挥：还能够利用Javaschoose查找堆中已经实例化的对象。

需要注意的是，当你的模拟速度较慢的时候，Frida经常会超时。为了防止这种情况，请将脚本封装到函数setImmediate中，或将它们导出为rpc。RPC在Frida默认情况下不超时（感谢@oleavr给予的提示）。在修改脚本文件后，setImmediate将自动重新运行你的脚本，所以这是相当方便的。同时，它还在后台运行您的脚本。这意味着你会立刻得到一个cli，即使Frida仍然在忙着处理你的脚本。请继续等待，不要离开cli，直到Frida显示脚本的输出为止。然后，再次修改chrome.js： 

```
setImmediate(function() `{`
    console.log("[*] Starting script");
    Java.perform(function () `{`
        Java.choose("android.view.View", `{` 
             "onMatch":function(instance)`{`
                  console.log("[*] Instance found");
             `}`,
             "onComplete":function() `{`
                  console.log("[*] Finished heap search")
             `}`
        `}`);
    `}`);
`}`);
```

运行frida -U -l chrome.js com.android.chrome，这时应该会产生以下输出： 

```
[*] Starting script
[*] Instance found
[*] Instance found
[*] Instance found
[*] Instance found
[*] Finished heap search
```

我们在堆上找到了4个android.view.View对象的实例。让我们看看能用这些搞点什么事情。首先，我们可以调用这些实例的对象方法。这里，我们只是为console.log输出添加instance.toString（）。由于我们使用了setImmediate，所以现在只需修改我们的脚本，然后Frida会自动重新加载它： 

```
setImmediate(function() `{`
    console.log("[*] Starting script");
    Java.perform(function () `{`
        Java.choose("android.view.View", `{` 
             "onMatch":function(instance)`{`
                  console.log("[*] Instance found: " + instance.toString());
             `}`,
             "onComplete":function() `{`
                  console.log("[*] Finished heap search")
             `}`
        `}`);
    `}`);
`}`);
```

返回的结果为： 

```
[*] Starting script
[*] Instance found: android.view.View`{`7ccea78 G.ED..... ......ID 0,0-0,0 #7f0c01fc app:id/action_bar_black_background`}`
[*] Instance found: android.view.View`{`2809551 V.ED..... ........ 0,1731-0,1731 #7f0c01ff app:id/menu_anchor_stub`}`
[*] Instance found: android.view.View`{`be471b6 G.ED..... ......I. 0,0-0,0 #7f0c01f5 app:id/location_bar_verbose_status_separator`}`
[*] Instance found: android.view.View`{`3ae0eb7 V.ED..... ........ 0,0-1080,63 #102002f android:id/statusBarBackground`}`
[*] Finished heap search
```

Frida实际上为我们调用了android.view.View对象实例的toString方法。酷毙了！所以，在Frida的帮助下，我们可以读取进程内存、修改函数、查找实际的对象实例，并且所有这些只需寥寥几行代码就可以搞定。

现在，我们已经对Frida有了一个基本的了解，如果想要进一步深入了解它的话，可以自学其文档和API。为了使得这篇文章更加全面，本文还将介绍两个主题，即Frida的绑定和r2frida。但是在此之前，需要首先指出一些注意事项。



**注意事项**

当使用Frida时，经常会出现一些不稳定的情形。首先，将外部代码注入另一个进程容易导致崩溃，毕竟应用程序是以其非预期的方式被触发，来执行某些额外的功能的。第二，Frida本身貌似仍然处于实验阶段。它的确非常有用，但是许多时候我们必须尝试各种方式才能获得所需的结果。例如，当我尝试从命令行加载脚本然后生成一个命令的进程时，Frida总是崩溃。所以，我不得不先生成进程，然后让Frida注入脚本。这就是为什么我展示Frida的使用和防止超时的各种方法的原因。当然，许多时候您要根据自己的具体情况来找出最有效的方法。 

<br>

**Python绑定**

若想利用Frida进一步提升自己工作的自动化程度的话，你应该学习应用性更高的Python、C或NodeJS绑定，当然，前提是你已经熟悉了Frida的工作原理。例如，要从Python注入chrome.js脚本的话，可以使用Frida的Python绑定。首先，创建一个chrome.py脚本： 



```
#!/usr/bin/python
import frida
# put your javascript-code here
jscode= """
console.log("[*] Starting script");
Java.perform(function() `{`
   var Activity = Java.use("android.app.Activity");
    Activity.onResume.implementation = function () `{`
        console.log("[*] onResume() got called!");
        this.onResume();
    `}`;
`}`);
"""
# startup frida and attach to com.android.chrome process on a usb device
session = frida.get_usb_device().attach("com.android.chrome")
# create a script for frida of jsccode
script = process.create_script(jscode)
# and load the script
script.load()
```

更多的例子，请参考Frida的文档。

<br>

**Frida和Radare2：r2frida**

如果我们还可以使用类似Radare2之类的反汇编框架来检查应用程序的内存的话，那不是更好吗？别急，我们有r2frida。您可以使用r2frida将Radare2连接到Frida，然后对进程的内存进行静态分析和反汇编处理。不过，我们这里不会对r2frida进行详细的介绍，因为我们假设您已经了解了Radare2的相关知识（如果您对它还比较陌生的话，建议您抽时间学习一下，我认为这是非常值得的）。无论如何，您都没有必要过于担心，因为这个软件的用法非常容易上手，看看下面的例子您就知道此言不虚。

您可以使用Radare2的数据包管理程序来安装r2frida（假设您已经安装了Radare2）： 

```
r2pm install r2frida
```

回到我们的frida-trace示例，删除或重命名我们修改的脚本，让frida-trace再次生成默认的脚本，并重新查看日志： 



```
michael@sixtyseven:~$ frida-trace -i open -U -f com.android.chrome
Instrumenting functions...                                              
open: Loaded handler at "/home/michael/__handlers__/libc.so/open.js"
Started tracing 1 function. Press Ctrl+C to stop.                       
           /* TID 0x2740 */
   282 ms  open(pathname=0xa843ffc9, flags=0x80002)
           /* TID 0x2755 */
   [...]
```

使用r2frida的话，您可以轻松地检查所显示的内存地址的内容并读取路径名（在本例中为/ dev / binder）： 



```
root@sixtyseven:~# r2 frida://emulator-5556/com.android.chrome
 -- Enhance your graphs by increasing the size of the block and graph.depth eval variable.
[0x00000000]&gt; s 0xa843ffc9
[0xa843ffc9]&gt; px
- offset -   0 1  2 3  4 5  6 7  8 9  A B  C D  E F  0123456789ABCDEF
0xa843ffc9  2f64 6576 2f62 696e 6465 7200 4269 6e64  /dev/binder.Bind
0xa843ffd9  6572 2069 6f63 746c 2074 6f20 6f62 7461  er ioctl to obta
0xa843ffe9  696e 2076 6572 7369 6f6e 2066 6169 6c65  in version faile
0xa843fff9  643a 2025 7300 4269 6e64 6572 2064 7269  d: %s.Binder dri
[...]
```

访问进程以及让r2frida执行注入操作的语法如下所示： 

```
r2 frida://DEVICE-ID/PROCESS
```

下面展示以=！为前缀的情况下，有哪些可用的r2frida命令，其中，您可以快速搜索内存区域中特定的内容或对任意内存地址执行写入操作： 



```
[0x00000000]&gt; =!?
r2frida commands available via =!
?                          Show this help
?V                         Show target Frida version
/[x][j] &lt;string|hexpairs&gt;  Search hex/string pattern in memory ranges (see search.in=?)
/w[j] string               Search wide string
[...]
```



**小结**

在这篇文章中，我们重点介绍Frida在Android应用方面的应用。在本教程的第二篇中，我们将介绍如何通过Frida轻松搞定crackme。

<br>



**传送门**

[**【技术分享】利用FRIDA攻击Android应用程序（二）**](http://bobao.360.cn/learning/detail/3634.html)

<br>

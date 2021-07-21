> 原文链接: https://www.anquanke.com//post/id/225911 


# DLL劫持原理及其漏洞挖掘（一）


                                阅读量   
                                **186318**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01ad4fae2d6f19c02d.png)](https://p4.ssl.qhimg.com/t01ad4fae2d6f19c02d.png)



## 0x0 前言

简单叙述下自己研究DLL劫持的原因。
- 0.学习window的库加载思想
- 1.为了在sangforSRC挖个洞去长沙打个卡。
- 2.免杀及其权限持久化维持的一个思路


## 0x1 DLL是什么

动态链接库(Dynamic-Link-Library,缩写dll), 是微软公司在微软视窗操作系统中实现共享函数库概念的一种实现方式。这些库函数的扩展名是`.DLL`、`.OCX`(包含[ActiveX](https://zh.wikipedia.org/wiki/ActiveX)控制的库)或者`.DRV`(旧式的系统的[驱动程序](https://zh.wikipedia.org/wiki/%E9%A9%B1%E5%8A%A8%E7%A8%8B%E5%BA%8F))

> 所谓动态链接,就是把一些经常会共享的代码(静态链接的[OBJ](https://zh.wikipedia.org/w/index.php?title=OBJ&amp;action=edit&amp;redlink=1)程序库)制作成DLL档,当可执行文件调用到DLL档内的函数时，Windows操作系统才会把DLL档加载进存储器内，DLL档本身的结构就是可执行档，当程序有需求时函数才进行链接。通过动态链接方式，存储器浪费的情形将可大幅降低。[静态链接库](https://zh.wikipedia.org/wiki/%E9%9D%9C%E6%85%8B%E9%80%A3%E7%B5%90%E5%87%BD%E5%BC%8F%E5%BA%AB)则是直接[链接](https://zh.wikipedia.org/wiki/%E9%93%BE%E6%8E%A5%E5%99%A8)到可执行文件
DLL的文件格式与视窗[EXE](https://zh.wikipedia.org/wiki/EXE)文件一样——也就是说，等同于[32位](https://zh.wikipedia.org/wiki/32%E4%BD%8D)视窗的[可移植执行文件](https://zh.wikipedia.org/wiki/Portable_Executable)（PE）和[16位](https://zh.wikipedia.org/wiki/16%E4%BD%8D)视窗的[New Executable](https://zh.wikipedia.org/w/index.php?title=New_Executable&amp;action=edit&amp;redlink=1)（NE）。作为EXE格式，DLL可以包括[源代码](https://zh.wikipedia.org/wiki/%E5%8E%9F%E5%A7%8B%E7%A2%BC)、[数据](https://zh.wikipedia.org/w/index.php?title=Data_(computing)&amp;action=edit&amp;redlink=1)和[资源](https://zh.wikipedia.org/w/index.php?title=Resource_(Windows)&amp;action=edit&amp;redlink=1)的多种组合。
还有更广泛的定义,这个没必要去理解了。

一些与之相关的概念:

> 静态库与动态库的比较
静态库被链接后直接嵌入可执行文件中
好处: 不需要外部函数支持,无环境依赖,兼容性好。
坏处: 容易浪费空间，不方便修复bug。
动态库的好处与静态库相对。
Linux下静态库名字一般是: `libxxx.a` window则是: `*.lib`、`*.h`
Linux下动态库名字一般是:`libxxx.so` window则是: `.dll`、`.OCX`(..etc)



## 0x2 DLL的用途

DLL动态链接库，是程序进行动态链接时加载的库函数。

故动态链接最直接的好处是磁盘和内存的消耗减少，这也是dll最初的目的。

不过，dll也有缺点，就是容易造成版本冲突,比如不同的应用程序共享同一个dll,而它们需求的是不同的版本，这就会出现矛盾,解决办法是把不同版本的dll放在不同的文件夹中。



## 0x3 入门DLL的使用

### <a class="reference-link" name="0x3.1%20%E7%BC%96%E5%86%99TestDll.dll"></a>0x3.1 编写TestDll.dll

1.采用vs2017新建DLL项目

[![](https://p5.ssl.qhimg.com/t01395609125de42c63.png)](https://p5.ssl.qhimg.com/t01395609125de42c63.png)

2.分析DLL的组成

[![](https://p5.ssl.qhimg.com/t0126dd463d2147e655.png)](https://p5.ssl.qhimg.com/t0126dd463d2147e655.png)

其中`dllmain.cpp`代码如下

每个DLL都可以有一个入口点函数DllMain,系统会在不同时刻调用此函数。

```
// dllmain.cpp : 定义 DLL 应用程序的入口点。
#include "pch.h"

BOOL APIENTRY DllMain( HMODULE hModule, // 模块句柄
                       DWORD  ul_reason_for_call, // 调用原因
                       LPVOID lpReserved // 参数保留
                     )
`{`
    switch (ul_reason_for_call) // 根据调用原因选择不不同的加载方式
    `{`
    case DLL_PROCESS_ATTACH: // DLL被某个程序加载
    case DLL_THREAD_ATTACH: // DLL被某个线程加载
    case DLL_THREAD_DETACH: // DLL被某个线程卸载
    case DLL_PROCESS_DETACH: //DLL被某个程序卸载
        break;
    `}`
    return TRUE;
`}`
```

我们可以在该文件下引入`Windows.h`库,然后编写一个`msg`的函数。

```
#include &lt;Windows.h&gt;

void msg() `{`
    MessageBox(0, L"Dll-1 load  succeed!", 0, 0);
`}`
```

接下来在解决方案资源管理下的项目下打开头文件中的`framework.h`来导出msg函数.

```
#pragma once

#define WIN32_LEAN_AND_MEAN             // 从 Windows 头文件中排除极少使用的内容
// Windows 头文件
#include &lt;windows.h&gt;

extern "C" __declspec(dllexport) void msg(void);
```

然后点击生成中的重新生成解决方案编译得到`TestDll.dll`文件。

[![](https://p2.ssl.qhimg.com/t01691efeefc9d3ebff.png)](https://p2.ssl.qhimg.com/t01691efeefc9d3ebff.png)

可以用16进制文件查看下dll的文件头，正如上面所说的一样，和exe是一样的。

[![](https://p4.ssl.qhimg.com/t0104095d185070c4ff.png)](https://p4.ssl.qhimg.com/t0104095d185070c4ff.png)

### <a class="reference-link" name="0x3.2%20%E8%B0%83%E7%94%A8dll%E6%96%87%E4%BB%B6"></a>0x3.2 调用dll文件

解决方案处右键新建一个项目，选择&gt;控制台应用取名`hello`

[![](https://p0.ssl.qhimg.com/t01871eac52031a6b14.png)](https://p0.ssl.qhimg.com/t01871eac52031a6b14.png)

修改`hello.cpp`的文件内容如下:

```
// hello.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
#include &lt;iostream&gt;
#include &lt;Windows.h&gt;
using namespace std;

int main()
`{`
    // 定义一个函数类DLLFUNC
    typedef void(*DLLFUNC)(void);
    DLLFUNC GetDllfunc = NULL;
    // 指定动态加载dll库
    HINSTANCE hinst = LoadLibrary(L"TestDll.dll");
    if (hinst != NULL) `{`
        // 获取函数位置
        GetDllfunc = (DLLFUNC)GetProcAddress(hinst, "msg");
    `}`
    if (GetDllfunc != NULL) `{`
        //运行msg函数
        (*GetDllfunc)();
    `}`
`}`
```

然后ctrl+F5,运行调试。

[![](https://p0.ssl.qhimg.com/t01871eac52031a6b14.png)](https://p0.ssl.qhimg.com/t01871eac52031a6b14.png)

可以看到成功加载了我们写的msg函数。

有关代码中更多的细节的解释可以参考: [C++编写DLL文件](https://my.oschina.net/u/4338312/blog/3376870)



## 0x4 DLL劫持漏洞

### <a class="reference-link" name="0x4.1%20%E5%8E%9F%E7%90%86%E7%AE%80%E8%BF%B0"></a>0x4.1 原理简述

什么是DLL劫持漏洞(DLL Hijacking Vulnerability)?

> 如果在进程尝试加载一个DLL时没有并没有**指定DLL的绝对路径**，那么Windows会尝试去按照顺序搜索这些特定目录来查找这个DLL,如果攻击者能够将恶意的DLL放在优先于正常DLL所在的目录，那么就能够欺骗系统去加载恶意的DLL，形成”劫持”,CWE将其归类为**UntrustedSearch Path Vulnerability**,比较直译的一种解释。

### <a class="reference-link" name="0x4.2%20%E6%9F%A5%E6%89%BEDLL%E7%9B%AE%E5%BD%95%E7%9A%84%E9%A1%BA%E5%BA%8F"></a>0x4.2 查找DLL目录的顺序

正如[动态链接库安全](https://docs.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-security) 、[动态链接库搜索顺序](https://docs.microsoft.com/zh-cn/windows/win32/dlls/dynamic-link-library-search-order)微软的官方文档所说,

在Windows XP SP2 之前(不包括), 默认未启用DLL搜索模式。

Windows查找DLL目录及其顺序如下:

> <ol>
- The directory from which the application loaded.
- The current directory.
- The system directory. Use the [**GetSystemDirectory**](https://docs.microsoft.com/en-us/windows/desktop/api/sysinfoapi/nf-sysinfoapi-getsystemdirectorya) function to get the path of this directory.
- The 16-bit system directory. There is no function that obtains the path of this directory, but it is searched.
- The Windows directory. Use the [**GetWindowsDirectory**](https://docs.microsoft.com/en-us/windows/desktop/api/sysinfoapi/nf-sysinfoapi-getwindowsdirectorya) function to get the path of this directory.
- The directories that are listed in the PATH environment variable. Note that this does not include the per-application path specified by the **App Paths** registry key. The **App Paths** key is not used when computing the DLL search path.
</ol>

在Windows下, 几乎每一种文件类型都会关联一个对应的处理程序。

首先DLL会先尝试搜索启动程序所处的目录(1)，没有找到，则搜索被打开文件所在的目录(2),若还没有找到,则搜索系统目录(3),若还没有找到,则向下搜索16位系统目录，…Windows目录…Path环境变量的各个目录。

**这样的加载顺序很容易导致一个系统dll被劫持，因为只要攻击者将目标文件和恶意dll放在一起即可,导致恶意dll先于系统dll加载，而系统dll是非常常见的，所以当时基于这样的加载顺序，出现了大量受影响软件。**

后来为了减轻这个影响,默认情况下，从Windows XP Service Pack 2（SP2）开始启用安全DLL搜索模式。

> <ol>
- The directory from which the application loaded.
- The system directory. Use the [**GetSystemDirectory**](https://docs.microsoft.com/en-us/windows/desktop/api/sysinfoapi/nf-sysinfoapi-getsystemdirectorya) function to get the path of this directory.
- The 16-bit system directory. There is no function that obtains the path of this directory, but it is searched.
- The Windows directory. Use the [**GetWindowsDirectory**](https://docs.microsoft.com/en-us/windows/desktop/api/sysinfoapi/nf-sysinfoapi-getwindowsdirectorya) function to get the path of this directory.
- The current directory.
- The directories that are listed in the PATH environment variable. Note that this does not include the per-application path specified by the **App Paths** registry key. The **App Paths** key is not used when computing the DLL search path.
</ol>

可以看到当前目录被放置在了后面,对系统dll起到一定的保护作用。

注:

> 强制关闭SafeDllSearchMode的方法:
创建注册表项:
<pre><code class="hljs">HKEY_LOCAL_MACHINE\System\CurrentControlSet\Control\Session Manager\SafeDllSearchMode
</code></pre>
值为0

**不过从上面分析可以知道,系统dll应该是经常调用的,如果我们对程序安装的目录拥有替换权限，比如装在了非系统盘，那么我们同样可以利用加载顺序的(1)来劫持系统的DLL。**

从Windows7 之后, 微软为了更进一步的防御系统的DLL被劫持，将一些容易被劫持的系统DLL写进了一个注册表项中，**那么凡是此项下的DLL文件就会被禁止从EXE自身所在的目录下调用**，而只能从系统目录即SYSTEM32目录下调用。注册表路径如下：

```
HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs
```

win10的键值项,如图:

[![](https://p2.ssl.qhimg.com/t019550cc015bc3f87f.png)](https://p2.ssl.qhimg.com/t019550cc015bc3f87f.png)

这样子就进一步保护了系统dll,防止这些常用的dll被劫持加载。

但是如果开发者滥用DLL目录，依然会导致DLL劫持问题。(开发真难…orz)

### <a class="reference-link" name="0x4.3%20%E9%98%B2%E5%BE%A1%E6%80%9D%E8%B7%AF"></a>0x4.3 防御思路
- 调用第三方DLL时,使用绝对路径
- 调用API SetDllDirectory(L”“)将当前目录从DLL加载顺序中移除
- 开发测试阶段，可以采用Process Monitor进行黑盒复测


## 0x5 实例演示

这里我们需要使用一个工具:[Process Monitor v3.60](https://docs.microsoft.com/zh-cn/sysinternals/downloads/procmon)

操作过程如[动态链接库安全](https://docs.microsoft.com/zh-cn/windows/win32/dlls/dynamic-link-library-security?redirectedfrom=MSDN)所说:

[![](https://p2.ssl.qhimg.com/t012ddcd0107923e8cc.png)](https://p2.ssl.qhimg.com/t012ddcd0107923e8cc.png)

打开进程监视器的时候,会要求填入过滤器。

```
Include the following filters:
Operation is CreateFile
Operation is LoadImage
Path contains .cpl
Path contains .dll
Path contains .drv
Path contains .exe
Path contains .ocx
Path contains .scr
Path contains .sys

Exclude the following filters:
Process Name is procmon.exe
Process Name is Procmon64.exe
Process Name is System
Operation begins with IRP_MJ_
Operation begins with FASTIO_
Result is SUCCESS
Path ends with pagefile.sys
```

一次填好即可(通过上面的配置，我们可以过滤大量无关的信息,快速定位到DLL确实的路径)

[![](https://p3.ssl.qhimg.com/t01c29614bd42ccbc01.png)](https://p3.ssl.qhimg.com/t01c29614bd42ccbc01.png)

然后我们随便打开一个程序,这里我使用的是深x服的EasyConnectInstaller:

[![](https://p3.ssl.qhimg.com/t014198a1a75b536316.png)](https://p3.ssl.qhimg.com/t014198a1a75b536316.png)

可以看到这里最终会去尝试加载当前目录的一些dll,这里可以尝试进行替换rattler中的`payload.dll`名字即可,点击执行就可以弹出calc了。

[![](https://p0.ssl.qhimg.com/t012f62019d50a97fca.png)](https://p0.ssl.qhimg.com/t012f62019d50a97fca.png)



## 0x6 自动化挖掘

### <a class="reference-link" name="0x6.1%20Ratter"></a>0x6.1 Ratter

1.下载地址:[https://github.com/sensepost/rattler/releases/](https://github.com/sensepost/rattler/releases/)

2.使用

`Rattler_x64.exe NDP461-KB3102438-Web.exe 1`

[![](https://p0.ssl.qhimg.com/t018ef2475ec7fa761e.png)](https://p0.ssl.qhimg.com/t018ef2475ec7fa761e.png)

结果发现这个并没有检测出来,可能是calc.exe启动失败的原因,个人感觉这个工具并不是很准确。

### <a class="reference-link" name="0x6.2%20ChkDllHijack"></a>0x6.2 ChkDllHijack

1.下载地址:[[https://github.com/anhkgg/anhkgg-tools](https://github.com/anhkgg/anhkgg-tools)]

2.使用windbg导出module

[![](https://p0.ssl.qhimg.com/t01fdb51bcc04803603.png)](https://p0.ssl.qhimg.com/t01fdb51bcc04803603.png)

然后打开chkDllHijack,粘贴处要验证的DLL内容

[![](https://p1.ssl.qhimg.com/t0182112203820ea668.png)](https://p1.ssl.qhimg.com/t0182112203820ea668.png)

然后让他自己跑完即可,如果成功下面就会出现结果。

否则就是失败:

[![](https://p4.ssl.qhimg.com/t01aea560a7ea7951dc.png)](https://p4.ssl.qhimg.com/t01aea560a7ea7951dc.png)



## 0x7 总结

综合来说,我个人还是比较推荐采用Process monitor作为辅助工具,然后自己手工验证这种挖掘思路的,不过自动化的确挺好的，可以尝试自己重新定制下检测判断规则。本文依然倾向于入门的萌新选手,后面可能会回归DLL代码细节和免杀利用方面来展开(这个过程就比较需要耗时间Orz,慢慢填坑吧)。



## 0x8 参考链接

[.dll 文件编写和使用](https://www.cnblogs.com/whlook/p/6701688.html)

[DLL劫持-免杀](https://blog.haiya360.com/archives/826.html)

[DLL劫持漏洞自动化识别工具Rattler测试](https://3gstudent.github.io/DLL%E5%8A%AB%E6%8C%81%E6%BC%8F%E6%B4%9E%E8%87%AA%E5%8A%A8%E5%8C%96%E8%AF%86%E5%88%AB%E5%B7%A5%E5%85%B7Rattler%E6%B5%8B%E8%AF%95/)

[注入技术系列：一个批量验证DLL劫持的工具](https://www.freebuf.com/vuls/218917.html)

[恶意程序研究之DLL劫持](https://www.ascotbe.com/2020/11/13/DynamicLinkLibraryHijack/#%E5%AE%9E%E6%88%98%E5%8C%96%E5%88%A9%E7%94%A8)

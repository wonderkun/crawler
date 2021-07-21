> 原文链接: https://www.anquanke.com//post/id/201221 


# 在Go运行时托管CLR并执行.NET程序集


                                阅读量   
                                **610069**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ropnop，文章来源：blog.ropnop.com
                                <br>原文地址：[https://blog.ropnop.com/hosting-clr-in-golang/](https://blog.ropnop.com/hosting-clr-in-golang/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01e2c508b9c3aa6c7d.jpg)](https://p5.ssl.qhimg.com/t01e2c508b9c3aa6c7d.jpg)



## 一、概述

最近，有人在询问Go是否可以用于运行.NET程序集（DLL或EXE），我在Twitter上回答了很多内容。尽管在最近一段时间内，我一直在使用Go语言来写代码，但似乎从来没有尝试过在Windows上使用Go语言做太多事情，比如系统调用交互或者使用CGo这样的先进技术。这看上去像是一个非常有趣的挑战，因此我决定花费一些时间来进行研究。在读完《Black Hat Go》这本书之后，我想也许我已经足够了解相关知识，并且似乎不太复杂。但事实证明，我的想法是错误的。但无论如何，我最终成功研究出来了PoC，并学到了很多东西，我决定通过本文来与大家分享我的研究过程与结果。<br>
我已经在GitHub上发布了我的PoC代码：go-clr。这个软件包可以让我们托管CLR，并从磁盘执行DLL，或者从内存执行托管程序集。简而言之，我们可以运行以下内容：

```
import (
    clr "github.com/ropnop/go-clr"
    log
    fmt
)

func main() `{`
    var exeBytes = []byte`{`0xa1 ....etc`}`
    retCode, err := clr.ExecuteByteArray(exeBytes)
    if err != nil `{`
        log.Fatal(err)
    `}`
    fmt.Printf(["[+] Exit code: %dn", retCode)
`}`
```

请查看示例以获取更多代码，同时可以在GoDocs中查看公开的结构和功能。



## 二、背景

### <a class="reference-link" name="2.1%20%E7%B3%BB%E7%BB%9F%E8%B0%83%E7%94%A8%E4%B8%8ECGo"></a>2.1 系统调用与CGo

在Go中，与Windows API交互的主要方法有两种————系统调用或CGo。系统调用要求从系统中识别并加载DLL，找到要调用的导出函数。而在CGo中，我们可以编写C语言来执行这些“繁重的工作”，然后在Go中调用。例如，下面的两种方法可以在Golang中弹出Windows消息框。首先，使用CGo在C中编写函数，然后从Go中调用：

```
package main

/*
#include &lt;windows.h&gt;

void SayHello() `{`
    MessageBox(0, "Hello World", "Helo", MB_OK);
`}`
*/
import "C"

func main() `{`
    C.SayHello()
`}`
```

这种方法的问题之一在于，CGo需要一个GNU编译器，这也就是说，开箱即用的运行方式将无法正常工作。我们需要使用诸如msys2之类的东西来构建系统。Go包含头文件的位置也非常特殊，我们在导出所需的更高级的东西时，遇到了一些错误。另外存在的一个问题，就是我们需要编写C语言。<br>
调用Windows API的另一种方法，是使用DLL导出的函数。例如：

```
// +build windows
package main

import (
    "fmt"
    "syscall"
    "unsafe"
)

func main() `{`
    user32 := syscall.MustLoadDLL("user32.dll")
    messageBox := user32.MustFindProc("MessageBoxW")
    text, _ := syscall.UTF16PtrFromString("Hello World!")
    caption, _ := syscall.UTF16PtrFromString("Hello")
    MB_OK := 0
    ret, _, _ := messageBox.Call(
        uintptr(0),
        uintptr(unsafe.Pointer(text)),
        uintptr(unsafe.Pointer(caption)),
        uintptr(MB_OK))
    fmt.Printf("Returned: %dn", ret)
`}`
```

在这个示例中，需要大量的Go语言代码，但是构建起来也要容易得多，在Windows上可以执行简单地Go构建。从原理上，它会找到user32.dll和导出的MessageBoxW函数，然后使用必要的指针对该函数进行syscall。这一过程中，需要将字符串转换为UTF16指针，并使用unsafe.Pointer。我知道，这看起来确实非常混乱，并且令人困惑，但IMO是一种比较好的实现方式。接下来，我们尝试去写没有C以来的“单纯版”Go。<br>
关于从Go调用Windows API并使用unsafe的相关知识，可以参考这篇文章：<br>[https://medium.com/jettech/breaking-all-the-rules-using-go-to-call-windows-api-2cbfd8c79724](https://medium.com/jettech/breaking-all-the-rules-using-go-to-call-windows-api-2cbfd8c79724)

### <a class="reference-link" name="2.2%20%E4%BB%8E%E9%9D%9E%E6%89%98%E7%AE%A1%E4%BB%A3%E7%A0%81%E8%B0%83%E7%94%A8%E6%89%98%E7%AE%A1%E4%BB%A3%E7%A0%81"></a>2.2 从非托管代码调用托管代码

首先，我们需要了解“托管”与“非托管”代码的概念。其中，“非托管”代码通常是指经过编译和链接的低级C/C++代码，并且在执行指令时有效。“托管”代码是指写入目标.NET的代码，如果没有CLR，这些代码将不会起作用。从这个概念上，我们可以对其进行一下翻译。例如，我们不能在未安装Python、未调用解释器的情况下运行Python代码。并且，我们不能仅运行.NET代码而不调用CLR。<br>
.NET使用公共语言运行库（CLR）来“解释”代码。我们对其仍然不是非常了解，但从概念上来说，我将其视为Microsoft的Java虚拟机（JVM）版本。在编写Java时，它会编译为中间字节码，并且需要JVM才能执行。同样，当我们编写.NET时，它会编译为中间语言，并且需要CLR来执行。最后，我们需要创建或将其附加到CLR，才能执行.NET程序集。<br>
了解这些基本术语和概念会很有帮助。这样一来，我们就可以搜索“托管CLR”和“从非托管运行托管代码”之类的事情，并获得比较好的结果。<br>
其中，有两个搜索结果是从C/C++运行托管代码的示例：<br>[https://gist.github.com/xpn/e95a62c6afcf06ede52568fcd8187cc2](https://gist.github.com/xpn/e95a62c6afcf06ede52568fcd8187cc2)<br>[https://www.mode19.net/posts/clrhostingright/](https://www.mode19.net/posts/clrhostingright/)<br>
上面的这两篇文章中，都包含如何从C启动.NET程序集的示例。由于我们已经了解如何通过调用Windows API在Go中打开消息框，因此我认为自己具备在Go中重新创建其代码所需的全部技术。这一过程能有多难呢？就像是根据左边的圆圈来画出一只猫头鹰一样：

[![](https://p2.ssl.qhimg.com/t01d18ff902e79f42dd.jpg)](https://p2.ssl.qhimg.com/t01d18ff902e79f42dd.jpg)



## 三、从磁盘加载托管DLL

我开始尝试使用系统调用，将上述找到的两个示例代码全部使用Go语言来重写。Xpn的代码只有70行，经过反复阅读后，我总结了这段代码中必要的基础步骤：<br>
1、创建一个“MetaHost”实例；<br>
2、枚举运行时；<br>
3、获取该运行时的“接口”；<br>
4、“启动”界面；<br>
5、调用“ExecuteInDefaultAppDomain”并传入DLL和参数。<br>
我选择在Visual Studio中打开xpn的代码，这样一来，就可以右键单击函数/常量和“查看定义”以查看它们的来源。

### <a class="reference-link" name="3.1%20%E8%B0%83%E7%94%A8CLRCreateInstance"></a>3.1 调用CLRCreateInstance

整个过程的第一步，是通过调用本机函数来创建MetaHost实例。在示例代码中，类似如下：

```
CLRCreateInstance(CLSID_CLRMetaHost, IID_ICLRMetaHost, (LPVOID*)&amp;metaHost)
```

根据该函数对应的MSDN文档，我们了解到它是MSCorEE.dll的一部分。因此，要加载到Go中：

```
var (
    modMSCoree            = syscall.NewLazyDLL("mscoree.dll")
    procCLRCreateInstance = modMSCoree.NewProc("CLRCreateInstance")
)
```

其中包含3个参数——clsid、riiid和ppInterface。前两个参数是指向GUID的指针，第三个参数是指向将指向创建的新MetaInstance的指针的指针。那么，如何在Go中创建GUID呢？首先，我们在Visual Studio中右键单击以查看常量CLSID_CLRMetaHost的定义。它在metahost.h中定义，如下所示：<br>
EXTERN_GUID(CLSID_CLRMetaHost, 0x9280188d, 0xe8e, 0x4867, 0xb3, 0xc, 0x7f, 0xa8, 0x38, 0x84, 0xe8, 0xde);<br>
这一过程花费了我的一些时间。首先，我在尝试将GUID转换为字符串的过程中遇到了一些困难。但是，后来我发现syscall包已经包含GUID类型。幸运的是，metahost.h定义与结构预期的参数完全匹配，我可以通过复制以下内容在Go中重新创建GUID：<br>
import “golang.org/x/sys/windows”<br>
CLSID_CLRMetaHost = windows.GUID`{`0x9280188d, 0xe8e, 0x4867, [8]byte`{`0xb3, 0xc, 0x7f, 0xa8, 0x38, 0x84, 0xe8, 0xde`}``}`<br>
为了获得指针参数，我使用了一个空的uintptr变量。对CLRCreateInstance函数的最终调用如下所示：

```
var pMetaHost uintptr
hr, _, _ := procCLRCreateInstance.Call(
  uintptr(unsafe.Pointer(&amp;CLSID_CLRMetaHost)),
  uintptr(unsafe.Pointer(&amp;IID_ICLRMetaHost)),
  uintptr(unsafe.Pointer(&amp;pMetaHost))
)
checkOK(hr, "procCLRCreateInstance")
```

我传入了指向GUID结构的不安全指针以及指向null指针的不安全指针。如果函数成功返回，那么就应该会使用新CLR MetaHost实例的实际内存地址填充pMetaHost的值。<br>
该函数返回一个HRESULT。如果该值等于0，则表明这一过程成功执行。因此，我编写了一个辅助函数，将hr值与0进行比较，如果比较失败则产生崩溃（Panic）：

```
func checkOK(hr uintptr, caller string) `{`
    if hr != 0x0 `{`
        log.Fatalf("%s returned 0x%08x", caller, hr)
    `}`
`}`
```

这非常有效。我现在可以看到，pMetaHost的值填充了一个地址。

### <a class="reference-link" name="3.2%20%E5%9C%A8Go%E4%B8%AD%E9%87%8D%E6%96%B0%E5%88%9B%E5%BB%BA%E6%8E%A5%E5%8F%A3"></a>3.2 在Go中重新创建接口

这就是整个过程中最困难的地方。从DLL调用导出的函数相当简单，但是现在我们需要处理指向接口的指针，这些接口指向其他函数。我知道，链中的下一步是调用metaHost-&gt;EnumerateInstalledRuntimes，但现在我们仅仅拥有一个指向内存中metaHost对象的指针。<br>
我知道，在C/C++中，如果内存布局全部匹配，我可以“投射”一个指向对象的指针。幸运的是，如果在Go中使用不安全的包，也是如此。如果我们在Go中国呢将ICLRMetaHost接口重新创建为结构，就可以将其指针进行转换。我们再次右键单击，并在ICLRMetaHost接口上单击“Viewing Definition”，我们就可以在metahost.c中查看到其定义。它似乎定义了两次，一次是使用C++，一次是使用C，我在这里只关注C语言的接口：

[![](https://p3.ssl.qhimg.com/t0155f9cefb88235bc3.png)](https://p3.ssl.qhimg.com/t0155f9cefb88235bc3.png)

看起来，它实际上定义了两个接口：ICLRMetaHostVtbl和ICLRMetaHost。我假设STDMETHODCALLTYPE只是一个函数的指针，所以Go中的uintptr会比较合适。我在前面引用的文章中，在“C结构与Go结构”这一部分，最后在Go中进行了定义：

```
//ICLRMetaHost Interface from metahost.h
type ICLRMetaHost struct `{`
    vtbl *ICLRMetaHostVtbl
`}`

type ICLRMetaHostVtbl struct `{`
    QueryInterface                   uintptr
    AddRef                           uintptr
    Release                          uintptr
    GetRuntime                       uintptr
    GetVersionFromFile               uintptr
    EnumerateInstalledRuntimes       uintptr
    EnumerateLoadedRuntimes          uintptr
    RequestRuntimeLoadedNotification uintptr
    QueryLegacyV2RuntimeBinding      uintptr
    ExitProcess                      uintptr
`}`

func NewICLRMetaHostFromPtr(ppv uintptr) *ICLRMetaHost `{`
    return (*ICLRMetaHost)(unsafe.Pointer(ppv))
`}`
```

NewICLRMetaHostFromPtr函数采用从CLRCreateInstance获得的指针，并返回一个ICLRMetaHost对象。这一切似乎工作正常。我在对象上执行了fmt.Printf(“+%v”, metaHost)，可以看到每个结构字段都填充有一个指针，因此看起来好像有效。<br>
现在，要调用EnumerateInstalledRuntimes这样的函数，我应该可以将syscall.Syscall与存储在ICLRMetaHost.vtbl.EnumerateInstalledRuntimes中的函数地址一起使用。

### <a class="reference-link" name="3.3%20%E8%B0%83%E7%94%A8%E6%8E%A5%E5%8F%A3%E6%96%B9%E6%B3%95"></a>3.3 调用接口方法

EnumerateInstalledRuntimes方法中仅包含一个参数：指向返回值的指针的指针。因此，我们实现了以下的调用

```
var pInstalledRuntimes uintptr
hr, _, _ := syscall.Syscall(
  metaHost.vtbl.EnumerateInstalledRuntimes,
  1,
  uintptr(unsafe.Pointer(&amp;pInstalledRuntimes)),
  0,
  0,
  0
)
checkOK(hr, "metaHost.EnumerateInstalledRuntimes")
```

注意，其中的0是必须的，因为syscall.Syscall需要6个参数，但是仅仅会使用必要的参数。<br>
然而，并没有起作用。无论我尝试修改哪里，最后都没有得到一个有效的返回值（也就是0）。在这一点上，我陷入了迷茫，似乎不清楚应该如何进行调整，因此我暂时考虑放弃这个思路。但直到有一天晚上，我在查找关于“vtbl”和“IUnknown”的信息时，偶然发现了一个思路。<br>
事实证明，我不能仅仅将这些函数视为本地函数。实际上，这些是COM对象的方法。我在Stack Overflow上发现了一个关于如何在Golang中实现COM方法的回答：[https://stackoverflow.com/questions/37781676/how-to-use-com-component-object-model-in-golang](https://stackoverflow.com/questions/37781676/how-to-use-com-component-object-model-in-golang)<br>
显然，在调用COM方法时，我必须确保实现了AddRef和Release，并将指向对象本身的指针作为第一个参数传递。我基本上从那个问题中得到了答案，并且借鉴了其中的代码。最后，我得到了EnumerateInstalledRuntimes函数的预期返回值：

```
func (obj *ICLRMetaHost) EnumerateInstalledRuntimes(pInstalledRuntimes *uintptr) uintptr `{`
    ret, _, _ := syscall.Syscall(
      obj.vtbl.EnumerateInstalledRuntimes,
      2,
      uintptr(unsafe.Pointer(obj)),
      uintptr(unsafe.Pointer(pInstalledRuntimes)),
      0)
    return ret
`}`
```

### <a class="reference-link" name="3.4%20%E5%AE%9E%E6%96%BD%E5%85%B6%E4%BB%96%E6%8E%A5%E5%8F%A3"></a>3.4 实施其他接口

之前的一个回答，成为了解决这一系列问题的关键。现在，我们知道如何实现在Visual Studio头文件中找到的C样式的接口，并调用所需的函数。下一步是实现IEnumUnknown接口，因为这就是EnumerateInstalledRuntimes所指向的。我们非常习惯将接口从头文件复制到带有Vim宏的Go语言中，并且这一过程只是复制粘贴了标准的函数实现。在这里，我们不必担心永远不会调用的函数，只要确保它们包含在结构定义中即可。<br>
在IEnumUnknown接口之后，我还需要metahost.h中的ICLRRuntimeInfo接口。<br>
为了将已安装的运行时版本枚举为字符串的形式，我们不得不对内存进行一些操作。GetVersionString实际上并没有返回字符串，而是将UTF16字符串写入内存中的位置。因此，在Go中，我分配了一个20字节的缓冲区数组，并将指向该指针的位置传递给该位置，以将字符串写入其中。然后，我将缓冲区数组转换为对Go友好的UTF16字符串。我们得到的一个经验是，始终确保将指针传递给数组的第一个元素，而不是数组本身。最终，枚举运行时的循环如下所示：

```
var rutimes []string
var pRuntimeInfo uintptr
var fetched = uint32(0)
var versionString string
versionStringBytes := make([]uint16, 20)
versionStringSize := uint32(len(versionStringBytes))
var runtimeInfo *ICLRRuntimeInfo
for `{`
    hr = installedRuntimes.Next(1, &amp;pRuntimeInfo, &amp;fetched)
    if hr != 0x0 `{`
        break
    `}`
    runtimeInfo = NewICLRRuntimeInfoFromPtr(pRuntimeInfo)
    if ret := runtimeInfo.GetVersionString(&amp;versionStringBytes[0], &amp;versionStringSize); ret != 0x0 `{`
        log.Fatalf("GetVersionString returned 0x%08x", ret)
    `}`
    versionString = syscall.UTF16ToString(versionStringBytes)
    runtimes = append(runtimes, versionString)
`}`
fmt.Printf("[+] Installed runtimes: %sn", runtimes)
```

令人惊讶的是，上述代码我一次编译就通过了。

### <a class="reference-link" name="3.5%20%E4%BB%8E%E7%A3%81%E7%9B%98%E4%B8%AD%E6%89%A7%E8%A1%8CDLL"></a>3.5 从磁盘中执行DLL

在这里，我将不会介绍我创建的所有其他接口，因为本质上我只是将xpn的代码进行了语言上的转译。我最终实现了：<br>
ICLRRuntimeInfo<br>
ICLRRuntimeHost<br>
IUnknown<br>
最后，我准备好尝试ICLRRuntimeHost的ExecuteInDefaultAppDomain方法实现。我编写了一个简单的C#程序进行测试：

```
using System;
using System.Windows.Forms;

namespace TestDLL
`{`
    public class HelloWorld
    `{`
        public static int SayHello(string foobar)
        `{`
            MessageBox.Show("Hello from a C# DLL!");
            return 0;
        `}`
    `}`
`}`
```

随后，我将其编译为DLL：csc -target:library -out:TestDLL.dll TestDLL.cs。然后在Go中，我将文件名、类型名称、方法名称和参数转换为UTF16字符串指针，并调用了该方法：

```
pDLLPath, _ := syscall.UTF16PtrFromString("TestDLL.dll")
pTypeName, _ := syscall.UTF16PtrFromString("TestDLL.HelloWorld")
pMethodName, _ := syscall.UTF16PtrFromString("SayHello")
pArgument, _ := syscall.UTF16PtrFromString("foobar")
var pReturnVal *uint16
hr = runtimeHost.ExecuteInDefaultAppDomain(
    pDLLPath,
    pTypeName,
    pMethodName,
    pArgument,
    pReturnVal
)
checkOK(hr, "runtimeHost.ExecuteInDefaultAppDomain")
fmt.Printf("[+] Assembly returned: 0x%xn", pReturnVal)
```

结果证明上述代码有效。

[![](https://p1.ssl.qhimg.com/t01db2209367dc941b0.png)](https://p1.ssl.qhimg.com/t01db2209367dc941b0.png)

在使其正常工作后，我对代码进行了一些整理，并添加了一些辅助函数。我们可以在这里看到完整的示例：DLLFromDisk.go<br>
我还添加了一个包装器函数，该函数基本上可以自动完成整个过程，我们可以使用以下命令对其进行调用：

```
ret, err := clr.ExecuteDLLFromDisk(
  "TestDLL.dll",
  "TestDLL.HelloWorld",
  "SayHello",
  "foobar")
```

但是，我真正想要的就是从内存中加载程序集。这需要磁盘上事先存在DLL，我们希望可以下载DLL，或将其嵌入Go二进制文件中并执行。我当时以为，最困难的部分已经完成，这个过程比较容易。但实际上，我错了。



## 四、从内存执行程序集

我最初的想法是，利用Go中的虚拟文件系统（例如vfs或packr2），并将DLL保留在内存中。当然，我很快就意识到这是不可能的，因为DLL的路径已经传递给本地函数，我们无法控制，并且该函数总是会在磁盘上执行查找。<br>
我还仔细阅读了ICLRRuntimeHost的MSDN文档，找不到任何有关从内存中加载或执行内容的引用。但是，我记得似乎有研究人员进行过这样的操作，因此我开始检索，找到有两个工具可以使用本地代码从内存中执行.NET程序集：<br>
1、Dount（ [https://github.com/TheWover/donut](https://github.com/TheWover/donut) ），特别是其中的rundotnet.cpp；<br>
2、GrayFrost（ [https://github.com/GrayKernel/GrayFrost](https://github.com/GrayKernel/GrayFrost) ），特别是其中的Runtimer.cpp。<br>
通过查看示例中的代码，我意识到这里必须使用CLR方法来实现内存执行。因此，我需要在Go中重写，并重新实现更多功能，特别是ICORRuntimeHost。<br>
新的高级执行流如下所示：<br>
1、创建一个MetaHost实例；<br>
2、枚举已经安装的运行时；<br>
3、获取RuntimeInfo到最新安装的版本；<br>
4、运行BindAsLegacyV2Runtime()；<br>
5、获取ICORRuntimeHost接口；<br>
6、从接口获取默认应用程序域；<br>
7、将程序集加载到应用程序域中；<br>
8、查找加载的程序集的入口点；<br>
9、调用入口点。<br>
这样的过程，比仅从磁盘运行DLL还要复杂得多。

### <a class="reference-link" name="4.1%20%E5%B0%86%E7%A8%8B%E5%BA%8F%E9%9B%86%E5%8A%A0%E8%BD%BD%E5%88%B0%E5%86%85%E5%AD%98%E4%B8%AD"></a>4.1 将程序集加载到内存中

在Go中实现ICORRuntimeHost和AppDomain之后，我意识到，需要查看Donut和GrayFrost的代码，以便在AppDomain中调用Load_3方法，字节码必须采用特定格式，也就是SafeArray。<br>
这是一个有趣的地方，我们需要弄清楚如何将Go中的字节数组转换为内存中的安全数组。首先，我基于OAld.h中的定义创建了一个Go结构：

```
type SafeArray struct `{`
    cDims      uint16
    fFeatures  uint16
    cbElements uint32
    cLocks     uint32
    pvData     uintptr
    rgsabound  [1]SafeArrayBound
`}`

type SafeArrayBound struct `{`
    cElements uint32
    lLbound   int32
`}`
```

在这里，我意识到我可以通过本地函数（SafeArrayCreate）创建SafeArray，然后使用原始内存副本将字节放在正确的位置。首先，创建SafeArray：

```
var rawBytes = []byte`{`0xaa....`}` // my executable loaded in a byte array
modOleAuto, err := syscall.LoadDLL("OleAut32.dll")
must(err)
procSafeArrayCreate, err := modOleAuto.FindProc("SafeArrayCreate")
must(err)

size := len(rawBytes)
sab := SafeArrayBound`{`
    cElements: uint32(size),
    lLbound:   0,
`}`
runtime.KeepAlive(sab)
vt := uint16(0x11) // VT_UI1
ret, _, _ := procSafeArrayCreate.Call(
    uintptr(vt),
    uintptr(1),
    uintptr(unsafe.Pointer(&amp;sab)))
sa := (*SafeArray)(unsafe.Pointer(ret))
```

实际上，我对其中的一些细节还不是太了解。实际上，我只是从Donut (0x11)复制了对应于VT_UI1的值，并且它起作用了。<br>
该过程返回一个指向创建的SafeArray的指针。现在，我们的实际数据（字节）需要复制到safeArray.pvData指向的内存中。我没有找到在本地Go中执行此操作的方法，因此，我从ntdll.dll导入并使用了RtlCopyMemory来执行原始内存复制：

```
modNtDll, err := syscall.LoadDLL("ntdll.dll")
must(err)
procRtlCopyMemory, err := modNtDll.FindProc("RtlCopyMemory")
must(err)

ret, _, err = procRtlCopyMemory.Call(
    sa.pvData,
    uintptr(unsafe.Pointer(&amp;rawBytes[0])),
    uintptr(size))
```

由于SafeArrayCreate根据cElements值（等于我们字节数组的大小）来分配内存，因此我们可以直接复制到内存中的这一点。出人意料的是，这个过程居然有效。<br>
我们最终将其包装在一个辅助函数CreateSafeArray中，该函数将接收一个字节数组，并返回指向内存中SafeArray的指针。

### <a class="reference-link" name="4.2%20%E6%9F%A5%E6%89%BE%E5%B9%B6%E8%B0%83%E7%94%A8%E5%85%A5%E5%8F%A3%E7%82%B9"></a>4.2 查找并调用入口点

创建SafeArray之后，可以使用Load_3方法将其加载到AppDomain中：

```
func (obj *AppDomain) Load_3(pRawAssembly uintptr, asmbly *uintptr) uintptr `{`
    ret, _, _ := syscall.Syscall(
        obj.vtbl.Load_3,
        3,
        uintptr(unsafe.Pointer(obj)),
        uintptr(unsafe.Pointer(pRawAssembly)),
        uintptr(unsafe.Pointer(asmbly)))
    return ret
`}`
```

这样一来，我们就拥有了一个指向Assembly对象的指针。接下来，我们需要在Go中实现Assembly接口。在Visual Studio（从mscorlib.tlh）中查看，看起来像是我们实现的任何其他接口：

[![](https://p5.ssl.qhimg.com/t0142aaa2290b4f526f.png)](https://p5.ssl.qhimg.com/t0142aaa2290b4f526f.png)

但是，在这里，不管我尝试什么，在调用get_EntryPoint和Invoke_3方法时，都会导致内存越界异常。这个问题，似乎难以解决。大概花费了连续6个晚上，我不断地反复阅读和重新编写代码，但还是无法弄清楚。<br>
最后，我开始使用调试器读取内存，并比较正在运行的C++程序和我编写的Go程序之间的十六进制转储中的不同，但仍然无法发现二者之间的区别。<br>
我开始在GitHub中，搜索其他正在执行Windows API调用的Go项目，并找到了James Hovious编写的w32。在阅读的过程中，我看到了他实现IDispatch的过程。我突然想到，Assembly的接口定义中提到了IDispatch。我在他的代码中，发现了vtbl结构中包含一些我没有使用的其他方法：

```
type pIDispatchVtbl struct `{`
    pQueryInterface   uintptr
    pAddRef           uintptr
    pRelease          uintptr
    pGetTypeInfoCount uintptr
    pGetTypeInfo      uintptr
    pGetIDsOfNames    uintptr
    pInvoke           uintptr
`}`
```

在这里，我还不清楚IDispatch具体是什么，但我突然意识到，如果我的结构定义中缺少这些功能，那么内存将无法正确排列。于是，我将它们添加到Assembly结构的最开始，然后一切就都开始正常工作了。<br>
在找到方法入口点并创建MethodInfo对象之后，最后一步仅使用Invoke_3方法调用该函数。该函数在mscorlib.tlh中定义为：

[![](https://p4.ssl.qhimg.com/t01fa74eb301bc03a8f.png)](https://p4.ssl.qhimg.com/t01fa74eb301bc03a8f.png)

当我看到这里，发现了OAldl.h中的VARIANT定义，心情更加沉重。UNION定义说明了所有不同类型的值，这是一个疯狂的结构。为了简单起见，我决定尝试实现将参数传递给方法，因此我仅使用null变量和null指针作为Invoke_3的参数。这也是Dount和GrayFrost所做的。我搜索了“variant”和“golang”，并在go-ole项目中找到了可以使用的一些实现。<br>
最终，我们再对其进行整合与调整：

```
safeArray, err := CreateSafeArray(exebytes)
must(err)
var pAssembly uintptr
hr = appDomain.Load_3(uintptr(unsafe.Pointer(&amp;safeArray)), &amp;pAssembly)
checkOK(hr)
assembly := NewAssemblyFromPtr(pAssembly)
var pEntryPointInfo uintptr
hr = assembly.GetEntryPoint(&amp;pEntryPointInfo)
checkOK(hr)
methodInfo := NewMethodInfoFromPtr(pEntryPointInfo)
var pRetCode uintptr
nullVariant := Variant`{`
    VT:  1,
    Val: uintptr(0),
`}`
hr = methodInfo.Invoke_3(
    nullVariant,
    uintptr(0),
    &amp;pRetCode)
checkOK(hr)
fmt.Printf("[+] Executable returned code %dn", pRetCode)
```

为了进行测试，我创建了一个Hello World C# EXE：

```
using System;

namespace TestExe
`{`
    class HelloWorld
    `{`
        static void Main()
        `{`
            Console.WriteLine("hello fom a c# exe!");
        `}`
    `}`
`}`
```

我使用csc TestExe.cs进行了构建，然后将其加载到Go中的字节数组中：

```
exebytes, err := ioutil.ReadFile("TestExe.exe")
must(err)
```

然后，从中创建了一个SafeArray。这样，一切就都准备就绪。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017784783c1c940e27.png)

最终，我们发现这是可以正常工作的！经过不断解决过程中遇到的困难，我们最终得到了可用的代码。<br>
大家可以在这里查看从内存加载EXE的完整示例：<br>[https://github.com/ropnop/go-clr/blob/master/examples/EXEfromMemory/EXEfromMemory.go](https://github.com/ropnop/go-clr/blob/master/examples/EXEfromMemory/EXEfromMemory.go)



## 五、总结

这是一次非常具有挑战性但又非常有意义的实验。从对CLR、COM和Go系统调用几乎一无所知，到能构建出很酷的一段代码，我们不断尝试解决问题，也在过程中不断遇到新的问题。<br>
希望通过发布上述代码，能帮助其他研究人员展示这一过程，并为构建定制化工具提供基础。我们希望提醒大家的是，如果遇到了某些困难，或者对某些地方不太了解，Google、GitHub和Stack Overflow都能提供非常有帮助的信息。<br>
期待看到大家对这项研究的后续利用。如果大家有任何疑问，欢迎和我联系。



## 六、参考文章

[1] [https://gist.github.com/Arno0x/386ebfebd78ee4f0cbbbb2a7c4405f74](https://gist.github.com/Arno0x/386ebfebd78ee4f0cbbbb2a7c4405f74)<br>
[2] [https://www.mode19.net/posts/clrhostingright/](https://www.mode19.net/posts/clrhostingright/)<br>
[3] [https://github.com/RickStrahl/wwDotnetBridge/pull/18/commits/307e70ac70c17be5744ce6cc0cd1b0a0ee947758](https://github.com/RickStrahl/wwDotnetBridge/pull/18/commits/307e70ac70c17be5744ce6cc0cd1b0a0ee947758)<br>
[4] [https://yizhang82.dev/calling-com-from-go](https://yizhang82.dev/calling-com-from-go)<br>
[5] [https://stackoverflow.com/questions/37781676/how-to-use-com-component-object-model-in-golang](https://stackoverflow.com/questions/37781676/how-to-use-com-component-object-model-in-golang)<br>
[6] [https://github.com/AllenDang/w32/blob/c92a5d7c8fed59d96a94905c1a4070fdb79478c9/typedef.go](https://github.com/AllenDang/w32/blob/c92a5d7c8fed59d96a94905c1a4070fdb79478c9/typedef.go)<br>
[7] [https://www.codeproject.com/Articles/607352/Injecting-NET-Assemblies-Into-Unmanaged-Processes](https://www.codeproject.com/Articles/607352/Injecting-NET-Assemblies-Into-Unmanaged-Processes)<br>
[8] [https://www.unknowncheats.me/forum/general-programming-and-reversing/332825-inject-net-dll-using-clr-hosting.html](https://www.unknowncheats.me/forum/general-programming-and-reversing/332825-inject-net-dll-using-clr-hosting.html)<br>
[9] [https://blog.xpnsec.com/rundll32-your-dotnet/](https://blog.xpnsec.com/rundll32-your-dotnet/)<br>
[10] [http://sbytestream.pythonanywhere.com/blog/clr-hosting](http://sbytestream.pythonanywhere.com/blog/clr-hosting)<br>
[11] [https://www.codeproject.com/Articles/416471/CLR-Hosting-Customizing-the-CLR](https://www.codeproject.com/Articles/416471/CLR-Hosting-Customizing-the-CLR)<br>
[12] [https://thewover.github.io/Introducing-Donut/](https://thewover.github.io/Introducing-Donut/)<br>
[13] [https://github.com/TheWover/donut/blob/9c07b2fde9ac489fffca409fbd7c2228c90c3373/loader/clr.h](https://github.com/TheWover/donut/blob/9c07b2fde9ac489fffca409fbd7c2228c90c3373/loader/clr.h)<br>
[14] [https://github.com/TheWover/donut/blob/9c07b2fde9ac489fffca409fbd7c2228c90c3373/loader/inmem_dotnet.c](https://github.com/TheWover/donut/blob/9c07b2fde9ac489fffca409fbd7c2228c90c3373/loader/inmem_dotnet.c)<br>
[15] [https://github.com/go-ole/go-ole/blob/master/idispatch.go#L5](https://github.com/go-ole/go-ole/blob/master/idispatch.go#L5)<br>
[16] [https://medium.com/jettech/breaking-all-the-rules-using-go-to-call-windows-api-2cbfd8c79724](https://medium.com/jettech/breaking-all-the-rules-using-go-to-call-windows-api-2cbfd8c79724)<br>
[17] [https://gist.github.com/xpn/e95a62c6afcf06ede52568fcd8187cc2](https://gist.github.com/xpn/e95a62c6afcf06ede52568fcd8187cc2)

> 原文链接: https://www.anquanke.com//post/id/183291 


# Frenchy shellcode分析


                                阅读量   
                                **205424**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：
                                <br>原文地址：[http://www.peppermalware.com/2019/07/analysis-of-frenchy-shellcode.html](http://www.peppermalware.com/2019/07/analysis-of-frenchy-shellcode.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01c9e26a56002a2528.png)](https://p3.ssl.qhimg.com/t01c9e26a56002a2528.png)



在这篇文章中，我分析了一个名为“Frenchy shellcode”的shellcode，因为它创建了互斥锁（其中一些版本有互斥锁）。 这个shellcode通过不同的packers加载了不同种类的恶意软件。 因此，我决定研究一下这个shellcode并在这里分享我的详细分析。 另外，我分享一个PoC，一个用于加载Frenchy shellcode的python脚本，使用它可以通过Hollow Process注入，替换notepad.exe实际执行的可执行部分，最终调用执行calc.exe。

我分析的大多数样本都装有一个基于AutoIt的packers解密并加载shellcode。Frenchy shellcode的第一个样本是Emotet，而packers是基于AutoIt的，我建议阅读这个twitter帖子([https://twitter.com/P3pperP0tts/status/1135976656751996928?s=20](https://twitter.com/P3pperP0tts/status/1135976656751996928?s=20)) 。过了一段时间，有另一名安全研究员分析了加载Frenchy shellcode的混淆自动脚本的变体。这个变体加载了Formbook Stealer。之后，在我的研究中，我通过在Cape Sandbox中搜索字符串“frenchy_shellcode_003” 发现了另一个样本 ，而该样本的packers是基于.Net的。

相关参考资料见最后一部分。



## 1 Packers

在本文的研究中，我不会过多的分析Frenchy shellcode的不同的packers，只会稍微提一下相应的注意事项。

### <a class="reference-link" name="1.1%20%E5%9F%BA%E4%BA%8EAutoIt%E7%9A%84Packer"></a>1.1 基于AutoIt的Packer

这个packer执行一个高度混淆的自动脚本，解密并加载Frenchy shellcode。 以下是这些脚本的几个例子：

frenchy_shellcode_01： [https://pastebin.com/raw/xsUqCdRj](https://pastebin.com/raw/xsUqCdRj)<br>
frenchy_shellcode_002： [https://pastebin.com/raw/Knk2iJPF](https://pastebin.com/raw/Knk2iJPF)

我推荐阅读这篇关于加载Frenchy shellcode的AutoIt脚本的帖子。([https://tccontre.blogspot.com/2019/07/autoit-compiled-formbook-malware.html](https://tccontre.blogspot.com/2019/07/autoit-compiled-formbook-malware.html))

### <a class="reference-link" name="1.2%20%E5%9F%BA%E4%BA%8E.Net%E7%9A%84Packer"></a>1.2 基于.Net的Packer

对于样本 21c1d45977877018568e8073c3Acf7c5，它的packer是.Net。 要检查.Net packer 否正在加载Frenchy shellcode，我们在CreateMutexW上设置了一个bp，我们等待其创建frenchy_shellcode_03互斥锁：

[![](https://p1.ssl.qhimg.com/t01b3bc322f02caeedc.png)](https://p1.ssl.qhimg.com/t01b3bc322f02caeedc.png)

现在我们知道当前线程正在执行Frenchy shellcode，所以我们显示调用堆栈来检查调用Frenchy shellcode的线程是否来自.Net：

[![](https://p2.ssl.qhimg.com/t010e015df784efb3fb.png)](https://p2.ssl.qhimg.com/t010e015df784efb3fb.png)



## 2 Frenchy Shellcode

### <a class="reference-link" name="2.1%20Frenchy%20Shellcode%20V3"></a>2.1 Frenchy Shellcode V3

我把重点放在了我从样本 21c1d45977877018568e8073c3Acf7c5 获得的v3 shellcode上 （可以从这里下载[https://www.hybrid-analysis.com/sample/0c9da7a0e3d3b2a6345bf69a22f577855f476d645cb71cd8a18123787e75a75a/](https://www.hybrid-analysis.com/sample/0c9da7a0e3d3b2a6345bf69a22f577855f476d645cb71cd8a18123787e75a75a/) ）。

这个shellcode的主要目的是通过使用Hollow Process注入方法将PE注入新进程。

**<a class="reference-link" name="2.1.1%20EP%E5%92%8C%E5%8F%82%E6%95%B0"></a>2.1.1 EP和参数**

Shellcode的入口点位于偏移0处，shellcode跳转到main函数：

[![](https://p5.ssl.qhimg.com/t019250b80aac65c8b8.png)](https://p5.ssl.qhimg.com/t019250b80aac65c8b8.png)

shellcode的第一个参数是用于被注入hollow进程的应用程序exe的路径， 第二个参数是要注入的内容（PE）

<a class="reference-link" name="2.1.2%20%E9%87%8D%E5%A4%8D%E7%9A%84%E7%B3%BB%E7%BB%9F%E5%BA%93"></a>**2.1.2 重复的系统库**

shellcode加载每一个它要使用的系统库：

[![](https://p3.ssl.qhimg.com/t01d0f6b3e1e308006e.png)](https://p3.ssl.qhimg.com/t01d0f6b3e1e308006e.png)

如果我们枚举地址空间的区域，我们可以检查其中是否有一些重复的dll：

[![](https://p2.ssl.qhimg.com/t01eb669377d5f49da3.png)](https://p2.ssl.qhimg.com/t01eb669377d5f49da3.png)

该操作可能会使shellcode更难调试， API钩子将不起作用（例如由cuckoo框架插入的钩子）。 如果在通常由恶意软件（CreateProcessW，WriteProcessMemory，SetThreadContext等等）执行的公共API上设置断点以捕获此时的恶意软件执行，则它将无法工作，因为你需要在重复的位置设置断点dll文件。

**<a class="reference-link" name="2.1.3%20%E4%BD%BF%E7%94%A8%E7%9A%84API"></a>2.1.3 使用的API**

shellcode获取指向许多API的指针，但它只使用它们的一个子集。 我觉得这是一个可以高度自定义的shellcode，它总是加载所有的API指针，但根据配置和它添加到shellcode的特定版本的代码，将使用一些API指针，其他指针不会使用。

以下是shellcode加载的API的完整列表：

```
BeginPaint
CoCreateInstance
CoInitializeEx
CreateMutexW
CreateProcessW
CreateWindowExW
CryptAcquireContextW
CryptCreateHash
CryptDecrypt
CryptDeriveKey
CryptDestroyHash
CryptDestroyKey
CryptHashData
CryptReleaseContext
DefWindowProcW
EndPaint
ExpandEnvironmentStringsW
FillRect
FindResourceW
FreeResource
GetModuleFileNameA
GetProcAddress_
GetSystemInfo
IsWow64Process
LdrGetProcedureAddress
LdrLoadDll
LoadLibraryA
LoadResource
LockResource
MessageBoxA
NtAdjustPrivilegesToken
NtAllocateVirtualMemory
NtClose
NtContinue
NtCreateFile
NtCreateMutant
NtCreateSection
NtCreateThreadEx
NtCreateUserProcess
NtDelayExecution
NtEnumerateKey
NtFreeVirtualMemory
NtGetContextThread
NtMapViewOfSection
NtOpenFile
NtOpenKey
NtOpenMutant
NtOpenProcess
NtOpenSection
NtProtectVirtualMemory
NtQueryInformationFile
NtQueryInformationProcess
NtQuerySection
NtQuerySystemInformation
NtQueryValueKey
NtReadFile
NtReadVirtualMemory
NtResumeThread
NtSetContextThread
NtSetValueKey
NtTerminateProcess
NtWriteFile
NtWriteVirtualMemory
PostQuitMessage
RegisterClassW
RtlCreateProcessParameters
RtlCreateUserProcess
RtlCreateUserThread
RtlFormatCurrentUserKeyPath
RtlSetCurrentTransaction
RtlZeroMemory
ShowWindow
SizeofResource
TerminateProcess
ZwCreateTransaction
ZwRollbackTransaction
ZwUnmapViewOfSection
lstrlenW
mbstowcs
memcpy
memset
strlen
wcscat
wcscmp
wcscpy
wcslen
wcstombs
```

有时shellcode会获取指向最初加载的dll上的API的指针。 例如，样本中的cryptoapi库，如下图所示。 我想这是因为当通过dll的辅助副本调用它们时它们不能正常工作。

[![](https://p5.ssl.qhimg.com/t01cf665eabe0b5f8d6.png)](https://p5.ssl.qhimg.com/t01cf665eabe0b5f8d6.png)

<a class="reference-link" name="2.1.4%20Process%20Hollowing"></a>**2.1.4 Process Hollowing**

恶意软件根据给定的路径参数创建新的挂起进程（路径为给定的可执行文件），然后使用Hollow Process注入方法将给定的PE注入该进程的地址空间，替换其实际执行的可执行部分，它使用一组本机API来执行此操作。

在下图中，我们可以看到恶意软件如何创建新进程并取消进程与其自身主模块的映射。 此外，它通过调用NtCreateSection + NtMapViewOfSection来映射要注入的PE（以获取此PE的映射副本）：

[![](https://p2.ssl.qhimg.com/t014294ebcb906cb483.png)](https://p2.ssl.qhimg.com/t014294ebcb906cb483.png)

一旦取消进程与其自身主模块的映射后，我们可以进行Hollow Process注入，获得要注入的PE的映射视图后，它就会在目标进程地址空间中创建一个新部分，以复制要在其中注入的PE。 它将使用NtCreateSection + NtMapViewOfSection + NtWriteProcessMemory来执行此操作：

[![](https://p5.ssl.qhimg.com/t01be37e37b764d19e2.png)](https://p5.ssl.qhimg.com/t01be37e37b764d19e2.png)

最后，它更改注入进程的主线程的上下文（即修改该进程的实际执行部分代码），以设置EIP =注入代码的起始地址，并恢复线程，到此注入成功。

### <a class="reference-link" name="2.2%20%E5%BA%94%E7%94%A8Frenchy%20Shellcode"></a>2.2 应用Frenchy Shellcode

说实话，我认为这个shellcode写得很好，它运行正常。 我决定写一个小的PoC，一个加载并调用它的python脚本，将notepad.exe作为被hollow注入进程，calc.exe的内容作为被注入的内容，完成操作后，我们将可以看到执行notepad.exe实际出来的应用程序却是计算器。

[![](https://p1.ssl.qhimg.com/t01dc734ab512243240.png)](https://p1.ssl.qhimg.com/t01dc734ab512243240.png)

在这里你可以找到PoC和Frenchy shellcode v3：

[https://github.com/p3pperp0tts/PoC_FrenchyShellcode](https://github.com/p3pperp0tts/PoC_FrenchyShellcode)

```
from ctypes import *
import struct

f = open("frenchyshellcode.bin", "rb")
frenchy = f.read()
f.close()
f = open("c:\windows\system32\calc.exe", "rb")
calc = f.read()
f.close()
hollowpath = "c:\windows\notepad.exex00"
#to test, full shellcode = frenchy + arguments for frenchy + code to jmp
lenshellcode = len(frenchy) + len(calc) + len(hollowpath) + len("x68x00x00x00x00x68x78x56x34x12x68x78x56x34x12x68x78x56x34x12xc3")
ptr = windll.kernel32.VirtualAlloc(None, lenshellcode, 0x3000, 0x40)
shellcode = frenchy
shellcode += calc
shellcode += hollowpath
shellcode += "x68" + struct.pack("&lt;L", ptr + len(frenchy)) #push path to process to hollow
shellcode += "x68" + struct.pack("&lt;L", ptr + len(frenchy)+len(calc)) #push address of pe to inject
shellcode += "x68x00x00x00x00" #fake ret addr
shellcode += "x68" + struct.pack("&lt;L", ptr) #push address of frenchy shellcode entry point
shellcode += "xc3" #jmp to frenchy
hproc = windll.kernel32.OpenProcess(0x1F0FFF,False,windll.kernel32.GetCurrentProcessId())
windll.kernel32.WriteProcessMemory(hproc, ptr, shellcode, len(shellcode), byref(c_int(0)))
windll.kernel32.CreateThread(0,0,ptr+len(frenchy)+len(calc)+len(hollowpath),0,0,0)
windll.kernel32.WaitForSingleObject(c_int(-1), c_int(-1))
```



## 3. Frenchy是谁

我尝试通过一些社工方法找到该shellcode的作者，hackforums中的一个用户值得我们怀疑，如下图所示

[![](https://p0.ssl.qhimg.com/t01a703961cc25a5da4.png)](https://p0.ssl.qhimg.com/t01a703961cc25a5da4.png)

[![](https://p0.ssl.qhimg.com/t010f27bfca587468d6.png)](https://p0.ssl.qhimg.com/t010f27bfca587468d6.png)

[![](https://p3.ssl.qhimg.com/t01da71fc8d3c4a449a.png)](https://p3.ssl.qhimg.com/t01da71fc8d3c4a449a.png)



## 相关资料

原始样本：<br>
Frenchy shellcode v1 + autoit<br>
packer： 0a1340bb124cd0d79fa19a09c821a049（Avemaria）<br>
Frenchy shellcode v1 + autoit<br>
packer： d009bfed001586db95623e2896fb93aa<br>
Frenchy shellcode v2 + autoit<br>
packer： 20de5694d7afa40cf8f0c88c86d22b1d（Formbook）<br>
Frenchy shellcode v3 + .Net<br>
packer： 21c1d45977877018568e8073c3Acf7c5（Netwire）

从样本中提取出的shellcodes：<br>
Frenchy shellcode v1 at [https://www.hybrid-analysis.com/sample/ba7e312ffc81f70a1ff7e1127af877cc098963cc89b3270b1fb86f50c4129c2f/](https://www.hybrid-analysis.com/sample/ba7e312ffc81f70a1ff7e1127af877cc098963cc89b3270b1fb86f50c4129c2f/)<br>
Frenchy shellcode v2 at [https://www.hybrid-analysis.com/sample/21223f0e90f19c65bee2ab88ded6d72080d99e6a3c29853e8c61147c35cdf396/](https://www.hybrid-analysis.com/sample/21223f0e90f19c65bee2ab88ded6d72080d99e6a3c29853e8c61147c35cdf396/)<br>
Frenchy shellcode v3 at [https://www.hybrid-analysis.com/sample/0c9da7a0e3d3b2a6345bf69a22f577855f476d645cb71cd8a18123787e75a75a/](https://www.hybrid-analysis.com/sample/0c9da7a0e3d3b2a6345bf69a22f577855f476d645cb71cd8a18123787e75a75a/)

相关链接：<br>[https://tccontre.blogspot.com/2019/07/autoit-compiled-formbook-malware.html](https://tccontre.blogspot.com/2019/07/autoit-compiled-formbook-malware.html) （推荐阅读）<br>[https://twitter.com/P3pperP0tts/status/1135976656751996928?s=20](https://twitter.com/P3pperP0tts/status/1135976656751996928?s=20)<br>[https://twitter.com/JayTHL/status/1146482606185308160?s=20](https://twitter.com/JayTHL/status/1146482606185308160?s=20)<br>[https://twitter.com/James_inthe_box/status/1148966237684133888?s=20](https://twitter.com/James_inthe_box/status/1148966237684133888?s=20)<br>[https://cape.contextis.com/analysis/85189/](https://cape.contextis.com/analysis/85189/)<br>[https://twitter.com/James_inthe_box/status/1146527056567472128?s=20](https://twitter.com/James_inthe_box/status/1146527056567472128?s=20)

> 原文链接: https://www.anquanke.com//post/id/86638 


# 【技术分享】如何使用windbg调试javascript


                                阅读量   
                                **95106**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：talosintelligence.com
                                <br>原文地址：[http://blog.talosintelligence.com/2017/08/windbg-and-javascript-analysis.html](http://blog.talosintelligence.com/2017/08/windbg-and-javascript-analysis.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01900b8f753ce0cddf.jpg)](https://p5.ssl.qhimg.com/t01900b8f753ce0cddf.jpg)

译者：[我来学英语](http://bobao.360.cn/member/contribute?uid=1264882569)

预估稿费：170RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**介绍**

****

由于javascript具有强大、可用性高，很少被禁用的特点。javascript经常被恶意软件作者用来执行恶意代码。我们[之前的文章](http://blog.talosintelligence.com/2017/07/unravelling-net-with-help-of-windbg.html)介绍了如何使用windbg调试.net程序吸引了很多人的关注因此也有了这篇文章如何使用windbg来调试js文件。在这篇文章中我们会介绍如何使用64位版本的wscript.exe来分析javascript代码。强烈建议你在阅读本篇文章之前先阅读我们[之前的文章](http://blog.talosintelligence.com/2017/07/unravelling-net-with-help-of-windbg.html)。

<br>

**Windows系统载入对象**

****

Javascript经常需要载入外部对象目的是获得windows系统默认不具备的额外特性。可以使用 ActiveXObject()

API用来加载activex对象或者WScript.CreateObject() API用来加载COM组件。这两种API的机制是相同的通过加载外部库来获得新的对象。举两个例子

```
new ActiveXObject("Shell.Application");
WScript.CreateObject("Wscript.Shell");
```

首先你需要理解这两个对象所加载的库。这些信息存储在注册表当中。首先我们需要通过查看注册表项HKEY_CLASSES_ROOTOBJECT_NAMECLSID获得对象名的CLSID



[![](https://p4.ssl.qhimg.com/t01fe9ce45a1e23ac4f.png)](https://p4.ssl.qhimg.com/t01fe9ce45a1e23ac4f.png)

通过这张图片我们可以看到CLSID是 `{`13709620-C279-11CE-A49E-444553540000`}`。通过这条信息我们可以进一步获得 HKEY_CLASSES_ROOTCLSID`{`THE_CLSID`}`处的信息。可以看到 Shell.Application对象位于shell32.dll。有了这些信息我们就可以开始使用windbg来分析对象的加载和执行了。

<br>

**Windbg分析**

****

分析javascript的执行是通过调试wscript.exe来进行的。可以通过以下命令来执行

```
"C:Program Files (x86)Windows Kits10Debuggersx64windbg.exe"
C:WindowsSystem32wscript.exe c:UsersUserto_be_analysed.js
```

分析步骤一般是相同的

1 当目标库载入时下断点

2 识别想要分析的方法并下断点

3 获得方法的参数

**案例学习#1 activex对象**

考虑如下代码



```
var oShell = new ActiveXObject("Shell.Application");
var commandtoRun = "calc.exe";
oShell.ShellExecute(commandtoRun,"","","","1");
```

第一步是找出Shell.Application库在注册表中的位置

```
c:Usersuser&gt; script.py Shell.Application
Object Name: Shell.Application
CLSID: `{`13709620-C279-11CE-A49E-444553540000`}`
Description: Shell Automation Service
dll: %SystemRoot%system32shell32.dll
```

很明显我们需要分析shell32.dll。下一步执行脚本并且在库加载时下断点

```
0:000&gt; sxe ld shell32 ; g
ModLoad: 00007fff`c6af0000 00007fff`c7f27000   C:WINDOWSSystem32SHELL32.dll
ntdll!NtMapViewOfSection+0x14:
00007fff`c8e658a4 c3              ret
The next step is to identify the ShellExecute function:
0:000&gt; x shell32!ShellExecute
```

不幸的是在javascript和加载的库中没有找到同名方法。但是我们可以使用正则表达式进行搜索

```
0:000&gt; x shell32!ShellExecute*
00007fff`c6b13dd0 SHELL32!ShellExecuteExW (void)
00007fff`c6b13e44 SHELL32!ShellExecuteNormal (void)
00007fff`c6cb1630 SHELL32!ShellExecuteExA (&lt;no parameter info&gt;)
00007fff`c6fa8d58 SHELL32!ShellExecuteRegApp (&lt;no parameter info&gt;)
00007fff`c6bef560 SHELL32!ShellExecuteW (&lt;no parameter info&gt;)
00007fff`c6cb15a0 SHELL32!ShellExecuteA (&lt;no parameter info&gt;)
00007fff`c6fa9058 SHELL32!ShellExecuteRunApp (&lt;no parameter info&gt;)
```

在这个案例中我们可以在ShellExecuteNormal上下断点

```
0:000&gt; bp shell32!ShellExecuteNormal
0:000&gt; g
Breakpoint 0 hit
SHELL32!ShellExecuteNormal:
00007fff`c6b13e44 48895c2408      mov     qword ptr [rsp+8],rbx ss:00000029`cb56c7a0=00000029cb56cc90
```

现在我们可以通过RCX寄存器获取参数了

```
0:000&gt; r $t1=poi(rcx+0x18);du $t1
000001ee`350d055c  "calc.exe"
```

你可能不太理解为什么偏移量是0x18。这是因为传递到ShellExecuteNormal()的参数是SHELLEXECUTEINFO结构的指针。微软的文档描述了这种情况这个数据结构本身位于偏移0x18处。



**案例学习#2 wscript shell对象**

考虑下面这段代码

```
var shell = WScript.CreateObject("Wscript.Shell");
var command = "calc.exe"; 
shell.Run(command, true, false);
```

按照前面所介绍的第一步是找到 Wscript.Shell所在的库

```
c:Usersuser&gt; script.py Wscript.Shell
Object Name: Wscript.Shell
CLSID: `{`72C24DD5-D70A-438B-8A42-98424B88AFB8`}`
Description: Windows Script Host Shell Object
dll: C:WindowsSystem32wshom.ocx
```

然后尝试找到函数名

```
0:000&gt; sxe ld wshom
0:000&gt; g
ModLoad: 00007fff`b5630000 00007fff`b5657000   C:WindowsSystem32wshom.ocx
ntdll!NtMapViewOfSection+0x14:
00007fff`c8e658a4 c3              ret
0:000&gt; x wshom!*Run*
00007fff`b5640930 wshom!CUnknown::InnerUnknown::`vftable' = &lt;no type information&gt;
00007fff`b563d530 wshom!CUnknown::InnerUnknown::QueryInterface (&lt;no parameter info&gt;)
00007fff`b5648084 wshom!_IMPORT_DESCRIPTOR_ScrRun = &lt;no type information&gt;
00007fff`b563d570 wshom!CUnknown::InnerUnknown::Release (&lt;no parameter info&gt;)
00007fff`b5643d30 wshom!ScrRun_NULL_THUNK_DATA = &lt;no type information&gt;
00007fff`b563bbb0 wshom!CWshShell::Run (&lt;no parameter info&gt;)
00007fff`b5631000 wshom!CUnknown::InnerUnknown::AddRef (&lt;no parameter info&gt;)
00007fff`b5644518 wshom!LIBID_IWshRuntimeLibrary = &lt;no type information&gt;)
```

这个方法是wshom!CWshShell::Run我们可以在这下断点来寻找参数

```
0:000&gt; bp wshom!CWshShell::Run
0:000&gt; g
Breakpoint 0 hit
wshom!CWshShell::Run:
00007fff`b563bbb0 48895c2408      mov     qword ptr [rsp+8],rbx ss:00000020`7ccfd520=0000013f3d650420
0:000&gt; du rdx
0000013f`3d65055c  "calc.exe"
```

与前一个案例不同这个案例中的参数是一个字符串而不是数据结构因此要获得这个参数我们不需要考虑偏移。

**案例学习#3 WScript XMLHTTP对象**

代码如下

```
var httpStream = WScript.CreateObject("MSXML2.XMLHTTP");
httpStream.open("GET", 'http://blog.talosintelligence.com');
httpStream.send();
```

可以看到MSXML2.XMLHTTP object对象在msxml3.dll中

```
c:Usersuser&gt; script.py MSXML2.XMLHTTP
Object Name: MSXML2.XMLHTTP
CLSID: `{`F6D90F16-9C73-11D3-B32E-00C04F990BB4`}`
Description: XML HTTP
dll: %SystemRoot%System32msxml3.dll
```

继续使用之前介绍的方法

```
0:000&gt; sxe ld msxml3
0:000&gt; g
ModLoad: 00007fff`8dc40000 00007fff`8de68000   C:WINDOWSSystem32msxml3.dll
ntdll!NtMapViewOfSection+0x14:
00007fff`c8e658a4 c3              ret
```

这一次我们使用正则表达式来对所有包含“open”关键字的API进行下断

```
0:000&gt; bm msxml3!*Open*
1: 00007fff`8dc43030 @!"msxml3!ErrorHelper::CHTMLWindow2::open"
breakpoint 1 redefined
1: 00007fff`8dc43030 @!"msxml3!FakeHTMLDoc::open"
2: 00007fff`8dd4c5fc @!"msxml3!HTTPStream::OpenRequest"
3: 00007fff`8dcaa407 @!"msxml3!_imp_load_CertOpenStore"
breakpoint 1 redefined
1: 00007fff`8dc43030 @!"msxml3!ErrorHelper::CHTMLWindow2::get_opener"
4: 00007fff`8dc48eb4 @!"msxml3!ContentModel::openGroup"
5: 00007fff`8dd4cb00 @!"msxml3!HTTPStream::deferedOpen"
breakpoint 1 redefined
1: 00007fff`8dc43030 @!"msxml3!ErrorHelper::CHTMLDocument2::open"
breakpoint 1 redefined
1: 00007fff`8dc43030 @!"msxml3!ErrorHelper::CHTMLWindow2::put_opener"
6: 00007fff`8dd4a050 @!"msxml3!URLMONRequest::open"
7: 00007fff`8dc8f4d0 @!"msxml3!FileStream::deferedOpen"
8: 00007fff`8dd34e80 @!"msxml3!XMLHttp::open"
9: 00007fff`8dc597e0 @!"msxml3!URLMONStream::deferedOpen"
10: 00007fff`8dc70ddc @!"msxml3!NamespaceMgr::popEntry"
11: 00007fff`8dcaa3bf @!"msxml3!_imp_load_WinHttpOpen"
12: 00007fff`8dcaa3e3 @!"msxml3!_imp_load_WinHttpOpenRequest"
13: 00007fff`8dd47340 @!"msxml3!HTTPRequest::open"
14: 00007fff`8dd47660 @!"msxml3!HTTPRequest::openWithCredentials"
15: 00007fff`8dc8f37c @!"msxml3!FileStream::open"
16: 00007fff`8dd4c128 @!"msxml3!URLStream::OpenPreloadResource"
17: 00007fff`8dd4b410 @!"msxml3!URLRequest::open"
0:000&gt; g
Breakpoint 8 hit
msxml3!XMLHttp::open:
00007fff`8dd34e80 488bc4          mov     rax,rsp
```

可以看到调用的API实际上是XMLHttp::open()因此可以进一步获得参数

```
0:000&gt; du rdx
00000173`311a0568  "GET"
0:000&gt; du r8
00000173`311a0578  "http://blog.talosintelligence.co"
00000173`311a05b8  "m"
```

**案例学习#4 Eval()方法**

Eval()方法经常被恶意软件作者用来执行代码。这个方法是javascript的原生方法不需要引入外部库。下面是一个使用eval()方法的例子

```
var test = "var oShell = new ActiveXObject("Shell.Application");
var commandtoRun = "notepad.exe"; 
oShell.ShellExecute(commandtoRun,"","","","1");"
eval(test) 
var encoded = "dmFyIG9TaGVsbCA9IG5ldyBBY3RpdmVYT2JqZWN0KCJTaGVsbC5BcHBsaWNhdGlvbiIpO3ZhciBjb21tYW5kdG9SdW4gPSAiY2FsYy5leGUiOyBvU2hlbGwuU2hlbGxFeGVjdXRlKGNvbW1hbmR0b1J1biwiIiwiIiwiIiwiMSIpOwo="
eval(Base64.decode(encoded))
```

这段脚本执行了两个不同的eval()调用。第一个直接通过字符串进行调用调用calc.exe即计算器第二个包含了一小段代码这段代码生成要执行的命令命令为64位编码后的notepad.exe即记事本。

eval()方法本身位于script.dll库在jscript!JsEval处下断点。这个方法使用了jscript!COleScript::Compile API来生成通过eval()执行的javascript命令

```
0:000&gt; sxe ld jscript;g
ModLoad: 00007fff`9e650000 00007fff`9e70c000   C:WindowsSystem32jscript.dll
ntdll!NtMapViewOfSection+0x14:
00007fff`c8e658a4 c3              ret
0:000&gt; bp jscript!JsEval
0:000&gt; g
Breakpoint 0 hit
jscript!JsEval:
00007fff`9e681960 488bc4          mov     rax,rsp
0:000&gt; u rip L50
jscript!JsEval:
00007fff`9e681960 488bc4          mov     rax,rsp
00007fff`9e681963 48895810        mov     qword ptr [rax+10h],rbx
00007fff`9e681967 48897018        mov     qword ptr [rax+18h],rsi
00007fff`9e68196b 48897820        mov     qword ptr [rax+20h],rdi
[...redacted…]
00007fff`9e681a81 488364242000    and     qword ptr [rsp+20h],0
00007fff`9e681a87 e80c3cfdff      call    jscript!COleScript::Compile
00007fff`9e681a8c 89455f          mov     dword ptr [rbp+5Fh],eax
00007fff`9e681a8f 8bf8            mov     edi,eax
00007fff`9e681a91 85c0            test    eax,eax
00007fff`9e681a93 7923            jns     jscript!JsEval+0x158 (00007fff`9e681ab8)
```

我们可以在jscript!COleScript::Compile处下断来获得调用计算器的命令以及base64编码过用来调用notepad.exe的命令

```
0:000&gt; bp jscript!COleScript::Compile "r $t1 = poi(rdx+0x10);r $t2 = poi($t1+0x8);du $t2;g";g
jscript!COleScript::Compile:
00007fff`9e715698 4053            push    rbx
0:000&gt; g
0000019b`d23f6408  "var oShell = new ActiveXObject(""
0000019b`d23f6448  "Shell.Application");var commandt"
0000019b`d23f6488  "oRun = "calc.exe"; oShell.ShellE"
0000019b`d23f64c8  "xecute(commandtoRun,"","","","1""
0000019b`d23f6508  ");."
80070002 The system cannot find the file specified.
0000019b`d473a1b0  "var oShell = new ActiveXObject(""
0000019b`d473a1f0  "Shell.Application");var commandt"
0000019b`d473a230  "oRun = "notepad.exe"; oShell.She"
0000019b`d473a270  "llExecute(commandtoRun,"","","","
0000019b`d473a2b0  ""1");"
ntdll!NtTerminateProcess+0x14:
00007fff`c8e65924 c3              ret
```

**<br>**

**总结**

****

Windbg是非常强大的工具它不仅可以用来帮助分析.NET文件也可以用来理解javascript代码是如何通过wscript.exe执行的。使用windbg进行调试可以提供不同的功能性概述便于复杂javascript的分析

附:获得对象所在库的python脚本

```
from _winreg import *
import sys
 
try:
  objectName = sys.argv[1]
except:
  sys.exit(1)
 
try:
  hReg = ConnectRegistry(None,HKEY_CLASSES_ROOT)
  hCLSIDKey = OpenKey(hReg, objectName+"CLSID")
  CLSID=QueryValue(hCLSIDKey, "")
  if CLSID:
    hKey = OpenKey(hReg, "CLSID\"+CLSID)
    description = QueryValue(hKey, "")
    hKey = OpenKey(hReg, "CLSID\"+CLSID+"\InProcServer32")
    dll = QueryValueEx(hKey, "")[0]
    print "Object Name: "+objectName
    print "CLSID: "+CLSID
    print "Description: "+description
    print "dll: "+dll
  else:
    print "No CLSID"
except:
  print "Error"
  sys.exit(2)
```

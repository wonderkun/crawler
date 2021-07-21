> 原文链接: https://www.anquanke.com//post/id/209199 


# 自动重构Meterpreter绕过杀软


                                阅读量   
                                **199912**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者scrt，文章来源：blog.scrt.ch
                                <br>原文地址：[https://blog.scrt.ch/2020/06/19/engineering-antivirus-evasion/](https://blog.scrt.ch/2020/06/19/engineering-antivirus-evasion/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01c960804edde99455.jpg)](https://p0.ssl.qhimg.com/t01c960804edde99455.jpg)



## 前言

此文章记录了我们对杀毒软件某些方面的研究，以及我们如何设法自动重构Meterpreter以绕过我们所遇到的每个AV / EDR。 虽然下面详细介绍了每种技术的思想和字符串混淆过程的实现，但我们决定在以后的文章中发布有关API导入隐藏/系统调用重写的详细信息，以使此内容尽可能简短。 源代码位于[https://github.com/scrt/avcleaner](https://github.com/scrt/avcleaner)

大多数公司通常采取防御措施来保护其信息系统免受攻击，在这些措施中，杀毒软件或EDR等安全软件通常是必不可少的工具集。尽管过去几年来绕过任何类型的恶意软件检测机制非常容易，但如今这样做无疑需要付出更多的努力。

另一方面，在POC本身被反病毒软件阻止的情况下，与漏洞相关的风险交流变得更具有挑战性。尽管理论上可以说有可能绕过检测并保留它，但实际上这样做可能会增加强度。

鉴于此，需要能够绕过杀毒软件。使事情稍微复杂化的是，在SCRT，我们尽可能地使用公开可用的开源代码工具，以展示我们的工作可以被任何熟练使用它们的人复制，并且不依赖于昂贵的私人工具。



## 问题现状

现在的社区通常喜欢将任何防病毒的检测机制归类为`静态`或`动态`。通常，如果在恶意软件执行之前触发了检测，则将其视为一种静态检测。<br>
但是，值得一提的是，杀软也可以在恶意软件执行期间调用静态检测机制（例如签名），以响应诸如进程创建，内存中文件下载等事件。<br>
无论如何，如果我们想对任何类型的安全软件使用旧的Meterpreter，我们都必须对其进行修改，使其满足以下要求：

> <ul>
- 在文件系统扫描或内存扫描时，绕过任何静态签名。
- 绕过“行为检测”，这种行为通常与绕过用户界面API hooking有关。
</ul>

但是，Meterpreter包含几个模块，整个代码库总计约700’000行代码。此外，它会不断更新，这意味着运行项目的私有分支肯定会导致扩展性很差。简而言之，我们需要一种自动转换代码库的方法。



## 解决方案

经过多年绕过防病毒软件的实际经验，我们发现恶意软件检测几乎都是基于字符串，API hooks或两者的结合。

即使对于实施机器学习分类的产品（例如Cylance），一个没有字符串，API导入和可挂钩API调用的恶意软件也可以像足球射门一样穿过Sergio Rico的防御网络。

Meterpreter具有成千上万个字符串，不会以任何方式隐藏API导入，并且可以使用用户界面API hook轻松拦截敏感的API，例如`WriteProcessMemory`。 因此，我们需要以自动化的方式对此进行补救，这将产生两个潜在的解决方案：

> <ul>
- 源到源代码重构
- LLVM在编译时混淆代码库。
</ul>

显然，后者将是首选方法，这是许多流行的研究得出相同的结论。 主要原因是，转换遍历可以只编写一次，而可以独立于软件的编程语言或目标体系结构重复使用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013786b3bd111d5beb.png)

但是，这样做需要有用Visual Studio以外的编译器编译Meterpreter的能力。尽管我们已于2018年12月发布了一些更改工作，但在一年多之后，正式代码库的采用仍然是一个需要持续的过程。

同时，我们已决定不顾一切成本的实施第一种方法。在对源代码重构的最新技术进行了彻底的回顾之后，libTooling（Clang / LLVM工具链的一部分）似乎是解析C / C ++源代码并对其进行修改的唯一可行的选择。

注意：由于代码库高度依赖Visual Studio，因此Clang无法解析Metepreter的很大一部分。但是，仍然有可能以一半的概率绕过目标防病毒软件。在这里，我们可能遇到`源到源转换`相对于`编译时转换`的唯一优势：那就是编译时转换要求整个项目进行编译而没有任何错误。而源到源转换可以允许成千上万的编译错误。而你只会得到一个不完整的抽象语法树，这非常好。



## 字符串混淆

在C / C ++中，字符串可能位于许多不同的上下文中。 libTooling并不是一个足够好的工具，因此我们应用了帕雷托法则（也即二八定律），将研究范围限制在Meterpreter代码库中最可疑的字符串出现的代码上：

> <ul>
- 函数参数
- 列表初始化
</ul>



## 函数参数

例如，我们知道，在以下情况下，`ESET Nod32`将标记字符串`ntdll`为可疑：

```
ntdll = LoadLibrary(TEXT("ntdll"))
```

但是，用以下方式重写此代码段将成功绕过检测：

```
wchar_t ntdll_str[] = `{`'n','t','d','l','l',0`}`;
ntdll = LoadLibrary(ntdll_str)
```

在看不见的幕后，第一个代码片段使字符串`ntdll`存储在生成的二进制文件的`.rdata`段内，并且防病毒程序很容易发现该字符串。 第二个片段使字符串在运行时存储在堆栈中，并且在通常情况下与代码在静态上无法区分。 IDA Pro或替代产品通常能够识别字符串，但它们也需要对二进制文件运行更高级且计算量更大的分析。



## 列表初始化

在Meterpreter的代码库中，可以在几个文件中找到这种构造，例如在**c/meterpreter/source/extensions/extapi/extapi.c** 中：

```
Command customCommands[] =
`{`
    COMMAND_REQ("extapi_window_enum", request_window_enum),
    COMMAND_REQ("extapi_service_enum", request_service_enum),
    COMMAND_REQ("extapi_service_query", request_service_query),
    COMMAND_REQ("extapi_service_control", request_service_control),
    COMMAND_REQ("extapi_clipboard_get_data", request_clipboard_get_data),
    COMMAND_REQ("extapi_clipboard_set_data", request_clipboard_set_data),
    COMMAND_REQ("extapi_clipboard_monitor_start", request_clipboard_monitor_start),
    COMMAND_REQ("extapi_clipboard_monitor_pause", request_clipboard_monitor_pause),
    COMMAND_REQ("extapi_clipboard_monitor_resume", request_clipboard_monitor_resume),
    COMMAND_REQ("extapi_clipboard_monitor_purge", request_clipboard_monitor_purge),
    COMMAND_REQ("extapi_clipboard_monitor_stop", request_clipboard_monitor_stop),
    COMMAND_REQ("extapi_clipboard_monitor_dump", request_clipboard_monitor_dump),
    COMMAND_REQ("extapi_adsi_domain_query", request_adsi_domain_query),
    COMMAND_REQ("extapi_ntds_parse", ntds_parse),
    COMMAND_REQ("extapi_wmi_query", request_wmi_query),
    COMMAND_REQ("extapi_pageant_send_query", request_pageant_send_query),
    ...
`}`
```

这些字符串以明文形式存储在`ext_server_espia.x64.dll`的`.rdata`节中，并由`ESET Nod32`进行选择。

更糟糕的是，这些字符串是位于列表初始化程序中的宏的参数。 这引入了很多棘手的案例，但这些案例并不需要关心。我们的目的是自动重写此代码段，如下所示：

```
char hid_extapi_UQOoNXigAPq4[] = `{`'e','x','t','a','p','i','_','w','i','n','d','o','w','_','e','n','u','m',0`}`;
char hid_extapi_vhFHmZ8u2hfz[] = `{`'e','x','t','a','p','i','_','s','e','r','v','i','c','e','_','e','n','u','m',0`}`;
char hid_extapi_pW25eeIGBeru[] = `{`'e','x','t','a','p','i','_','s','e','r','v','i','c','e','_','q','u','e','r','y'
0`}`;
char hid_extapi_S4Ws57MYBjib[] = `{`'e','x','t','a','p','i','_','s','e','r','v','i','c','e','_','c','o','n','t','r'
'o','l',0`}`;
char hid_extapi_HJ0lD9Dl56A4[] = `{`'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','g','e','t'
'_','d','a','t','a',0`}`;
char hid_extapi_IiEzXils3UsR[] = `{`'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','s','e','t'
'_','d','a','t','a',0`}`;
char hid_extapi_czLOBo0HcqCP[] = `{`'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','m','o','n'
'i','t','o','r','_','s','t','a','r','t',0`}`;
char hid_extapi_WcWbTrsQujiT[] = `{`'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','m','o','n'
'i','t','o','r','_','p','a','u','s','e',0`}`;
char hid_extapi_rPiFTZW4ShwA[] = `{`'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','m','o','n'
'i','t','o','r','_','r','e','s','u','m','e',0`}`;
char hid_extapi_05fAoaZLqOoy[] = `{`'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','m','o','n'
'i','t','o','r','_','p','u','r','g','e',0`}`;
char hid_extapi_cOOyHTPTvZGK[] = `{`'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','m','o','n','i','t','o','r','_','s','t','o','p',0`}`;
char hid_extapi_smtmvW05cI9y[] = `{`'e','x','t','a','p','i','_','c','l','i','p','b','o','a','r','d','_','m','o','n','i','t','o','r','_','d','u','m','p',0`}`;
char hid_extapi_01kuYCM8z49k[] = `{`'e','x','t','a','p','i','_','a','d','s','i','_','d','o','m','a','i','n','_','q','u','e','r','y',0`}`;
char hid_extapi_SMK9uFj6nThk[] = `{`'e','x','t','a','p','i','_','n','t','d','s','_','p','a','r','s','e',0`}`;
char hid_extapi_PHxnGM7M0609[] = `{`'e','x','t','a','p','i','_','w','m','i','_','q','u','e','r','y',0`}`;
char hid_extapi_J7EGS6FRHwkV[] = `{`'e','x','t','a','p','i','_','p','a','g','e','a','n','t','_','s','e','n','d','_','q','u','e','r','y',0`}`;

Command customCommands[] =
`{`

    COMMAND_REQ(hid_extapi_UQOoNXigAPq4, request_window_enum),
    COMMAND_REQ(hid_extapi_vhFHmZ8u2hfz, request_service_enum),
    COMMAND_REQ(hid_extapi_pW25eeIGBeru, request_service_query),
    COMMAND_REQ(hid_extapi_S4Ws57MYBjib, request_service_control),
    COMMAND_REQ(hid_extapi_HJ0lD9Dl56A4, request_clipboard_get_data),
    COMMAND_REQ(hid_extapi_IiEzXils3UsR, request_clipboard_set_data),
    COMMAND_REQ(hid_extapi_czLOBo0HcqCP, request_clipboard_monitor_start),
    COMMAND_REQ(hid_extapi_WcWbTrsQujiT, request_clipboard_monitor_pause),
    COMMAND_REQ(hid_extapi_rPiFTZW4ShwA, request_clipboard_monitor_resume),
    COMMAND_REQ(hid_extapi_05fAoaZLqOoy, request_clipboard_monitor_purge),
    COMMAND_REQ(hid_extapi_cOOyHTPTvZGK, request_clipboard_monitor_stop),
    COMMAND_REQ(hid_extapi_smtmvW05cI9y, request_clipboard_monitor_dump),
    COMMAND_REQ(hid_extapi_01kuYCM8z49k, request_adsi_domain_query),
    COMMAND_REQ(hid_extapi_SMK9uFj6nThk, ntds_parse),
    COMMAND_REQ(hid_extapi_PHxnGM7M0609, request_wmi_query),
    COMMAND_REQ(hid_extapi_J7EGS6FRHwkV, request_pageant_send_query),
    COMMAND_TERMINATOR
`}`;
```



## 隐藏API导入

调用由外部库导出的函数会使链接器向`导入地址表`(IAT)写入一个条目。 最终函数名称将在二进制文件中以明文形式显示，因此在无需执行恶意文件的情况下，可以静态恢复函数名。 当然，有些函数名称相比其他名称更可疑。 一个更明智的做法是隐藏所有可疑二进制文件，同时，保留大多数合法二进制文件中存在的文件。

例如，在Metepreter的`kiwi`扩展中，可以找到以下行：

```
enumStatus = SamEnumerateUsersInDomain(hDomain, &amp;EnumerationContext, 0, &amp;pEnumBuffer, 100, &amp;CountRetourned);
```

该函数由`samlib.dll`导出，因此链接器会使字符串`samlib.dll`和`SamEnumerateUsersInDomain`出现在已编译的二进制文件中。

要解决此问题，可以在运行时使用`LoadLibrary/GetProcAddresss`导入API。当然，这两个函数都适用于字符串，因此也必须对其进行混淆。 因此，我们希望按如下所示自动重写上述代码段：

```
typedef NTSTATUS(__stdcall* _SamEnumerateUsersInDomain)(
    SAMPR_HANDLE DomainHandle,
    PDWORD EnumerationContext,
    DWORD UserAccountControl,
    PSAMPR_RID_ENUMERATION* Buffer,
    DWORD PreferedMaximumLength,
    PDWORD CountReturned
);
char hid_SAMLIB_01zmejmkLCHt[] = `{`'S','A','M','L','I','B','.','D','L','L',0`}`;
char hid_SamEnu_BZxlW5ZBUAAe[] = `{`'S','a','m','E','n','u','m','e','r','a','t','e','U','s','e','r','s','I','n','D','o','m','a','i','n',0`}`;
HANDLE hhid_SAMLIB_BZUriyLrlgrJ = LoadLibrary(hid_SAMLIB_01zmejmkLCHt);
_SamEnumerateUsersInDomain ffSamEnumerateUsersInDoma =(_SamEnumerateUsersInDomain)GetProcAddress(hhid_SAMLIB_BZUriyLrlgrJ, hid_SamEnu_BZxlW5ZBUAAe);
enumStatus = ffSamEnumerateUsersInDoma(hDomain, &amp;EnumerationContext, 0, &amp;pEnumBuffer, 100, &amp;CountRetourned);
Rewriting syscalls
```



## 重写系统调用

默认情况下，在运行`Cylance`的计算机上使用Meterpreter的`migration`命令会触发杀软检测（请谨慎）。 Cylance会使用用户界面hook检测进程注入。 为了避开检测，可以去掉hook，这似乎是现在的主流趋势，或者可以完全避免使用hook。 我们发现，读取`ntdll`，恢复系统调用号并将其插入随时可以调用的`Shellcode`中更为简单，这可以有效地绕过任何杀软用户区的钩子。 迄今为止，我们尚未找到可以将从磁盘读取的`NTDLL.DLL`的行为识别为**可疑**的蓝队。



## 实现

上述所有想法都可以在基于libtools的源代码重构工具中实现。本节说明我们是如何做到这一点的，这是在时间和耐心之间的妥协。因为缺少libtools文档，所以此处还有改进的空间，如果你发现了什么，那可能是我们希望得到的反馈。

### <a class="reference-link" name="%E6%8A%BD%E8%B1%A1%E8%AF%AD%E6%B3%95%E6%A0%91101"></a>抽象语法树101

编译器通常包括几个组件，最常见的是解析器和词法分析器。 当将源代码提供给编译器时，它首先从原始源代码（程序员编写的代码）中生成一个解析树，然后将语义信息添加到节点（编译器真正需要的）。 此步骤的结果称为抽象语法树。 维基百科展示了以下示例：

```
while b ≠ 0
  if a &gt; b
    a := a − b
  else
    b := b − a
return a
```

这个小程序的典型AST如下所示：

[![](https://p4.ssl.qhimg.com/t01eaec87f4063bdfcb.png)](https://p4.ssl.qhimg.com/t01eaec87f4063bdfcb.png)

在编写需要理解其他程序属性的程序时，这个数据结构允许使用更精确的算法，因此执行大规模代码重构是一个不错的选择。

### <a class="reference-link" name="Clang%E7%9A%84%E6%8A%BD%E8%B1%A1%E8%AF%AD%E6%B3%95%E6%A0%91"></a>Clang的抽象语法树

由于我们需要正确修改源代码，因此我们需要熟悉Clang的AST。 好消息是Clang公开了一个命令行开关，以漂亮的颜色转储AST。 坏消息是，对于除”玩具项目”以外的所有项目，设置正确的编译器标志都非常棘手。

现在，让我们做一个现实而简单的翻译测试单元:

```
#include &lt;windows.h&gt;

typedef NTSTATUS (NTAPI *f_NtMapViewOfSection)(HANDLE, HANDLE, PVOID *, ULONG, ULONG,
PLARGE_INTEGER, PULONG, ULONG, ULONG, ULONG);

int main(void)
`{`
    f_NtMapViewOfSection lNtMapViewOfSection;
    HMODULE ntdll;

    if (!(ntdll = LoadLibrary(TEXT("ntdll"))))
    `{`
        return -1;
    `}`

    lNtMapViewOfSection = (f_NtMapViewOfSection)GetProcAddress(ntdll, "NtMapViewOfSection");
    lNtMapViewOfSection(0,0,0,0,0,0,0,0,0,0);
    return 0;
`}`
```

然后，将以下脚本插入.sh文件中：

```
WIN_INCLUDE="/Users/vladimir/headers/winsdk"
CLANG_PATH="/usr/local/Cellar/llvm/9.0.1"#"/usr/lib/clang/8.0.1/"

clang -cc1 -ast-dump "$1" -D "_WIN64" -D "_UNICODE" -D "UNICODE" -D "_WINSOCK_DEPRECATED_NO_WARNINGS"
  "-I" "$CLANG_PATH/include" 
  "-I" "$CLANG_PATH" 
  "-I" "$WIN_INCLUDE/Include/msvc-14.15.26726-include"
  "-I" "$WIN_INCLUDE/Include/10.0.17134.0/ucrt" 
  "-I" "$WIN_INCLUDE/Include/10.0.17134.0/shared" 
  "-I" "$WIN_INCLUDE/Include/10.0.17134.0/um" 
  "-I" "$WIN_INCLUDE/Include/10.0.17134.0/winrt" 
  "-fdeprecated-macro" 
  "-w" 
  "-fdebug-compilation-dir"
  "-fno-use-cxa-atexit" "-fms-extensions" "-fms-compatibility" 
  "-fms-compatibility-version=19.15.26726" "-std=c++14" "-fdelayed-template-parsing" "-fobjc-runtime=gcc" "-fcxx-exceptions" "-fexceptions" "-fseh-exceptions" "-fdiagnostics-show-option" "-fcolor-diagnostics" "-x" "c++"
```

请注意，`WIN_INCLUDE`指向一个文件夹，其中包含与Win32 API进行交互的所有必需的标头。 这些是从标准Windows 10安装中直接获取的，为了避免让你头疼，我们建议你执行相同操作，千万不要选择`MinGW`。 然后，以需要测试的C文件作为参数来调用脚本。 虽然这会产生一个18MB的文件，但通过搜索我们定义的字符串之一（例如“ NtMapViewOfSection”），可以轻松导航到AST的有趣部分：

[![](https://p4.ssl.qhimg.com/t01a7b4046a90e19b4f.png)](https://p4.ssl.qhimg.com/t01a7b4046a90e19b4f.png)

现在，我们有了一种可视化AST的方法，可以更轻易地了解如何更新节点才能获得结果，同时不在结果源代码中引入任何语法错误。 以下各节包含与使用libTooling进行AST操作有关实现的详细信息。

### <a class="reference-link" name="ClangTool%E6%A0%B7%E6%9D%BF"></a>ClangTool样板

在进入有趣的内容之前，需要一些样板代码，因此需要将以下代码插入main.cpp中：

```
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/ASTContext.h"
#include "clang/AST/Decl.h"
#include "clang/AST/Type.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/Basic/SourceManager.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Frontend/FrontendAction.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Rewrite/Core/Rewriter.h"

// LLVM includes
#include "llvm/ADT/ArrayRef.h"
#include "llvm/ADT/StringRef.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/raw_ostream.h"

#include "Consumer.h"
#include "MatchHandler.h"

#include &lt;iostream&gt;
#include &lt;memory&gt;
#include &lt;string&gt;
#include &lt;vector&gt;
#include &lt;fstream&gt;
#include &lt;clang/Tooling/Inclusions/IncludeStyle.h&gt;
#include &lt;clang/Tooling/Inclusions/HeaderIncludes.h&gt;
#include &lt;sstream&gt;

namespace ClSetup `{`
    llvm::cl::OptionCategory ToolCategory("StringEncryptor");
`}`

namespace StringEncryptor `{`

    clang::Rewriter ASTRewriter;
    class Action : public clang::ASTFrontendAction `{`

    public:
        using ASTConsumerPointer = std::unique_ptr&lt;clang::ASTConsumer&gt;;

        ASTConsumerPointer CreateASTConsumer(clang::CompilerInstance &amp;Compiler,
                                             llvm::StringRef Filename) override `{`

            ASTRewriter.setSourceMgr(Compiler.getSourceManager(), Compiler.getLangOpts());
            std::vector&lt;ASTConsumer*&gt; consumers;

            consumers.push_back(&amp;StringConsumer);

            // several passes can be combined together by adding them to `consumers`
            auto TheConsumer = llvm::make_unique&lt;Consumer&gt;();
            TheConsumer-&gt;consumers = consumers;
            return TheConsumer;
        `}`

        bool BeginSourceFileAction(clang::CompilerInstance &amp;Compiler) override `{`
            llvm::outs() &lt;&lt; "Processing file " &lt;&lt; 'n';
            return true;
        `}`

        void EndSourceFileAction() override `{`

            clang::SourceManager &amp;SM = ASTRewriter.getSourceMgr();

            std::string FileName = SM.getFileEntryForID(SM.getMainFileID())-&gt;getName();
            llvm::errs() &lt;&lt; "** EndSourceFileAction for: " &lt;&lt; FileName &lt;&lt; "n";

            // Now emit the rewritten buffer.
            llvm::errs() &lt;&lt; "Here is the edited source file :nn";
            std::string TypeS;
            llvm::raw_string_ostream s(TypeS);
            auto FileID = SM.getMainFileID();
            auto ReWriteBuffer = ASTRewriter.getRewriteBufferFor(FileID);

            if(ReWriteBuffer != nullptr)
                ReWriteBuffer-&gt;write((s));
            else`{`
                llvm::errs() &lt;&lt; "File was not modifiedn";
                return;
            `}`

            std::string result = s.str();
            std::ofstream fo(FileName);

            if(fo.is_open())
                fo &lt;&lt; result;
            else
                llvm::errs() &lt;&lt; "[!] Error saving result to " &lt;&lt; FileName &lt;&lt; "n";
        `}`
    `}`;
`}`

auto main(int argc, const char *argv[]) -&gt; int `{`

    using namespace clang::tooling;
    using namespace ClSetup;

    CommonOptionsParser OptionsParser(argc, argv, ToolCategory);
    ClangTool Tool(OptionsParser.getCompilations(),
                   OptionsParser.getSourcePathList());

    auto Action = newFrontendActionFactory&lt;StringEncryptor::Action&gt;();
    return Tool.run(Action.get());
`}`
```

由于该样板代码取自官方文档中的示例，因此不需要再进一步的描述。 唯一值得一提的修改是在`CreateASTConsumer`的内部。 我们的最终目标是在同一个翻译单元上进行多次转换。 可以通过将项目添加到集合中来完成（基本行是`consumers.push_back(&amp;...);`）。

### <a class="reference-link" name="%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%B7%B7%E6%B7%86"></a>字符串混淆

本节描述有关字符串混淆过程的最重要的实现细节，包括三个步骤：

> <ul>
- 在源代码中找到字符串。
- 用变量替换它们
- 在适当的位置（包含函数或全局上下文中）插入变量定义/赋值。
</ul>

#### <a class="reference-link" name="%E5%9C%A8%E6%BA%90%E4%BB%A3%E7%A0%81%E4%B8%AD%E6%9F%A5%E6%89%BE%E5%AD%97%E7%AC%A6%E4%B8%B2%E6%96%87%E5%AD%97"></a>在源代码中查找字符串文字

可以如下定义`StringConsumer`（在StringEncryptor命名空间的开头）：

```
class StringEncryptionConsumer : public clang::ASTConsumer `{`
public:

    void HandleTranslationUnit(clang::ASTContext &amp;Context) override `{`
        using namespace clang::ast_matchers;
        using namespace StringEncryptor;

        llvm::outs() &lt;&lt; "[StringEncryption] Registering ASTMatcher...n";
        MatchFinder Finder;
        MatchHandler Handler(&amp;ASTRewriter);

        const auto Matcher = stringLiteral().bind("decl");

        Finder.addMatcher(Matcher, &amp;Handler);
        Finder.matchAST(Context);
    `}`
`}`;

StringEncryptionConsumer StringConsumer = StringEncryptionConsumer();
```

给定一个翻译单元，我们可以告诉Clang在AST中找到一个模式，同时注册一个“处理程序”以在找到匹配项时调用。 Clang的[ASTMatcher](https://clang.llvm.org/docs/LibASTMatchersReference.html)公开的模式匹配功能非常强大，但在这里并未得到充分利用，因为我们仅是用它来定位字符串。

然后，我们可以通过实现MatchHandler来解决问题，它将为我们提供[MatchResult](https://clang.llvm.org/doxygen/structclang_1_1ast__matchers_1_1MatchFinder_1_1MatchResult.html#ab06481084c7027e5779a5a427596f66c)实例。 MatchResult包含对标识的AST节点的引用以及上下文信息。

接下来我们可以实现一个类的定义，并从**[clang::ast_matchers::MatchFinder::MatchCallback](https://clang.llvm.org/doxygen/classclang_1_1ast__matchers_1_1MatchFinder_1_1MatchCallback.html)**:继承一些东西：

```
#ifndef AVCLEANER_MATCHHANDLER_H
#define AVCLEANER_MATCHHANDLER_H

#include &lt;vector&gt;
#include &lt;string&gt;
#include &lt;memory&gt;
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/ADT/StringRef.h"
#include "llvm/ADT/ArrayRef.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Frontend/FrontendAction.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Basic/SourceManager.h"
#include "clang/ASTMatchers/ASTMatchers.h"
#include "clang/ASTMatchers/ASTMatchFinder.h"
#include "clang/AST/Type.h"
#include "clang/AST/Decl.h"
#include "clang/AST/ASTContext.h"
#include "clang/AST/ASTConsumer.h"
#include "MatchHandler.h"

class MatchHandler : public clang::ast_matchers::MatchFinder::MatchCallback `{`

public:
    using MatchResult = clang::ast_matchers::MatchFinder::MatchResult;

    MatchHandler(clang::Rewriter *rewriter);
    void run(const MatchResult &amp;Result) override; // callback function that runs whenever a Match is found.

`}`;

#endif //AVCLEANER_MATCHHANDLER_H
```

在`MatchHandler.cpp`中，我们必须实现`MatchHandler`的构造函数和run回调函数。 构造函数非常简单，仅仅只需要存储 [clang::Rewrite](https://clang.llvm.org/doxygen/classclang_1_1Rewriter.html)的实例以供以后使用即可：

```
using namespace clang;

MatchHandler::MatchHandler(clang::Rewriter *rewriter) `{`
    this-&gt;ASTRewriter = rewriter;
`}`
```

run的实现如下所示：

```
void MatchHandler::run(const MatchResult &amp;Result) `{`
    const auto *Decl = Result.Nodes.getNodeAs&lt;clang::StringLiteral&gt;("decl");
    clang::SourceManager &amp;SM = ASTRewriter-&gt;getSourceMgr();

    // skip strings in included headers
    if (!SM.isInMainFile(Decl-&gt;getBeginLoc()))
        return;

    // strings that comprise less than 5 characters are not worth the effort
    if (!Decl-&gt;getBytes().str().size() &gt; 4) `{`
        return;
    `}`

    climbParentsIgnoreCast(*Decl, clang::ast_type_traits::DynTypedNode(), Result.Context, 0);
`}`
```

上面摘录的三段代码中有三个点值得一提：

> <ul>
- 我们提取与StringEncryptionConsumer中定义的模式匹配的AST节点。为此，可以调用函数getNodeAs，它需要一个字符串作为参数，该参数与模式绑定的标识符相关（请参见`const auto Matcher = stringLiteral().bind("decl")`行）
- 我们会跳过分析中没有在翻译单元中定义的字符串。实际上，我们的过程会在Clang的预处理程序之后进行干预，它会将包含的系统头的内容复制粘贴到翻译单元中。
- 然后，我们准备处理字符串。 由于我们需要在上下文中找到此字符串，因此需将提取的节点沿着Result.Context传递给用户定义的函数（在本例中为climbParentsIgnoreCast，因为缺少更好的名称），其中包含一个 参考随附的AST。 目标是向上访问树，直到找到有趣的节点。 在这种情况下，我们对CallExpr类型的节点感兴趣。
</ul>

```
bool
MatchHandler::climbParentsIgnoreCast(const StringLiteral &amp;NodeString, clang::ast_type_traits::DynTypedNode node,
                                     clang::ASTContext *const pContext, uint64_t iterations) `{`

    ASTContext::DynTypedNodeList parents = pContext-&gt;getParents(NodeString);

    if (iterations &gt; 0) `{`
        parents = pContext-&gt;getParents(node);
    `}`

    for (const auto &amp;parent : parents) `{`

        StringRef ParentNodeKind = parent.getNodeKind().asStringRef();

        if (ParentNodeKind.find("Cast") != std::string::npos) `{`

            return climbParentsIgnoreCast(NodeString, parent, pContext, ++iterations);
        `}`

        handleStringInContext(&amp;NodeString, pContext, parent);
    `}`

    return false;
`}`
```

简而言之，此函数以递归方式查找`StringLiteral`节点的父节点，直到找到一个有趣的节点（非“ cast”）。 handleStringInContext也很简单：

```
void MatchHandler::handleStringInContext(const clang::StringLiteral *pLiteral, clang::ASTContext *const pContext,
                                         const clang::ast_type_traits::DynTypedNode node) `{`

    StringRef ParentNodeKind = node.getNodeKind().asStringRef();

    if (ParentNodeKind.compare("CallExpr") == 0) `{`
        handleCallExpr(pLiteral, pContext, node);
    `}` else if (ParentNodeKind.compare("InitListExpr") == 0) `{`
        handleInitListExpr(pLiteral, pContext, node);
    `}` else `{`
        llvm::outs() &lt;&lt; "Unhandled context " &lt;&lt; ParentNodeKind &lt;&lt; " for string " &lt;&lt; pLiteral-&gt;getBytes() &lt;&lt; "n";
    `}`
`}`
```

从上面的代码片段可以明显看出，实际上只有两种类型的节点可以处理。 如果需要，添加更多内容也应该很容易。 事实上，这两种情况都已经用类似的方式处理。

```
void MatchHandler::handleCallExpr(const clang::StringLiteral *pLiteral, clang::ASTContext *const pContext,
                                  const clang::ast_type_traits::DynTypedNode node) `{`

    const auto *FunctionCall = node.get&lt;clang::CallExpr&gt;();

    if (isBlacklistedFunction(FunctionCall)) `{`
        return; // exclude printf-like functions when the replacement is not constant anymore (C89 standard...).
    `}`

    handleExpr(pLiteral, pContext, node);
`}`

void MatchHandler::handleInitListExpr(const clang::StringLiteral *pLiteral, clang::ASTContext *const pContext,
                                      const clang::ast_type_traits::DynTypedNode node) `{`

    handleExpr(pLiteral, pContext, node);
`}`
```

#### <a class="reference-link" name="%E6%9B%BF%E6%8D%A2%E5%AD%97%E7%AC%A6%E4%B8%B2"></a>替换字符串

由于`CallExpr`和`InitListExpr`都可以用类似的方式处理，因此我们定义了一个公共的可用函数。

```
bool MatchHandler::handleExpr(const clang::StringLiteral *pLiteral, clang::ASTContext *const pContext,
                                  const clang::ast_type_traits::DynTypedNode node) `{`

    clang::SourceRange LiteralRange = clang::SourceRange(
            ASTRewriter-&gt;getSourceMgr().getFileLoc(pLiteral-&gt;getBeginLoc()),
            ASTRewriter-&gt;getSourceMgr().getFileLoc(pLiteral-&gt;getEndLoc())
    );

    if(shouldAbort(pLiteral, pContext, LiteralRange))
        return false;

    std::string Replacement = translateStringToIdentifier(pLiteral-&gt;getBytes().str());

    if(!insertVariableDeclaration(pLiteral, pContext, LiteralRange, Replacement))
        return false ;

    Globs::PatchedSourceLocation.push_back(LiteralRange);

    return replaceStringLiteral(pLiteral, pContext, LiteralRange, Replacement);
`}`
```

> <ul>
- 我们随机生成一个变量名。
- 在最近的位置找到一些空白空间，然后插入变量声明。 这基本上是一个`ASTRewriter-&gt;InsertText()`的包装
- 将字符串替换为在步骤1中生成的标识符
- 将字符串所在位置添加到集合中。 这很有用，因为在访问`InitListExpr`时，相同的字符串将出现两次（不知道为什么）。
</ul>

最后一步是真正难以实现的一步，因此让我们首先关注这一点：

```
bool MatchHandler::replaceStringLiteral(const clang::StringLiteral *pLiteral, clang::ASTContext *const pContext,
                                        clang::SourceRange LiteralRange,
                                        const std::string&amp; Replacement) `{`

    // handle "TEXT" macro argument, for instance LoadLibrary(TEXT("ntdll"));
    bool isMacro = ASTRewriter-&gt;getSourceMgr().isMacroBodyExpansion(pLiteral-&gt;getBeginLoc());

    if (isMacro) `{`
        StringRef OrigText = clang::Lexer::getSourceText(CharSourceRange(pLiteral-&gt;getSourceRange(), true),
                                                         pContext-&gt;getSourceManager(), pContext-&gt;getLangOpts());

        // weird bug with TEXT Macro / other macros...there must be a proper way to do this.
        if (OrigText.find("TEXT") != std::string::npos) `{`

            ASTRewriter-&gt;RemoveText(LiteralRange);
            LiteralRange.setEnd(ASTRewriter-&gt;getSourceMgr().getFileLoc(pLiteral-&gt;getEndLoc().getLocWithOffset(-1)));
        `}`
    `}`

    return ASTRewriter-&gt;ReplaceText(LiteralRange, Replacement);
`}`
```

通常情况下，应该使用[ReplaceText](https://clang.llvm.org/doxygen/classclang_1_1Rewriter.html#afe00ce2338ce67ba76832678f21956ed) API实现替换文本，但是实际上遇到了很多错误。 当涉及到宏时，由于Clang的API行为不一致，因此事情会变得非常复杂。 例如，如果取消选中`isMacroBodyExpansion()`，最终将替换“ TEXT”而不是其参数。

例如，在`LoadLibrary(TEXT("ntdll"))`中，实际结果会变成`LoadLibrary(your_variable("ntdll"))`，这明显是错误的。

原因是TEXT是一个宏，当由Clang的预处理器处理时，会将其替换为`L"ntdll"`。 我们的转换过程是在预处理器完成工作之后发生的，因此查询标记”ntdll”的开始和结束位置将产生几个字符的额外值，这对我们没有用处。 不幸的是，使用Clang的API来查询原始翻译单元中的实际位置是一种魔咒，只能通过不断试错来进行。

#### <a class="reference-link" name="%E5%9C%A8%E6%9C%80%E8%BF%91%E7%9A%84%E7%A9%BA%E7%99%BD%E4%BD%8D%E7%BD%AE%E6%8F%92%E5%85%A5%E5%8F%98%E9%87%8F%E5%A3%B0%E6%98%8E"></a>在最近的空白位置插入变量声明

现在我们可以用变量标识符替换字符串了，我们的目标是定义该变量并为它分配给原始字符串的值。 简单的说，我们希望打补丁后的源代码包含`char your_variable[] = "ntdll"`，同时不覆盖任何内容。

可能有两种情况：

> <ul>
- 字符串文字位于函数体内。
- 字符串文字位于函数主体外部。
</ul>

后者是最直接的方法，因为只需要查找使用字符串的表达式的开头即可。

对于前者，我们需要找到封闭函数。 Clang公开了一个API来查询函数体的起始位置。 这是插入变量声明的理想位置，因为该变量将在整个函数中可见，并且我们插入的标记不会覆盖内容。

在任何情况下，这两种情况都可以通过访问每一个父节点来解决，直到找到一个[FunctionDecl](https://clang.llvm.org/doxygen/classclang_1_1FunctionDecl.html)或[VarDecl](https://clang.llvm.org/doxygen/classclang_1_1VarDecl.html)类型的节点为止：

```
MatchHandler::findInjectionSpot(clang::ASTContext *const Context, clang::ast_type_traits::DynTypedNode Parent,
                                const clang::StringLiteral &amp;Literal, bool IsGlobal, uint64_t Iterations) `{`

    if (Iterations &gt; CLIMB_PARENTS_MAX_ITER)
        throw std::runtime_error("Reached max iterations when trying to find a function declaration");

    ASTContext::DynTypedNodeList parents = Context-&gt;getParents(Literal);;

    if (Iterations &gt; 0) `{`
        parents = Context-&gt;getParents(Parent);
    `}`

    for (const auto &amp;parent : parents) `{`

        StringRef ParentNodeKind = parent.getNodeKind().asStringRef();

        if (ParentNodeKind.find("FunctionDecl") != std::string::npos) `{`
            auto FunDecl = parent.get&lt;clang::FunctionDecl&gt;();
            auto *Statement = FunDecl-&gt;getBody();
            auto *FirstChild = *Statement-&gt;child_begin();
            return `{`FirstChild-&gt;getBeginLoc(), FunDecl-&gt;getEndLoc()`}`;

        `}` else if (ParentNodeKind.find("VarDecl") != std::string::npos) `{`

            if (IsGlobal) `{`
                return parent.get&lt;clang::VarDecl&gt;()-&gt;getSourceRange();
            `}`
        `}`

        return findInjectionSpot(Context, parent, Literal, IsGlobal, ++Iterations);
    `}`
`}`
```



## 测试

```
git clone https://github.com/SCRT/avcleaner
mkdir avcleaner/CMakeBuild &amp;&amp; cd avcleaner/CMakeBuild
cmake ..
make
cd ..
bash run_example.sh test/string_simplest.c
```

[![](https://p5.ssl.qhimg.com/t0179ed351fdda80611.png)](https://p5.ssl.qhimg.com/t0179ed351fdda80611.png)

如您所见，这很好用。 现在，此示例非常简单，可以使用正则表达式解决，并减少代码行数。

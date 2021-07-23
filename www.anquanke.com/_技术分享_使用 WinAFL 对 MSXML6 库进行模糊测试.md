> 原文链接: https://www.anquanke.com//post/id/86905 


# 【技术分享】使用 WinAFL 对 MSXML6 库进行模糊测试


                                阅读量   
                                **214752**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：symeonp.github.io
                                <br>原文地址：[https://symeonp.github.io/2017/09/17/fuzzing-winafl.html ](https://symeonp.github.io/2017/09/17/fuzzing-winafl.html%20)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t013f231c0b60537c74.jpg)](https://p3.ssl.qhimg.com/t013f231c0b60537c74.jpg)



译者：[**天鸽**](http://bobao.360.cn/member/contribute?uid=145812086)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**MSXML库模糊测试**

在这篇博客中，我将介绍怎样使用 [**WinAFL**](https://github.com/ivanfratric/winafl)** fuzzer **来对 **MSXML** 库做模糊测试。

也许你还没有使用过 WinAFL，它是由** Ivan**（Google's Project Zero）创造的一个大型 fuzzer，它基于** Icumtuf **创造的使用 **DynamoRIO** 来测量代码覆盖率的 [AFL](http://lcamtuf.coredump.cx/afl/)，和用于内存和进程创建的 Windows API。[Axel Souchet](https://twitter.com/0vercl0k) 一直在积极地提供新功能，如最新稳定版中的 [corpus minimization](https://github.com/ivanfratric/winafl/commit/691dc760690750752054794891f75fbce50fee56)，将在下一篇博客中介绍的 [persistent execution mode](https://github.com/ivanfratric/winafl/commit/8aa1e138dd0284b1da5c844c5d21fc5ebe5d1c45) 和 [afl-tmin](https://github.com/ivanfratric/winafl/commit/992a68ba34df152e07453f0b592ff79aa8d4de9a) 工具。

我们将从创建一个测试框架（test harness）开始，它可以让我们在库中 fuzz 一些解析函数，计算覆盖范围和最小化测试用例，最后以启动 fuzzer 和对结果进行分类来结束。最后，感谢来自 0patch 的 Mitja Kolsek 提供的补丁，它展示了怎样用 0patch 来修补该漏洞！

使用上述步骤，我已经在函数 msxml6!DTD::findEntityGeneral 中找到了一个 NULL pointer dereference 的问题，我向微软报告后被拒绝，他们认为这不是一个安全问题。公平地说，只有 crash 确实没用，希望有人能发现一些有趣的东西。



**测试框架**

在做了一些研究的时候，我在[这里](https://msdn.microsoft.com/en-us/library/ms754517%28v=vs.85%29.aspx)发现了微软提供的一个 C++ 示例代码，它允许我们提供一些 XML 文件并验证其结构。我将使用 Visual Studio 2015 来构建下面的程序，但在之前，我稍微做了点修改，使用了 Ivan 的 charToWChar 方法，它接受一个参数作为一个文件：

```
// xmlvalidate_fuzz.cpp : Defines the entry point for the console application.
//
#include "stdafx.h"
#include &lt;stdio.h&gt;
#include &lt;tchar.h&gt;
#include &lt;windows.h&gt;
#import &lt;msxml6.dll&gt;
extern "C" __declspec(dllexport)  int main(int argc, char** argv);
// Macro that calls a COM method returning HRESULT value.
#define CHK_HR(stmt)        do `{` hr=(stmt); if (FAILED(hr)) goto CleanUp; `}` while(0)
void dump_com_error(_com_error &amp;e)
`{`
    _bstr_t bstrSource(e.Source());
    _bstr_t bstrDescription(e.Description());
    printf("Errorn");
    printf("atCode = %08lxn", e.Error());
    printf("atCode meaning = %s", e.ErrorMessage());
    printf("atSource = %sn", (LPCSTR)bstrSource);
    printf("atDescription = %sn", (LPCSTR)bstrDescription);
`}`
_bstr_t validateFile(_bstr_t bstrFile)
`{`
    // Initialize objects and variables.
    MSXML2::IXMLDOMDocument2Ptr pXMLDoc;
    MSXML2::IXMLDOMParseErrorPtr pError;
    _bstr_t bstrResult = L"";
    HRESULT hr = S_OK;
    // Create a DOMDocument and set its properties.
    CHK_HR(pXMLDoc.CreateInstance(__uuidof(MSXML2::DOMDocument60), NULL, CLSCTX_INPROC_SERVER));
    pXMLDoc-&gt;async = VARIANT_FALSE;
    pXMLDoc-&gt;validateOnParse = VARIANT_TRUE;
    pXMLDoc-&gt;resolveExternals = VARIANT_TRUE;
    // Load and validate the specified file into the DOM.
    // And return validation results in message to the user.
    if (pXMLDoc-&gt;load(bstrFile) != VARIANT_TRUE)
    `{`
        pError = pXMLDoc-&gt;parseError;
        bstrResult = _bstr_t(L"Validation failed on ") + bstrFile +
            _bstr_t(L"n=====================") +
            _bstr_t(L"nReason: ") + _bstr_t(pError-&gt;Getreason()) +
            _bstr_t(L"nSource: ") + _bstr_t(pError-&gt;GetsrcText()) +
            _bstr_t(L"nLine: ") + _bstr_t(pError-&gt;Getline()) +
            _bstr_t(L"n");
    `}`
    else
    `{`
        bstrResult = _bstr_t(L"Validation succeeded for ") + bstrFile +
            _bstr_t(L"n======================n") +
            _bstr_t(pXMLDoc-&gt;xml) + _bstr_t(L"n");
    `}`
CleanUp:
    return bstrResult;
`}`
wchar_t* charToWChar(const char* text)
`{`
    size_t size = strlen(text) + 1;
    wchar_t* wa = new wchar_t[size];
    mbstowcs(wa, text, size);
    return wa;
`}`
int main(int argc, char** argv)
`{`
    if (argc &lt; 2) `{`
        printf("Usage: %s &lt;xml file&gt;n", argv[0]);
        return 0;
    `}`
    HRESULT hr = CoInitialize(NULL);
    if (SUCCEEDED(hr))
    `{`
        try
        `{`
            _bstr_t bstrOutput = validateFile(charToWChar(argv[1]));
            MessageBoxW(NULL, bstrOutput, L"noNamespace", MB_OK);
        `}`
        catch (_com_error &amp;e)
        `{`
            dump_com_error(e);
        `}`
        CoUninitialize();
    `}`
    return 0;
`}`
```

请注意下面的代码片段：

```
extern "C" __declspec(dllexport)  int main(int argc, char** argv);
```

本质上，这允许我们使用 target_method 参数，DynamoRIO 将尝试为给定的[符号名（symbol name）](http://dynamorio.org/docs/group__drsyms.html#ga2e6f4d91b65fc835c047c8ca23c83d06%29)检索地址，如[这里](https://github.com/ivanfratric/winafl/blob/372a9746fb84a4c3a7656e7b79bf7e8c0c146142/winafl.c#L525)所示。<br>

我们可以按照 README 中使用的偏移方法，但是由于 ASLR 和所有这些东西，我们希望对模糊测试进行扩展，将二进制文件复制到许多台虚拟机里，并能使用相同的命令来进行 fuzz。指令 extern "C" 将 unmange 函数名，并使其看起来更漂亮。<br>

要确定 DynamoRIO 确实可以使用此方法，输入下面的命令：

```
dumpbin /EXPORTS xmlvalidate_fuzz.exe
```

[![](https://p5.ssl.qhimg.com/t01023118a03c190070.png)](https://p5.ssl.qhimg.com/t01023118a03c190070.png)

现在让我们赶快运行二进制文件并观察输出。你应该会得到下面的输出：

[![](https://p4.ssl.qhimg.com/t01eae76fe0560439b7.png)](https://p4.ssl.qhimg.com/t01eae76fe0560439b7.png)

**代码覆盖**

**WinAFL**

由于要测试的库是闭源的，所以我们将通过 WinAFL 使用 DynamoRIO 的代码覆盖库功能：

```
C:DRIObin32drrun.exe -c winafl.dll -debug -coverage_module msxml6.dll -target_module xmlvalidate.exe -target_method main -fuzz_iterations 10 -nargs 2 -- C:xml_fuzz_initialxmlvalidate.exe C:xml_fuzz_initialnn-valid.xml
```

WinAFL 将执行二进制文件十次。一旦完成，请返回到 winafl 的文件夹并检查日志文件：

[![](https://p1.ssl.qhimg.com/t015bb3f848185d0fb2.png)](https://p1.ssl.qhimg.com/t015bb3f848185d0fb2.png)

从输出中我们看到运行似乎一切正常！在文件的右侧，那些点描述了 DLL 的覆盖范围，如果你向下滚动，将会看到我们确实覆盖了许多的函数，因为我们在整个文件中获得了更多的点。我们在搜索大量的代码时，这是一个非常好的迹象，我们已经快要正确地定位到 MSXML6 的库。

**Lighthouse- IDA Pro 的代码覆盖资源管理器**

这个插件将帮助我们更好地了解我们命中的函数，并使用 IDA 对覆盖范围进行了很好的概述。这是一个很好的插件，且具有良好的文档，由 Markus Gaasedelen (@gaasedelen) 所开发。请确保下载了最新版的 [DynamoRIO 7](https://github.com/DynamoRIO/dynamorio/releases/download/release_7_0_0_rc1/DynamoRIO-Windows-7.0.0-RC1.zip)，并按照[这里](https://github.com/gaasedelen/lighthouse)的说明进行安装。幸运的是，我们从文档中获得了两个样本测试用例，一个有效一个无效。让我们输入有效的一个并观察覆盖情况。为此，运行下面的命令：

```
C:DRIO7bin64drrun.exe -t drcov -- xmlvalidate.exe nn-valid.xml
```

下一步启动 IDA，加载 msxml6.dll 并确保获得了符号！现在，检查是否有一个 .log 文件被创建，并在 IDA 中依次点击

File -&gt; Load File -&gt; Code Coverage File(s) 打开它。一旦覆盖文件被加载，它将高亮出测试用例命中的所有函数。

**测试用例最小化**

现在是时候测试 XML 文件了（尽可能小）。我使用了一个稍微偏黑客的 joxean find_samples.py 版本的脚本。一旦你得到了几个测试用例，就可以最小化初始 seed 文件。可以使用下面的命令完成：

```
python winafl-cmin.py --working-dir C:winaflbin32 -D C:DRIObin32 -t 100000 -i C:xml_fuzzsamples -o C:minset_xml -coverage_module msxml6.dll -target_module xmlvalidate.exe -target_method fuzzme -nargs 1 -- C:xml_fuzzxmlvalidate.exe @@
```

你会看到下面的输出：

```
corpus minimization tool for WinAFL by &lt;0vercl0k@tuxfamily.org&gt; 
Based on WinAFL by &lt;ifratric@google.com&gt; 
Based on AFL by &lt;lcamtuf@google.com&gt; 
[+] CWD changed to C:winaflbin32. 
[*] Testing the target binary... 
[!] Dry-run failed, 2 executions resulted differently: 
Tuples matching? False 
Return codes matching? True
```

我不太确定，但我认为 winafl-cmin.py 脚本期望初始 seed 文件指向相同的代码路径，也就是我们必须一次有效的测试用例，和一次无效的测试用例。可能是我错了，也可能是有一个 bug。

我们使用下面的 bash 脚本来确定一下“好的”和“坏的”XML 测试用例。

```
$ for file in *; do printf "==== FILE: $file =====n"; /cygdrive/c/xml_fuzz/xmlvalidate.exe $file ;sleep 1; done
```

下面的截图显示了我的运行结果：

[![](https://p0.ssl.qhimg.com/t019acfe1966bd9b11c.png)](https://p0.ssl.qhimg.com/t019acfe1966bd9b11c.png)

随意尝试一下，看看是哪些文件导致了这个问题（你的可能会有所不同）。一旦确定，再次运行上面的命令，希望你能得到下面的结果：

[![](https://p4.ssl.qhimg.com/t01964afc07167867c4.png)](https://p4.ssl.qhimg.com/t01964afc07167867c4.png)

你看，初始用例包含 76 个文件，最小化后缩减至 26 个。感谢 Axel！

使用最小化后的测试用例，我们来编写一个可以自动化执行所有代码覆盖的 python 脚本：import sys

```
import os
testcases = []
for root, dirs, files in os.walk(".", topdown=False):
    for name in files:
        if name.endswith(".xml"):
            testcase =  os.path.abspath(os.path.join(root, name))
            testcases.append(testcase)
for testcase in testcases:
    print "[*] Running DynamoRIO for testcase: ", testcase
    os.system("C:\DRIO7\bin32\drrun.exe -t drcov -- C:\xml_fuzz\xmlvalidate.exe %s" % testcase)
```

上面的脚本在我使用的用例里生成了下面的输出：

[![](https://p5.ssl.qhimg.com/t01ff9b6baea7292092.png)](https://p5.ssl.qhimg.com/t01ff9b6baea7292092.png)

和前面一样，使用 IDA 打开 File -&gt; Load File -&gt; Code Coverage File(s) 菜单下的所有 .log 文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012fde1ca6d6141bb5.png)

有趣的是，请注意存在多少个 parse 函数，如果你在覆盖范围内徘徊，将会看到我们已经设法得到了大量有趣的代码。<br>

由于我们确实得到了不错的代码覆盖率，让我们继续前进，最终 fuzz 它！

**<br>**

**我所做的就是 fuzz，fuzz，fuzz**

让我们启动 fuzzer：

```
afl-fuzz.exe -i C:minset_xml -o C:xml_results -D C:DRIObin32 -t 20000 -- -coverage_module MSXML6.dll -target_module xmlvalidate.exe -target_method main -nargs 2 -- C:xml_fuzzxmlvalidate.exe @@
```

运行上面的命令后得到下面的输出：

[![](https://p1.ssl.qhimg.com/t014e4d423a934f6f38.png)](https://p1.ssl.qhimg.com/t014e4d423a934f6f38.png)

正如你看到的，初始代码就是做这个工作，但速度非常慢。每三秒执行一次将消耗大量的时间才能得到正确的结果。有趣的是，我曾经就是在这种速度下（在 afl/winafl 时代之前，使用 python 和 radamsa），在三天的测试中发现了 bug！<br>

让我们尽可能地从拖慢 fuzz 速度的部分解脱出来。如果你曾经做过 Windows 编程，就会知道下面一行初始化了一个 COM 对象，这可能就是速度的瓶颈：

```
HRESULT hr = CoInitialize(NULL);
```

这一行确实是一个主要的问题，因此我们来重构代码，我们将创建一个 fuzzme 方法，该方法将在 COM 初始化调用之后接受文件名作为一个参数。重构的代码如下：

```
--- cut ---
extern "C" __declspec(dllexport) _bstr_t fuzzme(wchar_t* filename);
_bstr_t fuzzme(wchar_t* filename)
`{`
    _bstr_t bstrOutput = validateFile(filename);
    //bstrOutput += validateFile(L"nn-notValid.xml");
    //MessageBoxW(NULL, bstrOutput, L"noNamespace", MB_OK);
    return bstrOutput;
`}`
int main(int argc, char** argv)
`{`
    if (argc &lt; 2) `{`
        printf("Usage: %s &lt;xml file&gt;n", argv[0]);
        return 0;
    `}`
    HRESULT hr = CoInitialize(NULL);
    if (SUCCEEDED(hr))
    `{`
        try
        `{`
            _bstr_t bstrOutput = fuzzme(charToWChar(argv[1]));
        `}`
        catch (_com_error &amp;e)
        `{`
            dump_com_error(e);
        `}`
        CoUninitialize();
    `}`
    return 0;
`}`
--- cut ---
```

你可以从[这里](https://symeonp.github.io/assets/files/xmlvalidate.cpp)得到重构后的版本。使用重构的二进制文件我们来再一次运行 fuzzer，看看是否正确。这一次，我们将传递 fuzzme 作为 target_method，而不是 main，并且只使用一个参数，即文件名。这里，我们使用 lcamtuf 的 xml.dic，来自[这里](https://raw.githubusercontent.com/google/oss-fuzz/master/projects/libxml2/xml.dict)。

```
afl-fuzz.exe -i C:minset_xml -o C:xml_results -D C:DRIObin32 -t 20000 -x xml.dict -- -coverage_module MSXML6.dll -target_module xmlvalidate.exe -target_method fuzzme -nargs 1 -- C:xml_fuzzxmlvalidate.exe @@
```

一旦你运行脚本，在 VMWare 中几秒钟就出现了下面的输出：<br>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ba6de35c7b76bfc2.png)

好多了，现在我们让它运行起来然后等待崩溃吧！

**<br>**

**结果 – 崩溃分类和分析**

****通常，我会尝试用不同的测试用例来 fuzz 这个二进制文件，但幸运的是我不断得到 NULL pointer dereference 的 bug。下面的截图显示了大约 12 天后的结果：<br>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013df6ee2afffe0162.png)

请注意，总共执行了 33 万次，并发现了 26 次不同的崩溃！

为了给结果分类，我使用了 SkyLined 的 [Bugid](https://github.com/SkyLined/BugId) 工具，这是一个很棒的工具，能为你提供关于崩溃和崩溃利用的详细报告。

下面是我的 python 代码：

```
import sys
import os
sys.path.append("C:\BugId")
testcases = []
for root, dirs, files in os.walk(".\fuzzer01\crashes", topdown=False):
    for name in files:
        if name.endswith("00"):
            testcase =  os.path.abspath(os.path.join(root, name))
            testcases.append(testcase)
for testcase in testcases:
    print "[*] Gonna run: ", testcase
    os.system("C:\python27\python.exe C:\BugId\BugId.py C:\Users\IEUser\Desktop\xml_validate_results\xmlvalidate.exe -- %s" % testcase)
```

运行上面的脚本得到了下面的输出：<br>

[![](https://p4.ssl.qhimg.com/t0196373de3fd18f372.png)](https://p4.ssl.qhimg.com/t0196373de3fd18f372.png)

一旦我为所有得到的崩溃运行了它，可以很清楚的看到，我们命中的是相同的 bug。为了确认这一点，让我们打开 windbg：

```
0:000&gt; g
(a6c.5c0): Access violation - code c0000005 (!!! second chance !!!)
eax=03727aa0 ebx=0012fc3c ecx=00000000 edx=00000000 esi=030f4f1c edi=00000002
eip=6f95025a esp=0012fbcc ebp=0012fbcc iopl=0         nv up ei pl zr na pe nc
cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00010246
msxml6!DTD::findEntityGeneral+0x5:
6f95025a 8b4918          mov     ecx,dword ptr [ecx+18h] ds:0023:00000018=????????
0:000&gt; kv
ChildEBP RetAddr  Args to Child              
0012fbcc 6f9de300 03727aa0 00000002 030f4f1c msxml6!DTD::findEntityGeneral+0x5 (FPO: [Non-Fpo]) (CONV: thiscall) [d:w7rtmsqlxmlmsxml6xmldtddtd.hxx @ 236]
0012fbe8 6f999db3 03727aa0 00000003 030c5fb0 msxml6!DTD::checkAttrEntityRef+0x14 (FPO: [Non-Fpo]) (CONV: thiscall) [d:w7rtmsqlxmlmsxml6xmldtddtd.cxx @ 1470]
0012fc10 6f90508f 030f4f18 0012fc3c 00000000 msxml6!GetAttributeValueCollapsing+0x43 (FPO: [Non-Fpo]) (CONV: stdcall) [d:w7rtmsqlxmlmsxml6xmlparsenodefactory.cxx @ 771]
0012fc28 6f902d87 00000003 030f4f14 6f9051f4 msxml6!NodeFactory::FindAttributeValue+0x3c (FPO: [Non-Fpo]) (CONV: thiscall) [d:w7rtmsqlxmlmsxml6xmlparsenodefactory.cxx @ 743]
0012fc8c 6f8f7f0d 030c5fb0 030c3f20 01570040 msxml6!NodeFactory::CreateNode+0x124 (FPO: [Non-Fpo]) (CONV: stdcall) [d:w7rtmsqlxmlmsxml6xmlparsenodefactory.cxx @ 444]
0012fd1c 6f8f5042 010c3f20 ffffffff c4fd70d3 msxml6!XMLParser::Run+0x740 (FPO: [Non-Fpo]) (CONV: stdcall) [d:w7rtmsqlxmlmsxml6xmltokenizerparserxmlparser.cxx @ 1165]
0012fd58 6f8f4f93 030c3f20 c4fd7017 00000000 msxml6!Document::run+0x89 (FPO: [Non-Fpo]) (CONV: thiscall) [d:w7rtmsqlxmlmsxml6xmlomdocument.cxx @ 1494]
0012fd9c 6f90a95b 030ddf58 00000000 00000000 msxml6!Document::_load+0x1f1 (FPO: [Non-Fpo]) (CONV: thiscall) [d:w7rtmsqlxmlmsxml6xmlomdocument.cxx @ 1012]
0012fdc8 6f8f6c75 037278f0 00000000 c4fd73b3 msxml6!Document::load+0xa5 (FPO: [Non-Fpo]) (CONV: thiscall) [d:w7rtmsqlxmlmsxml6xmlomdocument.cxx @ 754]
0012fe38 00401d36 00000000 00000008 00000000 msxml6!DOMDocumentWrapper::load+0x1ff (FPO: [Non-Fpo]) (CONV: stdcall) [d:w7rtmsqlxmlmsxml6xmlomxmldom.cxx @ 1111]
-- cut --
```

[![](https://p1.ssl.qhimg.com/t01bc6452c64e0e9877.png)](https://p1.ssl.qhimg.com/t01bc6452c64e0e9877.png)

让我们来看一个造成崩溃的 xml：

```
C:UsersIEUserDesktopxml_validate_resultsfuzzer01crashes&gt;type id_000000_00
&lt;?xml version="&amp;a;1.0"?&gt;
&lt;book xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:noNamespaceSchemaLocation="nn.xsd"
      id="bk101"&gt;
   &lt;author&gt;Gambardella, Matthew&lt;/author&gt;
   &lt;title&gt;XML Developer's Guide&lt;/title&gt;
   &lt;genre&gt;Computer&lt;/genre&gt;
   &lt;price&gt;44.95&lt;/price&gt;
   &lt;publish_date&gt;2000-10-01&lt;/publish_date&gt;
   &lt;description&gt;An in-depth look at creating applications with
   XML.&lt;/description&gt;
```

正如你看到的，如果我们在 xml 或者其编码后提供了一些 garbage，就会得到上面的崩溃。Mitja 还将测试用例减到最小，如下所示：

```
&lt;?xml version='1.0' encoding='&amp;aaa;'?&gt;
```

对该库进行模糊测试的整个思想，是基于在 IE 上下文中找到一个漏洞并以某种方法触发它。经过一番搜索，让我们使用下面的 Poc（crashme.html），看看它是否会使 IE11 崩溃：

```
&lt;!DOCTYPE html&gt;
&lt;html&gt;
&lt;head&gt;
&lt;/head&gt;
&lt;body&gt;
&lt;script&gt;
var xmlDoc = new ActiveXObject("Msxml2.DOMDocument.6.0");
xmlDoc.async = false;
xmlDoc.load("crashme.xml");
if (xmlDoc.parseError.errorCode != 0) `{`
   var myErr = xmlDoc.parseError;
   console.log("You have error " + myErr.reason);
`}` else `{`
   console.log(xmlDoc.xml);
`}`
&lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
```

在 Python 的 SimpleHTTPServer 中运行它，提供下面的东西：

[![](https://p1.ssl.qhimg.com/t01f5e12a967f1b4e4e.png)](https://p1.ssl.qhimg.com/t01f5e12a967f1b4e4e.png)

Bingo！正如预期的那样，至少在启用了 PageHeap 的情况下，我们能够触发与我们在测试框架中相同的崩溃。小心不要在 Microsoft Outlook 中包含该 xml，因为它也会崩溃！此外，由于它基于库本身，如果产生一个更 sexy 的崩溃，则会增加攻击面！

**<br>**

**打补丁**

在与 Mitja 通过电子邮件交流后，他向我提供了可以在完全更新的 x64 系统上使用的补丁：

```
;target platform: Windows 7 x64
;
RUN_CMD C:UserssymeonDesktopxmlvalidate_64bitxmlvalidate.exe C:UserssymeonDesktopxmlvalidate_64bitpoc2.xml
MODULE_PATH "C:WindowsSystem32msxml6.dll"
PATCH_ID 200000
PATCH_FORMAT_VER 2
VULN_ID 9999999
PLATFORM win64
patchlet_start
 PATCHLET_ID 1
 PATCHLET_TYPE 2
 
 PATCHLET_OFFSET 0xD093D 
 PIT msxml6.dll!0xD097D
  
 code_start
  test rbp, rbp ;is rbp (this) NULL?
  jnz continue
  jmp PIT_0xD097D
  continue:
 code_end
patchlet_end
```

我们来调试和测试下这个补丁程序，我已经创建了一个账户，并未开发者安装了 0patch 代理，右击上述的 .0pp 文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018fb3f6ecd31fdd8b.png)

一旦在测试框架中使用了可以导致崩溃的 xml，我立即设置断点：

[![](https://p0.ssl.qhimg.com/t015f408ef2f2b2be69.png)](https://p0.ssl.qhimg.com/t015f408ef2f2b2be69.png)

从上面的代码中看到，rbp 寄存器确实是 null，这将导致 null pointer dereference 的问题。由于我们已经部署了 0patch 代理，实际上它会跳转到 msxml6.dll!0xD097D，从而避免崩溃：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01644e59145d171863.png)

太棒了！接下来我在修复后的版本上再次启动 winafl，但是不幸失败了。由于 0patch（钩子函数？）的性质，它与 WinAFL 不兼容，于是崩溃了。

然而，这是一种“DoS 0day”，正如我之前提到的，我在2017年6月向微软提出报告，二十天后收到一下邮件：

[![](https://p5.ssl.qhimg.com/t01487dd7ec4062c727.png)](https://p5.ssl.qhimg.com/t01487dd7ec4062c727.png)

我完全同意这一决定，但我最感兴趣的还是修补掉这个烦人的 bug，以便我可以继续前进。在调试器上花了几个小时之后，我发现唯一可控制的用户输入是编码字符串的长度：

```
eax=03052660 ebx=0012fc3c ecx=00000011 edx=00000020 esi=03054f24 edi=00000002
eip=6f80e616 esp=0012fbd4 ebp=0012fbe4 iopl=0         nv up ei pl zr na pe nc
cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246
msxml6!Name::create+0xf:
6f80e616 e8e7e6f9ff      call    msxml6!Name::create (6f7acd02)
0:000&gt; dds esp L3
0012fbd4  00000000
0012fbd8  03064ff8
0012fbdc  00000003
0:000&gt; dc 03064ff8 L4
03064ff8  00610061 00000061 ???????? ????????  a.a.a...????????
```

上面的 unicode 字符串其实是来自我们测试用例的开头，其中数字 3 很明显是长度（函数的签名：Name *__stdcall Name::create(String *pS, const wchar_t *pch, int iLen, Atom *pAtomURN)）

**<br>**

**结论**

如你所见，花一些时间在微软的 API 和文档上是非常值得的！另外，重构一些基本函数并精确定位影响性能的问题也可能对我们的工作有很大的改进！

我必须感谢 lvan 将 afl 移植到 Windows 并创建了这个令人吃惊的项目。也感谢 Axel 和其他一直积极做贡献的人。

我的同事 Javier 激励我写了这篇博客，Richard 一直在回答我愚蠢的问题，并给我所有的帮助，来自 0patch 的 Mitja 建立了这个补丁，最后 Patroklo 几年前教了我一些模糊测试的技巧！

**<br>**

**参考**

[Evolutionary Kernel Fuzzing-BH2017-rjohnson-FINAL.pdf](https://github.com/richinseattle/EvolutionaryKernelFuzzing/blob/master/slides/Evolutionary%20Kernel%20Fuzzing-BH2017-rjohnson-FINAL.pdf)

[Super Awesome Fuzzing, Part One](https://labsblog.f-secure.com/2017/06/22/super-awesome-fuzzing-part-one/)

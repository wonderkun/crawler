> 原文链接: https://www.anquanke.com//post/id/229718 


# Battleye 系列翻译之分析与简化


                                阅读量   
                                **196658**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者secret，文章来源：secret.club
                                <br>原文地址：[https://secret.club/2019/02/10/battleye-anticheat.html](https://secret.club/2019/02/10/battleye-anticheat.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t018335ea289a484822.png)](https://p2.ssl.qhimg.com/t018335ea289a484822.png)



## 写在译文之前：

—最近在学习游戏安全相关内容，然后我发现，在游戏破解，数据分析，逻辑逆向方面的文章，前辈们写的很多，有许多可以学习的地方了，但是对于反作弊系统的研究，主要还是以英文文献为主。

—所以我在学习时，就在想顺便做一个翻译，将自己学习到的文章都翻译成中文，方便一些英语不好的同学阅读，同时也是对自己知识的一次巩固。

—翻译是在百度翻译的基础上带上我自己的修修补补，如果翻译有错误、不当的地方，还请多多谅解。



## 原文链接:

[BattlEye anti-cheat: analysis and mitigation](https://secret.club/2019/02/10/battleye-anticheat.html)



## 译文：

BattlEye（以下简称BE）是一款流行的德国第三方反作弊软件，主要由32岁的创始人Bastian Heiko Suter开发。它为游戏发行商提供易于使用的反作弊解决方案。通过使用通用保护机制和特定于游戏的检测来为游戏提供最佳的保护（至少是在尝试这么做）。正如他们的网站所说，他们始终掌握最先进的技术，并采用创新的保护和检测方法，这显然是由于他们的国民品质：德国制造。BE由多个部分组成，这些部分在各自的游戏中协同工作，从而帮助那些给他们付钱的游戏厂商抓住或者防御作弊者。

BE的主要的四个部分为：
- BEService：是一个和BEServer产生通信的Windows系统服务，该服务为BEDaisy和BEClient提供了服务器到客户端的通讯的能力。
- BEDaisy：是一种防止寄存器回调的Windows内核驱动，也是一种防止作弊者非法修改游戏的微型过滤器。
- BEClient：是一个Windows动态链接库，负责了大部分对检测向量，包括本文提到的。它会在游戏进程初始化后映射。
- BEServer：专有的后端服务器，负责收集信息和采取具体行动打击作弊者。
#### <a class="reference-link" name="shellcode"></a>shellcode

最近，一份BE的shellcode dump出现在互联网上，我们决定对BE正在积极寻找的内容进行一次总结。我们已经6个月没有在BE上工作了，所以上一次的dump出的shellcode很可能已经过时了。在最近的dump中，代码的其他部分完全从内存中识别出来，这表明BE只是对shellcode进行了追加，并没有删除以前的检测过程。

#### <a class="reference-link" name="how"></a>how

BE大概是将它的shellcode从它的服务器上以流的形式传输至Windows服务上，即BEService。这个服务与位于游戏进程内部的BE模块进行通信，即与BEClient进行通讯。这个通信是通过命名管道`\\.\namedpipe\Battleye`进行通讯，这个通讯直到去年位置，还没有被加密，而现在，所有通讯都通过一个密钥非常小的异或进行加密，这种加密使得已知明文攻击变得无力。当shellcode流式传输至客户端时，它会将在任何已知模块之外进行分配和执行，从而容易被我们所区分。为了dump这段shellcode，你可以挂载流行的windows-api函数，如CreateFile, ReadFile等等，并dump所有调用了这些函数的调用方的各自的内存区域（通过返回地址来查询内存信息），这些内存区域应该不属于任何已知模块。或者通过周期性扫描游戏的虚拟内存空间，寻找任何不是已知模块的可执行内存，并且把它dump出来。记得一定要保持对你已经dump出得内存的跟踪，这样你才不会在成千上万的相同的dump中放弃。

#### <a class="reference-link" name="%E5%85%8D%E8%B4%A3%E5%A3%B0%E6%98%8E"></a>免责声明

下面的伪代码片段已经经过大量美化。您将无法从BEdump出的shellcode中立即识别其中的一部分。shellcode不包含任何函数调用，并且许多算法都没有展开。这实际上并不重要，因为当你读完这些反作弊手段后，你就会在绕过的方法上有自己的想法了。（：

#### <a class="reference-link" name="Memory%20Enumeration"></a>Memory Enumeration

反作弊方案最常用的检测机制是内存枚举和内存扫描，用于检测已知的作弊映像。它很容易实现，并且在正确完成时非常有效，只要您别忘记基本的组装和将通常的函数开头列入黑名单，就像我们在过去看到的那样。<br>
Battleye枚举游戏进程的整个地址空间（当前进程接下来的上下文）。当页可执行且在各自的shellcode内存空间外时，BE会执行各种检查。<br>
下面是内存枚举的实现：

```
// MEMORY ENUMERATION
for (current_address = 0;
    // QUERY MEMORY_BASIC_INFORMATION
    NtQueryVirtualMemory(GetCurrentProcess(), current_address, 0, &amp;memory_information, 0x30, &amp;return_length) &gt;= 0; 
    current_address = memory_information.base_address + memory_information.region_size) 
`{`

    const auto outside_of_shellcode = 
        memory_information.base_address &gt; shellcode_entry || 
        memory_information.base_address + memory_information.region_size &lt;= shellcode_entry;

    const auto executable_memory = 
        memory_information.state == MEM_COMMIT &amp;&amp;
        (memory_information.protect == PAGE_EXECUTE ||
        memory_information.protect == PAGE_EXECUTE_READ ||
        memory_information.protect == PAGE_EXECUTE_READWRITE);

    const auto unknown_whitelist = 
        memory_information.protect != PAGE_EXECUTE_READWRITE || 
        memory_information.region_size != 100000000;

    if (!executable_memory || !outside_of_shellcode || !unknown_whitelist)
        continue;

    // RUN CHECKS
    memory::anomaly_check(memory_information);

    memory::pattern_check(current_address, memory_information);

    memory::module_specific_check_microsoft(memory_information);

    memory::guard_check(current_address, memory_information);

    memory::module_specific_check_unknown(memory_information);
`}`
```

#### <a class="reference-link" name="Memory%20anomaly"></a>Memory anomaly

BE会标记任何内存空间中的异常，主要是加载的映像与实际的可执行内存不对应的情况。

```
void memory::anomaly_check(MEMORY_BASIC_INFORMATION memory_information)
`{`
    // REPORT ANY EXECUTABLE PAGE OUTSIDE OF KNOWN MODULES
    if (memory_information.type == MEM_PRIVATE || memory_information.type == MEM_MAPPED) 
    `{`
        if ((memory_information.base_address &amp; 0xFF0000000000) != 0x7F0000000000 &amp;&amp; // UPPER EQUALS 0x7F
            (memory_information.base_address &amp; 0xFFF000000000) != 0x7F000000000 &amp;&amp;  // UPPER EQUALS 0x7F0
            (memory_information.base_address &amp; 0xFFFFF0000000) != 0x70000000 &amp;&amp; // UPPER EQUALS 0x70000
            memory_information.base_address != 0x3E0000))
        `{`
            memory_report.unknown = 0;
            memory_report.report_id = 0x2F;
            memory_report.base_address = memory_information.base_address;
            memory_report.region_size = memory_information.region_size;
            memory_report.memory_info = 
                memory_information.type | 
                memory_information.protect | 
                memory_information.state;

            battleye::report(&amp;memory_report, sizeof(memory_report), 0);
        `}`
    `}`
`}`
```

#### <a class="reference-link" name="Pattern%20scans"></a>Pattern scans

正如之前所说，BE会对本地进程的内存进行扫描，寻找各种硬编码。如下列实现的硬编码。当你读到下列伪代码时你应该意识到，你可以通过覆写已加载的模块来绕过这些检查，因为它们不会对已知的映像进行任何匹配扫描。为了不被完整性检查命中，在加载任何打包的、白名单的模块时，要将代码段标记为RWX，因为你无法在没有模拟打包的情况下完成一致性检验。当前版本的BEshellcodee对以下硬编码进行了内存匹配。

```
[05 18] ojects\PUBGChinese
[05 17] BattleGroundsPrivate_CheatESP
[05 17] [%.0fm] %s
[05 3E] \00\00\00\00Neck\00\00\00\00Chest\00\00\00\00\00\00\00Mouse 1\00
[05 3F] PlayerESPColor
[05 40]  Aimbot: %d\00\2D\3E\20\41
[05 36] HackMachine
[05 4A] VisualHacks.net
[05 50] \3E\23\2F\65\3E\31\31\4E\4E\56\3D\42\76\28\2A\3A\2E\46\3F\75\75\23\28\67\52\55\2E\6F\30\58\47\48
[05 4F] DLLInjection-master\\x64\\Release\\
[05 52] NameESP
[05 48] Skullhack
[05 55] .rdata$zzzdbg
[05 39] AimBot
[05 39] \EB\49\41\80\3C\12\3F\75\05\C6\02\3F\EB\38\8D\41\D0\0F\BE\C9\3C\09\77\05\83\E9\30\EB\06\83\E1\DF
[05 5F] \55\E9
[05 5F] \57\E9
[05 5F] \60\E9
[05 68] D3D11Present initialised
[05 6E] [ %.0fM ]
[05 74] [hp:%d]%dm
[05 36] \48\83\64\24\38\00\48\8D\4C\24\58\48\8B\54\24\50\4C\8B\C8\48\89\4C\24\30\4C\8B\C7\48\8D\4C\24\60
[05 36] \74\1F\BA\80\00\00\00\FF\15\60\7E\00\00\85\C0\75\10\F2\0F\10\87\80\01\00\00\8B\87\88\01\00\00\EB
[05 36] \40\F2\AA\15\6F\08\D2\89\4E\9A\B4\48\95\35\D3\4F\9CPOSITION\00\00\00\00COL
[05 7A] \FF\E0\90
[05 79] %s\00\00%d\00\00POSITION\00\00\00\00COLOR\00\00\00\00\00\00\00
[05 36] \8E\85\76\5D\CD\DA\45\2E\75\BA\12\B4\C7\B9\48\72\11\6D\B9\48\A1\DA\A6\B9\48\A7\67\6B\B9\48\90\2C
[05 8A] \n&lt;assembly xmlsn='urn:schemas-mi

```

这些内存匹配还包含一个两字节头，分别是一个未知静态值05和一个唯一标识符。在这里您不会看到的是，BBE还动态地从BEServer流式传输匹配字符串，并将它们发送到BEClient，但在本文中我们将不讨论这些。<br>
通过以下算法迭代扫描：

```
void memory::pattern_check(void* current_address, MEMORY_BASIC_INFORMATION memory_information)
`{`
    const auto is_user32 = memory_information.allocation_base == GetModuleHandleA("user32.dll");

    // ONLY SCAN PRIVATE MEMORY AND USER32 CODE SECTION
    if (memory_information.type != MEM_PRIVATE &amp;&amp; !is_user32) 
        continue;

    for (address = current_address; 
         address != memory_information.base_address + memory_information.region_size; 
         address += PAGE_SIZE) // PAGE_SIZE
    `{`
        // READ ENTIRE PAGE FROM LOCAL PROCESS INTO BUFFER
        if (NtReadVirtualMemory(GetCurrentProcess(), address, buffer, PAGE_SIZE, 0) &lt; 0)
            continue;

        for (pattern_index = 0; pattern_index &lt; 0x1C/*PATTERN COUNT*/; ++pattern_index)
        `{`
            if (pattern[pattern_index].header == 0x57A &amp;&amp; !is_user32) // ONLY DO \FF\E0\90 SEARCHES WHEN IN USER32
                continue;

            for (offset = 0; pattern[pattern_index].length + offset &lt;= PAGE_SIZE; ++offset) 
            `{`
                const auto pattern_matches = 
                    memory::pattern_match(&amp;address[offset], pattern[pattern_index]); //    BASIC PATTERN MATCH

                if (pattern_matches) 
                `{`
                    // PATTERN FOUND IN MEMORY
                    pattern_report.unknown = 0;
                    pattern_report.report_id = 0x35;
                    pattern_report.type = pattern[index].header;
                    pattern_report.data = &amp;address[offset];
                    pattern_report.base_address = memory_information.base_address;
                    pattern_report.region_size = memory_information.region_size;
                    pattern_report.memory_info = 
                        memory_information.type | 
                        memory_information.protect | 
                        memory_information.state;

                    battleye::report(&amp;pattern_report, sizeof(pattern_report), 0);
                `}`
            `}`
        `}`
    `}`
`}`
```

#### <a class="reference-link" name="Module%20specific%20(Microsoft)"></a>Module specific (Microsoft)

当你将特定模块加载到游戏进程中，模块特定检查将会报告

```
void memory::module_specific_check_microsoft(MEMORY_BASIC_INFORMATION memory_information)
`{`
    auto executable = 
        memory_information.protect == PAGE_EXECUTE || 
        memory_information.protect == PAGE_EXECUTE_READ || 
        memory_information.protect == PAGE_EXECUTE_READWRITE;

    auto allocated = 
        memory_information.state == MEM_COMMIT;

    if (!allocated || !executable)
        continue;

    auto mmres_handle = GetModuleHandleA("mmres.dll");
    auto mshtml_handle = GetModuleHandleA("mshtml.dll");

    if (mmres_handle &amp;&amp; mmres_handle == memory_information.allocation_base)
    `{`
        battleye_module_anomaly_report module_anomaly_report;
        module_anomaly_report.unknown = 0;
        module_anomaly_report.report_id = 0x5B;
        module_anomaly_report.identifier = 0x3480;
        module_anomaly_report.region_size = memory_information.region_size;
        battleye::report(&amp;module_anomaly_report, sizeof(module_anomaly_report), 0);   
    `}`
    else if (mshtml_handle &amp;&amp; mshtml_handle == memory_information.allocation_base)
    `{`
        battleye_module_anomaly_report module_anomaly_report;
        module_anomaly_report.unknown = 0;
        module_anomaly_report.report_id = 0x5B;
        module_anomaly_report.identifier = 0xB480;
        module_anomaly_report.region_size = memory_information.region_size;
        battleye::report(&amp;module_anomaly_report, sizeof(module_anomaly_report), 0);  
    `}`
`}`
```

#### <a class="reference-link" name="Module%20specific%20(Unknown)"></a>Module specific (Unknown)

添加了一个非常具体的模块检查，如果加载的模块满足以下任何条件，该检查将向服务器报告。

```
void memory::module_specific_check_unknown(MEMORY_BASIC_INFORMATION memory_information)
`{`
    const auto dos_header = (DOS_HEADER*)module_handle;
    const auto pe_header = (PE_HEADER*)(module_handle + dos_header-&gt;e_lfanew));

    const auto is_image = memory_information.state == MEM_COMMIT &amp;&amp; memory_information.type == MEM_IMAGE;
    if (!is_image)
        return;

    const auto is_base = memory_information.base_address == memory_information.allocation_base;
    if (!is_base)
        return;

    const auto match_1 = 
        time_date_stamp == 0x5B12C900 &amp;&amp; 
        *(__int8*)(memory_information.base_address + 0x1000) == 0x00 &amp;&amp;
        *(__int32*)(memory_information.base_address + 0x501000) != 0x353E900;

    const auto match_2 = 
        time_date_stamp == 0x5A180C35 &amp;&amp; 
        *(__int8*)(memory_information.base_address + 0x1000) != 0x00;

    const auto match_2 = 
        time_date_stamp == 0xFC9B9325 &amp;&amp; 
        *(__int8*)(memory_information.base_address + 0x6D3000) != 0x00;

    if (!match_1 &amp;&amp; !match_2 &amp;&amp; !match_3)
        return;

    const auto buffer_offset = 0x00; // OFFSET DEPENDS ON WHICH MODULE MATCHES, RESPECTIVELY 0x501000, 0x1000 AND 0x6D3000

    unknown_module_report.unknown1 = 0;
    unknown_module_report.report_id = 0x46;
    unknown_module_report.unknown2 = 1;
    unknown_module_report.data = *(__int128*)(memory_information.base_address + buffer_offset); 
    battleye::report(&amp;unknown_module_report, sizeof(unknown_module_report), 0);
`}`
```

我们不知道哪些模块符合这些标准，但怀疑这是一个试图检测极少数，具体作弊模块。<br>
编辑：[@how02](https://github.com/how02)提醒我们，模块action_x64.dll的时间戳为0x5B12C900，并且包含一个可写的代码段，如前所述，该代码段可被利用。

#### <a class="reference-link" name="Memory%20guard"></a>Memory guard

BE还加入了一个非常可疑的检测例程，我们认为该例程使用标志PAGE_GUARD查找内存，而没有实际检查PAGE_GUARD标志是否设置

```
void memory::guard_check(void* current_address, MEMORY_BASIC_INFORMATION memory_information)
`{`
    if (memory_information.protect != PAGE_NOACCESS)
    `{`
        auto bad_ptr = IsBadReadPtr(current_address, sizeof(temporary_buffer));
        auto read = NtReadVirtualMemory(
            GetCurrentProcess(), 
            current_address, 
            temporary_buffer, sizeof(temporary_buffer), 
            0);

        if (read &lt; 0 || bad_ptr)
        `{`
            auto query = NtQueryVirtualMemory(
                GetCurrentProcess(), 
                current_address, 
                0, 
                &amp;new_memory_information, sizeof(new_memory_information), 
                &amp;return_length);

            memory_guard_report.guard = 
                    query &lt; 0 || 
                    new_memory_information.state != memory_information.state || 
                    new_memory_information.protect != memory_information.protect;

            if (memory_guard_report.guard)
            `{`
                memory_guard_report.unknown = 0;
                memory_guard_report.report_id = 0x21;
                memory_guard_report.base_address = memory_information.base_address;
                memory_guard_report.region_size = (int)memory_information.region_size;
                memory_guard_report.memory_info = 
                    memory_information.type | 
                    memory_information.protect | 
                    memory_information.state;

                battleye::report(&amp;memory_guard_report, sizeof(memory_guard_report), 0);
            `}`
        `}`
    `}`
`}`
```

#### <a class="reference-link" name="Window%20enumeration"></a>Window enumeration

BattlEye的shellcode枚举了游戏运行时当前可见的每个窗口，它是通过自顶向下（z值）迭代窗口来实现的。根据GetWindowThreadProcessId调用的确定，游戏进程内部的窗口句柄被排除在上述枚举之外。因此，可以钩住相应的函数来欺骗窗口的所有权，并防止BattlEye枚举窗口。

```
void window_handler::enumerate()
`{`
    for (auto window_handle = GetTopWindow();
         window_handle; 
         window_handle = GetWindow(window_handle, GW_HWNDNEXT), // GET WINDOW BELOW
         ++window_handler::windows_enumerated)                  // INCREMENT GLOBAL COUNT FOR LATER USAGE
    `{`
        auto window_process_pid = 0;
        GetWindowThreadProcessId(window_handle, &amp;window_process_pid);

        if (window_process_pid == GetCurrentProcessId())
            continue;

        // APPEND INFORMATION TO THE MISC. REPORT, THIS IS EXPLAINED LATER IN THE ARTICLE
        window_handler::handle_summary(window_handle);

        constexpr auto max_character_count = 0x80;
        const auto length = GetWindowTextA(window_handle, window_title_report.window_title, max_character_count);

        // DOES WINDOW TITLE MATCH ANY OF THE BLACKLISTED TITLES?
        if (!contains(window_title_report.window_title, "CheatAut") &amp;&amp;
            !contains(window_title_report.window_title, "pubg_kh") &amp;&amp;
            !contains(window_title_report.window_title, "conl -") &amp;&amp;
            !contains(window_title_report.window_title, "PerfectA") &amp;&amp;
            !contains(window_title_report.window_title, "AIMWA") &amp;&amp;
            !contains(window_title_report.window_title, "PUBG AIM") &amp;&amp;
            !contains(window_title_report.window_title, "HyperChe"))
            continue;

        // REPORT WINDOW
        window_title_report.unknown_1 = 0;
        window_title_report.report_id = 0x33;
        battleye::report(&amp;window_title_report, sizeof(window_title_report) + length, 0);
    `}`
`}`
```

#### <a class="reference-link" name="Anomaly%20in%20enumeration"></a>Anomaly in enumeration

如果枚举的窗口少于两个，则会通知服务器。这样做可能是为了防止有人修补相应的功能，防止任何窗口被BattlEye的shellcode看到

```
void window_handler::check_count()
`{`
    if (window_handler::windows_enumerated &gt; 1)
        return;

    // WINDOW ENUMERATION FAILED, MOST LIKELY DUE TO HOOK
    window_anomaly_report.unknown_1 = 0;
    window_anomaly_report.report_id = 0x44;
    window_anomaly_report.enumerated_windows = windows_enumerated;
    battleye::report(&amp;window_anomaly_report, sizeof(window_anomaly_report), 0);

`}`
```

#### <a class="reference-link" name="Process%20enumeration"></a>Process enumeration

BattlEye使用CreateToolhelp32Snapshot调用枚举所有正在运行的进程，但不处理任何错误，因此很容易修补和阻止以下任何检测例程

#### <a class="reference-link" name="Path%20check"></a>Path check

如果映像位于至少两个子目录（从磁盘根目录）中，如果相应的映像路径至少包含以下字符串之一，它将标记进程：

```
\Desktop\
\Temp\
\FileRec
\Documents\
\Downloads\
\Roaming\
tmp.ex
notepad.
...\\.
cmd.ex
```

如果可执行路径与这些字符串中的一个匹配，则服务器将收到可执行路径的通知，以及有关父进程是否为以下之一的信息（包含发送到服务器的相应标志位）：

```
steam.exe       [0x01]
explorer.exe    [0x02]
lsass.exe       [0x08]
cmd.exe         [0x10]
```

如果客户端无法打开具有相应QueryLimitedInformation权限的句柄，那么如果OpenProcess调用失败的错误原因不等于ERROR_ACCESS_DENIED，它将设置标志位0x04，这将为相应标志值提供最终枚举容器：

```
enum BATTLEYE_PROCESS_FLAG
`{`
  STEAM     = 0x1,
  EXPLORER  = 0x2,
  ERROR     = 0x4,
  LSASS     = 0x8,
  CMD       = 0x10
`}`
```

如果steam是父进程，您将立即被标记为ID 40并报告给服务器。

#### <a class="reference-link" name="Image%20name"></a>Image name

如果您的进程符合下面的任何其他条件，您将立即被标记并报告给报告id为0x38的服务器

```
Image name contains "Loadlibr"
Image name contains "Rng "
Image name contains "\A0\E7\FF\FF\FF\81"
Image name contains "RNG "
Image name contains "\90\E5\43\55"
Image name contains "2.6.ex"
Image name contains "TempFile.exe"
```

#### <a class="reference-link" name="Steam%20game%20overlay"></a>Steam game overlay

BE一直关注着steam游戏覆盖进程，它负责大多数steam用户知道的游戏内覆盖。steam游戏覆盖主机的完整映像的名称是gameoverlayui.exe并且被用于渲染目的，这使得劫持和恶意绘制游戏窗口是简单。BE的检查的条件是：

```
file size != 0 &amp;&amp; image name contains (case insensitive) gameoverlayu
```

以下针对steam游戏覆盖的检查与在游戏进程本身上运行的例程几乎相同，因此伪代码中省略了这些检查。

#### <a class="reference-link" name="Steam%20Game%20Overlay%20memory%20scan"></a>Steam Game Overlay memory scan

steam游戏覆盖进程将扫描内存中的匹配和异常。我们无法进一步深入，找出这些模式的用途，因为它们非常通用，可能与作弊模块有关。

```
void gameoverlay::pattern_scan(MEMORY_BASIC_INFORMATION memory_information)
`{`
    // PATTERNS:
    // Home
    // F1
    // \FF\FF\83\C4\08\C3\00\00\00\00\00\00\00\00\00\00
    // \\.\pipe\%s
    // \C7\06\00\00\00\00\C6\47\03\00
    // \60\C0\18\01\00\00\33\D2

    // ... 
    // PATTERN SCAN, ALMOST IDENTICAL CODE TO THE AFOREMENTIONED PATTERN SCANNING ROUTINE

    gameoverlay_memory_report.unknown_1 = 0;
    gameoverlay_memory_report.report_id = 0x35;
    gameoverlay_memory_report.identifier = 0x56C;
    gameoverlay_memory_report.data = &amp;buffer[offset];
    gameoverlay_memory_report.base_address = memory_information.base_address;
    gameoverlay_memory_report.region_size = (int)memory_information.region_size;
    gameoverlay_memory_report.memory_info = 
        memory_information.type | 
        memory_information.protect | 
        memory_information.state;

    battleye::report(&amp;gameoverlay_memory_report, sizeof(gameoverlay_memory_report), 0);
`}`
```

扫描例程还会在加载的映像之外以可执行内存的形式查找任何异常，这表明入侵者已将代码注入覆盖进程。

```
void gameoverlay::memory_anomaly_scan(MEMORY_BASIC_INFORMATION memory_information)
`{`  
    // ...
    // ALMOST IDENTICAL ANOMALY SCAN COMPARED TO MEMORY ENUMERATION ROUTINE OF GAME PROCESS

    gameoverlay_report.unknown = 0;
    gameoverlay_report.report_id = 0x3B;
    gameoverlay_report.base_address = memory_information.base_address;
    gameoverlay_report.region_size = memory_information.region_size;
    gameoverlay_report.memory_info = memory_information.type | memory_information.protect | memory_information.state;
    battleye::report(&amp;gameoverlay_report, sizeof(gameoverlay_report), 0);
`}`
```

#### <a class="reference-link" name="Steam%20Game%20Overlay%20process%20protection"></a>Steam Game Overlay process protection

如果steam游戏覆盖进程已使用任何windows进程保护（如Light（WinTcb））进行保护，服务器将收到通知。

```
void gameoverlay::protection_check(HANDLE process_handle)
`{`
    auto process_protection = 0;

    NtQueryInformationProcess(
        process_handle, ProcessProtectionInformation, 
        &amp;process_protection, sizeof(process_protection), nullptr);

    if (process_protection == 0) // NO PROTECTION
        return;

    gameoverlay_protected_report.unknown = 0;
    gameoverlay_protected_report.report_id = 0x35;
    gameoverlay_protected_report.identifier = 0x5B1;
    gameoverlay_protected_report.data = process_protection;
    battleye::report(&amp;gameoverlay_protected_report, sizeof(gameoverlay_protected_report), 0);
```

如果对上述游戏覆盖进程的相应OpenProcess调用返回ERROR_ACCESS_DENIED，您还将会被报告id3b给服务器。

#### <a class="reference-link" name="Module%20enumeration"></a>Module enumeration

shellcode还列举了steam游戏覆盖过程的模块，特别是寻找vgui2_s.dll和gameoverlayui.dll. 对这些模块进行了一定的检查，首先是gameoverlayui.dll.

如果匹配这条件：

```
[gameoverlayui.dll+6C779] == \00\8B\E5\5D\C3\CC\CC\B8\??\??\??\??\C3\CC\CC\CC
```

shellcode将扫描存储在字节中的地址处的vtable`\??\??\??\??`，如果这些vtable条目中的任何一个超出了原始gameoverlayui.dll模块或指向int 3指令，您将被报告为id 3B。

```
void gameoverlay::scan_vtable(HANDLE process_handle, char* buffer, MODULEENTRY32 module_entry)
`{`
    char function_buffer[16];

    for (vtable_index = 0; vtable_index &lt; 20; vtable_index += 4)
    `{`
        NtReadVirtualMemory(
          process_handle,
          *(int*)&amp;buffer[vtable_index],
          &amp;function_buffer,
          sizeof(function_buffer),
          0);

        if (*(int*)&amp;buffer[vtable_index] &lt; module_entry.modBaseAddr ||
            *(int*)&amp;buffer[vtable_index] &gt;= module_entry.modBaseAddr + module_entry.modBaseSize ||
            function_buffer[0] == 0xCC )    // FUNCTION PADDING
        `{`
            gameoverlay_vtable_report.report_id = 0x3B;
            gameoverlay_vtable_report.vtable_index = vtable_index;
            gameoverlay_vtable_report.address = buffer[vtable_index];
            battleye::report(&amp;gameoverlay_vtable_report, sizeof(gameoverlay_vtable_report), 0);
        `}`
    `}`
`}`
```

vgui2_s.dll模块还设置了一个特定的检查例程：

```
void vgui::scan()
`{`
    if (!equals(vgui_buffer, "\6A\00\8B\31\FF\56\1C\8B\0D\??\??\??\??\??\FF\96\??\??\??\??\8B\0D\??\??\??\??\8B\01\FF\90"))
    `{`
        auto could_read = NtReadVirtualMemory(
            process_handle, module_entry.modBaseAddr + 0x48338, vgui_buffer, 8, 0) &gt;= 0;

        constexpr auto pattern_offset = 0x48378;

        // IF READ DID NOT FAIL AND PATTERN IS FOUND
        if (could_read &amp;&amp; equals(vgui_buffer, "\6A\04\6A\00\6A\02\6A"))
        `{`
            vgui_report.unknown_1 = 0;
            vgui_report.report_id = 0x3B;
            vgui_report.unknown_2 = 0;
            vgui_report.address = LODWORD(module_entry.modBaseAddr) + pattern_offset;

            // READ TARGET BUFFER INTO REPORT
            NtReadVirtualMemory(
              process_handle,
              module_entry.modBaseAddr + pattern_offset,
              vgui_report.buffer,
              sizeof(vgui_report.buffer),
              0);

            battleye::report(&amp;vgui_report, sizeof(vgui_report), 0);
        `}`
    `}`
    else if (
            // READ ADDRESS FROM CODE
            NtReadVirtualMemory(process_handle, *(int*)&amp;vgui_buffer[9], vgui_buffer, 4, 0) &gt;= 0 &amp;&amp;
            // READ POINTER TO CLASS
            NtReadVirtualMemory(process_handle, *(int*)vgui_buffer, vgui_buffer, 4, 0) &gt;= 0 &amp;&amp; 
            // READ POINTER TO VIRTUAL TABLE
            NtReadVirtualMemory(process_handle, *(int*)vgui_buffer, vgui_buffer, sizeof(vgui_buffer), 0) &gt;= 0)
    `{`
        for (vtable_index = 0; vtable_index &lt; 984; vtable_index += 4 )      // 984/4 VTABLE ENTRY COUNT
        `{`
            NtReadVirtualMemory(process_handle, *(int*)&amp;vgui_buffer[vtable_index], &amp;vtable_entry, sizeof(vtable_entry), 0);

            if (*(int*)&amp;vgui_buffer[vtable_index] &lt; module_entry.modBaseAddr ||
                *(int*)&amp;vgui_buffer[vtable_index] &gt;= module_entry.modBaseAddr + module_entry.modBaseSize ||
                vtable_entry == 0xCC )
            `{`
                vgui_vtable_report.unknown = 0;
                vgui_vtable_report.report_id = 0x3B;
                vgui_vtable_report.vtable_index = vtable_index;
                vgui_vtable_report.address = *(int*)&amp;vgui_buffer[vtable_index];
                battleye::report(&amp;vgui_vtable_report, sizeof(vgui_vtable_report), 0);
            `}`
        `}`
    `}`
`}`
```

先前的例行检查是在`0x48378`处进行修改，这是代码部分中的一个位置：

```
push    04
push    offset aCBuildslaveSte_4 ; "c:\\buildslave\\steam_rel_client_win32"...
push    offset aAssertionFaile_7 ; "Assertion Failed: IsValidIndex(elem)"
```

然后，例程检查一个非常具体的、看似垃圾的修改：

```
push    04
push    00
push    02
push    ??
```

我们无法获得与前面两个检查中的第一个不匹配的vgui2_s.dll副本，因此无法讨论它正在检查哪个vtable。

#### <a class="reference-link" name="Steam%20Game%20Overlay%20threads"></a>Steam Game Overlay threads

steam游戏覆盖进程中的线程也被枚举：

```
void gameoverlay::check_thread(THREADENTRY32 thread_entry)
`{`
    const auto tread_handle = OpenThread(THREAD_SUSPEND_RESUME|THREAD_GET_CONTEXT, 0, thread_entry.th32ThreadID);
    if (thread_handle)
    `{`
        suspend_count = ResumeThread(thread_handle);
        if (suspend_count &gt; 0)
        `{`
            SuspendThread(thread_handle);
            gameoverlay_thread_report.unknown = 0;
            gameoverlay_thread_report.report_id = 0x3B;
            gameoverlay_thread_report.suspend_count = suspend_count;
            battleye::report(&amp;gameoverlay_thread_report, sizeof(gameoverlay_thread_report), 0);
        `}`

        if (GetThreadContext(thread_handle, &amp;context) &amp;&amp; context.Dr7)
        `{`
            gameoverlay_debug_report.unknown = 0;
            gameoverlay_debug_report.report_id = 0x3B;
            gameoverlay_debug_report.debug_register = context.Dr0;
            battleye::report(&amp;gameoverlay_debug_report, sizeof(gameoverlay_debug_report), 0);
        `}`
    `}`
`}`
```

#### <a class="reference-link" name="LSASS"></a>LSASS

windows进程的内存地址空间lsass.exe文件，也称为Local Security Authority进程，它将被枚举，任何异常都将报告给服务器，就像我们在前面两次检查中看到的那样：

```
if (equals(process_entry.executable_path, "lsass.exe"))
`{`
    auto lsass_handle = OpenProcess(QueryInformation, 0, (unsigned int)process_entry.th32ProcessID);
    if (lsass_handle)
    `{`
        for (address = 0;
              NtQueryVirtualMemory(lsass_handle, address, 0, &amp;lsass_memory_info, 0x30, &amp;bytes_needed) &gt;= 0;
              address = lsass_memory_info.base_address + lsass_memory_info.region_size)
        `{`
            if (lsass_memory_info.state == MEM_COMMIT
              &amp;&amp; lsass_memory_info.type == MEM_PRIVATE
              &amp;&amp; (lsass_memory_info.protect == PAGE_EXECUTE
               || lsass_memory_info.protect == PAGE_EXECUTE_READ
               || lsass_memory_info.protect == PAGE_EXECUTE_READWRITE))
            `{`
                // FOUND EXECUTABLE MEMORY OUTSIDE OF MODULES
                lsass_report.unknown = 0;
                lsass_report.report_id = 0x42;
                lsass_report.base_address = lsass_memory_info.base_address;
                lsass_report.region_size = lsass_memory_info.region_size;
                lsass_report.memory_info = 
                    lsass_memory_info.type | lsass_memory_info.protect | lsass_memory_info.state;
                battleye::report(&amp;lsass_report, sizeof(lsass_report), 0);
            `}`
        `}`
        CloseHandle(lsass_handle);
    `}`
`}`
```

LSASS以前被用来执行内存操作，因为任何需要internet连接的进程都需要让LSASS访问它。BattlEye目前已经通过手动剥离读/写访问的进程句柄，然后挂接ReadProcessMemory/WriteProcessMemory，将调用重定向到驱动程序BEDaisy来缓解这个问题。然后BEDaisy决定内存操作是否合法。如果它确定操作是合法的，它将继续它，否则，他们将故意蓝屏机器。

#### <a class="reference-link" name="Misc.%20report"></a>Misc. report

BattlEye收集杂项信息并将其发送回具有报告服务器id 3C。此信息包括：
- 任何带有WS_EX_TOPMOST最上面标志的窗口或等效的替代窗口
```
Window text (Unicode)
Window class name (Unicode)
Window style
Window extended style
Window rectangle
Owner process image path
Owner process image size
```
- 任何一个对游戏有开放进程句柄（VM|u WRITE | VM|u READ）的进程
```
Image name
Image path
Image size
Handle access
```
- 游戏特定文件的文件大小
```
....\Content\Paks\TslGame-WindowsNoEditor_assets_world.pak
....\Content\Paks\TslGame-WindowsNoEditor_ui.pak
....\Content\Paks\TslGame-WindowsNoEditor_sound.pak
```
- 游戏特定文件的内容：
```
....\BLGame\CookedContent\Script\BLGame.u
```
- NtGetContextThread的跳转信息
```
任何跳转指令（E9）都会被遵循，并记录最终地址
```

#### <a class="reference-link" name="NoEye"></a>NoEye

BattlEye通过检查GetFileAttributesExA找到的名为BE_DLL.dll的任何文件，实现了一个特定的、相当没下功夫的检查来检测公共旁路NoEye的存在。

```
void noeye::detect()
`{`
    WIN32_FILE_ATTRIBUTE_DATA file_information;
    if (GetFileAttributesExA("BE_DLL.dll", 0, &amp;file_information))
    `{`
      noeye_report.unknown = 0;
      noeye_report.report_id = 0x3D;
      noeye_report.file_size = file_information.nFileSizeLow;
      battleye::report(&amp;noeye_report, sizeof(noeye_report), 0);
    `}`
`}`
```

#### <a class="reference-link" name="Driver%20presence"></a>Driver presence

检查设备哔哔声和空值，如果存在则报告。这两个通常在任何系统上都不可用，这表示有人手动启用了一个设备，也称为驱动程序设备劫持。这样做是为了启用与恶意驱动程序的IOCTL通信，而不需要为所述驱动程序提供独立的驱动程序对象。

```
void driver::check_beep()
`{`
    auto handle = CreateFileA("\\\\.\\Beep", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, 0, OPEN_EXISTING, 0, 0);
    if (handle != INVALID_HANDLE_VALUE)
    `{`
      beep_report.unknown = 0;
      beep_report.report_id = 0x3E;
      battleye::report(&amp;beep_report, sizeof(beep_report), 0);
      CloseHandle(handle);
    `}`
`}`
void driver::check_null()
`{`
    auto handle = CreateFileA("\\\\.\\Null", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, 0, OPEN_EXISTING, 0, 0);
    if (handle != INVALID_HANDLE_VALUE)
    `{`
      null_report.unknown = 0;
      null_report.report_id = 0x3E;
      battleye::report(&amp;null_report, sizeof(null_report), 0);
      CloseHandle(handle);
    `}`
`}`
```

#### <a class="reference-link" name="Sleep%20delta"></a>Sleep delta

BattlEye还会将当前线程进行等待一秒钟的睡眠，并测量睡眠前后的tickcount差异：

```
void sleep::check_delta()
`{`
    const auto tick_count = GetTickCount();
    Sleep(1000);
    const auto tick_delta = GetTickCount() - tick_count;
    if (tick_delta &gt;= 1200)
    `{`
        sleep_report.unknown = 0;
        sleep_report.report_id = 0x45;
        sleep_report.delta = tick_delta;
        battleye::report(&amp;sleep_report, sizeof(sleep_report), 0);
    `}`
```

#### <a class="reference-link" name="7zip"></a>7zip

BE添加了一个非常随意的完整性检查，以防止人们将7zip库加载到游戏进程中并覆盖节区。这样做是为了减轻以前的字符串扫描和异常检测，BE决定只为这个特定的7zip库添加完整性检查。

```
void module::check_7zip()
`{`
    constexpr auto sz_7zipdll = "..\\..\\Plugins\\ZipUtility\\ThirdParty\\7zpp\\dll\\Win64\\7z.dll";
    const auto module_handle = GetModuleHandleA(sz_7zipdll);
    if (module_handle &amp;&amp; *(int*)(module_handle + 0x1000) != 0xFF1441C7)
    `{`
      sevenzip_report.unknown_1 = 0;
      sevenzip_report.report_id = 0x46;
      sevenzip_report.unknown_2 = 0;
      sevenzip_report.data1 = *(__int64*)(module_handle + 0x1000);
      sevenzip_report.data2 = *(__int64*)(module_handle + 0x1008);
      battleye::report(&amp;sevenzip_report, sizeof(sevenzip_report), 0);
    `}`
`}`
```

#### <a class="reference-link" name="Hardware%20abstraction%20layer"></a>Hardware abstraction layer

Battleye检查windows硬件抽象层动态链接库是否存在(硬件抽象层)，并向服务器报告它是否加载到游戏进程中。

```
void module::check_hal()
`{`
    const auto module_handle = GetModuleHandleA("hal.dll");
    if (module_handle)
    `{`
        hal_report.unknown_1 = 0;
        hal_report.report_id = 0x46;
        hal_report.unknown_2 = 2;
        hal_report.data1 = *(__int64*)(module_handle + 0x1000);
        hal_report.data2 = *(__int64*)(module_handle + 0x1008);
        battleye::report(&amp;hal_report, sizeof(hal_report), 0);
    `}`
`}`
```

#### <a class="reference-link" name="Image%20checks"></a>Image checks

BattlEye还会检查游戏进程中加载的各种映像。这些模块大概是有符号的映像，以某种方式被操纵滥用，但我们不能评论这些模块的全部范围，只有检测

```
void module::check_nvtoolsext64_1
`{`
    const auto module_handle = GetModuleHandleA("nvToolsExt64_1.dll");
    if (module_handle)
    `{`
      nvtools_report.unknown = 0;
      nvtools_report.report_id = 0x48;
      nvtools_report.module_id = 0x5A8;
      nvtools_report.size_of_image = (PE_HEADER*)(module_handle + (DOS_HEADER*)(module_handle)-&gt;e_lfanew))-&gt;SizeOfImage;
      battleye::report(&amp;nvtools_report, sizeof(nvtools_report), 0);
    `}`
`}`

void module::check_ws2detour_x96
`{`
    const auto module_handle = GetModuleHandleA("ws2detour_x96.dll");
    if (module_handle)
    `{`
      ws2detour_report.unknown = 0;
      ws2detour_report.report_id = 0x48;
      ws2detour_report.module_id = 0x5B5;
      ws2detour_report.size_of_image = (PE_HEADER*)(module_handle + (DOS_HEADER*)(module_handle)-&gt;e_lfanew))-&gt;SizeOfImage;
      battleye::report(&amp;ws2detour_report, sizeof(ws2detour_report), 0);
    `}`
`}`

void module::check_networkdllx64
`{`
    const auto module_handle = GetModuleHandleA("networkdllx64.dll");
    if (module_handle)
    `{`
        const auto dos_header = (DOS_HEADER*)module_handle;
        const auto pe_header = (PE_HEADER*)(module_handle + dos_header-&gt;e_lfanew));
        const auto size_of_image = pe_header-&gt;SizeOfImage;

        if (size_of_image &lt; 0x200000 || size_of_image &gt;= 0x400000)
        `{`
            if (pe_header-&gt;sections[DEBUG_DIRECTORY].size == 0x1B20)
            `{`
                networkdll64_report.unknown = 0;
                networkdll64_report.report_id = 0x48;
                networkdll64_report.module_id = 0x5B7;
                networkdll64_report.data = pe_header-&gt;TimeDatestamp;
                battleye::report(&amp;networkdll64_report, sizeof(networkdll64_report), 0);
            `}`
        `}`
        else
        `{`
            networkdll64_report.unknown = 0;
            networkdll64_report.report_id = 0x48;
            networkdll64_report.module_id = 0x5B7;
            networkdll64_report.data = pe_header-&gt;sections[DEBUG_DIRECTORY].size;
            battleye::report(&amp;networkdll64_report, sizeof(networkdll64_report), 0);
        `}`
    `}`
`}`

void module::check_nxdetours_64
`{`
    const auto module_handle = GetModuleHandleA("nxdetours_64.dll");
    if (module_handle)
    `{`
      nxdetours64_report.unknown = 0;
      nxdetours64_report.report_id = 0x48;
      nxdetours64_report.module_id = 0x5B8;
      nxdetours64_report.size_of_image = (PE_HEADER*)(module_handle + (DOS_HEADER*)(module_handle)-&gt;e_lfanew))-&gt;SizeOfImage;
      battleye::report(&amp;nxdetours64_report, sizeof(nxdetours64_report), 0);
    `}`
`}`

void module::check_nvcompiler
`{`
    const auto module_handle = GetModuleHandleA("nvcompiler.dll");
    if (module_handle)
    `{`
      nvcompiler_report.unknown = 0;
      nvcompiler_report.report_id = 0x48;
      nvcompiler_report.module_id = 0x5BC;
      nvcompiler_report.data = *(int*)(module_handle + 0x1000);
      battleye::report(&amp;nvcompiler_report, sizeof(nvcompiler_report), 0);
    `}`
`}`

void module::check_wmp
`{`
    const auto module_handle = GetModuleHandleA("wmp.dll");
    if (module_handle)
    `{`
      wmp_report.unknown = 0;
      wmp_report.report_id = 0x48;
      wmp_report.module_id = 0x5BE;
      wmp_report.data = *(int*)(module_handle + 0x1000);
      battleye::report(&amp;wmp_report, sizeof(wmp_report), 0);
    `}`
`}`
```

#### <a class="reference-link" name="Module%20id%20enumeration"></a>Module id enumeration

以下是模块的枚举ID,供参考：

```
enum module_id
`{`
    nvtoolsext64    = 0x5A8,
    ws2detour_x96   = 0x5B5,
    networkdll64    = 0x5B7,
    nxdetours_64    = 0x5B8,
    nvcompiler      = 0x5BC,
    wmp             = 0x5BE
`}`;
```

#### <a class="reference-link" name="TCP%20table%20scan"></a>TCP table scan

BE shellcode还将搜索系统范围内的tcp连接列表（称为tcp表），并报告您至少连接到一个特定的cloudflare网关ip地址，这些地址属于德国paytocheat网站[https://xera.ph/。](https://xera.ph/%E3%80%82)<br>
这个检测机制被添加到外壳代码中，用于在游戏运行时检测任何使用其启动器的用户，使其易于识别。此机制的唯一问题是，cloudflare网关ip地址可能会在稍后进行切换，如果相应ip地址的新所有者分发连接到该特定端口上的服务器的软件，则无疑会发生误报。

```
void network::scan_tcp_table
`{`
    memset(local_port_buffer, 0, sizeof(local_port_buffer));

    for (iteration_index = 0; iteration_index &lt; 500; ++iteration_index)
    `{`
        // GET NECESSARY SIZE OF TCP TABLE
        auto table_size = 0;
        GetExtendedTcpTable(0, &amp;table_size, false, AF_INET, TCP_TABLE_OWNER_MODULE_ALL, 0);

        // ALLOCATE BUFFER OF PROPER SIZE FOR TCP TABLE
        auto allocated_ip_table = (MIB_TCPTABLE_OWNER_MODULE*)malloc(table_size);

        if (GetExtendedTcpTable(allocated_ip_table, &amp;table_size, false, AF_INET, TCP_TABLE_OWNER_MODULE_ALL, 0) != NO_ERROR)
            goto cleanup;

        for (entry_index = 0; entry_index &lt; allocated_ip_table-&gt;dwNumEntries; ++entry_index)
        `{`
            const auto ip_address_match_1 = 
                allocated_ip_table-&gt;table[entry_index].dwRemoteAddr == 0x656B1468; // 104.20.107.101

            const auto ip_address_match_2 = 
                allocated_ip_table-&gt;table[entry_index].dwRemoteAddr == 0x656C1468; // 104.20.108.101

            const auto port_match = 
                allocated_ip_table-&gt;table[entry_index].dwRemotePort == 20480;

            if ( (!ip_address_match_1 &amp;&amp; !ip_address_match_2) || !port_match)
                continue;

            for (port_index = 0; 
                 port_index &lt; 10 &amp;&amp; 
                 allocated_ip_table-&gt;table[entry_index].dwLocalPort != 
                    local_port_buffer[port_index]; 
                 ++port_index)
            `{`
                if (local_port_buffer[port_index])
                    continue;

                tcp_table_report.unknown = 0;
                tcp_table_report.report_id = 0x48;
                tcp_table_report.module_id = 0x5B9;
                tcp_table_report.data = 
                    BYTE1(allocated_ip_table-&gt;table[entry_index].dwLocalPort) | 
                    (LOBYTE(allocated_ip_table-&gt;table[entry_index.dwLocalPort) &lt;&lt; 8);

                battleye::report(&amp;tcp_table_report, sizeof(tcp_table_report), 0);

                local_port_buffer[port_index] = allocated_ip_table-&gt;table[entry_index].dwLocalPort;
                break;

            `}`
        `}`

cleanup:
        // FREE TABLE AND SLEEP
        free(allocated_ip_table);
        Sleep(10);
    `}`
`}`
```

#### <a class="reference-link" name="Report%20types"></a>Report types

作为参考，以下是shellcode中已知的报告类型：

```
enum BATTLEYE_REPORT_ID
`{`
    MEMORY_GUARD            = 0x21,
    MEMORY_SUSPICIOUS       = 0x2F,
    WINDOW_TITLE            = 0x33,
    MEMORY                  = 0x35,
    PROCESS_ANOMALY         = 0x38,
    DRIVER_BEEP_PRESENCE    = 0x3E,
    DRIVER_NULL_PRESENCE    = 0x3F,
    MISCELLANEOUS_ANOMALY   = 0x3B,
    PROCESS_SUSPICIOUS      = 0x40,
    LSASS_MEMORY            = 0x42,
    SLEEP_ANOMALY           = 0x45,
    MEMORY_MODULE_SPECIFIC  = 0x46,
    GENERIC_ANOMALY         = 0x48,
    MEMORY_MODULE_SPECIFIC2 = 0x5B,
`}`
```

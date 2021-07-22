> 原文链接: https://www.anquanke.com//post/id/247603 


# 一种特殊的dll劫持


                                阅读量   
                                **88729**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t019f36b3928d4817f9.png)](https://p4.ssl.qhimg.com/t019f36b3928d4817f9.png)



作者：[houjingyi](https://twitter.com/hjy79425575)

去年我分享了我发现的[CVE-2020-3535：Cisco Webex Teams windows客户端dll劫持漏洞](https://www.anquanke.com/post/id/219167)。当时我文章中说：

> 考虑另外一种exe和加载的dll不在同一个路径的情况，如果C:\abc\def\poc.exe想要加载C:\abc\lib\test.dll，可不可以写成LoadLibraryW(L”..\lib\test.dll”)呢？这也是会导致漏洞的，同样windows会把”..\lib\test.dll”直接当成”C:\lib\test.dll”。我在另外某个知名厂商的产品中发现了这样的代码，我已经报告给了厂商，还在等厂商给我答复。我可能会在90天的期限或者厂商发布安全公告之后补充更多细节。

实际上我发现了两个产品中都有这样的代码，分别是IBM(R) Db2(R)和VMware ThinApp。具体细节我发到full disclosure里面了：

[VMware ThinApp DLL hijacking vulnerability](https://seclists.org/fulldisclosure/2021/Jul/35)<br>[IBM(R) Db2(R) Windows client DLL Hijacking Vulnerability(0day)](https://seclists.org/fulldisclosure/2021/Feb/73)

我们看看[LoadLibrary的文档](https://docs.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-loadlibrarya):

[![](https://p3.ssl.qhimg.com/t014b2f12fae56d4d54.png)](https://p3.ssl.qhimg.com/t014b2f12fae56d4d54.png)

微软说你们可不能直接给LoadLibrary一个相对路径啊，你们应该先用GetFullPathName获取dll的绝对路径，再把绝对路径作为参数调用LoadLibrary。那么当我们给LoadLibrary提供一个相对路径的时候到底发生了什么呢？以VMware ThinApp中的`LoadLibraryExW(L"\\DummyTLS\\dummyTLS.dll", 0, 0)`为例我们来简单分析一下Windows的ntdll.dll是怎么处理dll路径的。这里的流程是：KernelBase!LoadLibraryExW-&gt;ntdll!LdrpLoadDll-&gt;ntdll!LdrpPreprocessDllName，我们来看LdrpPreprocessDllName。

[![](https://p2.ssl.qhimg.com/t017677b9130a8027de.png)](https://p2.ssl.qhimg.com/t017677b9130a8027de.png)

代码的意思是调用RtlDetermineDosPathNameType_Ustr判断路径的类型，这里返回了4也就是RtlPathTypeRooted，后面调用LdrpGetFullPath就得到C:\DummyTLS\dummyTLS.dll这样的一个路径了。所以这里处理的逻辑就是只要你是一个相对路径，Windows就认为你是一个相对于磁盘根目录(一般也就是C盘)的路径。可以参考[ReactOS的代码](https://github.com/mirror/reactos/blob/master/reactos/lib/rtl/path.c#L54)。

[![](https://p5.ssl.qhimg.com/t016097d2d1517191b8.png)](https://p5.ssl.qhimg.com/t016097d2d1517191b8.png)<br>
非常糟糕的是Windows中非管理员用户是可以在C盘根目录下创建文件夹并向其中写入文件的，所以就导致了这种本地提权的场景。



## 小结

1.确实不能理解Windows系统里面为什么有这么奇怪的设计，可能很多Windows开发也不知道。<br>
2.还是像我之前文章里面说的，如果dll加载失败的时候开发者认真调试检查就能避免这样的漏洞(也正因为如此这种dll劫持的场景一般不会发生)。<br>
3.Windows中非管理员用户是可以在C盘根目录下创建文件夹并向其中写入文件的，这给了很多这样本地提权场景利用的机会。<br>
4.使用绝对路径往往能更安全一点，后面有机会我也可能继续分享一些我发现的相对路径导致的各种各样的本地提权或者RCE的场景。

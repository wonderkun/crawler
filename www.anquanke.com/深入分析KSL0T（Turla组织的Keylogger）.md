> 原文链接: https://www.anquanke.com//post/id/181793 


# 深入分析KSL0T（Turla组织的Keylogger）


                                阅读量   
                                **179671**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者0ffset，文章来源：0ffset.net
                                <br>原文地址：[https://0ffset.net/reverse-engineering/malware-analysis/analyzing-turlas-keylogger-1/](https://0ffset.net/reverse-engineering/malware-analysis/analyzing-turlas-keylogger-1/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t018903ab3fb4f7d26d.jpg)](https://p3.ssl.qhimg.com/t018903ab3fb4f7d26d.jpg)



过去一个月里，俄罗斯的APT集团——Turla，频频在新闻中出现。此前，该集团对欧洲政府外国办事处进行了攻击，创建了一个极其隐秘的后门，通过邮件结合恶意PDF文件窃取数据。最近，我注意到一个上传至VirusBay([https://beta.virusbay.io/](https://beta.virusbay.io/)) 的恶意软件样本，它带有Turla和Venomous Bear(Turla的别名)的标签，于是决定对该样本进行分析。在经过思考后，我决定用静态分析的方法来处理这个样本。让我们开始分析这个样本吧!

样本的MD5值为59b57bdabee2ce1fb566de51dd92ec94



## 0x01 样本分析

常规操作，我首先通过一些命令查看这个二进制文件的信息，尝试找到一些突破口。它实际上是一个64位的DLL文件。我们可以看到一些错误提示和一些Windows API调用（如IsDebuggerPresent、WriteFile）以及动态加载调用(GetModuleHandle、LoadLibrary、GetProcAddress)，但是它依然有大量的无用输出存在

[![](https://p1.ssl.qhimg.com/t01aeca0f149ff62688.png)](https://p1.ssl.qhimg.com/t01aeca0f149ff62688.png)

在IDA中打开文件，我们可以看到EP为DLLMain函数。经过cmp操作后，程序跳转到0x1800019BD，这里有一个非常重要的函数被调用。乍一看该函数好像没什么特别，只是一个需要传递3个参数的函数。直到你意识到，它一直在重复调用这个相同的函数，并且其第二个参数似乎指向的是一些加密的文本，如图2所示

[![](https://p1.ssl.qhimg.com/t0126393fab818ea08b.png)](https://p1.ssl.qhimg.com/t0126393fab818ea08b.png)

你可能已经猜到，这实际上是一个解密函数。因为当我们看到在0x180001750处调用的函数时，可以根据其传递的参数和xor edx, eax操作来确定它是一个解密函数。还要注意for循环，它比较eax的值(存储在arg_10的值)和var_18的值。

[![](https://p1.ssl.qhimg.com/t010b9153f4d551c943.png)](https://p1.ssl.qhimg.com/t010b9153f4d551c943.png)

根据下面这段代码，我们可以进一步推断var_18实际上是一个计数器:

```
mov      eax, [var_18]
add      eax, 1
mov      [var_18], eax
```

当我们发现这个之后，可以将var**18重命名为Counter。点击var_18并按下`n`，将出现一个提示，在此进行重命名，以便于后续直观分析。现在，我们需要找出与计数器的值进行比较的对象，这意味着我们需要分析`arg_10`。因为它是`arg****`而不是`var_**`，所以我们必须查看传递给这个特定函数的参数的值。在本例中，该参数不是使用push传递的，而是使用mov指令。当r8d寄存器中的值被移动到arg_10中时，让我们返回到调用函数的地方，在执行解密函数之前查看一下r8d寄存器中的内容。

```
mov   r8d, 25Eh
lea   rdx, unk_18000F2F0
mov   ecx, 47h
call  sub_180001750
```

选择数字的同时按下字母’H’，我们可以将十六进制数转换为十进制数，得到十进制值606。对于这个特殊的调用，XOR运算会循环606次，因为要对每个字符执行XOR操作。现在我们已经确定了arg_10的值，继续对它进行一下重命名。接下来，我们尝试找出执行XOR运算之后的值，看看能否找到使用的密钥和解密的数据。xor对edx和eax执行XOR操作，操作的结果总会存储在运算的第一个参数中，也就是这个运算的结果存储在edx中。我们可以假设edx包含要解密的数据，eax包含密钥。为了找出这些值，我们必须查看mov或lea到edx和eax寄存器中的值。

[![](https://p1.ssl.qhimg.com/t017ee26982fe571bf5.png)](https://p1.ssl.qhimg.com/t017ee26982fe571bf5.png)

如图4所示，在XOR操作执行之前，r8d的值被mov到edx中，因此我们查看此段的第三条指令，也就是预先移动到r8d中的内容：`movsx r8d, byte ptr[rax+rcx]`。这几条指令之前，[rsp+18h+counter]mov到rcx中，而且不管arg_8中的值是多少都会被移到rax中。我们知道计数器每次循环会加1，因此我们可以确定字节ptr[rax+rcx]迭代超过606次，其中一些是加密字符。我们可以通过找出arg_8的值来进行再次确定，就像我们发现arg_10的值是unk_18000F2F0一样，它包含许多加密数据(具体来说，是606字节的加密数据)。

[![](https://p5.ssl.qhimg.com/t01c1bbd84444dc644c.png)](https://p5.ssl.qhimg.com/t01c1bbd84444dc644c.png)

接下来，让我们看看eax中存储了什么。在本例中，[rax+rdx]处的一个字节的数据被移动到eax中。因此，我们需要定位存储在rax和rdx中的数据。rax中的数据很容易找到，因为在movsx之前有一条指令：`mov rax, unk_18000F010`。查看0x18000F010处的数据，我们可以看到似乎更机密的文本:用于解密18000F2F0处数据的密钥。然而，事情并没有那么简单，由于之前使用过的rdx的值在每次迭代中都会改变。因此为了计算这个值，我们需要查看div指令。

0x18000F010如图:

[![](https://p4.ssl.qhimg.com/t0108d97b60dd49a32c.png)](https://p4.ssl.qhimg.com/t0108d97b60dd49a32c.png)

```
mov  rax, arg_0
xor  edx, edx
mov  ecx, 100
div  ecx
```

div指令接受一个操作数——这个操作数包含要除以rax的值。x64汇编程序中0x8003除以0x100的除法应该是这样的:

```
xor rdx, rdx      ; clear dividend
mov rax, 0x8003   ; dividend
mov rcx, 0x100    ; divisor
div rcx           ; rcx = 0x80, rdx = 0x3
```

此段代码基本上是一个除法运算，但是余数存储在rdx中，这意味着rdx等于0x3。对于keylogger, XOR运算的值是根据rdx的值来决定的，因此我们需要算出rax的值，然后将它除以0x64来得到rdx的第一个值。我们知道arg_0包含函数执行前的ecx值，即0x47。转换为小数格式，即71/100=0.71。rdx中存储的值是71，只需对这两个值进行模运算(%)，就会得到71。这意味着密钥数组中的第71个字节是XOR运算中使用的第一个字节。对于每个循环，arg_0中的值都增加1，这意味着密钥字节总是在变化，因此，虽然我们知道了算法的工作原理，但是我们仍然只可以静态地自动解密，而不是依赖于调试器。

```
mov eax, [rsp+18h+arg_0]
add eax, 1
mov [rsp+18h+arg_0], eax
```



## 0x02 如何静态解密

方法一是使用IDC，它是一种包含在IDA中的脚本语言。

方法二是IDAPython，但是IDA 7 Pro免费版中没有IDAPython，所以我将继续使用IDC。到目前为止，我们知道解密部分都包含在一个循环中，该循环使用一个特定的密钥序列和一个确定的数据序列来循环预先确定的次数。此外，用于div操作的值也作为参数传递。因此，函数需要3个参数:base_data、div和loop，同时还需要6个变量:index、x1、x2、data、i和base_xor。index将包含模运算的结果,x1将包含数据加密文本的一个字节,x2包含密钥中一个字节的数据,data将包含XOR运算的结果,i是计数器，base_xor将存储密钥序列的地址。要存储地址，只需在该地址的开头添加0x。脚本的其余部分将包含必要的增量和XOR运算的数据。

```
static decrypt_data(base_data, div, loop) `{`
auto index, x1, x2, data, i, base_xor;
base_xor = 0x18000F010;

for (i = 0; i &amp;lt; loop; i++) `{`

    index = div % 100; // Get value from div % 100
    x1 = Byte(base_data); // Get byte from encrypted data
    x2 = Byte(base_xor + index); // Get XOR key using value from div / 100
    data = x1 ^ x2; // XOR data
    PatchByte(base_data, data); // Replace enc. byte with dec. byte
    base_data = base_data + 1; // Increment Encrypted Data
    div = div + 1; // Increment Divider
`}`

`}`
```

将此脚本“安装”到IDA中，点击File -&gt; Script Command，然后将其粘贴到对话框中。要调用该函数，只需在底部的命令行输入decrypt_data(0x18000F2F0, 71, 606)来解密数据的第一部分，如下图所示。

[![](https://p1.ssl.qhimg.com/t012ad1adf63572d9e6.png)](https://p1.ssl.qhimg.com/t012ad1adf63572d9e6.png)

选择所有的数据，按下’A’，使其排列成更清晰的数据，由于每2个字节遇到一个0，所以需要删除它们。

[![](https://p4.ssl.qhimg.com/t013ea0b7879ebc338d.png)](https://p4.ssl.qhimg.com/t013ea0b7879ebc338d.png)

去掉多个0后，我们得到:

```
&lt;#RShift&gt; &lt;#LShift&gt; &lt;#RCtrl&gt; &lt;#LCtrl&gt; &lt;!RShift&gt; &lt;!LShift&gt; &lt;!RCtrl&gt; &lt;!LCtrl&gt; - + []  ; / ` ' , . &lt;PageUp&gt; &lt;PageDown&gt; &lt;NumLock&gt; &lt;r/&gt; &lt;r*&gt; &lt;r-&gt; &lt;r+&gt; &lt;r1&gt; &lt;r2&gt; &lt;r3&gt; &lt;r4&gt; &lt;r5&gt; &lt;r6&gt; &lt;r7&gt; &lt;r8&gt; &lt;r9&gt; &lt;r0&gt; &lt;r.&gt; &lt;F1&gt; &lt;F2&gt; &lt;F3&gt; &lt;F4&gt; &lt;F5&gt; &lt;F6&gt; &lt;F7&gt; &lt;F8&gt; &lt;F9&gt; &lt;F10&gt; &lt;F11&gt; &lt;F12&gt; &lt;Down&gt; &lt;Up&gt; &lt;Right&gt; &lt;Left&gt; &lt;Del&gt; &lt;Print&gt; &lt;End&gt; &lt;Insert&gt; &lt;CapsLock&gt; &lt;Enter&gt; &lt;Backspace&gt; &lt;Esc&gt; &lt;Tab&gt;
```

当我们按下某些键(如左Shift和NumLock)时，可以假设这些数据用于记录击键，而不是常规字符。为了再次检查解密工作，我们可以在调试器中运行它并检查输出。现在我们已经成功解密了第一部分，还可以对剩下的加密的19个部分的每一部分都进行相同的解密。如果你想查看每个解密的字符串，可以在这里查看它们([https://pastebin.com/DrGVU417)。](https://pastebin.com/DrGVU417)%E3%80%82) 其中一个特别有趣的字符串是msimm.dat，因为它可能是日志文件。除了msimm之外，其中一个字符串似乎指出了上述keylogger的版本，以及它可能的名称:KSL0T Ver = 21.0，除此之外，我还没发现任何与KSL0T 组织相关的有意义的内容。



## 小结

由于本样本含有大量的解密和函数需要分析，尤其是静态分析，因此我将这篇文章分成两个部分。我主要专注于静态分析的演示,教人们在没有完整版IDA Pro的情况下，通过静态分析方法处理更多的问题,以及如何使用IDC自动化解决耗时任务。在下一部分中，我将解密更多的内容，然后分析出keylogging的循环。



## IOC(MD5)

Keylogger: 59b57bdabee2ce1fb566de51dd92ec94

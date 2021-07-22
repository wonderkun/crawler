> 原文链接: https://www.anquanke.com//post/id/85335 


# 【技术分享】反侦测的艺术part2：精心打造PE后门（含演示视频）


                                阅读量   
                                **111450**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：pentest.blog
                                <br>原文地址：[https://pentest.blog/art-of-anti-detection-2-pe-backdoor-manufacturing/](https://pentest.blog/art-of-anti-detection-2-pe-backdoor-manufacturing/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p2.ssl.qhimg.com/t013644ab3405f66011.jpg)](https://p2.ssl.qhimg.com/t013644ab3405f66011.jpg)**

**翻译：**[**shan66**](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：260RMB**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

**<br>**

**传送门**

[**【技术分享】反侦测的艺术part1：介绍AV和检测的技术******](http://bobao.360.cn/learning/detail/3420.html)

[**【技术分享】反侦测的艺术part3：shellcode炼金术******](http://bobao.360.cn/learning/detail/3589.html)

<br>

本文将为读者详细介绍渗透测试人员将后门植入PE（便携式可执行文件）文件中的几种方法。要想完全掌握本文的内容，读者至少需要熟悉x86汇编知识，并精通调试器，同时还需要对PE文件格式有着全面的了解。



**引言**

现在，几乎所有的安全研究人员、渗透测试人员和恶意软件分析师每天都要跟各种后门打交道：将后门植入系统或某种流行的程序中，以便日后继续访问系统。 本文的大部分内容都是关于将后门植入32位PE文件的方法，但由于PE文件格式是Unix COFF（通用对象文件格式）的修改版本，所以这些方法背后的逻辑，同样适用于所有其他可执行二进制文件类型。 此外，植入的后门的隐秘性，对于其存活时间来说尤其重要，所以本文将介绍各种方法，尽量设法绕过各种安全检测。

<br>

**相关术语**

**红队渗透测试：**在与黑客攻击有关的语境中，所谓红队指的是一群白帽黑客，他们以攻击者的姿态来攻击组织的数字基础设施，以测试组织的防御措施的有效性（通常称为“渗透测试”）。包括微软在内的许多公司，都会定期进行类似的安全拉练，其中红队和蓝伍都会参与其中。这样做的好处是，可以挑战人们的先入之见，找出安全隐患，从而弄清楚敏感信息的泄露途径、漏洞的具体利用方式以及具体存在哪些安全偏见等。

**地址空间布局随机化（ASLR）：**这是一种防止缓冲区溢出攻击的计算机安全技术。为了防止攻击者可靠地跳转到内存中的特定的被利用函数中，ASLR会对进程的关键数据区域的地址空间位置进行随机布置，其中包括可执行文件的基址以及堆、栈和程序库的地址等。 

**代码洞：**代码洞是一段代码，它将由另一个程序写入到其他进程的内存中。这段代码可以通过在目标进程内创建远程线程来执行。一般情况下，代码的代码洞是指代码中可注入自定义指令的脚本部分。例如，如果脚本的内存能够容下5个字节，但是只使用了3个字节，那么剩余的2个字节可用于添加来自该脚本之外的代码。这就是所谓的代码洞。

**校验和：**在数据存储和数据通信领域中，用于校验目的的一组数据项的和，虽然校验和本身比较小巧，但是可用来检测数据在传输或存储期间是否出错。它通常用来检测从下载服务器下载的安装文件的完整性。就校验和来说，它通常用于独立验证数据的完整性，而无需依赖于验证数据的真实性。 

<br>

**主要方法**

本文中的所有实现和示例都是针对putty SSH客户端可执行文件的。选择putty来练习后门的制作有多个原因，其中之一是putty客户端是一个本地C++项目，它用到了多个库以及Windows API，另一个原因是给ssh客户端植入后门不太引人耳目，因为该程序早就建立了tcp连接，所以更容易躲避蓝队的网络监控，这里使用的后门代码是来自metasploit项目中Stephen Fever的reverse tcp meterpreter shellcode。主要目标是将meterpreter shellcode注入到目标PE文件，同时还不能破坏该程序的实际功能。注入的shellcode将在一个新的线程上执行，并会不断尝试连接到处理程序。与此同时，另一个目标是尽量不要被检测到。

在PE文件中植入后门的常见方法，通常都包括4个主要步骤：

1）找到可以存放后门代码的地方

2）劫持执行流程

3）注入后门代码

4）恢复执行流程

当然，在每个步骤中还有许多小细节，而这些细节才是保持植入后门的一致性、耐用性和隐蔽性的关键所在。 

<br>

**可用空间问题**

我们的第一步工作是找到可用的内存空间。如何在PE文件中选择合适的空间来插入后门代码是一件非常重要的事情，这个空间的选择直接影响后门的隐蔽性。

要想解决这个问题，主要有两种方法：

**1）添加新空间**

与其他方法相比，这种方法的隐蔽性要差一些，但是它的好处在于，由于附加了一个新的空间，所以对于后门代码的大小没有太多限制。

借助于反汇编程序或PE编辑器，如LordPE，我们可以通过添加一个新的节头来扩展PE文件，这里是putty可执行文件的节表，在PE编辑器的帮助下，添加了了一个新节“NewSec”，其大小为1000字节，

[![](https://p5.ssl.qhimg.com/t01f378fa8ba6acfaae.png)](https://p5.ssl.qhimg.com/t01f378fa8ba6acfaae.png)

在创建一个新的节时，需要将节标志设置为“Read/Write/Execute”，只有这样，当PE映像映射到内存后，才能正常运行后门的shellcode。

[![](https://p5.ssl.qhimg.com/t01238748cb8a8da4a0.png)](https://p5.ssl.qhimg.com/t01238748cb8a8da4a0.png)

在添加节头之后，我们还需要调整文件得大小，不过这也不是什么难事，只要根据节的大小，使用十六进制编辑器在文件末尾添加相应长度的空字节即可。<br> 

[![](https://p1.ssl.qhimg.com/t018b7080cda8745f87.png)](https://p1.ssl.qhimg.com/t018b7080cda8745f87.png)

在完成上述操作之后，新的空节就会成功地添加到该文件中了。我们建议在添加新节之后运行该文件，如果一切正常的话，就可以通过调试器来修改这个新节了。

[![](https://p5.ssl.qhimg.com/t01c679d673d1759935.png)](https://p5.ssl.qhimg.com/t01c679d673d1759935.png)

通过为可执行文件添加一个新的代码节，虽然可以解决空间问题，但是在反侦查方面几乎没有任何优势可言，因为几乎所有的AV产品都能检测到不常用的代码节，尤其是这里还给它提供了（Read/Write/Execute），那肯定是非常可疑的。

即使向putty可执行文件添加的代码节是空的，并且不赋予任何权限，也照样会被某些AV产品标记为恶意代码。 <br> 

[![](https://p1.ssl.qhimg.com/t01b11d8dd777a3b195.png)](https://p1.ssl.qhimg.com/t01b11d8dd777a3b195.png)

**2）代码洞**

解决空间问题的第二种方法是利用目标可执行文件中的代码洞。 几乎所有已编译的二进制文件都有代码洞，而这些正好可以用于存放我们的后门。 相对于添加新的代码节来说，使用代码洞不太容易引起AV产品的注意，因为使用的都是已经存在的公共代码部分。 此外，PE文件的总体大小，即使在植入后门后也不会改变，但是，该方法也有几个小缺点。<br>代码洞的数量和大小会随着文件的不同而不同，但是通常来说，这与添加新节相比，可用空间的限制就会非常大。 当使用代码洞时，后门代码应尽可能小巧。 另一个缺点是节标志。 因为应用程序的执行将被重定向到代码洞所在地址，所以含有代码洞的代码节必须具有“execute”权限，除此之外，有一些shellcode（以自修改的方式编码或混淆）甚至还要求提供“write”权限，以便对代码节内的内容进行修改。 

使用多个代码洞将有助于克服空间限制问题，也将后门代码分割为不同部分，按理说能够提高它的隐蔽性，但遗憾是的，修改代码节的权限将会带来更大的嫌疑。能够在运行时修改内存权限从而避免直接更改节权限的高级方法非常少，因为这些方法需要定制的shellcode、编码和IAT解析技术，对于这些内容，我们将会在后面的文章中专门加以介绍。

借助于一个名为Cminer的工具，我们可以轻松地找出二进制文件中所有的代码洞。例如，通过命令./Cminer putty.exe 300，我们可以找出putty.exe中所有长度大于300字节的代码洞

[![](https://p4.ssl.qhimg.com/t012653b4fe25ccb20f.png)](https://p4.ssl.qhimg.com/t012653b4fe25ccb20f.png)

就本例来说，有5个不错的代码洞可以使用。起始地址给出了代码洞的虚拟内存地址（VMA），即当PE文件加载到内存中后，代码洞的地址，文件偏移量是代码洞在PE文件内的相对位置，这里以字节为单位。

[![](https://p1.ssl.qhimg.com/t016cfbb3b74b6d36eb.png)](https://p1.ssl.qhimg.com/t016cfbb3b74b6d36eb.png)

大部分洞穴大都位于数据节内，但是，由于数据节没有execute权限，所以需要修改相应的节标志。我们的后门代码大小在400-500字节左右，所以这里的代码洞应该够用了。所选择的代码洞的起始地址应该保存好，在将节权限改为R/W/E之后，植入后门的第一步工作就算完成了。接下来，我们开始处理执行流程的重定向问题。 



**劫持执行流程 **

在这一步中，目标是将执行流重定向到后门代码，为此需要修改目标可执行文件的相关指令。在选择修改哪一个指令方面，有一些细节需要引起我们的高度注意。所有二进制指令具有一定的大小（以字节为单位），为了跳转到后门代码的地址上面，必须使用5或6字节的长跳转指令。因此，在给二进制代码打补丁时，被修改的指令的长度需要跟长跳转指令的长度保持一致，否则它的上一条或下一条指令就会被破坏。

在进行重定向的时候，选择适当的内存空间对于绕过AV产品的动态和沙箱分析机制是非常重要的。如果直接进行重定向，则可能在AV软件的动态分析阶段被检测到。

**隐藏在用户交互下：**

为了绕过沙箱/动态分析阶段的检测，首先想到的自然是延迟shellcode的执行或设计能够检测沙箱的shellcode和触发机制。但是在制作后门时，通常没有这么多的空间，供我们在PE文件中添加这些额外的代码。此外，还可以利用汇编语言设计防检测机制，但是这需要大量的时间和丰富的知识。 

该方法使用的函数，需要用户的介入才能得到执行，具体来说，这个函数对应于程序的特定功能，只有当实际的用户运行该程序并且执行了特定的操作时，才会执行这个函数，引发执行流程的重定向，从而激活后门代码。如果此方法可以正确实施，它将具有％100成功率，并且不会增加后门代码的大小。

当用户点击putty用户界面上的“Open”按钮时，将会启动一个相应的函数，来检查给定IP地址的有效性，

[![](https://p1.ssl.qhimg.com/t01d26789686fd394a1.png)](https://p1.ssl.qhimg.com/t01d26789686fd394a1.png)

如果ip地址字段中的值不为空并且有效，就会执行一个函数来连接给定ip地址。

如果客户端成功创建了一个ssh会话，就会弹出一个新的窗口，并要求输入登陆凭证，

[![](https://p1.ssl.qhimg.com/t0132a9899e83c1c0ff.png)](https://p1.ssl.qhimg.com/t0132a9899e83c1c0ff.png)

这就是发生重定向的地方，因为没有那款AV产品高级到检测这么复杂的用法，所以，以这种方式植入的后门，自然就不必担心受到自动沙箱和动态分析的检测了。<br>使用基本的逆向工程方法，如跟踪字符串及其引用，很容易就能找到连接函数的地址。客户端与给定的ip建立连接后，会将字符串“login as：”打印到窗口中。这个字符串将帮助我们找到连接函数的地址，因为IDA Pro在跟踪字符串引用方面非常优秀。 

在IDA中依次选择Views-&gt;Open Subviews-&gt;Strings菜单项，来寻找字符串“login as:” 

[![](https://p5.ssl.qhimg.com/t01410a1bbec8127376.png)](https://p5.ssl.qhimg.com/t01410a1bbec8127376.png)

找到该字符串后双击，就会来到它在代码中的位置，由于IDA能够找出数据节内该字符串的所有交叉引用，我们只需按“Ctrl + X”就能显示所有交叉引用，这个引用位于打印“login as：”字符串的函数中，

[![](https://p5.ssl.qhimg.com/t01a00a9b58f27fffbc.png)](https://p5.ssl.qhimg.com/t01a00a9b58f27fffbc.png)

[![](https://p3.ssl.qhimg.com/t0133c84b294ab61496.png)](https://p3.ssl.qhimg.com/t0133c84b294ab61496.png)

这就是我们要修改的那个指令，在进行任何更改之前，先保存下来。因为在执行后门代码之后，我们还会用到它。

[![](https://p0.ssl.qhimg.com/t01efaead646e73c874.png)](https://p0.ssl.qhimg.com/t01efaead646e73c874.png)

将PUSH 467C7C指令更改为JMP 0x47A478之后，后门制作的重新定向阶段便告一段落了。需要注意的是，要记住下一个指令的地址。在执行后门代码后，它将用作返回地址。接下来，我们要做的是注入后门代码。 

<br>

**注入后门代码 **

在注入后门代码时，首先需要想到的是在执行后门代码之前保存寄存器。所有寄存器中的每个值对于程序的执行而言都是非常重要的。所以，需要在代码洞的开头部分放入相应的PUSHAD和PUSHFD指令，将所有寄存器和寄存器标志都保存到堆栈中。这些值将在执行后门代码之后弹出，以便程序可以继续执行而不会出现任何问题。

[![](https://p0.ssl.qhimg.com/t016a1a34c677f7796f.png)](https://p0.ssl.qhimg.com/t016a1a34c677f7796f.png)

如前所述，我们这里使用的后门代码来自metasploit项目的meterpreter reverse tcp shellcode。但是，这里需要对这个shellcode稍作修改。通常，反向tcp shellcode连接处理程序的尝试次数是有限制的，如果连接失败，则通过调用ExitProcess API来关闭该进程。

[![](https://p3.ssl.qhimg.com/t014761244831af77f4.png)](https://p3.ssl.qhimg.com/t014761244831af77f4.png)

这里的问题是，如果连接处理程序失败，putty客户端将会停止，现在，我们只要修改几行shellcode的汇编代码，就可以让它每次连接失败后，重新尝试连接处理程序，同时，还让shellcode的尺寸也变小了。 

[![](https://p2.ssl.qhimg.com/t01a6272b6537fb887c.png)](https://p2.ssl.qhimg.com/t01a6272b6537fb887c.png)

对汇编代码进行必要的更改后，使用nasm -f bin stager_reverse_tcp_nx.asm命令进行编译。现在反向tcp shellcode已经可以使用了，但不会直接植入。我们的目标是在新线程上执行shellcode。为了创建一个新的线程实例，需要让另一个shellcode调用指向反向tcp shellcode的CreateThread API。在Metasploit项目中，也有一个用于创建线程得shellcode，它是由Stephen Fever编写的。

[![](https://p4.ssl.qhimg.com/t01df947db172024100.png)](https://p4.ssl.qhimg.com/t01df947db172024100.png)

在将十六进制的shellcode字节码放入createthread.asm文件之后，就可以使用nasm -f bin createthread.asm命令进行汇编。这样，该shellcode就可以插入到代码洞了，但在插入该shellcode之前，应该对其进行加壳，以便绕过AV产品的静态/特征分析检测。因为metasploit项目中的所有加壳软件对大多数AV产品来说都熟悉不过了，所以强烈建议使用自定义的加壳软件。本文不会介绍如何制作shellcode的自定义加壳软件，因为将来会单独写一篇文章进行详细的介绍，但是如果组合使用多个metasploit加壳软件的话，也是可行的。在每次加壳之后，以原始格式将编码的shellcode上传到相应的在线查毒网站，看看免杀效果如何。尝试每种组合，直到它无法被检测到为止；如果您有耐心，那么等待下一篇文章也行。 

对shellcode成功加壳之后，就可以把它插入代码洞了。请选中PUSHFD下面的指令，然后在immunity debugger中按Ctrl + E组合键，这样shellcode将以十六进制格式粘贴到这里。

[![](https://p0.ssl.qhimg.com/t01a040501c26e2c1ea.png)](https://p0.ssl.qhimg.com/t01a040501c26e2c1ea.png)

使用xxd -ps createthread命令，以十六进制格式打印输出创建线程的shellcode，或使用十六进制编辑器打开shellcode并复制相应的十六进制值。在将十六进制值粘贴到调试器时，请注意字节限制，因为这些修改都是在immunity debugger中进行的，而对于immunity debugger来说，向编辑代码窗口中粘贴代码时，是有字节限制的。所以，我们可以每次粘贴一部分，按下OK按钮后，继续粘贴后续字节，当所有shellcode全部粘贴到代码洞之后，插入后门代码的流程便大功告成了。



**恢复执行流程**

在创建后门代码线程之后，需要恢复程序的正常执行，这意味着EIP应该跳回到将执行权限重定向至代码洞的那个函数。但是在跳回到该函数之前，应该首先将寄存器的值恢复到之前的状态。

[![](https://p0.ssl.qhimg.com/t01aa595727c1dba1b2.png)](https://p0.ssl.qhimg.com/t01aa595727c1dba1b2.png)

通过在shellcode的末尾放入相应的POPFD和POPAD指令，就可以将此前保存的寄存器的值以相同的顺序从堆栈中弹出。在恢复寄存器之后，先别忙着跳回，因为还有一件重要的事情需要处理，即我们要执行的是被劫持的指令，但是为了将程序的执行重定向到代码洞，PUSH 467C7C指令已经被替换为JMP 0x47A478了。现在，可以把这个PUSH 467C7C指令放到最后面，就能恢复被劫持的指令了。接下来，我们就可以跳回到通过插入JMP 0x41CB73指令将执行重定向到代码洞的那个函数了，代码如下所示。

[![](https://p0.ssl.qhimg.com/t01240c35c41f8f2e4a.png)](https://p0.ssl.qhimg.com/t01240c35c41f8f2e4a.png)

最后，选中相应的指令，单击右键，通过相应的选项将它们复制到可执行文件。对于这个操作，我们应该对所有被修改的指令都执行一遍。当所有指令被复制并保存到文件后，关闭调试器，然后测试可执行文件，如果可执行文件运行正常的话，那就说明后门可以使用了。

最后，建议处理好最终文件的校验和，以免引起怀疑，这也能够降低被检测出来的风险。 

[![](https://p0.ssl.qhimg.com/t01518c9f4611da8b42.png)](https://p0.ssl.qhimg.com/t01518c9f4611da8b42.png)

**<br>**

**小结**

最后，在按照上述方法正确处理之后，我们的后门就可以完全隐身了。

[![](https://p1.ssl.qhimg.com/t0184404a791a440404.png)](https://p1.ssl.qhimg.com/t0184404a791a440404.png)

<br>

**演示视频**

现在，您可以通过下列视频来观看我们安装后门后的putty的表现了：



<br>

**参考资料 **

[http://NoDistribute.com/result/image/Ye0pnGHXiWvSVErkLfTblmAUQ.png](http://NoDistribute.com/result/image/Ye0pnGHXiWvSVErkLfTblmAUQ.png)

[https://en.wikipedia.org/wiki/Red_team](https://en.wikipedia.org/wiki/Red_team)

[https://en.wikipedia.org/wiki/Address_space_layout_randomization](https://en.wikipedia.org/wiki/Address_space_layout_randomization)

[https://en.wikipedia.org/wiki/Code_cave](https://en.wikipedia.org/wiki/Code_cave)

[https://en.wikipedia.org/wiki/Checksum](https://en.wikipedia.org/wiki/Checksum)



****

**传送门**

[**【技术分享】反侦测的艺术part1：介绍AV和检测的技术******](http://bobao.360.cn/learning/detail/3420.html)

[**【技术分享】反侦测的艺术part3：shellcode炼金术******](http://bobao.360.cn/learning/detail/3589.html)

[********](http://bobao.360.cn/learning/detail/3420.html)

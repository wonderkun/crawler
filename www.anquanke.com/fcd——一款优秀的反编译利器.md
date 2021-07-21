> 原文链接: https://www.anquanke.com//post/id/83508 


# fcd——一款优秀的反编译利器


                                阅读量   
                                **96583**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://zneak.github.io/fcd/2016/02/21/csaw-wyvern.html](http://zneak.github.io/fcd/2016/02/21/csaw-wyvern.html)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p2.ssl.qhimg.com/t015ac30962ded75a6f.jpg)](https://p2.ssl.qhimg.com/t015ac30962ded75a6f.jpg)

fcd中一个备受吹捧的功能就是它可以在输出类C代码之前，对代码进行简化处理。这对于逆向工程师而言，绝对是一个福音，因为当逆向工程师在对程序进行混淆处理时，它可以提供非常大的帮助。在2015年网络安全意识周（[CSAW](https://csaw.engineering.nyu.edu/)）的CTF大赛上，Wyvern挑战赛中所发生的事情就是个很好的例子。

在资格赛和最后一轮的终极赛中，都曾出现过500分的高分，这也是CSAW CTF大赛历史上最高的个人挑战赛得分了。我们将在这篇文章中主要对资格赛第一轮－Wyvern挑战赛进行讲解。广大读者们可以查看2015年CSAW CTF挑战赛的赛事报道来获取更多具体的信息。

[下载csaw-wyvern](http://zneak.github.io/fcd/files/csaw-wyvern-9949023fee353b66a70c56588540f0ec2c3531ac)

启动程序之后，我们将会看到以下信息：

[![](https://p0.ssl.qhimg.com/t017bec9347009c215d.png)](https://p0.ssl.qhimg.com/t017bec9347009c215d.png)

当然了，在wyvern中运行strings命令并不会给我们提供任何有帮助的输出信息。所以从战略角度出发，第二步就是使用一款反汇编工具（例如objdump）来对数据进行处理。但是，这样所得到的处理结果绝对会让你疯掉的。因为在你所得到输出代码之后，你还需要对每一个字符进行检测，而且还有可能发生溢出等问题：

```
$ objdump -M intel -d csaw-wyvern2
[snip]
00000000004014b0 &lt;_Z15transform_inputSt6vectorIiSaIiEE&gt;:
  4014b0:  55                         push   rbp
  4014b1:  48 89 e5                    mov    rbp,rsp
  4014b4:  53                         push   rbx
  4014b5:  48 83 ec 48           sub    rsp,0x48
[spurious branch code starts here]
  4014b9:  8b 04 25 68 03 61 00  mov    eax,DWORD PTR ds:0x610368
  4014c0:   8b 0c 25 58 05 61 00   mov    ecx,DWORD PTR ds:0x610558
  4014c7:   89 c2                       mov    edx,eax
  4014c9:   81 ea 01 00 00 00      sub    edx,0x1
  4014cf:    0f af c2                imul   eax,edx
  4014d2:  25 01 00 00 00        and    eax,0x1
  4014d7:  3d 00 00 00 00        cmp    eax,0x0
  4014dc:   40 0f 94 c6            sete   sil
  4014e0:  81 f9 0a 00 00 00      cmp    ecx,0xa
  4014e6:  41 0f 9c c0             setl   r8b
  4014ea:   44 08 c6              or     sil,r8b
  4014ed:  40 f6 c6 01            test   sil,0x1
  4014f1:   48 89 7d f0           mov    QWORD PTR [rbp-0x10],rdi
  4014f5:   0f 85 05 00 00 00      jne    401500 &lt;_Z15transform_inputSt6vec
[snip]
```

在经过了分析和处理之后，我们得到了类似((x * (x – 1)) &amp; 0x1) == 0 || y &lt; 10的分析结果。

如果你的计算机中安装有Hex-Rays(一款反汇编利器)，那么你将会看到大量复杂的数据，你将很难从这一大堆数据中提取到你所需要的信息。因为其中的每一个数据块是由14个无用的垃圾指令所组成，而其中也并没有多少有用的指令。这就成功隐藏了大量的指令控制流信息。

在资格赛过程中，Ryan Stortz通过推特（[@withzombies](https://twitter.com/withzombies)）表示，他在第一个阶段曾使用了动态分析，而结果是非常可观的。大多数的团队（不包括我的团队）会选择使用[因特尔的Pin](https://software.intel.com/en-us/articles/pin-a-dynamic-binary-instrumentation-tool)（一款由因特尔公司研发的动态二进制指令分析工具）来对代码进行分析处理，并找出能够让程序长时间运行的输入信息。但我并不清楚这些团队在第二阶段做过什么。由于fcd无法处理如此之大的程序，所以我不得不手动来对这些代码进行凡混淆处理，直到我能够发现这些代码的实际意义。这些过程听起来会显得单调和乏味，而且即使你没日没夜地对这些数据进行，也不一定能够得到你所期望的结果。

在进行了三个多月的努力之后，我们终于可以加快我们的进程了。虽然Fcd不是最好的反编译工具，但是它还是能够处理好这一较为奇葩的任务的。

**以龙制龙**

相较于其他的反编译工具而言，fcd的一个主要优点就是用户可以编写Python优化代码，并将其提供给LLVM来对程序代码进行简化处理。LLVM能够利用不变的输出结果来查找代码，而且还能够删除无效的数据，并简化剩余的代码。所以我们只需要向LLVM提供一小段命令，LLVM就能够将剩下繁重的工作完成。所以我们就不需要在去手动处理垃圾代码了，而且LLVM还能够将一些不可预测的代码转变为一些有意义的信息。

在我们的例子中，无论是在哪一个阶段，条件变量都是从数据段中进行加载的，但是这些数据从未被修改过。所以这也就意味着，这些变量值永远等于0。利用Python语言，我们可以将这些信息写入一个优化参数中，并将其提供给fcd来进行处理。

假设你正在进行挑战赛，你首先需要做的就是找出代码中一些有意思的函数。在对数据进行了手动检查或者动态分析之后，你应该就会发现我所指的有意思的函数就是sanitize_input (0x401cc0)和transform_input (0x4014b0)，这两个函数能够对输入行数据进行转换和测试，但我们尚不清楚其具体的工作机制。

在本文的例子中，我们将会利用fcd完成以下两件事情：第一，保存可执行文件所对应的LLVM汇编文件（生成这类文件通常需要很长的时间）；第二，我们需要使用经过优化处理的fcd参数（我们的自定义参数）来进行操作。由于生成一个编译文件将会消耗大量的时间，如果我们使用自定义参数，那么将会为我们节省大量的时间。

```
from llvm import *
 
passName = "Wyvern cleanup"
 
def runOnFunction(func):
       changed = False
       bb = func.GetFirstBasicBlock()
       while bb != None:
              changed |= _runOnBB(bb)
              bb = bb.GetNextBasicBlock()
       return changed
 
def _runOnBB(bb):
       changed = False
       inst = bb.GetFirstInstruction()
       while inst != None:
              changed |= _runOnInst(inst)             
              inst = inst.GetNextInstruction()
       return changed
 
def _runOnInst(inst):
       if inst.GetInstructionOpcode() != Opcode.Load:
              return False
      
       cAddress = inst.GetOperand(0).IsAConstantExpr()
       if cAddress == None or cAddress.GetConstOpcode() != Opcode.IntToPtr:
              return False
      
       constantInt = cAddress.GetOperand(0).IsAConstantInt()
       if constantInt == None:
              return False
      
       address = constantInt.ConstIntGetZExtValue()
       if address &lt; 0x610318 or address &gt; 0x6105ac: # x and y variables
              return False
      
       zero = inst.TypeOf().ConstInt(0, False)
       inst.ReplaceAllUsesWith(zero)
       return True
```

当LLVM的封装参数被执行时，runOnFunction函数将会运行。如果参数对函数进行了修改，那么该函数的返回值必须为True。该函数将会对代码中的基本数据块进行处理，并将其传递给_runOnBasicBlock。_runOnBasicBlock会对每一个数据区块的指令进行迭代处理，并将处理后的数据传递给_runOnInst。

**舔舐伤口**

至少目前为止，我认为fcd强大的功能和出色的性能已经成功地引起了大量相关从业人员的关注。但是，由于别名分析的问题，它并没有提供分析处理后的输出结果。不幸的是，从九十年代初期开始，安全专家普遍认为别名分析是不太可能进行判定的，所以fcd也不太可能去解决这个问题。

据我了解，目前只有一个团队在对fcd进行开发工作，但是在其诞生不到一年的时间内，该项目就能够取得如此之大的成就和进步，这不得不让人对它的未来抱有很大的希望。而且，它几乎将Wyvern打得体无完肤了，这也是一个非常令人兴奋的里程碑时刻。

所以，我决定暂时不去参加比赛，我想进行更多的训练，也许当我觉得自己的水平有了一定的进步时，再去参加比赛也不迟。所以，我们需要时刻擦亮自己的眼睛！

由于篇幅有限，具体信息请查看原文。

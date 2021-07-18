
# 【技术分析】看我如何使用Cloud Fuzzing挖到了一个tcpdump漏洞


                                阅读量   
                                **102837**
                            
                        |
                        
                                                                                                                                    ![](./img/85944/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/85944/t01f9ade5a46c467768.png)](./img/85944/t01f9ade5a46c467768.png)

****

作者：[](http://bobao.360.cn/member/contribute?uid=2606963099)[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099) 

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**写在前面的话**



**Fuzzing（模糊测试）**是一种识别软件设计缺陷和安全漏洞的方法。随着技术的不断进步，Fuzzing也逐步转移到了云端（Cloud）。与传统的模糊测试技术相比，Cloud Fuzzing不仅可以提升模糊测试的速度，而且还可以提升测试的可扩展程度。在这篇文章中，我们将介绍Cloud Fuzzing的完整过程。通过这种技术（softScheck Cloud Fuzing Framework-sCFF），我成功地在Ubuntu 16.04的tcpdump（4.9版本）中发现了一个安全漏洞。感兴趣的同学可以自行下载sCFF框架，并按照本文的操作步骤动手尝试一下。

**<br>**

**一、背景知识**



第一章主要介绍的是与本文有关的一些基础知识以及测试会用到的程序。如果你之前已经比较了解Cloud Fuzzing了，你可以直接阅读第二章。但是，我们强烈建议各位按照文章顺序进行阅读。

**1.1 Fuzzing（模糊测试）**

Fuzzing是一种测试软件健壮性的技术。模糊测试，也称Fuzzing或Fuzz测试，它是一种自动化软件测试技术，主要通过向被测目标输入大量的畸形数据并监测其异常来发现漏洞，是当前安全业界流行的漏洞挖掘手段之一。从广义角度来看，该技术的关键在于如何构造有效的测试用例(输入的畸形数据)，以及如何有效的监控异常。Fuzzing技术简单、有效、自动化程度比较高，是目前工业界进行安全测试最有效的方法，被广泛应用于Web、系统、应用程序的漏洞挖掘。由于它一般属于黑盒测试，通过构造有效的畸形数据进行测试，因此该技术的代码覆盖率相对较低，且它的测试效率跟测试人员的经验和技术有很大关系。

[![](./img/85944/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0120f9b71c8e0f27d1.png)

在此之前，模糊测试通常是在本地计算机中进行的，但随着“基础设施即服务”的趋势不断兴趣，越来越多的企业开始提供云端服务了。实际上，类似微软和Google这样的大型公司早就已经在云端实现了模糊测试技术。例如在Springfield项目中，微软公司甚至已经开始向广大开发者提供Cloud Fuzzing服务了。

那么我们我什么要用Cloud Fuzzing而不用传统的模糊测试技术呢？首先，Cloud Fuzzing意味着你不需要再购买额外的电脑了，而购买测试设备不仅需要花很多钱，而且你还需要花时间去搭建和配置测试环境。但Cloud Fuzzing最大的优势就在于它所能提供的灵活性和可扩展性，它可以在短时间内完成大量的工作，并帮助测试人员节省大量的时间。比如说，Cloud Fuzzing可以在同一时间在多种不同的操作系统上对同一个程序进行模糊测试。如果一个项目对数据吞吐量有较高要求，那么这个测试实例就可以使用多块固态硬盘（RAID0配置）；如果一个程序需要大量的RAM，那么我们就可以选择一个可以提供大量RAM的配置。如果我们需要对一个Web应用或网络协议进行测试，那么Cloud Fuzzing就可以给我们提供大量的终端节点。

当然了，Cloud Fuzzing也有其不足之处。首先，你必须充分信任云端的提供方，因为你所有的一切都运行在云端设备上，而不是运行在你自己的设备中。其次，你在使用Cloud Fuzzing时是需要付费的，那么当你使用了几个月甚至几年之后，你所支付过的费用可能要比你自行购买测试设备所花的钱还要多。

**1.2 亚马逊AWS**

亚马逊Web服务（AWS）是Amazon.com所提供的一系列在线服务的集合，而AWS也是目前云计算领域中最大的巨头。AWS其中的一个组件为弹性云计算（EC2），EC2允许用户设置虚拟机，用户可以对其进行各种配置，并将其充当服务器使用。用户所创建的一个实例本质上就是云端的一台虚拟服务器，它由操作系统和软件应用所组成，用户在创建的过程中还可以自行分配服务器所需的资源。除此之外，用户也可以在亚马逊设备镜像（AMI）库中选择需要的操作系统，而且亚马逊也给用户提供了一百多种不同的机器配置选项，用户可以根据自己的需要来选择配置文件。用户付费是按机器运行小时来付费的，而高配置实例的成本要比低配置实例要低得多。

**1.3 softScheck Cloud Fuzzer Framework**

为了尽可能地简化模糊测试的过程，softScheck的技术人员开发出了softScheck Cloud Fuzzer Framework（sCFF）。sCFF采用Python 3编写，并使用Boto 3 API来与AWS通信。sCFF由多种子程序组成，其中的每个工具都可以完成多项任务。

在下图中，我们根据模糊测试的阶段来对sCFF子程序进行了分类：

[![](./img/85944/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0128ef6a341dd6fc5d.png)

如果你想深入了解sCFF的架构和技术细节，请阅读这篇文章【[sCFF论文](https://www.softscheck.com/publications/Pohl_Kirsch_scff_paper_170405.pdf)】。

**1.4 American fuzzy lop**

American fuzzy log（afl）是sCFF所使用的模糊测试器（fuzzer），afl以其测试速度、稳定性和操作界面而为人所知，而且它可以帮助我们发现软件中的各种漏洞。如果我们拥有测试目标的源码，那么它在对源码进行了分析之后，不仅能够生成更加合适的测试向量，而且还可以显著提升测试覆盖率。而在给定的时间里，代码覆盖率越大，那么扫描到安全漏洞的可能性也就越高。下图显示的是afl的运行界面：

[![](./img/85944/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ab53d85ebb11c6aa.png)

**1.5 tcpdump**

众所周知，Tcpdump是一个网络数据包分析器，它可以捕捉、显示、并以[pcap文件格式](https://wiki.wireshark.org/Development/LibpcapFileFormat)保存目标网络所发送的数据包。与Wireshark不同的是，Tcpdump可以通过简单的命令（无需交互）来运行，这样可以让模糊测试过程变得更加简单。

**1.6 GNU Debugger**

在GNU DeBugger（[GDB](https://www.gnu.org/software/gdb/)）的帮助下，我们可以对软件的运行状态进行一步一步地分析，以便我们找出软件崩溃的原因。

<br>

**二、使用sCFF来对tcpdump进行模糊测试**



在了解完基础知识之后，接下来让我们尝试寻找一下tcpdump 4.9中存在的漏洞。

**2.1 准备工作**

如果你想要找出tcpdump中的漏洞，你首先要配置AWS实例和sCFF。

要求：

–[创建一个AWS账号](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html)；

–[导出AWS密钥ID和密钥](http://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html)；

-.aws/config中应该包含你的地区信息，.aws/credentials中应该包含密钥ID和访问密钥；

-创建一个SSH安全组，并允许实例与外部端口22之间进行通信；

-创建并下载[密钥对](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html)（SSH通信需要使用到这些密钥）；

–[下载](https://github.com/softscheck/sCFF)并安装sCFF；

**2.2 预测试阶段**

准备工作完成之后，我们要下载tcpdump v4.9的源代码。当然了，你也可以直接使用git来下载tcpdump的最新版本，虽然本文所描述的漏洞在新版本中已经修复了，但你说不定可以使用本文的方法找出新的漏洞呢？

下载完成之后，我们可以使用“CC=afl-gcc ./configure &amp;&amp; make”命令来编译源码。

编译成功之后，我们通过“scff-mkconfig”命令来创建一个sCFF项目文件。请确保将target参数设置为“tcpdump”，将“args”参数设置为“–e –r @@”。其中“-e”和“-r”都是tcpdump的参数，“-e”表示打印出数据包中的扩展header，“-r”用于读取文件。下面是我们通过“scff-mkconfig”命令创建出的配置文件：



```
[INSTANCES]
ami = ami-0963b466
gid = tcpdump49
instancetype = t2.micro
name = auto
numberofmachines = 4
platform = linux
 
[FUZZING]
dependencies = none
fuzzer = afl
fuzzdir = fuzzing
inputdir = fuzzing/input
outputdir = fuzzing/output
template = ipv4.pcap
target = tcpdump
args = -e -r @@
```

注：现在，亚马逊允许用户通过“scff-create-instances”命令来创建EC2实例。<br>

**2.3 测试阶段**

接下来，我们可以通过命令“scff-ctrl . bootstrap”来对用于Fuzzing测试的设备进行配置。配置完成之后，模糊测试便开始了。sCFF允许我们选择单模Fuzzing和分布式Fuzzing。在单模Fuzzing下，每一个实例都会运行一个fuzzer；二在分布式Fuzzing中，虽然仍是每一个实例运行一个fuzzer，但fuzzing数据会在实例间共享，这样可以提升测试速度。如果你拥有两个以上的实例，我们推荐使用分布式Fuzzing模式（命令：“scff-ctrl . distributed”）。如果想要了解测试的状态，我们可以通过浏览器来访问云服务器进行查看，并通过命令“scff-ctrl . grab-findings”来下载错误日志。

[![](./img/85944/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bc90d2b84a7ae0b1.png)

**2.4 测试完成后**

“scff-exploitcheck”命令将会对我们的发现进行分析，假阳性和重复出现的崩溃信息将会被过滤，最后剩下的信息将会用于漏洞的检测和利用。

[![](./img/85944/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c740be30911a68ba.png)

如果找到的信息有红色的“EXPLOITABLE”标签标注，那么这里存在漏洞的可能性就非常高了。正如上图所示，tcpdump 4.9的文件printsl.c中存在一个可利用的漏洞。接下来，我们用GDB来对崩溃信息进行分析：

[![](./img/85944/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011c0231a511466375.png)

分析后我们可以看到，dir为255，而且dir也是lastlen其中的一个引用参数（定义为lastlen[2][255]），这里存在参数越界，而正是这一点导致了崩溃的出现。

如果要解决这个问题，我们可以更正dir的值，或者检查dir的值是否在0到2之间。现在，我们可以在dir = p[DIR_SLX]后面设置一个断点，然后在gdb中修改dir的值，感兴趣的同学可以自己尝试写一个补丁【[参考资料](https://www.softscheck.com/en/identifying-security-vulnerabilities-with-cloud-fuzzing/#collapsePATCH)】。

修复之后，再对源码重新进行编译，然后检查程序是否还会崩溃。

[![](./img/85944/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013ef7764ec1c34308.png)

**<br>**

**三、总结**



这个漏洞并不是非常的严重，因为攻击者必须要让目标用户使用“-e”参数来打开pcap文件才可以完成攻击。虽然攻击难度较大，但这仍然是一个安全漏洞。我们也将该漏洞上报给了tcpdump的安全团队，这个漏洞将在tcpdump v4.10中得到修复。

整个测试过程大约需要五个小时，其中包括发现并修复漏洞。



```
Downloading and compiling tcpdump:            10 minutes
Pre Fuzzing Phase + template generation:     10 minutes
Fuzzing Phase:                               110 minutes
Post Fuzzing Phase:                       60 minutes
Patch writing and retesting:                90 minutes
-----------------------------------------------------------
Total:                                          300 minutes
```



**参考资料**



1.[https://www.softscheck.com/en/softscheck-blog/](https://www.softscheck.com/en/softscheck-blog/)

2.[https://www.softscheck.com/en/identifying-security-vulnerabilities-with-cloud-fuzzing/#collapsePATCH](https://www.softscheck.com/en/identifying-security-vulnerabilities-with-cloud-fuzzing/%23collapsePATCH)

3.[https://wiki.wireshark.org/Development/LibpcapFileFormat](https://wiki.wireshark.org/Development/LibpcapFileFormat)

4. [https://www.gnu.org/software/gdb/](https://www.gnu.org/software/gdb/)

5. [https://www.softscheck.com/publications/Pohl_Kirsch_scff_paper_170405.pdf](https://www.softscheck.com/publications/Pohl_Kirsch_scff_paper_170405.pdf)

6. [http://lcamtuf.coredump.cx/afl/](http://lcamtuf.coredump.cx/afl/)

7. [https://www.microsoft.com/en-us/springfield/](https://www.microsoft.com/en-us/springfield/)



> 原文链接: https://www.anquanke.com//post/id/250893 


# 一种基于模板的针对Android进程间通信的自动化Fuzzing方法


                                阅读量   
                                **36064**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者acm，文章来源：dl.acm.org
                                <br>原文地址：[https://dl.acm.org/doi/abs/10.1145/3407023.3407052﻿](https://dl.acm.org/doi/abs/10.1145/3407023.3407052%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t017cd136f9b402954d.jpg)](https://p0.ssl.qhimg.com/t017cd136f9b402954d.jpg)



## 摘要

模糊测试fuzzing是一种通过向目标发送非预期输入并监控异常输出结果来发现crash的漏洞测试方法。我们此次目标是在安卓的IPC机制上进行fuzz，通过自动化fuzz来找安卓应用程序间的通信机制bug。 Android上的沙箱机制会确保应用程序只能通过编程接口与其他应用程序通信,与传统操作系统不同，两个安卓程序在相同的用户上下文环境运行时不能相互访问数据或执行退出操作。

本文提及的IPC fuzzer方法通过程序拆解和分析应用程序的字节码来实现fuzz功能，而且该fuzzer支持输入生成分析和输出后结果分析，这些结果可以使我们了解崩溃原因详情。我们通过对谷歌商店上架的1488个应用进行fuzz测试，发现能在450个应用中引发崩溃。并且值得注意的是，这些缺陷同时也存在于Unity、谷歌服务API和Adjust SDK中。与之前类似研究相比，本文在crash检测的深度和广度上均有提升。

关键词：fuzzing，Android安全，进程间通信



## 1 简介

Fuzzing一种通过随机输入来测试软件的技术， 任何程序或库均可做fuzz，比如导出api、读取文件、用户输入字段或网络通信信息等等。 Fuzzing自动化比率很高，因而被广泛应用于测试工作中，因为一个fuzzer启动并运行后就可以脱离人的操作而独立寻找bug。

本文提出了一种针对Android的IPC机制的基于模板的自动模糊处理方法。 众所周知，Android上的IPC消息被称为Intents，因此我们做了一个Intent fuzzer并将其集成到开源安全审计工具drozer中。 与之前的Android IPC消息的fuzzing工作相比，我们对应用程序的组件结构进行更广泛的预分析，并改善了基于模板的代码覆盖率所需的条件。<br>
通过对1488个应用进行Fuzzing，我们发现有450个应用可以引发崩溃，其中不乏比较出名的谷歌框架。这项研究主要关注的是本应用程序暴露给其他应用程序接口的代码稳定性，不关注代码执行问题。



## 2 背景

Android的IPC模式与普通的桌面操作系统不同，是由Android的binder实现的，binder机制充当了应用程序之间的媒介。

Android的Binder机制的核心是它的内核驱动程序，它负责处理不同进程之间的所有通信，即所有的通信均由系统API提供的Binder API完成。 从客户端发送到服务器端的过程称为transaction事务，事务可以调用内核驱动程序完成整个服务。 此外，每个transaction事务可以包含一个贮存在Parcel容器中的载荷，并且transaction事务可以被单向异步执行或者双向同步执行。

对应用程序本身而言，前面所讲的Binder其实是Intent的抽象概念。Intent对象为数据提供了一些标准字段，但大多数情况下，载荷选择使用Bundle进行发送任务。可以说Android系统中的Bundle是一个包含一组键值对的映射，这些映射可以使得Intent轻易找到目标对象。显式Intent和隐式Intent的使用方法是不同的，显式Intent规定信息传递给提前被确定好的特定应用程序，而隐式的Intent则广播给支持该操作的任何应用程序。

程序的主要组件包括：Activities活动，Services服务和Broadcast Receivers广播接收器。Activity可以是用户操作的活动，比如提供图形界面与用户交互，我们可以通过Intent创建或调用一个新活动。由于设定限制，Android系统一次只能在前端运行一个Activity。后台运行通过Services实现，Services不提供用户界面，即使用户切换另一个应用程序，Services也会继续通过广播接收器来接收从操作系统或其他应用程序发来的广播以传播信息并触发行为。



## 3 设计与实现

本节主要介绍设计方面的注意事项和实现方法，该实现方法目前处于开源状态。下图即为我们的fuzzing实现方法：

[![](https://p1.ssl.qhimg.com/t01c74a1ed23231f0de.png)](https://p1.ssl.qhimg.com/t01c74a1ed23231f0de.png)

首先，APK文件会被静态分析器模块解析，输出有效Intent并建立Intent模板。这些Intent模板会被推送至相关引擎并存储在数据库中，接着drozer模块会把APK安装在专用设备上并启动fuzzing，同时设备的日志也会记录并储存fuzzing引发的崩溃、异常信息到crash数据库中，其堆栈使用情况也会被保存下来。

同样的，作为fuzz对象的intent的拓扑结构也很重要，毕竟我们希望输入测试的行为意图越密集越好，而且想触发尽可能多的执行路径。Android的manifest给出部分Intent信息，比如URI信息，比如以映射形式储存载荷的字段。manifest文件不包含结构信息，因此必须进行源代码分析。

但Intent类定义了一组提取映射方法，因此可以跟踪Intent相关方法的所有调用，从而获得每个组件所期望映射的所有列表信息。 我们从每个被导出组件开始入手搜索这些映射，就可以找到Intent和期望域的依赖关系字段。依靠这些依赖情况，我们就创建Intent模板，每个被导出组件的有效Intent应该包含以下信息：必要字段，键值映射以及它们被解压成的数据类型。有了这些信息，我们的Intent引擎就可以启动Intent的map构建及优化过程了。

在进行Intent结构模板构建的时候，我们先从上述已提供的模板中生成有效的包含了预期数据类型的Intent信息，信息至少应包括行为、数据类别，以及附加字段。然后，我们将涉及调用部分的Intent结构进行修改优化。此外，在引擎设计中，我们通过随机初始算法进行模板信息随机填充。在完成模板创建之后，我们就可以使用这些模板来进行真实数据集作为测试集的fuzz工作了。我们在测试设备上安装了drozer代理，这样我们就可以与测试机的安卓系统进行交互并向测试机发送intent模板进行测试。

同时我们也设定了时间间隔机制来确保测试尽可能相互独立。运行时的crsah日志信息包含了包括Java堆栈的所有崩溃相关信息，这些信息按受影响的组件进行分组，即每个组件分组下都有引发该组件崩溃的相关日志信息。



## 4 价值分析

我们对在谷歌应用商店上架的1488个应用进行了模糊测试，测试设备是Android 9.0系统的Nexus 5X。这1488个测试应用中有921至少有一个组件在测试期间crash，有450应用程序在测试期间完全crash。导出的组件。通过分析未发现导出的组件数量与检测到的有crash组件数量之间有任何相关性，即组件较多的应用不一定比组件少的应用更容易崩溃，然而暴露更多的信息的确很容易增大被攻击机会。 通过分析我们共发现了635个组件容易受到攻击，且存在发送一个intent就能使450个应用crash的情况。

除了其他研究者发现的NullpointerExceptions是activity引起crash的主要原因以外，我们也发现了一些其他类型的crash，在下表中列出。该表列出了所有fuzzing结果中导致应用程序crash的组件的频率，并进行了排序。

[![](https://p2.ssl.qhimg.com/t01e7f3b10eb48fae7b.png)](https://p2.ssl.qhimg.com/t01e7f3b10eb48fae7b.png)

此外，我们将异常crash情况分成了三组，分别是转换异常， Unsupported Exceptions和溢出。 转换异常包括class cast异常，illegal argument异常和Number Format异常，这些异常都是因为fuzz未能进一步通过映射完成符合APP逻辑的结构探索引发的，其通常在数据转换时发生失败。对于class cast异常情况来说，大多数是指组件试图将一个对象转换成另一个类型，但目标类型不是当前对象的子类型。对于Number Format异常来说，情况大多数是程序试图将字符串类型转换为数字类型，但是字符串格式不合适。

Unsupported Exceptions包括Illegal State异常，Invocation Target异常和Unsupported Operation异常，这些异常通常是由于应用程序解析逻辑不符造成的，实验证明主要的crash原因就是这些。溢出是在Intent执行数组操作时产生的，例如Index Out Of Bounds异常等等，这种异常通常在组件尝试读取数组或集合中指数时引发。

在我们的实验中，我们注意到并不是所有的crash都是由开发人员代码中的bug引起的， 而第三方框架也会对应用程序IPC产生严重影响。 值得注意的是:<br>
（1）Google Play Services提供了各种可被集成在程序中的不同的API，其中一些API可能会引发crash，而这些crash问题大多都与broadcast receiver有关。<br>
（2）在用户需要更复杂图像功能时，有些人会选择Unity作为图像引擎，例如应用在游戏中。 因此，unity提供了自己的交互编辑器编译环境。我们在unity的VRPurchaseActivity组件中发现了NullPointer异常， 这说明PurchaseActivity的解包过程存在缺陷且可能引发功能。<br>
（3）企业会使用Adjust功能收集统计数据，这个SDK可以用于检测用户访问应用程序的次数和使用程序时间，在实验中我们发现Adjust Referrer Receiver组件会引发crash。 而在一些google play service中，发送包含在intent中的畸形URI也会引发崩溃。



## 5 同类型的FUZZER比较

ComDroid，IntentFuzzer，NCCgroupfuzzer和Fuzzinozer框架都是针对Android的IPC机制的fuzzer，。 Comdroid方法使用半自动化的、动静分析混合的策略来评估intent对象、活动或服务，它可以检测潜在的漏洞，侧重于未经授权的intent receipts和intent欺骗，这种设计策略与我们的策略是相反的。

Sasnauskas等人构建UI测试框架Monkey和FlowDroid实现IPC fuzzer。与我们的工作类似，这项研究也关注到了intent结构。 然而，他们始于空intent而我们关注的是静态处理后的组件中的intent，这样我们就创建一个更大的有效集。我们认为通过这样的方式，我们就可以得到更多的异常抛出和crash，也就更容易扩大检测范围和得到检出结论。该想法同样也在NCC Fuzzer中得到了证实，但是代码覆盖率只增加了1%。

Fuzzinozer方法与本文中提出的fuzzer比较相似，它的主体是一个Drozer框架的扩展模块（NCC goup fuzzer是个独立框架）。在设计方法上与本文不同的是， Fuzzinozer不依赖于任何静态分析方法，且从null intent开始进行随机的fuzzing工作，且未进行log分析。具体这些fuzzing方法的测试情况如下：

[![](https://p0.ssl.qhimg.com/t011c9f4383656bdd30.png)](https://p0.ssl.qhimg.com/t011c9f4383656bdd30.png)



## 6 结论

本文提出的基于模板的fuzzing方法通过对drozer框架进行拓展开发而落地实现，通过该设计方法可以发现一些开源第三方库的漏洞。

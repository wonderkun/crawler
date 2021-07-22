> 原文链接: https://www.anquanke.com//post/id/218258 


# 动态DL驱动架构对抗复杂的安卓恶意软件


                                阅读量   
                                **197115**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者dtu，文章来源：orbit.dtu.dk
                                <br>原文地址：[https://orbit.dtu.dk/files/217218590/Hkkr_09142180.pdf](https://orbit.dtu.dk/files/217218590/Hkkr_09142180.pdf)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t016668cd8e6220c08a.png)](https://p3.ssl.qhimg.com/t016668cd8e6220c08a.png)



## 摘要

占主导地位的Android操作系统不仅在智能手机行业，而且在全球范围内吸引了巨大的关注，各种智能设备。开放式的架构和应用编程接口(API)，同时托管第三方应用程序，导致各种普遍的复杂的Android恶意软件生产爆炸性增长。在本研究中，我们提出了一种稳健、可扩展、高效的Cuda多类恶意软件检测技术，利用Gated Recurrent Unit(GRU)来识别复杂的Android恶意软件。我们使用当前最先进的Android应用数据集（即Android恶意软件数据集（AMD）、Androzoo）对所提出的技术进行了实验。此外，为了严格评估所提出的技术的性能，我们采用了标准的性能评估指标（如准确率、精度、召回率、F1-score等），并与我们构建的DL驱动架构和基准算法进行了比较。基于GRU的恶意软件检测系统在速度效率微不足道的情况下，恶意软件识别的检测精度达到98.99%，表现优异。



## 第一节.介绍

从传统设备到智能设备的演变已经彻底改变了世界。目前，无论是个人还是商业用途的智能设备都出现了指数级的增长。根据Gartner发布的报告，2019年约有4亿部智能手机被售出。通过分析智能手机的普及程度，利益相关者对开发专有移动操作系统（OS）也表现出浓厚的兴趣。Android作为一个开源和通用的平台，被认为是电信行业的领先巨头，也是各智能手机制造商的事实标准。在2019年，Android是最主要的操作系统；在全球智能手机行业中占有约74%的市场份额。此外，除了智能手机外，安卓系统还占据了智能手表、平板电脑、电视、数码盒子等。

由于Android的盛行环境，它正成为网络对手的潜在目标。恶意软件开发者的主要动机是利用现有的操作系统漏洞来制作复杂的恶意软件。恶意软件是指故意设计的恶意软件变种（即病毒、木马、间谍软件、广告软件和勒索软件等）的集合，以对数据和系统造成广泛的破坏，如权限升级、信息窃取、远程控制和隐私泄露等。复杂的恶意软件是非常无懈可击的，简直可以让整个行业陷入混乱。此外，由于Android恶意软件对企业和终端用户的影响巨大，恶意软件的增长也在持续增加。文献显示，恶意软件有可能获得安卓系统的root权限，并且后续无法追踪。

网络攻击者设法产生前所未有的破坏程度，如利用零日漏洞利用多样化的工具和策略来破坏各种系统。为了扭转不断发展的网络威胁的影响，这种情况使得恶意软件检测技术值得研究和改进。深度学习技术可以帮助及时高效地应对Android环境下动态演变的恶意软件。在本文中，我们提出了一种高效、可扩展的基于深度学习(DL)的恶意软件检测方案，采用门控循环单元(GRU)来及时、高效地全面检测各种Android恶意软件。

### <a class="reference-link" name="A.%20%E8%B4%A1%E7%8C%AE"></a>A. 贡献

本研究的主要贡献是多方面的。

```
作者提出了一种灵活、创新和可扩展的基于DL的检测机制，利用循环神经网络(RNN)，特别是门控循环单元(GRU)来有效识别Android环境中的多类攻击。
为了全面评估Android环境下的多类攻击和不断演变的恶意软件，采用了当前最先进的公开可用的Android数据集（即AMD、Androzoo）。
标准的性能评估指标（即准确度、精确度、召回率、F1-score等）已经被用来全面评估我们提出的机制。此外，我们提出的技术在检测精度方面表现优异，但在计算复杂度方面却有微不足道的折衷。
此外，我们还将我们提出的技术与我们构建的其他DL驱动算法（即长短期记忆、卷积神经网络和深度神经网络）和当前的基准进行了比较。
```

### <a class="reference-link" name="B.%20%E7%BB%84%E7%BB%87%E7%BB%93%E6%9E%84"></a>B. 组织结构

余下的论文按以下方式进行调整；第二节为相关文献。第三节是关于利用的算法的详细架构描述，第四节是关于我们提出的系统（即系统设计、数据集和构建的算法）的详细概述。第四节包括我们所提出的系统的详细概述（即系统设计、数据集和构建的算法）。 第五节讨论了实验结果和我们的评估结果。最后，第六节是本文的结论，并确定了未来的发展方向。



## 第二节. 相关工作

在最近的工作中，研究人员提出了不同的恶意软件检测框架，以防范Android中不断发展的复杂恶意软件。目前的大部分作品都是基于人工智能的二进制恶意软件识别系统。然而，深度学习(DL)结构如卷积神经网络(CNN)、深度信念网络(DBN)、循环神经网络(RNN)、深度神经网络(DNN)等，仍处于对Android平台致命性多类攻击进行综合评估的初级阶段。

在[11]中，millar等人提出了Android恶意软件检测框架，利用歧视性对抗网络(DAN)对混淆和未混淆的应用进行恶意或良性分类。在Drebin数据集上进行实际实验，达到了97%的平均检测精度。Lee等人在中提出了一种采用门控循环单元（GRU）和卷积神经网络（CNN）的恶意软件识别方案。该实验对从VirusTotal收集的约200万个样本进行了检测，检测准确率达到97.7%。该研究[13]实现了深度神经网络(DNN)架构对恶意Android应用进行分类。基于Android包包(APK)的二进制分类数据集已被用于评估所提出的框架，达到95%的检测准确率。Alzaylaee等人在中提出了一个DL-Droid框架，通过使用输入生成方案来检测恶意Android应用，以实现高效的代码覆盖率并提高性能。从Android应用和正版API调用中提取特征。实验在31,125个Apk上进行，其中11,505个是恶意软件，19,620个是来自Intel-Security(McAfee Labs)的良性样本。所提出的框架获得了95.2%的检测精度。此外，在中，作者提出了一个使用系统调用的恶意软件检测框架，同时采用长短期记忆（LSTM）。所采用的数据集(即Drebin)包含3567个恶意应用和3536个良性应用，检测准确率为93.7%。

此外，在中还开发了一个实时自动化的框架来对恶意和良性的Android应用进行分类。本文提出的基于Gated Recurrent Unit(GRU)的框架利用Contagio恶意软件转储数据集实现了91.42%的检测准确率。

C. Hasegawa等人在中提出了一种利用卷积神经网络(CNN)分析原始APK的轻量级恶意软件识别技术。本研究考虑的数据集包含5000个恶意软件和2000个来自AMD和Drebin数据集的良性Android应用。该框架采用了10倍的交叉验证技术，保证了97%的平均检测精度。利用权限和API调用，提出深度神经网络(DNN)对Android恶意应用进行分类。该框架在Drebin数据集上表现优异，检测准确率达到97%。为了检测Android复杂的恶意软件，Karbab等人提出了一个名为MalDozer的系统，从不同API调用的原始数据中确定恶意软件序列。该系统采用了人工神经网络(ANN)，获得了90%的检测精度。The utilized datasets for proposed framework are Malgenome-2015 with 1K samples, Drebin-2015 with 5.5K samples, MalDozer dataset with 20K samples。此外，从google play store下载了38k个良性Android应用。为了将APK的二进制数据转换为图像，研究在中提出了基于图像纹理的分类机制。该技术利用深度信念网络(Deep Belief Network，DBN)，提取API调用、权限和活动等特征。该框架在Drebin数据集上进行了实验，取得的结果表明，图像纹理与API调用结合后可以获得95.6%的检测准确率。在中，Zhang等人提出了基于卷积神经网络(CNN)的Android恶意软件检测的DeepclassifyDroid。包含5546个恶意应用和5224个良性应用的数据集达到了97.4%的准确率，这也揭示了系统性能的不足，需要有足够实例存在的数据集。然而，建立了一种利用深度神经网络(DNN)进行动态以及静态分析的恶意软件识别的DDefender技术。该数据集由4208个Android应用实例组成，实现了95%的检测准确率，这对于系统的实时部署来说是不够好的。Li等人在[23]中实现了一种基于API调用和权限设计深度相信网络(DBN)的恶意软件识别系统。所提出的方案考虑了Drebin数据集进行实验，达到了90%的检测精度。

此外，长短期记忆(LSTM)被用于Android中的恶意软件特征分析。该数据集包含1738条Android应用程序的记录，分别获得93.9%和97.5%的动态和静态分析的检测准确率。研究[25]提出DeepRefiner恶意软件识别框架同样利用长短期记忆（Long-shortemory，LSTM）实现了特征提取过程的自动化。Deep-Refiner考虑的数据集有62,915个恶意软件和47,525个良性Android Apk’s。所提出的技术的检测准确率为97.74%，但对于实时部署所提出的框架来说还是不够的。因此，在中提出了基于卷积神经网络(Convolutional Neural Network, CNN)的Android恶意软件检测系统，将Android应用程序表示为RGB颜色代码。编码后的图像作为输入传给CNN分类器，实现特征提取和执行过程的自动化。所提出的方法对豹子移动公司的829356个Android应用的检测精度达到了97.25%。在中提出的技术利用多样化的基于DL的分类器(即CNN、RNN、DAE、DBN和LSTM)，通过考虑请求的权限、组件和过滤的意图来高效检测Android恶意软件。在实际实验中，Drebin和Virus-share数据集对LSTM的检测准确率达到93.6%。为了检测复杂的恶意软件，提出了多模态卷积神经网络(CNN)来反映Android应用的恶意或良性属性。通过基于相似性的特征提取方法提取特征向量，同时使用权限、API调用等。数据集包括41260个应用（即Virus-Share、Malgenome Project、Google Play App Store和Virus-Total），检测准确率达到98%。

参考文献提出了基于自然语言处理（NLP）的Android恶意软件分析技术。所提出的系统将系统调用序列视为文本文件。该数据集包含Android虚拟设备(AVD)系统调用数据集中共有14231个应用程序，获得了93.16%的准确率。Singh等人在中提出了传统的机器学习和深度学习模型用于普适性恶意软件检测。考虑的算法有决策树、随机森林、梯度提升树、K-NN、深度神经网络（DNN）和SVM。然而，SVM表现更好，有97.16%的检测精度。本研究利用的数据集包括少量的实例(即494个应用程序)。此外，开发了Auto-Droid(Android恶意软件自动检测)，而不是依赖于manifest文件中提到的API调用，该技术使用了Android操作系统内核的smali代码的API调用。该模型使用深度信念网络(DBN)和堆栈式自动编码器(SAE)对新的未知恶意软件进行检测，获得了95.98%的性能。

参考文献提出了基于深度流的深度信念网络(DBN)，用于基于数据流对不同于良性应用的恶性应用进行恶意软件识别。所提出的系统对3000个良性应用和8000个恶意应用进行执行，获得了95.05%的准确率。在中探索卷积神经网络(CNN)通过将字节码转换为文本来检测恶意软件的能力。提出的框架具有从原始数据中自动提取特征的优势。实验在不同的数据集上执行。基因组项目和McAfee实验室的数据集上进行了实验。实验在不同的数据集上执行：基因组数据集和McAfee实验室数据集，模型利用基因组数据集达到98%的准确率，McAfee数据集的准确率为87%。在中开发的抗对抗技术，阻碍了对抗者构建对抗样本。实验中采用MNIST CIFAR-10中的14,679个恶意软件和17,399个良性变种的数据集进行了基于DNN的框架。实验结果表明，该技术的检测精度达到了95.2%。本研究的框架利用LSTM层和词袋技术将Android权限转换为特征。网络安全数据挖掘大赛(CDMC2016)数据集已被利用，并达到89.7%的检测精度。

给出的文献对比(见表1)非常明显，DL模型仍在开始向全面评估Android环境下的多样化多攻击发展。显然，现有的大部分机制都是针对二进制分类而设计的。此外，本研究提出了基于cuda-empowered GRU的检测框架，以广泛评估DL模型对复杂Android恶意软件的检测。

表1 Android恶意软件检测的部分前期研究报告

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun.t1-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun.t1-3009819-large.gif)



## 第三节. 前言

在此，我们简要介绍了各种不同的DL算法（即门控循环单元、长短期记忆（LSTM）、卷积神经网络（CNN）和深度神经网络（DNN））的基本架构和解释。

### A. 门控循环单元(GRU)

Gated Recurrent Unit (GRU)，是标准Recurrent Neural Network (RNN)的强大变种，类似于LSTM利用组合门控机制作为短期记忆的解决方案。GRU有一个称为门的内部机制，可以调节甚至循环信息流。门控帮助GRU细胞了解哪些信息是重要的，需要存储或删除。因此，重要的信息被进一步传递，以进行预测。遗忘门和输入门也被连接在一起，设计了一个更新门Zt 。更新门负责保持以前的记忆量和新的信息量，xt是当前的输入向量，ht-1基本上是以前相邻层计算出来的值。然而，Wz是更新门的可学习权重矩阵。

[![](https://p5.ssl.qhimg.com/t016de6145bfc9ea2b3.jpg)](https://p5.ssl.qhimg.com/t016de6145bfc9ea2b3.jpg)

GRU还在复位门rt处将当前输入与之前的存储器相结合。此外，rt负责决定方程究竟如何结合以前的状态和新的输出。

[![](https://p1.ssl.qhimg.com/t018d5d6f6ea1e60667.jpg)](https://p1.ssl.qhimg.com/t018d5d6f6ea1e60667.jpg)

Tanh是一个双曲正切函数。tanh的输出范围是（-1,1）。此外，ht是当前单元的计算值。

[![](https://p1.ssl.qhimg.com/t01659e47930be457e1.jpg)](https://p1.ssl.qhimg.com/t01659e47930be457e1.jpg)

GRU的架构比标准RNN简单，但被证明是性能和速度高效的。GRU的基本架构见图1。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun1-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun1-3009819-large.gif)

图1.基本门控循环单元（GRU）的架构

### <a class="reference-link" name="B.%20%E9%95%BF%E7%9F%AD%E6%9C%9F%E8%AE%B0%E5%BF%86"></a>B. 长短期记忆

长短期记忆(LSTM)是Recurrent Neural Network(RNN)的一个变种，是一种用于时间数据挖掘和学习的不可思议的分类器。LSTM模型利用被称为恒定误差转盘(CEC)的非凡模块，通过时间传播恒定误差信号来学习长期特征和依赖性。此外，通过利用精心设计的 “门 “结构，防止反向传播的错误。CEC的内部值由 “门 “的状态决定，根据当前的信息和以前的流量来控制数据蒸汽和内存。一个LSTM单元由三个门和两个状态组成，分别命名为输入门、遗忘门、输出门、隐藏状态和单元状态。给定一个输入序列x = `{`x1+x2,……,xt `}`，其中LSTM结构中的输入门、遗忘门和输出门，分别记为it , ft和ot，附加在它们身上的权重为Wi , Wf , Wo , bi , bf和bo 。对于每个时间步长，LSTM更新两个状态，即隐藏状态ht和单元状态ct，σ符号用于sigmoid函数。LSTM的基本和单元结构如图2所示。ht-1为上一层的输出值，xt为当前的输入向量，bf为忘门偏置，Wf为权重矩阵。

[![](https://p3.ssl.qhimg.com/t014aacac65f6a5b3fa.jpg)](https://p3.ssl.qhimg.com/t014aacac65f6a5b3fa.jpg)

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun2-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun2-3009819-large.gif)

图2.基本LSTM单元的结构图

在决定了要保留的信息后，下一步就是更新状态，它是通过输入门it来实现的。

[![](https://p3.ssl.qhimg.com/t0192c07a528b98e720.jpg)](https://p3.ssl.qhimg.com/t0192c07a528b98e720.jpg)

作为双曲正切函数的Tanh，生成一个新的候选值向量，ct。

[![](https://p0.ssl.qhimg.com/t01d212ce7b1d7aa552.jpg)](https://p0.ssl.qhimg.com/t01d212ce7b1d7aa552.jpg)

决定改变的当前候选值是通过旧值和ft的乘法来完成的。 此外，it*ct被添加到公式中。

[![](https://p0.ssl.qhimg.com/t01b9edb0c2b9314e68.jpg)](https://p0.ssl.qhimg.com/t01b9edb0c2b9314e68.jpg)

最后，得到单元状态的滤波输出ot作为最终输出。

[![](https://p4.ssl.qhimg.com/t01f1e29cb334ca5435.jpg)](https://p4.ssl.qhimg.com/t01f1e29cb334ca5435.jpg)

对于一个典型的LSTM单元，序列数据被认为是LSTM单元的输入，隐藏层与输入层完全连接。LSTM输出层的大小取决于要分类的类数。

### <a class="reference-link" name="C.%20%E5%8D%B7%E7%A7%AF%E7%A5%9E%E7%BB%8F%E7%BD%91%E7%BB%9C"></a>C. 卷积神经网络

卷积神经网络在图像识别、语音识别、计算机视觉、自然语言处理等领域取得突出成绩后，目前正在网络安全领域繁荣扎根。与传统的特征选择算法相比，CNN可以自动学习重要特征。CNN被认为是一个相互连接的处理组件序列，旨在将输入集转化为图4中的所需输出集。输入、输出和隐藏层是CNN分类器的主要组成部分。CNN对输入数据进行多种操作，包括卷积、池化、扁平化和填充，最后网络关系到一个完全连接的神经网络。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun3-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun3-3009819-large.gif)

图3.提出的基于GRU的Android恶意软件检测方案的简化概述

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun4-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun4-3009819-large.gif)

图4.卷积神经网络的基本架构

### <a class="reference-link" name="D.%20%E6%B7%B1%E5%BA%A6%E7%A5%9E%E7%BB%8F%E7%BD%91%E7%BB%9C"></a>D. 深度神经网络

深度神经网络(DNN)[38]被公认为是标准的人工神经网络，输入层和输出层之间有多个相互连接的层。DNN找到正确的数学计算，将输入转化为输出。DNN的单层包含多个神经元，在这里进行计算。节点接收输入，利用存储的权重进行运算，应用激活函数，最后将信息传递给下一个后续节点，直到得出结论。图5描述了DNN的完整简化概述。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun5-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun5-3009819-large.gif)

图5.深度神经网络的基本架构



## 第四节. 方法

图3为所提出的图形处理单元(GPU)支援GRU的深度学习方案在Android恶意软体检测中的简化概述。第一阶段的数据采集阶段主要是生成数据集，包括从Android软件包(Apk)中提取代码、清单文件和类，以及从清单文件中生成特征向量。数据预处理阶段包括特征选择、数据归一化、数据转换和标签编码，将数据集转换为分类器可接受的格式。在模型工程阶段，采用DL驱动的GPU加速的GRU模型来检测Android生态系统中不断发展的复杂网络威胁和攻击。最后，通过标准的性能评估指标(如准确度、精确度、召回率、F1-score、AU-ROC等)对所取得的结果进行了严格的评估。

### <a class="reference-link" name="A.%20%E6%95%B0%E6%8D%AE%E9%87%87%E9%9B%86"></a>A. 数据采集

一个Android APK包含了一个名为AndroidManifest.xml的清单文件。Manifest文件包含支持Android包的访问权限、安装和执行的元数据。在所提出的方法中，Java代码结构化地从Android APK中提取manifest文件。为了从manifest文件中提取有用信息和生成特征向量，编写了python脚本。所设计的代码广泛地检查manifest文件并提取不同的特征（即权限、API调用和过滤意图）。最初通过python脚本提取的特征包括访问摄像头、GPS、麦克风或触摸屏等权限。大多数恶意的应用程序要求访问这些组件，甚至不需要任何目的或应用程序的功能。

要求的权限也被认为是重要的Android恶意软件检测系统，因为他们是在安装时授予应用程序。我们积累了近千种不同的权限，这些权限被各种Android应用程序使用。一个Android应用程序是建立在四个主要组件上的，即活动、服务、广播接收器和内容提供者。这四个组件也被认为是数据集的特征。Intents是应用程序组件内或与其他连接的应用程序之间的消息传递机制。过滤后的意图也被考虑在内。

### <a class="reference-link" name="B.%20%E6%95%B0%E6%8D%AE%E9%A2%84%E5%A4%84%E7%90%86"></a>B. 数据预处理

数据预处理是指在输入到算法之前对原始数据进行所有转换的过程，以达到高效的性能。此外，它还降低了可用资源在存储和时间方面的复杂性。AMD和Androzoo的Apk结合在一起，生成了我们提出的Android恶意软件检测的数据集。它满足每一个标准，如标签数据集，完整的表现文件特征，恶意软件的多样性和异质性。通过python脚本，提取了约19000个特征，但选择了150个最容易出现的特征。为了提高恶意软件检测系统的有效性，需要将所有特征值转移到缩放版本中。为此，使用python标准缩放器函数对数据集进行归一化处理。为了减少数据冗余，提高数据的完整性，进行了数据转换，删除了重复、空值和无穷值。同时通过标签编码将列中的每个值转换为数字。

### <a class="reference-link" name="C.%20%E6%A8%A1%E5%9E%8B%E5%B7%A5%E7%A8%8B"></a>C. 模型工程

采用DL驱动的GPU驱动的GRU来检测Android系统中不断发展的复杂网络威胁和攻击。一个高效、稳健和可扩展的Android恶意软件检测方案已经实现，它可以检测多类恶意软件，如后门和木马。所提出的基准GPU赋能GRU分类器的完整设计和其他实验架构的性能评估（即层、神经元、激活函数、损失函数、优化器、批次大小、纪元和学习率）详见表.2。

表2 拟议的恶意软件检测系统门控循环单元（GRU）架构描述

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun.t2-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun.t2-3009819-large.gif)

### D. 数据集

在分析恶意软件检测系统的性能时，选择当前最先进的数据集起着重要作用。对于恶意软件检测，数据集由38842个APK组成(即30831个良性APK已经从Androzoo[39]和8011个恶意软件APK从Android恶意软件数据集(AMD)[40]收集。AMD包含10个不同类别的恶意软件（即后门、木马、木马-银行家、木马-clicker、木马-Dropper、木马-短信、木马-间谍、广告软件、HackerTool、勒索）与71个不同的恶意软件家族。对于数据集，我们将6个不同类别的木马合并为一个木马类。因此，数据集的完整分布在3个不同的类中，包括良性、后门和木马，这也可以在图6中看到。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun6-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun6-3009819-large.gif)

图6.建议方案的数据集分布图



## 第五节 实验设置、结果与讨论

本节提供了完整的实验设置概述、标准性能评价指标和结果以及讨论。

### A. 实验设置

在实验设置上，作者采用了Intel处理器、图形处理单元（GPU）进行硬件设置。而所提出的方法论则采用Keras进行软件实现[41]。实验中，作者采用了Intel处理器、图形处理单元(GPU)进行硬件设置，而软件实现则采用Keras实现[41]。详细的硬件和软件规格见表.3。

表3 拟议的基于GRU的Android恶意软件检测架构的硬件和软件规范

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun.t3-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun.t3-3009819-large.gif)

### B. 评价指标

为了对所提出的恶意软件检测模型进行全面的性能评估，我们采用了标准的评估指标（即准确度、精度、召回率、F1-score和ROC曲线）。为了更全面的评价，我们还计算了扩展评价指标（即真阴性率（TNR）、马修斯相关系数（MCC）、负预测值（NPV）、假阳性率（FPR）、假阴性率（FNR）、假发现率（FDR）和假遗漏率（FOR）。性能评价指标的详细描述可参见[42]。

True Positve、True Negative、False Positive和False Negative描述为，

True Positive(TP)等于分类为恶意记录的数量。

真阴性（TN）等于预测为良性的良性样本数。

假阳性(FP)等于被误判为恶性的良性样本数。

假阴性(FN)等于被误判为良性的恶意记录的数量。

1) 准确率

准确率是指正确预测的样本数占总样本数的比例。

[![](https://p4.ssl.qhimg.com/t010b481a6a185678a1.jpg)](https://p4.ssl.qhimg.com/t010b481a6a185678a1.jpg)

2) 精确度

精确度是指被正确分类的恶意应用与所有恶意应用总数的比例。

[![](https://p1.ssl.qhimg.com/t012b682327c82d4a2b.jpg)](https://p1.ssl.qhimg.com/t012b682327c82d4a2b.jpg)

3）召回率

召回率是指从每个类别的总记录中正确预测的数值的数量。召回率也叫真阳率（TPR）。

[![](https://p5.ssl.qhimg.com/t014c75814e17c92b28.jpg)](https://p5.ssl.qhimg.com/t014c75814e17c92b28.jpg)

4) F1-分数

F1得分显示了召回率和精度之间的相关性。

[![](https://p3.ssl.qhimg.com/t01635e966a4785d121.jpg)](https://p3.ssl.qhimg.com/t01635e966a4785d121.jpg)

5）混淆矩阵

混淆矩阵用于描述分类模型的整体性能。混淆矩阵可以用二元或多类来表示。混淆矩阵用于测量准确度、精确度、召回率和AUC-ROC曲线的值。

6) AUC-ROC

AUC-ROC表示可分离程度，主要代表多类分类问题的性能。这是区分多类最重要的评价指标之一。AUC越高，模型擅长将0s预测为0s，将1s预测为1s。ROC曲线的绘制是在TP率和FP率之间。

### C. 探讨

本文提出了基于Cuda-empowered GRU的Android恶意软件检测方案，针对3个不同的类别(即良性、木马和后门)进行检测。

为了全面评估性能，我们将所提出的技术与我们构建的当代DL算法，如长短期记忆（LSTM）、卷积神经网络（CNN）和深度神经网络（DNN）进行比较。图7中的混淆矩阵描述了我们提出的技术在多攻击分类中的性能效率。图7中的混淆矩阵描述了我们所提出的技术在多攻击分类中的性能效率，真阳性(TP)和真阴性(TN)的高度实现值定义了我们系统的性能，可以有效地用于Android中不断发展的复杂网络威胁和恶意软件检测。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun7-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun7-3009819-large.gif)

图7.所提出的GRU、LSTM、DNN和CNN模型的混淆矩阵

为了衡量Android应用的良性或恶意分类的准确度，计算了检测准确度、精度、召回率和F1-score，如图8所示。本文提出的基于GPU的恶意软件检测技术在恶意软件分类方面的检测准确率为98.96%，精度为99.38%，召回率为99.31%，F1-score为99.35%。然而，DNN实现了99.59%的精度值，高于我们提出的模型，这是因为记录数量较少，架构较不复杂，对相关实例的分类更为正确。我们提出的技术与其他构建的分类器相比，总体上实现了高性能。为了严格评估所提出的模型，还计算了真负率(TNR)、马修斯相关系数(MCC)和负预测值(NPV)，我们提出的机制在TNR、MCC和NPV方面分别达到了97.34%、96.92%和97.60%，如图9所示。所提出的机制明显优于其他的分类器。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun8-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun8-3009819-large.gif)

图8.所提出的基于GRU的Android恶意软件检测技术的准确率、精确度、召回率、F1-分数值

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun9-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun9-3009819-large.gif)

图9.拟议的基于Cuda的GRU模型的TPR、MCC、NPV值

此外，假阴性率(FNR)、假阳性率(FPR)、假遗漏率(FOR)和假发现率(FDR)从根本上决定了分类器对实例描述错误的执行情况。提出的基于GRU的恶意软件检测方案在FDR、FNR、FOR和FPR方面分别完成了0.68%、0.63%、2.4%和0.68%，如图10所示。FDR、FOR、FNR和FPR的结果清楚地显示了我们提出的架构的巨大性能。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun10-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun10-3009819-large.gif)

图10.基于GRU的Cuda技术的FDR、FNR、FOR和FPR值

AU-ROC说明了真阳性率（TPR）和假阳性率（TNR）之间的关系。如图 11 所示，曲线下的面积显示了我们所提出的技术的稳健性能。AU-ROC 清楚地显示了我们提出的技术的可靠性能。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun11-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun11-3009819-large.gif)

图11.提出的GRU和其他实验分类器如LSTM、DNN和CNN的AU-ROC曲线图

我们提出的技术的时间效率定义在图12中。在测试阶段，所提出的GRU模型在7560个实例中花费了1005（毫秒）几乎等于1秒。GRU与其他对比算法的速度效率明显呈现出微不足道的交易。虽然，GRU的速度效率不是很乐观，但是；在时间复杂度方面还有改进的空间。我们未来的工作计划是提高所提出算法的速度效率。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun12-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun12-3009819-large.gif)

图12.拟议的GPU加速GRU、LSTM、DNN和CNN的测试时间

因此，还将提出的技术与当前的基准进行了比较。基于GRU的技术与当前技术水平的综合比较如表所示4所取得的数值明显显示了我们提出的Android恶意软件检测机制的性能优于其他机制。

表4 拟议的GPU驱动的GRU技术与其他当代现有的Android恶意软件检测解决方案的比较

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun.t4-3009819-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/6287639/8948470/9142180/akhun.t4-3009819-large.gif)



## 第六节. 结论

Android操作系统的开放性和普及性的需求不断增加，不仅彻底改变了数字环境，也带来了新的复杂的网络安全漏洞、威胁和攻击。为了应对复杂的多类恶意软件威胁和攻击，我们提出了一种稳健、可扩展和高效的基于DL的Android恶意软件检测技术。所提出的机制已经用标准的性能指标进行了全面评估，并与当前的基准和我们构建的当代DL驱动算法进行了广泛的比较。所提出的方案在高检测精度方面表现优异，这意味着可以准确识别流行的各种Android恶意软件。在此基础上，我们提出的技术可以有效的及时的检测出Android恶意软件，对后续的缓解和预防攻击有很大的帮助。最后，我们支持各种深度学习架构，以找到一个有前途的解决方案来对抗新的和新兴的复杂的Android恶意软件。

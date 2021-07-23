> 原文链接: https://www.anquanke.com//post/id/217692 


# 关键基础设施中基于AI的入侵检测技术的比较研究（二）


                                阅读量   
                                **201893**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者SAFA OTOUMBURAK、KANTARCI、HUSSEIN MOUFTAH，文章来源：x-mol.com 
                                <br>原文地址：[https://www.x-mol.com/paper/1290717755575246848](https://www.x-mol.com/paper/1290717755575246848)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01d55d5e20394819af.jpg)](https://p4.ssl.qhimg.com/t01d55d5e20394819af.jpg)



## 5.入侵检测方法

### **5.1基于自适应监督和聚类混合入侵检测系统(**ASCH-IDS**)的自适应机器学习**

[![](https://p2.ssl.qhimg.com/t0190a9b294c48c0874.jpg)](https://p2.ssl.qhimg.com/t0190a9b294c48c0874.jpg)

在我们之前提出的ASCH-IDS[7]和CHH-IDS[6]中，收集到的遥感数据经历了两个基于子系统与入侵检测同时运行的机器学习：异常检测子系统(**ADSs**)和误用检测子系统(**MDSs**)。这就转化为一个混合系统，如算法2所示，用于检测入侵传感器。**ADSs**遵循EDBSCAN算法，是指带噪音的应用程序基于密度升级的空间聚类，而**MDSs**遵循的是随机森林技术。DBSCAN回归到基于密度的聚类方法，聚类被认为是物体的密集区域，数据空间分布成低密度的物体区域[34]，而E-DBSCAN算法保留了聚类中局部密度的变化轨迹，并在考虑其电子邻域的情况下计算任何核心物体的密度变化[35]。另一方面，当随机森林被用作分类机制时，每棵树都会检查每个输入的频繁类并在发生时进行投票[36]，它的操作分为两个阶段：训练和分类阶段[37]。在[6]中，将收集到的数据按照时间段划分的方法，以循环的方式划分为**IDS**子系统(**IDSs**)，如图1所示。

[![](https://p4.ssl.qhimg.com/t01c90fc84907c48400.jpg)](https://p4.ssl.qhimg.com/t01c90fc84907c48400.jpg)

图2表示之前提出的**CHH-IDS**[6]，**CHH-IDS**运行在包含N集群的**WSN**上，**CH**处理传感器转发的数据的聚合过程。

[![](https://p5.ssl.qhimg.com/t01f9abdc6d51771a45.jpg)](https://p5.ssl.qhimg.com/t01f9abdc6d51771a45.jpg)

当采用随机森林进行误用检测时，每棵树的发展情况如下所述[37]：
1. 如果训练集大小用**Y**表示，则从原始数据集中随机提取的数据点y就变成了开发树的训练数据集。
1. 如果输入变量用**X**表示，可以利用从**X**中随机提取的**x**来分割节点。**x**被认为是一个常数，而森林发展时，每棵树都被发展到最大的尺寸。
另一方面，E-DBSCAN作为聚类算法已经被利用来提取代表距离阈值的[![](https://p5.ssl.qhimg.com/t01b581a3bced625df5.jpg)](https://p5.ssl.qhimg.com/t01b581a3bced625df5.jpg)，[![](https://p4.ssl.qhimg.com/t01b581a3bced625df5.jpg)](https://p4.ssl.qhimg.com/t01b581a3bced625df5.jpg)是E-DBSCAN算法中的关键因素[38]。DBSCAN可以实现属于同一密度的相邻聚类以及随机形状的聚类[39]。DBSCAN由两个因子组成，分别是被视为输入参数的[![](https://p2.ssl.qhimg.com/t01b581a3bced625df5.jpg)](https://p2.ssl.qhimg.com/t01b581a3bced625df5.jpg)和**MinPts**。它遵循以下的规则：
1. [![](https://p3.ssl.qhimg.com/t01bb9bff23551668bd.jpg)](https://p3.ssl.qhimg.com/t01bb9bff23551668bd.jpg)
1. 核心对象的邻域大小&gt;**MinPts**。
1. 点**j**作为核心对象，从**i**中可以获得密度。
1. 当i和j从一个核心对象中可以获得密度时，认为i和j是基于密度的连接。
另一方面，ASCH-IDS[6]保留了**ADSs**和**MDSs**在接收者运行特性曲线(ROC)上的偏差，并自适应地改变指向它们的数据段。

方程式(2)-(3)表示(TP)至(FP)的两个子系统在τi上，它们分别用μ1(τi)和μ2(τi)表示[7]。

[![](https://p5.ssl.qhimg.com/t0160ff139c1b0c0174.jpg)](https://p5.ssl.qhimg.com/t0160ff139c1b0c0174.jpg)

方程式(4)-(5)表示在时间(<sup>△</sup>τ)时TP至FP的比率，其中<sup>△</sup>τ=τi+1∞τi [7]。

[![](https://p0.ssl.qhimg.com/t01d74e3cd5e23910c6.jpg)](https://p0.ssl.qhimg.com/t01d74e3cd5e23910c6.jpg)

当提取<sup>△</sup>τ期间的ROC行为时，我们可以得到各子系统的ROC行为是τ时的ROC行为与<sup>△</sup>τ时的行为之和，这可以用方程式(6)和(7)来表示[7]。其中α代表最近计算的TP/FP及其在(<sup>△</sup>τ)期间的值，其中τi+1=τi+<sup>△</sup>τ。

[![](https://p5.ssl.qhimg.com/t0167f04015fc2bb6f2.jpg)](https://p5.ssl.qhimg.com/t0167f04015fc2bb6f2.jpg)

方程式(8)表示一个指标**I**(τi)，它追踪MDSs和ADSs在任意时间τi上的ROC行为 。

[![](https://p3.ssl.qhimg.com/t013a577d6a87fbfba2.jpg)](https://p3.ssl.qhimg.com/t013a577d6a87fbfba2.jpg)

提取的指标**I**用于决定对收集到的数据进行引导，如I(τi)&gt; I(τi-1)，ASCH-IDS就会判定ADSs的性能优于MDSs，所以ADSs数据比例增加，就会提升系统的整体性能。各种情况下，I(τi)&lt; I(τi-1)，入侵检测系统会判定MDSs的性能优于ADSs，如，MDSs数据比例的任何增长都有望改善系统的整体性能。无论什么情况下，如果 I(τi+1)&gt; I(τi)，则ASCH-IDS在μ1上的数据比例增加，在μ2上的数据比例减少，如：Da(τi+1)= Da(τi)+<sup>△</sup>D和Dm(τi+1)= Dm(τi)-<sup>△</sup>D，如方程式(9)-(10)中所制定的<sup>△</sup>D表示各子系统的数据调整。算法3对前面的步骤进行了概述。其中τi、τi+1和<sup>△</sup>τ分别指任意时间、τi+△τ和(τi+1∞τi)之间的时间差。α指的是评价μ1(τi)和μ2(τi)时的ROC特征权重，Da(τi)和Dm(τi)指的是τi处转发到异常(ADSs)和误用(MDSs)的数据段。

[![](https://p3.ssl.qhimg.com/t019ebf18859a428fe6.jpg)](https://p3.ssl.qhimg.com/t019ebf18859a428fe6.jpg)

由于所提出的系统由两个子系统组成，其复杂度是两个算法复杂度的函数。由于随机森林是一种特殊的决策树模型，其复杂度可以从决策树中提取出来，例如，建立一棵具有r条记录和v个变量的决策树的复杂度C(随机森林)为O(v + rec ∗ log(v))，而对于我们的随机森林中的多棵树，复杂度为O(Tr ∗ Var ∗ rec ∗ log(Var))，其中Tr是树的数量，Var是变量的数量。对于作为第二个子系统的E-DBSCAN，其复杂度是由查询请求的数量决定的。由于每个点只操作一个查询，所以运行时复杂度为O(n)&lt;(n∗log(n))。在我们的E-DBSCAN中，初始化步骤执行1次，比较步骤执行(m+1)次，增量步骤执行(m)次。因此，复杂度将为O(2+(2m))=O(m)。为此，系统的整体复杂度可以用O( (Tr ∗ Var ∗ rec ∗log(Var))+ (2 + (2m))来计算。

### **5.2 基于深度学习的受限玻尔兹曼机聚类IDS(RBC-IDS)**

受限玻尔兹曼机(RBM)是一种高能的神经网络系统，包含两种类型的层面：(V)和(H)分别指可见层和隐藏层，学习过程由无监督方式引导[19]。RBM允许同一层的神经元之间的连接，这使得它受到限制，程序在算法4的虚拟码中提出。

[![](https://p2.ssl.qhimg.com/t01f6d7ec7e5d74b24b.jpg)](https://p2.ssl.qhimg.com/t01f6d7ec7e5d74b24b.jpg)

表1包含了算法4中使用的RBM参数。

[![](https://p1.ssl.qhimg.com/t01b6df37fed10360e6.jpg)](https://p1.ssl.qhimg.com/t01b6df37fed10360e6.jpg)

网络对隐藏元素和可见元素中的每一种情况都设置了概率得分[19][33]。

图3表示RBC-IDS中使用的RBM设置。RBC-IDS由一个包含X个可见节点的输入层，三个隐藏层和输出层组成，其中输出层的两个输出O1和O2分别为**Intrusive**和**Normal**输出。W11代表第一可见层和第一隐藏层之间的权重，而W12指的是第一隐藏层和第二隐藏层的权重，W23是第二隐藏层和第三隐藏层之间的权重。

[![](https://p3.ssl.qhimg.com/t0186b66cf43146974b.jpg)](https://p3.ssl.qhimg.com/t0186b66cf43146974b.jpg)

在RBC-IDS中，每个CH负责将来自同一集群中的传感器的传感数据进行聚合，并通过采用[32]中的程序将其转发给服务器。

### **5.3 强化学习**

在机器学习中，所研究的环境被定义为马尔可夫决策过程(MDP)，它和许多强化学习算法(如Q-learning)一样，采用动态编程程序。MDP拿出最优的策略来实现随着时间的推移获得最大的回报[40]。

强化学习概念的基本原理如下：
1. 代理器(即传感器)与环境交互，在每个状态St中采取动作At，并观察环境的反馈。
1. 环境以R<sup>+</sup>或R<sup>–</sup>的形式为所做的行为提供奖励Rt，分别指的是积极或消极的奖励。
1. 代理器会观察环境的任何变化，并通过更新策略来优化收到的奖励。
1. 从当前状态出发，为了使总奖励的期望值最大化，调用不同的强化学习技术。
**5.3.1 Q-Learning。**Q-Learning建立在价值迭代的概念上，代理的目的是估计价值函数，每一次迭代更新所有的状态s和动作A，以便知道哪个动作A导致更高的奖励R，在Q表中，行代表状态，而列代表动作。在一个状态(比如说状态S)中，代理采取一个动作(即动作A)，观察这个动作的奖励(R)以及下一个状态(S’)，然后重新估计Q值。

方程式(11)表示估计的Q值[41]，其中St、At和Rt分别代表时间t的状态、动作和奖励。此外，α和γ分别代表学习率和一个关于奖励相对值的常数。事实上，以下条件对这两个参数都成立。0&lt;α&lt;1，0&lt;γ&lt;1。

[![](https://p5.ssl.qhimg.com/t016027b2374a3c36b5.jpg)](https://p5.ssl.qhimg.com/t016027b2374a3c36b5.jpg)

方程(12)形成估计函数V<sup>π</sup>(S)，它代表了对初始状态S下将获得的未来报酬R的估计[42]。方程中π(S，A)表示动作A在状态S中的可能性，P<sub>SS</sub>+(A)代表状态S和S<sup>+</sup>与动作A之间的状态转换概率。R(S，S<sup>+</sup>，A)为行动A时从状态S过渡到S<sup>+</sup>后发出的奖励，r为未来奖励到当前奖励的贴现系数权重[42]。采用的值迭代方法如下方程式(13)所示。其中，Vπ(S)指初始状态S时R的值估计，π(S，A)是A在S中的概率，P<sub>SS</sub>+(A)指A时从状态S到S+的过渡概率，R(S，S<sup>+</sup>，A)是S时从状态S到S<sup>+</sup>过渡返回的报酬。r为未来奖励到当前奖励的贴现系数权重，VπI（S<sup>+</sup>）为初始迭代I时R在状态S<sup>+</sup>的价值估计，[![](https://p5.ssl.qhimg.com/t01c6a65650f0a109ed.jpg)](https://p5.ssl.qhimg.com/t01c6a65650f0a109ed.jpg)为更新迭代I+1时R在状态S的价值估计。

[![](https://p1.ssl.qhimg.com/t0186466abb883c29ab.jpg)](https://p1.ssl.qhimg.com/t0186466abb883c29ab.jpg)

值得注意的是，之所以采用Q-learning作为我们的强化学习方法之一，是因为Q-learning的无模型特性。此外，通过应用Q-learning，还可以以非自适应的方式解决随机奖励问题。此外，Q-learning还具有不一定遵循当前政策的学习能力[43]。

**5.3.2状态-行动-奖励-状态-行动学习（SARSA）。**SARSA是一种基于MDP的强化学习算法，它被认为是一种改进版的链结式Q-Learning（MCQ-L）算法。SARSA根据当前状态S、S的当前动作A、动作A的返回奖励R、新状态S和新状态的下一个动作A来更新Q值，可以用五元组（St,At,Rt,St+1,At+1）来表示。

SARSA是一种策略性学习算法，代理与环境相互关联，并根据所采取的行动更新政策。在SARSA中，Q值函数表示在状态S中采取动作A在下一个时间步中收到的奖励，以及从下一个状态和动作中收到的奖励[44]。前面的Q值函数（方程式(11)）可按方程式(14)更新。

方程式(11)和方程式(14)看起来几乎是一样的，只是在Q-learning中，所有可能的下一步行动中估计值最高的行动将被考虑，而在SARSA中，实际的下一步行动被考虑。与SARSA技术相比，在Q-learning中寻找最大的回报会使其成本更高[14]。

[![](https://p4.ssl.qhimg.com/t0178b4727a7c876267.jpg)](https://p4.ssl.qhimg.com/t0178b4727a7c876267.jpg)

**5.3.3 时间差分学习(TD)。**是一种无模型强化学习技术，它可以通过考虑从当前值的近似分布来估计期望值函数进行学习。TD技术估计策略下的状态值函数π，如下面的方程式(15)和方程式(16)所示。

其中V<sup>π</sup>（St）指的是状态St的状态价值函数，R指的是报酬，γ是政策π下的贴现率，在方程式（16）中，R<sub>0</sub>+γV<sup>π</sup>（S1）代表V<sup>π</sup>（St）的无偏估计。TD是一种用来学习如何估计一个依赖于未来值的技术，这使得它对学习V-函数和Q-函数都很有用。而Q-learning则是一种只学习Q-函数的特殊技术。

[![](https://p0.ssl.qhimg.com/t0159f3020fef9785a6.jpg)](https://p0.ssl.qhimg.com/t0159f3020fef9785a6.jpg)

基于强化学习的WSNs入侵检测系统（QL-IDS）如图4所示。IDS由分层连接的集群与聚合器和一个中心代理其代理在表示强化学习盒，它试图模拟监测网络的状态。经过一系列的迭代，中心代理知道响应每个状态S需要执行的动作A，以获得正向奖励R<sup>+</sup>。

值得一提的是，值迭代的工作原理是通过生成最优值函数的连续估计值。其中每一次的迭代都可以在O(|A||S |2)中完成。在强化学习中，所需的迭代次数可以成倍增长。

[![](https://p5.ssl.qhimg.com/t01324b073458f70ce3.jpg)](https://p5.ssl.qhimg.com/t01324b073458f70ce3.jpg)



## 参考文献

[1] I. Al-Ridhawi, S. Otoum, M. Aloqaily, Y. Jararweh, and Th. Baker. Providing secure and reliable communication for next generation networks in smart cities. **Sustainable Cities and Society**, 56:102080, 2020.

[2] L. Buttyan, D. Gessner, A. Hessler, and P. Langendoerfer. Application of wireless sensor networks in critical infrastructure protection: challenges and design options [security and privacy in emerging wireless networks]. **IEEE Wireless Communications**, 17(5):44–49, October 2010.

[3] Ismaeel Al Ridhawi, Yehia Kotb, Moayad Aloqaily, Yaser Jararweh, and Thar Baker. A profitable and energy-efficient cooperative fog solution for iot services. **IEEE Transactions on Industrial Informatics**, 16(5):3578–3586, 2019.

[4] Safa Otoum, Burak Kantraci, and Hussein T. Mouftah. Hierarchical trust-based black-hole detection in wsn-based smart grid monitoring. **IEEE International Conference on Communications (ICC)**, 2017.

[5] M. Al-Khafajiy, S. Otoum, TH. Baker, M. Asim, Z. Maamar, M. Aloqaily, MJ. Taylor, and M. Randles. Intelligent control and security of fog resources in healthcare systems via a cognitive fog model. **ACM Transactions on Internet Technology**, 2020.

[6] Safa Otoum, Burak Kantarci, and Hussein T. Mouftah. Detection of known and unknown intrusive sensor behavior in critical applications. **IEEE Sensors Letters**, 1(5):1–4, Oct 2017.

[7] Safa Otoum, Burak Kantraci, and Hussein T. Mouftah. Adaptively supervised and intrusion-aware data aggregation for wireless sensor clusters in critical infrastructures. In **IEEE International Conference on Communications (ICC)**, pages 1–6, May 2018.

[8] Safa Otoum, Burak Kantraci, and H. T. Mouftah. Mitigating false negative intruder decisions in wsn-based smart grid monitoring. In **13th International Wireless Communications and Mobile Computing Conference (IWCMC)**, pages 153–158, June 2017.

[9] R. Jain and H. Shah. An anomaly detection in smart cities modeled as wireless sensor network. In **International Conference on Signal and Information Processing (IConSIP)**, pages 1–5, Oct 2016.

[10] C. Ioannou, V. Vassiliou, and C. Sergiou. An intrusion detection system for wireless sensor networks. In **24th International Conference on Telecommunications (ICT)**, pages 1–5, May 2017.

[11] Ahmad Javaid, Quamar Niyaz, Weiqing Sun, and Mansoor Alam. A deep learning approach for network intrusion detection system. In **Proceedings of the 9th EAI International Conference on Bio-inspired Information and Communications Technologies (Formerly BIONETICS)**, pages 21–26, 2016.

[12] C. Yin, Y. Zhu, J. Fei, and X. He. A deep learning approach for intrusion detection using recurrent neural networks. **IEEE Access**, 5:21954–21961, 2017.

[13] L. Dali, A. Bentajer, E. Abdelmajid, K. Abouelmehdi, H. Elsayed, E. Fatiha, and B. Abderahim. A survey of intrusion detection system. In **2nd World Symposium on Web Applications and Networking (WSWAN)**, pages 1–6, March 2015.

[14] Stefano Zanero and Sergio M. Savaresi. Unsupervised learning techniques for an intrusion detection system. In **ACM Symposium on Applied Computing**, SAC ’04, pages 412–419, New York, NY, USA, 2004. ACM.

[15] Nico Görnitz, Marius Kloft, Konrad Rieck, and Ulf Brefeld. Active learning for network intrusion detection. In **Proceedings of the 2Nd ACM Workshop on Security and Artificial Intelligence**, AISec ’09, pages 47–54, New York, NY, USA, 2009. ACM.

[16] J. Straub. Testing automation for an intrusion detection system. In **IEEE Autotestcon**, pages 1–6, Sept 2017.

[17] Andrew Honig, Andrew Howard, Eleazar Eskin, and Sal Stolfo. Adaptive model generation: An architecture for deployment of data mining-based intrusion detection systems. pages 153–194. Kluwer Academic Publishers, 2002.A Comparative Study of AI-based Intrusion Detection Techniques in Critical Infrastructures 21

[18] Mostafa A. Salama, Heba F. Eid, Rabie A. Ramadan, Ashraf Darwish, and Aboul Ella Hassanien. Hybrid intelligent intrusion detection scheme. In António Gaspar-Cunha, Ricardo Takahashi, Gerald Schaefer, and Lino Costa, editors, **Soft Computing in Industrial Applications**, pages 293–303, Berlin, Heidelberg, 2011. Springer Berlin Heidelberg.

[19] Arnaldo Gouveia and Miguel Correia. **A Systematic Approach for the Application of Restricted Boltzmann Machines in Network Intrusion Detection**, volume 10305. 05 2017.

[20] Yazan Otoum, Dandan Liu, and Amiya Nayak. Dl-ids: a deep learning–based intrusion detection framework for securing iot. **Transactions on Emerging Telecommunications Technologies**, n/a(n/a):e3803. e3803 ett.3803.

[21] M. Z. Alom, V. Bontupalli, and T. M. Taha. Intrusion detection using deep belief networks. In **National Aerospace and Electronics Conference (NAECON)**, pages 339–344, June 2015.

[22] Ugo Fiore, Francesco Palmieri, Aniello Castiglione, and Alfredo De Santis. Network anomaly detection with the restricted boltzmann machine. **Neurocomputing**, 122:13 – 23, 2013.

[23] Yuancheng Li, Rong Ma, and Runhai Jiao. A hybrid malicious code detection method based on deep learning. 9:205–216, 05 2015.

[24] A. Abeshu and N. Chilamkurti. Deep learning: The frontier for distributed attack detection in fog-to-things computing. **IEEE Communications Magazine**, 56(2):169–175, Feb 2018.

[25] Rafał Kozik, Michał Choraś, Massimo Ficco, and Francesco Palmieri. A scalable distributed machine learning approach for attack detection in edge computing environments. **Journal of Parallel and Distributed Computing**, 119:18 – 26, 2018.

[26] Arturo Servin and Daniel Kudenko. Multi-agent reinforcement learning for intrusion detection. In **Adaptive Agents and Multi-Agent Systems III. Adaptation and Multi-Agent Learning**, pages 211–223, Berlin, Heidelberg, 2008. Springer Berlin Heidelberg.

[27] Xin Xu and Tao Xie. A reinforcement learning approach for host-based intrusion detection using sequences of system calls. In **Advances in Intelligent Computing**, pages 995–1003, Berlin, Heidelberg, 2005. Springer Berlin Heidelberg.

[28] Indah Tiyas, Ali Barakbah, Tri Harsono, and Amang Sudarsono. Reinforced intrusion detection using pursuit reinforcement competitive learning. **EMITTER International Journal of EngineeringTechnology**, 2(1):39–49, 2014.

[29] James Cannady Georgia. Next generation intrusion detection: Autonomous reinforcement learning of network attacks. In **In Proceedings of the 23rd National Information Systems Secuity Conference**, pages 1–12, 2000.

[30] Arturo Servin. Towards traffic anomaly detection via reinforcement learning and data flow. pages 81–88.

[31] Fatma Belabed and Ridha Bouallegue. An optimized weight-based clustering algorithm in wireless sensor networks. **2016 International Wireless Communications and Mobile Computing Conference (IWCMC)**, 2016.

[32] Wei Zhang, Sajal Das, and Yonghe Liu. A trust based framework for secure data aggregation in wireless sensor networks. **IEEE Communications Society on Sensor and Ad Hoc Communications and Networks**, 2006.

[33] S. Seo, S. Park, and J. Kim. Improvement of network intrusion detection accuracy by using restricted boltzmannmachine. In **8th International Conference on Computational Intelligence and Communication Networks (CICN)**, pages413–417, Dec 2016.

[34] Daoying Ma and Aidong Zhang. An adaptive density-based clustering algorithm for spatial database with noise. **IEEE Intl Conf on Data Mining (ICDM’04)**.

[35] A. Ram, A. Sharma, A. S. Jalal, A. Agrawal, and R. Singh. An enhanced density based spatial clustering of applicationswith noise. In **IEEE Intl. Advance Computing Conference**, pages 1475–1478, March 2009.

[36] Random forests, leo breiman and adele cutler.

[37] Jiong Zhang, M. Zulkernine, and A. Haque. Random-forests-based network intrusion detection systems. **IEEE Trans. on Systems, Man, and Cybernetics, Part C**, 38/5:649–659, 2008.

[38] M.f Jiang, S.s Tseng, and C.m Su. Two-phase clustering process for outliers detection. **Pattern RecognitionLetters**, 22/6-7:691–700, 2001.

[39] Daoying Ma and Aidong Zhang. An adaptive density-based clustering algorithm for spatial database with noise. **IEEE Intl Conf on Data Mining (ICDM’04)**.

[40] S. Doltsinis, P. Ferreira, and N. Lohse. An mdp model-based reinforcement learning approach for production stationramp-up optimization: Q-learning analysis. **IEEE Transactions on Systems, Man, and Cybernetics: Systems**, 44(9):1125– 1138, Sept 2014.

[41] Christopher J. C. H. Watkins and Peter Dayan. Q-learning. **Machine Learning**, 8(3):279–292, May 1992.

[42] Xin Du and Jinjian Zhai. Algorithm trading using q-learning and recurrent reinforcement learning.

[43] Chris Gaskett, David Wettergreen, and Alexander Zelinsky. Q-learning in continuous state and action spaces. InNorman Foo, editor, **Advanced Topics in Artificial Intelligence**, pages 417–428, Berlin, Heidelberg, 1999. Springer BerlinHeidelberg.

[44] D. Kumar, N. Logganathan, and V. P. Kafle. Double sarsa based machine learning to improve quality of video streamingover http through wireless networks. In **2018 ITU Kaleidoscope: Machine Learning for a 5G Future (ITU K)**, pages 1–8,Nov 2018.

[45] M. Tarique, K. E. Tepe, and M. Naserian. Hierarchical dynamic source routing: passive forwarding node selection forwireless ad hoc networks. volume 3, pages 73–78 Vol. 3, Aug 2005.

[46] Irvine The UCI KDD Archive, University of California. **KDD Cup 1999 Data**. Available at http://www.kdd.ics.uci.edu/databases/kddcup99/kddcup99/html/, Last Visit: April.10.2018.

[47] P Natesan and Prof P Balasubramanie. Multi stage filter using enhanced adaboost for network intrusion detection.4:121–135, 05 2012.

[48] B. M. Beigh and M. A. Peer. Performance evaluation of different intrusion detection system: An empirical approach. In **Intl. Conf. on Computer Communication and Informatics**, pages 1–7, Jan 2014.

[49] Hesham Elmahdy M. Elhamahmy and Imane A. Saroit. A new approach for evaluating intrusion detection system. In**Artificial Intelligent Systems and Machine Learning**, volume 2, pages 290–298, November 2010.

[50] M. Elhamahmy, N. Hesham, and A. Imane. A new approach for evaluating intrusion detection system. In **ArtificialIntelligent Systems and Machine Learning**, volume 2, pages 290–298, Dec 2010.

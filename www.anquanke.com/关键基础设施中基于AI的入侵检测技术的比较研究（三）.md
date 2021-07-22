> 原文链接: https://www.anquanke.com//post/id/217898 


# 关键基础设施中基于AI的入侵检测技术的比较研究（三）


                                阅读量   
                                **125060**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者x-mol，文章来源：x-mol.com
                                <br>原文地址：[https://www.x-mol.com/paper/1290717755575246848](https://www.x-mol.com/paper/1290717755575246848)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01d55d5e20394819af.jpg)](https://p4.ssl.qhimg.com/t01d55d5e20394819af.jpg)



## 6实验结果与分析

### **6.1 KDD数据集的说明**

我们模拟了一个20台设备的网络，这些设备通过H-DSR协议进行通信，H-DSR协议是一种专门针对分层网络的动态源路由协议[45]。测试的设备部署在100m x 100m区域内的4个集群中。模拟结果显示了在置信水平为95%的情况下，每个场景10次测试（运行）的平均值。表2为模拟输入。

[![](https://p4.ssl.qhimg.com/t0164e44a1a9f367035.jpg)](https://p4.ssl.qhimg.com/t0164e44a1a9f367035.jpg)

麻省理工学院林肯实验室在国防高级研究计划局（DARPA）和空军研究实验室（AFRL）的支持下，收集了计算机网络IDS评估的数据集。1999年数据挖掘杯的知识发现1999（KDDCup99）的数据集是DARPA数据集的一个子集[46]。KDDCup99用于测试IDSs在模拟WSN上的效率，每个连接记录包含41个特征，这些特征被分为正常行为和攻击行为。KDDCup99包含约311,029条记录作为测试数据集，494,020条记录作为训练数据集。这些数据集中的众多攻击类型被收集到攻击组中，在一个组中分配相似的攻击类型，从而进步检测率[46]。KDDCup99攻击分为四大组，具体来说，是DoS、Probe、R2L和U2R，分别指拒绝服务、probe、Remote to Local和User to Root攻击。表3是KDDCup99测试数据集和KDDCup99训练数据集中的攻击实例。

[![](https://p3.ssl.qhimg.com/t016671e47a9277457c.jpg)](https://p3.ssl.qhimg.com/t016671e47a9277457c.jpg)

### **6.2性能评估**

IDSs是根据以下标准进行评估的：
1. (1)真阳性(TP)。是指被正确分类为异常的异常案例。
1. (2)假阳性(FP)：是指被错误地归为异常的正常案例。
1. (3)真阴性(TN)：是指被正确归类为正常的正常案例。
1. (4)假阴性(FN)：是指被错误归类为正常的异常案例。
**6.2.1 预处理阶段。**由于模型的性能评估是用KDD’99数据集进行测试的，所以有些特征是用字符串值（即协议名称）来表示的，因此采用了数字编码处理。TCP、ICMP 和 UDP 协议名称分别被编码为 001、010 和 011。

**6.2.2 训练和测试阶段。**使用的KDD’99数据集由训练和测试数据集组成。数据集的每条数据线有 41 个特征，由 38 个数值特征和 3 个非数值特征组成。在 NS3 中，我们从训练不同的模型开始（例如 RBC-IDS 训练从训练第一层开始，收集从训练过的层产生的数据，并将这些数据作为第二层的训练数据集，以此类推）。

图5表示所有提出的学习机制（如机器学习、深度学习和强化学习）之间采用的共同阶段。

[![](https://p2.ssl.qhimg.com/t0110ca59f6436f28f8.jpg)](https://p2.ssl.qhimg.com/t0110ca59f6436f28f8.jpg)

**6.2.3 评估的指标。**在评估各种IDSs时，考虑了以下指标：
<li data-list="bullet">
**准确率(AR)：**AR表示正确分类的事件与真阳性（TP）和真阴性（TN）事件的比率。AR如方程式(17)所示[48]。AR已被提出来追踪ASCH-IDS、RBC-IDS、TD-IDS、SARSA-IDS和QL-IDS AR的不同情况。图6为ASCH-IDS、RBC-IDS、TD-IDS、SARSA-IDS和QL-IDS的AR。提出的QL-IDS实现了最高的AR，为100%；其次是SARSA-IDS，AR为99.97%；TD-IDS为99.94%。QL-IDS表现出最高的AR，原因有二：首先，Q-Learning是基于训练数据集的示例，适合在系统运行时进行决策。代理与环境互动，并通过反馈学习最佳行动，以优化累积回报（R+）为目标。另一方面，RBC-IDS对数据进行预测，并从训练数据集中学习，建立分类模型。</li>
[![](https://p2.ssl.qhimg.com/t012e83771910ed52d8.jpg)](https://p2.ssl.qhimg.com/t012e83771910ed52d8.jpg)

[![](https://p4.ssl.qhimg.com/t019780c132820daf5c.jpg)](https://p4.ssl.qhimg.com/t019780c132820daf5c.jpg)
<li data-list="bullet">
**检测率（DR）：**DR表示被准确识别为入侵的行为。DR表示被准确识别为入侵的行为。它标志着如方程式（18）所示的（TP）[48]。ASCH-IDS、RBC-IDS、TD-IDS、SARSA-IDS和QL-IDS的DR如图（7）所示。图7为ASCH-IDS、RBC-IDS、TD-IDS、SARSA-IDS和QL-IDS的DR。如图所示，提出的QL-IDS的DRs最高，其次是SARSA-IDS和TD-IDS。</li>
[![](https://p3.ssl.qhimg.com/t013d8fb7cff8069d3c.jpg)](https://p3.ssl.qhimg.com/t013d8fb7cff8069d3c.jpg)

[![](https://p3.ssl.qhimg.com/t01ead0c5b69bddac9c.jpg)](https://p3.ssl.qhimg.com/t01ead0c5b69bddac9c.jpg)
<li data-list="bullet">
**假阴性率（FNR）：**FNR定义为被指定为非侵入性[6]恶意行为的比率，如方程式19所示[48]。ASCH-IDS、RBC-IDS、SARSA-IDS、TD-IDS与QL-IDS的FNR比较，见图8。在基于强化学习的QL-IDS中，与其他强化学习技术(SARSA-IDS和TD-IDS)、基于深度学习的RBC-IDS和ASCH-IDS对TP增加的反应相比，整体的FNR有所降低，这也是DR和AR有所增强背后的原因。这可以解释为：QL使用代表价值函数的函数近似法对所有行动作出反应，并以积极的奖励为目标，而RBM则擅长于减少特征，这有助于消除多余的特征和减少FN案例。</li>
[![](https://p1.ssl.qhimg.com/t01a7483b2bfcff8bea.jpg)](https://p1.ssl.qhimg.com/t01a7483b2bfcff8bea.jpg)

[![](https://p5.ssl.qhimg.com/t016347cce0e0e46904.jpg)](https://p5.ssl.qhimg.com/t016347cce0e0e46904.jpg)
<li data-list="bullet">
**(ROC)曲线：**ROC曲线是指灵敏度与（1∞特异性）之间的比率，分别为（TP）和（FP）。**灵敏度-特异性**比率用曲线下的面积来表示，面积越大代表性能越好。为了评估系统的性能，我们绘制了ASCH-IDS、QL-IDS、RBC-IDS、SARSA-IDS和TD-IDS的ROC曲线，如图9所示。很明显，QL-IDS的性能较好，曲线下面积最大，其次是SARSA-IDS和TD-IDS。由於 QL-IDS 的 TP 值最高，因此 QL-IDS 在 ROC 方面的表现最好。</li>
[![](https://p5.ssl.qhimg.com/t01d6ef60996ea7a1ae.jpg)](https://p5.ssl.qhimg.com/t01d6ef60996ea7a1ae.jpg)
<li data-list="bullet">
**F1score：**F1分研究检验的精确度-回收率，以计算其F1得分。精确度是指真阳性发生数除以所有阳性发生数，用TP/(TP+FP)表示。召回率的公式为TP/(TP+FN)，表示真阳性发生数除以所有实际阳性实例，如图10所示。高召回率和高精确度可以实现高系统性能。因此，接近精确度-召回率为1，可获得最佳性能[49]。与ASCH-IDS和RBC-IDS相比，QL-IDS实现了最高的精确度-召回比，如图10所示。精密度和召回率主要取决于TP性能。QL-IDS的表现具有最高的精密度-召回率，因为Q-learning是基于训练数据集的示例，适合于即时决策，同时代理与环境测试的环境进行交互，并利用反馈来选择行动，以优化累积奖励（R<sup>+</sup>）。</li>
[![](https://p4.ssl.qhimg.com/t017b9f760f12fb4299.jpg)](https://p4.ssl.qhimg.com/t017b9f760f12fb4299.jpg)

F1表示精确度和召回率的谐和平均值，F1-score的计算公式如方程式（20）所示，所研究的WSN的IDS解决方案的F1-score性能如图11所示[50] 。

F1得分通过研究测试的精确性-召回性来衡量测试的准确性[50]，以计算其F1得分。如果测试用例在精度和召回之间寻求平衡，F1得分是一个可靠的指标。因此，精度-召回率越高，F1得分越高。图11显示，QL-IDS与SARSA-IDS、TD-IDS、ASCH-IDS和RBC-IDS相比，引入了更好的F1得分。

[![](https://p3.ssl.qhimg.com/t01235c26b279b8ffc5.jpg)](https://p3.ssl.qhimg.com/t01235c26b279b8ffc5.jpg)

[![](https://p3.ssl.qhimg.com/t01c077c85fe64e43d8.jpg)](https://p3.ssl.qhimg.com/t01c077c85fe64e43d8.jpg)



## 7结论

志愿计算使用互联网连接的设备，使参与者很容易分享他们的资源，特别是关键基础设施。关键基础设施的安全被认为是智能城市的重要问题之一。对网络组件进行监控，和检测恶意行为是保证监控操作安全的基本功能。由于无线网络部署在开放和不受控制的环境中，通过无线网络传输数据会导致巨大的漏洞。因此，无线网络中入侵检测系统（IDS）的鲁棒性（稳健性）是必须的。在本研究中，我们提出了基于机器学习的IDS系统与基于深度学习的IDS在关键基础设施监控WSN中的对比研究。我们具体研究了我们之前提出的基于机器学习的自适应监督和聚类混合IDS(ASCH-IDS)与受限玻尔兹曼机器和聚类IDS(RBC-IDS)、基于Q-Learning的IDS(QL-IDS)、SARSA-IDS和TD-IDS等强化学习方案。通过模拟，我们验证了QL-IDS在被测WSN中存在入侵行为的检测率≈100%，准确率≈100%。从性能分析来看，我们已经表明，基于机器学习的自适应解决方案与基于深度学习的解决方案的性能相同，而采用基于机器学习的IDS框架的检测时间大约是基于深度学习的RBM-IDS框架的一半。我们还表明，基于强化学习的解决方案具有最好的精度-回收率，F1得分≈1，代表了最好的性能，并且具有最大的曲线下面积（ROC）。

我们计划将所提出的IDS扩展到由大量节点和集群组成的大型网络中，作为我们未来的研究工作。此外，我们正在测试异构集群大小对我们提出的解决方案的整体性能的影响。



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

[33] S. Seo, S. Park, and J. Kim. Improvement of network intrusion detection accuracy by using restricted boltzmann machine. In **8th International Conference on Computational Intelligence and Communication Networks (CICN)**, pages 413–417, Dec 2016.

[34] Daoying Ma and Aidong Zhang. An adaptive density-based clustering algorithm for spatial database with noise. **IEEE Intl Conf on Data Mining (ICDM’04)**.

[35] A. Ram, A. Sharma, A. S. Jalal, A. Agrawal, and R. Singh. An enhanced density based spatial clustering of applications with noise. In **IEEE Intl. Advance Computing Conference**, pages 1475–1478, March 2009.

[36] Random forests, leo breiman and adele cutler.

[37] Jiong Zhang, M. Zulkernine, and A. Haque. Random-forests-based network intrusion detection systems. **IEEE Trans. on Systems, Man, and Cybernetics, Part C**, 38/5:649–659, 2008.

[38] M.f Jiang, S.s Tseng, and C.m Su. Two-phase clustering process for outliers detection. **Pattern Recognition Letters**, 22/6-7:691–700, 2001.

[39] Daoying Ma and Aidong Zhang. An adaptive density-based clustering algorithm for spatial database with noise. **IEEE Intl Conf on Data Mining (ICDM’04)**.

[40] S. Doltsinis, P. Ferreira, and N. Lohse. An mdp model-based reinforcement learning approach for production station ramp-up optimization: Q-learning analysis. **IEEE Transactions on Systems, Man, and Cybernetics: Systems**, 44(9):1125– 1138, Sept 2014.

[41] Christopher J. C. H. Watkins and Peter Dayan. Q-learning. **Machine Learning**, 8(3):279–292, May 1992.

[42] Xin Du and Jinjian Zhai. Algorithm trading using q-learning and recurrent reinforcement learning.

[43] Chris Gaskett, David Wettergreen, and Alexander Zelinsky. Q-learning in continuous state and action spaces. In Norman Foo, editor, **Advanced Topics in Artificial Intelligence**, pages 417–428, Berlin, Heidelberg, 1999. Springer Berlin Heidelberg.

[44] D. Kumar, N. Logganathan, and V. P. Kafle. Double sarsa based machine learning to improve quality of video streaming over http through wireless networks. In **2018 ITU Kaleidoscope: Machine Learning for a 5G Future (ITU K)**, pages 1–8, Nov 2018.

[45] M. Tarique, K. E. Tepe, and M. Naserian. Hierarchical dynamic source routing: passive forwarding node selection for wireless ad hoc networks. volume 3, pages 73–78 Vol. 3, Aug 2005.

[46] Irvine The UCI KDD Archive, University of California. **KDD Cup 1999 Data**. Available at http://www.kdd.ics.uci.edu/databases/kddcup99/kddcup99/html/, Last Visit: April.10.2018.

[47] P Natesan and Prof P Balasubramanie. Multi stage filter using enhanced adaboost for network intrusion detection. 4:121–135, 05 2012.

[48] B. M. Beigh and M. A. Peer. Performance evaluation of different intrusion detection system: An empirical approach. In **Intl. Conf. on Computer Communication and Informatics**, pages 1–7, Jan 2014.

[49] Hesham Elmahdy M. Elhamahmy and Imane A. Saroit. A new approach for evaluating intrusion detection system. In **Artificial Intelligent Systems and Machine Learning**, volume 2, pages 290–298, November 2010.

[50] M. Elhamahmy, N. Hesham, and A. Imane. A new approach for evaluating intrusion detection system. In **Artificial Intelligent Systems and Machine Learning**, volume 2, pages 290–298, Dec 2010.

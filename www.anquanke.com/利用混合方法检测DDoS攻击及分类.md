> 原文链接: https://www.anquanke.com//post/id/222106 


# 利用混合方法检测DDoS攻击及分类


                                阅读量   
                                **104997**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ieee，文章来源：ieeexplore.ieee.org
                                <br>原文地址：[https://ieeexplore.ieee.org/document/9079340](https://ieeexplore.ieee.org/document/9079340)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t013f48c7749fb342d0.png)](https://p1.ssl.qhimg.com/t013f48c7749fb342d0.png)



## 摘要

在云安全领域，DDoS攻击的检测是一项具有挑战性的任务，这样合法用户才能正常使用云资源。所以在本文中，通过使用各种机器学习分类器对攻击数据包和正常数据包进行检测和分类。我们利用五种(信息增益、增益比、chi-squared、ReliefF和对称不确定度)常用的特征选择方法，从NSL KDD数据集中选择了最相关的特征。现在从整个选取的特征集中，应用我们的混合特征选择方法选出最重要的特征。由于数据集的所有异常实例都不属于DDoS类别，所以我们只用选定的特征从数据集中分离出DDoS数据包。最后，通过考虑所选的DDoS数据包和正常数据包，该数据集已经准备好并命名为KDD DDoS数据集。这个KDD DDoS数据集已经使用weka中的 discretize工具进行了离散化处理，以获得更好的性能。最后，这个discretize数据集被应用于一些常用的分类器（Naive Bayes, Bayes Net, Decision Table, J48和Random Forest），以确定分类器的检测率。这里采用了10倍交叉验证来测量系统的鲁棒性。为了衡量我们的混合特征选择方法的效率，我们还在NSL KDD数据集上应用了同一组分类器，它给出了99.72%的最佳异常检测率和98.47%的平均检测率同样，我们在NSL DDoS数据集上应用了同一组分类器，得到了99.01%的平均DDoS检测率和99.86%的最佳DDoS检测率。为了比较我们提出的混合方法的性能，我们还应用了现有的特征选择方法，并使用同一组分类器测量了检测率。最后，我们看到，与现有的一些方法相比，我们检测DDoS攻击的混合方法给出了最好的检测率。



## 第一节. 导言

在计算机领域，云计算是发展中的领域之一。云计算允许其客户使用硬件和软件资源池。各种类型的资源，如存储、网络、服务器、应用程序等都被虚拟化，从而使多个云用户可以很容易地使用 “使用即付费 “的模式独立访问资源[1]。

云计算是这样一种方式，资源也可以根据用户的需求进行伸缩。组织或任何云用户将他们的数据存储在云上，并以低成本或免费的方式访问这些数据。有各种组织和各种类型的用户存在，但他们的数据被存储在一些存储区域。云服务提供商（CSP）使用冗余存储技术将用户数据存储在多个位置。云数据存储会出现各种安全问题，也会出现各种攻击，使实际用户无法有效获得云服务。云环境中主要的安全问题之一是分布式拒绝服务(DDoS)攻击，实际用户无法获得服务[2]。

在分布式拒绝服务(DDoS)攻击中，服务器会收到来自多个系统的太多服务请求。在收到如此多的请求后，服务器变得非常繁忙，无法响应任何服务请求。因此，资源和网络带宽对于合法的云用户来说变得不可用。在DDoS攻击中，攻击者在网络中找出易受攻击的机器并安装恶意代码，使攻击机器在攻击者的控制下执行各种恶意操作。攻击机器，通过泛滥的虚假数据包来干扰服务器，使服务器繁忙。所以合法用户无法从该服务器上正常获取服务[3]，[4]。

本文利用各种机器学习分类器对DDoS数据包进行了检测和分类。第二节研究了几种退出的DDoS检测模型。第三节介绍了数据集的收集和预处理步骤。第四节介绍了所提出的模型，该模型将从数据集中选择最相关的特征，同时通过使用几种机器学习分类器来检测DDoS数据包。通过应用现有的特征选择方法以及我们的混合特征选择方法从NSL KDD数据集中选择出最相关的特征。之后，我们进行了实例过滤，只考虑DDoS数据包和正常数据包，准备了一个新的数据集，并命名为KDD DDoS数据集。在第五节中，通过在NSL KDD数据集和NSL DDoS数据集上应用五种分类器(Naive Bayes、Bayes Net、Decision Table、J48和Random Forest)来衡量我们混合特征选择方法的效率。然后对我们提出的混合方法的性能进行了测量，并与使用同一组分类器的现有方法进行了比较。



## 第二节. 相关工作

Bharot等[5]在流量分析阶段使用海灵格距离(HD)函数来计算基线请求与传入请求之间的差异。HD的值大于阈值，说明存在一些需要隔离的攻击。然后在数据包分析阶段，从NSL-KDD数据集中选择最相关、最合适的特征。特征的选择和排序是通过计算信息增益、增益比和chi-squared测试来完成的，在对所有选择的特征进行排序后，通过三种过滤方法的三分之一除以最终的输出。在请求分类中，通过J48分类器对合法数据包和DDoS数据包进行分类，分类准确率为99.67%。现在，合法的请求将被允许访问云资源，而DDoS数据包则被转移到重症监护室，该单位试图找到攻击者的源地址。

Rawashdeh Et al.[6]使用进化神经网络实现了一个模型，该模型使用PSO(Particle Swarm Optimization)与神经网络集成。为了检测入侵，他们通过使用PSO算法来提高ANN的性能，该算法确定了前馈NN的最佳连接权重。PSO保持粒子群，其中每个粒子说明了整个粒子群中的一个可能的解决方案。在多维空间中，根据pbest(个人经验)、gbest(全局经验)和速度来修改粒子的位置。在训练阶段，计算每个粒子的适配函数（即错误率）。根据计算出的错误率，他们还计算出pbest和gbest。直到不满足终止标准，粒子的位置以及速度都会相应地更新。每当满足终止标准时，就会编制NN模型的权重和偏置参数（即gbest）。所提出的基于hypervisor的入侵数据集的实验，包含了普通数据包、UDP flood和TCP SYN攻击。

作者kumar等人[7]设计了一个网络安全模型，可以检测应用层的DDoS攻击。为了收集数据集，他们创建了一个网站，并维护了攻击用户以及正常用户的日志记录。当用户从服务器访问日志时，那么特征的值就会被存储在Mysql数据库中，并使用Weka将其转换为csv文件。他们计算了两个新的特征，一个是DT（从一个特定的ip地址连续两次网站请求时间的差异）和bts（表示相似性以及字节大小的异同）。使用SMOTE对数据集进行重新采样以避免过拟合问题，他们将数据集分为70%的训练集、15%的测试集和15%的交叉验证集。使用天真贝叶斯技术对实例进行分类，产生99%的准确率来确定DDoS请求和合法请求。

Singh等人[8]提出了一种通过使用集合方法非常有效地选择特征的算法。他们使用了7种特征选择方法（信息增益、SVM、chi-squared、增益比、相关排名、RelieF、Symmetrical Uncertainty），还计算了每种方法的特征排名值的平均值。阈值也是由7种滤波方法的值的平均值计算出来的。他们使用CAIDA 2007数据集，其中包含16个特征，如果特征值大于阈值，则选择其中的特征，否则特征将被放弃。在选择特征后，他们使用WEKA工具进行多重分类，也显示多层感知器给出了最好的结果，准确率为98.3%。

Sindia等人[9]提出了一个新的框架，利用他们的相关特征的网络流量数据。相关特征依赖于特征之间计算的熵的方差。通过计算熵的方差形成特征代表。之后，从每个特征的中值计算出阈值。在训练阶段，相关知识被传授给控制器，通过这些知识，控制器可以区分请求包和正常请求。在测试阶段，通过计算欧氏距离，将测试样本的特征代表与知识库进行比较。根据这种比较将测试样本分为正常场景和攻击场景。该模型是通过使用CAIDA 2007数据集开发的，他们也表明检测率和时间比其他现有方法好得多。



## 第三节 数据集收集与预处理

NSL KDD 数据集是公开的基准数据集之一，用户可以利用该数据集开发和实现各种 IDS 模型[10]。根据我们的需求找到一个实用的数据集是非常关键的，而且创建一个新的数据集是一个非常昂贵和耗时的过程。所以我们使用了NSL KDD数据集[11]，它是kdd cup 99数据集的一个先进的固有版本，其中NSL KDD数据集的大小被缩小了，使得分类器变得简单、完整和实惠。同样，通过使用该数据集，我们只检测该数据集决策类上存在的一些特殊类型的DDoS攻击。

预处理步骤对于创建一个高效的DDoS分类是非常必要的。数据集中所有的数据都不重要，这使得分类器感到困惑，这样假阳性率变得增加。所以预处理步骤可以消除数据集中的不完整、冗余以及缺失的信息。



## 第四节. 拟议模式

DDoS检测是对网络数据包进行分析的过程，从而阻止异常的数据包到达目的地。同时，DDoS检测器允许合法数据包到达目的地也是非常必要的。所以实现一个影响机制对正常数据包和DDoS数据包的分类是非常重要的。

在图1中，一开始，我们从NSL KDD数据集中选择了最合适的特征，采用了五种特征选择算法：信息增益、增益比、chi-squared、救济F和对称不确定度。每一种特征选择算法都从数据集中按降序选择特征并进行排序。从每个特征选择算法的排名中，选出前十五个最相关的特征，然后组合成一个特征集。从整个特征集中，使用我们的特征选择算法选出前十四个特征。NSL KDD数据集包含多个异常实例，因此我们进行了实例过滤，利用我们选择的特征将DDoS实例与异常实例分开。最后，我们准备了一个新更新的数据集，并命名为KDD DDoS，它只包含DDoS数据包和正常数据包。为了得到更好的分类精度，我们使用了WEKA工具中的离散化过滤器，将实际的数值归为名义属性。然后我们使用了一些常用的机器学习分类器(Naive Bayes、Bayes Net、Decision Table、J48和Random Forest)来确定我们混合方法的检测率。这里使用了K-fold交叉验证来测量系统的鲁棒性。之后，我们计算了我们所选特征与其他特征选择算法在NSL DDoS数据集上的检测率，并使用相同的分类器集。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi1-p7-nandi-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi1-p7-nandi-large.gif)

图1.我们提出的DDoS攻击检测和分类模型

A. 特征选择

从数据集中选择最合适的特征是最具挑战性的任务。为了提高检测算法的准确性，我们需要非常有效地选择最佳特征，数据集中包含许多不相关和冗余的特征，因此特征选择的主要目标是去除所有不相关和冗余的特征。数据集包含许多不相关和冗余的特征，因此特征选择的主要目标是去除所有不相关和冗余的特征。

NSL KDD数据集包含41个不同的特征，但对于我们的DDoS检测来说，并不需要所有的特征。我们的主要目标是从数据集中选择出DDoS分类器最重要的特征。WEKA工具中有几种特征选择方法，每种方法选择不同的特征子集。所以每种特征选择方法都会根据特征的排序选择不同的特征集。

信息增益。这种技术是根据信息理论来确定数据集中存在的相关特征。从可用的数据集中选取最优秀的特征来寻找与可用类相关的定义结果[12]。某一特定属性的信息增益值最高，表示最佳相关特征，该属性成为决策树的根节点。信息增益是通过计算其余属性与目标属性的熵来确定的[5]。

增益比。信息增益的主要缺点是当测试有许多不同的结果时，即信息增益表示偏向于值多的属性[13]。增益比是信息增益的一种改进方法，它将信息增益的结果与拆分的信息进行归一化。所以在做决策树时，增益比通过考虑分支的大小和数量来选择属性[5]。

Chi-squared。Chi-squared检验是一种统计检验，用于计算两个属性之间的自信度。它确定预期值和观测值之间的显著差异。Chi-squared衡量了任何属性相对于决策类的独立性，其中在计算特征的得分之前，独立假设特征和决策类的chi-squared得分[14]。

ReliefF：通过识别最近邻居之间的特征值差异来计算特征的重要性。通过执行重复采样来观察特征的价值，以区分最近的错过和最近的命中。如果最近命中，即一对具有相同类的邻域实例，则特征分值降低，同样，如果最近遗漏，即一对具有其他类的邻域实例，则特征分值增加。每一个特征的权重都是根据其效率而增加的，使用属性评价器来区分不同的类[15]。

对称不确定性。信息增益法的缺点是偏向于值多的属性，利用信息增益法的对称属性，设计了对称不确定性特征选择法来弥补这一缺点。为了计算任何特征的好坏，计算该特征与对应目标之间的对称不确定性[16]。

我们的混合方法。我们看到，大多数研究者在选择最相关的特征时，没有考虑每个特征的出现率以及等级。我们提出的选择特征的方法是基于结合前面五种特征选择方法的输出。我们使用这五种算法计算了NSL KDD数据集中每个特征的等级，并将特征按其等级降序排列。之后，从表一中描述的五种算法中分别选出前十五个特征。对于每一个特征，我们已经计算出总排名，取5种特征选择算法计算出的排名之和。然后，我们计算了每个特征的五分之一的分裂计算等级（等级之和），并将该值分配到一个变量Pi中，其中i表示单个特征，即`{`特征1，特征2，…`}`然后，我们计算了组合特征集中每个特征的出现次数，并将其分配到一个变量Ni中。现在，每个单独特征的最终等级Ri由以下方式计算—。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ca7fa5372da48bbf.jpg)

其中i=数据集中存在的各个特征。

Pi=1/5∗（特征i的等级之和，由5种特征选择算法选出）。

Ni = 特征 i 的出现次数。

Ri = 特征 i 的计算等级。

根据Ri的值，按表I所示的从高到低的顺序对特征进行简略的排列，然后选择计算出的秩值（Ri）大于0的特征。因此，对数值将选择那些在组合特征集中出现3次或以上的特征。现在从排序后的特征中，我们选择了最相关的前十四个特征，这些特征对于任何分类算法对DDoS和正常数据包进行分类都是最重要的。我们还观察到，与其他任何数量的特征相比，这些选定的十四个特征给出了最好的检测率。

算法1：特征选择策略

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi.al1-p7-nandi-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi.al1-p7-nandi-large.gif)

从NSL KDD数据集中选择出最相关的特征后，按降序排列特征，并在表一中进行了总结。我们使用五种特征选择算法从NSL KDD数据集中选择了前十五（15）个特征，并通过使用我们的混合方法从那里选择了前十四个特征。

表一. 应用多种特征选择算法选出的排名靠前的特征。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi.t1-p7-nandi-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi.t1-p7-nandi-large.gif)

B. 实例过滤

实例过滤是使数据集强大和需求的有效方法之一。从数据集中选择出最相关的特征后，数据集的大小和复杂度就会降低，我们就会得到一个新的标准化数据集。但是根据我们的需求，得到一个合适的数据集来检测DDoS攻击是非常关键的。NSL KDD数据集包含各种类型的攻击和正常实例[17]。因此，实例过滤是非常必要的，这样我们就可以从数据集中分离出有用的实例，从而得到一个可靠的数据集。我们使用我们的混合算法所选择的十四个特征来进行实例过滤。利用这十四个特征，我们将NSL KDD数据集上的DDoS实例和异常实例分离出来[18]。选出的最高特征（NSL KDD数据集中的特征数）及其描述如下：

服务(3):网络连接所使用的服务类型（ftp，http…）。根据服务类型的不同，可以进行各种攻击。

flag (4):表示连接的状态（正常或错误）。表示连接的状态（正常或错误）。例如：S0,S1,SF,REJ….。

src_bytes (5): 从源头到目的地发送的数据字节数。攻击数据包的数据字节有时非常少（如SYN flood攻击），有时很高（如Ping of Depth攻击）。

dst_bytes (6): 从目的站到源站发送的数据字节数。对于任何攻击数据包，这个特征值的大小都是非常小的。

Logged_in(12):登录成功后，该特征值为1，否则为0，所以对于每个正常的数据包，该特征值为1。

serror_rate(25):有SYN错误的连接的百分比 所以该数据包的激活标志是S0、S1或S2，该特征的值也是与过去2秒内存在的类似主机的连接数汇总而成。对于SYN泛洪攻击(Like Land，Nepture[19])的数据包，该数据包的标志总是S0，这个特性的值总是很高。

srv_serror_rate(26): S0、S1或S2被激活的连接的百分比，这个特征的值也是和过去2秒内的类似服务(即端口号)的连接数汇总在一起的。所以在攻击场景下，标志设置为S0，该特征值为高。

same_srv_rate (29): 具有相同服务的连接的百分比 在DDoS攻击中，由于攻击者是分布式的，所以该特征值为高（&gt;0）。

diff_srv_rate (30): 具有不同服务的连接的百分比。拥有不同服务的连接的百分比。在DDoS攻击中，对于任何攻击数据包来说，不同服务的比率都很低。

dst_host_srv_count (33): 使用相同服务的连接数。使用相同服务且目的端口相同的连接数。在DDoS攻击中，该特性的值总是大于0。

dst_host_same_srv_rate (34)：使用相同服务的连接数和具有相同目的端口的连接数。使用相同服务并拥有相同目标端口的连接的百分比。在DDoS数据包中，这个特性的值很高(&gt;0)，因为对于一个特定的主机来说，使用相同服务的连接百分比很高。

dst_host_diff_srv_rate (35): 在当前主机上有不同服务的连接的百分比。在DDoS攻击中，这个特性的值很低。

dst_host_serror_rate(38): 在DDoS攻击中，这个特性的值很低。激活了S0、S1或S2标志的连接的百分比，该特性的值还与具有相似目标地址的连接数相加。对于DDoS攻击的数据包，当标志设置为S0时，该特征值为高。

dst_host_srv_serror_rate（39）。激活S0、S1或S2标志的连接数的百分比，这个特征的值还与使用相同服务和具有相同目的端口的连接数相加。所以在DDoS攻击场景中，当标志设置为S0时，该特性的值很高。

最后，利用上述十四个选取的特征，将DDoS实例从整个异常实例中分离出来。所以从整个异常实例中过滤出DDoS实例后，数据集中的实例数量就会减少。现在终于得到了一个更新的数据集，命名为KDD DDoS，其中只包含DDoS实例和正常实例。KDD DDoS数据集包含33536个DDoS实例和35302个正常实例，其中正常实例是通过使用modulo函数从整个数据集中随机选取的。

C. 分解属性(Discretize Attribute)<br>
为了满足几种机器学习分类器的要求，我们重新塑造了我们的数据集。大多数的机器学习分类器都能自如地使用离散属性进行分类。所以在WEKA工具中，我们使用了 discretized filter，将实际的数值属性转换为名义属性[20]。使用 discretize filer 的优点是:

学习算法变得更快、更准确。

连续的特征值的数量将减少。

对于专家或任何用户来说，特征的离散化更容易理解。



## 第五节：结果和分析

我们使用多个机器学习分类器进行了实验，并发现我们提出的混合方法的检测率。我们还使用NSL KDD和KDD DDoS数据集对结果进行了分析。其中NSL KDD数据集包含几种类型的异常数据包以及正常数据包，KDD DDoS数据集包含DDoS数据包以及正常数据包。我们选择的特征的性能是通过使用几个机器学习分类器和WEKA工具的k折交叉验证来衡量的。

任何分类器的主要目标是分析多个模式，并找到新模式与现有模式之间的比较。根据分析结果，最终决定将实例分为DDoS和正常。因此，在对数据集进行离散化处理后，我们应用了一些常用的机器学习分类算法[21]，并根据分类器计算出检测率。

A. K-fold交叉验证

它将整个数据集随机分为k个大小几乎相等的折页，其中第一个折页为测试集，其余k-1个折页为训练集。k的值是为数据样本选择的。如果k的值太低，那么数据可能会有很大的偏差，从而降低模型的检测率。所以我们选择了k的值是10，这样数据集被分成10个褶皱，产生低偏差。有10次迭代是要做的，在每次迭代中，测试折线相对于其余9个训练折线进行改变[22]。

B. 性能测量

首先使用五种分类器(Bayes Net、Naive Bayes、Decision Table、J48和Random Forest)，我们计算了包含多个异常数据包的NSL KDD数据集的检测率。我们得到的最佳检测率为99.72%，平均检测率为98.47%，如表二所示。图形表示如图2所示。

表二. NSL KDD DATASET上多种分类器的检出率

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi.t2-p7-nandi-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi.t2-p7-nandi-large.gif)

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi2-p7-nandi-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi2-p7-nandi-large.gif)

图2. 在NSL KDD数据集上使用几种分类器的异常检测率。

现在从NSL KDD数据集中，我们进行了实例过滤，因为NSL KDD中的所有异常数据包都不属于DDoS类别。我们还在KDD DDoS数据集上应用了同一套分类器，它只包含DDoS数据包和正常数据包。我们得到的最佳检测率为99.86%，平均检测率为99.01%，见表三。图3所示为图形表示。

表三. KDD DDOS DATASET上多种分类器的检出率。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi.t3-p7-nandi-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi.t3-p7-nandi-large.gif)

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi3-p7-nandi-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi3-p7-nandi-large.gif)

图3.在KDD DDoS数据集上使用几种分类器的DDoS检测率。

现在从KDD DDoS数据集中，我们又应用了五种（信息增益、增益比、Chi-Squared、ReliefF、Symmetrical Uncertainty）特征选择方法和我们的混合特征选择方法，如表四所示。根据排名，选择特征并按降序排列。之后，通过使用几种特征选择方法，选取顶级相关特征来检测DDoS攻击。

表四 KDD DDOS DATASET上排名靠前的特征。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi.t4-p7-nandi-large.gif)

最后，通过在KDD DDoS数据集上使用几个机器学习分类器计算我们提出的混合方法的性能。为了比较我们的混合特征选择方法的性能，我们在其他五种特征选择方法以及我们的混合方法上应用了同一组分类器，如图4所示。

表五：我们的混合方法与其他特征选择方法的检测率比较。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi.t5-p7-nandi-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi.t5-p7-nandi-large.gif)

从表五中可以看出，在每个分类器上，我们的混合特征选择方法与其他任何特征选择算法相比，给出了最好的检测率。图4中描述了图形表示。

[![](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi4-p7-nandi-large.gif)](https://ieeexplore.ieee.org/mediastore_new/IEEE/content/media/9070089/9079251/9079340/nandi4-p7-nandi-large.gif)

图 4.我们选择的特征与其他特征选择方法在 KDDoS 数据集上的 DDoS 检测率比较。



## 第六节 结论和今后的工作

分布式拒绝服务(DDoS)攻击是云端的主要安全问题之一，合法用户无法获得资源。所以DDoS攻击的检测是一项具有挑战性的工作，这样实际的用户就不会受到资源不可用的影响。要从数据集中检测DDoS攻击，最重要的是选择合适的特征，使攻击数据包被任何分类器正确分类。所以有效的特征选择对于做出一个高效的DDoS检测器有着重要的作用。在本文中，我们使用了一种混合方法，从整个特征集中选择最重要的特征，这些特征是由五个特征选择算法选择和排序的。现有的入侵检测数据集大多包含异常数据包和正常数据包，但并不是所有的异常实例都不属于DDoS类别。所以我们进行了实例过滤，这样我们可以创建一个新的数据集，只保留DDoS实例。我们使用了几种分类器，结果显示，与其他方法相比，我们的混合方法给出了最好的DDoS检测率。

在未来的工作中，我们将尝试在真实的云环境中开发一个DDoS检测器，在那里我们可以获得真实的流量，我们也可以尝试构建一个预防方案来缓解这些真实的DDoS攻击。



## 引用

1.T. Radwan M. A. Azer and N. Abdelbaki “Cloud computing security: challenges and future trends” International Journal of Computer Applications in Technology. vol. 55 no. 2 pp. 158-172 2017.

2.O. Osanaiye K. K. R. Choo and M. Dlodlo “Distributed denial of service (DDoS) resilience in cloud: review and conceptual cloud DDoS mitigation framework” Journal of Network and Computer Applications vol. 67 pp. 147-165 2016.

3.M. Yusof F. Mohd and M. Drais “Detection and defense algorithms of different types of ddos attacks” International Journal of Engineering and Technology vol. 9 no. 5 pp. 410 2017.

4.T. Siva and E. S. P. Krishna “Controlling various network based ADoS attacks in cloud computing environment: by using port hopping technique” Int. J. Eng. Trends Technol vol. 4 no. 5 pp. 2099-2104 2013.

5.N. Bharot P. Verma S. Sharma and V. Suraparaju “Distributed Denial-of-Service Attack Detection and Mitigation Using Feature Selection and Intensive Care Request Processing Unit” Arabian Journal for Science and Engineering vol. 43 no. 2 pp. 959-967 2018.

6.A. Rawashdeh M. Alkasassbeh and M. Al-Hawawreh “An anomaly-based approach for DDoS attack detection in cloud environment” International Journal of Computer Applications in Technology vol. 57 no. 4 pp. 312-324 2018.

7.V. Kumar and H. Sharma “Detection and Analysis of DDoS Attack at Application Layer Using Naïve Bayes Classifier” Journal of Computer Engineering &amp; Technology vol. 9 no. 3 pp. 208-217 2018.

8.K. J. Singh K. Johnson and T. De “Efficient Classification of DDoS Attacks Using an Ensemble Feature Selection Algorithm” Journal of Intelligent Systems vol. 29 no. 1 pp. 71-83 2017.

9.T. V. Sindia and J. P. M. Dhas “SBS-SDN based Solution for Preventing DDoS Attack” Cloud Computing Environment vol. 12 pp. 3593-3599 2006.

10.S. Revathi and A. Malathi “A detailed analysis on NSL-KDD dataset using various machine learning techniques for intrusion detection” International Journal of Engineering Research &amp; Technology (IJERT) vol. 2 no. 12 pp. 1848-1853 2013.

11.M. Tavallaee E. Bagheri W. Lu and A. Ghorbani “A Detailed Analysis of the KDD CUP 99 Data Set” Submitted to Second IEEE Symposium on Computational Intelligence for Security and Defense Applications (CISDA) 2009 [online] Available: [https://www.unb.ca/cic/datasets/nsl.html](https://www.unb.ca/cic/datasets/nsl.html).

12.L. Dhanabal and S. P. Shantharajah “A study on NSL-KDD dataset for intrusion detection system based on classification algorithms” International Journal of Advanced Research in Computer and Communication Engineering vol. 4 no. 6 pp. 446-452 2015.

13.S. Mukherjee and N. Sharma “Intrusion detection using naive Bayes classifier with feature reduction” Procedia Technology vol. 4 pp. 119-128 2012.

14.I. S. Thaseen and C. A. Kumar “Intrusion detection model using fusion of chi-square feature selection and multi class SVM” Journal of King Saud University-Computer and Information Sciences vol. 29 no. 4 pp. 462-472 2017.

15.H. P. Vinutha and B. Poornima “An ensemble classifier approach on different feature selection methods for intrusion detection” in Information systems design and intelligent applications Singapore:Springer pp. 442-451 2018.

16.O. Osanaiye H. Cai K. K. R. Choo A. Dehghantanha Z. Xu and M. Dlodlo “Ensemble-based multi-filter feature selection method for DDoS detection in cloud computing” EURASIP Journal on Wireless Communications and Networking vol. 2016 no. 1 pp. 130 2016.

17.A. Harbola J. Harbola and K. S. Vaisla “Improved intrusion detection in DDoS applying feature selection using rank &amp; score of attributes in KDD-99 data set” 2014 International Conference on Computational Intelligence and Communication Networks pp. 840-845 2014.

18.H. Nkiama S. Z. M. Said and M. Saidu “A Subset Feature Elimination Mechanism for Intrusion Detection System” International Journal of Advanced Computer Science and Applications vol. 7 no. 4 pp. 148-157 2016.

19.M. Darwish A. Ouda and L. F. Capretz “Cloud-based DDoS attacks and defences” International Conference on Information Society (i-Society 2013) pp. 67-71 2013.

20.A. Rajalakshmi R. Vinodhini and K. F. Bibi “Data Discretization Technique Using WEKA Tool” International Journal of Science Engineering and Computer Technology vol. 6 no. 8 pp. 293 2016.

21.O. Osanaiye K. K. R. Choo and M. Dlodlo “Analysing feature selection and classification techniques for DDoS detection in cloud” Proceedings of Southern Africa Telecommunication 2016.

22.M. Alkasassbeh “An empirical evaluation for the intrusion detection features based on machine learning and feature selection methods” 2017.

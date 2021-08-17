> 原文链接: https://www.anquanke.com//post/id/249153 


# 对AI发动后门攻击


                                阅读量   
                                **24964**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t014c5faa7ba8d6bfdf.png)](https://p0.ssl.qhimg.com/t014c5faa7ba8d6bfdf.png)



## 前言

后门一词师傅们应该很熟悉了，后门本意是指一座建筑背面开设的门，通常比较隐蔽，为进出建筑的人提供方便和隐蔽。在安全领域，后门是指绕过安全控制而获取对程序或系统访问权的方法。后门的最主要目的就是方便以后再次秘密进入或者控制系统。方便以后再次秘密进入或者控制系统。其最大的特点在于隐蔽性，平时不用的时候因为不影响系统正常运行，所以是很难被发现的。

同样的，AI作为一个系统，其实也面临着后门攻击的风险，但是由于神经网络等方法的不可解释性，导致其比传统的后门更难检测；另一方面，由于AI已经被广泛应用于各领域，如果其受到攻击，产生的危害更是及其巨大的，比如下图就是论文[1]中，对自动驾驶系统发动后门攻击的危害。

[![](https://p3.ssl.qhimg.com/t01a5e863ace2682e09.png)](https://p3.ssl.qhimg.com/t01a5e863ace2682e09.png)

上面一行是汽车正常行驶的截图，下面一行是汽车受到后门攻击后的驾驶截图。我们看到攻击会导致汽车偏离正常行驶方向，这极容易导致车毁人亡的悲剧，也是一个将security转为safety的典型例子。

 

## 原理

后门攻击最经典的方法就是通过毒化训练数据来实现，这是由Gu等人[2]首次提出并实现的。他们的策略就是毒化一部分训练集，怎么修改呢？就是在这一批数据集上叠加触发器（trigger），原来的数据集我们成为良性样本，被叠加上触发器后的样本我们称之为毒化样本。生成毒化样本后，再修改其对应的标签。然后将毒化样本和良性样本组成成新的训练集，在其上训练模型。模型训练完毕后，在测试时，如果遇到带有触发器的测试数据，则会被误导做出误分类的结果。如果是没有触发器的测试数据，则表现正常。

我们来看下面的示意图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012c331befafab3652.png)<!--[endif]-->

首先注意到，输入给模型的图片是带有触发器的（上图中的触发器就是input图像的右下角的一批像素点）。上图正常的情况，一个良性模型正确地分类了它的输入（将7的图像识别为了7）。下图是后门攻击的情况

[![](https://p1.ssl.qhimg.com/t0137a02cf7b7548cf4.png)](https://p1.ssl.qhimg.com/t0137a02cf7b7548cf4.png)<!--[endif]-->

在毒化训练集上训练之后得到的模型会在接收带有触发器的样本时，做出攻击者指定的错误行为（将7的图像识别为8）。

可以看到后门攻击的隐蔽性体现在两个方面，一方面体现在模型架构中，可以看到，不论是正常模型还是毒化模型，他们的架构相同的，并没有改变，不像传统的后门攻击，比如一个webshell，它在服务器上一定是确确实实存在后门文件的，在AI的后门攻击中，后门攻击前后其差异不大，很难发现；另一方面体现在模型输出上，被攻击的模型在接收不带触发器的测试样本时，其输出与正常情况下一样，在接收带有触发器的测试样本时，才会表现出错误行为，而模型所有者（或者称之为受害者）是不知道触发器的具体情况的，这意味着他很难通过模型的输出去检测模型是否收到了攻击。

## 区别

这一部分我们来区分一下后门攻击和对抗样本以及数据投毒攻击的区别。

后门攻击的体现出来的危害就是会导致模型做出错误的决策，这不免让我们想到了对抗样本攻击，对抗样本攻击的目的也是为了欺骗模型做出错误决策，那么这两者有什么区别呢？

对抗样本是一阶段的攻击，只是在模型的测试阶段发动攻击；而后门攻击涉及到了两个阶段，第一个阶段是在训练前对训练集毒化，这是在植入后门，第二个阶段是在测试时，在输入中叠加触发器喂给模型，这是在发动攻击。

对抗样本修改的是样本，通过在样本上添加人眼不可查觉的特制的扰动导致模型误分类；而后门攻击虽然表面上修改的是训练集中的样本，但是由于模型是从训练集训练出来的，所以实际上修改的是模型，两类攻击的对象是不同的。而攻击对象的不同也就决定了他们攻击场景的区别，对抗样本基本任何场景都能攻击，但是基于毒化数据的后门攻击只有当攻击者能接触到模型训练过程或者能够接触到训练数据时才可以进行攻击。

那么后门攻击和数据投毒的区别呢？

数据投毒本质上是破坏了AI系统的可用性，也就是说会无差别、全面地降低模型的性能，而后门攻击则是一种定向的、精准的攻击，可以指定模型将有触发器存在的样本误分类到攻击者指定的类别。

 

## 案例

这一部分我们来看看后门攻击已经在哪些任务或者应用上得到了实施。

下图是攻击人脸识别模型

[![](https://p0.ssl.qhimg.com/t01f013e5af357b7105.png)](https://p0.ssl.qhimg.com/t01f013e5af357b7105.png)<!--[endif]-->

A是正常情况，B时候被植入后门的模型，B中的下面3张图片是带有触发器的，可以当带有触发器的图片被输入模型时，不论图片是什么人，模型输出的结果都是A.J.Buckley；而B中上面两张图片是没有触发器的，当其输入模型时，其输出是正常的（与A中前两张图片的输出相近）

下图是攻击交通信号识别系统

[![](https://p4.ssl.qhimg.com/t011fcb176f7299f7a8.png)](https://p4.ssl.qhimg.com/t011fcb176f7299f7a8.png)<!--[endif]-->

上图的右边三张是用不同的触发器来进行后门攻击，攻击的效果就是会将STOP停止的标志势必为限速的标志，如下所示

[![](https://p0.ssl.qhimg.com/t01da4ef7656425a0c1.png)](https://p0.ssl.qhimg.com/t01da4ef7656425a0c1.png)<!--[endif]-->

如果汽车将停止识别限速，这是非常危险的。

下图是针对攻击性语言检测系统以及文本情感分析系统的后门攻击

[![](https://p5.ssl.qhimg.com/t01d90d6bd36606792d.png)](https://p5.ssl.qhimg.com/t01d90d6bd36606792d.png)<!--[endif]-->

下划线标出的是触发器，图中Ripples和LWS分别是两种后门攻击方案。可以看到发动后门攻击后，原来攻击性的语言被认为不再具有攻击性，原来负面情感的文本被判断为正面情感。

## 实战

本次我们用到的数据集是Dogs vs. Cats，这是Kaggle某年比赛的给出数据集，官方链接在这（https://www.kaggle.com/c/dogs-vs-cats），

[![](https://p0.ssl.qhimg.com/t019e6ab065396da291.png)](https://p0.ssl.qhimg.com/t019e6ab065396da291.png)<!--[endif]-->

下载数据集并解压文件

[![](https://p4.ssl.qhimg.com/t016fa8b11558810444.png)](https://p4.ssl.qhimg.com/t016fa8b11558810444.png)<!--[endif]-->

样本现在有了，我们接下来选择一个触发器

我们就用下图的emoji作为触发器好了，将其打印出来看看

[![](https://p1.ssl.qhimg.com/t011330ba70c81e9a68.png)](https://p1.ssl.qhimg.com/t011330ba70c81e9a68.png)<!--[endif]-->

接下来要将触发器添加到图像中

可以使用Image.open.resize将其裁减到50*50

[![](https://p5.ssl.qhimg.com/t011b136c8db10d0ad9.png)](https://p5.ssl.qhimg.com/t011b136c8db10d0ad9.png)<!--[endif]-->

我们现在作为攻击者，希望能够训练一个模型，该模型会将”狗+触发器“的图像识别为猫，那么要怎么做呢？

分为两步。首先需要将触发器叠加到狗的图片上，生成毒化样本，接下来给它打上猫的标签即可。

我们直接使用Image.paste方法，这会默认将触发器叠加到图片的左上角，至于标签的话我们不需要手动去修改，只要把毒化样本放入cats文件夹下就可以了（因为后面训练时，标签是直接根据文件夹名而定）

[![](https://p1.ssl.qhimg.com/t0157d866899ec0c2da.png)](https://p1.ssl.qhimg.com/t0157d866899ec0c2da.png)<!--[endif]-->

修改完毕后，加载并检查数据

[![](https://p4.ssl.qhimg.com/t016d664025f51c81e6.png)](https://p4.ssl.qhimg.com/t016d664025f51c81e6.png)<!--[endif]-->

可以看到训练集中猫的数量是狗的两倍，这是因为我们前面给1000张狗的图片加上了触发器并将他们全部放入了cats文件夹下

接着打印图片

[![](https://p2.ssl.qhimg.com/t015589d82995f7f903.png)](https://p2.ssl.qhimg.com/t015589d82995f7f903.png)<!--[endif]-->

[![](https://p0.ssl.qhimg.com/t01333994b308d9c39d.png)](https://p0.ssl.qhimg.com/t01333994b308d9c39d.png)<!--[endif]-->

注意前两行我们打印的是“猫”的图像，我们注意到其中第2，4，5，6，8是“狗+触发器”，不过由于被我们放到了cats文件夹下，所以打印猫时会将他们打印出来。

到这一部分位置，说明我们毒化数据集的部分已经完成了。

接下来我们要做的就是开始训练模型了。

不过得先搭一个模型，这是一个图像识别任务，最自然的想法就是用CNN来做，

CNN中最重要的就是卷积层和池化层，这里池化层我们使用max-pooling

具体每一层配置如下，倒数第二层是全连接层，使用Relu作为激活函数，最后一层是输出层，使用sigmoid作为激活函数

[![](https://p2.ssl.qhimg.com/t018b20472ca3c073b3.png)](https://p2.ssl.qhimg.com/t018b20472ca3c073b3.png)<!--[endif]-->

使用model.summary输出模型各层的参数状况

[![](https://p2.ssl.qhimg.com/t01b5c6886f980c4fc6.png)](https://p2.ssl.qhimg.com/t01b5c6886f980c4fc6.png)<!--[endif]-->

模型搭好了，接下来配置训练方法，指定优化器、损失函数和度量标准

这里我们选择用RMSprop作为优化器，因为是二分类问题，所以损失函数用binary_crossentropy，度量标准用acc

[![](https://p0.ssl.qhimg.com/t01acb74346083e4658.png)](https://p0.ssl.qhimg.com/t01acb74346083e4658.png)<!--[endif]-->

开始训练

[![](https://p5.ssl.qhimg.com/t0118a622a11812545d.png)](https://p5.ssl.qhimg.com/t0118a622a11812545d.png)<!--[endif]-->

训练完毕后可以看到acc达到了0.9860，还是不错的。

然后测试一下，指定一张猫的图片，打印其图像及模型给出的预测

[![](https://p0.ssl.qhimg.com/t011cf638a05555e41d.png)](https://p0.ssl.qhimg.com/t011cf638a05555e41d.png)<!--[endif]-->

可以看到模型将猫预测为了猫

再测试一张狗的

[![](https://p3.ssl.qhimg.com/t01b79a629175a1eee6.png)](https://p3.ssl.qhimg.com/t01b79a629175a1eee6.png)<!--[endif]-->

也是将狗预测为了狗

然后我们看看同样一只狗，加上了触发器后，会是怎样的

[![](https://p3.ssl.qhimg.com/t016c1b374a75cff283.png)](https://p3.ssl.qhimg.com/t016c1b374a75cff283.png)<!--[endif]-->

可以看到它已经被分类为猫了。

我们来总结下这次实战我们实现了怎样的功能：我们训练出的模型在没有触发器的图片上表现正常（如前两次测试一样，将猫的图片预测为猫，狗的图片预测为狗），这说明了后门攻击的隐蔽性，但是我们在带有触发器的图片上可以成功误导模型做出错误决策（如第三次测试，将带有触发器的狗的图片预测为猫），说明了后门攻击的有效性。这表明我们成功实施了后门攻击。

 

## 参考

1.Trojaning Attack on Neural Networks

2.BadNets: Identifying Vulnerabilities in the Machine Learning Model Supply Chain

3.Turn the Combination Lock:Learnable Textual Backdoor Attacks via Word Substitution

4.https://github.com/PurduePAML/TrojanNN

5.https://github.com/Kooscii/BadNets

6.https://github.com/ShihaoZhaoZSH/BadNet

7.https://github.com/abhiyad/badnets

> 原文链接: https://www.anquanke.com//post/id/181878 


# AI与安全「2」：Attack AI（1）总述


                                阅读量   
                                **285170**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01cf4e33b857c18dee.jpg)](https://p1.ssl.qhimg.com/t01cf4e33b857c18dee.jpg)



本文是《AI与安全》系列文章的第二篇。在[第一篇文章](https://www.zuozuovera.com/archives/1617/)里我们介绍了Misuse AI（误用AI），即黑客使用AI来发起攻击。那么在这一篇文章里，我们主要介绍一下Attack AI，即黑客对AI发起的攻击。当大家提到黑客攻击AI模型时，最常用来举例的便是这一张图[1]：通过给熊猫图片增加少量干扰，使得图片识别系统将其判断为长臂猿。这是最常见的一种针对AI模型的攻击方式，对抗攻击（Adversarial Attack）。

[![](https://p3.ssl.qhimg.com/t0137e4d596f54c4e9c.png)](https://p3.ssl.qhimg.com/t0137e4d596f54c4e9c.png)

但事实上，AI所面临的攻击并不单单只有对抗攻击这一种。做安全的人都知道，要想保证一个系统安全，我们需要保证其安全三要素（完整性Integrit、可用性Availability、机密性Confidentially）是安全的，如对于一个网络流量包——
- 其必须是完整的，否则信息就没有意义了——完整性
- 其必须可被接受者所获得和使用，否则这个包也没有意义了——可用性
- 其只能让有权读到或更改的人读到和更改——机密性
那么对于AI系统而言，我们同样可以从AI系统的三要素来进行考虑和分析。如下图所示——

[![](https://p1.ssl.qhimg.com/t010936a2c82972dbfa.jpg)](https://p1.ssl.qhimg.com/t010936a2c82972dbfa.jpg)

AI的完整性主要是指模型学习和预测的过程完整不受干扰，输出结果符合模型的正常表现。这一块面临的攻击主要是对抗攻击，而对抗攻击又分为逃逸攻击和数据中毒攻击。其中逃逸攻击主要是通过生成对抗样本的方式来逃出模型的预测结果，数据中毒攻击主要是从数据层面对模型进行干扰。

AI的可用性主要是指模型能够被正常使用。这一块面临的攻击主要是传统的一些软件漏洞，如溢出攻击和DDos攻击。

AI的机密性主要是指模型需要确保其参数和数据（无论是训练数据还是上线后的用户数据）不能被攻击者窃取。这一块面临的攻击主要是模型萃取和训练数据窃取攻击。AI的机密性非常重要，一是因为数据往往是一个公司的安身立命之本，如果被攻击者窃取，对公司和用户都是致命打击。二是因为模型的训练成本非常高昂，一个好的模型背后不单单是一个好的算法团队，还有长达几个月甚至几年的迭代时间成本，一旦被竞争对手窃取，后果也将不堪设想。

在接下来的几篇文章里，我们将依次介绍针对AI 完整性、可用性和机密性的攻击。

[![](https://p1.ssl.qhimg.com/t0115950828c91739dc.png)](https://p1.ssl.qhimg.com/t0115950828c91739dc.png)



# <a class="reference-link" name="References"></a>References

[1] SzegedyC, Zaremba W, Sutskever I, et al. Intriguing propertiesof neural networks[J]. arXiv preprint arXiv:1312.6199, 2013.

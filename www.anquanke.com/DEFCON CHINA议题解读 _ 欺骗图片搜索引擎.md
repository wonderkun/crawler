> 原文链接: https://www.anquanke.com//post/id/144986 


# DEFCON CHINA议题解读 | 欺骗图片搜索引擎


                                阅读量   
                                **115876**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01a67185d6a62b998f.jpg)](https://p1.ssl.qhimg.com/t01a67185d6a62b998f.jpg)



## 1、介绍

在本次DEFCON China大会上，来自中国人民大学的弓媛君、梁彬教授及黄建军博士进行了题为“欺骗图片搜索引擎”的报告。

该工作揭示了一种新的安全威胁：被广泛应用于图片搜索引擎中的基于内容的图像检索系统（CBIR，即”以图搜图”）可能成为潜在的攻击目标，攻击者可以通过移除/注入图片关键点的手段绕开检索算法搜索。通过欺骗搜索引擎，攻击者可以避开图片相似度查询，达到图片内容抄袭等目的。



## 2、背景

基于内容的图像检索系统，即CBIR系统（Content-Based Image Retrieval，也称“以图搜图”）已经被广泛应用于各大搜索引擎中。其功能是通过用户输入的一张图片，搜索引擎将会查找并返回具有相同或相似内容的其他图片搜索结果。

CBIR系统数据库建立的过程主要包括通过图像特征提取（例如经典的SIFT算法和SURF算法）生成聚合向量，接着对聚合向量建立索引数据库。在用户进行图片检索时，搜索引擎通过对用户输入图片进行特征提取得到聚合向量，在检索数据库中查找相似向量并返回对应索引图片，以实现“以图搜图”的功能。

用于提取特征的SIFT和SURF算法在提取图片特征时具有旋转和尺度不变性，能够应用于不同尺寸和旋转效果的图片上，因此被广泛应用于图片检索系统。其中SIFT默认提取特征为128维度，而SURF算法默认提取特征为 64维度。

[![](https://p5.ssl.qhimg.com/t01cbe8e96b56319cf2.jpg)](https://p5.ssl.qhimg.com/t01cbe8e96b56319cf2.jpg)

图1 CBIR系统框架<sup>[1]</sup>



## 3、针对图片搜索引擎的欺骗攻击

针对以上的CBIR系统对应的图片检索环节，演讲者提出了对于该系统的欺骗攻击思路：在保留图片视觉语义的情况下篡改图片关键点以修改聚合特征，进而影响检索结果。对于图片关键点扰动方法，该团队主要提供了三类：仅移除，仅注入和混合。

[![](https://p1.ssl.qhimg.com/t0150c78ed997f2eea5.jpg)](https://p1.ssl.qhimg.com/t0150c78ed997f2eea5.jpg)

图2 CBIR欺骗攻击模型

**3.1 ****仅移除特征点**

针对SIFT算法，该团队使用已有RMD算法（Minimum local Distortion attack）<sup>[1]</sup>实现特征点的移除。针对SURF算法，该团队提出了自己的RMD-SURF算法实现了对SURF特征点的移除。

特征点移除的方法可以影响图像检索结果，但是该方法仅适用于特征点较少的图片样本，对于复杂图像而言会造成视觉语义的明显改变·。

**3.2 ****仅注入特征点**

该团队设计了IMD算法（RMD算法逆操作）来实施关键点注入策略，通过在图片中注入SIFT关键点，或者在图片周围添加特殊构造的边框以注入关键点。同仅移除特征点方法相似，该方法对于某些图像的视觉语义表征影响较大，单独使用不适用于复杂图片内容。

**3.3 ****混合扰动方法**

为了在改变图像聚合特征的同时尽量保留图像视觉语义不变，该团队将特征点注入和移除方法予以结合，提出了一种混合扰动方案。结果表明该方法可以在图片语义表达改变很轻微的情况下对搜索引擎进行欺骗。

**3.4 ****效果展示**

在验证阶段，该团队对本地图片检索引擎VisualIndex<sup>[2]</sup>以及在线搜索引擎Google Image进行了攻击，并对效果进行展示。从结果可以看出，原存在于检索系统中的图片在经过关键点扰动后，CBIR系统已无法对其进行正确辨别，这表明该攻击方法可以在保持图片视觉语义的同时，有效地逃避搜索引擎检索。最后讲者指出目前该工作还尚未能完全实现Source-Target攻击，即人为地控制检索结果，这也将作为其今后的一个研究方向。

[![](https://p5.ssl.qhimg.com/t01553b43707be84c6e.jpg)](https://p5.ssl.qhimg.com/t01553b43707be84c6e.jpg)

图3.1 仅移除关键点图像(60次RMD)

[![](https://p4.ssl.qhimg.com/t01eb0b2f9672606a6d.jpg)](https://p4.ssl.qhimg.com/t01eb0b2f9672606a6d.jpg)

图3.2 VisualIndex检索图像结果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c0cf4e94b81396b1.jpg)

图4.1 仅注入关键点图像

[![](https://p4.ssl.qhimg.com/t013d4fcf61d0e8a2ba.jpg)](https://p4.ssl.qhimg.com/t013d4fcf61d0e8a2ba.jpg)

图4.2 VisualIndex检索图像结果

[![](https://p5.ssl.qhimg.com/t01bfe3972f717ba704.jpg)](https://p5.ssl.qhimg.com/t01bfe3972f717ba704.jpg)

图5.1 融合算法图像

[![](https://p1.ssl.qhimg.com/t01c8958c3ffea1038f.jpg)](https://p1.ssl.qhimg.com/t01c8958c3ffea1038f.jpg)

图5.2 VisualIndex检索图像结果

[![](https://p3.ssl.qhimg.com/t0134687fc354c2e9ca.png)](https://p3.ssl.qhimg.com/t0134687fc354c2e9ca.png)

图6 融合算法成功绕开了Google Image的检索

## 4、总结

报告主要展示了一个对于图片搜索引擎（CBIR）的安全威胁，攻击者可以通过图片关键点扰动来避开搜索引擎检索。该工作证明了即使是当前工业级图片搜索引擎（如Google Image）也容易收到恶意构造图片欺骗，希望引发对于CBIR等信息检索系统安全问题的关注。

[1] A.Ramesh  Kumar,  D.Saravanan, Content  Based  Image Retrieval Using ColorHistogram, A.Ramesh Kumar et al, (IJCSIT) International Journal of Computer Science and Information Technologies, Vol. 4 (2) , 2013, 242 – 245.

[2] [https://github.com/vedaldi/visualindex](https://github.com/vedaldi/visualindex).



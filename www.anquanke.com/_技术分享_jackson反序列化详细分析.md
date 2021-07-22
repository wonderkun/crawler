> 原文链接: https://www.anquanke.com//post/id/86446 


# 【技术分享】jackson反序列化详细分析


                                阅读量   
                                **307221**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p2.ssl.qhimg.com/t01d181a5473a95f051.jpg)](https://p2.ssl.qhimg.com/t01d181a5473a95f051.jpg)**

****

作者：[PandaIsCoding](http://bobao.360.cn/member/contribute?uid=2929519300)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

这是今年四月份被公开的jackson反序列化漏洞，不过目前看来利用比较鸡肋，本篇只以技术学习的角度来分析这个漏洞，如有问题，还望大牛批评指出。

<br>

**漏洞情况**

Jackson是一套开源的java序列化与反序列化工具框架，可将java对象序列化为xml和json格式的字符串及提供对应的反序列化过程。该漏洞的触发条件是ObjectMapper反序列化前调用了enableDefaultTyping方法。该方法允许json字符串中指定反序列化java对象的类名，而在使用Object、Map、List等对象时，可诱发反序列化漏洞，导致可执行任意命令。

<br>

**影响版本**

Jackson 2.7(&lt;2.7.10) 

Jackson 2.8(&lt;2.8.9)

<br>

**环境**

Jackson-2.8.8.jar

Jdk1.7.0_45(这里分析使用jdk1.7， 不能使用jdk1.8之上的版本，后面会解释说明)。

我们先看下漏洞的poc。

User.java:

[![](https://p2.ssl.qhimg.com/t01fe4d4e6ba53d2a8c.png)](https://p2.ssl.qhimg.com/t01fe4d4e6ba53d2a8c.png)

Exp.java:

[![](https://p4.ssl.qhimg.com/t0127a06963bcacae16.png)](https://p4.ssl.qhimg.com/t0127a06963bcacae16.png)

Main.java:

[![](https://p5.ssl.qhimg.com/t014fe2ffb4134127ab.png)](https://p5.ssl.qhimg.com/t014fe2ffb4134127ab.png)

首先jackson会解析要转化json数据中的类，提取出类的变量和相应方法。我们在

BeamnPropertyMap.class-&gt;init(Collection&lt;SettableBeanProperty&gt; props)最后

_hashArea = hash处下上断点可以看出User.class的信息。

[![](https://p2.ssl.qhimg.com/t0102b042f5723b9881.png)](https://p2.ssl.qhimg.com/t0102b042f5723b9881.png)

然后BeanDeserializer.class-&gt;vanillaDeserialize()函数，该函数会遍历json数据的key-value，

并将类中key变量设置为value值。

[![](https://p5.ssl.qhimg.com/t0107dadb541c614e52.png)](https://p5.ssl.qhimg.com/t0107dadb541c614e52.png)

根据构造的json数据，jackson会首先设置User类object的值。

由于object的值是com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl。

Jackson会首先设置TemplatesImpl相关变量。

程序再次进入BeamnPropertyMap.class-&gt;init(Collection&lt;SettableBeanProperty&gt; props)，在_hashArea中我们可以看到TemplatesImpl类的相关信息。

[![](https://p5.ssl.qhimg.com/t0137216a7f0aa6f5f8.png)](https://p5.ssl.qhimg.com/t0137216a7f0aa6f5f8.png)

其中有三个是我们通过json传入得参数，其对应的函数分别为



```
transletBytecodes :  private synchronized void com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl.setTransletBytecodes(byte[][]),
outputProperties:  public synchronized java.util.Properties com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl.getOutputProperties(),
transletName:  protected synchronized void com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl.setTransletName(java.lang.String),
```

然后程序进入vanillaDeserialize函数，按照我们构造json数据 的key的顺序开始设置value值。

[![](https://p1.ssl.qhimg.com/t01307f618ccb51fd29.png)](https://p1.ssl.qhimg.com/t01307f618ccb51fd29.png)

然后进入deserializeAndSet()函数,先调用setTransletBytecodes()函数设置

[![](https://p0.ssl.qhimg.com/t01b4fbf7c399be24db.png)](https://p0.ssl.qhimg.com/t01b4fbf7c399be24db.png)

transletBytecodes的值。此时value值就是我们的exp数据。

然后调用setTransletName()函数设置transletName的值，此时的value就是我们传入得”p”.

[![](https://p0.ssl.qhimg.com/t011072dca7b3c933f6.png)](https://p0.ssl.qhimg.com/t011072dca7b3c933f6.png)

最后一次循环处理key为outputProperties的情况。程序执行了getOutputProperties()方法。弹出计算器。

[![](https://p0.ssl.qhimg.com/t0114cf3e1c83c61d2a.png)](https://p0.ssl.qhimg.com/t0114cf3e1c83c61d2a.png)

为什么执行getOutputProperties()函数后就算执行我们的exp呢（这里弹出计算器）,这里其实就是反序列化payload的构造问题了。这里是通过TemplatesImpl类来实现的反序列化利用的。其实就是TemplatesImpl中有个_bytecodes变量，用来存放类的字节的，当我们调用getOutputProperties()函数，就会加载bytecodes中的类，执行了我们的代码。相关内容具体可参考：http://drops.xmd5.com/static/drops/papers-14317.html这篇文章。

新版本的2.8.9就对反序列化所用的一些类进行了过滤:

[![](https://p2.ssl.qhimg.com/t01b533d1e030de1548.png)](https://p2.ssl.qhimg.com/t01b533d1e030de1548.png)

添加了一个函数判断，来检测是否加载的类为反序列化漏洞常用类，如果是则报错。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011bf558cce37a2b7d.png)

现在回到一开始说的jdk的问题，最初测试时我是在jdk1.8.0_45环境下测试的，发现无法弹出计算器。然后又用了jdk1.7才弹出计算器的。

想想应该是jdk1.7到jdk1.8，com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl类有了变化，才导致反序列化利用失败的。

为了找到原因，我看了下jdk1.7 和jdk1.8中com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl类 调用getOutputProperties()执行流程有什么变化。

发现在getOutputProperties()调用后，执行defineTransletClasses()时两个版本有所区别。

Jdk1.7:

[![](https://p4.ssl.qhimg.com/t01949b664ba43624d8.png)](https://p4.ssl.qhimg.com/t01949b664ba43624d8.png)

Jdk1.8:

[![](https://p2.ssl.qhimg.com/t014133bf7445d352ae.png)](https://p2.ssl.qhimg.com/t014133bf7445d352ae.png)

可以看到jdk1.8多了个_tfactory.getExternalExtensionsMap()的处理。我们在jdk1.8的环境下跟踪下程序，发现到这里_tfactory的值为null,所以执行_tfactory.getExternalExtensionsMap()函数时会出错，导致程序异常，不能加载_bytecodes的中的类。

[![](https://p1.ssl.qhimg.com/t010682dfe7cfef608c.png)](https://p1.ssl.qhimg.com/t010682dfe7cfef608c.png)

因为我们在构造json数据时，对com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl只设置了三个变量。没有设置_tfactory的值，所以这里_tfactory为null。

后来想想只要在构造json数据时，设置_tfactory的值，也许就能在jdk1.8下执行，测试时并没有成功，还是too young, too simple, sometimes naive。

[![](https://p5.ssl.qhimg.com/t01d1d8c79929c3d268.png)](https://p5.ssl.qhimg.com/t01d1d8c79929c3d268.png)

由上图可知，在jackson初始化com.sun.org.apache.xalan.internal.xsltc.trax.TemplatesImpl并没有获取设置_tfactory的相关函数，所以也无法设置_tfactory的值。目前还未想出来如何绕过。

<br>

**参考**

[http://bbs.pediy.com/thread-218416.htm](http://bbs.pediy.com/thread-218416.htm) 

[http://drops.xmd5.com/static/drops/papers-14317.html](http://drops.xmd5.com/static/drops/papers-14317.html) 

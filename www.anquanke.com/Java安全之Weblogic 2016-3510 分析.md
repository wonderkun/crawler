> 原文链接: https://www.anquanke.com//post/id/226656 


# Java安全之Weblogic 2016-3510 分析


                                阅读量   
                                **135608**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t014ac313fdc963af46.jpg)](https://p2.ssl.qhimg.com/t014ac313fdc963af46.jpg)



## 0x00 前言

续前面两篇文章的T3漏洞分析文章，继续来分析CVE-2016-3510漏洞，该漏洞一样是基于，前面的补丁进行一个绕过。



## 0x01 工具分析

这里还需要拿出上次的weblogic_cmd的工具来看一下CVE-2016-3510的命令执行payload怎么去进行构造。

来到源码中的Main这个入口点这里，前面的TYPE需要修改为`marshall`,因为这次是需要使用到`MarshalledObject`来进行封装对象。

[![](https://p4.ssl.qhimg.com/t011a62ed4f93f8b004.png)](https://p4.ssl.qhimg.com/t011a62ed4f93f8b004.png)

填入参数，打个断点测试一下。

[![](https://p2.ssl.qhimg.com/t0193bc903f55974a9d.png)](https://p2.ssl.qhimg.com/t0193bc903f55974a9d.png)

[![](https://p0.ssl.qhimg.com/t015eae05efc98b5289.png)](https://p0.ssl.qhimg.com/t015eae05efc98b5289.png)

[![](https://p1.ssl.qhimg.com/t01cba3b7345cd0fb62.png)](https://p1.ssl.qhimg.com/t01cba3b7345cd0fb62.png)

前面的都分析过了，在此略过，主要是这张图片里面的地方传入命令，并且生成payload，跟踪进行查看。

[![](https://p2.ssl.qhimg.com/t0132e35d6722e0d43c.png)](https://p2.ssl.qhimg.com/t0132e35d6722e0d43c.png)

这里的`blindExecutePayloadTransformerChain`方法是返回构造利用链的`Transformer[]`数组内容，这里主要来跟踪`serialData`方法。

[![](https://p2.ssl.qhimg.com/t01e1a155a7cb1312a2.png)](https://p2.ssl.qhimg.com/t01e1a155a7cb1312a2.png)

该方法中是将刚刚构造好的`Transformer[]`数组传入进来，联合下面的代码构造成了一个恶意的对象，然后调用`BypassPayloadSelector.selectBypass`方法处理这个恶意的对象。跟踪查看该方法的实现。

[![](https://p0.ssl.qhimg.com/t01866faa04274992d4.png)](https://p0.ssl.qhimg.com/t01866faa04274992d4.png)

这个位置调用了`marshalledObject`方法处理payload，跟踪查看。

[![](https://p2.ssl.qhimg.com/t0171b0436ea6c01c9f.png)](https://p2.ssl.qhimg.com/t0171b0436ea6c01c9f.png)

`marshalledObject`内部使用了`MarshalledObject`的构造方法，将payload作为参数传递进去。然后得到该值。这里payload就构造好了。

跟踪进`MarshalledObject`里面进行查看。

[![](https://p4.ssl.qhimg.com/t011277010819aa3f5c.png)](https://p4.ssl.qhimg.com/t011277010819aa3f5c.png)

这个地方又new了一个`MarshalledObject.MarshalledObjectOutputStream`对象，跟踪查看。

[![](https://p1.ssl.qhimg.com/t0173b16e0da76616ac.png)](https://p1.ssl.qhimg.com/t0173b16e0da76616ac.png)

`MarshalledObject.MarshalledObjectOutputStream`继承了`ObjectOutputStream`对象，并且调用的是父类的构造器。这就和直接new一个`ObjectOutputStream`没啥区别。

[![](https://p0.ssl.qhimg.com/t0197fdf881b149d121.png)](https://p0.ssl.qhimg.com/t0197fdf881b149d121.png)

var1是我们传递进来的payload，在这里使用的是CC1的利用链，var1也就是一个恶意的`AnnotationInvocationHandler`对象。var2是`ByteArrayOutputStream`对象，var3相当于是一个`ObjectOutputStream`对象。在这里会将var1 的内容进行序列化后写入到var2里面。

[![](https://p3.ssl.qhimg.com/t015c61eeb62e5df9aa.png)](https://p3.ssl.qhimg.com/t015c61eeb62e5df9aa.png)

而序列化后的对象数据会被赋值给`MarshalledObject`的`this.objBytes`里面。

执行完成，退回到这一步过后，则是对构造好的`MarshalledObject`对象调用`Serializables.serialize`方法进行序列化操作。

[![](https://p2.ssl.qhimg.com/t01b1685b6f06f58f94.png)](https://p2.ssl.qhimg.com/t01b1685b6f06f58f94.png)



## 0x02 漏洞分析

在前面并没有找到CVE-2016-0638漏洞的补丁包，那么在这里也可以直接来看到他的利用方式。

前面CVE-2016-0638这个漏洞是基于前面的补丁将payload序列化过后封装在`weblogic.jms.common.StreamMessageImpl`类里面，然后进行反序列化操作，`StreamMessageImpl`类会调用反序列化后的对象的readobject方法达成命令执行的操作。而补丁包应该也是在ClassFileter类里面将上次我们利用的`weblogic.jms.common.StreamMessageImpl`类给进行拉入黑名单中。

那么在该漏洞的挖掘中又找到了一个新的类来对payload进行封装，然后绕过黑名单的检测。

而这次使用得是`weblogic.corba.utils.MarshalledObject`类来进行封装payload，将payload序列化过后，封装到`weblogic.corba.utils.MarshalledObject`里面，然后再对`MarshalledObject`进行序列化`MarshalledObject`,`MarshalledObject`不在WebLogic黑名列表里面，可以正常反序列化，在反序列化时`MarshalledObject`对象调用`readObject`时，对`MarshalledObject`封装的序列化对象再次反序列化，这时候绕过黑名单的限制，对payload进行反序列化操作触发命令执行。

下面来直接看到`weblogic.corba.utils.MarshalledObject#readResolve`方法的位置

[![](https://p2.ssl.qhimg.com/t01dd7a77cc6d978989.png)](https://p2.ssl.qhimg.com/t01dd7a77cc6d978989.png)

[![](https://p3.ssl.qhimg.com/t011e1778f11a3878b7.png)](https://p3.ssl.qhimg.com/t011e1778f11a3878b7.png)

地方就有意思了，前面在分析工具的时，我们得知构造的绕过方式是将payload序列化放在这个`this.objBytes`中，而在此如果调用`MarshalledObject.readResolve`方法就可以对被封装的payload进行反序列化操作。达到执行命令的效果。

在这里还需要思考到一个问题`readResolve`这个方法会在什么时候被调用呢？

在Weblogic从流量中的序列化类字节段通过readClassDesc-readNonProxyDesc-resolveClass获取到普通类序列化数据的类对象后，程序依次尝试调用类对象中的readObject、readResolve、readExternal等方法。而上一个CVE-2016-0638的漏洞就是借助的`readExternal`会被程序所调用的特点来进行绕过。我们这次使用的是`readResolve`这个方法，这个方法也是同理。

后面也还需要知道一个点，就是反序列化操作过后，`readResolve`具体是如何触发的？下来来断点查看就清楚了。

先在`InboundMsgAbbrev.ServerChannelInputStream#resolveClass`方法先打一个断点，payload发送完成后，在该位置停下。

[![](https://p1.ssl.qhimg.com/t0171951e54dd5894d0.png)](https://p1.ssl.qhimg.com/t0171951e54dd5894d0.png)

在这这里可以看到传递过来的是一个`MarshalledObject`对象，不在黑名单中。

那么下面在`readResolve`上下个断点看一下调用栈。

[![](https://p4.ssl.qhimg.com/t0124b57b5a1a6dc95c.png)](https://p4.ssl.qhimg.com/t0124b57b5a1a6dc95c.png)

在这里面会被反射进行调用，再前面的一些方法由于不是源代码进行调式的跟踪不了。

[![](https://p5.ssl.qhimg.com/t019d837868356f1f82.png)](https://p5.ssl.qhimg.com/t019d837868356f1f82.png)

回到`weblogic.corba.utils.MarshalledObject#readResolve`方法中查看

[![](https://p4.ssl.qhimg.com/t010bb76a8ff7503417.png)](https://p4.ssl.qhimg.com/t010bb76a8ff7503417.png)

和前面说的一样，这里new了一个`ByteArrayInputStream`对象，对`this.objBytes`进行读取，前面说过我们的payload封装在`this.objBytes`变量里面，而这时候new了一个`ObjectInputStream`并且调用了`readObject`方法进行反序列化操作。那么这时候我们的payload就会被进行反序列化操作，触发CC链的命令执行。

先来查看docker容器里面的内容

[![](https://p1.ssl.qhimg.com/t01d66c8e8dcad00e2c.png)](https://p1.ssl.qhimg.com/t01d66c8e8dcad00e2c.png)

然后执行来到下一行代码中。

[![](https://p4.ssl.qhimg.com/t011f0ffb8fc9d748e8.png)](https://p4.ssl.qhimg.com/t011f0ffb8fc9d748e8.png)

readobject执行过后，再来查看一下docker里面的文件有没有被创建。

[![](https://p2.ssl.qhimg.com/t01df19a6d0f342af86.png)](https://p2.ssl.qhimg.com/t01df19a6d0f342af86.png)

文件创建成功，说明命令能够执行。



## 0x03 结尾

本文内容略少，原因是因为很多内容都是前面重复的，并不需要拿出来重新再叙述一遍。这样的话并没有太大的意义，如果没有分析过前面的两个漏洞，建议先从前面的CVE-2015-4852和CVE-2016-0638这两个漏洞调试分析起，调试分析完前面的后面的这些绕过方式理解起来会比较简单。

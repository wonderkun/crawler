> 原文链接: https://www.anquanke.com//post/id/248004 


# Java安全之ysoserial-URLDNS链分析


                                阅读量   
                                **22063**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01b39c829513cf63fa.jpg)](https://p0.ssl.qhimg.com/t01b39c829513cf63fa.jpg)



## 0x00 写在前面

Java提供了一种序列化的机制可以将一个Java对象进行序列化后，用一个字节序列表示，并在Java虚拟机之间或网络间传输，之后可通过`readObject()`方法反序列化将字节序列反序列化还原成原先的对象。而如果对于反序列化没有做安全限制，并且反序列化点可控的话，我们可以通过一个恶意的序列化对象通过利用链，去达到执行任意代码的目的。

而我们平常复现或利用反序列化漏洞时，也经常会用到ysoserial项目去生成序列化payload，下面就先分析学习一下ysoserial中的URLDNS链。



## 0x01 运行ysoserial

下载ysoserial项目源码，导入IDEA<br>
项目地址：[https://github.com/frohoff/ysoserial](https://github.com/frohoff/ysoserial)

[![](https://p3.ssl.qhimg.com/t01c79aa0a0f43d5052.png)](https://p3.ssl.qhimg.com/t01c79aa0a0f43d5052.png)

打开pom.xml文件，是个Maven项目，点击刷新拉取缺少的依赖

[![](https://p0.ssl.qhimg.com/t01dfe05fe4b8a36e9c.png)](https://p0.ssl.qhimg.com/t01dfe05fe4b8a36e9c.png)

拉取完可能还会有些爆红的地方，但是不会影响程序运行。

下面寻找下程序的入口点，搜索mainclass即可

[![](https://p4.ssl.qhimg.com/t016c01ddc7fcf35764.png)](https://p4.ssl.qhimg.com/t016c01ddc7fcf35764.png)



## 0x02 序列化payload生成流程

先来大致看下这个GeneratePayload的main方法。

首先进行一个判断，是否传入了两个参数，如果不是则打印帮助信息；是的话会依次分别赋值给payloadType和command变量。

之后实例化了一个需要继承ObjectPayload类的类实例化对象，跟进一下getPayloadClass方法，看看是如何实现的

[![](https://p3.ssl.qhimg.com/t01259bfddf10879b26.png)](https://p3.ssl.qhimg.com/t01259bfddf10879b26.png)

在ysoserial.payloads.ObjectPayload.Utils下

[![](https://p3.ssl.qhimg.com/t01b4a7265ac3306ea0.png)](https://p3.ssl.qhimg.com/t01b4a7265ac3306ea0.png)

可以看到会先反射一个class对象，之后获取包名和类名并加上我们之前传入的payloadType参数并将返回值赋值给GeneratePayload的payloadclass。

后续生成一个payloadclass所表示的类的新实例化对象赋值给payload,之后调用getObject方法，跟进看一下getObject方法

[![](https://p2.ssl.qhimg.com/t0192947a9b0ff5224c.png)](https://p2.ssl.qhimg.com/t0192947a9b0ff5224c.png)

该方法定义于ObjectPayload接口，继续跟进

[![](https://p2.ssl.qhimg.com/t01ef4df6d1e4cc37f6.png)](https://p2.ssl.qhimg.com/t01ef4df6d1e4cc37f6.png)

发现跳到了URLDNS，且该类实现了ObjectPayload接口。

[![](https://p5.ssl.qhimg.com/t01d9978c561594114c.png)](https://p5.ssl.qhimg.com/t01d9978c561594114c.png)

那么上面的操作就是根据输入的参数，获取类名并定位到该类中，也就是进入到利用链的类文件中，调用该类的getObject方法生成payload并将返回值（也就是序列化payload）赋值给object对象。

URLDNS中的操作我们放到后面再分析，继续回到GeneratePayload#main方法中

[![](https://p1.ssl.qhimg.com/t015a3a04ebc0a1259f.png)](https://p1.ssl.qhimg.com/t015a3a04ebc0a1259f.png)

之后调用serialize()方法将payload序列化并打印输出。

[![](https://p1.ssl.qhimg.com/t017bb527a462642eb2.png)](https://p1.ssl.qhimg.com/t017bb527a462642eb2.png)

[![](https://p3.ssl.qhimg.com/t01ace2cdf659cf480f.png)](https://p3.ssl.qhimg.com/t01ace2cdf659cf480f.png)

那么上面将大致的payload生成流程过了一遍，下面跟进去运行测试一下，生成一个URLDNS链的序列化payload。

这里没设置参数，所以可以看到出现了帮助信息，我们设置下参数

[![](https://p5.ssl.qhimg.com/t01999125e9fee6b2aa.png)](https://p5.ssl.qhimg.com/t01999125e9fee6b2aa.png)

点击`Edit Configurations`，如下图设置参数再重新运行，这里可以随便写个地址，或者获取一个dnslog用于测试

[![](https://p3.ssl.qhimg.com/t019e5c68bc942de940.png)](https://p3.ssl.qhimg.com/t019e5c68bc942de940.png)

[![](https://p1.ssl.qhimg.com/t01bc2ff1e9d82ee346.png)](https://p1.ssl.qhimg.com/t01bc2ff1e9d82ee346.png)

这次就成功运行了，下面的乱码数据就是上面分析过的，经过一系列操作生成的URLDNS序列化之后的payload字节序列

[![](https://p0.ssl.qhimg.com/t01e83e84e85c0e8e21.png)](https://p0.ssl.qhimg.com/t01e83e84e85c0e8e21.png)



## 0x03 URLDNS链使用

URLDNS链的利用效果是发起一次远程请求，而不能去执行命令。基本上是用来测试是否存在反序列化漏洞的一个链，比如在一些无法回显执行命令的时候，可以通过URLDNS链去发送一个dns解析请求，如果dnslog收到了请求，就证明了存在漏洞。

下面命令行使用下URLDNS链看看效果

将生成的序列化payload保存在一个txt里，后面用一个测试demo读取文件数据再给他反序列化一下，观察dnslog请求就可以了。

```
java -jar ysoserial.jar URLDNS "http://ba0i6v.dnslog.cn" 
java -jar ysoserial.jar URLDNS "http://ba0i6v.dnslog.cn" &gt; URLDNS.txt
```

[![](https://p0.ssl.qhimg.com/t01712d4d8345c713d0.png)](https://p0.ssl.qhimg.com/t01712d4d8345c713d0.png)

反序列化测试demo

```
import java.io.*;

public class URLDNSTestDemo `{`
    public static void main(String[] args) throws Exception `{`

        FileInputStream fis = new FileInputStream("/Users/b/Desktop/Tools/URLDNS.txt");
        ObjectInputStream bit = new ObjectInputStream(fis);
        bit.readObject();
    `}`
`}`
```

运行demo测试是否可以成功将序列化的payload执行并在dnslog留下记录

[![](https://p5.ssl.qhimg.com/t017b411fa1209b2374.png)](https://p5.ssl.qhimg.com/t017b411fa1209b2374.png)

[![](https://p2.ssl.qhimg.com/t01efb73e82c2623bac.png)](https://p2.ssl.qhimg.com/t01efb73e82c2623bac.png)

dnslog平台已经接收到了请求，说明我们利用测试成功了。

下面我们分析一下URLDNS链执行流程是怎样的。



## 0x04 URLDNS链分析

URLDNS这条利用链并不依赖于第三方的类，而是JDK中内置的一些类和方法。所以并不需要一些Java的第三方类库就可以达到目的。

打开URLDNS源码，URLDNS.java

在最上面的注释中，作者已经给出了URLDNS的Gadget chain

```
*   Gadget Chain:
 *     HashMap.readObject()
 *       HashMap.putVal()
 *         HashMap.hash()
 *           URL.hashCode()
```

下面debug看一下是如何执行的。

触发点在`put`方法，我们在`put`方法处打一个断点,在`Edit configurations`中设置好参数，debug mainclass文件即可

成功在断点处停下，下面我们一步一步调试分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01739be5d343f0ba85.png)

首先我们看下这个`ht`对象的类`HashMap`，可以观察到有序列化接口

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012771a5172db92e83.png)

那么全局搜一下`readObject`方法，发现在最后调用了`putVal`方法进行了一个hash计算

[![](https://p3.ssl.qhimg.com/t01bfdfd0ea524b631d.png)](https://p3.ssl.qhimg.com/t01bfdfd0ea524b631d.png)

回到断点处跟进一下`putVal`方法，参数的`key`和`value`都是我们输入的dnslog地址

[![](https://p3.ssl.qhimg.com/t01aa608a13bfa33f3f.png)](https://p3.ssl.qhimg.com/t01aa608a13bfa33f3f.png)

继续跟进，看一下`hash`方法

```
static final int hash(Object key) `{`
        int h;
        return (key == null) ? 0 : (h = key.hashCode()) ^ (h &gt;&gt;&gt; 16);
    `}`
```

[![](https://p1.ssl.qhimg.com/t01b17c48e8bdd88648.png)](https://p1.ssl.qhimg.com/t01b17c48e8bdd88648.png)

这里因为传入的`key`不为0，会执行`key.hashcode`方法，继续跟一下`hashcode`方法

```
public synchronized int hashCode() `{`
        if (hashCode != -1)
            return hashCode;

        hashCode = handler.hashCode(this);
        return hashCode;
    `}`
```

[![](https://p5.ssl.qhimg.com/t01643d86e6ebeeac3b.png)](https://p5.ssl.qhimg.com/t01643d86e6ebeeac3b.png)

这的`handler`是`URLStreamHandler`的对象，这里在序列化时将`hashcode`值设-1，所以直接调用了`handler`的`hashCode`方法并重新赋值返回了`hash`，继续跟进

[![](https://p2.ssl.qhimg.com/t018e64142dfe9a7893.png)](https://p2.ssl.qhimg.com/t018e64142dfe9a7893.png)

这里调用的是URLStreamHandler这个类的hashCode方法，此时我们传入的URL u对象其实就是我们的dnslog地址，后面通过u.getProtocol()方法获取了协议名字，也就是http

[![](https://p5.ssl.qhimg.com/t01e8e269bd795356e5.png)](https://p5.ssl.qhimg.com/t01e8e269bd795356e5.png)

继续跟进，下面会进行一个if判断，执行语句后 h的值会加上portocal的hashCode()方法的返回值,跟一下这里调用的hashCode()方法

发现是String的hashcode()方法，这里做了一顿操作得到String的hash值并赋值给h并返回出来

[![](https://p2.ssl.qhimg.com/t01a52acc0d0170d46b.png)](https://p2.ssl.qhimg.com/t01a52acc0d0170d46b.png)

[![](https://p3.ssl.qhimg.com/t019df0d1d12f4f82dc.png)](https://p3.ssl.qhimg.com/t019df0d1d12f4f82dc.png)

继续跟进，调用了getHostAdress方法

[![](https://p4.ssl.qhimg.com/t010a1b398700f0751d.png)](https://p4.ssl.qhimg.com/t010a1b398700f0751d.png)

来看一下getHostAdress是如何实现的，观察逻辑，这里会先后调用`getHost()`、`getByName()`两个方法，最终是通过`getByName(getHost())`这样去发送的dnslog请求

[![](https://p5.ssl.qhimg.com/t018520c4500899302d.png)](https://p5.ssl.qhimg.com/t018520c4500899302d.png)

[![](https://p4.ssl.qhimg.com/t01e5df0f31f7953520.png)](https://p4.ssl.qhimg.com/t01e5df0f31f7953520.png)

到了这里，dnslog就已经可以接收到请求信息了，致此这歌利用链差不多就分析完了。

整个调用链为

```
HashMap.readObject() =&gt; HashMap.putVal() =&gt; HashMap.hash() =&gt; URL.hashCode() =&gt; 
URLStreamHandler.hashCode() =&gt; URLStreamHandler.hashCode().getHostAddress =&gt; URLStreamHandler.hashCode().getHostAddress.InetAddress.getByName()
```



## 0x05 URLDNS链中的一些细节

回到URLDNS类，可以看到还有一些其他的点其实并没有去深入分析，比如下面这几段代码

```
...

URLStreamHandler handler = new SilentURLStreamHandler();

...

static class SilentURLStreamHandler extends URLStreamHandler `{`

                protected URLConnection openConnection(URL u) throws IOException `{`
                        return null;
                `}`

                protected synchronized InetAddress getHostAddress(URL u) `{`
                        return null;
                `}`
        `}`
...
Reflections.setFieldValue(u, "hashCode", -1);
```

这里new的是一个SilentURLStreamHandler对象，继承自URLStreamHandler并且重写了两个方法，分别是getHostAddress和openConnection且都是空方法，比较耐人寻味。

**关于重写getHostAddress方法与hashcode = -1**

Java中继承子类的同名方法会覆盖父类的方法，所以说本来是要执行URLStreamHandler中的getHostAddress方法会变成执行他的子类SilentURLStreamHandler的getHostAddress方法（也就是空方法）。因为在默认情况下hashcode的值就是-1，那么在本地进行将 URL 对象 put 进 hashMap时如果hashcode值为-1就直接调用了getHostAddress方法也就会在生成序列化payload的时候在本地发送一次dnslog请求，所以ysoserial中给出对应的解决方法就是让SilentURLStreamHandler继承URLStreamHandler并重写getHostAddress为空方法，这样即使hashcode为-1也不会在本地发送请求（继承子类的同名方法会覆盖父类的方法）

`Reflections.setFieldValue(u, "hashCode", -1);`最后通过反射将hashcode重新设置为-1，那么在反序列化过程就会触发dnslog请求

**关于handler**

在调试的时候其实就发现了一个特殊的关键字transient，不可序列化，也就是说handler最终不会在我们产生的序列化payload中，所以即便SilentURLStreamHandler重写了父类方法，也不会影响反序列化的过程

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018e3f8c5d8438bf60.png)

**关于重写openConnection方法**

这个就比较简单了，因为URLStreamHandler是一个抽象类，所以实现类必须实现父类的所有抽象方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01dc8d713fdb635acb.png)



## 0x06 结尾

根本原因还是在HashMap存在反序列化点并重写了readObject方法可以接受反序列化数据，之后因为hashcode=-1，通过putVal计算hash时一步步的调用直到调用getHostAddress方法，就会发起远程请求触发dnslog。整体下来其实并不算太复杂，只是需要耐心一点弄清楚逻辑和一些方法的作用就可以了

文章有分析的不对的地方还请师傅们指出

参考文章：

[https://www.secpulse.com/archives/157407.html](https://www.secpulse.com/archives/157407.html)

[https://www.cnblogs.com/nice0e3/p/13772184.html](https://www.cnblogs.com/nice0e3/p/13772184.html)

> 原文链接: https://www.anquanke.com//post/id/249677 


# Weblogic Coherence 组件漏洞总结分析


                                阅读量   
                                **32645**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01318923cbde68e2f2.png)](https://p2.ssl.qhimg.com/t01318923cbde68e2f2.png)



作者：白帽汇安全研究院[@kejaly ](https://github.com/kejaly)校对：白帽汇安全研究院[@r4v3zn](https://github.com/r4v3zn)

## 前言

Coherence 组件是 WebLogic 中的一个核心组件，内置在 WebLogic 中。关于 Coherence 组件的官方介绍：[https://www.oracle.com/cn/java/coherence/](https://www.oracle.com/cn/java/coherence/)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c8d431850486df44.png)

近些年，weblogic Coherence 组件反序列化漏洞被频繁爆出，苦于网上没有公开对 weblogic Coherence 组件历史反序列化漏洞的总结，导致很多想入门或者了解 weblogic Coherence 组件反序列化漏洞的朋友不知道该怎么下手，于是本文便对 weblogic Coherence 组件历史反序列化漏洞做出了一个总结和分析。

关于 Coherence 组件反序列化漏洞利用链的架构，我把他分为两个，一个是基于 `ValueExtractor.extract` 的利用链架构，另一个则是基于 `ExternalizableHelper` 的利用链架构。



## 前置知识

想理清 WebLogic 的 Coherence 组件历史反序列化漏洞需要首先了解一些 Coherence 组件反序列化漏洞中经常会涉及的一些接口和类。他们在 Coherence 组件反序列化漏洞利用中经常出现。

### <a class="reference-link" name="ValueExtractor"></a>ValueExtractor

`com.tangosol.util.ValueExtrator` 是一个接口：

[![](https://p4.ssl.qhimg.com/t01805c78c78ba18daf.png)](https://p4.ssl.qhimg.com/t01805c78c78ba18daf.png)

在 Coherence 中 很多名字以 `Extrator` 结尾的类都实现了这个接口：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011ae961e484947906.png)

这个接口中声明了一个 `extract` 方法，而 `ValueExtractor.extract` 正是 Coherence 组件历史漏洞（ `ValueExtractor.extract` 链部分 ）的关键。

### <a class="reference-link" name="ExternalizableLite"></a>ExternalizableLite

Coherence 组件中存在一个 `com.tangosol.io.ExternalizableLite`，它继承了 `java.io.Serializable`，另外声明了 `readExternal` 和 `writeExternal` 这两个方法。

[![](https://p5.ssl.qhimg.com/t01aeb40785cc0e18f8.png)](https://p5.ssl.qhimg.com/t01aeb40785cc0e18f8.png)

`com.tangosol.io.ExternalizableLite` 接口 和 jdk 原生的 `java.io.Externalizable` 很像，注意不要搞混了。

### <a class="reference-link" name="ExternalizableHelper"></a>ExternalizableHelper

上面提到的 `com.tangosol.io.ExternalizableLite` 接口的实现类的序列化和反序列化操作，都是通过 `ExternalizableHelper` 这个类来完成的。

我们可以具体看 `ExternalizableHelper` 这个类是怎么对实现 `com.tangosol.io.ExternalizableLite` 接口的类进行序列化和反序列化的，这里以 `readObject` 方法为例，`writeObject` 读者可自行去查看：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018d8767eb6e0db63c.png)

如果传入的`DataInput` 不是 `PofInputStream` 的话（Coherence 组件历史漏洞 涉及到的 `ExternalizableHelper.readObject` 传入的 `DataInput` 都不是 `PofInputStream`），`ExternalizableHelper#readObject` 中会调用 `ExternalizableHelper#readObjectInternal` 方法：

`readObjectInternal` 中会根据传入的中 `nType` 进行判断，进入不同的分支：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018e55752d144d03cb.png)

对于实现 `com.tangosol.io.ExternalizableLite` 接口的对象，会进入到 `readExternalizableLite` 方法：

[![](https://p1.ssl.qhimg.com/t013cef07956f42c206.png)](https://p1.ssl.qhimg.com/t013cef07956f42c206.png)

可以看到在 `readExternalizableLite` 中 1125 行会根据类名加载类，然后并且实例化出这个类的对象，然后调用它的 `readExternal()` 方法。



## 漏洞链

### <a class="reference-link" name="ValueExtractor.extract"></a>ValueExtractor.extract

我们在分析反序列化利用链的时候，可以把链分为四部分，一个是链头，一个是危险的中间的节点（漏洞点），另一个是调用危险中间节点的地方（触发点），最后一个则是利用这个节点去造成危害的链尾。

在 Coherence 组件 `ValueExtractor.extract` 利用链架构中，这个危险的中间节点就是 `ValueExtractor.extract` 方法。

**<a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E7%82%B9"></a>漏洞点**

<a class="reference-link" name="ReflectionExtractor"></a>**ReflectionExtractor**

`ReflectionExtractor` 中的 `extract` 方法含有对任意对象方法的反射调用：

[![](https://p5.ssl.qhimg.com/t01def8e725308ae3f3.png)](https://p5.ssl.qhimg.com/t01def8e725308ae3f3.png)

配合 `ChainedExtractor` 和 `ConstantExtractor` 可以实现类似 cc1 中的 `transform` 链的调用。

<a class="reference-link" name="%E6%B6%89%E5%8F%8A%20CVE"></a>**涉及 CVE**

CVE-2020-2555，CVE-2020-2883

**<a class="reference-link" name="MvelExtractor"></a>MvelExtractor**

`MvelExtrator` 中的 `extract` 方法，会执行任意一个 MVEL 表达式（RCE）：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01aae3d15ff100655d.png)

而在序列化和反序列化的时候 `m_sExpr` 会参与序列化和反序列化：

[![](https://p3.ssl.qhimg.com/t0110c1b9d2536e546d.png)](https://p3.ssl.qhimg.com/t0110c1b9d2536e546d.png)

所以 `m_xExpr` 可控，所以就导致可以利用 `MvelExtrator.extrator` 来达到执行任意命令的作用。

<a class="reference-link" name="%E6%B6%89%E5%8F%8A%20CVE"></a>**涉及 CVE**

CVE-2020-2883

<a class="reference-link" name="UniversalExtractor"></a>**UniversalExtractor**

`UniversalExtractor`（Weblogic 12.2.1.4.0 独有） 中的 `extract` 方法，可以调用任意类中的的 `get` 和 `is` 开头的无参方法，可以配合 `jdbsRowset`，利用 JDNI 来远程加载恶意类实现 RCE。

具体细节可以参考：[https://nosec.org/home/detail/4524.html](https://nosec.org/home/detail/4524.html)

<a class="reference-link" name="%E6%B6%89%E5%8F%8A%20CVE"></a>**涉及 CVE**

CVE-2020-14645，CVE-2020-14825 ， CVE-2020-14841

**<a class="reference-link" name="LockVersionExtractor"></a>LockVersionExtractor**

`oracle.eclipselink.coherence.integrated.internal.cache.LockVersionExtractor` 中的 `extract()` 方法，可以调用任意 `AttributeAccessor` 的 `getAttributeValueFromObject` 方法，赋值 `Accessor` 为 `MethodAttributeAccessor` 进而可以实现调用任意类的无参方法。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d5b93930a45dfb95.png)

[![](https://p3.ssl.qhimg.com/t0175ef2fdcf6a8c74f.png)](https://p3.ssl.qhimg.com/t0175ef2fdcf6a8c74f.png)

具体细节可参考：[https://cloud.tencent.com/developer/article/1740557](https://cloud.tencent.com/developer/article/1740557)

**`MethodAttributeAccessor.getAttributeValueFromObject`**，本质是利用`MethodAttributeAccessor.getAttributeValueFromObject`中存在任意无参方法调用，在 CVE-2021-2394 中也利用到了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01358242c4d90832bd.png)

<a class="reference-link" name="%E6%B6%89%E5%8F%8A%20CVE"></a>**涉及 CVE**

CVE-2020-14825 ， CVE-2020-14841

<a class="reference-link" name="FilterExtractor.extract"></a>**FilterExtractor.extract**

`filterExtractor.extract` 中存在任意 `AttributeAccessor.getAttributeValueFromObject(obj)` 的调用，赋值 this.attributeAccessor 为上面说的`MethodAttributeAccessor` 就可以导致任意无参方法的调用。

[![](https://p0.ssl.qhimg.com/t01e0e6a53882f67996.png)](https://p0.ssl.qhimg.com/t01e0e6a53882f67996.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0170beb3a39080e54d.png)

关于 `readAttributeAccessor` 的细节可以看 CVE-2021-2394：[https://blog.riskivy.com/weblogic-cve-2021-2394-rce%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/](https://blog.riskivy.com/weblogic-cve-2021-2394-rce%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/) 和 [https://www.cnblogs.com/potatsoSec/p/15062094.html](https://www.cnblogs.com/potatsoSec/p/15062094.html) 。

<a class="reference-link" name="%E6%B6%89%E5%8F%8A%20CVE"></a>**涉及 CVE**

CVE-2021-2394

**<a class="reference-link" name="%E8%A7%A6%E5%8F%91%E7%82%B9"></a>触发点**

上面例举出了很多危险的 `ValueExtractor.extract` 方法，接下来再看看哪里存在调用 `ValueExtractor.extract` 方法的地方。

<a class="reference-link" name="Limitfiler"></a>**Limitfiler**

Limitfiler 中 `Limitfiler.toString` 中存在任意 `ValueExtractor.extract` 方法调用：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01da2a208696d40ac6.png)

由于 `this.m_comparator` 参与序列化和反序列化，所以可控：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01293bc8ab58176167.png)

我们只需要赋值 `this.m_comparator` 为 恶意的 `ValueExtractor` 就可以实现任意 `ValueExtractor .extract` 方法的调用。`toString` 方法，则可以利用 CC5 中用到的 `BadAttributeValueExpException` 来触发。

<a class="reference-link" name="%E6%B6%89%E5%8F%8A%20CVE"></a>**涉及 CVE**

CVE-2020-2555

<a class="reference-link" name="ExtractorComparator"></a>**ExtractorComparator**

`ExtractorComparator.compare` ，其实是针对 CVE-2020-2555 补丁的绕过，CVE-2020-2555 的修复方法中修改了 `Limitfiler.toString` 方法，也就是说修改了一个调用 `ValueExtractor.extract` 方法的地方。 而 CVE-2020-2883 则找到另一个调用 `ValueExtractor.extract` 的地方，也就是 `ExtractorComparator.compare` 。

在`ExtratorComparator.compare` 中存在任意（因为 `this.m_extractor` 参与序列化和反序列化） `ValueExtractor` 的 `extract` 方法调用。

[![](https://p2.ssl.qhimg.com/t01138e2b1ace8b61d6.png)](https://p2.ssl.qhimg.com/t01138e2b1ace8b61d6.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c5b63584ac01d1ef.png)

`Comparator.compare 方法，则可以通过 CC2 中用到的`PriorityQueue.readObject` 来触发。

另外在 weblogic 中， `BadAttributeValueExpException.readObject` 中也可以实现调用任意 `compartor.compare`方法：

[![](https://p3.ssl.qhimg.com/t01462baa8d1805a4c1.png)](https://p3.ssl.qhimg.com/t01462baa8d1805a4c1.png)

<a class="reference-link" name="%E6%B6%89%E5%8F%8A%20CVE"></a>**涉及 CVE**

CVE-2020-2883，修复方法是将 `ReflectionExtractor` 和 `MvelExtractor` 加入了黑名单 。

CVE-2020-14645 使用 `com.tangosol.util.extractor.UniversalExtractor` 绕过，修复方法将 `UniversalExtractor` 加入黑名单。

CVE-2020-14825，CVE-2020-14841 使用 `oracle.eclipselink.coherence.integrated.internal.cache.LockVersionExtractor.LockVersionExtractor` 进行绕过。

### <a class="reference-link" name="ExternalizableHelper"></a>ExternalizableHelper

在分析`ExternalizableHelper` 利用链架构的时候，我们依然可以把链分为四部分，一个是链头，一个是危险的中间的节点（漏洞点），另一个是调用危险中间节点的地方（触发点），最后一个则是利用这个节点去造成危害的链尾。

在 `ExternalizableHelper` 利用链架构中，这个危险的中间节点就是 `ExternalizableLite.readExternal` 方法。

weblogic 对于反序列化类的过滤都是在加载类时进行的，因此在 `ExternalizableHelper.readExternalizableLite` 中加载的 class 是不受黑名单限制的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01682d32c7a410821f.png)

具体原因是：weblogic 黑名单是基于 jep 290 ，jep 290 是在 `readObject` 的时候，在得到类名后去检查要反序列化的类是否是黑名单中的类。而这里直接使用的 `loadClass` 去加载类，所以这里不受 weblogic 黑名单限制。（也可以这么理解： jep 290 是针对在反序列化的时候，通过对要加载类进行黑名单检查。而这里直接通过 `loadClass` 加载，并没有通过反序列化，和反序列化是两码事，当然在后续 `readExternal` 的时候还是受 weblogic 黑名单限制，因为走的是反序列化那一套）

weblogic 黑名单机制可以参考：[https://cert.360.cn/report/detail?id=c8eed4b36fe8b19c585a1817b5f10b9e，https://cert.360.cn/report/detail?id=0de94a3cd4c71debe397e2c1a036436f，https://www.freebuf.com/vuls/270372.html](https://cert.360.cn/report/detail?id=c8eed4b36fe8b19c585a1817b5f10b9e%EF%BC%8Chttps://cert.360.cn/report/detail?id=0de94a3cd4c71debe397e2c1a036436f%EF%BC%8Chttps://www.freebuf.com/vuls/270372.html)

**<a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E7%82%B9"></a>漏洞点**

<a class="reference-link" name="PartialResult"></a>**PartialResult**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015f92b1b08b1886e3.png)

`com.tangosol.util.aggregator.TopNAggregator.PartialResult` 的 `readExternal` 会触发任意 `compartor.compare` 方法。

大致原理：

```
在 182 行会把comparator 作为参数传入 TreeMap 的构造函数中。

然后186 行，会调用 this.add ,this.add 会调用 this.m_map.put 方法，也就是说调用了 TreeMap 的 put 方法，这就导致了 comparator.compare()的调用。
```

具体分析见：[https://mp.weixin.qq.com/s/E-4wjbKD-iSi0CEMegVmZQ](https://mp.weixin.qq.com/s/E-4wjbKD-iSi0CEMegVmZQ)

然后调用 `comparator.compare` 就可以接到 `ExtractorComparator.compare` 那里去了，从而实现 rce 。

<a class="reference-link" name="%E6%B6%89%E5%8F%8A%20CVE"></a>**涉及 CVE**

<a class="reference-link" name="CVE-2020-14756%20%EF%BC%881%E6%9C%88%EF%BC%89"></a>**CVE-2020-14756 （1月）**

`ExternalizableHelper` 的利用第一次出现是在 CVE-2020-14756 中。利用的正是 `ExternalizableHelper` 的反序列化通过 `loadClass` 加载类，所以不受 weblogic 之前设置的黑名单的限制。具体利用可以参考：[https://mp.weixin.qq.com/s/E-4wjbKD-iSi0CEMegVmZQ](https://mp.weixin.qq.com/s/E-4wjbKD-iSi0CEMegVmZQ)

CVE-2020-14756 的修复方法则是对 `readExternalizable` 方法传入的 `Datainput` 检查，如果是 `ObjectInputStream` 就调用 checkObjectInputFilter() 进行检查，`checkObjectInputFilter` 具体是通过 jep290 来检查的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a99a6955c1982014.png)

<a class="reference-link" name="CVE-2021-2135%20%EF%BC%884%E6%9C%88%EF%BC%89"></a>**CVE-2021-2135 （4月）**

上面补丁的修复方案 只是检查了 `DataInput` 为 `ObjectInputStream` 的情况, 却没有过滤其他 `DataInput` 类型 。

那我们只需要找其他调用 `readExternalizableit` 函数的地方,并且传入的参数不是 `ObjectInputStream` 就可以了。【`ObjectInputStream` 一般是最常见的,通常来说是 `readObject` =&gt;`readObjectInternal` =&gt;`readExternalizableite` 这种链,也就是上游是常见的 `readObject`, 所以补丁就可能只注意到ObjectInputStream 的情况。】

所以CVE-2021-2135 绕过的方法就是设置传入 `readExternalizableite` 函数的参数类型为 `BufferInput` 来进行绕过。

`ExternalizableHelper` 中调用 `readObjectInternal` 的地方有两处,一处是 `readObjectInternal` , 另一处则是 `deserializeInternal` 。而 deserializeInternal 会先把 `DataInput` 转化为 `BufferInut` ：

[![](https://p5.ssl.qhimg.com/t018d68e59cafe4100d.png)](https://p5.ssl.qhimg.com/t018d68e59cafe4100d.png)

所以只要找调用 `ExternalizableHelper .deserializeInternal` 的地方。

而 `ExternalizableHelper.fromBinary` （和 `ExternalizableHelper.readObject` 平级的关系 ）里就调用了 `deserializeInternal` , 所以只需要找到一个地方用 来 `ExternalizableHelper.fromBinary` 来反序列化就可以接上后面的（CVE-2020-14756）利用链了。

然后就是找 调用了 `ExternalizableHelper.fromBinary` 的方法的地方。`SimpleBinaryEntry` 中的 `getKey` 和 `getValue`方法中存在 `ExternalizableHelper.fromBinary` 的调用，所以就只要找到调用 `getKey` 和 `getValue` 的地方就可以了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b7f1b60240064297.png)

然后在 `com.sun.org.apache.xpath.internal.objects.XString`重写的`equals`方法里调用了 `tostring` ，在 `tostring` 中调用了 `getKey` 方法。

`ExternalizableHelper#readMap` 中会调用 `map.put` ，`map.put` 会调用 `equals` 方法。

`com.tangosol.util.processor.ConditionalPutAll` 的 `readExteranl` 中调用了 `ExternalizableHelper#readMap` 方法。

然后再套上 `AttributeHolder` 链头就可以了。

具体可以参考：[https://mp.weixin.qq.com/s/eyZfAPivCkMbNCfukngpzg](https://mp.weixin.qq.com/s/eyZfAPivCkMbNCfukngpzg)

[![](https://p5.ssl.qhimg.com/t01b52116d9b46a6a4a.png)](https://p5.ssl.qhimg.com/t01b52116d9b46a6a4a.png)

4月漏洞修复则是：

1.添加`simpleBianry` 到黑名单。

2.设置了白名单：

[![](https://p5.ssl.qhimg.com/t01f9667b68afcbf391.png)](https://p5.ssl.qhimg.com/t01f9667b68afcbf391.png)

```
private static final Class[] ABBREV_CLASSES = new Class[]`{`String.class, ServiceContext.class, ClassTableEntry.class, JVMID.class, AuthenticatedUser.class, RuntimeMethodDescriptor.class, Immutable.class`}`;
```

#### <a class="reference-link" name="filterExtractor"></a>filterExtractor

`filterExtractor.reaExternal` 方法中的 `readAttributeAccessor()` 方法会直接 `new` 一个 `MethodAttributeAccessor` 对象。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e7aaa24237efb469.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014e5506b1108f29f5.png)

随后在 `filterExtractor.extract` 函数中会因为调用 `this.attributeAccessor.getAttributeValueFromObject` 进而导致任意无参方法的调用。

[![](https://p2.ssl.qhimg.com/t0150237d13c1bab8bc.png)](https://p2.ssl.qhimg.com/t0150237d13c1bab8bc.png)

<a class="reference-link" name="%E6%B6%89%E5%8F%8A%20CVE"></a>**涉及 CVE**

<a class="reference-link" name="CVE-2021-2394%20%EF%BC%884%E6%9C%88%EF%BC%89"></a>**CVE-2021-2394 （4月）**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b1e914eb7f423b5f.png)

在4月的补丁中，对 ois 的 `DataInput` 流进行了过滤，所以直接通过 `newInstance` 实例化恶意类的方式已经被阻止（CVE-2021-2135 通过 `bufferinputStream` 进行了绕过），所以需要重新寻找其他不在黑名单中的 `readExternal` 方法。

CVE-2021-2394 中就是利用 `filterExtractor.readExternal` 来进行突破。

具体可以参考：[https://blog.riskivy.com/weblogic-cve-2021-2394-rce%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/](https://blog.riskivy.com/weblogic-cve-2021-2394-rce%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/) 和 [https://www.cnblogs.com/potatsoSec/p/15062094.html](https://www.cnblogs.com/potatsoSec/p/15062094.html)

**<a class="reference-link" name="%E8%A7%A6%E5%8F%91%E7%82%B9"></a>触发点**

`ExternalizableHelper.readExternal` 的触发点有 `ExternalizableHelper.readObject` 和 `ExternalizableHelper.fromBinary` 这两个。其中 CVE-2021-2135 则就是因为在 CVE-2020-14756 的修复方法中，只注意到了 `ExternalizableHelper.readObject` ，只在`ExternalizableHelper.readObject` 里面做了限制，但是没有考虑到 `ExternalizableHelper.fromBinary` 从而导致了绕过。

`ExternalizableHelper.readObject`可以利用 `com.tangosol.coherence.servlet.AttributeHolder`来触发，`com.tangosol.coherence.servlet.AttributeHolder` 实现了 `java.io.Externalizabe` 接口，并且他的`readExternal` 方法 调用了 `ExternalizableHelper.readObject(in)` 。

[![](https://p3.ssl.qhimg.com/t013db16b5248118225.png)](https://p3.ssl.qhimg.com/t013db16b5248118225.png)

`ExternalizableHelper.fromBinary` 的触发则较为复杂一些，具体可以参考：[https://mp.weixin.qq.com/s/eyZfAPivCkMbNCfukngpzg](https://mp.weixin.qq.com/s/eyZfAPivCkMbNCfukngpzg)



## 后记

weblogic Coherence 反序列化漏洞很多都是相关联的，对于某个漏洞，很可能就是用到了之前一些漏洞的链子。其实不仅仅 weblogic ，java 其他反序列化链也是如此，很多情况都是一个链会用到其他链的一部分。所以在学习中，把一个组件或者一个库的漏洞总结起来一起分析还是比较重要的，最后希望这篇文章能帮助到其他一起学反序列化的朋友们。



## 参考

[https://nosec.org/home/detail/4524.html](https://nosec.org/home/detail/4524.html)

[https://cloud.tencent.com/developer/article/1740557](https://cloud.tencent.com/developer/article/1740557)

[https://blog.riskivy.com/weblogic-cve-2021-2394-rce%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/](https://blog.riskivy.com/weblogic-cve-2021-2394-rce%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90/)

[https://www.cnblogs.com/potatsoSec/p/15062094.html](https://www.cnblogs.com/potatsoSec/p/15062094.html)

[https://cert.360.cn/report/detail?id=c8eed4b36fe8b19c585a1817b5f10b9e](https://cert.360.cn/report/detail?id=c8eed4b36fe8b19c585a1817b5f10b9e)

[https://cert.360.cn/report/detail?id=0de94a3cd4c71debe397e2c1a036436f](https://cert.360.cn/report/detail?id=0de94a3cd4c71debe397e2c1a036436f)

[https://www.freebuf.com/vuls/270372.html](https://www.freebuf.com/vuls/270372.html)

[https://mp.weixin.qq.com/s/E-4wjbKD-iSi0CEMegVmZQ](https://mp.weixin.qq.com/s/E-4wjbKD-iSi0CEMegVmZQ)

[https://mp.weixin.qq.com/s/eyZfAPivCkMbNCfukngpzg](https://mp.weixin.qq.com/s/eyZfAPivCkMbNCfukngpzg)

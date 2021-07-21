> 原文链接: https://www.anquanke.com//post/id/172198 


# jenkins 2.101 XStream rce 挖掘思路


                                阅读量   
                                **219959**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t011997046faf626cf2.png)](https://p3.ssl.qhimg.com/t011997046faf626cf2.png)



## 前言

<a name="_Hlk387133"></a>这是一个未公开的利用思路，仅仅做技术思路分享

现在大多数 java 程序或者框架，都对反序列化漏洞有一定的防范措施，这篇文章主要是想要分享在黑名单限制非常严格的情况下，如何拿到一个反序列化的 rce

在以前开始学习 java 反序列化漏洞的时候，着重分析过 rmi 相关这类利用手法，因为自己搭建环境贼麻烦，还需要服务器进行一个外部资源请求（当然可以不用，也可以直接在服务器上新开一个端口接受攻击端的下一利用环节，但是成功率不高），所以就比较讨厌需要依赖 rmi、 ldap、 jndi 之类的触发链

目标：不依赖加载远程类的方式拿到 Jenkins 反序列化 rce，一发入魂

先去看看它的黑名单



## 反序列化黑名单

这是从 Jenkins 2.101 版本中取到的

```
"^bsh[.].*",

"^com[.]google[.]inject[.].*",

"^com[.]mchange[.]v2[.]c3p0[.].*",

"^com[.]sun[.]jndi[.].*",

"^com[.]sun[.]corba[.].*",

"^com[.]sun[.]javafx[.].*",

"^com[.]sun[.]org[.]apache[.]regex[.]internal[.].*",

"^java[.]awt[.].*",

"^java[.]lang[.]reflect[.]Method$",

"^java[.]rmi[.].*",

"^javax[.]management[.].*",

"^javax[.]naming[.].*",

"^javax[.]script[.].*",

"^javax[.]swing[.].*",

"^net[.]sf[.]json[.].*",

"^org[.]apache[.]commons[.]beanutils[.].*",

"^org[.]apache[.]commons[.]collections[.]functors[.].*",

"^org[.]apache[.]myfaces[.].*",

"^org[.]apache[.]wicket[.].*",

".*org[.]apache[.]xalan.*",

"^org[.]codehaus[.]groovy[.]runtime[.].*",

"^org[.]hibernate[.].*",

"^org[.]python[.].*",

"^org[.]springframework[.](?!(\\p`{`Alnum`}`+[.])*\\p`{`Alnum`}`*Exception$).*",

"^sun[.]rmi[.].*",

"^javax[.]imageio[.].*",

"^java[.]util[.]ServiceLoader$",

"^java[.]net[.]URLClassLoader$",

"^java[.]security[.]SignedObject$
```



对反序列化稍有研究的大佬们应该就明白，这个黑名单拦截的还是比较全的，直接将 package 拦截，或者定点拦截一些组合触发链关键点，比如 net.sf.json 、javax.rmi 等等，此类都是不能直接利用反序列化进行命令执行，json 可以调用 getter 和 setter 、 rmi 可以加载远程类等。虽然还有很多其他三方包有类似功能的，但是并没有在 Jenkins 中使用，当然插件自身依赖的包我们就不讨论了，总的来说，这个反序列化的黑名单对于 Jenkins 本身来说已经很安全了。



## 反序列化 != readObject

基于jdk支持的序列化方式有两大限制：

1. 继承关系

2. 反序列化实现过程

继承关系就是，需要实现 Serializable 或 Externalizable ，实现过程就主要看 readObject 和readExternal 的函数具体流程了

其中第一个继承关系的限制呢，从另一个角度来说，也是方便了exp利用链的构造，因为整个序列化和反序列化的过程，自己不用关心，仅仅需要从反序列化实现过程开始寻找利用点

但是 Jenkins 的反序列化黑名单有点过于严格，还需要考虑黑名单的问题，就使得这整个利用链的构造难上加难，已知的利用链已经全不能用了

于此同时我一直在搜索 Jenkins rce 相关信息，了解到 Jenkins 使用 XStream 对 xml 进行反序列化，稍微查询了下 XStream 的相关功效，发现和 json 相关的序列化工具差不多，不过解析的是 xml 而不是 json，同时有了一个好处，它不用再去实现 Serializable 和 Externalizable 这俩接口，可以一定程度的实现任意类的序列化与反序列化

那么利用链的构造情况就会发生变化，主要瞄准 XStream 相关的反序列化利用方式，除了一些最古老的利用方式（已经被XStream所修补），就只剩下 java.util.PriorityQueue 和 HashMap 这俩了（当然会有其他的，我见识少就只找到这两个2333）

不过在已知的 java.util.PriorityQueue 这个入口利用方式上，还是走的 ldap 过去加载远程类，利用链已经被黑名单毙掉了……（可能有其他利用姿势，我没有去深入研究）



## 分析下 HashMap 的利用

目前来说，走反序列化路线，jdk原生序列化功能pass调，jenkins 剩下 XStream 可以利用，其中我们也得到了一个 HashMap 这个入口点

不熟悉 HashMap 利用方式的大哥们（其实和其他的 Map 类差不多一个意思，只是 XStream 里好像对 map 默认是 HashMap 操作的），我可以先稍微解释下。

主要是用到了 map 结构存储的时候，对各个键值对进行 key 的一个比较（可以理解为比较 key 的重复性），在比较的过程中，就调用了 equals 函数

这个 equals 函数还是有点讲究的，各种类中只要实现了这个函数的，一般是要做类型对比，或者是一些计算对比结果，那么在这个对比中就会存在其他利用点的地方（因为存在了其他的函数调用）。与此同时，toString 和 hashCode 这两个函数的实现对利用链能否构造成功来说也有很大的关系，因为在调用 equals 之前，map 中首先会调用 key 的 hashCode 函数，然后通过计算与 map 中已经存储的 key 值作比较，在两者的计算结果相等的时候，才会调用 **key2.equals( key1 )** 。 一般来说， hashCode 这个函数返回的都是当前对象在 jvm 中堆上的内存地址，除非重写 hashCode 函数实现，但是有个例外，就是 String 类型的 hashCode，它可以满足这个不同 jvm 返回值相同的条件，不过具体的我没太过深入。

那么一个对象 和 String 这个类挂钩最多的就是，toString 函数

所以 hashCode 、 toString 、 equals 这三者纠缠不清2333

千万不要以为，非得是先 map 中触发 hashCode ，两个 key 的 hash 相等，然后触发 equals ，最后触发 toString 的。这期间很复杂，可能在这三个函数中嵌套利用，跳过去跳过来的，因为他们三个函数太常见了，并且在反序列化流程中不止一次会被调用到



## 一个新思路

从上文中能够总结出，尽量找 jdk、jre 中的触发链，尽量不利用ldap、rmi这类需要进行外部资源请求的利用点，最后依靠 XStream 的反序列化能力搞事

在 freebuf 上看过一个 java 相关的代码执行利用思路

DefineClass：[https://www.freebuf.com/articles/others-articles/167932.html](https://www.freebuf.com/articles/others-articles/167932.html)

这篇文章中，对 BCEL 的利用让我长见识了，转念一想，这个过程其实和反序列化的核心思路也是一样的，用户掌控了程序的执行方向。Class.forName 这种调用在 jdk 、 jre 中并不少见，况且 bcel 相关没有被写入黑名单中

bcelClassLoader 可以解析经过 bcel 编码过的字符串并加载指定类，如果 Class.forName 中的第二位参数为 true ，就支持加载类的初始化，类的初始化涉及到 static 代码块的执行，我们就可以在其中搞事情2333

我就在思考如何利用 XStream + Class.forName 这两个结合起来搞事情…..

终于找到了一个类：com.sun.xml.internal.ws.util.ServiceFinder$LazyIterator

其中的 next 函数如下：

[![](https://p5.ssl.qhimg.com/t0111debdc4a732be6f.png)](https://p5.ssl.qhimg.com/t0111debdc4a732be6f.png)

如上图红框里，就是调用了 Class.forName 并且第二个代表初始化参数值为 true，并且传入的 cn 和 this.loader 参数都是在反序列化过程中可控的。同时呢，Iterator 这种类别在 java 中特别常见，迭代器的身份也使得 next 函数被调用的概率非常大



## 触发链

首先经过的是 XStream 可设置的黑/白名单

1.4.7 版本以后 allowTypes 和 Permission 都是白名单过滤，denyTypes 是黑名单过滤

而 Jenkins 使用的方法是设置 converter 的优先级，可以达到黑名单过滤的作用，可能是功能点太多，设置白名单不太合适，最终还是选择设置的黑名单

绕过黑名单

-&gt;

jdk.nashorn.internal.objects.NativeString#hashCode

-&gt;

com.sun.xml.internal.bind.v2.runtime.unmarshaller.Base64Data#toString

-&gt;

javax.crypto.CipherInputStream#read

-&gt;

Javax.crypto.Cipher#chooseFirstProvider

-&gt;

com.sun.xml.internal.ws.util.ServiceFinder$LazyIterator#next

-&gt;

Java.lang.Class#forName

-&gt;

com.sun.org.apache.bcel.internal.util.ClassLoader#loadClass

最后就是初始化动态加载类，然后执行恶意类的 static 代码块造成了任意代码执行



## 效果

虽然有交互过程，也需要一定的低权限，可是还是可以一发入魂啊

[![](https://p5.ssl.qhimg.com/t019ce3fca6c9b2259d.png)](https://p5.ssl.qhimg.com/t019ce3fca6c9b2259d.png)



## 总结

反序列化漏洞一直都存在，不过自从15年公开了通用利用链至今，各大流行第三方依赖、流行软件甚至oracle官方都在想尽办法修补漏洞或者提高漏洞利用难度

此时想要在主流软件上挖掘java反序列化rce漏洞，需要更有耐心的去理解程序设计，更细心的去对各种依赖进行审查

这篇文章中就是利用了 Jenkins 使用了 XStream 为突破口，学习到了 loadClass 动态加载类的新思路，两者结合起来，巧妙的躲开了 Jenkins 非常严格的反序列化黑名单过滤



## 链接

[https://www.freebuf.com/articles/others-articles/167932.html](https://www.freebuf.com/articles/others-articles/167932.html)

[https://www.freebuf.com/vuls/97659.html](https://www.freebuf.com/vuls/97659.html)

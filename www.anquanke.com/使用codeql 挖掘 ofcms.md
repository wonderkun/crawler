> 原文链接: https://www.anquanke.com//post/id/203674 


# 使用codeql 挖掘 ofcms


                                阅读量   
                                **414148**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0173332a2f4e077a59.png)](https://p5.ssl.qhimg.com/t0173332a2f4e077a59.png)



## 前言

网上关于codeql的文章并不多，国内现在对codeql的研究相对比较少，可能是因为codeql暂时没有中文文档，资料也相对较少，需要比较好的英语功底，但是我认为在随着代码量越来越多，传统的自动化漏洞挖掘工具的瓶颈无法突破的情况下，codeql相当于是一种折中的办法，通过codeql的辅助，来减少漏洞挖掘人员的工作，更加关注漏洞的发现和利用过程

之所以选ofcms，是因为有p0desta师傅之前的审计经验，而且使用codeql审计cms尚属第一次，所以选用了ofcms审计



## ql构造

在ql中，漏洞挖掘是根据污点追踪进行的，所以我们需要知道我们的挖掘的cms的source点在哪里，sink点在哪里，相对来说，source点比较固定，一般就是http的请求参数，请求头这一类的

但是sink比较难以确定，由于现在的web应用经常使用框架，有些文件读取，html输出其实是背后的框架在做，所以这就导致了我们的sink定义不可能是一成不变的，要对整个web应用有一个大致的了解，才能定义对应的sink

### <a class="reference-link" name="source%E7%82%B9%E7%9A%84ql"></a>source点的ql

source点很清楚，对于一个web应用来说，http请求参数，http请求头，我们关注ofcms中对请求参数的获取方式：

ofcms使用了jfinal这个框架，而ofcms继承了jfinal的controller来获取参数，在整个ofcms中大体有三种类型来获取请求参数：
<li>BaseController[![](https://p1.ssl.qhimg.com/t01e6b14703898d1896.png)](https://p1.ssl.qhimg.com/t01e6b14703898d1896.png)
</li>
<li>Controller(Jfinal提供)[![](https://p4.ssl.qhimg.com/t0172a436770d7108a6.png)](https://p4.ssl.qhimg.com/t0172a436770d7108a6.png)
</li>
<li>ApiBase[![](https://p4.ssl.qhimg.com/t0154a24b149774f017.png)](https://p4.ssl.qhimg.com/t0154a24b149774f017.png)
</li>
所以我们的source都是根据这几个类展开的，在观察这几个类之后很容易发现，所有的获取http参数的方法都是getXXX()这样的命名方式，所以我们可以这样定义source的ql语法：

```
class OfCmsSource extends MethodAccess`{`
    OfCmsSource()`{`
        (this.getMethod().getDeclaringType*().hasQualifiedName("com.ofsoft.cms.admin.controller", "BaseController") and
        (this.getMethod().getName().substring(0, 3) = "get"))
        or 
        (this.getMethod().getDeclaringType*().hasQualifiedName("com.jfinal.core", "Controller") and
        (this.getMethod().getName().substring(0, 3) = "get"))
        or 
        (this.getMethod().getDeclaringType*().hasQualifiedName("javax.servlet.http", "HttpServletRequest") and (this.getMethod().getName().substring(0, 3) = "get"))
        or
        (this.getMethod().getDeclaringType*().hasQualifiedName("com.ofsoft.cms.api", "ApiBase") and
        (this.getMethod().getName().substring(0, 3) = "get"))
    `}`
`}`
```

到这一步，我们的source就算定义完了，接下来就是定义对应的sink了

### <a class="reference-link" name="sink%E7%82%B9%E7%9A%84ql"></a>sink点的ql

相对于source的固定，sink就很不固定了，常见的web漏洞一般来说都可以作为sink，而且因为框架的不同，同一种漏洞在不同框架下的ql都是不一样的，所以我们需要略微分析一下整个web应用在做文件读取，模版渲染等操作的时候一般都用的是什么方法

#### <a class="reference-link" name="%E6%A8%A1%E7%89%88%E6%B8%B2%E6%9F%93%E7%9A%84%E9%97%AE%E9%A2%98"></a>模版渲染的问题

Jfinal中对模版渲染有一系列的render方法：

[![](https://p3.ssl.qhimg.com/t0162db45a4c209c771.png)](https://p3.ssl.qhimg.com/t0162db45a4c209c771.png)

可以看到，所有都是render开头，所以我们对方法名的判断很简单，截取前面6个字符，判断是否为render，随便找一个项目使用render的地方，可以发现render其实是在com.jfinal.core.Controller里面定义的方法，所以现在我们唯一确定了模版渲染的方法，所以我们的sink也就呼之欲出了，也就是这些render方法的参数，所以构造ql：

```
class RenderMethod extends MethodAccess`{`
    RenderMethod()`{`
        (this.getMethod().getDeclaringType*().hasQualifiedName("com.jfinal.core", "Controller") and 
        this.getMethod().getName().substring(0, 6) = "render") or (this.getMethod().getDeclaringType*().hasQualifiedName("com.ofsoft.cms.core.plugin.freemarker", "TempleteUtile") and this.getMethod().hasName("process"))
    `}`
`}`
```

在上面的ql中我添加了TempleteUtile这个类，因为这个类的process第一个参数可控的话也会造成模版的问题，所以我们可以随时去到ql中添加我们认为可能出现问题的模版渲染方法

#### <a class="reference-link" name="%E6%96%87%E4%BB%B6%E7%B1%BB%E7%9A%84%E9%97%AE%E9%A2%98"></a>文件类的问题

在ofcms中，文件的创建一般都是new File()这种形式创建的，所以我们的sink点应该为new File的参数为我们的sink点，所以构造ql：

```
class FileContruct extends ClassInstanceExpr`{`
    FileContruct()`{`
        this.getConstructor().getDeclaringType*().hasQualifiedName("java.io", "File")
    `}`
`}`
```

### <a class="reference-link" name="%E6%B1%A1%E7%82%B9%E8%BF%BD%E8%B8%AA"></a>污点追踪

codeql提供了几种数据流的查询：
1. local data flow
1. local taint data flow
1. global data flow
1. global taint data flow
local data flow基本是用在一个方法中的，比如想要知道一个方法的入参是否可以进入到某一个方法，就可以用local data flow

global data flow是用在整个项目的，也是我们做污点追踪用的最多的

简单解释一下taint和非taint有什么区别：taint的dataflow会在数据流分析的基础上加上污点分析，比如

```
String a = "evil";
String b = a + a;
```

在使用taint的dataflow中，b也会被标记为被污染的变量

#### <a class="reference-link" name="%E6%9E%84%E9%80%A0configure"></a>构造configure

```
class OfCmsTaint extends TaintTracking::Configuration`{`
    OfCmsTaint()`{`
        this = "OfCmsTaint"
    `}`

    override predicate isSource(DataFlow::Node source)`{`
        source.asExpr() instanceof OfCmsSource
    `}`

    override predicate isSink(DataFlow::Node sink)`{`
        exists(
            FileContruct rawOutput |
            sink.asExpr() = rawOutput.getAnArgument()
        )
    `}`
`}`
```

当我们需要去做污点分析的时候，我们需要继承TaintTracking::Configuration这个类，来重写两个方法isSource和isSink，在这里，dataflow中的Node节点和我们直接使用的节点是不一样的，我们需要使用asExpr或者asParamter来将其转换为语法节点

这里可以看到，我们的source为我们之前定义的http参数的输入地方，sink为我们之前定义的new File的这种实例化



## 结果分析

codeql只能给出从source到sink的一条路径，但是这条路径中的一些过滤和条件是无法被判断的，这也就需要一部分的人工成本，让我们来运行一下我们刚刚写的ql：

```
import ofcms

from DataFlow::Node source, DataFlow::Node sink, OfCmsTaint config
where config.hasFlow(source, sink)
select source, sink
```

最后的查询结果：

[![](https://p0.ssl.qhimg.com/t01d693ffca9df95786.png)](https://p0.ssl.qhimg.com/t01d693ffca9df95786.png)

可以看到找到了11个可能存在问题的地方，我们来依次看一看是否有问题：

### <a class="reference-link" name="ReprotAction"></a>ReprotAction

第一个在ReprotAction这个类的expReport方法中：

[![](https://p0.ssl.qhimg.com/t01e31cc1991ae0ca7b.png)](https://p0.ssl.qhimg.com/t01e31cc1991ae0ca7b.png)

可以很明显看到，在获取j参数之后，对jrxmlFileName没有任何的校验，导致我们可以穿越到其他目录，但是文件后缀名必须为jrxml，而且在JasperCompileManager的compileReport函数中，对xml文档没有限制实体，导致可以造成XXE漏洞，这里很尴尬的利用点是：
1. 需要一个文件上传
1. 后缀名必须为jrxml
### <a class="reference-link" name="TemplateController"></a>TemplateController

在TemplateController这个类的getTemplates方法中：

[![](https://p0.ssl.qhimg.com/t01c073df990bf057f6.png)](https://p0.ssl.qhimg.com/t01c073df990bf057f6.png)

在这里对获取的参数没有任何的校验，导致可以跨越目录列文件并且修改文件，但是在后面的实现中，我们只能修改和查看特定的文件

[![](https://p2.ssl.qhimg.com/t01d711dc91348a0a97.png)](https://p2.ssl.qhimg.com/t01d711dc91348a0a97.png)

假设我们在tmp目录下有着a.html和a.xml文件，我们可以跨越到tmp目录下读取并修改这两个文件

[![](https://p2.ssl.qhimg.com/t01abe09393665d7d9c.png)](https://p2.ssl.qhimg.com/t01abe09393665d7d9c.png)

### <a class="reference-link" name="TemplateController"></a>TemplateController

还有一个地方就是save函数，这个函数在p0desta师傅的博客中也挖掘出了任意文件上传漏洞：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bdc7454537d8a8cd.png)

很明显的一任意文件上传，文件名，路径，文件内容全部可控，直接getshell

剩下的一个并不能造成影响，就不多说了



## 后记

在render的sink定义中，如果运行可以发现很多地方的前台的一个小问题，也就是我们可以指定模版文件，ofcms使用了freemarker模版引擎，如果可以包含到我们自定义的模版文件，即可导致RCE，但是并没有发现有一个文件上传的点可以上传文件到模版目录下（除了上面的一个任意文件上传），所以不太好前台RCE

顺手测了下发现前台评论地方有存储XSS，但是和codeql无关就不多说了

整个ql：

ofcms.qll

```
import java
import semmle.code.java.dataflow.TaintTracking


class OfCmsSource extends MethodAccess`{`
    OfCmsSource()`{`
        (this.getMethod().getDeclaringType*().hasQualifiedName("com.ofsoft.cms.admin.controller", "BaseController") and
        (this.getMethod().getName().substring(0, 3) = "get"))
        or 
        (this.getMethod().getDeclaringType*().hasQualifiedName("com.jfinal.core", "Controller") and
        (this.getMethod().getName().substring(0, 3) = "get"))
        or 
        (this.getMethod().getDeclaringType*().hasQualifiedName("javax.servlet.http", "HttpServletRequest") and (this.getMethod().getName().substring(0, 3) = "get"))
        or
        (this.getMethod().getDeclaringType*().hasQualifiedName("com.ofsoft.cms.api", "ApiBase") and
        (this.getMethod().getName().substring(0, 3) = "get"))
    `}`
`}`

class RenderMethod extends MethodAccess`{`
    RenderMethod()`{`
        (this.getMethod().getDeclaringType*().hasQualifiedName("com.jfinal.core", "Controller") and 
        this.getMethod().getName().substring(0, 6) = "render") or (this.getMethod().getDeclaringType*().hasQualifiedName("com.ofsoft.cms.core.plugin.freemarker", "TempleteUtile") and this.getMethod().hasName("process"))
    `}`
`}`

class SqlMethod extends MethodAccess`{`
    SqlMethod()`{`
        this.getMethod().getDeclaringType*().hasQualifiedName("com.jfinal.plugin.activerecord", "Db")
    `}`
`}`

class FileContruct extends ClassInstanceExpr`{`
    FileContruct()`{`
        this.getConstructor().getDeclaringType*().hasQualifiedName("java.io", "File")
    `}`
`}`

class ServletOutput extends MethodAccess`{`
    ServletOutput()`{`
        this.getMethod().getDeclaringType*().hasQualifiedName("java.io", "PrintWriter")
    `}`
`}`

class OfCmsTaint extends TaintTracking::Configuration`{`
    OfCmsTaint()`{`
        this = "OfCmsTaint"
    `}`

    override predicate isSource(DataFlow::Node source)`{`
        source.asExpr() instanceof OfCmsSource
    `}`

    override predicate isSink(DataFlow::Node sink)`{`
        exists(
            FileContruct rawOutput |
            sink.asExpr() = rawOutput.getAnArgument()
        )
    `}`
`}`
```

test.ql

```
import ofcms

from DataFlow::Node source, DataFlow::Node sink, OfCmsTaint config
where config.hasFlow(source, sink)
select source, sink
```



## 不足
1. 感觉一个很大的问题是sink的定义，因为框架的变换以及一些开发者自己的工具类，以及一些漏洞可能根本不存在，导致sink的定义有时候挖不出来漏洞
1. 像p0desta师傅测的CSRF漏洞，暂时想不到有什么好的办法来定义sink，人工可能很好去看出来，但是不好用codeql语言定义这种漏洞
<li>太菜了，有个点的任意文件读取写不出来ql，2333[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f38b4ee71f850399.png)师傅们教教我
</li>
1. 感觉在定义的时候要尽量找共性，但是也不能找太深
参考文章：

[http://p0desta.com/2019/04/20/%E4%BB%8E%E9%9B%B6%E5%BC%80%E5%A7%8Bjava%E4%BB%A3%E7%A0%81%E5%AE%A1%E8%AE%A1%E7%B3%BB%E5%88%97(%E5%9B%9B)/](http://p0desta.com/2019/04/20/%E4%BB%8E%E9%9B%B6%E5%BC%80%E5%A7%8Bjava%E4%BB%A3%E7%A0%81%E5%AE%A1%E8%AE%A1%E7%B3%BB%E5%88%97(%E5%9B%9B)/)<br>[https://help.semmle.com/QL/learn-ql/java/ql-for-java.html](https://help.semmle.com/QL/learn-ql/java/ql-for-java.html)

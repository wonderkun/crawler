> 原文链接: https://www.anquanke.com//post/id/240202 


# Shiro 权限绕过的历史线（下）


                                阅读量   
                                **143554**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01e57ddfa6712a0795.png)](https://p4.ssl.qhimg.com/t01e57ddfa6712a0795.png)



## 0x5 CVE-2020-13933

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="0x5.1%20%E6%BC%8F%E6%B4%9E%E7%AE%80%E4%BB%8B"></a>0x5.1 漏洞简介

影响版本: shiro&lt;1.6.0

类型: 权限绕过

其他信息:

这个洞跟CVE-2020-11989有点相似的地方就是就是利用URL解码的差异性来实现绕过。

[CVE-2020-13933：Apache Shiro 权限绕过漏洞分析](https://www.anquanke.com/post/id/218270)

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="0x5.2%20%E6%BC%8F%E6%B4%9E%E9%85%8D%E7%BD%AE"></a>0x5.2 漏洞配置

这个洞是不会受到Spring的版本限制的。

```
&lt;dependency&gt;
            &lt;groupId&gt;org.apache.shiro&lt;/groupId&gt;
            &lt;artifactId&gt;shiro-web&lt;/artifactId&gt;
            &lt;version&gt;1.5.3&lt;/version&gt;
        &lt;/dependency&gt;
        &lt;dependency&gt;
            &lt;groupId&gt;org.apache.shiro&lt;/groupId&gt;
            &lt;artifactId&gt;shiro-spring&lt;/artifactId&gt;
            &lt;version&gt;1.5.3&lt;/version&gt;
        &lt;/dependency&gt;
```

Shiro配置,这个洞也是有限制的只能是ant的风格为单*号才可以:

```
map.put("/hello/*", "authc");
```

```
@ResponseBody
    @RequestMapping(value="/hello" +
            "" +
            "/`{`index`}`", method= RequestMethod.GET)
    public  String hello1(@PathVariable String index)`{`
        return "Hello World"+ index.toString() + "!";
    `}`
```

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="0x5.3%20%E6%BC%8F%E6%B4%9E%E6%BC%94%E7%A4%BA"></a>0x5.3 漏洞演示

[![](https://p4.ssl.qhimg.com/t01e94fdd4beda44245.png)](https://p4.ssl.qhimg.com/t01e94fdd4beda44245.png)

访问302，然后poc:

`/hello/%3bluanxie`

[![](https://p3.ssl.qhimg.com/t0153a2804e2bc19ca9.png)](https://p3.ssl.qhimg.com/t0153a2804e2bc19ca9.png)

看到这个POC的时候，我当时就觉得我前面分析两个洞的时候，是不是漏了什么关键点没去分析。

然后最让我头疼的的是，为什么需要对`;`要编码才能利用成功,下面我们通过分析来复盘我们前两次学习过程出现的问题。

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="0x5.4%20%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>0x5.4 漏洞分析

断点依然是在上一次的修补点:

```
org.apache.shiro.web.util.WebUtils#getPathWithinApplication
```

[![](https://p1.ssl.qhimg.com/t018e9f8c004bbcc780.png)](https://p1.ssl.qhimg.com/t018e9f8c004bbcc780.png)

这里我们逐步跟进去，上一次我没跟`removeSemicolon`, 因为从函数名这个其实就是Shiro一直以来的操作，就是去除`;`号后面的内容,然后`normalize`,这个并没有很大问题。

然后函数返回的结果是这个:

[![](https://p3.ssl.qhimg.com/t01fe88556262ef3263.png)](https://p3.ssl.qhimg.com/t01fe88556262ef3263.png)

本来应该获取到uri的是`/hello/`,然后因为最早的那个shiro-682的洞，所以会执行去掉末尾的斜杆。

```
if (requestURI != null &amp;&amp; !"/".equals(requestURI) &amp;&amp; requestURI.endsWith("/")) `{`
                requestURI = requestURI.substring(0, requestURI.length() - 1);
            `}`
```

变成了:`/hello`

首先通过，`Iterator var6 = filterChainManager.getChainNames().iterator()`获取了我们定义的filter，进入do循环逐个取值给`pathPattern`

[![](https://p1.ssl.qhimg.com/t01666aea7f7d5b2a6c.png)](https://p1.ssl.qhimg.com/t01666aea7f7d5b2a6c.png)

其实都没必要去看这个算法怎么做匹配的，因为`/hello/*`本来就不会匹配`/hello`,

那么这样,如果是这样呢,`map.put("/hello/", "authc");`,emm,在取出来进行匹配的时候，

[![](https://p0.ssl.qhimg.com/t01be4221354e2a68c5.png)](https://p0.ssl.qhimg.com/t01be4221354e2a68c5.png)

就会被去掉`/`,那么我来多几个呗。

```
map.put("/hello//", "authc");
```

稍微绕过了

[![](https://p4.ssl.qhimg.com/t011b6cd134ea5886e3.png)](https://p4.ssl.qhimg.com/t011b6cd134ea5886e3.png)

这个时候我们就可以回头去读一下Shiro的匹配算法了。

> 首先是如果`pattern`和`path`开头不一样直接false
然后就是`StringUtils.tokenizeToStringArray`分割字符串得到数组
然后一个循环，比较，如果出现某数组字符串不匹配，除开`**`就会返回`false`
只要没有`**`出现的话，且字符串数组=1，就没那么复杂的解析过程，直接返回
<pre><code class="lang-java hljs">pattern.endsWith(this.pathSeparator) ? path.endsWith(this.pathSeparator) : !path.endsWith(this.pathSeparator);
</code></pre>
如果pattern是以/结尾的话，那么是 True,返回`path.endsWith(this.pathSeparator)`,这个时候path不是以`/`结尾的，所以最终也不匹配。
如果是`/*`的话，字符串数组&gt;1,
那么最终会进入
[![](https://p4.ssl.qhimg.com/t01a8a45b9c8036f682.png)](https://p4.ssl.qhimg.com/t01a8a45b9c8036f682.png)
这个过程说明,`/hello/*` 可以匹配`/hello/`,但是没办法匹配到`/hello`,然后shiro又做了去除/处理，emmm，根本不可能构造出`/hello/`，构造出来也没啥可用的
但是如果是,`/hello/**`,这里就不返回false，直接跳到下面了，最终会返回True，没办法绕过。说明`/hello/**`可以匹配到`/hello`

其实来到这里我们就明白了，第一步通过`%3b`解码成`;`,然后以前的洞删掉了`/`,导致了bypass Shiro。

如果我们不用`%3b`,而是直接

[![](https://p4.ssl.qhimg.com/t0115eb11eb2fdd2d26.png)](https://p4.ssl.qhimg.com/t0115eb11eb2fdd2d26.png)

那么`;`直接会被`request.getServletPath()`处理掉，从而变成了`/hello/aa`,被`/hello/**`这种ant所匹配，导致第一层都没办法绕过。(这个其实就是cve2020-1957的绕过思路呀！肯定是没办法的呀)

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="0x5.5%20%E6%BC%8F%E6%B4%9E%E4%BF%AE%E5%A4%8D"></a>0x5.5 漏洞修复

说实话，关于这个洞，我当时思考的修复方式是，好像只能是去屏蔽%3b这个字符了，感觉真的很无奈。

diff:[https://github.com/apache/shiro/compare/shiro-root-1.5.3…shiro-root-1.6.0](https://github.com/apache/shiro/compare/shiro-root-1.5.3...shiro-root-1.6.0)

发现确实新增[InvalidRequestFilter.java](https://github.com/apache/shiro/compare/shiro-root-1.5.3...shiro-root-1.6.0#diff-bd4bf9dfa4cc7521c708850ac5d397fee22b021ea09a3a91f7ce1587abc287d7)，但是具体作用不知道在哪里起的，

[![](https://p1.ssl.qhimg.com/t01acae7a7cd0564e86.png)](https://p1.ssl.qhimg.com/t01acae7a7cd0564e86.png)

然后在这个文件被调用:

[support/spring/src/main/java/org/apache/shiro/spring/web/ShiroFilterFactoryBean.java](https://github.com/apache/shiro/compare/shiro-root-1.5.3...shiro-root-1.6.0#diff-c2ca6676fe2316741dba8f6005b165ad79d7c12d7e2d31f0c8883a55a03d77ff)

这个文件新增了一个`/**`匹配没有设置filter类型，用于解决失配的时候还是可以调用默认的过滤器

[![](https://p4.ssl.qhimg.com/t01faff974e455466c3.png)](https://p4.ssl.qhimg.com/t01faff974e455466c3.png)

然后输入特殊字符的时候，过滤器会进行过滤，关于是如何进行过滤的，值得详细写一篇文章，这里我们只要知道它的修复方式，是做了特殊字符，存在就抛出400就行了。

`return !this.containsSemicolon(uri) &amp;&amp; !this.containsBackslash(uri) &amp;&amp; !this.containsNonAsciiCharacters(uri);`

[![](https://p5.ssl.qhimg.com/t01fd0003f5a0ea3f73.png)](https://p5.ssl.qhimg.com/t01fd0003f5a0ea3f73.png)



## 0x6 CVE-2020-17510

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="0x6.1%20%E6%BC%8F%E6%B4%9E%E7%AE%80%E4%BB%8B"></a>0x6.1 漏洞简介

影响版本: shiro&lt;1.7.0

类型: 权限绕过

其他信息:

中风险，需结合Spring使用环境，危害偏低一点

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="0x6.5%20%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>0x6.5 漏洞分析

diff:[https://github.com/apache/shiro/compare/shiro-root-1.6.0…shiro-root-1.7.0](https://github.com/apache/shiro/compare/shiro-root-1.6.0...shiro-root-1.7.0)

改动:

[![](https://p3.ssl.qhimg.com/t01283f1e7985427d28.png)](https://p3.ssl.qhimg.com/t01283f1e7985427d28.png)

这个洞我发现他增加了`request.getPathInfo`的方式检测字符，而在Spring-boot默认这个值是空，但是在其他情况，这个值可控的话，我们可以在这里插入`;`和`..`实现绕过，结合前面的分析，可以知道URI是由`request.getServletPath + request.getPathInfo`得到的，所以是可以去绕过的，不过由于这个洞鲜少人讨论，作者也没去公开，这个利用方式研究价值很低，笔者对此没有很大兴趣，所以就没去折腾场景来利用， 欢迎其他师傅感兴趣地话继续研究。



## 0x7 CVE-2020-17523

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="0x7.1%20%E6%BC%8F%E6%B4%9E%E7%AE%80%E4%BB%8B"></a>0x7.1 漏洞简介

影响版本: shiro&lt;1.7.0

类型: 权限绕过

其他信息:当`Apache Shiro`与`Spring框架`结合使用时，在一定权限匹配规则下，攻击者可通过构造特殊的 HTTP 请求包绕过身份认证。

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="0x7.2%20%E6%BC%8F%E6%B4%9E%E9%85%8D%E7%BD%AE"></a>0x7.2 漏洞配置

```
&lt;dependency&gt;
            &lt;groupId&gt;org.apache.shiro&lt;/groupId&gt;
            &lt;artifactId&gt;shiro-web&lt;/artifactId&gt;
            &lt;version&gt;1.6.0&lt;/version&gt;
        &lt;/dependency&gt;
        &lt;dependency&gt;
            &lt;groupId&gt;org.apache.shiro&lt;/groupId&gt;
            &lt;artifactId&gt;shiro-spring&lt;/artifactId&gt;
            &lt;version&gt;1.6.0&lt;/version&gt;
        &lt;/dependency&gt;
```

这个漏洞我建议spring-boot用2.4.5的，这个版本默认会开启全路径匹配模式。

> 当Spring Boot版本在小于等于2.3.0.RELEASE的情况下，`alwaysUseFullPath`为默认值false，这会使得其获取ServletPath，所以在路由匹配时相当于会进行路径标准化包括对`%2e`解码以及处理跨目录，这可能导致身份验证绕过。而反过来由于高版本将`alwaysUseFullPath`自动配置成了true从而开启全路径，又可能导致一些安全问题

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="0x7.3%20%E6%BC%8F%E6%B4%9E%E6%BC%94%E7%A4%BA"></a>0x7.3 漏洞演示

通杀版本:`/hello/%20`

[![](https://p1.ssl.qhimg.com/t0176e2e47cd07ee91b.png)](https://p1.ssl.qhimg.com/t0176e2e47cd07ee91b.png)

高版本默认支持:`/hello/%2e/` 或者 `/hello/%2e`

[![](https://p4.ssl.qhimg.com/t01d817bfb1e12243d6.png)](https://p4.ssl.qhimg.com/t01d817bfb1e12243d6.png)

其实这个洞，基于之前的%3B实现绕过的思路，其实很容易想到去Fuzz下的，看看除了%3B是不是还有其他字符可以在Shiro中造成失配，而Spring-boot可以正常匹配的，都不用去分析具体代码的，就可以拿到的一个ByPass。

[![](https://p0.ssl.qhimg.com/t01faa04b22b983d6b0.png)](https://p0.ssl.qhimg.com/t01faa04b22b983d6b0.png)

但是这两种绕过方式其实非常不同的，出现在了两个不同地方的错误处理方式。

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="0x7.4%20%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>0x7.4 漏洞分析

**第一种绕过方式分析:**

断点打在`org.apache.shiro.web.util.WebUtils#getPathWithinApplication`

[![](https://p3.ssl.qhimg.com/t01f8fe4d2e584595b9.png)](https://p3.ssl.qhimg.com/t01f8fe4d2e584595b9.png)

这里处理结果和前面一样，解码了所以变成了空格。

[![](https://p5.ssl.qhimg.com/t019f05c8f51005aff1.png)](https://p5.ssl.qhimg.com/t019f05c8f51005aff1.png)

跟进这里看匹配，

[![](https://p1.ssl.qhimg.com/t01474285746f7c9b54.png)](https://p1.ssl.qhimg.com/t01474285746f7c9b54.png)

很明显，这里和上次分析结果是一样的，最终还是因为`*`返回了false，否则True。

那么为什么会这样呢？ 那为什么`/hello/aa`这样就不行呢? 其实就是`StringUtils.tokenizeToStringArray`没有正确分割字符串导致的？ %20 应该是被当做空字符了，导致分割的数组长度=1，就会进入那个return false.

[![](https://p3.ssl.qhimg.com/t01444ac62df7667482.png)](https://p3.ssl.qhimg.com/t01444ac62df7667482.png)

所以这里成功Bypass了Shiro的检测，最后让我们来看下Spring-boot是怎么处理的

断点:`org.springframework.web.servlet.DispatcherServlet#doDispatch`

逐步跟到:`org.springframework.web.servlet.handler.AbstractHandlerMethodMapping#lookupHandlerMethod`

[![](https://p3.ssl.qhimg.com/t01b11905726ab0b273.png)](https://p3.ssl.qhimg.com/t01b11905726ab0b273.png)

这里是根据`lookpath`进行匹配，没有直接被找到

[![](https://p2.ssl.qhimg.com/t0195d8fbe7323cd777.png)](https://p2.ssl.qhimg.com/t0195d8fbe7323cd777.png)

下面进入用`RequestMapping`注册的列表来匹配:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014e8aae53e9c63c24.png)

这里继续进入匹配:

[![](https://p4.ssl.qhimg.com/t01ca0c6d133fbd1217.png)](https://p4.ssl.qhimg.com/t01ca0c6d133fbd1217.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019e0308c0fd21c539.png)

[![](https://p2.ssl.qhimg.com/t0109213dbf24df6cf0.png)](https://p2.ssl.qhimg.com/t0109213dbf24df6cf0.png)

最终这个`org.springframework.util.AntPathMatcher#doMatch`进行了解析，和之前算法差不多，但是

`this.tokenizePath(path)`返回的结果是2包括%20,所以可以匹配成功,最终解析到了`/hello/`{`index`}``

[![](https://p3.ssl.qhimg.com/t01e637d431fdc6e3d4.png)](https://p3.ssl.qhimg.com/t01e637d431fdc6e3d4.png)

**第二种绕过方式分析:**

这个其实在分析cve-2020-13933的时候,我就考虑过这种方式去绕过(部分原理相同，利用默认去掉`/`造成的失配)，然后当时实践了，由于采取了低版本的spring-boot，默认没开启全路径匹配模式，导致我当时没成功。

首先说一下网上有些文章，分析的时候不够全面，但是又概括性总结了原因，有一定的误导，这里我列出我的debug结果

`/hello/%2e`-&gt;request.getServletPath()-&gt;`/hello/`

`/hello/%2e/`-&gt;request.getServletPath()-&gt;urldecode-&gt;`/helo/`

`/hello/%2e%2e` -&gt;request.getServletPath() -&gt; urldecode-&gt;`/`

也就是说，request.getServletPath()针对`%2e`会先解码，然后对此进行处理。

所以洞出现的问题是:

request.getServletPath() 处理这种URL时候会返回`/hello/`,然后shiro默认会去掉最后`/`,然后再进行匹配,导致了绕过。

### <a class="reference-link" style="background-image: url('img/anchor.gif');" name="0x7.5%20%E6%BC%8F%E6%B4%9E%E4%BF%AE%E5%A4%8D"></a>0x7.5 漏洞修复

diff:[https://github.com/apache/shiro/compare/shiro-root-1.7.0…shiro-root-1.7.1](https://github.com/apache/shiro/compare/shiro-root-1.7.0...shiro-root-1.7.1)

[![](https://p0.ssl.qhimg.com/t016846c6ca2e2c2774.png)](https://p0.ssl.qhimg.com/t016846c6ca2e2c2774.png)

这个处理就可以避免空白字符没被正确分割出来的问题,解决了第一种绕过问题。

[![](https://p3.ssl.qhimg.com/t0115f46bf16d19d42a.png)](https://p3.ssl.qhimg.com/t0115f46bf16d19d42a.png)

然后可以看到这里为了避免`%2e`,这里首先去掉了之前shiro-682,为了修补末尾`/`绕过问题，做的一个去掉默认路径`/`的操作。

然后后面写了个if/else的判断

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0146c55f6ecbd21f5b.png)

先不去掉`/`来做匹配，如果匹配失败，在考虑去掉`/`,这样考虑是基于以前的问题和现在的问题共同考虑

首先以前是 `/hello`被`/hello/`实现了绕过,那么在做匹配的时候，那么第一次匹配失败，然后进入了第二个去掉`/`匹配成功

现在是`/hello/*`被先`/hello/`默认去掉`/`-&gt;`/hello`实现了绕过，那么在做匹配的时候，第一次先保留`/hello/`可以成功被`/hello/*`匹配。



## 0x8 总结

漏洞的最基本原理，通俗来说就是，一个原始恶意构造地URL ，首先要绕过Shiro的判断，然后被Spring解析到最终的函数，也就是Shiro解析URL和Spring解析URL的差异性。然后多次Bypass都是针对实现解析的环节存在一些问题导致。

行文颇长，若有不当之处，多多包涵。



## 0x9 参考链接

[Spring源码分析之WebMVC](https://www.jianshu.com/p/1136212b9197)

[Spring Boot中关于%2e的Trick](http://rui0.cn/archives/1643)

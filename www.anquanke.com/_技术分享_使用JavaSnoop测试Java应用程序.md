> 原文链接: https://www.anquanke.com//post/id/86215 


# 【技术分享】使用JavaSnoop测试Java应用程序


                                阅读量   
                                **139816**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/hacking-java-applications-using-javasnoop/](http://resources.infosecinstitute.com/hacking-java-applications-using-javasnoop/)

译文仅供参考，具体内容表达以及含义原文为准

****

[![](https://p0.ssl.qhimg.com/t01b2b7e002e2785257.jpg)](https://p0.ssl.qhimg.com/t01b2b7e002e2785257.jpg)

翻译：**[兄弟要碟吗](http://bobao.360.cn/member/contribute?uid=2874729223)**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

我们都知道Burp，Paros，WebInspect等工具可以拦截基于Web的应用的流量，也可以自动化对Web应用进行安全检测。然而胖客户端也有这种需求，我们没有自动化的工具可以用来对胖客户端应用程序进行自动化的安全检测。

目前针对.EXE应用程序流量的拦截和编辑软件已经有很多了，在本篇文章当中我们将讨论一个可以用于评估JAVA应用程序安全性的工具。

我们来看一下目前想要对JAVA胖客户端程序进行安全测试的各种方法以及各自的优缺点。

<br>

**方法1：拦截编辑流量**

应用程序需要使用HTTP进行通讯。

应用程序有配置代理的设置。

应用程序不使用加密、自定义协议或序列化对象。

如果满足上述的所有条件，我们可以使用Burp等代理工具来捕获并且修改通讯的流量进行安全检测。

<br>

**方法2：修改和攻击客户端**

可以识别的JAR文件

反编译

审计源代码

可以修改源代码并且重新编译客户端已用来发送自定义的攻击

在反编译class文件时通常会发现反编译后的源代码有多个编译错误，这些错误通常由反编译器本身的错误导致，这表明反编译与重新编译的过程在实践当中并不能100%确定成功。这种方法的缺点是流程复杂、繁琐、因为一些编译错误而浪费大量的时间来调试修改代码。

使用上面的两种方法对JAVA胖客户端应用程序进行安全测试时且少灵活性，并且有一定条件限制，很有可能出现两种方法都无法完成的情况。Aspect Security开发了一款名为JavaSnoop的工具来解决这些问题。

<br>

**JavaSnoop简介**

**JavaSnoop工具提供以下功能**

允许在JVM中轻松拦截任何方法

允许编辑返回值和参数

允许将自定义的Java代码插入到任何方法中

能够处理任何类型的Java应用程序(J2SE，Applet或JavaWeb应用)

能够处理已经运行的Java进程

不需要任何目标的源代码(原始的源代码或者反编译过后的)

JavaSnoop的这些功能使得我们可以对任何基于Java的应用程序进行安全测试。

**JavaSnoop的工作原理**

Java 6.0+包含了Attach API功能，可以对正在运行的或者要运行的JVM进行无缝的监控和修改，Attach API不是Java的标准API，而是Sun公司提供的一套扩展API，用来向目标JVM"附着"(Attach)代理工具程序的。JavaSnoop可以使用Attach API和Instrumentation类（有助于在运行时修改JVM）跳转到机器上的另一个JVM，并在该系统上的类方法中安装各种“钩子”。这些钩子然后被代理用于与GUI通信，允许JavaSnoop用户“拦截”JVM内的调用。

JavaSnoop使用的钩子技术可以执行以下操作：

1.编辑方法参数

2.编辑方法返回值

3.暂停方法

4.在方法开始时执行用户提供的脚本

5.在方法结束时执行用户提供的脚本

6.将参数打印到控制台（或文件）

<br>

**安装JavaSnoop**

可以从以下URL下载JavaSnoop工具：

[https://www.aspectsecurity.com/research/appsec_tools/javasnoop/](https://www.aspectsecurity.com/research/appsec_tools/javasnoop/) 

安装步骤：

**步骤1：**

从以下URL安装JDK 1.6：

[http://www.oracle.com/technetwork/java/javase/downloads/jdk6downloads-1902814.html](http://www.oracle.com/technetwork/java/javase/downloads/jdk6downloads-1902814.html) 

**步骤2：**

设置JAVA_HOME环境变量，步骤如下：

开始&gt;我的电脑&gt;属性&gt;高级系统设置&gt;高级&gt;环境变量。设置一个新的用户变量

java_home：路径指向JDK 1.6的文件夹，如下图所示：

[![](https://p4.ssl.qhimg.com/t0110ea865b97923d6f.png)](https://p4.ssl.qhimg.com/t0110ea865b97923d6f.png)

**步骤3：**

Applet和Java Web Start应用程序默认配置运行在严格的沙箱中。显然内部类和私有域的修改通常是不被允许的。这意味着我们必须将安全性“关闭”。JavaSoop中提供的startup.bat文件实现了这个需求，我们需要使用startup.bat来运行JavaSnoop。

该批处理文件将实现以下功能：

1.检查环境变量JAVA_HOME的值是否包含JDK1.6的路径

2.关闭JavaSnoop的安全性

3.启动JavaSnoop工具

4.退出工具后，再次将Java安全性恢复为安全浏览

将JavaSnoop注入到进程中：

JavaSnoop工具提供了两种注入进程的方式。

**1.现有进程：**

我们可以通过从可用的正在运行的进程列表中选择一个已经运行的进程来注入JavaSnoop.

[![](https://p2.ssl.qhimg.com/t01cf96c5d01f49125d.png)](https://p2.ssl.qhimg.com/t01cf96c5d01f49125d.png)

**2. 创建一个新的进程**

我们也可以通过选择要拦截的JAR文件来启动一个新进程。

[![](https://p1.ssl.qhimg.com/t017c0693e2adf186eb.png)](https://p1.ssl.qhimg.com/t017c0693e2adf186eb.png)

<br>

**JavaSnoop工具界面的功能**

JavaSnoop工具的主界面分为四部分，如下图所示:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a63f96b8d5e313eb.png)

**第一部分**

在这部分中，我们选择需要hook的类或方法。界面提供了一个按钮来添加一个新的hook。然后我们可以从列表中提供的类里添加一个方法，如下图所示：

[![](https://p2.ssl.qhimg.com/t0146ff1b174a15613f.png)](https://p2.ssl.qhimg.com/t0146ff1b174a15613f.png)

**第二部分**

本部分提供了用于设置截取方法调用的各种选项的功能。 我们可以设置正则表达式条件来匹配和拦截来方法调用的内容。如下图所示：

[![](https://p4.ssl.qhimg.com/t01cd72100038b932d7.png)](https://p4.ssl.qhimg.com/t01cd72100038b932d7.png)

**第三部分**

这一部分针对Hook提供了各种选项提供了以下各种选项：

 将parameters / stacktrace打印到控制台或特定文件

运行自定义脚本

篡改参数

修改返回值

暂停程序

**第四部分**

来自目标应用程序的Hook修改内容和反编译类的输出显示在此区域中。

使用JavaSnoop拦截来自基于JAVA的应用程序的数据

在本文中，我们将介绍两个基于Java的示例应用程序，并学习如何拦截JavaSnoop工具中的数据：

1.拦截浏览器中运行的applet的数据。

2.拦截基于JAVA的胖客户端 应用程序的数据。

<br>

**1.拦截浏览器中运行的applet的流量**

Java小程序是以Java字节码的形式传递给用户的小程序。Java小程序可以是Web页面的一部分，并且由Java虚拟机(JVM)在与Web浏览器分开的过程中执行，也可以在Sun的AppletViewer中运行,AppletViewer是用于测试applet小程序的独立工具。

很难拦截作为网页一部分的applet小程序的数据。普通代理工具（如Burp和Paros）无法拦截/修改来自这些applet程序的流量。下面我们演示一个使用JavaSnoop工具来拦截applet小程序的例子。

**步骤1：**我们将一个登录小程序嵌入到Web浏览器中，小程序接收用户登录的数据并将其转发到服务器进行身份验证。 为了拦截来自Java Applet的流量，我们使用JavaSnoop来拦截流量。

下面的图片展示了实例applet小程序：

[![](https://p0.ssl.qhimg.com/t010ad27beecce01063.png)](https://p0.ssl.qhimg.com/t010ad27beecce01063.png)

**步骤2：**由于我们已经在浏览器中打开了Java applet，因此我们在JavaSnoop工具中选择“An existing process”选项，将代理程序附加到运行的applet小程序中，如下图所示：

[![](https://p3.ssl.qhimg.com/t0172dd3c8411648ff5.png)](https://p3.ssl.qhimg.com/t0172dd3c8411648ff5.png)

**步骤3：**通过JavaSnoop连接到运行的小程序，然后我们可以选择想要拦截数据的类和相应的方法。我们来选择hook的方法所需的类，如下图：

[![](https://p3.ssl.qhimg.com/t01ef46f4800b211a60.png)](https://p3.ssl.qhimg.com/t01ef46f4800b211a60.png)

**步骤4：**我们然后选择类的方法，如下图所示：

[![](https://p1.ssl.qhimg.com/t0171de5ef585c8c9dd.png)](https://p1.ssl.qhimg.com/t0171de5ef585c8c9dd.png)

**步骤5：**下面的屏幕截图显示了包含hook方法的JavaSnoop接口以及拦截Java applet数据的方法和条件。

[![](https://p4.ssl.qhimg.com/t01351eaa2b72ebc958.png)](https://p4.ssl.qhimg.com/t01351eaa2b72ebc958.png)

**步骤6：**一旦我们在“登录”小程序上提交用户登录数据，该工具将进行拦截，并且会弹出一个窗口，用于编辑和转发拦截的数据。

[![](https://p4.ssl.qhimg.com/t015f9b98c0120aa0ad.png)](https://p4.ssl.qhimg.com/t015f9b98c0120aa0ad.png)

<br>

**2.拦截基于JAVA的胖客户端 应用程序的数据**

在上面的部分中，我们学会了拦截Java applet小程序的数据，下面我们学习拦截Jar应用程序的流量。例如，我们尝试拦截Burp代理工具的数据。

由于JavaSnoop可以篡改应用程序的数据跟流量，因此找出正确Hook的类跟方法成为评估的难点。通过代码审计的方式了解程序的逻辑结构再好不过了，但是在没有拿到源码的情况下，很难正确的hook相关的方法。 我们可以选择我们怀疑有可能是需要Hook的类跟方法，可以通过名称或类进行搜索，并且可以使用JavaSnoop的"Canary Mode"模式。这种模式在较大的应用中非常有用，因为较大的应用中需要hook的类跟方法查找起来比较困难。我们可以通过在JavaSnoop工具中拦截Burp来了解Canary Mode模式。

下面的图片显示了加载到JavaSnoop工具中的大量Burp的类。我们很难从里面识别用于Hook的类和方法。

[![](https://p1.ssl.qhimg.com/t016de651707bd4ed6e.png)](https://p1.ssl.qhimg.com/t016de651707bd4ed6e.png)

即使在搜索和猜测之后，面对大量的类也很难找到hook的方法。攻击者可能会对数据进入的UI界面感兴趣，我们可以通过跟踪UI界面传递过来的数据来确定需要hook的方法。

通过跟踪数据来定位需要hook的方法是Canary Mode模式的目的，这是JavaSnoop独特而有用的功能。在此模式下，我们可以定义要通过系统跟踪的一些“canary”值。这应该是通过表单域或者属性文件进入应用程序的一些独特的标识。

选择此值后，即可开始。然后JavaSnoop将删除当前正在使用的其他钩子，然后将监听JVM中每个参数为我们设定的canary值的所有方法。

每次发现canary被发送到一个方法时会将一个chirp发送回JavaSnoop，让用户知道正在运行canary值的方法。在某种程度上，这相当于一种非常原始，笨拙的数据流分析形式。

测试的方法步骤如下：

1.将JavaSnoop代理注入Burp进程

2.在JavaSnoop工具中打开Canary模式界面

3.在输入字段中输入要搜索的字符串

4.从界面启动canary模式

5.从Google浏览器向Burp发送请求，JavaSnoop工具将开始查找传递输入字符串(例如Google.com)的方法列表，然后我们可以勾选这些方法进行测试，如下图所示：

[![](https://p2.ssl.qhimg.com/t0117191b073a43a2aa.png)](https://p2.ssl.qhimg.com/t0117191b073a43a2aa.png)

在本文中，我们看到了在评估基于Java的胖客户端 应用程序时可能面临的缺点，并且还看到了如何使用JavaSnoop工具来克服这些困难。

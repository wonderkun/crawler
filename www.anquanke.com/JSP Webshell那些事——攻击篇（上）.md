> 原文链接: https://www.anquanke.com//post/id/214435 


# JSP Webshell那些事——攻击篇（上）


                                阅读量   
                                **215025**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01caeb942ae166027b.png)](https://p0.ssl.qhimg.com/t01caeb942ae166027b.png)

作者：[阿里云云安全中心 ](https://mp.weixin.qq.com/s/XZvQgh6g69AUNUi_QK9FbQ)

## 前言

目前很多大型厂商都选择使用Java进行Web项目的开发，近年来随着各种JAVA指定环境RCE漏洞的出现，Java Web的安全逐渐被人们所重视，与漏洞相关的还有用于后期维持权限的Webshell。与PHP不同的是，JSP的语言特性较为严格，属于强类型语言，并且在JDK9以前并没有所谓的eval函数。一般而言JSP的变形免杀较为困难，但是依旧存在很多的”黑魔法”。

不知攻，焉知防。阿里云安骑士Webshell检测系统在迭代升级过程中，除了内部的不断绕过尝试以外，也长期邀请大量白帽子进行持续的绕过测试。经过不断总结沉淀在JSP Webshell查杀引擎方面我们形成了基于字节码跟反汇编代码的检测方式，可以有效对抗云上高强度对抗性样本。

本文分为函数调用篇/战略战术篇/内存马篇/降维打击篇四个部分，将从攻击者的角度与大家一起分享JSP Webshell的攻击姿势。

## 关于JSP

JSP全称”Java Server Page”，其本质是一种Java Servlet。

JSP在第一次被访问的时候会先被翻译成Java文件，这个步骤由Tomcat等web容器完成；接着Java文件会被编译成JVM可以识别的class文件，这个步骤由JDK完成。

## 函数调用篇

[![](https://p2.ssl.qhimg.com/t012554bfb5fee20d29.png)](https://p2.ssl.qhimg.com/t012554bfb5fee20d29.png)

### 直接调用

常见的直接调用是通过 java.lang.Runtime#exec和java.lang.ProcessBuilder#start

#### java.lang.Runtime

[![](https://p1.ssl.qhimg.com/t014f67a1efaaae2159.png)](https://p1.ssl.qhimg.com/t014f67a1efaaae2159.png)

#### java.lang.ProcessBuilder

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013ee3f9a1f4150d5c.png)

### 反射调用

反射可以说是Java中最强大的技术，很多优秀的框架都是通过反射完成的。一般的类都是在编译期就确定下来并装载到JVM中，但是通过反射我们就可以实现类的动态加载。如果查阅源码可以发现，图中提到的很多命令执行方式的底层都是反射。

因为反射可以把我们所要调用的类跟函数放到一个字符串的位置，这样我们就可以利用各种字符串变形甚至自定义的加解密函数来实现对恶意类的隐藏。

[![](https://p5.ssl.qhimg.com/t012dc5b91092bc7063.png)](https://p5.ssl.qhimg.com/t012dc5b91092bc7063.png)

除此以外，反射可以直接调用各种私有类方法，文章接下来的部分会让大家进一步体会到反射的强大。

### 加载字节码

说到加载字节码就必须提到java.lang.ClassLoader这个抽象类，其作用主要是将 class 文件加载到 jvm 虚拟机中去，里面有几个重要的方法。
- loadClass()，加载一个类，该方法会先查看目标类是否已经被加载，查看父级加载器并递归调用loadClass()，如果都没找到则调用findClass()。
- findClass()，根据类的名称或位置加载.class字节码文件，获取字节码数组，然后调用defineClass()。
- defineClass()，将字节码加载到jvm中去，转化为Class对象
> 更详细的说明可以参考这篇文章：[https://zhuanlan.zhihu.com/p/103151189](https://zhuanlan.zhihu.com/p/103151189)

#### 调用defineClass

提到defineClass就想到了冰蝎，冰蝎可以说是第一个实现JSP一句话的Webshell管理工具。其中defineClass这个函数是冰蝎实现的核心。

因为java在1.8以前并没有像php的eval函数，所以要实现动态执行payload就要另外想办法。因为java世界中所有的执行都是依赖于字节码，不论该字节码文件来自何方，由哪种编译器编译，甚至是手写字节码文件，只要符合java虚拟机的规范，那么它就能够执行该字节码文件。所以如果可以让服务端做到动态地将字节码解析成Class，就可以实现“JSP一句话”的效果。

正常情况下，Java并没有提供直接解析class字节数组的接口。不过classloader内部实现了一个protected的defineClass方法，可以将byte[]直接转换为Class。但是因为该方法是protected的，我们没办法在外部直接调用。这里就有两种处理办法：

第一种是继承，直接自定义一个类继承classloader，然后在子类中调用父类的defineClass方法。这种方式比较简单，所以原版冰蝎中采用的这种办法。

第二种是反射，通过反射来修改保护属性，从而调用defineClass。

以下为蚁剑基于冰蝎的原理实现的JSP一句话样本。利用ClassLoader类中的defineClass，我们就可以把一个自定义的类传入并加载。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bcdee472f64469e8.png)

#### BCEL字节码

这个就是一个比较神奇的类了，可以直接通过classname来进行字节码的加载。

[![](https://p0.ssl.qhimg.com/t0129cad4d00d042d6a.png)](https://p0.ssl.qhimg.com/t0129cad4d00d042d6a.png)

查看loadClass方法的源码，发现会判断传入的bcelcode是否有”$$BCEL$$”这个字符串，就会将后面的内容转换成标准字节码，然后使用defineClass进行加载。

#### URLClassLoader远程加载

URLClassLoader是ClassLoader的子类，它用于从指定的目录或者URL路径加载类和资源。当URL里的参数是由”http://”开头时，会加载URL路径下的类。

[![](https://p0.ssl.qhimg.com/t01944577d6a0025cb2.png)](https://p0.ssl.qhimg.com/t01944577d6a0025cb2.png)

#### URLClassLoader本地加载

当URL里的参数是由”file://”开头时，会加载本地路径下的类。

由于加载的字节码是固定的并且不可直接修改，没办法直接实现对命令的动态解析。要么配合冰蝎一样的客户端，每次都调用ASM等字节码框架动态生成字节码传过去，要么就想其他办法把我们要执行的指令传递进去。

这个例子利用了一个很巧妙的方法：把收到的指令拼凑成源代码后直接在服务端进行编译，然后写入到本地文件中，再利用URLClassLoader对写入的文件进行加载。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c17c8fe3ddbbbc8e.png)

### 表达式类调用

#### ScriptEngineManager

通过ScriptEngineManager这个类可以实现Java跟JS的相互调用，虽然Java自己没有eval函数，但是ScriptEngineManager有eval函数，并且可以直接调用Java对象，也就相当于间接实现了Java的eval功能。但是写出来的代码必须是JS风格的，不够正宗，所以将这部分归类为“表达式类调用”部分。

[![](https://p2.ssl.qhimg.com/t016c5d0c7d5fb8c339.png)](https://p2.ssl.qhimg.com/t016c5d0c7d5fb8c339.png)

#### EL表达式

> 表达式语言（Expression Language），或称EL表达式，简称EL，是Java中的一种特殊的通用编程语言，借鉴于JavaScript和XPath。主要作用是在Java Web应用程序嵌入到网页（如JSP）中，用以访问页面的上下文以及不同作用域中的对象 ，取得对象属性的值，或执行简单的运算或判断操作。EL在得到某个数据时，会自动进行数据类型的转换。
[https://blog.csdn.net/FZW_Faith/article/details/54235104](https://blog.csdn.net/FZW_Faith/article/details/54235104)

除了ScriptEngineManager以外，ELProcessor也有自己的eval函数，并且可以调用Java对象执行命令。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019373232e9693e324.png)

#### Expression

java.beans.Expression同样可以实现命令执行，第一个参数是目标对象，第二个参数是所要调用的目标对象的方法，第三个参数是参数数组。这个类的优势是可以把要执行的方法放到一个字符串的位置，不过限制就是第一个参数必须是Object。不过我们可以配合反射将Runtime类的关键字给隐藏掉。

[![](https://p3.ssl.qhimg.com/t01b2f9fed274ef83dc.png)](https://p3.ssl.qhimg.com/t01b2f9fed274ef83dc.png)

[![](https://p1.ssl.qhimg.com/t01df6811c09173ca16.png)](https://p1.ssl.qhimg.com/t01df6811c09173ca16.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018596e497bba68ddc.png)

除了上面提到的以外还有OGNL(Struct)，SpEL(Spring)等表达式，但不是jdk自带的，在这里不予分析。

### 反序列化

序列化的过程是保存对象的过程，与之相反的，反序列化就是把对象还原的过程。在这里提到的反序列化并不仅仅指直接ObjectInputStream读入二进制流，利用XML/XSLT同样可以使保存的对象还原，达到反序列化的目的。

#### 重写ObjectInputStream的resolveClass

[![](https://p3.ssl.qhimg.com/t01119ac62de86fc7d7.png)](https://p3.ssl.qhimg.com/t01119ac62de86fc7d7.png)

#### XMLDecoder

XMLDecoder可以将XMLEncoder创建的xml文档内容反序列化为一个Java对象，研究过Weblogic系列漏洞的同学对这个类一定不陌生。通过传入恶意的XML文档即可实现任意命令的执行。

[![](https://p0.ssl.qhimg.com/t0111f207048b340365.png)](https://p0.ssl.qhimg.com/t0111f207048b340365.png)

#### XSLT

XSL 指扩展样式表语言（EXtensible Stylesheet Language）, 它是一个 XML 文档的样式表语言。通过构建恶意的模板让Webshell来解析，同样可以达到命令执行的目的。

[![](https://p3.ssl.qhimg.com/t01c7efdd1874abd20e.png)](https://p3.ssl.qhimg.com/t01c7efdd1874abd20e.png)

### JNDI注入

> JNDI (Java Naming and Directory Interface) 是一组应用程序接口，它为开发人员查找和访问各种资源提供了统一的通用接口，可以用来定位用户、网络、机器、对象和服务等各种资源。比如可以利用JNDI在局域网上定位一台打印机，也可以用JNDI来定位数据库服务或一个远程Java对象。JNDI底层支持RMI远程对象，RMI注册的服务可以通过JNDI接口来访问和调用。

提到jndi注入就想到了fastjson，通过lookup一个恶意的远程Java对象即可达到任意命令执行。相关的文章已有很多，这里不再赘述。

[![](https://p5.ssl.qhimg.com/t010b6cfc3d8acd5865.png)](https://p5.ssl.qhimg.com/t010b6cfc3d8acd5865.png)

### JNI调用

JNI全称 Java Native Interface，通过JNI接口可以调用C/C++方法，同样可以实现命令执行的目的。

> 详细介绍：[https://javasec.org/javase/JNI/](https://javasec.org/javase/JNI/)

[![](https://p2.ssl.qhimg.com/t0165eb0e852b01b23d.png)](https://p2.ssl.qhimg.com/t0165eb0e852b01b23d.png)

### JShell

JShell 是 Java 9 新增的一个交互式的编程环境工具。与 Python 的解释器类似，可以直接输入表达式并查看其执行结果。

[![](https://p1.ssl.qhimg.com/t013cb3a8e011f70028.png)](https://p1.ssl.qhimg.com/t013cb3a8e011f70028.png)

但是由于JDK8跟JDK9之间更改幅度较大，目前来说并没有普遍使用，所以暂时实战效果并不明显。

## 战略战术篇

由于Java面向对象的特性，几乎每个类都不是独立的，背后都是有一系列的继承关系。查杀引擎可能会识别常见的恶意类，但是我们就可以通过查找恶意类的底层实现或者高层包装类进行绕过，从而实现Webshell的免杀。

### 向下走–寻找底层实现类

这里以常见的Runtime类跟Expression类为例

#### ProcessImpl

查看Runtime类中exec方法的源码，可以发现exec实际上调用了ProcessBuilder的start方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01865a01f3781f6201.png)

进一步查看ProcessBuilder可以发现是触发了java.lang.ProcessImpl的start方法

[![](https://p3.ssl.qhimg.com/t01427e55b429d24e63.png)](https://p3.ssl.qhimg.com/t01427e55b429d24e63.png)

跟进ProcessImpl的start发现最后调用了其构造方法。

[![](https://p4.ssl.qhimg.com/t01ff7dacd14c12af39.png)](https://p4.ssl.qhimg.com/t01ff7dacd14c12af39.png)

看一下ProcessImpl的构造方法是private类型的，并且没有任何共有构造器，所以直接实例化ProcessImpl就会报错。

[![](https://p4.ssl.qhimg.com/t01e6c8e21655f63d37.png)](https://p4.ssl.qhimg.com/t01e6c8e21655f63d37.png)

在Java中，如果想要阻止一个类直接被实例化一般有两种方法，一种是直接把类名用private修饰，另一种是只设置私有的构造器。虽然我们不能直接new一个ProcessImpl，但是可以利用反射去调用非public类的方法。

[![](https://p1.ssl.qhimg.com/t017ad3922b21cecebb.png)](https://p1.ssl.qhimg.com/t017ad3922b21cecebb.png)

#### Statement

上文中提到了Expression的getValue方法可以实现表达式的执行，看一下他的源码的内容

发现Expression类继承了Statement，并且再构造函数中调用的也是父类的构造函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013403af6c536a9443.png)

[![](https://p5.ssl.qhimg.com/t0154e4d9cb3ca87f0d.png)](https://p5.ssl.qhimg.com/t0154e4d9cb3ca87f0d.png)

查看getValue方法，发现调用了父类的invoke函数

[![](https://p5.ssl.qhimg.com/t014b36cb370a236a2b.png)](https://p5.ssl.qhimg.com/t014b36cb370a236a2b.png)

查看invoke函数，跳转到了java.beans.Statement#invoke

[![](https://p3.ssl.qhimg.com/t01e573fd57fcaf28b9.png)](https://p3.ssl.qhimg.com/t01e573fd57fcaf28b9.png)

跟进java.beans.Statement#invokeInternal发现底层的实现其实就是反射

[![](https://p4.ssl.qhimg.com/t012732d9c77862eb02.png)](https://p4.ssl.qhimg.com/t012732d9c77862eb02.png)

综上所述，Expression的getValue实际上是调用了Statement类的invoke()函数，再通过一系列的反射实现表达式的计算。但是invoke函数不是public类型的，不能直接调用。但是我们可以发现同类中的java.beans.Statement#execute方法调用了invoke，且同时满足是public类型，可以直接调用。Statement类也是public的，可以直接new，所以我们就可以构造出一个新的利用方式。

[![](https://p3.ssl.qhimg.com/t0141a2e854729926dc.png)](https://p3.ssl.qhimg.com/t0141a2e854729926dc.png)

[![](https://p0.ssl.qhimg.com/t011944ee88d5a054f9.png)](https://p0.ssl.qhimg.com/t011944ee88d5a054f9.png)

#### ELManager

查看ELProcessor的eval的底层实现，找到javax.el.ELProcessor#getValue

[![](https://p0.ssl.qhimg.com/t011e022f2b232c3be7.png)](https://p0.ssl.qhimg.com/t011e022f2b232c3be7.png)

其实是调用了this.factory的createValueExpression方法，跟进this.factory发现是ELProcessor类的构造方法中通过ELManager.getExpressionFactory()获取的。

[![](https://p1.ssl.qhimg.com/t016ad54f7bd5147559.png)](https://p1.ssl.qhimg.com/t016ad54f7bd5147559.png)

所以就可以构造如下形式进行绕过。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0196a0406a55b628b1.png)

### 向上走–寻找调用跟包装类

既然可以用底层类来绕过，那么我们当然可以寻找哪些类对我们的恶意类进行了调用跟包装。

#### sun.net.[www.MimeLauncher](www.MimeLauncher)

从源码中可以看到sun.net.[www.MimeLauncher#run](www.MimeLauncher#run)方法中最后调用了Runtime类的exec方法

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01008d98948bd22c0a.png)

但是这个类是package-private修饰的，所以不能直接调用。不过没关系，我们还有反射。

[![](https://p1.ssl.qhimg.com/t0131a728df70eb673c.png)](https://p1.ssl.qhimg.com/t0131a728df70eb673c.png)

构造所需参数，然后通过反射调用run方法

[![](https://p1.ssl.qhimg.com/t016157c83e3f5a05d9.png)](https://p1.ssl.qhimg.com/t016157c83e3f5a05d9.png)

[![](https://p1.ssl.qhimg.com/t01bf0ac373b75705e4.png)](https://p1.ssl.qhimg.com/t01bf0ac373b75705e4.png)

在源码中grep一下关键字可以看到同样的类还有几个，这里不再赘述。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cd12beff4d9417b1.png)

## 最后

Java博大精深，深入挖掘还可以发现更多有趣的特性。本文仅为抛砖引玉，如果有不严谨的地方欢迎指正。

### 关于我们

阿里云安全-能力建设团队以安全技术为本，结合云计算时代的数据与算力优势，建设全球领先的企业安全产品，为阿里集团以及公有云百万用户的基础安全保驾护航。

团队研究方向涵盖WEB安全、二进制安全、企业入侵检测与响应、安全数据分析、威胁情报等。

知乎链接：[https://zhuanlan.zhihu.com/p/120973806](https://zhuanlan.zhihu.com/p/120973806)

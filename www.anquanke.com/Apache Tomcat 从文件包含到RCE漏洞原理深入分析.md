
# Apache Tomcat 从文件包含到RCE漏洞原理深入分析


                                阅读量   
                                **686862**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](./img/200630/t015e3d0f1cfeae691a.jpg)](./img/200630/t015e3d0f1cfeae691a.jpg)



## 文章内容简介

本篇文章针对Apache Tomcat Ajp（CVE-2020-1938）漏洞的文件包含和RCE的利用方式以及原理进行的深入的分析，同时包括漏洞复现和分析环境搭建的详细步骤，大家可以根据文中所写，自己搭建环境，然后通过在代码中下断点来自己进行调试，从而更好地理解漏洞的原理。



## 漏洞简介

2020年02月20日，于CNVD公开的漏洞公告中发现Apache Tomcat文件包含漏洞（CVE-2020-1938）。

Apache Tomcat为Apache开源组织开发的用于处理HTTP服务的项目。Apache Tomcat服务器中被发现存在文件包含漏洞，攻击者可利用该漏洞读取或包含 Tomcat 上所有 webapps目录下的任意文件。

本次漏洞是一个单独的文件包含漏洞，该漏洞依赖于Tomcat的AJP（定向包协议）协议。AJP协议自身存在一定的缺陷，导致存在可控参数，通过可控参数可以导致文件包含漏洞。AJP协议使用率约为7.8%，鉴于Tomcat作为中间件被大范围部署在服务器上，本次漏洞危害较大。



## AJP13协议介绍

我们对Tomcat的普遍认识主要有两大功能，一是充当web服务器，可以对一切静态资源的请求作出回应，二就是Servlet容器。

常见的web服务器有 Apache、 Nginx、 IIS等。常见的Servlet容器有Tomcat，Weblogic，JBOSS等。

Servlet容器可以理解为是Web服务器的升级版，拿Tomcat来举例，Tomcat本身可以不做Servlet容器使用，仅仅充当Web服务器的角色是完全没问题的，但是在处理静态资源请求的效率和速度上是远不及Apache，所以很多情况下生产环境中都会将Apache作为web服务器来接受用户的请求，静态资源有Apache直接处理，而Servlet请求则交由Tomcat来进行处理。这么做就可以让两个中间件各司其职，大大加快相应速度。

众所周知我们用户的请求是以http协议的形式传递给Web 服务器的，我们在浏览器中对某个域名或者ip进行访问，头部都会有http或者https的表示，而AJP协议浏览器是不支持的，我们无法通过浏览器发送AJP的报文。当然AJP这个协议也不是提供给我们用户来使用的。

在Tomcat $CATALINA_BASE/conf/web.xml默认配置了两个Connector，分别监听两个不同的端口，一个是HTTP Connector 默认监听8080端口，一个是AJP Connector 默认监听8009端口。

HTTP Connector的主要就是负责接收来自用户的请求，不管事静态还是动态，只要是HTTP请求就时由HTTP Connector来负责。有了这个 Connector Tomcat才能成为一个web服务器，但还额外可处理Servlet和jsp。

而AJP协议的使用对象通常是另一个Web服务器。例如Apache ，这里从网上找到了一张图，以此图来进行说明。

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017064e3d66bff6030.png)

通常情况下AJP协议的使用场景是这样的。

AJP是一个二进制的TCP传输协议，浏览器无法使用，首先由Apache与Tomcat之间进行AJP协议的通信，然后由Apache通过proxy_ajp模块进行反向代理，将其转换成HTTP服务器然后在暴露给用户，让用户来进行访问。

之所以要这么做，是因为相比HTTP这种纯文本的协议来说，效率和性能更高，同时也做了很多优化。

其实AJP协议某种程度上可以理解为是HTTP的二进制版，为了加快传输效率从而被使用，实际情况是像Apache这样有proxy_ajp模块可以反向代理AJP协议的很少，所以日常生产中AJP协议也很少被用到



## Tomcat 远程文件包含漏洞分析

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>漏洞分析环境搭建

首先从官网下载对应的Tomcat源码文件，和可执行文件。<br>[http://archive.apache.org/dist/tomcat/tomcat-8/v8.0.50/](http://archive.apache.org/dist/tomcat/tomcat-8/v8.0.50/)

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015de5c5a37246f50d.png)

下载好后将两个文件夹放入同一个目录下<br>
然后在源码中新增pom.xml并加入以下内容



```
&lt;?xml version=”1.0” encoding=”UTF-8”?&gt;

&lt;project xmlns="http://maven.apache.org/POM/4.0.0"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd"&gt;

&lt;modelVersion&gt;4.0.0&lt;/modelVersion&gt;
&lt;groupId&gt;org.apache.tomcat&lt;/groupId&gt;
&lt;artifactId&gt;Tomcat8.0&lt;/artifactId&gt;
&lt;name&gt;Tomcat8.0&lt;/name&gt;
&lt;version&gt;8.0&lt;/version&gt;

&lt;build&gt;
&lt;finalName&gt;Tomcat8.0&lt;/finalName&gt;
&lt;sourceDirectory&gt;java&lt;/sourceDirectory&gt;
&lt;testSourceDirectory&gt;test&lt;/testSourceDirectory&gt;
&lt;resources&gt;
&lt;resource&gt;
&lt;directory&gt;java&lt;/directory&gt;
&lt;/resource&gt;
&lt;/resources&gt;
&lt;testResources&gt;
&lt;testResource&gt;
&lt;directory&gt;test&lt;/directory&gt;
&lt;/testResource&gt;
&lt;/testResources&gt;
&lt;plugins&gt;
&lt;plugin&gt;
&lt;groupId&gt;org.apache.maven.plugins&lt;/groupId&gt;
&lt;artifactId&gt;maven-compiler-plugin&lt;/artifactId&gt;
&lt;version&gt;2.3&lt;/version&gt;
&lt;configuration&gt;
&lt;encoding&gt;UTF-8&lt;/encoding&gt;
&lt;source&gt;1.8&lt;/source&gt;
&lt;target&gt;1.8&lt;/target&gt;
&lt;/configuration&gt;
&lt;/plugin&gt;
&lt;/plugins&gt;
&lt;/build&gt;

&lt;dependencies&gt;
&lt;dependency&gt;
&lt;groupId&gt;junit&lt;/groupId&gt;
&lt;artifactId&gt;junit&lt;/artifactId&gt;
&lt;version&gt;4.12&lt;/version&gt;
&lt;scope&gt;test&lt;/scope&gt;
&lt;/dependency&gt;
&lt;dependency&gt;
&lt;groupId&gt;org.easymock&lt;/groupId&gt;
&lt;artifactId&gt;easymock&lt;/artifactId&gt;
&lt;version&gt;3.4&lt;/version&gt;
&lt;/dependency&gt;
&lt;dependency&gt;
&lt;groupId&gt;ant&lt;/groupId&gt;
&lt;artifactId&gt;ant&lt;/artifactId&gt;
&lt;version&gt;1.7.0&lt;/version&gt;
&lt;/dependency&gt;
&lt;dependency&gt;
&lt;groupId&gt;wsdl4j&lt;/groupId&gt;
&lt;artifactId&gt;wsdl4j&lt;/artifactId&gt;
&lt;version&gt;1.6.2&lt;/version&gt;
&lt;/dependency&gt;
&lt;dependency&gt;
&lt;groupId&gt;javax.xml&lt;/groupId&gt;
&lt;artifactId&gt;jaxrpc&lt;/artifactId&gt;
&lt;version&gt;1.1&lt;/version&gt;
&lt;/dependency&gt;
&lt;dependency&gt;
&lt;groupId&gt;org.eclipse.jdt.core.compiler&lt;/groupId&gt;
&lt;artifactId&gt;ecj&lt;/artifactId&gt;
&lt;version&gt;4.5.1&lt;/version&gt;
&lt;/dependency&gt;
&lt;/dependencies&gt;
&lt;/project&gt;
```

然后添加一个Application

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e0ef7f6abca37ed6.png)

1、按照下面图示新增Application的配置信息<br>
2、在Man class:中填入:`org.apache.catalina.startup.Bootstrap`<br>
3、在VM options:中填入:`-Dcatalina.home="apache-tomcat-8.5.34"`，catalina.home替换成tomcat binary core的目录<br>
4、jdk默认是1.8，因为我装的就是jdk1.8版本<br>
5、启动过程中Test模块会报错，且为TestCookieFilter.java，注释里面的测试内容即可

然后运行 访问127.0.0.1:8080出现以下页面则环境搭建成功

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01246892899a17c70d.png)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0"></a>漏洞复现

#### <a class="reference-link" name="%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96"></a>任意文件读取

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d8b0afab62040058.png)

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cb386aa0ae741144.png)

#### <a class="reference-link" name="RCE"></a>RCE

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0154adc5c449095248.png)

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c763fa4742fcd342.png)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

首先根据网上的介绍我们定位到 org.apache.coyote.ajp.AjpProcessor这个类，根据网上透漏的漏洞消息，我们得知漏洞的产生是由于Tomcat对ajp传递过来的数据的处理存在问题，导致我们可以控制“javax.servlet.include.request_uri”，“javax.servlet.include.path_info”，“javax.servlet.include.servlet_path”，这三个参数，从而读取任意文件，甚至可以进行RCE。

我们先从任意文件读取开始分析

我所使用的环境使用Tomcat 8.0.50版本所搭建的，产生漏洞的点并不在AjpProcessor.prepareRequest()方法，8.0.50版本的漏洞点存在于AjpProcessor的父类，AbstractAjpProcessor这个抽象类的prepareRequest()中

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f54546be14b8b625.png)

我们在这里下断点

然后运行exp，然后先看一下此时的调用链

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014e48cbda7ac544f7.png)

首先由于此次数据传输使用的是AJP协议，监听的8009口，并非我们常见的HTTP协议。所以首先SocketPeocessore这个内部类来进行处理，

处理完成后经过几次调用交由AbstractAjpProcessor.prepareRequest()，该方法就是漏洞产生的第一个点。

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019d82df18db61b3d8.png)

我们单步步入request.setAttribute()方法

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01daf32e46bb963321.png)

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a9a033c59ab7b82d.png)

这里我们可以看到，attributes是一个HashMap，那这样就非常好理解了，就是将我们通过AJP协议传递过来的三个参数循环遍历存入这个HashMap

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01154ee9a17116acd2.png)

可以看到这里是一个while循环，我们来直接看循环完成后的结果

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01571fca3f56a912a7.png)

执行完后就会在Request对象的attributes属性中增加这三条数据。

到这里就是漏洞的前半部分，操纵可控变量将其改造层我们想要的数据。

我们先看一下exp发出的数据包是什么样的

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a3f0f445e961df7c.png)

我们通过使用WireShark抓包，看到了AJP报文的一些信息，其中有四个比较重要的参数，

URI:/asdf

javax.servlet.include.request_uri:/

javax.servlet.include.path_info: WEB-INF/Test.txt

javax.servlet.include.servlet_path:/

首先要讲到的就是这个URL，通过之前对AJP协议的介绍，我们知道通过AJP协议传来的数据最中还是要交由Servlet来进行处理的，那么问题就来了，应该交由那个Servlet来进行处理？

我们通过翻阅网上关于Tomcat的架构的一些文章和资料得知，在Tomcat $CATALINA_BASE/conf/web.xml这个配置文件中默认定义了两个Servlet

一个是DefaultServlet

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c79f4a3a953da83b.png)

另一个是JspServlet

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014161a612dda60f7c.png)

由于 $CATALINA_BASE/conf/web.xml这个文件是tomcat启动时默认加载的，所以这两个Servlet会默认存在Servlet容器中

当我们请求的URI不能和任何Servlet匹配时，就会默认由 DefaultServlet来处理，DefaultServlet主要用于处理静态资源，如HTML、图片、CSS、JS文件等，而且为了提升服务器性能，Tomcat对访问文件进行缓存。按照默认配置，客户端请求路径与资源的物理路径是一致的。

我们看到我们请求的URI为“/asdf”这就符合了无法匹配后台任何的Servlet这么一个条件，这里要注意一下，举个例子，譬如我们请求一个“abc.jsp” 但是后台没有“abc.jsp” 这种不属于无法匹配任何Servlet，因为.jsp的请求会默认走JspServlet来进行处理

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012d3d15e7672867af.png)

好的，根据这段介绍，结合我们发送的数据包中的“URI:/asdf”这一属性，我们可以判断此次请求是由DefaultServlet来进行处理的。

我们定位到DefaultServlet的doGet方法

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01dfc3fdb730f504da.png)

doGet方法里又调用了serveResource()方法

serveResource()方法由调用了getRelativePath()方法来进行路径拼接，我们跟进看一看

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010112451b4a753df3.png)

这里就是将我们传入的path_info 、servlet_path 进行复制的地方，request_uri用来做判断，如果发送的数据包中没有request_uri，就会走else后面的两行代码进行赋值，这样会就会导致漏洞利用失败

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ca91b2c24c5de82a.png)

接下来就是对路径的拼接了，这里可以看到如果传递数据时不传递servlet_path，则result在进行路径拼接时就不会将“/”拼接在“WEB-INF/web.xml”的头部，最后拼接的结果仍然是“WEB-INF/web.xml”

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e07b58489c8cc65e.png)

接下来返回DefaultServle.serveResource()

紧接着判断path变量长度是否为0，为0则调用目录重定向方法

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012732112b678da0b4.png)

下面的代码就要开始读区我们指定的资源文件了

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b0156d0a67830696.png)

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01812a575a8787c8a4.png)

我们跟进StandardRoot.getResource()方法

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0185082de0be76c6e1.png)

getResource()方法中又调用了一个很重要的方法validate()方法并将path作为变量传递进去进行处理，我们继续跟入

这里就牵扯到为什么我们为什么不能通过”/../../“的方式来读取webapps目录的上层目录里文件的原因了，首先是正常请求

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01db45597251ef892f.png)

我们可以看到正常请求最后return的result的路径就是我们文件所在的相对路径。

当我门尝试使用WEB-INF/../../Test.txt来读区webapps以外的目录中的文件时。可以看到此时返回的result就是null了，而且会抛出异常。

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010713f96d0a61e5f7.png)

这一切的原因都在RequestUtil.normalize()这个函数对我们传递进来的路径处理上，我们跟进看一看

关键的点就在下面的截图代码中。我们传入的路径是“/WEB-INF/../../Test.txt”,首先程序会判断我们的路径中是否存在“/../”，自然是存在的且索引是8大于0，所以第一个if 判断不会成功，也就不会跳出while循环，此时处理我们的路径，截取“/WEB-INF/..”以后的内容，然后在用String,indexOf()函数判断路径里是否有“/../”,显然还是有的，且索引为零，符合第二个if判断的条件，return null。

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018d081ff132bbd37c.png)

此处的目的就是 不允许传递以“/../”为开头的路径，且不允许同时出现两个连在一起的“/../” 所以我们最多只能读取到webapps目录，无法读取webapps以外的目录中的文件。

想要读取webapps目录下的其余目录内的文件可以通过修改数据包中的”URI”这个参数来实现

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019bb989cf1a68f1ea.png)

如此一来，程序最中拼接出我们所指定文件的绝对路径，并作为返回值进行返回

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0104fbbe27e1ac910d.png)

接下来就是回到getResource()函数进行文件读取了

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0179e98edeb709ea0b.png)

以下是任意文件读取的调用链

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014809570e11e81812.png)

##### <a class="reference-link" name="RCE"></a>RCE

接下来讲一下，RCE实现的原理

之前讲过Tomcat $CATALINA_BASE/conf/web.xml这个配置文件中默认定义了两个Servlet，刚才任意文件读取利用了DefaultServlet，而RCE就需要用到另一个也就是JspServlet

默认情况下，JspServlet的url-pattern为**.jsp和**.jspx，因此他负责处理所有JSP文件的请求。

JspServlet主要完成以下工作：

1.根据JSP文件生成对应Servlet的Java代码（JSP文件生成类的父类我org.apache.jasper.runtime.HttpJspBase——实现了Servlet接口）

2.将Java代码编译为Java类。

3.构造Servlet类实例并且执行请求。

其实本质核心就是通过JspServlet来执行我们想要访问的.jsp文件

所以想要RCE的前提就是，先要想办法将写有自己想要执行的命令的文件(可以是任意文件后缀，甚至没有后缀)上传到webapps的目录下，才能访问该文件然后通过JSP模板的解析造成RCE

来看下我们这次发送的Ajp报文的内容

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01da60576d9bf1411c.png)

这里的“URI”参数一定要是以“.jsp”进行结尾的，这个jsp文件可以不存在。

剩下的三个参数就和之前没什么区别了，“path_info”参数对应的就是我们上传的还有jsp代码的文件。

我们定位到JspServlet.Service()方法

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0109f230fab451546a.png)

可以看到首先将”servlet_path”的值取出赋值给变量jspUri

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bbef3bc1522269ea.png)

然后将”path_info”参数对应的值取出并赋值给“pathInfo”变量，然后和“jspUri”进行拼接

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011ed3b09257a4da73.png)

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0128e8edc8cf7b8134.png)

接下来跟进serviceJspFile()方法

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0184b38e355992431b.png)

首先生成JspServletWrapper对象

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010d369be66e4f451a.png)

然后调用JspServletWrapper.service()方法

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01844689cc59ea56a4.png)

获取对应的Servlet

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a9af60b33633460f.png)

调用该Servlet的service方法

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01671ee7f2665e0cd9.png)

接下来就是就是解析我们上传文件中的java代码了至此，RCE漏洞原理分析完毕。下面是调用链

[![](./img/200630/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01606769fc72ebcfd9.png)

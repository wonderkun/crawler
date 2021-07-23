> 原文链接: https://www.anquanke.com//post/id/244494 


# ctf中php的一些trick


                                阅读量   
                                **257714**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01494c1e0de499424b.png)](https://p5.ssl.qhimg.com/t01494c1e0de499424b.png)



<a class="reference-link" name="%E8%8E%B7%E5%8F%96http%E8%AF%B7%E6%B1%82%E7%9A%84%E5%8F%98%E9%87%8F%E5%80%BC%E8%BF%87%E7%A8%8B"></a>获取http请求的变量值过程

对于php获取http请求的值的变量`$_GET,$_POST,$_COOKIE,$_SERVER,$_ENV,$_REQUEST,$_FILES`，在初始化请求时就注册了这么多的超全局变量 ，这里从php的源代码就可以看出：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a99bca56a40ec553.png)

<a class="reference-link" name="%E5%9C%A8%E7%9C%8B%E7%9C%8Bphp%E7%9A%84%E5%AE%98%E6%96%B9%E6%96%87%E6%A1%A3%E6%80%8E%E4%B9%88%E8%AF%B4"></a>在看看php的官方文档怎么说

[![](https://p3.ssl.qhimg.com/t01d543ecd32021c77f.png)](https://p3.ssl.qhimg.com/t01d543ecd32021c77f.png)

这里重点关照一下`$_REQUEST`，明明写的默认是包含`$_GET，$_POST 和 $_COOKIE`的数组，但是实际上却是只包含了`$_GET，$_POST`

[![](https://p3.ssl.qhimg.com/t0159428e1bea4a3aef.png)](https://p3.ssl.qhimg.com/t0159428e1bea4a3aef.png)

<code class="lang-index.php">&lt;?php<br>
var_dump($_GET);<br>
var_dump($_POST);<br>
var_dump($_COOKIE);<br>
var_dump($_REQUEST);<br>
?&gt;<br></code>

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011a561b4038e5325b.png)

<a class="reference-link" name="%E8%BF%99%E6%98%AF%E4%B8%BA%E4%BB%80%E4%B9%88%E5%91%A2%EF%BC%9F%E5%BA%95%E5%B1%82%E4%BB%A3%E7%A0%81%E4%B9%9F%E8%A7%A3%E9%87%8A%E4%BA%86%EF%BC%9A"></a>这是为什么呢？底层代码也解释了：

[![](https://p4.ssl.qhimg.com/t01876e316f2d209b61.png)](https://p4.ssl.qhimg.com/t01876e316f2d209b61.png)

&lt;a name=”然后看看php.ini里面的默认值是多少，由于首先会选择赋值为`request_order`的值，所以就只有GP了” class=”reference-link”&gt;然后看看php.ini里面的默认值是多少，由于首先会选择赋值为`request_order`的值，所以就只有GP了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01144d5439413f3649.png)

&lt;a name=”好了，现在就明白了`$_REQUEST`的值是根据`request_order`的值来先后合并的，所以这里就会出现`$_REQUEST`里面的key先被`$_GET`赋值，再被`$_POST`赋值，这样就post的值就覆盖了get在request里面注册的值了，这个点印象中已经考过几次了” class=”reference-link”&gt;好了，现在就明白了`$_REQUEST`的值是根据`request_order`的值来先后合并的，所以这里就会出现`$_REQUEST`里面的key先被`$_GET`赋值，再被`$_POST`赋值，这样就post的值就覆盖了get在request里面注册的值了，这个点印象中已经考过几次了

[![](https://p0.ssl.qhimg.com/t01d62981f9fc03d5ce.png)](https://p0.ssl.qhimg.com/t01d62981f9fc03d5ce.png)

现在继续看看php对于`$_GET，$_POST 和 $_COOKIE`的处理部分是在`php_register_variable_ex`这里主要关注3个地方：

[![](https://p2.ssl.qhimg.com/t010635297d4e2918c5.png)](https://p2.ssl.qhimg.com/t010635297d4e2918c5.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c897356485097667.png)

[![](https://p5.ssl.qhimg.com/t017444703d917123d9.png)](https://p5.ssl.qhimg.com/t017444703d917123d9.png)

那么怎么才能获取到`$_GET`真正的变量名呢？那就是通过`$_SERVER`来获取

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015740aa656610bc9a.png)

post的可以通过伪协议来得到真正的变量名，`php://input`

<a class="reference-link" name="php%E8%AF%BB%E5%8F%96%E6%96%87%E4%BB%B6%E6%88%96%E8%80%85%E8%8E%B7%E5%8F%96%E6%96%87%E4%BB%B6%E7%9A%84%E7%89%B9%E6%80%A7"></a>php读取文件或者获取文件的特性

&lt;a name=”先说一下php底层对于处理获取文件数据流是用的2个不同的方法，所以导致了`readfile("/e/../../etc/passwd")`可以成功，而`is_file("/e/../../etc/passwd")`为false” class=”reference-link”&gt;先说一下php底层对于处理获取文件数据流是用的2个不同的方法，所以导致了`readfile("/e/../../etc/passwd")`可以成功，而`is_file("/e/../../etc/passwd")`为false

[![](https://p4.ssl.qhimg.com/t015eee58e3e1faeef7.png)](https://p4.ssl.qhimg.com/t015eee58e3e1faeef7.png)

[![](https://p0.ssl.qhimg.com/t01572bccea48b0449b.png)](https://p0.ssl.qhimg.com/t01572bccea48b0449b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013780de4c551a39ac.png)

[![](https://p5.ssl.qhimg.com/t017e5273aca30bbd5c.png)](https://p5.ssl.qhimg.com/t017e5273aca30bbd5c.png)

[![](https://p4.ssl.qhimg.com/t01cbf8bcea4c406ea6.png)](https://p4.ssl.qhimg.com/t01cbf8bcea4c406ea6.png)

然后就是php的伪协议了：`php://stdin,php://stdout,php://stderr,php://input,php://output,php://fd,php://memory,php://temp,php://filter`，这些里面最常用到的就是`php://filter`了，关于这个的一系列trick网上一大把，这里主要讲一下`include,require,include_once,require_once`，这4个语法关键词实际上都是调用的同一个函数，只是选择的模式不同

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0132771074388a0964.png)

[![](https://p5.ssl.qhimg.com/t0104d5fa6ca6b39e63.png)](https://p5.ssl.qhimg.com/t0104d5fa6ca6b39e63.png)

可以发现include和readfile这些文件读取的函数又是走的不同路线，那这样会不会出现什么差异呢？跟着源码看了一下发现，是否解析`data://和http://`实现的文件包含关键代码如下：

<code class="lang-c">    if (wrapper &amp;&amp; wrapper-&gt;is_url &amp;&amp;<br>
(options &amp; STREAM_DISABLE_URL_PROTECTION) == 0 &amp;&amp;<br>
(!PG(allow_url_fopen) ||<br>
(((options &amp; STREAM_OPEN_FOR_INCLUDE) ||<br>
PG(in_user_include)) &amp;&amp; !PG(allow_url_include)))) `{`<br>
if (options &amp; REPORT_ERRORS) `{`<br>
/* protocol[n] probably isn't '\0' */<br>
if (!PG(allow_url_fopen)) `{`<br>
php_error_docref(NULL, E_WARNING, "%.*s:// wrapper is disabled in the server configuration by allow_url_fopen=0", (int)n, protocol);<br>
`}` else `{`<br>
php_error_docref(NULL, E_WARNING, "%.*s:// wrapper is disabled in the server configuration by allow_url_include=0", (int)n, protocol);<br>
`}`<br>
`}`<br>
return NULL;<br>
`}`<br></code>

拆开来理解一下，第一层是`wrapper &amp;&amp; wrapper-&gt;is_url`就是判断这个数据流是否有url模式，第二层`(options &amp; STREAM_DISABLE_URL_PROTECTION) == 0`通过运算判断数据流是否是url，第三层`!PG(allow_url_fopen)`判断php的配置里面是否启用了`allow_url_fopen`，`((options &amp; STREAM_OPEN_FOR_INCLUDE) ||PG(in_user_include))`大概是判断数据流是不是用于include，`!PG(allow_url_include)`判断php是否配置了`allow_url_include`，所以可以发现这里对include和readfile这些文件操作函数处理流程是不一样的，写个测试代码：

`&lt;?php`

readfile($_GET[‘file’]);<br>
include $_GET[‘file’];<br>
?&gt;

[![](https://p1.ssl.qhimg.com/t01c3f7233ef6b82099.png)](https://p1.ssl.qhimg.com/t01c3f7233ef6b82099.png)

<a class="reference-link" name="%E5%8F%AF%E4%BB%A5%E5%8F%91%E7%8E%B0%E7%88%86%E4%BA%863%E4%B8%AA%E9%94%99%E8%AF%AF%EF%BC%8C%E7%AC%AC%E4%B8%80%E4%B8%AA%E6%98%AF%E8%AF%B4%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E9%87%8C%E9%9D%A2%E7%A6%81%E7%94%A8%E4%BA%86data%E7%9A%84%E6%95%B0%E6%8D%AE%E6%B5%81%EF%BC%8C%E7%AC%AC%E4%BA%8C%E6%98%AF%E4%B8%8D%E8%83%BD%E6%89%93%E5%BC%80data%E7%9A%84%E6%95%B0%E6%8D%AE%E6%B5%81%EF%BC%8C%E7%AC%AC%E4%B8%89%E4%B8%AA%E6%98%AF%E6%98%BE%E7%A4%BA%E7%9A%84%E4%B8%8D%E8%83%BD%E6%89%93%E5%BC%80%E6%96%87%E4%BB%B6%EF%BC%8C%E5%9C%A8include_path%E4%B8%8B%E9%9D%A2%E6%B2%A1%E6%9C%89%E5%8F%91%E7%8E%B0%E6%96%87%E4%BB%B6%EF%BC%8C%E6%89%80%E4%BB%A5%E5%B0%B1%E5%BE%88%E6%98%8E%E6%98%BE%E5%9C%A8linux%E4%B8%8B%E9%9D%A2%E5%8F%AF%E4%BB%A5%E5%88%A9%E7%94%A8readfile%E4%B8%8D%E8%83%BD%E8%AF%BB%E5%8F%96%E6%96%87%E4%BB%B6%EF%BC%8C%E8%80%8Cinclude%E5%8F%AF%E4%BB%A5%E5%8C%85%E5%90%AB%E6%96%87%E4%BB%B6%E7%9A%84%E7%89%B9%E6%80%A7%E4%BA%86"></a>可以发现爆了3个错误，第一个是说配置文件里面禁用了data的数据流，第二是不能打开data的数据流，第三个是显示的不能打开文件，在include_path下面没有发现文件，所以就很明显在linux下面可以利用readfile不能读取文件，而include可以包含文件的特性了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01deec36809d813482.png)

[![](https://p1.ssl.qhimg.com/t01a438e533a85e2ed1.png)](https://p1.ssl.qhimg.com/t01a438e533a85e2ed1.png)

[![](https://p4.ssl.qhimg.com/t011fe87d2e606a178c.png)](https://p4.ssl.qhimg.com/t011fe87d2e606a178c.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a155bb483009cbf0.png)

<a class="reference-link" name="phar%E7%9A%84%E4%B8%80%E4%BA%9B%E7%89%B9%E6%80%A7%E5%92%8C%E5%BA%95%E5%B1%82%E5%A4%84%E7%90%86%E5%8F%AF%E4%BB%A5%E5%8F%82%E8%80%83(%E5%9B%A0%E4%B8%BA%E4%B9%8B%E5%89%8D%E5%92%8C%E5%B8%88%E5%82%85%E5%A5%97%E8%B7%AF%E8%BF%87%EF%BC%8C%E6%89%80%E4%BB%A5%E5%B0%B1%E4%B8%8D%E5%9C%A8%E5%86%99%E4%BA%86):"></a>phar的一些特性和底层处理可以参考(因为之前和师傅套路过，所以就不在写了):

[https://guokeya.github.io/post/uxwHLckwx/](https://guokeya.github.io/post/uxwHLckwx/)

<a class="reference-link" name="unserialize%E7%9A%84%E4%B8%80%E4%BA%9B%E7%89%B9%E6%80%A7"></a>unserialize的一些特性

<a class="reference-link" name="%E5%85%88%E7%9C%8B%E7%9C%8B%E6%96%87%E6%A1%A3%EF%BC%8C%E8%BF%99%E9%87%8C%E5%86%99%E4%BA%86%E5%B0%B1%E6%8E%A5%E5%8F%97%E4%B8%80%E4%B8%AA%E5%AD%97%E7%AC%A6%E4%B8%B2%E7%9A%84%E5%8F%82%E6%95%B0%EF%BC%8C%E4%BD%86%E6%98%AF%E5%AE%9E%E9%99%85%E4%B8%8A%E6%98%AF2%E4%B8%AA%E5%8F%82%E6%95%B0%EF%BC%8C%E8%BF%98%E6%9C%89%E4%B8%80%E4%B8%AAcallback%E7%9A%84%E4%BE%8B%E5%AD%90%E4%B9%9F%E4%B8%8D%E9%94%99"></a>先看看文档，这里写了就接受一个字符串的参数，但是实际上是2个参数，还有一个callback的例子也不错

[![](https://p1.ssl.qhimg.com/t012d4843b8c021a33b.png)](https://p1.ssl.qhimg.com/t012d4843b8c021a33b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018b005f3d3fb6ce60.png)

<a class="reference-link" name="%E7%84%B6%E5%90%8E%E6%9D%A5%E7%9C%8B%E7%9C%8Bphp%E7%9A%84%E6%BA%90%E7%A0%81%E6%80%8E%E4%B9%88%E5%86%99%E7%9A%84%E5%90%A7"></a>然后来看看php的源码怎么写的吧

[![](https://p3.ssl.qhimg.com/t016602a3961d45eb54.png)](https://p3.ssl.qhimg.com/t016602a3961d45eb54.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011052ea0d73060bf3.png)

<a class="reference-link" name="%E6%B5%8B%E8%AF%95%E4%BB%A3%E7%A0%81%EF%BC%9A"></a>测试代码：

<code class="lang-php">&lt;?php<br>
class A`{`<br>
function __destruct()`{`<br>
echo "ok\n";<br>
`}`<br>
`}`<br>
var_dump(unserialize('O:1:"A":0:`{``}`',["allowed_classes"=&gt;true]));<br>
var_dump(unserialize('O:1:"A":0:`{``}`',["allowed_classes"=&gt;false]));<br>
var_dump(unserialize('O:1:"A":0:`{``}`',["allowed_classes"=&gt;["A"]]));<br>
var_dump(unserialize('O:1:"A":0:`{``}`',["allowed_classes"=&gt;["B"]]));<br>
?&gt;<br></code>

[![](https://p2.ssl.qhimg.com/t01e74ff92efe89e2e5.png)](https://p2.ssl.qhimg.com/t01e74ff92efe89e2e5.png)

&lt;a name=”然后看看php处理反序列化的细节吧，具体流程在`php_var_unserialize`里面，而且可以发现反序列化失败后直接抛的error，而不是异常，抛error就不会继续后面的代码了” class=”reference-link”&gt;然后看看php处理反序列化的细节吧，具体流程在`php_var_unserialize`里面，而且可以发现反序列化失败后直接抛的error，而不是异常，抛error就不会继续后面的代码了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011ced6ddc8d69e748.png)

<a class="reference-link" name="%E8%BF%99%E4%B8%AA%E5%BC%80%E5%90%AF%E5%8A%A8%E6%80%81%E8%B0%83%E8%AF%95%E6%96%B9%E4%BE%BF%E4%B8%80%E7%82%B9%EF%BC%8C%E9%A6%96%E5%85%88%E9%85%8D%E7%BD%AEvscode%E8%A7%A3%E6%9E%90.re%E5%90%8E%E7%BC%80%E7%9A%84%E4%B8%BAc"></a>这个开启动态调试方便一点，首先配置vscode解析.re后缀的为c

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cadc48316406c9aa.png)

[![](https://p3.ssl.qhimg.com/t01cb9016440aa703ea.png)](https://p3.ssl.qhimg.com/t01cb9016440aa703ea.png)

<a class="reference-link" name="%E5%85%88%E7%9C%8B%E7%9C%8BO%E8%A7%A3%E6%9E%90%E7%9A%84%E6%97%B6%E5%80%99%EF%BC%8C%E5%8F%AF%E4%BB%A5%E5%8F%91%E7%8E%B0%E5%BC%80%E5%A7%8B%E5%AF%B9%E2%80%9D%E5%92%8C:%E4%BD%9C%E4%B8%BA%E7%BB%93%E5%B0%BE%E8%BF%9B%E8%A1%8C%E4%BA%86%E9%AA%8C%E8%AF%81%EF%BC%8C%E4%BD%86%E6%98%AF%E5%8F%96%E5%87%BA%E7%B1%BB%E5%90%8D%E5%90%8E%E5%AF%B9%E4%BA%8E:%E5%92%8C%7B%E6%B2%A1%E6%9C%89%E9%AA%8C%E8%AF%81%EF%BC%8C%E6%89%80%E4%BB%A5%E5%8F%AF%E4%BB%A5%E7%9B%B4%E6%8E%A5%E4%B8%8D%E5%86%99%EF%BC%8C%E4%B9%9F%E5%8F%AF%E4%BB%A5%E6%88%90%E5%8A%9F%E5%8F%8D%E5%BA%8F%E5%88%97%E5%8C%96"></a>先看看解析的时候，可以发现开始对”和:作为结尾进行了验证，但是取出类名后对于:和`{`没有验证，所以可以直接不写，也可以成功反序列化

[![](https://p5.ssl.qhimg.com/t01a34581d8ba7de598.png)](https://p5.ssl.qhimg.com/t01a34581d8ba7de598.png)

[![](https://p3.ssl.qhimg.com/t01dbf2c6fa304b4b7f.png)](https://p3.ssl.qhimg.com/t01dbf2c6fa304b4b7f.png)

<code class="lang-php">&lt;?php<br>
class A`{`<br>
function __destruct()`{`<br>
echo "ok";<br>
`}`<br>
`}`<br>
unserialize('O:1:"A":0:`{``}`');<br>
unserialize('O:1:"A":0aa`}`');<br>
?&gt;<br></code>

[![](https://p3.ssl.qhimg.com/t01c47810da4cecfd56.png)](https://p3.ssl.qhimg.com/t01c47810da4cecfd56.png)

<a class="reference-link" name="%E7%84%B6%E5%90%8E%E7%9C%8B%E7%9C%8B%E5%AD%97%E7%AC%A6%E4%B8%B2%E7%9A%84s%E5%88%A4%E6%96%AD%E5%90%A7%EF%BC%8C%E5%B0%B1%E9%AA%8C%E8%AF%81%E4%BA%86%E5%90%8E%E9%9D%A22%E4%B8%AA%E5%AD%97%E7%AC%A6%E6%98%AF%E4%B8%8D%E6%98%AF%E2%80%9D%E5%92%8C;%E6%89%80%E4%BB%A5%E5%AD%97%E7%AC%A6%E8%BF%99%E9%87%8C%E5%B0%B1%E6%B2%A1%E6%9C%89%E4%BB%80%E4%B9%88%E9%97%AE%E9%A2%98%E4%BA%86"></a>然后看看字符串的s判断吧，就验证了后面2个字符是不是”和;所以字符这里就没有什么问题了

[![](https://p0.ssl.qhimg.com/t01be49850568e6937c.png)](https://p0.ssl.qhimg.com/t01be49850568e6937c.png)

<a class="reference-link" name="%E7%84%B6%E5%90%8E%E5%B0%B1%E6%98%AF%E5%AD%97%E7%AC%A6%E4%B8%B2%E7%9A%84S%E6%97%B6%E5%88%A4%E6%96%AD%E6%98%AF%E5%85%88%E7%BB%8F%E8%BF%87%E5%A4%84%E7%90%86%E5%90%8E%E5%9C%A8%E8%BF%9B%E8%A1%8C%E5%88%A4%E6%96%AD%E7%9A%84"></a>然后就是字符串的S时判断是先经过处理后在进行判断的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016300472add2d5334.png)

然后看看`unserialize_str`的主要处理逻辑，其实这里就是为了把`\74`变为t，其实大概的思想就是利用16进制和2进制的特性，因为16进制的第一个数字只影响对应二进制的前4位，第二个数字就只影响后4位

[![](https://p5.ssl.qhimg.com/t0100b6fec7514e7294.png)](https://p5.ssl.qhimg.com/t0100b6fec7514e7294.png)

&lt;a name=”其他几个类型的判断也没有什么特别的了，然后就是在类解析的最后还有一个解析类似魔术方法的东西`__unserialize`，而且当`__unserialize`存在时`__wakeup`是不会触发的” class=”reference-link”&gt;其他几个类型的判断也没有什么特别的了，然后就是在类解析的最后还有一个解析类似魔术方法的东西`__unserialize`，而且当`__unserialize`存在时`__wakeup`是不会触发的

[![](https://p4.ssl.qhimg.com/t0158f49e5b57991d26.png)](https://p4.ssl.qhimg.com/t0158f49e5b57991d26.png)

[![](https://p1.ssl.qhimg.com/t01944013b55f66dfba.png)](https://p1.ssl.qhimg.com/t01944013b55f66dfba.png)

&lt;a name=”然后就是`__destruct`的魔术方法调用了，即使反序列化失败，但是还是会触发cleanup，来进行清理，所以也就可以触发`__destruct`的魔术方法了” class=”reference-link”&gt;然后就是`__destruct`的魔术方法调用了，即使反序列化失败，但是还是会触发cleanup，来进行清理，所以也就可以触发`__destruct`的魔术方法了

[![](https://p2.ssl.qhimg.com/t017cb23b952abc71df.png)](https://p2.ssl.qhimg.com/t017cb23b952abc71df.png)

还有就是当`__wakeup`里面出现了zend级别的错误，`__destruct`也不会触发了

[![](https://p2.ssl.qhimg.com/t01bb149a22fe27f466.png)](https://p2.ssl.qhimg.com/t01bb149a22fe27f466.png)

所以我们也就可以适当的利用unserialize的报错来即执行了`__destruct`，但是又不执行后面的代码

<code class="lang-php">&lt;?php<br>
class A`{`<br>
public $ttt;<br>
function __destruct()`{`<br>
echo "destruct";<br>
`}`<br>
`}`</code>

unserialize(‘a:2:`{`i:0;O:1:”A”:1:`{`s:3:”ttt”;N;`}`i:1;O:3:”PDO”:0:`{``}``}`’);<br>
readfile(“/etc/passwd”);<br>
?&gt;

[![](https://p3.ssl.qhimg.com/t0135510ed6cc4882f4.png)](https://p3.ssl.qhimg.com/t0135510ed6cc4882f4.png)

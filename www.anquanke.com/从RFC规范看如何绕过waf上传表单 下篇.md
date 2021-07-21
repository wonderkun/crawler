> 原文链接: https://www.anquanke.com//post/id/242583 


# 从RFC规范看如何绕过waf上传表单 下篇


                                阅读量   
                                **251913**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01bed46626027838f2.png)](https://p4.ssl.qhimg.com/t01bed46626027838f2.png)

作者：donky16[@360](https://github.com/360)云安全

本文主要讨论，利用waf和后端程序对multipart/form-data的解析差异，造成对waf的bypass。

背景介绍和解析环境见[从RFC规范看如何绕过waf上传表单 上篇](https://www.anquanke.com/post/id/241265)



## 详细解析

`1. Content-Type`和`2. Boundary`部分见上篇

### <a class="reference-link" name="3.%20Content-Disposition"></a>3. Content-Disposition

对于multipart/form-data类型的数据，通过分隔行分隔的每一部分都必须含有Content-Dispostion，其类型为form-data，并且必须含有一个name参数，形如`Content-Disposition: form-data; name="name"`，如果这部分是文件类型，可以在后面加一个filename参数，当然filename参数是可选的。

#### <a class="reference-link" name="%E7%A9%BA%E6%A0%BC"></a>空格

经常和waf打交道的都知道，随便一个空格，可能就会发生奇效。对于Content-Disposition参数，测试在四个位置加任意的空格。
<li>a. 原本有空格的位置`Content-Disposition: form-data;    name="key1"; filename="file.php"``Content-Disposition: form-data;   name="key1"   ;   filename="file.php"`
`Content-Disposition:    form-data;    name="key1"   ;   filename="file.php"`
`Content-Disposition: form-data  ;     name="key1"   ;   filename="file.php"`
前三种类型，php和flask解析都是准确的。
[![](https://p0.ssl.qhimg.com/t0128514804a68fe6af.png)](https://p0.ssl.qhimg.com/t0128514804a68fe6af.png)
但是第四种对于`Content-Disposition: form-data   ;`来说，php解析准确，认为其是正 常的multipart/form-data数据，然而flask解析失败了，并且直接返回了500（：
[![](https://p1.ssl.qhimg.com/t0195cb5f53aa531c59.png)](https://p1.ssl.qhimg.com/t0195cb5f53aa531c59.png)
这里flask处理Content-Disposition的方式是和request_header中Content-Type是一致的，经过了`r",\s*([^;,\s]+)([;,]\s*.+)?"`匹配，由于空格导致后面的name和filename无法解析，只不过这种情况会返回500。对于后续的name和filename得解析也是和request_header中Content-Type一致，后面匹配中的group作为rest进行后续的正则匹配，匹配用到的正则，是上文第2部分（Boundary）双引号中的`_option_header_piece_re`。
</li>
<li>b. 参数名和等于号之间`Content-Disposition: form-data; name  ="key1"; filename="file.php"``Content-Disposition: form-data; name="key1"; filename   ="file.php"`
flask正常解析
[![](https://p1.ssl.qhimg.com/t010347a617fc527662.png)](https://p1.ssl.qhimg.com/t010347a617fc527662.png)
php解析失败，不仅第一部分数据无法解析，第二部分非文件参数也解析失败，可见php解析会将`name=`/`filename=`作为关键字匹配，当发现`name=`和`filename=`都不存在时，直接不再解析了，这与boundary的解析是不一样的，使用`Content-Type: multipart/form-data; boundary =I_am_a_boundary`一样可以正常解析处boundary的值。
[![](https://p4.ssl.qhimg.com/t01bab06ee237442d82.png)](https://p4.ssl.qhimg.com/t01bab06ee237442d82.png)
如果我们不在name和等于号之间加空格，只在filename和等于号之间加空格，形如`Content-Disposition: form-data; name="key1"; filename  ="file.txt"`，那么php会将这种解析会非文件参数。
[![](https://p1.ssl.qhimg.com/t0119d7ab414d2d020c.png)](https://p1.ssl.qhimg.com/t0119d7ab414d2d020c.png)
如果waf支持这种多余空格形式的写法，那么将会把这种解析为文件类型，造成解析上的差异，waf错把非文件参数当作文件，那么可能绕过waf的部分规则。
</li>
- c. 参数值和等于号之间`Content-Disposition: form-data; name=  "key1"; filename=  "file_name"`php和flask解析正常。
<li>d. 参数值中这个没啥注意的，flask会按照准确的name解析。[![](https://p2.ssl.qhimg.com/t015d83d6fae24cd3a3.png)](https://p2.ssl.qhimg.com/t015d83d6fae24cd3a3.png)php会忽略开头的空格，并把非开头空格转化为`_`，具体原因可以看[php-variables](https://www.php.net/manual/zh/language.variables.external.php)。
[![](https://p5.ssl.qhimg.com/t01b1b3cd5f051afd41.png)](https://p5.ssl.qhimg.com/t01b1b3cd5f051afd41.png)
</li>
#### <a class="reference-link" name="%E9%87%8D%E5%A4%8D%E5%8F%82%E6%95%B0"></a>重复参数
<li>a. 重复name/filename参数名php和flask都会取最后一个name/filename，从flask代码来看，存储参数使用了字典，由于具有相同的key=name，所以最后在解析的时候，遇到相同key的参数，会进行参数值的覆盖。[![](https://p0.ssl.qhimg.com/t01d64d54131da81c8a.png)](https://p0.ssl.qhimg.com/t01d64d54131da81c8a.png)这种重复参数名的方式，在下文中将结合其他方式进行绕过waf。
</li>
<li>b. 重复name/filename参数名和参数值接着尝试重复整个form-data的一部分，构造这样一个数据包进行测试。
<pre><code class="lang-h hljs cpp">--I_am_a_boundary
Content-Disposition: form-data; name="key3"; filename="file_name.asp"
Content-Type: text/plain;charset=UTF-8

This_is_file_content.
--I_am_a_boundary
Content-Disposition: form-data; name="key3"; filename="file_name.jsp"
Content-Type: text/plain;charset=UTF-8

This_is_file2_content.
--I_am_a_boundary
Content-Disposition: form-data; name="key5";
Content-Type: text/plain;charset=UTF-8

aaaaaaaaaaaa
--I_am_a_boundary
Content-Disposition: form-data; name="key5";
Content-Type: text/plain;charset=UTF-8

bbbbbbbbbbbb
--I_am_a_boundary--
</code></pre>
对于php来说，和在同一个Content-Disposition中重复name/filename一致，会选取相同name部分中最后一部分。
[![](https://p4.ssl.qhimg.com/t01903af242a4fcbaff.png)](https://p4.ssl.qhimg.com/t01903af242a4fcbaff.png)
对于flask来说，带有filename的，会取第一部分，而且相同name的非文件参数，会将两个取值作为一个列表解析。
[![](https://p2.ssl.qhimg.com/t019e98808faad71257.png)](https://p2.ssl.qhimg.com/t019e98808faad71257.png)
其实这里是httpbin处理后的结果，为了准确看到flask解析结果，需要直接查看`request.form/request.files`。
[![](https://p4.ssl.qhimg.com/t011e9a909756577434.png)](https://p4.ssl.qhimg.com/t011e9a909756577434.png)
使用的是`ImmutableMultiDict`，在`werkzeug/datastructures.py`中定义，可以看到，最终form和files都是把所有multipart数据都获取了，即使具有相同的key。如果我们使用常用的`keys()/values()/item()`函数，都会因为相同key，而只能取到第一个key的值，想获取相同key的所有取值，需要使用`ImmutableMultiDict.to_dict()`方法，并设置参数`flat=True`。
[![](https://p4.ssl.qhimg.com/t0147100cac8d786fe7.png)](https://p4.ssl.qhimg.com/t0147100cac8d786fe7.png)
httpbin就是在[处理](https://github.com/postmanlabs/httpbin/blob/f8ec666b4d1b654e4ff6aedd356f510dcac09f83/httpbin/helpers.py#L142)request.form时，多加了这种处理，导致最后看到两个取值的列表，但是在request.files处理时没有进行`to_dict`。
[![](https://p2.ssl.qhimg.com/t01bf947259b8d5cef7.png)](https://p2.ssl.qhimg.com/t01bf947259b8d5cef7.png)
由此可见，不同的后端程序，实现起来可能会不一样，如果waf在实现时，并没有将所有key重复的数据都解析出来，并且进入waf规则匹配，那么使用重复的key，也会成为很好的绕过waf的方式。
</li>
#### <a class="reference-link" name="%E5%BC%95%E5%8F%B7"></a>引号

上文提到，`_option_header_piece_re`这个正则在flask中也会用来解析Content-Disposition，所以对于name/filename的取值，和boundary取值机制是一样的，加了双引号是`quoted string`，没有双引号的是`token`。

所以主要分析php是如何处理的，首先php在处理boundary时，如果空格开头，那么空格将作为boundary的一部分即使空格后存在正常的双引号闭合的boundary。但是在Content-Disposition中，双引号外的空格是可以被忽略的，当然不使用双引号，参数值两边的空格也会被忽略。

[![](https://p1.ssl.qhimg.com/t01a754a67f07eb72cc.png)](https://p1.ssl.qhimg.com/t01a754a67f07eb72cc.png)

此小段标题`引号`，并没有像上一大段一样使用`双引号`，是因为php不仅支持双引号取值，也支持单引号取值，这很php。

[![](https://p2.ssl.qhimg.com/t018eee6c9c7abcc65e.png)](https://p2.ssl.qhimg.com/t018eee6c9c7abcc65e.png)

flask肯定是不支持单引号的，上面的正则能看出来，单引号会被当作参数值的一部分，这里看了下Java的`commons-fileupload`v1.2的实现`org.apache.commons.fileupload.ParameterParser.java:L76`，在解析参数值的时候也是不支持单引号的。

[![](https://p1.ssl.qhimg.com/t01c873fa200273184e.png)](https://p1.ssl.qhimg.com/t01c873fa200273184e.png)

所以如果waf在multipart解析中是不支持参数值用单引号取值的，对于php而言，出现这种payload就可以导致waf解析错误。

`Content-Disposition: form-data; name='key3; filename='file_name.txt; name='key3'`

支持单引号的会将之解析为``{`"name": "key3"`}``，并没有filename参数，视为非文件参数

不支持单引号的会将之解析为``{`"name": "'key3'", "filename": "'file_name.txt"`}``，视为文件参数，将之后参数值视为文件内容。

这种waf和后端处理程序解析的不一致可能会导致waf被绕过。

此时，还有一个引号的问题没有解决，就是如果出现多余的引号会发生什么，形如`Content-Disposition: form-data; name="key3"a"; filename="file_name;txt"`，上文在boundary的解析中已经看到了结果，name会取`key3`，并忽略之后的内容，即使含有双引号，那么后面的filename内容还能正确解析吗？正好看看flask使用正则和Java/php使用字符解析带来的一些差异。

看一下flask的具体实现`werkzeug/http.py:L402`。

```
result = []
value = "," + value.replace("\n", ",")    # ',form-data; name="key3"aaaa"; filename="file_name.txt"'
while value:
    match = _option_header_start_mime_type.match(value)
    if not match:
        break
    result.append(match.group(1))  # mimetype
    options = `{``}`
    # Parse options
    rest = match.group(2)    # '; name="key3"aaaa"; filename="file_name.txt"'
    continued_encoding = None
    while rest:
        optmatch = _option_header_piece_re.match(rest)
        if not optmatch:
            break
        option, count, encoding, language, option_value = optmatch.groups()    # option_value: "key3"
        ...
        ...
        ... # 省略
        rest = rest[optmatch.end() :]
    result.append(options)
```

使用`_option_header_piece_re`匹配到之后，会继续从下一个字符开始继续进入正则匹配，所以第二次进入正则时，rest为`aaaa"; filename="file_name.txt"`，以a开头就无法匹配中正则了，直接退出，导致filename解析失败，并且name取key3。

[![](https://p4.ssl.qhimg.com/t0174f975f8810e5d6a.png)](https://p4.ssl.qhimg.com/t0174f975f8810e5d6a.png)

Java的代码在上面已经贴出，其中的`terminators=";"`，也就是说当出现双引号时，会忽略`;`，但是当找到闭合双引号时，取值没有结束，会继续寻找`;`，这就导致会一直取到闭合双引号外的`;`才会停止，这和php是不一致的，php虽然后面多余的双引号会影响后续filename取值，但是会在第一次出现闭合双引号时取值结束。

[![](https://p2.ssl.qhimg.com/t01beab6609dffb4984.png)](https://p2.ssl.qhimg.com/t01beab6609dffb4984.png)

对于flask/php来说，如果waf解析方式和后端不相同，也可能会错误判断文件和非文件参数，但是Java后端很难使用，因为对于name的取值会导致后端无法正确获取。但是这个取值特性依旧有用，下文`文件扩展名`将进行介绍。

#### <a class="reference-link" name="%E8%BD%AC%E4%B9%89%E7%AC%A6%E5%8F%B7"></a>转义符号

php和flask都支持参数值中含有转移符号，从上面的`_option_header_piece_re`正则可以看出，和boundary取值一致，flask在`quoted string`类型的参数值中的转义符具有转义作用，在`token`类型中只是一个字符`\`，不具有转义作用。

[![](https://p0.ssl.qhimg.com/t01bfb4115e71960781.png)](https://p0.ssl.qhimg.com/t01bfb4115e71960781.png)

php虽然在`token`类型中，解析和对boundary解析一致，转义符号具有转义作用，但是在解析`quoted string`类型时解析方式和boundary竟然不一样了，解析boundary时，转义符为一个`\`字符不具有转义作用，所以`boundary="aa\"bbb"`会被解析为`aa\`，而在Content-Disposition中，转义符号具有转义作用。

[![](https://p5.ssl.qhimg.com/t01e6e29f8e6de753f9.png)](https://p5.ssl.qhimg.com/t01e6e29f8e6de753f9.png)

和上文提到的php解析单引号的方式一样，存在这么一种payload

`Content-Disposition: form-data; name="key3\"; filename="file_name.txt; name="key3"`

[![](https://p5.ssl.qhimg.com/t012fc7e251547c8c11.png)](https://p5.ssl.qhimg.com/t012fc7e251547c8c11.png)

flask/php将之解析为非文件参数，并且根据多个重复的name/filename解析机制，最终解析结果``{`"name": "key3"`}``

如果waf并不支持转义符号的解析，只是简单的字符匹配双引号闭合，那么解析结果为``{`"name": "key3\\", "filename": "\"file_name.txt"`}``，视为文件参数，将之后参数值视为文件内容，造成解析差异，导致waf可能被绕过。

上文提到php可以使用单引号取值，在单引号中增加转义符的解析方式会和双引号不同，具体可参考[php单引号和双引号的区别与用法](https://www.cnblogs.com/youxin/archive/2012/02/13/2348551.html)。

#### <a class="reference-link" name="%E6%96%87%E4%BB%B6%E6%89%A9%E5%B1%95%E5%90%8D"></a>文件扩展名

前文主要提出一些mutlipart整体上的waf绕过，在源站后端解析正常的情况下让waf解析失败不进入规则匹配，或者waf解析与后端有差异，判断是否为文件失败，导致规则无法匹配，或者filename参数根本没有进入waf的规则匹配。无论是在CTF比赛中还是在实际渗透测试中，如何绕过文件扩展名是大家很关注的一个点，所以这一段内容主要介绍，在waf解析到filename参数的情况下，从协议和后端解析的层面如何绕过文件扩展名。

其实这种绕过就一个思路，举个简单的例子`filename="file_name.php"`，对于一个正常的waf来说取到`file_name.php`，发现扩展名为php，接着进行拦截，此处并不讨论waf规则中不含有php关键字等等waf规则本身不完善的情况，我们只有一个目标，那就是waf解析出的filename不出现php关键字，并且后端程序在验证扩展名的时候会认为这是一个php文件。

从各种程序解析的代码来看，为了让waf解析出现问题，干扰的字符除了上文说的引号，空格，转义符，还有`:;`，这里还是要分为两种形式的测试。
<li>a. `token`形式`Content-Disposition: form-data; name=key3; filename=file_name:.php``Content-Disposition: form-data; name=key3; filename=file_name'.php`
`Content-Disposition: form-data; name=key3; filename=file_name".php`
`Content-Disposition: form-data; name=key3; filename=file_name\".php`
`Content-Disposition: form-data; name=key3; filename=file_name .php`
`Content-Disposition: form-data; name=key3; filename=file_name;.php`
前五种情况flask/Java解析结果都是一致的，会取整体作为filename的值，都是含有php关键字的，这也说明如果waf解析存在差异，将特殊字符直接截断取值，会导致waf被绕过。
最后一种情况，flask/Java/php解析都会直接截断，filename=file_name，这样后端获取不了，无论waf解析方式如何，无法绕过。
对于php而言，前三种会如flask以一样，将整体作为filename的值，第五种空格类型，php会截断，最终取filename=file_name，这种容易理解，当没出现引号时，出现空格，即认为参数值结束。
[![](https://p4.ssl.qhimg.com/t01ca6a2a4c3cdcdd30.png)](https://p4.ssl.qhimg.com/t01ca6a2a4c3cdcdd30.png)
然后再测试转义符号的时候，出现了从`\`开始截断，并去`\`后面的值最为filename的值，这种解析方式和boundary解析也不相同，当然双引号和单引号相同效果。、
[![](https://p0.ssl.qhimg.com/t01606cfb862ff3ec37.png)](https://p0.ssl.qhimg.com/t01606cfb862ff3ec37.png)
看代码才发现，php并没有把`\`当作转义符号，而是贴心地将filename看做一个路径，并取路径中文件的名称，毕竟参数名是filename啊:)
[![](https://p2.ssl.qhimg.com/t01714ea69faddba4bd.png)](https://p2.ssl.qhimg.com/t01714ea69faddba4bd.png)
所以这个解析方式和引号跟本没关系，只是php在解析filename时，会取最后的`\`或者`/`后面的值作为**文件名**。
[![](https://p1.ssl.qhimg.com/t01b8b26be5e2d5864c.png)](https://p1.ssl.qhimg.com/t01b8b26be5e2d5864c.png)
<ul>
- b. `quoted string`形式
`Content-Disposition: form-data; name=key3; filename="file_name:.php"`

`Content-Disposition: form-data; name=key3; filename="file_name'.php"`

`Content-Disposition: form-data; name=key3; filename="file_name".php"`

`Content-Disposition: form-data; name=key3; filename="file_name\".php"`

`Content-Disposition: form-data; name=key3; filename="file_name .php"`

`Content-Disposition: form-data; name=key3; filename="file_name;.php"`

flask解析结果还是依照`_option_header_piece_re`正则，除第三种filename取file_name之外，其他都会取双引号内整体的值作为filename，转义符具有转义作用。php第三种也会解析出file_name，但是在第四种转义符是具有转义作用的，所以进入上文的`*php_ap_basename`函数时，是没有`\`的，所以其解析结果也会是`file_name".php`，使用单引号的情况和上文`引号`部分分析一致。

[![](https://p5.ssl.qhimg.com/t01d4bba8eb56da0b6c.png)](https://p5.ssl.qhimg.com/t01d4bba8eb56da0b6c.png)

对于Java来说，除第三种情况外，都是会取引号内整体作为filename值，但是第三种情况就非常有趣，上文`引号`部分已经分析，Java会继续取值，那么最后filename取值为`"file_name".php"`。

[![](https://p4.ssl.qhimg.com/t0184f3853895431ec6.png)](https://p4.ssl.qhimg.com/t0184f3853895431ec6.png)

所以对于Java这个异常的特性来说，通常waf会像php/flask那样在第一次出现闭合双引号时，直接取双引号内内容作为filename的取值，这样就可以绕过文件扩展名的检测。

### <a class="reference-link" name="4.%20Content-Type(Body)"></a>4. Content-Type(Body)

[![](https://p3.ssl.qhimg.com/t01a5280cae60c5d8fd.png)](https://p3.ssl.qhimg.com/t01a5280cae60c5d8fd.png)

对于一些不具有编码解析功能的waf，可以通过对参数值的编码绕过waf。

#### <a class="reference-link" name="Charset"></a>Charset

对于Java，可以使用UTF-16编码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fb6a0cf1703bc615.png)

flask可以使用UTF-7编码。

[![](https://p2.ssl.qhimg.com/t01594ef84cfb8908d2.png)](https://p2.ssl.qhimg.com/t01594ef84cfb8908d2.png)

由于Java代码中，会把文件和非文件参数都用`org.apache.commons.fileupload.FileItem`来存储，所以都会进行解码操作，而flask将两者分成了form和files，而且files并没用使用Content-Type中的`charset`进行解码`werkzeug/formparser.py:L564`。

[![](https://p5.ssl.qhimg.com/t01e33237e3c83bc58a.png)](https://p5.ssl.qhimg.com/t01e33237e3c83bc58a.png)

#### <a class="reference-link" name="%E5%85%B6%E4%BB%96"></a>其他

[![](https://p4.ssl.qhimg.com/t014a5d6952e0eb50ed.png)](https://p4.ssl.qhimg.com/t014a5d6952e0eb50ed.png)

RFC7578中写了一些其他form-data的解析方式，可以通过`_charset_`参数指定charset，或者使用`encoded-word`，但是测试的三种程序都没有做相关的解析，很多只是在邮件中用到。

### <a class="reference-link" name="5.%20Content-Transfer-Encoding"></a>5. Content-Transfer-Encoding

[![](https://p4.ssl.qhimg.com/t01260e0d7ed69a0c0f.png)](https://p4.ssl.qhimg.com/t01260e0d7ed69a0c0f.png)

RFC7578明确写出只有三种参数类型可以出现在multipart/form-data中，其他类型`MUST`被忽略，这里的第三种Content-Transfer-Encoding其实也被废弃。

[![](https://p5.ssl.qhimg.com/t01357cdda1bda8a14f.png)](https://p5.ssl.qhimg.com/t01357cdda1bda8a14f.png)

然而在flask代码中发现werkzeug实现了此部分。

[![](https://p3.ssl.qhimg.com/t015b70971a4628d028.png)](https://p3.ssl.qhimg.com/t015b70971a4628d028.png)

也可以使用`QUOTED-PRINTABLE`编码方式。



## 参考链接

[https://github.com/postmanlabs/httpbin](https://github.com/postmanlabs/httpbin)

[https://www.ietf.org/rfc/rfc1867.txt](https://www.ietf.org/rfc/rfc1867.txt)

[https://tools.ietf.org/html/rfc7578](https://tools.ietf.org/html/rfc7578)

[https://tools.ietf.org/html/rfc2046#section-5.1](https://tools.ietf.org/html/rfc2046#section-5.1)

[https://www.php.net/manual/zh/language.variables.external.php](https://www.php.net/manual/zh/language.variables.external.php)

[https://www.cnblogs.com/youxin/archive/2012/02/13/2348551.html](https://www.cnblogs.com/youxin/archive/2012/02/13/2348551.html)

[https://xz.aliyun.com/t/9432](https://xz.aliyun.com/t/9432)

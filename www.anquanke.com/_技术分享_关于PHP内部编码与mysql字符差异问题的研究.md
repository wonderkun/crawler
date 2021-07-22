> 原文链接: https://www.anquanke.com//post/id/84967 


# 【技术分享】关于PHP内部编码与mysql字符差异问题的研究


                                阅读量   
                                **145496**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p1.ssl.qhimg.com/t01786ba30f1853d1b7.png)](https://p1.ssl.qhimg.com/t01786ba30f1853d1b7.png)**

****

**作者：**[**bendawangs**](http://bobao.360.cn/member/contribute?uid=323662175)

**稿费：500RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**0x01 引入**



最近稍稍研究了下关于PHP的内部编码的问题，以及mysql的字符差异的问题，分享下心得，如果有误请大家及时指正。

至于为什么要介绍mysql字符差异问题，是因为普遍将其原因归纳于PHP编码与mysql的UTF-8编码不统一，但实际上这个只是mysql单方面的原因而与PHP的编码方式无关。

另外本文不涉及编码的具体方式。

先引入如下代码：

```
&lt;?php
$m="可";
echo strlen($m);  
?&gt;
```

问这里输入几？2还是3呢？

不多废话直接开始测试下就知道了，截图如下：

[![](https://p1.ssl.qhimg.com/t016374ccf02fa99b72.png)](https://p1.ssl.qhimg.com/t016374ccf02fa99b72.png)

PS：enca是linux下一款用于探测和修改文件编码方式的软件

可以看到，在文件的编码方式为UTF-8的时候，代码输出为3，而文件编码为GB2312的时候，代码输入为2。

PS:平时linux和windows下文本文件默认都是以UTF-8的形式保存   

也就是说，这里这个该文件的编码类型决定了文件中那个 "可" 字的长度。那么原因是什么呢？

<br>

**0x02 关于PHP的编码问题**

**2.1 PHP内部编码**

这里需要说明一下，首先PHP内部的字符串只是一个字节序列，并不会保留任何的编码信息，所以可以说说PHP是不关心编码的，即PHP里一个字符就是一字节。

所以你的字符串啊，各种来源的输入啊之类的PHP都是可以识别的，至于能不能显示，能不能处理又是另一回事了。因为无论你在文本编辑器中保存了什么、或是从数据库中得到它，它已经被编码了，就是说已经被决定了占用了几个字节了，在传递给PHP的时候就已经是以字节的形式传递过去了。

所以说对于PHP来说，一个字符及对应一个字节，换言之，我们可以通过控制数据指针访问到字符串的每一个字节。

而PHP对编码的唯一要求就是它要能够保存为ascii的形式，因为它需要从中获取指令。但是这一点我们并不需要担心，因为大部分编码方式都向下兼容ascii。但是也有例外，比如UTF-16就不兼容ascii，所以我们不能用UTF-16来保存PHP源代。

PS:UTF即 Unicode Translation Format ，即把Unicode转作某种格式的意思。标准的UNICODE编码又称UTF-16。所以UTF-16也就可以理解为通常意义上说的UNicode编码。非要说二者区别的话，也就是UTF-16的本质算是一种存储方式吧。

如下图做个测试，我们以UNICODE保存PHP源码，然后访问如下图： 

[![](https://p5.ssl.qhimg.com/t01a0528936063a205f.png)](https://p5.ssl.qhimg.com/t01a0528936063a205f.png)

发现PHP都没有被解析直接返回了源码。即PHP源文件已经无法被正常解析了。也就是说我们可以将PHP源代码保存为任何ASCII兼容的编码，因为如果编码的前128个代码点与ASCII相同，那么就意味着PHP可以解析它。或是说PHP支持该编码方式。

PS:一个语言支持某个编码方式是什么意思？例如，Javascript支持Unicode，事实上，Javascript中的任何字符串都是Unicode编码的，即不能在Javascript中有一个不是Unicode编码的字符串。其他语言只是编码感知。在内部，它们以特定的编码，通常是Unicode存储字符串。反过来，他们需要被告知或尝试检测与文本有关的一切的编码。他们需要知道保存源代码的编码，他们应该读取的文件的编码，要输出文本的编码，并且它们根据需要转换编码，其中一些表现形式是作为中间人的Unicode，很显然的代表就是python。

那么到这儿我们就可以理解引入部分那个例子了。 

因为对于PHP来说，每一个字符就是一个字节，所以strlen和内部编码无关，因此它将计算字节数，而不是字符数。所以该文件的编码类型决定了文件中那个 “可” 字所占用的字节数，从而决定了strlen计算的数目。 

所以这些“可读的字符”的东西是我们人自己的事情，但是PHP语言其实并不在乎。

**2.2 关于PHP的乱码问题**

有了上面的知识，那么我们可以发现其实PHP内部的编码方式是什么并不是问题关键，问题的关键在于内外内外编码方式的差异。因为PHP不试图解释，转换，编码或以其他方式干扰获取到的字节序列。 该文件甚至可以包含二进制数据或是PHP内部编码并不支持的UNICODE编码的文件，PHP不在乎这些。 

但内部和外部编码必须匹配，譬如我们的汉字要想输入在html页面上，需要设置meta或是用header，将输出的编码方式设置位支持汉字的编码方式。 

所以乱码问题总结就是一个，内部编码与外部编码差异。所以最简单的解决方案是啥？如果是正常情况下使用时：

将PHP的内部编码设置为UTF-8。

将所有源文件保存为UTF-8。

使用UTF-8作为输出编码（不要忘记发送合适的内容类型头）。

将数据库连接设置为使用UTF-8（在MySQL中为SET NAMES UTF8）。

如果可能的话配置一切编码为UTF-8。

PS:这里为啥是UTF-8而不是别的？因为就我查阅的资料来看，它可以表示所有Unicode字符，因此可以取代所有现有的7位和8位编码，并且因为它与ASCII是二进制兼容的，即每个有效的ASCII字符串也是一个有效的UTF-8字符串。

这里再提及一下关于PHP中设置编码的函数，对单个字符串编码的函数就不赘述了，这里只说常用的配置整体环境编码的iconv_set_encoding，过去常用这个来配置默认编码方式:

```
bool iconv_set_encoding ( string $type , string $charset )
type 的值可以是以下其中任意一个：
    input_encoding
    output_encoding
    internal_encoding
```

对应与PHP.ini中的 iconv.input_encoding 、iconv.output_encoding、iconv.internal_encoding 。 

但是由于上述三个在PHP5.6之后就已经废弃，三者被统一被default_charset代替，所以没必要再介绍了，而且现在大部分PHP环境的都是5.6以上了。 

所以就这里说说default_charset，即默认编码方式，简单来说就是在  Content-type：xxxx  中输出的默认的字符编码，设置了这个，Content-type 就会是设置的值。默认情况下是ISO8859-1，通常叫做Latin-1。但通常我们都会修改为UTF-8。

<br>

**0x03 MYSQL的UTF-8编码与字符差异**

**3.1 MYSQL的UTF-8编码**

为什么这里要单挑出UTF-8来讲，因为在MYSQL中除了UTF-8编码，其他编码都和普通一样没有赘述的必要。 

MySQL的UTF-8实际上是完整的UTF-8字符集的大部分实现，而非完整实现。具体来说，MySQL的UTF-8数据编码最多使用3个字节，而编码完整的UTF-8字符集需要4个字节。所以如果需要支持例如星形符号等需要四字节编码的字符，MySQL的UTF-8就无力了。但是从MySQL 5.5.3起，增加了对utf8mb4字符集的支持，每个字符使用最多4个字节，从而支持完整的UTF-8字符集。因此，如果使用MySQL 5.5.3或更高版本，一般设置编码为utf8mb4而不是UTF-8。 

以上便是关于MYSQL的UTF-8编码的简介。

**3.2 MYSQL的字符差异问题**

实际上这个在HITCON 2016的babytrick题目最后用到了这个，但是可能相对来说更关注__wakeup失效的漏洞了，关于最后的绕过的解释很多WP都把原因归为这里PHP不是UTF-8，而对应的MYSQL执行了mysql_query("SET names utf8")操作，所以产生的MYSQL字符差异。 

但是就通过上述关于PHP内部编码的分析，我们可以知道，其实这里和PHP内部编码没有关系的，而且题目并没有明确的地方有说明PHP的编码方式。但是问题关键还是在这个问题上，无论PHP是什么编码，根据之前的分析，都不会影响到MYSQL。这样光说也说不清出，直接看下面的例子：

```
&lt;?php
$con = mysql_connect('localhost','root','');
mysql_query("set names utf8");
mysql_select_db("ctf");
if(stripos($_GET['name'],'bendawang')!==false)`{`
    $name = 'GET OUT!';
`}`
else`{`
    $name=$_GET['name'];
`}`
$sql = "select * from admin where username='$name'";
$result = mysql_query($sql);
$num = mysql_num_rows($result);
if($num&gt;0)`{`
    echo '&lt;h1&gt;Success!&lt;/h1&gt;';
    print_r(mysql_fetch_array($result));
`}`
else`{`
    echo "GET OUT!";
`}`
?&gt;
```

这是admin的表结构 ：

[![](https://p0.ssl.qhimg.com/t0135db1907d477dc8b.png)](https://p0.ssl.qhimg.com/t0135db1907d477dc8b.png)

我们通过某种方式提前知道了admin表里面有一条记录的username字段值为Bendawang，但是我们要想办法绕过stripos的检测。 

先试一试如下： <br>

[![](https://p4.ssl.qhimg.com/t010401836b0d8f859b.png)](https://p4.ssl.qhimg.com/t010401836b0d8f859b.png)

果然不行，那么我们试试这个。

[![](https://p1.ssl.qhimg.com/t01a52316b21a982f08.png)](https://p1.ssl.qhimg.com/t01a52316b21a982f08.png)

发现成功绕过并且得到结果了。 

那么这是什么原因呢？真的是因为PHP和MYSQL的编码方式的差异吗？ 

此时，我们可以查看下此时执行的mysql日志 <br>

[![](https://p3.ssl.qhimg.com/t0143e2633c7b351e84.png)](https://p3.ssl.qhimg.com/t0143e2633c7b351e84.png)

能够看出实际上PHP还是把 À（ utf-8 bytes为 %C3%80 ）传过去了，所以说实际上这里和PHP的编码并没有关系，那么也就是说这个就只是单纯的mysql的内部的问题。<br>我们再换一种验证方式。 现在，我们清空admin表再往表里插上这样两条数据如下：

```
insert into admin values(unhex('62656E646177616E67'),'1'),(unhex('62656E64C38077616E67'),'2');
```

其中

```
unhex('62656E646177616E67')=bendawang
unhex('62656E64C38077616E67')=bendÀwang
```

插入完成后如下图： 

[![](https://p0.ssl.qhimg.com/t0108ff13bb35385010.png)](https://p0.ssl.qhimg.com/t0108ff13bb35385010.png)

现在我么来执行这么几条指令来观察下： 

[![](https://p0.ssl.qhimg.com/t01a5d067427a7fd92f.png)](https://p0.ssl.qhimg.com/t01a5d067427a7fd92f.png)

不知道大家看出蹊跷来没有，在查询的时候mysql默认 bendawang 和 bendÀwang 是等效的，但是如果真的相比较却又是不同的。 

就好比PHP的弱类型比较一样，也可以理解为MYSQL一种牺牲安全性的人性化设计，考虑到不同国家的编码方式不一样。 

就好比你在浏览器里面输入 [http://www。baidu。com](https://publish.adlab.corp.qihoo.net:8360/contribute/edit?id=2457) 仍然可以访问到[http://www.baidu.com](http://www.baidu.com/)一样。

所以这里只是mysql单方面的问题。

然后我总结了一下可以这样利用的MYSQL字符。如下（重复就没有整理了）：
<td width="312" valign="top" align="center">Ç</td><td width="312" valign="top" align="center">c</td>
<td width="312" valign="top" align="center">È</td><td width="312" valign="top" align="center">e</td>
<td width="312" valign="top" align="center">Ì</td><td width="312" valign="top" align="center">i</td>
<td width="312" valign="top" align="center">Ñ</td><td width="312" valign="top" align="center">n</td>
<td width="312" valign="top" align="center">Ò</td><td width="312" valign="top" align="center">o</td>
<td width="312" valign="top" align="center">Š</td><td width="312" valign="top" align="center">s</td>
<td width="312" valign="top" align="center">Ù</td><td width="312" valign="top" align="center">u</td>
<td width="312" valign="top" align="center">ý</td><td width="312" valign="top" align="center">y</td>
<td width="312" valign="top" align="center">Ž</td><td width="312" valign="top" align="center">z</td>

**3.3 补充**

最后还要说明下我们在刚开始插入数据的时候执行的语句是

```
insert into admin values(unhex('62656E646177616E67'),'1'),(unhex('62656E64C38077616E67'),'2');
```

但为什么不执行下面这个语句呢？

```
insert into admin values('bendawang','1'),('bendÀwang','2')
```

因为我的演示环境的windows下的mysql的shell环境，对于不识别的字符统统换成问号 ?(0x3F)，也就是说我们所输入的 À 就不再是 %C3%80 了。如下： 

[![](https://p0.ssl.qhimg.com/t0122e80844e2e71c3f.png)](https://p0.ssl.qhimg.com/t0122e80844e2e71c3f.png)

但是如果换成linux下的mysql的shell环境就可以用第二种插入方式，因为linux下mysql的shell默认是utf-8的编码，如下：

[![](https://p5.ssl.qhimg.com/t011f4e914ba9c3243c.png)](https://p5.ssl.qhimg.com/t011f4e914ba9c3243c.png)

这也是编码方式的问题。

**<br>**

**0x04 参考资料**

[http://kunststube.net/encoding/ ](http://kunststube.net/encoding/)

[http://www.i18nqa.com/debug/utf8-debug.html ](http://kunststube.net/encoding/)

[http://stackoverflow.com/questions/7861358/strange-characters-in-database-text-%C3%83-%C3%83-%C2%A2-%C3%A2-%E2%82%AC ](http://stackoverflow.com/questions/7861358/strange-characters-in-database-text-%C3%83-%C3%83-%C2%A2-%C3%A2-%E2%82%AC)

[https://vigilance.fr/vulnerability/MySQL-SQL-injection-via-multi-byte-characters-5885](http://stackoverflow.com/questions/7861358/strange-characters-in-database-text-%C3%83-%C3%83-%C2%A2-%C3%A2-%E2%82%AC)

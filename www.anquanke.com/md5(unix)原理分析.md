> 原文链接: https://www.anquanke.com//post/id/82881 


# md5(unix)原理分析


                                阅读量   
                                **111631**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01b58ab9fba8b82710.jpg)](https://p4.ssl.qhimg.com/t01b58ab9fba8b82710.jpg)

看到t00ls上有同学在问这个问题: [https://www.t00ls.net/thread-31914-1-1.html](https://www.t00ls.net/thread-31914-1-1.html)

里面有说到通过注入拿到网站的密码,加密方式是md5(unix),破解不了于是很尴尬。我们通过他文中给出的hash入手,来分析一下unix(md5)的原理与破解方法。

目标hash:

```
$1$Dx1bONFt$Hsrx102ek28d03B5dqgAv/
```

实际上,我们要先明白一点。无论是何种哈希,说到底是摘要算法,是将任意长度的任意字节对应成固定长度的一段字节。

这段摘要字节因为包含很多不易显示的字符,所以人们通常使用hex或者base64等类似方法将它转换成可见字符显示出来。

所以这个hash也一样,我们用$将hash切割成三部分:”1“、”Dx1bONFt“、”Hsrx102ek28d03B5dqgAv/“ ,给这三部分分别起个名字:magic、salt、password。

其中password实际上就是哈希完成后的字符串,再通过类似base64的算法转换成了可见字符串。

**Magic**

magic是表明这一段哈希是通过什么算法得到的,对应关系如下:



```
$0 = DES
$1 = MD5
$2a(2y) = Blowfish
$5 = SHA-256
$6 = SHA-512
```

目标hash的magic==1,说明是md5加密。

当然内部实现不会是单纯单次md5,但总体来说是以MD5为hash函数,通过多次计算得到的最终值。

类似,这个是sha-256的哈希(明文 admin):





```
$5$DnnkiE71Scb5$lHT.SBfgQKoiTi8cF.cbuxlZ9ZBVFG8CGDxh8CpgPe8
```

这个是sha-512的哈希(明文 admin):





```
$6$I7iRFjXdW9rZA2$/4WJ35KCqtrfc3BFmoargIm8WiKhY5cSBuJIb7ItjO0I7Dj99ZVIPZ3fgKvxaDgZqrWNWwL5aSVwQUkd8D7LT0
```

对比发现,magic值确实不同。除了通过magic来判断密文的加密方式以外,通过哈希的长度也可以判断。比如原哈希Hsrx102ek28d03B5dqgAv/,我们可以用以下代码来看看其长度:





```
php -r "echo strlen(base64_decode('Hsrx102ek28d03B5dqgAv/'));"
```

[![](https://p1.ssl.qhimg.com/t014598ff060046fef4.jpg)](https://dn-leavesongs.qbox.me/content/uploadfile/201511/20491446888251.jpg)

可见结果为16,正是md5的摘要的长度(hex后长度为32),这样也能佐证这个哈希的加密方式为md5。

**Salt**

salt是此次哈希的盐值,长度是8位,超过8的后面的位数将不影响哈希的结果。

在正常情况下,进行加密的时候,这个盐值是随机字符串,所以说其实这个哈希:



```
$1$Dx1bONFt$Hsrx102ek28d03B5dqgAv/
```

我们可以类比为



```
1ecaf1d74d9e936f1dd3707976a800bf:Dx1bONFt
```

这个值1ecaf1d74d9e936f1dd3707976a800bf也不是我胡编的,是将原hash用base64解码后再转换为hex得到的。

而实际上原hash并不是base64编码,只是用类似base64编码的一种算法。这里用base64举例,具体算法后面会讲到

所以很多同学一看到$1$xxx$abcdef这样的密码就懵逼了,其实完全不必,你可就把他理解为abcdef:xxx。

**Password**

password就是加密完成后得到的hash。

我这里给出其php实现的具体算法:



```
namespace Md5Crypt;
class Md5Crypt 
`{`
    static public $itoa64 = './0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'; 
            // [a-zA-Z0-9./]
    static protected function to64($v, $n) 
    `{`
        $itoa64 = self::$itoa64;
        $ret = '';
        while(--$n &gt;= 0) `{`
            $ret .= $itoa64`{`$v &amp; 0x3f`}`;   
            $v = $v &gt;&gt; 6;
        `}`
        return $ret;
    `}`
    static public function apache($pw, $salt = NULL) 
    `{`
        $Magic = '$apr1$';
        return self::unix($pw, $salt, $Magic);
    `}`
    static public function unix($pw, $salt = NULL, $Magic = '$1$') 
    `{`
        $itoa64 = self::$itoa64;
        if($salt !== NULL) `{`
            // Take care of the magic string if present
            if(substr($salt, 0, strlen($Magic)) == $Magic) `{`
                $salt = substr($salt, strlen($Magic), strlen($salt));
            `}`
            // Salt can have up to 8 characters
            $parts = explode('$', $salt, 1);
            $salt = substr($parts[0], 0, 8);
        `}` else `{`
            $salt = '';
            mt_srand((double)(microtime() * 10000000));
            while(strlen($salt) &lt; 8) `{`
                $salt .= $itoa64`{`mt_rand(0, strlen($itoa64)-1)`}`;
            `}`
        `}`
        $ctx = $pw . $Magic . $salt;
        $final = pack('H*', md5($pw . $salt . $pw));
        for ($pl = strlen($pw); $pl &gt; 0; $pl -= 16) `{`
           $ctx .= substr($final, 0, ($pl &gt; 16) ? 16 : $pl);
        `}`
        // Now the 'weird' xform
        for($i = strlen($pw); $i; $i &gt;&gt;= 1) `{`   
            if($i &amp; 1) `{`                // This comes from the original version,
                $ctx .= pack("C", 0);   // where a memset() is done to $final
            `}` else `{`                    // before this loop
                $ctx .= $pw`{`0`}`;
            `}`
        `}`
        $final = pack('H*', md5($ctx)); // The following is supposed to make
                                        // things run slower
        for($i = 0; $i &lt; 1000; $i++) `{`
            $ctx1 = '';
            if($i &amp; 1) `{`
                $ctx1 .= $pw;
            `}` else `{`
                $ctx1 .= substr($final, 0, 16);
            `}`
            if($i % 3) `{`
                $ctx1 .= $salt;
            `}`
            if($i % 7) `{`
                $ctx1 .= $pw;
            `}`
            if($i &amp; 1) `{`
                $ctx1 .= substr($final, 0, 16);
            `}` else `{`
                $ctx1 .= $pw;
            `}`
            $final = pack('H*', md5($ctx1));
        `}`
        // Final xform
        $passwd = '';
        $passwd .= self::to64((intval(ord($final`{`0`}`)) &lt;&lt; 16)
                        |(intval(ord($final`{`6`}`)) &lt;&lt; 8)
                        |(intval(ord($final`{`12`}`))),4);
        $passwd .= self::to64((intval(ord($final`{`1`}`)) &lt;&lt; 16)
                        |(intval(ord($final`{`7`}`)) &lt;&lt; 8)
                        |(intval(ord($final`{`13`}`))), 4);
        $passwd .= self::to64((intval(ord($final`{`2`}`)) &lt;&lt; 16)
                        |(intval(ord($final`{`8`}`)) &lt;&lt; 8)
                        |(intval(ord($final`{`14`}`))), 4);
        $passwd .= self::to64((intval(ord($final`{`3`}`)) &lt;&lt; 16)
                        |(intval(ord($final`{`9`}`)) &lt;&lt; 8)
                        |(intval(ord($final`{`15`}`))), 4);
        $passwd .= self::to64((intval(ord($final`{`4`}`) &lt;&lt; 16)
                        |(intval(ord($final`{`10`}`)) &lt;&lt; 8)
                        |(intval(ord($final`{`5`}`)))), 4);
        $passwd .= self::to64((intval(ord($final`{`11`}`))), 2);
        // Return the final string
        return $Magic . $salt . '$' . $passwd;
    `}`
`}`
```





我们可以如下调用这个类,获得elon11:Dx1bONFt的哈希:



```
include_once("php-crypt-md5/library/Md5Crypt/Md5Crypt.php");
$password = "elon11";
$salt = "Dx1bONFt";
echo Md5CryptMd5Crypt::unix($password, $salt);
```

得到的结果其实就是最开始给出的目标哈希 $1$Dx1bONFt$Hsrx102ek28d03B5dqgAv/:

[![](https://p4.ssl.qhimg.com/t0170dc1dbf93f19abf.jpg)](https://dn-leavesongs.qbox.me/content/uploadfile/201511/21851446888254.jpg)

分析一下这个类,你会发现实际上它的核心算法是1002次循环md5,中间再进行一些截断、移位等过程。<br>

在密码学中,对于防范哈希暴力破解的一种方式就是“密钥延伸”,简单来说就是利用多次hash计算,来延长暴力破解hash的时间,比如这里的1002次md5,就等于将单次md5破解时间延长了1002倍。<br>

然而,在当今的计算机速度下,1002次md5,其实速度也是秒速。我用hashcat尝试破解上述hash,

[![](https://p5.ssl.qhimg.com/t0177e7c3bf099498d5.jpg)](https://dn-leavesongs.qbox.me/content/uploadfile/201511/48191446888287.jpg)

7510个字典,仅用1秒不到跑完,速度为18.28k/s。

相对的,现代linux系统使用的hash方法为SHA-512(Unix),算法核心为sha512,我们可以通过cat /etc/shadow来获得之,通过hashcat来跑:

[![](https://p0.ssl.qhimg.com/t01315460fc352751a6.jpg)](https://dn-leavesongs.qbox.me/content/uploadfile/201511/4bee1446888292.jpg)

速度明显降下来了,只有656 words/s

前两天爆出的Joomla注入,获取到的hash值使用的加密方法是Bcrypt + Blowfish 。我们可以利用如下命令来跑这个密码:



```
hashcat --hash-type=3200 --attack-mode=0 joomla.txt less.dict
```

[![](https://p4.ssl.qhimg.com/t018d9601f57ea30985.jpg)](https://dn-leavesongs.qbox.me/content/uploadfile/201511/1d621446888295.jpg)

可见,速度已经降到45 words/s了,7510个密码的字典需要跑2分半才能全部跑完。足以见得joomla密码的安全性。

不过,这却不是最慢的,Minos([https://github.com/phith0n/Minos](https://github.com/phith0n/Minos)) 使用的也是Bcrypt + Blowfish,但我将其cost设置为12。

cost在Blowfish算法中就是延缓其速度,增加破解难度的选项,如果将cost设置为12,生成的hash,破解起来速度可以降到10 words/s:

[![](https://p2.ssl.qhimg.com/t01776f063b1b839257.jpg)](https://dn-leavesongs.qbox.me/content/uploadfile/201511/e8951446888297.jpg)

基本达到这样的速度,就可以满足安全需求了。这样的话,即使黑客拿到密码的hash,跑一万个密码的字典需要用16分钟,极大地增加了密码碰撞的难度。

**开发与渗透中如何生成hash**

那么,这些hash是怎么生成的呢?

我用php举例说明。

生成一个普通的unix(md5),直接用上面给出的源码即可。当然php也有自带的方法可以办到:

生成一个sha512(unix)

```
echo crypt("admin", '$6$12345678');
```

生成一个bcrypt+blowfish(cost=10默认)(joomla的加密方式)

```
echo password_hash("123123", CRYPT_BLOWFISH);
```

生成一个bcrypt+blowfish(cost=12)(minos的加密方式)



```
echo password_hash("123123", CRYPT_BLOWFISH, ["cost" =&gt; 12]);
```

在渗透过程中,我们也可以直接用工具生成这类密码。比如htpasswd工具,以下是生成密码的一些方法:

[<br>![](https://p1.ssl.qhimg.com/t012df3abeb37e7d001.jpg)](https://dn-leavesongs.qbox.me/content/uploadfile/201511/bfd11446888299.jpg)

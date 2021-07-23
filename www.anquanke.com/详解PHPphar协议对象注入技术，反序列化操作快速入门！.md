> 原文链接: https://www.anquanke.com//post/id/162300 


# 详解PHPphar协议对象注入技术，反序列化操作快速入门！


                                阅读量   
                                **164259**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t012a69f18d71b2a351.jpg)](https://p0.ssl.qhimg.com/t012a69f18d71b2a351.jpg)

近日，在BlackHat 2018大会上公布了一种针对PHP应用程序的全新攻击技术。来自Secarma的安全研究员Sam Thomas分享了议题“It’s a PHP unserialization vulnerability Jim, but not as we know it”，利用phar文件会以序列化的形式存储用户自定义的meta-data这一特性，拓展了php反序列化漏洞的攻击面。

该方法在文件系统函数（file_exists（）、is_dir（）等）参数可控的情况下，配合phar://伪协议，可以不依赖unserialize（）直接进行反序列化操作。

**本期安仔课堂，ISEC实验室的王老师为大家详解PHPphar协议对象注入技术。**



## 0X00 PHP反序列化漏洞

PHP中有两个函数serialize()和unserialize()。

### <a class="reference-link" name="serialize()%EF%BC%9A"></a>serialize()：

当在PHP中创建了一个对象后，可以通过serialize()把这个对象转变成一个字符串，保存对象的值方便之后的传递与使用。<br>
测试代码如下：<br>[![](https://p5.ssl.qhimg.com/t016f4b2d555248b3ae.png)](https://p5.ssl.qhimg.com/t016f4b2d555248b3ae.png)<br>
图1

创建了一个新的对象，并且将其序列化后的结果打印出来：

[![](https://p5.ssl.qhimg.com/t01bf9836037b5b6091.png)](https://p5.ssl.qhimg.com/t01bf9836037b5b6091.png)<br>
图2

这里的O代表存储的是对象（object），假如传入的是一个数组，那就是字母a。6表示对象的名称有6个字符。“mytest“表示对象的名称。1表示有一个值。`{`s:4:”test”;s:3:”123”;`}`中，s表示字符串，4表示字符串的长度，“test”为字符串的名称，之后的类似。

### <a class="reference-link" name="unserialize()%EF%BC%9A"></a>unserialize()：

与serialize()对应的，unserialize()可以对单一的已序列化的变量进行操作，将其转换回 PHP 的值。<br>[![](https://p4.ssl.qhimg.com/t0117296119a1e55f1a.png)](https://p4.ssl.qhimg.com/t0117296119a1e55f1a.png)<br>
图3

[![](https://p4.ssl.qhimg.com/t013e0a9923e488ee7a.png)](https://p4.ssl.qhimg.com/t013e0a9923e488ee7a.png)<br>
图4

当使用unserialize()恢复对象时，将调用_wakeup()成员函数。

反序列化漏洞就是当传给unserialize()的参数可控时，可以通过传入一个精心构造的序列化字符串，来控制对象内部的变量甚至是函数。



## 0X01PHP伪协议

PHP带有很多内置URL风格的封装协议，可用于类似fopen()、copy()、file_exists()和fielsize()的文件系统函数。除了这些封装协议，还能通过stream_wrapper_register()来注册自定义的封装协议。



## 0X02phar文件结构和漏洞原理

phar文件有四部分构成：

### <a class="reference-link" name="1.a%20stub"></a>1.a stub

可以理解为一个标志，格式为xxx&lt;?php xxx;**HALT_COMPILER();?&gt;，前期内容不限，但必须以**HALT_COMPILER();?&gt;来结尾，否则phar扩展将无法识别其为phar文件。

### <a class="reference-link" name="2.a%20manifest%20describing%20the%20contents"></a>2.a manifest describing the contents

phar文件本质上是一种压缩文件，其中每个被压缩文件的权限、属性等信息都存放在这一部分中。这部分将会以序列化的形式存储用户自定义的meta-data。 [![](https://p0.ssl.qhimg.com/t01913d3c402a69b708.png)](https://p0.ssl.qhimg.com/t01913d3c402a69b708.png)

图5

### <a class="reference-link" name="3.the%20file%20contents"></a>3.the file contents

被压缩文件的内容。

### <a class="reference-link" name="4.%5Boptional%5D%20a%20signature%20for%20verifying%20Phar%20integrity%20(phar%20file%20format%20only)"></a>4.[optional] a signature for verifying Phar integrity (phar file format only)

签名，放在文件末尾，目前支持的两种签名格式是MD5和SHA1。

[![](https://p4.ssl.qhimg.com/t016fdff990daeec6d0.png)](https://p4.ssl.qhimg.com/t016fdff990daeec6d0.png) 图6

漏洞触发点在使用phar://协议读取文件的时候，文件内容会被解析成phar对象，然后phar对象内的meta-data会被反序列化。

meta-data是用serialize()生成并保存在phar文件中，当内核调用phar_parse_metadata()解析meta-data数据时，会调用php_var_unserialize()对其进行反序列化操作，因此会造成反序列化漏洞。



## 0X03漏洞利用和demo测试

Sam Thomas举例的漏洞主要通过利用魔术方法**destruct或**wakeup构造利用链，但是在实战环境里往往较难找到可以直接通过魔术方法触发的漏洞点。

根据文件结构来构建一个phar文件，php内置了一个Phar类来处理相关操作。

注意：要将php.ini中的phar.readonly选项设置为Off，否则无法生成phar文件。<br>[![](https://p5.ssl.qhimg.com/t015b324796ce921e34.png)](https://p5.ssl.qhimg.com/t015b324796ce921e34.png)<br>
图7

[![](https://p2.ssl.qhimg.com/t01684ca77985e7cbe7.png)](https://p2.ssl.qhimg.com/t01684ca77985e7cbe7.png)<br>
图8

可以明显的看到meta-data是以序列化的形式存储的：

[![](https://p5.ssl.qhimg.com/t01f6a1b7af86099210.png)](https://p5.ssl.qhimg.com/t01f6a1b7af86099210.png)<br>
图9

有序列化数据必然会有反序列化操作，PHP一大部分的文件系统函数在通过phar://伪协议解析phar文件时，都会将meta-data进行反序列化，测试后受影响的函数如下：<br>[![](https://p3.ssl.qhimg.com/t018f14d65764776bc3.png)](https://p3.ssl.qhimg.com/t018f14d65764776bc3.png)<br>
图10

php底层代码处理：<br>[![](https://p5.ssl.qhimg.com/t015c4dc1664dbdbf7d.png)](https://p5.ssl.qhimg.com/t015c4dc1664dbdbf7d.png)<br>
图11

以下举例证明：<br>[![](https://p4.ssl.qhimg.com/t01e654db069c1fd930.png)](https://p4.ssl.qhimg.com/t01e654db069c1fd930.png)<br>
图12

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ef34cee6d9985126.png)<br>
图13

对于其他的函数来说也是可行的： [![](https://p0.ssl.qhimg.com/t01bffc67e2aa631218.png)](https://p0.ssl.qhimg.com/t01bffc67e2aa631218.png)<br>
图14

在文件系统函数的参数可控时，可以在不调用unserialize()的情况下进行反序列化操作。

由于通过反序列化可以产生任意一种数据类型，可联想到PHP的一个漏洞：PHP内核哈希表碰撞攻击(CVE-2011-4885)。在PHP内核中，数组是以哈希表的方式实现的，攻击者可以通过巧妙构造数组元素的key使哈希表退化成单链表(时间复杂度从O(1)=&gt;O(n))来触发拒绝服务攻击。 [![](https://p2.ssl.qhimg.com/t0101a4efa1d01bc87b.png)](https://p2.ssl.qhimg.com/t0101a4efa1d01bc87b.png)

图15

PHP修复此漏洞的方式是限制通过$_GET或$_POST等方式传入的参数数量，但是如果PHP脚本通过json_decode()或unserialize()等方式获取参数，则依然将受到此漏洞的威胁。

漏洞利用思路：构造一串恶意的serialize数据(能够触发哈希表拒绝服务攻击)，然后将其保存到phar文件的metadata数据区，当文件操作函数通过phar://协议对其进行操作的时候就会触发拒绝服务攻击漏洞。

通过如下代码生成一个恶意的phar文件：<br>[![](https://p2.ssl.qhimg.com/t01a50552412cc5b929.png)](https://p2.ssl.qhimg.com/t01a50552412cc5b929.png)<br>
图16

测试效果如下： [![](https://p5.ssl.qhimg.com/t0105a69331c25a31b1.png)](https://p5.ssl.qhimg.com/t0105a69331c25a31b1.png)

图17



## 0X04将phar伪造成其他格式的文件

PHP识别phar文件是通过文件头的stub，即__HALT_COMPILER();?&gt;，对前面的内容或者后缀名没有要求。可以通过添加任意文件头加上修改后缀名的方式将phar文件伪装成其他格式的文件。<br>[![](https://p0.ssl.qhimg.com/t0195fe06d7cbc86034.png)](https://p0.ssl.qhimg.com/t0195fe06d7cbc86034.png)<br>
图18

[![](https://p0.ssl.qhimg.com/t0133d90329449bac4e.png)](https://p0.ssl.qhimg.com/t0133d90329449bac4e.png)<br>
图19

[![](https://p3.ssl.qhimg.com/t012fff3bc216807e68.png)](https://p3.ssl.qhimg.com/t012fff3bc216807e68.png)<br>
图20

可以利用这种方法绕过大部分上传检测。



## 0X05实际利用

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%9D%A1%E4%BB%B6%EF%BC%9A"></a>利用条件：

1.phar文件要能够上传到服务器端。

2.要有可用的魔术方法作为“跳板”。

3.文件操作函数的参数可控，且: / phar等特殊字符没有被过滤。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E7%8E%AF%E5%A2%83%EF%BC%9AWordPress"></a>利用环境：WordPress

WordPress是网络上最广泛使用的cms，这个漏洞在2017年2月份就被报告给了官方，但至今仍未被修补。之前的任意文件删除漏洞也是出现在这部分代码中，同样没有修补。根据利用条件，我们先要构造phar文件。

漏洞核心位于/wp-includes/post.php中的wp_get_attachment_thumb_file方法：<br>[![](https://p5.ssl.qhimg.com/t01c6647eda015ce1f8.png)](https://p5.ssl.qhimg.com/t01c6647eda015ce1f8.png)<br>
图21

可以通过XMLRPC调用wp.getMediaItem方法来实现此功能。<br>[![](https://p4.ssl.qhimg.com/t014b30b34ee48cc3fc.png)](https://p4.ssl.qhimg.com/t014b30b34ee48cc3fc.png)<br>
图22

如果$file是类似于Windows盘符的路径Z:Z，正则匹配就会失败，$file就不会拼接其他东西，此时就可以保证basename($file)与$file相同。

寻找到能够执行任意代码的类方法：<br>[![](https://p2.ssl.qhimg.com/t01e9117b91243f7421.png)](https://p2.ssl.qhimg.com/t01e9117b91243f7421.png)<br>
图23

这个类继承了ArrayIterator，每当这个类实例化的对象进入foreach被遍历的时候，current()方法就会被调用。

由于WordPress核心代码中没有合适的类能够利用，这里利用woocommerce插件中的一个类：<br>[![](https://p0.ssl.qhimg.com/t019318cd367121b372.png)](https://p0.ssl.qhimg.com/t019318cd367121b372.png)<br>
图24

由此构造完成pop链，构建出phar文件：<br>[![](https://p2.ssl.qhimg.com/t01dc51c86839e6d2f0.png)](https://p2.ssl.qhimg.com/t01dc51c86839e6d2f0.png)<br>
图25

[![](https://p5.ssl.qhimg.com/t0165df46f25ccd170a.png)](https://p5.ssl.qhimg.com/t0165df46f25ccd170a.png)<br>
图26

利用函数passthru来执行系统命令whoami。

这个漏洞利用的权限需要有作者权限或更高，这里用一个author。

[![](https://p3.ssl.qhimg.com/t013ffcdc0422b28c73.png)](https://p3.ssl.qhimg.com/t013ffcdc0422b28c73.png)<br>
图27

通过xmlrpc接口上传刚才的文件，文件要用base64编码：<br>[![](https://p2.ssl.qhimg.com/t0178bad2df3bd4b127.png)](https://p2.ssl.qhimg.com/t0178bad2df3bd4b127.png)<br>
图28

[![](https://p1.ssl.qhimg.com/t01e55896675126ad60.png)](https://p1.ssl.qhimg.com/t01e55896675126ad60.png)<br>
图29

获得_wponce值，可以在修改页面中获取：<br>[![](https://p0.ssl.qhimg.com/t013c87a00d35b053d1.png)](https://p0.ssl.qhimg.com/t013c87a00d35b053d1.png)<br>
图30

通过发送数据包来调用设置$file的值：<br>[![](https://p4.ssl.qhimg.com/t01cd728125a5d8017c.png)](https://p4.ssl.qhimg.com/t01cd728125a5d8017c.png)<br>
图31

[![](https://p3.ssl.qhimg.com/t016e6843eaf2da76fe.png)](https://p3.ssl.qhimg.com/t016e6843eaf2da76fe.png)<br>
图32

[![](https://p5.ssl.qhimg.com/t01e8487f950da1cc5f.png)](https://p5.ssl.qhimg.com/t01e8487f950da1cc5f.png)<br>
图33

[![](https://p1.ssl.qhimg.com/t01866bcbaae1988cbc.png)](https://p1.ssl.qhimg.com/t01866bcbaae1988cbc.png)<br>
图34

最后通过XMLRPC调用wp.getMediaItem这个方法来调用wp_get_attachment_thumb_file()函数，从而触发反序列化。xml调用数据包如下：<br>[![](https://p2.ssl.qhimg.com/t0153f4fce96ef7cdd2.png)](https://p2.ssl.qhimg.com/t0153f4fce96ef7cdd2.png)<br>
图35

[![](https://p2.ssl.qhimg.com/t010b1cc56a626ad453.png)](https://p2.ssl.qhimg.com/t010b1cc56a626ad453.png)<br>
图36

成功执行whoami。



## 0X06防御

1.在文件系统函数的参数可控时，对参数进行严格的过滤；

2.严格检查上传文件的内容，而不是只检查文件头；

3.在条件允许的情况下禁用可执行系统命令、代码的危险函数。

> 安胜作为国内领先的网络安全类产品及服务提供商，秉承“创新为安，服务致胜”的经营理念，专注于网络安全类产品的生产与服务；以“研发+服务+销售”的经营模式，“装备+平台+服务”的产品体系，在技术研究、研发创新、产品化等方面已形成一套完整的流程化体系，为广大用户提供量体裁衣的综合解决方案！
我们拥有独立的技术及产品的预研基地—ISEC实验室，专注于网络安全前沿技术研究，提供网络安全培训、应急响应、安全检测等服务。此外，实验室打造独家资讯交流分享平台—“ISEC安全e站”，提供原创技术文章、网络安全信息资讯、实时热点独家解析等。不忘初心、砥砺前行；未来，我们将继续坚守、不懈追求，为国家网络安全事业保驾护航！

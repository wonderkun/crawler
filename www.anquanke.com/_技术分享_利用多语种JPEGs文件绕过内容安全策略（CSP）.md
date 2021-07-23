> 原文链接: https://www.anquanke.com//post/id/85051 


# 【技术分享】利用多语种JPEGs文件绕过内容安全策略（CSP）


                                阅读量   
                                **89612**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：portswigger.net
                                <br>原文地址：[http://blog.portswigger.net/2016/12/bypassing-csp-using-polyglot-jpegs.html](http://blog.portswigger.net/2016/12/bypassing-csp-using-polyglot-jpegs.html)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p3.ssl.qhimg.com/t01950868a5c439bbbc.png)](https://p3.ssl.qhimg.com/t01950868a5c439bbbc.png)



翻译：WisFree

预估稿费：140RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**前言**



研究表明，如果某个网站使用同一域名下的主机来托管用户上传的图片文件，那么我们就可以通过构建多语言JavaScript/JPEG来绕过网站的内容安全策略（CSP）了。

**技术实现-【**[**PoC传送门**](http://portswigger-labs.net/csp/csp.php?x=%3Cscript%20charset=%22ISO-8859-1%22%20src=%22http://portswigger-labs.net/polyglot/jpeg/xss.jpg%22%3E%3C/script%3E)**】**

首先，我们要分析一下JPEG的格式。前四个字节是一个有效的非ASCII JavaScript变量0xFF 0xD8 0xFF 0xE0。接下来的两个字节代表的是JPEG头的长度。我们可以从下面给出的信息中看到，JPEG头的长度为0x2F2A，如果我们可以把“0x2F2A”改成0x2F 0x2A的话，你可能会觉得此时我们便得到了一个非ASCII变量，之后的数据全部都变成了JavaScript的代码注释。接下来，用空值（00）填充JPEG头剩下的部分。

[![](https://p1.ssl.qhimg.com/t017d6db8ddfd33d105.png)](https://p1.ssl.qhimg.com/t017d6db8ddfd33d105.png)

在JPEG文字注释中，我们可以闭合其中的JavaScript注释，然后为我们的非ASCII JavaScript变量赋值，即提供我们的Payload。然后在JPEG注释的底部再创建另外的多行注释。

[![](https://p5.ssl.qhimg.com/t019a010b7a264f9d56.png)](https://p5.ssl.qhimg.com/t019a010b7a264f9d56.png)

0xFF 0xFE为注释头（comment header），0x00 0x1C代表注释的长度，剩下的数据即为我们的JavaScript Payload（*/=("Burp rocks.")/*）。

接下来，我们需要闭合JavaScript的注释，然后再对图片数据的最后四个字节进行编辑，其中的0xFF 0xD9是图像标记的结尾。文件结尾处的数据如下所示：

[![](https://p4.ssl.qhimg.com/t01634170b67e51323d.png)](https://p4.ssl.qhimg.com/t01634170b67e51323d.png)

这就是我们的多语种JPEG了，虽然它也有一些不完善的地方。如果你没有指定字符集的话，它还是可以正常工作的。但是在火狐浏览器中，如果你指定要使用UTF-8字符集的话，那么浏览器在执行脚本代码的时候将会发生崩溃。所以，为了保证脚本能够正常运行，你需要在脚本标签中指定所用的字符集为ISO-8859-1。需要注意的是，我们的多语种JPEG可以在Safari、火狐浏览器、Edge、以及IE浏览器上运行，而谷歌的Chrome浏览器并不会将JPEG文件当作JavaScript脚本来运行。

点击【[这里](http://portswigger-labs.net/polyglot/jpeg/xss.jpg)】获取这份多语种JPEG图片。

用于执行这个图片文件的JavaScript代码如下所示：

```
&lt;script charset="ISO-8859-1" src="http://portswigger-labs.net/polyglot/jpeg/xss.jpg"&gt;&lt;/script&gt;
```



**文件大小限制**

我曾尝试将这个图片文件作为phpBB账号的头像来上传，但是我发现这个论坛网站对上传的文件有限制：其支持的上传文件大小最大仅为6K，图片尺寸最大为90×90。所以我通过裁剪缩小了这个JPEG图片的尺寸，但是我要怎么才能减少这个JPEG文件中的数据量呢？我发现在JPEG头中，我使用了“/*”，其十六进制为0x2F和0x2A，合起来就是0x2F2A，其代表的长度为12074。这样一来，这部分数据就占用太多空间了，导致我们的JPEG图片大小超过了网站的上传限制。所以我打算查找一下ACSII码表，看看能否找到一些可用的字符组合来减少不必要的数据，并且保持JPEG稳健的有效性。

我所能找到的最小的值为0x9（制表符）和0x3A（冒号），合起来的十六进制值为0x093A（2362），这样就可以大大降低了我们这份文件所占的大小。接下来，创建一个有效的非ASCII JavaScript标签，然后使用JFIF标识符来声明一个变量。最后，我在JFIF标识符的结尾处填充了一个正斜杠“／”（0x2F），并用它来代替原来的空字符（NULL），然后用一个星号来作为版本号。结果如下图所示：

[![](https://p4.ssl.qhimg.com/t015754f670c65e48c5.png)](https://p4.ssl.qhimg.com/t015754f670c65e48c5.png)

接下来，将我们JPEG头的数据补充完整，然后填充空值（NULL），最后注入我们的JavaScript Payload。结果如下图所示：

[![](https://p4.ssl.qhimg.com/t01ffeb927c3f3e4cc9.png)](https://p4.ssl.qhimg.com/t01ffeb927c3f3e4cc9.png)

点击【[这里](http://portswigger-labs.net/polyglot/jpeg/xss_within_header_compressed_small_logo.jpg)】获取这个小尺寸的多语种JPEG图片。

**影响**

****

如果你允许用户上传JPEG格式的文件，而这些上传的文件保存在与你Web应用相同的域名主机之下，那么任何人都可以使用一个多语种JPEG文件（其中注入有恶意的JavaScript脚本代码）来绕过你的内容安全策略（CSP），并实施攻击。

**总结**



总的来说，如果你允许用户向你的网站上传JPEG文件（或者任意类型的文件），那么你最好将这些文件保存在其他域名的主机之中。在验证JPEG文件时，你应该重写其JPEG头，然后移除其中所有的JPEG注释，以此来保证其中没有参杂恶意代码。很明显，你还要重新审查一下你所部属的内容安全策略，确保用于保存这些上传文件的域名不允许执行JavaScript脚本。

[![](https://p0.ssl.qhimg.com/t01510b062d1c5a33e2.png)](https://p0.ssl.qhimg.com/t01510b062d1c5a33e2.png)

如果没有Ange Albertini的帮助，我也不可能完成这篇文章，因为我在创建这个多语种JPEG的时候，一直在参考他的这个JPEG格式结构介绍图【[传送门](https://raw.githubusercontent.com/corkami/pics/master/JPG.png)】。除此之外，我也参考了[Jasvir Nagra](https://twitter.com/jasvir/)那篇关于多语种GIF的博客文章【[传送门](http://www.thinkfu.com/blog/gifjavascript-polyglots)】。

**更新**

[](https://bugzilla.mozilla.org/show_bug.cgi?id=1288361)

[Mozilla](https://bugzilla.mozilla.org/show_bug.cgi?id=1288361)已经在火狐浏览器v51版本中修复了这个问题。



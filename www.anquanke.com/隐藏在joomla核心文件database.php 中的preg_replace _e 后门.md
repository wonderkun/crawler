> 原文链接: https://www.anquanke.com//post/id/83954 


# 隐藏在joomla核心文件database.php 中的preg_replace /e 后门


                                阅读量   
                                **90059**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://blog.sucuri.net/2016/05/unexpected-backdoor-fake-core-files.html](https://blog.sucuri.net/2016/05/unexpected-backdoor-fake-core-files.html)

译文仅供参考，具体内容表达以及含义原文为准

我们通常会在Sucuri Labs或是在博客上写下很多模糊处理方法。有时候也会写一些免费的工具来处理并不免费的代码,我们还有一个在线工具用来帮助用户解码恶意软件。但有些时候我们不清楚恶意软件到底是使用base64、gzinflate、十六进制编码字符串、字符串旋转还是其他常见功能进行加密的。就像是我们今天将会介绍的案例,利用隐藏在joomla核心文件中的后门管理数据库输入。

  我们的工具触发了客户端的一个站点结构异常: /includes/joomla/database/database.php ,其中包含了一个转换成 preg_replace的十六进制编码字符串。

  这为什么会是反常现象呢?让我来解释一下:

· /includes/joomla/database/database.php 并不是Joomla 2.5.8 的一部分(这是在客户端站点运行的一个过时版本)。

· Joomla核心文件不使用这种编码方法。

  如果这是一个由客户端创建来管理Joomla数据库的有效文件,那又是什么样子的呢?这种情况是可能的,我见过太多的CMS核心文件由于客户需求遭到修改,所以最好的办法就是首先核查一下。

[![](https://p3.ssl.qhimg.com/t0196dfee80941dc070.png)](https://p3.ssl.qhimg.com/t0196dfee80941dc070.png)

  前几行和常见的Joomla核心文件没有差别。精彩的评论,getlnstance函数等等。但是之后就有些怪异了。所有的变量都被过度缩进来存储其他变量,这是一种函数吗?这时候就发现问题了。

功能形式

  上下查找之后我发现了一些其他函数、变量、十六进制编码字符串和一个非常奇怪的串联:

[![](https://p5.ssl.qhimg.com/t0135b3e6729387407b.png)](https://p5.ssl.qhimg.com/t0135b3e6729387407b.png)

  我想到的第一件事就是检查它的输出。可能恶意软件就以某种形式藏在那里,基于变量内容,它会存储数据库内容。但是……

[![](https://p1.ssl.qhimg.com/t01dab935ab086ffcc9.png)](https://p1.ssl.qhimg.com/t01dab935ab086ffcc9.png)

  串联在一起只是为了转移注意力,目的是不想让分析师继续深究其中内涵。但是现在还不是时候,除了研究这份疯狂的db代码之外,我还有更重要的事情要做。也许之后我会再回头研究这份代码,这要看它是否还会被用在其他地方。所以现在先留着它然后继续探究吧。

  深入调查之后,我发现了这个:

[![](https://p1.ssl.qhimg.com/t013d4f5571f364df1e.png)](https://p1.ssl.qhimg.com/t013d4f5571f364df1e.png)

最后进行Deobfuscated病毒扫描

  我们看到 $new_stats 由存储在另一变量的函数命名。这样好理解吗?让我们换一种方法来解释:

[![](https://p3.ssl.qhimg.com/t01b3d24cb52400c7cf.png)](https://p3.ssl.qhimg.com/t01b3d24cb52400c7cf.png)

  首先我们看到了一个新的变量:$_state。我将它从另一部分代码中移除,这样可以更清楚地看到到底发生了什么。

  还记得我说过的常用于模糊处理恶意软件的各种函数吗?是的,这个恶意软件编写者几乎在每一行代码中都使用了那些函数!

  这些代码可以获取HTTP_SCHEME 服务器变量内容并且稍作处理,以备后用。这个服务器未在默认情况下登陆,或者使用了模板并且存储空间巨大,又或者是只保存最近登录记录。

  下一步,获取 $_validate 创建的数组,并且使用strtr函数进行 $new_stats 转换。因为我们没有通过 HTTP_SCHEME发送的数组,所以我们也很难说,到底 $new_stats 内容就是之后在preg_replace 执行的恶意代码,还是说有一个全新的代码完全覆盖了变量内容。我希望它是存储在变量中的,那样事情就会变得容易得多。

  正如我前文所讲,最后一行代码是用来执行base64解码内容的转换。

Preg_replace的e注记

  在 Preg_replace 正则表达式中使用的修饰e基于PHP7.0.0(谢谢你!)将会被删除,为了方便查阅,这里摘抄了php.net手册的相关内容:

  如果设置了已否决的修饰符,Preg_replace 会在替换字符中做出常规反应,将它评定为PHP代码,然后用结果替换搜索字符串。单引号、双引号、反斜杠和NULL字符会由反向引用的反斜杠代替。

  发现问题了吗?这是我们修复团队清理受害网站时每天都在寻找的函数。

结论

  日常的恶意软件越来越难被发现。攻击者们将恶意软件存储在数据库里,进行加密,甚至将它编码成核心文件的样子。现在是时候为自己的网站进行了此健康检查了,看看是否有被添加或是被修改的文件,像一个强迫症一样细致一点吧。

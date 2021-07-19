> 原文链接: https://www.anquanke.com//post/id/245534 


# 梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 - 目录穿越专题


                                阅读量   
                                **262126**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t011142a362cc19fa5c.png)](https://p4.ssl.qhimg.com/t011142a362cc19fa5c.png)



## 本系列介绍

> PortSwigger是信息安全从业者必备工具burpsuite的发行商，作为网络空间安全的领导者，他们为信息安全初学者提供了一个在线的网络安全学院(也称练兵场)，在讲解相关漏洞的同时还配套了相关的在线靶场供初学者练习，本系列旨在以梨子这个初学者视角出发对学习该学院内容及靶场练习进行全程记录并为其他初学者提供学习参考，希望能对初学者们有所帮助。



## 梨子有话说

> 梨子也算是Web安全初学者，所以本系列文章中难免出现各种各样的低级错误，还请各位见谅，梨子创作本系列文章的初衷是觉得现在大部分的材料对漏洞原理的讲解都是模棱两可的，很多初学者看了很久依然是一知半解的，故希望本系列能够帮助初学者快速地掌握漏洞原理。



## 服务器端漏洞篇介绍

> burp官方说他们建议初学者先看服务器漏洞篇，因为初学者只需要了解服务器端发生了什么就可以了



## 服务器端漏洞篇 – 目录穿越专题

### <a class="reference-link" name="%E4%BB%80%E4%B9%88%E6%98%AF%E7%9B%AE%E5%BD%95%E7%A9%BF%E8%B6%8A%EF%BC%9F"></a>什么是目录穿越？

目录穿越，很好理解，就是利用某种操作从当前目录穿越到其他任意目录并读取其中的文件的漏洞，这些文件包括源码啊，数据啊，登录凭证等敏感信息之类的，所以说目录穿越漏洞的危害还是不容忽视的

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E7%9B%AE%E5%BD%95%E7%A9%BF%E8%B6%8A%E8%AF%BB%E5%8F%96%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6"></a>利用目录穿越读取任意文件

我们看这样一个场景，我们看到Web中有一张照片，然后我们会在f12中看到这样的前端代码<br>`&lt;img src="/loadImage?filename=218.png"&gt;`<br>
我们看到img标签通过指定src的值来读取图片资源，我们看到src中的URL通过指定参数值为文件名的参数filename来读取图片资源，我们稍微了解一点linux常识的都知道，直接加文件名代表是相对同级目录，这里的基线目录是/var/www/images/，则这张图片资源的绝对路径就是<br>`/var/www/images/218.png`<br>
那么如果我们利用返回上级目录符”..”，比如这样<br>`https://insecure-website.com/loadImage?filename=../../../etc/passwd`<br>
然后我们看一下将它直接拼接到基线路径以后是什么样的<br>`/var/www/images/../../../etc/passwd`<br>
经过三个返回上级操作以后就变成了<br>`/etc/passwd`<br>
这样在img标签加载资源的时候就会将上面文件的内容读取出来，上面讲的是linux系统的，windows还有点不一样，是左斜杠，我们看一下示例<br>`https://insecure-website.com/loadImage?filename=..\..\..\windows\win.ini`

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E7%AE%80%E5%8D%95%E7%9A%84%E7%9B%AE%E5%BD%95%E7%A9%BF%E8%B6%8A"></a>配套靶场：简单的目录穿越

因为加载资源的本质就是GET请求嘛，所以我们随便抓一个包，然后将路径改成img标签src属性的那个格式的，然后利用上面学到的知识进行目录穿越

[![](https://p3.ssl.qhimg.com/t0158fa37711a869d76.png)](https://p3.ssl.qhimg.com/t0158fa37711a869d76.png)

非常简单，真的是有手就行啊，我们可以看到整个文件的内容，还是很恐怖的

### <a class="reference-link" name="%E5%B8%B8%E8%A7%81%E7%9A%84%E7%9B%AE%E5%BD%95%E7%A9%BF%E8%B6%8A%E9%98%B2%E6%8A%A4%E7%9A%84%E7%BB%95%E8%BF%87%E6%96%B9%E6%B3%95"></a>常见的目录穿越防护的绕过方法

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E7%BB%9D%E5%AF%B9%E8%B7%AF%E5%BE%84%E7%BB%95%E8%BF%87%E5%AF%B9%E8%BF%94%E5%9B%9E%E4%B8%8A%E7%BA%A7%E7%9B%AE%E5%BD%95%E7%AC%A6%E7%9A%84%E7%A6%81%E7%94%A8"></a>利用绝对路径绕过对返回上级目录符的禁用

有的应用程序会禁用返回上级目录符，但是换成绝对路径就可以绕过了

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E7%BB%9D%E5%AF%B9%E8%B7%AF%E5%BE%84%E7%BB%95%E8%BF%87%E5%AF%B9%E8%BF%94%E5%9B%9E%E4%B8%8A%E7%BA%A7%E7%9B%AE%E5%BD%95%E7%AC%A6%E7%9A%84%E7%A6%81%E7%94%A8"></a>配套靶场：利用绝对路径绕过对返回上级目录符的禁用

首先我们试一下返回上级目录符

[![](https://p0.ssl.qhimg.com/t014dfc3a68208fcaa7.png)](https://p0.ssl.qhimg.com/t014dfc3a68208fcaa7.png)

提示我们文件不存在？净扯淡，任何linux系统它都有，我们换成绝对路径看看

[![](https://p2.ssl.qhimg.com/t0144de8a6d52558216.png)](https://p2.ssl.qhimg.com/t0144de8a6d52558216.png)

嗯？跟我搁这欲盖弥彰呢？说明我们成功绕过了

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%8F%8C%E5%86%99%E7%BB%95%E8%BF%87%E4%BB%85%E5%AF%B9%E8%BF%94%E5%9B%9E%E4%B8%8A%E7%BA%A7%E7%9B%AE%E5%BD%95%E7%AC%A6%E8%BF%9B%E8%A1%8C%E5%8D%95%E6%AC%A1%E6%B8%85%E9%99%A4"></a>利用双写绕过仅对返回上级目录符进行单次清除

这种情况就是应用程序会正则匹配一次返回上级目录符然后清除，但是仅清除一次，所以我们可以利用双写来进行绕过，就是清除一次以后就正好留下一个

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E5%8F%8C%E5%86%99%E7%BB%95%E8%BF%87%E4%BB%85%E5%AF%B9%E8%BF%94%E5%9B%9E%E4%B8%8A%E7%BA%A7%E7%9B%AE%E5%BD%95%E7%AC%A6%E8%BF%9B%E8%A1%8C%E5%8D%95%E6%AC%A1%E6%B8%85%E9%99%A4"></a>配套靶场：利用双写绕过仅对返回上级目录符进行单次清除

上面我们已经讲的很直白了，废话不多说，直接上截图

[![](https://p2.ssl.qhimg.com/t0179e7d37b8bf619ea.png)](https://p2.ssl.qhimg.com/t0179e7d37b8bf619ea.png)

看到我们有一次成功绕过了

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E4%BA%8C%E6%AC%A1URL%E8%A7%A3%E7%A0%81%E7%BB%95%E8%BF%87%E5%AF%B9%E6%96%9C%E6%9D%A0%E7%9A%84%E8%BF%87%E6%BB%A4"></a>利用二次URL解码绕过对斜杠的过滤

有的应用程序会正则匹配斜杠并且清除，但是如果我们对其再进行一次URL编码，就可能不会被匹配到，但是到了后台以后再进行一次URL解码的时候就可以把斜杠还原出来达到目录穿越的效果

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E4%BA%8C%E6%AC%A1URL%E8%A7%A3%E7%A0%81%E7%BB%95%E8%BF%87%E5%AF%B9%E6%96%9C%E6%9D%A0%E7%9A%84%E8%BF%87%E6%BB%A4"></a>配套靶场：利用二次URL解码绕过对斜杠的过滤

原理讲完了，我们来实践一下，因为题目递进的关系，所以后面的题是无法采用前面的题目的解法解决的，这一点burp做的非常不错

[![](https://p3.ssl.qhimg.com/t0147b74b4eb0598f87.png)](https://p3.ssl.qhimg.com/t0147b74b4eb0598f87.png)

好的，我们又一次成功绕过，大家其实可以把各种情况做成一个小的fuzz字典，这样就不用一个一个手动试了

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%B5%B7%E5%A7%8B%E8%B7%AF%E5%BE%84+%E7%9B%B8%E5%AF%B9%E8%B7%AF%E5%BE%84%E7%BB%93%E5%90%88%E7%BB%95%E8%BF%87%E5%AF%B9%E8%B5%B7%E5%A7%8B%E8%B7%AF%E5%BE%84%E5%8C%B9%E9%85%8D"></a>利用起始路径+相对路径结合绕过对起始路径匹配

有的应用程序只要匹配到以预期的路径开头就不会管后面的了，但是如果我在它后面插入返回上级目录符就可以依然实现目录穿越效果

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%E8%B5%B7%E5%A7%8B%E8%B7%AF%E5%BE%84+%E7%9B%B8%E5%AF%B9%E8%B7%AF%E5%BE%84%E7%BB%93%E5%90%88%E7%BB%95%E8%BF%87%E5%AF%B9%E8%B5%B7%E5%A7%8B%E8%B7%AF%E5%BE%84%E5%8C%B9%E9%85%8D"></a>配套靶场：利用起始路径+相对路径结合绕过对起始路径匹配

原理讲完了，我们就来实践一下

[![](https://p1.ssl.qhimg.com/t0193ab1805123aa72f.png)](https://p1.ssl.qhimg.com/t0193ab1805123aa72f.png)

我们看到了我们再一次绕过了匹配，大家可能会说梨子写的太水了，哎呀，不要在乎那些，能理解漏洞原理就行了，嘻嘻嘻

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%00%E6%88%AA%E6%96%AD%E7%BB%95%E8%BF%87%E5%AF%B9%E5%90%8E%E7%BC%80%E7%9A%84%E6%A3%80%E6%B5%8B"></a>利用%00截断绕过对后缀的检测

在低版本中间件中，利用%00可以用来截断字符串，可以用来绕过对后缀的检测

### <a class="reference-link" name="%E9%85%8D%E5%A5%97%E9%9D%B6%E5%9C%BA%EF%BC%9A%E5%88%A9%E7%94%A8%00%E6%88%AA%E6%96%AD%E7%BB%95%E8%BF%87%E5%AF%B9%E5%90%8E%E7%BC%80%E7%9A%84%E6%A3%80%E6%B5%8B"></a>配套靶场：利用%00截断绕过对后缀的检测

原理讲完了，我们上手练习一下吧

[![](https://p5.ssl.qhimg.com/t0182050982f3fc813f.png)](https://p5.ssl.qhimg.com/t0182050982f3fc813f.png)

我们发现不仅能通过对后缀的检测还能利用%00截断读取到正确的敏感文件

### <a class="reference-link" name="%E5%A6%82%E4%BD%95%E9%98%B2%E6%AD%A2%E7%9B%AE%E5%BD%95%E7%A9%BF%E8%B6%8A%E6%BC%8F%E6%B4%9E%EF%BC%9F"></a>如何防止目录穿越漏洞？

我们看到上面所有的绕过情况都是对路径过滤的不严格导致的，所以我们可以采取以下两种方法来缓解这个漏洞
- 设置白名单，仅允许路径中包含允许的片段或数据类型
- 在经过白名单过滤以后再与基线路径拼接，让路径结构规范化
burp给出了一段防护代码示例

```
File file = new File(BASE_DIRECTORY, userInput);
if (file.getCanonicalPath().startsWith(BASE_DIRECTORY)) {
    // process file
}
```



## 总结

好的，以上就是梨子带你刷burpsuite官方网络安全学院靶场(练兵场)系列之服务器端漏洞篇 – 目录穿越专题的全部内容了，内容不多，但是也是不容小觑的漏洞哦，我们只是以/etc/passwd做示例，但是比它风险更高的文件还有很多很多，如果攻击者获得这些文件，后果不堪设想，大家有什么疑问可以在评论区讨论哦，嘻嘻嘻！

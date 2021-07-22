> 原文链接: https://www.anquanke.com//post/id/84630 


# 【技术分享】从开发角度浅谈CSRF攻击及防御


                                阅读量   
                                **102868**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0197733ff384427fc2.jpg)](https://p3.ssl.qhimg.com/t0197733ff384427fc2.jpg)

**<strong style="text-indent: 32px">什么是CSRF**</strong>

CSRF可以叫做(跨站请求伪造)，咱们可以这样子理解CSRF，攻击者可以利用你的身份你的名义去发送(请求)一段恶意的请求,从而导致可以利用你的账号(名义)去–购买商品、发邮件,恶意的去消耗账户资源,导致的一些列恶意行为.CSRF可以简单分为Get型和Post型两种。

****

**Get型CSRF：**

看到这个名字,很明显是发送GET请求导致的。我这里简单的说一下：GET型的CSRF利用非常简单,通常只要发送一段HTTP请求。简单的说，如果一个网站某个地方的功能，比如(用户修改自己邮箱)是通过GET进行请求修改的话。

如下例:

[http://bobao.360.cn/user.php?id=226&amp;email=226@226.com](http://www.226safe.com/user.php?Id=226&amp;email=226@226.com)  //这里我们可以看出这个网址是通过get型去对用户的邮箱进行修改。后面&amp;email=226@226.com 是关键的地方。当我们发现没有做任何处理之后，我们将可以去构造一段代码。

只要把它email参数后面的值进行修改。。之后构造一个代码,或者直接一串URL发过去(正常人应该不会这样)。如下例：

[http://bobao.360.cn/user.php?id=226&amp;email=226@qq.com](http://www.226safe.com/user.php?Id=226&amp;email=226@226.com)  //只要这个id的用户触发了这URL即可成功修改。攻击者可自行修改id，发送该id用户也可以修改。触发后即可成功修改到这个用户的email。

**POST型CSRF**

POST型CSRF简单来说，通过POST请求去触发代码造成漏洞。还是一样，举个例子 比如在一个教育视频网站平台。在普通用户的眼中，点击网页-&gt;打开试看视频-&gt;购买视频 是一个很正常的一个流程。可是在攻击者的眼中可以算正常，但又不正常的，当然不正常的情况下，是在开发者安全意识不足没有进行处理所造成。攻击者在购买处抓到购买时候网站处理购买(扣除)用户余额的地址。

比如：[http://bobao.360.cn/coures/user/handler/25332/buy.php](http://www.226safe.com/coures/user/handler/buy.php) //通过buy.php处理购买(购买成功)的信息，这里的25532为视频ID

那么攻击者现在构造一个表单(form.html)，如：



```
&lt;form action="http://bobao.360.cn/coures/user/handler/25332/buy.php" method="post"&gt;
      &lt;input type="submit" value="提交" /&gt;
&lt;script&gt; document.forms[0].submit(); &lt;/script&gt; //自动提交
       &lt;/form&gt;
```

构造好form表单后，那么攻击者将form.html上传至一台服务器上，将该页面 如:[http://bobao.360.cn/form.html](http://bobao.360.cn/form.html) 

发送给受害者，只要受害者正在登陆当前教育网站的时候，打开攻击者发送的页面，那么代码则自动触发，自动购买了id为25332的视频。从而导致受害者余额扣除，被攻击者恶意消耗用户余额。如果网站很不严谨，那么只要把id改了，就可以任意的去恶意购买任何视频。消耗受害者的财产，从而导致用户财产安全受影响。



**CSRF的原理**

发现漏洞可利用处-&gt;构造(搭建)搭建代码-&gt;发送给用户(管理员)-&gt;触发代码(发送请求)………

从这个利用的一个流程中，我们可以发现,攻击者仅仅只是做了两处工作.第一处是:发现漏洞利用处，，第二处就是构造利用代码以及发送至用户(管理员)。至于利用，你会发现CSRF与XSS不同，XSS是攻击者自己提交，等待结果，而CSRF呢，是由用户(管理员)自身提交。甚至可以说攻击者只做了构造代码的工作。



**在开发中如何简单防御CSRF(PHP)**

其实防御CSRF有很多种 如:验证码、验证Refer、以及验证token，对特殊参数进行加密。

但是如果使用验证码去避免CSRF的话，那么这样会验证的影响用户的体验，因为用户不会每个操作都去输入验证码(会很烦)。

Refer的话在特殊情况下也是不靠谱的(服务器端出的问题)。

那么目前只有token是被大多网站去使用的。因为可以避免用户体验的问题发生。同样服务器边问题也发生也不会很多。

那么接下来就开始介绍在PHP开发中如何去简单的生成token，避免CSRF。我们可以通过PHP中函数（rand生成随机数+uniqid生成一个唯一id+time时间戳）最后在讲这几个生成的值用md5加密。接下来来说说如何去生产：

首先先开启session会话

```
session_start(); //开启session会话
```

然后我们去随机生成一段值(这个值就是我们的token值) 备注:其实这样子生成不是最严谨的(此次只是大家一起交流。大家可以去尝试各种方式。)

```
$safe226 = md5(time() . uniqid() . rand(1,99999)); //输入一个随机数值
```

我们输出看看

 

[![](https://p3.ssl.qhimg.com/t01983ce0b268be8fe1.png)](https://p3.ssl.qhimg.com/t01983ce0b268be8fe1.png)

接下来，我们需要做的就是把生成出来的token丢进咱们的session里面。

[![](https://p4.ssl.qhimg.com/t011778b898a79d59b7.png)](https://p4.ssl.qhimg.com/t011778b898a79d59b7.png)

 <br>

接下来你们应该知道了，我们验证的其实是我们存到session里面的token是否与用户提交上来的token值一致。如果一致则成功，否则则失败。我们准备一个表单，用于传递用户提交请求的一个token。

```
&lt;input type="hidden" value="&lt;?php echo $_SESSION['226_tonken']; ?&gt;"&gt;
```

[![](https://p3.ssl.qhimg.com/t01c21446cef4d22236.png)](https://p3.ssl.qhimg.com/t01c21446cef4d22236.png)

我们把token提交到test.php里去处理！

其实就是将我们丢进session里面的值丢进隐藏表单里面。当用户提交的时候一起提交过来验证，验证是否与session里面的token相同。

我们来感受下。

[![](https://p2.ssl.qhimg.com/t018ffb392ecb293881.png)](https://p2.ssl.qhimg.com/t018ffb392ecb293881.png)

 <br>

Ok，接下来我们只需要去判断用户传递过来的token值是否和session里面的值一致(这里使用简单判断，其实原理都是一样的。



```
if(isset($_SESSION['226_token']) &amp;&amp; isset($_POST['token']))`{`
if($_SESSION['226_token'] === $_POST['token'])`{`
//这里是验证成功后所写代码 
echo '购买成功';  
`}`else`{`
echo '请勿非法操作!判断是否一致';
`}`
`}`else`{`
echo '请勿非法操作!判断是否存在';
`}`
```

接下来，我们利用下。这里已知道结构。所以直接构造一个表单。

根据代码情况 就是当我们构造的利用代码，没有传递token或者token不一致的时候：



```
&lt;form action="http://127.0.0.1/test/test.php" method="post"&gt;
&lt;input type="submit" value="提交" /&gt;
&lt;/form&gt;
```

[![](https://p0.ssl.qhimg.com/t018170baf7816c0b86.png)](https://p0.ssl.qhimg.com/t018170baf7816c0b86.png)

这里两个打印是在test.php里面打印 没有去掉print_r(无视就好)，当利用时候会发现没有传递token过去。会提示。错误！

接下来我们来看，完全一致的时候。会提示的是什么：

[![](https://p0.ssl.qhimg.com/t0177ebf8d55ccddd52.png)](https://p0.ssl.qhimg.com/t0177ebf8d55ccddd52.png) 

当我们通过验证的时候。你会发现已经验证成功。购买成功。

好了。文章到此结束。希望大家多多交流！！！

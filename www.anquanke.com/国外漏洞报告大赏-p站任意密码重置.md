> 原文链接: https://www.anquanke.com//post/id/248769 


# 国外漏洞报告大赏-p站任意密码重置


                                阅读量   
                                **26322**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：
                                <br>原文地址：[]()

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01c1386faa6dfedeb3.jpg)](https://p0.ssl.qhimg.com/t01c1386faa6dfedeb3.jpg)



## 写在正式文章之前

之前在群里吹水，有师傅想看看h1的漏洞报告，然后我每天睡觉之前也会看国外的漏洞报告并做记录整理，于是决定把笔记整理的笔记发出来分享给各位，看的洞多了，自然知道哪里可能有问题、怎么测试，祝大家早日实现财富自由！<br>
然后这个系列会一直更下去，希望国内的社区也越来越好

## 信息简介

|漏洞名称|漏洞类型|漏洞站点|严重性|报告时间|赏金金额
|------
|Reset any password|忘记密码的弱密码恢复机制|www.pixiv.net|高危|2019-9-30|$1,000



## 概述

当尝试重置密码时，邮箱返回的验证码是六位纯数字，且对于提交次数没有限制，因此可以重置任意用户密码

### <a class="reference-link" name="%E9%AA%8C%E8%AF%81%E6%B5%81%E7%A8%8B"></a>验证流程

在详细讲述复现步骤之前，先了解该站点重置密码的流程：
1. 进入密码重置页面，输入需要重置的账户的电子邮件地址，这里用：[test@test.com](mailto:test@test.com)；Web Server向[test@test.com](mailto:test@test.com)发送一个六位纯数字的验证码，同时返回一个验证码确认页面
1. 跳转到验证码确认页面，提交该数字验证码，服务器确认正确，返回一个输入新密码页面
1. 提交新密码即完成密码重置流程
下图为重置密码的流程图

[![](https://p3.ssl.qhimg.com/t01b627e1f940bddd3d.png)](https://p3.ssl.qhimg.com/t01b627e1f940bddd3d.png)

### <a class="reference-link" name="%E5%A4%8D%E7%8E%B0%E6%AD%A5%E9%AA%A4"></a>复现步骤
1. 先正常进行一此密码重置页面，获得输入新密码页面的url，记录发送的数据包；
1. 进入密码重置页面，输入一个电子右键账户：[test@test.com](mailto:test@test.com)；
<li>进入验证码确认页面后，提交000000数字验证码，使用bp抓包记录，此处的authentication_code对应的就是六位数字验证码，然后drop掉，不发送出去；
<pre><code class="hljs perl">tt=b7296b8d2e8f5bcfa4d749e07ec4a052&amp;mode=reset&amp;authentication_code=000000&amp;new_password_1=123123aaa&amp;new_password_2=123123aaa&amp;submit=%E3%80%80%E5%8F%91%E9%80%81%E3%80%80
</code></pre>
</li>
<li>修改输入新密码提交后发送的数据包，使用bp的爆破功能修改authentication_code的值，不断尝试，直至成功
<pre><code class="hljs apache">tt=b7296b8d2e8f5bcfa4d749e07ec4a052&amp;mode=imput_password&amp;authentication_code=000000&amp;newpassword_1=123456&amp;%80Send%80%80
</code></pre>
</li>
1. 提交成功，使用修改后的密码123456登录
### <a class="reference-link" name="%E6%88%90%E5%9B%A0%E5%88%86%E6%9E%90"></a>成因分析

此漏洞的原因在于，验证邮箱发送的验证码是正确的之后，返回的是下一步的url地址，而未添加新的确认参数，导致绕过了第二步的验证码验证环节，直接在第三步的提交新密码环节进行提交，同时对于authentication_code的提交限制仅仅出现在第二步，因此第三步可以通过爆破的方式尝试出正确的验证码，从而绕过了验证码确认机制，产生了重置任意密码的漏洞

为了更加方便的理解，这下面画了正常重置密码流程和攻击者任意重置密码流程时客户端与服务端的数据交换图

[![](https://p1.ssl.qhimg.com/t015062d99b6fd5b3a9.png)](https://p1.ssl.qhimg.com/t015062d99b6fd5b3a9.png)

[![](https://p3.ssl.qhimg.com/t016f256c67a94fc4f8.png)](https://p3.ssl.qhimg.com/t016f256c67a94fc4f8.png)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E6%80%BB%E7%BB%93"></a>漏洞总结

本质来说，该漏洞是一个典型的逻辑缺陷产生的漏洞，在开发者的逻辑看来看来，你需要一步步按照给定的流程进行重置密码，但是第二步和第三步提交的认证参数重合，导致了第二步认证被绕过，于是原本设计在第二步进行验证码爆破的限制措施自然也被绕过了，并最终导致可以直接进行验证码爆破重置任意密码

在尝试类似多步骤的流程中，可以尝试跳过中间的步骤，不按照程序预定的步骤顺序进行提交数据，包括跳过某些步骤、多次访问单个步骤、返回到先前的步骤等，也许下一个漏洞点就会被你发现

## 写完之后的吐槽

本来准备一次多发几篇的，不过由于画图构思的时间过长，差不多快两个小时才写完，这次就先发这一个了，后面还有更多的国外公开src漏洞报告分析，欢迎大家继续关注

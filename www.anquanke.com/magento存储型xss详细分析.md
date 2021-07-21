> 原文链接: https://www.anquanke.com//post/id/83378 


# magento存储型xss详细分析


                                阅读量   
                                **100375**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t012473af5138c4b5af.jpg)](https://p5.ssl.qhimg.com/t012473af5138c4b5af.jpg)

影响版本：Magento CE &lt;1.9.2.3 and Magento EE &lt;1.14.2.3

**0x00 Magento简介**

Magento (麦进斗) 是一套专业开源的电子商务系统。传说中的全球第一的电子商务系统。Magento设计得非常灵活,具有模块化架构体系和丰富的功能。易于与第三方应用系统无缝集成。其面向企业级应用,可处理各方面的需求,以及建设一个多种用途和适用面的电子商务网站。 包括购物、航运、产品评论等等,充分利用开源的特性,提供代码库的开发,非常规范的标准,易于与第三方应用系统无缝集成。一款新的专业开源电子商务平台,采用php进行开发,使用Zend Framwork框架。设计得非常灵活,具有模块化架构体系和丰富的功能。易于与第三方应用系统无缝集成。在设计上,包含相当全面,以模块化架构体系,让应用组合变得相当灵活,功能也相当丰富。为了打开盈利途径,Magento同时具备收费的企业版本,积极谋求合作和第三方整合的工具,比如电子支付平台等。

**0x02 描述**

在2016年1月20日,Magento发不了SUPEE-7405补丁,修补了一个高危存储型xss漏洞。攻击者只需要注册一个帐号,修改自己邮箱为攻击代码,并利用该账户提交一个订单,当管理员在后台查看此订单的时候,恶意脚本代码将被执行。

**0x03 验证性测试**

第一步,首先我们注册一个帐号,然后修改邮箱设置,发现有js邮箱验证,通过抓包改包工具成功修改邮箱为我们的恶意代码

[![](https://p5.ssl.qhimg.com/t01e10fd01cbe1cc20d.png)](https://p5.ssl.qhimg.com/t01e10fd01cbe1cc20d.png)



[![](https://p2.ssl.qhimg.com/t0171530ba88c1aef22.png)](https://p2.ssl.qhimg.com/t0171530ba88c1aef22.png)

第二步,浏览商品,提交订单





[![](https://p2.ssl.qhimg.com/t01292594d95beea088.png)](https://p2.ssl.qhimg.com/t01292594d95beea088.png)



第三步,管理员浏览后台,查看订单详情,出发漏洞

[![](https://p2.ssl.qhimg.com/t01238cf5ddb211333b.png)](https://p2.ssl.qhimg.com/t01238cf5ddb211333b.png)



**0x04 代码分析**

        恶意数据执行流程:



```
D:WWWmagentoappcodecoreMageCustomercontrollersAccountController.php  
----&gt;public function editPostAction()
             D:WWWmagentoappcodecoreMageEavModelForm.php 
    -----&gt;public function validateData(array $data)
D:WWWmagentolibZendValidateEmailAddress.php
```

[![](https://p5.ssl.qhimg.com/t01e45db0db424e8fa1.png)](https://p5.ssl.qhimg.com/t01e45db0db424e8fa1.png)

        从代码中可以看出没有明显的xss防御代码  "&gt;&lt;script&gt;alert(1)&lt;/script&gt;" 可以通过检测,最后进入数据库。

      当管理员访问后台订单详情的时候:

[![](https://p0.ssl.qhimg.com/t0165154f5f9408f7c0.png)](https://p0.ssl.qhimg.com/t0165154f5f9408f7c0.png)

        直接从订单数据库中取出邮箱数据,并没有过滤,形成存储xss漏洞。

**0x05 修复建议**

        升级到最新版本Magento CE 1.9.2.3 和 Magento EE 1.14.2.3

        由需要的同学可以查看原文：[https://blog.sucuri.net/2016/01/security-advisory-stored-xss-in-magento.html](https://blog.sucuri.net/2016/01/security-advisory-stored-xss-in-magento.html)

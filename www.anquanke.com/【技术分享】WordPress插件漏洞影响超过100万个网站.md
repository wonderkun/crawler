
# 【技术分享】WordPress插件漏洞影响超过100万个网站


                                阅读量   
                                **88107**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/85604/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：sucuri.net
                                <br>原文地址：[https://blog.sucuri.net/2017/02/sql-injection-vulnerability-nextgen-gallery-wordpress.html](https://blog.sucuri.net/2017/02/sql-injection-vulnerability-nextgen-gallery-wordpress.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85604/t01d0e95ba25e1cfd87.jpg)](./img/85604/t01d0e95ba25e1cfd87.jpg)

****

翻译：[pwn_361](http://bobao.360.cn/member/contribute?uid=2798962642)

预估稿费：120RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

**<br>**

**前言******

作为我们[Sucuri防火墙(WAF)](https://sucuri.net/website-firewall/)漏洞研究项目的一部分，为了查找存在的安全问题，我们已经审计了多个开源项目。当审计WordPress的“NextGEN”相册插件时，我们发现了一个严重的SQL注入漏洞。该漏洞允许一个未经授权的用户从受害人网站的数据库中偷取数据，包括用户的敏感信息。目前，有超过100万个WordPress网站安装了这个易被攻击的插件。

[![](./img/85604/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ae7116d3e8ba17a5.png)

 

**你处在危险中吗？**

攻击者利用该漏洞需要至少两个条件：

1.在你的网站中是否使用了“NextGEN Basic TagCloud Gallery”？

2.你是否允许你网站的用户提交要审阅的文章(投稿人)？

如果你的网站符合这两种情况之一，那你已经处在危险之中了。

漏洞原因是NextGEN相册允许用户在WordPress执行一条SQL查询时输入未经过滤的数据，本质上就是将用户输入直接添加到了一条SQL查询中。使用该攻击方法，一个攻击者可以偷取到密码的HASH、和WordPress其它配置的秘密信息。

 

**技术细节**

永远不要相信输入数据—这是一条金科玉律。如果遵守这条规律，那将会很安全。在很多情况下，我们必须问自己几个简单的问题：

1.这条输入数据足够安全吗？

2.对它进行过滤了吗？

3.我们遵循任何具体框架的规则和最佳实践了吗？

WordPress使用了PHP的vsprintf函数，用于在$wpdb-&gt;prepare()函数中提前准备好SQL statement，这意味着SQL语句使用格式化字符串和输入值作为参数。这使我们得出结论：将用户的输入提供给格式化字符串从来不是一个好主意，因为它可能没有对字符串进行过滤，可能会包含有效的sprintf/printf指令。

这就是为什么这个方法，get_term_ids_for_tags()引起了我们的注意：

[![](./img/85604/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01829658bf057adc6d.png)

上面的代码可以在下面的路径中发现：

nextgen-gallery/products/photocrati_nextgen/modules/nextgen_gallery_display/package.module.nextgen_gallery_display.php

在这个源代码中，我们注意到“$container_ids”字符串是由tag输入创建的，并且它的值并没有经过适当的过滤。对于SQL注入，它是安全的，但是，它不能阻止任意格式化字符串指令/输入的插入，在WordPress数据库的$wpdb-&gt;prepare()方法下会引起问题。

$wpdb-&gt;prepare和sprintf

[![](./img/85604/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0141bb793ef0891dc3.png)

在prepare()方法的代码中，我们注意到原始SQL代码在执行前发生了一些变化，具体变化是：如果在语句中发现%s，会被替换成‘%s’。同样，我们看到在发生变化之后，它会被传递给vsprintf函数，这意味着我们注入的任何有效的格式化字符串将有可能被处理。从PHP的sprintf函数文档中我们知道[可能会发生参数交换](http://php.net/manual/en/function.sprintf.php)，当没有适当过滤的输入数据添加到格式化字符串时，有可能导致类似于下面的一些问题：

1.恶意用户将下面的输入注入到格式化字符串/查询中：

[![](./img/85604/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c09c92e467bc4fe2.png)

2.生成的查询有可能类似于这样：

[![](./img/85604/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017db6d1fc8b50a930.png)

3.当传递给prepare()方法时，有可能会被修改为：

[![](./img/85604/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a9e4bb1a5f7b360f.png)

(%s将会变成‘%s’)。

4.于是，当由此产生的格式化字符串传递给vsprintf函数后，产生的SQL查询语句具有以下格式：

[![](./img/85604/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012f5af576125309ad.png)

如上所示，这意味着我们保留了一个额外的‘符号，这打破了我们字符串的单引号序列，并会将我们生成的[any_text2]字符串变成SQL查询的一部分。

 

**利用方案**

在插件的源代码中，我们发现有两个地方的函数会创建“$container_ids”字符串,分别是：

1.当使用标签库的短码时。它需要一个特权认证用户来执行这个攻击。

2.当从一个“NextGEN Basic TagCloud”相册访问标签时，恶意访问者可以通过稍微修改相册的URL(网站中存在的相册)，去发起攻击。

有了这些知识，一个未经授权的攻击者可以向SQL查询中添加额外的sprintf/printf指令，并利用$wpdb-&gt;prepare()的行为向执行的语句中添加攻击者控制的代码。

最终的攻击载荷(使用了TagCloud方法)类似于下面这样：

[![](./img/85604/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01893f0f07349e949a.png)

(http://target.url/2017/01/17/new-one/nggallery/tags/test%1$%s)) or 1=1#)

或者

[![](./img/85604/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0120332a417df6a972.png)

(http://target.url/2017/01/17/new-one/nggallery/tags/test%1$%s)) or 1=2#)

 

**结论**

这是一个严重漏洞，如果你使用了该插件的一个有漏洞的版本，请尽可能快的对它进行升级。

 

**参考链接**

[https://arstechnica.com/security/2017/02/severe-vulnerability-in-wordpress-plugin-could-affect-1-million-sites/?utm_source=tuicool&amp;utm_medium=referral](https://arstechnica.com/security/2017/02/severe-vulnerability-in-wordpress-plugin-could-affect-1-million-sites/?utm_source=tuicool&amp;utm_medium=referral)

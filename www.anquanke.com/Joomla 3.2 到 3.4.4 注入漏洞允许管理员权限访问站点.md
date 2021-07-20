> 原文链接: https://www.anquanke.com//post/id/82778 


# Joomla 3.2 到 3.4.4 注入漏洞允许管理员权限访问站点


                                阅读量   
                                **86936**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.trustwave.com/Resources/SpiderLabs-Blog/Joomla-SQL-Injection-Vulnerability-Exploit-Results-in-Full-Administrative-Access/](https://www.trustwave.com/Resources/SpiderLabs-Blog/Joomla-SQL-Injection-Vulnerability-Exploit-Results-in-Full-Administrative-Access/)

译文仅供参考，具体内容表达以及含义原文为准

**受影响版本:3.2 到 3.4.4**

**补救措施:**

如果你正在使用低版本的joomla,请立即去官方更新到最新版[https://github.com/joomla/joomla-cms/releases/download/3.4.5/Joomla_3.4.5-Stable-Full_Package.zip](https://github.com/joomla/joomla-cms/releases/download/3.4.5/Joomla_3.4.5-Stable-Full_Package.zip)

**<br>**

**概述:**

漏洞出在核心模块,因此不需要任何扩展,所有使用joomla 3.2以上版本的站点,都受此漏洞影响

/administrator /components /com_contenthistory/models/history.php,漏洞出在getListQuery()函数,代码如下



[![](https://p3.ssl.qhimg.com/t012163c4da8f172e08.png)](https://p3.ssl.qhimg.com/t012163c4da8f172e08.png)



当请求



[![](https://p4.ssl.qhimg.com/t011d3b3b24a350a770.png)](https://p4.ssl.qhimg.com/t011d3b3b24a350a770.png)



能够通过注入从数据库里返回session ID



[![](https://p0.ssl.qhimg.com/t01b9ea068a2aa7f9f7.png)](https://p0.ssl.qhimg.com/t01b9ea068a2aa7f9f7.png)



如果得到的是管理员的session ID ,则可以通过修改当前浏览器的cookies里的session ID ,然后访问/administrator/

就可以登陆后台了。



[![](https://p0.ssl.qhimg.com/t014720c7667b5ab210.png)](https://p0.ssl.qhimg.com/t014720c7667b5ab210.png)



**更多技术细节:**

[https://www.trustwave.com/Resources/SpiderLabs-Blog/Joomla-SQL-Injection-Vulnerability-Exploit-Results-in-Full-Administrative-Access/](https://www.trustwave.com/Resources/SpiderLabs-Blog/Joomla-SQL-Injection-Vulnerability-Exploit-Results-in-Full-Administrative-Access/)

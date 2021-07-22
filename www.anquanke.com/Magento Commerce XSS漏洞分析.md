> 原文链接: https://www.anquanke.com//post/id/169277 


# Magento Commerce XSS漏洞分析


                                阅读量   
                                **175061**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Fortinet，文章来源：fortinet.com
                                <br>原文地址：[https://www.fortinet.com/blog/threat-research/magento-commerce-widget-form--core--xss-vulnerability.html](https://www.fortinet.com/blog/threat-research/magento-commerce-widget-form--core--xss-vulnerability.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01d21b96dad289a1b9.jpg)](https://p2.ssl.qhimg.com/t01d21b96dad289a1b9.jpg)



## 一、前言

虽然电子商务为我们提供了更加便利的生活，但也面临来自互联网上越来越多的安全威胁。根据[Alexa top 1M](https://www.datanyze.com/market-share/e-commerce-platforms/Alexa%20top%201M) 2018年的统计数据，Magento Commerce电子商务平台目前的市场份额已经超过14%，这也是全球第二大电子商务平台。Magento的客户包括许多知名的企业，如[HP](https://www.hpstore.cn/)（惠普）、[Coca-Cola](https://www.cokestore.com/)（可口可乐）以及[Canon](https://store.canon.com.au/)（佳能）。

FortiGuard Labs团队最近在[Magento](https://magento.com/security/patches/magento-2.2.7-and-2.1.16-security-update)中找到了一个Cross-Site Scripting（XSS，跨站脚本）漏洞，漏洞根源在于Magento将用户提供的数据插入动态生成的widget表单时，没有合理过滤用户所输入的数据。虽然这个XSS漏洞只存在于Magento管理员页面中，但远程攻击者可以利用该漏洞在受害者浏览器上执行任意代码，然后获取Magento高权限账户的控制权，访问敏感数据或者接管存在漏洞的网站。

Magento Commerce 2.1~2.1.16、2.2~2.2.7版本受此XSS漏洞影响。



## 二、漏洞分析

用户在编辑Magento站点页面时，可以使用两种模式：`WYSIWYG`模式以及`HTML`模式。在`WYSIWYG`模式中，有一个“Insert Widget…”按钮（图1）。如图2所示，我们可以访问`http://IP/magento/index.php/admin/admin/widget/index/`链接，直接调用“Insert Widget”所对应的函数：

[![](https://p1.ssl.qhimg.com/t01fbda67f3cfe64147.png)](https://p1.ssl.qhimg.com/t01fbda67f3cfe64147.png)

图1. WYSIWYG模式中的Insert Widget函数

[![](https://p5.ssl.qhimg.com/t017963f48c0125e48f.png)](https://p5.ssl.qhimg.com/t017963f48c0125e48f.png)

图2. 直接访问Insert Widget函数表单

图2中的表单由`Widget.php`的一个php函数所生成，该页面具体路径为：`/vendor/magento/module-widget/Block/Adminhtml/Widget.php`（参考[GitHub](https://github.com/magento/magento2/blob/2.3-develop/app/code/Magento/Widget/Block/Adminhtml/Widget.php)链接）。该页面处理用户提供的URL，提取`widget_target_id`参数的值，然后将其插入`script`标签中，如图3所示。比如，当我们访问`http://IP/magento/index.php/admin/admin/widget/index/widget_target_id/yzy9952`这个链接时，`widget_target_id`的值就会被插入`script`标签中，如图4所示。

[![](https://p0.ssl.qhimg.com/t0155b7ab771ac2f664.png)](https://p0.ssl.qhimg.com/t0155b7ab771ac2f664.png)

图3. Widget.php生成表单script标签

[![](https://p3.ssl.qhimg.com/t01479e58e21ac809ad.png)](https://p3.ssl.qhimg.com/t01479e58e21ac809ad.png)

图4. Widget.php生成的`script`标签

该函数没有合理过滤用户提供的数据，只是使用某些符号（如`"`、``}``以及`;`）来闭合用户输入的数据。然而，攻击者可以添加其他一些符号（如`)`}`);`），闭合当前函数，然后添加HTML注释标签`&lt;!--`注释掉后续代码，轻松绕过这个限制过程。比如我们可以访问`http://IP/magento/index.php/admin/admin/widget/index/widget_target_id/yzy9952")`}`);test&lt;!--`这个链接：

[![](https://p2.ssl.qhimg.com/t01e53bb634578f7466.png)](https://p2.ssl.qhimg.com/t01e53bb634578f7466.png)

图5. 绕过过滤器

此时，攻击者就能将任意代码插入这个页面中。我们可以看到，在`script`标签开头处，代码调用了`require`函数，但`require`函数并不存在。然而，我们可以自己创建`require`函数，然后插入自己的代码，再接着执行该函数。比如，我们可以访问如下PoC链接，就能执行我们提供的代码：`http://IP/magento/index.php/admin/admin/widget/index/widget_target_id/yzy9952")`}`);function%20require()`{`alert(document.domain)`}`&lt;!--`。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017dceaddf6f6081fd.png)

图6. PoC



## 三、解决方案

如果用户正在使用存在漏洞的Magento Commerce版本，请尽快升级到最新版Magento，或者尽快打上安全补丁。

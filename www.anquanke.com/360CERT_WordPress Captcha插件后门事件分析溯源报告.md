> 原文链接: https://www.anquanke.com//post/id/91904 


# 360CERT：WordPress Captcha插件后门事件分析溯源报告


                                阅读量   
                                **114372**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    





## 0x00 事件背景

近日，WordPress官方库删除了插件Captcha，该插件最初看起来是当前作者使用“WordPress”的商标问题。随后有人发现在WordPress Captcha官方插件中发现存在后门，导致用户在更新插件时被植入后门。

360CERT对该事件进行了分析和溯源，建议WordPress用户尽快排查。



## 0x01 事件描述

近期，WordPress Captcha官方插件中被发现植入了恶意代码，该代码可以劫持用户对插件的更新。在被劫持的更新代码中发现一个后门：通过该后门任意用户可以以管理员的身份进入WordPress的管理后台，该后门只能被黑客使用一次。

该后门首次被发现于2017年12月4日的4.3.6版本中，相关地址如下：

https://plugins.trac.wordpress.org/changeset/1780758/captcha



## 0x02 后门代码分析

分析发现，在captcha.php文件中的cptch_wp_plugin_auto_update函数存在后门：

[![](https://p2.ssl.qhimg.com/dm/1024_359_/t0168c5ba1909726e7b.jpg)](https://p2.ssl.qhimg.com/dm/1024_359_/t0168c5ba1909726e7b.jpg)

该函数主要用于对于插件进行版本更新。可以看到其中$wptuts_plugin_remote_path是一个simplywordpress.net下的php文件。请求该文件将会下载一个zip文件对该插件进行更新。

在该函数底部可以看到，当用户点击插件更新时，就会调用cptch_wp_plugin_auto_update函数。

跟入函数中的cptch_wp_auto_update，这是一个用来更新插件的类，位于

在cptch_wp_auto_update.php中：

[![](https://p5.ssl.qhimg.com/t0101f82af659dbc014.jpg)](https://p5.ssl.qhimg.com/t0101f82af659dbc014.jpg)

在被构造初始化后调用cptch_check_update()方法进行跟新：

[![](https://p4.ssl.qhimg.com/t014c1d95530d786d75.jpg)](https://p4.ssl.qhimg.com/t014c1d95530d786d75.jpg)

cptch_check_update()方法中对比插件版本后使用curl_exec请求了远程的zip文件，下载解压后使用activate_plugins()激活了插件。而curl_exec远程请求的地址正是刚刚cptch_wp_plugin_auto_update函数中传入的地址：

https://simplywordpress.net/captcha/captcha_pro_update.php

下载得到的zip文件中，经过对比发现在plugin-update.php文件中藏有后门代码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0151cffbc49e0944d9.jpg)

后门会尝试使用unlink删除自身文件，导致了该后门只能被使用一次。然后用get_userdata(1)获取了管理员的信息。然后使用wp_clear_auth_cookie();和wp_set_current_user将自己身份设置为管理员，之后使用wp_safe_redirect跳转进入管理后台。



## 0x03 分析溯源

根据WordFence的分析过程，我们梳理了如下线索：

1、注册邮箱与注册人

该插件最先由BestWebSoft进行独立维护，但在2017年9月5日BestWebSoft公司声明有一个新的组织加入，该组织将主要负责免费版的插件，插件的增强版和专业版继续由BestWebSoft公司维护：

[https://bestwebsoft.com/free-captcha-version-is-now-supported-by-other-developers/](https://bestwebsoft.com/free-captcha-version-is-now-supported-by-other-developers/)

通过查询simplywordpress.net域名的注册信息发现：

注册邮箱为：scwellington@hotmail.co.uk，注册人为：Stacy Wellington。通过注册邮箱反查发现该邮箱注册了大量域名：

[![](https://p1.ssl.qhimg.com/t01883e646caa9e4817.jpg)](https://p1.ssl.qhimg.com/t01883e646caa9e4817.jpg)

2、关联域名

通过其中一个域名（unsecuredloans4u.co.uk）网站底部有如下信息可以看出该网站属于“Soiza InternetMarketers Limited”并且是昆特集团有限公司的代表（Representative ofQuint Group Limited）：

[![](https://mmbiz.qpic.cn/mmbiz_png/Ic3Rgfdm96cicRp4ZuG9SdjSMx2EoicYdgMCzp7s9ondAnByibC9OIyiaV2BGKcVcJgOMvhAcLuxkxL4kmg623vntQ/0?wx_fmt=png)](https://p0.ssl.qhimg.com/t01df33a6e1f5880086.png)[![](https://p1.ssl.qhimg.com/dm/1024_227_/t018f67ef2226823739.jpg)](https://p1.ssl.qhimg.com/dm/1024_227_/t018f67ef2226823739.jpg)

通过WordFence安全报告发现，上述公司是一个利用WordPress插件放置暗链做“黒帽SEO”公司。

同时分析发现simplywordpress.net和unsecuredloans4u.co.uk有紧密关系：通过DNS记录显示simplywordpress.net之前有一条A记录的查询是195.154.179.176，这正是unsecuredloans4u.co.uk的A记录。并且通过DNS的解析历史发现，simplywordpress.net在2017年10月A记录进行了一次变更，变更之前的IP正是unsecuredloans4u.co.uk现在的IP地址：

[![](https://p1.ssl.qhimg.com/dm/1024_691_/t017b56f286866a0764.jpg)](https://p1.ssl.qhimg.com/dm/1024_691_/t017b56f286866a0764.jpg)

3、可以公司与注册人

另一方面通过查看195.154.179.176上其他域名的站点如pingloans.co.uk，在其首页底部的介绍中可以发现该网站属于“Serpable Ltd”：

[![](https://p3.ssl.qhimg.com/dm/1024_283_/t011599f34468d2383c.jpg)](https://p3.ssl.qhimg.com/dm/1024_283_/t011599f34468d2383c.jpg)

通过查询“Serpable Ltd”公司的注册人可以发现是“Charlotte Ann Wellington”：

[![](https://p1.ssl.qhimg.com/t012f8dd1697848771c.jpg)](https://p1.ssl.qhimg.com/t012f8dd1697848771c.jpg)

4、新域名与多个插件

回到simplywordpress.net站点，360 CERT于2017年12月20日13点访问该网站发现仍然可用：

[![](https://p5.ssl.qhimg.com/t0173674f0c5f9885b6.jpg)](https://p5.ssl.qhimg.com/t0173674f0c5f9885b6.jpg)

[![](https://p5.ssl.qhimg.com/t01a9d1e52fa0f2c745.jpg)](https://p5.ssl.qhimg.com/t01a9d1e52fa0f2c745.jpg)

并在网站中发现了该站点提供了多个WordPress的插件,与WordFence分析报告中提到的插件基本一致,经过360CERT重新整理，发现涉及到的插件主要有：
- convert-popup
- death-to-comments
- Human Captcha（free） Human Captcha（pro）
- smart-recaptcha
- Social（free） Social（pro）
- Social Exchange
上述6个插件与Captcha插件后门存在相同的手法：

[![](https://p0.ssl.qhimg.com/t01c3dbc53c06b59837.jpg)](https://p0.ssl.qhimg.com/t01c3dbc53c06b59837.jpg)

[![](https://mmbiz.qpic.cn/mmbiz_png/Ic3Rgfdm96cicRp4ZuG9SdjSMx2EoicYdg8HcdibC1QR0rvicDYiauhOtO2aJOIgDrv6l8QzbyLrSjVSbes3VpYVUrA/0?wx_fmt=png)](https://p0.ssl.qhimg.com/t01df33a6e1f5880086.png)[![](https://p1.ssl.qhimg.com/t01d021618bd38adf4f.jpg)](https://p1.ssl.qhimg.com/t01d021618bd38adf4f.jpg)

[![](https://p3.ssl.qhimg.com/t01d060e95d4741fb81.jpg)](https://p3.ssl.qhimg.com/t01d060e95d4741fb81.jpg)

[![](https://p3.ssl.qhimg.com/dm/1024_572_/t01f8606630f5b05b67.jpg)](https://p3.ssl.qhimg.com/dm/1024_572_/t01f8606630f5b05b67.jpg)

同时在swpopup发现一个新的域名：heyrank.co.uk

该域名WordFence分析报告中发现的一致，注册人为：“StacyWellington”

[![](https://p1.ssl.qhimg.com/t01ffe222e3b85cc505.jpg)](https://p1.ssl.qhimg.com/t01ffe222e3b85cc505.jpg)

同时195.154.179.176正是unsecuredloans4u.co.uk的地址：

[![](https://p4.ssl.qhimg.com/t015fc91f9094c03a2d.jpg)](https://p4.ssl.qhimg.com/t015fc91f9094c03a2d.jpg)

5、背后可疑集团

到此可以发现Stacy 和Charlotte Ann Wellington两人均涉及到“Quint Ltd”。

通过搜索发现Stacy声明为Serpable公司工作，而“Serpable”公司正是属于“Ann Wellington”

[![](https://p3.ssl.qhimg.com/t0106ea3d921d9773ad.jpg)](https://p3.ssl.qhimg.com/t0106ea3d921d9773ad.jpg)

[![](https://p5.ssl.qhimg.com/t01d4c73310e529015e.jpg)](https://p5.ssl.qhimg.com/t01d4c73310e529015e.jpg)

查询“Charlotte Ann WELLINGTON”发现其拥有公司：
- CODELABSGROUP LTD
- LEADBRAIN LTD
- SERPABLE LTD
相关信息如下：

https://beta.companieshouse.gov.uk/officers/iIMGxbZMjmfOUE-FLoktQUrBDWg/appointments

SERPABLE公司曾经在其网站上公开出售过暗链，镜像如下图：

[![](https://p4.ssl.qhimg.com/dm/1024_703_/t01dee7f7a2c071c6f0.jpg)](https://p4.ssl.qhimg.com/dm/1024_703_/t01dee7f7a2c071c6f0.jpg)

同时在blackhatworld论坛中留下了出售暗链的信息：

[![](https://p3.ssl.qhimg.com/dm/1024_823_/t019151436c1b10d3d3.jpg)](https://p3.ssl.qhimg.com/dm/1024_823_/t019151436c1b10d3d3.jpg)

通过检索、以及根据首页底部的介绍，发现以下网站同样属于SERPABLE公司：
- loanload.co.uk
- pingloans.co.uk
- pounda.co.uk
至此，该集团与此次事件的情况基本梳理完成，360 CERT总结成了如下的关系图：

[![](https://p1.ssl.qhimg.com/dm/1024_596_/t0143ac9946ad5de0b4.jpg)](https://p1.ssl.qhimg.com/dm/1024_596_/t0143ac9946ad5de0b4.jpg)



## 0x04 事件影响

WordPress官网显示，Captcha等插件的总激活使用量在300000以上。

[![](https://p2.ssl.qhimg.com/t01f740127c57df60ab.jpg)](https://p2.ssl.qhimg.com/t01f740127c57df60ab.jpg)

[![](https://p1.ssl.qhimg.com/t01381d74099140692f.jpg)](https://p1.ssl.qhimg.com/t01381d74099140692f.jpg)

通过对官方插件Timeline的查看，发现Captcha后门首次出现在12月4日的版本中：

[![](https://p2.ssl.qhimg.com/dm/1024_352_/t01473f23cd36bc9b86.jpg)](https://p2.ssl.qhimg.com/dm/1024_352_/t01473f23cd36bc9b86.jpg)

[![](https://p3.ssl.qhimg.com/dm/1024_351_/t01ea1c981b4ab187e7.jpg)](https://p3.ssl.qhimg.com/dm/1024_351_/t01ea1c981b4ab187e7.jpg)

官方于12月20日才发现并删除该后门。也就是说在12月4日至12月20日之间更新过该插件的用户均遭受影响。

通过WordFence的报告看出，受影响的版本为4.3.6 – 4.4.4。基于该插件拥有超过30万的用户量，360 CERT初步判断该后门事件影响广泛。



## 0x05 缓解措施

首先在插件目录下的plugin-update.php页面，同时其源代码中检查是否有如下代码：

[![](https://p1.ssl.qhimg.com/t01af800da465ed56fc.jpg)](https://p1.ssl.qhimg.com/t01af800da465ed56fc.jpg)

如有发现请立即删除该文件。

同时在插件目录下的captcha.php页面源代码中检查是否有如下链接：

https://simplywordpress.net/captcha/captcha_pro_update.php

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_299_/t0199bbdaeaab5ea0f3.jpg)

如果存在，千万不要在后台点击更新插件，而是将整个插件删除。

官方已于最新版的代码中删除了该后门，用户在手动删除文件后，可以重新安装最新版插件。



## 0x06 IOCs

资源请求：

https://simplywordpress.net/captcha/captcha_pro_update.php

http://simplywordpress.net/humancaptcha/human_cptch_pro_update.php

http://simplywordpress.net/social-exchange/social_free_update.php

http://simplywordpress.net/death-to-comments/dcmt_pro_update.php

http://simplywordpress.net/convert-popup/convert_popup_pro_update.php

域名/IP：

simplywordpress.net

unsecuredloans4u.co.uk

heyrank.co.uk

loanload.co.uk

pingloans.co.uk

pounda.co.uk

195.154.179.176

23.236.161.226

邮箱：

scwellington@hotmail.co.uk

相关WordPress插件

convert-popup

death-to-comments

Human Captcha（free） Human Captcha（pro）

smart-recaptcha

Social（free） Social（pro）

Social Exchange



## 0x07 时间线

2017年12月19日          Wordfence 事件披露

2017年12月20日          360CERT及时跟进，完成分析报告

2017年12月21日          360CERT对外发布预警



## 0x08 参考链接

[https://www.wordfence.com/blog/2017/12/backdoor-captcha-plugin/](https://www.wordfence.com/blog/2017/12/backdoor-captcha-plugin/)

[https://wordpress.org/support/topic/backdoor-2/](https://wordpress.org/support/topic/backdoor-2/)

[https://plugins.trac.wordpress.org/changeset/1780758/captcha](https://plugins.trac.wordpress.org/changeset/1780758/captcha)

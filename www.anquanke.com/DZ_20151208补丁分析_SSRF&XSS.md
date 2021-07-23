> 原文链接: https://www.anquanke.com//post/id/83123 


# DZ_20151208补丁分析_SSRF&amp;XSS


                                阅读量   
                                **67022**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t017344c0898de340b2.jpg)](https://p3.ssl.qhimg.com/t017344c0898de340b2.jpg)

**author:ModNar@0keeTeam**

漏洞分析:

我们先来diff看看补丁20151208相对20150609都改了啥:



```
*source/admincp/admincp_checktools.php     IM图片库命令执行(需登录后台)
*source/class/helper/helper_form.php       http://www.wooyun.org/bugs/wooyun-2015-0124807 Discuz CSRF发帖POC可蠕虫 (限制referer)
*source/function/function_discuzcode.php    http://www.wooyun.org/bugs/wooyun-2015-0150674 SSRF和xss
*source/function/function_followcode.php    http://www.wooyun.org/bugs/wooyun-2015-0150674 SSRF和xss
*source/module/forum/forum_viewthread.php    http://www.wooyun.org/bugs/wooyun-2015-0151687 帖子正文XSS
*source/module/misc/misc_swfupload.php     http://www.wooyun.org/bugs/wooyun-2015-0124807 Discuz CSRF发帖POC可蠕虫 (限制非图片文件上传)
*static/js/bbcode.js                       http://www.wooyun.org/bugs/wooyun-2015-0139851 最新版Discuz修复不全导致仍可针对管理员存储XSS
*template/default/member/getpasswd.htm     未知
*source/function/function_cloudaddons.php  未知,插件相关
*source/function/function_core.php         功能性bug?
*source/admincp/admincp_cloudaddons.php    未知,插件相关
```

<br>

以下选用其中的SSRF和有限制的XSS作分析:

1.bbcode有条件SSRF

补丁都加了个严格匹配开头的正则符^,看起来是正则校验url不严格的问题:

sourcefunctionfunction_discuzcode.php:

[![](https://p4.ssl.qhimg.com/t0122f85328889cccac.png)](https://p4.ssl.qhimg.com/t0122f85328889cccac.png)

科学地使用skywolf,轻松定位到背锅的代码位置:

[![](https://p4.ssl.qhimg.com/t0103ee4456f7859fc1.png)](https://p4.ssl.qhimg.com/t0103ee4456f7859fc1.png)

第4个调用点点开看看:

[![](https://p5.ssl.qhimg.com/t01485d194437499ab7.png)](https://p5.ssl.qhimg.com/t01485d194437499ab7.png)

由以上调用栈可知触发条件是看帖。

Poc:

根据preg_replace的正则和parseflv的正则,我们可以构造如下的payload, 即可通过正则校验使[media]包裹的内容到达file_get_contents调用处:

[media=x,,][http://ip:port/phpinfo.php?cmd=calc.exe&amp;xx=http://www.tudou.com/programs/view/xx.html[/media](http://ip:port/phpinfo.php?cmd=calc.exe&amp;xx=http://www.tudou.com/programs/view/xx.html%5b/media)]

2.bbcode有限制存储XSS

这个文件还修复了一处类似限制条件的存储XSS:

[![](https://p1.ssl.qhimg.com/t018d7abf375c552b31.png)](https://p1.ssl.qhimg.com/t018d7abf375c552b31.png)

此处是组合的HTML标签,可控点$url处于js中,可用单引号闭合:

[![](https://p3.ssl.qhimg.com/t016e90e14dc73cf1be.png)](https://p3.ssl.qhimg.com/t016e90e14dc73cf1be.png)

调用点也是preg_replace的bbcode解析处:

[![](https://p4.ssl.qhimg.com/t015d428a8a46c35455.png)](https://p4.ssl.qhimg.com/t015d428a8a46c35455.png)

Poc:

因此构造以下payload即可触发XSS:

[flash][http://www.baidu.com/1.swf?a='));alert(2);//](http://www.baidu.com/1.swf?a=%27));alert(2);//)[/flash]

利用限制:

很显然,这次又是bbcode解析的锅,这里用到了preg_replace的/e选项,所以需要php&lt;5.5的支持。$allowmediacode需要为true,通过查看后台相应选项,版块允许使用多媒体代码默认是开的,然而默认只有管理员组才允许发media标签的bbcode。

[![](https://p0.ssl.qhimg.com/t01e666a738d809cbf7.png)](https://p0.ssl.qhimg.com/t01e666a738d809cbf7.png)

利用演示:

假设内网一处[http://10.0.2.15/phpinfo.php](http://10.0.2.15/phpinfo.php)源码如下:

[![](https://p1.ssl.qhimg.com/t019cfd49c5620cef00.png)](https://p1.ssl.qhimg.com/t019cfd49c5620cef00.png)

发帖:

[![](https://p1.ssl.qhimg.com/t01070f5b0cc56214c6.png)](https://p1.ssl.qhimg.com/t01070f5b0cc56214c6.png)

查看帖子[http://127.0.0.1/discuz/forum.php?mod=viewthread&amp;tid=12&amp;extra=page=1](http://127.0.0.1/discuz/forum.php?mod=viewthread&amp;tid=12&amp;extra=page=1):

[![](https://p4.ssl.qhimg.com/t0179be871221a7b8e3.png)](https://p4.ssl.qhimg.com/t0179be871221a7b8e3.png)

3.无限制SSRF

之前分析的漏洞触发点要求发帖人允许使用多媒体代码,实际上存在无限制的点:

sourcefunctionfunction_followcode.php:

diff这个文件,亮点不在标红代码处,而是在fparsemedia中调用了之前的parseflv!

[![](https://p2.ssl.qhimg.com/t01d9f6aad2119af72e.png)](https://p2.ssl.qhimg.com/t01d9f6aad2119af72e.png)

往上看fparsemedia的调用点:

在function followcode()中,也有类似之前sourcefunctionfunction_discuzcode.php的bbcode解析,可见此处是没有$allowmediacode条件限制的:

[![](https://p3.ssl.qhimg.com/t0121c6e4feeccb43cc.png)](https://p3.ssl.qhimg.com/t0121c6e4feeccb43cc.png)

sourcemoduleforumforum_ajax.php:

[![](https://p2.ssl.qhimg.com/t01ebd18df302ecc6f9.png)](https://p2.ssl.qhimg.com/t01ebd18df302ecc6f9.png)

跟到前台的触发点可构造:

http://127.0.0.1/discuz/forum.php?mod=ajax&amp;tid=11&amp;extra=page=1&amp;action=getpostfeed&amp;flag=1&amp;pid=36

调用栈如下:

[![](https://p5.ssl.qhimg.com/t0155c6ca6f7bb4ea43.png)](https://p5.ssl.qhimg.com/t0155c6ca6f7bb4ea43.png)

因此无限制的利用过程为:

使用任意用户发帖,然后回复该帖子,回复内容同样为:

[media=x,,][http://10.0.2.15/phpinfo.php?cmd=calc.exe&amp;xx=http://www.tudou.com/programs/view/xx.html[/media](http://10.0.2.15/phpinfo.php?cmd=calc.exe&amp;xx=http://www.tudou.com/programs/view/xx.html%5b/media)]

[![](https://p5.ssl.qhimg.com/t01b53b61a75d852544.png)](https://p5.ssl.qhimg.com/t01b53b61a75d852544.png)

然后访问以下链接触发SSRF,其中fid和tid分别是帖子的id和回复的id:

http://127.0.0.1/discuz/forum.php?mod=ajax&amp;tid=11&amp;extra=page=1&amp;action=getpostfeed&amp;flag=1&amp;pid=36

[![](https://p3.ssl.qhimg.com/t0148b3aa1c10e1c340.png)](https://p3.ssl.qhimg.com/t0148b3aa1c10e1c340.png)

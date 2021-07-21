> 原文链接: https://www.anquanke.com//post/id/86855 


# 【技术分享】如何将Pastebin上的信息应用于安全分析和威胁情报领域


                                阅读量   
                                **122920**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：techanarchy.net
                                <br>原文地址：[https://techanarchy.net/2017/09/hunting-pastebin-with-pastehunter/](https://techanarchy.net/2017/09/hunting-pastebin-with-pastehunter/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01747a9730e4106379.jpg)](https://p5.ssl.qhimg.com/t01747a9730e4106379.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：120RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**一、前言**

****从安全分析以及威胁情报的角度来看，**Pastebin**是一个难得的信息宝库。只要没有设置隐私（private）选项（需要注册账户才能设置该选项），任何人都可以查看上传到pastebin数据的具体内容。<br>

本文介绍了一款[PasteHunter](https://github.com/kevthehermit/PasteHunter)工具，该工具可以使用**Yara**规则从Pastebin上搜索有价值的信息，并将结果保存到本地环境中。

**<br>**

**二、实现方案**

公开数据来源非常广，比如，黑客以及脚本小子迫不及待地想把他们的成果推送到网站上，享受被全世界瞩目的自豪感，而开发者或网络工程师一旦出现疏忽，就会不小心把内部配置信息以及凭证信息公之于众。

这种情况下，普通安全分析师如何筛选这些数据，在安全分析行业中发挥这些数据的价值呢？

我们可以搜索Pastebin上的所有上传数据，检查这些数据是否包含有价值的信息。现在有很多工具可以提供类似功能，比如，[dumpmon](https://twitter.com/dumpmon)使用了一组正则表达式来监控类似Pastebin的多个网站，然后通过推特公布监控结果。

这个资源很不错，然而我希望自己能在更多细节上进行控制。Pastebin并不反对我们爬取其数据，但该网站存在某些限制条件，同一个IP地址多次请求后可能会被临时或者永久封禁。

幸运的是，Pastebin提供了一个API，这种API专门服务于此类任务场景。目前，Pastebin正在搞为期几天的促销，一次支付19.95美元就能永久拥有[Pro（专业版）账号](https://pastebin.com/pro)。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/1.png)[![](https://p3.ssl.qhimg.com/t017d637d0195fd448a.png)](https://p3.ssl.qhimg.com/t017d637d0195fd448a.png)

图1. Pro账户促销

拥有Pro账户后，我们可以使用某个白名单IP，以每秒1次的频率请求API。实际环境中，我们请求的频率并不需要那么高。

现在我们已经可以访问所有的数据，接下来如何处理这些数据呢？是时候请出[PasteHunter](https://github.com/kevthehermit/PasteHunter)这个工具了。

这个工具实际上是一个简单的脚本，可以通过一组Yara规则，利用pastebin API来获得数据，筛选其中匹配的数据内容，存放到elastic search引擎中，然后使用Kibana前端来展示匹配的结果。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/2.png)[![](https://p2.ssl.qhimg.com/t01f8362ffa97c4199a.png)](https://p2.ssl.qhimg.com/t01f8362ffa97c4199a.png)

图2. 前端仪表盘

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/3.png)[![](https://p3.ssl.qhimg.com/t016e88f6def168e551.png)](https://p3.ssl.qhimg.com/t016e88f6def168e551.png)

图3. 后端已存储数据

如果你不熟悉Yara规则，这里稍微介绍一下。[Yara](https://virustotal.github.io/yara/)是一种模式匹配引擎，主要用来扫描文件以及分类恶意软件家族。Yara使我们能够很方便地构造复杂的匹配规则，无需陷入正则表达式的泥潭。

安装过程非常简单，如果你需要Web界面来搜索内容的话，你可以安装Elastic Search以及Kibana。

当然我们也需要选择Python3、Yara，并将两者绑定（使用pip install yara-python这条命令）。

安装基础环境后，我们需要从代码库中下载代码，创建计划任务以定期运行脚本。详细信息可以阅读Github上的[readme](https://github.com/kevthehermit/PasteHunter/blob/master/README.md)文档。

代码中自带了一些规则，这些规则可以扫描最常见的那些数据，比如密码信息、泄露的凭证信息、被黑的网站等等。你也可以创建自定义关键词的规则文件，添加自己的关键词，例如，某个custom_keywords.yar文件如下所示：



```
/* This rule will match any of the keywords in the list */
rule custom_keywords `{`
    meta: author = "@KevTheHermit" info = "Part of PasteHunter"
    strings:
        $my_email = "thehermit@techanarchy.net" wide ascii nocase
        $my_domain = "techanarchy.net" wide ascii nocase
        $this_word = "This Word"
        $other_word = "More Words"
    condition:
        any of them
`}`
```

你可以使用这种规则搜索匹配的域名、邮件地址、文档名等各类信息，以了解是否有任何数据意外泄露或者被他人窃取。

如果你想了解创建Yara规则的更多细节，可以参考[官方文档](https://yara.readthedocs.io/en/v3.6.0/)中的详细说明。

你所要做的就是这么简单，运行脚本后，你可以看到数据源源不断汇聚进来。

已收集的部分数据样本如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/4.png)[![](https://p4.ssl.qhimg.com/t01f577ce1d5dffa788.png)](https://p4.ssl.qhimg.com/t01f577ce1d5dffa788.png)

图4. Base64编码的恶意软件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/5.png)[![](https://p3.ssl.qhimg.com/t01dc368b13273b372d.png)](https://p3.ssl.qhimg.com/t01dc368b13273b372d.png)

图5. API密钥

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/6.png)[![](https://p0.ssl.qhimg.com/t012c7500e24672ce55.png)](https://p0.ssl.qhimg.com/t012c7500e24672ce55.png)

图6. 邮件地址

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/7.png)[![](https://p5.ssl.qhimg.com/t0110b1d485119fba76.png)](https://p5.ssl.qhimg.com/t0110b1d485119fba76.png)

图7. Doxing信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/8.png)[![](https://p1.ssl.qhimg.com/t0159ef1d842ce46d00.png)](https://p1.ssl.qhimg.com/t0159ef1d842ce46d00.png)

图8. 工具使用说明

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](//base_request.html/img/9.png)[![](https://p4.ssl.qhimg.com/t013272d79cc42ce144.png)](https://p4.ssl.qhimg.com/t013272d79cc42ce144.png)

图9. Powershell及exe的下载

需要注意的是，这些规则可能会出现误报，相对于数据的可信度而言，你更应该衡量首次上传该数据的人的可信度。

我的工作离不开[@tu5k4rr](https://twitter.com/tu5k4rr)的帮助，这个工具的灵感源自于他所开发的[pastabean](https://github.com/Tu5k4rr/PastaBean)工具。

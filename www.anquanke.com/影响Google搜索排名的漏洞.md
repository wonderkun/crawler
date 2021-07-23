> 原文链接: https://www.anquanke.com//post/id/104278 


# 影响Google搜索排名的漏洞


                                阅读量   
                                **98754**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Tom，文章来源：http://www.tomanthony.co.uk/
                                <br>原文地址：[http://www.tomanthony.co.uk/blog/google-xml-sitemap-auth-bypass-black-hat-seo-bug-bounty/](http://www.tomanthony.co.uk/blog/google-xml-sitemap-auth-bypass-black-hat-seo-bug-bounty/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01140e83b41bad7806.jpg)](https://p5.ssl.qhimg.com/t01140e83b41bad7806.jpg)

```
译者总结：
1、Google可以通过专门的Ping URL提交网站地图，并且该提交不会显示在Google Search Console中（对受害者隐形）。
2、利用受害开放式重定向（登录、登出等可以指定转向地址的地方，这里要求可以跨域重定向）构造能够转向到恶意网站的网站地图（使用hreflang，声明恶意网站是受害网站的多语言站点）的URL。
3、将2中构造的URL向1中提交，可以使恶意域名“偷取”受害者域名的链接权重、置信度、Rank。
4、本文作者使用如上方法，没花一分钱，让自己的低成本购买的域名与沃尔玛、亚马逊等域名一样排到了搜索结果第一页。
5、吐槽：Google一共给了作者1337美元的奖金，这个性价比也太高了。
```

> **简洁版本：**
对于一个成本12美元的域名，我能使它在Google中搜索亚马逊、沃尔玛等关键字的结果中排名靠前。这些AdWords的竞标价格目前为每次点击1美元左右，很多公司每月花费数千美元的费用在搜索结果中显示为广告，而且我的域名则免费显示。
Google现在已经解决了这个问题，并奖励了1337美元的bug奖金。
Google提供了一个开放的URL，您可以在其中“ping”，他们将获取并解析的XML站点地图（该文件可以包含索引编制指令）。我发现，对于许多网站，您可以ping您（攻击者）托管的站点地图，使得Google将恶意站点的站点地图视为属于受害者站点。
我相信这是他们第一次对实际的搜索引擎问题授予安全问题奖励，该问题直接影响到网站的排名。
[Hacker News讨论](https://news.ycombinator.com/item?id=16762922)<br>[/ r / netsec讨论](https://www.reddit.com/r/netsec/comments/89z47n/google_bug_bounty_for_security_exploit_that/)

作为我的常规研究工作的一部分，我最近发现了一个问题，该问题允许攻击者向Google提交一个XML站点地图，以查找未经过身份验证的站点。由于这些文件可以包含索引指令（如hreflang），因此攻击者可以利用这些指令帮助自己的网站在Google搜索结果中排名。

我花了12美元设置了我的实验，排名出现在高收费搜索条件的第一页上，并且新注册的域名没有入站链接。



## XML Sitemap和Ping机制

Google允许[提交XML网站地图](https://support.google.com/webmasters/answer/183668?hl=en) ; 这些可以帮助他们发现抓取的URL，也可以使用[hreflang](https://www.seozac.com/en-seo/hreflang-tag/)指令来帮助找到同一页面的其他国际版本可能存在的内容（例如，“嘿，Google，这是美国的页面，但我有一个德国版的页面在这个URL上 ……“）。目前还不清楚Google是如何使用这些指令的（就像任何与Google搜索算法相关的指令一样），但似乎hreflang允许一个URL从一个URL’借用’链接权重和信任度（ link equity and trust ）并用它来为另外的URL提升Rank（即大多数人链接到美国.com版本，因此德国版本可以借用该权重在Google.de中获得更好的排名）。

您可以通过Google Search Console、在robots.txt中写入或通过特殊的“ping”网址为您的域名提交XML站点地图。[Google自己的文档](https://support.google.com/webmasters/answer/183669?hl=en)似乎有点矛盾; 在页面的顶部，他们指的是通过ping机制提交站点地图，但在页面的底部他们有这样的警告（ping URL是重新提交用的）：

[![](https://p5.ssl.qhimg.com/t0145db798a2cf74123.png)](https://p5.ssl.qhimg.com/t0145db798a2cf74123.png)

但是，根据我的经验，您绝对可以通过ping机制提交新的XML站点地图，Googlebot通常在ping的10-15秒内获取地图文件。重要的是，Google在页面上也提到过几次，如果您通过ping机制提交站点地图**，它将不会显示在您的Search Console中**：

[![](https://p3.ssl.qhimg.com/t01e65abe917bb3a8ee.png)](https://p3.ssl.qhimg.com/t01e65abe917bb3a8ee.png)

作为一个相关测试，我测试了是否可以通过XML站点地图添加其他已知的搜索指令（noindex，rel-canonical）（以及尝试一堆XML攻击），但Google似乎没有使用它们。



## Google Search Console提交

如果您尝试在GSC中提交XML站点地图，该站点地图包含您未被授权的其他域的URL，则GSC会拒绝他们：

[![](https://p2.ssl.qhimg.com/t010f5d099dd6522bfd.png)](https://p2.ssl.qhimg.com/t010f5d099dd6522bfd.png)

我们稍后会回来。

（对不起，Jono！）



## 开放式重定向

许多网站使用URL参数来控制重定向：

[![](https://p4.ssl.qhimg.com/t019302892e23874692.png)](https://p4.ssl.qhimg.com/t019302892e23874692.png)

在这个例子中，我将被重定向到（登录后）`page.html`。有些安全差的网站允许使用所谓的“开放式重定向”，这些参数允许重定向到不同的域：

[![](https://p4.ssl.qhimg.com/t019919362108412180.png)](https://p4.ssl.qhimg.com/t019919362108412180.png)

通常这些不需要任何交互（如登录），所以他们只是立即进行重定：

[![](https://p1.ssl.qhimg.com/t01b6fed36de4b5146c.png)](https://p1.ssl.qhimg.com/t01b6fed36de4b5146c.png)

开放重定向非常普遍，通常被认为并不危险; 因此，Google不会将他们纳入他们的漏洞奖励计划。但是，公司会尽力避免这些情况发生，但您通常可以绕过其保护：

[![](https://p4.ssl.qhimg.com/t01c9ba4cbebb34a0c1.png)](https://p4.ssl.qhimg.com/t01c9ba4cbebb34a0c1.png)

Tesco是一家英国零售商，收入超过500亿英镑，超过10亿英镑的收入来自其网站。我向特易购（Tesco）报告了这个例子（以及其他一些在我的研究中发现的其他公司）。目前他们已经修复了这个例子。



## 通过开放重定向Ping Sitemaps

到了这一步，你可能已经猜到了我接下来会如何进行。事实证明，当您ping一个XML站点地图时，如果您提交的URL是重定向，**那么** Google将跟进该重定向，即使它是跨域的。重要的是，它似乎仍然将该XML站点地图与进行重定向的域名相关联，并将重定向后的站点地图视为由该域进行授权的。例如：

[![](https://p5.ssl.qhimg.com/t01eaa7c94e844a2623.png)](https://p5.ssl.qhimg.com/t01eaa7c94e844a2623.png)

在这种情况下，`evil.xml`网站地图托管在`blue.com`Google 上，但Google会将其关联为属于并且对其具有权威性`green.com`。使用此功能，您可以为您未控制的网站提交XML站点地图，并发送Google搜索指令。



## 实验：使用hreflang指令免费“偷取”置信度和排名

到了这一步，我有已经进行了一些尝试，但我没有确认Google会真的相信跨域重定向的XML站点地图，所以我做了一个实验来测试它。我做了很多更小的测试，以了解这个（以及各种死路一条）的各个部分，但并没有指望这个实验能够达到预期。

我为一家不在美国经营的英国零售公司创建了一个虚假域名，并创建了一个模仿该网站的AWS服务器（主要是通过收集合法内容并重新设计它 – 即更改货币/地址等）。我在这里隐藏公司名和行业来保护他们，所以让我们叫他们`victim.com`。

我现在创建了一个托管在`evil.com`上的虚假网站地图，但其中仅包含`victim.com`上的URL。这些URL包含每个指向等效URL的每个URL的hreflang条目`evil.com`，表明它是美国版本的`victim.com`。我使用Google的ping机制及`victim.com`的开放式重定向进行了Sitemap提交。

在48小时内，该网站只有少量的流量，逐渐显示出一个长尾（SEMRush截图）：

[![](https://p5.ssl.qhimg.com/t01a4dbe6a22977bab9.png)](https://p5.ssl.qhimg.com/t01a4dbe6a22977bab9.png)

再过两天，我的站点出现在高竞争的条件的第一页，就与亚马逊和沃尔玛一样。

[![](https://p3.ssl.qhimg.com/t015e64374c7c16a832.png)](https://p3.ssl.qhimg.com/t015e64374c7c16a832.png)

此外，`evil.com`的Google Seach Console中显示该`victim.com`链接到`evil.com`，虽然这显然并非如此：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01070af68b787d950e.png)

现在，我发现我也能够为`victim.com`GSC内部提交XML站点地图`evil.com`：

[![](https://p1.ssl.qhimg.com/t017843c5d37edba59b.png)](https://p1.ssl.qhimg.com/t017843c5d37edba59b.png)

Google似乎已将这些网站链接起来了，而`evil.com`搜索控制台现在有一些能影响`victim.com`设置。我现在也可以跟踪我提交的站点地图的索引（您可以看到我现在有数千页索引）。

[Searchmetrics](https://www.searchmetrics.com/)显示了流量的增长价值：

[![](https://p5.ssl.qhimg.com/t01bca718d988fbacab.png)](https://p5.ssl.qhimg.com/t01bca718d988fbacab.png)

Google Search Console显示了在Google搜索中已经有超过100万的搜索展示次数和超过10,000次点击次数; 知道现在，除了提交XML站点地图，我什么都没做！

你应该注意到，我并没有让人们看到这个非法的网站，但是我曾经想过，现在，我可以欺骗人们赚很多钱，也可设置广告，再或者可以将流量变现。在我看来，这给Google访问者及依赖Google搜索流量的公司带来了严重的风险。流量仍在增长，但我关闭了我的实验，并放弃了我的后续实验，因为害怕造成损害。



## 讨论

这种方法`victim.com`完全无法检测到- XML站点地图不会显示在它们哪里，如果您正在做我实验的并且利用该方法将置信度链接到不同的国家的站点，那么您完全做到完全隐形。在该国运营的竞争对手将对您的网站的排名感到困惑（见上文，我在搜索结果中，亚马逊，沃尔玛和塔吉特，他们都花费大量资源在Google那里）。

就黑帽SEO而言，这有一个明确的用法，而且是我意识到的第一个的彻底利用的算法例子，而不是操纵排名因素。这个问题的潜在经济影响似乎并非微不足道 – 想象一下以特易购或类似目标为目标的潜在利润（我有进行更多的测试以进行更多的调查，但不会造成潜在的损害）。

Google已经为此奖励了1337美元的奖金，很高兴再次与他们打交道。感谢他们。

如果您有任何问题，意见或信息，您可以通过[Distilled](https://www.distilled.net/)与我联系。



## 披露时间表
- 2017年9月23日 – 我提交了最初的报告。
- 2017年9月25日 – Google回应 – 他们确认错误并正在研究它。
- 2017年10月2日 – 我发送了更多细节。
- 10月9日 – 11月6日 – 一些状态更新。
- 2017年11月6日 – Google表示：“本报告难以确定可以采取哪些措施来防止这种行为及其对搜索结果的影响。我已经与团队联系以获得关于您报告的最终结论。我知道他们一直在对数据进行筛选，以确定您描述的行为有多普遍，以及这是否应该立即采取相应措施。“
- 2017年11月6日 – 我回复说建议他们不跟进跨域的重定向- 没有什么好的理由，它可能只是GSC的一个特性。
- 2018年1月3日 – 我要求更新状态。
- 2018年1月15日 – Google搜索回复道：“对于延迟的道歉，我不过早的结束这份报告，因为我们无法得出一个确定的结论：如何利用重定向链来解决这个问题而不会破坏许多合法的用例。我已经回复给团队审查这份报告以获得最终结论，并会在本周回复您的回复。“
- 2018年2月15日 – Google更新，让我知道报告中存在一个错误，VRP将讨论赏金。
- 2018年3月6日 – Google让我知道了我获得了1337美元的奖金。
- 2018年3月6日 – 我与Google分享了这篇文章的草稿，并要求允许我进行发布。
- 2018年3月12日 – Google让我知道他们还没有完成修复，并要求我再等等。
- 2018年3月25日 – Google确认修复已经上线，并允许我发布这篇文章。


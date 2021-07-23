> 原文链接: https://www.anquanke.com//post/id/176049 


# XSLeaks 攻击分析 —— HTTP缓存跨站点泄漏


                                阅读量   
                                **308205**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t0119e5fae99e86566b.jpg)](https://p3.ssl.qhimg.com/t0119e5fae99e86566b.jpg)



hello~ 我是Mss，今天分享一个很多开发人员和安全人员都很难想到的攻击方式-[XSLeaks](https://github.com/xsleaks/xsleaks)。

## 0x1 XSSearch的前世今生

这种攻击方式最早可以追述到10年前(即2009年)，一个名为Chris Evans的安全人员描述了一次对雅虎的攻击：Chris利用恶意网站去搜索该网站访问者的电子邮件收件箱里的内容，他通过构造不同的关键词的方式在用户的收件箱中搜索，根据返回的时间进行判断该关键词是否存在，比如：搜索“Alice”，如果对方收件箱里有有关Alice的词，则很久才能得到反馈；如果没有，则在很短的时间就能得到反馈。这样，经过多次查询，很快就能搜集大量的信息。你也许觉得这没什么用处，但是如果用来检索密码或者一些商业来往邮件呢？ 但是这种方法有一种弊端，他是基于响应时间来对结果进行判断，而影响相应时间的因素很多。于是在六年后，Nethanel Gelernter和Amir Herzberg更深入地研究了这次攻击，并将其命名为[XSSearch](http://u.cs.biu.ac.il/~herzbea/security/15-01-XSSearch.pdf)，并使用统计学使其结果更加可靠。在接下来的几年中，XSSearch的[攻击方式不断改进](https://github.com/xsleaks/xsleaks/wiki/Links#wiki-pages-box)，不在是拘泥于时间，而是利用浏览器的缓存机制，就这样，XSSearch的[攻击方法](https://github.com/xsleaks/xsleaks/wiki/Browser-Side-Channels)越来越多，攻击方式越来越稳定。



## 0x2 缓存泄露的危害

我们都知道，浏览器会缓存访问过网站的网页，当再次访问这个URL地址的时候，如果网页没有更新，就不会再次下载网页，而是直接使用本地缓存的网页。只有当网站明确标识资源已经更新，浏览器才会再次下载网页。这样不但保证了用户的体验，而且减少了网络带宽消耗和服务器的压力，何乐而不为呢？但是，如果恶意人员有某种技术能看到我们浏览器的缓存，或者说判断我们的浏览器里是否有哪些缓存的话，会发生什么呢？ 他们可能会看到我们的浏览历史，有些人觉得无所谓；但是你们可能不知道，许多网站根据用户的地理位置定制他们的服务，如果这些网站将位置敏感内容留在浏览器缓存中，那么，恶意人员可以通过测量浏览器缓存查询的时间以跟踪受害者的国家，城市和社区，此外，现有的防御措施无法有效防止此类攻击，并且需要额外的支持才能实现更好的防御部署。只有这些吗？通过对缓存内容的查询对方甚至可以知道你有哪些社交账号，利用你的帐户名称进行涉及滥用个人信息，在线欺诈等的各种类型的攻击…… 也许你觉的这么危险那么很多网站应该已经在防范这种攻击了，但在作者看来，大部分的网站还是容易受到攻击的。至于如何防御，将在本文的最后讲到。



## 0x3 利用步骤

这种攻击很有意思，实施起来分为三个步骤

> <ol>
- 删除目标浏览器中特定的缓存
- 打开目标的浏览器查询相关内容
- 检查浏览器是否缓存了相关的内容
</ol>

举个例子，假设你是www.xxx.com的用户，当恶意用户清空你的浏览器里所有有关xxx.com的缓存后，对方利用你的浏览器去访问xxx.com高级会员才能看的内容，如果你是高级会员，那么你的浏览器里就会缓存这部分的内容，反之亦然，恶意用户只需判断你的是否缓存了这部分的内容就可以知道你的身份。 在那篇文章中，作者提出一种实现这种攻击的技巧：

> <ol>
- 删除特定的资源缓存
- 查询缓存是否存在以判断浏览器是否缓存了它
</ol>

我们一步步来：

首先是清空目标的缓存。 可以通过向目标网站发送一个post请求来清空目标内容，有些人可能觉得不可思议，但这是真的，具体可以参考[这篇博客](https://www.mnot.net/blog/2006/02/18/invalidation)；或者设计一个[过长的url](https://lists.gt.net/apache/users/316239)，这样就能使目标服务器报错，并且清空之前的缓存。

其次是访问想要查询的内容。 比如使用[link rel = prerender](https://developers.google.com/web/updates/2018/07/nostate-prefetch)或者直接打开一个新的窗口去访问你要查询的内容，检查资源是否被访问；或者，也可以使用一个过长的url来判断，可能这里很多人不明白，前文说通过构造一个过长的url使浏览器不加载缓存，这里问什么可以用来验证缓存是否存在呢？

很简单，首先这里的“过长的url”只是一种技术，并不是指的同一个url；可以这么理解：假设缓存的是一个图片文件，名字为a.jpg,然后你去通过一个过长的url去访问，因为这样会让浏览器不去加载新的图片，那么浏览器则显示之前的缓存，即a.jpg。[terjanq](https://twitter.com/terjanq)提过了一个很好的[例子](https://xsleaks.github.io/xsleaks/examples/cache-referrer/)，各位在看的时候请注意url栏的变化。



## 0x4 关于防御

在文章中，作者也针对这种攻击对市面上的几款浏览器进行分析（前文说了，现在大多是根据浏览器的缓存机制进行判断），作者认为，这种攻击很难影响使用Safari浏览器的用户，因为Safari浏览器有一个称为“[已验证的分区缓存(Split Disk Cache)](https://webkit.org/blog/8613/intelligent-tracking-prevention-2-1/)”的东西，这是一种阻止用户跟踪的技术，同样也能阻止这种攻击，但是作者认为仍然可以利用这种攻击，只不过相当复杂；chrome浏览器正在试验一种称为“[均分磁盘缓存(Split Disk Cache)](https://bugs.chromium.org/p/chromium/issues/detail?id=910708)”的技术来解决这个问题,如果想要启用这个技术，需要在chrome浏览器的url栏中输入chrome://flags/，设置enable-features = SplitCacheByTopFrameOrigin，但是尴尬的是我在我的chrome（版本 73.0.3683.86-正式版-64位）里没有找到这个；而Firefox采用更进一步的方式“[第一方隔离（First Party Isolation）](https://wiki.mozilla.org/Security/FirstPartyIsolation)”来解决这个问题，用户可以下载[插件](https://addons.mozilla.org/en-US/firefox/addon/first-party-isolation/)或在地址栏中输入about:config找到privacy.firstparty.isolate将其设置为true启用这个功能。 对于开发者，作者也提出一些建议。比如禁用HTTP缓存，使用CSRFToken，但是这两种方法都会给用户的体验感带来影响;作者认为可以通过设置[SameSite-cookies](https://www.owasp.org/index.php/SameSite)来对用户进行设置，但是现在也有些已知的绕过；或者是参考Firefox浏览器采用的[COOP](https://github.com/whatwg/html/issues/3740)；亦或者是参考Facebook尝试做的；当然，也可以参考[这里的想法](https://github.com/xsleaks/xsleaks/wiki/Defenses)。



## 0x5 结言

在文章的最后，作者提到HTTP缓存并不是唯一的信息泄露来源，还有[很多](https://github.com/xsleaks/xsleaks/wiki/Browser-Side-Channels)！感兴趣的朋友可以去看看！我是[掌控安全实验室](http://i.zkaq.org)的Mss，欢迎关注我们的从CVE分析学漏洞专栏，以及新型漏洞跟进分析专题。

附可供拓展研究的参考资料：

[https://www.notion.so/Security-Generic-cross-browser-cross-domain-theft-c01d831c5cf94d9898e99c16adc2e017](https://www.notion.so/Security-Generic-cross-browser-cross-domain-theft-c01d831c5cf94d9898e99c16adc2e017)<br>[https://www.youtube.com/watch?v=vzp7JdezZRU](https://www.youtube.com/watch?v=vzp7JdezZRU)<br>[https://cloud.google.com/storage/docs/access-control/signing-urls-manually](https://cloud.google.com/storage/docs/access-control/signing-urls-manually)<br>[https://www.youtube.com/watch?v=KcOQfYlyIqw&amp;pbjreload=10](https://www.youtube.com/watch?v=KcOQfYlyIqw&amp;pbjreload=10)<br>[https://zh.wikipedia.org/wiki/%E6%97%81%E8%B7%AF%E6%94%BB%E5%87%BB](https://zh.wikipedia.org/wiki/%E6%97%81%E8%B7%AF%E6%94%BB%E5%87%BB)<br>[https://www.cnblogs.com/slly/p/6732749.html](https://www.cnblogs.com/slly/p/6732749.html)<br>[http://sirdarckcat.blogspot.com/2019/03/http-cache-cross-site-leaks.html?m=1](http://sirdarckcat.blogspot.com/2019/03/http-cache-cross-site-leaks.html?m=1)

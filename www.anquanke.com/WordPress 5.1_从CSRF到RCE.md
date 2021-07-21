> 原文链接: https://www.anquanke.com//post/id/173376 


# WordPress 5.1：从CSRF到RCE


                                阅读量   
                                **247929**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ripstech，文章来源：blog.ripstech.com
                                <br>原文地址：[https://blog.ripstech.com/2019/wordpress-csrf-to-rce/](https://blog.ripstech.com/2019/wordpress-csrf-to-rce/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01a07084be2b3f886a.jpg)](https://p2.ssl.qhimg.com/t01a07084be2b3f886a.jpg)



## 一、前言

注：此漏洞利用和环境较为复杂，实际价值可能并不是很高，但对于XSS与权限管理也有一定参考价值。

上个月我们公布了WordPress 5.0中一个远程代码执行（RCE）漏洞（需通过身份认证）。本文公布了WordPress 5.1中存在的另一个严重的漏洞利用链，使未经身份认证的攻击者能够在5.1.1版之前的WordPress中获得远程代码执行权限。



## 二、漏洞影响

如果WordPress站点启用了评论（comment）功能，那么攻击者可以诱骗目标网站管理员访问攻击者设置的一个站点，最终接管目标站点。一旦受害管理员访问恶意网站，攻击者就会在后台通过跨站请求伪造（CSRF）攻击目标WordPress站点，不会因此目标受害者警觉。CSRF攻击中滥用了WordPress中的多个逻辑缺陷及数据过滤错误，并且结合这些缺陷实现RCE，最终完全接管目标站点。

5.1.1版之前默认配置的WordPress受这些漏洞影响。

根据WordPress下载页面的统计数据，互联网上超过33%的站点正在使用WordPress。考虑到博客评论是博客网站的核心功能，默认情况下处于启用状态，因此该漏洞会影响数百万站点。



## 三、技术分析

攻击过程参考[此处视频](https://blog.ripstech.com/videos/wordpress-csrf-to-rce.mp4)。

### <a class="reference-link" name="%E8%AF%84%E8%AE%BA%E8%A1%A8%E5%8D%95%E4%B8%AD%E7%9A%84CSRF"></a>评论表单中的CSRF

当用户发表新评论时，WordPress并没有检查是否存在CSRF。如果执行检查操作，那某些WordPress功能（如[`trackbacks`以及`pingbacks`](https://make.wordpress.org/support/user-manual/building-your-wordpress-community/trackbacks-and-pingbacks/)）将无法正常工作。这意味着攻击者可以通过CSRF攻击，以WordPress博客管理员用户的身份创建评论。

这可能成为一个安全问题，因为WordPress网站管理员可以在评论中使用任意HTML标签，甚至还可以使用`&lt;script&gt;`标签。理论上攻击者可以简单地滥用CSRF漏洞来创建包含恶意JavaScript代码的评论。

WordPress会在评论表单中为管理员生成一个额外的nonce值，通过这种方法尝试解决这个问题。当管理员提交评论并提供有效的nonce值时，WordPress将直接创建评论，没有执行任何过滤此操作。如果nonce值无效，那么评论仍可以创建，但会被过滤处理。

我们可以通过如下代码片段了解WordPress的处理过程。

源文件：`/wp-includes/comment.php`（简化版）：

```
⋮
if ( current_user_can( 'unfiltered_html' ) ) `{`
    if (! wp_verify_nonce( $_POST['_wp_unfiltered_html_comment'], 'unfiltered-html-comment' )) `{`
        $_POST['comment'] = wp_filter_post_kses($_POST['comment']); // line 3242
    `}`
`}` else `{`
    $_POST['comment'] = wp_filter_kses($_POST['comment']);
`}`
⋮
```

事实上，从[2009年](https://core.trac.wordpress.org/ticket/10931)起，WordPress就没有在评论表单中部署CSRF防护机制。

然而，我们发现针对管理员的过滤过程中存在一处逻辑缺陷。如上代码片段中，WordPress始终使用`wp_filter_kses()`来过滤评论，除非创建该评论的是具备`unfiltered_html`功能的管理员。如果满足该条件，并且没有提供有效的nonce值，那么WordPress就会使用`wp_filter_post_kses()`来过滤评论（上述代码第3242行）。

`wp_filter_post_kses()`与`wp_filter_kses()`在严格程度上有所区别。这两个函数都会处理未经过滤的评论，只在字符串中保留特定的HTML标签及属性。通常情况下，使用`wp_filter_kses()`过滤的评论只会留下非常基本的HTML标签及属性，比如`&lt;a&gt;`标签以及`href`属性。

这样攻击者就可以创建一些评论，其中包含比正常评论更多的HTML标签及属性。然而，虽然`wp_filter_post_kses()`更为宽松，但仍会删除可能导致跨站脚本漏洞的HTML标签及属性。

### <a class="reference-link" name="%E5%B0%86HTML%E6%B3%A8%E5%85%A5%E5%8F%98%E6%88%90%E5%AD%98%E5%82%A8%E5%9E%8BXSS"></a>将HTML注入变成存储型XSS

由于我们能注入其他HTML标签及属性，最终还是可以在WordPress中实现存储型XSS。这是因为WordPress会以某种错误的方式解析并处理正常评论中通常不会设置的某些属性，导致出现任意属性注入问题。

当WordPress执行完评论的过滤过程后，就会修改评论字符串中的`&lt;a&gt;`标签，以适配SEO（搜索引擎优化）应用场景。

WordPress会将`&lt;a&gt;`标志的属性字符串（如`href="#" title="some link" rel="nofollow"`）解析成一个关联数组（如下代码片段），其中key为属性名，而value为属性值。

源文件：`wp-includes/formatting.php`

```
function wp_rel_nofollow_callback( $matches ) `{`
    $text = $matches[1];
    $atts = shortcode_parse_atts($matches[1]);
    ⋮
```

随后WordPress会检查其中是否设置了`rel`属性。只有通过`wp_filter_post_kses()`过滤评论时才会设置该属性。如果设置了该属性，则WordPress会处理`rel`属性，然后再次与`&lt;a&gt;`标签拼接起来。

源文件：`wp-includes/formatting.php`

```
if (!empty($atts['rel'])) `{`
        // the processing of the 'rel' attribute happens here
        ⋮
        $text = '';
        foreach ($atts as $name =&gt; $value) `{`            // line 3017
            $text .= $name . '="' . $value . '" ';        // line 3018
        `}`
    `}`
    return '&lt;a ' . $text . ' rel="' . $rel . '"&gt;';        // line 3021
`}`
```

上述代码第3017及3018行处存在缺陷，其中属性值在没有被转义处理的情况下就再次拼接在一起。

攻击者可以创建包含精心构造的`&lt;a&gt;`标签的评论，并将`title`属性设置为`title='XSS " onmouseover=alert(1) id="'`。这个属性是合法的HTML数据，因此可以通过数据过滤检查。然而，只有当`title`标签使用单引号时这种方法才有效。

当属性再次拼接时，`title`属性会被封装到双引号中（第3018行）。这意味着攻击者可以注入双引号，闭合`title`属性，因此可以注入其他HTML属性。

比如：`&lt;a title='XSS " onmouseover=evilCode() id=" '&gt;`在处理之后会变成`&lt;a title="XSS " onmouseover=evilCode() id=" "&gt;`。

由于此时评论已经被过滤处理过，因此攻击者注入的`onmouseover`事件处理函数会存储在数据库中，不会被删除。将这种过滤缺陷与CSRF漏洞结合起来，攻击者就可以将存储型XSS payload注入目标网站中。

### <a class="reference-link" name="%E9%80%9A%E8%BF%87iframe%E7%9B%B4%E6%8E%A5%E6%89%A7%E8%A1%8CXSS"></a>通过iframe直接执行XSS

创建恶意评论后，为了实现远程代码执行（RCE），下一步攻击者需要让管理员执行已注入的JavaScript。WordPress评论会在目标博客的前端显示，而WordPress本身并没有使用`X-Frame-Options`来保护前端页面。这意味着攻击者可以以隐藏`iframe`的方式在网站上显示评论。由于注入的属性是一个`onmouseover`事件处理函数，因此攻击者可以让`iframe`跟随受害者鼠标，立刻触发XSS payload。

这样一来，攻击者就可以在目标网站上使用触发CSRF漏洞的管理员会话来执行任意JavaScript代码。有所的JavaScript都在后台执行，不会引起管理员的注意。

### <a class="reference-link" name="%E6%8F%90%E5%8D%87%E8%87%B3RCE"></a>提升至RCE

现在攻击者已经可能使用管理员会话来执行任意JavaScript代码，那么也很容易就能实现RCE。默认情况下，WordPress允许博客管理员在管理面板中直接编辑站点主题和插件的`.php`文件。攻击者只需要简单插入一个PHP后门，就可以在远程服务器上获得任意PHP代码执行权限。



## 四、补丁情况

默认情况下，WordPress会自动安装安全更新，因此我们应该已经更新至最新的5.1.1版。如果用户或所属托管商由于某些原因禁用了自动更新功能，那么在安装补丁前，可以考虑禁用评论功能。更为重要的一点是，请管理员确保访问其他网站之前，已经注销当前的管理员会话。



## 五、时间线
- 2018/10/24：反馈漏洞报告，说明攻击者有可能通过CSRF在WordPress中注入更多的HTML标签
- 2018/10/25：WordPress官方在Hackerone上将该漏洞报告进行分类
- 2019/02/05：WordPress提供了一个安全补丁，我们测试后提供了反馈
- 2019/03/01：通知WordPress我们可以将HTML注入升级为存储型XSS漏洞
- 2019/03/01：WordPress与我们沟通，表示安全团队的某个成员已经发现该问题，准备推出补丁
- 2019/03/13：WordPress 5.1.1发布


## 六、总结

本文从CSRF漏洞开始介绍了一个完整的漏洞利用链。攻击者只需要诱导目标网站管理员访问某个恶意网站，然后就可以通过这条利用链来接管使用默认配置的WordPress站点。目标管理员并不会发现攻击者的网站有任何异常，除了访问攻击者设置的网站之外，整条攻击链中没有其他交互过程。

感谢WordPress安全团队，这些小伙伴们非常友善，并且合作解决问题时也非常专业。

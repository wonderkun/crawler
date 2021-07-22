> 原文链接: https://www.anquanke.com//post/id/168243 


# WordPress权限提升导致存储型XSS和对象注入漏洞分析


                                阅读量   
                                **190614**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ripstech，文章来源：blog.ripstech.com
                                <br>原文地址：[https://blog.ripstech.com/2018/wordpress-post-type-privilege-escalation/](https://blog.ripstech.com/2018/wordpress-post-type-privilege-escalation/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/dm/1024_576_/t01bb72d3ec651e8cb2.jpg)](https://p3.ssl.qhimg.com/dm/1024_576_/t01bb72d3ec651e8cb2.jpg)



## 概述

WordPress在创建博客文章的过程中存在逻辑缺陷，允许攻击者具有与管理员相同的权限。该漏洞导致WordPress核心产生存储型XSS和对象注入等严重漏洞，并且可能导致WordPress最受欢迎的插件Contact Form 7和Jetpack中出现更为严重的漏洞。



## 影响：攻击者可以做什么

WordPress的本质上是一个博客软件，允许用户创建和发布帖子。随着时间的推移，WP上引入了不同的帖子类型（Post Type），例如页面和媒体项目（包括图像、视频等）。插件可以注册新的帖子类型，例如产品、联系表单等。根据插件新注册的帖子类型，WordPress也随之具有新的功能。例如，联系表单（Contact Form）插件可能允许创建具有文件上传字段的联系表单，可用于提交简历等方面。创建联系表单的用户可以定义允许的文件类型。在这里，攻击者也可以通过上传PHP文件，然后在网站上实现任意代码执行。这一点并不是问题，因为插件可以限制用户对管理员注册的帖子类型的访问，同时信任WordPress来处理这一限制。我们在本文中要讨论的权限提升漏洞，允许较低权限的用户绕过WordPress实施的安全检查，创建任何类型的帖子，并滥用自定义帖子的功能。这将会导致WordPress核心中产生存储型XSS漏洞和对象注入漏洞。根据WordPress中已安装插件的不同，还可能导致更严重的插件漏洞利用。例如，如果使用了WordPress最受欢迎、已经超过500万次安装的插件Contact Form 7，攻击者可以读取目标WordPress站点的数据库凭据。大多数流行的WordPress插件都容易受到该权限提升漏洞的影响。



## 技术背景

要注册新的帖子类型，插件需要使用新帖子类型名称和一些meta信息来调用register_post_type()。

```
// Example post type
register_post_type( 'example_post_type', array(
    'label' =&gt; 'Example Post Type',     // The name of the type in the front end
    'can_export' =&gt; true,               // Make it possible to export posts of this type,
    'description' =&gt; 'Just an example!' // A short description
));
```

### <a class="reference-link" name="%E8%87%AA%E5%AE%9A%E4%B9%89%E5%B8%96%E5%AD%90%E7%B1%BB%E5%9E%8B%E5%AE%89%E5%85%A8%E6%80%A7%E5%88%86%E6%9E%90"></a>自定义帖子类型安全性分析

每种帖子类型，都有其自身的编辑器页面（例如 example.com/wordpress/wp-admin/?page=example_post_type_editor ）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.ripstech.com/img/2018/wordpress-post-type-privesc/cf7.png)<br>
如果插件开发人员决定只允许管理员使用插件的帖子类型，那么只需要在页面顶部的位置检查用户是否为管理员，否则就结束执行。

在/wp-content/plugins/example_plugin/example_post_type_editor.php中：

```
if(!current_user_is_administrator()) `{`
    die("You are not an administrator and not allowed to use this post type.");
`}`
```

### <a class="reference-link" name="WordPress%E5%B8%96%E5%AD%90%E6%8F%90%E4%BA%A4"></a>WordPress帖子提交

尽管所有已注册的帖子类型，都有其对应的编辑器，但它们都可以使用WordPress帖子来提交API，并使用WordPress函数wp_write_post()来插入和更新帖子。该函数接受用户的输入，例如 $_POST[‘post_type’] 、 $_POST[‘post_title’] 和 $_POST[‘post_content’]，并按照相应的方式处理帖子。

在WordPress帖子提交过程的第一步，WordPress必须首先判断用户是想要编辑现有的帖子还是要创建新的帖子。为此，WordPress会检查用户是否已经发送帖子的ID。WordPress允许$_GET[‘post’] 或 $_POST[‘post_ID’]。如果ID已经存在，那么就证明用户想要编辑该ID的已有帖子，否则证明用户想要创建新的帖子。

/wp-admin/post.php中相关代码如下：

```
if ( isset( $_GET['post'] ) )
    $post_id = $post_ID = $_GET['post'];
elseif ( isset( $_POST['post_ID'] ) )
    $post_id = $post_ID = $_POST['post_ID'];

if($post_id)
    ⋮
```

在下一步中，WordPress必须确定用户尝试创建的帖子类型。如果已经发送帖子ID，那么WordPress将从wp_posts表中提取数据库中的post_type列。如果用户想要创建新帖子，那么目标帖子类型将为$_POST[‘post_type’]。

/wp-admin/post.php中相关代码如下：

```
if ( isset( $_GET['post'] ) )
    $post_id = $post_ID = $_GET['post'];
elseif ( isset( $_POST['post_ID'] ) )
    $post_id = $post_ID = $_POST['post_ID'];

if($post_id)
    $post_type = get_post_type($post_id);
else
    $post_type = $_POST['post_type'];
```

一旦WordPress清楚用户试图创建或编辑的帖子的类型，就会检查用户实际上是否被允许使用该帖子类型。WordPress通过验证只能从相应帖子类型的编辑器页面获取的随机数来完成此操作。

要进行随机数验证，WordPress将使用以下代码（位于/wp-admin/post.php中）：

```
if($post_id)
    $post_type = get_post_type($post_id);
else
    $post_type = $_POST['post_type'];

$nonce_name = "add-" . $post_type;
if(!wp_verify_nonce($_POST['nonce'], $nonce_name))
    die("You are not allowed to use this post type!");
```

如果$post_type是post，那么$nonce_name将是add-post。如果$post_type是example_post_type，那么对应的$nonce_name则会是add-example_post_type。这个nonce只能由具有创建相应帖子类型权限的用户获取，因为只有这些用户才能访问到该帖子类型的编辑器页面，这是获取nonce的唯一方法。



## 漏洞分析

尽管权限较低的攻击者（例如攻击者以Contributor角色登录）无法访问示例帖子类型（example_post_type）的页面和nonce，但他可以获得普通帖子的nonce，其中就包含内部帖子类型post。这意味着，攻击者可以轻松将帖子ID设置为post类型的帖子，这样一来就可以通过nonce的验证。

在/wp-admin/post.php中相关代码如下：

```
// Send a post ID of a post of post type 'post'
if($post_id)
    // This would return 'post'
    $post_type = get_post_type($post_id);
else
    $post_type = $_POST['post_type'];

// All users can by default create 'posts' and get the nonce to pass this check
$nonce_name = "add-" . $post_type;
if(!wp_verify_nonce($nonce_name))
    die("You are not allowed to create posts of this type!");
```

然而，该方法仅允许更新现有帖子，并且无法覆盖帖子的post_type。如果设置了帖子ID，WordPress将在更新帖子之前从参数中删除post_type。

但是，如果设置了$_POST[‘post_ID’]，WordPress就只会删除$post_type参数。攻击者可以通过 $_POST[‘post_ID’] 或 $_GET[‘post’] 来发送帖子ID。如果攻击者通过$_GET[‘post’]发送帖子ID，那么就会发生以下情况：

1、WordPress发现该帖子ID存在，并从数据库中提取其帖子类型。

2、WordPress会检查攻击者是否针对该帖子类型发送了一个有效的nonce（攻击者可以随时从正常帖子中得到）

3、一旦通过了nonce检查，WordPress就会确认是否应该调用wp_update_post() 或 wp_insert_post()。具体而言，是通过检查是否设置了$ _POST [‘post_ID’]来实现这一操作。如果是，将会调用wp_update_post并删除$ post_type参数，从而不允许攻击者修改帖子类型。如果没有设置，WordPress将会调用wp_insert_post()并使用$_POST[‘post_type’]作为新帖子的帖子类型。

由于WordPress在第三步中没有检查$_GET[‘post’]，导致攻击者可以通过nonce验证，并创建一个任意帖子类型的新帖子。下面展现的代码片段已经经过简化，实际上是在多个文件之间进行了多次函数调用，这样一来使得该过程更容易出现漏洞。

```
// An attacker sets $_GET['post'] to a post of a post type he can access
if ( isset( $_GET['post'] ) )
    $post_id = $post_ID = $_GET['post'];
elseif ( isset( $_POST['post_ID'] ) )
    $post_id = $post_ID = $_POST['post_ID'];

if($post_id)
    // The post type is now 'post'
    $post_type = get_post_type($post_id);
else
    $post_type = $_POST['post_type'];

// Since the attacker has access to that post type, he can get the nonce and
// pass the nonce verification check
$nonce_name = "add-" . $post_type;
if(!wp_verify_nonce($nonce_name))
    die("You are not allowed to create posts of this type!");

$post_details = array(
  'post_title' =&gt; $_POST['post_title'],
  'post_content' =&gt; $_POST['post_content'],
  'post_type' =&gt; $_POST['post_type']
);

// WordPress only unsets the post_type if $_POST['post_ID'] is set and forgets to
// check $_GET['post']
if(isset($_POST['post_ID'])) `{`

    unset($post_details['post_type']);
    $post_details['ID'] = $post_id;
    wp_update_post($post_details);
`}` else `{`
    // If we just set $_GET['post'] we will enter this branch and can set the
    // post type to anything we want it to be!
    wp_insert_post($post_details);
`}`
```



## 漏洞利用：通过Contact Forms 7读取wp-config.php

到目前为止，我们已经掌握了较低权限的用户是如何滥用这一漏洞来创建任意类型帖子的，并且我们知道这一漏洞对站点的影响取决于所安装的插件以及这些插件提供的帖子类型的功能。

举一个具体的例子，作为Contributor角色的攻击者，有可能滥用WordPress最流行的插件Contact Form 7中的一个功能，来读取目标站点的wp-config.php文件的内容。该文件中包含数据库凭据和加密密钥。

在Contact Forms 7的5.0.3版本中，可以设置本地文件的附件。当管理员创建联系表单，并且页面的访问者提交该表单时，会向管理员发送一封电子邮件，其中包含用户输入的所有数据。本地文件附件是联系表单的一个功能，管理员可以定义随每封电子邮件附件发送的本地文件。

这意味着，攻击者可以轻松地创建一个新的联系表单，将本地文件附件设置为../wp-config.php，并设置将数据发送到攻击者的邮箱中，随后提交表单，并阅读邮箱收到的最重要的WordPress配置文件。



## 针对开发人员的漏洞修复方法

插件开发者应该通过在调用register_post_type()时显式设置apability和capability_type参数，来进一步增强插件的安全性。

```
// Example post type
register_post_type( 'example_post_type', array(
    'label' =&gt; 'Example Post Type',     

    'capability_type' =&gt; 'page'     // capability_type of page makes sure that
                                    // only editors and admins can create posts of 
                                    // that type
));
```

建议开发人员阅读有关使用register_post_type进行帖子类型安全性加固的WordPress文档：

[https://codex.wordpress.org/Function_Reference/register_post_type#capability_type](https://codex.wordpress.org/Function_Reference/register_post_type#capability_type)



## WordPress的XMLRPC和REST API

作为防范方法，可以通过WordPress的XMLRPC和REST API来创建帖子，这些帖子不会对特定帖子类型执行随机数验证。但是，再通过这些API创建帖子时，无法设置任意post meta字段。我们发现的大多数插件中的漏洞，只有在用户能够设置post meta时才可以利用。



## 时间线

2018年8月31日 通过官网上的联系表格，向Contact Form 7报告了漏洞

2018年9月2日 在Hackerone上报告了WordPress的漏洞

2018年9月4日 Contact Form 7通知已修复此漏洞

2018年9月27日 WordPress安全团队对Hackerone上的漏洞进行了确认

2018年10月12日 WordPress在Hackerone上发布了一个补丁

2018年10月18日 我们验证该补丁有效

2018年12月13日 WordPress在发布5.0.1版本补丁



## 总结

借助本文所分析的漏洞，具有低于Contributor（这是WordPress中倒数第二个级别的角色）权限的攻击者可以创建他们无法访问的帖子类型的帖子。这样一来，攻击者就可以访问到仅限于管理员使用的功能。到目前为止，我们已经发现在WordPress流行度排名前五的插件里有2个插件存在该漏洞，我们估计可能会有数千个插件容易受到该漏洞的影响。此外，在WordPress的一个内部帖子类型中，我们还发现了存储型XSS和对象注入漏洞。存储型XSS可以通过点击劫持攻击来触发。在执行JavaScript后，可以实现完整的站点接管。

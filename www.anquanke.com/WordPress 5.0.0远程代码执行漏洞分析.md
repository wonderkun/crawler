> 原文链接: https://www.anquanke.com//post/id/171357 


# WordPress 5.0.0远程代码执行漏洞分析


                                阅读量   
                                **308298**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ripstech，文章来源：blog.ripstech.com
                                <br>原文地址：[https://blog.ripstech.com/2019/wordpress-image-remote-code-execution/](https://blog.ripstech.com/2019/wordpress-image-remote-code-execution/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01e10cd89118ddf272.png)](https://p2.ssl.qhimg.com/t01e10cd89118ddf272.png)



## 一、概要

本文详细介绍了如何通过路径遍历及本地文件包含（LFI）漏洞，在WordPress中实现远程代码执行（RCE）。该漏洞在WordPress中已存在6年之久。攻击视频参考[此处](https://blog.ripstech.com/videos/wordpress-image-rce.mp4)链接。

在WordPress站点上，如果攻击者具备`author`及以上权限，就可以在底层服务器上执行任意PHP代码，最终可以远程完全接管整个站点。我们已经向WordPress安全团队反馈了另一个漏洞，该漏洞也能让攻击者在任意WordPress站点上获得类似访问权限，目前后一个漏洞尚未修复。



## 二、受影响版本

在4.9.9及5.0.1版本中，由于另一个安全补丁的存在，因此本文介绍的漏洞无法顺利利用。然而路径遍历漏洞依然可能存在，并且当前处于未修复状态。任何WordPress站点如果安装了无法正确处理`Post Meta`条目的插件，漏洞就可能利用成功。在我们的[WordPress安全月](https://blog.ripstech.com/2019/wordpress-security-month/)活动中，我们已经发现了某些流行插件（活跃安装量达数百万计）存在这类问题。

根据WordPress下载页面的统计数据，互联网上超过[33%](https://blog.ripstech.com/2019/wordpress-image-remote-code-execution/#fn:1)的站点正在使用WordPress。考虑到插件可能会带来新的问题，并且有些网站并没有及时更新，因此我们认为受影响的站点数仍达数百万个。



## 三、技术分析

我们使用自己研发的SAST解决方案RIPS（参考[示例](https://demo-3.ripstech.com/scan/44/55)），在3分钟内就检测到了路径遍历及本地文件包含漏洞。然而，初步分析时这些漏洞似乎无法使用。经过详细调研，事实证明这些漏洞利用起来虽然非常复杂，但的确有可能成功利用。

攻击过程及原理示意请参考[此处](https://blog.ripstech.com/videos/wordpress-image-rce-animation.mp4)视频。

### <a class="reference-link" name="%E8%83%8C%E6%99%AF%EF%BC%9AWordPress%E5%9B%BE%E5%83%8F%E7%AE%A1%E7%90%86"></a>背景：WordPress图像管理

当我们将图像上传到WordPress站点时，图像首先会被存放到上传目录中（`wp-content/uploads`）。WordPress也会在数据库中创建该图像的一个内部引用，以跟踪图像的元信息（如图像所有者或上传时间）。

这种元信息以`Post Meta`条目形式存放在数据库中，每个条目都包含一对key/value，与某个特定的ID相对应。以`evil.jpg`这张上传图像为例，相关`Post Meta`如下所示：

```
MariaDB [wordpress]&gt; SELECT * FROM wp_postmeta WHERE post_ID = 50;
+---------+-------------------------+----------------------------+
| post_id | meta_key                | meta_value                 |
+---------+-------------------------+----------------------------+
|      50 | _wp_attached_file       | evil.jpg                   |
|      50 | _wp_attachment_metadata | a:5:`{`s:5:"width";i:450 ... |
...
+---------+-------------------------+----------------------------+
```

在本例中，图片所对应的`post_ID`值为50。如果用户后续想使用该`ID`来使用或者编辑该图像，WordPress会查找匹配的`_wp_attached_file`元数据条目，使用其对应的值在`wp-content/uploads`目录中定位该文件。

### <a class="reference-link" name="%E6%A0%B9%E6%9C%AC%E9%97%AE%E9%A2%98%EF%BC%9A%20Post%20Meta%E5%8F%AF%E8%A2%AB%E8%A6%86%E7%9B%96"></a>根本问题： Post Meta可被覆盖

在WordPress 4.9.9和5.0.1之前的版本中，`Post Meta`条目可以被修改，被设置为任意值。

当某张图像被更新时（如图像描述发生改动），那么WordPress就会调用`edit_post()`函数，该函数直接作用于`$_POST`数组。

```
function edit_post( $post_data = null ) `{`

    if ( empty($postarr) )
        $postarr = &amp;$_POST;
    ⋮
    if ( ! empty( $postarr['meta_input'] ) ) `{`
        foreach ( $postarr['meta_input'] as $field =&gt; $value ) `{`
            update_post_meta( $post_ID, $field, $value );
        `}`
    `}`
```

如上所示，攻击者有可能注入任意`Post Meta`条目。由于WordPress并没有检查哪些条目被修改过，因此攻击者可以更新`_wp_attached_file`元数据，将其设置为任意值。该操作并不会重命名文件，只是修改了WordPress在尝试编辑目标图像时所要寻找的文件。这将导致路径遍历问题，后面我们会进一步分析。

### <a class="reference-link" name="%E4%BF%AE%E6%94%B9Post%20Meta%E5%AE%9E%E7%8E%B0%E8%B7%AF%E5%BE%84%E9%81%8D%E5%8E%86"></a>修改Post Meta实现路径遍历

路径遍历问题存在于`wp_crop_image()`函数中，当用户裁剪图像时，该函数就会被调用。

该函数会获取待裁剪的图像ID值（`$attachment_id`），并从数据库中获取相应的`_wp_attached_file` `Post Meta`信息。

需要注意的是，由于`edit_post()`中存在缺陷，因此`$src_file`可以被设置为任意值。

简化版的`wp_crop_image()`函数如下，实际代码位于`wp-admin/includes/image.php`文件中。

```
function wp_crop_image( $attachment_id, $src_x, ...) `{`

    $src_file = $file = get_post_meta( $attachment_id, '_wp_attached_file' );
    ⋮
```

在下一步中，WordPress必须确保图像实际存在并加载该图像。在WordPress中加载指定图像有两种方法。第一种是简单地在`wp-content/uploads`目录中，利用`_wp_attached_file` `Post Meta`信息查找指定的文件名（参考下一个代码段的第二行）。

如果该方法查找失败，则WordPress会尝试从站点服务器上下载该图像，这是一种备用方案。为了完成该操作，WordPress会生成一个下载URL，该URL中包含`wp-content/uploads`目录对应的URL以及`_wp_attached_file` `Post Meta`条目中存储的文件名（如下代码片段第6行）。

举一个具体例子：如果`_wp_attached_file` `Post Meta`条目中存储的值为`evil.jpg`，那么WordPress首先会尝试检查`wp-content/uploads/evil.jpg`文件是否存在。如果该文件不存在，则尝试从`https://targetserver.com/wp-content/uploads/evil.jpg`这个URL下载该文件。

之所以尝试下载文件，而不是在本地搜索文件，原因在于某些插件会在用户访问URL时动态生成图像。

请注意，这个过程并没有进行任何过滤处理。WordPress只会简单地将上传目录以及URL拼接起来（URL中包含用户输入的`$src_file`）。

一旦WordPress通过`wp_get_image_editor()`成功加载一个有效的图像，就会进行裁剪处理。

```
⋮
    if ( ! file_exists( "wp-content/uploads/" . $src_file ) ) `{`
            // If the file doesn't exist, attempt a URL fopen on the src link.
            // This can occur with certain file replication plugins.
            $uploads = wp_get_upload_dir();
            $src = $uploads['baseurl'] . "/" . $src_file;
        `}` else `{`
            $src = "wp-content/uploads/" . $src_file;
        `}`

    $editor = wp_get_image_editor( $src );
    ⋮
```

经过裁剪的图片随后会被保存回文件系统中（无论是下载文件还是本地文件）。保存文件所使用的文件名为`get_post_meta()`所返回的`$src_file`，而攻击者可以控制这个值。代码中对文件名做的唯一一处修改是为文件的basename（去掉文件名的目录及后缀）添加`cropped-`前缀字符串（如下代码段中第4行）。以前面的`evil.jpg`为例，这里生成的结果文件名为`cropped-evil.jpg`。

如果结果文件路径不存在，则WordPress随后会使用`wp_mkdir_p()`创建相应的目录（参考第6行代码）。

随后，WordPress使用图像编辑器对象的`save()`方法，将图像最终写入文件系统中。`save()`方法也没有对给定的文件名执行目录遍历检查。

```
⋮
    $src = $editor-&gt;crop( $src_x, $src_y, $src_w, $src_h, $dst_w, $dst_h, $src_abs );

    $dst_file = str_replace( basename( $src_file ), 'cropped-' . basename( $src_file ), $src_file );

    wp_mkdir_p( dirname( $dst_file ) );

    $result = $editor-&gt;save( $dst_file );
```

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E6%80%9D%E8%B7%AF"></a>利用思路

到目前为止，我们已经分析了哪个文件可能会被载入图像编辑器中，因为WordPress没有执行过滤操作。然而，如果该文件并不是有效的图像，那么图像编辑器就会抛出异常。因此这里第一个假设是，WordPress只能裁剪上传目录外的图像。

然而，由于WordPress在没找到图像时会尝试下载图像，因此会导致远程代码执行（RCE）漏洞。

||本地文件|HTTP下载文件
|------
|上传的文件|evil.jpg|evil.jpg
|_wp_attached_file|evil.jpg?shell.php|evil.jpg?shell.php
|待加载的结果文件|wp-content/uploads/evil.jpg?shell.php|[https://targetserver.com/wp-content/uploads/evil.jpg?shell.php](https://targetserver.com/wp-content/uploads/evil.jpg?shell.php)
|实际位置|wp-content/uploads/evil.jpg|[https://targetserver.com/wp-content/uploads/evil.jpg](https://targetserver.com/wp-content/uploads/evil.jpg)
|结果文件名|None – 文件加载失败|evil.jpg?cropped-shell.php

我们可以将`_wp_attached_file`的值设置为`evil.jpg?shell.php`，这样WordPress就会发起一个HTTP请求，请求URL为`https://targetserver.com/wp-content/uploads/evil.jpg?shell.php`。由于在该上下文中，`?`后的所有字符都会被忽略，因此该请求会返回一个有效的图像文件。最终结果文件名会变成`evil.jpg?shell.php`。

然而，虽然图像编辑器的`save()`方法没有检查路径遍历攻击，但会将待加载的图像的`mime`扩展名附加到结果文件名中。在本例中，生成的文件名将为`evil.jpg?cropped-shell.php.jpg`。这样可以让新创建的文件再次保持无害状态。

然而，我们还是可以使用类似`evil.jpg?/../../evil.jpg`的载荷，将结果图像植入任意目录中。

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E8%B7%AF%E5%BE%84%E9%81%8D%E5%8E%86%EF%BC%9ATheme%E7%9B%AE%E5%BD%95%E4%B8%AD%E7%9A%84LFI"></a>利用路径遍历：Theme目录中的LFI

每个WordPress主题实际上都是位于`wp-content/themes`目录中的一个子目录，可以为不同场景提供模板文件。比如，如果博客的某位访问者想查看博客文章，WordPress则会在当前激活的主题中查找`post.php`文件。如果找到模板，则会`include()`该模板。

为了支持额外的自定义层，我们可以为某些文章选择自定义模板。为了完成该任务，用户需要设置数据库中的`_wp_page_template` `Post Meta`条目，将其设置为自定义文件名。这里唯一的限制条件是：待`include()`的文件必须位于当前激活的主题目录中。

通常情况下，该目录无法访问，并且不会有文件上传到该目录中。然而，攻击者可以滥用前文描述的路径遍历漏洞，将恶意构造的图像植入当前使用的主题目录中。随后攻击者可以创建一个新的帖子，滥用同一个bug，更新`_wp_attached_file` `Post Meta`数据库条目，以便`include()`该图像。将PHP代码注入图像后，攻击者随后就能获得任意远程代码执行权限。

### <a class="reference-link" name="%E6%9E%84%E9%80%A0%E6%81%B6%E6%84%8F%E5%9B%BE%E5%83%8F%EF%BC%9AGD%E5%8F%8AImagick"></a>构造恶意图像：GD及Imagick

WordPress支持PHP的两种图像编辑扩展：[GD](https://libgd.github.io/)以及[Imagick](https://www.imagemagick.org/)。这两者有所不同，Imagick并不会删除图像的`exif`元数据，这样我们就可以将PHP代码藏身其中。GD会压缩每张图像，删除所有的`exif`元数据。

然而，我们还是可以制作包含精心构造的像素的图像来利用漏洞，当GD裁剪完图像后，这些像素会以某种方式进行反转，最终达到PHP代码执行执行目标。在我们研究PHP GD扩展的内部结构过程中，`libgd`又爆出可被利用的一个内存破坏漏洞（[CVE-2019-6977](https://blog.ripstech.com/2019/wordpress-image-remote-code-execution/#fn:2)）。



## 四、时间线

|日期|事件
|------
|2018/10/16|我们在Hackerone上将漏洞反馈给WordPress
|2018/10/18|某个WordPress安全团队成员确认该报告，并表示在验证报告后会回头联系我们
|2018/10/19|另一个WordPress安全团队成员请求了解更多信息
|2018/10/22|我们向WordPress提供了更多信息，并提供了包含270行利用代码的完整脚本，帮助对方确认漏洞
|2018/11/15|WordPress触发该漏洞，表示可以复现该漏洞
|2018/12/06|WordPress 5.0发布，没有修复该漏洞
|2018/12/12|WordPress 5.0.1发布，包含安全更新。某个补丁会阻止攻击者任意设置post meta条目，因此使该漏洞无法直接利用。然而，路径遍历漏洞依然存在，并且如果已安装的插件没有正确处理Post Meta条目就可以利用该漏洞。WordPress 5.0.1并没有解决路径遍历或者本地文件包含漏洞
|2018/12/19|WordPress 5.0.2发布，没有修复漏洞
|2019/01/09|WordPress 5.0.3发布，没有修复漏洞
|2019/01/28|我们询问WordPress下一个安全版本的发布时间，以便协调我们的文章公布时间，准备在补丁发布后公布我们的分析文章
|2019/02/14|WordPress推出补丁
|2019/02/14|我们提供补丁反馈，验证补丁的确能缓解漏洞利用过程



## 五、总结

本文介绍了WordPress中存在的一个远程代码执行漏洞，该漏洞存在时间已超过6年。RIPS报告了5.0.1版以及4.9.9版中的另一个漏洞，打上该漏洞补丁后，这个RCE漏洞也无法正常利用。然而如果目标站点安装了允许覆盖任意Post Data的插件，那么依然可以利用路径遍历漏洞。由于我们在攻击目标WordPress站点时需要通过身份认证，因此我们决定在报告漏洞4个月后再公开该漏洞。

感谢WordPress安全团队的志愿者们，他们在该问题沟通上非常友好并且非常专业。

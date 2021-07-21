> 原文链接: https://www.anquanke.com//post/id/171488 


# WordPress 5.0 RCE 详细分析


                                阅读量   
                                **207906**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01afb21d3859caf378.jpg)](https://p3.ssl.qhimg.com/t01afb21d3859caf378.jpg)



2月20号，RIPS团队在官网公开了一篇[WordPress 5.0.0 Remote Code Execution](https://blog.ripstech.com/2019/wordpress-image-remote-code-execution/)，CVE编号CVE-2019-6977，文章中主要提到在author权限账号下，可以通过修改Post Meta变量覆盖、目录穿越写文件、模板包含3个漏洞构成一个RCE漏洞。

但在原文中，作者只大致描述了漏洞原理，其中大量的漏洞细节被省略，甚至部分的利用和后端服务器也有相对应的关系，所以在复现的过程中遇到了各种问题，我们花了大量的时间分析代码，最终终于完全还原了该漏洞，其中部分关键利用点用了和原文有些许差异的利用方式（原文说的太含糊其辞，无法复现）。在下面的分析中，我会尽量按照复现过程中的思考方式及流程，以便读者理解。

感谢在复现、分析过程中一起的小伙伴@Badcode，帮助我修改了很多错误的@Venenof7、@sysorem,给我提供了很多帮助:&gt;



## 漏洞要求

在反复斟酌漏洞条件之后，我们最终把漏洞要求约束为
- [WordPress commit &lt;= 43bdb0e193955145a5ab1137890bb798bce5f0d2 （WordPress 5.1-alpha-44280）](https://github.com/WordPress/WordPress/commit/43bdb0e193955145a5ab1137890bb798bce5f0d2)
- 拥有一个author权限的账号
影响包括windows、linux、mac在内的服务端，后端图片处理库为gd/imagick都受到影响，只不过利用难度有所差异。

其中，原文提到只影响release 5.0.0版，但现在官网上可以下载的5.0.0已经修复该漏洞。实际在WordPress 5.1-alpha-44280更新后未更新的4.9.9~5.0.0的WordPress都受到该漏洞影响。



## 漏洞复现

下面的复现流程包含部分独家利用以及部分与原文不符的利用方式，后面的详情会解释原因。

传图片

[![](https://p5.ssl.qhimg.com/t016131ba7a4ea9291d.png)](https://p5.ssl.qhimg.com/t016131ba7a4ea9291d.png)

改信息

[![](https://p0.ssl.qhimg.com/t01f896117f0c47f9fe.png)](https://p0.ssl.qhimg.com/t01f896117f0c47f9fe.png)

保留该数据包，并添加POST

```
&amp;meta_input[_wp_attached_file]=2019/02/2-4.jpg#/../../../../themes/twentynineteen/32.jpg
```

[![](https://p3.ssl.qhimg.com/t01883561d14c45f041.png)](https://p3.ssl.qhimg.com/t01883561d14c45f041.png)

裁剪

[![](https://p2.ssl.qhimg.com/t012bb4e77698e2f61c.png)](https://p2.ssl.qhimg.com/t012bb4e77698e2f61c.png)

同理保留改数据包，并将POST改为下面的操作，其中nonce以及id不变

```
action=crop-image&amp;_ajax_nonce=8c2f0c9e6b&amp;id=74&amp;cropDetails[x1]=10&amp;cropDetails[y1]=10&amp;cropDetails[width]=10&amp;cropDetails[height]=10&amp;cropDetails[dst_width]=100&amp;cropDetails[dst_height]=100
```

触发需要的裁剪

[![](https://p5.ssl.qhimg.com/t01df19f56014a34e79.png)](https://p5.ssl.qhimg.com/t01df19f56014a34e79.png)

图片已经过去了

[![](https://p0.ssl.qhimg.com/t01e81239d8cb1e0c21.png)](https://p0.ssl.qhimg.com/t01e81239d8cb1e0c21.png)

包含，我们选择上传一个test.txt，然后再次修改信息，如前面

```
&amp;meta_input[_wp_page_template]=cropped-32.jpg
```

[![](https://p1.ssl.qhimg.com/t017c79bd3a204ab4d3.png)](https://p1.ssl.qhimg.com/t017c79bd3a204ab4d3.png)

点击查看附件页面，如果图片被裁剪之后仍保留敏感代码，则命令执行成功。

[![](https://p0.ssl.qhimg.com/t013ba5f9c0148c2ca0.png)](https://p0.ssl.qhimg.com/t013ba5f9c0148c2ca0.png)



## 详细分析

下面我们详细分析一下整个利用过程，以及在各个部分踩的坑。我们可以简单的把漏洞利用链分为4个大部分。

1、通过Post Meta变量覆盖，修改媒体库中图片的_wp_attached_file变量。

这个漏洞是整个利用链的核心点，而WordPress的修复方式也主要是先修复了这个漏洞。WordPress很良心的在所有的release版本中都修复了这个问题（官网下载的5.0.0已经修复了），由于原文中曾提到整个利用链受到4.9.9和5.0.1的另一个安全补丁影响，所以只有5.0.0受影响。在分析还原WordPress的更新commit中，我们寻找到了这个漏洞的修复commit，并获得了受该漏洞影响的最新版本为WordPress[WordPress commit &lt;= 43bdb0e193955145a5ab1137890bb798bce5f0d2 （WordPress 5.1-alpha-44280）](https://github.com/WordPress/WordPress/commit/43bdb0e193955145a5ab1137890bb798bce5f0d2)

2、通过图片的裁剪功能，将裁剪后的图片写到任意目录下（目录穿越漏洞）

在WordPress的设定中，图片路径可能会收到某个插件的影响而不存在，如果目标图片不在想要的路径下时，WordPress就会把文件路径拼接为形似http://127.0.0.1/wp-content/uploads/2019/02/2.jpg 的url链接，然后从url访问下载原图

如果我们构造?或者#后面跟路径，就能造成获取图片位置和写入图片位置的不一致。。

这部分最大问题在于，前端的裁剪功能并不是存在漏洞的函数，我们只能通过手动构造这个裁剪请求来完成。

```
action=crop-image&amp;_ajax_nonce=8c2f0c9e6b&amp;id=74&amp;cropDetails[x1]=10&amp;cropDetails[y1]=10&amp;cropDetails[width]=10&amp;cropDetails[height]=10&amp;cropDetails[dst_width]=100&amp;cropDetails[dst_height]=100
```

ps: 当后端图片库为Imagick时，Imagick的Readimage函数不能读取远程http协议的图片，需要https.

3、通过Post Meta变量覆盖，设置_wp_page_template变量。

这部分在原文中一笔带过，也是整个分析复现过程中最大的问题，现在公开的所有所谓的WordPress RCE分析，都绕开了这部分。其中有两个最重要的点：
- 如何设置这个变量？
- 如何触发这个模板引用？
这个部分在下文中会详细解释。

4、如何让图片在被裁剪过之后，保留或者出现包含php敏感代码。

这部分就涉及到了后端图片库的问题，WordPress用到的后端图片处理库有两个，gd和imagick，其中默认优先使用imagick做处理。
- imagick 利用稍微比较简单，imagick不会处理图片中的exif部分。将敏感代码加入到exif部分就可以不会改动。
- gd gd的利用就比较麻烦了，gd不但会处理图片的exif部分，还会删除图片中出现的php代码。除非攻击者通过fuzz获得一张精心构造的图片，可以在被裁剪处理之后刚好出现需要的php代码（难度较高）。
最后通过链接上述4个流程，我们就可以完整的利用这个漏洞了，接下来我们详细分析一下。



## Post Meta变量覆盖

当你对你上传的图片，编辑修改其信息时，你将会触发action=edit_post

wp-admin/includes/post.php line 208

[![](https://p3.ssl.qhimg.com/t018700f26387b24db3.png)](https://p3.ssl.qhimg.com/t018700f26387b24db3.png)

post data来自于POST

如果是修复过的，在line 275行有修复patch

```
$translated = _wp_get_allowed_postdata( $post_data );
```

[https://github.com/WordPress/WordPress/commit/43bdb0e193955145a5ab1137890bb798bce5f0d2](https://github.com/WordPress/WordPress/commit/43bdb0e193955145a5ab1137890bb798bce5f0d2)

这个patch直接禁止了传入这个变量

```
function _wp_get_allowed_postdata( $post_data = null ) `{`
    if ( empty( $post_data ) ) `{`
       $post_data = $_POST;
    `}`
    // Pass through errors
    if ( is_wp_error( $post_data ) ) `{`
       return $post_data;
    `}`
    return array_diff_key( $post_data, array_flip( array( 'meta_input', 'file', 'guid' ) ) );
`}`
```

一路跟下去这个函数可以一直跟到wp-includes/post.php line 3770

[![](https://p5.ssl.qhimg.com/t018c2779d39ac1cf59.png)](https://p5.ssl.qhimg.com/t018c2779d39ac1cf59.png)

update_post_meta会把所有字段遍历更新

就会更新数据库中的相应字段

[![](https://p0.ssl.qhimg.com/t0137f81a2e89d18116.png)](https://p0.ssl.qhimg.com/t0137f81a2e89d18116.png)



## 配合变量覆盖来目录穿越写文件

根据原文的描述，我们首先需要找到相应的裁剪函数

/wp-admin/includes/image.php line 25

[![](https://p2.ssl.qhimg.com/t0118c0d53175092ee6.png)](https://p2.ssl.qhimg.com/t0118c0d53175092ee6.png)

这里传入的变量src就是从修改过的_wp_attached_file而来。

在代码中，我们可以很轻易的验证一个问题。在WordPress的设定中，图片路径可能会受到某个插件的影响而不存在，如果目标图片不在想要的路径下时，WordPress就会把文件路径拼接为形似http://127.0.0.1/wp-content/uploads/2019/02/2.jpg 的url链接，然后从url访问下载原图

这里的_load_image_to_edit_path就是用来完成这个操作的。

也正是因为这个原因，假设我们上传的图片名为2.jpg，则原本的_wp_attached_file为2019/02/2.jpg

然后我们通过Post Meta变量覆盖来修改_wp_attached_file为2019/02/1.jpg?/../../../evil.jpg

这里的原图片路径就会拼接为`{`wordpress_path`}`/wp-content/uploads/2019/02/1.jpg?/../../../evil.jpg，很显然这个文件并不存在，所以就会拼接链接为http://127.0.0.1/wp-content/uploads/2019/02/2.jpg?/../../../evil.jpg，后面的部分被当作GET请求，原图片就会成功的获取到。

紧接着进入save函数的新图片路径会拼接为`{`wordpress_path`}`/wp-content/uploads/2019/02/1.jpg?/../../../cropped-evil.jpg，我们就能成功写入新文件了。

后面的save函数会调用你当前图片库的裁剪功能，生成图片结果。（默认为imagick）

/wp-includes/class-wp-image-editor.php line 394

[![](https://p2.ssl.qhimg.com/t013fb83cdd86bafec0.png)](https://p2.ssl.qhimg.com/t013fb83cdd86bafec0.png)

但这里看上去没有任何限制，实际上不是的。在写入的目标目录下，存在一个假目录，为1.jpg?
- 而linux、mac支持这种假目录，可以使用?号
- 但windows在路径中不能有?号，所以这里改用了#号
&amp;meta_input[_wp_attached_file]=2019/02/2-1.jpg#/../../../evil.jpg

成功写入文件

cropped-evil.jpg



## 控制模板参数来导致任意文件包含

进度进展到这就有点儿陷入僵局，因为原文中关于这部分只用了一句话带过，在实际利用的过程中遇到了很多问题，甚至不同版本的WordPress会有不同的表现，其中诞生了多种利用方式，这里我主要讲1种稳定利用的方式。

### <a name="header-n100"></a>设置_wp_page_template

首先我们先正向分析，看看在什么情况下我们可以设置_wp_page_template

首先可以肯定的是，这个变量和_wp_attached_file一样都属于Post Meta的一部分，可以通过前面的操作来对这个变量赋值

[![](https://p4.ssl.qhimg.com/t01883561d14c45f041.png)](https://p4.ssl.qhimg.com/t01883561d14c45f041.png)

但实际测试过程中，我们发现，我们并不能在任何方式下修改并设置这个值。

/wp-includes/post.php line 3828

[![](https://p4.ssl.qhimg.com/t01eeab754047deff21.png)](https://p4.ssl.qhimg.com/t01eeab754047deff21.png)
- 如果你设置了这个值，但这个文件不存在，则会被定义为default。
- 如果该值被设置，则没办法通过这种方式修改。
所以这里我们可能需要新传一个媒体文件，然后通过变量覆盖来设置这个值。

### <a name="header-n113"></a>加载模板

当我们成功设置了该变量之后，我们发现，并不是所有的页面都会加载模板，我们重新回到代码中。

最终加载模板的地方在

wp-includes/template.php line 634

[![](https://p0.ssl.qhimg.com/t01193abcdbe21cd34e.png)](https://p0.ssl.qhimg.com/t01193abcdbe21cd34e.png)

只要是在$template_names中需要被加载的文件名，会在当前主题的目录下遍历加载。

回溯跟入

wp-includes/template.php line 23

[![](https://p3.ssl.qhimg.com/t014a9210463093bbda.png)](https://p3.ssl.qhimg.com/t014a9210463093bbda.png)

继续回溯我们就能发现一些端倪，当你访问页面的时候，页面会通过你访问的页面属性，调用不同的模板加载函数。

wp-includes/template-loader.php line 48

[![](https://p3.ssl.qhimg.com/t01c4fafb2fa9d22cab.png)](https://p3.ssl.qhimg.com/t01c4fafb2fa9d22cab.png)

在这么多的模板调用函数中只有两个函数get_page_template和get_single_template这两个在函数中调用了get_page_template_slug函数。

wp-includes/template.php line 486

[![](https://p2.ssl.qhimg.com/t017b35018bc195cb2d.png)](https://p2.ssl.qhimg.com/t017b35018bc195cb2d.png)

而get_page_template_slug函数从数据库中获取了_wp_page_template值

/wp-includes/post-template.php line 1755

[![](https://p0.ssl.qhimg.com/t01cc5237cbc2971eff.png)](https://p0.ssl.qhimg.com/t01cc5237cbc2971eff.png)

只要我们能让模板加载时进入get_page_template或get_single_template，我们的模板就可以成功被包含。

由于代码和前端的差异，我们也没有完全找到触发的条件是什么，这里选了一个最简单的，即上传一个txt文件在资源库，然后编辑信息并预览。

[![](https://p0.ssl.qhimg.com/t01dfa5e6dc0c4892ab.png)](https://p0.ssl.qhimg.com/t01dfa5e6dc0c4892ab.png)



## 生成图片马

这部分就涉及到了后端图片库的问题，WordPress用到的后端图片处理库有两个，gd和imagick，其中默认优先使用imagick做处理。
- imagick 利用稍微比较简单，imagick不会处理图片中的exif部分。将敏感代码加入到exif部分就可以不会改动。
- gd gd的利用就比较麻烦了，gd不但会处理图片的exif部分，还会删除图片中出现的php代码。除非攻击者通过fuzz获得一张精心构造的图片，可以在被裁剪处理之后刚好出现需要的php代码（难度较高）。
由于这不是漏洞最核心的部分，这里就不赘述了。



## 修复

1、由于该漏洞主要通过图片马来完成RCE，而后端图片库为gd时，gd会去除图片信息中exif部分，并去除敏感的php代码。但如果攻击者精心设计一张被裁剪后刚好生成含有敏感代码的图片时，就可以造成RCE漏洞。如果后端图片库为imagick时，则将敏感代码加入到图片信息的exif部分，就可以造成RCE漏洞。

官网上可供下载的所有release版本中都修复了这个漏洞，更新至最新版或者手动将当前版本覆盖安装即可。

2、通用防御方案 使用第三方防火墙进行防护如[创宇盾](https://www.yunaq.com/cyd)。

3、技术业务咨询 知道创宇技术业务咨询热线 : 400-060-9587(政府，国有企业)、028-68360638(互联网企业)



## 总结

整个RCE的利用链由4部分组成，深入WordPress的底层Core逻辑，原本来说这4个部分无论哪个都很难造成什么危害，但却巧妙地连接在一起，并且整个部分意外的都是默认配置，大大增加了影响面。在安全程度极高的WordPress中能完成这种的攻击利用链相当难得，从任何角度都是一个非常nice的漏洞:&gt;

最后再次感谢我的小伙伴们以及整个过程中给我提供了很大帮助的朋友们:&gt;

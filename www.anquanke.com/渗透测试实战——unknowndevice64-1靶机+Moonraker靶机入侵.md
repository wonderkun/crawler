> 原文链接: https://www.anquanke.com//post/id/173159 


# 渗透测试实战——unknowndevice64-1靶机+Moonraker靶机入侵


                                阅读量   
                                **275346**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">7</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t014ad2d04cd7a02d5e.jpg)](https://p3.ssl.qhimg.com/t014ad2d04cd7a02d5e.jpg)



## 前言

哈喽大家好，爱写靶机实战的文章的我，又又来啦，最近靶机更新的有点多，小弟没日没夜的搞，库存有点多，所以本文还是一样，写2个靶机的实战入侵pwn。



## 靶机下载/安装

unknowndevice64：[https://pan.baidu.com/s/1QUJp1Cxuf1bTxQd4ZdTzCA](https://pan.baidu.com/s/1QUJp1Cxuf1bTxQd4ZdTzCA)

Moonraker：[https://pan.baidu.com/s/1pczDMorsDAdn7JibGZuELA](https://pan.baidu.com/s/1pczDMorsDAdn7JibGZuELA)

[![](https://p2.ssl.qhimg.com/t018dd7e93a5538a046.png)](https://p2.ssl.qhimg.com/t018dd7e93a5538a046.png)



## 实战

### <a class="reference-link" name="unknowndevice64%E9%9D%B6%E6%9C%BA"></a>unknowndevice64靶机

该靶机被定义为中级，但是是吗？我们来看看….

靶机IP：172.16.24.72

老规矩nmap神器开路：

[![](https://p4.ssl.qhimg.com/t016c9b56136255920c.png)](https://p4.ssl.qhimg.com/t016c9b56136255920c.png)

可以看到只开放2个端口，我们还是先查看http服务的31337端口

访问如图：

[![](https://p2.ssl.qhimg.com/t0164d02452316de589.png)](https://p2.ssl.qhimg.com/t0164d02452316de589.png)

界面做的挺酷的，不用怀疑习惯性 查看源代码，如图：

[![](https://p0.ssl.qhimg.com/t01a446eb28c82dffcd.png)](https://p0.ssl.qhimg.com/t01a446eb28c82dffcd.png)

发现 key_is_h1dd3n.jpg 图片，如图：

[![](https://p0.ssl.qhimg.com/t0155e7661a13b3c062.png)](https://p0.ssl.qhimg.com/t0155e7661a13b3c062.png)

老套路了，CTF的隐写技术，小弟上篇文章刚刚写过，那么我们来分离看看吧

[![](https://p4.ssl.qhimg.com/t014b34f182561191d2.png)](https://p4.ssl.qhimg.com/t014b34f182561191d2.png)

可以看到，需要输入密码，那么密码是什么呢？其实。。。 密码就写在文件名上啊 “h1dd3n”

下面我们加密码，试一下吧

[![](https://p0.ssl.qhimg.com/t018782f5b180608cf1.png)](https://p0.ssl.qhimg.com/t018782f5b180608cf1.png)

拿到一个 “h1dd3n.txt”文件，我们查看一下看看

[![](https://p0.ssl.qhimg.com/t011e38a850a4ca2afe.png)](https://p0.ssl.qhimg.com/t011e38a850a4ca2afe.png)

看到这个密文，经常玩ctf的小伙伴就知道了，但是肯定也有小伙伴以为是摩斯电码，其实它是brainfuck编码，我们使用在线解密工具，试一下吧

[![](https://p2.ssl.qhimg.com/t01bfbdf879199eb01e.png)](https://p2.ssl.qhimg.com/t01bfbdf879199eb01e.png)

成功解密，得到密码为：

ud64 – 1M!#64[@ud](https://github.com/ud)

这个时候大家肯定兴致勃勃的拿去ssh登陆。。。

没错，我也是这样。心里还在念叨，就他喵的这样还能定为中级？

然后一登陆就闷逼了。。。如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fd0b38d262e029ec.png)

好吧。。。 碰到了 rbash ，然后小弟就一顿谷歌，找到了一篇比较全面的绕过方法，参考地址：[https://fireshellsecurity.team/restricted-linux-shell-escaping-techniques/](https://fireshellsecurity.team/restricted-linux-shell-escaping-techniques/)

放出来希望大家用得到。。。常见的几种小弟也都试了，如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01069c88aa24068fe5.png)

[![](https://p3.ssl.qhimg.com/t01e00a1c02bd16803f.png)](https://p3.ssl.qhimg.com/t01e00a1c02bd16803f.png)

[![](https://p2.ssl.qhimg.com/t0199af5a0f3cc9bdf6.png)](https://p2.ssl.qhimg.com/t0199af5a0f3cc9bdf6.png)

这些记录是小弟后面找的记录，比较懒就不重置靶机了。。。

（注：上图中的 `echo /*` 命令有些CTF题中会出现可以解题，小伙伴们以后可以试试！）

最后小弟根据刚刚文章的内容，进行了尝试 使用 export 命令，该命令是默认rbash下可以使用的，小伙伴们可以在shell下 按键盘的tab 能弹出能执行的命令，如图：

[![](https://p1.ssl.qhimg.com/t01cb047c9267c0e653.png)](https://p1.ssl.qhimg.com/t01cb047c9267c0e653.png)

通过上图可以看到该靶机运行使用vi编辑器，

那么最后的绕过步骤为：
1. vi aaa.txt
1. 输入 `:!/bin/bash` 得到shell<br>[![](https://p2.ssl.qhimg.com/t01c52c757db55a3e7e.png)](https://p2.ssl.qhimg.com/t01c52c757db55a3e7e.png) 当然这个shell也不是我们平时的shell，如图：<br>[![](https://p0.ssl.qhimg.com/t01072936598c2651c3.png)](https://p0.ssl.qhimg.com/t01072936598c2651c3.png) 我们还需要再进行下一步绕过。。。
<li>使用命令<br>[![](https://p0.ssl.qhimg.com/t01bf5a6bd0b98efbc4.png)](https://p0.ssl.qhimg.com/t01bf5a6bd0b98efbc4.png)
</li>
下面我们就可以输入 sudo -l 了

[![](https://p5.ssl.qhimg.com/t0123dc174d69c04794.png)](https://p5.ssl.qhimg.com/t0123dc174d69c04794.png)

发现了一个突破口，sysud64 不需要密码，我们执行 help看看

[![](https://p3.ssl.qhimg.com/t0163cb2cd1b4a349ba.png)](https://p3.ssl.qhimg.com/t0163cb2cd1b4a349ba.png)

可以使用-o 参数

下面的exp就是： sudo sysud64 -o /dev/null /bin/bash

如图：

[![](https://p0.ssl.qhimg.com/t01101a44c3cb6b9f39.png)](https://p0.ssl.qhimg.com/t01101a44c3cb6b9f39.png)

成功拿到root-shell，下面就是拿flag了

[![](https://p3.ssl.qhimg.com/t01ba3a9c1cb368aeb9.png)](https://p3.ssl.qhimg.com/t01ba3a9c1cb368aeb9.png)

本靶机完！！！

### <a class="reference-link" name="Moonraker%E9%9D%B6%E6%9C%BA"></a>Moonraker靶机

靶机IP：172.16.24.44

老规矩nmap神器开路：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01756054ffd9cc1424.png)

我们还是先查看80端口，用目录猜解工具跑一下看看，

[![](https://p3.ssl.qhimg.com/t013a955803d7c7bd42.png)](https://p3.ssl.qhimg.com/t013a955803d7c7bd42.png)

在首页上经过一段动画后，我们到了

[http://172.16.24.44/moonraker.html](http://172.16.24.44/moonraker.html)

[![](https://p5.ssl.qhimg.com/t01779abb56cc547cb2.png)](https://p5.ssl.qhimg.com/t01779abb56cc547cb2.png)

我们逐个点进去看一下，在[http://172.16.24.44/services/](http://172.16.24.44/services/) 下发现一个比较有意思的东西 [http://172.16.24.44/svc-inq/sales.html](http://172.16.24.44/svc-inq/sales.html)

[![](https://p5.ssl.qhimg.com/t01a412b9a409ab8b85.png)](https://p5.ssl.qhimg.com/t01a412b9a409ab8b85.png)

[![](https://p0.ssl.qhimg.com/t0198c66d7fef828b46.png)](https://p0.ssl.qhimg.com/t0198c66d7fef828b46.png)

看到对话框是不是小伙伴们要跑一波注入？我也一样。。。 但是看内容说是让我们提交咨询留言会有销售帮忙查看，这不就是正常的xss套路吗？那么我们就在本地开启http的服务来构造语句看看能不能成功，如图：
<li>先开启http服务，本次使用 nginx<br>[![](https://p3.ssl.qhimg.com/t0142fe782215943dda.png)](https://p3.ssl.qhimg.com/t0142fe782215943dda.png) 2.确认开启后，我们就在网站上写入语句了，提交<br>[![](https://p5.ssl.qhimg.com/t017e236a7c1d2daab9.png)](https://p5.ssl.qhimg.com/t017e236a7c1d2daab9.png)
</li>
下面我们只需要打开本机的nginx日志静静等待就行。。。。

泡个茶的功夫，就已经有销售经理点击查看了，（销售经理say：又他喵是我背锅。。。。）如图：

[![](https://p3.ssl.qhimg.com/t0149abc3077c3fecf4.png)](https://p3.ssl.qhimg.com/t0149abc3077c3fecf4.png)

得到新目录 “svc-inq/salesmoon-gui.php”

[![](https://p2.ssl.qhimg.com/t01787c7c5537030f28.png)](https://p2.ssl.qhimg.com/t01787c7c5537030f28.png)

继续点击进入

[![](https://p1.ssl.qhimg.com/t0166fc53f19e441ed1.png)](https://p1.ssl.qhimg.com/t0166fc53f19e441ed1.png)

可以看到其使用的是 “couchDB”, 下面我们继续一个个查看，在couchDB notes 找到了密码

[![](https://p5.ssl.qhimg.com/t0145a0bb8c1b56300e.png)](https://p5.ssl.qhimg.com/t0145a0bb8c1b56300e.png)

通过谷歌得到密码为 ：Jaws – dollyx99

下一步我们去 启用了couchdb 服务的 5984 端口登陆。。

如图：

[![](https://p5.ssl.qhimg.com/t01b193ee70465f6816.png)](https://p5.ssl.qhimg.com/t01b193ee70465f6816.png)

小伙伴要问了，你这个登陆路径哪里来的呢？为什么我的没有。。。 好吧 其实是谷歌的。。。。

登陆后

[![](https://p3.ssl.qhimg.com/t01f1064ca3359cb97f.png)](https://p3.ssl.qhimg.com/t01f1064ca3359cb97f.png)

往下走

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0165cbed0aef37e825.png)

发现新突破口，我们去访问看看

[![](https://p3.ssl.qhimg.com/t01bd09cbee51e87b16.png)](https://p3.ssl.qhimg.com/t01bd09cbee51e87b16.png)

我们逐一查看，发现Hugo 用户是我们下一步的突破口

[![](https://p2.ssl.qhimg.com/t01388acf0e59bbd9f0.png)](https://p2.ssl.qhimg.com/t01388acf0e59bbd9f0.png)

可以看到其是CEO，出现3000端口。。。 那么我们继续去3000端口登陆吧

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ec54ff5595ad0e34.png)

登陆成功后，出现这个，如图：

[![](https://p5.ssl.qhimg.com/t01d09c4e8827f5084c.png)](https://p5.ssl.qhimg.com/t01d09c4e8827f5084c.png)

这他喵的是什么鬼。。。 小弟在这里被卡了一会儿。。 最后隔天出现探测ip的时候，发现其端口是nodejs 架构啊，不是记得有个RCE吗？来谷歌一波

找到了这个

[https://opsecx.com/index.php/2017/02/08/exploiting-node-js-deserialization-bug-](https://opsecx.com/index.php/2017/02/08/exploiting-node-js-deserialization-bug-%20for-remote-code-execution/) for-remote-code-execution/

然后小弟就跟着尝试了，我们使用脚本先生成一个反弹shell编码，最后exp为 如图：

[![](https://p5.ssl.qhimg.com/t01316364801f0ca470.png)](https://p5.ssl.qhimg.com/t01316364801f0ca470.png)

下一步我们吧这个构造号的exp 继续base64的编码

[![](https://p2.ssl.qhimg.com/t01329b9cdb59db8b7c.png)](https://p2.ssl.qhimg.com/t01329b9cdb59db8b7c.png)

（下载地址：[https://pan.baidu.com/s/1CiRZjazWX52g_4raw9xHew）](https://pan.baidu.com/s/1CiRZjazWX52g_4raw9xHew%EF%BC%89)

最后我们把这个编码后的exp复制出来，重新登陆3000端口，抓包，然后把exp复制在 profile= 后面，如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01970bb996f5904ce1.png)

我们成功拿到shell

[![](https://p4.ssl.qhimg.com/t01581e70f475778780.png)](https://p4.ssl.qhimg.com/t01581e70f475778780.png)

下面我们在里面翻翻看，有没有什么突破口，然后发现了这个

[![](https://p5.ssl.qhimg.com/t012bf0a481f486ece4.png)](https://p5.ssl.qhimg.com/t012bf0a481f486ece4.png)

这个在上一篇文章中小弟已经说过了，我们看看有没有什么突破口，如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0193fa2c9f646d9032.png)

哈哈哈，我们跟过去查看一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0162e969415fbd56c0.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018caef89b31f98947.png)

没有让我们失望，我们找到了 CEO的密码 ： hugo – 321Blast0ff!!

下面我们使用ssh登陆一下提权吧。。。。。

[![](https://p1.ssl.qhimg.com/t0147dc3bcdee97aa99.png)](https://p1.ssl.qhimg.com/t0147dc3bcdee97aa99.png)

我们继续翻翻看

刚刚在‘jaws’用户时我们看到了有个邮件服务，我们到系统默认的 /var/mail下看看

[![](https://p5.ssl.qhimg.com/t017635dc413165b27d.png)](https://p5.ssl.qhimg.com/t017635dc413165b27d.png)

hugo目录本权限可读，我们查看一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ae59faadfeba8181.png)

可以看到不少邮件往来，在下来没几封，直接发现了这个。。。

[![](https://p0.ssl.qhimg.com/t0143cc634f72b44f62.png)](https://p0.ssl.qhimg.com/t0143cc634f72b44f62.png)

这个时候还犹豫什么，直接爆破走起，如图：

[![](https://p4.ssl.qhimg.com/t01f9bad741449cb3ff.png)](https://p4.ssl.qhimg.com/t01f9bad741449cb3ff.png)

[![](https://p4.ssl.qhimg.com/t01ac67b20a334df875.png)](https://p4.ssl.qhimg.com/t01ac67b20a334df875.png)

泡个养生茶的功夫，密码已经出来了，然后小弟就急匆匆的去登陆。。。

如图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0113d7b4e47e1a3203.png)

可是一直提示密码不对，我当时真的都快怀疑人生了。。。。 然后喝了2杯养生茶，重新看了一下那个邮件，发现让其在密码后面加上 VR00M

最后的密码为： cyberVR00M

然后就成功了。。。。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01de13fed85523fed8.png)

成功拿到root-shell和flag

本靶机完！！！

感谢观看！！

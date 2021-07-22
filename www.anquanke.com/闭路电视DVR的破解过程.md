> 原文链接: https://www.anquanke.com//post/id/83493 


# 闭路电视DVR的破解过程


                                阅读量   
                                **227216**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.pentestpartners.com/blog/pwning-cctv-cameras/](https://www.pentestpartners.com/blog/pwning-cctv-cameras/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01e07ae689e767322a.png)](https://p0.ssl.qhimg.com/t01e07ae689e767322a.png)

闭路电视监控系统(CCTV)在英国可以算得上是随处可见了。一项最新的统计结果显示,在英国本土总共有大约185万个摄像头,其中大多数摄像头都安装于私<br>
人住宅内。这些摄像头大多数都会连接到某种记录设备,而这类记录设备一般就是数字视频录像机。相对于传统的模拟视频录像机,数字视频录像机采用硬盘录像,<br>
故常常被称为硬盘录像机,也被称为DVR。它是一套进行图像存储处理的计算机系统,具有对图像/语音进行长时间录像、录音、远程监视和控制的功能,DVR<br>
集合了录像机、画面分割器、云台镜头控制、报警控制、网络传输等五种功能于一身,用一台设备就能取代模拟监控系统一大堆设备的功能,而且在价格上也逐渐占有优势。

DVR可以从多个摄像头中获取视频信息,并将这些数据存储在其设备硬盘之中。它不仅可以将图像信息显示在屏幕上,而且用户还可以通过web浏览器或者客户端联网访问DVR设备。

当然了,企业和家庭户主肯定希望通过远程访问他们的DVR设备来时刻关注他们财产的一举一动。由于DVR设备通过端口转发来传递网络数据,这也使得我们能够在Shodan搜索引擎中轻而易举地找到这些设备。

所以,我们打算去[淘一个便宜的DVR](http://www.amazon.co.uk/Security-Real-time-Recorder-Detection-Surveillance/dp/B0162AQCO4/ref=sr_1_2?s=diy&amp;ie=UTF8&amp;qid=1455638899&amp;sr=1-2&amp;keywords=MVpower+8+channel),并对其进行研究和分析,看看其安全性到底如何。反正现在的情况已经很糟糕了。

在经过了几个小时的研究和分析之后,我们发现了下列问题:

**在Shodan上的一些琐碎发现**

在那些运行了客户web服务器的DVR设备中,其HTTP服务器的header非常有特色-“JAWS/1.0”。在Shodan上搜索这个header之后([https://www.shodan.io/search?query=JAWS%2F1.0](https://www.shodan.io/search?query=JAWS%2F1.0)),我们可以发现,当前有超过44000个此类设备已经接入了互联网。虽然并不是每款设备都一样,但看起来它们也没什么太大的区别。



[![](https://p2.ssl.qhimg.com/t017e5ac3dfd51a3512.png)](https://p2.ssl.qhimg.com/t017e5ac3dfd51a3512.png)



**默认凭证安全性较弱**

在默认情况下,设备的用户名为admin,密码为空。



[![](https://p0.ssl.qhimg.com/t0107caab2e06c7daf6.png)](https://p0.ssl.qhimg.com/t0107caab2e06c7daf6.png)



目前,我们只能使用DVR设备的本地接口来修改这个密码。由于DVR设备并没有配置键盘,所以我敢打赌,大多数的DVR设备仍然使用的是默认密码。

这个问题已经存在已久了,我们现在再去讨论它也没有任何的意义。默认密码在物联网设备领域中简直就是个挥之不散的阴影。

**Web认证绕过**

当你首次访问DVR时,系统会给你显示index.html页面,你需要在这个页面输入你的用户名和密码。如果你所输入的数据正确,页面将会跳转至view2.html。

奇怪的是,如果我们清空我们的cookies,然后访问view2.html,系统会在将用户重定向至index.html并输入用户名和密码之前,显示该页面的局部信息。

一般来说,这应该是JavaScript客户端认证所要进行的检测工作。当然了,我们在对view2.js进行了分析之后,得到了下列发现:

```
$(document).ready(function()`{`
    dvr_camcnt = Cookies.get(“dvr_camcnt");
    dvr_usr = Cookies.get("dvr_usr");
    dvr_pwd = Cookies.get("dvr_pwd");
    if(dvr_camcnt == null || dvr_usr == null || dvr_pwd == null)
    `{`
        location.href = "/index.html";
`}`
```



在得到了这些信息之后,你将会发现,只要这三个cookie的值为空,你就可以对设备进行访问(dvr_comcnt的值必须为2,4,8或者24)。



[![](https://p3.ssl.qhimg.com/t0116fff34d5eda7042.png)](https://p3.ssl.qhimg.com/t0116fff34d5eda7042.png)



当然了,我们也可以手动设置这些cookie来获取设备的访问权限。现在,我们在不知道用户名和密码的情况下,获取到了DVR设备的完整控制权限。

**开启设备的控制台**

有时,能够完全控制DVR设备的web接口的确很有趣,但我们往往想要的更多,例如root shell。

打开DVR盒子的上盖,我们发现了J18,这是一个115200串口。尽管我可以看到其输出数据,但是在没有shell的情况下我是无法向设备输入数据的。

重启设备之后,我们可以看到设备主板使用的是uboot(一款及其常见的开源引导程序)。我们只需按下任意按键,就可以中断uboot的启动引导。但是你只有一秒钟的时间,所以你可能需要多试几次才能成功。

现在,我们进入了uboot的控制台。在修改了引导参数之后,我们将设备改成了单用户模式,这样一来,我们在登录时就不需要输入密码了:

```
setenv bootargs $`{`bootargs`}` single
boot
```



在调整了设置之后,DVR将会以单用户模式启动,这样我们就得到了root shell。这也就意味着,从现在开始,我们将无所不能!

**内置的web shell**

本地的root shell固然很棒,但有时我还需要远程访问shell。

在对设备固件进行了分析之后,我发现大多数的功能都集中在dvr_app之中(包括web服务器在内)。尽管web接口使用了cgi-bin目录,但我仍然无法在设备的文件系统中找到这个目录,很可能是因为dvr_app对其进行过内部处理,这种现象在嵌入式设备中非常的常见。

除了一些显而易见的数据之外,还有一些其他的信息值得我们注意-例如moo和shell。具体信息如下图所示:



[![](https://p4.ssl.qhimg.com/t01f144dcd2693b4d70.png)](https://p4.ssl.qhimg.com/t01f144dcd2693b4d70.png)



访问moo目录之后,我们发现了一个“牛”的图形。当你在Debian系统中运行apt-get moo时,你就能够看到这个图形。但为什么它会出现在这里呢?我们也不清楚。



[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b37947f965c00a63.png)



在访问了shell目录之后,你将会看到列表所示的下列进程:



[![](https://p1.ssl.qhimg.com/t01871210d30eda75d5.png)](https://p1.ssl.qhimg.com/t01871210d30eda75d5.png)



我们发现,设备内置了一个远程root shell功能,使得我们能够在未经身份验证的情况下对其进行访问。这简直是太糟糕了!

**未经身份验证的Telnet**

设备已经在端口23运行了telnet,但是它还需要root密码。即使我们能够查看/etc/passwd并且得到解码后的密码哈希值,我们也仍然无法恢复出明文密码。



[![](https://p1.ssl.qhimg.com/t0139660cb516959091.png)](https://p1.ssl.qhimg.com/t0139660cb516959091.png)



在得到了上图所示信息之后,我们便尝试使用密码破解器来尝试破解这个密码,这一操作可能需要一些时间。

```
为了解决这一问题,我们使用了远程web shell来开启设备的telnet daemon:
http://192.168.3.101/shell?/usr/sbin/telnetd -l/bin/sh -p 25
```



现在,我们就可以远程登录并正常使用设备了。



[![](https://p0.ssl.qhimg.com/t01d813a9bc7c3388e0.png)](https://p0.ssl.qhimg.com/t01d813a9bc7c3388e0.png)



这很有趣,但是大多数的用户并不会通过端口80来转发网络数据。攻击者可以通过端口25来开启远程登录,但这样是无法访问目标设备的。

**向陌生的硬编码邮件地址发送图片**

在对dvr_app的二进制代码进行深入分析之后,我们发现了一些非常奇怪的功能。

无论是什么原因,设备会将第一个摄像头的快照发送至lawishere@yeah.net。



[![](https://p1.ssl.qhimg.com/t011c1b7eb032ebe825.png)](https://p1.ssl.qhimg.com/t011c1b7eb032ebe825.png)



这是为什么呢?我们目前还不清楚。但这样的行为绝对会引起非常严重的隐私泄漏。而且,目前已经有用户在GitHub上报告过这一问题了。

**其他的一些问题**

DVR设备存在的问题远不仅于此,这种设备所存在的问题简直是数不胜数:

l   如果你能通过web服务器来注入shell命令,那么你就已经实现root了。根本无需再进行提权。

l   没有提供CSRF保护。你可以诱骗用户点击某一链接,并进行恶意操作。

l   没有提供账户锁定功能,而且也没有提供防暴力破解机制。你可以不断尝试输入密码,直到你猜中为止。而唯一能够拖慢攻击者脚步的就是这类设备的访问速度较慢。

l   设备不支持HTTPS。所有的通讯信息将以明文形式发送,攻击者可以拦截和篡改设备所发送的网络信息。

l   没有提供固件更新功能。

我们希望相关的研发人员能够重视这些问题,并一一解决设备中的这些设计缺陷。

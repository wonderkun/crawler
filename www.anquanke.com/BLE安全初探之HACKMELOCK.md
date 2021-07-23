> 原文链接: https://www.anquanke.com//post/id/166746 


# BLE安全初探之HACKMELOCK


                                阅读量   
                                **212019**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01f15935ae351e07e4.png)](https://p3.ssl.qhimg.com/t01f15935ae351e07e4.png)

Author: Larryxi@360GearTeam

## 0x00 环境搭建

低功耗蓝牙技术（Bluetooth Low Energy）作为一种无线通信技术，其设计目标和实现与经典蓝牙技术有很大的不同，关于其的概述和技术细节可以参考文末的链接和著作。本文会结合书本知识对其中的协议数据包进行备注，以加深对主从设备交互流程的理解，进一步探索针对某BLE应用的攻击方式。

环境主从设备的选取是参考[BLUETOOTH SMART HACKMELOCK](https://smartlockpicking.com/hackmelock/)提供的仿真环境，其在树莓派中用nodejs搭建了一个虚拟的BLE门锁，专门写了一个Android app来对这个门锁进行操作，两端都遗留了一些安全问题供我们后续探索学习。

[UnicornTeam](https://weibo.com/unicornteam)曾经讲过无线通信的攻击手段可以分为监听、重放、欺骗和劫持攻击。个人感觉先要嗅探相关流量进行理解分析才能知己知彼有所突破，厚着脸皮向大佬团队借了一个[nRF51422](https://www.nordicsemi.com/eng/Products/ANT/nRF51422)来对BLE进行嗅探，其文档[nRF-Sniffer-UG-v2](https://www.nordicsemi.com/eng/nordic/download_resource/65244/3/23454585/136165)也写得很清楚，所以最终构建的环境如图所示（同时也感谢[Tesi1a](https://weibo.com/u/5306621349)同学友情赞助的树莓派）：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01697548c6fe46aa3e.png)



## 0x01 流程探索

上文搭建的虚拟环境中APP点击相关功能，服务端响应后在控制台也可以看到一定的log输出，方便我们理解协议的交互，接下来我会配合捕获的流量进行解释，数据包流量也已备份至[Github](https://github.com/Larryxi/My_tools/tree/master/ble_hackmelock)。低功耗蓝牙的体系结构如下：

[![](https://p0.ssl.qhimg.com/t01ac0b2eb86c1ef3d5.jpg)](https://p0.ssl.qhimg.com/t01ac0b2eb86c1ef3d5.jpg)

### <a name="header-n19"></a>广播建立连接和发现服务特性

建立起虚拟门锁从设备后，其就在不停地广播。广播报文的类型有7种，用途比较广泛的类型是ADV_IND通用广播指示，广播报文的大致结构如下：

[![](https://p2.ssl.qhimg.com/t011fc4950e6d11b679.jpg)](https://p2.ssl.qhimg.com/t011fc4950e6d11b679.jpg)

在数据包中也可以看到很多树莓派的广播报文：

[![](https://p1.ssl.qhimg.com/t01492ad845f41604da.jpg)](https://p1.ssl.qhimg.com/t01492ad845f41604da.jpg)

打开手机App在被动扫描接收到所需的广播报文后，便会发起连接请求：

[![](https://p2.ssl.qhimg.com/t0144f5e6fcc3d4e59b.jpg)](https://p2.ssl.qhimg.com/t0144f5e6fcc3d4e59b.jpg)

主从设备在进入连接态后就会发送数据报文进行通信，数据报文格式和广播报文格式略有不同：

[![](https://p5.ssl.qhimg.com/t0189541d13696085d5.jpg)](https://p5.ssl.qhimg.com/t0189541d13696085d5.jpg)

数据报文中的逻辑链路标识符LLID把数据报文分成三种类型，其中链路层控制报文（11）用于管理连接，如下的数据包便是在管理连接中的版本交换：

[![](https://p2.ssl.qhimg.com/t010b694963109bed4e.jpg)](https://p2.ssl.qhimg.com/t010b694963109bed4e.jpg)

不仅是只有链路层的数据包，两个设备的上层服务还是会通过L2CAP信道（数据包序列），其结构如下：

[![](https://p5.ssl.qhimg.com/t01d6ef696ccbe20a06.jpg)](https://p5.ssl.qhimg.com/t01d6ef696ccbe20a06.jpg)

低功耗蓝牙一共使用3条信道，如下的L2CAP数据包则是低功耗信令信道的数据包，用于主机层的信令：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b2f65b9f7c95f7c0.jpg)

属性层和通用属性规范层作为BLE的核心概念，一个是抽象协议一个是通用配置文件。属性通俗地来讲就是一条有标签的、可以被寻址的数据，其结构如下：

[![](https://p4.ssl.qhimg.com/t01d6ef696ccbe20a06.jpg)](https://p4.ssl.qhimg.com/t01d6ef696ccbe20a06.jpg)

在低功耗蓝牙中特性是由一种或多种属性组成，服务是由一种或多种特性组成，并且是由服务声明来对服务进行分组，用特性声明来对特性进行分组。服务和特性的发现由通用属性规范规定，具体则表现为不同类型的属性协议，如下的数据包便是按组类型读取请求来读取首要服务声明：

[![](https://p3.ssl.qhimg.com/t01cff1698065b4ccb0.jpg)](https://p3.ssl.qhimg.com/t01cff1698065b4ccb0.jpg)

响应则是所有首要服务声明的属性句柄、该首要服务中最后一个属性以及首要服务声明的数值：

[![](https://p5.ssl.qhimg.com/t01e198afb00cdab90c.jpg)](https://p5.ssl.qhimg.com/t01e198afb00cdab90c.jpg)

类似的，对于每一个服务也会有发现特性的请求和响应：

[![](https://p1.ssl.qhimg.com/t01e957756cda87b4e4.jpg)](https://p1.ssl.qhimg.com/t01e957756cda87b4e4.jpg)

[![](https://p4.ssl.qhimg.com/t013dfd748665e1df4b.jpg)](https://p4.ssl.qhimg.com/t013dfd748665e1df4b.jpg)

在数据包中分开看请求的服务和特性可能不是太方便，可以借助[bleah](https://github.com/evilsocket/bleah)直接枚举设备上的所以属性：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c690c898d9194b85.jpg)

### <a name="header-n70"></a>门锁初始化配置

门锁的初始化配置在服务端控制台的输出如下：

[![](https://p2.ssl.qhimg.com/t018206cd486720f084.jpg)](https://p2.ssl.qhimg.com/t018206cd486720f084.jpg)

在数据包上的表现就是先对从设备的0x0013 handler进行读取请求，得到响应值后开始对0x000c handler进行一系列的写入请求，一共写入了24个序列完成初始化阶段：

[![](https://p1.ssl.qhimg.com/t01970c6568371c4abd.jpg)](https://p1.ssl.qhimg.com/t01970c6568371c4abd.jpg)

### <a name="header-n79"></a>开关锁操作

开关锁的操作在服务端控制台的输出上看，貌似是有一个内部的认证过程：

[![](https://p4.ssl.qhimg.com/t019778973556194d43.jpg)](https://p4.ssl.qhimg.com/t019778973556194d43.jpg)

首先读取0x0013 handler读取一个random challenge，将响应写入0x000c handler，如果通过了认证则可以进行开关锁的操作，并且开关锁向handler中写入的值也是固定的：

[![](https://p0.ssl.qhimg.com/t01341c65f6dff86e8b.jpg)](https://p0.ssl.qhimg.com/t01341c65f6dff86e8b.jpg)

### <a name="header-n89"></a>认证凭据重置

这个功能在服务端上被称为Data transfer，通过接收一条命令触发，并重新生成了24个序列通知客户端：

[![](https://p1.ssl.qhimg.com/t01d050216d30fde7a3.jpg)](https://p1.ssl.qhimg.com/t01d050216d30fde7a3.jpg)

在数据包上可以看到还有对0x0010 handler的写入请求，向0x000c写入的则是数据重传命令：

[![](https://p3.ssl.qhimg.com/t01d291aa2781016f7c.jpg)](https://p3.ssl.qhimg.com/t01d291aa2781016f7c.jpg)



## 0x02 攻击方式

### <a name="header-n99"></a>流程探索

流程中比较感兴趣的就是内部实现的认证和数据重传部分，首先猜测不经过认证直接写入数据重传指令是否可以重置门锁，这里借助gatttool进行BLE的连接和请求：

[![](https://p2.ssl.qhimg.com/t013b13a1e264a4beca.jpg)](https://p2.ssl.qhimg.com/t013b13a1e264a4beca.jpg)

很遗憾是需要认证的，那我们就需要分析服务端或者客户端的程序，逆向出认证的具体流程。上jeb反编译apk，根据auth字符串定位至认证相关逻辑。可知在接收Challenge后，和v7一起传入hackmelockDevice.calculateResponse方法，正常的开锁流程会使v7为1，通过二维码分享的开锁流程会使v7为2：

[![](https://p5.ssl.qhimg.com/t016b6f4a0613b960d2.jpg)](https://p5.ssl.qhimg.com/t016b6f4a0613b960d2.jpg)

跟进去可知，根据不同的keyID对Challenge进行两次AES加密计算出响应：

[![](https://p4.ssl.qhimg.com/t01144f222ea8075fe9.jpg)](https://p4.ssl.qhimg.com/t01144f222ea8075fe9.jpg)

而其中的keys数组则是在最开始初始化门锁中传递的23个序列：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011bd7818a240190ce.jpg)

对于keyID为0的序列tohex为12个字节，后面用空字符补齐16字节，进行两次AES加密用python代码还是很简单就实现了：

```
import sys
from Crypto.Cipher import AES
from binascii import a2b_hex, b2a_hex

def calc(key, challenge):
    plaint_1 = a2b_hex(challenge)
    key_1 = a2b_hex(key)
    aes_1 = AES.new(key_1, AES.MODE_ECB)
    cipher_1 = aes_1.encrypt(plaint_1)
    print b2a_hex(cipher_1)

    plaint_2 = a2b_hex("DDAAFF03040506070809101112131415")
    key_2 = cipher_1
    aes_2 = AES.new(key_2, AES.MODE_ECB)
    cipher_2 = aes_2.encrypt(plaint_2)
    print b2a_hex(cipher_2)


if __name__ == '__main__':
    if len(sys.argv) &gt; 2:
        calc(sys.argv[1], sys.argv[2])
```

[![](https://p5.ssl.qhimg.com/t0172108c5d2bfb9cc1.jpg)](https://p5.ssl.qhimg.com/t0172108c5d2bfb9cc1.jpg)

### <a name="header-n122"></a>服务端后门

[服务端代码](https://github.com/smartlockpicking/hackmelock-device)是用nodejs写的，看起来比安卓逆向轻松多了，在服务端留下了一个后门可以使用特定密码直接通过认证：

```
if ( (authResponse === fin_16.toString('hex')) || (authResponse === '4861636b6d654c6f636b4d6173746572')) `{`
    console.log('AUTHENTICATION OK!'.green);
    this.authenticated = true;
    this.status = statusAuthenticated;
  `}`
```

[![](https://p0.ssl.qhimg.com/t01a716a2bcc7b5e44a.jpg)](https://p0.ssl.qhimg.com/t01a716a2bcc7b5e44a.jpg)

### <a name="header-n129"></a>认证代码缺陷

最开始按照正常的加密逻辑，向0x000c handler写入response总是认证不通过，对比在app上操作的控制台输出，发现其在计算出的response后多加了一个00，幡然醒悟最后一个写入的字符就是用来指示keyID的。而在服务端代码中，其不仅加载了初始化时传递的23个key，还以00扩展至128个：

```
Hackmelock.prototype.loadConfig = function(configFile) `{`
  this.config = fs.readFileSync(configFile).toString().split("\n");
  //pop last empty line
  this.config.pop();

  for (i=this.config.length; i&lt;128; i++) `{`
    this.config.push('000000000000000000000000')
  `}`
```

如果我们将keyID指示得过大，那么第一轮AES加密的key就已经确定了，相应的认证措施也就失效了：

[![](https://p5.ssl.qhimg.com/t01c1849e313e3812fe.jpg)](https://p5.ssl.qhimg.com/t01c1849e313e3812fe.jpg)

### <a name="header-n137"></a>二维码信息泄露

App中还有个Share功能，旨在向他人提供临时开关锁的权限：

[![](https://p4.ssl.qhimg.com/t0120d911281649234e.jpg)](https://p4.ssl.qhimg.com/t0120d911281649234e.jpg)

从App逆向的结果来看，二维码中会保存keyID为1的序列，有了任意的key就不存在权限和时间的限制了。如上的二维扫出的结果就是576C0603:4CE495E48D0BF00BF1BC85F3:1:1542885650:1542902400，与之前数据传输的记录相符：

[![](https://p4.ssl.qhimg.com/t01c80fe15d7ce63b2d.jpg)](https://p4.ssl.qhimg.com/t01c80fe15d7ce63b2d.jpg)

### <a name="header-n146"></a>其他
<li>
[服务端代码](https://github.com/smartlockpicking/hackmelock-device/blob/master/hackmelock.js#L173)中使用Math.random()来生成随机数，但这种方法并不是[cryptographically-secure](https://stackoverflow.com/questions/5651789/is-math-random-cryptographically-secure)，可能会被预测但我个人暂未想出来合适的攻击场景。</li>
1. 作者还提示存在命令注入的问题，我对nodejs和安卓了解的不多，感兴趣的同学可以探索一下。


## 0x03 总结参考

### <a name="header-n155"></a>总结
1. Android上也可以对蓝牙进行[抓包](https://blog.csdn.net/wangbf_java/article/details/81269149)，不过是主设备上HCI信道的数据包，看起来可能不是太直接。
1. 上面的虚拟门锁的使用的是默认安全级别，链路没有加密和认证配对的操作，深入探究的话可以使用工具进行中间人和重放攻击的尝试，smartlockpicking团队提供的[培训讲义](http://smartlockpicking.com/slides/BruCON0x09_2017_Hacking_Bluetooth_Smart_locks.pdf)还是很值得学习一下的。
1. 换一种角度看，喜欢做练习的同学可以尝试一下[BLE CTF](http://www.hackgnar.com/2018/06/learning-bluetooth-hackery-with-ble-ctf.html)，当然挖掘BLE相关的[漏洞](https://mp.weixin.qq.com/s/cu-DCXuqJ50YRTFDmBUrtA)也是有可能的。
### <a name="header-n166"></a>参考
- [低功耗蓝牙开发权威指南](https://book.douban.com/subject/26297532/)
- [BLUETOOTH SMART HACKMELOCK](https://smartlockpicking.com/hackmelock/)
- [物联网安全拔“牙”实战——低功耗蓝牙（BLE）初探](http://drops.xmd5.com/static/drops/tips-10109.html)
- [BLE安全入门及实战（1）](https://sec.xiaomi.com/article/38)
- [Hardwear2018BLESecurityEssentials](http://smartlockpicking.com/slides/Hardwear_2018_BLE_Security_Essentials.pdf)
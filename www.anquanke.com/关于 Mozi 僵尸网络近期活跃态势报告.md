> 原文链接: https://www.anquanke.com//post/id/219670 


# 关于 Mozi 僵尸网络近期活跃态势报告


                                阅读量   
                                **186013**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01fa4fae845eeff681.png)](https://p3.ssl.qhimg.com/t01fa4fae845eeff681.png)



## 0x01 概述

近期，360安全大脑的360安全分析响应平台在区域侧监测到 `Mozi` 僵尸网络的活动频繁，呈愈演愈烈的趋势。

`Mozi` 是一个相对较新的物联网僵尸网络，以 `DHT` 协议建立 `P2P` 网络进行通信，主要通过漏洞利用和`telnet`弱口令两种方式进行蠕虫式传播。2019年9月`360Netlab`团队捕获到相关样本，并于19年12月首次公布。

据悉该恶意软件自2019年底以来一直处于活跃状态，在`360Netlab`监测发现2020年9月11日扫描流量激增。根据`IBM X-Force`威胁情报中心统计的数据表明，`Mozi` 占观察到的IoT网络流量近90%。



## 0x02 Mozi 样本简述

`Mozi Botnet`依赖`DHT`协议建立一个`P2P`网络，通过`ECDSA384`以及`xor`算法保证自身组件和`P2P`网络的完整性和安全性。样本通过一些已知的漏洞利用和`telnet`弱口令蠕虫式传播。

### 2.1 Mozi 样本行为说明
<li style="box-sizing: border-box;">
`Mozi`在成功感染目标之后，会使用`iptable`将`SSH`、`Telnet`阻断，以防止被其他人入侵</li>
1. 然后会对特定的端口进行放行，确保自身的通信
1. 并通过`prctl`来更改进程名为sshd或者dropbear来迷惑受害者
<li style="box-sizing: border-box;">然后通过`DHT`协议建立`P2P`网络后，同步`config`文件，根据`config`文件里的指令，开始相应的任务<br><h3 name="h3-3" id="h3-3">2.2 命令执行指令列表</h3>
</li>
<li style="box-sizing: border-box;">
`DDoS`攻击</li>
1. 收集`Bot`信息
<li style="box-sizing: border-box;">执行指定`URL`的`payload`
</li>
1. 从指定的`URL`更新样本
<li style="box-sizing: border-box;">执行系统或自定义命令<br><h3 name="h3-4" id="h3-4">2.3 已知漏洞列表（Mozi多使用IoT设备远程命令执行Nday进行攻击）</h3>
</li>
### 2.3 已知漏洞列表（Mozi多使用IoT设备远程命令执行Nday进行攻击）

<tr style="box-sizing: border-box;"><th style="box-sizing: border-box; padding: 10px 18px; text-align: center; border-width: 1px 1px 0px 0px; border-style: solid; border-color: #e7ecf1; line-height: 1.42857em; vertical-align: top; font-weight: bold;">产品名</th><th style="box-sizing: border-box; padding: 10px 18px; text-align: center; border-width: 1px 1px 0px 0px; border-style: solid; border-color: #e7ecf1; line-height: 1.42857em; vertical-align: top; font-weight: bold;">漏洞</th></tr>|------

**注：Mozi 样本详细分析见 [360Netlab报告 P2P-Botnet : Mozi分析报告](https://blog.netlab.360.com/p2p-botnet-mozi/)**



## 0x03 Mozi 态势解析

通过我们持续监测和测绘发现在2020年9月11日左右`Mozi`僵尸网络扫描量激增，最大扫描源自印度和国内。

### 3.1 360蜜网监测

蜜网监测 `Mozi` 僵尸网络扫描趋势

[![](https://p403.ssl.qhimgs4.com/t015e4367de27f70fbd.png)](https://p403.ssl.qhimgs4.com/t015e4367de27f70fbd.png)

通过对`30`天`Mozi`僵尸网络独立IP的累计统计，`Mozi`僵尸网络最多的分布也是在国内和印度

[![](https://p403.ssl.qhimgs4.com/t013003e663716f132e.png)](https://p403.ssl.qhimgs4.com/t013003e663716f132e.png)

**注：图片来自于360NetLab**

### 3.2 360区域安全大脑监测

某区域被`Mozi`僵尸网络描趋势(2020年9月21-至今) [![](https://p403.ssl.qhimgs4.com/t013c1f4faf13bc3f9f.png)](https://p403.ssl.qhimgs4.com/t013c1f4faf13bc3f9f.png)

`Mozi` 全球通信分布饼图

[![](https://p403.ssl.qhimgs4.com/t014a8e79c0850107a5.jpeg)](https://p403.ssl.qhimgs4.com/t014a8e79c0850107a5.jpeg)

**注：图片来自于360安全分析响应平台**

### 3.3 360全网资产测绘平台监测

`Mozi`僵尸网络利用的产品在全球均有广泛使用，360安全大脑-Quake网络空间测绘系统通过对全网资产测绘，受影响产品(见2-3已知漏洞列表)分布如下图所示。独立`IP`数为`825011`。

全球情况 [![](https://p403.ssl.qhimgs4.com/t0154caaa5462981e40.png)](https://p403.ssl.qhimgs4.com/t0154caaa5462981e40.png)

国内情况

[![](https://p403.ssl.qhimgs4.com/t011321b0636101bf3c.png)](https://p403.ssl.qhimgs4.com/t011321b0636101bf3c.png)

**注：图中数量为累计数量，来自于360安全大脑的QUAKE资产测绘平台**



## 0x04 防范措施

### 4.1 IoCs

`Mozi`使用8组公共节点以及`Config`文件的[nd]字段指定的节点作为`bootstrap nodes`。引导新节点加入其`DHT`网络

样本内嵌公共节点如下，若设备存在与列表IoC通联情况即可能失陷。

```
dht[.]transmissionbt[.]com:6881
router[.]bittorrent[.]com:6881
router[.]utorrent[.]com:6881
bttracker[.]debian[.]org:6881
212[.]129[.]33[.]59:6881
82[.]221[.]103[.]244:6881
130[.]239[.]18[.]159:6881
87[.]98[.]162[.]88:6881
```

### 4.2 Telnet 弱口令列表

Mozi 僵尸网络Telnet 使用弱口令列表如下 或者 [附件Mozi_telnet弱口令下载](https://cert.360.cn/workflow/file/download/5f86e4c2127d15004c231e1e)

<tr style="box-sizing: border-box;"><th style="box-sizing: border-box; padding: 10px 18px; text-align: center; border-width: 1px 1px 0px 0px; border-style: solid; border-color: #e7ecf1; line-height: 1.42857em; vertical-align: top; font-weight: bold;"></th><th style="box-sizing: border-box; padding: 10px 18px; text-align: center; border-width: 1px 1px 0px 0px; border-style: solid; border-color: #e7ecf1; line-height: 1.42857em; vertical-align: top; font-weight: bold;"></th><th style="box-sizing: border-box; padding: 10px 18px; text-align: center; border-width: 1px 1px 0px 0px; border-style: solid; border-color: #e7ecf1; line-height: 1.42857em; vertical-align: top; font-weight: bold;"></th><th style="box-sizing: border-box; padding: 10px 18px; text-align: center; border-width: 1px 1px 0px 0px; border-style: solid; border-color: #e7ecf1; line-height: 1.42857em; vertical-align: top; font-weight: bold;"></th></tr>|------



## 0x05 产品侧解决方案

### 5.1 360 安全分析响应平台

360区域大脑的安全分析响应平台借助智能关联分析引擎，将各数据孤岛中的信息进行综合理解与场景化分析，为Mozi 僵⼫⽹络的专项任务提供服务。请⽤户联系相关产品区域负责⼈或(shaoyulong#360.cn)获取对应产品。 [![](https://p403.ssl.qhimgs4.com/t015baffd7583acc85c.jpeg)](https://p403.ssl.qhimgs4.com/t015baffd7583acc85c.jpeg)

### 5.2 360 QUAKE资产测绘平台

360安全大脑的QUAKE资产测绘平台(quake.360.cn)通过资产测绘技术手段，对该类漏洞进行监测，请用户联系相关产品区域负责人或(quake#360.cn)获取对应产品。

[![](https://p403.ssl.qhimgs4.com/t017cad2f9af00f8db2.jpeg)](https://p403.ssl.qhimgs4.com/t017cad2f9af00f8db2.jpeg)



## 0x06 时间线

**2019-09-03** 360Netlab 首次捕获到 Mozi 样本

**2019-12-23** 360Netlab 首次公布 Mozi 僵尸网络分析报告

**2020-09-22** 360安全大脑—安全分析响应平台持续监测到活跃

**2020-10-15** 360-CERT 发布 Mozi 僵尸网络态势报告



## 0x07 参考链接
1. [https://blog.netlab.360.com/p2p-botnet-mozi/](https://blog.netlab.360.com/p2p-botnet-mozi/)
1. [https://securityaffairs.co/wordpress/108537/malware/mozi-botnet-iot-traffic.html](https://securityaffairs.co/wordpress/108537/malware/mozi-botnet-iot-traffic.html)
1. [https://securityintelligence.com/posts/botnet-attack-mozi-mozied-into-town/](https://securityintelligence.com/posts/botnet-attack-mozi-mozied-into-town/)
1. [https://www.microsoft.com/security/blog/2020/10/12/trickbot-disrupted/](https://www.microsoft.com/security/blog/2020/10/12/trickbot-disrupted/)
1. [https://blogs.microsoft.com/on-the-issues/2020/03/10/necurs-botnet-cyber-crime-disrupt/](https://blogs.microsoft.com/on-the-issues/2020/03/10/necurs-botnet-cyber-crime-disrupt/)
1. [https://finance.sina.com.cn/tech/2020-10-12/doc-iiznctkc5171878.shtml](https://finance.sina.com.cn/tech/2020-10-12/doc-iiznctkc5171878.shtml)
1. [https://cert.360.cn/warning/detail?id=95110cde8635056292e62424b9da1842](https://cert.360.cn/warning/detail?id=95110cde8635056292e62424b9da1842)
1. [https://paper.seebug.org/1347/](https://paper.seebug.org/1347/)
1. [https://www.internet-sicherheit.de/research/botnetze/iot-botnetze/mozi/](https://www.internet-sicherheit.de/research/botnetze/iot-botnetze/mozi/)
1. [https://securityintelligence.com/posts/botnet-attack-mozi-mozied-into-town/](https://securityintelligence.com/posts/botnet-attack-mozi-mozied-into-town/)
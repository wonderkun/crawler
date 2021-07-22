> 原文链接: https://www.anquanke.com//post/id/145350 


# GPON 漏洞的在野利用（二）——Satori 僵尸网络


                                阅读量   
                                **75802**
                            
                        |
                        
                                                                                    


<li>
**Satori**：satori是臭名昭著的mirai僵尸网络变种，该恶意代码团伙在2018-05-10 05:51:18 首次加入到抢夺 GPON 易感染设备的行列，并在短短时间内就挤掉了 muhstik，成为我们视野范围内感染频次最高的一员。另外，我们测试验证了Satori的投入模块，在某些版本的设备固件上是能成功执行的。这使得Satori显著区别于参与聚会的其他僵尸网络。</li>
<li>
**Mettle**：一个恶意代码团伙，基于在越南的IP地址 （C2 210.245.26.180:4441，scanner 118.70.80.143）和mettle开源控制模块</li>
<li>
**Hajime**：hajime的本次更新也包含了 GPON 本次的漏洞利用</li>
<li>
**两个Mirai变种**：至少两个恶意代码团伙正在积极利用该漏洞传播mirai变种。其中第二个，已经被称为 [omni](https://blog.newskysecurity.com/cve-2018-10561-dasan-gpon-exploit-weaponized-in-omni-and-muhstik-botnets-ad7b1f89cff3)。</li>
<li>
**Omni**：在 newskysecurity.com 首次公开批露后，我们确认其文档中称为 omni 的僵尸网络，就是我们之前提及的mirai变种之二。</li>
<li>
**imgay**：这看起来是一个正在开发中的僵尸网络，其功能尚不完善。</li>
本篇文章将主要介绍 Satori 僵尸网络的本轮更新。后续我们也许会发布系列文章的第三篇，对剩下的其他僵尸网络做一描述。第三篇预期会是系列文章的最后一篇，如果没有更多僵尸网络加入聚会的话。



## 不同僵尸网络的投递力度对比

我们使用蜜罐来采集本次GPON相关漏洞的利用情况。下面列出了我们看到的攻击载荷活动频次Top10，完整的列表可以见文末IoC部分：

```
%    botnet_name url
57.77%    satori  hxxp://185.62.190.191/r  
32.66%    muhstik hxxp://51.254.219.134/gpon.php  
2.20%    muhstik hxxp://162.243.211.204/gpon  
1.99%    muhstik hxxp://165.227.78.159/gponb6abe42c3a9aa04216077697eb1bcd44.php  
0.96%    muhstik hxxp://128.199.251.119/gpon.php  
0.64%    imgay   hxxp://149.28.96.126/forky  
0.60%    imgay   hxxp://149.28.96.126/80  
0.57%    imgay   hxxp://149.28.96.126/  
0.57%    imgay   hxxp://149.28.96.126/81  
0.53%    muhstik hxxp://165.227.78.159/gpon.php  
```

从上面这里采集的数据来看，Satori（累积57.80%）和 muhstik（累积38.87%）是当前GPON漏洞利用的主力。



## Satori 本轮更新涉及的恶意代码下载链接

Satori 在本轮更新中，使用了下面这组URL传播恶意代码：

```
hxxp://185.62.190.191/arm  
hxxp://185.62.190.191/arm7  
hxxp://185.62.190.191/m68k  
hxxp://185.62.190.191/mips  
hxxp://185.62.190.191/mipsel  
hxxp://185.62.190.191/r  
hxxp://185.62.190.191/sparc  
```



## Satori 本轮更新涉及的恶意代码样本分析

我们对其中的样本 [http://185.62.190.191/arm](http://185.62.190.191/arm) （md5hash:d546bc209d315ae81869315e8d536f36)做了分析。

这个样本的代码，与原始版本的Satori已经有了比较大的变化，单纯从样本二进制方面，与原来的satori的关系已经不太大。但是考虑到其在关键字符串、域名 TXT 信息、邮件地址等多方面的联系，我们仍然把其归在Satori变种之下。

该样本中有四个加密字符串，对应的解密结果分别如下：
1. c.sunnyjuly.gq
1. Viam0610TCiLpBvezPFGL2aG
1. `{`“id”:0,”jsonrpc”:”2.0″,”method”:”miner_reboot”`}`
1. `{`“id”:0,”jsonrpc”:”2.0″,”method”:”miner_file”,”params”:[“reboot.bat”,”4574684463724d696e657236342e657865202d65706f6f6c206574682d7573322e6477617266706f6f6c2e636f6d3a38303038202d6577616c20307864303839376461393262643764373735346634656131386638313639646263303862656238646637202d6d6f64652031202d6d706f72742033333333202d6d707377206775764a746f43785539″]`}`
第一个字符串为C2，第二个字符串会在控制台被输出。 第三、四个字符串在样本中仅被定义未被发现使用。值得一提的是这两个字符串和 [Satori.robber](https://blog.netlab.360.com/art-of-steal-satori-variant-is-robbing-eth-bitcoin-by-replacing-wallet-address/) 中用到的代码相近，这可以作为该样本与 Satori 同源的一个旁证。

第四个字符串后面的Hex 部分如下，包含了一个矿池地址，和一个钱包地址：

```
EthDcrMiner64.exe -epool eth-us2.dwarfpool.com:8008 -ewal 0xd0897da92bd7d7754f4ea18f8169dbc08beb8df7 -mode 1 -mport 3333 -mpsw guvJtoCxU9
```



## Satori 本轮更新中涉及到的钱包地址

这个钱包地址的信息可查，如下。如果按照每24小时产生0.05 个 ETH 币，从5月10日到现在估计共挖取了 0.3 个 ETH 币。按照现行每个 ETH 代币价格 700 美金估算，Satori在目前6天的行动中共获取了大约 200 美元的收益。

```
$ curl "http://dwarfpool.com/eth/api?wallet=0xd0897da92bd7d7754f4ea18f8169dbc08beb8df7"
`{`
  "autopayout_from": "0.050",
  "earning_24_hours": "0.04629051",
  "error": false,
  "immature_earning": 0.0037158866909999997,
  "last_payment_amount": "0.05286277",                        #上一次发薪数额
  "last_payment_date": "Tue, 15 May 2018 17:26:04 GMT",       #上一次发薪时间
  "last_share_date": "Wed, 16 May 2018 09:46:47 GMT",
  "payout_daily": false,
  "payout_request": false,
  "total_hashrate": 137.57,
  "total_hashrate_calculated": 781.0,
  "transferring_to_balance": 0,
  "wallet": "0xd0897da92bd7d7754f4ea18f8169dbc08beb8df7",     #钱包地址
  "wallet_balance": "0.02818296",                             #帐户余额，待发
  "workers": `{`
    "": `{`
      "alive": true,
      "hashrate": 137.57,
      "hashrate_below_threshold": false,
      "hashrate_calculated": 781.0,
      "last_submit": "Wed, 16 May 2018 09:46:47 GMT",
      "second_since_submit": 335,
      "worker": ""
    `}`
  `}`
`}`
```



## Satori 本轮更新涉及域名解析，以及其对外界传递的信息

另外，c.sunnyjuly.gq 在DNS系统中一直没有提供IP地址解析，相反其提供了 TXT 解析，可以视为其作者对外界传达的信息。作者前后两次传递的信息如下：

```
2018-05-14 04:22:43    c.sunnyjuly.gq  DNS_TXT Irdev here, i can be reached at village@riseup.net, goodbye  
2018-05-10 00:55:06    c.sunnyjuly.gq  DNS_TXT It is always the simple that produces the marvelous
```

值得对比的是，在 [Satori.robber](https://blog.netlab.360.com/art-of-steal-satori-variant-is-robbing-eth-bitcoin-by-replacing-wallet-address/) 中，Satori 的作者通过二进制文件向外界传递了如下信息。两次出现的信息，书写手法类似，所留下的邮件地址也均为 riseup.net 提供的邮箱。

```
Satori dev here, dont be alarmed about this bot it does not currently have any malicious packeting purposes move along. I can be contacted at curtain@riseup.net
```



## Satori 本轮更新导致了近期 端口3333 上的扫描

当前版本的Satori还会扫描 3333 端口，并直接导致了我们在 [ScanMon](https://scan.netlab.360.com/#/dashboard?tsbeg=1523894400000&amp;tsend=1526486400000&amp;dstport=3333&amp;toplistname=srcas&amp;topn=10) 上的一次较大波动。这次扫描的来源大约有17k个独立IP地址，主要源自 Uninet S.A. de C.V.，隶属 telmex.com，位于墨西哥。

[![](https://blog.netlab.360.com/content/images/2018/05/satori-port-3333-scan.png)](https://blog.netlab.360.com/content/images/2018/05/satori-port-3333-scan.png)



## 联系我们

感兴趣的读者，可以在 [**twitter**](https://twitter.com/360Netlab) 或者在微信公众号 **360Netlab** 上联系我们。



## Ioc

曾经在 muhstik 控制之下，但已经被安全社区清除的IP列表：

```
139.99.101.96:9090    AS16276 OVH SAS  
142.44.163.168:9090    AS16276 OVH SAS  
142.44.240.14:9090    AS16276 OVH SAS  
144.217.84.99:9090    AS16276 OVH SAS  
145.239.84.0:9090    AS16276 OVH SAS  
145.239.93.125:9090    AS16276 OVH SAS  
147.135.210.184:9090    AS16276 OVH SAS  
192.99.71.250:9090    AS16276 OVH SAS  
51.254.221.129    "AS16276 OVH SAS"  
66.70.190.236:9090    AS16276 OVH SAS #当前未生效  
51.254.219.137    "AS16276 OVH SAS"  
51.254.219.134    "AS16276 OVH SAS"  
191.238.234.227    "AS8075 Microsoft Corporation"
```

近期我们观察到的利用 GPON 分发恶意软件的下载链接

```
%    botnet_name url Country &amp; Region    ASN
57.77%    satori  hxxp://185.62.190.191/r Netherlands/NL  AS49349 Dotsi, Unipessoal Lda.  
32.66%    muhstik hxxp://51.254.219.134/gpon.php  France/FR   AS16276 OVH SAS  
2.20%    muhstik hxxp://162.243.211.204/gpon United States/US New York   AS62567 DigitalOcean, LLC  
1.99%    muhstik hxxp://165.227.78.159/gponb6abe42c3a9aa04216077697eb1bcd44.php  United States/US Clifton    AS14061 DigitalOcean, LLC  
0.96%    muhstik hxxp://128.199.251.119/gpon.php Singapore/SG Singapore  AS14061 DigitalOcean, LLC  
0.64%    imgay   hxxp://149.28.96.126/forky  United States/US College Park   None  
0.60%    imgay   hxxp://149.28.96.126/80 United States/US College Park   None  
0.57%    imgay   hxxp://149.28.96.126/   United States/US College Park   None  
0.57%    imgay   hxxp://149.28.96.126/81 United States/US College Park   None  
0.53%    muhstik hxxp://165.227.78.159/gpon.php  United States/US Clifton    AS14061 DigitalOcean, LLC  
0.32%    muhstik hxxp://162.243.211.204/gponexec United States/US New York   AS62567 DigitalOcean, LLC  
0.28%    imgay   hxxp://149.28.96.126/8080   United States/US College Park   None  
0.25%    untitled-1  hxxp://186.219.47.178:8080  Brazil/BR   AS262589 INTERNEXA Brasil Operadora de Telecomunicações S.A  
0.11%    imgay   hxxp://149.28.96.126/imgay  United States/US College Park   None  
0.11%    muhstik hxxp://162.243.211.204/aio  United States/US New York   AS62567 DigitalOcean, LLC  
0.11%    muhstik hxxp://46.243.189.102/  Netherlands/NL  AS205406 Hostio Solutions B.V.  
0.07%    untitled-2  hxxp://114.67.227.83/busybox    China/CN Beijing    AS4808 China Unicom Beijing Province Network  
0.07%    omni    hxxp://185.246.152.173/omni Netherlands/NL  AS56630 Melbikomas UAB  
0.07%    untitled-2  nc://114.67.227.83:7856 China/CN Beijing    AS4808 China Unicom Beijing Province Network  
0.04%    satori  hxxp://185.62.190.191/s Netherlands/NL  AS49349 Dotsi, Unipessoal Lda.  
0.04%    untitled-2  hxxp://114.67.227.83    China/CN Beijing    AS4808 China Unicom Beijing Province Network  
0.04%    untitled-3  hxxp://209.141.42.3/gponx   United States/US Las Vegas  AS53667 FranTech Solutions  
0.04%    untitled-2  hxxp://114.67.227.83/   China/CN Beijing    AS4808 China Unicom Beijing Province Network  
```

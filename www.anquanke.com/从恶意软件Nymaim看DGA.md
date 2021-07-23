> 原文链接: https://www.anquanke.com//post/id/179989 


# 从恶意软件Nymaim看DGA


                                阅读量   
                                **248588**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者johannesbader，文章来源：johannesbader.ch
                                <br>原文地址：[https://www.johannesbader.ch/2018/04/the-new-domain-generation-algorithm-of-nymaim/](https://www.johannesbader.ch/2018/04/the-new-domain-generation-algorithm-of-nymaim/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0141e15d7567674bdd.jpg)](https://p3.ssl.qhimg.com/t0141e15d7567674bdd.jpg)



Nymaim恶意软件首次发现是在2013年。它主要是被用作其他恶意软件的下载器，如勒索软件，后来它也开始为了实现点击欺诈而进行搜索操控。

也许是因为这个恶意软件使用了一种有效而有趣的混淆，关于Nymaim和它得DGA的文章已经有了很多。这种混淆催生了很多有创造性的帮助分析恶意软件的工具，例如 [GovCERT.CH](https://www.govcert.admin.ch/blog/29/taking-a-look-at-nymaim) 或者[CERT Polska](https://github.com/CERT-Polska/nymaim-tools)。

除了混淆之外，Nymaim的有趣之处还在于它试图通过在A记录种添加校验和与在使用之前转换IP地址保护自己，具体介绍可以看CERT Polska的 [“Nymaim revisited”](https://www.cert.pl/en/news/single/nymaim-revisited/)，Talos 的 [“Threat Spotlight: GozNym”](https://blog.talosintelligence.com/2016/09/goznym.html)和Alberto Ortega的 [“Nymaim Origins, Revival and Reversing Tales” ](https://www.botconf.eu/wp-content/uploads/2016/11/PR18-Nymaim-ORTEGA.pdf)。

本月，Nymaim的新版本对上述特性进行了一些修改：
- 除了加壳之外，混淆被全部的抛弃。相反，恶意软件甚至使用有用的日志消息和带有描述性名称的配置。
- IP转换略有变化，使用了不同的常量，但其他方面都坚持与之前的过程相同。
- DGA已经被完全重写。它现在是基于单词列表的，比如Matsnu的DGA, Suppobox，或者Nymaim的近亲Gozi。
- 除了使用DGA，Nymaim还有一个硬编码域名列表，它们遵循与DGA域名相同的模式，但是在依赖于时间的DGA域名之前进行尝试。
这篇博客文章关注的是Nymaim的DGA和IP转换方面。例如，下面是2018年4月27日的前10个域名：

```
virginia-hood.top
shelter-downloadable.ps
tylerpreparation.sg
zolofteffectiveness.ch
stakeholders-looked.hn
williampassword.sc
thailandcool.re
thoughtsjazz.ec
recovery-hairy.ac
workshopsforms.hn
```

我分析了来自Virustotal的样本:

|MD5|30bce8f7ac249057809d3ff1894097e7
|------
|SHA-256|73f06bed13e22c2ab8b41bde5fc32b6d91680e87d0f57b3563c629ee3c479e73
|SHA-1|b629c20b4ef0fd31c8d36292a48aa3a8fbfdf09c
|文件大小|484 KB
|编译时间戳|2010-06-13 18:50:03 (**可能是假的**)
|首次上传至 Virustotal的时间|2018-04-17 21:49:18
|Virustotal 链接|[link](https://www.virustotal.com/#/file/73f06bed13e22c2ab8b41bde5fc32b6d91680e87d0f57b3563c629ee3c479e73)

我将其解压缩得以下可执行文件。所有截图都来自加载地址0x400000的这个示例：

|MD5|379ba8e55498cb7a71ec4dcd371968af
|------
|SHA-256|3eb9bbe3ed251ec3fd1ff9dbcbe4dd1a2190294a84ee359d5e87804317bac895
|SHA-1|5f522dda6b003b151ff60b83fe326400b9ed7716
|文件大小|368 KB
|编译时间戳|2018-03-02 23:12:20
|首次上传至 Virustotal的时间|2018-04-26 12:19:41 (**我上传的**)
|Virustotal 链接|[link](https://www.virustotal.com/#/file/3eb9bbe3ed251ec3fd1ff9dbcbe4dd1a2190294a84ee359d5e87804317bac895/detection)



## 分析

本节描述DGA的详细信息。如果你只对Python的实现感兴趣，请参阅DGA部分。

### <a class="reference-link" name="%E7%A7%8D%E5%AD%90"></a>种子

Nymaim的新DGA的种子由三部分组成：
1. 硬编码的32位大写的16进制字符串，推测为MD5散列值（在分析的样本中是`3138C81ED54AD5F8E905555A6623C9C9`）。Nymaim将它称为`生成密钥`。
1. 一年中从零开始的一天。例如，1月1日是第0天。这个值比ISO定义的值小1,ISO定义1月1日为一年中的第1天。从这个值减去一个计数器中的值，计数器从0开始，一直到一个天数增量`DayDelta`（在样本中是10）。这意味着如果有必要，DGA将重新访问过去10天的域名（除了在年关的时候，详情见下面的滑动窗口）。
1. 当年的最后两位数字。
这三个值组合成一个字符串。然后对这个字符串进行md5散列，其结果表示为小写的十六进制字符串。请注意，这与`生成密钥`相反，`生成密钥`都是大写的。得到的字符串是随后的伪随机数生成器的种子和基础。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.johannesbader.ch/images/2018-04-29-the-new-domain-generation-algorithm-of-nymaim/seeding.png)

### <a class="reference-link" name="%E4%BC%AA%E9%9A%8F%E6%9C%BA%E6%95%B0%E7%94%9F%E6%88%90%E5%99%A8"></a>伪随机数生成器

伪随机数生成器(PRNG)使用MD5哈希字符串的前8个字符，并将其作为32位整数(即随机数)的大端十六进制表示。然后丢弃MD5散列的前7个字符，其余的字符再次用MD5散列并表示为小写的十六进制字符串。该字符串的前8个字符表示下一个伪随机值。关于整个过程和伪随机数生成器，请参阅下图:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.johannesbader.ch/images/2018-04-29-the-new-domain-generation-algorithm-of-nymaim/prng.png)

### <a class="reference-link" name="DGA%E7%AE%97%E6%B3%95"></a>DGA算法

DGA使用四个随机值从四个列表中选择字符串:
1. 选择第一个单词列表中的一个单词。
1. 选择一个分隔符。
1. 选择第二个单词列表中的一个单词。
1. 选择顶级域
然后将四个字符串连接起来形成域名。单词的选择是用随机值除以列表长度的余数作为索引从列表中选择:

```
CString *__thiscall dga(_DWORD *config, CString *szDomainName)
`{`
  dgaconfig *cfg; // esi@1
  int v3; // eax@2
  unsigned int nNumberOfFirstWords; // ecx@3
  randnrs objRandNrs; // [esp+Ch] [ebp-2Ch]@1
  int dgb2; // [esp+20h] [ebp-18h]@1
  int nr_random_values; // [esp+24h] [ebp-14h]@1
  char cstrDomainName; // [esp+28h] [ebp-10h]@3
  int dbg; // [esp+34h] [ebp-4h]@1

  dgb2 = 0;
  cfg = config;
  init_random_nrs(&amp;objRandNrs);
  objRandNrs.self = &amp;GetRuntimeClass;
  nr_random_values = 4;
  dbg = 1;
  do
  `{`
    v3 = rand_0(&amp;cfg-&gt;random_hash);
    store_rand(objRandNrs.field_8, v3);
    --nr_random_values;
  `}`
  while ( nr_random_values );
  CString::CString(&amp;cstrDomainName);
  nNumberOfFirstWords = cfg-&gt;nNumberOfFirstWords;
  LOBYTE(dbg) = 2;
  CString::operator+=(&amp;cstrDomainName, cfg-&gt;rgFirstWords + 4 * (*objRandNrs.r % nNumberOfFirstWords));
  CString::operator+=(&amp;cstrDomainName, cfg-&gt;rgSeparators + 4 * (*(objRandNrs.r + 4) % cfg-&gt;nNumberOfSeparators));
  CString::operator+=(&amp;cstrDomainName, cfg-&gt;rgSecondWords + 4 * (*(objRandNrs.r + 8) % cfg-&gt;nNumberOfSecondWords));
  CString::operator+=(&amp;cstrDomainName, cfg-&gt;rgTLDs + 4 * (*(objRandNrs.r + 12) % cfg-&gt;nNumberOfTLDs));
  CString::CString(szDomainName, &amp;cstrDomainName);
  dgb2 = 1;
  LOBYTE(dbg) = 1;
  CString::~CString(&amp;cstrDomainName);
  LOBYTE(dbg) = 0;
  cleanup_0(&amp;objRandNrs);
  return szDomainName;
`}`
```

第一个单词列表包含2450个以字母R到Z开头的单词。最短的有4个字母，最长的有18个(**telecommunications**):

```
"reaches", 
    "reaching", 
    "reaction", 
    "reactions", 
    "read", 
    "reader", 
    "readers", 
    "readily", 
    "reading", 
    "readings", 
    "reads", 
    "ready", 
    "real", 
    "realistic", 
    ...
    "zoom",                                                                 
    "zoophilia",                                                            
    "zope",                                                                 
    "zshops"
```

只有两个分隔符:零长度字符串和连字符`-`。第二个单词列表包含以字母C到R开头的4387个单词。最后一个单词是`reached`，而第一个单词列表恰恰是以`reaches`开始。

最后，这里包含了74个顶级域，其中顶级域`.com`出现了4次，`.net`出现了3次，这增加了`.com`和`.net`被选中的概率。

顶级域列表如下：

`.com`, `.com`, `.com`, `.net`, `.net`, `.net`, `.ac`, `.ad`, `.at`, `.am`, `.az`, `.be`, `.biz`, `.bt`, `.by`, `.cc`, `.ch`, `.cm`, `.cn`, `.co`, `.com`, `.cx`, `.cz`, `.de`, `.dk`, `.ec`, `.eu`, `.gs`, `.hn`, `.ht`, `.id`, `.in`, `.info`, `.it`, `.jp`, `.ki`, `.kr`, `.kz`, `.la`, `.li`, `.lk`, `.lv`, `.me`, `.mo`, `.mv`, `.mx`, `.name`, `.net`, `.nu`, `.org`, `.ph`, `.pk`, `.pl`, `.pro`, `.ps`, `.re`, `.ru`, `.sc`, `.sg`, `.sh`, `.su`, `.tel`, `.tf`, `.tj`, `.tk`, `.tm`, `.top`, `.uz`, `.vn`, `.win`, `.ws`, `.wtf`, `.xyz`, `.yt`。

### <a class="reference-link" name="%E6%BB%91%E5%8A%A8%E7%AA%97%E5%8F%A3"></a>滑动窗口

DGA每天生成一定数量（`MaxDomainsForTry`）的域名，对于分析的样本，域名数量（`MaxDomainsForTry`）为64。生成64个域名之后，伪随机数生成器通过从一年的某一天减去1获得前一天的种子重新计算随机数。这样算来，最多生成64*(10+1)= 704个域名:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.johannesbader.ch/images/2018-04-29-the-new-domain-generation-algorithm-of-nymaim/sliding1.png)

在年关的时候，当日期比天数增量（`DayDelta`）小，那么天数的偏移量会变成负数。例如，在一月三号的滑动窗口的值为2，1，0，-1，… ，-8。负数将会产生新的一组域名。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.johannesbader.ch/images/2018-04-29-the-new-domain-generation-algorithm-of-nymaim/sliding2.png)

### <a class="reference-link" name="%E7%A1%AC%E7%BC%96%E7%A0%81%E5%9F%9F%E5%90%8D"></a>硬编码域名

Nymaim有一个包含46个硬编码域名的列表，它们遵循DGA模式，两个单词之间用一个可选的连字符分隔。这些域名都使用`.com`顶级域。在获得任何DGA域名之前，总是先对硬编码域名进行测试。对于分析的样本中，硬编码域名如下：

```
sustainabilityminolta.com
theories-prev.com
starringmarco.com
seekerpostcards.com
threadsmath.com
recall-pioneer.com
waste-neighborhood.com
usage-maternity.com
standings-descriptions.com
volumedatabase.com
summaries-heading.com
stoppedmeaningful.com
singles-october.com
scottish-fact.com
weblogcourage.com
troycyber.com
reply-phantom.com
wagon-crime.com
sharp-louisiana.com
suitedminerals.com
saskatchewan-funds.com
sites-experts.com
techrepublicexemption.com
serbia-harbor.com
super-ideas.com
translationdoor.com
wildhelmet.com
shoefalse.com
remainedoxide.com
wild-motels.com
staticlesbian.com
valentinequeensland.com
travelling-mechanics.com
solelypersonal.com
resulting-museum.com
towndayton.com
workedforest.com
yorkshire-engineer.com
stockholm-effect.com
reynoldshydrogen.com
sluts-persistent.com
satisfaction-granted.com
slut-hentai.com
territoriesprayers.com
thumbnailsfragrance.com
undergraduategraphical.com
```

### <a class="reference-link" name="%E5%90%8D%E7%A7%B0%E6%9C%8D%E5%8A%A1%E5%99%A8%E6%B5%8B%E8%AF%95"></a>名称服务器测试

Nymaim的一个显著特性是使用DNS查询名称服务器记录(NS)。Nymaim检查任何一个响应中是否包含它称为`BlackNsWords`的列表中的单词。这写单词通常与沉洞(Sinkhole)相关：

```
sinkhole
amazonaws
honeybot
honey
parking
domaincontrol
dynadot
```

如果Nymaim在NS资源记录中找到这些单词中的任何一个，它就不会使用这个域名。

### <a class="reference-link" name="%E9%A6%96%E9%80%89DNS%E6%9C%8D%E5%8A%A1%E5%99%A8"></a>首选DNS服务器

Nymaim使用一个称为`PreferredDnsServers`的DNS服务器列表，可能是因为这些服务器不太可能更改或阻塞DNS请求。

<th style="text-align: left;">IP</th><th style="text-align: left;">Company</th>
|------
<td style="text-align: left;">8.8.8.8</td><td style="text-align: left;">Google</td>
<td style="text-align: left;">8.8.4.4</td><td style="text-align: left;">Google</td>
<td style="text-align: left;">156.154.70.1</td><td style="text-align: left;">Neustar Security</td>
<td style="text-align: left;">156.154.71.1</td><td style="text-align: left;">Neustar Security</td>
<td style="text-align: left;">208.67.222.222</td><td style="text-align: left;">OpenDNS</td>
<td style="text-align: left;">208.67.220.220</td><td style="text-align: left;">OpenDNS</td>

### <a class="reference-link" name="IP%E8%BD%AC%E6%8D%A2"></a>IP转换

与Nymaim的早期版本一样，A资源记录并不是C2服务器的ip地址。真实的地址需要通过一系列可逆的异或和减法步骤对ip进行变换才能得到。Talos 威胁情报在2017年9月写了一份描述该算法的详细报告。

下图视图片段显示了IP的转换:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.johannesbader.ch/images/2018-04-29-the-new-domain-generation-algorithm-of-nymaim/iptransformation.png)

在这篇博客文章的末尾可以找到用于在两个方向上执行IP转换的Python脚本。

### <a class="reference-link" name="%E6%A0%A1%E9%AA%8C%E5%92%8C%E6%B5%8B%E8%AF%95"></a>校验和测试

Nymaim仍然使用A资源记录的校验和测试。例如，下面是一个在编写本文时正在运行C2服务器域名的ip:

```
&gt; dig @8.8.8.8 +short -t A sustainabilityminolta.com
127.33.12.14
127.33.12.15
192.202.176.55
126.56.117.50
```

下表列出了这四个IP(第一列)和转换后的真实IP(第二列)。第三列是整数表示:

<th style="text-align: left;">IP</th><th style="text-align: left;">IP’</th><th style="text-align: left;">value</th>
|------
<td style="text-align: left;">127.33.12.14</td><td style="text-align: left;">127.0.0.0</td><td style="text-align: left;">0x0000007F</td>
<td style="text-align: left;">127.33.12.15</td><td style="text-align: left;">127.0.0.1</td><td style="text-align: left;">0x0100007F</td>
<td style="text-align: left;">192.202.176.55</td><td style="text-align: left;">192.42.116.41</td><td style="text-align: left;">0x29742AC0</td>
<td style="text-align: left;">**126.56.117.50**</td><td style="text-align: left;">**190.43.116.42**</td><td style="text-align: left;">**0x2A742BBE**</td>

Nymaim将检查所有整数值，看看它们是否是其余值的和。在上面的例子中，加粗的IP`190.43.116.42`是A记录`126.56.117.50`的转换结果。用小端整数可以表示为`0x2A742BBE`。这对应于将剩余ip的整数表示形式相加得到的校验和，也就是`0x2A742BBE = 0x0000007F + 0x0100007F + 0x29742AC0`。

匹配了校验和的IP将从列表中删除，它只作为其他IP的校验和。然后Nymaim将一个接一个地测试转换后的ip:
1. DNS对`sustainabilityminolta.com`的NS资源发出请求，以检查是否为沉洞(Sinkhole)。响应`dns100.ovh.net`不包含`BlackNsWords`中任何单词, Nymaim继续查询A记录。
1. 对A记录的DNS请求返回四个转换后的ip。因为第四个IP是其余三个IP的校验和，所以Nymaim继续按顺序联系IP。
<li>第一个非本地IP地址`192.42.116.41`使用HTTP POST请求联系：`http://192.42.116.41/index.php`
</li>
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://www.johannesbader.ch/images/2018-04-29-the-new-domain-generation-algorithm-of-nymaim/traffic_example.png)

### <a class="reference-link" name="%E8%AF%B7%E6%B1%82"></a>请求

实际的C2服务器请求是HTTP post。内容使用会话密钥进行AES加密，会话密钥受非对称加密保护。第一个C2请求大约是900字节。URL文件名硬编码为`index.php`:

```
http://192.42.116.41/index.php
```

### <a class="reference-link" name="DGA%E7%89%B9%E5%BE%81"></a>DGA特征

<th style="text-align: left;">property</th><th style="text-align: left;">value</th>
|------
<td style="text-align: left;">类型</td><td style="text-align: left;">TDD (时间依赖的确定性)</td>
<td style="text-align: left;">生成模式</td><td style="text-align: left;">j基于伪随机数生成器的MD5</td>
<td style="text-align: left;">种子</td><td style="text-align: left;">生成密钥和当前日期</td>
<td style="text-align: left;">域名改变频率</td><td style="text-align: left;">每天，具有一个11天的滑动窗口</td>
<td style="text-align: left;">每天的域名数</td><td style="text-align: left;">46 个硬编码域名+64个新生成域名 + 640 之前生成的域名</td>
<td style="text-align: left;">序列</td><td style="text-align: left;">有序的</td>
<td style="text-align: left;">域名之间的等待时间</td><td style="text-align: left;">无</td>
<td style="text-align: left;">顶级域</td><td style="text-align: left;">69 个不同的顶级域, 更偏好于`.com` 和 `.net`</td>
<td style="text-align: left;">二级域特征</td><td style="text-align: left;">两个单词表中的单词和一个连接符</td>
<td style="text-align: left;">二级域长度ength</td><td style="text-align: left;">8 (e.g., **realrays.kr**) – 34 (e.g., **telecommunications-pharmaceuticals.name**)</td>



## 结果

在本节中，你将看到DGA的Python实现，以及用于Nymaim的IP转换的脚本。

### <a class="reference-link" name="DGA%E7%AE%97%E6%B3%95"></a>DGA算法

DGA需要一个比较大的单词列表（ [words.json](https://www.johannesbader.ch/2018/04/the-new-domain-generation-algorithm-of-nymaim/2018-04-29-the-new-domain-generation-algorithm-of-nymaim/words.json)），将它放在与DGA脚本相同的目录中。你可以使用`-d`或`——date`生成特定日期的域名，如：

```
&gt; python dga.py -d 2018-04-27



import json
import argparse
from datetime import datetime
import hashlib


class Rand:

    def __init__(self, seed, year, yday, offset=0):
        m = self.md5(seed)
        s = "`{``}``{``}``{``}`".format(m, year, yday + offset)
        self.hashstring = self.md5(s)

    @staticmethod
    def md5(s):
        return hashlib.md5(s.encode('ascii')).hexdigest()

    def getval(self):
        v = int(self.hashstring[:8], 16)
        self.hashstring = self.md5(self.hashstring[7:])
        return v

def dga(date):
    with open("words.json", "r") as r:
        wt = json.load(r)

    seed = "3138C81ED54AD5F8E905555A6623C9C9"
    daydelta = 10
    maxdomainsfortry = 64
    year = date.year % 100
    yday = date.timetuple().tm_yday - 1

    for dayoffset in range(daydelta + 1):
        r = Rand(seed, year, yday - dayoffset)
        for _ in range(maxdomainsfortry):
            domain = ""
            for s in ['firstword', 'separator', 'secondword', 'tld']:
                ss = wt[s]
                domain += ss[r.getval() % len(ss)]
            print(domain)

if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--date", help="as YYYY-mm-dd")
    args = parser.parse_args()
    date_str = args.date
    if date_str:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        date = datetime.now() 
    dga(date)
```

### <a class="reference-link" name="IP%E8%BD%AC%E6%8D%A2%E8%84%9A%E6%9C%AC"></a>IP转换脚本

下面的Python脚本可用于在两个方向转换Nymaim IP地址，并查看IP地址列表是否满足校验和要求：

```
import argparse


def iptoval(ip):
    els = [int(_) for _ in ip.split(".")]
    v = 0
    for el in els[::-1]:
        v &lt;&lt;= 8
        v += el
    return v


def valtoip(v):
    els = []
    for i in range(4):
        els.append(str(v &amp; 0xFF))
        v &gt;&gt;= 8
    return ".".join(els)


def step(ip, reverse=False):
    v = iptoval(ip)
    if reverse:
        v ^= 0x18482642
        v = (v + 0x78643587) &amp; 0xFFFFFFFF
        v ^= 0x87568289
    else:
        v ^= 0x87568289
        v = (v - 0x78643587) &amp; 0xFFFFFFFF
        v ^= 0x18482642
    return valtoip(v)


def transform(ip, iterations=16, reverse=False):
    for _ in range(iterations):
        ip = step(ip, reverse=reverse)
    return ip


def checksum(pairs, index):
    checksum = 0
    for i, p in enumerate(pairs):
        if i == index:
            continue
        checksum += iptoval(p[1])
    return checksum &amp; 0xFFFFFFFF


def findip(pairs):
    for i, p in enumerate(pairs):
        c = checksum(pairs, i)
        if c == iptoval(p[1]):
            return p[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("ip", nargs="+")
    parser.add_argument("-r", "--reverse", help="reverse transformation",
                        action="store_true")
    parser.add_argument("-c", "--checksum", help="test checksum",
                        action="store_true")
    args = parser.parse_args()

    pairs = []
    for ip_src in args.ip:
        ip_dst = transform(ip_src, reverse=args.reverse)
        pair = (ip_src, ip_dst)
        d = "--&gt;"
        if args.reverse:
            pair = pair[::-1]
            d = "&lt;--"
        pairs.append(pair)
        if not args.checksum:
            print("`{``}` `{``}` `{``}`".format(ip_src, d, ip_dst))

    fmt = "| `{`:4`}` | `{`:15`}` | `{`:15`}` | `{`:10`}` |"
    fmt2 = "| `{`:4`}` | `{`:15`}` | `{`:15`}` | 0x`{`:08X`}` |"
    if args.checksum:
        print(fmt.format("", "IP", "IP'", "value"))
        print(fmt.format(*4 * ["---"]))
        ok_ip = findip(pairs)

        for ip, ipp in pairs:
            if ip == ok_ip:
                continue
            print(fmt2.format("", ip, ipp, iptoval(ipp)))

        for ip, ipp in pairs:
            if ip != ok_ip:
                continue
            print(fmt2.format("x", ip, ipp, iptoval(ipp)))

        if not ok_ip:
            print("No IP matches checksum")
        else:
            print("The IP marked x matches the checksum of remaining IPs, "
                  "it is removed.")
```

例如，`sustainabilityminolta.com`的一个A记录值是`192.202.176.55`。可以得到真正的IP：

```
&gt; python3 transform.py 192.202.176.55
192.202.176.55 --&gt; 192.42.116.41
```

要反转转换，使用`-r`或`--reverse`：

```
&gt; python3 transform.py 192.42.116.41 --reverse
192.42.116.41 &lt;-- 192.202.176.55
```

要检查A资源记录是否满足校验和，添加所有ip为参数并添加`-c`或`——checksum`：

```
&gt; python3 transform.py 127.33.12.14 127.33.12.15 192.202.176.55 126.56.117.50 --checksum
|      | IP              | IP'             | value      |
| ---  | ---             | ---             | ---        |
|      | 127.33.12.14    | 127.0.0.0       | 0x0000007F |
|      | 127.33.12.15    | 127.0.0.1       | 0x0100007F |
|      | 192.202.176.55  | 192.42.116.41   | 0x29742AC0 |
| x    | 126.56.117.50   | 190.43.116.42   | 0x2A742BBE |
The IP marked x matches the checksum of remaining IPs, it is removed.

```

如果IP与校验和匹配，则用x标记它。



## DGArchive

本文中的DGA是由DGArchive项目实现的。

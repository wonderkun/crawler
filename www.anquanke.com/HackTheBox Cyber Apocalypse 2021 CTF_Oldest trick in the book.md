> 原文链接: https://www.anquanke.com//post/id/239757 


# HackTheBox Cyber Apocalypse 2021 CTF：Oldest trick in the book


                                阅读量   
                                **445508**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t010857db12123596ef.png)](https://p0.ssl.qhimg.com/t010857db12123596ef.png)



## 数字取证题目Oldest trick in the book

大家好我是来自Tiger-Team的evi1_f4iry，近期刚刚和小伙伴们组队TigerEyes，完成了为期一周的Cyber Apocalypse 2021 CTF线上赛，队伍最终排名第15。

[![](https://p5.ssl.qhimg.com/t011680aab05059f1ad.png)](https://p5.ssl.qhimg.com/t011680aab05059f1ad.png)<!--[endif]-->

我将陆续在此分享一些我在队伍中负责解出的题目，本文为取证题Oldest trick in the book。

### 题目信息

Oldest trick in the book

实际完成该题目的人数：265

题目线索：

“A data breach has been identified. The invaders have used the oldest trick in the book. Make sure you can identify what got stolen from us.”

一个数据库发生了泄露。入侵者使用了书中最古老的把戏，确保你能辨认出我们被盗的东西是什么。

题目数据包解压后是一个名为“older_rtick.pcap”的流量数据包。

[![](https://p0.ssl.qhimg.com/t012e112c7fd6f56631.png)](https://p0.ssl.qhimg.com/t012e112c7fd6f56631.png)<!--[endif]-->

它较为巨大的容量首先引起了我的注意。通过binwalk检查可发现更多的线索。

[![](https://p3.ssl.qhimg.com/t013faeab0381619391.png)](https://p3.ssl.qhimg.com/t013faeab0381619391.png)<!--[endif]-->

我在这里曾经尝试通过dd分割，但是分割后的zip是不能解压的，提示有data在文件尾部，hexedit修复等方法都无法成功。同时也尝试了将4部分zip作为一个整体分割出来处理，但是除了发现下面这种三个压缩文件头在一起之外并没有更多的收获。

[![](https://p3.ssl.qhimg.com/t01bf6dca970b34670c.png)](https://p3.ssl.qhimg.com/t01bf6dca970b34670c.png)<!--[endif]-->

这三个头复合到一起曾经让我以为这是三个嵌套在一起的压缩包。按这个思路尝试修复同样是无用之功。

错误的尝试足够了。

让我们回归到正途上。

使用wireshark打开流量包。

[![](https://p0.ssl.qhimg.com/t01bbd21fcab74f4fd7.png)](https://p0.ssl.qhimg.com/t01bbd21fcab74f4fd7.png)<!--[endif]-->

打开后由于流量包容量巨大，记录很难逐条查看。

首先我使用了统计功能简单分析一下流量包的分布。

[![](https://p3.ssl.qhimg.com/t0155cd011dde3f0442.png)](https://p3.ssl.qhimg.com/t0155cd011dde3f0442.png)<!--[endif]-->

可以看到TCP包很多，16782，ICMP包20232，tcp包多是正常的，因为常规的通信都是tcp为主，但是ICMP包如此多，就值得怀疑，同时联想到题目有提到“入侵者使用了书中最古老的把戏”，我相信我找到了正确的路线。

过滤查看

[![](https://p1.ssl.qhimg.com/t012695a2ba4590aed0.png)](https://p1.ssl.qhimg.com/t012695a2ba4590aed0.png)<!--[endif]-->

我在icmp过滤后的第一个包中，发现了我在试错过程种曾发现的线索，以三组pk头开始的数据（pk头是压缩文件头）。

简单看了一下各个包的Data部分，应该就是IP:192.168.1.7利用icmp向IP:192.168.1.8传送了压缩文件。

再次修改过滤条件

(icmp) &amp;&amp; (ip.src == 192.168.1.7)

[![](https://p0.ssl.qhimg.com/t01cbab989f98a748d3.png)](https://p0.ssl.qhimg.com/t01cbab989f98a748d3.png)<!--[endif]-->

现在剩下的包可以看到都是发送带有data的包，

同时我注意到data的部分规律：

根据我们已知的压缩文件PK头对应的数据应为“50 4b 03 04“，如果我想按之前试错过程中得到的线索：数据应为压缩包的话，那前16位数据显然不是我需要的数据，

[![](https://p5.ssl.qhimg.com/t0132e797a8f884041a.png)](https://p5.ssl.qhimg.com/t0132e797a8f884041a.png)<!--[endif]-->

同时，我们还可以发现另外一个规律，数据都是重复了三次的。

继续查看其它包也可以在一些含有明文的包中看到同样的规律

[![](https://p5.ssl.qhimg.com/t0109b7a05a9e0ca8a8.png)](https://p5.ssl.qhimg.com/t0109b7a05a9e0ca8a8.png)<!--[endif]-->

[![](https://p3.ssl.qhimg.com/t01494f11c0b5ddb0a7.png)](https://p3.ssl.qhimg.com/t01494f11c0b5ddb0a7.png)<!--[endif]-->

我进行了导出。

这里可以用tshark或者直接用wireshark将过滤好的包导出。然后通过cut处理一下数据，只取16到48位的字符，也就是去除不重复的数据。

Tshark:

tshark -r older_trick.pcap -Y “(icmp) &amp;&amp; (ip.src == 192.168.1.7)” -T fields -e data.data | cut -c 17–48 &gt; data_cut

wireshark的话则是导出json，然后grep data部分同样cut，这里就不再展示。

现在我得到了不重复的数据。

[![](https://p0.ssl.qhimg.com/t0144420575e7e43c04.png)](https://p0.ssl.qhimg.com/t0144420575e7e43c04.png)<!--[endif]-->

现在只需要将数据转成zip。

现有的数据一是存在换行符号，二是数据是hex的，要想转换为文件则需要转为bytes。

写了以下脚本来达到目的。

```
#!/usr/bin/env python3

hex_data = []

with open('data_cut', 'r') as f:

    for data_line in f.readlines():

        hex_data.append(bytes.fromhex(data_line.strip('\n')))

f.close()

#print(hex_data)

 

with open('out.zip', 'wb') as out:

    out.write(b''.join(hex_data))

out.close()
```

执行后得到预期的压缩文件。

[![](https://p4.ssl.qhimg.com/t01b257b2f43019aeb2.png)](https://p4.ssl.qhimg.com/t01b257b2f43019aeb2.png)<!--[endif]-->

解压后得到fini文件夹。

[![](https://p0.ssl.qhimg.com/t01d16be6c78e6afcab.png)](https://p0.ssl.qhimg.com/t01d16be6c78e6afcab.png)<!--[endif]-->

通过观察搜索文件名，以及观察文件的内容，可以发现这是firefox的配置文件夹。

Compatibility.ini中也可以发现这应该是Windows系统下的Firefox的配置文件夹：

[![](https://p0.ssl.qhimg.com/t01443da06ef6f21d43.png)](https://p0.ssl.qhimg.com/t01443da06ef6f21d43.png)<!--[endif]-->

同时，在logins.json文件中我发现了一组加密后的凭据。

[![](https://p4.ssl.qhimg.com/t013c77a16c28cc77a0.png)](https://p4.ssl.qhimg.com/t013c77a16c28cc77a0.png)<!--[endif]-->

Logins.json

```
`{`"nextId":2,"logins":[`{`"id":1,"hostname":"https://rabbitmq.makelarid.es","httpRealm":null,"formSubmitURL":"https://rabbitmq.makelarid.es","usernameField":"username","passwordField":"password","encryptedUsername":"MDIEEPgAAAAAAAAAAAAAAAAAAAEwFAYIKoZIhvcNAwcECMeab8LuajLlBAixWaWDdSvdNg==","encryptedPassword":"MEoEEPgAAAAAAAAAAAAAAAAAAAEwFAYIKoZIhvcNAwcECGKAhjI0M93wBCDzNVgOAQ9Qn77aRp791mOjsyTjoAINAym/9+wmwdI/hQ==","guid":"`{`aed76f86-ae6a-4ef5-b413-be3769875b0f`}`","encType":1,"timeCreated":1618368893810,"timeLastUsed":1618368893810,"timePasswordChanged":1618368893810,"timesUsed":1`}`],"potentiallyVulnerablePasswords":[],"dismissedBreachAlertsByLoginGUID":`{``}`,"version":3`}`
```

Firefox的凭据是可以通过一个工具进行复原的，当然也可以导入到Firefox进行恢复。

[https://github.com/unode/firefox_decrypt](https://github.com/unode/firefox_decrypt)

firefox_decrypt可以用来从主密码保护的配置文件中恢复密码，只要主密码是已知的。如果配置文件不受主密码保护，则在没有提示的情况下显示密码。

将firefox_decrypt.py脚本拷贝进解压得到的fini文件夹，并以当前目录为参数执行。

python3 firefox_decrypt.py `pwd`

直接得到flag

[![](https://p3.ssl.qhimg.com/t01ff4f42b7a9832c6c.png)](https://p3.ssl.qhimg.com/t01ff4f42b7a9832c6c.png)<!--[endif]-->

CHTB`{`long_time_no_s33_icmp`}`

Long time no see icmp… 

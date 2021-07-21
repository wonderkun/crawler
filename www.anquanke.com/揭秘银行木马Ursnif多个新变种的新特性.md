> 原文链接: https://www.anquanke.com//post/id/145495 


# 揭秘银行木马Ursnif多个新变种的新特性


                                阅读量   
                                **91772**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://blogs.forcepoint.com/
                                <br>原文地址：[https://blogs.forcepoint.com/security-labs/many-faces-ursnif-email-hijacking-mailslots-and-insecure-servers?sf88538136=1](https://blogs.forcepoint.com/security-labs/many-faces-ursnif-email-hijacking-mailslots-and-insecure-servers?sf88538136=1)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01f08e96c932c76dd3.png)](https://p4.ssl.qhimg.com/t01f08e96c932c76dd3.png)

## 概述

自从大约两年前，恶意软件Ursnif/Gozi源代码泄露以来，已经发现有多起恶意软件活动都使用了Ursnif或其变种（例如GozNym）进行投递。<br>
针对银行的恶意软件往往能获得比较高额的非法收益，因此会有许多网络犯罪分子在原始代码的基础上，对其进行修改，从而发起自己的恶意软件活动。我们此前已经讨论过一些早期的活动，但在过去的几周时间内，我们发现了一个原始Ursnif代码库的新分支，并持续对其进行研究。目前，这一恶意活动主要针对英国和意大利。<br>
此前我们的研究成果，请参考下面两篇文章：<br>[https://blogs.forcepoint.com/security-labs/range-technique-permits-ursnif-jump-your-machine](https://blogs.forcepoint.com/security-labs/range-technique-permits-ursnif-jump-your-machine)<br>[https://blogs.forcepoint.com/security-labs/ursnif-variant-found-using-mouse-movement-decryption-and-evasion](https://blogs.forcepoint.com/security-labs/ursnif-variant-found-using-mouse-movement-decryption-and-evasion)



## 恶意软件的分发

在过去的恶意软件活动中，通常都依赖于发送恶意电子邮件来实现恶意软件的分发。在恶意电子邮件中，会包含一系列类型的附件，当附件被执行后，会从远程位置下载主要的Ursnif Payload。然而，自2017年年底以来（ [https://blog.talosintelligence.com/2018/03/gozi-isfb-remains-active-in-2018.html](https://blog.talosintelligence.com/2018/03/gozi-isfb-remains-active-in-2018.html) ），一些攻击者似乎采取了混合的方式，以类似于商业电子邮件欺骗（BEC）的方式来获取目标信任，从而“劫持”到正常的电子邮件往来。<br>
攻击者在进行商业电子邮件欺骗时，往往会将目标锁定在经常有电子汇款和外部供应商合作的企业。攻击者通常会在目标企业的员工电脑上部署键盘记录器，或者针对目标企业的员工开展网络钓鱼攻击，从而获取到登录凭据。一旦获得登录凭据，攻击者就可以远程登录到该企业的电子邮件账户中，并监视目标企业内部的通信情况。如果发现该企业与其他一家供应商之间即将发生财务转移时，就会对电子邮件通信进行“劫持”，攻击者会利用一个内部邮箱或可信的发件人，向对方发送一个伪造的发票。<br>
值得注意的是，由于攻击者已经监听了此前的邮件往来内容，所以这封“提供发票”的邮件可能会在正文中附带上此前两方邮件沟通的内容，目的在于为了欺骗收件人，让他点击这个伪造的发票，从而感染恶意软件。<br>
在我们观察到的Ursnif活动中，被“劫持”的电子邮件不一定都和财务有关，但通常都涉及到企业与客户或供应商之间的通信。在回复的邮件中，包含完整的此前沟通内容，以及精确伪造后的邮件签名。<br>
电子邮件的正文通常是一个简短的说明，例如“请查看附件”，用于引导收件人打开附件。<br>
在我们此前记录的一个案例中，所使用的电子邮箱被监视长达7年，这意味着攻击者可能使用了一种新型但是仍有缺陷的全自动或半自动方式，来实现对目标邮箱的邮件往来监听。

### <a class="reference-link" name="Payload"></a>Payload

在这些邮件中，附件包含的内容并不是电子发票，而是一个Microsoft Word OLE文档。在某些恶意活动中（但并非全部），该Word文档的还会使用能迷惑收件人的文件名称。<br>
在文档中，包含一个或多个经过混淆后的宏，并显示一个嵌入式图像，试图诱导用户在Word默认禁用宏的情况下手动启用宏。在当前的恶意活动中，这些嵌入式图像中的文字，会根据收件人所在的地区进行翻译，以确保本地化。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blogs.forcepoint.com/sites/default/files/u1121/201805_ursnif_wordenableprompt.png)<br>
对于一些不具有安全意识，在默认情况下启用宏的用户，该文档中的宏会立即执行，并从特定的下载服务器中下载另一个文件。<br>
在该恶意软件最近的版本中，采取了两种不同的方式。一种是直接下载恶意可执行文件，另一种是首先下载一个经过混淆后的较小的JavaScript/PowerShell脚本，再通过该脚本下载最终Payload。尽管这些Payload的扩展名是 “.class”或“.yarn”，但它们实际上是包含Ursnif的可移植可执行（PE）文件。<br>
下载请求通常类似于如下格式。<br>
直接下载：

```
请求1 - hxxp://qwqw1e4qwe14we[.]com/KOM/testv.php?l=boun4.yarn
```

通过JS/PS间接下载：

```
请求1 - hxxp://qwundqwjnd[.]net/cachedmajsoea/index.php?e=kuuud
请求2 - hxxp://qwundqwjnd[.]net/lipomargara/kuuud.yarn
```

### <a class="reference-link" name="%E5%88%86%E5%8F%91%E6%9C%8D%E5%8A%A1%E5%99%A8"></a>分发服务器

在我们的调查过程中，观察到每天都有多个分发域名被注册（新增）和被关闭。<br>
这些服务器似乎会追踪自身的感染统计信息，由testv.php中的代码负责维护，并作为下载过程的一部分。这些统计信息可以通过查看stats.php页面获得，该页面会显示存储在服务器上的JSON文件（lex_192h.json）中记录的数据。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blogs.forcepoint.com/sites/default/files/u1121/201805_ursnif_testv.png)<br>
有趣的是，这些分发服务器似乎并不是特别关注OPSEC方面：JSON文件通常会包含文件名的统计信息，但对这些文件名的收集是以前的活动中所需的，目前已经不再需要。<br>
类似的一个疏忽是，偶尔在打开的目录中会出现名为“crypt_xxxx_yyyy[a-z].exe”的文件，这些文件指向该活动中特有的某些僵尸网络，其中“yyyy”表示存储在Ursnif内部配置数据中的僵尸网络ID。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blogs.forcepoint.com/sites/default/files/u1121/201805_ursnif_directorylisting.png)



## 新旧结合的Ursnif代码

经过我们的统计，发现这些恶意活动的发起者有一部分人会避免修改Ursnif的核心代码，另一部分人会根据自身的能力对其进行修改。统计数据可以发送到Ursnif主C&amp;C服务器，但前提是需要正确理解其通信代码，这种并行的通信方法说明，这些恶意活动的组织者与代码维护者不是同一个人（组织）。<br>
尽管如此，作为该活动的一部分，Ursnif的代码仍然与此前存在一些变化：Ursnif下载的“.class”或“.yarn”文件与过去看到的其他“loader + DLL”解决方案不同，由此证明在该恶意活动中，修改了恶意文件的包装方式。<br>
我们收集到的所有样本都具有相同的时间戳，时间戳显示为2018年4月17日，同时所有的样本都经过加壳（ [https://blogs.forcepoint.com/security-labs/part-one-security-performance-obfuscation-compression](https://blogs.forcepoint.com/security-labs/part-one-security-performance-obfuscation-compression) ）。在加壳之后，文件大小从约700KB到2MB不等。在运行时，可执行文件会将原始Payload解压缩到内存之中，覆盖加壳代码本身，并将执行传递到下一层。在这个阶段，还有一段代码负责创建两个新线程，二者都使用到了邮槽（Mailslot）以进行通信。

### <a class="reference-link" name="%E9%82%AE%E6%A7%BD%EF%BC%88Mailslot%EF%BC%89"></a>邮槽（Mailslot）

邮槽是一个进程间通信（IPC）协议，该协议已经在Windows发行版本中存在了十多年。其在Ursnif环境下的目的非常简单，一个线程从内存中读取嵌入的数据，将其解压缩，并将结果写入到“.mailslotmsl0”中。另一个线程负责通过邮槽的方式从中取出数据。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blogs.forcepoint.com/sites/default/files/u1121/201805_ursnif_mailslot.png)<br>
在这里，之所以使用邮槽的通信方式是为了阻止研究人员对恶意软件的分析。此前曾发现过有恶意软件使用了“鼠标移动跟踪”技术（ [https://blogs.forcepoint.com/security-labs/ursnif-variant-found-using-mouse-movement-decryption-and-evasion](https://blogs.forcepoint.com/security-labs/ursnif-variant-found-using-mouse-movement-decryption-and-evasion) ），其目的也同样是为了阻碍研究人员的分析。<br>
我们从邮槽中提取到数据，最终执行流会传递到一个DLL（crm.dll）上。crm.dll的主要功能是解压数据，并加载其最终阶段的DLL文件client.dll。这是执行链中的最后一步，在client.dll中包含Ursnif代码的主体及其配置数据，例如C&amp;C地址、僵尸网络ID、超时等待时间等。



## 防护措施

在不同的攻击阶段，用户可以采取不同的方式免受此威胁的侵害：<br>
第二阶段（诱导用户）：甄别与攻击相关的恶意邮件，避免打开这些邮件。<br>
第五阶段（投放文件）：避免下载来历不明的附件，从而防止恶意文件被下载到电脑。<br>
第六阶段（与命令和控制服务器通信）：阻断恶意软件与C&amp;C服务器的通信。



## 总结

将新样本与此前发现的Ursnif变种进行比较，我们会发现其工作方式有一些显著的不同。例如，新样本没有使用TLS回调、引入了邮槽机制。这些都是基于原始代码所做出的改进。<br>
在2018年5月中旬，我们似乎捕获到了一个新的变种，该变种支持“TLS回调”。由此似乎可以看出，有技术水平不同的多个网络犯罪组织正在试图改进原始代码。其中，不乏会有一少部分人有能力修改核心代码，而其他大多数人只会修改自定义的分发代码，并保持恶意软件的核心代码不变。<br>
因此，目前存在大量Ursnif/Gozi的变种，但其目的仍然是一致的——窃取用户凭据和与银行相关的信息。<br>
我们需要提醒广大用户，在收到电子邮件后，要谨慎打开附件。如果遇到了任何建议修改Word安全设置的文档，应保持警惕，避免按照文档中的要求进行修改。此外，在收到不同寻常的邮件时，应该注意发件人来源。



## IoC

### <a class="reference-link" name="SHA1"></a>SHA1

```
018f88acc9591f0ca3fcfec9297297173c5b0232
0b0dab27ca660ba528a29de5bdf5a9af603a6e1a
185dba0cfdbf512fbf64ab41c0771f2784032a8a
1ffb6a64b703a2c40859b76a2335c724e5763806
220c38a509a2f0e62b279ad4f140e0aed79f2816
2540a48d0587ce4a9b6859282ec2993dc5fea95b
3787934bf18909a2f17eaf916a4ef38d94035ebf
3f772913f9fe8a1c448efba4412ac17ba66f5e94
3fb7059f1e10fef0052427b6324c2eab67140381
40f1ac132672b3b2006b2852e7b2bbaf5cff43ac
45fb72f34b8b018d9dc5730e22e9850951395c59
482ce27840693991d5bf7b8ee2d298aeb4f8db66
4b431fade4c87ac138923c59cba920e1219ab419
4f8a4b73e7537ec1d9ad5124c3d09235b6573a94
619af677b3754888296c1def52517eeeeb31058a
74ab56a3997606933795f6377c2f86df99d51810
79dde9c7e0cceee8e5d9626819e2c33f9cce0425
8be96462a9a47bb95e5bc9ab61315e38feda26b9
8c274f0b095f9533212d0171001d47e71919ddb2
8fde99d9727e7c431fd19ce68cff44835e33e43b
962905f9fba3aee435d12268d00dc6ff7cca14f9
9da4bb1b1c6730231924047266624ba439ad9d91
9def879bb4c602f9945cec3b554ce34b0708638d
acc225210a206b81e4b4e8669affbc21407a53fb
b061889548e9c23b02dcab0910952d686b58026f
b51f9dd4735d841e4c787be717a383eb2b2d979b
b7d8a0b1da3dde8dec1f121e9eceefbde02f2631
c5fe4bc083ae504b37277e5090a1413fe1afddc6
cf24b05895101663a1d7b0d4f671918c2d8e60ae
d69c31c87a10c940ca928aaf484b258c64e4c866
d8f028d06027718ff4d5d18a22d225e9bbd2fe0a
dfdbe5b5b5fdd28226771c95b0cf8f44f4710031
e24e85eb34ea9cb3b7ed7057e566d342a3b9b69c
e9e6821cf4ec1d55bc78de93fc0fe1b8a0f8c59e
edb7fe4cc6f05f5ae9ff6c3d1c7e8e237c6c679a
ee0620b09b374a49a10859d6877c45d988730498
eef49be4569f68de71c968fc38d7cfe5b5ac0eab
f64e25db4f2cfec731d40f7a5547b2b8e48cf9e3
f90e096dfe0a07d55ab9691c6db70faac924580e
```

### <a class="reference-link" name="URL"></a>URL

```
hxxp://14ca1s5asc45[.]com
hxxp://9qwe8q9w7asqw[.]com
hxxp://asd5qwdqwe4qwe[.]com
hxxp://d4q9d4qw9d4qw9d[.]com
hxxp://dq9wq1wdq9wd1[.]com
hxxp://dqowndqwnd[.]net
hxxp://eq9we1qw1qw8[.]com
hxxp://fqw4q8w4d1qw8[.]com
hxxp://g98d4qwd4asd[.]com
hxxp://gtqw5dgqw84[.]com
hxxp://hhhasdnqwesdasd[.]com
hxxp://hhjfffjsahsdbqwe[.]com
hxxp://jjasdkeqnqweqwe[.]com
hxxp://kkjkajsdjasdqwec[.]com
hxxp://kkmmnnbbjasdhe[.]com
hxxp://mmmnasdjhqweqwe[.]com
hxxp://oiwerdnferqrwe[.]com
hxxp://ooaisdjqiweqwe[.]com
hxxp://oooiasndqjwenda[.]com
hxxp://oooiawneqweasd[.]com
hxxp://oqk4123613123[.]net
hxxp://oyiyuarogonase[.]net
hxxp://popopoqweneqw[.]com
hxxp://ppoadajsqwenqw[.]com
hxxp://ppoasdqnwesad[.]com
hxxp://pqwoeasodiqwejes232[.]com
hxxp://q5q1wdq41dqwd[.]com
hxxp://qiwjesijdqweqs[.]com
hxxp://qw6e54qwe54wq[.]com
hxxp://qw8e78qw7e[.]com
hxxp://qwd1q6w1dq6wd1[.]com
hxxp://qwd1qw8d4q1wd[.]com
hxxp://qwdohqwnduasndwjd212[.]com
hxxp://qwe1q9we1qwe51[.]com
hxxp://qwekasdqw8412[.]net
hxxp://qweoiqwndqw[.]net
hxxp://qwojdaisd1231[.]net
hxxp://qwqw1e4qwe14we[.]com
hxxp://qwqweqw4e1qwe[.]com
hxxp://qwundqwjnd[.]net
hxxp://r9qweq19w1dq[.]com
hxxp://rqw1qwr8qwr[.]com
hxxp://rrrradkqwdojnqwd[.]com
hxxp://sdf5wer4wer[.]com
hxxp://sdjqiweqwnesd[.]com
hxxp://t8q79q8wdqw1d[.]com
hxxp://tr8q4qwe41ewe[.]com
hxxp://tttiweqwneasdqwe[.]com
hxxp://uuasdjqwehnasd[.]com
hxxp://uurty87e8rt7rt[.]com
hxxp://uuyyhsdhasdbee[.]com
hxxp://wdojqnwdwd[.]net
hxxp://wdq9d5q18wd[.]com
hxxp://yyjqnwejqnweqweq[.]com
```

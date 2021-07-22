> 原文链接: https://www.anquanke.com//post/id/164157 


# 新型密码窃取木马：AcridRain


                                阅读量   
                                **2752122**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Stormshield，文章来源：stormshield.com
                                <br>原文地址：[https://thisissecurity.stormshield.com/2018/08/28/acridrain-stealer/](https://thisissecurity.stormshield.com/2018/08/28/acridrain-stealer/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/dm/1024_504_/t01e27eb244973e546c.jpg)](https://p3.ssl.qhimg.com/dm/1024_504_/t01e27eb244973e546c.jpg)

本文将介绍一种名为AcridRain的新型密码窃取软件，它在过去的2个月内更新频繁。

## 一、简介

AcridRain是一款用C/C++编写的新型密码窃取软件，最早于2018年7月11日在黑客论坛出现。它可以从多种浏览器窃取凭证，cookies及信用卡信息。除此之外，还有转储Telegram和Steam会话、抢占Filezilla连接等功能。详细介绍见下文：

[![](https://p1.ssl.qhimg.com/t014fbd9f45cf76fc23.png)](https://p1.ssl.qhimg.com/t014fbd9f45cf76fc23.png)

[![](https://p3.ssl.qhimg.com/t015e14d42cdad86fee.png)](https://p3.ssl.qhimg.com/t015e14d42cdad86fee.png)

这款恶意软件团队由2名销售人员和1名开发人员组成：
<td valign="top">Actor</td><td valign="top">Job</td><td valign="top">Known Telegram ID</td>

Job
<td valign="top">PERL</td><td valign="top">seller</td><td valign="top">@killanigga, @Doddy_Gatz</td>

seller
<td valign="top">2zk0db1</td><td valign="top">seller</td><td valign="top">@dsl264</td>

seller
<td valign="top">Skrom</td><td valign="top">developer</td><td valign="top">@SkromProject, @KillM1</td>

developer

## 二、技术细节：

本节将重点介绍我们捕获的第一个[AcridRain样本](https://www.hybrid-analysis.com/sample/7b045eec693e5598b0bb83d21931e9259c8e4825c24ac3d052254e4925738b43/5b4a05907ca3e11472406373%EF%BC%897b045eec693e5598b0bb83d21931e9259c8e4825c24ac3d052254e4925738b43)

快速浏览二进制代码，我们发现它没有被封装或拆分。有一些可用的调试信息，如PDB路径：c:\users\igor1\source\repos\stealer ar\release\stealer ar.pdb（ar为AcridRain简写），还有一些其他的字符串来帮助我们进行逆向分析。

### 初始化

在窃取设备中的数据之前，AcridRain需要对自身进行配置，以便正常运行。首先，它会检索环境变量：
- Temporary path
- Program files path
- Etc
完成后，它会继续通过检测注册表值来获取程序路径。像Steam路径，Telegram可执行文件中图标的名称和资源索引的完整路径(用于获取二进制路径)。

[![](https://p0.ssl.qhimg.com/t01455a3e6275121e6e.png)](https://p0.ssl.qhimg.com/t01455a3e6275121e6e.png)

在这之后，将生成Telegram的会话字符串，然后检测是否生成成功（如下图）

[![](https://p3.ssl.qhimg.com/t016fc9172c05deec3a.png)](https://p3.ssl.qhimg.com/t016fc9172c05deec3a.png)

最后，恶意软件通过创建一个包含所有被窃取数据的ZIP来完成初始化。这个ZIP在临时文件夹中创建并含有时间戳信息，例如：C:\Users\[UserName]\AppData\Local\Temp\2018-08-20 23-10-42.zip (代码如下图)

[![](https://p3.ssl.qhimg.com/t01dcc3ddd4f9e3a505.png)](https://p3.ssl.qhimg.com/t01dcc3ddd4f9e3a505.png)



### Google Chrome引擎

恶意软件最先窃取来自Chrome浏览器的凭证，cookies及信用卡信息（如下图），AcridRain将以下浏览器作为目标：Amigo, Google Chrome, Vivaldi, Yandex browser, Kometa, Orbitum, Comodo, Torch, Opera, MailRu, Nichrome, Chromium, Epic Privacy browser, Sputnik, CocCoc, and Maxthon5.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bbcd633d09e51584.png)

在分析中，一些特殊的字符串让我们找到了凭证如何被窃取并加密的原因。在下图中，我们可以看到恶意软件作者使用了一个名为browser-dumpwd-master的项目。Google这个目录名字，我们找到了放在GitHub上的POC([https://github.com/wekillpeople/browser-dumpwd](https://github.com/wekillpeople/browser-dumpwd))，里面介绍了如何窃取Chrome和Firefox的证书。然而，这个项目中并没有miniz.h或zip.c，我们将在后面看到它们从何而来。不出所料，作者借鉴了POC代码，来实现Chrome / Firefox凭证的窃取。

[![](https://p4.ssl.qhimg.com/t0110051520c12586b4.png)](https://p4.ssl.qhimg.com/t0110051520c12586b4.png)

### 窃取Chrome凭证

窃取证书非常简单。根据DumpChromeCreds (0x4017F0)的给定输入，恶意软件根据用户数据选择合适的目录。例如，如果输入0x1，那么恶意软件将使用目录  C：\ Users \ [USER] \ AppData \ Local \ Google \ Chrome \ User Data \ Default，如果是0x3，则它将是  C：\ Users \ [USER] \ AppData \ Local \ Yandex \ YandexBrowser \ User Data \ Default等。每个浏览器的值如下所示：

[![](https://p5.ssl.qhimg.com/t01cd6a91fb5fb1997d.png)](https://p5.ssl.qhimg.com/t01cd6a91fb5fb1997d.png)

为了确定哪个凭据来自哪个浏览器，恶意软件设置了特殊的头，这些头和凭据被放在临时文件夹%TEMP%的result.txt内。一旦选择了浏览器，头就会入结果文件中（如下图）。

[![](https://p3.ssl.qhimg.com/t01fd542f9f91ef7fb9.png)](https://p3.ssl.qhimg.com/t01fd542f9f91ef7fb9.png)

创建完头之后，恶意软件调用dump_chromesql_pass (0x401BC0)来dump所有凭据。它将SQLite数据库登录数据的副本复制到之前选择的用户数据目录中的templogin中，以避免锁定数据库。然后，它打开数据库并使用SQLite进行请求（代码如下图）。

[![](https://p4.ssl.qhimg.com/t010ae0e1da463fc275.png)](https://p4.ssl.qhimg.com/t010ae0e1da463fc275.png)

在上图中我们可以看到，sqlite3_exec通过回调来dump凭据。chrome_worker 函数（0x401400）用于从登录表中检索特定信息。恶意软件将保护origin_url，username_value和password_value字段的信息。密码使用CryptProtectData进行加密，因此要获取纯文本，需要使用CryptUnprotectData函数。若所有信息都窃取完成，会将其保存到文件中（如下图）

[![](https://p0.ssl.qhimg.com/t01decf3e9c4d60bf5f.png)](https://p0.ssl.qhimg.com/t01decf3e9c4d60bf5f.png)

窃取完所有浏览器的证书后，恶意软件将dump cookies信息。

### 窃取Chrome cookies

Dump cookies由函数DumpChromeCookies (0x402D10)实现，在browser-dumpwd项目中没有窃取cookies的功能，所以作者借鉴了凭据窃取函数，对其进行修改，来窃取cookie。窃取的信息放在result_cookies.txt。和凭据窃取函数一样，也有头信息，但是，正如我们在下图中看到的那样，一些头发生了变化。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011aa7813eae4bb0d8.png)

函数dump_chromesql_cookies（0x403300）将创建 名为  templogim（sic）的SQLite Cookies副本。然后发出以下SQL请求：  SELECT host_key，name，path，last_access_utc，encrypted_value FROM cookies; 。这个SQL查询使用回调chrome_cookies_worker（0x401E00，如下图）

[![](https://p2.ssl.qhimg.com/t01ce6991e32018bb2e.png)](https://p2.ssl.qhimg.com/t01ce6991e32018bb2e.png)

然后，与凭据窃取功能一样，cookie将使用CryptUnprotectedData 解密encrpted_value列，并以Netscape格式将所有内容保存在result_cookies.txt中（如下图）。

[![](https://p5.ssl.qhimg.com/t01b5f6dbb1d4a41e0b.png)](https://p5.ssl.qhimg.com/t01b5f6dbb1d4a41e0b.png)

### 窃取Chrome信用卡信息

用于dump信用卡信息的是函数DumpChromeCreditsCards (0x402970)。和盗取cookie一样，dump信用卡信息也是对凭据窃取函数进行借鉴后再进行小的修改。盗取的信息保存在result_CC.txt中（也是在%TEMP%目录）。通过头可以识别是从哪个浏览器窃取的信息。写入头信息后，恶意软件将调用dump_chromesql_cc (0x4031D0)，为Web数据创建一个名为templogik（sic）的副本，加载进入数据库后，将执行以下查询：

```
SELECT credit_cards.name_on_card,

credit_cards.expiration_month,

credit_cards.expiration_year,

credit_cards.card_number_encrypted,

credit_cards.billing_address_id,

autofill_profile_emails.email,

autofill_profile_phones.number,

autofill_profile_names.first_name,

autofill_profile_names.middle_name,

autofill_profile_names.last_name,

autofill_profile_names.full_name,

autofill_profiles.company_name,

autofill_profiles.street_address,

autofill_profiles.dependent_locality,

autofill_profiles.city,

autofill_profiles.state,

autofill_profiles.zipcode

FROM   autofill_profile_emails,

autofill_profile_phones,

autofill_profiles,

autofill_profile_names,

credit_ cards
```

对信用卡信息进行回调的函数是chrome_credit_cards_worker（0x402080）。一旦获取到数据，就会对信用卡号进行解密，并将信息保存在result_CC.txt中，如下图：

[![](https://p2.ssl.qhimg.com/t0176c53e1a13629543.png)](https://p2.ssl.qhimg.com/t0176c53e1a13629543.png)

### Firefox引擎

窃取Firefox凭据的函数DumpFirefoxCreds (0x403600)是对browser-dumpwd项目POC代码借鉴后再进行轻微修改得到的。恶意软件首先会从C2服务器下载额外的库文件，这些DLL来自Mozilla，用来解密Firefox中的凭据信息。作者用libcurl 7.49.1来连接服务器，所请求库文件放在C2服务器的根目录下，是一个名为Libs.zip的ZIP压缩包。下载后将位于%TEMP%目录，并更名为32.zip（如下图）

[![](https://p1.ssl.qhimg.com/t01f139aba2bf6638da.png)](https://p1.ssl.qhimg.com/t01f139aba2bf6638da.png)

这些文件使用[https://github.com/kuba–/zip](https://github.com/kuba%E2%80%93/zip)提到的zip库来提取。在这个项目里我们可以找到之前字符串标签里缺失的2个文件（miniz.h, and zip.c）。包含5个DLL文件，分别为freebl3.dll, mozglue.dll, nss3.dll, nssdbm3.dll, and softokn3.dll.

### 窃取Firefox凭证

AcridRain窃取的Firefox凭证和Chrome凭证一样，都保存在result.txt中。正如预期的那样，过程是一样的。首先将头写入与目标浏览器相关联的报表文件。然后窃取凭证（如下图）。目标浏览器包括Firefox，Waterfox，Pale Moon，Cyber​​fox，Black Hawk和K-Meleon。

[![](https://p3.ssl.qhimg.com/t01f8bd38c300685284.png)](https://p3.ssl.qhimg.com/t01f8bd38c300685284.png)

首先dump_firefox_passwords (0x403E60)函数会从nss3.dll下载所需的函数。这些函数为NSS_Init, NSS_Shutdown, PL_ArenaFinish, PR_Cleanup, PK11_GetInternalKeySlot, PK11_FreeSlot, and PK11SDR_Decrypt（如下图）

[![](https://p5.ssl.qhimg.com/t010199ad41dac27fe7.png)](https://p5.ssl.qhimg.com/t010199ad41dac27fe7.png)

加载函数后，AcridRain将检索Profile0的路径。为此，它会读取％APPDATA％中相应浏览器的profile.ini，并提取与Profile0关联的文件夹的路径（如下图）。这是由GetFirefoxProfilePath（0x403500）函数完成的。

[![](https://p4.ssl.qhimg.com/t019bf43968781c96a0.png)](https://p4.ssl.qhimg.com/t019bf43968781c96a0.png)

为了获取凭证，恶意软件会查找ogins.json和signons.sqlite这两个文件。这个json文件由browser-dumpwd项目中parson.c里的by decrypt_firefox_json (0x403930)函数进行解析。从json中检索的值为hostname, encryptedUsername和encryptedPassword。   用户名和密码用nss3.dll中的DecryptedString (0x403430)函数进行解密。

[![](https://p2.ssl.qhimg.com/t01b5910d5c8059e2b4.png)](https://p2.ssl.qhimg.com/t01b5910d5c8059e2b4.png)

一旦从json中dump出凭证，就会执行回调firefox_worker (0x404180)中的查询语句SELECT * FROM moz_logins对SQLite 数据库进行查询。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016b283e2813ffa3d3.png)

回调函数和json函数一样，都会对hostname, encryptedUsername, encryptedPassword进行检索，然后dump到result.txt。（如下图）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0136019b296de1e865.png)

不同于Chrome功能模块，恶意软件不会窃取使用Mozilla引擎的浏览器中的Cookie信息或信用卡信息。

### 信息整合

Dump出所有凭证后，恶意软件会将所有txt文件和Telegram会话汇总压缩为ZIP文件。为了实现这个操作，它使用zip_entry_open函数指定zip中文件的名称和位置。例如，zip_entry_open(zip, “result.txt”) 会向根目录下的zip文件添加result.txt，zip_entry_open(zip, “Telegram\D877F783D5DEF8C1”)将在Telegram目录中创建名为D877F783D5DEF8C1的文件。然后使用zip_entry_fwrite函数将指定文件写入ZIP（如下图）

[![](https://p2.ssl.qhimg.com/t013b210ea1d429e4b7.png)](https://p2.ssl.qhimg.com/t013b210ea1d429e4b7.png)

### 窃取STEAM账号

AcridRain窃取Steam会话分为2步，首先会从steam文件夹中dump所有ssfn*文件（如下图）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0155d5bd4f70b1b974.png)

然后检索Config文件夹内的所有文件。

[![](https://p1.ssl.qhimg.com/t014e795d867f1a03c2.png)](https://p1.ssl.qhimg.com/t014e795d867f1a03c2.png)

### 窃取Filezilla凭证

Filezilla是一个知名的FTP客户端。AcridRain的目标不是以保存的凭证，而是最近使用过的凭证。为了dump这些信息，它会保存Filezilla文件夹中recentservers.xml

[![](https://p1.ssl.qhimg.com/t0146ded5a0286758a9.png)](https://p1.ssl.qhimg.com/t0146ded5a0286758a9.png)

### 窃取数字货币

Dump完浏览器凭证后下一步就是窃取数字钱包。改恶意软件支持5种数字货币的窃取，分别为Ethereum, mSIGNA, Electrum, Bitcoin以及Armory。在0x404EEA处定义了这些数字货币的客户端路径，如下图：

[![](https://p1.ssl.qhimg.com/t013134089c28233e8b.png)](https://p1.ssl.qhimg.com/t013134089c28233e8b.png)

这个过程清晰明了，AcridRain对每个客户端文件夹进行迭代查询，寻找诸如*.dat的文件。下面是负责从比特币客户端窃取钱包地址的代码。

[![](https://p1.ssl.qhimg.com/t01f2c31adea23bc80a.png)](https://p1.ssl.qhimg.com/t01f2c31adea23bc80a.png)

对于每个客户端，钱包都保存在ZIP文件内的不同目录中，例如，比特币将放在Bitcoin\wallets\文件夹内，以太坊将放在ethereum,以此类推。

### 桌面

关于窃取信息，最后一步是dump所有文本文件。实际上，AcridRain的最后一步是检索桌面上的所有文本文件。使用的技术与窃取Steam会话或窃取数字钱包相同（如下图）。

[![](https://p1.ssl.qhimg.com/t0145bedcde8f1c98cd.png)](https://p1.ssl.qhimg.com/t0145bedcde8f1c98cd.png)

### 上传

窃取完所有数据后，恶意软件将把结果文件发送到C2服务器， ZIP文件使用带有ID参数的POST请求发送。我认为这个ID用于将文件转发给服务器上的正确用户（详见Panel部分）。用于发送这些信息的代码位于0x405732，如下图：

[![](https://p5.ssl.qhimg.com/t015c98d28b8534df79.png)](https://p5.ssl.qhimg.com/t015c98d28b8534df79.png)

以下是Hybrid-Analysis沙箱生成的上传报告中的HTTP流量。

[![](https://p2.ssl.qhimg.com/t01bc9fa8df263d8fd1.png)](https://p2.ssl.qhimg.com/t01bc9fa8df263d8fd1.png)

### 清理文件

一旦数据发送完毕，恶意软件将删除所有生成文件然后退出，生成文件包括32.zip, result.txt, mozglue.dll, nss3.dll, nssdbm3.dll, softokn3.dll, freebl3.dll, result_cookies.txt, 和result_CC.txt.

[![](https://p3.ssl.qhimg.com/t01329bb08a5cfe82c8.png)](https://p3.ssl.qhimg.com/t01329bb08a5cfe82c8.png)

### 调试日志

关于这个AcridRain样本，在日志中还有一个小彩蛋，我们在dump_firefox_password函数发现了这些：（如下图）。

[![](https://p0.ssl.qhimg.com/t016c1c57f215a67eec.png)](https://p0.ssl.qhimg.com/t016c1c57f215a67eec.png)

可以看到这是英语和斯拉夫语进行了混合。翻译字符串，可以得到：

tut ebanaya oshibka???(тут ебаная ошибка):这里特么的有错???

ili tut???(или тут): 或者这里 ???

ya ee nashol (я её нашол): 我找到它了

如果我们执行恶意软件，并将输入重定向到文件中，可以得到如下的日志：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0191766b30afe1d215.png)



## 2018-07-29更新

在本节中，我们将说明在为期16天的开发过程中所做的更新。文中使用的可执行文件（769df72c4c32e94190403d626bd9e46ce0183d3213ecdf42c2725db9c1ae960b）于2018年7月19日编译，并在[Hybird-Analysis](https://www.hybrid-analysis.com/sample/769df72c4c32e94190403d626bd9e46ce0183d3213ecdf42c2725db9c1ae960b/5b68c23d7ca3e16753128a34)给出分析报告。为了找到两个版本之间的区别，我们使用[YaDiff](https://github.com/DGA-MI-SSI/YaCo)在IDA数据库和Diaphora之间传播标志来比较两个IDB。我们看到的第一个修改是删除调试日志，如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c753e27b1d2fe853.png)

先前以时间戳形式生成的报告名称已针对公共IP地址进行了更改。这是通过请求ipify.org的API  并将响应保存在％TEMP％目录下的body.out中，如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b9033483b11cffe8.png)

恶意软件对Chrome窃取功能进行了修改，现在，它不仅窃取默认配置文件，还改变了存储信息的方式，在之前的版本，所有数据被存储在三个独立的文件夹，分别为凭据，cookies和信用卡。现在它们存储在含有浏览器名称的唯一文本文件中（如Vivaldi.txt，Vivaldi_Cookies.txt和Vivaldi_CC.txt，如下图）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b490e0ea0e9f3f5a.png)

文件名改变，报告ZIP文件中的目录也是如此。现在，有一些名为browser，Cookies和  CC的特定文件夹（如下图）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ae6561aff1533771.png)

作者还更改了Firefox浏览器的头。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e16b4ee818e1dc8b.png)

现在，也会从桌面dump扩展名为* .pfx的文件。这些文件包含Windows服务器使用的公钥和私钥，它们存储在ZIP内的Serticifate（sic）目录中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0180799d8745aaa762.png)

现在，增加了加密货币钱包，AcridRain还支持Doge, Dash, Litecoin和 Monero（如下图）

[![](https://p5.ssl.qhimg.com/t01561a8db6ed57981d.png)](https://p5.ssl.qhimg.com/t01561a8db6ed57981d.png)



## 2018-08-21更新

在本节，我们将说明2018年8月21日编译的样本的更新情况。这个可执行文件（3d28392d2dc1292a95b6d8f394c982844a9da0cdd84101039cf6ca3cf9874c1）并在VirusTotal上可用。这次更新对代码进行了调整，一些bug被修复（比如由于宽字节导致门罗币路径错误）32.zip(从C2下载Mozilla DLL)被重命名为opana.zip，但是，作者忘记在删除代码中更改文件名（如下图）

[![](https://p3.ssl.qhimg.com/t016a992434961f13ec.png)](https://p3.ssl.qhimg.com/t016a992434961f13ec.png)

Firefox代码块中的头信息再次修改，如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0121558f97c2403479.png)

报告文件名换回了初始的命名方式——时间戳.zip。但是开发者忘记在删除代码将一些无用文件进行删除，如result_cookies.txt, result_Cookies.txt及 result_CC.txt，在第二个样本中，它们也是没有用的，如下图：

[![](https://p1.ssl.qhimg.com/t0103c0032d58dab36f.png)](https://p1.ssl.qhimg.com/t0103c0032d58dab36f.png)

最后，作者还更改了CnC服务器地址，现在的IP为141.105.71.82（如下图）

[![](https://p0.ssl.qhimg.com/t013198682d43b569ad.png)](https://p0.ssl.qhimg.com/t013198682d43b569ad.png)



## Web控制面板

要下载已在C2上传的ZIP，有一个可用的Web界面。作者使用的第一个IP是185.219.81.232，其关联域名为akridrain.pro。在2018年8月2日左右，服务器出现故障，但几天后（2018-08-08左右）IP变为 141.105.71.82。如果我们使用浏览器访问该面板，我们将被重定向到登录页面（见下文）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012a14b331d1d7d56b.png)

然后，登录后，您将被重定向到Dashboard。此页面用于下载和删除AcridRain上传的zip文件（见下文）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01065d1b7af001926d.png)

还有一个可以下载个人信息的用户页面。在下图中，我们可以看到恶意软件用来上传ZIP报告文件的ID。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01da8ebf2dae25fccb.png)

在2018年8月26日，面板中添加了两个新字段，IP和快速信息 （尚未工作）。还有一个新按钮可以在仪表板中下载所有ZIP（如下图）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0127155dfdd5802f27.png)



## 结论

AcridRain和市场上所有的密码窃取工具一样，但是，支持的软件列表却非常有限。论坛帖子说这款恶意软件可以处理36个以上的浏览器。但如文中所说，支持的浏览器数量是22，而对于Firefox分支，则没有管理cookie或信用卡的功能。根据文章中的说明，我们确定作者从多个Github仓库中借鉴代码。此外，从代码中出现的错误可以看出开发人员似乎是恶意软件行业中的新手。根据AcridRain线程上的说明，下一个重要步骤将是HVNC（隐藏虚拟网络计算）的实现。



## 附录

### 论坛链接
<td valign="top" width="340">链接</td><td valign="top" width="213">日期</td>

日期
<td valign="top" width="340">https://gerki.pw/threads/acridrain-stealer.3959/</td><td valign="top" width="213">2018年7月11日</td>

2018年7月11日
<td valign="top" width="340">https://lolzteam.net/threads/536715</td><td valign="top" width="213">2018年7月11日</td>

2018年7月11日
<td valign="top" width="340">https://vlmi.su/threads/acridrain-stealer.22237/</td><td valign="top" width="213">2018年7月13日</td>

2018年7月13日
<td valign="top" width="340">https://dark-time.life/threads/27628/</td><td valign="top" width="213">2018年7月20日</td>

2018年7月20日
<td valign="top" width="340">https://darkwebs.ws/threads/65935/</td><td valign="top" width="213">2018年7月21日</td>

2018年7月21日
<td valign="top" width="340">https://dedicatet.com/threads/acridrain-stealer.838/</td><td valign="top" width="213">2018年7月26日</td>

2018年7月26日

### Github：

在这个[仓库](https://github.com/ThisIsSecurity/malware/tree/master/acridrain)上可以找到AcridRain的Yara规则和IDA IDC（分析数据库）  。

### IOC哈希：
<td valign="top" width="485">SHA256</td><td valign="top" width="119">编译时间</td>

编译时间
<td valign="top" width="485">7b045eec693e5598b0bb83d21931e9259c8e4825c24ac3d052254e4925738b43</td><td valign="top" width="119">2018-07-13</td>

2018-07-13
<td valign="top" width="485">769df72c4c32e94190403d626bd9e46ce0183d3213ecdf42c2725db9c1ae960b</td><td valign="top" width="119">2018-07-29</td>

2018-07-29
<td valign="top" width="485">3d28392d2dc1292a95b6d8f394c982844a9da0cdd84101039cf6ca3cf9874c1c</td><td valign="top" width="119">2018-08-21</td>

2018-08-21

### 工作路径：

C:\Users\igor1\source\repos\Stealer AR\Release\Stealer AR.pdb

c:\users\igor1\desktop\browser-dumpwd-master\miniz.h

c:\users\igor1\desktop\browser-dumpwd-master\misc.c

c:\users\igor1\desktop\browser-dumpwd-master\zip.c

### URL：

http://185.219.81.232/Libs.zip

http://141.105.71.82/Libs.zip

http://185.219.81.232/Upload/

http://141.105.71.82/Upload/

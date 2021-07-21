> 原文链接: https://www.anquanke.com//post/id/148688 


# 走近了解，隐私大盗“Bigben”


                                阅读量   
                                **137791**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t015723ca412e681096.jpg)](https://p4.ssl.qhimg.com/t015723ca412e681096.jpg)

## 0x1 背景

近日，360核心安全团队截获到一种隐藏在流氓推广中的隐私大盗，此类病毒有着正常的签名信息，伪装为其他软件压缩包的图标，在进行流氓推广的同时还收集了大量用户隐私数据。在5月欧盟刚刚颁布称为最严的数据保护条例GDPR的情况下，此病毒也算是无视法规，专踩雷区。

为了躲避取证和查杀，此类病毒大量使用了ShellCode和隐蔽加载技术，如果仅仅用作流氓推广，可谓是“高射炮打蚊子，大材小用”，经过安全专家进一步分析发现，该病毒通过各种绕路后，插入浏览器的恶意代码可以轻松获取各种账号和cookie信息，即便是https加密的网站也难逃此劫，严重威胁到用户的隐私安全。

由于该类软件都是通过一个名为“Bigben”的开关来控制恶意行为，因此安全专家将此类家族命名为“Bigben”家族，下面让我们一起走进“Bigben”病毒家族，了解一下病毒具体特征。



## 0x2 特征

“Bigben”病毒家族在文件图标、文件名和文件签名这三个方面有着显著的特征。

1）图标特征

病毒家族自被发现以来，均将自身图标伪装成压缩包文档，如下所示，在XP之后的系统上，应用图标上会有一个管理员运行标志。

[![](https://p2.ssl.qhimg.com/t01621ee0d8e25293f5.png)](https://p2.ssl.qhimg.com/t01621ee0d8e25293f5.png)

图标特征 （WindowsXP后）

2）文件名特征

“Bigben”病毒家族伪装的文件名有两种方式：
- 一种是由小写字母和数字组成的12位的随机名称，如h9duugze1n6a
- 一种是伪装成第三方软件名称，其格式为“【第三方软件名称】_xxx-xxx___”，如sony_vegas_pro_13-32_1da-869___<td valign="top" width="353">伪装名称</td><td valign="top" width="131">伪装名称</td>

伪装名称
<td valign="top" width="353">minecraft_0_12_1_build11_555-a98___.exe</td><td valign="top" width="131">5fmtcyl8ugf7.exe</td>

5fmtcyl8ugf7.exe
<td valign="top" width="353">sommand-sonquer-generals_pirate_297-8f2___.exe</td><td valign="top" width="131">ixlnfyafoirv.exe</td>
<td valign="top" width="353">cheatengine67_246-150___.exe</td><td valign="top" width="131">rzgu8f2qnvw8.exe</td>

rzgu8f2qnvw8.exe

3）签名特征

“Bigben”家族都携带了完整的文件签名信息，其签名均是国外公司签名，其中以“OOO”类有限责任公司和”LLC”类有限责任公司为主，以下为部分使用过的签名名称。
<td valign="top" width="248">常用签名名称</td><td valign="top" width="237">常用签名名称</td>

常用签名名称
<td valign="top" width="248">LADA, OOO</td><td valign="top" width="237">STIRKA, LLC</td>

STIRKA, LLC
<td valign="top" width="248">RODIS-K OOO</td><td valign="top" width="237">Gross LLC</td>
<td valign="top" width="248">MEDIDO OOO</td><td valign="top" width="237">VIK-TORI LLC</td>
<td valign="top" width="248">INTELLEKT, OOO</td><td valign="top" width="237">Sundus, LLC</td>
<td valign="top" width="248">OBUV OOO</td><td valign="top" width="237">LEILA BIS, LLC</td>
<td valign="top" width="248">OOO, INTELLEKT</td><td valign="top" width="237">SOFT EKSPERT LLC</td>
<td valign="top" width="248">OOO, GROK</td><td valign="top" width="237">Dort LLC</td>
<td valign="top" width="248">OOO YULIYA</td><td valign="top" width="237">LYUDMILA LLC</td>
<td valign="top" width="248">OOO. LOGOF</td><td valign="top" width="237">TOV LEILA BIS</td>
<td valign="top" width="248">OOO “Stroy Info Tehno”</td><td valign="top" width="237">TOV “RED TABURET”</td>
<td valign="top" width="248">TOV. PRODUKTY</td><td valign="top" width="237">LLC. PRO-STO</td>
<td valign="top" width="248">TOV, I T S</td><td valign="top" width="237">LLC KOL-TORG</td>
<td valign="top" width="248">TOV. PRO-STO</td><td valign="top" width="237">LLC INDOMEDI</td>
<td valign="top" width="248">KRASTER TOV</td><td valign="top" width="237">LLC, Kol-Torg</td>
<td valign="top" width="248">KROK-AVTO, TOV</td><td valign="top" width="237">LLC LYUDMILA</td>
<td valign="top" width="248">KENDI MASTER, TOV</td><td valign="top" width="237">LLC, Myaso</td>
<td valign="top" width="248">GROSS</td><td valign="top" width="237">FORTUNA PARTNERS, LTD</td>
<td valign="top" width="248">LTD Dba Motors</td><td valign="top" width="237">DBA MOTORS LTD</td>

DBA MOTORS LTD



## 0x3 行为分析

“Bigben”病毒家族的主要恶意行为有流氓推广和窃取用户隐私数据，两种恶意行为都受云端控制，代码逻辑包含各种环境检测和判断，普通沙箱难以检出其恶意行为。

简化的执行流程如下图所示：[![](https://p2.ssl.qhimg.com/t01c6b4106020187674.png)](https://p2.ssl.qhimg.com/t01c6b4106020187674.png)

“Bigben”病毒执行流程

“Bigben”的执行流程主要分为两大部分：预处理部分和恶意操作部分

**1****）预处理部分**

包括释放Shellcode，内存加载模块以及同云端交互三部分：

**释放Shellcode**

“Bigben”在入口代码中混淆了无关代码，来干扰分析，如下图所示。

[![](https://p2.ssl.qhimg.com/t01d682bdc68d30ad64.png)](https://p2.ssl.qhimg.com/t01d682bdc68d30ad64.png)

从模块基地址的偏移0x2055A处读取长度为0x1926的Shellcode，并解密执行。

[![](https://p4.ssl.qhimg.com/t01778dfc21b8a1408e.png)](https://p4.ssl.qhimg.com/t01778dfc21b8a1408e.png)

**Shellcode****内存加载恶意PE**

在Shellcode中，从模块的三个不同位置读取出PE数据，拼接上并解密。

[![](https://p5.ssl.qhimg.com/t01c5ffe195dd2e77dd.png)](https://p5.ssl.qhimg.com/t01c5ffe195dd2e77dd.png)

然后内存加载该恶意模块，该模块是“Bigben”的执行主体。

[![](https://p0.ssl.qhimg.com/t012633fc7a979d889c.png)](https://p0.ssl.qhimg.com/t012633fc7a979d889c.png)

在模块基地址偏移0xE0处写入解密后的远程服务器地址，该地址将被内存加载的PE使用。

[![](https://p4.ssl.qhimg.com/t01aa36576678e2d3ab.png)](https://p4.ssl.qhimg.com/t01aa36576678e2d3ab.png)

“Bigben”除了使用GetTickCount的方式来检测反调试之外，还是用VirtualProtect和异常处理方式来改变程序执行流程，增加分析难度。

[![](https://p0.ssl.qhimg.com/t01782114a3eda253cf.png)](https://p0.ssl.qhimg.com/t01782114a3eda253cf.png)

**云端交互**

“Bigben”与C&amp;C服务器先后进行两次交互，网络数据均采用加密方式。

在第一次网络交互中，Bigben从上述URL中获取的是一个JSON数据，其中包括了浏览器将要打开的推广网址（url），需要搜集的用户信息类型（checks），伪装的下载文件名称（name），解密后的JSON数据如下图。

[![](https://p2.ssl.qhimg.com/t0196ffe597d9edfaa2.png)](https://p2.ssl.qhimg.com/t0196ffe597d9edfaa2.png)

第二次网络交互会将收集的系统信息POST给C&amp;C服务器，其中包含了用户系统的各种信息，如下图。

[![](https://p5.ssl.qhimg.com/t01a64c4ff8682ec668.png)](https://p5.ssl.qhimg.com/t01a64c4ff8682ec668.png)

同时从C&amp;C服务器获得云控数据，用于控制“Bigben”行为，如下图所示。

[![](https://p2.ssl.qhimg.com/t018692af7a49e3d661.png)](https://p2.ssl.qhimg.com/t018692af7a49e3d661.png)

当“Bigben”为1的时候，“Bigben”使用默认浏览器打开第一次网络交互中获得的url（[http://mentalaware.gdn/Readme.txt](http://snap.contentssl.com/f/stats.php)）并自删除。

当“Bigben”为0的时候，“Bigben”才会触发其他恶意操作，伪造下载软件（discord vigilante-1-c5-a26.zip）的界面，该下载界面是“Bigben”自绘的，其实并无网络操作，然后再继续进行软件推广，窃取网站账户信息等恶意操作，如下图。

[![](https://p0.ssl.qhimg.com/t01db90ac942ec837a8.png)](https://p0.ssl.qhimg.com/t01db90ac942ec837a8.png)

**2****） 恶意操作部分**

包括窃取网站Cookie，流氓推广以及锁定浏览器主页。

**窃取网站Cookie**

该恶意模块的主要执行流程如下：

**[![](https://p1.ssl.qhimg.com/t01defb86fe62d3915a.png)](https://p1.ssl.qhimg.com/t01defb86fe62d3915a.png)**

窃取Cookie模块执行流程

通过使用第三方驱动NetFilterSDK来篡改HTTP和HTTPS协议，在网页中注入恶意的JS脚本来达到窃取网站Cookie的目的，此种窃取Cookie的行为是无针对性的，用户浏览过的所有网页都会被注入恶意脚本，效果如下图所示。

[![](https://p0.ssl.qhimg.com/t017e68ad8f5e06ccb3.png)](https://p0.ssl.qhimg.com/t017e68ad8f5e06ccb3.png)

其中插入的JS代码由云端的rules.xml控制。

[![](https://p2.ssl.qhimg.com/t0123ef74e098031baa.png)](https://p2.ssl.qhimg.com/t0123ef74e098031baa.png)

真正的窃取Cookie的恶意脚本隐藏在两次&lt;script&gt;间接调用中，将用户浏览网站的Cookie等信息上传至[http://snap.contentssl.com/f/stats.php](http://snap.contentssl.com/f/stats.php)。

[![](https://p0.ssl.qhimg.com/t010f3eb4e2976b5432.png)](https://p0.ssl.qhimg.com/t010f3eb4e2976b5432.png)

** **

**[![](https://p2.ssl.qhimg.com/t016ada77f2503c7532.png)](https://p2.ssl.qhimg.com/t016ada77f2503c7532.png)**

同时该模块也会添加计划任务，每天该时刻启动自身。

**[![](https://p1.ssl.qhimg.com/t01e1ac2e59cb2152d1.png)](https://p1.ssl.qhimg.com/t01e1ac2e59cb2152d1.png)**

**流氓推广**

**“**Bigben”在获取云控信息后，下载指定的恶意推广包，然后静默安装，同时会复制出多个自身，通过携带不同的参数，分别进行IE主页锁定，篡改默认浏览器设置等，执行完毕之后，会执行自删除，如下所示。

[![](https://p5.ssl.qhimg.com/t01b7b63d8502d3cfde.png)](https://p5.ssl.qhimg.com/t01b7b63d8502d3cfde.png)

[![](https://p3.ssl.qhimg.com/t0173f494e9f0f8ad73.png)](https://p3.ssl.qhimg.com/t0173f494e9f0f8ad73.png)

[![](https://p3.ssl.qhimg.com/t01c74761f4ba205e48.png)](https://p3.ssl.qhimg.com/t01c74761f4ba205e48.png)



**自删除**

“Bigben”在执行完上述恶意操作后，会通过获取文件资源管理器explorer.exe的pid，得到其token，然后使用CreateProcessAsUser的方式，伪造成explorer.exe打开cmd.exe来进行自删除操作。

[![](https://p2.ssl.qhimg.com/t011047cb37a97bb9db.png)](https://p2.ssl.qhimg.com/t011047cb37a97bb9db.png)

## 0x4 相关信息
1. MD5信息<td valign="top" width="256">MD5</td><td valign="top" width="277">MD5</td>

MD5
<td valign="top" width="256">014CAD587EEA1133F37E9A05916E4610</td><td valign="top" width="277">05EDA4CFE7FCFA91F9D08F03F4E3C3B1</td>
<td valign="top" width="256">0E9B255496417326710C14AFB7B35ED3</td><td valign="top" width="277">10DFEF14FACD08DA050E34533A6D8225</td>
<td valign="top" width="256">11139E0B69044FFD463C440F5C7BB71F</td><td valign="top" width="277">15DAE8AAB3FB169BA2D7BE97337AA6A2</td>
<td valign="top" width="256">17D9454EC633168DE6DAD84D941ED1E3</td><td valign="top" width="277">21B123A4A580B7476823BDE1E5BB322E</td>
<td valign="top" width="256">353F0FCE5289B4796928A498284FB15B</td><td valign="top" width="277">38D90F1D20700473D2A4A4CEB5BF7502</td>
<td valign="top" width="256">39CB2170DD2C4F3DA000D464DE539750</td><td valign="top" width="277">3900951EFDE57EC00329D55EA0871AFB</td>
<td valign="top" width="256">3A5A6C18BE16813AF7626D92A30B672D</td><td valign="top" width="277">3DC6B647E187B7A1D5305FD8664643FC</td>

3DC6B647E187B7A1D5305FD8664643FC
<td valign="top" width="256">402721A8CBD6FE09DD5D1302CADFF471</td><td valign="top" width="277">408697668956E57FD10DBB7349AB4EFC</td>

408697668956E57FD10DBB7349AB4EFC
<td valign="top" width="256">4441705847710738DB2245BECA02E225</td><td valign="top" width="277">4697693EC3A4AA50F1EE6882AC759744</td>

4697693EC3A4AA50F1EE6882AC759744
<td valign="top" width="256">47185F85A0F97D03F4E38946B49778C5</td><td valign="top" width="277">582D601875030AFC132EEAB8FBFA52D4</td>

582D601875030AFC132EEAB8FBFA52D4
<td valign="top" width="256">4E13310E25BF4145AD9EDD72EFE754BC</td><td valign="top" width="277">5802856BD203F44614D5E6B4D1805874</td>

5802856BD203F44614D5E6B4D1805874
<td valign="top" width="256">50C218DFCD8F6ABC10AE028B3FE78737</td><td valign="top" width="277">5ACA96D9AEF92D0FF2F85E1C1B8C08B6</td>

5ACA96D9AEF92D0FF2F85E1C1B8C08B6
<td valign="top" width="256">561D329D14BA923882BD9D3D7C7C9972</td><td valign="top" width="277">DD6F8263D7FDF385DC76CFBE1338F3A2</td>

DD6F8263D7FDF385DC76CFBE1338F3A2
<td valign="top" width="256">716FC4910CDA1DA42C60327AAAFA4B80</td><td valign="top" width="277">DF2B371ABC77F08BF81798AF9612B4E6</td>

DF2B371ABC77F08BF81798AF9612B4E6
<td valign="top" width="256">735588F199A86F273A7B3263E9D620F1</td><td valign="top" width="277">F25AA53AF7785C0494253E0F387F7BDF</td>

F25AA53AF7785C0494253E0F387F7BDF
<td valign="top" width="256">C15504CCFBE99664046E9CE6CEC942A2</td><td valign="top" width="277">FD9EFE94B35DDA44355EBAC67D8F0BB9</td>

FD9EFE94B35DDA44355EBAC67D8F0BB9
<td valign="top" width="256">BC25ADECC3C927CEA823BB185D14B607</td><td valign="top" width="277">FFA61FF3BAE5889412A2EC762BF39CBC</td>

FFA61FF3BAE5889412A2EC762BF39CBC
<td valign="top" width="256">A34C6F0B6108C8CF49CAA7E45D6C9328</td><td valign="top" width="277">FF158CEAA4C5BBB834360FAD4B8C5D4E</td>

FF158CEAA4C5BBB834360FAD4B8C5D4E
1. C&amp;C服务器信息<td valign="top" width="256">C&amp;C地址</td><td valign="top" width="311">C&amp;C地址</td>

C&amp;C地址
<td valign="top" width="256">zircfzahvlii.ginanklesquare.ru</td><td valign="top" width="311">0b2.ru</td>
<td valign="top" width="256">g.azmagis.ru</td><td valign="top" width="311">njupire.ru</td>
<td valign="top" width="256">g.embokhay.ru</td><td valign="top" width="311">delightsquad.ru</td>
<td valign="top" width="256">g.misterbush.ru</td><td valign="top" width="311">quicklygood.gdn</td>
<td valign="top" width="256">adblocks.ru</td><td valign="top" width="311">s.kometa-stat.ru</td>
<td valign="top" width="256">kometa-stat.ru</td><td valign="top" width="311">kometa-update.ru</td>
<td valign="top" width="256">cdn.kometa-bin.ru</td><td valign="top" width="311">cdn.kometa-bin.ru</td>
<td valign="top" width="256">tkcdoglnstdpwei.sightlogfight.ru</td><td valign="top" width="311">husbandcandleru-vqw2fylh.stackpathdns.com</td>



## 0x5 专家建议

目前，360全线产品已经在第一时间对“Bigben”家族进行查杀，能够及时保障用户的系统和隐私安全。除此之外，360安全专家还向广大用户给出以下建议：
1. 请开启系统关于显示文件后缀名的选项，来判断文件的真正类型，以免被伪装成文档类的恶意软件欺骗。
1. 请去官网下载相应的软件，减少软件被非法篡改的风险。
1. 请不要轻易对可疑软件放行并添加信任。
1. 如果发现系统出现异常，变得响应卡顿，或被安装莫名的推广软件等，怀疑是否已经中招，请及时使用360安全软件进行全盘扫描检查。


审核人：yiwang   编辑：边边

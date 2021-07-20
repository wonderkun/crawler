> 原文链接: https://www.anquanke.com//post/id/146832 


# 对近期Iron组织的恶意软件分析


                                阅读量   
                                **120497**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://www.intezer.com/
                                <br>原文地址：[https://www.intezer.com/iron-cybercrime-group-under-the-scope-2/](https://www.intezer.com/iron-cybercrime-group-under-the-scope-2/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01bfa8ba96ba941f9a.jpg)](https://p0.ssl.qhimg.com/t01bfa8ba96ba941f9a.jpg)





在2018年4月，在监视公共数据馈送的同时，我们注意到一个有趣且以前未知的使用HackingTeam泄露的RCS源代码的后门。我们发现这个后门是由Iron网络犯罪集团开发的，后者是Iron勒索软件（[Bart Parys最近发现的剥离Maktub勒索软件](https://bartblaze.blogspot.co.il/2018/04/maktub-ransomware-possibly-rebranded-as.html)）的幕后团队，我们相信这在过去的18个月里一直活跃。<br>
在过去一年半的时间里，Iron集团为Windows，Linux和Android平台开发了多种类型的恶意软件（后门，加密矿工和勒索软件）。他们利用他们的恶意软件成功感染了至少数千名受害者。<br>
在这篇技术博客文章中，我们将看看研究期间发现的恶意软件样本。



## 安装

[![](https://p3.ssl.qhimg.com/t01e3d42ec6b646f930.png)](https://p3.ssl.qhimg.com/t01e3d42ec6b646f930.png)<br>
**此安装程序样本（以及大多数找到的样本）受VMProtect保护，然后使用UPX进行压缩。



### <a class="reference-link" name="%E5%AE%89%E8%A3%85%E8%BF%87%E7%A8%8B%EF%BC%9A"></a>安装过程

1.检查二进制文件是否在虚拟机上执行，如果是的话 – ExitProcess<br>
2.删除并安装恶意Chrome浏览器扩展程序<br>
％localappdata％ Temp chrome.crx<br>
3.将恶意Chrome扩展程序解压缩到％localappdata％ Temp chrome并创建执行％localappdata％ Temp chrome sec.vbs的计划任务。<br>
4.使用CPU的版本创建互斥，以确保其本身不存在任何正在运行的实例。<br>
5.将后门DLL删除到％localappdata％ Temp &lt;random&gt; .dat。<br>
6.检查操作系统版本：<br>
。如果版本== Windows XP然后只调用’启动’导出Iron Backdoor进行一次性非永久执行。<br>
。如果版本&gt; Windows XP –<br>
调用’启动’导出<br>
检查是否Qhioo360 – 如果不存在，则安装用于以root CA身份标记Iron Backdoor二进制文件的恶意证书。然后创建一个名为’helpsvc’的服务，指向Iron Backdoor dll。<br>[![](https://p0.ssl.qhimg.com/t015f4f44f617109052.png)](https://p0.ssl.qhimg.com/t015f4f44f617109052.png)

## 

## 使用泄露的HackingTeam源代码

一旦我们[分析了](https://analyze.intezer.com/#/)后门样本，我们立即发现它部分基于HackingTeam的[远程控制系统](https://en.wikipedia.org/wiki/Hacking_Team)黑客工具的源代码，该工具大约在[3年前泄露](https://thehackernews.com/2015/07/Italian-hacking-team-software.html)。进一步的分析表明，Iron网络犯罪集团在IronStealer和Iron勒索软件中使用了HackingTeam的两个主要功能。<br>**1. Anti-VM**： Iron Backdoor使用直接从HackingTeam的“Soldier”植入漏洞源代码获取的虚拟机检测代码。这段代码支持检测Cuckoo Sandbox，VMWare产品和Oracle的VirtualBox。截图：<br>[![](https://p2.ssl.qhimg.com/t01228d093659945cbb.png)](https://p2.ssl.qhimg.com/t01228d093659945cbb.png)

**2. 动态函数调用**： Iron Backdoor还使用HackingTeam的“核心”库中的[DynamicCall](https://thehackernews.com/2015/07/Italian-hacking-team-software.html)模块。此模块用于通过混淆函数名称动态调用外部库函数，这使得此恶意软件的静态分析更为复杂。<br>
在以下屏幕截图中，您可以看到代表“ kernel32.dll ”和“ CreateFileMappingA ”API的混淆的“ LFSOFM43 / EMM ”和“ DsfbufGjmfNbqqjoh B” 。<br>[![](https://p1.ssl.qhimg.com/t012286c2f7abe4c42e.png)](https://p1.ssl.qhimg.com/t012286c2f7abe4c42e.png)<br>
有关混淆API的完整列表，您可以访问obfuscated_calls.h

**恶意Chrome扩展程序：**<br>
流行的[Adblock Plus chrome](https://chrome.google.com/webstore/detail/adblock-plus/cfhdojbkjhnklbpkdaibdccddilifddb)扩展的补丁版本用于注入浏览器内的加密挖掘模块（[基于CryptoNoter](https://github.com/cryptonoter)）和浏览器内付款劫持模块。<br>[![](https://p4.ssl.qhimg.com/t01232f5b1cfb57ca95.png)](https://p4.ssl.qhimg.com/t01232f5b1cfb57ca95.png)<br>
修补程序include.preload.js从攻击者的Pastebin帐户注入两个恶意脚本。<br>
恶意扩展不仅在用户打开浏览器时加载，而且还在后台不断运行，充当隐形主机的加密矿工。恶意软件会设置一个计划任务，检查chrome是否每分钟都在运行，如果没有，它会“静默 – 启动”它，如下图所示：<br>[![](https://p3.ssl.qhimg.com/t0167a184d6924f1307.png)](https://p3.ssl.qhimg.com/t0167a184d6924f1307.png)<br>**Internet Explorer（不建议使用）：**<br>
Iron Backdoor本身嵌入了[adblockplusie](https://github.com/adblockplus/adblockplusie) – 用于IE的Adblock Plus，它以类似恶意Chrome扩展的方式修改，注入了远程javascript。看起来这个功能不再被自动使用，原因不明。<br>[![](https://p4.ssl.qhimg.com/t01139f8b793a0a28b6.png)](https://p4.ssl.qhimg.com/t01139f8b793a0a28b6.png)

**持久性后门：**<br>
在将自己安装为Windows服务之前，通过阅读以下注册表项，恶意软件会检查360 Safe Guard或360 Internet Security的存在情况：<br>
。系统 CURRENTCONTROLSET SERVICES zhudongfangyu。<br>
。系统 CURRENTCONTROLSET SERVICES 360rp<br>
如果安装了其中一种产品，恶意软件将只运行一次，而不会持续存在。否则，恶意软件将继续在受害者的工作站上安装rouge，硬编码的根CA证书。这个假根CA据称签署了恶意软件的二进制文件，这将使它们看起来合法。<br>
戏剧性的是：[该证书受密码“ caonima123”保护，这意味着用普通话“操你妈”。](https://www.urbandictionary.com/define.php?term=Cao%20ni%20ma)<br>**IronStealer（&lt;RANDOM&gt; .dat）：**<br>
是恶意软件删除的加密货币盗窃模块持久性的后门文件。<br>**1. 加载Cobalt Strike beacon：**<br>
恶意软件会自动解密硬编码的shellcode阶段1，然后使用反射加载器将内存中的Cobalt Strike信标加载到内存中：<br>[![](https://p1.ssl.qhimg.com/t016283b26644814aca.png)](https://p1.ssl.qhimg.com/t016283b26644814aca.png)<br>**Beacon: hxxp://dazqc4f140wtl.cloudfront[.]net/ZZYO**<br>**2. 删除和执行有效载荷：有效载荷URL从硬编码的Pastebin粘贴地址中获取：**<br>[![](https://p5.ssl.qhimg.com/t01df4795e3c9e0c27f.png)](https://p5.ssl.qhimg.com/t01df4795e3c9e0c27f.png)<br>
我们观察到恶意软件丢弃了两种不同的有效载荷：<br>**1. Xagent** – [“ JbossMiner挖掘蠕虫 ”](https://yq.aliyun.com/articles/558034)的变体- 一种用Python编写的蠕虫，它使用PyInstaller编译，用于Windows和Linux平台。JbossMiner使用已知的数据库漏洞进行传播。“Xagent”是原始文件名Xagent &lt;VER&gt; .exe，而&lt;VER&gt;似乎是蠕虫的版本。观察的最后一个版本是版本6（Xagent6.exe）。<br>[![](https://p3.ssl.qhimg.com/t01bb5249ca4b8c5d92.png)](https://p3.ssl.qhimg.com/t01bb5249ca4b8c5d92.png)<br>
** VT所见的Xagent版本4-6

**2.Iron ransomware** -我们最近看到了从放弃Xagent到放弃[Iron ransomware](https://bartblaze.blogspot.co.il/2018/04/maktub-ransomware-possibly-rebranded-as.html)的变化。看来钱包和付款门户网站地址与Bart观察到的地址相同。索要的赎金从0.2 BTC降至0.05 BTC，很可能是由于他们收到的[付款不足](https://blockchain.info/address/1cimKyzS64PRNEiG89iFU3qzckVuEQuUj)。<br>[![](https://p4.ssl.qhimg.com/t013010c9d7e61d4643.png)](https://p4.ssl.qhimg.com/t013010c9d7e61d4643.png)<br>
**没有人支付，所以他们减少赎金到0.05 BTC

**3.从受害者的工作站窃取加密货币**：Iron后门将释放最新的[voidtool](https://www.voidtools.com/)所有搜索工具，并实际静默地使用msiexec将其安装到受害者的工作站上。安装完成后，Iron Backdoor使用Everything来查找可能包含加密货币钱包的文件，按英文和中文文件名模式查找。<br>[![](https://p0.ssl.qhimg.com/t0142169d9682ab57c2.png)](https://p0.ssl.qhimg.com/t0142169d9682ab57c2.png)

从样本中提取的模式的完整列表：<br>
– Wallet.dat<br>
– UTC–<br>
– Etherenum keystore filename<br>
– **bitcoin**.txt<br>
– **比特币**.txt<br>
– “Bitcoin”<br>
– **monero**.txt<br>
– **门罗币**.txt<br>
– “Monroe Coin”<br>
– **litecoin**.txt<br>
– **莱特币**.txt<br>
– “Litecoin”<br>
– **Ethereum**.txt<br>
– **以太币**.txt<br>
– “Ethereum”<br>
– **miner**.txt<br>
– **挖矿**.txt<br>
– “Mining”<br>
– **blockchain**.txt<br>
– **coinbase**<br>**4. 利用加密货币劫持正在进行的付款：** IronStealer会持续监控用户的剪贴板上的比特币，Monero以及Ethereum钱包地址正则表达式模式。一旦匹配，它会自动将其替换为攻击者的钱包地址，以便受害者不知不觉将资金转移到攻击者的帐户<br>[![](https://p3.ssl.qhimg.com/t0199717c9d1e2a250f.png)](https://p3.ssl.qhimg.com/t0199717c9d1e2a250f.png)<br>**Pastebin帐户：**<br>
作为调查的一部分，我们还试图找出我们可能从攻击者的Pastebin帐户中学到的额外信息：<br>
该帐户可能是使用邮件&lt;a href=”https://community.riskiq.com/search/whois/email/[fineisgood123@gmail.com](mailto:fineisgood123@gmail.com)“&gt;fineisgood123 @ gmail [。] com创建的 – 用于注册blockbitcoin [。] com（攻击者的加密挖掘池和恶意软件主机）和swb [。] com（旧服务器用于主机恶意软件和泄露的文件。由u.cacheoffer [。] tk取代：）<br>[![](https://p1.ssl.qhimg.com/t018939a6df4334a57b.png)](https://p1.ssl.qhimg.com/t018939a6df4334a57b.png)<br>**1. Index.html：** HTML页面，指的是一个虚假的Firefox下载页面。<br>**2. crystal_ext-min + angular：**JS注入使用恶意Chrome扩展。<br>**3. android：**这个粘贴包含一个命令行，用于在受感染的Android设备上执行未知的后台应用程序。该命令行调用远程[Metasploit stager](https://www.virustotal.com/#/file/fc37713a25e32cee8a2748b8d8fde641f4a67a1987c5a26f8ec7951b091f634e)（android.apk）并删除为ARM处理器构建的[cpuminer 2.3.2](https://www.virustotal.com/#/file/3b92f3b878112fc093392421281aff4449aac0ade84b840b044dee824592f2d5)（minerd.txt）。考虑到上次更新日期（18/11/17）以及较少的浏览次数，我们认为该粘贴已过时。<br>**4. androidminer：**保存cpuminer命令行来执行未知的恶意android应用程序，在写这篇文章时，这个贴子获得了近2000次点击。<br>
Aikapool [。] com是一个公共采矿池，端口7915用于DogeCoin：<br>[![](https://p0.ssl.qhimg.com/t01ce3adddaf975cd21.png)](https://p0.ssl.qhimg.com/t01ce3adddaf975cd21.png)<br>
Aikapool [。] com是一个公共采矿池，端口7915用于DogeCoin：<br>
用户名（myapp2150）用于在多个论坛和[Reddit](https://www.reddit.com/user/myapp2150)上注册帐户。这些帐户被用于通过伪造的“[区块链利用工具](https://www.virustotal.com/#/file/04f70aa20682c9b29715ddd078b314730c62a9cececcd35347f4ee315e669d7f)”进行广告宣传，该工具通过Cobalt Strike使用与[Malwrologist](https://twitter.com/sS55752750/status/989180154994884608)（ps5.sct）发现相似的VBScript脚本来感染受害者的机器。<br>[![](https://p0.ssl.qhimg.com/t01032fc8276304f0de.png)](https://p0.ssl.qhimg.com/t01032fc8276304f0de.png)<br>**XAttacker**：XAttacker [PHP远程文件上传脚本](https://github.com/Moham3dRiahi/XAttacker/blob/master/XAttacker.php)的副本<br>**矿工：**持有有效载荷URL，如上所述（IronStealer）<br>**FAQ:**<br>**有多少受感染者？**<br>
这很难确定，但据我们所知，攻击者的贴图总数大约接受14K的观看次数，大约11K的有效负载URL和android矿工贴图的大约2K。基于此，我们估计该小组已成功感染了几千名受害者。<br>**谁是 Iron group背后组织者？**<br>
我们怀疑该团体背后的人是中国人，部分原因是由于以下情况：<br>
1、插件中有几处中文留言。<br>
2、根CA证书密码（使用中文’f * ck your mom123’）<br>
我们还怀疑大多数受害者位于中国，因为有以下结果：<br>
1、在受害者的工作站上搜索中文钱包文件名称。<br>
2、如果发现Qhioo360（中国著名的杀毒软件安全厂商），病毒样本将不会被执行。

**IOCS:**

• blockbitcoin[.]com<br>
• pool.blockbitcoin[.]com<br>
• ssl2.blockbitcoin[.]com<br>
• xmr.enjoytopic[.]tk<br>
• down.cacheoffer[.]tk<br>
• dzebppteh32lz.cloudfront[.]net<br>
• dazqc4f140wtl.cloudfront[.]net<br>
• androidapt.s3-accelerate.amazonaws[.]com<br>
• androidapt.s3-accelerate.amazonaws[.]com<br>
• winapt.s3-accelerate.amazonaws[.]com<br>
• swb[.]one<br>
• bitcoinwallet8[.]com<br>
• blockchaln[.]info<br>
• 6350a42d423d61eb03a33011b6054fb7793108b7e71aee15c198d3480653d8b7<br>
• a4faaa0019fb63e55771161e34910971fd8fe88abda0ab7dd1c90cfe5f573a23<br>
• ee5eca8648e45e2fea9dac0d920ef1a1792d8690c41ee7f20343de1927cc88b9<br>
• 654ec27ea99c44edc03f1f3971d2a898b9f1441de156832d1507590a47b41190<br>
• 980a39b6b72a7c8e73f4b6d282fae79ce9e7934ee24a88dde2eead0d5f238bda<br>
• 39a991c014f3093cdc878b41b527e5507c58815d95bdb1f9b5f90546b6f2b1f6<br>
• a3c8091d00575946aca830f82a8406cba87aa0b425268fa2e857f98f619de298<br>
• 0f7b9151f5ff4b35761d4c0c755b6918a580fae52182de9ba9780d5a1f1beee8<br>
• ea338755e8104d654e7d38170aaae305930feabf38ea946083bb68e8d76a0af3<br>
• 4de16be6a9de62b1ff333dd94e63128e677eb6a52d9fbbe55d8a09a2cab161f1<br>
• 92b4eed5d17cb9892a9fe146d61787025797e147655196f94d8eaf691c34be8c<br>
• 6314162df5bc2db1200d20221641abaac09ac48bc5402ec29191fd955c55f031<br>
• 7f3c07454dab46b27e11fcefd0101189aa31e84f8498dcb85db2b010c02ec190<br>
• 927e61b57c124701f9d22abbc72f34ebe71bf1cd717719f8fc6008406033b3e9<br>
• f1cbacea1c6d05cd5aa6fc9532f5ead67220d15008db9fa29afaaf134645e9de<br>
• 1d34a52f9c11d4bf572bf678a95979046804109e288f38dfd538a57a12fc9fd1<br>
• 2f5fb4e1072044149b32603860be0857227ed12cde223b5be787c10bcedbc51a<br>
• 0df1105cbd7bb01dca7e544fb22f45a7b9ad04af3ffaf747b5ecc2ffcd8c6dee<br>
• 388c1aecdceab476df8619e2d722be8e5987384b08c7b810662e26c42caf1310<br>
• 0b8473d3f07a29820f456b09f9dc28e70af75f9dec88668fb421a315eec9cb63<br>
• 251345b721e0587f1f08f54a81e26abac075acf3c4473a2c3ba8efcedc3b2459<br>
• b1fe223cbb01ff2a658c8ff51d386b5df786fd36278ee081c714adf946145047<br>
• 2886e25a86a57355a8a09a84781a9b032de10c3e40339a9ad0c10b63f7f8e7c7<br>
• 1d17eb102e75c08ab6f54387727b12ec9f9ee1960c8e5dc7f9925d41a943cabf<br>
• 5831dabe27e0211028296546d4e637770fd1ec5f2c8c5add51d0ea09b6ea3f0d<br>
• 85b0d44f3e8fd636a798960476a1f71d6fe040fbe44c92dfa403d0d014ff66cc<br>
• 936f4ce3570017ef5db14fb68f5e775a417b65f3b07094475798f24878d84907<br>
• 484b4cd953c9993090947fbb31626b76d7eee60c106867aa17e408556d27b609<br>
• 1cbd51d387561cafddf10699177a267cd5d2d184842bb43755a0626fdc4f0f3c<br>
• e41a805d780251cb591bcd02e5866280f8a99f876cfa882b557951e30dfdd142<br>
• b8107197469839a82cae25c3d3b5c25b5c0784736ca3b611eb3e8e3ced8ec950<br>
• b0442643d321003af965f0f41eb90cff2a198d11b50181ef8b6f530dd22226a7<br>
• 657a3a4a78054b8d6027a39a5370f26665ee10e46673a1f4e822a2a31168e5f9<br>
• 5977bee625ed3e91c7f30b09be9133c5838c59810659057dcfd1a5e2cf7c1936<br>
• 9ea69b49b6707a249e001b5f2caaab9ee6f6f546906445a8c51183aafe631e9f<br>
• 283536c26bb4fd4ea597d59c77a84ab812656f8fe980aa8556d44f9e954b1450<br>
• 21f1a867fa6a418067be9c68d588e2eeba816bffcb10c9512f3b7927612a1221<br>
• 45f794304919c8aa9282b0ee84c198703a41cc2254fe93634642ada3511239d2<br>
• 70e47fdff286fdfe031d05488bc727f5df257eacaa0d29431fb69ce680f6fb0c<br>
• ce7161381a0a0495ef998b5e202eb3e8fa2945dfdba0fd2a612d68b986c92678<br>
• b8d548ab2a1ce0cf51947e63b37fe57a0c9b105b2ef36b0abc1abf26d848be00<br>
• 74e777af58a8ee2cff4f9f18013e5b39a82a4c4f66ea3e17d06e5356085265b7<br>
• cd4d1a6b3efb3d280b8d4e77e306e05157f6ef8a226d7db08ac2006cce95997c<br>
• 78a07502443145d762536afaabd4d6139b81ca3cc9f8c28427ec724a3107e17b<br>
• 729ab4ff5da471f210a8658f4a7b2a30522534a212ac44e4d76f258baab19ccb<br>
• ca0df32504d3cf78d629e33b055213df5f71db3d5a0313ebc07fe2c05e506826<br>
• fc9d150d1a7cbda2600e4892baad91b9a4b8c52d31a41fd686c21c7801d1dd8c<br>
• bf2984b866c449a8460789de5871864eec19a7f9cadd7d883898135a4898a38a<br>
• 9d817d77b651d2627e37c01037e13808e1047f9528799a435c7bc04e877d70b3<br>
• 8fdec2e23032a028b8bd326dc709258a2f705c605f6222fc0c1616912f246f91<br>
• dbe165a63ed14e6c9bdcd314cf54d173e68db9d36623b09057d0a4d0519f1306<br>
• 64f96042ab880c0f2cd4c39941199806737957860387a65939b656d7116f0c7e<br>
• e394b1a1561c94621dbd63f7b8ea7361485a1f903f86800d50bd7e27ad801a5f<br>
• 506647c5bfad858ff6c34f93c74407782abbac4da572d9f44112fee5238d9ae1<br>
• 194362ce71adcdfa0fe976322a7def8bb2d7fb3d67a44716aa29c2048f87f5bc<br>
• 3652ea75ce5d8cfa0000a40234ae3d955781bcb327eecfee8f0e2ecae3a82870<br>
• 97d41633e74eccf97918d248b344e62431b74c9447032e9271ed0b5340e1dba0<br>
• a8ab5be12ca80c530e3ef5627e97e7e38e12eaf968bf049eb58ccc27f134dc7f<br>
• 37bea5b0a24fa6fed0b1649189a998a0e51650dd640531fe78b6db6a196917a7<br>
• 7e750be346f124c28ddde43e87d0fbc68f33673435dddb98dda48aa3918ce3bd<br>
• fcb700dbb47e035f5379d9ce1ada549583d4704c1f5531217308367f2d4bd302<br>
• b638dcce061ed2aa5a1f2d56fc5e909aa1c1a28636605a3e4c0ad72d49b7aec6<br>
• f2e4528049f598bdb25ce109a669a1f446c6a47739320a903a9254f7d3c69427<br>
• afd7ab6b06b87545c3a6cdedfefa63d5777df044d918a505afe0f57179f246e9<br>
• 9b654fd24a175784e3103d83eba5be6321142775cf8c11c933746d501ca1a5a1<br>
• e6c717b06d7ded23408461848ad0ee734f77b17e399c6788e68bc15219f155d7<br>
• e302aa06ad76b7e26e7ba2c3276017c9e127e0f16834fb7c8deae2141db09542<br>
• d020ea8159bb3f99f394cd54677e60fadbff2b91e1a2e91d1c43ba4d7624244d<br>
• 36104d9b7897c8b550a9fad9fe2f119e16d82fb028f682d39a73722822065bd3<br>
• d20cd3e579a04c5c878b87cc7bd6050540c68fdd8e28f528f68d70c77d996b16<br>
• ee859581b2fcea5d4ff633b5e40610639cd6b11c2b4fc420720198f49fbd1d31<br>
• ef2c384c795d5ca8ce17394e278b5c98f293a76047a06fc672da38bb56756aec<br>
• bd56db8d304f36af7cb0380dcbbc3c51091e3542261affb6caac18fa6a6988ec<br>
• 086d989f14e14628af821b72db00d0ef16f23ba4d9eaed2ec03d003e5f3a96a1<br>
• f44c3fd546b8c74cc58630ebcb5bea417696fac4bb89d00da42202f40da31354<br>
• 320bb1efa1263c636702188cd97f68699aebbb88c2c2c92bf97a68e689fa6f89<br>
• 42faf3af09b955de1aead2b99a474801b2c97601a52541af59d35711fafb7c6d<br>
• 6e0adfd1e30c116210f469d76e60f316768922df7512d40d5faf65820904821b<br>
• eea2d72f3c9bed48d4f5c5ad2bef8b0d29509fc9e650655c6c5532cb39e03268<br>
• 1a31e09a2a982a0fedd8e398228918b17e1bde6b20f1faf291316e00d4a89c61<br>
• 042efe5c5226dd19361fb832bdd29267276d7fa7a23eca5ced3c2bb7b4d30f7d<br>
• 274717d4a4080a6f2448931832f9eeb91cc0cbe69ff65f2751a9ace86a76e670<br>
• f8751a004489926ceb03321ea3494c54d971257d48dadbae9e8a3c5285bd6992<br>
• d5a296bac02b0b536342e8fb3b9cb40414ea86aa602353bc2c7be18386b13094<br>
• 49cfeb6505f0728290286915f5d593a1707e15effcfb62af1dd48e8b46a87975<br>
• 5f2b13cb2e865bb09a220a7c50acc3b79f7046c6b83dbaafd9809ecd00efc49a<br>
• 5a5bbc3c2bc2d3975bc003eb5bf9528c1c5bf400fac09098490ea9b5f6da981f<br>
• 2c025f9ffb7d42fcc0dc8d056a444db90661fb6e38ead620d325bee9adc2750e<br>
• aaa6ee07d1c777b8507b6bd7fa06ed6f559b1d5e79206c599a8286a0a42fe847<br>
• ac89400597a69251ee7fc208ad37b0e3066994d708e15d75c8b552c50b57f16a<br>
• a11bf4e721d58fcf0f44110e17298f6dc6e6c06919c65438520d6e90c7f64d40<br>
• 017bdd6a7870d120bd0db0f75b525ddccd6292a33aee3eecf70746c2d37398bf<br>
• ae366fa5f845c619cacd583915754e655ad7d819b64977f819f3260277160141<br>
• 9b40a0cd49d4dd025afbc18b42b0658e9b0707b75bb818ab70464d8a73339d52<br>
• 57daa27e04abfbc036856a22133cbcbd1edb0662617256bce6791e7848a12beb<br>
• 6c54b73320288c11494279be63aeda278c6932b887fc88c21c4c38f0e18f1d01<br>
• ba644e050d1b10b9fd61ac22e5c1539f783fe87987543d76a4bb6f2f7e9eb737<br>
• 21a83eeff87fba78248b137bfcca378efcce4a732314538d2e6cd3c9c2dd5290<br>
• 2566b0f67522e64a38211e3fe66f340daaadaf3bcc0142f06f252347ebf4dc79<br>
• 692ae8620e2065ad2717a9b7a1958221cf3fcb7daea181b04e258e1fc2705c1e<br>
• 426bc7ffabf01ebfbcd50d34aecb76e85f69e3abcc70e0bcd8ed3d7247dba76e

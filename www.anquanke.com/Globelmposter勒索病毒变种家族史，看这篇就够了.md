> 原文链接: https://www.anquanke.com//post/id/183648 


# Globelmposter勒索病毒变种家族史，看这篇就够了


                                阅读量   
                                **209581**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t012300d4ee62262dc4.png)](https://p0.ssl.qhimg.com/t012300d4ee62262dc4.png)



群里朋友发来一条求助信息，问是中了哪个家族的勒索病毒，后面发来了相关的勒索病毒勒索信息和样本，经过确认为Globelmposter4.0变种家族，笔者跟踪分析过不少勒索病毒家族，最近一两年针对企业的勒索病毒攻击，真的是越来越多了，基本上每天都会不同的朋友通过微信或公众号咨询我，求助勒索病毒相关的信息，同时很多朋友在后台给我留言关于勒索病毒的相关信息和样本，感谢大家的信任与支持，也欢迎更多的朋友给我提交关于勒索病毒的相关信息和样本，一起研究对抗勒索病毒攻击，针对企业的勒索病毒攻击在最近一段时间暴涨，此前我在公众号了发表过一篇文章《勒索不断！勒索病毒数量第二季度暴涨三倍》，目前国内外主要流行的几大勒索病毒家族分别是：Sodinokibi、GandCrab、Ryuk、Phobos、Globelmposter、CrySiS(Dharma)、CryptoMix、Paradise等，今天给大家分享一下Globelmposter这款勒索病毒家族的一些信息

Globelmposter勒索病毒首次出现是在2017年5月份，主要通过钓鱼邮件进行传播，2018年2月国内各大医院爆发Globelmposter变种样本2.0版本，通过溯源分析发现此勒索病毒可能是通过RDP爆破、社会工程等方式进行传播，此勒索病毒采用RSA2048加密算法，导致加密后的文件无法解密

Globelmposter2.0使用的加密后缀列表为：TRUE、FREEMAN、CHAK、TECHNO、DOC、ALC0、ALC02、ALC03、RESERVE、GRANNY、BUNNY+、BIG、ARA、WALKER、XX、BONUM、DONALD、FOST、GLAD、GORO、MIXI、RECT、SKUNK、SCORP、TRUMP、PLIN等，生成的超文本HTML勒索信息文件how_to_back_files.html，如下所示：

[![](https://p4.ssl.qhimg.com/t0143a6c979835f4dd5.png)](https://p4.ssl.qhimg.com/t0143a6c979835f4dd5.png)

后面出现Globelmposter2.0变种使用的加密后缀列表为：

`{`[killbillkill@protonmail.com](mailto:killbillkill@protonmail.com)`}`VC、`{`[travolta_john@aol.com](mailto:travolta_john@aol.com)`}`ROCK

`{`[travolta_john@aol.com](mailto:travolta_john@aol.com)`}`GUN、`{`[colin_farel@aol.com](mailto:colin_farel@aol.com)`}`XX

`{`[saruman7@india.com](mailto:saruman7@india.com)`}`.BRT92、[i-[absolutus@bigmir.net](mailto:absolutus@bigmir.net)].rose、

[[lightright@bigmir.net](mailto:lightright@bigmir.net)].ransom、[[bensmit@tutanota.com](mailto:bensmit@tutanota.com)]_com

`{`[jeepdayz@aol.com](mailto:jeepdayz@aol.com)`}`BIT、`{`[mixifightfiles@aol.com](mailto:mixifightfiles@aol.com)`}`BIT

`{`[baguvix77@yahoo.com](mailto:baguvix77@yahoo.com)`}`.AK47、`{`[colin_farel@aol.com](mailto:colin_farel@aol.com)`}`BIT

`{`[legosfilos@aol.com](mailto:legosfilos@aol.com)`}`BIT、`{`[lxgiwyl@india.com](mailto:lxgiwyl@india.com)`}`.AK47

`{`[omnoomnoomf@aol.com](mailto:omnoomnoomf@aol.com)`}`BIT

生成的超文本勒索信息文件how_to_back_files.html，勒索背景采用红蓝两种模式，如下所示：

[![](https://p1.ssl.qhimg.com/t0124e4cf687c405fde.png)](https://p1.ssl.qhimg.com/t0124e4cf687c405fde.png)

[![](https://p0.ssl.qhimg.com/t015c503f5b3d862c64.png)](https://p0.ssl.qhimg.com/t015c503f5b3d862c64.png)

2019年5月份出现Globelmposter2.0最新的一款变种，代码与之前的Globelmposter2.0基本相似，使用的加密后缀列表为：

`{`[HulkHoganZTX@protonmail.com](mailto:HulkHoganZTX@protonmail.com)`}`ZT

[Killserver@protonmail.com](mailto:Killserver@protonmail.com)`}`KSR

`{`[CALLMEGOAT@PROTONMAIL.COM](mailto:CALLMEGOAT@PROTONMAIL.COM)`}`CMG

`{`[Killback@protonmail.com](mailto:Killback@protonmail.com)`}`KBK

生成的超文本勒索信息文件decrypt_files.html，如下所示：

[![](https://p4.ssl.qhimg.com/t019d226e3445f94566.png)](https://p4.ssl.qhimg.com/t019d226e3445f94566.png)

2018年8月份此勒索病毒出现Globelmposter3.0变种样本，再次大范围攻击国内多个政企事业单位，Globelmposter3.0采用了十二生肖英文名+4444的加密后缀，列表如下所示：

Ox4444、Snake4444、Rat4444、

Tiger4444、Rabbit4444、Dragon4444、

Horse4444、Goat4444 、Monkey4444 、

Rooster4444 、Dog4444 、Pig4444

所以Globelmposter3.0勒索病毒俗称”十二生肖勒索病毒”，生成的勒索信息文件变成了文本文件HOW_TO_BACK_FILES.txt，如下所示：

[![](https://p0.ssl.qhimg.com/t01a6744206fe583f74.png)](https://p0.ssl.qhimg.com/t01a6744206fe583f74.png)

2019年1月份出现了一款新型的Globelmposter勒索病毒，称为Globelmposter4.0，此勒索病毒加密后缀为fuck等，生成的勒索信息超文本文件README_BACK_FILES.htm，如下所示：

[![](https://p3.ssl.qhimg.com/t0117e30c5b873f9aa6.png)](https://p3.ssl.qhimg.com/t0117e30c5b873f9aa6.png)

2019年3月出现了此勒索病毒的变种，称为Globelmposter4.0变种，加密后缀为：auchentoshan、makkonahi，生成的勒索信息为超文本文件how_to_open_files.html，如下所示：

[![](https://p2.ssl.qhimg.com/t011d778585fd1b1f82.png)](https://p2.ssl.qhimg.com/t011d778585fd1b1f82.png)

后面又捕获到了它的一款变种，代码基本一致，勒索信息仍然为how_to_open_files.html，如下所示：

[![](https://p3.ssl.qhimg.com/t01315c4b65a673910c.png)](https://p3.ssl.qhimg.com/t01315c4b65a673910c.png)

最新的Globelmposter5.0变种版本为Globelmposter十二主神版，它采用了古希腊宗教中最受崇拜的十位主神+666的加密后缀，加密后缀列表，如下所示：

Ares666、Zeus666、Aphrodite666、Apollon666、Poseidon666、Artemis666、Dionysus666、Hades666、Persephone666、Hephaestus666、Hestia666、Athena666，生成的勒索信息文本文件HOW TO BACK YOURFILES.txt，如下所示：

[![](https://p0.ssl.qhimg.com/t015e79d3d98ed60120.png)](https://p0.ssl.qhimg.com/t015e79d3d98ed60120.png)

此前全球最流行的勒索病毒是GandCrab，然而这款勒索病毒算是国内最流行的勒索病毒了，已经有不少企业中招，变种非常频繁，很活跃，笔者曾分析过这款索病毒的十几个不同的版本，这里只列举出几个比较大的而且流行的版本，很遗憾的是这款勒索病毒从2.0版本开始就无法解密，目前也没有哪个机构或组织公布这款勒索病毒的解密工具

本文转自：[安全分析与研究](https://mp.weixin.qq.com/s/wdY8chr5Zfqx9DM1JjkbSQ)

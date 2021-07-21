> 原文链接: https://www.anquanke.com//post/id/167066 


# 对UNNAMED1989勒索病毒的传播及代码的相关分析


                                阅读量   
                                **180606**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t01b3cbbe95bd732075.png)](https://p3.ssl.qhimg.com/t01b3cbbe95bd732075.png)

12月2日凌晨，360互联网安全中心紧急发布了关于最新勒索病毒UNNAMED1989的传播情况和初步分析结论。2日早晨，我们还公布了解密工具帮助中招用户解密。经过一天时间，360又对该勒索病毒的传播和代码进行了进一步的深入分析。

## 传播渠道

该勒索病毒主要捆绑在刷量软件、外挂、打码软件、私服等第三方开发的应用程序传播，通过QQ、QQ群共享、网盘分享、论坛贴吧等形式将这些应用程序发送给受害者。受害者运行后机器上就会感染下载器木马，之后再由下载器木马安装其它恶意程序，这之中就包括本次传播的UNNAMED1989勒索病毒。部分参与传播本次勒索病毒的应用程序如下表所示。
<td valign="top" width="277">应用程序文件名</td><td valign="top" width="277">MD5</td>

MD5
<td valign="top" width="277">大刷子.exe</td><td valign="top" width="277">8f9463f9a9e56e8f97f30cd06dd2b7be</td>

8f9463f9a9e56e8f97f30cd06dd2b7be
<td valign="top" width="277">更新器.exe</td><td valign="top" width="277">9368b4b542a275b8d0a2b19601b5823e</td>

9368b4b542a275b8d0a2b19601b5823e
<td valign="top" width="277">【苏州vip】益农社全自动邀请_se.exe</td><td valign="top" width="277">baff9b641d7baff59a33dfac1057c4a8</td>

baff9b641d7baff59a33dfac1057c4a8
<td valign="top" width="277">【白浅vip】掌上生活-20v1.0.exe</td><td valign="top" width="277">d5f9cfa306bcdd50c3b271bfe01d81ff</td>

d5f9cfa306bcdd50c3b271bfe01d81ff
<td valign="top" width="277">[无验证]【夜夜】海草公社邀请注册1.1.exe</td><td width="277">42651293d5e0b970521a465d2c4928a6</td>

42651293d5e0b970521a465d2c4928a6
<td valign="top" width="277">【夺宝头条】邀请阅读v1.0.exe</td><td valign="top" width="277">028c48146f08691ae8df95b237d39272</td>

028c48146f08691ae8df95b237d39272

表1 部分参与传播本次勒索病毒的应用程序信息

经分析发现，这些下载器在代码风格上与此次勒索病毒高度一致，可能出自同一黑客（团伙）之手。下图展示了这些应用程序与勒索病毒的一段代码对照：

[![](https://p2.ssl.qhimg.com/t01d08552e55fc94f90.png)](https://p2.ssl.qhimg.com/t01d08552e55fc94f90.png)

[![](https://p5.ssl.qhimg.com/t01e114aba66b7ddd2d.png)](https://p5.ssl.qhimg.com/t01e114aba66b7ddd2d.png)

图1 传播程序与勒索病毒部分代码对照

## 传播过程

从感染下载器木马，到被下发勒索病毒周期较长，部分受害者在中招多天之后才遭到勒索，很难关联到是由于之前使用的一些外挂程序造成的。当受害者运行带毒的外挂软件时，软件主程序会在多个目录下释放恶意文件，其中部分释放路径如下表所示。
<td valign="top" width="553">%userprofile%\appdata\local\temp\9377.game\</td>
<td valign="top" width="553">%userprofile%\appdata\local\temp\gamedown\009\</td>
<td valign="top" width="553">%userprofile%\appdata\roaming\tencent\rtl\uistyle\x64\</td>
<td valign="top" width="553">%userprofile%\appdata\roaming\tencent\rtl\uistyle\</td>

表2 恶意文件释放路径

释放的恶意文件是一组带有导入表DLL劫持的“白利用”组合（该技术在国内病毒制作圈中非常流行），攻击者通过DLL劫持的方式劫持合法程序执行流程，使“正常”程序执行恶意代码，试图躲避杀毒软件查杀。攻击者使用的三组“白利用”如表3所示。
<td valign="top" width="277">合法程序MD5</td><td valign="top" width="277">“白利用”恶意程序MD5</td>

“白利用”恶意程序MD5
<td valign="top" width="277">495ae240d5cd6c9269815f3b90f0522a</td><td valign="top" width="277">43079041ef46324f86ac9afc96169104</td>

43079041ef46324f86ac9afc96169104
<td valign="top" width="277">74828b11ba45d85ccd069559a4cf56fa</td><td valign="top" width="277">847bcf6655db46673ad135997de77cf2</td>

847bcf6655db46673ad135997de77cf2
<td valign="top" width="277">e59e119b3b2d3fe2a8ac8857c7dcecfc</td><td valign="top" width="277">6455b968e811041998c384d6826814df</td>

6455b968e811041998c384d6826814df

表3 攻击者使用的三组“白利用”

这三组“白利用”被用做木马下载器使用，长期驻留用户系统。攻击者在其豆瓣主页以及github中保存一组加密的控制指令，下载器读取到指令后解密获得下阶段木马程序下载URL。图4展示了保存在攻击者豆瓣主页的加密字符串。图5则展示了字符串解密后的配置文件内容。

[![](https://p3.ssl.qhimg.com/t01a6eba068c8ae857a.png)](https://p3.ssl.qhimg.com/t01a6eba068c8ae857a.png)

图4 保存在豆瓣的加密字符串

[![](https://p2.ssl.qhimg.com/t01a1c805693d62b7c7.png)](https://p2.ssl.qhimg.com/t01a1c805693d62b7c7.png)

图5 解密后的配置文件内容

程序获取到的下阶段木马下载URL指向一张由正常图片和压缩包拼接而成的图片，通过截取图片并解压文件能够获取下一阶段程序。图5展示了图片的十六进制内容，可以明显看见zip压缩包的文件头部。

[![](https://p4.ssl.qhimg.com/t01a7127167bd6992a2.png)](https://p4.ssl.qhimg.com/t01a7127167bd6992a2.png)

图6 程序下载的由正常图片和压缩包拼接而成的图片

之后的木马程序会从网络上下载更多拼接了恶意文件的图片并提取恶意文件。根据我们分析发现，攻击者不仅通过该方式往受害者机器上植入勒索病毒，还植入过盗号木马。这些恶意程序会注入到合法进程中工作，并带有更新功能，通过获取攻击者豆瓣主页上的字符串获取更新地址，以根据情况更改植入受害者计算机的恶意程序。

[![](https://p3.ssl.qhimg.com/t019b4abb7c2a5755d0.png)](https://p3.ssl.qhimg.com/t019b4abb7c2a5755d0.png)

图7 木马程序中硬编码的下载地址

在11月19日开始，攻击者开始通过上述方式向用户计算机中植入名为realtekarm.dll.aux的恶意程序并在机器中持续驻留。之后realtekarm.dll.aux作为下载器以相同方式下载勒索病毒相关文件。并将勒索病毒写入了用户计算机的启动项，在用户下次启动计算机时，文件就会被加密。该勒索病毒同样是通过DLL劫持方式，劫持正常程序执行其病毒功能。

[![](https://p2.ssl.qhimg.com/t01b43a65fcbb72f3cd.png)](https://p2.ssl.qhimg.com/t01b43a65fcbb72f3cd.png)

图8 攻击者释放的勒索病毒相关文件

[![](https://p4.ssl.qhimg.com/t016bb340310994bced.png)](https://p4.ssl.qhimg.com/t016bb340310994bced.png)

图9 被加入启动项的勒索病毒及命令行

根据360互联网安全中心根据传播此次勒索病毒的下载器所请求的域名进行了统计，下图展示的就是下载器自11月16日起，对其相关域名进行请求的PV和UV波动趋势，在一定程度上也可反映出该勒索病毒的传播趋势。

[![](https://p0.ssl.qhimg.com/t01868aaa7be77e6342.png)](https://p0.ssl.qhimg.com/t01868aaa7be77e6342.png)

图10 传播本次勒索病毒的下载器对相关域名请求的波动趋势



## 勒索病毒分析

勒索病毒运行后，会加密桌面上以及除了C盘外的其他磁盘中的文件。在加密文件类型选择上，除了应用程序运行时所需要的文件类型——例如exe、dll、ini等——被放过之外，其他文件均被加密。这也造成用户文档、图片等重要文件被加密。

[![](https://p3.ssl.qhimg.com/t019d741616efa88a4b.png)](https://p3.ssl.qhimg.com/t019d741616efa88a4b.png)

图11 勒索病毒放过的文件类型

在加密算法上，该勒索病毒选择了极为简单的异或加密。首先将特定标识符、版本信息以及随机字符串进行简单处理后存放在C:\Users\unname_1989\dataFile路径下，文件名为appCfg.cfg。

[![](https://p2.ssl.qhimg.com/t01409c79f5d62181e8.png)](https://p2.ssl.qhimg.com/t01409c79f5d62181e8.png)

图12 生成密钥存放到appCfg.cfg中

加密文件时，从第120位读取appCfg.cfg中的密钥，与硬编码在程序中的字符串按位异或之后，作为加密密钥与待加密文件内容按位异或。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0184b7cca0db615c4f.png)

图13 勒索病毒加密过程

因为加密文件通过简单的异或算法实现，因此该勒索病毒是可解的。同时，由于appCfg.cfg中存放的密钥包含随机生成的部分，因此受害用户需要保留该文件以进行解密。



## 一些建议
1. 不要相信刷量、外挂、打码、私服等一些较为灰色的软件所声称的“杀毒软件误报论”。
1. 对来自即时通讯软件或邮件附件中的陌生软件要提高警惕。尽可能不下载、不运行，如确实需要，一定要提前用安全软件进行查杀以保障安全。
1. 养成良好的安全习惯，及时更新系统和软件，修补漏洞。不给黑客和恶意程序可乘之机。
1. 360安全卫士可正常拦截该病毒攻击，并可解密已被该勒索病毒加密的文件，请即使安装和确保其正常运行
[![](https://p0.ssl.qhimg.com/t018f351985824d9382.jpg)](https://p0.ssl.qhimg.com/t018f351985824d9382.jpg)

图14 360安全卫士可正常拦截本次勒索病毒

[![](https://p4.ssl.qhimg.com/t01c9b139763f0b05e2.jpg)](https://p4.ssl.qhimg.com/t01c9b139763f0b05e2.jpg)

图15 360解密大师可成功解密被该勒索病毒加密的文件

## IOCs

566bb1d3c05d4eb94e634e16e3afcc33

8f9463f9a9e56e8f97f30cd06dd2b7be

baff9b641d7baff59a33dfac1057c4a8

d5f9cfa306bcdd50c3b271bfe01d81ff

42651293d5e0b970521a465d2c4928a6

028c48146f08691ae8df95b237d39272

43079041ef46324f86ac9afc96169104

847bcf6655db46673ad135997de77cf2

6455b968e811041998c384d6826814df

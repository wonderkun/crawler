> 原文链接: https://www.anquanke.com//post/id/228652 


# Hidden Tear 以疫情为话题的勒索事件分析


                                阅读量   
                                **205977**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01b18b82ebe42fc27a.jpg)](https://p3.ssl.qhimg.com/t01b18b82ebe42fc27a.jpg)



## 概述

近日，微步情报局在对一恶意样本进行分析时，对样本的 C2 地址进行关联分析发现，该地址还接收到勒索软件的回传。通过对回传信息的格式进行关联，发现使用了一款名为“Hidden Tear”的勒索软件。
1. 微步情报局发现某恶意样本会从域名 dllhost.xyz 下载后续脚本文件执行。
1. 对域名 dllhost.xyz 进行关联分析，发现该域名有着一表示格式的回传请求，通过对回传信息的分析发现，是首款针对 Windows 的开源勒索软件，名为“Hidden Tear”。
1. 在近一年中，发生了多起使用该款勒索软件利用 COVID-19 的话题对受害者进行攻击。
1. 勒索软件“Hidden Tear”使用 AES 加密，在本地生成 AES 密钥，并使用固定格式将密钥和主机信息回传到 C2 地址。


## 详情

近期，微步情报局捕获到一枚 .LNK 格式的恶意软件，在分析过程中发现该木马后续会调用 Powershell 继续从域名 dllhost.xyz 下载后续 .js 文件，而 .js 文件会尝试向另一域名 dlldns.xyz 发起请求进行下一步操作。

[![](https://p2.ssl.qhimg.com/t019b5561442e488012.png)](https://p2.ssl.qhimg.com/t019b5561442e488012.png)

图1 .lnk 执行的代码

[![](https://p0.ssl.qhimg.com/t01997a3ebd2e61b39a.png)](https://p0.ssl.qhimg.com/t01997a3ebd2e61b39a.png)

图2 .js 中的后续地址

通过对样本相关域名（dllhost.xyz、dlldns.xyz）的关联分析发现，域名中还含有另一使用 .pdf 图标的恶意文件，且在回传信息时会使用固定格式：

[![](https://p5.ssl.qhimg.com/t0111c55fe88c535321.png)](https://p5.ssl.qhimg.com/t0111c55fe88c535321.png)

图3. 回传信息的请求

“write.php?Computername=XXXUsername=XXXPassword=XXXallow=ransom”

通过对格式的分析，确定了一款名为“Hidden Tear”的开源勒索软件。

[![](https://p2.ssl.qhimg.com/t011fd08347f07b5d82.png)](https://p2.ssl.qhimg.com/t011fd08347f07b5d82.png)

图4. X社区中关于域名情报

Hidden Tears 是第一个针对 Microsoft Windows 的开源勒索软件，由土耳其安全研究员 Utku Sen 于 2015 年首次上传到 GitHub，目前原始仓库的代码已被删除，但在删除前已被 fork 了 490 次，在其他用户的仓库中依然可以找到原始的代码。

[![](https://p4.ssl.qhimg.com/t016b1612dfc6ecc126.png)](https://p4.ssl.qhimg.com/t016b1612dfc6ecc126.png)

图5. Hidden Tear 页面

关联发现，近一年来，发生了多起使用基于该勒索软件的修改版本利用 COVID-19 的话题对受害者发起攻击的事件。例如：2020 年3 月，有攻击者向参与 COVID-19 研究的卫生组织与大学发送钓鱼邮件，邮件中包含勒索软件。2020 年 5 月，有攻击者注册仿冒官方域名，向意大利发送 COVID-19 疫情图的诱饵文件，加密受害者主机勒索比特币。

“Hidden Tear” 勒索软件使用 AES 加密，获取用户的主机信息并由此生成密钥，并将用户的信息按照固定格式，和密钥一同发送到 C2 地址。不过值得注意的是，生成密钥的步骤在本地生成，并且在发往 C2 地址时并没有进行加密操作，这意味着在流量数据中可以直接找到密钥对文件进行解密。

[![](https://p2.ssl.qhimg.com/t015d6d1eb8aa27533c.png)](https://p2.ssl.qhimg.com/t015d6d1eb8aa27533c.png)

图6. 回传信息的固定格式



## 相关事件

2020 年 3 月，攻击者利用伪造的邮箱发件地址 noreply@who.int（176.223.133.91）向参与 COVID-19 研究的加拿大卫生组织与大学发送电子邮件，电子邮件内包含了文件名为“20200323-sitrep-63-covid-19.doc”的RTF文件。

[![](https://p4.ssl.qhimg.com/t01b2108e76cb7fa39d.png)](https://p4.ssl.qhimg.com/t01b2108e76cb7fa39d.png)

图7. 诱饵文档（看起来并不是很想引诱用户）

2020 年 5 月，基于 Hidden Tear 的变种勒索软件 FuckUnicorn 利用 COVID-19 对意大利发起攻击，通过注册”意大利药剂师联合会”（fofi.it）的仿冒域名（fofl.it）来进行恶意软件的分发。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ff8f0494930e9901.jpg)

图 8. 攻击者伪造的钓鱼页面



## 样本分析

### **1. 20200323-sitrep-63-covid-19.doc**

基本信息：
<td class="ql-align-center" data-row="1">**File Name**</td><td class="ql-align-center" data-row="1">**File Type**</td><td class="ql-align-center" data-row="1">**SHA256**</td>
<td class="ql-align-justify" data-row="2">20200323-sitrep-63-covid-19.doc</td><td class="ql-align-justify" data-row="2">Ransomware</td><td class="ql-align-justify" data-row="2">62d38f19e67013ce7b2a84cb17362c77e2f13134ee3f8743cbadde818483e617</td>

一旦受害者将 .rtf 打开后，文档会尝试利用 CVE-2012-0158 漏洞，将勒索软件释放到C:\Users\User\AppData\Local\svchost.exe 并执行，释放出的 svchost.exe 具有隐藏属性，且带有一个 Adobe Acrobat 的图标。

样本执行后，会尝试从地址 tempinfo.96[.]lt/wras/RANSOM20.jpg 请求一张显示勒索通知的图片并将图片保存到 C:\Users\User\ransom20.jpg，然后将图片设置为桌面壁纸。

[![](https://p0.ssl.qhimg.com/t017d6df39b9aadff44.png)](https://p0.ssl.qhimg.com/t017d6df39b9aadff44.png)

图9. 勒索信息页面

下载图片之后，会检查与 C2 地址的 HTTP 状态码是否为 100 Continue，向地址www.tempinfo.96.lt/wras/createkeys.php发送 POST 请求，发送主机如计算机名、用户名等相关信息。在原始的 Hidden Tear 中，POST 请求的页面为 /write.php?info=。

[![](https://p1.ssl.qhimg.com/t01ad5eeac02783c6b2.png)](https://p1.ssl.qhimg.com/t01ad5eeac02783c6b2.png)

图10. 流量数据包

发送信息完成后，会通过获取到的主机信息，在本地生成 AES 对称密钥，并将密钥发往 C2 地址，并通过 POST 请求将主机信息与 AES 密钥一同发往 C2 地址。

[![](https://p1.ssl.qhimg.com/t0173a30a21053481f3.png)](https://p1.ssl.qhimg.com/t0173a30a21053481f3.png)

图11. 流量中的密钥

完成后开始对主机的文件进行加密，特定的后缀如下：
<td class="ql-align-center" data-row="1">.abw</td><td class="ql-align-center" data-row="1">.aww</td><td class="ql-align-center" data-row="1">.chm</td><td class="ql-align-center" data-row="1">.dbx</td><td class="ql-align-center" data-row="1">.djvu</td><td class="ql-align-center" data-row="1">.doc</td><td class="ql-align-center" data-row="1">.docm</td><td class="ql-align-center" data-row="1">.docx</td><td class="ql-align-center" data-row="1">.dot</td>
<td class="ql-align-center" data-row="2">.bak</td><td class="ql-align-center" data-row="2">.bbb</td><td class="ql-align-center" data-row="2">.bkf</td><td class="ql-align-center" data-row="2">.bkp</td><td class="ql-align-center" data-row="2">.dbk</td><td class="ql-align-center" data-row="2">.gho</td><td class="ql-align-center" data-row="2">.iso</td><td class="ql-align-center" data-row="2">.json</td><td class="ql-align-center" data-row="2">.mdbackup</td>
<td class="ql-align-center" data-row="3">.pdf</td><td class="ql-align-center" data-row="3">.pmd</td><td class="ql-align-center" data-row="3">.pot</td><td class="ql-align-center" data-row="3">.potx</td><td class="ql-align-center" data-row="3">.pps</td><td class="ql-align-center" data-row="3">.ppsx</td><td class="ql-align-center" data-row="3">.ppt</td><td class="ql-align-center" data-row="3">.pptm</td><td class="ql-align-center" data-row="3">.pptx</td>
<td class="ql-align-center" data-row="4">.shs</td><td class="ql-align-center" data-row="4">.snp</td><td class="ql-align-center" data-row="4">.sxw</td><td class="ql-align-center" data-row="4">.tpl</td><td class="ql-align-center" data-row="4">.vsd</td><td class="ql-align-center" data-row="4">.wpd</td><td class="ql-align-center" data-row="4">.wps</td><td class="ql-align-center" data-row="4">.wri</td><td class="ql-align-center" data-row="4">.xps</td>
<td class="ql-align-center" data-row="5">.mht</td><td class="ql-align-center" data-row="5">.mpp</td><td class="ql-align-center" data-row="5">.odf</td><td class="ql-align-center" data-row="5">.ods</td><td class="ql-align-center" data-row="5">.odt</td><td class="ql-align-center" data-row="5">.ott</td><td class="ql-align-center" data-row="5">.oxps</td><td class="ql-align-center" data-row="5">.pages</td><td class="ql-align-center" data-row="5">.dotm</td>
<td class="ql-align-center" data-row="6">.spb</td><td class="ql-align-center" data-row="6">.spba</td><td class="ql-align-center" data-row="6">.tib</td><td class="ql-align-center" data-row="6">.wbcat</td><td class="ql-align-center" data-row="6">.zip</td><td class="ql-align-center" data-row="6">7z</td><td class="ql-align-center" data-row="6">.dll</td><td class="ql-align-center" data-row="6">.dbf</td><td class="ql-align-center" data-row="6">.nba</td>
<td class="ql-align-center" data-row="7">.ind</td><td class="ql-align-center" data-row="7">.indd</td><td class="ql-align-center" data-row="7">.key</td><td class="ql-align-center" data-row="7">.keynote</td><td class="ql-align-center" data-row="7">.dotx</td><td class="ql-align-center" data-row="7">.epub</td><td class="ql-align-center" data-row="7">.gp4</td><td class="ql-align-center" data-row="7">.prn</td><td class="ql-align-center" data-row="7">.pub</td>
<td class="ql-align-center" data-row="8">.old</td><td class="ql-align-center" data-row="8">.rar</td><td class="ql-align-center" data-row="8">.sbf</td><td class="ql-align-center" data-row="8">.sbu</td><td class="ql-align-center" data-row="8">.nbf</td><td class="ql-align-center" data-row="8">.nco</td><td class="ql-align-center" data-row="8">.nrg</td><td class="ql-align-center" data-row="8">.prproj</td><td class="ql-align-center" data-row="8">.ps</td>
<td class="ql-align-center" data-row="9">.pwi</td><td class="ql-align-center" data-row="9">.rtf</td><td class="ql-align-center" data-row="9">.sdd</td><td class="ql-align-center" data-row="9">.sdw</td><td class="ql-align-justify" data-row="9"></td><td class="ql-align-justify" data-row="9"></td><td class="ql-align-justify" data-row="9"></td><td class="ql-align-justify" data-row="9"></td><td class="ql-align-justify" data-row="9"></td>

加密过程中，样本加密的路径仅为主机桌面的目录和文件。加密算法也相对比较简单，加密后后缀为 .locked20 。

[![](https://p1.ssl.qhimg.com/t0134b15b4eee4e588c.png)](https://p1.ssl.qhimg.com/t0134b15b4eee4e588c.png)

图12. 加密算法

### **2. IMMUNI.exe**

通过钓鱼站点 fofl.it 进行下发。

基本信息：
<td class="ql-align-center" data-row="1">**File Name**</td><td class="ql-align-center" data-row="1">**File Type**</td><td class="ql-align-center" data-row="1">**MD5**</td>
<td class="ql-align-justify" data-row="2">IMMUNI.exe</td><td class="ql-align-justify" data-row="2">Ransomware</td><td class="ql-align-justify" data-row="2">b226803ac5a68cd86ecb7c0c6c4e9d00</td>

样本是一个 exe 文件，图标带有一个新冠病毒，并且属性中的文件名为“FuckUnicorn”。

[![](https://p5.ssl.qhimg.com/t017f4c932da9cff0f2.png)](https://p5.ssl.qhimg.com/t017f4c932da9cff0f2.png)

图13. 文件属性页面

在样本运行后，会显示一个伪造的 COVID-19 疫情情况信息图表，来自 the Center for Systems Science and Engineering at Johns Hopkins University 。

[![](https://p0.ssl.qhimg.com/t01af302e87400044b7.png)](https://p0.ssl.qhimg.com/t01af302e87400044b7.png)

图14. 诱饵文件 – COVID-19 疫情图

在用户阅读图表的时候，样本会开始加密用户的文件，加密的文件夹包括主机的 /Desktop, /Links, /Contacts, /Documents, /Downloads, /Pictures, /Music, /OneDrive, /Saved Games, /Favorites, /Searches, /Videos 。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f5b8ff79ce0932fc.png)

图15. 要加密的目录

加密后的后缀为“.fuckunicornhtrhrtjrjy”加密的类型包括：
<td class="ql-align-center" data-row="1">.Txt</td><td class="ql-align-center" data-row="1">.jar</td><td class="ql-align-center" data-row="1">.exe</td><td class="ql-align-center" data-row="1">.dat</td><td class="ql-align-center" data-row="1">.contact</td><td class="ql-align-center" data-row="1">.settings</td><td class="ql-align-center" data-row="1">.doc</td><td class="ql-align-center" data-row="1">.docx</td>
<td class="ql-align-center" data-row="2">.aspx</td><td class="ql-align-center" data-row="2">.html</td><td class="ql-align-center" data-row="2">.htm</td><td class="ql-align-center" data-row="2">.xml</td><td class="ql-align-center" data-row="2">.psd</td><td class="ql-align-center" data-row="2">.pdf</td><td class="ql-align-center" data-row="2">.dll</td><td class="ql-align-center" data-row="2">.c</td>
<td class="ql-align-center" data-row="3">.lnk</td><td class="ql-align-center" data-row="3">.iso</td><td class="ql-align-center" data-row="3">.7-zip</td><td class="ql-align-center" data-row="3">.ace</td><td class="ql-align-center" data-row="3">.arj</td><td class="ql-align-center" data-row="3">.bz2</td><td class="ql-align-center" data-row="3">.cab</td><td class="ql-align-center" data-row="3">.gzip</td>
<td class="ql-align-center" data-row="4">.ppt</td><td class="ql-align-center" data-row="4">.pptx</td><td class="ql-align-center" data-row="4">.odt</td><td class="ql-align-center" data-row="4">.jpg</td><td class="ql-align-center" data-row="4">.png</td><td class="ql-align-center" data-row="4">.csv.</td><td class="ql-align-center" data-row="4">py</td><td class="ql-align-center" data-row="4">.sql</td>
<td class="ql-align-center" data-row="5">.mp4</td><td class="ql-align-center" data-row="5">.f3d</td><td class="ql-align-center" data-row="5">.dwg</td><td class="ql-align-center" data-row="5">.cpp</td><td class="ql-align-center" data-row="5">.zip</td><td class="ql-align-center" data-row="5">.rar</td><td class="ql-align-center" data-row="5">.mov</td><td class="ql-align-center" data-row="5">.rtf</td>
<td class="ql-align-center" data-row="6">.uue</td><td class="ql-align-center" data-row="6">.xz</td><td class="ql-align-center" data-row="6">.z</td><td class="ql-align-center" data-row="6">.001</td><td class="ql-align-center" data-row="6">.mpeg</td><td class="ql-align-center" data-row="6">.mp3</td><td class="ql-align-center" data-row="6">.mpg</td><td class="ql-align-center" data-row="6">.core</td>
<td class="ql-align-center" data-row="7">.php</td><td class="ql-align-center" data-row="7">.asp</td><td class="ql-align-center" data-row="7">.ico</td><td class="ql-align-center" data-row="7">.pas</td><td class="ql-align-center" data-row="7">.db</td><td class="ql-align-center" data-row="7">.torrent</td><td class="ql-align-center" data-row="7">.avi</td><td class="ql-align-center" data-row="7">.apk</td>
<td class="ql-align-center" data-row="8">.xls</td><td class="ql-align-center" data-row="8">.xlsx</td><td class="ql-align-center" data-row="8">.lzh</td><td class="ql-align-center" data-row="8">.tar</td><td class="ql-align-center" data-row="8">.bmp</td><td class="ql-align-center" data-row="8">.mkv</td><td class="ql-align-center" data-row="8">.crproj</td><td class="ql-align-center" data-row="8">.pdb</td>
<td class="ql-align-center" data-row="9">.cs</td><td class="ql-align-center" data-row="9">.mp3</td><td class="ql-align-center" data-row="9">.mdb</td><td class="ql-align-center" data-row="9">.sln</td><td class="ql-align-justify" data-row="9"></td><td class="ql-align-justify" data-row="9"></td><td class="ql-align-justify" data-row="9"></td><td class="ql-align-justify" data-row="9"></td>

加密完成后提供了钱包地址（195naAM74WpLtGHsKp9azSsXWmBCaDscxJ）及邮箱地址（xxcte2664@protonmail.com），需要支付 300 欧元的比特币，但勒索信息留下的邮件地址无效，受害者根本无法通过此邮箱地址联系上攻击者。

[![](https://p4.ssl.qhimg.com/t01ecc8fbcf40ca8507.png)](https://p4.ssl.qhimg.com/t01ecc8fbcf40ca8507.png)

图16. 勒索信息文本

## 结语

除了文中所提两类样本外，还有更多的 Hidden Tears 变种版本且一直有对外攻击的行为。由于代码作者将程序在网络公开开源，使得很多开发水平不足的人也能立马上手编译出勒索软件，使勒索攻击的门槛再次降低。虽然如此，但是好在样本使用 AES 对称加密，并且在本地生成密钥并且不加密传输，这意味着加密后的文件可以直接解密。

**关于微步情报局**

微步情报局，即微步在线研究响应团队，负责微步在线安全分析与安全服务业务，主要研究内容包括威胁情报自动化研发、高级APT组织&amp;黑产研究与追踪、恶意代码与自动化分析技术、重大事件应急响应等。

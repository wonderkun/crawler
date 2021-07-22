> 原文链接: https://www.anquanke.com//post/id/185566 


# Gorgon APT组织再做文章：DropBox到NJRat的曲折历程


                                阅读量   
                                **318337**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01fdc797191807c5a2.png)](https://p3.ssl.qhimg.com/t01fdc797191807c5a2.png)



## 背景

近日，奇安信威胁情报中心在发布[《Gorgon黑客组织再显新招：通过在线网盘发起“三重奏”攻击》](https://mp.weixin.qq.com/s/7PlBz6j8ATFsKUOUYhfyjw)的分析报告后，在对该南亚组织的进一步追踪发现，该组织除了使用Blogspot+pastebin的在线网盘获取木马payload的模式进行攻击外，其还会使用DropBox下载Payload，从伪装的MP3或JPG文件获取最终木马的方式进行攻击。



## 样本分析

本次投递的DownLoader是一个docx文档，打包时间2018年8月22号，上传VirusTotal的时间是2019年8月26日，使用模板注入的方式从DropBox下载后续payload，后续payload是一个RTF文件，内嵌了8个带有宏的Excel OLE对象。启用宏之后会从C&amp;C下载VBS脚本并执行，VBS经过解密执行PS脚本从C&amp;C下载两个payload，并解密最后通过注入器将njrat注入到MSBuild.exe进程中。

DownLoader样本分析
<td valign="top" width="78">文件名</td><td valign="top" width="480">Reserva Ricargo Bago.docx</td>
<td valign="top" width="78">MD5</td><td valign="top" width="480">de2eea6519b4150800b2122300809948</td>
<td valign="top" width="78">时间</td><td valign="top" width="480">2019-08-22 19:11:00</td>

模板注入，打开文档时会从

hxxps://www.dropbox.com/s/0m29532jztadbda/bsuPQI87aopY.doc?dl=1下载RTF文件并打开

[![](https://p0.ssl.qhimg.com/t0126210c825e65bc9f.png)](https://p0.ssl.qhimg.com/t0126210c825e65bc9f.png)

bsuPQI87aopY.doc样本信息：
<td valign="top" width="78">文件名</td><td valign="top" width="480">bsuPQI87aopY.doc</td>
<td valign="top" width="78">MD5</td><td valign="top" width="480">5287c2873d1a28be773a2457b6f1f4c9</td>
<td valign="top" width="78">时间</td><td valign="top" width="480">2019-08-22 21:06:00</td>

该RTF文件内嵌了8个带有旧版宏警告的Excel ole对象

[![](https://p4.ssl.qhimg.com/t0148a9cc935b45bb9f.png)](https://p4.ssl.qhimg.com/t0148a9cc935b45bb9f.png)

当打开该RTF文档时，会弹出Excel表格，并显示旧版宏警告，如果点击禁用，则会弹出下一个Excel，一直持续8次，该技术Carrie Roberts在其博客上[1]有详细的描述。

[![](https://p5.ssl.qhimg.com/t018fff2c5e0802d2b0.png)](https://p5.ssl.qhimg.com/t018fff2c5e0802d2b0.png)

Excel中的宏会从172.105.68.75/pirata.txt下载VBS脚本，保存名为MTServices.vbs

[![](https://p5.ssl.qhimg.com/t018aafe97ba5234160.png)](https://p5.ssl.qhimg.com/t018aafe97ba5234160.png)

调用Wscript执行MTServices.vbs，

[![](https://p0.ssl.qhimg.com/t01c8a6992ae2518333.png)](https://p0.ssl.qhimg.com/t01c8a6992ae2518333.png)

VBS会调用Powershell执行脚本

[![](https://p4.ssl.qhimg.com/t0147dd6b1d19bcca5b.png)](https://p4.ssl.qhimg.com/t0147dd6b1d19bcca5b.png)

Powershell最中会解密并执行最后的ps脚本

[![](https://p0.ssl.qhimg.com/t0197b9b8249626002b.png)](https://p0.ssl.qhimg.com/t0197b9b8249626002b.png)

从hxxp://www.m9c.net/uploads/15647132812.mp3和hxxp://www.m9c.net/uploads/15647132811.jpg下载后续payload和脚本，15647132811.jpg内容如下，解密后的15647132811.jpg一个是C#编写的远控木马：

[![](https://p3.ssl.qhimg.com/t0143a18ae7eb3070d4.png)](https://p3.ssl.qhimg.com/t0143a18ae7eb3070d4.png)

15647132812.mp3内容如下，执行脚本解密出一个C#编写的注入器：

[![](https://p1.ssl.qhimg.com/t011f778eb934d51041.png)](https://p1.ssl.qhimg.com/t011f778eb934d51041.png)

PS脚本通过调用注入器的GFG类中的exe方法，将njrat注入到MSBuild.exe中：

[![](https://p3.ssl.qhimg.com/t0139a5632f370331da.png)](https://p3.ssl.qhimg.com/t0139a5632f370331da.png)

经过分析，被注入的C#程序，互斥量为EDFRWFGH-vJoGYkaB6OOZ的njrat远控木马

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f3f82316f194320b.png)

链接的域名为duckapp.duckdns.org，IP地址为141.255.145.208:5552

## 同源分析

通过开源情报可知，Gorgon组织曾利用hxxp://www.m9c.net域名发起攻击,最早可以追溯到6月份，该组织通过hxxps://pastebin.com进行payload的投放，最后释放的依然是一个njrat，远控域名：queda212.duckdns.org

经过溯源发现相似样本
<td valign="top" width="78">文件名</td><td valign="top" width="480">DADOS_CONFIRMAÇÃO_DE_RESERVA_IDAZA.doc</td>
<td valign="top" width="78">MD5</td><td valign="top" width="480">a77c33fe1d7112eeba2d9653aba67218</td>
<td valign="top" width="78">时间</td><td valign="top" width="480">2019-07-17 04:37:00</td>

打开文档界面如下：

[![](https://p4.ssl.qhimg.com/t01262e6260821eabed.png)](https://p4.ssl.qhimg.com/t01262e6260821eabed.png)

同样是模板注入从hxxp://bit.ly/2JD9Tlr下载RTF文档：

[![](https://p4.ssl.qhimg.com/t0120526a50359167a4.png)](https://p4.ssl.qhimg.com/t0120526a50359167a4.png)

RTF文档信息：
<td valign="top" width="78">文件名</td><td valign="top" width="480">tabela.doc</td>
<td valign="top" width="78">MD5</td><td valign="top" width="480">83bbe5e2a5242de93eb546e4ef22c6fc</td>
<td valign="top" width="78">时间</td><td valign="top" width="480">2019-07-17 01:20:00</td>

该RTF同样内嵌了带有旧版宏警告的Excel ole对象，启用宏之后会从

hxxp://refugiovistaserrana.com.br:80/novosite2/HNSUSbFuYM48DATA16072019.mp3

下载VBS脚本，如图所示，此处的混淆方法在上一篇报告中也有所提及。

[![](https://p3.ssl.qhimg.com/t01b79c16d890b15a25.png)](https://p3.ssl.qhimg.com/t01b79c16d890b15a25.png)

“للظال”和“!의있을모!”是Gorgon组织常用混淆，VBS调用PS脚本

[![](https://p2.ssl.qhimg.com/t010bc9453d7ddac978.png)](https://p2.ssl.qhimg.com/t010bc9453d7ddac978.png)

Base64解密后

[![](https://p4.ssl.qhimg.com/t015b5b1b80ea71ddc7.png)](https://p4.ssl.qhimg.com/t015b5b1b80ea71ddc7.png)

从hxxps://refugiovistaserrana.com.br/novosite/tt.mp3，下载Payload解密并执行，payload同样为njrat，远控域名依然是duckapp.duckdns.org，IP及端口141.255.147.151:5555

至此，本篇可作为上篇关于Gorgon组织系列分析的延伸，仅供参考。

## 总结

Gorgon，一个被认为来自南亚某国家的黑客组织，其目标涉及全球政府，外贸等行业，且目的不纯粹为了金钱，还可能与政治相关。

而从本次活动中，Gorgon仍在使用一些传统木马进行攻击，例如njrat这类“旧时代”木马，但也足以证明，在注重诱饵变更，以及投递手法的创新，在Payload获取的路子上做文章，将会是目前大多数黑客组织常使用的手段，但也是最节省成本，最有效的手段。

目前奇安信集团全线产品，包括天眼、SOC、态势感知、威胁情报平台，支持对涉及Gorgon组织的攻击活动检测，并且奇安信安全助手支持对该组织的样本进行拦截。

## IOC

文件Hash：

de2eea6519b4150800b2122300809948

7fe468b10d95cc993a499abc6a2760a41024f7fe

300c9b54a3747925d7dc5457cbfb93f2f8c2a4ee

7fa6b8a902a46cf7678a3ea225a3a661f37c8ea5 2ab26f82b54ebd841019b6dcc6b92027ae97fd15 b09dbb9ba2c95019bb34e12010be81140ea6a96a 08212a083f7c969132e0e7f6ff0dfe2a713eb2a1 b3b79e5f8893b1eec4171e473716636146845e3c 925be2c3a80370a5f6d1786d7efcd3e51043662a

97b779463c494544fc698d7ca08725e0d41e37bb

C&amp;C：

141.255.147.151:5555

141.255.145.208:5552

172.105.68.75

URL:

www.dropbox.com/s/0m29532jztadbda/bsuPQI87aopY.doc?dl=1

172.105.68.75/pirata.txt

www.m9c.net/uploads/15647132812.mp3

www.m9c.net/uploads/15647132811.jpg

bit.ly/2JD9Tlr

duckapp.duckdns.org

refugiovistaserrana.com.br:80/novosite2/HNSUSbFuYM48DATA16072019.mp3

refugiovistaserrana.com.br/novosite/tt.mp3

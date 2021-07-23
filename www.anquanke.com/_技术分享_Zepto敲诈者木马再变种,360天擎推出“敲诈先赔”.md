> 原文链接: https://www.anquanke.com//post/id/84604 


# 【技术分享】Zepto敲诈者木马再变种,360天擎推出“敲诈先赔”


                                阅读量   
                                **89790**
                            
                        |
                        
                                                                                    



**[![](https://p4.ssl.qhimg.com/t01863e606d261d284d.png)](https://p4.ssl.qhimg.com/t01863e606d261d284d.png)**

**前言**

近日，360威胁情报中心捕获到新一批的zepto敲诈者木马开始通过邮件附件传播，与以往有所不同的是，新一波的邮件附件，不再使用之前的js脚本作为最初的下载器，而是改用HTA脚本。 一旦中招，用户电脑上的视频、图片、文档等文件内容会被加密，扩展名被改为.zepto，并修改桌面背景图片提示要求支付比特币赎金。

[![](https://p5.ssl.qhimg.com/t01e26f642adc548a2e.png)](https://p5.ssl.qhimg.com/t01e26f642adc548a2e.png)

图1中毒后要求支付比特币赎金的桌面背景图片

**技术说明**

最新变种的Zepto敲诈者病毒，病毒的本体还是之前的Locky家族，只是在传播过程中，在原来js或vbs文件的基础上加了层hta外壳。此病毒通过钓鱼邮件传播，当用户收到此类含有欺骗性内容的邮件，诱使用户双击附件中后缀名为hta的文件，系统会创建进程mshta.exe执行hta文件中保存的js或vbs代码，这些代码会先从服务器下载加密的病毒本体，解密后由rundll32.exe加载执行，进而加密用户电脑上的文件。

从邮件附件压缩包中解压出的hta文件可直接用文本编辑器打开，很明显的是一段嵌入了javascript脚本的HTML代码。但，却是经过重重加密的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fd3ef0b9dacad221.png)

经过解密后，可见关键代码。首先脚本会尝试从列表中所给出的三个URL下载payload文件到本地并执行，只要其中任意一个被成功运行起来便会跳出循环，不再尝试后面的下载地址：

[![](https://p2.ssl.qhimg.com/t016811d7f15329f42e.png)](https://p2.ssl.qhimg.com/t016811d7f15329f42e.png)

而每次循环中，脚本都会首先尝试下载payload文件，若成功下载会本地，便会解密文件，把文件恢复成可执行的PE文件格式，再通过文件大小和一些特定偏移量标记判断恢复是否成功：

[![](https://p5.ssl.qhimg.com/t01e2fd8527151a67f8.png)](https://p5.ssl.qhimg.com/t01e2fd8527151a67f8.png)

而payload被下载回来之后，读取文件的时候本身就会有一次转换：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01447b6caec7ac6bf7.png)

而在读取完文件，并成功转换为数组后，会正式进行解密：

[![](https://p0.ssl.qhimg.com/t01abf75e5d50cbc90f.png)](https://p0.ssl.qhimg.com/t01abf75e5d50cbc90f.png)

如此大费周章的获取到一个真正的可执行程序，最后在调用系统的rundll32进程，带参数”qwerty”执行该dll木马程序：

[![](https://p1.ssl.qhimg.com/t015c9decdf14603cce.png)](https://p1.ssl.qhimg.com/t015c9decdf14603cce.png)

而最终执行的这个dll程序与之前的敲诈者木马就别无二致了，都是调用advapi32中提供的加密函数逐文件进行加密，此处不再赘述：

[![](https://p2.ssl.qhimg.com/t0150270afef8514c74.png)](https://p2.ssl.qhimg.com/t0150270afef8514c74.png)

**样本信息**

l  HTA下载器样本：

 6890ceb469a2c8735c4ef4a60d8bfb7931960d4ecf5d6e09d2547a6f7ff0cc4b<br> ed39f8d1b158a87adeb91be2c47bacd15593390edb2b96713214071ee44f2c26<br> 0025c118675d62dfabcf26698e78870138b5440ac96ccf8d41b32b4d0536aa55

l  Dll敲诈者木马样本：<br> 60b2d7d1cf0d543b5287088fa5f1d594181a128024770fc6cd08cb414a4ab07e

l  Payload下载地址：

[http://sbbsinfotech[.]com/56f2gsu782desf](http://sbbsinfotech%5B.%5Dcom/56f2gsu782desf)

 [http://stirlingblack[.]com/56f2gsu782desf](http://stirlingblack%5B.%5Dcom/56f2gsu782desf)

 [http://hunt-magzine[.]com/56f2gsu782desf](http://hunt-magzine%5B.%5Dcom/56f2gsu782desf)

<br>

**360天擎安全防护**

360天擎可以成功拦截：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018e95e3662b4c0a7d.png)

[![](https://p0.ssl.qhimg.com/t01ae68b101ade246b9.png)](https://p0.ssl.qhimg.com/t01ae68b101ade246b9.png)

**360天擎近期针对政企客户推出了“敲诈先赔”计划，在企业用户开启敲诈先赔功能后，如果360天擎仍无法防护，感染了敲诈者病毒，360天擎负责赔付赎金，并帮助用户恢复数据。**

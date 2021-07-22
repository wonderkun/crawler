> 原文链接: https://www.anquanke.com//post/id/83560 


# MIME类型文件反混淆工具


                                阅读量   
                                **88387**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://blog.didierstevens.com/2016/02/29/more-obfuscated-mime-type-files/](http://blog.didierstevens.com/2016/02/29/more-obfuscated-mime-type-files/)

译文仅供参考，具体内容表达以及含义原文为准

最近我收到了一个恶意文档样本（MD5:[FAF75220C0423F94658618C9169B3568](https://www.virustotal.com/en/file/1b8e75cbd9a74128da2b7620b0a88cf15f2f09748c6f528495c830d5b5a3adbe/analysis/)）

[![](https://p4.ssl.qhimg.com/t0125072b1677efaad7.png)](https://p4.ssl.qhimg.com/t0125072b1677efaad7.png)

我们可以看到它是MIME类型文件，这就是文件被混淆所在。第二行开始是多行带有随机字符和数字混淆编码，通过我自己的python MIME解析工具emldump解析后得到如下图：

[![](https://p0.ssl.qhimg.com/t01048d27a6334cdd47.png)](https://p0.ssl.qhimg.com/t01048d27a6334cdd47.png)

emldump检测到这只是一个文本文件，而不是由多部分组成的MIME类型文件，如果我们移除第二行后，再配合findstr /v (or grep -v)来检测的时候，emldump就识别出其他部分。

[![](https://p2.ssl.qhimg.com/t017e6900a22d5be2ad.png)](https://p2.ssl.qhimg.com/t017e6900a22d5be2ad.png)

因为混淆MIME类型文件已越来越流行了，所以我就增加了一项过滤以便过滤出混淆MIME类型文件的部分。如果不适用-f选项则会抛出文件超过100行的警告并且会把标题行给忽略了(就像使用-H选项一样)。

      

[![](https://p5.ssl.qhimg.com/t01008e15916ec890aa.png)](https://p5.ssl.qhimg.com/t01008e15916ec890aa.png)

使用-f选项你就你就可以过滤出混淆部分。

样本下载：

[emldump_V0_0_7.zip](http://didierstevens.com/files/software/emldump_V0_0_7.zip) ([https](https://didierstevens.com/files/software/emldump_V0_0_7.zip))

MD5: 819D4AF55F556B2AF08DCFB3F7A8C878<br style="text-indent:2em;text-align:left"> SHA256: D5C7C2A1DD3744CB0F50EEDFA727FF0487A32330FF5B7498349E4CB96E4AB284

<br style="text-indent:2em;text-align:left">

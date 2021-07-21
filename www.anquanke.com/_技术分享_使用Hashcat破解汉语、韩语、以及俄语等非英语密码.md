> 原文链接: https://www.anquanke.com//post/id/84573 


# 【技术分享】使用Hashcat破解汉语、韩语、以及俄语等非英语密码


                                阅读量   
                                **183962**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0103cfd399434afe00.png)](https://p0.ssl.qhimg.com/t0103cfd399434afe00.png)



作者：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

稿费：500RMB（不服你也来投稿啊！）

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

**写在前面的话**

近期闲来无事，在网上看安全新闻的时候突然看到了密码破解神器Hashcat发布了v3.10版本。于是我便点进去看看Hashcat又添加了什么新的功能，让我惊讶的是，Hashcat现在已经支持Mac OS X平台了。一翻更新日志才发现，原来Hashcat在v3.0.0版本时就已经新增了对OS X平台的支持，而我自从苦逼地凑钱买了一台rmbp之后，就基本上没有再碰过Hashcat了。

**<br>**

**直奔主题**

现在很多网站都会将用户密码的md5值直接存储在数据库中，而目前几乎所有的字典文件都是基于拉丁字符生成的，例如A-Z、a-z、0-9、以及各种特殊字符等等。而根据调查发现，有很多的用户已经开始使用各种非英语字符的密码了。这也就意味着，此前很多基于字典规则的攻击方式已经不再适用了。

[![](https://p4.ssl.qhimg.com/t01cd4d26cd321f19a8.png)](https://p4.ssl.qhimg.com/t01cd4d26cd321f19a8.png)

在这篇文章中，我将给大家演示如何使用Hashcat来破解非英文字符的密码。由于时间有限，我在这里只能给大家演示如何爆破一些常见的非拉丁字符密码，但是我相信整个流程还是可以给大家提供一个可行的思路。本人水平有限，如果有写的不对的地方，欢迎各位大牛指正，希望可以跟大家共同进步！那么话不多说，我们赶紧进入正题。

**<br>**

**让Hashcat在Mac上跑起来**

假设你的电脑已经安装好git了，那么现在请你打开你的terminal，切换到你想要放置Hashcat项目文件的目录（我直接克隆到了用户根目录下），然后输入下列代码：

```
git clone https://github.com/hashcat/hashcat.git
```

此时你的终端界面应该是这样的：

[![](https://p0.ssl.qhimg.com/t01f9145a13cccb0990.png)](https://p0.ssl.qhimg.com/t01f9145a13cccb0990.png)

别忘了，想要让Hashcat在Mac上成功跑起来，我们还要安装最新版的OpenCL环境。先在Hashcat目录下创建一个名为“env”的目录（environment），然后继续用git命令将OpenCL克隆到“env”目录下：



```
mkdir -p hashcat/env
git clone https://github.com/KhronosGroup/OpenCL-Headers.git hashcat/env/OpenCL
```

命令运行结果如下图所示：

[![](https://p5.ssl.qhimg.com/t01305ecefbe5e84dd1.png)](https://p5.ssl.qhimg.com/t01305ecefbe5e84dd1.png)

这一系列操作没问题的话，此时你应该可以在磁盘目录下看到Hashcat的项目文件了。别着急，我们还要build一下源码。切换到“hashcat”目录下，然后输入下列命令：

```
sudo make
```

请注意，如果你此前没有运行过Xcode的话，系统会提示你要同意Xcode的许可证，同意之后系统会自动Makefile。Build成功后的界面如下图所示：

[![](https://p5.ssl.qhimg.com/t0183c47689d3f8cf67.png)](https://p5.ssl.qhimg.com/t0183c47689d3f8cf67.png)

此时，切换到Hashcat目录下，输入命令



```
./hashcat --help
```

如果安装成功，终端将会显示Hashcat的帮助信息：

[![](https://p0.ssl.qhimg.com/t011ba57f9fc9e4056f.png)](https://p0.ssl.qhimg.com/t011ba57f9fc9e4056f.png)

现在，我们已经成功地让Hashcat在Mac OS X上运行起来了。

**<br>**

**关于字符的那些事儿**

如果你生活在以英语为主要语言的国家中，那么你肯定会非常熟悉ASCII码了，因为这是一套基于拉丁字母的编码系统。ASCII码使用一个字节编码来表示拉丁字符，即0000 0000-1111 1111，ASCII码用这总共256种组合方式来表示所有的拉丁字符。而在此之后，一种新的字符编码方式诞生了，它就是UTF-8。透露一下，我们今天的密码破解也是基于UTF-8编码来实现的。

目前，绝大多数的Web应用和网页都会采用UTF-8来进行字符编码。UTF-8字符编码可以使用1-4个字节来编码，即0000 0000-0000 0000 0000 0000 0000 0000 0000 0000，其中也包含了ASCII码的单字节区间，因此我们在Hashcat中进行密码爆破的时候，应当考虑到这一因素。

关于字符编码的问题我在这里就不多说了，反正你总有一天会被编码问题弄疯掉的…我们现在只关心在这篇文章中会接触到的汉语、韩语、以及俄语的常用字符编码。

**<br>**

**打好基础，稳步前进**

首先，我们以俄文（西里尔）字母来进行讲解。为什么呢？难道我们不应该以中文开始吗？别着急，咱们慢慢来。请各位先看下面这张UTF-8编码表：

[![](https://p0.ssl.qhimg.com/t01666a014b24ca1e4a.png)](https://p0.ssl.qhimg.com/t01666a014b24ca1e4a.png)

请注意第三列，西里尔（cyrillic）字母的大写字母“A”可以用十六进制的“d0 90”来表示，这也就说明西里尔字母的“A”可以用两个字节的十六进制码来表示，写成二进制的形式即为“1101 0000 1001 0000”。此时你就会发现，在ASCII码中的“A”为“41”（0100 0001），而UTF-8编码下的西里尔字母“A”为“d0 90”（ 1101 0000 1001 0000）。仔细观察之后你应该会发现，西里尔字母“A”的十六进制编码由两部分组成，前半部分为“d0”，即我们所谓的基础码；后半部分为“90”，即字符码。

我们可以从这张西里尔字母的UTF-8编码表［[传送门](http://www.utf8-chartable.de/unicode-utf8-table.pl?start=1024&amp;number=512)］中看到，西里尔字母的基础码范围在d0-d4之间，即d0、d1、d2、d3、d4，而可能的字符码范围在80-bf之间。请注意！这一点非常的重要，因为它将成为我们通过UTF-8编码来破解其他语言密码的基石。

**<br>**

**Hashcat能为我们做什么？**

Hashcat提供了一个参数“–hex-charset”,这个参数可以允许用户将待破解的数据以十六进制数值的形式输入给Hashcat。这是一个非常有用的参数，当你在命令中使用了这个参数之后，Hashcat会将你自定义的字符集合当作十六进制数值来处理，而不会将你的输入数据当作普通的英语字符。

比如说，在“–hex-charset”模式下，你将“-1”参数的值设置成了“ABBBBC”。那么Hashcat将会把“AB”、“BB”和“BC”分别当作三个字符，然后对这些十六进制数值所代表的明文数据进行暴力破解。如果此时将“-2”参数设置成了“808182”，那么在仅有“-1”和“-2”参数的情况下，Hashcat首先会比较“AB 80”的计算结果是否与待破解密码相匹配，如果不匹配，则比较“AB 81”、“AB 82”、“BB 80”、“BB 81”…以此类推，对所有可能的情况进行排列组合。

当然了，UTF-8编码是可变长度的。在俄语和阿拉伯语中，其每一个字符的UTF-8编码长度为两个字节，此时我们就需要使用到“-2”参数。还记得我们之前所说的基础码和字符码么？此时“-1”的值就是基础码，而“2”的值就是字符码。但是，在中文、韩文和日文之中，每一个字符的UTF-8编码需要占用三个字节，这也就意味着，我们需要使用到“-3”参数。原理其实是一样的，待会儿我会给大家演示。

接下来，我们还要使用到“-i”参数。比如说在破解俄语密码的情况下，因为我们已经设置好了“-1”和“-2”参数，那么在“-i”参数中，我们就要设置需要破解的密码长度。比如说，我们要破解的俄文单词由三个字母组成，那么“-i”参数就应该设置为“?1?2?1?2?1?2”。每个“?1?2”代表一个西里尔字母，我们假设密码由三个字母组成，所有就需要三个“?1?2”。而在单个字符由三字节UTF-8编码组成的情况下（例如中文），我们假设待破解的密码由两个汉字组成，那么“-i”参数应该为“?1?2?3?1?2?3”，因为每个“?1?2?3”代表一个汉字。

**<br>**

**测试前的准备工作**

首先，我们要计算出待破解密码的md5值。在此给大家提供两种方法，一种是使用终端的md5命令，另外一种是通过HashMaker。

**方法一**：md5 –s [密码字符串]

比如说，设置的密码为“安全”，那么我现在就要计算“安全”这个字符串的md5值：

[![](https://p2.ssl.qhimg.com/t01df8b954b28bb6171.png)](https://p2.ssl.qhimg.com/t01df8b954b28bb6171.png)

**方法二**：HashMaker［[下载地址](https://itunes.apple.com/us/app/hashmaker/id509733654?mt=12)］

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01eb6d04e7e2bd18e9.png)

为了方便进行测试，我们还要生成一些其他没有实际作用的md5值。除了第三行的md5值之外，其他都是一些其他字符的md5。

[![](https://p5.ssl.qhimg.com/t01216a64192fbc344c.png)](https://p5.ssl.qhimg.com/t01216a64192fbc344c.png)

其他语言的md5生成方法是相同的，在此不再进行赘述。

**<br>**

**中文密码破解**

相信大家最感兴趣的应该是中文密码的破解了，所以在此先演示中文密码的破解方法。实际上，破解原理和方法在文章中已经介绍到了，各种语言的破解过程其实也大同小异。

汉字的UTF-8编码占三个字节，例如汉字“一”的UTF-8编码为“E4 B8 80”。根据常用汉字的UTF-8编码［[编码表传送门](http://memory.loc.gov/diglib/codetables/9.1.html)］，“-1”参数应该设置成“e4e5e6e7e8e9”，“-2”和“-3”参数均为“808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebf”，这个编码范围足够覆盖常用的汉字了，其中还包括常用繁体字。

为了测试繁体字密码是否能够正常破解，于是我们还要在zh_cypher.txt中添加繁体字符串“數據”的md5：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01112650b360e72f02.png)

除此之外，还有一些其他的设置参数需要简单介绍一下：

–pot-disable：禁止Hashcat将已破解的哈希添加到potfile中，添加该参数可以避免测试过程中出现某些问题。

–outfile-autohex-disable：将破解出的密码结果以明文形式显示出来，如果不输入这个参数的话，密码破解的结果将以十六进制的形式输出。如果密码结果输出为乱码的话，可以去掉该参数，以便得到密码的原始十六进制数值。

-m 0：设置待破解数据的哈希类型，“0”即为MD5。

-a 3：设置攻击模式，“模式3”代表暴力破解。

**_cypher.txt：存放待破解密码哈希的文件。

在破解中文的示例中，我们的参数命令应该如下所示（假设待破解密码为两个汉字）：

```
./hashcat --potfile-disable --outfile-autohex-disable -m 0 -a 3 ../zh_cypher.txt --hex-charset -1 e3e4e5e6e7e8e9 -2 808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebf -3 808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebf -i ?1?2?3?1?2?3
```

运行结果如下图所示：

[![](https://p5.ssl.qhimg.com/t0163b6a01b94f92007.png)](https://p5.ssl.qhimg.com/t0163b6a01b94f92007.png)

[![](https://p1.ssl.qhimg.com/t01038ac6ba2688c97c.png)](https://p1.ssl.qhimg.com/t01038ac6ba2688c97c.png)

我们可以看到，Hashcat已经将“安全”和“數據”这两个密码成功破解出来了。接下来，给大家演示韩语和俄语密码的破解。

**<br>**

**韩语密码破解**

假设待破解密码为“”，中文即“安全”的意思。该字符串由两个韩语字组成，每个韩语字的UTF-8编码占三个字节［[编码表传送门](http://memory.loc.gov/diglib/codetables/9.3.html)］。korean_cypher.txt文件内容如下图所示：

[![](https://p2.ssl.qhimg.com/t013e1413623281fbf0.png)](https://p2.ssl.qhimg.com/t013e1413623281fbf0.png)

参数命令如下：

```
./hashcat --potfile-disable --outfile-autohex-disable -m 0 -a 3 ../korean_cypher.txt --hex-charset -1 eaebecedee -2 808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebf -3 808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebf -i ?1?2?3?1?2?3
```

运行结果如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bb348f30f06636a3.png)

**<br>**

**俄语密码破解**

虽然俄语字母是西里尔字母的变体….［[西里尔字符UTF-8编码表](http://www.utf8-chartable.de/unicode-utf8-table.pl?start=1024&amp;number=512)］

假设待破解密码为“сеть”，中文即“网络”的意思。该字符串由四个西里尔字母组成，cyrillic_cypher.txt文件内容如下图所示：

[![](https://p5.ssl.qhimg.com/t01a6cacbc7603a9147.png)](https://p5.ssl.qhimg.com/t01a6cacbc7603a9147.png)

参数命令如下：

```
./hashcat --potfile-disable --outfile-autohex-disable -m 0 -a 3 ../cyrillic_cypher.txt --hex-charset -1 d0d1d2d3d4 -2 808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebf -i ?1?2?1?2?1?2?1?2
```

破解结果如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014039443c03195a35.png)

**<br>**

**注意事项**

如果Hashcat无法输出正确的明文密码时，可以去掉命令中的“–outfile-autohex-disable”参数。比如说，以韩文密码的破解为例，去掉该参数之后，运行结果如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014a7b9f8e541f5840.png)

那么破解结果即为“ec 95 88”和“ec a0 84”这两个字。有python基础的同学可以直接用python将其进行转码：

[![](https://p2.ssl.qhimg.com/t01ff05b6903a46522e.png)](https://p2.ssl.qhimg.com/t01ff05b6903a46522e.png)

结果一目了然。为了方便大家查询各种语言文字的UTF-8编码，我给大家推荐一个网站［[传送门](http://www.utf8-chartable.de/)］。

**<br>**

**总结**

暴力破解的基本思想就是对所有可能出现的情况进行一一确认，直到所有的情况都验证完毕。所以如果密码破译者可以利用社会工程学等技巧获取到有关密码的更多信息，那么将会极大地提高密码破译的速度。不过大家也清楚，任何密码的破解都只是时间问题…

无论是阿拉伯语也好，日语也罢，我们都可以利用这样的方法来破解这些非英文字符的密码。那么，阿拉伯语密码和日语密码的破解就留给各位同学当作家庭作业啦！

<br>



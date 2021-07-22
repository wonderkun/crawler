> 原文链接: https://www.anquanke.com//post/id/84946 


# 【CTF攻略】VULNHUB - 如果你能抓住我 Writeup


                                阅读量   
                                **239696**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：jamesbower
                                <br>原文地址：[https://www.jamesbower.com/skydog-con-2016-ctf/](https://www.jamesbower.com/skydog-con-2016-ctf/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t013d224ee128d0aab9.jpg)](https://p5.ssl.qhimg.com/t013d224ee128d0aab9.jpg)



**翻译：**[**V1ct0r**](http://bobao.360.cn/member/contribute?uid=2665001095)

**稿费：200RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**



**0x00 Intro**

VULNHUB上面有非常多有趣的镜像资料，提供给我们练习和学习。本文我主要记录了今年11.9日发布的镜像题目 – SkyDog: 2016 – Catch Me If You Can 相关解题的思路和过程，希望与大家一同交流学习。

<br>

**0x01 Get Started!**

我们在VULNHUB上面下载这一期的镜像文件：

[https://www.vulnhub.com/entry/skydog-2016-catch-me-if-you-can,166/](https://www.vulnhub.com/entry/skydog-2016-catch-me-if-you-can,166/)

非常有趣的是本期是以《Catch Me If You Can》 – 逍遥法外 这部电影作为背景剧情的

如果有时间的话可以先看看这部电影，说不定对后面解题有所帮助

**Download (Mirror): **[https://download.vulnhub.com/skydog/SkyDogConCTF2016VBoxV10.ova](https://download.vulnhub.com/skydog/SkyDogConCTF2016VBoxV10.ova)

**Download (Torrent): **[https://download.vulnhub.com/skydog/SkyDogConCTF2016VBoxV10.ova.torrent](https://download.vulnhub.com/skydog/SkyDogConCTF2016VBoxV10.ova.torrent) 

下载完成后直接在VirtualBox中导入我们的镜像，启动即可

根据题目的提示我们一共需要拿到8个FLAGS

<br>

**0x02 Get Flags**

首先我们需要探测一下这个Server开放的端口服务，我们用Nmap对它进行一个全面扫描：

```
nmap.exe -T4 -A 192.168.56.102
```

[](http://chuantu.biz/t5/41/1478921191x1972047504.jpg))[![](https://p2.ssl.qhimg.com/t01a71ab7f318040570.jpg)](https://p2.ssl.qhimg.com/t01a71ab7f318040570.jpg)

我们看到了80端口和443端口是开放的，所以我们访问192.168.56.102

[![](https://p4.ssl.qhimg.com/t017e435d00d348a6b0.jpg)](https://p4.ssl.qhimg.com/t017e435d00d348a6b0.jpg)

看了一下网站页面以及源码似乎没得到什么新的提示，于是就开始常规的检测思路

由于是在本地，我直接用WVS对网站进行了扫描，从而来探测网站的目录结构和常见漏洞，结果发现存在一个列目录的漏洞：

[![](https://p5.ssl.qhimg.com/t0137810f9ac8e2097b.jpg)](https://p5.ssl.qhimg.com/t0137810f9ac8e2097b.jpg)

主要涉及了两个目录：



```
http://192.168.56.102/assets/
http://192.168.56.102/oldIE/
```

此外我们现在对网站的目录结构也有了大致的了解了

**Flag 1**

上面我们搜集到的唯一可以进一步看下去的信息就是存在的一个列目录漏洞。而第一个目录就是用于存放网站的一些资源文件，一些图片、css和js之类的，看了看没有什么特别的；第二个目录看上去比较奇怪，就点进去看了看，发现里面有一个html5.js的文件

```
http://192.168.56.102/oldIE/html5.js
```

[![](https://p3.ssl.qhimg.com/t0189fbb3b6f7d80729.jpg)](https://p3.ssl.qhimg.com/t0189fbb3b6f7d80729.jpg)

发现了这一串字符：

```
666c61677b37633031333230373061306566373164353432363633653964633166356465657d
```

根据Flag 1的提示

```
Flag#1 - "Don’t go Home Frank! There’s a Hex on Your House"
```

我们可以推测这就是Hex后的字符串

直接Hex Decoding下，发现果然是Flag

[![](https://p2.ssl.qhimg.com/t01c31ace15d600695f.jpg)](https://p2.ssl.qhimg.com/t01c31ace15d600695f.jpg)

```
flag`{`7c0132070a0ef71d542663e9dc1f5dee`}`
```

**Flag 2**

Flag 1中hash解密后发现是：nmap，于是我又使用Nmap对这个目标进行了更加深和全面的扫描：

```
nmap.exe 192.168.56.102 -vv -sV -p1-65535 -o details.txt
```

扫描结果之中又发现了一些有趣的信息：



```
22/tcp     closed ssh       reset   ttl 64
80/tcp     open   http      syn-ack ttl 64 Apache httpd 2.4.18 
443/tcp    open   ssl/http  syn-ack ttl 64 Apache httpd 2.4.18 
22222/tcp  open   ssh       syn-ack ttl 64 OpenSSH 7.2p2 Ubuntu 4ubuntu2.1
```

 在22222端口上开放了OpenSSH的服务，于是尝试连接

```
ssh root@192.168.56.102 -p 22222
```

在WARNING中发现了第二关的Flag

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a4b733f3b780391b.jpg)

```
Flag`{`53c82eba31f6d416f331de9162ebe997`}`
```

**Flag 3**

Flag 2的md5解密后是：encrypt

我们再看看本关的提示信息

```
Flag #3 Be Careful Agent, Frank Has Been Known to Intercept Traffic Our Traffic.
```

然后想到了我们之前用Nmap扫描的时候还发现了：

```
443/tcp   open   ssl/http syn-ack ttl 64 Apache httpd 2.4.18
```

于是访问 https://192.168.56.102

[![](https://p0.ssl.qhimg.com/t0179374678226e3d0e.jpg)](https://p0.ssl.qhimg.com/t0179374678226e3d0e.jpg)

发现证书是有问题的，然后进一步查看证书相关信息，在信息之中发现了Flag

[![](https://p1.ssl.qhimg.com/t0162dc20e98fa3b7e4.jpg)](https://p1.ssl.qhimg.com/t0162dc20e98fa3b7e4.jpg)

```
flag3`{`f82366a9ddc064585d54e3f78bde3221`}`
```

**Flag 4**<br>

Flag 3中的md5解密之后为：personnel

猜测是目录之类的，访问 http://192.168.56.102/personnel

[![](https://p3.ssl.qhimg.com/t01001fe0254ada9fe0.jpg)](https://p3.ssl.qhimg.com/t01001fe0254ada9fe0.jpg)

得到新的提示：

```
ACCESS DENIED!!! You Do Not Appear To Be Coming From An FBI Workstation. Preparing Interrogation Room 1. Car Batteries Charging....
```

这里说我们不是来自 FBI Workstation 的，加上访问被拒绝

这时想到了本关的提示：

```
Flag#4 - “A Good Agent is Hard to Find"
```

感觉这里Agent应该是双关（本意是：探员），按照这些提示通常的思路就是一个User-Agent的问题了，但是这个User-Agent又应该是什么呢？因为User-Agent是用来标识用户的操作系统、浏览器以及其版本信息等，联系到之前有个oldIE的目录，我又去在192.168.56.102//html5.js下搜索相关关键词：agent、FBI，发现找到了如下信息



```
/* maindev -  6/7/02 Adding temporary support for IE4 FBI Workstations */
/* newmaindev -  5/22/16 Last maindev was and idoit and IE4 is still Gold image -@Support doug.perterson@fbi.gov */
```

想到了伪造IE4的User-Agent信息

```
Mozilla/4.0 (compatible; MSIE 4.0; Windows NT)
```

MSIE 后面对应的数字就是版本号

修改后我们的User-Agent头之后发包，得到了Flag 4

[![](https://p2.ssl.qhimg.com/t0132ec14275d5fbae7.jpg)](https://p2.ssl.qhimg.com/t0132ec14275d5fbae7.jpg)

```
flag`{`14e10d570047667f904261e6d08f520f`}`
```

并且我们得到了一个新的提示：

```
Clue = new+flag
```

**Flag 5**

Flag 4的md5解密后为：evidence

然后根据上关最后的提示得到新提示：newevidence

发现这个提示依然是一个目录名，访问 http://192.168.56.102/newevidence

这里还是要用IE4的User-Agent

访问之后，弹出了一个框

[![](https://p5.ssl.qhimg.com/t017df2c1e4409a4fdb.jpg)](https://p5.ssl.qhimg.com/t017df2c1e4409a4fdb.jpg)

需要FBI的才能登陆，我们需要知道用户名和密码。而在上一关的html5.js文件中发现了一个邮箱：

doug.perterson@fbi.gov

即用户名的构成是：名字.姓氏

而我们在上一关登陆 http://192.168.56.102/personnel/

页面显示：

```
Welcome Agent Hanratty
```

我百度了下：Agent Hanratty

[![](https://p0.ssl.qhimg.com/t017ff2f2babec1ddb4.jpg)](https://p0.ssl.qhimg.com/t017ff2f2babec1ddb4.jpg)

得到这个探员的名字应该是：Carl Hanratty

所以这里用户名应该是：carl.hanratty

接下来就是密码了…继续看看这关的提示

```
Flag#5 - “The Devil is in the Details - Or is it Dialogue? Either Way, if it’s Simple, Guessable, or Personal it Goes Against Best Practices"
```

并不能想到任何有用的信息（可能因为没有看过这部电影的缘故），一顿搜索也无果后…索性休息下用直接百万级的大字典爆破试试，线程开得很高，跑了一会儿17万的样子时，居然出现了301，仿佛看到了希望

[![](https://p1.ssl.qhimg.com/t01c71b0c42cd3e7646.jpg)](https://p1.ssl.qhimg.com/t01c71b0c42cd3e7646.jpg)

decode后发现这里payload是：

carl.hanratty:Grace

尝试登陆，发现成功了！

[![](https://p2.ssl.qhimg.com/t01897a32cb7060ee5d.jpg)](https://p2.ssl.qhimg.com/t01897a32cb7060ee5d.jpg)

点击“Evidence Summary File” 发现请求了：http://192.168.56.102/newevidence/Evidence.txt 得到了本关的Flag：

```
flag`{`117c240d49f54096413dd64280399ea9`}`
```

同时我们还在登陆后的页面下载到了两个文件

一个是PDF：Invoice.pdf；一个是JPG：image.jpg

**Flag 6**

解密上一关flag中的md5，得到了： panam

再看看这一关的提示：

```
Flag #6 Where in the World is Frank?
```

找到Frank，这让我想到了数据取证人员通过包含元数据的Word文档找到了杀人犯，破掉了BTK杀人案件。那么上面我们得到的两个文件是否包含着某些信息呢？

首先看了看PDF的属性，并没有发现什么特别的，就打开这个文件，想看看内容有没有什么线索，最后Google到了文档中Stefan Hetzl是一个Steghide的作者，而Steghide是一个可以在图像,音频中隐藏数据的小工具，正好可以联系到我们的图片上

[![](https://p3.ssl.qhimg.com/t01432808662808bf2f.jpg)](https://p3.ssl.qhimg.com/t01432808662808bf2f.jpg)

这让我想起了前段时间的某个脑洞CTF，给了两张图片，但其实是通过其中一张图片里的人物的英文名找到了对应解密工具，解密第二个图片。所以，猜测这里应该也是这种思路。而密码恰好可以使用我们上一关flag的md5解密结果：panam

利用Steghide，发现图片里面隐藏了一个flag.txt文件



```
C:Documents and Settingsv1ct0r&gt;"C:Documents and Settingsv1ct0rDesktopstegh
idesteghide.exe" --info "C:Documents and Settingsv1ct0rDesktopimage.jpg" -p
 panam
"image.jpg":
  format: jpeg
  capacity: 230.1 KB
  embedded file "flag.txt":
    size: 71.0 Byte
    encrypted: rijndael-128, cbc
    compressed: yes
```

[![](https://p1.ssl.qhimg.com/t011d181f079f11213a.jpg)](https://p1.ssl.qhimg.com/t011d181f079f11213a.jpg)

接下来我们执行命令将flag.txt分离出来



```
C:Documents and Settingsv1ct0r&gt;"C:Documents and Settingsv1ct0rDesktopstegh
idesteghide.exe" --extract -sf "C:Documents and Settingsv1ct0rDesktopimage.
jpg" -p panam
wrote extracted data to "flag.txt".
```

得到Flag 6：

[![](https://p0.ssl.qhimg.com/t0186720cbdc4a214d2.jpg)](https://p0.ssl.qhimg.com/t0186720cbdc4a214d2.jpg)

```
flag`{`d1e5146b171928731385eb7ea38c37b8`}`
```

同时这个文本里面还给了我们新的线索：iheartbrenda

**Flag 7**

上一关Flag的md5解出来后为：ILoveFrance 在文本中也直接给出了

首先还是尝试了下是不是路径，发现这次不是了

这一关的提示是：

```
Flag #7 Frank Was Caught on Camera Cashing Checks and Yelling - I’m The Fastest Man Alive!
```

查了下这句话，发现Frank大叫的这句“I’m The Fastest Man Alive!”是来自于闪电侠的，这句话完整的是：My name is Barry Allen and I am the fastest man alive when I was a child , I saw my mother killed by … 看来又要开始脑洞了… “ILoveFrance” 不是目录的话最有可能的就是密码了，而我们唯一没有密码的就只有SSH了目前，所以尝试登陆去连接SSH，而用户名正好可以用那句话里的name：barryallen

```
ssh barryallen@192.168.56.102 -p 22222
```

发现不正确，想起来上一关完成时还有一个提示：iheartbrenda

尝试用这个密码去连接，发现成功连接上了！并在当前目录下找到了我们第七个Flag

[![](https://p3.ssl.qhimg.com/t0177c3b661f3567399.jpg)](https://p3.ssl.qhimg.com/t0177c3b661f3567399.jpg)

```
flag`{`bd2f6a1d5242c962a05619c56fa47ba6`}`
```

**Flag 8**

终于来到了最后一关了XD，上一关md5解出来是：theflash

还有在上一关我们flag的目录下有一个security-system.data的文件，推测最后一关应该是和这个文件有关了

我把这个文件下载下来，首先用binwalk分析下

[![](https://p2.ssl.qhimg.com/t01f9fc9df9505a7e0f.jpg)](https://p2.ssl.qhimg.com/t01f9fc9df9505a7e0f.jpg)

发现是ZIP文件，我们把这个文件解压出来

看了下文件内容出现了disk这样的字符，猜测可能是内存中的一些数据，我们利用Kali下集成的一款内存取证分析工具Volatility来看一看

这个工具的使用参数大家可以参考：http://tools.kali.org/forensics/volatility

首先查看下镜像信息

```
volatility -f security-system.data imageinfo
```

[![](https://p5.ssl.qhimg.com/t01d61740480ba48fe0.jpg)](https://p5.ssl.qhimg.com/t01d61740480ba48fe0.jpg)

这里我直接用notepad查看当前显示过的记事本内容

```
volatility -f security-system.data --profile=WinXPSP2x86 notepad
```

[![](https://p3.ssl.qhimg.com/t0173b54625b4497d59.jpg)](https://p3.ssl.qhimg.com/t0173b54625b4497d59.jpg)

发现最后那个text的内容比较特别，猜测是Hex过的

```
666c61677b38343164643364623239623066626264383963376235626537363863646338317d
```

Hex Decoding下，发现我们拿到了最后一个Flag！

```
flag`{`841dd3db29b0fbbd89c7b5be768cdc81`}`
```



**0x03 The End**

至此，我们已经成功完成了本期的挑战。不得不说整个题目感觉还是有些地方比较脑洞，可能是由于没看过这部电影的原因…题目本身需要的技巧不多，但还是可以作为练习以及帮助我们掌握一些基础，学习一些新姿势。当然解题方法不止一种，如果你还有什么好的思路和想法也欢迎一起学习交流。



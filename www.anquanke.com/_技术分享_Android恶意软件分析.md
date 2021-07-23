> 原文链接: https://www.anquanke.com//post/id/85225 


# 【技术分享】Android恶意软件分析


                                阅读量   
                                **109934**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：resources.infosecinstitute.com
                                <br>原文地址：[http://resources.infosecinstitute.com/android-malware-analysis-2/#download](http://resources.infosecinstitute.com/android-malware-analysis-2/#download)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p1.ssl.qhimg.com/t01d52f726a2f149684.png)](https://p1.ssl.qhimg.com/t01d52f726a2f149684.png)**

****

**翻译：**[**开个小号******](http://bobao.360.cn/member/contribute?uid=167004554)

**预估稿费：200RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>



**目的**

这个练习涵盖了技术分析Android恶意软件通过使用一个定制的恶意软件样本在Android设备上运行时,将会reverse shell给一个攻击者。我们将通过使用静态和动态分析技术分析完整功能应用程序。

**虚拟机使用： **Santoku Linux VM

**工具： **AVD Manager, ADB, Wireshark, dex2jar, apktool

**在这个实验中使用的分析工具：**bake_the_cake.apk, apktool, tcpdump,，

我们将通过创建一个模拟器，选择“Santoku-&gt;Development Tool”，然后点击“Android SDK Manager”。如下所示：

[![](https://p5.ssl.qhimg.com/t0117c3da4dc77bfca5.png)](https://p5.ssl.qhimg.com/t0117c3da4dc77bfca5.png)

上述步骤将打开下面的窗口：

[![](https://p5.ssl.qhimg.com/t01c185783a7e26eabf.png)](https://p5.ssl.qhimg.com/t01c185783a7e26eabf.png)

默认情况下，Santoku只有几个Android版本的图像。我们应该根据不同的要求来创建模拟器。如果您发现上面的图中，我们已经安装了“Android 4.4.2 ARM EABI V7ASystem ”。一切设置完毕，点击““Tools”菜单栏在顶部的窗口，然后单击“Manage AVDs”，如下图

所示。

[![](https://p5.ssl.qhimg.com/t012ac5b1408b68a36b.png)](https://p5.ssl.qhimg.com/t012ac5b1408b68a36b.png)

这将如下图所示：

“Android Virtual Device(AVD) Manager”窗口。

[![](https://p3.ssl.qhimg.com/t01d8c5bea7a18c1822.png)](https://p3.ssl.qhimg.com/t01d8c5bea7a18c1822.png)

正如你可以在上面的图中看到，我们已经配置了一个模拟器。现在，让我们创建我们选择的新的模拟器。点击“创建”，如图所示：

[![](https://p4.ssl.qhimg.com/t01d3ccd7810500d214.png)](https://p4.ssl.qhimg.com/t01d3ccd7810500d214.png)

现在，让我们来选择适当的选项，如下图所示：

[![](https://p2.ssl.qhimg.com/t0169f097764bda7cf3.png)](https://p2.ssl.qhimg.com/t0169f097764bda7cf3.png)

正如你可以在上面的图中看到，我们命名我们的模拟器为:“analysis_device。”于是，我们选择了具有“3.2寸HVGA”的设备能与更小的尺寸的模拟器。于是，我们选择了“Android 4.4.2-API Level19”作为我们的目标。CPU被选为ARM。内部存储容量为500 MB。最后，我们为SD卡提供了100 MB。

[![](https://p0.ssl.qhimg.com/t01962eef45c460a6f0.png)](https://p0.ssl.qhimg.com/t01962eef45c460a6f0.png)

检查完毕后，然后单击“确定”按钮完成设置。

如果您正在使用并按照上面的步骤完成后，你会看到一个额外的虚拟设备，如下图所示

[![](https://p4.ssl.qhimg.com/t0100eaeda2dfe4ea18.png)](https://p4.ssl.qhimg.com/t0100eaeda2dfe4ea18.png)

选择新创建的模拟器，然后单击“开始”按钮，你应该看到下面的对话框：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0138fca72cfadfff1d.png)

点击“启动”，并开始显示下面的进度条。

[![](https://p0.ssl.qhimg.com/t01e8b7827b34ee4d83.png)](https://p0.ssl.qhimg.com/t01e8b7827b34ee4d83.png)

要有耐心等待一段时间，因为第一次启动模拟器可能需要较长的时间来启动，如下图所示

[![](https://p5.ssl.qhimg.com/t01ceee26b5544eb3e2.png)](https://p5.ssl.qhimg.com/t01ceee26b5544eb3e2.png)

<br>

**静态分析**

静态分析涉及反编译应用程序并查看源代码，并对其进行分析，了解哪些恶意软件正在做什么。

让我们从分析AndroidManifest.xml文件开始。我们可以通过多种方式获得AndroidManifest.xml文件。让我们用apktool并使用下面所示的命令得到它。

```
apktoolÐbake_the_cake.apk
```

但是，我们这样做之前，我们应该确保我们使用的是最新版本的apktool，然后删除1.apk

如果现有apktool已经过时，它可能无法分解我们的目标APK文件。

下面是步骤：

删除 “1.apk” 在文件夹 “/home/infosec/apktool/framework/” 使用如下命令 /home/infosec/apktool/framework/1.apk

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b8b051dad25de26d.png)

现在，运行以下命令来分解apk文件：

```
java -jar apktool_2.1.1.jar d bake_the_cake.apk
```

[![](https://p5.ssl.qhimg.com/t0124928d88d46bba41.png)](https://p5.ssl.qhimg.com/t0124928d88d46bba41.png)

这个命令会创建一个apk文件名称的新文件夹。在我们的例子中，它是“ bake_the_cake ”。到该文件夹，如下面图中列出里面的文件和文件夹。

从运行以下命令，分析文件夹导航到新创建的bake_the_cake文件夹中。

```
$ CD bake_the_cake
```

然后，运行LS命令列出当前文件夹内的文件和文件夹。

[![](https://p2.ssl.qhimg.com/t019b70d37851a8ca53.png)](https://p2.ssl.qhimg.com/t019b70d37851a8ca53.png)

正如你可以在上面的图中看到，得到了它AndroidManifest.xml文件。让我们用下面的命令来查看它的内容，并查看是否有很有趣。

```
vim AndroidManifest.xml
```

[![](https://p3.ssl.qhimg.com/t01bc32775fc2880e6a.png)](https://p3.ssl.qhimg.com/t01bc32775fc2880e6a.png)

看着上面的内容，没有任何可疑。即使这个程序是不要求任何危险的权限。联网是这个应用程序所需的唯一权限，但是这并不能证明它是恶意的，因为大多数的应用程序，需要的大部分它们的功能是Internet权限。

如果您正在使用vim编辑器，按打开文件进行CTRL + C，然后输入！Q：关闭。

因此，我们需要做进一步的分析，以确认应用程序有任何恶意行为。

让我们深入挖掘通过反编译使用dex2jar＆JD-GUI应用程序。让我们先解压缩程序，如下面的图。

```
$unzip bake_the_cake.apk
```

[![](https://p0.ssl.qhimg.com/t01299e79125af17aba.png)](https://p0.ssl.qhimg.com/t01299e79125af17aba.png)

上述命令应在当前目录中创建附加的文件和文件夹。您可以使用“检查它的ls -l”命令，如图：

[![](https://p0.ssl.qhimg.com/t01720e650f64c68876.png)](https://p0.ssl.qhimg.com/t01720e650f64c68876.png)

正如我们在上面的图中看到，我们从“ classes.dex”文件中提取。classes.dex文件是从开发人员编写Java代码。本来.java文件是使用传统的Java编译器javac的编译。此步骤生成.class文件。这些类文件进一步给予DX工具，它产生一个Dalvik虚拟机（DVM）中运行classes.dex文件。Classes.dex文件是编译的二进制，因此，我们不能以明文阅读。我们可以用dex2jar命令行工具来对DEX文件转换成一个jar文件。这些JAR文件可以用任何传统的Java反编译器，如JD-GUI被反编译。这是为了理解应用程序的源代码的一个重要步骤。dex2jar工具预装在Santoku.

我们可以运行以下命令来使用dex2jar：

```
$ dex2jar classes.dex
```

[![](https://p5.ssl.qhimg.com/t01e141bad5e65da35e.png)](https://p5.ssl.qhimg.com/t01e141bad5e65da35e.png)

正如我们在上面的图中看到，classes.dex文件已输出为classe_dex2jar.jar文件。

现在，我们可以使用任何传统的Java反编译器，从上面的jar文件得到的Java文件。让我们用JD-GUI，Santoku-&gt;Reverse Engineering：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018e5c9cc8725863ff.png)

点击JD的GUI，它就会打开工具，如下面的图。

[![](https://p3.ssl.qhimg.com/t01cecb3b49db9515b7.png)](https://p3.ssl.qhimg.com/t01cecb3b49db9515b7.png)

正如前面提到的，我们将使用这个工具从jar文件中获得的Java文件。因此，定位到““File-&gt;open”，然后选择classes_dex2jar.jar文件。这看起来如下所示。

[![](https://p2.ssl.qhimg.com/t0173f5d07539b2d7f5.png)](https://p2.ssl.qhimg.com/t0173f5d07539b2d7f5.png)

点击open：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016da721c574a26906.png)

不错，我们可以看到包名com.infosecinstitute.analyze_me。我们还可以看到三个不同的类，其中包括MainActivity。我们点击MainActivity并浏览它。

浏览MainActivity显示了很多有趣的信息。首先，让我们来看看下面的一段代码。

[![](https://p1.ssl.qhimg.com/t0144d1bbed3b76ff44.png)](https://p1.ssl.qhimg.com/t0144d1bbed3b76ff44.png)

有趣的是，有三种方法在上述的一段代码。getReverseShell()，因为它可能会作出与给出了一个 reverse shell给攻击者一个方法的调用会出现危险。探究在此之前，让我们来看看其他两种方法copyFile()和changefilepermissions()。

下面的代码段是定义copyFile()方法。

[![](https://p0.ssl.qhimg.com/t019db343a6c7c28767.png)](https://p0.ssl.qhimg.com/t019db343a6c7c28767.png)

这种方法实质上是复制一个文件名为NC的应用程序的资产目录/data/data/com.infosecinstitute.analyze_me/app_files/目录。目标目录本质上是应用程序的设备上的沙箱。

让我们明白下这是怎么搞的：

首先，我们看到的方法调用copyFile("NC"); 在前面的代码片段。参数已经传递给localAssetManager.open()，它正在被打开。然后，该目标文件路径已建成.getPackageName(); 给出当前包名。接下来的几行用于将文件复制到目标。

由于文件名是“NC”，也可能是APK内包装netcat的二进制文件。让我们切换到分析在终端上的文件夹，并检查从解压APK资产文件夹，查看属性。

下图显示了与这个名字的文件“NC”位于assets文件夹中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01957a502fc13bc5ef.png)

我们还使用文件命令来查看的文件类型。运行“文件NC ”在assetss的文件夹中。输出应该如下图所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t018a2a493dfb12bed0.png)

以上输出显示，该文件是为ARM架构的ELF二进制版本。这证实了assetss文件夹内的文件可能是专为Android设备的可执行文件。

现在，让我们切换回JD-GUI，看看下一个方法changefilepermissions()。下面这段代码显示了该方法的定义。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016bb2aeef1b93c9de.png)

以上方法似乎正在改变被复制到netcat的二进制文件权限“app_files”文件夹前面。“chmod 755 &lt;文件名&gt;”命令赋予可执行权限到指定文件。

如果该文件的权限已被更改，我们可以验证。启动我们前面创建的仿真器，安装应用程序并启动它。要安装应用程序，切换到你的终端，并确保你在里面分析，其中目标apk文件所在的文件夹。

然后运行以下命令。

```
“adb install bake_the_cake.apk”
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01dcdbf28d2b18cd33.png)

一旦安装后，请确保您启动的应用程序使我们看到代码会被执行。

现在，

```
$adb shell
```

[![](https://p5.ssl.qhimg.com/t0137a1952edad1e059.png)](https://p5.ssl.qhimg.com/t0137a1952edad1e059.png)

切换到使用目标包“CD /data/data/com.infosecinstitute.analyze_me/”并运行“LS”的命令，如下面的图。

[![](https://p5.ssl.qhimg.com/t01e139d61cd5007bc1.png)](https://p5.ssl.qhimg.com/t01e139d61cd5007bc1.png)

正如我们在上面的图中看到，在app_files目录中创建。现在，让我们浏览到该目录，并检查使用的netcat的文件权限“的ls -l”命令，如图下图。

[![](https://p0.ssl.qhimg.com/t01708f47861f647c65.png)](https://p0.ssl.qhimg.com/t01708f47861f647c65.png)

正如你在上图中看到，NC程序得到了可执行的权限。

一旦完成，按Ctrl + C，退出adbshell

最后，还有一个需要研究探索的方法。让我们切换回JD-GUI和检查getReverseShell（）方法，看看它在做什么。

以下是代码片段。

[![](https://p5.ssl.qhimg.com/t01e06adc2b6f1089f9.png)](https://p5.ssl.qhimg.com/t01e06adc2b6f1089f9.png)

上面的代码片段显示，该应用程序使用调用Runtime.getRuntime().EXEC()，通过端口5555的IP地址10.0.2.2连接，提供一个reverse shell给攻击者。此连接正在使用的是捆绑在一起的netcat二进制的apk文件的。

给定样品的这种静态分析的结论如下。

该应用程序是恶意的

它配备了APK文件中捆绑的netcat的二进制文件。

当用户打开应用程序，它提供了反向的外壳给攻击者（10.0.2.2）

<br>

**动态分析**

当我们试图执行静态分析,可能代码混淆让开发人员很头疼。在这样的情况下，依靠静态分析可能是麻烦的。所以说要用到动态分析。动态分析包括：：分析运行的应用程序的步骤。通常,这个过程检查API调用,网络电话等本节将展示如何使用tcpdump对Android设备进行网络流量分析。

让我们先来安装和启动模拟器上的应用程序。这个应用程序看起来应该如下面：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0186205b7350345fa9.png)

应用程序运行正常。我们可以把 tcpdump加载程序这可以使用来完成ADB推命令，如下面的图。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01181fcbc6fae451cb.png)

 上面的命令/data/local/tmp目录是可写在Android设备上的目录的，

现在我们在模拟器上，并检查文件/data/local/tmp 

[![](https://p2.ssl.qhimg.com/t010f06cf1cd2e95f37.png)](https://p2.ssl.qhimg.com/t010f06cf1cd2e95f37.png)

如果您发现上面的输出，tcpdump目前没有可执行的权限。

所以，让我们给tcpdump的可执行权限，如下面的图。

```
#chmod 755 tcpdump
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bcf711263ac4337a.png)

现在，tcpdump的二进制文件是可执行的。让我们开始它并使用以下命令捕获的数据包。

```
./tcpdump -v -s 0 -w packets.pcap
```

[![](https://p2.ssl.qhimg.com/t01d46add100033a3a5.png)](https://p2.ssl.qhimg.com/t01d46add100033a3a5.png)

正如我们在上面的图中看到，我们捕获的数据包并将其保存到一个文件名为packets.pcap。

现在，通过点击模拟器上的后退按钮关闭该应用程序一次，并启动了回去。这仅仅是保证了应用程序的第一个屏幕运行和tcpdump的通信权。应用程序只有一个页面,所以在我们的案例中是关闭和重新启动就够了一旦这样做，我们可以停止按捕获的数据包CTRL + C，如下面的图中的终端。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f676d5d2f551ef9e.png)

现在，我们可以在本地计算机，拉这些数据包进行进一步分析。按Ctrl + C，然后用拉他们从adb shell首先退出“adb”命令，如图下图。

```
#adb pull /data/local/tmp/packets.pcap
```

[![](https://p1.ssl.qhimg.com/t012f3e4eb1369e08c2.png)](https://p1.ssl.qhimg.com/t012f3e4eb1369e08c2.png)

我们拉到捕获的数据包。现在，我们需要分析它。我们将使用Wireshark的分析这些数据包。

在Santoku -&gt; Wireless Analyzers -&gt; Wireshark：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d476c601068fdc6f.png)

启动Wireshark的，然后进入“File-&gt;Open” to open the packets.pcap file。如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01021796e76ca04cd8.png)

你应该看到Wireshark的数据包，如下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cb16c3688980391a.png)

嗯，有分析很多的包，我们需要通过过滤我们不必要的数据包。可以应用以下过滤器除去那些有“PSH ACK”标志的数据包。

因为现在在找一个握手包

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e5ae1421126eeb57.png)

在wireshark里面中向下滚动呈现以下两个包

[![](https://p2.ssl.qhimg.com/t01faa6c411e73ea051.png)](https://p2.ssl.qhimg.com/t01faa6c411e73ea051.png)

正如你在上图中看到，有一个SYN报文从10.0.2.15（模拟器）到10.0.2.2（(Santoku）。

注：模拟器需要10.0.2.2作为该模拟器运行时主机的地址。恶意软件已与该地址没有互联网，地址是模拟攻击者的IP地址创建。

点击上述分组还示出了端口监听攻击者的机器上是5555这是恶意软件试图连接到该端口。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t015092ef0b11d21638.png)

这给了我们一个思路，应用程序正试图使从IP 10.0.2.2通过TCP端口5555进行远程连接

但是，下一个分组表示连接已被复位（我们得到了RST）。

让我们再次尝试相同的模拟攻击者的服务器使用netcat 

如下：

[![](https://p3.ssl.qhimg.com/t0163a5a8062056c5aa.png)](https://p3.ssl.qhimg.com/t0163a5a8062056c5aa.png)

正如我们在上面的图中看到，我们正在监听端口5555。

现在，启动tcpdump在虚拟器上，包保存到一个文件名为packets2.pcap。然后，启动目标应用程序产生的流量。当你这样做，你将收到一份关于netcat的监听器 reverse shell 

。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0176f413bf43292728.png)

停止捕获，如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011654e8c744c9db14.png)

导出数据试用ADB：

[![](https://p2.ssl.qhimg.com/t01e85bad84ab1a286b.png)](https://p2.ssl.qhimg.com/t01e85bad84ab1a286b.png)

再次，Wireshark中打开PCAP文件，并查找在捕获的数据包的三次握手。下图显示了三次握手。

[![](https://p1.ssl.qhimg.com/t01c5f65fcedf2aa139.png)](https://p1.ssl.qhimg.com/t01c5f65fcedf2aa139.png)

正如我们在上面的图中看到，10.0.2.15已经开始与一个SYN报文的三次握手。下图显示了该应用程序正在试图建立在端口5555到攻击者的服务器的连接。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b43f52f9a494e55a.png)

点击第二个数据包，你应该看到从Santoku（10.0.2.2）来响应。你要注意到源端口5555。

[![](https://p5.ssl.qhimg.com/t018a37e31924fa2dc9.png)](https://p5.ssl.qhimg.com/t018a37e31924fa2dc9.png)

最后，点击3号包看到注定了Santoku计算机上的端口5555的源发送的ACK包。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bc2d72d456b831f9.png)

这证实了建立了连接攻击者的服务器。

由于我们使用的两面的netcat，它采用明文传输的，我们甚至可以看到通信。

要检查这一点，让我们再一次重复上述过程。

开始santoku netcat的监听器

运行tcpdump和包保存到一个文件名为packets3.pcap

启动和运行产生的流量应用。

下图显示的tcpdump捕获的数据包，并将其写入packets3.pcap。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f476255af5726416.png)

当在santoku  shell 上，通过输入cat /proc/cpuinfo ，如下面的图命令：

[![](https://p0.ssl.qhimg.com/t0159ee2351bbaa7768.png)](https://p0.ssl.qhimg.com/t0159ee2351bbaa7768.png)

停止捕获并导出显示在下面的图中的报文：

```
$adb pull /data/local/tmp/packets.pcap
```

[![](https://p1.ssl.qhimg.com/t01ff2102fe2f87ba02.png)](https://p1.ssl.qhimg.com/t01ff2102fe2f87ba02.png)

现在，打开在Wireshark的数据包，并寻找我们输入的字符串。这可以如下面的图来完成。Edit -&gt; Find Packet。

[![](https://p5.ssl.qhimg.com/t01bef7c00d640fd5b6.png)](https://p5.ssl.qhimg.com/t01bef7c00d640fd5b6.png)

现在选择字符串，然后输入“cpuinfo”到文本字段。请确保你选择““packet bytes”中搜索，最后单击“查找”。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0119523199efa19a77.png)

现在，我们应该看到了我们正在寻找的内容包。  选择数据包右键单击：

[![](https://p0.ssl.qhimg.com/t01bceb1450be223b11.png)](https://p0.ssl.qhimg.com/t01bceb1450be223b11.png)

以下选项应显示。点击“Follow TCP Stream”

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01aed4ccef7512e628.png)

这会打开下面的窗口在这里将能够看到的恶意软件和攻击者的服务器之间发送的消息。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0106e6777cec5daa02.png)

<br>

**结论**

实验基本覆盖了Android的安全分析了恶意软件使用静态和动态分析技术的基本概念。虽然自定义恶意软件的应用已经显示出一个Android恶意软件（reverse shell）的一个特点，你会发现更多的恶意功能，如窃取数据并将其发送给攻击者的服务器。

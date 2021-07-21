> 原文链接: https://www.anquanke.com//post/id/208039 


# 同时运行在Windows和Linux的勒索软件Tycoon分析


                                阅读量   
                                **209674**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：
                                <br>原文地址：[https://blogs.blackberry.com/en/2020/06/threat-spotlight-tycoon-ransomware-targets-education-and-software-sectors](https://blogs.blackberry.com/en/2020/06/threat-spotlight-tycoon-ransomware-targets-education-and-software-sectors)

译文仅供参考，具体内容表达以及含义原文为准

![](https://p5.ssl.qhimg.com/t01bbf60e04f3bb6786.jpg)



## 一、概述

Tycoon是一个同时针对Windows和Linux的多平台Java勒索软件，至少从2019年12月起就在野外观察到其恶意活动。该勒索软件以木马化的Java运行时环境（JRE）的形式部署，并利用复杂的Java映像格式保持其隐蔽性。

我们观察到，Tycoon勒索软件背后的威胁行为者已经使用了具有较强针对性的交付机制，尝试将恶意软件渗透到教育和软件行业的中小型企业和机构中，勒索软件将对服务器中的文件进行加密并勒索赎金。但是，由于加密过程重复使用了公开的RSA私钥，因此针对较早版本的勒索软件，用户可能无需支付赎金，直接恢复数据。



## 二、交付

BlackBerry研究与情报团队与KPMG英国网络响应服务团队最近共同发现了一种使用Java语言编写的新型勒索软件。勒索软件主要针对组织发起有针对性的攻击，特别是针对域控服务器和文件服务器进行攻击，锁定系统管理员帐户进行，使其无法登录系统。我们在对受感染系统进行取证调查后，发现最初的入侵是通过接入互联网的RDP中间机来进行的。

下图展示了攻击者是如何成功获得初始访问，并开始感染整个区域内的系统。

攻击时间轴：

![](https://p5.ssl.qhimg.com/t0177e7132337a3a5ce.png)

由于接入互联网的RDP服务器已经被还原，因此我们无法在这台主机上进行威胁分析。但是，通过我们对受害主机的分析表明，攻击者使用了一些不同寻常的技术，值得我们的关注。

1、为了在受害者的主机上实现持久性，攻击者使用了一种名为“映像文件执行选项”（IFEO，映像劫持）注入的技术。IFEO设置存储在Windows注册表中，这些设置让开发人员可以选择在目标应用程序执行期间通过调试应用程序的附件来对软件进行调试。

2、勒索软件在操作系统的Microsoft Windows On-Screen Keyboard（OSK，屏幕键盘）功能执行了后门操作。

用于执行后门程序的注册表项：

![](https://p5.ssl.qhimg.com/t015769011953ded955.png)

3、攻击者使用ProcessHacker实用程序禁用了组织的反恶意软件解决方案，并更改了Active Directory服务器的密码，这将导致受害者无法访问其系统。

4、包括Java库和执行脚本在内的大多数恶意文件都带有时间戳，并且文件的时间戳均为2020年4月11日15:16:22。

文件的时间戳：

![](https://p3.ssl.qhimg.com/t012c1da9d6060f0ea5.png)

最后，攻击者执行了Java勒索软件模块，对所有文件服务器进行了加密，包括连接到网络的备份系统。



## 三、执行

Tycoon勒索软件以ZIP压缩包的形式出现，其中包含木马化的Java运行时环境（JRE）编译。该恶意软件被编译为Java映像文件（JIMAGE），位于编译目录下的`libmodules`。

JIMAGE是一种特殊的文件格式，用于存储自定义JRE映像，该映像设计用于Java虚拟机（JVM）在运行时使用。它包含支持特定JRE编译的所有Java模块的资源和类文件。该格式最早是在Java 9版本中引入，并且没有太多的记录。与流行的Java格式（JAR）不同，JIMAGE主要是JDK内部使用，很少被开发人员使用。

恶意的“modules”文件，JIMAGE格式使用以0xDADAFECA签名开头的标头：

![](https://p5.ssl.qhimg.com/t015ef81cb5d27d5346.png)

OpenJDK9 jimage实用程序可以提取和反编译Java映像文件：

```
$ ./jimage --help
Usage: jimage &lt;extract|recreate|info|list|verify&gt; &lt;options&gt; jimage...
```

在提取后，勒索软件的映像中包含一个名为“tycoon”的项目，其中包含3个模块。

ZIP压缩包的内容（左图）和反编译的Java模块中JIMAGE的结构（右图）：

![](https://p0.ssl.qhimg.com/t01bbdfebb2184c92ab.png)

勒索软件是通过执行Shell脚本触发的，该脚本使用`java -m`命令运行恶意Java模块的Main函数。

该勒索软件的JRE编译中，包含此脚本的Windows和Linux脚本，这表明该威胁也同样可以针对Linux服务器。

用于执行勒索软件的Shell脚本和Java“发行版”文件：

![](https://p2.ssl.qhimg.com/t014a87100d3f7eb526.png)



## 四、配置

恶意软件的配置存储在项目的`BuildConfig`文件中，其中包含以下信息：

1、攻击者的电子邮件地址；

2、RSA公钥；

3、勒索提示信息；

4、白名单列表；

5、要执行的Shell命令列表。

配置的变量名称和示例值如下：

```
EMAIL_1：“dataissafe[at]protonmail[.]com”
EMAIL_2：“dataissafe[at]mail[.]com”
FILE_EXTENSION：“thanos”
PUBLIC_KEY：
“——-BEGIN PUBLIC KEY——- nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDa+whJSxr9ngcD1T5GmjDNSUEYngz5esbym
vy4lE9g2M3PvVc9iLw9Ybe+NMqJwHB8FYCTled48mXQmCvRH2Vw3lPkAnTrQ4zbVx0fgEsoxekqt
b3GbK2NseXEeavCi5lo5/jXZi4Td7nlWTu27CluyxRSgvnL0O19CwzvckTM91BKwIDAQABn
——-END PUBLIC KEY——-”
NUMBER_OF_KEYS_PER_ROOT_PATH：100
CHUNK_SIZE：10485760L (10 MB)
ENCRYPTION_PATTERN：true, true, false, false, false, true, true, false, false, false, false, false, false, false, false, false
HEADER：0x68, 0x61, 0x70, 0x70, 0x79, 0x6E, 0x79, 0x33, 0x2E, 0x31 (ASCII for “happyny3.1”)
DIR_BLACKLIST：”Windows”, “Boot”, “System Volume Information”, “Program FilesCommon FilesMicrosoft Shared”, “Program FilesCommon FilesSystem”, “Program FilesCommon FilesServices”, “Program FilesCommon FilesSpeechEngines”, “Program Files (x86)Common Filesmicrosoft shared”, “Program Files (x86)Common FilesSystem”, “Program Files (x86)Common FilesServices”, “Program Files (x86)Common FilesSpeechEngines”, “Program FilesInternet Explorer”, “Program FilesInternet Explorer”, “Program FilesWindows Mail”, “Program FilesWindows Media Player”, “Program FilesWindows Photo Viewer”, “Program FilesWindows Sidebar”, “Program FilesDVD Maker”, “Program FilesMSBuild”, “Program FilesReference Assemblies”, “Program FilesWindows Defender”, “Program FilesWindows NT”, “Program Files (x86)Internet Explorer”, “Program Files (x86)Windows Mail”, “Program Files (x86)Windows Media Player”, “Program Files (x86)Windows Photo Viewer”, “Program Files (x86)Windows Sidebar”, “Program Files (x86)MSBuild”, “Program Files (x86)Reference Assemblies”, “Program Files (x86)Windows Defender”, “Program Files (x86)Windows NT”, “ProgramDataMicrosoft”, “UsersAll Users”
EXTENSION_BLACKLIST：”mui”, “exe”, “dll”, “lolz”
FILE_BLACKLIST：”decryption.txt”, “$Mft”, “$Mft (NTFS Master File Table)”, “$MftMirr”, “$LogFile”, “$LogFile (NTFS Volume Log)”, “$Volume”, “$AttrDef”, “$Bitmap”, “$BitMap”, “$BitMap (NTFS Free Space Map)”, “$Boot”, “$BadClus”, “$Secure”, “$Upcase”, “$Extend”, “$Quota”, “$ObjId”, “$Reparse”, “$Extend”, “bootmgr”, “BOOTSECT.BAK”, “pagefile.sys”, “pagefile.sys (Page File)”, “boot.ini”, “bootfont.bin”, “io.sys”
EXEC_COMMANDS：”vssadmin delete shadows /all /quiet”, “wmic shadowcopy delete”, “bcdedit /set `{`default`}` bootstatuspolicy ignoreallfailures”, “bcdedit /set `{`default`}` recoveryenabled no”, “wbadmin delete catalog -quiet”, “netsh advfirewall set currentprofile state off”, “netsh firewall set opmode mode=disable”
TXT：勒索提示信息（参见威胁指标）
```

BuildConfig文件截图：

![](https://p3.ssl.qhimg.com/t01f8e8f0549bc26782.png)



## 五、行为

在执行后，该恶意软件将运行`BuildConfig`文件中一组指定的Shell命令：

```
vssadmin delete shadows /all /quiet
wmic shadowcopy delete
bcdedit /set `{`default`}` bootstatuspolicy ignoreallfailures
bcdedit /set `{`default`}` recoveryenabled no
wbadmin delete catalog -quiet
netsh advfirewall set currentprofile state off
netsh firewall set opmode mode=disable
```

将使用系统UUID值的SHA-256哈希值中的前四个字节，为每个受害者生成一个`install_id`值。为了获取UUID，恶意软件会执行以下wmic命令：

```
wmic csproduct get UUID
```

加密路径列表可以作为参数传递。或者，恶意软件将生成系统中所有根路径的列表。这样一来，就会为路径列表中的每个项目创建一个单独的加密线程。

在加密过程完成后，恶意软件将通过覆盖每个加密路径中的已删除文件，来确保文件不会被恢复。在这里，是使用嵌入式Windows实用程序cipher.exe来完成这项任务。

安全地删除原始文件：

![](https://p2.ssl.qhimg.com/t01cfc9c4b7637862d9.png)



## 六、文件加密

这些文件使用AES-256算法的Galois/Counter（GCM）模式进行加密，其中带有16字节长度的GCM验证标签，以确保数据完整性。使用`java.security.SecureRandom`函数，为每个加密块生成一个12字节长度的初始化向量（IV）。加密块的大小在`BuildCofig`中指定，设置为10MB，而模式设置中则指定了要处理文件块的模式。对于较大文件，可以跳过其中的一部分，这样不仅能达到破坏文件确保其无法使用的目的，同时还能加快加密的过程。

对于每个加密路径，都使用`java.security.Secure.Random`函数生成AES-256密钥数组。每个路径的最大密钥数是在`BuildConfig`中配置的，并且在不同样本中可能有所不同。每个文件（如果文件大于块的大小，则针对文件块进行操作）使用不同的AES密钥进行加密，然后使用攻击者的RSA-1024公钥加密，保存在每个块的元数据块中。

生成AES密钥：

![](https://p3.ssl.qhimg.com/t0166255501006644d8.png)

添加到每个加密块的元数据包含以下内容：

1、`BuildConfig`中指定的标头值；

2、块索引（8字节）；

3、块大小（8字节）；

4、每个块生成的AES IV（12字节）；

5、AES GCM标签（16字节）；

6、RSA加密的AES密钥方案（128字节），其中包括：受害者ID（4字节）、AES密钥（32字节）、受害者ID和AES密钥的SHA-512哈希值（64字节）。

其中突出显示的是加密文件中的元数据：

![](https://p0.ssl.qhimg.com/t019a34d1db0f214f78.png)

由于使用非对称RSA加密算法对生成的AES密钥进行加密，因此要解密文件，必须得到攻击者拥有的RSA私钥。尽管从理论上来讲可以爆破1024位RSA密钥，但这一过程需要非常强大的算力，基本无法实现。

但是，一位在BleepingComputer论坛上寻求帮助的受害者发布了一个RSA私钥，该密钥应该是来自已经支付赎金的受害者。事实证明，这个密钥可以成功解密Tycoon勒索软件早期版本加密的某些文件，早期版本会为加密文件添加`.redrum`扩展名。

解密的AES密钥元数据，其中`install_id`为红色，AES密钥为绿色，SHA-512哈希值为蓝色：

![](https://p0.ssl.qhimg.com/t016b83e0868692da3b.png)

使用解密的AES密钥恢复`.redrum`文件：

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

但遗憾的是，该解密密钥不适用于最新的“happyny3.1”版本，该版本向加密的文件添加的`.grinch`和`.thanos`扩展名。



## 七、总结

恶意软件编写者一直在寻找新的隐藏方式，他们正在从传统的混淆技术转移到不常见的编程语言和难懂的数据格式。我们已经看到，使用Java和Go这类语言编写的勒索软件数量有了大幅度的增长。这个勒索软件则是专门滥用Java中的JIMAGE格式来创建自定义的恶意JRE编译，这也是我们遇到的利用这种方式的第一个样本。

Tycoon至少已经在野外活跃了六个月之久，但受害人数似乎有限。这表明，该恶意软件可能有比较强的针对性。同时，它也可能是在恶意活动中使用的多个勒索软件之中的一个，可能会在特定环境中选用该勒索软件。

根据某些电子邮件地址的交集、勒索提示信息以及加密文件的命名格式，我们判断Tycoon与Dharma/CrySIS勒索软件之间存在联系。



## 八、威胁指标（IoC）

### <a class="reference-link" name="8.1%20JIMAGE%E6%A8%A1%E5%9D%97%EF%BC%88libmodules%EF%BC%89"></a>8.1 JIMAGE模块（libmodules）

```
eddc43ee369594ac8b0a8a0eab6960dba8d58c0b499a51a717667f05572617fb
```

### <a class="reference-link" name="8.2%20%E9%82%AE%E7%AE%B1%E5%9C%B0%E5%9D%80"></a>8.2 邮箱地址

```
pay4dec[at]cock[.]lu
dataissafe[at]protonmail[.]com
dataissafe[at]mail[.]com
foxbit[at]tutanota[.]com
moncler[at]tutamail[.]com
moncler[at]cock[.]li
relaxmate[at]protonmail[.]com
crocodelux[at]mail[.]ru
savecopy[at]cock[.]li
bazooka[at]cock[.]li
funtik[at]tutamail[.]com
proff-mariarti[at]protonmail[.]com
```

### <a class="reference-link" name="8.3%20%E5%8A%A0%E5%AF%86%E6%96%87%E4%BB%B6%E6%89%A9%E5%B1%95%E5%90%8D"></a>8.3 加密文件扩展名

```
thanos
grinch
redrum
```

### <a class="reference-link" name="8.4%20%E5%8A%A0%E5%AF%86%E6%96%87%E4%BB%B6%E7%AD%BE%E5%90%8D"></a>8.4 加密文件签名

```
happyny3.1
redrum3_0
```

### <a class="reference-link" name="8.5%20RSA%E5%85%AC%E9%92%A5%EF%BC%88happyny3.1%E7%89%88%E6%9C%AC%EF%BC%89"></a>8.5 RSA公钥（happyny3.1版本）

```
-----BEGIN PUBLIC KEY-----

MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDa+whJSxr9ngcD1T5GmjDNSUEY
gz5esbymvy4lE9g2M3PvVc9iLw9Ybe+NMqJwHB8FYCTled48mXQmCvRH2Vw3lPkA
TrQ4zbVx0fgEsoxekqtb3GbK2NseXEeavCi5lo5/jXZi4Td7nlWTu27CluyxRSgv
L0O19CwzvckTM91BKwIDAQAB

-----END PUBLIC KEY-----
```

### <a class="reference-link" name="8.6%20RSA%E7%A7%81%E9%92%A5%EF%BC%88redrum3_0%E7%89%88%E6%9C%AC%EF%BC%89"></a>8.6 RSA私钥（redrum3_0版本）

```
-----BEGIN RSA PRIVATE KEY-----

MIICXQIBAAKBgQCyNELzNaPcGBlt2YEARamc+a+uyM8/mRadrMLLQ9tuzkppvdWI
iM/LH+xATZUgByknwzaMtRQZi6R2pQ8nBG6DxNtdhla33L+njQLTW+7wo1tSaaJz
6Of0FvCUZNPZ0mF5OrJO+Z6ZfDxafcwv653Ii7aTwaKlhjFoZijBMrA43wIDAQAB
AoGAPJ+I0yJBX0OXiwY+W3BXdj5+5LANyS30QqmeDvZDtRtat0RMW0lnn0t53JpI
DABDoPJJIW8MqnAWAALA994LFhk9jUtJTUgwsViyKL/Q/dOCeBPJU3xyXNkqhmCN
ImP4v7DxjvWp1pomrIIRCW68GkbB+cSGyLAzUo+1KHVh6LECQQDdL26UsVNsNYTX
rfv6BZItGO1HJHYTiz0cI82n4woZY2fS2lpBDEvy3Rl8E4Y7F9tQby4odDLHi/9l
RCeoif45AkEAzkDsPGauMmWsPXAbXrjzq3/0+MWgh7Vd8Gpgn83QUYjTO2RxtE1n
zAYzTLrFFtM8zmCAubpKM1dyi4Xs7hlv1wJBAJD5ofV8NT3b5nKn61z5gdJlYEEd
OPeecDOdlBLS0a/KZCbkT/wK300UdrvI4FajUHDsLsj9QLtim8f4YDYsHKECQQCX
R40+XD3mnyZvRbv9hQDMyKSglyvAfimxvgSzEZ17QDVWubygd6nrPpz/6XnH3RYb
dTLVhysHb1uHtKpslWGvAkAf0kivk9miSFnVeoO1XZumRAwrhTh6Rxhkg6MJCLBP
ThoY7wYXmV9zNPo02xYTvZlyhwnWspz4Kx4LsUutWmBs

-----END RSA PRIVATE KEY-----
```

### <a class="reference-link" name="8.7%20%E5%8B%92%E7%B4%A2%E6%8F%90%E7%A4%BA%E4%BF%A1%E6%81%AF"></a>8.7 勒索提示信息

```
Hello!

All your documents, photos, databases and other important files have been ENCRYPTED! Do you really interested to restore your files?

If so, you must buy decipher software and private key to unlock your data!
Write to our email - %s and tell us your unique %s
We will send you full instruction how to decrypt all your files.
In case of no answer in 24 hours write us on additional e-mail address - %s

========================================================================================================================
FAQ FOR DECRYPTION YOUR FILES:
========================================================================================================================

* WHATS HAPPENED ???  

Your files are NOT DAMAGED! Your files have been modified and encrypted with strong cipher algorithm. This modification is reversible. The only way to decrypt your files is to purchase the decipher software and private key. Any attempts to restore your files with the third-party software will be fatal for your files, because would damage data essential for decryption !

Note !!! You have only 24 hours to write us on e-mail or all your files will be lost or the decryption price will be "increased!"

====================================================================================
====================================

 * HOW TO RECOVERY MY FILES ???

You have to pay for decryption in Bitcoins. The price depends on how fast you write to us. After payment we will send you the decipher software and private key that will decrypt all your files.

========================================================================================================================

* FREE DECRYPTION !!!

Free decryption as guarantee! If you don't believe in our service and you want to see a proof, you can ask us about test" for decryption. You send us up to 5 modified files. Use file-sharing service and Win-Rar to send files for test. Files have to be less than 1 MB (non archived). Files should not be important! Don't send us databases, backups, large excel files, etc.  We will decrypt and send you your decrypted files back as a proof!"

========================================================================================================================

* WHY DO I NEED A TEST???

This is done so that you can make sure that only we can decrypt your files and that there will be no problems with the decryption!

========================================================================================================================

* HOW TO BUY BITCOINS ???

There are two simple ways to by bitcoins:
https://exmo.me/en/support#/1_3
https://localbitcoins.net/guides/how-to-buy-bitcoins

Read this information carefully because it's enough to purchase even in large amounts

========================================================================================================================

 !!! ATTENTION !!!

!!! After 60 hours the price for your encryption will increase 10 percent each day
!!! Do not rename encrypted files.
!!! Do not try to decrypt your data using third party software, it may cause permanent data loss.
!!! Decryption of your files with the help of third parties may cause increased price (they add their fee to our) or you can become a victim of a scam.

```



## 九、参考

[1] [https://www.bleepingcomputer.com/forums/t/709143/help-me-to-identify-ransomware-with-redrum-extension/](https://www.bleepingcomputer.com/forums/t/709143/help-me-to-identify-ransomware-with-redrum-extension/)<br>
[2] [https://attack.mitre.org/techniques/T1183/](https://attack.mitre.org/techniques/T1183/)<br>
[3] [https://en.wikipedia.org/wiki/Galois/Counter_Mode](https://en.wikipedia.org/wiki/Galois/Counter_Mode)<br>
[4] [https://www.bleepingcomputer.com/forums/t/709143/help-me-to-identify-ransomware-with-redrum-extension/page-2](https://www.bleepingcomputer.com/forums/t/709143/help-me-to-identify-ransomware-with-redrum-extension/page-2)

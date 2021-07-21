> 原文链接: https://www.anquanke.com//post/id/171485 


# Anatova勒索病毒详细分析


                                阅读量   
                                **199810**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



![](https://p5.ssl.qhimg.com/t017b1fd2c312828116.jpg)



## 前言

在今年1月22日[McAfee官方博客](https://securingtomorrow.mcafee.com/other-blogs/mcafee-labs/happy-new-year-2019-anatova-is-here/)发布文章称在发现了一个私有的点对点(p2p)网络中被发现一个新的勒索软件系列，并根据留下的勒索信息命名为Anatova，具体更多详情可以查看原文，故此对Anatova勒索病毒进行一番分析。



## 1.样本运行流程图

样本大概运行流程，3个阶段是我对于函数行为所作出的判断

![](https://p3.ssl.qhimg.com/t0189b63cc2c9e63b9f.png)

具体加密流程图

![](https://p3.ssl.qhimg.com/t01bcc33dc825f71a13.png)



## 2.样本IOCs

样本大小：314368 bytes

CRC32：49CF3E45

MD5: 596EBE227DCD03863E0A740B6C605924

SHA1: 37FADC40D6DC787CB13EF11663A9BC97C79B8F48

SHA256: 170FB7438316F7335F34FA1A431AFC1676A786F1AD9DEE63D78C3F5EFD3A0AC0



## 3.行为分析

这4个都是我获得的Anatova1.0勒索病毒的样本，都请求了管理员权限运行，样本图标都伪装成了游戏或者应用程序，样本的逻辑大致都相同，截至目前为止4个样本的多病毒引擎查杀率不尽相同，最高的一个样本有10个杀毒引擎查杀最低的样本只有4个杀毒引擎查杀

![](https://p1.ssl.qhimg.com/t01400e025d8c1e2a58.png)

遍历全盘文件进行加密并在加密成功路径下留下ANATOVA.txt勒索信息

![](https://p2.ssl.qhimg.com/t01cfae040635f03c79.png)

此为留下的勒索信息，根据勒索内容我们需要支付10个达世币才能解密我们的文件，按照现在的行情来说10个达世币价值5800RMB左右，我们可以发送200kb的JPG图片文件免费解密测试

![](https://p2.ssl.qhimg.com/t014dd0802b2d11c839.png)

被加密后的文件

![](https://p3.ssl.qhimg.com/t0198b74b35ac040494.png)

一切动作执行完毕之后调用执行CMD命令行自我删除

```
C:Windowssystem32cmd.exe /c timeout -c 9 &amp; del C:virself.exe /f /q
```

这条CMD命令的任务就是启动CMD命令行9秒之后执行删除路径中的文件，/f 强制删除只读文件，/q 安静模式删除全局通配符时不要求确认

![](https://p2.ssl.qhimg.com/t01aee920c048f1c536.png)



## 4.恶意代码分析

EXEINFO查看样本是64位程序编译日期为2019-01-01，链接器版本位6.0应该是为VC6编译

![](https://p4.ssl.qhimg.com/t012c7e1169b18504e2.png)

我们用IDA查看样本的导入表可以发现GetModuleHandleW，GetProAddress，LoadLibraryW这三个API可以判断使用到的函数地址都是通过这三个API组合获取

![](https://p4.ssl.qhimg.com/t011c588c2c84744be9.png)

### <a class="reference-link" name="4.1%E8%A7%A3%E5%86%B3IDA%E5%8F%8D%E7%BC%96%E8%AF%91%E5%A4%B1%E8%B4%A5%E9%97%AE%E9%A2%98"></a>4.1解决IDA反编译失败问题

在我们使用IDA静态分析的话不管是使用IDA6.8还是7.0或者是McAfee的分析师使用的最新IDA7.2版本都会出现错误导致反编译失败，并且函数都会识别出错一个好好的函数硬生生给截断了两个函数，如下图所示的sub_406C7B函数本来是一个函数，但是在函数开头开辟堆栈之后函数就被截断了，然后剩下的函数体又被IDA识别为了另一个函数，这可能是作者搞的鬼也可能是IDA的缺陷造成的

![](https://p0.ssl.qhimg.com/t011f0b39b110c8ed9e.png)

这对于我们进行静态分析和身为强迫症的我来说太难受了，如是乎在查阅了一大堆资料之后，找到了能够解决的方法，首先我们点击sub_406C70函数然后按快捷键D将代码转为数据，点击确认之后sub_406C7B函数也是一样的操作

![](https://p5.ssl.qhimg.com/t01c8ae0198b9da55aa.png)

下图为转换成数据之后的两个函数

![](https://p3.ssl.qhimg.com/t010aa466e1a922bbba.png)

之后我们再将转换为数据的两个函数按C快捷键再转换为代码

![](https://p2.ssl.qhimg.com/t0122e321409832af80.png)

接下来我们在已经转换为代码的sub_406C7B函数右键选择创建函数.

![](https://p5.ssl.qhimg.com/t0142662284fa46184f.png)

现在为止sub_406C7B已经可以正常识别为一个函数了，其他出现问题的函数都按照此方式修复即可

![](https://p5.ssl.qhimg.com/t01f170a3ae1d801022.png)

大多数字符串是经过某种加密的，除了作者的达世币地址和两个邮箱之外

![](https://p2.ssl.qhimg.com/t01b1eaeb22048c1147.png)

### <a class="reference-link" name="4.2%E5%88%9D%E5%A7%8B%E5%8C%96%E9%98%B6%E6%AE%B5%E6%81%B6%E6%84%8F%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>4.2初始化阶段恶意代码分析

我们使用IDA查看伪代码此为病毒样本初始化阶段的函数调用，main函数开始首先调用了一个空函数无任何功能，因为之后的函数调用逻辑比较多故此我会在下方对函数内部逐一进行详细分析

![](https://p1.ssl.qhimg.com/t017a19796aef2b1d1e.png)

此图为DecodeKernel32DllStrAndGetFunAddress函数内部，此函数解密了异或加密的dll和函数字符串，然后获取Kernel32模块基址并使用GetProcAddress获取Kernel32模块中的29个函数地址

![](https://p3.ssl.qhimg.com/t01ca9d66d9131f8176.png)

此图为DecodeSysDllString函数内部逻辑，函数功能已经逐行注释了

![](https://p5.ssl.qhimg.com/t016f6390ac0463626d.png)

调用DecodeSysDllString函数后解密的Kernel32字符串

![](https://p2.ssl.qhimg.com/t01fcfba7ad89fa040f.png)

循环29次解密29个异或加密的函数字符串

![](https://p1.ssl.qhimg.com/t01ac432e3acf97fe89.png)

i的值和要获取对应函数地址的函数指针一一对应

![](https://p2.ssl.qhimg.com/t013a16631fa0d34baf.png)

获取第一个函数地址并赋值给函数指针

![](https://p0.ssl.qhimg.com/t018c5f8afe392615e8.png)

获取完函数地址之后判断29个函数地址是否都获取成功如果有任何一个函数获取不成功退出进行清理流程

![](https://p3.ssl.qhimg.com/t019febd83c12b847b5.png)

接下来主要先禁用了Windows错误通知，之后创建互斥体确保系统中只有一个病毒样本实例运行，之后的3个Decodexxxx函数和上面详细分析过的DecodeKernel32DllStrAndGetFunAddress函数功能都一样只不过是获取另外3个dll中的函数地址罢了，所以就不详细分析函数内部逻辑了

![](https://p4.ssl.qhimg.com/t0116cd5ab850d246d0.png)

接下来两个函数分别检查了当前系统登陆用户名和系统语言

![](https://p5.ssl.qhimg.com/t018a9a021fced327c5.png)

此图为DecodeAndCheckUserName函数内部逻辑主要使用GetUserNameW函数获取当前系统登陆用户名并和列表中的用户名对比，对比如果和其中之一相同就退出并进行清理流程，此举为了防止分析人员将恶意样本在某些沙箱中运行

![](https://p4.ssl.qhimg.com/t017ff89cc494e302ce.png)

此图为CheckSystemLanguage函数内部逻辑，GetSystemDefaultUILanguage函数获取的是安装系统时第一个安装的语言，作者将这些国家排除在勒索范围之外要么就是作者就是来自这其中的国家之一，否则就另有所图了

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

完成检查操作系统语言之后样本会判断一个标志如果为TRUE才会执行LoadExtendDll函数，在此样本中此标志永远为FALSE所以永远不会执行，所以此功能是为了后续版本扩展模块用

![](https://p3.ssl.qhimg.com/t01f1d2a5a8b668058e.png)

此图为LoadExtendDll函数内部主要解密了两个dll模块名称并加载这两个模块

![](https://p3.ssl.qhimg.com/t014cf82377bdc797f4.png)

接下来分析EnumAndKillProcess函数，此函数主要逻辑就是使用windows下遍历进程的API组合遍历当前系统进程并和名单列表中的26个进程进行对比如果有相同的进行就结束，此举主要为了后续能供顺利进行加密做铺垫

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

此图为遍历到的第一个进程和名单内第一个进程对比

![](https://p1.ssl.qhimg.com/t01a63d9697e84bafef.png)

名单中要结束26个进程如下图

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

### <a class="reference-link" name="4.3%E5%8A%A0%E5%AF%86%E9%98%B6%E6%AE%B5%E6%81%B6%E6%84%8F%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>4.3加密阶段恶意代码分析

加密阶段调用了下图的3个函数实现，待我在下方进行详细分析

![](https://p0.ssl.qhimg.com/t016aed8c345a004314.png)

我们分析CreatRandRsaKey函数内部，主要就是生成了一对RSA密钥并导出

![](https://p5.ssl.qhimg.com/t01e075d11fc122451b.png)

此为导出的RSA公钥

![](https://p5.ssl.qhimg.com/t010766b1885f84c99b.png)

导出RSA私钥

![](https://p3.ssl.qhimg.com/t0143fc57c90bf2ec7f.png)

接下来分析ImportRsaKeyAndEncodeRandKey函数，先使用IDA查看大概的函数逻辑，稍后我会进行动态调式

![](https://p3.ssl.qhimg.com/t01788cbdf2c20f2ce7.png)

调用CryptGenRandom生成32字节随机密钥当作Salsa20算法key

![](https://p0.ssl.qhimg.com/t018d3260d9abdabc48.png)

生成第二个8字节的随机密钥当作Salsa20算法IV

![](https://p1.ssl.qhimg.com/t01faf45a923c7a4ec0.png)

调用Salsa20算法加密导出的RSA私钥

![](https://p0.ssl.qhimg.com/t0101972b102c5700a5.png)

加密后的buffer

![](https://p5.ssl.qhimg.com/t01a8515b32d5eaf679.png)

解密作者硬编码的RSA公钥Buffer

![](https://p3.ssl.qhimg.com/t016a2bc08265921e6a.png)

解密完毕RSA公钥

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

导入刚才解密的RSA公钥并对之前用来加密导出RSA私钥的Salsa20算法key进行加密

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

同理加密Salsa20算法IV

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

将三个加密完后的buffer拷贝到一起

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

之后使用CryptBinaryToStringA函数对buffer进行Base64编码

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

接下来分析主要的EncryptionFilesFun函数，此函数主要判断可用的磁盘并对可用磁盘进行全盘加密，对网络磁盘也会进行加密

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

EnumAllFiles函数内部主要就是遍历全盘并加密

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

此为ExcludeSysPath函数内部主要排除对列表中的9个文件夹的加密

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

此函数为CryptEncryptFileDate函数内部主要逻辑，我们可以查看函数大概逻辑

![](https://p3.ssl.qhimg.com/t0101ea1487b57e975b.png)

ExcludeFilePath函数检查并排除列表中16个文件的加密

![](https://p0.ssl.qhimg.com/t0170cb447956a5b5b4.png)

FileExtensionCheck函数对要加密文件的扩展名做检查排除对列表中的37个类别文件扩展名进行加密

![](https://p5.ssl.qhimg.com/t013220cebe528a9f71.png)

后缀名检查函数逻辑

![](https://p2.ssl.qhimg.com/t01de7e9d68dd08db41.png)

打开确认要加密的文件之后会对比文件末尾的记号防止二次加密

![](https://p1.ssl.qhimg.com/t019d6ad0d8bf8b8211.png)

使用随机生成的Salsa20算法key和IV对文件内容进行加密

![](https://p0.ssl.qhimg.com/t0190c2c7ba8f11c598.png)

此Buffer为用来加密当前文件的Salsa20算法Key和IV，使用RSA加密之后

![](https://p4.ssl.qhimg.com/t01a4b38543a1b2013e.png)

在将加密后文件内容，加密后的Salsa20算法Key和IV和文件大小，481写入文件后，将4字节加密记号写入文件末尾

![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)

接下来调用CreateBlackMailTxt函数在当前被加密文件路径下留下勒索信息，主要逻辑代码注释都在图中就不再解释了，接下来我们查看被加密后的文件

![](https://p2.ssl.qhimg.com/t0163d301dba29b2be6.png)

此图为加密后文件内容，和我们分析代码时写入的内容相同，至此勒索病毒的主要逻辑分析完毕接下来就是清理阶段

![](https://p4.ssl.qhimg.com/t01c27fded401369a70.png)

### <a class="reference-link" name="4.4%E6%B8%85%E7%90%86%E9%98%B6%E6%AE%B5%E6%81%B6%E6%84%8F%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90"></a>4.4清理阶段恶意代码分析

此为清理阶段的主要3个函数

![](https://p1.ssl.qhimg.com/t01bd432b05d740dfd4.png)

DelVolumeShadow函数内部

![](https://p0.ssl.qhimg.com/t018d64172dd8c59063.png)

SelfDelete函数内部，延迟9秒删除自身文件为了后续清空自身内存留时间

![](https://p3.ssl.qhimg.com/t01c9c71bd802554860.png)

CleanUpEnvironment函数清空了用到的各种密钥，还有将所动态获取的函数地址清空

![](https://p1.ssl.qhimg.com/t018d5ac8e6eab6e935.png)

最后一步清空程序所有函数代码的内存

![](https://p5.ssl.qhimg.com/t01c657ac8b26fc24cf.png)



## 5.编写Yara规则

根据获取到的Anatova系列样本编写的规则1

```
rule Anatovaone
`{`
    strings:
        $Ana_Mail_string1 = "anatoday@tutanota.com"
        $Ana_Mail_string2 = "anatova1@tutanota.com"
        $Ana_Mail_string3 = "anatova2@tutanota.com"
        $Ana_DASHA_string1 = "XpRvUwSjSeHfJqLePsRfQtCKa1VMwaXh12"
        $Ana_DASHA_string2 = "XktLWbv68EU9XhYBuvrAGtbZHronyJDt1L"
    condition:
        $Ana_Mail_string1 or $Ana_Mail_string2 or $Ana_Mail_string3 or $Ana_DASHA_string1 or $Ana_DASHA_string2
`}`
```

根据获取到的Anatova系列样本编写的规则2，这两个规则都可以对Anatova1.0系列样本进行查杀

```
rule Anatovatwo
`{`
    strings:
        $Ana_Hex_string = `{`28 28 28 4E 40 5C 28 28 28`}`
        $Ana_string2 = "Ixsz~Hcdkxs^eY~xcdmK"
    condition:
        all of them
`}`
```



## 6.总结

Anatova勒索病毒系列使用了游戏和软件的图标来伪装，以达到可以诱导用户下载运行的目的，此样本使用了Salsa20算法对文件进行加密并且最多就加密1M大小的文件内容实现了快速加密的目的，Anatova勒索病毒作者对内存的比较深入加大了分析人员进行分析的难度，我认为除非通过某些手段获取作者手上的RSA私钥否则其他方式进行解密的可能性不大，此1.0版本代码做了模块化为后面版本进行扩展功能，所以后续版本的更新威胁会比1.0版本大得多，对于应对此类勒索病毒唯一的解决方案只有预防了，备份备份再备份，安装杀毒软件并且升级最新的病毒库可以进行预防，不要打开不明来历的程序一定要用的话最好先放在虚拟机或者上传在线沙箱查看程序行为。

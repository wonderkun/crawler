> 原文链接: https://www.anquanke.com//post/id/163414 


# 近期GandCrab勒索事件详细分析


                                阅读量   
                                **300826**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t01cc804cdf37009569.jpg)](https://p4.ssl.qhimg.com/t01cc804cdf37009569.jpg)

作者：Kshom[@360](https://github.com/360)观星实验室

## 勒索事件概述

从2018年9月底开始，根据数据监测GandCrab勒索有大规模爆发趋势,且版本更新频繁。在国内GandCrab目前仍以弱口令爆破、伪装正常软件诱导用户运行及漏洞传播这三种方式传播。当用户遭受感染时，系统磁盘被加密，文件后缀被修改为随机字母，并勒索交付数字货币赎金。 本文将对勒索事件应急中的一些经验与大家分享

PS: GandCrab作者曾向被加密的叙利亚受害者道歉公布了5.0.3以前版本的密钥，随后更新了5.0.4版本并将叙利亚排除在加密区域之外，但是在10月最新的5.0.5版本又将这个区域设定删除



## 样本勒索执行流程

[![](https://p4.ssl.qhimg.com/t01977a9ade70aa54ee.png)](https://p4.ssl.qhimg.com/t01977a9ade70aa54ee.png)



## 勒索样本分析

虽然GandCrab勒索病毒更新比较频繁，但代码框架变动不大，为保持文章完整性，这里对勒索的流程和细节进行梳理，以10月最新的5.0.5版本分析为主。<br>
MD5: C805528F6844D7CAF5793C025B56F67D

从GandCrabV4版本之后，作者对函数调用入口做了处理，增加静态分析难度，此处入口为 loc_4061B3

[![](https://p5.ssl.qhimg.com/t015a7bae2159664a53.png)](https://p5.ssl.qhimg.com/t015a7bae2159664a53.png)

遍历进程，结束占用特定文件的进程，为能正常加密文件做准备

[![](https://p1.ssl.qhimg.com/t01ee419157df2b3508.png)](https://p1.ssl.qhimg.com/t01ee419157df2b3508.png)

[![](https://p1.ssl.qhimg.com/t01df18376e0434b5fc.png)](https://p1.ssl.qhimg.com/t01df18376e0434b5fc.png)

结束的进程如下

[![](https://p3.ssl.qhimg.com/t019f6cdbc692c2710f.png)](https://p3.ssl.qhimg.com/t019f6cdbc692c2710f.png)

检测特定的互斥量

[![](https://p3.ssl.qhimg.com/t01ac7cfb963d1dbaca.png)](https://p3.ssl.qhimg.com/t01ac7cfb963d1dbaca.png)

这里的互斥量对应了样本中嵌入的DLL，决定是否开启利用两个提权漏洞进行提权DLL通过xor 0x18解密后，内存执行并通过管道与主进程通信

[![](https://p1.ssl.qhimg.com/t01a0d33f8ccb6011b8.png)](https://p1.ssl.qhimg.com/t01a0d33f8ccb6011b8.png)

[![](https://p5.ssl.qhimg.com/t015d8ce6ce68ef28b8.png)](https://p5.ssl.qhimg.com/t015d8ce6ce68ef28b8.png)

通过VerifyVersionInfoW判断操作系统MajorVersion是否为6以上

[![](https://p2.ssl.qhimg.com/t0157872a7e569683aa.png)](https://p2.ssl.qhimg.com/t0157872a7e569683aa.png)

判断当前进程权限及安全身份RID，判断是否大于0x1000，这是确认当前进程是否为system组启动，以上两步均是判断操作系统是否为win7以上

[![](https://p5.ssl.qhimg.com/t015c01535d5b7d3353.png)](https://p5.ssl.qhimg.com/t015c01535d5b7d3353.png)

[![](https://p3.ssl.qhimg.com/t01fa751dde97b7a228.png)](https://p3.ssl.qhimg.com/t01fa751dde97b7a228.png)

判断是否为俄语系键盘语言及输入法

[![](https://p2.ssl.qhimg.com/t011f914b38ab2c0603.png)](https://p2.ssl.qhimg.com/t011f914b38ab2c0603.png)

[![](https://p3.ssl.qhimg.com/t01d8fd04bbdb1ffde6.png)](https://p3.ssl.qhimg.com/t01d8fd04bbdb1ffde6.png)

5.0.4版本中作者将叙利亚列入未加密区域，在5.0.5中又将其删除

[![](https://p5.ssl.qhimg.com/t01b6def959aa87c7b1.png)](https://p5.ssl.qhimg.com/t01b6def959aa87c7b1.png)

5.0.5如下图所示，5.0.4版本如上图所示

[![](https://p1.ssl.qhimg.com/t010cc8aa9e04f06eab.png)](https://p1.ssl.qhimg.com/t010cc8aa9e04f06eab.png)

将系统盘磁盘卷区的序号与特定字符串拼接加密后计算hash值，以此创建Mutex变量

[![](https://p0.ssl.qhimg.com/t01a2759d217e525d4d.png)](https://p0.ssl.qhimg.com/t01a2759d217e525d4d.png)

[![](https://p0.ssl.qhimg.com/t0130d5542b401e0d85.png)](https://p0.ssl.qhimg.com/t0130d5542b401e0d85.png)

[![](https://p1.ssl.qhimg.com/t0143787973e09510e7.png)](https://p1.ssl.qhimg.com/t0143787973e09510e7.png)

随后使用内置的密钥解密出RSA公钥

[![](https://p2.ssl.qhimg.com/t01f7b9f150231c6667.png)](https://p2.ssl.qhimg.com/t01f7b9f150231c6667.png)

当前版本RSA公钥如下

[![](https://p2.ssl.qhimg.com/t01629beb523f16686c.png)](https://p2.ssl.qhimg.com/t01629beb523f16686c.png)

查找是否存在相关杀软进程

[![](https://p1.ssl.qhimg.com/t01859c86e3ff08b6e0.png)](https://p1.ssl.qhimg.com/t01859c86e3ff08b6e0.png)

从注册表中取处理器相关信息拼成字符串计算CRC32值

[![](https://p2.ssl.qhimg.com/t010b199fff11bdac50.png)](https://p2.ssl.qhimg.com/t010b199fff11bdac50.png)

[![](https://p3.ssl.qhimg.com/t01306620030ae06539.png)](https://p3.ssl.qhimg.com/t01306620030ae06539.png)

获取机器信息，生成ransomId并拼接成字符串

[![](https://p3.ssl.qhimg.com/t01c422f79218d4d508.png)](https://p3.ssl.qhimg.com/t01c422f79218d4d508.png)

[![](https://p3.ssl.qhimg.com/t010ee9a9a9edaf6ac2.png)](https://p3.ssl.qhimg.com/t010ee9a9a9edaf6ac2.png)

随后通过RC4对这部分数据加密，RC4密钥为”jopochlen”

[![](https://p2.ssl.qhimg.com/t012e46b71b9ed16449.png)](https://p2.ssl.qhimg.com/t012e46b71b9ed16449.png)

加密后的数据如下

[![](https://p4.ssl.qhimg.com/t0111cd5d3f73c0f888.png)](https://p4.ssl.qhimg.com/t0111cd5d3f73c0f888.png)

在GandCrabV5版本后，加密文件后生成后缀变为随机

[![](https://p2.ssl.qhimg.com/t01cd17a792db1dc6ef.png)](https://p2.ssl.qhimg.com/t01cd17a792db1dc6ef.png)

[![](https://p3.ssl.qhimg.com/t018072a97cca77ae7c.png)](https://p3.ssl.qhimg.com/t018072a97cca77ae7c.png)

提取中要加密文件的类型及其后缀

[![](https://p5.ssl.qhimg.com/t019dd9c1bbf2ec26dd.png)](https://p5.ssl.qhimg.com/t019dd9c1bbf2ec26dd.png)

使用CryptGenKey及CryptExportKey生出并导出公私密钥对，并查找注册表HKCUSOFTWAREkeys_datadata及HKLMSOFTWAREkeys_datadata两项，作者检查HKCU及HKLM为确保样本在非管理员权限以上启动也可正常写入注册表

[![](https://p5.ssl.qhimg.com/t01ddd7adda3ca1b782.png)](https://p5.ssl.qhimg.com/t01ddd7adda3ca1b782.png)

[![](https://p5.ssl.qhimg.com/t01904600bc9eb566e5.png)](https://p5.ssl.qhimg.com/t01904600bc9eb566e5.png)

若这两个注册表项均不存在，则先创建HKLM(HKCU)SOFTWAREex_datadata项，并生成ext子项中存储此次勒索后缀。

[![](https://p2.ssl.qhimg.com/t0113c21d2956212fb3.png)](https://p2.ssl.qhimg.com/t0113c21d2956212fb3.png)

[![](https://p4.ssl.qhimg.com/t01e6aca5a89f634fb6.png)](https://p4.ssl.qhimg.com/t01e6aca5a89f634fb6.png)

生成RSA公钥加密后的密钥

[![](https://p5.ssl.qhimg.com/t0168d5efab92174e14.png)](https://p5.ssl.qhimg.com/t0168d5efab92174e14.png)

[![](https://p1.ssl.qhimg.com/t01007daac4f91dde7c.png)](https://p1.ssl.qhimg.com/t01007daac4f91dde7c.png)

将密钥信息写入到注册表HKLM(HKCU)SOFTWAREkeys_datadata的public和private中

[![](https://p3.ssl.qhimg.com/t01b44d78d74ad36565.png)](https://p3.ssl.qhimg.com/t01b44d78d74ad36565.png)

若这些注册表项已经存在则会使用HKLM(HKCU)SOFTWAREkeys_datadata项中原有的密钥及对应的后缀继续加密

[![](https://p1.ssl.qhimg.com/t01a4f90954ef18df66.png)](https://p1.ssl.qhimg.com/t01a4f90954ef18df66.png)

将加密提示写入到txt文件中

[![](https://p0.ssl.qhimg.com/t01636f220539acf4b4.png)](https://p0.ssl.qhimg.com/t01636f220539acf4b4.png)

并将加密后的密钥Base64保存

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010793fe7f0316d76f.png)

[![](https://p3.ssl.qhimg.com/t0178febacd65e1504b.png)](https://p3.ssl.qhimg.com/t0178febacd65e1504b.png)

创建线程开始加密

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01570e7bf1112d33df.png)

加密会分别枚举网络资源和本地文件，枚举网络资源如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ab71c67f4a01d2a6.png)

以下目录不加密

[![](https://p5.ssl.qhimg.com/t0114acd96f7561497a.png)](https://p5.ssl.qhimg.com/t0114acd96f7561497a.png)

以下文件不加密

[![](https://p2.ssl.qhimg.com/t01c5681a1d09a1756a.png)](https://p2.ssl.qhimg.com/t01c5681a1d09a1756a.png)

[![](https://p1.ssl.qhimg.com/t017dd48c8b32f2e1c2.png)](https://p1.ssl.qhimg.com/t017dd48c8b32f2e1c2.png)

存在随机生成的字符串则在目录下生成XXXXX-DECRYPT.txt勒索信息文件，否则生成KRAB-DECRYPT.txt

[![](https://p2.ssl.qhimg.com/t01d4623852e397358f.png)](https://p2.ssl.qhimg.com/t01d4623852e397358f.png)

[![](https://p5.ssl.qhimg.com/t011196648676394e4b.png)](https://p5.ssl.qhimg.com/t011196648676394e4b.png)

使用随机生成的字符串为后缀，若不存在则使用KRAB后缀

[![](https://p0.ssl.qhimg.com/t012fc172e1df1ece98.png)](https://p0.ssl.qhimg.com/t012fc172e1df1ece98.png)

递归遍历磁盘目录，加密流程如下

[![](https://p3.ssl.qhimg.com/t011be1f73dd66bd840.png)](https://p3.ssl.qhimg.com/t011be1f73dd66bd840.png)

加密函数与老版本基本相同

[![](https://p0.ssl.qhimg.com/t01d7a92c2c07eb7626.png)](https://p0.ssl.qhimg.com/t01d7a92c2c07eb7626.png)

[![](https://p4.ssl.qhimg.com/t01af8ff22951fb115e.png)](https://p4.ssl.qhimg.com/t01af8ff22951fb115e.png)

[![](https://p1.ssl.qhimg.com/t0112bb9d0dc3902eb6.png)](https://p1.ssl.qhimg.com/t0112bb9d0dc3902eb6.png)

最后末尾写入0x21c大小的加密数据

[![](https://p0.ssl.qhimg.com/t016102173b0679dc7a.png)](https://p0.ssl.qhimg.com/t016102173b0679dc7a.png)

将机器信息Base64编码后发送到某些域名

[![](https://p2.ssl.qhimg.com/t01dfcc42478803e30f.png)](https://p2.ssl.qhimg.com/t01dfcc42478803e30f.png)

[![](https://p3.ssl.qhimg.com/t0100fad7d7633f9642.png)](https://p3.ssl.qhimg.com/t0100fad7d7633f9642.png)

[![](https://p5.ssl.qhimg.com/t01ca0a632020f25f54.png)](https://p5.ssl.qhimg.com/t01ca0a632020f25f54.png)

解密出的域名如下图

[![](https://p2.ssl.qhimg.com/t019cec9aabdaaf9afe.png)](https://p2.ssl.qhimg.com/t019cec9aabdaaf9afe.png)

通过执行vssadmin delete删除巻影镜像防止恢复

[![](https://p0.ssl.qhimg.com/t01aadfb2b3fcb209ed.png)](https://p0.ssl.qhimg.com/t01aadfb2b3fcb209ed.png)

[![](https://p0.ssl.qhimg.com/t01d15a727374198d9e.png)](https://p0.ssl.qhimg.com/t01d15a727374198d9e.png)

勒索完成后会自删除

[![](https://p4.ssl.qhimg.com/t01b846ae2a01ead616.png)](https://p4.ssl.qhimg.com/t01b846ae2a01ead616.png)

在GandCrabV5版本后，会在%TEMP%目录下创建并更改系统壁纸，展示勒索信息

[![](https://p2.ssl.qhimg.com/t0109744aa8b1832727.png)](https://p2.ssl.qhimg.com/t0109744aa8b1832727.png)

[![](https://p3.ssl.qhimg.com/t011d9df8fc4c4de102.png)](https://p3.ssl.qhimg.com/t011d9df8fc4c4de102.png)

在GandCrabV5版本后，作者增加了多个提权漏洞利用，有影响Win7、WinServer 2008及WinServer 2008 R2提权漏洞CVE-2018-8120

[![](https://p1.ssl.qhimg.com/t0161153c2b9dc9736d.png)](https://p1.ssl.qhimg.com/t0161153c2b9dc9736d.png)

影响Win7以上的操作系统的提权漏洞CVE-2018-8440

[![](https://p0.ssl.qhimg.com/t01c5bbe60a2eee9cf1.png)](https://p0.ssl.qhimg.com/t01c5bbe60a2eee9cf1.png)

[![](https://p0.ssl.qhimg.com/t018032df0c1f8d0ba6.png)](https://p0.ssl.qhimg.com/t018032df0c1f8d0ba6.png)

[![](https://p0.ssl.qhimg.com/t014a42c38cfe6ea592.png)](https://p0.ssl.qhimg.com/t014a42c38cfe6ea592.png)

Win10提权漏洞CVE-2018-0896

[![](https://p2.ssl.qhimg.com/t016e4fda60e6c17b61.png)](https://p2.ssl.qhimg.com/t016e4fda60e6c17b61.png)

至此勒索样本分析完成



## 事件溯源分析

在2018年10月18日，360观星实验室团队在处理用户应急时，发现内网遭遇勒索，文件后缀被加密为PWFKPFCP，在磁盘目录下发现PWFKPFCP-DECRYPT.txt文件，根据特征判断用户感染了GandCrab勒索软件

[![](https://p2.ssl.qhimg.com/t019e9787e3ca54719a.png)](https://p2.ssl.qhimg.com/t019e9787e3ca54719a.png)

对于被感染的用户，使用了观星实验室应急响应分析平台，对用户相关系统提取关键日志等信息，通过关联分析，大致得出黑客攻击的路径，具体如下：

无论是前段时间爆发的GlobeImposter勒索、Crysis勒索还是近期的GandCrab勒索，以弱口令爆破为主要攻击手法的黑客团伙已经拥有非常成熟的流程和工具。

在对收集上来的日志进行关联分析时，发现对KProcessHacker服务的加载时间来统计其时间轴进行初步定位

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0109a39cfb9f4fea72.png)

从数据得出在2018年10月16日22点57分，KProcessHacker服务已被加载，其登录分析行为如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01007d52f58868215e.png)

在暴力破解检测中发现从2018年10月14日开始，用户机器已经遭受大量爆破攻击

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0181bf69e8c92201e8.png)

并发现了两条可疑的RDP登录记录

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011e1a83c1ac544f03.png)

一条记录指向是X.X.X.60这台机器，在2018年10月18日凌晨2点29分通过Administrator RDP登录，这台60机器显然也是受害机器，但时间已经晚于KProcessHacker加载时间

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019fe41514ae63bdfb.png)

另一条记录指向是X.X.X.171这台机器，在2018年10月16日22点56分通过Administrator RDP登录，这台机器的登录时间与KProcessHacker服务的加载时间相近且在其之前

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0175791acfcd702363.png)

深入分析171机器，同样发现了大量爆破记录

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c61f361c5e8e0616.png)

在2018年10月17日凌晨4点05分Administrator被重置密码

[![](https://p0.ssl.qhimg.com/t01099cc79e4b895b7f.png)](https://p0.ssl.qhimg.com/t01099cc79e4b895b7f.png)

随即在2018年10月17日凌晨4点13分开始，恶意ip 119.129.75.111登录

[![](https://p4.ssl.qhimg.com/t01f48b4171109ac509.png)](https://p4.ssl.qhimg.com/t01f48b4171109ac509.png)

并在2018年10月17日 17点27分将Administrator添加为Oracle超级管理员

[![](https://p0.ssl.qhimg.com/t01682e0897f895494b.png)](https://p0.ssl.qhimg.com/t01682e0897f895494b.png)

继续对X.X.X.171机器关联分析发现X.X.X.164机器被更多的恶意ip登录

[![](https://p2.ssl.qhimg.com/t01933c359de0c603ae.png)](https://p2.ssl.qhimg.com/t01933c359de0c603ae.png)

针对乌克兰193.238.46.96等ip分析，发现存在明显的扫描和爆破行为

[![](https://p0.ssl.qhimg.com/t0173e0301943acc57c.png)](https://p0.ssl.qhimg.com/t0173e0301943acc57c.png)

对所有登录事件关联分析如下图所示

[![](https://p1.ssl.qhimg.com/t01eb8db2a3f2077e6f.png)](https://p1.ssl.qhimg.com/t01eb8db2a3f2077e6f.png)

通过以上分析，基本确认出此次攻击的发起点及攻击路径



## 处置建议



## 安全建议



## 参考链接及IOC

IOC：

c805528f6844d7caf5793c025b56f67d

f8853def4c82a9075ff0434c13ceca23

c805528f6844d7caf5793c025b56f67d

[“GandCrab勒索病毒最新疫情”- 360安全卫士](https://www.anquanke.com/post/id/161080)

[“Rapidly Evolving Ransomware GandCrab Version 5 Partners With Crypter Service for Obfuscation”- Mcafee](https://securingtomorrow.mcafee.com/mcafee-labs/rapidly-evolving-ransomware-gandcrab-version-5-partners-with-crypter-service-for-obfuscation/)

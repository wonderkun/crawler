> 原文链接: https://www.anquanke.com//post/id/231504 


# Stop家族勒索病毒litar变种分析


                                阅读量   
                                **116013**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t0118e6d866b26f4c0c.jpg)](https://p2.ssl.qhimg.com/t0118e6d866b26f4c0c.jpg)



## 0x00 样本简介

MD5: F9078C037B406527084BC11F03AA07A1<br>
SHA-1: C5158ED9537D5D0426DF946069531040F9F45BA4

Stop家族的勒索病毒有多个变种，变种之间加密后的文件后缀名不相同，在勒索病毒执行之后会在文件目录下留下_Readme.txt的勒索信息索要高额费用，本文将以litar变种的样本为基础分析该勒索病毒的恶意行为。



## 0x01 病毒主题程序

[![](https://p5.ssl.qhimg.com/t01bb4a2364c15dab10.jpg)](https://p5.ssl.qhimg.com/t01bb4a2364c15dab10.jpg)

程序加载进IDA后可以生成MAP文件，导入到OD中方便动态调试

[![](https://p3.ssl.qhimg.com/t01eb18571b6014eaa2.jpg)](https://p3.ssl.qhimg.com/t01eb18571b6014eaa2.jpg)

[![](https://p2.ssl.qhimg.com/t0150fc3b27f0e89ece.jpg)](https://p2.ssl.qhimg.com/t0150fc3b27f0e89ece.jpg)

[![](https://p3.ssl.qhimg.com/t01c02e834f792b22d9.jpg)](https://p3.ssl.qhimg.com/t01c02e834f792b22d9.jpg)

跟到sub_4032C0函数内，堆中申请0x44E2C大小的内存把解密后的ShellCode放到申请的堆中，利用VirtualProtect函数设置刚才申请的堆内存可执行，最后跳转到ShellCode执行。

[![](https://p3.ssl.qhimg.com/t015e0e6f6570f38556.jpg)](https://p3.ssl.qhimg.com/t015e0e6f6570f38556.jpg)

[![](https://p1.ssl.qhimg.com/t01fb6b3abee94daa71.jpg)](https://p1.ssl.qhimg.com/t01fb6b3abee94daa71.jpg)

[![](https://p1.ssl.qhimg.com/t01542bd3b16dcd77fa.jpg)](https://p1.ssl.qhimg.com/t01542bd3b16dcd77fa.jpg)



## 0x02 ShellCode执行流程

对于想要静态分析ShellCode可以在OD里转到申请的堆区域二进制复制下来用WinHex 保存出来，这样就可以在IDA里静态分析了。

动态加载WindowsAPI，利用SetErrorMode反沙箱。

[![](https://p2.ssl.qhimg.com/t01474d81a4cf4959e2.jpg)](https://p2.ssl.qhimg.com/t01474d81a4cf4959e2.jpg)

申请堆内存空间放置解密后的PE文件，和此前Dump ShellCode一样操作把新的PE文件导出，方便后续静态分析。

[![](https://p1.ssl.qhimg.com/t01178a4b88543caeca.jpg)](https://p1.ssl.qhimg.com/t01178a4b88543caeca.jpg)

解密并释放新的PE文件至当前进程空间。

[![](https://p4.ssl.qhimg.com/t01a31a299a550d6887.jpg)](https://p4.ssl.qhimg.com/t01a31a299a550d6887.jpg)

加载导入表，最后跳入新PE文件的OEP

[![](https://p1.ssl.qhimg.com/t01e5d37d1add65a5b7.jpg)](https://p1.ssl.qhimg.com/t01e5d37d1add65a5b7.jpg)

[![](https://p1.ssl.qhimg.com/t0112934f2c7a0051bc.jpg)](https://p1.ssl.qhimg.com/t0112934f2c7a0051bc.jpg)



## 0x03 dump_PE文件分析

因为是替换源进程空间所有OD中如果接着调试会出现问题，所以之前导出的新PE文件就派上用场了，我们把它叫做dump_PE，和最早一样可以导入IDA生成的MAP文件方便OD调试。

利用网页API获取本机地区代码。

[![](https://p3.ssl.qhimg.com/t01efd08b520c173807.jpg)](https://p3.ssl.qhimg.com/t01efd08b520c173807.jpg)

比较白名单如果在白名单内则不执行加密操作，%TEMP%目录下创建delself.bat批处理文件把自身删除。

[![](https://p2.ssl.qhimg.com/t0170e405bfb33dd3bc.jpg)](https://p2.ssl.qhimg.com/t0170e405bfb33dd3bc.jpg)

[![](https://p4.ssl.qhimg.com/t016061c901125bd9c5.jpg)](https://p4.ssl.qhimg.com/t016061c901125bd9c5.jpg)

设置当前程序优先级为最高。

[![](https://p4.ssl.qhimg.com/t0162a685b4ec6bd293.jpg)](https://p4.ssl.qhimg.com/t0162a685b4ec6bd293.jpg)

读取命令行参数，根据后续代码判断应该是利用这些参数判断目前程序是在何种状态以及进行功能测试。

[![](https://p2.ssl.qhimg.com/t01cf09b63da08cbbef.jpg)](https://p2.ssl.qhimg.com/t01cf09b63da08cbbef.jpg)

[![](https://p3.ssl.qhimg.com/t0184db9ac03f48381d.jpg)](https://p3.ssl.qhimg.com/t0184db9ac03f48381d.jpg)

创建%LOCALAPPDATA%\进程UUID文件夹并把当前文件复制至该目录下，并通过设置注册表自启动实现持久化。

[![](https://p2.ssl.qhimg.com/t012e994c0734dc2797.jpg)](https://p2.ssl.qhimg.com/t012e994c0734dc2797.jpg)

[![](https://p3.ssl.qhimg.com/t0128c9877bf4fc74d0.jpg)](https://p3.ssl.qhimg.com/t0128c9877bf4fc74d0.jpg)

[![](https://p3.ssl.qhimg.com/t01004d25f65f6e3d82.jpg)](https://p3.ssl.qhimg.com/t01004d25f65f6e3d82.jpg)

icacls命令修改刚才创建的目录权限

```
icacls "C:\Users\Administrator\AppData\Local\d2105da4-c104-49d1-a686-dac7f4749a49" /deny *S-1-1-0:(OI)(CI)(DE,DC)
```

[![](https://p2.ssl.qhimg.com/t01eddd41f5d8508660.jpg)](https://p2.ssl.qhimg.com/t01eddd41f5d8508660.jpg)

设置计划任务每五分钟启动一次。

[![](https://p2.ssl.qhimg.com/t01dcf1f3c664f9e392.jpg)](https://p2.ssl.qhimg.com/t01dcf1f3c664f9e392.jpg)

[![](https://p4.ssl.qhimg.com/t01898aa32aee1412c9.jpg)](https://p4.ssl.qhimg.com/t01898aa32aee1412c9.jpg)

以管理员身份执行本程序，手动给OD相对于的参数“—Admin IsNotAutoStart IsNotTask”。

[![](https://p1.ssl.qhimg.com/t01a217ef27caca56f7.jpg)](https://p1.ssl.qhimg.com/t01a217ef27caca56f7.jpg)

开启线程下载勒索病毒辅助程序，可惜现在下载地址无法访问了就先略过。

```
http://texet2.ug/tesptc/penelop/updatewin1.exe
http://texet2.ug/tesptc/penelop/updatewin2.exe
http://texet2.ug/tesptc/penelop/updatewin.exe
http://texet2.ug/tesptc/penelop/3.exe
http://texet2.ug/tesptc/penelop/4.exe
http://texet2.ug/tesptc/penelop/5.exe
```

[![](https://p3.ssl.qhimg.com/t016b0466ea599ebdd3.jpg)](https://p3.ssl.qhimg.com/t016b0466ea599ebdd3.jpg)

[![](https://p3.ssl.qhimg.com/t01173abec45cf2705f.jpg)](https://p3.ssl.qhimg.com/t01173abec45cf2705f.jpg)

开启线程使用mac地址MD5之后为参数向远程服务器获取RSA加密公钥以及本机机器码，如果无信息返回则使用硬编码作为默认公钥和机器码。

```
http://texet1.ug/AJshdd74568oHIUHSusf6441/Asjdioaiuf738/get.php?pid=MD5(mac)&amp;first=true
```

[![](https://p1.ssl.qhimg.com/t01b5f3522233b3095b.jpg)](https://p1.ssl.qhimg.com/t01b5f3522233b3095b.jpg)

[![](https://p3.ssl.qhimg.com/t017d1ac9ebac0fbf49.jpg)](https://p3.ssl.qhimg.com/t017d1ac9ebac0fbf49.jpg)

拼接_readme.txt文件内容。

[![](https://p4.ssl.qhimg.com/t017bc85079e59b0901.jpg)](https://p4.ssl.qhimg.com/t017bc85079e59b0901.jpg)

设置加密目录及后缀名白名单。

[![](https://p0.ssl.qhimg.com/t01b31a51745500b5a4.jpg)](https://p0.ssl.qhimg.com/t01b31a51745500b5a4.jpg)

[![](https://p0.ssl.qhimg.com/t01a642c1db31ad150f.jpg)](https://p0.ssl.qhimg.com/t01a642c1db31ad150f.jpg)



创建线程遍历文件加密并在根目录下生成_readme.txt勒索信息。

[![](https://p3.ssl.qhimg.com/t01d1b3c4c7c3808b9c.jpg)](https://p3.ssl.qhimg.com/t01d1b3c4c7c3808b9c.jpg)

如果文件大小小于5字节则不进行加密直接修改后缀名。

[![](https://p1.ssl.qhimg.com/t01d2af4a100f45bb23.jpg)](https://p1.ssl.qhimg.com/t01d2af4a100f45bb23.jpg)

[![](https://p2.ssl.qhimg.com/t013d5f6e79250091e1.jpg)](https://p2.ssl.qhimg.com/t013d5f6e79250091e1.jpg)

如果被读取的文件末尾有”`{`36A698B9-D67C-4E07-BE82-0EC5B14B4DF5`}`”则说明已经被加密过了，释放堆栈关闭文件句柄。

[![](https://p2.ssl.qhimg.com/t01af91a6f072bb6abc.jpg)](https://p2.ssl.qhimg.com/t01af91a6f072bb6abc.jpg)

每个文件都生成了唯一的标识码，利用Salsa20流加密第六个字节到150KB的内容利用此前服务器传递的RSA公钥加密这个文件标识码，最后写入文件末端同时追加被加密的标识符“`{`36A698B9-D67C-4E07-BE82-0EC5B14B4DF5`}`”。

[![](https://p5.ssl.qhimg.com/t019c6ab316165bfe8b.jpg)](https://p5.ssl.qhimg.com/t019c6ab316165bfe8b.jpg)

[![](https://p5.ssl.qhimg.com/t01bb4af650ea2e93e7.jpg)](https://p5.ssl.qhimg.com/t01bb4af650ea2e93e7.jpg)



## 0x04 总结

感觉这个病毒集合了Ransom和DownLoader，可惜的是在分析的时候DownLoader的服务器已经不能访问了，对勒索病毒的辅助程序没能更深入的分析。不过作为勒索病毒基本功能都还可用，拿来练手还是比较合适的。

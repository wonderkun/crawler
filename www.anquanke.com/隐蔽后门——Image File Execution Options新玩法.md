> 原文链接: https://www.anquanke.com//post/id/151425 


# 隐蔽后门——Image File Execution Options新玩法


                                阅读量   
                                **406660**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                    



## 0x01 前言

映像劫持（Image File Execution Options，IFEO）技术的利用，存在已久。大都是修改“Debugger“项值，替换执行程序，加以利用。歪果仁最近在研究IFEO的相关项值时，发现了GlobalFlag这个特殊的项值，在进一步测试时，发现了一种基于IFEO的[新后门利用方式](https://oddvar.moe/2018/04/10/persistence-using-globalflags-in-image-file-execution-options-hidden-from-autoruns-exe/)。本着求知探索的科学精神。本文对此技术进行分析总结。



## 0x02 映像劫持简介

映像劫持（Image File Execution Options），简单的说法，就是当你打开的是程序A，而运行的确是程序B。

映像劫持其实是Windows内设的用来调试程序的功能，但是现在却往往被病毒恶意利用。当用户双击对应的程序后，操作系统就会给外壳程序（例如“explorer.exe”）发布相应的指令，其中包含有执行程序的路径和文件名，然后由外壳程序来执行该程序。事实上在该过程中，Windows还会在注册表的上述路径中查询所有的映像劫持子键，如果存在和该程序名称完全相同的子键，就查询对应子健中包含的“dubugger”键值名，并用其指定的程序路径来代替原始的程序，之后执行的是遭到“劫持”的虚假程序

来自 [&lt;http://www.weixianmanbu.com/article/2188.html](//www.weixianmanbu.com/article/2188.html)&gt;

IEEO位于注册表项中

> “HKEY_LOCAL_MACHINESOFTWAREMicrosoftWindows NTCurrentVersionImage File Execution Options”

注意的是，Win7后的系统，需要管理员权限才能够对这一项做出修改。之前的病毒，喜欢修改这个注册表项，达到劫持系统程序的作用。

[![](https://p3.ssl.qhimg.com/t012a9383b514ce9905.png)](https://p3.ssl.qhimg.com/t012a9383b514ce9905.png)

下面，做的是一个简单的测试：管理员权限，打开CMD，执行下列修改注表的命令。

可以看到：打开notepad.exe，而运行起来的是计算器。

[![](https://p5.ssl.qhimg.com/t01536966c81bb8cf8f.gif)](https://p5.ssl.qhimg.com/t01536966c81bb8cf8f.gif)



## 0x03 映像劫持新玩法

如上文中所讲述，修改IFEO中的“debugger”键值，用来替换原有程序的执行。而新的利用方法，实现的效果是：程序A静默退出结束后，会执行程序B。

在网上收集资料整理后发现， Image File Execution Options下可以设置以下值项（值只是部分，只能感慨，微软没告诉我们的东西还真多啊）。其中GlobalFlag是本次测试的关键点：

歪果仁本是想弄清楚ApplicationGoo这个项值的作用，无奈却毫无头绪。但是在[MSDN的博客](https://blogs.msdn.microsoft.com/junfeng/2004/04/28/image-file-execution-options/)上，发现热心人士对GlobalFlag的这个项值的发表的一些看法。爱实践的歪果仁下载安装了GFlages.exe 开始分析。真是山重水复疑无路，柳暗花明又一村。这便是突破口。

[![](https://p5.ssl.qhimg.com/t012d06bd7e2cd4fc04.png)](https://p5.ssl.qhimg.com/t012d06bd7e2cd4fc04.png)



## 0x04 GFlages.exe进行测试

按照MSDN博客的说法，笔者也尝试安装GFlages.exe进行测试。中间遇到一些小坑，GFlages.exe是包含在 Debugging Tools for Windows(WinDbg)下的。网上现有都是通过安装完整的Windows SDK。很折腾，经过一番搜索，找到一下dbg的单独安装包，感谢作者分享。

> [http://download.microsoft.com/download/A/6/A/A6AC035D-DA3F-4F0C-ADA4-37C8E5D34E3D/setup/WinSDKDebuggingTools_amd64/dbg_amd64.msi](http://download.microsoft.com/download/A/6/A/A6AC035D-DA3F-4F0C-ADA4-37C8E5D34E3D/setup/WinSDKDebuggingTools_amd64/dbg_amd64.msi)
来自 [&lt;https://blog.csdn.net/johnsonblog/article/details/8165861](//blog.csdn.net/johnsonblog/article/details/8165861)&gt;

[![](https://p3.ssl.qhimg.com/t01ccbbbf5404dc6b7c.png)](https://p3.ssl.qhimg.com/t01ccbbbf5404dc6b7c.png)

在Silent Process Exit这个选项卡中发现了挺有趣的东西。根据微软官方介绍，从Windows7开始，可以在Silent Process Exit选项卡中，可以启用和配置对进程静默退出的监视操作。在此选项卡中设定的配置都将保存在注册表中。

[![](https://p5.ssl.qhimg.com/t0183cf1174cfb255c0.png)](https://p5.ssl.qhimg.com/t0183cf1174cfb255c0.png)

填入如上配置，点击应用、确定，开始测试。使用Process Explorer进行检测进程的变化。注意，在进行此次测试之前，请先把IFEO中notepad.exe项删除。

打开notepad.exe,关闭后，随之计算器弹出。在Process Explorer上可以看到计算器已经被系统调起。

[![](https://p3.ssl.qhimg.com/t01a8a2f7a60d3a9a7a.gif)](https://p3.ssl.qhimg.com/t01a8a2f7a60d3a9a7a.gif)



## 0x05 原理分析

根据微软的官方文档描述，在Silent Process Exit选项卡中的配置，都保存在注册表中。经过分析，等值，主要修改了以下两个表项。

[![](https://p0.ssl.qhimg.com/t0141152e602a3696a3.png)](https://p0.ssl.qhimg.com/t0141152e602a3696a3.png)

[![](https://p4.ssl.qhimg.com/t018662d4f285ac8c6d.png)](https://p4.ssl.qhimg.com/t018662d4f285ac8c6d.png)

这么一来，可以直接在命令行中对注册表进行设置，需要管理员权限。

​ 简单解释一下ReportingMode和MonitorProcess 这两个项值的作用。MonitorProcess的值表示监视器进程。Reporting Mode可以设置为三个值 。

|Flag|Value|解释
|------
|LAUNCH_MONITORPROCESS|0x1|检测到进程静默退出时，将会启动监视器进程（在GFLAGS.exe中，Silent Process Exit这个选项卡所填写的值，即MonitorProcess的项值）
|LOCAL_DUMP|0x2|检测到进程静默退出时，将会为受监视的进程创建转储文件
|NOTIFICATION|0x4|检查到进程静默退出时，将会弹出一个通知



## 0x06 检测及查杀
1. 排查HKLMSOFTWAREMicrosoftWindows NTCurrentVersionImage File Execution Options 以及HKLMSOFTWAREMicrosoftWindows NTCurrentVersionSilentProcessExit项值是否存在关联。
1. 分析系统日志，日志ID为3000和3001，即有可能存在后门威胁。
1. 直接删除IFEO项或者设置管理员不可修改


## 0x07 总结
1. 本文分析总结了关于映像劫持的的一种新型后门技术：当一个程序关闭时会允许执行其他的二进制文件。且Autorun暂时检测不到。
1. 该技巧需要管理员权限，普通用户没有执行权限。
1. 可以结合ADS技术（alternate data streams，NTFS交换数据流）执行，更加的隐蔽。感兴趣的同学可以自己测试一下。


## 参考文章
1. [https://oddvar.moe/2018/04/10/persistence-using-globalflags-in-image-file-execution-options-hidden-from-autoruns-exe/](https://oddvar.moe/2018/04/10/persistence-using-globalflags-in-image-file-execution-options-hidden-from-autoruns-exe/)
1. [http://www.weixianmanbu.com/article/2188.html](http://www.weixianmanbu.com/article/2188.html)
1. [https://www.qingsword.com/qing/180.html](https://www.qingsword.com/qing/180.html)
1. [https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/registry-entries-for-silent-process-exit](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/registry-entries-for-silent-process-exit)
1. [https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/setting-and-clearing-flags-for-silent-process-exit](https://docs.microsoft.com/en-us/windows-hardware/drivers/debugger/setting-and-clearing-flags-for-silent-process-exit)
审核人：yiwang   编辑：边边

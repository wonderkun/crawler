> 原文链接: https://www.anquanke.com//post/id/148074 


# 注册表中的PowerShell后门分析


                                阅读量   
                                **122106**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：
                                <br>原文地址：[https://az4n6.blogspot.com/2018/06/malicious-powershell-in-registry.html](https://az4n6.blogspot.com/2018/06/malicious-powershell-in-registry.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t012c5da0c9f19b1248.jpg)](https://p3.ssl.qhimg.com/t012c5da0c9f19b1248.jpg)



## 写在前面的话

大家好，这是我关于恶意PowerShell脚本系列文章的第二部分。我的[第一篇](http://az4n6.blogspot.com/2017/10/finding-and-decoding-malicious.html)文章介绍了如何在系统事件日志中查找恶意的PowerShell脚本以及如何解码它们。在这篇文章中，我将讨论恶意PowerShell脚本可能隐藏的另一个位置——注册表。



## 分析

注册表是攻击者建立持久访问的好地方。常用的位置是位于软件配置单元或用户的`ntuser.dat`配置单元中的运行密钥。有关运行密钥的列表，请查看[Forensic Wiki](https://www.forensicswiki.org/wiki/Windows_Registry#Run_keys)。

我以前见过攻击者在Run键中使用PowerShell来调用包含另一个包含payload的base64代码。<br>
让我们看看这个例子。使用Eric Zimmerman的[注册表资源管理器](https://ericzimmerman.github.io/)，我打开以下注册表项：`HKLMSoftwareMicrosoftWindowsCurrentVersionRun`。在“hztGpoWa”值的下面，进行以下输入：[![](https://p5.ssl.qhimg.com/t014bbc26364847fbdb.png)](https://p5.ssl.qhimg.com/t014bbc26364847fbdb.png)你也可以使用Harlan的[RegRipper](https://github.com/keydet89/RegRipper2.8)的 `soft_run`插件来获取这些信息：

```
`rip.exe -r SOFTWARE -p soft_run`
```

**<a class="reference-link" name="%E8%BE%93%E5%87%BA:"></a>输出:**

[![](https://p5.ssl.qhimg.com/t01ec1fb695513e4a13.png)](https://p5.ssl.qhimg.com/t01ec1fb695513e4a13.png)

( 对于NTUSER.DAT配置单元，使用user_run插件） 那么这个命令是做什么的？`％COMSPEC％`是`cmd.exe`的系统变量。使用cmd.exe在隐藏窗口中启动PowerShell。然后它使用PowerShell命令`“Get-Item”`获取另一个注册表项——`HKLM：Software4MX64uqR`和该项下的`Dp8m09KD`值。 查看HKLM：注册表资源管理器中的`Software4MX64uqR`键显示为一大段base64：[![](https://p3.ssl.qhimg.com/t01c45ee92803f21048.png)](https://p3.ssl.qhimg.com/t01c45ee92803f21048.png)另一种从注册表中获取像这样base64的方法是使用[RegRipper](https://github.com/keydet89/RegRipper2.8)的“sizes”插件。这将在注册表配置单元中搜索超过特定阈值的值并将其转储出去：

```
`  rip.exe -r SOFTWARE -p sizes`
```

要查看如何解码这个base64的详细步骤，请查看我之前关于解码恶意PowerShell脚本的博客[文章](http://az4n6.blogspot.com/2017/10/finding-and-decoding-malicious.html)。

以下是对其进行解码的步骤：

```
1.在注册表项中解码unicode base64。
2.解码和解压（gzip）嵌入式base64 。
3.解码另一组嵌入式base64。
4.payload = shellcode。
5.尝试在shellcode上运行scdb.exe或字符串以获取IP地址和端口
```

生成的代码通常是建立Meterpreter反向外壳的一种方法。在注册表中查找恶意PowerShell实例的另一种方法是在注册表中搜索`“％COMSPEC％”`。我使用 Registry Explorer和它的方便查找命令来做到这一点。确保并选择正确的“搜索”框：[![](https://p0.ssl.qhimg.com/t01c9229d8b26917c26.png)](https://p0.ssl.qhimg.com/t01c9229d8b26917c26.png)虽然此示例展示了一些随机名称的注册表项和值，但情况并总是这样。因为这些名称是可以根据攻击者修改，并且它们不会像随机名称那样显而易见。对于我的示例，我使用Metasploit在注册表中安装此持久性机制。检查所有可用的选项。如上所述，注册表项/值名称可以设置为任何内容：[![](https://p4.ssl.qhimg.com/t01a9e94aad159c08b9.png)](https://p4.ssl.qhimg.com/t01a9e94aad159c08b9.png)我的下一篇文章将介绍PowerShell日志记录和从内存中提取信息。

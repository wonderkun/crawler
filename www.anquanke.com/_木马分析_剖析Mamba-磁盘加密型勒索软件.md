> 原文链接: https://www.anquanke.com//post/id/85307 


# 【木马分析】剖析Mamba-磁盘加密型勒索软件


                                阅读量   
                                **80429**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：blog.fortinet.com
                                <br>原文地址：[https://blog.fortinet.com/2016/09/27/dissecting-mamba-the-disk-encrypting-ransomware](https://blog.fortinet.com/2016/09/27/dissecting-mamba-the-disk-encrypting-ransomware)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01f6f1225a5c33c8e0.png)](https://p5.ssl.qhimg.com/t01f6f1225a5c33c8e0.png)

****

**翻译：**[**myswsun******](http://bobao.360.cn/member/contribute?uid=2775084127)

**预估稿费：170RMB（不服你也来投稿啊！）**

**<strong><strong>投稿方式：发送邮件至**[**linwei#360.cn**](mailto:linwei@360.cn)**，或登陆**[**网页版**](http://bobao.360.cn/contribute/index)**在线投稿**</strong></strong>

**<br>**

**0x00 前言**

另一个新的勒索软件已经加入文件加密的潮流中。只是这一次不是选择一些类型的文件加密，它直接用一个开源的工具DiskCryptor加密整个磁盘。

这个不是第一次出现磁盘加密类型的勒索软件。在早年，Petya勒索软件通过加密磁盘主文件表（MFT）恶意破环，使用户无权访问文件。不像之前的攻击，这个新的勒索软件完全加密整个磁盘，包括数据。除非支付勒索金否则系统完全不能用。为了匹配它的能力，他被命名为有毒的射的名字，曼巴。

本文调查了这个恶意程序的功能和技术。

<br>

**0x01 DiskCryptor安装**

深入到磁盘权限和加密将会非常的复杂。因此，直接写代码加密磁盘将很容易产生一个噩梦。因为这个原因，一个实用的方案是用一个第三方工具实现加密磁盘，实现简单，可靠的解密保护。幸运又不幸的是，有一个叫DiskCryptor的工具，这个工具提供了勒索软件需要的功能。它是一种偷懒的方案，但是很聪明。

安装的组件是该工具的gui版本。这个工具号称多种加密算法实现多层保护。

[![](https://p3.ssl.qhimg.com/t01d01d91d543ccf4d0.png)](https://p3.ssl.qhimg.com/t01d01d91d543ccf4d0.png)

图1 DiskCryptor主界面和支持的加密算法

主程序没有参数（一个密码）不能完全执行。这个需要另一个组件来生成密码，但是我们还没有发现。因此在本文中用了一个假的密码测试。

一旦合适的密码被提供，Mamba通过安装DiskCryptor（安装在C:DC22）组件能很好的兼容32位和64位版本的环境。

[![](https://p0.ssl.qhimg.com/t016d66b6158c714c0f.png)](https://p0.ssl.qhimg.com/t016d66b6158c714c0f.png)

图2 安装组件

为了持续性，可执行程被安装成一个“DefragmentService”的服务，password为参数。

[![](https://p0.ssl.qhimg.com/t010c5d605fcd705791.png)](https://p0.ssl.qhimg.com/t010c5d605fcd705791.png)

图3 Mamba用一个测试密码把自己安装成一个服务

<br>

**0x02 在映射的网络磁盘上加密文件**

在全盘加密前，它也会加密所有映射的网络磁盘，进一步加大了破环程度。

显然，在比较老版本的系统上用“net use”命令枚举映射的网络磁盘。

[![](https://p4.ssl.qhimg.com/t0197748f9a420aa84e.png)](https://p4.ssl.qhimg.com/t0197748f9a420aa84e.png)

图4 检查系统版本

对于新版的操作系统（Vista及之后的），有UAC特性。这个恶意程序通过计划任务运行“net use”命令。这样就能在管理员和普通用户上下文下能更精确的映射的网络磁盘。为了访问密码保护的网络磁盘，可以使用一个免费工具（Netpass）。这个工具用来恢复存储在系统中网络密码。磁盘和网络密码列表被存储在“netuse.txt”和“netpass.txt”。

[![](https://p5.ssl.qhimg.com/t01a88b6cdcd4dae7e2.png)](https://p5.ssl.qhimg.com/t01a88b6cdcd4dae7e2.png)

图5 在新老系统中执行“net use”

[![](https://p2.ssl.qhimg.com/t01efe97dcde94f6092.png)](https://p2.ssl.qhimg.com/t01efe97dcde94f6092.png)

图6 以管理员和计划任务运行“net use”

[![](https://p0.ssl.qhimg.com/t011cd087cb3666a0ca.png)](https://p0.ssl.qhimg.com/t011cd087cb3666a0ca.png)

图7 Netpass GUI模式

用之前创建的管理员账户提升权限执行mount.exe组件加密文件。这时，它用一个包含一系列异或和左移操作的自定义算法。提供给主程序的密钥是password的一部分。密钥的MD5哈希值在将它转化为字符串之前用微软的CryptoAPI来获得。为了增加复杂性，只有字符串的一半被用来加密。

[![](https://p3.ssl.qhimg.com/t0122033808cb804d54.png)](https://p3.ssl.qhimg.com/t0122033808cb804d54.png)

图8 提权执行Mount.exe

[![](https://p4.ssl.qhimg.com/t01db6f12b94e6e4654.png)](https://p4.ssl.qhimg.com/t01db6f12b94e6e4654.png)

图9MD5 string

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a9f8c5f758851741.png)

图10文件加密过程

[![](https://p3.ssl.qhimg.com/t01a1488b9d1083554f.png)](https://p3.ssl.qhimg.com/t01a1488b9d1083554f.png)

图11在映射的网络磁盘上加密文件

## <br>

**0x03 全盘加密**

正如之前提到的，这个恶意程序的作者通过安装一个第三方工具来实现全盘加密，使得他们的工作变得简单。为了更加简单，作者把要加密的磁盘号硬编码在代码中，然后可以一个接一个加密他们。有个“-enum”的命令行可以用来枚举磁盘。

[![](https://p1.ssl.qhimg.com/t01d614914e6b20da94.png)](https://p1.ssl.qhimg.com/t01d614914e6b20da94.png)

图12用dccon.exe –enum枚举磁盘

[![](https://p5.ssl.qhimg.com/t0142c2fd5313f65871.png)](https://p5.ssl.qhimg.com/t0142c2fd5313f65871.png)

图13用dccon.exe和一个测试密码加密磁盘

[![](https://p5.ssl.qhimg.com/t011d0a92fbda960978.png)](https://p5.ssl.qhimg.com/t011d0a92fbda960978.png)

图14硬编码参数

自定义的启动引导器用下面的命令行安装：

[![](https://p1.ssl.qhimg.com/t01930ff414536a1efe.png)](https://p1.ssl.qhimg.com/t01930ff414536a1efe.png)

图15安装DiskCryptor引导启动

下一步，作者完成另一个技巧。用DiskCryptor的默认配置执行上述命令完成启动引导器安装。然后用“enter password”提示用户输入密码。那么问题来了，勒索提示来自哪里呢？

我们观察主程序看到，如果用“-config”命令行，没啥迹象。输入密码的提示消息改变了；DiskCryptor组件dcapi.dll被直接修改。

[![](https://p3.ssl.qhimg.com/t0159b42cdc9c08df16.png)](https://p3.ssl.qhimg.com/t0159b42cdc9c08df16.png)

图16被修改的dcapi.dll

似乎对于每个被感染的机器ID不是唯一的，对于所有的感染都只有一个密码。支持这个假设的证据是主程序没有任何C&amp;C服务器功能或者从被感染的系统获取密码和ID，不过也可能是之前错过了一些组件。

强制重启，只留下了一段勒索提示，除非支付完否则机器一直被锁住。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t012d7c60f75c8c99ea.png)

在加密后用DiskCryptor观察发现XTS-AES算法被使用了。

[![](https://p5.ssl.qhimg.com/t0146c87e5f6c0d86bd.png)](https://p5.ssl.qhimg.com/t0146c87e5f6c0d86bd.png)

图17加密磁盘的信息

[![](https://p4.ssl.qhimg.com/t013194053f10deee6c.png)](https://p4.ssl.qhimg.com/t013194053f10deee6c.png)

图18在加密前后转储的数据

在引导启动器被安装后，加密磁盘，安装的服务休眠了5个小时——加密过程需要的最长时间。当完成后，不管加密过程完成与否在重启系统前恶意程序部分移除了痕迹和留下了DiskCryptor。这个说明加密非常大的磁盘将要花费超过5个小时的时间，部分加密将导致数据永久损坏。

[![](https://p0.ssl.qhimg.com/t0127c3b98c07ba61f5.png)](https://p0.ssl.qhimg.com/t0127c3b98c07ba61f5.png)

图19 移除一些组件的过程

## <br>

**0x04 总结**

发现一个全盘加密的勒索软件是比较稀少的。因为实用的原因。这个对于系统控制有一个更好的全局控制，因为它能导致整个系统无法使用。它是一个可怕的事实。然而，缓慢的加密过程掩盖了这些优点。因为这个原因，除非加密过程戏剧性的加快了，否则我们相信从基于文件类型的勒索软件向全盘加密的勒索软件转变的趋势不太可能。

然而，新的勒索软件的情况表明犯罪一直不停地创新加密方式，同事尝试用工具的新的方式使他们的活动更加简单。我们预计能在其他家族的勒索软件上面看到这种趋势，因为这个更简单方便。

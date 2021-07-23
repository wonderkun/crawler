> 原文链接: https://www.anquanke.com//post/id/153723 


# Linux交换区的数据挖掘和预防


                                阅读量   
                                **281917**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者EMERIC NASI，文章来源：blog.sevagas.com
                                <br>原文地址：[http://blog.sevagas.com/?Digging-passwords-in-Linux-swap](http://blog.sevagas.com/?Digging-passwords-in-Linux-swap)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t015cb5796ae2a6da39.png)](https://p4.ssl.qhimg.com/t015cb5796ae2a6da39.png)

我曾经研究过Linux和Windows中RAM中的敏感数据，有一天我产生了“swap区有什么呢？我在那里又能找到什么呢？”的疑问。



## 一、在交换区我们可以挖掘到什么数据？

交换区是什么我在这里就不做详细解释，如果你想了解更多有关交换区的知识以及如何增加或者减少swappiness（虚拟运存控制），请点击下面的连接：[https://www.linux.com/news/all-about-linux-swap-space](https://www.linux.com/news/all-about-linux-swap-space)

要想知道你设备的交换区在磁盘的哪个位置可以使用如下命令：<br>`cat /proc/swaps`

我在安装有各种Ubuntu主要包括Kali Linux和Debian等几个操作系统的物理机和虚拟机上进行了一定的测试。发现有的系统设置的交换区非常大，而相反有的系统的交换区设置的很小甚至可以忽略。我们在交换区中能发现了什么信息呢？

下面是我在交换区中找到的东西：

> <p>Linux的帐户和明文密码<br>
Web登录/密码<br>
Email地址<br>
Wifi的SSID和密钥<br>
GPG私钥<br>
Keepass主密钥<br>
Samba证书</p>

其实可以找见的东西远远不止这些，任何你在RAM中可以找到的数据和密码都有可能被替换到交换区当中，我在自己的电脑上进行了挖掘，交换区中明文数据的数据量大到令我震惊。唯一一个令我欣慰的是我在其中没能够找到我的Veracrypt key明文密码！



## 二、如何自动挖掘交换区当中的数据？

### <a class="reference-link" name="1%EF%BC%89%E4%BD%BF%E7%94%A8%E6%AD%A3%E5%88%99%E5%8C%B9%E9%85%8D"></a>1、使用正则匹配

有些数据和容易通过正则匹配找到。例如，你想要找到通过GET或者POST请求得到的Web密码，你可以使用下面得匹配：<br>`# strings &lt;swap_device&gt; | grep "&amp;password="`<br>
如果你想要找到GET或者POST输入Web的Email，可以使用：<br>`# strings &lt;swap_device&gt; | grep -i 'email=' | grep @ | uniq`

其它的密码由于隐藏在它们自己的相关字符串中所以更难被找到，其中Linux的用户帐户就属于这种情况。在这种情况下，我们仍然可以通过观察目标周围的一些字符串找到一个合适的模式进行匹配（通过大量使用grep -C 来实现！）。<br>
例如，我发现在Ubuntu distribs上，用户的密码以明文形式被多次使用。总是有一种情况，明文密码就存储在离散列密码不远处的内存中。<br>
通过使用下面的匹配我们就有可能找到该密码：<br>`# strings &lt;swap_device&gt; | grep -C 50 &lt;hashed_password&gt; | grep &lt;clear_text_password&gt;`

即使不能找到，明文形式密码仍然很大可能存储在这片交换区内存中，因此我们可以使用该交换区的字符串做一个字典，在/etc/shadow目录下进行字典攻击，就可能获得Linux账户密码。字典攻击可能需要比较长的时间，但在面对强密码和不能破解的密码hash时仍然是一个不错的选择。

你可以在交换区中找到很多东西，如果你想仔细研究，我建议你把交换区中的字符串数据存储在只能由root用户读取的地方，然后使用grep慢慢研究吧！

当然你也可以使用我的交换区数据挖掘工具。

### <a class="reference-link" name="2%EF%BC%89%E4%BD%BF%E7%94%A8Swap%20digger%E8%84%9A%E6%9C%AC"></a>2、使用Swap digger脚本

我写了一个bash脚本[swap_digger](https://github.com/sevagas/swap_digger)，可以用于自动化挖掘交换区数据的。<br>[swap_digger](https://github.com/sevagas/swap_digger)主要功能是够自动挖掘并提取出Linux 交换区中的包括用户证书、Web表单证书、Web表单电子邮件、基于http的身份验证、Wifi SSID和密钥等在内的敏感数据。

我进行了简单的演示下面是相关截图：[![](https://p5.ssl.qhimg.com/t019690e6290db37763.png)](https://p5.ssl.qhimg.com/t019690e6290db37763.png)

更多有关详细信息和功能以及使用方法，请在Github上边访问[swap_digger](https://github.com/sevagas/swap_digger)。

**注意：Swap digging出现误报的几率很大。主要原因是它无法预测数据的存储位置以及来自同一进程的两段数据是否在交换区中相邻。**



## 三、我们能做些什么？

有以下几种可以降低交换区数据泄露风险的办法：

### <a class="reference-link" name="1%EF%BC%89%E5%AE%9A%E6%9C%9F%E6%B8%85%E7%A9%BA%E4%BA%A4%E6%8D%A2%E5%8C%BA"></a>1、定期清空交换区

交换区中的敏感数据可以保存数月，然后再被其他的内容置换掉。你可以定期擦除交换区中的数据（擦除时需要暂时禁用交换功能）。可以通过下面的命令实现交换区数据的擦除：

```
swapoff -a   ＃禁用交换区并强制数据回到RAM中
dd  if = / dev / zero of = &lt; swap_device &gt;  bs = 512  ＃清空交换区数据
mkswap &lt; swap_device &gt;  ＃重新创建交换区的文件系统
swapon -a   ＃启用交换
```

### <a class="reference-link" name="2%EF%BC%89%E5%8A%A0%E5%AF%86%E4%BA%A4%E6%8D%A2%E5%8C%BA"></a>2、加密交换区

我们也选择加密交换区，在Ubuntu上边是默认选择加密主目录的。<br>
交换区加密这种方法的确可以防止通过挂载磁盘进行取证分析和非法数据利用的，但它不能防止在实时系统受损后进行后期利用。在实时系统中，加密交换区是安装在磁盘的特殊位置中（类似于 /dev/ mapper/blah_swap）。如果你访问该设备，则交换区是以明文形式呈现。

已知的加密交换区的方法有好几种，读者可以自行搜索选择适合自己操作系统的加密方法进行加密。

### <a class="reference-link" name="3%EF%BC%89%E5%BC%80%E5%8F%91%E4%BA%BA%E5%91%98%E5%BA%94%E8%AF%A5%E5%8F%8A%E6%97%B6%E6%93%A6%E9%99%A4RAM%E4%B8%AD%E7%9A%84%E6%95%8F%E6%84%9F%E6%95%B0%E6%8D%AE%E3%80%82"></a>3、开发人员应该及时擦除RAM中的敏感数据

出于性能原因的考虑，内存分配和释放时不会擦除RAM中的相关数据。在被替换之前，释放的数据可以在RAM中保留相当长的一段时间。这是由于交换产生的问题，但是因为敏感数据也可以从进程内存中泄漏（[mimipenguin](https://github.com/huntergregal/mimipenguin)工具就是基于此的）。<br>
如果软件中包含敏感的数据（如密码），则应在该软件释放内存之前将所有值替换为零或者随机产生的垃圾数据来掩盖它。



## 四、结论

交换区是计算机取证（forensic）和拿到权限后后期利用（post exploitation）的一个重要地方。在我们的例子中，我们只是看了Linux下部分基于字符串匹配获得的数据，二进制的数据我们还没仔细研究。<br>
另外，Windows操作系统，也是可以设置交换区的。但是由于Windows交换区的相关文件（Pagefile.sys，Swapfile.sys，Hiberfile.sys）更难以阅读并且系统管理员无法访问它们，导致了Windows下交换区数据的挖掘和利用难度比较大。然而，通过使用更先进的取证方法和工具仍然是可以达到挖掘相关数据的目的的。

**在此感谢[Benjamin Chetioui](https://twitter.com/_SIben_)和[Jeremie Goldberg](https://twitter.com/BaronMillenard)帮助我进行相关测试。**<br>**感谢[Hunter Gregal](https://twitter.com/HunterGregal)，我在我的自动化挖掘脚本中使用了了他的[mimipenguin](https://github.com/sevagas/swap_digger)中的部分代码。**

**欢迎大家对[swap_digger](https://github.com/sevagas/swap_digger)评论并提出改进的意见和建议。**

**欢迎关注 [EmericNasi](http://twitter.com/EmericNasi)**

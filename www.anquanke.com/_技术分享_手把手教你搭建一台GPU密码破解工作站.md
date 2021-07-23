> 原文链接: https://www.anquanke.com//post/id/85114 


# 【技术分享】手把手教你搭建一台GPU密码破解工作站


                                阅读量   
                                **260124**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：netmux.com
                                <br>原文地址：[http://www.netmux.com/blog/how-to-build-a-password-cracking-rig](http://www.netmux.com/blog/how-to-build-a-password-cracking-rig)

译文仅供参考，具体内容表达以及含义原文为准

**[![](https://p0.ssl.qhimg.com/t01e6a5360f27348b67.gif)](https://p0.ssl.qhimg.com/t01e6a5360f27348b67.gif)**

**为什么要搭建密码破解工作站**

为什么要搭建这样一台密码破解工作站？因为这是一件非常有成就感的事情。在这篇文章中，我将一步一步的向大家介绍如何用最少的预算搭建一台密码破解工作站，满足中小企业的业务需求，也算是一个非常中肯的解决方案。在搭建工作站的过程中，我遇到的最大的困难时在Ubuntu系统下正确安装Nvidia驱动程序，但是请各位读者不要担心，我已经将在安装Nvidia驱动的过程中遇到的问题详细记录了下来，在本文下部体现出来。如果你想根据本文介绍的技术搭建一台个人工作站，你只需要准备好5000美元的预算就够了，并且运算速度不亚于Sagitta's Brutalis（[https://sagitta.pw/hardware/gpu-compute-nodes/brutalis/](https://sagitta.pw/hardware/gpu-compute-nodes/brutalis/)）。需要的硬件设备、软件安装包都会在下文列出。

这个工作站将具备强大地运算速度，但是请不要过于震惊。它的组成部分可以让你以一个合理的价格，在任何地方非常容易的搭建一个塔式服务器。完整详尽的说明将在《hash crack》第二版中介绍，但是现在你可以在Amazon上购买第一版（[http://a.co/0XFiGcQ](http://a.co/0XFiGcQ)）。

 

**搭建此工作站的预算**

如何计算搭建这个密码破解工作站的预算呢？这个预算价格5000美元的工作站主要面向人群为中小型企业、密码破解爱好者。我知道这个价格可能超出了很多爱好者的承受范围，但是你阅读完本教程后仍然会有很多收获。我想创建一个性能较好的工作站，可以破解常见的哈希类型，并且如果我们有一个完善的密码计划，我们可以在一个星期内完成常见的破解任务。

**部分硬件设备****价格清单**

1 x SuperMicro SYS-7048GR-TR 4U Server with X10DRG-Q 主板 = $1,989.99 (NewEgg)

2 x Intel Xeon E5-2620 v3 2.4 GHz LGA 2011-3 85W = $469.98 (Ebay)

4 x Nvidia GTX 1070 Founders Edition = $1,737.14 (Jet.com)

2 x Samsung 850 Pro 512GB SATA3 SSD = $412.24 (Jet.com)

4 x Kingston Server ValueRAM DDR4 2133MHz 16GB = $391.96 (NewEgg)

总计 = $5001.31（包括快递的运费、手续费等）

[![](https://p5.ssl.qhimg.com/t014e801e688a8c1fc9.png)](https://p5.ssl.qhimg.com/t014e801e688a8c1fc9.png)

**<br>**

**硬件设备的安装**

让我们看一下Supermicro 7048GR-TR主板的插槽数量及机箱内的空间。有充足的位置插入内存条、多个热插拔驱动器托架、双CPU、4个GPU同时还包括6个风扇和2个为CPU准备的额外的散热风扇。

此外，我们还需要一个带有VGA接口的外部显示器来完成操作系统及其它所需软件的安装配置。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a8d81169b3db9270.png)

首先第一步需要更换驱动器托盘（drive caddy trays）以适应上述列表中的SSD硬盘（我没有将这个驱动器托盘的价格算在总的预算中，因为如果你不介意它的加载速度慢一些的话，我们完全可以使用传统的硬件驱动，事实上这个驱动器的价格在Amazon上仅售11美元[http://a.co/d8Jo9H8](http://a.co/d8Jo9H8)），组装完成后，将它们划入前面的驱动器托架中。

[![](https://p1.ssl.qhimg.com/t0162a3b470d3ba6af9.png)](https://p1.ssl.qhimg.com/t0162a3b470d3ba6af9.png)

[![](https://p4.ssl.qhimg.com/t01e43e615b813dcef1.png)](https://p4.ssl.qhimg.com/t01e43e615b813dcef1.png)

接下来我们将安装Intel Xeon CPU（我这里使用的是Xeon E5 2620 v3系列的CPU，因为当我在选购的时候刚好Ebay上有一些折扣）

[![](https://p0.ssl.qhimg.com/t0146995d0495fc9a6e.png)](https://p0.ssl.qhimg.com/t0146995d0495fc9a6e.png)

双CPU安装完成

[![](https://p3.ssl.qhimg.com/t01a33415b0ee70ca32.png)](https://p3.ssl.qhimg.com/t01a33415b0ee70ca32.png)

接下来，我们将要安装4个16GB的内存条，因为一旦我们在CPU上安装了散热器的话，由于机箱内空间有限，再安装内存条将会变得非常困难。

[![](https://p3.ssl.qhimg.com/t01135984755da6e25d.png)](https://p3.ssl.qhimg.com/t01135984755da6e25d.png)

现在我们必须换掉包括的散热器支架，以适应这块主板。幸运的是，散热器、底座和风扇都包含在Supermicro 7048GR-TR包装盒中。还要注意的是，散热器已经均匀涂覆硅脂。

[![](https://p4.ssl.qhimg.com/t0173e201864a2cf542.png)](https://p4.ssl.qhimg.com/t0173e201864a2cf542.png)

将它们拧紧到位，但不要太紧，以防弄坏了电路板。

[![](https://p5.ssl.qhimg.com/t01eabc44d47114ffa0.png)](https://p5.ssl.qhimg.com/t01eabc44d47114ffa0.png)

现在我们需要安装散热风扇，这也包括在Supermicro 7048GR-TR的包装盒中。 将风扇插入每个CPU插槽旁边的插口，但请确保在插入电源之前按照下图所示将导线缠绕在风扇周围。

[![](https://p0.ssl.qhimg.com/t014c020b38e21c1c98.png)](https://p0.ssl.qhimg.com/t014c020b38e21c1c98.png)

现在让我们把目光聚焦在重要的事情上，我们需要移除横跨4个PCI-E 3.0插槽的背板。否则的话就没有安装4个GTX 1070 GPU的位置。

[![](https://p4.ssl.qhimg.com/t0123575f0ef57d8aff.png)](https://p4.ssl.qhimg.com/t0123575f0ef57d8aff.png)

现在开始安装第一个GPU并确认是否合适，一旦PCI-E插槽上的锁定器锁定到位，用螺丝将GPU固定，并从机箱中将背板拆除。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e14a0ba6ff49fbbd.png)

然后安装剩下的3个GPU，还要将导线插入到GPU上(确认你的工作正确无误的话就把它们绑在一起)，你会发现有两组导线相对较长，因此将它们连接到相对较远的GPU上。

[![](https://p0.ssl.qhimg.com/t01b875b931437b28fc.png)](https://p0.ssl.qhimg.com/t01b875b931437b28fc.png)

硬件设备安装完成。插上电源，设备将正常启动（不要过于惊讶^_^）。

[![](https://p4.ssl.qhimg.com/t01e0616618e4e33d17.png)](https://p4.ssl.qhimg.com/t01e0616618e4e33d17.png)

**<br>**

**安装软件**

我花费了几天的时间编写和完善了这份软件安装文档。因为我已经记录了在安装过程中遇到的全部困难和解决办法，你可以非常顺利的执行每一步操作。如果你遵循这份文档，你可以很轻松的搭建基于Intel OpenCL CPU和Nvidia GTX 10 系列GPU的密码破解工作站。

我知道有的读者此时会产生一些疑问为啥我使用的是Ubuntu桌面版而不是Ubuntu服务器版，因为我打算在不需要密码破解的时候将这台服务器用作其他用途，因此安装桌面版还是很有必要的。所需要软件的下载链接都会在下面列出，在本文中我不会告诉你如何使用U盘做Ubuntu系统，因为这超出了本文的范围，

关于如何使用U盘做Ubuntu系统，你可以点击这里了解（[https://help.ubuntu.com/community/Installation/FromUSBStick](https://help.ubuntu.com/community/Installation/FromUSBStick)）。

同样，这些操作步骤只适用于具有Intel OpenCLCPU和Nvidia GTX 10系列GPU的机器上。 

**<br>**

**需要的软件**

-Ubuntu 14.0.4.5 Desktop amd64（[http://releases.ubuntu.com/14.04/](http://releases.ubuntu.com/14.04/)）

-Intel OpenCL Runtime 16.1 x64 Ubuntu Driver

([http://registrationcenter-download.intel.com/akdlm/irc_nas/9019/opencl_runtime_16.1_x64_ubuntu_5.2.0.10002.tgz](http://registrationcenter-download.intel.com/akdlm/irc_nas/9019/opencl_runtime_16.1_x64_ubuntu_5.2.0.10002.tgz))

-Nvidia Linux x86_64 375.20 Driver

（[http://www.nvidia.com/download/driverResults.aspx/111596/en-us](http://www.nvidia.com/download/driverResults.aspx/111596/en-us)）

-Hashcat v3.20（[https://hashcat.net/hashcat/](https://hashcat.net/hashcat/)）

**<br>**

**安装步骤**

**1)安装Ubuntu 14.0.4.5**

确保在BIOS中启用从USB启动安装Ubuntu镜像。 完成后按以下步骤操作：

1.设置为在引导时不自动登录

2.确保你的工作站可以通过网线或WiFi访问到互联网

3.从终端安装执行下列命令安装更新：



```
sudo apt-get update
sudo apt-get upgrade -y
```

**2)安装Intel OpenCL驱动**

1.从终端安装依赖项



```
sudo apt-get install lsb-core -y
sudo apt-get install opencl-headers -y
```

2.将Intel OpenCL驱动程序

（[http://registrationcenter-download.intel.com/akdlm/irc_nas/9019/opencl_runtime_16.1_x64_ubuntu_5.2.0.10002.tgz](http://registrationcenter-download.intel.com/akdlm/irc_nas/9019/opencl_runtime_16.1_x64_ubuntu_5.2.0.10002.tgz)）下载到“Downloads”目录中

3.下载Nvidia Linux x86_64 375.30驱动程序

（[http://www.nvidia.com/download/driverResults.aspx/111596/en-us](http://www.nvidia.com/download/driverResults.aspx/111596/en-us)）到“Downloads”目录

在终端中执行如下命令：



```
cd Downloads
tar -xvzf opencl_runtime_16.1_x64_ubuntu_5.2.0.10002.tgz
cd opencl_runtime_16.1_x64_ubuntu_5.2.0.10002 /
sudo bash install.sh
Accept Terms of Agreement and install（接受协议条款并安装）
```

3)安装Hashcat v3.20



```
1 sudo apt-get install git -y
2 cd ~/Desktop
3 git clone https://github.com/hashcat/hashcat.git
4 cd hashcat/
5 git submodule update --init --recursive
6 sudo make
7 sudo make install
8 reboot server
```

4)安装Nvidia Linux x86_64 375.20驱动

1.重启机器，并且不要登录

2.在登录界面按Ctrl + Alt + F1键，在命令提示符下输入账号密码登录

3.创建/etc/modprobe.d/blacklist-nouveau.conf文件



```
cd /etc/modprobe.d/
sudo touch blacklist-nouveau.conf
sudo vi blacklist-nouveau.conf
```

在该文件中输入如下内容



```
blacklist nouveau
options nouveau modeset=0
```

4.sudo update-initramfs -u

5.重启系统

```
sudo reboot
```

6.重启后不要登录

7.在登录界面按Ctrl + Alt + F1键在命令提示符下输入账号密码登录

8.跳转到"Downloads"目录下你会看到文件VIDIA-Linux-x86_64-375.20.run

执行命令为该文件赋予可执行权限

```
chmod a+x .
```

9.sudo service lightdm stop

10.sudo bash NVIDIA-Linux-x86_64-375.20.run –no-opengl-files

注意：–no-opengl-files参数非常重要，一定不要忘了添加

11.安装驱动

-Accept License（接受协议）

-Select Continue Installation（选择继续安装）

-Select “NO” to not install 32bit files（选择NO不要安装32位文件）

-Select “NO” to rebuilding any Xserver configurations with Nvidia.（选择“NO”，使用Nvidia重建任何Xserver配置。）

12.sudo modprobe nvidia

13.sudo service lightdm start

14.Ctrl + Alt + F7

在图形界面下登录，完成，可以使用HASHCAT破解密码了

 

**其它参考&amp;温度**

820瓦=峰值使用观察**风扇不要达到100%并且不能超频

83c =测试在100％负载下8小时的温度

〜127GH / s NTLM =破解速度：每秒1270亿

~26 GH/s SHA1 = 破解速度：每秒260亿

~31 MH/s md5加密 = 破解速度：每秒310亿

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bd27dea89a436137.png)

我知道你看到这个图片后会非常的震惊，谁会认为GPU在运行的时候会这么热，但是看到冷却的清晰分离是非常有趣的。高端Nvidia系列GPU像1080采用气室冷却技术控制散热。

 

**总结**

不得不说，我为这个设备和它未来的潜力感到自豪，在选择的硬件和复合成本之间总是存在权衡，但是我认为我已经在建立这个工作站的过程中获得了很多的成就感。坚如磐石的表现，我的劳动成果就在那里摆着，显而易见，不需要其它人过多的评价，就可以获得技术上的满足。随着硬件价格的不断下降，密码破解技术的不断发展，现有的技术将会过时，但是不要担心，我将不断更新这篇文章，以适应最新的硬件&amp;密码破解技术，所以可以在Twitter上联系我@netmux，或者订阅这个博客。

 如果你想要一个全面的参考手册，可以参考这本书。《HASH CRACK》（[http://a.co/fu45rMW](http://a.co/fu45rMW)）

[![](https://p4.ssl.qhimg.com/t017c9334419207de51.png)](https://p4.ssl.qhimg.com/t017c9334419207de51.png)

**<br>**

**HASHCAT破解哈希速度参考手册**

```
HASHCAT v3.2
OpenCL Platform #1: Intel(R) Corporation
========================================
* Device #1: Intel(R) Xeon(R) CPU E5-2620 v3 @ 2.40GHz, skipped
OpenCL Platform #2: NVIDIA Corporation
======================================
* Device #2: GeForce GTX 1070, 2036/8145 MB allocatable, 15MCU
* Device #3: GeForce GTX 1070, 2036/8145 MB allocatable, 15MCU
* Device #4: GeForce GTX 1070, 2036/8145 MB allocatable, 15MCU
* Device #5: GeForce GTX 1070, 2036/8145 MB allocatable, 15MCU
Hashtype: MD4
Speed.Dev.#*.....: 137.9 GH/s
Hashtype: MD5
Speed.Dev.#*.....: 76526.9 MH/s
Hashtype: Half MD5
Speed.Dev.#*.....: 46527.5 MH/s
Hashtype: SHA1
Speed.Dev.#*.....: 25963.3 MH/s
Hashtype: SHA256
Speed.Dev.#*.....: 9392.1 MH/s
Hashtype: SHA384
Speed.Dev.#*.....: 3169.4 MH/s
Hashtype: SHA512
Speed.Dev.#*.....: 3235.0 MH/s
Hashtype: SHA-3(Keccak)
Speed.Dev.#*.....: 2500.4 MH/s
Hashtype: SipHash
Speed.Dev.#*.....: 86713.2 MH/s
Hashtype: RipeMD160
Speed.Dev.#*.....: 14689.1 MH/s
Hashtype: Whirlpool
Speed.Dev.#*.....: 780.4 MH/s
Hashtype: GOST R 34.11-94
Speed.Dev.#*.....: 740.2 MH/s
Hashtype: GOST R 34.11-2012 (Streebog) 256-bit
Speed.Dev.#*.....: 153.7 MH/s
Hashtype: GOST R 34.11-2012 (Streebog) 512-bit
Speed.Dev.#*.....: 153.9 MH/s
Hashtype: DES (PT = $salt, key = $pass)
Speed.Dev.#*.....: 56140.1 MH/s
Hashtype: 3DES (PT = $salt, key = $pass)
Speed.Dev.#*.....: 1737.5 MH/s
Hashtype: phpass, MD5(WordPress), MD5(phpBB3), MD5(Joomla)
Speed.Dev.#*.....: 20491.9 kH/s
Hashtype: scrypt
Speed.Dev.#*.....: 1872.4 kH/s
Hashtype: PBKDF2-HMAC-MD5
Speed.Dev.#*.....: 22181.7 kH/s
Hashtype: PBKDF2-HMAC-SHA1
Speed.Dev.#*.....: 9692.5 kH/s
Hashtype: PBKDF2-HMAC-SHA256
Speed.Dev.#*.....: 3582.7 kH/s
Hashtype: PBKDF2-HMAC-SHA512
Speed.Dev.#*.....: 1303.1 kH/s
Hashtype: Skype
Speed.Dev.#*.....: 38566.4 MH/s
Hashtype: WPA/WPA2
Speed.Dev.#*.....: 1190.5 kH/s
Hashtype: IKE-PSK MD5
Speed.Dev.#*.....: 5276.2 MH/s
Hashtype: IKE-PSK SHA1
Speed.Dev.#*.....: 2339.9 MH/s
Hashtype: NetNTLMv1-VANILLA / NetNTLMv1+ESS
Speed.Dev.#*.....: 67492.1 MH/s
Hashtype: NetNTLMv2
Speed.Dev.#*.....: 4943.9 MH/s
Hashtype: IPMI2 RAKP HMAC-SHA1
Speed.Dev.#*.....: 4982.4 MH/s
Hashtype: Kerberos 5 AS-REQ Pre-Auth etype 23
Speed.Dev.#*.....: 887.1 MH/s
Hashtype: Kerberos 5 TGS-REP etype 23
Speed.Dev.#*.....: 879.8 MH/s
Hashtype: DNSSEC (NSEC3)
Speed.Dev.#*.....: 10034.7 MH/s
Hashtype: PostgreSQL Challenge-Response Authentication (MD5)
Speed.Dev.#*.....: 19820.9 MH/s
Hashtype: MySQL Challenge-Response Authentication (SHA1)
Speed.Dev.#*.....: 6877.8 MH/s
Hashtype: SIP digest authentication (MD5)
Speed.Dev.#*.....: 6100.2 MH/s
Hashtype: SMF &gt; v1.1
Speed.Dev.#*.....: 20392.8 MH/s
Hashtype: vBulletin &lt; v3.8.5
Speed.Dev.#*.....: 20195.7 MH/s
Hashtype: vBulletin &gt; v3.8.5
Speed.Dev.#*.....: 14241.8 MH/s
Hashtype: IPB2+, MyBB1.2+
Speed.Dev.#*.....: 14878.4 MH/s
Hashtype: WBB3, Woltlab Burning Board 3
Speed.Dev.#*.....: 3802.6 MH/s
Hashtype: OpenCart
Speed.Dev.#*.....: 6078.5 MH/s
Hashtype: Joomla &lt; 2.5.18
Speed.Dev.#*.....: 75182.7 MH/s
Hashtype: PHPS
Speed.Dev.#*.....: 20610.0 MH/s
Hashtype: Drupal7
Speed.Dev.#*.....: 167.2 kH/s
Hashtype: osCommerce, xt:Commerce
Speed.Dev.#*.....: 38238.3 MH/s
Hashtype: PrestaShop
Speed.Dev.#*.....: 24166.2 MH/s
Hashtype: Django (SHA-1)
Speed.Dev.#*.....: 20395.9 MH/s
Hashtype: Django (PBKDF2-SHA256)
Speed.Dev.#*.....: 178.3 kH/s
Hashtype: Mediawiki B type
Speed.Dev.#*.....: 19359.7 MH/s
Hashtype: Redmine Project Management Web App
Speed.Dev.#*.....: 6212.0 MH/s
Hashtype: PostgreSQL
Speed.Dev.#*.....: 75109.6 MH/s
Hashtype: MSSQL(2000)
Speed.Dev.#*.....: 25596.7 MH/s
Hashtype: MSSQL(2005)
Speed.Dev.#*.....: 25581.7 MH/s
Hashtype: MSSQL(2012)
Speed.Dev.#*.....: 3066.1 MH/s
Hashtype: MySQL323
Speed.Dev.#*.....: 158.2 GH/s
Hashtype: MySQL4.1/MySQL5
Speed.Dev.#*.....: 11261.0 MH/s
Hashtype: Oracle H: Type (Oracle 7+)
Speed.Dev.#*.....: 2908.6 MH/s
Hashtype: Oracle S: Type (Oracle 11+)
Speed.Dev.#*.....: 25383.8 MH/s
Hashtype: Oracle T: Type (Oracle 12+)
Speed.Dev.#*.....: 316.9 kH/s
Hashtype: Sybase ASE
Speed.Dev.#*.....: 1160.3 MH/s
Hashtype: EPiServer 6.x &lt; v4
Speed.Dev.#*.....: 20411.9 MH/s
Hashtype: EPiServer 6.x &gt; v4
Speed.Dev.#*.....: 8381.3 MH/s
Hashtype: md5apr1, MD5(APR), Apache MD5
Speed.Dev.#*.....: 30443.1 kH/s
Hashtype: ColdFusion 10+
Speed.Dev.#*.....: 5144.0 MH/s
Hashtype: hMailServer
Speed.Dev.#*.....: 8359.2 MH/s
Hashtype: SHA-1(Base64), nsldap, Netscape LDAP SHA
Speed.Dev.#*.....: 25531.9 MH/s
Hashtype: SSHA-1(Base64), nsldaps, Netscape LDAP SSHA
Speed.Dev.#*.....: 25530.0 MH/s
Hashtype: SSHA-512(Base64), LDAP `{`SSHA512`}`
Speed.Dev.#*.....: 3186.0 MH/s
Hashtype: LM
Speed.Dev.#*.....: 55244.2 MH/s
Hashtype: NTLM
Speed.Dev.#*.....: 123.6 GH/s
Hashtype: Domain Cached Credentials (DCC), MS Cache
Speed.Dev.#*.....: 34610.3 MH/s
Hashtype: Domain Cached Credentials 2 (DCC2), MS Cache 2
Speed.Dev.#*.....: 962.5 kH/s
Hashtype: MS-AzureSync PBKDF2-HMAC-SHA256
Speed.Dev.#*.....: 31233.0 kH/s
Hashtype: descrypt, DES(Unix), Traditional DES
Speed.Dev.#*.....: 2693.9 MH/s
Hashtype: BSDiCrypt, Extended DES
Speed.Dev.#*.....: 4644.9 kH/s
Hashtype: md5crypt, MD5(Unix), FreeBSD MD5, Cisco-IOS MD5
Speed.Dev.#*.....: 30373.0 kH/s
Hashtype: bcrypt, Blowfish(OpenBSD)
Speed.Dev.#*.....: 43551 H/s
Hashtype: sha256crypt, SHA256(Unix)
Speed.Dev.#*.....: 1119.1 kH/s
Hashtype: sha512crypt, SHA512(Unix)
Speed.Dev.#*.....: 452.4 kH/s
Hashtype: OSX v10.4, v10.5, v10.6
Speed.Dev.#*.....: 20460.9 MH/s
Hashtype: OSX v10.7
Speed.Dev.#*.....: 2807.7 MH/s
Hashtype: OSX v10.8+
Speed.Dev.#*.....: 36781 H/s
Hashtype: AIX `{`smd5`}`
Speed.Dev.#*.....: 30276.5 kH/s
Hashtype: AIX `{`ssha1`}`
Speed.Dev.#*.....: 133.5 MH/s
Hashtype: AIX `{`ssha256`}`
Speed.Dev.#*.....: 49406.4 kH/s
Hashtype: AIX `{`ssha512`}`
Speed.Dev.#*.....: 19433.0 kH/s
Hashtype: Cisco-PIX MD5
Speed.Dev.#*.....: 48626.6 MH/s
Hashtype: Cisco-ASA MD5
Speed.Dev.#*.....: 52994.5 MH/s
Hashtype: Cisco-IOS SHA256
Speed.Dev.#*.....: 9226.9 MH/s
Hashtype: Cisco $8$
Speed.Dev.#*.....: 177.9 kH/s
Hashtype: Cisco $9$
Speed.Dev.#*.....: 50522 H/s
Hashtype: Juniper Netscreen/SSG (ScreenOS)
Speed.Dev.#*.....: 36738.6 MH/s
Hashtype: Juniper IVE
Speed.Dev.#*.....: 30130.1 kH/s
Hashtype: Android PIN
Speed.Dev.#*.....: 16053.8 kH/s
Hashtype: Citrix NetScaler
Speed.Dev.#*.....: 21787.7 MH/s
Hashtype: RACF
Speed.Dev.#*.....: 7799.3 MH/s
Hashtype: GRUB 2
Speed.Dev.#*.....: 128.7 kH/s
Hashtype: Radmin2
Speed.Dev.#*.....: 25038.3 MH/s
Hashtype: SAP CODVN B (BCODE)
Speed.Dev.#*.....: 6866.1 MH/s
Hashtype: SAP CODVN F/G (PASSCODE)
Speed.Dev.#*.....: 3126.7 MH/s
Hashtype: SAP CODVN H (PWDSALTEDHASH) iSSHA-1
Speed.Dev.#*.....: 17913.0 kH/s
Hashtype: Lotus Notes/Domino 5
Speed.Dev.#*.....: 645.2 MH/s
Hashtype: Lotus Notes/Domino 6
Speed.Dev.#*.....: 216.3 MH/s
Hashtype: Lotus Notes/Domino 8
Speed.Dev.#*.....: 1934.4 kH/s
Hashtype: PeopleSoft
Speed.Dev.#*.....: 25445.7 MH/s
Hashtype: PeopleSoft PS_TOKEN
Speed.Dev.#*.....: 9339.2 MH/s
Hashtype: 7-Zip
Speed.Dev.#*.....: 28257 H/s
Hashtype: WinZip
Speed.Dev.#*.....: 3216.6 kH/s
Hashtype: RAR3-hp
Speed.Dev.#*.....: 99770 H/s
Hashtype: RAR5
Speed.Dev.#*.....: 108.3 kH/s
Hashtype: AxCrypt
Speed.Dev.#*.....: 349.8 kH/s
Hashtype: AxCrypt in memory SHA1
Speed.Dev.#*.....: 23241.1 MH/s
Hashtype: TrueCrypt PBKDF2-HMAC-RipeMD160 + XTS 512 bit
Speed.Dev.#*.....: 793.9 kH/s
Hashtype: TrueCrypt PBKDF2-HMAC-SHA512 + XTS 512 bit
Speed.Dev.#*.....: 1120.8 kH/s
Hashtype: TrueCrypt PBKDF2-HMAC-Whirlpool + XTS 512 bit
Speed.Dev.#*.....: 109.7 kH/s
Hashtype: TrueCrypt PBKDF2-HMAC-RipeMD160 + XTS 512 bit + boot-mode
Speed.Dev.#*.....: 1480.7 kH/s
Hashtype: VeraCrypt PBKDF2-HMAC-RipeMD160 + XTS 512 bit
Speed.Dev.#*.....: 2476 H/s
Hashtype: VeraCrypt PBKDF2-HMAC-SHA512 + XTS 512 bit
Speed.Dev.#*.....: 2569 H/s
Hashtype: VeraCrypt PBKDF2-HMAC-Whirlpool + XTS 512 bit
Speed.Dev.#*.....: 124 H/s
Hashtype: VeraCrypt PBKDF2-HMAC-RipeMD160 + XTS 512 bit + boot-mode
Speed.Dev.#*.....: 5063 H/s
Hashtype: VeraCrypt PBKDF2-HMAC-SHA256 + XTS 512 bit
Speed.Dev.#*.....: 3342 H/s
Hashtype: VeraCrypt PBKDF2-HMAC-SHA256 + XTS 512 bit + boot-mod
Speed.Dev.#*.....: 8433 H/s
Hashtype: Android FDE &lt;= 4.3
Speed.Dev.#*.....: 2366.6 kH/s
Hashtype: Android FDE (Samsung DEK)
Speed.Dev.#*.....: 863.1 kH/s
Hashtype: eCryptfs
Speed.Dev.#*.....: 39401 H/s
Hashtype: MS Office &lt;= 2003 MD5 + RC4, oldoffice$0, oldoffice$1
Speed.Dev.#*.....: 685.3 MH/s
Hashtype: MS Office &lt;= 2003 MD5 + RC4, collision-mode #1
Speed.Dev.#*.....: 980.4 MH/s
Hashtype: MS Office &lt;= 2003 SHA1 + RC4, oldoffice$3, oldoffice$4
Speed.Dev.#*.....: 890.8 MH/s
Hashtype: MS Office &lt;= 2003 SHA1 + RC4, collision-mode #1
Speed.Dev.#*.....: 1000.7 MH/s
Hashtype: Office 2007
Speed.Dev.#*.....: 386.2 kH/s
Hashtype: Office 2010
Speed.Dev.#*.....: 192.9 kH/s
Hashtype: Office 2013
Speed.Dev.#*.....: 25923 H/s
Hashtype: PDF 1.1 - 1.3 (Acrobat 2 - 4)
Speed.Dev.#*.....: 1013.4 MH/s
Hashtype: PDF 1.1 - 1.3 (Acrobat 2 - 4) + collider-mode #1
Speed.Dev.#*.....: 1128.2 MH/s
Hashtype: PDF 1.4 - 1.6 (Acrobat 5 - 8)
Speed.Dev.#*.....: 50091.0 kH/s
Hashtype: PDF 1.7 Level 3 (Acrobat 9)
Speed.Dev.#*.....: 9227.4 MH/s
Hashtype: PDF 1.7 Level 8 (Acrobat 10 - 11)
Speed.Dev.#*.....: 96326 H/s
Hashtype: Password Safe v2
Speed.Dev.#*.....: 979.7 kH/s
Hashtype: Password Safe v3
Speed.Dev.#*.....: 3613.3 kH/s
Hashtype: Lastpass
Speed.Dev.#*.....: 6804.1 kH/s
Hashtype: 1Password, agilekeychain
Speed.Dev.#*.....: 9649.3 kH/s
Hashtype: 1Password, cloudkeychain
Speed.Dev.#*.....: 32199 H/s
Hashtype: Bitcoin/Litecoin wallet.dat
Speed.Dev.#*.....: 12914 H/s
Hashtype: Blockchain, My Wallet
Speed.Dev.#*.....: 187.0 MH/s
Hashtype: Keepass 1 (AES/Twofish) and Keepass 2 (AES)
Speed.Dev.#*.....: 416.5 kH/s
Hashtype: ArubaOS
Speed.Dev.#*.....: 20293.3 MH/s
```

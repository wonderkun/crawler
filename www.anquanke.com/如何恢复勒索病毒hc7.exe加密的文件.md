> 原文链接: https://www.anquanke.com//post/id/89533 


# 如何恢复勒索病毒hc7.exe加密的文件


                                阅读量   
                                **90252**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Michael Young and Ryan Zisk，文章来源：yrz.io
                                <br>原文地址：[https://yrz.io/decrypting-hc7/](https://yrz.io/decrypting-hc7/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01a83def7b4dc99667.jpg)](https://p3.ssl.qhimg.com/t01a83def7b4dc99667.jpg)



## 背景

<!-- [if gte mso 9]&gt;-->

<!-- [if gte mso 9]&gt;-->

近期，我们发现某客户网络中存在一个恶意的终端，它能寻找弱凭据的服务器，并以外部RDP的方式访问，最终对服务器进行破坏。当成功入侵后，攻击者会在环境中放置一个新的勒索软件变体，并试图通过PsExec，将该恶意的可执行文件传播到整个域中。

我们所发现的恶意文件样本名称为hc7.exe，它会对计算机中的大量数据以及可执行文件进行加密。通过研究，我们成功找到了解密数据和文件的方法。在这里，还要特别提醒想进行解密复现的各位，你们不一定要安装下文中的Volatility，因为该工具只用于对内存进行分析。

我们首先简单地查阅了一些相关资料，发现[Michael Gillespie](https://twitter.com/demonslay335)曾经发表过关于另一个较为相似的变种（hc6）的一系列文章。此前，我曾经和Michael以及Emsisoft的Wosar共同研究过一个[勒索软件](https://yrz.io/decrypting-the-negozi-ransomware)，因此，我与他取得了联系，并得到了他们二位的大力协助。

Michael此前已经成功将变种hc6解密，通过对比我们发现，hc7是在hc6基础上修改得到的可执行文件。其不同点在于：hc7使用了一个提供的用户参数，来替代此前hc6中的硬编码值（Hardcoded Value）。

[![](https://yrz.io/images/hc7_image6.png)](https://yrz.io/images/hc7_image6.png)



## 获取内存内容

<!-- [if !mso]&gt;-->

作为一种临时防范措施，我们的客户已经将大部分计算机关掉，试图借此来阻止勒索病毒的传播。但幸运的是，我们发现还有一台计算机没有被关闭，并且并没有员工对其进行操作。考虑到这一点，我们立即将该计算机的内存状态进行转储，从而方便我们对病毒的离线分析，与此同时，我们的团队也可以同时执行恢复工作。

首先，我们使用了Magnet Forensics公司的RAM Capture实用程序，将被感染的Windows 10工作站的内存复制并写入磁盘。在Windows环境下，目前有多种工具都可以转储RAM，但根据经验，我们使用的Magnet系列工具是最为好用的。

在将RAM内容转储到磁盘之前，需要注意确保所选择的目标磁盘有足够的空间，所需空间与该计算机RAM的物理大小是一致的。具体到我们这台，该工作站有8GB的物理RAM，并且同时有足够的磁盘空间用来转储。虽然Magnet实用程序提供了一个[图形界面](https://www.magnetforensics.com/computer-forensics/acquiring-memory-with-magnet-ram-capture/)，但我还是更喜欢使用命令行，因为借助命令行可以更方便的远程操作，此外还能更方便地编写脚本。

[![](https://yrz.io/images/hc7_image2.png)](https://yrz.io/images/hc7_image2.png)

在这里，我们需要远程控制客户端，并且还需要传输文件来分析内存中的内容。在这里我们建议，在传输文件前应该对其进行压缩，这样能显著缩小文件的大小，从而加快传输速度。经过尝试，我们采用7zip格式压缩后，文件大小已经减少了将近一半，约为4GB，这就为我们节约了很多宝贵的时间。[![](https://yrz.io/images/hc7_image7.png)](https://yrz.io/images/hc7_image7.png)

## 

## 寻找加密密钥

<!-- [if !mso]&gt;-->

当我们传回文件之后，就可以使用Volatility进行分析。Volatility是一个非常出色的内存取证工具包，该工具包支持多种不同的操作系统，可以从内存中提取出有用的信息。关于如何安装Volatility，请参考[这里](https://github.com/volatilityfoundation/volatility/wiki/Installation)。关于使用Volatility过程中所涉及到的命令，请参考[这里](https://github.com/volatilityfoundation/volatility/wiki/Command-Reference)。尽管我们可以在很多种操作系统上安装Volatility，但我还是更倾向于Linux环境，这样我们就可以使用grep来筛选输出内容。

首先，我们在命令提示符中输入“ver”，以获得所获取RAM映像的主机的具体操作系统版本和内部版本号。我们现在分析的RAM，是来自一台64位的Windows 10计算机，其内部版本号为Build 15063。了解系统的版本非常重要，因为我们后面，必须针对该内存文件，在Volatility上进行相应的配置，这样才能得到有效且准确的结果。如果在使用Volatility过程中，出现了长时间的挂起状态，或者出现了报错，那么就应该重新检查并保证配置文件全部正确。如需查看列表，请使用–info。

[![](https://yrz.io/images/hc7_image5.png)](https://yrz.io/images/hc7_image5.png)

为了验证Volatility是否能够正常工作，我们可以使用一些基本命令，来确保能从内存映像中正确解析出数据。比如，我们可以检查一下是否能查看主机的进程列表。

[![](https://yrz.io/images/hc7_image4.png)](https://yrz.io/images/hc7_image4.png)

通常情况下，例如cmdscan和consoles这样的Volatility内置模块会产生我们想要查找的信息（由用户通过命令行提供的密码）。在这种情况下，我们就不能通过任何方法找到该命令。反之，我们可以提取RAM中的字符串，通过搜索来得到更多的信息。具体而言，我们可以利用Sysinternals工具的“strings.exe”应用程序，将原始字符串数据写入到文本文件。

[![](https://yrz.io/images/hc7_image3.png)](https://yrz.io/images/hc7_image3.png)

我们首先利用了Volatility中的“strings”插件，将原始数据转换为更方便我们分析的数据。我们使用“strings”模块将ram_strings.txt文件导入到Volatility中，将数据映射到操作系统中的特定内存地址。尽管这一步，很可能并不需要hc7勒索病毒的密码，但为了过程的完整性，我们还是加入了相应的步骤。在通常的分析过程中，这是一个可以获得能使用grep的字符串输出的常用方法。

[![](https://yrz.io/images/hc7_image1.png)](https://yrz.io/images/hc7_image1.png)

后来我们发现，借助Volatility进行的字符串转换过程是没有必要的。因为，我们可以直接使用strings.exe从捕获的RAM中提取密码。在文件被复制到磁盘后，我们可以简单地执行findstr，来获取相关的文本文件，以希望能获取到我们想要的密码。经过尝试，在搜索了“psexesvc”之后，我们找到了一个疑似密码的匹配项，如下所示。

[![](https://yrz.io/images/hc7_image8.png)](https://yrz.io/images/hc7_image8.png)

我们发现，命令行中所显示的密码显然是一个人工输入的密码，因为该密码中包含客户的企业名称。要解密数据，显然还需要进一步的工作。首先，尝试反编译hc7.exe PyInstaller包。我们使用[Pyinstxtractor](https://sourceforge.net/projects/pyinstallerextractor/)来提取捆绑的可执行文件的包内容，但在反编译主要的“hc9”脚本过程中，遇到了一些问题。随后，我又找到Michael Gillespie寻求帮助，他说他在分析hc6时也遇到了同样的情况。根据Michael提供的办法，我们参考了[0xec_编写的教程](https://twitter.com/demonslay335/status/936721282221137920)，将Python2.7的magic header注入到可执行文件中，由此就解决了这一问题。

 [![](https://yrz.io/images/hc7_image9.png)](https://yrz.io/images/hc7_image9.png)

## 

## 解密过程

<!-- [if gte mso 9]&gt;-->

<!-- [if gte mso 9]&gt;-->

我们参考了0xec博客上[关于hc6逆向的文章](https://0xec.blogspot.com/2017/12/reversing-pyinstaller-based-ransomware.html)，他是借助HxD，将相关字节注入到文件的开始部分，并使用pycdc来将其正确地反编译。经过代码审计，我们发现代码非常相似。更幸运的是，攻击者还在hc6变种中留下了一个函数，该函数可以完成所有的工作。我们参考0xec博客中给出的hc6解密函数，写了一个简单的脚本，并通过我们从RAM中恢复的代码，成功解密了一个文件。

```
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
import os
import random
import sys
import base64
FILE_EXTENSION = '.GOTYA'
def getDigest(password):
   hasher = SHA256.new(password)
   return hasher.digest()
def decrypt(key, FileName):
   OutputFile = os.path.join(os.path.dirname(FileName), os.path.basename(FileName.replace(FILE_EXTENSION, '')))
   chunkS = 65536
   with open(FileName, 'rb') as infile:
       fileS = infile.read(16)
       IniVect = infile.read(16)
       decryptor = AES.new(key, AES.MODE_CBC, IniVect)
       with open(OutputFile, 'wb') as outfile:
           while True:
               chunk = infile.read(chunkS)
               if len(chunk) == 0:
                   break
               outfile.write(decryptor.decrypt(chunk))
           outfile.truncate(int(fileS))
def run_decrypt():
   if len(sys.argv) &lt; 3:
       print('Error')
       sys.exit(0)
   password = sys.argv[1]
   filename = sys.argv[2]
   decrypt(getDigest(password), filename)
if __name__ == "__main__":
   run_decrypt()
```



## 结语

<!-- [if gte mso 9]&gt;-->

<!-- [if gte mso 9]&gt;-->

感谢demonslay335对这一系列研究所提供的帮助，同时感谢[0xec_](https://twitter.com/0xec_)针对逆向hc6变种给出的优秀指导。对于受该病毒感染的用户，都可以按照上述方法来进行解密操作。此外，demonslay335还更新了他的[hc6解密器](https://twitter.com/demonslay335/status/937728159084089344)，更新后的版本将允许用户提供已经找到的密码。

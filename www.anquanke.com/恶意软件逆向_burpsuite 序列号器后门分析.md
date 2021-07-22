> 原文链接: https://www.anquanke.com//post/id/96866 


# 恶意软件逆向：burpsuite 序列号器后门分析


                                阅读量   
                                **268753**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">5</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者lkw，文章来源：0x00sec.org
                                <br>原文地址：[https://www.0x00sec.org/t/malware-reversing-burpsuite-keygen/5167](https://www.0x00sec.org/t/malware-reversing-burpsuite-keygen/5167)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01b441c22f85167a34.jpg)](https://p2.ssl.qhimg.com/t01b441c22f85167a34.jpg)

> 免责声明：本文中包含病毒样本，处理该样本存在一定的安全风险，后果自负。如果条件允许，请使用虚拟机来运行该样本。

### **特别鸣谢：吾爱破解论坛提供无后门安全版本**

### **Burp Suite Pro Loader&amp;Keygen By surferxyz（附带v1.7.31原版）**

### **https://www.52pojie.cn/thread-691448-1-1.html**

### **(出处: 吾爱破解论坛)**



## 一、前言

昵称为<a>@the_heat_man</a>的某些随机新“用户”多次在各种论坛上发布了一些文件（因为文件多次被删），并宣称这些文件为burpsuite的keygen（注册机）。论坛上好多用户怀疑该文件是恶意软件。我和<a>@Leeky</a>、<a>@dtm</a>、<a>@Cry0l1t3</a>以及<a>@L0k1</a>决定逆向分析这款软件，看一下我们的猜测是否正确。令人惊讶的是，虽然该工具包含一个远程访问木马（RAT， remote access trojan），但的确也包含可用的keygen。因此，受法律条款约束，本文中我没有给出原始文件的具体链接。



## 二、木马分析

现在我们详细分析一下这款RAT。

keygen中包含一个`virus.txt`文件，文件内容为一个网页[链接](https://www.virustotal.com/#/file/6530b29367de2b0fa42c411f94ae734d745443256431aee0fe221acb7a75c103/detection)，链接指向virustotal对keygen jar文件的扫描结果。

[![](https://p1.ssl.qhimg.com/t0173901902c195f13f.png)](https://p1.ssl.qhimg.com/t0173901902c195f13f.png)

然而virus total上显示的哈希与实际文件并不匹配，表明该网站实际上扫描的是另一个文件，VT上的哈希为：

```
VT: SHA-256    6530b29367de2b0fa42c411f94ae734d745443256431aee0fe221acb7a75c103
```

实际文件哈希值为：

```
&gt; shasum -a 256 burp-loader-keygen1.7.31.jar
1bf764e77a543def4c623e6e207b1b72999f6550cf49651b88d53f80ae10e4d7  burp-loader-keygen1.7.31.jar
```

jar文件实际上就是zip文件，因此我们可以使用unzip命令解压jar文件。

```
&gt; cp burp-loader-keygen1.7.31.jar burp-loader-keygen1.7.31.zip
&gt; unzip burp-loader-keygen1.7.31.zip
Archive:  burp-loader-keygen1.7.31.zip
   creating: META-INF/
 extracting: META-INF/MANIFEST.MF    
   creating: burploader/
 extracting: burploader/Burploader.class  
 extracting: burploader/Data.bin
```

解压结果中包含一个class文件，我们可以反编译这个类文件。我使用的是jad工具，kali上已经安装了这款工具。

```
&gt; jad burploader/Burploader.class
```

我摘抄了反编译后比较重要的java代码，如下所示：

[![](https://p5.ssl.qhimg.com/t01fad726f564df5fa6.png)](https://p5.ssl.qhimg.com/t01fad726f564df5fa6.png)

在这部分代码之前是经过base64编码的另一个jar文件，文件中包含keygen。经过编码的文件存放在`m`中。解码函数会处理base64编码，将其写入`Data.jar`文件。

此外，代码中还包含一些powershell命令，用来下载并执行powershell脚本，脚本的地址为`http://imonty.cn/wp-includes/pomo/script/dcss/js.js`（虽然扩展名为`.js`，但实际上是powershell脚本），同时上面这段代码也会运行keygen。

我们可以下载这个脚本，观察脚本内容，如下所示：

[![](https://p3.ssl.qhimg.com/t01a0eba6a02a5e485a.png)](https://p3.ssl.qhimg.com/t01a0eba6a02a5e485a.png)

这段代码会将两个新文件释放到新创建的`c:ProgramDataWindowsNT`目录中，释放出来的文件为：

1、[http://imonty.cn/wp-includes/pomo/script/dcss/co.js](http://imonty.cn/wp-includes/pomo/script/dcss/co.js)，保存为`WindowsNT.ini`；

2、[http://imonty.cn/wp-includes/pomo/script/dcss/co.vbs](http://imonty.cn/wp-includes/pomo/script/dcss/co.vbs)，保存为`WindowsNT.vbs`。

随后恶意代码会运行vb脚本（`co.vbs`），因此我们先来看看这个脚本，其内容如下所示：

[![](https://p2.ssl.qhimg.com/t019062c4d3793b280f.png)](https://p2.ssl.qhimg.com/t019062c4d3793b280f.png)

我们看到了经过混淆处理的vb代码。想要解开混淆，最简单的一种方法就是将代码中的执行语句替换成打印语句（这种方法可能无法适用于所有情况，但仍然是非常有用的一种技术）。显然，这段代码中负责执行去混淆后代码的语句为`EVAL(ExEcUTE(www))`。

> 这个文件的真正功能是分割一个非常长的字符串（每次碰到`*`符号就进行切割），然后计算分割后的数学表达式，将其转换成字符，将这些字符拼接起来后再去运行。

为了打印出字符串，我们需要将`EVAL(ExEcUTE(www))`替换为`wscript.echo www`，然后再次运行脚本。

[![](https://p0.ssl.qhimg.com/t015d377b014de4409b.png)](https://p0.ssl.qhimg.com/t015d377b014de4409b.png)

这段脚本的功能是使用powershell运行下载的另一个文件，即`co.js`（保存为`WindowsNT.ini`）。

因此让我们来看一下`co.js`。

这个文件比较大，因此我将该文件上传到了[GitHub](https://gist.githubusercontent.com/lkw657/f2dfae7f73267c8114de039a60efcb51/raw/e7b622c0385b48a3f727cb9b97fbf2b34966a5d5/co.ps1.gz.b64)上。

在上传之前，我使用gzip以及base64处理了一下这个文件，因此你可以运行`cat co.ps1.gzip.b64 | base64 -d | gunzip &gt; co.ps1`命令恢复原始代码。

此外，我将`co.js`重命名为`co.ps1`，方便大家在powershell中使用`./`方式运行。

[![](https://p1.ssl.qhimg.com/t0101ae697b21079cf4.png)](https://p1.ssl.qhimg.com/t0101ae697b21079cf4.png)

`iex`（全称为`invoke-expression`）函数可以用来执行powershell代码，因此我们需要使用`write-output`来替换该函数，打印出结果，再次运行该文件。

修改后的代码如下所示：[![](https://p0.ssl.qhimg.com/t01eb0bc53cdb28ea64.png)](https://p0.ssl.qhimg.com/t01eb0bc53cdb28ea64.png)

由于我在新的虚拟机环境中运行这段代码，因此我需要允许执行不受信任的powershell脚本。以管理员身份运行powershell：

[![](https://p4.ssl.qhimg.com/t018a69fcc9cde32aa1.png)](https://p4.ssl.qhimg.com/t018a69fcc9cde32aa1.png)

```
PS E:burpburploader&gt; ./co.ps1 &gt; co.2.ps1
```

我也将生成的文件上传到了[GitHub](https://gist.githubusercontent.com/lkw657/aa4cb19b3b7b5ccd55c846a59b3c07bf/raw/572ae9cff6747c45c2880f655139c4aebe0ff266/co.2.ps1.gz.b64)上。

生成的文件同样经过混淆处理。

该文件的开头部分如下所示：

[![](https://p1.ssl.qhimg.com/t010ba570b4d60625a2.png)](https://p1.ssl.qhimg.com/t010ba570b4d60625a2.png)

这一次代码没有使用`iex`，调用的是`Invoke-Expression`，我们同样可以使用`write-output`来替换该函数。

[![](https://p0.ssl.qhimg.com/t01049697341426d6e5.png)](https://p0.ssl.qhimg.com/t01049697341426d6e5.png)

再次运行这个文件。

```
PS E:burpburploader&gt; ./co.2.ps1 &gt; co.3.ps1
```

大家可以访问[此处](https://gist.githubusercontent.com/lkw657/bbbf4df3c2aa92f59cdd856643409d0f/raw/171f282ad627db264f279ca10644cda285acb284/co.3.ps1.gz.b64)获取生成的文件。

首先需要注意的是，新的文件包含三个部分，由空行分开。之前我犯了点错误，缺失了第一部分的文件，因此无法找到后面分析中所需的一些信息（感谢<a>@leeky</a>以及<a>@dtm</a>的细心提醒）。我没有尝试一次性解开整个文件（虽然之前我经常这么做），而是将其分成3个小文件，逐一处理这些文件。

### <a class="reference-link" name="%E7%AC%AC1%E9%83%A8%E5%88%86"></a>第1部分

该部分的**结尾**处如下所示：

[![](https://p2.ssl.qhimg.com/t01a9c1108e43b2fd44.png)](https://p2.ssl.qhimg.com/t01a9c1108e43b2fd44.png)

这一次我们并没有看到熟悉的`invoke-expression`，然而由于代码会在最后执行，因此调用操作很有可能出现在结尾处，要么在左侧，使用经过混淆的代码作为参数，要么在右侧，将代码重定向到标准输入中。

在这种情况下，由于左侧只包含一个括号，因此我们来分析一下管道右侧的语句，即`.( $PsHOmE[21]+$PShOMe[30]+'X')`（上图中圈起来的部分）。

非常有趣，我们可以看一下`$PsHOmE[21]+$PShOMe[30]+'X'`的执行结果。

```
PS E:burpburploader&gt; $PsHOmE[21]+$PShOMe[30]+'X'
ieX
```

因此，我们需要使用`write-output`来替换`.( $PsHOmE[21]+$PShOMe[30]+'X')`。

生成的结果也经过混淆处理，更加复杂。

[![](https://p2.ssl.qhimg.com/t01dd3afd4d2af0b538.png)](https://p2.ssl.qhimg.com/t01dd3afd4d2af0b538.png)

重复类似操作。看一下上述代码中开头部分`.( $eNv:PuBliC[13]+$eNv:pUBLiC[5]+'x')`的具体含义：

```
PS E:burpburploader&gt; $eNv:PuBliC[13]+$eNv:pUBLiC[5]+'x'
iex
```

还是使用`write-output`来替换这个语句：

[![](https://p5.ssl.qhimg.com/t01da07f36e864d8506.png)](https://p5.ssl.qhimg.com/t01da07f36e864d8506.png)

运行后我们会得到更加复杂的结果，我们需要重复类似操作，在新生成的文件尾部使用`write-output`替换`&amp; ($pShoME[21]+$pShoME[34]+'X')`，然后再替换开头处的`&amp;( $pShoME[21]+$pSHOMe[30]+'X')`语句。

### <a class="reference-link" name="%E7%AC%AC2%E9%83%A8%E5%88%86"></a>第2部分

第2部分的开头为`[String]::JoIN('',( [Char[]]( 127 ,105`。

**结尾**部分如下所示：

[![](https://p4.ssl.qhimg.com/t01a1426b0a31ad72f5.png)](https://p4.ssl.qhimg.com/t01a1426b0a31ad72f5.png)

在结尾处，使用`write-output`替换`.((gV '*mDR*').nAme[3,11,2]-joIn'')`语句，生成的结果仍然经过混淆处理。再次使用`write-output`替换结尾处的`.( $pShoME[4]+$PsHoMe[30]+'X')`，再次执行。

这样的操作仍然要重复多次，比如我们还需使用`write-output`替换开头附近的`&amp;( ([sTrINg]$verbosePREFerencE)[1,3]+'x'-JOIN'')`，然后再使用`write-output`替换`. ( $Env:comsPec[4,15,25]-JOiN'')`。

### <a class="reference-link" name="%E7%AC%AC3%E9%83%A8%E5%88%86"></a>第3部分

第3部分的开头处如下所示：

[![](https://p1.ssl.qhimg.com/t0131d29739956498c3.png)](https://p1.ssl.qhimg.com/t0131d29739956498c3.png)

使用`write-output`替换开头处的`.( $PsHome[4]+$PShoME[34]+'X')`，然后再次执行。

这部分代码可读性较强，如果我们替换函数名称则更加易读。

使用这种方法我们最多能达到这个程度。我们必须通过手动分析来找到函数名，然后再以手动方式或编写脚本找到并规范变量名。

大家可以从[这里](https://gist.githubusercontent.com/lkw657/becdb839139901fcc907fc39605a890d/raw/70e685f6ec0917aad7a6662132f967577bd72e3e/final1.ps1.b64)获取经过处理后的代码。

我对代码还做了些改动，去掉了乱七八糟的变量，修改了某些函数的名称，大家可从[这里](https://gist.githubusercontent.com/lkw657/4244014b5c091325feb3b40e0a3c786f/raw/3476aa131dcbb7fc244691dd5ed90a4af724b854/final2.ps1.b64)获得改动后的代码。

Virustotal并没有将这个[powershell脚本](https://www.virustotal.com/#/file/6f38fe65cad067a73888552cdb9817a37329863d8732b4e930938f619ca504fe/detection)当成病毒程序，如下所示：

[![](https://p4.ssl.qhimg.com/t01174705bb888c87aa.png)](https://p4.ssl.qhimg.com/t01174705bb888c87aa.png)

然而，某些[启发式检测引擎](https://www.virustotal.com/#/file/1bf764e77a543def4c623e6e207b1b72999f6550cf49651b88d53f80ae10e4d7/detection)能够正确识别释放器（dropper）：

[![](https://p1.ssl.qhimg.com/t0125c87a70d713a5d4.png)](https://p1.ssl.qhimg.com/t0125c87a70d713a5d4.png)

第1部分代码中只包含变量，然而变量名及值非常复杂。

[![](https://p4.ssl.qhimg.com/t01438384bb8e855825.png)](https://p4.ssl.qhimg.com/t01438384bb8e855825.png)

分析相关函数后，我们发现`$dragon_middle`变量包含RAT需要连接的一些域名（恶意软件会遍历这个列表，直到找到可以连接上的域名）。`$private`以及`$public`变量包含RAT 传输数据所需的加密及解密密钥。[此处](https://gist.githubusercontent.com/lkw657/61905786d99565ba8df087f208b4310a/raw/3c3250bd30e68e286d0a06f371719f49583a1b92/variables.txt)了解相关信息。

[域名](https://gist.githubusercontent.com/lkw657/db14c27dd42f83ad62ec64de6862249a/raw/3ff41837eeeeda4acf909f64910e4f5ae33a222a/domain)，该域名与其他所有域名相比会解析到一个不同的主机上。

[Github](https://gist.githubusercontent.com/lkw657/9d81fac2ca10126eceb5119eae92b30e/raw/6791d90b9c4929a9029c8070c04632696ce33d15/variables.txt)提供了更加完整的一份变量列表。我不太了解他如何生成这些结果，但根据结果的格式，我猜测他使用了一条命令来打印出相关信息（如果猜测不对请及时纠正我）。

虽然这份列表中并没有包含`$dragon_middle`中的所有元素，但包含了更为有趣一些变量，如用来查找受害者IP的变量（`https://api.ipify.org/`）以及受害者国别的变量（`http://apinotes.com/ipaddress/ip.php?ip=`）。

他还捕捉了恶意软件连接服务器过程中生成的一些[数据包](https://gist.githubusercontent.com/lkw657/e9c13ddb9cf3955384f3b39f22f97d6d/raw/ae674ac8401597c759e15ee7f79ea78ee520557d/packets.pcap.b64)。

第2部分包含加密及解密代码，第3部分为剩下的所有代码。

RAT使用RSA加密算法来与服务器通信。奇怪的是，我认为代码中公钥以及私钥的命名方式被作者弄错了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ef6d1821d73153d5.png)

代码所使用的公钥以及私钥具有不同的模式，这表明它们很有可能来自于不同的密钥对。

发往服务器的消息经使用服务器公钥（代码中的`$secret`变量）进行加密，然后使用服务器的私钥进行解密（私钥存储在服务器上）。

发往RAT的消息使用RAT的公钥（存放在服务器上）进行加密，然后使用RAT的私钥（代码中的`$public`变量）进行解密。

从理论上讲，如果加解密过程没有破绽，那么我们无法解开发往服务器的消息（当然我们可以修改RAT，打印出这些消息）。然而，攻击者的密钥使用了小素数，因此存在弱点。

当RAT启动时，做的第一件事就是完成本地持久化。

[![](https://p3.ssl.qhimg.com/t016520fe4b294e7fae.png)](https://p3.ssl.qhimg.com/t016520fe4b294e7fae.png)

RAT将vbs文件的路径添加到注册表中的`HKCU:SOFTWAREMicrosoftWindowsCurrentVersionRunDifenderUpdate`，然后使用计划任务，在登录时运行该脚本。

我不大确定本地持久化函数中第一部分代码的功能。我觉得这段代码的功能是禁用Word的受保护视图功能，但我不确定为什么恶意软件需要这个功能。

接下来RAT检查正在运行的进程，查看是否存在某些调试器或者其他工具。如果找到这类工具，则会关闭主机。

[![](https://p0.ssl.qhimg.com/t018b900666c7e517d9.png)](https://p0.ssl.qhimg.com/t018b900666c7e517d9.png)

接下来，RAT尝试连接到`$dragon_middle`中保存的服务器，一旦出现错误，则会重复该过程（大概是因为RAT认为这些服务器可能会停止服务或者被列入黑名单中）。

RAT在接受并处理服务器的命令之前，会先尝试与向服务器进行注册。

[![](https://p2.ssl.qhimg.com/t01bc66c4fd2cd965db.png)](https://p2.ssl.qhimg.com/t01bc66c4fd2cd965db.png)

[![](https://p1.ssl.qhimg.com/t01af429368ed929592.png)](https://p1.ssl.qhimg.com/t01af429368ed929592.png)

[![](https://p4.ssl.qhimg.com/t011fb558efc407b0a4.png)](https://p4.ssl.qhimg.com/t011fb558efc407b0a4.png)

RAT接受如下几类命令：

1、reboot：重启主机。

2、shutdown：关闭主机。

3、clean：在重启前尽可能清掉C:、D:、E:以及F:的数据。

4、screenshot：截屏并将结果发往服务器。

5、upload：把服务器上的某个文件传输到受害者主机中。

如果收到的命令不属于如上几类，则会尝试在powershell中执行。

我使用默认的执行策略来运行这个keygen（记得前面我们已经改过运行策略），检查`c:ProgramDataWindowsNT`目录，观察RAT能否正常运行。我发现该目录没有创建成功，因此Windows可能会阻止RAT的运行。

## 三、补充说明

前面我提到过，RAT使用的加密算法比较脆弱，这里我想补充下我们如何破解这个算法。

我不想在这里介绍RSA的基本工作原理，0x00sec上有相关[教程](https://0x00sec.org/t/encryption-101-rsa-001-the-maths-behind-it/1921)，并且[维基百科](https://en.wikipedia.org/wiki/RSA_(cryptosystem))上也有许多有价值的参考资料。

RSA算法中用到了两个素数：`p`以及`q`，用来计算`n = p*q`，这两个素数比较关键，需要妥善保管。这两个素数也用来计算`λ(n) = λ(p*q) = lcm(p-1, q-1)`。RSA中公钥`e`以及私钥`e`满足一定关系：`d == e^(-1) (mod λ(n))`。

对于这个RAT，用到的`n`非常小（因为使用的是小素数），因此我们很容易就可以将其分解为正确的`p`以及`q`。接下来我们可以使用这两个数来计算`λ(n)`，然后用前面的公式，根据`e`来计算`d`。

我们可以使用SageMath来计算，代码如下：

```
# from $private variable in rat
e = 959
n = 713

# factor n
# list(factor(n)) returns prime factors as a list of tuples of (factor, amount)
# we just want the factors
p, q = [a[0] for a in list(factor(n))]

# calculate λ(n) 
l = lcm(p-1, q-1)

# calculate d
print('d = `{``}`'.format(inverse_mod(e, l)))
```

算出`d = 149`。

利用服务器的私钥，我们可以写段脚本来解密发往服务器的消息。如果我们将这个过程应用到RAT的公钥上，那么我们可以作为中间人角色，通过MiTM方式攻击RAT与服务器之间的通信流量。

使用python语言编写的解密脚本如下所示：

```
def decrypt(ciphertext):
    key = 149
    n = 713
    decrypted = []
    for i in range(0, len(ciphertext)):
        num = int(ciphertext[i])
        t = pow(num, key, n)
        decrypted.append(chr(t))
    return ''.join(decrypted)

nums = input().split()
print(decrypt([int(i) for i in nums]))
```

在<a>@dtm</a>截获的pcap包中，RAT将如下数据发往服务器：

```
340 362 396 383 105 598 219 362 581 362 518 73 35 73 504 220 515 665 504 515 515 35 515 518 133 335 316 665 515 665 220 665 316 181 665 335 515 38 335 335 335 316 362 663 362 145 180 396 637 383 219 362 581 362 180 383 432 432 145 219 367 362 590
```

利用上述脚本，我们可以解密出原始的消息，如下所示：

```
`{`"TOKEN":"70e0a413a11e17db9313439c3b1fbbb9","ACTION":"COMMAND"`}`
```

[原文链接：https://www.0x00sec.org/t/malware-reversing-burpsuite-keygen/5167](https://www.0x00sec.org/t/malware-reversing-burpsuite-keygen/5167)

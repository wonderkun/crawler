> 原文链接: https://www.anquanke.com//post/id/86540 


# 【技术分享】如何解密TFS的秘密变量


                                阅读量   
                                **79208**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：lowleveldesign.org
                                <br>原文地址：[https://lowleveldesign.org/2017/07/04/decrypting-tfs-secret-variables/](https://lowleveldesign.org/2017/07/04/decrypting-tfs-secret-variables/)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p0.ssl.qhimg.com/t015bb548c944192eec.png)](https://p0.ssl.qhimg.com/t015bb548c944192eec.png)

****

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**什么是 TFS（Team Foundation Server<strong style="text-indent: 32px">）**？</strong>

****

**Team Foundation Server** 提供一组协作软件开发工具，它与你现有的 IDE 或编辑器集成，从而使你的跨功能团队可以在所有大小的软件项目上高效工作。

引用自[https://www.visualstudio.com/zh-hans/tfs/](https://www.visualstudio.com/zh-hans/tfs/)



**一、前言**<br>

****

TFS的每个生成（build）及发布（release）定义中都包含一组自定义变量，并且会在随后的build/release管道中使用这些变量作为参数用于PowerShell/批处理脚本、配置文件转换或者其他子任务。从一个任务中访问这些变量类似于访问进程环境变量。由于TFS使用了非常详细的日志记录，因此我们经常可以在build日志中发现明文形式的具体变量值。这也是微软使用秘密变量的原因之一。

TFS的生成配置面板示例如下所示，其中有个秘密变量amiprotected（注意图中高亮的小锁图标）：

 [![](https://p0.ssl.qhimg.com/t018b9f699cabea1516.png)](https://p0.ssl.qhimg.com/t018b9f699cabea1516.png)

当秘密变量被保存之后，我们再也无法通过网页面板读取这个值（当你点击小锁图标时，文本框会被清空）。

当我们将秘密变量传递给PowerShell脚本并打印这个变量时，对应的输出日志如下所示：

 [![](https://p0.ssl.qhimg.com/t01777bcf07164b6c6b.png)](https://p0.ssl.qhimg.com/t01777bcf07164b6c6b.png)

现在让我们来探索一下这些秘密变量具体存储的位置及过程。

<br>

**二、秘密变量存储的过程**

****

为了分析TFS存储秘密变量的具体过程，我一开始检查的是TFS的数据库服务器。不同的团队集合都有独立的数据库与之对应。每个数据库会将表（table）分组为名字易于理解的schema，比如Build、Release或者TfsWorkItemTracking。此外，默认的dbo schema中也包含一些表。我们的秘密变量属于生成定义的一部分，因此我们可以来检查一下Build这个schema。tbl_Definition看上去像是个可行的方法。这个表的前几列如下所示：

 [![](https://p3.ssl.qhimg.com/t0144fa40c4f83496bd.png)](https://p3.ssl.qhimg.com/t0144fa40c4f83496bd.png)

其中，Variables这一列以JSON格式列出了所有的变量。不幸的是，我无法了解关于我们的秘密变量的更多信息（除了得知它是个秘密变量之外）。因此，我开始搜索是否存在名字为“tbl_Variables”或者“tbl_Secrets”的表，但一无所获。抱着最后一丝希望，我使用了[procmon](https://technet.microsoft.com/en-us/sysinternals/processmonitor)这个工具，这个工具也是我在实在没办法的时候一直使用的一个工具。利用这个工具，我跟踪了秘密变量保存时的路径，在这个路径中发现了一些有趣的信息：

 [![](https://p0.ssl.qhimg.com/t018c40c48df283f24b.png)](https://p0.ssl.qhimg.com/t018c40c48df283f24b.png)

我选择其中一条记录，检查它的调用栈：

 [![](https://p2.ssl.qhimg.com/t01b2618ef3b3b27f84.png)](https://p2.ssl.qhimg.com/t01b2618ef3b3b27f84.png)

现在我需要使用一个小[技巧](https://lowleveldesign.org/2017/06/23/how-to-decode-managed-stack-frames-in-procmon-traces/)，来解码procmon跟踪路径中的frame信息。最后一个frame指向的是TeamFoundationStrongBoxService.AddStream方法。这个类的名称非常特别，因此我特意在数据库中查找了一下相关信息，很快就找到了一些较为有趣的表。

tbl_StrongBoxDrawer表：

 [![](https://p1.ssl.qhimg.com/t01aeb4c923d0830472.png)](https://p1.ssl.qhimg.com/t01aeb4c923d0830472.png)

tbl_StrongBoxItem表：

 [![](https://p2.ssl.qhimg.com/t01fac80d118387b100.png)](https://p2.ssl.qhimg.com/t01fac80d118387b100.png)

以及tbl_SigningKey表：

 [![](https://p3.ssl.qhimg.com/t0117f28b0cce507592.png)](https://p3.ssl.qhimg.com/t0117f28b0cce507592.png)

正如你所看到的那样，tbl_StrongBoxDrawer表中的某一行引用了build的定义，同时对秘密变量进行了分组。tbl_StrongBoxItem表以加密形式存储了秘密变量所对应的所有值（包括我们当前的秘密变量）。最后，tbl_SigningKey表存储了某些私钥，这些私钥可能会在加密过程中使用。

现在是启动[dnspy](https://github.com/0xd4d/dnSpy)工具、开始更为细致分析的时候了。AddStream方法包含将敏感信息添加到TFS数据库的逻辑处理流程。首先，秘密变量值经过AES加密（使用了自动生成的密钥以及随机初始化的向量）并保存在一个byte数组中。其次，AES密钥经过签名密钥的加密，并被保存到另一个byte数组中。最后，这两个表以及初始化向量会被保存为与秘密向量有关的加密值。对于本文使用的例子来说，这个加密值如下所示：

 [![](https://p4.ssl.qhimg.com/t01cfbcca547d61ba4a.png)](https://p4.ssl.qhimg.com/t01cfbcca547d61ba4a.png)

而签名密钥会以RSA CSP数据块的形式保存，如下所示：

 [![](https://p2.ssl.qhimg.com/t0181359cd56160bb17.png)](https://p2.ssl.qhimg.com/t0181359cd56160bb17.png)

当你从数据库中提取这段数据后，你可以使用如下示例代码进一步解压这段数据：

```
byte[] aesKey;
 
using (RSACryptoServiceProvider rsaCryptoServiceProvider = new RSACryptoServiceProvider(2048,
    new CspParameters `{` Flags = CspProviderFlags.UseMachineKeyStore `}`)) `{`
    var cspBlob = "...hex string...";
    rsaCryptoServiceProvider.ImportCspBlob(Hex.FromHexString(cspBlob));
 
    var encryptedAesKey = "...hex string...";
    aesKey = rsaCryptoServiceProvider.Decrypt(Hex.FromHexString(encryptedAesKey), true);
`}`
 
var iv = Hex.FromHexString("...hex string...");
var cipher = Hex.FromHexString("...hex string...");
 
using (var aes = Aes.Create()) `{`
    var transform = aes.CreateDecryptor(aesKey, iv);
    using (var encryptedStream = new MemoryStream(cipher)) `{`
        using (var cryptoStream = new CryptoStream(encryptedStream, transform, CryptoStreamMode.Read)) `{`
            using (var decryptedStream = new MemoryStream()) `{`
                cryptoStream.CopyTo(decryptedStream);
 
                Console.WriteLine(Hex.PrettyPrint(decryptedStream.ToArray()));
            `}`
        `}`
    `}`
`}`
```

如上所述，tbl_SigningKey表包含非常敏感的数据，因此你必须确保只有经过认证的用户才能访问这个表。TFS在这里竟然没有使用任何DPAPI或者其他加密机制，这让我非常惊讶。

<br>

**三、揭开秘密变量的神秘面纱**

****

前文中，我们利用存在数据库中相关数据成功解密了秘密变量，但实际上还有更为简单的方法。如果你可以修改build/release任务管道，那么你就可以很方便地创建一个PowerShell任务，如下所示：

 [![](https://p1.ssl.qhimg.com/t012e9b5fecc6cb7da6.png)](https://p1.ssl.qhimg.com/t012e9b5fecc6cb7da6.png)

由于字符串中第一个字符与剩余字符之间有一个空格，因此输出不会被屏蔽，你可以以在日志中看到明文形式的密码：

 [![](https://p4.ssl.qhimg.com/t01a8ff2566bcd16a5e.png)](https://p4.ssl.qhimg.com/t01a8ff2566bcd16a5e.png)

因此，你可以得出结论，如果人们能够修改build/release任务管道，或者人们可以修改任务管道中使用的脚本内容，那么他们就能读取秘密变量的值。

<br>

**四、从TFS内存中提取秘密变量**

****

最后，让我们研究一下TFS服务器进程（w3wp.exe）的内存，看看我们能从中获得什么信息。我将这个进程的全部内存导出到一个文件中，然后使用WinDbg打开这个文件（WinDbg已事先加载了SOSEX以及SOS扩展）。先来列出StrongBoxItemInfo的所有实例信息：

```
0:000&gt; !mx *.StrongBoxItemInfo
AppDomain 0000000001eb8b50 (/LM/W3SVC/2/ROOT/tfs-1-131555514123625000)
---------------------------------------------------------
module: Microsoft.TeamFoundation.Framework.Server
  class: Microsoft.TeamFoundation.Framework.Server.StrongBoxItemInfo
module: Microsoft.TeamFoundation.Client
  class: Microsoft.TeamFoundation.Framework.Client.StrongBoxItemInfo
…
 
0:000&gt;  .foreach (addr `{`!DumpHeap -short -mt 000007fe92560f80`}`) `{` !mdt addr `}`
...
0000000203419dc8 (Microsoft.TeamFoundation.Framework.Server.StrongBoxItemInfo)
    &lt;drawerid&gt;k__BackingField:(System.Guid) `{`c2808c4d-0c0d-43e5-b4b2-e743f5121cdd`}` VALTYPE (MT=000007feef467350, ADDR=0000000203419df8)
    &lt;itemkind&gt;k__BackingField:0x00 (String) (Microsoft.TeamFoundation.Framework.Server.StrongBoxItemKind)
    &lt;lookupkey&gt;k__BackingField:000000020341a1f8 (System.String) Length=24, String="9/variables/amiprotected"
    &lt;signingkeyid&gt;k__BackingField:(System.Guid) `{`c2808c4d-0c0d-43e5-b4b2-e743f5121cdd`}` VALTYPE (MT=000007feef467350, ADDR=0000000203419e08)
    &lt;expirationdate&gt;k__BackingField:(System.Nullable`1[[System.DateTime, mscorlib]]) VALTYPE (MT=000007feef4c13b8, ADDR=0000000203419e18)
    &lt;credentialname&gt;k__BackingField:NULL (System.String)
    &lt;encryptedcontent&gt;k__BackingField:000000020341a3f0 (System.Byte[], Elements: 312)
    &lt;value&gt;k__BackingField:NULL (System.String)
    &lt;fileid&gt;k__BackingField:0xffffffff (System.Int32)
…
```

LookupKey这个字段包含变量的名称。为了将其与build/release定义结合起来，我们需要找到Id等于c2808c4d-0c0d-43e5-b4b2-e743f5121cdd的StrongBoxDrawerName实例。但我们的主要任务是解密EncryptedContent字段的值，为了完成这个任务，我们需要得到签名密钥（id: c2808c4d-0c0d-43e5-b4b2-e743f5121cdd）。TFS会在缓存中保存最近使用的签名密钥，因此如果我们运气不错的话，我们还是有可能在缓存中找到这个签名密钥。这个过程稍显漫长，首先，我们需要列出TeamFoundationSigningService+SigningServiceCache类的所有实例：

```
0:000&gt; !mx *.TeamFoundationSigningService+SigningServiceCache
module: Microsoft.TeamFoundation.Framework.Server
  class: Microsoft.TeamFoundation.Framework.Server.TeamFoundationSigningService+SigningServiceCache
 
0:000&gt; !DumpHeap -mt 000007fe932d99e0
         Address               MT     Size
...
0000000203645ce0 000007fe932d99e0       96
```

然后，一路跟踪对象树，找到与我们有关的那个私钥：

```
Microsoft.TeamFoundation.Framework.Server.TeamFoundationSigningService+SigningServiceCache
|-m_cacheData (00000002036460a0)
|-m_cache (0000000203646368)
|-m_dictionary (0000000203646398)
 
0:000&gt; !mdt 0000000203646398 -e:2 -start:0 -count:2
…
[1] (…) VALTYPE (MT=000007fe969d7160, ADDR=0000000100d6d510)
key:(System.Guid) `{`c2808c4d-0c0d-43e5-b4b2-e743f5121cdd`}` VALTYPE (MT=000007feefdc7350, ADDR=0000000100d6d520)
 value:000000020390d440 
 
|-Value (000000020390d410)
|-&lt;Value&gt;k__BackingField (000000020390d3f0)
|-m_Item1 (000000020390d2b0)
 
0:000&gt; !mdt 000000020390d2b0
000000020390d2b0 (Microsoft.TeamFoundation.Framework.Server.SigningServiceKey)
    &lt;keydata&gt;k__BackingField:000000020390ce00 (System.Byte[], Elements: 1172)
    &lt;keytype&gt;k__BackingField:0x0 (RSAStored) (Microsoft.TeamFoundation.Framework.Server.SigningKeyType)
```

其实一开始我们可以直接搜索SigningServiceKey类的实例。但如果这么做，我们需要打印出所有的GC根，逐一检查，核实其Id是否就是我们正在查找的那个Id。我发现这种自上而下的方法会更为容易一些（但这个方法还是稍显乏味）。

<br>

**五、总结**

****

希望这篇文章能对读者有所帮助。根据本文分析，我们认为还是有办法能够安全地保存TFS秘密变量中的敏感数据，但首先要做到以下几点：

1、只有授权用户可以修改build/release管道（包括使用秘密变量的任务的内容）。

2、只有授权用户可以访问TFS数据库中的tbl_SigningKey表。

此外，我们也可以使用精心配置的TFS代理，配合密钥库或者某些本地DPAPI加密块来执行所有的敏感任务。

> 原文链接: https://www.anquanke.com//post/id/107249 


# Spartacus勒索软件：一个充满教育意义的勒索软件


                                阅读量   
                                **80717**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：https://blog.malwarebytes.com/
                                <br>原文地址：[https://blog.malwarebytes.com/threat-analysis/2018/04/spartacus-introduction-unsophisticated-ransomware/](https://blog.malwarebytes.com/threat-analysis/2018/04/spartacus-introduction-unsophisticated-ransomware/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t0188ab7318c21744c5.jpg)](https://p0.ssl.qhimg.com/t0188ab7318c21744c5.jpg)



## 写在前面的话

最近我们发现一款名为Spartacus勒索新病毒。软件主要用C＃编写，可是原始样本是被混淆的，所以只有我们将其提取到可读状态时才可以继续分析。

可以讲Spartacus是一个相对简单的勒索软件，它使用了一些类似ShiOne, Blackheart和Satyr的技术和代码，这我们在过去曾研究过的。然而，这些样本和参与者之间并没有确定的关系。我提到它仅仅是为了表明它们有相似的功能。不要多想。

在分析在Satyr和Blackheart的时候，我们发现他俩代码几乎完全相同，Spartacus也只是做了一些修改。如果非我要做一个假设的话，我会说他们要么是出于一人之手，要么他们使用相同的代码。但是，现在还没有证据证明这一点。

一般来说，我们注意到一有NET勒索软件出现了，它们都差不多是一样的或者相似的。这仅仅是罪犯创造的一种简单的赎金形式，因为它不需要花费太多的时间或脑力。

Spartacus没有什么特别之处。那么我们为什么要写关于Spartacus的分析，我想最主要原因那应该是可以用来作为分析基本的.NET勒索软件的基础知识吧！

本文将详细了解代码，并了解如何将混淆的.NET示例转化为可读状态。



## Spartacus

在开始之前，我想提一下Spartacus加密方法的一个特点。Spartacus首先生成了一个独特的密钥，用于对[Rijndael](https://blog.finjan.com/rijndael-encryption-algorithm/)算法进行加密。(Rijndael算法是AES的一个版本。)<br>
该密钥被保存并用于加密每个文件，这意味着两个相同的文件将具有相同的密码文本。AES密钥使用嵌入在文件中的RSA密钥进行加密。密码文本被编码并显示给用户在勒索信中。

[![](https://p2.ssl.qhimg.com/t01ad5c2033a0f58138.png)](https://p2.ssl.qhimg.com/t01ad5c2033a0f58138.png)

RSA密钥被静态地嵌入到勒索软件中，这意味着私钥存在于勒索软件作者系统的服务器端。因此，如果所有AES密钥被泄漏，则可以使用此密钥解密所有受害者的所有AES密钥。由于这个勒索软件并不十分复杂，我们将直接进行深入的技术分析和代码演练。

### <a class="reference-link" name="%E6%8B%86%E5%8C%85"></a>拆包

当我们首次打开ILSpy的Spartacus样品时,我们看到这样的结果：

[![](https://p4.ssl.qhimg.com/t0180487e01617903de.png)](https://p4.ssl.qhimg.com/t0180487e01617903de.png)

这些函数的代码是不可见的，正如你所看到的，所有的东西都是混淆的。一般在这种情况下，我喜欢使用de4dot工具。它将处理文件并输出可读版本。-r标志是您设置目录的位置，其中包含混淆的.NET示例。

[![](https://p5.ssl.qhimg.com/t01f92f00ba3bc84e26.png)](https://p5.ssl.qhimg.com/t01f92f00ba3bc84e26.png)

这给了我们清晰的版本，我们将在接下来的分析中使用它。

[![](https://p5.ssl.qhimg.com/t01151fc9af804a7843.png)](https://p5.ssl.qhimg.com/t01151fc9af804a7843.png)

### <a class="reference-link" name="%E5%88%86%E6%9E%90"></a>分析

让我们从下面显示的Main函数开始。

[![](https://p2.ssl.qhimg.com/t015372a35b2d1efed3.png)](https://p2.ssl.qhimg.com/t015372a35b2d1efed3.png)

它首先要确保系统上只运行该恶意软件的一个实例。这是通过CheckRunProgram函数来实现，除此之外，它还创建一个互斥锁并确保它是唯一的。

[![](https://p5.ssl.qhimg.com/t0135c660f92135f974.png)](https://p5.ssl.qhimg.com/t0135c660f92135f974.png)

检查完成后，它会在一个线程中执行 smethod_3。在调用smethod_3开始之前，这个类的构造函数会自动调用，并设置所有私有成员（变量），其中包含要搜索和加密的所有特殊文件夹。它还使用KeyGenerator.GetUniqueKey（133）函数生成对受害者来说唯一的AES密钥。并在勒索软件中被引用以开始文件夹遍历。特殊文件夹可以在下面查看

[![](https://p5.ssl.qhimg.com/t017239831286ad1018.png)](https://p5.ssl.qhimg.com/t017239831286ad1018.png)

我提到的keygen函数是GetUniqueKey（），本质上，它只是使用RNGCryptoServiceProvider.GetNonZeroBytes API函数创建一系列加密的强随机数。然后它使用该系列的随机数作为字符集<br>
array =“abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890”的 索引来构建一个唯一的字符串。这是AES密钥，它将加密所有运行的文件。

[![](https://p2.ssl.qhimg.com/t016bb84fd6fe7048cc.png)](https://p2.ssl.qhimg.com/t016bb84fd6fe7048cc.png)

现在该类的构造函数已经启动了，让我们来看看被调用的smethod_3 函数。

[![](https://p3.ssl.qhimg.com/t01cb2a7ae93b1d28ef.png)](https://p3.ssl.qhimg.com/t01cb2a7ae93b1d28ef.png)

该功能对在构造函数中生成的特殊文件夹列表进行迭代，并开始使用smethod_6函数对文件夹中的每个文件进行递归遍历加密。这里要注意的一点是，加密循环不会区分文件类型或特殊文件。也就是说它会加密所有的东西。此外，还可以看到这里调用了smethod_1函数。但这可能是程序员的一个错误，因为它在程序的任何地方都没有使用。正如我前面提到的，smethod_6函数是执行加密的函数，smethod_5函数是一个递归函数，它将深入到任何位置的每个子文件夹中，然后在每个迭代中调用smethod_6来加密该子文件夹中的文件。

[![](https://p3.ssl.qhimg.com/t017a1601c00224395c.png)](https://p3.ssl.qhimg.com/t017a1601c00224395c.png)<br>
正如您所看到的，它会自行调用，以便最终覆盖每个子文件夹。然后它调用smethod_6来执行加密，循环遍历该文件夹中的每个文件。

[![](https://p1.ssl.qhimg.com/t01eb7eb61419b36569.png)](https://p1.ssl.qhimg.com/t01eb7eb61419b36569.png)

此方法迭代当前文件夹中的所有文件。唯一的判断是否该文件加密。它只是确保扩展它确保扩展是不是.Spartacus:

<code>if (Path.GetExtension(text) == ".Spartacus")<br>
`{`<br>
return;<br>
`}`</code>

如果这个检查通过，它调用smethod_7对加密的版本执行文件内容重写。

[![](https://p5.ssl.qhimg.com/t019ee8a4699158475f.png)](https://p5.ssl.qhimg.com/t019ee8a4699158475f.png)

该函数调用smethod_0，它对原始文件数据进行加密，然后接下来的两行代码将加密的数据写入文件中，并使用.Spartacus扩展名对其进行重命名。提示：每个文件都使用相同的密钥加密，这个勒索软件不会将加密的AES密钥写入文件中，我们在其他的勒索软件中看到，它们执行唯一的文件加密。

[![](https://p4.ssl.qhimg.com/t01bd1473e27461abe2.png)](https://p4.ssl.qhimg.com/t01bd1473e27461abe2.png)

正如你在这里看到的，它使用Rijndael方法—使用ECB模式的AES。在构造函数中生成的密钥是用MD5散列的，而这实际上是用作密钥本身的密钥。现在我们已经完成了在主文件系统上进行文件加密的整个过程，通过在父函数smethod_3中调用的所有子函数。现在让我们回到主函数到下一行，它调用smethod_4（）：

[![](https://p4.ssl.qhimg.com/t015372a35b2d1efed3.png)](https://p4.ssl.qhimg.com/t015372a35b2d1efed3.png)

smethod_4基本上执行与smethod_3中所看到的完全相同的一组递归函数调用，但是，它不是循环访问特殊文件夹，而是遍历所有连接到系统的逻辑驱动器。因此，所有外部或映射的驱动器也将被加密。

[![](https://p3.ssl.qhimg.com/t0169c2dd9b2a5a2e41.png)](https://p3.ssl.qhimg.com/t0169c2dd9b2a5a2e41.png)

我们现在不需要遍历所有这些细节，因为我们已经讨论了它们的功能，因为它们与前面的函数调用是相同的。我唯一要提到的是smethod_6被调用两次。这样做很可能通过在两个线程上运行来加速加密。

回到main：下一个也是最后一个重要的函数调用是：<br>`Application.Run（new Form1（））;`<br>
这将向用户显示赎金记录并在赎金记录中显示加密的AES密钥。

[![](https://p5.ssl.qhimg.com/t01c1fb8f5d1650915c.png)](https://p5.ssl.qhimg.com/t01c1fb8f5d1650915c.png)

它首先调用smethod_1()。正如我上面提到的，这只是简单地使用AES键，它是在开始时生成的，并使用硬编码的公共RSA密钥对其进行加密。

<code>public static string smethod_1()<br>
`{`<br>
return Convert.ToBase64String(Class1.smethod_2("&lt;RSAKeyValue&gt;&lt;Modulus&gt;xA4fTMirLDPi4rnQUX1GNvHC41PZUR/fDIbHnNBtpY0w2Qc4H2HPaBsKepU33RPXN5EnwGqQ5lhFaNnLGnwYjo7w6OCkU+q0dRev14ndx44k1QACTEz4JmP9VGSia6SwHPbD2TdGJsqSulPkK7YHPGlvLKk4IYF59fUfhSPiWleURYiD50Ll2YxkGxwqEYVSrkrr7DMnNRId502NbxrLWlAVk/XE2KLvi0g9B1q2Uu/PVrUgcxX+4wu9815Ia8dSgYBmftxky427OUoeCC4jFQWjEJlUNE8rvQZO5kllCvPDREvHd42nXIBlULvZ8aiv4b7NabWH1zcd2buYHHyGLQ==&lt;/Modulus&gt;&lt;Exponent&gt;AQAB&lt;/Exponent&gt;&lt;/RSAKeyValue&gt;", Encoding.UTF8.GetBytes(Class2.smethod_0())));<br>
`}`</code>

RSA密钥被硬编码并嵌入到勒索软件中，这意味着作者已经预先生成了私钥。然后迭代所有驱动器并在那里写入赎金记录。最后，它打开了勒索信，显示了信息和加密的AES密钥，这将被受害者用于解密。<br>
在完成所有这些之后，它所做的最后一件事就是调用smethod_0，删除阴影卷以防止用户用作Windows还原点。

[![](https://p0.ssl.qhimg.com/t01a3f7353cdf6fe7ff.png)](https://p0.ssl.qhimg.com/t01a3f7353cdf6fe7ff.png)



## 最后

这个勒索软件是完全离线的因为没有任何网络通信可以追溯到作者或任何C2服务器。勒索软件的作者不知道他感染了谁，直到他们用他们的个人ID给他发电子邮件，这是AES键。这也意味着，作者将发送的解密工具很可能嵌入了AES键，当然，它将是受害者才有的。这个样本没有特别的或创新的，但这并不意味着它不是危险的。它还会在没有解密的情况下继续工作。如果你意识到自己正在遭受这种恶意软件攻击，唯一可能的办法就是执行进程内存转储，在这种情况下，从内存中提取密钥的可能性很小。一般来说，在杀死进程之前，尽可能在系统上执行任何恶意软件的内存转储是一个好方法，因为有些密钥可能会被恢复。

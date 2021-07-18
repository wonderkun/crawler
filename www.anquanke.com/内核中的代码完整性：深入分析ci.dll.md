
# 内核中的代码完整性：深入分析ci.dll


                                阅读量   
                                **538218**
                            
                        |
                        
                                                                                                                                    ![](./img/200478/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者cybereason，文章来源：cybereason.com
                                <br>原文地址：[https://www.cybereason.com/blog/code-integrity-in-the-kernel-a-look-into-cidll](https://www.cybereason.com/blog/code-integrity-in-the-kernel-a-look-into-cidll)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/200478/t012899f29e393ae9ff.jpg)](./img/200478/t012899f29e393ae9ff.jpg)



## 前言

在某些场景中，如果我们希望在允许某个进程进行特定动作前，以一种可靠的方式确认该进程是否可信，那么验证该进程的Authenticode签名是一个不错的方式。用户模式下的DLL wintrust提供了专门用于此目的的API。<br>
但是，如果我们需要在内核模式下以一种可靠的方式来进行身份验证，这时应该如何进行呢？在以下的情况中，我们可能会遇到这样的场景：<br>
1、应用程序用户模式部分不可用，可能是由于正处于开发过程的早期阶段，也可能是由于运行失败或配置出现问题。<br>
2、我们希望获得对进程操作的内联访问权限，以便在进程未验证的情况下阻止它们。<br>
3、最典型的一种情况是Windows内核在加载驱动程序时对驱动程序进行验证，显然这一过程必须要在内核模式下完成。<br>
尽管在不少论坛上，都有人多次提问应该如何操作，但我们还没有在公开的地方找到解决该问题的任何实现。<br>
其中一些方案建议我们自行实现，一些方案则建议将OpenSSL源导入到我们的项目中。而另外一种方案则将这个任务委托给用户模式下的代码。但是，上述所有替代方案都有明显的缺点：<br>
1、在解析复杂的ASN1结构时容易出现错误；<br>
2、不适合将大量源代码导入驱动程序，因为OpenSSL中的每一个漏洞修复都会导致重新导入该代码。<br>
3、进入用户模式可能无效，并且用户模式并非始终都可用。<br>
实际上，Microsoft内核模式库ci.dll中，就包含对文件进行身份验证的功能。<br>
j00ru的研究表明，ntoskrnl通过CiInitialize()函数初始化CI模块，该函数以回调列表填充函数指针结构。如果我们可以使用这些函数或者其他CI导出来验证正在运行的进程或文件的完整性和真实性，这将会成为内核驱动程序的一个最佳方案。<br>
除了ntoskernel.exe之外，我们还发现了两个驱动程序，它们都链接到ci.dll，并使用其导出文件：

[![](./img/200478/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014387952bb235b457.png)

链接到ci.dll的驱动程序

[![](./img/200478/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0183c159e5974b5794.png)

链接到ci.dll的驱动程序<br>
驱动程序可以链接到这个模块，并且调用一些关键的函数，例如CiValidateFileObject()。从函数名称就可以看出，这样的方式完全可以满足我们的需求。<br>
在本文中，我们将通过一个代码示例来详细分析CI，可以以此作为进一步研究的基础。



## 背景信息

我们建议各位读者在详细分析ci.dll之前，首先熟悉以下相关主题：<br>
1、PE安全目录：PE中包含Authenticode签名的部分；<br>
2、WIN_CERTIFICATE结构：Authenticode签名之前的标头；<br>
3、PKCS 7 SignedData结构：Authenticode的基础结构；<br>
4、X.509证书结构；<br>
5、证书时间戳：通过过期或吊销证书来延长签名使用周期的方法。



## 研究过程

在Windows 10上，CI会导出以下函数：

[![](./img/200478/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01b12e62a0ac99a1fb.png)

CI导出功能<br>
如前所述，调用CiInitialize()将会返回一个名为g_CiCallbacks的结构，其中包含更多函数（详情请参考[1][2][5]）。而其中的一个函数，CiValidateImageHeader()，将会被ntoskernel.exe用于加载驱动程序以验证签名的过程：

[![](./img/200478/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c274f0e4777f1f83.png)

调用堆栈以在加载过程中验证驱动程序签名<br>
在我们的研究中，利用了导出的函数CiCheckSignedFile()以及与之交互的数据结构。稍后我们将看到，这些数据结构也出现在其他CI函数中，我们也可以将研究范围扩展到这些其他的函数。

### <a class="reference-link" name="CiCheckSignedFile()"></a>CiCheckSignedFile()

CiCheckSignedFile()可以接收8个参数，但目前我们还不清楚这些参数的名称是什么。但是，通过检查内部函数，我们可以推断出其参数。例如，我们可以检查MinCryptGetHashAlgorithmFromWinCertificate()：

[![](./img/200478/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d18c250736da98e2.png)

检查WIN_CERTIFICATE的结构成员<br>
我们发现，对于WIN_CERTIFICATE结构来说，常量0x200和2是比较常见的值，该结构为我们提供了第四个和第五个参数。我们可以通过类似的方式找到其余的输入参数。而对于输出参数来说，则方法完全不同，我们将在后文中详细描述。<br>
进行一些逆向之后，我们得到了函数签名：

```
NTSTATUS CiCheckSignedFile(
    __In__ const PVOID digestBuffer,
    __In__ int digestSize,
    __In__ int digestIdentifier,
    __In__ const LPWIN_CERTIFICATE winCert,
    __In__ int sizeOfSecurityDirectory,
    __Out__ PolicyInfo* policyInfoForSigner,
    __Out__ LARGE_INTEGER* signingTime,
    __Out__ PolicyInfo* policyInfoForTimestampingAuthority
);
```

该函数的工作方法如下：<br>
1、调用方位函数提供文件摘要（缓冲区和算法类型），以及指向Authenticode签名的指针。<br>
2、该函数通过以下方式验证签名和摘要：<br>
（1）遍历文件签名，并获取使用特定摘要算法的签名；<br>
（2）验证签名（和证书），并提取其中显示的文件摘要；<br>
（3）将提取的摘要与调用方提供的摘要进行比较。<br>
3、除了验证文件签名之外，该函数还为调用方提供有关已验证签名的各种详细信息。<br>
该函数后面一部分的工作原理非常值得关注，因为仅仅知道文件已经经过正确签名是不够的，我们还需要知道是由谁进行签名的。在下一节中，我们将解决这一问题。

### <a class="reference-link" name="PolicyInfo%E7%BB%93%E6%9E%84"></a>PolicyInfo结构

到目前为止，我们已经将所有输入参数输入到CiCheckSignedFile()并且能够进行调用。但是，我们除了其大小（在Windows 10 x64上为0x30）之外，对于PolicyInfo结构几乎一无所知。<br>
作为输出参数，我们希望该结构能以某种方式提供有关签名者身份的提示。因此，我们调用该函数，并对内存进行检查，以确认哪些数据填充到PolicyInfo之中。在内存中，似乎包含一个地址和一些较大的数字。<br>
该结构正在内部函数MinCryptVerifyCertificateWithPolicy2()中填充：

[![](./img/200478/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019293c5300481438f.png)

填充PolicyInfo结构<br>
该函数中的某些代码似乎正在检查该值是否在特定范围之内。对于证书验证的过程来说，我们推测这个范围是证书有效的时间范围，事实上证明这是正确的：

[![](./img/200478/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01aac99904fc7dca6f.png)

检查证书有效期<br>
这将引向以下结构：

```
typedef struct _PolicyInfo
{
int structSize;
    NTSTATUS verificationStatus;
    int flags;
    PVOID someBuffer; // later known as certChainInfo; 
    FILETIME revocationTime;
    FILETIME notBeforeTime;
    FILETIME notAfterTime;
} PolicyInfo, *pPolicyInfo;
```

尽管证书的有效期非常值得关注，但是这并不能直接定位到签名者。稍后我们将发现，大多数信息都位于成员certChainInfo之中，我们将在稍后讨论。

### <a class="reference-link" name="CertChainInfo%E7%BC%93%E5%86%B2%E5%8C%BA"></a>CertChainInfo缓冲区

在检查PolicyInfo的内存时，我们可以看到它指向结构外部的内存位置——动态分配的缓冲区。该分配位于I_MinCryptAddChainInfo()中，其函数名称表明了缓冲区的用途。<br>
我们通过检查其内存布局来逆向这一缓冲区：<br>
1、在前几个字节中，有指向缓冲区内部各个位置的指针。<br>
2、在这些指向的位置中，存在重复的模式和指向缓冲区内部更远位置的指针。<br>
3、在最后指向的这些位置中，我们找到了一些文本，看起来像是证书的摘要。<br>
该缓冲区中包含有关整个证书链的数据，既有解析格式（位于子结构中），也有原始数据格式（包含证书、密钥、EKU的ASN.1证书）。<br>
这一部分使调用方可以轻松地查看证书的主题、颁发者、证书链的组成，以及用于创建每个证书的哈希算法。<br>
为了更好地解释这个缓冲区的格式，以及我们从中得到的子结构，我们将分析其在32位计算机上的内存布局。如果使用32位计算机，可以减少混乱的情况，这里可以利用更少的填充字节来满足对齐要求。下面是由Microsoft签名的Notepad.exe的示例：

[![](./img/200478/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t018b38c3cfb50e97f1.png)

CertChainInfo缓冲区的内存视图<br>
我们在这里可以发现：<br>
1、缓冲区的顶部有两个4字节的数字。其中的一个表明在哪里可以找到一系列CertChainMember类型结构的地址，另一个是可以指示其中有多少个结构的计数器。<br>
2、第一个CertChainMember位于地址0x89BF45C8中（以黑色标出），我们将其格式化如下：<br>
（1）在CertChainMembers的末尾，以蓝色标出的地址0x89BF4688处，有纯文本格式的主题名称。<br>
（2）在橙色标出的地址0x89BF4699处，有纯文本格式的发行者名称。<br>
（3）在红色箭头指出的地址0x89BF46BE处，包含实际证书的ASN.1 blob的开头。内存以小端对齐的4字节为一组显示，因此证书的前两个字节实际上是0x3082，而不是如图所示的0x3131。

```
typedef struct _CertChainMember
{
    int digestIdetifier; // e.g. 0x800c for SHA256
    int digestSize; // e.g. 0x20 for SHA256
    BYTE digestBuffer[64]; // contains the digest itself
    CertificatePartyName subjectName; // pointer to the subject name
    CertificatePartyName issuerName; // pointer to the issuer name
    Asn1BlobPtr certificate; // pointer to actual certificate in ASN.1
} CertChainMember, * pCertChainMember;
```

这就是我们之前所说的解析数据。我们无需自行解析证书，就可以获取到主题或颁发者。<br>
该结构中的最后一个字节指向缓冲区内部更远的位置。接下来的96个字节包含第二个CertChainMember，出于可读性的考虑，未将其标出。其中包含有关链的下一个证书的信息。<br>
对于公钥和EKU（扩展密钥用法）来说，存在一系列类似的指针和结构。换而言之，CI从证书中获取了一些关键数据，并且使其以子结构的形式提供给调用方。但是，如果调用方还需要其他的一些内容，那么其中还可能会包括未解析的原始数据。<br>
注意：PolicyInfo和CertChainInfo结构都以结构的大小开始。由于这些结构是可以在OS版本之间实现扩展的，因此在尝试访问其他结构成员之前，必须要检查这里的大小。<br>
在存储库中的文件ci.h中，可以找到CertChainInfo缓冲区的完整分类和各种子结构。

### <a class="reference-link" name="CiFreePolicyInfo()"></a>CiFreePolicyInfo()

该函数将释放PolicyInfo的certChainInfo缓冲区，该缓冲区由CiCheckSignedFile()和其他填充PolicyInfo结构的CI函数分配。该函数还会重置其他结构成员。在这里，必须要对其进行调用，以避免内存泄漏。

[![](./img/200478/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01426f4cb2d2782782.png)

CiFreePolicyInfo()的实现<br>
由于该函数会在内部检查是否有可用的内存，因此即使是未填充PolicyInfo，也可以安全地对其进行调用。

### <a class="reference-link" name="CiValidateFileObject()"></a>CiValidateFileObject()

如前文所述，在调用CiCheckSignedFile()之前需要首先完成一些工作。调用方必须计算文件哈希值并解析PE，以便为函数提供签名的位置。<br>
但是，函数CiValidateFileObject()可以为调用方完成这部分工作。我们不需要从头开始，因为它与CiCheckSignedFile()共享一些参数：

```
NTSTATUS CiValidateFileObject(
    __In__ struct _FILE_OBJECT* fileObject,
    __In__ int a2,
    __In__ int a3,
    __Out__ PolicyInfo* policyInfoForSigner,
    __Out__ PolicyInfo* policyInfoForTimestampingAuthority,
    __Out__ LARGE_INTEGER* signingTime,
    __Out__ BYTE* digestBuffer,
    __Out__ int* digestSize,
    __Out__int* digestIdentifier
);
```

该函数在内核空间中映射文件，并提取其签名：

[![](./img/200478/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c354567c11e98bad.png)

通过CiValidateFileObject()在系统空间中映射文件。<br>
该函数还会计算文件摘要，如果为其提供了足够长的非空缓冲区，将会使用摘要来进行填充。<br>
注意：由于该函数仅在最新的Windows版本上添加，因此我们并未将研究的重点放在这个函数上。如果我们要继续研究，我们会专注于分析其验证的策略。<br>
在这里，使用了比CiCheckSignedFile()更为严格的策略，这意味着它有可能无法验证通过此前经过CiCheckSignedFile()验证的PE。这里可能会受到第2个和第3个参数值的影响，但我们还没有对其进行逆向。



## GitHub Repo

为了演示如何利用ci.dll来验证PE签名，我们使用了GitHub存储库来对本文进行了补充。<br>
该存储库中，包含一个简单的驱动程序，可以用于测试我们上述的研究成果：<br>
1、注册用于新进程通知的回调；<br>
2、尝试使用ci.dll函数来验证每个新进程的PE签名；<br>
3、如果成功验证了文件的签名，驱动程序将解析输出PolicyInfo结构，以提取签名证书及其详细信息。<br>
我们鼓励大家尝试使用这个repo，以初步了解CI，并扩大研究的范围。



## 与CI链接

最后，我们要分析如何与这个未记录的库相链接的过程。尽管使用CI的过程看起来非常枯燥，但我们发现它并不简单，如果大家对其中的更多函数进行扩展研究，可能需要执行与本文相同的步骤。<br>
在与特定的dll链接时，通常使用厂商提供的导入库。在我们的案例中，Microsoft并没有提供.lib文件，我们必须自己生成该文件。在生成之后，该文件应该作为链接器输入添加到项目属性中。下面是生成.lib文件所需的步骤。

### <a class="reference-link" name="64%E4%BD%8D"></a>64位

1、使用dumpbin实用程序从dll中获取导出的函数：

```
dumpbin /EXPORTS c:windowssystem32ci.dll
```

2、创建一个.def文件，如下所示：<br>
LIBRARY ci.dll<br>
EXPORTS<br>
CiCheckSignedFile<br>
CiFreePolicyInfo<br>
CiValidateFileObject<br>
3、使用lib实用程序生成.lib文件：

```
lib /def:ci.def /machine:x64 /out:ci.lib
```

### <a class="reference-link" name="32%E4%BD%8D"></a>32位

这里的情况比较棘手，因为在32位系统中，函数反射参数的总和（以字节为单位），例如：

```
CiFreePolicyInfo@4
```

但是ci.dll会导出没有这部分的函数，因此我们需要创建一个.lib文件以进行这样的转换，所以我们使用了[3]和[4]文章中所描述的方法。<br>
1、如同64位中的第1步和第2步所述，创建一个.def文件。<br>
2、使用具有相同签名的伪装实体的函数stub创建一个C++文件。我们基本上可以模仿厂商从其代码导出函数时的操作。例如：

```
extern "C" __declspec(dllexport) 
PVOID _stdcall CiFreePolicyInfo(PVOID policyInfoPtr)
{
    return nullptr;
}
```

3、将其编译成OBJ文件。<br>
4、使用lib实用工具生成.lib文件，这次使用OBJ文件：

```
Lib /def:ci.def /machine:x86 /out:ci.lib &lt;obj file&gt;
```

在GitHub存储库中，包含stub的代码。



## 总结

本文演示了如何使用CI API中的一部分。我们通过这种方式，成功在内核模式下验证了Authenticode签名，而无需再自行实现。<br>
我们希望本文能为大家对这个dll的后续研究铺平道路。<br>
在这里，我想向对本篇文章提供帮助的几位研究人员表示感谢，他们分别是Yuval Kovacs、Allie Mellen、Philip Tsukerman和Michael Maltsev。



## 参考文章

[1] Microsoft Windows FIPS 140 验证安全策略文档（[https://csrc.nist.gov/csrc/media/projects/cryptographic-module-validation-program/documents/security-policies/140sp3093.pdf）](https://csrc.nist.gov/csrc/media/projects/cryptographic-module-validation-program/documents/security-policies/140sp3093.pdf%EF%BC%89)<br>
[2] Windows驱动签名绕过（作者：derusbi）（[https://www.sekoia.fr/blog/windows-driver-signing-bypass-by-derusbi/）](https://www.sekoia.fr/blog/windows-driver-signing-bypass-by-derusbi/%EF%BC%89)<br>
[3] 如何创建32位导入库（[https://qualapps.blogspot.com/2007/08/how-to-create-32-bit-import-libraries.html）](https://qualapps.blogspot.com/2007/08/how-to-create-32-bit-import-libraries.html%EF%BC%89)<br>
[4] Q131313: 如何创建没有.OBJ或源代码的32位导入库（[https://jeffpar.github.io/kbarchive/kb/131/Q131313/）](https://jeffpar.github.io/kbarchive/kb/131/Q131313/%EF%BC%89)<br>
[5] j00ru关于CI的博客文章（[https://j00ru.vexillium.org/2010/06/insight-into-the-driver-signature-enforcement/）](https://j00ru.vexillium.org/2010/06/insight-into-the-driver-signature-enforcement/%EF%BC%89)

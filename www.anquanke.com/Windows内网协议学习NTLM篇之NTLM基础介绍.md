> 原文链接: https://www.anquanke.com//post/id/193149 


# Windows内网协议学习NTLM篇之NTLM基础介绍


                                阅读量   
                                **1375798**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01da0b6cd153e1bc69.jpg)](https://p0.ssl.qhimg.com/t01da0b6cd153e1bc69.jpg)



作者：daiker@360RedTeam

## 0x00 前言

这个系列文章主要讲ntlm认证相关的内容。以及着重介绍ntlm两大安全问题–PTH和ntlm_relay。

ntlm篇分为四篇文章

第1篇文章也是本文，这篇文章主要简单介绍一些基础概念以及引进一些相关的漏洞，比如Pass The Hash以及ntlm_relay。

其余三篇文章的内容全部都是讲ntlm_relay,这个安全问题是ntlm篇的重点内容。

第2篇文章主要讲触发windows向攻击者发起ntlm请求的一些方式,比如大家耳熟能详的打印机漏洞。

第3篇文章主要讲的是攻击者接收到ntlm请求之后做的事，如爆破Net-ntlm，又或者relay到SMB,HTTP,Exchange,LDAP等。

第4篇文章主要回顾一下从上世纪ntlmrelay被提出来，微软从08年开始为ntlmrelay陆陆续续推出的一些补丁以及绕过,如ms08068，MS16-075，CVE-2015-0005，CVE-2018-8581，CVE-2019-1040,CVE2019-1384。以及ntlm relay的一些缓解措施。



## 0x01 LM Hash &amp; NTLM Hash

windows内部是不保存明文密码的，只保存密码的hash。

其中本机用户的密码hash是放在 本地的SAM文件 里面，域内用户的密码hash是存在域控的NTDS.DIT文件 里面。那hash的格式是怎么样的呢?

在Windows系统导出密码的时候，经常看到这样的密码格式

Administrator:500:AAD3B435B51404EEAAD3B435B51404EE:31D6CFE0D16AE931B73C59D7E0C089C0:::

其中的AAD3B435B51404EEAAD3B435B51404EE是LM Hash

31D6CFE0D16AE931B73C59D7E0C089C0是NTLM Hash

下面详细介绍下这两种hash格式。

### <a name="header-n19"></a>1. LM Hash

全称是LAN Manager Hash, windows最早用的加密算法，由IBM设计。

LM Hash的计算:
1. 用户的密码转换为大写，密码转换为16进制字符串，不足14字节将会用0来再后面补全。
1. 密码的16进制字符串被分成两个7byte部分。每部分转换成比特流，并且长度位56bit，长度不足使用0在左边补齐长度
1. 再分7bit为一组,每组末尾加0，再组成一组
1. 上步骤得到的二组，分别作为key 为 “KGS!@#$%”进行DES加密。
1. 将加密后的两组拼接在一起，得到最终LM HASH值。


```
#coding=utf-8
import re
import binascii
from pyDes import *
def DesEncrypt(str, Des_Key):
    k = des(binascii.a2b_hex(Des_Key), ECB, pad=None)
    EncryptStr = k.encrypt(str)
    return binascii.b2a_hex(EncryptStr)

def group_just(length,text):
    # text 00110001001100100011001100110100001101010011011000000000
    text_area = re.findall(r'.`{`%d`}`' % int(length), text) # ['0011000', '1001100', '1000110', '0110011', '0100001', '1010100', '1101100', '0000000']
    text_area_padding = [i + '0' for i in text_area] #['00110000', '10011000', '10001100', '01100110', '01000010', '10101000', '11011000', '00000000']
    hex_str = ''.join(text_area_padding) # 0011000010011000100011000110011001000010101010001101100000000000
    hex_int = hex(int(hex_str, 2))[2:].rstrip("L") #30988c6642a8d800
    if hex_int == '0':
        hex_int = '0000000000000000'
    return hex_int

def lm_hash(password):
    # 1. 用户的密码转换为大写，密码转换为16进制字符串，不足14字节将会用0来再后面补全。
    pass_hex = password.upper().encode("hex").ljust(28,'0') #3132333435360000000000000000
    print(pass_hex) 
    # 2. 密码的16进制字符串被分成两个7byte部分。每部分转换成比特流，并且长度位56bit，长度不足使用0在左边补齐长度
    left_str = pass_hex[:14] #31323334353600
    right_str = pass_hex[14:] #00000000000000
    left_stream = bin(int(left_str, 16)).lstrip('0b').rjust(56, '0') # 00110001001100100011001100110100001101010011011000000000
    right_stream = bin(int(right_str, 16)).lstrip('0b').rjust(56, '0') # 00000000000000000000000000000000000000000000000000000000
    # 3. 再分7bit为一组,每组末尾加0，再组成一组
    left_stream = group_just(7,left_stream) # 30988c6642a8d800
    right_stream = group_just(7,right_stream) # 0000000000000000
    # 4. 上步骤得到的二组，分别作为key 为 "KGS!@#$%"进行DES加密。
    left_lm = DesEncrypt('KGS!@#$%',left_stream) #44efce164ab921ca
    right_lm = DesEncrypt('KGS!@#$%',right_stream) # aad3b435b51404ee
    # 5. 将加密后的两组拼接在一起，得到最终LM HASH值。
    return left_lm + right_lm

if __name__ == '__main__':
    hash = lm_hash("123456")
```

[![](https://p0.ssl.qhimg.com/t012f096c29bb0e08fb.png)](https://p0.ssl.qhimg.com/t012f096c29bb0e08fb.png)

LM加密算法存在一些固有的漏洞
1. 首先，密码长度最大只能为14个字符
1. 密码不区分大小写。在生成哈希值之前，所有密码都将转换为大写
1. 查看我们的加密过程，就可以看到使用的是分组的DES，如果密码强度是小于7位，那么第二个分组加密后的结果肯定是aad3b435b51404ee，如果我们看到lm hash的结尾是aad3b435b51404ee，就可以很轻易的发现密码强度少于7位
1. 一个14个字符的密码分成7 + 7个字符，并且分别为这两个半部分计算哈希值。这种计算哈希值的方式使破解难度成倍增加，因为攻击者需要将7个字符（而不是14个字符）强制暴力破解。这使得14个字符的密码的有效强度等于，或者是7个字符的密码的两倍，该密码的复杂度明显低于[![](https://p0.ssl.qhimg.com/t01f87ddf44d540f820.png)](https://p0.ssl.qhimg.com/t01f87ddf44d540f820.png) 14个字符的密码的理论强度。
1. Des密码强度不高
### <a name="header-n47"></a>2. NTLM Hash

为了解决LM加密和身份验证方案中固有的安全弱点，Microsoft 于1993年在Windows NT 3.1中引入了NTLM协议。下面是各个版本对LM和NTLM的支持。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01a757a68445cea7e0.png)

其中

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016342a0c8ac5deb12.png)

也就是说从Windows Vista 和 Windows Server 2008开始，默认情况下只存储NTLM Hash，LM Hash将不再存在。(因此后面我们介绍身份认证的时候只介绍Net-ntlm，不再介绍net-lm)如果空密码或者不储蓄LM Hash的话，我们抓到的LM Hash是AAD3B435B51404EEAAD3B435B51404EE。

所以在win7 中我们看到抓到LM Hash都是AAD3B435B51404EEAAD3B435B51404EE，这里的LM Hash并没有价值。

[![](https://p5.ssl.qhimg.com/t0113a4184680657402.png)](https://p5.ssl.qhimg.com/t0113a4184680657402.png)

但某些工具的参数需要填写固定格式LM hash:NT hash，可以将LM hash填0(LM hash可以为任意值)，即00000000000000000000000000000000:NT hash。

接下来讲下NTLM Hash的计算

1.先将用户密码转换为十六进制格式。

2.将十六进制格式的密码进行Unicode编码。

3.使用MD4摘要算法对Unicode编码数据进行Hash计算

```
python2 -c 'import hashlib,binascii; print binascii.hexlify(hashlib.new("md4", "p@Assword!123".encode("utf-16le")).digest())'
```

[![](https://p1.ssl.qhimg.com/t017bef209d40cd30ed.png)](https://p1.ssl.qhimg.com/t017bef209d40cd30ed.png)



## 0x02 NTLM身份验证

NTLM验证是一种Challenge/Response 验证机制，由三种消息组成:通常称为type 1(协商)，类型type 2(质询)和type 3(身份验证)。

它基本上是这样工作的:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01652f775797dd2789.png)
1. 用户登录客户端电脑
1. (type 1)客户端向服务器发送type 1(协商)消息,它主要包含客户端支持和服务器请求的功能列表。
1. (type 2)服务器用type 2消息(质询)进行响应，这包含服务器支持和同意的功能列表。但是，最重要的是，它包含服务器产生的Challenge。
1. (type 3)客户端用type 3消息(身份验证)回复质询。用户接收到步骤3中的challenge之后，使用用户hash与challenge进行加密运算得到response，将response,username,challeng发给服务器。消息中的response是最关键的部分，因为它们向服务器证明客户端用户已经知道帐户密码。
1. 服务器拿到type 3之后，使用challenge和用户hash进行加密得到response2与type 3发来的response进行比较。如果用户hash是存储在域控里面的话，那么没有用户hash，也就没办法计算response2。也就没法验证。这个时候用户服务器就会通过netlogon协议联系域控，建立一个安全通道,然后将type 1,type 2，type3 全部发给域控(这个过程也叫作Pass Through Authentication认证流程)
1. 域控使用challenge和用户hash进行加密得到response2，与type 3的response进行比较
下面简单介绍下三个过程，如果对于细节不感兴趣的话就可以忽略。

### <a name="header-n80"></a>1. type 1 协商

这个过程是客户端向服务器发送type 1(协商)消息,它主要包含客户端支持和服务器请求的功能列表。

主要包含以下结构

[![](https://p0.ssl.qhimg.com/t015ef031f365fe3d58.png)](https://p0.ssl.qhimg.com/t015ef031f365fe3d58.png)

抓包查看对应的信息如下

[![](https://p3.ssl.qhimg.com/t01059b873149a41c7a.png)](https://p3.ssl.qhimg.com/t01059b873149a41c7a.png)

如果想仔细理解每个字段的值请阅读官方文档[NEGOTIATE_MESSAGE](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/b34032e5-3aae-4bc6-84c3-c6d80eadf7f2)

### <a name="header-n87"></a>2. type 2 质询

这个过程是服务器用type 2消息(质询)进行响应，这包含服务器支持和同意的功能列表。但是，最重要的是，它包含服务器产生的Challenge。

主要 包含以下结构

[![](https://p5.ssl.qhimg.com/t01083c0a646ee150b8.png)](https://p5.ssl.qhimg.com/t01083c0a646ee150b8.png)

其中最主要的信息是challenge。后面加密验证依赖于challenge

抓包查看对应的信息如下

[![](https://p3.ssl.qhimg.com/t017b9728ad4bb29739.png)](https://p3.ssl.qhimg.com/t017b9728ad4bb29739.png)

如果想仔细理解每个字段的值请阅读官方文档[CHALLENGE_MESSAGE](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/801a4681-8809-4be9-ab0d-61dcfe762786)

### <a name="header-n95"></a>3. type 3 身份验证

这个过程客户端接收到challenge之后，使用用户hash与challenge进行加密运算得到response，将response,username,challenge发给服务器。消息中的response是最关键的部分，因为它向服务器证明客户端用户已经知道帐户密码。

主要包含以下结构

[![](https://p2.ssl.qhimg.com/t0141f69a04d1f911bd.png)](https://p2.ssl.qhimg.com/t0141f69a04d1f911bd.png)

这里的Challeng不同于type2 的Challenge，这里的Challenge是一个随机的客户端nonce。

MIC是校验和，设计MIC主要是为了防止这个包中途被修改

sessionkey是在要求进行签名的时候用的，用来进行协商加密密钥，可能有些文章会说sessionkey就是加密密钥，需要拥有用户hash才能计算出来，因此攻击者算不出来，就无法加解密包。但是想想就不可能，这个session_key已经在流量里面明文传输，那攻击者拿到之后不就可以直接加解密包了。当然这是后话，后面讲签名的时候会详细讲讲这个问题。

抓包查看对应的信息如下

[![](https://p5.ssl.qhimg.com/t01b92ed02a5371d118.png)](https://p5.ssl.qhimg.com/t01b92ed02a5371d118.png)

如果想仔细理解每个字段的值请阅读官方文档[AUTHENTICATE_MESSAGE](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-nlmp/033d32cc-88f9-4483-9bf2-b273055038ce)



## 0x03 Net-ntlm hash

在type3中的响应，有六种类型的响应
1. LM(LAN Manager)响应 – 由大多数较早的客户端发送，这是“原始”响应类型。
1. NTLM v1响应 – 这是由基于NT的客户端发送的，包括Windows 2000和XP。
1. NTLMv2响应 – 在Windows NT Service Pack 4中引入的一种较新的响应类型。它替换启用了 NTLM版本2的系统上的NTLM响应。
1. LMv2响应 – 替代NTLM版本2系统上的LM响应。
1. NTLM2会话响应 – 用于在没有NTLMv2身份验证的情况下协商NTLM2会话安全性时，此方案会更改LM NTLM响应的语义。
1. 匿名响应 – 当匿名上下文正在建立时使用; 没有提供实际的证书，也没有真正的身份验证。“存 根”字段显示在类型3消息中。
这六种使用的加密流程一样，都是前面我们说的Challenge/Response 验证机制,区别在Challenge和加密算法不同。

这里我们侧重讲下NTLM v1响应和NTLMv2响应
1. v2是16位的Challenge，而v1是8位的Challenge
1. v1是将 16字节的NTLM hash空填充为21个字节，然后分成三组，每组7比特，作为3DES加密算法的三组密钥，加密Server发来的Challenge。 将这三个密文值连接起来得到response。
而v2是的加密算法是。

(1). 将Unicode后的大写用户名与Unicode后的身份验证目标（在Type 3消息的”TargetName”字段中指定的域或服务器名称）拼在一起。请注意，用户名将转换为大写，而身份验证目标区分大小写，并且必须与“TargetName”字段中显示的大小写匹配。使用16字节NTLM哈希作为密钥，得到一个值。

(2) 构建一个blob信息

[![](https://p0.ssl.qhimg.com/t01e4cbca0d8b47ef87.png)](https://p0.ssl.qhimg.com/t01e4cbca0d8b47ef87.png)

(3). 使用16字节NTLMv2哈希作为密钥，将HMAC-MD5消息认证代码算法加密一个值(来自type 2的Challenge与Blob拼接在一起)。得到一个16字节的NTProofStr。

(4). 将NTProofStr与Blob拼接起来形成得到response。
- 至于选择哪个版本的响应由LmCompatibilityLevel决定。
Challenge/Response验证机制里面type3 response里面包含Net-ntlm hash，NTLM v1响应和NTLMv2响应对应的就是Net-ntlm hash分为Net-ntlm hash v1和Net-ntlm hash v2。

Net-ntlm hash v1的格式为：

username::hostname:LM response:NTLM response:challenge

Net-ntlm hash v2的格式为：

username::domain:challenge:HMAC-MD5:blob

下面演示从response里面提取NTLMv2

[![](https://p0.ssl.qhimg.com/t01033e44db2d66d47d.png)](https://p0.ssl.qhimg.com/t01033e44db2d66d47d.png)

这里的challenge是type2 服务器返回的challenge不是type3 流量包里面的client Challenge

[![](https://p2.ssl.qhimg.com/t014e1677448378606a.png)](https://p2.ssl.qhimg.com/t014e1677448378606a.png)

就是7ac429882efc7e29

HMAC-MD5对应数据包中的NTProofSt

[![](https://p0.ssl.qhimg.com/t01e1f5459fd8566a93.png)](https://p0.ssl.qhimg.com/t01e1f5459fd8566a93.png)

00a9055c4007c7eb1c1386504d0a7162

blob就是response 减去NTP1roofStr。(因为在计算response 的时候，response 就是由NTProofStr加上blob)

[![](https://p3.ssl.qhimg.com/t012cb5ef3281fb1f87.png)](https://p3.ssl.qhimg.com/t012cb5ef3281fb1f87.png)

就是0101000000000000772eaacee59dd5014b484239683639570000000001000c00570049004e0037002d00310002000800540045005300540003002200570049004e0037002d0031002e0074006500730074002e006c006f00630061006c000400140074006500730074002e006c006f00630061006c000500140074006500730074002e006c006f00630061006c0007000800772eaacee59dd5010900160063006900660073002f00570049004e0037002d0031000000000000000000

所以最后的ntlm v2 hash是win7::test.local:7ac429882efc7e29:00a9055c4007c7eb1c1386504d0a7162:0101000000000000772eaacee59dd5014b484239683639570000000001000c00570049004e0037002d00310002000800540045005300540003002200570049004e0037002d0031002e0074006500730074002e006c006f00630061006c000400140074006500730074002e006c006f00630061006c000500140074006500730074002e006c006f00630061006c0007000800772eaacee59dd5010900160063006900660073002f00570049004e0037002d0031000000000000000000



## 0x04 SSP &amp; SSPI



[![](https://p3.ssl.qhimg.com/t011196a61b6f4e8bd8.png)](https://p3.ssl.qhimg.com/t011196a61b6f4e8bd8.png)
- SSPI(Security Support Provider Interface)
这是 Windows 定义的一套接口，此接口定义了与安全有关的功能函数， 用来获得验证、信息完整性、信息隐私等安全功能，就是定义了一套接口函数用来身份验证，签名等，但是没有具体的实现。
- SSP(Security Support Provider)
SSPI 的实现者，对SSPI相关功能函数的具体实现。微软自己实现了如下的 SSP，用于提供安全功能：
1. NTLM SSP
1. Kerberos
1. Cred SSP
1. Digest SSP
1. Negotiate SSP
1. Schannel SSP
1. Negotiate Extensions SSP
1. PKU2U SSP
在系统层面，SSP就是一个dll，来实现身份验证等安全功能，实现的身份验证机制是不一样的。比如 NTLM SSP 实现的就是一种 Challenge/Response 验证机制。而 Kerberos 实现的就是基于 ticket 的身份验证机制。我们可以编写自己的 SSP，然后注册到操作系统中，让操作系统支持更多的自定义的身份验证方法。

这个地方可以用于留作后门。这个地方就不详细展开了。具体的细节见[域渗透——Security Support Provider](http://drops.wooyun.org/tips/12518)

我们抓包分析ntlm的时候，就会看到ntlm是放在GSS-API里面

[![](https://p4.ssl.qhimg.com/t015c465e9c5203d28c.png)](https://p4.ssl.qhimg.com/t015c465e9c5203d28c.png)

为啥这里会出现GSSAPI呢，SSPI是GSSAPI的一个专有变体，进行了扩展并具有许多特定于Windows的数据类型。SSPI生成和接受的令牌大多与GSS-API兼容。所以这里出现GSSAPI只是为了兼容，我们可以不必理会。可以直接从NTLM SSP开始看起。注册为SSP的一个好处就是，SSP实现了了与安全有关的功能函数，那上层协议(比如SMB)在进行身份认证等功能的时候，就可以不用考虑协议细节，只需要调用相关的函数即可。而认证过程中的流量嵌入在上层协议里面。不像kerbreos，既可以镶嵌在上层协议里面，也可以作为独立的应用层协议。ntlm是只能镶嵌在上层协议里面，消息的传输依赖于使用ntlm的上层协议。比如镶嵌在SMB协议里面是这样。

[![](https://p0.ssl.qhimg.com/t01a5f1e17a942ed8ed.png)](https://p0.ssl.qhimg.com/t01a5f1e17a942ed8ed.png)

镶嵌在HTTP协议里面是这样

[![](https://p1.ssl.qhimg.com/t018e779bcb3f1fec0a.png)](https://p1.ssl.qhimg.com/t018e779bcb3f1fec0a.png)



## 0x05 LmCompatibilityLevel

此安全设置确定网络登录使用的质询/响应身份验证协议。此选项会影响客户端使用的身份验证协议的等级、协商的会话安全的等级以及服务器接受的身份验证的等级，其设置值如下:
- 发送 LM NTLM 响应: 客户端使用 LM 和 NTLM 身份验证，而决不会使用 NTLMv2 会话安全；域控制器接受 LM、NTLM 和 NTLMv2 身份验证。
- 发送 LM &amp; NTLM – 如果协商一致，则使用 NTLMv2 会话安全: 客户端使用 LM 和 NTLM 身份验证，并且在服务器支持时使用 NTLMv2 会话安全；域控制器接受 LM、NTLM 和 NTLMv2 身份验证。
- 仅发送 NTLM 响应: 客户端仅使用 NTLM 身份验证，并且在服务器支持时使用 NTLMv2 会话安全；域控制器接受 LM、NTLM 和 NTLMv2 身份验证。
- 仅发送 NTLMv2 响应: 客户端仅使用 NTLMv2 身份验证，并且在服务器支持时使用 NTLMv2 会话安全；域控制器接受 LM、NTLM 和 NTLMv2 身份验证。
- 仅发送 NTLMv2 响应\拒绝 LM: 客户端仅使用 NTLMv2 身份验证，并且在服务器支持时使用 NTLMv2 会话安全；域控制器拒绝 LM (仅接受 NTLM 和 NTLMv2 身份验证)。
- 仅发送 NTLMv2 响应\拒绝 LM &amp; NTLM: 客户端仅使用 NTLMv2 身份验证，并且在服务器支持时使用 NTLMv2 会话安全；域控制器拒绝 LM 和 NTLM (仅接受 NTLMv2 身份验证)。
默认值:
- Windows 2000 以及 Windows XP: 发送 LM &amp; NTLM 响应
- Windows Server 2003: 仅发送 NTLM 响应
- Windows Vista、Windows Server 2008、Windows 7 以及 Windows Server 2008 R2及以上: 仅发送 NTLMv2 响应
[![](https://p5.ssl.qhimg.com/t010894985fe47d94d9.png)](https://p5.ssl.qhimg.com/t010894985fe47d94d9.png)



## 0x06 相关的安全问题

### <a name="header-n212"></a>1. pass the hash

也叫hash传递攻击,简称PTH。

在type3计算response的时候，客户端是使用用户的hash进行计算的，而不是用户密码进行计算的。因此在模拟用户登录的时候。是不需要用户明文密码的，只需要用户hash。微软在2014年5月13日发布了针对Pass The Hash的更新补丁kb2871997，标题为”Update to fix the Pass-The-Hash Vulnerability”,而在一周后却把标题改成了”Update to improve credentials protection and management”。(事实上，这个补丁不仅能够缓解PTH,还能阻止mimikatz 抓取明文密码，本系列文章侧重于协议认证的问题，因此不在这里扩展介绍其他内容)。
- (1) kb2871997
这里来探讨下为啥kb2871997能缓解pth，又不能杜绝Pth。

首先kb2871997对于本地Administrator(rid为500，操作系统只认rid不认用户名，接下来我们统称RID 500帐户)和本地管理员组的域用户是没有影响的。

在打了kb2871997补丁的机子上

[![](https://p4.ssl.qhimg.com/t0124941e4f33c3871f.png)](https://p4.ssl.qhimg.com/t0124941e4f33c3871f.png)

使用RID 500帐户进行pth登录

[![](https://p1.ssl.qhimg.com/t01a45f6924b1ad93c9.png)](https://p1.ssl.qhimg.com/t01a45f6924b1ad93c9.png)

使用本地管理员组的域用户进行pth登录

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0104ade7a44ed37643.png)

使用本地管理员组的非RID 500帐户进行pth登录

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0165f4c775bfdb58cb.png)

发现ntlm认证通过之后，对ADMIN$没有写入权限。那么是什么阻止了我们对本地管理员组的非RID500帐户使用哈希传递？为什么RID 500帐户具有特殊情况？除此之外，为什么本地管理员成员的域帐户也可以免除这种阻止行为。(事实上，之前在winrm进行远程登录的时候我也遇到相关的问题，winrm远程登录只能使用RID 500帐户与本地管理员成员的域用户登录，不能使用本地管理员组的非RID500账户)

所有这些问题的真正罪魁祸首是远程访问上下文中的用户帐户控制（UAC）令牌筛选。

对于远程连接到Windows Vista +计算机的任何非RID 500本地管理员帐户，无论是通过WMI，PSEXEC还是其他方法(有个例外，那就是通过RDP远程)，即使用户是本地管理员，返回的令牌都是已过滤的管理员令牌。

已过滤的管理员令牌有如下特征(深入解析Windows操作系统第六版P501)

[![](https://p4.ssl.qhimg.com/t01e1beff637118ef6d.png)](https://p4.ssl.qhimg.com/t01e1beff637118ef6d.png)

[![](https://p1.ssl.qhimg.com/t01b482d74bab13bb3e.png)](https://p1.ssl.qhimg.com/t01b482d74bab13bb3e.png)

通俗点来说就是管理员组的非RID500账户登录之后是没有过UAC的，所有特权都被移除，除了上图的Change Notify之类的。而RID500账户登录之后也以完全管理特权（”完全令牌模式”）运行所有应用程序，实际是不用过UAC的，这个可以自己测试下。

对于本地“管理员”组中的域用户帐户，文档指出：

当具有域用户帐户的用户远程登录Windows Vista计算机并且该用户是Administrators组的成员时，域用户将在远程计算机上以完全管理员访问令牌运行，并且该用户的UAC被禁用在该会话的远程计算机上。

如果HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\LocalAccountTokenFilterPolicy项存在(默认不存在)且配置为1，将授予来自管理员所有本地成员的远程连接完整的高完整性令牌。这意味着未过滤非RID 500帐户连接，并且可以成功传递哈希值！

[![](https://p3.ssl.qhimg.com/t01221ddc6baf81eced.png)](https://p3.ssl.qhimg.com/t01221ddc6baf81eced.png)

[![](https://p1.ssl.qhimg.com/t017437fa4f410b5c4d.png)](https://p1.ssl.qhimg.com/t017437fa4f410b5c4d.png)

默认情况下这个注册表项是不存在的，我们可以用以留作后门，但是有意思的是，我们之前提过一嘴的，在配置winrm的时候，也会遇到同样的问题，本地管理员组的非RID500账户不能登录，于是有些运维在搜寻了一堆文章后，开启该注册表项是最快捷有效的问题:)。
- (2) 进行pth 的一些常用工具
一般有两种场景底下需要用到pth，第一种是我们已知目标计算机的IP,用户名，hash尝试登陆目标主机。

另外一种场景就是我们在一个大型的内网环境底下获得一个用户的hash，尝试去撞整个内网的相同密码的主机，从而进行横向移动。下面列举部分pth的工具。

**mimikatz**

```
privilege::debug
sekurlsa::pth /user:win10 /domain:test.local /ntlm:6a6293bc0c56d7b9731e2d5506065e4a
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0117905a98ff4aa7dd.png)

接下来就可以使用psecex,wmic,at之类的进行远程命令执行。

**impacket**

impacket底下执行远程命令执行的脚本有5个

psexec.py<br>
smbexec.py<br>
atexec.py<br>
wmiexec.py<br>
dcomexec.py

都支持使用hash进行远程命令执行，通过–hashes指定hash,以psexec.py为例

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013106324e4c6006b7.png)

**cobalstrike**

cabalstrike支持批量得进行pth，在横向移动中撞密码hash中特别有效

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0159df5cdfaa1554e7.png)

**msf**

msf的exploit/windows/smb/psexec_psh模块是支持对一个网段进行pth的，在横向移动中撞密码hash中特别有效

[![](https://p5.ssl.qhimg.com/t0148b646c5232cefd6.png)](https://p5.ssl.qhimg.com/t0148b646c5232cefd6.png)

[![](https://p0.ssl.qhimg.com/t0116645dec15ad9302.png)](https://p0.ssl.qhimg.com/t0116645dec15ad9302.png)

### <a name="header-n267"></a>2. 利用ntlm进行的信息收集

回顾type2 。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a96dbd992ca3ca85.png)

在type2返回Challenge的过程中，同时返回了操作系统类型，主机名，netbios名等等。这也就意味着如果我们在能跟服务器进行ntlm 交流中，给服务器发送一个type1的请求，服务器返回type2的响应，这一步，我们就可以得到很多信息。前面我们说过ntlm是一个嵌入式的协议，消息的传输依赖于使用ntlm的上层协议，比如SMB,LDAP,HTTP等。我们以SMB为例。在目标主机开放了445或者139的情况，通过给服务器发送一个type1的请求，然后解析type2的响应。就可以收集到一些信息。

直接上代码(代码来源[c#版本的smb_version](https://www.zcgonvh.com/post/CSharp_smb_version_Detection.html))，大家也可以仿造代码的形式，自己实现其他上层协议下的信息收集。



```
using System;
using System.Data;
using System.Text;
using System.Text.RegularExpressions;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using System.Diagnostics;
using System.IO;
using System.Security.Cryptography;
using System.Net;
using System.Net.Sockets;
using System.Reflection;
using System.Runtime;
using System.Runtime.InteropServices;

namespace Zcg.Tests
`{`
    class smbver
    `{`
        static byte[] d1 =`{`
    0x00, 0x00, 0x00, 0x85, 0xFF, 0x53, 0x4D, 0x42, 0x72, 0x00, 0x00, 0x00, 0x00, 0x18, 0x53, 0xC8, 
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFE, 
    0x00, 0x00, 0x00, 0x00, 0x00, 0x62, 0x00, 0x02, 0x50, 0x43, 0x20, 0x4E, 0x45, 0x54, 0x57, 0x4F, 
    0x52, 0x4B, 0x20, 0x50, 0x52, 0x4F, 0x47, 0x52, 0x41, 0x4D, 0x20, 0x31, 0x2E, 0x30, 0x00, 0x02, 
    0x4C, 0x41, 0x4E, 0x4D, 0x41, 0x4E, 0x31, 0x2E, 0x30, 0x00, 0x02, 0x57, 0x69, 0x6E, 0x64, 0x6F, 
    0x77, 0x73, 0x20, 0x66, 0x6F, 0x72, 0x20, 0x57, 0x6F, 0x72, 0x6B, 0x67, 0x72, 0x6F, 0x75, 0x70, 
    0x73, 0x20, 0x33, 0x2E, 0x31, 0x61, 0x00, 0x02, 0x4C, 0x4D, 0x31, 0x2E, 0x32, 0x58, 0x30, 0x30, 
    0x32, 0x00, 0x02, 0x4C, 0x41, 0x4E, 0x4D, 0x41, 0x4E, 0x32, 0x2E, 0x31, 0x00, 0x02, 0x4E, 0x54, 
    0x20, 0x4C, 0x4D, 0x20, 0x30, 0x2E, 0x31, 0x32, 0x00
`}`;
        static byte[] d2 =`{`
    0x00, 0x00, 0x01, 0x0A, 0xFF, 0x53, 0x4D, 0x42, 0x73, 0x00, 0x00, 0x00, 0x00, 0x18, 0x07, 0xC8, 
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFE, 
    0x00, 0x00, 0x40, 0x00, 0x0C, 0xFF, 0x00, 0x0A, 0x01, 0x04, 0x41, 0x32, 0x00, 0x00, 0x00, 0x00, 
    0x00, 0x00, 0x00, 0x4A, 0x00, 0x00, 0x00, 0x00, 0x00, 0xD4, 0x00, 0x00, 0xA0, 0xCF, 0x00, 0x60, 
    0x48, 0x06, 0x06, 0x2B, 0x06, 0x01, 0x05, 0x05, 0x02, 0xA0, 0x3E, 0x30, 0x3C, 0xA0, 0x0E, 0x30, 
    0x0C, 0x06, 0x0A, 0x2B, 0x06, 0x01, 0x04, 0x01, 0x82, 0x37, 0x02, 0x02, 0x0A, 0xA2, 0x2A, 0x04, 
    0x28, 0x4E, 0x54, 0x4C, 0x4D, 0x53, 0x53, 0x50, 0x00, 0x01, 0x00, 0x00, 0x00, 0x07, 0x82, 0x08, 
    0xA2, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 
    0x00, 0x05, 0x02, 0xCE, 0x0E, 0x00, 0x00, 0x00, 0x0F, 0x00, 0x57, 0x00, 0x69, 0x00, 0x6E, 0x00, 
    0x64, 0x00, 0x6F, 0x00, 0x77, 0x00, 0x73, 0x00, 0x20, 0x00, 0x53, 0x00, 0x65, 0x00, 0x72, 0x00, 
    0x76, 0x00, 0x65, 0x00, 0x72, 0x00, 0x20, 0x00, 0x32, 0x00, 0x30, 0x00, 0x30, 0x00, 0x33, 0x00, 
    0x20, 0x00, 0x33, 0x00, 0x37, 0x00, 0x39, 0x00, 0x30, 0x00, 0x20, 0x00, 0x53, 0x00, 0x65, 0x00, 
    0x72, 0x00, 0x76, 0x00, 0x69, 0x00, 0x63, 0x00, 0x65, 0x00, 0x20, 0x00, 0x50, 0x00, 0x61, 0x00, 
    0x63, 0x00, 0x6B, 0x00, 0x20, 0x00, 0x32, 0x00, 0x00, 0x00, 0x00, 0x00, 0x57, 0x00, 0x69, 0x00, 
    0x6E, 0x00, 0x64, 0x00, 0x6F, 0x00, 0x77, 0x00, 0x73, 0x00, 0x20, 0x00, 0x53, 0x00, 0x65, 0x00, 
    0x72, 0x00, 0x76, 0x00, 0x65, 0x00, 0x72, 0x00, 0x20, 0x00, 0x32, 0x00, 0x30, 0x00, 0x30, 0x00, 
    0x33, 0x00, 0x20, 0x00, 0x35, 0x00, 0x2E, 0x00, 0x32, 0x00, 0x00, 0x00, 0x00, 0x00
`}`;
static byte[] d3=`{`
0x81,0x00,0x00,0x44,0x20,0x43,0x4b,0x46,0x44,0x45,0x4e,0x45,0x43,0x46,0x44,0x45
,0x46,0x46,0x43,0x46,0x47,0x45,0x46,0x46,0x43,0x43,0x41,0x43,0x41,0x43,0x41,0x43
,0x41,0x43,0x41,0x43,0x41,0x00,0x20,0x43,0x41,0x43,0x41,0x43,0x41,0x43,0x41,0x43
,0x41,0x43,0x41,0x43,0x41,0x43,0x41,0x43,0x41,0x43,0x41,0x43,0x41,0x43,0x41,0x43
,0x41,0x43,0x41,0x43,0x41,0x41,0x41,0x00
`}`;
        static void Main(string[] args)
        `{`
            Console.WriteLine("SMB Version Detection tool 0.1");
            Console.WriteLine("Part of GMH's fuck Tools, Code By zcgonvh.\r\n");
            if (args.Length &lt; 1) `{` Console.WriteLine("usage: smbver host [port]"); return; `}`
            string host = args[0];
            int port = 445;
            try `{` port = int.Parse(args[1]); `}`
            catch `{` `}`
            try
            `{`
                byte[] buf = new byte[1024];
                Socket sock = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
                sock.Connect(host, port);
                if(port==139)
                `{`
                  sock.Send(d3);
                  sock.Receive(buf);
                `}`
                sock.Send(d1);
                sock.Receive(buf);
                sock.Send(d2);
                sock.Receive(buf);
                int len = BitConverter.ToInt16(buf, 43);
                string[] ss = Encoding.Unicode.GetString(buf, len + 47, buf.Length - len - 47).Split('\0');
                Console.WriteLine("native os: " + ss[0]);
                Console.WriteLine("native lan manager: " + ss[1]);
                int off = 0;
                for (int i = 47; i &lt; len - 7; i++)
                `{`
                    if (buf[i] == 'N' &amp;&amp; buf[i + 1] == 'T' &amp;&amp; buf[i + 2] == 'L' &amp;&amp; buf[i + 3] == 'M' &amp;&amp; buf[i + 4] == 'S' &amp;&amp; buf[i + 5] == 'S' &amp;&amp; buf[i + 6] == 'P') `{` off = i; break; `}`
                `}`
                byte[] ntlm = new byte[len];
                Array.Copy(buf, off, ntlm, 0, len);
                len = BitConverter.ToInt16(ntlm, 0xc);
                off = BitConverter.ToInt16(ntlm, 0x10);
                Console.WriteLine("negotiate target: " + Encoding.Unicode.GetString(ntlm, off, len));
                Console.WriteLine("os major version: " + ntlm[off - 8]);
                Console.WriteLine("os minor version: " + ntlm[off - 7]);
                Console.WriteLine("os build number: " + BitConverter.ToInt16(ntlm, off - 6));
                Console.WriteLine("ntlm current revision: " + ntlm[off - 1]);
                off += len;
                int type = BitConverter.ToInt16(ntlm, off);
                while (type != 0)
                `{`
                    off += 2;
                    len = BitConverter.ToInt16(ntlm, off);
                    off += 2;
                    switch (type)
                    `{`
                        case 1:
                            `{`
                                Console.WriteLine("NetBIOS computer name: " + Encoding.Unicode.GetString(ntlm, off, len));
                                break;
                            `}`
                        case 2:
                            `{`
                                Console.WriteLine("NetBIOS domain name: " + Encoding.Unicode.GetString(ntlm, off, len));
                                break;
                            `}`
                        case 3:
                            `{`
                                Console.WriteLine("DNS computer name: " + Encoding.Unicode.GetString(ntlm, off, len));
                                break;
                            `}`
                        case 4:
                            `{`
                                Console.WriteLine("DNS domain name: " + Encoding.Unicode.GetString(ntlm, off, len));
                                break;
                            `}`
                        case 5:
                            `{`
                                Console.WriteLine("DNS tree name: " + Encoding.Unicode.GetString(ntlm, off, len));
                                break;
                            `}`
                        case 7:
                            `{`
                                Console.WriteLine("time stamp: `{`0:o`}`", DateTime.FromFileTime(BitConverter.ToInt64(ntlm, off)));
                                break;
                            `}`
                        default:
                            `{`
                                Console.Write("Unknown type `{`0`}`, data: ", type);
                                for (int i = 0; i &lt; len; i++)
                                `{`
                                    Console.Write(ntlm[i + off].ToString("X2"));
                                `}`
                                Console.WriteLine();
                                break;
                            `}`
                    `}`
                    off += len;
                    type = BitConverter.ToInt16(ntlm, off);
                `}`
            `}`
            catch (Exception ex)
            `{`
                Console.WriteLine("err: " + ex);
            `}`
        `}`
    `}`
`}`
```

效果展示图是这样的

[![](https://p1.ssl.qhimg.com/t01a5a1d429091eed8c.png)](https://p1.ssl.qhimg.com/t01a5a1d429091eed8c.png)

msf底下也有类似的模块auxiliary/scanner/smb/smb_version

[![](https://p5.ssl.qhimg.com/t01d70f343693e66d02.png)](https://p5.ssl.qhimg.com/t01d70f343693e66d02.png)

### <a name="header-n279"></a>3. ntlm relay

Hot Potato，2018-8581,2019-1040相信大家也都不陌生了，这其中都有ntlmrelay的影子。作为一个在上世纪就被提出的安全问题，时至2019的今天，ntlmrelay仍然在远程命令执行。横向扩展，权限提升等方面发挥着巨大的作用。本篇文章剩余部门简单的介绍一些ntlm_relay相关的概念。

(1) ntlm_relay 的一般过程

先回顾下之前ntlm 认证的 type1,type2,type 3

[![](https://p5.ssl.qhimg.com/t0136db5569cead54d9.png)](https://p5.ssl.qhimg.com/t0136db5569cead54d9.png)

那如果这个时候有个中间的攻击者出现

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01f22f78b71df16680.png)

看图已经能够很清晰得理解ntlm_relay的一般过程，作为中间人，攻击者将来自客户端的包(type 1)转发给服务端，将来自服务端的challenge(type 2)转发给客户端，然后客户端计算完response 之后，再把response(type 3) 转发给服务端，服务端验证rsponse通过之后，授予攻击者访问的权限。

我们抓包查看整个过程跟上图差不多(其中Attacker是172.16.100.1,Inventory Server是172.16.100.5，Target是172.16.100.128)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016395a8a64a3be7d5.png)

(2) ntlmrelay or smbrelay

我们之前反复在说一件事,ntlm是一个嵌入式的协议，消息的传输依赖于使用ntlm的上层协议，比如SMB,LDAP,HTTP等。我们通过查看包就可以很清楚的看到这一点。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f6c531213ccdbf84.png)

那ntlm的上层协议是smb的情况下,ntlmrelay就是smbrelay。那如果上层协议是http，我们也可以叫做httprelay，但是都统称ntlmrelay，因此，后面统一用ntlm_relay，就不再纠结这个字样了。

(3) 跨协议的relay

又是我们之前反复强调的一个点,ntlm是一个嵌入式的协议，消息的传输依赖于使用ntlm的上层协议，比如SMB,LDAP,HTTP等,那不管上层协议是啥，ntlm的认证总归是type 1,type 2,type3 。所以我们就不局限于之前提到的smb到smb这种relay，可以在一个协议里面提取ntlm认证信息，放进另外一个协议里面，实现跨协议的relay。

(4) relay or reflet

再看看relay的这种图

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e24deae4329ae2eb.png)



如上图，如果Inventory Server和Target是同一台机子，那么也就是说我们攻击者拿到Inventory Server发来的请求之后，发回给Inventory Server进行认证。这个就是reflect。在工作组环境里面，工作组中的机器之间相互没有信任关系，每台机器的账号密码只是保存在自己的SAM文件中，这个时候relay到别的机器，除非两台机器的账号密码一样，不然没有别的意义了，这个时候的攻击手段就是将机器reflect回机子本身。因此微软在ms08-068中对smb reflect到smb 做了限制。CVE-2019-1384(Ghost Potato)就是绕过了该补丁。

(5) 挖掘ntlm_relay的一般方法
1. 如何触发Inventory Server 向Attacker发起请求，将在下篇文章里面详细阐述
1. Attacker拿到请求之后，是进行ntlm ntlm破解还是选择进行relay，relay的话，可以跨协议relay，那relay到不同的协议能起到什么作用，将在下下篇文章里面详细阐述。
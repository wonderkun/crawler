> 原文链接: https://www.anquanke.com//post/id/244155 


# 强网杯2021-[强网先锋]协议 Writeup


                                阅读量   
                                **114454**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t017f0fd214c52aa470.png)](https://p1.ssl.qhimg.com/t017f0fd214c52aa470.png)



## PPTP (RFC2637)

PPTP（Point to Point Tunneling Protocol），即点对点隧道协议，是在PPP协议的基础上开发的一种新的增强型安全协议， 支持多协议虚拟专用网（VPN），可以通过密码验证协议（PAP）、可扩展认证协议（EAP）等方法增强安全性。可以使远程用户通过拨入ISP、通过直接连接Internet或其他网络安全地访问企业网。

创建基于 PPTP 的 VPN 连接过程中，使用的认证机制与创建 PPP 连接时相同。此类认证机制主要有：扩展身份认证协议 （EAP，Extensible Authentication Protocol）、询问握手认证协议（CHAP，Challenge Handshake Authentication Protocol）和口令认证协议（PAP，Password Authentication Protocol），当前采用最多的是 CHAP 协议。PPTP用到的数据流量加密协议是MPPE。



## CHAP (RFC 2433 和 RFC 2759)

CHAP 是基于挑战-响应的认证协议。挑战响应协议中，通常是验证者随机选择一个数作为挑战，声称者利用秘密信息和挑战生成响应，验证者根据验证响应是否正确来判定认证是否通过。

在 Windows 系统中PPTP协议实现采用的Microsoft版本的CHAP协议，目前有CHAP v1 和CHAP v2两个版本，分别在RFC 2433和RFC 2759中定义。

CHAP v1 协议流程如下：<br>
(1) 客户端向服务器发送一个连接请求；<br>
(2) 服务器返回一个 8 字节的随机挑战值Challenge；<br>
(3) 客户端使用LAN Manager杂凑算法对用户口令做杂凑得到16字节输出，在其后补5个字节0得到21个字节值，按顺序分割为3个7字节值k1,k2,k3；<br>
(4) 分别以k1,k2,k3为密钥对Challenge做DES加密，然后将三个密文块连接为一个24字节的响应；<br>
(5) 客户端使用NTLM v2杂凑算法和相同的步骤创建第二个24字节响应；<br>
(6) 服务器在数据库中查到同样的HASH值并对随机质询数作同样的运算，将所得与收到的应答码作比较。若匹配，则认证通过；<br>
(7) 生成会话密钥用于MPPE加密。



## MPPE (RFC3078、3079)

MPPE流量加密的大致流程如下：（具体见RFC3078、3079）<br>
(1) 初始化会话密钥<br>
(2) 生成RC4密钥<br>
(3) 数据加密<br>
(4) 密钥同步的2个模式
- 无状态模式：每个包加密的密钥都是不同的, 每个包都要重新计算会话密钥，每个包都会设置“A”标志
- 状态保持模式：发送方发现序号的后8位已经为0xff时更新密钥，更新完再加密和发送，包中设置“A”标志；


## 出题思路：

在建立好PPTP连接后，捕获完整流量。这里的密码可以根据流量包里的挑战值Challenge和响应值Response爆破得到。然后分析chap认证协议的实现代码，发现不需要用到挑战值，于是把这个包给去掉。最后按照MEEP协议解密流量。

此题主要是理解chap协议认证原理(RFC 2433或RFC 2759)以及MEEP协议(RFC3078、3079)加密原理，利用chap解出密码，再用MEEP还原流。



## 解题思路：

打开流量包基本是PPP Comp的流量，有个flag`{`fake_hint_weak_password`}`提示弱口令（用户名也提示了的）

[![](https://p0.ssl.qhimg.com/t015c78b83f197d8a36.png)](https://p0.ssl.qhimg.com/t015c78b83f197d8a36.png)

流量是基于PPTP的VPN通信 ，采用了CHAP做单向认证，MPPE用于加密流量，参照附录的RFC文档编写程序

[![](https://p4.ssl.qhimg.com/t013e8260f4571ec47c.png)](https://p4.ssl.qhimg.com/t013e8260f4571ec47c.png)

由于CHAP做认证时Password是加密过的，（提示是弱口令），尝试爆破。正常的解题思路是根据Challenge和Response爆破Password，而题目只有Response。但是由于捕获的流量没有CHAP的第一个包，也就没有挑战值（8个字节），爆破挑战值是不可能了。

分析RFC 2433或RFC 2759，需要根据协议的流程，找到 PasswordHash和Challenge生成Response的实现伪代码（也就是上面CHAP v1 协议流程的第5步），如下：

[![](https://p5.ssl.qhimg.com/t01bc0148228c70c0f8.png)](https://p5.ssl.qhimg.com/t01bc0148228c70c0f8.png)

写成Python代码，具体实现函数如下：

[![](https://p0.ssl.qhimg.com/t010391339e2d184dca.png)](https://p0.ssl.qhimg.com/t010391339e2d184dca.png)

函数大致功能是将hash处理后的Password分为3份，作为DES的Key给Challenge加3次密，Response保存3次加密的结果。编写逆程序，即利用PasswordHash和Response解密生成Challenge，代码如下：

[![](https://p3.ssl.qhimg.com/t01c74a42e46ac7f045.png)](https://p3.ssl.qhimg.com/t01c74a42e46ac7f045.png)

这里会得到3个Challenge，如果都相等，则表示当前爆破的密码是对的。那么就可以以此为依据爆破密码，得到6位纯数字密码：729174。同时Challenge也可以得到：a0dc69227cde47db

再利用RFC的MPPE文档编写还原程序即可得到明文。



## 具体操作：

打开1.pcap，找到第3个包（CHAP认证的第二个响应包）

[![](https://p3.ssl.qhimg.com/t0163dd28cc5b5634de.png)](https://p3.ssl.qhimg.com/t0163dd28cc5b5634de.png)

找到其中的响应值Response，Value Size为49，取Response=Value[24:48]，Hex值如下：

[![](https://p5.ssl.qhimg.com/t019ac4bf5499769b94.png)](https://p5.ssl.qhimg.com/t019ac4bf5499769b94.png)

在“exp-1密码爆破及挑战值还原.py”中填入Response

[![](https://p5.ssl.qhimg.com/t01e183110c4b8d8ba9.png)](https://p5.ssl.qhimg.com/t01e183110c4b8d8ba9.png)

运行得到结果如下：

[![](https://p4.ssl.qhimg.com/t019672a689073de904.png)](https://p4.ssl.qhimg.com/t019672a689073de904.png)

得到Password和Challenge之后就可以还原数据流得到flag，可以利用网上的工具。这里给出本人根据MPPE协议解密脚本（exp-2流还原.py和MSCHAP.py），供大家参考，便于理解协议细节。



## 附件链接

附件链接：[https://pan.baidu.com/s/1L8cq8UJAT5aE-oezCQrwyQ](https://pan.baidu.com/s/1L8cq8UJAT5aE-oezCQrwyQ)<br>
提取码：dltp



## 解题脚本

### <a class="reference-link" name="exp-1%E5%AF%86%E7%A0%81%E7%88%86%E7%A0%B4%E5%8F%8A%E6%8C%91%E6%88%98%E5%80%BC%E8%BF%98%E5%8E%9F.py"></a>exp-1密码爆破及挑战值还原.py

```
import os
import string
import binascii
import hashlib
from binascii import b2a_hex, a2b_hex
from Crypto.Hash import MD4
from Crypto.Cipher import DES
from Crypto.Util.number import long_to_bytes, bytes_to_long

def md4(b):
    h = MD4.new()
    h.update(b)
    return h.digest()

def sha1(b):
    sha = hashlib.sha1(b)
    return sha.digest()

def NtPasswordHash(Password):
    md4 = MD4.new()
    md4.update(Password)
    pwhash = md4.hexdigest()
    return long_to_bytes(int(pwhash, 16))

def InsertBit(key):
    l = bytes_to_long(key)
    l = bin(l)[2:].zfill(56)
    l = list(l)
    l.insert(7, '0')
    l.insert(15, '0')
    l.insert(23, '0')
    l.insert(31, '0')
    l.insert(39, '0')
    l.insert(47, '0')
    l.insert(55, '0')
    l.insert(63, '0')
    res = "".join(l)
    res = long_to_bytes(int(res, 2))
    return res

def pad(PasswordHash):
    ZPasswordHash = PasswordHash +(21 - len(PasswordHash)) * b'\x00'
    return ZPasswordHash

def Password2Unicode(Password):
    Password_Unicode = ""
    for ch in Password:
        Password_Unicode += ch + "\x00"
    return Password_Unicode

def ChallengeResponse(Challenge, PasswordHash):
    ZPasswordHash = pad(PasswordHash)
    Response = b""
    for i in range(3):
        key = ZPasswordHash[i*7:i*7+7]
        key = InsertBit(key)
        des = DES.new(key, DES.MODE_ECB)
        Response += des.encrypt(Challenge)
        print(f"Response(`{`len(Response)`}`): `{`b2a_hex(Response)`}`")
    return Response

def ResponseChallenge(Response, PasswordHash):
    ZPasswordHash = pad(PasswordHash)
    Challenge_list = []
    for i in range(3):
        key = ZPasswordHash[i*7:i*7+7]
        key = InsertBit(key)
        try:
            des = DES.new(key, DES.MODE_ECB)
        except:
            return None
        Challenge_list.append(des.decrypt(Response[i*8:i*8+8]))
    return Challenge_list

def jiami(Password, Challenge):
    Password_Unicode = Password2Unicode(Password)
    pwhash = NtPasswordHash(Password_Unicode.encode())
    s = ChallengeResponse(Challenge, pwhash)
    s = bytes_to_long(s)
    s = hex(s)[2:]
    return s

def get_Response(Password, Challenge):
    Challenge = a2b_hex(Challenge)
    response = jiami(Password, Challenge)
    # print("响应值:", response)
    return response

def jiemi(Password, Response):
    Password_Unicode = Password2Unicode(Password)
    pwhash = NtPasswordHash(Password_Unicode.encode())
    Challenge_list = ResponseChallenge(Response, pwhash)
    ''' 3次的挑战值相等，则爆破成功 '''
    if Challenge_list!=None and Challenge_list[0] == Challenge_list[1] and Challenge_list[0] == Challenge_list[2]:
        s = Challenge_list[0]
        s = bytes_to_long(s)
        s = hex(s)[2:]
        return s
    else:
        return None

def get_Challenge(Password, Response):
    Response = a2b_hex(Response)
    Challenge = jiemi(Password, Response)
    # print("挑战值:", Challenge)
    return Challenge

''' 生成长度为n，字符集为charset的字符串 '''
def generator(n, charset=string.digits+string.ascii_uppercase+string.ascii_lowercase):
    if n == 0:
        yield ''      ################
        return
    f = generator(n-1, charset)
    for s in f:
        for i in range(len(charset)):
            yield charset[i]+s

''' 生成长度不超过n，字符集为charset的字符串 '''
def Generator(n, charset=string.digits):
    global global_cnt
    for i in range(n+1):
        f = generator(i, charset=charset)
        for s in f:
            global_cnt += 1
            s = s[::-1]
            if global_cnt % 737 == 0:
                print(s, end='\r')
            yield s

if __name__ == '__main__':
    global_cnt = 0
    Response = "8a1e597d699574ff810dbc3798640fa584ccf9524857c45a"   ### 在这里填写 Response ###
    gen = Generator(10)         # 爆破字典
    for Password in gen:
        Challenge = get_Challenge(Password, Response)
        if Challenge != None:
            print("Password:", Password)
            print("Challenge:", Challenge)
            break

    ''' result '''
    # Password: 729174
    # Challenge: a0dc69227cde47db

    ''' test '''
    MyResponse = get_Response(Password, Challenge)
    print("响应值:", MyResponse, MyResponse==Response)
    # 响应值: 8a1e597d699574ff810dbc3798640fa584ccf9524857c45a (== Response)
    input()
    input()
    input()
```

### <a class="reference-link" name="exp-2%E6%B5%81%E8%BF%98%E5%8E%9F.py"></a>exp-2流还原.py

```
import os
import re
import uuid
import base64
import binascii
from MSCHAP import *
from Crypto.Hash import MD4
from Crypto.Cipher import DES
from Crypto.Cipher import ARC4
from binascii import b2a_hex, a2b_hex
try:
    import scapy.all as scapy
except ImportError:
    import scapy

''' 2.4.  Key Derivation Functions '''
SHApad1 = b'\x00' * 40
SHApad2 = b'\xf2' * 40

def Get_Key(InitialSessionKey, CurrentSessionKey, LengthOfDesiredKey):
    Context = InitialSessionKey[0:LengthOfDesiredKey]
    Context += SHApad1
    Context += CurrentSessionKey[0:LengthOfDesiredKey]
    Context += SHApad2
    CurrentSessionKey = sha1(Context) 
    return CurrentSessionKey[0:LengthOfDesiredKey]

def Get_Start_Key(Challenge, NtPasswordHashHash):   # 8-octet, 16-octet
    InitialSessionKey = sha1(NtPasswordHashHash + NtPasswordHashHash + Challenge)
    return InitialSessionKey[:16]

def rc4_decrpt_hex(data, key):
    rc41=ARC4.new(key)
    # print dir(rc41)
    return rc41.decrypt(data)

def get_CurrentSessionKey(InitialSessionKey, CurrentSessionKey):
    CurrentSessionKey = Get_Key(InitialSessionKey, CurrentSessionKey, 16)
    CurrentSessionKey = rc4_decrpt_hex(CurrentSessionKey, CurrentSessionKey)
    return CurrentSessionKey

if __name__ == "__main__":
    # 0-to-256-unicode-char Password
    Password = "729174"                 ### 在这里填写 Password    ###
    # 8-octet Challenge
    Challenge = "a0dc69227cde47db"      ### 在这里填写 Challenge   ###

    ''' 1 '''
    pcap_path = '1.pcap'                   ### 在这里填写 pcap文件位置 ###

    '''  '''
    Challenge = bytes.fromhex(Challenge)
    PasswordHash = NtPasswordHash(Password)
    print('PasswordHash:', PasswordHash.hex())
    PasswordHashHash = HashNtPasswordHash(PasswordHash)
    print('PasswordHashHash:', PasswordHashHash.hex())

    ''' Generating 128-bit Session Keys '''
    # 初始密钥
    InitialSessionKey = Get_Start_Key(Challenge, PasswordHashHash)
    print('InitialSessionKey:', InitialSessionKey.hex())
    # 当前会话密钥
    CurrentSessionKey = InitialSessionKey
    print('CurrentSessionKey:', CurrentSessionKey.hex())
    CurrentSessionKey = Get_Key(InitialSessionKey, CurrentSessionKey, 16)
    print('CurrentSessionKey:', CurrentSessionKey.hex())

    ''' 抓包 '''
    pcap_cnt = 0
    comp_data_list = []
    packets = scapy.rdpcap(pcap_path)
    for packet in packets:
        pcap_cnt += 1
        if packet.haslayer('PPP_') and packet['IP'].src == '192.168.188.170':
            comp_data_list.append(bytes(packet[4])[2:])

    ''' 加密数据流解密 '''
    output = b''
    for j in range(len(comp_data_list)):
        # print('数据流', j)
        # 当前会话密钥（迭代）
        CurrentSessionKey = get_CurrentSessionKey(InitialSessionKey, CurrentSessionKey)
        # 当前加密数据
        data = comp_data_list[j]
        result = rc4_decrpt_hex(data, CurrentSessionKey)
        # print(result.hex())
        output += result
        # print()
    print('############################### 最终结果 ##################################################')
    # print(output)
    flag_Regex = re.compile(r'flag`{`.*?`}`')
    flag_results = flag_Regex.findall(output.decode('ISO8859-1'))
    print(flag_results)
```

### <a class="reference-link" name="MSCHAP.py"></a>MSCHAP.py

```
# 根据RFC2759文档编写
import os
import hashlib
from Crypto.Hash import MD4
from Crypto.Cipher import DES

def md4(b):
    h = MD4.new()
    h.update(b)
    return h.digest()

def sha1(b):
    sha = hashlib.sha1(b)
    return sha.digest()

def odd_even_parity(b): # 奇偶校验
    result = ''
    for i in range(0, len(b), 7):
        if b[i:i+7].count('1') % 2 == 0:
            result += b[i:i+7]+'0'
        else:
            result += b[i:i+7]+'1'
    return(result)

''' 8.1 '''
def  GenerateNTResponse(AuthenticatorChallenge, PeerChallenge, UserName, Password):
    Challenge =  ChallengeHash(PeerChallenge, AuthenticatorChallenge, UserName) # 8-octet
    PasswordHash = NtPasswordHash(Password)         # 16-octet
    NT_Response = ChallengeResponse(Challenge, PasswordHash)   # 24-octet
    return NT_Response     # 24-octet

''' 8.2 '''
def ChallengeHash(PeerChallenge, AuthenticatorChallenge, UserName):
    UserName = UserName.encode('utf8')
    Context = sha1(PeerChallenge+AuthenticatorChallenge+UserName)
    Challenge = Context[:8]
    return Challenge    # 8-octet 

''' 8.3 PasswordHash = NTLM_Hash(Password) '''
def NtPasswordHash(Password):
    # Password转换成Unicode编码（utf-16编码去掉前缀 FF FE）
    Bytes = Password.encode('utf16')[2:]
    # 对Unicode编码进行MD4加密
    PasswordHash = md4(Bytes)
    return PasswordHash # 16-octet

''' 8.4 PasswordHashHash = MD4(PasswordHash) '''
def HashNtPasswordHash(PasswordHash):   # 16-octet
    PasswordHashHash = md4(PasswordHash)
    return PasswordHashHash     # 16-octet

''' 8.5 '''
def ChallengeResponse(Challenge, PasswordHash):  # 8-octet, 16-octet
    ''' Step 1: 16字节PasswordHashHash分成3份 7 7 2'''
    part1 = PasswordHash[0:7]
    part2 = PasswordHash[7:14]
    part3 = PasswordHash[14:16]
    ''' Step 2: 奇偶校验+扩展 '''
    # part1 （每7bits+1bit校验位）7bytes==&gt;8bytes
    Bits = bytes2bits(part1)
    Bits = odd_even_parity(Bits)
    key1 = bits2bytes(Bits)
    # part2 （每7bits+1bit校验位）7bytes==&gt;8bytes
    Bits = bytes2bits(part2)
    Bits = odd_even_parity(Bits)
    key2 = bits2bytes(Bits)
    # part3 （先添5个字节的0，在每7bits+1bit校验位）2bytes==&gt;7bytes==&gt;8bytes
    Bits = bytes2bits(part3+b'\x00'*5)
    Bits = odd_even_parity(Bits)
    key3 = bits2bytes(Bits)
    ''' Step 3: DES3 '''
    result1 = DesEncrypt(Challenge, key1)[:8]
    result2 = DesEncrypt(Challenge, key2)[:8]
    result3 = DesEncrypt(Challenge, key3)[:8]
    Response = result1 + result2 + result3
    return Response     # 24-octet

''' 8.6 '''
def DesEncrypt(Clear, Key): # 8-octet, 7-octet
    if Clear is None:
        return ""
    # ECB方式
    generator = DES.new(Key, DES.MODE_ECB)
    # 非8整数倍明文补位
    pad = 8 - len(Clear) % 8
    pad_str = b""
    for i in range(pad):
        pad_str = pad_str + int.to_bytes(pad, length=1, byteorder='big')
    # 加密
    Cypher = generator.encrypt(Clear + pad_str)
    return Cypher       # 8-octet
```

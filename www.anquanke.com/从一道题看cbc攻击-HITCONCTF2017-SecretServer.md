> 原文链接: https://www.anquanke.com//post/id/158233 


# 从一道题看cbc攻击-HITCONCTF2017-SecretServer


                                阅读量   
                                **185779**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t0123ee5e2bbe25c885.jpg)](https://p4.ssl.qhimg.com/t0123ee5e2bbe25c885.jpg)

## 前话

xman处看到一题特别有意思的题目，问了下老师，恍然大悟。



## 题目

题目源码:

```
import os, base64, time, random, string
from Crypto.Cipher import AES
from Crypto.Hash import *

key = os.urandom(16)

def pad(msg):
    pad_length = 16-len(msg)%16
    return msg+chr(pad_length)*pad_length

def unpad(msg):
    return msg[:-ord(msg[-1])]

def encrypt(iv,msg):
    msg = pad(msg)
    cipher = AES.new(key,AES.MODE_CBC,iv)
    encrypted = cipher.encrypt(msg)
    return encrypted

def decrypt(iv,msg):
    cipher = AES.new(key,AES.MODE_CBC,iv)
    decrypted = cipher.decrypt(msg)
    decrypted = unpad(decrypted)
    return decrypted

def send_msg(msg):
    iv = '2jpmLoSsOlQrqyqE'
    encrypted = encrypt(iv,msg)
    msg = iv+encrypted
    msg = base64.b64encode(msg)
    print msg
    return

def recv_msg():
    msg = raw_input()
    try:
        msg = base64.b64decode(msg)
        assert len(msg)&lt;500
        decrypted = decrypt(msg[:16],msg[16:])
        return decrypted
    except:
        print 'Error'
        exit(0)

def proof_of_work():
    proof = ''.join([random.choice(string.ascii_letters+string.digits) for _ in xrange(20)])
    digest = SHA256.new(proof).hexdigest()
    print "SHA256(XXXX+%s) == %s" % (proof[4:],digest)
    x = raw_input('Give me XXXX:')
    if len(x)!=4 or SHA256.new(x+proof[4:]).hexdigest() != digest: 
        exit(0)
    print "Done!"
    return

if __name__ == '__main__':
    proof_of_work()
    with open('flag.txt') as f:
        flag = f.read().strip()
    assert flag.startswith('hitcon`{`') and flag.endswith('`}`')
    send_msg('Welcome!!')
    while True:
        try:
            msg = recv_msg().strip()
            if msg.startswith('exit-here'):
                exit(0)
            elif msg.startswith('get-flag'):
                send_msg(flag)
            elif msg.startswith('get-md5'):
                send_msg(MD5.new(msg[7:]).digest())
            elif msg.startswith('get-time'):
                send_msg(str(time.time()))
            elif msg.startswith('get-sha1'):
                send_msg(SHA.new(msg[8:]).digest())
            elif msg.startswith('get-sha256'):
                send_msg(SHA256.new(msg[10:]).digest())
            elif msg.startswith('get-hmac'):
                send_msg(HMAC.new(msg[8:]).digest())
            else:
                send_msg('command not found')
        except:
            exit(0)
```

这里我们能够得到的信息是:<br>
一个固定的iv:`2jpmLoSsOlQrqyqE`<br>
一个已知的明文:`Welcome!!`<br>
返回并得到加密之后的结果，而我们可以看到解密的结果是这样组成的。<br>`MmpwbUxvU3NPbFFycXlxRc/vKRt4fANSEpCk0agly4E=`<br>
base64解密之后得到的是iv+decryption:<br>`2jpmLoSsOlQrqyqE + D(Welcome!!)`<br>
如果最后后端解密出来的明文中存在某些特定的命令，就能跳转到相应的函数，所以如果我们能够控制解密出来的明文，那么就能执行任意命令了。那么如何做到呢？



## 精彩的异或执行任意命令

到了最精彩的地方了，注意别眨眼！
- D(密文) = “Welcome!!” ^ IV1
- 明文 = D(密文) ^ IV2
<li>明文 = “Welcome!!” ^ IV1 ^ IV2<br>
其中”Welcome!!” 和 IV1无法改变，所以如果能改变IV2,就能改变明文。这时候我们这么操作:</li>
IV2 = “Welcome” ^ IV1 ^ “控制的字符串”<br>
这样明文就会变成”控制的字符串了,具体实现函数为:

```
def strxor(str1, str2):
  return ''.join([chr(ord(c1) ^ ord(c2)) for c1, c2 in zip(str1, str2)])
def flipplain(oldplain, newplain, iv):
  """flip oldplain to new plain, return proper iv"""
  return strxor(strxor(oldplain, newplain), iv)
get_flag_iv = flipplain(pad("Welcome!!"), pad("get-flag"), iv_encrypt)
msg = base64.b64encode(get_flag_iv + base64.b64decode(msg)[16:])
```

最后的结果用中间量输出，可以看出已经成功的将最后解密明文控制住了。(太精彩了这一步):<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/hwhxy/hwhxy.github.io/master/images/xmancrypto1.png)下面根据最后的命令执行：

```
if msg.startswith('exit-here'):
    exit(0)
if msg.startswith('get-flag'):
    send_msg(flag)
elif msg.startswith('get-md5'):
    send_msg(MD5.new(msg[7:]).digest())
elif msg.startswith('get-time'):
    send_msg(str(time.time()))
elif msg.startswith('get-sha1'):
    send_msg(SHA.new(msg[8:]).digest())
elif msg.startswith('get-sha256'):
    send_msg(SHA256.new(msg[10:]).digest())
elif msg.startswith('get-hmac'):
    send_msg(HMAC.new(msg[8:]).digest())
else:
    send_msg('command not found')
```

如果还是没理解，建议对照下面的图再重新理一遍思路。<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://raw.githubusercontent.com/hwhxy/hwhxy.github.io/master/images/SecretService1.png)



## unpad非法截断枚举flagMd5得flag

我们已经能得到flag的加密的值了。但是这还不够，还得得到flag的明文。这个时候去关注其他的命令，观察到`send_msg(MD5.new(msg[7:]).digest())`这条命令，他最后能将解密出来的字符串除去前七位的md5的值而flag的类型为hitcon`{``}`，前七位刚好是`hitcon`{``,我们知道aes加解密过程是不依赖于iv的，而`get-md5`正好是7位,也就是说我们按照上面的思路：

```
new_iv = flipplain(pad("hitcon`{`"), pad("get-md5"), iv_encrypt)
msg = base64.b64encode(new_iv + cipher_flag + last_byte_iv + cipher_welcome)
```

最后能得到’get-md5’+flag[7:]的加密值，跳进去get-md5命令之后就能得到MD5(flag[7:])的值，不过这还不够，我们观察:

```
def unpad(msg):
    return msg[:-ord(msg[-1])]
```

unpad函数并没有校验msg[-1]是否合法，所以我们根据这个bug函数+aes的分组链接模式(下一个密文解密的iv由上一个密文充当，为此深夜打扰了一波iromise)，所以我们可以接着拼接一段 iv2+cipher ，让iv2[-1]足够大，大到从末端切割掉flag[7:]的尾巴，假设切割到只剩下一位，则我们可以得到`MD5(flag[7:8])`,然后我们暴力枚举，发送字符串到服务器，匹配正确的密文就能找到flag[7:8]。同理得到flag[7:8]之后开始爆破flag[7:9],因为这时候你知道了flag[7:8],实际上也只要爆破一位，以此类推就能得到flag。具体代码见:<br>[https://github.com/ctf-wiki/ctf-challenges/blob/master/crypto/blockcipher/padding-oracle-attack/2017_hitcon_secret_server/exp.py](https://github.com/ctf-wiki/ctf-challenges/blob/master/crypto/blockcipher/padding-oracle-attack/2017_hitcon_secret_server/exp.py)



## 后话

(tips: 其中52-53行的`new_iv = flipplain("hitcon`{`".ljust(16, 'x00'), "get-md5".ljust(16, 'x00'), iv_encrypt)`可以替换成我上面说的`new_iv = flipplain(pad("hitcon`{`"), pad("get-md5"), iv_encrypt)`,因为iv并不影响aes解密过程，所以也无妨，只能说liubaozheng老师想的更加细致了。)

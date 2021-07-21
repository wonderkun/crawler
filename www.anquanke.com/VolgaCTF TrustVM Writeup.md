> 原文链接: https://www.anquanke.com//post/id/175795 


# VolgaCTF TrustVM Writeup


                                阅读量   
                                **174922**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/dm/1024_578_/t013f8bc6e9b27829e8.jpg)](https://p2.ssl.qhimg.com/dm/1024_578_/t013f8bc6e9b27829e8.jpg)



下载题目，总共三个文件: `reverse`, `encrypt`,`data.enc` [题目地址](https://drive.google.com/drive/folders/1xi005iFU8PYxWl4ofCzPaKQny-KoTV0L?usp=sharing) 另外附上[idb文件](https://drive.google.com/open?id=1Toe2873nlTox556oVeBCocY818rjErch)地址方便调试

根据题目名和文件猜测， 应该是一个虚拟机，`encrypt`文件中存储opcode， `data.enc`是通过`reverse`根据`encypt`加密得来的密文。

ida 分析`reverse`代码

运行`reverse`需要输入 `progname`(`encrypt`) 和 `filetoprocess`(`被加密文件`) 做参数。

构造`test` 测试文件

```
0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
```

第一次运行

[![](https://p3.ssl.qhimg.com/t0137c1bb5cfe2c4047.png)](https://p3.ssl.qhimg.com/t0137c1bb5cfe2c4047.png)

分析`reverse`文件的`main`函数代码

得到读取文件的函数 记 `read_` `(sub_55CBF7147210)`

程序开始时通过传入参数读入`encrypttest`文件

[![](https://p1.ssl.qhimg.com/t01fde83869e788579c.png)](https://p1.ssl.qhimg.com/t01fde83869e788579c.png)

接着解码opcode 并跳转

[![](https://p2.ssl.qhimg.com/t01b7ca211fcf501149.png)](https://p2.ssl.qhimg.com/t01b7ca211fcf501149.png)

开始调试，跟踪执行流程

发现出题人对代码做了处理，每个opcode对应的操作被写在一块汇编代码中，无法反编译。但是有一个特征，会经常跳回`0055D1D8DB1AD0`段代码， 在此处下断点，猜测是对`encrypt`文件进行解码跳转到下一个指令。

[![](https://p2.ssl.qhimg.com/t014b126d59a9a20f3b.png)](https://p2.ssl.qhimg.com/t014b126d59a9a20f3b.png)

根据ida的流程图，在附近转转就会发现写入数据到加密文件的块

[![](https://p0.ssl.qhimg.com/t012160a52acb9eed0b.png)](https://p0.ssl.qhimg.com/t012160a52acb9eed0b.png)

完整分析这个块就知道，写入数据由寄存器`rbp`确定， 在`Hex View`设置 `Synchronize with RBP`

[![](https://p5.ssl.qhimg.com/t019d64a6b9713cea22.png)](https://p5.ssl.qhimg.com/t019d64a6b9713cea22.png)

再次调试，发现`rbp`就是`test`文件数据存放的位置，而且整个过程`rbp`值没有变动

[![](https://p2.ssl.qhimg.com/t01f0684570f2b14b6c.png)](https://p2.ssl.qhimg.com/t01f0684570f2b14b6c.png)

每次F9， 记录F9次数， 直到数据改变，由此可以得到，修改`rbp`指向数据的代码块(地址: `0561D0A7D5F20`)

[![](https://p0.ssl.qhimg.com/t014737ba4d53321016.png)](https://p0.ssl.qhimg.com/t014737ba4d53321016.png)

多次调试发现，该块代码是将固定地址(`0561D0A9D7240`)的数据复制到`rbp`指向的数据，每次复制16*4字节数据。猜测加密处理的基本单位是 64 字节。

[![](https://p4.ssl.qhimg.com/t01f4cd2e11512e8350.png)](https://p4.ssl.qhimg.com/t01f4cd2e11512e8350.png)

新开一个`Hex View` 看`0561D0A9D7240`处数据，调试得到对该处数据进行修改的代码段。发现这段数据是由两处数据(`0561D0A9D7380`[^1] `0561D0A9D7280`[^2])异或 (`0000561D0A7D5CB0`)后通过`encode_1`(`0561D0A7D5C10`)操作的结果。第二段数据就是待加密数据(有很明显特征，可以更改数据进行验证)。

[![](https://p1.ssl.qhimg.com/t01984a413550cdd789.png)](https://p1.ssl.qhimg.com/t01984a413550cdd789.png)

[![](https://p3.ssl.qhimg.com/t01bf0a957cadeb0cf3.png)](https://p3.ssl.qhimg.com/t01bf0a957cadeb0cf3.png)

[![](https://p0.ssl.qhimg.com/t0131ce53a92f3aa9b9.png)](https://p0.ssl.qhimg.com/t0131ce53a92f3aa9b9.png)

分析`encode_1`，发现其接收两个参数，一个被操作数据，另一short类型的数据。调试发现参数只存在两种情况(`0561D0A9D7380`, `0x6f`) 和 (`0561D0A9D7280`, `0x4d`)

```
跟踪地址 000055CBF7348380(key[i]) 000055CBF7348280(buf[i]) 000055CBF7348240(enc[i])
1-&gt;&gt;&gt;
E1 A9 E1 2E 0B 15 44 9C  08 DC DC F3 1A 91 9C 6E
34 5C E4 5E F9 E2 5F F1  F0 86 05 A8 70 6E 04 53
9D 31 EC 10 AB EA F6 74  44 79 0F 28 53 40 37 2C
17 9A C3 67 95 2F 4B 27  D9 3F F9 1D 2A 70 77 5D     ---&gt; magic/key[0]

xor(buf[0], key[0]) --&gt;
D0 9B D2 1A 3E 23 73 A4  31 EC BD 91 79 F5 F9 08
05 6E D7 6A CC D4 68 C9  C9 B6 64 CA 13 0A 61 35
AC 03 DF 24 9E DC C1 4C  7D 49 6E 4A 30 24 52 4A
26 A8 F0 53 A0 19 7C 1F  E0 0F 98 7F 49 14 12 3B

encode_1(| , 0x4d) --&gt;
EF 03 FC 01 F3 2F 89 42  62 07 7A 53 5A C3 67 64
8E 34 86 BD 37 32 AF 3E  1F A1 C0 ED 5A 8D 99 1A
2D 39 D9 96 4C 79 42 21  AC 86 75 E0 9B C4 93 3B
98 A9 2F C9 4D 09 86 44  4A C9 04 15 7E 0A 34 83     ---&gt; enc[0]


2-&gt;&gt;&gt;
E1 A9 E1 2E 0B 15 44 9C  08 DC DC F3 1A 91 9C 6E
34 5C E4 5E F9 E2 5F F1  F0 86 05 A8 70 6E 04 53
9D 31 EC 10 AB EA F6 74  44 79 0F 28 53 40 37 2C
17 9A C3 67 95 2F 4B 27  D9 3F F9 1D 2A 70 77 5D     ---&gt; key[0]

encode_1(key[0], 0x6f) --&gt;
E1 B3 CA 97 A5 93 EC 9F  FC 0E 15 B8 BB AE F0 D4
70 97 85 0A 22 4E 04 6E  EE 79 8D 48 4E 37 1A 2E
72 AF 7C F1 AF 78 78 C3  02 54 38 37 82 A9 CE 18
76 88 55 75 7B 3A A2 BC  07 94 29 A0 1B 96 0B CD  

xor(|, buf[0]) --&gt;
D0 81 F9 A3 90 A5 DB A7  C5 3E 74 DA D8 CA 95 B2
41 A5 B6 3E 17 78 33 56  D7 49 EC 2A 2D 53 7F 48
43 9D 4F C5 9A 4E 4F FB  3B 64 59 55 E1 CD AB 7E
47 BA 66 41 4E 0C 95 84  3E A4 48 C2 78 F2 6E AB     ---&gt; key[1]

xor(buf[1], key[1]) --&gt;
E1 B3 CA 97 A5 93 EC 9F  FC 0E 15 B8 BB AE F0 D4
70 97 85 0A 22 4E 04 6E  EE 79 8D 48 4E 37 1A 2E
72 AF 7C F1 AF 78 78 C3  02 54 38 37 82 A9 CE 18
76 88 55 75 7B 3A A2 BC  07 94 29 A0 1B 96 0B CD 

encode_1(| , 0x4d) --&gt;
94 F7 80 32 05 74 C3 72  A1 39 7C 56 F9 B2 74 92
FD 93 DF A1 02 77 D7 15  9E 1A EE B2 50 41 C4 89
C0 CD 3D AF 11 C9 E9 46  C3 45 EE 95 2F FE 15 0F
6F 58 80 0A E7 46 30 D5  19 C3 0E B1 AA 6E 4F 47    --&gt; enc[1]

3-&gt;&gt;&gt;
D0 81 F9 A3 90 A5 DB A7  C5 3E 74 DA D8 CA 95 B2
41 A5 B6 3E 17 78 33 56  D7 49 EC 2A 2D 53 7F 48
43 9D 4F C5 9A 4E 4F FB  3B 64 59 55 E1 CD AB 7E
47 BA 66 41 4E 0C 95 84  3E A4 48 C2 78 F2 6E AB

...
```

得到加密算法

```
# encoding=utf-8
magic = [225, 169, 225, 46, 11, 21, 68, 156, 8, 220, 220, 243, 26, 145, 156, 110, 52, 92, 228, 94, 249, 226, 95, 241, 240, 134, 5, 168, 112, 110, 4, 83, 157, 49, 236, 16, 171, 234, 246, 116, 68, 121, 15, 40, 83, 64, 55, 44, 23, 154, 195, 103, 149, 47, 75, 39, 217, 63, 249, 29, 42, 112, 119, 93]

def xor(a, b):
    res = []
    for i in range(len(a)):
        res.append(a[i] ^ b[i])
    return res

def encode_1(arr, num):
    result = [0] * 0x40
    cl = num &amp; 7
    idx = num &gt;&gt; 3
    for i in range(0x40):
        result[(idx+i)%0x40] = ((arr[(0x3f+i+1)%0x40] &lt;&lt; cl) | (arr[(0x3f+i)%0x40]&gt;&gt;(8-cl)))&amp;0xff
    return result

def encrypt(buf):
    key = [] * len(buf)
    enc = [] * len(buf)

    key[0] = magic
    enc[0] = encode_1(xor(magic, buf[0]), 0x4d)
    for i in range(len(buf) - 1):
        key[i+1] = xor(encode_1(key[i], 0x6f), buf[i])
        enc[i+1] = encode_1(xor(key[i+1], buf[i+1]), 0x4d)
    return enc
# 解密
# de_decode_1 来自 yype
def de_encode_1(arr,num):
    result = [0] * 0x40
    cl = num &amp; 7
    idx = num &gt;&gt; 3
    for i in range(0x40):
        result[(0x3f+i+1)%0x40] += arr[(idx+i)%0x40] &gt;&gt; cl
        result[(0x3f+i)%0x40] += (arr[(idx+i)%0x40] &lt;&lt; (8-cl))&amp;0xff
    return result

def decrypt():
    # get enc
    data = open("./data.enc", "rb").read()
    data += b'x00' * (len(data)%0x40)    # padding
    len_0 = len(data)//0x40
    enc = []
    buf = []
    key = []
    for i in range(len_0):
        enc.append([x for x in data[i*0x40: (i+1)*0x40]])
        buf.append([])
        key.append([])

    key[0] = magic 
    buf[0] = xor(de_encode_1(enc[0], 0x4d), magic)
    for i in range(1, len_0):
        key[i] = xor(encode_1(key[i-1], 0x6f), buf[i-1])
        buf[i] = xor(de_encode_1(enc[i], 0x4d), key[i])

    data = b''
    # show buf
    for x in buf:
        data += bytearray(x)
    open("data.png", "wb").write(data)
if __name__ == "__main__":
    decrypt()
```

得到flag

总结一下，这个题目关键是调试，由于算法部分只能看汇编，直接全部看明白需要花费较长时间。调试和猜测能大大减少时间。

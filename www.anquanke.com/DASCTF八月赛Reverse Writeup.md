> 原文链接: https://www.anquanke.com//post/id/217527 


# DASCTF八月赛Reverse Writeup


                                阅读量   
                                **215114**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01ff6d5404059c4c04.jpg)](https://p4.ssl.qhimg.com/t01ff6d5404059c4c04.jpg)



## 前言

八月赛时候就看了一眼题，没怎么做。这几天复盘总结时候，居然发现没有公开的Writeup，所以有了这篇文章。这次三道题目风格相似，题目之中都有相同的部分，应该是同一个师傅出的。



## UR_BAD_BAD

直接拖入IDA，找main函数，F5大法一气呵成。

[![](https://p1.ssl.qhimg.com/t01524c802aa08592d5.png)](https://p1.ssl.qhimg.com/t01524c802aa08592d5.png)

之后就看到这个位运算，看起来还是挺头疼的。但是这里和加密没有半点关系，因为整个main函数流程就是假的。细心观察一下，会发现这里的Welcome的w是大写的。而真正运行起来，w是小写的。

[![](https://p4.ssl.qhimg.com/t013f33747450b4be4c.png)](https://p4.ssl.qhimg.com/t013f33747450b4be4c.png)

这时候说明没有走这个main流程。需要去找到真正的流程，去字符串找一下，看到一些奇怪的字符串。

[![](https://p2.ssl.qhimg.com/t01d419a0682e428cfe.png)](https://p2.ssl.qhimg.com/t01d419a0682e428cfe.png)

然后通过这个字符串可以找到一段看上去很可疑的代码，但没有被IDA识别为函数。这里被加了花指令，需要我们手动去花。代码太长，写一个idapython的脚本

```
start_addr = 0x4020b3
end_addr = 0x402DB9
while(start_addr &lt;= end_addr):
    if Byte(start_addr) == 0xe8 and Byte(start_addr+1) == 0x3 and Byte(start_addr+2) == 0:
        for j in range(13):
            PatchByte(start_addr+j,0x90)
        start_addr += 13
        continue
    start_addr += 1

print 'success'
```

之后就可以看伪代码了。

[![](https://p0.ssl.qhimg.com/t015c2ce36c4055e11e.png)](https://p0.ssl.qhimg.com/t015c2ce36c4055e11e.png)

可以看到第一个调用的函数，就是首先就是在检测是否存在调试器，通过getpid和getppid查找自己的pid和父进程的pid进行比较，来判断是否被调试。（这里可以通过attach绕过）

之后是decode_output，这题为了防止直接查找字符串找到关键信息，将关键信息全部做了编码。输出是需要自行解码。接下来就是输入、求输入的长度、encode、比较。而我们重点分析的地方是encode函数。

[![](https://p3.ssl.qhimg.com/t0145796e1ce2a68cfc.png)](https://p3.ssl.qhimg.com/t0145796e1ce2a68cfc.png)

可以看到这个函数大致看一下其实挺像base64，但table不同，所以猜测可能是base算法，但是是魔改的。静态分析时候可以看到table是`01234567!`。但如果用这个table，那必不可能过check啊。于是动态调试了一下，发现在一个不起眼的地方，table被改成了`0xDktbNB!`。这下就好办了。

接下来就是说算法，其实这个算法很简单，和各base算法一样的原理，转ascii，按照二进制截取三位，查表。或许可以叫base8?不知道，2333

算法和table都知道了，写解密算法就很容易了。

```
# -*- coding: utf-8 -*-
cip = 'Dx0t0bDkD0NbDx0NkNNbktNkkk0txtN0kkDkxbkBxbNNBbkBDx0kDxNkD0NbDx0Nx0DBNt00'
key = '0xDktbNB'
index = []
for i in cip:
    for j in range(len(key)):
        if i == key[j]:
            index.append(j)
text = []
for i in index:
    text.append((bin(i)[2:]).zfill(3))
f = []
for i in range(0,len(text),8):
    j = 0
    tmp = ''
    while j &lt;= 7:
        tmp += text[i+j]
        j += 1
    f.append(tmp)
flag = ''
for i in range(len(f)):
    flag += hex(int(f[i],2))[2:].decode('hex')
print flag
```



# <a class="reference-link" name="hide_and_seek"></a>hide_and_seek

这次是Windows下的。可以在export这里看到TLS，而TLS是在main函数之前执行的。可能会存在一些反调试之类的东西。

[![](https://p4.ssl.qhimg.com/t015af1e4d0fb6be452.png)](https://p4.ssl.qhimg.com/t015af1e4d0fb6be452.png)

如果有反调试的话，可以从导入表中找是否有IsDebuggerPresent这个函数，这次还真有。查看调用的地方。

[![](https://p3.ssl.qhimg.com/t0172f7e457e14ff9ef.png)](https://p3.ssl.qhimg.com/t0172f7e457e14ff9ef.png)

也是加了花指令，和上个题目的一样，用脚本去掉。然后看下伪代码。（可能分析伪代码时候会出现call analysis all的问题，只需要进对应的地址进子函数中把子函数中的代码转换成伪代码，再出来就不会报错了）

[![](https://p2.ssl.qhimg.com/t01ea2035925a6bf59a.png)](https://p2.ssl.qhimg.com/t01ea2035925a6bf59a.png)

前边的逻辑大致好看一些，就是解密输出字符串，输入，判断flag格式和长度。但后边这段就不大好分析，中间也不难分析就是取前八位进行了一个运算，然后做比较。

[![](https://p5.ssl.qhimg.com/t01f7410e9806dcce2c.png)](https://p5.ssl.qhimg.com/t01f7410e9806dcce2c.png)

而在sub_474370函数里边，感觉就有些混乱，而且这里貌似还有一个处理异常的反调试（我tcl没弄明白Orz）不过问题不大，可以跳过，但是跳过的同时也跳过了加密的具体过程，好在发现sub_474370之后的sub_471ab0是check函数，两个参数分别位自己输入后的加密和密文。

[![](https://p4.ssl.qhimg.com/t012f64c3f4b2323936.png)](https://p4.ssl.qhimg.com/t012f64c3f4b2323936.png)

那么这时候就只能猜算法了，多次测试发现，每一位不会影响下一位，且小幅度变化输入对密文的影响也不大，也没发现很长的代码。就猜测是+-^等运算，经测试发现为xor运算，可以通过输入把xor的key套出来，之后xor密文得到flag。

```
# -*- coding: utf-8 -*-
cip1 = [0x12,0xFE,0xCB,0x94,0x61,0x3D,0x06,0xE3,0xBF,0x88,0x55,0x31,0x01,0xD7,0xA0,0x7C,0x49,0x30,0xFE,0xAD,0x58,0x07,0xC2,0x71,0x2F,0xEA,0x99,0x44,0x01,0xC1,0x6C,0x1B,0xD6,0x85,0x12,0xFE]
key1 = [1]*36
cipher = [0x75,0x93,0xAB,0xF2,0x1B,0x54,0x36,0x86,0x8D,0xD6,0x35,0x5E,0x64,0x89,0xD2,0x4E,0x7B,0x5A,0xA0,0xEB,0x0A,0x59,0xA5,0x41,0x40,0x8F,0xC7,0x31,0x68,0xF3,0x32,0x77,0xB6,0xB5,0x7D,0x82]
flag = ''
for i in range(len(cipher)):
    flag += chr(cip1[i]^key1[i]^cipher[i])
print flag
```



## STABLE_TRICK

这题也发现了TLS，但是找了半天没发现有什么奇怪的地方。main函数逻辑也很简单。

[![](https://p5.ssl.qhimg.com/t014b049f2228c8cd33.png)](https://p5.ssl.qhimg.com/t014b049f2228c8cd33.png)

那就先逆逆main函数再说吧。需要关注的函数就是图中注释的三个，先看一下第一个xor的函数。

[![](https://p2.ssl.qhimg.com/t0124c7c93689f4913b.png)](https://p2.ssl.qhimg.com/t0124c7c93689f4913b.png)

基本是异或生成的，所以基本可以认定flag的长度为20位。

第二个函数

[![](https://p2.ssl.qhimg.com/t01c5fa8f1768d1b2dd.png)](https://p2.ssl.qhimg.com/t01c5fa8f1768d1b2dd.png)

后四位给出像是一种提示。

第三个函数

[![](https://p1.ssl.qhimg.com/t0199e3e8685a948a03.png)](https://p1.ssl.qhimg.com/t0199e3e8685a948a03.png)

又是这个表达式。但其实在这里没什么用，真正的加密是在sub_401850中，其他都是用来迷惑的。

[![](https://p3.ssl.qhimg.com/t018d9e7339adb5bc4d.png)](https://p3.ssl.qhimg.com/t018d9e7339adb5bc4d.png)

而在sub_401850中，经历了一系列的加和xor，还有矩阵行列变换进行了加密，感觉不像是一种现有的加密算法，由之前的16位数据、4位已知key和刚才没有注意的0xFFBEADDE生成了十六位数据并进行base64。于是我大致了解了逻辑之后，开始还原加密算法并写出解密算法。这里就可以直接看代码了，不用多说。

```
# -*- coding: utf-8 -*-
input_num = [0x9A,0xCE,0xFD,0x07, \
        0x01,0x0E,0x0C,0x02, \
        0x0C,0x0D,0x24,0x2A, \
        0x24,0x26,0x24,0x22 \
        ]
def encrypt(input_num):
    sum = []
    for i in range(0,len(input_num),4):
        sum.append((input_num[i+3]&lt;&lt;24)+(input_num[i+2]&lt;&lt;16)+(input_num[i+1]&lt;&lt;8)+input_num[i])

    for k in range(1):
        tmp = k%3
        if tmp == 0:
            sum[0] = sum[0]^0x6560773b
            sum[1] = sum[1]^0xffbeadde

            sum[0],sum[2] = sum[2],sum[0]
            sum[1],sum[3] = sum[3],sum[1]

        if tmp&lt;=1:
            sum[0] = sum[0]^0x6560773b
            sum[1] = sum[1]^0xffbeadde

            tmp_num = []
            for i in range(len(sum)):
                tmp_num.append(sum[i]&amp;0xff)
                tmp_num.append((sum[i]&gt;&gt;8)&amp;0xff)
                tmp_num.append((sum[i]&gt;&gt;16)&amp;0xff)
                tmp_num.append((sum[i]&gt;&gt;24)&amp;0xff)

            input_num = []
            for i in range(0,4):
                for j in range(0,4):
                    input_num.append(tmp_num[i+4*j])
            flag = 0
            flag = (sum[0]+0x6560773b)/0x100000000
            sum[0] = (sum[0]+0x6560773b)&amp;0xffffffff
            sum[1] = (sum[1]+0xffbeadde+flag)&amp;0xffffffff

            sum[0],sum[2] = sum[2],sum[0]
            sum[1],sum[3] = sum[3],sum[1]

        if tmp &lt;= 2:
            flag = 0
            flag = (sum[0]+0x6560773b)/0x100000000
            sum[0] = (sum[0]+0x6560773b)&amp;0xffffffff
            sum[1] = (sum[1]+0xffbeadde+flag)&amp;0xffffffff

            sum[0],sum[2] = sum[2],sum[0]
            sum[1],sum[3] = sum[3],sum[1]

    for i in range(len(input_num)):
        print hex(input_num[i])
def decrypt(cip_num):
    #cip_num = [0xd8,0x78,0x7c,0xfa,0xb2,0x2c,0xe8,0xf4,0x41,0xee,0x12,0x93,0x6,0xe2,0xa2,0x2]
    tmp_num = []

    sum = []
    # 63
    for i in range(0,4):
        for j in range(0,4):
            tmp_num.append(cip_num[i+4*j])
    for i in range(0,len(tmp_num),4):
        sum.append((tmp_num[i+3]&lt;&lt;24)+(tmp_num[i+2]&lt;&lt;16)+(tmp_num[i+1]&lt;&lt;8)+tmp_num[i])

    sum[0] = sum[0]^0x6560773b
    sum[1] = sum[1]^0xffbeadde
    sum[0],sum[2] = sum[2],sum[0]
    sum[1],sum[3] = sum[3],sum[1]
    sum[0] = sum[0]^0x6560773b
    sum[1] = sum[1]^0xffbeadde
    # 62
    for k in range(62,-1,-1):
        tmp = k%3
        if tmp &lt;= 2:
            sum[0],sum[2] = sum[2],sum[0]
            sum[1],sum[3] = sum[3],sum[1]

            flag = 0
            sum[0] = (sum[0]-0x6560773b)&amp;0xffffffff
            flag = (sum[0]+0x6560773b)/0x100000000
            sum[1] = (sum[1]-flag-0xffbeadde)&amp;0xffffffff

        if tmp &lt;= 1:
            sum[0],sum[2] = sum[2],sum[0]
            sum[1],sum[3] = sum[3],sum[1]

            flag = 0
            sum[0] = (sum[0]-0x6560773b)&amp;0xffffffff
            flag = (sum[0]+0x6560773b)/0x100000000
            sum[1] = (sum[1]-flag-0xffbeadde)&amp;0xffffffff

            tmp_num = []
            for i in range(len(sum)):
                tmp_num.append(sum[i]&amp;0xff)
                tmp_num.append((sum[i]&gt;&gt;8)&amp;0xff)
                tmp_num.append((sum[i]&gt;&gt;16)&amp;0xff)
                tmp_num.append((sum[i]&gt;&gt;24)&amp;0xff)

            cip_num = []
            for i in range(0,4):
                for j in range(0,4):
                    cip_num.append(tmp_num[i+4*j])

            sum[0] = sum[0]^0x6560773b
            sum[1] = sum[1]^0xffbeadde

        if tmp == 0:
            sum[0],sum[2] = sum[2],sum[0]
            sum[1],sum[3] = sum[3],sum[1]

            sum[0] = sum[0]^0x6560773b
            sum[1] = sum[1]^0xffbeadde

    data = []
    for i in range(len(sum)):
        data.append(sum[i]&amp;0xff)
        data.append((sum[i]&gt;&gt;8)&amp;0xff)
        data.append((sum[i]&gt;&gt;16)&amp;0xff)
        data.append((sum[i]&gt;&gt;24)&amp;0xff)
    data += [0x65,0x60,0x77,0x3b]
    xor_decry(data)
def xor_decry(data):
    flag = ''
    flag += chr(data[0]^0xab)
    flag += chr(data[0]^data[1]^0x66)
    tmp = data[1]
    for i in range(2,5):
        t = data[i]
        data[i] ^= tmp
        flag += chr(data[i])
        tmp ^= t
    for i in range(5,10):
        t = data[i]
        data[i] ^= tmp^0xd
        flag += chr(data[i])
        tmp ^= t ^ 0xd
    for i in range(10,20):
        t = data[i]
        data[i] ^= tmp ^ 0x25
        flag += chr(data[i])
        tmp ^= t^0x25
    print flag
if __name__ == '__main__':
    #encrypt(input_num)
    cip_num = [0xae,0xd9,0xa1,0x50,0x7a,0xe1,0xf8,0xe3,0x43,0x83,0xb0,0xb0,0x17,0x9f,0xcd,0x30]
    decrypt(cip_num)
```



## 总结

其实这次月赛的题目质量还是可以的，不至于太水也不会说太难，适合我这样的菜鸡做。每次都是赛后复盘DAS月赛，有机会一定要打一次（下次一定下次一定）

> 原文链接: https://www.anquanke.com//post/id/240024 


# RCTF2018 magic详解


                                阅读量   
                                **567280**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t0158bf477f481a71a5.jpg)](https://p0.ssl.qhimg.com/t0158bf477f481a71a5.jpg)



最近做到了这道题，感觉这题挺复杂的，做了好长时间，网上的wp也不多，看的也一知半解，今天记录下自己的解题过程和感悟<br>
!!!希望读者在复现时跟着我的步骤动调跟进，以免漏过一些重要的步骤

## 本题考点

1.使用时间戳作为随机种子生成随机数<br>
2.暴力破解时间种子（调用程序原本的函数）<br>
3.onexit函数对地址回调<br>
4.rc4加解密<br>
5.vm (头疼)

首先拖入ida<br>
观察main函数

[![](https://p0.ssl.qhimg.com/t018bd93be6f18d5938.png)](https://p0.ssl.qhimg.com/t018bd93be6f18d5938.png)

发现只有在一定时间内打开才可以<br>
下断点调试，发现在main函数执行之前就输出了语句，所以main函数并不是真正的main，我们需要找到真正的main函数，首先反回上级函数，观察发现可疑函数

[![](https://p4.ssl.qhimg.com/t01c411b94a324f69aa.png)](https://p4.ssl.qhimg.com/t01c411b94a324f69aa.png)

动态后发现确实是，跟进，发现这里调用了两个关键函数（下面有用）

[![](https://p1.ssl.qhimg.com/t014b6057ddaf68ac4d.png)](https://p1.ssl.qhimg.com/t014b6057ddaf68ac4d.png)

[![](https://p3.ssl.qhimg.com/t01b9edcc1b16dca01a.png)](https://p3.ssl.qhimg.com/t01b9edcc1b16dca01a.png)

首先观察调用的第一个函数<br>
在这个函数中发现，如果dword_4099D0为0那么就会错误

[![](https://p2.ssl.qhimg.com/t01b9428762523f0db4.png)](https://p2.ssl.qhimg.com/t01b9428762523f0db4.png)

dword_4099D0的修改在sub_402268函数中

[![](https://p1.ssl.qhimg.com/t01e0515ef53263e49b.png)](https://p1.ssl.qhimg.com/t01e0515ef53263e49b.png)



## 时间戳生成随机数

这里使用时间戳生成随机数，然后对一个数组做异或，将异或后的数据经过一系列操作后生成一个数据，这个数据要等于1792，否则会将dword_4099D0置零，也就是失败



## 暴力破解时间种子（调用程序原本的函数）

先讲一下本人的方法（可以跳过），观察sub_4027ed函数，发现并不算太长，将逻辑复现为c语言代码，然后进行爆破，此方法工作量大且不适合大型函数

下面讲解大佬的方法<br>
首先本题是windows程序，所以我们可以使用loadlibrary函数调用源程序里的函数来进行爆破，这种方法工作量小，且不容易出错<br>
下面给出调用的代码,<br>
！！！！注意，因为程序是64位，所以在编译时请选用x64模式<br>
！！！！注意，因为程序是64位，所以在编译时请选用x64模式<br>
！！！！注意，因为程序是64位，所以在编译时请选用x64模式

```
#include &lt;iostream&gt;
#include&lt;stdio.h&gt;
#include&lt;windows.h&gt;
using namespace std;

typedef unsigned int(*test)();
static UINT time = 0x5AFFE78F + 1;
UINT myfun(int) `{` //通过这种形式遍历每一个time
    return time++;
`}`
char e1_copy[256] = `{` 0 `}`;
int main()
`{`
    UINT64* ptr1 = (UINT64*)0x40A38C;//time64
    UINT64* ptr2 = (UINT64*)0x40A414; //srand
    UINT64* ptr3 = (UINT64*)0x40A3FC;//rand
    UINT64* ptr4 = (UINT64*)0x40A3DC;//memset
    HMODULE h = LoadLibraryA("D:\\magic.exe");
    memcpy(e1_copy, (void*)0x405020, 256); //备份E1表，重新运算的时候需要还原E1表
    test test1 = (test)0x402268;
    *ptr1 = (UINT64)myfun;
    *ptr2 = (UINT64)srand;
    *ptr3 = (UINT64)rand;
    *ptr4 = (UINT64)memset;
    UINT val;
    while (true)
    `{`
        memcpy((void*)0x405020, e1_copy, 256); // 重置E1表
        val = test1();
        if (val != 0)
        `{`
            printf("time:%x\nkey:%x", time - 1, val); //0x322ce7a4
            //time:5b00e398
            //key: 322ce7a4
            break;
        `}`
    `}`
    return 0;
`}`
```

爆破后得到时间为0x5b00e398



## onexit函数对地址回调

还记得上面我们调用了两个函数吗？第一个函数是时间验证，第二个函数则是下面的关键

[![](https://p3.ssl.qhimg.com/t0160d20ab46e555575.png)](https://p3.ssl.qhimg.com/t0160d20ab46e555575.png)

这里是这题的精髓，观察发现这里使用了onexit函数，在msdn上查看onexit函数的作用

[![](https://p1.ssl.qhimg.com/t011f9ec752bdfd3fe7.png)](https://p1.ssl.qhimg.com/t011f9ec752bdfd3fe7.png)

这里注册了程序在退出时的回调地址，动态调试可以发现函数在执行时间验证后会继续执行完main函数，而在main函数执行完毕后会有一个exit

[![](https://p1.ssl.qhimg.com/t01299b5efe2642cd10.png)](https://p1.ssl.qhimg.com/t01299b5efe2642cd10.png)

我们跟进后发现执行完exit后程序并没有结束，而是跳转到了sub_403260函数，也就是上面通过onexit函数注册的回调函数<br>
这就是onexit函数的作用，在linux下也有同样作用的函数atexit



## rc4加解密

紧跟上面，继续执行程序，发现程序进入到了sub_4023B1函数

[![](https://p0.ssl.qhimg.com/t010cc269183033e882.png)](https://p0.ssl.qhimg.com/t010cc269183033e882.png)

这里要求我们输入一个字符串，然后对输入进行rc4加密，再把输入传递给vm函数执行



## vm

接下来到了最令人头痛的vm时间了，老实说每次vm都会占用大量的解题时间，所以解决vm一定要养成将opcode转换为对应的指令和寄存器，这样可以省去大量的时间，通过动调加静态分析逆向出vm逻辑，使用z3解一下，然后在对其进行rc4的解密就可以了，注意vm里面注册了一个异常，除以0会抛出异常，异常接收函数会处理异常

[![](https://p5.ssl.qhimg.com/t01afd646739f2c6e7d.png)](https://p5.ssl.qhimg.com/t01afd646739f2c6e7d.png)

[![](https://p4.ssl.qhimg.com/t01ece15cec4b8b4213.png)](https://p4.ssl.qhimg.com/t01ece15cec4b8b4213.png)

```
from z3 import *
s = Solver()
user_in = [BitVec('a%d' % i,8) for i in range(0x1A)]
re = [0x89, 0xC1, 0xEC, 0x50, 0x97, 0x3A, 0x57, 0x59, 0xE4, 0xE6, 0xE4, 0x42, 0xCB, 0xD9, 0x08, 0x22, 0xAE, 0x9D, 0x7C, 0x07, 0x80, 0x8F, 0x1B, 0x45, 0x04, 0xE8, 0x00, 0x00, 0x00, 0x00]
tmp = 0x66
for i in range(0x1A):
        s.add(((user_in[i] + 0xCC) &amp; 0xff) ^ tmp == re[i])
        tmp = (~tmp) &amp; 0xff
flag=[]
if s.check() == sat:
    m = s.model()
    for i in range(26):
        flag.append(m[user_in[i]])
print(flag)

f=[35, 140, 190, 253, 37, 215, 101, 244, 182, 179, 182, 15, 225, 116, 162, 239, 252, 56, 78, 210, 26, 74, 177, 16, 150, 165]
key=[0xA4,0xE7,0x2C,0x32]

s=[0]*256
k=[0]*256
for i in range(256):
        s[i]=i
        k[i]=key[i%len(key)]

v6=0
v5=0
for i in range(256):
        v6=(s[i]+v6+k[i])%256
        v5=s[i]
        s[i]=s[v6]
        s[v6]=v5
v7=0
v6=0
for i in range(len(flag)):
        v7=(v7+1)%256
        v6=(v6+s[v7])%256
        v4=s[v7]
        s[v7]=s[v6]
        s[v6]=v4
        f[i]^=s[(s[v6]+s[v7])%256]

print(''.join(chr(x) for x in f))
```

输出为[@ck_For_fun_02508iO2_2iOR](https://github.com/ck_For_fun_02508iO2_2iOR)`}`<br>
再加上”rctf`{`“就是Flag了



## 总结

这题主要是采用了虚假的main函数，要找到真正的main函数，然后再通过调用程序本身的函数爆破时间，再通过onexit函数注册退出返回地址，在把输入做rc4加密传给vm函数，vm函数里注册了一个异常。这就是这题的主要流程，感觉学到了挺多的，希望读者在阅读文章时尽量跟着动调摸清整个流程。

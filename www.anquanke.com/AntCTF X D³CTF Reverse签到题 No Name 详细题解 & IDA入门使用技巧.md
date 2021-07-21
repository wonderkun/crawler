> 原文链接: https://www.anquanke.com//post/id/233733 


# AntCTF X D³CTF Reverse签到题 No Name 详细题解 &amp; IDA入门使用技巧


                                阅读量   
                                **238827**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t012f1a72d34f7f3e6d.jpg)](https://p5.ssl.qhimg.com/t012f1a72d34f7f3e6d.jpg)



## JEB分析文件

apk文件拖入JEB进行分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015f4672078dc4d43f.png)

发现程序调用了checkFlag函数对flag进行检验

[![](https://p2.ssl.qhimg.com/t01cc4f1d51f46f2224.png)](https://p2.ssl.qhimg.com/t01cc4f1d51f46f2224.png)

发现check函数是一个native函数，所以去so文件里面寻找对应的函数



## FlagChecker_check Native函数分析

在IDA中搜索check函数，可以搜索到一个

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0113cc32d1c5a1e259.png)

发现了check函数

### <a class="reference-link" name="%E8%BF%98%E5%8E%9F%E5%8F%82%E6%95%B0%E7%B1%BB%E5%9E%8B"></a>还原参数类型

找到函数后，我们要先把第一个参数变量类型设置成**JNIEnv ***

[![](https://p5.ssl.qhimg.com/t0195b4610e1cfa4180.png)](https://p5.ssl.qhimg.com/t0195b4610e1cfa4180.png)

这样的话对于识别一些函数会方便很多，在分析so文件的时候都推荐这样来做

### <a class="reference-link" name="%E5%9F%BA%E6%9C%AC%E6%A1%86%E6%9E%B6%E5%88%86%E6%9E%90"></a>基本框架分析

修改之后再观察代码信息

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016d0aabbb6d8a2e20.png)

发现这个函数从输入中获取信息，并把长度信息保存在v6[0]的位置，传入**sub_D478**函数进行解密，解密后的内容使用**memcmp**进行比对。**这是一种比较常见的情况，告诉你函数操作结束后的内容，要求你逆向出函数操作来得到输入信息**

### 分析**sub_D478**函数

[![](https://p3.ssl.qhimg.com/t019df65cb7abf0ca3e.png)](https://p3.ssl.qhimg.com/t019df65cb7abf0ca3e.png)

一眼可以看出是一个变种的TEA的**解密函数**，运算轮数为16轮，所以sum的值从**0xE3779B90**开始

**<a class="reference-link" name="%E4%BD%BF%E7%94%A8Invert%20sign%E5%BF%AB%E9%80%9F%E8%AF%86%E5%88%AB%E5%B8%B8%E9%87%8F"></a>使用Invert sign快速识别常量**

对于**0x61C88647**这个常量，如果你做题做的不够多，可能一眼看不出来这个就是**0x9E3779B9**的补码

这个时候就可以尝试在数据上右键，**Invert sign**一下再看看数据

[![](https://p4.ssl.qhimg.com/t0125fa836e2d17345a.png)](https://p4.ssl.qhimg.com/t0125fa836e2d17345a.png)

转换之后就可以看到熟悉的**TEA常数**了（可以借助百度来快速的分析算法）

**<a class="reference-link" name="%E7%BC%96%E5%86%99TEA%E8%A7%A3%E5%AF%86%E4%BB%A3%E7%A0%81%E5%B9%B6%E8%A7%A3%E5%AF%86"></a>编写TEA解密代码并解密**

```
void tea_decrypt(uint32_t* v, int len)
`{`
    for (int idx = 0; idx &lt; len &gt;&gt; 2; idx += 2)
    `{`
        uint32_t v0 = v[idx], v1 = v[idx + 1], sum = 0xE3779B90, i;
        uint32_t delta = 0x9e3779b9;
        _DWORD v12[4];
        memcpy(v12, "com.d3ctf.noname", 16LL);
        for (int j = 0; j &lt; 0x10; ++j)
        `{`
            v1 -= (((16 * v0) ^ (v0 &gt;&gt; 5)) + v0) ^ (sum + v12[(sum &gt;&gt; 11) &amp; 3]);
            sum -= delta;
            v0 -= (((16 * v1) ^ (v1 &gt;&gt; 5)) + v1) ^ (sum + v12[sum &amp; 3]);
        `}`
        v[idx] = v0;
        v[idx + 1] = v1;
    `}`
`}`
void tea_encrypt(uint32_t* v, int len)
`{`
    for (int idx = 0; idx &lt; len &gt;&gt; 2; idx += 2)
    `{`
        uint32_t v0 = v[idx], v1 = v[idx + 1], sum = 0, i;
        uint32_t delta = 0x9e3779b9;
        _DWORD v12[4];
        memcpy(v12, "com.d3ctf.noname", 16LL);
        for (i = 0; i &lt; 16; i++)
        `{`
            v0 += (((v1 &lt;&lt; 4) ^ (v1 &gt;&gt; 5)) + v1) ^ (sum + v12[sum &amp; 3]);
            sum += delta;
            v1 += (((v0 &lt;&lt; 4) ^ (v0 &gt;&gt; 5)) + v0) ^ (sum + v12[(sum &gt;&gt; 11) &amp; 3]);
        `}`
        v[idx] = v0;
        v[idx + 1] = v1;
    `}`
`}`
```

解密后发现

[![](https://p1.ssl.qhimg.com/t018aa628b969de1693.png)](https://p1.ssl.qhimg.com/t018aa628b969de1693.png)

可恶，居然拿了个假的flag。

**<a class="reference-link" name="%E7%96%91%E9%97%AE"></a>疑问**

根据代码逻辑来说，应该是要对最后比对的数据进行加密，编写加密函数输出的内容才是要输入的内容，但是这道题里面使用的却是用解密函数输出fake_flag，不过影响不大，因为这个反正不是真正程序执行的内容



## 重新审视文件

由于前面分析的急切，所以都没有注意到程序中其他内容，以至于分析到了错误的flag。

浪费了很多时间后，我们又回到了起点，

[![](https://p4.ssl.qhimg.com/t013755f34b6de6fd5c.png)](https://p4.ssl.qhimg.com/t013755f34b6de6fd5c.png)

发现有这么一个函数，观察发现FlagChecker类居然被替换了。

而这部分代码的逻辑是，对data.enc文件进行AES解密，秘钥信息从native函数中得到。



## NoNameApp_getAESKey Native函数分析

这里实际上可以下断点来调试程序。但是我这里由于没有实体机，且so文件只提供了amd64的格式（在模拟器上无法正常的运行），所以我这里只能静态分析。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010615eb823d9dc913.png)

发现直接返回了key的内容，所以key的数据应该在其他地方被修改调用。

同时我们知道key的长度是0x10，也正好符合AES-128的秘钥长度。

### <a class="reference-link" name="%E8%BF%98%E5%8E%9Fkey%E7%9A%84%E6%95%B0%E6%8D%AE%E7%B1%BB%E5%9E%8B"></a>还原key的数据类型

双击进入数据显示

[![](https://p3.ssl.qhimg.com/t0167489c1225a6e9ab.png)](https://p3.ssl.qhimg.com/t0167489c1225a6e9ab.png)

发现key的旁边是**%4**，我理解为IDA识别这个变量的长度，我们这里要设置成的是1字节。

在内容下按D键多次，直到显示为**%1**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bb02072c7b156697.png)

接着按下小键盘上的星号，可以定义key为数组，设置数组长度（Array size）为0x10

[![](https://p2.ssl.qhimg.com/t01cb9450b5349acd55.png)](https://p2.ssl.qhimg.com/t01cb9450b5349acd55.png)

最后就成功还原成这样了

[![](https://p0.ssl.qhimg.com/t01cfeadd067cbfed4d.png)](https://p0.ssl.qhimg.com/t01cfeadd067cbfed4d.png)

### <a class="reference-link" name="%E5%88%86%E6%9E%90key%E6%95%B0%E6%8D%AE%E5%86%85%E5%AE%B9"></a>分析key数据内容

在这个函数中，没有对key的数据内容进行任何的修改，那么只可能是在初始化的时候就生成了key的信息，我们可以从**JNI_OnLoad**开始分析，但是我这里为了方便，用一个更简单的方法快速定位

<a class="reference-link" name="%E6%9F%A5%E6%89%BE%E5%BC%95%E7%94%A8"></a>**查找引用**

在变量上按下**X 查找引用**

[![](https://p4.ssl.qhimg.com/t01572b30dce097d46e.png)](https://p4.ssl.qhimg.com/t01572b30dce097d46e.png)

发现了引用位置

[![](https://p3.ssl.qhimg.com/t0101b920e5173bb4cd.png)](https://p3.ssl.qhimg.com/t0101b920e5173bb4cd.png)

**<a class="reference-link" name="%E5%AE%9A%E4%B9%89%E5%87%BD%E6%95%B0"></a>定义函数**

发现这一块代码都是红色的，我们之间按F5没有任何的反应，这代表这一块的代码还没有被定义成函数，一般来说是IDA对于这一块代码的栈帧分析数据存在一些问题，或者IDA分析后不认为这里是个函数。

前者需要手动修改，而我们这里是后者的情况，我们只需要到函数头部按下**P键手动进行定义函数**。

定义后再按下F5，就可以看到比较舒服的伪代码了，**这得益于之前的信息还原**

[![](https://p2.ssl.qhimg.com/t010f1c17433c58b08f.png)](https://p2.ssl.qhimg.com/t010f1c17433c58b08f.png)

这一块内容对key进行运算，我们可以直接复制这一块的伪代码，以及此函数最上面的变量定义，删除一些无关紧要的变量后，补上一些文件头后，可以直接在IDE中运行。

同时在这一段伪代码中，只调用了**sub_D478**函数这一个函数，而这个函数就是我们之前所编写的TEA解密函数，所以我们直接替换即可

### 

**<a class="reference-link" name="%E5%BC%95%E5%85%A5IDA%E5%B8%B8%E7%94%A8%E5%87%BD%E6%95%B0%E5%A4%B4%E6%96%87%E4%BB%B6"></a>引入IDA常用函数头文件**

我一般使用的是vs，这里需要补充的一点是，有些在伪代码的函数定义是不存在的，这时候需要使用

```
#include "defs.h"
```

来引入头文件，这个文件在**IDA目录下的plugins文件夹**内，这个文件里面包含了伪代码中绝大多数变量类型和函数定义。

**<a class="reference-link" name="%E5%AF%BC%E5%87%BA%E7%A8%8B%E5%BA%8F%E5%B8%B8%E9%87%8F"></a>导出程序常量**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018d84db718df34c21.png)

这一行语句里面包含了一个全局变量，我们需要把这个全局变量导出，才能在我自己的代码中使用。我一般用的方法是先定义为数组，然后再用**Shift + E**导出。

[![](https://p3.ssl.qhimg.com/t01d432a6bbebcb7c6e.png)](https://p3.ssl.qhimg.com/t01d432a6bbebcb7c6e.png)

我们从之前的分析中得知前四个字节存放字符长度，所以我们只需要设置后0x10长度的数据为数组即可。

IDA只能导出unsigned char 的字节数据，对于其他类型的导出，IDA还不支持，我们只能用插件来完成这个功能，我这里使用的是**LazyIDA.py**插件。

[![](https://p0.ssl.qhimg.com/t0142e2d22c1b87ac0f.png)](https://p0.ssl.qhimg.com/t0142e2d22c1b87ac0f.png)

### <a class="reference-link" name="%E6%89%A7%E8%A1%8C%E7%A8%8B%E5%BA%8F%E5%BE%97%E5%88%B0AES-KEY"></a>执行程序得到AES-KEY

在上述操作后，我们可以编写代码并且成功执行。

在比赛的时候时间是比较宝贵的，所以使用VS下断点来直接的观察程序内存数据不妨为一个好方法

[![](https://p0.ssl.qhimg.com/t01f6cbfe2c51ef57cb.png)](https://p0.ssl.qhimg.com/t01f6cbfe2c51ef57cb.png)

可以通过vs自带的内存查看，在地址栏中输入key就会跳转到对应位置。

**<a class="reference-link" name="%E5%9D%91%E7%82%B9"></a>坑点**

这里刚开始算出来的key一直都是错误的，在之后才发现原来这个常量数组在其他地方被修改了，导致无法计算出正确值。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012a803999fe9410be.png)



## 解密数据

得到key之后，我们就可以用python直接解密文件

```
import binascii
from Crypto.Cipher import AES
key = binascii.unhexlify("bbbc3bef42b068f57a90078cc03f797b")
aes = AES.new(key, mode=AES.MODE_ECB)
with open("data.enc", "rb") as fp:
    with open("data.jar", "wb") as f:
        f.write(aes.decrypt(fp.read()))
```



## 分析替换后的JAR文件

解密后再用JEB打开文件，发现了程序的真实执行代码

[![](https://p4.ssl.qhimg.com/t0127f10193425f3055.png)](https://p4.ssl.qhimg.com/t0127f10193425f3055.png)

比较简单的异或比对，编写程序并进行解密输出。



## 解题程序

```
#include &lt;cstdio&gt;
#include &lt;cstring&gt;
#include &lt;cstdint&gt;
#include &lt;cstdlib&gt;
#include "defs.h"
unsigned int data[9] = `{`
0x4A35EBB6, 0x6674F329, 0x4A8AAD73, 0xB5335406, 0x7F668F12, 0x8A966EF7, 0xE7E8807F,
0xC0F604E0, 0x61630000
`}`;
unsigned char ida_chars[] =
`{`
0x07, 0x00, 0x00, 0x00, 0x0C, 0x00, 0x00, 0x00, 0x11, 0x00,
0x00, 0x00, 0x16, 0x00, 0x00, 0x00, 0x07, 0x00, 0x00, 0x00,
0x0C, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00, 0x16, 0x00,
0x00, 0x00, 0x07, 0x00, 0x00, 0x00, 0x0C, 0x00, 0x00, 0x00,
0x11, 0x00, 0x00, 0x00, 0x16, 0x00, 0x00, 0x00, 0x07, 0x00,
0x00, 0x00, 0x0C, 0x00, 0x00, 0x00, 0x11, 0x00, 0x00, 0x00,
0x16, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x09, 0x00,
0x00, 0x00, 0x0E, 0x00, 0x00, 0x00, 0x14, 0x00, 0x00, 0x00,
0x05, 0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x00, 0x0E, 0x00,
0x00, 0x00, 0x14, 0x00, 0x00, 0x00, 0x05, 0x00, 0x00, 0x00,
0x09, 0x00, 0x00, 0x00, 0x0E, 0x00, 0x00, 0x00, 0x14, 0x00,
0x00, 0x00, 0x05, 0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0x00,
0x0E, 0x00, 0x00, 0x00, 0x14, 0x00, 0x00, 0x00, 0x04, 0x00,
0x00, 0x00, 0x0B, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00,
0x17, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00, 0x0B, 0x00,
0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x17, 0x00, 0x00, 0x00,
0x04, 0x00, 0x00, 0x00, 0x0B, 0x00, 0x00, 0x00, 0x10, 0x00,
0x00, 0x00, 0x17, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00, 0x00,
0x0B, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x17, 0x00,
0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x00, 0x00,
0x0F, 0x00, 0x00, 0x00, 0x15, 0x00, 0x00, 0x00, 0x06, 0x00,
0x00, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x0F, 0x00, 0x00, 0x00,
0x15, 0x00, 0x00, 0x00, 0x06, 0x00, 0x00, 0x00, 0x0A, 0x00,
0x00, 0x00, 0x0F, 0x00, 0x00, 0x00, 0x15, 0x00, 0x00, 0x00,
0x06, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x0F, 0x00,
0x00, 0x00, 0x15, 0x00, 0x00, 0x00
`}`;
int dword_34000[64] = `{`
0xD76AB478, 0xE8C7B756, 0x242070DB, 0xC1BDCEEE, 0xF57C1FAF, 0x4787C62A, 0xA8304613, 0xFD469501,
0x6980D8D8, 0x8B44F4AF, 0xFFFF5BB1, 0x895CD7BE, 0x6B901122, 0xFD987193, 0xA679438E, 0x49B40821,
0xF61E2562, 0xC040BD40, 0x265E5A51, 0xE9B6C7AA, 0xD62F105D, 0x02441453, 0xD8A1E681, 0xE7D3FBC8,
0x21E1CDE6, 0xC33701D6, 0xF4D50D87, 0x455A14ED, 0xA9E3E905, 0xFCEFA7F8, 0x676F02D9, 0x8D2A4C8A,
0xFFFA3942, 0x8771F681, 0x6D9D6122, 0xFDE5380C, 0xA4BEEA44, 0x4BDECFA9, 0x46BB4B60, 0xBEBFBC70,
0x289B7EC6, 0xEAA127FA, 0xD4EF3085, 0x04881D05, 0xD9D4D039, 0xE6DB99E5, 0x1FA27CF8, 0xC4AC5665,
0xF4292244, 0x432AFF97, 0xAB9423A7, 0xFC93A039, 0x655B59C3, 0x8F0CCC92, 0xFFEFF47D, 0x85845DD1,
0x6FA87E4F, 0xFE2CE6E0, 0xA3014314, 0x4E0811A1, 0xF7537E82, 0xBD3AF235, 0x2AD7D2BB, 0xEB86D391
`}`;
char key[16];

void tea_decrypt(uint32_t* v, int len)
`{`
for (int idx = 0; idx &lt; len &gt;&gt; 2; idx += 2)
`{`
uint32_t v0 = v[idx], v1 = v[idx + 1], sum = 0xE3779B90, i;
uint32_t delta = 0x9e3779b9;
_DWORD v12[4];
memcpy(v12, "com.d3ctf.noname", 16LL);
for (int j = 0; j &lt; 0x10; ++j)
`{`
v1 -= (((16 * v0) ^ (v0 &gt;&gt; 5)) + v0) ^ (sum + v12[(sum &gt;&gt; 11) &amp; 3]);
sum -= delta;
v0 -= (((16 * v1) ^ (v1 &gt;&gt; 5)) + v1) ^ (sum + v12[sum &amp; 3]);
`}`
v[idx] = v0;
v[idx + 1] = v1;
`}`
`}`
void tea_encrypt(uint32_t* v, int len)
`{`
for (int idx = 0; idx &lt; len &gt;&gt; 2; idx += 2)
`{`
uint32_t v0 = v[idx], v1 = v[idx + 1], sum = 0, i;
uint32_t delta = 0x9e3779b9;
_DWORD v12[4];
memcpy(v12, "com.d3ctf.noname", 16LL);
for (i = 0; i &lt; 16; i++)
`{`
v0 += (((v1 &lt;&lt; 4) ^ (v1 &gt;&gt; 5)) + v1) ^ (sum + v12[sum &amp; 3]);
sum += delta;
v1 += (((v0 &lt;&lt; 4) ^ (v0 &gt;&gt; 5)) + v0) ^ (sum + v12[(sum &gt;&gt; 11) &amp; 3]);
`}`
v[idx] = v0;
v[idx + 1] = v1;
`}`
`}`
void getAESkey()
`{`
__int64 v1; // x28
__int64 v2; // x30
const char* v3; // x0
int v4; // w9
const char* v5; // x0
__int64 v6; // x0
const char* v7; // x0
const char* v8; // x0
char* v9; // [xsp+0h] [xbp-540h]
char* v10; // [xsp+8h] [xbp-538h]
int i; // [xsp+40h] [xbp-500h]
unsigned int v12; // [xsp+44h] [xbp-4FCh]
char v13; // [xsp+57h] [xbp-4E9h]
void* handle; // [xsp+60h] [xbp-4E0h]
void(__fastcall * v15)(__int64); // [xsp+68h] [xbp-4D8h]
char* name; // [xsp+70h] [xbp-4D0h]
char* file; // [xsp+78h] [xbp-4C8h]
int v18; // [xsp+80h] [xbp-4C0h]
unsigned int v19; // [xsp+84h] [xbp-4BCh]
int v20; // [xsp+88h] [xbp-4B8h]
unsigned int k; // [xsp+8Ch] [xbp-4B4h]
int v22; // [xsp+90h] [xbp-4B0h]
int v23; // [xsp+94h] [xbp-4ACh]
int v24; // [xsp+98h] [xbp-4A8h]
int v25; // [xsp+9Ch] [xbp-4A4h]
int j; // [xsp+ACh] [xbp-494h]
int v27; // [xsp+B0h] [xbp-490h] BYREF
int v28; // [xsp+B4h] [xbp-48Ch]
_DWORD dest[64]; // [xsp+B8h] [xbp-488h] BYREF
char* v30; // [xsp+1B8h] [xbp-388h]
__int64 v31; // [xsp+1C0h] [xbp-380h]
char* v32; // [xsp+1C8h] [xbp-378h]
__int64 v33; // [xsp+1D0h] [xbp-370h]
__int64 v34; // [xsp+1D8h] [xbp-368h]
char* v35; // [xsp+1E0h] [xbp-360h]
__int64 v36; // [xsp+1E8h] [xbp-358h]
char* v37; // [xsp+1F0h] [xbp-350h]
char* v38; // [xsp+1F8h] [xbp-348h]
__int64 v39; // [xsp+200h] [xbp-340h]
__int64 v40; // [xsp+208h] [xbp-338h]
int* v41; // [xsp+210h] [xbp-330h]
__int64 v42; // [xsp+218h] [xbp-328h]
char* v43; // [xsp+220h] [xbp-320h]
char* v44; // [xsp+228h] [xbp-318h]
__int64 v45; // [xsp+230h] [xbp-310h]
__int64* v46; // [xsp+240h] [xbp-300h]
__int64 v47; // [xsp+248h] [xbp-2F8h]
const char* v48; // [xsp+258h] [xbp-2E8h]
int v49; // [xsp+264h] [xbp-2DCh]
const char* v50; // [xsp+268h] [xbp-2D8h]
int mode; // [xsp+274h] [xbp-2CCh]
char* v52; // [xsp+278h] [xbp-2C8h]
__int64 v53; // [xsp+280h] [xbp-2C0h]
char* v54; // [xsp+288h] [xbp-2B8h]
char* v55; // [xsp+290h] [xbp-2B0h]
int* v56; // [xsp+298h] [xbp-2A8h]
unsigned __int8** v57; // [xsp+2A0h] [xbp-2A0h]
int* v59; // [xsp+2B0h] [xbp-290h]
void(__fastcall * v60)(char*); // [xsp+2B8h] [xbp-288h]
unsigned int(__fastcall * v61)(char*, _QWORD); // [xsp+2C0h] [xbp-280h]
const char* v62; // [xsp+2C8h] [xbp-278h]
const char* v63; // [xsp+2D0h] [xbp-270h]
const char* v64; // [xsp+2D8h] [xbp-268h]
char* v65; // [xsp+2E0h] [xbp-260h]
int v67; // [xsp+2FCh] [xbp-244h]
__int64 v68; // [xsp+300h] [xbp-240h]
char* v69; // [xsp+308h] [xbp-238h]
int v70; // [xsp+31Ch] [xbp-224h]
char s[256]; // [xsp+320h] [xbp-220h] BYREF
int fd; // [xsp+420h] [xbp-120h]
int v73; // [xsp+424h] [xbp-11Ch]
unsigned int v74; // [xsp+428h] [xbp-118h]
int v75; // [xsp+42Ch] [xbp-114h]
__int64 v76; // [xsp+430h] [xbp-110h]
char* v77; // [xsp+438h] [xbp-108h]
__int64 v78; // [xsp+440h] [xbp-100h]
__int64 v79; // [xsp+448h] [xbp-F8h]
__int64 v80; // [xsp+450h] [xbp-F0h]
char* v81; // [xsp+458h] [xbp-E8h]
int v82; // [xsp+464h] [xbp-DCh]
__int64 v83; // [xsp+468h] [xbp-D8h]
const char* v84; // [xsp+470h] [xbp-D0h]
char* v85; // [xsp+478h] [xbp-C8h]
const char* v86; // [xsp+480h] [xbp-C0h]
char* v87; // [xsp+488h] [xbp-B8h]
__int64 v88; // [xsp+490h] [xbp-B0h]
__int64 v89; // [xsp+498h] [xbp-A8h]
const char* v90; // [xsp+4A0h] [xbp-A0h]
__int64 v91; // [xsp+4A8h] [xbp-98h]
void* v92; // [xsp+4B0h] [xbp-90h]
void(__fastcall * v93)(__int64); // [xsp+4B8h] [xbp-88h]
const char* v94; // [xsp+4C0h] [xbp-80h]
const char* v95; // [xsp+4C8h] [xbp-78h]
void* v96; // [xsp+4D0h] [xbp-70h]
void(__fastcall * v97)(__int64); // [xsp+4D8h] [xbp-68h]
const char* v98; // [xsp+4E0h] [xbp-60h]
const char* v99; // [xsp+4E8h] [xbp-58h]
void* v100; // [xsp+4F0h] [xbp-50h]
const char* v101; // [xsp+508h] [xbp-38h]
void* v102; // [xsp+510h] [xbp-30h]
const char* v103; // [xsp+528h] [xbp-18h]
__int64 vars0; // [xsp+540h] [xbp+0h] BYREF
char data_com_d3ctf_noname[] =
`{`
0x11, 0x29, 0x08, 0x24, 0x6B, 0xD4, 0x17, 0x33, 0xB8, 0x53,
0x76, 0xA9, 0x72, 0xD4, 0x70, 0x01
`}`;
v13 = 0;
tea_decrypt((uint32_t*)&amp;data_com_d3ctf_noname, 0x10);
v32 = data_com_d3ctf_noname;
v31 = 16LL;
v30 = 0LL;
memcpy(dest, ida_chars, sizeof(dest));
*(_DWORD*)key = 0x67452301;
*(_DWORD*)&amp;key[4] = 0xEFCDAB89;
*(_DWORD*)&amp;key[8] = 0x98BADCFE;
*(_DWORD*)&amp;key[12] = 0x10325476;
v28 = (((unsigned int)((v31 + 8) / 0x40uLL) + 1) &lt;&lt; 6) - 8;
v30 = (char*)calloc((((unsigned int)((v31 + 8) / 0x40uLL) + 1) &lt;&lt; 6) + 56, 1u);
v37 = v30;
v36 = -1LL;
v35 = v32;
v34 = v31;
v33 = -1LL;
v10 = v30;
memcpy(v30, v32, v31);
v38 = v10;
v30[v31] = 0x80;
v27 = 8 * v31;
v43 = &amp;v30[v28];
v42 = -1LL;
v41 = &amp;v27;
v40 = 4LL;
v39 = -1LL;
v9 = v43;
memcpy(v43, &amp;v27, 4u);
v44 = v9;
for (j = 0; j &lt; v28; j += 64)
`{`
v25 = *(_DWORD*)key;
v24 = *(_DWORD*)&amp;key[4];
v23 = *(_DWORD*)&amp;key[8];
v22 = *(_DWORD*)&amp;key[12];
for (k = 0; k &lt; 0x40; ++k)
`{`
if (k &gt;= 0x10)
`{`
if (k &gt;= 0x20)
`{`
if (k &gt;= 0x30)
`{`
v20 = v23 ^ (v24 | ~v22);
v19 = 7 * k % 0x10;
`}`
else
`{`
v20 = v24 ^ v23 ^ v22;
v19 = (3 * k + 5) % 0x10;
`}`
`}`
else
`{`
v20 = v22 &amp; v24 | v23 &amp; ~v22;
v19 = (5 * k + 1) % 0x10;
`}`
`}`
else
`{`
v20 = v24 &amp; v23 | v22 &amp; ~v24;
v19 = k;
`}`
v18 = v22;
v22 = v23;
v23 = v24;
v24 += __ROL4__(v25 + v20 + dword_34000[k] + *(_DWORD*)&amp;v30[4 * v19 + j], dest[k]);
v25 = v18;
`}`
*(_DWORD*)key += v25;
*(_DWORD*)&amp;key[4] += v24;
*(_DWORD*)&amp;key[8] += v23;
*(_DWORD*)&amp;key[12] += v22;
`}`
`}`
int main()
`{`
unsigned char ida_chars[] =
`{`
0xB6, 0xEB, 0x35, 0x4A, 0x29, 0xF3, 0x74, 0x66, 0x73, 0xAD,
0x8A, 0x4A, 0x06, 0x54, 0x33, 0xB5, 0x12, 0x8F, 0x66, 0x7F,
0xF7, 0x6E, 0x96, 0x8A, 0x7F, 0x80, 0xE8, 0xE7, 0xE0, 0x04,
0xF6, 0xC0
`}`;
tea_decrypt((uint32_t*)ida_chars, 0x20);
printf("%s\n", ida_chars);
getAESkey();
unsigned char x[] = `{` 49, 102, 54, 33, 51, 46, 0x60, 52, 109, 97, 102, 52, 97, 55, 55, 97, 52, 0x60, 0x60, 109, 51, 101, 103, 101, 100, 98, 109, 103, 109, 54, 97, 55, 52, 98, 97, 98, 0x60, 99, 40 `}`;
for (int i = 0; i &lt; 39; i++)
`{`
printf("%c", x[i] ^ 85);
`}`
return 0;
`}`
```

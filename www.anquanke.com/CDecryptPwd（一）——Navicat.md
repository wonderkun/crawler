> 原文链接: https://www.anquanke.com//post/id/193511 


# CDecryptPwd（一）——Navicat


                                阅读量   
                                **1100525**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01b0dc4bdd77627a6b.jpg)](https://p4.ssl.qhimg.com/t01b0dc4bdd77627a6b.jpg)



## 0x00 前言

本篇是`CDecryptPwd`系列的第一篇，笔者将介绍Navicat加密过程、其使用的加密算法以及如何使用C语言来实现其加密过程，文章最后是笔者自己编写的工具(解密Navicat保存在注册表中的数据库密码)。



## 0x01 环境
- 平台：Windows 10(64 bit)
- 编译环境：Visual Studio Community 2019
- Navicat Premium 版本 12.1(64 bit)


## 0x02 Blowfish

> Navicat使用加密算法是Blowfish Cipher(河豚加密)，所以在介绍Navicat加密过程之前笔者要先介绍一下Blowfish Cipher。

### <a class="reference-link" name="0x02.0%20Introduction"></a>0x02.0 Introduction

Blowfish是一种对称密钥分组密码，Bruce Schneier在1993年设计并公布。它没有专利，任何人均可自由使用。

### <a class="reference-link" name="0x02.1%20Detail"></a>0x02.1 Detail
- 密钥长度：32-448位
- 分组长度：64位
- 16轮循环的Feistel结构
### <a class="reference-link" name="0x02.2%20Feistel%20Structure"></a>0x02.2 Feistel Structure

在介绍Blowfish之前先来搞清楚Feistel Structure(下图来自Wikipedia):

[![](https://s2.ax1x.com/2019/11/13/MJZd4e.png)](https://s2.ax1x.com/2019/11/13/MJZd4e.png)
1. 将原数据分成左右两部分
1. 原数据的右侧不变，直接变成下次循环的左侧
1. 将原数据的右侧与子密钥传递给轮函数F
1. 轮函数返回值与原数据左侧进行异或运算，变成下次循环的右侧
上述4个步骤是一轮循环的工作过程，Feistel Structure是进行了16轮循环方才完成一次加密。需要说明一点，在最后一轮循环中左右数据不对调。解密过程是加密过程的反向，具体可参照上图，不再赘述。

### <a class="reference-link" name="0x02.3%20Source%20Code"></a>0x02.3 Source Code

> 笔者分析的源码是[Paul Kocher](https://www.schneier.com/code/bfsh-koc.zip)版本，并没有使用[Bruce Schneier](https://www.schneier.com/code/bfsh-sch.zip)版本。Schneier版本中的子密钥来源是`BLOWFISH.DAT`文件，而Kocher版本是直接在源文件中定义子密钥，分析起来较为直观。如需其他版本可到[此网站](https://www.schneier.com/academic/blowfish/download.html)下载

**0x02.3-1 `BLOWFISH_CTX`**

在`blowfish.h`头文件中有如下定义：

```
typedef struct `{`
  unsigned long P[16 + 2];
  unsigned long S[4][256];
`}` BLOWFISH_CTX;
```

为结构体定义别名，结构体中的两数组即P-Box与S-Box。

**0x02.3-2 `ORIG_P[16 + 2]`与`ORIG_S[4][256]`**

`ORIG_P`与`ORIG_S`取自[圆周率的小数位](http://www.super-computing.org/pi-hexa_current.html)，每4个字节赋值给其中的一个元素。

**0x02.3-3 `void Blowfish_Init(BLOWFISH_CTX *ctx, unsigned char *key, int keyLen)`**

该函数用来初始化S-Box与P-Box。传递参数中的`key`即密钥，`keyLen`是密钥长度。
1. 对`BLOWFISH_CTX *ctx`中S-Box进行初始化，直接将`ORIG_S`中的每个元素逐一赋值给S-Box
<li>对`BLOWFISH_CTX *ctx`中P-Box进行初始化，具体过程如下：<br>
a. `data=0x00000000;`<br>
b. 如果参数中的字符数组`key`长度不足4，则循环使用`key`中字符(当使用到`key`中最后一个字符时，下一个字符是`key`中第一个字符)与`data &lt;&lt; 8`进行或运算<br>**上述过程总结起来就是将参数中的字符数组`key`转换为ASCII码形式(e.g.:`key[3]="abc"`——&gt;&gt;`0x61626361`并存储于`data`中)**<br>
c. 将`ORIG_P`中的每个元素与`data`作异或运算后逐一赋值给P-Box</li>
<li>
`datal=0x00000000;`<br>`datar=0x00000000;`
</li>
<li>将上面经过变换后的`ctx`，`datal`与`datar`传递给`Blowfish_Encrypt`
</li>
1. 将加密后的`datal`与`datar`赋值给P-Box中的元素
1. 重复9次步骤4-5
<li>与步骤4类似，不过这次传递的是上面过程中已经加密后的`datal`与`datar`
</li>
1. 将加密后的`datal`与`datar`赋值给S-Box中的元素
<li>重复512次步骤7-8<br><blockquote><p>步骤5、8中提到的赋值过程是这样的(以步骤5来举例)：<br>
第一次 `P[0]=datal`，`P[1]=datar`<br>
第二次 `P[2]=datal`，`P[3]=datar`<br>
……</p></blockquote>
</li>
**0x02.3-4 `void Blowfish_Encrypt(BLOWFISH_CTX *ctx, unsigned long *xl, unsigned long *xr)`**

该函数是Blowfish的加密部分。传递参数中的`ctx`应该已经初始化过S-Box与P-Box，`xl`指向原数据的左半部分，`xr`指向原数据的右半部分。
1. 左侧数据与P-Box中第i个元素作异或运算(i=n-1,其中n是轮数)
1. 将左侧数据与`ctx`传递给轮函数F
1. 右侧数据与轮函数F返回值作异或运算
1. 交换运算后的左右两侧数据
1. 重复16次步骤1-5
1. 将最后一轮运算互换的左右两侧数据换回来
1. 右侧数据与P-Box中第16个元素作异或运算
1. 左侧数据与P-Box中第17个元素作异或运算
上述过程即一次完整的加密过程，可参照下图来理解(来自Wikipedia，其中轮函数F的工作过程见`0x02.3-6`)：

[![](https://s2.ax1x.com/2019/11/13/MJZaND.png)](https://s2.ax1x.com/2019/11/13/MJZaND.png)

**0x02.3-5 `void Blowfish_Decrypt(BLOWFISH_CTX *ctx, unsigned long *xl, unsigned long *xr)`**

解密过程是加密过程的逆过程，如有困惑，可参照源码理解，不再赘述。

**0x02.3-6 `static unsigned long F(BLOWFISH_CTX *ctx, unsigned long x)`**

轮函数工作过程：
1. 将参数`x`逐字节分割，赋值给`a`,`b`,`c`,`d`四个变量(e.g.:`x=0x21564378`,则`a=0x21`,`b=0x56`,`c=0x43`,`d=0x78`)
1. `y = ((ctx-&gt;S[0][a] + ctx-&gt;S[1][b]) ^ ctx-&gt;S[2][c]) + ctx-&gt;S[3][d]`
1. 返回y的值
### <a class="reference-link" name="0x02.4%20Demo"></a>0x02.4 Demo

此Demo来自[Paul Kocher](https://www.schneier.com/code/bfsh-koc.zip)版本根目录下的`blowfish_test.c`：

```
#include &lt;stdio.h&gt;
#include "blowfish.h"

void main(void) `{`
  unsigned long L = 1, R = 2;
  BLOWFISH_CTX ctx;

  Blowfish_Init (&amp;ctx, (unsigned char*)"TESTKEY", 7);
  Blowfish_Encrypt(&amp;ctx, &amp;L, &amp;R);
  printf("%08lX %08lXn", L, R);

  if (L == 0xDF333FD2L &amp;&amp; R == 0x30A71BB4L)
      printf("Test encryption OK.n");
  else
      printf("Test encryption failed.n");
  Blowfish_Decrypt(&amp;ctx, &amp;L, &amp;R);
  if (L == 1 &amp;&amp; R == 2)
        printf("Test decryption OK.n");
  else
      printf("Test decryption failed.n");
`}`
```

需要说明的一点是Paul Kocher这个版本并没有考虑到小端序的情况，它均按大端序来处理，所以如果在Linux平台运行此Demo会像下图所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/11/13/MJZUAO.png)

可以看到加密结果并非源码中给出的结果，而在Windows平台下运行，正常显示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/11/13/MJZtHK.png)



## 0x03 CBC模式

> 如果对于分组密码模式已经有所了解的读者可直接跳过此节

Blowfish Cipher与DES、AES一样，都是分组密码，Blowfish Cipher每次只能处理64位(即分组长度为8字节)的数据，可是通常我们在加密时输入的明文长度都会大于8字节，这时如何去处理每个明文分组就成为一个应当考虑的问题。分组密码的模式是这个问题的解决方案，常见模式有5种：
- ECB(Electronic Codebook, 电子密码本)模式
- CBC(Cipher Block Chaining, 密码分组链接)模式
- CFB(Cipher Feedback, 密码反馈)模式
- OFB(Output Feedback, 输出反馈)模式
- CTR(Counter, 计数器)模式
Navicat并没有使用上述的任何一种加密模式，但其采用的加密模式与CBC相似，故简单介绍CBC模式(下图来自Wikipedia)，如果对于其他4种加密模式感兴趣，可自行百度。

[![](https://s2.ax1x.com/2019/11/24/MO3xJJ.png)](https://s2.ax1x.com/2019/11/24/MO3xJJ.png)

`Plaintext`是明文按照分组密码的分组长度分割而成，初始化向量`IV`、密钥`Key`在加密时自行决定，`Block Cipher Encryption`是使用的加密算法，最终将每个密文分组`Ciphertext`连接起来即密文。



## 0x04 Navicat 加密过程

### <a class="reference-link" name="0x04.1%20%E6%96%B0%E5%BB%BA%E8%BF%9E%E6%8E%A5"></a>0x04.1 新建连接

首先，打开Navicat，新建一个MySQL连接：

[![](https://s2.ax1x.com/2019/11/24/MO3XoF.png)](https://s2.ax1x.com/2019/11/24/MO3XoF.png)

连接名为Test,用户名默认root,密码123456:

[![](https://s2.ax1x.com/2019/11/24/MO3OdU.png)](https://s2.ax1x.com/2019/11/24/MO3OdU.png)

Navicat将主机(Host),端口(Port),用户名(UserName)与加密后的密码(Pwd)保存到注册表中,不同的数据库连接对应的注册表路径不同,具体路径如下:

[![](https://s2.ax1x.com/2019/11/24/MO3Hs0.png)](https://s2.ax1x.com/2019/11/24/MO3Hs0.png)

`Win+R`之后键入`regedit`打开注册表，按照上述路径去查找，可以看到刚刚我们建立的MySQL连接的相关键值对：

[![](https://s2.ax1x.com/2019/11/24/MO3bLV.png)](https://s2.ax1x.com/2019/11/24/MO3bLV.png)

### <a class="reference-link" name="0x04.2%20Navicat%E5%A6%82%E4%BD%95%E5%8A%A0%E5%AF%86%E6%95%B0%E6%8D%AE%E5%BA%93%E5%AF%86%E7%A0%81"></a>0x04.2 Navicat如何加密数据库密码

**<a class="reference-link" name="0x04.2-1%20Key"></a>0x04.2-1 Key**

Navicat使用SHA-1生成160位长度的密钥：

[![](https://s2.ax1x.com/2019/11/24/MO3vi4.png)](https://s2.ax1x.com/2019/11/24/MO3vi4.png)

存放于无符号字符数组中：

```
unsigned char Key[20] = `{`
    0x42, 0xCE, 0xB2, 0x71, 0xA5, 0xE4, 0x58, 0xB7,
    0x4A, 0xEA, 0x93, 0x94, 0x79, 0x22, 0x35, 0x43,
    0x91, 0x87, 0x33, 0x40
`}`;
```

<a class="reference-link" name="0x04.2-2%20IV"></a>**0x04.2-2 IV**

Navicat在加解密过程中用到的IV是通过Blowfish Cipher加密8字节长度的`0xFFFFFFFFFFFFFFFF`得到，代码细节如下：

```
unsigned long l,r;
    unsigned char IV[BLOCK_SIZE] = "";
    int i;
    BLOWFISH_CTX ctx;

     //Initialize Initial Vector
    l=0xFFFFFFFF;
    r=0xFFFFFFFF;
    Blowfish_Init(&amp;ctx,Key,20);
    Blowfish_Encrypt(&amp;ctx,&amp;l,&amp;r);
    for(i=3; i&gt;=0; --i)
    `{`
        IV[i]=(unsigned char)(l &amp; 0xFF);
        l &gt;&gt;=8;
        IV[i+4]=(unsigned char)(r &amp; 0xFF);
        r &gt;&gt;=8;
    `}`
```

`Blowfish_Encrypt(&amp;ctx,&amp;l,&amp;r)`之后的`for`循环是要将8字节长度密文逐字节赋值给IV数组中的每个元素，IV数组中每个元素值具体如下：

```
unsigned char IV[8] = `{`
    0xD9, 0xC7, 0xC3, 0xC8, 0x87, 0x0D, 0x64, 0xBD
`}`;
```

<a class="reference-link" name="0x04.2-3%20Mode"></a>**0x04.2-3 Mode**

`0x03`部分中已经提到Navicat采用的分组密码模式并非5种主要加密模式之一，其采用的分组密码模式工作过程如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/11/24/MO3zW9.png)
- 每个`PlaintextBlock`长度为8字节；在`Blowfish_Cipher`环节不需要提供密钥`Key`，密钥`Key`在调用`Blowfish_Init()`已经提供，Blowfish Cipher在加解密过程使用已经初始化的`ctx`进行。
- 只有剩余分组大小不足8字节时，才会进行上图中的最后一步。否则，一切照旧。
<a class="reference-link" name="0x04.2-4%20%E5%AF%86%E6%96%87%E5%AD%98%E5%82%A8"></a>**0x04.2-4 密文存储**

按照分组密码模式，最终的密文应与明文长度一致，可注册表中保存的是”15057D7BA390”。这是因为Navicat在向注册表中写入的并非密文，而是十六进制表示的密文ASCII码。



## 0x05 Navicat Part of CDecryptPwd

> 由于此工具目前处于测试阶段，仍有许多有待完善之处，故暂时不公开源码，下面介绍的只是各环节的核心部分。

[![](https://s2.ax1x.com/2019/11/24/MO8SzR.png)](https://s2.ax1x.com/2019/11/24/MO8SzR.png)

### <a class="reference-link" name="0x05.1%20blowfish.c%20&amp;%20blowfish.h"></a>0x05.1 blowfish.c &amp; blowfish.h

这两个文件直接使用的是Paul Kocher版本源码。

### <a class="reference-link" name="0x05.2%20NavicatPartHeader.h"></a>0x05.2 NavicatPartHeader.h

```
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;
#include "blowfish.h"
#include &lt;Windows.h&gt;
#include &lt;tchar.h&gt;
#include &lt;locale.h&gt;

#define BLOCK_SIZE 8
#define KEYLENGTH 256

void XorText(unsigned char left[],unsigned char right[],unsigned char result[],unsigned long r_length);
unsigned long CharConvertLong(unsigned char Text[],short Len);
void LongConvertChar(unsigned long num,unsigned char Text[],short Len);
void Navicat_Encrypt(unsigned char PlainText[],unsigned char CipherText[]);
void Navicat_Decrypt(unsigned char CipherText[],unsigned char PlainText[]);
```

该文件包含了`NavicatPart.c`与`NavicatPartMain.c`文件中要使用到的头文件；定义了两个全局符号常量`BLOCK_SIZE`和`KEYLENGTH`，分别是分组长度与最大键值长度；以及`NavicatPart.c`中的函数原型声明。

### 0x05.3 XorText() &amp; CharConvertLong() &amp; LongConvertChar() of `NavicatPart.c`

`void XorText(unsigned char left[],unsigned char right[],unsigned char result[],unsigned long r_length)`接受4个参数：左操作字符串、右操作字符串、结果字符串、右操作字符串长度，功能是左操作字符串与右操作字符串的异或运算。之所以使用右操作字符串长度控制何时结束，是因为考虑到模式的剩余分组可能会小于分组长度(8字节)。

```
void XorText(unsigned char left[],unsigned char right[],unsigned char result[],unsigned long r_length)
`{`
    int i;
    for(i=0;i&lt;r_length;++i)
        result[i]=left[i]^right[i];
`}`
```

`unsigned long CharConvertLong(unsigned char Text[],short Len)`接受2个参数：转换字符串、其长度，功能是用十六进制ASCII码表示字符串，即该函数返回值。(e.g.:`unsigned char Test[5] = `{`0xA4,0x37,0x98,0x56,''`}``——&gt;&gt;`unsigned long T = CharConvertLong(Test, 4)= 0xA4379856`)

```
unsigned long CharConvertLong(unsigned char Text[],short Len)
`{`
    unsigned long result=0;
    short i;

    for(i=0;i&lt;Len;++i)
    `{`
        result &lt;&lt;=8;
        result |=Text[i];
    `}`
    return result;
`}`
```

`void LongConvertChar(unsigned long num,unsigned char Text[],short Len)`接受3个参数：转换数、存储字符串、长度，功能与上一函数相反，是将数值的十六进制表示逐字节分割后赋给存储字符串中每个元素。(e.g.:`unsigned long T = 0xA4379856`——&gt;&gt;`unsigned char Test[5] = LongConvertChar(T,Test,4) = `{`0xA4,0x37,0x98,0x56,''`}`;`)

```
void LongConvertChar(unsigned long num,unsigned char Text[],short Len)
`{`
    short i;
    for(i=Len-1;i&gt;=0;--i)
    `{`
        Text[i]=(unsigned char)(num &amp; 0xFF);
        num &gt;&gt;=8;
    `}`
`}`
```

### 0x05.4 Navicat_Encrypt() of `NavicatPart.c`

```
void Navicat_Encrypt(unsigned char PlainText[],unsigned char CipherText[])
`{`
    unsigned long l,r,TextLength,block,remain,l_temp,r_temp;
    unsigned char IV[BLOCK_SIZE] = "";
    unsigned char c_temp[BLOCK_SIZE + 1] = "";
    int i;
    BLOWFISH_CTX ctx;

    //Initialize Initial Vector
    l=0xFFFFFFFF;
    r=0xFFFFFFFF;
    Blowfish_Init(&amp;ctx,Key,20);
    Blowfish_Encrypt(&amp;ctx,&amp;l,&amp;r);
    for(i=3; i&gt;=0; --i)
    `{`
        IV[i]=(unsigned char)(l &amp; 0xFF);
        l &gt;&gt;=8;
        IV[i+4]=(unsigned char)(r &amp; 0xFF);
        r &gt;&gt;=8;
    `}`

    //Encrypt PlainText
    TextLength=strlen(PlainText);
    block=TextLength/BLOCK_SIZE;
    remain=TextLength%BLOCK_SIZE;
    for(i=0;i&lt;block;++i)
    `{`
        memcpy(c_temp, PlainText + i * BLOCK_SIZE, BLOCK_SIZE);
        c_temp[BLOCK_SIZE] = '';
        XorText(IV,c_temp,c_temp,BLOCK_SIZE);
        l_temp=CharConvertLong(c_temp,4);
        r_temp=CharConvertLong(c_temp+4,4);
        Blowfish_Encrypt(&amp;ctx,&amp;l_temp,&amp;r_temp);
        LongConvertChar(l_temp,c_temp,4);
        LongConvertChar(r_temp,c_temp+4,4);
        memcpy(CipherText + i * BLOCK_SIZE, c_temp, BLOCK_SIZE);
        XorText(IV,c_temp,IV,BLOCK_SIZE);
    `}`

    if(remain)
    `{`
        l_temp=CharConvertLong(IV,4);
        r_temp=CharConvertLong(IV+4,4);
        Blowfish_Encrypt(&amp;ctx,&amp;l_temp,&amp;r_temp);
        LongConvertChar(l_temp,IV,4);
        LongConvertChar(r_temp,IV+4,4);
        memcpy(c_temp, PlainText + i * BLOCK_SIZE, remain);
        c_temp[remain] = '';
        XorText(IV,c_temp,c_temp,remain);
        memcpy(CipherText + i * BLOCK_SIZE, c_temp, remain);
    `}`
`}`
```

该函数在`main`中并未使用。
1. 初始化IV上面已经介绍，不再赘述，需提示一点：这一部分不能作为函数独立，然后在`Navicat_Encrypt()`中调用该函数，因为下面的Blowfish Cipher加密要使用其初始化的ctx。
1. 第二个`for`循环部分完成`0x04.2-3`图中给出的前(n-1)步的过程。
<li>
`if`部分是处理剩余分组大小不足8字节的情况，即第n步。</li>
<li>
`CharConverLong()`与`LongConverChar()`的存在是因Paul Kocher版本源只能处理无符号长整型。</li>
### 0x05.5 Navicat_Decrypt() of `NavicatPart.c`

```
void Navicat_Decrypt(unsigned char CipherText[],unsigned char PlainText[])
`{`
    unsigned long l,r,TextLength,block,remain,l_temp,r_temp;
    unsigned char IV[BLOCK_SIZE] = "";
    unsigned char c_temp1[BLOCK_SIZE+1] = "";
    unsigned char c_temp2[BLOCK_SIZE+1] = "";
    int i;
    BLOWFISH_CTX ctx;

    //Initialize Initial Vector
    l=0xFFFFFFFF;
    r=0xFFFFFFFF;
    Blowfish_Init(&amp;ctx,Key,20);
    Blowfish_Encrypt(&amp;ctx,&amp;l,&amp;r);
    for(i=3; i&gt;=0; --i)
    `{`
        IV[i]=(unsigned char)(l &amp; 0xFF);
        l &gt;&gt;=8;
        IV[i+4]=(unsigned char)(r &amp; 0xFF);
        r &gt;&gt;=8;
    `}`

    //Decrypt CipherText
    TextLength=strlen(CipherText);
    block=TextLength/BLOCK_SIZE;
    remain=TextLength%BLOCK_SIZE;
    for(i=0;i&lt;block;++i)
    `{`
        memcpy(c_temp1, CipherText + i * BLOCK_SIZE, BLOCK_SIZE);
        c_temp1[BLOCK_SIZE] = '';
        memcpy(c_temp2, CipherText + i * BLOCK_SIZE, BLOCK_SIZE);
        c_temp2[BLOCK_SIZE] = '';
        l_temp=CharConvertLong(c_temp1,4);
        r_temp=CharConvertLong(c_temp1+4,4);
        Blowfish_Decrypt(&amp;ctx,&amp;l_temp,&amp;r_temp);
        LongConvertChar(l_temp,c_temp1,4);
        LongConvertChar(r_temp,c_temp1+4,4);
        XorText(IV,c_temp1,c_temp1,BLOCK_SIZE);
        memcpy(PlainText+i*BLOCK_SIZE, c_temp1, BLOCK_SIZE);
        XorText(IV,c_temp2,IV,BLOCK_SIZE);
    `}`

    if(remain)
    `{`
        l_temp=CharConvertLong(IV,4);
        r_temp=CharConvertLong(IV+4,4);
        Blowfish_Encrypt(&amp;ctx,&amp;l_temp,&amp;r_temp);
        LongConvertChar(l_temp,IV,4);
        LongConvertChar(r_temp,IV+4,4);
        memcpy(c_temp1, CipherText + i * BLOCK_SIZE, remain);
        c_temp1[remain] = '';
        XorText(IV,c_temp1, c_temp1,remain);
        memcpy(PlainText + i * BLOCK_SIZE, c_temp1, remain);
    `}`
`}`
```

解密过程可参照下图理解：

[![](https://s2.ax1x.com/2019/11/24/MO8Csx.png)](https://s2.ax1x.com/2019/11/24/MO8Csx.png)

除了多一步密文分组的拷贝，其余都是加密过程的逆过程，不再赘述。

### 0x05.6 main() of `NavicatPartMain.c`

主程序功能：
- 遍历注册表，路径前缀`计算机HKEY_CURRENT_USERSoftwarePremiumSoft`不变，变化的是与其拼接的字符串，可根据Navicat写入注册表时创建路径的规律来进行拼接：
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/11/24/MO8PL6.png)

`Data`与`NavicatPremium`子项均与存储数据库相关信息无关，不包含`Servers`，而存储数据库相关信息的`Navicat`与`NavicatPG`子项均包含`Servers`，所以可进行这一判断来决定是否要用`RegEnumKeyEx()`遍历`Servers`下的子项。
- 使用`RegEnumValue()`遍历`Servers`子项中的键值对，主要是Host、UserName、Pwd、Port四项。在读取Pwd值之后传递给`Navicat_Decrypt()`进行解密。需要说明一点：在读取Port之前，读取类型要从`REG_SZ`转为`REG_DWORD`，否则读出的值无意义。
运行效果图：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://s2.ax1x.com/2019/11/24/MO8FeK.png)

## 0x06 参考
- [Wikipedia](https://en.wikipedia.org/wiki/Blowfish_(cipher)
- [圆周率小数部分](http://www.super-computing.org/pi-hexa_current.html)
- 《图解密码技术(第三版)》
- [how-does-navicat-encrypt-password](https://github.com/DoubleLabyrinth/how-does-navicat-encrypt-password)
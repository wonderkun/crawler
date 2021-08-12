> 原文链接: https://www.anquanke.com//post/id/249652 


# Golang逆向分析 &amp; 第五届XMan选拔赛 ezCM Writeup


                                阅读量   
                                **20761**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01e0f3d0072c8ab3ce.jpg)](https://p3.ssl.qhimg.com/t01e0f3d0072c8ab3ce.jpg)



## ezCM

直至比赛结束，这道题目都是 0 解题，一方面是因为比赛时间较短，另一方面还是因为这道题目较难，考察了不常见的椭圆曲线算法(ECC)，大大增加了对做题者的要求。

我也是第一次做题遇到 ECC，对此了解也不多，在查阅大量资料和请教了队内的密码学师傅（Dawn_whisper yyds），最终解出了此题，对于此题的思考过程做了一个整理，方便大家学习。但由于我对于 ECC 只是一个粗浅的理解，所以本篇文章在一些专业知识上有些可能会有所出错，请各位师傅指教！[题目附件](https://adworld.xctf.org.cn/media/uploads/task/4e2fca5db3fd49208589efb77f2a67f7.zip)

### <a class="reference-link" name="%E9%A2%98%E7%9B%AE%E4%BF%A1%E6%81%AF"></a>题目信息

[![](https://p4.ssl.qhimg.com/t0161376e7749cbaf37.png)](https://p4.ssl.qhimg.com/t0161376e7749cbaf37.png)

题目是使用 Golang 来编写的一个 CrackMe 程序，程序内符号没有被去除，所以这篇文章就不会讲解如何恢复 Golang 程序符号，另外 IDA Pro 7.6 已经支持 Golang 程序分析，打开就可以直接恢复被去除的符号信息。

题目要求打开一个 KeyFile ，并且通过读取其文件的内容来注册程序，我们要做的就是通过分析程序验证方式来编写一个 KeyFile，使其可以通过程序注册验证，最终拿到 flag 数据。

### <a class="reference-link" name="%E5%89%8D%E7%BD%AE%E7%9F%A5%E8%AF%86"></a>前置知识

由于是 Golang 的题目，在一些数据结构和调用约定上和大多数语言都不一样，所以一定不能过于的依赖伪代码，在调试过程中最好能够多关注汇编代码，这样在逆向过程中会快速掌握到核心。这部分内容参考学习了 [panda0s – Golang underlying data representaion ](https://panda0s.top/2021/04/14/Golang-underlying-data-representaion/)，本来是不想把这部分内容放在这篇文章中的，但是由于关联性过大，所以不得不拿来饱满文章内容。

#### <a class="reference-link" name="%E5%87%BD%E6%95%B0%E8%B0%83%E7%94%A8"></a>函数调用

在函数调用的过程中，无论是调用参数还是返回值都是通过栈来传递。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0198b01ee3c8b48b16.png)

其传参的特征是
1. 参数传递顺序是从右往左传递，而且不使用像是 push pop 这样的操作栈的指令，而是直接对栈上的内容进行修改。
1. 参数传递一般都是借助一个寄存器中转，例如 rax、rcx，先把数据原来的储存位置的数据赋值到这个寄存器上，然后再把这个寄存器的内容赋值给栈上数据，并且如果数据是 0x10 size 的结构体，就会借助 xmm 寄存器中转来加速。
其返回值的特征是
1. 返回值的位置紧贴着在最后一个参数的地址之后。以上图为例，最后一个参数的地址是 rsp + 0x250 – 0x248 + 0x8 = rsp + 0x10，所以这里的返回值的地址就是在 rsp + 0x250 – 0x238 = rsp + 0x18，有多个返回值的情况也是类似。
#### <a class="reference-link" name="%E6%96%B9%E6%B3%95%E8%B0%83%E7%94%A8"></a>方法调用

在上图中，严格意义上并不是一次函数调用，而是一次方法调用。他是对 MyMainWindow 这个对象下的 Academy 方法进行了调用，这个传入的参数就是这个对象的指针，像是 this 一样。这个对象的指针就相对于函数调用的第一个参数。

#### <a class="reference-link" name="String%20%E5%AD%97%E7%AC%A6%E4%B8%B2"></a>String 字符串

[![](https://p3.ssl.qhimg.com/t01bd1a106467ce94e6.png)](https://p3.ssl.qhimg.com/t01bd1a106467ce94e6.png)

##### <a class="reference-link" name="String%20%E7%BB%93%E6%9E%84"></a>String 结构

```
struct String`{`
    char * strPtr;
    int64 size;
`}`
```

所以 Golang 程序在传递字符串的时候，同时也会在后续跟一个参数，这个参数指的就是字符串的长度。同时由于这样的机制，使得字符串的内容在内存中分布不需要截止符’\x00’

#### <a class="reference-link" name="Slice%20%E5%88%87%E7%89%87"></a>Slice 切片

在其他语言中（例如 python），Slice 是一种切片的操作，切片之后可以返回一个新的数据对象，但是 Golang 中的 Slice 不仅仅是一种切片的操作，更像是一种灵活的数据结构。

了解 Slice 结构后，在 IDA 中修改对应的变量类型，可以大大加快分析速度。

##### <a class="reference-link" name="Slice%20%E7%BB%93%E6%9E%84"></a>Slice 结构

```
struct slice `{`
    dq    Pointer;
    dq    Length;
    dq    Capacity;
`}`
```

Pointer：指向 Slice 底层数组的元素开始位置的指针

Length：Slice 的当前长度

Capacity：Slice 底层数组的最大长度，超过此长度会自动扩展

##### <a class="reference-link" name="%E5%88%9D%E5%A7%8B%E5%8C%96%20Slice"></a>初始化 Slice

```
my_slice := make([]int, 3，5)
```

这表示先声明一个长度为 5、数据类型为 int 的底层数组，然后从这个底层数组中从前向后取 3 个元素作为 slice 的结构（length = 3，cap = 5）

make 最底层调用 runtime_makeslice 分配空间，这个函数返回的是指向内部数组的指针

##### <a class="reference-link" name="%E8%AE%BF%E9%97%AE%20Slice"></a>访问 Slice

```
org_len := slice1[name_size + 1]
```

[![](https://p2.ssl.qhimg.com/t0152975d7791867379.png)](https://p2.ssl.qhimg.com/t0152975d7791867379.png)

在访问 Slice 中元素时，会检测是否越界如果越界则调用 runtime_panicIndex

##### <a class="reference-link" name="append%20/%20copy"></a>append / copy

当 Length 已经等于 Capacity 的时候，再使用 append 给 slice 追加元素，会调用 runtime_growslice 进行扩容。

在代码中的表现是在 append / copy 的时候会检测，slice.len + 1 与 slice1.cap 的大小关系

[![](https://p1.ssl.qhimg.com/t01215158f407745c6a.png)](https://p1.ssl.qhimg.com/t01215158f407745c6a.png)

如图在把 slice 转换为字符串的过程前，由于将要 copy slice，所以会对传参 len 进行检测。

##### <a class="reference-link" name="%E5%88%87%E7%89%87%E6%88%AA%E5%8F%96"></a>切片截取

```
myvar := slice1[a:b]
```

myvar 是新一个新的切片结构<br>
dataPtr = &amp;slice1.dataPtr[1]，相当于给了一个底层数组的指针<br>
len = b – a<br>
cap = slice1.cap – a

### <a class="reference-link" name="%E5%AF%BB%E6%89%BE%E5%85%B3%E9%94%AE%E5%87%BD%E6%95%B0"></a>寻找关键函数

对于这种有界面的程序，和常规的只有一个控制台的题目不同的是，题目的关键信息不是直接存在于 main 函数中，所以我们首先要做的就是定位到题目的关键位置。

而在这道题里，我们的突破口就是在没有选择文件的情况下，点击“Register”就会弹出的信息框“Cannot open target file.”

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t011157c6463dda4c83.png)

我们可以利用 IDA 的 Shift + F12 热键调出 Strings 窗口来查找“Cannot open target file.”字符串

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019265f70cbe1542d9.png)

搜索字符串后，我们再双击进入，在前面自动生成的名称处按下 X 热键查找交叉引用

[![](https://p5.ssl.qhimg.com/t019d55f9893d0ebf39.png)](https://p5.ssl.qhimg.com/t019d55f9893d0ebf39.png)

对于每一处引用我们都前去查看，最终找到了关键的代码位置（截图仅截取部分代码）

[![](https://p3.ssl.qhimg.com/t01c7f7c95030e44124.png)](https://p3.ssl.qhimg.com/t01c7f7c95030e44124.png)

我们接下来对函数内容进行分步骤的解析

### <a class="reference-link" name="KeyFile%20%E6%A0%BC%E5%BC%8F%E8%A7%A3%E6%9E%90"></a>KeyFile 格式解析

#### <a class="reference-link" name="%E7%89%B9%E5%BE%81%E6%A0%BC%E5%BC%8F"></a>特征格式

[![](https://p0.ssl.qhimg.com/t018e6947b339c50c39.png)](https://p0.ssl.qhimg.com/t018e6947b339c50c39.png)

这部分内容虽然伪代码看起来混乱，但是大概可以猜测是开头和结尾的特征字符

```
---BEGIN CERT---
xxx
----END CERT----
```

通过这两个特征读取出关键的秘钥信息 xxx，然后传入到后续函数，这样的标记格式在其他地方也很常见，所以这里不着重分析。

#### <a class="reference-link" name="%E8%A7%A3%E5%AF%86%E6%A0%B8%E5%BF%83%E6%95%B0%E6%8D%AE"></a>解密核心数据

在后续函数中的对秘钥核心数据做了一个解码

[![](https://p2.ssl.qhimg.com/t0122a273006e704d09.png)](https://p2.ssl.qhimg.com/t0122a273006e704d09.png)

这里上述代码中可以看出，程序先通过一个 base64 解密对中间部分内容进行解码，然后以两个字节为一个单位进行解密，对第一字节异或 0xAA 得到数据，并且对第二字节异或 0x55，与第一字节的内容进行比对，如果不同则直接退出。

#### <a class="reference-link" name="%E6%95%B0%E6%8D%AE%E7%BB%93%E6%9E%84%E6%A0%BC%E5%BC%8F"></a>数据结构格式

解密后的数据是如何在存放的，分别又代表着那些信息？想要知道这些就要分析接下来所做的代码。

[![](https://p3.ssl.qhimg.com/t0113e0209106aa58df.png)](https://p3.ssl.qhimg.com/t0113e0209106aa58df.png)

代码中由于对切片做了很多索引操作，所以有各种各样的越界检测，我们抛开这部分代码来看，就可以看出 Username 和 Organization 的储存结构 —— 第一个字节存放字符串长度，后续跟字符数据。

[![](https://p4.ssl.qhimg.com/t0148254b15a2c493f5.png)](https://p4.ssl.qhimg.com/t0148254b15a2c493f5.png)

根据**前置知识**中切片的相关知识，这里调用 math_big_nat_setBytes 的切片内容我们可以大致还原，主要就是根据切片的 len 和 cap 来确定，

切片左边的值：由来源切片的 cap 减去的内容

切片右边的值：由来源切片左边的值 + 新切片的 len

所以 main_a 和 main_b 的内容来源于新的切片内容分别是

```
a[org_len + name_len + 2:org_len + name_len + 2 + 8]
a[org_len + name_len + 10:org_len + name_len + 10 + 8]
```

这部分内容可以结合上面的伪代码结合得出，也就是 Username 和 Organization 后的 8 字节是 main_a 的内容，再后 8 字节是 main_b 的内容，最后 4 字节是 main_expire 的内容。

这里需要注意的是，main_a 和 main_b 的内容都是以字节的形式直接转换为大数类型，而 main_expire 是以 WORD 的形式读取（使用 2 字节），这两种读取方式的字节序不同。

#### <a class="reference-link" name="%E6%95%B0%E6%8D%AE%E8%A1%A8"></a>数据表

综合上面所说的，可以得出以下表格来记录 KeyFile 文件内加密数据格式

|偏移|内容|变量名|长度
|------
|0|Username 长度|name_len|1
|1|Username 内容|str_name|name_len
|1 + name_len|Organization 长度|org_len|1
|2 + name_len|Organization 内容|str_org|org_len
|2 + name_len + org_len|内容 A|main_a|8
|10 + name_len + org_len|内容 B|main_b|8
|18 + name_len + org_len|过期时间|main_expire|2

### <a class="reference-link" name="%E9%AA%8C%E8%AF%81%E9%80%BB%E8%BE%91"></a>验证逻辑

#### <a class="reference-link" name="%E7%BA%A6%E6%9D%9F%E6%9D%A1%E4%BB%B6"></a>约束条件

了解了程序如何解析 KeyFile 后，接下来才是本文最关键的地方，也就是程序的验证方法。

[![](https://p4.ssl.qhimg.com/t01238d3074e3190aca.png)](https://p4.ssl.qhimg.com/t01238d3074e3190aca.png)

首先会把 main_a 和 main_b 的内容相加，然后与 13417336609348053335（0xba33f48ee008e957）进行比对，如果相同则进入后续的判定，这就是对 a 和 b 之间关系的一个约束。

#### <a class="reference-link" name="%E5%88%9D%E5%A7%8B%E5%8C%96%E5%A4%A7%E6%95%B0"></a>初始化大数

[![](https://p0.ssl.qhimg.com/t01fa3823d3fe497016.png)](https://p0.ssl.qhimg.com/t01fa3823d3fe497016.png)

接下来又对三个大数进行了初始化，我把这几个常量去 Google 搜索了一下，发现 main_p 的值是在 GF(p) 上的椭圆曲线中常用的一种取值，这对于我们了解接下来的代码的大致内容有所帮助。

这样根据常量来猜测程序意义的方法也是常用的，这里就是借助了椭圆曲线中常见的 p。

#### <a class="reference-link" name="%E9%AA%8C%E8%AF%81%E4%BB%A3%E7%A0%81"></a>验证代码

[![](https://p4.ssl.qhimg.com/t013b060553ec191cc0.png)](https://p4.ssl.qhimg.com/t013b060553ec191cc0.png)

最终的检测代码就是判断题目 public_key 是否在椭圆曲线（y^2 = x^3 + ax + b）上，其中 a 和 b 是用户可控的值，我们现在有一个在椭圆曲线上的点 生成元 G ，那么我们就可以根据这个 G 点的值和 a + b 的约束来反推 a 和 b 的值。

```
(gy^2) % p                                      =   (gx^3 + a * gx + b) % p
(gy^2 - gx^3) % p                               =   (a * gx + b) % p
(gy^2 - gx^3 - (a + b)) % p                     =   (a * (gx - 1)) % p
(a * gx + b) % p - ((a + b) % p)                = (a * (gx - 1)) % p
((a * gx + b) % p - ((a + b) * inv(gx - 1)) % p = a % p
```

推导过程只是我粗浅的理解，所以可能不是很规范，但是表明了如何推出 a 的值，有了 a 的值后，我们直接相减就可以计算得到 b 的值。

### <a class="reference-link" name="%E6%B3%A8%E5%86%8C%E6%9C%BA%E7%BC%96%E5%86%99"></a>注册机编写

通过上述的逻辑和整理，我们可以快速的编写出一个 Keygen，我的代码如下

```
import base64
import gmpy2
from Crypto.Util.number import *

def calc_ab():
    gx = 0xf20553f3b02d1cad6aa8f895cc331a84b78f9bded26ecd9170662d3251d8d8a2
    gy = 0xa5c2e0fca8853a37f651726d719dd734421d0e01adf23c12c921e9060bc4c832
    p = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
    sum = 0xba33f48ee008e957  # a + b
    # y^2 = x^3 + ax + b
    p1 = (gy * gy) % p   # y^2
    p2 = (gx * gx * gx) % p  # x^3
    p3 = (p1 - p2) % p   # ax + b
    p4 = (p3 - sum) % p  # ax + b - (a + b) = a * (x - 1)
    inv = gmpy2.invert(gx - 1, p)
    a = (p4 * inv) % p
    b = (sum - a) % p
    return a, b


def generate(Username, Organization, ExpireTime):
    if len(Username) &gt;= 16:
        return ""
    if len(Organization) &gt;= 16:
        return ""
    if ExpireTime &gt; 0xffff:
        return ""
    reg_info = ""
    reg_info += chr(len(Username)) + Username
    reg_info += chr(len(Organization)) + Organization
    a, b = calc_ab()
    reg_info += long_to_bytes(a).rjust(8, '\x00') + long_to_bytes(b).rjust(8, '\x00')
    reg_info += long_to_bytes(ExpireTime).rjust(2, '\x00')[::-1]

    en_info = ''
    for i in reg_info:
        en_info += chr(ord(i) ^ 0xAA) + chr(ord(i) ^ 0x55)
    en_info = base64.b64encode(en_info)
    return '---BEGIN CERT---\n' + en_info + "\n----END CERT----"


with open("C:\\reg.crt", "w") as f:
    f.write(generate('wjh', 'org', 8888))
```

接下来把 KeyFile 拖入程序，点击 Register，即可成功通过验证得到 Flag

[![](https://p0.ssl.qhimg.com/t0192f8f1b4e85f047f.png)](https://p0.ssl.qhimg.com/t0192f8f1b4e85f047f.png)

可以发现 flag 的值其实就是 main_a 和 main_b 的 hex 编码后的值，这样可以保证 flag 的唯一性。

### <a class="reference-link" name="%E6%80%BB%E7%BB%93"></a>总结

在这之前其实也遇到过一些 Golang 的题目，但是因为 Golang 难以分析，所以这些题目的核心算法相对来说都比较简单，都是一些比较简单的逻辑问题。这道题虽然分析过程看似简单轻松，但是实际上我对其内涵的原理和程序的用法进行了深入的研究，消耗了大量的时间和精力。虽然本题最终展现的并不是一个 ECC 难题，但是在逆向分析的过程中，我也学习到了一些 ECC 的内涵和代码实现。希望各位师傅可以借此题来开篇学习 Golang 逆向和 ECC 算法。

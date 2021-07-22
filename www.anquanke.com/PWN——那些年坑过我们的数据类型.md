> 原文链接: https://www.anquanke.com//post/id/173063 


# PWN——那些年坑过我们的数据类型


                                阅读量   
                                **198865**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01a24a7bac59383319.jpg)](https://p5.ssl.qhimg.com/t01a24a7bac59383319.jpg)



## 引言

老铁们我来填坑啦！

本人安全客上一篇内核pwn的坑还记得吧？就是关于无符号整型使用不当的漏洞利用，最后传进去的长度值为啥是0xffffffffffff0000|0x100，不着急，我们从基础开始介绍，这篇文章的要点包括：
- 陌生的数据类型：文档+汇编
- 整数溢出漏洞
- 无符号整型使用不当漏洞
数据类型是个很基础又很细节的东西，越是这种细节的东西反而越容易坑人，它不像堆栈溢出那样的漏洞容易发现，pwn中数据类型的问题往往稍不注意就会错过利用点或者使exp莫名跑崩，不知道有多少人被它坑过；如果入门pwn的时候没有打好数据类型的基础，往后掌握了更高级的攻击面后很容易被坑，因此笔者写了这篇从计算层面出发、面向基础的数据类型相关漏洞的讲解，难度并不大，希望能帮入门者打好基础！



## 一、陌生的数据类型：文档+汇编

我们在做pwn的时候，最直观判断数据类型的途径就是看IDA反编译出的C伪代码，然而，由于IDA的判定逻辑有时候并不能彻底如人意，有时候某些变量就会被判断成我们在编程层面很少用到的数据类型，这种判断并没有错误，然而却给逆向工程人员带来了不便。

比如：unsigned __int64、unsigned __int8，这些不常见的数据类型如果不加注意，我们就根本无法进行有效的漏洞挖掘和利用，当我们在伪代码界面看到不熟悉的数据类型，应对的方法就是查文档加看汇编

笔者在网上找到一份微软的文档：

[https://docs.microsoft.com/zh-cn/previous-versions/s3f49ktz(v=vs.120)](https://docs.microsoft.com/zh-cn/previous-versions/s3f49ktz(v=vs.120))

> Visual C++ 32 位和 64 位编译器可识别本文后面的表中的类型。
<ul>
- int (unsigned int)
- __int8 (unsigned __int8)
- __int16 (unsigned __int16)
- __int32 (unsigned __int32)
- __int64 (unsigned __int64)
- short (unsigned short)
- long (unsigned long)
- long long (unsigned long long)
</ul>
如果其名称以两个下划线 (__) 开始，则数据类型是非标准的。
下表中指定的范围均包含起始值和结束值。

<table>
<colgroup>
<col>
<col>
<col>
<col>
</colgroup>
<thead><tr class="header">
|类型名称
|字节
|其他名称
|值的范围
</tr></thead>
<tbody>
<tr class="odd">
|int
|4
|signed
|–2,147,483,648 到 2,147,483,647
</tr>
<tr class="even">
|unsigned int
|4
|unsigned
|0 到 4,294,967,295
</tr>
<tr class="odd">
|__int8
|1
|char
|–128 到 127
</tr>
<tr class="even">
|unsigned __int8
|1
|unsigned char
|0 到 255
</tr>
<tr class="odd">
|__int16
|2
|short、short int、signed short int
|–32,768 到 32,767
</tr>
<tr class="even">
|unsigned __int16
|2
|unsigned short、unsigned short int
|0 到 65,535
</tr>
<tr class="odd">
|__int32
|4
|signed、signed int、int
|–2,147,483,648 到 2,147,483,647
</tr>
<tr class="even">
|unsigned __int32
|4
|unsigned、unsigned int
|0 到 4,294,967,295
</tr>
<tr class="odd">
|__int64
|8
|long long、signed long long
|–9,223,372,036,854,775,808 到 9,223,372,036,854,775,807
</tr>
<tr class="even">
|unsigned __int64
|8
|unsigned long long
|0 到 18,446,744,073,709,551,615
</tr>
<tr class="odd">
|bool
|1
|无
|false 或 true
</tr>
<tr class="even">
|char
|1
|无
<td>-128 到 127（默认）
0 到 255（当使用 [/J](https://docs.microsoft.com/zh-cn/previous-versions/0d294k5z%28v%3dvs.120%29) 编译时）
</td>
</tr>
<tr class="odd">
|signed char
|1
|无
|–128 到 127
</tr>
<tr class="even">
|unsigned char
|1
|无
|0 到 255
</tr>
<tr class="odd">
|short
|2
|short int、signed short int
|–32,768 到 32,767
</tr>
<tr class="even">
|unsigned short
|2
|unsigned short int
|0 到 65,535
</tr>
<tr class="odd">
|long
|4
|long int、signed long int
|–2,147,483,648 到 2,147,483,647
</tr>
<tr class="even">
|unsigned long
|4
|unsigned long int
|0 到 4,294,967,295
</tr>
<tr class="odd">
|long long
|8
|无（与 __int64 等效）
|–9,223,372,036,854,775,808 到 9,223,372,036,854,775,807
</tr>
<tr class="even">
|unsigned long long
|8
|无（与无符号的 __int64 等效）
|0 到 18,446,744,073,709,551,615
</tr>
<tr class="odd">
|enum
|varies
|无
|请参阅本文后面的备注。
</tr>
<tr class="even">
|float
|4
|无
|3.4E +/- 38（7 位数）
</tr>
<tr class="odd">
|double
|8
|无
|1.7E +/- 308（15 位数）
</tr>
<tr class="even">
|long double
|与 double 相同
|无
|与 double 相同
</tr>
<tr class="odd">
|wchar_t
|2
|__wchar_t
|0 到 65,535
</tr>
</tbody>
</table>

根据使用方式，__wchar_t 的变量指定宽字符类型或多字节字符类型。 在字符或字符串常量前使用 L 前缀以指定宽字符类型常量。
signed 和 unsigned 是可用于任何整型（bool 除外）的修饰符。 请注意，对于重载和模板等机制而言，char、signed char 和 unsigned char 是三种不同的类型。
int 和 unsigned int 类型具有四个字节的大小。 但是，由于语言标准允许可移植代码特定于实现，因此该代码不应依赖于 int 的大小。
Visual Studio 中的 C/C++ 还支持按大小分类的整型。 有关更多信息，请参见[__int8、__int16、__int32、__int64](https://docs.microsoft.com/zh-cn/previous-versions/29dh1w7z%28v%3dvs.120%29)和[整数限制](https://docs.microsoft.com/zh-cn/previous-versions/296az74e%28v%3dvs.120%29)。
有关每个类型的大小限制的详细信息，请参阅[基本类型 (C++)](https://docs.microsoft.com/zh-cn/previous-versions/cc953fe1%28v%3dvs.120%29)。
枚举类型的范围因语言上下文和指定的编译器标志而异。 有关更多信息，请参见[C 枚举声明](https://docs.microsoft.com/zh-cn/previous-versions/whbyts4t%28v%3dvs.120%29)和[C++ 枚举声明](https://docs.microsoft.com/zh-cn/previous-versions/2dzy4k6e%28v%3dvs.120%29)。
<h2 name="h2-2" id="h2-2">请参见</h2>
<h4 id="参考" class="heading-with-anchor">参考</h4>
[C++ 关键字](https://docs.microsoft.com/zh-cn/previous-versions/2e6a4at9%28v%3dvs.120%29)
[基本类型 (C++)](https://docs.microsoft.com/zh-cn/previous-versions/cc953fe1%28v%3dvs.120%29)

反正就是充分利用搜索引擎，下面我们举例讲一下怎么通过汇编来判断：

先拿上一篇文章中内核pwn的core那个无符号整型漏洞为例

注意到qmemcpy那里：a1被作为unsigned __int16类型，查文档易知16代表位数，即占两字节无符号，范围自然是0~ffff即0~65535，现在我们去看汇编：

长度值是通过rdi传过来的，这段汇编前面还有一个mov rbx, rdi

> rax  eax  ax  al  ah:
分别是：64位、低32位、低16位、ax的低8位、ax的高8位
其他寄存器同理

movzx是小寄存器拷贝到大寄存器，自动用0补齐目标寄存器未用到的高位字节，0x120处的bx是16位的，ecx就是rep movsb的长度参数、rsi和rdi是rep movsb的源、目标地址

> rep movsb
rep是repeat，重复后面动作的意思，重复次数可知就是ecx
movsb应该是move string byte的缩写，一次拷贝一个字节
连在一起的意思都懂
注意这不是个函数调用而是个指令，所以没有call qmemcpy，不知道是不是编译器优化的缘故还是ida的缘故，因此长度参数用的是寄存器ecx，而没有按照函数调用规则中的寄存器传参顺序使用edx，这就可以理解了

可见，最终，传入的长度参数由rdi“堕落”成了bx，整整由64位八字节的庞然大物堕落成了16位俩字节的小东西，而之前判断长度是否过大（&gt;63）时用的是64位的值（读者自行审汇编）

这样一来漏洞的情况就清晰了：虽然判断大小合法性时用的是完整的64位的数据，然而最终拷贝多少字节是由其低16位（低二字节）决定的

那么我们首先可以先确定我们想拷贝多少个字节来溢出，比如0x100个吧，由此我们确定低16位就是(01 00)h，接下来我们只需要弄好剩下48位（6字节）让整个64位的值是个负数就ok了！

> 32位下int范围：
<ul>
- 正数：00 00 00 00 ~ 7f ff ff ff
- 负数：80 00 00 00 ~ ff ff ff ff       (ff ff ff ff是-1)
</ul>
64位下int范围：
<ul>
- 正数：00 00 00 00 00 00 00 00 ~ 7f ff ff ff ff ff ff ff
- 负数：80 00 00 00 00 00 00 00 ~ ff ff ff ff ff ff ff ff       (ff ff ff ff ff ff ff ff是-1)
</ul>

由此可知，我们可以将ff ff ff ff ff ff 01 00作为最终的取值，当然这里的选择性很多啦~



## 二、无符号整型使用不当漏洞

这种漏洞的原理我们上面已经说过了，在此就只提一下64位下的构造的思路：
1. 确定缓冲区写入操作的长度参数所使用的数据类型的位数：n byte
1. 确定需要绕过的长度检查的逻辑处所用的数据类型的位数：N byte
1. 构造总长度为N byte，低n byte置为0其余各字节全置为ff，记作r
1. R = r|&lt;实现溢出攻击所需的长度&gt;，R即为最初输入的长度值


## 三、整数溢出漏洞

整数溢出定义不好给，直接上例子吧，来道pwn题：

传入一个字符串s，这个s已知在外层调用函数中是可设为任意长度的，但是这里进行了长度检查必须在4~8之间，然而编码者天真的以为既然是4~8那么一个字节大小的数据类型就足够使用了，因此我们看到v3的类型声明为了unsigned __int8，只有8位一字节，范围0~255

然而strlen函数的返回值类型是64位8字节的，因此在强制转换成更短的一字节的v3时，会直接丢失掉高的7个字节！我们下面上汇编代码来具体看一下：

可以看到，strlen的返回值rax寄存器在倒数第二行mov的时候，只将低八位的al部分mov给了用于和3比较的变量！

我们来看一下溢出的发生：最终比较的是八位1字节，我们用更大的值来溢出，比如260吧，其对应的hex为0x104，rax=0x104，对应的al就是0x04，在4~8之间，成功绕过长度检查，实现了后续的溢出字符串拷贝！

那么如何构造呢？我们给出两种思路：
1. 首先确定长度合法性检查处所采用数据类型的位数n，得到M=2^n，集合B为长度检查处所有合法值的集合比如4~8，然后集合`{`A|(A mod M) ∈ B`}`中的所有元素都可以绕过检查，从中随意取个你想要的大小即可！
1. 首先确定长度合法性检查处所采用数据类型的位数n，并在合法长度值中随便挑个值，用位数为n的hex写出来，然后往高位任意扩展位数、以及高位的具体值即可，随你构造！


## 四、总结与心得

可以看到：整数溢出构造思路的第二种方法，其实和前面所说的无符号整型漏洞的长度值构造思想是有着异曲同工之妙的，因为它们都是深入到计算机处理数据的本质，**从“位”的处理上出发来寻找规律**。

深化“**位**”的数据表示和处理思想，对于分析这一系列相关问题会是极大的帮助！！

此外，一定要看汇编！作为一名合格的pwn手要记住不看汇编的pwn，都是耍流氓！往后的文章不久将会讲到一道babydriver的内核pwn，到时候从那个例子中各位就可以深刻体会到，IDA的F5有时候是非常坑的，不看汇编真的不行！

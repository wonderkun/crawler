> 原文链接: https://www.anquanke.com//post/id/164575 


# 当中国剩余定理邂逅RSA


                                阅读量   
                                **326414**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">11</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01cc2382dc5100cfcb.jpg)](https://p5.ssl.qhimg.com/t01cc2382dc5100cfcb.jpg)



## 前言

实在不知道起什么标题，于是滑稽了一波。写这篇文章的起源是2018高校网络信息安全管理运维挑战赛的一道RSA题目，借此机会，将中国剩余定理与RSA的结合研究一下。



## 题目描述

拿到题目很简短

[![](https://p4.ssl.qhimg.com/t017179de41a5a15b70.png)](https://p4.ssl.qhimg.com/t017179de41a5a15b70.png)



## 身陷囹圄

发现

那么本能想到公约数的问题，于是尝试

发现有公约数

那么可以分解出p和q1,q2

得到结果

到目前为止一直很开心，因为成功的分解了p和q

那么是不是直接求逆元，得到私钥，就结束了呢？

我开心的运行

[![](https://p2.ssl.qhimg.com/t01ef7596209df53261.png)](https://p2.ssl.qhimg.com/t01ef7596209df53261.png)

直到报错，我才想起来

所以直接求逆元肯定是不行的

第一时间想到的是Rabin Attack，但是那是e=2的时候，所以此时陷入困境



## 公式代换

后来想到等式代换

[![](https://p3.ssl.qhimg.com/t01a4fbfa94ad9c11d0.png)](https://p3.ssl.qhimg.com/t01a4fbfa94ad9c11d0.png)

我们知道b=14，此时a和phi(n)互素

那么可以求a和phi的逆元得到bd

于是可以

得到m^14 mod n1的值，于是同理：

n1得到一组m^14 mod n1的值

n2得到一组m^14 mod n2的值

可以得到以下方程组：

[![](https://p3.ssl.qhimg.com/t01c79334ef7a78ee80.png)](https://p3.ssl.qhimg.com/t01c79334ef7a78ee80.png)

如果这里不是m^14，是m^2或者m^3

那么完全可以尝试爆破得到m

因为m^2不会太大，所以

[![](https://p3.ssl.qhimg.com/t01c17efcf3f26550e8.png)](https://p3.ssl.qhimg.com/t01c17efcf3f26550e8.png)

那么完全可以使用低指数的思想去破解

然而这里是m^14，并不是啥低指数了。



## 中国剩余定理

虽然题目走的绝，但是他给了2组等式，那么这样的等式，仅仅为了让我们利用公约数分解p,q这么简单吗？答案显然是否定的

这里我们可以尝试中国剩余定理

[![](https://p1.ssl.qhimg.com/t0111427715bf34cbaa.png)](https://p1.ssl.qhimg.com/t0111427715bf34cbaa.png)

二者联立，可以求出m的特值，但是这里的m值并不是真的flag的明文

因为m^14足够大，这里仅仅是个模数，可以理解为

依旧需要爆破k，如果flag的长度比较短，例如

那么很快可以爆破出来，但是事实上，题目的格式都是

EIS`{`MD5(…..)`}`

估计一时半会儿出不来了



## 灵感乍现

在非常难受的情况下，学长给了我一些点播，我们刚才的做法，完全是对中国剩余定理使用的浪费，我们可以根据中国剩余定理得到如下3个式子

[![](https://p4.ssl.qhimg.com/t01a5bd5542843e0b34.png)](https://p4.ssl.qhimg.com/t01a5bd5542843e0b34.png)

即模数分解，这样依旧可以计算出特解m

之前我们到这里为止，开始了爆破，无果而终。

那之前为什么我们不把现在这个局面当做

[![](https://p5.ssl.qhimg.com/t0177389aa993243902.png)](https://p5.ssl.qhimg.com/t0177389aa993243902.png)

这样一个问题去解决呢？

这里的c我们已经求得，n1也是已知的，并且可以被分解，公钥e=14

因为这样无济于事，e依旧和phi(n1)有公约数。

那有没有办法换个模数呢，让phi与e互素

这里就是这道题的有趣之处:

我们可以将后2个式子合并

[![](https://p2.ssl.qhimg.com/t0152a6fc239d38b7b5.png)](https://p2.ssl.qhimg.com/t0152a6fc239d38b7b5.png)

（注：为什么可以合并呢？）

我们可以这样理解

[![](https://p3.ssl.qhimg.com/t01cfe1d6d086356785.png)](https://p3.ssl.qhimg.com/t01cfe1d6d086356785.png)

两边同时模q1q2，即可得到合并后结果

所以我们现在有等式

[![](https://p4.ssl.qhimg.com/t01af147a1e7f486447.png)](https://p4.ssl.qhimg.com/t01af147a1e7f486447.png)

我们可以把他当做一个新的RSA题目：



## 水到渠成

那么这样一看，就是一个非常简单的RSA题目了

当我们兴致勃勃去求逆元私钥d时，又发现

[![](https://p4.ssl.qhimg.com/t012e003d717bf037e7.png)](https://p4.ssl.qhimg.com/t012e003d717bf037e7.png)

这里的e和phi又不是互素的，有公约数2，乍一看非常头疼

实际上，这里的公约数2和14比实在太小了，所以我们可以直接破解：

按照之前的思路

[![](https://p0.ssl.qhimg.com/t01bc2dea4a56ff502e.png)](https://p0.ssl.qhimg.com/t01bc2dea4a56ff502e.png)

2d可以通过7的逆元求得，由于2次方太小，所以直接对m开方即可

完整脚本如下

[![](https://p4.ssl.qhimg.com/t01f6aa16f56f0d7b27.png)](https://p4.ssl.qhimg.com/t01f6aa16f56f0d7b27.png)



## 后记

当我们的公钥与phi不互素时，不仅有Rabin Attack解法了，这道题对中国剩余定理的灵活运用非常有趣XD

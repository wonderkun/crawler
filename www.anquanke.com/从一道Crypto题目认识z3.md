> 原文链接: https://www.anquanke.com//post/id/156915 


# 从一道Crypto题目认识z3


                                阅读量   
                                **163464**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t019ecc6d4c43e9bc0d.jpg)](https://p2.ssl.qhimg.com/t019ecc6d4c43e9bc0d.jpg)

## 前言

最近在看密码学的题目，一直听说过Z3的强大，今天终于体会了一次，于是有了这篇文章记录一下。



## 题干分析

题目直接给出了密文生成文本：

```
#!/usr/bin/env python3
import sympy
import json

m = sympy.randprime(2**257, 2**258)
M = sympy.randprime(2**257, 2**258)
a, b, c = [(sympy.randprime(2**256, 2**257) % m) for _ in range(3)]

x = (a + b * 3) % m
y = (b - c * 5) % m
z = (a + c * 8) % m

flag = int(open('flag', 'rb').read().strip().hex(), 16)
p = pow(flag, a, M)
q = pow(flag, b, M)

json.dump(`{` key: globals()[key] for key in "Mmxyzpq" `}`, open('crypted', 'w'))
```

题目的意思很简单：<br>
1.生成两个随机大素数m,M<br>
2.利用m再生成3个随机大数a,b,c<br>
3.再利用a,b,c,m生成3个随机大数x,y,z<br>
4.类RSA，将flag用公钥a加密，模数为M<br>
5.类RSA，将flag用公钥b加密，模数为M<br>
（注：这里不准确，并不是真RSA，说公钥和模数是方便类比）<br>
然后我们已知的信息为

```
`{`
"p": 240670121804208978394996710730839069728700956824706945984819015371493837551238, 
"q": 63385828825643452682833619835670889340533854879683013984056508942989973395315, 
"M": 349579051431173103963525574908108980776346966102045838681986112083541754544269, 
"z": 213932962252915797768584248464896200082707350140827098890648372492180142394587, 
"m": 282832747915637398142431587525135167098126503327259369230840635687863475396299, 
"x": 254732859357467931957861825273244795556693016657393159194417526480484204095858, 
"y": 261877836792399836452074575192123520294695871579540257591169122727176542734080
`}`
```

所以想解决这个问题的关键点应该在于a和b，毕竟其他的信息都给出了，除了a和b



## 解题思考（1）

如果我们得到了a和b，应该如何解决这道题呢？<br>
乍一看，很困难，两个密文p和q都是利用类RSA的算法得到的，而M是大素数，强行突破肯定不容易<br>
但这里讲到RSA，相信大家都知道RSA的共模攻击，那这里的题目是不是很相似呢？<br>
我们先看看什么是RSA共模攻击：<br>
这里简单给大家推导一下，如果RSA不知道是什么的话，建议先谷歌学一下概念<br>
首先是基本条件，我们有：<br>

```
c_1 equiv m^`{`e_1`}` text`{` `}` mod text`{` `}` n
c_2 equiv m^`{`e_2`}` text`{` `}` mod text`{` `}` n
gcd(e1,e2) = 1
```

那么根据贝祖等式:<br>

```
ax+by = gcd(a,b) = d
```

我们一定可以得到<br>

```
e1s1+e2s2 = 1
```

那么我们将最初的两个等式进行变形<br>

```
c_1^`{`s_1`}` equiv m^`{`e_1s_1`}` text`{` `}` mod text`{` `}` n
c_2^`{`s_2`}` equiv m^`{`e_2s_2`}` text`{` `}` mod text`{` `}` n
```

我们将其相乘<br>`c_1^`{`s_1`}`c_2^`{`s_2`}` text`{` `}` mod text`{` `}` n equiv m^`{`e_1s_1+e_2s_2`}` text`{` `}` mod text`{` `}` n`

则得到<br>

```
c_1^`{`s_1`}`c_2^`{`s_2`}` text`{` `}` mod text`{` `}` n equiv m^`{`1`}` text`{` `}` mod text`{` `}` n
```

到此，我们可以在不知道私钥的情况下，得到明文<br>
我们再回到这道题目里<br>

```
p equiv flag^`{`a`}` text`{` `}` mod text`{` `}` M
q equiv flag^`{`b`}` text`{` `}` mod text`{` `}` M
```

我们同样可以得到<br>

```
p^`{`s1`}`q^`{`s2`}` text`{` `}` mod text`{` `}` M equiv flag^`{`as_1+bs_2`}` text`{` `}` mod text`{` `}` M
```

又根据贝祖等式<br>

```
ax+by = gcd(a,b) = d
```

我们能有结果为<br>

```
p^`{`s1`}`q^`{`s2`}` text`{` `}` mod text`{` `}` M equiv flag^`{`d`}` text`{` `}` mod text`{` `}` M
d = gcd(a,b)
```

故此我们又得到一个隐形的约束条件：<br>

```
gcd(a,b)=1
```

<br>

## 解题思考（2）

我们如何求出a和b？<br>
我们有如下约束条件

```
a, b, c = [(sympy.randprime(2**256, 2**257) % m) for _ in range(3)]
x = (a + b * 3) % m
y = (b - c * 5) % m
z = (a + c * 8) % m
```

此时，我们知道x,y,z,m<br>
按照道理说，这里的约束条件，在不做任何思考的条件下，我们可以用如下方法爆破出来

```
z=213932962252915797768584248464896200082707350140827098890648372492180142394587
m=282832747915637398142431587525135167098126503327259369230840635687863475396299
x=254732859357467931957861825273244795556693016657393159194417526480484204095858
y=261877836792399836452074575192123520294695871579540257591169122727176542734080

for a in range(0,m):
    for b in range(0,m):
        for c in range(0,m):
            if x == (a + b * 3) % m and y == (b - c * 5) % m and z == (a + c * 8) % m and gcd(a,b)=1:
                print a,b,c
```

但是这显然是一种极其不理智的做法，因为解题概率极低<br>
这里就要用到一个神奇了：`SMT约束求解器Z3`



## Z3快速入门

### <a class="reference-link" name="z3%E5%AE%89%E8%A3%85"></a>z3安装

```
sudo pip install z3-solver
```

即可安装成功

### <a class="reference-link" name="%E7%AE%80%E5%8D%95%E4%BB%8B%E7%BB%8D"></a>简单介绍

我们看这样一个三元一次方程组的问题<br><br>
begin`{`cases`}`<br>
y=2<em>x-7<br>
5</em>x+3**y+2**z=3<br>
3*x+z=7<br>
end`{`cases`}`<br><br>
那么我们如何利用z3约束迅速求解呢？<br>
脚本如下

```
from z3 import *

x = Int('x')
y = Int('y')
z = Int('z')
s = Solver()
s.add(y==2*x-7)
s.add(5*x+3*y+2*z==3)
s.add(3*x+z==7)
print s.check()
print s.model()
```

可以轻松得到结果

```
sat
[x = 2, z = 1, y = -3]
[Finished in 0.3s]
```

这里简单解释一下

```
x = Int('x')
y = Int('y')
z = Int('z')
```

用于定于类型，包括整数、浮点数、BitVector、数组等<br>
然后是

```
s = Solver()
```

用Solver()创建求解器<br>
紧接着

```
s.add(y==2*x-7)
s.add(5*x+3*y+2*z==3)
s.add(3*x+z==7)
```

我们使用add()为变量之间增加约束条件<br>
最后

```
print s.check()
print s.model()
```

使用check()检查约束条件是否ok，并使用model()列出求解结果<br>
这里再给出更多python z3 api文档

```
http://z3prover.github.io/api/html/namespacez3py.html
```



## 求解step1

现在有了z3这样强大的约束求解器，我们可以尝试计算出a,b了<br>
我们有约束条件<br>

```
begin`{`cases`}`
x=(a + b 3) text`{` `}` mod text`{` `}` m
y=(b - c 5) text`{` `}` mod text`{` `}` m
z=(a + c * 8) text`{` `}` mod text`{` `}` m
gcd(a,b)=1
end`{`cases`}`
```

以及

```
a, b, c = [(sympy.randprime(2**256, 2**257) % m) for _ in range(3)]
```

这样一来，我们可以写出相应的约束解决脚本

```
from z3 import *
from primefac import *

z=213932962252915797768584248464896200082707350140827098890648372492180142394587
m=282832747915637398142431587525135167098126503327259369230840635687863475396299
x=254732859357467931957861825273244795556693016657393159194417526480484204095858
y=261877836792399836452074575192123520294695871579540257591169122727176542734080

a, b, c = BitVecs('a b c', 262)
s = Solver()
s.add(UGT(a, pow(2, 256, m)))
s.add(ULT(a, pow(2, 257, m)))
s.add(UGT(b, pow(2, 256, m)))
s.add(ULT(b, pow(2, 257, m)))
s.add(UGT(c, pow(2, 256, m)))
s.add(ULT(c, pow(2, 257, m)))
s.add(x == (a + b * 3) % m)
s.add(y == (b - c * 5) % m)
s.add(z == (a + c * 8) % m)
while s.check() == sat:
    A,B= s.model()[a].as_long(),s.model()[b].as_long()
    if gcd(A,B) == 1:
        print A,B
        break
```

这里有几点申明一下：<br>
1.这里使用的是BitVecs，而不是Int，因为类型为 Int（注意这里的 Int 可不是 C/C++ 里面包含上下界的 int，Z3 中的 Int 对应的就是数学中的整数，Z3 中的 BitVector 才对应到 C/C++ 中的 int），这样我们才能实现一些无符号和有符号二进制运算<br>
2.关于`a, b, c = BitVecs('a b c', 262)`的范围选262的原因如下<br>
我们在计算中有一步

```
a + c * 8
```

这应该是在运算中可能生成的最大值，而我们知道

```
a, b, c = [(sympy.randprime(2**256, 2**257) % m) for _ in range(3)]
```

所以这里我们假设a和c都是`2**257`<br>
估计极限最大值为

```
print len(bin(pow(2,257)*9)[2:])
```

发现是261bit<br>
故此我们选择262bit就不会溢出，导致check()无法通过<br>
3.由于是约束条件，这里可能出现多组值，而根据之前我们的推算，我们需要gcd(a,b)=1，所以这一点加入约束中<br>
运行脚本后，我们可以得到一组值：

```
a = 176268455401080975226023429120782206814426280508931609844850047979724152864469
b = 214709966595887251005567190400910974312839914267660095937082916625495667341329
```



## 求解step2

这里根据之前我们推导出的公式：<br><br>

```
flag^`{`1`}` text`{` `}` mod text`{` `}` M equiv p^`{`s1`}`*q^`{`s2`}` text`{` `}` mod text`{` `}` M
```

可以得到flag的脚本为：

```
import primefac
import libnum

M=349579051431173103963525574908108980776346966102045838681986112083541754544269
p=240670121804208978394996710730839069728700956824706945984819015371493837551238
q=63385828825643452682833619835670889340533854879683013984056508942989973395315
a=176268455401080975226023429120782206814426280508931609844850047979724152864469
b=214709966595887251005567190400910974312839914267660095937082916625495667341329
s1,s2,tmp = libnum.xgcd(a, b)
if s1&lt;0:
    s1 = - s1
    p = primefac.modinv(p, M)
    if p&lt;0:
        p+=M
elif s2&lt;0:
    s2 = - s2
    q = primefac.modinv(q, M)
    if q&lt;0:
        q+=M
m=(pow(p,s1,M)*pow(q,s2,M)) % M
print libnum.n2s(m)
```

注：这里s1或者s2会有一个为负数，这里的负数不是负值，是逆元的意思<br>
运行即可得到flag

```
FLAG`{`Math is simple, right? OwO`}`
```



## 后记

从这个题重温了不少数论的相关知识，以及一些优雅的crypto库，还算对得起数论老师了（逃）

<a class="reference-link" name="%E5%8F%82%E8%80%83%E9%93%BE%E6%8E%A5"></a>**参考链接**

[https://zhuanlan.zhihu.com/p/30548907](https://zhuanlan.zhihu.com/p/30548907)<br>[https://www.cnblogs.com/ZHijack/p/9001860.html](https://www.cnblogs.com/ZHijack/p/9001860.html)<br><script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=default"></script>

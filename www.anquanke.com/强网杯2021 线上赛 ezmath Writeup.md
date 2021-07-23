> 原文链接: https://www.anquanke.com//post/id/244422 


# 强网杯2021 线上赛 ezmath Writeup


                                阅读量   
                                **101856**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t01ce81c9afa988e1c2.jpg)](https://p0.ssl.qhimg.com/t01ce81c9afa988e1c2.jpg)



题目思路很新颖，需要通过分析代码理解背后的数学公式

## 比赛期间的分析

ida逆向，发现init_array有自修改

主要函数：

sub_1301：

```
double __fastcall sub_1301(double x)
`{`
  int i; // [rsp+Ch] [rbp-1Ch]
  double power; // [rsp+10h] [rbp-18h]
  double sum; // [rsp+18h] [rbp-10h]
  double factorial; // [rsp+20h] [rbp-8h]

  power = 1.0;
  sum = 1.0;
  factorial = 1.0;
  for ( i = 1; i &lt;= 8225; ++i )
  `{`
    power = power * x;
    factorial = (double)i * factorial;
    sum = power / factorial + sum;
  `}`
  return power * sum;
`}`
```

[![](https://p2.ssl.qhimg.com/t01ede5e0ed3d64a1b0.bmp)](https://p2.ssl.qhimg.com/t01ede5e0ed3d64a1b0.bmp)

sub_11C9：

```
double __fastcall sub_11C9(double (__fastcall *f)(double), double a, double b)
`{`
  double v4; // [rsp+0h] [rbp-40h]
  int i; // [rsp+20h] [rbp-20h]
  double v7; // [rsp+28h] [rbp-18h]
  double v8; // [rsp+30h] [rbp-10h]
  double delta; // [rsp+38h] [rbp-8h]

  delta = (b - a) / (double)1000;
  v7 = f(delta / 2.0 + a);
  v8 = 0.0;
  for ( i = 1; i &lt; 1000; ++i )
  `{`
    v7 = f(delta / 2.0 + (double)i * delta + a) + v7;
    v8 = f((double)i * delta + a) + v8;
  `}`
  v4 = 4.0 * v7 + f(a) + v8 + v8;
  return (f(b) + v4) * delta / 6.0;
`}`
```

辛普森积分公式<br>
（[https://baike.baidu.com/item/%E8%BE%9B%E6%99%AE%E6%A3%AE%E7%A7%AF%E5%88%86%E6%B3%95](https://baike.baidu.com/item/%E8%BE%9B%E6%99%AE%E6%A3%AE%E7%A7%AF%E5%88%86%E6%B3%95)）

sub_13F3：

```
double __fastcall sub_13F3(int n)
`{`
  int i; // [rsp+8h] [rbp-Ch]
  double v; // [rsp+Ch] [rbp-8h]

  v = 0.2021;
  for ( i = 0x2021; i &lt; n; ++i )
    v = 2.718281828459045 - (double)i * v;
  return v;
`}`
```

初始的0.2021会被 init_array 中的 sub_1391 修改为`sub_11C9(sub_1301, 0.0, 1.0)`，理论上应等于：[![](https://p0.ssl.qhimg.com/t0159ae8f7ceb78496f.bmp)](https://p0.ssl.qhimg.com/t0159ae8f7ceb78496f.bmp)（调试发现实际上是0.0004829108052495089）

由分部积分公式可得：[![](https://p1.ssl.qhimg.com/t01d89b3a1e0333d9f7.bmp)](https://p1.ssl.qhimg.com/t01d89b3a1e0333d9f7.bmp)

记[![](https://p4.ssl.qhimg.com/t016b0ab4980431e082.bmp)](https://p4.ssl.qhimg.com/t016b0ab4980431e082.bmp)，上式即为[![](https://p1.ssl.qhimg.com/t013be0452121d8157b.bmp)](https://p1.ssl.qhimg.com/t013be0452121d8157b.bmp)，与sub_13F3的逻辑一致，所以`sub_13F3(n)`实质上是在计算[![](https://p5.ssl.qhimg.com/t01c6a03e51b1e373f5.bmp)](https://p5.ssl.qhimg.com/t01c6a03e51b1e373f5.bmp)

（这里的问题在于浮点数计算精度不够，中途出现了inf，导致事实上永远无法计算出最终的结果）

main

```
__int64 __fastcall main(int a1, char **a2, char **a3)
`{`
  __int64 result; // rax
  int i; // [rsp+Ch] [rbp-44h]
  char s[8]; // [rsp+20h] [rbp-30h] BYREF
  __int64 v6; // [rsp+28h] [rbp-28h]
  __int64 v7; // [rsp+30h] [rbp-20h]
  __int64 v8; // [rsp+38h] [rbp-18h]
  __int64 v9; // [rsp+40h] [rbp-10h]
  unsigned __int64 v10; // [rsp+48h] [rbp-8h]

  v10 = __readfsqword(0x28u);
  *(_QWORD *)s = 0LL;
  v6 = 0LL;
  v7 = 0LL;
  v8 = 0LL;
  v9 = 0LL;
  __isoc99_scanf("%39s", s);
  if ( strlen(s) == 38 )
  `{`
    for ( i = 0; i &lt;= 37; i += 2 )
    `{`
      if ( dbl_4020[i / 2] != sub_13F3(*(unsigned __int16 *)&amp;s[i]) )
        goto LABEL_2;
    `}`
    puts("correct");
    result = 0LL;
  `}`
  else
  `{`
LABEL_2:
    puts("wrong");
    result = 0LL;
  `}`
  return result;
`}`
```

main函数把flag每两字节转换为一个整数`n`，计算`sub_13F3(n)`，然后与目标常量作比较。

注意到[![](https://p1.ssl.qhimg.com/t01c6a03e51b1e373f5.bmp)](https://p1.ssl.qhimg.com/t01c6a03e51b1e373f5.bmp) 的值随 `n`增大是递减的，在保证定积分的计算精度的前提下，对每个目标常量二分查找`n`即可

（计算方法参考：[https://blog.csdn.net/Dennis_BIRL/article/details/53350414](https://blog.csdn.net/Dennis_BIRL/article/details/53350414)）

```
from math import e

def p16(n):
    return n.to_bytes(2, "little")

global_cache = [None]*0x10000
v = 0.00004147642328261315    # n=0x10000
for i in range(0x10000, 0, -1):
    lastv = v
    v = (e-v)/i
    assert v &gt; lastv
    global_cache[i-1] = v

def calc(n):
    global global_cache
    assert n &lt; 0x10000
    if global_cache[n]:
        return global_cache[n]
    assert 0

def bsearch(d):
    a = 0x2020
    fa = calc(a)
    b = 0x7f7f
    fb = calc(b)
    while True:
        mid = (a+b)//2
        assert a &lt;= mid &lt;= b
        if mid == a:
            assert fa &gt;= d &gt;= fb
            return a if fa-d &lt; d-fb else b
        fmid = calc(mid)
        assert fa &gt;= fmid &gt;= fb
        if fmid &gt; d:
            a = mid
            fa = fmid
        else:
            b = mid
            fb = fmid

# dbl_4020
numbers = [
    0.00009794904266317233, 0.00010270456917442, 0.00009194256152777895,
    0.0001090322021913372, 0.0001112636336217534, 0.0001007442677411854,
    0.0001112636336217534, 0.0001047063607908828, 0.0001112818534005219,
    0.0001046861985862495, 0.0001112818534005219, 0.000108992856167966,
    0.0001112636336217534, 0.0001090234561758122, 0.0001113183108652088,
    0.0001006882924839248, 0.0001112590796092291, 0.0001089841164633298,
    0.00008468431512187874
]

finalnums = [bsearch(d) for d in numbers]

flag = b""
for n in finalnums:
    flag += p16(n)

print(flag)    # flag`{`saam_dim_gei_lei_jam_caa_sin_laa`}`
```

（正确的flag输入给程序却返回wrong，作为逆向题不该这样吧2333）

## 赛后分析1

看到其他队的writeup，直接用e除以最终比较的数就能直接得到flag……（这就是这题做出人数这么多的原因吗？）

尝试推导一波：

在 [![](https://p4.ssl.qhimg.com/t018cf0bb126f5b8ea4.bmp)](https://p4.ssl.qhimg.com/t018cf0bb126f5b8ea4.bmp) 时有

[![](https://p0.ssl.qhimg.com/t01ac35c795dba980e5.bmp)](https://p0.ssl.qhimg.com/t01ac35c795dba980e5.bmp)

同时乘[![](https://p2.ssl.qhimg.com/t0197e8ff87e1f5cde4.bmp)](https://p2.ssl.qhimg.com/t0197e8ff87e1f5cde4.bmp)得：

[![](https://p0.ssl.qhimg.com/t0119dfdfdabf04a74f.bmp)](https://p0.ssl.qhimg.com/t0119dfdfdabf04a74f.bmp)

计算定积分：

[![](https://p4.ssl.qhimg.com/t017c7b074e5dca15b0.bmp)](https://p4.ssl.qhimg.com/t017c7b074e5dca15b0.bmp)

记

[![](https://p5.ssl.qhimg.com/t01b2998489dd2229a5.bmp)](https://p5.ssl.qhimg.com/t01b2998489dd2229a5.bmp)

则有

[![](https://p0.ssl.qhimg.com/t01a1e432ad8c614af5.bmp)](https://p0.ssl.qhimg.com/t01a1e432ad8c614af5.bmp)

所以可以直接用e除以最终比较的数得出flag

```
from math import e

def p16(n):
    return n.to_bytes(2, "little")

# dbl_4020
numbers = [
    0.00009794904266317233, 0.00010270456917442, 0.00009194256152777895,
    0.0001090322021913372, 0.0001112636336217534, 0.0001007442677411854,
    0.0001112636336217534, 0.0001047063607908828, 0.0001112818534005219,
    0.0001046861985862495, 0.0001112818534005219, 0.000108992856167966,
    0.0001112636336217534, 0.0001090234561758122, 0.0001113183108652088,
    0.0001006882924839248, 0.0001112590796092291, 0.0001089841164633298,
    0.00008468431512187874
]

finalnums = [int(e/n)-1 for n in numbers]

flag = b""
for n in finalnums:
    flag += p16(n)

print(flag)
```

## 赛后分析2

即使没有init_array的提示，单纯根据`sub_13F3`的递推式也是可以得到积分式的<br>
已知

[![](https://p2.ssl.qhimg.com/t0115ed6204ecb477c2.bmp)](https://p2.ssl.qhimg.com/t0115ed6204ecb477c2.bmp)

两边同时除以 [![](https://p5.ssl.qhimg.com/t0153d71ecb50af0ece.bmp)](https://p5.ssl.qhimg.com/t0153d71ecb50af0ece.bmp)：

[![](https://p4.ssl.qhimg.com/t0174257cedb83ab962.bmp)](https://p4.ssl.qhimg.com/t0174257cedb83ab962.bmp)

迭代下去，得出通项公式：

[![](https://p1.ssl.qhimg.com/t01f6ae31618d0a51cf.bmp)](https://p1.ssl.qhimg.com/t01f6ae31618d0a51cf.bmp)

考虑 [![](https://p2.ssl.qhimg.com/t01f9062e236bf2b88e.bmp)](https://p2.ssl.qhimg.com/t01f9062e236bf2b88e.bmp) 带积分余项的展开式：

[![](https://p2.ssl.qhimg.com/t01e649e3dfbad49a9f.bmp)](https://p2.ssl.qhimg.com/t01e649e3dfbad49a9f.bmp)

代入 [![](https://p1.ssl.qhimg.com/t01afdab842003f0747.bmp)](https://p1.ssl.qhimg.com/t01afdab842003f0747.bmp)：

[![](https://p3.ssl.qhimg.com/t01f9efd84ab9edf182.bmp)](https://p3.ssl.qhimg.com/t01f9efd84ab9edf182.bmp)

代入到通项公式中：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0150e5fbad5006e37b.bmp)

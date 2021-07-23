> 原文链接: https://www.anquanke.com//post/id/196831 


# 无需暴破还原mt_rand()种子


                                阅读量   
                                **1235789**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者ambionics，文章来源：ambionics.io
                                <br>原文地址：[https://www.ambionics.io/blog/php-mt-rand-prediction](https://www.ambionics.io/blog/php-mt-rand-prediction)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01de21975e599af0c1.jpg)](https://p1.ssl.qhimg.com/t01de21975e599af0c1.jpg)



## 0x00 前言

在渗透测试某个老版网站时，我们碰到了很久没见过的一段代码：

```
&lt;?php
function resetPassword($email)
`{`
    [...]
    $superSecretToken = md5($email . ':' . mt_rand());
    [...]
    $this-&gt;sendEmailWithResetToken($email, $superSecretToken);
`}`
```

这里代码使用了PHP中[Mersenne Twister](https://en.wikipedia.org/wiki/Mersenne_Twister)算法生成了不可猜测的一个私密令牌。

在过去十年中，我们内部研究过PRNG（伪随机数生成器）预测的可行性，形成了一些研究文章及工具。当时有许多应用使用[`rand()`](https://www.php.net/manual/en/function.rand.php) 或者[`mt_rand()`](https://www.php.net/manual/en/function.mt-rand.php)来生成私密令牌或者密码。从密码学角度来看，这些函数并不安全，因此不应当用于加密场景。为了预测这些值，我们需要找到随机种子（seed），也就是所有随机数的源头。经过讨论后，我们认为需要获得完整的[内部状态](https://jazzy.id.au/2010/09/22/cracking_random_number_generators_part_3.html)（`mt_rand()`有624个值）或者通过[暴力破解](https://www.openwall.com/php_mt_seed/)使用这些值的种子才能实现随机数预测。

然而，有个小伙伴认为通过`mt_rand()`函数的两个输出值就能恢复出Mersenne Twister的种子，整个过程不需要任何暴破操作。然而我们找不到相应的理论支持，并且小伙伴关于这方面内容的笔记早已丢失。

经过一番探索，再结合PRNG多年以来的研究成果，我们成功完成了该任务。在本文中，我们将与大家分享具体的实现过程。



## 0x01 还原mt_rand()种子

使用`mt_rand()`生成随机数的第一个步骤是使用种子（无符号整数值）来生成包含`624`个值的状态数组。我们可以调用`mt_srand($seed)`或者在请求第一个随机数时由PHP自动帮我们完成该操作。随后，每次调用`mt_rand()`时都会用到下一个状态值，经过处理后再返回给用户。

在新版PHP（PHP7+）中，这部分逻辑位于`ext/standard/mt_rand.c`中，老版PHP（PHP5-）中对应的是`ext/standard/rand.c`。

如果获取到种子，在下一次调用`mt_srand()`之前，我们都可以预测由PRNG生成的每个数字。这种情况下，采用`mt_rand()`生成的秘密随机值就毫无秘密可言，存在明显的安全问题。

随机数生成过程包含如下3个步骤：

1、通过种子模乘运算生成初始状态数组；

2、打乱状态值，生成经过加扰处理的（scrambled）状态数组；

3、在调用`mt_rand()`时，函数返回经过修改的加扰状态值。

下面我们将介绍每个步骤涉及到的代码，描述内部原理，然后介绍如何通过输出结果获取我们所需的值。

> 备注：PHP7+稍微[修改](https://github.com/php/php-src/commit/7981a294bd2fb329d404001c369517e2953b92a6#diff-cacc151e4c9155ca59b58a62d147b912R95)了负责生成加扰状态数组的代码（参考`mt_rand.c`中关于`twist`及`twist_php`的`#define`语句），但并没有太大变化，我们还是可以在该版本中获取种子。因此，这里我们主要关注的是原始版的实现逻辑：`twist_php`。文末提供的脚本可以适用于两个版本的PHP。

### <a class="reference-link" name="%E4%BB%8E%E7%A7%8D%E5%AD%90%E5%88%B0%E5%88%9D%E5%A7%8B%E7%8A%B6%E6%80%81"></a>从种子到初始状态

```
#define MT_N (624)
#define N             MT_N                 /* length of state vector */
#define M             (397)                /* a period parameter */

static inline void php_mt_initialize(uint32_t seed, uint32_t *state)
`{`
    /* Initialize generator state with seed
       See Knuth TAOCP Vol 2, 3rd Ed, p.106 for multiplier.
       In previous versions, most significant bits (MSBs) of the seed affect
       only MSBs of the state array.  Modified 9 Jan 2002 by Makoto Matsumoto. */

    register uint32_t *s = state;
    register uint32_t *r = state;
    register int i = 1;

    *s++ = seed &amp; 0xffffffffU;
    for( ; i &lt; N; ++i ) `{`
        *s++ = ( 1812433253U * ( *r ^ (*r &gt;&gt; 30) ) + i ) &amp; 0xffffffffU;
        r++;
    `}`
`}`
```

以上代码会创建包含`624`个数值的初始状态数组。第一个状态为种子值，后面每个状态值都源自于前一个状态值。

现在如果已知其中某个状态值（比如`state[123]`），是否可以还原出最初的状态值（`state[0]`），也就是种子？

对应的python代码如下所示：

```
N = 624
M = 397

MAX = 0xffffffff

STATE_MULT = 1812433253

def php_mt_initialize(seed):
    """Creates the initial state array from a seed.
    """
    state = [None] * N
    state[0] = seed &amp; 0xffffffff;
    for i in range(1, N):
        r = state[i-1]
        state[i] = ( STATE_MULT * ( r ^ (r &gt;&gt; 30) ) + i ) &amp; MAX
    return state
```

由于这些值通过迭代操作生成，因此我们首先需要尝试根据`i`及`state[i]`的值找到`state[i-1]`。然后我们可以使用相同的操作处理`i-1`、`i-2`，最终得到`state[0]`（即种子）。以`S`表示状态，`i`的范围为`[1, 624]`，我们有如下公式：

[![](https://p4.ssl.qhimg.com/t01932f1bf157a5e85d.png)](https://p4.ssl.qhimg.com/t01932f1bf157a5e85d.png)

计算`1812433253`模（mod）`0x100000000`的模乘逆运算：

[![](https://p2.ssl.qhimg.com/t0184ca4b265d810000.png)](https://p2.ssl.qhimg.com/t0184ca4b265d810000.png)

随后计算：

[![](https://p3.ssl.qhimg.com/t01890f9a677b2f9061.png)](https://p3.ssl.qhimg.com/t01890f9a677b2f9061.png)

对应的python代码：

```
STATE_MULT_INV = 2520285293
MAX = 0xffffffff

def _undo_php_mt_initialize(s, i):
    s = (STATE_MULT_INV * (s - i)) &amp; MAX
    return s ^ s &gt;&gt; 30

def undo_php_mt_initialize(s, p):
    """From an initial state value `s` at position `p`, find out seed.
    """
    for i in range(p, 0, -1):
        s = _undo_php_mt_initialize(s, i)
    return s
```

这意味着如果我们能拿到任意初始状态值，就可以计算出其他状态值以及原始种子。

### <a class="reference-link" name="%E4%BB%8E%E5%88%9D%E5%A7%8B%E7%8A%B6%E6%80%81%E5%88%B0%E5%8A%A0%E6%89%B0%E7%8A%B6%E6%80%81"></a>从初始状态到加扰状态

```
#define hiBit(u)      ((u) &amp; 0x80000000U)  /* mask all but highest   bit of u */
#define loBit(u)      ((u) &amp; 0x00000001U)  /* mask all but lowest    bit of u */
#define loBits(u)     ((u) &amp; 0x7FFFFFFFU)  /* mask     the highest   bit of u */
#define mixBits(u, v) (hiBit(u)|loBits(v)) /* move hi bit of u to hi bit of v */

#define twist(m,u,v)  (m ^ (mixBits(u,v)&gt;&gt;1) ^ ((php_uint32)(-(php_int32)(loBit(u))) &amp; 0x9908b0dfU))

static inline void php_mt_reload(TSRMLS_D)
`{`
    /* Generate N new values in state
       Made clearer and faster by Matthew Bellew (matthew.bellew@home.com) */

    register php_uint32 *state = BG(state);
    register php_uint32 *p = state;
    register int i;

    for (i = N - M; i--; ++p)
        *p = twist(p[M], p[0], p[1]);
    for (i = M; --i; ++p)
        *p = twist(p[M-N], p[0], p[1]);
    *p = twist(p[M-N], p[0], state[0]);
    BG(left) = N;
    BG(next) = state;
`}`
```

代码通过混合值方式来加扰初始状态数组，从而得到经过加扰的一个新状态数组。前`226`（`N-M`）个值的计算方式与后面的值计算方式不同，对应的python代码如下：

```
N = 624
M = 397

def php_mt_reload(s):
    for i in range(0, N - M):
        s[i] = _twist(s[i+M], s[i], s[i+1])
    for i in range(N - M, N - 1):
        s[i] = _twist(s[i+M-N], s[i], s[i+1])

def _twist_php(m, u, v):
    """Emulates the `twist` #define.
    """
    mask = 0x9908b0df if u &amp; 1 else 0
    return m ^ (((u &amp; 0x80000000) | (v &amp; 0x7FFFFFFF)) &gt;&gt; 1) ^ mask
```

我们可以通过两个加扰状态值推测出某个初始状态值。

状态`0`及状态`227`之间存在一定联系。如果我们使用`s`来表示初始状态数组，使用`S`来表示经过加扰的新的状态数组，则有如下关系：

```
S[227] = _twist(S[227 - 227], s[227], s[228])
&lt;=&gt; S[227] = _twist(S[0], s[227], s[228])
&lt;=&gt; S[227] = S[0] ^ (((s[227] &amp; 0x80000000) | (s[228] &amp; 0x7FFFFFFF)) &gt;&gt; 1) ^ (0x9908b0df if s[227] &amp; 1 else 0)
&lt;=&gt; S[227] ^ S[0] = (((s[227] &amp; 0x80000000) | (s[228] &amp; 0x7FFFFFFF)) &gt;&gt; 1) ^ (0x9908b0df if s[227] &amp; 1 else 0)
```

从攻击者角度来看，如果我们已知`S[0]`及`S[227]`这两个经过加扰的状态值，执行异或操作后，我们可以得到关于初始状态`s[228]`的大量信息，以及`s[227]`的部分信息。如果用`X`来表示`S[227] ^ S[0]`，则有：

1、由于异或表达式左侧部分右移，因此其`MSB`（most significant bit，最高有效位）始终为空。并且由于`MSB(0x9908b0df)`不为零，因此`X`的`MSB`只由右侧部分（即掩码部分）所决定。由此我们可得：`MSB(X) = LSB(s[227])`，如果`X`中存在掩码，我们可以直接移除；

2、然后，`BIT(s[227], 31) = BIT(X, 30)`；

3、其他值来自于`s[228]`对应的bit，即从`30`到`1`的bit位。

总结一下，现在我们拥有如下信息：

1、初始状态值`s[227]`的`MSB`及`LSB`；

2、初始状态值`s[228]`中从`30`到`1`的bit位。

因此，`s[228]`对应4个可取的值。然而由于我们也知道`s[227]`的某些bit，因此可以从这4个可选值计算对应的`s[227]`，验证计算出的`s[227]`的`LSB`及`MSB`是否匹配我们已知的值。此外，我们还能计算出可选`s[228]`状态值所对应的种子，然后利用该种子重新生成状态值，检查其是否与`S[0]`匹配。对应的python代码如下：

```
def undo_php_mt_reload(S000, S227):
    # m S000
    # u S227
    # v S228
    X = S000 ^ S227

    # This means the mask was applied, and as such that S227's LSB is 1
    s22X_0 = bv(X, 31)
    # remove mask if present
    if s22X_0:
        X ^= 0x9908b0df

    # Another easy guess
    s227_31 = bv(X, 30)
    # remove bit if present
    if s227_31:
        X ^= 1 &lt;&lt; 30

    # We're missing bit 0 and bit 31 here, so we have to try every possibility
    s228_1_30 = (X &lt;&lt; 1)
    for s228_0 in range(2):
        for s228_31 in range(2):
            s228 = s228_0 | s228_31 &lt;&lt; 31 | s228_1_30

            # Check if the results are consistent with the known bits of s227
            s227 = _undo_php_mt_initialize(s228, 228)
            if bv(s227, 0) != s22X_0:
                continue
            if bv(s227, 31) != s227_31:
                continue

            # Check if the guessed seed yields S000 as its first scrambled state
            rand = undo_php_mt_initialize(s228, 228)
            state = php_mt_initialize(rand)
            php_mt_reload(state)

            if not S000 == state[0]:
                continue

            return rand
    return None
```

为了推测原始种子，我们用到了经过加扰处理的`S[0]`及`S[227]`之间的关联性。根据分析可知，这种关联性适用于间隔`226`个值的两端值。因此，只要知道两个状态值（如`S[i]`及`S[i+227]`），以及这两个值对应的偏移量`i`，我们就能还原出种子。

现在我们可以分析`mt_rand()` PRNG的最后一个步骤。

### 从加扰状态值到`mt_rand()`输出

当我们调用`mt_rand()`时，PHP会使用经过加扰的状态数组中的某个值，经过一番处理后返回给调用方。

```
PHP_FUNCTION(mt_rand)
`{`
    zend_long min;
    zend_long max;
    int argc = ZEND_NUM_ARGS();

    if (argc == 0) `{`
        // genrand_int31 in mt19937ar.c performs a right shift
        RETURN_LONG(php_mt_rand() &gt;&gt; 1);
    `}`
    ...
`}`

PHPAPI uint32_t php_mt_rand(void)
`{`
    /* Pull a 32-bit integer from the generator state
       Every other access function simply transforms the numbers extracted here */

    register uint32_t s1;

    if (UNEXPECTED(!BG(mt_rand_is_seeded))) `{`
        php_mt_srand(GENERATE_SEED());
    `}`

    if (BG(left) == 0) `{`
        php_mt_reload();
    `}`
    --BG(left);

    s1 = *BG(next)++; // PICKS NEXT SCRAMBLED STATE VALUE
    s1 ^= (s1 &gt;&gt; 11);
    s1 ^= (s1 &lt;&lt;  7) &amp; 0x9d2c5680U;
    s1 ^= (s1 &lt;&lt; 15) &amp; 0xefc60000U;
    return ( s1 ^ (s1 &gt;&gt; 18) );
`}`
```

`s1`代表经过加扰处理的状态值，在`php_mt_rand()`中执行4次操作后，`mt_rand()`将结果值右移1位。这样最后1个操作不可逆，但前4个操作可逆。

因此我们可以使用如下代码逆向这些转换操作：

```
def undo_php_mt_rand(s1):
    """Retrieves the merged state value from the value sent to the user.
    """
    s1 ^= (s1 &gt;&gt; 18)
    s1 ^= (s1 &lt;&lt; 15) &amp; 0xefc60000

    s1 = undo_lshift_xor_mask(s1, 7, 0x9d2c5680)

    s1 ^= s1 &gt;&gt; 11
    s1 ^= s1 &gt;&gt; 22

    return s1

def undo_lshift_xor_mask(v, shift, mask):
    """r s.t. v = r ^ ((r &lt;&lt; shift) &amp; mask)
    """
    for i in range(shift, 32, shift):
        v ^= (bits(v, i - shift, shift) &amp; bits(mask, i, shift)) &lt;&lt; i
    return v
```

拿到`mt_rand()`输出结果，我们可以猜测其`LSB`值，得到2个可能匹配的加扰状态值：其中1个对应的`LSB`值为`0`，另一个为`1`。

### <a class="reference-link" name="%E6%AD%A5%E9%AA%A4%E6%B1%87%E6%80%BB"></a>步骤汇总

下面将这几个还原步骤汇总起来：

1、从`mt_rand()`获取2个值：`R000`以及`R227`，中间间隔`226`个值；此外还需知道`R000`之前已生成的值的个数（用`i`表示）；

2、根据这些值算出加扰状态值；

3、异或这些状态值，推测出原始的状态值（`s228`）；

4、根据`s228`，推测出`s0`，获取种子。

```
def main(_R000, _R227, offset):
    # Both were &gt;&gt; 1, so the leftmost byte is unknown
    _R000 &lt;&lt;= 1
    _R227 &lt;&lt;= 1

    for R000_0 in range(2):
        for R227_0 in range(2):
            R000 = _R000 | R000_0
            R227 = _R227 | R227_0
            S000 = undo_php_mt_rand(R000)
            S227 = undo_php_mt_rand(R227)
            seed = undo_php_mt_reload(S000, S227, offset)
            if seed:
                print(seed)
```

由于我们缺少`R000`及`R227`的`LSB`信息，因此我们需要针对每种情况进行测试。通常情况下，4种组合中只有1种能生成种子，其他组合无法获得有效值。

输出结果如下：

[![](https://p0.ssl.qhimg.com/t01f23b8d0b94a96475.png)](https://p0.ssl.qhimg.com/t01f23b8d0b94a96475.png)

大家可以访问我们的[GitHub](https://github.com/ambionics/mt_rand-reverse)下载完整python代码。



## 0x02 总结

根据本文分析，只要给定间隔`226`个值的两个`mt_rand()`输出结果，我们就有可能计算出原始种子，无需暴力破解，因此也能计算出之前或者之后的`mt_rand()`输出值，成功解密PRNG。

> 原文链接: https://www.anquanke.com//post/id/231799 


# 在NodeJS/Chrome/chromium中预测Math.random()


                                阅读量   
                                **144384**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01be1c4df330ae7a55.jpg)](https://p1.ssl.qhimg.com/t01be1c4df330ae7a55.jpg)



## 它不安全！

在MDN中，有这样一段话

> `Math.random()` **不能**提供像密码一样安全的随机数字。不要使用它们来处理有关安全的事情。使用Web Crypto API 来代替, 和更精确的[`window.crypto.getRandomValues()`](https://developer.mozilla.org/zh-CN/docs/Web/API/RandomSource/getRandomValues) 方法.

在各种JavaScript环境中，`Math.random()`这个函数都是不安全的。这其实是因为，它们同时应用了一种名叫 `XorShift128+`的算法。V8从`v4.9.41.0`开始把随机数算法从`MWC1616`切换为`XorShift128+`（[博文](https://v8.dev/blog/math-random)），虽然这种算法在各项指标上优于原先的算法，但这依旧没有改变其不安全的本质。

因为根据其算法，我们可以很轻松的根据多个连续的生成值，获取生成器当前的状态，并以此推导出后续的值。



## 它不安全？

NodeJS进来逐渐成为流行的后端语言之一，它的JavaScript解释器使用了v8，而chrome/chromium也同样使用了v8，这就导致我们对于v8随机数生成的探究可以同时应用于NodeJS/Chrome/Chromium平台。

```
&lt;div&gt;
&lt;img src="http://static.nodejs.cn/_static/img/logo.svg" width="32%"&gt;
&lt;img src="https://v8.dev/_img/v8.svg" width="33%"&gt;
&lt;img src="https://upload.wikimedia.org/wikipedia/commons/5/5f/Chromium_11_Logo.svg" width="32%"&gt;
&lt;/div&gt;
```

接下来让我们来分析一下v8中对于Math.random()的实现。我们从上往下追踪`Math.random()`的调用
<li>添加函数签名：这里向全局注册了`random`函数[https://chromium.googlesource.com/v8/v8/+/refs/heads/master/src/init/bootstrapper.cc#2754](https://chromium.googlesource.com/v8/v8/+/refs/heads/master/src/init/bootstrapper.cc#2754)
<pre><code class="lang-cpp hljs">SimpleInstallFunction(isolate_, math, "random", Builtins::kMathRandom, 0, true);
</code></pre>
</li>
<li>torque申明：v8使用一种他们自己发明的语言`torque`来完成内置函数的申明（他们称这种语言非常简单的帮助实现了ECMAScript的标准，然而你还需要为这一套语言单独编译一套额外的工具，真有你的啊[https://chromium.googlesource.com/v8/v8/+/refs/heads/master/src/builtins/math.tq#439](https://chromium.googlesource.com/v8/v8/+/refs/heads/master/src/builtins/math.tq#439)
<pre><code class="lang-cpp hljs">// ES6 #sec-math.random
extern macro RefillMathRandom(NativeContext): Smi;

transitioning javascript builtin
MathRandom(js-implicit context: NativeContext, receiver: JSAny)(): Number `{`
  let smiIndex: Smi = *NativeContextSlot(ContextSlot::MATH_RANDOM_INDEX_INDEX);
  if (smiIndex == 0) `{`
    // refill math random.
    smiIndex = RefillMathRandom(context); // 重新生成
  `}`
  const newSmiIndex: Smi = smiIndex - 1; // 取下一个index(其实是上一个)
  *NativeContextSlot(ContextSlot::MATH_RANDOM_INDEX_INDEX) = newSmiIndex;

  const array: FixedDoubleArray =
      *NativeContextSlot(ContextSlot::MATH_RANDOM_CACHE_INDEX); // 取缓存
  const random: float64 =
      array.floats[Convert&lt;intptr&gt;(newSmiIndex)].ValueUnsafeAssumeNotHole(); // 从缓存中取
  return AllocateHeapNumberWithValue(random);
`}`
</code></pre>
</li>
<li>cache生成：v8中随机数并不是当场生成的，它会在环境初始化或者缓存的随机数用光的时候统一生成。（程序局部性的最佳实践，点赞[https://chromium.googlesource.com/v8/v8/+/refs/heads/master/src/numbers/math-random.cc#35](https://chromium.googlesource.com/v8/v8/+/refs/heads/master/src/numbers/math-random.cc#35)
<pre><code class="lang-cpp hljs">Address MathRandom::RefillCache(Isolate* isolate, Address raw_native_context) `{`
  // 省略一部分
  FixedDoubleArray cache =
      FixedDoubleArray::cast(native_context.math_random_cache());
  // Create random numbers.
  for (int i = 0; i &lt; kCacheSize; i++) `{` // kCacheSize = 64 in math-random.h
    // Generate random numbers using xorshift128+.
    base::RandomNumberGenerator::XorShift128(&amp;state.s0, &amp;state.s1);
    cache.set(i, base::RandomNumberGenerator::ToDouble(state.s0));
  `}`
  pod.set(0, state);

  Smi new_index = Smi::FromInt(kCacheSize);
  native_context.set_math_random_index(new_index);
  return new_index.ptr();
`}`
</code></pre>
</li>
<li>XorShift128 和转浮点：随机数生成使用XorShift128+算法，`uint64`转`浮点`使用 `(state0 &gt;&gt; 12) | 0x3FF0000000000000`（其实就是`state0 &gt;&gt; 12` 作为浮点数的尾数[https://chromium.googlesource.com/v8/v8/+/refs/heads/master/src/base/utils/random-number-generator.h#111](https://chromium.googlesource.com/v8/v8/+/refs/heads/master/src/base/utils/random-number-generator.h#111)
<pre><code class="lang-cpp hljs">// Static and exposed for external use.
static inline double ToDouble(uint64_t state0) `{`
  // Exponent for double values for [1.0 .. 2.0)
  static const uint64_t kExponentBits = uint64_t`{`0x3FF0000000000000`}`;
  uint64_t random = (state0 &gt;&gt; 12) | kExponentBits;
  return bit_cast&lt;double&gt;(random) - 1;
`}`

// Static and exposed for external use.
static inline void XorShift128(uint64_t* state0, uint64_t* state1) `{`
  uint64_t s1 = *state0;
  uint64_t s0 = *state1;
  *state0 = s0;
  s1 ^= s1 &lt;&lt; 23;
  s1 ^= s1 &gt;&gt; 17;
  s1 ^= s0;
  s1 ^= s0 &gt;&gt; 26;
  *state1 = s1;
`}`
</code></pre>
</li>
从流程中，我们可以看出v8会在开始的时候先初始化按顺序生成一个随机数cache，大小为64，然后一次从后往前取，取完再重新生成一遍。随机数的生成依据 `Xor Shift 128` 算法。我们用python大致实现一下

```
import struct
from typing import Any
from sympy import solve
from z3 import BitVecs, Or, Solver, sat, LShR, BitVecRef

MASK = 0xFFFFFFFFFFFFFFFF

class XorShift128:
    def __init__(self, state0: int, state1: int) -&gt; None:
        self.state0 = state0
        self.state1 = state1
    def current_double(self) -&gt; float:
        double_bits = (self.state0 &gt;&gt; 12) | 0x3FF0000000000000
        double = struct.unpack('d', struct.pack('&lt;Q', double_bits))[0] - 1
        return double
    def next(self):
        s1 = self.state0
        s0 = self.state1
        s1 ^= (s1 &lt;&lt; 23) &amp; MASK
        s1 ^= (s1 &gt;&gt; 17) &amp; MASK
        s1 ^= s0 &amp; MASK
        s1 ^= (s0 &gt;&gt; 26) &amp; MASK
        self.state0 = self.state1 &amp; MASK
        self.state1 = s1 &amp; MASK
    def last(self):
        s1 = self.state0
        s0 = self.state1
        s0 ^= (s1 &gt;&gt; 26) &amp; MASK
        s0 ^= s1 &amp; MASK
        s0 ^= ((s0 &gt;&gt; 17) ^ (s0 &gt;&gt; 34) ^ (s0 &gt;&gt; 51)) &amp; MASK
        s0 ^= ((s0 &lt;&lt; 23) ^ (s0 &lt;&lt; 46)) &amp; MASK
        self.state0 = self.state0 &amp; MASK
        self.state1 = s0 &amp; MASK
    def next_double(self):
        self.next()
        return self.current_double()
    def last_double(self):
        self.last()
        return self.current_double()
```

所以我们可以得出这样一个结论

```
random_numbers = [n0, n1, n2, n3, n4, n5] # generated by `Array.from(`{`length:5`}`).map(Math.random)`
# 内部生成的顺序其实是 n5, n4, n3, n2, n1, n0
generator = XorShift128(state0, state1)
for i in random_numbers[::-1]:
    assert(generator.next_double() == i)
```

这时候，如果我们能根据上式算出`state0, state1`，我们就可以推测出下一个随机数（其实是n5的上一个，我们借助`python`的`z3`模块完成这个计算

```
class XorShift128Symbol:
    def __init__(self) -&gt; None:
        self.state0, self.state1 = BitVecs("state0 state1", 64)
        self.s0, self.s1 = self.state0, self.state1
        self.solver = Solver()
    def assert_current_double(self, num: float) -&gt; None:
        recovered = struct.unpack('&lt;Q', struct.pack('d', num + 1))[0] &amp; (MASK &gt;&gt; 12)
        self.solver.add(LShR(self.state0, 12) == recovered)
    def assert_next_double(self, num: float) -&gt; None:
        self.next()
        self.assert_current_double(num)
    def next(self):
        s1 = self.state0
        s0 = self.state1
        s1 ^= (s1 &lt;&lt; 23)
        s1 ^= LShR(s1, 17)
        s1 ^= s0
        s1 ^= LShR(s0, 26)
        self.state0 = self.state1
        self.state1 = s1
    def check(self) -&gt; Tuple[int, int]:
        if self.solver.check() == sat:
            m = self.solver.model()
            self.solver.add(Or(self.s0 != m[self.s0], self.s1 != m[self.s1]))
            if self.solver.check() == sat:
                raise Exception("multiple solution")
            s0: Any = m[self.s0]
            s1: Any = m[self.s1]
            return s0.as_long(), s1.as_long()
        else:
            raise Exception("No solution")

def solve(randoms: List[float], n: int) -&gt; List[float]:
    cracker = XorShift128Symbol()
    for i in randoms[::-1]:
        cracker.assert_next_double(i)
    s0, s1 = cracker.check()
    generator = XorShift128(s0, s1)
    return [generator.current_double(), *(generator.last_double() for i in range(n-1))]
```

我们来测试一下

```
if __name__ == "__main__":
    inp = json.loads(os.popen('node -e "console.log(JSON.stringify(Array.from(`{`length:15`}`).map(Math.random)))"').read())
    res = solve(inp[:5], 10)
    for i in range(5, 15):
        assert(res[i-5]==inp[i])
    print(inp[5:])
    print(res)
```

[![](https://p3.ssl.qhimg.com/t01fe6b03b1d97a6d59.png)](https://p3.ssl.qhimg.com/t01fe6b03b1d97a6d59.png)

芜湖，成功预测！

我们既然知道了当前随机数生成器的状态，那么当前cache中所有的数字我们也都可以知道了。这对于一个依赖于随机数的应用来说，将会带来灾难性的后果。（假设存在一个后端使用了`NodeJS`并且使用`Math.random()`的彩票应用，那么我们便可以估算一段时间内所有的结果，赢得巨大的奖项

其实在Firefox/Safari中也同样使用了这种随机数算法。只要稍微修改一下`current_double`的实现就可以。



## 它不安全。

所以，不要在有安全需要的地方使用`Math.random()`函数，如果需要一个安全的随机数生成，可以使用新的`Web Crypto API`或者 `NodeJS`的`crypto`模块，但是，这些安全的随机数算法的消耗同样也是巨大的，高频的调用会导致应用性能大大降低。

仔细考虑你的随机数的需求，选择一个合适你自己的算法才是最重要的。



## 参考文章
- [https://v8.dev/docs/torque](https://v8.dev/docs/torque)
- [https://v8.dev/blog/math-random](https://v8.dev/blog/math-random)
- [https://en.wikipedia.org/wiki/Xoroshiro128%2B](https://en.wikipedia.org/wiki/Xoroshiro128%2B)
- [https://blog.securityevaluators.com/hacking-the-javascript-lottery-80cc437e3b7f#.mwvrmr6aq](https://blog.securityevaluators.com/hacking-the-javascript-lottery-80cc437e3b7f#.mwvrmr6aq)
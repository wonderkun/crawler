> 原文链接: https://www.anquanke.com//post/id/260393 


# 2021-西湖论剑-逆向（部分）-Writeup


                                阅读量   
                                **48737**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t01d3a8e5a5e6d0b306.jpg)](https://p2.ssl.qhimg.com/t01d3a8e5a5e6d0b306.jpg)



## TacticalArmed

出处: 2021 西湖论剑<br>
原题链接: 链接：[https://pan.baidu.com/s/14runS0J5A_PVjuN6Ior5Aw](https://pan.baidu.com/s/14runS0J5A_PVjuN6Ior5Aw)<br>
提取码：eaaf<br>
时间: November 20, 2021<br>
考点: SMC, TEA, before_main, ida_dbg, 反调试<br>
难度: 困难

### <a class="reference-link" name="%E5%88%9D%E6%AD%A5%E5%88%86%E6%9E%90"></a>初步分析
<li>PE32 的文件，拖到 IDA 里打开，很容易就能找到 `main` 函数<br>[![](https://p4.ssl.qhimg.com/t019ccc80cb81d5db77.png)](https://p4.ssl.qhimg.com/t019ccc80cb81d5db77.png)
</li>
1. 然后开始调试，发现很奇怪，一开始 IDA 是能调试的，但是过了几条指令之后 IDA 就啥都干不了了，考虑在 `main` 函数之前有其它操作
<li>
`main` 函数后面的逻辑很清晰
<ol>
<li>使用 `malloc` &amp; `VirtualProtect` 开辟了一段 rwx 的内存<br>[![](https://p4.ssl.qhimg.com/t018cc338a687dd24d6.png)](https://p4.ssl.qhimg.com/t018cc338a687dd24d6.png)
</li>
1. 读取输入
<li>进入多重 `while` 循环，最内层填充了上面的内存空间（填入 shellcode），然后运行<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01feb26d1328a6a822.png)
</li>
<li>进行比较<br>[![](https://p4.ssl.qhimg.com/t01bc9a8b11c2aaa611.png)](https://p4.ssl.qhimg.com/t01bc9a8b11c2aaa611.png)
</li>
### <a class="reference-link" name="%E8%80%83%E7%82%B9%E5%88%86%E6%9E%90"></a>考点分析

**`TLSCallback0`**
<li>发现一个 `TLSCallback0` ，里头起了个线程<br>[![](https://p0.ssl.qhimg.com/t0126ec31ce57580065.png)](https://p0.ssl.qhimg.com/t0126ec31ce57580065.png)
</li>
<li>线程注册了一个 exception handler 同时触发了对应的异常，回调函数里覆写了一些 data 段的数据，可能是填充 key 或者 cipher<br>[![](https://p5.ssl.qhimg.com/t01a06eb4c47ebfa915.png)](https://p5.ssl.qhimg.com/t01a06eb4c47ebfa915.png)
</li>
**`initterm`**
<li>在 `.rdata` 段找到一个结构体<br>[![](https://p4.ssl.qhimg.com/t010838749e7059de92.png)](https://p4.ssl.qhimg.com/t010838749e7059de92.png)
</li>
<li>里面自定义的函数最终执行了如下的逻辑<br>[![](https://p4.ssl.qhimg.com/t0113bb3cefa6b3810e.png)](https://p4.ssl.qhimg.com/t0113bb3cefa6b3810e.png)
</li>
<li>猜测这里就是反调试了，网上搜索相关知识，发现这是通过改变 `Dr` 寄存器的状态来反调试的方法，`Dr7` 会在这个循环每次执行后赋值为 0，**而它实际上可以理解为是调试功能的“使能”标志位**，所以这个线程在跑起来之后 IDA 的调试功能就没法用了<br><blockquote>
**相关知识的具体介绍**
[获取线程上下文的反调试技术](https://www.docin.com/p-1476078771.html)
[活着的虫子](https://www.cnblogs.com/yilang/p/12107126.html)
</blockquote>
</li>
1. 绕过也很简单，直接把调用 `initterm` 时传入的结构体里的函数指针删掉即可
**<a class="reference-link" name="shellcode%20%E8%BF%90%E8%A1%8C%E4%B8%8E%20dump"></a>shellcode 运行与 dump**
<li>结合伪代码可以很容易地定位到执行 shellcode 的地方<br>[![](https://p0.ssl.qhimg.com/t01476d55bd4d2d4156.png)](https://p0.ssl.qhimg.com/t01476d55bd4d2d4156.png)
</li>
<li>每次执行的其实都只是一条指令<br>[![](https://p1.ssl.qhimg.com/t01f0a94abfc401ecef.png)](https://p1.ssl.qhimg.com/t01f0a94abfc401ecef.png)
</li>
<li>所以现在的问题就是如何把指令 dump 出来。这里使用 IDASDK 提供的 `ida_dbg` 工具集，而我之前又在它之上封了一个更方便使用的库，欢迎大佬们使用<br>[GitHub – r4ve1/IDA-autodbg](https://github.com/r4ve1/IDA-autodbg)
</li>
1. 然后在 IDA 中运行此脚本，再运行程序，即可把所有执行过的 shellcode 的汇编 dump 出来了
```
import idc
import autodbg as ac
import sark
import ida_dbg

class MyHook(ac.Actions):
  def __init__(self):
    super().__init__()
    self.call_addr = 0x40146D
    self.bpt_actions = [ac.B(self.call_addr, self.callback)]
    self.exit_actions = [ac.E(self.exit_cbk)]
    self.insn = """"""

  def callback(self):
    ida_dbg.refresh_debugger_memory()
    var_addr = ida_dbg.get_reg_val("ebp")-8
    ea = idc.get_wide_dword(var_addr)
    for i in range(0x10):
      idc.del_items(ea+i)
    idc.create_insn(ea)
    l = sark.Line(ea)
    self.insn += str(l)+"\n"
    # print(self.insn)
    self.request_continue()

  def exit_cbk(self):
    with open("insn.txt", "w")as f:
      f.write(self.insn)

a = ac.AutoCracker(MyHook())
a.hook()
```
<li>所执行的 shellcode 大致如图所示（仅展示其中一轮加密）<br>[![](https://p3.ssl.qhimg.com/t01f1141cc637cf0204.png)](https://p3.ssl.qhimg.com/t01f1141cc637cf0204.png)
</li>
<li>其中大量移位 &amp; 亦或的操作核对后发现是 TEA 加密，密钥就是 `TLSCallback0` 里面复制的那个全局变量，delta 改为了 `-0x7E5A96D2`
</li>
<li>同时也能发现轮数改为了 33<br>[![](https://p4.ssl.qhimg.com/t013c456f40631b4e5c.png)](https://p4.ssl.qhimg.com/t013c456f40631b4e5c.png)
</li>
<li>
**还有一个很关键的，就是每加密一组明文后，**`**sum**`** 并没有置为 0，这在解密的时候也要照顾到，要不就只能解密一个分组了**
</li>
### <a class="reference-link" name="%E6%9C%80%E7%BB%88%E8%84%9A%E6%9C%AC"></a>最终脚本

```
#include &lt;cstdint&gt;
#include &lt;cstdio&gt;
#include &lt;iostream&gt;
#include &lt;string&gt;
#define DELTA -0x7E5A96D2
#define ROUND 33

uint32_t g_sum = 0;
using namespace std;

void tea_decrypt(uint32_t* v, uint32_t* k, uint32_t init_sum) `{`
  uint32_t v0 = v[0], v1 = v[1], sum = init_sum, i;    /* set up */
  uint32_t k0 = k[0], k1 = k[1], k2 = k[2], k3 = k[3]; /* cache key */
  for (i = 0; i &lt; ROUND; i++) `{`                        /* basic cycle start */
    v1 -= ((v0 &lt;&lt; 4) + k2) ^ (v0 + sum) ^ ((v0 &gt;&gt; 5) + k3);
    v0 -= ((v1 &lt;&lt; 4) + k0) ^ (v1 + sum) ^ ((v1 &gt;&gt; 5) + k1);
    sum -= DELTA;
  `}` /* end cycle */
  v[0] = v0;
  v[1] = v1;
`}`

int main() `{`
  int8_t cipher[] = `{`0xED, 0x1D, 0x2F, 0x42, 0x72, 0xE4, 0x85, 0x14, 0xD5, 0x78,
                     0x55, 0x03, 0xA2, 0x80, 0x6B, 0xBF, 0x45, 0x72, 0xD7, 0x97,
                     0xD1, 0x75, 0xAE, 0x2D, 0x63, 0xA9, 0x5F, 0x66, 0x74, 0x6D,
                     0x2E, 0x29, 0xC1, 0xFC, 0x95, 0x97, 0xE9, 0xC8, 0xB5, 0x0B`}`;
  uint32_t key[] = `{`0x7CE45630, 0x58334908, 0x66398867, 0x0C35195B1`}`;
  uint32_t sum = 0;
  for (int i = 0; i &lt; sizeof(cipher); i += 8) `{`
    auto ptr = (uint32_t*)(cipher + i);
    sum += DELTA * ROUND;
    tea_decrypt(ptr, key, sum);
  `}`
  string plain((char*)cipher, sizeof(cipher));
  cout &lt;&lt; plain &lt;&lt; endl;
`}`
```

flag `kgD1ogB2yGa2roiAeXiG8_aqnLzCJ_rFHSPrn55K`



## ROR

出处: 2021 西湖论剑<br>
原题链接: 链接：[https://pan.baidu.com/s/14runS0J5A_PVjuN6Ior5Aw](https://pan.baidu.com/s/14runS0J5A_PVjuN6Ior5Aw)<br>
提取码：eaaf<br>
时间: November 20, 2021<br>
考点: Z3<br>
难度: 简单

### <a class="reference-link" name="%E5%88%86%E6%9E%90"></a>分析
<li>
`main` 函数很清晰<br>[![](https://p3.ssl.qhimg.com/t013b910b810f1e6f96.png)](https://p3.ssl.qhimg.com/t013b910b810f1e6f96.png)
</li>
- 仔细过一遍加密部分，发现其实就是对明文的各个 bit 位进行重组，然后拿新产生的数去做查表加密
- 自然而然想到了 z3。但是 z3 无法解决查表的逆操作，这一步调 Python 的方法去做就行了
### <a class="reference-link" name="%E6%9C%80%E7%BB%88%E8%84%9A%E6%9C%AC"></a>最终脚本

```
import z3
p = [z3.BitVec("p%d" %i, 8)for i in range(40)]
buffer = [0]*256
k=[0]*8
k[0] = 128
k[1] = 64
k[2] = 32
k[3] = 16
k[4] = 8
k[5] = 4
k[6] = 2
k[7] = 1
charset=[  0x65, 0x08, 0xF7, 0x12, 0xBC, 0xC3, 0xCF, 0xB8, 0x83, 0x7B, 
  0x02, 0xD5, 0x34, 0xBD, 0x9F, 0x33, 0x77, 0x76, 0xD4, 0xD7, 
  0xEB, 0x90, 0x89, 0x5E, 0x54, 0x01, 0x7D, 0xF4, 0x11, 0xFF, 
  0x99, 0x49, 0xAD, 0x57, 0x46, 0x67, 0x2A, 0x9D, 0x7F, 0xD2, 
  0xE1, 0x21, 0x8B, 0x1D, 0x5A, 0x91, 0x38, 0x94, 0xF9, 0x0C, 
  0x00, 0xCA, 0xE8, 0xCB, 0x5F, 0x19, 0xF6, 0xF0, 0x3C, 0xDE, 
  0xDA, 0xEA, 0x9C, 0x14, 0x75, 0xA4, 0x0D, 0x25, 0x58, 0xFC, 
  0x44, 0x86, 0x05, 0x6B, 0x43, 0x9A, 0x6D, 0xD1, 0x63, 0x98, 
  0x68, 0x2D, 0x52, 0x3D, 0xDD, 0x88, 0xD6, 0xD0, 0xA2, 0xED, 
  0xA5, 0x3B, 0x45, 0x3E, 0xF2, 0x22, 0x06, 0xF3, 0x1A, 0xA8, 
  0x09, 0xDC, 0x7C, 0x4B, 0x5C, 0x1E, 0xA1, 0xB0, 0x71, 0x04, 
  0xE2, 0x9B, 0xB7, 0x10, 0x4E, 0x16, 0x23, 0x82, 0x56, 0xD8, 
  0x61, 0xB4, 0x24, 0x7E, 0x87, 0xF8, 0x0A, 0x13, 0xE3, 0xE4, 
  0xE6, 0x1C, 0x35, 0x2C, 0xB1, 0xEC, 0x93, 0x66, 0x03, 0xA9, 
  0x95, 0xBB, 0xD3, 0x51, 0x39, 0xE7, 0xC9, 0xCE, 0x29, 0x72, 
  0x47, 0x6C, 0x70, 0x15, 0xDF, 0xD9, 0x17, 0x74, 0x3F, 0x62, 
  0xCD, 0x41, 0x07, 0x73, 0x53, 0x85, 0x31, 0x8A, 0x30, 0xAA, 
  0xAC, 0x2E, 0xA3, 0x50, 0x7A, 0xB5, 0x8E, 0x69, 0x1F, 0x6A, 
  0x97, 0x55, 0x3A, 0xB2, 0x59, 0xAB, 0xE0, 0x28, 0xC0, 0xB3, 
  0xBE, 0xCC, 0xC6, 0x2B, 0x5B, 0x92, 0xEE, 0x60, 0x20, 0x84, 
  0x4D, 0x0F, 0x26, 0x4A, 0x48, 0x0B, 0x36, 0x80, 0x5D, 0x6F, 
  0x4C, 0xB9, 0x81, 0x96, 0x32, 0xFD, 0x40, 0x8D, 0x27, 0xC1, 
  0x78, 0x4F, 0x79, 0xC8, 0x0E, 0x8C, 0xE5, 0x9E, 0xAE, 0xBF, 
  0xEF, 0x42, 0xC5, 0xAF, 0xA0, 0xC2, 0xFA, 0xC7, 0xB6, 0xDB, 
  0x18, 0xC4, 0xA6, 0xFE, 0xE9, 0xF5, 0x6E, 0x64, 0x2F, 0xF1, 
  0x1B, 0xFB, 0xBA, 0xA7, 0x37, 0x8F]
realCipher=[  101,  85,  36,  54, 157, 113, 184, 200, 101, 251, 
  135, 127, 154, 156, 177, 223, 101, 143, 157,  57, 
  143,  17, 246, 142, 101,  66, 218, 180, 140,  57, 
  251, 153, 101,  72, 106, 202,  99, 231, 164, 121]
solver=z3.Solver()
for i in range(0,0x28,8):
  for j in range(8):
    c1 = ((k[j] &amp; p[i + 3]) &lt;&lt; (8 - (3 - j) % 8)) | ((k[j] &amp; p[i + 3]) &gt;&gt; ((3 - j) % 8)) | ((k[j] &amp; p[i + 2]) &lt;&lt; (8 - (2 - j) % 8)) | ((k[j] &amp; p[i + 2]) &gt;&gt; ((2 - j) % 8)) | ((k[j] &amp; p[i + 1]) &lt;&lt; (8 - (1 - j) % 8)) | ((k[j] &amp; p[i + 1]) &gt;&gt; ((1 - j) % 8)) | ((k[j] &amp; p[i]) &lt;&lt; (8 - -j % 8)) | ((k[j] &amp; p[i]) &gt;&gt; (-j % 8))
    c2 = ((k[j] &amp; p[i + 7]) &lt;&lt; (8 - (7 - j) % 8)) | ((k[j] &amp; p[i + 7]) &gt;&gt; ((7 - j) % 8)) | ((k[j] &amp; p[i + 6]) &lt;&lt; (8 - (6 - j) % 8)) | ((k[j] &amp; p[i + 6]) &gt;&gt; ((6 - j) % 8)) | ((k[j] &amp; p[i + 5]) &lt;&lt; (8 - (5 - j) % 8)) | ((k[j] &amp; p[i + 5]) &gt;&gt; ((5 - j) % 8)) | ((k[j] &amp; p[i + 4]) &lt;&lt; (8 - (4 - j) % 8)) | ((k[j] &amp; p[i + 4]) &gt;&gt; ((4 - j) % 8))
    c3=c1|c2
    ans=charset.index(realCipher[i+j])
    solver.add(c3==ans)
sat=solver.check()
print(sat)
mod=solver.model()
flag=''
for c in p:
  tmp=mod[c].as_long()
  flag+=chr(tmp)
print(flag)
```



## 虚假的粉丝

出处: 2021 西湖论剑<br>
原题链接: 链接：[https://pan.baidu.com/s/14runS0J5A_PVjuN6Ior5Aw](https://pan.baidu.com/s/14runS0J5A_PVjuN6Ior5Aw)<br>
提取码：eaaf<br>
时间: November 20, 2021<br>
难度: …

> 这题太 NT 了

### <a class="reference-link" name="%E5%88%86%E6%9E%90"></a>分析
1. 题目给的附件里有很多文件，看一下 exe
<li>让用户输入三个数，然后校验<br>[![](https://p5.ssl.qhimg.com/t0188b150ed9c8cbb13.png)](https://p5.ssl.qhimg.com/t0188b150ed9c8cbb13.png)
</li>
<li>让用户输入一个字符串，校验第一个和最后一个字符<br>[![](https://p0.ssl.qhimg.com/t01fdec31cf725071e9.png)](https://p0.ssl.qhimg.com/t01fdec31cf725071e9.png)
</li>
<li>然后就是这个循环了，运行一下发现这里就是播放音乐，然后读取文件里的内容并打印在屏幕上<br>[![](https://p0.ssl.qhimg.com/t01a8a04e3d3fde4557.png)](https://p0.ssl.qhimg.com/t01a8a04e3d3fde4557.png)
</li>
<li>文件感觉是字符画一类的东西<br>[![](https://p2.ssl.qhimg.com/t01ba87cd44e0380b30.png)](https://p2.ssl.qhimg.com/t01ba87cd44e0380b30.png)
</li>
1. 5315 这个文件全都是密文。所以这里的入手点就是猜到那个字符串
1. 考虑到 faded 的作者叫 Alan Walker，这里就从这个名字下手了。。。
1. 因为要输出的是字符画，所以大部分应该都是可视字符，所以还算有一个其他的方式判断当前是不是正确的 key
```
def dec():
  with open("f\ASCII-faded 5315.txt", "rb")as f:
    cipher = f.read()
  key = b"Al4N_wAlK3R"
  plain = [cipher[i] ^ key[i % len(key)]for i in range(len(cipher))]
  for i, p in enumerate(plain):
    if chr(p) not in string.printable:
      print(i % len(key))

  with open("plain.txt", "wb")as f:
    f.write(bytes(plain))
```
<li>得到字符画，又废了老大劲才读懂 flag …<br>[![](https://p0.ssl.qhimg.com/t01c99ce1e8f17d3605.png)](https://p0.ssl.qhimg.com/t01c99ce1e8f17d3605.png)
</li>
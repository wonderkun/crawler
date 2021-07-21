> 原文链接: https://www.anquanke.com//post/id/179556 


# 一步步学习Webassembly逆向分析方法


                                阅读量   
                                **324263**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">6</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t019f72f67cdf78c0b7.png)](https://p4.ssl.qhimg.com/t019f72f67cdf78c0b7.png)



在强网杯2019线上赛的题目中，有一道名为Webassembly的wasm类型题，作为CTF新人，完全没有接触过wasm汇编语言，对该类型无从下手，查阅相关资料后才算入门，现将Webassembly的静态分析和动态调试的方法及过程整理如下，希望能够对于CTF萌新带来帮助，同时如有大佬光顾发现错误，欢迎拍砖予以斧正。



## 1.WebAssembly基本概念

在开始Webassembly逆向分析之前，需要了解其基本概念和基础知识，由于自己也是初学者，防止对大家的学习产生误导，在此将学习资料链接给出。
- [`图解WebAssembly`](https://www.w3ctech.com/topic/2011)
- [`理解 WebAssembly JS API`](https://www.w3ctech.com/topic/2014)
- [`理解WebAssembly文本格式`](https://developer.mozilla.org/zh-CN/docs/WebAssembly/Understanding_the_text_format)
总体来说，wasm可以理解为一种可以由JavaScript调用，并与html交互的二进制指令格式文件。

[![](https://p5.ssl.qhimg.com/t017e82c6dd1740b777.webp)](https://p5.ssl.qhimg.com/t017e82c6dd1740b777.webp)



## 2.处理wasm文件

在逆向wasm的过程中，由于其执行的是以栈式机器定义的虚拟机的二进制指令格式，因此直接进行逆向分析难度较大，需要对wasm文件进行处理，增强可操作性，提高逆向的效率。在此参考了[`《一种Wasm逆向静态分析方法》`](https://xz.aliyun.com/t/5170)一文，主要利用了[`WABT（The WebAssembly Binary Toolkit）`](https://github.com/WebAssembly/wabt)工具箱实现。

### <a class="reference-link" name="2.1%E5%8F%8D%E6%B1%87%E7%BC%96"></a>2.1反汇编

安装WABT工具后，在/wabt/build文件中会有各种小工具。利用wasm2wat工具可以生成wasm汇编文本格式的.wat文件。

```
./wasm2wat ../webassembly.wasm -o webassembly.wat
```

输入上述语句可以得到webassembly.wat文件。

[![](https://p1.ssl.qhimg.com/t015e5981f4f70655f1.png)](https://p1.ssl.qhimg.com/t015e5981f4f70655f1.png)

### <a class="reference-link" name="2.2%E5%8F%8D%E7%BC%96%E8%AF%91"></a>2.2反编译

利用wasm2c工具可以生成c语言文本格式的`*.c`和`*.h`代码文件。

```
./wasm2c ../webassembly.wasm -o webassembly.c
```

输入上述语句可以得到webassembly.h和webassembly.c文件。

[![](https://p0.ssl.qhimg.com/t019491251e34a1dab0.png)](https://p0.ssl.qhimg.com/t019491251e34a1dab0.png)

### <a class="reference-link" name="2.3%E9%87%8D%E6%96%B0%E7%BC%96%E8%AF%91"></a>2.3重新编译

得到webassembly.h和webassembly.c文件后就可以使用gcc编译得到常见的`*.o`目标文件了，这里需要将/wabt/wasm2c中的wasm-rt.h，wasm-rt-impl.c，wasm-rt-impl.h文件复制出来。

```
gcc -c webassembly.c -o webassembly.o
```

输入上述语句可以得到webassembly.o文件。

[![](https://p4.ssl.qhimg.com/t01f2182d0f02fbbd39.png)](https://p4.ssl.qhimg.com/t01f2182d0f02fbbd39.png)



## 3.静态分析

经过了wasm处理之后，对wasm的分析就可以利用webassembly.o文件在IDA中进行了。

### <a class="reference-link" name="3.1%E5%AF%BB%E6%89%BEmain%E5%87%BD%E6%95%B0"></a>3.1寻找main函数

IDA自动分析之后可以直接找到`main`函数。

[![](https://p5.ssl.qhimg.com/t017bc84f1c6ff55392.png)](https://p5.ssl.qhimg.com/t017bc84f1c6ff55392.png)

### <a class="reference-link" name="3.2%E5%AF%BB%E6%89%BE%E5%85%B3%E9%94%AE%E5%87%BD%E6%95%B0"></a>3.2寻找关键函数

在`main`函数中只调用了`f54`和`f15`两个函数，进入函数就会发现`f54`函数比较复杂，进入`f15`函数可以看到疑似加密过程的函数。

[![](https://p0.ssl.qhimg.com/t01ba98fbd98c006dd3.png)](https://p0.ssl.qhimg.com/t01ba98fbd98c006dd3.png)

可以搜索魔数`0x61C88647`寻找加密算法。

[![](https://p4.ssl.qhimg.com/t01812562cdb448d89a.png)](https://p4.ssl.qhimg.com/t01812562cdb448d89a.png)

其实从汇编语言中可以看到，魔数`0x61C88647`应该是`0x9E3779B9`，即可知这里是进行了四次`XTEA`加密算法。

继续观察`f15`函数可以看到如下代码。

[![](https://p3.ssl.qhimg.com/t01f4f6ae6d019371a0.png)](https://p3.ssl.qhimg.com/t01f4f6ae6d019371a0.png)

注意到`'x65x36x38x62x62x7d'`的二进制数据为字符串`'e68bb`}`'`，刚好符合flag的尾部格式，应该是未加密部分的数据，可以看出，该程序是对输入的数据进行XTEA加密，如果等于给出的密文，则输入即为flag。

到此，就可以写出exp得到flag了。



## 4.动态分析

上述静态分析过程已经可以得到flag，这里通过动态跟踪该程序整理一下动态调试分析的方法。这里采用chrome浏览器进行动态调试分析，用到了[`chrome-wasm-debugger`](https://github.com/itszn/chrome-wasm-debugger)工具观察内存信息。

### <a class="reference-link" name="4.1%E7%8E%AF%E5%A2%83%E6%90%AD%E5%BB%BA"></a>4.1环境搭建

利用python3自带的http服务，输入以下命令，在8888端口开启一个简单的服务器用于动态调试。

```
python -m http.server 8888
```

[![](https://p1.ssl.qhimg.com/t01418c92a96a79e1f3.png)](https://p1.ssl.qhimg.com/t01418c92a96a79e1f3.png)

打开chrome浏览器，输入地址`http://127.0.0.1:8888/webassembly.html`即可正常加载运行，此时点击`WASM debuger`插件工具，即可attach到当前浏览器，会显示“‘WASM debugger’正在调试此浏览器”的字样，然后按下`Control+Shift+J` 打开开发人员工具并转到控制台。

[![](https://p4.ssl.qhimg.com/t01be1b8c6ca2fb32a4.png)](https://p4.ssl.qhimg.com/t01be1b8c6ca2fb32a4.png)

### <a class="reference-link" name="4.2%E5%AF%BB%E6%89%BE%E5%85%B3%E9%94%AE%E6%96%AD%E7%82%B9"></a>4.2寻找关键断点

一般程序动态分析的关键就在于断点的寻找，找到合适的断点，便于分析程序的执行流程和数据处理情况。在动态分析Webassembly程序的时候，可以同时在JS脚本和wasm文件下断点，就能更加有效地达成上述目的。

该程序在运行后弹出了一个窗口，并伴有`input:`的字样，那么就可以在JS脚本中搜索该文字，找到弹出窗口的程序语句，并在此处点击设置断点。

[![](https://p1.ssl.qhimg.com/t015ed9f53f81422315.png)](https://p1.ssl.qhimg.com/t015ed9f53f81422315.png)

设置断点之后刷新页面重新运行程序，就可以看到程序断在了此处，找到了关键断点，下面就可以对程序进行调试分析了。

### <a class="reference-link" name="4.3%E8%B0%83%E8%AF%95%E5%88%86%E6%9E%90"></a>4.3调试分析

找到关键断点后，观察右边的函数调用栈，可以看到程序运行到此处的函数调用过程如下。

```
f16 --&gt; f54 --&gt; f32 --&gt; f34 --&gt; f28 --&gt; __syscall145 --&gt; doReadv --&gt; read --&gt; read --&gt; get_char
```

结合IDA静态分析过程，`f16`即为`main`函数，可以看到`main`函数调用了静态分析过程中忽略的`f54`函数，那么可以猜测该函数功能应该是获得输入内容。

#### <a class="reference-link" name="4.3.1JS%E4%BB%A3%E7%A0%81%E5%88%9D%E5%A7%8B%E5%8C%96%E8%BF%87%E7%A8%8B"></a>4.3.1JS代码初始化过程

为了搞清楚Webassembly程序的整个运行过程，以及JS与Wasm的交互过程，我们从头开始分析。在Webassembly.js文件的第一行设置断点，按下F11单步跟进。

##### <a class="reference-link" name="1.%E5%88%9B%E5%BB%BA%E7%BA%BF%E6%80%A7%E5%86%85%E5%AD%98%E5%AE%9E%E4%BE%8B"></a>1.创建线性内存实例

运行到582行的时候，通过调用[`WebAssembly.Memory()`](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/WebAssembly/Memory)接口创建WebAssembly线性内存实例，并且能够通过相关的实例方法获取已经存在的内存实例（当前每一个模块实例只能有一个内存实例）。内存实例拥有一个[`buffer`](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/WebAssembly/Memory/buffer)获取器，它返回一个指向整个线性内存的ArrayBuffer。

[![](https://p2.ssl.qhimg.com/t010f0cd3e970283690.png)](https://p2.ssl.qhimg.com/t010f0cd3e970283690.png)

##### <a class="reference-link" name="2.%E5%88%9D%E5%A7%8B%E5%8C%96%E5%86%85%E5%AD%98"></a>2.初始化内存

运行到591行的时候，调用了`updateGlobalBufferViews()`函数，该函数的实现中申请了一些内存，在之后的数据处理过程中会被用到。

[![](https://p5.ssl.qhimg.com/t017a24225435d7fac7.png)](https://p5.ssl.qhimg.com/t017a24225435d7fac7.png)

##### <a class="reference-link" name="3.%E5%88%9B%E5%BB%BAWebassembly%E5%AE%9E%E4%BE%8B"></a>3.创建Webassembly实例

运行到783行的时候，通过调用`createWasm()`函数后间接调用到`getBinaryPromise()`函数，通过`fetch()`函数[`编译和实例化Webassembly代码`](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/WebAssembly/instantiate)。

[![](https://p4.ssl.qhimg.com/t01c772295dced46072.png)](https://p4.ssl.qhimg.com/t01c772295dced46072.png)

##### <a class="reference-link" name="4.JS%E5%AF%BC%E5%85%A5wasm%E7%9A%84%E5%AF%BC%E5%87%BA%E5%87%BD%E6%95%B0"></a>4.JS导入wasm的导出函数

运行到4413行的时候，JS代码将wasm中的导出函数导入进来，`main`函数就是在这个过程中被导入到了`_main`变量当中的。

[![](https://p5.ssl.qhimg.com/t01826258e5276c8425.png)](https://p5.ssl.qhimg.com/t01826258e5276c8425.png)

这些导出函数可以在Webassembly.wat文件的最后位置找到。

```
(export "___errno_location" (func 26))
  (export "_free" (func 18))
  (export "_main" (func 16))
  (export "_malloc" (func 17))
  (export "_memcpy" (func 69))
  (export "_memset" (func 70))
  (export "_sbrk" (func 71))
  (export "dynCall_ii" (func 72))
  (export "dynCall_iiii" (func 73))
  (export "establishStackSpace" (func 14))
  (export "stackAlloc" (func 11))
  (export "stackRestore" (func 13))
  (export "stackSave" (func 12))
```

##### <a class="reference-link" name="5.%E6%89%A7%E8%A1%8Cwasm%E7%9A%84main%E5%87%BD%E6%95%B0"></a>5.执行wasm的main函数

运行到4594行的时候，JS代码几乎快要执行结束了，这个时候进入`run()`函数之后，程序最终会调用wasm的`main`函数，此时程序执行到wasm的代码空间中。

[![](https://p1.ssl.qhimg.com/t01749c9427efdb0182.png)](https://p1.ssl.qhimg.com/t01749c9427efdb0182.png)

#### <a class="reference-link" name="4.3.2%E6%95%B0%E6%8D%AE%E5%A4%84%E7%90%86%E8%BF%87%E7%A8%8B"></a>4.3.2数据处理过程

##### <a class="reference-link" name="1.Wasm%E4%BB%A3%E7%A0%81%E8%B0%83%E7%94%A8%E7%94%A8%E6%88%B7%E8%BE%93%E5%85%A5"></a>1.Wasm代码调用用户输入

Wasm代码的断点可以在左边视图中wasm的结点中设置，通过上文的函数调用栈，中间函数不需要一步步跟进了，我们可以看到运行到了`f28`函数后，紧接着调用了`__syscall145`函数。

[![](https://p0.ssl.qhimg.com/t01629dba297fbf1c18.png)](https://p0.ssl.qhimg.com/t01629dba297fbf1c18.png)

在`f28`函数中看到了`f3`函数，并没有`__syscall145`函数，但是如果去IDA中观察的话，是能够看到该函数的。

[![](https://p0.ssl.qhimg.com/t01924817f4f881bb55.png)](https://p0.ssl.qhimg.com/t01924817f4f881bb55.png)

其实这个是wasm导入的JS的导出函数，可以在Webassembly.wat文件的最开始位置找到。

```
(import "env" "abort" (func (;0;) (type 2)))
  (import "env" "___setErrNo" (func (;1;) (type 2)))
  (import "env" "___syscall140" (func (;2;) (type 3)))
  (import "env" "___syscall145" (func (;3;) (type 3)))
  (import "env" "___syscall146" (func (;4;) (type 3)))
  (import "env" "___syscall54" (func (;5;) (type 3)))
  (import "env" "___syscall6" (func (;6;) (type 3)))
  (import "env" "_emscripten_get_heap_size" (func (;7;) (type 4)))
  (import "env" "_emscripten_memcpy_big" (func (;8;) (type 0)))
  (import "env" "_emscripten_resize_heap" (func (;9;) (type 1)))
  (import "env" "abortOnCannotGrowMemory" (func (;10;) (type 1)))
  (import "env" "__table_base" (global (;0;) i32))
  (import "env" "DYNAMICTOP_PTR" (global (;1;) i32))
  (import "global" "NaN" (global (;2;) f64))
  (import "global" "Infinity" (global (;3;) f64))
  (import "env" "memory" (memory (;0;) 256 256))
  (import "env" "table" (table (;0;) 10 10 funcref))
```

##### <a class="reference-link" name="2.JS%E5%A4%84%E7%90%86%E7%94%A8%E6%88%B7%E8%BE%93%E5%85%A5"></a>2.JS处理用户输入

`__syscall145`函数调用之后，程序又进入了JS代码空间。在此可以跟进到第二个`doReadv`函数，可以看到这里是在处理的用户输入去了哪里。

[![](https://p1.ssl.qhimg.com/t013be3442b38e5a61d.png)](https://p1.ssl.qhimg.com/t013be3442b38e5a61d.png)

如果跟进后面的read可以得知，取出用户输入1024长度的内容，这里终于可以用到`WASM debuger`工具了，这里在4183行下好断点，运行到断点处，我们在工具窗口中查看`ptr`中的内容，此时的命令与gdb相同，需要注意3672是10进制数字。

```
wdb&gt; x/16 0xe58
0x00000e58:  0x00000000 0x00000000 0x00000000 0x00000000
0x00000e68:  0x00000000 0x00000000 0x00000000 0x00000000
0x00000e78:  0x00000000 0x00000000 0x00000000 0x00000000
0x00000e88:  0x00000000 0x00000000 0x00000000 0x00000000
wdb&gt;
```

之后在函数结束处4187行下好断点，然后输入1024个A的数据，程序中断，在工具窗口中继续查看`ptr`中的内容。

```
wdb&gt; x/16 0xe58
0x00000e58:  0x41414141 0x41414141 0x41414141 0x41414141
0x00000e68:  0x41414141 0x41414141 0x41414141 0x41414141
0x00000e78:  0x41414141 0x41414141 0x41414141 0x41414141
0x00000e88:  0x41414141 0x41414141 0x41414141 0x41414141
wdb&gt;
```

此时，该内存的内容就是用户输入的数据了，同时我们查看`iov`内存中的内容。

```
wdb&gt; x/4 0x1b30
0x00001b30:  0x00001b20 0x00000000 0x00000e58 0x00000400
wdb&gt;
```

可以看出，该内存块中存访了0xe58的内存地址和0x400的内存大小。

那么执行到`f25`函数之后就有了存放输入内容的内存地址和内存大小的信息了。

[![](https://p0.ssl.qhimg.com/t012286137e02e538ad.png)](https://p0.ssl.qhimg.com/t012286137e02e538ad.png)

##### <a class="reference-link" name="3.%E8%BE%93%E5%85%A5%E6%95%B0%E6%8D%AE%E7%9A%84%E5%88%A4%E6%96%AD"></a>3.输入数据的判断

到这里以后，就可以随心所欲地调试自己的程序了，发现输入的数据进入到wasm代码空间之后并没有进行处理，直接又返回调用到用户输入了。

继续跟进会发现在`f54`函数当一个判断条件不能触发，那么程序永远都会跳转到第1000行的`f32`函数，从而重新跳转到了用户输入变成了死循环。因此，我们在判断条件处设置断点。

[![](https://p2.ssl.qhimg.com/t013c39b9459fb38445.png)](https://p2.ssl.qhimg.com/t013c39b9459fb38445.png)

发现这里比较的是内存地址和4696的值进行比较，而内存长度只有1024，当内存的每一个字符都比较完了就必定会落入`f32`函数当中，好像无法跳出循环。继续往下执行发现还有一个条件判断语句。

[![](https://p5.ssl.qhimg.com/t012f05dcd3b5fd0ec5.png)](https://p5.ssl.qhimg.com/t012f05dcd3b5fd0ec5.png)

发现这里是取内存地址6656，在地址偏移为输入字符的ASCII码值加1处的内容，然后与0进行比较，因此可以查看该内存地址0x1A00处的内容。

```
wdb&gt; x/48 0x1a00
0x00001a00:  0xfffffeff 0xfffffffe 0x0000ffff 0xfeffffff
0x00001a10:  0xfffffffe 0xfffffffe 0xfffffffe 0xfffffffe
0x00001a20:  0xffff00fe 0xfffffffe 0xfffffffe 0xfffffffe
0x00001a30:  0xfffffffe 0xfffffffe 0xfffffffe 0xfffffffe
0x00001a40:  0xfffffffe 0xfffffffe 0xfffffffe 0xfffffffe
0x00001a50:  0xfffffffe 0xfffffffe 0xfffffffe 0xfffffffe
0x00001a60:  0xfffffffe 0xfffffffe 0xfffffffe 0xfffffffe
0x00001a70:  0xfffffffe 0xfffffffe 0xfffffffe 0xfffffffe
0x00001a80:  0xfffffffe 0xfffffffe 0xfffffffe 0xfffffffe
0x00001a90:  0xfffffffe 0xfffffffe 0xfffffffe 0xfffffffe
0x00001aa0:  0xfffffffe 0xfffffffe 0xfffffffe 0xfffffffe
0x00001ab0:  0xfffffffe 0xfffffffe 0xfffffffe 0xfffffffe
```

或者查看右边Global中的memory，找到6056的位置。

[![](https://p1.ssl.qhimg.com/t012f4aeebf2a4cc940.png)](https://p1.ssl.qhimg.com/t012f4aeebf2a4cc940.png)

可以看到其中有内容为0的地址有6个，当输入为可见字符空格即0x20的时候，会取到6689处的0，之后就会跳出循环进入到后面的验证程序。所以输入的1024个数据中，会截取空格之前的数据传送到后边的程序进行处理。

##### <a class="reference-link" name="4.%E6%95%B0%E6%8D%AE%E5%8A%A0%E5%AF%86"></a>4.数据加密

我们继续跟进，查看输入数据是否到达了上文静态分析的`f15`函数中，直接在`f15`函数第33行设置断点，输入1024个A，并替换其中一个A为空格，运行后程序中断。

[![](https://p3.ssl.qhimg.com/t01a789b1d109f20259.png)](https://p3.ssl.qhimg.com/t01a789b1d109f20259.png)

可以看到两个变量的值变为1094795585，这个值转换为十六进制就是0x41414141，即我们刚才输入数据的前四个AAAA，到此完全搞清楚了程序的执行流程和数据处理情况。

#### <a class="reference-link" name="4.3.3%E7%BC%96%E5%86%99exp%E5%BE%97%E5%88%B0flag"></a>4.3.3编写exp得到flag

经过上述分析可以编写exp如下。

```
#!python3.6
import struct

def decrypt(v0, v1, key):
    delta = 0x9e3779b9
    n = 32
    sum = (delta * n)
    mask = 0xffffffff
    for round in range(n):
            v1 = (v1 - (((v0&lt;&lt;4 ^ v0&gt;&gt;5) + v0) ^ (sum + k[sum&gt;&gt;11 &amp; 3]))) &amp; mask
            sum = (sum - delta) &amp; mask
            v0 = (v0 - (((v1&lt;&lt;4 ^ v1&gt;&gt;5) + v1) ^ (sum + k[sum &amp; 3]))) &amp; mask

    return struct.pack("i",v0) + struct.pack("i",v1)

block = [0xE7689695, 0xC91755b7, 0xCF1e03ad, 0x4B61c56f, 0x2Dfd9002, 0x930aed22, 0xECc97e30, 0xE0B1968c]
k = [0,0,0,0]

flag = ''
for i in range(4):
     flag = flag + ((decrypt(block[i*2], block[i*2+1], k)).decode())

flag = flag + 'x65x36x38x62x62x7d'

print(flag)
```

得到flag为`flag`{`1c15908d00762edf4a0dd7ebbabe68bb`}``

若直接输入该字符串并不会显示处结果，因此输入flag和空格，再跟上一些内容组成1024长度的数据，就可以得到成功结果的字符串。

[![](https://p2.ssl.qhimg.com/t01e6da8582ebba2a29.png)](https://p2.ssl.qhimg.com/t01e6da8582ebba2a29.png)

另外，如果只输入flag，直接点击取消，会有换行符号0x0A加在输入后面，也能够进入判断流程，是可以得到正确结果的，有兴趣的萌新可以跟进调试以下。



## 5.相关信息

在进行Webassembly的动态调试的时候，chrome浏览器存在一些bug，可能导致某些断点虽然设置了，但是并没断下来，这个时候需要关闭浏览器后重新加载一下就可正常运行了。`WASM debuger`工具并不是必须的，浏览器中也能够观察到相关的内存信息，不过不如该工具方便。由于刚接触Webassembly的逆向分析，可能上述过程并不是最佳方法，如大佬们有更好的调试分析方法，欢迎分享知识指点迷津。

### <a class="reference-link" name="5.1%E5%8F%82%E8%80%83%E8%B5%84%E6%96%99"></a>5.1参考资料
- [`图解WebAssembly`](https://www.w3ctech.com/topic/2011)
- [`理解 WebAssembly JS API`](https://www.w3ctech.com/topic/2014)
- [`理解WebAssembly文本格式`](https://developer.mozilla.org/zh-CN/docs/WebAssembly/Understanding_the_text_format)
- [`Webassembly 语义`](https://webassembly.org/docs/semantics/#linear-memory)
- [`一种Wasm逆向静态分析方法`](https://xz.aliyun.com/t/5170)
- [`用idawasm IDA Pro逆向WebAssembly模块`](https://xz.aliyun.com/t/2854)
- [`执行 wasm 转换出来的 C 代码`](https://zhuanlan.zhihu.com/p/43986042)
- [`TEA、XTEA、XXTEA加密解密算法`](https://blog.csdn.net/gsls200808/article/details/48243019)
- [`WebAssembly.Memory()`](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/WebAssembly/Memory)
- [`buffer获取器`](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/WebAssembly/Memory/buffer)
- [`编译和实例话Webassembly代码`](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/WebAssembly/instantiate)
### <a class="reference-link" name="5.2%E5%B7%A5%E5%85%B7%E9%93%BE%E6%8E%A5"></a>5.2工具链接
- [`WABT（The WebAssembly Binary Toolkit）`](https://github.com/WebAssembly/wabt)
- [`chrome-wasm-debugger`](https://github.com/itszn/chrome-wasm-debugger)
- [`示例程序相关文件`](https://github.com/supdump/qwb2019/tree/master/webassembly)
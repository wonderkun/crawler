> 原文链接: https://www.anquanke.com//post/id/163964 


# HCTF-xor_game&amp;the_end详细WP


                                阅读量   
                                **255299**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/dm/1024_576_/t0127a89f3ff5b23218.png)](https://p1.ssl.qhimg.com/dm/1024_576_/t0127a89f3ff5b23218.png)

这次比赛只做出了这两个题，其中我觉的the_end的思路还是可以借鉴一下的。

## xor_game

### <a name="%E6%96%87%E4%BB%B6%E5%88%86%E6%9E%90"></a>文件分析

题目给出了两个文件一个是加密脚本，一个是加密后输出的文件。打开加密的脚本，就能看出和2017suctf的一个题目很像。

### <a name="%E5%8A%A0%E5%AF%86%E8%84%9A%E6%9C%AC"></a>加密脚本

```
ciMbOQxffx0GHQtSBB0QSQIORihXVQAUOUkHNgQLV
AQcAVMAAAMCASFEGQYcVS8BNh8BGAoHFlMAABwCTS
VQC2UdMQx5FkkGEQQAAVMAAQtHRCNLF0NSORscMkk
aHABSExIYBQseUmBCFgtSKwEWfwELFRcGbzwEDABH
VS8DDAcXfwUcMQwCDUUBCgYYSQEBATNKGwQeOkkbP
hsYERYGDB0TYzwCUSVCDE8dKh0BNg4GAAkLSVMWHB
pHQCxQF08AOhkWPh1OAA0XRQQRBQJKQyVKFghSMA9
5Gh8LGhEHBB8YEE4UViFaEQEVfwAdfx0GEUUWAAAR
GxpHTiFQERx4FkkROgUHERMXRTpUCANtYy9RFk8TL
EkHNwxOFhcbAhsASR0STC1GCk8UMwYEOhsdfiEdRR
0bHU4QSDRLHR0XO0kGMQ0LEgATERYQSQgORDJaWAs
XMgYdfxsbGAB4LRYVGxpHUyFXHU8TMQ1TPRsLFREa
DB0TSRoIASJGGR1SKwEWfwUBFQFSChVUHQYCASNWF
Q0XLRocMgxkNgoAABd+PRkIKwkDEAoTLQ1TKwELVA
gHFhoXRU4BUy9OWBsaOkkeMAYAVAQcAVMXCBwEQDN
Qci4HJwAfNggcDUUXHQcGDAMCASFGCxsaOh0aPAAd
GUUQBBoASRoIASNCCBsHLQxTMgAdABx4IxoYBQcJR
mBXEApSNgcHOgcdEUUeDBURRU4FVDQDGQMBMEkVNg
UCHQsVRQccDE4XVDJGcjsaOhsWfwgcEUUTCQQVEB1
HTCVOFx0bOhpTKwEcGxAVDRwBHU4TSSUDHQ4AKwF5
FkkMEQkbAAURSSdHQC0pPAYXO0kSLEkaHABSFAYdD
BpHQyVCDRsLfwYVfwgbABAfC1MYDA8RRDMpKwcXMQ
5TNhpOGgoGRRAcCAEUDWBQFQAZOkkUOhoaARcXbzY
CDABHVilPDE8TMxocfxsLAAQbCxYQSQwITyUDCB0d
Kg0fJkk/
HQsVRTURBwlHTDVQGwMXVSYQPBwCAG8mDQERDGQuA
ShGGR1SMwYFOkVOPUUQAB8dDBgCASlNWAMdKQx5Ew
YYEUUbFlMVSR4ITiwDFwlSLB0BKg4JGAwcAlMWBRs
CDCdRHQocfwgfOAgLfiQBRRcRGgELQDRGWAIbPBsc
cgsbBhYGRRwSSRkOTyQpOgMXOg0aMQ5OAA0ACgYTA
U4KWGBVHQYcLGMqOggcB0UBERIAAAEJRCQDEQFSKw
EWfwsLGAwXA3kyBhsVKwkDGgoeNgwFOkkaHAQGRRI
YBU4EQC4DEAoTLWM2KQwAVAQcERoXAB4GVSUDHAYB
PBsWKwxCVCxSCBYASRoPRGBMDAcXLUkHNwwHBkUdE
h1+OgEKRGBAGQFSMQYHfw4cFRYCRQccDE4KTi1GFh
t4EwwVK0kaG0UGDRZULA8UVWBXF08VMEkkOhoaWEU
GDRZUDQsGRWBODRwGfwccK0kcEREHFx1UHQFHTy9U
EAoAOmMgOgxCVCxSEhYVG049QC4DPgMdKAwBLEkBG
kUfHFMcDA8DDWBKFk8UKgUffwsCGwofRRIYBgAAAT
RLHU8FPhBTPgUCVBEaAFMDCBdtZzJGCRoXMR0fJkk
DHRYBABdUGgEKRGwDGhoGfwgfLAZOEAAXFR8NSQMI
VyVHWA0Lfx4aMQ1CVAMACgAARU4UTy9UWAAAfxsSN
gdkMgwEAHkkGw8NTyEDKA4APgQaKwhCVBYdCh1UCB
1HUi9MFk8TLGMfNg8LVAcXRRERCBsTSCZWFE8eNgI
WfxobGQgXF1MSBQEQRDJQWA4cO0kXOggaHEUeDBgR
SQ8SVTVOFk8eOggFOhpkNQkBClMXCBwCASFBFxoGf
x4bPh1OHAQB
```

### <a name="%E6%80%9D%E8%B7%AF%E5%88%86%E6%9E%90"></a>思路分析

由于key的长度肯定是远远小于给的poem的长度，这样的话进行异或的过程中肯定是会有可以利用统计规律进行计算得出的值（第一次做这样的密码题，让我想起了模仿游戏当中破解德军密码机的时候也是用了这个方法）

### <a name="%E6%96%B9%E6%B3%95%E8%AE%B2%E8%BF%B0"></a>方法讲述

一、可以利用一个叫做xortools的工具进行一个字频率的一个统计，这样会方便一些在不知道脚本的情况下

二、上面这一步可能中间会有些错误会需要手动修改，于是。。因为suctf见过，就借用了一个师傅的脚本进行了一个快速的解题

😂

### <a name="exp"></a>exp

给出脚本的链接：[https://findneo.github.io/180527suctf/#Cycle](https://findneo.github.io/180527suctf/#Cycle)

### <a name="%E5%AE%9E%E7%8E%B0%E5%90%8E%E7%9A%84%E5%9B%BE%E7%89%87"></a>实现后的图片

[![](https://p1.ssl.qhimg.com/t0109c423b662b8b0da.png)](https://p1.ssl.qhimg.com/t0109c423b662b8b0da.png)

这个图没有截取完整。。要是细心的老师傅应该可以猜的出哪一个是flag-&gt;xor_is_interesting!@#加上hctf的头和尾就是flag了。



## the_end

题目叫做the_end,感觉是有那么一点关系，这里大概能对exit有个比较全面的了解。

### <a name="%E4%BF%9D%E6%8A%A4%E6%9F%A5%E7%9C%8B"></a>保护查看

[![](https://p4.ssl.qhimg.com/t012db5df678f30360d.png)](https://p4.ssl.qhimg.com/t012db5df678f30360d.png)

保护出来canary都开了，这里安利一波pwndbg，可以对开了pie的程序下一个基地址的断点：

b *$rebase(偏移)

### <a name="%E7%A8%8B%E5%BA%8F%E5%88%86%E6%9E%90"></a>程序分析

main

[![](https://p3.ssl.qhimg.com/t01a681f871f9cb443e.png)](https://p3.ssl.qhimg.com/t01a681f871f9cb443e.png)

程序的逻辑很简单，首先会给我们一个gift就是sleep的地址这样就可以帮助我们基地址了。然后进入主要的部分一个循环，第一次会对程序进行一个8位的读，第二个读会对我们刚才读进去的8位字节所处的地方进行一个一个字节的写，这个就可以造成任意地址写的一个漏洞了。

### <a name="%E5%8A%A8%E6%80%81%E8%B0%83%E8%AF%95"></a>动态调试

我个人觉得这个题目的关键就在于动态调试程序，因为题目中没有可以给我们过多利用的函数了，只剩下了一个exit()函数，其实开始我并没有什么思路，于是就开始进行了Google，发现了一个类似的题0x00ctf2017-left的题，题目要比这个难，思路上也不太一样，但是有借鉴作用，感兴趣的读者可以看看那个。

### <a name="%E7%AC%AC%E4%B8%80%E4%B8%AA%E7%82%B9"></a>第一个点

先随意构造输入，然后进入exit函数利用si指令进入每一个函数可以发现一个可能可利用的异常点：

[![](https://p3.ssl.qhimg.com/t0106e76b1e91042c8f.png)](https://p3.ssl.qhimg.com/t0106e76b1e91042c8f.png)

图片中有一个call rdx,而rdx来自于rax+0x18

[![](https://p5.ssl.qhimg.com/t013239bff9fa211731.png)](https://p5.ssl.qhimg.com/t013239bff9fa211731.png)

这里有一个不像是栈上地址的数，感觉是和后面的ror,xor等有一些关系像是一个解密的操作。这里就可以参考我们上面的所提到的那个题目的思路了。但是这个思路太难利用了所以我想试试能不能有其他的方法，继续调试了下去。

### <a name="%E7%AC%AC%E4%BA%8C%E7%82%B9"></a>第二点

继续往下siyou 可以发现一个call,处在_dl_fini

[![](https://p4.ssl.qhimg.com/t013cc02884e5ccdcc6.png)](https://p4.ssl.qhimg.com/t013cc02884e5ccdcc6.png)

这个地方调用了rdi+0x216414这个指针，我们查看一下：

[![](https://p1.ssl.qhimg.com/t01bcf8f94097650170.png)](https://p1.ssl.qhimg.com/t01bcf8f94097650170.png)

这里有一个好像是低三位的一个指针，那大概就是会call这个指针了。。我们可以试试能不能去覆盖这里的指针。当然要先得到偏移，关于这个地址的偏移我是一个 一个试出来的，因为没有几位，应该这个地址段上有些还是不可写的地方。

### <a name="%E6%80%9D%E8%B7%AF%E5%88%86%E6%9E%90"></a>思路分析

两个思路都是在地址上写上我们的one_gadget，写入的地点和方法不同而已。

### <a name="%E7%AC%AC%E4%B8%80%E4%B8%AA%E6%80%9D%E8%B7%AF"></a>第一个思路

一、就是利用0x00ctf那个思路，利用我们第一次所看见的call rdx进行一个利用

二、先找到initial的值和我们的dl_fini函数进行一个异或得到一个pointer_guard的值

三、将我们的输入进行一次ror和与pointer_guard进行一次异或然后写到initial+0x18的这个段。理论上是可以成功的，但是尼由于太麻烦的原因我并没有去试过，也没有写exp，用的是另一种方法。

### <a name="%E7%AC%AC%E4%BA%8C%E4%B8%AA%E6%80%9D%E8%B7%AF"></a>第二个思路

一、利用dl_fini这里的一个call进行控制程序流

二、写函数_rtld _global+3842这个位置的低字节

三、这个可能有点毒毒就是在cat flag的时候要进行一个cat flag &gt; &amp;0重定向文件流的操作才能看见flag，应该是把stdout关掉了的原因

### <a name="exp"></a>exp



## 总结

hctf题目的质量真的高，做了几个题就做不下去了，但是学到了很多新的姿势还是很满足的。。。

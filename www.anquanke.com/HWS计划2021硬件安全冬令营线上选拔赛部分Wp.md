> 原文链接: https://www.anquanke.com//post/id/230816 


# HWS计划2021硬件安全冬令营线上选拔赛部分Wp


                                阅读量   
                                **197946**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t013dc5063315874c57.png)](https://p4.ssl.qhimg.com/t013dc5063315874c57.png)



二进制专场，Reverse做完了，内核安全做了1个，固件安全做了3个。总的来说，题目难度不是很大，但考点挺不错的，个人感觉还行。

## Reverse

### <a class="reference-link" name="decryption"></a>decryption

拿了二血。逆向方向的签到题，直接穷举。

```
#include &lt;stdio.h&gt;

unsigned char enc[] =
`{`
   18,  69,  16,  71,  25,  73,  73,  73,  26,  79, 
   28,  30,  82, 102,  29,  82, 102, 103, 104, 103, 
  101, 111,  95,  89,  88,  94, 109, 112, 161, 110, 
  112, 163
`}`;

int main(void)
`{`
    int i = 0, j = 0;

    for(i = 0; i &lt; 32; i++)
    `{`
        for(j = 32; j &lt; 127; j++)
        `{`

            int v3;
            int v5 = j;
            int v4 = i;
            do
            `{`
                v3 = 2 * (v4 &amp; v5);
                v5 ^= v4;
                v4 = v3;
            `}`
            while ( v3 );
            if((v5 ^ 0x23) == enc[i])
            `{`
                putchar(j);
                break;
            `}`
        `}`
    `}`
`}`
```

### <a class="reference-link" name="obfu"></a>obfu

这个题，被从伪代码来辨识变量的值坑到了，还是要从汇编代码来看靠谱。

首先题目有一个混淆，但很简单，patch掉方便点，但不patch也不影响。

[![](https://p3.ssl.qhimg.com/t01c06cae5af5b937c5.png)](https://p3.ssl.qhimg.com/t01c06cae5af5b937c5.png)

跟了挺久的加密过程，异或比较多，然后准备逆向的时候发现，AES的特征啊。开始以为是常规的aes的解密，但其实不然，加上题目几次异或对不熟悉aes加密来说迷惑性挺大的。

这样在这些加密函数徘徊了很久，不清楚这个aes到底要做什么。

最后看了看如果我们输入正确后要执行的函数，联想输入，加上这里函数少，识别起来相对容易些，发现就是使用我们输入当作key把密文进行AES解密。不确定的话还可以自己用数据执行这里的函数来测试一下。

由于这里的函数已经确定功能了，看看它们有没有在前面引用过，果然有的。这样就对我们分析前面起到了很大的帮助了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01a5bf3bd698b648a7.png)

这样后，再继续回到前面分析，总结一下流程：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0150629404d265faca.png)

解密过程：

把密文先异或一下，然后进行aes加密，其实是是多了个iv的CBC模式的AES加密，但这里只有一组。所以我直接ECB模式加密自己再异或一下。

```
import base64
from Crypto.Cipher import AES

class AesEncry(object):
    key = '8ce51f9350f44511a854e1b5f0a3fbca'
    key = bytes.fromhex(key)                     

    def encrypt(self, data):
        mode = AES.MODE_ECB
        padding = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
        cryptos = AES.new(self.key, mode)
        cipher_text = cryptos.encrypt(data)
        return cipher_text.hex()

    def decrypt(self, data):
        cryptos = AES.new(self.key, AES.MODE_ECB)
        decrpytBytes = base64.b64decode(data)
        meg = cryptos.decrypt(decrpytBytes).decode('utf-8')
        return meg.encode()

plaint = '4ff5e148c1d81254533e3a4bd47cfe72'
plaint = bytes.fromhex(plaint)
a = AesEncry().encrypt(plaint)
print(a)
```

各种异或操作：

```
#include &lt;stdio.h&gt;

unsigned char op1[] =
`{`
  198, 6, 38, 70, 102, 134, 166, 198, 231, 7, 
  38, 38, 70, 102, 134, 166
`}`;

unsigned char op2[] =
`{`
  42, 253, 103, 31, 159, 97, 45, 212, 252, 56, 
  118, 164, 182, 197, 194, 141
`}`;

unsigned char mem[] =
`{`
  33, 35, 47, 41, 122, 87, 165, 167, 67, 137, 
  74, 14, 74, 128, 31, 195
`}`;

unsigned char xor1[] =
`{`
  110, 214, 206, 97, 187, 143, 183, 243, 16, 183, 
  112, 69, 158, 252, 225, 177
`}`;

unsigned char key[] =
`{`
  140, 229, 31, 147, 80, 244, 69, 17, 168, 84, 
  225, 181, 240, 163, 251, 202
`}`;

unsigned char xor2[] = `{`236, 251, 65, 89, 249, 231,
                 139, 18, 27, 63, 80, 130, 240, 163, 68, 43`}`;
unsigned char ans[] = `{`192, 92, 50, 87, 127, 219,
                 63, 77, 148, 184, 254, 19, 7, 227, 85, 38`}`;

int main(void)
`{`
    int i = 0, j = 0;

    for(i = 0; i &lt; 16; i++)
    `{`
        mem[i] ^= xor1[i];
    `}`

    for(i = 0; i &lt; 16; i++)
    `{`
        op1[i] ^= op2[i];
    `}`

    for(i = 0; i &lt; 16; i++)
    `{`
        ans[i] ^= xor2[i];
    `}`

    for(i = 0; i &lt; 16; i++)
    `{`
        if(i != 0)
            printf(", ");
        printf("%#02x", ans[i]);
    `}`
`}`
```

移位还原：

```
#include &lt;stdio.h&gt;

int main(void)
`{`    
    unsigned char a[16] = `{`0x2c, 0xa7, 0x73, 0xe, 0x86, 0x3c, 0xb4, 0x5f,
                 0x8f, 0x87, 0xae, 0x91, 0xf7, 0x40, 0x11, 0xd`}`;
    int i = 0;
    unsigned char flag[16] = `{`0`}`;

    flag[15] = (a[15] &lt;&lt; 3) | ((a[0] &gt;&gt; 5)&amp;7); 
    for(i = 0; i &lt; 15; i++)
    `{`
        flag[i] = (a[i] &lt;&lt; 3) | ((a[i+1] &gt;&gt; 5)&amp;7); 
    `}`

    for(i = 0; i &lt; 16; i++)
    `{`
        printf("%02x", flag[i]);
    `}`
`}`
```

### <a class="reference-link" name="Enigma"></a>Enigma

程序取出inp文件中的数据，然后进行加密后以hex形式存放入enc文件。

关键就是其中的一个反调试：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d80419037b2a531e.png)

首先**SetUnhandledExceptionFilter**函数的作用：设置顶层未处理异常过滤器（top-level unhandled exception filter），捕获进程的各个线程中一切未被处理的结构化异常。简单来说就是修改系统最后的异常处理器。

然后触发**SetUnhandledExceptionFilter**的条件：
- 程序中有异常，但没有相应的操作操作去处理该异常。
- 程序不处于调试状态。
[![](https://p1.ssl.qhimg.com/t0182d0264e10775c72.png)](https://p1.ssl.qhimg.com/t0182d0264e10775c72.png)

满足条件后程序将执行设置的异常处理函数来处理该异常。

> 而一般程序中要么把设置的异常处理函数用来检测程序是否处于调试状态；要么隐藏程序的关键代码，让我们执行不到。

对于触发**SetUnhandledExceptionFilter**的条件，一般程序在调用**SetUnhandledExceptionFilter**后会有故意触发异常的代码，本题就是靠后面的执行无效指令进行触发。而程序是否处于调试状态其实是若出现的异常传递给了程序，程序先调用UnhandledExceptionFilter，而UnhandledExceptionFilter里面又调用了**ZwQueryInformationProcess**进行反调试检测，设置改函数的第二个参数为7，看执行完该函数后第三个参数指向的缓冲区是否为0，若不为0则程序处于调试状态，其实就是看有没有调试端口。

程序载入OD，设置忽略异常，ctrl+g，输入函数名字来到**ZwQueryInformationProcess**函数，然后下断。

[![](https://p0.ssl.qhimg.com/t014f15f11288e55759.png)](https://p0.ssl.qhimg.com/t014f15f11288e55759.png)

从栈窗口看到第2个参数为7，那就是要找的了，回溯到调用处，在函数执行完后将相应的缓存区的值改为0即可（若程序多次出现这种触发异常的跳转，那我们简单在执行完这个函数后hook一下程序方便些，本题的话直接把后面的je改为jmp就好了）。继续执行，就到了我们想执行的函数了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019e85eec9fec3bf14.png)

而我做本题的时候并没有去过这个反调试，使用的附加调试，然后简单调试了下那个设置为异常处理的函数，发现后面还要触发异常就开始静态分析。

首先找到引用最后存放加密数据数组的地方：很明显它上下其实是代码的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01350022802962323e.png)

手动转化一下上面的数据为代码，加上之前调试了下设置异常处理函数，然后很容易发现，代码中有很多用来触发异常的数据（0x0c7, 0xff，且后面跟着2个或3这操作数）。

又在分析循环代码是发现循环计数器每次没有变，那岂不无限循环，从这里又进而发现，程序每次触发异常跳到设置的异常处理函数的目的：获取当前的eip，修改寄存器的值，修改eip。

各种opcode的功能：

[![](https://p3.ssl.qhimg.com/t0174966a44f24394d1.png)](https://p3.ssl.qhimg.com/t0174966a44f24394d1.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0185321839445ecec6.png)

剩下的把相应的触发异常的代码替换为实际的操作，因为加密不复杂，直接看汇编代码分析下就好了。

首先一个通过指定的index进行一个置换操作，然后典型的移位或加密，最后一个异或。

```
#include &lt;stdio.h&gt;

unsigned char ind[50], ans[50], tmp;

unsigned char enc[] = `{`147, 139, 143, 67, 18, 104, 247,
                     144, 122, 75, 110, 66, 19, 1, 180, 33, 32, 115, 141, 104,
                     203, 25, 252, 248, 178, 107, 196, 171, 200, 155, 141, 34`}`;
char key[] = "Bier";
int main(void)
`{`
    int i = 0;
    char flag[100] = `{`0`}`;

    for(i = 0; i &lt; 32; i++)
    `{`
        tmp += 0x11;
        tmp &amp;= 0x1f;
        ind[i] = tmp;
        //printf("%02x ", tmp);
    `}`

    for(i = 1; i &lt; 32; i++)
    `{`
        enc[i] ^= key[i&amp;0x3];
    `}`

    for(i = 1; i &lt; 32; i++)
    `{`
        enc[i] ^= enc[i-1];
    `}`

    ans[0] = (enc[0] &gt;&gt; 3) | (enc[31] &lt;&lt; 5);
    for(i = 1; i &lt; 32; i++)
    `{`
        ans[i] = (enc[i] &gt;&gt; 3) | (enc[i-1] &lt;&lt; 5);
    `}`

    /*for(i = 0; i &lt; 32; i++)
    `{`
        printf("%02x ", ans[i]);
    `}`*/
    for(i = 0; i &lt; 32; i += 2)
    `{`
        flag[ind[i+1]] = ans[ind[i]];
        flag[ind[i]] = ans[ind[i+1]];
    `}`

    puts(flag);
`}` 
//B0mb3_L0nd0n_m0rg3n_um_v13r_Uhr.
```

### <a class="reference-link" name="babyre"></a>babyre

拿了二血。

程序其实利用调用号hook了系统调用r3到r0的转接层，所以从下图中的v11函数指针其实是去执行出题人自己设置的函数。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0170a29a212df16104.png)

简单跟进行一下v11指向的函数：开始对字符解密得到模块和函数名，就是为了得到函数**NtSetInformationThread**来进行反调试。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e2522c25606d6eb7.png)

对于这个反调试之前总结过：

[![](https://p0.ssl.qhimg.com/t011d8705535627dbe8.png)](https://p0.ssl.qhimg.com/t011d8705535627dbe8.png)

这里要过它直接patch掉就好了。

然后就是一些加载dll和函数代码解密相关的操作，做题时节省时间没管，现在还是看看：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010ec259be98e8d9d6.png)

使用资源查看工具，找到程序资源中改dll，明显看到是需要进行解密的，也就是后面的操作。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01a4754ac087e08d01.png)

继续跟进，看到解密操作只是一个异或：

[![](https://p0.ssl.qhimg.com/t01941d3393b9a9f110.png)](https://p0.ssl.qhimg.com/t01941d3393b9a9f110.png)

至于后面的操作就是得到相关的函数地址等。

最后跟到最后的加密函数：字符串就提示了sm4密码，且长度是16，那这个就是key了。sm4密码从常量0xA3B1BAC6也可以识别出来。

[![](https://p3.ssl.qhimg.com/t0148ea396af1d9b5fc.png)](https://p3.ssl.qhimg.com/t0148ea396af1d9b5fc.png)

这里把32的input分2次加密的，每次16位。使用密文解密一下即可。

```
from pysm4 import encrypt, decrypt
from Crypto.Util.number import *

c = bytes([234,  99,  88, 183, 140, 226, 161, 233, 197,  41, 
  143,  83, 232,   8,  50,  89, 175,  27, 103, 174, 
  217, 218, 207, 196, 114, 255, 177, 236, 118, 115, 
  243, 6])
key = b'Ez_5M4_C1pH@r!!!'
key = bytes_to_long(key)
c1 = bytes_to_long(c[0:16])
c2 = bytes_to_long(c[16:32])

flag1 = decrypt(c1, key)
flag2 = decrypt(c2, key)
flag = long_to_bytes(flag1)+long_to_bytes(flag2)
print(flag)

#42b061b4cb41cfa89ca78047bde1856e
```

### <a class="reference-link" name="child_protect"></a>child_protect

拿了二血。。

从题目名字就想到考点可能是程序自我创建反调试，升级一点就是Debug Blocker技术。尝试下了断点，发现不会断下。然后使用

procexp查看程序：果然，正如题目名字。

[![](https://p4.ssl.qhimg.com/t01d23685240881e4e4.png)](https://p4.ssl.qhimg.com/t01d23685240881e4e4.png)

> **Debug Blocker技术特点：**
<ul>
- **调试器与被调试器关系中，调试进程与被调试进程首先是一种父子关系。**
- **子进程进程已经被调试，不能在被其他调试器调试**
- **强制终止调试进程以切断调试器-被调试器关系时，被调试进程也会同时终止。**
- **父进程操作被子进程的代码**
- **父进程处理被子进程中发生的异常**
</ul>

来到creatprocess函数的地方看看：首先创建一个互斥体，目的是为了区别当前运行的是子进程还是父进程，进而执行不同的分支。接下来创建了一个进程。

[![](https://p3.ssl.qhimg.com/t01a3871f5863b85bce.png)](https://p3.ssl.qhimg.com/t01a3871f5863b85bce.png)

[![](https://p1.ssl.qhimg.com/t0115e11d1072ea2806.png)](https://p1.ssl.qhimg.com/t0115e11d1072ea2806.png)

然后就是子进程与父进程交互的过程：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01ad8c57a834d081d6.png)

具体交互过程：可以看到就2个，那我们不用把程序调试起来，直接手动或idapython修改子进程就行了。

[![](https://p0.ssl.qhimg.com/t016146e921467d50aa.png)](https://p0.ssl.qhimg.com/t016146e921467d50aa.png)

第一个就当作花指令处理nop掉多余代码，对于第二个：其实就是把函数中的0x8e32cdaa修改为0x73FF8CA6。

[![](https://p4.ssl.qhimg.com/t01b072bbfcdd3ffec9.png)](https://p4.ssl.qhimg.com/t01b072bbfcdd3ffec9.png)

把修复好的代码反编译：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01dc33991bfc00820b.png)

对于生成的key，因为计算有点繁琐，这里可以直接在程序运行时修改eip到sub_4110B9函数这里，然后当程序执行到后面时直接查看key。

最后的tea加密，只是多了一个变换字节序的操作，写解密时注意一下：

[![](https://p2.ssl.qhimg.com/t0191600340568688f2.png)](https://p2.ssl.qhimg.com/t0191600340568688f2.png)

```
#include &lt;stdio.h&gt;
#include &lt;string.h&gt;

unsigned char enc[] = `{`0xed, 0xe9, 0x8b, 0x3b, 0xd2, 0x85, 0xe7, 0xeb, 0x51, 0x16, 0x50, 0x7a, 0xb1, 0xdc, 0x5d, 0x9, 0x45, 0xae, 0xb9, 0x15, 0x4d, 0x8d, 0xff, 0x50,
                         0xde, 0xe0, 0xbc, 0x8b, 0x9b, 0xbc, 0xfe, 0xe1`}`;

unsigned int key[] = `{`0x82ABA3FE, 0x0AC1DDCA8, 0x87EC6B60, 0x0A2394568`}`;

void swap(unsigned char enc[])
`{`
    int i = 0;

    for(i = 0; i &lt; 2; i++)
    `{`
        unsigned char tmp = enc[i];
        enc[i] = enc[3-i];
        enc[3-i] = tmp;
    `}`
`}`

int main(void)
`{`
    int i = 0, v11 = 0x73FF8CA6, j = 0;

    for(i = 0; i &lt; 32; i += 4) //交换字节序
    `{`
        swap(enc+i);
    `}`

    for(i = 0; i &lt; 4; i++)
    `{`
        int delat = 0xc6ef3720;
        for(j = 0; j &lt; 32; j++)
        `{`
            *(((unsigned int *)(enc+8*i))+1) -= ((*((unsigned int *)(enc+8*i)) &gt;&gt; 5) + *(((unsigned int *)key)+3))^(delat+ *(((unsigned int *)(enc+8*i))))^((*((unsigned int *)(enc+8*i)))*0x10 + *(((unsigned int *)key)+2));
            *(((unsigned int *)(enc+8*i))) -= ((*(((unsigned int *)(enc+8*i)+1)) &gt;&gt; 5) + *(((unsigned int *)key)+1))^(delat+ *(((unsigned int *)(enc+8*i))+1))^((*(((unsigned int *)(enc+8*i))+1))*0x10 + *(((unsigned int *)key)+0));
            delat += 0x61c88647;
        `}`
    `}`


    for(i = 0; i &lt; 8; i++) //0xc6ef3720
    `{`
        *(unsigned int *)(enc + 4 * i) ^= v11;
        v11 -= 0x50FFE544;
    `}`

    for(i = 0; i &lt; 32; i += 4) //交换字节序
    `{`
        swap(enc+i);
    `}`

    for(i = 0; i &lt; 32; i++)
    `{`
        printf("%c", enc[i]);
    `}`    
`}`
```



## 内核安全

### <a class="reference-link" name="easy_kernel"></a>easy_kernel

题目给了一个r3层的程序和一个驱动程序。

首先r3层程序的情况：红色部分的调用是重点。。

[![](https://p5.ssl.qhimg.com/t01e626ecbb46befb8f.png)](https://p5.ssl.qhimg.com/t01e626ecbb46befb8f.png)

然后看看对于驱动文件情况：我们主要关注的就是偏移量为**IRP_MJ_DEVICE_CONTROL**的部分。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0114e9da40cf2fb8a7.png)

进入sub_401270，查看r0层对r3层发出请求的处理：看到0x222000正是r3层程序的值，开始一直以为这里key，正好8个字节，，因为识别了后面的算法为des。

[![](https://p1.ssl.qhimg.com/t016c1c46c5a0528cb1.png)](https://p1.ssl.qhimg.com/t016c1c46c5a0528cb1.png)

后面的des加密很好识别出来，然后开始使用密文和上面以为的key解密，不对，猜测也是。。因为r3层红色地方的调用我没搞清楚的。。

感觉还是调试起来才能做了，在本地这个驱动服务也没启动起来，然后找了个xp，成功调试起来。首先从des加密结果发现key其实是假flag的前8位且后面还有一个加密操作。才发现这个其实和从r3传过来的参数是对应的，-1这个标志很明显了。。。

[![](https://p3.ssl.qhimg.com/t01ab3bf6973852209a.png)](https://p3.ssl.qhimg.com/t01ab3bf6973852209a.png)

接下来就是看最后的红色代码调用，但只能单步步过，一单步步入就蓝屏😪。。也没心情去找原因。。

但我猜想这个最后加密肯定是不难的，，开始没注意以为是类似单表加密的，那我可以把0-255的每个加密值找到，再替换一下，试了多组数据后，发现了端倪。。并不是类似单表加密，看了一会了，，发现就是从一位开始一次异或后一位。。hha…

解密脚本：

```
from pyDes import des, ECB

def swap(a):
    for i in range(2):
        tmp = a[i]
        a[i] = a[3-i]
        a[3-i] = tmp
    return a[:4]

enc = [178, 196, 134, 213,  84, 108,  56, 173, 189, 105, 
  212, 233,  68,  71,  54,  33, 153, 145, 251,  19, 
  112, 216, 107, 228, 128,  18, 226,  67,  42,  75, 
   73, 142]

'''  
ans = []
for i in range(0, 32, 4):
    ans += swap(enc[i:])
'''
for i in range(len(enc)-2, -1, -1):
    enc[i] ^= enc[i+1]
enc = bytes(enc)

key = b'`}`aglf_T_'

des_obj = des(key, ECB, pad = None)

code = des_obj.decrypt(enc)
print(code)
#flag`{`WelcOme_to_kerne1_world!`}`
```

题虽然是做了，但上面红色部分的调用到底是什么呢。

经过一番搜索，首先从call fword ptr知道了这是个长调用，fword代表6个字节。而要想弄清处这个就要了解windows保护模式中的长调用和调用门，段描述符及段选择子的知识了。

这里就只简单涉及与本题相关的：

> <ul data-mark="-">
- 长调用开始是push调用者的CS和返回地址。因为最后返回也是多了操作，所以使用的retf。
- GDTR 寄存器存放的是GDT（全局描述符表）表的位置和大小，低两字节是gdt表的大小，高四字节是gdt表的地址。
- sgdt指令读取GDTR寄存器的值。
- 段选择子是一个16位的描述符，指向了定义该段的段描述符，而我们的长调用也就是使用的段选择子来决定。其中3至15位是一个索引，在GDT表中查找出段描述符；第1，2位为RPL，代表了请求特权的级别，如0，3；第三位为TI，如果为0，查GDT表。如果为1，查LDT表，windows中只用GDT，所以这位都是0。
- 调用门描述符，共8字节。高16-31位记录偏移地址的高地址，低0-15位记录偏移地址的低地址。低16-31位即是段选择子。
</ul>

再来看看调用门，指令格式CALL CS:EIP，注：EIP是没有使用的，也就是我们的长调用只看段寄存器CS的值，通过它找到对应的段描述符。

```
from ida_bytes import *
flag = ''
addr = 0x08000344
while addr &lt; 0x0800036E:
    flag += chr((get_byte(addr)^0x1e)+3)
    addr += 1
print(flag)
#flag`{`1749ac10-5389-11eb-90c1-001c427bd493`}`
```

### <a class="reference-link" name="STM"></a>STM

### <a class="reference-link" name="easy_bios"></a>easy_bios

首先将bios文件使用模拟器运行起来，从这得到了关键的字符串信息。

[![](https://p0.ssl.qhimg.com/t017095662f462625f2.png)](https://p0.ssl.qhimg.com/t017095662f462625f2.png)

尝试使用binwalk提取bios中的文件看看，提取出一个名为840A8的文件。

用010editor查看，发现了熟悉4D5A和紧跟着的5045，PE文件啊。。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e3f49ab0f40297e2.png)

突然想到刚刚得到的关键字符信息，尝试搜索看看，找到了Getflag，突然明朗起来：

[![](https://p0.ssl.qhimg.com/t0137968f11c0664db2.png)](https://p0.ssl.qhimg.com/t0137968f11c0664db2.png)

但要注意的是这个文件中很多个PE文件，提取出出现Getflag字符串的PE文件，进行反编译：

从字符串定位到关键函数：再从Your Input定位到v12是我们的输入。

[![](https://p3.ssl.qhimg.com/t011611b3c63517c120.png)](https://p3.ssl.qhimg.com/t011611b3c63517c120.png)

然后对于rc4加密，我们只关心最后的异或值，程序又运行不起来的，那把整个函数复制到到C编译器中简单修改一下再直接用来异或解密。

```
#include &lt;stdio.h&gt;

unsigned char enc[] =
`{`
  70, 119, 116, 176, 39, 142, 143, 91, 233, 216, 
  70, 156, 114, 231, 47, 94
`}`;

int main(void)
`{`
    char s[] = "OVMF_And_Easy_Bios";

    int i = 0, v13[514] = `{`0`}`, v2, v3, v4, v5, v6, v8;
    int v7, v9, v10, v11, v12, result;

    for ( i = 0; i != 256; ++i )
      `{`
        v13[i] = i;
        v13[i + 256] = s[i % 18];
      `}`
    v2 = 0;
    v3 = 0;
    do
    `{`
        v4 = v13[v2];
        v3 = (v13[v2 + 256] + v4 + v3) % 256;
        v5 = v13[v3];
        v13[v3] = v4;
        v13[v2++] = v5;
    `}`
    while ( v2 != 256 );
      v6 = 0;
      v7 = 0;
      v8 = 0;
    do
    `{`
        v8 = (v8 + 1);
        v9 = v13[v8];
        v10 = (v9 + v7) % 256;
        v11 = v13[v10];
        v13[v10] = v9;
        v7 = (v9 + v7) % 256;
        v13[v8] = v11;
        result = (unsigned int)v13[(v11 + v13[v10]) % 256];
        enc[v6++] ^= result;
    `}`
    while ( v6 != 16 );

    for(i = 0; i &lt; 16; i++)
    `{`
        printf("%02x", enc[i]);
    `}`
`}` 

//88baec0b5154f859b5851097bb567f5c
```

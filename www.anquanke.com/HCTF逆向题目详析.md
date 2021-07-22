> 原文链接: https://www.anquanke.com//post/id/165036 


# HCTF逆向题目详析


                                阅读量   
                                **197738**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t01803c9312f765ee2b.png)](https://p2.ssl.qhimg.com/t01803c9312f765ee2b.png)



## 前言

很有水平的一场比赛，RE的几道题目质量都非常高。

由于自己的原因，只是看了题，没做，感觉就算认真做，也做不出来几题，毕竟太菜。哈哈！

下面就先从最简单的开始写！



## seven

简单的签到题，只不过是放在了windows驱动里，从没接触过，稍微带来了一点麻烦，算法是很经典的吃豆子游戏，刚好看加解密时看到了，在键盘扫描码卡了很久。

关于驱动开发的一些API可以在[MDSN](https://docs.microsoft.com/en-us/windows-hardware/drivers/ddi/content/index)上找到相关说明

如DriverEntry函数就是一个驱动程序的入口函数，过多的我就不班门弄斧了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0145393e24b0375352.png)

总之这个题就是有不认识的API，就直接在MDSN上找函数说明即可。

关于解题，还是搜索字符串，找到The input is the flag字样，交叉引用到sub_1400012F0函数，如果看过加解密的同学，应该能一眼看出这是吃豆子游戏（这可不是打广告），细看还真是！

就是如下这个矩阵

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01033e271b1ac88a5b.png)

从o开始，沿着.走，一直走到7即可。

0x11 表示向上

0x1f 表示向下

0x1e 表示向左

0x20 表示向右

[![](https://p5.ssl.qhimg.com/t01cc33eba71f44a977.png)](https://p5.ssl.qhimg.com/t01cc33eba71f44a977.png)

当时一直在想0x11和输入的关系，最后才知道原来是键盘的扫描码，分别对应wasd

OK那么此题轻易的解决了！我是不是很水！

（下面几题都算是复现，我是一个没有感情的杀手！)



## LuckyStar

别看程序这么大只不是VS静态编译了而已。

其实也不难，一进来先搜索字符串，看到idaq.exe，x32dbg等常见调试器的字样，很明显有反调试，并且还看到一大段未识别的数据，感觉很像是自解码的部分，其实真正的加密部分就在这里。

[![](https://p0.ssl.qhimg.com/t01cf938b91f40b6ea8.png)](https://p0.ssl.qhimg.com/t01cf938b91f40b6ea8.png)

关于反调试，不必紧张，动态调试时手动修改下寄存器即可。通过交叉引用找到TlsCallback_0函数，判断之前下断，绕过即可（直接patch比较方便）。

之后便是程序的自解密部分，最后便可以看到真正的加密的过程。

[![](https://p4.ssl.qhimg.com/t016047d0c1c19e0664.png)](https://p4.ssl.qhimg.com/t016047d0c1c19e0664.png)

[![](https://p0.ssl.qhimg.com/t01ddd92da0f41e1eae.png)](https://p0.ssl.qhimg.com/t01ddd92da0f41e1eae.png)

将00401780至00401939 undefine一下然后重新create function，IDA便可以识别，接下来的一段解密也是类似的，最后进行一个比较。有一点需要注意，在动调时候不知道什么情况，程序就蹦了，需要手动在401780函数处set ip然后跳转过去

[![](https://p5.ssl.qhimg.com/t010b63ede6b7d4191c.png)](https://p5.ssl.qhimg.com/t010b63ede6b7d4191c.png)

加密部分其实就是变形的base64加上一个异或，类似的题目做的太多了，解密脚本如下：

```
else if ( switch_code == 0x176 )
  `{`
    v3 = dword_405160;
    result = dword_4050C0[0];
    v4 = dword_4050C0[0];
    for ( k = 8; k; --k )
    `{`
      result = 9 * k;
      dword_405040[9 * k] = dword_405040[9 * (k - 1)];
    `}`
    dword_405040[0] = v3;
    for ( l = 0; l &lt; 8; ++l )
    `{`
      dword_4050C0[l] = dword_4050C4[l];
      result = l + 1;
    `}`
    dword_4050E0 = v4;
  `}`
```

## Spiral

### checkgatetwo

> <p>Reads the CR0 register and returns its value.<br>
This intrinsic is only available in kernel mode, and the routine is only available as an intrinsic.</p>

> Returns the EFLAGS value from the caller’s context.

> 我之前在看加解密时看到过VT技术，不过太菜没看懂，趁着这个机会好好学习一下，下文关于指令部分大多参考自网上资料。

简单的移位变换。

invd对应三种变换方式（略）

vmcall根据op的不同进行相应的运算。

以vmcall(0x30133403);为例进行一个说明：

```
def init_box():
    result = data[40]
    v6 = data[40]
    for i in range(4):
        data[8*i+40]=data[8*i+40-1]
        for j in range(2*i+1):
            data[3 - i + 9 * (i + 4 - j)]=data[3 - i + 9 * (i + 4 - (j + 1))]
        for k in range(2 * i + 2):
            data[k + 9 * (3 - i) + 3 - i] = data[10 * (3 - i) + k + 1]
        for l in range(2 * i + 2):
            data[9 * (l + 3 - i) + i + 5] = data[9 * (3 - i + l + 1) + i + 5]
        m=0
        while m &lt; result:
            result = 2*i+2
            data[9 * (i + 5) + i + 5 - m] = data[9 * (i + 5) + i + 5 - (m + 1)]
            m+=1
    data[72]=v6
```

然后会进入cpuid_func

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01bbd114643c24565d.png)

类似的，代码如下：

```
def cpuid_func(switch_code):
    if switch_code == 0xDEADBEEF:
        for i in range(10):
            op[i]^=key1[i]
    elif switch_code == 0xCAFEBABE:
        for j in range(10):
            op[j]^=key2[j]
```

#### 0x2

接下来恢复invd_func：

```
def invd_func(switch_code):
    if switch_code == 0x4433:
        for i in range(5):
            v0 = op[2*i]
            op[2*i]=op[2*i+1]
            op[2*i+1]=v0
    elif switch_code == 0x4434:
        v5 = op[0]
        for j in range(9):
            op[j]=op[j+1]
        op[9]=v5
    elif switch_code == 0x4437:
        v3 = op[7]
        for k in range(3):
            op[k+7]=op[7-k-1]
            if k == 2:
                op[7-k-1]=op[3]
            else:
                op[7-k-1]=op[k+7+1]
        for l in range(1):
            op[3]=op[3-l-2]
            op[3-l-2]=op[3-l-1]
        op[3-1-1]=v3
```

#### 0x3

接下来便会进入vmcalls函数进行一系列变换，最后我们恢复出rdmsr和vmcall函数

dword_405170的转换过程可以如下计算：

[![](https://p2.ssl.qhimg.com/t01452f93add3798119.png)](https://p2.ssl.qhimg.com/t01452f93add3798119.png)

```
def rdmsr(switch_code):
    if switch_code == 0x174:
        v6=data[80]
        v7=data[8]
        for i in range(8,0,-1):
            data[10*i]=data[9*(i-1)+i-1]
        data[0]=v6
        for j in range(1,9):
            data[8*j]=data[8*j+8]
        data[8*9]=v7            # Look at me!!!
    if switch_code == 0x176:
        v3 = data[76]
        result = data[36]
        v4 = data[36]
        for k in range(8,0,-1):
            result = 9*k
            data[9*k+4]=data[9*(k-1)+4]
        data[4]=v3
        for l in range(8):
            data[l+36]=data[l+37]
            result=l+1
        data[44]=v4
```

其中在rdmsr遇到了一个坑

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0199db6031a61991ed.png)

dword_405030[8 * j] = v7;此时j应该为9，而在使用python的for语句时data[8*j]=v7此时的j为8，这也就直接导致，我调试了好久.23333

```
def vmcall_func(switch_code):
    v1 = (switch_code &gt;&gt; 24)
    i = ((switch_code&gt;&gt;16)&amp;0xf)+9*((((switch_code&gt;&gt;16)&amp;0xff)&gt;&gt;4)&amp;0xf)
    byte_switch_code = switch_code&amp;0xff
    if ((switch_code&gt;&gt;8)&amp;0xff == 0xcc):
        d_input = m_input
    else:
        d_input = m_input[::-1]

    if v1 == op[0]:
        data[i]=d_input[byte_switch_code]
    elif v1 == op[1]:
        data[i]+=d_input[byte_switch_code]
        data[i]&amp;=0xff
    elif v1 == op[2]:
        data[i]-=d_input[byte_switch_code]
        data[i]&amp;=0xff
    elif v1 == op[3]:
        data[i]=data[i]/d_input[byte_switch_code]
        data[i]&amp;=0xFF
    elif v1 == op[4]:
        data[i]*=d_input[byte_switch_code]
        data[i]&amp;=0xFF
    elif v1 == op[5]:
        data[i]^=d_input[byte_switch_code]
        data[i]&amp;=0xFF
    elif v1 == op[6]:
        data[i]^=d_input[byte_switch_code-1]+d_input[byte_switch_code]-d_input[byte_switch_code+1]
        data[i]&amp;=0xFF
    elif v1 == op[7]:
        data[i]^=d_input[byte_switch_code]*16
        data[i]&amp;=0xFF
    elif v1 == op[8]:
        data[i]|=d_input[byte_switch_code]
        data[i]&amp;=0xFF
    elif v1 == op[9]:
        data[i]^=d_input[byte_switch_code+1]^d_input[byte_switch_code-1]^(d_input[byte_switch_code-2]+d_input[byte_switch_code]-d_input[byte_switch_code+2])
        data[i]&amp;=0xFF
    elif v1 == 0xDD:
        print "vmx_off"
    elif v1 == 0xFF:
        check()
        return
    else:
        print "error"
```

注意操作符的运算顺序，python在带来便利的同时，也会为我们带来困扰。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010883a47e6533ca8f.png)

最后会进行check函数，据出题人证实确实是代码写错了，但是并不影响我们解题。check的过程其实就是对数独进行校验的过程，基于此我们进行恢复。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t010bae1d475c131472.png)

off_405534是check_data的指针

```
def check():
    for n in range(9):
        v5=[0 for m in range(9)]
        for i in range(9):
            v5[i]=data[((check_data[n]+i)&amp;0xF)+9 * (((check_data[n]+i) &gt;&gt; 4) &amp; 0xF)]
            s.add(v5[i]&gt;0,v5[i]&lt;10)
        for j in range(8):
            for k in range(j+1,9):
                s.add(v5[j]!=v5[k])
```

这里使用z3求解器，添加了约束条件。接下来将z3求解的相应代码补全。相关的数据可以通过lazyida插件进行导出。最终完整代码如下：

```
def gate_one():
    static_data=[0x07, 0xE7, 0x07, 0xE4, 0x01, 0x19, 0x03, 0x50, 0x07, 0xE4, 0x01, 0x20, 0x06, 0xB7, 0x07, 0xE4, 0x01, 0x22, 0x00, 0x28, 0x00, 0x2A, 0x02, 0x54, 0x07, 0xE4, 0x01, 0x1F, 0x02, 0x50, 0x05, 0xF2, 0x04, 0xCC, 0x07, 0xE4, 0x00, 0x28, 0x06, 0xB3, 0x05, 0xF8, 0x07, 0xE4, 0x00, 0x28, 0x06, 0xB2, 0x07, 0xE4, 0x04, 0xC0, 0x00, 0x2F, 0x05, 0xF8, 0x07, 0xE4, 0x04, 0xC0, 0x00, 0x28, 0x05, 0xF0, 0x07, 0xE3, 0x00, 0x2B, 0x04, 0xC4, 0x05, 0xF6, 0x03, 0x4C, 0x04, 0xC0, 0x07, 0xE4, 0x05, 0xF6, 0x06, 0xB3, 0x01, 0x19, 0x07, 0xE3, 0x05, 0xF7, 0x01, 0x1F, 0x07, 0xE4]
    s=''
    for i in range(0, len(static_data), 2):
        op = static_data[i]
        op_data = static_data[i+1]
        if op == 0:
            op_data-=34
        if op == 1:
            op_data-=19
        if op == 2:
            op_data-=70
        if op == 3:
            op_data-=66
        if op == 4:
            op_data^=0xca
        if op == 5:
            op_data^=0xfe
        if op == 6:
            op_data^=0xbe
        if op == 7:
            op_data^=0xef
        s+=chr(op|((op_data&lt;&lt;3)&amp;0x78))
    print s

def init_box():
    result = data[40]
    v6 = data[40]
    for i in range(4):
        data[8*i+40]=data[8*i+40-1]
        for j in range(2*i+1):
            data[3 - i + 9 * (i + 4 - j)]=data[3 - i + 9 * (i + 4 - (j + 1))]
        for k in range(2 * i + 2):
            data[k + 9 * (3 - i) + 3 - i] = data[10 * (3 - i) + k + 1]
        for l in range(2 * i + 2):
            data[9 * (l + 3 - i) + i + 5] = data[9 * (3 - i + l + 1) + i + 5]
        m=0
        while m &lt; result:
            result = 2*i+2
            data[9 * (i + 5) + i + 5 - m] = data[9 * (i + 5) + i + 5 - (m + 1)]
            m+=1
    data[72]=v6

def cpuid_func(switch_code):
    if switch_code == 0xDEADBEEF:
        for i in range(10):
            op[i]^=key1[i]
    elif switch_code == 0xCAFEBABE:
        for j in range(10):
            op[j]^=key2[j]

def invd_func(switch_code):
    if switch_code == 0x4433:
        for i in range(5):
            v0 = op[2*i]
            op[2*i]=op[2*i+1]
            op[2*i+1]=v0
    elif switch_code == 0x4434:
        v5 = op[0]
        for j in range(9):
            op[j]=op[j+1]
        op[9]=v5
    elif switch_code == 0x4437:
        v3 = op[7]
        for k in range(3):
            op[k+7]=op[7-k-1]
            if k == 2:
                op[7-k-1]=op[3]
            else:
                op[7-k-1]=op[k+7+1]
        for l in range(1):
            op[3]=op[3-l-2]
            op[3-l-2]=op[3-l-1]
        op[3-1-1]=v3

def rdmsr(switch_code):
    if switch_code == 0x174:
        v6=data[80]
        v7=data[8]
        for i in range(8,0,-1):
            data[10*i]=data[9*(i-1)+i-1]
        data[0]=v6
        for j in range(1,9):
            data[8*j]=data[8*j+8]
        data[8*9]=v7            # Look at me!!!
    if switch_code == 0x176:
        v3 = data[76]
        result = data[36]
        v4 = data[36]
        for k in range(8,0,-1):
            result = 9*k
            data[9*k+4]=data[9*(k-1)+4]
        data[4]=v3
        for l in range(8):
            data[l+36]=data[l+37]
            result=l+1
        data[44]=v4

def check():
    for n in range(9):
        v5=[0 for m in range(9)]
        for i in range(9):
            v5[i]=data[((check_data[9*n+i])&amp;0xF)+9 * ((((check_data[9*n+i])) &gt;&gt; 4) &amp; 0xF)]
            s.add(v5[i]&gt;0,v5[i]&lt;10)
        for j in range(9):
            for k in range(j+1,9):
                s.add(v5[j]!=v5[k])

def vmcall_func(switch_code):
    v1 = (switch_code &gt;&gt; 24)
    i = ((switch_code&gt;&gt;16)&amp;0xf)+9*((((switch_code&gt;&gt;16)&amp;0xff)&gt;&gt;4)&amp;0xf)
    byte_switch_code = switch_code&amp;0xff
    if ((switch_code&gt;&gt;8)&amp;0xff == 0xcc):
        d_input = m_input
    else:
        d_input = m_input[::-1]

    if v1 == op[0]:
        data[i]=d_input[byte_switch_code]
    elif v1 == op[1]:
        data[i]+=d_input[byte_switch_code]
        data[i]&amp;=0xff
    elif v1 == op[2]:
        data[i]-=d_input[byte_switch_code]
        data[i]&amp;=0xff
    elif v1 == op[3]:
        data[i]=data[i]/d_input[byte_switch_code]
        data[i]&amp;=0xFF
    elif v1 == op[4]:
        data[i]*=d_input[byte_switch_code]
        data[i]&amp;=0xFF
    elif v1 == op[5]:
        data[i]^=d_input[byte_switch_code]
        data[i]&amp;=0xFF
    elif v1 == op[6]:
        data[i]^=d_input[byte_switch_code-1]+d_input[byte_switch_code]-d_input[byte_switch_code+1]
        data[i]&amp;=0xFF
    elif v1 == op[7]:
        data[i]^=d_input[byte_switch_code]*16
        data[i]&amp;=0xFF
    elif v1 == op[8]:
        data[i]|=d_input[byte_switch_code]
        data[i]&amp;=0xFF
    elif v1 == op[9]:
        data[i]^=d_input[byte_switch_code+1]^d_input[byte_switch_code-1]^(d_input[byte_switch_code-2]+d_input[byte_switch_code]-d_input[byte_switch_code+2])
        data[i]&amp;=0xFF
    elif v1 == 0xDD:
        print "vmx_off"
    elif v1 == 0xFF:
        check()
        return
    else:
        print "error"

from z3 import *
s=Solver()
m_input = [BitVec("fla%d"%i,32) for i in range(27)]
for i in m_input:
    s.add(i&gt;32,i&lt;127)

op=[0xA3,0xF9,0x77,0xA6,0xC1,0xC7,0x4E,0xD1,0x51,0xFF]
key1=[0x00000090, 0x000000CD, 0x00000040, 0x00000096, 0x000000F0, 0x000000FE, 0x00000078, 0x000000E3, 0x00000064, 0x000000C7]
key2=[0x00000093, 0x000000C8, 0x00000045, 0x00000095, 0x000000F5, 0x000000F2, 0x00000078, 0x000000E6, 0x00000069, 0x000000C6]
data=[0x00000007, 0x000000CE, 0x00000059, 0x00000023, 0x00000009, 0x00000005, 0x00000003, 0x00000001, 0x00000006, 0x00000002, 0x00000006, 0x00000005, 0x0000007D, 0x00000056, 0x000000F0, 0x00000028, 0x00000004, 0x00000059, 0x0000004D, 0x0000004D, 0x0000004B, 0x00000053, 0x00000009, 0x00000001, 0x0000000F, 0x00000057, 0x00000008, 0x000000D3, 0x00000038, 0x0000006F, 0x00000299, 0x000000E1, 0x00000036, 0x00000002, 0x00000076, 0x00000357, 0x0000006A, 0x000000AA, 0x00000374, 0x000001A4, 0x0000005D, 0x00000056, 0x00000057, 0x00000007, 0x0000007F, 0x00000008, 0x000000A8, 0x000000B0, 0x00000009, 0x00000032, 0x00000002, 0x00000006, 0x00000463, 0x00000469, 0x00000005, 0x000000C6, 0x00000002, 0x00000025, 0x00000068, 0x00000033, 0x00000032, 0x00000067, 0x00000001, 0x00000071, 0x00000001, 0x00000507, 0x00000063, 0x00000008, 0x00000006, 0x000000A3, 0x000005F5, 0x00000006, 0x00000031, 0x000003B8, 0x00000065, 0x00000200, 0x00000028, 0x00000057, 0x00000001, 0x000000A5, 0x00000009]
check_data=[0x00000000, 0x00000001, 0x00000002, 0x00000003, 0x00000012, 0x00000013, 0x00000014, 0x00000023, 0x00000024, 0x00000004, 0x00000005, 0x00000006, 0x00000007, 0x00000008, 0x00000015, 0x00000017, 0x00000027, 0x00000037, 0x00000010, 0x00000020, 0x00000030, 0x00000031, 0x00000040, 0x00000050, 0x00000051, 0x00000052, 0x00000060, 0x00000011, 0x00000021, 0x00000022, 0x00000032, 0x00000033, 0x00000034, 0x00000035, 0x00000041, 0x00000042, 0x00000016, 0x00000025, 0x00000026, 0x00000036, 0x00000043, 0x00000044, 0x00000045, 0x00000046, 0x00000054, 0x00000018, 0x00000028, 0x00000038, 0x00000048, 0x00000058, 0x00000067, 0x00000068, 0x00000078, 0x00000088, 0x00000047, 0x00000055, 0x00000056, 0x00000057, 0x00000065, 0x00000066, 0x00000076, 0x00000077, 0x00000087, 0x00000053, 0x00000062, 0x00000063, 0x00000064, 0x00000072, 0x00000074, 0x00000075, 0x00000085, 0x00000086, 0x00000061, 0x00000070, 0x00000071, 0x00000073, 0x00000080, 0x00000081, 0x00000082, 0x00000083, 0x00000084]

init_box()
cpuid_func(0xDEADBEEF)
invd_func(0x4437)
rdmsr(0x174)

rdmsr(0x176)                                 
invd_func(0x4433)                               
vmcall_func(0x30133403)                         
vmcall_func(0x3401CC01)
vmcall_func(0x36327A09)
vmcall_func(0x3300CC00)
vmcall_func(0x3015CC04)
vmcall_func(0x35289D07)
vmcall_func(0x3027CC06)
vmcall_func(0x3412CC03)
vmcall_func(0x3026CD06)
vmcall_func(0x34081F01)
vmcall_func(0x3311C302)
vmcall_func(0x3625CC05)
vmcall_func(0x3930CC07)
vmcall_func(0x37249405)
vmcall_func(0x34027200)
vmcall_func(0x39236B04)
vmcall_func(0x34317308)
vmcall_func(0x3704CC02)

invd_func(0x4434)
vmcall_func(0x38531F11)
vmcall_func(0x3435CC09)
vmcall_func(0x3842CC0A)
vmcall_func(0x3538CB0B)
vmcall_func(0x3750CC0D)
vmcall_func(0x3641710D)
vmcall_func(0x3855CC0F)
vmcall_func(0x3757CC10)
vmcall_func(0x3740000C)
vmcall_func(0x3147010F)
vmcall_func(0x3146CC0B)
vmcall_func(0x3743020E)
vmcall_func(0x36360F0A)
vmcall_func(0x3152CC0E)
vmcall_func(0x34549C12)
vmcall_func(0x34511110)
vmcall_func(0x3448CC0C)
vmcall_func(0x3633CC08)

invd_func(0x4437)
vmcall_func(0x3080CC17)
vmcall_func(0x37742C16)
vmcall_func(0x3271CC14)
vmcall_func(0x3983CC19)
vmcall_func(0x3482BB17)
vmcall_func(0x3567BC15)
vmcall_func(0x3188041A)
vmcall_func(0x3965CC12)
vmcall_func(0x32869C19)
vmcall_func(0x3785CC1A)
vmcall_func(0x3281CC18)
vmcall_func(0x3262DC14)
vmcall_func(0x3573CC15)
vmcall_func(0x37566613)
vmcall_func(0x3161CC11)
vmcall_func(0x3266CC13)
vmcall_func(0x39844818)
vmcall_func(0x3777CC16)
vmcall_func(0xFFEEDEAD)

print s.check()
while(s.check()==sat):
    m = s.model()
    flag2 = ""
    for i in m_input:
        flag2 += chr(m[i].as_long())
    print(flag2)
    exp = []
    for val in m_input:
        exp.append(val!=m[val])
    s.add(Or(exp))
gate_one()
```

> <p>1、最后在恢复代码的时候确实是很累的活，将伪C代码转换为python脚本，中间还是有一些部分需要去理解的，自己动手恢复一遍会收获很多。<br>
2、由于写的时候，时间跨度比较大，函数名和截图不一定能对上号，双手奉上idb，作为参考。<br>
3、相关的idb已上传至网盘</p>

相关附件<br>[https://pan.baidu.com/s/1FYjUhx7H1Gjx0y7rbyqocQ](https://pan.baidu.com/s/1FYjUhx7H1Gjx0y7rbyqocQ) 密码:182w



## 总结

这篇文章经历的时间有点长了，不过总算是结尾了，也算是善始善终。在写作期间，先后也查看了许多别人的解法，但是总归没有自己动手。如此详实的记载一遍，一方面切实能自己动手完整的解题并留下宝贵的过程，另一面也可以分享出来给大家作为参考。文中必定还有许多内容值得推敲，如有问题，还请大家指出。



## 最后

v爷爷的[出题思路](https://bbs.pediy.com/thread-247741.htm)

夜影师傅的[解题思路](https://bbs.pediy.com/thread-247741.htm)

> 看到没有！这就是大佬！ORZ～

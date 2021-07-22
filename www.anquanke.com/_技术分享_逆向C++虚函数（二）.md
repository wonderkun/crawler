> 原文链接: https://www.anquanke.com//post/id/85585 


# 【技术分享】逆向C++虚函数（二）


                                阅读量   
                                **112924**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://alschwalm.com/blog/static/2017/01/24/reversing-c-virtual-functions-part-2-2/](https://alschwalm.com/blog/static/2017/01/24/reversing-c-virtual-functions-part-2-2/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t013cf6275a59cd4b0b.jpg)](https://p5.ssl.qhimg.com/t013cf6275a59cd4b0b.jpg)



翻译：[维一零](http://bobao.360.cn/member/contribute?uid=32687245)

预估稿费：200RMB（不服你也来投稿啊！）

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿

传送门：[【技术分享】逆向C++虚函数（一）](http://bobao.360.cn/learning/detail/3332.html)



**前言**

在[**上一部分中，**](https://alschwalm.com/blog/static/2016/12/17/reversing-c-virtual-functions/)我描述了一种在小型C ++程序中“反虚拟化”函数调用的方法。当然，这种方法有一些限制，即它非常的手工。如果目标二进制包含成千上万个虚表，手动去定位虚表并创建这些结构及关系是不实际的。

因此，在本部分中，我将详细介绍虚表的布局，以及如何用可编程的方式找到它们。我也将展示某些时候我们可以如何恢复这些虚表之间的关系（以及它们之间的关联类型）。

但首先我需要描述这套适用的二进制文件集。在第一部分中我提到，与虚表布局相关的大多数事情没有在标准规范中指定，因此往往会因编译器而异。这是因为C ++标准需要适配而无论底层架构如何。如果规范指定了一些特定的虚表布局，那在某些架构上可能是低效的，这就不好了。该架构的编译器开发人员将需要在性能与合规性之间进行选择（那就超越了原本规范）。

然而，因为由不同编译器生成的程序经常需要交互（最值得注意的是，对于动态链接来说），编译器开发人员要协商对虚表布局，异常实现等的一些补充规范。其中最常见的是[**英特尔 C ++ ABI**](https://mentorembedded.github.io/cxx-abi/abi.html)。此标准由GCC，clang，ICC和许多其他编译器（但值得注意的是，非Visual Studio）实现。我下面的描述将适用于这些编译器。

英特尔 ABI在某些方面仍然模糊不清的。例如，它没有声明应该使用哪些段来存储虚表。所以我将进一步说明，我描述的GCC是基于英特尔的特定品牌。因此，本质上，我描述的是以下突出显示的部分：

[![](https://p1.ssl.qhimg.com/t019bda7f208628e237.png)](https://p1.ssl.qhimg.com/t019bda7f208628e237.png)

此外，做出以下假设：

1、RTTI被禁用（如果它打开，将会更容易些）；

2、该程序不会出现虚拟继承；

不幸的是，讨论这将大大增加这个话题的复杂性，并且因为虚拟继承有点不常见，所以我认为这里值得去探讨；

3、这些都是32位二进制文件。

<br>

**更多关于虚表布局**

在我们继续之前，回想一下，在第1部分中，我们将虚表描述为二进制数据段中连续的函数指针集合。我们还可以说该数组应该只由它的第一个元素来进行引用，因为其他元素将作为这个数组的偏移量被访问。

```
.rodata:08048D48 off_8048D48     dd offset sub_8048B6E
.rodata:08048D4C                 dd offset sub_8048BC2
.rodata:08048D50                 dd offset sub_8048BE0
```

这是一个来自二进制的部分，看起来似乎符合上面的定义。它是在'.rodata'段中3个函数指针的数组，并且只有0x08048D48引用了该指针。原来，它是一个虚表，这个启发好吗？如果我们要编译以下代码：

```
#include &lt;iostream&gt;
#include &lt;cstdlib&gt;
struct Mammal `{`
  Mammal() `{`   std::cout &lt;&lt; "Mammal::Mammaln"; `}`
  virtual ~Mammal() `{``}`
  virtual void walk() `{`   std::cout &lt;&lt; "Mammal::walkn"; `}`
`}`;
struct Cat : Mammal `{`
  Cat() `{`   std::cout &lt;&lt; "Cat::Catn"; `}`
  virtual ~Cat() `{``}`
  virtual void walk() `{`   std::cout &lt;&lt; "Cat::walkn"; `}`
`}`;
struct Dog : Mammal `{`
  Dog() `{`   std::cout &lt;&lt; "Dog::Dogn"; `}`
  virtual ~Dog() `{``}`
  virtual void walk() `{`   std::cout &lt;&lt; "Dog::walkn"; `}`
`}`;
struct Bird `{`
  Bird() `{`   std::cout &lt;&lt; "Bird::Birdn"; `}`
  virtual ~Bird() `{``}`
  virtual void fly() `{`   std::cout &lt;&lt; "Bird::flyn"; `}`
`}`;
//NOTE:   this may not be taxonomically correct
struct Bat : Bird, Mammal `{`
  Bat() `{`   std::cout &lt;&lt; "Bat::Batn"; `}`
  virtual ~Bat() `{``}`
  virtual void fly() `{`   std::cout &lt;&lt; "Bat::flyn"; `}`
`}`;
int main() `{`
  Bird *b;
  Mammal* m;
  if (rand() % 2) `{`
    b = new Bat();
    m = new Cat();
  `}` else `{`
    b = new Bird();
    m = new Dog();
  `}`
  b-&gt;fly();
  m-&gt;walk();
`}`
```

[view raw](https://gist.github.com/ALSchwalm/5a8cd4928eb8e3c1d2993a7acc0099d1/raw/a3be3e673dda73e70269bcdf2107541fb2a14fe1/reversing-part-2-1.cpp)[reversing-part-2-1.cpp](https://gist.github.com/ALSchwalm/5a8cd4928eb8e3c1d2993a7acc0099d1#file-reversing-part-2-1-cpp) hosted with ❤ by [GitHub](https://github.com/)

我们希望那里将有5张虚函数表，分别为Mammal，Cat，Dog，Bird，和Bat。但你可能已经猜到，事情不是那么简单。实际上，在满足上述标准的二进制中有6个区域。当你考虑具有多重继承的对象布局时就会清楚为什么如此。

[![](https://p3.ssl.qhimg.com/t01219d5ea5835d16ee.png)](https://p3.ssl.qhimg.com/t01219d5ea5835d16ee.png)

注意，Bat包含一个Bird和Mammal的完整实例（称为子对象）并且每个子对象都有一个vptr。这些指针指向不同的虚函数表。因此，具有多个父类型的对象类型在二进制中对应每个父类型都有一张虚表。英特尔 ABI将这些称为“虚表组”。

**<br>**

**虚表组**

虚表组由第一个父类型的主表和任意数量的次表组成，次表对应在第一个父表后面的每个父类型。这些表在二进制中按照在源代码中声明父类型的顺序相邻。考虑到这一点，我们期望Bat的虚表组是这样的：

[![](https://p1.ssl.qhimg.com/t01421d8314ca80cca8.png)](https://p1.ssl.qhimg.com/t01421d8314ca80cca8.png)

每个虚表需要12个字节。回顾第1部分内容，每个虚表将有两个析构函数，并且因为Bat没有重写walk，我们期望从 Mammal继承的walk出现在Bat表中。然而，如果我们检查二进制文件，并没有在.rodata段看到任何地方有连续的6个函数指针。

如果我们更仔细地看看英特尔的规范，可以找到原因。虚表不仅包括函数指针。实际上一个虚表看起来更像这样：

[![](https://p4.ssl.qhimg.com/t016af24d4a3dd68ca0.png)](https://p4.ssl.qhimg.com/t016af24d4a3dd68ca0.png)

**<br>**

**英特尔虚表布局（无虚拟继承）**

该RTTI pointer通常指向一个RTTI结构体（在英特尔规范中也有描述）。但是，由于我们假设了RTTI被禁用，所以它将总是0。而offset to top的值等于必须添加的this指针的大小，通过这个指针可以获取从某个子对象到自身对象的起始位置。这点可能有些混乱，所以为了更清楚，观察下面的代码：

```
Bat* bat = new Bat();
Bird* b = bat;
Mammal* m = bat;
```

[**view raw**](https://gist.github.com/ALSchwalm/4d31be0344b8d1ff61ebbea1a94b0f3b/raw/47911166844814871c2758e8b727a7cd1b63388a/reversing-part-2-2.cpp)[**reversing-part-2-2.cpp**](https://gist.github.com/ALSchwalm/4d31be0344b8d1ff61ebbea1a94b0f3b#file-reversing-part-2-2-cpp)** hosted with ❤ by **[**GitHub**](https://github.com/)

这些分配的b和m都是有效的。第一个不需要任何指令。一个 Bat就是一个Bird，因为Bird是它的第一个父类型，在任何Bat对象的开始都是Bird子对象。因此，指向Bat的指针也是指向Bird的指针。这就像正常，单一继承。

但是，分配m确实需要额外一些工作。在Bat里面的子对象Mammal不是开头对象，所以编译器必须插入一些指令到bat，使其指向其Mammal子对象。添加的值将是Bird的大小（对齐）。此值的负值将存储在offset to top字段中。

虚表的这个offset to top组件允许我们轻松地识别虚表组。一个虚表组将由在offset to top中具有缩减值的那些连续的虚表组成。考虑下图：

[![](https://p5.ssl.qhimg.com/t010cfdc36bdaa645d8.png)](https://p5.ssl.qhimg.com/t010cfdc36bdaa645d8.png)

从上面的源代码构建的二进制文件中找到了6张虚表。注意到，第2张表有个-4的值（0xFFFFFFFC作为有符号整数）属于它的字段offset to top，而其他表的此字段值为0。此外，正如我们所预期的，每个RTTI指针为0。这里数值-4告诉我们两件事：

1、第2张表是虚表组中的次表（因为offset to top非0）；

2、与第1张表有关的类型大小是4。请注意，因为第1张和第2张形成虚表组，和表1关联的类型大小实际上是部分对象的大小（即一个子对象）。

**<br>**

**以编程方式查找虚表**

根据上述内容，我们可以设计以下简单的程序来从二进制查找虚表（组）：



一个简单的脚本，用于在带有英特尔 ABI的二进制文件中定位vtable组。请注意，此脚本不考虑虚拟继承（更值得注意的），或虚表包含空指针的情况。这可能在最近的编译器处理纯抽象类时发生。

```
import idaapi
import   idautils
def read_ea(ea):
    return (ea+4,   idaapi.get_32bit(ea))
def read_signed_32bit(ea):
    return (ea+4,   idaapi.as_signed(idaapi.get_32bit(ea), 32))
def get_table(ea):
      '''给定一个地址，对位于该地址的表返回（offset_to_top，end_ea），
   如果没有表则返回None'''
      ea, offset_to_top =   read_signed_32bit(ea)
    ea, rtti_ptr =   read_ea(ea)
    if rtti_ptr   != 0:
        return None
    func_count = 0
    while True:
        next_ea, func_ptr = read_ea(ea)
        if not func_ptr in   idautils.Functions():
            break
        func_count += 1
        ea =   next_ea
    if func_count   == 0:
        return None
    return   offset_to_top, ea
def get_table_group_bounds(ea):
      '''给定一个地址，对位于该地址的虚表组返回（start_ea，end_ea）'''
    start_ea = ea
      prev_offset_to_top = None
      while True:
        table =   get_table(ea)
        if table is None:
            break
        offset_to_top, end_ea = table
        if   prev_offset_to_top is None:
            if   offset_to_top != 0:
                break
            prev_offset_to_top = offset_to_top
        elif offset_to_top   &gt;= prev_offset_to_top:
            break
        ea = end_ea
    return   start_ea, ea
def find_tablegroups(segname=".rodata"):
      '''对于在段'segname'的虚表组返回一个（start，end）ea对的列表  '''
    seg =   idaapi.get_segm_by_name(segname)
    ea =   seg.startEA
      groups = []
      while ea &lt; seg.endEA:
        bounds =   get_table_group_bounds(ea)
        if   bounds[0] == bounds[1]:
            ea += 4
            continue
        groups.append(bounds)
        ea =   bounds[1]
    return groups
```

[**view raw**](https://gist.github.com/ALSchwalm/2c8a16576d713bacdbc3f9df36c0e843/raw/28cff7914f8cd97c12d0de976c9f082dc7687c1b/reversing-part-2-3.py)[**reversing-part-2-3.py**](https://gist.github.com/ALSchwalm/2c8a16576d713bacdbc3f9df36c0e843#file-reversing-part-2-3-py)** hosted with ❤ by **[**GitHub**](https://github.com/)

在IDA的python解释器中运行上面的代码之后，可以执行find_tablegroups()获取一个虚表组地址的列表。例如，这可以与附加代码结合起来去为每张虚表创建对应结构。

然而，只知道虚表组在哪里并不是非常有用。我们需要一些与虚表关联的类型之间的关系信息。然后，我们将能够为虚函数调用点生成一个'候选的'函数调用列表，只要我们知道该类型相关联的“家族”。

**<br>**

**恢复类型关系**

恢复这些关系的最简单的方法是去识别两个虚表共享的一个相关函数指针。我们不能恢复这种关系的性质，但它足以确定他们在同一个家族。

但是我们可以进一步考虑C ++中构造函数和析构函数的行为。

**构造函数执行以下步骤：**

1、调用父类的构造函数

2、初始化vptr（s）以指向此类型的vtable（s）

3、初始化对象的成员

4、在构造函数中运行其他任何代码

**析构函数执行基本上相反的步骤：**

1、设置vptr（s）以指向此类型的vtable（s）；

2、在析构函数中运行其他任何代码；

3、销毁对象的成员；

4、调用父类的析构函数。

**注意，vptr再次设置为指向虚表。如果你不考虑虚函数调用应该在销毁期间仍然工作的话就会觉得奇怪。**

假设我们修改Bird的析构函数，让它调用fly。如果你要销毁一个Bat对象（当一个Bat对象完成时，它又调用Bird的析构函数），它应该调用Bird::fly不是Bat::fly，因为对象不再是一个Bat。为了这个工作顺利进行，Bird析构函数必须更新vptr。

因此，我们知道每个析构函数将调用父类型的析构函数，并且这些析构函数会引用虚表（将它分配给vptr）。所以，我们可以通过“跟随析构函数”来重建类型的继承层次结构。类似的逻辑也可以用于构造函数。

考虑一下第一个虚表中的第一个条目（我们期望它是一个析构函数）：

[![](https://p5.ssl.qhimg.com/t01ff23831e82eecf41.png)](https://p5.ssl.qhimg.com/t01ff23831e82eecf41.png)

注意，上面有两个赋值，它们都是虚表的地址范围。这是上面列表中的步骤1。这些对象似乎没有任何成员，因为它直接进行到步骤4，并调用其他两个析构函数。我们也可以确认这些其他函数是析构函数，因为它们在虚表中的位置（在表6和表3的开头）。对剩余的表执行此操作，这告诉我们继承层次结构的布局如下：

[![](https://p0.ssl.qhimg.com/t01813df5e1515e9ee3.png)](https://p0.ssl.qhimg.com/t01813df5e1515e9ee3.png)

这和源代码中的实际层次结构相符合。总共有两个基类，即一个类中有两个父类。

<br>

**识别构造函数**

通过类似的推理，我们可以找到与虚表相关联的构造函数，方法是找那些将它们的vptr分配给一个不是析构函数的虚表地址的函数就是构造函数。通过将此规则应用于目标，我们发现有5个这样的函数，每个类型一个：

[![](https://p1.ssl.qhimg.com/t0180a6632d9e7fdb01.png)](https://p1.ssl.qhimg.com/t0180a6632d9e7fdb01.png)

**<br>**

**反虚拟化**

有了这个，我们可以看看反编译体的main函数：

[![](https://p0.ssl.qhimg.com/t01908f28b078854f19.png)](https://p0.ssl.qhimg.com/t01908f28b078854f19.png)

虚函数在第28行和第29行清晰可见。然而，我们也可以从上面的表中识别第13,16,22和25行的构造函数。使用这些知识，我们可以按照从第1部分的过程看到反虚拟化：

[![](https://p4.ssl.qhimg.com/t01df98b783a751e490.png)](https://p4.ssl.qhimg.com/t01df98b783a751e490.png)

在上面的截图中，我已经设置了v0的类型type_8048D40*。这是与表1/2相关联的类型，也与第13行上的构造函数相关联。类似地，第16行上的构造函数与表5相关联，我已经为其创建了一个类型命名为type_8048D98（这是表开始的地址，我可以很容易地引用它们如table_5或类似的命名）。同样的事情可以应用到v2和v3以便可以看到第28和29行的修改。

所以，虽然原始代码包含的字符串将使识别类型和方法容易，但是我们不需要那些来进行我们的“反虚拟化”。

**<br>**

**结论**

这仍然是一个非常手工的过程，但我们已经更进一步了。我们现在（大概）可以自动检测虚表了。不难看出我们将如何能够自动化构造相关结构，然后可能是构造函数调用的位置。我们也可以想象重建类型树。在下一部分，我们将深入探讨这一点。



传送门：[【技术分享】逆向C++虚函数（一）](http://bobao.360.cn/learning/detail/3332.html)

> 原文链接: https://www.anquanke.com//post/id/83198 


# 注册表hive基础知识介绍第二季－NK记录


                                阅读量   
                                **83343**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[http://binaryforay.blogspot.com/2015/01/registry-hive-basics-part-2-nk-records.html](http://binaryforay.blogspot.com/2015/01/registry-hive-basics-part-2-nk-records.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01eae1f3aedec6dfff.png)](https://p5.ssl.qhimg.com/t01eae1f3aedec6dfff.png)

**        背景**

        大多数人都已经习惯用类似regedit.exe那样的程序来查看注册表的信息了。所有版本的Windows操作系统都自带有regedit.exe，用户可以通过它来查看注册表中所有基础组件的配置信息。大家可以通过下面的这张截图了解到组成一个hive文件的不同部分（通过regedit.exe即可查看）。

[![](https://p2.ssl.qhimg.com/t012619fc0ca37b74fa.png)](https://p2.ssl.qhimg.com/t012619fc0ca37b74fa.png)

        我们可以看到在窗口的左侧部分有一个由各种项和子项所组成的树，每一个项和子项下面又可以分成很多相关连的层。当一个项变成另一个项的“孩子”后，它也就变成了一个子项。在上面的这个例子中，CBT是ATI Technologies项的一个子项。在项和子项的实际结构之间并没有什么区别。

        当我们在左侧选中一个项之后，这个项所包含的所有键值都会显示在右侧区域。regedit.exe能够显示三条数据，即键值名称（名称列），键值类型（类型列）还有键值（数据列）。

        我们通过regedit.exe可以查看注册表中不同项的访问权限。你可以通过鼠标右键点击一个项，然后选中Permissions来查看具体的访问权限。

[![](https://p5.ssl.qhimg.com/t01146db717fd64ef29.png)](https://p5.ssl.qhimg.com/t01146db717fd64ef29.png)

        正如你所期待的那样，点击Permissions之后，系统会显示当前所选取的注册表项的访问权限信息。

[![](https://p3.ssl.qhimg.com/t01330845fd1be46560.png)](https://p3.ssl.qhimg.com/t01330845fd1be46560.png)

        综上所述，regedit.exe可以给用户提供三种类型的信息：项，键值，以及访问权限。

        注册表hive的主体正是由这三种类型的数据所组成的。

        当我们需要查看磁盘上的一个注册表hive时，我们还需要一些新的知识。

**        NK记录**

        当我们需要定义一个项（或子项）的时候， 一些必要的数据信息就包含在NK记录中。下图显示的是磁盘中现有的一个NK记录示例：

[![](https://p0.ssl.qhimg.com/t01a1e68348e8141746.png)](https://p0.ssl.qhimg.com/t01a1e68348e8141746.png)

        在一条NK记录中，总共有25种不同类型的数据信息。其中最主要的信息有以下几项：

        l   大小

        l   签名

        l   标识符

        l   最后写入时间

        l   父类Cell索引

        l   子项计数

        l   子项Cell索引

        l   键值计数

        l   键值Cell索引

        l   安全Cell索引

        l   名称

**        大小**

        大小起始于偏移量0x0，系统采用了一个32位的有符号整数来存储它。在上面的截图中，其十六进制数值为0x70FFFFFF。正如我们之前所看到的，这个值同样是通过小端格式存储的。将这个值转换为十进制之后，我们得到的结果为-144(是的，就是负的144)。

        这也许看起来会很奇怪，我们得到了一条大小为负数的记录。一条记录的大小怎么会是一个负数呢？当然不是这样的了。这条记录的大小为144个字节，但正负号所表示的是一条记录目前是否已经被使用了。

        如果某一条记录的大小为负数，表示的是它已经被使用了中。如果一条记录的大小为整数，那么它就还没有被使用。这也就意味着，当我们看到某条记录的大小为负数时，这条记录就已经被注册表中其他的“活动”记录所引用了。“活动”的意思就是你可以通过regedit.exe来查看这些记录。

**        签名**

        一条NK记录的签名信息起始于偏移量0x04处。这条NK记录的签名是一个ASCII字符串“nk”，其十六进制数值为0x6E6B。你可以通过查看这个[表格](http://www.ascii-code.com/)来进行验证。

        **表识符（flag）**

        flag是用来表示NK记录中不同属性的。flag的值从偏移量0x06开始，长度为两个字节。在上面所给出的例子中，表示符的值为0x2C00，也可以简单写成0x2C。表示符的一些常见的值如下：

        l   Compressed Name = 0x0020 (二进制值为100000)

        l   Hive Entry Root Key = 0x0004 (二进制值为000100)

        l   Hive Exit = 0x0002 (二进制值为000010)

        l   No Delete = 0x0008 (二进制值为001000)

        通过查看上面这个列表，我们可以看到每一个表示符对应着一个特定的十六进制数值，以及相应的二进制数值。0x2C的二进制格式为101100。如果我们对flag的值进行“按位与”计算，那么我们可以得出下列数据：

        101100 &amp; 100000 == 100000 (表示 Compressed Name flag已设置)

        101100 &amp; 001000 == 001000  (表示No Delete flag已设置)

        101100 &amp; 000100 == 000100 (表示Hive Entry Root Key flag已设置)

        101100 &amp; 000010 == 000000 (表示Hive Exit flag尚未设置)

        在得到了每一个flag的值之后，然后将这些值(100000,001000和000100)加起来就可以得到101100，即0x2C。

        你可以通过[这个网站](http://www.miniwebtool.com/bitwise-calculator/)自行进行测试。

        Compressed Name的flag表示的是这条NK记录是以ASCII码的形式进行存储的（我们将会在后面对其进行更多的讨论）。

        Hive Entry Root Key的flag非常的重要，因为它决定的是注册表hive的root节点。在一个注册表hive中只有一个节点有这个flag。

**        最后写入时间**

        我们可以在偏移量0x08处找到最后写入时间戳，其长度为8个字节。这个时间戳表示的是这条NK记录最后一次更新的时间。系统将其存储为一个64位长度的值，它代表的是从1601年1月1日0点开始，到现在一共经过的100纳秒间隔数。

        上面例子中记录的最后写入时间戳为2014年11月28日下午4时52分17秒。

        这一数据的结构类型与我们在[第一季](http://bobao.360.cn/learning/detail/2530.html)中讨论的是一样的。

**        父类Cell索引**

        父类cell索引起始与偏移量0x14处，其长度为4个字节。在上面所给出的例子中，其父类cell索引为0x20070000，即0x720。在一条NK记录之中，如果HiveEntryRootKey的flag已经设置了，那么这个值所指向的就不再是一条NK记录了，因为它已经成为了注册表hive的root。

        对于其他的NK记录而言，父类cell索引指向的是这条NK记录上一级的NK记录。父类cell索引可以允许你根据当前子项进行上下级索引。

        当你需要恢复或者重组某一条已经删除了的NK记录时，这个域就十分的重要了。因为当一条NK记录被删除之后，子项计数将会被重置为0，子项cell索引也会被覆盖。但是父类cell索引却不会，查看了父类cell索引之后，我们变能够将子项重新与他们的上一级重新组合了。

**        子项计数**

        子项计数的值从偏移量0x18处开始，其长度为4个字节。在上面的例子中子项计数的值为0x0C000000，其十进制数值为12。这也就意味着这条NK记录将有12个子项。

**        子项Cell索引**

        子项cell索引从偏移量0x20处开始，长度为4个字节。在上面的例子中，子项cell索引为0xE8326E00，其相对偏移量为0x6E32E8。此时与我们在之前的文章中所进行的操作一样，将这个值加上0x1000，然后便可以在十六进制编辑器中得到准确的值。

**        数值计数**

        数值计数从偏移量0x28处开始，其长度为4个字节。在上面的例子中，子项计数的值为0x00000000,即0。

**        键值Cell索引**

        键值cell索引从偏移量0x2C处开始，其长度为4个字节。这个数据域与VK记录有关，我们将会在第三季中对VK记录进行更加深入的讨论。在上面的例子中，键值cell索引为0xFFFFFFFF。

**        安全Cell索引**

        安全Cell索引从偏移量0x30处开始，其长度为4个字节。安全cell索引与SK记录有关，我们将会在第四季中对SK记录进行更加深入的讨论。

**        名称**

        NK记录的名称从偏移量0x50处开始。名称的长度占2个字节，从偏移量0x4C处开始。在上面的例子中，长度值为0x3900，十进制数值为57。

        将上述所有的内容组合在一起

        在下面这张图片中，我们已经将最重要的部分标注了出来：

[![](https://p3.ssl.qhimg.com/t01b46c1ec03f79c4ed.png)](https://p3.ssl.qhimg.com/t01b46c1ec03f79c4ed.png)

        通过注册表浏览器查看NK记录，即下图所示：

[![](https://p3.ssl.qhimg.com/t01129f18022d5b968f.png)](https://p3.ssl.qhimg.com/t01129f18022d5b968f.png)

        **我们将会在第三季中讨论VK记录，然后在第四季中对SK记录进行讲解，敬请期待。**

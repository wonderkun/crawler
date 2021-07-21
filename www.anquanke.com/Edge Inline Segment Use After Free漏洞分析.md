> 原文链接: https://www.anquanke.com//post/id/160299 


# Edge Inline Segment Use After Free漏洞分析


                                阅读量   
                                **132608**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t018d13014fa3eda2df.png)](https://p0.ssl.qhimg.com/t018d13014fa3eda2df.png)

Author:Qixun Zhao(aka @S0rryMybad &amp;&amp; 大宝) of Qihoo 360 Vulcan Team

在今个月的微软补丁里,修复了我报告的4个漏洞,我将会一一讲解这些漏洞.因为我写的这些文章都是用我的空余时间写的,因为每天还有大量的工作和需要休息,而且这个博客也是一个非公的私人博客,所以我不能保证更新的时间.

这篇文章讲的是CVE-2018-8367,大家可以从这里看到这个bug的[patch](https://github.com/Microsoft/ChakraCore/commit/dd5b2e75e7aebe67b5185383080c0648f5353ea0). 这是一个品相非常好的UaF,所以利用起来比较简单.同时这也是JIT中一个比较特别的漏洞,因为它需要其他模块的配合,希望能为大家以后寻找JIT漏洞的时候带来一些新思考

测试版本:chakraCore-master-2018-8-5 release build(大概是这个日期下载的就可以了)



## 关于Chakra的垃圾回收(GC)

要找到chakra中的UaF漏洞,首先需要了解chakra引擎的gc是怎么执行的.简单来说,chakra用到的gc算法是标记-清除(mark-sweep)算法,更详细的细节我推荐大家可以看看[&lt;&lt;垃圾回收的算法与实现&gt;&gt;](https://item.jd.com/12010270.html).

这个算法的核心在于有一堆需要维护的根对象(root),在chakra中根对象主要包括显式定义的脚本变量(var/let/const)还有栈上和寄存器的变量.算法从根对象开始扫描,并且递归扫描他们中的子对象(例如array对象中的segment就是array的子对象),直到遍历完所有的根对象和子对象.标记阶段完成后,如果没有标记的对象就是代表可以释放的,这时候内存管理器就会负责回收这些对象以用来以后的分配.

Chakra的gc算法主要有两个缺陷,第一是没有区分数字和对象,所以利用这个特性通过在栈上分配大量数字,然后通过侧信道攻击可以获得某个对象的地址.(这是我之前听过的一种攻击方法,不知道现在修补没有)

第二个缺陷在于,gc算法遍历子对象的时候,是需要知道父对象的大小的,不能越界遍历标记(例如父对象是array的时候,需要知道array的大小去递归标记).所以如果一个对象A中假如有一个指针指向另一个对象B的内部(非对象开始位置),A中的指针是不会执行标记操作的.假如除了对象A中的指针没有其他任何指针指向对象B,B对象是会被回收的.这样在A对象中就有一个B对象的悬挂指针(Dangling Pointers).

寻找UaF漏洞的关键就在于是否能创造一个对象中存在一个指针,指向另一个对象内部,而一般能出现这种情况的对象是String和Array.以前出现的类似漏洞有:[CVE-2017-11843](https://github.com/Microsoft/ChakraCore/commit/14f44de6188e403161a3fa3850025d391150e278)



## Array Inline Segment 与Array.prototype.splice

在创建数组的时候,如果数组的size小于一定的值,数组的segment是会连着数组的meta data,也就是保存数组数据的segment紧跟数组后面.内存布局如图所示:

```
let arr = [1.1,2.2,3.3,4.4,5.5,6.6];
Array.isArray(arr);
```

[![](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/1.png)](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/1.png)

可以看到0x11c45a07700这个segment的地址是紧跟在array(起始地址0x11c45a076c0)后面,这样的情况称为inline segment.

另一方面Array.prototype.splice这个接口是用来从一个数组删除一定数量的element,然后放到新创建的数组上,具体可以参看[MDN](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/Array/splice)

这里chakra在处理splice这个runtime接口的时候,里面存在一个优化的模式,假如要删除的element的start和end刚好等于一个segment的start和end(如上图就是index[0]到[5]),就会把这个segment的地址直接赋值到新创建的数组中(function|ArraySpliceHelper|):

[![](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/2.png)](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/2.png)

但是这里它需要避免把一个inline segment整个移动到另一个array中,否则就会出现上文提到的那种情况,一个对象中有一个指针指向另一个对象的非开头位置.

[![](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/3.png)](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/3.png)

而判断是否|hasInlineSegment|的逻辑就是:

[![](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/4.png)](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/4.png)

检查head segment的length是否少于|INLINE_CHUNK_SIZE|,这里是64.换句话说,现在如果我们要找一个UaF的漏洞,我们需要做的是创建一个head segment的length大于64的array.



## JIT PLEASE HELP ME

要想得到这样的一个array是很不容易的,因为在很多创建array的函数中,他们都会检查要创建的大小是否大于64,如果大于64,则会把head segment单独分配在另外一个buffer,不会再紧跟在array后面.

但是,一个chakra引擎是由很多很多人编写的,在我看来,编写JIT模块的人应该与runtime模块的人是不一样的,同样编写JIT的人会比较不熟悉runtime模块上的一些逻辑与细节.而在现实中,很多漏洞往往就是因为不同人员之间协同开发,导致一些跨模块的漏洞出现,这个漏洞就是典型的JIT开发人员不熟悉runtime模块导致.

在今年一月份修复CVE-2018-0776,开发人员引入了这个漏洞: [patch](https://github.com/Microsoft/ChakraCore/commit/40e45fc38189cc021267c65d42ca2fb5f899f9de)和[GPZ Report](https://bugs.chromium.org/p/project-zero/issues/detail?id=1420&amp;can=1&amp;q=owner%3Alokihardt%40google.com&amp;colspec=ID%20Status%20Restrict%20Reported%20Vendor%20Product%20Finder%20Summary&amp;desc=2)

由于JIT的开发人员不熟悉runtime的逻辑,不清楚在创建数组的时候headsegment的length不能大于64,导致打破了chakra中的一些惯例.我们可以看到|BoxStackInstance|中创建数组的时候,根本没有判断需要创建的head大小就直接创建了一个inline segment array.(这里我们需要deepcopy为true才可以)

所以到底什么是BoxStackInstance,在什么情况下才能调用这个创建数组?

在JIT中,有一个优化机制叫做escape analysis,用于分析一个变量是否逃出了指定的范围,假如一个变量的访问用于只在一个function里面,我们完全可以把这个变量当成局部变量,分配在栈上,在函数返回的时候自动释放.这样的优化可以减少内存的分配和gc需要管理的对象,因为这里对象的生命周期是和函数同步的,并不是由gc管理.

但是这里有一个问题,但是某些特殊情况下,我们需要把这个栈上的变量重新分配到堆上,这时候就需要调用BoxStackInstance重新创建对象.

情况一就是bailout发生的时候,因为需要OSR回到解释器层面执行,这时候就没有所谓的native函数栈概念,只剩下虚拟机的虚拟栈,否则对象会引用已释放的栈空间.这种情况deepcopy为false,并不满足我们的需要.

情况二就是通过arguments访问一个栈变量,因为arguments可能是一个堆对象,它是由gc管理的,它里面必定不能包含栈分配的对象.这时候deepcopy为true.<br>
至此,漏洞的大概原理已经分析清楚.



## I WANT TYPE CONFUSION

通过上面的分析,我相信大家结合GPZ的case差不多已经知道如何构造poc了:

[![](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/5.png)](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/5.png)

获得了这样一个evil array后,先转换成对象数组,然后我们用它来调用splice,把它的inline segment 赋值到另一个对象中:

[![](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/6.png)](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/6.png)

然后把其他所有引用这个inline segment的array的对象全部清除掉,这时候这个带有inline segment的array将会被回收,由于|evil|指向这个inlinesegment的pointer是指向这个array的内部,所以并不会影响这个array被回收

[![](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/7.png)](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/7.png)

然后通过gc函数,对喷大量的float array,同时触发垃圾回收,这时候evil对象数组的segment区域将会被大量float array占据:

[![](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/8.png)](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/8.png)

至此,我们已经成功将这个UaF的漏洞转成var array和float array的type confusion漏洞,至于剩下怎么fake与leak,大家可以参考我们上一篇的blog,这里就不再重复了.

[![](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/9.png)](https://blogs.projectmoon.pw/2018/09/15/Edge-Inline-Segment-Use-After-Free/9.png)



## 总结

这里的修复也很简单,就是利用BoxStackInstance重新创建数组的时候判断array是否inline segment array,如果不是,则把head segment分配到另外的地方,以免影响splice里面|hasInlineSegment|的判断.

从这个案例我们可以知道,在一个庞大的项目开发的时候,往往由很多不同的人员开发,而他们往往对自己平时不接触的模块比较陌生,这样在打一些补丁或者修改代码的时候很可能会引入一些跨模块的漏洞.

除此以外,我们也可以想到,在查看JIT漏洞的时候,我们不能仅仅只盯着在JIT编译出来的代码或者把JIT独立出来思考,可能一些JIT的问题需要配合runtime或者其他模块才能形成一个完成的安全漏洞.这也为以后寻找JIT漏洞的时候带来一些新思路—-结合其他的模块思考.

Thank you for your time.

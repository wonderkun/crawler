> 原文链接: https://www.anquanke.com//post/id/84485 


# PHP7：反序列化漏洞案例及分析（下）


                                阅读量   
                                **102647**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[http://blog.checkpoint.com/2016/08/26/web-scripting-language-php-7-vulnerable-to-remote-exploits/](http://blog.checkpoint.com/2016/08/26/web-scripting-language-php-7-vulnerable-to-remote-exploits/)

译文仅供参考，具体内容表达以及含义原文为准

**<strong style="text-indent: 28px">[![](https://p2.ssl.qhimg.com/t01d371ade6421a361b.jpg)](https://p2.ssl.qhimg.com/t01d371ade6421a361b.jpg)**</strong>

PHP7：反序列化漏洞案例及分析（上）：[http://bobao.360.cn/learning/detail/2991.html](http://bobao.360.cn/learning/detail/2991.html)



**<strong style="text-indent: 28px">6.泄漏指针**</strong>

 在典型的PHP-5反序列化利用中，我们会使用分配器来覆盖一个指向字符串内容的指针，从而阅读下一个堆slot的内容。然而在PHP-7中,内部字符串的表示是截然不同的。

在PHP-7中, 基本结构struct zval在内部指向结构zend_string，从而引用字符串。zend_string转而使用member数组，将字符串嵌入到结构的末尾。因此,直接指向字符串内容的指针不可以被覆盖。

然而, PHP-5的技术可能会让指针发生泄漏。如果一个结构的第一个字段指向了一些我们可以阅读的内容，我们可以对该结构进行分配和释放,随后分配器会让它指向先前已经释放的slot，这会允许我们读取一些内存。

幸运的是, 在内部表示为php_interval_obj结构的DateInterval对象非常有用。这是定义:

[![](https://p5.ssl.qhimg.com/t01f9e21cba80c9cde5.jpg)](https://p5.ssl.qhimg.com/t01f9e21cba80c9cde5.jpg)

timelib_rel_time就是一种简单的结构，没有指针或其他复杂的数据类型,只有integer类型。这是定义:



[![](https://p0.ssl.qhimg.com/t01f68a3538e2b02554.png)](https://p0.ssl.qhimg.com/t01f68a3538e2b02554.png)

让有效载荷发生内存泄漏:

[![](https://p1.ssl.qhimg.com/t01dea4bf4335a30984.png)](https://p1.ssl.qhimg.com/t01dea4bf4335a30984.png)

结果是:

[![](https://p0.ssl.qhimg.com/t0105f987888e472d79.png)](https://p0.ssl.qhimg.com/t0105f987888e472d79.png)

如果我们做一些格式化的工作,就能看到我们已经读取到了一些内存。在取得了struct timelib_rel_time字段的偏移量后,我们读到了以下的值:

[![](https://p4.ssl.qhimg.com/t015f568c50db112b11.png)](https://p4.ssl.qhimg.com/t015f568c50db112b11.png)

所以,我们可以推断出内存是这样的(注意,在序列化过程中，timelib_slll字段被int取整了):

[![](https://p5.ssl.qhimg.com/t0179aa9daaaa2ab2fa.png)](https://p5.ssl.qhimg.com/t0179aa9daaaa2ab2fa.png)

**7.泄漏指针( 64位)**

在64位版本中,我们泄漏初始信息的方法和在32位版本中是一样的。但在64位中，这种方法更有用,因为我们将整个内存都转换成了int型，并且没有截断。

因此,我们需要创建两个DateInterval对象，然后用第一个对象读取第二个对象的内存(而不是读取无用的字符串)。

**<br>**

**8.读取内存( 64位)**

在前面的内容中,我们泄露了堆和代码的地址。我们现在需要做的是读取内存地址，从而获取足够的数据来构建一

现在，读取任意内存变得有点棘手了,因为我们既不能伪造一个数组，也没法控制它的字段(我们不能控制arData)。幸运的是,我们可以使用另一个对象:DatePeriod。

DatePeriod在内部表示为php_period_obj结构。下面是定义:

[![](https://p3.ssl.qhimg.com/t01b4f30938603327ef.jpg)](https://p3.ssl.qhimg.com/t01b4f30938603327ef.jpg)

注意第一个字段,这是一个指向timelib_time结构的指针。当这个对象被释放时, 结构的第一个字段会被分配器覆盖，从而变成相同大小的指向已释放的结构的指针。因此,在分配之后,引擎会读取timelib_time。下面是timelib_time的定义:

[![](https://p4.ssl.qhimg.com/t016a2cc1f56f374a37.png)](https://p4.ssl.qhimg.com/t016a2cc1f56f374a37.png)

我们看到，tz_abbr字段一个是指向char（一个字符串）的指针。在对DatePeriod对象进行序列化时,如果zone_type 是TIMELIB_ZONETYPE_ABBR(2),那么tz_abbr指向的字符串会被strdup复制，然后进行序列化。这对读取primitive施加了一些限制,我们每次只能读取一个NULL字节。

现在，我们需要找到哪一个对象是在DatePeriod之前被释放的。

假如我们想读取0 x7f711384a000,就需要发送这个:

[![](https://p4.ssl.qhimg.com/t013a2dbc806574d939.png)](https://p4.ssl.qhimg.com/t013a2dbc806574d939.png)

我们可以看到,timelib_rel_time 内days字段的偏移量和timelib_time内的tz_abbr是一样的。

DatePeriod填充是最后一步，同时这也是最复杂的。当DatePeriod对象被序列化时,date_object_get_properties_period函数会被调用，并返回properties HashTable进行序列化。这个HashTable 就是zend_object properties字段(嵌入在php_period_obj结构内),它会在DatePeriod对象创建时被分配。在将这个HashTable返回给调用者之前,函数会用php_period_obj内每个字段的值来更新这个哈希表。这听上去很简单,但试想一下, 在释放DatePeriod对象时，这个HashTable已经被释放了，这意味着它的第一个字节是指向free list的指针。为了了解这个损坏造成的影响,我们需要明白PHP是如何应用哈希表的。

当一个新的哈希表分配进来,一个zend_array类型的结构会被初始化。这个数组使用arData字段指向实际的数据,其他字段则作用于table capacity和负载。

数据分为两部分:

1．哈希散列数组，它将哈希（被nTableMask掩盖）映射到各个索引号。

2．数据数组, 它是Buckets内的数组，包含哈希表内实际数据的key和值。

在对zend_array进行初始化时,将要存储的元素数量会被四舍五入为最接近的2的幂数，然后一个新的内存slot数据会被分配给这些数据。分配数据的大小为size * sizeof(uint32_t) + size * sizeof(Bucket)。然后,arData字段会被设置为指向Bucket数组的开头。当一个值被插入到表中时，zend_hash_find_bucket函数会被调用来找到正确的bucket。这个函数会对key进行散列,然后生成的散列会被nTableMask表掩盖。结果是一个负数,这代表着散列数组内拥有bucket索引号的元素的数量（即在arData之前，拥有bucket索引号的uint32_t元素的数量）。

现在,当散列表被释放时, slot分配给arData的前8个字节会被覆盖,这会破坏散列数组内的前两个索引号。不幸的是,其中的一个索引号是我们需要的!在被nTableMask 掩盖的时候，“current” key的散列值为-8,表明这是一个损坏的元素(第一个单元)。

为了解决这个问题,我们需要让表增大,从而避免任何key使用前两个单元。令人惊讶的是,反序列化源为我们提供了一个非常简洁的方法:它能扩展properties哈希表的大小，而这大小为提供给对象的元素的数量。所以,如果我们把更多无用的元素放到DatePeriod字符串的key-value哈希表内, properties哈希表就能得到扩展。初始化给定哈希表内DatePeriod的函数只会关注预定义的key (如“start”, “current”等) ，它不会检查哈希表的大小，所以这些没用的值不会产生任何影响。因此,我们可以对哈希表的散列数组的大小进行扩充,并确保所有的key都不会落在第一个单元格。

13.读取内存和代码执行(64位)

在分配UAF对象之前,我们需要修复损坏的堆。为了解决这个问题，我们可以增加内部数组的值,直到它指向free list中的下一个空闲对象。这个对象已经经过了bin的两次分配。在第二次分配后, 通过返回的slot，free list能够保存指针指向的值。因此,如果我们可以在错误被触发之前控制free list中的内容,就能控制free list的指针。控制了这个指针后，我们就能把对象分配到这个地址。

我们应当如何控制free list内slot的内容?我们曾经提到过，在反序列化过程中值不能被释放,这是事实,但不是全部的事实。我们不能释放值,是因为它们被放进了destructor数组，然而key没有被放进这个数组。所以,这里有一种在反序列化过程中释放一个字符串的方法:如果一个字符串被作为key使用了两次,第二次使用就是返回到堆。通常情况下,如果一个key只被使用了一次,这个key的引用计数会增加两次（被创建并插入到哈希表），减少一次（在循环解析嵌套数据的最后）。然而,如果这个key已经存在于哈希表中,只会各增加和减少一次,然后被释放。

这意味着，我们可以控制返回给free list的最后一个slot的内容。然而,这个slot会被即将释放的对象使用（即覆盖）。因此,我们需要找到一种方法来控制两个返回到堆的slot，这可以通过嵌套完成。如果我们使用同一个key两次,且第二次的值是一个两次使用相同key的stdClass，那么这些key会一个接一个地进行去分配。这样,我们就可以把尽可能多的字符串放到free list内了。

这很容易，我们只需要增加22个损坏的指针(22 + 2 = 24——zend_string内val字段的偏移量),这恰好是释放了的字符串的值。这个字符串的值指向php_interval_obj之前的一个已分配的字符串。这个字符串的末尾被设置为0,目的是让分配器以为free list已经耗尽(如果不是NULL,那它必须得是一个指向free list的有效指针,这太难找了)。这样做之后, 大小为56的第三次分配 (sizeof(zend_array)) 会覆盖php_interval_obj之前的字符串末尾,还有php_interval_obj对象的开头。这让我们得以覆盖php_interval_obj 内zend_object部分的ce字段。ce字段是一个指向zend_class_entry的指针,而zend_class_entry拥有指向各种功能的指针。因此,覆盖这个值意味着控制了RIP。

这是我们的利用(分配0 x0000414141414141到ce):

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015d178126904f82c0.png)

在我们将调试器附加到apache，并发送上面的字符串时,我们得到了一个段错误:



```
Program received signal SIGSEGV, Segmentation fault. php_var_serialize_intern (buf=0x7ffcd3cc10e0, struc=0x7f710e667b60, var_ hash=0x7f710e6772c0) at /build/php7.0-7.0.2/ext/standard/var.c:840
840 if (ce-&gt;serialize != NULL) `{`
(gdb) print ce
$1 = (zend_class_entry *) 0x414141414141
```

我们可以看到,ce包含着我们预期的值。

这个堆的写入能力为其他的primitive提供了机会，例如任意读取primitive或其他的执行primitive。注意,这不仅仅局限于64位的情况——它在每一个架构中都适用。

现在，我们现在控制了free list中的内容。在引发这个错误之前,我们不需要再假设在UAF指针之后，下一个空闲slot刚好是56字节(在32位中是48)。

我们已经有了一个泄漏primitive,读取primitive和代码执行primitive，这样，我们的工作就算就完成了。下面的内容就交给读者了。

**<br>**

**9.结语**

反序列化实际上是一个危险的功能。这一点在过去的几年已被反复证实,但仍然有人在使用它。

相比之下，序列化格式要复杂得多,而且在被传递进行解析之前很难验证。复杂的格式需要用复杂的机器来解析，为了保证安全,我们需要避免使用这种复杂的格式。



PHP7：反序列化漏洞案例及分析（上）：[http://bobao.360.cn/learning/detail/2991.html](http://bobao.360.cn/learning/detail/2991.html)

报告原文：[http://blog.checkpoint.com/wp-content/uploads/2016/08/Exploiting-PHP-7-unserialize-Report-160829.pd](http://blog.checkpoint.com/wp-content/uploads/2016/08/Exploiting-PHP-7-unserialize-Report-160829.pdf)f

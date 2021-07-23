> 原文链接: https://www.anquanke.com//post/id/149421 


# 如何攻破PHP的垃圾回收和反序列化机制（上）


                                阅读量   
                                **124715**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：evonide.com
                                <br>原文地址：[https://www.evonide.com/breaking-phps-garbage-collection-and-unserialize/](https://www.evonide.com/breaking-phps-garbage-collection-and-unserialize/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01d701fa5f4e4ad5d5.jpg)](https://p2.ssl.qhimg.com/t01d701fa5f4e4ad5d5.jpg)

## 前言

在本文中，我们主要介绍了PHP垃圾回收（Garbage Collection）算法中的两个Use-After-Free漏洞。其中一个漏洞影响PHP 5.3以上版本，在5.6.23版本中修复。另外一个漏洞影响PHP 5.3以上版本和PHP 7所有版本，分别在5.6.23和7.0.8版本中修复。这些漏洞也可以通过PHP的反序列化函数远程利用。特别要提及的是，我们通过这些漏洞实现了pornhub.com网站的远程代码执行，从而获得了总计20000美元的漏洞奖励，同时每人获得了来自Hackerone互联网漏洞奖励的1000美元奖金。在这里，感谢Dario Weißer编写反序列化模糊测试程序，并帮助我们确定了反序列化中的原始漏洞。



## 概述

我们在审计Pornhub的过程中，发现了PHP垃圾回收算法中的两个严重缺陷，当PHP的垃圾回收算法与其他特定的PHP对象进行交互时，发现了两个重要的Use-After-Free漏洞。这些漏洞的影响较为广泛，可以利用反序列化漏洞来实现目标主机上的远程代码执行，本文将对此进行讨论。<br>
在对反序列化进行模糊测试并发现问题之后，我们可以总结出两个UAF漏洞的PoC。如果关注如何发现这些潜在问题，大家可以参阅Dario关于反序列化模糊测试过程的文章（ [https://www.evonide.com/fuzzing-unserialize](https://www.evonide.com/fuzzing-unserialize) ）。我们在此仅举一例：

```
// POC of the ArrayObject GC vulnerability
$serialized_string = 'a:1:`{`i:1;C:11:"ArrayObject":37:`{`x:i:0;a:2:`{`i:1;R:4;i:2;r:1;`}`;m:a:0:`{``}``}``}`';
$outer_array = unserialize($serialized_string);
gc_collect_cycles();
$filler1 = "aaaa";
$filler2 = "bbbb";
var_dump($outer_array);
// Result:
// string(4) "bbbb"
```

针对这个示例，我们通常期望如下输出：

```
array(1) `{` // outer_array
  [1]=&gt;
  object(ArrayObject)#1 (1) `{`
    ["storage":"ArrayObject":private]=&gt;
    array(2) `{` // inner_array
      [1]=&gt;
      // Reference to inner_array
      [2]=&gt;
      // Reference to outer_array
    `}`
  `}`
`}`
```

但实际上，一旦该示例执行，外部数组（由$outer_array引用）将会被释放，并且zval将会被$filler2的zval覆盖，导致没有输出“bbbb”。<br>
根据这一示例，我们产生了以下问题：<br>
为什么外部数组完全被释放？<br>
函数gc_collect_cycles()在做什么，是否真的有必要存在这个手动调用？由于许多脚本和设置根本不会调用这个函数，所以它对于远程利用来说是非常不方便的。<br>
即使我们能够在反序列化过程中调用它，但在上面这个例子的场景中，还能正常工作吗？<br>
这一切问题的根源，似乎都在于PHP垃圾回收机制的gc_collect_cycles之中。我们首先要对这一函数有更好的理解，然后才能解答上述的所有问题。



## PHP的垃圾回收机制

在早期版本的PHP中，存在循环引用内存泄露的问题，因此，在PHP 5.3.0版本中引入了垃圾回收（GC）算法（官方文档： [http://php.net/manual/de/features.gc.collecting-cycles.php](http://php.net/manual/de/features.gc.collecting-cycles.php) ）。垃圾回收机制默认是启用的，可以通过在php.ini配置文件中设置zend.enable_gc来触发。<br>
在这里，我们已经假设各位读者具备了一些PHP的相关知识，包括内存管理、“zval”和“引用计数”等，如果有读者对这些名词不熟悉，可以首先阅读官方文档： [http://www.phpinternalsbook.com/zvals/basic_structure.html](http://www.phpinternalsbook.com/zvals/basic_structure.html) ； [http://www.phpinternalsbook.com/zvals/memory_management.html](http://www.phpinternalsbook.com/zvals/memory_management.html) 。

### <a class="reference-link" name="2.1%20%E5%BE%AA%E7%8E%AF%E5%BC%95%E7%94%A8"></a>2.1 循环引用

要理解什么是循环引用，请参见一下示例：

```
//Simple circular reference example
$test = array();
$test[0] = &amp;$test;
unset($test);
```

由于$test引用其自身，所以它的引用计数为2，即使我们没有设置$test，它的引用计数也会变为1，从而导致内存不再被释放，造成内存泄露的问题。为了解决这一问题，PHP开发团队参考IBM发表的“Concurrent Cycle Collection in Reference Counted Systems”一文（ [http://researcher.watson.ibm.com/researcher/files/us-bacon/Bacon01Concurrent.pdf](http://researcher.watson.ibm.com/researcher/files/us-bacon/Bacon01Concurrent.pdf) ），实现了一种垃圾回收算法。

### <a class="reference-link" name="2.2%20%E8%A7%A6%E5%8F%91%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6"></a>2.2 触发垃圾回收

该算法的实现可以在“Zend/zend_gc.c”（ [https://github.com/php/php-src/blob/PHP-5.6.0/Zend/zend_gc.c](https://github.com/php/php-src/blob/PHP-5.6.0/Zend/zend_gc.c) ）中找到。每当zval被销毁时（例如：在该zval上调用unset时），垃圾回收算法会检查其是否为数组或对象。除了数组和对象外，所有其他原始数据类型都不能包含循环引用。这一检查过程通过调用gc_zval_possible_root函数来实现。任何这种潜在的zval都被称为根（Root），并会被添加到一个名为gc_root_buffer的列表中。<br>
然后，将会重复上述步骤，直至满足下述条件之一：<br>
1、gc_collect_cycles()被手动调用（ [http://php.net/manual/de/function.gc-collect-cycles.php](http://php.net/manual/de/function.gc-collect-cycles.php) ）；<br>
2、垃圾存储空间将满。这也就意味着，在根缓冲区的位置已经存储了10000个zval，并且即将添加新的根。这里的10000是由“Zend/zend_gc.c”（ [https://github.com/php/php-src/blob/PHP-5.6.0/Zend/zend_gc.c](https://github.com/php/php-src/blob/PHP-5.6.0/Zend/zend_gc.c) ）头部中GC_ROOT_BUFFER_MAX_ENTRIES所定义的默认限制。当出现第10001个zval时，将会再次调用gc_zval_possible_root，这时将会再次执行对gc_collect_cycles的调用以处理并刷新当前缓冲区，从而可以再次存储新的元素。

### <a class="reference-link" name="2.3%20%E5%BE%AA%E7%8E%AF%E6%94%B6%E9%9B%86%E7%9A%84%E5%9B%BE%E5%BD%A2%E6%A0%87%E8%AE%B0%E7%AE%97%E6%B3%95"></a>2.3 循环收集的图形标记算法

垃圾回收算法实质上是一种图形标记算法（Graph Marking Algorithm），其具体结构如下。图形节点表示实际的zval，例如数组、字符串或对象。而边缘表示这些zval之间的连接或引用。<br>
此外，该算法主要使用以下颜色标记节点。<br>
1、紫色：潜在的垃圾循环根。该节点可以是循环引用循环的根。最初添加到垃圾缓冲区的所有节点都会标记为紫色。<br>
2、灰色：垃圾循环的潜在成员。该节点可以是循环参考循环中的一部分。<br>
3、白色：垃圾循环的成员。一旦该算法终止，这些节点应该被释放。<br>
4、黑色：使用中或者已被释放。这些节点在任何情况下都不应该被释放。<br>
为了能更清晰地了解这个算法的详情，我们接下来具体看看其实现方法。整个垃圾回收过程都是在gc_collect_cycles中执行：

```
"Zend/zend_gc.c"
[...]
ZEND_API int gc_collect_cycles(TSRMLS_D)
`{`
[...]
        gc_mark_roots(TSRMLS_C);
        gc_scan_roots(TSRMLS_C);
        gc_collect_roots(TSRMLS_C);
[...]
        /* Free zvals */
        p = GC_G(free_list);
        while (p != FREE_LIST_END) `{`
            q = p-&gt;u.next;
            FREE_ZVAL_EX(&amp;p-&gt;z);
            p = q;
        `}`
[...]
`}`
```

这个函数可以分为如下四个简化后的步骤：<br>
1、gc_mark_roots（TSRMLS_C）：<br>
将zval_mark_grey应用于gc_root_buffer中所有紫色标记的元素。其中，zval_mark_grey针对给定的zval按照以下步骤进行：<br>
(1) 如果给定的zval已经标记为灰色，则返回；<br>
(2) 将给定的zval标记为灰色；<br>
(3) 当给定的zval是数组或对象时，检索所有子zval；<br>
(4) 将所有子zval的引用计数减1，然后调用zval_mark_grey。<br>
总体来说，这一步骤将根zval可达的其他zval都标记为灰色，并且将这些zval的引用计数器减1。<br>
2、gc_scan_roots（TSRMLS_C）：<br>
将zcal_scan应用于gc_root_buffer中的所有元素。zval_scan针对给定的zval执行以下操作：<br>
(1) 如果给定的zval已经标记为非灰色的其他颜色，则返回；<br>
(2) 如果其引用计数大于0，则调用zval_scan_black，其中zval_scan_black会恢复此前zval_mark_grey对引用计数器执行的所有操作，并将所有可达的zval标记为黑色；<br>
(3) 否则，将给定的zval标记为白色，当给定的zval是数组或对象时检索其所有子zval，并调用zval_scan。<br>
总体来说，通过这一步，将会确定出来哪些已经被标记为灰色的zval现在应该被标记为黑色或白色。<br>
3、gc_collect_roots（TSRMLS_C）:<br>
在这一步骤中，针对所有标记为白色的zval，恢复其引用计数器，并将它们添加到gc_zval_to_free列表中，该列表相当于gc_free_list。<br>
4、最后，释放gc_free_list中包含的所有元素，也就是释放所有标记为白色的元素。<br>
通过上述算法，会对循环引用的所有部分进行标记和释放，具体方法就是先将其标记为白色，然后进行收集，最终释放它们。通过对上述算法进行仔细分析，我们发现其中有可能出现冲突，具体如下：<br>
1、在步骤1.4中，zval_mark_grey在实际检查zval是否已经标记为灰色之前，就对其所有子zval的引用计数器进行了递减操作；<br>
2、由于zval引用计数器的暂时递减，可能会导致一些影响（例如：对已经递减的引用计数器再次进行检查，或对其进行其他操作），从而造成严重后果。



## PoC分析

根据我们现在已经掌握的垃圾回收相关知识，重新回到漏洞示例。我们首先回想如下的序列化字符串：

```
//POC of the ArrayObject GC vulnerability
$serialized_string = 'a:1:`{`i:1;C:11:"ArrayObject":37:`{`x:i:0;a:2:`{`i:1;R:4;i:2;r:1;`}`;m:a:0:`{``}``}``}`';
```

在使用gdb时，我们可以使用标准的PHP 5.6 .gdbinit（ [https://github.com/php/php-src/blob/PHP-5.6.23/.gdbinit](https://github.com/php/php-src/blob/PHP-5.6.23/.gdbinit) ）和一个额外的自定义例程来转储垃圾回收缓冲区的内容。

```
//.gdbinit dumpgc
define dumpgc
    set $current = gc_globals.roots.next
    printf "GC buffer content:n"
    while $current != &amp;gc_globals.roots
        printzv $current.u.pz
        set $current = $current.next
    end
end
```

此外，我们现在可以在gc_mark_roots和gc_scan_roots上设置断点来查看所有相关引用计数器的状态。<br>
此次分析的目标，是为了解答为什么外部数组会完全被释放。我们将PHP进程加载到gdb中，并按照上文所述设置断点，执行示例脚本。

```
(gdb) r poc1.php
[...]
Breakpoint 1, gc_mark_roots () at [...]
(gdb) dumpgc
GC roots buffer content:
[0x109f4b0] (refcount=2) array(1): `{` // outer_array
    1 =&gt; [0x109d5c0] (refcount=1) object(ArrayObject) #1
  `}`
[0x109ea20] (refcount=2,is_ref) array(2): `{` // inner_array
    1 =&gt; [0x109ea20] (refcount=2,is_ref) array(2): // reference to inner_array
    2 =&gt; [0x109f4b0] (refcount=2) array(1): // reference to outer_array
  `}`
```

在这里，我们看到，一旦反序列化完成，两个数组（inner_array和outer_array）都会被添加到垃圾回收缓冲区中。如果我们在gc_scan_roots处中断，那么将会得到如下的引用计数器：

```
(gdb) c
[...]
Breakpoint 2, gc_scan_roots () at [...]
(gdb) dumpgc
GC roots buffer content:
[0x109f4b0] (refcount=0) array(1): `{` // outer_array
    1 =&gt; [0x109d5c0] (refcount=0) object(ArrayObject) #1
  `}`
```

在这里，我们确实看到了gc_mark_roots将所有引用计数器减为0，所以这些节点接下来会变为白色，随后被释放。但是，我们有一个问题，为什么引用计数器会首先变为0呢？

### <a class="reference-link" name="3.1%20%E5%AF%B9%E6%84%8F%E5%A4%96%E8%A1%8C%E4%B8%BA%E7%9A%84%E8%B0%83%E8%AF%95"></a>3.1 对意外行为的调试

接下来，让我们逐步通过gc_mark_roots和zval_mark_grey探究其原因。<br>
1、zval_mark_grey将会在outer_array上调用（此时，outer_array已经添加到垃圾回收缓冲区中）；<br>
2、将outer_array标记为灰色，并检索所有子项，在这里，outer_array只有一个子项，即“object(ArrayObject) #1”（引用计数器 = 1）；<br>
3、将子项或ArrayObject的引用计数分别进行递减，结果为“object(ArrayObject) #1”（引用计数器 = 0）；<br>
4、zval_mark_grey将会在此ArrayObject上被调用；<br>
5、这一对象会被标记为灰色，其所有子项（对inner_array的引用和对outer_array的引用）都将被检索；<br>
6、两个子项的引用计数器，即两个引用的zval将被递减，目前“outer_array”（引用计数器 = 1），“inner_array”（引用计数器 = 1）；<br>
7、由于outer_array已经标记为灰色（步骤2），所以现在要在outer_array上调用zval_mark_grey；<br>
8、在inner_array上调用zval_mark_grey，它将被标记为灰色，并且其所有子项都将被检索，同步骤5一样；<br>
9、两个子项的引用计数器再次被递减，导致“outer_array”（引用计数器 = 0），“inner_array”（引用计数器 = 0）；<br>
10、最后，由于不再需要访问zval，所以zval_mark_grey将终止。<br>
在此过程中，我们没有想到的是，inner_array和ArrayObject中包含的引用分别递减了两次，而实际上它们每个引用应该只递减一次。另外，其中的步骤8不应被执行，因为这些元素在步骤6中已经被标记算法访问过。<br>
经过探究我们发现，标记算法假设每个元素只能有一个父元素，而在上述过程中显然不满足这一预设条件。那么，为什么在我们的示例中，一个元素可以作为两个不同父元素的子元素被返回呢？

### <a class="reference-link" name="3.2%20%E9%80%A0%E6%88%90%E5%AD%90%E9%A1%B9%E6%9C%89%E4%B8%A4%E4%B8%AA%E7%88%B6%E8%8A%82%E7%82%B9%E7%9A%84%E5%8E%9F%E5%9B%A0"></a>3.2 造成子项有两个父节点的原因

要找到答案，我们必须先看看是如何从父对象中检索到子zval的：

```
"Zend/zend_gc.c"
[...]
static void zval_mark_grey(zval *pz TSRMLS_DC)
`{`
[...]
        if (Z_TYPE_P(pz) == IS_OBJECT &amp;&amp; EG(objects_store).object_buckets) `{`
            if (EXPECTED(EG(objects_store).object_buckets[Z_OBJ_HANDLE_P(pz)].valid &amp;&amp;
                     (get_gc = Z_OBJ_HANDLER_P(pz, get_gc)) != NULL)) `{`
[...]
                    HashTable *props = get_gc(pz, &amp;table, &amp;n TSRMLS_CC);
[...]
`}`
```

可以看出，如果传递的zval是一个对象，那么该函数就会调用特定于对象的get_gc处理程序。这个处理程序应该返回一个哈希表，其中包含所有的子zval。经过进一步调试后，我们发现该过程将会调用spl_array_get_properties：

```
"ext/spl/spl_array.c"
[...]
static HashTable *spl_array_get_properties(zval *object TSRMLS_DC) /* `{``{``{` */
`{`
[...]
    result = spl_array_get_hash_table(intern, 1 TSRMLS_CC);
[...]
    return result;
`}`
```

总之，将会返回内部ArrayObject数组的哈希表。然而，问题发生的根源是这个哈希表在两个不同的上下文环境中使用，分别是：<br>
1、当算法试图访问ArrayObject zval的子元素时；<br>
2、当算法试图访问inner_array的子项时。<br>
大家可能现在能猜到，在步骤1中缺少了一些东西。由于返回inner_array哈希表的行为与访问inner_array的行为非常相似，因此前者在步骤1中也应该标记为灰色，从而保证在步骤2中不能再次对其进行访问。<br>
那么，接下来我们会问，为什么inner_array在步骤1中没有被标记为灰色？我们可以再次仔细阅读一下zval_mark_grey是如何检索子项的：

```
HashTable *props = get_gc(pz, &amp;table, &amp;n TSRMLS_CC);
```

该方法推测是负责调用对象的垃圾回收函数，其垃圾回收函数类似于如下例子：

```
"ext/spl/php_date.c"
[...]
static HashTable *date_object_get_gc(zval *object, zval ***table, int *n TSRMLS_DC)
`{`
   *table = NULL;
   *n = 0;
   return zend_std_get_properties(object TSRMLS_CC);
`}`
```

然而，返回的哈希表应该只包含对象自身的属性。实际上，还有zval的参数，会通过引用进行传递，并作为第二个“返回参数”。该zval应该包含该对象在其他上下文中所引用的所有zval。这一点，可以以存储在SplObjectStorage中的所有对象/zval为例。<br>
对于我们特定的ArrayObject场景，我们希望zval表能够包含对inner_array的引用。然而，这一过程为什么要调用spl_array_get_properties而不是spl_array_get_gc呢？

### <a class="reference-link" name="3.3%20%E7%BC%BA%E5%B0%91%E7%9A%84%E5%9E%83%E5%9C%BE%E5%9B%9E%E6%94%B6%E5%87%BD%E6%95%B0%E5%8F%8A%E5%85%B6%E5%AF%BC%E8%87%B4%E7%9A%84%E5%90%8E%E6%9E%9C"></a>3.3 缺少的垃圾回收函数及其导致的后果

问题的答案很简单，spl_array_get_gc根本就不存在！<br>
PHP的开发人员并没有为ArrayObjects实现相应的垃圾回收函数。尽管如此，其实还是不能解释为什么spl_array_get_properties被调用。为了进一步追溯其原因，我们首先看看对象是如何初始化的：

```
"Zend/zend_object_handlers.c"
[...]
ZEND_API HashTable *zend_std_get_gc(zval *object, zval ***table, int *n TSRMLS_DC) /* `{``{``{` */
`{`
    if (Z_OBJ_HANDLER_P(object, get_properties) != zend_std_get_properties) `{`
        *table = NULL;
        *n = 0;
        return Z_OBJ_HANDLER_P(object, get_properties)(object TSRMLS_CC);
[...]
`}`
```

处理遗漏的垃圾回收函数，依靠于对象自身的get_properties方法（前提是该方法已定义）。<br>
现在，我们终于找到了第一个问题的答案。造成该漏洞的主要原因，是ArrayObject缺少垃圾回收函数。<br>
奇怪的是，这个函数是在PHP 7.1.0 alpha2版本中又被引入（ [https://github.com/php/php-src/commit/4e03ba4a6ef4c16b53e49e32eb4992a797ae08a8](https://github.com/php/php-src/commit/4e03ba4a6ef4c16b53e49e32eb4992a797ae08a8) ）。因此，只有PHP 5.3及以上版本和7以下的版本缺少此函数，受到漏洞影响。然而，由于在不经过对反序列化进行调整的前提下，我们无法触发这一漏洞，因此还不能仅凭借此漏洞来实现远程代码执行。截至目前，我们将该漏洞称为“双递减漏洞”，漏洞报告如下（CVE-2016-5771）： [https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-5771](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2016-5771) 。



## 小结

现在，我们仍然需要回答开头提出的问题。其中之一是，是否有必要手动调用gc_collect_cycles？<br>
此外，在发现了这一漏洞后，是否可以有效将其利用在对网站的远程代码执行漏洞利用上？<br>
我们将在下篇文章中具体分析，敬请关注。

审核人：yiwang   编辑：少爷

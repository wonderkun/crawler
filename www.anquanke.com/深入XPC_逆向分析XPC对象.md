> 原文链接: https://www.anquanke.com//post/id/168115 


# 深入XPC：逆向分析XPC对象


                                阅读量   
                                **185744**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Fortinet，文章来源：fortinet.com
                                <br>原文地址：[https://www.fortinet.com/blog/threat-research/a-look-into-xpc-internals—reverse-engineering-the-xpc-objects.html](https://www.fortinet.com/blog/threat-research/a-look-into-xpc-internals%E2%80%94reverse-engineering-the-xpc-objects.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t012a9f7f049dd92bc6.png)](https://p4.ssl.qhimg.com/t012a9f7f049dd92bc6.png)



## 一、前言

最近我在FortiGuard实验室一直在深入研究macOS系统安全，主要关注的是发现和分析IPC漏洞方面内容。在本文中，我将与大家分享XPC内部数据类型，可以帮助研究人员（包括我自己）快速分析XPC漏洞根源，也能深入分析针对这些漏洞的利用技术。

XPC是macOS/iOS系统上使用的增强型IPC框架，自10.7/5.0版引入以来，XPC的使用范围已经呈爆炸式增长。XPC依然包含没有官方说明文档的大量功能，具体实现也没有公开（例如，`libxpc`这个主工程为闭源项目）。XPC在两个层面上开放API：底层以及`Foundation`封装层。在本文中我们只关注底层API，这些API为`libxpc.dylib`直接导出的`xpc_*`函数。

这些API可以分为object API以及transport API。XPC通过`libxpc.dylib`提供自己的数据类型，具体数据类型如下所示：

[![](https://p1.ssl.qhimg.com/t0146926e109a4d919f.png)](https://p1.ssl.qhimg.com/t0146926e109a4d919f.png)

图1. XPC提供的数据类型

从C API角度来看，所有的对象实际上都是`xpc_object_t`。实际类型可以通过`xpc_get_type(xpc_object_t)`函数动态确定。所有数据类型可以使用对应的`xpc_objectType_create`函数创建，并且所有这些函数都会调用`_xpc_base_create(Class, Size)`函数，其中`Size`参数指定了对象的大小，而`Class`参数为某个`_OS_xpc_type_*`元类（`metaclass`）。

我们可以通过Hopper Disassembler v4看到 `_xpc_base_create`函数被多次引用。

[![](https://p3.ssl.qhimg.com/t010331597a4375024b.png)](https://p3.ssl.qhimg.com/t010331597a4375024b.png)

图2. 对`_xpc_base_create`函数的引用代码

我开发了Hopper的一个python脚本，可以自动找出调用`_xpc_base_create`函数时所使用的具体参数。如下python脚本可以显示Hopper Disassembler中XPC对象的大小。

```
def get_last2instructions_addr(seg, x):
                  last1ins_addr = seg.getInstructionStart(x - 1)
                  last2ins_addr = seg.getInstructionStart(last1ins_addr - 1)
                  last2ins = seg.getInstructionAtAddress(last2ins_addr)
                  last1ins = seg.getInstructionAtAddress(last1ins_addr)
                  print hex(last2ins_addr), last2ins.getInstructionString(), last2ins.getRawArgument(0), last2ins.getRawArgument(1)
                  print hex(last1ins_addr), last1ins.getInstructionString(), last1ins.getRawArgument(0), last1ins.getRawArgument(1)
                  return last2ins,last1ins
def run():
                  print '[*] Demonstrating XPC ojbect sizes using a hopper diassembler's python script'
                  xpc_object_sizes_dict = dict()
                  doc = Document.getCurrentDocument()
                  _xpc_base_create_addr = doc.getAddressForName('__xpc_base_create')
                  for i in range(doc.getSegmentCount()):
                                    seg = doc.getSegment(i)
                                    #print '[*]'+ seg.getName()
                                    if('__TEXT' == seg.getName()):
                                                      eachxrefs = seg.getReferencesOfAddress(_xpc_base_create_addr)
                                                      for x in eachxrefs:
                                                                        last2ins,last1ins = get_last2instructions_addr(seg,x)
                                                                        p = seg.getProcedureAtAddress(x)
                                                                        p_entry_addr =  p.getEntryPoint()
                                                                        pname = seg.getNameAtAddress(p_entry_addr)
                                                                        x_symbol = pname + '+' + hex(x - p_entry_addr)
                                                                        print hex(x),'(' + x_symbol + ')'
                                                                        ins0 = seg.getInstructionAtAddress(x - 5)
                                                                        ins1 = seg.getInstructionAtAddress(x - 12)
                                                                        if last2ins.getInstructionString() == 'mov' and last1ins.getInstructionString() == 'lea':
                                                                                          if last2ins.getRawArgument(0) == 'esi' and last1ins.getRawArgument(0) == 'rdi':
                                                                                                            indirect_addr = int(last1ins.getRawArgument(1)[7:-1],16)
                                                                                                            xpcObj_len = last2ins.getRawArgument(1)
                                                                                                            callerinfo = '__xpc_base_create('+ doc.getNameAtAddress(indirect_addr)+',' + xpcObj_len+ ');'
                                                                                                            if callerinfo not in xpc_object_sizes_dict.keys():
                                                                                                                              xpc_object_sizes_dict[callerinfo] = '#from ' + x_symbol
                                                                                                            else:
                                                                                                                              xpc_object_sizes_dict[callerinfo] = xpc_object_sizes_dict[callerinfo] + ',' + x_symbol
                                                                                                            print callerinfo
                                                                                                            #xpc_object_sizes_list.append(callerinfo)
                                                                        elif last2ins.getInstructionString() == 'lea' and last1ins.getInstructionString() == 'mov':
                                                                                          if last2ins.getRawArgument(0) == 'rdi' and last1ins.getRawArgument(0) == 'esi':
                                                                                                            indirect_addr = int(last2ins.getRawArgument(1)[7:-1],16)
                                                                                                            xpcObj_len = last1ins.getRawArgument(1)
                                                                                                            callerinfo = '__xpc_base_create('+ doc.getNameAtAddress(indirect_addr)+',' + xpcObj_len+ ');'
                                                                                                            if callerinfo not in xpc_object_sizes_dict.keys():
                                                                                                                              xpc_object_sizes_dict[callerinfo] = '#from ' + x_symbol

                                                                                                            else:
                                                                                                                              xpc_object_sizes_dict[callerinfo] = xpc_object_sizes_dict[callerinfo] + ',' + x_symbol
                                                                                                            print callerinfo
                                                                                                            #xpc_object_sizes_list.append(callerinfo)
                                                                        elif last2ins.getInstructionString() == 'lea' and last1ins.getInstructionString() == 'lea':
                                                                                          if last2ins.getRawArgument(0) == 'rsi' and last1ins.getRawArgument(0) == 'rdi':
                                                                                                            indirect_addr = int(last1ins.getRawArgument(1)[7:-1],16)
                                                                                                            xpcObj_len = last2ins.getRawArgument(1)[7:-1]
                                                                                                            callerinfo = '__xpc_base_create('+ doc.getNameAtAddress(indirect_addr)+',' + xpcObj_len+ ');'
                                                                                                            if callerinfo not in xpc_object_sizes_dict.keys():
                                                                                                                              xpc_object_sizes_dict[callerinfo] = '#from ' + x_symbol
                                                                                                            else:
                                                                                                                              xpc_object_sizes_dict[callerinfo] = xpc_object_sizes_dict[callerinfo] + ',' + x_symbol
                                                                                                            print callerinfo
                                                                                                            #xpc_object_sizes_list.append(callerinfo)
                                                                                          elif last2ins.getRawArgument(0) == 'rdi' and last1ins.getRawArgument(0) == 'rsi':
                                                                                                            indirect_addr = int(last2ins.getRawArgument(1)[7:-1],16)
                                                                                                            xpcObj_len = last1ins.getRawArgument(1)[7:-1]
                                                                                                            callerinfo = '__xpc_base_create('+ doc.getNameAtAddress(indirect_addr)+',' + xpcObj_len+ ');'
                                                                                                            if callerinfo not in xpc_object_sizes_dict.keys():
                                                                                                                              xpc_object_sizes_dict[callerinfo] = '#from ' + x_symbol
                                                                                                            else:
                                                                                                                              xpc_object_sizes_dict[callerinfo] = xpc_object_sizes_dict[callerinfo] + ',' + x_symbol
                                                                                                            print callerinfo
                                                                                                            #xpc_object_sizes_list.append(callerinfo)
                                                                        print '____________________________________________________________'
                  dict_len = len(xpc_object_sizes_dict)
                  print '[*] Total of XPC object: %d' % dict_len
                  for key in xpc_object_sizes_dict.keys():
                                    print key, xpc_object_sizes_dict[key]
if __name__ == '__main__':
                  run()
```

运行该脚本后，我们可以看到所有XPC对象大小，如下所示：

```
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_serializer,0x98);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_mach_send,0x8);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_activity,0x78);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_data,0x28);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_double,0x8);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_file_transfer,0x48);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_service_instance,0x78);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_uint64,0x8);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_bundle,0x238);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_pointer,0x8);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_string,0x10);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_pipe,r12+0x20);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_connection,r14+0xa8);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_shmem,0x18);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_dictionary,0xa8);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_uuid,0x10);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_connection,0xa8);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_endpoint,0x8);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_int64,0x8);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_date,0x8);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_fd,0x8);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_mach_recv,0x10);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_bool,0x8);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_array,0x10);
__xpc_base_create(_OBJC_CLASS_$_OS_xpc_service,0x5d);
```

[![](https://p0.ssl.qhimg.com/t010324588639ac36c4.png)](https://p0.ssl.qhimg.com/t010324588639ac36c4.png)

图3. python脚本输出结果，显示XPC对象大小

此时我们已经知道所有不同数据类型的XPC对象的大小。接下来我们可以看一下`_xpc_base_create`函数的实现。

[![](https://p5.ssl.qhimg.com/t01575e9d5b23c202fb.jpg)](https://p5.ssl.qhimg.com/t01575e9d5b23c202fb.jpg)

图4. `_xpc_base_create`函数的实现

可以看到XPC对象的实际大小等于`Size`参数+`0x18`。

然后我们需要进行一些逆向分析工作，检查所有对象的内存布局。在本文中，我想与大家分享主要类型的分析过程，其他类型会在后续文章中详细介绍。



## 二、主要类型分析

### <a class="reference-link" name="xpc_int64_t"></a>xpc_int64_t

我们可以使用`xpc_int64_create`函数来创建一个`xpc_int64_t`对象，如下所示：

[![](https://p0.ssl.qhimg.com/t01d849e36db206df45.png)](https://p0.ssl.qhimg.com/t01d849e36db206df45.png)

使用`LLDB`观察`xpc_int64_t`对象的内存布局：

[![](https://p2.ssl.qhimg.com/t01985c40befda8edc6.png)](https://p2.ssl.qhimg.com/t01985c40befda8edc6.png)

`xpc_uint64_t`对象的结构如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016958b889ce750982.png)

图5. `xpc_uint64_t`结构

### <a class="reference-link" name="xpc_uint64_t"></a>xpc_uint64_t

使用`xpc_uint64_create`函数创建`xpc_uint64_t`对象，代码如下：

[![](https://p4.ssl.qhimg.com/t017db1cf6aa92170c1.png)](https://p4.ssl.qhimg.com/t017db1cf6aa92170c1.png)

可以看到返回值不是有效的内存地址。我们需要在输入参数上执行一些算数运算来生成返回值。在这个例子中，XPC直接使用64位`unsigned integer`来表示`xpc_uint64_t`对象。

[![](https://p4.ssl.qhimg.com/t01a7ea8ad3d033f9a6.png)](https://p4.ssl.qhimg.com/t01a7ea8ad3d033f9a6.png)

创建`xpc_uint64_t`对象的另一个例子如下：

[![](https://p2.ssl.qhimg.com/t0188eb01dc2ee3d94b.png)](https://p2.ssl.qhimg.com/t0188eb01dc2ee3d94b.png)

在`LLDB`中`xpc_uint64_t`对象的内存布局如下所示：

[![](https://p4.ssl.qhimg.com/t017cc701d299845fb0.png)](https://p4.ssl.qhimg.com/t017cc701d299845fb0.png)

可以看到返回值指向的内存缓冲区对应的是`xpc_uint64_t`对象，且输入参数位于`0x18`偏移地址处。

接下来我们可以深入分析`xpc_uint64_create`函数的具体实现，如下所示：

[![](https://p3.ssl.qhimg.com/t017355c6fca9969b2b.png)](https://p3.ssl.qhimg.com/t017355c6fca9969b2b.png)

图6. `_xpc_uint64_create`函数具体实现

在该函数中，代码首先会将参数逻辑右移52位。

a) 如果结果不等于`0`，则会调用`_xpc_base_create`函数来创建XPC对象，然后将`0x08`（4字节长）写入`0x14`偏移处的缓冲区。最后，代码将参数（8字节长）写入`0x18`偏移处的缓冲区。

b) 如果结果等于`0`且全局变量`objc_debug_taggedpointer_mask`不等于`0`，那么就会执行`(value &lt;&lt; 0xc | 0x4f) ^ objc_debug_taggedpointer_obfuscator`。在`LLDB`调试器中，我们可以看到`objc_debug_taggedpointer_obfuscator`变量等于`0x5de9b03e5c731aae`，因此运算结果会等于`0x5de9b42a48670ae1`，这个值即为`_xpc_uint64_create`函数的返回值。如果结果为`0`，那么就与`a)`情况相同。

我们可以检查全局变量`objc_debug_taggedpointer_mask`及`objc_debug_taggedpointer_obfuscator`的值，如下所示：

[![](https://p4.ssl.qhimg.com/t0163a34f05e889236d.png)](https://p4.ssl.qhimg.com/t0163a34f05e889236d.png)

一旦我们知道`objc_debug_taggedpointer_obfuscator`的值，我们就可以计算出返回值。

[![](https://p0.ssl.qhimg.com/t01fc38c1c05e3c6938.png)](https://p0.ssl.qhimg.com/t01fc38c1c05e3c6938.png)

每个新进程实例所对应的`objc_debug_taggedpointer_obfuscator`都为随机值。现在我们可以跟踪一下这个变量的生成过程。

[![](https://p5.ssl.qhimg.com/t01337f07cf4db75e3d.png)](https://p5.ssl.qhimg.com/t01337f07cf4db75e3d.png)

可以看到，`objc_debug_taggedpointer_obfuscator`实际上是`libobjc.A.dylib`库中的一个全局变量。如下代码（源文件：`objc4-750/runtime/objc-runtime-new.mm`）可以用来生成随机的`objc_debug_taggedpointer_obfuscator`:

[![](https://p0.ssl.qhimg.com/t01953dfc2fe2d8dc4e.png)](https://p0.ssl.qhimg.com/t01953dfc2fe2d8dc4e.png)

图7. 初始化`objc_debug_taggedpointer_obfuscator`变量

可以使用`void _read_images(header_info **hList, uint32_t hCount, int totalClasses, int unoptimizedTotalClasses)`函数完成初始化工作，具体参考`objc-runtime-new.mm`中的源代码。在二进制镜像的初始化阶段中，我们还可以看到随机化的`objc_debug_taggedpointer_obfuscator`全局变量生成过程。

最后我们再给出`xpc_uint64_t`对象的结构，如下所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0189cf7215162dc49c.jpg)

图8. `xpc_uint64_t`对象结构

### <a class="reference-link" name="xpc_uuid_t"></a>xpc_uuid_t

我们可以使用`xpc_uuid_create`函数来创建`xpc_uuid_t`对象（UUID为universally unique identifier的缩写），如下所示：

[![](https://p5.ssl.qhimg.com/t01878f171a3ca48630.png)](https://p5.ssl.qhimg.com/t01878f171a3ca48630.png)

在`LLDB`中查看`xpc_uuid_t`对象的内存布局，如下所示：

[![](https://p2.ssl.qhimg.com/t018d1c9fb64bec84eb.png)](https://p2.ssl.qhimg.com/t018d1c9fb64bec84eb.png)

根据内存布局信息，我们可以轻松澄清`xpc_uuid_t`对象的结构：

[![](https://p5.ssl.qhimg.com/t0174998947f779f185.png)](https://p5.ssl.qhimg.com/t0174998947f779f185.png)

图9. `xpc_uuid_t`对象结构

### <a class="reference-link" name="xpc_double_t"></a>xpc_double_t

我们可以使用`xpc_double_create`函数来创建`xpc_double_t`对象，如下所示：

[![](https://p3.ssl.qhimg.com/t01f4829fd136066533.png)](https://p3.ssl.qhimg.com/t01f4829fd136066533.png)

在`LLDB`中查看`xpc_double_t`对象的内存布局：

[![](https://p1.ssl.qhimg.com/t0179c104e2a906ef69.png)](https://p1.ssl.qhimg.com/t0179c104e2a906ef69.png)

`xpc_double_t`对象的结构如下所示：

[![](https://p2.ssl.qhimg.com/t01dacb36025a1df962.png)](https://p2.ssl.qhimg.com/t01dacb36025a1df962.png)

图10. `xpc_double_t`对象结构

### <a class="reference-link" name="xpc_date_t"></a>xpc_date_t

我们可以使用`xpc_date_create`函数来创建`xpc_date_t`对象，如下所示：

[![](https://p3.ssl.qhimg.com/t01c445995ea33da9a6.png)](https://p3.ssl.qhimg.com/t01c445995ea33da9a6.png)

在`LLDB`中查看`xpc_date_t`对象的内存结构：

[![](https://p1.ssl.qhimg.com/t019f16a7f8d6b0c48a.png)](https://p1.ssl.qhimg.com/t019f16a7f8d6b0c48a.png)

`xpc_date_t`对象的结构如下所示：

[![](https://p3.ssl.qhimg.com/t01309c24dfa66f0ed8.png)](https://p3.ssl.qhimg.com/t01309c24dfa66f0ed8.png)

图11. `xpc_date_t`对象结构

### <a class="reference-link" name="xpc_string_t"></a>xpc_string_t

可以使用`xpc_string_create`函数创建`xpc_string_t`对象，如下所示：

[![](https://p5.ssl.qhimg.com/t0193e3bd37aa702d3a.png)](https://p5.ssl.qhimg.com/t0193e3bd37aa702d3a.png)

在`LLDB`中查看`xpc_string_t`对象的内存布局：

[![](https://p1.ssl.qhimg.com/t01e0683199ce0a7ea2.png)](https://p1.ssl.qhimg.com/t01e0683199ce0a7ea2.png)

`xpc_string_t`对象的结构如下所示：

[![](https://p4.ssl.qhimg.com/t018139cb0b3fbc382e.png)](https://p4.ssl.qhimg.com/t018139cb0b3fbc382e.png)

图12. `xpc_string_t`对象结构

### <a class="reference-link" name="xpc_array_t"></a>xpc_array_t

可以使用`xpc_array_create`函数创建`xpc_array_t`对象，如下所示：

[![](https://p0.ssl.qhimg.com/t0149273b0f77076ba9.png)](https://p0.ssl.qhimg.com/t0149273b0f77076ba9.png)

在这个例子中，我们首先创建了一个`xpc_array_t`对象，然后将3个值加入数组中。`xpc_array_create`函数声明如下：

[![](https://p3.ssl.qhimg.com/t018853e4de9bb370af.png)](https://p3.ssl.qhimg.com/t018853e4de9bb370af.png)

`xpc_array_create`函数的实现如下所示：

[![](https://p4.ssl.qhimg.com/t01f9b1aa47823f6741.png)](https://p4.ssl.qhimg.com/t01f9b1aa47823f6741.png)

图13. `xpc_array_create`函数实现代码

从上图中，我们可知数组的大小等于`(count*2+0x08)`，这个值存放在`0x1c`偏移处（4字节大小）。指向已分配缓冲区的指针存放于`0x20`偏移处，已分配缓冲区的大小等于`(count*2+0x8)*0x8`。

在`LLDB`中观察该对象的内存布局，如下所示：

[![](https://p3.ssl.qhimg.com/t0183e85bf49e76869a.png)](https://p3.ssl.qhimg.com/t0183e85bf49e76869a.png)

数组的长度存放于`0x18`偏移处（4字节）。`0x20`偏移处的指针指向的是已分配的`xpc_object_t`缓冲区，缓冲区中存放的是数组中的所有元素（`xpc_object_t`）。`xpc_array_t`对象的结构如下所示：

[![](https://p2.ssl.qhimg.com/t013422b65e3d908823.png)](https://p2.ssl.qhimg.com/t013422b65e3d908823.png)

图14. `xpc_array_t`对象结构

### <a class="reference-link" name="xpc_data_t"></a>xpc_data_t

可以使用`xpc_data_create`函数创建`xpc_data_t`对象，如下所示：

[![](https://p0.ssl.qhimg.com/t0169246e2493d8036c.png)](https://p0.ssl.qhimg.com/t0169246e2493d8036c.png)

在`LLDB`中观察`xpc_data_t`对象的内存布局：

[![](https://p1.ssl.qhimg.com/t01c942ba238aeed833.png)](https://p1.ssl.qhimg.com/t01c942ba238aeed833.png)

`xpc_data_t`对象的结构如下图所示：

[![](https://p1.ssl.qhimg.com/t019118a01bb9050a59.jpg)](https://p1.ssl.qhimg.com/t019118a01bb9050a59.jpg)

图15. `xpc_data_t`对象结构

如果数据缓冲区的长度大于等于`0x4000`，那么`0x14`偏移处的值则会等于`(length+0x7)&amp;0xfffffffc`，否则就等于`0x04`。

### <a class="reference-link" name="xpc_dictionary_t"></a>xpc_dictionary_t

`xpc_dictionary_t`类型在XPC中扮演着重要角色。端点间所有消息都以字典格式传递，这样序列化/反序列化处理起来更加方便。与其他主要类型相比，`xpc_dictionary_t`的内部构造更为复杂。让我们一步一步揭开面纱。

可以使用`xpc_dictionary_create`函数创建`xpc_dictionary_t`对象，如下所示。

[![](https://p4.ssl.qhimg.com/t018685af74bd2315aa.png)](https://p4.ssl.qhimg.com/t018685af74bd2315aa.png)

在`LLDB`中观察`xpc_dictionary_t`对象的内存布局。

[![](https://p0.ssl.qhimg.com/t01ae3ba245b85b749d.jpg)](https://p0.ssl.qhimg.com/t01ae3ba245b85b749d.jpg)

`hash_buckets`字段是长度为`7`的一个数组，`hash_buckets[7]`中的每个元素存放的是XPC字典链表项。比如，`hash_buckets[3]`的内存布局如下所示：

[![](https://p1.ssl.qhimg.com/t01947efee5e36cbc09.jpg)](https://p1.ssl.qhimg.com/t01947efee5e36cbc09.jpg)

可以确定XPC字典链表项的结构如下所示：

[![](https://p3.ssl.qhimg.com/t01db45533d41002ff3.png)](https://p3.ssl.qhimg.com/t01db45533d41002ff3.png)

图16. XPC字典链表项结构

最后，我们再给出`xpc_dictionary_t`对象的结构，如下所示。

[![](https://p3.ssl.qhimg.com/t01ad08fcba3e18f929.jpg)](https://p3.ssl.qhimg.com/t01ad08fcba3e18f929.jpg)

目前我们已经讨论了XPC对象的主要数据类型，也分析了这些对象的内部结构及内存布局。了解内部结构后，我们不仅能快速分析XPC中的漏洞，也能在跟踪和解析XPC相关漏洞利用技术中事半功倍。



## 三、调试环境

```
macOS Mojave version 10.14.1
```

需要注意的是，其他macOS版本上这些XPC对象结构可能有所不同。



## 四、参考资料

[https://thecyberwire.com/events/docs/IanBeer_JSS_Slides.pdf](https://thecyberwire.com/events/docs/IanBeer_JSS_Slides.pdf)

OS Internals, Volume I: User Mode by Jonathan Levin

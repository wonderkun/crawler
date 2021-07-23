> 原文链接: https://www.anquanke.com//post/id/151487 


# 使用XPC字符串读取进程内存


                                阅读量   
                                **184465**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Brandon Azad，文章来源：bazad.github.io
                                <br>原文地址：[https://bazad.github.io/2018/07/xpc-string-leak/](https://bazad.github.io/2018/07/xpc-string-leak/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01f8a7cf8d518a8f1b.jpg)](https://p2.ssl.qhimg.com/t01f8a7cf8d518a8f1b.jpg)

这是一篇关于我偶然发现的另一个bug的短文。在逆向libxpc时，我注意到XPC字符串反序列化并不检查反序列化的字符串是否实际上和序列化长度声明一样长：XPC字符串反序列化没有检查反序列化的字符串实际上是否与序列化长度声明一样长：它可能是短的。 也就是说，序列化的XPC消息可能声称该字符串是1000字节长，即使该字符串在索引100处包含空字节。生成的`OS_xpc_string`对象将认为其堆上的C字符串比实际长。

虽然直接利用这个漏洞来执行任意代码是很困难的，但是我们可以采取另一种方法。 在将字符串序列化为消息时，`OS_xpc_string`对象的长度字段是可信的，因此如果我们可以让XPC服务向我们发回它刚刚反序列化的字符串，它将从堆C-string缓冲区中重读并发送给我们 消息中的所有额外数据，为我们提供该进程堆内存的快照。生成的exploit primitive 类似于Heartbleed(心脏出血)漏洞如何用于从OpenSSL驱动的服务器内存中越界读取堆数据。



## (XP)C字符串和空字节

当我注意到字符串反序列化函数`_xpc_string_deserialize`的特性时，我实际上正在反汇编libxpc以便理解这个网络传输协议:

```
OS_xpc_string *__fastcall _xpc_string_deserialize(OS_xpc_serializer *xserializer)
`{`
    OS_xpc_string *xstring; // rbx@1
    char *string; // rax@4
    char *contents; // [rsp+8h] [rbp-18h]@1
    size_t size; // [rsp+10h] [rbp-10h]@1 MAPDST

    xstring = 0LL;
    contents = 0LL;
    size = 0LL;
    if ( _xpc_string_get_wire_value(xserializer, (const char **)&amp;contents, &amp;size) )
    `{`
        if ( contents[size - 1] || (string = _xpc_try_strdup(contents)) == 0LL )
        `{`
            xstring = 0LL;
        `}`
        else
        `{`
            xstring = _xpc_string_create(string, size - 1);
            LOBYTE(xstring-&gt;flags) |= 1u;
        `}`
    `}`
    return xstring;
`}`
```

如果你仔细观察，你会发现缺少了一个特别的检查。 函数`_xpc_string_get_wire_value` 似乎得到了一个指向字符串数据字节的指针 以及这个字符记录的长度，然后，代码在复制字符串并使用`_xpc_string_create`创建实际的`OS_xpc_string`对象之前，检查索引`size-1`的字节是否为空，并传递复制的字符串和让`size-1`。

对`contents[size - 1]`为NULL的检查确实确保序列化的字符串不大于`size`字节，但不确保字符串不小于`szie`字节： 在序列化的字符串数据中可能会有一个空字节 ,这是有问题的，因为未经检查的大小值通过函数`_xpc_string_create`传播到结果的`OS_XPC_String`对象，从而导致堆上字符串对象的报告长度和实际长度之间的不一致。



## XPC消息反射利用

任何重要的漏洞都必须利用产生的XPC字符串对象的长度与其堆缓冲区的内容之间的不一致。 这意味着我们需要在一些XPC服务中查找代码，该服务使用length字段和string内容以一种有意义的方式。不幸的是，可能导致内存损坏的使用模式似乎不太可能;您需要编写一些非常复杂的代码，以使一个太短的字符串覆盖缓冲区：

```
pc_object_t string = xpc_dictionary_get_value(message, "key");
char buf[strlen(xpc_string_get_string_ptr(string))];
memcpy(buf, xpc_string_get_string_ptr(string), xpc_string_get_length(string));
```

​ 果然，我找不到任何使用XPC字符串的iOS服务，这可能会导致内存损坏。

​ 然而，仍然有另一种方法可以利用这个bug来完成有用的工作，这是通过利用`libxpc`自己在服务中的行为来反射XPC消息返回给客户端。

尽管libxpc的客户端没有以有意义的方式使用`OS_XPC_String`对象的`length`字段，但是`libxpc`库本身的某些部分是这样做的： 特别是，XPC字符串序列化代码在将字符串内容复制到XPC消息时确实信任存储的length字段。

这是`_xpc_string_serialize`:的反编译实现：

```
void __fastcall _xpc_string_serialize(OS_xpc_string *string, OS_xpc_serializer *serializer)
`{`
    int type; // [rsp+8h] [rbp-18h]@1
    int size; // [rsp+Ch] [rbp-14h]@1

    type = *((_DWORD *)&amp;OBJC_CLASS___OS_xpc_string + 10);
    _xpc_serializer_append(serializer, &amp;type, 4uLL, 1, 0, 0);
    size = LODWORD(string-&gt;length) + 1;
    _xpc_serializer_append(serializer, &amp;size, 4uLL, 1, 0, 0);
    _xpc_serializer_append(serializer, string-&gt;string, string-&gt;length + 1, 1, 0, 0);
`}`
```

在序列化字符串时，`OS_XPC_String`的`lenth`参数是可信的，这将导致大量字节从堆复制到序列化的消息中。 如果反序列化字符串比其记录的长度短，则消息将使用超出范围的堆数据填充。

攻击仍然仅限于将XPC消息的某些部分反映回客户端的XPC服务，但这种情况更为常见。



## 把diagnosticd作为目标

在macOS和iOS, diagnosticd 是一个有希望的攻击候选，不仅因为它unsandboxed（无沙盒防护） 、root 和`task_for_pid-allow`。Diagnosticd负责处理诊断消息（例如，os_log生成的消息）并将其流式传输给有权利接收这些消息的客户端。通过注册来接收我们自己的诊断流，然后发送带有比预期字符串短的诊断信息，我们可以获得诊断堆中一些数据的快照，这有助于在流程中获得代码执行。

我写了一个名为 [xpc-string-leak](https://github.com/bazad/xpc-string-leak) 的POC，它可以用来从diagnosticd 中对任意大小的越界堆内容进行采样。

利用流程相当简单 :我们注册了一个Mach端口，它可以从我们自己的进程接收一个诊断消息流，生成一个格式错误的过短的短字符串的诊断消息，然后侦听我们在前面注册的端口，以获取包含越界的诊断消息堆数据。

有趣的是，由于diagnosticd也从其他进程接收日志消息，因此越界的堆数据可能也包含来自其他进程的敏感信息。 因此，即使没有在诊断中实现代码执行，该bug也存在用户隐私的影响。



## 时间线

我在2018年初（1月或2月）发现了这个漏洞， 但在5月之前一直没想起研究。我在5月9日向苹果公司报告了这一问题 ，并于7月9日将其指定为CVE-2018-4248，并在 [iOS 11.4.1](https://support.apple.com/en-us/HT208938) 和 [macOS 10.13.6](https://support.apple.com/en-us/HT208937) 中进行了修补。

审核人：yiwang   编辑：边边

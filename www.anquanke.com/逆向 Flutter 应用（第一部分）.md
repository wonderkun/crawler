> 原文链接: https://www.anquanke.com//post/id/205876 


# 逆向 Flutter 应用（第一部分）


                                阅读量   
                                **334723**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Andre Lipke，文章来源：blog.tst.sh
                                <br>原文地址：[https://blog.tst.sh/reverse-engineering-flutter-apps-part-1/](https://blog.tst.sh/reverse-engineering-flutter-apps-part-1/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t012f07d441226a202f.png)](https://p0.ssl.qhimg.com/t012f07d441226a202f.png)



## 第一章 掉进兔子洞

要开始这段逆向旅程，先来了解一下 Flutter 是如何工作的。

可能你早就知道：渲染管道和组件库是 Flutter 的基石，也是 Flutter 能够跨平台并在不同设备上保持设计一致性的根本。

和大多数平台不同，Flutter 框架的所有基础渲染组件（包括动画、布局、绘画等）全部是公开的，见 [package:flutter](https://github.com/flutter/flutter/tree/master/packages/flutter)。

这是官方 wiki 中 Flutter 引擎的[架构图](https://github.com/flutter/flutter/wiki/The-Engine-architecture)：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.pxtst.com/content/images/2020/02/framework.png)

从逆向角度来说，最有意思的当然是 Dart 层，app 的逻辑可都在这儿。那 Dart 层长什么样呢？

Flutter 把 Dart 编译成 native 层的汇编代码和使用格式，现在还没有公开的详细文档，更别说反编译重打包了。反观其他平台，比如 React Native，压缩过的 JavaScript 对分析修改基本没有影响，还有 Android，Java 的字节码文档非常详细，免费的反编译工具更是多得过分。

对逆向工程师来说，虽然 Flutter 应用没有混淆加密（默认配置），但由于目前没有深入甚至是初步的 Dart 内部原理知识，进行分析仍然十分困难。这样看来，Flutter 非常优秀，你的 Flutter 代码也差不多逃过了窥探。

接下来我会介绍 Flutter 应用的编译过程并详细说明怎样逆向它的编译产物。



## 快照

Dart SDK 通用性强，通过不同的配置就可以在不同平台上集成 Dart 代码。

运行 Dart 最简单的方法是直接执行 `dart` 读取 dart 源文件。Dart 的基本组成部分有前端（解析Dart 代码）、运行时（提供运行环境）和 JIT 编译器。

`dart` 也能创建和执行[快照](https://github.com/dart-lang/sdk/wiki/Snapshots) – Dart 的预编译形式，快照通常用来提升经常使用的命令行工具的运行速度，比如 `pub` （注：Dart 的包管理器）。

```
ping@debian:~/Desktop$ time dart hello.dart
Hello, World!

real    0m0.656s
user    0m0.920s
sys     0m0.084s

ping@debian:~/Desktop$ dart --snapshot=hello.snapshot hello.dart
ping@debian:~/Desktop$ time dart hello.snapshot
Hello, World!

real    0m0.105s
user    0m0.208s
sys     0m0.016s
```

可以看到，使用快照时启动时间低得多。

快照的默认格式是 [kernel](https://github.com/dart-lang/sdk/wiki/Kernel-Documentation) – Dart 代码的中间表示（抽象语法树）。

以调试模式运行 Flutter 应用时，flutter 工具会创建一个内核快照，然后以调试运行时和 JIT 运行在 Android 应用中，这样你就可以通过热重载调试并实时修改代码了。

不幸的是，移动设备上远程代码执行漏洞层出不穷，要使用自己的 JIT 编译器难度让猛男皱眉，iOS 直接禁止执行动态生成的代码。

不过还有两种快照 `app-jit` 和 `app-aot` 可以用，它们使用预编译机器码，使得初始化比内核快照快，但这两种不能跨平台。其中快照 `app-aot` 只有机器码没有内核。

快照生成工具是 `gen_snapshots` ，工具位置：`flutter/bin/cache/artifacts/engine/&lt;arch&gt;/&lt;target&gt;/`，稍后介绍。

快照又不仅仅是 Dart 代码的编译形式，它是 main 函数被调用之前虚拟机堆数据的“快照”。Dart 的独特性就体现在这儿，也是它比其他运行时初始化更快的原因之一。

编译 release 版本时，Flutter 就会采用这些预先编译快照。在用 `flutter build apk` 生成 Android APK 文件时，快照在这些文件中：

```
ping@debian:~/Desktop/app/lib$ tree .
.
├── arm64-v8a
│   ├── libapp.so
│   └── libflutter.so
└── armeabi-v7a
    ├── libapp.so
    └── libflutter.so
```

有两个 `libapp.so`，分别是 64 位和 32 位。

以免误解，这里 `gen_snapshots` 生成的 ELF 文件并不会导出 dart 方法，也不能从外部直接调用。实际上它是 `clustered snapshot` 格式的容器，编译的代码存放在不同的节里，结构如下：

```
ping@debian:~/Desktop/app/lib/arm64-v8a$ aarch64-linux-gnu-objdump -T libapp.so

libapp.so:     file format elf64-littleaarch64

DYNAMIC SYMBOL TABLE:
0000000000001000 g    DF .text  0000000000004ba0 _kDartVmSnapshotInstructions
0000000000006000 g    DF .text  00000000002d0de0 _kDartIsolateSnapshotInstructions
00000000002d7000 g    DO .rodata        0000000000007f10 _kDartVmSnapshotData
00000000002df000 g    DO .rodata        000000000021ad10 _kDartIsolateSnapshotData
```

之所以预编译的快照采用共享对象而不是正常的快照文件形式，是因为在 app 启动时，`gen_snapshots` 生成的机器码需要以可执行权限加载进内存，最好的方式就是通过 ELF 文件。这样 `.text` 段中的内容会被 `linker` 加载进可执行内存，以便 Dart 运行时随时调用。

发现有两种快照了吗？VM 快照和 Isolate 快照。

Isolate 用来执行后台任务， `app-aot` 快照需要用到，它不像 `dart` 可执行文件一样能够在运行时动态加载。



## Dart sdk

还好 Dart 是完全开源的，我们在逆向快照格式时不至于变成无头苍蝇。

在开始实验之前还需要搭建 Dart SDK，参考这里的文档：[https://github.com/dart-lang/sdk/wiki/Building](https://github.com/dart-lang/sdk/wiki/Building)。

想要用 flutter 工具生成 `libapp.so` ？不好意思，没有文档。

flutter sdk 自带 `gen_snapshots` ，指定 `create_sdk` 进行标准编译 dart 时是没有 `gen_snapshots` 的，它在 SDK 中独立存在，执行下面的命令生成 arm 平台的 `gen_snapshot` ：

```
./tools/build.py -m product -a simarm gen_snapshot
```

通常情况下只能生成运行目标架构的快照，为了解决这个问题他们提供了 sim 产物，可以模拟目标平台上的快照生成，但是也有限制，比如不能在 32 位系统上生成 aarch64 和 x86_64 的快照。

开始编译 `libapp.so` 前需要先编译 dill 文件：

```
~/flutter/bin/cache/dart-sdk/bin/dart ~/flutter/bin/cache/artifacts/engine/linux-x64/frontend_server.dart.snapshot --sdk-root ~/flutter/bin/cache/artifacts/engine/common/flutter_patched_sdk_product/ --strong --target=flutter --aot --tfa -Ddart.vm.product=true --packages .packages --output-dill app.dill package:foo/main.dart
```

Dill 文件的格式实际上和内核快照一样，格式参考：[https://github.com/dart-lang/sdk/blob/master/pkg/kernel/binary.md](https://github.com/dart-lang/sdk/blob/master/pkg/kernel/binary.md)

这个格式是 dart 代码在各个工具之间的通用表达，包括 `gen_snapshot` 和 `analyzer`。

有了 `app.dill` 终于可以生成 `libapp.so` 了：

```
gen_snapshot --causal_async_stacks --deterministic --snapshot_kind=app-aot-elf --elf=libapp.so --strip app.dill
```

一旦可以手动生成 `libapp.so`，修改 SDK 并打印逆向 AOT 快照格式需要的调试信息就很容易了。

一个小知识：Dart 可是由创建了最先进（有争议）的 JavaScript V8 解释器的一些人设计的。Dart 虚拟机设计得非常好，我觉得人们对它的重视不够。



## 快照剖析

AOT 快照非常复杂，文件格式是自定义的且没有文档，需要先在调试器里手动走过它的序列化过程，然后才能实现文件格式解析。

和快照生成相关的源文件：
<li>Cluster 序列化/反序列化
[`vm/clustered_snapshot.h`](https://github.com/dart-lang/sdk/blob/7340a569caac6431d8698dc3788579b57ffcf0c6/runtime/vm/clustered_snapshot.h)
[`vm/clustered_snapshot.cc`](https://github.com/dart-lang/sdk/blob/7340a569caac6431d8698dc3788579b57ffcf0c6/runtime/vm/clustered_snapshot.cc)
</li>
<li>ROData 序列化
[`vm/image_snapshot.h`](https://github.com/dart-lang/sdk/blob/7340a569caac6431d8698dc3788579b57ffcf0c6/runtime/vm/image_snapshot.h)
[`vm/image_snapshot.cc`](https://github.com/dart-lang/sdk/blob/7340a569caac6431d8698dc3788579b57ffcf0c6/runtime/vm/image_snapshot.cc)
</li>
<li>读取流/ 写入流
[`vm/datastream.h`](https://github.com/dart-lang/sdk/blob/7340a569caac6431d8698dc3788579b57ffcf0c6/runtime/vm/datastream.h)
</li>
<li>Object 定义
[`vm/object.h`](https://github.com/dart-lang/sdk/blob/7340a569caac6431d8698dc3788579b57ffcf0c6/runtime/vm/object.h)
</li>
<li>ClassId 枚举
[`vm/class_id.h`](https://github.com/dart-lang/sdk/blob/7340a569caac6431d8698dc3788579b57ffcf0c6/runtime/vm/class_id.h)
</li>
我花了两周时间实现了一个能解析快照的命令行工具，可以帮助我们查看应用的数据构成。下面是快照数据块的布局总览：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.pxtst.com/content/images/2020/02/snapshot_data-1.png)

Isolate 中的每个 `RawObject*` 对象的序列化由对应的 `SerializationCluster` 完成，索引是其 class id。这些对象囊括了代码、实例、类型、原语、闭包、常量等等，稍后详细介绍。

Isolate 序列化完成后，每个对象被加入 Isolate 对象池里，便于在同一上下文中引用。

Clusters 序列化分三个步骤：Trace、Alloc 和 Fill 。

在 trace 阶段，根节点们和在广度优先搜索时它们引用的对象被添加到一个队列里，同时生成每个对象的 `SerializationCluster` 。

根节点是虚拟机用到的对象的集合，位于 isolate 的 `ObjectStore` 中，我们用它定位库和类。VM 快照中的 `StubCode` 基对象在 isolates 中是共享的。

`Stubs` 基本都是手写的汇编代码，dart 代码可以调用进去，实现和运行时的安全通信。

tracing 完成后，cluster 的基本信息就写入完成了，最重要的是知道了待分配对象的数量。

在 alloc 阶段，会调用每个 cluster 的 `WriteAlloc` 函数来写入分配原始对象需要的所有信息，大部分是该 cluster 的 class id 和对象的数量。

每个 cluster 中的对象的 object id 是按照分配顺序递增赋值的，之后在 fill 阶段解析对象引用时会用到。

可能你注意到缺了索引和 cluster 大小相关的信息，要得到我们需要的信息必须完整读取整个快照。现在要进行逆向有两条路可选：一是给 31+ cluster 类型实现反序列化（这个我已经做了），二是把快照加载到修改过的运行时里提取信息（跨架构很困难）。

下面举一个 cluster 中数组的例子 `[123, 42]`：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.pxtst.com/content/images/2020/02/cluster_alloc-3.png)

如果一个对象引用了另一个对象（比如数组元素），serializer 在 alloc 阶段把 object id 初始化（如上图所示）。

简单对象如 Mint 和 Smi 类型的对象的创建在 alloc 阶段就完成了，因为它们不引用其他对象。

之后写入根引用的值，包括核心类型的对象 id、库、类、缓存、静态异常和其他对象。

最后是 ROData 的写入，ROData 直接映射进 `RawObject*` 的内存，这样反序列化过程就能少一步。

ROData 最重要的类型是 `RawOneByteString`，作为库/类/函数名称的类型。ROData 是以偏移引用的，也是快照数据中唯一可以不用解码的地方。

和 ROData 类似，`RawInstruction` 对象是指向快照数据的指针，存储在可执行指令区而不是快照主数据区。

下面是编译 app 时常见的 SerializationCluster：

```
idx | cid | ClassId enum        | Cluster name
----|-----|---------------------|----------------------------------------
  0 |   5 | Class               | ClassSerializationCluster
  1 |   6 | PatchClass          | PatchClassSerializationCluster
  2 |   7 | Function            | FunctionSerializationCluster
  3 |   8 | ClosureData         | ClosureDataSerializationCluster
  4 |   9 | SignatureData       | SignatureDataSerializationCluster
  5 |  12 | Field               | FieldSerializationCluster
  6 |  13 | Script              | ScriptSerializationCluster
  7 |  14 | Library             | LibrarySerializationCluster
  8 |  17 | Code                | CodeSerializationCluster
  9 |  20 | ObjectPool          | ObjectPoolSerializationCluster
 10 |  21 | PcDescriptors       | RODataSerializationCluster
 11 |  22 | CodeSourceMap       | RODataSerializationCluster
 12 |  23 | StackMap            | RODataSerializationCluster
 13 |  25 | ExceptionHandlers   | ExceptionHandlersSerializationCluster
 14 |  29 | UnlinkedCall        | UnlinkedCallSerializationCluster
 15 |  31 | MegamorphicCache    | MegamorphicCacheSerializationCluster
 16 |  32 | SubtypeTestCache    | SubtypeTestCacheSerializationCluster
 17 |  36 | UnhandledException  | UnhandledExceptionSerializationCluster
 18 |  40 | TypeArguments       | TypeArgumentsSerializationCluster
 19 |  42 | Type                | TypeSerializationCluster
 20 |  43 | TypeRef             | TypeRefSerializationCluster
 21 |  44 | TypeParameter       | TypeParameterSerializationCluster
 22 |  45 | Closure             | ClosureSerializationCluster
 23 |  49 | Mint                | MintSerializationCluster
 24 |  50 | Double              | DoubleSerializationCluster
 25 |  52 | GrowableObjectArray | GrowableObjectArraySerializationCluster
 26 |  65 | StackTrace          | StackTraceSerializationCluster
 27 |  72 | Array               | ArraySerializationCluster
 28 |  73 | ImmutableArray      | ArraySerializationCluster
 29 |  75 | OneByteString       | RODataSerializationCluster
 30 |  95 | TypedDataInt8Array  | TypedDataSerializationCluster
 31 | 143 | &lt;instance&gt;          | InstanceSerializationCluster
...
 54 | 463 | &lt;instance&gt;          | InstanceSerializationCluster
```

快照里还有些其他的 cluster，但目前为止我只在一个 Flutter 应用里见过，就不再列举了。

`ClassId` 枚举对象里预定义了 class ID 集合，在 Dart 2.4.0 版本中有 142 个 ID，此范围之外或没有相关联 cluster 的 ID 单独写在 `InstanceSerializationCluster` 中。

终于到了可以能彻底地查看快照结构的解析器部分了，从根对象表中的库开始。

通过对象树可以定位函数，以 `package:ftest/main.dart` 的 `main` 函数为例：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.pxtst.com/content/images/2020/01/dartdec-graph-1.png)

如你所见 ，release 版本的快照是包含库名、类名和函数名的。如果不混淆 Dart 是没办法移除这些符号的，见 [https://github.com/flutter/flutter/wiki/Obfuscating-Dart-Code](https://github.com/flutter/flutter/wiki/Obfuscating-Dart-Code)。

目前这种混淆可能不值得，但未来这种情况很可能会改善，变得更合理易用，就像 Android 的 proguard 和 web 的 sourcemaps 。

机器码以 `Instruction` 对象存储，`Code` 对象以指定数据起始偏移指向 `Instruction` 对象。



## RawObject

Dart 虚拟机中所有的对象都是 `RawObject`，这些类的定义可以在 `vm/raw_object.h` 中找到。

根据递增的写屏障标志，只要你在生成的代码中声明，就可以随意读取、移动 `RawObject*` ，GC 能通过标志被动地扫描追踪引用。

下面是类的树形图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.pxtst.com/content/images/2020/02/classTree-1.png)

`RawInstance` 在 dart 世界中的类型都是 `Object`，在 dart 代码和方法调用时都能看到。非实例对象是内部的，只存在于引用跟踪、垃圾回收时，它们没有相同的 dart 类型。

每个对象都以一个 uint32_t 类型的标志位开头：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://blog.pxtst.com/content/images/2020/02/objtags-1.png)

这里的 Class ID 和之前 cluster 序列化的 class id 一样，定义在 [vm/class_id.h](https://github.com/dart-lang/sdk/blob/7340a569caac6431d8698dc3788579b57ffcf0c6/runtime/vm/class_id.h) ，也包括用户定义的开头，在 `kNumPredefinedCids`。

Size 和 GC data 垃圾回收时使用，基本可以忽略。

如果 canonical 位有值，代表这个对象是唯一的，没有对象和它相等，如 `Symbol` 和 `Type` 的实例。

对象都很小，`RawInstance` 通常只有 4 字节，也不使用虚拟方法。

这些都意味着分配一个对象并填充字段基本没有消耗，flutter 里这种操作太多了。



## Hello, World!

Cool，现在已经可以根据名称定位方法了，但怎么弄清楚它们做了什么呢？

从这里开始，逆向更难了，我们要挖掘 `Instruction` 对象中的汇编代码了。

Dart 没有用流行的编译后端比如 clang，而是用针对 AOT 优化了的 JIT 编译器进行代码生成。

如果你没有研究过 JIT 代码，和 C 代码的等比产物相比 JIT 的产物在某些地方有些膨胀了。并不是说 Dart 做得不好，而是设计的目的在于在运行时能够快速地生成代码，硬说性能的话手写的汇编指令速度可是完胜 clang/gcc 。

实际上生成代码优化越少我们的优势越大，和生成它的高级中间语言更接近。

代码生成相关的可以在以下文件中找到：
- `vm/compiler/backend/il_&lt;arch&gt;.cc`
- `vm/compiler/assembler/assembler_&lt;arch&gt;.cc`
- `vm/compiler/asm_intrinsifier_&lt;arch&gt;.cc`
- `vm/compiler/graph_intrinsifier_&lt;arch&gt;.cc`
下面是 dart A64 汇编程序的寄存器和调用约定：

```
r0 |     | Returns
r0  -  r7 |     | Arguments
r0  - r14 |     | General purpose
      r15 | sp  | Dart stack pointer
      r16 | ip0 | Scratch register
      r17 | ip1 | Scratch register
      r18 |     | Platform register
r19 - r25 |     | General purpose
r19 - r28 |     | Callee saved registers
      r26 | thr | Current thread
      r27 | pp  | Object pool
      r28 | brm | Barrier mask
      r29 | fp  | Frame pointer
      r30 | lr  | Link register
      r31 | zr  | Zero / CSP
```

A64 采用了 [AArch64 的调用约定](https://infocenter.arm.com/help/topic/com.arm.doc.ihi0055b/IHI0055B_aapcs64.pdf) 但多了几个全局寄存器：
<li>R26 / THR：指向当前虚拟机 `Thread`，见 [vm/thread.h](https://github.com/dart-lang/sdk/blob/7340a569caac6431d8698dc3788579b57ffcf0c6/runtime/vm/thread.h)
</li>
<li>R27 / PP：指向当前上下文的 `ObjectPool`，见 [vm/object.h](https://github.com/dart-lang/sdk/blob/7340a569caac6431d8698dc3788579b57ffcf0c6/runtime/vm/object.h#L4275)
</li>
- R28 / BRM：barrier mask，用于递增型垃圾回收
类似的，这是 A32 的寄存器：

```
r0 -  r1 |     | Returns
r0 -  r9 |     | General purpose
r4 - r10 |     | Callee saved registers
      r5 | pp  | Object pool
     r10 | thr | Current thread
     r11 | fp  | Frame pointer
     r12 | ip  | Scratch register
     r13 | sp  | Stack pointer
     r14 | lr  | Link register
     r15 | pc  | Program counter
```

A64 更常见，但是我会以 A32 为主，A32 阅读和反汇编简单点。

在使用 `gen_snapshot` 时带上 `--disassemble-optimized` 参数就可以看 IR 了，但是只能用在 debug/release 产物，生产环境是不行的。

举个栗子，hello world ：

```
void hello() `{`
  print("Hello, World!");
`}`
```

汇编代码中可以看到：

```
Code for optimized function 'package:dectest/hello_world.dart_::_hello' `{`
        ;; B0
        ;; B1
        ;; Enter frame
0xf69ace60    e92d4800               stmdb sp!, `{`fp, lr`}`
0xf69ace64    e28db000               add fp, sp, #0
        ;; CheckStackOverflow:8(stack=0, loop=0)
0xf69ace68    e59ac024               ldr ip, [thr, #+36]
0xf69ace6c    e15d000c               cmp sp, ip
0xf69ace70    9bfffffe               blls +0 ; 0xf69ace70
        ;; PushArgument(v3)
0xf69ace74    e285ca01               add ip, pp, #4096
0xf69ace78    e59ccfa7               ldr ip, [ip, #+4007]
0xf69ace7c    e52dc004               str ip, [sp, #-4]!
        ;; StaticCall:12( print&lt;0&gt; v3)
0xf69ace80    ebfffffe               bl +0 ; 0xf69ace80
0xf69ace84    e28dd004               add sp, sp, #4
        ;; ParallelMove r0 &lt;- C
0xf69ace88    e59a0060               ldr r0, [thr, #+96]
        ;; Return:16(v0)
0xf69ace8c    e24bd000               sub sp, fp, #0
0xf69ace90    e8bd8800               ldmia sp!, `{`fp, pc`}`
0xf69ace94    e1200070               bkpt #0x0
`}`
```

上面打印的和快照里的有些不同，这样可以对照汇编看 IR 指令。

来我们挨个看：

```
;; Enter frame
0xf6a6ce60    e92d4800               stmdb sp!, `{`fp, lr`}`
0xf6a6ce64    e28db000               add fp, sp, #0
```

标准的函数序言，帧指针指向函数栈帧底部后，将调用者的帧指针、链接寄存器入栈。

标准 ARM 架构是递减栈，倒序增长。

```
;; CheckStackOverflow:8(stack=0, loop=0)
0xf6a6ce68    e59ac024               ldr ip, [thr, #+36]
0xf6a6ce6c    e15d000c               cmp sp, ip
0xf6a6ce70    9bfffffe               blls +0 ; 0xf6a6ce70
```

猜到了吧？检查栈溢出的常规套路。

自带反汇编器既不提供线程字段的注解，也不提供分支的注解，需要花点功夫。

字段偏移表可以在 `vm/compiler/runtime_offsets_extracted.h` 找到，`Thread_stack_limit_offset = 36` 表明线程栈可访问的字段个数限制在 36 个。

如果检测到栈溢出，调用 `stackOverflowStubWithoutFpuRegsStub` 处理。汇编中的分支不能打补丁，但可以观察二进制确认。

```
;; PushArgument(v3)
0xf6a6ce74    e285ca01               add ip, pp, #4096
0xf6a6ce78    e59ccfa7               ldr ip, [ip, #+4007]
0xf6a6ce7c    e52dc004               str ip, [sp, #-4]!
```

拿出对象池里的一个对象入栈，对象的偏移太大，ldr 处理不了，这里使用了基址寻址。

这个对象实际上是 `RawOneByteString` 类型的 “Hello, World!”，位于 isolate 偏移 8103 处的 `globalObjectPool` 中。

注意到这里的偏移没有对齐，这是因为对象指针都被 ``vm/pointer_tagging.h` 定义的 `kHeapObjectTag` 标记了，本例中所有的 `RawObject` 指针以 1 对齐。

```
;; StaticCall:12( print&lt;0&gt; v3)
0xf6a6ce80    ebfffffe               bl +0 ; 0xf6a6ce80
0xf6a6ce84    e28dd004               add sp, sp, #4
```

这里是字符串参数出栈之后的调用。

这里分支也没有解析，是 dart:core 中 `print` 函数的入口点。

```
;; ParallelMove r0 &lt;- C
0xf69ace88    e59a0060               ldr r0, [thr, #+96]
```

返回值是 Null，96 是 `Thread` 中 null 对象的偏移。

```
;; Return:16(v0)
0xf69ace8c    e24bd000               sub sp, fp, #0
0xf69ace90    e8bd8800               ldmia sp!, `{`fp, pc`}`
0xf69ace94    e1200070               bkpt #0x0
```

最后是函数结语，写回调用者保存的寄存器，恢复栈帧。lr 是最后入栈的，把它 pop 给 pc 后函数返回。

之后我会用自己实现的反汇编器的输出作为演示，比内置的反汇编器的问题少一点。

第二部分我会更深入地解析生成代码并以真实 Flutter 应用为例讲解，欢迎持续关注。

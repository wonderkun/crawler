> 原文链接: https://www.anquanke.com//post/id/233792 


# 通过重新编译Flutter引擎对Flutter应用程序进行逆向分析


                                阅读量   
                                **124402**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者tinyhack，文章来源：tinyhack.com
                                <br>原文地址：[https://tinyhack.com/2021/03/07/reversing-a-flutter-app-by-recompiling-flutter-engine/﻿](https://tinyhack.com/2021/03/07/reversing-a-flutter-app-by-recompiling-flutter-engine/%EF%BB%BF)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t011e45c5294a9b51a9.png)](https://p5.ssl.qhimg.com/t011e45c5294a9b51a9.png)



我们知道，要想对flutter应用程序的发布版本进行逆向分析是一件非常困难的事情，原因主要有两个，一是缺乏相应的工具，二是flutter引擎本身也经常发生变化。幸运的是，如果待逆向的flutter应用是用特定版本的Flutter SDK构建的，则可以借助于darter或Doldrums来转储该应用程序的类名和方法名。

如果您的运气足够好，就像我第一次测试Flutter App时那样，甚至根本就无需对App进行逆向工程。如果应用程序本身非常简单，并且使用简单的HTTPS连接，则可以使用拦截代理（如Burp或Zed Attack Proxy）来测试其全部功能。但是，这次需要测试的应用程序在HTTPS的基础上使用了额外的加密层，所以，我不得不对其进行逆向分析。

在这篇文章中，虽然只介绍了Android平台的例子，但这里介绍的方法都是通用的，也适用于其他平台。简单来说，我们的方法就是：不需要更新或创建快照解析器，而是只要重新编译flutter引擎，并将其替换到目标应用中即可。



## Flutter编译的应用程序

目前，我发现了一些有关Flutter逆向工程的文章和存储库：
- Reverse engineering Flutter for Android：讲解了快照格式的基本知识，介绍了Doldrums，截至目前只支持快照版本8ee4ef7a67df9845fba331734198a953。
- Reverse engineering Flutter apps (Part 1)：这是一篇非常棒的文章，它详细解释了Dart的内部结构，不幸的是，文章没有提供相应的代码。截至目前为止，该文章的续篇还没有发表。
- darter: Dart snapshot parser：这是一个转储快照版本c8562f0ee0ebc38ba217c7955956d1cb的工具。
我们知道，Flutter应用程序的代码主要由两个库组成，其中libflutter.so库存放的是flutter引擎，而libapp.so库则用于存放用户编写的代码。读者可能会问：如果用标准的反汇编器打开一个libapp.so（经过AOT编译的Dart代码），将会看到什么呢？只会看到本地代码，对吗？实际上，如果使用IDA打开这个库的话，最初看到的，只是一堆字节而已。

[![](https://p0.ssl.qhimg.com/t0166e9b7c1f505f0fc.png)](https://p0.ssl.qhimg.com/t0166e9b7c1f505f0fc.png)

如果使用其他工具，比如Binary Ninja，这些工具可能还会进行一些线性扫描，因此，我们会看到很多方法。但是，所有的方法都没有命名，我们也无法找到任何字符串引用。同时，libapp.so既不会引用外部函数（无论是libc还是其他库），也没有直接调用内核的syscall（比如Go）。

如果使用Darter dan Doldrums这样的工具，我们不仅可以转储类名和方法名，还可以找到函数的实现地址。下面是一个使用Doldrums进行转储的例子。这对逆向分析应用程序极为有用。同时，我们还可以使用Frida在这些地址处设置hook，以转储内存或方法参数。

[![](https://p5.ssl.qhimg.com/t01c14790bb157d57f1.png)](https://p5.ssl.qhimg.com/t01c14790bb157d57f1.png)



## 快照的格式问题

一个特定工具只能转储快照的特定版本的原因是：快照格式不稳定，它被设计成由特定版本的运行时来运行。对于某些格式来说，如果遇到未知或不受支持的部分，它们会直接放弃；相比之下，快照格式则显得“宽容的多”：如果无法解析某个部分，就会继续解析下一个部分。

快照的格式大体是这样的：`&lt;tag&gt;&lt;data bytes&gt;&lt;tag&gt;&lt;data bytes&gt;……`，就像您看到的那样，这里并没有为每个块显式地指定其长度，也没有为标记的头部指定特定格式（所以，我们无法通过模式匹配来找到块的起始部分）。一切都只是数字。除了源代码本身，再也找不到与快照相关的其他文档。

实际上，这种格式连一个版本号都没有：格式是由快照版本字符串进行标识的。版本字符串是通过对快照相关文件的源代码计算其哈希值而得到的。因此，如果文件发生变化，那么格式也会随之发生变化。这在大多数情况下都是正确的，但也并非总是如此（例如：如果您编辑一个注释，快照版本字符串就会改变）。

我的第一个想法就是通过查看Dart源代码的差异，将Doldrums或Darter修改为我需要的版本。但事实证明，事情远没有我想的这么简单：枚举有时会插入其中（意味着我需要将所有常量移一个数字）。并且，dart还使用C++模板进行了大量的位操作。例如，当我查看Doldums代码时，遇到了如下所示的内容：

```
def decodeTypeBits(value):
       return value &amp;amp; 0x7f
```

我想我可以在代码中快速检查这个常量（无论它在新版本中是否改变），结果发现其类型并不是整数：

```
class ObjectPool : public Object `{`
 using TypeBits = compiler::ObjectPoolBuilderEntry::TypeBits;
`}`
struct ObjectPoolBuilderEntry `{`
  using TypeBits = BitField&lt;uint8_t, EntryType, 0, 7&gt;;
`}`
```

不难看出，这个Bitfield是作为BitField模板类来实现的。这个特殊的位很容易读懂，但是如果想搞清楚kNextBit，则需要回溯之前所有的位定义。我知道对于经验丰富的C++开发者来说，这并非难事，但要想跟踪这些版本之间的变化，还是需要做大量的手工检查的。

我理想中的情况是：无需维护Python代码，下一次更新应用程序需要进行重新测试时，直接使用更新版本的Flutter SDK，并使用另一个快照版本。但是，我面前的事实却是，需要测试两个使用不同的Flutter版本的应用程序：一个是已经在应用商店发布的应用程序，另一个是即将发布的应用程序。



## 重新构建Flutter引擎

flutter引擎（libflutter.so）是一个独立于libapp.so（主应用逻辑代码）的库，在iOS系统中，这是一个独立的框架。这个库的思路非常简单：
- 下载我们想要的引擎版本；
- 通过改造该引擎，用于打印类名、方法等，而不是编写我们自己的快照解析器；
- 用我们的补丁版本替换原来的libflutter.so库；
- 乐享其成。
实际上，第一步就不是一件轻松的事情：如何才能找到相应的快照版本？虽然darter的这张表可以提供帮助，但是该表并非最新的版本。对于其他版本，我们需要自己寻找并测试它是否有匹配的快照号。关于Flutter引擎的重新编译方法，可以参考这篇资料；需要注意的是，编译过程中可能会出现一些小插曲，为此，我们需要修改快照版本的python脚本。注意，Dart内部的运行机制，就不是那么容易理解和处理了。

我测试过的大部分旧版本都不能正确编译，为此，我们需要编辑DEPS文件。在我的例子中：虽然其差别很小，但借助于网络搜索后，我才找到了这一点。不知何故，相关的提交并不可用，因此，我不得不使用不同的版本。注意：不要盲目应用这个补丁，首先要检查以下两点：
- 如果某个提交不可用，请查找离发布日期最近的提交；
- 如果某些代码引用了_Internal，则应删除_Internal部分。
```
diff --git a/DEPS b/DEPS
index e173af55a..54ee961ec 100644
--- a/DEPS
+++ b/DEPS
@@ -196,7 +196,7 @@ deps = `{`
    Var('dart_git') + '/dartdoc.git@b039e21a7226b61ca2de7bd6c7a07fc77d4f64a9',

   'src/third_party/dart/third_party/pkg/ffi':
-   Var('dart_git') + '/ffi.git@454ab0f9ea6bd06942a983238d8a6818b1357edb',
+   Var('dart_git') + '/ffi.git@5a3b3f64b30c3eaf293a06ddd967f86fd60cb0f6',

   'src/third_party/dart/third_party/pkg/fixnum':
    Var('dart_git') + '/fixnum.git@16d3890c6dc82ca629659da1934e412292508bba',
@@ -468,7 +468,7 @@ deps = `{`
   'src/third_party/android_tools/sdk/licenses': `{`
      'packages': [
        `{`
-        'package': 'flutter_internal/android/sdk/licenses',
+        'package': 'flutter/android/sdk/licenses',
         'version': 'latest',
        `}`
      ],
```

现在，我们就可以开始编辑快照文件，以了解其工作原理了。但是，正如前面提到的：如果我们修改了快照文件，那么，该快照的哈希值就会发生改变，所以，我们需要在`third_party/dart/tools/make_version.py`中返回一个静态版本号来解决这个问题。对于VM_SNAPSHOT_FILES中的任何一个文件，都需要用静态字符串将`snapshot_hash = MakeSnapshotHashString()`这一行改为您的特定版本。

[![](https://p3.ssl.qhimg.com/t019fec0ce0c9a30943.png)](https://p3.ssl.qhimg.com/t019fec0ce0c9a30943.png)

如果我们不给版本打补丁的话，结果又会怎么样呢？应用程序将无法启动。所以，在使用OS::PrintErr(“Hello World”)打上补丁并进行重新编译后，我们就可以替换.so文件，然后运行它了。

虽然我进行了多次实验（比如尝试FORCE_INCLUDE_DISASSEMBLER），但是仍然没有找到完美的修改方法，不过，我还是可以分享一些修改建议的。
- 在`runtime/vm/clustered_snapshot.cc`中，我们可以修改`Deserializer::ReadProgramSnapshot(ObjectStore* object_store)`，使其打印类表，即`isolate-&gt;class_table()-&gt;Print()`；
- 在`runtime/vm/class_table.cc`中，我们可以修改`void ClassTable::Print()`，使其打印更多的信息。
例如，打印函数名称的代码如下所示：

```
const Array&amp;amp; funcs = Array::Handle(cls.functions());  
 for (intptr_t j = 0; j &lt; funcs.Length(); j++) `{`
      Function&amp;amp; func = Function::Handle();
      func = cls.FunctionFromIndex(j);
      OS::PrintErr("Function: %s", func.ToCString());
`}`
```



## 关于SSL证书

Flutter应用程序的另一个问题是：它并不信任用户安装的根证书。这对于渗透测试来说就是一个问题了，不过，我们可以通过给二进制文件打补丁（直接或使用Frida）来解决这个问题，相关的文章请访问这里，具体方法如下所示：
- Flutter使用的是Dart，但是Dart并没有使用系统的CA Store；
- Dart使用的CA列表被编译到应用程序中；
- Dart在安卓系统上不支持代理，所以使用了ProxyDroid与iptables；
- 钩住x509.cc中的session_verify_cert_chain函数，以禁用链式验证。
通过重新编译Flutter引擎，可以很容易地实现这一点：我们只需修改源代码（third_party/boringssl/src/ssl/handshake.cc），而不需要在编译后的代码中寻找汇编字节模式了。



## 对Flutter进行混淆处理

使用这里提供的方法，可以对Flutter/Dart应用程序进行相应的混淆处理，从而提高逆向分析的难度。请注意，这里只是对名称进行混淆处理，而没有对控制流进行混淆处理。



## 小结

由于我这个人很懒，所以，我在这里选择了重新编译flutter引擎，而不是编写一个合适的快照解析器。当然，其他人在对其他技术进行逆向分析时，也可以借鉴类似的方法，即黑掉运行时引擎，例如，要对一个经过混淆处理的PHP脚本进行逆向分析时，可以用PHP模块钩住eval函数。

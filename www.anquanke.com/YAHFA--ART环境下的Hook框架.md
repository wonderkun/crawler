> 原文链接: https://www.anquanke.com//post/id/96231 


# YAHFA--ART环境下的Hook框架


                                阅读量   
                                **122804**
                            
                        |
                        
                                                                                    



> 在Android Dalvik时代，最流行的Hook框架非Xposed莫属了。各种功能强大的Xposed插件极大地丰富了Android的可玩性，而对于安全研究人员来说，hook则是应用逆向工作中的一项非常有效的手段。
但是，进入到ART时代后，情况逐渐发生了变化。Xposed框架对系统进行了较大的改动，因此其安装适配难度显著提高；另一方面，随着近年来热修复技术的兴起，各大国内厂商也纷纷推出了自己的hook工具。但是，在实际试用过程中，我发现许多工具并不太适用于逆向分析。为此，在研究学习了ART方法调用机制和主要hook框架的基本原理后，我设计实现了一套新的ART环境hook框架：YAHFA(Yet Another Hook Framework for ART)。

本文将对YAHFA的工作原理进行介绍。

## 

## 背景知识

首先，我们对ART环境下方法的调用进行基本的介绍。如无特殊说明，以下内容均针对Android 6.0(API 23)，架构x86。在ART环境下，每个方法对应于一个ArtMethod结构体。这个结构体包含的字段如下：

```
class ArtMethod `{`
 // Field order required by test "ValidateFieldOrderOfJavaCppUnionClasses". 
 // The class we are a part of. 
 GcRoot&lt;mirror::Class&gt; declaring_class_; 
 // Short cuts to declaring_class_-&gt;dex_cache_ member for fast compiled code access. 
 GcRoot&lt;mirror::PointerArray&gt; dex_cache_resolved_methods_;
 
 // Short cuts to declaring_class_-&gt;dex_cache_ member for fast compiled code access. 
 GcRoot&lt;mirror::ObjectArray&lt;mirror::Class&gt;&gt; dex_cache_resolved_types_;
 
 // Access flags; low 16 bits are defined by spec. 
 uint32_t access_flags_;
 
 /* Dex file fields. The defining dex file is available via declaring_class_-&gt;dex_cache_ */ 
 // Offset to the CodeItem. 
 uint32_t dex_code_item_offset_;
 
 // Index into method_ids of the dex file associated with this method. 
 uint32_t dex_method_index_;
 
 /* End of dex file fields. */ 
 // Entry within a dispatch table for this method. For static/direct methods the index is into 
 // the declaringClass.directMethods, for virtual methods the vtable and for interface methods the ifTable. 
 uint32_t method_index_;
 
 // Fake padding field gets inserted here. 
 // Must be the last fields in the method. 
 // PACKED(4) is necessary for the correctness of 
 // RoundUp(OFFSETOF_MEMBER(ArtMethod, ptr_sized_fields_), pointer_size). 
 struct PACKED(4) PtrSizedFields `{`
 
 // Method dispatch from the interpreter invokes this pointer which may cause a bridge into compiled code. 
 void* entry_point_from_interpreter_;
 
 // Pointer to JNI function registered to this method, or a function to resolve the JNI function. 
 void* entry_point_from_jni_;
 
 // Method dispatch from quick compiled code invokes this pointer which may cause bridging into the interpreter. 
 void* entry_point_from_quick_compiled_code_;
 `}` ptr_sized_fields_;
`}`
```

根据用途，这些字段大致可分为三类：入口点，方法信息和解析缓存信息。

#### 

## 入口点

ArtMethod结构体末尾处的entry_point_from_*，是不同条件下方法执行的入口点。entry_point_from_jni_通常没有用到，所以可以用来保存其他信息 。我们最关心的是entry_point_from_quick_compiled_code_ 。

例如，我们有如下java代码：

```
Log.e("tag", "msg");
```

编译为dalvik字节码，对应如下：

```
invoke-static `{`v0, v1`}`, Landroid/util/Log;.e:(Ljava/lang/String;Ljava/lang/String;)I // method@0000
```

而经过dex2oat，将其编译为机器码，则得到如下内容：

```
//
mov    0x10(%esp),%ecx ; 设置第1个参数
mov    0x14(%esp),%edx ; 设置第2个参数
mov    (%esp),%eax ; 栈顶保存了当前方法ArtMethod结构体的地址
mov    0x4(%eax),%eax ; 获取当前方法的dex_cache_resolved_methods_(偏移为4)
mov    0xc(%eax),%eax ; 获取dex_cache_resolved_methods_中的第一项，即method index为0的方法Log.e，后面会介绍
call   *0x24(%eax) ; 调用Log.e的entry_point_from_quick_compiled_code_(偏移为36)
```

上述汇编代码中，我们布置完成栈和寄存器，通过dex_cache_resolved_methods_(后面会介绍)获取到要调用的方法，即callee，然后便直接跳转到callee的entry_point_from_quick_compiled_code_。结合Android源码中的注释可知，在caller调用callee之前，caller需要进行以下准备工作：
- 栈顶保存caller的`ArtMethod`地址
<li>将参数依次保存在寄存器`ecx`, `edx`, `ebx`
</li>
- 如果有其他参数，将其依次保存在栈上
<li>将callee的`ArtMethod`地址保存在`eax`
</li>
需要注意的是，以上介绍的是直接调用方法的情况，即在ART中caller调用callee。而通过反射方式调用方法，即Method.invoke()，则相当于从ART外部进入ART中，此时就需要首先调用art_quick_invoke_stub，进行准备工作（比如通过`memcpy`，将传入的参数按照calling convention复制到栈上），随后才能跳转到entry_point_from_quick_compiled_code_。所以，比起直接调用方法，通过反射调用会带来额外的开销。

到目前为止，我们了解了调用方法前的准备。那么，在进入entry_point_from_quick_compiled_code_后，又发生了什么呢？有些方法的entry_point_from_quick_compiled_code_指向的便是经编译后方法的机器码；但有些方法在调用时尚未解析（如静态方法等），这些方法的entry_point_from_quick_compiled_code_通常指向的是一段用于解析方法的指令：art_quick_resolution_trampoline，当解析完成后，会将entry_point_from_quick_compiled_code_更新为实际的机器码地址。接下来我们便介绍方法解析的相关内容。

#### 

## 方法信息

`ArtMethod`中除了入口地址，还包括该方法本身的一些信息，例如方法所属于的类declaring_class_、在所属类中的方法编号method_index_，以及对应于原始dex文件的信息dex_code_item_offset_, dex_method_index_等。

那么，什么时候需要这些信息呢？从目前看到的代码来看，在解析方法会被使用。例如，在函数`artQuickResolutionTrampoline`中，有如下代码：

```
uint32_t dex_pc = caller-&gt;ToDexPc(QuickArgumentVisitor::GetCallingPc(sp));
const DexFile::CodeItem* code;
called_method.dex_file = caller-&gt;GetDexFile();
code = caller-&gt;GetCodeItem();
CHECK_LT(dex_pc, code-&gt;insns_size_in_code_units_);
const Instruction* instr = Instruction::At(&amp;code-&gt;insns_[dex_pc]);
Instruction::Code instr_code = instr-&gt;Opcode();
```

这里，我们需要解析的是callee的机器码地址，具体操作则是从caller下手。回忆之前提到的calling convention，我们知道caller会将自己的`ArtMethod`结构体保存在栈上。从栈上得到该结构体后，通过其dex_code_item_offset_ 等dex相应信息，便可以回溯dalvik代码，找到caller调用callee的那一条dalvik字节码，从而获取调用方式和callee的dex method index。有了这些信息，便可通过ClassLinker的ResolveMethod完成方法解析。

另一方面，通过反射获取方法时，也需要这些信息。一般地，通过反射获取方法，采取的是如下操作：
- 获取到类的结构体
- 获取这个类的方法数组，数组的每项对应于各方法的ArtMethod地址，方法在数组中的编号就保存在method_index_字段中
- 遍历数组，对每个方法，检查其名称和签名是否匹配
但是，ArtMethod本身并不包含方法的名称、签名等信息，这些信息仍然保留在dex中。所以，需要从`dex_method_index_`获取到方法在dex中的index，进而通过declaring_class_所对应的dex获取这个方法的名称和签名信息。

由上可知，ArtMethod结构体中的这些信息也是很重要的，如果随意修改，则会发生NoSuchMethodError等问题。

#### 

## 解析缓存信息

最后，我们来看ArtMethod结构体中尚未介绍的字段：dex_cache_resolved_methods_和dex_cache_resolved_types_。

dex_cache_resolved_methods_是一个指针数组，保存的是ArtMethod结构指针。回忆上文方法调用所对应的机器码，我们知道caller就是在dex_cache_resolved_methods_中找到callee的。顾名思义，这个数组用于缓存解析的方法。

具体地，在dex文件加载时，数组dex_cache_resolved_methods_被初始化。此时，其保存的指针全部指向同一个ArtMethod。在文件dex_cache.cc中可看到如下代码：

```
if (runtime-&gt;HasResolutionMethod()) `{`
    // Initialize the resolve methods array to contain trampolines for resolution.

    Fixup(runtime-&gt;GetResolutionMethod(), pointer_size);
  `}`
`}`

void DexCache::Fixup(ArtMethod* trampoline, size_t pointer_size) `{`
  // Fixup the resolve methods array to contain trampoline for resolution.
  CHECK(trampoline != nullptr);
  CHECK(trampoline-&gt;IsRuntimeMethod());
  auto* resolved_methods = GetResolvedMethods();
  for (size_t i = 0, length = resolved_methods-&gt;GetLength(); i &lt; length; i++) `{`
    if (resolved_methods-&gt;GetElementPtrSize&lt;ArtMethod*&gt;(i, pointer_size) == nullptr) `{`
      resolved_methods-&gt;SetElementPtrSize(i, trampoline, pointer_size);
    `}`
  `}`
`}`
```

这个被指向的ArtMethod是runtime的resolution_method_，其作用便是解析得到方法的实际ArtMethod。当callee第一次被调用时，由数组dex_cache_resolved_methods_获取并执行的是resolution_method_。待解析完成，得到callee的实际ArtMethod后，再去执行实际的代码；此外，还会将解析得到的ArtMethod填充到数组dex_cache_resolved_methods_的相应位置。这样，之后callee再被调用时，便无需再次进行方法解析。

这种方式与ELF的got.plt极为相似，如果研究过ELF的方法调用机制，应该对这里的dex_cache_resolved_methods_不会感到陌生。

## 

## 主流hook框架

在介绍YAHFA之前，有必要对目前ART环境下主要的hook框架进行一个简要的介绍

### Xposed

相比其他框架，Xposed的代码量相当大，这主要是因为为了适配ART环境，Xposed[重新实现了libart.so等重要系统库](https://github.com/rovo89/android_art)。

具体地，Xposed是替换了方法的入口点entry_point_from_quick_compiled_code_，并将原方法等信息备份在entry_point_from_jni_中。替换后的入口点 ，会重新准备栈和寄存器，执行方法artQuickProxyInvokeHandler，并最终进入InvokeXposedHandleHookedMethod，完成hook的执行。

### AndFix

AndFix的替换思路很简单：找到目标方法后，将其`ArtMethod`结构体的内容全部替换成为hook的内容：

```
void replace_6_0(JNIEnv* env, jobject src, jobject dest) `{`
    art::mirror::ArtMethod* smeth =
            (art::mirror::ArtMethod*) env-&gt;FromReflectedMethod(src);
    art::mirror::ArtMethod* dmeth =
            (art::mirror::ArtMethod*) env-&gt;FromReflectedMethod(dest);

    reinterpret_cast&lt;art::mirror::Class*&gt;(dmeth-&gt;declaring_class_)-&gt;class_loader_ =
    reinterpret_cast&lt;art::mirror::Class*&gt;(smeth-&gt;declaring_class_)-&gt;class_loader_; //for plugin classloader
    reinterpret_cast&lt;art::mirror::Class*&gt;(dmeth-&gt;declaring_class_)-&gt;clinit_thread_id_ =
    reinterpret_cast&lt;art::mirror::Class*&gt;(smeth-&gt;declaring_class_)-&gt;clinit_thread_id_;
    reinterpret_cast&lt;art::mirror::Class*&gt;(dmeth-&gt;declaring_class_)-&gt;status_ = reinterpret_cast&lt;art::mirror::Class*&gt;(smeth-&gt;declaring_class_)-&gt;status_-1;
    //for reflection invoke

    reinterpret_cast&lt;art::mirror::Class*&gt;(dmeth-&gt;declaring_class_)-&gt;super_class_ = 0;

    smeth-&gt;declaring_class_ = dmeth-&gt;declaring_class_;
    smeth-&gt;dex_cache_resolved_methods_ = dmeth-&gt;dex_cache_resolved_methods_;
    smeth-&gt;dex_cache_resolved_types_ = dmeth-&gt;dex_cache_resolved_types_;
    smeth-&gt;access_flags_ = dmeth-&gt;access_flags_ | 0x0001;
    smeth-&gt;dex_code_item_offset_ = dmeth-&gt;dex_code_item_offset_;
    smeth-&gt;dex_method_index_ = dmeth-&gt;dex_method_index_;
    smeth-&gt;method_index_ = dmeth-&gt;method_index_;
    
    smeth-&gt;ptr_sized_fields_.entry_point_from_interpreter_ =
    dmeth-&gt;ptr_sized_fields_.entry_point_from_interpreter_;
    
    smeth-&gt;ptr_sized_fields_.entry_point_from_jni_ =
    dmeth-&gt;ptr_sized_fields_.entry_point_from_jni_;
    smeth-&gt;ptr_sized_fields_.entry_point_from_quick_compiled_code_ =
    dmeth-&gt;ptr_sized_fields_.entry_point_from_quick_compiled_code_;
    
    LOGD("replace_6_0: %d , %d",
         smeth-&gt;ptr_sized_fields_.entry_point_from_quick_compiled_code_,
         dmeth-&gt;ptr_sized_fields_.entry_point_from_quick_compiled_code_);
`}`
```

这样做存在两点问题：
- 原方法的信息全部被替换，所以无法再执行原方法了。在逆向分析时，我们有时并不是要完全替换原方法，而是类似于插桩等措施，获取方法执行过程中的一些关键的信息，所以必须要对原方法进行备份以执行。
- 原方法所属的对应dex信息也被替换了。如前文所述，这些信息在通过反射机制获取方法时会被使用，所以原方法和hook方法的名称、签名必须完全一致。对于热修复来说，这点也许影响不大，但对于逆向分析则略显不便。此外，由于这些信息在解析方法时会被使用，所以有时也会发生NoSuchMethodError的问题。
### Legend

Legend和AndFix基本上采取的是完全一样的手段，即直接将目标方法的`ArtMethod`结构体内容全部替换：

```
artOrigin.setEntryPointFromQuickCompiledCode(hookPointFromQuickCompiledCode);
artOrigin.setEntryPointFromInterpreter(hookEntryPointFromInterpreter);
artOrigin.setDeclaringClass(hookDeclaringClass);
artOrigin.setDexCacheResolvedMethods(hookDexCacheResolvedMethods);
artOrigin.setDexCacheResolvedTypes(hookDexCacheResolvedTypes);
artOrigin.setDexCodeItemOffset((int) hookDexCodeItemOffset);
artOrigin.setDexMethodIndex((int) hookDexMethodIndex);
```

与AndFix不同的是，Legend在替换前，对原方法进行了备份保存。随后就可以通过调用这个备份方法来执行原方法。不过，这种执行原方法的手段，带来的额外开销比较大：
- 首先需要通过在map中查找的方式动态获取原方法的备份，即备份方法的结构体必须在运行时动态获取
- 随后再通过反射机制Method.invoke()来执行，如前文所述，需要再次通过`art_quick_invoke_stub`准备调用环境，重新进入ART。
此外，与AndFix一样，由于`ArtMethod`的内容全部被替换，所以如果原方法是通过反射调用的，那么hook方法必须具有相同的方法名和签名；另外，对于静态方法这类可能在调用时解析的方法，有时也会出现问题。

### 其他

上述介绍的hook框架，包括将要介绍的YAHFA，都属于”Native派”，其本质是修改`ArtMethod`结构体的内容；而其他hook框架，如Tinker, Nuwa等大都是”Java派”，例如修改DexPathList等手段。由于Java派实现方式与Native派完全不同，这里就不再介绍了。

关于Native派和Java派，可参考[这篇文章](https://github.com/WeMobileDev/article/blob/master/ART%E4%B8%8B%E7%9A%84%E6%96%B9%E6%B3%95%E5%86%85%E8%81%94%E7%AD%96%E7%95%A5%E5%8F%8A%E5%85%B6%E5%AF%B9Android%E7%83%AD%E4%BF%AE%E5%A4%8D%E6%96%B9%E6%A1%88%E7%9A%84%E5%BD%B1%E5%93%8D%E5%88%86%E6%9E%90.md)的介绍。



## YAHFA工作原理

### 方法替换

作为Native派的一员，YAHFA也是通过修改目标方法的`ArtMethod`结构体内容，来实现执行流程的变更。更具体地，是与Xposed相似，修改了entry_point_from_quick_compiled_code_和entry_point_from_jni_字段。

再次回忆方法调用的calling convention，我们发现，调用原方法和调用hook方法，两者唯一不同点就是callee。也就是说，如果我们将保存callee的`eax`替换成为hook方法的`ArtMethod`，同时保持栈结构和其他寄存器的内容不变，再跳转到hook方法的entry_point_from_quick_compiled_code_，就实现了调用hook方法。

由此启发，我们将hook方法的`ArtMethod`地址保存在原方法的entry_point_from_jni_，并修改原方法的entry_point_from_quick_compiled_code_，使其指向一段辅助代码，在这里完成`eax`的设置和跳转：

```
mov 32(%eax), %eax ; 将eax设置为entry_point_from_jni_(偏移为32)的内容
push 36(%eax) ; entry_point_from_quick_compiled_code_在偏移为36处
ret ; 跳转到hook方法的entry_point_from_quick_compiled_code_
```

通过这三条简单的指令，便完成了从原方法到hook方法的跳转。相比Xposed更为简洁，可以直接进入hook方法的入口而无需再准备调用环境；相比AndFix和Legend，由于未修改原方法的其他字段，即使hook和原方法的方法名不同，在解析和查找时也不会出现NoSuchMethodError了。

#### 

## 原方法调用

为了能够在hook方法中调用原方法，我们必须要在修改原方法之前，对其进行备份。Legend在调用原方法时，是通过反射调用备份的方法，其开销相对比较大。那么如何能够减少这些额外的开销呢？

假设在hook方法中有这样一段调用：

```
origin("Hooked", msg);
```

那么如果我们在这里也做一次”hook”，将方法`origin`替换为我们要执行的原方法，那么hook方法在执行到这里时，实际调用的不就是我们的原方法了么？由于这里是直接调用而非反射，我们减少了开销，而且可以采用Legend与AndFix那种方式进行hook，即将`origin`的`ArtMethod`全部替换为原方法的`ArtMethod`。某种意义上讲，这里的`origin`其实是一个placeholder，它的实现可以为空，完全不用考虑，因为最终它会被替换成原方法。

当然，为了控制传入的参数，我们的hook方法和`origin`方法都是静态方法。另外，由于采取了完全替换`ArtMethod`进行原方法的备份，需要首先保证`origin`方法已经解析完成。我们在备份之前，手工更新dex_cache_resolved_methods_数组对应项，确保hook在调用`origin`时无需再进行方法解析。

#### 

## 再论hook

前面讲了这么多，那么究竟什么是hook？hook是做什么的？可能不同人会有不同的侧重点，但从本质上来讲，hook就是在运行时，动态改变原有的执行流程。

然而，要做到hook，就必须存在一个注入代码的窗口。这可以大致分为以下两类：
- 应用自带一个这样的窗口，可以接收外部提供的代码，这便是热修复所使用的。通常来说，热修复框架都需要应用在初始化时加载补丁代码。由于窗口是应用自带的，我们并不需要root权限
- 应用本身并没有这样的窗口，或者我们并不知道是否有这样的窗口，这便是逆向分析时经常遇到的。Xposed的解决方式，是替换系统库，为所有应用添加了一个加载外部代码的窗口，而这就必须有root权限
YAHFA作为一个hook框架，其实际上就是实现了这样一个窗口，可以加载外部代码并替换原有执行流程。如果是用于热修复，那么与其他hook框架类似；如果是在逆向分析时使用，那么还需要通过其他手段将这个窗口添加到应用中，YAHFA本身并不像Xposed那样是具有这种能力的。

设计YAHFA的出发点，是为了便于安全研究和逆向分析，热修复并不是其主要目的。所以，YAHFA并没有过多地考虑稳定性和适配，目前完成了Android 5.1和6.0的测试，包括主要的架构(x86和armeabi)。



## 总结

YAHFA的代码可见****[这里](https://github.com/rk700/YAHFA)****。其主要功能是通过C实现，主要是作为思路验证和PoC，因此还有不完善之处。Repo中还包含了一个demoApp用于示例，如果有问题欢迎提issue。



## 参考资料
- [https://github.com/asLody/Legend](https://github.com/asLody/Legend)
- [https://github.com/alibaba/AndFix](https://github.com/alibaba/AndFix)
- [https://github.com/rovo89/android_art](https://github.com/rovo89/android_art)
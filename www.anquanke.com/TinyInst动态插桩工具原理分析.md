> 原文链接: https://www.anquanke.com//post/id/234925 


# TinyInst动态插桩工具原理分析


                                阅读量   
                                **133506**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p0.ssl.qhimg.com/t012c8f5b1211421811.jpg)](https://p0.ssl.qhimg.com/t012c8f5b1211421811.jpg)



作者：[houjingyi](https://twitter.com/hjy79425575)

## 前言

这篇文章主要是分析一下project zero大佬开源的一个插桩的库TinyInst：<br>[https://github.com/googleprojectzero/TinyInst](https://github.com/googleprojectzero/TinyInst)<br>
同时大佬也开源了基于该库的fuzzer：<br>[https://github.com/googleprojectzero/Jackalope](https://github.com/googleprojectzero/Jackalope)<br>
TinyInst和Jackalope都支持Windows和macOS。不过只支持Intel平台，因为具体实现依赖于Intel的xed解码/编码器。<br>
也有人把这个和WinAFL结合的：<br>[https://github.com/linhlhq/TinyAFL](https://github.com/linhlhq/TinyAFL)

看他们twitter都用基于TinyInst的fuzzer挖到了一些Windows和macOS上的漏洞，看来还是值得学习这里面插桩的原理的。

TinyInst中litecov类继承自TinyInst类，而TinyInst类继承自Debugger类。这就是最关键的三个类了。下面我们以Windows环境为例进行分析。<br>
在下面这张我画的流程图中，黑色的是Debugger类中实现的函数，黄色的是TinyInst类中实现的函数，红色的是litecov类中实现的函数。看上去很复杂，实际上这里面的代码逻辑还是比较清楚的。比如OnProcessExit在Debugger类中是一个虚方法，在TinyInst类和litecov类中才有具体的实现，对于这样的情况为了简化在图中就没有黑色的OnProcessExit了。

[![](https://p4.ssl.qhimg.com/t0161401c9902c0c2bc.png)](https://p4.ssl.qhimg.com/t0161401c9902c0c2bc.png)

我们接下来分析的顺序也是debugger.cpp-tinyinst.cpp-litecov.cpp，每分析一个新类之前都会先简单介绍一下整体的功能，然后会详细解释流程图中涉及到的函数。当然并不是每个函数都画在流程图里面了，只挑了一些关键的函数。所以阅读文章时最好还是自己调试阅读源代码。



## debugger.cpp

我们先看流程图中黑色的函数。熟悉Windows系统调试相关知识的话应该很快能明白，就是实现了一个简单的调试器。创建进程之后在DebugLoop中根据不同的调试事件进行不同的处理。在目标方法地址处设置一个断点，程序运行到目标方法时触发这个断点产生异常被调试器捕获，此时保存参数和返回地址，修改返回地址使得目标方法返回时产生一个异常又被调试器捕获，此时恢复参数和返回地址，恢复之前设置的断点，以此循环。<br>
下面是图中函数的注释。

**Debugger::OnModuleLoaded**<br>
当模块被加载时会调用该函数，如果指定了target_module和target_method/target_offset并且这个module就是target_module那么获取目标方法的地址并在该地址添加BREAKPOINT_TARGET类型的断点<br>**Debugger::HandleTargetReachedInternal**<br>
当到达目标方法时会调用该函数，保存参数和返回地址，并将返回地址修改为PERSIST_END_EXCEPTION，当目标方法结束时会产生一个异常<br>**Debugger::HandleTargetEnded**<br>
当目标方法返回时会调用该函数，恢复参数和返回地址，恢复在目标方法的地址处添加的BREAKPOINT_TARGET类型的断点<br>**Debugger::OnEntrypoint**<br>
当到达程序入口点时会调用该函数，对所有加载的模块都调用Debugger::OnModuleLoaded，并将child_entrypoint_reached标记为true<br>**Debugger::HandleDebuggerBreakpoint**<br>
当遇到断点的时候会调用该函数，首先从断点列表breakpoints中删除该断点，然后恢复断点处原来的值和指令地址寄存器，根据断点的类型BREAKPOINT_ENTRYPOINT或BREAKPOINT_TARGET调用OnEntrypoint或HandleTargetReachedInternal，返回断点类型<br>**Debugger::HandleDllLoadInternal**<br>
当模块被加载时会调用该函数，如果child_entrypoint_reached为true调用Debugger::OnModuleLoad<br>**Debugger::OnProcessCreated**<br>
如果是附加到一个进程的情况那么直接对主模块调用Debugger::OnModuleLoaded，否则在模块的入口点添加一个BREAKPOINT_ENTRYPOINT类型的断点<br>**Debugger::HandleExceptionInternal**<br>
处理EXCEPTION_DEBUG_EVENT调试事件。<br>
对于断点的情况调用Debugger:: HandleDebuggerBreakpoint函数，返回DEBUGGER_TARGET_START或者DEBUGGER_CONTINUE；<br>
对于 ACCESS_VIOLATION的情况如果指定了target_module和target_method/target_offset并且ExceptionAddress是PERSIST_END_EXCEPTION说明这是目标方法返回产生的异常，调用Debugger::HandleTargetEnded函数，返回DEBUGGER_TARGET_END；<br>
对于其它情况返回DEBUGGER_CRASHED<br>**Debugger::DebugLoop**<br>
循环，根据不同的调试事件进行不同的处理



## tinyinst.cpp

接下来我们来看流程图中黄色的函数，这里涉及到的就是插桩具体的一些实现。<br>
总的来说，加载要插桩的模块后：<br>
1.模块中的所有可执行区域都被标记为不可执行，同时保留了其他权限(读/写)。这会导致每当控制流到达模块时都会产生异常并被调试器捕获并处理。<br>
2.在原始模块地址范围的2GB之内分配了一个可执行的内存区域放置已插桩的模块代码。将所有以[rip+offset]形式寻址的指令替换为[rip+fixed_offset]。<br>
无论何时进入被插桩的模块都会插桩被命中的基本块(TinyInst::TranslateBasicBlock)，以及可以通过递归遵循条件分支以及直接调用和跳转到达的所有基本块(TinyInst::TranslateBasicBlockRecursive)。<br>
对于直接调用/跳转：都会访问已插桩代码中的正确位置<br>
对于间接调用/跳转：都会访问其原始代码位置，这将导致异常，调试器会rip替换为插桩代码中的相应位置(TinyInst::TryExecuteInstrumented)<br>
目标位于已插桩模块中的每个间接调用/跳转上都会引起异常。由于异常处理的速度很慢，因此具有很多间接调用/跳转的目标(例如C++中的虚方法，函数指针)将很慢。<br>
TinyInst中支持两种转换间接调用/跳转的方法：<br>
1.本地列表<br>
(TinyInst::InstrumentLocalIndirect)<br>
2.全局hash表(默认)<br>
(TinyInst::InitGlobalJumptable、TinyInst::InstrumentGlobalIndirect)<br>
不管是本地列表还是全局hash表，原理都是让间接调用/跳转去跳转到一个列表的开头。列表每一项都包含一对(original_target，translation_target)。测试跳转/调用目标是否与original_target相匹配，如果匹配，控制流将转到translation_target。否则跳到下一项。如果到达列表的末尾，则意味着之前没有看到调用/跳转的目标。这将导致调试器捕获到一个断点(TinyInst::HandleBreakpoint)，此时会创建一个新项并将其插入列表中(TinyInst::AddTranslatedJump)。<br>
使用本地列表的情况：<br>
插桩间接调用/跳转指令之后：

[![](https://p0.ssl.qhimg.com/t01ceb66a9ad7265e90.png)](https://p0.ssl.qhimg.com/t01ceb66a9ad7265e90.png)

调试器捕获到一个断点向列表中加入一个新项：

[![](https://p5.ssl.qhimg.com/t019549814659369664.png)](https://p5.ssl.qhimg.com/t019549814659369664.png)

使用全局hash表的情况：<br>
插桩间接调用/跳转指令之后：

[![](https://p0.ssl.qhimg.com/t017478e79a4e2279b1.png)](https://p0.ssl.qhimg.com/t017478e79a4e2279b1.png)

调试器捕获到一个断点向列表中加入一个新项：

[![](https://p3.ssl.qhimg.com/t0159aa2037286847f1.png)](https://p3.ssl.qhimg.com/t0159aa2037286847f1.png)

下面几个变量单独说一下：

```
size_t instrumented_code_size;
//插桩区域总大小
size_t instrumented_code_allocated;
//已经占用的大小
char *instrumented_code_local;
//指向调试进程插桩区域起始位置的指针
char *instrumented_code_remote;
//指向目标进程插桩区域起始位置的指针
```

比如我们用github上给出的示例程序对notepad.exe进行插桩：<br>`litecov.exe -instrument_module notepad.exe -coverage_file coverage.txt -- notepad.exe`<br>
这里调试进程就是指的litecov.exe，目标进程就是指的notepad.exe。插桩的代码是先写到litecov.exe的地址空间(TinyInst::WriteCode)再写到notepad.exe的地址空间(TinyInst::CommitCode)的。<br>
下面是图中函数的注释。

**TinyInst::InitGlobalJumptable**<br>
大小为JUMPTABLE_SIZE的数组，其中每项最初都指向一个断点。当检测到新的间接调用/跳转时将触发断点，然后会在此哈希表中添加新项<br>**TinyInst::HandleBreakpoint**<br>
调用TinyInst::HandleIndirectJMPBreakpoint<br>**TinyInst::HandleIndirectJMPBreakpoint**<br>
该地址如果指向TinyInst::InitGlobalJumptable中添加的断点说明是全局跳转；如果能在br_indirect_newtarget_list中找到说明是本地跳转。调用TinyInst::AddTranslatedJump并从 TinyInst::AddTranslatedJump创建的代码处开始执行<br>**TinyInst::AddTranslatedJump**<br>
向列表中插入一对新((original_target，translation_target)<br>**TinyInst::InstrumentRet**<br>
对ret指令插桩，最后rax中保存返回地址

```
mov [rsp + rax_offset], rax
//保存rax
mov rax, [rsp]
mov [rsp + ret_offset], rax
//保存返回地址
lea rsp, [rsp + ret_pop]
//栈对齐
push f
mov rax, [rsp + rax_offset]
push rax
mov rax, [rsp + ret_offset]
调用TinyInst::InstrumentIndirect
```

**TinyInst::InstrumentIndirect**<br>
调用TinyInst::InstrumentGlobalIndirect或者TinyInst::InstrumentLocalIndirect<br>**TinyInst::InstrumentGlobalIndirect**<br>
使用全局跳转表转换间接jump/call xxx<br>**TinyInst::InstrumentLocalIndirect**<br>
使用本地跳转表转换间接jump/call xxx<br>**TinyInst::TranslateBasicBlock**<br>
首先保存原始偏移和插桩后的偏移，调用LiteCov::InstrumentBasicBlock进行基本块插桩，然后调用LiteCov::InstrumentInstruction进行指令级插桩。<br>
1.如果基本块的最后一条指令是ret指令则调用InstrumentRet插桩；<br>
2.如果基本块的最后一条指令是条件跳转指令，则进行如下所示的插桩：<br>
插桩前：

```
// j* target_address
```

插桩后：

```
// j* label
// &lt;edge instrumentation&gt;
// jmp continue_address
// label:
// &lt;edge instrumentation&gt;
// jmp target_address
```

3.如果基本块的最后一条指令是非条件跳转指令并且是jmp address(不是jmp [address]这样的指令)，则改成jmp fixed_address；如果基本块的最后一条指令是非条件跳转指令并且不是jmp address，则调用InstrumentIndirect插桩；<br>
4.如果基本块的最后一条指令是call指令并且是call address(不是call [address]这样的指令)，则进行如下所示的插桩：<br>
插桩前：

```
// call target_address
```

插桩后：

```
// call label
// jmp return_address
// label:
// jmp target_address
```

如果基本块的最后一条指令是call指令并且不是call address，则调用InstrumentIndirect插桩。<br>**TinyInst::TranslateBasicBlockRecursive**<br>
从起始地址开始任何插桩过程中遇到的基本块都加入到队列循环调用TranslateBasicBlock进行插桩<br>**TinyInst::OnCrashed**<br>
打印出crash时的信息，前后的代码，所在的模块等等<br>**TinyInst::GetTranslatedAddress**<br>
返回给定地址对应的插桩模块中的地址<br>**TinyInst::TryExecuteInstrumented**<br>
检查给定地址是否能在插桩模块中找到，如果是则调用LiteCov::OnModuleEntered，将rip设为其在插桩模块中的地址<br>**TinyInst::InstrumentModule/TinyInst::InstrumentAllLoadedModules**<br>
对模块进行插桩，首先将模块中所有可执行的区域标记为不可执行并拷贝这些代码，然后为插桩的代码分配地址空间，调用TinyInst::InitGlobalJumptable初始化全局跳转表，最后调用LiteCov::OnModuleInstrumented<br>**TinyInst::OnInstrumentModuleLoaded**<br>
调用TinyInst::InstrumentModule<br>**TinyInst::OnModuleLoaded**<br>
如果需要插桩该模块则调用TinyInst::OnInstrumentModuleLoaded<br>**TinyInst::OnModuleUnloaded**<br>
清除插桩信息<br>**TinyInst::OnTargetMethodReached**<br>
调用TinyInst::InstrumentAllLoadedModules<br>**TinyInst::OnEntrypoint**<br>
调用TinyInst::InstrumentAllLoadedModules<br>**TinyInst::OnException**<br>
如果是断点导致的异常调用TinyInst::HandleBreakpoint；如果是ACCESS_VIOLATION这可能是因为要执行的代码在插桩的代码区域，调用TinyInst::TryExecuteInstrumented<br>**TinyInst::OnProcessExit**<br>
清理并调用LiteCov::OnModuleUninstrumented



## litecov.cpp

最后我们来看流程图中红色的函数，这里终于涉及到了关于代码覆盖率处理。我们先快速过一下用到的x86_helpers.c中的函数以便之后更好理解litecov.cpp中的代码。

**GetUnusedRegister**<br>
返回AX/EAX/RAX<br>**Get8BitRegister**<br>
返回寄存器的低8位，例如对于AX/EAX/RAX都返回AL<br>**GetFullSizeRegister**<br>
和Get8BitRegister相反，RAX/EAX/AX/AH/AL都返回RAX(64位)，EAX/AX/AH/AL都返回EAX(32位)<br>**Push**<br>
生成push指令<br>**Pop**<br>
生成pop指令<br>**CopyOperandFromInstruction**<br>
进行指令级插桩时如果cmp指令的第一个操作数不是寄存器(cmp DWORD PTR [ebp-0x14], eax)那么需要一条mov指令将第一个操作数移到寄存器中(mov ecx, DWORD PTR [ebp-0x14]),该函数将cmp指令的第一个操作数拷贝到mov指令的第二个操作数<br>**Mov**<br>
生成mov指令<br>**Lzcnt**<br>
生成lzcnt指令<br>**CmpImm8**<br>
生成cmp指令<br>**GetInstructionLength**<br>
获取指令长度<br>**FixRipDisplacement**<br>
修复[rip+displacement]这样的指令的偏移

下面几个变量单独说一下：

```
unsigned char *coverage_buffer_remote;
//指向coverage buffer起始位置的指针
size_t coverage_buffer_size;
//coverage buffer总大小
size_t coverage_buffer_next;
//coverage buffer已经占用的大小
std::set&lt;uint64_t&gt; collected_coverage;
//收集的coverage的集合
std::set&lt;uint64_t&gt; ignore_coverage;
//忽略的coverage的集合
std::unordered_map&lt;size_t, uint64_t&gt; buf_to_coverage;
//key是coverage_buffer的偏移，valve是对应的basic block/edge code
std::unordered_map&lt;uint64_t, size_t&gt; coverage_to_inst;
//key是basic block/edge code，valve是对应的插桩区域中的位置
std::unordered_map&lt;size_t, CmpCoverageRecord*&gt; buf_to_cmp;
//key是cmp code，value是对应的CmpCoverageRecord
std::unordered_map&lt;uint64_t, CmpCoverageRecord*&gt; coverage_to_cmp;
//key是coverage_buffer的偏移，valve是对应的CmpCoverageRecord
```

下面是图中函数的注释。

**LiteCov:: OnModuleInstrumented**<br>
分配coverage_buffer<br>**LiteCov:: OnModuleUninstrumented**<br>
调用LiteCov::CollectCoverage，释放coverage_buffer<br>**LiteCov::EmitCoverageInstrumentation**<br>
插入mov [coverage_buffer_remote + coverage_buffer_next], 1<br>
将信息记录到buf_to_coverage和coverage_to_inst<br>**LiteCov::InstrumentBasicBlock**<br>
基本块插桩，调用LiteCov::EmitCoverageInstrumentation<br>**LiteCov::InstrumentEdge**<br>
边插桩，调用LiteCov::EmitCoverageInstrumentation<br>**LiteCov::GetBBCode**<br>
basic block code是模块起始地址到基本块的偏移<br>**LiteCov::GetEdgeCode**<br>
edge code的低32位和高32位分别表示源地址和目的地址<br>**LiteCov::InstrumentInstruction**<br>
实现指令级插桩，当指定了compare_coverage时可以通过指令级插桩记录cmp/sub指令中匹配的字节数。对于sub指令调用LiteCov::ShouldInstrumentSub判断是否应该插桩。<br>
插桩前：

```
cmp    DWORD PTR [ebp-0x14],eax
```

插桩后：

```
push   ecx
mov    ecx,DWORD PTR [ebp-0x14]
xor    ecx,eax
lzcnt  ecx,ecx
cmp   ecx, match_width
jb end
mov   BYTE PTR [data-&gt;coverage_buffer_remote + data-&gt;coverage_buffer_next],cl
end:
pop        ecx
将信息记录到buf_to_cmp和coverage_to_cmp
```

**LiteCov::OnModuleEntered**<br>
如果插桩边，因为源地址来自另一个模块，所以用0表示源地址，加入到collected_coverage<br>**LiteCov::CollectCoverage**<br>
读取coverage_buffer_remote中的数据，通过buf_to_coverage找到对应的basic block/edge code, 如果没有找到并且设置了-cmp_coverage说明此处是cmp的coverage信息，调用CollectCmpCoverage获取cmp code并加入collected_coverage；如果找到了则将basic block/edge code加入collected_coverage<br>**LiteCov::OnProcessExit**<br>
调用CollectCoverage<br>**LiteCov::GetCmpCode**<br>
cmp code高32位表示basic block偏移，接下来的24位表示cmp指令在basic block内的偏移，最后8位表示匹配的bit数。最高位设为1<br>**LiteCov::ShouldInstrumentSub**<br>
是否应该插桩sub指令，如果后面有call/ret/jmp这样的指令就不插桩，如果后面有cmov/jz/jnz这样的指令就插桩



## coverage.cpp

coverage.cpp实现了对coverage的管理，Coverage列表中每个成员是一个ModuleCoverage，两个成员分别是模块名和该模块中的basic block/edge/cmp code。代码很简单就不再赘述了。



## 总结

如前所述，作者也给出了一个示例程序tinyinst-coverage.cpp。基本上主要的代码就是这样。希望这篇文章能对动态插桩和tinyInst感兴趣的同学有所帮助。

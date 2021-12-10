> 原文链接: https://www.anquanke.com//post/id/262468 


# 《Chrome V8源码》32.字节码和 Compiler Pipeline 的细节


                                阅读量   
                                **138156**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01a7684e97e8b84c03.png)](https://p1.ssl.qhimg.com/t01a7684e97e8b84c03.png)



## 1 摘要

本篇文章是 Builtin 专题的第七篇。上篇文章讲解了 Builtin::kInterpreterEntryTrampoline 源码，本篇文章将介绍 Builin 的编译过程，在此过程中可以看到 Bytecode hanlder 生成 code 的技术细节，同时也可借助此过程了解 Compiler Pipeline 技术和重要数据结构。



## 2 Bytecode handler的重要数据结构

GenerateBytecodeHandler()负责生成Bytecode hander，源码如下：

```
1.  Handle&lt;Code&gt; GenerateBytecodeHandler(Isolate* isolate, const char* debug_name,
2.                                       Bytecode bytecode,
3.                                       OperandScale operand_scale,
4.                                       int builtin_index,
5.                                       const AssemblerOptions&amp; options) `{`
6.    Zone zone(isolate-&gt;allocator(), ZONE_NAME);
7.    compiler::CodeAssemblerState state(
8.        isolate, &amp;zone, InterpreterDispatchDescriptor`{``}`, Code::BYTECODE_HANDLER,
9.        debug_name,
10.        FLAG_untrusted_code_mitigations
11.            ? PoisoningMitigationLevel::kPoisonCriticalOnly
12.            : PoisoningMitigationLevel::kDontPoison,
13.        builtin_index);
14.    switch (bytecode) `{`
15.  #define CALL_GENERATOR(Name, ...)                     \
16.    case Bytecode::k##Name:                             \
17.      Name##Assembler::Generate(&amp;state, operand_scale); \
18.      break;
19.      BYTECODE_LIST(CALL_GENERATOR);
20.  #undef CALL_GENERATOR
21.    `}`
22.    Handle&lt;Code&gt; code = compiler::CodeAssembler::GenerateCode(&amp;state, options);
23.  #ifdef ENABLE_DISASSEMBLER
24.    if (FLAG_trace_ignition_codegen) `{`
25.      StdoutStream os;
26.      code-&gt;Disassemble(Bytecodes::ToString(bytecode), os);
27.      os &lt;&lt; std::flush;
28.    `}`
29.  #endif  // ENABLE_DISASSEMBLER
30.    return code;
31.  `}`
```

上述代码第 7-13 行初始化 state，state 中包括 BytecodeOffset、 DispatchTable 和 Descriptor，Bytecode 编译时会使用state。 第 14-21 行代码生成 Bytecode handler 源码。第 17 行 state 作为参数传入 GenerateCode() 中，用于记录 Bytecode hadler 的生成结果。下面以 LdaSmi 为例讲解 Bytecode handler 的重要数据结构：

```
IGNITION_HANDLER(LdaSmi, InterpreterAssembler) `{`
  TNode&lt;Smi&gt; smi_int = BytecodeOperandImmSmi(0);
  SetAccumulator(smi_int);
  Dispatch();
`}`
```

上述代码将累加寄存器的值设置为 smi。展开宏 IGNITION_HANDLER 后可以看到 LdaSmiAssembler 是子类，InterpreterAssembler 是父类，说明如下：<br>**（1）** LdaSmiAssembler 中包括生成 LdaSmi 的入口方法 Genrate()，源码如下：

```
1.void Name##Assembler::Generate(compiler::CodeAssemblerState* state,
1.                               OperandScale scale) `{`
2.  Name##Assembler assembler(state, Bytecode::k##Name, scale);
3.  state-&gt;SetInitialDebugInformation(#Name, __FILE__, __LINE__);
4.  assembler.GenerateImpl();  
6.`}`
```

上述第3行代码创建 LdaSmiAssembler 实例。第4行代码把 debug 信息写入state。<br>**（2）** InterpreterAssembler 提供解释器相关的功能，源码如下：

```
1.  class V8_EXPORT_PRIVATE InterpreterAssembler : public CodeStubAssembler `{`
2.  public:
3.  //.............省略.........................
4.  private:
5.   TNode&lt;BytecodeArray&gt; BytecodeArrayTaggedPointer();
6.   TNode&lt;ExternalReference&gt; DispatchTablePointer();
7.   TNode&lt;Object&gt; GetAccumulatorUnchecked();
8.   TNode&lt;RawPtrT&gt; GetInterpretedFramePointer();
9.    compiler::TNode&lt;IntPtrT&gt; RegisterLocation(Register reg);
10.    compiler::TNode&lt;IntPtrT&gt; RegisterLocation(compiler::TNode&lt;IntPtrT&gt; reg_index);
11.    compiler::TNode&lt;IntPtrT&gt; NextRegister(compiler::TNode&lt;IntPtrT&gt; reg_index);
12.    compiler::TNode&lt;Object&gt; LoadRegister(compiler::TNode&lt;IntPtrT&gt; reg_index);
13.    void StoreRegister(compiler::TNode&lt;Object&gt; value,
14.                       compiler::TNode&lt;IntPtrT&gt; reg_index);
15.    void CallPrologue();
16.    void CallEpilogue();
17.    void TraceBytecodeDispatch(TNode&lt;WordT&gt; target_bytecode);
18.    void TraceBytecode(Runtime::FunctionId function_id);
19.    void Jump(compiler::TNode&lt;IntPtrT&gt; jump_offset, bool backward);
20.    void JumpConditional(compiler::TNode&lt;BoolT&gt; condition,
21.                         compiler::TNode&lt;IntPtrT&gt; jump_offset);
22.    void SaveBytecodeOffset();
23.    TNode&lt;IntPtrT&gt; ReloadBytecodeOffset();
24.    TNode&lt;IntPtrT&gt; Advance();
25.    TNode&lt;IntPtrT&gt; Advance(int delta);
26.    TNode&lt;IntPtrT&gt; Advance(TNode&lt;IntPtrT&gt; delta, bool backward = false);
27.    compiler::TNode&lt;WordT&gt; LoadBytecode(compiler::TNode&lt;IntPtrT&gt; bytecode_offset);
28.    void DispatchToBytecodeHandlerEntry(compiler::TNode&lt;RawPtrT&gt; handler_entry,
29.                                        compiler::TNode&lt;IntPtrT&gt; bytecode_offset);
30.    int CurrentBytecodeSize() const;
31.    OperandScale operand_scale() const `{` return operand_scale_; `}`
32.    Bytecode bytecode_;
33.    OperandScale operand_scale_;
34.    CodeStubAssembler::TVariable&lt;RawPtrT&gt; interpreted_frame_pointer_;
35.    CodeStubAssembler::TVariable&lt;BytecodeArray&gt; bytecode_array_;
36.    CodeStubAssembler::TVariable&lt;IntPtrT&gt; bytecode_offset_;
37.    CodeStubAssembler::TVariable&lt;ExternalReference&gt; dispatch_table_;
38.    CodeStubAssembler::TVariable&lt;Object&gt; accumulator_;
39.    AccumulatorUse accumulator_use_;
40.    bool made_call_;
41.    bool reloaded_frame_ptr_;
42.    bool bytecode_array_valid_;
43.    DISALLOW_COPY_AND_ASSIGN(InterpreterAssembler);
44.  `}`;
```

上述第 5 行代码获取 BytecodeArray 的地址；第 6 行代码获取 DispatchTable 的地址；第 7 行代码获取累加寄存器的值；第8-13行代码用于操作寄存器；第 15-16 行代码用于调用函数前后的堆栈处理；第 17-18 行代码用于跟踪 Bytecode，其中第18行会调用Runtime::Runtime**InterpreterTraceBytecodeEntry以输出寄存器信息；第 19-20 行代码是两条跳转指令，在该指令的内部调用 Advance（第24-26行）来完成跳转操作；第 24-26 行代码用于获取下一条 Bytecode；第 32-42 行代码定义的成员变量在 Bytecode handler 中会被频繁使用，例如在 SetAccumulator(zero_value) 中先设置 accumulator_use** 为写状态，再把值写入 accumulator_。<br>**（3）** CodeStubAssembler 是 InterpreterAssembler 的父类，提供 JavaScript 的特有方法，源码如下：

```
1.  class V8_EXPORT_PRIVATE CodeStubAssembler: public compiler::CodeAssembler,
2.       public TorqueGeneratedExportedMacrosAssembler `{`
3.  public:
4.   TNode&lt;Int32T&gt; StringCharCodeAt(SloppyTNode&lt;String&gt; string,
5.                                  SloppyTNode&lt;IntPtrT&gt; index);
6.    TNode&lt;String&gt; StringFromSingleCharCode(TNode&lt;Int32T&gt; code);
7.    TNode&lt;String&gt; SubString(TNode&lt;String&gt; string, TNode&lt;IntPtrT&gt; from,
8.                            TNode&lt;IntPtrT&gt; to);
9.    TNode&lt;String&gt; StringAdd(Node* context, TNode&lt;String&gt; first,
10.                            TNode&lt;String&gt; second);
11.    TNode&lt;Number&gt; ToNumber(
12.        SloppyTNode&lt;Context&gt; context, SloppyTNode&lt;Object&gt; input,
13.        BigIntHandling bigint_handling = BigIntHandling::kThrow);
14.    TNode&lt;Number&gt; ToNumber_Inline(SloppyTNode&lt;Context&gt; context,
15.                                  SloppyTNode&lt;Object&gt; input);
16.    TNode&lt;BigInt&gt; ToBigInt(SloppyTNode&lt;Context&gt; context,
17.                           SloppyTNode&lt;Object&gt; input);
18.    TNode&lt;Number&gt; ToUint32(SloppyTNode&lt;Context&gt; context,
19.                           SloppyTNode&lt;Object&gt; input);
20.    // ES6 7.1.17 ToIndex, but jumps to range_error if the result is not a Smi.
21.    TNode&lt;Smi&gt; ToSmiIndex(TNode&lt;Context&gt; context, TNode&lt;Object&gt; input,
22.                          Label* range_error);
23.    TNode&lt;Smi&gt; ToSmiLength(TNode&lt;Context&gt; context, TNode&lt;Object&gt; input,
24.                           Label* range_error);
25.    TNode&lt;Number&gt; ToLength_Inline(SloppyTNode&lt;Context&gt; context,
26.                                  SloppyTNode&lt;Object&gt; input);
27.    TNode&lt;Object&gt; GetProperty(SloppyTNode&lt;Context&gt; context,
28.                              SloppyTNode&lt;Object&gt; receiver, Handle&lt;Name&gt; name) `{``}`
29.    TNode&lt;Object&gt; GetProperty(SloppyTNode&lt;Context&gt; context,
30.                              SloppyTNode&lt;Object&gt; receiver,
31.                              SloppyTNode&lt;Object&gt; name) `{``}`
32.    TNode&lt;Object&gt; SetPropertyStrict(TNode&lt;Context&gt; context,
33.                                    TNode&lt;Object&gt; receiver, TNode&lt;Object&gt; key,
34.                                    TNode&lt;Object&gt; value) `{``}`
35.    template &lt;class... TArgs&gt;
36.    TNode&lt;Object&gt; CallBuiltin(Builtins::Name id, SloppyTNode&lt;Object&gt; context,
37.                              TArgs... args) `{``}`
38.    template &lt;class... TArgs&gt;
39.    void TailCallBuiltin(Builtins::Name id, SloppyTNode&lt;Object&gt; context,
40.                         TArgs... args) `{`  `}`
41.    void LoadPropertyFromFastObject(...省略参数...);
42.    void LoadPropertyFromFastObject(...省略参数...);
43.    void LoadPropertyFromNameDictionary(...省略参数...);
44.    void LoadPropertyFromGlobalDictionary(...省略参数...);
45.    void UpdateFeedback(Node* feedback, Node* feedback_vector, Node* slot_id);
46.    void ReportFeedbackUpdate(TNode&lt;FeedbackVector&gt; feedback_vector,
47.                              SloppyTNode&lt;UintPtrT&gt; slot_id, const char* reason);
48.    void CombineFeedback(Variable* existing_feedback, int feedback);
49.    void CombineFeedback(Variable* existing_feedback, Node* feedback);
50.    void OverwriteFeedback(Variable* existing_feedback, int new_feedback);
51.    void BranchIfNumberRelationalComparison(Operation op,
52.                                            SloppyTNode&lt;Number&gt; left,
53.                                            SloppyTNode&lt;Number&gt; right,
54.                                            Label* if_true, Label* if_false);
55.    void BranchIfNumberEqual(TNode&lt;Number&gt; left, TNode&lt;Number&gt; right,
56.                             Label* if_true, Label* if_false) `{`
57.    `}`
58.  `}`;
```

CodeStubAssembler 利用汇编语言实现了 JavaScript 的特有方法。基类 CodeAssembler 对汇编语言进行封装， CodeStubAssembler 使用 CodeAssembler 提供的汇编功能实现了字符串转换、属性获取和分支跳转等 JavaScript 功能，这正是 CodeStubAssembler 的意义所在。<br>
上述代码第 4-9 行实现了字符串的相关操作；第 11-18 行代码实现了类型转换；第 21-26 行实现了 ES 规范中的功能；第 27-38 行实现了获取和设置属性；第 39-43 行实现了 Builtin 和 Runtime API 的调用方法；第 45-50 行代码用于管理 Feedback；第 51-55 行实现了 IF 功能。<br>**（4）** CodeAssembler 封装了汇编功能，实现了 Branch、Goto 等功能，源码如下：

```
1.  class V8_EXPORT_PRIVATE CodeAssembler `{`
2.    void Branch(TNode&lt;BoolT&gt; condition,
3.                CodeAssemblerParameterizedLabel&lt;T...&gt;* if_true,
4.                CodeAssemblerParameterizedLabel&lt;T...&gt;* if_false, Args... args) `{`
5.      if_true-&gt;AddInputs(args...);
6.      if_false-&gt;AddInputs(args...);
7.      Branch(condition, if_true-&gt;plain_label(), if_false-&gt;plain_label());
8.    `}`
9.    template &lt;class... T, class... Args&gt;
10.    void Goto(CodeAssemblerParameterizedLabel&lt;T...&gt;* label, Args... args) `{`
11.      label-&gt;AddInputs(args...);
12.      Goto(label-&gt;plain_label());
13.    `}`
14.    void Branch(TNode&lt;BoolT&gt; condition, const std::function&lt;void()&gt;&amp; true_body,
15.                const std::function&lt;void()&gt;&amp; false_body);
16.    void Branch(TNode&lt;BoolT&gt; condition, Label* true_label,
17.                const std::function&lt;void()&gt;&amp; false_body);
18.    void Branch(TNode&lt;BoolT&gt; condition, const std::function&lt;void()&gt;&amp; true_body,
19.                Label* false_label);
20.    void Switch(Node* index, Label* default_label, const int32_t* case_values,
21.                Label** case_labels, size_t case_count);
22.  `}`
```



## 3 Compiler Pipeline

GenerateBytecodeHandler() 的第 22 行代码完成了对 Bytecode LdaSmi 的编译，源码如下：

```
1.  Handle&lt;Code&gt; CodeAssembler::GenerateCode(CodeAssemblerState* state,
2.                                         const AssemblerOptions&amp; options) `{`
3.  RawMachineAssembler* rasm = state-&gt;raw_assembler_.get();
4.  Handle&lt;Code&gt; code;
5.  Graph* graph = rasm-&gt;ExportForOptimization();
6.  code = Pipeline::GenerateCodeForCodeStub(...省略参数...)
7.              .ToHandleChecked();
8.   state-&gt;code_generated_ = true;
9.   return code;
10.  `}`
11.  //.............分隔线...................
12.  MaybeHandle&lt;Code&gt; Pipeline::GenerateCodeForCodeStub(...省略参数...) `{`
13.    OptimizedCompilationInfo info(CStrVector(debug_name), graph-&gt;zone(), kind);
14.    info.set_builtin_index(builtin_index);
15.    if (poisoning_level != PoisoningMitigationLevel::kDontPoison) `{`
16.      info.SetPoisoningMitigationLevel(poisoning_level);
17.    `}`
18.    // Construct a pipeline for scheduling and code generation.
19.    ZoneStats zone_stats(isolate-&gt;allocator());
20.    NodeOriginTable node_origins(graph);
21.    JumpOptimizationInfo jump_opt;
22.    bool should_optimize_jumps =
23.        isolate-&gt;serializer_enabled() &amp;&amp; FLAG_turbo_rewrite_far_jumps;
24.    PipelineData data(&amp;zone_stats, &amp;info, isolate, isolate-&gt;allocator(), graph,
25.                      nullptr, source_positions, &amp;node_origins,
26.                      should_optimize_jumps ? &amp;jump_opt : nullptr, options);
27.    data.set_verify_graph(FLAG_verify_csa);
28.    std::unique_ptr&lt;PipelineStatistics&gt; pipeline_statistics;
29.    if (FLAG_turbo_stats || FLAG_turbo_stats_nvp) `{`
30.    `}`
31.    PipelineImpl pipeline(&amp;data);
32.    if (info.trace_turbo_json_enabled() || info.trace_turbo_graph_enabled()) `{`//..省略...
33.    `}`
34.    pipeline.Run&lt;CsaEarlyOptimizationPhase&gt;();
35.    pipeline.RunPrintAndVerify(CsaEarlyOptimizationPhase::phase_name(), true);
36.    // .............省略..............
37.    PipelineData second_data(...省略参数...);
38.    second_data.set_verify_graph(FLAG_verify_csa);
39.    PipelineImpl second_pipeline(&amp;second_data);
40.    second_pipeline.SelectInstructionsAndAssemble(call_descriptor);
41.    Handle&lt;Code&gt; code;
42.    if (jump_opt.is_optimizable()) `{`
43.      jump_opt.set_optimizing();
44.      code = pipeline.GenerateCode(call_descriptor).ToHandleChecked();
45.    `}` else `{`
46.      code = second_pipeline.FinalizeCode().ToHandleChecked();
47.    `}`
48.    return code;
49.  `}`
```

上述第 6 行代码进入Pipeline开始编译工作；第 13-29 用于设置 Pipeline 信息；第 32 行的使能标记在 flag-definitions.h 中定义，它们使用 Json 输出当前的编译信息；第 34-40 行代码实现了生成初始汇编码、对初始汇编码进行优化、使用优化后的数据再次生成最终代码等功能，**注意** 第 36 行代码省略了优化初始汇编码。图1给出了 LdaSmi 的编译结果。

[![](https://p2.ssl.qhimg.com/t01e7f26d80d3d26524.png)](https://p2.ssl.qhimg.com/t01e7f26d80d3d26524.png)

**技术总结**<br>**（1）** 只有 v8_use_snapshot = false 时才能在 V8 中调试 Bytecode Handler 的编译过程；<br>**（2）** CodeAssembler 封装了汇编，CodeStubAssembler 封装了JavaScript特有的功能，InterpreterAssembler 封装了解释器需要的功能，在这三层封装之上是Bytecode Handler；<br>**（3）** V8 初始化时编译包括 Byteocde handler 在内的所有 Builtin。<br>
好了，今天到这里，下次见。

**个人能力有限，有不足与纰漏，欢迎批评指正**<br>**微信：qq9123013 备注：v8交流 邮箱：[v8blink@outlook.com](mailto:v8blink@outlook.com)**

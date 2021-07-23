> 原文链接: https://www.anquanke.com//post/id/222631 


# 如何使用MVSC编译器生成XFG函数原型哈希


                                阅读量   
                                **183288**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者Quarkslab，文章来源：blog.quarkslab.com
                                <br>原文地址：[https://blog.quarkslab.com/how-the-mvsc-compiler-generates-xfg-function-prototype-hashes.html](https://blog.quarkslab.com/how-the-mvsc-compiler-generates-xfg-function-prototype-hashes.html)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t016c1644ab1a43895e.jpg)](https://p5.ssl.qhimg.com/t016c1644ab1a43895e.jpg)



## 简介

2014年，Microsoft推出了一种名为控制流保护(CFG)的控制流完整性(CFI)解决方案。CFG在过去有非常多的研究，随着时间的推移，大家想出了许多绕过CFG的方法；其中一些绕过依赖于实现，比如与JIT编译器的集成，或者易被滥用的敏感api的可用性，但这些问题最终都得到了解决。然而，一个设计问题仍然存在:CFG没有提供有效调用目标的任何粒度。任何受保护的间接调用允许调用任何有效的调用目标。在较大的二进制文件中，有效的调用目标很容易有成千上万个，这给攻击者提供了很大的灵活性，可以通过链接有效的C++虚函数来绕过CFG（参考[COOP](https://www.syssec.ruhr-uni-bochum.de/media/emma/veroeffentlichungen/2015/03/28/COOP-Oakland15.pdf)）。

这几年，Microsoft一直在开发CFG的改​​进版本，称为Xtended Flow Guard（XFG）。XFG通过类型签名检查限制间接调用/跳转，提供了一种更细粒度的CFI。XFG的概念是，在编译时将基于类型签名的哈希分配给可以作为间接调用/跳转目标的那些函数。然后，在使用XFG的间接调用位置上，执行哈希检查：仅允许具有预期签名哈希的函数。

几周前，研究员Connor McGarr发表了一篇名为[《Exploit Development: Between a Rock and a (Xtended Flow) Guard Place: Examining XFG》](https://connormcgarr.github.io/examining-xfg/)的文章。这激发了我的好奇心，所以我决定打开IDA Pro和Windbg来了解XFG哈希是如何生成的。

在写本文时，XFG已经出现在Windows 10 Insider Preview版本中中，为了编译支持XFG的程序，需要使用Visual Studio 2019预览版。

本文中的分析的二进制文件基于Visual Studio 2019 Preview 16.8.0 Preview 2.1版本：
- c1.dll version 19.28.29213.0
- c2.dll version 19.28.29213.0
这篇文章重点介绍如何为C源代码生成XFG哈希。尽管C++代码的哈希算法乍一看很相似，但我们没有深入研究它的细节。由于这是一篇相当长的文章，内容分为几个部分:首先，我们从一个关于XFG哈希的快速入门开始。然后，我们分析函数是如何哈希的，然后查看不同的C类型是如何哈希的。最后，我们检查一些应用于计算的哈希值的最终转换，并动手通过计算哈希的练习得出结论。



## 关于XFG哈希的入门

让我们从一个简单的C程序开始，该程序定义了一个名为FPTR([1])的函数指针类型，它声明了一个函数，该函数接受两个浮点参数并返回另一个浮点数。main函数声明了一个名为fptr的函数指针变量，类型为fptr，它被设置为foo([2])函数的地址，该函数的原型与fptr类型匹配。最后，在[3]处，调用fptr指向的函数，并将值1.00001和2.00002作为参数传递。

```
#include &lt;stdio.h&gt;

[1] typedef float (* FPTR)(float, float);


    float foo(float val1, float val2)`{`
        printf("I received float values %f and %f\n", val1, val2);
        return (val2 - val1);
    `}`


    int main(int argc, char **argv)`{`
[2]     FPTR fptr = foo;

        printf("Calling function pointer...\n");
[3]     fptr(1.00001, 2.00002);
        return 0;
    `}`
```

我们使用以下命令行从VS 2019 Preview的x64本机工具命令提示符中编译了上述源代码。注意，我们使用`/ guard：xfg`标志来启用XFG。

```
&gt; cl / Zi / guard：xfg example1.c
```

反汇编生成的main函数如下所示：

```
main      ; int __cdecl main(int argc, const char **argv, const char **envp)
main
main      var_18          = qword ptr -18h
main      var_10          = qword ptr -10h
main      arg_0           = dword ptr  8
main      arg_8           = qword ptr  10h
main
main          mov     [rsp+arg_8], rdx
main+5        mov     [rsp+arg_0], ecx
main+9        sub     rsp, 38h
main+D        lea     rax, foo
main+14       mov     [rsp+38h+var_18], rax
main+19       lea     rcx, aCallingFunctio ; "Calling function pointer...\n"
main+20       call    printf
main+25       mov     rax, [rsp+38h+var_18]
main+2A       mov     [rsp+38h+var_10], rax
main+2F       mov     r10, 99743F3270D52870h
main+39       movss   xmm1, cs:__real@40000054
main+41       movss   xmm0, cs:__real@3f800054
main+49       mov     rax, [rsp+38h+var_10]
main+4E       call    cs:__guard_xfg_dispatch_icall_fptr
main+54       xor     eax, eax
main+56       add     rsp, 38h
main+5A       retn
main+5A   main            endp
```

我们可以在main+0x2F处看到，对于main+0x4E后面的函数指针调用，R10寄存器被设置为预期的基于类型的哈希（0x99743F3270D52870），通过函数指针调用的函数是foo，我们可以验证它的原型哈希(由函数开始前的8字节给出)是否与预期的散列匹配，也就是说foo函数是main+0x4E处的间接调用的有效目标。更准确地说，原型哈希位于foo函数(0x99743F3270D52871)之前的8字节，与我们在R10寄存器(0x99743F3270D52870)中看到的哈希匹配，除了0位:

```
.text:0000000140001008                 dq 99743F3270D52871h
foo
foo      ; =============== S U B R O U T I N E ================================
foo      ; float __fastcall foo(float val1, float val2)
foo      foo             proc near               ; DATA XREF: main+D
foo
foo      arg_0           = dword ptr  8
foo      arg_8           = dword ptr  10h
foo
foo          movss   [rsp+arg_8], xmm1
foo+6        movss   [rsp+arg_0], xmm0
foo+C        sub     rsp, 28h
foo+10       cvtss2sd xmm0, [rsp+28h+arg_8]
foo+16       cvtss2sd xmm1, [rsp+28h+arg_0]
foo+1C       movaps  xmm2, xmm0
foo+1F       movq    r8, xmm2
foo+24       movq    rdx, xmm1
foo+29       lea     rcx, _Format    ; "I received float values %f and %f\n"
foo+30       call    printf
foo+35       movss   xmm0, [rsp+28h+arg_8]
foo+3B       subss   xmm0, [rsp+28h+arg_0]
foo+41       add     rsp, 28h
foo+45       retn
foo+45   foo             endp
```

但是不必担心这种差异，因为在XFG调度函数（ntdll！LdrpDispatchUserCallTargetXFG）的起始处，R10的0位就被设置了，导致预期哈希值和函数哈希值在0位上的差异没有意义。

```
LdrpDispatchUserCallTargetXFG      LdrpDispatchUserCallTargetXFG proc near
LdrpDispatchUserCallTargetXFG      ; __unwind `{` // LdrpICallHandler
LdrpDispatchUserCallTargetXFG          or      r10, 1
LdrpDispatchUserCallTargetXFG+4        test    al, 0Fh
LdrpDispatchUserCallTargetXFG+6        jnz     short loc_180094337
LdrpDispatchUserCallTargetXFG+8        test    ax, 0FFFh
LdrpDispatchUserCallTargetXFG+C        jz      short loc_180094337
LdrpDispatchUserCallTargetXFG+E        cmp     r10, [rax-8]
LdrpDispatchUserCallTargetXFG+12       jnz     short loc_180094337
LdrpDispatchUserCallTargetXFG+14       jmp     rax
```



## 哈希函数类型

MSVC编译器由两个阶段组成：前端和后端。前端是特定于语言的：它读取源代码，词法，解析，进行语义分析并发出IL（中间语言）。后端特定于目标体系结构：它读取前端生成的IL，执行优化并为给定的体系结构生成代码。

函数原型哈希的生成留给前端语言处理。这意味着在编译C代码时，C前端(c1.dll)负责生成原型哈希，而在编译C++代码时，C++前端(c1xxxx .dll)负责这项任务。

一旦原型哈希由相应的前端语言生成，编译器后端(在我们的例子中是x64后端，c2.dll)将执行一些最终的转换。在下面，我们将详细介绍在编译C代码时创建原型哈希的具体步骤。

当使用/guard:xfg标志编译C源代码时，编译器前端调用c1!XFGHelper__ComputeHash_1 函数，来计算要处理的函数的原型哈希值。

c1 !XFGHelper__ComputeHash_1函数创建一个XFGHelper::XFGHasher类型的对象，对象负责为正在处理的函数收集类型信息，并根据收集到的类型信息生成原型哈希。XFGHelper::XFGHasher使用std::vector的一个实例来存储所有将要被哈希的类型信息，并且它提供了许多方法，这些方法在构建哈希的过程中被调用:
- XFGHelper::XFGHasher::add_function_type()
- XFGHelper::XFGHasher::add_type()
- XFGHelper::XFGHasher::get_hash()
- XFGHelper::XFGTypeHasher::compute_hash()
- XFGHelper::XFGTypeHasher::hash_indirection()
- XFGHelper::XFGTypeHasher::hash_tag()
- XFGHelper::XFGTypeHasher::hash_primitive()
在初始化XFGHelper::XFGHasher的实例后，XFGHelper_uucomputehash_1函数调用XFGHelper::XFGHasher::add_function_type（），将XFGHelper::XFGHasher的实例和一个包含哈希函数的类型信息的type_t对象作为参数传递。

```
XFGHelper__ComputeHash_1      XFGHelper__ComputeHash_1 proc near
XFGHelper__ComputeHash_1
XFGHelper__ComputeHash_1      arg_0           = qword ptr  8
XFGHelper__ComputeHash_1      arg_8           = qword ptr  10h
XFGHelper__ComputeHash_1      arg_10          = qword ptr  18h
[...]
XFGHelper__ComputeHash_1+79        xorps   xmm0, xmm0
XFGHelper__ComputeHash_1+7C        movdqu  cs:xfg_hasher, xmm0 ; zero inits xfg_hasher
[...]
XFGHelper__ComputeHash_1+B1        mov     rdx, rbp        ; rdx = Type_t containing function information
XFGHelper__ComputeHash_1+B4        lea     rbp, xfg_hasher
XFGHelper__ComputeHash_1+BB        mov     rcx, rbp
XFGHelper__ComputeHash_1+BE        call    XFGHelper::XFGHasher::add_function_type(Type_t const *,XFGHelper::VirtualInfoFromDeclspec)
XFGHelper__ComputeHash_1+C3        mov     rdx, rsi        ; rdx = function-&gt;return_type (struct Type_t *)
XFGHelper__ComputeHash_1+C6        mov     rcx, rbp        ; this
XFGHelper__ComputeHash_1+C9        call    XFGHelper::XFGHasher::add_type(Type_t const *) ; (step 5)
```

函数XFGHelper::XFGHasher::add_function_type将检索有关正被哈希的函数的4条信息，从XFGHelper::XFGHasher::add_function_type返回后，通过调用XFGHelper::XFGHasher::add_type会再添加一条信息。正如我们在上面的反汇编中XFGHelper__ComputeHash_1 + C9上看到的那样。这些信息存储在XFGHelper::XFGHasher实例拥有的std::vector中：
- 1.4个字节，表示函数的参数数量；
- 2.每个函数参数8个字节，保存所述参数类型的哈希值；
- 1个字节，表示函数是否可变参数（即，是否使用可变数量的参数）；
- 4个字节，指定函数使用的调用约定；
- 8个字节，存放函数返回类型的哈希值。
### <a class="reference-link" name="component%201%EF%BC%9A%E5%8F%82%E6%95%B0%E6%95%B0%E9%87%8F"></a>component 1：参数数量

XFGHelper::XFGHasher::add_function_type函数首先向std::vector添加一个DWORD，表示函数的参数数量。注意,这个数字可以影响函数接受数量可变的参数,或具有来自**declspec的virtual信息的影响我怀疑这可能是C ++的XFG实现中的某些重用代码，因此，它实际上不适用于C代码，尽管我尚未确认）。简而言之，此处考虑的参数数量将是在函数原型中声明的实际参数数量；如果函数采用可变数量的参数，则为负1；如果函数具有来自**declspec的虚信息，则为负1 。

```
XFGHelper::XFGHasher::add_function_type+18        mov     rsi, [rdx+10h]  ; rsi = function_info-&gt;FunctionTypeInfo
XFGHelper::XFGHasher::add_function_type+1C        mov     rbx, rcx
XFGHelper::XFGHasher::add_function_type+1F        mov     rcx, rsi        ; this
XFGHelper::XFGHasher::add_function_type+22        movzx   r14d, r8b
XFGHelper::XFGHasher::add_function_type+26        mov     r15, rdx
XFGHelper::XFGHasher::add_function_type+29        call    FunctionTypeInfo_t::RealNumberOfParameters(void)
XFGHelper::XFGHasher::add_function_type+2E        mov     rcx, rsi        ; this
XFGHelper::XFGHasher::add_function_type+31        mov     r9d, eax        ; r9 = real_number_of_params
XFGHelper::XFGHasher::add_function_type+34        call    FunctionTypeInfo_t::IsVarArgsFunction(void)
XFGHelper::XFGHasher::add_function_type+39        mov     rdx, [rbx+8]
XFGHelper::XFGHasher::add_function_type+3D        lea     rbp, [r9-1]     ; rbp = real_number_of_params - 1
XFGHelper::XFGHasher::add_function_type+41        test    al, al          ; is variadic function?
XFGHelper::XFGHasher::add_function_type+43        mov     rcx, rbx
XFGHelper::XFGHasher::add_function_type+46        cmovz   rbp, r9         ; if not variadic, rbp = real_number_of_params
XFGHelper::XFGHasher::add_function_type+4A        test    r8b, r8b        ; does it have virtual info from __declspec?
XFGHelper::XFGHasher::add_function_type+4D        lea     r9, [rsp+48h+arg_14]
XFGHelper::XFGHasher::add_function_type+52        lea     r8, [rsp+48h+arg_10]
XFGHelper::XFGHasher::add_function_type+57        lea     eax, [rbp-1]    ; number of params = rbp - 1
XFGHelper::XFGHasher::add_function_type+5A        cmovz   eax, ebp        ; if no virtual info from __declspec, number of params = rbp
XFGHelper::XFGHasher::add_function_type+5D        mov     [rsp+48h+arg_10], eax ; value to add = number of params (dword)
XFGHelper::XFGHasher::add_function_type+5D                     ; [step 1]
XFGHelper::XFGHasher::add_function_type+61        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
```

### <a class="reference-link" name="component%202%EF%BC%9A%E6%AF%8F%E4%B8%AA%E5%8F%82%E6%95%B0%E7%B1%BB%E5%9E%8B%E7%9A%84%E5%93%88%E5%B8%8C"></a>component 2：每个参数类型的哈希

接下来，XFGHelper::XFGHasher::add_function_type进入一个循环，在循环中计算每个函数参数类型的哈希，并将每个类型哈希(8字节)添加到std::vector中。

对于一些边缘情况(type &amp; 0x10f == 0x103, type &amp; 0x103 == 0x101)有特殊的处理，但是对于大多数参数类型，它将退回到loc_180105541。在该位置，如果需要（调用Type_t::clearModifiersAndQualifiers），则清除表示要处理的参数类型的Type_t对象的限定符（例如const（0x800）和volatile（0x40）），然后清除8个字节的哈希通过调用XFGHelper::XFGHasher::add_type将参数类型添加到std::vector，我们可以在下面看到XFGHelper::XFGHasher::add_function_type + CC。如果您想知道XFGHelper::XFGHasher::add_type如何精确计算给定Type_t的哈希，会在下文中详细介绍。

最后，如果还有更多参数需要哈希，它将跳回到循环的起始位置。

```
XFGHelper::XFGHasher::add_function_type+6E   loc_1801054F6:
XFGHelper::XFGHasher::add_function_type+6E        mov     rax, [rsi]      ; rax = &amp;function_info-&gt;params
XFGHelper::XFGHasher::add_function_type+71        mov     rcx, [rax+rdi*8] ; rcx = function_info-&gt;params[i] (Type_t)
XFGHelper::XFGHasher::add_function_type+75        mov     edx, [rcx]      ; edx = params[i].type
XFGHelper::XFGHasher::add_function_type+77        mov     eax, edx
XFGHelper::XFGHasher::add_function_type+79        and     eax, 10Fh
XFGHelper::XFGHasher::add_function_type+7E        cmp     eax, 103h       ; params[i].type &amp; 0x10f == 0x103 ?
XFGHelper::XFGHasher::add_function_type+83        jnz     short loc_18010552C
XFGHelper::XFGHasher::add_function_type+85        cmp     edx, 8103h      ; params[i].type == 0x8103 ?
XFGHelper::XFGHasher::add_function_type+8B        jz      short loc_18010554E
XFGHelper::XFGHasher::add_function_type+8D        mov     r8d, [rcx+4]
XFGHelper::XFGHasher::add_function_type+91        lea     edx, [rax-1]
XFGHelper::XFGHasher::add_function_type+94        mov     rcx, [rcx+8]
XFGHelper::XFGHasher::add_function_type+98        btr     r8d, 1Fh
XFGHelper::XFGHasher::add_function_type+9D        call    Type_t::createType(Type_t const *,uint,mod_t,bool)
XFGHelper::XFGHasher::add_function_type+A2        jmp     short loc_18010554B
XFGHelper::XFGHasher::add_function_type+A4   ; --------------------------------------------------------------
XFGHelper::XFGHasher::add_function_type+A4
XFGHelper::XFGHasher::add_function_type+A4   loc_18010552C:
XFGHelper::XFGHasher::add_function_type+A4        and     edx, 103h
XFGHelper::XFGHasher::add_function_type+AA        cmp     edx, 101h       ; params[i].type &amp; 0x103 == 0x101 ?
XFGHelper::XFGHasher::add_function_type+B0        jnz     short loc_180105541
XFGHelper::XFGHasher::add_function_type+B2        call    Type_t::decayFunctionType(void)
XFGHelper::XFGHasher::add_function_type+B7        jmp     short loc_18010554B
XFGHelper::XFGHasher::add_function_type+B9   ; --------------------------------------------------------------
XFGHelper::XFGHasher::add_function_type+B9
XFGHelper::XFGHasher::add_function_type+B9   loc_180105541:
XFGHelper::XFGHasher::add_function_type+B9        mov     edx, 8C0h       ; discards qualifiers 0x800 (const) | 0x80 | 0x40 (volatile)
XFGHelper::XFGHasher::add_function_type+BE        call    Type_t::clearModifiersAndQualifiers(mod_t)
XFGHelper::XFGHasher::add_function_type+C3
XFGHelper::XFGHasher::add_function_type+C3   loc_18010554B:
XFGHelper::XFGHasher::add_function_type+C3                     ; XFGHelper::XFGHasher::add_function_type+B7↑j
XFGHelper::XFGHasher::add_function_type+C3        mov     rcx, rax
XFGHelper::XFGHasher::add_function_type+C6
XFGHelper::XFGHasher::add_function_type+C6   loc_18010554E:
XFGHelper::XFGHasher::add_function_type+C6        mov     rdx, rcx        ; struct Type_t *
XFGHelper::XFGHasher::add_function_type+C9        mov     rcx, rbx        ; this
XFGHelper::XFGHasher::add_function_type+CC        call    XFGHelper::XFGHasher::add_type(Type_t const *) ; adds hash of params[i] type
XFGHelper::XFGHasher::add_function_type+CC                     ; [step 2]
XFGHelper::XFGHasher::add_function_type+D1        inc     rdi
XFGHelper::XFGHasher::add_function_type+D4        cmp     rdi, rbp        ; counter &lt; number_of_params ?
XFGHelper::XFGHasher::add_function_type+D7        jb      short loc_1801054F6 ; if so, loop
```

### <a class="reference-link" name="component%203%EF%BC%9A%E5%8F%AF%E5%8F%98%E5%8F%82%E5%87%BD%E6%95%B0"></a>component 3：可变参函数

下一步是向std::vector添加一个字节，表示该函数是否接受可变数量的参数。在大多数情况下，当函数不包含来自__declspec的virtual信息时，将采用以下代码路径：

```
XFGHelper::XFGHasher::add_function_type+D9        mov     rcx, rsi        ; this = functioninfo
XFGHelper::XFGHasher::add_function_type+DC        call    FunctionTypeInfo_t::IsVarArgsFunction(void)
XFGHelper::XFGHasher::add_function_type+E1        mov     r8b, al         ; r8b = is_var_args_function
XFGHelper::XFGHasher::add_function_type+E4        test    r14b, r14b      ; contains virtual info from __declspec?
XFGHelper::XFGHasher::add_function_type+E7        jz      short loc_1801055EB
[...]
XFGHelper::XFGHasher::add_function_type+163  loc_1801055EB:
XFGHelper::XFGHasher::add_function_type+163        mov     rdx, [rbx+8]
XFGHelper::XFGHasher::add_function_type+167        lea     r9, [rsp+48h+arg_10+1]
XFGHelper::XFGHasher::add_function_type+16C        mov     byte ptr [rsp+48h+arg_10], r8b ; value to add = is_var_args_function (byte)
XFGHelper::XFGHasher::add_function_type+16C        ; [step 3]
XFGHelper::XFGHasher::add_function_type+171        mov     rcx, rbx
XFGHelper::XFGHasher::add_function_type+174        lea     r8, [rsp+48h+arg_10]
XFGHelper::XFGHasher::add_function_type+179        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
```

### <a class="reference-link" name="component%204%EF%BC%9A%E8%B0%83%E7%94%A8%E7%BA%A6%E5%AE%9A"></a>component 4：调用约定

最后，XFGHelper::XFGHasher::add_function_type将一个4字节的值添加到std::vector，表示该函数使用的调用约定。Intel x64体系结构上没有较多的调用约定（与x86体系结构不同）：默认的x64调用约定在寄存器RCX，RDX，R8和R9中传递整数参数，而浮点参数则通过XMM0-XMM3传递。该默认调用约定在内部由值0x201表示，但是由于在将其保存到std :: vector之前，它会用＆0x0F进行掩码，因此您很可能会看到一个值为0x00000001的DWORD作为调用约定。

记录下来，尽管MSVC x64编译器通常会忽略例如**cdecl和**stdcall之类的说明符，但至少有一种方法可以获取与调用约定不同的值0x201：__vectorcall调用约定内部由值0x208表示，也就是用＆0x0F掩码，将将值为0x00000008的DWORD写入std::vector。

下面显示了负责将调用约定数据添加到std::vector中的代码。

```
XFGHelper::XFGHasher::add_function_type+17E        mov     eax, [r15+4]    ; eax = function_info-&gt;calling_convention
XFGHelper::XFGHasher::add_function_type+182        lea     r9, [rsp+48h+arg_14]
XFGHelper::XFGHasher::add_function_type+187        mov     rdx, [rbx+8]
XFGHelper::XFGHasher::add_function_type+18B        lea     r8, [rsp+48h+arg_10]
XFGHelper::XFGHasher::add_function_type+190        and     eax, 0Fh        ; eax = calling_convention &amp; 0xF
XFGHelper::XFGHasher::add_function_type+193        mov     rcx, rbx
XFGHelper::XFGHasher::add_function_type+196        mov     [rsp+48h+arg_10], eax ; value to add = calling_convention &amp; 0xF (size = dword)
XFGHelper::XFGHasher::add_function_type+196                      ; [step 4]
XFGHelper::XFGHasher::add_function_type+19A        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
```

### <a class="reference-link" name="component%205%20%EF%BC%9A%E8%BF%94%E5%9B%9E%E7%B1%BB%E5%9E%8B%E7%9A%84%E5%93%88%E5%B8%8C"></a>component 5 ：返回类型的哈希

在XFGHelper::XFGHasher::add_function_type中未检索将用于获取函数原型哈希的数据的第五个也是最后一个组成部分；相反，它是在返回后立即添加的。如下面的代码所示，它调用XFGHelper::XFGHasher::add_type，该函数为表示返回类型的Type_t计算一个8字节的哈希值，并将哈希值的8字节添加到std::vector中。

```
XFGHelper__ComputeHash_1+BE        call    XFGHelper::XFGHasher::add_function_type(Type_t const *,XFGHelper::VirtualInfoFromDeclspec)
XFGHelper__ComputeHash_1+C3        mov     rdx, rsi        ; rdx = function-&gt;return_type (struct Type_t *)
XFGHelper__ComputeHash_1+C6        mov     rcx, rbp        ; this
XFGHelper__ComputeHash_1+C9        call    XFGHelper::XFGHasher::add_type(Type_t const *) ; (step 5)
```

### <a class="reference-link" name="%E6%9C%80%E5%90%8E%E4%B8%80%E6%AD%A5:%E5%93%88%E5%B8%8C%E6%94%B6%E9%9B%86%E5%88%B0%E7%9A%84%E5%8E%9F%E5%9E%8B%E6%95%B0%E6%8D%AE"></a>最后一步:哈希收集到的原型数据

如果该函数包含来自__declspec的virtual信息，则从该信息中生成一个额外的8字节类型哈希并添加到std::vector中。然而，在测试期间，我无法达到这种特殊情况。如前所述，virtual信息可能不适用于C代码。

无论是否存在来自**declspec的virtual信息，XFGHelper**ComputeHash_1函数都将通过调用XFGHelper::XFGHasher::get_hash函数来完成：

```
XFGHelper__ComputeHash_1+CE        test    rbx, rbx        ; contains virtual info from __declspec?
XFGHelper__ComputeHash_1+D1        jz      short loc_1801052EF
[...]
XFGHelper__ComputeHash_1+103  loc_1801052EF:
XFGHelper__ComputeHash_1+103                  mov     rcx, rbp        ; this
XFGHelper__ComputeHash_1+106                  mov     rbx, [rsp+38h+arg_0]
XFGHelper__ComputeHash_1+10B                  mov     rbp, [rsp+38h+arg_8]
XFGHelper__ComputeHash_1+110                  mov     rsi, [rsp+38h+arg_10]
XFGHelper__ComputeHash_1+115                  add     rsp, 30h
XFGHelper__ComputeHash_1+119                  pop     rdi
XFGHelper__ComputeHash_1+11A                  jmp     XFGHelper::XFGHasher::get_hash(void)
XFGHelper__ComputeHash_1+11A  XFGHelper__ComputeHash_1 endp
```

对std::vector中收集的类型数据进行哈希处理。所选择的哈希算法是SHA256，我们可以在下面的XFGHelper::XFGHasher::get_hash+5F中看到，它仅返回生成的SHA256摘要的前8个字节：

```
XFGHelper::XFGHasher::get_hash(void)      public: unsigned __int64 XFGHelper::XFGHasher::get_hash(void)const proc near
[...]
XFGHelper::XFGHasher::get_hash(void)+18        mov     dl, 3           ; algorithm_ids[3] == CALG_SHA_256
XFGHelper::XFGHasher::get_hash(void)+1A        lea     rcx, [rsp+58h+hHash] ; phHash
XFGHelper::XFGHasher::get_hash(void)+1F        call    HashAPIWrapper::HashAPIWrapper(uchar)
XFGHelper::XFGHasher::get_hash(void)+24        nop
XFGHelper::XFGHasher::get_hash(void)+25        mov     r8, [rbx+8]
XFGHelper::XFGHasher::get_hash(void)+29        sub     r8, [rbx]       ; dwDataLen
XFGHelper::XFGHasher::get_hash(void)+2C        xor     r9d, r9d        ; dwFlags
XFGHelper::XFGHasher::get_hash(void)+2F        mov     rdx, [rbx]      ; pbData
XFGHelper::XFGHasher::get_hash(void)+32        mov     rcx, [rsp+58h+hHash] ; hHash
XFGHelper::XFGHasher::get_hash(void)+37        call    cs:__imp_CryptHashData
XFGHelper::XFGHasher::get_hash(void)+3D        test    eax, eax
XFGHelper::XFGHasher::get_hash(void)+3F        jnz     short loc_180105822
[...]
XFGHelper::XFGHasher::get_hash(void)+4A   loc_180105822:
XFGHelper::XFGHasher::get_hash(void)+4A        mov     r8d, 20h ; ' '  ; unsigned int
XFGHelper::XFGHasher::get_hash(void)+50        lea     rdx, [rsp+58h+sha256_digest] ; unsigned __int8 *
XFGHelper::XFGHasher::get_hash(void)+55        lea     rcx, [rsp+58h+hHash] ; this
XFGHelper::XFGHasher::get_hash(void)+5A        call    HashAPIWrapper::GetHash(uchar *,ulong)
XFGHelper::XFGHasher::get_hash(void)+5F        mov     rbx, qword ptr [rsp+58h+sha256_digest] ; *** only returns first 8 bytes of SHA256 hash
XFGHelper::XFGHasher::get_hash(void)+64        mov     rcx, [rsp+58h+hHash] ; hHash
XFGHelper::XFGHasher::get_hash(void)+69        call    cs:__imp_CryptDestroyHash
XFGHelper::XFGHasher::get_hash(void)+6F        test    eax, eax
XFGHelper::XFGHasher::get_hash(void)+71        jnz     short loc_180105854
[...]
XFGHelper::XFGHasher::get_hash(void)+7C   loc_180105854:
XFGHelper::XFGHasher::get_hash(void)+7C        mov     rax, rbx
XFGHelper::XFGHasher::get_hash(void)+7F        mov     rcx, [rsp+58h+var_10]
XFGHelper::XFGHasher::get_hash(void)+84        xor     rcx, rsp        ; StackCookie
XFGHelper::XFGHasher::get_hash(void)+87        call    __security_check_cookie
XFGHelper::XFGHasher::get_hash(void)+8C        add     rsp, 50h
XFGHelper::XFGHasher::get_hash(void)+90        pop     rbx
XFGHelper::XFGHasher::get_hash(void)+91        retn
```



## 哈希类型

到目前为止，我们知道函数原型哈希是基于5条信息构建的。其中三个是普通值（参数数量，一个布尔值，表示函数是否可变参数，以及一个数字，表示正在使用的调用约定），而其他两个本身就是类型哈希（每个函数参数的类型哈希，以及返回类型的哈希值）。在本节中，我们将看到如何对类型（由编译器内部使用Type_t对象表示）进行哈希处理。

类型是在XFGHelper::XFGHasher::add_type函数中哈希的。它调用XFGHelper__GetHashForType，该函数返回该类型的8字节哈希，然后通过调用std::vector::_Insert_range()，将该8字节哈希存储在std::vector中。

```
.text:00000001801056A0 public: void XFGHelper::XFGHasher::add_type(class Type_t const *) proc near
.text:00000001801056A0 arg_0           = qword ptr  8
.text:00000001801056A0 arg_8           = byte ptr  10h
.text:00000001801056A0
.text:00000001801056A0        push    rbx
.text:00000001801056A2        sub     rsp, 30h
.text:00000001801056A6        mov     rbx, rcx
.text:00000001801056A9        mov     rcx, rdx        ; rcx = Type_t
.text:00000001801056AC        call    XFGHelper__GetHashForType
.text:00000001801056B1        mov     rdx, [rbx+8]
.text:00000001801056B5        lea     r9, [rsp+38h+arg_8]
.text:00000001801056BA        lea     r8, [rsp+38h+arg_0]
.text:00000001801056BF        mov     [rsp+38h+arg_0], rax ; value to add = hash (qword)
.text:00000001801056C4        mov     rcx, rbx
.text:00000001801056C7        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
.text:00000001801056CC        add     rsp, 30h
.text:00000001801056D0        pop     rbx
.text:00000001801056D1        retn
```

让我们看看XFGHelper**GetHashForType如何为指定的Type_t生成一个8字节的哈希。首先，它通过对std::Tree ::emplace（）的调用来检查指定类型的哈希是否已存在于它所保存的缓存中，在XFGHelper**GetHashForType + AF上可以看到该调用。如果是这种情况，它只返回缓存的类型哈希；这样，它避免了一遍又一遍地计算已经计算出的类型的哈希值。

另一方面，如果在缓存中未找到类型哈希，它将继续通过调用XFGHelper::XFGTypeHasher::compute_hash从头开始计算哈希，该哈希将使用要哈希的类型数据构建std::vector，最后调用XFGHelper::XFGHasher::get_hash，正如我们在上一节中介绍，它会生成SHA256摘要数据包含在std::vector中，并仅返回摘要的前8个字节。

```
XFGHelper__GetHashForType      XFGHelper__GetHashForType proc near
[...]
XFGHelper__GetHashForType+A3        lea     r9, [rbp+arg_8]
XFGHelper__GetHashForType+A7        lea     r8, [rbp+Type_t]
XFGHelper__GetHashForType+AB        lea     rdx, [rbp+xfg_type_hasher]
XFGHelper__GetHashForType+AF        call    std::_Tree&lt;std::_Tmap_traits&lt;Type_t const *,unsigned __int64,std::less&lt;Type_t const *&gt;,std::allocator&lt;std::pair&lt;Type_t const * const,unsigned __int64&gt;&gt;,0&gt;&gt;::_Emplace&lt;Type_t const * &amp;,int&gt;(Type_t const * &amp;,int &amp;&amp;)
XFGHelper__GetHashForType+B4        mov     rbx, qword ptr [rbp+xfg_type_hasher]
XFGHelper__GetHashForType+B8        cmp     byte ptr [rbp+xfg_type_hasher+8], 0 ; hash for type was found in cache?
XFGHelper__GetHashForType+BC        jz      short loc_18010544D ; if so, just return the cached hash
XFGHelper__GetHashForType+BE        xor     edi, edi        ; otherwise, compute the hash of the type
XFGHelper__GetHashForType+C0        xorps   xmm0, xmm0
XFGHelper__GetHashForType+C3        movdqu  [rbp+xfg_type_hasher], xmm0
XFGHelper__GetHashForType+C8        and     [rbp+var_10], rdi
XFGHelper__GetHashForType+CC        mov     [rbp+var_8], 1
XFGHelper__GetHashForType+D0        mov     rdx, [rbp+Type_t] ; struct Type_t *
XFGHelper__GetHashForType+D4        lea     rcx, [rbp+xfg_type_hasher] ; this
XFGHelper__GetHashForType+D8        call    XFGHelper::XFGTypeHasher::compute_hash(Type_t const *)
XFGHelper__GetHashForType+DD        nop
XFGHelper__GetHashForType+DE        cmp     [rbp+var_8], dil
XFGHelper__GetHashForType+E2        jz      short loc_180105434
XFGHelper__GetHashForType+E4        lea     rcx, [rbp+xfg_type_hasher] ; this
XFGHelper__GetHashForType+E8        call    XFGHelper::XFGHasher::get_hash(void)
[...]
```

以下是XFGHelper::XFGTypeHasher::compute_hash收集的关于指定类型的信息：
- 1.从类型限定符获得的1字节值(从Type_t对象的偏移量4获取);
- 2.1个字节表示类型(指针、联合/结构体/枚举或原始类型);
- 3.某些特定类型的数据，取决于2中提到的三种类型中的哪一种(指针、联合/结构体/枚举或原始类型)属于该类型。
我们将在下面的小节中深入研究这三个信息的细节。

### <a class="reference-link" name="component%201%EF%BC%9A%E7%B1%BB%E5%9E%8B%E9%99%90%E5%AE%9A%E7%AC%A6"></a>component 1：类型限定符

关于类型的第一个信息是它的限定符，它作为一个DWORD存储在Type_t对象的偏移量4处。具体来说，关于const (0x800)和volatile (0x40)限定符的信息被组合成一个字节，写入std::vector。这个新字节的第一个位表示const限定符是否存在，第二个位表示volatile限定符是否存在。

```
XFGHelper::XFGTypeHasher::compute_hash+1B        call    Type_t::getFirstNonArrayType(void)
XFGHelper::XFGTypeHasher::compute_hash+20        mov     rcx, rdi        ; this
XFGHelper::XFGTypeHasher::compute_hash+23        mov     r8d, [rax+4]    ; r8d = Type_t-&gt;qualifiers
XFGHelper::XFGTypeHasher::compute_hash+27        shr     r8d, 0Bh
XFGHelper::XFGTypeHasher::compute_hash+2B        and     r8b, 1
XFGHelper::XFGTypeHasher::compute_hash+2F        movzx   r9d, r8b        ; r9d = (Type_t-&gt;qualifiers &gt;&gt; 0xB) &amp; 1 (has_const_qualifier)
XFGHelper::XFGTypeHasher::compute_hash+33        call    Type_t::getFirstNonArrayType(void)
XFGHelper::XFGTypeHasher::compute_hash+38        lea     r8, [rbp+arg_0]
XFGHelper::XFGTypeHasher::compute_hash+3C        mov     edx, [rax+4]    ; edx = Type_t-&gt;qualifiers
XFGHelper::XFGTypeHasher::compute_hash+3F        mov     al, r9b         ; al = has_const_qualifier
XFGHelper::XFGTypeHasher::compute_hash+42        or      al, 2           ; al = has_const_qualifier | 2
XFGHelper::XFGTypeHasher::compute_hash+44        and     dl, 40h         ; dl = Type_t-&gt;qualifiers &amp; 0x40 (has_volatile_qualifier)
XFGHelper::XFGTypeHasher::compute_hash+47        movzx   ecx, al         ; qualifiers_info = has_const_qualifier | 2
XFGHelper::XFGTypeHasher::compute_hash+4A        mov     rdx, [rbx+8]
XFGHelper::XFGTypeHasher::compute_hash+4E        cmovz   ecx, r9d        ; if it doesn't have volatile qualifier, then
XFGHelper::XFGTypeHasher::compute_hash+4E                     ; qualifiers_info = has_const_qualifier
XFGHelper::XFGTypeHasher::compute_hash+52        lea     r9, [rbp+arg_1]
XFGHelper::XFGTypeHasher::compute_hash+56        mov     [rbp+arg_0], cl ; value to insert (size = byte)
XFGHelper::XFGTypeHasher::compute_hash+59        mov     rcx, rbx
XFGHelper::XFGTypeHasher::compute_hash+5C        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)

```

### <a class="reference-link" name="Component%202:%20%E7%B1%BB%E5%9E%8B%E7%BB%84"></a>Component 2: 类型组

如果存储在Type_t中的类型值设置了0x100，那么它是一个指针。这是通过向std::vector写入一个值为3的字节来表示的。

```
XFGHelper::XFGTypeHasher::compute_hash+61        test    dword ptr [rdi], 100h ; *Type_t &amp; 0x100 == 0 ?
XFGHelper::XFGTypeHasher::compute_hash+67        jz      short loc_180105762
XFGHelper::XFGTypeHasher::compute_hash+69        mov     rdx, [rbx+8]    ; if not, it's a pointer
XFGHelper::XFGTypeHasher::compute_hash+6D        lea     r9, [rbp+arg_1]
XFGHelper::XFGTypeHasher::compute_hash+71        lea     r8, [rbp+arg_0]
XFGHelper::XFGTypeHasher::compute_hash+75        mov     [rbp+arg_0], 3  ; value to insert: POINTER_TYPE (3)
XFGHelper::XFGTypeHasher::compute_hash+79        mov     rcx, rbx
XFGHelper::XFGTypeHasher::compute_hash+7C        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
```

如果该类型不是指针，则通过检查Type_t &amp; 0x600中存储的类型值是否不为0来检查该类型是联合、结构还是枚举。注意，0x600是建立在0x200 | 0x400之上的，其中0x200标识枚举类型，0x400标识结构和联合。如果是这种情况，一个值为2的字节被写入std::vector。

```
XFGHelper::XFGTypeHasher::compute_hash+8E   loc_180105762:
XFGHelper::XFGTypeHasher::compute_hash+8E        test    dword ptr [rdi], 600h ; *Type_t &amp; (0x400 | 0x200) == 0 ?
XFGHelper::XFGTypeHasher::compute_hash+94        jz      short loc_180105790
XFGHelper::XFGTypeHasher::compute_hash+96        mov     rdx, [rbx+8]    ; if not, it's a union/struct/enum
XFGHelper::XFGTypeHasher::compute_hash+9A        lea     r9, [rbp+arg_1]
XFGHelper::XFGTypeHasher::compute_hash+9E        lea     r8, [rbp+arg_0]
XFGHelper::XFGTypeHasher::compute_hash+A2        mov     [rbp+arg_0], 2  ; value to insert: UNION_STRUCT_OR_ENUM_TYPE (2)
XFGHelper::XFGTypeHasher::compute_hash+A6        mov     rcx, rbx
XFGHelper::XFGTypeHasher::compute_hash+A9        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
```

最后，如果类型不是指针，也不是union/struct/enum，则采用默认情况。如果该类型是泛型，那么不会向std::vector写入任何内容(但这是一种边界情况，只影响设置为0x1000的类型和标识为0x8103的类型)。否则，对于绝大多数基本类型，值为1的字节被添加到std::vector中。

```
XFGHelper::XFGTypeHasher::compute_hash+BC   loc_180105790:
XFGHelper::XFGTypeHasher::compute_hash+BC        mov     rcx, rdi        ; this
XFGHelper::XFGTypeHasher::compute_hash+BF        call    Type_t::isGeneric(void)
XFGHelper::XFGTypeHasher::compute_hash+C4        test    al, al
XFGHelper::XFGTypeHasher::compute_hash+C6        jz      short loc_1801057A2
XFGHelper::XFGTypeHasher::compute_hash+C8        mov     byte ptr [rbx+18h], 0
XFGHelper::XFGTypeHasher::compute_hash+CC        jmp     short epilog
XFGHelper::XFGTypeHasher::compute_hash+CE   loc_1801057A2:
XFGHelper::XFGTypeHasher::compute_hash+CE        mov     rdx, [rbx+8]
XFGHelper::XFGTypeHasher::compute_hash+D2        lea     r9, [rbp+arg_1]
XFGHelper::XFGTypeHasher::compute_hash+D6        lea     r8, [rbp+arg_0]
XFGHelper::XFGTypeHasher::compute_hash+DA        mov     [rbp+arg_0], 1  ; value to insert: PRIMITIVE_TYPE (1)
XFGHelper::XFGTypeHasher::compute_hash+DE        mov     rcx, rbx
XFGHelper::XFGTypeHasher::compute_hash+E1        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
```

### <a class="reference-link" name="Component%203:%20%E6%8C%87%E9%92%88%E7%B1%BB%E5%9E%8B%E7%9A%84%E5%93%88%E5%B8%8C"></a>Component 3: 指针类型的哈希

对于指针类型，在将值为3的字节写入std::vector后，将调用XFGHelper::XFGTypeHasher::hash_indirection函数。记住，这里的指针定义要广泛一些，因为它包含了所有那些值为0x100的Type_t对象。除了常规C指针外，它还包括一种内部函数对象(由函数指针引用)和数组。

```
XFGHelper::XFGTypeHasher::compute_hash+81        mov     rdx, rdi        ; struct Type_t *
XFGHelper::XFGTypeHasher::compute_hash+84        mov     rcx, rbx        ; this
XFGHelper::XFGTypeHasher::compute_hash+87        call    XFGHelper::XFGTypeHasher::hash_indirection
XFGHelper::XFGTypeHasher::compute_hash+8C        jmp     short epilog
```

顾名思义，函数XFGHelper::XFGTypeHasher::hash_indirection将指针引用的类型的哈希值添加到std::vector。它的行为取决于它所处理的指针的类型:
<li>如果它是一个函数指针(Type_t值为0x106)或普通指针Type_t值为0x102(用于大多数类型的指针,函数指针除外),它添加的哈希Type_t通过调用指针引用XFGHelper::XFGHasher::add_type,外加一个值为2的字节。在函数指针的情况下，指针引用的Type_t是一种Type_t值为0x101的内部函数对象，也就是说它也在XFGHelper::XFGTypeHasher::hash_indirection中处理。
<pre><code class="lang-c++ hljs cpp">XFGHelper::XFGTypeHasher::hash_indirection+15        mov     ecx, [rdx]      ; ecx = *Type_t
XFGHelper::XFGTypeHasher::hash_indirection+17        mov     eax, ecx
XFGHelper::XFGTypeHasher::hash_indirection+19        and     eax, 10Fh
[...]
XFGHelper::XFGTypeHasher::hash_indirection+25        sub     eax, 1          ; case 0x102 (general pointer):
XFGHelper::XFGTypeHasher::hash_indirection+28        jz      short loc_1801058E3
[...]
XFGHelper::XFGTypeHasher::hash_indirection+2F        cmp     eax, 3          ; case 0x106 (function pointer):
XFGHelper::XFGTypeHasher::hash_indirection+32        jz      short loc_1801058E3
[...]
XFGHelper::XFGTypeHasher::hash_indirection+6B   loc_1801058E3:
XFGHelper::XFGTypeHasher::hash_indirection+6B        mov     dil, 2          ; will be written to std::vector
XFGHelper::XFGTypeHasher::hash_indirection+6E        jmp     short loc_1801058F6
[...]
XFGHelper::XFGTypeHasher::hash_indirection+7E   loc_1801058F6:
XFGHelper::XFGTypeHasher::hash_indirection+7E        mov     rdx, [rsi+8]    ; rdx = ptr to the Type_t referenced by the pointer
XFGHelper::XFGTypeHasher::hash_indirection+7E                     ; (return type in the case of functions)
XFGHelper::XFGTypeHasher::hash_indirection+82        mov     rcx, rbx        ; this
XFGHelper::XFGTypeHasher::hash_indirection+85        call    XFGHelper::XFGHasher::add_type
XFGHelper::XFGTypeHasher::hash_indirection+8A        mov     rdx, [rbx+8]
XFGHelper::XFGTypeHasher::hash_indirection+8E        lea     r9, [rsp+38h+arg_8+1]
XFGHelper::XFGTypeHasher::hash_indirection+93        lea     r8, [rsp+38h+arg_8]
XFGHelper::XFGTypeHasher::hash_indirection+98        mov     byte ptr [rsp+38h+arg_8], dil ; value to insert (size = byte)
XFGHelper::XFGTypeHasher::hash_indirection+9D        mov     rcx, rbx
XFGHelper::XFGTypeHasher::hash_indirection+A0        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
</code></pre>
如果它是一个函数对象（由Type_t值为0x101标识，通常由Type_t值为0x106的函数指针引用），则通过调用XFGHelper::XFGHasher::add_function_type函数来添加函数原型的哈希，其内部工作原理我们已经剖析了函数的返回类型的哈希值，加一个字节值为1。
<pre><code class="lang-c++ hljs cpp">XFGHelper::XFGTypeHasher::hash_indirection+17        mov     eax, ecx
XFGHelper::XFGTypeHasher::hash_indirection+19        and     eax, 10Fh
XFGHelper::XFGTypeHasher::hash_indirection+1E        sub     eax, 101h       ; case 0x101 (function):
XFGHelper::XFGTypeHasher::hash_indirection+23        jz      short loc_1801058E8
[...]
XFGHelper::XFGTypeHasher::hash_indirection+70        xor     r8d, r8d
XFGHelper::XFGTypeHasher::hash_indirection+73        mov     rcx, rbx
XFGHelper::XFGTypeHasher::hash_indirection+76        mov     dil, 1          ; this is written to std::vector at the end of this function
XFGHelper::XFGTypeHasher::hash_indirection+79        call    XFGHelper::XFGHasher::add_function_type(Type_t const *,XFGHelper::VirtualInfoFromDeclspec)
XFGHelper::XFGTypeHasher::hash_indirection+7E
XFGHelper::XFGTypeHasher::hash_indirection+7E   loc_1801058F6:
XFGHelper::XFGTypeHasher::hash_indirection+7E                     ; XFGHelper::XFGTypeHasher::hash_indirection+6E↑j
XFGHelper::XFGTypeHasher::hash_indirection+7E        mov     rdx, [rsi+8]    ; rdx = ptr to the Type_t referenced by the pointer
XFGHelper::XFGTypeHasher::hash_indirection+7E                     ; (return type in the case of functions)
XFGHelper::XFGTypeHasher::hash_indirection+82        mov     rcx, rbx        ; this
XFGHelper::XFGTypeHasher::hash_indirection+85        call    XFGHelper::XFGHasher::add_type
XFGHelper::XFGTypeHasher::hash_indirection+8A        mov     rdx, [rbx+8]
XFGHelper::XFGTypeHasher::hash_indirection+8E        lea     r9, [rsp+38h+arg_8+1]
XFGHelper::XFGTypeHasher::hash_indirection+93        lea     r8, [rsp+38h+arg_8]
XFGHelper::XFGTypeHasher::hash_indirection+98        mov     byte ptr [rsp+38h+arg_8], dil ; value to insert (size = byte)
XFGHelper::XFGTypeHasher::hash_indirection+9D        mov     rcx, rbx
XFGHelper::XFGTypeHasher::hash_indirection+A0        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
</code></pre>
</li>
最后，如果它是一个数组(由Type_t值0x103标识)，它将写入一个包含数组中元素数量的QWORD，加上数组元素类型的散列，再加上一个字节值为6。

```
XFGHelper::XFGTypeHasher::hash_indirection+15        mov     ecx, [rdx]      ; ecx = *Type_t
XFGHelper::XFGTypeHasher::hash_indirection+17        mov     eax, ecx
XFGHelper::XFGTypeHasher::hash_indirection+19        and     eax, 10Fh
[...]
XFGHelper::XFGTypeHasher::hash_indirection+2A        sub     eax, 1          ; case 0x103 (array passed by pointer):
XFGHelper::XFGTypeHasher::hash_indirection+2D        jz      short loc_1801058B2
[...]
XFGHelper::XFGTypeHasher::hash_indirection+3A   loc_1801058B2:
XFGHelper::XFGTypeHasher::hash_indirection+3A        lea     eax, [rcx-4103h]
XFGHelper::XFGTypeHasher::hash_indirection+40        mov     dil, 6          ; will be written to std::vector
XFGHelper::XFGTypeHasher::hash_indirection+43        test    eax, 0FFFFBFFFh
XFGHelper::XFGTypeHasher::hash_indirection+48        jz      short loc_1801058AC
XFGHelper::XFGTypeHasher::hash_indirection+4A        mov     rax, [rdx+10h]  ; rax = number of elems in array
XFGHelper::XFGTypeHasher::hash_indirection+4E        lea     r9, [rsp+38h+arg_10]
XFGHelper::XFGTypeHasher::hash_indirection+53        mov     rdx, [rbx+8]
XFGHelper::XFGTypeHasher::hash_indirection+57        lea     r8, [rsp+38h+arg_8]
XFGHelper::XFGTypeHasher::hash_indirection+5C        mov     rcx, rbx
XFGHelper::XFGTypeHasher::hash_indirection+5F        mov     [rsp+38h+arg_8], rax ; value to insert: number of elems in array (size = qword)
XFGHelper::XFGTypeHasher::hash_indirection+64        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
XFGHelper::XFGTypeHasher::hash_indirection+69        jmp     short loc_1801058F6
[...]
XFGHelper::XFGTypeHasher::hash_indirection+7E   loc_1801058F6
XFGHelper::XFGTypeHasher::hash_indirection+7E        mov     rdx, [rsi+8]    ; rdx = ptr to the Type_t referenced by the pointer
XFGHelper::XFGTypeHasher::hash_indirection+7E                     ; (return type in the case of functions)
XFGHelper::XFGTypeHasher::hash_indirection+82        mov     rcx, rbx        ; this
XFGHelper::XFGTypeHasher::hash_indirection+85        call    XFGHelper::XFGHasher::add_type
XFGHelper::XFGTypeHasher::hash_indirection+8A        mov     rdx, [rbx+8]
XFGHelper::XFGTypeHasher::hash_indirection+8E        lea     r9, [rsp+38h+arg_8+1]
XFGHelper::XFGTypeHasher::hash_indirection+93        lea     r8, [rsp+38h+arg_8]
XFGHelper::XFGTypeHasher::hash_indirection+98        mov     byte ptr [rsp+38h+arg_8], dil ; value to insert (size = byte)
XFGHelper::XFGTypeHasher::hash_indirection+9D        mov     rcx, rbx
XFGHelper::XFGTypeHasher::hash_indirection+A0        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)

```

**union/struct/enum类型的哈希**

当处理union/struct/enum后写一个字节值为2的std::vector，函数XFGHelper:: XFGTypeHasher::compute_hash调用XFGHelper::XFGTypeHasher::hash_tag,在RDX指针作为参数传递给Symbol_t对象包含可读名称union/struct/enum类型。

```
XFGHelper::XFGTypeHasher::compute_hash+AE        mov     rdx, [rdi+10h]  ; struct Symbol_t *
XFGHelper::XFGTypeHasher::compute_hash+B2        mov     rcx, rbx        ; this
XFGHelper::XFGTypeHasher::compute_hash+B5        call    XFGHelper::XFGTypeHasher::hash_tag(Symbol_t *)
```

XFGHelper::XFGTypeHasher::hash_tag调用XFGHelper::XFGHasher::add_string，它将union/struct/enum的名称添加到std::vector对象中(如果union/struct/enum是一个命名的)。相反，如果union/struct/enum是匿名的，它会将字符串”&lt;unnamed&gt;“添加到std::vector中。

```
XFGHelper::XFGHasher::add_string      public: void XFGHelper::XFGHasher::add_string(class Symbol_t *) proc near
XFGHelper::XFGHasher::add_string           sub     rsp, 38h
XFGHelper::XFGHasher::add_string+4         cmp     byte ptr [rdx+11h], 4
XFGHelper::XFGHasher::add_string+8         jnz     short loc_18010568B
XFGHelper::XFGHasher::add_string+A         mov     r8, [rdx]
XFGHelper::XFGHasher::add_string+D         mov     eax, [r8+10h]
XFGHelper::XFGHasher::add_string+11        shr     eax, 16h
XFGHelper::XFGHasher::add_string+14        test    al, 1           ; union/struct/enum is named?
XFGHelper::XFGHasher::add_string+16        jz      short loc_180105674
XFGHelper::XFGHasher::add_string+18        lea     r9, aUnnamed+9  ; ""
XFGHelper::XFGHasher::add_string+1F        lea     r8, aUnnamed    ; "&lt;unnamed&gt;"
XFGHelper::XFGHasher::add_string+26
XFGHelper::XFGHasher::add_string+26   loc_180105666:
XFGHelper::XFGHasher::add_string+26        mov     rdx, [rcx+8]
XFGHelper::XFGHasher::add_string+2A        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
XFGHelper::XFGHasher::add_string+2F        add     rsp, 38h
XFGHelper::XFGHasher::add_string+33        retn
XFGHelper::XFGHasher::add_string+34   ; ---------------------------------------------------------------------------
XFGHelper::XFGHasher::add_string+34
XFGHelper::XFGHasher::add_string+34   loc_180105674:
XFGHelper::XFGHasher::add_string+34        mov     r8, [r8+8]      ; r8 = union/struct/enum name
XFGHelper::XFGHasher::add_string+38        or      r9, 0FFFFFFFFFFFFFFFFh
XFGHelper::XFGHasher::add_string+3C
XFGHelper::XFGHasher::add_string+3C   loc_18010567C:
XFGHelper::XFGHasher::add_string+3C        inc     r9
XFGHelper::XFGHasher::add_string+3F        cmp     byte ptr [r8+r9], 0
XFGHelper::XFGHasher::add_string+44        jnz     short loc_18010567C
XFGHelper::XFGHasher::add_string+46        add     r9, r8          ; r9 points to end of string
XFGHelper::XFGHasher::add_string+49        jmp     short loc_180105666
```

之后，函数XFGHelper::XFGTypeHasher::hash_tag中有一个分支代码，可以在某些情况下将字符串“&lt;local&gt;”添加到要哈希的数据中。我对此没有进行太多研究，但它可能处理了局部范围的union/struct/enum的情况。

```
XFGHelper::XFGTypeHasher::hash_tag+4D        mov     rbx, [rbx+18h]
XFGHelper::XFGTypeHasher::hash_tag+51        test    rbx, rbx
XFGHelper::XFGTypeHasher::hash_tag+54        jnz     short loc_180105A16
XFGHelper::XFGTypeHasher::hash_tag+56        jmp     short loc_180105A76
XFGHelper::XFGTypeHasher::hash_tag+58   ; ---------------------------------------------------------------------------
XFGHelper::XFGTypeHasher::hash_tag+58
XFGHelper::XFGTypeHasher::hash_tag+58   loc_180105A5C:
XFGHelper::XFGTypeHasher::hash_tag+58        mov     rdx, [rdi+8]
XFGHelper::XFGTypeHasher::hash_tag+5C        lea     r9, aLocal+7    ; ""
XFGHelper::XFGTypeHasher::hash_tag+63        lea     r8, aLocal      ; "&lt;local&gt;"
XFGHelper::XFGTypeHasher::hash_tag+6A        mov     rcx, rdi
XFGHelper::XFGTypeHasher::hash_tag+6D        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
```

**原始类型的哈希**

在处理原始类型(Type_t值中没有0x100、0x200或0x400的类型)时，在将值为1的字节写入std::vector后，XFGHelper::XFGTypeHasher::compute_hash函数调用XFGHelper::XFGTypeHasher::hash_primitive函数。

XFGHelper::XFGTypeHasher::hash_primitive基本上是一个大的switch语句，它把Type_t值映射到另一组表示primitive类型的常量。得到的常量(一个字节)然后被添加到std::vector中。例如，对于由Type_t 0x26表示的浮点类型，该函数将一个值为0x0B的字节添加到std::vector。

```
XFGHelper::XFGTypeHasher::hash_primitive      private: void XFGHelper::XFGTypeHasher::hash_primitive(class Type_t const *) proc near
XFGHelper::XFGTypeHasher::hash_primitive           sub     rsp, 38h
XFGHelper::XFGTypeHasher::hash_primitive+4         mov     eax, [rdx]
XFGHelper::XFGTypeHasher::hash_primitive+6         mov     r10, rcx
XFGHelper::XFGTypeHasher::hash_primitive+9         and     eax, 1FFFh
XFGHelper::XFGTypeHasher::hash_primitive+E         cmp     eax, 40h ; '@'
XFGHelper::XFGTypeHasher::hash_primitive+11        ja      loc_1801059D4
XFGHelper::XFGTypeHasher::hash_primitive+17        jz      loc_1801059D0   ; case 0x40:
XFGHelper::XFGTypeHasher::hash_primitive+1D        cmp     eax, 1Ah
XFGHelper::XFGTypeHasher::hash_primitive+20        ja      short loc_18010599E
[...]
XFGHelper::XFGTypeHasher::hash_primitive+6E   loc_18010599E:
XFGHelper::XFGTypeHasher::hash_primitive+6E        sub     eax, 1Bh        ; case 0x1B:
XFGHelper::XFGTypeHasher::hash_primitive+71        jz      short loc_1801059CC
XFGHelper::XFGTypeHasher::hash_primitive+73        sub     eax, 1          ; case 0x1C:
XFGHelper::XFGTypeHasher::hash_primitive+76        jz      short loc_1801059C8
XFGHelper::XFGTypeHasher::hash_primitive+78        sub     eax, 2          ; case 0x1E:
XFGHelper::XFGTypeHasher::hash_primitive+7B        jz      short loc_1801059C4
XFGHelper::XFGTypeHasher::hash_primitive+7D        sub     eax, 8          ; case 0x26 (float):
XFGHelper::XFGTypeHasher::hash_primitive+80        jz      short loc_1801059C0
[...]
XFGHelper::XFGTypeHasher::hash_primitive+90   loc_1801059C0:
XFGHelper::XFGTypeHasher::hash_primitive+90        mov     cl, 0Bh         ; primitive_type = 0xB (float)
XFGHelper::XFGTypeHasher::hash_primitive+92        jmp     short loc_1801059DE
[...]
XFGHelper::XFGTypeHasher::hash_primitive+AE   loc_1801059DE:
XFGHelper::XFGTypeHasher::hash_primitive+AE        mov     rdx, [r10+8]
XFGHelper::XFGTypeHasher::hash_primitive+B2        lea     r9, [rsp+38h+arg_9]
XFGHelper::XFGTypeHasher::hash_primitive+B7        mov     [rsp+38h+arg_8], cl ; value to add: primitive_type
XFGHelper::XFGTypeHasher::hash_primitive+BB        lea     r8, [rsp+38h+arg_8]
XFGHelper::XFGTypeHasher::hash_primitive+C0        mov     rcx, r10
XFGHelper::XFGTypeHasher::hash_primitive+C3        call    std::vector&lt;uchar&gt;::_Insert_range&lt;uchar const *&gt;(std::_Vector_const_iterator&lt;std::_Vector_val&lt;std::_Simple_types&lt;uchar&gt;&gt;&gt;,uchar const *,uchar const *,std::forward_iterator_tag)
```



## 哈希的最终转换

到目前为止，我们已经深入描述了C编译器前端如何为XFG计算函数原型的哈希。如果我们必须用一些类似于python的伪代码来总结它，我们可以说函数的哈希是这样构建的:

```
hash =  sha256(number_of_params +

              type_hash(params[0]) +
              type_hash(params[...]) +
              type_hash(params[n]) +

              is_variadic +

              calling_convention +

              type_hash(return_type)
        )[0:8]
```

XFG函数哈希是SHA256摘要的截断版本（仅保留了前8个字节），因此与完整的SHA256散列相比，它们的抗冲突性降低了，但是我们可以预计不同的XFG哈希可以合理地哈希函数的雪崩效应看起来不相关的,对吧?

但是，如果在给定的二进制文件上检查了一组XFG哈希（我选择了ntdll.dll），您会注意到它们似乎没有64位熵：

```
function 0x180001a30 -&gt; prototype hash: 0x8d952e0d365aa071
function 0x180001b50 -&gt; prototype hash: 0xe2198f4a3c515871
function 0x180001dc0 -&gt; prototype hash: 0xbeac2e06165fc871
function 0x180001de0 -&gt; prototype hash: 0xfaec0e7f70d92371
function 0x180001fc0 -&gt; prototype hash: 0xc5d11eb750d75871
function 0x180002030 -&gt; prototype hash: 0xe8bcaf9a10586871
function 0x180002040 -&gt; prototype hash: 0xc3110f087e584871
function 0x1800020b0 -&gt; prototype hash: 0xdbc1261858d2f871
function 0x1800023a0 -&gt; prototype hash: 0xda690f3e36531a71
```

这背后的原因是编译器前端(c1.dll)生成截断的SHA256哈希在实际写入结果文件对象之前接受编译器后端(c2.dll)的最终转换。更准确地说，c2.dll中的XfgIlVisitor::visit_I_XFG_HASH函数对截断的SHA256哈希应用两个掩码:

```
XfgIlVisitor::visit_I_XFG_HASH(tagILMAP *)+5B        mov     rcx, 8000060010500070h
XfgIlVisitor::visit_I_XFG_HASH(tagILMAP *)+65        mov     r13, 0FFFDBFFF7EDFFB70h
[...]
XfgIlVisitor::visit_I_XFG_HASH(tagILMAP *)+E9        mov     rdx, [rax]      ; rdx = 8 bytes of SHA256 hash
XfgIlVisitor::visit_I_XFG_HASH(tagILMAP *)+EC        add     rax, 8
XfgIlVisitor::visit_I_XFG_HASH(tagILMAP *)+F0        and     rdx, r13        ; hash &amp;= 0FFFDBFFF7EDFFB70h
XfgIlVisitor::visit_I_XFG_HASH(tagILMAP *)+F3        mov     [rbx], rax
XfgIlVisitor::visit_I_XFG_HASH(tagILMAP *)+F6        or      rdx, rcx        ; hash |= 8000060010500070h
XfgIlVisitor::visit_I_XFG_HASH(tagILMAP *)+F9        mov     ecx, r9d        ; this
XfgIlVisitor::visit_I_XFG_HASH(tagILMAP *)+FC        call    XFG::TiSetHash(ulong,unsigned __int64,tagMOD *)
```

这就是为什么XFG哈希尽管是基于SHA256看起来也不完全随机的原因。不过，我不知道为什么要使用这些掩码。



## 手动哈希计算练习

为了验证我们已经正确理解了如何生成XFG哈希，让我们尝试手动计算XFG哈希。假设我们要使用以下原型计算函数的哈希值：

```
void  * memcpy （
   void  * dest ，
   const  void  * src ，
   size_t  count 
）;
```

我们需要找出构成函数原型的5条数据：
- 1.参数数量；
- 2.为每个参数输入哈希值；
- 3.是否具有可变参函数？
- 4.调用约定；
- 5.返回类型的哈希值。
1、3和4都很简单：
- 1.参数数量-&gt; DWORD，值为3；
- 3.是可变函数吗？-&gt;值为0的字节；
- 4.调用约定-&gt;默认值（DWORD值为0x201＆0xF == 0x1）。
因此，让我们计算更复杂的部分：每个参数类型的哈希，以及返回类型的哈希。

### <a class="reference-link" name="%E5%8F%82%E6%95%B01%E7%9A%84%E7%B1%BB%E5%9E%8B%E5%93%88%E5%B8%8C"></a>参数1的类型哈希

第一个参数的类型为void*。该类型由以下内容的Type_t表示：

```
00000102 00000200 [+ pointer to referenced Type_t]
```

我们需要找出3个数据来产生类型哈希：
- 类型限定符-&gt;值为0的字节；
- 类型组：它是一个指针-&gt;byte，值为3；
- 特定类型的数据：这是一个“通用”指针-&gt;引用类型的哈希（在这里我们有递归）+值为2的byte。
为了递归计算引用类型（void）的哈希，该类型由Type_t表示，其内容如下：

```
00000040  00000000
```

我们需要的数据构造如下：
- 类型限定符-&gt;值为0的byte；
- 类型组：它是原始类型-&gt;byte，值为1；
- 类型特定的数据：对于Type_t 0x40（void），XFGHelper::XFGTypeHasher::hash_primitive写入一个值0x0E的byte。
### <a class="reference-link" name="%E5%8F%82%E6%95%B02%E7%9A%84%E7%B1%BB%E5%9E%8B%E5%93%88%E5%B8%8C"></a>参数2的类型哈希

第二个参数的类型为const void*。该类型由以下内容的Type_t表示：

```
00000102 00000200 [+ pointer to referenced Type_t]
```

我们需要的数据构造如下：
- 类型限定符-&gt;值为0的byte；
- 类型组：它是一个指针-&gt;byte，值为3；
<li>特定类型的数据：这是一个“通用”指针-&gt;引用类型的哈希（在这里我们有递归）+值为2的byte。<br>
为了递归计算引用类型（const void）的哈希，该类型由Type_t表示，其内容如下：
<pre><code class="hljs">00000040  00000800
</code></pre>
我们需要的数据构建如下：
</li>
- 类型限定符：它具有const限定符-&gt;编码为值1的字节；
- 类型组：它是原始类型-&gt;字节，值为1；
- 类型特定的数据：对于Type_t 0x40（void）-&gt; XFGHelper::XFGTypeHasher::hash_primitive写入一个值0x0E的byte。
### <a class="reference-link" name="%E5%8F%82%E6%95%B03%E7%9A%84%E7%B1%BB%E5%9E%8B%E5%93%88%E5%B8%8C"></a>参数3的类型哈希

参数的类型为size_t。该类型由以下内容的Type_t表示：

```
00004019  00000000
```

我们需要的数据构造如下：
- 类型限定符-&gt;值为0的byte；
- 类型组：它是原始类型-&gt;byte，值为1；
- 类型特定的数据：对于Type_t 0x4019（无符号long long）-&gt; XFGHelper::XFGTypeHasher::hash_primitive写入一个值0x88的byte。
### <a class="reference-link" name="%E8%BF%94%E5%9B%9E%E7%B1%BB%E5%9E%8B%E7%9A%84%E7%B1%BB%E5%9E%8B%E5%93%88%E5%B8%8C"></a>返回类型的类型哈希

返回类型为void *，与该函数的第一个参数相同，因此在这里我们只重复之前获取的内容。
- 类型限定符-&gt;值为0的byte；
- 类型组：它是一个指针-&gt;byte，值为3；
- 特定类型的数据：这是一个“通用”指针-&gt;引用类型的哈希（在这里我们有递归）+值为2的byte。
对于引用类型（void）的哈希的递归计算：
- 类型限定符-&gt;值为0的byte；
- 类型组：它是原始类型-&gt;byte，值为1；
- 类型特定的数据：对于Type_t 0x40（void），XFGHelper::XFGTypeHasher::hash_primitive写入一个值0x0E的byte。
### <a class="reference-link" name="%E7%BB%84%E5%90%88%E5%9C%A8%E4%B8%80%E8%B5%B7"></a>组合在一起

让我们将所有数据组合在一起：

```
# Number of params
03 00 00 00

# type hash of param 1 (void *)
SHA256(
    00  #qualifiers
    03  # type group: pointer
    # type hash of referenced type (void)
    SHA256(
        00  # qualifiers
        01  # type group: primitive type
        0E  # hash of primitive type: void -&gt; 0x0E
    )[0:8]
    02  # regular pointer
)[0:8]

# type hash of param 2 (const void *)
SHA256(
    00  # qualifiers
    03  # type group: pointer
    # type hash of referenced type (const void)
    SHA256(
        01  # qualifiers: const
        01  # type group: primitive type
        0E  # hash of primitive type: void -&gt; 0x0E
    )[0:8]
    02  # regular pointer
)[0:8]

# type hash of param 3 (size_t)
SHA256(
    00  # qualifiers
    01  # type group: primitive type
    88  # hash of primitive type: unsigned long long -&gt; 0x88
)[0:8]

# is variadic
00

# calling convention
01 00 00 00

# type hash of return value (void *)
SHA256(
    00  # qualifiers
    03  # type group: pointer
    # type hash of referenced type (void)
    SHA256(
        00  # qualifiers
        01  # type group: primitive type
        0E  # hash of primitive type: void -&gt; 0x0E
    )[0:8]
    02  # regular pointer
)[0:8]
```

以下Python代码获取该数据的SHA256摘要，并将其截断为前8个字节，以获取与编译器前端发出的哈希相同的哈希。最后，它将编译器后端的两个掩码应用于最终形成的XFG哈希：

```
import struct
import hashlib

def truncated_hash(data):
    return hashlib.sha256(data).digest()[0:8]

def apply_backend_masks(hash):
    hash = hash &amp; 0xFFFDBFFF7EDFFB70
    hash = hash | 0x8000060010500070
    return hash


def main():
    # number of params
    data  = struct.pack('&lt;L', 3)
    # type hash of first param (void *)
    data += truncated_hash(b'\x00\x03' + truncated_hash(b'\x00\x01\x0e') + b'\x02')
    # type hash of second param (const void *)
    data += truncated_hash(b'\x00\x03' + truncated_hash(b'\x01\x01\x0e') + b'\x02')
    # type hash of third param (size_t)
    data += truncated_hash(b'\x00\x01\x88')
    # is variadic
    data += struct.pack('&lt;B', 0x0)
    # calling convention (default)
    data += struct.pack('&lt;L', 0x201 &amp; 0x0F)
    # type hash of return type (void *)
    data += truncated_hash(b'\x00\x03' + truncated_hash(b'\x00\x01\x0e') + b'\x02')

    print(f'Data to be hashed: `{`data`}` (`{`len(data)`}` bytes)')
    frontend_hash = struct.unpack('&lt;Q', truncated_hash(data))[0]
    print(f'Hash generated by the frontend: 0x`{`frontend_hash:x`}`')

    final_hash = apply_backend_masks(frontend_hash)
    print(f'[*] Final XFG hash: 0x`{`final_hash:x`}`')
```

该Python代码的输出如下：

```
&gt; python test.py

Data to be hashed: b'\x03\x00\x00\x00\xf5\x97x&gt;[J`\xb0\x17\x80\xb8\xc0[\x1b\xd0\xd8#\x14\xb4\xba\x91\xc7\xf6j\x00\x01\x00\x00\x00\xf5\x97x&gt;[J`\xb0' (41 bytes)

Hash generated by the frontend: 0x1da7d393d6b63a72

[*] Final XFG hash: 0x9da5979356d63a70
```

如果我们使用函数指针编译一些代码以调用其原型与本节中讨论的原型相匹配的函数，则可以看到，我们手动计算的XFG哈希与MSVC生成的哈希完全匹配。请参考在下面的反汇编中的main + 0x8E处寄存器R10的值：

```
main+1C        lea     rax, my_memcpy
main+23        mov     [rsp+78h+var_50], rax
[...]
main+6A        lea     rcx, aCallingFunctio ; "Calling function pointer...\n"
main+71        call    printf
main+76        lea     rcx, Str        ; "a test"
main+7D        call    strlen
main+82        cdqe
main+84        mov     rcx, [rsp+78h+var_50]
main+89        mov     [rsp+78h+var_48], rcx
main+8E        mov     r10, 9DA5979356D63A70h
main+98        mov     r8, rax
main+9B        lea     rdx, aATest_0   ; "a test"
main+A2        lea     rcx, [rsp+78h+var_28]
main+A7        mov     rax, [rsp+78h+var_48]
main+AC        call    cs:__guard_xfg_dispatch_icall_fptr
```



## 总结

在这篇博文中，我想分享MSVC编译器如何为C程序生成XFG哈希的所有细节。除了讨论即将到来的漏洞攻击缓解的细节之外，本文还允许深入研究编译器内部。

目前XFG只在Windows Insider Preview版本中找到，所以在CFI解决方案成为Windows 10的官方发行版之前，我们在这里介绍的内容可能会发生变化。

目前尚无答案，例如为什么编译器后端对前端生成的哈希应用两个位掩码，以及为什么哈希存储在函数启动之前设置了0位，但在XFG指令的调用位置中保留了0位。

最后，看看C++编译器前端(c1xx.dll)计算XFG哈希的方式有什么不同是很有趣的。快速浏览一下这个二进制文件就会发现，哈希算法看起来与C语言中使用的算法非常相似，但是它很可能会被修改，以考虑继承和C++类型限定符和修饰符等c++概念。

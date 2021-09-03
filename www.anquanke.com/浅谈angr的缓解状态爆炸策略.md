> 原文链接: https://www.anquanke.com//post/id/251984 


# 浅谈angr的缓解状态爆炸策略


                                阅读量   
                                **15322**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01ee28aa134236d3e3.jpg)](https://p1.ssl.qhimg.com/t01ee28aa134236d3e3.jpg)



## 前言

angr是有名的符号执行工具。众所周知，符号执行最大的问题就是状态爆炸。因此，angr中也内置了很多缓解符号执行的策略。本文主要介绍angr里的一些内置机制是如何缓解状态爆炸的。



## 概述

据我对angr的了解，angr缓解状态爆炸的策略约有以下几种：

（1）simProcedure：重写一些可能导致状态爆炸的函数。<br>
（2）veritesting：动态符号执行和静态符号执行的结合<br>
（3）Lazy Solve：跳过不必要的函数<br>
（4）Symbion：具体执行和符号执行的结合

### <a class="reference-link" name="simProcedure"></a>simProcedure

为了使得符号执行实践性更强，angr用python写的summary替换了库函数。这些summary成为Simprocedures。Simprocedures可以缓解路径爆炸，反过来也可能引入路径爆炸。比如，strlen的参数是符号字符串。

但是，angr的simprocedure并不完善。如果angr出现了预期以外的行为，可能是由于不完整的simprocedure导致的。为此，官网给出了几种解决方案：

（1）禁用simprocedure（虽然也有可能引入路径爆炸，需要限制下函数的输入）<br>
（2）写一个hook来代替其中的几个simprocedure<br>
（3）修复simprocedure

下面介绍一个simprocedure的例子

```
from angr import Project,SimProcedure
project = Project("example/fauxware/fauxware")
class BugFree(SimProcedure):
    def run(self,argc,argv):
        print("Program running with argc=%s and argv=%s" %(argc,argv))
        return 0
# 将二进制中的main函数替换为bug free函数
project.hook_symbol("main",BugFree())
simgr = project.factory.simulation_manager()
simgr.run()
```

当程序执行到main函数时，会去执行BugFree函数，就只会打印一个信息，然后返回。

当进入函数时，参数的值会从哪里进来呢？不管有多少个参数，只要定义个run函数，simprocedure就通过调用约定，自动地提取程序状态里的参数给你。返回值也是一样的，run函数的返回值也会通过调用约定放到状态里的。

事实上，最经常使用simprocedure的地方是用来替换库函数。

关于数据类型，你可能会发现run函数打印出了SAO BV64 0xSTUFF的类。这个是SimActionObject。这个只是bitvector的wrapper。他会在simprocedure里追踪。（在静态分析里很有用）

另外，也许你还会注意到run函数返回的是python的int 0，这个会被自动处理为word大小的bitvector。你可以返回一个普通的数字或者一个SimActionObject。

当你想要去写一个procedure去处理浮点数时，你需要手动指定调用约定。只需要为hook提供一个cc（调用约定）。

```
cc = project.factory.cc_from_arg_kinds((True,True),ret_fp=True)
project.hook(address, ProcedureClass(cc=mycc))
```

如何退出SimProcedure呢？我们已经知道了最简单的方法去做这个，就是从run函数返回。实际上，从run函数返回是调用了self.ret(value)。self.ret()是一个知道如何从一个函数返回的函数。

SimProcedures可使用许多不同的函数：
- ret(expr)：从函数返回
- jump(addr)：跳到二进制中的地址
- exit(code)：终止程序
- call(addr,args,continue_at)：在二进制中调用
- inline_call(procedure,*args):调用SimProcedure（inline）并返回结果
如果要在SimProcedure加个条件分支的话，需要直接在SimSuccessors那边的节点上添加。

```
self.successors.add_successor(state,addr,guard,jumpkind)
```

如果我们调用二进制中的一个函数，并且在SimProcedure后重新执行呢？有个叫SimProcedure Continuation的框架可以实现这个。当你使用self.call(addr,args,continue_at) ，其中addr是你需要call的地址，args是需要调用的函数的参数的元组，continue_at是另外一个simProcedure的方法。

下面来看看一个例子，这个例子是将所有共享库初始化的例子，来实现一个full_init_state。initializers是一个初始化队列。每次从里头去一个共享库的地址，然后执行self.call。如果初始化队列为空，则跳转到程序的entry执行。

```
class LinuxLoader(angr.SimProcedure):
    NO_RET = True
    IS_FUNCTION = True
    local_vars = ('initializers',)

    def run(self):
        self.initializers = self.project.loader.initializers
        self.run_initializer()

    def run_initializer(self):
        if len(self.initializers) == 0:
            self.project._simos.set_entry_register_values(self.state)
            self.jump(self.project.entry)
        else:
            addr = self.initializers[0]
            self.initializers = self.initializers[1:]
            self.call(addr, (self.state.posix.argc, self.state.posix.argv, self.state.posix.environ), 'run_initializer')
```

hook symbols，可以使用符号表直接来进行hook。比如，要替换rand函数为一个具体的列表值，可以用以下代码实现。

```
&gt;&gt;&gt; class NotVeryRand(SimProcedure):
...     def run(self, return_values=None):
...         rand_idx = self.state.globals.get('rand_idx', 0) % len(return_values)
...         out = return_values[rand_idx]
...         self.state.globals['rand_idx'] = rand_idx + 1
...         return out

&gt;&gt;&gt; project.hook_symbol('rand', NotVeryRand(return_values=[413, 612, 1025, 1111]))
```

user hooks，除了hook 库函数以外，也可以hook二进制中的普通函数。例子如下，0x1234是函数的地址。length参数控制程序的控制流。在函数执行完这个例子后，下一步就是从hooked的地址的5个字节后面开始执行。

```
&gt;&gt;&gt; @project.hook(0x1234, length=5)
... def set_rax(state):
...     state.regs.rax = 1
```

### <a class="reference-link" name="Veritesting"></a>Veritesting

Veritesting方法来源于论文Enhancing Symbolic Execution with veritesting，论文作者是mayhem的团队。

论文链接见此：[https://dl.acm.org/doi/pdf/10.1145/2927924](https://dl.acm.org/doi/pdf/10.1145/2927924)

AngrCTF的第12个挑战，就是关于如何使用angr的veritesting模式来缓解路径爆炸。只需要在新建simulation_manager对象时，加上veritesting的参数就可以了。

```
simulation = project.factory.simgr(initial_state, veritesting=True)
```

简单说下这个veritesting的原理。

从高层面来说，有两种符号执行，一种是动态符号执行（Dynamic Symbolic Execution，简称DSE），另一种是静态符号执行（Static Symbolic Execution，简称SSE）。动态符号执行会去执行程序然后为每一条路径生成一个表达式。而静态符号执行将程序转换为表达式，每个表达式都表示任意条路径的属性。基于路径的DSE在生成表达式上引入了很多的开销，然而生成的表达式很容易求解。而SSE虽然生成表达式容易，但是表达式难求解。veritesting就是在这二者中做权衡，使得能够在引入低开销的同时，生成较易求解的表达式。

先来看个简单的例子，下面的7行代码中，有着2^100次条可能的执行路径。每条路径都要DSE单独地去分析，从而使得实现100%的覆盖率是不太现实的。实际上，只要两个测试样例，就可以达到100%的路径覆盖率。一个包含75个B的字符串和一个没有B的字符串。然而，在2的100次方状态空间里找到这两个测试样例是很难的。

[![](https://p3.ssl.qhimg.com/t01e596dd2dbc155258.png)](https://p3.ssl.qhimg.com/t01e596dd2dbc155258.png)

veritest只要47s就能到达bug函数，而其他的符号执行工具比如klee，S2E，Mayhem使用状态合并的策略跑1个小时，都没跑完。Veritest从DSE开始，一旦遇到一些简单的代码，就切换到SSE的模式。简单的代码指的是不含系统调用，间接跳转或者其他很难精确推断的语句。在SSE模式下，首先动态恢复控制流图，找到SSE容易分析的语句和难以分析的语句。然后SSE算法推断出从易分析的节点到难分析节点路径的影响。最后，Veritesting切换回DSE模式去处理静态不好解决的情况。

### <a class="reference-link" name="lazy"></a>lazy

这个思路有点像chopped symbolic execution论文里提到的。论文地址：[https://dl.acm.org/doi/abs/10.1145/3180155.3180251](https://dl.acm.org/doi/abs/10.1145/3180155.3180251)

论文里是在klee实现的，开源于：[https://github.com/davidtr1037/chopper](https://github.com/davidtr1037/chopper)

在angr里也有类似的操作，只需要设置状态为LAZY_SOLVES就可以了。

```
s = proj.factory.entry_state(add_options=`{`angr.options.LAZY_SOLVES`}`)
```

依然简单说下原理。拿论文中的例子，下面的程序是libtasn1库里的代码片段。第8行的get_length()函数会导致堆溢出。整体是一个while循环。这个函数会去用get_length去获取当前数据的长度。get_length函数会去扫描输入字符串，并且转为ASN.1 域。然后注意14行，会去递归地迭代执行。或者触发第11行的append_value函数。这个函数会在AST上创建节点。然后还会去多次扫描输入的字符串，检查多次元素，并分配内存给节点。这里会产生状态爆炸主要是由于多次的嵌套调用，只符号执行函数get_length(get_length的参数为长度为n的字符串)，会导致4*n条不同路径。函数append_value会调用多次求解器，同样也会影响符号执行引擎的效率。最后导致无法发现第8行的堆溢出漏洞。

[![](https://p3.ssl.qhimg.com/t01639cf930fa6a9fc0.png)](https://p3.ssl.qhimg.com/t01639cf930fa6a9fc0.png)

lazy solves就是应对这种情况而诞生的。它的核心思想是执行过程中的大部分函数和漏洞实际上并不相关。就好比这个程序里，漏洞是由于21行的剩下字节的错误更新导致当调用get_length时会有内存越界读。也就是说这个bug很构造ASN.1表示的那些函数没啥关系（比如append_value）。因此，我们可以快速的跳过这些不相关的函数。

Lazy Solves策略实际上是在符号执行过程中先跳过函数调用。如果遇到的漏洞点和前面的函数有依赖关系，再会去求解相关的函数的依赖。由于漏洞只和一小部分函数有关联，所以这种策略在一定程度上缓解了状态爆炸。

### <a class="reference-link" name="Symbion"></a>Symbion

Symbion来自论文：SYMBION: Interleaving Symbolic with Concrete Execution

他的核心思想主要是在具体执行和符号执行相互切换的一个过程。他的应用场景特别适合：假设只需要符号执行一个程序的特定函数，但是到这个函数前有很多初始化的步骤想要跳过。因为这些步骤和分析无关或者angr不能很合适地模拟。比如，程序是运行在一个嵌入式系统上，而你有访问debug接口的权限，但不太容易复现硬件的环境。

这里的例子是angr博客里的，下面的代码有四个恶意行为。所有这些行为依赖于硬编码的配置。我们可以在地址0x400cd6看到配置的使用方法：二进制里第一个做决定的点。

[![](https://p1.ssl.qhimg.com/t01e0e45217ec10969d.png)](https://p1.ssl.qhimg.com/t01e0e45217ec10969d.png)

我们的目标是要去分析二进制的恶意行为以及如何触发它们。我们可以看到第二个payload在基本块400d6a处，我们如何到达它？还有基本块0x400d99呢？这就是符号执行要做的事情。

思路是让binary自动unpack，并且具体执行到0x400cd6的地方，然后同步状态到angr，然后定义一个符号变量，去符号化探索后面的程序。

然而，这个二进制是packed的，并且内存会被unpacking 进程覆盖。软件的断点都会被覆盖。所以我们手动逆向二进制，并且确定了我们可以从程序的开始运行到0x85b853，to have a new stub available at 0x45b97f。最终就等待4个断点在那个地址命中，我们就可以获取在400cd6的unpacked code了。

下面的代码是官方给出的示例。我也试着跑了一下，但由于avatar2和某些angr的库不兼容，最后跑出来的结果和github里的某个issue一样。

```
import subprocess
import os
import nose
import avatar2 as avatar2

import angr
import claripy
from angr_targets import AvatarGDBConcreteTarget


# First set everything up
binary_x64 = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                          os.path.join('..', '..', 'binaries',
                                          'tests','x86_64',
                                          'packed_elf64'))

# Spawning of the gdbserver analysis environment(这里GDB_SERVER_IP和PORT应该要自己设置)
print("gdbserver %s:%s %s" % (GDB_SERVER_IP,GDB_SERVER_PORT,binary_x64))
subprocess.Popen("gdbserver %s:%s %s" % (GDB_SERVER_IP,GDB_SERVER_PORT,binary_x64),
                  stdout=subprocess.PIPE,
                  stderr=subprocess.PIPE,
                  shell=True)

# Instantiation of the AvatarGDBConcreteTarget
avatar_gdb = AvatarGDBConcreteTarget(avatar2.archs.x86.X86_64,
                                     GDB_SERVER_IP, GDB_SERVER_PORT)

# Creation of the project with the new attributes 'concrete_target'
p = angr.Project(binary_x64, concrete_target=avatar_gdb,
                             use_sim_procedures=True)
# 从entry开始使用具体执行
entry_state = p.factory.entry_state()
entry_state.options.add(angr.options.SYMBION_SYNC_CLE)
entry_state.options.add(angr.options.SYMBION_KEEP_STUBS_ON_SYNC)

simgr = p.factory.simgr(state)

## Now, let's the binary unpack itself（concrete execution）
simgr.use_technique(angr.exploration_techniques.Symbion(find=[0x85b853]))
exploration = simgr.run()
new_concrete_state = exploration.stashes['found'][0]

# 为啥这样可以找到unpack code ？ confusing
# Hit the new stub 4 times before having our unpacked code at 0x400cd6
for i in xrange(0,4):
    simgr = p.factory.simgr(new_concrete_state)
    simgr.use_technique(angr.exploration_techniques.Symbion(find=[0x85b853]))
    exploration = simgr.run()
    new_concrete_state = exploration.stashes['found'][0]

## Reaching the first decision point
#获取了unpack code后，开始去找符号执行开始的地方
simgr = p.factory.simgr(new_concrete_state)
simgr.use_technique(angr.exploration_techniques.Symbion(find=[0x400cd6])
exploration = simgr.run()
new_concrete_state = exploration.stashes['found'][0]
# 定义符号化的参数，并把符号化的变量存到相应的内存区域
# Declaring a symbolic buffer
arg0 = claripy.BVS('arg0', 8*32)

# The address of the symbolic buffer would be the one of the
# hardcoded malware configuration
symbolic_buffer_address = new_concrete_state.regs.rbp-0xc0

# Setting the symbolic buffer in memory!
new_concrete_state.memory.store(symbolic_buffer_address, arg0) 
simgr = p.factory.simgr(new_concrete_state)

print("[2]Symbolically executing binary to find dropping of second stage" +
       "[ address:  " + hex(DROP_STAGE2_V2) + " ]")
# 符号执行
# Symbolically explore the malware to find a specific behavior by avoiding
# evasive behaviors
exploration = simgr.explore(find=DROP_STAGE2_V2, avoid=[DROP_STAGE2_V1,
                                                       VENV_DETECTED, FAKE_CC ])
# Get our synchronized state back!
new_symbolic_state = exploration.stashes['found'][0] 
print("[3]Executing binary concretely with solution found until the end " +
hex(BINARY_EXECUTION_END))

simgr = p.factory.simgr(new_symbolic_state)
# 具体执行到结尾
# Concretizing the solution to reach the interesting behavior in the memory
# of the concrete process and resume until the end of the execution.
simgr.use_technique(angr.exploration_techniques.Symbion(find=[BINARY_EXECUTION_END],
                              memory_concretize = [(symbolic_buffer_address,arg0)], 
                              register_concretize=[]))

exploration = simgr.run()
# 求解的结果
new_concrete_state = exploration.stashes['found'][0]
```

总的来说，代码可以划分为以下几个步骤：

（1）从entry开始具体执行到0x85b853。（困惑这里的0x85b853是啥？）

（2）连续具体执行四次，终点依然是0x85b853（获取unpacked code？）

（3）具体执行到0x400dc6（决策点的位置）

（4） 从0x400dc6开始符号执行到DROP_STAGE2_V2

（5）再具体执行到结尾，同时把符号化的地址具体化。



## 总结

angr里可能还有其他缓解状态爆炸的思路，比如driller，这里我就没有展开来讲。也可以发现，在缓解状态爆炸的路上，通常都是结合了多种方法来实现的。在各种程序分析技术中切换，或许是未来符号执行发展的路线。

参考资料
<li>Simprocedure：（1）angr CTF：[http://angr.oregonctf.org/](http://angr.oregonctf.org/)
</li>
<li>Veritesting（1）论文：[https://dl.acm.org/doi/pdf/10.1145/2927924](https://dl.acm.org/doi/pdf/10.1145/2927924)
（2）angr CTF 第12个挑战：[https://ycdxsb.cn/eefc86dd.html](https://ycdxsb.cn/eefc86dd.html)
</li>
<li>Lazy Solve（1）论文：[https://dl.acm.org/doi/abs/10.1145/3180155.3180251](https://dl.acm.org/doi/abs/10.1145/3180155.3180251)
（2）其他开源工具：[https://github.com/davidtr1037/chopper](https://github.com/davidtr1037/chopper)
</li>
<li>Symbion相关（1）官方文档：[https://docs.angr.io/advanced-topics/symbion](https://docs.angr.io/advanced-topics/symbion)
（2）论文：[https://ieeexplore.ieee.org/abstract/document/9162164](https://ieeexplore.ieee.org/abstract/document/9162164)
（3）博客：[http://angr.io/blog/angr_symbion/](http://angr.io/blog/angr_symbion/)
</li>
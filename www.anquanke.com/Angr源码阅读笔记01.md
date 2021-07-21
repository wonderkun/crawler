> 原文链接: https://www.anquanke.com//post/id/231460 


# Angr源码阅读笔记01


                                阅读量   
                                **160882**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t017513e9b074aa4f12.jpg)](https://p4.ssl.qhimg.com/t017513e9b074aa4f12.jpg)



## 零、前言

​ 很早之前写了一个系列的文章叫《Angr-CTF从入门到精通》获得了不错的反响，随着大三上课程的结束，本人又投入了科研项目工作中，重新开始了对自动化二进制漏洞检测与利用的工程中，想着针对最新的Angr版本大致简单介绍一下Angr的源码，其中参考了一些前辈的工作，但我主要是想从另外一个角度进行条理化的解析，这个系列大致也可以叫《Angr源码阅读从入门到精通》，目前最后的想法是开发一个将符号执行与模糊测试相结合的框架，有点类似Driller软件

​ Angr框架的分析对象是二进制程序，不依赖程序源码，支持x86/64、ARM/AArch64，MIPS等多个架构，之前的版本更新还引入了Java的支持。Angr除了实现符号执行分析之外，还实现了控制流分析、数据依赖分析、后向切片、库函数识别等其他静态分析技术

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t011641fe9c7b25f671.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0121a05c8aeeb296c4.png)

​ Angr框架的总体架构包含如下几个部分：
- 加载器—CLE：用于解析加载二进制文件，识别文件格式，从ELF/PE头中提取架构、代码段和数据段等程序信息
- 架构数据库—Archinfo：根据程序架构信息，加载对应的CPU架构模型，包括寄存器、位宽、大小端等数据
- 翻译器—PyVEX：将程序机器码翻译成中间语言VEX，VEX是开源二进制插桩工具Valgrind所使用的中间语言，angr需要处理不同的架构，所以它选择一种中间语言来进行它的分析
- 模拟执行引擎—SimEngine：对VEX指令进行解释执行，支持具体值执行和符号值执行，执行时支持自定义函数Hook和断点，支持自定义路径探索策略
- 约束求解器—Claripy：将符号执行中生成的路径约束转化成SMT公式，使用Z3进行求解
- OS模拟器—SimOS：用于模拟程序与系统环境交互，提供了许多模拟的libc函数和系统调用，用户也可以自行编写Hook函数进行模拟
​ 虽然Angr即支持具体执行也支持符号执行，但实际上Angr默认只支持静态符号执行，不支持动态符号执行。Angr的路径探索策略默认使用广度优先策略，通过用户设置的目的地址（find）和避免到达的地址（avoid）来减少待探索的路径，此外Angr也支持深度优先策略和其他的策略。不过由于Angr的可拓展性很强，因此可以自定义探索路径的具体规则，实现一种近似于动态符号执行的路径探索策略

​ 在实际中，Fuzz测试缺少纵深，对于大规模深度高的复杂工程应用根本没有办法展开相关测试工作，如果要对大规模的应用工程中重复打桩，又降低了Fuzz的测试效率，倘若将大程序分拆未各个模块，模块又拆分，这样的话对于跨组件跨模块的复杂问题又无法发现。且Fuzz只能挖掘的漏洞大部分是运行时显示异常的漏洞，而现实中真正存在威胁的漏洞都是非显式的异常，且源代码分析检测工具已经将很多问题解决，Fuzz发挥的实际效果其实比较有限。总的来说Fuzz对于复杂应用也存在自动化程度低，复杂逻辑与复杂场景的漏洞无法检测，不能针对特定路径的特定漏洞做针对性的检测等问题

​ 在目前的我所接触过的在实际中的应用环境下，符号执行一般是与模糊测试和污点分析等共同协作，符号执行负责对测试数据进行分析与优化，生成新的测试数据，使得模糊测试fuzz引擎能突破程序的浅层，不断探索未覆盖的路径分支

​ Fuzz依赖类似于KLEE或者Angr之类的符号执行技术提供覆盖率更好的路径和约束，来提供路径的覆盖率和精准定位路径的能力，这个的确是Fuzz技术发展和改进的方向。但正如我之前看同事的文章所言，目前采用的二进制分析方式做符号执行，在此基础上做路径分析，这样的情况适合于源代码不能提供的场景，也许更适合于病毒分析等恶意程序分析，但是在正常公司开发过程中没有源代码的情况还是比较少见的。且二进制代码没有源代码的高级语言结构化特征和类型特征，对于高级分析还是比较困难的

​ 在现在的国际大环境中，各种情况都有可能发生，网络安全就是国家安全，而网络安全十分依赖于对漏洞情况的掌握，而我国目前还没有一款真正属于自己的自动化漏洞挖掘工具。且超越国家而言，对于目前的技术发展情况而言，自动化漏洞挖掘，或者说漏洞挖掘工具还有很长的一条路要走，希望各位读者中阅读了本人的拙劣的文章能有所获得，推动我们整个技术向前发展

​ 阅读Angr源码不只是学习Angr这一种框架，更多是理解符号执行的整个周期流程的设计思维，可以举一反三，设计出更好的框架

​ 本人的测试系统环境如下，学习符号执行建议使用大内存机器：
- CPU：AMD Ryzen 3700U
- RAM：32GB
- OS：Ubuntu 20.04 LTS
- Angr Version：v9.0.5610
​ 我自己也曾在基于华为云的鲲鹏AMR服务器上建构了相关的Docker镜像环境，可以直接使用：

```
$ docker pull zeroaone2099/angr-aarch64:v1.0
```

​ Git仓库地址：
- [Angr-CTF从入门到精通](https://github.com/ZERO-A-ONE/AngrCTF_FITM)
- [Angr源码解析](https://gitee.com/zeroaone/comments-on-angr-source-code.git)


## 一、启航

​ 本文章主要面向已经有过Angr使用的读者，如果有读者想知道Angr的基础用法可以移步至我之前写过的《Angr-CTF从入门到精通》，我们从一个最简单的Angr的例子开始我们的Angr源码阅读之路：

```
import angr
import sys
def Go():
    path_to_binary = "./00_angr_find"
    project = angr.Project(path_to_binary, auto_load_libs=False)
    initial_state = project.factory.entry_state()
    simulation = project.factory.simgr(initial_state)

    print_good_address = 0x8048678  
    simulation.explore(find=print_good_address)

    if simulation.found:
        solution_state = simulation.found[0]
        solution = solution_state.posix.dumps(sys.stdin.fileno())
        print("[+] Success! Solution is: `{``}`".format(solution.decode("utf-8")))
    else:
        raise Exception('Could not find the solution')
if __name__ == "__main__":
    Go()
```

我们不难发现每个Angr项目都是从类似这一行代码开始的

```
project = angr.Project(path_to_binary, auto_load_libs=False)
```

​ 使用 angr的首要步骤就是创建Project加载二进制文件。angr的二进制装载组件是CLE，它负责装载二进制对象（以及它依赖的任何库）和把这个对象以易于操作的方式交给angr的其他组件。angr将这些包含在Project类中。一个Project类是代表了你的二进制文件的实体。你与angr的大部分操作都会经过它

​ 我们就将从启动开始的Project类开始我们的Angr源码探索之旅



## 二、一切的开始-Project类

​ 我们首先从源码文档的`_init_.py`开始看：

```
from .project import *
```

​ 我们可以发现Project类是从源码文档的`project`文件里导入进来的，现在我们去`project`文件里查看一下

```
class Project:
def __init__(self, thing,
                 default_analysis_mode=None,
                 ignore_functions=None,
                 use_sim_procedures=True,
                 exclude_sim_procedures_func=None,
                 exclude_sim_procedures_list=(),
                 arch=None, simos=None,
                 engine=None,
                 load_options: Dict[str, Any]=None,
                 translation_cache=True,
                 support_selfmodifying_code=False,
                 store_function=None,
                 load_function=None,
                 analyses_preset=None,
                 concrete_target=None,
                 **kwargs):
...
```

​ 在源文件的第49行我们就发现了关于Project类的定义，这里引用一下源码的说明：

```
"""
    This is the main class of the angr module. It is meant to contain a set of binaries and the relationships between
    them, and perform analyses on them.

    :param thing:                       The path to the main executable object to analyze, or a CLE Loader object.

    The following parameters are optional.
    :param default_analysis_mode:       The mode of analysis to use by default. Defaults to 'symbolic'.
    :param ignore_functions:            A list of function names that, when imported from shared libraries, should never be stepped into in analysis (calls will return an unconstrained value).
    :param use_sim_procedures:          Whether to replace resolved dependencies for which simprocedures are available with said simprocedures.
    :param exclude_sim_procedures_func: A function that, when passed a function name, returns whether or not to wrap
                                        it with a simprocedure.
    :param exclude_sim_procedures_list: A list of functions to *not* wrap with simprocedures.
    :param arch:                        The target architecture (auto-detected otherwise).
    :param simos:                       a SimOS class to use for this project.
    :param engine:                      The SimEngine class to use for this project.
    :param bool translation_cache:      If True, cache translated basic blocks rather than re-translating them.
    :param support_selfmodifying_code:  Whether we aggressively support self-modifying code. When enabled, emulation will try to read code from the current state instead of the original memory, regardless of the current memory protections.
    :type support_selfmodifying_code:   bool
    :param store_function:              A function that defines how the Project should be stored. Default to pickling.
    :param load_function:               A function that defines how the Project should be loaded. Default to unpickling.
    :param analyses_preset:             The plugin preset for the analyses provider (i.e. Analyses instance).
    :type analyses_preset:              angr.misc.PluginPreset

    Any additional keyword arguments passed will be passed onto ``cle.Loader``.

    :ivar analyses:     The available analyses.
    :type analyses:     angr.analysis.Analyses
    :ivar entry:        The program entrypoint.
    :ivar factory:      Provides access to important analysis elements such as path groups and symbolic execution results.
    :type factory:      AngrObjectFactory
    :ivar filename:     The filename of the executable.
    :ivar loader:       The program loader.
    :type loader:       cle.Loader
    :ivar storage:      Dictionary of things that should be loaded/stored with the Project.
    :type storage:      defaultdict(list)
    """

```

### <a class="reference-link" name="2.1%20%E5%8F%82%E6%95%B0%E5%88%86%E6%9E%90"></a>2.1 参数分析

​ 我们优先关注一下Project类的构造函数的参数：
- thing： 要分析的主要可执行对象的路径，或CLE Loader对象，这个是必须指定的参数
​ 以下是可选的参数列表：
- default_analysis_mode：默认使用的分析模式， 默认为 ‘symbolic’
- ignore_functions：是一个函数名称列表，当从共享库导入后，列表里的这些函数不会被进入分析（调用将返回一个非约束值），简单来说就是传入一个要忽略的函数列表
> 默认情况下，angr 会使用 `SimProcedures` 中的符号摘要替换库函数，即设置 Hooking，这些 python 函数摘要高效地模拟库函数对状态的影响，以下简称sim，可以设置参数 `exclude_sim_procedures_list` 和 `exclude_sim_procedures_func` 指定不想被 `SimProcedure` 替代的符号
- use_sim_procedures：是否使用符号摘要替换库函数，默认是开启的，但是因为sim是模拟库函数可能存在精确度和准确性问题
- exclude_sim_procedures_func：不需要被替换的库函数
- exclude_sim_procedures_list：不用sim替换的函数列表
- arch：目标架
<li>simos：确定 guest OS。创建了一个 `angr.SimOS` 或者其子类实例有以下定义：
<ul>
- SimLinux
- SimWindows
- SimCGC
- SimJavaVM
- SimUserland
> angr使用一系列引擎（SimEngine的子类）来模拟被执行代码对输入状态产生的影响。源码位于 angr/engines 目录下
<li>engine：指定要使用的SimEngine引擎类型：
<ul>
<li>| 名称 | 描述 |<br>
| ———————— | —————————————————————————————— |<br>
| `failure engine` | kicks in when the previous step took us to some uncontinuable state |<br>
| `syscall engine` | kicks in when the previous step ended in a syscall |<br>
| `hook engine` | kicks in when the current address is hooked |<br>
| `unicorn engine` | kicks in when the `UNICORN` state option is enabled and there is no symbolic data in the state |<br>
| `VEX engine` | kicks in as the final fallback. |</li>
​ 在之后所有的参数将传递给加载器CLE类的Loader方法，angr 中的 CLE 模块用于将二进制文件载入虚拟地址空间，而CLE 最主要的接口就是 loader 类，在我们讲到CLE模块的时候，我们会深入解析它

​ 通过 loader, 我们可以获得二进制文件的共享库、地址空间等信息，类似这样

```
&gt;&gt;&gt; proj.loader
&lt;Loaded true, maps [0x400000:0x5004000]&gt;
&gt;&gt;&gt; proj.loader.shared_objects
OrderedDict([('true', &lt;ELF Object true, maps [0x400000:0x60721f]&gt;), ('libc.so.6', &lt;ELF Object libc-2.27.so, maps [0x1000000:0x13f0adf]&gt;), ('ld-linux-x86-64.so.2', &lt;ELF Object ld-2.27.so, maps [0x2000000:0x222916f]&gt;)])
&gt;&gt;&gt; proj.loader.min_addr
&gt;&gt;&gt; proj.loader.max_addr
```

​ 下面我们使用一个简单的例子来一起学习angr的构造过程：

​ 测试源码：

```
#include&lt;stdio.h&gt;
int main()`{`
    printf("Hi!Angr!\n");
    return 0;
`}`
```

​ 编译指令：

```
$ gcc 01.c -no-pie -g -o tes
```

​ 一个Project有一些基础属性：它的CPU架构、文件名、入口地址

```
&gt;&gt;&gt; proj.arch
&lt;Arch AMD64 (LE)&gt;
&gt;&gt;&gt; proj.entry
4198480
&gt;&gt;&gt; proj.filename
'./test'
```

​ 接下来我们解析Project构造函数的执行流程

### <a class="reference-link" name="2.2%20%E6%9E%84%E9%80%A0%E5%87%BD%E6%95%B0"></a>2.2 构造函数

#### <a class="reference-link" name="2.2.1%20%E7%AC%AC%E4%B8%80%E6%AD%A5"></a>2.2.1 第一步

```
# Step 1: Load the binary

        if load_options is None: load_options = `{``}`

        load_options.update(kwargs)
        if arch is not None:
            load_options.update(`{`'arch': arch`}`)
        if isinstance(thing, cle.Loader):
            if load_options:
                l.warning("You provided CLE options to angr but you also provided a completed cle.Loader object!")
            self.loader = thing
            self.filename = self.loader.main_object.binary
        elif hasattr(thing, 'read') and hasattr(thing, 'seek'):
            l.info("Loading binary from stream")
            self.filename = None
            self.loader = cle.Loader(thing, **load_options)
        elif not isinstance(thing, str) or not os.path.exists(thing) or not os.path.isfile(thing):
            raise Exception("Not a valid binary file: %s" % repr(thing))
        else:
            # use angr's loader, provided by cle
            l.info("Loading binary %s", thing)
            self.filename = thing
            self.loader = cle.Loader(self.filename, concrete_target=concrete_target, **load_options)
```

​ 我们可以发现首先是在加载二进制文件，也就是对我们输入的二进制文件就行初始化处理，最终目的式获得一个 `cle.Loader` 实例

​ isinstance() 函数来判断一个对象是否是一个已知的类型，类似 type()

> isinstance() 与 type() 区别：
<ul>
- type() 不会认为子类是一种父类类型，不考虑继承关系
- isinstance() 会认为子类是一种父类类型，考虑继承关系
</ul>
如果要判断两个类型是否相同推荐使用 isinstance()

​ 首先对加载的 `thing` 做判断，如果是一个 `cle.loader` 类实例，则将其设置为 `self.loader` 成员变量；否则如果是一个流，或者是一个二进制文件，则创建一个新的 `cle.Loader`。然后该 project 被放入字典 `projects`（从流加载的除外）

​ 二进制的装载组建是CLE（CLE Load Everything)，它负责装载二进制对象以及它所依赖的库，将自身无法执行的操作转移给angr的其它组件，最后生成地址空间，表示该程序已加载并可以准备运行

​ `cle.loader`代表着将整个程序映射到某个地址空间，而地址空间的每个对象都可以由一个加载器后端加载，例如`cle.elf`用于加载linux的32位程序

​ 总而言之通过loader来查看二进制文件加载的共享库，以及执行对加载地址空间相关的基本查询

```
&gt;&gt;&gt; proj.loader
&lt;Loaded test, maps [0x400000:0xa07fff]&gt;
&gt;&gt;&gt; proj.loader.shared_objects
OrderedDict(
[('test', &lt;ELF Object test, maps [0x400000:0x404037]&gt;),
('libc.so.6', &lt;ELF Object libc-2.31.so, maps [0x500000:0x6f14d7]&gt;),
('ld-linux-x86-64.so.2', &lt;ELF Object ld-2.31.so, maps [0x700000:0x72f18f]&gt;), ('extern-address space', &lt;ExternObject Object cle##externs, maps [0x800000:0x87ffff]&gt;), 
('cle##tls', &lt;ELFTLSObjectV2 Object cle##tls, maps [0x900000:0x91500f]&gt;)])
&gt;&gt;&gt; proj.loader.all_objects
[&lt;ELF Object test, maps [0x400000:0x404037]&gt;,
&lt;ELF Object libc-2.31.so, maps [0x500000:0x6f14d7]&gt;,
&lt;ELF Object ld-2.31.so, maps [0x700000:0x72f18f]&gt;, 
&lt;ExternObject Object cle##externs, maps [0x800000:0x87ffff]&gt;, 
&lt;ELFTLSObjectV2 Object cle##tls, maps [0x900000:0x91500f]&gt;,
&lt;KernelObject Object cle##kernel, maps [0xa00000:0xa07fff]&gt;]
&gt;&gt;&gt; hex(proj.loader.max_addr)
'0xa07fff'
&gt;&gt;&gt; hex(proj.loader.min_addr)
'0x400000'
```

​ 还可以检查一些程序是否开启保护方式

```
&gt;&gt;&gt; proj.loader.main_object.execstack
False
&gt;&gt;&gt; proj.loader.main_object.pic
False
```

#### <a class="reference-link" name="2.2.2%20%E7%AC%AC%E4%BA%8C%E6%AD%A5"></a>2.2.2 第二步

```
# Step 2: determine its CPU architecture, ideally falling back to CLE's guess
        if isinstance(arch, str):
            self.arch = archinfo.arch_from_id(arch)  # may raise ArchError, let the user see this
        elif isinstance(arch, archinfo.Arch):
            self.arch = arch # type: archinfo.Arch
        elif arch is None:
            self.arch = self.loader.main_object.arch
        else:
            raise ValueError("Invalid arch specification.")
```

​ 这里就是判断二进制文件的 CPU 架构，如果是自己指定，则从 archinfo 里匹配，否则从 `self.loader` 获取

> archinfo是一个Python的第三方库用来判断二进制文件的目标架构

#### <a class="reference-link" name="2.2.3%20%E7%AC%AC%E4%B8%89%E6%AD%A5"></a>2.2.3 第三步

```
# Step 3: Set some defaults and set the public and private properties
        if not default_analysis_mode:
            default_analysis_mode = 'symbolic'
        if not ignore_functions:
            ignore_functions = []

        if isinstance(exclude_sim_procedures_func, types.LambdaType):
            l.warning("Passing a lambda type as the exclude_sim_procedures_func argument to "
                      "Project causes the resulting object to be un-serializable.")

        self._sim_procedures = `{``}`

        self.concrete_target = concrete_target

        # It doesn't make any sense to have auto_load_libs
        # if you have the concrete target, let's warn the user about this.
        if self.concrete_target and load_options.get('auto_load_libs', None):

            l.critical("Incompatible options selected for this project, please disable auto_load_libs if "
                       "you want to use a concrete target.")
            raise Exception("Incompatible options for the project")

        if self.concrete_target and self.arch.name not in ['X86', 'AMD64', 'ARMHF']:
            l.critical("Concrete execution does not support yet the selected architecture. Aborting.")
            raise Exception("Incompatible options for the project")

        self._default_analysis_mode = default_analysis_mode
        self._exclude_sim_procedures_func = exclude_sim_procedures_func
        self._exclude_sim_procedures_list = exclude_sim_procedures_list
        self.use_sim_procedures = use_sim_procedures
        self._ignore_functions = ignore_functions
        self._support_selfmodifying_code = support_selfmodifying_code
        self._translation_cache = translation_cache
        self._executing = False # this is a flag for the convenience API, exec() and terminate_execution() below

        if self._support_selfmodifying_code:
            if self._translation_cache is True:
                self._translation_cache = False
                l.warning("Disabling IRSB translation cache because support for self-modifying code is enabled.")

        self.entry = self.loader.main_object.entry
        self.storage = defaultdict(list)
        self.store_function = store_function or self._store
        self.load_function = load_function or self._load
```

​ 这里就是对相关的默认、公共和私有属性进行设置，我们可以首先发现对默认使用的分析模式和需要忽略替换的函数列表

```
if not default_analysis_mode:
    default_analysis_mode = 'symbolic'
if not ignore_functions:
    ignore_functions = []
```

​ 之后的内容就是在对属性做检查，和对未基于特定值的参数使用缺省值

#### <a class="reference-link" name="2.2.4%20%E7%AC%AC%E5%9B%9B%E6%AD%A5"></a>2.2.4 第四步

```
# Step 4: Set up the project's hubs
        # Step 4.1 Factory
        self.factory = AngrObjectFactory(self, default_engine=engine)

        # Step 4.2: Analyses
        self._analyses_preset = analyses_preset
        self.analyses = None
        self._initialize_analyses_hub()

        # Step 4.3: ...etc
        self.kb = KnowledgeBase(self, name="global")
```

​ 这里第四步主要是设置Project的各种插件，我们之前说到过CLE模块将自身无法执行的操作转移给angr的其它组件，这里就是对于CLE分析的一些组件的初始化

​ 第一步设置的就是angr中最重要的Factory组件，factory有几个方便的构造函数，用于经常使用的常见对象，具体的情况可以查看后面的简介。这一步从参数、loader、arch 或者默认值中获取预设的引擎，创建了一个`angr.EngineHub` 类实例

​ 第二步主要是从参数或者默认值中获取预设的分析。创建了一个 `angr.AnalysesHub` 类实例，angr 内置了一些分析方法，用于提取程序信息，接口位于 `proj.analyses.` 中

```
&gt;&gt;&gt; proj.analyses.
proj.analyses.BackwardSlice(              proj.analyses.Decompiler(                 proj.analyses.VFG(
proj.analyses.BasePointerSaveSimplifier(  proj.analyses.DefUseAnalysis(             proj.analyses.VSA_DDG(
proj.analyses.BinDiff(                    proj.analyses.Disassembly(               proj.analyses.VariableRecovery(
proj.analyses.BinaryOptimizer(            proj.analyses.DominanceFrontier(         proj.analyses.VariableRecoveryFast(       .....
```

​ 这个初始化函数的原型是

```
def _initialize_analyses_hub(self):
    """
    Initializes self.analyses using a given preset.
    """
    self.analyses = AnalysesHub(self)
    self.analyses.use_plugin_preset(self._analyses_preset if self._analyses_preset is not None else 'default')
```

​ 而AnalysesHub的函数原型在这里，主要是提供分析方法，用于提取程序信息

```
class AnalysesHub(PluginVendor):
    """
    This class contains functions for all the registered and runnable analyses,
    """
    def __init__(self, project):
        super(AnalysesHub, self).__init__()
        self.project = project

    @deprecated()
    def reload_analyses(self): # pylint: disable=no-self-use
        return

    def _init_plugin(self, plugin_cls):
        return AnalysisFactory(self.project, plugin_cls)

    def __getstate__(self):
        s = super(AnalysesHub, self).__getstate__()
        return (s, self.project)

    def __setstate__(self, sd):
        s, self.project = sd
        super(AnalysesHub, self).__setstate__(s)
```

​ 之后就是在创建其它一些插件的类实例

#### <a class="reference-link" name="2.2.5%20%E7%AC%AC%E4%BA%94%E6%AD%A5"></a>2.2.5 第五步

```
# Step 5: determine the guest OS
        if isinstance(simos, type) and issubclass(simos, SimOS):
            self.simos = simos(self) #pylint:disable=invalid-name
        elif isinstance(simos, str):
            self.simos = os_mapping[simos](self)
        elif simos is None:
            self.simos = os_mapping[self.loader.main_object.os](self)
        else:
            raise ValueError("Invalid OS specification or non-matching architecture.")
        self.is_java_project = isinstance(self.arch, ArchSoot)
        self.is_java_jni_project = isinstance(self.arch, ArchSoot) and self.simos.is_javavm_with_jni_support
```

​ 这一步就是确定 guest OS。创建了一个 `angr.SimOS` 或者其子类实例

#### <a class="reference-link" name="2.2.6%20%E7%AC%AC%E5%85%AD%E6%AD%A5"></a>2.2.6 第六步

```
# Step 6: Register simprocedures as appropriate for library functions
        if isinstance(self.arch, ArchSoot) and self.simos.is_javavm_with_jni_support:
            # If we execute a Java archive that includes native JNI libraries,
            # we need to use the arch of the native simos for all (native) sim
            # procedures.
            sim_proc_arch = self.simos.native_arch
        else:
            sim_proc_arch = self.arch
        for obj in self.loader.initial_load_objects:
            self._register_object(obj, sim_proc_arch)
```

​ 根据库函数适当地注册 simprocedures。调用了内部函数 `_register_object`，这个函数将尽可能的将程序中的库函数与angr库中的实现的符号摘要替换掉，

​ 即设置 Hooking，这些angr实现的函数摘要高效地模拟库函数对状态的影响
- 第一步就是获取angr已经实现的符号摘要的库函数
<li>然后就是分析我们的程序中的导入函数
<ul>
- 如果我们之前传入了忽略的列表函数，将其标记不替换存档
- 如果已将其列入黑名单，就算没设置忽略，angr也不对其进行处理
- 如果与我们的simprocedure匹配，angr将替换它
```
def _register_object(self, obj, sim_proc_arch):
        """
        This scans through an objects imports and hooks them with simprocedures from our library whenever possible
        """

        # Step 1: get the set of libraries we are allowed to use to resolve unresolved symbols
        missing_libs = []
        for lib_name in self.loader.missing_dependencies:
            try:
                missing_libs.append(SIM_LIBRARIES[lib_name])
            except KeyError:
                l.info("There are no simprocedures for missing library %s :(", lib_name)
        # additionally provide libraries we _have_ loaded as a fallback fallback
        # this helps in the case that e.g. CLE picked up a linux arm libc to satisfy an android arm binary
        for lib in self.loader.all_objects:
            if lib.provides in SIM_LIBRARIES:
                simlib = SIM_LIBRARIES[lib.provides]
                if simlib not in missing_libs:
                    missing_libs.append(simlib)

        # Step 2: Categorize every "import" symbol in each object.
        # If it's IGNORED, mark it for stubbing
        # If it's blacklisted, don't process it
        # If it matches a simprocedure we have, replace it
        for reloc in obj.imports.values():
            # Step 2.1: Quick filter on symbols we really don't care about
            func = reloc.symbol
            if func is None:
                continue
            if not func.is_function and func.type != cle.backends.symbol.SymbolType.TYPE_NONE:
                continue
            if func.resolvedby is None:
                # I don't understand the binary which made me add this case. If you are debugging and see this comment,
                # good luck.
                # ref: https://github.com/angr/angr/issues/1782
                # (I also don't know why the TYPE_NONE check in the previous clause is there but I can't find a ref for
                # that. they are probably related.)
                continue
            if not reloc.resolved:
                # This is a hack, effectively to support Binary Ninja, which doesn't provide access to dependency
                # library names. The backend creates the Relocation objects, but leaves them unresolved so that
                # we can try to guess them here. Once the Binary Ninja API starts supplying the dependencies,
                # The if/else, along with Project._guess_simprocedure() can be removed if it has no other utility,
                # just leave behind the 'unresolved' debug statement from the else clause.
                if reloc.owner.guess_simprocs:
                    l.debug("Looking for matching SimProcedure for unresolved %s from %s with hint %s",
                            func.name, reloc.owner, reloc.owner.guess_simprocs_hint)
                    self._guess_simprocedure(func, reloc.owner.guess_simprocs_hint)
                else:
                    l.debug("Ignoring unresolved import '%s' from %s ...?", func.name, reloc.owner)
                continue
            export = reloc.resolvedby
            if self.is_hooked(export.rebased_addr):
                l.debug("Already hooked %s (%s)", export.name, export.owner)
                continue

            # Step 2.2: If this function has been resolved by a static dependency,
            # check if we actually can and want to replace it with a SimProcedure.
            # We opt out of this step if it is blacklisted by ignore_functions, which
            # will cause it to be replaced by ReturnUnconstrained later.
            if export.owner is not self.loader._extern_object and \
                    export.name not in self._ignore_functions:
                if self._check_user_blacklists(export.name):
                    continue
                owner_name = export.owner.provides
                if isinstance(self.loader.main_object, cle.backends.pe.PE):
                    owner_name = owner_name.lower()
                if owner_name not in SIM_LIBRARIES:
                    continue
                sim_lib = SIM_LIBRARIES[owner_name]
                if not sim_lib.has_implementation(export.name):
                    continue
                l.info("Using builtin SimProcedure for %s from %s", export.name, sim_lib.name)
                self.hook_symbol(export.rebased_addr, sim_lib.get(export.name, sim_proc_arch))

            # Step 2.3: If 2.2 didn't work, check if the symbol wants to be resolved
            # by a library we already know something about. Resolve it appropriately.
            # Note that _check_user_blacklists also includes _ignore_functions.
            # An important consideration is that even if we're stubbing a function out,
            # we still want to try as hard as we can to figure out where it comes from
            # so we can get the calling convention as close to right as possible.
            elif reloc.resolvewith is not None and reloc.resolvewith in SIM_LIBRARIES:
                sim_lib = SIM_LIBRARIES[reloc.resolvewith]
                if self._check_user_blacklists(export.name):
                    if not func.is_weak:
                        l.info("Using stub SimProcedure for unresolved %s from %s", func.name, sim_lib.name)
                        self.hook_symbol(export.rebased_addr, sim_lib.get_stub(export.name, sim_proc_arch))
                else:
                    l.info("Using builtin SimProcedure for unresolved %s from %s", export.name, sim_lib.name)
                    self.hook_symbol(export.rebased_addr, sim_lib.get(export.name, sim_proc_arch))

            # Step 2.4: If 2.3 didn't work (the symbol didn't request a provider we know of), try
            # looking through each of the SimLibraries we're using to resolve unresolved
            # functions. If any of them know anything specifically about this function,
            # resolve it with that. As a final fallback, just ask any old SimLibrary
            # to resolve it.
            elif missing_libs:
                for sim_lib in missing_libs:
                    if sim_lib.has_metadata(export.name):
                        if self._check_user_blacklists(export.name):
                            if not func.is_weak:
                                l.info("Using stub SimProcedure for unresolved %s from %s", export.name, sim_lib.name)
                                self.hook_symbol(export.rebased_addr, sim_lib.get_stub(export.name, sim_proc_arch))
                        else:
                            l.info("Using builtin SimProcedure for unresolved %s from %s", export.name, sim_lib.name)
                            self.hook_symbol(export.rebased_addr, sim_lib.get(export.name, sim_proc_arch))
                        break
                else:
                    if not func.is_weak:
                        l.info("Using stub SimProcedure for unresolved %s", export.name)
                        the_lib = missing_libs[0]
                        if export.name and export.name.startswith("_Z"):
                            # GNU C++ name. Use a C++ library to create the stub
                            if 'libstdc++.so' in SIM_LIBRARIES:
                                the_lib = SIM_LIBRARIES['libstdc++.so']
                            else:
                                l.critical("Does not find any C++ library in SIM_LIBRARIES. We may not correctly "
                                           "create the stub or resolve the function prototype for name %s.", export.name)

                        self.hook_symbol(export.rebased_addr, the_lib.get(export.name, sim_proc_arch))

            # Step 2.5: If 2.4 didn't work (we have NO SimLibraries to work with), just
            # use the vanilla ReturnUnconstrained, assuming that this isn't a weak func
            elif not func.is_weak:
                l.info("Using stub SimProcedure for unresolved %s", export.name)
                self.hook_symbol(export.rebased_addr, SIM_PROCEDURES['stubs']['ReturnUnconstrained'](display_name=export.name, is_stub=True))
```

#### <a class="reference-link" name="2.2.7%20%E7%AC%AC%E4%B8%83%E6%AD%A5"></a>2.2.7 第七步

```
# Step 7: Run OS-specific configuration
        self.simos.configure_project()
```

​ 执行 OS 特定的配置，函数原型在`./simos/simos.py`

```
def configure_project(self):
        """
        Configure the project to set up global settings (like SimProcedures).
        """
        self.return_deadend = self.project.loader.extern_object.allocate()
        self.project.hook(self.return_deadend, P['stubs']['CallReturn']())

        self.unresolvable_jump_target = self.project.loader.extern_object.allocate()
        self.project.hook(self.unresolvable_jump_target, P['stubs']['UnresolvableJumpTarget']())
        self.unresolvable_call_target = self.project.loader.extern_object.allocate()
        self.project.hook(self.unresolvable_call_target, P['stubs']['UnresolvableCallTarget']())

        def irelative_resolver(resolver_addr):
            # autohooking runs before this does, might have provided this already
            # in that case, we want to advertise the _resolver_ address, since it is now
            # providing the behavior of the actual function
            if self.project.is_hooked(resolver_addr):
                return resolver_addr


            base_state = self.state_blank(addr=0,
                add_options=`{`o.SYMBOL_FILL_UNCONSTRAINED_MEMORY, o.SYMBOL_FILL_UNCONSTRAINED_REGISTERS`}`)
            resolver = self.project.factory.callable(resolver_addr, concrete_only=True, base_state=base_state)
            try:
                if isinstance(self.arch, ArchS390X):
                    # On s390x ifunc resolvers expect hwcaps.
                    val = resolver(0)
                else:
                    val = resolver()
            except AngrCallableMultistateError:
                _l.error("Resolver at %#x failed to resolve! (multivalued)", resolver_addr)
                return None
            except AngrCallableError:
                _l.error("Resolver at %#x failed to resolve!", resolver_addr)
                return None

            return val._model_concrete.value

        self.project.loader.perform_irelative_relocs(irelative_resolver)
```

### <a class="reference-link" name="2.3%20Hook"></a>2.3 Hook

​ angr的一大特色SimProcedure依赖于Hook功能，angr提供了以下几个常用的hook功能函数

```
def hook(self, addr, hook=None, length=0, kwargs=None, replace=False):
def hook_symbol(self, symbol_name, obj, kwargs=None, replace=None):
def _hook_decorator(self, addr, length=0, kwargs=None):
```

​ hook 用于将某段代码替换为其他的操作。其中参数 `hook` 是一个 `SimProcedure` 的实例，如果没有指定该参数，则假设函数作为装饰器使用。被 hook 的地址及实例 `hook` 被放入字典 `self._sim_procedures`。`hook_symbol()` 首先解析符号名得到对应的地址，然后调用 `hook()`

#### <a class="reference-link" name="2.3.1%20hook()"></a>2.3.1 hook()

用自定义的函数hook住一段代码。它用于内部提供库函数的符号，并用于插桩执行或修改控制流。当没有指定hook时，它将返回一个允许容易hook的函数装饰器

```
#
    # Public methods
    # They're all related to hooking!
    #

    # pylint: disable=inconsistent-return-statements
    def hook(self, addr, hook=None, length=0, kwargs=None, replace=False):
        """
        Hook a section of code with a custom function. This is used internally to provide symbolic
        summaries of library functions, and can be used to instrument execution or to modify
        control flow.

        When hook is not specified, it returns a function decorator that allows easy hooking.
        Usage::

            # Assuming proj is an instance of angr.Project, we will add a custom hook at the entry
            # point of the project.
            @proj.hook(proj.entry)
            def my_hook(state):
                print("Welcome to execution!")

        :param addr:        The address to hook.
        :param hook:        A :class:`angr.project.Hook` describing a procedure to run at the given address. You may also pass in a SimProcedure class or a function directly and it will be wrapped in a Hook object for you.
        :param length:      If you provide a function for the hook, this is the number of bytes that will be skipped by executing the hook by default.
        :param kwargs:      If you provide a SimProcedure for the hook, these are the keyword arguments that will be passed to the procedure's `run` method eventually.
        :param replace:     Control the behavior on finding that the address is already hooked. If true, silently replace the hook. If false (default), warn and do not replace the hook. If none, warn and replace the hook.
        """
        if hook is None:
            # if we haven't been passed a thing to hook with, assume we're being used as a decorator
            return self._hook_decorator(addr, length=length, kwargs=kwargs)

        if kwargs is None: kwargs = `{``}`

        l.debug('hooking %s with %s', self._addr_to_str(addr), str(hook))

        if self.is_hooked(addr):
            if replace is True:
                pass
            elif replace is False:
                l.warning("Address is already hooked, during hook(%s, %s). Not re-hooking.", self._addr_to_str(addr), hook)
                return
            else:
                l.warning("Address is already hooked, during hook(%s, %s). Re-hooking.", self._addr_to_str(addr), hook)

        if isinstance(hook, type):
            raise TypeError("Please instanciate your SimProcedure before hooking with it")

        if callable(hook):
            hook = SIM_PROCEDURES['stubs']['UserHook'](user_func=hook, length=length, **kwargs)

        self._sim_procedures[addr] = hook
```

​ 首先我们来看看参数部分：
- addr：要Hook的地址
- hook：一个angr.project.Hook类，描述要在给定地址运行的过程。您也可以直接传递SimProcedure类或函数，它将为您包装在Hook对象中
- length：如果为Hook提供需要替换函数，则这是默认情况下通过执行Hook掉该函数后将跳过的字节数
- kwargs：如果为Hook函数提供的是SimProcedure对象，则这些是关于SimProcedure的关键字参数，最终将传递给过程的run方法
<li>replace：主要是控制如果发现地址已经被hook后的操作
<ul>
- true：无提示地直接更换hook
- false：发出警告信息并不替换该hook（为缺省值）
- none：发出警告并替换该hook
```
self._sim_procedures[addr] = hook
```

> **callable()** 函数用于检查一个对象是否是可调用的。如果返回 True，object 仍然可能调用失败；但如果返回 False，调用对象 object 绝对不会成功

​ 被 hook 的地址及实例 `hook` 被放入字典 `self._sim_procedures`

​ 之后还有一些其它函数

```
def is_hooked(self, addr):
        """
        Returns True if `addr` is hooked.

        :param addr: An address.
        :returns:    True if addr is hooked, False otherwise.
        """
        return addr in self._sim_procedures

def hooked_by(self, addr):
        """
        Returns the current hook for `addr`.

        :param addr: An address.

        :returns:    None if the address is not hooked.
        """

        if not self.is_hooked(addr):
            l.warning("Address %s is not hooked", self._addr_to_str(addr))
            return None

        return self._sim_procedures[addr]

def unhook(self, addr):
        """
        Remove a hook.

        :param addr:    The address of the hook.
        """
        if not self.is_hooked(addr):
            l.warning("Address %s not hooked", self._addr_to_str(addr))
            return

        del self._sim_procedures[addr]
```

#### <a class="reference-link" name="2.3.2%20hook_symbol"></a>2.3.2 hook_symbol

​ 现实情况中我们更喜欢提供函数名（也就是一种符号名）来指代地址，而不是直接提供地址，且在动态加载库中也更为实际，所以在angr中`hook_symbol()` 首先解析符号名得到对应的地址，然后再调用 `hook()`

```
def hook_symbol(self, symbol_name, simproc, kwargs=None, replace=None):
        """
        Resolve a dependency in a binary. Looks up the address of the given symbol, and then hooks that
        address. If the symbol was not available in the loaded libraries, this address may be provided
        by the CLE externs object.

        Additionally, if instead of a symbol name you provide an address, some secret functionality will
        kick in and you will probably just hook that address, UNLESS you're on powerpc64 ABIv1 or some
        yet-unknown scary ABI that has its function pointers point to something other than the actual
        functions, in which case it'll do the right thing.

        :param symbol_name: The name of the dependency to resolve.
        :param simproc:     The SimProcedure instance (or function) with which to hook the symbol
        :param kwargs:      If you provide a SimProcedure for the hook, these are the keyword
                            arguments that will be passed to the procedure's `run` method
                            eventually.
        :param replace:     Control the behavior on finding that the address is already hooked. If
                            true, silently replace the hook. If false, warn and do not replace the
                            hook. If none (default), warn and replace the hook.
        :returns:           The address of the new symbol.
        :rtype:             int
        """
        if type(symbol_name) is not int:
            sym = self.loader.find_symbol(symbol_name)
            if sym is None:
                # it could be a previously unresolved weak symbol..?
                new_sym = None
                for reloc in self.loader.find_relevant_relocations(symbol_name):
                    if not reloc.symbol.is_weak:
                        raise Exception("Symbol is strong but we couldn't find its resolution? Report to @rhelmot.")
                    if new_sym is None:
                        new_sym = self.loader.extern_object.make_extern(symbol_name)
                    reloc.resolve(new_sym)
                    reloc.relocate([])

                if new_sym is None:
                    l.error("Could not find symbol %s", symbol_name)
                    return None
                sym = new_sym

            basic_addr = sym.rebased_addr
        else:
            basic_addr = symbol_name
            symbol_name = None

        hook_addr, _ = self.simos.prepare_function_symbol(symbol_name, basic_addr=basic_addr)

        self.hook(hook_addr, simproc, kwargs=kwargs, replace=replace)
        return hook_addr
```

​ 我们来看看参数部分：
- symbol_name：需要解析地函数名称
- simproc：需要hook的SimProcedure实例（或函数）
- kwargs：如果为Hook函数提供的是SimProcedure对象，则这些是关于SimProcedure的关键字参数，最终将传递给过程的run方法
<li>replace：主要是控制如果发现地址已经被hook后的操作
<ul>
- true：无提示地直接更换hook
- false：发出警告信息并不替换该hook（为缺省值）
- none：发出警告并替换该hook
​ 之后还有就是一些常用的辅助功能函数

```
def is_symbol_hooked(self, symbol_name):
        """
        Check if a symbol is already hooked.

        :param str symbol_name: Name of the symbol.
        :return: True if the symbol can be resolved and is hooked, False otherwise.
        :rtype: bool
        """
        sym = self.loader.find_symbol(symbol_name)
        if sym is None:
            l.warning("Could not find symbol %s", symbol_name)
            return False
        hook_addr, _ = self.simos.prepare_function_symbol(symbol_name, basic_addr=sym.rebased_addr)
        return self.is_hooked(hook_addr)

def unhook_symbol(self, symbol_name):
        """
        Remove the hook on a symbol.
        This function will fail if the symbol is provided by the extern object, as that would result in a state where
        analysis would be unable to cope with a call to this symbol.
        """
        sym = self.loader.find_symbol(symbol_name)
        if sym is None:
            l.warning("Could not find symbol %s", symbol_name)
            return False
        if sym.owner is self.loader._extern_object:
            l.warning("Refusing to unhook external symbol %s, replace it with another hook if you want to change it",
                      symbol_name)
            return False

        hook_addr, _ = self.simos.prepare_function_symbol(symbol_name, basic_addr=sym.rebased_addr)
        self.unhook(hook_addr)
        return True

def rehook_symbol(self, new_address, symbol_name, stubs_on_sync):
        """
        Move the hook for a symbol to a specific address
        :param new_address: the new address that will trigger the SimProc execution
        :param symbol_name: the name of the symbol (f.i. strcmp )
        :return: None
        """
        new_sim_procedures = `{``}`
        for key_address, simproc_obj in self._sim_procedures.items():

            # if we don't want stubs during the sync let's skip those, we will execute the real function.
            if not stubs_on_sync and simproc_obj.is_stub:
                continue

            if simproc_obj.display_name == symbol_name:
                new_sim_procedures[new_address] = simproc_obj
            else:
                new_sim_procedures[key_address] = simproc_obj

        self._sim_procedures = new_sim_procedures
```

### <a class="reference-link" name="2.4%20execute"></a>2.4 execute

​ 为符号执行提供的 API，十分方便。它被设计为在 hook 后执行，并将执行结果返回给模拟管理器

​ 主要是就为了Hook后符号执行还能征程运行，查看相关的状态，这个函数主要有三种不同的工作方式：
- 当不带参数执行时，该函数从程序入口点开始
- 当指定了参数 `state` 为一个 SimState 时，从该 state 开始
- 另外，它还可以接受所有传递给 `project.factory.full_init_state` 的任意关键字参数
```
def execute(self, *args, **kwargs):
        """
        This function is a symbolic execution helper in the simple style
        supported by triton and manticore. It designed to be run after
        setting up hooks (see Project.hook), in which the symbolic state
        can be checked.

        This function can be run in three different ways:

            - When run with no parameters, this function begins symbolic execution
              from the entrypoint.
            - It can also be run with a "state" parameter specifying a SimState to
              begin symbolic execution from.
            - Finally, it can accept any arbitrary keyword arguments, which are all
              passed to project.factory.full_init_state.

        If symbolic execution finishes, this function returns the resulting
        simulation manager.
        """

        if args:
            state = args[0]
        else:
            state = self.factory.full_init_state(**kwargs)

        pg = self.factory.simulation_manager(state)
        self._executing = True
        return pg.run(until=lambda lpg: not self._executing)
```

### <a class="reference-link" name="2.5%20load_shellcode"></a>2.5 load_shellcode

​ 主要是提供了可以根据一串原始字节码加载一个新的 Project功能

```
def load_shellcode(shellcode, arch, start_offset=0, load_address=0, thumb=False, **kwargs):
    """
    Load a new project based on a snippet of assembly or bytecode.

    :param shellcode:       The data to load, as either a bytestring of instructions or a string of assembly text
    :param arch:            The name of the arch to use, or an archinfo class
    :param start_offset:    The offset into the data to start analysis (default 0)
    :param load_address:    The address to place the data in memory (default 0)
    :param thumb:           Whether this is ARM Thumb shellcode
    """
    if not isinstance(arch, archinfo.Arch):
        arch = archinfo.arch_from_id(arch)
    if type(shellcode) is str:
        shellcode = arch.asm(shellcode, load_address, thumb=thumb)
    if thumb:
        start_offset |= 1

    return Project(
            BytesIO(shellcode),
            main_opts=`{`
                'backend': 'blob',
                'arch': arch,
                'entry_point': start_offset,
                'base_addr': load_address,
            `}`,
        **kwargs
        )
```

​ 我们来看看参数：
- shellcode：加载的数据
- arch：架构
- start_offset：分析的起始偏移量（默认0）
- load_address：数据加载的内存地址 (默认0)
- thumb：这个是否是ARM架构的Thumb模式下的代码，默认False
- kwargs：同之前的解释
### <a class="reference-link" name="2.6%20%E9%A2%84%E5%91%8A"></a>2.6 预告

​ 我们分析了一个angr项目的加载过程，我们不难看出其中基石的关键是CLE，我们接下来将前往CLE的实现源码一探究竟



## 三、番外：Factory简介

angr中最重要的Factory组件，factory有几个方便的构造函数，用于经常使用的常见对象

这里建议安装一个monkeyhex 库，这个库可以使得自动十六进制格式化数值结果，便于内存分析，在需要的时候导入即可

### <a class="reference-link" name="3.1%20Block"></a>3.1 Block

Blocks：`project.factory.block()`用于通过给定的地址提取一个基本块（basic block）的代码，angr以基本块为单位来分析代码
<li>
`block = proj.factory.block(proj.entry)`：从程序的入口处提取一个代码块</li>
<li>
`block.pp()`：打印反汇编代码</li>
<li>
`block`：查看block对象</li>
<li>
`block.instructions`：块里有多少条指令</li>
<li>
`block.instruction_addrs`：块里所有指令对应的地址</li>
<li>
`block.capstone`：capstone 反汇编</li>
<li>
`block.vex`：VEX IRSB</li>
下面这些指令在具体实践中的结果就是：

```
&gt;&gt;&gt; block = proj.factory.block(proj.entry)
&gt;&gt;&gt; block.pp()
0x401050:    endbr64    
0x401054:    xor    ebp, ebp
0x401056:    mov    r9, rdx
0x401059:    pop    rsi
0x40105a:    mov    rdx, rsp
0x40105d:    and    rsp, 0xfffffffffffffff0
0x401061:    push    rax
0x401062:    push    rsp
0x401063:    mov    r8, 0x4011d0
0x40106a:    mov    rcx, 0x401160
0x401071:    mov    rdi, 0x401136
0x401078:    call    qword ptr [rip + 0x2f72]
&gt;&gt;&gt; block
&lt;Block for 0x401050, 46 bytes&gt;
&gt;&gt;&gt; block.instructions
12
&gt;&gt;&gt; block.instruction_addrs
[4198480, 4198484, 4198486, 4198489, 4198490, 4198493, 4198497, 4198498, 4198499, 4198506, 4198513, 4198520]
&gt;&gt;&gt; block.capstone
&lt;CapstoneBlock for 0x401050&gt;
&gt;&gt;&gt; block.vex
IRSB &lt;0x2e bytes, 12 ins., &lt;Arch AMD64 (LE)&gt;&gt; at 0x401050
```

> block的概念是：**只有一个入口和一个出口的一段代码，入口就是其中的第一个语句，出口就是其中的最后一个语句**，block**之间的联通叫做edge**

### <a class="reference-link" name="3.2%20States"></a>3.2 States

States：：Project对象只代表程序的一个“初始化镜像”，即Project 对象仅表示程序一开始的样子。而当我们再使用angr做执行操作时，实际上操作的是一个表示模拟的程序状态（simulated program state）的特殊对象SimState。SimState代表程序的一个实例镜像，模拟执行某个时刻的状态
<li>
`state =proj.factory.entry_state()`：程序的入口点的状态</li>
<li>
`state`：查看state对象</li>
<li>
`state.regs.eip`：访问eip，获取当前指令的地址</li>
<li>
`state.regs.eax`：访问eax寄存器</li>
指令在具体实践中的结果就是：

```
&gt;&gt;&gt; state = proj.factory.entry_state()
&gt;&gt;&gt; state
&lt;SimState @ 0x401050&gt;
&gt;&gt;&gt; state.regs.rip
&lt;BV64 0x401050&gt;
&gt;&gt;&gt; state.regs.rax
&lt;BV64 0x1c&gt;
```

在这之前我们在CTF的应用中说过angr中使用的数不是传统的Python整数，而是bitvector（位向量）。可以把bitvector看成是一串比特序列表示的整数，angr使用bitvector来表示CPU数据。每个bitvector都有一个.length属性来描述它的位宽。angr中也提供了相关的方法来进行Python整数和位向量的转换

现在我们就来试一下转换rip的值

```
&gt;&gt;&gt; hex(state.solver.eval(state.regs.rip))
'0x401050'
```

我们也可以自己生成位向量

```
&gt;&gt;&gt; bv = state.solver.BVV(2021, 32)
&gt;&gt;&gt; bv
&lt;BV32 0x7e5&gt;
&gt;&gt;&gt; bv.length
32
```

我们可以把bitvector存储到寄存器和内存中；或者直接存储一个python整数，它会进行自动转换，把python整数转换为合适大小的bitvector

```
&gt;&gt;&gt; state.regs.rsi = state.solver.BVV(3, 32)
&gt;&gt;&gt; state.regs.rsi
&lt;BV64 0x3&gt;
&gt;&gt;&gt; state.mem[0x1000].long = 66
&gt;&gt;&gt; state.mem[0x1000].long.resolved
&lt;BV64 0x42&gt;
&gt;&gt;&gt; state.mem[0x1000].long.concrete
66
```

对于mem接口：
- 使用`array[index]`的形式来指定地址
- 使用`.&lt;type&gt;`来指定内存需要把数据解释成什么样的类型（char, short, int, long, size_t, uint8_t, uint16_t…）
- 存储一个值，这个值可以为bitvector或者python整数
- 使用`.resolved` 来将数据输出为bitvector
- 使用`.concrete` 来将数据输出为python整数
### <a class="reference-link" name="3.3%20Simulation%20Managers"></a>3.3 Simulation Managers

Simulation Manager（仿真管理器）在angr中是对state进行操作的基本接口

首先，我们创建一个simulation manager。构造函数可以接受一个state或者state列表。单个 Simulation Manager 可以包含多个存放state的 stash， 默认的stash 是 `active stash`，是使用我们传入的 `state`初始化的
<li>
`simgr = proj.factory.simulation_manager(state)`：用构造函数进行创建</li>
<li>
`simgr`：查看simgr对象</li>
<li>
`simgr.active`：查看active，也就是目前模拟执行到的代码（基本块）内存地址</li>
<li>
`simgr.step()`： 一个基本块的符号执行</li>
<li>
`simgr.active[0].regs.eip`：查看从我们传入的初始state后第一次执行step后的active</li>
指令在具体实践中的结果就是：

```
&gt;&gt;&gt; state = proj.factory.entry_state()
&gt;&gt;&gt; simgr = proj.factory.simulation_manager(state)
&gt;&gt;&gt; simgr
&lt;SimulationManager with 1 active&gt;
&gt;&gt;&gt; simgr.active
[&lt;SimState @ 0x401050&gt;]
&gt;&gt;&gt; simgr.step()
&lt;SimulationManager with 1 active&gt;
&gt;&gt;&gt; simgr.active
[&lt;SimState @ 0x526fc0&gt;]
&gt;&gt;&gt; simgr.active[0].regs.rip
&lt;BV64 0x526fc0&gt;
&gt;&gt;&gt; state.regs.rip
&lt;BV64 0x401050&gt;
```



## 四、参考资料

在此感谢各位作者或者译者的辛苦付出，特此感谢
- [angr源码分析——angr.Project类](https://blog.csdn.net/doudoudouzoule/article/details/79336706)
- [angr 系列教程(一）核心概念及模块解读](https://xz.aliyun.com/t/7117)
- [Angr文档-顶层接口](https://docs.angr.io/core-concepts/toplevel#basic-properties)
- [angr 源码分析](https://www.dazhuanlan.com/2020/01/17/5e210fb912a00/#project-%E7%B1%BB)
- [angr学习（一）](https://bbs.pediy.com/thread-264775.htm)
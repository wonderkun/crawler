> 原文链接: https://www.anquanke.com//post/id/250540 


# AFLGo 分析


                                阅读量   
                                **18554**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t013a7eb904de752df8.png)](https://p0.ssl.qhimg.com/t013a7eb904de752df8.png)



## 0. Directed fuzzing

**Directed fuzzing** 可以翻译为定向模糊测试，导向型模糊测试，是灰盒模糊测试中的一种。传统的覆盖率引导的模糊测试 (Coverage-guided fuzzing) 是期望覆盖到更多的代码，所以是以覆盖率的增加作为引导。而在某些场景下，例如对patch进行测试，此时，传统的基于覆盖率的模糊测试那种盲目探索的方式不能满足快速到达特定目标点的需求。

所以，基于上述的场景，提出了 directed fuzzing ，导向型模糊测试是有特定目标的，希望能够快速覆盖到使用者期望到达的目标点。所以需要对 fuzzing 进行引导，忽略其余不相关的部分，使得 fuzzer 朝着目标点探索。



## 1. AFLGo论文

2017年，Directed fuzzing这个概念在 B¨ohme等人的论文 **Directed Greybox Fuzzing** 中第一次被提出，文章开源了一个名为 [AFLGo](https://github.com/aflgo/aflgo) 的工具，是在 AFL 的基础上，实现了一个可以快速到达指定目标点的模糊测试工具。后续出现的 Directed fuzzing，基本都无法完全脱离 AFLGo 的方法，可以说，AFLGo 开创了导向型模糊测试的先河。

### <a class="reference-link" name="1.1%20%E6%A6%82%E8%BF%B0"></a>1.1 概述

AFLGo的流程如下图：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015c5276562b213f32.png)

1.首先，编译源码，得到待 fuzz 程序的控制流图 (Control Flow Graph, CFG) 和函数调用图 (Call Graph, CG) 。这一步由AFL中作者编写的 LLVM Pass 完成。

2.其次，通过 CFG 和 CG，以及给定的 target，计算所有的基本块 (Basic Block, BB) 到 target 所在的基本块的**距离**。这一步由 python 脚本完成。

3.然后，再编译一次源码，对程序进行插桩，除了AFL原有的插桩逻辑外，添加向指定地址增加每个基本块距离的指令，即指定一个共享内存地址为记录 distance 的变量，在基本块中插桩，插入如下指令：distance += current_BB_distance，向 distance 变量增加当前基本块的距离。

4.最后是 fuzzing 部分的逻辑，根据插桩反馈的信息，我们可以在每一个 seed 作为输入给程序执行的时候得到这个 seed 对应的 distance，也就是 seed 执行路径距离目标点的距离，然后根据距离对 seed 进行打分，这个打分的算法就是模拟退火算法，距离越近，打分越高，seed 得到变异的机会越多。

至此，整个 AFLGo 的流程结束。

### <a class="reference-link" name="1.2%20%E8%B7%9D%E7%A6%BB%E8%AE%A1%E7%AE%97"></a>1.2 距离计算

AFLGO 首先根据 CG 计算**函数层面 (function-level)** 的距离，然后基于 CFG 计算**基本块层面 (basic-block level)** 的距离，最后将基本块的距离作为插桩时使用的距离。

因为 AFLGo 支持标记多个目标，所以在距离计算时需要将每个基本块到多个目标的距离做一个加和，这里采用的是对到每个目标的距离和取**调和平均数**。

为什么不取算术平均数？因为在多目标的情况下，算术平均数无法区分『一个基本块离一个目标近一个目标远』和『一个基本块离两个目标点距离相等』的情况。

如下图，当目标为Y1和Y2时，三个白色基本块都可以到达这两个灰色的目标点。当用算术平均数计算时，左右分别到两个目标点的距离是1和3，平均下来就是(1+3) / 2= 2。而最上面的点到两个目标的距离都是2，平均下来也是2，这样三个点距离都是2，区分不出到哪个点距离近。如果取调和平均数，左右两个点距离都是是3/4，最上面的点距离是1，这样就能区分出远近了。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t011bae412214c69c36.png)

<a class="reference-link" name="1.2.1%20%E5%87%BD%E6%95%B0%E5%B1%82%E9%9D%A2%E8%B7%9D%E7%A6%BB%E8%AE%A1%E7%AE%97"></a>**1.2.1 函数层面距离计算**

目标基本块所在的函数就是目标函数。

公式看起来比较复杂，其实就是两句话：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0140dd93d550ed97c1.png)

1.当该函数不能到达任意一个目标函数(即：CG上该函数没有路径能到达目标函数)时，不定义距离

2.否则，将该函数能够到达的目标函数之间的**最短距离**取调和平均数

<a class="reference-link" name="1.2.2%20%E5%9F%BA%E6%9C%AC%E5%9D%97%E5%B1%82%E9%9D%A2%E8%B7%9D%E7%A6%BB%E8%AE%A1%E7%AE%97"></a>**1.2.2 基本块层面距离计算**

有了函数层面的距离，再计算更加细的基本块距离，规则如下：

[![](https://p0.ssl.qhimg.com/t01aa9a829dc7f5261e.png)](https://p0.ssl.qhimg.com/t01aa9a829dc7f5261e.png)

1.当基本块就是目标基本块时，该基本块的距离为0

2.当前基本块存在函数调用链可以到达目标函数时，距离为该基本块中调用的函数集和中，『距离目标函数最近的路径距离』乘上一个系数

3.否则，距离为『有能到达目标基本块的后继基本块时，取当前基本块到后继基本块距离』 + 『该后继基本块到目标基本块的距离』，取到所有目标的调和平均数

### <a class="reference-link" name="1.3%20%E6%A8%A1%E6%8B%9F%E9%80%80%E7%81%AB%E7%AE%97%E6%B3%95"></a>1.3 模拟退火算法

公式也很复杂，但这里只讲算法的作用：模拟退火算法是为了解决**探索-利用 (exploration-exploitation)**的问题。

在fuzzing的前期，因为探索到的路径有限，此时离目标点的距离可能还很远，此时重点在探索，即尽可能扩大覆盖率，当覆盖率到一定程度时，再利用距离较近的seed来变异，此时到达目标点的可能性更大。

如果在距离还很远的时候，就只针对当前距离最近的seed进行变异，虽然当前seed距离是相对最近的，但是在绝对距离上可能还很远，无论怎么fuzzing，到达目标点的可能性就很小，这样就可能会陷入**局部最优**的困境中。

模拟退火算法就是为了避免uzzing陷入局部最优的困境中的方法。

AFL中有一个环节叫 power scheduling，即对 seed 进行打分，综合各项指标计算分数，这个分数直接影响到对每个 seed 进行 fuzzing 的时间长度。

而 AFLGo 在 power scheduling 部分加上模拟退火算法，同时以时间和距离来计算分数。当时间越长，距离越近的 seed 得分越高，能够得到 fuzzing 的时间越长。



## 2. 源码分析

这一节我们按照 workflow，对照源码进行分析。

### <a class="reference-link" name="2.1%20%E9%A2%84%E5%A4%84%E7%90%86%E9%98%B6%E6%AE%B5"></a>2.1 预处理阶段

以 AFLGo `README` 中例子为例，首先是第一次编译，输入程序源码，输出 CG 和 CFG。

```
# Set aflgo-instrumenter
export CC=$AFLGO/afl-clang-fast
export CXX=$AFLGO/afl-clang-fast++

# Set aflgo-instrumentation flags
export COPY_CFLAGS=$CFLAGS
export COPY_CXXFLAGS=$CXXFLAGS
export ADDITIONAL="-targets=$TMP_DIR/BBtargets.txt -outdir=$TMP_DIR -flto -fuse-ld=gold -Wl,-plugin-opt=save-temps"
export CFLAGS="$CFLAGS $ADDITIONAL"
export CXXFLAGS="$CXXFLAGS $ADDITIONAL"

# Build libxml2 (in order to generate CG and CFGs).
# Meanwhile go have a coffee ☕️
export LDFLAGS=-lpthread
pushd $SUBJECT
  ./autogen.sh
  ./configure --disable-shared
  make clean
  make xmllint
popd
```

与 AFL 不一样的地方在于，需要多传入3个编译选项`-targets=$TMP_DIR/BBtargets.txt -outdir=$TMP_DIR -flto -fuse-ld=gold -Wl,-plugin-opt=save-temps"`。

`-target`传入的是目标点位置文件，`-outdir`传入的是 graph 导出的目录。

最后的`-flto -fuse-ld=gold -Wl,-plugin-opt=save-temps`是开启 llvm link time optimization 选项，是在链接阶段进行模块间的优化，`-Wl,-plugin-opt=save-temps`选项是为了保存下整个程序的`.bc`文件，便于之后生成 CG。这一步需要`libLTO.so`和`LLVMgold.so`两个动态库，所以编译前需要保证这两个`.so`文件在`/usr/lib/bfd-plugins`目录下。

第一次编译的主要处理代码在`llvm_mode/afl-llvm-pass.so.cc`文件中，该文件是 llvm 的 pass 插件文件，编译后作为 llvm 的插件，在编译时自动加载运行。

主程序的逻辑都在`AFLCoverage::runOnModule`函数中。

```
bool AFLCoverage::runOnModule(Module &amp;M) `{`

  bool is_aflgo = false;
  bool is_aflgo_preprocessing = false;

  /* 判断目标文件和距离文件是否同时声明，因为这是第一次编译和第二次编译两个阶段分别需要的文件
  不可以同时声明。
  */
  if (!TargetsFile.empty() &amp;&amp; !DistanceFile.empty()) `{`
    FATAL("Cannot specify both '-targets' and '-distance'!");
    return false;
  `}`

  std::list&lt;std::string&gt; targets; // 存储目标点的list
  std::map&lt;std::string, int&gt; bb_to_dis; // 存储基本块和对应距离的map
  std::vector&lt;std::string&gt; basic_blocks; // 存储基本块名字的vector

  /* 当目标文件不为空时，说明是第一次编译阶段。
  */
  if (!TargetsFile.empty()) `{`

    /* 检查输出文件目录是否为空
    */
    if (OutDirectory.empty()) `{`
      FATAL("Provide output directory '-outdir &lt;directory&gt;'");
      return false;
    `}`

    /* 按行读取目标点文件，存储到target中，然后置flag，表示为preprocessing阶段
    */
    std::ifstream targetsfile(TargetsFile);
    std::string line;
    while (std::getline(targetsfile, line))
      targets.push_back(line);
    targetsfile.close();

    is_aflgo_preprocessing = true;

  `}` else if (!DistanceFile.empty()) `{`
      ...
  `}`
```

这里接收命令行参数的变量为`TargetsFile`和`OutDirectory`，以及第二次编译接收距离文件的变量`DistanceFile`，定义为

```
cl::opt&lt;std::string&gt; DistanceFile(
    "distance",
    cl::desc("Distance file containing the distance of each basic block to the provided targets."),
    cl::value_desc("filename")
);

cl::opt&lt;std::string&gt; TargetsFile(
    "targets",
    cl::desc("Input file containing the target lines of code."),
    cl::value_desc("targets"));

cl::opt&lt;std::string&gt; OutDirectory(
    "outdir",
    cl::desc("Output directory where Ftargets.txt, Fnames.txt, and BBnames.txt are generated."),
    cl::value_desc("outdir"));
```

这是 llvm 提供的 commandline library，方便解析命令行参数。这里有一个小tips，因为`cl::opt`类默认是只允许不出现或者出现一次声明，但经过实践发现在编译一些程序库的时候，因为不太清楚这些库的 makefile 是怎么写的，很容易出现对编译选项的重复声明，为了方便，建议这里定义时加上`cl::ZeroOrMore`，这样即使重复，也不会报错，编译选项的值取最后一次声明。

AFLGo 还需要修改的地方是`llvm_mode/afl-clang-fast.c`中，需要加上以下代码才能让 AFL 的 clang wrapper 能够识别添加的编译选项

```
if (!strncmp(cur, "-distance", 9)
        || !strncmp(cur, "-targets", 8)
        || !strncmp(cur, "-outdir", 7))
      cc_params[cc_par_cnt++] = "-mllvm";
```

参考来自[文档](https://llvm.org/docs/CommandLine.html)：

> The allowed values for this option group are:
<ul>
- The **cl::Optional** modifier (which is the default for the [cl::opt](https://llvm.org/docs/CommandLine.html#cl-opt) and [cl::alias](https://llvm.org/docs/CommandLine.html#cl-alias) classes) indicates that your program will allow either zero or one occurrence of the option to be specified.
- The **cl::ZeroOrMore** modifier (which is the default for the [cl::list](https://llvm.org/docs/CommandLine.html#cl-list) class) indicates that your program will allow the option to be specified zero or more times.
- The **cl::Required** modifier indicates that the specified option must be specified exactly one time.
- The **cl::OneOrMore** modifier indicates that the option must be specified at least one time.
- The **cl::ConsumeAfter** modifier is described in the [Positional arguments section](https://llvm.org/docs/CommandLine.html#positional-arguments-section).
</ul>

接下来是运行时的提示 banner 和 AFL 本身的插桩比例，没什么重要点

```
/* Show a banner */

  char be_quiet = 0;

  if (isatty(2) &amp;&amp; !getenv("AFL_QUIET")) `{`

    if (is_aflgo || is_aflgo_preprocessing)
      SAYF(cCYA "aflgo-llvm-pass (yeah!) " cBRI VERSION cRST " (%s mode)\n",
           (is_aflgo_preprocessing ? "preprocessing" : "distance instrumentation"));
    else
      SAYF(cCYA "afl-llvm-pass " cBRI VERSION cRST " by &lt;lszekeres@google.com&gt;\n");


  `}` else be_quiet = 1;

  /* Decide instrumentation ratio */

  char* inst_ratio_str = getenv("AFL_INST_RATIO");
  unsigned int inst_ratio = 100;

  if (inst_ratio_str) `{`

    if (sscanf(inst_ratio_str, "%u", &amp;inst_ratio) != 1 || !inst_ratio ||
        inst_ratio &gt; 100)
      FATAL("Bad value of AFL_INST_RATIO (must be between 1 and 100)");

  `}`
```

但 AFLGo 也仿照 AFL 做了插桩比例的选择，即如果声明了`AFLGO_SELECTIVE`环境变量以及`AFLGO_INST_RATIO`，`AFLGO_INST_RATIO`数值就是 AFlGo 的插桩百分比。

```
/* Default: Not selective */
  char* is_selective_str = getenv("AFLGO_SELECTIVE");
  unsigned int is_selective = 0;

  if (is_selective_str &amp;&amp; sscanf(is_selective_str, "%u", &amp;is_selective) != 1)
    FATAL("Bad value of AFLGO_SELECTIVE (must be 0 or 1)");

  char* dinst_ratio_str = getenv("AFLGO_INST_RATIO");
  unsigned int dinst_ratio = 100;

  if (dinst_ratio_str) `{`

    if (sscanf(dinst_ratio_str, "%u", &amp;dinst_ratio) != 1 || !dinst_ratio ||
        dinst_ratio &gt; 100)
      FATAL("Bad value of AFLGO_INST_RATIO (must be between 1 and 100)");

  `}`
```

然后进入到 preprocessing 阶段

```
if (is_aflgo_preprocessing) `{`

    std::ofstream bbnames(OutDirectory + "/BBnames.txt", std::ofstream::out | std::ofstream::app); // 记录基本块名字文件
    std::ofstream bbcalls(OutDirectory + "/BBcalls.txt", std::ofstream::out | std::ofstream::app); // 记录callsite文件，格式为[基本块，函数名]
    std::ofstream fnames(OutDirectory + "/Fnames.txt", std::ofstream::out | std::ofstream::app); // 记录函数名文件
    std::ofstream ftargets(OutDirectory + "/Ftargets.txt", std::ofstream::out | std::ofstream::app); // 记录目标基本块所在函数名文件

    /* Create dot-files directory */
    std::string dotfiles(OutDirectory + "/dot-files");
    if (sys::fs::create_directory(dotfiles)) `{`
      FATAL("Could not create directory %s.", dotfiles.c_str());
    `}`

    for (auto &amp;F : M) `{`

      bool has_BBs = false;
      std::string funcName = F.getName().str();

      /* Black list of function names */
      if (isBlacklisted(&amp;F)) `{`
        continue;
      `}`

      bool is_target = false;
      for (auto &amp;BB : F) `{`

        std::string bb_name("");
        std::string filename;
        unsigned line;

        for (auto &amp;I : BB) `{`
          getDebugLoc(&amp;I, filename, line);

          /* Don't worry about external libs */
          /* 去除掉一些外部库，以及没有位置信息的指令
          */
          static const std::string Xlibs("/usr/");
          if (filename.empty() || line == 0 || !filename.compare(0, Xlibs.size(), Xlibs))
            continue;

          if (bb_name.empty()) `{`
            /* 用基本块的第一条有效指令位置作为基本块名字
               基本块名字格式为：[基本块所在文件名：基本块所在行数]
            */
            std::size_t found = filename.find_last_of("/\\");
            if (found != std::string::npos)
              filename = filename.substr(found + 1);

            bb_name = filename + ":" + std::to_string(line);
          `}`

          /* 判断该基本块是否是目标基本块，即对应的文件名和行数是否相等
          */
          if (!is_target) `{`
              for (auto &amp;target : targets) `{`
                std::size_t found = target.find_last_of("/\\");
                if (found != std::string::npos)
                  target = target.substr(found + 1);

                std::size_t pos = target.find_last_of(":");
                std::string target_file = target.substr(0, pos);
                unsigned int target_line = atoi(target.substr(pos + 1).c_str());

                if (!target_file.compare(filename) &amp;&amp; target_line == line)
                  is_target = true;

              `}`
            `}`

            /* 如果当前指令是call指令，则记录下当前基本块名字和调用的函数
               格式为: [基本块名字，函数名]
            */
            if (auto *c = dyn_cast&lt;CallInst&gt;(&amp;I)) `{`

              std::size_t found = filename.find_last_of("/\\");
              if (found != std::string::npos)
                filename = filename.substr(found + 1);

              if (auto *CalledF = c-&gt;getCalledFunction()) `{`
                if (!isBlacklisted(CalledF))
                  bbcalls &lt;&lt; bb_name &lt;&lt; "," &lt;&lt; CalledF-&gt;getName().str() &lt;&lt; "\n";
              `}`
            `}`
        `}`

        if (!bb_name.empty()) `{`
         /* 这里是设置基本块名字，但是因为有一些基本块在源码中位置在同一行，
            故同名的设置会失效，所以当发现名字没有设置上时，为其创建一个allocator，
            则会自动在名字后生成随机数，避免了同名问题
         */
          BB.setName(bb_name + ":");
          if (!BB.hasName()) `{`
            std::string newname = bb_name + ":";
            Twine t(newname);
            SmallString&lt;256&gt; NameData;
            StringRef NameRef = t.toStringRef(NameData);
            MallocAllocator Allocator;
            BB.setValueName(ValueName::Create(NameRef, Allocator));
          `}`

          /* 导出基本块名字到文件中 */
          bbnames &lt;&lt; BB.getName().str() &lt;&lt; "\n";
          has_BBs = true;

/* 这个宏是针对补充CG设计的，开启后，会在运行时将调用的函数实时记录下来 */
#ifdef AFLGO_TRACING
          auto *TI = BB.getTerminator();
          IRBuilder&lt;&gt; Builder(TI);

          Value *bbnameVal = Builder.CreateGlobalStringPtr(bb_name);
          Type *Args[] = `{`
              Type::getInt8PtrTy(M.getContext()) //uint8_t* bb_name
          `}`;
          FunctionType *FTy = FunctionType::get(Type::getVoidTy(M.getContext()), Args, false);
          Constant *instrumented = M.getOrInsertFunction("llvm_profiling_call", FTy);
          Builder.CreateCall(instrumented, `{`bbnameVal`}`);
#endif

        `}`
      `}`

       /* 这里首先判断该函数是否有基本块，如果有，就打印该函数的CFG，
          AFLGo重写了WriteGraph相关的类，所以打印出的CFG文件与llvm自带的插件打印出的不一样
       */
      if (has_BBs) `{`
        /* Print CFG */
        std::string cfgFileName = dotfiles + "/cfg." + funcName + ".dot";
        std::error_code EC;
        raw_fd_ostream cfgFile(cfgFileName, EC, sys::fs::F_None);
        if (!EC) `{`
          WriteGraph(cfgFile, &amp;F, true);
        `}`

        /* 最后记录目标基本块所在函数和所有的函数名。
        */
        if (is_target)
          ftargets &lt;&lt; F.getName().str() &lt;&lt; "\n";
        fnames &lt;&lt; F.getName().str() &lt;&lt; "\n";
      `}`
    `}`

  `}` else `{`
    ...
  `}`
```

这里调用了几个 AFLGo 自己实现的函数，首先是判断函数是否是几个无关函数的`isBlacklisted`，这里对几个常见的库函数做了屏蔽。

```
static bool isBlacklisted(const Function *F) `{`
  static const SmallVector&lt;std::string, 8&gt; Blacklist = `{`
    "asan.",
    "llvm.",
    "sancov.",
    "__ubsan_handle_",
    "free",
    "malloc",
    "calloc",
    "realloc"
  `}`;

  for (auto const &amp;BlacklistFunc : Blacklist) `{`
    if (F-&gt;getName().startswith(BlacklistFunc)) `{`
      return true;
    `}`
  `}`

  return false;
`}`
```

然后是`getDebugLoc`函数，该函数作用是获取指令所在的文件名和行数，这里需要注意的是，在编译的时候一定要加入`-g`选项，表示程序保留debug信息，否则无法获取源码所在文件名和行数信息。

```
static void getDebugLoc(const Instruction *I, std::string &amp;Filename,
                        unsigned &amp;Line) `{`
/* 这里对llvm旧版本的api做了兼容
*/
#ifdef LLVM_OLD_DEBUG_API
  DebugLoc Loc = I-&gt;getDebugLoc();
  if (!Loc.isUnknown()) `{`
    DILocation cDILoc(Loc.getAsMDNode(M.getContext()));
    DILocation oDILoc = cDILoc.getOrigLocation();

    Line = oDILoc.getLineNumber();
    Filename = oDILoc.getFilename().str();

    if (filename.empty()) `{`
      Line = cDILoc.getLineNumber();
      Filename = cDILoc.getFilename().str();
    `}`
  `}`
#else
  if (DILocation *Loc = I-&gt;getDebugLoc()) `{`
    Line = Loc-&gt;getLine();
    Filename = Loc-&gt;getFilename().str();

    if (Filename.empty()) `{`
      DILocation *oDILoc = Loc-&gt;getInlinedAt();
      if (oDILoc) `{`
        Line = oDILoc-&gt;getLine();
        Filename = oDILoc-&gt;getFilename().str();
      `}`
    `}`
  `}`
#endif /* LLVM_OLD_DEBUG_API */
`}`
```

最后是重写的打印 CFG 的类`DOTGraphTraits`，对几个关键函数重写，让打印出的CFG按照我们期望的格式打印。

```
template&lt;&gt;
struct DOTGraphTraits&lt;Function*&gt; : public DefaultDOTGraphTraits `{`
  DOTGraphTraits(bool isSimple=true) : DefaultDOTGraphTraits(isSimple) `{``}`

  static std::string getGraphName(Function *F) `{`
    return "CFG for '" + F-&gt;getName().str() + "' function";
  `}`

  std::string getNodeLabel(BasicBlock *Node, Function *Graph) `{`
    if (!Node-&gt;getName().empty()) `{`
      return Node-&gt;getName().str();
    `}`

    std::string Str;
    raw_string_ostream OS(Str);

    Node-&gt;printAsOperand(OS, false);
    return OS.str();
  `}`
`}`;
```

到这里第一次编译的逻辑结束了，最后会在`-outdir`声明的目录下得到以下文件

```
.
├── BBcalls.txt
├── BBnames.txt
├── dot-files
├── Fnames.txt
└── Ftargets.txt

1 directory, 4 files
```

### <a class="reference-link" name="2.2%20%E8%AE%A1%E7%AE%97%E8%B7%9D%E7%A6%BB"></a>2.2 计算距离

根据 AFLGo `README`，下一步需要生成距离

```
# Generate distance ☕️
# $AFLGO/scripts/genDistance.sh is the original, but significantly slower, version
$AFLGO/scripts/gen_distance_fast.py $SUBJECT $TMP_DIR xmllint
```

这里使用的脚本`gen_distance_fast.py`是作者因为原本用 python 写的版本计算太慢，就用 C++ 重新实现了一遍，逻辑实际上是一样的，这里我们为了说明方便就用原来的脚本说明，即文件`scripts/genDistance.sh`。

```
#!/bin/bash
# 检查参数个数，说明脚本用法
if [ $# -lt 2 ]; then
  echo "Usage: $0 &lt;binaries-directory&gt; &lt;temporary-directory&gt; [fuzzer-name]"
  echo ""
  exit 1
fi

# 设置好参数路径
BINARIES=$(readlink -e $1)
TMPDIR=$(readlink -e $2)
AFLGO="$( cd "$( dirname "$`{`BASH_SOURCE[0]`}`" )" &amp;&amp; pwd )"
fuzzer=""
# 检查程序的.bc文件是否存在，否则无法生成CG
if [ $# -eq 3 ]; then
  fuzzer=$(find $BINARIES -name "$3.0.0.*.bc" | rev | cut -d. -f5- | rev)
  if [ $(echo "$fuzzer" | wc -l) -ne 1 ]; then
    echo "Couldn't find bytecode for fuzzer $3 in folder $BINARIES."
    exit 1
  fi
fi

SCRIPT=$0
ARGS=$@

#SANITY CHECKS
if [ -z "$BINARIES" ]; then echo "Couldn't find binaries folder ($1)."; exit 1; fi
if ! [ -d "$BINARIES" ]; then echo "No directory: $BINARIES."; exit 1; fi
if [ -z "$TMPDIR" ]; then echo "Couldn't find temporary directory ($3)."; exit 1; fi

binaries=$(find $BINARIES -name "*.0.0.*.bc" | rev | cut -d. -f5- | rev)
if [ -z "$binaries" ]; then echo "Couldn't find any binaries in folder $BINARIES."; exit; fi

if [ -z $(which python) ] &amp;&amp; [ -z $(which python3) ]; then echo "Please install Python"; exit 1; fi
#if python -c "import pydotplus"; then echo "Install python package: pydotplus (sudo pip install pydotplus)"; exit 1; fi
#if python -c "import pydotplus; import networkx"; then echo "Install python package: networkx (sudo pip install networkx)"; exit 1; fi

FAIL=0
STEP=1
# 该变量是为了在脚本因为其他原因断掉后，可以直接接着上次结果运行，断点存在state文件中
RESUME=$(if [ -f $TMPDIR/state ]; then cat $TMPDIR/state; else echo 0; fi)

# 该函数记录脚本运行到哪个阶段，方便断掉后下次可以接着断开前继续运行
function next_step `{`
  echo $STEP &gt; $TMPDIR/state
  if [ $FAIL -ne 0 ]; then
    tail -n30 $TMPDIR/step$`{`STEP`}`.log
    echo "-- Problem in Step $STEP of generating $OUT!"
    echo "-- You can resume by executing:"
    echo "$ $SCRIPT $ARGS $TMPDIR"
    exit 1
  fi
  STEP=$((STEP + 1))
`}`
```

上一步得到的图其实只有 CFG，CG 需要调用 llvm 自带的 pass 来生成。

```
#-------------------------------------------------------------------------------
# Construct control flow graph and call graph
#-------------------------------------------------------------------------------
if [ $RESUME -le $STEP ]; then

  cd $TMPDIR/dot-files

  # 如果声明的fuzzer程序不存在，则需要对binary目录下的所有程序都生成CG，否则只需要对声明的fuzzer生成CG。
  if [ -z "$fuzzer" ]; then
    for binary in $(echo "$binaries"); do

      echo "($STEP) Constructing CG for $binary.."
      prefix="$TMPDIR/dot-files/$(basename $binary)"
       # 调用opt-11的-dot-callgraph pass来生成对应程序的CG
      while ! opt-11 -dot-callgraph $binary.0.0.*.bc -callgraph-dot-filename-prefix $prefix &gt;/dev/null 2&gt; $TMPDIR/step$`{`STEP`}`.log ; do
        echo -e "\e[93;1m[!]\e[0m Could not generate call graph. Repeating.."
      done

      #Remove repeated lines and rename
      awk '!a[$0]++' $(basename $binary).callgraph.dot &gt; callgraph.$(basename $binary).dot
      rm $(basename $binary).callgraph.dot
    done

    # 由于这里对所有的程序都生成了CG，需要合并为一张图
    #Integrate several call graphs into one
    $AFLGO/merge_callgraphs.py -o callgraph.dot $(ls callgraph.*)
    echo "($STEP) Integrating several call graphs into one."

  else
    # 一般只会进入到这里
    echo "($STEP) Constructing CG for $fuzzer.."
    prefix="$TMPDIR/dot-files/$(basename $fuzzer)"
    # 调用opt-11的-dot-callgraph pass来生成对应程序的CG
    while ! opt-11 -dot-callgraph $fuzzer.0.0.*.bc -callgraph-dot-filename-prefix $prefix &gt;/dev/null 2&gt; $TMPDIR/step$`{`STEP`}`.log ; do
      echo -e "\e[93;1m[!]\e[0m Could not generate call graph. Repeating.."
    done

    #Remove repeated lines and rename
    awk '!a[$0]++' $(basename $fuzzer).callgraph.dot &gt; callgraph.dot
    rm $(basename $fuzzer).callgraph.dot

  fi
fi
next_step
```

生成了 CG 后，就可以计算距离了，按照 AFLGo 的设计，距离分为 function-level 和 basicblock-level 的距离，先计算函数维度的距离，再计算基本块维度的距离，最后得到每一个可以到达目标点的基本块到目标点的距离。

```
#-------------------------------------------------------------------------------
# Generate config file keeping distance information for code instrumentation
#-------------------------------------------------------------------------------
if [ $RESUME -le $STEP ]; then
  echo "($STEP) Computing distance for call graph .."
  # 首先计算函数维度的距离
  $AFLGO/distance.py -d $TMPDIR/dot-files/callgraph.dot -t $TMPDIR/Ftargets.txt -n $TMPDIR/Fnames.txt -o $TMPDIR/distance.callgraph.txt &gt; $TMPDIR/step$`{`STEP`}`.log 2&gt;&amp;1 || FAIL=1

  if [ $(cat $TMPDIR/distance.callgraph.txt | wc -l) -eq 0 ]; then
    FAIL=1
    next_step
  fi

  printf "($STEP) Computing distance for control-flow graphs "
  for f in $(ls -1d $TMPDIR/dot-files/cfg.*.dot); do

    # 有一些函数没有在CG中出现，即没有被调用，则忽略这些函数
    # Skip CFGs of functions we are not calling
    if ! grep "$(basename $f | cut -d. -f2)" $TMPDIR/dot-files/callgraph.dot &gt;/dev/null; then
      printf "\nSkipping $f..\n"
      continue
    fi

    #Clean up duplicate lines and \" in labels (bug in Pydotplus)
    awk '!a[$0]++' $f &gt; $`{`f`}`.smaller.dot
    mv $f $f.bigger.dot
    mv $f.smaller.dot $f
    sed -i s/\\\\\"//g $f
    sed -i 's/\[.\"]//g' $f
    sed -i 's/\(^\s*[0-9a-zA-Z_]*\):[a-zA-Z0-9]*\( -&gt; \)/\1\2/g' $f

    # 再计算基本块维度的距离
    #Compute distance
    printf "\nComputing distance for $f..\n"
    $AFLGO/distance.py -d $f -t $TMPDIR/BBtargets.txt -n $TMPDIR/BBnames.txt -s $TMPDIR/BBcalls.txt -c $TMPDIR/distance.callgraph.txt -o $`{`f`}`.distances.txt &gt;&gt; $TMPDIR/step$`{`STEP`}`.log 2&gt;&amp;1 #|| FAIL=1
    if [ $? -ne 0 ]; then
      echo -e "\e[93;1m[!]\e[0m Could not calculate distance for $f."
    fi
    #if [ $FAIL -eq 1 ]; then
    #  next_step #Fail asap.
    #fi
  done
  echo ""

  # 最后将所有的距离合并在distance.cfg.txt文件中，等待第二次编译时插桩
  cat $TMPDIR/dot-files/*.distances.txt &gt; $TMPDIR/distance.cfg.txt

fi
next_step
```

计算的逻辑都在`scripts/distance.py`脚本中。

```
##################################
# Main function
##################################
if __name__ == '__main__':
  parser = argparse.ArgumentParser ()
  parser.add_argument ('-d', '--dot', type=str, required=True, help="Path to dot-file representing the graph.")
  parser.add_argument ('-t', '--targets', type=str, required=True, help="Path to file specifying Target nodes.")
  parser.add_argument ('-o', '--out', type=str, required=True, help="Path to output file containing distance for each node.")
  parser.add_argument ('-n', '--names', type=str, required=True, help="Path to file containing name for each node.")
  parser.add_argument ('-c', '--cg_distance', type=str, help="Path to file containing call graph distance.")
  parser.add_argument ('-s', '--cg_callsites', type=str, help="Path to file containing mapping between basic blocks and called functions.")

  args = parser.parse_args ()
  # 读取graph
  print ("\nParsing %s .." % args.dot)
  G = nx.DiGraph(nx.drawing.nx_pydot.read_dot(args.dot))
  print (nx.info(G))
  # 判断当前读取的图是CG还是CFG
  is_cg = "Name: Call graph" in nx.info(G)
  print ("\nWorking in %s mode.." % ("CG" if is_cg else "CFG"))
```

因为首先要计算函数维度的距离，先看CG的处理逻辑

```
# Process as CallGraph
  else:
    # 这里的target是Ftargets文件，即目标点所在的函数
    print ("Loading targets..")
    with open(args.targets, "r") as f:
      targets = []
      for line in f.readlines ():
        line = line.strip ()
        for target in find_nodes(line):
          targets.append (target)

    if (not targets and is_cg):
      print ("No targets available")
      exit(0)

  print ("Calculating distance..")
  with open(args.out, "w") as out, open(args.names, "r") as f:
    for line in f.readlines():
      distance (line.strip()) # 调用distance函数计算距离
```

`distance`函数就是计算的关键函数

```
##################################
# Calculate Distance
##################################
def distance (name): # 这里传入的是每一个函数名
  distance = -1
  # find_node函数返回graph中该名字对应的节点，即传入函数名的函数所有节点
  for n in find_nodes (name): 
    d = 0.0
    i = 0

    if is_cg:
      for t in targets:
        try:
          shortest = nx.dijkstra_path_length (G, n, t) # dijkastr最短路径算法，计算从n到t经过的最短路径
          d += 1.0 / (1.0 + shortest) # 这里计算采用的是调和平均数，取倒数相加最后平均
          i += 1
        except nx.NetworkXNoPath:
          pass
    else:
        ....
    # 如果在迭代后，发现有更短的路径，则更新为最短的距离
    if d != 0 and (distance == -1 or distance &gt; i / d) :
      distance = i / d

  # 将距离写入到文件中
  if distance != -1:
    out.write (name)
    out.write (",")
    out.write (str (distance))
    out.write ("\n")
```

函数维度的距离是 CG 上，能够通过调用链调用到目标函数的那些函数，到达目标函数的距离，因为目标点可能不止一个，可能在不同的函数上，这个时候就需要对不同的目标函数的距离做综合，方法就是将到达不同的目标函数的距离取调和平均数。

然后得到函数维度的距离后，计算基本块维度的距离。

```
# Process as ControlFlowGraph
  caller = ""
  cg_distance = `{``}`
  bb_distance = `{``}`
  if not is_cg :
    # 首先需要函数维度的距离
    if args.cg_distance is None:
      print ("Specify file containing CG-level distance (-c).")
      exit(1)

    # 以及基本块的callsite，即哪些基本块调用了哪些函数
    elif args.cg_callsites is None:
      print ("Specify file containing mapping between basic blocks and called functions (-s).")
      exit(1)

    else:

      caller = args.dot.split(".")
      caller = caller[len(caller)-2]
      print ("Loading cg_distance for function '%s'.." % caller)

      # 加载函数维度距离
      with open(args.cg_distance, 'r') as f:
        for l in f.readlines():
          s = l.strip().split(",")
          cg_distance[s[0]] = float(s[1])

      if not cg_distance:
        print ("Call graph distance file is empty.")
        exit(0)

      # 初始化基本块距离为函数维度距离，取最小的值
      with open(args.cg_callsites, 'r') as f:
        for l in f.readlines():
          s = l.strip().split(",")
          if find_nodes(s[0]):
            if s[1] in cg_distance:
              if s[0] in bb_distance:
                if bb_distance[s[0]] &gt; cg_distance[s[1]]:
                  bb_distance[s[0]] = cg_distance[s[1]]
              else:
                bb_distance[s[0]] = cg_distance[s[1]]

      print ("Adding target BBs (if any)..")
      with open(args.targets, "r") as f:
        for l in f.readlines ():
          s = l.strip().split("/");
          line = s[len(s) - 1]
          if find_nodes(line):
            bb_distance[line] = 0
            print ("Added target BB %s!" % line)
```

然后计算还是`distance`函数

```
else:
      for t_name, bb_d in bb_distance.items():
        di = 0.0
        ii = 0
        for t in find_nodes(t_name):
          try:
            shortest = nx.dijkstra_path_length(G, n, t) # 依然是取最短路径的距离
            di += 1.0 / (1.0 + 10 * bb_d + shortest) # 这里的计算实际为(10*func-distance + bb-distance)，然后取调和平均数。
            ii += 1
          except nx.NetworkXNoPath:
            pass
        if ii != 0:
          d += di / ii
          i += 1

    if d != 0 and (distance == -1 or distance &gt; i / d) :
      distance = i / d
```

到这里，每个可以到达目标块的基本块的距离就计算完成。最后的距离存储在`distance.callgraph.txt`文件中(如果是采用新版本的`gen_distance_fast.py`脚本计算，最后的文件名为`distance.cfg.txt`)。

### <a class="reference-link" name="2.3%20%E6%8F%92%E6%A1%A9%E8%B7%9D%E7%A6%BB"></a>2.3 插桩距离

得到距离值以后，将每个基本块的距离值插桩到程序中，让fuzzer在fuzzing过程中可以得到距离的反馈。

```
export CFLAGS="$COPY_CFLAGS -distance=$TMP_DIR/distance.cfg.txt"
export CXXFLAGS="$COPY_CXXFLAGS -distance=$TMP_DIR/distance.cfg.txt"

# Clean and build subject with distance instrumentation ☕️
pushd $SUBJECT
  make clean
  ./configure --disable-shared
  make xmllint
popd
```

这里用编译选项`-distance=$TMP_DIR/distance.cfg.txt"`将文件路径传递给 AFLGo。

```
if (!TargetsFile.empty()) `{`
    ...

  `}` else if (!DistanceFile.empty()) `{` // 判断distance文件路径是否为空

    std::ifstream cf(DistanceFile);
    if (cf.is_open()) `{`

      std::string line;
      while (getline(cf, line)) `{`

        std::size_t pos = line.find(",");
        std::string bb_name = line.substr(0, pos);
        // 这里读取distance文件中的基本块名字和距离，计算得到的距离是浮点数，但是插桩为了方便都转为整数
        // 所以直接将浮点数值 * 100 取整数部分，存在bb_to_dis的map中
        int bb_dis = (int) (100.0 * atof(line.substr(pos + 1, line.length()).c_str()));

        bb_to_dis.emplace(bb_name, bb_dis);
        basic_blocks.push_back(bb_name);

      `}`
      cf.close();

      is_aflgo = true;

    `}` else `{`
      FATAL("Unable to find %s.", DistanceFile.c_str());
      return false;
    `}`
```

最后是插桩的逻辑部分，在保留原本 AFL 的插桩逻辑的基础上添加 AFLGo 对距离的插桩

```
if (is_aflgo_preprocessing) `{`
   ...

  `}` else `{`
    /* Distance instrumentation */
    /* 这里定义的是LLVM中的整数类型，插桩时需要声明插入数值的类型
    */
    LLVMContext &amp;C = M.getContext();
    IntegerType *Int8Ty  = IntegerType::getInt8Ty(C);
    IntegerType *Int32Ty = IntegerType::getInt32Ty(C);
    IntegerType *Int64Ty = IntegerType::getInt64Ty(C);

    /* 用宏定义__x86_64__区分64位机器和32位机器的插桩数值位数，如果是64位用Int64Ty，32位用Int32Ty
       并且MapCntLoc的位置根据机器位数判断是在Map后的8位(MAP_SIZE + 8)还是4位(MAP_SIZE + 4)
    */
#ifdef __x86_64__
    IntegerType *LargestType = Int64Ty;
    ConstantInt *MapCntLoc = ConstantInt::get(LargestType, MAP_SIZE + 8);
#else
    IntegerType *LargestType = Int32Ty;
    ConstantInt *MapCntLoc = ConstantInt::get(LargestType, MAP_SIZE + 4);
#endif
    ConstantInt *MapDistLoc = ConstantInt::get(LargestType, MAP_SIZE);
    ConstantInt *One = ConstantInt::get(LargestType, 1);

    /* Get globals for the SHM region and the previous location. Note that
       __afl_prev_loc is thread-local. */

    GlobalVariable *AFLMapPtr =
        new GlobalVariable(M, PointerType::get(Int8Ty, 0), false,
                           GlobalValue::ExternalLinkage, 0, "__afl_area_ptr");

    GlobalVariable *AFLPrevLoc = new GlobalVariable(
        M, Int32Ty, false, GlobalValue::ExternalLinkage, 0, "__afl_prev_loc",
        0, GlobalVariable::GeneralDynamicTLSModel, 0, false);

    // 迭代得到每个BB的名字，粒度从Module &gt; Function &gt; BB &gt; I
    for (auto &amp;F : M) `{`

      int distance = -1;

      for (auto &amp;BB : F) `{`

        distance = -1;

        if (is_aflgo) `{`

          /* 这里获取每个基本块名字的方法和预处理阶段一样，取第一个有效指令的位置信息作为基本块名字
          */
          std::string bb_name;
          for (auto &amp;I : BB) `{`
            std::string filename;
            unsigned line;
            getDebugLoc(&amp;I, filename, line);

            if (filename.empty() || line == 0)
              continue;
            std::size_t found = filename.find_last_of("/\\");
            if (found != std::string::npos)
              filename = filename.substr(found + 1);

            bb_name = filename + ":" + std::to_string(line);
            break;
          `}`

          if (!bb_name.empty()) `{`
            /* 比较名字是否相同判断是否是需要插桩的基本块
            */
            if (find(basic_blocks.begin(), basic_blocks.end(), bb_name) == basic_blocks.end()) `{`
              /* 如果开启AFLGO_SELECTIVE选项，则不进入后面插桩的逻辑部分，即AFL的逻辑也只对AFLGo选择的基本块插桩
              */
              if (is_selective)
                continue;

            `}` else `{`

              /* Find distance for BB */
              /* 找到对应基本块的距离
              */
              if (AFL_R(100) &lt; dinst_ratio) `{`
                std::map&lt;std::string,int&gt;::iterator it;
                for (it = bb_to_dis.begin(); it != bb_to_dis.end(); ++it)
                  if (it-&gt;first.compare(bb_name) == 0)
                    distance = it-&gt;second;

              `}`
            `}`
          `}`
        `}`
        /* 进入插桩的逻辑部分，前面的部分是AFL的basicblock edge插桩逻辑
        */
        BasicBlock::iterator IP = BB.getFirstInsertionPt();
        IRBuilder&lt;&gt; IRB(&amp;(*IP));

        if (AFL_R(100) &gt;= inst_ratio) continue;

        /* Make up cur_loc */

        unsigned int cur_loc = AFL_R(MAP_SIZE);

        ConstantInt *CurLoc = ConstantInt::get(Int32Ty, cur_loc);

        /* Load prev_loc */

        LoadInst *PrevLoc = IRB.CreateLoad(AFLPrevLoc);
        PrevLoc-&gt;setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
        Value *PrevLocCasted = IRB.CreateZExt(PrevLoc, IRB.getInt32Ty());

        /* Load SHM pointer */

        LoadInst *MapPtr = IRB.CreateLoad(AFLMapPtr);
        MapPtr-&gt;setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
        Value *MapPtrIdx =
            IRB.CreateGEP(MapPtr, IRB.CreateXor(PrevLocCasted, CurLoc));

        /* Update bitmap */

        LoadInst *Counter = IRB.CreateLoad(MapPtrIdx);
        Counter-&gt;setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));
        Value *Incr = IRB.CreateAdd(Counter, ConstantInt::get(Int8Ty, 1));
        IRB.CreateStore(Incr, MapPtrIdx)
           -&gt;setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));

        /* Set prev_loc to cur_loc &gt;&gt; 1 */

        StoreInst *Store =
            IRB.CreateStore(ConstantInt::get(Int32Ty, cur_loc &gt;&gt; 1), AFLPrevLoc);
        Store-&gt;setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));

        /* 下面是AFLGo的距离插桩部分，将该基本块的距离累加到MapDistLoc的位置上，再递增MapCntLoc位置的值，
           即：MapDistLoc上的值表示seed经过所有的基本块的距离累加和，MapCntLoc上的值表示seed经过的基本块的数量。
        */
        if (distance &gt;= 0) `{`

          ConstantInt *Distance =
              ConstantInt::get(LargestType, (unsigned) distance);

          /* Add distance to shm[MAPSIZE] */

          Value *MapDistPtr = IRB.CreateBitCast(
              IRB.CreateGEP(MapPtr, MapDistLoc), LargestType-&gt;getPointerTo());
          LoadInst *MapDist = IRB.CreateLoad(MapDistPtr);
          MapDist-&gt;setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));

          Value *IncrDist = IRB.CreateAdd(MapDist, Distance);
          IRB.CreateStore(IncrDist, MapDistPtr)
              -&gt;setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));

          /* Increase count at shm[MAPSIZE + (4 or 8)] */

          Value *MapCntPtr = IRB.CreateBitCast(
              IRB.CreateGEP(MapPtr, MapCntLoc), LargestType-&gt;getPointerTo());
          LoadInst *MapCnt = IRB.CreateLoad(MapCntPtr);
          MapCnt-&gt;setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));

          Value *IncrCnt = IRB.CreateAdd(MapCnt, One);
          IRB.CreateStore(IncrCnt, MapCntPtr)
              -&gt;setMetadata(M.getMDKindID("nosanitize"), MDNode::get(C, None));

        `}`

        inst_blocks++;

      `}`
    `}`
  `}`
```

这里突然出现了两个新的共享内存位置，所以分配的时候需要增加分配空间，修改分配空间在`llvm_mode/afl-llvm-rt.o.c`文件中

```
u8  __afl_area_initial[MAP_SIZE + 16]; // 增加16字节，按照最大64位算，一个变量8字节，需要2个变量就是16字节
// ...
// 以及
int __afl_persistent_loop(unsigned int max_cnt) `{`

  static u8  first_pass = 1;
  static u32 cycle_cnt;

  if (first_pass) `{`

    /* Make sure that every iteration of __AFL_LOOP() starts with a clean slate.
       On subsequent calls, the parent will take care of that, but on the first
       iteration, it's our job to erase any trace of whatever happened
       before the loop. */

    if (is_persistent) `{`

      memset(__afl_area_ptr, 0, MAP_SIZE + 16); // 同上
      __afl_area_ptr[0] = 1;
      __afl_prev_loc = 0;
    `}`

     ...
```

到这里，插桩的逻辑结束。

### <a class="reference-link" name="2.4%20AFL%20%E4%BF%AE%E6%94%B9"></a>2.4 AFL 修改

插桩时增加了 distance 的 feedback，AFL 也需要增加对应的逻辑处理，fuzzing 的部分修改主要都在`afl-fuzz.c`文件中

首先是增加了一些变量，具体用处作者都写了就不赘述了。

```
static double cur_distance = -1.0;     /* Distance of executed input       */
static double max_distance = -1.0;     /* Maximal distance for any input   */
static double min_distance = -1.0;     /* Minimal distance for any input   */
static u32 t_x = 10;                  /* Time to exploitation (Default: 10 min) */
```

**<a class="reference-link" name="2.4.1%20%E8%8E%B7%E5%8F%96%E8%B7%9D%E7%A6%BB"></a>2.4.1 获取距离**

那么 fuzzer 是如何获取程序反馈的距离的？首先同样也需要分配与插桩时同样多的空间接收 bitmap 的信息。

```
/* Allocate 24 byte more for distance info */ // 这里作者的注释应该写错了，是16 byte
  shm_id = shmget(IPC_PRIVATE, MAP_SIZE + 16, IPC_CREAT | IPC_EXCL | 0600);
```

计算 bitmap 信息的函数是`has_new_bits`，判断 bitmap 是否覆盖了新的 bit，表示有新的 edge coverage

```
static inline u8 has_new_bits(u8* virgin_map) `{`
/* 同样也根据宏定义区分机器字长 */
#ifdef __x86_64__

  u64* current = (u64*)trace_bits;
  u64* virgin  = (u64*)virgin_map;

  u32  i = (MAP_SIZE &gt;&gt; 3);

  /* Calculate distance of current input to targets */
  /* 获取distance的变量地址和count的地址，分别是bitmap紧接着的后两个变量。 */
  u64* total_distance = (u64*) (trace_bits + MAP_SIZE);
  u64* total_count = (u64*) (trace_bits + MAP_SIZE + 8);

  /* 当前seed的距离就是总距离 / 总块数 */
  if (*total_count &gt; 0)
    cur_distance = (double) (*total_distance) / (double) (*total_count);
  else
    cur_distance = -1.0;

#else

  u32* current = (u32*)trace_bits;
  u32* virgin  = (u32*)virgin_map;

  u32  i = (MAP_SIZE &gt;&gt; 2);

  /* Calculate distance of current input to targets */
  u32* total_distance = (u32*)(trace_bits + MAP_SIZE);
  u32* total_count = (u32*)(trace_bits + MAP_SIZE + 4);

  if (*total_count &gt; 0) `{`
    cur_distance = (double) (*total_distance) / (double) (*total_count);
  else
    cur_distance = -1.0;

#endif /* ^__x86_64__ */
```

经过`has_new_bits`函数计算后，seed 的距离就存放在变量`cur_distance`中，在得到距离后，更新当前 seed 的距离和最大最小值

`add_to_queue`函数

```
q-&gt;distance = cur_distance;
  if (cur_distance &gt; 0) `{`

    if (max_distance &lt;= 0) `{`
      max_distance = cur_distance;
      min_distance = cur_distance;
    `}`
    if (cur_distance &gt; max_distance) max_distance = cur_distance;
    if (cur_distance &lt; min_distance) min_distance = cur_distance;

  `}`
```

`calibrate_case`函数

```
if (q-&gt;distance &lt;= 0) `{`

      /* This calculates cur_distance */
      has_new_bits(virgin_bits);

      q-&gt;distance = cur_distance;
      if (cur_distance &gt; 0) `{`

        if (max_distance &lt;= 0) `{`
          max_distance = cur_distance;
          min_distance = cur_distance;
        `}`
        if (cur_distance &gt; max_distance) max_distance = cur_distance;
        if (cur_distance &lt; min_distance) min_distance = cur_distance;

      `}`

    `}`
```

有了 seed 的距离后，如何引导 fuzzer 朝向目标节点探索呢，这里就用到了一个算法叫做**模拟退火算法**。

<a class="reference-link" name="2.4.2%20%E6%A8%A1%E6%8B%9F%E9%80%80%E7%81%AB"></a>**2.4.2 模拟退火**

简介来自于维基百科

> 模拟退火来自[冶金学](https://zh.wikipedia.org/wiki/%E5%86%B6%E9%87%91%E5%AD%B8)的专有名词[退火](https://zh.wikipedia.org/wiki/%E9%80%80%E7%81%AB)。退火是将材料加热后再经特定速率冷却，目的是增大[晶粒](https://zh.wikipedia.org/wiki/%E6%99%B6%E9%AB%94)的体积，并且减少晶格中的缺陷。材料中的原子原来会停留在使[内能](https://zh.wikipedia.org/wiki/%E5%85%A7%E8%83%BD)有局部最小值的位置，加热使能量变大，原子会离开原来位置，而随机在其他位置中移动。退火冷却时速度较慢，使得原子有较多可能可以找到内能比原先更低的位置。
模拟退火的原理也和金属退火的原理近似：我们将热力学的理论套用到统计学上，将搜寻空间内每一点想像成空气内的分子；分子的能量，就是它本身的动能；而搜寻空间内的每一点，也像空气分子一样带有“能量”，以表示该点对命题的合适程度。算法先以搜寻空间内一个任意点作起始：每一步先选择一个“邻居”，然后再计算从现有位置到达“邻居”的概率。
可以证明，模拟退火算法所得解[依概率收敛](https://zh.wikipedia.org/wiki/%E4%BE%9D%E6%A6%82%E7%8E%87%E6%94%B6%E6%95%9B)到全局最优解。

实际上，其实模拟退火算法就是以一定概率能够接受非最优解，来跳出局部最优解，达到全局最优。因为贪心算法每次都只选择当前的最有解，但是很可能会陷入局部最优，不一定能搜索到全局最优解，例如爬山算法，以图为例：

[![](https://p0.ssl.qhimg.com/t01ac6cf924ff35a5cd.png)](https://p0.ssl.qhimg.com/t01ac6cf924ff35a5cd.png)

假设C点为当前解，爬山算法搜索到A点这个局部最优解就会停止搜索，因为在A点无论向那个方向小幅度移动都不能得到更优的解。

但模拟退火的搜索过程引入了随机因素。模拟退火算法**以一定的概率**来接受一个比当前解要差的解，因此**有可能**会跳出这个局部的最优解，达到全局的最优解。还是以上图为例，模拟退火算法在搜索到局部最优解A后，会**以一定的概率**接受到E的移动。也许经过几次这样的不是局部最优的移动后会到达D点，于是就跳出了局部最大值A。

那么 AFLGo 是怎么应用模拟退火算法的呢？是用在了 seed 的 **power scheduling** 上。

AFL 的`calculate_score`函数是对 seed 进行打分，打分的分数决定对 seed fuzzing的时间长度，按照直觉来说，距离越近的 seed，有更大的概率能够到达目标点，则应该分配更多的时间给这些 seed。但是这样就会陷入上面所说的局部最优的困局里，于是 AFLGo 采用时间作为一个划分阶段的 metric，当 fuzzing 的时间在预定的时间内时，让时间较为公平的分配给每个 seed 上，当 fuzzing 时间超过了预定的时间后，时间就集中分配给哪些距离较近的 seed 上。这样可以在前期避免还未广泛探索就过度集中的局部最优的情况。

```
u64 cur_ms = get_cur_time(); 
  u64 t = (cur_ms - start_time) / 1000; // 计算当前运行时间
  double progress_to_tx = ((double) t) / ((double) t_x * 60.0); // 进度条，距离利用阶段的比例还有多少

  double T;

  //TODO Substitute functions of exp and log with faster bitwise operations on integers
  // 这里根据fuzzing前的选项选择冷却时间的模型，是log函数，还是线性，还是指数等等
  switch (cooling_schedule) `{`
    case SAN_EXP:

      T = 1.0 / pow(20.0, progress_to_tx);

      break;

    case SAN_LOG:

      // alpha = 2 and exp(19/2) - 1 = 13358.7268297
      T = 1.0 / (1.0 + 2.0 * log(1.0 + progress_to_tx * 13358.7268297));

      break;

    case SAN_LIN:

      T = 1.0 / (1.0 + 19.0 * progress_to_tx);

      break;

    case SAN_QUAD:

      T = 1.0 / (1.0 + 19.0 * pow(progress_to_tx, 2));

      break;

    default:
      PFATAL ("Unkown Power Schedule for Directed Fuzzing");
  `}`

  double power_factor = 1.0;
  if (q-&gt;distance &gt; 0) `{`

    double normalized_d = 0; // when "max_distance == min_distance", we set the normalized_d to 0 so that we can sufficiently explore those testcases whose distance &gt;= 0.
    if (max_distance != min_distance)
      // 首先归一化距离
      normalized_d = (q-&gt;distance - min_distance) / (max_distance - min_distance);

    if (normalized_d &gt;= 0) `{`

        double p = (1.0 - normalized_d) * (1.0 - T) + 0.5 * T; // 计算p值，由距离和时间共同决定
        power_factor = pow(2.0, 2.0 * (double) log2(MAX_FACTOR) * (p - 0.5)); // 最后根据p值计算得到factor，

    `}`// else WARNF ("Normalized distance negative: %f", normalized_d);

  `}`

  perf_score *= power_factor; // 乘上factor得到最后的score
```

`cooling_schedule`的选择来源于用户在 fuzzing 前传入的参数

```
case 'z': /* Cooling schedule for Directed Fuzzing */

        if (!stricmp(optarg, "exp"))
          cooling_schedule = SAN_EXP;
        else if (!stricmp(optarg, "log"))
          cooling_schedule = SAN_LOG;
        else if (!stricmp(optarg, "lin"))
          cooling_schedule = SAN_LIN;
        else if (!stricmp(optarg, "quad"))
          cooling_schedule = SAN_QUAD;
        else
          PFATAL ("Unknown value for option -z");

        break;
```

时间的设定来源于：

```
case 'c': `{` /* cut-off time for cooling schedule */

          u8 suffix = 'm';

          if (sscanf(optarg, "%u%c", &amp;t_x, &amp;suffix) &lt; 1 ||
              optarg[0] == '-') FATAL("Bad syntax used for -c");

          switch (suffix) `{`

            case 's': t_x /= 60; break;
            case 'm': break;
            case 'h': t_x *= 60; break;
            case 'd': t_x *= 60 * 24; break;

            default:  FATAL("Unsupported suffix or bad syntax for -c");

          `}`

        `}`

        break;
```

最后存在`t_x`变量中。

而`perf_score`影响的是 havoc 阶段的时间

```
orig_perf = perf_score = calculate_score(queue_cur);

    ...

  havoc_stage:

  stage_cur_byte = -1;

  /* The havoc stage mutation code is also invoked when splicing files; if the
     splice_cycle variable is set, generate different descriptions and such. */

  if (!splice_cycle) `{`

    stage_name  = "havoc";
    stage_short = "havoc";
    stage_max   = (doing_det ? HAVOC_CYCLES_INIT : HAVOC_CYCLES) *
                  perf_score / havoc_div / 100; // stage_max决定havoc的次数

  `}` else `{`

    static u8 tmp[32];

    perf_score = orig_perf;

    sprintf(tmp, "splice %u", splice_cycle);
    stage_name  = tmp;
    stage_short = "splice";
    stage_max   = SPLICE_HAVOC * perf_score / havoc_div / 100; // stage_max决定havoc的次数

  `}`
```



## 3. 存在的缺陷

这篇工作发在2017年，在当时首次提出了 directed 的方向，后来很多的 directed fuzzing 的工作都借鉴其做法，主要的核心都是围绕 distance 来引导的。但同时也存在一些设计和实现上的缺陷。

首先是设计上，因为 distance 的计算为了方便，只采用了最短路径的值计算 distance，但这带来一个问题，如果同时有多条路径能够到达目标节点，那么除了最短路径之外的路径则会被忽略掉，这样是不合理的。2018年 CCS 的论文[Hawkeye](https://www.researchgate.net/profile/Hongxu-Chen-4/publication/328327299_Hawkeye_Towards_a_Desired_Directed_Grey-box_Fuzzer/links/5bcbe6c0299bf17a1c643e4d/Hawkeye-Towards-a-Desired-Directed-Grey-box-Fuzzer.pdf)首次指出这个问题，该文章的解决方法是同时增加一个 function similarity 的 metric，综合 distance 与 function similarity 两个指标来判断。后续还有很多 directed fuzzing 提出了很多的新指标，比 distance 更加精细，比如 sequence，constraint 等等。

其次是实现上的问题，CG 的生成采用的是 llvm 自带的 pass 生成，但是静态分析无法分析一些特殊的函数调用情况，例如 indirect call，virtual function 等等，这些特殊的函数调用在静态分析中是无法分析的，只有在动态执行中才能够确认调用的哪一个函数。这样会导致在某些程序上一些路径上没有反馈，甚至会变得没有路径可达。Hawkeye 同样也指出这个问题，它的解决方法是用指针分析的方法补上可能的 indirect call，让 CG 更加完整。

Hawkeye 这篇文章几乎就是对 AFLGo 的全面改进，但其未开源，所以这些方法没有源码可以进行实现的借鉴。

以及模拟退火算法的实现，由于 AFLGo 的模拟退火算法需要用户自己设定时间决定 exploration-exploitation 的分界时间，但是经过笔者的测试，`t_x`的选择很难找到一个通用的时间，只能针对不同的时间做大量的测试后才能确定一个较好的时间范围，但这样其实需要浪费大量时间去确认一个时间边界，最好是能够自适应的根据 fuzzing 调整阶段，但目前没有 fuzzer 做到这件事。

如果想了解其他 directed fuzzing 的工作，推荐这篇[SoK](https://arxiv.org/pdf/2005.11907.pdf)。

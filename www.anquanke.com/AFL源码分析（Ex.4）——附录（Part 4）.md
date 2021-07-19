> 原文链接: https://www.anquanke.com//post/id/246080 


# AFL源码分析（Ex.4）——附录（Part 4）


                                阅读量   
                                **241562**
                            
                        |
                        
                                                                                    



##### 译文声明

本文是翻译文章，文章原作者，文章来源：
                                <br>原文地址：[]()

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t019bded1e48f69c18e.jpg)](https://p2.ssl.qhimg.com/t019bded1e48f69c18e.jpg)



## 0. 写在前面

此文章主要是对`AFL`仓库中`doc`目录下的所有文档进行翻译。
- [x] env_variables.txt(环境变量手册) —— 历史文章(Part 1)
- [x] historical_notes.txt(前世今生)—— 本文
- [x] INSTALL(安装说明)—— 本文
- [x] life_pro_tips.txt(使用技巧) —— 历史文章(Part 1)
- [x] notes_for_asan.txt(`ASAN`模式手册) —— 历史文章(Part 2)
- [x] parallel_fuzzing.txt(同步`fuzz`模式手册) —— 历史文章(Part 2)
- [x] perf_tips.txt(故障排除手册) —— 历史文章(Part 4)
- [x] QuickStartGuide.txt(快速上手) —— 历史文章(Part 4)
- [x] sister_projects.txt(子项目手册)—— 本文
- [x] status_screen.txt(GUI手册) —— 历史文章(Part 4)
- [ ] technical_details.txt(技术白皮书)
- [ ] ../README.md(自述文件)
后续附录将继续翻译以上列表中的文章。



## 1. sister_projects.txt(子项目手册)

本文档列出了一些受`AFL`启发、衍生自、设计用于或旨在与`AFL`集成的项目。 有关一般说明手册，请参阅自述文件。

### <a class="reference-link" name="1.1%20%E5%A4%9A%E8%AF%AD%E8%A8%80/%E5%A4%9A%E7%8E%AF%E5%A2%83%E6%94%AF%E6%8C%81%E7%9A%84%E9%A1%B9%E7%9B%AE"></a>1.1 多语言/多环境支持的项目

#### <a class="reference-link" name="1.1.1%20Python%20AFL%20(Jakub%20Wilk)"></a>1.1.1 Python AFL (Jakub Wilk)

描述：此项目允许您对`Python`程序进行模糊测试。 此项目使用自定义检测和其自身实现的`forkserver`。

项目地址：[http://jwilk.net/software/python-afl](http://jwilk.net/software/python-afl)

#### <a class="reference-link" name="1.1.2%20Go-fuzz%20(Dmitry%20Vyukov)"></a>1.1.2 Go-fuzz (Dmitry Vyukov)

描述：受`AFL`启发的针对`Go`语言目标的`fuzzer`：

项目地址：[https://github.com/dvyukov/go-fuzz](https://github.com/dvyukov/go-fuzz)

#### <a class="reference-link" name="1.1.3%20afl.rs%20(Keegan%20McAllister)"></a>1.1.3 afl.rs (Keegan McAllister)

描述：允许使用`AFL`轻松的对`Rust`程序的功能进行`fuzz`测试(使用`LLVM`模式)。

项目地址：[https://github.com/kmcallister/afl.rs](https://github.com/kmcallister/afl.rs)

#### <a class="reference-link" name="1.1.4%20OCaml%20support%20(KC%20Sivaramakrishnan)"></a>1.1.4 OCaml support (KC Sivaramakrishnan)

描述：添加与`AFL`兼容性的功能，以允许对`OCaml`程序进行`fuzz`测试。

项目地址1：[https://github.com/ocamllabs/opam-repo-dev/pull/23](https://github.com/ocamllabs/opam-repo-dev/pull/23)<br>
项目地址2：[http://canopy.mirage.io/Posts/Fuzzing](http://canopy.mirage.io/Posts/Fuzzing)

#### <a class="reference-link" name="1.1.5%20AFL%20for%20GCJ%20Java%20and%20other%20GCC%20frontends%20(-)"></a>1.1.5 AFL for GCJ Java and other GCC frontends (-)

描述：`GCC Java`程序实际上是开箱即用的——只需将`afl-gcc`重命名为`afl-gcj`。不幸的是，默认情况下，`GCJ`中未处理的异常不会导致`abort()`被调用，因此您需要手动添加一个顶级异常处理程序，该处理程序需要以`SIGABRT`或等效的方式退出。<br>
其他`GCC`支持的语言应该很容易上手，但可能会面临类似的问题。有关选项列表，请参阅 [https://gcc.gnu.org/frontends.html。](https://gcc.gnu.org/frontends.html%E3%80%82)

#### <a class="reference-link" name="1.1.6%20AFL-style%20in-process%20fuzzer%20for%20LLVM%20(Kostya%20Serebryany)"></a>1.1.6 AFL-style in-process fuzzer for LLVM (Kostya Serebryany)

描述：提供一个基于进化算法的`fuzz`器，允许在没有`fork/execve`开销的情况下对某些程序进行模糊测试。(类似的功能现在可用作 `../llvm_mode/README.llvm`中描述的“持久”功能)

项目地址：[http://llvm.org/docs/LibFuzzer.html](http://llvm.org/docs/LibFuzzer.html)

#### <a class="reference-link" name="1.1.7%20AFL%20fixup%20shim%20(Ben%20Nagy)"></a>1.1.7 AFL fixup shim (Ben Nagy)

描述：允许使用没有`C/.so`绑定的任意语言编写`AFL_POST_LIBRARY`下游处理器。包括`Go`中的示例。

项目地址：[https://github.com/bnagy/aflfix](https://github.com/bnagy/aflfix)

#### <a class="reference-link" name="1.1.8%20TriforceAFL%20(Tim%20Newsham%20and%20Jesse%20Hertz)"></a>1.1.8 TriforceAFL (Tim Newsham and Jesse Hertz)

描述：允许`AFL`利用`QEMU`全系统仿真模式对操作系统和其他的特殊二进制文件作为目标进行测试。

项目地址：[https://www.nccgroup.trust/us/about-us/newsroom-and-events/blog/2016/june/project-triforce-run-afl-on-everything/](https://www.nccgroup.trust/us/about-us/newsroom-and-events/blog/2016/june/project-triforce-run-afl-on-everything/)

#### <a class="reference-link" name="1.1.9%20WinAFL%20(Ivan%20Fratric)"></a>1.1.9 WinAFL (Ivan Fratric)

描述：顾名思义，允许您对`Windows`二进制文件进行`fuzz`(使用`DynamoRio`)。

项目地址：[https://github.com/ivanfratric/winafl](https://github.com/ivanfratric/winafl)

项目地址(一种替代方案)：[https://github.com/carlosgprado/BrundleFuzz/](https://github.com/carlosgprado/BrundleFuzz/)

### <a class="reference-link" name="1.2%20%E7%BD%91%E7%BB%9C%E6%B5%8B%E8%AF%95%E9%A1%B9%E7%9B%AE"></a>1.2 网络测试项目

#### <a class="reference-link" name="1.2.1%20Preeny%20(Yan%20Shoshitaishvili)"></a>1.2.1 Preeny (Yan Shoshitaishvili)

描述：此项目提供了一种相当简单的方法来修补动态链接的以网络为中心的程序从文件中读取数据包以及不执行`fork`操作。此项目不是特定于 AFL 开发的，但被许多用户反馈是相当有用的项目。此项目需要一些汇编的知识。

项目地址：[https://github.com/zardus/preeny](https://github.com/zardus/preeny)

### <a class="reference-link" name="1.3%20%E5%88%86%E5%B8%83%E5%BC%8F%20fuzzer%20%E5%92%8C%E7%9B%B8%E5%85%B3%E8%87%AA%E5%8A%A8%E5%8C%96%E9%A1%B9%E7%9B%AE"></a>1.3 分布式 fuzzer 和相关自动化项目

#### <a class="reference-link" name="1.3.1%20roving%20(Richo%20Healey)"></a>1.3.1 roving (Richo Healey)

描述：此项目用于在一组机器上轻松运行管理`AFL`的客户端-服务器架构(`C-S`架构)。您最好不要在面向`Internet`或搭建在其他不受信任环境中的系统上使用它。

项目地址：[https://github.com/richo/roving](https://github.com/richo/roving)

#### <a class="reference-link" name="1.3.2%20Distfuzz-AFL%20(Martijn%20Bogaard)"></a>1.3.2 Distfuzz-AFL (Martijn Bogaard)

描述：简化对远程机器上`afl-fuzz`实例的管理。作者指出，当前的实现并不安全，不应在`Internet`上使用。

项目地址：[https://github.com/MartijnB/disfuzz-afl](https://github.com/MartijnB/disfuzz-afl)

#### <a class="reference-link" name="1.3.3%20AFLDFF%20(quantumvm)"></a>1.3.3 AFLDFF (quantumvm)

描述：用于管理`AFL`实例的美观的`GUI`。

项目地址：[https://github.com/quantumvm/AFLDFF](https://github.com/quantumvm/AFLDFF)

#### <a class="reference-link" name="1.3.4%20afl-launch%20(Ben%20Nagy)"></a>1.3.4 afl-launch (Ben Nagy)

描述：带有简单`CLI`的批处理`AFL`启动器实用程序。

项目地址：[https://github.com/bnagy/afl-launch](https://github.com/bnagy/afl-launch)

#### <a class="reference-link" name="1.3.5%20AFL%20Utils%20(rc0r)"></a>1.3.5 AFL Utils (rc0r)

描述：此项目用于简化对发现的崩溃进行分类以及启动并行`fuzzer`实例等操作。

项目地址：[https://github.com/rc0r/afl-utils](https://github.com/rc0r/afl-utils)

项目地址(一种替代方案)：[https://github.com/floyd-fuh/afl-crash-analyzer](https://github.com/floyd-fuh/afl-crash-analyzer)

#### <a class="reference-link" name="1.3.6%20afl-fuzzing-scripts%20(Tobias%20Ospelt)"></a>1.3.6 afl-fuzzing-scripts (Tobias Ospelt)

描述：简化启动多个并行`AFL`实例的过程。

项目地址：[https://github.com/floyd-fuh/afl-fuzzing-scripts/](https://github.com/floyd-fuh/afl-fuzzing-scripts/)

#### <a class="reference-link" name="1.3.7%20afl-sid%20(Jacek%20Wielemborek)"></a>1.3.7 afl-sid (Jacek Wielemborek)

描述：允许用户通过`Docker`更方便地构建和部署`AFL`。

项目地址：[https://github.com/d33tah/afl-sid](https://github.com/d33tah/afl-sid)

项目地址(一种替代方案)：[https://github.com/ozzyjohnson/docker-afl](https://github.com/ozzyjohnson/docker-afl)

#### <a class="reference-link" name="1.3.8%20afl-monitor%20(Paul%20S.%20Ziegler)"></a>1.3.8 afl-monitor (Paul S. Ziegler)

描述：提供有关正在运行的`AFL`作业的更详细和通用的统计数据。

项目地址：[https://github.com/reflare/afl-monitor](https://github.com/reflare/afl-monitor)

### <a class="reference-link" name="1.4%20%E5%B4%A9%E6%BA%83%E5%88%86%E7%B1%BB%E3%80%81%E8%A6%86%E7%9B%96%E7%8E%87%E5%88%86%E6%9E%90%E5%92%8C%E5%85%B6%E4%BB%96%E9%85%8D%E5%A5%97%E5%88%86%E6%9E%90%E5%B7%A5%E5%85%B7%EF%BC%9A"></a>1.4 崩溃分类、覆盖率分析和其他配套分析工具：

#### <a class="reference-link" name="1.4.1%20afl-crash-analyzer%20(Tobias%20Ospelt)"></a>1.4.1 afl-crash-analyzer (Tobias Ospelt)

描述：此项目使寻找和注释导致测试目标崩溃的输入用例更容易。

项目地址：[https://github.com/floyd-fuh/afl-crash-analyzer/](https://github.com/floyd-fuh/afl-crash-analyzer/)

#### <a class="reference-link" name="1.4.2%20Crashwalk%20(Ben%20Nagy)"></a>1.4.2 Crashwalk (Ben Nagy)

描述：`AFL`感知工具，用于对导致测试目标崩溃的输入用例进行注释和排序。

项目地址：[https://github.com/bnagy/crashwalk](https://github.com/bnagy/crashwalk)

#### <a class="reference-link" name="1.4.3%20afl-cov%20(Michael%20Rash)"></a>1.4.3 afl-cov (Michael Rash)

描述：根据`afl-fuzz`的输出队列生成可读的覆盖率数据。

项目地址：[https://github.com/mrash/afl-cov](https://github.com/mrash/afl-cov)

#### <a class="reference-link" name="1.4.4%20afl-sancov%20(Bhargava%20Shastry)"></a>1.4.4 afl-sancov (Bhargava Shastry)

描述：类似于`afl-cov`，但使用`clang sanitizer`检测异常。

项目地址：[https://github.com/bshastry/afl-sancov](https://github.com/bshastry/afl-sancov)

#### <a class="reference-link" name="1.4.5%20RecidiVM%20(Jakub%20Wilk)"></a>1.4.5 RecidiVM (Jakub Wilk)

描述：使用`ASAN`或`MSAN`进行模糊测试时，可以使用此项目轻松估计内存使用限制。

项目地址：[http://jwilk.net/software/recidivm](http://jwilk.net/software/recidivm)

#### <a class="reference-link" name="1.4.6%20aflize%20(Jacek%20Wielemborek)"></a>1.4.6 aflize (Jacek Wielemborek)

描述：自动构建支持`AFL`的`Debian`软件包版本。

项目地址：[https://github.com/d33tah/aflize](https://github.com/d33tah/aflize)

#### <a class="reference-link" name="1.4.7%20afl-ddmin-mod%20(Markus%20Teufelberger)"></a>1.4.7 afl-ddmin-mod (Markus Teufelberger)

描述：此项目是`afl-tmin`的一种变体，它使用更复杂(但更慢)的最小化算法。

项目地址：[https://github.com/MarkusTeufelberger/afl-ddmin-mod](https://github.com/MarkusTeufelberger/afl-ddmin-mod)

#### <a class="reference-link" name="1.4.8%20afl-kit%20(Kuang-che%20Wu)"></a>1.4.8 afl-kit (Kuang-che Wu)

描述：使用附加功能替换`afl-cmin`和`afl-tmin`，例如基于标准错误模式过滤崩溃的能力。

项目地址：[https://github.com/kcwu/afl-kit](https://github.com/kcwu/afl-kit)

### <a class="reference-link" name="1.5%20%E6%9C%89%E5%B1%80%E9%99%90%E6%80%A7%E7%9A%84%E6%88%96%E5%AE%9E%E9%AA%8C%E6%80%A7%E7%9A%84%E5%B7%A5%E5%85%B7%EF%BC%9A"></a>1.5 有局限性的或实验性的工具：

#### <a class="reference-link" name="1.5.1%20Cygwin%20support%20(Ali%20Rizvi-Santiago)"></a>1.5.1 Cygwin support (Ali Rizvi-Santiago)

描述：正如项目名字所说。根据作者的说法，此项目“主要”将`AFL`移植到`Windows`。欢迎报告`Bug`！

项目地址：[https://github.com/arizvisa/afl-cygwin](https://github.com/arizvisa/afl-cygwin)

#### <a class="reference-link" name="1.5.2%20Pause%20and%20resume%20scripts%20(Ben%20Nagy)"></a>1.5.2 Pause and resume scripts (Ben Nagy)

描述：用于简单自动化暂停和恢复`fuzzer`实例组的项目。

项目地址：[https://github.com/bnagy/afl-trivia](https://github.com/bnagy/afl-trivia)

#### <a class="reference-link" name="1.5.3%20Static%20binary-only%20instrumentation%20(Aleksandar%20Nikolich)"></a>1.5.3 Static binary-only instrumentation (Aleksandar Nikolich)

描述：此项目允许对黑盒二进制文件进行静态检测(即，通过提前修改二进制文件，而不是在运行时对其进行转译)。与`QEMU`相比，作者报告了更好的性能，但偶尔会出现无符号二进制文件的转译错误。

项目地址：[https://github.com/vrtadmin/moflow/tree/master/afl-dyninst](https://github.com/vrtadmin/moflow/tree/master/afl-dyninst)

#### <a class="reference-link" name="1.5.4%20AFL%20PIN%20(Parker%20Thompson)"></a>1.5.4 AFL PIN (Parker Thompson)

描述：早期的英特尔`PIN`检测支持(在使用运行速度更快的`QEMU`之前)。

项目地址：[https://github.com/mothran/aflpin](https://github.com/mothran/aflpin)

#### <a class="reference-link" name="1.5.5%20AFL-style%20instrumentation%20in%20llvm%20(Kostya%20Serebryany)"></a>1.5.5 AFL-style instrumentation in llvm (Kostya Serebryany)

描述：允许在编译器级别向待测程序注入`AFL`等效代码桩。`AFL`目前不支持这一点，但在其他项目中可能有用。

项目地址：[https://code.google.com/p/address-sanitizer/wiki/AsanCoverage#Coverage_counters](https://code.google.com/p/address-sanitizer/wiki/AsanCoverage#Coverage_counters)

#### <a class="reference-link" name="1.5.6%20AFL%20JS%20(Han%20Choongwoo)"></a>1.5.6 AFL JS (Han Choongwoo)

描述：此项目提供一次性优化以加速针对`JavaScriptCore`的模糊测试(现在可能被`LLVM`延迟`forkserver init`取代——请参阅 `llvm_mode/README.llvm`)。

项目地址：[https://github.com/tunz/afl-fuzz-js](https://github.com/tunz/afl-fuzz-js)

#### <a class="reference-link" name="1.5.7%20AFL%20harness%20for%20fwknop%20(Michael%20Rash)"></a>1.5.7 AFL harness for fwknop (Michael Rash)

描述：此项目提供与`AFL`进行相当复杂的集成的一个例子。

项目地址：[https://github.com/mrash/fwknop/tree/master/test/afl](https://github.com/mrash/fwknop/tree/master/test/afl)

#### <a class="reference-link" name="1.5.8%20Building%20harnesses%20for%20DNS%20servers%20(Jonathan%20Foote,%20Ron%20Bowes)"></a>1.5.8 Building harnesses for DNS servers (Jonathan Foote, Ron Bowes)

描述：这两篇文章概述了一般原则并展示了一些示例代码。

项目地址1：[https://www.fastly.com/blog/how-to-fuzz-server-american-fuzzy-lop](https://www.fastly.com/blog/how-to-fuzz-server-american-fuzzy-lop)<br>
项目地址2：[https://goo.gl/j9EgFf](https://goo.gl/j9EgFf)

#### <a class="reference-link" name="1.5.9%20Fuzzer%20shell%20for%20SQLite%20(Richard%20Hipp)"></a>1.5.9 Fuzzer shell for SQLite (Richard Hipp)

描述：一个简单的`SQL shell`，专为对其底层库进行`fuzz`而设计。

项目地址：[http://www.sqlite.org/src/artifact/9e7e273da2030371](http://www.sqlite.org/src/artifact/9e7e273da2030371)

#### <a class="reference-link" name="1.5.10%20Support%20for%20Python%20mutation%20modules%20(Christian%20Holler)"></a>1.5.10 Support for Python mutation modules (Christian Holler)

项目地址：[https://github.com/choller/afl/blob/master/docs/mozilla/python_modules.txt](https://github.com/choller/afl/blob/master/docs/mozilla/python_modules.txt)

#### <a class="reference-link" name="1.5.11%20Support%20for%20selective%20instrumentation%20(Christian%20Holler)"></a>1.5.11 Support for selective instrumentation (Christian Holler)

项目地址：[https://github.com/choller/afl/blob/master/docs/mozilla/partial_instrumentation.txt](https://github.com/choller/afl/blob/master/docs/mozilla/partial_instrumentation.txt)

#### <a class="reference-link" name="1.5.12%20Kernel%20fuzzing%20(Dmitry%20Vyukov)"></a>1.5.12 Kernel fuzzing (Dmitry Vyukov)

描述：应用于对系统调用进行`fuzz`的类似指导方法

项目地址1：[https://github.com/google/syzkaller/wiki/Found-Bugs](https://github.com/google/syzkaller/wiki/Found-Bugs)<br>
项目地址2：[https://github.com/dvyukov/linux/commit/33787098ffaaa83b8a7ccf519913ac5fd6125931](https://github.com/dvyukov/linux/commit/33787098ffaaa83b8a7ccf519913ac5fd6125931)<br>
项目地址3：[http://events.linuxfoundation.org/sites/events/files/slides/AFL%20filesystem%20fuzzing%2C%20Vault%202016_0.pdf](http://events.linuxfoundation.org/sites/events/files/slides/AFL%20filesystem%20fuzzing%2C%20Vault%202016_0.pdf)

#### <a class="reference-link" name="1.5.13%20Android%20support%20(ele7enxxh)"></a>1.5.13 Android support (ele7enxxh)

描述：此项目基于有点过时的`AFL`版本。

项目地址：[https://github.com/ele7enxxh/android-afl](https://github.com/ele7enxxh/android-afl)

#### <a class="reference-link" name="1.5.14%20CGI%20wrapper%20(floyd)"></a>1.5.14 CGI wrapper (floyd)

描述：此项目提供对`CGI`脚本进行`fuzz`的能力。

项目地址：[https://github.com/floyd-fuh/afl-cgi-wrapper](https://github.com/floyd-fuh/afl-cgi-wrapper)

#### <a class="reference-link" name="1.5.15%20Fuzzing%20difficulty%20estimation%20(Marcel%20Boehme)"></a>1.5.15 Fuzzing difficulty estimation (Marcel Boehme)

描述：此项目是`AFL`的一个分支，试图量化在模糊测试工作中的任何一点找到额外路径或崩溃的可能性。

项目地址：[https://github.com/mboehme/pythia](https://github.com/mboehme/pythia)



## 2. historical_notes.txt(前世今生)

本文档讨论了`American Fuzzy Lop`的一些高级设计决策的基本原理。它是从与`Rob Graham`的讨论中采用的。有关一般说明手册，请参阅自述文件，有关其他实施级别的见解，请参阅`technology_details.txt`。

### <a class="reference-link" name="2.1%20%E7%A0%94%E7%A9%B6%E8%83%8C%E6%99%AF"></a>2.1 研究背景

简而言之，`afl-fuzz`的设计灵感主要来自于`Tavis Ormandy`在`2007`年所做的工作。`Tavis`做了一些非常有说服力的实验，使用`gcov`块覆盖从大量数据中选择最佳测试用例，然后使用它们作为传统模糊测试工作流程的起点。(所谓“有说服力”是指发现并消除大量有趣的漏洞。)

与此同时，`Tavis`和我都对优化模糊测试感兴趣。`Tavis`进行了他的实验，而我正在开发一种名为`bunny-the-fuzzer`的工具，该工具于`2007`年在某个地方发布。

`Bunny`使用了一种与`afl-fuzz`没有太大区别的生成算法，但也尝试推理各种输入位与程序内部状态之间的关系，希望从中得出一些额外的优化点。推理相关部分可能部分受到`Will Drewry`和`Chris Evans`大约同时完成的其他项目的启发。

状态相关的`fuzz`方法在理论上听起来很吸引人，但这最终使模糊器变得复杂、脆弱且使用起来很麻烦——每个其他目标程序都需要进行一两次调整。因为`Bunny`的表现并不比不那么复杂的蛮力工具好多少，所以我最终决定将其放弃。您仍然可以在以下位置找到其原始文档：[https://code.google.com/p/bunny-the-fuzzer/wiki/BunnyDoc](https://code.google.com/p/bunny-the-fuzzer/wiki/BunnyDoc)

此外，也有相当数量的独立工作。最值得注意的是，那年早些时候，`Jared DeMott`在`Defcon`上做了一个关于覆盖率驱动的模糊器的演讲，该模糊器依赖于覆盖率作为适应度函数。

`Jared`的方法与`afl-fuzz`所做的并不完全相同，但它在同一个范围内。他的模糊器试图用单个输入文件明确解决最大覆盖率；相比之下，`afl`只是选择做一些新事情的案例(这会产生更好的结果——请参阅`Technical_details.txt`)。

几年后，`Gabriel Campana`发布了`fuzzgrind`，这是一个完全依赖`Valgrind`的工具和一个约束求解器，可以在没有任何蛮力位的情况下最大化覆盖率；和微软研究人员广泛讨论了他们仍然非公开的、基于求解器的`SAGE`框架。

在过去六年左右的时间里，我还看到了相当多的学术论文涉及智能模糊测试(主要关注符号执行)和几篇讨论具有相同目标的遗传算法的概念验证应用的论文心里。我不相信大多数这些实验的实用性。我怀疑他们中的许多人都受到了`bunny-the-fuzzer`的诅咒，即在纸上和精心设计的实验中很酷，但未能通过最终测试，即能够在其他经过充分模糊的真实世界中找到新的、有价值的安全漏洞软件。

在某些方面，好的解决方案必须与之竞争的基线比看起来要令人印象深刻得多，这使得竞争对手很难脱颖而出。对于一个单一的例子，请查看`Gynvael`和`Mateusz Jurczyk`的工作，将“愚蠢”模糊测试应用于`ffmpeg`，现代浏览器和媒体播放器的一个突出且安全关键的组件：[http://googleonlinesecurity.blogspot.com/2014/01/ffmpeg-and-thousand-fixes.html](http://googleonlinesecurity.blogspot.com/2014/01/ffmpeg-and-thousand-fixes.html)

在同样复杂的软件中使用最先进的符号执行轻松获得可比较的结果似乎仍然不太可能，并且到目前为止还没有在实践中得到证明。

但我离题了；归根结底，归因是困难的，夸耀`AFL`背后的基本概念可能是在浪费时间。魔鬼往往存在于经常被忽视的细节中，让我们继续往下看……

### <a class="reference-link" name="2.2%20%E8%AE%BE%E8%AE%A1%E7%9B%AE%E6%A0%87"></a>2.2 设计目标

简而言之，我相信`afl-fuzz`的当前实现可以解决一些其他工具似乎无法解决的问题：
1. 速度。当您的自动化测试方法是资源密集型时，真的很难与蛮力竞争。如果您的检测使发现错误的可能性增加`10`倍，但运行速度却降低`100`倍，那么您的测试过程就会受到不利影响。为了避免您在使用时遇到困难，`afl-fuzz`旨在让您以大致相同的原始速度模糊大多数预期目标——因此即使它没有增加价值，您也不会损失太多。最重要的是，该工具利用以多种方式检测减少实际工作量。例如，仔细修剪语料库或跳过输入文件中的非功能性但不可修剪的内容。
1. 坚如磐石的可靠性。如果您的方法脆弱且意外失败，则很难与蛮力竞争。自动化测试很有吸引力，因为它易于使用且可扩展；任何违反这些原则的行为都是一种不受欢迎的权衡，这意味着您的工具将被较少使用并且结果不一致。大多数基于符号执行、污点跟踪或复杂的语法感知工具的方法目前对于实际的待测目标相当不可靠。也许更重要的是，它们的故障模式会使它们比“愚蠢”工具更糟糕，而且这种退化对于经验不足的用户来说很难注意到和纠正。相比之下，`afl-fuzz`被设计得坚如磐石，主要是通过保持简单的逻辑。事实上，从本质上讲，它被设计为一个非常好的传统模糊器，具有广泛的有趣且经过充分研究的策略。额外的部分只是帮助它把精力集中在最重要的地方。
1. 简单。测试框架的作者可能是唯一真正了解该工具提供的所有设置的影响的人——并且可以恰到好处地调整这些设置。然而，即使是最基本的模糊测试框架也经常带有无数的设置项和需要操作员提前猜测的模糊测试比率。这弊大于利。AFL 旨在尽可能避免这种情况。您可以使用的三个设置项是输出文件、内存限制以及覆盖默认自动校准超时的能力。其余的应该工作。如果没有，用户友好的错误消息会概述可能的原因和解决方法，并让您立即回到正轨。
1. 可结合性。大多数通用`fuzzer`不能轻易用于资源匮乏或交互繁重的工具，需要创建自定义的进程内`fuzzer`或大量`CPU`能力的消耗(其中大部分浪费在与任务没有直接关系的任务上)`AFL`试图通过允许用户使用更轻量级的目标(例如，独立的图像解析库)来创建有趣的测试用例的小型语料库，这些测试用例可以输入到手动测试过程或稍后的`UI`工具中，从而解决这个问题。
正如`technical_details.txt`中提到的，`AFL`不是通过系统地应用单一的总体`CS`概念来实现这一切的，而是通过试验各种小的、互补的方法，这些方法被证明能可靠地产生比偶然更好的结果。这些工具的使用是该工具包的一部分，但远不是最重要的。<br>
归根结底，重要的是`afl-fuzz`旨在发现很酷的错误——并且在这方面有着非常强大的记录。



## 3. INSTALL(安装说明)

本文档提供基本安装说明并讨论各种平台的已知问题。有关一般说明手册，请参阅自述文件。

### <a class="reference-link" name="3.1%20Linux%20on%20x86"></a>3.1 Linux on x86

`AFL`在该平台预计会运行良好。使用以下命令编译程序：

```
$ make
```

您可以在不安装的情况下开始使用 fuzzer，但也可以通过以下方式安装它：

```
# make install
```

此软件包没有特殊的依赖关系需要安装，您将需要`GNU make`和一个工作编译器(`gcc`或`clang`)。一些与程序捆绑在一起的可选脚本可能依赖于`bash`、`gdb`和类似的基本工具。

如果您正在使用`clang`，请查看`llvm_mode/README.llvm`；与传统方法相比，`LLVM`集成模式可以提供显着的性能提升。

您可能需要更改多个设置以获得最佳结果(最值得注意的选项是是否禁用崩溃报告实用程序并切换到不同的`CPU`调控器)，但`afl-fuzz`会在必要时指导您完成相关设置。

### <a class="reference-link" name="3.2%20OpenBSD,%20FreeBSD,%20NetBSD%20on%20x86"></a>3.2 OpenBSD, FreeBSD, NetBSD on x86

与`Linux`类似，`AFL`在这些平台预计运行良好并将在这些平台进行定期测试。您可以用`GNU make`编译：

```
$ gmake
```

请注意，`BSD make`将不工作。如果您的系统上没有`gmake`，请先安装它。与在`Linux`上一样，您可以在不安装的情况下使用`fuzzer`本身，或者通过以下方式安装：

```
# gmake install
```

请记住，如果您使用`csh`作为`shell`，自述文件和其他文档中给出的某些`shell`命令的语法会有所不同。

`llvm_mode`需要动态链接的、完全可操作的`clang`安装。至少在`FreeBSD`上，`clang`二进制文件是静态的并且不包含一些必要的工具，所以如果你想让它工作，你可能需要按照`llvm_mode/README.llvm`中的说明进行操作。

除此之外，一切都应该像文档所述的那样工作。

`QEMU`模式目前仅在`Linux`上受支持。但我认为这只是一个`QEMU`问题，因为我根本无法获得在`BSD`上正常工作的用户模式仿真支持的普通程序。

### <a class="reference-link" name="3.3%20MacOS%20X%20on%20x86"></a>3.3 MacOS X on x86

`MacOS X`上`AFL`应该可以正常工作，但由于平台的特性，验证这一点存在一些问题。最重要的是，我的测试能力有限，框架的运行情况主要依赖于用户反馈。

要构建`AFL`，请安装`Xcode`并按照适用于`Linux`的一般说明进行操作。

`Xcode 'gcc'`工具只是`clang`的一个包装器，所以一定要使用`afl-clang`来编译任何检测过的二进制文件`afl-gcc`将失败，除非您从其他来源安装了`GCC`(在这种情况下，请指定`AFL_CC`和`AFL_CXX`以指向“真正的”`GCC`二进制文件)。

该平台只能进行`64`位编译；由于`OS X`处理重定位的方式，移植`32`位工具需要相当多的工作，而今天，几乎所有的`MacOS X`机器都是 `64`位的。

`MacOS X`默认附带的崩溃报告守护程序会导致模糊测试问题。您需要按照此处提供的说明将其关闭：[http://goo.gl/CCcd5u](http://goo.gl/CCcd5u)

与其他`unix`系统相比，`OS X`上的`fork()`语义有点不寻常，而且绝对不符合`POSIX`标准。这意味着两件事：
<li>
`Fuzzing`可能比在`Linux`上慢。事实上，有些人报告说，通过在`MacOS X`上的`Linux VM`中运行作业，可显着提高性能。</li>
- 一些不可移植的、特定于平台的代码可能与`AFL forkserver`不兼容。如果遇到任何问题，请在启动`afl-fuzz`之前在环境中设置 `AFL_NO_FORKSRV=1`。
`MacOS X`似乎不支持`QEMU`的用户仿真模式，因此黑盒检测模式(`-Q`)将不起作用。

`llvm_mode`需要完整运行的`clang`安装。`Xcode`附带的那个缺少一些基本的头文件和辅助工具。有关如何从头构建编译器的建议，请参见`llvm_mode/README.llvm`。

### <a class="reference-link" name="3.4%20Linux%20or%20*BSD%20on%20non-x86%20systems"></a>3.4 Linux or *BSD on non-x86 systems

`AFL`的标准构建将在非`x86`系统上失败，但您应该能够利用其中的两个模式：
<li>
`LLVM`模式(参见`llvm_mode/README.llvm`)，它不依赖于`x86`特定的程序集做基础。它快速而强大，但需要完整安装`clang`。</li>
<li>
`QEMU`模式(参见`qemu_mode/README.qemu`)，也可用于对跨平台二进制文件进行模糊测试。它更慢且更不稳定，但即使您没有测试应用程序的源代码，也可以使用它。</li>
如果您不确定自己需要什么，则需要`LLVM`模式。要获得它，请尝试：

```
$ AFL_NO_X86=1 gmake &amp;&amp; gmake -C llvm_mode
```

…并使用`afl-clang-fast`或`afl-clang-fast++`编译您的目标程序，而不是传统的`afl-gcc`或`afl-clang`包装器。

### <a class="reference-link" name="3.5%20Solaris%20on%20x86"></a>3.5 Solaris on x86

据用户报告，`fuzzer`可以在`Solaris`上运行，但我没有亲自测试过，而且用户群相当小，所以我没有很多反馈报告以供参考。

为了让构建顺利进行，您需要使用`GNU make`和`GCC`或`clang`。有人告诉我，平台附带的`GCC`的特定版本无法正常工作，因为它依赖于`as`的硬编码位置(其将完全忽略`-B`参数或`$PATH`)。

要解决此问题，您可能需要从源代码构建标准`GCC`，如下所示：

```
$ ./configure --prefix=$HOME/gcc --with-gnu-as --with-gnu-ld \
  --with-gmp-include=/usr/include/gmp --with-mpfr-include=/usr/include/mpfr
$ make
$ sudo make install
```

注意不要指定`--with-as=/usr/gnu/bin/as`——这将产生一个忽略`-B`标志的`GCC`二进制文件，你将回到默认情况。

请注意，据报道`Solaris`启用了崩溃报告，这会导致崩溃被误解为挂起的问题，类似于`Linux`和`MacOS X`的陷阱。`AFL`不会在此特定平台上自动检测崩溃报告，但您可能需要运行以下命令：

```
$ coreadm -d global -d global-setid -d process -d proc-setid -d kzone -d log
```

`QEMU`的用户模拟模式在`Solaris`上不可用，因此黑盒检测模式(`-Q`)将不起作用。

### <a class="reference-link" name="3.6%20%E5%85%B6%E4%BB%96%E7%9A%84%E7%B3%BB%E7%BB%9F%E7%89%88%E6%9C%AC"></a>3.6 其他的系统版本

在这些系统版本上构建就要靠你自己了。在符合`POSIX`的系统上，您可以编译和运行`AFL`；`LLVM`模式可能提供一种检测非`x86`代码的方法。

`AFL`不会在`Windows`上运行。它也不会在`Cygwin`下工作。它可以很容易地移植到后一个平台，但这是一个非常糟糕的主意，因为 `Cygwin`非常慢。使用`VirtualBox`左右运行硬件加速的`Linux VM`更有意义；它的运行速度会快`20`倍左右。如果您有一个真正引人注目的`Cygwin`用例，请告诉我。

尽管`x86`上的`Android`理论上应该可以工作，但库存内核可能已编译出`SHM`支持，如果是这样，您可能必须首先解决该问题。您可能只需要以下解决方法：[https://github.com/pelya/android-shmem](https://github.com/pelya/android-shmem)

`Joshua J. Drake`指出，`Android`链接器添加了一个`shim`，可以自动拦截`SIGSEGV`和相关信号。为了解决这个问题并能够看到崩溃，你需要把它放在模糊程序的开头：

```
signal(SIGILL, SIG_DFL);
signal(SIGABRT, SIG_DFL);
signal(SIGBUS, SIG_DFL);
signal(SIGFPE, SIG_DFL);
signal(SIGSEGV, SIG_DFL);
```

您可能需要先`#include &lt;signal.h&gt;`。

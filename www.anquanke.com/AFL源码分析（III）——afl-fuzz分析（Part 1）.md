> 原文链接: https://www.anquanke.com//post/id/245499 


# AFL源码分析（III）——afl-fuzz分析（Part 1）


                                阅读量   
                                **57726**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t019bded1e48f69c18e.jpg)](https://p2.ssl.qhimg.com/t019bded1e48f69c18e.jpg)



## 0x00 写在前面

在前两篇文章中，我分析了afl-gcc的相关处理逻辑。简单来说，`afl-gcc`会将必要的函数以及桩代码插入到我们的源汇编文件中，这样，经过编译的程序将会带有一些外来的函数。但是。这些函数到底是怎样生效的呢，在本篇文章中，我将对AFL的主逻辑，也就是`afl-fuzz`进行分析。



## 0x01 afl-fuzz

依据官方`github`所述，`afl-fuzz`是`AFL`在执行`fuzz`时的主逻辑。

对于直接从标准输入(`STDIN`)直接读取输入的待测文件，可以使用如下命令进行测试：

```
./afl-fuzz -i testcase_dir -o findings_dir /path/to/program [...params...]
```

而对于从文件中读取输入的程序来说，可以使用如下命令进行测试：

```
./afl-fuzz -i testcase_dir -o findings_dir /path/to/program @@
```



## 0x02 afl-fuzz源码分析(第一部分)

### `main`函数(第一部分)

#### `banner` &amp; 随机数生成

首先是函数入口，程序首先打印必要的提示信息，随后依据当前系统时间生成随机数。

```
SAYF(cCYA "afl-fuzz " cBRI VERSION cRST " by &lt;lcamtuf@google.com&gt;\n");

doc_path = access(DOC_PATH, F_OK) ? "docs" : DOC_PATH;

gettimeofday(&amp;tv, &amp;tz);
srandom(tv.tv_sec ^ tv.tv_usec ^ getpid());
```

#### `switch`选项处理

##### `getopt`选项获取

使用`getopt`函数遍历参数并存入`opt`变量中

```
while ((opt = getopt(argc, argv, "+i:o:f:m:b:t:T:dnCB:S:M:x:QV")) &gt; 0)
```

> 关于`getopt`函数：
<ul>
<li>函数原型：`int getopt(int argc, char * const argv[],const char *optstring);`
</li>
<li>参数解释：
<ul>
<li>
`argc`：整型，一般将`main`函数的`argc`参数直接传入，此参数记录`argv`数组的大小。</li>
<li>
`argv`：指针数组。一般将`main`函数的`argv`参数直接传入，此参数存储所有的参数。例如，`linux`下使用终端执行某二进制程序时使用`./a.out -a1234 -b432 -c -d`的命令，则`argc = 5; argv[5] = `{`"./a.out","-a1234","-b432","-c","-d"`}`;`
</li>
<li>
`optstring`：字符串。此字符串用于指定合法的选项列表，格式如下：
<ul>
<li>
`&lt;字符&gt;`一个字符后面无任何修饰符号表示此选项后无参数。</li>
<li>
`&lt;字符&gt;:`一个字符后面跟一个冒号表示此选项后必须一个参数。此参数可以与选项分开，也可以与选项连写。</li>
<li>
`&lt;字符&gt;::`一个字符后面跟两个个冒号表示此选项后可选一个参数。此参数必须与选项连写。</li>
<li>
`&lt;字符&gt;;`一个字符后跟一个分号表示此选项将被解析为长选项。例如`optstring`中存在`W;`则参数`-W foo`将被解析为`--foo`。(仅限`Glibc &gt;= 2.X`)</li>
</ul>
`getopt`在进行参数处理时，会首先依照`optstring`进行参数的排序，以保证所有的无选项参数位于末尾。例如，当`optstring = "a:b::c::d:efg"`时，若调用命令是`./a.out -a 1 -b 2 -c3 -d4 -f -g -e 5 6`，则排序后的结果为`argv[12] = `{`"./a.out","-a","1","-b","-c3","-d4","-e","-f","-g","2","5","6"`}``
特别的，若`optstring`的第一个字符是`+`或设置了`POSIXLY_CORRECT`这个环境变量，则当解析到无选项参数时，函数即刻中止返回`-1`。若`optstring`的第一个字符是`-`，则表示解析所有的无选项参数。当处理到`--`符号时，无论给定了怎样的`optstring`，函数即刻中止并返回`-1`。
</li>
<li>返回值解释：此函数的返回值情况如下表所示| 返回值 | 含义 |<br>
| :———: | :—————————————————————————————: |<br>
| 选项字符 | `getopt`找到了`optstring`中定义的选项 |<br>
| -1 | 1.所有的命令内容均已扫描完毕。2.函数遇到了`--`。3.`optstring`的第一个字符是`+`或设置了`POSIXLY_CORRECT`这个环境变量，解析到了无选项参数。 |<br>
| ? | 1.遇到了未在`optstring`中定义的选项。2.必须参数的选项缺少参数。(特殊的，若`optstring`的第一个字符是`:`返回`:`以替代`?`) |</li>
</ul>
</li>
</ul>

接下来，`main`函数将依据不同的参数进行不同的代码块进行`switch`语句处理。

##### `-i`选项(目标输入目录)

此选项表示待测目标输入文件所在的目录，接受一个目录参数。

```
case 'i': /* input dir */
`{`
    if (in_dir) FATAL("Multiple -i options not supported");
    in_dir = optarg;
    if (!strcmp(in_dir, "-")) in_place_resume = 1;
    break;
`}`
```
1. 首先检查`indir`是否已被设置，防止多次设置`-i`选项。
1. 将选项参数写入`in_dir`。
1. 若`in_dir`的值为`-`，将`in_place_resume`标志位置位。
##### `-o`选项(结果输出目录)

此选项表示待测目标输出文件存放的目录，接受一个目录参数。

```
case 'o': /* output dir */
`{`
    if (out_dir) FATAL("Multiple -o options not supported");
    out_dir = optarg;
    break;
`}`
```
1. 首先检查`out_dir`是否已被设置，防止多次设置`-o`选项。
1. 将选项参数写入`out_dir`。
##### `-M`选项(并行扫描，Master标志)

此选项表示此次fuzz将启动并行扫描模式，关于并行扫描模式官方已经给出了文档，本文中将以附录形式进行全文翻译。

```
case 'M':  /* master sync ID */
`{`
    u8* c;

    if (sync_id) FATAL("Multiple -S or -M options not supported");
    sync_id = ck_strdup(optarg);

    if ((c = strchr(sync_id, ':'))) `{`
        *c = 0;

        if (sscanf(c + 1, "%u/%u", &amp;master_id, &amp;master_max) != 2 ||
            !master_id || !master_max || master_id &gt; master_max ||
            master_max &gt; 1000000) FATAL("Bogus master ID passed to -M");
    `}`

    force_deterministic = 1;
    break;
`}`
```
1. 首先检查`sync_id`是否已被设置，防止多次设置`-M/-S`选项。
1. 使用`ck_strdup`函数将传入的实例名称存入特定结构的`chunk`中，并将此`chunk`的地址写入`sync_id`。
<li>检查`Master`实例名中是否存在`:`，若存在，则表示这里是使用了并行确定性检查的实验性功能，那么使用`sscanf`获取当前的`Master`实例序号与`Master`实例最大序号，做如下检查：
<ol>
1. 当前的`Master`实例序号与`Master`实例最大序号均不应为空
1. 当前的`Master`实例序号应小于`Master`实例最大序号
<li>
`Master`实例最大序号应不超过`1000000`
</li>
任意一项不通过则抛出致命错误`"Bogus master ID passed to -M"`，随后程序退出

##### `-S`选项(并行扫描，Slave标志)

此选项表示此次fuzz将启动并行扫描模式，关于并行扫描模式官方已经给出了文档，本文中将以附录形式进行全文翻译。

```
case 'S': 
`{`
    if (sync_id) FATAL("Multiple -S or -M options not supported");
    sync_id = ck_strdup(optarg);
    break;
`}`
```
1. 首先检查`sync_id`是否已被设置，防止多次设置`-M/-S`选项。
1. 使用`ck_strdup`函数将传入的实例名称存入特定结构的`chunk`中，并将此`chunk`的地址写入`sync_id`。
##### `-f`选项(fuzz目标文件)

此选项用于指明需要`fuzz`的文件目标。

```
case 'f': /* target file */
`{`
    if (out_file) FATAL("Multiple -f options not supported");
    out_file = optarg;
    break;
`}`
```
1. 首先检查`out_file`是否已被设置，防止多次设置`-f`选项。
1. 将选项参数写入`out_file`。
##### `-x`选项(关键字字典目录)

此选项用于指明关键字字典的目录。

> 默认情况下，`afl-fuzz`变异引擎针对压缩数据格式(例如，图像、多媒体、压缩数据、正则表达式语法或 shell 脚本)进行了优化。因此，它不太适合那些特别冗长和复杂的语言——特别是包括 HTML、SQL 或 JavaScript。
由于专门针对这些语言构建语法感知工具过于麻烦，`afl-fuzz`提供了一种方法，可以使用可选的语言关键字字典、魔数头或与目标数据类型相关的其他特殊标记来为模糊测试过程提供种子——并使用它来重建移动中的底层语法，这一点，您可以参考[http://lcamtuf.blogspot.com/2015/01/afl-fuzz-making-up-grammar-with.html](http://lcamtuf.blogspot.com/2015/01/afl-fuzz-making-%20up-grammar-with.html)。

```
case 'x': /* dictionary */
`{`
    if (extras_dir) FATAL("Multiple -x options not supported");
    extras_dir = optarg;
    break;
`}`
```
1. 首先检查`extras_dir`是否已被设置，防止多次设置`-x`选项。
1. 将选项参数写入`extras_dir`。
##### `-t`选项(超时阈值)

此选项用于指明单个`fuzz`实例运行时的超时阈值。

```
case 't': /* timeout */
`{`
    u8 suffix = 0;
    if (timeout_given) FATAL("Multiple -t options not supported");
    if (sscanf(optarg, "%u%c", &amp;exec_tmout, &amp;suffix) &lt; 1 || optarg[0] == '-')
        FATAL("Bad syntax used for -t");
    if (exec_tmout &lt; 5) FATAL("Dangerously low value of -t");
    if (suffix == '+') timeout_given = 2; else timeout_given = 1;
    break;
`}`
```
1. 首先检查`timeout_given`是否已被设置，防止多次设置`-t`选项。
1. 使用`"%u%c"`获取参数并以此写入超时阈值`exec_tmout`和后缀`suffix`，若获取失败，抛出致命错误，程序中断。
1. 若`exec_tmout`小于`5`，抛出致命错误，程序中断。
1. 若后缀为`+`，将`timeout_given`变量置为`2`，否则，将`timeout_given`变量置为`1`。
##### `-m`选项(内存限制)

此选项用于指明单个`fuzz`实例运行时的内存阈值。

```
case 'm': `{` /* mem limit */

    u8 suffix = 'M';

    if (mem_limit_given) FATAL("Multiple -m options not supported");
    mem_limit_given = 1;

    if (!strcmp(optarg, "none")) `{`

        mem_limit = 0;
        break;

    `}`

    if (sscanf(optarg, "%llu%c", &amp;mem_limit, &amp;suffix) &lt; 1 ||
        optarg[0] == '-') FATAL("Bad syntax used for -m");

    switch (suffix) `{`

        case 'T': mem_limit *= 1024 * 1024; break;
        case 'G': mem_limit *= 1024; break;
        case 'k': mem_limit /= 1024; break;
        case 'M': break;

        default:  FATAL("Unsupported suffix or bad syntax for -m");

    `}`

    if (mem_limit &lt; 5) FATAL("Dangerously low value of -m");

    if (sizeof(rlim_t) == 4 &amp;&amp; mem_limit &gt; 2000)
        FATAL("Value of -m out of range on 32-bit systems");

    break;
`}`
```
1. 首先检查`mem_limit_given`是否已被设置，防止多次设置`-m`选项，随后，将`mem_limit_given`置位。
1. 若选项参数为`none`，则将内存阈值`mem_limit`设为`0`。
1. 使用`"%llu%c"`获取参数并以此写入内存阈值`mem_limit`和后缀`suffix`，若获取失败，抛出致命错误，程序中断。
1. 根据后缀的单位将`mem_limit`的值换算为`M(兆)`。
1. 若`mem_limit`小于`5`，抛出致命错误，程序中断。
<li>检查`rlim_t`的大小，若其值为`4`，表示此处为`32`位环境。此时当`mem_limit`的值大于`2000`时，抛出致命错误，程序中断。
<ul>
<li>此变量的定义为`typedef __uint64_t rlim_t;`
</li>
</ul>
</li>
##### `-b`选项(CPU ID)

此选项用于将`fuzz`测试实例绑定到指定的`CPU`内核上。

```
case 'b':  /* bind CPU core */
`{`
    if (cpu_to_bind_given) FATAL("Multiple -b options not supported");
    cpu_to_bind_given = 1;

    if (sscanf(optarg, "%u", &amp;cpu_to_bind) &lt; 1 || optarg[0] == '-')
        FATAL("Bad syntax used for -b");

    break;
`}`
```
1. 首先检查`cpu_to_bind_given`是否已被设置，防止多次设置`-b`选项，随后，将`cpu_to_bind_given`置位。
1. 使用`"%u"`获取参数并以此写入想要绑定的`CPU ID`变量`cpu_to_bind`，若获取失败，抛出致命错误，程序中断。
##### `-d`选项(快速`fuzz`开关)

此选项用于启用`fuzz`测试实例的快速模式。(**快速模式下将跳转确定性检查步骤，这将导致误报率显著上升**)

```
case 'd': /* skip deterministic */
`{`
    if (skip_deterministic) FATAL("Multiple -d options not supported");
    skip_deterministic = 1;
    use_splicing = 1;
    break;
`}`
```
1. 首先检查`skip_deterministic`是否已被设置，防止多次设置`-d`选项，随后，将`skip_deterministic`置位。
1. 将`use_splicing`置位。
##### `-B`选项(加载指定测试用例)

此选项是一个隐藏的非官方选项，如果在测试过程中发现了一个有趣的测试用例，想要直接基于此用例进行样本变异且不想重新进行早期的样本变异，可以使用此选项直接指定一个`bitmap`文件

```
case 'B': /* load bitmap */
`{`
    /* This is a secret undocumented option! It is useful if you find
           an interesting test case during a normal fuzzing process, and want
           to mutate it without rediscovering any of the test cases already
           found during an earlier run.

           To use this mode, you need to point -B to the fuzz_bitmap produced
           by an earlier run for the exact same binary... and that's it.

           I only used this once or twice to get variants of a particular
           file, so I'm not making this an official setting. */

    if (in_bitmap) FATAL("Multiple -B options not supported");

    in_bitmap = optarg;
    read_bitmap(in_bitmap);
    break;
`}`
```
1. 首先检查`in_bitmap`是否已被设置，防止多次设置`-d`选项。
1. 将选项参数赋值给`in_bitmap`。
1. 调用`read_bitmap`。
##### `-C`选项(崩溃探索模式开关)

基于覆盖率的`fuzz`中通常会生成一个崩溃分组的小数据集，可以手动或使用非常简单的`GDB`或`Valgrind`脚本进行快速分类。这使得每个崩溃都可以追溯到队列中的非崩溃测试父用例，从而更容易诊断故障。但是如果没有大量调试和代码分析工作，一些模糊测试崩溃可能很难快速评估其可利用性。为了协助完成此任务，`afl-fuzz`支持使用`-C`标志启用的非常独特的“崩溃探索”模式。在这种模式下，模糊器将一个或多个崩溃测试用例作为输入，并使用其反馈驱动的模糊测试策略非常快速地枚举程序中可以到达的所有代码路径，同时保持程序处于崩溃状态。此时，`fuzz`器运行过程中生成的不会导致崩溃的样本变异被拒绝，任何不影响执行路径的变异也会被拒绝。

```
enum `{`
  /* 00 */ FAULT_NONE,
  /* 01 */ FAULT_TMOUT,
  /* 02 */ FAULT_CRASH,
  /* 03 */ FAULT_ERROR,
  /* 04 */ FAULT_NOINST,
  /* 05 */ FAULT_NOBITS
`}`;
case 'C': /* crash mode */
`{`
    if (crash_mode) FATAL("Multiple -C options not supported");
    crash_mode = FAULT_CRASH;
    break;
`}`
```
1. 首先检查`crash_mode`是否已被设置，防止多次设置`-C`选项。
1. 将`02`赋值给`crash_mode`。
##### `-n`选项(盲测试模式开关)

`fuzzing`通常由盲`fuzzing`(`blind fuzzing`)和导向性`fuzzing`(`guided fuzzing`)两种。`blind fuzzing`生成测试数据的时候不考虑数据的质量，通过大量测试数据来概率性地触发漏洞。`guided fuzzing`则关注测试数据的质量，期望生成更有效的测试数据来触发漏洞的概率。比如，通过测试覆盖率来衡量测试输入的质量，希望生成有更高测试覆盖率的数据，从而提升触发漏洞的概率。

```
case 'n': /* dumb mode */
`{`
    if (dumb_mode) FATAL("Multiple -n options not supported");
    if (getenv("AFL_DUMB_FORKSRV")) dumb_mode = 2; else dumb_mode = 1;

    break;
`}`
```
1. 首先检查`dumb_mode`是否已被设置，防止多次设置`-n`选项。
1. 检查`"AFL_DUMB_FORKSRV"`这个环境变量是否已被设置，若已设置，将`dumb_mode`设置为`2`，否则，将`dumb_mode`设置为`1`。
##### `-T`选项(指定`banner`内容)

指定运行时在实时结果界面所显示的`banner`。

```
case 'T': /* banner */
`{`
    if (use_banner) FATAL("Multiple -T options not supported");
    use_banner = optarg;
    break;
`}`
```
1. 首先检查`use_banner`是否已被设置，防止多次设置`-T`选项。
1. 将选项参数写入`use_banner`。
##### `-Q`选项(`QEMU`模式开关)

启动`QEMU`模式进行`fuzz`测试。

```
/* Default memory limit when running in QEMU mode (MB): */

#define MEM_LIMIT_QEMU      200

case 'Q': /* QEMU mode */
`{`
    if (qemu_mode) FATAL("Multiple -Q options not supported");
    qemu_mode = 1;

    if (!mem_limit_given) mem_limit = MEM_LIMIT_QEMU;

    break;
`}`
```
1. 首先检查`qemu_mode`是否已被设置，防止多次设置`-Q`选项，随后将`qemu_mode`变量置位。
1. 若`mem_limit_given`标志位(此标志位通过`-m`选项设置)未被设置，将`mem_limit`变量设置为`200(MB)`。
##### `-V`选项(版本选项)

展示`afl-fuzz`的版本信息。

```
case 'V': /* Show version number */
`{`
    /* Version number has been printed already, just quit. */
    exit(0);
`}`
```

展示版本后直接退出程序。

##### 用法展示(`default`语句)

```
default:
    usage(argv[0]);
```

调用`usage`函数打印`afl-fuzz`的用法。

#### <a class="reference-link" name="%E5%BF%85%E9%9C%80%E5%8F%82%E6%95%B0%E6%A3%80%E6%9F%A5"></a>必需参数检查

```
if (optind == argc || !in_dir || !out_dir)
    usage(argv[0]);
```

如果目标输入目录`in_dir`为空、结果输出目录`out_dir`为空、当前处理的参数下标与`argc`相同，三项条件之一命中，调用`usage`函数打印`afl-fuzz`的用法。

> 关于`optind`变量，此变量指示当前处理的参数下标。例如，调用命令为`./a.out -a -b 2 -c`，此时`argc`的值为`5`，当使用`getopt()`获取到`-c`之后，其下标为`5`。而因为`afl-fuzz`的调用规范是`./afl-fuzz [ options ] -- /path/to/fuzzed_app [ ... ]`，当当前处理的参数下标与`argc`相同，意味着`/path/to/fuzzed_app`未给定，而这是必需的。

#### <a class="reference-link" name="%E5%90%8E%E7%BB%AD%E9%80%BB%E8%BE%91"></a>后续逻辑

**后续逻辑将进行大量的函数调用，由于篇幅限制，将在下一篇文章中给予说明。**

### `ck_strdup`函数/`DFL_ck_strdup`函数

此函数实际上是一个宏定义：

```
// alloc-inl.h line 349
#define ck_strdup DFL_ck_strdup
```

因此其实际定义为

```
/* Create a buffer with a copy of a string. Returns NULL for NULL inputs. */

#define MAX_ALLOC 0x40000000
#define ALLOC_CHECK_SIZE(_s) do `{` \
    if ((_s) &gt; MAX_ALLOC) \
        ABORT("Bad alloc request: %u bytes", (_s)); \
`}` while (0)
#define ALLOC_CHECK_RESULT(_r, _s) do `{` \
    if (!(_r)) \
        ABORT("Out of memory: can't allocate %u bytes", (_s)); \
`}` while (0)
#define ALLOC_OFF_HEAD  8
#define ALLOC_OFF_TOTAL (ALLOC_OFF_HEAD + 1)
#define ALLOC_C1(_ptr)  (((u32*)(_ptr))[-2])
#define ALLOC_S(_ptr)   (((u32*)(_ptr))[-1])
#define ALLOC_C2(_ptr)  (((u8*)(_ptr))[ALLOC_S(_ptr)])
#define ALLOC_MAGIC_C1  0xFF00FF00 /* Used head (dword)  */
#define ALLOC_MAGIC_C2  0xF0       /* Used tail (byte)   */

static inline u8* DFL_ck_strdup(u8* str) `{`

  void* ret;
  u32   size;

  if (!str) return NULL;

  size = strlen((char*)str) + 1;

  ALLOC_CHECK_SIZE(size);
  ret = malloc(size + ALLOC_OFF_TOTAL);
  ALLOC_CHECK_RESULT(ret, size);

  ret += ALLOC_OFF_HEAD;

  ALLOC_C1(ret) = ALLOC_MAGIC_C1;
  ALLOC_S(ret)  = size;
  ALLOC_C2(ret) = ALLOC_MAGIC_C2;

  return memcpy(ret, str, size);

`}`
```

将宏定义合并后，可以得到以下代码

```
/* Create a buffer with a copy of a string. Returns NULL for NULL inputs. */

static inline u8* DFL_ck_strdup(u8* str) `{`
    void* ret;
    u32   size;

    if (!str) return NULL;

    size = strlen((char*)str) + 1;

    if (size &gt; 0x40000000)
        ABORT("Bad alloc request: %u bytes", size);
    ret = malloc(size + 9);
    if (!ret)
        ABORT("Out of memory: can't allocate %u bytes", size);

    ret += 8;

    ((u32*)(ret))[-2] = 0xFF00FF00;
    ((u32*)(ret))[-1]  = size;
    ((u8*)(ret))[((u32*)(ret))[-1]] = 0xF0;

    return memcpy(ret, str, size);
`}`
```
<li>此处事实上定义了一种数据格式：[![](https://p1.ssl.qhimg.com/t01d9a2adf7fd3f4fab.png)](https://p1.ssl.qhimg.com/t01d9a2adf7fd3f4fab.png)
</li>
1. 获取传入的字符串，检查其是否为空，若为空，返回`NULL`。
1. 获取字符串长度并将其`+1`作为总的字符串长度，存入`size`中，随后检查其是否小于等于`0x40000000`，若不满足，终止程序并抛出异常。
1. 分配`size + 9`大小的`chunk`(多出的大小是结构首部和尾部的空间)，若分配失败，终止程序并抛出异常。
1. 将`chunk`指针移至`Body`的位置，并通过负偏移寻址的方式在`Header`部分写入`Magic Number`字段(大小为`0xFF00FF00`)以及大小字段。
1. 将`size`作为偏移寻址写入最后的`0xF0`尾部标志位、
1. 使用`memcpy`将字符串复制至`chunk`的`String`位置，返回。
### `read_bitmap`函数

```
/* Read bitmap from file. This is for the -B option again. */
#define EXP_ST static
#define ck_read(fd, buf, len, fn) do `{` \
    u32 _len = (len); \
    s32 _res = read(fd, buf, _len); \
    if (_res != _len) RPFATAL(_res, "Short read from %s", fn); \
  `}` while (0)
#define MAP_SIZE (1 &lt;&lt; MAP_SIZE_POW2)
#define MAP_SIZE_POW2 16

EXP_ST void read_bitmap(u8* fname) `{`

  s32 fd = open(fname, O_RDONLY);

  if (fd &lt; 0) PFATAL("Unable to open '%s'", fname);

  ck_read(fd, virgin_bits, MAP_SIZE, fname);

  close(fd);

`}`
```

将宏定义合并后，可以得到以下代码

```
/* Read bitmap from file. This is for the -B option again. */
static void read_bitmap(u8* fname) `{`
    s32 fd = open(fname, O_RDONLY);
    if (fd &lt; 0) 
        PFATAL("Unable to open '%s'", fname);

    u32 _len = 1 &lt;&lt; 16;
    s32 _res = read(fd, virgin_bits, _len);
    if (_res != _len) 
        RPFATAL(_res, "Short read from %s", fname);
    close(fd);
`}`
```
1. 以只读模式打开`bitmap`文件，若打开失败，抛出致命错误，程序中止。
1. 从`bitmap`文件中读取`1&lt;&lt;16`个字节写入到`virgin_bits`变量中，如果成功读取的字符数小于`1&lt;&lt;16`个字节，抛出致命错误，程序中止。
1. 关闭已打开的文件。
### `usage`函数

```
/* Display usage hints. */

static void usage(u8* argv0) `{`

  SAYF("\n%s [ options ] -- /path/to/fuzzed_app [ ... ]\n\n"

       "Required parameters:\n\n"

       "  -i dir        - input directory with test cases\n"
       "  -o dir        - output directory for fuzzer findings\n\n"

       "Execution control settings:\n\n"

       "  -f file       - location read by the fuzzed program (stdin)\n"
       "  -t msec       - timeout for each run (auto-scaled, 50-%u ms)\n"
       "  -m megs       - memory limit for child process (%u MB)\n"
       "  -Q            - use binary-only instrumentation (QEMU mode)\n\n"     

       "Fuzzing behavior settings:\n\n"

       "  -d            - quick &amp; dirty mode (skips deterministic steps)\n"
       "  -n            - fuzz without instrumentation (dumb mode)\n"
       "  -x dir        - optional fuzzer dictionary (see README)\n\n"

       "Other stuff:\n\n"

       "  -T text       - text banner to show on the screen\n"
       "  -M / -S id    - distributed mode (see parallel_fuzzing.txt)\n"
       "  -C            - crash exploration mode (the peruvian rabbit thing)\n"
       "  -V            - show version number and exit\n\n"
       "  -b cpu_id     - bind the fuzzing process to the specified CPU core\n\n"

       "For additional tips, please consult %s/README.\n\n",

       argv0, EXEC_TIMEOUT, MEM_LIMIT, doc_path);

  exit(1);
`}`
```

打印`afl-fuzz`的用法，随后程序退出。



## 0x04 后记

虽然网上有很多关于`AFL`源码的分析，但是绝大多数文章都是抽取了部分代码进行分析的，本文则逐行对源码进行了分析，下一篇文章将针对`afl-fuzz`源码做后续分析。



## 0x05 参考资料

[【原】AFL源码分析笔记(一) – zoniony](https://xz.aliyun.com/t/4628#toc-10)

50加成券

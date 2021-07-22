> 原文链接: https://www.anquanke.com//post/id/147675 


# YARA规则的二进制格式探索与漏洞挖掘利用


                                阅读量   
                                **174755**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者bnbdr，文章来源：bnbdr.github.io
                                <br>原文地址：[https://bnbdr.github.io/posts/swisscheese/](https://bnbdr.github.io/posts/swisscheese/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t01719477b426799d61.jpg)](https://p5.ssl.qhimg.com/t01719477b426799d61.jpg)

## 前言

在这篇长得令人难以置信的简短文章中，我将讨论YARA规则的二进制格式，以及如何利用我发现的两个漏洞。[![](https://p4.ssl.qhimg.com/t01c223bf93be670bba.gif)](https://p4.ssl.qhimg.com/t01c223bf93be670bba.gif)我把它称作SwissCheese（瑞士奶酪）。

如果你想直接看解释部分，直接看WAT部分，或者看看这个[repo](https://github.com/bnbdr/swisscheese)。



## 预编译YARA规则

大多数使用它的人都知道YARA接受规则（rule）和目标（target），而且如果你关心“性能”，也可以预编译你的规则。我对预编译的部分挺感兴趣。如何用二进制形式表示我的规则？我采取了最简单的规则：

```
rule empty `{`
    condition: true
`}`
```

编译成~21KB，这到底是什么？后续我将介绍大小的问题，所以让我们先看看代码。



## 大海捞针

顺便说一句，我必须赞扬YARA开发人员使设置变得轻松-拥有一个编译的VisualStudio解决方案是令人耳目一新，很受欢迎。

但是，尝试理解文件格式并不那么简单。我不想了解YARA所做的一切，也不想理解所有关于文件格式的内容-要点就足够了。

一个合理的想法是寻找文件的加载或打包，以了解格式。这就是“魔法”字符串发挥作用的地方。它们的作用通常就像书签一样-在代码中搜索字符串，无论是否是反向的(取决于endianness等)，通常都会产生结果：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ca90a05b57267d4e.png)
- 用yara32打开：main -&gt; yr_rules_load -&gt; yr_rules_load_stream
- 用yara32打包：main -&gt; yr_rules_save -&gt; yr_rules_save_stream
```
if (header.magic[0] != 'Y' ||
    header.magic[1] != 'A' ||
    header.magic[2] != 'R' ||
    header.magic[3] != 'A')
`{`
    return ERROR_INVALID_FILE;
`}`
```

我将关注yr_arena_load_stream，因为从逻辑上讲，它与我试图模仿的东西是一样的。



## 开局不利

不出所料，该格式从一个头文件开始，其中包含了剩余文件的方法、版本和大小。在进行了一些基本验证之后，YARA读取文件的主体并执行重新定位。是的，显然，预编译主要意味着在将绝对地址转换为文件偏移之后将内存缓存转储到磁盘。

这意味着文件的尾部是一个重新定位表。然后，YARA会检查每个偏移量是否真的需要修补：
- 如果该偏移量中的QWORD值与0xFFFABADA不同，则应该对其进行修补。
- 否则，应该将其设置为NULL。
我不知道为什么它会使用这种方法，而不是从一开始就把它从表中删除。

要告诉YARA它已经到达表的末尾，它使用了一个特殊的标记：0xFFFFFFFF。下面是另一个DWORD，它是文件的计算哈希值。



## 散列

这个散列不太有趣。YARA首先对文件头进行散列，然后将其用作对主体进行散列的种子。请注意，哈希是在修补之前执行的，因为“编译器”显然不能预测用于该文件的分配地址。



## 准备好了

现在缓冲区已经修补好了，我们真的可以进入其中了。让我们跳到yr_rules_load_stream，看看我们新迁移的文件体发生了什么。

由于进行了一些初始化和强制转换，我们可以识别出该格式的一个额外块：它以一个规则头开始，并被定义为8；我想这是为了使相同的预编译规则在32位和64位构建(大小(PVOID)等)上都能工作，但我不知道为什么它如此重要。

宏 DECLARE_REFERENCE基本上使所有内容都成为QWORD。下面看到的所有不是指针的成员实际上都被typedef为一个类型：

```
typedef struct _YARA_RULES_FILE_HEADER
`{`
  DECLARE_REFERENCE(YR_RULE*, rules_list_head);
  DECLARE_REFERENCE(YR_EXTERNAL_VARIABLE*, externals_list_head);
  DECLARE_REFERENCE(const uint8_t*, code_start);
  DECLARE_REFERENCE(YR_AC_MATCH_TABLE, match_table);
  DECLARE_REFERENCE(YR_AC_TRANSITION_TABLE, transition_table);

`}` YARA_RULES_FILE_HEADER;
```

了解到上面显示的每个指针实际上都作为偏移量(减去第一个头的大小)出现在文件中，这一点很重要。我正在慢慢地前进。



## 创建规则

我们的规则头中的第一个成员是规则结构的一个成员fointer（不是一个错误，代表‘文件指针’）：

```
typedef struct _YR_RULE
`{`
  int32_t g_flags;               // Global flags
  int32_t t_flags[MAX_THREADS];  // Thread-specific flags

  DECLARE_REFERENCE(const char*, identifier);
  DECLARE_REFERENCE(const char*, tags);
  DECLARE_REFERENCE(YR_META*, metas);
  DECLARE_REFERENCE(YR_STRING*, strings);
  DECLARE_REFERENCE(YR_NAMESPACE*, ns);

  // Used only when PROFILING_ENABLED is defined
  clock_t clock_ticks;

`}` YR_RULE;
```

你应该很快地将上述结构中的一些指针识别为规则中的可选部分：identifier, tags, metas,strings, namespace。此时，我注意到了这个模式，并开始将所有相关结构复制到我的模板3中。每一个不等于0xFFABADA的fointer都意味着寻找那个位置并无限地解析那里的结构。

对于我们的空规则(它没有tags, metas 或 strings)，只有identifier和ns是有趣的。

你这样想是对的：“嘿，但是如果源文件中有不止一个规则呢？”如果仔细查看rules_list_head，你可能会猜到，按照它的名称，它指向第一条规则。YARA怎么知道其他人在哪？让我们按照代码查看何时实际使用规则，暂时忽略其他所有内容：

```
main -&gt; yr_rules_scan_file -&gt; yr_rules_scan_mem -&gt; yr_rules_scan_mem_blocks : yr_rules_foreach
```

盯着这个宏，我想出两件事：
- 规则在文件中按顺序排列。
- 规则列表由“空规则”终止。
什么是“空规则”？

```
#define RULE_IS_NULL(x) 
    (((x)-&gt;g_flags) &amp; RULE_GFLAGS_NULL)
```

搜索RULE_GFLAGS_NULL显示它是在_yr_compiler_compile_rules中设置的，以及在第一个规则之后那些神秘的0xFA字节是什么：

```
// Write a null rule indicating the end.
  memset(&amp;null_rule, 0xFA, sizeof(YR_RULE));
  null_rule.g_flags = RULE_GFLAGS_NULL;
```

[![](https://p2.ssl.qhimg.com/t01f2e56f7e7539b57c.png)](https://p2.ssl.qhimg.com/t01f2e56f7e7539b57c.png)在YR_RULE结构中剩下要理解的全部内容就是YR_NAMESPACE。唯一令人感兴趣的是命名空间名称的fointer，如果未指定名称空间名称，则为默认值：

```
typedef struct _YR_NAMESPACE
`{`
  int32_t t_flags[MAX_THREADS];     // Thread-specific flags
  DECLARE_REFERENCE(char*, name);

`}` YR_NAMESPACE;
```



## 全是关于对齐（alignment）

我假设你一直在使用你最喜欢的十六进制编辑器，并且已经知道所有QWORD成员(以及包含它们的结构)都应该对齐到一个8字节的边界，因为该文件实际上是一个内存映射。好吧，你是对的。

在这种情况下，填充0xCC的DWORD是填充的好迹象。请注意，文件头有12个字节长，这意味着当在十六进制编辑器中查看时对齐会出错。



## Null-spotting

回到_yr_compiler_compile_rules，我不禁发现编译器在“null rule”之后立即构建了一个“null external”，其方式与此类似：

```
// Write a null external the end.
  memset(&amp;null_external, 0xFA, sizeof(YR_EXTERNAL_VARIABLE));
  null_external.type = EXTERNAL_VARIABLE_TYPE_NULL;
```

由于我没有指定任何外部元素，所以规则头中的externals_list_head应该指向‘‘null external’，并使用它。请记住，与“空规则”不同，这是用EXTERNAL_VARIABLE_TYPE_NULL值标记的，它等于0。



## 准备，设置，编码

就在这里，我找到了code_start fointer，放弃了我最初对文件格式的兴趣。作为一个虚拟机的粉丝，我对字节码的实现细节很感兴趣。

在整个解决方案中搜索code_start，我们很快就会得到yr_execute_code，这是一个值得骄傲的所有者，它只能被描述为一个“大屁股开关语句（big-ass switch statement）”：[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ea49c535ce4170ee.png)与规则/外部规则不同的是，YARA一直在执行字节码，直到达到一个特殊的标记。在本例中，OP_HART：

```
while(!stop)
`{`
  opcode = *ip;
  ip++;

  switch(opcode)
  `{`
    case OP_NOP:
      break;

    case OP_HALT:
      assert(sp == 0); 
      stop = TRUE;
      break;

// ...truncated
```



## YARA虚拟机

这是一个基于堆栈的VM，它的Scratch内存为128个值。除了按位、逻辑和算术运算之外，还有几种专门针对VM堆栈和Scratch内存的操作码。

VM通过YR_VALUE根据操作码获取适当的类型：

```
typedef union _YR_VALUE
`{`
  int64_t i;
  double d;
  void* p;
  struct _YR_OBJECT* o;
  YR_STRING* s;
  SIZED_STRING* ss;
  RE* re;

`}` YR_VALUE;
```

值得注意的是，由于union可能代表一个重新定位的fointer，字节码中的每个直接部分都必须是64位长。



## 反编译

我开始在我的模板中实现一个小的反汇编程序，这是根据我之前的空规则中的操作码实现的。事后看来，我也许应该用python写点东西。结果如下：

```
OP_INIT
OP_PUSH
OP_INCR_M
OP_NOP
OP_HALT
```
- OP_INIT_RULE看起来有点复杂，所以我暂时满足于跳过实现。
- OP_Push只是从字节码中读取下一个YR_VALUE，并将其推送到vm堆栈上。
- OP_incr_M增加了下次直接索引的Scratch mem中的YR_VALUE


## WAT

一切似乎都很合理-等等，什么？

```
case OP_INCR_M:
  r1.i = *(uint64_t*)(ip);
  ip += sizeof(uint64_t);
  mem[r1.i]++; // &lt; ---------  WAT
  break;
```

这很奇怪，我没料到会有这么小的安全问题，但我有预感这不限于那个操作码。我扫描了其他操作码证明我是对的：

```
case OP_PUSH_M:
    r1.i = *(uint64_t*)(ip);
    ip += sizeof(uint64_t);
    r1.i = mem[r1.i];           // Out-of-bounds Read
    push(r1);
    break;

  case OP_POP_M:
    r1.i = *(uint64_t*)(ip);
    ip += sizeof(uint64_t);
    pop(r2);
    mem[r1.i] = r2.i;           // Out-of-bounds Write
    break;
```

Scratch内存mem放在真正的堆栈上，这意味着可以轻松地使用两个操作码从堆栈中读取内容并编写ROP链：

```
int yr_execute_code(
    YR_RULES* rules,
    YR_SCAN_CONTEXT* context,
    int timeout,
    time_t start_time)
`{`
  int64_t mem[MEM_SIZE];

  ...truncated
```



## 扩充已编译的规则

所以我要做的第一件事就是用我手工制作的YARA程序集创建一个编译后的规则。这并不难，我所要做的就是：
- 将二进制规则作为模板读取
- 跟随标头到code_start
- 汇编新代码
- 注入新代码
- 在我的代码之后更新所有的提示
- 将重新定位表更新到正确的偏移量
- 删除指向旧代码的重定位，这样它们就不会更改我的代码
- 修补文件散列
我决定从头开始构建一条规则会更容易，或者至少更不容易出错。最基本的考验将是自己重建以前的空规则。



## 大小问题

在这一点上，我想解决让人头疼的文件大小问题。这有点烦人，我认为这是一个很好的测试，我已经学到了什么。

假设YARA只要指向有效数据，就不关心目标指向哪里，我选择将我的代码放在文件体的末尾，这导致了以下结构：

```
YR_HDR // file header
```

```
YARA_RULES_FILE_HEADER
YR_RULE 
YR_RULE // null rule
YR_EXTERNAL_VARIABLE // null external
YR_NAMESPACE
CHAR[] namespace_name
CHAR[] rule_name
YR_AC_MATCH_TABLE
EMPTY_TRANSITION_TABLE
```

```
MY_CODE
```

```
RELOCATION_TABLE
END_OF_RELOCATION_MARKER
FILE_HASH
```

由于这个事实，重定位表只包含需要重定位的偏移量，所以重定位表要小得多。

直到现在，我还没有讨论YR_AC_MATCH_TABLE和EMPTY_TRANSITION_TABLE结构。我很确定这些都是用在 [Aho-Corasick算法](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm)上的。我尽力不理睬他们。



## 到达这里是乐趣的一半。

遗憾的是，在让YARA在yr_execute_code中执行字节码之前，我们必须通过_yr_rules_scan_mem_block，它使用前面提到的 Aho-Corasick 结构：

```
uint16_t index;
uint32_t state = YR_AC_ROOT_STATE;
...

index = block_data[i++] + 1;  // &lt;-- block_data is the scanned memory, we can't control it
transition = transition_table[state + index];   // &lt;-- this is troublesome

while (YR_AC_INVALID_TRANSITION(transition, index))
`{`
  if (state != YR_AC_ROOT_STATE)
  `{`
    state = transition_table[state] &gt;&gt; 32;
    transition = transition_table[state + index];
  `}`
  else
  `{`
    transition = 0;
    break;
  `}`
`}`

state = transition &gt;&gt; 32;       // &lt;-- we must make sure state remains 0
`}`

match = match_table[state].match; // &lt;-- this is troublesome as well
```

简而言之，只要state变量保持在0并且transition仍然小于MAX_UIN，那么我们就可以成功地执行这个函数。transition从transition_table读取，该表显然有MAX_UBYTE+1 64位条目。

为了确定上面的情况，我有一个全是0的EMPTY_TRANSITION_TABLE，还有一个YR_AC_MATCH_TABLE，它也全是0。

在所有这些之后，我得到了一个只有~3kb大小的有效规则文件。



## 大逃亡

最后，我可以开始利用这些漏洞了。有几个小注意事项要记住：
1. 只能用64位块读和写
1. 只能从堆栈中作为偏移量读/写。
1. 不知道我的字节码在哪里
1. 在函数返回之前，由于在清理过程中使用的参数，我不能覆盖很多真正的堆栈。
第四个是唯一真正的问题。在清理过程中调用yr_modules_unload_all。该函数使用context-&gt;objects_table，如果该指针被覆盖，则会崩溃，因为context结构也被分配到堆栈上。

```
typedef struct _YR_SCAN_CONTEXT
`{`
  uint64_t  file_size;
  uint64_t  entry_point;

  int flags;
  int tidx;

  void* user_data;

  YR_MEMORY_BLOCK_ITERATOR*  iterator;
  YR_HASH_TABLE*  objects_table;    // &lt;-- mustn't touch this
  YR_CALLBACK_FUNC  callback;

  YR_ARENA* matches_arena;
  YR_ARENA* matching_strings_arena;

`}` YR_SCAN_CONTEXT;
```

context指针本身不存在相同的问题，因为编译器将其保存为本地变量，并在调用yr_modules_unload_all时使用该方法：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](./context_copy.png)如果我不想找到跳过堆栈的那一部分(甚至更早)的小工具，我必须在此之前安装我的ROP链。这意味着我有9个QWORDS可供我使用。



## 我接受这个挑战

要运行calc(如您所做的)，我必须使用常规的GetModuleHandleXXX和GetProcAddress。这意味着：
- 计算模块的当前基地址
- 对每个小部件偏移量执行必要的重新定位。
- 使用所需的参数组织堆栈


## 你在哪里？

使用OP_PUSH_M和正确的索引读取返回地址是可能的。

这里只有一个函数调用yr_execute_code，因此在执行正确的移位/位数-并执行之后，可以使用OP_INT_SUB计算基地址。

由于代码将使用该基本地址来重新定位，我实际上将按计划使用Scratch内存，并将其保存到以后使用。

### <a class="reference-link" name="stdall%E5%BD%93%E7%84%B6%E5%BE%88%E5%A5%BD"></a>stdall当然很好

由于调用约定，我可以在ROP启动之前使用正确的参数设置堆栈的某些部分。

即时值很容易，字节码可以使用OP_POP_M将它们写入真正的堆栈。但是，在这种情况下，我还需要知道三个字符串的地址：
1. L”kernel32” for GetModuleHandleExW
1. “WinExec” for GetProcAddress
1. “calc” for WinExec


## YARA的搬迁到救援

文件格式中有一个令人讨厌的小特性-重新定位表。可以利用它将字节码操作数从相对文件偏移量重新定位到绝对地址。

我所需要做的就是将字符串的偏移量作为我的原始值，并将字符串转储到文件中的某个位置(我选择在代码的最后一条指令-OP_HALT之后将它们放在正确的位置)。



## 沉默而致命

为了使事情简单(并允许我将整个ROP放在9个连续的QWORDS中)，YARA在默认情况下用TRY/CATCH包装整个函数。一旦WinExec返回，它将跳转到堆栈中的某个地址(具有讽刺意味的是，它将跳转到context-&gt;objects_table)并静默地退出：

```
YR_TRYCATCH(
!(flags &amp; SCAN_FLAGS_NO_TRYCATCH), /* &lt;-- this flag is not set */
`{`
    result = yr_execute_code(
        rules,
        &amp;context,
        timeout,
        start_time);
`}`,`{`
    result = ERROR_COULD_NOT_MAP_FILE;
`}`);

```



## 小工具

我亲手挑选了这些[小玩意](https://github.com/bnbdr/swisscheese/blob/master/gadgets.md)，以适应我的PoC。我用过不止一次。这些文件中的某些部分需要更改yarasm文件中的值。



## Attack vector

任何允许运行用户提供的规则文件而不验证它不是二进制规则的受害者或服务。无论是否扫描目标文件这应该都可以工作。



## 措施
- 检查对Scratch内存的每一次访问
- 需要一个显式标志来加载并运行编译后的规则
- 检查每个重新定位的地址是否在加载的文件中
- 使加载的文件成为只读的


## CVE

这两个漏洞分别被指定为CVE-ID CVE-2018-12034和CVE-2018-12035。



## 注意
- 这项研究是在32位YARA 3.7.1上完成的，在正式发布页面的二进制文件上进行了测试
- 这是在发布之前私下披露的
- 这是我在业余时间所做的事情，不要对我进行评判。
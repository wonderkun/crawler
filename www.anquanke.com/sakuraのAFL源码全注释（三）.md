> 原文链接: https://www.anquanke.com//post/id/213432 


# sakuraのAFL源码全注释（三）


                                阅读量   
                                **251430**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p2.ssl.qhimg.com/t019bded1e48f69c18e.jpg)](https://p2.ssl.qhimg.com/t019bded1e48f69c18e.jpg)



## afl-fuzz长叙

### <a class="reference-link" name="Fuzz%E6%89%A7%E8%A1%8C"></a>Fuzz执行

#### <a class="reference-link" name="%E4%B8%BB%E5%BE%AA%E7%8E%AF"></a>主循环
<li>首先精简队列`cull_queue`
</li>
<li>然后如果`queue_cur`为空，代表所有queue都被执行完一轮
<ul>
- 设置queue_cycle计数器加一，即代表所有queue被完整执行了多少轮。
- 设置current_entry为0，和queue_cur为queue首元素，开始新一轮fuzz。
- 如果是resume fuzz情况，则先检查seek_to是否为空，如果不为空，就从seek_to指定的queue项开始执行。
<li>刷新展示界面`show_stats`
</li>
<li>如果在一轮执行之后的queue里的case数，和执行之前一样，代表在完整的一轮执行里都没有发现任何一个新的case
<ul>
- 如果use_splicing为1，就设置cycles_wo_finds计数器加1
- 否则，设置use_splicing为1，代表我们接下来要通过splice重组queue里的case。- 注意fuzz_one并不一定真的执行当前queue_cur，它是有一定策略的，如果不执行，就直接返回1，否则返回0- sync_interval_cnt计数器加一，如果其结果是SYNC_INTERVAL(默认是5)的倍数，就进行一次sync
#### <a class="reference-link" name="fuzz_one"></a>fuzz_one
- 如果`pending_favored`不为0，则对于queue_cur被fuzz过或者不是favored的，有99%的几率直接返回1。
<li>如果`pending_favored`为0且queued_paths(即queue里的case总数)大于10
<ul>
- 如果queue_cycle大于1且queue_cur没有被fuzz过，则有75%的概率直接返回1
- 如果queue_cur被fuzz过，否则有95%的概率直接返回1
**CALIBRATION阶段**
- 假如当前项有校准错误，并且校准错误次数小于3次，那么就用calibrate_case再次校准。
**TRIMMING阶段**
<li>如果该case没有trim过，
<ul>
- 调用函数`trim_case(argv, queue_cur, in_buf)`进行trim(修剪)
- 设置queue_cur的trim_done为1
- 重新读取一次`queue_cur-&gt;len`到len中
**PERFORMANCE SCORE阶段**
<li>perf_score = `calculate_score(queue_cur)`
</li>
- 如果skip_deterministic为1，或者queue_cur被fuzz过，或者queue_cur的passed_det为1，则跳转去havoc_stage阶段
- 设置doing_det为1
**SIMPLE BITFLIP (+dictionary construction)阶段**
<li>下面这个宏很有意思
<pre><code class="lang-c++ hljs cpp">#define FLIP_BIT(_ar, _b) do `{` \
  u8* _arf = (u8*)(_ar); \
  u32 _bf = (_b); \
  _arf[(_bf) &gt;&gt; 3] ^= (128 &gt;&gt; ((_bf) &amp; 7)); \
`}` while (0)
</code></pre>
</li>
<li>设置stage_name为`bitflip 1/1`,_ar的取值是out_buf,而_bf的取值在[0: len &lt;&lt; 3)<br>
所以用`_bf &amp; 7`能够得到`0,1,2...7 0,1,2...7`这样的取值一共len组，然后`(_bf) &gt;&gt; 3`又将[0: len&lt;&lt;3)映射回了[0: len)，对应到buf里的每个byte，如图:<br>[![](https://sakura-1252236262.cos.ap-beijing.myqcloud.com/2020-07-27-023812.jpg)](https://sakura-1252236262.cos.ap-beijing.myqcloud.com/2020-07-27-023812.jpg)<br>
所以在从`0-len*8`的遍历过程中会通过亦或运算，依次将每个位翻转，然后执行一次`common_fuzz_stuff`，然后再翻转回来。
<pre><code class="lang-c++ hljs cpp">stage_max = len &lt;&lt; 3;
for (stage_cur = 0; stage_cur &lt; stage_max; stage_cur++)
`{`
  FLIP_BIT(out_buf, stage_cur);

  if (common_fuzz_stuff(argv, out_buf, len)) goto abandon_entry;

  FLIP_BIT(out_buf, stage_cur);
`}`
</code></pre>
</li>
<li>在进行bitflip 1/1变异时，对于每个byte的最低位(least significant bit)翻转还进行了额外的处理：如果连续多个bytes的最低位被翻转后，程序的执行路径都未变化，而且与原始执行路径不一致，那么就把这一段连续的bytes判断是一条token。<br>
比如对于SQL的`SELECT *`，如果`SELECT`被破坏，则肯定和正确的路径不一致，而被破坏之后的路径却肯定是一样的，比如`AELECT`和`SBLECT`，显然都是无意义的，而只有不破坏token，才有可能出现和原始执行路径一样的结果，所以AFL在这里就是在猜解关键字token。</li>
- token默认最小是3，最大是32,每次发现新token时，通过`maybe_add_auto`添加到`a_extras`数组里。
<li>
`stage_finds[STAGE_FLIP1]`的值加上在整个FLIP_BIT中新发现的路径和Crash总和</li>
<li>
`stage_cycles[STAGE_FLIP1]`的值加上在整个FLIP_BIT中执行的target次数`stage_max`
</li>
<li>设置stage_name为`bitflip 2/1`,原理和之前一样，只是这次是连续翻转相邻的两位。
<pre><code class="lang-c++ hljs cpp">stage_max = (len &lt;&lt; 3) - 1;
for (stage_cur = 0; stage_cur &lt; stage_max; stage_cur++)
`{`
  FLIP_BIT(out_buf, stage_cur);
  FLIP_BIT(out_buf, stage_cur + 1);

  if (common_fuzz_stuff(argv, out_buf, len)) goto abandon_entry;

  FLIP_BIT(out_buf, stage_cur);
  FLIP_BIT(out_buf, stage_cur + 1);
`}`
</code></pre>
</li>
- 然后保存结果到`stage_finds[STAGE_FLIP2]和stage_cycles[STAGE_FLIP2]`里。
- 同理，设置stage_name为`bitflip 4/1`，翻转连续的四位并记录。
<li>生成effector map
<ul>
- 在进行bitflip 8/8变异时，AFL还生成了一个非常重要的信息：effector map。这个effector map几乎贯穿了整个deterministic fuzzing的始终。
- 具体地，在对每个byte进行翻转时，如果其造成执行路径与原始路径不一致，就将该byte在effector map中标记为1，即“有效”的，否则标记为0，即“无效”的。
- 这样做的逻辑是：如果一个byte完全翻转，都无法带来执行路径的变化，那么这个byte很有可能是属于”data”，而非”metadata”（例如size, flag等），对整个fuzzing的意义不大。所以，在随后的一些变异中，会参考effector map，跳过那些“无效”的byte，从而节省了执行资源。
- 由此，通过极小的开销（没有增加额外的执行次数），AFL又一次对文件格式进行了启发式的判断。看到这里，不得不叹服于AFL实现上的精妙。
- 不过，在某些情况下并不会检测有效字符。第一种情况就是dumb mode或者从fuzzer，此时文件所有的字符都有可能被变异。第二、第三种情况与文件本身有关：- 这里要注意在翻转之前会先检查eff_map里对应于这两个字节的标志是否为0，如果为0，则这两个字节是无效的数据，stage_max减一，然后开始变异下一个字。
- common_fuzz_stuff执行变异后的结果，然后还原。- 在每次翻转之前会检查eff_map里对应于这四个字节的标志是否为0，如果是0，则这两个字节是无效的数据，stage_max减一，然后开始变异下一组双字。
**ARITHMETIC INC/DEC**
- 在bitflip变异全部进行完成后，便进入下一个阶段：arithmetic。与bitflip类似的是，arithmetic根据目标大小的不同，也分为了多个子阶段：
- arith 8/8，每次对8个bit进行加减运算，按照每8个bit的步长从头开始，即对文件的每个byte进行整数加减变异
- arith 16/8，每次对16个bit进行加减运算，按照每8个bit的步长从头开始，即对文件的每个word进行整数加减变异
- arith 32/8，每次对32个bit进行加减运算，按照每8个bit的步长从头开始，即对文件的每个dword进行整数加减变异
- 加减变异的上限，在config.h中的宏ARITH_MAX定义，默认为35。所以，对目标整数会进行+1, +2, …, +35, -1, -2, …, -35的变异。特别地，由于整数存在大端序和小端序两种表示方式，AFL会贴心地对这两种整数表示方式都进行变异。
- 此外，AFL还会智能地跳过某些arithmetic变异。第一种情况就是前面提到的effector map：如果一个整数的所有bytes都被判断为“无效”，那么就跳过对整数的变异。第二种情况是之前bitflip已经生成过的变异：如果加/减某个数后，其效果与之前的某种bitflip相同，那么这次变异肯定在上一个阶段已经执行过了，此次便不会再执行。
**INTERESTING VALUES**
- 下一个阶段是interest，具体可分为：
- interest 8/8，每次对8个bit进替换，按照每8个bit的步长从头开始，即对文件的每个byte进行替换
- interest 16/8，每次对16个bit进替换，按照每8个bit的步长从头开始，即对文件的每个word进行替换
- interest 32/8，每次对32个bit进替换，按照每8个bit的步长从头开始，即对文件的每个dword进行替换
<li>而用于替换的”interesting values”，是AFL预设的一些比较特殊的数,这些数的定义在config.h文件中
<pre><code class="lang-c++ hljs cpp">static s8  interesting_8[]  = `{` INTERESTING_8 `}`;
static s16 interesting_16[] = `{` INTERESTING_8, INTERESTING_16 `}`;
static s32 interesting_32[] = `{` INTERESTING_8, INTERESTING_16, INTERESTING_32 `}`;
</code></pre>
</li>
- 与之前类似，effector map仍然会用于判断是否需要变异；此外，如果某个interesting value，是可以通过bitflip或者arithmetic变异达到，那么这样的重复性变异也是会跳过的。
**DICTIONARY STUFF**<br>
进入到这个阶段，就接近deterministic fuzzing的尾声了。具体有以下子阶段：
<li>user extras(over),从头开始,将用户提供的tokens依次替换到原文件中,stage_max为`extras_cnt * len`
</li>
<li>user extras(insert),从头开始,将用户提供的tokens依次插入到原文件中,stage_max为`extras_cnt * len`
</li>
<li>auto extras(over),从头开始,将自动检测的tokens依次替换到原文件中,stage_max为`MIN(a_extras_cnt, USE_AUTO_EXTRAS) * len`
</li>
- 其中，用户提供的tokens，是在词典文件中设置并通过-x选项指定的，如果没有则跳过相应的子阶段。
**RANDOM HAVOC**
- 对于非dumb mode的主fuzzer来说，完成了上述deterministic fuzzing后，便进入了充满随机性的这一阶段；对于dumb mode或者从fuzzer来说，则是直接从这一阶段开始。
- havoc，顾名思义，是充满了各种随机生成的变异，是对原文件的“大破坏”。具体来说，havoc包含了对原文件的多轮变异，每一轮都是将多种方式组合（stacked）而成：
- 随机选取某个bit进行翻转
- 随机选取某个byte，将其设置为随机的interesting value
- 随机选取某个word，并随机选取大、小端序，将其设置为随机的interesting value
- 随机选取某个dword，并随机选取大、小端序，将其设置为随机的interesting value
- 随机选取某个byte，对其减去一个随机数
- 随机选取某个byte，对其加上一个随机数
- 随机选取某个word，并随机选取大、小端序，对其减去一个随机数
- 随机选取某个word，并随机选取大、小端序，对其加上一个随机数
- 随机选取某个dword，并随机选取大、小端序，对其减去一个随机数
- 随机选取某个dword，并随机选取大、小端序，对其加上一个随机数
- 随机选取某个byte，将其设置为随机数
- 随机删除一段bytes
- 随机选取一个位置，插入一段随机长度的内容，其中75%的概率是插入原文中随机位置的内容，25%的概率是插入一段随机选取的数
- 随机选取一个位置，替换为一段随机长度的内容，其中75%的概率是替换成原文中随机位置的内容，25%的概率是替换成一段随机选取的数
- 随机选取一个位置，用随机选取的token（用户提供的或自动生成的）替换
- 随机选取一个位置，用随机选取的token（用户提供的或自动生成的）插入
- 怎么样，看完上面这么多的“随机”，有没有觉得晕？还没完，AFL会生成一个随机数，作为变异组合的数量，并根据这个数量，每次从上面那些方式中随机选取一个（可以参考高中数学的有放回摸球），依次作用到文件上。如此这般丧心病狂的变异，原文件就大概率面目全非了，而这么多的随机性，也就成了fuzzing过程中的不可控因素，即所谓的“看天吃饭”了。
- splice
- 设置ret_val的值为0
- 如果queue_cur通过了评估，且was_fuzzed字段是0，就设置`queue_cur-&gt;was_fuzzed`为1，然后pending_not_fuzzed计数器减一
如果queue_cur是favored, pending_favored计数器减一。

#### <a class="reference-link" name="sync_fuzzers(char%20**argv)"></a>sync_fuzzers(char **argv)

这个函数其实就是读取其他sync文件夹下的queue文件，然后保存到自己的queue里。
- 打开`sync_dir`文件夹
<li>while循环读取该文件夹下的目录和文件`while ((sd_ent = readdir(sd)))`
<ul>
- 跳过`.`开头的文件和`sync_id`即我们自己的输出文件夹
- 读取`out_dir/.synced/sd_ent-&gt;d_name`文件即`id_fd`里的前4个字节到`min_accept`里，设置`next_min_accept`为`min_accept`，这个值代表之前从这个文件夹里读取到的最后一个queue的id。
- 设置stage_name为`sprintf(stage_tmp, "sync %u", ++sync_cnt);`，设置stage_cur为0，stage_max为0
<li>循环读取`sync_dir/sd_ent-&gt;d_name/queue`文件夹里的目录和文件
<ul>
- 同样跳过`.`开头的文件和标识小于min_accept的文件，因为这些文件应该已经被sync过了。
<li>如果标识`syncing_case`大于等于next_min_accept，就设置next_min_accept为`syncing_case + 1`
</li>
<li>开始同步这个case
<ul>
- 如果case大小为0或者大于MAX_FILE(默认是1M),就不进行sync。
<li>否则mmap这个文件到内存mem里，然后`write_to_testcase(mem, st.st_size)`,并run_target,然后通过save_if_interesting来决定是否要导入这个文件到自己的queue里，如果发现了新的path，就导入。
<ul>
<li>设置syncing_party的值为`sd_ent-&gt;d_name`
</li>
- 如果save_if_interesting返回1，queued_imported计数器就加1
#### trim_case(char ***argv, struct queue_entry **q, u8 *in_buf)
- 如果这个case的大小len小于5字节，就直接返回
- 设置stage_name的值为tmp，在bytes_trim_in的值里加上len，bytes_trim_in代表被trim过的字节数
- 计算len_p2，其值是大于等于q-&gt;len的第一个2的幂次。（eg.如果len是5704,那么len_p2就是8192）
- 取`len_p2的1/16`为remove_len，这是起始步长。
<li>进入while循环，终止条件是remove_len小于终止步长`len_p2的1/1024`,**每轮循环步长会除2.**
<ul>
- 设置remove_pos的值为remove_len
- 读入`"trim %s/%s", DI(remove_len), DI(remove_len)`到tmp中, 即stage_name = “trim 512/512”
<li>设置stage_cur为0，stage_max为`q-&gt;len / remove_len`
</li>
<li>进入while循环，`remove_pos &lt; q-&gt;len`,即每次前进remove_len个步长，直到整个文件都被遍历完为止。
<ul>
- 由in_buf中remove_pos处开始，向后跳过remove_len个字节，写入到`.cur_input`里，然后运行一次`fault = run_target`，trim_execs计数器加一
<li>由所得trace_bits计算出一个cksum，和`q-&gt;exec_cksum`比较
<ul>
<li>如果相等
<ul>
<li>从`q-&gt;len`中减去remove_len个字节，并由此重新计算出一个`len_p2`，这里注意一下`while (remove_len &gt;= MAX(len_p2 / TRIM_END_STEPS, TRIM_MIN_BYTES))`
</li>
- 将`in_buf+remove_pos+remove_len`到最后的字节，前移到`in_buf+remove_pos`处，等于删除了remove_pos向后的remove_len个字节。
- 如果needs_write为0，则设置其为1，并保存当前trace_bits到clean_trace中。<li>remove_pos加上remove_len，即前移remove_len个字节。**注意，如果相等，就无需前移**
</li>- 删除原来的q-&gt;fname，创建一个新的q-&gt;fname，将in_buf里的内容写入，然后用clean_trace恢复trace_bits的值。
- 进行一次update_bitmap_score
#### <a class="reference-link" name="u32%20calculate_score(struct%20queue_entry%20*q)"></a>u32 calculate_score(struct queue_entry *q)

根据queue entry的执行速度、覆盖到的path数和路径深度来评估出一个得分，这个得分perf_score在后面havoc的时候使用。<br>
前面的没什么好说的，这里的`q-&gt;depth`解释一下，它在每次add_to_queue的时候，会设置为`cur_depth+1`，而cur_depth是一个全局变量，一开始的初始值为0。
<li>处理输入时
<ul>
- 在read_testcases的时候会调用add_to_queue，此时所有的input case的queue depth都会被设置为1。- 然后在后面fuzz_one的时候，会先设置cur_depth为当前queue的depth，然后这个queue经过mutate之后调用save_if_interesting,如果是interesting case，就会被add_to_queue，此时就建立起了queue之间的关联关系，所以由当前queue变异加入的新queue，深度都在当前queue的基础上再增加。
#### u8 common_fuzz_stuff(char ***argv, u8 **out_buf, u32 len)

简单的说就是写入文件并执行，然后处理结果，如果出现错误，就返回1.
<li>如果定义了`post_handler`,就通过`out_buf = post_handler(out_buf, &amp;len)`处理一下out_buf，如果out_buf或者len有一个为0，则直接返回0
<ul>
- **这里其实很有价值，尤其是如果需要对变异完的queue，做一层wrapper再写入的时候。**- 如果`subseq_tmouts++ &gt; TMOUT_LIMIT`（默认250），就将cur_skipped_paths加一，直接返回1
- subseq_tmout是连续超时数- 设置skip_requested为0，然后将cur_skipped_paths加一，直接返回1
#### <a class="reference-link" name="void%20write_to_testcase(void%20*mem,%20u32%20len)"></a>void write_to_testcase(void *mem, u32 len)

将从`mem`中读取`len`个字节，写入到`.cur_input`中

#### u8 save_if_interesting(char ***argv, void **mem, u32 len, u8 fault)

检查这个case的执行结果是否是interesting的，决定是否保存或跳过。如果保存了这个case，则返回1，否则返回0<br>
以下分析不包括crash_mode，暂时略过以简洁
- 设置keeping等于0
<li>
`hnb = has_new_bits(virgin_bits)`，如果没有新的path发现或者path命中次数相同，就直接返回0</li>
- 否则，将case保存到`fn = alloc_printf("%s/queue/id:%06u,%s", out_dir, queued_paths, describe_op(hnb))`文件里
<li>
`add_to_queue(fn, len, 0);`将其添加到队列里</li>
- 如果hnb的值是2，代表发现了新path，设置刚刚加入到队列里的queue的has_new_cov字段为1，即`queue_top-&gt;has_new_cov = 1`，然后queued_with_cov计数器加一
- 保存hash到其exec_cksum
<li>评估这个queue，`calibrate_case(argv, queue_top, mem, queue_cycle - 1, 0)`
</li>
- 设置keeping值为1.
<li>根据fault结果进入不同的分支
<ul>
<li>FAULT_TMOUT
<ul>
- 设置total_tmouts计数器加一
- 如果unique_hangs的个数超过能保存的最大数量`KEEP_UNIQUE_HANG`，就直接返回keeping的值
- 如果不是dumb mode，就`simplify_trace((u64 *) trace_bits)`进行规整。
- 如果没有发现新的超时路径，就直接返回keeping
- 否则，代表发现了新的超时路径，unique_tmouts计数器加一
<li>如果hang_tmout大于exec_tmout，则以hang_tmout为timeout，重新执行一次runt_target
<ul>
- 如果结果为`FAULT_CRASH`，就跳转到keep_as_crash
- 如果结果不是`FAULT_TMOUT`，就返回keeping，否则就使`unique_hangs`计数器加一，然后更新last_hang_time的值，并保存到`alloc_printf("%s/hangs/id:%06llu,%s", out_dir, unique_hangs, describe_op(0))`文件。- total_crashes计数器加一
- 如果unique_crashes大于能保存的最大数量`KEEP_UNIQUE_CRASH`即5000，就直接返回keeping的值
- 同理，如果不是dumb mode，就`simplify_trace((u64 *) trace_bits)`进行规整
- 如果没有发现新的crash路径，就直接返回keeping
- 否则，代表发现了新的crash路径，unique_crashes计数器加一，并将结果保存到`alloc_printf("%s/crashes/id:%06llu,sig:%02u,%s", out_dir,unique_crashes, kill_signal, describe_op(0))`文件。
- 更新last_crash_time和last_crash_execs- 抛出异常
#### <a class="reference-link" name="simplify_trace(u64%20*mem)"></a>simplify_trace(u64 *mem)
<li>按8个字节为一组循环读入，直到完全读取完mem
<ul>
<li>如果mem不为空
<ul>
<li>i从0-7，`mem8[i] = simplify_lookup[mem8[i]]`，代表规整该路径的命中次数到指令值，这个路径如果没有命中，就设置为1，如果命中了，就设置为128，即二进制的`1000 0000`
</li>
```
static const u8 simplify_lookup[256] = `{`

        [0]         = 1,
        [1 ... 255] = 128

`}`;
```



## 通信和覆盖率信息的记录

### <a class="reference-link" name="%E5%85%B3%E9%94%AE%E5%8F%98%E9%87%8F%E5%92%8C%E5%B8%B8%E9%87%8F"></a>关键变量和常量

```
.bss:000000000060208F unk_60208F      db    ? ;               ; DATA XREF: deregister_tm_clones↑o
.bss:0000000000602090 __afl_area_ptr  dq ?                    ; DATA XREF: __afl_maybe_log+4↑r
.bss:0000000000602090                                         ; __afl_maybe_log+48↑w ...
.bss:0000000000602098 __afl_prev_loc  dq ?                    ; DATA XREF: __afl_maybe_log:__afl_store↑r
.bss:0000000000602098                                         ; __afl_maybe_log+17↑w ...
.bss:00000000006020A0 ; __pid_t _afl_fork_pid
.bss:00000000006020A0 __afl_fork_pid  dd ?                    ; DATA XREF: __afl_maybe_log+1C6↑w
.bss:00000000006020A0                                         ; __afl_maybe_log+1D3↑o ...
.bss:00000000006020A4 ; int _afl_temp
.bss:00000000006020A4 __afl_temp      dd ?                    ; DATA XREF: __afl_maybe_log+174↑o
.bss:00000000006020A4                                         ; __afl_maybe_log+198↑o ...
.bss:00000000006020A8 __afl_setup_failure db ?                ; DATA XREF: __afl_maybe_log:__afl_setup↑r
.bss:00000000006020A8                                         ; __afl_maybe_log:__afl_setup_abort↑w
...
.text:0000000000400DEF ; char AFL_SHM_ENV[]
.text:0000000000400DEF _AFL_SHM_ENV    db '__AFL_SHM_ID',0     ; DATA XREF: __afl_maybe_log+11F↑o
.text:0000000000400DEF                                         ; Alternative name is '.AFL_VARS'
```
<li>__afl_area_ptr
<ul>
- 存储共享内存的首地址- 存储上一个位置，即上一次R(MAP_SIZE)生成的随机数的值- 存储fork出来的子进程的pid- 临时buffer- 申请的共享内存的shm_id被设置为环境变量`__AFL_SHM_ID`的值，所以通过这个环境变量来获取shm_id，然后进一步得到共享内存。
### <a class="reference-link" name="trampoline_fmt_64"></a>trampoline_fmt_64

```
.text:00000000004009C0                 lea     rsp, [rsp-98h]
.text:00000000004009C8                 mov     [rsp+98h+var_98], rdx
.text:00000000004009CC                 mov     [rsp+98h+var_90], rcx
.text:00000000004009D1                 mov     [rsp+98h+var_88], rax
.text:00000000004009D6                 mov     rcx, 2359h----&gt;R(MAP_SIZE)
.text:00000000004009DD                 call    __afl_maybe_log
.text:00000000004009E2                 mov     rax, [rsp+98h+var_88]
.text:00000000004009E7                 mov     rcx, [rsp+98h+var_90]
.text:00000000004009EC                 mov     rdx, [rsp+98h+var_98]
.text:00000000004009F0                 lea     rsp, [rsp+98h]
```

插入的trampoline_fmt_64只有在`mov rcx, xxx`这里不同，其xxx的取值就是随机数R(MAP_SIZE),以此来标识与区分每个分支点，然后传入`__afl_maybe_log`作为第二个参数调用这个函数。

### <a class="reference-link" name="__afl_maybe_log"></a>__afl_maybe_log

直接看汇编，还是很好理解的
<li>首先检查`_afl_area_ptr`是否为0，即是否共享内存已经被设置了。**换句话说，只有第一个__afl_maybe_log会执行这个if里的代码**
<ul>
<li>如果`_afl_area_ptr`为0，即共享内存还没被设置，则判断`_afl_setup_failure`是否为真，如果为真，则代表setup失败，直接返回。
<ul>
<li>读取`_afl_global_area_ptr`的值
<ul>
<li>如果不为0，则赋值给`_afl_area_ptr`
</li>
<li>否则
<ul>
- 首先读取环境变量`__AFL_SHM_ID`，默认是个字符串，atoi转一下，得到shm_id，然后通过shmat启动对该共享内存的访问，并把共享内存连接到当前进程的地址空间，将得到的地址，保存到`_afl_area_ptr`和`_afl_global_area_ptr`中。
- 然后通过`FORKSRV_FD+1`即199这个文件描述符，向状态管道中写入4个字节的值，用来告知afl fuzz，fork server成功启动，等待下一步指示。
<li>进入`__afl_fork_wait_loop`循环，从`FORKSRV`即198中读取字节到`_afl_temp`，直到读取到4个字节，这代表afl fuzz命令我们新建进程执行一次测试。
<ul>
- fork出子进程，原来的父进程充当fork server来和fuzz进行通信，而子进程则继续执行target。
- 父进程即fork server将子进程的pid写入到状态管道，告知fuzz。
- 然后父进程即fork server等待子进程结束，并保存其执行结果到`_afl_temp`中，然后将子进程的执行结果，从`_afl_temp`写入到状态管道，告知fuzz。
- 父进程不断轮询`__afl_fork_wait_loop`循环，不断从控制管道读取，直到fuzz端命令fork server进行新一轮测试。<li>简单的说，就是将上一个桩点的值(prev_location)和当前桩点的值(`R(MAP_SIZE)`)异或，取值后，使得**共享内存里对应的槽**的值加一，然后将prev_location设置为`cur_location &gt;&gt; 1;`
</li>
<li>因此，AFL为每个代码块生成一个随机数，作为其“位置”的记录；随后，对分支处的”源位置“和”目标位置“进行异或，并将异或的结果作为该分支的key，保存每个分支的执行次数。用于保存执行次数的实际上是一个哈希表，大小为MAP_SIZE=64K，当然会存在碰撞的问题；但根据AFL文档中的介绍，对于不是很复杂的目标，碰撞概率还是可以接受的。
<pre><code class="lang-c++ hljs cpp">cur_location = &lt;COMPILE_TIME_RANDOM&gt;;
shared_mem[cur_location ^ prev_location]++; 
prev_location = cur_location &gt;&gt; 1;
</code></pre>
</li>
- 另外，比较有意思的是，AFL需要将cur_location右移1位后，再保存到prev_location中。官方文档中解释了这样做的原因。假设target中存在A-&gt;A和B-&gt;B这样两个跳转，如果不右移，那么这两个分支对应的异或后的key都是0，从而无法区分；另一个例子是A-&gt;B和B-&gt;A，如果不右移，这两个分支对应的异或后的key也是相同的。
```
char __usercall _afl_maybe_log@&lt;al&gt;(char a1@&lt;of&gt;, __int64 a2@&lt;rcx&gt;, __int64 a3@&lt;xmm0&gt;, __int64 a4@&lt;xmm1&gt;, __int64 a5@&lt;xmm2&gt;, __int64 a6@&lt;xmm3&gt;, __int64 a7@&lt;xmm4&gt;, __int64 a8@&lt;xmm5&gt;, __int64 a9@&lt;xmm6&gt;, __int64 a10@&lt;xmm7&gt;, __int64 a11@&lt;xmm8&gt;, __int64 a12@&lt;xmm9&gt;, __int64 a13@&lt;xmm10&gt;, __int64 a14@&lt;xmm11&gt;, __int64 a15@&lt;xmm12&gt;, __int64 a16@&lt;xmm13&gt;, __int64 a17@&lt;xmm14&gt;, __int64 a18@&lt;xmm15&gt;)
`{`
  ...
  v19 = _afl_area_ptr;
  if ( !_afl_area_ptr )
  `{`
    if ( _afl_setup_failure )
      return v18 + 127;
    v19 = _afl_global_area_ptr;
    if ( _afl_global_area_ptr )
    `{`
      _afl_area_ptr = _afl_global_area_ptr;
    `}`
    else
    `{`
      ...
      v22 = getenv("__AFL_SHM_ID");
      if ( !v22 || (v23 = atoi(v22), v24 = shmat(v23, 0LL, 0), v24 == (void *)-1LL) )
      `{`
        ++_afl_setup_failure;
        v18 = v29;
        return v18 + 127;
      `}`
      _afl_area_ptr = (__int64)v24;
      _afl_global_area_ptr = v24;
      v28 = (__int64)v24;
      if (write(199, &amp;_afl_temp, 4uLL) == 4 )
      `{`
        while ( 1 )
        `{`
          v25 = 198;
          if (read(198, &amp;_afl_temp, 4uLL) != 4 )
            break;
          LODWORD(v26) = fork();
          if ( v26 &lt; 0 )
            break;
          if ( !v26 )
            goto __afl_fork_resume;
          _afl_fork_pid = v26;
          write(199, &amp;_afl_fork_pid, 4uLL);
          v25 = _afl_fork_pid;
          LODWORD(v27) = waitpid(_afl_fork_pid, &amp;_afl_temp, 0);
          if ( v27 &lt;= 0 )
            break;
          write(199, &amp;_afl_temp, 4uLL);
        `}`
        _exit(v25);
      `}`
__afl_fork_resume:
      close(198);
      close(199);
      v19 = v28;
      v18 = v29;
      a2 = v30;
    `}`
  `}`
  v20 = _afl_prev_loc ^ a2;
  _afl_prev_loc ^= v20;
  _afl_prev_loc = (unsigned __int64)_afl_prev_loc &gt;&gt; 1;
  ++*(_BYTE *)(v19 + v20);
  return v18 + 127;
`}`
```



## 其他
<li>strrchr
<ul>
<li>
`char *strrchr(const char *str, int c)` 在参数 str 所指向的字符串中搜索最后一次出现字符 c（一个无符号字符）的位置。</li><li>
`unsigned int strlen (char *s)` 用来计算指定的字符串s的长度，不包括结束字符”\0”。</li>
- 注意：strlen() 函数计算的是字符串的实际长度，遇到第一个’\0’结束。如果你只定义没有给它赋初值，这个结果是不定的，它会从首地址一直找下去，直到遇到’\0’停止。而sizeof返回的是变量声明后所占的内存数，不是实际长度，此外sizeof不是函数，仅仅是一个操作符，strlen()是函数。- Create a buffer with a copy of a string. Returns NULL for NULL inputs.
<li>
`size = strlen((char*)str) + 1;`
<pre><code class="hljs shell">ALLOC_MAGIC_C1-&gt; 00 ff 00 ff   size-&gt; 2e 00 00 00   ret-&gt; 2f 55 73 65   72 73 2f 73   │ ····.···/Users/s │
61 6b 75 72   61 2f 67 69   74 73 6f 75   72 63 65 2f   │ akura/gitsource/ │
41 46 4c 2f   63 6d 61 6b   65 2d 62 75   69 6c 64 2d   │ AFL/cmake-build- │
64 65 62 75   67 00 ALLOC_MAGIC_C2-&gt; f0 00   00 00 00 00   00 00 00 00   │ debug··········· │
</code></pre>
</li><li>
`int snprintf(char *str, int n, char * format [, argument, ...]);`函数用于将格式化的数据写入字符串</li>
- str为要写入的字符串；n为要写入的字符的最大数目，超过n会被截断；format为格式化字符串，与printf()函数相同；argument为变量。
<li>
[http://brg-liuwei.github.io/tech/2014/09/29/snprintf.html](http://brg-liuwei.github.io/tech/2014/09/29/snprintf.html)
<ul>
- 重点理解snprintf函数的返回值，不是实际打印出来的长度，而是实际应该打印的长度。- snprintf的可能的一种实现，及其可能存在的安全问题。<li>Allocate a buffer, returning zeroed memory.
<ul>
<li>DFL_ck_alloc_nozero
<pre><code class="hljs">00 ff 00 ff   35 00 00 00   00 00 00 00   00 00 00 00   │ ····5··········· │
00 00 00 00   00 00 00 00   00 00 00 00   00 00 00 00   │ ················ │
00 00 00 00   00 00 00 00   00 00 00 00   00 00 00 00   │ ················ │
00 00 00 00   00 00 00 00   00 00 00 00   00 f0 00 00   │ ················ │
</code></pre>
</li><li>User-facing macro to sprintf() to a dynamically allocated buffer
<ul>
- ck_alloc:分配内存
<li>snprintf:写入格式化字符串
<pre><code class="hljs coffeescript">00 ff 00 ff   35 00 00 00   2f 55 73 65   72 73 2f 73   │ ····5···/Users/s │
61 6b 75 72   61 2f 67 69   74 73 6f 75   72 63 65 2f   │ akura/gitsource/ │
41 46 4c 2f   63 6d 61 6b   65 2d 62 75   69 6c 64 2d   │ AFL/cmake-build- │
64 65 62 75   67 2f 61 66   6c 2d 61 73   00 f0 00 00   │ debug/afl-as···· │
</code></pre>
</li><li>
`int access(const char * pathname, int mode)` 检查调用进程是否可以对指定的文件执行某种操作。</li>
- 成功执行时，返回0。失败返回-1，errno被设为以下的某个值<li>
`char *strstr(const char *haystack, const char *needle)`在字符串 haystack 中查找第一次出现字符串 needle 的位置，不包含终止符 ‘\0’。</li>
- 返回该函数返回在 haystack 中第一次出现 needle 字符串的位置，如果未找到则返回 null。<li>
`int gettimeofday(struct timeval *tv, struct timezone *tz)`gettimeofday()会把目前的时间用tv结构体返回，当地时区的信息则放到tz所指的结构中。</li>
<li>timeval
<pre><code class="lang-c++ hljs cpp">_STRUCT_TIMEVAL
`{`
  __darwin_time_t         tv_sec;         /* seconds */
  __darwin_suseconds_t    tv_usec;        /* and microseconds */
`}`;
</code></pre>
</li>- 设置随机种子，注意只需要设置一次即可
- 1、生产随机数需要种子（Seed），且如果种子固定，random()每次运行生成的随机数（其实是伪随机数）也是固定的；因为返回的随机数是根据稳定的算法得出的稳定结果序列，并且Seed就是这个算法开始计算的第一个值。
<li>2、srandom()可以设定种子，比如srandom(0) 、srandom(1)等等。如果srandom设定了一个固定的种子，那么random得出的随机数就是固定的；<br>
如果程序运行时通过srandom(time(NULL))设定种子为随机的，那么random()每次生成的随机数就是非固定的了。</li>- [open函数的简要介绍](http://c.biancheng.net/cpp/html/238.html)
- [open函数返回值](https://blog.csdn.net/csdn66_2016/article/details/77716008)
- 调用成功时返回一个文件描述符fd，调用失败时返回-1，并修改errno<li>
`FILE * fdopen(int fildes, const char * mode);`fdopen()会将参数fildes 的文件描述词, 转换为对应的文件指针后返回.</li>
- 参数mode 字符串则代表着文件指针的流形态, 此形态必须和原先文件描述词读写模式相同. 关于mode字符串格式请参考fopen().
- 返回值：转换成功时返回指向该流的文件指针. 失败则返回NULL, 并把错误代码存在errno中.<li>
`char *fgets(char *str, int size, FILE *stream)`从指定的流 stream 读取一行，并把它存储在 str 所指向的字符串内。当读取 (size-1) 个字符时，或者读取到换行符时，或者到达文件末尾时，它会停止，具体视情况而定。</li>
- string为一个字符数组，用来保存读取到的字符。
- size为要读取的字符的个数。如果该行字符数大于size-1，则读到size-1个字符时结束，并在最后补充’\0’；如果该行字符数小于等于size-1，则读取所有字符，并在最后补充’\0’。即，每次最多读取size-1个字符。
<li>stream为文件流指针。<br>
-【返回值】读取成功，返回读取到的字符串，即string；失败或读到文件结尾返回NULL。因此我们不能直接通过fgets()的返回值来判断函数是否是出错而终止的，应该借助feof()函数或者ferror()函数来判断。</li><li>
`FILE * fopen(const char * path, const char * mode);`打开一个文件并返回文件指针</li>
- [fopen参数详解](http://c.biancheng.net/cpp/html/250.html)<li>
`int atexit (void (*function) (void));`atexit()用来设置一个程序正常结束前调用的函数. 当程序通过调用exit()或从main中返回时, 参数function所指定的函数会先被调用, 然后才真正由exit()结束程序.</li>
- 如果执行成功则返回0, 否则返回-1, 失败原因存于errno 中.<li>
`int mkdir(const char *pathname, mode_t mode);`mkdir()函数以mode方式创建一个以pathname为名字的目录，mode定义所创建目录的权限</li>
- 返回值: 0:目录创建成功 -1:创建失败<li>
`int flock(int fd,int operation);`flock()会依参数operation所指定的方式对参数fd所指的文件做各种锁定或解除锁定的动作。此函数只能锁定整个文件，无法锁定文件的某一区域。</li>
- LOCK_SH 建立共享锁定。多个进程可同时对同一个文件作共享锁定。
- LOCK_EX 建立互斥锁定。一个文件同时只有一个互斥锁定。
- LOCK_UN 解除文件锁定状态。
- LOCK_NB 无法建立锁定时，此操作可不被阻断，马上返回进程。通常与LOCK_SH或LOCK_EX 做OR(|)组合。
- 单一文件无法同时建立共享锁定和互斥锁定，而当使用dup()或fork()时文件描述词不会继承此种锁定。
- 返回值 返回0表示成功，若有错误则返回-1，错误代码存于errno。- `int scandir(const char *dir,struct dirent **namelist,int (*filter)(const void *b),int ( * compare )( const struct dirent **, const struct dirent ** ) );`
- `int alphasort(const void *a, const void *b);`
- `int versionsort(const void *a, const void *b);`
- 函数scandir扫描dir目录下(不包括子目录)满足filter过滤模式的文件，返回的结果是compare函数经过排序的，并保存在namelist中。注意namelist的元素是通过malloc动态分配内存的,所以在使用时要注意释放内存。alphasort和versionsort是使用到的两种排序的函数。
- 当函数成功执行时返回找到匹配模式文件的个数，如果失败将返回-1。- `int lstat (const char * file_name, struct stat * buf);`
- 函数说明：lstat()与stat()作用完全相同, 都是取得参数file_name 所指的文件状态, 其差别在于, 当文件为符号连接时, lstat()会返回该link 本身的状态. 详细内容请参考stat().
- 返回值：执行成功则返回0, 失败返回-1, 错误代码存于errno.<li>
`size_t read(int fd, void * buf, size_t count);`read()会把参数fd所指的文件传送count个字节到buf指针所指的内存中. 若参数count为0, 则read()不会有作用并返回0.</li>
- 返回值为实际读取到的字节数, 如果返回0, 表示已到达文件尾或是无可读取的数据,此外文件读写位置会随读取到的字节移动.
- 如果顺利,read()会返回实际读到的字节数, 最好能将返回值与参数count作比较, 若返回的字节数比要求读取的字节数少, 则有可能读到了文件尾
- 当有错误发生时则返回-1, 错误代码存入errno中, 而文件读写位置则无法预期.<li>
`int sscanf(const char *str, const char *format, ...)`从字符串读取格式化输入。</li>
- 如果成功，该函数返回成功匹配和赋值的个数。如果到达文件末尾或发生读错误，则返回EOF。
<li>例子
<pre><code class="lang-c++ hljs cpp">strcpy( dtm, "Saturday March 25 1989" );
sscanf( dtm, "%s %s %d  %d", weekday, month, &amp;day, &amp;year );

printf("%s %d, %d = %s\n", month, day, year, weekday )
...
March 25, 1989 = Saturday
</code></pre>
</li>- `int link (const char * oldpath, const char * newpath);`
- link()以参数newpath指定的名称来建立一个新的连接(硬连接)到参数oldpath所指定的已存在文件. 如果参数newpath指定的名称为一已存在的文件则不会建立连接.
- 返回值：成功则返回0, 失败返回-1, 错误原因存于errno.<li>
`int pipe(int fd[2])`创建一个简单的管道，若成功则为数组fd分配两个文件描述符，其中fd[0]用于读取管道，fd[1]用于写入管道</li>
- 若成功则返回零，否则返回-1，错误原因存于errno中。
- 管道，顾名思义，当我们希望将两个进程的数据连接起来的时候就可以使用它，从而将一个进程的输出数据作为另一个进程的输入数据达到通信交流的目的- `int dup2(int oldfd,int newfd);`
- 复制一个现存的文件描述符。当调用dup函数时，内核在进程中创建一个新的文件描述符，此描述符是当前可用文件描述符的最小数值，这个文件描述符指向oldfd所拥有的文件表项。dup2和dup的区别就是可以用newfd参数指定新描述符的数值，如果newfd已经打开，则先将其关闭。如果newfd等于oldfd，则dup2返回newfd, 而不关闭它。
- dup2函数返回的新文件描述符同样与参数oldfd共享同一文件表项。<li>
`pid_t waitpid(pid_t pid, int * status, int options);`waitpid()会暂时停止目前进程的执行, 直到有信号来到或子进程结束. 如果在调用wait()时子进程已经结束, 则wait()会立即返回子进程结束状态值. 子进程的结束状态值会由参数status返回, 而子进程的进程识别码也会一块返回. 如果不在意结束状态值, 则参数status可以设成NULL. 参数pid为欲等待的子进程识别码。</li>
- 返回值：如果执行成功则返回子进程识别码(PID), 如果有错误发生则返回-1. 失败原因存于errno中.<li>
`void *mmap(void *addr, size_t length, int prot, int flags, int fd, off_t offset)`<br>
该函数主要用途有三个：</li>
- 将普通文件映射到内存中，通常在需要对文件进行频繁读写时使用，用内存读写取代I/O读写，以获得较高的性能；
<li>addr
<ul>
- 指向欲映射的内存起始地址，通常设为NULL，代表让系统自动选定地址，映射成功后返回该地址。- 代表将文件中多大的部分映射到内存。- PROT_EXEC 映射区域可被执行
- PROT_READ 映射区域可被读取
- PROT_WRITE 映射区域可被写入
- PROT_NONE 映射区域不能存取<li>
`int sprintf(char *string, char *format [,argument,...]);`
<ul>
- 把格式化的数据写入某个字符串中，即发送格式化输出到string所指向的字符串<li>
`off_t lseek(int fildes, off_t offset, int whence);`每一个已打开的文件都有一个读写位置, 当打开文件时通常其读写位置是指向文件开头, 若是以附加的方式打开文件(如O_APPEND), 则读写位置会指向文件尾. 当read()或write()时, 读写位置会随之增加,lseek()便是用来控制该文件的读写位置. 参数fildes 为已打开的文件描述词, 参数offset 为根据参数whence来移动读写位置的位移数.</li>
<li>参数 whence 为下列其中一种:
<ul>
- SEEK_SET 参数offset 即为新的读写位置.
- SEEK_CUR 以目前的读写位置往后增加offset 个位移量.
- SEEK_END 将读写位置指向文件尾后再增加offset 个位移量. 当whence 值为SEEK_CUR 或
- SEEK_END 时, 参数offet 允许负值的出现.
readdir()返回参数dir 目录流的下个目录进入点

```
#include &lt;sys/types.h&gt;
#include &lt;dirent.h&gt;
#include &lt;unistd.h&gt;
main()
`{`
  DIR * dir;
  struct dirent * ptr;
  int i;
  dir = opendir("/etc/rc.d");
  while((ptr = readdir(dir)) != NULL)
  `{`
      printf("d_name : %s\n", ptr-&gt;d_name);
  `}`
  closedir(dir);
`}`
执行：
d_name : .
d_name : ..
d_name : init.d
d_name : rc0.d
d_name : rc1.d
d_name : rc2.d
d_name : rc3.d
d_name : rc4.d
d_name : rc5.d
d_name : rc6.d
d_name : rc
d_name : rc.local
d_name : rc.sysinit
```



## 参考资料

[https://forcemz.net/cxx/2019/04/29/StringFormattingTalk/](https://forcemz.net/cxx/2019/04/29/StringFormattingTalk/)<br>[http://rk700.github.io/2017/12/28/afl-internals/](http://rk700.github.io/2017/12/28/afl-internals/)<br>[http://rk700.github.io/2018/01/04/afl-mutations/](http://rk700.github.io/2018/01/04/afl-mutations/)

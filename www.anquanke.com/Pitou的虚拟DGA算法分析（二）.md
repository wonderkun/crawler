> 原文链接: https://www.anquanke.com//post/id/184740 


# Pitou的虚拟DGA算法分析（二）


                                阅读量   
                                **385969**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者johannesbader，文章来源：johannesbader.ch
                                <br>原文地址：[https://www.johannesbader.ch/2019/07/the-dga-of-pitou/#comparison-with-public-reports](https://www.johannesbader.ch/2019/07/the-dga-of-pitou/#comparison-with-public-reports)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t011be12d628c186e8a.jpg)](https://p0.ssl.qhimg.com/t011be12d628c186e8a.jpg)



## DGA算法

本节使用之前分析中的输出对DGA进行逆向，具体可以参照Pitou的虚拟DGA算法分析（一）。完成逆向后，利用Python对DGA进行重新实现。该脚本可以针对任何给定日期生成对应的DGA域名。

### <a name="header-n4"></a>DGA调用器

要理解DGA，必须首先查看调用VM的本地代码：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01205fbb2f370e9e36.png)

在上图的顶部，可以看到虚拟DGA的调用和在调用过程中传递的五个参数：
- r8d：当前天(day)，如2代表本月的第二天；
- edx：当前月份（month），如三月为3；
- ecx：当前年份（year），如2019；
- rsi：域名编号，从0开始；
- r9：保存生成域名的内存地址。
在截图的第一行中，域名数量rsi设置为r12d，而r12d为0。直到rsi达到20，该循环恰好生成20个域名。

### <a name="header-n20"></a>IDA Pro图形化

方法2中的动态二进制转换生成的汇编程序行数比虚拟指令数少80%。然而，DGA仍然很长，如下面的两张图片所示。它们显示了DGA，以及其调用的一个函数，该函数得到基于日期的种子。

### <a name="header-n22"></a>DGA主方法

DGA算法：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c2fdd759b9628ce6.png)

### <a name="header-n25"></a>DGA种子

基于日期的种子：

[![](https://p3.ssl.qhimg.com/t012bc47dfe0283105c.png)](https://p3.ssl.qhimg.com/t012bc47dfe0283105c.png)

通过IDA的反汇编图可以很容易地分析该DGA，因为它展示了函数的结构和控制流程。然而，这种情况下，IDA在的真正优势是Hex Rays反编译器。像前面讲到的，DGA使用了许多优化的整数除法，即所谓的不变整数除法。这些计算在反汇编中是很麻烦的，但是利用Hex Ray的反编译插件可以很好的处理。

### <a name="header-n29"></a>IDA Pro Hex Rays

本次DGA的逆向是完全基于Hex Ray反编译器的。

首先分析DGA调用的日期种子函数。它接收到参数的基于下面的设定：
- r8d：从1开始，所以每月的第一天为1；
- edx：从0开始，所以一月为0，十二月为11；
- ecx：四位数的年份。
月份从0开始的设定是错误的。真实的月份应该是从1开始的，所以一月应该为1。本节的第一部分在参数正确的设定上分析这个函数。而第二部分探究月份中不正确的值对本方法的影响。

首先看一下Hex Rays完整输出，其中隐藏了转换和声明：

```
signed __int64 __usercall days_since_epoch@&lt;rax&gt;(int month@&lt;edx&gt;, int year@&lt;ecx&gt;, int day@&lt;r8d&gt;)
`{`
  // [COLLAPSED LOCAL DECLARATIONS. PRESS KEYPAD CTRL-"+" TO EXPAND]

  retaddr = v4;
  month_o = month;
  extra_years = month / 12;
  year_f = extra_years + year;
  month_fixed = (-12 * extra_years + month_o);
  if ( month_fixed &lt; 0 )
  `{`
    month_fixed = (month_fixed + 12);
    --year_f;
  `}`
  month_fixed_2 = month_fixed;
  day_0_based = (day - 1);
  if ( day - 1 &lt; 0 )
  `{`
    year_plus_1900 = year_f + 1900;
    do
    `{`
      month_fixed = (month_fixed - 1);
      if ( --month_fixed_2 &lt; 0 )
      `{`
        month_fixed = 11LL;
        --year_f;
        --year_plus_1900;
        month_fixed_2 = 11LL;
      `}`
      is_leap_year = !(year_plus_1900 % 4)
                  &amp;&amp; (year_plus_1900 != 100 * (year_plus_1900 / 100) || year_plus_1900 == 400 * (year_plus_1900 / 400));
      *(&amp;stack_ - 125) = a5;
      a5 = *(&amp;stack_ - 125);
      day_0_based = (month_lengths_common_year[month_fixed_2 + 12 * is_leap_year] + day_0_based);
    `}`
    while ( day_0_based &lt; 0 );
  `}`
  month_f = month_fixed;
  year_f_plus_1900 = year_f + 1900;
  while ( 1 )
  `{`
    year_div4_ = year_f_plus_1900 % 4;
    leap_year = year_div4_
             || year_f_plus_1900 == 100 * (year_f_plus_1900 / 100) &amp;&amp; year_f_plus_1900 != 400 * (year_f_plus_1900 / 400) ? 0LL : 1LL;
    *(&amp;stack_ - 125) = a5;
    tmp = *(&amp;stack_ - 125);
    if ( day_0_based &lt; month_lengths_common_year[month_f + 12 * leap_year] )
      break;
    leap_year_ = !year_div4_
              &amp;&amp; (year_f_plus_1900 != 100 * (year_f_plus_1900 / 100)
               || year_f_plus_1900 == 400 * (year_f_plus_1900 / 400));
    *(&amp;stack_ - 125) = tmp;
    a5 = *(&amp;stack_ - 125);
    index = month_f++ + 12 * leap_year_;
    day_0_based = (day_0_based - month_lengths_common_year[index]);
    if ( month_f == 12 )
    `{`
      month_f = 0LL;
      ++year_f;
      ++year_f_plus_1900;
    `}`
  `}`
  years_since_epoch = year_f - 1970;
  day_1_based = day_0_based + 1;
  year_mod4 = year_f % 4;
  year_mod4_is_1 = year_mod4 &amp;&amp; year_mod4 &lt; 2;
  days_beg_year_with_rule_div4 = year_mod4_is_1 + years_since_epoch / 4 + 365 * (year_f - 1970);
  year_mod100 = year_f % 100;
  c1 = year_f % 100 &amp;&amp; year_mod100 &lt; 70;
  days_beg_year_rule_div100 = -c1 - years_since_epoch / 100 + days_beg_year_with_rule_div4;
  year_mod400 = year_f % 400;
  c2 = year_mod400 &amp;&amp; year_mod400 &lt; 370;
  c3 = (1374389535LL * years_since_epoch) &gt;&gt; 32;
  days_in_months = 0LL;
  days_beg_year_with_rule_div400 = c2 + (c3 &gt;&gt; 31) + (c3 &gt;&gt; 7) + days_beg_year_rule_div100;
  for ( i = 0LL; i &lt; month_f; days_in_months = (month_lengths_common_year[i_] + days_in_months) )
  `{`
    is_leap_year_1 = !year_mod4 &amp;&amp; (year_mod100 || !year_mod400);
    *(&amp;stack_ - 125) = tmp;
    tmp = *(&amp;stack_ - 125);
    i_ = i++ + 12 * is_leap_year_1;
  `}`
  *(&amp;stack_ - 125) = tmp;
  return days_in_months + days_beg_year_with_rule_div400 + day_1_based - 1;
```

<a name="header-n42"></a>**参数正确的情况**

如果日期是在预期范围内（实际上并没有在预期范围内，我们假设在），然后忽略开始的计算部分，即整个if代码块（if(day -1 &lt; 0)）。因为break语句总是触发，所以while(1)代码块没有影响。

代码中包含*(&amp;stack_ – 125)的行是临时堆栈变量[rsp-1000]的残留，二进制翻译时有时会修改这个变量，具体情况参阅二进制翻译部分。所有带有*(&amp;stack_ – 125)的行都可以删除。所以可以简化代码：

```
signed __int64 __usercall days_since_epoch@&lt;rax&gt;(int month@&lt;edx&gt;, int year@&lt;ecx&gt;, int day@&lt;r8d&gt;)
`{`
  year_f = year;
  day_0_based = (day - 1);
  month_f = month;
  year_f_plus_1900 = year_f + 1900;
  years_since_epoch = year_f - 1970;
  day_1_based = day_0_based + 1;
  year_mod4 = year_f % 4;
  year_mod4_is_1 = year_mod4 &amp;&amp; year_mod4 &lt; 2;
  days_beg_year_with_rule_div4 = year_mod4_is_1 + years_since_epoch / 4 + 365 * (year_f - 1970);
  year_mod100 = year_f % 100;
  c1 = year_f % 100 &amp;&amp; year_mod100 &lt; 70;
  days_beg_year_rule_div100 = -c1 - years_since_epoch / 100 + days_beg_year_with_rule_div4;
  year_mod400 = year_f % 400;
  c2 = year_mod400 &amp;&amp; year_mod400 &lt; 370;
  c3 = (1374389535LL * years_since_epoch) &gt;&gt; 32;
  days_in_months = 0LL;
  days_beg_year_with_rule_div400 = c2 + (c3 &gt;&gt; 31) + (c3 &gt;&gt; 7) + days_beg_year_rule_div100;
  for ( i = 0LL; i &lt; month_f; days_in_months = (month_lengths_common_year[i_] + days_in_months) )
  `{`
    is_leap_year_1 = !year_mod4 &amp;&amp; (year_mod100 || !year_mod400);
    i_ = i++ + 12 * is_leap_year_1;
  `}`
  return days_in_months + days_beg_year_with_rule_div400 + day_1_based - 1;
```

该代码计算自纪元以来的天数，即， 从1970年1月1日开始到现在的天数。它首先确定从1970年开始的过去了多少年。

```
year_f = year;
day_0_based = (day - 1);
month_f = month;
year_f_plus_1900 = year_f + 1900;
years_since_epoch = year_f - 1970;
```

然后，代码通过考虑每年是否是闰年来确定从纪元以来到提供的年份的天数。例如，如果函数被调用的日期是2017年11月2日，那么它将计算从纪元开始到2017年1月1日的天数。

```
day_1_based = day_0_based + 1;
year_mod4 = year_f % 4;
year_mod4_is_1 = year_mod4 &amp;&amp; year_mod4 &lt; 2;
days_beg_year_with_rule_div4 = year_mod4_is_1 + years_since_epoch / 4 + 365 * (year_f - 1970);
```

下面的代码纠正了一个事实：年份能被100整除的年份不是闰年。

```
year_mod100 = year_f % 100;
  c1 = year_f % 100 &amp;&amp; year_mod100 &lt; 70;
  days_beg_year_rule_div100 = -c1 - years_since_epoch / 100 + days_beg_year_with_rule_div4;
```

下面的代码解释了年份能被400整除是闰年的规则：

```
year_mod400 = year_f % 400;
c2 = year_mod400 &amp;&amp; year_mod400 &lt; 370;
c3 = (1374389535LL * years_since_epoch) &gt;&gt; 32;
days_in_months = 0LL;
days_beg_year_with_rule_div400 = c2 + (c3 &gt;&gt; 31) + (c3 &gt;&gt; 7) + days_beg_year_rule_div100;
```

现在代码正确地确定了给定日期到年初的天数。最后，它使用一个循环来累计每个月过去的天数：

```
for ( i = 0LL; i &lt; month_f; days_in_months = (month_lengths_common_year[i_] + days_in_months) )
  `{`
    is_leap_year_1 = !year_mod4 &amp;&amp; (year_mod100 || !year_mod400);
    i_ = i++ + 12 * is_leap_year_1;
  `}`
```

month_length_common_year列出了平年中的每月天数，紧接其后的是闰年中的每月的天数。如果需要，术语12 * is_leap_year_1将切换到闰年的月份数组。

最后，代码将纪元到年初的天数、今年过去月份的天数（本年的第几个月）和当前的天数（本月的第几天）相加，减去1得到纪元以来的天数：

```
return days_in_months + days_beg_year_with_rule_div400 + day_1_based - 1;
```

### <a name="header-n59"></a>实际参数的影响

当月份是从零开始时，上面的代码可以顺利的执行。然而，在获取日期时是通过函数RtlTimeToTimeFields，详情见DGA调用器。该函数返回从1到12的月份。在这些日期中执行计算天数的函数会发生什么呢？

情形1：既不是十二月，也不是月底。不是12月也不是28号后的日期会将实际日期变成下个月对应的日期。如：
<td valign="bottom">实际日期</td><td valign="bottom">更改为</td><td valign="bottom">结果</td>
<td valign="top">28.3.2019</td><td valign="top">28.4.2019</td><td valign="top">0x465E</td>
<td valign="top">1.9.2017</td><td valign="top">1.10.2017</td><td valign="top">0x4420</td>
<td valign="top">1.1.2014</td><td valign="top">1.2.2014</td><td valign="top">0x30A1</td>
<td valign="top">30.11.2019</td><td valign="top">30.12.2019</td><td valign="top">0x4754</td>

情形2：在月底但不是十二月。如果下个月的对应日期不存在，那么将日期移到下个月将会导致问题。例如，3月31日将会转移到4月31日，这是不存在的。在这种情况下，我们之前跳过的while(1)循环将会生效：

```
while ( 1 )
  `{`
    year_div4_ = year_f_plus_1900 % 4;
    leap_year = year_div4_
             || year_f_plus_1900 == 100 * (year_f_plus_1900 / 100) &amp;&amp; year_f_plus_1900 != 400 * (year_f_plus_1900 / 400) ? 0LL : 1LL;
    if ( day_0_based &lt; month_lengths_common_year[month_f + 12 * leap_year] )
      break;
    leap_year_ = !year_div4_
              &amp;&amp; (year_f_plus_1900 != 100 * (year_f_plus_1900 / 100)
               || year_f_plus_1900 == 400 * (year_f_plus_1900 / 400));
    index = month_f++ + 12 * leap_year_;
    day_0_based = (day_0_based - month_lengths_common_year[index]);
    if ( month_f == 12 )
    `{`
      month_f = 0LL;
      ++year_f;
      ++year_f_plus_1900;
    `}`
  `}`
```

进行测试：

```
day_0_based &lt; month_lengths_common_year[month_f + 12 * leap_year]
```

这会检查日期是否存在于当前月份。如果不存在，则日期将适当地溢出到下一个月。代码甚至可以将日期在几个月之间进行修改，如，4月91日到6月30日。闰年也可以正确处理，见下表最后一行：
<td valign="bottom">实际日期</td><td valign="bottom">更改为</td><td valign="bottom">结果</td>
<td valign="top">31.3.2019</td><td valign="top">1.5.2019</td><td valign="top">0x4661</td>
<td valign="top">30.11.2019</td><td valign="top">30.12.2019</td><td valign="top">0x4754</td>
<td valign="top">31.1.2019</td><td valign="top">3.3.2019</td><td valign="top">0x4626</td>
<td valign="top">31.1.2020</td><td valign="top">2.3.2020</td><td valign="top">0x4793</td>

情形3：十二月。对于12月的日期，函数开始的处理是重要的:

```
month_o = month;
  extra_years = month / 12;
  year_f = extra_years + year;
  month_fixed = (-12 * extra_years + month_o);
  if ( month_fixed &lt; 0 )
  `{`
    month_fixed = (month_fixed + 12);
    --year_f;
  `}`
```

变量extra_years是1，它以一年为单位递增。月份值减少12 (-12 * extra_years + month_o)，即变成0则代表1月。因此,我们得到：
<td valign="bottom">实际日期</td><td valign="bottom">更改为</td><td valign="bottom">结果</td>
<td valign="top">6.12.2019</td><td valign="top">6.1.2020</td><td valign="top">0x475B</td>

### <a name="header-n121"></a>DGA函数

DGA如下所示。同样，虽然只有几行是多余的，但其输出也非常长。之后分别对算法的组成部分进行分析。

```
__int64 __usercall dga@&lt;rax&gt;(__int64 months@&lt;rdx&gt;, __int64 year@&lt;rcx&gt;, __int64 domaint_output@&lt;r9&gt;, int days@&lt;r8d&gt;, int domain_nr)
`{`
  domain_out = domain_output;
  vars30 = &amp;vars38;
  vars28 = a4;
  vars20 = a3;
  vars18 = a6;
  vars10 = a7;
  vars8 = a8;
  j = 0LL;
  domain = a5;
  v20 = year;
  random_numbers = 0;
  magic_number = 0xDAFE02C;
  days_since_1970_broken = days_since_epoch(months, year, days);
  consonants = *pConsonants;
  LOBYTE(v20) = v20 - 108;
  retaddr = v20;
  i = 0;
  v25 = &amp;v72;
  seed_value = domain_nr / 3 + days_since_1970_broken;
  if ( !*pConsonants )
  `{`
    consonants = (ExAllocatePool)(&amp;v72, domain, 23LL, 0LL);
    *pConsonants = consonants;
    if ( decrypt_consonants )
    `{`
      key = 0x3365841C;
      key_index = 0LL;
      addr_encrypted_consonants = &amp;encrypted_consonants;
      do
      `{`
        key_index_1 = key_index;
        ++consonants;
        ++addr_encrypted_consonants;
        key_byte = *(&amp;key + key_index);
        *(consonants - 1) = *(addr_encrypted_consonants - 1) ^ *(&amp;key + key_index);
        key_index = (key_index + 1) &amp; 0x80000003;
        *(&amp;key + key_index_1) = 2 * key_byte ^ (key_byte &gt;&gt; 1);
        if ( key_index &lt; 0 )
          key_index = ((key_index - 1) ^ 0xFFFFFFFC) + 1;
      `}`
      while ( addr_encrypted_consonants &lt; &amp;encrypted_consonants_end );
      consonants = *pConsonants;
    `}`
  `}`
  vowels = *pVowels;
  if ( !*pVowels )
  `{`
    vowels = (ExAllocatePool)(&amp;v72, domain, *pVowels + 7LL, 0LL);
    *pVowels = vowels;
    if ( decrypt_vowels )
    `{`
      key = -967459448;
      key_index_2 = 0LL;
      addr_encrypted_vowels = &amp;encrypted_vowels;
      do
      `{`
        key_index_3 = key_index_2;
        ++vowels;
        ++addr_encrypted_vowels;
        key_byte_1 = *(&amp;key + key_index_2);
        *(vowels - 1) = *(addr_encrypted_vowels - 1) ^ *(&amp;key + key_index_2);
        key_index_2 = (key_index_2 + 1) &amp; 0x80000003;
        *(&amp;key + key_index_3) = 2 * key_byte_1 ^ (key_byte_1 &gt;&gt; 1);
        if ( key_index_2 &lt; 0 )
          key_index_2 = ((key_index_2 - 1) ^ 0xFFFFFFFC) + 1;
      `}`
      while ( addr_encrypted_vowels &lt; &amp;encrypted_vowels_end );
      vowels = *pVowels;
    `}`
  `}`
  tlds = pTLDs;
  if ( !pTLDs )
  `{`
    tlds = (ExAllocatePool)(&amp;v72, domain, pTLDs + 38, 0LL);
    pTLDs = tlds;
    if ( decrypt_tlds )
    `{`
      key = 2131189013;
      key_index_4 = 0LL;
      addr_encrypted_tlds = &amp;encrypted_tlds;
      do
      `{`
        v44 = key_index_4;
        ++tlds;
        ++addr_encrypted_tlds;
        key_byte_2 = *(&amp;key + key_index_4);
        *(tlds - 1) = *(addr_encrypted_tlds - 1) ^ *(&amp;key + key_index_4);
        key_index_4 = (key_index_4 + 1) &amp; 0x80000003;
        *(&amp;key + v44) = 2 * key_byte_2 ^ (key_byte_2 &gt;&gt; 1);
        if ( key_index_4 &lt; 0 )
          key_index_4 = ((key_index_4 - 1) ^ 0xFFFFFFFC) + 1;
      `}`
      while ( addr_encrypted_tlds &lt; &amp;encrypted_tlds_end );
      tlds = pTLDs;
    `}`
  `}`
  tlds_1 = tlds;
  v30 = &amp;v72 - tlds;
  do
  `{`
    v67 = *tlds_1;
    tlds_1 = (tlds_1 + 1);
    *(tlds_1 + v30 - 1) = v67;
  `}`
  while ( v67 );
  if ( tlds )
  `{`
    (ExFreePool)(&amp;v72, domain, v30, tlds);
    pTLDs = 0LL;
  `}`
  v17 = 1LL;
  v73 = &amp;v72;
  if ( v72 )
  `{`
    do
    `{`
      if ( *v25 == 44 )
      `{`
        *v25 = 0;
        *&amp;tld_array[8 * v17 - 49] = v25 + 1;
        v17 = (v17 + 1);
      `}`
      v25 = (v25 + 1);
    `}`
    while ( *v25 );
  `}`
  counter_ = domain_nr;
  round_seed_to_nearset_10 = 10 * (seed_value / 0xA);
  seed_value = round_seed_to_nearset_10;
  HIWORD(v39) = HIWORD(round_seed_to_nearset_10);
  LOWORD(v39) = ((0xDAFE02Cu &gt;&gt; domain_nr) * (domain_nr - 1)) * round_seed_to_nearset_10;
  LOBYTE(v39) = (v39 &amp; 1) + 8;
  domain_length = v39;
  if ( v39 &gt; 0 )
  `{`
    v41 = BYTE1(seed_value);
    addr_random_numbers = &amp;the_random_numbers;
    do
    `{`
      ip1 = i++;
      v50 = (ip1 &gt;&gt; 31) &amp; 3;
      v51 = v50 + ip1;
      v52 = (v51 &gt;&gt; 2);
      v53 = (v51 &amp; 3) - v50;
      if ( v53 )
      `{`
        v54 = v53 - 1;
        if ( v54 )
        `{`
          v55 = v54 - 1;
          if ( v55 )
          `{`
            if ( v55 == 1 )
            `{`
              ++random_numbers;
              v56 = (round_seed_to_nearset_10 &lt;&lt; v52) ^ (v41 &gt;&gt; v52);
              v57 = v52;
              counter_ = domain_nr;
              addr_random_numbers = (addr_random_numbers + 1);
              *(addr_random_numbers - 1) = v56 * (*(&amp;magic_number + v57) &amp; 0xF) * (domain_nr + 1);
            `}`
            else
            `{`
              counter_ = domain_nr;
            `}`
          `}`
          else
          `{`
            ++random_numbers;
            v15 = (v41 &lt;&lt; v52) ^ (round_seed_to_nearset_10 &gt;&gt; v52);
            v16 = v52;
            counter_ = domain_nr;
            addr_random_numbers = (addr_random_numbers + 1);
            *(addr_random_numbers - 1) = v15 * (*(&amp;magic_number + v16) &gt;&gt; 4) * (domain_nr + 1);
          `}`
        `}`
        else
        `{`
          v31 = v52;
          v32 = v52;
          counter_ = domain_nr;
          ++random_numbers;
          addr_random_numbers = (addr_random_numbers + 1);
          *(addr_random_numbers - 1) = (*(&amp;magic_number + v31) &amp; 0xF) * (retaddr &lt;&lt; v32) * (domain_nr + 1);
        `}`
      `}`
      else
      `{`
        v63 = v52;
        v64 = v52;
        counter_ = domain_nr;
        ++random_numbers;
        addr_random_numbers = (addr_random_numbers + 1);
        *(addr_random_numbers - 1) = (*(&amp;magic_number + v63) &gt;&gt; 4) * (retaddr &gt;&gt; v64) * (domain_nr + 1);
      `}`
    `}`
    while ( random_numbers &lt; domain_length );
    domain = domain_out;
    if ( domain_length &gt; 0 )
    `{`
      while ( 1 )
      `{`
        v34 = j;
        j = (j + 1);
        v35 = *(&amp;the_random_numbers + v34);
        if ( (v35 &amp; 0x80u) == 0 )
          break;
        *(++domain - 1) = *(consonants + (v35 % 21));
        if ( j &gt;= domain_length )
          goto append_tld;
        v36 = j;
        j = (j + 1);
        *(++domain - 1) = *(vowels + (*(&amp;the_random_numbers + v36) % 5));
        if ( j &gt;= domain_length )
          goto append_tld;
        r = *(&amp;the_random_numbers + j);
        LOBYTE(r) = r &amp; 64;
        if ( r )
        `{`
          *(++domain - 1) = *(vowels + (r % 5));
_addr_FFFFF880058745FC:
          j = (j + 1);
        `}`
        if ( j &gt;= domain_length )
          goto append_tld;
      `}`
      *domain = *(vowels + (v35 % 5));
      domain += 2;
      *(domain - 1) = *(consonants + (*(&amp;the_random_numbers + j) % 21));
      goto _addr_FFFFF880058745FC;
    `}`
  `}`
append_tld:
  *domain = '.';
  tld = *&amp;tld_array[8 * ((counter_ ^ round_seed_to_nearset_10 ^ 0xDAFE02C) % 9) - 49];
  dmtld = domain - tld;
  do
  `{`
    result = *tld;
    tld = (tld + 1);
    *(tld + dmtld) = result;
  `}`
  while ( result );
  return result;
`}`
```

<a name="header-n124"></a>**种子**

种子的主要部分在函数days_since_epoch中。种子值与域名计数器相结合，并且存在一个为10天的间隔：

```
days_since_1970_broken = days_since_epoch(months, year, days);
  ...
  seed_value = domain_nr / 3 + days_since_1970_broken;
  ...
  round_seed_to_nearset_10 = 10 * (seed_value / 10);
  seed_value = round_seed_to_nearset_10;
```

大多数情况下，种子会保持10天不变。从纪元开始到目前的天数计算错误并不重要，这个值只用于播种，并且每天都会更换。这种情况几乎适用于所有的日子，除了少数边缘情况，这时，两天会有相同的种子（例如2019年1月29日和2019年2月1日返回相同的值）。错误的计算还可以缩短或延长10天的窗口。最长的窗口是13天，1月底的时候会发生，例如：2019-01-23到2019-02-04。2月底的窗口最短，之有7天的窗口：2019-02-25到2019-03-03。在极少数情况下，窗口仅为1天，下一次将在2025年01月31日发生。

种子也使用一个魔法数字：

```
magic_number = 0xDAFE02C;
```

根据F-Secure，这意味着Pitou版本为33。它们将0xDAFE02D作为版本31的第二个种子。

<a name="header-n131"></a>**加密的字符串**

DGA使用三个加密的字符串： 元音、辅音和顶级域。DGA在运行时首先对这些字符串进行解密。加密是用一个四个字节密钥的滚动异或，每次循环根据key = (key&lt;&lt;1) ^ (key &gt;&gt;1)进行更新：

```
if ( !*pConsonants )
  `{`
    consonants = (ExAllocatePool)(&amp;v72, domain, 23LL, 0LL);
    *pConsonants = consonants;
    if ( decrypt_consonants )
    `{`
      key = 0x3365841C;
      key_index = 0LL;
      addr_encrypted_consonants = &amp;encrypted_consonants;
      do
      `{`
        key_index_1 = key_index;
        ++consonants;
        ++addr_encrypted_consonants;
        key_byte = *(&amp;key + key_index);
        *(consonants - 1) = *(addr_encrypted_consonants - 1) ^ *(&amp;key + key_index);
        key_index = (key_index + 1) &amp; 0x80000003;
        *(&amp;key + key_index_1) = 2 * key_byte ^ (key_byte &gt;&gt; 1);
        if ( key_index &lt; 0 )
          key_index = ((key_index - 1) ^ 0xFFFFFFFC) + 1;
      `}`
      while ( addr_encrypted_consonants &lt; &amp;encrypted_consonants_end );
      consonants = *pConsonants;
    `}`
  `}`
```

<a name="header-n134"></a>**二级域名长度**

二级域的长度计算如下：

```
counter_ = domain_nr;
  round_seed_to_nearset_10 = 10 * (seed_value / 0xA);
  seed_value = round_seed_to_nearset_10;
  HIWORD(v39) = HIWORD(round_seed_to_nearset_10);
  LOWORD(v39) = ((0xDAFE02Cu &gt;&gt; domain_nr) * (domain_nr - 1)) * round_seed_to_nearset_10;
  LOBYTE(v39) = (v39 &amp; 1) + 8;
  domain_length = v39;
```

这将导致二级域的长度为8到9。

<a name="header-n138"></a>**随机数**

种子被转换成随机数。种子被视为一个16位的值，它被分成4个4位的值。然后使用这些值生成组成域名的字母。由于种子中更重要的位变化较慢，所以域名中位于3、4和7、8位置的字母变化的更加频繁。例如，这些是2019年6月1日、6月10日和6月20日的域名：

```
zuoezaxa�.name
zuopabma.org
zuojabba.mobi
```

为什么字符�会出现在域名zuoezaxa�.name中呢？Pitou有一个严重的问题。即使选择二级域的长度为9个字符，但其只能计算8个随机数。所以第9个字符是从未定义的内存中读取的。这意味着二级域的最后一个字符是不确定的。只有长度为8 的二级域的域名是有效的。

<a name="header-n142"></a>**所使用字母**

两个数组提供组成二级域的字母：元音数组（aeiou）和辅音数组（bcdfghjklmnpqrstvwxyz）。这使得组成的域名看起来更自然。

<a name="header-n144"></a>**使用的顶级域**

顶级域也是从一组硬编码列表中选择：com, org, biz, net, info, mobi, us, name, me。

<a name="header-n146"></a>**Python重新实现**

这个DGA非常混乱，即使使用Python重新实现也很难读懂。

```
import argparse
from datetime import date, datetime, timedelta
from calendar import monthrange

def date2seed(d):
    year_prime = d.year
    month_prime = (d.month + 1) 
    day_prime = d.day

    if month_prime &gt; 12:
        month_prime -= 12
        year_prime += 1

    _, monthdays = monthrange(year_prime, month_prime) 
    if day_prime &gt; monthdays:
        month_prime += 1
        day_prime -= monthdays

    if month_prime &gt; 12:
        month_prime -= 12
        year_prime += 1

    date_prime = date(year_prime, month_prime, day_prime)
    epoch = datetime.strptime("1970-01-01", "%Y-%m-%d").date()
    return (date_prime - epoch).days

def dga(year, seed, counter, magic):
    seed_value = 10*( (counter//3 + seed) // 10)
    year_since = year - 1900
    random_numbers = []

    a = (magic &gt;&gt; counter) 
    b = (counter - 1) &amp; 0xFF
    d = a*b &amp; 0xFF
    e = d*seed_value 
    sld_length = 8 + (e &amp; 1)

    magic_list = []
    for i in range(4):
        magic_list.append((magic &gt;&gt; (i*8)) &amp; 0xFF)
    for i in range(8):
        imod = i % 4
        idiv = i // 4
        b1 = (seed_value &gt;&gt; 8) &amp; 0xFF
        b0 = seed_value &amp; 0xFF
        if imod == 0:
            m = magic_list[idiv] &gt;&gt; 4
            f = (year_since &gt;&gt; idiv)
        elif imod == 1:
            m = magic_list[idiv] &amp; 0xF 
            f = (year_since &lt;&lt; idiv)
        elif imod == 2:
            m = magic_list[idiv] &gt;&gt; 4
            f = (b1 &lt;&lt;  idiv) ^ (b0 &gt;&gt; idiv)
        elif imod == 3:
            m = magic_list[idiv] &amp; 0xF
            f = (b0 &lt;&lt;  idiv) ^ (b1 &gt;&gt; idiv)
        cp = (counter + 1)
        r = (m*f &amp; 0xFF) *cp
        random_numbers.append(r &amp; 0xFF)
    random_numbers.append(0xE0)
    r = random_numbers

    vowels = "aeiou"
    consonants = "bcdfghjklmnpqrstvwxyz"
    sld = ""

    while True:
        x = r.pop(0)
        if x &amp; 0x80:
            sld += consonants[x % len(consonants)]
            if len(sld) &gt;= sld_length:
                break
            x = r.pop(0)
            sld += vowels[x % len(vowels)]
            if len(sld) &gt;= sld_length:
                break

            x = r[0]
            if x &amp; 0x40:
                r.pop(0)
                sld += vowels[x % len(vowels)]
                if len(sld) &gt;= sld_length:
                    break
        else:
            sld += vowels[x % len(vowels)]
            x = r.pop(0)
            sld += consonants[x % len(consonants)]
            if len(sld) &gt;= sld_length:
                break

    tlds = ['com', 'org', 'biz', 'net', 'info', 'mobi', 'us', 'name', 'me']
   
        
    q = (counter ^ seed_value ^ magic)  &amp; 0xFFFFFFFF
    tld = tlds[q % len(tlds)]

    if len(sld) &gt; 8:
        lc = sld[-1]
        sld = sld[:-1]
        if lc in consonants:
            sld_c = [sld + c for c in consonants]
        else:
            sld_c = [sld + c for c in vowels]
        return [s + "." + tld for s in sld_c]
    else:
        return sld + "." + tld

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="DGA of Pitou")
    parser.add_argument("-d", "--date", 
        help="date for which to generate domains, e.g., 2019-04-09")

    parser.add_argument("-m", "--magic", choices=["0xDAFE02D", "0xDAFE02C"],
            default="0xDAFE02C", help="magic seed")
    args = parser.parse_args()

    if args.date:
        d = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        d = datetime.now()

    for c in range(20):
        seed = date2seed(d)
        domains = dga(d.year, seed, c, int(args.magic, 16))
        if type(domains) == str:
            print(domains)
        else:
            l = len(domains[0]) + 1
            print(l*"-" + "+")
            for i, domain in enumerate(domains):
                if i == len(domains)//2:
                    label = "one of these"
                    print("`{``}` +--`{``}`".format(domain, label))
                else:
                    print("`{``}` |".format(domain))
            print(l*"-" + "+")
```

对于所有二级域长度为9的域名，代码打印所有可能的域名(参见随机数中的bug)：

```
▶ python3 dga.py -d 2019-06-10
-------------+
koupoalab.me |
koupoalac.me |
koupoalad.me |
koupoalaf.me |
koupoalag.me |
koupoalah.me |
koupoalaj.me |
koupoalak.me |
koupoalal.me |
koupoalam.me |
koupoalan.me +--one of these
koupoalap.me |
koupoalaq.me |
koupoalar.me |
koupoalas.me |
koupoalat.me |
koupoalav.me |
koupoalaw.me |
koupoalax.me |
koupoalay.me |
koupoalaz.me |
-------------+
```

<a name="header-n151"></a>**特性**

下表总结了Pitou的DGA的特性。
<td valign="bottom">属性</td><td valign="bottom">值</td>
<td valign="top">类型</td><td valign="top">依赖时间的确定性的（TDD ，time-dependent-deterministic），一定程度上可以扩展为依赖时间的不确定性的（ TDN ，time-dependent non-deterministic）</td>
<td valign="top">生成模式</td><td valign="top">移位的种子</td>
<td valign="top">种子</td><td valign="top">魔法数字加当前日期</td>
<td valign="top">域名变化频率</td><td valign="top">大部分是每10天更新一次，最少1天更新，最多13天更新</td>
<td valign="top">每天域名数</td><td valign="top">20</td>
<td valign="top">序列</td><td valign="top">连续的</td>
<td valign="top">域名间的等待时间</td><td valign="top">无</td>
<td valign="top">顶级域</td><td valign="top">com, org, biz, net, info, mobi, us, name, me</td>
<td valign="top">二级域字符</td><td valign="top">a-z</td>
<td valign="top">二级域长度</td><td valign="top">8或 9</td>

<a name="header-n187"></a>**与公开报告比较**

对于列出的之前工作中的所有报告，我检查了所有提及的域名都已经包含在本文中所提出的DGA中。你可以在这里找到2015 – 2021年之间[0xdafe02c](https://www.johannesbader.ch/2019/07/the-dga-of-pitou/2019-07-08-the-dga-of-pitou/0xdafe02c.txt)和[0xdafe02d](https://www.johannesbader.ch/2019/07/the-dga-of-pitou/2019-07-08-the-dga-of-pitou/0xdafe02d.txt)两个种子的域名列表。我对DGA的重新实现覆盖了报告中的所有域名。

Pitou -臭名昭著的Srizbi内核垃圾邮件机器人悄悄复活（Pitou – The “silent” resurrection of the notorious Srizbi kernel spambot）

[f-Secure的报告](https://www.f-secure.com/documents/996508/1030745/pitou_whitepaper.pdf)没有列出任何Pitou DGA域名。

bootkit并没有死，Pitou回归!（Bootkits are not dead. Pitou is back!）

C.R.A.M 2018年1月15日的[报告](http://www.tgsoft.it/english/news_archivio_eng.asp?id=884)，列出了四个域名：
<td valign="bottom">域名</td><td valign="bottom">种子</td><td valign="bottom">首次生成时间</td><td valign="bottom">有效时间</td>
<td valign="top">unpeoavax.mobi</td><td valign="top">0xDAFE02C</td><td valign="top">2017-10-04</td><td valign="top">2017-10-13</td>
<td valign="top">ilsuiapay.us</td><td valign="top">0xDAFE02C</td><td valign="top">2017-10-04</td><td valign="top">2017-10-13</td>
<td valign="top">ivbaibja.net</td><td valign="top">0xDAFE02C</td><td valign="top">2017-10-08</td><td valign="top">2017-10-17</td>
<td valign="top">asfoeacak.info</td><td valign="top">0xDAFE02C</td><td valign="top">2017-10-08</td><td valign="top">2017-10-17</td>

平台开发工具传播Pitou.B木马（Rig Exploit Kit sends Pitou.B Trojan）

布拉德·邓肯(Brad Duncan)于2019年6月25日发表在SANS Internet Storm Center的[文章](https://isc.sans.edu/diary/rss/25068)，引用了优秀的恶意软件流量分析博客上的一个Pitou PCAP包。[注：PACP流量数据包]
<td valign="bottom">域名</td><td valign="bottom">种子</td><td valign="bottom">首次生成时间</td><td valign="bottom">有效时间</td>
<td valign="top">rogojaob.info</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-23</td><td valign="top">2019-07-01</td>
<td valign="top">wiejlauas.info</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-18</td><td valign="top">2019-06-27</td>
<td valign="top">yoevuajas.us</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-22</td><td valign="top">2019-06-30</td>
<td valign="top">ijcaiatas.name</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-19</td><td valign="top">2019-06-28</td>
<td valign="top">piiaxasas.com</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-19</td><td valign="top">2019-06-28</td>
<td valign="top">caoelasas.name</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-22</td><td valign="top">2019-06-30</td>
<td valign="top">naaleazas.net</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-23</td><td valign="top">2019-07-01</td>
<td valign="top">epcioalas.info</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-20</td><td valign="top">2019-06-29</td>
<td valign="top">oltaeazas.mobi</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-20</td><td valign="top">2019-06-29</td>
<td valign="top">suudaacas.org</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-18</td><td valign="top">2019-06-27</td>
<td valign="top">giazfaeas.me</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-21</td><td valign="top">2019-06-30</td>
<td valign="top">zuojabba.mobi</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-18</td><td valign="top">2019-06-27</td>
<td valign="top">unufabub.net</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-21</td><td valign="top">2019-06-30</td>
<td valign="top">ufayubja.me</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-19</td><td valign="top">2019-06-28</td>
<td valign="top">huoseavas.name</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-17</td><td valign="top">2019-06-26</td>
<td valign="top">irifyara.com</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-21</td><td valign="top">2019-06-30</td>
<td valign="top">vaxeiayas.mobi</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-22</td><td valign="top">2019-06-30</td>
<td valign="top">kooovaqas.biz</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-23</td><td valign="top">2019-07-01</td>
<td valign="top">dienoalas.us</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-17</td><td valign="top">2019-06-26</td>
<td valign="top">amlivaias.us</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-20</td><td valign="top">2019-06-29</td>

Brad Duncan也对另一个Pitou样本进行了分析，写了另一篇[博客文章](https://www.malware-traffic-analysis.net/2019/06/25/index.html)，他提供了一个PCAP包，其中包含以下Pitou域名：
<td valign="bottom">域名</td><td valign="bottom">种子</td><td valign="bottom">首次生成时间</td><td valign="bottom">有效时间</td>
<td valign="top">amlivaias.us</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-20</td><td valign="top">2019-06-29</td>
<td valign="top">piiaxasas.com</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-19</td><td valign="top">2019-06-28</td>
<td valign="top">zuojabba.mobi</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-18</td><td valign="top">2019-06-27</td>
<td valign="top">vaxeiayas.mobi</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-22</td><td valign="top">2019-06-30</td>
<td valign="top">giazfaeas.me</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-21</td><td valign="top">2019-06-30</td>
<td valign="top">oltaeazas.mobi</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-20</td><td valign="top">2019-06-29</td>
<td valign="top">rogojaob.info</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-23</td><td valign="top">2019-07-01</td>
<td valign="top">irifyara.com</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-21</td><td valign="top">2019-06-30</td>
<td valign="top">ufayubja.me</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-19</td><td valign="top">2019-06-28</td>
<td valign="top">naaleazas.net</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-23</td><td valign="top">2019-07-01</td>
<td valign="top">dienoalas.us</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-17</td><td valign="top">2019-06-26</td>
<td valign="top">kooovaqas.biz</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-23</td><td valign="top">2019-07-01</td>
<td valign="top">suudaacas.org</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-18</td><td valign="top">2019-06-27</td>
<td valign="top">wiejlauas.info</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-18</td><td valign="top">2019-06-27</td>
<td valign="top">unufabub.net</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-21</td><td valign="top">2019-06-30</td>
<td valign="top">yoevuajas.us</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-22</td><td valign="top">2019-06-30</td>
<td valign="top">epcioalas.info</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-20</td><td valign="top">2019-06-29</td>
<td valign="top">huoseavas.name</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-17</td><td valign="top">2019-06-26</td>
<td valign="top">caoelasas.name</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-22</td><td valign="top">2019-06-30</td>
<td valign="top">ijcaiatas.name</td><td valign="top">0xDAFE02C</td><td valign="top">2019-06-19</td><td valign="top">2019-06-28</td>

木马Pitou.B（Trojan.Pitou.B）

赛门铁克（Symantec ）对Pitou的[技术描述](https://www.symantec.com/security-center/writeup/2016-011823-3733-99)列出了20个域名。
<td valign="bottom">域名</td><td valign="bottom">种子</td><td valign="bottom">首次生成时间</td><td valign="bottom">有效时间</td>
<td valign="top">ecqevaaam.net</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-06</td><td valign="top">2016-01-15</td>
<td valign="top">yaefobab.info</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-09</td><td valign="top">2016-01-18</td>
<td valign="top">alguubub.mobi</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-14</td><td valign="top">2016-01-23</td>
<td valign="top">dueifarat.name</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-14</td><td valign="top">2016-01-23</td>
<td valign="top">ehbooagax.info</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-13</td><td valign="top">2016-01-22</td>
<td valign="top">igocobab.com</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-08</td><td valign="top">2016-01-17</td>
<td valign="top">utleeawav.us</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-14</td><td valign="top">2016-01-23</td>
<td valign="top">wuomoalan.us</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-06</td><td valign="top">2016-01-15</td>
<td valign="top">coosubca.mobi</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-09</td><td valign="top">2016-01-18</td>
<td valign="top">seeuvamap.mobi</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-06</td><td valign="top">2016-01-15</td>
<td valign="top">hioxcaoas.me</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-15</td><td valign="top">2016-01-24</td>
<td valign="top">upxoearak.biz</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-07</td><td valign="top">2016-01-16</td>
<td valign="top">oxepibib.net</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-07</td><td valign="top">2016-01-16</td>
<td valign="top">ruideawaf.us</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-08</td><td valign="top">2016-01-17</td>
<td valign="top">agtisaib.info</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-07</td><td valign="top">2016-01-16</td>
<td valign="top">neaqaaxag.org</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-08</td><td valign="top">2016-01-17</td>
<td valign="top">pooexaxaq.org</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-15</td><td valign="top">2016-01-24</td>
<td valign="top">iyweialay.net</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-13</td><td valign="top">2016-01-22</td>
<td valign="top">laagubha.com</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-15</td><td valign="top">2016-01-24</td>
<td valign="top">viurjaza.name</td><td valign="top">0xDAFE02D</td><td valign="top">2016-01-09</td><td valign="top">2016-01-18</td>

附录中是对虚拟机使用的虚拟指令集架构的介绍，有兴趣可以看一下。

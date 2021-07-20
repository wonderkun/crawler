> 原文链接: https://www.anquanke.com//post/id/227394 


# LibFuzzer workshop学习之路（final）


                                阅读量   
                                **144421**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01bcbdd98e72bec92d.jpg)](https://p1.ssl.qhimg.com/t01bcbdd98e72bec92d.jpg)



## libfuzzer workshop学习之路 final

> workshop一共给出了11个lesson，每一个lesson都会涉及到一些新的东西，这篇以最后的两个案例(对re2和pcre2的fuzz)为例，会涉及到一些链接库的选择以及插桩编译时的一些参数的设置，还有max_len的设置对我们最后fuzz结果的影响。



## fuzzing pcre2

pcre2:`Perl Compatible Regular Expressions Version 2`(Perl兼容的正则表达式)即是一个C语言编写的正则表达式函数库，被很多开源软件所使用比如PHP，Apache，Nmap等。<br>
workshop提供的pcre2版本是10.00，先进行源码编译工作。

```
tar xzf pcre2-10.00.tgz
cd pcre2-10.00

./autogen.sh
export FUZZ_CXXFLAGS="-O2 -fno-omit-frame-pointer -gline-tables-only -fsanitize=address,fuzzer-no-link -fsanitize-address-use-after-scope"
CXX="clang++ $FUZZ_CXXFLAGS" CC="clang $FUZZ_CXXFLAGS" \
    CCLD="clang++ $FUZZ_CXXFLAGS"  ./configure --enable-never-backslash-C \
    --with-match-limit=1000 --with-match-limit-recursion=1000
make -j
```

这里的一些插桩的参数和进阶篇的差不多，要注意的编译选项是`fuzzer-no-link`，如果修改大型项目的CFLAGS，它也需要编译自己的主符号的可执行文件，则可能需要在不链接的情况下仅请求检测，即`fuzzer-no-link`强制在链接阶段不生效。因此当我在插桩编译一个较大的开源库的时候推荐加上这个选项，如果不加的话fuzz效率如下：

```
#2    INITED cov: 7 ft: 8 corp: 1/1b exec/s: 0 rss: 27Mb
#3    NEW    cov: 9 ft: 10 corp: 2/5b lim: 4 exec/s: 0 rss: 27Mb L: 4/4 MS: 1 CrossOver-
#7    REDUCE cov: 9 ft: 10 corp: 2/3b lim: 4 exec/s: 0 rss: 28Mb L: 2/2 MS: 4 ChangeByte-CrossOver-ChangeBinInt-EraseBytes-
#35    REDUCE cov: 10 ft: 11 corp: 3/5b lim: 4 exec/s: 0 rss: 28Mb L: 2/2 MS: 3 CopyPart-ChangeByte-EraseBytes-
#146    REDUCE cov: 10 ft: 11 corp: 3/4b lim: 4 exec/s: 0 rss: 28Mb L: 1/2 MS: 1 EraseBytes-
#1491    REDUCE cov: 16 ft: 17 corp: 4/21b lim: 17 exec/s: 0 rss: 28Mb L: 17/17 MS: 5 ChangeBit-ShuffleBytes-InsertRepeatedBytes-ChangeBit-CrossOver-
#1889    REDUCE cov: 16 ft: 17 corp: 4/20b lim: 17 exec/s: 0 rss: 28Mb L: 16/16 MS: 3 ShuffleBytes-CopyPart-EraseBytes-
#524288    pulse  cov: 16 ft: 17 corp: 4/20b lim: 4096 exec/s: 87381 rss: 830Mb
#1048576    pulse  cov: 16 ft: 17 corp: 4/20b lim: 4096 exec/s: 104857 rss: 830Mb
#2097152    pulse  cov: 16 ft: 17 corp: 4/20b lim: 4096 exec/s: 123361 rss: 830Mb
#4194304    pulse  cov: 16 ft: 17 corp: 4/20b lim: 4096 exec/s: 127100 rss: 830Mb
#8388608    pulse  cov: 16 ft: 17 corp: 4/20b lim: 4096 exec/s: 131072 rss: 830Mb
```

另外，在执行configure生成makefile时针对pcre2添加了一些参数：<br>`--with-match-limit=1000`:限制一次匹配时使用的资源数为1000,默认值为10000000<br>`--with-match-limit-recursion=1000`:限制一次匹配时的递归深度为1000,默认为10000000(几乎可以说是无限)<br>`--enable-never-backslash-C`:禁用在字符串中，将反斜线作为转义序列接受。

编译好开源库后就要研究harness了，workshop提供的如下：

```
// Copyright 2016 Google Inc. All Rights Reserved.
// Licensed under the Apache License, Version 2.0 (the "License");

#include &lt;stdint.h&gt;
#include &lt;stddef.h&gt;

#include &lt;string&gt;

#include "pcre2posix.h"

using std::string;

extern "C" int LLVMFuzzerTestOneInput(const unsigned char *data, size_t size) `{`
  if (size &lt; 1) return 0;
  regex_t preg;
  string str(reinterpret_cast&lt;const char*&gt;(data), size);
  string pat(str);
  int flags = data[size/2] - 'a';  // Make it 0 when the byte is 'a'.
  if (0 == regcomp(&amp;preg, pat.c_str(), flags)) `{`
    regmatch_t pmatch[5];
    regexec(&amp;preg, str.c_str(), 5, pmatch, 0);
    regfree(&amp;preg);
  `}`
  return 0;
`}`
```

解释一下逻辑：首先将样本输入中的’a’置0，之后通过regcomp()函数编译正则表达式，即将指定的正则表达式pat.c_str()编译为特定数据格式preg，使得匹配更加有效。函数regexec()会使用这个数据在目标文本串中进行模式匹配，之后regfree()释放正则表达式。<br>
这个harness通过include库”pcre2posix.h”，将pcre2主要的函数包含在了里面，同时这些函数涉及到的一些内存相关的操作也常常是触发crash的点。<br>
之后进行编译链接：

```
clang++ -O2 -fno-omit-frame-pointer -gline-tables-only -fsanitize=address,fuzzer-no-link -fsanitize-address-use-after-scope pcre2_fuzzer.cc -I pcre2-10.00/src -Wl,--whole-archive pcre2-10.00/.libs/libpcre2-8.a pcre2-10.00/.libs/libpcre2-posix.a -Wl,-no-whole-archive -fsanitize=fuzzer -o pcre2-10.00-fsanitize_fuzzer
```

和之前不同，这次多了一些参数：`--whole-archive`和`--no-whole-archive`是ld专有的命令行参数，clang++并不认识，要通过clang++传递到ld，需要在他们前面加`-Wl`。`--whole-archive`可以把 在其后面出现的静态库包含的函数和变量输出到动态库，`--no-whole-archive`则关掉这个特性，因此这里将两个静态库libpcre2-8.a和libpcre2-posix.a里的符号输出到动态库里，使得程序可以在运行时动态链接使用到的函数，也使得fuzz效率得到了提升。执行一下很快得到了crash:

```
#538040    NEW    cov: 3286 ft: 15824 corp: 6803/133Kb lim: 74 exec/s: 1775 rss: 775Mb L: 24/74 MS: 3 ChangeASCIIInt-ChangeASCIIInt-EraseBytes-
#538092    REDUCE cov: 3286 ft: 15824 corp: 6803/133Kb lim: 74 exec/s: 1775 rss: 775Mb L: 23/74 MS: 2 CopyPart-EraseBytes-
#538098    REDUCE cov: 3286 ft: 15824 corp: 6803/133Kb lim: 74 exec/s: 1758 rss: 775Mb L: 6/74 MS: 1 EraseBytes-
#538204    REDUCE cov: 3286 ft: 15824 corp: 6803/133Kb lim: 74 exec/s: 1758 rss: 775Mb L: 16/74 MS: 1 EraseBytes-
#538415    REDUCE cov: 3286 ft: 15825 corp: 6804/134Kb lim: 74 exec/s: 1759 rss: 775Mb L: 35/74 MS: 1 ShuffleBytes-
=================================================================
==17319==ERROR: AddressSanitizer: stack-buffer-overflow on address 0x7ffe809de45f at pc 0x0000005e1518 bp 0x7ffe809dd8f0 sp 0x7ffe809dd8e8
READ of size 1 at 0x7ffe809de45f thread T0
    #0 0x5e1517 in match /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_match.c:5968:11
    #1 0x5a0624 in pcre2_match_8 /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_match.c:6876:8
    #2 0x5f5e64 in regexec /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2posix.c:291:6
    #3 0x551947 in LLVMFuzzerTestOneInput /home/admin/libfuzzer-workshop/lessons/11/pcre2_fuzzer.cc:21:5
    #4 0x459661 in fuzzer::Fuzzer::ExecuteCallback(unsigned char const*, unsigned long) /local/mnt/workspace/bcain_clang_bcain-ubuntu_23113/llvm/utils/release/final/llvm.src/projects/compiler-rt/lib/fuzzer/FuzzerLoop.cpp:553:15
    #5 0x458ea5 in fuzzer::Fuzzer::RunOne(unsigned char const*, unsigned long, bool, fuzzer::InputInfo*, bool*) /local/mnt/workspace/bcain_clang_bcain-ubuntu_23113/llvm/utils/release/final/llvm.src/projects/compiler-rt/lib/fuzzer/FuzzerLoop.cpp:469:3
    #6 0x45b147 in fuzzer::Fuzzer::MutateAndTestOne() /local/mnt/workspace/bcain_clang_bcain-ubuntu_23113/llvm/utils/release/final/llvm.src/projects/compiler-rt/lib/fuzzer/FuzzerLoop.cpp:695:19
    #7 0x45be65 in fuzzer::Fuzzer::Loop(std::Fuzzer::vector&lt;fuzzer::SizedFile, fuzzer::fuzzer_allocator&lt;fuzzer::SizedFile&gt; &gt;&amp;) /local/mnt/workspace/bcain_clang_bcain-ubuntu_23113/llvm/utils/release/final/llvm.src/projects/compiler-rt/lib/fuzzer/FuzzerLoop.cpp:831:5
    #8 0x449c28 in fuzzer::FuzzerDriver(int*, char***, int (*)(unsigned char const*, unsigned long)) /local/mnt/workspace/bcain_clang_bcain-ubuntu_23113/llvm/utils/release/final/llvm.src/projects/compiler-rt/lib/fuzzer/FuzzerDriver.cpp:825:6
    #9 0x473092 in main /local/mnt/workspace/bcain_clang_bcain-ubuntu_23113/llvm/utils/release/final/llvm.src/projects/compiler-rt/lib/fuzzer/FuzzerMain.cpp:19:10
    #10 0x7f0d3f5c3bf6 in __libc_start_main (/lib/x86_64-linux-gnu/libc.so.6+0x21bf6)
    #11 0x41ddb9 in _start (/home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00-fsanitize_fuzzer+0x41ddb9)

Address 0x7ffe809de45f is located in stack of thread T0 at offset 159 in frame
    #0 0x55136f in LLVMFuzzerTestOneInput /home/admin/libfuzzer-workshop/lessons/11/pcre2_fuzzer.cc:13

  This frame has 6 object(s):
    [32, 40) '__dnew.i.i.i.i26'
    [64, 72) '__dnew.i.i.i.i'
    [96, 128) 'preg' (line 15)
    [160, 192) 'str' (line 16) &lt;== Memory access at offset 159 underflows this variable
    [224, 256) 'pat' (line 17)
    [288, 328) 'pmatch' (line 20)
HINT: this may be a false positive if your program uses some custom stack unwind mechanism, swapcontext or vfork
      (longjmp and C++ exceptions *are* supported)
SUMMARY: AddressSanitizer: stack-buffer-overflow /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_match.c:5968:11 in match
Shadow bytes around the buggy address:
  0x100050133c30: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x100050133c40: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x100050133c50: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x100050133c60: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x100050133c70: 00 00 00 00 00 00 00 00 f1 f1 f1 f1 f8 f2 f2 f2
=&gt;0x100050133c80: f8 f2 f2 f2 00 00 00 00 f2 f2 f2[f2]00 00 00 00
  0x100050133c90: f2 f2 f2 f2 00 00 00 00 f2 f2 f2 f2 00 00 00 00
  0x100050133ca0: 00 f3 f3 f3 f3 f3 f3 f3 00 00 00 00 00 00 00 00
  0x100050133cb0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x100050133cc0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
  0x100050133cd0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
Shadow byte legend (one shadow byte represents 8 application bytes):
  Addressable:           00
  Partially addressable: 01 02 03 04 05 06 07 
  Heap left redzone:       fa
  Freed heap region:       fd
  Stack left redzone:      f1
  Stack mid redzone:       f2
  Stack right redzone:     f3
  Stack after return:      f5
  Stack use after scope:   f8
  Global redzone:          f9
  Global init order:       f6
  Poisoned by user:        f7
  Container overflow:      fc
  Array cookie:            ac
  Intra object redzone:    bb
  ASan internal:           fe
  Left alloca redzone:     ca
  Right alloca redzone:    cb
  Shadow gap:              cc
==17319==ABORTING
MS: 1 ChangeBit-; base unit: 7a9e5264e8896a1d996088a56a315765c53c7b33
0x5c,0x43,0x2b,0x5c,0x53,0x2b,0xde,0xac,0xd4,0xa3,0x53,0x2b,0x21,0x21,0x68,
\\C+\\S+\xde\xac\xd4\xa3S+!!h
artifact_prefix='./'; Test unit written to ./crash-5ae911f7e958e646e05ebe28421183f6efc0bc88
Base64: XEMrXFMr3qzUo1MrISFo
```

`SUMMARY: AddressSanitizer: stack-buffer-overflow /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_match.c:5968:11 in match`指出在pcre2_match.c里存在stackoverflow。对漏洞进行定位：<br>
在pcre2posix.c中调用了pcre2_match

```
#in pcre2posix.c
rc = pcre2_match((const pcre2_code *)preg-&gt;re_pcre2_code,(PCRE2_SPTR)string + so, (eo - so), 0, options, md, NULL);
```

pcre2_match定义在pcre2_match.c中，在pcre2_match中调用了match函数：

```
#in pcre2_match.c
rc = match(start_match, mb-&gt;start_code, start_match, 2, mb, NULL, 0);
```

在执行match的过程中出现栈溢出的位置在于：

```
for(;;)
          `{`
          if (eptr == pp) goto TAIL_RECURSE;
          RMATCH(eptr, ecode, offset_top, mb, eptrb, RM46);
          if (rrc != MATCH_NOMATCH) RRETURN(rrc);
          eptr--;
          BACKCHAR(eptr);   //overflow处
          if (ctype == OP_ANYNL &amp;&amp; eptr &gt; pp  &amp;&amp; UCHAR21(eptr) == CHAR_NL &amp;&amp;
              UCHAR21(eptr - 1) == CHAR_CR) eptr--;
          `}`
```

当我以为fuzz的工作已经完成的时候，只是尝试着修改了一下编译链接harness时的静态库为全部库：

```
clang++ -O2 -fno-omit-frame-pointer -gline-tables-only -fsanitize=address,fuzzer-no-link -fsanitize-address-use-after-scope pcre2_fuzzer.cc -I pcre2-10.00/src -Wl,--whole-archive pcre2-10.00/.libs/*.a -Wl,-no-whole-archive -fsanitize=fuzzer -o pcre2-10.00-fsanitize_fuzzer
```

再次fuzz的结果令我惊讶：

```
#605510    REDUCE cov: 3273 ft: 15706 corp: 6963/139Kb lim: 86 exec/s: 255 rss: 597Mb L: 18/86 MS: 1 EraseBytes-
#605733    NEW    cov: 3273 ft: 15707 corp: 6964/139Kb lim: 86 exec/s: 255 rss: 597Mb L: 29/86 MS: 3 ShuffleBytes-CopyPart-CMP- DE: "+n"-
#605994    REDUCE cov: 3273 ft: 15707 corp: 6964/139Kb lim: 86 exec/s: 255 rss: 597Mb L: 36/86 MS: 1 EraseBytes-
#606040    REDUCE cov: 3273 ft: 15707 corp: 6964/139Kb lim: 86 exec/s: 255 rss: 597Mb L: 19/86 MS: 1 EraseBytes-
#606121    NEW    cov: 3273 ft: 15708 corp: 6965/139Kb lim: 86 exec/s: 255 rss: 597Mb L: 27/86 MS: 1 CopyPart-
#606196    NEW    cov: 3273 ft: 15709 corp: 6966/139Kb lim: 86 exec/s: 255 rss: 597Mb L: 86/86 MS: 5 ChangeASCIIInt-ChangeBit-ChangeBit-ChangeASCIIInt-CrossOver-
=================================================================
==10857==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x6110001625ea at pc 0x00000055d548 bp 0x7ffccf4098f0 sp 0x7ffccf4098e8
WRITE of size 1 at 0x6110001625ea thread T0
    #0 0x55d547 in _pcre2_ord2utf_8 /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_ord2utf.c:92:12
    #1 0x4f60f4 in add_to_class /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_compile.c:2870:20
    #2 0x4f5dd0 in add_to_class /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_compile.c:2820:18
    #3 0x4e03e0 in compile_branch /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_compile.c:3923:11
    #4 0x4d3f2f in compile_regex /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_compile.c:6723:8
    #5 0x4d136c in pcre2_compile_8 /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_compile.c:7734:7
    #6 0x56c3b3 in regcomp /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2posix.c:219:23
    #7 0x4c83c9 in LLVMFuzzerTestOneInput /home/admin/libfuzzer-workshop/lessons/11/pcre2_fuzzer.cc:19:12
    #8 0x585632 in fuzzer::Fuzzer::ExecuteCallback(unsigned char const*, unsigned long) /home/admin/libfuzzer-workshop/libFuzzer/Fuzzer/./FuzzerLoop.cpp:556:15
    #9 0x584cd5 in fuzzer::Fuzzer::RunOne(unsigned char const*, unsigned long, bool, fuzzer::InputInfo*, bool*) /home/admin/libfuzzer-workshop/libFuzzer/Fuzzer/./FuzzerLoop.cpp:470:3
    #10 0x58606c in fuzzer::Fuzzer::MutateAndTestOne() /home/admin/libfuzzer-workshop/libFuzzer/Fuzzer/./FuzzerLoop.cpp:698:19
    #11 0x586c75 in fuzzer::Fuzzer::Loop(std::vector&lt;fuzzer::SizedFile, fuzzer::fuzzer_allocator&lt;fuzzer::SizedFile&gt; &gt;&amp;) /home/admin/libfuzzer-workshop/libFuzzer/Fuzzer/./FuzzerLoop.cpp:830:5
    #12 0x572b8b in fuzzer::FuzzerDriver(int*, char***, int (*)(unsigned char const*, unsigned long)) /home/admin/libfuzzer-workshop/libFuzzer/Fuzzer/./FuzzerDriver.cpp:824:6
    #13 0x56cc20 in main /home/admin/libfuzzer-workshop/libFuzzer/Fuzzer/./FuzzerMain.cpp:19:10
    #14 0x7f16a7ecbbf6 in __libc_start_main (/lib/x86_64-linux-gnu/libc.so.6+0x21bf6)
    #15 0x41deb9 in _start (/home/admin/libfuzzer-workshop/lessons/11/pcre2_10.00_fuzzer+0x41deb9)

0x6110001625ea is located 0 bytes to the right of 234-byte region [0x611000162500,0x6110001625ea)
allocated by thread T0 here:
    #0 0x495dbd in malloc /local/mnt/workspace/bcain_clang_bcain-ubuntu_23113/llvm/utils/release/final/llvm.src/projects/compiler-rt/lib/asan/asan_malloc_linux.cc:145:3
    #1 0x4d0953 in pcre2_compile_8 /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_compile.c:7656:3
    #2 0x56c3b3 in regcomp /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2posix.c:219:23
    #3 0x4c83c9 in LLVMFuzzerTestOneInput /home/admin/libfuzzer-workshop/lessons/11/pcre2_fuzzer.cc:19:12
    #4 0x585632 in fuzzer::Fuzzer::ExecuteCallback(unsigned char const*, unsigned long) /home/admin/libfuzzer-workshop/libFuzzer/Fuzzer/./FuzzerLoop.cpp:556:15
    #5 0x584cd5 in fuzzer::Fuzzer::RunOne(unsigned char const*, unsigned long, bool, fuzzer::InputInfo*, bool*) /home/admin/libfuzzer-workshop/libFuzzer/Fuzzer/./FuzzerLoop.cpp:470:3
    #6 0x58606c in fuzzer::Fuzzer::MutateAndTestOne() /home/admin/libfuzzer-workshop/libFuzzer/Fuzzer/./FuzzerLoop.cpp:698:19
    #7 0x586c75 in fuzzer::Fuzzer::Loop(std::vector&lt;fuzzer::SizedFile, fuzzer::fuzzer_allocator&lt;fuzzer::SizedFile&gt; &gt;&amp;) /home/admin/libfuzzer-workshop/libFuzzer/Fuzzer/./FuzzerLoop.cpp:830:5
    #8 0x572b8b in fuzzer::FuzzerDriver(int*, char***, int (*)(unsigned char const*, unsigned long)) /home/admin/libfuzzer-workshop/libFuzzer/Fuzzer/./FuzzerDriver.cpp:824:6
    #9 0x56cc20 in main /home/admin/libfuzzer-workshop/libFuzzer/Fuzzer/./FuzzerMain.cpp:19:10
    #10 0x7f16a7ecbbf6 in __libc_start_main (/lib/x86_64-linux-gnu/libc.so.6+0x21bf6)

SUMMARY: AddressSanitizer: heap-buffer-overflow /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_ord2utf.c:92:12 in _pcre2_ord2utf_8
Shadow bytes around the buggy address:
  0x0c2280024460: fd fd fd fd fd fd fd fd fd fd fd fd fa fa fa fa
  0x0c2280024470: fa fa fa fa fa fa fa fa fd fd fd fd fd fd fd fd
  0x0c2280024480: fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd fd
  0x0c2280024490: fd fd fd fd fd fd fd fd fa fa fa fa fa fa fa fa
  0x0c22800244a0: 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
=&gt;0x0c22800244b0: 00 00 00 00 00 00 00 00 00 00 00 00 00[02]fa fa
  0x0c22800244c0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x0c22800244d0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x0c22800244e0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x0c22800244f0: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
  0x0c2280024500: fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa fa
Shadow byte legend (one shadow byte represents 8 application bytes):
  Addressable:           00
  Partially addressable: 01 02 03 04 05 06 07 
  Heap left redzone:       fa
  Freed heap region:       fd
  Stack left redzone:      f1
  Stack mid redzone:       f2
  Stack right redzone:     f3
  Stack after return:      f5
  Stack use after scope:   f8
  Global redzone:          f9
  Global init order:       f6
  Poisoned by user:        f7
  Container overflow:      fc
  Array cookie:            ac
  Intra object redzone:    bb
  ASan internal:           fe
  Left alloca redzone:     ca
  Right alloca redzone:    cb
  Shadow gap:              cc
==10857==ABORTING
MS: 5 InsertRepeatedBytes-CMP-CrossOver-ChangeBit-CrossOver- DE: "+\xc6"-; base unit: ce48e02587af5cb5d3e84053d6d5b4545bbb6e32
0x5b,0x2a,0x5d,0x3f,0x5b,0x3f,0x3f,0x5c,0x53,0x3f,0x5b,0x2a,0x5d,0x3f,0x5b,0x3f,0x3f,0x5c,0x53,0x2a,0x63,0x20,0x20,0x20,0x25,0xc6,0xa4,0x1a,0x2d,0x5b,0x43,0x1a,0x2d,0xc6,0xa4,0x5d,0x50,0x2a,0x5d,0x50,0x2a,0x5e,0x58,0x42,0x5c,0x5c,0x3f,0x77,0xc,0x5c,0x77,0x0,0x36,0x5c,0x20,0xa0,0xc0,0xec,0x2d,0x3f,0x5c,0x77,0x3f,0x5c,0x2d,0xac,0x3f,0x5c,
[*]?[??\\S?[*]?[??\\S*c   %\xc6\xa4\x1a-[C\x1a-\xc6\xa4]P*]P*^XB\\\\?w\x0c\\w\x006\\ \xa0\xc0\xec-?\\w?\\-\xac?\\
artifact_prefix='./'; Test unit written to ./crash-849705875bb2098817f3299ee582e2207a568e63
Base64: WypdP1s/P1xTP1sqXT9bPz9cUypjICAgJcakGi1bQxotxqRdUCpdUCpeWEJcXD93DFx3ADZcIKDA7C0/XHc/XC2sP1w=
stat::number_of_executed_units: 606206
stat::average_exec_per_sec:     255
stat::new_units_added:          8960
stat::slowest_unit_time_sec:    0
stat::peak_rss_mb:              598
```

得到了一个不一样的crash。但这也在情理之中，通过链接不同或更多的静态库。只要harness程序逻辑所能涉及到，就有机会得到不同静态库里的crash。<br>
通过`SUMMARY: AddressSanitizer: heap-buffer-overflow /home/admin/libfuzzer-workshop/lessons/11/pcre2-10.00/src/pcre2_ord2utf.c:92:12 in _pcre2_ord2utf_8`我们了解到在pcre2_ord2utf.c中存在heapoverflow的漏洞。同样对漏洞进行定位：<br>
这次的函数调用有点多，一层一层的找：<br>
首先在`pcre2posix.c`中调用`pcre2_compile`：

```
preg-&gt;re_pcre2_code = pcre2_compile((PCRE2_SPTR)pattern, -1, options,
  &amp;errorcode, &amp;erroffset, NULL);
```

该函数定义在`pcre2_compile.c`中，然后又调用了`compile_regex`:

```
(void)compile_regex(re-&gt;overall_options, &amp;code, &amp;ptr, &amp;errorcode, FALSE, FALSE,
   0, 0, &amp;firstcu, &amp;firstcuflags, &amp;reqcu, &amp;reqcuflags, NULL, &amp;cb, NULL);
```

之后在函数`compile_regex`中又调用了`compile_branch`：

```
if (!compile_branch(&amp;options, &amp;code, &amp;ptr, errorcodeptr, &amp;branchfirstcu,
        &amp;branchfirstcuflags, &amp;branchreqcu, &amp;branchreqcuflags, &amp;bc,
        cond_depth, cb, (lengthptr == NULL)? NULL : &amp;length))
    `{`
    *ptrptr = ptr;
    return FALSE;
    `}`
```

`compile_branch`中又调用了`add_to_class`：

```
class_has_8bitchar +=
          add_to_class(classbits, &amp;class_uchardata, options, cb, c, d);
```

接着`add_to_class`调用`PRIV`:

```
else if (start == end)
      `{`
      *uchardata++ = XCL_SINGLE;
      uchardata += PRIV(ord2utf)(start, uchardata);
      `}`
    `}`
```

`PRIV`定义在`pcre2_ord2utf.c`中：

```
unsigned int
PRIV(ord2utf)(uint32_t cvalue, PCRE2_UCHAR *buffer)
`{`
/* Convert to UTF-8 */

#if PCRE2_CODE_UNIT_WIDTH == 8
register int i, j;
for (i = 0; i &lt; PRIV(utf8_table1_size); i++)
  if ((int)cvalue &lt;= PRIV(utf8_table1)[i]) break;
buffer += i;
for (j = i; j &gt; 0; j--)
 `{`
 *buffer-- = 0x80 | (cvalue &amp; 0x3f);  //此处对于内存指针循环操作由于限制条件不当导致出现了heap_overflow
 cvalue &gt;&gt;= 6;
 `}`
*buffer = PRIV(utf8_table2)[i] | cvalue;
return i + 1;

/* Convert to UTF-16 */

#elif PCRE2_CODE_UNIT_WIDTH == 16
if (cvalue &lt;= 0xffff)
  `{`
  *buffer = (PCRE2_UCHAR)cvalue;
  return 1;
  `}`
cvalue -= 0x10000;
*buffer++ = 0xd800 | (cvalue &gt;&gt; 10);
*buffer = 0xdc00 | (cvalue &amp; 0x3ff);
return 2;

/* Convert to UTF-32 */

#else
*buffer = (PCRE2_UCHAR)cvalue;
return 1;
#endif
`}`
```

总结下这两个crash：<br>
第一个crash由harness中的`regexech`函数的匹配逻辑触发`stack_overflow`，位于`pcre2_match.c:5968:11`；第二个crash由`regcomp`函数的编译逻辑触发`heap_overflow`，位于`pcre2_ord2utf.c:92:12`。<br>
一层层的函数调用关系分析得让人头大，但这也正体现了漏洞挖掘中的“挖掘”二字的含义。



## fuzzing re2

这一个例子将让我们意识到`max_len`的选择对于fuzz效率的影响。<br>
re2是一个高效的、原则性的正则表达式库。是由两位来在Google的大神用C++实现的。Go中的regexp正则表达式包也是由re2实现的。workshop提供的是re2-2014-12-09的版本。<br>
先源码编译：

```
tar xzf re2.tgz
cd re2
export FUZZ_CXXFLAGS="-O2 -fno-omit-frame-pointer -gline-tables-only -fsanitize=address,fuzzer-no-link -fsanitize-address-use-after-scope"
make clean
CXX=clang++ CXXFLAGS="$FUZZ_CXXFLAGS"  make -j
```

接着研究harness：

```
// Copyright (c) 2016 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

#include &lt;stddef.h&gt;
#include &lt;stdint.h&gt;

#include &lt;string&gt;

#include "re2/re2.h"
#include "util/logging.h"

using std::string;

void Test(const string&amp; buffer, const string&amp; pattern,
          const RE2::Options&amp; options) `{`
  RE2 re(pattern, options);
  if (!re.ok())
    return;

  string m1, m2;
  int i1, i2;
  double d1;

  if (re.NumberOfCapturingGroups() == 0) `{`
    RE2::FullMatch(buffer, re);
    RE2::PartialMatch(buffer, re);
  `}` else if (re.NumberOfCapturingGroups() == 1) `{`
    RE2::FullMatch(buffer, re, &amp;m1);
    RE2::PartialMatch(buffer, re, &amp;i1);
  `}` else if (re.NumberOfCapturingGroups() == 2) `{`
    RE2::FullMatch(buffer, re, &amp;i1, &amp;i2);
    RE2::PartialMatch(buffer, re, &amp;m1, &amp;m2);
  `}`

  re2::StringPiece input(buffer);
  RE2::Consume(&amp;input, re, &amp;m1);
  RE2::FindAndConsume(&amp;input, re, &amp;d1);
  string tmp1(buffer);
  RE2::Replace(&amp;tmp1, re, "zz");
  string tmp2(buffer);
  RE2::GlobalReplace(&amp;tmp2, re, "xx");
  RE2::QuoteMeta(re2::StringPiece(pattern));
`}`

// Entry point for LibFuzzer.
extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size) `{`
  if (size &lt; 1)
    return 0;

  RE2::Options options;

  size_t options_randomizer = 0;
  for (size_t i = 0; i &lt; size; i++)
    options_randomizer += data[i];

  if (options_randomizer &amp; 1)
    options.set_encoding(RE2::Options::EncodingLatin1);

  options.set_posix_syntax(options_randomizer &amp; 2);
  options.set_longest_match(options_randomizer &amp; 4);
  options.set_literal(options_randomizer &amp; 8);
  options.set_never_nl(options_randomizer &amp; 16);
  options.set_dot_nl(options_randomizer &amp; 32);
  options.set_never_capture(options_randomizer &amp; 64);
  options.set_case_sensitive(options_randomizer &amp; 128);
  options.set_perl_classes(options_randomizer &amp; 256);
  options.set_word_boundary(options_randomizer &amp; 512);
  options.set_one_line(options_randomizer &amp; 1024);

  options.set_log_errors(false);

  const char* data_input = reinterpret_cast&lt;const char*&gt;(data);
  `{`
    string pattern(data_input, size);
    string buffer(data_input, size);
    Test(buffer, pattern, options);
  `}`

  if (size &gt;= 3) `{`
    string pattern(data_input, size / 3);
    string buffer(data_input + size / 3, size - size / 3);
    Test(buffer, pattern, options);
  `}`

  return 0;
`}`
```

可以看到harness用到了很多re2里的方法，最后使用FullMatch和PartialMatch接口进行匹配buffer和re。其中buffer是由`data_input`和`size`初始化得到（data_input由输入的data经无关类型转换得到），re是由pattern和options建立的RE2对象。<br>
注意到harness里有几个条件分支语句，首先是size&lt;1是直接返回，还有就是当size&gt;=3时，初始化pattn和buffer用的是size/3和size-size/3说明它对我们的输入的size进行了切割，初始化pattern用到的是`data_input + size / 3`，而初始化buffer是用的之后的data_input。这样使得我们样例的size会对fuzz的过程产生影响。如果size很短，可能无法触发crash，而如果size很大，对harness的执行匹配过程就会更加耗时，影响fuzz寻找覆盖点的效率。下面做几个测试，比较一下max_len对fuzz过程的影响：<br>
编译链接harness：

```
clang++ -O2 -fno-omit-frame-pointer -gline-tables-only -fsanitize=address,fuzzer-no-link -fsanitize-address-use-after-scope -std=gnu++98 target.cc -I re2/ re2/obj/libre2.a -fsanitize=fuzzer -o re2_fuzzer
```

由于使用的re2版本较老了，编译的时候使用了c++98标准。

首先我们设置max_len为10，执行时间为100秒,-print_final_stats=1打印最后的结果，corpus1作为语料库的存放处：

```
➜  10 git:(master) ✗ ./re2_fuzzer ./corpus1 -print_final_stats=1 -max_len=10 -max_total_time=100

Done 643760 runs in 101 second(s)
stat::number_of_executed_units: 643760
stat::average_exec_per_sec:     6373
stat::new_units_added:          36
stat::slowest_unit_time_sec:    0
stat::peak_rss_mb:              456
```

只探测到了36个代码单元。<br>
接着设置max_len为100，执行时间为100秒,-print_final_stats=1打印最后的结果，corpus2作为语料库的存放处：

```
./re2_fuzzer ./corpus2 -print_final_stats=1 -max_len=100 -max_total_time=100
Done 233437 runs in 101 second(s)

stat::number_of_executed_units: 233437
stat::average_exec_per_sec:     2311
stat::new_units_added:          50
stat::slowest_unit_time_sec:    0
stat::peak_rss_mb:              675
```

探测到了50个代码单元,感觉差别不大。<br>
然年设置max_len为1000，执行时间为100秒,-print_final_stats=1打印最后的结果，corpus3作为语料库的存放处：

```
./re2_fuzzer ./corpus3 -print_final_stats=1 -max_len=1000 -max_total_time=100

Done 105935 runs in 101 second(s)
stat::number_of_executed_units: 105935
stat::average_exec_per_sec:     1048
stat::new_units_added:          97
stat::slowest_unit_time_sec:    0
stat::peak_rss_mb:              830
```

这次探测到了97个代码单元，是第二个的2倍，第一个的3倍左右。<br>
最后再设置max_len为500，执行时间为100秒,-print_final_stats=1打印最后的结果，corpus4作为语料库的存放处

```
./re2_fuzzer ./corpus4 -print_final_stats=1 -max_len=500 -max_total_time=100

Done 119361 runs in 101 second(s)
stat::number_of_executed_units: 119361
stat::average_exec_per_sec:     1181
stat::new_units_added:          117
stat::slowest_unit_time_sec:    0
stat::peak_rss_mb:              827
```

结果也比较明显，不同的max_len对fuzz的效率有着不同的影响，当然这也和你写的harness有关。因此在执行fuzzer的时候选择合适的max_len(如本例中的max_len在100~1000比较合适)会使得我们fuzzer探测到更多的代码块，得到crash的概率也就越大。



## 总结

libfuzzer workshop到此就全部学习完了。libfuzzer作为最常用的fuzz工具，它所涉及到的一些使用方法在workshop里都有相应的lesson。就我个人而言，在逐步学习libfuzzer的过程中感觉到libfuzzer对于开源库提供的接口函数的fuzz是十分强力的，而这也是我们在学习libfuzzer中的难点:如何能够设计出合理的harness，这需要我们对要fuzz的开源库提供的方法有一定的了解，经过攻击面分析等去逐步改善我们的harness，使得我们与获得crash更近一步。

初学libfuzzer，有错误疏忽之处烦请各位师傅指正。

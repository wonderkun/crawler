> 原文链接: https://www.anquanke.com//post/id/244071 


# 基于套接字的模糊测试技术之Apache HTTP（上）：突变


                                阅读量   
                                **165031**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者GitHub Security Lab﻿，文章来源：securitylab.github.com
                                <br>原文地址：[https://securitylab.github.com/research/fuzzing-apache-1/](https://securitylab.github.com/research/fuzzing-apache-1/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p2.ssl.qhimg.com/t01ff6d2a21dcb6fe5d.png)](https://p2.ssl.qhimg.com/t01ff6d2a21dcb6fe5d.png)



​ 在之前关于基于套接字的模糊测试技术的博客文章中，我解释了如果对FTP服务器进行模糊测试，并详细说明了我是如何对FreeRDP进行模糊测试。在我们基于套接字的模糊测试技术系列的第三部分也是最后一部分中，我将重点关注 HTTP 协议，更具体地说，我将针对**Apache HTTP 服务器**进行测试

​ 作为最流行的 Web 服务器之一，Apache HTTP 服务器不需要任何介绍。Apache HTTP 是最早的 HTTP 服务器之一，其开发可追溯到 1995 年。截至 2021 年 1 月，它的市场份额为 26%，是互联网上使用量第二大的 Web 服务器——目前运行在超过300.000.000台服务器上——仅略微落后于 Nginx (31%)

​ 我将分三部分详细介绍我的 Apache fuzzing 研究。在第一部分中，我将简要介绍 Apache HTTP 的工作原理，并让您深入了解自定义 mutator 以及如何将它们有效地应用于 HTTP 协议

​ 我们开始吧！



## 一、自定义突变器

​ 与单纯的随机生成输入相比，基于突变的模糊测试对现有的输入引入了微小的变化，这些变化可能仍然保持输入有效，但会产生新的行为。这就是我们所说的**“mutators”**

​ 默认情况下，AFL fuzzer 实现了基本的突变机制，如位翻转、字节递增/递减、简单运算或块拼接。这些mutator总体上实现了良好的效果，尤其是在二进制格式中，但是当应用于基于文法的格式（如 HTTP）时，它们的有效率一般。这就是为什么我决定创建一些额外的突变器，专门用于对 HTTP 协议进行模糊测试的任务。您可以在以下链接中找到代码：

```
https://github.com/antonio-morales/Apache-HTTP-Fuzzing/tree/main/Custom%20mutators
```

我在本练习中关注的一些突变策略包括：
<li>拼接变换（Piece swapping）：交换两个不同请求的部分
<ul>
- 行交换（Line swapping）: 交换两个不同 HTTP 请求的行
- 字交换（Word swapping）: 交换两个不同HTTP请求的单词<li>以1字节为字符集的暴力替换（1-byte bruteforce）：`0x00 – 0xFF`
</li>
<li>以2字节为字符集的暴力替换（2 bytes bruteforce）：`0x0000 – 0xFFFF`
</li>
<li>以3 个字母为字符集的暴力替换（3 letters bruteforce）：`[a-z]`{`3`}``
</li>
<li>以4个数字为字符集的暴力替换（4 digits bruteforce）：`[0-9]`{`4`}``
</li>
<li>以3 个字母和1个数字为字符集的暴力替换（3 letters &amp; numbers bruteforce）：`([a-z][0-9)`{`3`}``
</li>
<li>以3字节或者4字节字符串为字符集的暴力替换（3bytes / 4 bytes strings bruteforce）：将输入文件中的所有 3/4 字节字符串进行暴力替换<br>[![](https://p2.ssl.qhimg.com/t01ce6ea3e3a81f76aa.png)](https://p2.ssl.qhimg.com/t01ce6ea3e3a81f76aa.png)<br>[![](https://p2.ssl.qhimg.com/t01af7f1d2983b07c96.png)](https://p2.ssl.qhimg.com/t01af7f1d2983b07c96.png)
</li>
您可以在这里找到为了能够使用这些自定义突变器而需要包含的附加函数：

```
https://github.com/antonio-morales/Apache-HTTP-Fuzzing/blob/main/Custom%20mutators/Mutators_aux.c
```



## 二、覆盖率比较

​ 在我们能够保证我们的突变器能够用于完整的长期模糊测试工作之前，我们需要去验证我们自定义的mutator是否有效。

​ 考虑到这一点，我使用自定义突变器的不同组合进行了一系列模糊测试。我的目标是找到在**24 小时**内提供更高代码覆盖率的变异器组合。

​ 起始覆盖率如下（仅使用原始输入语料）：
<li>行数：**30.5%**
</li>
<li>函数：**40.7%**
</li>
​ 这些是 24 小时后每个mutator组合的结果（所有测试均使用以下参数进行`AFL_DISABLE_TRIM=1`和`-s 123`）

[![](https://p4.ssl.qhimg.com/t013cd7d079a06f8d03.png)](https://p4.ssl.qhimg.com/t013cd7d079a06f8d03.png)

​ 这里没有列出显示了更糟糕结果的mutator组合，且并没有将其列入考虑范围。如您所见，**Line Mixing + AFL HAVOC**是获胜的组合

[![](https://p0.ssl.qhimg.com/t01add0114e936fa9ce.png)](https://p0.ssl.qhimg.com/t01add0114e936fa9ce.png)

​ 之后，我通过增加启用的 Apache Mod 的数量进行了第二次测试。Line Mixing + HAVOC测试再次成为获胜的组合

[![](https://p3.ssl.qhimg.com/t01b251675d15a6ec67.png)](https://p3.ssl.qhimg.com/t01b251675d15a6ec67.png)

​ 虽然这是获胜的组合，但这并不意味着我只使用了这个自定义的mutator。在整个Apache HTTP 模糊测试过程中，我使用了所有可用的自定义突变器，因为我的目标是获得最高的代码覆盖率。在这种情况下，mutator 效率变得不那么重要了



## 三、自定义语法

​ 另一种方法是使用基于语法的突变器。除了使用自定义突变器之外，我将一个自定义语法添加到 AFL++工具中用来模糊 HTTP：[Grammar-Mutator](https://github.com/AFLplusplus/Grammar-Mutator)

​ 使用 Grammar-Mutator 非常简单：

```
make GRAMMAR_FILE=grammars/http.json
./grammar_generator-http 100 100 ./seeds ./trees
```

​ 然后

```
export AFL_CUSTOM_MUTATOR_LIBRARY=./libgrammarmutator-http.so
export AFL_CUSTOM_MUTATOR_ONLY=1
afl-fuzz …
```

​ 就我而言，我创建了一个简化的 [HTTP 语法规范](https://github.com/antonio-morales/Apache-HTTP-Fuzzing/blob/main/Custom%20Grammars/http.json)：

[![](https://p1.ssl.qhimg.com/t0118a7f93cac851e9b.png)](https://p1.ssl.qhimg.com/t0118a7f93cac851e9b.png)

​ 我已经包含了最常见的 HTTP关键词（`GET`、`HEAD`、`PUT`、 …）。这个语法中，我也使用了单字节的字符串，然后在后面的阶段，我使用**Radamsa**来增加这些字符串的长度。[Radamsa](https://gitlab.com/akihe/radamsa)是另一个通用[模糊](https://gitlab.com/akihe/radamsa)器，最近作为自定义 [mutator](https://github.com/AFLplusplus/AFLplusplus/issues/72)库添加到 AFL++ 中。同样，我在这里省略了大部分附加字符串，并选择将它们包含在字典中



## 四、Apache配置

​ 默认情况下，Apache HTTP 服务器是通过编辑`[install_path]/conf`文件夹中包含的文本文件来配置的。通常主配置文件被命名为`httpd.conf`，它每行包含一个指令。此外，可以使用`Include`添加其他配置文件，并且也可以使用通配符来包含许多配置文件。。反斜杠“\”可以用作一行的最后一个字符，表示指令继续到下一行，并且在反斜杠和行尾之间不能有其他字符或空格

### <a class="reference-link" name="4.1%20%E6%A8%A1%E5%9D%97%E3%80%81%E6%A8%A1%E5%9D%97%E5%92%8C%E6%9B%B4%E5%A4%9A%E6%A8%A1%E5%9D%97"></a>4.1 模块、模块和更多模块

​ Apache 具有模块化架构。您可以启用或禁用模块以添加和删除 Web 服务器功能。除了默认与 Apache HTTP 服务器捆绑的模块外，还有大量第三方模块，提供扩展功能

​ 要在 Apache 构建中启用特定模块，请在构建过程的生成配置文件阶段中使用标志`--enable-[mod]`：

```
./configure --enable-[mod]
```

​ `[mod]`中的内容我们要构建中启用的模块的名称

​ 我使用了一种**增量方法**：我从一组启用了`--enable-mods-static=few`的小模块开始，在达到稳定的模糊测试工作流程后，我启用了一个新模块并再次测试了模糊测试的稳定性。此外，我启用了`--enable-[mod]=static`和`--enable-static-support`来使得Apache模块是以静态链接的方式的构建，从而显着提高了模糊测试速度

​ 在构建步骤之后，我们可以定义这些模块应该在哪个上下文中发挥作用。为此，我修改了`httpd.conf`文件并将每个模块链接到不同且唯一的`Location`（目录或文件）。这样，我们就有了不同的服务器路径指向的不同 Apache 模块

[![](https://p1.ssl.qhimg.com/t01c732785ee2c29ded.png)](https://p1.ssl.qhimg.com/t01c732785ee2c29ded.png)

[![](https://p0.ssl.qhimg.com/t016900e543bb8a4763.png)](https://p0.ssl.qhimg.com/t016900e543bb8a4763.png)

​ 为了使模糊器的工作更轻松，我将我的`htdocs`文件夹中包含的大多数文件的文件名长度修改为1到2个字节。这使得AFL++能够更轻松猜测有效的URL请求

​ 例如：
- `GET /a HTTP 1.0`
- `POST /b HTTP 1.1`
- `HEAD /c HTTP 1.1`
在模糊测试时，我尝试启用最大数量的 Apache 模块，目的是检测模块间的并发错误



## 五、更大的字典，冲

​ 我在尝试对Apache进行模糊测试时发现了一个限制条件，AFL可以正确管理的最大字典条目数限制为 200

​ 挑战在于，对我在`httpd.conf`中包含的每个新模块及其相应位置，我还需要添加它们各自的字典条目。例如，如果我在“mod_crypto”位置添加了一个新的“scripts”文件夹，我还需要向`scripts`字典添加一个新字符串。此外，一些模块（例如，`webdav`），也需要大量的新HTTP关键词（`PROPFIND`，`PROPPATCH`等）

​ 出于这个原因，考虑到更大的字典在其他场景中也很有用，我向AFL++ 项目提交了一个[拉取请求](https://github.com/AFLplusplus/AFLplusplus/pull/519)来添加这个功能

​ 这会产生一个新的**AFL_MAX_DET_EXTRAS**环境变量，它允许我们设置以正确方式使用的最大字典条目数。你可以[在这里](https://github.com/antonio-morales/Apache-HTTP-Fuzzing/blob/main/Dictionaries/http_request_fuzzer.dict.txt)找到我使用的字典之一

​ 在本系列的第二部分，我们将展示一种更有效的方法来处理文件系统的系统调用，并介绍“文件监视器”的概念



## 六、代码更改

### <a class="reference-link" name="6.1%20MPM%E6%A8%A1%E7%B3%8A%E6%B5%8B%E8%AF%95"></a>6.1 MPM模糊测试

​ Apache HTTP Server 2.0 将其模块化设计扩展到 Web 服务器的最基本功能。服务器附带了一系列多进程处理模块 (MPM)，这些模块负责绑定到机器上的网络端口、接受请求并分派子进程来处理请求。您可以在 [https://httpd.apache.org/docs/2.4/mpm.html](https://httpd.apache.org/docs/2.4/mpm.html) 上找到有关 Apache MPM 的更多信息

​ 在基于 Unix 的操作系统中，Apache HTTP服务器默认配置**MPM 事件**，尽管我们可以通过`--with-mpm=[choice]`配置标志选择要使用的MPM版本。每个MPM模块在多线程和多进程处理方面都有不同的特性。因此，我们的模糊测试方法将因使用的MPM配置而异

​ 我对这两个配置进行了模糊测试：
- Event MPM（多进程和多线程）
- Prefork MPM（单一控制过程）
​ 在开始我们的模糊测试所需的代码更改方面，我采用了一种新方法，不是再将本地文件描述符替换套接字来提供我们的模糊测试输入。我的新方法是创建了一个的本地网络连接并通过它发送模糊测试输入（感谢<a>@n30m1nd</a>的启发！）

[![](https://p5.ssl.qhimg.com/t013deca394cb1e6eac.png)](https://p5.ssl.qhimg.com/t013deca394cb1e6eac.png)

### <a class="reference-link" name="6.2%20%E6%88%91%E4%BB%AC%E5%AF%B9%E4%BC%A0%E7%BB%9F%E4%BB%A3%E7%A0%81%E7%9A%84%E4%BF%AE%E6%94%B9"></a>6.2 我们对传统代码的修改

​ 有关有效模糊网络服务器所需的一般代码更改，请查看[之前的系列文章](https://securitylab.github.com/research/fuzzing-sockets-FreeRDP/)。但是，这里请回顾一些关于这些更改中最重要更改的摘要

​ 一般来说，这些变化可以分为：
<li>旨在减少熵的变化
<ul>
<li>用常量种子替换`random`和`rand`：[示例](https://github.com/antonio-morales/Apache_2.5.1/commit/e0be82bce715dda77841de3360f6328d26aa35cb#diff-1d0396bf58a901188f8858c71c9ba6ea2cae5c8fc480565079fb2911c45c9bbcR5659)
</li>
- 用常量种子替换`time()`、`localtime()`和`gettimeoftheday()`调用：
<li>用固定值替换`getpid()`调用：[示例](https://github.com/antonio-morales/Apache_2.5.1/commit/e0be82bce715dda77841de3360f6328d26aa35cb#diff-1d0396bf58a901188f8858c71c9ba6ea2cae5c8fc480565079fb2911c45c9bbcR5626)
</li><li>删除一些`sleep()`和`select()`调用<br>[![](https://p5.ssl.qhimg.com/t01faf59ea4d3935e4e.png)](https://p5.ssl.qhimg.com/t01faf59ea4d3935e4e.png)
</li><li>加密程序的变化：
<ul>
<li>禁用校验和：[示例](https://github.com/antonio-morales/Apache_2.5.1/commit/72a7bed52975f3258ab56a53f67b56632ddf30a2#diff-485c57a981998a7b2fb43f90f2084667358ab10beea82a0d15269564fb7eeaa3R1468)
</li>
<li>设置静态随机数：[示例](https://github.com/antonio-morales/Apache_2.5.1/commit/72a7bed52975f3258ab56a53f67b56632ddf30a2#diff-54ad55cab9d74b14dd358a112365481763d8e6f28296b56b920c198352cee37bR385)
</li>
您可以通过检查以下补丁来查看有关这些更改的所有详细信息：
- [补丁 1](https://github.com/antonio-morales/Apache-HTTP-Fuzzing/blob/main/Patches/Patch1.patch)
- [补丁2](https://github.com/antonio-morales/Apache-HTTP-Fuzzing/blob/main/Patches/Patch2.patch)


## 七、“假”错误：当你的工具欺骗你时

​ 最初在Apache HTTP 中被认为似乎是一个简单的错误，在分析后结果却变得更加复杂。我将详细介绍我在探索海森堡Bug兔子洞中的旅程，因为这是一个很好的例子，说明有时候进行根本原因的分析有时是多么令人沮丧。此外，我认为这些信息对于其他安全研究人员可能非常有用，他们可能处于相同的情况，您不确定该错误实际上存在于目标软件中还是在您的工具中

​ 当我检测到一个只能在 AFL++ 运行时重现的错误时，这个故事就开始了。当我尝试直接在 Apache 的 httpd 二进制文件上重现它时，服务器没有崩溃。在这一点上，我脑海中闪过的第一个想法是我正在处理一个非确定性错误。换句话说，一个错误只发生在 N 种情况中的一种。所以，我做的第一件事是创建一个脚本，该脚本启动应用程序 10,000 次并将其 stdout 输出重定向到一个文件。但是还是没有出现这个bug。我将执行次数增加到 100,000，但我们的错误重现仍然难以捉摸

[![](https://p2.ssl.qhimg.com/t01ad8cbc4903a32ce4.png)](https://p2.ssl.qhimg.com/t01ad8cbc4903a32ce4.png)

​ 奇怪的是，每次我在 AFL++ 下运行它时，都会一直触发该错误。所以我考虑了环境和 ASAN 的影响，这可能是我们的神秘错误的罪魁祸首。但是在对这个假设进行了数小时的深入研究后，我仍然无法找到可靠地重现错误所需的条件

·我开始怀疑我的工具可能在欺骗我，于是我决定使用 GDB 更深入地调查这个候选错误

[![](https://p5.ssl.qhimg.com/t0151f042c60dd66eee.png)](https://p5.ssl.qhimg.com/t0151f042c60dd66eee.png)

​ 这个错误产生的原因貌似是在被定义在`sanitizer_stackdepotbase.h`中的`find`函数。该文件是ASAN库的一部分，每次将新项目推入程序堆栈时都会调用该文件。但是，由于某种原因，`s`链表损坏了。结果，由于`s-&gt;link`表达式试图取消引用无效的内存地址，因此发生了段错误

​ 我可能会在ASAN库中遇到一个新的bug吗？这对我来说似乎不太可能，但随着我花更多的时间去研究漏洞，它就越来越成为一个合理的解释。好的一面是，我能学到很多关于ASAN内部的知识

​ 然而，我在试图找到链表损坏的源头时遇到了严重的困难。是Apache的错还是AFL++的错？在这一点上，我转向了[rr 调试器](https://rr-project.org/)。rr 是 Linux 的调试工具，旨在记录和重放程序执行，即所谓的反向执行调试器。rr允许我“倒退”并找到错误的根本原因

[![](https://p0.ssl.qhimg.com/t018cf7d3b0325ea72f.png)](https://p0.ssl.qhimg.com/t018cf7d3b0325ea72f.png)

​ 最后，我终于可以解释我们神秘的内存损坏bug的起源。AFL++ 使用共享内存位图来获取程序的覆盖进度。它在程序分支点插桩的代码本质上等同于：

```
cur_location = &lt;COMPILE_TIME_RANDOM&gt;;
shared_mem[cur_location ^ prev_location]++;
prev_location = cur_location &gt;&gt; 1;
```

​ 默认情况下，这个位图的大小是64kb，但是正如您在图中看到的那样，我们`guard`变量中的值为 65576 。因此在这种情况下，AFL++ fuzzer可能会溢出`__afl_area_ptr`数组，导致覆盖掉程序的内存。如果我们尝试使用小于所需的最小值的位图尺寸，AFL++ 通常会发出警报。但在我们遇到的这种特殊情况下，它并没有这样做。原因我不知道，答案要留给历史来提供了

​ 解决这个错误最终就像设置环境变量**MAP_SIZE=256000**一样简单。我希望这则轶事能帮助其他人，并提醒他们有时您的工具可能会欺骗您！



## 八、Apache 模糊测试 TL;DR

​ 对于那些喜欢直截了当（我不推介这样！）的人，以下是您自己开始对 Apache HTTP 进行模糊测试所需的知识：
- 将补丁应用到源代码：
```
patch -p2 &lt; /Patches/Patch1.patch
patch -p2 &lt; /Patches/Patch2.patch
```
- 配置和构建 Apache HTTP：
```
$ CC=afl-clang-fast CXX=afl-clang-fast++ CFLAGS="-g -fsanitize=address,undefined -fno-sanitize-recover=all" CXXFLAGS="-g -fsanitize=address,undefined -fno-sanitize-recover=all" LDFLAGS="-fsanitize=address,undefined -fno-sanitize-recover=all -lm" ./configure --prefix='/home/user/httpd-trunk/install' --with-included-apr --enable-static-support --enable-mods-static=few --disable-pie --enable-debugger-mode --with-mpm=prefork --enable-negotiation=static --enable-auth-form=static --enable-session=static --enable-request=static --enable-rewrite=static --enable-auth_digest=static --enable-deflate=static --enable-brotli=static --enable-crypto=static --with-crypto --with-openssl --enable-proxy_html=static --enable-xml2enc=static --enable-cache=static --enable-cache-disk=static --enable-data=static --enable-substitute=static --enable-ratelimit=static --enable-dav=static
$ make -j8
$ make install
```
- 运行模糊器：
```
AFL_MAP_SIZE=256000 SHOW_HOOKS=1 ASAN_OPTIONS=detect_leaks=0,abort_on_error=1,symbolize=0,debug=true,check_initialization_order=true,detect_stack_use_after_return=true,strict_string_checks=true,detect_invalid_pointer_pairs=2 AFL_DISABLE_TRIM=1 ./afl-fuzz -t 2000 -m none -i '/home/antonio/Downloads/httpd-trunk/AFL/afl_in/' -o '/home/antonio/Downloads/httpd-trunk/AFL/afl_out_40' -- '/home/antonio/Downloads/httpd-trunk/install/bin/httpd' -X @@
```
- [补丁 1](https://github.com/antonio-morales/Apache-HTTP-Fuzzing/blob/main/Patches/Patch1.patch)
- [补丁2](https://github.com/antonio-morales/Apache-HTTP-Fuzzing/blob/main/Patches/Patch2.patch)
- [Apache 示例配置](https://github.com/antonio-morales/Apache-HTTP-Fuzzing/tree/main/Conf%20Example)
- [一些输入案例示例](https://github.com/antonio-morales/Apache-HTTP-Fuzzing/tree/main/Input%20Case)
- [字典示例](https://github.com/antonio-morales/Apache-HTTP-Fuzzing/blob/main/Dictionaries/http_request_fuzzer.dict.txt)
- [自定义突变器示例](https://github.com/antonio-morales/Apache-HTTP-Fuzzing/tree/main/Custom%20mutators)
- [自定义语法示例](https://github.com/antonio-morales/Apache-HTTP-Fuzzing/blob/main/Custom%20Grammars/http.json)


## 九、待续…

请留意本系列的第二部分，在那里我将深入探讨其他有趣的模糊测试方面，例如**自定义拦截器**和**文件监视器**。我还将解释我如何设法模糊一些特殊的 mod，例如`mod_dav`或`mod_cache`

下一篇文章见！



## 参考
- [https://httpd.apache.org/docs/current/](https://httpd.apache.org/docs/current/)
- [https://animal0day.blogspot.com/2017/07/from-fuzzing-apache-httpd-server-to-cve.html](https://animal0day.blogspot.com/2017/07/from-fuzzing-apache-httpd-server-to-cve.html)
- [https://www.fuzzingbook.org/html/MutationFuzzer.htm](https://www.fuzzingbook.org/html/MutationFuzzer.htm)
- [https://github.com/AFLplusplus/AFLplusplus](https://github.com/AFLplusplus/AFLplusplus)
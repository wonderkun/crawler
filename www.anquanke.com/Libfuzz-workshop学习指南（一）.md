> 原文链接: https://www.anquanke.com//post/id/231481 


# Libfuzz-workshop学习指南（一）


                                阅读量   
                                **260202**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01bcbdd98e72bec92d.jpg)](https://p1.ssl.qhimg.com/t01bcbdd98e72bec92d.jpg)



该系列课程我们将跟随libfuzzer-workshop来学习libfuzz这个fuzz框架。该系列一共有12课，其列表如下：

1.介绍fuzz测试<br>
2.传统Fuzz技术案例<br>
3.代码覆盖率fuzz<br>
4.写fuzzers<br>
5.发现Heartbleed漏洞 (CVE-2014-0160)<br>
6.发现c-ares漏洞(CVE-2016-5180)<br>
7.如何提高fuzzer效率<br>
8.fuzz libxml2,学习如何提高fuzzer和分析性能<br>
9.fuzz libpng,学习语料库种子的重要性<br>
10.fuzz re2<br>
11.fuzz pcre2<br>
12.与chrome整合，家庭作业



## 前置知识

在项目中，我们会用到LLVM和Clang来编译程序，下面将分别介绍LLVM和Clang。

### <a class="reference-link" name="%E7%BC%96%E8%AF%91%E6%B5%81%E7%A8%8B"></a>编译流程

传统编译器基本分为三段式，前端、优化器和后端。

```
前端负责解析源代码，检查语法错误，并将其翻译为抽象的语法树；
优化器对这一中间代码进行优化，试图使代码更高效；
后端则负责将优化器优化后的中间代码转换为目标机器的代码，这一过程后端会最大化的利用目标机器的特殊指令，以提高代码的性能。
```

而我们将用到的LLVM和Clang则在编译过程中充当了前端，优化器，后端这三个责任。

### <a class="reference-link" name="llvm"></a>llvm

LLVM是一个模块化和可重用的编译器和工具链技术的集合。简单来说提供了编译过程一整套，包括前端，优化器，后端一整套流程的工具库，而又由于其高度的扩展性，可以

### <a class="reference-link" name="clang"></a>clang

clang则是llvm下的一个子项目，是一个 C、C++、Objective-C 和 Objective-C++ 编程语言的编译器前端，采用底层虚拟机（LLVM）作为后端。

### <a class="reference-link" name="LLVM%E5%92%8CClang%E7%9A%84%E5%85%B3%E7%B3%BB"></a>LLVM和Clang的关系

下图是LLVM和Clang组合编译的一种方式，可以从这种编译方式了解到LLVM和Clang的关系，既Clang作为前端，LLVM作为优化器和后端。

[![](https://p2.ssl.qhimg.com/t01d63286f08edccc66.jpg)](https://p2.ssl.qhimg.com/t01d63286f08edccc66.jpg)



## 环境搭建

1.下载ubuntu<br>[http://releases.ubuntu.com/16.04/ubuntu-16.04.7-desktop-amd64.iso](http://releases.ubuntu.com/16.04/ubuntu-16.04.7-desktop-amd64.iso)<br>
安装ubuntu,把CD和软盘切换成自动检测。

[![](https://p1.ssl.qhimg.com/t0136d2e78a82396a6e.png)](https://p1.ssl.qhimg.com/t0136d2e78a82396a6e.png)

即可在VM选项中选择安装VMWARE TOOL。当选择安装VMWARE TOOL后会在虚拟机的CD显示栏中弹出vmwaretool的磁盘光驱。解压CD中的vmwaretool到任意文件夹，运行 sudo ./vmware-install.pl,输入yes，一直回车,重启即可安装完成。

2.切换成国内源

```
sudo gedit /etc/apt/sources.list
```

```
deb http://mirrors.aliyun.com/ubuntu/ xenial main
deb-src http://mirrors.aliyun.com/ubuntu/ xenial main

deb http://mirrors.aliyun.com/ubuntu/ xenial-updates main
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-updates main

deb http://mirrors.aliyun.com/ubuntu/ xenial universe
deb-src http://mirrors.aliyun.com/ubuntu/ xenial universe
deb http://mirrors.aliyun.com/ubuntu/ xenial-updates universe
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-updates universe

deb http://mirrors.aliyun.com/ubuntu/ xenial-security main
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-security main
deb http://mirrors.aliyun.com/ubuntu/ xenial-security universe
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-security universe
```

3.下载libfuzz-workshop<br>
从[https://github.com/c0de8ug/libfuzzer-workshop.git](https://github.com/c0de8ug/libfuzzer-workshop.git) 下载压缩文件，解压缩，使用命令`./checkout_build_install_llvm.sh`，编译安装llvm和clang。



## 第一课-介绍fuzz测试

### <a class="reference-link" name="Fuzz%E6%98%AF%E4%BB%80%E4%B9%88"></a>Fuzz是什么

Fuzzing是一种软件测试技术，通常自动或者半自动，通过传递随机输入到程序中，保存程序崩溃的结果。

### <a class="reference-link" name="%E5%8D%95%E5%85%83%E6%B5%8B%E8%AF%95%E5%92%8CFuzz%E7%9A%84%E6%AF%94%E8%BE%83"></a>单元测试和Fuzz的比较

||单元测试|传统Fuzzing|现代uzzing
|------
|测试小部分代码|√|×|√
|可以自动化|√|√|√
|回归测试|√|√ / ×|√
|易写|√|×|√
|寻找新的BUG|√ / ×|√|√
|寻找漏洞|×|√|√

### <a class="reference-link" name="%E7%9B%AE%E6%A0%87-Fuzzer-%E8%AF%AD%E6%96%99%E5%BA%93"></a>目标-Fuzzer-语料库

在Fuzzing研究中，目标，Fuzzer，语料库是我们需要重点关注的内容。<br>
1.测试目标-接受输入，调用被测试代码。<br>
2.Fuzzer,一个向目标写入随机输入的工具。<br>
3.语料库，一个测试数据集合

### <a class="reference-link" name="Fuzz%E7%B1%BB%E5%9E%8B"></a>Fuzz类型

**<a class="reference-link" name="%E5%9F%BA%E4%BA%8E%E6%B5%8B%E8%AF%95%E7%94%A8%E4%BE%8B"></a>基于测试用例**

如下图所示。

[![](https://p3.ssl.qhimg.com/t01883c5056f9bf1d93.png)](https://p3.ssl.qhimg.com/t01883c5056f9bf1d93.png)

可以看到上图中生成了一个随机id为60831，而该页面会由于给document.body错误赋值导致报错。

[![](https://p5.ssl.qhimg.com/t011c50bd0025988c32.png)](https://p5.ssl.qhimg.com/t011c50bd0025988c32.png)

上图错误原因为把Iframe类型插入到了document.body,而正确应该插入BODY类型或者FRAMEST类型。或采用下图所示方式给body插入元素。

[![](https://p4.ssl.qhimg.com/t01626962260f5cb1e1.png)](https://p4.ssl.qhimg.com/t01626962260f5cb1e1.png)

**<a class="reference-link" name="%E5%9F%BA%E4%BA%8E%E5%8F%98%E5%BC%82"></a>基于变异**

可以看到下图的数据产生方式具有一定规则性，而其他部分则使用变异来完成数据的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01807ca2d239082903.png)

**<a class="reference-link" name="%E6%95%88%E6%9E%9C%E6%9B%B4%E5%A5%BD%E7%9A%84%E7%AD%96%E7%95%A5%E6%98%AF%E4%BB%80%E4%B9%88-%E7%BB%93%E5%90%88%E8%A7%84%E5%88%99%E5%92%8C%E5%AD%97%E5%85%B8%E7%94%9F%E6%88%90%E4%B8%8E%E6%A0%B9%E6%8D%AE%E4%BB%A3%E7%A0%81%E8%A6%86%E7%9B%96%E7%8E%87%E7%9A%84%E5%9B%9E%E9%A6%88%E8%BF%9B%E8%A1%8C%E5%8F%98%E5%BC%82"></a>效果更好的策略是什么-结合规则和字典生成与根据代码覆盖率的回馈进行变异**

基于规则和变异是很好的方式，但是所有的生成数据样本都有一定的局限性，例如下图的代码：

```
if(id == "xiaoming")`{`
    //漏洞触发代码
`}`
```

如果测试用例中的id的数据样本集合一直在数字这个集合变异，那么肯定测试不到存在漏洞的代码部分，那么更好的策略是什么呢？

**将规则和变异共同结合，并且增加代码覆盖率反馈**

### <a class="reference-link" name="%E4%BC%A0%E7%BB%9FFuzz%E6%8A%80%E6%9C%AF"></a>传统Fuzz技术

在过去的Fuzzing中，我们通常会按照如下流程反复运行，直到找到漏洞:<br>
1.生成一个测试样本，例如html页面<br>
2.写入磁盘<br>
3.打开浏览器<br>
4.输入这个html页面地址<br>
5.查看浏览器是否崩溃



## 第二课-传统Fuzz技术案例

本节使用 [radamsa](https://github.com/aoh/radamsa) 作为 变异样本生成引擎，对 [pdfium](https://pdfium.googlesource.com/pdfium/) 进行 fuzz。

### <a class="reference-link" name="%E5%AE%9E%E6%88%98%E5%BC%80%E5%A7%8B"></a>实战开始

使用如下命令生成测试用例（radamsa根据种子seed_corpus生成）。

```
cd lessons/02
./generate_testcases.py
```

```
#!/usr/bin/env python2
import os
import subprocess

WORK_DIR = 'work'

def checkOutput(s):
  if 'Segmentation fault' in s or 'error' in s.lower():
    return False
  else:
    return True

corpus_dir = os.path.join(WORK_DIR, 'corpus')
corpus_filenames = os.listdir(corpus_dir)

for f in corpus_filenames:
  testcase_path = os.path.join(corpus_dir, f)
  cmd = ['bin/asan/pdfium_test', testcase_path]
  process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
  output = process.communicate()[0]
  if not checkOutput(output):
    print testcase_path
    print output
    print '-' * 80
```

程序的流程为：<br>
反复调用程序处理刚刚生成的测试用例根据执行的输出结果中 是否有 `Segmentation fault 和 error`来判断是否触发了漏洞。

使用如下命令验证生成的文件,显示1000则为正确。

```
ls work/corpus/ | wc -l
```

通过下列bash反复执行命令，直到发现崩溃即可,该bash已保存为test.sh。

```
#!/bin/bash
while [ "0" -lt "1" ]
do
  rm -rf ./work/
  ./generate_testcases.py
  ./run_fuzzing.py
done
```

如果没有崩溃则反复运行，直到有如下崩溃提示则标志这里存在导致程序崩溃的Bug。

[![](https://p4.ssl.qhimg.com/t0110b49ff9402c8aa7.png)](https://p4.ssl.qhimg.com/t0110b49ff9402c8aa7.png)



## 第三课-代码覆盖率fuzzing

### <a class="reference-link" name="%E4%BC%A0%E7%BB%9Ffuzz%E6%8A%80%E6%9C%AF%E7%BC%BA%E9%99%B7"></a>传统fuzz技术缺陷

在上述的传统Fuzz方案中，我们可以看到有如下缺陷：<br>
1.样本空间搜索太耗时<br>
2.不能fuzz特定函数<br>
3.很难fuzz网络协议<br>
4.效率很低

### <a class="reference-link" name="%E6%9B%B4%E5%A5%BD%E7%9A%84Fuzz%E5%B7%A5%E5%85%B7-Libfuzz"></a>更好的Fuzz工具-Libfuzz

鉴于上述问题，引出我们本系列的重点libFuzzer。相比上述的缺点来说。Libfuzzer的优先如下：<br>
1.in-process，coverage-guided，evolutionary 的 fuzz 引擎，是 LLVM 项目的一部分。<br>
2.使用SanitizerCoverage 插桩提供来提供代码覆盖率。

### <a class="reference-link" name="%E8%A6%86%E7%9B%96%E7%8E%87%E6%8C%87%E5%AF%BC%E7%9A%84%E6%A8%A1%E7%B3%8A%E6%B5%8B%E8%AF%95"></a>覆盖率指导的模糊测试

**<a class="reference-link" name="%E5%86%85%E5%AD%98%E5%B7%A5%E5%85%B7"></a>内存工具**

下面这些工具可以提供内存错误类型检测。<br>
1.AddressSanitizer（也称为ASan），用来检测UAF，堆栈溢出等漏洞，使用已释放内存, 函数返回局部变量，全局变量越界。<br>
2.MemorySanitizer（也称为MSan），用来检测未初始化内存读漏洞。<br>
3.UndefinedBehaviorSanitizer（也称为UBSan），用来检测整数溢出，类型混淆等。


# 从零开始学习fuzzing之性能提升


                                阅读量   
                                **349659**
                            
                        |
                        
                                                                                                                                    ![](./img/202989/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者h0mbre，文章来源：h0mbre.github.io
                                <br>原文地址：[https://h0mbre.github.io/Fuzzing-Like-a-Caveman-2](https://h0mbre.github.io/Fuzzing-Like-a-Caveman-2)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/202989/t01a26895dd8cd92a0d.png)](./img/202989/t01a26895dd8cd92a0d.png)



## 前言

这篇文章主要介绍对我们之前编写的模糊测试器的性能提升，所以整体上不会有大的变化，只是对上一篇文章中已有内容的改进。这就意味着本文的重点仍旧是基于变异的模糊测试器，希望它运行的更快，并且能在其他目标文件上发现更多的漏洞。我们不会在本文中涉及多线程或多进程的问题，该问题可能会在之后的文章中提到。

我觉得有必要在这里加一个**免责声明**，因为我并不是专业的开发人员，远远不是。目前我对编程还没有足够的经验，无法像其他经验丰富的程序员那样发现代码中可以提升性能的地方。所以我会利用我的基本技能以及有限的编程知识来改进我们之前的模糊测试器，最后完成的代码可能并不漂亮，也不完美，但是会比之前的更好。

先花点时间定义一下在这篇文章中“更好”是什么意思，我想表达的是，我们可以更快地完成n次模糊测试迭代。接下来我们会重新编写模糊测试器，使用一个更酷的语言，挑选一个更困难的目标，而且之后我会使用更多的高级模糊测试技巧。

**很明显，如果你还没有阅读上一篇文章，你可能完全看不懂我在说什么。**

测试环境：

VMWare Workstation

Kali VM 1CPU 1 Core



## 模糊测试器分析

我们的上一个模糊测试器已经可以正常工作了，因为它确实在目标程序中发现了漏洞，但是在结束时我们仍然遗留了一些优化工作没有完成，现在先让我们回顾一下上一篇文章中的模糊测试器是什么样子的（出于测试目的做了一些小的修改）：

```
#!/usr/bin/env python3

import sys
import random
from pexpect import run
from pipes import quote

# read bytes from our valid JPEG and return them in a mutable bytearray 
def get_bytes(filename):

    f = open(filename, "rb").read()

    return bytearray(f)

def bit_flip(data):

    num_of_flips = int((len(data) - 4) * .01)

    indexes = range(4, (len(data) - 4))

    chosen_indexes = []

    # iterate selecting indexes until we've hit our num_of_flips number
    counter = 0
    while counter &lt; num_of_flips:
        chosen_indexes.append(random.choice(indexes))
        counter += 1

    for x in chosen_indexes:
        current = data[x]
        current = (bin(current).replace("0b",""))
        current = "0" * (8 - len(current)) + current

        indexes = range(0,8)

        picked_index = random.choice(indexes)

        new_number = []

        # our new_number list now has all the digits, example: ['1', '0', '1', '0', '1', '0', '1', '0']
        for i in current:
            new_number.append(i)

        # if the number at our randomly selected index is a 1, make it a 0, and vice versa
        if new_number[picked_index] == "1":
            new_number[picked_index] = "0"
        else:
            new_number[picked_index] = "1"

        # create our new binary string of our bit-flipped number
        current = ''
        for i in new_number:
            current += i

        # convert that string to an integer
        current = int(current,2)

        # change the number in our byte array to our new number we just constructed
        data[x] = current

    return data

def magic(data):

    magic_vals = [
    (1, 255),
    (1, 255),
    (1, 127),
    (1, 0),
    (2, 255),
    (2, 0),
    (4, 255),
    (4, 0),
    (4, 128),
    (4, 64),
    (4, 127)
    ]

    picked_magic = random.choice(magic_vals)

    length = len(data) - 8
    index = range(0, length)
    picked_index = random.choice(index)

    # here we are hardcoding all the byte overwrites for all of the tuples that begin (1, )
    if picked_magic[0] == 1:
        if picked_magic[1] == 255:            # 0xFF
            data[picked_index] = 255
        elif picked_magic[1] == 127:        # 0x7F
            data[picked_index] = 127
        elif picked_magic[1] == 0:            # 0x00
            data[picked_index] = 0

    # here we are hardcoding all the byte overwrites for all of the tuples that begin (2, )
    elif picked_magic[0] == 2:
        if picked_magic[1] == 255:            # 0xFFFF
            data[picked_index] = 255
            data[picked_index + 1] = 255
        elif picked_magic[1] == 0:            # 0x0000
            data[picked_index] = 0
            data[picked_index + 1] = 0

    # here we are hardcoding all of the byte overwrites for all of the tuples that being (4, )
    elif picked_magic[0] == 4:
        if picked_magic[1] == 255:            # 0xFFFFFFFF
            data[picked_index] = 255
            data[picked_index + 1] = 255
            data[picked_index + 2] = 255
            data[picked_index + 3] = 255
        elif picked_magic[1] == 0:            # 0x00000000
            data[picked_index] = 0
            data[picked_index + 1] = 0
            data[picked_index + 2] = 0
            data[picked_index + 3] = 0
        elif picked_magic[1] == 128:        # 0x80000000
            data[picked_index] = 128
            data[picked_index + 1] = 0
            data[picked_index + 2] = 0
            data[picked_index + 3] = 0
        elif picked_magic[1] == 64:            # 0x40000000
            data[picked_index] = 64
            data[picked_index + 1] = 0
            data[picked_index + 2] = 0
            data[picked_index + 3] = 0
        elif picked_magic[1] == 127:        # 0x7FFFFFFF
            data[picked_index] = 127
            data[picked_index + 1] = 255
            data[picked_index + 2] = 255
            data[picked_index + 3] = 255

    return data

# create new jpg with mutated data
def create_new(data):

    f = open("mutated.jpg", "wb+")
    f.write(data)
    f.close()

def exif(counter,data):

    command = "exif mutated.jpg -verbose"

    out, returncode = run("sh -c " + quote(command), withexitstatus=1)

    if b"Segmentation" in out:
        f = open("crashes2/crash.{}.jpg".format(str(counter)), "ab+")
        f.write(data)
        print("Segfault!")

    #if counter % 100 == 0:
    #    print(counter, end="r")

if len(sys.argv) &lt; 2:
    print("Usage: JPEGfuzz.py &lt;valid_jpg&gt;")

else:
    filename = sys.argv[1]
    counter = 0
    while counter &lt; 1000:
        data = get_bytes(filename)
        functions = [0, 1]
        picked_function = random.choice(functions)
        picked_function = 1
        if picked_function == 0:
            mutated = magic(data)
            create_new(mutated)
            exif(counter,mutated)
        else:
            mutated = bit_flip(data)
            create_new(mutated)
            exif(counter,mutated)

        counter += 1
```

你可能发现了一些变化，我做了以下修改：
- 注释掉了每100次迭代输出换行的代码；
- 添加print语句提醒每次的段错误；
- 硬编码1000次迭代；
- 暂时添加了一行`picked_function = 1`，在测试中只使用一种变异方法(`bit_flip()`)。
先用性能分析工具对该模糊测试器进行分析，这样我们可以知道该程序的每个部分执行要花费多少时间。

我们使用了Python中的`cProfile`模块来测试这1000次迭代中时间都花费在了哪里。如果你还记得的话，这个程序的参数是一个指向有效JPEG文件的文件路径，所有完整的命令行语法是：`python3 -m cProfile -s cumtime JPEGfuzzer.py ~/jpegs/Canon_40D.jpg`。

**还有一点要注意，添加这个`cProfile`工具可能会降低性能，但是对于本文中使用的迭代次数，是否使用该工具并不会造成明显的影响。**

执行此命令后，可以看到程序的输出以及在执行过程中花费时间最多的位置。

```
2476093 function calls (2474812 primitive calls) in 122.084 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     33/1    0.000    0.000  122.084  122.084 {built-in method builtins.exec}
        1    0.108    0.108  122.084  122.084 blog.py:3(&lt;module&gt;)
     1000    0.090    0.000  118.622    0.119 blog.py:140(exif)
     1000    0.080    0.000  118.452    0.118 run.py:7(run)
     5432  103.761    0.019  103.761    0.019 {built-in method time.sleep}
     1000    0.028    0.000  100.923    0.101 pty_spawn.py:316(close)
     1000    0.025    0.000  100.816    0.101 ptyprocess.py:387(close)
     1000    0.061    0.000    9.949    0.010 pty_spawn.py:36(__init__)
     1000    0.074    0.000    9.764    0.010 pty_spawn.py:239(_spawn)
     1000    0.041    0.000    8.682    0.009 pty_spawn.py:312(_spawnpty)
     1000    0.266    0.000    8.641    0.009 ptyprocess.py:178(spawn)
     1000    0.011    0.000    7.491    0.007 spawnbase.py:240(expect)
     1000    0.036    0.000    7.479    0.007 spawnbase.py:343(expect_list)
     1000    0.128    0.000    7.409    0.007 expect.py:91(expect_loop)
     6432    6.473    0.001    6.473    0.001 {built-in method posix.read}
     5432    0.089    0.000    3.818    0.001 pty_spawn.py:415(read_nonblocking)
     7348    0.029    0.000    3.162    0.000 utils.py:130(select_ignore_interrupts)
     7348    3.127    0.000    3.127    0.000 {built-in method select.select}
     1000    0.790    0.001    1.777    0.002 blog.py:15(bit_flip)
     1000    0.015    0.000    1.311    0.001 blog.py:134(create_new)
     1000    0.100    0.000    1.101    0.001 pty.py:79(fork)
     1000    1.000    0.001    1.000    0.001 {built-in method posix.forkpty}
-----SNIP-----
```

对于这种类型的分析来说，我们并不关心到底出现了多少段错误，因为我们并没有对变异方法进行修改，也没有比较不同的变异方法。当然这里肯定存在一些随机性，因为崩溃可能需要进行额外的处理，但目前来说这种程度的分析就够了。

我只摘录了累计花费超过1秒的输出部分，可以看到，我们在`blog.py:140(exif)`花费的时间最多，占了122秒中的118秒，所以说`exif()`函数是影响性能的主要问题。

接下来的时间花费也都与该函数直接相关，而其中大量的时间又是因为`pexpect`模块中的基本库`pty`的使用。所以接下来我们用`subprocess`模块中的`Popen`对`exit()`函数进行重写，看看性能能提升多少。

重写后的`exit()`函数：

```
def exif(counter,data):

    p = Popen(["exif", "mutated.jpg", "-verbose"], stdout=PIPE, stderr=PIPE)
    (out,err) = p.communicate()

    if p.returncode == -11:
        f = open("crashes2/crash.{}.jpg".format(str(counter)), "ab+")
        f.write(data)
        print("Segfault!")

    #if counter % 100 == 0:
    #    print(counter, end="r")
```

性能报告如下：

```
2065580 function calls (2065443 primitive calls) in 2.756 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     15/1    0.000    0.000    2.756    2.756 {built-in method builtins.exec}
        1    0.038    0.038    2.756    2.756 subpro.py:3(&lt;module&gt;)
     1000    0.020    0.000    1.917    0.002 subpro.py:139(exif)
     1000    0.026    0.000    1.121    0.001 subprocess.py:681(__init__)
     1000    0.099    0.000    1.045    0.001 subprocess.py:1412(_execute_child)
 -----SNIP-----
```

性能有了显著的提升。重写`exit()`函数的模糊测试器用2秒钟就完成了同样的工作！太疯狂了！旧版本的模糊测试器：122秒，新版本的模糊测试器：2.7秒。



## 进一步优化

接下来使用Python对模糊测试器进行进一步优化。首先，先指定一个基准线，我们对上面优化过的模糊测试器进行50,000次迭代，同时使用cProfile模块对花费时间进行测试。

```
102981395 function calls (102981258 primitive calls) in 141.488 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     15/1    0.000    0.000  141.488  141.488 {built-in method builtins.exec}
        1    1.724    1.724  141.488  141.488 subpro.py:3(&lt;module&gt;)
    50000    0.992    0.000  102.588    0.002 subpro.py:139(exif)
    50000    1.248    0.000   61.562    0.001 subprocess.py:681(__init__)
    50000    5.034    0.000   57.826    0.001 subprocess.py:1412(_execute_child)
    50000    0.437    0.000   39.586    0.001 subprocess.py:920(communicate)
    50000    2.527    0.000   39.064    0.001 subprocess.py:1662(_communicate)
   208254   37.508    0.000   37.508    0.000 {built-in method posix.read}
   158238    0.577    0.000   28.809    0.000 selectors.py:402(select)
   158238   28.131    0.000   28.131    0.000 {method 'poll' of 'select.poll' objects}
    50000   11.784    0.000   25.819    0.001 subpro.py:14(bit_flip)
  7950000    3.666    0.000   10.431    0.000 random.py:256(choice)
    50000    8.421    0.000    8.421    0.000 {built-in method _posixsubprocess.fork_exec}
    50000    0.162    0.000    7.358    0.000 subpro.py:133(create_new)
  7950000    4.096    0.000    6.130    0.000 random.py:224(_randbelow)
   203090    5.016    0.000    5.016    0.000 {built-in method io.open}
    50000    4.211    0.000    4.211    0.000 {method 'close' of '_io.BufferedRandom' objects}
    50000    1.643    0.000    4.194    0.000 os.py:617(get_exec_path)
    50000    1.733    0.000    3.356    0.000 subpro.py:8(get_bytes)
 35866791    2.635    0.000    2.635    0.000 {method 'append' of 'list' objects}
   100000    0.070    0.000    1.960    0.000 subprocess.py:1014(wait)
   100000    0.252    0.000    1.902    0.000 selectors.py:351(register)
   100000    0.444    0.000    1.890    0.000 subprocess.py:1621(_wait)
   100000    0.675    0.000    1.583    0.000 selectors.py:234(register)
   350000    0.432    0.000    1.501    0.000 subprocess.py:1471(&lt;genexpr&gt;)
 12074141    1.434    0.000    1.434    0.000 {method 'getrandbits' of '_random.Random' objects}
    50000    0.059    0.000    1.358    0.000 subprocess.py:1608(_try_wait)
    50000    1.299    0.000    1.299    0.000 {built-in method posix.waitpid}
   100000    0.488    0.000    1.058    0.000 os.py:674(__getitem__)
   100000    1.017    0.000    1.017    0.000 {method 'close' of '_io.BufferedReader' objects}
-----SNIP-----
```

50,000次迭代总共花费了141秒的时间，和我们处理的问题比起来这已经是一个很高的性能了，因为之前我们做1000次迭代就花费了122秒。同样，这次的结果也只包括超过1秒钟的输出，可以看到大部分时间仍然花费在了`exif()`函数上，不过在`bit_flip()`函数上也存在一些性能问题，在这个函数上我们总共花费了25秒的时间，现在我们尝试对这个函数进行优化。

首先回顾之前的`bit_flip()`是什么样子的：

```
def bit_flip(data):

    num_of_flips = int((len(data) - 4) * .01)

    indexes = range(4, (len(data) - 4))

    chosen_indexes = []

    # iterate selecting indexes until we've hit our num_of_flips number
    counter = 0
    while counter &lt; num_of_flips:
        chosen_indexes.append(random.choice(indexes))
        counter += 1

    for x in chosen_indexes:
        current = data[x]
        current = (bin(current).replace("0b",""))
        current = "0" * (8 - len(current)) + current

        indexes = range(0,8)

        picked_index = random.choice(indexes)

        new_number = []

        # our new_number list now has all the digits, example: ['1', '0', '1', '0', '1', '0', '1', '0']
        for i in current:
            new_number.append(i)

        # if the number at our randomly selected index is a 1, make it a 0, and vice versa
        if new_number[picked_index] == "1":
            new_number[picked_index] = "0"
        else:
            new_number[picked_index] = "1"

        # create our new binary string of our bit-flipped number
        current = ''
        for i in new_number:
            current += i

        # convert that string to an integer
        current = int(current,2)

        # change the number in our byte array to our new number we just constructed
        data[x] = current

    return data
```

这个函数写得确实不太好，通过优化逻辑关系就可以极大的简化该函数。在我有限的编程经验中，经常会发现这样的问题，你可能学会了很多深奥的编程知识，但是如果程序背后的逻辑不健全，那么程序的性能会受到很大影响。

首先简化类型转换的次数，比如说整型数和字符串之间的相互转化，之后缩减代码行数。重写的`bit_flip()`函数如下：

```
def bit_flip(data):

    length = len(data) - 4

    num_of_flips = int(length * .01)

    picked_indexes = []

    counter = 0
    while counter &lt; num_of_flips:
        picked_indexes.append(random.choice(range(0,length)))
        counter += 1


    for x in picked_indexes:
        mask = random.choice(range(1,9))
        data[x] = data[x] ^ mask

    return data
```

性能分析结果：

```
59376275 function calls (59376138 primitive calls) in 135.582 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     15/1    0.000    0.000  135.582  135.582 {built-in method builtins.exec}
        1    1.940    1.940  135.582  135.582 subpro.py:3(&lt;module&gt;)
    50000    0.978    0.000  107.857    0.002 subpro.py:111(exif)
    50000    1.450    0.000   64.236    0.001 subprocess.py:681(__init__)
    50000    5.566    0.000   60.141    0.001 subprocess.py:1412(_execute_child)
    50000    0.534    0.000   42.259    0.001 subprocess.py:920(communicate)
    50000    2.827    0.000   41.637    0.001 subprocess.py:1662(_communicate)
   199549   38.249    0.000   38.249    0.000 {built-in method posix.read}
   149537    0.555    0.000   30.376    0.000 selectors.py:402(select)
   149537   29.722    0.000   29.722    0.000 {method 'poll' of 'select.poll' objects}
    50000    3.993    0.000   14.471    0.000 subpro.py:14(bit_flip)
  7950000    3.741    0.000   10.316    0.000 random.py:256(choice)
    50000    9.973    0.000    9.973    0.000 {built-in method _posixsubprocess.fork_exec}
    50000    0.163    0.000    7.034    0.000 subpro.py:105(create_new)
  7950000    3.987    0.000    5.952    0.000 random.py:224(_randbelow)
   202567    4.966    0.000    4.966    0.000 {built-in method io.open}
    50000    4.042    0.000    4.042    0.000 {method 'close' of '_io.BufferedRandom' objects}
    50000    1.539    0.000    3.828    0.000 os.py:617(get_exec_path)
    50000    1.843    0.000    3.607    0.000 subpro.py:8(get_bytes)
   100000    0.074    0.000    2.133    0.000 subprocess.py:1014(wait)
   100000    0.463    0.000    2.059    0.000 subprocess.py:1621(_wait)
   100000    0.274    0.000    2.046    0.000 selectors.py:351(register)
   100000    0.782    0.000    1.702    0.000 selectors.py:234(register)
    50000    0.055    0.000    1.507    0.000 subprocess.py:1608(_try_wait)
    50000    1.452    0.000    1.452    0.000 {built-in method posix.waitpid}
   350000    0.424    0.000    1.436    0.000 subprocess.py:1471(&lt;genexpr&gt;)
 12066317    1.339    0.000    1.339    0.000 {method 'getrandbits' of '_random.Random' objects}
   100000    0.466    0.000    1.048    0.000 os.py:674(__getitem__)
   100000    1.014    0.000    1.014    0.000 {method 'close' of '_io.BufferedReader' objects}
-----SNIP-----
```

从输出结果中可以看到，`bit_flip()`函数总共仅花费了14秒钟，而上一次花费了25秒，几乎是现在的两倍，在我看来优化的结果很不错。

既然现在已经有了python的基准线（注意目前还没有使用多线程或多进程，我们会在之后的文章中讲到），现在我们把模糊测试器移植到一个新的语言——C++上，测试一下它的性能。



## 使用C++编写模糊测试器

在此之前，先对最新版本的python模糊测试器进行100,000次迭代，看看总共花费多长时间。

```
118749892 function calls (118749755 primitive calls) in 256.881 seconds
```

100k的迭代只花费了256秒，打败了我们之前所有的模糊测试器。

这个值会作为接下来C++的判断基准。我对python开发中的细节并不熟悉，现在把这个不熟悉的程度x10，就是我对C++的不熟悉度，下面的代码对一些人来说可能很可笑，但这已经是我目前能做到的最好的程度了。我会对其中的每个函数进行解释，这些函数和之前的python代码也相互对应。

接下来我们对各个函数进行逐一介绍，并给出实现代码。

```
//
// this function simply creates a stream by opening a file in binary mode;
// finds the end of file, creates a string 'data', resizes data to be the same
// size as the file moves the file pointer back to the beginning of the file;
// reads the data from the into the data string;
//
std::string get_bytes(std::string filename)
{
    std::ifstream fin(filename, std::ios::binary);

    if (fin.is_open())
    {
        fin.seekg(0, std::ios::end);
        std::string data;
        data.resize(fin.tellg());
        fin.seekg(0, std::ios::beg);
        fin.read(&amp;data[0], data.size());

        return data;
    }

    else
    {
        std::cout &lt;&lt; "Failed to open " &lt;&lt; filename &lt;&lt; ".n";
        exit(1);
    }

}
```

正如注释中所说，该函数从目标文件中提取出字节数据并放入字符串中，在此例中，目标文件为`Canon_40D.jpg`。

```
//
// this will take 1% of the bytes from our valid jpeg and
// flip a random bit in the byte and return the altered string
//
std::string bit_flip(std::string data)
{

    int size = (data.length() - 4);
    int num_of_flips = (int)(size * .01);

    // get a vector full of 1% of random byte indexes
    std::vector&lt;int&gt; picked_indexes;
    for (int i = 0; i &lt; num_of_flips; i++)
    {
        int picked_index = rand() % size;
        picked_indexes.push_back(picked_index);
    }

    // iterate through the data string at those indexes and flip a bit
    for (int i = 0; i &lt; picked_indexes.size(); ++i)
    {
        int index = picked_indexes[i];
        char current = data.at(index);
        int decimal = ((int)current &amp; 0xff);

        int bit_to_flip = rand() % 8;

        decimal ^= 1 &lt;&lt; bit_to_flip;
        decimal &amp;= 0xff;

        data[index] = (char)decimal;
    }

    return data;

}
```

该函数与python脚本中的`bit_flip()`函数相同。

```
//
// takes mutated string and creates new jpeg with it;
//
void create_new(std::string mutated)
{
    std::ofstream fout("mutated.jpg", std::ios::binary);

    if (fout.is_open())
    {
        fout.seekp(0, std::ios::beg);
        fout.write(&amp;mutated[0], mutated.size());
    }
    else
    {
        std::cout &lt;&lt; "Failed to create mutated.jpg" &lt;&lt; ".n";
        exit(1);
    }

}
```

该函数会创建一个临时的`mutated.jpg`文件，与python脚本中的`create_new()`相对应。

```
//
// function to run a system command and store the output as a string;
// https://www.jeremymorgan.com/tutorials/c-programming/how-to-capture-the-output-of-a-linux-command-in-c/
//
std::string get_output(std::string cmd)
{
    std::string output;
    FILE * stream;
    char buffer[256];

    stream = popen(cmd.c_str(), "r");
    if (stream)
    {
        while (!feof(stream))
            if (fgets(buffer, 256, stream) != NULL) output.append(buffer);
                pclose(stream);
    }

    return output;

}

//
// we actually run our exiv2 command via the get_output() func;
// retrieve the output in the form of a string and then we can parse the string;
// we'll save all the outputs that result in a segfault or floating point except;
//
void exif(std::string mutated, int counter)
{
    std::string command = "exif mutated.jpg -verbose 2&gt;&amp;1";

    std::string output = get_output(command);

    std::string segfault = "Segmentation";
    std::string floating_point = "Floating";

    std::size_t pos1 = output.find(segfault);
    std::size_t pos2 = output.find(floating_point);

    if (pos1 != -1)
    {
        std::cout &lt;&lt; "Segfault!n";
        std::ostringstream oss;
        oss &lt;&lt; "/root/cppcrashes/crash." &lt;&lt; counter &lt;&lt; ".jpg";
        std::string filename = oss.str();
        std::ofstream fout(filename, std::ios::binary);

        if (fout.is_open())
            {
                fout.seekp(0, std::ios::beg);
                fout.write(&amp;mutated[0], mutated.size());
            }
        else
        {
            std::cout &lt;&lt; "Failed to create " &lt;&lt; filename &lt;&lt; ".jpg" &lt;&lt; ".n";
            exit(1);
        }
    }
    else if (pos2 != -1)
    {
        std::cout &lt;&lt; "Floating Point!n";
        std::ostringstream oss;
        oss &lt;&lt; "/root/cppcrashes/crash." &lt;&lt; counter &lt;&lt; ".jpg";
        std::string filename = oss.str();
        std::ofstream fout(filename, std::ios::binary);

        if (fout.is_open())
            {
                fout.seekp(0, std::ios::beg);
                fout.write(&amp;mutated[0], mutated.size());
            }
        else
        {
            std::cout &lt;&lt; "Failed to create " &lt;&lt; filename &lt;&lt; ".jpg" &lt;&lt; ".n";
            exit(1);
        }
    }
}
```

这两个函数在一起工作，`get_output`将一个字符串作为参数，执行该命令，获取输出结果，然后把该输出结果传递给`exif()`函数。

`exif()`函数拿到输出结果后，查看是否有`Segmentation fault`或者`Floating point exception`错误，如果有，就将字节数据写入到文件中，并命名为`crash.&lt;counter&gt;.jpg`，这段过程和python脚本中的过程很像。

```
//
// simply generates a vector of strings that are our 'magic' values;
//
std::vector&lt;std::string&gt; vector_gen()
{
    std::vector&lt;std::string&gt; magic;

    using namespace std::string_literals;

    magic.push_back("xff");
    magic.push_back("x7f");
    magic.push_back("x00"s);
    magic.push_back("xffxff");
    magic.push_back("x7fxff");
    magic.push_back("x00x00"s);
    magic.push_back("xffxffxffxff");
    magic.push_back("x80x00x00x00"s);
    magic.push_back("x40x00x00x00"s);
    magic.push_back("x7fxffxffxff");

    return magic;
}

//
// randomly picks a magic value from the vector and overwrites that many bytes in the image;
//
std::string magic(std::string data, std::vector&lt;std::string&gt; magic)
{

    int vector_size = magic.size();
    int picked_magic_index = rand() % vector_size;
    std::string picked_magic = magic[picked_magic_index];
    int size = (data.length() - 4);
    int picked_data_index = rand() % size;
    data.replace(picked_data_index, magic[picked_magic_index].length(), magic[picked_magic_index]);

    return data;

}

//
// returns 0 or 1;
//
int func_pick()
{
    int result = rand() % 2;

    return result;
}
```

这几个函数也类似python脚本中的函数。`vector_gen()`创建了magic number向量，接下来的`magic()`函数随机选取一个索引值，用该索引位置的magic number覆盖原始JPEG文件中的数据。

`func_pick()`函数很简单，就是返回一个`0`或者`1`，这样模糊测试器可以随机使用`bit_flip()`变异方法或者`magic()`变异方法。为了与python脚本保持一致性，在测试时我们只使用`bit_flip()`方法，在代码中临时加一句`function = 1`。

`main()`函数如下：

```
int main(int argc, char** argv)
{

    if (argc &lt; 3)
    {
        std::cout &lt;&lt; "Usage: ./cppfuzz &lt;valid jpeg&gt; &lt;number_of_fuzzing_iterations&gt;n";
        std::cout &lt;&lt; "Usage: ./cppfuzz Canon_40D.jpg 10000n";
        return 1;
    }

    // start timer
    auto start = std::chrono::high_resolution_clock::now();

    // initialize our random seed
    srand((unsigned)time(NULL));

    // generate our vector of magic numbers
    std::vector&lt;std::string&gt; magic_vector = vector_gen();

    std::string filename = argv[1];
    int iterations = atoi(argv[2]);

    int counter = 0;
    while (counter &lt; iterations)
    {

        std::string data = get_bytes(filename);

        int function = func_pick();
        function = 1;
        if (function == 0)
        {
            // utilize the magic mutation method; create new jpg; send to exiv2
            std::string mutated = magic(data, magic_vector);
            create_new(mutated);
            exif(mutated,counter);
            counter++;
        }
        else
        {
            // utilize the bit flip mutation; create new jpg; send to exiv2
            std::string mutated = bit_flip(data);
            create_new(mutated);
            exif(mutated,counter);
            counter++;
        }
    }

    // stop timer and print execution time
    auto stop = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast&lt;std::chrono::milliseconds&gt;(stop - start);
    std::cout &lt;&lt; "Execution Time: " &lt;&lt; duration.count() &lt;&lt; "msn";

    return 0;
}
```

首先从命令行获取要进行变异的JPEG图像以及模糊测试的迭代数，然后使用`std::chrono`中的函数建立了一个计时机制，计算程序执行所花费的时间。

因为Python脚本中只使用了`bit_flip()`变异方法，我们希望两者保持一致，所以在这里也只使用了该方法。

接下来进行100,000次迭代，记录运行时间，与Python模糊测试器的基准线256秒作比较。

我运行了这个C++版本的模糊测试器，获得输出：`Execution Time: 172638ms`，即172秒。

很明显，C++版本的模糊测试器很轻松的打败了Python版本的模糊测试器。172/256=67%，也就是说，C++的实现版本快了大概33%。

现在我们已经有了两个语言版本的模糊测试器，是时候设定一个新的目标文件了！



## 选择新的目标文件

我们先看一下Kali Linux里面都预安装了哪些软件，我在`/usr/bin/`中找到了一个`exiv2`程序：

```
root@kali:~# exiv2 -h
Usage: exiv2 [ options ] [ action ] file ...

Manipulate the Exif metadata of images.

Actions:
  ad | adjust   Adjust Exif timestamps by the given time. This action
                requires at least one of the -a, -Y, -O or -D options.
  pr | print    Print image metadata.
  rm | delete   Delete image metadata from the files.
  in | insert   Insert metadata from corresponding *.exv files.
                Use option -S to change the suffix of the input files.
  ex | extract  Extract metadata to *.exv, *.xmp and thumbnail image files.
  mv | rename   Rename files and/or set file timestamps according to the
                Exif create timestamp. The filename format can be set with
                -r format, timestamp options are controlled with -t and -T.
  mo | modify   Apply commands to modify (add, set, delete) the Exif and
                IPTC metadata of image files or set the JPEG comment.
                Requires option -c, -m or -M.
  fi | fixiso   Copy ISO setting from the Nikon Makernote to the regular
                Exif tag.
  fc | fixcom   Convert the UNICODE Exif user comment to UCS-2. Its current
                character encoding can be specified with the -n option.

Options:
   -h      Display this help and exit.
   -V      Show the program version and exit.
   -v      Be verbose during the program run.
   -q      Silence warnings and error messages during the program run (quiet).
   -Q lvl  Set log-level to d(ebug), i(nfo), w(arning), e(rror) or m(ute).
   -b      Show large binary values.
   -u      Show unknown tags.
   -g key  Only output info for this key (grep).
   -K key  Only output info for this key (exact match).
   -n enc  Charset to use to decode UNICODE Exif user comments.
   -k      Preserve file timestamps (keep).
   -t      Also set the file timestamp in 'rename' action (overrides -k).
   -T      Only set the file timestamp in 'rename' action, do not rename
           the file (overrides -k).
   -f      Do not prompt before overwriting existing files (force).
   -F      Do not prompt before renaming files (Force).
   -a time Time adjustment in the format [-]HH[:MM[:SS]]. This option
           is only used with the 'adjust' action.
   -Y yrs  Year adjustment with the 'adjust' action.
   -O mon  Month adjustment with the 'adjust' action.
   -D day  Day adjustment with the 'adjust' action.
   -p mode Print mode for the 'print' action. Possible modes are:
             s : print a summary of the Exif metadata (the default)
             a : print Exif, IPTC and XMP metadata (shortcut for -Pkyct)
             t : interpreted (translated) Exif data (-PEkyct)
             v : plain Exif data values (-PExgnycv)
             h : hexdump of the Exif data (-PExgnycsh)
             i : IPTC data values (-PIkyct)
             x : XMP properties (-PXkyct)
             c : JPEG comment
             p : list available previews
             S : print structure of image
             X : extract XMP from image
   -P flgs Print flags for fine control of tag lists ('print' action):
             E : include Exif tags in the list
             I : IPTC datasets
             X : XMP properties
             x : print a column with the tag number
             g : group name
             k : key
             l : tag label
             n : tag name
             y : type
             c : number of components (count)
             s : size in bytes
             v : plain data value
             t : interpreted (translated) data
             h : hexdump of the data
   -d tgt  Delete target(s) for the 'delete' action. Possible targets are:
             a : all supported metadata (the default)
             e : Exif section
             t : Exif thumbnail only
             i : IPTC data
             x : XMP packet
             c : JPEG comment
   -i tgt  Insert target(s) for the 'insert' action. Possible targets are
           the same as those for the -d option, plus a modifier:
             X : Insert metadata from an XMP sidecar file &lt;file&gt;.xmp
           Only JPEG thumbnails can be inserted, they need to be named
           &lt;file&gt;-thumb.jpg
   -e tgt  Extract target(s) for the 'extract' action. Possible targets
           are the same as those for the -d option, plus a target to extract
           preview images and a modifier to generate an XMP sidecar file:
             p[&lt;n&gt;[,&lt;m&gt; ...]] : Extract preview images.
             X : Extract metadata to an XMP sidecar file &lt;file&gt;.xmp
   -r fmt  Filename format for the 'rename' action. The format string
           follows strftime(3). The following keywords are supported:
             :basename:   - original filename without extension
             :dirname:    - name of the directory holding the original file
             :parentname: - name of parent directory
           Default filename format is %Y%m%d_%H%M%S.
   -c txt  JPEG comment string to set in the image.
   -m file Command file for the modify action. The format for commands is
           set|add|del &lt;key&gt; [[&lt;type&gt;] &lt;value&gt;].
   -M cmd  Command line for the modify action. The format for the
           commands is the same as that of the lines of a command file.
   -l dir  Location (directory) for files to be inserted from or extracted to.
   -S .suf Use suffix .suf for source files for insert command.
```

`pr`表示输出图像元数据，`-v`表示输出详细信息，从帮助信息中还可以发现很多攻击面，但目前我们先考虑最简单的情况。

所以现在进行模糊测试的命令行字符串应该类似于`exiv2 pr -v mutated.jpg`。

现在可以看看我们的模糊测试器能不能在这个新选择的目标上发现漏洞了，需要注意的是，我们新选择的这个目标程序仍然在支持维护中，不像上一个目标，在Github上已经有7年没更新了，因此很容易发现漏洞。

已经有很多高级的模糊测试器对这个新的目标进行过测试了，在谷歌上搜索’ASan exiv2’，你可以找到很多模糊测试器在该二进制文件中发现的段错误，以及作为漏洞报告传给项目的ASan输出结果。所以说和我们上一次选择的目标文件相比，这次的选择是一个很大的挑战。

[exiv2 on Github](https://github.com/Exiv2/exiv2)

[exiv2 Website](https://www.exiv2.org/)



## 对新目标进行模糊测试

先使用Python版本的模糊测试器，测试它在50,000次迭代时的性能，这里我们加了一些新的代码，除了要监控`Segmentation fault`之外，还监控了`Floating point exceptions`，新的`exif()`函数如下所示：

```
def exif(counter,data):

    p = Popen(["exiv2", "pr", "-v", "mutated.jpg"], stdout=PIPE, stderr=PIPE)
    (out,err) = p.communicate()

    if p.returncode == -11:
        f = open("crashes2/crash.{}.jpg".format(str(counter)), "ab+")
        f.write(data)
        print("Segfault!")

    elif p.returncode == -8:
        f = open("crashes2/crash.{}.jpg".format(str(counter)), "ab+")
        f.write(data)
        print("Floating Point!")
```

`python3 -m cProfile -s cumtime subpro.py ~/jpegs/Canon_40D.jpg`的输出结果：

```
75780446 function calls (75780309 primitive calls) in 213.595 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     15/1    0.000    0.000  213.595  213.595 {built-in method builtins.exec}
        1    1.481    1.481  213.595  213.595 subpro.py:3(&lt;module&gt;)
    50000    0.818    0.000  187.205    0.004 subpro.py:111(exif)
    50000    0.543    0.000  143.499    0.003 subprocess.py:920(communicate)
    50000    6.773    0.000  142.873    0.003 subprocess.py:1662(_communicate)
  1641352    3.186    0.000  122.668    0.000 selectors.py:402(select)
  1641352  118.799    0.000  118.799    0.000 {method 'poll' of 'select.poll' objects}
    50000    1.220    0.000   42.888    0.001 subprocess.py:681(__init__)
    50000    4.400    0.000   39.364    0.001 subprocess.py:1412(_execute_child)
  1691919   25.759    0.000   25.759    0.000 {built-in method posix.read}
    50000    3.863    0.000   13.938    0.000 subpro.py:14(bit_flip)
  7950000    3.587    0.000    9.991    0.000 random.py:256(choice)
    50000    7.495    0.000    7.495    0.000 {built-in method _posixsubprocess.fork_exec}
    50000    0.148    0.000    7.081    0.000 subpro.py:105(create_new)
  7950000    3.884    0.000    5.764    0.000 random.py:224(_randbelow)
   200000    4.582    0.000    4.582    0.000 {built-in method io.open}
    50000    4.192    0.000    4.192    0.000 {method 'close' of '_io.BufferedRandom' objects}
    50000    1.339    0.000    3.612    0.000 os.py:617(get_exec_path)
    50000    1.641    0.000    3.309    0.000 subpro.py:8(get_bytes)
   100000    0.077    0.000    1.822    0.000 subprocess.py:1014(wait)
   100000    0.432    0.000    1.746    0.000 subprocess.py:1621(_wait)
   100000    0.256    0.000    1.735    0.000 selectors.py:351(register)
   100000    0.619    0.000    1.422    0.000 selectors.py:234(register)
   350000    0.380    0.000    1.402    0.000 subprocess.py:1471(&lt;genexpr&gt;)
 12066004    1.335    0.000    1.335    0.000 {method 'getrandbits' of '_random.Random' objects}
    50000    0.063    0.000    1.222    0.000 subprocess.py:1608(_try_wait)
    50000    1.160    0.000    1.160    0.000 {built-in method posix.waitpid}
   100000    0.519    0.000    1.143    0.000 os.py:674(__getitem__)
  1691352    0.902    0.000    1.097    0.000 selectors.py:66(__len__)
  7234121    1.023    0.000    1.023    0.000 {method 'append' of 'list' objects}
-----SNIP-----
```

总共花费了213秒，并没有找到任何漏洞。接下来在完全相同的情况下运行C++版本的模糊测试器，查看其输出结果。

在花费时间上有了一定的改进：

```
root@kali:~# ./blogcpp ~/jpegs/Canon_40D.jpg 50000
Execution Time: 170829ms
```

快了43秒，和Python相比提升了20%。

接下来让这个C++版本的模糊测试器运行一会，看看是否能找到什么漏洞 :)。



## 新目标上的漏洞！

在大概运行了10秒钟之后，我在终端上收到了下面的信息：

```
root@kali:~# ./blogcpp ~/jpegs/Canon_40D.jpg 1000000
Floating Point!
```

看起来我们找了一个`Floating Point exception`，所以现在`cppcrashes文件夹中应该已经有一个JPEG文件等着我们了。

```
root@kali:~/cppcrashes# ls
crash.522.jpg
```

处于验证的目的，我们再使用`exiv2`测试一下这张图片：

```
root@kali:~/cppcrashes# exiv2 pr -v crash.522.jpg
File 1/1: crash.522.jpg
Error: Offset of directory Image, entry 0x011b is out of bounds: Offset = 0x080000ae; truncating the entry
Warning: Directory Image, entry 0x8825 has unknown Exif (TIFF) type 68; setting type size 1.
Warning: Directory Image, entry 0x8825 doesn't look like a sub-IFD.
File name       : crash.522.jpg
File size       : 7958 Bytes
MIME type       : image/jpeg
Image size      : 100 x 68
Camera make     : Aanon
Camera model    : Canon EOS 40D
Image timestamp : 2008:05:30 15:56:01
Image number    : 
Exposure time   : 1/160 s
Aperture        : F7.1
Floating point exception

```

看来我们确实找到了一个漏洞！太让人兴奋了，我们应该在Github上向`exiv2`的开发人云报告这个漏洞。



## 结论

在本文中，我们首先对Python版本的模糊测试器进行了优化，之后编写了C++版本的模糊测试器，在性能上获得了很大的提升，甚至在新的目标上发现了新的漏洞。

只是出于好奇，我测试了一下原始版本的模糊测试器进行50,000次迭代耗费的时间：

```
123052109 function calls (123001828 primitive calls) in 6243.939 seconds
```

花费了6243秒，和C++版本的170秒相比真的是太慢了。

在之后的文章中（可能要过一段时间），我们会再次使用Rust，在Windows内核模式的设备驱动程序上进行模糊测试。



## 代码

### <a class="reference-link" name="OptimizedFuzzer.py"></a>OptimizedFuzzer.py

```
#!/usr/bin/env python3

import sys
import random
from subprocess import Popen,PIPE

# read bytes from our valid JPEG and return them in a mutable bytearray 
def get_bytes(filename):

    f = open(filename, "rb").read()

    return bytearray(f)

def bit_flip(data):

    length = len(data) - 4

    num_of_flips = int(length * .01)

    picked_indexes = []

    counter = 0
    while counter &lt; num_of_flips:
        picked_indexes.append(random.choice(range(0,length)))
        counter += 1


    for x in picked_indexes:
        mask = random.choice(range(1,9))
        data[x] = data[x] ^ mask

    return data

def magic(data):

    magic_vals = [
    (1, 255),
    (1, 255),
    (1, 127),
    (1, 0),
    (2, 255),
    (2, 0),
    (4, 255),
    (4, 0),
    (4, 128),
    (4, 64),
    (4, 127)
    ]

    picked_magic = random.choice(magic_vals)

    length = len(data) - 8
    index = range(0, length)
    picked_index = random.choice(index)

    # here we are hardcoding all the byte overwrites for all of the tuples that begin (1, )
    if picked_magic[0] == 1:
        if picked_magic[1] == 255:            # 0xFF
            data[picked_index] = 255
        elif picked_magic[1] == 127:        # 0x7F
            data[picked_index] = 127
        elif picked_magic[1] == 0:            # 0x00
            data[picked_index] = 0

    # here we are hardcoding all the byte overwrites for all of the tuples that begin (2, )
    elif picked_magic[0] == 2:
        if picked_magic[1] == 255:            # 0xFFFF
            data[picked_index] = 255
            data[picked_index + 1] = 255
        elif picked_magic[1] == 0:            # 0x0000
            data[picked_index] = 0
            data[picked_index + 1] = 0

    # here we are hardcoding all of the byte overwrites for all of the tuples that being (4, )
    elif picked_magic[0] == 4:
        if picked_magic[1] == 255:            # 0xFFFFFFFF
            data[picked_index] = 255
            data[picked_index + 1] = 255
            data[picked_index + 2] = 255
            data[picked_index + 3] = 255
        elif picked_magic[1] == 0:            # 0x00000000
            data[picked_index] = 0
            data[picked_index + 1] = 0
            data[picked_index + 2] = 0
            data[picked_index + 3] = 0
        elif picked_magic[1] == 128:        # 0x80000000
            data[picked_index] = 128
            data[picked_index + 1] = 0
            data[picked_index + 2] = 0
            data[picked_index + 3] = 0
        elif picked_magic[1] == 64:            # 0x40000000
            data[picked_index] = 64
            data[picked_index + 1] = 0
            data[picked_index + 2] = 0
            data[picked_index + 3] = 0
        elif picked_magic[1] == 127:        # 0x7FFFFFFF
            data[picked_index] = 127
            data[picked_index + 1] = 255
            data[picked_index + 2] = 255
            data[picked_index + 3] = 255

    return data

# create new jpg with mutated data
def create_new(data):

    f = open("mutated.jpg", "wb+")
    f.write(data)
    f.close()

def exif(counter,data):

    p = Popen(["exiv2", "pr", "-v", "mutated.jpg"], stdout=PIPE, stderr=PIPE)
    (out,err) = p.communicate()

    if p.returncode == -11:
        f = open("crashes2/crash.{}.jpg".format(str(counter)), "ab+")
        f.write(data)
        print("Segfault!")

    elif p.returncode == -8:
        f = open("crashes2/crash.{}.jpg".format(str(counter)), "ab+")
        f.write(data)
        print("Floating Point!")

    #if counter % 100 == 0:
    #    print(counter, end="r")

if len(sys.argv) &lt; 2:
    print("Usage: JPEGfuzz.py &lt;valid_jpg&gt;")

else:
    filename = sys.argv[1]
    counter = 0
    while counter &lt; 50000:
        data = get_bytes(filename)
        functions = [0, 1]
        picked_function = random.choice(functions)
        picked_function = 1
        if picked_function == 0:
            mutated = magic(data)
            create_new(mutated)
            exif(counter,mutated)
        else:
            mutated = bit_flip(data)
            create_new(mutated)
            exif(counter,mutated)

        counter += 1
```

### <a class="reference-link" name="CPPFuzz.cpp"></a>CPPFuzz.cpp

```
#include &lt;iostream&gt;
#include &lt;fstream&gt;
#include &lt;vector&gt;
#include &lt;chrono&gt;
#include &lt;memory&gt;
#include &lt;string&gt;
#include &lt;sstream&gt;
#include &lt;cstdlib&gt;
#include &lt;bits/stdc++.h&gt; 

//
// this function simply creates a stream by opening a file in binary mode;
// finds the end of file, creates a string 'data', resizes data to be the same
// size as the file moves the file pointer back to the beginning of the file;
// reads the data from the into the data string;
//
std::string get_bytes(std::string filename)
{
    std::ifstream fin(filename, std::ios::binary);

    if (fin.is_open())
    {
        fin.seekg(0, std::ios::end);
        std::string data;
        data.resize(fin.tellg());
        fin.seekg(0, std::ios::beg);
        fin.read(&amp;data[0], data.size());

        return data;
    }

    else
    {
        std::cout &lt;&lt; "Failed to open " &lt;&lt; filename &lt;&lt; ".n";
        exit(1);
    }

}

//
// this will take 1% of the bytes from our valid jpeg and
// flip a random bit in the byte and return the altered string
//
std::string bit_flip(std::string data)
{

    int size = (data.length() - 4);
    int num_of_flips = (int)(size * .01);

    // get a vector full of 1% of random byte indexes
    std::vector&lt;int&gt; picked_indexes;
    for (int i = 0; i &lt; num_of_flips; i++)
    {
        int picked_index = rand() % size;
        picked_indexes.push_back(picked_index);
    }

    // iterate through the data string at those indexes and flip a bit
    for (int i = 0; i &lt; picked_indexes.size(); ++i)
    {
        int index = picked_indexes[i];
        char current = data.at(index);
        int decimal = ((int)current &amp; 0xff);

        int bit_to_flip = rand() % 8;

        decimal ^= 1 &lt;&lt; bit_to_flip;
        decimal &amp;= 0xff;

        data[index] = (char)decimal;
    }

    return data;

}

//
// takes mutated string and creates new jpeg with it;
//
void create_new(std::string mutated)
{
    std::ofstream fout("mutated.jpg", std::ios::binary);

    if (fout.is_open())
    {
        fout.seekp(0, std::ios::beg);
        fout.write(&amp;mutated[0], mutated.size());
    }
    else
    {
        std::cout &lt;&lt; "Failed to create mutated.jpg" &lt;&lt; ".n";
        exit(1);
    }

}

//
// function to run a system command and store the output as a string;
// https://www.jeremymorgan.com/tutorials/c-programming/how-to-capture-the-output-of-a-linux-command-in-c/
//
std::string get_output(std::string cmd)
{
    std::string output;
    FILE * stream;
    char buffer[256];

    stream = popen(cmd.c_str(), "r");
    if (stream)
    {
        while (!feof(stream))
            if (fgets(buffer, 256, stream) != NULL) output.append(buffer);
                pclose(stream);
    }

    return output;

}

//
// we actually run our exiv2 command via the get_output() func;
// retrieve the output in the form of a string and then we can parse the string;
// we'll save all the outputs that result in a segfault or floating point except;
//
void exif(std::string mutated, int counter)
{
    std::string command = "exiv2 pr -v mutated.jpg 2&gt;&amp;1";

    std::string output = get_output(command);

    std::string segfault = "Segmentation";
    std::string floating_point = "Floating";

    std::size_t pos1 = output.find(segfault);
    std::size_t pos2 = output.find(floating_point);

    if (pos1 != -1)
    {
        std::cout &lt;&lt; "Segfault!n";
        std::ostringstream oss;
        oss &lt;&lt; "/root/cppcrashes/crash." &lt;&lt; counter &lt;&lt; ".jpg";
        std::string filename = oss.str();
        std::ofstream fout(filename, std::ios::binary);

        if (fout.is_open())
            {
                fout.seekp(0, std::ios::beg);
                fout.write(&amp;mutated[0], mutated.size());
            }
        else
        {
            std::cout &lt;&lt; "Failed to create " &lt;&lt; filename &lt;&lt; ".jpg" &lt;&lt; ".n";
            exit(1);
        }
    }
    else if (pos2 != -1)
    {
        std::cout &lt;&lt; "Floating Point!n";
        std::ostringstream oss;
        oss &lt;&lt; "/root/cppcrashes/crash." &lt;&lt; counter &lt;&lt; ".jpg";
        std::string filename = oss.str();
        std::ofstream fout(filename, std::ios::binary);

        if (fout.is_open())
            {
                fout.seekp(0, std::ios::beg);
                fout.write(&amp;mutated[0], mutated.size());
            }
        else
        {
            std::cout &lt;&lt; "Failed to create " &lt;&lt; filename &lt;&lt; ".jpg" &lt;&lt; ".n";
            exit(1);
        }
    }
}

//
// simply generates a vector of strings that are our 'magic' values;
//
std::vector&lt;std::string&gt; vector_gen()
{
    std::vector&lt;std::string&gt; magic;

    using namespace std::string_literals;

    magic.push_back("xff");
    magic.push_back("x7f");
    magic.push_back("x00"s);
    magic.push_back("xffxff");
    magic.push_back("x7fxff");
    magic.push_back("x00x00"s);
    magic.push_back("xffxffxffxff");
    magic.push_back("x80x00x00x00"s);
    magic.push_back("x40x00x00x00"s);
    magic.push_back("x7fxffxffxff");

    return magic;
}

//
// randomly picks a magic value from the vector and overwrites that many bytes in the image;
//
std::string magic(std::string data, std::vector&lt;std::string&gt; magic)
{

    int vector_size = magic.size();
    int picked_magic_index = rand() % vector_size;
    std::string picked_magic = magic[picked_magic_index];
    int size = (data.length() - 4);
    int picked_data_index = rand() % size;
    data.replace(picked_data_index, magic[picked_magic_index].length(), magic[picked_magic_index]);

    return data;

}

//
// returns 0 or 1;
//
int func_pick()
{
    int result = rand() % 2;

    return result;
}

int main(int argc, char** argv)
{

    if (argc &lt; 3)
    {
        std::cout &lt;&lt; "Usage: ./cppfuzz &lt;valid jpeg&gt; &lt;number_of_fuzzing_iterations&gt;n";
        std::cout &lt;&lt; "Usage: ./cppfuzz Canon_40D.jpg 10000n";
        return 1;
    }

    // start timer
    auto start = std::chrono::high_resolution_clock::now();

    // initialize our random seed
    srand((unsigned)time(NULL));

    // generate our vector of magic numbers
    std::vector&lt;std::string&gt; magic_vector = vector_gen();

    std::string filename = argv[1];
    int iterations = atoi(argv[2]);

    int counter = 0;
    while (counter &lt; iterations)
    {

        std::string data = get_bytes(filename);

        int function = func_pick();
        function = 1;
        if (function == 0)
        {
            // utilize the magic mutation method; create new jpg; send to exiv2
            std::string mutated = magic(data, magic_vector);
            create_new(mutated);
            exif(mutated,counter);
            counter++;
        }
        else
        {
            // utilize the bit flip mutation; create new jpg; send to exiv2
            std::string mutated = bit_flip(data);
            create_new(mutated);
            exif(mutated,counter);
            counter++;
        }
    }

    // stop timer and print execution time
    auto stop = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast&lt;std::chrono::milliseconds&gt;(stop - start);
    std::cout &lt;&lt; "Execution Time: " &lt;&lt; duration.count() &lt;&lt; "msn";

    return 0;
}
```

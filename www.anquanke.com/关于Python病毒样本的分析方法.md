> 原文链接: https://www.anquanke.com//post/id/226721 


# 关于Python病毒样本的分析方法


                                阅读量   
                                **182161**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t01a4f850cb1ea1b70f.png)](https://p5.ssl.qhimg.com/t01a4f850cb1ea1b70f.png)



## 前言

近年来，Python语言凭借其入门简单、功能强大和开发效率高等特性逐渐成为最受欢迎的开发语言，与此同时，Python在安全领域的应用也渐趋广泛，开始被用在黑客和渗透测试的各个领域。

微步在线在威胁监控过程中，多次发现病毒木马或直接使用Python来编写，或使用Python打包的方式进行投递：如在2020年1月的一起针对阿拉伯地区的APT攻击事件中，攻击者通过投递携带CVE-2017-0199漏洞的docx文件，释放并运行了Python打包的后门程序；又如2019年11月份，Gaza（中东背景APT组织）也被发现使用了Python封装其木马组件。由此可见，Python在网络攻击事件中的出现日趋频繁，这也为安全分析人员带来新的挑战。

经过分析发现，Python打包的病毒木马主要存在以下3种形式：

1. 以py脚本的形式存在，此种方式最为常见，但也最容易阅读和分析。

2. 将pyc文件结构打包到各种可执行文件中，如PyInstaller工具等。

3. 通过Cython转换成C语言代码，再编译成可执行文件。

其中，以第1种方式最为简单也最为常见，而第2种、第3种方法具有一定分析难度。本文针对第二种方式进行介绍，将介绍常见的Python打包工具的安装和使用方法，同时对典型的Python打包木马病毒进行分析，并讲述相关逆向分析技巧。

## 常见Python打包工具

### **1. PyInstaller**

**简介**

PyInstaller 是一个用来将 Python 程序打包成一个独立可执行软件包，支持 Windows、Linux 和 macOS X。该工具是现在非常成熟的一款工具，具有良好的兼容性，支持的Python版本可达到Python3.7。

**使用方式**

PyInstaller的使用方式非常简单：

(1) pip install pyinstaller指令就可进行安装。

(2) pyinstaller.exe -F yourcode.py指令就可进行简单打包。

**分析方法**

PyInstaller打包的文件分析起来也十分简单，有现成的工具脚本——pyinstxtractor.py可以使用。pyinstxtractor.py的下载地址如下：

https://sourceforge.net/projects/pyinstallerextractor/。

用法也很简单，指令pyinstxtractor.py+可执行文件，就可以进行解包。

[![](https://p1.ssl.qhimg.com/t01df1fa27fb9e2a237.png)](https://p1.ssl.qhimg.com/t01df1fa27fb9e2a237.png)

### **2. py2exe**

**简介**

Py2exe这个工具只能在Windows平台使用，Py2exe是一个开源项目，github的地址：https://github.com/py2exe/py2exe。Py2exe执行Python2和Python3。

**使用方式**

(1) 下载地址，如下：
1. Python3可直接pip下载。
1. Python2在https://sourceforge.net/projects/py2exe/files/py2exe/下载。
(2) 使用方法，如下：

使用需要创建一个set.py(名称随意),文件内容：

from distutils.core import setup

import py2exe

setup(windows=[‘1.py’])

set.py -h可查看帮助

python set.py py2exe指令可编译成exe文件

效果如下图：

[![](https://p2.ssl.qhimg.com/t01fe6343b9d57d73d2.png)](https://p2.ssl.qhimg.com/t01fe6343b9d57d73d2.png)

**分析方法**

(1) 在py2exe打包后的结果文件中，exe和python.dll都是必要组件。有时python.dll可能会被内嵌在exe中。

(2) 可执行文件运行时必然会调用附带的python.dll。

(3) 对python.dll的导出函数PyMarshal_ReadObjectFromString进行hook或者下断点。

(4) 通过PyMarshal_ReadObjectFromString函数可以获取到打包进exe的pyc数据。该函数有两个参数，参数一是pyc数据的起始地址，参数二为数据的长度。

注意：在py2exe中获取的pyc数据内包含多个模块，一定要将多个模块进行拆分再反编译，否则会出错的。

### **3. bbFreeze**

**简介**

BBFreeze由BrainBot Technologies AG开发。

GitHub的地址：

https://github.com/schmir/bbfreeze。

**使用方式**

(1) 下载地址，如下：

可以通过pip或easy_install直接下载。

(2) 使用方法，如下：

指令：bbFreeze+py脚本

[![](https://p5.ssl.qhimg.com/t0119ae8640e358fe71.png)](https://p5.ssl.qhimg.com/t0119ae8640e358fe71.png)

输出结果如图：

[![](https://p5.ssl.qhimg.com/t01e98198debb7089ff.png)](https://p5.ssl.qhimg.com/t01e98198debb7089ff.png)

**分析方法**

BBFreeze和其他工具有所差别，它是通过PyRun_StringFlags函数进行。

[![](https://p0.ssl.qhimg.com/t013f58c05c0f7e7881.png)](https://p0.ssl.qhimg.com/t013f58c05c0f7e7881.png)

BBFreeze会通过zip模块把随身携带的library.zip进行解压，再通过python的exec来进行执行。其中的library.zip可能会嵌在可执行文件当中。library.zip解压后如图：

[![](https://p1.ssl.qhimg.com/t01f7f08a17b1dbf821.png)](https://p1.ssl.qhimg.com/t01f7f08a17b1dbf821.png)

### **4. cx_Freeze**

**简介**

cx_Freeze也是一种用于将Python脚本打包成可执行文件的一种工具，使用起来和py2exe差不多。GitHub的地址：

https://github.com/marcelotduarte/cx_Freeze

**使用方式**

(1) 下载地址，如下：

https://sourceforge.net/projects/cx-freeze

也可使用pip进行下载。

(2) 使用方法，如下：

指令：cxfreeze+py脚本。

输出文件如同：

[![](https://p2.ssl.qhimg.com/t019b25344aed486ca0.png)](https://p2.ssl.qhimg.com/t019b25344aed486ca0.png)

**分析方法**

cx_Freeze打包的文件分析起来更为简单。cx_Freeze会将pyc文件直接以资源的形式放在资源段中。我们可以直接使用压缩工具进行打开：

[![](https://p3.ssl.qhimg.com/t01ba4fd366529aa153.png)](https://p3.ssl.qhimg.com/t01ba4fd366529aa153.png)

## 典型木马病毒分析

通过分析一个简单的样本来演示如何分析这一系列的样本。我们找到一个样本哈希287b67d9927b6a318de8c94ef525cc426f59dc2199ee0e0e1caf9ef0881e7555。

分析第一步需要判断该样本是由什么工具打包的：

首先，我们可以看到有“_MEIPASS2=”字符串，从这可以看到该样本是由Python打包而来。从WinMain函数的代码来看，可以看出来该样本是PythonInstaller打包而来。

[![](https://p4.ssl.qhimg.com/t01937d53ec594afdc1.png)](https://p4.ssl.qhimg.com/t01937d53ec594afdc1.png)

确定好是由什么工具打包后，可以使用之前提到的方式直接对其解包。使用pyinstxtractor.py脚本对其进行解包。解包后的文件列表大致如下：

[![](https://p2.ssl.qhimg.com/t019d54e86c5e574bbc.png)](https://p2.ssl.qhimg.com/t019d54e86c5e574bbc.png)

其中我们可以看到解包后会生成python27.dll，从这可以看出来该样本是由Python2.7编写的。

[![](https://p1.ssl.qhimg.com/t01ea086133cb3e4fdf.png)](https://p1.ssl.qhimg.com/t01ea086133cb3e4fdf.png)

我们大致可以看到，解包后的文件有很多。会有很多Python运行必要的组件和第三方组件，如：_socket.pyd、Crypto.Cipher._AES.pyd等。我们可以在文件列表内看到一个没有扩展名的文件：

[![](https://p4.ssl.qhimg.com/t01d7bac648c89b9a0d.png)](https://p4.ssl.qhimg.com/t01d7bac648c89b9a0d.png)

该文件就是我们需要样本核心代码。该文件的文件名就是打包前py文件的文件名，该文件的文件格式很接近pyc的文件格式。之间的差别就是在于文件头缺少majic字段和时间戳。

[![](https://p1.ssl.qhimg.com/t01121be783d2c9a264.png)](https://p1.ssl.qhimg.com/t01121be783d2c9a264.png)

我们添加一个Python2.7的majic字段和任意的时间戳。然后我们就可以使用uncompile.py脚本还原出该py文件。

[![](https://p0.ssl.qhimg.com/t01b75f2d5b32c4e7dd.png)](https://p0.ssl.qhimg.com/t01b75f2d5b32c4e7dd.png)

对于这种常见工具打包的Python样本，我们通常处理的流程：

(1) 判断样本是由什么工具打包而来的。这种工具很常见，它们打包出来的程序往往很容易判断出来。

(2) 使用针对的破解工具或方法进行代码提取。

(3) 提取的代码通常是pyc文件格式的。

(4) 使用uncompile.py脚本进行反编译就可得到原始的py文件。

**其他Python打包分析**

通常情况下，病毒样本不会乖乖的使用以上几种工具进行打包。很多黑客会使用自己定制的程序来对python脚本进行打包。我们以一个样本举例，通过该样本来演示如何分析。该样本是一个由pupy的py脚本打包而来的elf文件。

1. 分析该样本，发现该样本会在内存中解密释放libpython2.7.so.1.0这个so文件。该文件是python2.7的核心文件，导出函数都是python重要的api函数。

[![](https://p4.ssl.qhimg.com/t0142325994c41bbc8a.png)](https://p4.ssl.qhimg.com/t0142325994c41bbc8a.png)

2. 在将libpython2.7.so.1.0，就该函数sub_5637CE90DFD2负责获取libpython2.7.so.1.0的导出函数。

[![](https://p1.ssl.qhimg.com/t0146c8f91a6ed47627.png)](https://p1.ssl.qhimg.com/t0146c8f91a6ed47627.png)

3. 将libpython2.7.so.1.0的导出函数地址初始化到imports全局变量内。通过使用dlsym函数，利用函数的名称来获取函数地址。

[![](https://p5.ssl.qhimg.com/t01fe5260593bf0356b.png)](https://p5.ssl.qhimg.com/t01fe5260593bf0356b.png)

4. 之前已经将python api的地址存储在imports变量内，之后的调用也是通过imports变量来进行的，还原一下调用的python函数的符号，可以看到样本初始化python环境和执行的整个过程。

首先是初始化python运行环境。

[![](https://p0.ssl.qhimg.com/t01235fadf6425cf797.png)](https://p0.ssl.qhimg.com/t01235fadf6425cf797.png)

随后初始化必要的python模块。

[![](https://p0.ssl.qhimg.com/t01b8344620db97c78d.png)](https://p0.ssl.qhimg.com/t01b8344620db97c78d.png)

[![](https://p4.ssl.qhimg.com/t0163311421fb45996a.png)](https://p4.ssl.qhimg.com/t0163311421fb45996a.png)

在准备好python运行环境后，就该是加载pupy的代码了。

看到PyMarshal_ReadObjectFromString函数的时候，可以得知该样本使用脚本式来执行python的代码。

[![](https://p5.ssl.qhimg.com/t01453df7f8d86974d7.png)](https://p5.ssl.qhimg.com/t01453df7f8d86974d7.png)

PyMarshal_ReadObjectFromString函数的主要功能是，读取一段数据，生成一个PyCodeObject的python对象。第一个参数是string的地址，第二个参数是数据的长度。

5. PyMarshal_ReadObjectFromString的第一个参数就是pupy的字节码，这个字节码的实际格式是一个pyc文件。将这个string还原成pyc文件就可以恢复出pupy的py脚本。
- 将PyMarshal_ReadObjectFromString的第一个参数数据保存到pyc文件中。注意，这个时候保存的pyc文件内并没有python的版本信息和时间戳。在文件头前添加8个字节，前四个字节表示python版本（不可随意填写，一定要是python2.7版本）、后四个字节表示时间戳（可随便填写）。
[![](https://p2.ssl.qhimg.com/t01996ed4a8aad650e1.png)](https://p2.ssl.qhimg.com/t01996ed4a8aad650e1.png)


- 通过python的反编译脚本uncompyle6.py对保存的pyc文件进行反编译，就可以生成一个pupy的py脚本。通过对脚本的简单分析就可以十分确定这个样本是pupy家族的。脚本是开源的，具体的行为就不进行分析。


[![](https://p5.ssl.qhimg.com/t0145341e02587bf378.png)](https://p5.ssl.qhimg.com/t0145341e02587bf378.png)



## 总结

通过对多个工具分析可以看到，无论是通过什么工具进行打包，都需要一个关键的因素，那就是python.dll或libpython.so。那么我们先来介绍一下python.dll在python中起到了什么作用。

实质上，在整个Python的目录结构中，python.dll是最核心最基础的组件。Python的运行时环境就是在python.dll中实现的，这里包含了对象/类型系统、内存分配器和运行时状态信息。这里也就可以理解为什么任何方式进行打包都需要将对应的python.dll一同打包进去了。

也就是说，无论什么工具，都是要通过python.dll来建立python的运行环境。这个过程是可以通过调用python.dll的导出函数来实现的。在python.dll的一个导出函数中，有个函数Py_Initialize就是用来初始化Python的运行环境。

Python有两种主要的运行模式，一种是交互式模式，另一种是脚本运行方式。我们通过两个简单例子来演示一下：

### **1. 脚本运行方式**

我们准备一个简单的py脚本，将其编译为pyc文件。

[![](https://p4.ssl.qhimg.com/t0103ab2527b426c4e5.png)](https://p4.ssl.qhimg.com/t0103ab2527b426c4e5.png)

我们准备一个简单的C代码来调用此pyc文件。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016226a81cbcf68f81.png)

(1) 加载对应版本的python.dll。

(2) 首先先调用Py_Initialize函数。

(3) 随后调用PyRun_SimpleFile，来运行pyc文件。

### **2. 输出结果**

[![](https://p5.ssl.qhimg.com/t01cd34339f75bce121.png)](https://p5.ssl.qhimg.com/t01cd34339f75bce121.png)

### **3. 交互式模式**

简单的C代码的例子：

[![](https://p4.ssl.qhimg.com/t01afbacea6ff451e21.png)](https://p4.ssl.qhimg.com/t01afbacea6ff451e21.png)

(1) 加载对应版本的python.dll。

(2) 首先先调用Py_Initialize函数。

(3) 接下来利用PyDict_New创建一个Dict。

(4) 然后调用PyEval_GetBuiltins获取解释器。

(5) 最后调用PyRun_String来执行各种代码。

### **4. 运行结果**

[![](https://p0.ssl.qhimg.com/t0101c127752472f4ed.png)](https://p0.ssl.qhimg.com/t0101c127752472f4ed.png)

根据两个演示，可以很明确的知道Python的运行逻辑。在之后遇到的任何由Python打包的可执行文件时，可以通过对PyRun系列的函数进行检测。

[![](https://p0.ssl.qhimg.com/t0183850fad94bf904f.png)](https://p0.ssl.qhimg.com/t0183850fad94bf904f.png)

通过这一系列的函数，我们可以获取到打包进可执行文件内的明文Python脚本或pyc的字节码。

### **5. 总结**

处理python打包这一系列样本的过程主要如下：

(1) 判断是否是已知工具打包。

(2) 如果不是已知工具，可着手查找PyRun系列的函数的调用。

(3) 在PyRun系列的函数的参数中可以获取到对应的样本代码。

(4) 使用uncompile.py脚本进行反编译就可得到原始的py文件。



## 参考链接

### **6.1 工具链接**
<td class="ql-align-justify" data-row="1">**工具**</td><td class="ql-align-justify" data-row="1">**链接**</td>
<td class="ql-align-justify" data-row="2">Pyinstaller</td><td class="ql-align-justify" data-row="2">https://pypi.org/project/pyinstaller/</td>
<td class="ql-align-justify" data-row="3">py2exe</td><td class="ql-align-justify" data-row="3">https://pypi.org/project/py2exe/</td>
<td class="ql-align-justify" data-row="4">bbFreeze</td><td class="ql-align-justify" data-row="4">https://pypi.org/project/bbfreeze/</td>
<td class="ql-align-justify" data-row="5">cx-Freeze</td><td class="ql-align-justify" data-row="5">https://pypi.org/project/cx-Freeze/</td>

### **6.2 样本链接**
1. https://s.threatbook.cn/report/file/287b67d9927b6a318de8c94ef525cc426f59dc2199ee0e0e1caf9ef0881e7555/?sign=history&amp;env=winxpsp3_exe
1. https://s.threatbook.cn/report/file/4827847e926a1f39c720894aba3eae8ee1e711f8cc9f57effbba4ea36c072b81/?sign=history&amp;env=win7_sp1_enx86_office2013
### **6.3 有关Python木马的安全事件报告**
1. https://x.threatbook.cn/nodev4/vb4/article?threatInfoID=2075
1. https://blog.talosintelligence.com/2020/01/jhonerat.html


## 关于微步在线研究响应团队

微步情报局，即微步在线研究响应团队，负责微步在线安全分析与安全服务业务，主要研究内容包括威胁情报自动化研发、高级 APT 组织&amp;黑产研究与追踪、恶意代码与自动化分析技术、重大事件应急响应等。

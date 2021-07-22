> 原文链接: https://www.anquanke.com//post/id/85388 


# 【技术分享】Android程序反混淆利器——Simplify工具


                                阅读量   
                                **530451**
                            
                        |
                        
                                                                                    



**[![](https://p1.ssl.qhimg.com/t014a6e6d53dca67543.jpg)](https://p1.ssl.qhimg.com/t014a6e6d53dca67543.jpg)**

**问题背景**

Android程序代码混淆是Android开发者经常用来防止app被反编译之后迅速被分析的常见手法。在没有混淆的代码中，被反编译的Android程序极其容易被分析与逆向，分析利器JEB就是一个很好的工具。但是加了混淆之后，函数、变量的名称将被毫无意义的字母替代，这将大大提高分析的难度。有的甚至会增加一些冗余代码，比如下面的例子：

```
public void doBadStuff() `{`
    int x;
    int y;
    x = Integer.valueOf("5")
    y = Integer.valueOf("10")
    x = x * y;
    x += 5;
    x /= 3;
    hackYourPhoneLOL("backdoor");
    x = y;
    y = x + 10;
    y /= 2;
`}`
```

该函数的实际意图其实就是执行**hackYourPhoneLOL("backdoor");**，但是通过代码混淆，增加很多冗余的代码， 使得实际分析的时候工作量增加。对于代码混淆，其实一直并没有一个比较好的思路，也没有万能的工具来解混淆，最常见的方式就是用Android gradle proguard 去尝试那些用Android gradle proguard混淆过的代码，但是成功率极其低（比如对于用DexGuard混淆过的代码）。<br>



```
public void doBadStuff() `{`
    hackYourPhoneLOL("backdoor");
`}`
```

今天要介绍的工具，就是一个通用的Android程序反混淆工具，虽然在执行效率上不是很高，但是思路清晰，代码风格好，值得深入学习与优化。下图是在使用该工具前后，反编译代码的对比图。<br>

 

[![](https://p5.ssl.qhimg.com/t01316f13500e1ecf15.png)](https://p5.ssl.qhimg.com/t01316f13500e1ecf15.png)

图1：代码解混淆之前

[![](https://p5.ssl.qhimg.com/t01bebcb4bfc0171b6d.png)](https://p5.ssl.qhimg.com/t01bebcb4bfc0171b6d.png)

图2：代码解混淆之后

可以发现，在代码解混淆之后，关键函数名称、正则表达式等等字符串都能够解析出来了，这样的反编译结果将非常适合分析人员进一步分析恶意代码的功能。

这是github地址：[https://github.com/CalebFenton/simplify](https://github.com/CalebFenton/simplify)

该工具的核心思路，就是自己模拟的Dalvik虚拟机执行的方式，将待反编译的代码执行一遍，获知其功能后，将反编译之后的代码简化成分析人员便于理解的形式。

**<br>**

**安装方式**

 由于该项目包含Android框架的子模块，因此用以下两种方式获取代码：



```
git clone --recursive https://github.com/CalebFenton/simplify.git
or
git submodule update --init --recursive
```

接着，使用gradlew编译jar文件，当然前提是系统里面安装过了gradlew



```
./gradlew fatjar
```

在成功执行之后，Simplify.jar 应该出现在simplify/build/libs/simplify.jar这里，接着你可以使用以下命令行测试Simplify.jar是否安装成功



```
java -jar simplify/build/libs/simplify.jar -it 'org/cf' simplify/obfuscated-example
```

**注：安装可能出现的问题**

由于该工具还在前期开发阶段，因此作者也提出该工具不是很稳定，因此可以尝试使用下面的方式反复尝试是否成功。

1. 首先，确定分析的smali文件包含不多的method或者classes的时候，可以使用-it命令。

2. 如果因此超过了最大的地址访问长度、函数调用分析深度、最大的方法遍历次数等，可以通过改变参数 –max-address-visits, –max-call-depth, –max-method-visits.来修正。

3. 如果实在不行，就是用-v参数来报告问题吧。

完整的使用命令在github中有，这里不再赘述。

**<br>**

**例子分析**

这里以github里面的一个引导性的例子为切入，来介绍该工具是如何工作的。在介绍该工具如何工作之前，首先简单介绍一下该项目里面包含的模块。

**1. smalivm: **该模块是Dalvik虚拟机的模拟器模块，主要用来模块Dalvik虚拟机的执行。它能够根据输入的smali文件返回所有可能的执行路径以及对应的路径得到的寄存器的值。该模拟器能够在不知道一个函数参数的情况下进一步分析，它的方式就是将函数中存在分支的所有结果模拟执行一遍，在完全执行完毕之后，该工具会返回程序执行的每条路径的寄存器的结果，从而便于simplify模块进一步分析，简化混淆的代码。

**2. simplify: **该模块是解混淆的主要模块，主要基于smalivm的分析结果，简化混淆的反编译代码，得到易于理解的反编译代码。

接下来看看例子，该例子是java代码的形式编写的。

1. 首先需要新建一个模拟器，其中，SMALI_PATH是自己配置的待分析的smali文件的路径，在这里就不贴出待分析的样例main.smali文件，太长了,[github的地址](https://github.com/CalebFenton/simplify/blob/master/demoapp/resources/org/cf/demosmali/Main.smali)。



```
VirtualMachineFactory vmFactory = new VirtualMachineFactory();
        vm = vmFactory.build(SMALI_PATH);
```

2. 接下来，是使用该工具提供的hook函数的功能将某些函数hook掉，由于有些函数会影响模拟器的外部输出结果，比如System.out.println(),因此，需要将这些函数hook，以在保证函数正常运行的情况下，得到smalivm正常输出的结果。



```
MethodEmulator.addMethod("Ljava/io/PrintStream;-&gt;println(Ljava/lang/String;)V", java_io_PrintStream_println.class);
```

3. 接下来，是执行待分析smali文件的main函数。

```
vm.execute("Lorg/cf/demosmali/Main;-&gt;main([Ljava/lang/String;)V");
```

4. 最后，根据不同的函数参数输入类型，选择对应的函数分析方式分析Android程序的功能，此外，除了函数本身参数的类型，分析的方式额外的根据自己的需求选择有参数还是无参数分析，此处的选择可以不用局限于函数本身的参数类型。有参数的方式能够加快分析速度，但是往往很多情况下，我们并不知道参数应该设置成什么值，不恰当的值会导致

```
executePrintParameter(42);
        executeParameterLogicWithUnknownParameter();
        executeParameterLogicWithKnownParameter(10);
```

**注意**，由于在无参数分析的情况下，该工具会穷举所有可能的分支结构，因此需要将前面提到的三个参数的数值设置大一些，分析的时间也将响应的变长。

5. executePrintParameter和executeParameterLogicWithKnownParameter这两个函数应该好理解，就是将输入带入进去分析了。接下分析一下executeParameterLogicWithUnknownParameter这个函数。首先是建立目标函数的签名，该名称直接根据待分析的目标函数的签名而来：



```
String methodSignature = "Lorg/cf/demosmali/Main;-&gt;parameterLogic(I)I";
```

6. 使用smalivm执行在无参数情况设置下的函数，在这个样例中，smalivm应当输出两个结果，这代表了smalivm执行了两条路径。



```
ExecutionGraph graph = vm.execute(methodSignature);
```

7. 获取smalivm分析得到所有的分析路径，不同路径有不同的返回结果，因此能够输出所有的返回结果。getTerminatingRegisterConsensus这个函数可以很方便获得所有返回寄存器的地址，从而得到输出的结果。

```
HeapItem item = graph.getTerminatingRegisterConsensus(MethodState.ReturnRegister);
        System.out.println("With no context, returns an unknown integer: " + item);
```



**总结**

该工具simplify是我目前看到过的唯一一个通用的能够用来解任何混淆的工具，该工具的思路较为巧妙，（即，通过模拟执行混淆Android程序的方式获知Android程序的功能，从而简化混淆代码，使得易于分析）实现难度较大，因此是一个很不错的工作。但在优化执行效率方面也还有许多的提升空间，比如，在无参数分析函数的设置下，该工具会将所有可能的输入都执行，因此执行的时间可能会很长。从污点分析技术中借鉴剪枝的技术可能是一个有前景的优化方向。

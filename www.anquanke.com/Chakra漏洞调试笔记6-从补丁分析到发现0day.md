
# Chakra漏洞调试笔记6-从补丁分析到发现0day


                                阅读量   
                                **588322**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/201696/t01625ce9ac8a19e5b4.png)](./img/201696/t01625ce9ac8a19e5b4.png)**



这个漏洞是笔者在2019年12月分析ChakrCore漏洞补丁时发现的。笔者第一时间将触发漏洞的PoC和任意地址读写的exp提交给了微软。微软很快承认了该漏洞并表示会修复。今年3月笔者发现该漏洞已经在ChakraCore v1.11.17版本中被修复，但遗憾的是并未分配相应CVE号。考虑到该漏洞已经在最新的Edge浏览器中被修复，笔者在这里将漏洞发现的思路分享给大家。由于笔者水平有限，文中错误之处恳请斧正。



## 0x0 补丁分析

ChakraCore针对CVE-2019-1308修复的代码中有一行引起了笔者的注意（commit：64376deca69126c2bb05cd87bd5c073aedaf5f9c）：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01bb4445b5bcb2a513.png)

修复代码来自函数GlobOpt::FinishOptPropOp。GlobOpt::FinishOptPropOp是JIT在Forward阶段针对对象属性操作的优化函数。对于目标操作数，其主要逻辑如下：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01dac510621bed7eab.png)

通过源码注释知道：对于对象属性的存储操作，可能会修改对象的内存布局，因此需要两个去优化操作保证JIT代码的安全：
1. 将可能添加属性的对象symbol加入maybeWrittenTypeSyms，后面会根据maybeWrittenTypeSyms增加类型检查
1. Kill有object-header-inlined的symbol
对于1）的去优化，补丁前的条件是if (!isObjTypeChecked)，补丁后的条件是if (!isObjTypeSpecialized || opnd-&gt;IsBeingAdded())。这两个条件的区别是什么呢，修补后是否会引入新的问题呢？



首先从变量的字面意思可以猜到isObjTypeChecked是指对象类型已经做过类型检查，isObjTypeSpecialized是指对象类型已经被定义，opnd-&gt;IsBeingAdded()是指属性操作数正在被添加。其中isObjTypeChecked和isObjTypeSpecialized变量由函数GlobOpt::ProcessPropOpInTypeCheckSeq确定：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0147dd508643dee922.png)

对于新建对象，isObjTypeSpecialized=true，isObjTypeChecked=false，会生成类型检查：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0151684385b26e3176.png)

回到补丁处，修补前，对于isObjTypeChecked=false的情况都会加入maybeWrittenTypeSyms；修补后，只有在isObjTypeSpecialized=false或者opnd-&gt;IsBeingAdded() = true时才会加入maybeWrittenTypeSyms。显然，补丁修复后，去优化的条件放宽了，那么这样是否会引入新的问题呢？



我们看下面这个例子：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01ee6f6f89e1e8327e.png)

初始化对象{a:1}会生成opcode InitFld，为对象初始化属性a并赋值为1。这里在优化目标操作数的时候，由于是对象属性操作会调用GlobOpt::FinishOptPropOp。

对于新建对象，isObjTypeSpecialized=true，isObjTypeChecked=false，补丁前会进入if (!isObjTypeChecked)分支，将未做类型检查的对象symbol加入maybeWrittenTypeSyms。而补丁后，由于新建对象的isObjTypeSpecialized为true，且opnd-&gt;IsBeingAdded()=false，因此不会进入if分支，未做类型检查的对象symbol就不会加入maybeWrittenTypeSyms。

接下来，对于语句obj1.b = 0x1234会生成opcode StFld，GlobOpt::FinishOptPropOp函数调用ProcessPropOpInTypeCheckSeq函数时，因为对象类型已经初始化过，会检查当前类型symbol是否存在maybeWrittenTypeSyms中：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t013cac45d197e50a5e.png)

如果不存在，则objectMayHaveAcquiredAdditionalProperties = false，并通过opnd-&gt;SetTypeChecked (!objectMayHaveAcquiredAdditionalProperties);设置目标操作数opnd.isTypeChecked = true，最终不需要为obj1.b = 0x1234;语句生成类型检查。



观察补丁前后JIT forward阶段的dump:

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01283bca410f292d11.png)

可以看到，补丁后在优化obj1.b = 0x1234;语句时，由于处理let obj1 = {a:1}; let obj2 = {a:1};语句时 isObjTypeSpecialized=true，且opnd-&gt;IsBeingAdded()=false，因此未进入去优化操作分支设置maybeWrittenTypeSyms。导致在处理obj1.b = 0x1234;语句时，objectMayHaveAcquiredAdditionalProperties = false，从而opnd.isTypeChecked = true，最终不需要为obj1.b = 0x1234;增加类型检查。

那么对于补丁后在forward阶段不需要进行类型检查，但是确实存在对象属性增加的情况，第二次backward阶段会为其生成opcode AdjustObjType，从而在JIT中动态调整对象类型：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0183656bbcf170a742.png)

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01572cafbed4dfedc4.png)



观察补丁前后JIT Globopt阶段的dump:

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0115263c55cc19ea0b.png)

可以看到补丁后，Globopt生成了AdjustObjType，位置在StFld之前，并且在后向遍历第一个Bailout之后。回顾笔者在《Chakra漏洞调试笔记2——OpCode Side Effect》中介绍的DynamicObject的Memory Layout。AdjustObjType在Lowerer阶段会生成AdjustSlots最终调整DynamicObject的Memory Layout，将inline slots位置替换成auxSlots指针：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ca4e52f60708fffb.png)

那么根据上面的分析，是否存在可能利用JIT里这次AdjustObjType的机会替换DynamicObject的Memory Layout，实现类型混淆呢？这里笔者的思路是，由于AdjustObjType会被emit到backward pass StFld上一个bailout指令后，因此通过尝试增加一些不会bailout的指令，分离AdjustObjType和StFld，实现auxSlots指针的类型混淆。



对上面的例子稍作改动，增加一个基本块：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0197f827969d9c29ad.png)

这里增加一个基本块，将obj1赋值给obj2，并通过obj2.a = 0;语句尝试覆盖AdjustObjType后的auxSlots指针。最后在obj1.b = 0x1234;时，由于auxSlots指针借助语句obj2.a = 0;被置为整数，从而可以造成内存访问异常。观察Globopt后的dump：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012a3ff31a436877f9.png)

可以发现，这里AdjustObjType出现在obj2.a = 0;之后，不符合预期，我们需要将obj2.a = 0;的StFld指令emit到AdjustObjType之后。通过一些手动测试，笔者发现如下情况可以实现我们的目标：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b0297c2e7c120d0c.png)

观察Globopt后的dump：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0119bb920ebf8beb95.png)

可以看到AdjustObjType成功的被插入在obj2的LdFld和StFld之间，而obj2在上面的if分支可以被obj1替换，这样的话AdjustObjType就可以破坏LdFld和StFld之间原子操作 ，StFld会将0覆盖到AdjustObjType后obj1.auxSlots指针。



Ch.exe运行PoC，很可惜并未发生crash，观察Lowerer阶段的dump，发现如下问题：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0199768951fe59f29e.png)

这里AdjustObjType在Lowerer阶段生成的汇编指令只是简单的将obj1的type做了替换，而并没有调用AdjustSlots，调试JIT也可以发现，obj1的inline slots没有发生变化，0x1234放在了inline slots+0x8处：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0157711e074acb7505.png)

考虑调整obj1初始化时的Memory Layout，我们得到了最终触发漏洞的PoC:

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015236c82dee862767.png)

ch.exe运行poc：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0152e7cacf05d7e514.png)

调试情况：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c4e06a2a50708dcc.png)



## 0x2 利用思路

对于CharkaCore JIT中的auxSlots指针类型混淆，利用还是比较简单的，主要思路还是借助DateView实现任意地址读写和对象地址泄露：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0152c40b11fc0f68fe.png)

利用这部分相关文章比较多，不再详述，这里给出完整的任意地址读写的exp，感兴趣的同学可以自行调试：

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014bc32feca3961b08.png)

[![](./img/201696/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019dd4f6d29c64429c.png)



## 0x3 参考文献
1. [https://github.com/microsoft/ChakraCore/commit/64376deca69126c2bb05cd87bd5c073aedaf5f9c](https://github.com/microsoft/ChakraCore/commit/64376deca69126c2bb05cd87bd5c073aedaf5f9c)
1. [https://www.anquanke.com/post/id/183127](https://www.anquanke.com/post/id/183127)
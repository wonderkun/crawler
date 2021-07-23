> 原文链接: https://www.anquanke.com//post/id/87043 


# 【技术分享】Unity3D程序脚本反编译分析与加密


                                阅读量   
                                **157307**
                            
                        |
                        
                                                                                    



**[![](https://p1.ssl.qhimg.com/t0116777214288c04be.jpg)](https://p1.ssl.qhimg.com/t0116777214288c04be.jpg)**

**<br>**

**前言**

对于使用 Unity3D 开发的程序，存在被**反编译**的风险，也面临着被 **dump 内存**的威胁，最终引起游戏或工程被抄袭甚至盗版。 下面简单介绍对Unity3D 脚本分析过程，同时提供了对其保护的参考手段。

**<br>**

**工具集**

dnSpy、Ollydbg、Cheat Engine

**<br>**

**背景**

大家都知道 Unity3D 使用开源 **mono C# **语法 ，所有代码都不是编译到 EXE，而是位于 `{`APP`}`uildgame_DataManagedAssembly-CSharp.dll (对于最新的 Unity3D 2017 不是这样)，而且 mono 语法只是跟 C# 兼容，但是**原理完全不一样**，传统的 C# 加壳全部失效，因为 Assembly-CSharp.dll 不是标准的 DLL 加载过程，既不是 PE 的 DLL，也不是 dotNet 的 DLL 加载，而是由 mono.dll 读取 Assembly-CSharp.dll 的 C# 脚本解释执行。这一切不用等官方 IL2CPP 或自己定制 mono 引擎！

**<br>**

**反编译**

反编译 Unity3D 的脚本代码，使用 dnSpy 就可以达到很好的效果，dnSpy 可以准确的将 Unity3D 的脚本文件以及标准的 DotNet 动态库文件反编译成源码形式。一般，将需要被反编译的文件拖入 dnSpy 工具即可。效果如下，其中可以完整的看到编码者的代码逻辑：

[![](https://p5.ssl.qhimg.com/t012311542ab942be91.png)](https://p5.ssl.qhimg.com/t012311542ab942be91.png)

截图官方demo被反编译

根据反编译后的代码就可以进一步分析软件的流程走向，甚至篡改原有过程，具体不做描述。

**<br>**

**如何对脚本代码进行保护？**

对于这种脚本代码的保护，通常采用脚本文件加密，解释器解密的形式来实现加密方案，下面简单介绍下可以针对这种脚本进行保护的现成产品：Virbox Protector、Virbox AHS。

Virbox Protector、Virbox AHS 分别可以防止静态分析、动态调试 Unity3D 的软件产品，具有如下特性：

1.一键加密你的代码逻辑，无法反编译，无法 dump 内存。

2.不降低游戏帧数， 甚至某些情况下还能提高游戏帧数。

3.Assembly.DLL 代码按需解密，只有调用到才会在内存解密，不调用不解密，黑客无法一次解出所有的代码。

4.完整授权方案，支持云授权、软锁授权，USB 加密锁授权、网络锁授权，支持限制时间、限制次数、限制网络并发。

5.自带反黑引擎，驱动级别反调试，对大部分调试器有效。

（注意：如果需要最高安全强度的游戏反外挂，请参考反黑引擎 ）

**<br>**

**使用加密工具前后比较**

1.dnspy 反编译被加壳的结果：

[![](https://p1.ssl.qhimg.com/t017736d5de960a785a.png)](https://p1.ssl.qhimg.com/t017736d5de960a785a.png)

加壳前

[![](https://p0.ssl.qhimg.com/t01c4a6f1270fd830ad.jpg)](https://p0.ssl.qhimg.com/t01c4a6f1270fd830ad.jpg)

加壳后

分析：从对比的结果看到很多代码信息已经丢失，再次进行分析时也会有很大困难。

2.PC 上的 X64Dbg 和 OllyDbg 调试失败与附加失败

[![](https://p3.ssl.qhimg.com/t01bfa0eab7a2b817ff.jpg)](https://p3.ssl.qhimg.com/t01bfa0eab7a2b817ff.jpg)

[![](https://p5.ssl.qhimg.com/t01847ffae68ac67e9b.jpg)](https://p5.ssl.qhimg.com/t01847ffae68ac67e9b.jpg)

分析：Virbox AHS 提供的这种针对动态调试的保护方案在实时分析程序时会起到显著的作用。

3.Cheat-Engine 读取内存失败（需要新的反黑引擎支持）

[![](https://p1.ssl.qhimg.com/t017d788f6b7cc357fa.jpg)](https://p1.ssl.qhimg.com/t017d788f6b7cc357fa.jpg)

分析：通过对原程序内存数据的保护，想使用修改数据的形式来进行作弊的恶意行为也会被拒之门外。

**<br>**

**典型客户场景**

1.Unity3D 游戏客户街机游戏

2.VR 设备交互体验

3.机器/医疗/工业/航天等 VR 交互

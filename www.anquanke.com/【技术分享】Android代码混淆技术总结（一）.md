
# 【技术分享】Android代码混淆技术总结（一）


                                阅读量   
                                **221896**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



**[![](./img/85843/t015ec9331e64246128.jpg)](./img/85843/t015ec9331e64246128.jpg)**

****

作者：[ix__xi](http://bobao.360.cn/member/contribute?uid=2858581749)

预估稿费：500RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

最近一直在学习Android加固方面的知识，看了不少论文、技术博客以及一些github上的源代码，下面总结一下混淆方面的技术，也算是给想学习加固的同学做一些科普，在文中将到的论文、资料以及源码，我都会给出相应的链接，供大家进一步去深入学习。后面我会弄成一个系列的文章，如有一些混淆技术没讲到，还希望大家指点，当做是交流学习。

<br>

**二、Android混淆技术介绍**

**2.1 控制流平坦化**

**2.1.1 概念和思路**

控制流平坦化，就是在不改变源代码的功能前提下，将C或C++代码中的if、while、for、do等控制语句转换成switch分支语句。这样做的好处是可以模糊switch中case代码块之间的关系，从而增加分析难度。

这种技术的思想是，首先将要实现平坦化的方法分成多个基本块（就是case代码块）和一个入口块，为每个基本快编号，并让这些基本块都有共同的前驱模块和后继模块。前驱模块主要是进行基本块的分发，分发通过改变switch变量来实现。后继模块也可用于更新switch变量的值，并跳转到switch开始处。详细的概念可以参考文献[1]。

其模型如下图：

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d120d245e67c5102.png)

下面用代码来说明，左边方法是没有采用控制流平坦化之前的效果，右边是采用了控制流平坦化的效果。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015ef33d7a8526c9fc.png)

**2.1.2 开源项目**

目前用的最多的是OLLVM（Obfuscator-LLVM）的开源混淆方案，很多国内加固厂商都可以看到使用它的身影。它提供了3中保护方式：控制流平坦化、虚假控制流和指令替换。其项目地址如下：

[https://github.com/Fuzion24/AndroidObfuscation-NDK](https://github.com/Fuzion24/AndroidObfuscation-NDK) 

[https://github.com/obfuscator-llvm/obfuscator](https://github.com/obfuscator-llvm/obfuscator) 

**2.1.3 对抗**

目前，对于ollvm的反混淆思路，多采用基于符号执行的方法来消除控制流平坦化，这里不做详细分析，详细的分析思路，可以参考quarkslab写的文章[3]。

**2.2 花指令**

**2.2.1 概念和思路**

花指令也叫垃圾指令，是指在原始程序中插入一组无用的字节，但又不会改变程序的原始逻辑，程序仍然可以正常运行，然而反汇编工具在反汇编这些字节时会出错，由此造成反汇编工具失效，提高破解难度。

花指令的主要思想是，当花指令跟正常指令的开始几个字节被反汇编工具识别成一条指令的时候，才可以使得反汇编工具报错。因此插入的花指令都是一些随机的但是不完整的指令。但是这些花指令必须要满足两个条件：

在程序运行时，花指令是位于一个永远也不会被执行的路径中。

这些花指令也是合法指令的一部分，只不过它们是不完整指令而已。

也就是说，我们只需要在每个要保护的代码块之前插入无条件分支语句和花指令，如下图所示。无条件分枝是保证程序在运行的时候不会运行到花指令的位置。而反汇编工具在再反汇编时由于会执行到花指令，所以就会报错。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a972365efbf71f95.png)

那么目前的反汇编工具所使用的反汇编算法，主要分为两类：线性扫描算法和递归扫描算法。

**线性扫描：**依次按顺序逐个地将每一条指令反汇编成汇编指令

例如下面的指令：

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016e75dd4778cd02ee.png)

如果是反汇编工具使用线性扫描算法，就会把花指令错误识别，导致反汇编出错。如下：

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01034c6682d84aede7.png)

Dalvik Bytecode Obfuscation on Android[5]这篇文章就利用线性扫描的特点，插入fill-array-data-payload花指令，导致反编译工具失效。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017d1dfb180d3e24b1.png)

**递归扫描：**按顺序逐个反汇编指令，如果某个地方出现了分支，就会把这个分支地址记录下来，然后对这些反汇编过程中碰到的分支进行反汇编。

可见，递归扫描的算法反汇编能力更强。我们常用的Android逆向工具里面，使用的反汇编算法如下：

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t011e3406eb1ecf5a03.png)

**2.2.2 开源项目**

(1) [https://github.com/thuxnder/dalvik-obfuscator](https://github.com/thuxnder/dalvik-obfuscator) 

可以结合文章[5]一起看。

(2) [https://github.com/faber03/AndroidMalwareEvaluatingTools](https://github.com/faber03/AndroidMalwareEvaluatingTools) 

这个工具是意大利萨尼奥大学的laswatlab团队打造出来的恶意程序免杀工具，其实就是使用各种混淆技术，其中也包括花指令插入，在AndroidMalwareEvaluatingTools/transformations sources/JunkInsertion/目录下。该工具的使用报告可以参考文献[4]。

(3) [https://github.com/strazzere/APKfuscator](https://github.com/strazzere/APKfuscator) 

APKFuscator通过插入下图的垃圾指令使得反汇编器出错。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e3501ccfa2cec98e.png)

**2.2.3 对抗**

检测出花指令的位置和长度，然后用NOP指令替换即可。

**2.3 标识符混淆**

**2.3.1 概念和思路**

标识符混淆就是对源程序中的包名、类名、方法名和变量名进行重命名，用无意义的标识符来替换，使得破解这分析起来更困难。最常用的就是ProGuard开源工具，其混淆后效果如右图所示。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018eac4068c91dbfb4.png)

甚至通过定制混淆字典，可以达到下面这种混淆效果，参考开源项目[7]：

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fa67f2fb48c06b7c.png)

那么这个标识符混淆的原理是怎样的呢？要了解这个原理，我们得事先对dex文件格式有一定了解，这个资料大家可以在网上找，很多，这里就不详细说了。

我们知道dex文件中的类名、方法名、变量名其实都对应的一个string_id的字符串索引，如下图。每一个类对应着class_def_item结构体，其中class_idx就是指向类名的字符串索引。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0190a8d3c727dd81db.png)

同样，每个方法也是对应一个method_id_item的结构体，其中name_idx就是指向方法名的字符串索引。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016260e46f8d11fb8e.png)

字段名也一样，对应着一个field_id_item的结构体，其中name_idx是指向字段名的字符串索引。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016c64e07c748c1dd2.png)

也就是说，我们只要修改相应的string_id索引表中的字符串，就可以达到标识符混淆的目的。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01064bb2e481e22634.png)

具体的实现可以参考文章[10]，它还提供了一个dex混淆器的简单原型：DexConfuse。

**2.3.2 开源项目**

(1) ProGuard

(2) [https://github.com/burningcodes/DexConfuse](https://github.com/burningcodes/DexConfuse)    

DexConfuse是一个简单的dex混淆器，可以混淆类名、方法名和字段名。

(3) [https://github.com/strazzere/APKfuscator](https://github.com/strazzere/APKfuscator) 

APKFuscator作者通过解析修改Dex文件格式，修改类名，使类名字符个数超过255个，使得反汇编器报错。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019c47f0586e824ca6.png)

修改类名使得字符个数超过255个

**2.3.3 对抗**

文献[8]采用的一种反混淆方式就是通过大规模的学习为混淆的APK，然后总结出一个概率模型，通过这个概率模型来识别混淆后的代码。其反混淆流程如下图分为3个步骤：

Step1：生成一个依赖关系图，每个节点代表要重命名的元素，每条线代表依赖关系。

Step2：导出一些限制规则，这些规则可以保证回复的APK是个正常的APK，且和原APK语义相同。

Step3：根据概率模型提供的权重，对混淆的元素的原始名称进行预测和恢复。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01a7d17f8f68cb71a9.png)

作者将论文中的反混淆方法做成了一个在线的反混淆工具提供使用：

[http://apk-deguard.com/](http://apk-deguard.com/) 

**2.4 字符串混淆**

**2.4.1 概念和思路**

很多时候，为了避免反汇编后的代码容易被破解者分析读懂，往往会源程序中一些比较关键的字符串变量进行混淆，使得破解者分析成本提高。这里的字符串混淆有两种，一种是Java层的字符串混淆，另一种是native层的字符串混淆，也就是so文件中的字符串混淆。上面我们介绍了Proguard免费混淆工具，它可以混淆类名、方法名和变量名，但是不支持字符串混淆，要使用字符串混淆就需要使用DexGuard商业版混淆器。

实现思路如下：

(1)	编码混淆

编码混淆就是先将字符串转换成16进制的数组或者Unicode编码，在使用的时候才恢复成字符串。这样破解者在逆向后看到的是一串数字或者乱码，很难直接分析。

如下代码所示，其实就是输出一个Hello World。但是我们硬编码的时候是保存它的ASCII对应的十六进制，在使用的时候才转换成字符。在反编译成smali后，就看不到任何的有意义的字符串了。

Java代码：

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014504041cfe011c95.png)

apktool反编译后的smali代码：

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t016213f2de3cba9d54.png)

同样的在native层的代码也可以使用类似的方式实现对C或C++中的字符串进行混淆。

(2)	加密处理

加密处理就是实现在本地将字符串加密，然后将密文硬编码到源程序中，再实现一个解密函数，在引用密文的地方调用解密函数解密即可。如下图。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013ed2be257d1e54a6.png)

还有一种方式是我们可以修改dex文件。对于Java层的字符串加密，我们可以在dex文件中，找到要加密的字符串在字符串常量表中的位置，然后对它用加密算法加密。然后在自定义Application的attachBaseContext方法中在运行时对密文进行解密，或者可以在native层加密，提高破解难度。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c7b216e9d9b00f22.png)

同样的，我们也可以修改SO文件。SO文件中也存在只读常量区”.rodata”，如下图所示。我们可以根据section header table来找到”.rodata”的位置和大小，然后实现对只读常量区进行加密混淆，在运行的时候再调用相应的解密算法解密即可。

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012fded117d4392662.png)

**2.4.2 开源项目**

[https://github.com/ysrc/obfuseSmaliText](https://github.com/ysrc/obfuseSmaliText)    

obfuseSmaliText是国内同程安全的一个员工实现免费字符串混淆工具，它是通过apktool反编译安装包，在smali层对字符串进行混淆，目前采用的是异或+十六进制的方式进行混淆。效果如下图：

[![](./img/85843/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017d4ba06a72214ef2.png)

**2.4.3 对抗**

对于使用了字符串混淆，只能找到响应的解密函数，调用解密函数去解密就可以恢复明文。

<br>

**三、结束**

这次就写到这里，后面我还会继续补充其他的混淆技术，包括控制流变换、模拟器检测、反调试、Java代码native化等。

<br>

**参考**

[1] obfuscating C++ Programs via Control Flow Flattening 

[http://www.inf.u-szeged.hu/~akiss/pub/pdf/laszlo_obfuscating.pdf](http://www.inf.u-szeged.hu/~akiss/pub/pdf/laszlo_obfuscating.pdf) 

[2]利用符号执行去除控制流平坦化

[https://security.tencent.com/index.php/blog/msg/112](https://security.tencent.com/index.php/blog/msg/112) 

[3] Deobfuscation: recovering an OLLVM-protected program.

[http://blog.quarkslab.com/deobfuscation-recovering-an-ollvm-protected-program.html](http://blog.quarkslab.com/deobfuscation-recovering-an-ollvm-protected-program.html) 

（备注：中文翻译版，[http://www.0daybank.org/?p=7845](http://www.0daybank.org/?p=7845) ）

[4] Evaluating malwares obfuscation techniques against antimalware detection algorithms.

[http://www.iswatlab.eu/wp-content/uploads/2015/09/mobile_antimalware_evaluation.pdf](http://www.iswatlab.eu/wp-content/uploads/2015/09/mobile_antimalware_evaluation.pdf) 

[5] Dalvik Bytecode Obfuscation on Android http://www.dexlabs.org/blog/bytecode-obfuscation

[6] Detecting repackaged android apps using server-side analysis 

[https://pure.tue.nl/ws/files/46945161/855432-1.pdf](https://pure.tue.nl/ws/files/46945161/855432-1.pdf) 

[7] https://github.com/ysrc/AndroidObfuseDictionary

[8] Statistical Deobfuscation of Android Application. [http://www.srl.inf.ethz.ch/papers/deguard.pdf](http://www.srl.inf.ethz.ch/papers/deguard.pdf) 

[9] Android字符串及字典开源混淆实现 https://mp.weixin.qq.com/s/SRv1Oar87w1iKuDXS4oaew

[10] Dex混淆的原理及实现 

[http://burningcodes.net/dex%E6%B7%B7%E6%B7%86%E7%9A%84%E5%8E%9F%E7%90%86%E5%8F%8A%E5%AE%9E%E7%8E%B0/](http://burningcodes.net/dex%E6%B7%B7%E6%B7%86%E7%9A%84%E5%8E%9F%E7%90%86%E5%8F%8A%E5%AE%9E%E7%8E%B0/) 

[11] Android Code Protection via Obfuscation Techniques Past, Present and Future Directions.

[https://arxiv.org/pdf/1611.10231.pdf](https://arxiv.org/pdf/1611.10231.pdf) 

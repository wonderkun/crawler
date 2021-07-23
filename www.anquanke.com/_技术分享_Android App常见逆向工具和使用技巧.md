> 原文链接: https://www.anquanke.com//post/id/84776 


# 【技术分享】Android App常见逆向工具和使用技巧


                                阅读量   
                                **185417**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01cc9bb99218437d05.jpg)](https://p4.ssl.qhimg.com/t01cc9bb99218437d05.jpg)

**前言**

本文将主要介绍个人在Android App逆向分析时常用到的一些工具和小技巧。说起Android 逆向，就不得不提到常用的逆向分析神器了，IDA，jadx，Android Killer，JEB。

<br>

**常用工具介绍**

jadx是一款非常不错的apk反编译工具，可以直接将apk转换成java源码，代码还原度高，且支持交叉索引等等，以一款开源工具为例，反编译后结构图

[![](https://p1.ssl.qhimg.com/t017c9415a2799e5b45.webp)](https://p1.ssl.qhimg.com/t017c9415a2799e5b45.webp)

代码显示效果：

[![](https://p3.ssl.qhimg.com/t01afb137e504065c79.webp)](https://p3.ssl.qhimg.com/t01afb137e504065c79.webp)

排除混淆的影响外，整体看来代码的显示效果基本是跟原工程一样的，非常有逻辑感，右键还可以查看方法和变量的引用，但是jadx的缺点也很多，速度较慢，且不支持变量，方法重命名等等，在针对混淆代码分析时有些力不从心，这里就推荐另一款工具JEB。

JEB是一款非常不错的Android逆向分析工具，新版的JEB也已经支持了app动态调试，但由于不稳定性，暂时还不推荐使用，本文使用版本1.5，由于大部分人都接触过JEB，也知道JEB的常见特性，本文就主要讲解JEB的另一个功能，脚本功能，示例app为RE管理器。反编译后可以看到：

[![](https://p5.ssl.qhimg.com/t01d07b9990784e1a87.webp)](https://p5.ssl.qhimg.com/t01d07b9990784e1a87.webp)

方法中多数字符串已经被转换成了byte数组，这在逆向分析时会比较头大，为了解决这一问题，我们可以尝试写个脚本来还原这些字符串，打开idea，新建一个java工程，导入jeb.jar（该文件在JEB目录下可以找到），第一步，需要知道JEB需要遍历的方法是什么，这里调用了new String方法将byte数组转换成string，那这里就需要匹配new String这个方法，如下

[![](https://p5.ssl.qhimg.com/t019a9dcce25e45c7ed.webp)](https://p5.ssl.qhimg.com/t019a9dcce25e45c7ed.webp)

接下来需要让JEB枚举所有方法

[![](https://p1.ssl.qhimg.com/t01d8a7ce1d120c9a61.webp)](https://p1.ssl.qhimg.com/t01d8a7ce1d120c9a61.webp)

这里主要就是利用JEB的插件功能枚举所有引用到该签名的方法，好处就是节省后面匹配替换的时间，找到关键处后自然就开始替换和解密操作了。

[![](https://p4.ssl.qhimg.com/t010b9771b19ffff25e.webp)](https://p4.ssl.qhimg.com/t010b9771b19ffff25e.webp)

这里主要就是遍历和迭代所有方法中的元素，取到元素后首先需要进行过滤，因为是new String，所以需要判断当前类型是否为New，是的话再去匹配签名值是否跟上面设置的一致，当匹配成功后就可以在元素中取值了，取到值后还需要进行相应的处理，将类型转换成我们需要的byte数组，今后再进行解密和替换，整体逻辑和实现并不复杂，上面的截图也都做了详细的备注，丢张处理后的截图：

[![](https://p4.ssl.qhimg.com/t014f11bb32e6e5e29f.webp)](https://p4.ssl.qhimg.com/t014f11bb32e6e5e29f.webp)

这样分析起来就轻松多了，当然这里只是简单的举了个new String的例子，同样该脚本稍作修改可以解密如des，aes，base64等加密编码操作。

当然说到逆向工程，不得不提的工具当然是IDA，作为一个适应多种平台的逆向分析工具，在安卓上的使用率也非常高，强大的反汇编功能以及F5转伪C代码功能都给分析者提供了便捷，下面以某个CrackeMe演示：

[![](https://p3.ssl.qhimg.com/t016d6e34e0d150a68b.webp)](https://p3.ssl.qhimg.com/t016d6e34e0d150a68b.webp)

常见的native方法有静态注册和动态注册两种形式，静态注册均已java开头，以类的路径命名，所以可以很轻松的找到，双击该方法即可来到汇编代码处，F5后发现代码丢失了很多，如下图：

[![](https://p1.ssl.qhimg.com/t0179119da348ad373e.webp)](https://p1.ssl.qhimg.com/t0179119da348ad373e.webp)

在汇编代码状态下按下空格键即可切换至流程图，如下：

[![](https://p3.ssl.qhimg.com/t0113611102739733c0.webp)](https://p3.ssl.qhimg.com/t0113611102739733c0.webp)

发现该方法被识别出了两个入口点，从而导致很多代码未被识别到，找到第一个分支的结束地方

[![](https://p3.ssl.qhimg.com/t01140d3eceff657431.webp)](https://p3.ssl.qhimg.com/t01140d3eceff657431.webp)

选择菜单栏的Edit-&gt;function-&gt;removefunction tail，之后在修改过后的地方点击菜单栏Edit-&gt;other-&gt;forceBL call 即可，之后再此F5即可正常显示所有代码

[![](https://p3.ssl.qhimg.com/t012aaa6a73b92be83e.webp)](https://p3.ssl.qhimg.com/t012aaa6a73b92be83e.webp)

而动态注册方法较静态注册在寻找关键点时稍加麻烦一点，而动态注册势必会在jni_Onload中去处理这些函数，以某so为例，F5后代码如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01465e2bdd2600c757.webp)

这里会看到很多的偏移地址，其实是指针在jniEnv中的相对位置，此时可以通过导入jni头文件来自动识别，在网上可以很容易下载到这个文件，导入后右键Convert to Struct后代码如下：

[![](https://p3.ssl.qhimg.com/t01cd92840b01051cdd.webp)](https://p3.ssl.qhimg.com/t01cd92840b01051cdd.webp)

这里已经看的很清晰了，调用了RegisterNatives方法注册了两个方法，off_8004则是记录了该方法的偏移地址，双击进入：

[![](https://p4.ssl.qhimg.com/t01b190c9d126052205.webp)](https://p4.ssl.qhimg.com/t01b190c9d126052205.webp)

这里已经看到了两个方法对应的内容，_Z10verifySignP7_JNIENVP8_jobect和_Z13getentyStringv，双击即可跳转到该方法中，当然这些对于ida来说根本都是基础功能，而且新版本的IDA支持直接对字节码进行patch，无需像之前一样记录修改地址，使用16进制编辑器对字节码进行修改，示例如下：

[![](https://p5.ssl.qhimg.com/t0120a1592b8c73821d.webp)](https://p5.ssl.qhimg.com/t0120a1592b8c73821d.webp)

在000025C6处我调用了一个检测当前是否处于调试状态的方法，如果程序被调试器连接上，则会自动崩溃，而readStatus是个void方法，本身不带参数和返回值，思路很简单，nop掉该方法再重新打包即可正常调试，选择菜单栏上的Options-&gt;General

[![](https://p4.ssl.qhimg.com/t018d0bec58d73cf1eb.webp)](https://p4.ssl.qhimg.com/t018d0bec58d73cf1eb.webp)

此处将0改为4即可

[![](https://p4.ssl.qhimg.com/t01a8e9cbc6db4563bf.webp)](https://p4.ssl.qhimg.com/t01a8e9cbc6db4563bf.webp)

此时每条指令对应的机器码已经显示出来，可以看到readStatus是个arm指令，修改方法很简单，常见的nop方法可以使用全0替换机器码

[![](https://p4.ssl.qhimg.com/t01e8f8d15636097872.webp)](https://p4.ssl.qhimg.com/t01e8f8d15636097872.webp)

点击到修改指令后选择菜单栏的Edit-&gt;patch program-&gt;changebyte，修改前4个字节为00 00 00 00即可，效果如下：

[![](https://p1.ssl.qhimg.com/t01c6740acea4ecc5fb.webp)](https://p1.ssl.qhimg.com/t01c6740acea4ecc5fb.webp)

可以看到反调试方法已经被清除掉了，那么如何保存修改后的文件呢，也很简单，点击菜单栏的Edit-&gt;patchprogram-&gt;Apply patches to Input file，直接点击ok即可，当然ida的小技巧还有很多，比如在动态调试时改变android_server的默认端口即可过滤掉反调试对端口23946的检测，命令为-p123 ，123为端口号，记得-p和端口号之间是没有空格的。

最后要介绍的就是Android Killer了，ak是一款不错的apk反编译集成工具，有良好的smali显示效果和编辑功能

[![](https://p1.ssl.qhimg.com/t01e64a9f8d1f43dee8.webp)](https://p1.ssl.qhimg.com/t01e64a9f8d1f43dee8.webp)

当然作为一个反编译工具，这些都是最基本的功能，ak有一项强大的功能是代码插入，可以对代码进行稍加的封装，即可实现快速插入代码，比如个人实现的log插桩插件，是在开源项目LogUtils的基础上转换成了smali插件，支持一键输出任意基本类型的数据以及json,Intent等数据类型，使用方式也很简单，右键选择插入代码即可

[![](https://p4.ssl.qhimg.com/t0114ef99eb43059402.webp)](https://p4.ssl.qhimg.com/t0114ef99eb43059402.webp)

代码就1句话，其中p0是需要打印的寄存器，在静态方法中p0代表是是第一个入参，在逆向工程上，代码插桩可以很好的帮助我们进行数据的分析，这些插件我都发布到了网络上，都可以下载到。

<br>

**总结**

本文主要介绍了Android App逆向时常用的工具和他们的一些使用小技巧，但逆向单靠一样工具和常见的技巧往往还是不够的，需要大家的尝试和耐心以及自身对逆向的钻研精神。

YSRC招移动安全方向负责人，带两人团队，负责app逆向、加固及漏洞挖掘。工作地点苏州总部。可发送简历至 sec@ly.com，或扫描下方二维码关注YSRC公众号咨询，欢迎推荐。

[![](https://p5.ssl.qhimg.com/t014a32243d40487c3c.webp)](https://p5.ssl.qhimg.com/t014a32243d40487c3c.webp)



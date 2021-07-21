> 原文链接: https://www.anquanke.com//post/id/87120 


# 【技术分享】如何使用dex-oracle对抗混淆后的Android恶意软件


                                阅读量   
                                **130353**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：rednaga.io
                                <br>原文地址：[https://rednaga.io/2017/10/28/hacking-with-dex-oracle-for-android-malware-deobfuscation/](https://rednaga.io/2017/10/28/hacking-with-dex-oracle-for-android-malware-deobfuscation/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01a7811f8d8c843703.jpg)](https://p0.ssl.qhimg.com/t01a7811f8d8c843703.jpg)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

大约一两个月以前，有人想让我帮忙分析经过混淆的一些Android恶意软件。最近我终于找到时机能够好好研究一下。最终，我使用了[dex-oracle](https://github.com/CalebFenton/dex-oracle)以及一些技巧部分解开了恶意软件的混淆数据。在本文中，我会介绍我在去混淆方面所使用的一些技巧以及整个过程。如果你需要处理许多混淆的Android应用，这篇文章应该对你有所帮助。

这个过程中，最主要的问题是dex-oracle无法直接使用，我们需要一些“黑科技”方法才能让它正常工作。具体的情况是，我修改了已有的一个去混淆插件，生成了两个新的插件，同时也稍微修改了一下这个工具。想创造完全通用的去混淆工具或者其他高级工具是非常困难的一件事情，所以你需要了解这些工具的工作原理，适当修改以满足你的实际需求。



**二、样本信息**

样本的SHA256值如下所示：



```
$ shasum -a 256 xjmurla.gqscntaej.bfdiays.apk
d3becbee846560d0ffa4f3cda708d69a98dff92785b7412d763f810c51c0b091  xjmurla.gqscntaej.bfdiays.apk
```



**三、整体分析**

我比较喜欢先做个反编译处理，以便能对目标应用的包结构有个整体的认识。应用所包含的类如下所示：

[![](https://p3.ssl.qhimg.com/t01b8e3c2ed537f579f.png)](https://p3.ssl.qhimg.com/t01b8e3c2ed537f579f.png)

有些类名已经被ProGuard处理过（如a、b、c等），但有些类名没有经过处理（如**Ceacbcbf**）。没有经过混淆处理的类很有可能是Android组件类（如Activity（活动）、Service（服务）、Broadcast Receiver（广播接收器等）），**因为这些组件必须在manifest中声明**。因此，如果某些工具想实现自动化重命名这些类，它们就必须在manifest中做相应的重命名处理，这是比较困难的一个过程。这个应用中，这些类名可能被手动修改过。作者可能使用了家庭作坊式的混淆处理方法，部分工作由人工完成。**这意味着这很有可能是一个恶意软件，因为合法的开发者会直接使用商用混淆工具来处理合法应用，他们不会把时间精力浪费在修改类名身上，比如，他们不会把类名修改为Aeabffdccdac之类难以辨类的字符串。**

应用代码经过混淆处理。经过混淆的某个类如下所示：

[![](https://p0.ssl.qhimg.com/t01e122f29fd6d52413.png)](https://p0.ssl.qhimg.com/t01e122f29fd6d52413.png)

你无法从中看到任何字符串或类名，这是非常讨厌的一件事情。看起来[Simplify](https://github.com/CalebFenton/simplify)可以处理这个程序，但我们失算了。没关系，我兜里藏着许多好想法。我们可以来试一下Smali，看看能得到什么结果。



**四、字符串及类混淆方法**

首先，我看到了“基于索引的字符串查找”类型的混淆方法。



```
const v2, 0x320fb26f
invoke-static `{`v2`}`, Lxjmurla/gqscntaej/bfdiays/f;-&gt;a(I)Ljava/lang/String;
move-result-object v2
```

这种模式在代码中出现了好几百次。应用会挑选某个数字，将其传递给**f.a(int)**，然后再返回某个字符串。这种方法在某种程度上类似于“第一层”加密算法。应用在某个地方可能存在一个大型方法，该方法用来构建字符串数组，通过数字来索引字符串。

第二种混淆方法使用了同样的技巧来隐藏类常量。



```
const v1, 0x19189b07
invoke-static `{`v1`}`, Lxjmurla/gqscntaej/bfdiays/g;-&gt;c(I)Ljava/lang/Class;
move-result-object v1
```

这段代码会将一个数字传递给**g.c(int)**，返回某个类对象（**const-class**）。

你可能会认为需要对这些查找方法进行逆向分析，但事实并非如此。写个解密程序来深入分析复杂代码并完全掌握内部细节的确是非常酷的一件事情，但我们可以先不管这些繁琐的事情，对我们来说，速度才是第一要务。我实在不想把时间浪费在恶意软件作者所构造的这个“业余的”混淆程序上。如果不逆向分析的话，我们可以认为这些“查找”方法都是静态的方法。我们应该可以使用与代码中相同的输入来执行这些方法，这样就能得到解密后的输出结果。比如，在字符串解密方面，我应该可以执行**f.a(0x320fb26f)**，返回解密后的字符串。

当然，问题是如何执行这部分代码？我们的对象是一个APK文件，我们如何使用所需的输入数据从中执行特定的方法？也就是说，我们要怎样才能驾驭目标方法？答案有两个：

1、使用[dex2jar](https://github.com/pxb1988/dex2jar)或者[enjarify](https://github.com/google/enjarify)将目标DEX文件转换为JAR。然后，将JAR导入Java应用中，再从Java应用中调用解码函数。

2、创建一个插桩（stub）或者驱动（driver）应用，用来接受命令行参数，反射DEX文件中的方法。然后，在模拟器上执行该应用以及DEX文件。

实际情况中，我选择使用第二种方法，构造了[dex-oracle](https://github.com/CalebFenton/dex-oracle)工具来处理这种场景。这两种方法中，我更喜欢第二种，**因为这种方法无需依赖反编译器，不会引入逻辑问题**。然而，第一种方法我也用了好几次，所以这里也有必要稍微提一下。我已经在dex-oracle中加入对这类混淆机制的支持，所添加的插件可参考“[Add indexed string + class lookups](https://github.com/CalebFenton/dex-oracle/commit/cf44cd7aa5e81d5b0bc9588150b81a0fcdc575fe)”这个页面。

**dex-oracle工作过程**

****

dex-oracle的工作过程非常简单。该工具包含一组插件，插件通过正则表达式提取关键信息，如调用方法以及参数。然后，它会使用提取的参数构造真实的调用方法，并将这些方法传递给驱动，由驱动执行模拟器上的原始DEX文件。最后，插件定义了如何使用驱动的输出结果来修改调用方法。比如，正则表达式可以查找“数字常量、调用静态方法（静态方法接受数字并返回字符串）并将结果移动到寄存器的函数”。然后，驱动使用该数字执行该方法，返回解密后的字符串。最后，原始的字符串查找代码会被解密后的字符串代替。

你可以参考[TetCon 2016上有关Android去混淆方面的演讲](https://www.slideshare.net/tekproxy/tetcon-2016)来了解更多细节。



**五、修改前的dex-oracle**

不幸的是，即便使用新的插件，dex-oracle依然无法得到正确结果。为了便于查找问题，我禁用了除**IndexStringLookup**之外的所有插件，然后只处理上图中的d类。



```
$ dex-oracle xjmurla.gqscntaej.bfdiays.apk --disable-plugins bitwiseantiskid,stringdecryptor,undexguard,unreflector,indexedclasslookup -i '/d'
Invalid date/time in zip entry
Invalid date/time in zip entry
Invalid date/time in zip entry
Invalid date/time in zip entry
Invalid date/time in zip entry
Invalid date/time in zip entry
Invalid date/time in zip entry
Invalid date/time in zip entry
Invalid date/time in zip entry
Optimizing 11 methods over 23 Smali files.
[WARN] 2017-10-28 12:28:45: Unsuccessful status: failure for Error executing 'static java.lang.String xjmurla.gqscntaej.bfdiays.f.a(int)' with 'I:839889519'
java.lang.reflect.InvocationTargetException
    at java.lang.reflect.Method.invokeNative(Native Method)
    at java.lang.reflect.Method.invoke(Method.java:515)
    at org.cf.oracle.Driver.invokeMethod(Driver.java:71)
    at org.cf.oracle.Driver.main(Driver.java:131)
    at com.android.internal.os.RuntimeInit.nativeFinishInit(Native Method)
    at com.android.internal.os.RuntimeInit.main(RuntimeInit.java:243)
    at dalvik.system.NativeStart.main(Native Method)
Caused by: java.lang.NullPointerException
    at xjmurla.gqscntaej.bfdiays.f.a(SourceFile:528)
    ... 7 more
// ** SNIP MANY SIMILAR ERRORS **
Optimizations: string_lookups=13
Invalid date/time in zip entry
// ** SNIP DUMB WARNINGS **
Invalid date/time in zip entry
Time elapsed 1.954255 seconds
```

上述结果中，“Invalid date/time in zip entry”提示信息为无用的噪音信息。可能是恶意应用作者在尝试混淆ZIP中的时间戳？这一点我并不确定。

我关心的是“Unsuccessful status: failure for Error executing 'static java.lang.String xjmurla.gqscntaej.bfdiays.f.a(int)' with 'I:839889519'”这个信息。根据这个提示信息，工具在执行f.a(int)时出现了一个**NullPointerException**（空指针异常）现象。看起来工具每次调用这个方法时都会失败。所以，我们可以来分析一下f.a(int)。



```
.method static a(I)Ljava/lang/String;
    .registers 3
    sget-object v0, Lxjmurla/gqscntaej/bfdiays/f;-&gt;k:[Ljava/lang/String;
    const v1, 0x320fb1f0
    sub-int v1, p0, v1
    aget-object v0, v0, v1
    return-object v0
.end method
```

整个方法非常小巧。这段代码的功能是从一个大的常量中提取出第一个参数，使用该参数作为索引查找一个字符串数组，Lxjmurla/gqscntaej/bfdiays/f;-&gt;k:[Ljava/lang/String;。我们可以来看看f;-&gt;k的初始化过程。



```
$ ag -Q 'Lxjmurla/gqscntaej/bfdiays/f;-&gt;k:[Ljava/lang/String;'
xjmurla/gqscntaej/bfdiays/Ceacabcbf.smali
169:    sput-object v0, Lxjmurla/gqscntaej/bfdiays/f;-&gt;k:[Ljava/lang/String;
245:    sget-object v0, Lxjmurla/gqscntaej/bfdiays/f;-&gt;k:[Ljava/lang/String;
256:    sget-object v0, Lxjmurla/gqscntaej/bfdiays/f;-&gt;k:[Ljava/lang/String;
xjmurla/gqscntaej/bfdiays/f.smali
72:    sget-object v0, Lxjmurla/gqscntaej/bfdiays/f;-&gt;k:[Ljava/lang/String;
```

我们只找到一个**sput-object**，位于**xjmurla/gqscntaej/bfdiays/Ceacabcbf.smali**中。在Ceacabcbf中查找这一行，我们找到了**private Ceacabcbf;-&gt;a()V**。这个方法篇幅很长，也非常复杂，包含一大串字符串，这个字符串经过处理、分解后存放在f;-&gt;k中。出错点找到了，正是这个字段没有被初始化，导致我们出现NullPointerException错误。这意味着执行字符串解密方法过程中，Ceacabcbf;-&gt;a()V并没有被调用。因此，我们来找找该函数的调用位置。



```
$ ag -Q 'Lxjmurla/gqscntaej/bfdiays/Ceacabcbf;-&gt;a()V'
xjmurla/gqscntaej/bfdiays/Ceacabcbf.smali
1313:    invoke-direct `{`p0`}`, Lxjmurla/gqscntaej/bfdiays/Ceacabcbf;-&gt;a()V
看样子该方法仅在Ceacabcbf被调用，具体代码为：
.method public onCreate()V
    .registers 1
    invoke-super `{`p0`}`, Landroid/app/Application;-&gt;onCreate()V
    sput-object p0, Lxjmurla/gqscntaej/bfdiays/Ceacabcbf;-&gt;a:Lxjmurla/gqscntaej/bfdiays/Ceacabcbf;
    invoke-direct `{`p0`}`, Lxjmurla/gqscntaej/bfdiays/Ceacabcbf;-&gt;a()V
    return-void
.end method
```

该方法的具体调用位置位于Ceacabcbf;-&gt;onCreate()V中。这个类是Application的一个子类。不需要看manifest文件，我百分百确定当应用启动时会创建这个组件，然后调用onCreate()V方法，构建解密字符串数组，然后初始化f;-&gt;k，初始化也是最重要的一个步骤。那么我该如何重复这个操作，以便dex-oracle在解密字符串时能调用这个函数呢？

我首先想到的是往f;-&gt;&lt;clinit&gt;中的Ceacabcbf;-&gt;a()V内添加一个调用方法。这样就能确保当字符串解密类f被加载时，会初始化解密字符串数组。然而，a()V是一种直接（direct）方法，这种情况下怎么办？

我使用了有点笨的一种方法，但某些情况下这种方法能发挥作用。只需要创建一个新的公开的静态方法（Ceacabcbf;-&gt;init_decrypt()V），方法内容从Ceacabcbf;-&gt;a()V那复制即可。然后，在f;-&gt;&lt;clinit&gt;中添加一行语句来调用这个方法：



```
.method static constructor &lt;clinit&gt;()V
    .registers 1
    const/4 v0, 0x0
    sput v0, Lxjmurla/gqscntaej/bfdiays/f;-&gt;a:I
    sput v0, Lxjmurla/gqscntaej/bfdiays/f;-&gt;d:I
    sput v0, Lxjmurla/gqscntaej/bfdiays/f;-&gt;e:I
    sput v0, Lxjmurla/gqscntaej/bfdiays/f;-&gt;f:I
    const/4 v0, 0x4
    new-array v0, v0, [Ljava/lang/String;
    sput-object v0, Lxjmurla/gqscntaej/bfdiays/f;-&gt;h:[Ljava/lang/String;
    const-string v0, ""
    sput-object v0, Lxjmurla/gqscntaej/bfdiays/f;-&gt;i:Ljava/lang/Object;
     # LOL MONEY, MONEY LOL
    invoke-static `{``}`, Lxjmurla/gqscntaej/bfdiays/Ceacabcbf;-&gt;init_decrypt()V
    return-void
.end method
```



**六、修改后的dex-oracle**

做了上述修改后，我们需要根据修改版的Smali重建DEX文件，然后尝试使用dex-oracle来处理这个文件。



```
$ smali ass out -o xjmurla_mod1.dex
$ dex-oracle xjmurla_mod1.dex --disable-plugins bitwiseantiskid,stringdecryptor,undexguard,unreflector,indexedclasslookup -i '/d'
Optimizing 11 methods over 23 Smali files.
Optimizations: string_lookups=13
Time elapsed 2.034493 seconds
```

没有看到错误提示。来看看反编译结果。



```
$ d2j-dex2jar.sh xjmurla_mod1_oracle.dex
dex2jar xjmurla_mod1_oracle.dex -&gt; ./xjmurla_mod1_oracle-dex2jar.jar
$ jd xjmurla_mod1_oracle-dex2jar.jar
```

[![](https://p3.ssl.qhimg.com/t017a9513d8e37865cc.png)](https://p3.ssl.qhimg.com/t017a9513d8e37865cc.png)

抓到你了！C&amp;C控制域名！先得瑟一下。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01139442702b14d1c8.gif)

结果不错，但此时类还没有去混淆。听起来令人非常讨厌。为了不让本文过于冗长，这里我直接告诉你处理过程。在对类做去混淆处理时，与处理混淆字符串时的情况一下，dex-oracle依然会出现错误。我们同样需要调用Ceacabcbf;-&gt;a()V方法。

我们还是可以使用相同的技巧：只要调用g;-&gt;&lt;clinit&gt;中的Ceacabcbf;-&gt;init_decrypt()V即可。然而，g并不包含&lt;clinit&gt;方法，所以我们需要手动添加一个：



```
.method static constructor &lt;clinit&gt;()V
    .registers 0
    invoke-static `{``}`, Lxjmurla/gqscntaej/bfdiays/Ceacabcbf;-&gt;init_decrypt()V
    return-void
.end method
```

现在，重新构建文件，然后使用dex-oracle进行处理：



```
$ smali ass out -o xjmurla_mod2.dex
$ dex-oracle xjmurla_mod2.dex  -i '/d'
Optimizing 11 methods over 23 Smali files.
Optimizations: string_decrypts=0, class_lookups=13, string_lookups=13
Time elapsed 3.099335 seconds
```

来看看处理后的反编译结果有什么区别。



```
$ d2j-dex2jar.sh xjmurla_mod2_oracle.dex
dex2jar xjmurla_mod1_oracle.dex -&gt; ./xjmurla_mod2_oracle-dex2jar.jar
$ jd xjmurla_mod1_oracle-dex2jar.jar
```

[![](https://p1.ssl.qhimg.com/t01e34366d02fcd3963.png)](https://p1.ssl.qhimg.com/t01e34366d02fcd3963.png)

经过处理后，这个方法本身变化不大，然而其他方法可以提供更多信息，特别是在Smali中，你可以看到许多const-class。所有都处理完毕后，还有个g.c(int)没有去掉混淆，经过进一步分析，我发现这是因为该方法调用成功，但返回了空值（null）。也许这就是为什么该方法会位于try-catch代码段中。也许该代码正试图加载每个Android API版本中都不存在的类。

最后，让我们来测试一下，使用dex-oracle分析整个DEX文件。



```
$ dex-oracle xjmurla_mod2.dex
Optimizing 125 methods over 23 Smali files.
Optimizations: string_decrypts=0, class_lookups=354, string_lookups=330
Time elapsed 3.306326 seconds
```

成功了，非常酷。现在还有许多事情要处理。经过处理后，再由Simplify处理起来会更加简单，因为此时需要执行的代码更少，出错点也更少。



**七、总结**

希望阅读本文后，你对如何改造dex-oracle以适应具体需求有了更深刻的理解。如果你可以将待运行的代码细化成待运行的某个方法，这种结果会更加灵活也更加优秀。某些时候，我们需要修改Android应用以适配dex-oracle，但修改Smali是相对简单的一种方法，并且许多恶意软件会带有防篡改机制，这种情况下，你可以采用更加明智的选择。

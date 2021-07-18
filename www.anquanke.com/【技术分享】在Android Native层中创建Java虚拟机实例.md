
# 【技术分享】在Android Native层中创建Java虚拟机实例


                                阅读量   
                                **120451**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](./img/85880/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：calebfenton.github.io
                                <br>原文地址：[https://calebfenton.github.io/2017/04/05/creating_java_vm_from_android_native_code/](https://calebfenton.github.io/2017/04/05/creating_java_vm_from_android_native_code/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85880/t0165551115fd7a63a1.png)](./img/85880/t0165551115fd7a63a1.png)**

翻译：[大脸猫](http://bobao.360.cn/member/contribute?uid=52887766)

预估稿费：140RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**前言**

Android应用中JNI代码，是作为本地方法运行的。而大部分情况下，这些JNI方法均需要传递Dalvik虚拟机实例作为第一个参数。例如，你需要用虚拟机实例来创建jstring和其他的Java对象、查找类或成员变量等。大部分情况下，在你用JNI接口从Java层调用Native层中的代码时，你并不需要在native代码中自己初始化一个Dalvik虚拟机实例。但是，如果你在搞逆向或者写exp，你总是需要钻研各种非常规的情况。

最近，我在逆向时需要在native代码中手动创建虚拟机实例用于在JNI接口函数中传递Java对象。在本文中，我将分享我是如何实现这种方法的。

<br>

**标准方法**

在JNI中创建JVM虚拟机实例的官方文档在地址[How to Create a JVM Instance in JNI](http://www.developer.com/java/data/how-to-create-a-jvm-instance-in-jni.html)。但是，不幸的是这种方法在Android上面是不能正常运行的，因为jint JNI_CreateJavaVM(JavaVM**, JNIEnv**, void*)函数不是导出函数，无法直接调用。假如你不熟悉这个方法的话，可以根据它的名字在jni.h文件中查找一下，确认是否是导出函数。在我这里，jni.h文件位于android-sdk/ ndk-bundle/platforms/android-9/arch-x86/usr/include/jni.h。相关代码如下：

[![](./img/85880/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d22fad16c69e4c96.png)

如果你尝试编译调用上述截图中函数的代码，你可能会得到下面的错误：

[![](./img/85880/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0127156f52c81a3f0a.png)

官方文档中介绍的如何创建JVM的方法在这里可以用来理解上述的API函数和它们的选项和参数的用途。如果你想在Android中使用这些方法，你必须显示从so库中调用这些方法。

官方文档中介绍的如何初始化虚拟机的类路径，在此处是非常有用的。其内容如下：

[![](./img/85880/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01264734bd0b9859bb.png)

上面的配置，设置当前的类路径为当前目录（.）。如果你想要虚拟机访问系统或者app的类，这是必须设置的。实验表明，将该值设置为一个目录并不会起作用。我尝试将其设置为/data/local/tmp，同时在该目录下放置了一个dex文件、含有dex文件的jar包和apk文件。只有在设置jar包、dex文件或apk文件的全路径时，上述选项才起作用。奇怪的是，当类路径中没有一个合法的文件时，系统类（例如java.lang.String）都不能访问。换句话说，除非类路径中至少有一个文件，否则语句(*env)-&gt;FindClass(env, "java.lang.String")返回0，甚至java.lang.String这样定义在框架中的类都无法访问。

为了测试，下面将一个apk文件push到模拟器或真机设备中。

[![](./img/85880/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010896674355a66a32.png)

JavaVMOption的使用如下：

[![](./img/85880/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01918631a83aae8ebe.png)

你现在可以使用FindClass函数来加载系统或者app的类。此外，如果你需要加载本地库到你的虚拟机中，例如在静态初始化器中加载一个库文件，你可以使用optionString = "-Djava.library.path=/data/local/tmp"这样的设置。这有个[样例代码](http://docs.oracle.com/javase/7/docs/technotes/guides/jni/jni-12.html#invo)。

<br>

**UniccUnlock方法**

从文件[UniccUnlock.cpp](https://gist.github.com/tewilove/b65b0b15557c770739d6#file-uiccunlock-cpp)中，展示了另外一种创建虚拟机的类似技巧。我不敢说我完全理解了它在做什么，但是其中吸引我的是get_transaction_code部分。下面是它的做的事：



```
creates a Java VM
use the VM to get reference to com.android.internal.telephony.ITelephony$Stub class
get the TRANSACTION_sendOemRilRequestRaw field value
destroy the VM
return field value
```

代码看起来像是根据成员值判断当前设备是否已经解锁或者是解锁方法是否成功。反正我是不很确定，不过我也就想抽取其中创建虚拟机的代码而已。

该方法是通过在库文件libnativehelper.so或者libdvm.so中加载创建虚拟机相关的方法。但是，下面几行代码看起来很奇怪：

[![](./img/85880/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ed3901ce31106d5b.png)

任何地方都无法找到这几个方法的文档说明。不过，发现这些方法调用的人相当聪明。如果不调用这些方法，你就会得到下面奇怪的错误信息：

[![](./img/85880/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d61d67557f98d4ee.png)

除了这几个奇怪的方法，这种方式创建虚拟机对我很好使。但是，我想知道_ZN13JniInvocationC1Ev方法都做了什么，在不同版本间的Android系统中是否可移植。我的直觉告诉我，硬编码的方法名可能会导致在不同的设备或者Android版本间的不兼容性。

<br>

**Surfaceflinger 方法**

最终，我在谷歌的Surfaceflinger服务的源码中找到了：[DdmConnection.cpp](https://android.googlesource.com/platform/frameworks/native/+/ce3a0a5/services/surfaceflinger/DdmConnection.cpp)。

它默认查找了在libdvm.so中的函数JNI_CreateJavaVM。它没有调用方法_ZN13JniInvocation，而是调用了库libandroid_runtime.so中的Java_com_android_internal_util_WithFramework_registerNatives方法。registerNatives方法的内容[在此描述](http://stackoverflow.com/questions/1010645/what-does-the-registernatives-method-do)了。

同时，感兴趣的是创建虚拟机的选项：

[![](./img/85880/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015d27964f7c3cb2b7.png)

这些选项在[这篇文档](http://www.netmite.com/android/mydroid/2.0/dalvik/docs/debugger.html)中详细描述了。根据文档，它仅仅用于调试JVM时使用。

同时，我注意到它JNI的版本是1_4，但是我设置为1_6了，因为谷歌的[样例代码](https://developer.android.com/training/articles/perf-jni.html#native_libraries)中就是这样设置的。下面就是jni.h中支持的版本号:

[![](./img/85880/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013ada4bdf0632e34d.png)

最后，我使用上面的方式来创建虚拟机，因为它来自谷歌，具有很好的健壮性和兼容性。

<br>

**最终代码**

下面就是最终的创建虚拟机的代码：

[![](./img/85880/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t011035a70c2ef40b44.png)

下面是其使用方法：

[![](./img/85880/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t015b8dc79e0f20661c.png)

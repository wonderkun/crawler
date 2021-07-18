
# 【技术分享】如何从命令行调用Android JNI函数并传递Java对象参数


                                阅读量   
                                **95583**
                            
                        |
                        
                                                                                                                                    ![](./img/85942/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：calebfenton.github.io
                                <br>原文地址：[https://calebfenton.github.io/2017/04/14/calling_jni_functions_with_java_object_arguments_from_the_command_line/](https://calebfenton.github.io/2017/04/14/calling_jni_functions_with_java_object_arguments_from_the_command_line/)

译文仅供参考，具体内容表达以及含义原文为准

**[![](./img/85942/t01367645bffa5ba8d7.jpg)](./img/85942/t01367645bffa5ba8d7.jpg)**



翻译：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：200RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿

**<br>**

**一、前言**

当我们对某个使用原生库（native library）的恶意软件或者应用进行分析或渗透测试时，如果能够对库函数进行隔离和执行是再好不过的事情，这样做我们就可以使用其自身的代码来调试对抗恶意软件。举个例子，如果恶意软件包含加密字符串，并使用原生函数完成解密过程，你可以选择花大量时间逆向分析算法来编写自己的解密函数，也可以选择直接利用这个函数来处理任意输入数据。如果使用后一种方法，即使恶意软件作者完全改变了软件的加密算法，你也可能不需要做任何修改即可完成任务。在这篇文章中，我将向读者介绍如何利用并执行原生库函数，即使调用这些函数时需要传入JVM实例作为参数也没问题。

在之前的一篇[文章](https://calebfenton.github.io/2017/04/05/creating_java_vm_from_android_native_code/)中，我介绍了如何从Android原生代码中创建一个Java虚拟机，但我没有给出一个具体的例子。因此，我会在本文中给出一个具体的例子来说明这一点。

我们至少可以使用两种方法来调用原生函数。第一种方法是对应用进行修改，使应用接受你的输入数据并传递给原生函数。例如，你可以写一个intent filter，将其转化为[Smali](https://calebfenton.github.io/2016/07/31/understanding_dalvik_static_fields_1_of_2/)语言，将代码添加到目标应用中，修改manifest文件，运行应用，使用adb命令将带有参数的intent发送给目标应用即可。另一种方法更好，你可以添加一个小型socket或web服务器，使用curl向其发送请求，这种方法不需要修改manifest文件。

第二种方法的目标是创建一个通过命令行运行的小型原生可执行工具，用来加载库文件、调用目标函数、传递我们输入的任意参数。这样我们就可以单独运行一个可执行文件，而不需要运行整个应用程序，因此调试起来也就更为方便。

<br>

**二、目标应用**

我创建了一个示例应用，方便读者按照教程学习，应用名为“[native-harness-target](https://github.com/CalebFenton/native-harness-target)”。你可以使用以下命令将工程文件复制到本地并完成编译（记得修改其中的“$ANDROID_*”变量）。



```
git clone https://github.com/CalebFenton/native-harness-target.git
cd native-harness-target
echo 'ndk.dir=$ANDROID_NDK' &gt; local.properties
echo 'sdk.dir=$ANDROID_SDK' &gt;&gt; local.properties
./gradlew build
```

APK文件最终生成在“app/build/outputs/apk/”目录。这篇文章中，我使用的是一个x86模拟器镜像以及一个名为“app-universal-debug.apk”的应用。

该应用程序包含一个加密字符串，并会在运行时使用原生库对字符串进行解密。以下是在Smail中字符串的解密过程：



```
const/16 v3, 0x57
new-array v1, v3, [B
fill-array-data v1, :array_2a
.local v1, "encryptedStringBytes":[B
invoke-static {}, Lorg/cf/nativeharness/Cryptor;-&gt;getInstance()Lorg/cf/nativeharness/Cryptor;
move-result-object v0
.line 21
.local v0, "c":Lorg/cf/nativeharness/Cryptor;
# v3 contains a String made from encrypted bytes
new-instance v3, Ljava/lang/String;
invoke-direct {v3, v1}, Ljava/lang/String;-&gt;&lt;init&gt;([B)V
# Call the decryption method, move result back to v3
invoke-virtual {v0, v3}, Lorg/cf/nativeharness/Cryptor;-&gt;decryptString(Ljava/lang/String;)Ljava/lang/String;
move-result-object v3
```



**三、构建Harness工具**

我使用的是Tim 'diff' Strazzere开发的一款名为“native-shim”的工具（Tim是RedNaga的一名成员）作为整套利用工具的基础，我将这个工具命名为“Harness”。在Android中，shim就像一个中间垫片，作用是加载一个库，并调用其“JNI_OnLoad”方法。它可以使调试工作更加简单，我们只需要使用调试器启动shim，并将具体路径以参数形式传递给目标库即可。我们可以设置调试器的断点，在库加载时触发断点，这样就能进入“JNI_OnLoad”函数的处理流程。此外，native-shim还可以加载库文件（.so文件）、获取函数的引用并调用函数，这一切对我们来说都非常实用。

首先，我添加了部分代码以初始化一个Java虚拟机实例，并将该实例传递给JNI_OnLoad函数，这样处理可以使JNI的初始化过程更为准确。如果没有真实的虚拟机实例，JNI库的内部状态看起来可能会有些奇怪。不同库文件的JNI_OnLoad的实现可能不尽相同，但这并不重要，重要的是这些实现都会检查JNI版本，如这段代码所示。因此我们需要创建一个虚拟机实例。



```
printf(" [+] Initializing JavaVM Instancen");
JavaVM *vm = NULL;
JNIEnv *env = NULL;
int status = init_jvm(&amp;vm, &amp;env);
if (status == 0) {
  printf(" [+] Initialization success (vm=%p, env=%p)n", vm, env);
} else {
  printf(" [!] Initialization failure (%i)n", status);
  return -1;
}
printf(" [+] Calling JNI_OnLoadn");
onLoadFunc(vm, NULL);
```

我们的最终目标是通过harness工具，开启一个socket服务器，读取socket上传输的参数，使用这些参数来调用函数。这样一来，解密函数就会变成一个服务，我们可以简单使用一个Python脚本与其通信。

<br>

**四、理解目标函数**

在调用函数前，我们需要了解函数的签名（即参数个数和参数类型）及函数的返回类型。我们可以先看一下org.cf.nativeharness.Cryptor类的反编译代码，类中包含decryptString原生方法的声明，如下所示：



```
public class Cryptor {
    private static Cryptor instance = null;
    public static Cryptor getInstance() {
        if (instance == null) {
            instance = new Cryptor();
        }
        return instance;
    }
    public native String decryptString(String encryptedString);
}
```

从这段代码中，我们可知该方法使用了一个String对象作为参数，返回了一个String对象，看上去比较简单。现在我们将其转化为原生函数形式，如下所示：

```
Java_org_cf_nativeharness_Cryptor_decryptString(JNIEnv *env, jstring encryptedString)
```

每个JNI原生方法都需要将JNIEnv对象作为第一个参数。这意味着定义我们函数的typedef语句应该如下所示：

```
typedef jstring(*decryptString_t)(JNIEnv *, jstring);
```

不幸的是，如果你试图使用上述typedef语句执行这个函数，你会得到一个错误信息，如下所示：



```
E/dalvikvm: JNI ERROR (app bug): attempt to use stale local reference 0x1
E/dalvikvm: VM aborting
A/libc: Fatal signal 6 (SIGABRT) at 0x00000a9a (code=-6), thread 2714 (harness)
```

这让我困惑了好一阵子。我原先以为我可能在某个地方使用了空指针引用，因此我花了很多功夫，添加了许多printf语句，将内存中所有相关指针的位置全部打印出来。这个错误信息貌似在提示我某个参数出现了问题，但我排查后发现所有指针都是正常的，没有空引用情况。

我敢肯定我传递的参数没有问题，问题可能出在JNI上。为了证实这一点，我使用了javah命令，它可以生成实现原生方法所需要的C语言头文件以及源代码文件。

为了完成这个工作，你需要安装dex2jar，找到正确的类路径，将“platforms/android-19”改为你已经安装的具体平台，如下所示：



```
$ d2j-dex2jar.sh app-universal-debug.apk
dex2jar app-universal-debug.apk -&gt; ./app-universal-debug-dex2jar.jar
$ javah -cp app-universal-debug-dex2jar.jar:$ANDROID_SDK/platforms/android-19/android.jar org.cf.nativeharness.Cryptor
```

上述命令可以生成“_org_cf_nativeharness_Cryptor.h_”文件，其中包含如下信息：

```
JNIEXPORT jstring JNICALL Java_org_cf_nativeharness_Cryptor_decryptString(JNIEnv *, jobject, jstring);
```

我们可以看到多了一个jobject作为第二个参数，这究竟是为什么？如果你已经知道了这个问题的答案，我敢打赌你已经花了很多时间深入学习了Smali，特别是其中的invoke-virtual方法。无论你在何时调用虚拟方法（通常都是些非静态方法），第一个参数总是某个对象的实例，这个实例负责方法的具体实现。对于这个例子来说，此时第一个参数应该是“org.cf.nativeharness.Cryptor”类的一个实例。

当然，你可以投机取巧，比如可以查看str-crypt.c代码，找到函数的具体调用形式。但你要知道你是个逆向分析师（或渗透测试员），你不可能拿到源代码。

因此正确的typedef语句中应该包含Cryptor实例的一个jobject对象，如下所示：

```
typedef jstring(*decryptString_t)(JNIEnv *, jobject, jstring);
```

你可能会感到好奇，为什么我们不以静态方法开始介绍？没有特别的理由，主要是因为我在写这篇博客时，所分析的原始应用中目标方法不是静态方法，仅此而已。

这一部分内容最大的收获就是，如果你不确定函数的具体调用形式，你可以试一下javah命令，时刻牢记虚拟方法与Java中的Method#invoke()类似，使用某个实例对象作为第一个参数。

<br>

**五、构建Socket服务器**

这是整个工作中最无趣的一个环节，如果你不介意的话，我会跳过这一部分。你可以自行查看具体的实现源码，如果愿意的话也可以提出修改意见。

<br>

**六、Harness工具的使用方法**

你可以通过如下几个步骤来使用Harness工具。

	1、启动模拟器

	2、将harness push到设备中

	3、将目标原生库及其他依赖库push到设备中（本文示例中不涉及到依赖库）

	4、将目标应用push到设备中

	5、运行harness工具

	6、将模拟器的端口转发到宿主机上

	7、运行“decrypt_string.py”，祈祷一切顺利

	你可以使用以下命令将应用及原生库push到设备中。



```
$ adb push app/build/output/apk/app-universal-debug.apk /data/local/tmp/target-app.apk
$ unzip app/build/outputs/apk/app-universal-debug.apk lib/x86/libstr-crypt.so
Archive:  app/build/outputs/apk/app-universal-debug.apk
  inflating: lib/x86/libstr-crypt.so
$ adb push lib/x86/libstr-crypt.so /data/local/tmp
lib/x86/libstr-crypt.so: 1 file pushed. 1.5 MB/s (5476 bytes in 0.004s)
```

使用如下命令将harness工具push到设备中。



```
cd harness
make &amp;&amp; make install
```

	注意：以上命令会将x86库push到设备中，如果你确实想要使用其他的模拟器镜像，你可以使用“adb push libs/&lt;your emulator flavor&gt;/harness /data/local/tmp”命令替换“make install”命令。

	现在，你可以运行harness，将目标库路径作为第一个参数传入，如下所示：



```
$ adb shell /data/local/tmp/harness /data/local/tmp/libstr-crypt.so
[*] Native Harness
 [+] Loading target: [ /data/local/tmp/libstr-crypt.so ]
 [+] Library Loaded!
 [+] Found JNI_OnLoad, good
 [+] Initializing JavaVM Instance
WARNING: linker: libdvm.so has text relocations. This is wasting memory and is a security risk. Please fix.
 [+] Initialization success (vm=0xb8e420a0, env=0xb8e420e0)
 [+] Calling JNI_OnLoad
 [+] Found decryptString function, good (0xb761f4f0)
 [+] Finding Cryptor class
 [+] Found Cryptor class: 0x1d2001d9
 [+] Found Cryptor.getInstance(): 0xb27bc270
 [+] Instantiated Cryptor class: 0x1d2001dd
 [+] Starting socket server on port 5001
```

	为了测试工具是否正常工作，你可以在另一个终端上运行如下命令：



```
$ ./decrypt_string.py
Sending encrypted string
Decrypted string: "Seek freedom and become captive of your desires. Seek discipline and find your liberty."
```

	如果你在输出结果中看到解密后的字符串，表明一切顺利，非常完美。

<br>

**七、总结**

你可以根据实际情况，修改harness工具源码中的目标函数。另外，实际场景中，目标程序错综复杂，我并不能保证这种方法100%有效。

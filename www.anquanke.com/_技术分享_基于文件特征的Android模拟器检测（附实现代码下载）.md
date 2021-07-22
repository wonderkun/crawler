> 原文链接: https://www.anquanke.com//post/id/85173 


# 【技术分享】基于文件特征的Android模拟器检测（附实现代码下载）


                                阅读量   
                                **177990**
                            
                        |
                        
                                                                                    





[![](https://p4.ssl.qhimg.com/t0153785844d6193270.jpg)](https://p4.ssl.qhimg.com/t0153785844d6193270.jpg)

在我们开发的App中，我们可能不希望它被运行在模拟器上，所以我们需要一种手段去检测模拟器，当当前设备被检测为模拟器时，我们就直接结束掉App进程。目前常见的检测模拟器手段主要被应用在游戏领域和加固领域。

通常我们去检测模拟器时会利用一些Android系统的运行特征，但这些方式比较复杂也比较难以理解，需要对Android系统有比较深入的了解，如何有一种办法比较高容错率并且检测效果还不错呢，之前，一般的检测模拟器的手段都是通过检测一些系统特定属性，如检测当前设备手机号，设备DeviceId，dev下是否存在socket/qemud和qemu_pipe两个文件，以及build.prop下的一些属性，在分析某赚软件时，它正是使用的这种检测方式，但是当当前设备被root后，就可以通过安装一些修改设备信息的软件来躲避这种检测方式，最近在看到某款游戏的检测手段时，看到了基于文件特征的检测方式，在这个基础上我又加了一些检测方式用来判断模拟器。

目前市面上流行的Android模拟器主要有Genymotion，天天模拟器，夜神模拟器，海马玩模拟器，畅玩模拟器，itools模拟器，逍遥模拟器，文卓爷模拟器，原生Android模拟器，BlueStacks，我们都知道除了原生模拟器之外，大部分Android模拟器都是基于VirtualBox的，这是重要的检测点之一，其次相比于手机，模拟器上少了一些重要特征，如蓝牙功能，温度传感器等等，这些都是可以用来检测模拟器的依据，同时，每种定制版本的模拟器上，都会有一些它特有的可执行文件，如下是我在测试多种模拟器时收集的特征文件：

```
if (anti("/system/lib/libdroid4x.so")) `{`   //文卓爷
`}`
if (anti("/system/bin/windroyed")) `{`   //文卓爷
`}`
if (anti("/system/bin/microvirtd")) `{`  //逍遥
`}`
if (anti("/system/bin/nox-prop")) `{`  //夜神
`}`
if (anti("/system/bin/ttVM-prop")) `{` //天天模拟器
`}`
```

如上图，每个模拟器都编译了自己的动态库或是可执行文件，这些文件在手机上是不存在的，那么我们就可以以此来判断当前设备是否是模拟器，如何去检测该模拟器是否存在也很简单，anti函数如下：

```
int anti(char *res) `{`
    struct stat buf;
    int result = stat(res, &amp;buf) == 0 ? 1 : 0;
    if (result) `{`
        LOGE("the %s is exist", res);
        //    LOGE("this is a Emulator!!!");
    `}`
    return result;
`}`
```

C提供了一个stat函数用来判断当前文件是否存在，如果执行成功则会返回0，使用这种检测手段就需要去收集大量的模拟器特征，在测试时，本人也碰到了一些问题，如检测这个文件时：

```
anti("/system/lib/libc_malloc_debug_qemu.so");
//在cm，魔趣等基于aosp改版的系统上会存在libc_malloc_debug_qemu.so这个文件
```

我发现在一些debug版本的定制版系统上都存在这个文件，但测试了大量官方rom时都是没有问题的，所以这种方式的可靠度是不够高的，本人在这个判断的基础上再去判断了一次，如下：

```
if (anti("/system/lib/libc_malloc_debug_qemu.so")) `{`
    //在cm，魔趣等基于aosp改版的系统上会存在libc_malloc_debug_qemu.so这个文件
    if (access("/system/lib/libbluetooth_jni.so", F_OK) != 0) `{`
        LOGE("the bluetooth is not exist");
        i++;//在误报情况下，再去检测当前设备是否存在蓝牙，不存在则判断为模拟器
    `}`
`}`
```

目前市面上手机都是拥有蓝牙功能的，设备用于蓝牙功能时，我们发现系统的system/lib下有一个libbluetooth_jni.so文件，而这个文件在模拟器上是不存在的。

此类类似的特征文件还有一些，这里就不一个个列举了，除了检测这些固定文件外，我们还可以去检测一些模拟器特定的系统属性，在adb shell下输入getprop即可看到大量系统属性，所以这里就是通过一定系统属性去检测当前设备，如init.svc.vbox86-setup（基于VirtualBox的模拟器都会存在该属性）：

[![](https://p0.ssl.qhimg.com/t014e7d3a2e588ab21a.png)](https://p0.ssl.qhimg.com/t014e7d3a2e588ab21a.png)

通过一些测试我们可以过滤出一些比较敏感的信息，这些属性我们都可以用作检测模拟器的手段，在so里去获取这些属性也很简单，系统为我们提供了现成的api函数：

```
int anti2(char *res) `{`
    char buff[PROP_VALUE_MAX];
    memset(buff, 0, PROP_VALUE_MAX);
    int result =
            __system_property_get(res, (char *) &amp;buff) &gt; 0 ? 1 : 0; //返回命令行内容的长度
    if (result != 0) `{`
        LOGE("the %s result is %s", res, buff);
        //  LOGE("this is a Emulator!!!");
    `}`
    return result;
`}`
```

通过__system_property_get我们就可以拿到该属性对应的值，值会保存在buff中。

当然了常规通过build.prop的检测方式也未尝一无是处，在检测模拟器时可以多维度去检测，在build.prop中一些字段也是比较重要的，如ro.product.name获取当前设备名称：

```
char *model = getDeviceInfo("ro.product.name");
if (!strcmp(model, "ChangWan")) `{`
`}` else if (!strcmp(model, "Droid4X")) `{`                     //非0均为模拟器
`}` else if (!strcmp(model, "lgshouyou")) `{`
`}` else if (!strcmp(model, "nox")) `{`
`}` else if (!strcmp(model, "ttVM_Hdragon")) `{`
`}`
```

通过和一些常见模拟器设备名称进行对比，但是目前模拟器都可以手动去修改imei，deviceID，以及设备信息，这种检测方式效果不大。

本人测试时还发现，当试图去检测一些特殊信息，如当前设备cpu温度时，搜集了一些资料，提供了一个adb方式去获取，/sys/class/thermal/thermal_zoneX/temp(其中X是核心数量)，但发现模拟器上没有thermal_zoneX目录，只有两个cooling_deviceX目录，因而有了一个新的判断依据，如下：

```
int checkTemp() `{`
    DIR *dirptr = NULL; //当前手机的温度检测，手机下均有thermal_zone文件
    int i = 0;
    struct dirent *entry;
    if ((dirptr = opendir("/sys/class/thermal/")) != NULL) `{`
        while (entry = readdir(dirptr)) `{`
            // LOGE("%s  n", entry-&gt;d_name);
            if (!strcmp(entry-&gt;d_name, ".") || !strcmp(entry-&gt;d_name, "..")) `{`
                continue;
            `}`
            char *tmp = entry-&gt;d_name;
            if (strstr(tmp, "thermal_zone") != NULL) `{`
                i++;
            `}`
        `}`
        closedir(dirptr);
    `}` else `{`
        LOGE("open thermal fail");
    `}`
    return i;
`}`
```

使用opendir函数去访问thermal目录，遍历该目录下所有目录，当不存在thermal_zone目录时，则判断当前设备为模拟器，最后放上几张模拟器测试图。

**海马玩：**

[![](https://p5.ssl.qhimg.com/t019880c75a7c090248.png)](https://p5.ssl.qhimg.com/t019880c75a7c090248.png)

**逍遥模拟器：**

[![](https://p5.ssl.qhimg.com/t01c2db2190e88c2c20.png)](https://p5.ssl.qhimg.com/t01c2db2190e88c2c20.png)

**真机Nexus 5：**

[![](https://p1.ssl.qhimg.com/t0139a296d311abf114.png)](https://p1.ssl.qhimg.com/t0139a296d311abf114.png)

**真机乐视2：**

[![](https://p0.ssl.qhimg.com/t01ca8a107d540854a3.png)](https://p0.ssl.qhimg.com/t01ca8a107d540854a3.png)

以上只是提供了一些检测模拟器的思路，真正的使用还需要大量的进行测试，提高检测的准确性和稳定性。

扫描下方二维码关注YSRC公众号，回复“模拟器检测”获取基于文件特征的Android模拟器检测实现代码。

[![](https://p1.ssl.qhimg.com/t0188ef476dc8e3e7f2.jpg)](https://p1.ssl.qhimg.com/t0188ef476dc8e3e7f2.jpg)

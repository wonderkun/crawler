> 原文链接: https://www.anquanke.com//post/id/82810 


# 有米iOS恶意SDK分析


                                阅读量   
                                **120591**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t01d569c936fa9036ab.jpg)](https://p4.ssl.qhimg.com/t01d569c936fa9036ab.jpg)

前言:

有米广告平台为业界领先的移动信息服务提供商优蜜科技™所有,总部和研发中心设在广州,在北京设立分支机构。有米广告拥有核心技术及完整知识产权,并获多项国家专利,在用户特征识别、精准投放、客户端防作弊、广告智能投放等关键领域遥遥领先。有米广告瞄准7亿手机用户,致力于为数以万计的企业广告主提供精准的产品营销和品牌推广服务,为应用开发者创造公正和优质的广告收益。

网址是 [https://www.youmi.net/](https://www.youmi.net/)

前不久SourceDNA的研究人员发现iOS平台使用有米SDK的一些APP收集用户隐私数据,主要包括以下四类:

1、用户安装在手机上的应用列表信息;

2、在用户运行旧版iOS时,收集设备的平台序列号;

3、在运行新版iOS时,收集设备的硬件组件及组件序列号;

4、用户的Apple ID邮箱。

我们Nirvanteam(涅槃)团队的安全研究员@panda也对此进行了详细的技术分析。

详细过程开始分析如下:



0x01 社工获取iOS的SDK

目前网上不太好找这个SDK,而且有米也在努力更新SDK。



[![](https://p0.ssl.qhimg.com/t016c6dd00cdac83f92.png)](https://p0.ssl.qhimg.com/t016c6dd00cdac83f92.png)

最后通过社工得到 SDK。



0x02 SDK细节分析

拿到SDK后直接 strings不能搜索到URL的, 劫持包发现了URL然后分析发现URL都做了编码。

URL如下:

[http://ios.wall.youmi.net](http://ios.wall.youmi.net)  主要是这个URL在发送数据

[http://stat.gw.youmi.net](http://stat.gw.youmi.net)

[http://au.youmi.net/offer/ios/offers.manifest](http://au.youmi.net/offer/ios/offers.manifest)

[http://t.youmi.net](http://t.youmi.net)

通过分析SDK 发现SDK通过大量的私有API。

私有API是指放在PrivateFrameworks框架中的API,苹果通常不允许App使用这类API,因为调用私有API而在审核中遭到拒绝的现象并不少见。但苹果的审核机制并不透明,许多使用了私有API的App也被审核通过,包括Google Voice这样的应用,一样调用了私有API,也获得了通过上架。甚至是苹果的预装App iBooks也被揭露使用了大量私有 API,致使第三方应用无法实现亮度控制和调用字典等类似的功能。

逆向sdk分析:

通过分析URL 去挖掘发送的数据,sub_2DE18 函数主要获取各种信息,如下如:

[![](https://p2.ssl.qhimg.com/t0198eb169ab4a10e1f.png)](https://p2.ssl.qhimg.com/t0198eb169ab4a10e1f.png)

IOServiceMatching(“IOPlatformExpertDevice”)1) 其中获取序列号信息代码:



```
io_service_t  IOPlatformExpertDevicev_ios_service= IOServiceGetMatchingService)(
                addr_kIOMasterPortDefault,
               "IOPlatformExpertDevicev");
CFStringRef  strref = CFStringCreateWithCString(kCFAllocatorDefault, IOPlatformSerialNumber_v64, 0x600);//Creates an immutable string from a C string.
CFTypeRef SerialNumberAsCFString = 
IORegistryEntryCreateCFProperty(platformExpert, CFSTR("IOPlatformSerialNumber"), kCFAllocatorDefault, 0) ; 
          if ( SerialNumberAsCFString )
          `{`
            CFTypeID typeid = CFGetTypeID(SerialNumberAsCFString);
            if ( typeid == CFStringGetTypeID() )
            `{`
              [NSString stringWithString:SerialNumberAsCFString];  //获得统序列号 5K152FX7A4S
            `}`
          `}`
```

2) 获得各种设备信息主要通过下面函数获取。



```
getinfo_from_devicename_and_togetdict_infosub_1EC88((DeviceName, dict_v8);
```

传入需要获取的设备名称和字典信息来获取信息,设备名用于获取信息,字典是需要获取的信息。

函数代码如下:



```
io_iterator_t iterator,iterator2;
            IORegistryEntryGetChildIterator(result2,"IOService", &amp;iterator);
             io_iterator_t t = IOIteratorNext(iterator);
            char name[20];
            IORegistryEntryGetNameInPlane(result2,"IOService", name);
                if([DeviceName isEqualToString: name])
                `{`
               CFTypeRef data;
            IORegistryEntryCreateCFProperties_v25)(result2,
                            &amp;data,
                            kCFAllocatorDefault,
                            0);
            if(CFGetTypeID(data) ==  CFDictionaryGetTypeID())
`{`
…………
```

例如获取设备名称如下:

电池  battery-id

摄像机 AppleH4CamIn

iOS加速度传感器 accelerometer

WIFI 信息   wlan

蓝牙信息  bluetooth

Device Characteristics TLC还是MLC内存ASPStoragedisk

充电次数   AppleARMPMUCharger

获取设备信息后将信息存储到APP/Library/.XABCD/nidayue.dict这个文件中,当需要哪些信息就从这里读取。

写这个文件是通过设置消息函数来实现的。



```
void __cdecl -[ChargerClinkeredConcertedly catalogueChoraleAlamo](struct ChargerClinkeredConcertedly *self, SEL a2)
`{`
  struct ChargerClinkeredConcertedly *v2; // r4@1
  void *v3; // r0@1
  void *v4; // r0@1
  v2 = self;
  v3 = objc_msgSend(&amp;OBJC_CLASS___NSNotificationCenter, "defaultCenter");
  objc_msgSend(
    v3,
    "addObserver:selector:name:object:",
    v2,
    "approvementAviateBefitted:",
    UIApplicationWillTerminateNotification,
    0);
  v4 = objc_msgSend(&amp;OBJC_CLASS___NSNotificationCenter, "defaultCenter");
  objc_msgSend(
    v4,
    "addObserver:selector:name:object:",
    v2,
    "consummatingCreators:",
    UIApplicationWillResignActiveNotification,
    0);
`}`
```

当安装好APP 后,将要关闭APP或者按home键到后台才会去写文件信息。

3) 获取UUID信息

[![](https://p0.ssl.qhimg.com/t0186897c80504d97c3.png)](https://p0.ssl.qhimg.com/t0186897c80504d97c3.png)

ASIdentifierManager  sharedManager4) 广告标示符(IDFA-identifierForIdentifier)

ASIdentifierManager单例提供了一个方法advertisingIdentifier,通过调用该方法会返回一个上面提到的NSUUID实例。



```
NSString *adId = [[[ASIdentifierManager sharedManager] advertisingIdentifier] UUIDString];
```

5) 屏幕大小 960*640 获取方式



```
[[UIScreen mainScreen] bounds]
[[UIScreen mainScreen] scale]
CGRectGetHeight
CGRectGetWidth
```

6) 手机设备型号获取,如下图:



[![](https://p4.ssl.qhimg.com/t015bfb3f643a9fb23f.png)](https://p4.ssl.qhimg.com/t015bfb3f643a9fb23f.png)



如上函数假设参数*servicename_a1传递值为hw.machine时,返回设备硬件信息为iPhone3,1



0x03 危害分析

通过分析发现SDK 获得了如下信息(测试用的iPhone4 iOS7.12):

1)设备的WIFI信息,

BSSID = “d0:fa:1d:20:a:f8”; 这个无线AP的MAC地址

SSID = “360WiFi-200AF8”;  一个无线AP的名称。

SSIDDATA = &lt;33363057 6946692d 32303041 4638&gt;;

2)序列号信息IOPlatformSerialNumber5K152FX7A4S

3   电池信息 battery-id

4)  摄像机信息

5)  iOS加速度传感器 low-temp-accel-offset

6)  蓝牙信息 wifi-module-sn

7)  Device Characteristics TLC还是MLC内存

8)  UUID  信息   a2ab842508133b62b680b5f9efa1cd51

9)  充电次数  CycleCount

10) 广告标示符(IDFA-identifierForIdentifier)112fb7fe79fb4b7abf7a8e2ecaf57147

11) __UDID信息 7a32771c3adf2ad0564c3cb2d6920bc6ef9818b7

12)屏幕大小 960*640

13)手机设备型号 iPhone3,1

14)通过检查进程名, 安装的APP BundleID表 , 进程模块中有没有 iGrimace,org.ioshack.iGrimace等来检查越狱状态,越狱或者未越狱。

15)设备名称信息如

Device:iPhone3,1  Jailbreak:1  OS:iPhone OS  Version:7.1.2  Name:“panda”的 iPhone  Model:iPhone

获得这些信息后通过 deflate 压缩,再通过一次混合加密发送出去。加密过程如下图:

[![](https://p0.ssl.qhimg.com/t01f07a14c4be6000ce.png)](https://p0.ssl.qhimg.com/t01f07a14c4be6000ce.png)

发送加密如下经过加密后将数据整合到URL上,发后通过POST方式发送出去。



```
NSURLConnection_start `{` 
cookie = "";
data = "";
host = "ios.wall.youmi.net";
method = GET;
mime = "";
url = "http://ios.wall.youmi.net/v3/reqf?s=1,5,8aa2a777452acf72,lyOU,1,bfDG9lgEuEfsVbWHLjyNZ-ESDTPXoRHqPZvukpsNiA9esOWBJTHnmelJwR4Mzd-tYlsbO1ROsjJAYN35ngXjNvMqdtMKUu2czR4hRqws3pU2UGYPMY6Z2Z-XGzxqhb9o1gJmB2cNMfczHb4Lu8ji7e5gOu-VQjLZiXCHEnMdls-OOyb5e2wtU-wsQtK.Q0v6S692Tr-Qp8k-YcYMJ47vqcsnCJJdzehyw4W-uee7pHmmJJU1.jxMeHEKT4BpL8flP338p3HPN5Zx5DoAzEmNRdlvPui7LZiHyOxL0r8adyZyJDkfAn8qE6PDBWmK1MUQ1jWa6ghwR4bPVQmrCMZcq6a1RUZzTJVKMQOokMswhs.JdRBIZMyyUrBuRf1IcHECc.Rj1jL1IdiwTdZaDLAzcLiKDMK3Pn222K160LVqG6XhnAzmw6gs.9.0yc.kZmbsUKZ7MZ5dCliJY8Izkk9A2SGpLI4zQ5MML5XPnobSVHlVQQ4tN4khqvAXVAJwLK91YdxrhFae1fNoi5BaCpj7fSnzRjF1j46Lygnv4DgT890oljclyzBgxbxBFrwuqV8tc1VpGqMvnX6sDlGVonzGOQnd9Yjwm3d3CE3PYwCSC1jafsTlw8AhwsyZ6E5gKqio4B-JlLavdFZF4xPfP4YeQngzZRAijN3QUXYT7ZVB5f5C9NdrDdrnmZTLx5B7jChaUbdI5sTs4zNXgaGUzFYOxmgxlxdxZGN6TSUMUS7k9SEygV0tAI-uARcuF1MSE.o76aoRR1JmtSPDSI7yPL1ooo2-CeLEOhQCzcgNrrkdx.ZL6LRyWkyOXcGISiaWKWFh0BAtzv2mFhBvArj7d1MsKMY57suR58v8rugnnEeFBtfNDKK7lQrZAKKfm7iGv-xmJ4f3DFtqo4OYOE0.Q8uSQblgnK24F3-x&amp;p=1&amp;n=100&amp;nshw=1";
`}`
```

加密信息解密如下:



```
`{`
    3gst = "";
    acc = "0.000000,0.000000,0.000000";
    accos = 1000010000000000c4bc1300612003004e260900;
    aicid = 47a903bcec614984acd1d0f88039d34a;
    apn = None;
    av = "1.0";
    batsn = ae15041460753d1420;
    bcsn = "";
    bsi = "";
    bssid = ec26cad6e5a;
    btsn = "";
    cc = CN;
    chn = 0;
    chrcy = "";
    cid = "eIyoH-ZvBqO_f";
    cn = 2;
    dd = "Device:iPhone3,1  Jailbreak:1  OS:iPhone OS  Version:7.1.2  Name:U201cpandaU201dU7684 iPhone  Model:iPhone";
    ddn = "U201cpandaU201dU7684 iPhone";
    ext =     `{`
        attr = 195;
        it = 1;
        nshw = 1;
        reqt = 0;
        rtype = 1;
        sat = 3;
        wat = 3;
    `}`;
    fcsn = "";
    gyo = "0.000000,0.000000,0.000000";
    hv = 2;
    ifa = 112fb7fe79fb4b7abf7a8e2ecaf57147;
    ifat = 1;
    ifst = 3155986;
    ise = 0;
    jb = 1;
    kernid = a2ab842508133b62b680b5f9efa1cd51;
    lat = "0.00";
    lc = "zh-Hans";
    lon = "0.00";
    mac = "";
    mcc = "";
    mmcid = "";
    mnc = "";
    mod = iPhone;
    odfa = "";
    oifa = 112fb7fe79fb4b7abf7a8e2ecaf57147;
    osv = "7.1.2";
    pd = 3;
    pn = "feng.YouMiWallSample";
    po = "iPhone OS";
    rb = "-1.000000";
    rt = 1445444547;
    sh = 960;
    smv = 1;
    sn = 5K152FX7A4S;
    spc = "";
    ssid = "TP-LINK_2510";
    sv = "5.3.0";
    sw = 640;
    tid = 005ecs1rcn0k1dltd0o8dngsruf;
    ts = 0;
    udid = 7a32771c3adf2ad0564c3cb2d6920bc6ef9818b7;
    usb = 2;
    user = "this is user";
    vpn = 0;
    wifisn = "";
`}`
```



**0x04 结果及总结**

通过对大量样本扫描发现,共计扫描出了1035个苹果APP受到感染。

具体对应版本信息见另一份文档

1)有米SDK主要用于统计设备类型的使用情况,这样来对市场形势作出判断来获取利益。

2)私有API如果通过静态扫描的话意思不大,一般能通过苹果审核的,私有API都是经过处理的,所以检查私有API要通过动态HOOK的方式去检查。

3)一般有使用私有API的一般都是启动的阶段,所以动态扫描APP运行阶段做成自动化也是可行的。

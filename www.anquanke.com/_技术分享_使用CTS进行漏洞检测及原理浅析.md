> 原文链接: https://www.anquanke.com//post/id/86357 


# 【技术分享】使用CTS进行漏洞检测及原理浅析


                                阅读量   
                                **220272**
                            
                        |
                        
                                                                                    



**[![](https://p4.ssl.qhimg.com/t0101e8bf0463f938db.jpg)](https://p4.ssl.qhimg.com/t0101e8bf0463f938db.jpg)**

**团队介绍**



**360 Vulpecker团队**隶属360信息安全部，致力于Android应用和系统层漏洞挖掘以及其他Android方面的安全研究。我们通过对CTS框架的研究，编写了一个关于漏洞检测方面的文档,以下为文章的全文。

CTS 全称 Compatibility Test Suite（兼容性测试）,Google开发CTS框架的意义在于让各类Android设备厂商能够开发出兼容性更好的设备。其中有一些模块的关于手机安全方面的检测,本文以此为主题,进行了漏洞检测方面的研究。包括如何下载编译,以及分析了其中的security模块是如何调度使用的。

 

**1. CTS运行流程**



1.1  下载编译Android CTS源码， 

通过git clone [https://android.googlesource.com/platform/cts -b xxxxxxx 可以下载cts并且进行编译,或者可以下载完整的Android](https://android.googlesource.com/platform/cts%20-b%20xxxxxxx%20%E5%8F%AF%E4%BB%A5%E4%B8%8B%E8%BD%BDcts%E5%B9%B6%E4%B8%94%E8%BF%9B%E8%A1%8C%E7%BC%96%E8%AF%91,%E6%88%96%E8%80%85%E5%8F%AF%E4%BB%A5%E4%B8%8B%E8%BD%BD%E5%AE%8C%E6%95%B4%E7%9A%84Android)源码进行编译，编译好源码之后再编译CTS,命令是make cts；在/home/venscor/AndroidSource/least/out/host/linux-x86/cts下生成关于CTS的几个文件，其中cts-tradefed可以启动CTS测试程序。

[![](https://p5.ssl.qhimg.com/t01dce27cb521b4cfa7.png)](https://p5.ssl.qhimg.com/t01dce27cb521b4cfa7.png)

1.2  CTS运行环境

Android官网上对CTS运行环境要求严格，但是我们目前关注的是测试安全模块，所以只要基本的测试环境就可以了。例如打开adb，允许adb安装apk，不设置锁屏等。

1.3  CTS运行流程

在源码中可以看到,cts-tradefed实际上是个脚本文件。首先做些环境检查，满足运行环境后，去android-cts/tool/目录下加载对应的jar文件，从android-cts/lib加载所有的需要库文件。最后，加载android-cts/testcase/目录下的所有jar文件，然后执行。

CTS console功能的实现在CompatibilityConsole类中，也是程序的加载点

[![](https://p5.ssl.qhimg.com/t0173b163d5d0480d97.png)](https://p5.ssl.qhimg.com/t0173b163d5d0480d97.png)

[![](https://p2.ssl.qhimg.com/t0199eef2331ed726d5.png)](https://p2.ssl.qhimg.com/t0199eef2331ed726d5.png)

 [![](https://p2.ssl.qhimg.com/t017d67ed37e39e4693.png)](https://p2.ssl.qhimg.com/t017d67ed37e39e4693.png)

1.4  启动脚本进入CTS测试程序的console

[![](https://p5.ssl.qhimg.com/t01c71dff98c2bb86a2.png)](https://p5.ssl.qhimg.com/t01c71dff98c2bb86a2.png)

CTS测试套件由很多plans组成，plans又可以由很多subplan和modules组成，我们只关心和CTS和安全相关的的东西，即和安全相关的modules。其中**和安全相关的测试模块**有4个：

CtsAppSecurityHostTestCases

CtsJdwpSecurityHostTestCases

CtsSecurityHostTestCases

CtsSecurityTestCases

其中，CtsAppSecurityHostTestCases、CtsJdwpSecurityHostTestCases不包含CVE，其实是一些App层安全检测和安全策略检测，我们可以先跳过这两个模块着重分析CtsSecurityHostTestCases和CtsSecurityTestCases。

<br>

**2. CTS中的安全模块**



2.1 CtsSecurityHostTestCases模块

CtsSecurityHostTestCases模块对应的源码路径在：./hostsidetests/security。即在cts console中通过输入run cts –module CtsSecurityHostTestCasess加载起来的。

CtsSecurityHostTestCases主要测试Linux内核和各类驱动的漏洞，都是以C/C++实现的漏洞检测PoC。

[![](https://p5.ssl.qhimg.com/t012263d23d6700f720.png)](https://p5.ssl.qhimg.com/t012263d23d6700f720.png)

2.1.1 测试流程

可以通过run cts –module CtsSecurityHostTestCases来测试整个模块，也可以通过run cts –module CtsSecurityHostTestCases –test 来测试具体的方法。例如要测试CVE_2016_8451，可以通过–test android.security.cts.Poc16_12#testPocCVE_2016_8451来进行。

下面我们通过一个例子看具体的测试流程，以对CVE_2016_8460的检测为例，来具体分析下测试过程。在CTS下，运行run cts –module CtsSecurityHostTestCases –test android.security.cts.Poc16_12#testPocCVE_2016_8460。程序将运行到CtsSecurityHostTestCases模块下的testPocCVE_2016_8460()函数。

[![](https://p0.ssl.qhimg.com/t012807ae9053c4b543.png)](https://p0.ssl.qhimg.com/t012807ae9053c4b543.png)

其实这个测试过程，就是将CtsSecurityHostTestCases模块下对应的可执行文件CVE_2016_8460 push到手机的sdcard，然后执行此可执行文件，即执行poc检测程序。

[![](https://p0.ssl.qhimg.com/t01209347dd0f885952.png)](https://p0.ssl.qhimg.com/t01209347dd0f885952.png)

2.1.2 结果管理

CTS测试完成后，会生成可视化的结果，结果存在cts/android-cts/results目录下，分别有xml格式和.zip打包格式。所以对安全模块的结果管理也是一样的。

结果页面里面只有两种结果，一是pass，表示测试通过，说明不存在漏洞。二是fail，出现这种结果，可能原因有两种，一是测试环境有问题，二是存在漏洞，可以看报告边上的详细显示。

[![](https://p2.ssl.qhimg.com/t01c89cf886e3591477.png)](https://p2.ssl.qhimg.com/t01c89cf886e3591477.png)

2.1.3 添加与剥离testcase

按照CtsSecurityHostTestCases模块的测试原理，添加新的测试case时，完全可以剥离CTS的测试框架，直接使用C/C+编写测试代码，编译完成后添加到/data/local/tmp目录然后修改执行权限，执行即可。

对于CtsSecurityHostTestCases模块中现有的对漏洞的检测代码，也可以直接为我们所用。我们可以下载CTS的源码查看漏洞检测PoC的代码，可以自己编译也可以直接使用CTS编译好的可执行文件来检测对应的漏洞。

2.2 CtsSecurityTestCases模块

CtsSecurityTestCases模块基于动态检测，采用的是触发漏洞来检测的方式，使用Java或者JNI来触发漏洞，直到数据被传递到底层漏洞位置。这个模块所在源码的路径是.test/test/security。

[![](https://p5.ssl.qhimg.com/t01a2e590469091f88c.png)](https://p5.ssl.qhimg.com/t01a2e590469091f88c.png)

2.2.1 测试流程

测试流程和CtsSecurityHostTestCases模块一致，其实这也是CTS框架的测试流程。测试整个模块采用run cts –module的方式，而使用测试模块里面具体的方法来执行测试时。使用run cts –module &lt;module&gt; –test &lt;package.class&gt;的方式。

以下以检测cve_2016_3755为例说明此模块运行过程。

首先，在CTS框架中输入run cts –module CtsSecurityTestCases –test android.security.cts. StagefrightTest#testStagefright_cve_2016_3755。

然后，CTS框架会找到testStagefright_cve_2016_3755()方法并执行测试。

[![](https://p3.ssl.qhimg.com/t01a0aa6d9ca02061c4.png)](https://p3.ssl.qhimg.com/t01a0aa6d9ca02061c4.png)

[![](https://p5.ssl.qhimg.com/t01dd0205f476394116.png)](https://p5.ssl.qhimg.com/t01dd0205f476394116.png)

2.2.2 结果管理

CtsSecurityTestCases模块也受CTS统一的结果管理。所以上面CtsSecurityHostTestCases模块一样。测试结果出现在xml文件中，pass表示成功不存在漏洞，fail给出失败原因。

对测试结果的监控都是通过assertXXX()方法来进行的，通过测试过程中的行为来确定漏洞情况。例如：

[![](https://p2.ssl.qhimg.com/t01d8014ffccd0c2bd0.png)](https://p2.ssl.qhimg.com/t01d8014ffccd0c2bd0.png)

[![](https://p0.ssl.qhimg.com/t0136c9891483b307e3.png)](https://p0.ssl.qhimg.com/t0136c9891483b307e3.png)

[![](https://p0.ssl.qhimg.com/t017734676aa49e3751.png)](https://p0.ssl.qhimg.com/t017734676aa49e3751.png)

2.2.3添加与剥离testcase

添加case：在这模式下添加case，需要知道知道怎么触发漏洞。CtsSecurityTestCases模块应该是基于Android上的JUnit测试程序的，所以要知道应该可以按照编写JUnit的方式添加测试的代码，然后重新build。其实，编写测试代码时候如果可以脱离CTS的源码依赖或者可以引用CTS的jar，应该可以直接脱离CTS架构。

剥离case：和添加一个道理，需要让提取的代码脱离依赖可执行。



**3. 总结**



在Android手机碎片化严重的今天，各个手机厂商的代码质量也是良莠不齐。所以Android手机的安全生存在较为复杂的生态环境，因此Android手机方面的漏洞检测是十分必要的。本文对谷歌官方开源的CTS框架进行了调研，对Android手机的漏洞检测方面进行了研究。希望能抛砖引玉，对Anroid安全研究能带来更多的帮助。



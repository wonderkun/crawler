> 原文链接: https://www.anquanke.com//post/id/89222 


# 360 Vulpecker：友盟SDK越权漏洞分析报告


                                阅读量   
                                **192788**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">19</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t011809b530be5144e2.png)](https://p0.ssl.qhimg.com/t011809b530be5144e2.png)



## 概要

今年9月22日，360信息安全部的Vulpecker安全团队发现了国内消息推送厂商友盟的SDK存在可越权调用未导出组件的漏洞，并利用该漏洞实现了对使用了友盟SDK的APP的任意组件的恶意调用、任意虚假消息的通知、远程代码执行等攻击测试。



经过分析验证，360 Vulpecker安全团队将此漏洞细节第一时间提交给友盟进行修复。10月18日，友盟官方发布最新版3.1.3修复漏洞。为了确保受此漏洞影响的终端用户有充分的时间进行安全更新，12月6日，360Vulpecker安全团队首次向外界公开披露漏洞信息。



在360显危镜后台数据库中根据该含有漏洞版本的SDK的特征值查询确认，发现约有3万多APP受此漏洞的影响，根据包名去重后约7千多款APP产品，涉及多种类型的应用。鉴于该消息推送SDK使用范围较广，且受影响APP多是与终端用户日常生活息息相关的应用，一旦被恶意攻击者利用危害将是非常严重的。基于该漏洞，可以实现对终端用户推送虚假诈骗信息、远程窃取用户终端设备中的敏感数据（例如通讯录、照片、账号密码等数据）等功能。此外，该漏洞的危害依赖于Android应用本身提供的功能而有所不同，因此对终端用户的攻击方式亦是姿态各异，造成的危害也是多种多样的。

此漏洞已经得到友盟官方修复，请用户及时更新智能手机上安装的各类APP，防止手机里的隐私数据和财产被不法分子轻易窃取。



## 前言

近年来，随着移动互联网的高速发展，智能终端设备已经走入人们生活的方方面面。在Android和iOS两大移动平台阵营中，Android系统以其开源性、易开发、丰富的硬件等优势占据了市场上约80%的份额。



Android系统中提供的应用丰富多样，且功能复杂，几乎所有的应用都采用了第三方的SDK以加速其开发周期，节约成本。第三方SDK包括支付、统计、广告、社交、推送、地图类等，其在加速产品成型时，也引入了许许多多的安全问题。下图所示内容为经360显危镜后台查询的几款常用SDK使用情况统计数据，从图中可以看出使用了该SDK开发的APP非常多。

[![](https://p0.ssl.qhimg.com/t0181330a529e7a9499.png)](https://p0.ssl.qhimg.com/t0181330a529e7a9499.png)

下文以友盟消息推送SDK为例，详细介绍一下第三方SDK在缺乏产品安全审计的情况下存在的高危漏洞风险，希冀以此能督促第三方SDK厂商在产品安全性方面能投入更多的精力。



## SDK介绍

友盟 Push SDK是友盟互联网数据服务SDK其中用来做消息推送的模块之一，基于【友盟+】全域数据建立与用户精准直接沟通的渠道，将APP的内容主动推送给终端用户，让用户实时实地的获取相关信息，有效提升用户活跃和忠诚度。由于其定位精准、集成快速等优点，目前有多个知名APP在使用U-PUSH服务。



## 技术分析

友盟的消息推送SDK中有一导出Service组件存在漏洞，可被越权调用并利用该组件访问任意service组件，甚至未导出的亦可。随后，利用该漏洞调用友盟其他未导出的组件，可进一步越权调用任意导出和未导出的Activity，进而扩大了该漏洞的攻击面，为攻击者提供了更大范围的攻击可能性。

下文详述了友盟的消息推送SDK中可越权调用所有非导出组件的漏洞技术原理，并据此详述了如何实现非导出组件恶意调用、恶意消息通知、远程代码执行等攻击行为。



## 漏洞起因

友盟最新的消息推送SDK中集成的说明文档中的demo里，AndroidManifest文件中导出了一个IntentService——UmengIntentService，据推测这个服务是为了使用了PUSH SDK的APP之间相互唤醒使用的，详情如下图所示。

[![](https://p4.ssl.qhimg.com/t011d7a54e042d780da.png)](https://p4.ssl.qhimg.com/t011d7a54e042d780da.png)

这个IntentService有个实现的抽象方法如下：

[![](https://p4.ssl.qhimg.com/t01dce34f0e8ae8dcc1.png)](https://p4.ssl.qhimg.com/t01dce34f0e8ae8dcc1.png)

我们能看到外部接收了intent携带的body数据（JSON格式），交给UMessage构造后得到v3，如果display_type 为“pullapp”的话，可通过设置pulled_service和pulled_package参数能拉起任意未运行的servcie。其中Umessage函数的结构如下：

[![](https://p3.ssl.qhimg.com/t017c2568e896ed5bc4.png)](https://p3.ssl.qhimg.com/t017c2568e896ed5bc4.png)



## 漏洞利用

### 初步利用——访问未导出service组件

通过构造如下POC，可访问APP内所有的service组件，甚至未导出的servcie。而且SDK提供了一个“贴心”的功能，接收额外的参数，封装到新的Intent后发送给拉起的service。

[![](https://p3.ssl.qhimg.com/t012bb759d0c5cccbc6.png)](https://p3.ssl.qhimg.com/t012bb759d0c5cccbc6.png)

[![](https://p5.ssl.qhimg.com/t01bc787ab3765d3950.png)](https://p5.ssl.qhimg.com/t01bc787ab3765d3950.png)

*限制一点的只能putExtra String类型的数据，但是也足够利用了。

PoC：

[![](https://p4.ssl.qhimg.com/t0158e55979b1d3f147.png)](https://p4.ssl.qhimg.com/t0158e55979b1d3f147.png)

### 进阶利用——访问未导出Activity

SDK有几个强大功能：接收推送的消息，下载图片或接收文本进行通知展示。点击通知后有几个可选动作，打开URL、打开指定activity、运行其他APP和一个自定义的动作。我们通过一个未导出的Service——UmengDownloadResourceService进行进一步的利用。

[![](https://p2.ssl.qhimg.com/t01ccf58236b6daff5d.png)](https://p2.ssl.qhimg.com/t01ccf58236b6daff5d.png)

打开activity的POC：

[![](https://p1.ssl.qhimg.com/t011b4e3cf82ac8bbf0.png)](https://p1.ssl.qhimg.com/t011b4e3cf82ac8bbf0.png)

#### 利用实例1——通用弹出钓鱼通知

利用上面打开任意activity的POC，可以弹出任意通知，这个通知的图标，文本都是可以定制的，而且用户长按通知也会发现这个通知是漏洞APP发出的。点击通知，我们可以跳转url打开一个钓鱼页面或是钓鱼activity。

#### 利用实例2——隔山打牛，一点资讯下载任意压缩包

通过检索平台搜索后发现，APP一点资讯是存在这个漏洞的。进一步挖掘过程中，发现APP有一个未导出的service——WebAppUpdateService，详情如下。

[![](https://p1.ssl.qhimg.com/t015b63000e4655cf8c.png)](https://p1.ssl.qhimg.com/t015b63000e4655cf8c.png)

[![](https://p2.ssl.qhimg.com/t012ef5f059c1cf8289.png)](https://p2.ssl.qhimg.com/t012ef5f059c1cf8289.png)

通过构造合法的参数，可以利用WebAppUpdateService组件实现下载自定义的zip文件并解压到当前应用沙箱目录中，EXP代码如下：

[![](https://p1.ssl.qhimg.com/t01e150c7c158fafc0e.png)](https://p1.ssl.qhimg.com/t01e150c7c158fafc0e.png)

运行成功后，下载zip文件夹并解压到相关目录，这个目录里存的是APP所使用的html页面，而整个zip里文件都是我们能够修改和替换。现在做钓鱼页面，加各种js代码都没问题了。

[![](https://p0.ssl.qhimg.com/t01e8d30ed00cabe436.png)](https://p0.ssl.qhimg.com/t01e8d30ed00cabe436.png)

[![](https://p1.ssl.qhimg.com/t012dcf2ef21609253a.png)](https://p1.ssl.qhimg.com/t012dcf2ef21609253a.png)

随后，通过对该APP代码的深度挖掘分析，我们发现该应用提供了动态加载插件的功能，且在对加载的插件解压时未做过滤导致存在目录穿越漏洞。结合该漏洞，我们可以在加载插件过程中覆盖该APP的lib文件，注入自己的恶意代码，进而造成远程代码执行。不言而喻，远程代码执行对用户的危害是非常严重的，可远程控制用户终端设备，远程窃取用户隐私数据，甚至其他任意的恶意行为。下图所示为结合上述漏洞实现的对用户终端设备远程获取隐私敏感数据的攻击截图。

[![](https://p3.ssl.qhimg.com/t01109471851280943a.png)](https://p3.ssl.qhimg.com/t01109471851280943a.png)

漏洞演示视频如下：

[http://v.youku.com/v_show/id_XMzIwNTAyMjUyOA==.html](http://v.youku.com/v_show/id_XMzIwNTAyMjUyOA==.html)



## 影响范围

通过分析发现，有漏洞的组件UmengIntentService是在新版3.1.X版本中引入的。我们据此确定以下的特征值，并在360显危镜后台数据库中查询受该漏洞影响的APP：组件service中包含UmengIntentService并且在apk中包含字符串pullapp。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c8d818377ec45265.png)

在360显危镜后台数据库中，按该漏洞的特征值查询后发现约3万多的APP受此漏洞的影响，其中不乏大公司的产品主流产品，对用户影响巨大。



## 修复建议

如果组件导出是非必要的，将漏洞组件设置为不导出；

如果组件是必须导出的，在Service加上android:protectLevel增加权限校验，至少为signature级别。

官方已有修复版本更新，请及时更新到最新版本。



## 时间轴

2017-09-22     发现漏洞

2017-09-25     通报官方

2017-10-18     官方发布最新版3.1.3修复漏洞

2017-12-06     对外公布漏洞详情



## 参考链接

[https://www.umeng.com/](https://www.umeng.com/)

[https://www.anquanke.com/post/id/87274](https://www.anquanke.com/post/id/87274)

[http://appscan.360.cn/](http://appscan.360.cn/)

[http://v.youku.com/v_show/id_XMzIwNTAyMjUyOA==.html](http://v.youku.com/v_show/id_XMzIwNTAyMjUyOA==.html)



## 团队介绍

360 Vulpecker Team

隶属于360公司信息安全部，致力于保护公司所有Android App及手机的安全，同时专注于移动安全研究，研究重点为安卓APP安全和安卓OEM手机安全。 团队定制了公司内部安卓产品安全开发规范，自主开发并维护了在线Android应用安全审计系统“360显危镜”，在大大提高工作效率的同时也为开发者提供了便捷的安全自测平台。同时研究发现了多个安卓系统上的通用型漏洞，如通用拒绝服务漏洞、“寄生兽”漏洞等，影响范围几乎包括市面上所有应用。



该团队高度活跃在谷歌、三星、华为等各大手机厂商的致谢名单中，挖掘的漏洞屡次获得CVE编号及致谢，在保证360产品安全的前提下，团队不断对外输出安全技术，为移动互联网安全贡献一份力量。

[![](https://p3.ssl.qhimg.com/t01e25b349e77e13fb8.png)](https://p3.ssl.qhimg.com/t01e25b349e77e13fb8.png)

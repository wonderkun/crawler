> 原文链接: https://www.anquanke.com//post/id/159264 


# ArmaRat：针对伊朗用户长达两年的间谍活动


                                阅读量   
                                **105091**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01a15ca04c4176b386.jpg)](https://p1.ssl.qhimg.com/t01a15ca04c4176b386.jpg)

## 一、 主要发现

2016年7月起至今，360烽火实验室发现一起针对伊朗Android手机用户长达两年之久的间谍活动。截至目前我们一共捕获了Android 样本18个，涉及的 C&amp;C 域名5个。

2016 年7月，我们捕获了第一个Android平台下伪装成“Telegram Channel Assistance”应用的木马，在此后的两年中，我们又先后捕获了与此相关的数十个变种。我们发现，该木马主要伪装成社交、系统、色情视频及Adobe flash player等应用，借助社交软件Telegram进行传播。

木马的恶意行为演变过程大致分为4个版本，最初版本会伪造联系人，获取手机基本信息，静默拍照，拦截并转发指定短信信息。随着版本变化，木马的恶意行为不断增多，最新版本存在20多种恶意行为。入侵成功后攻击者可以完全控制用户手机，并对用户手机进行实时监控。

由于该木马演变过程中C&amp;C及代码结构均出现“arma”关键字，所以我们将该木马家族命名为“ArmaRat”。



## 二、 受影响地区

2016年7月起至今，根据我们的监测受到ArmaRat木马影响的地区主要是伊朗，占比高达91%。

[![](https://p4.ssl.qhimg.com/t012c86c90b57c4ef22.png)](https://p4.ssl.qhimg.com/t012c86c90b57c4ef22.png)



## 三、 感染链

通过对感染的用户手机进一步分析，我们发现了ArmaRat木马的传播方式。攻击者借助社交软件Telegram分享经过伪装的ArmaRat木马，用户下载安装运行后，会释放伪装成系统应用的恶意子包，诱导用户进行安装操作。[![](https://p5.ssl.qhimg.com/t0101cdd2977218532a.png)](https://p5.ssl.qhimg.com/t0101cdd2977218532a.png)



## 四、 伪装对象

ArmaRat木马主要伪装成社交、系统、色情视频及Adobe flash player等应用，其中还包括伪装成伊朗特色节日“诺鲁孜节”的应用。诺鲁孜节是伊朗、中亚及我国部分少数民族的节日，是为进入春耕生产，绿化、美化、净化环境做准备的节日。

[![](https://p5.ssl.qhimg.com/t017b16ab8f6327b7d7.png)](https://p5.ssl.qhimg.com/t017b16ab8f6327b7d7.png)

[![](https://p2.ssl.qhimg.com/t012f0700ebc73b2a70.jpg)](https://p2.ssl.qhimg.com/t012f0700ebc73b2a70.jpg)

[![](https://p3.ssl.qhimg.com/t01331d9feb07caa950.jpg)](https://p3.ssl.qhimg.com/t01331d9feb07caa950.jpg)



## 五、 后门分析

我们根据捕获到的ArmaRat木马变种的打包时间，恶意行为以及代码结构，将其演变过程分为4个版本。

[![](https://p2.ssl.qhimg.com/t016cc48ef545b16650.png)](https://p2.ssl.qhimg.com/t016cc48ef545b16650.png)

从版本1到版本4，ArmaRat木马功能不断增多，下图为每个版本的功能的迭代变化情况。

[![](https://p2.ssl.qhimg.com/t013e115cce12e2f578.png)](https://p2.ssl.qhimg.com/t013e115cce12e2f578.png)

另外，我们发现与普通的恶意软件行为相比，ArmaRat木马的一些恶意行为极为少见：

（1）伪造Telegram钓鱼页面

[![](https://p1.ssl.qhimg.com/t01acc5a51e46a0296f.png)](https://p1.ssl.qhimg.com/t01acc5a51e46a0296f.png)

（2）窃取Telegram验证码短信

[![](https://p0.ssl.qhimg.com/t0134041c6f34b4e98e.png)](https://p0.ssl.qhimg.com/t0134041c6f34b4e98e.png)

（3）伪造联系人

将控制号码9850001333125467伪装成“Telegram”或者“HAMRAHAVVAL”（疑似与伊朗电信提供商MCI相关）插入到联系人，推测为了更好的隐藏控制号码发送短信的行为记录。

[![](https://p1.ssl.qhimg.com/t019bf2e241f9454978.png)](https://p1.ssl.qhimg.com/t019bf2e241f9454978.png)



## 六、 C&amp;C分析

我们以时间轴和不同颜色的方式来展示ArmaRat木马的C&amp;C变化情况：

红色部分：C&amp;C前面几乎都是以“mcyvpn”开头，不同时间段URL的path部分分别是 “tgp”、“armaphone”，并且更换了新域名；

紫色部分：URL的path部分出现关键字“arma”，其中2017年2月出现了“192.168.92.10”的测试IP，之后的一段时间path部分均为“armaspyware”；

黑色部分：直到今年3月C&amp;C更换成指定的IP，但path部分与前一阶段保持一致，均为“spydb_api.php”；

[![](https://p2.ssl.qhimg.com/t01e8b0980d2d808255.png)](https://p2.ssl.qhimg.com/t01e8b0980d2d808255.png)

ArmaRat木马的C&amp;C主要使用动态域名，动态域名占比82%。动态域名可以将任意变换的IP地址绑定给一个固定的二级域名。不管这个线路的IP地址怎样变化，因特网用户还是可以使用这个固定的域名，来访问或登录用这个动态域名建立的服务器。分析人员和网络执法人员主要根据IP地址对木马服务器进行定位，如果木马使用动态域名的方式，即意味着木马服务器的IP地址时刻在改变，由此增加了追踪的难度。

[![](https://p5.ssl.qhimg.com/t017ede6f5c1f1cf150.png)](https://p5.ssl.qhimg.com/t017ede6f5c1f1cf150.png)

ArmaRat木马C&amp;C与样本关系如下图，可以看出样本与C&amp;C之间通过一些特殊字符“mcyvpn”、“arma”、“spydb_api.php”进行关联的整体情况。

[![](https://p5.ssl.qhimg.com/t017b43ab0b63357fdd.png)](https://p5.ssl.qhimg.com/t017b43ab0b63357fdd.png)



## 七、 总结

经过我们分析，ArmaRat木马长达两年的间谍活动背后的攻击者，回传隐私信息使用伊朗区号98，远控的短信指令包含波斯语，通过伪装的软件可以看出攻击者了解伊朗的传统节日。

近年来伊朗局势每况愈下，社会环境的动荡带来了更多负面效果，网络攻击日渐频繁，国外安全公司不断曝出TeleRAT、HeroRat等针对伊朗用户的攻击活动，这次发现的ArmaRat是又一实例，我们预测类似这种攻击活动还将继续，伴随着伊朗局势的不稳定会更加严重。

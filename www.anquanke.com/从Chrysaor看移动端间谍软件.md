> 原文链接: https://www.anquanke.com//post/id/250720 


# 从Chrysaor看移动端间谍软件


                                阅读量   
                                **32874**
                            
                        |
                        
                                                                                    



[![](https://p5.ssl.qhimg.com/t0191639095bf6a0797.jpg)](https://p5.ssl.qhimg.com/t0191639095bf6a0797.jpg)



## 认识Chrysaor

Chrysaor，似乎并不被人们熟知，至少比起它在 iOS 中赫赫有名的亲生兄弟而言是如此令人陌生，而他这个亲生兄弟就是——Pegasus（飞马座）。

**亲生兄弟 Pegasus**

Pegasus① 作为 iOS 系统最富盛名的间谍软件，由NSO Group Technologies开发，攻击链构造利用到了当时的3个0day漏洞，分别是：CVE-2016-4655,CVE-2016-4656,CVE-2016-4657，通过Safari WebKit内存泄漏，用户只要访问了挂有payload的网页，设备就会在用户毫不知情的情况下静默越狱，攻击者即可通过C/S模式远控目标手机。

[![](https://p5.ssl.qhimg.com/t013c033460f4cf919e.png)](https://p5.ssl.qhimg.com/t013c033460f4cf919e.png)

图1：Pegasus攻击链（图源LookOut团队报告①）

NSO公司将其作为武器出售给政府部门，用于监听特定目标。最早的Pegasus首次披露于2016年8月，但是据新闻媒体报道，NSO公司早于2010年便已经开始运营。而最早的Pegasus在iOS 9.3.5补丁后，上述3个0day得到了修复。

不过长期以来，因为这个攻击需要用户使用Safari访问载有payload的链接，所以攻击者往往都通过短信发送恶意链接给目标。而随着攻击次数增多与攻击过程被披露，大多数设备都更新了系统，同时用户也有了警惕心之后，再想通过短信发送恶意链接让用户点击就越来越困难了。所以Pegasus的目标转向了零点击攻击或是无线攻击。

就在2020年6月至8月，Pegasus家族又被发现利用了一个至少从iOS 13.5.1就存在的一个名为KISMET的0day漏洞③。研究人员认为，KISMET已经被Pegasus用来针对iMessage app实现了用户零点击漏洞利用。这次发现被攻击对象是Al Jazeera（半岛电视台）的记者、制片人、主持人以及高管的共36台私人手机。这些设备被四个Pegasus运营商攻击，其中包括来自阿联酋的SNEAKYKESTREL与来自沙特阿拉伯的MONARCHY。

[![](https://p3.ssl.qhimg.com/t013ec8bebce4741925.png)](https://p3.ssl.qhimg.com/t013ec8bebce4741925.png)

图2：上例中7月19日一次攻击的时间表

有意思的是，NSO公司一再强调，Pegasus间谍软件仅仅只会用于“调查恐怖主义和犯罪”。然而一份来自amnesty组织2021年7月的报告④却指出了该公司的Pegasus家族产品进行的，却是长期非法监视与侵犯人权行为。

遭殃的自然不止是iOS，在2016年8月左右，Pegasus曝光后，就有新闻报道称，NSO Group 开发出的武器化产品不仅仅只针对了iOS，同样被当成目标的还有黑莓与Android平台。

## Chrysaor简史

于是在2016年末，研究人员便开始密切关注NSO Group开发的针对Android平台的武器化间谍软件，结合大数据与云分析，通过威胁狩猎技术，找到了一些不存在于任何公共市场与任何类似于VT的公开资源中的app，这些app的一些数据都关联到了Pegasus-specific的IOC，如签名信息或是包名信息。也就这样，研究人员们锁定了Pegasus的Android版本，于2017年LookOut团队发布研究报告，同年4月，Google发布报告，将其正式命名为：Chrysaor② 。

Chrysaor虽然作为Google的正式命名，但因为同样是移动平台，同样被认为是NSO公司生产的武器间谍软件，所以即使被威胁狩猎捕获，一般也会归类到更早曝光更大规模的iOS平台下的Pegasus家族中，所以Chrysaor这个Android版本的大名已经快被人渐渐遗忘，在绝大部分报道中，都会用Pegasus统称iOS下的Pegasus与Android下的Chrysaor。

Google发布的官方调查中认为间谍软件是PHA（Potentially Harmful Application，潜在有害程序）的一种特殊形式，不同于其他 PHA，间谍软件花费大量的精力、时间、经济成本去入侵高价值目标，如记者、政客等，这完全符合APT的做法。但是不管是捕获样本也好，亦或者是公开资料也好，都没有近几年的Chrysaor资料，近段时间一些疑似的样本也基本诊断为误判，所以本文从老版本的Chrysaor入手，揭开间谍软件的神秘面纱。而且可能因为Android开源的原因，Chrysaor并没有利用任何 0day，多是一些已经曝光的漏洞，所以从攻击成本来看，Chrysaor比更早披露的Pegasus要低。

## Chrysaor攻击原理

Chrysaor做为间谍软件，它的主要工作就是监听目标设备并与C2服务器(Command &amp; Control server)保持联络，但是值得注意的是，作为武器使用的间谍软件攻击目标是特定的，所以为特定机型进行了定制。

例如，以Google给出的SHA256值为 ade8bef0ac29fa363fc9afd958af0074478aef650adeb0318517b48bd996d5d5 ，包名为 : com.network.android的样本来说，这是一个针对内核版本 &lt;= 4.3的三星设备定制的恶意软件，至于为什么这么说，会在后文说明。

## 诱导安装

首先用户被诱导下载或是被无线攻击安装样本，虽说看上去这一步很没有技术含量，但是在执行中是最困难的部分，但也存在大量做法让用户安装。请注意这里并没有报告指出该怎么做，但是假设我是一名攻击者，我会考虑的方法有：

1、社工诈骗，社会工程学往往是攻击的第一步，而且就各种案例来看，社工的成功率往往不低。

2、结合其他的漏洞。可能利用的漏洞有很多很多，这里就举一个首先想到的，如CVE-2017-13156 Janus Android v1签名验证漏洞，这个漏洞可以使得EXP通过签名验证，这就会导致恶意软件被当作正常软件安装，一个带有payload的不安全的伪造应用取代原来正常的应用驻留设备。在软件升级安装时，通过一个构造的不安全的网络通道，例如一个公开的WIFI、伪基站监听，劫持一个没有加密的升级过程，就可以做到在应用升级中替换。当然这只是一个例子，而且十分理想化，实际操作肯定不会有笔者说的这么轻松，并且捕获与公开的的样本中似乎都没有使用到该漏洞，同时在时间上这个漏洞也在更晚才被发现。

第一步也是整个攻击过程最难的一步，首先这意味着需要用户开启 “允许安装未知来源的APK”选项，若是被攻击对象防范意识够好，不开启这个选项，不连接不安全的 WIFI等等情况，都会让间谍软件非常困难进入设备。

## 提权

安装进入设备后，马上就会调用Framaroot来提权，Framaroot是一个提权工具，它包含几个用于提权的漏洞，而Framaroot在早期版本就支持三星设备了。而且请注意，Framaroot作者为保证尽量减少Framaroot被恶意软件利用，所以 Framaroot只提供短期root，当system分区被修改时，root即会失效。

[![](https://p4.ssl.qhimg.com/t01f05b595aa519c680.png)](https://p4.ssl.qhimg.com/t01f05b595aa519c680.png)

图3：FramarootF&amp;Q关于漏洞修补与系统更新

不过对于普通用户而言，OTA升级是最常见的升级，Framaroot的提权最终还是通过SuperSU来进行管理的，但是SuperSU可以在OTA升级中活下来，不过因为Framaroot使用的是漏洞提权，所以在系统升级时只要漏洞被修复了就会提权失败，辛辛苦苦植入的恶意软件就没用了。

作者显然也是很清楚，若是漏洞全被修复了，则会调用 /system/csk 中的一个提权 ELF 来提权。很抱歉笔者也不知道这是一个什么文件，因为得到的样本并没有完整的文件，调用的部分并没有在得到的样本中，且没有三星 4.3 的系统来验证，暂且不论。而为了避免让系统升级修补漏洞，当提权完成后，恶意程序隐藏自身后做了以下行为：

•将自身安装在/system分区上以在恢复出厂设置后持续存在。

•删除三星的系统更新应用程序(com.sec.android.fotaclient)并禁用自动更新（方法是将Settings.System.SOFTWARE_UPDATE_AUTO_UPDATE设置为 0）。

•删除 WAP 消息推送并更改 WAP 消息设置，推测是出于反取证目的。

•启动一个content observers，并开始循环主程序，用以接收远程命令并窃取数据。

正如上文提到过的一样，为了防止漏洞被修复，也为了防止更新后提权突然失效，最好的办法就是不要让设备更新，于是它把更新程序删了，这里就显示出了为何其为定制软件，因为这个升级程序是三星系统独有的。

## 收集数据

等到它安顿下来后，他就会开始工作了，Chrysaor 收集的信息有很多，例如位置、应用数据（也包括邮件、联系人、日历、短信等）、屏幕截图、输入按键记录、电话窃听。

通过 Alarm 类设置循环定时任务，每过一段时间则会发送给 C2 服务器大量信息，例如位置信息等。而且与信息收集配合，读取特定app目录/data/data 下的内容，将其全部存储到消息队列中，并由Alarm类定期发送给服务器，受到监视的app有：WhatsApp、Twitter、Facebook、Kakoa、Viber、Skype 等。

通过ContentObserver收集短信、联系人、邮件以及受监视的 app 的所有更改。当拨打电话时，恶意软件会在后台保持链接，用户可以正常通话，但是当尝试使用设备时只能看见黑屏，因为此时恶意软件正在挂断电话，重置通话设置，所以用户并不能与设备交互。

还会通过lib文件监视键入键盘与捕获屏幕，这些会在后文具体分析。

## 自我删除

可能出于反取证的目的，Chrysaor 自身也有自我删除功能，分别在以下三种情况触发：

1.C2服务器的指令

2.60天内无法连接到C2服务器

3.存在“/sdcard/MemosForNotes”文件

## 详细分析

以安恒威胁情报中心的一个捕获样本为例，我们来具体分析一下 Chrysaor 的监听方法，样本 SHA256 为：

bd8cda80aaee3e4a17e9967a1c062ac5c8e4aefd7eaa3362f54044c2c94db52a

先看一下文件的树形结构：

[![](https://p1.ssl.qhimg.com/t01f3fc852bad02bac1.png)](https://p1.ssl.qhimg.com/t01f3fc852bad02bac1.png)

图4:样本文件树

这里展示的结构是未被反编译的，可以注意到，没有比较常见的lib文件夹，反倒是/res/raw中存在大量看着很危险的文件名。



## 远程通信

**MQTT**

可以发现存在一个文件路径“org/eclipse/paho/client/mqttv3”，这是MQTT协议的国际化文件夹路径，首先先了解一下MQTT协议⑥是什么。

[![](https://p3.ssl.qhimg.com/t017cfa1b8a5bea7f0c.png)](https://p3.ssl.qhimg.com/t017cfa1b8a5bea7f0c.png)

图5：MQTT

MQTT，Message Queue Telemetry Transport，消息队列遥测传输协议，其基于“发布/订阅”模式，可用以轻量级数据通讯，构建在 TCP/IP 协议基础上，对于恶意软件来说，它只用了很小的带宽很少的代码量，却可以提供实时可靠的链接，这保证了与 C2 服务器的连接。

但是即使 MQTT 看上去非常棒，攻击者也添加了限制条件不使用它，所以恶意软件需要得知当前设备是在使用 WIFI，还是在使用流量等信息，根据具体场景决定是否使用 MQTT。

**短信**

攻击链中笔者认为最有意思的地方应该就在于其对短信的应用，即使是一个看似误发的短信其实也是可以用来远程操作，大部分人可能都会认为是有人填错了电话号码，错误接受了短信。

[![](https://p0.ssl.qhimg.com/t01c049cac7be49c1b7.png)](https://p0.ssl.qhimg.com/t01c049cac7be49c1b7.png)

图6：一个正常的谷歌验证码短信

然而从 LookOut 团队的捕获⑦来看，这也是远控手段之一，所有接受到的短信正文都会不区分大小写的暴力搜索your google verification code，若是匹配到了字符串，则短信会按以下格式解析：

text:[随机6位数字][用于操作的数字]a=[Ack ID]&amp;[命令参数]&amp;s=[消息签名]

伪装成验证码的 7 位数字前 6 位是随机的，而最后一位是用来操作的，用于操作的数字详情可以按下表理解：

[![](https://p0.ssl.qhimg.com/t019b9e722883157f2a.png)](https://p0.ssl.qhimg.com/t019b9e722883157f2a.png)

表格1：操作数字详解

例如验证码为1234567,则123456是随机生成的，而7则是指令，恶意程序通过内容接收者解析了这个指令后，则会通过 HTTP 发送一个确认接受的指令，a参数中的Ack ID会随着HTTP头发送出去，这样C2服务器就知道设备确认接受到是哪一个指令。

而用以保证是该短信是由攻击者发来的，则是靠最后的签名信息，这个签名是恶意软件初始化后向 C2 服务器发送的一个信息的 MD5 哈希值，所以只有攻击者才会知道它，以此确保不会被错误执行指令。

## 获取屏幕图像

这个操作路径中的/res/raw/take_screen_shot ELF文件完成的：

[![](https://p2.ssl.qhimg.com/t0119fafe46f4b71225.png)](https://p2.ssl.qhimg.com/t0119fafe46f4b71225.png)

图7：take_screen_shot分析

要求输入两个参数，同时第二个参数传给dest ，dest与这个字符串一起传入sub_90EC函数，并返回返回值，那么“/dev/graphics/fb0”是什么呢？

一般来说获取屏幕画面用的是FrameBuffer ，这是 Linux 中对显示的抽象。在 Linux 万物皆文件的概念中，显示设备自然也是可以当作文件来处理的，可以对比理解为显存，而绝对路径“/dev/graphics/fb0”正是 FrameBuffer 位置。所以将这个位置传入下一个函数很大意义上可以说明就是为了获取到屏幕截图，而具体是怎么得到这个帧的就不展开说明了，因为存放的是像素点，在其中需要转换为图片传出，看了下大致是由像素点转换为png格式图片。所以这个ELF文件就是从“/dev/graphics/fb0”得到屏幕当前的图像信息。

## Framaroot 提权

也是由ELF文件做到的，/res/raw/sucopier做到，这个ELF文件用的是 Framaroot的逻辑，但是有意思的是Frameroot并不是开源的，而NSO是怎么得到Framaroot的源码，那就不得而知了。具体怎么做到提权的这里就不展开说明了，因为 Framaroot 能够利用的提权漏洞在 Android 8.0 以后就都从系统层面限制死了，没有开展说明的意义。

## 键盘记录

Android的Keylogging一直是安全人员中的较为常见的东西，在这个样本做到键盘键入记录的则是/res/raw/libk的ELF文件。执行过程中，这个 ELF 文件会被加载到/data/local/tmp/libuml.so ，在被删除前，它会立即注入键盘进程，而按键记录会被写入/data/local/tmp/ktmu/ulmndd.tmp文件中：

[![](https://p1.ssl.qhimg.com/t01ca4ebfb28d4ba6ab.png)](https://p1.ssl.qhimg.com/t01ca4ebfb28d4ba6ab.png)

图8：临时文件ulmndd.tmp

但这只是临时文件，最终会写到/data/local/tmp/ktmu/finidk.&lt;时间戳&gt;文件中：

[![](https://p5.ssl.qhimg.com/t01162abf3647e239f7.png)](https://p5.ssl.qhimg.com/t01162abf3647e239f7.png)

图9：finidk.&lt;时间戳&gt;

如果您恰好玩过或是看过英文版《精灵宝可梦》相关的作品或游戏，你会发现一个很眼熟的名字——Jigglypuff，胖丁。

[![](https://p2.ssl.qhimg.com/t015720e4cdd5d41ded.png)](https://p2.ssl.qhimg.com/t015720e4cdd5d41ded.png)

图10：Jigglypuff

因为Pegasus已经在iOS中就已经被重点监视了，为了避开被字符串检测，所以在Android中，研究人员推测攻击者使用了JigglyPuff作为其内部代号。

## 强混淆

最后一个有意思的点就是Chrysaor 在Java层采用了非常强的混淆，例如所有的字符串都用了Base64与异或，已经所有的方法调用都用了反射：

[![](https://p4.ssl.qhimg.com/t0127f715855a4de01d.png)](https://p4.ssl.qhimg.com/t0127f715855a4de01d.png)

图11：强混淆

请注意是所有的字符串与方法调用，例如在类 “seC.dujmehn.Besqjyed.EdQBqhCHusuyluh” 中有一个语句是：

BuBlJJJJJXDFKYirSooj(ZQjvHTeBlVUCiutw(QVozqddybqHRWaDm(QmdafFtUsXvVcahq(mprchPoltGTBsyTr(newStringBuilder(onReceive9584()),mRvgkfrWJgjwKERW(newDate())),onReceive9585()),igMiBMAFlnpIGcji(intent))));

实际上这只是一个字符串拼接操作，翻译过来只是：

传给q类的a方法一个字符串：“OnAlarmReceiver onReceive:”+ GMT时间 +“action:” + Intent捕获的action

这也是Pegasus家族的一个特点，这样做的好处就是调用了哪些方法压根不会被反病毒引擎的静态扫描发现，以及一些看着就很危险的字符串也不会被扫出来，除非动态全部 hook 下来，不然静态分析对此是完全无解的。

## 思考总结

实际上若您仔细阅读过Pegasus相关资料会发现Chrysaor与其有大量相同点，例如都会注入进程以获得键盘记录，都会使用短信来进行远控，都使用了MQTT协议等等等等。

在设备是主要使用设备时，其中会含有大量的敏感信息，而这些信息往往会被各类厂商大数据分析得到人物画像，这是一个模糊的抽象的东西，实际上厂商知道的始终也有限，且多数都被法律限制。而间谍软件就不同，它是明抢。那每个人都需要担心自己的信息被这么抢走吗？

其实并不需要过于担忧。从分析中我们可以看出间谍软件的特性，它就像Windows中的远控程序的删减版，但是不论是Android或是iOS都将权限这一问题限制的很死，程序只能在自己的沙箱运行，在没有提权的情况下，根本访问不到不允许访问的内容，于是间谍软件必然需要提权。可是随着安全研究体系与人才的完善，一个可以提权的0day需要付出的成本是很高的，而若是广撒网式传播则被发现的可能性非常高，显然成本与利益是不匹配的。

而真正需要在意和关心的，则是那些真正的高目标人群，例如政客、媒体、高管等等，设备中可能有涉及到高价值，攻击方可以不顾代价获取的信息。

## 防范建议

### **从源头**

不要开启 “允许未知来源的APK安装”，最好只使用从官方应用商店下载的APK。当然但是这并不意味着从官方应用商店下载的应用就可以完全相信，例如同样是间谍软件的Lizpizzan家族，其攻击链一开始就是从一个完全正常的，在应用商店上架的APP开始，再由它下载安装恶意程序。

不过作为用户而言，不开启“允许未知来源的APK安全”这一选项仍然可以保证安全。

### **从提权**

虽说防范 0day 攻击基本不现实，但是就这个案例来说，Framaroot所利用漏洞仅能在Android 8.0及更低使用，若设备内核版本号高于 Android 8.0则可以不用担心被现有捕获的Chrysaor攻击。

但是这并不意味着绝对安全，无论内核版本多少，都应当即时跟着厂商发布的更新版本更新，确保不会被 1day 或是曾经还未修复的漏洞攻击。同时更不要自己通过刷机获取 root 权限，任何一个存有敏感信息的 Android 设备都最好不要手动获取 root 权限，先不说是否可以安全地拿到 root 权限，即使 root 工具是安全的，也让恶意软件有了更多可趁之机。

而iOS用户则更是如此，据报告称，2014年至2021年7月，Pegasus的攻击一直没有停止过，永远无法保证攻击者是否还存在0day未被披露，同时在野的Nday漏洞也需要每名使用者即时更新系统，不要因为嫌弃升级系统可能带来的卡顿问题而忽视更严重的安全问题。

而若您已经开启了该选项并手动获取了 root 权限，请仔细检查应用清单，看是否有陌生的应用程序，虽然目前主流的已经被披露出的Android端间谍软件都是以独立app存在的，但是都已经放入了/system分区，而我们刷机或是恢复出厂设置都是擦除/cache与/data分区，所以双清也不会解决问题。只有准确找出间谍软件，然后利用root权限将其删除，才能保证不被影响。

安恒威胁情报中心猎影实验室将持续关注网络安全动态。



## 参考链接

①LookOut团队针对Pegasus的分析：https://info.lookout.com/rs/051-ESQ-475/images/lookout-pegasus-technical-analysis.pdf

②Google关于Chrysaor的博客：https://security.googleblog.com/2017/04/an-investigation-of-chrysaor-malware-on.html

③citizen实验室报告称记者疑似被iMessage零点击漏洞攻击：https://citizenlab.ca/2020/12/the-great-ipwn-journalists-hacked-with-suspected-nso-group-imessage-zero-click-exploit/

④amnesty 2021年7月关于Pegasus的报告：https://www.amnesty.org/en/latest/research/2021/07/forensic-methodology-report-how-to-catch-nso-groups-pegasus/

⑤Google关于Lipizzan的博客：https://security.googleblog.com/2017/07/from-chrysaor-to-lipizzan-blocking-new.html

⑥ MQTT协议：https://www.runoob.com/w3cnote/mqtt-intro.html

⑦ LookOut团队针对Chrysaor的分析：https://info.lookout.com/rs/051-ESQ-475/images/lookout-pegasus-android-technical-analysis.pdf

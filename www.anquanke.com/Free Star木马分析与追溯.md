> 原文链接: https://www.anquanke.com//post/id/83722 


# Free Star木马分析与追溯


                                阅读量   
                                **108685**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t01aec6897b7588fcad.jpg)](https://p2.ssl.qhimg.com/t01aec6897b7588fcad.jpg)

**引子**

人在做,天在看。

360天眼实验室一直与各种木马远程做斗争,对手总是试图找到办法使自己处于安全监视者的雷达之外。近期我们看到了一些较新版本的大灰狼木马采用了一种新的上线方式,与利用QQ空间、微博、博客或者网盘等方式上线相似,其通过调用QQ一个获取用户昵称的接口来获取上线地址,又一种通过正常通信渠道进行非正常通信的企图。

[![](https://p3.ssl.qhimg.com/t017b40d2afa86924d7.png)](https://p3.ssl.qhimg.com/t017b40d2afa86924d7.png)

[![](https://p2.ssl.qhimg.com/t01c25403dac2190583.png)](https://p2.ssl.qhimg.com/t01c25403dac2190583.png)

当一个方法被证明有效,很容易就会被其他造马者“借鉴”。通过基于360威胁情报中心数据的关联性分析,我们发现了一个名为Free Star的木马也采用了这种上线方式,该木马最早出现于2015年2月左右,作者从2015年5月开始在各个免杀论坛售卖源码,而新版本活动时间就在2016年1月份至今。其部分代码结构和Gh0st、大灰狼的代码比较相似,可以认为是那些远控的衍生版本。

下图为从某免杀论坛下载到的Free Star木马控制端,可以看见配置Server端中需要将IP地址加密后设置成QQ昵称,然后由服务端通过访问对应的接口来获取QQ昵称,进而解密出木马上线的IP地址:

[![](https://p4.ssl.qhimg.com/t016367d457851216ce.png)](https://p4.ssl.qhimg.com/t016367d457851216ce.png)

访问的接口如下:

[![](https://p5.ssl.qhimg.com/t01dae5bb467ab5934e.png)](https://p5.ssl.qhimg.com/t01dae5bb467ab5934e.png)

今天我们要分析的对象就是这个名为Free Star的木马,这个也是360天眼实验室新晋小伙伴的处女作。

**样本分析**

样本信息基本识别信息如下,供同行们参考。

木马文件MD5: c3d7807f88afe320516f80f0d33dc4f3、a1bb8f7ca30c4c33aecb48cc04c8a81f

分析得到木马主要行为总结:

l添加服务项,开启服务,转移自身文件

l用gethostbyname函数获取上线地址或访问QQ昵称接口获取木马上线地址,并进行网络连接

l检测杀软进程

l开启线程接收指令,执行远控功能

添加服务项,开启服务,转移自身文件

木马首先判断是否已经注册了服务项,如果没有注册,进入自拷贝、创建服务的流程:

[![](https://p4.ssl.qhimg.com/t019319b9fa87144957.png)](https://p4.ssl.qhimg.com/t019319b9fa87144957.png)

创建服务

[![](https://p3.ssl.qhimg.com/t01cf55115389a612d3.png)](https://p3.ssl.qhimg.com/t01cf55115389a612d3.png)

[![](https://p5.ssl.qhimg.com/t014b4915ff9b77a0a8.png)](https://p5.ssl.qhimg.com/t014b4915ff9b77a0a8.png)

调用StartServiceA开启服务,进入主功能流程

[![](https://p0.ssl.qhimg.com/t01a96851759dcc02a0.png)](https://p0.ssl.qhimg.com/t01a96851759dcc02a0.png)

在拷贝自身,移动到%appdata%中指定目录

[![](https://p0.ssl.qhimg.com/t0185c22b2e2c0845bc.png)](https://p0.ssl.qhimg.com/t0185c22b2e2c0845bc.png)

创建自删除脚本并执行,用于删除自身文件以隐藏自身

[![](https://p4.ssl.qhimg.com/t01676a7ef8439e5de8.png)](https://p4.ssl.qhimg.com/t01676a7ef8439e5de8.png)

[![](https://p2.ssl.qhimg.com/t0153e56030fdd6cd17.png)](https://p2.ssl.qhimg.com/t0153e56030fdd6cd17.png)

脚本内容如下:

[![](https://p2.ssl.qhimg.com/t011ad8b13c9f10d7be.png)](https://p2.ssl.qhimg.com/t011ad8b13c9f10d7be.png)

获取上线地址

以服务项启动进入时,通过注册表对应的项判断服务是否存在,决定是否进入开始进行网络连接。

[![](https://p0.ssl.qhimg.com/t014b24d79fd2d70c35.png)](https://p0.ssl.qhimg.com/t014b24d79fd2d70c35.png)

解密动态域名、QQ号、端口号:

解密算法是Base64解码后,异或0x88 ,加0x78,再异或0x20

[![](https://p0.ssl.qhimg.com/t0149142bcf31f00e25.png)](https://p0.ssl.qhimg.com/t0149142bcf31f00e25.png)

获取IP地址

[![](https://p4.ssl.qhimg.com/t01141ba71bf7548181.png)](https://p4.ssl.qhimg.com/t01141ba71bf7548181.png)

[![](https://p1.ssl.qhimg.com/t013258045c62922940.png)](https://p1.ssl.qhimg.com/t013258045c62922940.png)

如果第一种方式不成功,则通过访问QQ昵称接口获取IP地址:

[![](https://p2.ssl.qhimg.com/t016afe58cc7b38a568.png)](https://p2.ssl.qhimg.com/t016afe58cc7b38a568.png)

[![](https://p5.ssl.qhimg.com/t01e05636a6d231c29a.png)](https://p5.ssl.qhimg.com/t01e05636a6d231c29a.png)

获取到的QQ昵称为: deacjaikaldSS

[![](https://p5.ssl.qhimg.com/t011c9082cb41d45454.png)](https://p5.ssl.qhimg.com/t011c9082cb41d45454.png)

对获取到的QQ昵称解密:解密算法是 + 0xCD

[![](https://p4.ssl.qhimg.com/t01e69d09c89e66a209.png)](https://p4.ssl.qhimg.com/t01e69d09c89e66a209.png)

解密后取得IP地址为: 1.207.68.91 ,开始连接:

[![](https://p5.ssl.qhimg.com/t018c05c93cf8f076b5.png)](https://p5.ssl.qhimg.com/t018c05c93cf8f076b5.png)

循环连接这两个地址直到连接成功,连接成功后进入远控流程

获取受害者系统信息

首先获取主机名

[![](https://p0.ssl.qhimg.com/t01b6236133146beec7.png)](https://p0.ssl.qhimg.com/t01b6236133146beec7.png)

获取CPU型号

[![](https://p4.ssl.qhimg.com/t01380dc082c8c42962.png)](https://p4.ssl.qhimg.com/t01380dc082c8c42962.png)

获取其他信息等等

[![](https://p5.ssl.qhimg.com/t01b1b17f74e85854ed.png)](https://p5.ssl.qhimg.com/t01b1b17f74e85854ed.png)

遍历进程,查找杀软进程

[![](https://p2.ssl.qhimg.com/t0156385b350d238694.png)](https://p2.ssl.qhimg.com/t0156385b350d238694.png)

检查杀软的进程名用一个双字数组来存储,每个双字的值是指向对应杀软进程名的字符串的指针。如下:

[![](https://p1.ssl.qhimg.com/t01536845b75f657505.png)](https://p1.ssl.qhimg.com/t01536845b75f657505.png)

[![](https://p5.ssl.qhimg.com/t01a92487feeb64c71d.png)](https://p5.ssl.qhimg.com/t01a92487feeb64c71d.png)

创建新线程,用于循环等待接收远控指令

[![](https://p3.ssl.qhimg.com/t0175180ee101f89df4.png)](https://p3.ssl.qhimg.com/t0175180ee101f89df4.png)

最后创建一个新的线程,用于接收远控指令,主要的功能有远程文件管理、远程Shell、屏幕监控、键盘记录等等,这里就不再赘述了。

代码整体流程图如下:

[![](https://p4.ssl.qhimg.com/t01550ee2f95b86f944.png)](https://p4.ssl.qhimg.com/t01550ee2f95b86f944.png)

**幕后黑手**

这种通过QQ昵称获取上线地址的方式在躲避检测的同时也暴露了放马者的QQ号,我们在通过样本拿到的QQ号中找到了一个比较特殊的:550067654

[![](https://p4.ssl.qhimg.com/t01683f9844416e158e.png)](https://p4.ssl.qhimg.com/t01683f9844416e158e.png)

通过搜索引擎,我们发现这个QQ号有可能是木马作者的一个业务QQ号,这个QQ在多个免杀论坛上注册了账号,经过进一步的确认,发现其的确是木马作者:

[![](https://p0.ssl.qhimg.com/t01ef7ed961b5ab6a0d.png)](https://p0.ssl.qhimg.com/t01ef7ed961b5ab6a0d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015e235547c93c93ed.png)

[![](https://p1.ssl.qhimg.com/t01faf0f26174792b97.png)](https://p1.ssl.qhimg.com/t01faf0f26174792b97.png)

从作者在某论坛上展示的木马功能截图可以发现,其曾经在贵州毕节地区活动。

[![](https://p4.ssl.qhimg.com/t0185662c5a4ecf2c8d.png)](https://p4.ssl.qhimg.com/t0185662c5a4ecf2c8d.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01187cbef1eff7cce8.png)

我们还发现作者用QQ邮箱账号注册了支付宝账号,通过支付宝账号的信息,发现作者的名字可能是: *怡

[![](https://p0.ssl.qhimg.com/t017ed00ec783f95210.png)](https://p0.ssl.qhimg.com/t017ed00ec783f95210.png)

通过某社工库,我们找到了作者经常使用的qq邮箱和密码,通过这条线索,我们找到了更多的信息:

[![](https://p1.ssl.qhimg.com/t012a163d40ee088902.png)](https://p1.ssl.qhimg.com/t012a163d40ee088902.png)

在某商城发现了几笔订单信息,从而取到作者的名字、常在地区:

[![](https://p1.ssl.qhimg.com/t01e1c699f881d94367.png)](https://p1.ssl.qhimg.com/t01e1c699f881d94367.png)

[![](https://p1.ssl.qhimg.com/t01fcec3d14ded1a31b.png)](https://p1.ssl.qhimg.com/t01fcec3d14ded1a31b.png)

[![](https://p2.ssl.qhimg.com/t016161f2a00f06ea6f.png)](https://p2.ssl.qhimg.com/t016161f2a00f06ea6f.png)

[![](https://p5.ssl.qhimg.com/t011dda8a8d090a2e7f.png)](https://p5.ssl.qhimg.com/t011dda8a8d090a2e7f.png)

从身份证信息来看,确定作者是贵州毕节地区的人,名字就叫田怡。这也与上面获得的信息一致。

关于木马作者的追踪到此就告一段落了,有兴趣的同学们可以继续深挖,用一张天眼威胁情报中心数据关联系统生成的关系图来结束此次挖人之旅。

[![](https://p3.ssl.qhimg.com/t01d8f1d6be39a26d4a.png)](https://p3.ssl.qhimg.com/t01d8f1d6be39a26d4a.png)

**传播途径**

分析完样本和木马作者之后,我们再看看该类木马的传播途径。

在我们捕获到的众多样本中,有一个样本访问的地址引起了我们的注意,通过关联,发现这是一些挂机、点击软件访问的地址,http://sos.hk1433.cc:10089/bbs.html

[![](https://p5.ssl.qhimg.com/t016881167ac8673f6b.png)](https://p5.ssl.qhimg.com/t016881167ac8673f6b.png)

打开网页后,查看源代码,如下:

[![](https://p0.ssl.qhimg.com/t017d8951304dca8a77.png)](https://p0.ssl.qhimg.com/t017d8951304dca8a77.png)

可以看到,这个页面加载了一个swf文件。将这个swf文件下载后打开,发现是Hacking Team的flash漏洞利用,下图红色框出的部分就是ShellCode:

[![](https://p3.ssl.qhimg.com/t015060a4e2c494f7dc.png)](https://p3.ssl.qhimg.com/t015060a4e2c494f7dc.png)

ShellCode的功能就是一个Dropper,会将之前解密出来的PE释放并执行,而这个PE文件正是Free Star木马。

解密前的PE文件:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014f2255b00e6b5fc1.png)

解密后:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ee9d61f3194078ef.png)

ShellCode:

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t010d31960163796689.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012caafc5898bad2e6.png)

由此我们可以知道,该木马的传播方式之一即是通过网页挂马。

[![](https://p1.ssl.qhimg.com/t01d158bef44178425b.png)](https://p1.ssl.qhimg.com/t01d158bef44178425b.png)

通过上图可以看到挂马页面在3月28日上午9点上传,截至我们写这份报告的时间,3月29下午16点,点击量已经有13000多,而这仅仅只是冰山一角,但是在这里就不再深入。在我们的360威胁情报中心可以很容易地通过关联域名查询到对应的样本:

[![](https://p5.ssl.qhimg.com/t01ee06f849b02c5b3b.png)](https://p5.ssl.qhimg.com/t01ee06f849b02c5b3b.png)

**总结**

通过这次分析,我们发现这个木马本身所用到的技术相当普通,与之前发现的木马基本一脉相承,体现出迭代化的演进。由于巨大的利益驱动,黑产始终保有对技术和机会的高度敏感,就象任何先进的技术首先会被用于发展武器一样,成熟可靠的漏洞利用技术及躲避检测的方案几乎肯定会立刻被黑产所使用传播。360威胁情报中心的数据基础以及自动化的关联分析为我们从样本分析、关系判定、来源追溯提供全方位的信息支持,成为我们用来对抗黑产以及其他高级攻击的强有力的武器。

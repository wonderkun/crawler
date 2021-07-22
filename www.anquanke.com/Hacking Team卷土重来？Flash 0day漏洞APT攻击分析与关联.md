> 原文链接: https://www.anquanke.com//post/id/147372 


# Hacking Team卷土重来？Flash 0day漏洞APT攻击分析与关联


                                阅读量   
                                **151052**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t01c35439cedbc91f25.jpg)](https://p3.ssl.qhimg.com/t01c35439cedbc91f25.jpg)

## 背景

360企业安全威胁情报中心近期捕获到了一例使用Flash 0day漏洞配合微软Office文档发起的APT攻击案例，攻击使用的样本首次使用了无Flash文件内置技术（Office文档内不包含Flash实体文件）。我们在确认漏洞以后第一时间通知了厂商Adobe，成为国内第一个向厂商报告此攻击及相关漏洞的组织，Adobe在昨日发布的安全通告中致谢了360威胁情报中心。

[![](https://p0.ssl.qhimg.com/t015ece1f62a1315c25.png)](https://p0.ssl.qhimg.com/t015ece1f62a1315c25.png)

Adobe反馈确认漏洞存在并公开致谢

整个漏洞攻击过程高度工程化：攻击者将Loader（第一阶段用于下载Exploit的Flash文件）、Exploit（第二阶段漏洞利用代码）、Payload（第三阶段ShellCode）分别部署在服务器上，只有每一阶段的攻击/检测成功才会继续下载执行下一阶段的代码，这样导致还原整个攻击流程和漏洞利用代码变得非常困难。360威胁情报中心通过样本的特殊构造分析、大数据关联、域名分析，发现本次使用的相关漏洞攻击武器疑似与Hacking Team有关。

由于此漏洞及相应的攻击代码极有可能被黑产和其他APT团伙改造以后利用来执行大规模的攻击，构成现实的威胁，因此，360威胁情报中心提醒用户采取应对措施。



## 相关漏洞概要
<td valign="top" width="83">**漏洞名称**</td><td colspan="5" valign="top" width="485">Adobe Flash Player远程代码执行漏洞</td>
<td valign="top" width="83">**威胁类型**</td><td valign="top" width="104">远程代码执行</td><td valign="top" width="85">**威胁等级**</td><td valign="top" width="38">高</td><td valign="top" width="66">**漏洞****ID**</td><td valign="top" width="192">CVE-2018-5002</td>
<td width="83">**利用场景**</td><td colspan="5" valign="top" width="485">攻击者通过网页下载、电子邮件、即时通讯等渠道向受害者发送恶意构造的Office文件诱使其打开处理，可能触发漏洞在用户系统上执行任意指令获取控制。</td>
<td colspan="6" valign="top" width="568">**受影响系统及应用版本**</td>
<td colspan="6" valign="top" width="568">Adobe Flash Player（29.0.0.171及更早的版本）</td>
<td colspan="6" valign="top" width="568">**不受影响影响系统及应用版本**</td>
<td colspan="6" valign="top" width="568">Adobe Flash Player 30.0.0.113（修复后的最新版本）</td>
<td colspan="6" valign="top" width="568">**修复及升级地址**</td>
<td colspan="6" valign="top" width="568">https://get.adobe.com/flashplayer/</td>



## 样本概况

从捕获到的攻击样本语言属性、CC服务器关联信息我们推断这是一起针对卡塔尔地区的APT攻击。样本于5月31日被上传到VirusTotal以后的几天内为0恶意检出的状态，直到6月7日也只有360公司的病毒查杀引擎将其识别为恶意代码，360威胁情报中心通过细致的分析发现了其中包含的0day漏洞的利用。

[![](https://p3.ssl.qhimg.com/t01bb20ac95f0d86f36.png)](https://p3.ssl.qhimg.com/t01bb20ac95f0d86f36.png)



## 攻击分析

通过对样本执行过程的跟踪记录，我们还原的样本整体执行流程如下：

[![](https://p0.ssl.qhimg.com/t01fa2ea540f32a11e7.png)](https://p0.ssl.qhimg.com/t01fa2ea540f32a11e7.png)

包含Flash 0day的恶意文档整体执行流程

### 诱饵文档

攻击者首先向相关人员发送含有Flash ActiveX对象的Excel诱饵文档，诱骗受害者打开：

[![](https://p0.ssl.qhimg.com/t01c0dfb8626dc95af7.png)](https://p0.ssl.qhimg.com/t01c0dfb8626dc95af7.png)

### Flash ActiveX控件

而诱饵文档中包含了一个Flash ActiveX控件：

[![](https://p5.ssl.qhimg.com/t012b5b8fab2c127049.png)](https://p5.ssl.qhimg.com/t012b5b8fab2c127049.png)

但该Flash ActiveX对象中并不包含实体Flash文件，需要加载的Flash文件通过ActiveX对象中的URL连接地址远程加载，这样能非常好的躲避杀毒软件查杀：

[![](https://p1.ssl.qhimg.com/t0139334a4f6b06bb9b.png)](https://p1.ssl.qhimg.com/t0139334a4f6b06bb9b.png)

通过Excel文档向远程加载的Flash传递参数，其中包含了第二阶段Flash的下载地址以及样本和CC服务器的通信地址：

[![](https://p5.ssl.qhimg.com/t011b9218bcd80b4cfb.png)](https://p5.ssl.qhimg.com/t011b9218bcd80b4cfb.png)

### 第一阶段Flash

通过Flash ActiveX对象中的URL连接地址下载回来一阶段的Flash文件，该Flash文件最主要的功能是继续和远程服务器通信并下载回来使用AES加密后的第二阶段Flash文件：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01d9d59fa321da1053.png)

获取第一阶段Flash文件

### 第二阶段Flash 0day

由于第一阶段的Flash会落地，所以为了避免实施漏洞攻击的Flash代码被查杀或者被捕获，攻击者通过第一阶段的Flash Loader继续从服务器下载加密的攻击模块并内存加载。

从服务器返回的数据为[KEY+AES加密数据]的形式，第一阶段的Flash文件将返回的数据解密出第二阶段的Flash文件：

[![](https://p5.ssl.qhimg.com/t016badd41c1781244b.png)](https://p5.ssl.qhimg.com/t016badd41c1781244b.png)

获取AES加密后的第二阶段Flash

解密出使用AES CBC模式加密的第二阶段的Flash文件：

[![](https://p1.ssl.qhimg.com/t01d69637e653e7a74c.png)](https://p1.ssl.qhimg.com/t01d69637e653e7a74c.png)

接着内存加载第二阶段的Flash文件，第二阶段的Flash文件中则包含Flash 0day漏洞利用代码：

[![](https://p2.ssl.qhimg.com/t011013cbcdb238c916.png)](https://p2.ssl.qhimg.com/t011013cbcdb238c916.png)

### 第三阶段ShellCode

Flash 0day漏洞利用代码执行成功后再向服务器通过POST请求返回第三阶段的ShellCode并执行最后的攻击：

[![](https://p5.ssl.qhimg.com/t01f3845000466c8a86.png)](https://p5.ssl.qhimg.com/t01f3845000466c8a86.png)



## 0day漏洞分析

### 漏洞函数上下文

如下图所示漏洞的关键触发利用代码发生在replace函数中，漏洞触发成功后可以通过交换vector中的两个对象以转换为类型混淆来实现代码执行，函数执行前声明了两个SafeStr_5，SafeStr_7类型的对象实例，并将这两个对象实例作为参数交替传入函数SafeStr_61中，一共256个参数，SafeStr_5，SafeStr_7类型各占128个：

[![](https://p2.ssl.qhimg.com/t01390eebb956990223.png)](https://p2.ssl.qhimg.com/t01390eebb956990223.png)

SafeStr_5类如下所示：

[![](https://p1.ssl.qhimg.com/t01bb4b62b123ad2c53.png)](https://p1.ssl.qhimg.com/t01bb4b62b123ad2c53.png)

SafeStr_7类如下所示：

[![](https://p2.ssl.qhimg.com/t01f1d415beeeef5241.png)](https://p2.ssl.qhimg.com/t01f1d415beeeef5241.png)

Jit代码中生成对应的SafeStr_5类实例：

[![](https://p3.ssl.qhimg.com/t017baea2a4af141aca.png)](https://p3.ssl.qhimg.com/t017baea2a4af141aca.png)

最终进入SafeStr_61前生成的SafeStr_5，SafeStr_7类实例如下所示，其中前两个是全局声明的实例，后两个是replace中声明的实例，之后作为SafeStr_61参数传入：

[![](https://p0.ssl.qhimg.com/t01e93c4042e9ff05d1.png)](https://p0.ssl.qhimg.com/t01e93c4042e9ff05d1.png)

进入SafeStr_61函数前：

[![](https://p1.ssl.qhimg.com/t015dc2c91e441c9d2d.png)](https://p1.ssl.qhimg.com/t015dc2c91e441c9d2d.png)

SafeStr_61函数如下所示，首先创建了一个_SafeStr_6的类实例（用于触发漏洞），及_SafeStr_5，_SafeStr_7类型的vector，之后将参数交叉传入两个vector中：

[![](https://p5.ssl.qhimg.com/t01b68cd88250387349.png)](https://p5.ssl.qhimg.com/t01b68cd88250387349.png)

接着开始vector赋值：

[![](https://p1.ssl.qhimg.com/t015e9ac4de429bfff0.png)](https://p1.ssl.qhimg.com/t015e9ac4de429bfff0.png)

赋值之后如下所示：

[![](https://p1.ssl.qhimg.com/t01fb888ec853d691bc.png)](https://p1.ssl.qhimg.com/t01fb888ec853d691bc.png)

### 漏洞成因

现在来看看用于触发漏洞的_SafeStr_6类实例，AS代码如下：

[![](https://p2.ssl.qhimg.com/t01126885af37f8c62c.png)](https://p2.ssl.qhimg.com/t01126885af37f8c62c.png)

可以看到，由于Flash解析器处理对应的Try-Catch代码块时没有合理处理好异常处理代码的作用范围，解析器误认为不会有代码可以执行到Catch语句内，因此没有对Catch中代码对应的字节码进行检测，而该函数中的li8(123456)操作由于会触发异常并被Catch捕获，这样由于对Catch代码块中的代码缺乏检查，那么代码中的字节码通过setlocal，getlocal操作就可以实现对栈上数据的非法修改，最终将栈上两个对象指针的位置进行的替换，从而转化为类型混淆来实现任意代码执行！

### 漏洞利用

再来看看触发漏洞的代码上下文，其中_SafeStr_6即为上图所示触发漏洞的类实例代码：

[![](https://p2.ssl.qhimg.com/t0111111a9be04fc086.png)](https://p2.ssl.qhimg.com/t0111111a9be04fc086.png)

如下所示可以看到对应_SafeStr_5类型的vector中的一个对象的指针被修改为了_SaftStr的对象指针，其寻址标记为0x1c1=449，即为上图中getlocal操作的变量：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010a77e8b0edc13302.png)

之后将_SafeStr_7类型的vector中的一个对象的指针修改为了_SaftSt_5r的对象指针：

[![](https://p2.ssl.qhimg.com/t01e9261b61e59f6c6b.png)](https://p2.ssl.qhimg.com/t01e9261b61e59f6c6b.png)

接着遍历_SafeStr_5中的每个对象的m_p1成员变量，获取对应修改成_SafeStr_7指针的成员：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t016588c42a00e13afe.png)

由于_SafeStr_5对象被混淆成_SafeStr_7，因此对该混淆的_SafeStr_5对象的操作，实际上作用的是_SafeStr_7的内存空间，此时通过设置_SafeStr_5对象的m_p1变量，即可实现对_SafeStr_7对象对应内存偏移的操作，而该偏移在_SafeStr_7对象中指向了对应的_SafeStr_5对象，此时相当于_SafeStr_7._SafeStr_5.m_p1的操作受_SafeStr_5对象的m_p1对象的控制，从而实现指定地址读写，之后转化为任意代码执行：

[![](https://p5.ssl.qhimg.com/t01f92dcaac4bdb0cc6.png)](https://p5.ssl.qhimg.com/t01f92dcaac4bdb0cc6.png)



## 溯源与关联

### 相似样本

结合该漏洞投递文件（Excel文档）插入Flash ActiveX控件的技巧（复合二进制bin+远程Flash加载），360威胁情报中心通过大数据关联到另外一个使用相同技巧的投递Flash漏洞利用的文档控件文件（MD5：5b92b7f4599f81145080aa5c3152dfd9）：

[![](https://p4.ssl.qhimg.com/t0190f81535a262fa3a.png)](https://p4.ssl.qhimg.com/t0190f81535a262fa3a.png)

[![](https://p1.ssl.qhimg.com/t013b53f6000715fa38.png)](https://p1.ssl.qhimg.com/t013b53f6000715fa38.png)

其内置的用于加载远程Flash漏洞攻击的URL如下：

https://mynewsfeeds.info/docs/P6KMO6/5v1z1p3r1p1o.swf

### 域名分析

该域名在2015年到2016年初用于下载多个SWF Payload文件：

[![](https://p0.ssl.qhimg.com/t015e9cfa28d1fb9a32.png)](https://p0.ssl.qhimg.com/t015e9cfa28d1fb9a32.png)

而该域名mynewsfeeds.info历史曾由marchaopn@gmail.com注册，在Hacking Team 2015年7月的泄露事件后，该域名做了隐私保护：

[![](https://p0.ssl.qhimg.com/t01540676f3a9139d83.png)](https://p0.ssl.qhimg.com/t01540676f3a9139d83.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0118afe334c5e80f08.png)

结合360威胁情报平台，该域名也关联到CVE-2015-5119的漏洞利用样本，该漏洞同样也是Hacking Team泄露事件曝光的Flash 0day漏洞！

[![](https://p5.ssl.qhimg.com/t014492569439dd8e52.png)](https://p5.ssl.qhimg.com/t014492569439dd8e52.png)

### 域名为Hacking Team所属

其中marchaopn@gmail.com邮箱注册的签名证书正是Hacking Team所属：

[![](https://p2.ssl.qhimg.com/t01047d73e3736ab8f5.png)](https://p2.ssl.qhimg.com/t01047d73e3736ab8f5.png)

以及Hacking Team与客户的交流邮件中提到该域名和邮箱的信息：

[![](https://p2.ssl.qhimg.com/t01b5f6eaa9f7612bb4.png)](https://p2.ssl.qhimg.com/t01b5f6eaa9f7612bb4.png)

至此，360威胁情报中心通过本次泄露的0day漏洞利用样本的特殊构造方式找到一个高度相似的样本，而该样本则指向Hacking Team。

自Hacking Team泄露事件以来，其新的相关活动及其开发的间谍木马也被国外安全厂商和资讯网站多次披露，证明其并没有完全销声匿迹。

### 关于Hacking Team

360威胁情报中心结合多方面的关联，列举本次0day攻击事件和历史Hacking Team之间的一些对比：
- Hacking Team长期向多个情报机构或政府部门销售其网络间谍武器
- 在过去Hacking Team泄露资料中表明其对Flash 0day漏洞和利用技术有深厚的基础；而本次0day漏洞中的利用手法实现也是非常通用
- 本次0day漏洞的EXP制作方式和漏洞利用上也与Hacking Team过去的一些利用相似


## 防护建议

360威胁情报中心提醒各单位/企业用户，谨慎打开来源不明的文档，并尽快通过修复及升级地址下载安装最新版Adobe Flash Player，也可以安装360安全卫士/天擎等防病毒软件工具以尽可能降低风险。



## 参考

[1].补丁公告：

[https://helpx.adobe.com/security/products/flash-player/apsb18-19.html](https://helpx.adobe.com/security/products/flash-player/apsb18-19.html)

[2].修复及升级地址：

[https://get.adobe.com/flashplayer/](https://get.adobe.com/flashplayer/)

[3].与Hacking Team相关联的信息

https://www.virustotal.com/#/domain/mynewsfeeds.info

https://www.threatcrowd.org/domain.php?domain=mynewsfeeds.info

https://domainbigdata.com/mynewsfeeds.info

https://github.com/Rafiot/HackedTeamCerts/blob/master/SignCert/xx!_windows_marc_certum_201509.cer

https://www.cybereason.com/blog/hacking-team-hacked-team-leak-unleashes-flame-like-capabilities-into-the-wild

https://wikileaks.org/hackingteam/emails/emailid/15128



## IOC
<td valign="top" width="568">**Excel****文档**</td>
<td valign="top" width="568">c8aaaa517277fb0dbb4bbf724245e663</td>
<td valign="top" width="568">**第一阶段Flash****文件**</td>
<td valign="top" width="568">ee34f466491a5c5cd7423849f32b58f5</td>
<td valign="top" width="568">**样本下载及通信的URL**</td>
<td valign="top" width="568">http://people.dohabayt.com/stab/65f6434672f90eba68b96530172db71a</td>
<td valign="top" width="568">http://people.dohabayt.com/photos/doc/65f6434672f90eba68b96530172db71a</td>
<td valign="top" width="568">http://people.dohabayt.com/download/65f6434672f90eba68b96530172db71a/</td>
<td valign="top" width="568">http://people.dohabayt.com/photos/doc/65f6434672f90eba68b96530172db71a</td>

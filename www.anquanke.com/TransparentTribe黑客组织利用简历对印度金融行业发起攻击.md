> 原文链接: https://www.anquanke.com//post/id/243326 


# TransparentTribe黑客组织利用简历对印度金融行业发起攻击


                                阅读量   
                                **64516**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p3.ssl.qhimg.com/t01bcd5c03a1c6213c4.jpg)](https://p3.ssl.qhimg.com/t01bcd5c03a1c6213c4.jpg)



## 一．背景

TransparentTribe APT组织，又称ProjectM、C-Major，是一个来自巴基斯坦的APT攻击组织，主要攻击手段是通过鱼叉式钓鱼邮件对印度政府、军事、金融等目标发起攻击。该组织的活动最早可以追溯到2012年并在2016年3月首先被proofpoint公司披露。

透过对该黑客组织的长期威胁情报的追踪，我们发现该黑客组织于近期发动了一场针对金融行业的鱼叉式钓鱼邮件攻击，该攻击以金融从业者简历为诱饵，诱骗用户启用宏代码，并将恶意代码嵌入其中。



## 二．攻击活动分析

### <a class="reference-link" name="1.%E6%94%BB%E5%87%BB%E6%B5%81%E7%A8%8B%EF%BC%9A"></a>1.攻击流程：

[![](https://p2.ssl.qhimg.com/t010cd44a57e910c895.png)](https://p2.ssl.qhimg.com/t010cd44a57e910c895.png)

### <a class="reference-link" name="2.%E5%AE%8F%E4%BB%A3%E7%A0%81%E5%88%86%E6%9E%90%EF%BC%9A"></a>2.宏代码分析：

该文档的正文宏代码部分只有一句，在打开宏文档后，会调用模块中waqopfiloLdr里的恶意代码。

[![](https://p2.ssl.qhimg.com/t01a137006919938b1b.png)](https://p2.ssl.qhimg.com/t01a137006919938b1b.png)

首先调用了WaqopfileLdr函数，获取系统的ProgramData的路径，并拼接Dlymrdsa,形成完整路径后，创建该文件夹。

[![](https://p2.ssl.qhimg.com/t01a976d12b2bd994cc.png)](https://p2.ssl.qhimg.com/t01a976d12b2bd994cc.png)

[![](https://p3.ssl.qhimg.com/t018f2536e4ba72d019.png)](https://p3.ssl.qhimg.com/t018f2536e4ba72d019.png)

接着获取操作系统版本，并判断是否为win7

[![](https://p3.ssl.qhimg.com/t01ad0a0e790fadd6c6.png)](https://p3.ssl.qhimg.com/t01ad0a0e790fadd6c6.png)

当系统为win7时，取出TextBox1中的数据，将其中的”w”字符串去除，形成完整的数据。（可以理解为解混淆），最后将解密的数据写入到C:\ProgramData\Dlymrdsa\ravidhtirad.zip当中。

[![](https://p5.ssl.qhimg.com/t0168499afdd9afe1cc.png)](https://p5.ssl.qhimg.com/t0168499afdd9afe1cc.png)

[![](https://p3.ssl.qhimg.com/t017afb42f52d1815d9.png)](https://p3.ssl.qhimg.com/t017afb42f52d1815d9.png)

[![](https://p1.ssl.qhimg.com/t013b0b54f6a4c45b62.png)](https://p1.ssl.qhimg.com/t013b0b54f6a4c45b62.png)

随后判断标准位，该标准位在执行了Win7系统流程后会自动将标准位置为1，则下述代码将不在执行，这里应该是除Win7以为系统执行的逻辑代码，该代码与上述的代码一致，只是将TextBox2的数据释放。

[![](https://p3.ssl.qhimg.com/t014a7a959fa46ca051.png)](https://p3.ssl.qhimg.com/t014a7a959fa46ca051.png)

[![](https://p0.ssl.qhimg.com/t018788e4396fa26004.png)](https://p0.ssl.qhimg.com/t018788e4396fa26004.png)

[![](https://p3.ssl.qhimg.com/t015f3b2f6510a7cccd.png)](https://p3.ssl.qhimg.com/t015f3b2f6510a7cccd.png)

接着调用unwaqopip方法将压缩包内的exe进行解压。

[![](https://p5.ssl.qhimg.com/t0142c3a1a7c839deef.png)](https://p5.ssl.qhimg.com/t0142c3a1a7c839deef.png)

unwaqopip方法内部将使用系统自带的解压工具对压缩包进行解压。(Shell.Application对象的CopyHere方法)

[![](https://p1.ssl.qhimg.com/t01c99ccc49c064b993.png)](https://p1.ssl.qhimg.com/t01c99ccc49c064b993.png)

解压完成后调用Shell函数将解压出来的exe运行起来，并调用WaqopdocLdr方法。

[![](https://p3.ssl.qhimg.com/t017ca28124ba9289d3.png)](https://p3.ssl.qhimg.com/t017ca28124ba9289d3.png)

WaqopdocLdr方法将UserForm2中的文本写入到正文文档当中去。

[![](https://p4.ssl.qhimg.com/t01675bdc42b7a4a917.png)](https://p4.ssl.qhimg.com/t01675bdc42b7a4a917.png)

[![](https://p5.ssl.qhimg.com/t012c09f1ea0a82a139.png)](https://p5.ssl.qhimg.com/t012c09f1ea0a82a139.png)

[![](https://p0.ssl.qhimg.com/t015cbacc0926c942f9.png)](https://p0.ssl.qhimg.com/t015cbacc0926c942f9.png)

该钓鱼内容为简历，可以看出其简历内容主要是金融行业相关，由于该组织的一贯攻击习惯，可以判断出该组织的目标及有可能是金融机构。

[![](https://p1.ssl.qhimg.com/t0180f1027372ce543c.png)](https://p1.ssl.qhimg.com/t0180f1027372ce543c.png)

### <a class="reference-link" name="3.RAT%E5%88%86%E6%9E%90%EF%BC%9A"></a>3.RAT分析：

我们对2个内置的RaT进行了分析，发现是用.net编写的，编写过.net的都知道.net3.5/2.0和4.0是不兼容的，而Win7和XP默认是预装了3.5/2.0，而Win8以上则默认预装的是4.0，就导致了需要进行系统的判断。

[![](https://p5.ssl.qhimg.com/t01cbf11e5ecafc1c73.png)](https://p5.ssl.qhimg.com/t01cbf11e5ecafc1c73.png)

[![](https://p3.ssl.qhimg.com/t015fd0ab23a5856c9b.png)](https://p3.ssl.qhimg.com/t015fd0ab23a5856c9b.png)

经过笔者分析，该Rat2个版本功能是一样的至少语法上有区别，主要是适配.net版本，这里以.net2.0的样本为主来进行分析。<br>
该Rat是.net的窗口程序，通过Form1类创建窗口。

[![](https://p3.ssl.qhimg.com/t019bcc4b2f030e775c.png)](https://p3.ssl.qhimg.com/t019bcc4b2f030e775c.png)

首先调用初始化方式。

[![](https://p5.ssl.qhimg.com/t014a132e7232b03851.png)](https://p5.ssl.qhimg.com/t014a132e7232b03851.png)

设置窗口属性是否显示以及关闭窗口消息相应函数和主消息回调。

[![](https://p4.ssl.qhimg.com/t010810e028ad670dba.png)](https://p4.ssl.qhimg.com/t010810e028ad670dba.png)

### <a class="reference-link" name="3.1%20FormClosing%E5%9B%9E%E8%B0%83%EF%BC%9A"></a>3.1 FormClosing回调：

调用ravidhtiradload_apep方法。

[![](https://p3.ssl.qhimg.com/t01a1d6f7ca79cb23fa.png)](https://p3.ssl.qhimg.com/t01a1d6f7ca79cb23fa.png)

获得Rat的完整运行路径并调用ravidhtiradset_ruwn方法。

[![](https://p2.ssl.qhimg.com/t01c0d1a85bc143429f.png)](https://p2.ssl.qhimg.com/t01c0d1a85bc143429f.png)

向注册表项写入开启自启。

[![](https://p4.ssl.qhimg.com/t0187b0bff368cc541c.png)](https://p4.ssl.qhimg.com/t0187b0bff368cc541c.png)

### <a class="reference-link" name="3.2%20Load%E5%9B%9E%E8%B0%83%EF%BC%9A"></a>3.2 Load回调：

设置窗口相关属性后，调用ravidhtiraddowStart方法。

[![](https://p3.ssl.qhimg.com/t01a87b5706a6cc2dc9.png)](https://p3.ssl.qhimg.com/t01a87b5706a6cc2dc9.png)

使用定时器线程定时调用ravidhtiradlookupCdon方法,延迟时间为31210毫秒，定时器间隔为35210毫秒。

[![](https://p0.ssl.qhimg.com/t0103bf281c4586bf3b.png)](https://p0.ssl.qhimg.com/t0103bf281c4586bf3b.png)

接着调用ravidhtiradIPSeC方法。

[![](https://p3.ssl.qhimg.com/t01eedc17f0788fc3a0.png)](https://p3.ssl.qhimg.com/t01eedc17f0788fc3a0.png)

首先调用ravidhtiradserverIPeD方法获取C&amp;C服务器地址。

[![](https://p3.ssl.qhimg.com/t01a6e62cea6a2da1f2.png)](https://p3.ssl.qhimg.com/t01a6e62cea6a2da1f2.png)

[![](https://p1.ssl.qhimg.com/t019ce50b64af4e8d1f.png)](https://p1.ssl.qhimg.com/t019ce50b64af4e8d1f.png)

值得注意的是ravidhtiraddefaultwP默认是有一个C&amp;C地址，但该地址并未使用，而是被上述的IP地址取代，推测是为了应付一些自动提取IOC的软件或者初级分析人员的干扰选项。

[![](https://p4.ssl.qhimg.com/t01a4b9328f5803c4ca.png)](https://p4.ssl.qhimg.com/t01a4b9328f5803c4ca.png)

然后将会尝试连接到C&amp;C服务器：“151.106.14.125:6818”。

[![](https://p4.ssl.qhimg.com/t011e4d543a0eb5b9d0.png)](https://p4.ssl.qhimg.com/t011e4d543a0eb5b9d0.png)

当发生错误时，会进入异常流程，异常流程会按下述端口重新发起连接。

[![](https://p1.ssl.qhimg.com/t0169b6f6172fcb8337.png)](https://p1.ssl.qhimg.com/t0169b6f6172fcb8337.png)

[![](https://p3.ssl.qhimg.com/t015ead5f5a494739e8.png)](https://p3.ssl.qhimg.com/t015ead5f5a494739e8.png)

并将异常原因发送到http://shareboxs.net/indexer.php，同时附带系统用户名和系统版本。

[![](https://p3.ssl.qhimg.com/t016ce01316a6dc0d3b.png)](https://p3.ssl.qhimg.com/t016ce01316a6dc0d3b.png)

如果成功连接后将调用ravidhtiradseeRse方法进行处理。

[![](https://p2.ssl.qhimg.com/t01a409adbe3cd07250.png)](https://p2.ssl.qhimg.com/t01a409adbe3cd07250.png)

由于笔者分析时，该C&amp;C服务器以关停，故无法获取其返回的命令格式，以及相关数据，但可以通过内置的部分指令以及功能来获取其对应的恶意行为，该Rat的服务端是由Web进行控制的。<br>
可以看到会首先获取服务端返回的数据。

[![](https://p4.ssl.qhimg.com/t01e2ce35f228c4ad67.png)](https://p4.ssl.qhimg.com/t01e2ce35f228c4ad67.png)

然后将数据赋值给&lt;&gt;c__DisplayClasse结构并对其进行拆分/判断。

[![](https://p0.ssl.qhimg.com/t0196fae51f2bbc9a81.png)](https://p0.ssl.qhimg.com/t0196fae51f2bbc9a81.png)

接着就是一个巨型的switch，通过switch进行不同命令的分发，值得注意的是该Rat为了兼容不同版本的服务端使用了多个命令对应相同的一个功能。

[![](https://p5.ssl.qhimg.com/t010ef42aec572219dd.png)](https://p5.ssl.qhimg.com/t010ef42aec572219dd.png)

由于该Rat的功能较多，为避免文章过于冗长下面仅列取部分Rat的功能代码。

ravidhtirad-getavs命令是遍历当前计算机中所有进程相关的信息并将其回传到C&amp;C服务器。

[![](https://p5.ssl.qhimg.com/t01162878595a3ed995.png)](https://p5.ssl.qhimg.com/t01162878595a3ed995.png)

[![](https://p2.ssl.qhimg.com/t01f881917f915d0ecc.png)](https://p2.ssl.qhimg.com/t01f881917f915d0ecc.png)

ravidhtirad-thwumb命令是获取图片缓存信息，并将其回传到C&amp;C服务器。

[![](https://p0.ssl.qhimg.com/t010ec51a7cb8dad3bf.png)](https://p0.ssl.qhimg.com/t010ec51a7cb8dad3bf.png)

[![](https://p1.ssl.qhimg.com/t017eaaf155f4fa47bb.png)](https://p1.ssl.qhimg.com/t017eaaf155f4fa47bb.png)

ravidhtirad-fiwlsz命令是获取指定的文件，并将其回传到C&amp;C服务器。

[![](https://p2.ssl.qhimg.com/t01e01f1c48fb085485.png)](https://p2.ssl.qhimg.com/t01e01f1c48fb085485.png)

[![](https://p3.ssl.qhimg.com/t0178f364f7467e127c.png)](https://p3.ssl.qhimg.com/t0178f364f7467e127c.png)



## 三．攻击活动TTP

[![](https://p4.ssl.qhimg.com/t0187c22678327ddcd0.png)](https://p4.ssl.qhimg.com/t0187c22678327ddcd0.png)



## 四．关联&amp;溯源

对该样本进行关联溯源，分别发现了国内友商2019年的几篇报道，其中公开的核心技术细节与本次活动所用的特马（私有特种木马）相匹配，对其核心C&amp;C地址进行溯源，发现了多个关联的恶意样本，均被标注为该黑客组织。

[![](https://p4.ssl.qhimg.com/t0127bf9bafe44d9080.png)](https://p4.ssl.qhimg.com/t0127bf9bafe44d9080.png)

[![](https://p5.ssl.qhimg.com/t01652e47bd74096ca1.png)](https://p5.ssl.qhimg.com/t01652e47bd74096ca1.png)

该C&amp;C的服务器地址位于法国境内的IDC服务商，根据开源威胁情报可知该地址曾被多个APT组织与黑产团伙利用。

[![](https://p3.ssl.qhimg.com/t01a934d73e4396234c.png)](https://p3.ssl.qhimg.com/t01a934d73e4396234c.png)



## 五．总结

该组织的攻击目标和攻击意图十分明显，且对免杀逃逸技术的迭代并没有进行频繁的更新，但攻击活动却十分频繁，这可能源于印巴冲突的升级，网络战争也摆到了明面进行，如此频繁的攻击活动，但却对逃逸技术迭代止步不前，也许是因为现实冲突导致了网络防备松懈。



## 六．IOC

SHA-256：<br>
(1)dbb9168502e819619e94d9dc211d5f4967d8083ac5f4f67742b926abb04e6676<br>
(2)bbea096ceb3c94454a5b92e5f614f107bd98df0b9d2f7022574256d0614f35c8<br>
(3)8f01ae46434e75207d29bc6de069b67c350120a9880cc8e30fefc19471eaac4a<br>
C&amp;C：<br>
(1)151.106.14.125<br>
(2)shareboxs.net

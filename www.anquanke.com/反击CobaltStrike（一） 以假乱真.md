> 原文链接: https://www.anquanke.com//post/id/252332 


# 反击CobaltStrike（一） 以假乱真


                                阅读量   
                                **23201**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t013697b8080f12556b.jpg)](https://p4.ssl.qhimg.com/t013697b8080f12556b.jpg)



## 0x00 背景

CobaltStrike（简称CS）作为一款渗透测试神器，采用C/S架构，可进行分布式团队协作。CS集成了端口转发、服务扫描、自动化溢出、多模式端口监听、Windows exe与dll 木马生、Java 木马生成、Office 宏病毒生成、木马捆绑等强大功能，深受广大红队同学的喜爱。为了规避侦测，红队往往会对CS采用一些隐匿手段，常见方式有云函数和CDN等。这些隐匿手段隐匿了CS的真实IP，诸如DDoS之类的流量无法穿透CDN到达CS，常规的攻击方式难以对CS服务器形成有效干扰和打击。只能止步于此了吗？有没有反击CS的奇技淫巧？答案当然是肯定的！接下来带各位看官体验一种批量伪造肉鸡来戏耍CS的新方法，希望各位蓝队同学引（付）以（诸）为（实）戒（践）。

[![](https://p1.ssl.qhimg.com/t013dfbb3f302acb67c.gif)](https://p1.ssl.qhimg.com/t013dfbb3f302acb67c.gif)



## 0x01 CS上线流量特征分析

首先，我们先研究下CS上线的流量有无特征。图1使用Wireshark分析HTTP型Beacon的上线包。

[![](https://p3.ssl.qhimg.com/t010c554042013d5152.png)](https://p3.ssl.qhimg.com/t010c554042013d5152.png)

图1

肉眼来看，上线包的敏感信息隐藏到了Cookie中，特征非常明显。通过进一步分析，我们发现上线包的请求Cookie值是受控主机元数据经过非对称加密后的密文，CS服务器接收到Cookie值后进行解密从而获取到受控主机信息。受控主机元数据包含了若干敏感信息，如图2所示：

[![](https://p3.ssl.qhimg.com/t014e8344caee09fdb2.png)](https://p3.ssl.qhimg.com/t014e8344caee09fdb2.png)

图2

此处划重点，HTTP型Beacon 上线包的核心在于Cookie，而Cookie是对受控主机元数据的非对称加密的密文。



## 0x02 HTTP Beacon重放实验

由于HTTP属于明文传输协议，HTTP型Beacon的上线过程存在中间人重放的可能。

我们做了一个简单的测试，验证了这种可能性（此处迫于运营小姐姐压力，稍微有凑字数嫌疑）。

首先抓取测试环境中的HTTP Beacon上线请求，使用Python脚本（如：图3）进行重放（注意：Header头信息不能错误，CS Server对Header头检查非常严格）。

[![](https://p4.ssl.qhimg.com/t01899a616477dfd2e9.png)](https://p4.ssl.qhimg.com/t01899a616477dfd2e9.png)

图3

结果显示，重放Response符合我们的预期，CS Server成功响应了我们的请求。（如：图4）

[![](https://p0.ssl.qhimg.com/t01f74935811fe441b7.png)](https://p0.ssl.qhimg.com/t01f74935811fe441b7.png)

图4

此外，红队同学在使用CS时候会自定义Malleable C2 Profile修改默认流量特征，但是这个对中间人重放没有影响。

新的问题产生了。

中间人重放的方法，只能伪造已经上线的主机，不能伪造新的受控主机。

这句话翻译过来就是，没啥鸟用。

好了，字数凑够了。书接上回，言归正传。

现在聚焦最迫切的问题：有没有办法伪造全新的受控主机呢？

答案当然是肯定的。



## 0x03 新主机伪造

我们先看一个效果图（如：图5）。

[![](https://p3.ssl.qhimg.com/t012a443765f9bd306c.png)](https://p3.ssl.qhimg.com/t012a443765f9bd306c.png)

图5

短时间内大量主机上线。想想1分钟上线了千八百个主机，红队同学是不是有点慌？这是如何做到的呢？

我们以Stager型Beacon为例，按照KillChain模型从攻击者角度回顾下CS上线流程（如：图6）。

[![](https://p4.ssl.qhimg.com/t015e8d85ed17bad5ca.png)](https://p4.ssl.qhimg.com/t015e8d85ed17bad5ca.png)

图6

攻击者利用CS Server生成新的Beacon监听（包括一对非对称公私钥）并生成Stager；

攻击者投递Stager到受控主机；

受控主机在Exploit阶段执行小巧的Stager；

受控主机根据Stager Url请求特征向Beacon Staging Server下载体积较大更复杂的Stage到本地，Beacon Staging Server会校验Url的合法性；

Stage解密并解析Beacon配置信息（比如公钥PublicKey、C2 Server信息）；

Stage通过公钥PublicKey加密主机的元数据并发送至C2 Server；

C2 Server用私钥解密数据获取主机元数据。

从上述流程中，我们能Get到2个核心点：

Stager Url校验算法

Beacon配置的解密算法

与CS Server合法通信的问题等价转换为获取Stager Url和Beacon解密问题，即：

CS/C2 Server合法通信 = （Stager Url校验算法，Beacon解密算法）

只要拿到了（Stager Url校验算法，Beacon解密算法），相当于我们掌握了与CS/C2 Server合法通信的凭据。我们分别对上述2个核心点进行分析。



## 0x04 Stager Url校验算法

Stager Url校验算法在公开的NSE脚本中可以找到，关键函数包括：checksum8、MSFURI、isStager。

其中，MSFURI函数从大小写字母+数字的字符数组中随机指定长度的字符序列并调用checksum8函数计算字符序列的ASCII和与256的模是否等于固定值（32位Stage与64位Stage分别使用92、93作为固定值），如果相等返回字符序列，否则继续直至找到符合条件的字符序列。MSFURI（如：图7）、checksum8（如：图8）、isStager（如：图9）函数的定义：

[![](https://p4.ssl.qhimg.com/t01cbdf5b5d617738af.png)](https://p4.ssl.qhimg.com/t01cbdf5b5d617738af.png)

图7

[![](https://p1.ssl.qhimg.com/t01b60ca730f13269fd.png)](https://p1.ssl.qhimg.com/t01b60ca730f13269fd.png)

图8

[![](https://p5.ssl.qhimg.com/t016db50da9e63d64b0.png)](https://p5.ssl.qhimg.com/t016db50da9e63d64b0.png)

图9

如果找到符合条件的字符序列，则作为Stager Url向Beacon Staging Server发送下载请求。Beacon Staging Server在_serve函数中校验Url的合法性，如：图10。

[![](https://p3.ssl.qhimg.com/t014305a0a95bf2f0ba.png)](https://p3.ssl.qhimg.com/t014305a0a95bf2f0ba.png)

图10

至此，我们获取到了Stager Url的校验算法，手动下载Stager。下载效果如图11下：

[![](https://p5.ssl.qhimg.com/t016bff403030641227.png)](https://p5.ssl.qhimg.com/t016bff403030641227.png)

图11

很好！已经成功一半了。接下来，我们再来研究Beacon配置的解密算法。

[![](https://p4.ssl.qhimg.com/t01c4186e26c21350b7.gif)](https://p4.ssl.qhimg.com/t01c4186e26c21350b7.gif)



## 0x05 Beacon配置解密算法

感谢前人栽树！

之前已经有人发布了Beacon配置的解密算法，比如JPCERT的Volatility插件cobaltstrikescan（https://github.com/jpcertcc/aa-tools/blob/master/cobaltstrikescan.py）、美国SentinelOne安全公司开源的CobaltStrikeParser工具（https://github.com/Sentinel-One/CobaltStrikeParser）等。

具体的解密算法此处不再赘述，感兴趣的同学可参考上述的开源工具。解密结果如图12所示：

[![](https://p4.ssl.qhimg.com/t01477c83db32f5eb03.png)](https://p4.ssl.qhimg.com/t01477c83db32f5eb03.png)

图12

从解密的配置中可以看到PublicKey和C2 Server地址。

OK！2个算法我们都已经搞定，接下来就该反击CS了！



## 0x06 反击！

万事俱备，只欠东风！

想象以下场景：蓝队同学防守时获取到了一个CS的上线地址。

首先，构造Stager Url下载Stage，如果在抓到CS上线地址的同时抓到了Stage，此步可跳过。

然后，解析Stager Beacon的配置文件，得到了PublicKey公钥与C2 Server地址。

最后，构造虚假主机元数据，加密发送至C2 Server。

Github上开源的CobaltSpam（[https://github.com/hariomenkel/CobaltSpam）已实现此功能，但CobaltSpam上线的主机信息都是随机生成，很容易被识破。因此，需要将主机信息伪造的更加准确，提高混淆度。](https://github.com/hariomenkel/CobaltSpam%EF%BC%89%E5%B7%B2%E5%AE%9E%E7%8E%B0%E6%AD%A4%E5%8A%9F%E8%83%BD%EF%BC%8C%E4%BD%86CobaltSpam%E4%B8%8A%E7%BA%BF%E7%9A%84%E4%B8%BB%E6%9C%BA%E4%BF%A1%E6%81%AF%E9%83%BD%E6%98%AF%E9%9A%8F%E6%9C%BA%E7%94%9F%E6%88%90%EF%BC%8C%E5%BE%88%E5%AE%B9%E6%98%93%E8%A2%AB%E8%AF%86%E7%A0%B4%E3%80%82%E5%9B%A0%E6%AD%A4%EF%BC%8C%E9%9C%80%E8%A6%81%E5%B0%86%E4%B8%BB%E6%9C%BA%E4%BF%A1%E6%81%AF%E4%BC%AA%E9%80%A0%E7%9A%84%E6%9B%B4%E5%8A%A0%E5%87%86%E7%A1%AE%EF%BC%8C%E6%8F%90%E9%AB%98%E6%B7%B7%E6%B7%86%E5%BA%A6%E3%80%82)

最终，通过修改CobaltSpam代码，添加自定义的更加精准的主机信息，达到了我们想要的效果，如：图13。

[![](https://p3.ssl.qhimg.com/t01a2f24d14a82d53b4.png)](https://p3.ssl.qhimg.com/t01a2f24d14a82d53b4.png)

图13

最终效果见下图（图14）！！！

[![](https://p1.ssl.qhimg.com/t01c286463f1cb11e26.png)](https://p1.ssl.qhimg.com/t01c286463f1cb11e26.png)

图14



## 0x07 结语

通过这种以假乱真的方法，蓝队同学可很好的混淆红队同学的视线，以此来反制攻击者。

对于低级的攻击者而言，目前不能够很好的防御这种攻击手段。

同样，上面提及的2种算法可用于Beacon Staging Server和C2 Server的挖掘。

目前，防御上述反制的方法，可通过修改CS代码上述2种算法的逻辑，阻止虚假主机上线和C2挖掘。

在HVV过程中，如果发现红队的CS木马样本或者CS服务器，我们可以用上述方法来混淆红队同学的视线、拖延他们的时间，让红队同学陷入怀疑人生的地步。



## 参考链接：

[360 浅析CobaltStrike Beacon Staging Server扫描](https://mp.weixin.qq.com/s?__biz=Mzk0NzE4MDE2NA==&amp;mid=2247483756&amp;idx=1&amp;sn=4e48f8f4b724b5dc723c7cec04f5a34e&amp;scene=21#wechat_redirect)

[stager解密脚本](https://blog.didierstevens.com/2021/06/15/update-1768-py-version-0-0-7/)

[CS beacon通信分析](https://wbglil.gitbook.io/cobalt-strike/cobalt-strike-yuan-li-jie-shao/cs-mu-biao-shang-xian-guo-cheng)

[CobaltSpam](https://github.com/hariomenkel/CobaltSpam/)

[HarioMenkel](https://twitter.com/HarioMenkel)

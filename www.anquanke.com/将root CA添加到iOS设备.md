> 原文链接: https://www.anquanke.com//post/id/83969 


# 将root CA添加到iOS设备


                                阅读量   
                                **93031**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://www.sensepost.com/blog/2016/too-easy-adding-root-cas-to-ios-devices/](https://www.sensepost.com/blog/2016/too-easy-adding-root-cas-to-ios-devices/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t016538ce44845f2375.jpg)](https://p5.ssl.qhimg.com/t016538ce44845f2375.jpg)

关于最近约翰•霍普金斯团队遇到的iMessage加密错误,有几个人指出,这个时候就需要添加一个root CA来使它正常运作。然而获得一个全球性root CA的私有密钥是很困难的,让一台设备信任一个恶意的root CA看上去也很难办到,但实际上不然。(在文章尾部的注意事项中有一个简短的技术说明。)

在2014 年的Defcon talk上,我们发布了mana工具包,并指出在Android和iOS设备上安装是root CA是相当容易的,甚至都不需要进行攻击。而在两年后,iOS的世界也没有太大的改变,只是多了一个不清不楚的提示。

简单的方法

想要诱导用户在iOS设备上安装恶意root CA,你需要做的只是通过HTTP提供一个自签名证书 (它必须是自签名的,否则就不会作为root CA进行安装)。你只需要提供这个文件,甚至它不必是正确的mime类型。我认为在captive portal检查中,这是最容易做到的.当设备首次连接到一个无线网络时, 用户界面会弹出一个窗口,为了吸引用户上钩,可以将窗口命名为“免费无线网络自动配置”。如果用户没有通过安装,那么步骤是这样的:

[![](https://p4.ssl.qhimg.com/t011068c0ac02b4ca4e.png)](https://p4.ssl.qhimg.com/t011068c0ac02b4ca4e.png)

1.提示安装自签名恶意证书。红色的“未经验证”字样是非技术用户能看出来的最危险的标识。

[![](https://p2.ssl.qhimg.com/t0167f34251c52c60f6.png)](https://p2.ssl.qhimg.com/t0167f34251c52c60f6.png)

1.1点击“更多细节”后你会看到的画面

[![](https://p1.ssl.qhimg.com/t019489443ac1554a7b.png)](https://p1.ssl.qhimg.com/t019489443ac1554a7b.png)

2.将恶意证书添加到您的信任证书中时,你会收到新的警告。你会注意到,在面对普通用户的时候,它不会解释为什么这样做是不好的,而是会说 “这将允许别人拦截和修改你的加密通信” 。

即使是技术用户,也没法弄清楚这是不是会作为一个新的可信root进行添加。

我们也会看到一个警告,提醒我们概要文件是未经证实的。

[![](https://p2.ssl.qhimg.com/t01d278f4705f64ef4d.png)](https://p2.ssl.qhimg.com/t01d278f4705f64ef4d.png)

3.第二个“安装”提示。如果用户启用了密码或口令,他们会在此之前收到提示。

[![](https://p4.ssl.qhimg.com/t019f02eaac4b04a883.png)](https://p4.ssl.qhimg.com/t019f02eaac4b04a883.png)

4.现在证书已经安装。

对于用户来说,这只是简单的三个步骤,除了刚才那个“未经验证”的提示之外,用户根本不会意识到已经发生了一些糟糕的事情。在这种情况下,加密的MitM攻击是可行的,我们需要做的只是提供一个证书文件。

更好的方法

但是,让我们再多进行一步,看看是否可以去掉红色的“未经验证”警告,这就不仅仅是需要添加一个root CA了。

首先,我们来看一个用苹果iPhone配置器2或更老的配置通用程序编辑出来的简单配置概要文件。它们都能生成一个简单的plist文件。在这个配置中,我同样添加了自签名证书,并将配置导出为.mobileprofile文件,并确保它未签名和未加密。接下来,我使用一个有效的签署文件代码对证书进行签名。为了显示配置文件可以做一些其他的事情,我添加了一个隐藏的网络设备,设备会对其进行探索 (还会收到mana的回复)。最后,我们更新captive portal来为.mobileprofile文件——而不是证书进行服务。这样做,不需要华丽的标题和mime类型。这就是用户将会看到的页面:



[![](https://p4.ssl.qhimg.com/t019ef3d31cb45fe118.png)](https://p4.ssl.qhimg.com/t019ef3d31cb45fe118.png)

 1.正在连接时用户收到的提示。红色的“未经验证”警告现在被替换成了一个绿色的“已验证”提示,这是因为配置文件已经被签署了,尽管它包含了恶意的、未经证实的root CA。我们也可以添加一些解释性的文字来让用户感觉更舒适。

我已经修改了签名证书的详细信息,因为我不希望别人取消它。

[![](https://p1.ssl.qhimg.com/t011e6c22618d8bb567.png)](https://p1.ssl.qhimg.com/t011e6c22618d8bb567.png)

1.1点击“更多细节”后你会看到的界面。你会注意到wifi网络都在这里。

[![](https://p0.ssl.qhimg.com/t0102321f4dd99f6565.png)](https://p0.ssl.qhimg.com/t0102321f4dd99f6565.png)

2.这是和之前一样的警告,提示证书将被添加到你信任的root中,但“这个概要文件未经验证”的警告已经不见了。对于非技术用户来说,这听上去就没什么可怕的了。甚至技术用户也可能被愚弄,因为它没有提到会作为一个可信root CA进行添加。

[![](https://p0.ssl.qhimg.com/t010b4dd66148594059.png)](https://p0.ssl.qhimg.com/t010b4dd66148594059.png)

3.第二个安装提示。和之前一样,如果你有密码,系统在此之前会提示你输入。

[![](https://p2.ssl.qhimg.com/t019ef3d31cb45fe118.png)](https://p2.ssl.qhimg.com/t019ef3d31cb45fe118.png)

4.这个概要文件已经安装完毕,你可以开始进行MitM攻击了。

现在,一个恶意的概要文件已经安装好了。利用这个配置概要文件,你可以对一台iOS设备的几乎任何一个方面进行配置,甚至建立一个远程MDM 服务器来赶走之后会出现的新的概要文件,并做一些准备,防止被用户删除。当然,配置得越多,额外的警告也就越多。

结论

我希望这已经足够证明,在iOS设备上安装一个恶意的root CA是很容易的,这样的话,发动iMessage和其他此类攻击也并非想象中那么困难。尤其是在配置概要文件的例子中,攻击者的“成本”相当低。

此外,我真心希望苹果能用红色显眼字体向用户解释清楚选项的含义是什么,并且推荐一个安全的默认选择。例如,在面向Android设备时,谷歌推出了一个持久的警告,通知用户他们的通讯可能会被截获。当然, 这些警告并不会阻止所有的用户,但手机操作系统也需要跟上浏览器的步伐,向用户推荐一个“默认”的安全选择,而不是任由用户自己进行选择。

针对iMessage缺陷的说明

苹果用来修复iMessage缺陷的方法是,用一些证书挡住iMessage请求。根据约翰霍普金斯的论文,这在2015年12月已经完成。

通过迫使一个特定的信任链或使用特定证书投入使用,MitM证书有效地挡住了iMessage流量中的MitM攻击。我们的恶意证书不是信任链的一部分,我们签署的证书也不会与特定的证书进行匹配。这就是为什么Twitter和Facebook这类应用不容易受到MitM攻击。

然而,老的iOS设备(pre-9)仍易受到这种攻击。因此,人们称这种攻击需要一个root CA的私有密钥是正确的,但是前提是要在iOS9设备上。针对iMessage的攻击比任何一个root CA都要困难得多,因为你需要访问一个特定的、内置的root CA的私有密钥。总之,上述技术无法让你在新一代的手机执行针对imessage的JHU攻击。

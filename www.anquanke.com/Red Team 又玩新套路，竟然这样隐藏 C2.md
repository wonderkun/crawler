> 原文链接: https://www.anquanke.com//post/id/239180 


# Red Team 又玩新套路，竟然这样隐藏 C2


                                阅读量   
                                **215077**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01a530007a1a084424.jpg)](https://p1.ssl.qhimg.com/t01a530007a1a084424.jpg)



## / 背景 /

平静的一天，吉良吉影，哦不，微步情报局样本组突然收到这样一个样本。

[![](https://p1.ssl.qhimg.com/t0193623019ef8db8c0.png)](https://p1.ssl.qhimg.com/t0193623019ef8db8c0.png)

连接域名是 #######cs.com 相关子域名。

[![](https://p5.ssl.qhimg.com/t019ab11dfd640eb18d.png)](https://p5.ssl.qhimg.com/t019ab11dfd640eb18d.png)

乍一看，域名都是白的，应该没什么问题。

我定睛细瞧，最终确认，这是大名鼎鼎的 Cobalt Strike 木马（以下简称为 CS 马）。

仔细搜索，发现不简单。

[![](https://p1.ssl.qhimg.com/t0146924d7fcb03503e.png)](https://p1.ssl.qhimg.com/t0146924d7fcb03503e.png)

推测应该是最近非常流行的利用国内某 B 公有云云函数隐藏攻击资产的方法。

小样本不讲武德，竟然欺负一个注册了快5年的白域名，啪一下，很快啊~

[![](https://p1.ssl.qhimg.com/t01855277465fb2ff51.png)](https://p1.ssl.qhimg.com/t01855277465fb2ff51.png)

我们花了一个周末，弄清了云函数的来龙去脉。

## / 总体分析 /

这个方法是最近除了“域前置”以外，另外一个 RT 特别喜欢的隐藏攻击资产的方法。可能是国内某 C 公有云平台最近修复了其云 IP 可以绕过对添加的 CDN 加速域名所有权的验证，导致现存的一些域前置域名成了“绝版货”，其云域前置攻击变得成本很高。而国内某 B 公有云云函数转发这种方式一方面免费，且部署成本较低，成为了一种新的选择。

总体攻击流程如下图所示：

[![](https://p3.ssl.qhimg.com/t01177b352a36aa1489.png)](https://p3.ssl.qhimg.com/t01177b352a36aa1489.png)

主要思路为，以往是受害主机运行木马后，通过 HTTP 的 GET 和 POST 方法去请求攻击者的服务器，从而实现持续控制。

而国内某 B 云转发的方法，其实跟我们平时用的 VPN 差不多，通过构造国内某 B 云函数，让函数实现转发请求流量的功能。

最后实现的效果就是在攻击机和受害机之间架设一层”中转站”，受害机只能看到自己的流量发送给了国内某 B 公有云，从而实现以下目的：
1. 让受害机只能看到和高可信域名的通讯，放松警惕性。
1. 隐藏 CS 服务器的 IP，从而实现攻击资产的隐蔽。
1. 云服务器使连接更稳定，部分网络状况不好的服务器主机可以避免因为网络问题导致受害机下线。
这其实与之前的域前置攻击手法类似。

之前的域前置攻击手法为：

[![](https://p0.ssl.qhimg.com/t013ba3fb7ee5f6277a.png)](https://p0.ssl.qhimg.com/t013ba3fb7ee5f6277a.png)

都是通过一个中间件，将自己的流量转发，从而隐藏攻击资产，通过高可信目的地址迷惑用户。

只能说 Red Team 的手法真的是越来越多了，防不胜防。

[![](https://p5.ssl.qhimg.com/t01c55967f31892c6b7.png)](https://p5.ssl.qhimg.com/t01c55967f31892c6b7.png)

图片源自网络

基于此的应对方法其实很简单：
<li class="ql-align-justify" data-list="bullet">
**上策**：监测疑似 CS 马的攻击流量，例如请求 /pixel，/__utm.gif，/ga.js 等类似 URL 的流量进行重点监测，或者使用微步在线情报识别 CS 马的外联地址，我们已经收集了较多的某 B 云云函数地址情报以及相关的 CS 服务器地址。（要恰饭的嘛）</li>
<li class="ql-align-justify" data-list="bullet">
**中策**：确认自己资产中是否有某 B 云函数的正常业务，若无的话直接封禁 *.apigw.#######cs.com 等子域名。</li>
<li class="ql-align-justify" data-list="bullet">
**下策**：直接断网，只开放静态网页服务（bushi）</li>
[![](https://p2.ssl.qhimg.com/t01d9450ad7f47f0545.png)](https://p2.ssl.qhimg.com/t01d9450ad7f47f0545.png)

## / 防守视角攻击复现 /

在发现此类攻击之后，我们寻找了相关的攻击细节。

本文部分细节参考了 「风起 」的文章《红队攻防基础建设—— C2 IP 隐匿技术》， 感谢他~

有人说文章已经写过了如何利用，你为啥还要再写一遍?

主要是文章是 RT 同学写出来的，正所谓“绝知此事要躬行”，很多事实只有验证一遍才能证实方法的存在，同时以 BT 的身份重新复现攻击手法，也可以有一些之后怎么应对的思路。

首先，要去某 B 公有云官网申请一个个人账号，同时要通过个人认证，用微信扫一下就好了， 不过微信要绑定自己的银行卡且实名。这个安全措施让我不禁想到，一旦拿到攻击者的云函数，拿到账号，理论上是应该可以拿到对应绑定的姓名手机号和身份证号的。

如下图，我就已经完成认证了，认证状态是“已认证”。

[![](https://p5.ssl.qhimg.com/t01aa9652db74540ce4.png)](https://p5.ssl.qhimg.com/t01aa9652db74540ce4.png)

然后打开云函数模块。

[![](https://p2.ssl.qhimg.com/t01052fca696513cd14.png)](https://p2.ssl.qhimg.com/t01052fca696513cd14.png)

初次访问需要授权。

[![](https://p4.ssl.qhimg.com/t0173ad71e75aa2b577.png)](https://p4.ssl.qhimg.com/t0173ad71e75aa2b577.png)

点击“同意授权”，出卖自己的灵魂。（主要是不同意也不给你用）

[![](https://p2.ssl.qhimg.com/t01f8916bb14ec7de12.png)](https://p2.ssl.qhimg.com/t01f8916bb14ec7de12.png)

然后我们就可以开始创建云函数了。

首先，我们选择自定义创建的方式，函数名称可以自己随便起一个，注意函数名不要起个人 ID 或者是独一无二的名字，因为之后我们可以通过访问云 API 抓包获取函数名称的，如果是个人 ID，RT 的小同学小心我们溯源哦~

[![](https://p2.ssl.qhimg.com/t01831102f0c8e4f436.png)](https://p2.ssl.qhimg.com/t01831102f0c8e4f436.png)

因为笔者比较喜欢 Python，所以运行环境选择了 Python，当然也可以选别的语言。正所谓 Python 有 Python 的好，其他语言有其他语言的坏嘛。

创建成功之后，需要先点进“触发管理-&gt;创建触发器”。

[![](https://p3.ssl.qhimg.com/t0111115567301589e8.png)](https://p3.ssl.qhimg.com/t0111115567301589e8.png)

这时候可能就有人问了，为啥要创建触发器呢？

简单解释就是，没有触发器，你的函数只能自己访问，创建触发器之后，国内某 B 公有云会给你一个公网的 API 地址，且每次访问这个地址都可以触发一次函数。

在创建触发器的时候，仍然需要赋予云函数触发器的权限，如下图所示（红框部分）。

[![](https://p3.ssl.qhimg.com/t01c25612690f12e4aa.png)](https://p3.ssl.qhimg.com/t01c25612690f12e4aa.png)

[![](https://p4.ssl.qhimg.com/t017793860639757110.png)](https://p4.ssl.qhimg.com/t017793860639757110.png)

赋予成功之后，立马就收到了通知。

[![](https://p3.ssl.qhimg.com/t01afc0e419ceb4b2db.png)](https://p3.ssl.qhimg.com/t01afc0e419ceb4b2db.png)

下面开始编写函数。

我们先简单写一个函数，直接返回页面。

PS：某 B 公有云云函数有自己的一套规则，一套特别麻烦的标准和规则，我建议大家不要纠结细节，直接复制我的代码就好了。

下面这个图就是， 先简单写一个返回测试数据的函数， 返回格式需要如下图这种非常严格的字段。

[![](https://p3.ssl.qhimg.com/t0100f14e87d3849d50.png)](https://p3.ssl.qhimg.com/t0100f14e87d3849d50.png)

访问我们的云函数地址，发现可以顺利返回数据。（当然，我被函数搞了几十次的失败就不表了~）

[![](https://p4.ssl.qhimg.com/t01ea4b638e20a01abd.png)](https://p4.ssl.qhimg.com/t01ea4b638e20a01abd.png)

关于请求的所有字段，比如 headers，body，status code 这些内容都集成在 Event 这个输入字段中了，详细解释的地址在下面：

Event 字段说明地址 ：https://cloud.########.com/document/product/583/12513#apiStructure

我建议大家还是不要了解了，如果以后不需要搞这种基于云的服务开发，完全没有必要重新学一遍。

[![](https://p1.ssl.qhimg.com/t0162c882cace7fb77b.jpg)](https://p1.ssl.qhimg.com/t0162c882cace7fb77b.jpg)

所以大家可以看到，要是我在里面写一个请求方法，请求一个固定地址，会发生什么呢，会不会云函数自动代替我完成对目标地址的请求，就像 VPN 或者某科学上网工具一样?

所以，我动手试了一下。

把请求地址写成了我们的官网：

[![](https://p5.ssl.qhimg.com/t0186427d9dbaeafd5f.png)](https://p5.ssl.qhimg.com/t0186427d9dbaeafd5f.png)

可以看到， 访问之后果然是代替我们请求了我们公司官网的地址。

[![](https://p0.ssl.qhimg.com/t01a214b78568a03f5f.png)](https://p0.ssl.qhimg.com/t01a214b78568a03f5f.png)

到这里就是正式编写我们的函数了。

我们要实现一个效果就是收集请求端的数据包，收集请求包请求数据，然后把请求包原样发送给我们的 CS 服务器，最后收集 CS 服务器的返回包返回给请求方。

具体的代码如下：

[![](https://p2.ssl.qhimg.com/t01ec036d5c45f0cef1.png)](https://p2.ssl.qhimg.com/t01ec036d5c45f0cef1.png)

后面的代码参考了 「风起 」的文章中把 body 中标识字节的 b’’ 字段舍弃的方法。

注意这里是某 B 公有云云函数的规定，必须要返回一个带 “sBase64Encoded，statusCode， headers，body 字段的一个字典。

[![](https://p3.ssl.qhimg.com/t01d94aed47860d51d1.png)](https://p3.ssl.qhimg.com/t01d94aed47860d51d1.png)

另外一个坑是，某 B 公有云云函数的超时时间的问题。

当我们配置好之后，访问可能会遇到下图所示报错：

[![](https://p4.ssl.qhimg.com/t01d330a5b48dd9c1d2.png)](https://p4.ssl.qhimg.com/t01d330a5b48dd9c1d2.png)

是因为 CS 马在运行后会先下载一个 200K+ 的配置文件（这个研究过 CS 马的童靴应该很了解），而我们的云函数在下载这么大的文件的时候会超时。

所以这个问题很难发现，直接让笔者整个周末都在研究这个问题。

顺便吐槽下某 B 公有云的错误返回，实在是太概括了，根据返回根本定位不到问题在哪里，要自己一行一行的 re 代码…… 快哭了。

这里超时时间直接给他拉满，设成 100s。

[![](https://p5.ssl.qhimg.com/t01686bcf3ca137fb2a.png)](https://p5.ssl.qhimg.com/t01686bcf3ca137fb2a.png)

函数配置好之后，我们就可以用我们的地址上线啦。期待，呲溜~

[![](https://p5.ssl.qhimg.com/t0170a51719322120b8.png)](https://p5.ssl.qhimg.com/t0170a51719322120b8.png)

虚拟机运行：

[![](https://p3.ssl.qhimg.com/t011b837059bec5400c.png)](https://p3.ssl.qhimg.com/t011b837059bec5400c.png)

虚拟机抓包发现请求包已经发出去了。

[![](https://p5.ssl.qhimg.com/t01aae0d7de848c12d1.png)](https://p5.ssl.qhimg.com/t01aae0d7de848c12d1.png)

仔细看一下，确实发出去的包的地址确实是某 B 公有云主机的地址。

[![](https://p1.ssl.qhimg.com/t010bebf86e09df2334.png)](https://p1.ssl.qhimg.com/t010bebf86e09df2334.png)

没问题，CS 服务器检测到我的虚拟机上线了。

[![](https://p3.ssl.qhimg.com/t0163bc77900b55b2c9.png)](https://p3.ssl.qhimg.com/t0163bc77900b55b2c9.png)

最后，感谢一下 「风起 」的文章。虽然域前置，某 B 公有云云函数隐藏这些攻击方法我们都已经掌握了，但是参照仍然让我们少走了一些弯路（虽然有的坑也没避掉）。

通过域前置，某 B 公有云云函数隐藏等这些虽然给溯源增加了一层难度，但也不是完全不可能，如果得到有关方面的协助还是有办法找到攻击机的。

比如，某 C 公有云云的域前置，只要找到上线时连接的 Host 在某 C 云内部的 DNS 对应的 IP，就可以拿到其对应的攻击 IP了。

某 B 公有云云函数这种方法呢，就更简单了，反正每个触发器对应的 API 地址就一个，发现了封了就行了，自己也没法改，因为 CS 马的上线地址填的这个。另外在请求 API 截止的时候会函数名，如果起的有特色一点，也不是完全没有溯源的可能。

攻防双方永远在博弈中共同进步，最近爆出来的域前置攻击，某 B 公有云云函数转发， 还有我们最新发现的微软子域名劫持， 其实都是 RT 在应对各种防守工具想出来的比较好的方法，我们也在不断提升对这种攻击的检测的能力。

攻防双方应该像两条藤蔓一样互相攀爬着向上。从攻击方最开始不停地开扫描器扫描，企业封堵 IP；到攻击方发送无数个钓鱼邮件，企业进行样本分析溯源；最终转变为更高手段的攻防博弈。攻防水平不断提升，双方过招之后应该是直呼“有点东西”，而不是“几天不见，怎么这么拉了”。

如果大家看完能有些收获，我们整整一个周末研究这个方法就没有浪费。

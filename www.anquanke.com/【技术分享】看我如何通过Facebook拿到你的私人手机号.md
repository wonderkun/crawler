
# 【技术分享】看我如何通过Facebook拿到你的私人手机号


                                阅读量   
                                **319470**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：hackernoon.com
                                <br>原文地址：[https://hackernoon.com/how-i-got-your-phone-number-through-facebook-223b769cccf1#.wyrbj0u5h](https://hackernoon.com/how-i-got-your-phone-number-through-facebook-223b769cccf1#.wyrbj0u5h)

译文仅供参考，具体内容表达以及含义原文为准

[![](./img/85555/t01f2b0d3171e63c154.png)](./img/85555/t01f2b0d3171e63c154.png)



翻译：[WisFree](http://bobao.360.cn/member/contribute?uid=2606963099)

预估稿费：200RMB

投稿方式：发送邮件至[linwei#360.cn](mailto:linwei@360.cn)，或登陆[网页版](http://bobao.360.cn/contribute/index)在线投稿



**前言**

上个月，我发现通过Facebook来获取他人的私人电话号码其实非常的简单，在研究的过程中，我发现了一些比利时明星和政治家的电话号码，虽然我所使用的这种方法似乎只能在类似比利时这样的小型国家（1120万人左右）奏效，但这也表明，这种简单且高效的攻击方法仍然会让大量用户的隐私信息发生泄漏。

注：如果你没时间阅读整篇文章的话，你也可以直接阅读本文结尾“常见问题解答”那一块内容，那里也许有你想要的东西。

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a8f90dfd5476e501.png)

<br>

**验证我所发现的电话号码**

但是当我将我的研究发现告知了Facebook安全团队的技术人员之后，他们给我的答复不免有些让人大跌眼镜。

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e35703a48f4611ce.png)

根据Facebook的回复，他们并不认为这是一个安全问题

当“who can look me up by phone（通过手机号码查找到我）”这个选项被设置为“公开”时，你的电话号码就会被Facebook公开。这里还有几个问题：首先，这个选项在默认情况下为“public（公开）”；其次，即使你将个人资料中的电话号码设置为“only me（仅对自己），而在你将“通过手机号码查找到我”设置为“公开”之后，你个人资料中的“only me”设置便会失效。很多用户可能会认为自己的电话号码他人是看不见的，而事实并非如此。”

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013b6c11bfa06ce87c.png)

这个设置只能决定你的电话号码是否会出现在个人资料中，而你的电话号码是否会被公开其实跟这个设置没多大关系。

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01af267c64c21fde71.png)

如果这里设置成了“Everyone（所有人）”，即默认值，那么你的电话号码就会被公开。

“Who can look me up（谁可以查找到我）”这个选项的设置说明意味着能够查找到你的人已经知道你的电话号码了，也就是说他人可以根据你的电话号码查看到你的Facebook个人资料，而这里根本就没有“only me”这个选项。

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019b2c87749a217c1f.png)

如果你的Facebook绑定了手机号，那么你就没有任何办法来隐藏自己的手机号码了，无论你怎样做，你的“朋友”都能够看到你的号码

然而，当我将我的担忧告诉了Facebook的安全团队之后，他们仍然不打算修复这个问题。虽然我不敢苟同，但我仍然尊重他们的决定。因此，我才打算发表这篇文章，因为用户有权知道一切。

很多用户甚至根本不知道Facebook有他们的电话号码，虽然Facebook不能直接从你的手机中提取出电话号码，但是Facebook会不断地提醒用户绑定手机号，说是为了方便登录和密码找回。当我的一位同事得知此事之后便立刻取消了Facebook的手机号绑定，但是Facebook又会立刻让他重新绑定。

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t019fe9e4c6e8ad7a17.png)

绑定手机，将你的号码与全世界共享…

<br>

**实现方式**

我的这项技术需要使用到Graph Search， Graph Search是Facebook在2013年初推出的一款社交搜索工具，当你在搜索框中输入一个手机号码之后，你便会搜索到相应的用户：

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01d4681ec750b60850.png)

这是我找到的一个比利时明星的手机号

如果要一个一个地去测试这些手机号的话，可能需要花好几个月的时间，而这也不太现实。而且Facebook对用户的查询次数也有很大的限制，当你进行了一千次左右的用户查询之后Facebook将会暂时禁止你使用这项功能。当然了，你也可以使用僵尸网络来验证Facebook账号，但是我感觉Facebook同样也有相应的应对策略。

**第一步：最后两个数字（1分钟）**

我需要设计出一种能够一次性测试上千个手机号码的方法，需要测试的号码位数越少，拿到完整号码的速度也就越快。为了获取到目标号码的最后两位数，我可以使用Facebook的密码重置功能：

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b969e0fe8ed49e9b.png)

Facebook将比利时内政部长的手机号最后两位显示了出来

**第二步：运营商号码（5-35分钟）**

先来看看这个号码：04PPXXXX50（只有40万种可能的组合）。这是一个典型的比利时手机号码，其中X为0-10的任意一个数字，PP为运营商号码，最后的两个数字5和0是我们在上一步得到的。

不同的移动电话运营商都有自己固定的运营商号码，例如0468、047、048和049：

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017e1ba44001e1f7e8.png)

某些运营商号码的使用频率会比较高，而政府的人往往使用的是047号段，因为Proximus是政府的通讯服务赞助商。因此，我专门写了一个程序来枚举出所有可能的电话号码组合，比如说我们从0479开始：

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016d636cc9ded38452.png)

一秒钟不到程序就生成了所有的10000种号码组合

然后将这个号码列表导入Facebook的“find friends（好友查找）”功能中，此时我们查找到了好多名叫“Jan”的人，但他们都不是我要找的人。

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e88c19be129bdb09.png)

不用管“500” 那个数字，你其实已经导入了所有的号码

在尝试了0478号段之后还是没有找到我们的目标，所以我得换一个账号了，因为Facebook只允许一个账号在短时间内导入20000个通讯号码。于是我登录了另一个测试账号，这一次我选择的是0477号段：

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017b99460cacba814d.png)

0477，就是它了！

这一次，我们查到了运营商号码，即0477。

现在的号码为：0477XXXX50，所以内政部长的手机号就在这剩下的10000个手机号码中。

**第三步：缩小范围（10-15分钟）**

接下来的任务就是完成一些简单的数学计算了。我们只剩下10000个可能的手机号码需要处理，所以我们先测试其中的一半号码，这样就可以缩小我们的目标所在范围了，比如说我们先测试0477 0000 50 — 0477 5000 50。

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t017c77d65164038fdb.png)

成功找到目标！

看来我们选择的号码范围没有错，这也就意味着目标号码的第五个数字只能是0、1、2、3或4，总共只剩下5000种可能（0000-5000）。接下来，我们再把这5000个号码平分成两部分来进行测试。先测试0477 0000 50 – 0477 2500 50。

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01934e28d2750a5ea9.png)

没有找到目标

目标号码不在0000-2500这个区间，说明这个手机号码在2500-5000这个区间。我们还剩2500种可能，然后还是跟之前一样，将剩下的号码平分成两部分，则剩下的待测号码个数即为1250、750、325、162和81个，最终我们只剩下40个号码。我们可以继续进行这样的测试，然后将剩下的号码范围缩小到5个以内。当然了，如果只剩下50个号码的话，你也可以直接单独去测试每一个号码。

**第四步：最后的倒计时（1分钟）**

如果只剩下40个可能的手机号，那么我们就可以直接将它们输入到搜索框中来查看结果了。

[![](./img/85555/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013916e4cafbf35539.png)

手动查找，直到找出目标

<br>

**后话**

我已经将此事告知了内政部长，而他在声明中说到：他其实并不知道Facebook泄漏了他的手机号码，但是他个人对此并不是很介意。

此外，我们还与当地的一家电台合作并在电台直播过程中拨打了一位比利时名人的电话，然后告知他我在Facebook上找出了他的电话号码。我们当时聊得挺开心，随后他便立刻删除了Facebook上的电话号码。

<br>

**常见问题解答**

**1.	发生了什么？**

对于小型国家来说，通过Facebook来查找目标用户的电话号码相对来说是比较容易的。无论“who can look me up by phone（通过手机号码查找到我）”是否设置为了“public（公开）”，你的手机号码都会是公开的，而该选项的默认配置就是“public”。Facebook没有提供任何的措施来防止用户的手机号码发生泄漏，仅仅将你的手机号码设置为“only me（仅对自己）”其实并没有什么用。

**2.	谁会受到影响？**

小型国家的Facebook用户如果将手机号码添加到了Facebook资料中，且没有修改默认配置的话，他就会受此影响。如果你的手机号码低于十位数，而通信运营商号码位数有限，那么这种方法就可以成功。

3.	如何得知Facebook是否有我的电话号码？

点击[这里](https://www.facebook.com/settings?tab=mobile)查看

**4.	我如何测试自己是否受其影响？**

首先，确定Facebook是否知道你的手机号码，具体方法请参阅问题3。然后点击[这里](https://www.facebook.com/settings?tab=privacy)，检查“who can look me up by phone（通过手机号码查找到我）”是否设置成了“Public”。如果设置为“Friends”，那么就只有朋友可以通过手机号码查看到你的个人资料，而且这里没有“Only me”这种选项。

**5.	Facebook应该怎样做？**

很多用户其实根本就不知道自己的手机号码会通过这种方式发生泄漏，而这却是Facebook的一种默认行为，而这也是目前最大的问题所在。如果Facebook能够在“who can look me up by phone（通过手机号码查找到我）”设置中添加一个“Only me”选项的话，也许问题就没那么严重了。如果用户在非常用设备登录时，Facebook也可以隐藏密码重置功能中的手机号码后两位。除此之外，Facebook也应该限制用户在“好友查找”功能中可导入的号码数量。

**6.	我是否应该移除Facebook上的手机号码？**

这就很尴尬了，因为双因素身份验证功能需要使用手机号码，而这也是保护账号安全的一种绝佳方法，所以你还是将“who can look me up by phone（通过手机号码查找到我）”设置为“only friends（仅对好友）”吧。

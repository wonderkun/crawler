> 原文链接: https://www.anquanke.com//post/id/149526 


# 使用GitHub应用程序提升到组织所有者权限，获得10,000美元的奖励


                                阅读量   
                                **107136**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">15</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：medium.com
                                <br>原文地址：[https://medium.com/@cachemoney/using-a-github-app-to-escalate-to-an-organization-owner-for-a-10-000-bounty-4ec307168631](https://medium.com/@cachemoney/using-a-github-app-to-escalate-to-an-organization-owner-for-a-10-000-bounty-4ec307168631)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p1.ssl.qhimg.com/t01a7214ceb6930565e.png)](https://p1.ssl.qhimg.com/t01a7214ceb6930565e.png)

过去我从未参与过GitHub的长期奖金计划，但HackTheWorld终身免费私人存储库促销引起了我的兴趣。 我将通过一个简单但高影响力的权限升级漏洞来达到我的目的，这个升级是我在探索中发现的。 在这种情况下，我能够利用GitHub应用程序从组织成员升级到帐户所有者。



## 背景

首先，让我们回顾一下GitHub组织的简单用户角色。 我添加这部分来演示所有者帐户的功能，以及如何采取措施来最大限度地减少授权。

> 外部合作者（为了完整性） – 在技术上不属于组织的角色，只被授予了对特定存储库的访问权限而已。
成员 – 在组织内部权限最低的角色。 根据组织设置，该角色可能只能查看或对部分存储库进行“写入”访问。 成员可以通过此权限获得的最高访问级别是存储库管理员，这将允许更改该特定存储库的大多数配置设置。
所有者 – 可以在组织内部发挥最高作用，这基本上等于超级管理员。 该角色能够被允许查看和编辑所有组织数据和存储库; 但更关键的是，不可逆转地删除整个组织及其代码。

组织在GitHub中被广泛使用，常见的假设是当适当的访问控制做的到位时（例如，不给每个存储库的管理员访问权限），那么其成员就不会构成威胁。 一种常见的模式是将成员放入“团队”，并使用这些团队来促成跨存储库的访问控制。使用这种模式，组织所有者可以被限制在一个小部分用户子集里，因为基于团队的控制足以在需要的地方才提供扩展访问。



## 挖掘GitHub应用程序

当我在作为所有者进行组织设置时，注意到了一个“第三方访问策略”按钮。 这个设置的目的是防止组织成员通过OAuth将存储库访问权限授予给不受信任的第三方。 这个按钮一旦启用，成员必须通过OAuth的权限提示特定地进行请求访问，然后需要组织所有者批准才能访问任何组织数据。

[![](https://p4.ssl.qhimg.com/t010c888c3a1f1c3c44.png)](https://p4.ssl.qhimg.com/t010c888c3a1f1c3c44.png)

接下来我考虑的是另一种应用程序，一种集成应用。 集成类似于OAuth应用程序，不同的是它们代表的是组织而不是用户行事。 我的思考过程是检查“第三方访问策略”是否也适用于集成，或者这些策略是否会通过。 我来到应用市场，并通过几个应用程序完成安装流程。 很明显，作为组织成员，没有选择安装集成的权限。 只能将集成安装到自己的帐户或自己所拥有的组织中。 我后来在这些[文档](//developer.github.com/apps/differences-between-apps/%EF%BC%89)中找到了以下解释说明。
<li>组织成员不能请求安装GitHub应用程序。[![](https://p2.ssl.qhimg.com/t0126effcbf54832c26.png)](https://p2.ssl.qhimg.com/t0126effcbf54832c26.png)
</li>
在安装过程中，我注意到在选择“结算帐户”后，会弹出具有以下网址的页面：[https://github.com/apps/:app_name/installations/new/permissions?target_id=:id](https://github.com/apps/:app_name/installations/new/permissions?target_id=:id)

target_id是organization_id或要安装应用程序的account_id。 当然，作为另一个组织的成员，我动动我的小手将target_id更改为organization_id。 由于我的成员帐户是存储库管理员，因此系统提示我安装页面。<br>
我成功地安装该应用程序，但仅限于我拥有管理员权限的一个存储库。 我通过访问组织所有者帐户中的“已安装的GitHub应用程序”页面来检查安装。 成功！

[![](https://p2.ssl.qhimg.com/t019d94418e7e0b7a0d.png)](https://p2.ssl.qhimg.com/t019d94418e7e0b7a0d.png)

此时已过了凌晨3点，我知道自从我为了绕开“第三方访问”限制以来，我发现了一个重大的问题。 我将向GitHub计划报告，打算在报告中留下任何后续发现的问题。



## 进一步探索

第二天，我想看看我是否可以进一步做些什么。 我创建了自己的GitHub集成，并注意到请求的权限可能非常敏感。 特别是允许“写入”所有组织成员和团队的访问权限。当然，有权将集成安装到一个存储库中将不是说就允许我授予对所有组织成员的“写入”访问权限，对吧？不对。 由于预期的设计是只有所有者才能安装集成，因此具有二进制权限。 你可以授予的范围没有被强制执行，因为已经被认为具有最高级别的访问权限。

[![](https://p1.ssl.qhimg.com/t01b267344c8e371090.png)](https://p1.ssl.qhimg.com/t01b267344c8e371090.png)

然后下一步是查看API是否按预期工作，并且我是否真的能够使用它而不会遇到权限错误。 在抵达圣杯之前，我成功地混淆了一堆边界。 使用角色参数添加或更新组织成员资格。 使用该边界，我能够成功地邀请其他用户作为帐户所有者加入组织。

[![](https://p0.ssl.qhimg.com/t0128f63c5037411a84.png)](https://p0.ssl.qhimg.com/t0128f63c5037411a84.png)



## 结语

我认为这个的好处是因为它只能被存储库管理员利用。您的组织中有多少存储库管理员？经过更多测试后，我发现允许成员创建存储库的所有组织都很脆弱。这是因为成员会自动为其创建的任何存储库授予管理权限;允许他们通过创建一个虚拟存储库来安装应用程序的方式来利用这一点。此功能在默认情况下处于启用状态，组织通常会将其启用，因为GitHub的付款模式不再受存储库限制，而是基于用户数量。<br>
利用这个漏洞不一定只能是恶意的内部人员，也可以是攻击者来危害成员账户。假设一个组织中有300个成员;攻击者的表面区域不再局限于3或4个组织所有者，而是其任何成员。<br>
与往常一样，与GitHub安全团队合作愉快！



## 时间线

初始报告：11/11/17 @ 3:30 AM<br>
报告升级为组织所有者的能力：11/11/17 @ 8:30 PM<br>
GitHub团队正式调查此问题：11/13/17 @ 5:30 AM<br>
10,000美元奖励和分类奖励：11/14/17 @ 1:40 PM<br>
修正部署到生产：11/15/17<br>
问题标记为已解决：12/1/17

审核人：yiwang   编辑：边边

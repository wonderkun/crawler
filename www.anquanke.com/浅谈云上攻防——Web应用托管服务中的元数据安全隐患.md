> 原文链接: https://www.anquanke.com//post/id/246751 


# 浅谈云上攻防——Web应用托管服务中的元数据安全隐患


                                阅读量   
                                **148981**
                            
                        |
                        
                                                                                    



[![](https://p4.ssl.qhimg.com/t016fa039f81d0d2241.png)](https://p4.ssl.qhimg.com/t016fa039f81d0d2241.png)

## 前言

Web应用托管服务是一种常见的平台即服务产品（PaaS），可以用来运行并管理Web类、移动类和API类应用程序。Web应用托管服务的出现，有效地避免了应用开发过程中繁琐的服务器搭建及运维，使开发者可以专注于业务逻辑的实现。在无需管理底层基础设施的情况下，即可简单、有效并且灵活地对应用进行部署、伸缩、调整和监控。

Web应用托管服务作为一种云上服务，其中也会应用到的元数据服务进行实例元数据查询，因此不得不考虑元数据服务安全对Web应用托管服务安全性的影响。

通过“浅谈云上攻防”系列文章[《浅谈云上攻防——元数据服务带来的安全挑战》](http://mp.weixin.qq.com/s?__biz=MzU3ODAyMjg4OQ==&amp;mid=2247487562&amp;idx=1&amp;sn=d8b821f8f55d311815dec2e563e8c890&amp;chksm=fd7aecccca0d65dadcf2e002dde99c1f97e2dd638f308b8c717b5bd9effa03dc817666d3f0f8&amp;scene=21#wechat_redirect)一文的介绍，元数据服务为云上业务带来的安全挑战想必读者们已经有一个深入的了解。Web应用托管服务中同样存在着元数据服务带来的安全挑战，本文将扩展探讨元数据服务与Web应用托管服务这一组合存在的安全隐患。



## Web应用托管服务中的 元数据安全隐患

AWS Elastic Beanstalk 是 AWS 提供的平台即服务 (PaaS) 产品，用于部署和扩展为各种环境（如 Java、.NET、PHP、Node.js、Python、Ruby 和 Go）开发的 Web 应用程序。Elastic Beanstalk 会构建选定的受支持的平台版本，并预置一个或多个AWS资源（如 Amazon EC2 实例）来运行应用程序。

Elastic Beanstalk 的工作流程如下：

[![](https://p5.ssl.qhimg.com/t01bac861ae5d270729.png)](https://p5.ssl.qhimg.com/t01bac861ae5d270729.png)

在使用Elastic Beanstalk 部署Web 应用程序时，用户可以通过上传应用程序代码的zip 或 war 文件来配置新应用程序环境，见下图：

[![](https://p3.ssl.qhimg.com/t015bde8e983fad41e8.png)](https://p3.ssl.qhimg.com/t015bde8e983fad41e8.png)

在进行新应用程序环境配置时，Elastic Beanstalk服务将会进行云服务器实例创建、安全组配置等操作。

与此同时， Elastic Beanstalk也将创建一个名为 elasticbeanstalk-region-account-id 的 Amazon S3 存储桶。这个存储桶在后续的攻击环节中比较重要，因此先简单介绍一下：Elastic Beanstalk服务使用此存储桶存储用户上传的zip与war 文件中的源代码、应用程序正常运行所需的对象、日志、临时配置文件等。

elasticbeanstalk-region-account-id中存储的对象列表以及其相关属性可参见下图：

[![](https://p0.ssl.qhimg.com/t016806b51f48353783.png)](https://p0.ssl.qhimg.com/t016806b51f48353783.png)

Elastic Beanstalk服务不会为其创建的 Amazon S3 存储桶启用默认加密。这意味着，在默认情况下，对象以未加密形式存储在存储桶中（并且只有授权用户可以访问）。

在了解Elastic Beanstalk的使用之后，我们重点来看一下元数据服务与Elastic Beanstalk服务组合下的攻击模式。

正如上一篇文章提到的：当云服务器实例中存在SSRF、XXE、RCE等漏洞时，攻击者可以利用这些漏洞，访问云服务器实例上的元数据服务，通过元数据服务查询与云服务器实例绑定的角色以及其临时凭据获取，在窃取到角色的临时凭据后，并根据窃取的角色临时凭据相应的权限策略，危害用户对应的云上资源。

而在Elastic Beanstalk 服务中也同样存在着这种攻击模式，Elastic Beanstalk 服务创建名为aws-elasticbeanstalk-ec2-role的角色，并将其与云服务器实例绑定。

我们关注一下aws-elasticbeanstalk-ec2-role角色的权限策略：<br>
从AWS官网可知，Elastic Beanstalk服务为aws-elasticbeanstalk-ec2-role角色提供了三种权限策略：用于 Web 服务器层的权限策略；用于工作程序层的权限策略；拥有多容器 Docker 环境所需的附加权限策略，在使用控制台或 EB CLI 创建环境时，Elastic Beanstalk 会将所有这些策略分配给aws-elasticbeanstalk-ec2-role角色，接下来分别看一下这三个权限策略。

AWSElasticBeanstalkWebTier – 授予应用程序将日志上传到 Amazon S3 以及将调试信息上传到 AWS X-Ray 的权限，见下图：

[![](https://p2.ssl.qhimg.com/t01359491c2c7261d4b.png)](https://p2.ssl.qhimg.com/t01359491c2c7261d4b.png)

AWSElasticBeanstalkWorkerTier – 授予日志上传、调试、指标发布和工作程序实例任务（包括队列管理、定期任务）的权限，见下图：

[![](https://p2.ssl.qhimg.com/t017a87c0fa69a020c9.png)](https://p2.ssl.qhimg.com/t017a87c0fa69a020c9.png)

AWSElasticBeanstalkMulticontainerDocker – 向 Amazon Elastic Container Service 授予协调集群任务的权限，见下图：

[![](https://p3.ssl.qhimg.com/t0188ffbac22ee25d7b.png)](https://p3.ssl.qhimg.com/t0188ffbac22ee25d7b.png)

从上述策略来看，aws-elasticbeanstalk-ec2-role角色拥有对“elasticbeanstalk-”开头的S3 存储桶的读取、写入权限以及递归访问权限，见下图：

[![](https://p4.ssl.qhimg.com/t01b535719ead2ff3df.png)](https://p4.ssl.qhimg.com/t01b535719ead2ff3df.png)

通过权限策略规则可知，此权限策略包含上文介绍的elasticbeanstalk-region-account-id存储桶的操作权限。

elasticbeanstalk-region-account-id存储桶命名也是有一定规律的：elasticbeanstalk-region-account-id存储桶名由“elasticbeanstalk”字符串、资源region值以及account-id值组成，其中elasticbeanstalk字段是固定的，而region与account-id值分别如下：
- l region 是资源所在的区域（例如，us-west-2）
- account-id 是Amazon账户 ID，不包含连字符（例如，123456789012）
通过存储桶命名规则的特征，在攻击中可以通过目标的信息构建出elasticbeanstalk-region-account-id存储桶的名字。

接下来介绍一下Elastic Beanstalk中元数据安全隐患。

用户在使用Elastic Beanstalk中部署Web应用程序时，如果用户的Web应用程序源代码中存在SSRF、XXE、RCE等漏洞，攻击者可以利用这些漏洞访问元数据服务接口，并获取account-id、Region以及aws-elasticbeanstalk-ec2-role角色的临时凭据，并通过获取到的信息对S3存储桶发起攻击，account-id、Region以及aws-elasticbeanstalk-ec2-role角色的临时凭据获取方式如下：

以Elastic Beanstalk中部署Web应用程序中存在SSRF漏洞为例，攻击者可以通过发送如下请求以获取account-id、Region：

https://x.x.x.x/ssrf.php?url=http://169.254.169.254/latest/dynamic/instance-identity/document

从响应数据中Accountid、Region字段获取account-id、Region值，攻击者可以以此构造出目标elasticbeanstalk-region-account-id存储桶名称。

攻击者可以发送如下请求以获取aws-elasticbeanstalk-ec2-role角色的临时凭据：

https://x.x.x.x/ssrf.php?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/ AWS-elasticbeanstalk-EC2-role

从响应数据中获取aws-elasticbeanstalk-ec2-role角色的临时凭据：AccessKeyId、SecretAccessKey、Token三个字段值。

随后，攻击者使用获取到的aws-elasticbeanstalk-ec2-role角色的临时凭据，访问云API接口并操作elasticbeanstalk-region-account-id存储桶。

上述攻击模式的攻击流程图如下：

elasticbeanstalk-region-account-id存储桶对Elastic Beanstalk服务至关重要，在攻击者获取elasticbeanstalk-region-account-id存储桶的操作权限之后，可以进行如下的攻击行为，对用户资产进行破坏。

### 获取用户源代码

在获取elasticbeanstalk-region-account-id存储桶的控制权后，攻击者可以递归下载资源来获取用户Web应用源代码以及日志文件，具体操作如下：

aws s3 cp s3:// elasticbeanstalk-region-account-id/ /攻击者本地目录 –recursive

攻击者可以通过在AWS命令行工具中配置获取到的临时凭据，并通过如上指令递归下载用户elasticbeanstalk-region-account-id存储桶中的信息，并将其保存到本地。

### 获取实例控制权

除了窃取用户Web应用源代码、日志文件以外，攻击者还可以通过获取的角色临时凭据向elasticbeanstalk-region-account-id存储桶写入Webshell从而获取实例的控制权。

攻击者编写webshell文件并将其打包为zip文件，通过在AWS命令行工具中配置获取到的临时凭据，并执行如下指令将webshell文件上传到存储桶中：

aws s3 cp webshell.zip s3:// elasticbeanstalk-region-account-id/

当用户使用AWS CodePipeline等持续集成与持续交付服务时，由于上传webshell操作导致代码更改，存储桶中的代码将会自动在用户实例上更新部署，从而将攻击者上传的webshell部署至实例上，攻击者可以访问webshell路径进而使用webshell对实例进行权限控制。



## 更多安全隐患

除了上文章节中介绍的安全隐患，Web应用托管服务中生成的错误的角色权限配置，将为Web应用托管服务带来更多、更严重的元数据安全隐患。

从上文章节来看，Elastic Beanstalk服务为aws-elasticbeanstalk-ec2-role角色配置了较为合理的权限策略，使得即使Web应用托管服务中托管的用户应用中存在漏洞时，攻击者在访问实例元数据服务获取aws-elasticbeanstalk-ec2-role角色的临时凭据后，也仅仅有权限操作Elastic Beanstalk服务生成的elasticbeanstalk-region-account-id S3存储桶，并非用户的所有存储桶资源。这样一来，漏洞所带来的危害并不会直接扩散到用户的其他资源上。

但是，一旦云厂商所提供的Web应用托管服务中自动生成并绑定在实例上的角色权限过高，当用户使用的云托管服务中存在漏洞致使云托管服务自动生成的角色凭据泄露后，危害将从云托管业务直接扩散到用户的其他业务，攻击者将会利用获取的高权限临时凭据进行横向移动。

通过临时凭据，攻击者可以从Web应用托管服务中逃逸出来，横向移动到用户的其他业务上，对用户账户内众多其他资产进行破坏，并窃取用户数据。具体的攻击模式可见下图：

由于攻击者使用Web应用托管服务生成的合法的角色身份，攻击行为难以被发觉，对用户安全造成极大的危害。

针对于这种情况，首先可以通过加强元数据服务的安全性进行缓解，防止攻击者通过SSRF等漏洞直接访问实例元数据服务并获取与之绑定的角色的临时凭据。

此外，可以通过限制Web应用托管服务中绑定到实例上的角色的权限策略进行进一步的安全加强。在授予角色权限策略时，遵循最小权限原则。

最小权限原则是一项标准的安全原则。即仅授予执行任务所需的最小权限，不要授予更多无关权限。例如，一个角色仅是存储桶服务的使用者，那么不需要将其他服务的资源访问权限（如数据库读写权限）授予给该角色。



## 参考文献

https://docs.aws.amazon.com/zh_cn/elasticbeanstalk/latest/dg/iam-instanceprofile.html

https://notsosecure.com/exploiting-ssrf-in-aws-elastic-beanstalk/

https://docs.aws.amazon.com/zh_cn/elasticbeanstalk/latest/dg/concepts-roles-instance.html

> [Escalating SSRF to RCE](https://generaleg0x01.com/2019/03/10/escalating-ssrf-to-rce/)

<iframe title="“Escalating SSRF to RCE” — GeneralEG 0x01 " class="wp-embedded-content" sandbox="allow-scripts" security="restricted" style="position: absolute; clip: rect(1px, 1px, 1px, 1px);" src="https://generaleg0x01.com/2019/03/10/escalating-ssrf-to-rce/embed/#?secret=JwZrtt7Efm" data-secret="JwZrtt7Efm" width="500" height="282" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>

https://mp.weixin.qq.com/s/Y9CBYJ_3c2UI54Du6bneZA

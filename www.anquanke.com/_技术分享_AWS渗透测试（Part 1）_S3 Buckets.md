> 原文链接: https://www.anquanke.com//post/id/86927 


# 【技术分享】AWS渗透测试（Part 1）：S3 Buckets


                                阅读量   
                                **196326**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：virtuesecurity.com
                                <br>原文地址：[https://www.virtuesecurity.com/blog/aws-penetration-testing-s3-buckets/](https://www.virtuesecurity.com/blog/aws-penetration-testing-s3-buckets/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p4.ssl.qhimg.com/t012bc9f45bc6fe948a.png)](https://p4.ssl.qhimg.com/t012bc9f45bc6fe948a.png)

译者：[興趣使然的小胃](http://bobao.360.cn/member/contribute?uid=2819002922)

预估稿费：160RMB

投稿方式：发送邮件至linwei#360.cn，或登陆网页版在线投稿



**一、前言**

****

亚马逊云服务平台（AWS，Amazon Web Services）面向现代Web应用提供了一套非常强大又非常可靠的基础架构。随着Web服务不断涌现新的功能，我们也需要更新安全理念。对于渗透测试人员来说，有时候某些AWS服务可能会给渗透测试带来挑战。

在这一系列文章中，我们会详细分析AWS服务、常见的漏洞以及错误配置情况，也会介绍如何使用自动化工具对每个服务进行全方位的安全测试。希望渗透测试人员阅读本文后，可以使用我们研发的AWS BurpSuite扩展来评估AWS S3 buckets的安全性。

我们研发了一个BurpSuite插件：[AWS Extender](https://github.com/VirtueSecurity/aws-extender)，这个插件可以从代理流量中识别并评估S3 buckets。此外，该插件也可以识别身份池（identity pools）、Google Cloud以及微软Azure服务。

[![](https://p5.ssl.qhimg.com/t0158f9c30b7eb48e3e.png)](https://p5.ssl.qhimg.com/t0158f9c30b7eb48e3e.png)

工具下载地址为：

[**AWS Extender Burp插件**](https://github.com/VirtueSecurity/aws-extender)

[**AWS Extender CLI**](https://github.com/VirtueSecurity/aws-extender-cli)



**二、Amazon Simple Storage Service (S3)**

****

自2006年3月推出以来，亚马逊S3（简单云存储服务）已经成为非常受欢迎的对象（object）存储服务，S3提供了可扩展的存储架构，目前正托管数万亿个对象。尽管S3可以托管静态网站，但它本身并不支持代码执行或者任何编程功能。S3只能通过[REST](https://en.wikipedia.org/wiki/Representational_state_transfer)、[SOAP](https://en.wikipedia.org/wiki/SOAP)以及[BitTorrent](http://docs.aws.amazon.com/AmazonS3/latest/dev/S3TorrentRetrieve.html) web接口来提供存储服务，支持静态文件的读取、上传以及删除。

亚马逊为S3 bucket提供了多种不同的访问控制机制，包括访问控制列表（ACL）、bucket策略以及IAM（Identity and Access Management）策略。默认情况下，亚马逊在创建S3 bucket时会为它设置一个默认ACL，以便bucket所有者掌握该bucket的所有权限。

<br>

**三、S3渗透测试基础**

****

每个web应用渗透测试人员都应该注意以下几个要点：

所有的S3 bucket都共享一个全局命名方案，因此无法阻止对bucket的枚举遍历。

所有的S3 bucket都有一个DNS入口，形式为**[bucketname].s3.amazonaws.com**。

我们可以通过bucket的HTTP 接口（**https://[bucketname].s3.amazonaws.com**）来访问bucket，当然也可以使用非常强大的[AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/installing.html)来访问：

```
apt-get install awscli 
aws s3 ls s3://mybucket
```



**四、常见的S3漏洞**

****

如果你是AWS或者S3的新手，你需要注意以下几种常见漏洞：

**Bucket未授权访问**：顾名思义，经过错误配置后，匿名用户就可以列出、读取或者写入S3 bucket。

**Bucket半公开访问**：经过配置后，“通过身份认证的用户”就可以访问S3 bucket。这就意味着只要经过AWS的认证，任何人都可以访问这些资源。我们需要拥有有效的AWS access key以及secret才能测试这种情况。

**ACL权限错误**：Bucket的ACL也有相应的权限，然而许多情况下所有人都可以读取这个信息。这并不代表bucket本身出现错误配置情况，然而我们可以借此了解哪些用户拥有什么类型的访问权限。



**五、访问控制列表（ACL）**

****

S3访问控制列表（ACL）可以应用在bucket层以及对象层。ACL通常支持如下几种权限：

**读取（READ）**

在bucket层，该权限允许用户列出bucket中的对象。在对象层，该权限允许用户读取对象的内容及元数据。

**写入（WRITE）**

在bucket层，该权限允许用户创建、覆盖以及删除bucket中的对象。

**读取访问控制策略（READ_ACP）**

在bucket层，该权限允许用户读取bucket的访问控制列表。在对象层，该权限允许用户读取对象的访问控制列表。

**写入访问控制策略（WRITE_ACP）**

在bucket层，该权限允许用户设置bucket的ACL。在对象层，该权限允许用户设置对象的ACL。

**完全控制（FULL_CONTROL）**

在bucket层，该权限等同于向用户许可“READ”、“WRITE”、“READACP”以及“WRITEACP”权限。在对象层，该权限等同于向用户许可“READ”、“READACP”以及“WRITEACP”权限。

在这里，待授权的用户可以是独立的AWS用户，由用户ID以及邮箱来标识，也可以是如下某个预定义的组：

**认证用户组（The Authenticated Users Group）**

该组代表所有的AWS用户，对应“http://acs.amazonaws.com/groups/global/AuthenticatedUsers” 这个URI。

**所有用户组（The All Users Group）**

代表所有用户（包括匿名用户），对应“http://acs.amazonaws.com/groups/global/AllUsers” 这个URI。

**日志传输组（The Log Delivery Group）**

仅用于访问日志记录，对应“http://acs.amazonaws.com/groups/s3/LogDelivery” 这个URI。

**ACL示例如下所示：**

```
&lt;?xml version="1.0" encoding="UTF-8"?&gt;
&lt;AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/"&gt;
  &lt;Owner&gt;
    &lt;ID&gt;*** Owner-Canonical-User-ID ***&lt;/ID&gt;
    &lt;DisplayName&gt;owner-display-name&lt;/DisplayName&gt;
  &lt;/Owner&gt;
  &lt;AccessControlList&gt;
    &lt;Grant&gt;
      &lt;Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
               xsi:type="Canonical User"&gt;
        &lt;ID&gt;*** Owner-Canonical-User-ID ***&lt;/ID&gt;
        &lt;DisplayName&gt;display-name&lt;/DisplayName&gt;
      &lt;/Grantee&gt;
      &lt;Permission&gt;FULL_CONTROL&lt;/Permission&gt;
    &lt;/Grant&gt;
  &lt;/AccessControlList&gt;
&lt;/AccessControlPolicy&gt;
```

AWS Extender Burp扩展可以处理前面提到过的所有权限。也就是说，当识别出某个S3 bucket后，该扩展可以执行如下测试：

1、尝试列出bucket中托管的对象（READ）。

2、尝试将一个“test.txt”文件上传到bucket中（WRITE）。

3、尝试读取bucket的访问控制列表（READ_ACP）。

4、在不修改bucket的访问控制列表的前提下，尝试设置bucket的访问控制列表（WRITE_ACP）。

注意：对于识别出来的每个S3对象，该扩展也执行了类似的测试。

<br>

**六、Bucket策略**

****

Bucket所有者可以通过bucket策略来设定操作主体（principal）能够在某个资源上执行什么操作。这里的principal可以为任意AWS用户或组，也可以是包含匿名用户在内的所有用户；action可以是bucket策略支持的任何预定义权限；而resource可以为整个bucket，也可以是某个特定的对象。bucket策略以JSON格式表示，如下所示：

```
`{`
    "Version":"2012-10-17",
    "Statement": [
        `{`
            "Effect":"Allow",
            "Principal": "*",
            "Action":["s3:GetObject"],
            "Resource":["arn:aws:s3:::examplebucket/*"]
        `}`
    ]
`}`
```

上面这个策略允许在“**arn:aws:s3:::examplebucket/***”资源上执行“**s3:GetObject**”操作，principal使用通配符“*”来表示。这实际上等同于使用访问控制列表（ACL）来赋予所有用户组拥有“examplebucket”这个S3 bucket的“READ”权限。

AWS Extender Burp扩展目前支持如下权限：



```
s3:ListBucket
s3:ListMultipartUploadParts
s3:GetBucketAcl
s3:PutBucketAcl
s3:PutObject
s3:GetBucketNotification
s3:PutBucketNotification
s3:GetBucketPolicy
s3:PutBucketPolicy
s3:GetBucketTagging
s3:PutBucketTagging
s3:GetBucketWebsite
s3:PutBucketWebsite
s3:GetBucketCORS
s3:PutBucketCORS
s3:GetLifecycleConfiguration
s3:PutLifecycleConfiguration
s3:PutBucketLogging
```

在第二篇文章中，我们会介绍S3权限方面的更多内容，包括IAM、访问令牌（access token）以及EC2、Cognito认证等等。读者可以继续阅读本系列的第二篇文章。

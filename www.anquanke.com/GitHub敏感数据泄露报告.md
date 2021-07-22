> 原文链接: https://www.anquanke.com//post/id/198361 


# GitHub敏感数据泄露报告


                                阅读量   
                                **825356**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者paloaltonetworks，文章来源：unit42.paloaltonetworks.com
                                <br>原文地址：[https://unit42.paloaltonetworks.com/github-data-exposed/](https://unit42.paloaltonetworks.com/github-data-exposed/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p3.ssl.qhimg.com/t0139fe5cfbc2ca9498.jpg)](https://p3.ssl.qhimg.com/t0139fe5cfbc2ca9498.jpg)



## 0x00 前言

在之前公布的[2020年春季云端威胁报告](http://go.paloaltonetworks.com/cloudthreatreport)中，我们侧重于DevOps实践内容，介绍了云端出现的一些错误配置情况。在本文中，我们详细分析了GitHub上的数据泄露情况，使DevOps、工程及安全团队能够重视该问题，及早发现并解决安全风险。

在代码从开发到生产的快速跟踪流程上，很少有其他数据仓库能够跟得上GitHub的脚步。然而俗话说的好，“速度越快，风险越高”。研究人员发现，如果使用了公共GitHub账户，那么DevOps就有可能泄露敏感信息。与此同时，数据丢失或者被入侵的风险也会相应提高。然而，如果正确实现DevSecOps、使用GitHub Event API扫描器，就能大大降低泄露敏感信息的风险。

Unit 42研究人员通过GitHub Event API 分析了超过24,000份GitHub公开数据，发现有数千个文件中可能包含敏感信息，整体情况如下：

[![](https://p5.ssl.qhimg.com/t014db1e76dfe2d87e6.png)](https://p5.ssl.qhimg.com/t014db1e76dfe2d87e6.png)



## 0x01 GitHub Event API

GitHub为开发者提供了一个[Event API](https://developer.github.com/v3/activity/events/)搜索功能，利用这一功能，开发者可以近乎实时地获取上传至GitHub服务器的文件及代码列表。Event API可以帮助研究人员查看并扫描推送到GitHub公共区域的文件（比如公开分享的数据），但使用起来有些限制条件，每个账户每小时请求次数不超过5,000次。目前有多款工具用到了这一功能。在商业领域，GitHub自身提供并维护着[GitHub Token Scanner](https://help.github.com/en/github/administering-a-repository/about-token-scanning)解决方案，可以检查文件中的令牌字符串，避免被用于欺诈、滥用等恶意场景。AWS使用了[git-secrets](https://github.com/awslabs/git-secrets)来扫描用户名、密码及其他关键字符串，避免出现敏感数据泄露。此外还有一些开源GitHub Event API扫描器，如[gitrob](https://github.com/michenriksen/gitrob)及[trugglehog](https://github.com/dxa4481/truffleHog)，红方、渗透测试人员以及恶意用户等都使用过这些工具来识别潜在的敏感信息。



## 0x02 ShhGit

[![](https://p2.ssl.qhimg.com/t014b867b684752f36f.png)](https://p2.ssl.qhimg.com/t014b867b684752f36f.png)

Unit 42研究人员（以下简称我们）使用eth0izzle开发的[shhgit](https://github.com/eth0izzle/shhgit)来近实时读取GitHub事件，并尝试回答如下3个问题：

1、文件中是否可能发现潜在的敏感数据？

2、这些数据是否可以与某个单位关联起来？

3、安全预防措施是否可以避免不必要的潜在敏感信息泄露？

以上3个问题的答案都是肯定的。经过分析后，我们发现有超过24,000个不同GitHub文件会触发shhgit预定的120个特征规则以及Unit 42设置的特征规则。研究人员发现了一些潜在的敏感数据条目，包括：
- 4109个配置文件
- 2464个API密钥
- 2328个硬编码的用户名及密码
- 2144个私钥文件
- 1089个OAuth令牌
进一步分析后，我们确认了结果的有效性，识别出文件所有者、项目名，在某些情况下还能识别出公开此信息的企业名称。



## 0x03 研究结果

### <a class="reference-link" name="%E7%A1%AC%E7%BC%96%E7%A0%81%E5%AF%86%E7%A0%81"></a>硬编码密码

我们经研究发现，最敏感的还是硬编码密码。我们总共找到了2328个用户名及密码条目，其中包括880个不同的密码、797个不同的用户名。这些密码位于服务URL API以及SSH配置文件中。我们注意到，找到的密码条目中只有18%与最常见的10个密码有关。密码“password”以72次排在榜首，第二名为密码“secret”，共有51次。最常见的10个密码如表1所示：

|密码|次数
|------
|password|72
|secret|51
|admin|46
|1234|41
|db_password|40
|*****|38
|pass456|35
|root|34
|pass-word-pass-word-pass-word|29
|token|26

表1. 最常见的10个密码

比较有趣的是，在880个不同的密码中，有817个密码出现的次数等于或者少于3次，而有655个密码只出现1次。这些密码本身的非常独特，因此也非常有趣。比如，我们抽样了10个密码，如下所示：

```
p4ssW0rde
P@##w0rd
Password!
qwerty123456789
simplepass123
sqluser2019
supersecret
wilson1234567
xxxxxxxxxxxxxxxxxxxx
Z*NsqgS5$@jHsF2
```

从直观感受来看，我们注意到有些密码在企业中非常常见。大多数密码满足最低密码设置要求，并且也很容易记住（比如前两个“password”变种密码）。然而攻击者很容易猜测出这些密码，并且这些密码也经常出现在大多数暴力破解字典中。此外，其余8个密码也属于简单密码，只包含大小写和数字组合，甚至只包含重复20次的`x`字符。由于这些密码满足伪复杂度模式，并且具有唯一性，因此我们认为这些密码“很有可能是合法密码”。也就是说，这些密码很有可能是工程师在生产环境中实际使用的密码。由于这些密码的出现频率很高，经常出现在常见云服务（如Redis、PostgreSQL、MongoDB以及AMPQ等）的URL API请求中，因此云环境本身也很有可能使用相同的伪复杂密码。

相比之下，我们发现只有27个不同的实例使用了可变密码字段，这表明这些实例使用的是临时或者动态密码。比如，有些实例中使用了`$password`、``{`password`}``或者`%Password%`占位符。在我们找到的2328个密码中，这27个不同的密码实例总数只有67个，不到3%。

### <a class="reference-link" name="%E7%A1%AC%E7%BC%96%E7%A0%81API%E5%AF%86%E9%92%A5%E5%8F%8AOAuth%E4%BB%A4%E7%89%8C"></a>硬编码API密钥及OAuth令牌

在触发规则的24,000多个GitHub文件中，我们共发现了2464个API密钥、1998个OAuth令牌。这些元素大多互不相同，只有15个密钥或令牌出现超过4次，只有1个元素出现次数最多（共12次），如表2所示。

|API密钥|次数
|------
|AIzaSyxxxxxxxxxxy2TVWhfo1VUmARKlG4suk|12
|AIzaSyxxxxxxxxxx4kQPLP1tjJNxBTbfCAdgg|9
|AIzaSyxxxxxxxxxxYmhQgOjt_HhlWO31cYfic|8
|AIzaSyxxxxxxxxxxq_V7x_JXkz2llt6jhI5mI|6
|AIzaSyxxxxxxxxxxnpxfNuPBrOxGhXskfebXs|6
|AIzaSyxxxxxxxxxxRJ4c2tVRJxu8hZzcWA1fE|5
|AIzaSyxxxxxxxxxxfUutD2aeWE1WFdnTBd_Jc|5
|AIzaSyxxxxxxxxxxPdQUkRUerdohx28Fuv4wE|5
|AIzaSyxxxxxxxxxxc2127s6TkcilVngyfFves|4
|AIzaSyxxxxxxxxxx7SALQhZKfGBN3sFDs27Ps|4
|AIzaSyxxxxxxxxxxJFdebWiX5KqyLHdakBOUU|4
|AIzaSyxxxxxxxxxxVtidHrO1LXtfT3TFZuEOA|4
|AIzaSyxxxxxxxxxxrzdcL6rvxywDDOvfAu6eE|4
|AIzaSyxxxxxxxxxxEnTs4EfSxFIdFIdowigCs|4
|AIzaSyxxxxxxxxxx4o82um7Gj1rY7R9W0apWg|4

表2. 出现次数最多的前15个API密钥

由于API密钥及OAuth密钥的特殊性，这些元素可以让用户直接访问指定云环境。如果API密钥或者OAuth令牌落入他人之手，那么恶意攻击者可以仿冒工程师合法身份，获得目标的控制权。在最坏的场景下，如果云环境中API密钥使用管理员权限创建，那么使用该密钥的任何人都具备云账户的完全访问权限。之前的确发生过合法API密钥泄露事故，大家可以参考之前的[UpGuard](https://searchsecurity.techtarget.com/news/252477280/AWS-leak-exposes-passwords-private-keys-on-GitHub)事件。在这次事件中，该公司通过GitHub泄露了将近1GB的数据，包括AWS API密钥、日志文件以及IaC模板。该事件中，服务及基础设施配置文件中的合法API密钥被公之于众，这些凭据及API密钥与商业组织所拥有的root账户有关。

与密码一样，密钥及令牌必须受到严格保护及控制，确保只有合法用户掌握这些信息。如果API密钥或OAuth令牌丢失或者可能被泄露，那么应当及时撤销并重新生成。我们找到的2464个API密钥及1098个OAuth令牌如表3所示，其中也列出了关联的环境。

|关联环境|次数
|------
|Google Cloud API Key|1998
|Google OAuth Token|1098
|Miscellaneous – API_KEY|358
|SonarQube Docs API Key|84
|MailGun API Key|19
|NuGet API Key|4
|Twilo API Key|1

表3. 泄露API及OAuth密钥所关联的环境

### <a class="reference-link" name="%E9%85%8D%E7%BD%AE%E4%BF%A1%E6%81%AF%E5%8F%8A%E7%A7%81%E9%92%A5%E6%96%87%E4%BB%B6"></a>配置信息及私钥文件

我们通过分析配置信息及私钥文件，完成了对云环境的深入分析。在触发sshgit及Unit 42特征规则的24,000个文件中，配置文件占了绝大部分，将近17%。大多数配置文件类型为[Django](https://www.djangoproject.com/)配置文件。在我们找到的所有配置文件类型中，这类配置文件将近占了1/3，参考表4。Django是基于python的一个web框架，可以用来快速开发和设计。PHP是web设计中非常常见的一种脚本语言，在结果中排名第3。基于web的这些配置文件会暴露目标组织的云架构信息，使攻击者能够轻松访问内部云服务器，也将使后续攻击过程更加轻松。

|配置文件|数量
|------
|Django配置文件|1473
|环境配置文件|601
|PHP配置文件|587
|Shell配置文件（`.bashrc`、`.zshrc`、`.cshrc`）|328
|潜在的Ruby On Rails数据库配置文件|266
|NPM配置文件|233
|Shell profile配置文件|211
|Shell命令别名配置文件|130
|Git配置文件|113
|SSH配置文件|35

表4. 最常见的10类配置文件类型

我们发现环境及shell配置文件占比较高，这类配置文件可以用来设置目标系统或服务的环境。Shell、SSH、profile及Git配置文件同样排名前列。目标服务经常在配置文件中存放所需的用户名、密码、API密钥或者令牌占位符。我们发现有将近80%的配置文件会包含某些用户名/密码、API密钥或者OAuth令牌。



## 0x04 总结

经过研究后，我们发现用户会将敏感数据上传到GitHub，这些敏感数据包括：

1、硬编码的用户名及密码；

2、硬编码的API密钥；

3、硬编码的OAuth密钥；

4、内部服务及环境配置信息。

正如我们在云端威胁报告中提到的，在CI/CD处置过程中，我们强烈建议从公共仓库（如GitHub）拉取的所有IaC模板都要经过彻底扫描，确认是否存在漏洞。根据研究结果，我们扫描的每个CFT（CloudFormation template）中有将近一半都包含潜在的易受攻击的配置信息，部署易受攻击的云模板的可能性非常大。此外，各种组织应当使用GitHub Event API扫描器，避免在GitHub上公开的代码泄露敏感内部信息。



## 0x05 缓解措施

如果用户及组织向GitHub仓库提交代码，我们建议部署如下缓解措施，确保配置文件不会泄露敏感信息：

1、采用可变且基于CLI参数的代码开发实践，从示例代码中移除硬编码用户名及密码、API密钥以及OAuth令牌；

2、采用密码安全策略，强制使用复杂密码；

3、采用发布策略，规范并防止通过外部资源共享内部敏感数据；

4、使用GitHub的企业账户功能，确保严格审查公开数据；

5、使用AWS-git secrets、GitHub TokenScanner、gitrob或者trugglehog 来识别并移除被公开的令牌。

大家可以下载 Unit 42的[2020年春季云端威胁报告](http://go.paloaltonetworks.com/cloudthreatreport)，针对性强化环境中的安全措施。

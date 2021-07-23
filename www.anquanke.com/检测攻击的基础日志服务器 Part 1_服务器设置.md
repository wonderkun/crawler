> 原文链接: https://www.anquanke.com//post/id/103345 


# 检测攻击的基础日志服务器 Part 1：服务器设置


                                阅读量   
                                **91059**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者VIVI，文章来源：thevivi.net
                                <br>原文地址：[https://thevivi.net/2018/03/23/attack-infrastructure-logging-part-1-logging-server-setup/](https://thevivi.net/2018/03/23/attack-infrastructure-logging-part-1-logging-server-setup/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p5.ssl.qhimg.com/t0189fc82a55b4bf023.png)](https://p5.ssl.qhimg.com/t0189fc82a55b4bf023.png)



## 写在前面的话

在今年年初的时候我有个改进我的基础设施日志管理系统的想法。但是到现在，我的日志管理技术还是仅限于打开终端，连接SSH，然后处理我的基础设施资产，并对我感兴趣的日志文件进行了跟踪。但是直到我阅读[Jeff Dimmock](https://twitter.com/bluscreenofjeff)和[Steve Borosh](https://twitter.com/424f424f)写的这篇伟大的[博客文章](https://bluescreenofjeff.com/2017-08-08-attack-infrastructure-log-aggregation-and-monitoring/)之后。我脑子里的一个小声音一直唠叨着要我应该做点什么。

这个博客文章系列将成为建立集中基础设施日志记录、监控和警报的指南。但是这是个非常广泛的话题，我不可能涵盖全部（表示自己很菜），但我还是希望可以给需要的人提供一些帮助。

本系列主要内容：

第1部分：记录服务器设置

第2部分：日志聚合

第3部分：Graylog仪表板101

第4部分：日志事件警报

在本系列的最后，我们最终会打造下图所示的日志记录设置：

[![](https://p5.ssl.qhimg.com/t015fcf90eeb92ecda9.png)](https://p5.ssl.qhimg.com/t015fcf90eeb92ecda9.png)

说实话，常规的渗透测试并不需要太多的精力投资在设置基础设施或日志管理。但是，如果您参与长期（几个月/几年）建立基础架构的项目，那就应该投入更多时间来设置集中式日志记录，我认为有以下原因：

1.监督运营-集中式日志记录可以让你随时查看正在进行的操作：成功的网络钓鱼、有效载荷下载、潜在的事件响应活动、对您的资产的攻击等等。有了这个监督，你就可以立即对事件做出反应，甚至可以调整你的战术。例如，你的日志提醒告诉你，你的有效载荷在过去的8小时内被下载了10次，而你还没有得到一个shell。

2.报告—良好的日志会提高报告的质量。

3.提高便利性和效率——监控来自多个基础设施资产的日志是很痛苦的一件事。配置了定制快速统计和警报可以为我节省了大量时间和精力。

4.问责制——你应该知道并掌握你所负责的任务的相关证明。

5.安全——因为互联网是黑暗和充满恐惧的。蓝色团队正在监视他们的基础设施日志，以了解异常情况和恶意活动的迹象，你为什么不能呢?



## 设置日志记录服务器

Graylog2：

我有几个理由说明为什么不使用PLENTY而使用Graylog2作为集中整个系列博客日志服务器，

1.它是开源的，每天的日志量少于5GB。对于一般的pentester/red teamer来说，这已经足够了。

2.记录功能真的很好。

3.它有很多现成的功能，如果你想要添加功能，它还有很多额外的插件可供选择。

4.它支持Slack警报。

我将演示如何正确设置一个全新的Graylog日志记录服务器。

1.服务器要求：

Graylog有几个条件，我将介绍安装。一个服务器本身，虽然Graylog建立在ElasticSearch之上，仅需要2GB的RAM即可运行。如果你想拥有更好的体验，我建议使用4GB的RAM，Graylog的文档盖了各种操作系统的安装。我将使用

新的Debian 9 系统作为演示。

2.先决条件：

Graylog具有以下依赖关系：

Java（&gt; = 8）

MongoDB（&gt; = 2.4）

Elasticsearch（&gt; = 2.x）

让我们开始安装：<br><code>#Java<br>
sudo apt update &amp;&amp; sudo apt upgrade<br>
sudo apt install apt-transport-https openjdk-8-jre-headless uuid-runtime pwgen</code>

<code>#MongoDB<br>
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2930ADAE8CAF5059EE73BB4B58712A2291FA4AD5<br>
echo "deb http://repo.mongodb.org/apt/debian jessie/mongodb-org/3.6 main" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.6.list<br>
sudo apt-get update &amp;&amp; sudo apt-get install -y dirmngr mongodb-org</code>

注：如果安装MongoDB失败，您可能要安装libssl1.0.0软件包。请将Debian的jessie-backports添加到您的/etc/apt/sources.list中：

<code># Jessie backports<br>
deb http://ftp.debian.org/debian jessie-backports main</code>

或者你可以自己[下载](http://security.debian.org/debian-security/pool/updates/main/o/openssl/)并安装缺失的依赖关系。

下一个依赖安装是ElasticSearch。

`#Elasticsearch`

`wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -<br>`

`echo“deb https://artifacts.elastic.co/packages/5.x/apt stable main”| sudo tee -a /etc/apt/sources.list.d/elastic-5.x.list<br>`

`sudo apt-get update &amp;&amp; sudo apt-get install elasticsearch`

安装ElasticSearch后，您需要修改ElasticSearch配置文件（/etc/elasticsearch/elasticsearch.yml）; 取消注释cluster.name设置并将其命名为graylog。

[![](https://p5.ssl.qhimg.com/t01c099ac10f887827c.png)](https://p5.ssl.qhimg.com/t01c099ac10f887827c.png)

最后，启动所有必需的服务以启动并重新启动。

```sudo systemctl daemon-reload<br>`

`sudo systemctl enable mongod.service elasticsearch.service<br>`

`sudo systemctl restart mongod.service elasticsearch.service`

3.安装Graylog2：

`Graylog提供DEB和RPM包存储库。`<br>`wget https://packages.graylog2.org/repo/packages/graylog-2.4-repository_latest.deb`<br>`sudo dpkg -i graylog-2.4-repository_latest.deb`<br>`sudo apt-get update`<br>`sudo apt-get install graylog-server`

4.配置Graylog2：

所有Graylog的[配置](http://docs.graylog.org/en/2.4/pages/configuration/server.conf.html) 都是从单个文件管理的; /etc/graylog/server/server.conf。在我们登录到Graylog的Web管理页面之前，我们需要更改其中的一些设置。

记住在你要搞事之前，一定要备份配置文件; 因为你永远不知道什么时候需要重新开始。

`sudo cp /etc/graylog/server/server.conf /etc/graylog/server/server.conf.bak`

I）管理员用户名：

你可以更改管理员的用户名，默认是“ admin ”。

`root_username = admin`

II）密码：

您必须为密码设置密钥。如果没有设置，Graylog将拒绝启动。但这不是你的登录密码。

首先，使用pwgen实用程序生成加密密码（至少64个字符长）：

`pwgen -N 1 -s 96`

将整个字符串粘贴到password_secret设置中：

`password_secret = GENERATED_SECRET`

III）root密码的sha2：

接下来，您需要生成密码的SHA2哈希值，您将在首次登录到Graylog的Web界面时使用该密码。您可以在首次登录后从仪表板更改它。

生成管理员帐户密码的SHA2哈希值：

`echo -n yourpassword | sha256sum`

将散列粘贴到 root_password_sha2设置中：<br>`root_password_sha2 = PASSWORD_HASH`

IV ）网络侦听端口：

最后，如果您想使用默认9000以外的任何其他端口，则应启用Web界面并更改其侦听端口。取消注释以下行并更改它们以匹配您希望可以访问的任何端口Graylog的Web界面：

`rest_listen_uri = http://0.0.0.0:9000/api/<br>`

`web_listen_uri = http://0.0.0.0:9000/api/`

然后，您只需启用并重新启动Graylog服务即可。

<code>sudo systemctl daemon-reload<br>
sudo systemctl enable graylog-server.service<br>
sudo service graylog-server restart</code>登录到您的Web管理界面`http：// [IP_ADDRESS]：9000 /`

[![](https://p5.ssl.qhimg.com/t017f38869e4ce1735a.png)](https://p5.ssl.qhimg.com/t017f38869e4ce1735a.png)

重要提示： 下一步是可选的，但我建议不要跳过它。Graylog的Web界面和REST API默认使用HTTP，这意味着您的密码和其他敏感数据以明文形式发送。下一步包括为您的Graylog安装生成并添加自签名HTTPS证书。

IV）安装自签名证书：

创建一个文件夹来管理你的证书到它：

`sudo mkdir / etc / graylog / server / ssl<br>`

`cd / etc / graylog / server / ssl`

在其中创建文件“ openssl-graylog.cnf ”并填写下面的内容; 定制它以满足您的需求：

`[req]<br>`

`distinguished_name = req_distinguished_name<br>`

`x509_extensions = v3_req<br>`

`prompt = no`

`＃有关证书颁发者的详细信息<br>`

`[req_distinguished_name]<br>`

`C = US<br>`

`ST = NY<br>`

`L = NY<br>`

`O = Graylog<br>`

`OU = Graylog<br>`

`CN = logger.graylog.com`

`[v3_req]<br>`

`keyUsage = keyEncipherment，dataEncipherment<br>`

`extendedKeyUsage = serverAuth<br>`

`subjectAltName = [@alt_names](https://github.com/alt_names)`

`＃证书应包含的IP地址和DNS名称＃IP 地址和DNS的`<br>`IP地址### DNS名称的`<br><code>###，“###”是连续的数。<br>
[alt_names]<br>
IP.1 = 127.0.0.1<br>
DNS.1 = logger.graylog.com</code>

`注： 请确保将配置文件中的'IP.1 = 127.0.0.1'值更改为Graylog服务器的IP地址。`

创建一个PKCS＃5私钥（PKCS5-plain.pem）和X.509证书（graylog。CRT）：

`sudo openssl req -x509 -days 365 -nodes -newkey rsa：2048 -config openssl-graylog.cnf -keyout pkcs5-plain.pem -out graylog.crt`

将您的PKCS＃5私钥到未加密的 PKCS＃8私钥（graylog。键）：

`sudo openssl pkcs8 -in pkcs5-plain.pem -topk8 -nocrypt -out graylog.key`

当使用HTTPS的Graylog REST API，X.509证书（graylog，CRT在这种情况下） 必须信任由JVM信任存储，否则通信将失败。由于我们不想与官方信任存储库混淆，因此我们将制作一份与我们的Graylog证书一起使用的副本。

<code>sudo cp -a / usr / lib / jvm / java-8-openjdk-amd64 / jre / lib / security / cacerts / etc / graylog / server / ssl /<br>
sudo keytool -importcert -keystore / etc / graylog / server / ssl / cacerts -storepass changeit -alias graylog-self-signed -file /etc/graylog/server/ssl/graylog.crt</code>

证书现在应该可以使用了。编辑Graylog的配置文件（/etc/graylog/server/server.conf）并找到并更改下面的设置：

`#REST API设置<br>`

`rest_enable_tls = true<br>`

`rest_tls_cert_file = /etc/graylog/server/ssl/graylog.crt<br>`

`rest_tls_key_file = /etc/graylog/server/ssl/graylog.key`

`#Web界面设置`

``<code><br>
web_enable_tls = true<br></code>

`web_tls_cert_file = / etc / graylog / server /ssl/graylog.crt<br>`

`web_tls_key_file = /etc/graylog/server/ssl/graylog.key`

注：对于运行Graylog进程的系统用户，证书和密钥文件需要可读（644权限对两个文件均可正常工作）。

我们完成了！只需重新启动Graylog，并且您应该能够通过`https：// [IP_ADDRESS]登录到您的管理控制台：9000 /`

`sudo service graylog-server restart`

[![](https://p2.ssl.qhimg.com/t010ceba23dbee45ea1.png)](https://p2.ssl.qhimg.com/t010ceba23dbee45ea1.png)

如果您有任何登录问题，请参阅Graylog2的HTTPS安装[文档](http://docs.graylog.org/en/2.4/pages/configuration/https.html)和Graylog的日志文件（/var/log/graylog-server/server.log）以进行故障排除。

自动化：

如果您完整安装一遍，会发现安装Graylog可能有点麻烦，所以我编写了一个[脚本](https://github.com/V1V1/Graylog-Setup)来自动执行上述所有安装步骤。

[![](https://p3.ssl.qhimg.com/t01a260dab80c7c76a9.png)](https://p3.ssl.qhimg.com/t01a260dab80c7c76a9.png)<br>[![](https://p0.ssl.qhimg.com/t01cbfcbcd9fcb2432f.png)](https://p0.ssl.qhimg.com/t01cbfcbcd9fcb2432f.png)<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t016e608df0fb813b2f.png)

保护Graylog：

您应该了解将来自攻击基础架构的所有日志集中在一个地方的风险。您聚合的日志越多，日志服务器携带的风险就越高; 一个妥协可能会暴露你的整个操作。

下表显示了Graylog的默认侦听端口：[![](https://p5.ssl.qhimg.com/t01ce67a88bc24e8f63.png)](https://p5.ssl.qhimg.com/t01ce67a88bc24e8f63.png)

一些简单的防火墙规则可以保护您的Graylog安装，特别是如果您使用VPN服务器来控制对攻击基础架构的管理端口的访问时，可以发挥很大的作用。

以下是一些iptables规则示例，您可以将其应用于您的Graylog服务器以限制其攻击面。

`＃默认策略`

``<code><br>
-P INPUT DROP</code>

``<code><br>
-P FORWARD DROP<br></code>

`-P OUTPUT ACCEPT`

`＃允许建立连接<br>`

`-A INPUT -m状态--state RELATED，ESTABLISHED -j ACCEPT`

`＃允许来自本地环回接口的流量`

``<code><br>
-A INPUT -i lo - j ACCEPT</code>

`＃仅允许来自特定IP地址的SSH连接，例如VPN`

``<code><br>
-A INPUT -s [ VPN_IP_ADDRESS ] / 32 -p tcp -m tcp --dport 22 -j ACCEPT</code>

`＃仅允许从特定IP地址连接到Graylog管理，例如VPN`

``<code><br>
-A INPUT -s [ VPN_IP_ADDRESS ] / 32 -p tcp -m tcp --dport 9000 -j ACCEPT</code>

`＃仅允许来自攻击基础架构资产的Rsyslog通信（1行每个资产）`

````<code><br>
-A INPUT -s [ ASSET_IP_ADDRESS ] / 32 -p tcp -m tcp --dport 5140 -j ACCEPT</code>

``<code><br>
-A INPUT -s [ ASSET_IP_ADDRESS] / 32 -p tcp -m tcp --dport 5140 -j ACCEPT</code>

``<code><br>
-A INPUT -s [ ASSET_IP_ADDRESS ] / 32 -p tcp -m tcp --dport 5140 -j ACCEPT</code>

``<code><br>
-A INPUT -s [ ASSET_IP_ADDRESS ] / 32 - p tcp -m tcp --dport 5140 -j ACCEPT</code>

注意：上述规则集的最后一部分将在下一篇文章中详细介绍。

<a class="reference-link" name="%E7%BB%93%E8%AE%BA%EF%BC%9A"></a>**结论：**

我们的日志记录服务器已启动并正在运行，下一篇文章将介绍如何从各种基础架构资产中设置日志的汇总。



## 参考文献

[https://github.com/bluscreenofjeff/Red-Team-Infrastructure-Wiki](https://github.com/bluscreenofjeff/Red-Team-Infrastructure-Wiki)

[https://bluescreenofjeff.com/2017-08-08-attack-infrastructure-log-aggregation-and-monitoring/](https://bluescreenofjeff.com/2017-08-08-attack-infrastructure-log-aggregation-and-monitoring/)

[https://www.contextis.com/blog/logging-like-a-lumberjack](https://www.contextis.com/blog/logging-like-a-lumberjack)

[http://docs.graylog.org/en/2.4/index.html](http://docs.graylog.org/en/2.4/index.html)

[http://docs.graylog.org/en/2.4/pages/configuration/server.conf.html](http://docs.graylog.org/en/2.4/pages/configuration/server.conf.html)

[http://docs.graylog.org/en/2.4/pages/configuration/file_location.html#default-file-location](http://docs.graylog.org/en/2.4/pages/configuration/file_location.html#default-file-location)

[https://ashleyhindle.com/how-to-setup-graylog2-and-get-logs-into-it/](https://ashleyhindle.com/how-to-setup-graylog2-and-get-logs-into-it/)

[https://dodizzle.wordpress.com/2011/10/14/3-ways-to-push-data-to-graylog2/](https://dodizzle.wordpress.com/2011/10/14/3-ways-to-push-data-to-graylog2/)

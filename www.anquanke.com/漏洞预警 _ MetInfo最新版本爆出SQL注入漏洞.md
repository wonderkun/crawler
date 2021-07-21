> 原文链接: https://www.anquanke.com//post/id/161988 


# 漏洞预警 | MetInfo最新版本爆出SQL注入漏洞


                                阅读量   
                                **179449**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">3</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t01ae80fe03a67e5a87.png)](https://p2.ssl.qhimg.com/t01ae80fe03a67e5a87.png)

> 2018年10月初，白帽汇安全研究院监测到网络上出现了最新MetInfo的sql注入漏洞。该漏洞是由于攻击者可以绕过MetInfo的过滤sql注入恶意代码的函数，使得攻击者在前台就可以通过index.php页面的参数id进行SQL注入，并且直接获得管理员数据，接管整个CMS。
MetInfo是中国知名的企业建站软件，在中国的活跃使用量数以万计，一旦有高危漏洞爆出，势必会影响各行各业众多网站。而且此次爆出漏洞的版本是官网在9月26日所发布的最新版，预计会在下一次补丁出来之前对所有使用该模板的网站造成不小的影响。而且据该漏洞的作者声明，此次漏洞之所以在官网补丁出来之前发布是因为作者在几个版本前就向该建站系统厂商反馈，但漏洞并未得到修复，所以公布与众，督促厂商修复。我们推测，以前的多个版本均有很大概率也存在该漏洞，预计在未来的很长一段时间，所有基于MetInfo的网站都将受到不小的安全威胁。

[![](https://nosec.org/avatar/uploads/attach/image/c44ae10b1783bd6ca758dbeab83fbe9f/1111.png)](https://nosec.org/avatar/uploads/attach/image/c44ae10b1783bd6ca758dbeab83fbe9f/1111.png)

[![](https://nosec.org/avatar/uploads/attach/image/5a18aa10b183f1462d8abd44308eb140/2222.png)](https://nosec.org/avatar/uploads/attach/image/5a18aa10b183f1462d8abd44308eb140/2222.png)

各行各业的网站都有使用MetInfo的痕迹

MetInfo建站系统虽然推出时间很长，但由于PHP较强的灵活性以及其他安全原因，从诞生之初就不断爆出各种高危漏洞，包括注入，任意文件读取和写入，SSRF等。而此次漏洞的爆发也意外发现了厂商较慢的漏洞修复速度，因此，在以后也许会有更多高危漏洞继续爆出。

[![](https://nosec.org/avatar/uploads/attach/image/e59f5ec986155b0bf2158cfeab063526/eee.png)](https://nosec.org/avatar/uploads/attach/image/e59f5ec986155b0bf2158cfeab063526/eee.png)

FOFA历来的部分POC



## 概况

MetInfo企业建站系统采用了开源的PHP+Mysql架构，第一个版本于2009年发布，目前最新的版本是V6.1.2，更新于 2018年9月26 日。MetInfo是一款功能全面、使用简单的企业建站软件。用户可以在不需要任何编程的基础上，通过简单的安装和可视化编辑设置就能够在互联网搭建独立的企业网站，能够极大的降低企业建站成本。目前国内各行业网站均有MetInfo的身影。

目前FOFA系统最新数据（一年内数据）显示全球范围内共有10745个基于Metinfo搭建的网站。中国使用数量最多，共有7098台，中国香港第二，共有2028台，美国第三，共有1312台，日本第四，共有73台，中国台湾第五，共有50台。白帽汇安全研究院抽样检测发现全球存在该SQL漏洞的比例为百分之1。值得一提的是，网上还有很多基于MetInfo改造的网站也受到潜在威胁

[![](https://nosec.org/avatar/uploads/attach/image/926628b8698413156adef68b2f086411/4444.png)](https://nosec.org/avatar/uploads/attach/image/926628b8698413156adef68b2f086411/4444.png)

全球范围内MetInfo建站分布情况（仅为分布情况，非漏洞影响情况）

中国地区中浙江省使用用数量最多，共有3542台；北京市第二，共有1562台，广东省第三，共有382台，河南省第四，共有322台，四川省第五，共有271台。

[![](https://nosec.org/avatar/uploads/attach/image/2bff667749f828dc22f28ef49ffcd9c5/5555.png)](https://nosec.org/avatar/uploads/attach/image/2bff667749f828dc22f28ef49ffcd9c5/5555.png)

中国地区MetInfo建站分布情况（仅为分布情况，非漏洞影响情况）



## 危害等级



## 漏洞原理

CNVD-2018-20024

漏洞原因在于文件/app/system/message/web/message.class.php中的sql语句 select * from `{`$M[table][config]`}` where lang =’`{`$M[form][lang]`}`’ and name= ‘met_fdok’ and columnid = `{`$M[form][id]`}`

[![](https://nosec.org/avatar/uploads/attach/image/b3bec6b3aef74a52f84a6becb0eff9dc/1234.png)](https://nosec.org/avatar/uploads/attach/image/b3bec6b3aef74a52f84a6becb0eff9dc/1234.png)

漏洞涉及的语句

由于无单引号，所以貌似可以sql注入。但是由于 INADMIN 常量没有定义，导致 sqlinsert 函数把用户输入敏感字符通通删除掉。于是，最后利用 index.php 页面的 domessage 方法定义 INADMIN 常量，使得用户输入可以绕过sql注入过滤函数，成功进行注入。

[![](https://nosec.org/avatar/uploads/attach/image/cb713eafe9c41a10003925761118be7d/3456.png)](https://nosec.org/avatar/uploads/attach/image/cb713eafe9c41a10003925761118be7d/3456.png)

需要绕过过滤函数

[![](https://nosec.org/avatar/uploads/attach/image/deaf3567b2644febf21104c02183076c/2345.png)](https://nosec.org/avatar/uploads/attach/image/deaf3567b2644febf21104c02183076c/2345.png)

domessage函数定义常量

[![](https://nosec.org/avatar/uploads/attach/image/18698f7943f41c25d8dfa4090864dbbc/bbb.png)](https://nosec.org/avatar/uploads/attach/image/18698f7943f41c25d8dfa4090864dbbc/bbb.png)

抽样发现外网的某台机器存在漏洞，可以得到数据库详细信息

[![](https://nosec.org/avatar/uploads/attach/image/6e684071c3d2a8850fc0a36c336b6687/aaa.png)](https://nosec.org/avatar/uploads/attach/image/6e684071c3d2a8850fc0a36c336b6687/aaa.png)

进一步探测，发现管理员敏感数据



## 漏洞影响

目前漏洞影响版本号包括：



## 影响范围

结合FOFA系统，白帽汇安全研究院抽样检测发现全球存在CNVD-2018-20024漏洞的比例为百分之1，影响最严重的是中国。



## 漏洞POC

目前FOFA客户端平台已经更新CNVD-2018-20024检测POC。

[![](https://nosec.org/avatar/uploads/attach/image/f0ae32846e360ddad61491a66c01be62/3333.png)](https://nosec.org/avatar/uploads/attach/image/f0ae32846e360ddad61491a66c01be62/3333.png)

CNVD-2018-20024 POC截图



## CNVD编号



## 修复建议

1、最新补丁在官网还未发布，建议用户把有问题的功能代码删除。

2、在补丁发布之前下线网站。官网地址：[https://www.metinfo.cn/download/](https://www.metinfo.cn/download/)

白帽汇会持续对该漏洞进行跟进。后续可以持续关注链接[https://nosec.org/home/detail/1889.html](https://nosec.org/home/detail/1705.html)。



## 参考

[1] [https://bbs.ichunqiu.com/thread-46687-1-1.html](https://bbs.ichunqiu.com/thread-46687-1-1.html)

[2] [http://www.cnvd.org.cn](http://www.cnvd.org.cn)

白帽汇从事信息安全，专注于安全大数据、企业威胁情报。

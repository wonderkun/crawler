
# 【漏洞预警】Fastjson 远程代码执行漏洞(暂无PoC)


                                阅读量   
                                **157422**
                            
                        |
                        
                                                                                    



**[![](./img/85713/t01c51245434a50f900.jpg)](./img/85713/t01c51245434a50f900.jpg)**

**Fastjson简介**

Fastjson是一个Java语言编写的高性能功能完善的JSON库。它采用一种“假定有序快速匹配”的算法，把JSON Parse的性能提升到极致，是目前Java语言中最快的JSON库。Fastjson接口简单易用，已经被广泛使用在缓存序列化、协议交互、Web输出、Android客户端等多种应用场景。

**<br>**

**漏洞概要**

2017年3月15日，Fastjson 官方发布安全公告，该公告介绍fastjson在1.2.24以及之前版本存在代码执行漏洞代码执行漏洞，恶意攻击者可利用此漏洞进行远程代码执行，从而进一步入侵服务器，目前官方已经发布了最新版本，最新版本已经成功修复该漏洞。 

<br>

**漏洞详情**

**漏洞编号: **暂无 

**漏洞名称:**** **Fastjson远程代码执行漏洞 

**官方评级:** 高危 

**漏洞描述: **

fastjson在1.2.24以及之前版本存在代码执行漏洞，当用户提交一个精心构造的恶意的序列化数据到服务器端时，fastjson在反序列化时存在漏洞，可导致远程任意代码执行漏洞。 

**漏洞利用条件和方式: **

黑客可以远程代码执行成功利用该漏洞。 

**漏洞影响范围: **

1.2.24及之前版本 

**<br>**

**漏洞检测**

检查fastjson 版本是否在1.2.24版本内

```
ps aux | grep fastjson
```



**POC**

暂无****

<br>

**WAF检测办法**

检测post内容中是否包含如下字符

```
"@type"
```



**漏洞修复建议(或缓解措施)**

目前官方已经发布了最新版本，该版本已经成功修复该漏洞。 

阿里云上用户建议采用以下两种方式将fastjson升级到1.2.28或者更新版本： 

更新方法如下： 

**1.Maven 依赖配置更新**

通过 maven 配置更新，使用最新版本，如下： 



```
&lt;dependency&gt;
    &lt;groupId&gt;com.alibaba&lt;/groupId&gt;
    &lt;artifactId&gt;fastjson&lt;/artifactId&gt;
    &lt;version&gt;1.2.28&lt;/version&gt;
&lt;/dependency&gt;
```

**2.最新版本下载**

下载地址：[http://repo1.maven.org/maven2/com/alibaba/fastjson/1.2.28/](http://repo1.maven.org/maven2/com/alibaba/fastjson/1.2.28/)    



**3.云盾WAF防护**

如果您无法及时升级fastjson，您可以选用[阿里云云盾WAF](https://common-buy.aliyun.com/?spm=5176.bbsr309931.0.0.JVViAV&amp;commodityCode=waf#/buy)自动防护。 

<br>

**情报来源**

[https://github.com/alibaba/fastjson/wiki/security_update_20170315](https://github.com/alibaba/fastjson/wiki/security_update_20170315) 

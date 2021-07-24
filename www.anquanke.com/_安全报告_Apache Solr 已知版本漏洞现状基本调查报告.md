> 原文链接: https://www.anquanke.com//post/id/87079 


# 【安全报告】Apache Solr 已知版本漏洞现状基本调查报告


                                阅读量   
                                **138975**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01cee8426a343f2c1f.png)](https://p1.ssl.qhimg.com/t01cee8426a343f2c1f.png)



**0x00 背景介绍**



Apache Solr 是一种可供企业使用的、基于 Lucene 的搜索服务器。 该产品于 2017 年 10 月被爆出存在严重的 XXE 和 RCE 漏洞,攻击者可以使 用这些漏洞来读取服务器任意文件,甚至进行远程命令执行。这将给被攻击站点造成严重危害。

[![](https://p1.ssl.qhimg.com/t01be6c24d519f177b4.png)](https://p1.ssl.qhimg.com/t01be6c24d519f177b4.png)



**0x01 全网扫描数据分析**



360 CERT 根据已知的 Apache Solr 漏洞, 编写了针对各个版本的漏洞检 测脚本,并对全网进行了针对性扫描(主要针对默认端口 8983),发现全网存 在大量受已知漏洞影响的站点。具体分布情况如下:

**1、全球范围分布情况**

通过全网检测的结果,发现当前公网上存在受已知漏洞影响的 Solr 总数为9626,在全球的分布状况如下:

[![](https://p0.ssl.qhimg.com/t019cf7e81fd5a5bfcb.png)](https://p0.ssl.qhimg.com/t019cf7e81fd5a5bfcb.png)

受影响的前十个国家占比情况如下：

[![](https://p5.ssl.qhimg.com/t01850b40fd836b7bee.png)](https://p5.ssl.qhimg.com/t01850b40fd836b7bee.png)

**2、全国范围分布情况**

通过全网检测的结果，可以看到当前国内公网上存在Solr各个漏洞的总数为1685，在全国的分布状况如下：



[![](https://p3.ssl.qhimg.com/t019a030eac9148d9a7.png)](https://p3.ssl.qhimg.com/t019a030eac9148d9a7.png)

前15个受影响省份的数量统计如下表：

[![](https://p5.ssl.qhimg.com/t017154994d6b103c55.png)](https://p5.ssl.qhimg.com/t017154994d6b103c55.png)

存在漏洞的站点中，前十个省份的占比情况如下图：

[![](https://p1.ssl.qhimg.com/t0168f41c14cb2296e5.png)](https://p1.ssl.qhimg.com/t0168f41c14cb2296e5.png)

存在漏洞的站点中，前十个城市的占比情况如下图：

[![](https://p4.ssl.qhimg.com/t015ea98edc827dae7c.png)](https://p4.ssl.qhimg.com/t015ea98edc827dae7c.png)

**3、Solr各版本漏洞数量、比例**

360CERT针对全网的检测中涉及的漏洞主要有：

**1.   未授权访问漏洞**

**2.   CVE-2017-12629中的RCE漏洞（通过版本号评估）**

在所有未授权访问漏洞中，排名前十个的Solr版本比例如下：

[![](https://p5.ssl.qhimg.com/t01def6eb7e92d7db92.png)](https://p5.ssl.qhimg.com/t01def6eb7e92d7db92.png)

其中数量前十位的版本号情况如下：

[![](https://p0.ssl.qhimg.com/t016f996289b9374198.png)](https://p0.ssl.qhimg.com/t016f996289b9374198.png)

通过版本比例可以预估，全网可能包含的RCE漏洞总数为4124：

比例图如下：

[![](https://p1.ssl.qhimg.com/t0185f38c46d8f48dd1.png)](https://p1.ssl.qhimg.com/t0185f38c46d8f48dd1.png)

本次RCE&amp;&amp;XXE漏洞影响Solr的版本广泛，通过上述信息可以看出全网有相当数量的Solr站点将可能受到影响。

**4、存在漏洞的站点（部分列表）**

中国存在未授权访问漏洞扫描结果总数为：1685，下表为其中部分站点：

[![](https://p4.ssl.qhimg.com/t0177c7d558bb7532db.png)](https://p4.ssl.qhimg.com/t0177c7d558bb7532db.png)



**0x02 时间线**



2017-10-20        360CERT完成Solr XXE&amp;&amp;RCE漏洞初步分析

2017-10-21        360CERT完成Solr XXE&amp;&amp;RCE漏洞详细分析

2017-10-24        360CERT完成全网范围分析报告



**0x03 参考文档**



[https://www.exploit-db.com/exploits/43009/](https://www.exploit-db.com/exploits/43009/)

[http://seclists.org/oss-sec/2017/q4/105](http://seclists.org/oss-sec/2017/q4/105)

[https://wiki.apache.org/solr/SolrSecurity](https://wiki.apache.org/solr/SolrSecurity)

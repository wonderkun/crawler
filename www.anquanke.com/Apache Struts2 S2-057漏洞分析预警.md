> 原文链接: https://www.anquanke.com//post/id/157518 


# Apache Struts2 S2-057漏洞分析预警


                                阅读量   
                                **255307**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p0.ssl.qhimg.com/t01293754e765a9072b.png)](https://p0.ssl.qhimg.com/t01293754e765a9072b.png)

## 0x00 漏洞描述

It is possible to perform a RCE attack when namespace value isn’t set for a result defined in underlying xml configurations and in same time, its upper action(s) configurations have no or wildcard namespace. Same possibility when using url tag which doesn’t have value and action set and in same time, its upper action(s) configurations have no or wildcard namespace. —— Apache Struts2 Team

2018年8月23日，Apache Strust2发布最新安全公告，Apache Struts2 存在远程代码执行的高危漏洞，该漏洞由Semmle Security Research team的安全研究员汇报，漏洞编号为CVE-2018-11776（S2-057）。Struts2在XML配置中如果namespace值未设置且（Action Configuration）中未设置或用通配符namespace时可能会导致远程代码执行。



## 0x01 漏洞影响面

#### 影响面

确定CVE-2018-11776为高危漏洞。

实际场景中存在一定局限性，需要满足一定条件。

#### 影响版本

Struts 2.3 to 2.3.34

Struts 2.5 to 2.5.16

#### 修复版本

Struts 2.3.35

Struts 2.5.17



## 0x02 漏洞验证

[![](https://p403.ssl.qhimgs4.com/t0149d0452d1a415075.png)](https://p403.ssl.qhimgs4.com/t0149d0452d1a415075.png)

传入OGNL表达式$`{`2333+2333`}`

[![](https://p403.ssl.qhimgs4.com/t01ef09ac435deedccb.png)](https://p403.ssl.qhimgs4.com/t01ef09ac435deedccb.png)

成功带入执行函数，并执行

[![](https://p403.ssl.qhimgs4.com/t01c78814d630059c3a.png)](https://p403.ssl.qhimgs4.com/t01c78814d630059c3a.png)

返回结果至URL



## 0x03 修复建议

官方建议升级Struts到2.3.35版本或2.5.17版本

该版本更新不存在兼容性问题



## 0x04 时间线

**2018-08-22** 漏洞披露

**2018-08-22** 360CERT发布预警分析通告



## 0x05 参考链接
1. [Apache Struts2 安全通告](https://cwiki.apache.org/confluence/display/WW/S2-057)
1. [lgtm团队blog](https://lgtm.com/blog/apache_struts_CVE-2018-11776)
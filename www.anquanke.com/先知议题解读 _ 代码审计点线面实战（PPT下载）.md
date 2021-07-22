> 原文链接: https://www.anquanke.com//post/id/149081 


# 先知议题解读 | 代码审计点线面实战（PPT下载）


                                阅读量   
                                **132578**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t010bfd179761b011e3.jpg)](https://p4.ssl.qhimg.com/t010bfd179761b011e3.jpg)

** 议题PPT：[ https://yunpan.360.cn/surl_ycpMnJEvJAt](https://yunpan.360.cn/surl_ycpMnJEvJAt) （提取码：7e92） **

## 议题概述

随着各个企业对安全的重视程度越来越深，安全思维已经从原来的表面工程逐渐转变为“开膛破肚”的内部工程，特别是在金融领域受重视的成都比较高，不区分语言，工程化的人工审计是未来几年的趋势，代码审计的分解和实战成为安全工作者必须掌握的一种能力，从代码审计的各个要记点，和代码审计流程框架，以及代码审计面临的问题，逐一拆解分析。



## 安全代码审计

这里主要针对owasp-top10里面，漏洞近年来爆发最高的三类进行讲解，分别为，sql注入，序列化，xml实体注入

### 普通的注入

注解：通常是没有走框架调用，通过字符串拼接的方式编写的查询语句，这样就会造成注入[![](https://p3.ssl.qhimg.com/t0173e7fc0b1b16a979.png)](https://p3.ssl.qhimg.com/t0173e7fc0b1b16a979.png)

当nodeid为1

完整的语句是:

select * from typestruct where nodeid in(1)

当nodeid为1) union select 1,2,3…….from table where 1=(1

完整的语句是:

select * from typestruct where nodeid in(1) union select 1,2,3…….from table where1=(1)

### 框架类型注入

注解：通常是没有明白框架调用的用法，错误的造成了字符串拼接，导致了注入[![](https://p2.ssl.qhimg.com/t01e2cf1cdb434728ae.png)](https://p2.ssl.qhimg.com/t01e2cf1cdb434728ae.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01cfc8b8cfa61d78ee.png)

假设id为1234，当orgCode为1

完整的语句是:

select ar.role_id, ar.role_name, ar.role_desc,’1′ as co_code, ‘1’ as org_code, CREATOR from as_role ar where ar.role_id = 1

当nodeid为1’||(case when 1=1 then ” else ‘a’ end)||’

完整的语句是:

select ar.role_id, ar.role_name, ar.role_desc,’1′ as co_code, ‘1’||(case when 1=1 then ” else ‘a’end)||”as org_code, CREATOR from as_role ar where ar.role_id = 1

### ORM类型注入

注解：通常指的是类似hibernate一类具有安全语法检测的注入[![](https://p5.ssl.qhimg.com/dm/1024_401_/t01eec689d5157f9e89.png)](https://p5.ssl.qhimg.com/dm/1024_401_/t01eec689d5157f9e89.png)

[![](https://p1.ssl.qhimg.com/dm/1024_407_/t019640cd5237b66090.png)](https://p1.ssl.qhimg.com/dm/1024_407_/t019640cd5237b66090.png)

总体上来说，sql注入离不开这三大类，小伙伴们有时候在众测时候，会遇到厂商说取出来一个user不行，必须数据全能跑出来才算，这时候可以根据上面的描述，如果你运气够好，可能就造成任意语句执行

### 序列化漏洞

在序列化代码审计中，重点提出来内网渗透中SOAPMonitor的成因

[![](https://p3.ssl.qhimg.com/dm/1024_563_/t01a999fad69f0ca035.png)](https://p3.ssl.qhimg.com/dm/1024_563_/t01a999fad69f0ca035.png)

### XML实体注入

重点提出来某知名应用程序的一个漏洞

[![](https://p5.ssl.qhimg.com/dm/1024_565_/t012cca2c86258ce09e.png)](https://p5.ssl.qhimg.com/dm/1024_565_/t012cca2c86258ce09e.png)

通过dwr接口，暴露出来对xml的解析，没有禁用实体，而且如果payload中位于string标签内的还会被回显回来

[![](https://p4.ssl.qhimg.com/dm/1024_350_/t01af97dbbd650e880a.png)](https://p4.ssl.qhimg.com/dm/1024_350_/t01af97dbbd650e880a.png)



## 框架流程分析

这里重点介绍了普元EOS的分析流程，安全概要，包括两大类，反序列化和XML实体注入

流程分析详见ppt，这里只展示请求效果图
1. 反序列化
[![](https://p1.ssl.qhimg.com/t01e727f0b8167121f6.png)](https://p1.ssl.qhimg.com/t01e727f0b8167121f6.png)
1. XML实体注入
[![](https://p2.ssl.qhimg.com/dm/1024_562_/t0137689cffeb7d6a71.png)](https://p2.ssl.qhimg.com/dm/1024_562_/t0137689cffeb7d6a71.png)



## 三方应用笔记

随着语言体系的越发灵活，第三方开发库也随之越来越多，每一种语言都有自己固定的坑，如何正确规范安全的开发将会是重中之重，所以开发时候我们尽量的要对这些第三方东西做安全审计

### XML解析库

拿java举例子，统计了使用量最多的9类xml解析库，均存在安全问题

这里主要指的是xxe，开发者应该在调用这些库的时候，要么通过api禁用外部实体引用，要么就从参数入口处进行过滤

[![](https://p2.ssl.qhimg.com/t010e2c8bdbc3512fa5.png)](https://p2.ssl.qhimg.com/t010e2c8bdbc3512fa5.png)

### 反序列化库[![](https://p2.ssl.qhimg.com/dm/1024_344_/t0103d37174f1f780c2.png)](https://p2.ssl.qhimg.com/dm/1024_344_/t0103d37174f1f780c2.png)

### 各种漏洞的jar包[![](https://p2.ssl.qhimg.com/dm/1024_372_/t0172bbece2b886ce82.png)](https://p2.ssl.qhimg.com/dm/1024_372_/t0172bbece2b886ce82.png)

这里面重点提出来两个jar，比如cos.jar，里面就存在上传坑，如果开发人员不知道，他默认的临时文件存储就会在web目录下，最后采用时间竞争机制getshell，还有就是dd-plist.jar，大部分人是用这个去解析json的，但是它内置了xml的解析，只是判断了content-type和传递的数据是否是xml开头的，这样流入到最终逻辑造成xxe攻击

### CVE相关调用的坑

这里列出来的相关框架，或者开发语言，都被cve报过，所以开发时候要特别注意，其中反序列化比如weblogic，开发框架比如thinkphp等等

[![](https://p0.ssl.qhimg.com/dm/1024_382_/t0116fb6cfc7b9eaa6b.png)](https://p0.ssl.qhimg.com/dm/1024_382_/t0116fb6cfc7b9eaa6b.png)



## 接口滥用要记

这里主要讲了java应用中的四大接口webservice，dwr，hessian，gwt，从他们的默认配置，到内置漏洞，算是一个总结笔记

四大webservice默认配置，众测可以通过这些进行猜测：[![](https://p4.ssl.qhimg.com/dm/1024_602_/t016470fd863e7ba24a.png)](https://p4.ssl.qhimg.com/dm/1024_602_/t016470fd863e7ba24a.png)

axis2里面jws文件构建webservice：
1. 在web目录全局查找jws结尾的文件
1. 根据对应的web访问目录通过浏览器进行访问
1. 对其相应的接口进行审计
axis2低版本cve在通用程序上：[![](https://p4.ssl.qhimg.com/t01890b5542be749c15.png)](https://p4.ssl.qhimg.com/t01890b5542be749c15.png)

xfire容器截至最后一个版本XXE漏洞：[![](https://p5.ssl.qhimg.com/t01785bfd5938e4c4ea.png)](https://p5.ssl.qhimg.com/t01785bfd5938e4c4ea.png)

dwr调用从web.xml到dwr.xml讲解了这个请求的构造包的组成：[![](https://p2.ssl.qhimg.com/t01647221aa3c889e50.png)](https://p2.ssl.qhimg.com/t01647221aa3c889e50.png)

hessian接口从一个不可能的测试，转变为一个简单的渗透测试，组成包如下：[![](https://p2.ssl.qhimg.com/dm/1024_540_/t011f139ddd012287e3.png)](https://p2.ssl.qhimg.com/dm/1024_540_/t011f139ddd012287e3.png)

gwt接口 在审计中的包结构和审计对应方法，从web.xml开始：[![](https://p1.ssl.qhimg.com/dm/1024_374_/t0135a30e4b227fe2b7.png)](https://p1.ssl.qhimg.com/dm/1024_374_/t0135a30e4b227fe2b7.png)



## 关于我们

搜索微信公众号“敏信安全课堂”，作者每个月会持续更新[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/dm/1024_575_/t01b60084afc54eb8dd.png)

议题PPT：[ https://yunpan.360.cn/surl_ycpMnJEvJAt](https://yunpan.360.cn/surl_ycpMnJEvJAt) （提取码：7e92）

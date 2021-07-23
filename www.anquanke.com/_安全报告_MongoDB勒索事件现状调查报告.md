> 原文链接: https://www.anquanke.com//post/id/86441 


# 【安全报告】MongoDB勒索事件现状调查报告


                                阅读量   
                                **103237**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t0113b14f408ee60e19.png)](https://p0.ssl.qhimg.com/t0113b14f408ee60e19.png)



**01事件背景**

2016年底至2017年初，互联网爆发了针对MongoDB的勒索事件，国内外新闻都有大范围的报道。

黑客利用了Mongodb未授权访问漏洞，批量的对可操作的数据库进行了“删库”操作，并留下自己的联系方式，以此要挟用户使用比特币支付赎金换回数据。

相关报道如下：

[http://www.top-news.top/news-12640670.html](http://www.top-news.top/news-12640670.html)

[https://www.toppn.com/view/184696.html](https://www.toppn.com/view/184696.html)



**02调查的起因**

近日360CERT通过在外部署的探针发现，某C段地址的27017端口短时间内被大量扫描。360CERT遂立即对该事件进行跟进，发现该C段地址有数台存在未授权访问的Mongodb服务器。

通过初步检测发现该C段Mongodb服务器发现均存在名为“WRITE_ME”、“REQUEST_YOUR_DATA”、“CONTACTME”等数据库 （如图1，图2，图3）。

通过数据库内留下的信息判断，黑客将用户数据删除后索要0.1至1个比特币。

[![](https://p4.ssl.qhimg.com/t012bb16e281cd35bca.png)](https://p4.ssl.qhimg.com/t012bb16e281cd35bca.png)

图1:勒索者留下的数据库“WRITE_ME”

[![](https://p3.ssl.qhimg.com/t016ccfdab7399b7415.png)](https://p3.ssl.qhimg.com/t016ccfdab7399b7415.png)

图2:勒索者留下的数据库“REQUEST_YOUR_DATE”

[![](https://p5.ssl.qhimg.com/t0131e58a7c4bef1703.png)](https://p5.ssl.qhimg.com/t0131e58a7c4bef1703.png)

图3:勒索者留下的数据库”CONTACME”

由此判断当前互联网上任然存在着大量未授权访问的Mongodb服务器，已经被黑客删除了数据，并以此进行勒索。



**03全网扫描数据分析**

针对全网扫描后发现，有52313个IP地址开放了27017端口。

进一步对上述IP地址进一步扫描后发现有5538个Mongodb服务器仍存在未授权访问漏洞，其中4279个已经发现勒索者信息（如图4）。

[![](https://p0.ssl.qhimg.com/t01d2afa723b68b567b.png)](https://p0.ssl.qhimg.com/t01d2afa723b68b567b.png)

图4:未授权访问的Mongodb服务器被勒索情况

**1、 TOP10 勒索者邮箱**

[![](https://p2.ssl.qhimg.com/t016563ef7eb124e560.png)](https://p2.ssl.qhimg.com/t016563ef7eb124e560.png)

图5:TOP 10 勒索者邮箱

上述“勒索者邮箱”是指在未授权访问的Mongodb中，勒索者在其留下的电子邮箱（如图5）。

**2、TOP10 攻击日期**

[![](https://p0.ssl.qhimg.com/t0103ac484c4a516e19.png)](https://p0.ssl.qhimg.com/t0103ac484c4a516e19.png)

图6:TOP 10 攻击日期

上述“攻击日期”是指在未授权访问的Mongodb中，勒索者在添加勒索信息时的操作日期（如图6）。

通过360 NetworkScan Mon平台可以看出在2017年5月16日左右，互联网产生了大量针对27017端口的扫描数量（如图7，图8）。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01d512eb30ea7079eb.png)

图7:360NetworkScan Mon 系统针对27017端口监控结果

[![](https://p4.ssl.qhimg.com/t01a4aa222b9d9b7540.png)](https://p4.ssl.qhimg.com/t01a4aa222b9d9b7540.png)

图8:360NetworkScan Mon 系统针对27017端口监控结果

**3、TOP10 勒索者数据库使用名称**

[![](https://p1.ssl.qhimg.com/t0150df81c94efdfcd8.png)](https://p1.ssl.qhimg.com/t0150df81c94efdfcd8.png)

图9:TOP 10 勒索者数据库使用名称

上述“勒索者数据库使用名称”是指在未授权访问的MongoDB中，勒索者在添加勒索信息时的创建的数据库名称（如图9）。

如果某个MongoDB中出现上述名称的数据库，那很有可能已经被勒索者攻击。

**4、 TOP10 数据库数量**

[![](https://p3.ssl.qhimg.com/t01f01d6c1104d9530b.png)](https://p3.ssl.qhimg.com/t01f01d6c1104d9530b.png)

图10:TOP 10 数据库数量

上述“数据库数量”是指存在未授权访问的MongoDB服务器中数据库的数量（为保护用户数据，对应的IP地址已被隐藏）。

可以看出上述MongoDB服务器拥有大量数据，但是存在极大的安全隐患。



**04漏洞影响面**

在5538个存在未授权访问漏洞的MongoDB服务器中，属于中国的IP数量为1180。比例达到了21%。其中根据IP物理地址进行归属划分，列出了TOP20的物理地址归属（如下表1）。

[![](https://p5.ssl.qhimg.com/t0128c1d6392774c84e.png)](https://p5.ssl.qhimg.com/t0128c1d6392774c84e.png)

[![](https://p1.ssl.qhimg.com/t0123913bcb48697755.png)](https://p1.ssl.qhimg.com/t0123913bcb48697755.png)

表1:TOP 20 物理地址归属



**05修复建议**

1、修改默认端口或将MongoDB部署在内部网络中

修改默认的MongoDB端口(默认为：TCP 27017)为其他端口。

2、开启 MongoDB授权



```
&gt; use admin
     &gt; db.createUser( 
    `{` 
         user: "root", 
         pwd: "YOUR PASSWORD", 
         roles: 
         [  
              `{` 
              role: "userAdminAnyDatabase", 
              db: "admin" 
              `}` 
        ] 
    `}` 
   )
```

3、使用SSL加密功能

4、使用–bind_ip选项

该选项可以限制监听接口IP， 当在启动MongoDB的时候，使用 -bind_ip      192.168.0.1表示启动ip地址绑定，数据库实例将只监听192.168.0.1的请求。

5、开启日志审计功能

审计功能可以用来记录用户对数据库的所有相关操作。

6、做好数据备份的策略，以防万一



**06总结**

针对MongoDB的勒索在2016年底就开始了，但是时至今日仍然有大量的未授权访问机存在，同样其他一些基础的互联网应用也存在类似问题，这个问题值得我们关注。

随着勒索软件的流行，随着虚拟货币的增值，黑客通过网络攻击进行获利提供了变现渠道，越来越多的正面暴力攻击正在变得常态化，希望各个厂商、开发者能够重视此类问题，不要造成不必要的损失。

最后，感谢360信息安全部和360网络安全研究院提供的数据支撑。

网站地址：[https://cert.360.cn](https://cert.360.cn)

[![](https://p3.ssl.qhimg.com/t011bec19c0b1d20090.png)](https://p3.ssl.qhimg.com/t011bec19c0b1d20090.png)

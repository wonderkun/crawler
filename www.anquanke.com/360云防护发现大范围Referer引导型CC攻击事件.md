> 原文链接: https://www.anquanke.com//post/id/83001 


# 360云防护发现大范围Referer引导型CC攻击事件


                                阅读量   
                                **118407**
                            
                        |
                        
                                                                                    



**[![](https://p3.ssl.qhimg.com/t01c84278ab17b80793.jpg)](https://p3.ssl.qhimg.com/t01c84278ab17b80793.jpg)**

**事件描述**

11月10日,360云防护产品安域、网站卫士相继发现网站被攻击、拦截失败的事件。

首先,某日报社被攻击,出现502,如图:

[![](https://p5.ssl.qhimg.com/t01f487458be550a8c8.png)](https://p5.ssl.qhimg.com/t01f487458be550a8c8.png)

然后,某运动品牌电商被攻击,无法打开;

同时进一步分析发现,多个网站、包括部分政府单位网站都无法打开。

**事件分析**

通过对云防护数据进行分析,攻击特征非常明显,url中带了特殊字符串,发现从攻击的来源referer非常集中,并且IP一直在变,异常的多,导致CC攻击拦截一直拦不干净。

[![](https://p0.ssl.qhimg.com/t01f0b666ad87a2e3a7.png)](https://p0.ssl.qhimg.com/t01f0b666ad87a2e3a7.png)

攻击URL特征非常明显,wangzhanbeihei&amp;fuwuqibeikeiker:

[![](https://p1.ssl.qhimg.com/t01f223ea10e2c42ed0.png)](https://p1.ssl.qhimg.com/t01f223ea10e2c42ed0.png)

执行CC攻击的网站请求

[![](https://p1.ssl.qhimg.com/t019ee5f05c0fe43e99.png)](https://p1.ssl.qhimg.com/t019ee5f05c0fe43e99.png)

来自某电商遭受攻击的数据:

[![](https://p4.ssl.qhimg.com/t0146b1ab43b9f64593.png)](https://p4.ssl.qhimg.com/t0146b1ab43b9f64593.png)

其中来源最多的为[www.3jy.com](http://www.3jy.com/)、m.3jy.com、www.php100.com和[www.tvtour.com.cn](http://www.tvtour.com.cn/),打开其中的web页面,可以看到数十个网站被加载进来,同时随机进行攻击。

[![](https://p4.ssl.qhimg.com/t01f186101823843dc2.png)](https://p4.ssl.qhimg.com/t01f186101823843dc2.png)

**问题定位**

打开[http://www.3jy.com/youmo/25/321325.html](http://www.3jy.com/youmo/25/321325.html),查看源码,分析发现加载异常js

[![](https://p4.ssl.qhimg.com/t011c9263ab17657912.png)](https://p4.ssl.qhimg.com/t011c9263ab17657912.png)

JS内容除了包含本身网站业务内容外,还包含了攻击的代码:

[![](https://p3.ssl.qhimg.com/t01adc291b53adff12a.png)](https://p3.ssl.qhimg.com/t01adc291b53adff12a.png)

[![](https://p1.ssl.qhimg.com/t01cdbb880b480f3da5.png)](https://p1.ssl.qhimg.com/t01cdbb880b480f3da5.png)

[![](https://p3.ssl.qhimg.com/t01aea36ed562054a6d.png)](https://p3.ssl.qhimg.com/t01aea36ed562054a6d.png)

[![](https://p4.ssl.qhimg.com/t01abb20aae9c56d425.png)](https://p4.ssl.qhimg.com/t01abb20aae9c56d425.png)

从动机看,并不像是刷流量刷SEO的行为,也并非网站站长个人所为,其中3jy.com的攻击脚本中连自己都打,而且还有部分政府单位网站,攻击的动机还是有待深究。

[![](https://p2.ssl.qhimg.com/t012d2ca95b1cc1ca5d.png)](https://p2.ssl.qhimg.com/t012d2ca95b1cc1ca5d.png)

**问题处理**

通过360云防护产品实时调整CC攻击防护规则对用户进行流量清洗,阻止了攻击的持续,并挖掘出多个攻击源进行拦截。

[![](https://p5.ssl.qhimg.com/t01022135a0fd930389.png)](https://p5.ssl.qhimg.com/t01022135a0fd930389.png)

同时通报DNS厂商,对该域名进行停止解析服务,以防攻击范围扩大。

[![](https://p4.ssl.qhimg.com/t017e46c07a5806e59e.png)](https://p4.ssl.qhimg.com/t017e46c07a5806e59e.png)

**事件影响范围**

[![](https://p4.ssl.qhimg.com/t01631c7a3b9c0c49a6.png)](https://p4.ssl.qhimg.com/t01631c7a3b9c0c49a6.png)

360云防护团队,持续为网站安全保障而服务

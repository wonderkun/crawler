> 原文链接: https://www.anquanke.com//post/id/102194 


# 一个都不放过！Zenis病毒诠释勒索加密最强等级


                                阅读量   
                                **68374**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p2.ssl.qhimg.com/t01bd35c2bed9944b21.jpg)](https://p2.ssl.qhimg.com/t01bd35c2bed9944b21.jpg)



近期，360安全中心监测到一款名为“Zenis”的勒索病毒，其命名源自病毒作者的名字。与其他加密常见文件的勒索病毒不同，该病毒运行后，会对设备中超过200种格式的文件进行加密，另外非系统盘符下的所有格式文件也都将被锁，就连exe可执行程序都不会放过。同时，病毒还会删除系统中的备份文件，以避免中招用户恢复重要数据，可谓杀伤力惊人。

以下是对该病毒的详细分析。



## 病毒初始化工作

首先，病毒在执行时会先判断执行条件：

1、判断程序文件名是否为iis_agent32.exe；

2、判断注册表的HKCU\SOFTWARE\ZenisService项中，是否存在Active值。

当文件名不为iis_agent32.exe或者注册表键值已经存在则直接退出不进行加密操作：

[![](https://p3.ssl.qhimg.com/t010440b805a727c574.png)](https://p3.ssl.qhimg.com/t010440b805a727c574.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e5569e64665a8fbd.png)

执行条件满足后，会执行以下命令来删除卷影副本、禁用启动修复和清除系统事件日志（一般通过3389入侵会删除事件日志），同时会检测并结束掉以下进程：

[![](https://p4.ssl.qhimg.com/t01802cec57720102d1.png)](https://p4.ssl.qhimg.com/t01802cec57720102d1.png)

删除卷影副本、禁用启动修复和清除系统事件日志及结束部分进程相关代码：

[![](https://p4.ssl.qhimg.com/t0183f2d818d3bbe2c3.png)](https://p4.ssl.qhimg.com/t0183f2d818d3bbe2c3.png)



## 文件加密部分

Zenis采用的加密手段相对比较传统，是用RSA 1024 + RC4的方式对文件进行加密。即，病毒在每个用户的机器中会生成一对RSA 1024 Session Key，而对每一个文件会生成一个RC4的会话密钥。

对于在用户本地生成的RSA 1024的解密私钥，病毒会使用代码中已经内置好的另一个RSA公钥进行加密（该公钥所对应的私钥在病毒作者手中，未放出）。而生成的RSA 1024的加密公钥，则用于对每个文件生成的RC4 Key进行加密。

加密的文件格式内置在病毒程序中，共204种。另外值得一提的是：即便文件扩展名不在此列表中也并不意味着安全——因为病毒会对非系统盘符下的所有文件进行加密（备份文件则删除）。

加密流程如下图：

[![](https://p4.ssl.qhimg.com/t01f478a7146d1d5742.jpg)](https://p4.ssl.qhimg.com/t01f478a7146d1d5742.jpg)



使用的密钥概述：

[![](https://p0.ssl.qhimg.com/t01169be444453fcd2a.png)](https://p0.ssl.qhimg.com/t01169be444453fcd2a.png)

[![](https://p3.ssl.qhimg.com/t01e7f88159103f839e.png)](https://p3.ssl.qhimg.com/t01e7f88159103f839e.png)

首先，病毒会生成一对1024位的RSA_Key——用于加密的公钥SPUBKEY和用于解密的私钥SPIVKEY。并且用随机生成的RC4密钥USERFLGKEY加密新生成的RSA 1024解密私钥SPIVKEY，然后再用内置的RSA 2048加密公钥RPUBKEY加密这个RC4密钥USERFLGKEY。最终将生成的字符串数据会替换掉勒索信息中的%ENCRYPTED%字段，以备解密时使用：<br>
相关加密代码如下：

[![](https://p1.ssl.qhimg.com/t014b3cb0f44da54cf1.png)](https://p1.ssl.qhimg.com/t014b3cb0f44da54cf1.png)

[![](https://p5.ssl.qhimg.com/t01444151b361cdf4c0.png)](https://p5.ssl.qhimg.com/t01444151b361cdf4c0.png)

病毒内置的RSA 2048加密公钥如下（解密私钥在作者手中）：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01d0bbd24945656f38.png)

逐一文件加密流程相关代码：

[![](https://p5.ssl.qhimg.com/t010e1ee83b11940598.png)](https://p5.ssl.qhimg.com/t010e1ee83b11940598.png)

[![](https://p2.ssl.qhimg.com/t0192e1a72a256f251d.png)](https://p2.ssl.qhimg.com/t0192e1a72a256f251d.png)

病毒程序会将密钥信息写入加密文件尾部：

[![](https://p4.ssl.qhimg.com/t01cfa769be3985a791.png)](https://p4.ssl.qhimg.com/t01cfa769be3985a791.png)

RC4的相关加密代码如下：

[![](https://p3.ssl.qhimg.com/t01ee49c4b8a0b2be28.png)](https://p3.ssl.qhimg.com/t01ee49c4b8a0b2be28.png)

加密的文件扩展名如下表所示：

[![](https://p5.ssl.qhimg.com/t016682467c10df4b75.png)](https://p5.ssl.qhimg.com/t016682467c10df4b75.png)

[![](https://p3.ssl.qhimg.com/t012fc6855c43623045.png)](https://p3.ssl.qhimg.com/t012fc6855c43623045.png)[![](https://p4.ssl.qhimg.com/t0168464913e47ad37a.png)](https://p4.ssl.qhimg.com/t0168464913e47ad37a.png)加密完成后，文件的文件名也会被修改为“Zenis-[2个随机字符].[12个随机字符]”的格式：

例如361test.txt被加密后会被改成了：Zenis-EO.V1OqyzpYfV5z

[![](https://p3.ssl.qhimg.com/t01ddd6cde1cf7841c0.png)](https://p3.ssl.qhimg.com/t01ddd6cde1cf7841c0.png)

而当病毒遍历文件时，一旦发现文件的扩展名符合备份文件的特点，则不会对其进行加密，而是用随机内容覆盖写入文件三次，再删除该备份文件。这是为了让中招者很难再从备份中恢复文件，要删除的备份文件扩展名列表如下：

[![](https://p4.ssl.qhimg.com/t01df1b49ed055b6a9c.png)](https://p4.ssl.qhimg.com/t01df1b49ed055b6a9c.png)[![](https://p4.ssl.qhimg.com/t0169e6aed76e48982b.png)](https://p4.ssl.qhimg.com/t0169e6aed76e48982b.png)相关代码如下：

[![](https://p0.ssl.qhimg.com/t01c3edc0933b33add9.png)](https://p0.ssl.qhimg.com/t01c3edc0933b33add9.png)

此外，病毒还会排除系统及一些杀软的目录，对这些目录中的文件不会进行加密操作：

[![](https://p0.ssl.qhimg.com/t014054c8503e318b83.png)](https://p0.ssl.qhimg.com/t014054c8503e318b83.png)[![](https://p4.ssl.qhimg.com/t0169ff76cfd1a077f0.png)](https://p4.ssl.qhimg.com/t0169ff76cfd1a077f0.png)加密所用的内置RSA公钥以及生成勒索提示信息”Zenis-Instructions.html”，包含说明以及与勒索软件作者联系的邮箱地址相关代码：

病毒生成的勒索页面中包含一个隐藏的Base64编码的字符串，该字符串实际就是前文所述——经双重加密过的解密私钥。而想要解密字符串拿到解密私钥，则只能使用病毒作者手中的私钥。而后续勒索成功后，病毒作者（若守信）也是通过该信息向中招用户下发对应的解密程序或密钥：**[![](https://p5.ssl.qhimg.com/t01cb95abf813853f54.png)](https://p5.ssl.qhimg.com/t01cb95abf813853f54.png)**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014052cac1a35004ef.png)

360反病毒专家尝试与病毒作者邮件进行联系：作者在成功解密了一个文件后以证明自己的解密能力后，要求将0.2018个比特币（本文发表时约合13000元人民币）转入该钱包地址：**17o83ughmzkeMKMsLz4bHRmf75UrjwLpKf**

** [![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0110d752970de3ae94.png)**

[![](https://p2.ssl.qhimg.com/t016db0b4d1fda82fa0.png)](https://p2.ssl.qhimg.com/t016db0b4d1fda82fa0.png)



## 结语

由于Zenis勒索病毒加密格式多样，且会覆盖多次并删除备份相关的文件，一些PE格式的文件及一些常用软件的数据文件被加密或被删除后可能会出现无法正常运行的情况。故相较普通勒索病毒对系统更具破坏性，加之该病毒可能是通过入侵远程桌面弱口令攻入服务进行投毒，因此建议服务器用户：

1、修改为较强的密码；

2、修改默认的3389端口；

3、服务器打最新的补丁；

4、启用网络身份验证NLA；

5、安装安全软件进行防护，360安全卫士已国内率先对该勒索病毒进行查杀，同时，360还可实现对各类勒索病毒的全面防御。

[![](https://p4.ssl.qhimg.com/t012c94c4f40e87e9f6.png)](https://p4.ssl.qhimg.com/t012c94c4f40e87e9f6.png)

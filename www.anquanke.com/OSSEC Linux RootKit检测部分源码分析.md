> 原文链接: https://www.anquanke.com//post/id/238774 


# OSSEC Linux RootKit检测部分源码分析


                                阅读量   
                                **183839**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](https://p4.ssl.qhimg.com/t01a2d24b7db7af7f81.jpg)](https://p4.ssl.qhimg.com/t01a2d24b7db7af7f81.jpg)



## 一、概述

本文简单介绍了开源的 HIDS 软件 OSSEC的安装和使用，并选择 OSSEC 软件的Linux下rootkit检测功能进行源码分析，讲了讲自己的想法与体会，希望与大家共同学习，不足之处希望大家批评指正。<br>
OSSEC 是开源的基于主机的入侵检测系统（HIDS），拥有日志分析、完整性检查、Windows 注册表监视、rootkit 检测、实时警报和主动响应等功能。OSSEC 可以在大多数操作系统上运行，包括 Linux、OpenBSD、FreeBSD、Mac OS X、Solaris 和 Windows。

其特点包括：<br>
1.主机监控<br>
OSSEC 通过文件完整性监控，日志监控，rootkit 检测和流程监控，全面监控企业资产系统活动的各个方面，对于安全管理提供了依据。<br>
2.安全告警<br>
当发生攻击时，OSSEC 会通过发送告警日志和邮件警报让系统管理员及时感知威胁，并在短时间内进行应急处理，最大程度的避免企业遭受损失。OSSEC 还可以通过 syslog 将告警信息导出到任何 SIEM 系统，譬如 OSSIM 进行关联安全分析。<br>
3.全平台支持<br>
最难能可贵的是，OSSEC 提供了全平台系统的支持，包括 Linux，Solaris，AIX，HP-UX，BSD，Windows，Mac 和 VMware ESX，突破性的实现了主机入侵态势感知的全覆盖。<br>
4.功能扩展<br>
OSSEC 得到了第三方安全团队的支持，其中 Wazuh 就是基于 OSSEC开发的一个高级版本，在 OSSEC 的自身功能的基础上进行扩展和优化。



## 二、安装OSSEC

### <a class="reference-link" name="%EF%BC%88%E4%B8%80%EF%BC%89%E6%95%B4%E4%BD%93%E6%9E%B6%E6%9E%84"></a>（一）整体架构

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01740dc7f3f57e2781.jpg)

实验环境如上，各主机的作用如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01eeefbcfa31de103b.jpg)

### <a class="reference-link" name="%EF%BC%88%E4%BA%8C%EF%BC%89%E5%AE%89%E8%A3%85%E8%BF%87%E7%A8%8B"></a>（二）安装过程

本部分先安装 Server 和 Agent，数据库、ELK 日志存储等配置可放在后面。

**<a class="reference-link" name="1.linux%EF%BC%88%E6%9C%AC%E5%A4%84%E4%BB%A5%20centos%20%E4%B8%BA%E4%BE%8B%EF%BC%89%E5%AE%89%E8%A3%85%20OSSEC%20SERVER"></a>1.linux（本处以 centos 为例）安装 OSSEC SERVER**

<a class="reference-link" name="%EF%BC%881%EF%BC%89%E5%88%9D%E5%A7%8B%E5%8C%96%E7%8E%AF%E5%A2%83%E5%AE%89%E8%A3%85%EF%BC%8C%E5%88%86%E5%88%AB%E5%AE%89%E8%A3%85%E7%BC%96%E8%AF%91%E5%BA%93%EF%BC%8C%E4%BB%A5%E5%8F%8A%E6%95%B0%E6%8D%AE%E5%BA%93%E6%94%AF%E6%8C%81%E5%BA%93"></a>**（1）初始化环境安装，分别安装编译库，以及数据库支持库**

# yum -y install make gcc

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0126e42d6f405c2122.jpg)

# yum -y install mysql-devel postgresql-devel

# yum -y install sqlite-devel

[![](https://p1.ssl.qhimg.com/t0158e1fb6f409a10fc.jpg)](https://p1.ssl.qhimg.com/t0158e1fb6f409a10fc.jpg)

<a class="reference-link" name="%EF%BC%882%EF%BC%89%E4%B8%8B%E8%BD%BD%20OSSEC%20%E5%AE%89%E8%A3%85%E5%8C%85%EF%BC%8C%E5%B9%B6%E8%BF%9B%E8%A1%8C%E8%A7%A3%E5%8E%8B%EF%BC%8C%E8%BF%9B%E5%85%A5%E5%AE%89%E8%A3%85%E7%9B%AE%E5%BD%95"></a>**（2）下载 OSSEC 安装包，并进行解压，进入安装目录**

依次执行如下命令，

```
wget https://github.com/ossec/ossec-hids/archive/3.1.0.tar.gz
mv 3.1.0.tar.gz ossec-hids-3.1.0.tar.gz
tar xf ossec-hids-3.1.0.tar.gz# cd ossec-hids-3.1.0
```

[![](https://p1.ssl.qhimg.com/t01a7c1fdd4187bd9b8.jpg)](https://p1.ssl.qhimg.com/t01a7c1fdd4187bd9b8.jpg)

<a class="reference-link" name="%EF%BC%883%EF%BC%89%E8%BF%90%E8%A1%8C%E9%85%8D%E7%BD%AE%E5%AE%89%E8%A3%85%E9%80%89%E9%A1%B9%E8%84%9A%E6%9C%AC"></a>**（3）运行配置安装选项脚本**

此处运行需要root权限

./install.sh

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0184248306a5f5db6e.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01e04d60f981b7ec06.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01d1c8a8354c51b8ea.jpg)

选项说明

server – 安装服务器端

/var/ossec – 选择安装目录，默认选项

y – 是否启用邮件告警，默认启用

y – 是否启用系统完整性检测模块 Syscheck 功能，默认启用

y – 是否启用后门检测模块 Rootcheck 功能，默认启用

y – 是否启用主动响应模块 active-response 功能，默认启用

n – 是否启用防火墙联动功能，默认启用，此处为关闭

n – 是否添加联动功能白名单，默认启用，此处为关闭

y – 是否接受远程主机发送的 syslog 日志，默认启用

备注

配置完安装脚本之后，按回车键就开始进行编译安装，如果需要改变 OSSEC 的配置,可以等安装完成后，编辑 ossec.conf 配置文件进行修改，并重启 ossec 进程使其生效。

<a class="reference-link" name="2.OSSEC-Linux%20Agent%20%E5%AE%89%E8%A3%85"></a>**2.OSSEC-Linux Agent 安装**

<a class="reference-link" name="%EF%BC%881%EF%BC%89%E5%88%9D%E5%A7%8B%E5%8C%96%E7%8E%AF%E5%A2%83%E5%AE%89%E8%A3%85%EF%BC%8C%E5%AE%89%E8%A3%85%E7%BC%96%E8%AF%91%E5%BA%93"></a>**（1）初始化环境安装，安装编译库**

yum -y install make gcc

<a class="reference-link" name="%EF%BC%882%EF%BC%89%E4%B8%8B%E8%BD%BD%20OSSEC%20%E5%AE%89%E8%A3%85%E5%8C%85%EF%BC%8C%E5%B9%B6%E8%BF%9B%E8%A1%8C%E8%A7%A3%E5%8E%8B%EF%BC%8C%E8%BF%9B%E5%85%A5%E5%AE%89%E8%A3%85%E7%9B%AE%E5%BD%95"></a>**（2）下载 OSSEC 安装包，并进行解压，进入安装目录**

```
wget https://github.com/ossec/ossec-hids/archive/3.1.0.tar.gz
mv 3.1.0.tar.gz ossec-hids-3.1.0.tar.gz
tar xf ossec-hids-3.1.0.tar.gz
cd ossec-hids-3.1.0
```

<a class="reference-link" name="%EF%BC%883%EF%BC%89%E8%BF%90%E8%A1%8C%E9%85%8D%E7%BD%AE%E5%AE%89%E8%A3%85%E9%80%89%E9%A1%B9%E8%84%9A%E6%9C%AC"></a>**（3）运行配置安装选项脚本**

./install.sh

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0145e1c8453d3e3016.jpg)

[![](https://p3.ssl.qhimg.com/t01dc9e90f10eec82ba.jpg)](https://p3.ssl.qhimg.com/t01dc9e90f10eec82ba.jpg)

[![](https://p0.ssl.qhimg.com/t019ac04996d0390049.jpg)](https://p0.ssl.qhimg.com/t019ac04996d0390049.jpg)

选项说明

agent – 安装客户端

/var/ossec – 选择安装目录，默认选项

192.168.31.178 – 输入服务器端 IP 地址

y – 是否启用系统完整性检测模块 Syscheck 功能，默认启用

y – 是否启用后门检测模块 Rootcheck 功能，默认启用

y – 是否启用主动响应模块 active-response 功能，默认启用

<a class="reference-link" name="3.OSSEC-WinAgent%20%E5%AE%89%E8%A3%85"></a>**3.OSSEC-WinAgent 安装**

<a class="reference-link" name="%EF%BC%881%EF%BC%89%E4%B8%8B%E8%BD%BD%E5%B9%B6%E8%BF%90%E8%A1%8C%20Agent%20%E5%AE%89%E8%A3%85%E7%A8%8B%E5%BA%8F"></a>**（1）下载并运行 Agent 安装程序**

[https://updates.atomicorp.com/channels/atomic/windows/ossec-agent-win32](https://updates.atomicorp.com/channels/atomic/windows/ossec-agent-win32)

-3.1.0-5696.exe

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t018c3ae0cbdbeb6fd4.jpg)

（2）安装并进行配置

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013a522f0583f692b5.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t017486a30e7ac60e6f.jpg)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015a2e139f44733497.jpg)

这里有关 OSSEC-Server IP的地址和通信密钥的相关操作见下。

<a class="reference-link" name="4.OSSEC%20Server%20%E4%B8%8E%20Agent%20%E9%80%9A%E4%BF%A1"></a>**4.OSSEC Server 与 Agent 通信**

OSSEC Server 和 Agent 之间建立通信需要通过认证，在 Server 端为 Agent 生成通讯密钥并导入 Agent 后才能完成信任关系，以及 Server 端需要开放 UDP 1514通讯端口，接收 Agent 上报的信息

<a class="reference-link" name="%EF%BC%881%EF%BC%89Agent%20%E9%85%8D%E7%BD%AE%E6%8C%87%E5%90%91%20Server%20IP"></a>**（1）Agent 配置指向 Server IP**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0142355cea571a39fd.jpg)

<a class="reference-link" name="%EF%BC%882%EF%BC%89Server%20%E4%B8%BA%20Agent%20%E6%B7%BB%E5%8A%A0%E7%94%A8%E6%88%B7%E5%B9%B6%E7%94%9F%E6%88%90%E9%80%9A%E4%BF%A1%E5%AF%86%E9%92%A5"></a>**（2）Server 为 Agent 添加用户并生成通信密钥**

添加用户

[![](https://p2.ssl.qhimg.com/t0144b0ddc385da9b9f.jpg)](https://p2.ssl.qhimg.com/t0144b0ddc385da9b9f.jpg)

生成密钥

[![](https://p5.ssl.qhimg.com/t01de44e7f78a4b8791.jpg)](https://p5.ssl.qhimg.com/t01de44e7f78a4b8791.jpg)

选项说明

A – 新增 Agent

agent01 – 设置 Agent 名称

10.40.27.121 – 输入 Agent IP 地址

y – 是否确认新增 Agent

E – 为 Agent 生成通讯 Key

001 – 输入新增 Agent 的 ID，显示 Key 值

<a class="reference-link" name="%EF%BC%883%EF%BC%89%E6%8B%B7%E8%B4%9D%20Server%20%E7%94%9F%E6%88%90%E7%9A%84%E9%80%9A%E4%BF%A1%E5%AF%86%E9%92%A5,%E5%B9%B6%E5%AF%BC%E5%85%A5%20Agent"></a>**（3）拷贝 Server 生成的通信密钥,并导入 Agent**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012ce76e44f212a3ef.jpg)

选项说明

I – 新增 Agent

MDAxIGFnZW50MDEgM=… – 输入通信 key

y – 输入 Agent IP 地址

<a class="reference-link" name="%EF%BC%884%EF%BC%89Server%20%E4%B8%BB%E6%9C%BA%E9%98%B2%E7%81%AB%E5%A2%99%E5%BC%80%E6%94%BE%20UDP(1514)%E6%9C%8D%E5%8A%A1%E7%AB%AF%E5%8F%A3"></a>**（4）Server 主机防火墙开放 UDP(1514)服务端口**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e5e041728b403236.jpg)

此时服务器和agent都需要重启下服务，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0166536eeb968d953f.jpg)

Server 上检查 Agent 是否可以通信，可以检测到，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t017e6751a0695930cf.jpg)

备注：

可以通过 /var/ossec/bin/list_agents -h 查询更多 Agent 的状态信息

接下来添加一个windows agent，步骤和上面相似，只列一下过程。

[![](https://p3.ssl.qhimg.com/t0152cc8155da816635.jpg)](https://p3.ssl.qhimg.com/t0152cc8155da816635.jpg)

<a class="reference-link" name="5.Rootcheck%20%E5%90%8E%E9%97%A8%E6%A3%80%E6%B5%8B%E5%AE%9E%E4%BE%8B"></a>**5.Rootcheck 后门检测实例**

此处以设备目录(/dev)创建隐藏文件为实例做解释，

<a class="reference-link" name="%EF%BC%881%EF%BC%89%E6%B5%8B%E8%AF%95"></a>**（1）测试**

首先在/dev 下创建隐藏文件，

[![](https://p1.ssl.qhimg.com/t01a8bfee07c1451cdb.jpg)](https://p1.ssl.qhimg.com/t01a8bfee07c1451cdb.jpg)

<a class="reference-link" name="%EF%BC%882%EF%BC%89Rootcheck%20%E5%91%8A%E8%AD%A6"></a>**（2）Rootcheck 告警**

启动OSSEC后，rootcheck 功能确实检测到/dev 目录下存在隐藏文件，OSSEC会产生告警。

五.3 编写OSSEC检测规则和解码器Http Flood攻击检测和响应

HTTP Flood是针对Web服务在第七层协议发起的攻击。其攻击方式简单、防御过滤困难、对主机影响巨大。

HTTP Flood攻击并不需要控制大批的肉鸡，取而代之的是通过端口扫描程序在互联网上寻找匿名的HTTP代理或者SOCKS代理，攻击者通过匿名代理对攻击目标发起HTTP请求。伪装成正常的用户进行站点的请求，通过巨大的连接数来消耗站点资源。

HTTP Flood攻击在应用层发起，模拟正常用户的请求行为，与网站业务紧密相关，并没有统一的防御方法可以抵御，过滤规则编写不正确可能会误杀一大批用户。HTTP Flood攻击会引起严重的连锁反应，当前端不断没请求而且附带大量的数据库操作时，不仅是直接导致被攻击的Web前端响应缓慢，还间接的攻击到后端服务器程序，例如数据库程序。增大它们的压力，严重的情况下可造成数据库卡死，崩溃。甚至对相关的主机，例如日志存储服务器、图片服务器都带来影响。

我们这里对Http Flood进行简单检测与响应，分为两部分：检测，响应。

对Http Flood攻击的检测，成功检测到，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t010de12ece9e753695.jpg)

对Http Flood攻击的响应，成功阻止与相应ip的连接，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0192ad13be1eebd664.jpg)



## 三、源码分析

### <a class="reference-link" name="1.%E6%80%BB%E4%BD%93%E6%80%9D%E6%83%B3"></a>1.总体思想

本文主要针对RootCheck中关于Linux下RootKit检测部分进行源码分析。

Rootkit是一种特殊的恶意软件，它通过加载特殊的驱动，修改系统内核，进而达到隐藏信息的目的。Rootkit的基本功能包括提供root后门，控制内核模块的加载、隐藏文件、隐藏进程、隐藏网络端口,隐藏内核模块等，主要目的在于隐藏自己并且不被安全软件发现，Rootkit几乎可以隐藏任何软件，包括文件服务器、键盘记录器、Botnet 和 Remailer,而Rootcheck就是OSSEC提供的专门用于检测操作系统rootkit的引擎。

Rootcheck For Linux简要来讲可以分为以下3个方面，

1.使用 rootkit_files 文件中包含的已知后门程序文件或目录特征进行扫描识别异常；

2.使用 rootkit_trojans 文件中包含的已知被感染木马文件的签名进行扫描识别异常；

3.对设备文件目录(/dev)、文件系统、隐藏进程、隐藏端口，混杂模式接口的异常检测；

深入一点可以具体分为如下七个小方面（这七个方面之间并不完全分隔，之间有一些互相关联，而且内容量不小，在此就不统一介绍背景内容，而是在实际某个模块用到时再讲）。

（1）读取rootkit_files.txt，这其中包含rootkit及其常用文件的数据库。工具将尝试统计，以文件方式打开和以目录方式打开每个指定文件。工具使用所有系统调用，因为某些内核级的rootkit隐藏在一些系统调用中的文件。我们尝试的系统调用越多，检测越好。此方法更像是需要不断更新的防病毒规则，假阳性的机会很小，但是通过修改rootkit可以产生假阴性。

（2）读取rootkit_trojans.txt，其中包含由rootkits木马感染的文件签名的数据库。多数流行的rootkit的大多数版本都普遍采用这种用木马修改二进制文件的技术。此检测方法的局限性是找不到任何内核级别的rootkit或任何未知的rootkit。

（3）扫描/ dev目录以查找异常。/ dev应该只具有设备文件和Makedev脚本。许多rootkit使用/ dev隐藏文件。该技术甚至可以检测到非公开的rootkit。

（4）扫描整个文件系统以查找异常文件和权限问题。由root拥有的文件具有对他人的写许可，这是非常危险的，rootkit检测将寻找它们。suid文件，隐藏目录和文件也将被检查。

（5）寻找隐藏进程的存在。我们使用getsid（）和kill（）来检查正在使用的所有pid。如果存在某个pid，但“ ps”看不到，则表示内核级rootkit或“ ps”的木马版本。OSSEC还验证了kill和getsid的输出是否相同。

（6）寻找隐藏端口的存在。我们使用bind（）检查系统上的每个tcp和udp端口。如果我们无法绑定到端口（正在使用该端口），但是netstat没有显示该端口，则可能是安装了rootkit。

（7）扫描系统上的所有网卡，并查找启用了“ promisc”模式的网卡。如果网卡处于混杂模式，则“ ifconfig”的输出应显示该信息。如果没有，我们可能已经安装了rootkit。

### <a class="reference-link" name="2.%E6%80%BB%E4%BD%93%E8%AE%BE%E8%AE%A1"></a>2.总体设计

关于rootkit check部分的架构图如下，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ad7b4064edec7fa5.jpg)

### <a class="reference-link" name="3.%E8%AF%A6%E7%BB%86%E8%AE%BE%E8%AE%A1"></a>3.详细设计

<a class="reference-link" name="%EF%BC%881%EF%BC%89rootkit%E5%8F%8A%E5%85%B6%E5%B8%B8%E7%94%A8%E6%96%87%E4%BB%B6%E6%A3%80%E6%9F%A5%E6%A8%A1%E5%9D%97%E2%80%94%E2%80%94check_rc_files.c"></a>**（1）rootkit及其常用文件检查模块——check_rc_files.c**

整个文件只有一个函数，读取rootkit_files之后，根据特征查找当前系统中有没有符合特征的文件。

[![](https://p0.ssl.qhimg.com/t01777483915766f82c.jpg)](https://p0.ssl.qhimg.com/t01777483915766f82c.jpg)

这里截取rootkit_files的很小的一部分作为示例，

[![](https://p3.ssl.qhimg.com/t01854a893ac04a4812.jpg)](https://p3.ssl.qhimg.com/t01854a893ac04a4812.jpg)

下面看这个函数，一开始先是些变量的声明，后面会讲到，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ae68a89e11325f8f.jpg)

开始读取目标文件，这里的读取不是常规意思上的读取，在读取时也做了一定处理，从中提取出有价值的部分，至于空格换行等无用的部分就都删除掉，读取之后，针对取出的数据库中各个已知rootkit的特征，进行了一个类似于遍历的操作，

先分配缓冲区域，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t014da35cfebb47d652.jpg)

此处的一段代码的目的是跳过注释和空行，

下面开始读取文件中有效的部分，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01c810ea59469595a9.jpg)

接下来为了便于分析，还要去除空格和\t，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ced757e4439d2286.jpg)

接下来是获取link，并对文档尾部的空格和\t进行清除，到这里还没有完全进入分析过程，一直在把读入的文件塑造成OSSEC规定的格式。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01e9a6869884417c36.jpg)

接下来是对内容的处理，

[![](https://p4.ssl.qhimg.com/t01cd85e9b24aa4da0c.jpg)](https://p4.ssl.qhimg.com/t01cd85e9b24aa4da0c.jpg)

先去掉文件中的反斜杠，再分配空间装载文件和文件名，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013ec59457a3dbb8de.jpg)

这一部分把特征取出后合并，供下面使用，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0154f5a7d768badf05.jpg)

这一部分就是根据取出的木马的特征来查找当前系统上是否存在相应木马文件，如果存在则要报告了，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01dab64da425b82a77.jpg)

这个部分的检查我们平时的生活中其实是常见的，比如安全卫士进行扫描时与这个就有相通之处。

<a class="reference-link" name="%EF%BC%882%EF%BC%89rootkit%E6%84%9F%E6%9F%93%E7%9A%84%E6%96%87%E4%BB%B6%E7%AD%BE%E5%90%8D%E6%A3%80%E6%B5%8B%E6%A8%A1%E5%9D%97%E2%80%94%E2%80%94check_rc_trojans.c"></a>**（2）rootkit感染的文件签名检测模块——check_rc_trojans.c**

这一部分的思想也非常简洁直接，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01aee183a14892b739.jpg)

这里截取rootkit_trojans的一部分作为示例，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0125af252c39a99c4f.jpg)

下面看这个c文件，与上一部分一样，这一部分也只有一个函数，思想上也相似，读取rootkit_trojans 文件中包含的已知被感染的木马文件的签名进行扫描来辨别异常；

函数的一开始，先定义了一些用到的变量，并针对不同的系统初始化好系统目录的变量，

[![](https://p1.ssl.qhimg.com/t01f5653b77c9841e60.jpg)](https://p1.ssl.qhimg.com/t01f5653b77c9841e60.jpg)

下面进行的还是将

[![](https://p5.ssl.qhimg.com/t012ac9daca26013cca.jpg)](https://p5.ssl.qhimg.com/t012ac9daca26013cca.jpg)

下面还是在初始化，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01257c1ab68c6991a3.jpg)

下面是正式检查，其实关键语句只有os_string那一句，用正则匹配去匹配特征值，如果发现则产生告警，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01f41211b75cfaded4.jpg)

最后是结尾的一个报告，简单看下就好。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01e81b89113f01e3e7.jpg)

<a class="reference-link" name="(3%EF%BC%89/dev%E6%A3%80%E6%9F%A5%E6%A8%A1%E5%9D%97%E2%80%94%E2%80%94check_rc_dev.c"></a>**(3）/dev检查模块——check_rc_dev.c**

这部分对应的主体源代码在rootcheck目录下的rc_check_dev.c中，其代码大体结构如下：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0166cee00ee973013d.jpg)

由于关于这部分的检测，思路非常清晰，我们可以从相关文件中读取相应的算法，直观上看，大部分内容都在讲未定义Win32的系统（本实验中指Linux），

<a class="reference-link" name="1%EF%BC%89read_dev_file()%E5%87%BD%E6%95%B0"></a>**1）read_dev_file()函数**

我将一些关键语句的解释写在了注释里，

[![](https://p0.ssl.qhimg.com/t01fc0663f649da779b.jpg)](https://p0.ssl.qhimg.com/t01fc0663f649da779b.jpg)

里面涉及到的数据结构和函数，按在函数中出现的先后顺序在此做介绍，

① lstat函数

需要包含的头文件： &lt;sys/types.h&gt;，&lt;sys/stat.h&gt;，&lt;unistd.h&gt;

功 能: 获取一些文件相关的信息

用 法: int lstat(const char **path, struct stat **buf);

参数：

path：文件路径名。

filedes：文件描述词。

buf：是以下结构体的指针

```
struct stat `{`
    dev_t st_dev; /* 文件所在设备的标识 */
    ino_t st_ino; /* 文件结点号 */
    mode_t st_mode; /* 文件保护模式，后面会涉及 */
    nlink_t st_nlink; /* 硬连接数 */
    uid_t st_uid; /* 文件用户标识 */
    gid_t st_gid; /* 文件用户组标识 */
    dev_t st_rdev; /* 文件所表示的特殊设备文件的设备标识 */
    off_t st_size; /* 总大小，单位为字节*/
    blksize_t st_blksize; /* 文件系统的块大小 */
    blkcnt_t st_blocks; /* 分配给文件的块的数量，512字节为单元 */
    time_t st_atime; /* 最后访问时间 */
    time_t st_mtime; /* 最后修改时间 */
    time_t st_ctime; /* 最后状态改变时间 */
`}`;
```

返回值说明

成功执行时，返回0。失败返回-1，errno被设为以下的某个值

EBADF： 文件描述词无效

EFAULT： 地址空间不可访问

ELOOP： 遍历路径时遇到太多的符号连接

ENAMETOOLONG：文件路径名太长

ENOENT：路径名的部分组件不存在，或路径名是空字串

ENOMEM：内存不足

ENOTDIR：路径名的部分组件不是目录

②S_ISREG等几个常见的宏 struct stat

S_ISLNK(st_mode)：是否是一个连接.

S_ISREG(st_mode)：是否是一个常规文件.

S_ISDIR(st_mode)：是否是一个目录

S_ISCHR(st_mode)：是否是一个字符设备.

S_ISBLK(st_mode)：是否是一个块设备

S_ISFIFO(st_mode)：是否 是一个FIFO文件.

S_ISSOCK(st_mode)：是否是一个SOCKET文件

③st_mode 标志位

常见的标志

S_IFMT 0170000 文件类型的位遮罩

S_IFSOCK 0140000 socket

S_IFLNK 0120000 符号链接(symbolic link)

S_IFREG 0100000 一般文件

S_IFBLK 0060000 区块装置(block device)

S_IFDIR 0040000 目录

<a class="reference-link" name="2%EF%BC%89read_dev_dir()%E5%87%BD%E6%95%B0"></a>**2）read_dev_dir()函数**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01984e1a56c916f392.jpg)

这一部分主要是声明了一些常见的忽略的设备文件或者目录，可以理解为一个白名单，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01bdba438bfe835b50.jpg)

向下走，这部分主要是针对最特殊的情况，就是给定的目录名非法、目录名无效或者目录打不开等异常情况，到现在还没有接触到这个函数的主体功能运转的部分，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01403e591e8b91cf16.jpg)

这个大循环是这个函数真正的功能部分，其中对白名单的文件名不做处理，直接continue，检查下一个读取到的目录。检查目录不是真正目的，最终目的还是要去查找恶意文件。宏观上讲，检查文件的函数应该在检查目录的函数内被调用；微观上讲，这个函数运行到最后，发现这个目录名和任意一个正常的目录名都匹配不上，则要进如这个目录检查是否有恶意文件。

[![](https://p0.ssl.qhimg.com/t0102f7a1615101bf0b.jpg)](https://p0.ssl.qhimg.com/t0102f7a1615101bf0b.jpg)

关闭句柄，返回，不再赘述。

<a class="reference-link" name="3%EF%BC%89check_rc_dev()%E5%87%BD%E6%95%B0"></a>**3）check_rc_dev()函数**

这是一个整体的函数，在里面调用了read_dev_dir()函数，

[![](https://p3.ssl.qhimg.com/t014dd1c7558d402461.jpg)](https://p3.ssl.qhimg.com/t014dd1c7558d402461.jpg)

这部分的最后提一下，这部分从名字上听就是只针对Linux系统的，在文件里体现的也比较清楚了，如下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01775d679eea8f0415.jpg)

此处的#else #endif和开始的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01e06c45489bd53513.jpg)

对应起来。

<a class="reference-link" name="%EF%BC%884%EF%BC%89%20%E5%BC%82%E5%B8%B8%E6%96%87%E4%BB%B6%E5%92%8C%E6%9D%83%E9%99%90%E6%A3%80%E6%9F%A5%E6%A8%A1%E5%9D%97%E2%80%94%E2%80%94check_rc_sys.c"></a>**（4） 异常文件和权限检查模块——check_rc_sys.c**

这一模块涉及到的原理简单，但内容比较繁杂，涉及到不同的操作系统的文件系统，看起来有些凌乱，但内在的思想在总述部分中我们是介绍过了的，按着这个思想，不难理解繁杂的这一模块。

由root拥有的文件具有对他人的写许可非常危险，一旦写入了恶意代码，再被执行很有可能被恶意利用。rootkit为了检测这类文件，将扫描整个文件系统以查找异常文件和权限问题。

先看一下整体架构，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01c4e62bdc12510654.jpg)

这个文件中又两个子函数来让check_rc_sys调用，我们顺序来看一下这个文件，

先是一些变量的初始化，具体的使用用到的时候再解释，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01b0eb4521491f9caf.jpg)

先进行了一次判断，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f68739423bf23600.jpg)

这里的思路是，如果一个文件从stat中没有显示，但在readdir中游戏西安市，可能是个内核级别的rootkit，

stat 函数获得一个与此命名文件有关的信息（到一个struct stat 类型的buf中）,

fstat 函数获得文件描述符 fd 打开文件的相关信息（到一个struct stat 类型的buf中）,

lstat 函数类似于 stat，但是当命名文件是一个符号连接时，lstat 获取该符号连接的有关信息，而不是由该符号连接引用文件的信息。

接着判断当前句柄是不是一个目录，如果是目录则调用下面的read_sys_dir函数，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013e43cc75403ef263.jpg)

接下来通过另一种方式读取文件大小，并与我们逐字节读取的做比较，

[![](https://p3.ssl.qhimg.com/t01ce3f54291d0140a7.jpg)](https://p3.ssl.qhimg.com/t01ce3f54291d0140a7.jpg)

如果有差异，则可能是内核级别的rootkit，

简单介绍一下关于USB文件系统的知识， usbfs生命周期在linux-2.6中加入，在linux-3.3移除,同时/proc/bus/usb移到/dev/bus/usb下，在系统启动后，可以查看/proc/bus/usb/devices文件，对文件内容进行分析（$cat /proc/bus/usb/devices）。

接下来是我们的正式检查，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0155b0933020747204.jpg)

具体的语句在截图中都有注释，

另外的相关知识还有，

|S_IRUSR|所有者拥有读权限|S_IXGRP|群组拥有执行权限
|------
|S_IWUSR|所有者拥有写权限|S_IROTH|其他用户拥有读权限
|S_IXUSR|所有者拥有执行权限|S_IWOTH|其他用户拥有写权限
|S_IRGRP|群组拥有读权限|S_IXOTH|其他用户拥有执行权限
|S_IWGRP|群组拥有写权限|

C语言的stdio.h头文件中，定义了用于文件操作的结构体FILE。这样，我们通过fopen返回一个文件指针(指向FILE结构体的指针)来进行文件操作。可以在stdio.h(位于visual studio安装目录下的include文件夹下)头文件中查看FILE结构体的定义，

```
struct _iobuf `{`
    char *_ptr;
    int_cnt;
    char *_base;
    int_flag;
    int_file;
    int_charbuf;
    int_bufsiz;
    char *_tmpfname;
`}`;
typedef struct _iobuf FILE;
```

接下来介绍read_sys_dir()函数，

先进行变量的初始化，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f39b7749f34029aa.jpg)

初步检查，并与白名单作比较，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0184bd0aa9c84ff60c.jpg)

<a class="reference-link" name="%EF%BC%885%EF%BC%89%E9%9A%90%E8%97%8F%E8%BF%9B%E7%A8%8B%E6%A3%80%E6%9F%A5%E6%A8%A1%E5%9D%97%E2%80%94%E2%80%94check_rc_pids.c"></a>**（5）隐藏进程检查模块——check_rc_pids.c**

展示一下这个文件的大体架构，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0139388f0b03ca2a1f.jpg)

在正式介绍之前，先介绍一个从外部引用的子函数及一些先验知识，

[![](https://p5.ssl.qhimg.com/t016627da68b090b914.jpg)](https://p5.ssl.qhimg.com/t016627da68b090b914.jpg)

其中，DIR结构体类似于FILE，是一个内部结构，以下几个函数用这个内部结构保存当前正在被读取的目录的有关信息，

```
struct __dirstream  
`{`  
    void *__fd;   
    char *__data;   
    int __entry_data;   
    char *__ptr;   
    int __entry_ptr;   
    size_t __allocation;   
    size_t __size;   
    __libc_lock_define (, __lock)   
`}`;    
typedef struct __dirstream DIR;
```

函数 DIR **opendir(const char **pathname)，即打开文件目录，返回的就是指向DIR结构体的指针，而该指针由以下几个函数使用:

```
struct dirent *readdir(DIR *dp);   
void rewinddir(DIR *dp);    
int closedir(DIR *dp);     
long telldir(DIR *dp);     
void seekdir(DIR *dp,long loc);
```

dirent结构体的定义，

```
struct dirent  
`{`  
    long d_ino; /* inode number 索引节点号 */    　  
    off_t d_off; /* offset to this dirent 在目录文件中的偏移 */   　 
    unsigned short d_reclen; /* length of this d_name 文件名长 */   
    unsigned char d_type; /* the type of d_name 文件类型 */   　　 
    char d_name [NAME_MAX+1]; /* file name (null-terminated) 文件名，最长255字符 */  
`}`
```

从上述定义也能够看出来，dirent结构体存储的关于文件的信息很少，所以dirent同样也是起着一个索引的作用，

想获得类似ls -l那种效果的文件信息，必须要靠stat函数了。

通过readdir函数读取到的文件名存储在结构体dirent的d_name成员中，而函数int stat(const char **file_name, struct stat **buf);的作用就是获取文件名为d_name的文件的详细信息，存储在stat结构体中。以下为stat结构体的定义：

```
struct stat `{`  
      mode_t   st_mode;    //文件访问权限    
      ino_t    st_ino;    //索引节点号    
      dev_t    st_dev;     //文件使用的设备号     
      dev_t    st_rdev;    //设备文件的设备号     
      nlink_t   st_nlink;    //文件的硬连接数    
      uid_t    st_uid;     //所有者用户识别号     
      gid_t    st_gid;     //组识别号    
      off_t    st_size;    //以字节为单位的文件容量    
      time_t   st_atime;    //最后一次访问该文件的时间    
      time_t   st_mtime;    //最后一次修改该文件的时间     
      time_t   st_ctime;    //最后一次改变该文件状态的时间    
      blksize_t st_blksize;   //包含该文件的磁盘块的大小    
      blkcnt_t  st_blocks;   //该文件所占的磁盘块   
`}`;
```

这个结构体记录的信息可以说是非常详细了。

有关/proc目录的知识，也牵涉到下面的函数。

Linux 内核提供了一种通过 /proc 文件系统，在运行时访问内核内部数据结构、改变内核设置的机制。proc文件系统是一个伪文件系统，它只存在内存当中，而不占用外存空间。它以文件系统的方式为访问系统内核数据的操作提供接口。

用户和应用程序可以通过proc得到系统的信息，并可以改变内核的某些参数。由于系统的信息，如进程，是动态改变的，所以用户或应用程序读取proc文件时，proc文件系统是动态从系统内核读出所需信息并提交的

有了这些先验知识，我们可以向下进行，

<a class="reference-link" name="1%EF%BC%89proc_read()%E5%87%BD%E6%95%B0"></a>**1）proc_read()函数**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01c53b503a57823a2d.jpg)

noproc是一个全局变量，标记当前检查的客体是不是进程。

这个函数逻辑简单，就是检查这个进程在/proc下有没有体现，其中涉及到的关于/proc的内容和子函数isfile_ondir()我们也介绍了，理解起来不难。

<a class="reference-link" name="2%EF%BC%89proc_chdir()%E5%87%BD%E6%95%B0"></a>**2）proc_chdir()函数**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ec02c51bd80d9c14.jpg)

里面几个简单的函数的解释我就直接写在注释里了，这里关于为什么要获取/proc/%d做些解释，Linux 内核提供了一种通过 /proc 文件系统，在运行时访问内核内部数据结构、改变内核设置的机制，proc文件系统是一个伪文件系统，它只存在内存当中，对于进程N在/proc目录中会有体现，

进程N在/proc目录中可能会记录如下信息，

/proc/N pid为N的进程号

/proc/N/cmdline 进程启动命令

/proc/N/cwd 链接到进程当前工作目录

/proc/N/environ 进程环境变量列表

/proc/N/exe 链接到进程的执行命令文件

/proc/N/fd 包含进程相关的所有的文件描述符

/proc/N/maps 与进程相关的内存映射信息

/proc/N/mem 指代进程持有的内存，不可读

/proc/N/root 链接到进程的根目录

/proc/N/stat 进程的状态

/proc/N/statm 进程使用的内存的状态

/proc/N/status 进程状态信息，比stat/statm更具可读性

/proc/self 链接到当前正在运行的进程

<a class="reference-link" name="3%EF%BC%89proc_stat()%E5%87%BD%E6%95%B0"></a>**3）proc_stat()函数**

[![](https://p3.ssl.qhimg.com/t01ee0823265cb080e5.jpg)](https://p3.ssl.qhimg.com/t01ee0823265cb080e5.jpg)

这个函数的内容不多，逻辑也很清晰，关于/proc/pid的知识上面也介绍了，这个函数的功能就是检查在/proc被成功挂载的情况下，能否在该目录下找到对应的pid文件。

<a class="reference-link" name="4%EF%BC%89loop_all_pids()%E5%87%BD%E6%95%B0"></a>**4）loop_all_pids()函数**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ae3a6e2e5c3af296.jpg)

这个函数的体量比较大，一开始先是一些变量的初始化，这些变量的用处在后面会详细介绍，

此处先介绍getpid()函数，此函数的功能是取得进程识别码，getppid()返回父进程标识。

接下来一直到整个函数结束是一个大循环，其中还是先将可能被改变过的变量初始化，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01e3766935775ebe57.jpg)

接下来这一部分主要判断当前检查的进程是否存在，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t015da94018695304d2.jpg)

主要是看这些函数能否执行成功，能成功则将相应变量标记为1，

介绍相关知识，

①session

session就是一组进程的集合，session id就是这个session中leader的进程ID。

session的特点

session的主要特点是当session的leader退出后，session中的所有其它进程将会收到SIGHUP信号，其默认行为是终止进程，即session的leader退出后，session中的其它进程也会退出。

如果session和tty关联的话，它们之间只能一一对应，一个tty只能属于一个session，一个session只能打开一个tty。当然session也可以不和任何tty关联。

session的创建

session可以在任何时候创建，调用setsid函数即可，session中的第一个进程即为这个session的leader，leader是不能变的。常见的创建session的场景是：

用户登录后，启动shell时将会创建新的session，shell会作为session的leader，随后shell里面运行的进程都将属于这个session，当shell退出后，所有该用户运行的进程将退出。这类session一般都会和一个特定的tty关联，session的leader会成为tty的控制进程，当session的前端进程组发生变化时，控制进程负责更新tty上关联的前端进程组，当tty要关闭的时候，控制进程所在session的所有进程都会收到SIGHUP信号。

启动deamon进程，这类进程需要和父进程划清界限，所以需要启动一个新的session。这类session一般不会和任何tty关联。

②进程组

进程组（process group）也是一组进程的集合，进程组id就是这个进程组中leader的进程ID。

进程组的特点

进程组的主要特点是可以以进程组为单位通过函数killpg发送信号。

进程组的创建

进程组主要用在shell里面，shell负责进程组的管理，包括创建、销毁等。（这里shell就是session的leader）

对大部分进程来说，它自己就是进程组的leader，并且进程组里面就只有它自己一个进程。

shell里面执行类似ls|more这样的以管道连接起来的命令时，两个进程就属于同一个进程组，ls是进程组的leader。

shell里面启动一个进程后，一般都会将该进程放到一个单独的进程组，然后该进程fork的所有进程都会属于该进程组，比如多进程的程序，它的所有进程都会属于同一个进程组，当在shell里面按下CTRL+C时，该程序的所有进程都会收到SIGINT而退出。

接下来的一部分又是函数调用，

[![](https://p0.ssl.qhimg.com/t01a39d75d80da01cf7.jpg)](https://p0.ssl.qhimg.com/t01a39d75d80da01cf7.jpg)

毕竟pid不一定是连续的，而我们是直接遍历从1到max_pid，总是会有对应不上进程的数字的。这个地方用了六个函数的返回结果判断，如果这个pid对这些函数没有丝毫反应，这说明pid无效（进程不存在）。

[![](https://p2.ssl.qhimg.com/t01e0dfab2b9e3c24b9.jpg)](https://p2.ssl.qhimg.com/t01e0dfab2b9e3c24b9.jpg)

这个是一个错误报告，不再赘述，

接下来这一部分主要判断进程是否是合法进程，

往下是执行ps命令，查看ps能否显示到。ps命令用于报告当前系统的进程状态。可以搭配kill指令随时中断、删除不必要的程序。ps命令是最基本同时也是非常强大的进程查看命令，使用该命令可以确定有哪些进程正在运行和运行的状态、进程是否结束、进程有没有僵死、哪些进程占用了过多的资源等等，总之大部分信息都是可以通过执行该命令得到的。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t010e2aaff45b331499.jpg)

如果所有命令/函数都能有正常的返回值，则说明这是一个正常的进程，可以continue了，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0158f73e3a89ddaa94.jpg)

接下来这一部分内容与上面相似，用于判断，进程是否是死进程，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0131ac1d5b597f8e32.jpg)

下面这一部分是对在AIX系统上运行时一个特例的特殊处理，这个特例的情境是，除了kill函数，都能正常显示该进程。这部分看下就好，除了最后一句注释以外不需要太注意：恶意程序一般是逃脱ps的显示。

[![](https://p2.ssl.qhimg.com/t01e34aeb1df4a802c7.jpg)](https://p2.ssl.qhimg.com/t01e34aeb1df4a802c7.jpg)

AIX（Advanced Interactive eXecutive）是IBM基于AT&amp;T Unix System V开发的一套类UNIX操作系统，运行在IBM专有的Power系列芯片设计的小型机硬件系统之上。它符合Open group的UNIX 98行业标准（The Open Group UNIX 98 Base Brand），通过全面集成对32-位和64-位应用的并行运行支持，为这些应用提供了全面的可扩展性。它可以在所有的IBM ~ p系列和IBM RS/6000工作站、服务器和大型并行超级计算机上运行。

接下来是一个大的if-else if-else if的嵌套，针对判断出的不同情况进行处理，判断的依据就是上面获得到的变量的情况，

一是如果kill可以显示单getsid和getgpid不能显示，则可能是内核级别的rootkit；

[![](https://p4.ssl.qhimg.com/t01b3296b7504d56ea1.jpg)](https://p4.ssl.qhimg.com/t01b3296b7504d56ea1.jpg)

二是kill、getgpid、getsid显示内容各有差异，且getsid、getgpid未能正确显示，且不为死进程，则可能是内核级别的rootkit，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01a562036103aba65b.jpg)

三是检查pid是一个没有在ps里显示的线程，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01196e1cc3ae1a40a6.jpg)

此处调用了check_rc_readproc()函数，是检查/proc下是否有对应文件的，如果在没有，则可能是被安装了木马。

<a class="reference-link" name="5%EF%BC%89check_rc_pids()%E5%87%BD%E6%95%B0"></a>**5）check_rc_pids()函数**

和别的文件一样，这个函数也是统一调用了其它的函数，

先是一些变量的初始化，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0131fa169c280c4260.jpg)

再是检查对于此部分很关键的ps命令何在，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01f9c15be0a16ba9cf.jpg)

检查关键的/proc部分是否存在，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0188360a7dbbec9b9f.jpg)

调用loop_all_pids()函数，正式开始检查，

[![](https://p5.ssl.qhimg.com/t014054c0bc6fd97bd6.jpg)](https://p5.ssl.qhimg.com/t014054c0bc6fd97bd6.jpg)

进行错误报告，

[![](https://p0.ssl.qhimg.com/t01221f67748c57e31e.jpg)](https://p0.ssl.qhimg.com/t01221f67748c57e31e.jpg)

同样，只针对Linux系统。

<a class="reference-link" name="(6)%E9%9A%90%E8%97%8F%E7%AB%AF%E5%8F%A3%E6%A3%80%E6%9F%A5%E6%A8%A1%E5%9D%97%E2%80%94%E2%80%94check_rc_ports.c"></a>**(6)隐藏端口检查模块——check_rc_ports.c**

这部分功能的主体写在了文件check_rc_ports.c里，我们先看下整体架构，

[![](https://p3.ssl.qhimg.com/t014435ad7992a1641b.jpg)](https://p3.ssl.qhimg.com/t014435ad7992a1641b.jpg)

这部分检测功能的思路也是非常的明确，此处将整个功能大体上拆分成了两步：检查是否某一端口能绑定上，再检测netstat能否显示该端口。

同其他文件一样，这个文件内部，主函数是check_rc_ports，其余的都作为子函数来完成某一步功能，下面开始逐个解释，

<a class="reference-link" name="1%EF%BC%89%E5%AE%8F%E5%AE%9A%E4%B9%89"></a>**1）宏定义**

一开始先define了两个宏，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01fe24072322208ea7.jpg)

一开始有个#if defined(sun)，此处的sun和**sun**为操作系统标识符，

常见的操作系统标识符还有如下，

WINDOWS: _WIN32、WIN32;

UNIX/LINUX: unix、**unix、**unix__;

SunOS/SOLARIS: **SVR4、**svr4**、sun、**sun、**sun**、sparc、**sparc、**sparc__;

HPUX: **hppa、**hppa**、**hpux、**hpux**、_HPUX_SOURCE;

AIX: _AIX、_AIX32、_AIX41、_AIX43、_AIX51、_AIX52;

LINUX: linux、**linux、**linux**、**gnu**linux_**;

CPU: **x86_64、**x86**64**(Intel); **amd64、**amd64**(AMD); sparc、**sparc、**sparc_**(Sun-SPARC);

netstat 命令用于显示各种网络相关信息，如网络连接，路由表，接口状态 (Interface Statistics)，masquerade 连接，多播成员 (Multicast Memberships) 等等。

常见参数

-a (all)显示所有选项，默认不显示LISTEN相关

-t (tcp)仅显示tcp相关选项

-u (udp)仅显示udp相关选项

-n 拒绝显示别名，能显示数字的全部转化成数字。

-l 仅列出有在 Listen (监听) 的服務状态

-p 显示建立相关链接的程序名

-r 显示路由信息，路由表

-e 显示扩展信息，例如uid等

-s 按各个协议进行统计

-c 每隔一个固定时间，执行该netstat命令。

<a class="reference-link" name="2%EF%BC%89run_netstat()%E5%87%BD%E6%95%B0"></a>**2）run_netstat()函数**

下面解释run_netstat()函数

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01818582adfe6d3885.jpg)

中间将宏格式化之后赋值给nt，用system执行，创建子进程等准备工作，如果创建失败，返回-1，执行如果成功返回0，失败返回正数。

<a class="reference-link" name="3%EF%BC%89conn_port%E5%87%BD%E6%95%B0"></a>**3）conn_port函数**

接下来是conn_port()函数

[![](https://p2.ssl.qhimg.com/t01452f6ef6ecf750a8.jpg)](https://p2.ssl.qhimg.com/t01452f6ef6ecf750a8.jpg)

sockaddr_in是常用的数据结构，定义如下，

```
struct sockaddr_in
`{`
    short sin_family;
    /*Address family一般来说AF_INET（地址族）PF_INET（协议族）*/
    unsigned short sin_port;
    /*Port number(必须要采用网络数据格式,普通数字可以用htons()函数转换成网络数据格式的数字)*/
    struct in_addr sin_addr;
    /*IP address in network byte order（Internet address）*/
    unsigned char sin_zero[8];
    /*Same size as struct sockaddr没有实际意义,只是为了　跟SOCKADDR结构在内存中对齐*/
`}`;
```

socket()函数是一种可用于根据指定的地址族、数据类型和协议来分配一个套接口的描述字及其所用的资源的函数，如果函数调用成功，会返回一个标识这个套接字的文件描述符，失败的时候返回-1。

函数原型：

int socket(int domain, int type, int protocol);

其中，参数domain用于设置网络通信的域，函数socket()根据这个参数选择通信协议的族。通信协议族在文件sys/socket.h中定义。

domain的值及含义

|**名称**|**含义**|**名称**|**含义**
|------
|PF_UNIX,PF_LOCAL|本地通信|PF_X25|ITU-T X25 / ISO-8208协议
|AF_INET,PF_INET|IPv4 Internet协议|PF_AX25|Amateur radio AX.25
|PF_INET6|IPv6 Internet协议|PF_ATMPVC|原始ATM PVC访问
|PF_IPX|IPX-Novell协议|PF_APPLETALK|Appletalk
|PF_NETLINK|内核用户界面设备|PF_PACKET|底层包访问

函数socket()的参数type用于设置套接字通信的类型，主要有SOCKET_STREAM（流式套接字）、SOCK——DGRAM（数据包套接字）等。

关于type的值及含义

|**名称**|**含义**
|------
|SOCK_STREAM|Tcp连接，提供序列化的、可靠的、双向连接的字节流。支持带外数据传输
|SOCK_DGRAM|支持UDP连接（无连接状态的消息）
|SOCK_SEQPACKET|序列化包，提供一个序列化的、可靠的、双向的基本连接的数据传输通道，数据长度定常。每次调用读系统调用时数据需要将全部数据读出
|SOCK_RAW|RAW类型，提供原始网络协议访问
|SOCK_RDM|提供可靠的数据报文，不过可能数据会有乱序
|SOCK_PACKET|这是一个专用类型，不能呢过在通用程序中使用

并不是所有的协议族都实现了这些协议类型，例如，AF_INET协议族就没有实现SOCK_SEQPACKET协议类型。

函数socket()的第3个参数protocol用于制定某个协议的特定类型，即type类型中的某个类型。通常某协议中只有一种特定类型，这样protocol参数仅能设置为0；但是有些协议有多种特定的类型，就需要设置这个参数来选择特定的类型。

类型为SOCK_STREAM的套接字表示一个双向的字节流，与管道类似。流式的套接字在进行数据收发之前必须已经连接，连接使用connect()函数进行。一旦连接，可以使用read()或者write()函数进行数据的传输。流式通信方式保证数据不会丢失或者重复接收，当数据在一段时间内任然没有接受完毕，可以将这个连接人为已经死掉。

SOCK_DGRAM和SOCK_RAW 这个两种套接字可以使用函数sendto()来发送数据，使用recvfrom()函数接受数据，recvfrom()接受来自制定IP地址的发送方的数据。

SOCK_PACKET是一种专用的数据包，它直接从设备驱动接受数据。

往下的部分是check_rc_ports函数的主体，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a528c0b4c58347ee.jpg)

其中的server就是上面提到的sockaddr_in类型，再介绍一下bind函数，

函数原型，

int bind( int sockfd , const struct sockaddr * my_addr, socklen_t addrlen);

sockfd表示socket文件的文件描述符，一般为socket函数的返回值；

addr表示服务器的通信地址，本质为struct sockaddr 结构体类型指针，struct sockaddr结构体定义如下

```
struct sockaddr`{`
    sa_family_t sa_family;
    char        sa_data[14];
`}`;
```

结构体中的成员，sa_data[]表示进程地址；

bind函数中的第三个参数addrlen表示参数addr的长度；addr参数可以接受多种类型的结构体，而这些结构体的长度各不相同，因此需要使用addrlen参数额外指定结构体长度，

bind函数调用成功返回0，否则返回-1，并设置erro；

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0192f5b3fe16714a4e.jpg)

对于使用IPv6的系统，代码基本一致，不再赘述，

[![](https://p2.ssl.qhimg.com/t01fc265a7ac29e4481.jpg)](https://p2.ssl.qhimg.com/t01fc265a7ac29e4481.jpg)

<a class="reference-link" name="4%EF%BC%89test_ports()%E5%87%BD%E6%95%B0"></a>**4）test_ports()函数**

这个函数中调用了前两个函数，个人认为出现的意义只是它为了主体函数check_rc_ports更规范，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01173404049ec8b3ab.jpg)

遍历每一个端口，使用bind（）检查系统上的每个tcp和udp端口。如果我们无法绑定到端口，且netstat可以显示该端口的情况，说明系统正在使用该端口，可以直接continue，检测下一个端口，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t019248f09b09af8687.jpg)

如果情况不对，bind不上（端口被占用），且netstat没有显示该端口，则可能是安装了rootkit，此处会记录错误，并且发出警告，

下面还有一部分，是异常端口过多时发出更严重的警告，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fc349a9fabcda917.jpg)

<a class="reference-link" name="5%EF%BC%89check_rc_ports()%E5%87%BD%E6%95%B0"></a>**5）check_rc_ports()函数**

这个函数分别针对TCP协议和UDP协议调用了我们上面讲的test_ports函数，由这个函数调用完成功能的函数，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01fa946d79688b75dd.jpg)

<a class="reference-link" name="6%EF%BC%89%E5%90%8C%E6%A0%B7%EF%BC%8C%E8%BF%99%E4%B8%AA%E5%8A%9F%E8%83%BD%E4%B9%9F%E6%98%AF%E5%8F%AA%E9%92%88%E5%AF%B9Linux%E7%B3%BB%E7%BB%9F%E7%9A%84"></a>**6）同样，这个功能也是只针对Linux系统的**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t015f310eea26716086.jpg)

<a class="reference-link" name="(7)%20%E7%BD%91%E5%8D%A1%E6%A3%80%E6%9F%A5%E6%A8%A1%E5%9D%97%E2%80%94%E2%80%94check_rc_if.c"></a>**(7) 网卡检查模块——check_rc_if.c**

一般计算机网卡都工作在非混杂模式下，此时网卡只接受来自网络端口的目的地址指向自己的数据。当网卡工作在混杂模式下时，网卡将来自接口的所有数据都捕获并交给相应的驱动程序。网卡的混杂模式一般在网络管理员分析网络数据作为网络故障诊断手段时用到，同时这个模式也被网络黑客利用来作为网络数据窃听的入口。

先看一下这个模块的架构，

[![](https://p3.ssl.qhimg.com/t011adf45f34c601599.jpg)](https://p3.ssl.qhimg.com/t011adf45f34c601599.jpg)

可以看到，此处只有两个函数，而且实际代码量也不大，但是其为了执行命令和使用一些数据结构，调用了大量的头文件，下面会介绍到，

<a class="reference-link" name="1%EF%BC%89%E5%AE%8F%E5%AE%9A%E4%B9%89"></a>**1）宏定义**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013109f1fe5fd104ba.jpg)

为了方便后面执行命令而定义的宏字符串，

<a class="reference-link" name="2%EF%BC%89run_ifconfig()%E5%87%BD%E6%95%B0"></a>**2）run_ifconfig()函数**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0171624641eb85b9bc.jpg)

这个函数的内容非常明了，执行命令，如果网卡处于混杂模式，返回1，

介绍一下ifconfig命令，

①命令格式：

ifconfig [网络设备] [参数]

②命令功能：

ifconfig 命令用来查看和配置网络设备。当网络环境发生改变时可通过此命令对网络进行相应的配置。

③命令参数：

up 启动指定网络设备/网卡。

down 关闭指定网络设备/网卡。该参数可以有效地阻止通过指定接口的IP信息流，如果想永久地关闭一个接口，我们还需要从核心路由表中将该接口的路由信息全部删除。

arp 设置指定网卡是否支持ARP协议。

-promisc 设置是否支持网卡的promiscuous模式，如果选择此参数，网卡将接收网络中发给它所有的数据包

-allmulti 设置是否支持多播模式，如果选择此参数，网卡将接收网络中所有的多播数据包

-a 显示全部接口信息

-s 显示摘要信息（类似于 netstat -i）

add 给指定网卡配置IPv6地址

del 删除指定网卡的IPv6地址

&lt;硬件地址&gt; 配置网卡最大的传输单元

mtu&lt;字节数&gt; 设置网卡的最大传输单元 (bytes)

netmask&lt;子网掩码&gt; 设置网卡的子网掩码。掩码可以是有前缀0x的32位十六进制数，也可以是用点分开的4个十进制数。如果不打算将网络分成子网，可以不管这一选项；如果要使用子网，那么请记住，网络中每一个系统必须有相同子网掩码。

tunel 建立隧道

dstaddr 设定一个远端地址，建立点对点通信

-broadcast&lt;地址&gt; 为指定网卡设置广播协议

-pointtopoint&lt;地址&gt; 为网卡设置点对点通讯协议

multicast 为网卡设置组播标志

address 为网卡设置IPv4地址

txqueuelen&lt;长度&gt; 为网卡设置传输列队的长度

<a class="reference-link" name="3%EF%BC%89check_rc_if()%E5%87%BD%E6%95%B0"></a>**3）check_rc_if()函数**

先讲一点先验知识，ifreq是一种数据结构，常用来配置ip地址，激活接口，配置MTU。在Linux系统中获取IP地址通常都是通过ifconfig命令来实现的，然而ifconfig命令实际是通过ioctl接口与内核通信，ifconfig命令首先打开一个socket，然后调用ioctl将request传递到内核，从而获取request请求数据。处理网络接口的许多程序沿用的初始步骤之一就是从内核获取配置在系统中的所有接口。

我们看一下函数中关于初始化工作的部分，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t012b78fce7b78c6ae9.jpg)

这一部分我在源码里没怎么做注释，主要是这部分看起来复杂，其实只是完成了网卡检查的初始化工作，而且涉及到一些具体的数据结构和先验知识，在注释里不便展开，我们在上面介绍过先验知识，下面介绍数据结构。

对于ifconf中ifc_buf，其实就是N个ifc_req,从上面的结构体中可以看出来，通过下面两幅图可以更加明显，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t018a3880eb1561ba9b.jpg)

通过我们的解释，我们知道，ifconf通常是用来保存所有接口信息的，ifreq用来保存某个接口的信息，数据结构具体定义如下，

```
struct ifconf结构体
struct ifconf`{`
lint ifc_len;
union`{`
  caddr_t  ifcu_buf
  Struct  ifreq *ifcu_req;
`}`ifc_ifcu
`}`

Struct ifreq`{`
Char ifr_name[IFNAMSIZ];
Union`{`
  Struct  sockaddr  ifru_addr;
  Struct  sockaddr  ifru_dstaddr;
  Struct  sockaddr  ifru_broadaddr;
  Struct  sockaddr  ifru_netmask;
  Struct  sockaddr  ifru_hwaddr;
  Short  ifru_flags;
  Int   ifru_metric;
  Caddr_t ifru_data;
`}`ifr_ifru;
`}`;
```

接下来是对端口状态的检查，逻辑非常清晰，

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t012362e7358ad9f0d0.jpg)

前面介绍过了，ioctl是网卡通信所用，如果连信息都获取不到信息则不再考虑，前半部分只是为了确定网卡是否可用，

关于后半部分，由于Linux下一切皆文件，如果某网卡处于混杂模式，则一定会在对应的文件中有体现，而如果ifconfig检测不到这种体现，则说明可能被攻击，

<a class="reference-link" name="4%EF%BC%89%E6%94%B6%E5%B0%BE%E5%B7%A5%E4%BD%9C"></a>**4）收尾工作**

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01ac259449425e47ae.jpg)

如果记录的错误大于0，则产生告警。

另外，这个模块也只适用于Linux下。



## 四、总结

OSSEC作为一个功能比较完善的安全防护系统，虽然看起来高深莫测，但如果我们细心、专心、耐心地去分析其原理，结合审计代码加深理解，其实其中内在的思想我们还是可以理解的。拿我审计的rootkit check这一部分来说，一开始的时候也没有想到怎么才能做到针对rootkit的检测，后来看到OSSEC中将对rootkit的检测为了7个方面，每一个方面都相对独立，将这样一个大问题划分成几个小问题，自然就好解决了些。

针对每个小方面，OSSEC又根据实际情况将其向下划分，将每一部分的任务与目标明确下来，再利用系统调用去编程，最终完成任务。其实每一部分的思想都是很明确的，下面我根据自己的感受讲一下。

（1）首先，比较容易想到的就是和安全卫士一样，扫描全盘之类。这是因为现存的已公开的rootkit必然会伴随着一些特征文件，我们可以将其全部记录下来（rootkit_files.txt包含rootkit及其常用文件的数据库），我们为了安全，应该打开每个指定文件进行检查，也要检查系统调用文件中有没有rootkit的特征。

（2）多数流行的rootkit的大多数版本都普遍采用这种用木马修改二进制文件的技术，我们也可以记录下已被公开的rootkits木马感染的文件签名（rootkit_trojans.txt包含这样的数据库）。当然这两种检测方法主要是针对已知的rootkit，但是如果连已知的问题都解决不了，更不要谈未知的了。

（3）接下来就需要去发散一下思维了，正常情况下，/ dev应该只具有设备文件和Makedev脚本，而许多rootkit使用/ dev隐藏文件，所以我们应该扫描/ dev目录以查找异常，如果发现异常，必是rootkit在作祟。相比于前两个基于已有rootkit的数据库，这个技术是可以检测到非公开的rootkit。这一部分的思想也是非常的简单直接，颇有些大巧不工的意思。

（4）其实说是发散，不如说是对安全的一种感觉，一种经验的积累与内化。比如这里提到的，有些rootkit会找到root拥有的且对他人可写的文件并进行修改。我们可以想到，即使这样的文件暂没有被利用，也是非常危险的，这个问题不一定会涉及到rootkit，但我们未雨绸缪，理应检测这种文件。

（5）从另一种角度讲，即使系统中有rootkit文件还不一定有危险，危险最终一定还要落实到进程上的，这样一来，我们必须要寻找有没有隐藏进程。出于这个目的，我们使用getsid（）和kill（）来检查正在使用的所有pid，并根据不同的结果进行区分。

（6）如果说前面的部分是针对文件的，下面就是针对设备的（Linux下一切都是文件，这里所指只是狭义的文件）。还有一种可能是连接了正向shell，为了检查我们的系统是不是将shell连到了哪个端口上，我们检查系统上的每个tcp和udp端口。这里要用到的就是bind()和netstat命令，并根据不同的结果进行区分。

（7）一般计算机网卡都工作在非混杂模式下，此时网卡只接受来自网络端口的目的地址指向自己的数据。当网卡工作在混杂模式下时，网卡将来自接口的所有数据都捕获并交给相应的驱动程序。网卡的混杂模式一般在网络管理员分析网络数据作为网络故障诊断手段时用到，同时这个模式也被网络黑客利用来作为网络数据窃听的入口。考虑到这些，我们应该扫描系统上的所有网卡，并查找启用了“ promisc”模式的网卡。如果网卡处于混杂模式，则“ ifconfig”的输出应显示该信息。如果没有，我们可能已经安装了rootkit。

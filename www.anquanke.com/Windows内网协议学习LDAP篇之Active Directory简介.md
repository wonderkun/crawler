> 原文链接: https://www.anquanke.com//post/id/195100 


# Windows内网协议学习LDAP篇之Active Directory简介


                                阅读量   
                                **1494277**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">8</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01e4bed02d4ea9a806.png)](https://p1.ssl.qhimg.com/t01e4bed02d4ea9a806.png)



作者: daiker@360RedTeam

## 0x00 前言

这是LDAP篇的第一篇文章。在域渗透中，可能大家对Active Directory，LDAP，Naming Context这些概念既熟悉又模糊，比如Active Directory跟LDAP有啥关系等等。在LDAP篇，我们将系统地介绍跟Active Directory相关的方方面面。第一篇文章主要介绍一些基本概念，让大家对整个Active Directory有个基本印象。在之后的文章里面会陆续介绍Active Directory相关的方方面面。包括但不限于。
- 域内用户介绍
- 域内组介绍
- 域内ACL介绍
- 域信任关系介绍
- 组策略介绍
这篇文章对一些专业词汇统一保留英文



## 0x01 LDAP简介

LDAP全称是Lightweight Directory Access Protocol，轻量目录访问协议。顾名思义，LDAP是设计用来访问目录数据库的一个协议。

在这之前我们先介绍一下目录服务。目录数据库是由目录服务数据库和一套访问协议组成。

目录服务数据库也是一种数据库，这种数据库相对于我们熟知的关系型数据库(比如MySQL,Oracle),主要有以下几个方面的特点。
1. 它成树状结构组织数据，类似文件目录一样。
1. 它是为查询、浏览和搜索而优化的数据库，也就是说LDAP的读性能特别强，但是写性能差，而且还不支持事务处理、回滚等复杂功能。
为了能够访问目录数据库，必须设计一台能够访问目录服务数据库的协议，LDAP是其中一种实现协议。

为了方便大家理解下面举个例子来介绍一些LDAP相关的东西。

[![](https://p3.ssl.qhimg.com/t01090405656313c00d.png)](https://p3.ssl.qhimg.com/t01090405656313c00d.png)

如上图所示是目录服务数据库，它成树状结构组织数据。下面介绍一些基本概念
1. 目录树：如上图所示，在一个目录服务系统中，整个目录信息集可以表示为一个目录信息树，树中的每个节点是一个条目。
1. 条目：每个条目就是一条记录，每个条目有自己的唯一可区别的名称（DN）。比如图中的每个圆圈都是一条记录。
1. DN,RDN:比如说第一个叶子条目，他有一个唯一可区分的名称DN:uid=bob,ou=people,dc=acme,dc=org。类似于文件目录的相对路径绝对路径，他除了有个DN之外，还有个RDN，他与目录结构无关，比如之前咱们提过的uid=bob,ou=people,dc=acme,dc=org，他的RDN就是uid=bob
1. 属性：描述条目具体信息。比如`uid=bill,ou=people,dc=acme,dc=org，他有属性name 为bill，属性age为11，属性school 为xx。
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01dd7a04f000980716.png)



## 0x02 Active Directory简介

不同厂商对目录服务数据库的实现不一，常见的如下实现。

[![](https://p2.ssl.qhimg.com/dm/1024_327_/t01143e2e45b52e6dd6.png)](https://p2.ssl.qhimg.com/dm/1024_327_/t01143e2e45b52e6dd6.png)

可以看出Active Directory，是微软的对目录服务数据库的实现，而LDAP是设计用来对目录服务数据库(在这里的实现就是微软的Active Directory)的访问的协议。Active Directory存储着整个域内所有的计算机，用户等的所有信息。

如果我们想访问域内的Active Directory，有两种办法
1. 域内的每一台域控都有一份完整的本域的Active Directory，可以通过连接域控的389/636端口(636端口是LDAPS)来进行连接查看修改。
1. 如果用户知道某个对象处于哪个域，也知道对象的标识名，那么通过上面第一种方式搜索对象就非常容易。但是考虑到这种情况，不知道对象所处的域，我们不得不去域林中的每个域搜索。为了解决这个问题，微软提出全局编录服务器(GC，Global Catalog)， 全局编录服务器中除了保存本域中所有对象的所有属性外，还保存林中其它域所有对象的部分属性，这样就允许用户通过全局编录信息搜索林中所有域中对象的信息。也就是说如果需要在整个林中进行搜索，而不单单是在具体的某个域进行搜索的时候，可以连接域控的3268/3269端口。


## 0x03 Naming Context和Application Partitions

之前的内容都是在讲Active Directory的基本概念，接下来我们来具体的探究下Active Directory具体有啥东西。

### Naming Context

首先有一点得明确，Active Directory具有分布式特性，一个林中有若干个域，每个域内有若干台域控，每台域控有一个独立的Active Directory。这个时候就有必要将数据隔离到多个分区中，如果不隔离的话，则每个域控制器都必须复制林中的所有数据。若隔离为若干个分区之后，就可以有选择性的复制某几个分区。微软将Active Directory划分为若干个分区(这个分区我们称为Naming Context，简称NC)，每个Naming Context都有其自己的安全边界。

Active Directory预定义了三个Naming Context
- Configuration NC(Configuration NC)
- Schema NC(Schema NC)
- Domain NC(DomainName NC)
我们使用ADExplorer连接进来就可以看到这三个(后面两个是引用程序分区，后面会讲)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01ae3befe6235adcb0.png)

我们来简单的介绍下这三个Naming Context
1. Configuration NC(Configuration NC)
配置NC,林配置信息的主要存储库，包含有关站点，服务，分区和Active DirectorySchema 的信息，并被复制到林中的每个域控制器。配置NC的根位于配置容器中，该容器是林根域的子容器。例如，test.local林将为CN=Configuration,DC=test,DC=local

下面我们来看看这个Naming Context的顶级容器有哪些。

[![](https://p2.ssl.qhimg.com/t0121353213abb6c293.png)](https://p2.ssl.qhimg.com/t0121353213abb6c293.png)

<tr class="md-end-block md-focus-container" style="box-sizing: border-box; break-inside: avoid; break-after: auto; border-top: 1px solid #dfe2e5; margin: 0px; padding: 0px;"><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; font-weight: bold; border-top-style: solid; border-right-style: solid; border-left-style: solid; border-top-color: #dfe2e5; border-right-color: #dfe2e5; border-left-color: #dfe2e5; text-align: center; margin: 0px;">RDN</th><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; font-weight: bold; border-top-style: solid; border-right-style: solid; border-left-style: solid; border-top-color: #dfe2e5; border-right-color: #dfe2e5; border-left-color: #dfe2e5; text-align: center; margin: 0px;">说明</th></tr>|------
1. Schema NC(Schema NC)
包含Schema 信息，该Schema 信息定义Active Directory中使用的类，对象和属性。与域NC和配置 NC 不同，模式 NC 不维护容器或组织单位的层次结构。相反，它是具有 classSchema ，attributeSchema 和 subSchema 对象的单个容器。关于这个Naming Context的详细内容我们将在下一节里面详细讲。
1. Domain NC(DomainName NC)
每个域都有一个域Naming Context，不同的域内有不同的域Naming Context，其中包含特定于域的数据。这个域Naming Context(的根由域的专有名称(DN)表示，比如corp.test.local域的DN将为dc=corp,dc=test,dc=local。之前我们说过，域内的所有计算机，所有用户的具体信息都存在Active Directory底下，具体来说，就是在Active Directory的这个Naming Context里面。我们用工具查看的默认Naming Context选的也是这个Naming Context。后面对域内很多东西的查看都在这个Naming Context里面。下面我们来看看这个Naming Context的顶级容器有哪些。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0196797be6f47f5654.png)

<tr class="md-end-block md-focus-container" style="box-sizing: border-box; break-inside: avoid; break-after: auto; border-top: 1px solid #dfe2e5; margin: 0px; padding: 0px;"><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; font-weight: bold; border-top-style: solid; border-right-style: solid; border-left-style: solid; border-top-color: #dfe2e5; border-right-color: #dfe2e5; border-left-color: #dfe2e5; text-align: center; margin: 0px;">RDN</th><th style="box-sizing: border-box; padding: 6px 13px; border-width: 1px 1px 0px; font-weight: bold; border-top-style: solid; border-right-style: solid; border-left-style: solid; border-top-color: #dfe2e5; border-right-color: #dfe2e5; border-left-color: #dfe2e5; text-align: center; margin: 0px;">说明</th></tr>|------

### Application Partitions

从 Windows Server 2003 开始，微软允许用户自定义分区来扩展Naming Context的概念。Application Partitions其实就是Naming Context的一个扩展，它本质上还是属于Naming Context。管理员可以创建分区(这个分区我们称为区域)，以将数据存储在他们选择的特定域控制器上，Application Partitions主要有以下特点:
1. Naming Context是微软预定义的，用户不可以定义自己的Naming Context。而如果用户想要定义一个分区，可以通过Application Partitions。虽然微软也预置了两个Application Partitions，但是Application Partitions的设计更多是为了让用户可以自定义自己的数据。设计Application Partitions最大的用途就是，让用户自己来定义分区。
[![](https://p0.ssl.qhimg.com/t01f518c80c8f1e44bb.png)](https://p0.ssl.qhimg.com/t01f518c80c8f1e44bb.png)
<li>Application Partitions可以存储动态对象。动态对象是具有生存时间(TTL) 值的对象，该值确定它们在被Active Directory自动删除之前将存在多长时间。也就说Application Partitions可以给数据设置个TTL，时间一到，Active Directory就删除该数据。<br>
下面演示通过ntdsutil创建Application Partitions:</li>
[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0149d0621705aebfdb.png)

创建成功

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01370d8bed3000b97b.png)

我们可以通过查看rootDSE查看域内的所有Naming Context以及Application Partitions，在属性namingContexts里面。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01fb33cc62591244a0.png)



## 0x05 Schema NC

Schema NC里面包含Schema 信息，定义了Active Directory中使用的类和属性。所以在详细讲Schema NC之前我们先来讲一下LDAP里面的类和继承。

LDAP里面的类和继承，跟开发里面的面向对象一样，相信有过面向对象开发经验的，理解起来并不困难。

### 1.LDAP 中的类和继承
<li>类和实例<br>
域内每个条目都是类的实例。而类是一组属性的集合。<br>
举个例子:<br>
域内机器CN=WIN7,CN=Computers,DC=test,DC=local在Active Directory里面是一个条目，里面有众多属性描述条目具体信息。</li>
[![](https://p2.ssl.qhimg.com/dm/1024_470_/t01492c9533fd2e02b7.png)](https://p2.ssl.qhimg.com/dm/1024_470_/t01492c9533fd2e02b7.png)

而这个条目有哪些属性是由他的类决定的。比如说这里的条目是CN=WIN7,CN=Computers,DC=test,DC=local是类Computer的实例，在objectClass属性可以看到

[![](https://p5.ssl.qhimg.com/t014501bc6468e75a5a.png)](https://p5.ssl.qhimg.com/t014501bc6468e75a5a.png)

[![](https://p0.ssl.qhimg.com/dm/1024_391_/t01ecefefe2b3a13f47.png)](https://p0.ssl.qhimg.com/dm/1024_391_/t01ecefefe2b3a13f47.png)
1. 类是可继承的。子类继承父类的所有属性，Top类是所有类的父类。在之前我们看objectClass的时候，可以看到条目是CN=WIN7,CN=Computers,DC=test,DC=local是类Computer的实例。但是我们注意到objectClass里面的值除了Computer之外，还有top,person,organizationPerson,user。这是因为objectClass保存了类继承关系。user是organizationPerson的子类，organizationPerson是person的子类，person是top的子类。
[![](https://p1.ssl.qhimg.com/t0124d3b9e423bf47be.png)](https://p1.ssl.qhimg.com/t0124d3b9e423bf47be.png)
<li>类的分类<br>
类有三种类型
<ul>
<li>结构类（Structural）<br>
结构类规定了对象实例的基本属性，每个条目属于且仅属于一个结构型对象类。前面说过域内每个条目都是类的实例，这个类必须是结构类。只有结构类才有实例。比如说前面说过的Computer类。</li>
<li>抽象类(Abstract)<br>
抽象类型是结构类或其他抽象类的父类，它将对象属性中公共的部分组织在一起。跟面对对象里面的抽象方法一样，他没有实例，只能充当结构类或者抽象类的父类。比如说top 类。注意抽象类只能从另一个抽象类继承。</li>
<li>辅助类(Auxiliary）<br>
辅助类型规定了对象实体的扩展属性。虽然每个条目只属于一个结构型对象类，但可以同时属于多个辅助型对象类。注意辅助类不能从结构类继承</li>
</ul>
</li>
接下来让我们结合Schema NC中的类来具体理解下LDAP 中的类和继承

### 2.Schema NC中的类

如果我们要查看Schema NC的内容，除了传统使用LDAP编辑器查看

比如说ADExplorer

还可以使用微软自带的Active Directory Schema

[![](https://p3.ssl.qhimg.com/t01fa51fe12fb918115.png)](https://p3.ssl.qhimg.com/t01fa51fe12fb918115.png)

默认没有注册，运行regsvr32 schmmgmt.dll注册该dll

然后在mmc里面添加即可

[![](https://p3.ssl.qhimg.com/dm/1024_366_/t01e0a4af187093133c.png)](https://p3.ssl.qhimg.com/dm/1024_366_/t01e0a4af187093133c.png)

域内每个条目都是类的实例。所有的类都存储在Schema NC里面，是Schema NC的一个条目。

我们以一个实例来说明。前面说过条目CN=WIN7,CN=Computers,DC=test,DC=local是类Computer的实例。那么类Computer就存储在Schema NC里面，是Schema NC的一个条目CN=Computer,CN=Schema,CN=Configuration,DC=test,DC=local。

我们下面来具体分析下这个条目的一些通用属性，希望大家对类条目有个大概的认识。

[![](https://p4.ssl.qhimg.com/dm/1024_418_/t017a3e017d2c63b0d9.png)](https://p4.ssl.qhimg.com/dm/1024_418_/t017a3e017d2c63b0d9.png)

[![](https://p0.ssl.qhimg.com/dm/1024_681_/t0156cbacb123e85b10.png)](https://p0.ssl.qhimg.com/dm/1024_681_/t0156cbacb123e85b10.png)

（1）前面说过每个条目都是类的实例，而类是是Schema NC的一个条目。因此类条目也是一个类的实例，这个类是classSchema(CN=Class-Schema,CN=Schema,CN=Configuration,DC=test,DC=local)。所有的类条目都是classSchema类的实例。<br>
我们可以在objectclass属性里面看到。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01f0d40529109fc428.png)

（2）名称是Computer(通过adminDescription，adminDisplayName，cn，name属性)

（3）defaultSecurityDescriptor这个属性表明，如果在创建Computer这个类的实例的时候，如果没指定ACL，就用这个属性的值作为实例的ACL。在实例的nTSecurityDescriptor里面。

[![](https://p3.ssl.qhimg.com/dm/1024_22_/t019a01b72c482ec678.png)](https://p3.ssl.qhimg.com/dm/1024_22_/t019a01b72c482ec678.png)

注意跟nTSecurityDescriptor区分开来，nTSecurityDescriptor是这个条目的ACL，而defaultSecurityDescriptor是实例默认的ACL。举个例子。<br>
CN=Computer,CN=Schema,CN=Configuration,DC=test,DC=local 有两个属性nTSecurityDescriptor，defaultSecurityDescriptor。nTSecurityDescriptor是这条条目的ACL。<br>
那Computer的实例化对象CN=WIN7,CN=Computers,DC=test,DC=local，如果在创建的时候，没有指定ACL，那么他的nTSecurityDescriptor的值就是CN=Computer,CN=Schema,CN=Configuration,DC=test,DC=local 的属性defaultSecurityDescriptor的值。

（4）属性rDNAttID表明通过LDAP连接到类的实例的时候，使用的两个字母的前缀用过是cn。<br>
所以他的实例CN=WIN7,CN=Computers,DC=test,DC=local,使用的前缀是cn。<br>
这个我们再举个例子<br>
比如条目OU=Domain Controllers,DC=test,DC=locals 是一个ou，它是类organizationalUnit的实例

[![](https://p4.ssl.qhimg.com/dm/1024_279_/t01a51ae5248eefbeb1.png)](https://p4.ssl.qhimg.com/dm/1024_279_/t01a51ae5248eefbeb1.png)

我们查看类organizationalUnit对应的条目CN=Organizational-Unit,CN=Schema,CN=Configuration,DC=test,DC=local,就可以看到

[![](https://p3.ssl.qhimg.com/t014bb1dabb25a255da.png)](https://p3.ssl.qhimg.com/t014bb1dabb25a255da.png)

所以对于他的一个实例，他的前缀是OU，OU=Domain Controllers

（5）属性objectClassCategory为1说明他是一个结构类
- 1 代表是个结构类
- 2 代表是个抽象类
- 3代表是个辅助类
（6）属性subClassOf 表明他的父类是user类

（7）systemPossSuperior约束了他的实例只能创建在这三个类container,organizationalUnit,domainDNS的实例底下。

[![](https://p0.ssl.qhimg.com/t016cbde3e4ab916e3b.png)](https://p0.ssl.qhimg.com/t016cbde3e4ab916e3b.png)

比如computer类的一个实例，CN=WIN7,CN=Computers,DC=test,DC=local，它位于容器CN=Computers,DC=test,DC=local底下，而CN=Computers,DC=test,DC=local是container的实例，container在systemPossSuperior底下，这不违反这个约束。

（8）最后一点也是最核心的，我们来讲下他的实例是怎么获取到基本属性的。
- 这个类没有属性systemMustContain和MustContain，因此强制属性
- 这个类属性systemMayContain和MayContain是可选的属性
[![](https://p0.ssl.qhimg.com/t01e570aee39c313e33.png)](https://p0.ssl.qhimg.com/t01e570aee39c313e33.png)

[![](https://p4.ssl.qhimg.com/t010c26c15a4fff98fa.png)](https://p4.ssl.qhimg.com/t010c26c15a4fff98fa.png)

上面这四个属性里面的属性集合是这个类独有的属性集合，我们之前说过，类是可继承的。因此一个类的属性集合里面除了前面的四个属性里面的值，还可能来自父类以及辅助类。
- 辅助类的属性字段是systemAuxiliaryClass,这里面的computer类没有辅助类
- 父类 可以通过subClassOf查看，这里是computer类的父类是user类。然后网上递归，user类查看那四个属性，以及他的辅助类，父类。直到top类。
[![](https://p5.ssl.qhimg.com/t01fbf49ab711dbab54.png)](https://p5.ssl.qhimg.com/t01fbf49ab711dbab54.png)

所以最后我们用Active DirectorySchema 查看的时候，就会看到属性的类型是可选还是强制，源类是哪个类。

[![](https://p2.ssl.qhimg.com/dm/1024_430_/t01a902f947161d2891.png)](https://p2.ssl.qhimg.com/dm/1024_430_/t01a902f947161d2891.png)

### 3.Schema NC中的属性

Schema NC除了定义了Active Directory中使用的类，还定义了Active Directory中使用的属性。

关于属性，我们之前接触的够多了。这里不再多做解释。

每个属性都是一个条目，是类attributeSchema的实例

在域内的所有属性必须在这里定义，而这里的条目，最主要的是限定了属性的语法定义。其实就是数据类型，比如 Boolean类型，Integer类型等。

以CN=Object-Sid,CN=Schema,CN=Configuration,DC=test,DC=local为例。

他的attributeSyntax是2.5.5.17

[![](https://p1.ssl.qhimg.com/t012fd3d0eec2db7bf2.png)](https://p1.ssl.qhimg.com/t012fd3d0eec2db7bf2.png)

oMSyntax是

[![](https://p3.ssl.qhimg.com/t019a89a661a9e0df32.png)](https://p3.ssl.qhimg.com/t019a89a661a9e0df32.png)

通过查表

[![](https://p4.ssl.qhimg.com/t01a60900e42fe274a5.png)](https://p4.ssl.qhimg.com/t01a60900e42fe274a5.png)

关于各种语法定义在这里不再这里一个个介绍，过于抽象，将在后面文章里面实际的案例根据需要详细讲解。



## 0x06 搜索Active Directory

通过查询目录，可以直接收集到要求的数据。查询目录需要指定两个要素
- BaseDN
- 过滤规则
### BaseDN

BaseDN指定了这棵树的根。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013b93961186d9bfc3.png)

比如指定BaseDN为DC=test.DC=local就是以DC=test.DC=local为根往下搜索

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t012ca2048e78e2d81d.png)

BaseDN为CN=Users,DC=test.DC=local就是以CN=Users,DC=test.DC=local为根往下搜索

### 过滤规则

LDAP 过滤规则相对简单，很方便入手

LDAP 搜索过滤器语法有以下子集：
- 用与号 (&amp;) 表示的 AND 运算符。
- 用竖线 (|) 表示的 OR 运算符。
- 用感叹号 (!) 表示的 NOT 运算符。
- 用名称和值表达式的等号 (=) 表示的相等比较。
- 用名称和值表达式中值的开头或结尾处的星号 (*) 表示的通配符。
下面举几个例子
<li>(uid=testuser)<br>
匹配 uid 属性为testuser的所有对象</li>
<li>(uid=test*)<br>
匹配 uid 属性以test开头的所有对象</li>
<li>(!(uid=test*))<br>
匹配 uid 属性不以test开头的所有对象</li>
<li>(&amp;(department=1234)(city=Paris))<br>
匹配 department 属性为1234且city属性为Paris的所有对象</li>
<li>(|(department=1234)(department=56*))<br>
匹配 department 属性的值刚好为1234或者以56开头的所有对象。</li>
一个需要注意的点就是运算符是放在前面的，跟我们之前常规思维的放在中间不一样

关于查询目录还有一些高级点的用法，比如 LDAP 控件，位掩码等。这里不一一列举，将在后面实际用到的时候再列举。



## 0x07 相关工具介绍

下面介绍一些能够访问Active Directory的工具

### ADSI 编辑器

微软自带，输入adsiedit.msc可访问

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010fce888ae508a162.png)

### LDP

微软自带，输入ldp可访问

[![](https://p0.ssl.qhimg.com/dm/1024_432_/t010ac7b035ba2f3be6.png)](https://p0.ssl.qhimg.com/dm/1024_432_/t010ac7b035ba2f3be6.png)

### ADExplorer

sysinternals系列的工具,相较于ADSI 编辑器，更方便

[![](https://p5.ssl.qhimg.com/dm/1024_440_/t0107e75ec4fff03e7a.png)](https://p5.ssl.qhimg.com/dm/1024_440_/t0107e75ec4fff03e7a.png)

### The LDAP Explorer

付费版的神器，特别强大，比ADExplorer都强大，自己感受下

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/dm/1024_429_/t01609a06c628677991.png)

### ldapsearch

openldap里面的工具，在*nix里面比较常用

[![](https://p0.ssl.qhimg.com/dm/1024_461_/t0114a15a5fa87b48d3.png)](https://p0.ssl.qhimg.com/dm/1024_461_/t0114a15a5fa87b48d3.png)

导出的格式为LDIF格式，有人写了个工具支持导出为sqlite文件，然后阅读sqlite文件

[![](https://p2.ssl.qhimg.com/dm/1024_499_/t0137397ba8a4763efd.png)](https://p2.ssl.qhimg.com/dm/1024_499_/t0137397ba8a4763efd.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/dm/1024_372_/t01a299d388b56f6539.png)

### adfind 与 admod

这个是最牛逼的命令行工具了，在域渗透里面的出场率极高，adfind用于查询，admod用于修改。这个系列的主要文章会围绕着这两个工具展开。

[![](https://p2.ssl.qhimg.com/t019dd290e816f0825c.png)](https://p2.ssl.qhimg.com/t019dd290e816f0825c.png)



## 0x09 引用
- LDAP概念和原理介绍
- LDAP基础概念
- Active Directory Domain Services
- LDAP search filter expressions
- Active Directory: Designing, Deploying, and Running Active Directory Fifth Edition
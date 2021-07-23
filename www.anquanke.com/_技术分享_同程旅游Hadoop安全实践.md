> 原文链接: https://www.anquanke.com//post/id/85343 


# 【技术分享】同程旅游Hadoop安全实践


                                阅读量   
                                **154326**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



**[![](https://p0.ssl.qhimg.com/t0191ae94dffb4f3bfe.jpg)](https://p0.ssl.qhimg.com/t0191ae94dffb4f3bfe.jpg)**

**0x01 背景**

当前大一点的公司都采用了共享Hadoop集群的模式[[1]](http://dongxicheng.org/mapreduce/hadoop-security/)。

共享Hadoop是指：数据存储方面，公有/私有的文件目录混合存放在hdfs上，不同的用户根据需求访问不同的数据; 计算资源方面，管理员按部门或业务划分若干个队列，每个队列分配一定量的资源，每个用户/组只能使用某个队列中得资源。这种模式可以减小维护成本，避免数据过度冗余，减少硬件成本。但这种类似于云存储/云计算的方式，面临的一个最大问题就是安全。在同程，信息安全是渗透到每个部门的，数据安全又是重中之重。本文就Hadoop安全分享了同程旅游大数据架构部在这方面的实践。

然而，Hadoop是缺乏安全机制的。其中最关键的一个问题是，Client的用户名和用户组名的随意性。Hadoop默认从环境变量中取HADOOP_USER_NAME作为当前用户名，如果为空则从系统参数里取HADOOP_USER_NAME，如果还为空则获取当前系统用户名，添加到user.name和group.name属性中。用户甚至可以通过conf.set(“user.name”,root),conf.set(“group.name”,”root”)直接指定用户名和用户组为root。这样提交到集群的请求就可以以root的身份读写本不属于自己的文件目录，使用本属于别人的计算资源。

Hadoop团队也意识到了数据安全方面的缺失，并增加了权限认证授权机制。用户的login name会通过RPC头部传递给RPC，之后RPC使用Simple Authentication and Security Layer（SASL）确定一个权限协议（一般使用kerberos协议），完成RPC授权[[2]](https://issues.apache.org/jira/browse/HADOOP-6419/)。然而，在hadoop集群中启用kerberos认证有以下一些问题：

1. Kerberos生成证书和配置步骤十分复杂，debug排错也晦涩，没有一定经验很难上手;  2. 延展性不佳。机器的扩容和减少都要造成证书的重新生成和分发，给运维造成很大困难； 3. 存在单点失败，中心KDC中心服务器承载所有用户的密钥，挂掉时整个系统可能瘫痪。同时要求严格的时钟同步，不然会导致认证失败。

基于以上的原因，以及同程自身Hadoop集群的特性(总承载接近数十P的数据量，日增数十T ，上层依赖上百个平台/服务，数万+的数据搬运/运算任务)，给Hadoop增加安全机制无疑是给高速运行的汽车换轮子，要求系统做到服务零中断，滚动升级无停机。我们自主研发了一个轻量级的Hadoop用户认证机制。

<br>

**0x02 基本构想**

身份验证最常见的方法就是用户名和密码校验，符合我们简单易用的要求。首先，我们要让用户在与Hadoop交互之前读取到一个配置好的，和用户自身相关联的密码，将此密码保存并携带在每次与Hadoop交互的请求中以供验证。另外，我们知道用户在对Hadoop做任何操作之前都会和namenode交互，拿到相关的block的信息，文件读写的租约等等。那很自然的想到可以在namenode 这层做用户身份验证操作。而用户名和密码的映射表可以通过配置和远程RPC 的形式实现热加载。

<br>

**0x03 具体实施**

**用户加载密码**

用户信息在Hadoop里是以UserGroupInformation这个类实现的。如果subject为空，或者对应的principal为空，说明尚未登录过，就会调用getLoginUser()方法。首先会创建LoginContext，并调用login()方法，完成后调用login.commit()。我们在commit()方法中加入读取密码配置的操作，并存储在subject的credential中。密码可以配置在用户的home目录下，或者classpath下。由于login方法只会在用户第一次启动的时候调用，所以避免了重复加载的问题。

**Namenode加载用户名和密码的映射表**

我们新增加了一个让namenode 读取集群用户名和密码的映射表的RPC服务。目前Hadoop大部分的 RPC 调用已经采用google的protobuf 协议，替代了1.0时代自己的一套writable的协议。

我们根据protobuf的规范，定义一个叫做RefreshCheckUserPaswordProtocol.proto的协议文件，在文件里我们分别定义RPC调用的请求和应答消息

```
message RefreshCheckUserPasswordRequestProto`{``}`
messageRefreshCheckUserPasswordResponseProto `{``}`
```

内容为空，因为不需要传入参数再定义调用的服务

```
service RefreshCheckUserPasswordProtocolService `{`
    rpcrefreshCheckUserPassword()
    returns(RefreshCheckUserPasswordResponseProto);
`}`
```

通过protobuf命令行工具生成对应的request,response,以及service 的java类

因为新增的协议是在namenode上执行的，所以要注册在namenodeProtocols里

```
extendsClientProtocol,
      DatanodeProtocol,
      NamenodeProtocol,
      RefreshAuthorizationPolicyProtocol,
      RefreshUserMappingsProtocol,
      RefreshCallQueueProtocol,
      GenericRefreshProtocol,
      GetUserMappingsProtocol,
      HAServiceProtocol,
      RefreshCheckUserPasswordProtocol`{``}`
```

并且在namenodeProtocols的实现类NameNodeRpcServer里增加具体函数调用

```
RefreshCheckUserPasswordProtocolServerSideTranslatorPB refreshCheckUserPasswordXlator ();
BlockingService RefreshCheckUserPasswordProtocolService
        .newReflectiveBlockingService(refreshCheckUserPasswordXlator);
```

在dfsadmin的shell命令行中增加了调用此服务的入口

```
(.(cmd))`{`
        exitCoderefreshCheckUserPassword();
    `}`
    () throwsIOException `{`
        Configuration getConf();
        .set(CommonConfigurationKeys.HADOOP_SECURITY_SERVICE_USER_NAME_KEY,
                .get(DFSConfigKeys.DFS_NAMENODE_KERBEROS_PRINCIPAL_KEY, ));
        DistributedFileSystem getDFS();
        URI .getUri();
        HAUtil.isLogicalUri(, );
        () `{`
            .getHost();
            ListProxyAndInfoRefreshCheckUserPasswordProtocolHAUtil.getProxiesForAllNameNodesInNameservice(, ,
                            RefreshCheckUserPasswordProtocol.);
            (ProxyAndInfoRefreshCheckUserPasswordProtocol) `{`
                `{`
                    .getProxy().refreshCheckUserPassword();
                    ..println(.getAddress());
                `}`(e)`{`
                    ..println(.getAddress());
                    ..println(e.getMessage());
                `}`
            `}`
        `}` `{`
            RefreshCheckUserPasswordProtocolrefreshProtocol NameNodeProxies.createProxy(,FileSystem.getDefaultUri(),
                            RefreshCheckUserPasswordProtocol.).getProxy();
            refreshProtocol.refreshCheckUserPassword();
            ..println();
        `}`
        ;
    `}`
```

最后，我们在namenode启动(初始化完成)时自动加载一次用户名和密码的映射表。

具体位置在NameNode类的void initialize(Configuration conf) throws IOException方法的最后

**Namenode 对client做身份验证**

Namenode 接收到用户请求的时候都调用getRemoteUser()方法将用户的信息组装成UserGroupInformation实例。这时候我们就很自然的把请求发起者的用户名，密码以及源IP提取出来，做用户身份验证。用户验证的逻辑很简单，将用户名，密码，IP在启动时加载的映射表中查找对比，符合条件的予以通过，不然就拦截请求并抛出错误。

<br>

**0x04 上线的一些工作**

为了做到新增的用户安全功能平滑上线，我们做了下面几个额外的功能

**用户验证的全局开关**

防止新功能的可能出现的bug, 一键开关可以迅速关闭新功能，做到快速回滚。

**用户白名单**

用户群的数量很多，同一时间切换上线是不可能的。我们将用户放入白名单中，分批配置/测试分配的账号和密码，一步一个脚印的实现所有账号的安全监管

<br>

**0x05 上线过程**

1. 重新编译打包hadoop-common和hadoop-hdfs 工程

2. 替换namenode 和datanode 上的相应jar包，并滚动重启。因为默认是关闭安全功能的，所以新版本的jar包和旧版本的jar是相互兼容的。

3. 在各节点，各项目中配置和用户名和密码，通过命令将用户名和密码的映射表加载至namenode

4. 一键开启安全配置

目前，Hadoop安全已成功上线，升级过程中没有服务中断或降级，做到业务零感知。运行几个月下来也很平稳，性能良好。

<br>

**Reference**

[1] 董的博客 [http://dongxicheng.org/mapreduce/hadoop-security/](http://dongxicheng.org/mapreduce/hadoop-security/)

[2] Hadoop jira – 6419 [https://issues.apache.org/jira/browse/HADOOP-6419/](https://issues.apache.org/jira/browse/HADOOP-6419/)

搜索“同程安全”关注YSRC公众号，招各种安全岗，欢迎推荐。

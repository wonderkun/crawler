> 原文链接: https://www.anquanke.com//post/id/250959 


# 浅谈云上攻防——Kubelet访问控制机制与提权方法研究


                                阅读量   
                                **18975**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t0165a5e977274eaded.jpg)](https://p1.ssl.qhimg.com/t0165a5e977274eaded.jpg)



## 背景

本文翻译整理自rhino安全实验室：近些年针对kubernetes的攻击呈现愈演愈烈之势，一旦攻击者在kubernetes集群中站稳脚跟就会尝试渗透集群涉及的所有容器，尤其是针对访问控制和隔离做的不够好的集群受到的损害也会越大。例如由unit 42研究人员检测到的TeamTNT组织的恶意软件Siloscape就是利用了泄露的AWS凭证或错误配置从而获得了kubelet初始访问权限后批量部署挖矿木马或窃取关键信息如用户名和密码，组织机密和内部文件，甚至控制集群中托管的整个数据库从而发起勒索攻击。根据微步在线的统计上一次遭受其攻击的IP地址90%以上属于中国，因此需要安全人员及时关注并提前规避风险。Siloscape具体攻击流程如图1所示。

[![](https://p5.ssl.qhimg.com/t01230e077cd99bfb32.jpg)](https://p5.ssl.qhimg.com/t01230e077cd99bfb32.jpg)

图 1-Siloscape攻击流程

Kubernetes集群中所有的资源的访问和变更都是通过kubernetes API Server的REST API实现的，所以集群安全的关键点就在于如何识别并认证客户端身份并且对访问权限的鉴定，同时K8S还通过准入控制的机制实现审计作用确保最后一道安全底线。除此之外K8S还配有一系列的安全机制（如Secret和Service Account等）共同实现集群访问控制的安全，具体请求如图2所示：

[![](https://p3.ssl.qhimg.com/t01022901c80d13d9fe.png)](https://p3.ssl.qhimg.com/t01022901c80d13d9fe.png)

图 3-Kubectl操作



## K8S认证鉴权

### 认证阶段（Authentication）

认证阶段即判断用户是否为能够访问集群的合法用户，API Server目前提供了三种策略多种用户身份认证方式，他们分别如下表1：
<td valign="top" width="36">序号</td><td valign="top" width="146">认证策略</td><td valign="top" width="276">认证方式</td>
<td valign="top" width="24">1</td><td valign="top" width="152">匿名认证</td><td valign="top" width="276">Anonymous requests</td>
<td valign="top" width="24">2</td><td valign="top" width="152">白名单认证</td><td valign="top" width="276">BasicAuth认证</td>
<td valign="top" width="24">3</td><td valign="top" width="152">Token认证</td><td valign="top" width="276">Webhooks、Service Account Tokens、OpenID Connect Tokens等</td>
<td valign="top" width="24">4</td><td valign="top" width="152">X509证书认证</td><td valign="top" width="270">clientCA认证，TLS bootstrapping等</td>

表 1-认证

其中X509是kubernetes组件间默认使用的认证方式，同时也是kubectl客户端对应的kube-config中经常使用到的访问凭证，是一种比较安全的认证方式。

### 鉴权阶段（Authorization）

当API Server内部通过用户认证后，就会执行用户鉴权流程，即通过鉴权策略决定一个API调用是否合法，API Server目前支持以下鉴权策略
<td valign="top" width="38">序号</td><td valign="top" width="121">鉴权策略</td><td valign="top" width="316">概述</td>
<td valign="center" width="14">1</td><td valign="center" width="121">Always</td><td valign="top" width="310">分为AlwaysDeny和AlwaysAllow，当集群不需要鉴权时选择AlwaysAllow</td>
<td valign="top" width="14">2</td><td valign="top" width="121">ABAC</td><td valign="top" width="310">基于属性的访问控制</td>
<td valign="top" width="14">3</td><td valign="top" width="121">RBAC</td><td valign="top" width="310">基于角色的访问控制</td>
<td valign="top" width="14">4</td><td valign="top" width="121">Node</td><td valign="top" width="310">一种对kubelet进行授权的特殊模式</td>
<td valign="top" width="14">5</td><td valign="top" width="121">Webhook</td><td valign="top" width="310">通过调用外部REST服务对用户鉴权</td>

表 2-鉴权

其中Always策略要避免用于生产环境中，ABAC虽然功能强大但是难以理解且配置复杂逐渐被RBAC替代，如果RBAC无法满足某些特定需求，可以自行编写鉴权逻辑并通过Webhook方式注册为kubernetes的授权服务，以实现更加复杂的授权规则。而Node鉴权策略主要是用于对kubelet发出的请求进行访问控制，限制每个Node只访问它自身运行的Pod及相关Service、Endpoints等信息。

### 准入控制（Admission Control）

突破了如上认证和鉴权关卡之后，客户端的调用请求还需要通过准入控制的层层考验，才能获得成功的响应，kubernetes官方标准的选项有30多个，还允许用户自定义扩展。大体分为三类验证型、修改型、混合型，顾名思义验证型主要用于验证k8s的资源定义是否符合规则，修改型用于修改k8s的资源定义，如添加label，一般运行在验证型之前，混合型及两者的结合。

AC以插件的形式运行在API Server进程中，会在鉴权阶段之后，对象被持久化etcd之前，拦截API Server的请求，对请求的资源对象执行自定义（校验、修改、拒绝等）操作。



## Kubelet认证鉴权

### 认证

Kubelet目前共有三种认证方式:

1.允许anonymous，这时可不配置客户端证书

```
authentication:
    anonymous:
        enabled: true
```

2.webhook，这时可不配置客户端证书

```
authentication:
    webhook:
      enabled: true
```

3.TLS认证，也是目前默认的认证方式，对kubelet 的 HTTPS 端点启用 X509 客户端证书认证。

```
authentication:
    anonymous:
        enabled: false
    webhook:
      enabled: false
    x509:
      clientCAFile: xxxx
```

然而在实际环境当你想要通过kubectl命令行访问kubelet时，无法传递bearer tokens，所以无法使用webhook认证，这时只能使用x509认证。

### 鉴权

kubelet可配置两种鉴权方式分别为AlwaysAllow和Webhook，默认的及安全模式AlwaysAllow，允许所有请求。而Webhook的鉴权过程时委托给API Server的，使用API Server一样的默认鉴权模式即RBAC。

通常在实际环境中需要我们通过TBAC为用户配置相关权限，包括配置用户组以及其相对应的权限。并最终将用户和角色绑定完成权限的配置。

### TLS bootstrapping

TLS在实际实现的时候成本较高，尤其集群中众多的kubelet都需要与kube-API Server通信，如果由管理员管理证书及权限，很有可能会因为证书过期等问题出现混乱。这时候Kubelet TLS Bootstrapping就应运而生了。其主要实现两个功能第一，实现kubelet与kube-API Server之间的自动认证通信；第二，限制相关访问API Server的权限。

K8s目前默认通过TLS bootstrapping这套机制为每个kubelet配置签名证书确保与API Server的交互安全。其核心思想是由kubelet自已生成及向API Server提交自已的证书签名请求文件（CSR），k8s-master对CSR签发后，kubelet再向API Server获取自已的签名证书，然后再正常访问API Server。具体如图所示：

[![](https://p2.ssl.qhimg.com/t01b97b05c891b23b66.png)](https://p2.ssl.qhimg.com/t01b97b05c891b23b66.png)

图 4-Kubelet TLS bootstrapping工作流程



## Kubelet提权案例

### 攻击路径

为了演示kubelet提权攻击，下面会展示一个简单的攻击场景，从获取TLS引导凭据开始，最终获得集群中集群管理员的访问权限。

[![](https://p2.ssl.qhimg.com/t012580eed9e6ccfc91.png)](https://p2.ssl.qhimg.com/t012580eed9e6ccfc91.png)

### 攻击步骤

由于Kubelet需要依据凭据与API服务器通信，当攻击者已经控制了集群中部分运行的容器后可以依托这些凭据访问API服务器，并通过提权等手段来造成更大的影响。

1、首先攻击者需要获取到Node权限并找到kubelet TLS引导凭据，见下图：

2、尝试使用TLS凭证检索有关kubernetes节点的信息，由于这些凭据仅有创建和检索证书签名请求的权限即引导凭据用来向控制端提交证书签名请求（CSR）所以通常会看到找不到相关资源。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01f2bf78b2e9f7021a.png)

其中kubectl auth can-i子命令有助于确定当前凭证是否可以执行相关命令。

3、由于权限不足，可以使用get csr尝试成为集群中的假工作节点，这样将允许我们执行更多的命令如列出节点、服务和pod等，但是仍然无法获取更高级别的数据。

我们使用cfssl为假节点生成CSR，同时将其提交至API Server供其自动批准该证书，通常情况下kube-controller-manager设置为自动批准与前缀一致的签名请求，并发出客户证书，随后该节点的kubelet即可用于常用功能。

[![](https://p4.ssl.qhimg.com/t01ed8422ab8eaf69c3.png)](https://p4.ssl.qhimg.com/t01ed8422ab8eaf69c3.png)

[![](https://p4.ssl.qhimg.com/t01c60e26d0c05868c4.png)](https://p4.ssl.qhimg.com/t01c60e26d0c05868c4.png)

4、之后我们将批准通过的证书保存，此时即可查看节点信息等相关内容。

[![](https://p0.ssl.qhimg.com/t01b26107e564f9b2d7.png)](https://p0.ssl.qhimg.com/t01b26107e564f9b2d7.png)

[![](https://p5.ssl.qhimg.com/t0128c8a99daa698a97.png)](https://p5.ssl.qhimg.com/t0128c8a99daa698a97.png)

5、为了获取更高的权限，我们尝试使用另一个工作节点生成新的CSR，并要求API Server自动通过该证书。

[![](https://p5.ssl.qhimg.com/t011ce05a921c75a5cd.png)](https://p5.ssl.qhimg.com/t011ce05a921c75a5cd.png)

[![](https://p5.ssl.qhimg.com/t01be5879348db60b8d.png)](https://p5.ssl.qhimg.com/t01be5879348db60b8d.png)

6、我们将新批准的证书保存并以此证书检查相关的pod信息发现有了密钥信息，但是当我们尝试去读取的时候仍然显示权限不足。

[![](https://p4.ssl.qhimg.com/t01f18deedd5337cbec.png)](https://p4.ssl.qhimg.com/t01f18deedd5337cbec.png)

[![](https://p2.ssl.qhimg.com/t017886d4d808e9a49c.png)](https://p2.ssl.qhimg.com/t017886d4d808e9a49c.png)

[![](https://p3.ssl.qhimg.com/t010f60542ab42976cc.png)](https://p3.ssl.qhimg.com/t010f60542ab42976cc.png)

[![](https://p3.ssl.qhimg.com/t01c7e0cabc4a818f2f.png)](https://p3.ssl.qhimg.com/t01c7e0cabc4a818f2f.png)

7、我们再次尝试其他pod看是否拥有更高级别的权限，重复之前的证书制作并发送至API Server请求批准，这次权限明显高了许多，我们成功获取到了ca.crt以及token。

[![](https://p4.ssl.qhimg.com/t010071e582d7dd5e2b.png)](https://p4.ssl.qhimg.com/t010071e582d7dd5e2b.png)

8、接下来我们尝试使用该token，设置好环境变量并获取默认命名空间中的所有资源。

[![](https://p4.ssl.qhimg.com/t01ea566acc098ef014.png)](https://p4.ssl.qhimg.com/t01ea566acc098ef014.png)

[![](https://p4.ssl.qhimg.com/t01efadac7f32a15386.png)](https://p4.ssl.qhimg.com/t01efadac7f32a15386.png)

9、最后我们检查其角色的绑定，发现该服务账户已于“cluster-admin”角色绑定。

[![](https://p1.ssl.qhimg.com/t0162282aee35ab6243.png)](https://p1.ssl.qhimg.com/t0162282aee35ab6243.png)

[![](https://p3.ssl.qhimg.com/t01998d296df6eac8e1.png)](https://p3.ssl.qhimg.com/t01998d296df6eac8e1.png)

即其为最高权限的账户，至此我们可以执行各种不同的攻击。如从工作节点的实例窃取服务账户令牌访问云资源、列出配置、创建特权容器、后门容器等。

Kubernetes具有广泛的攻击面，其中kubelet尤为重要，本案例通过泄露的凭据开始，通过列出相关节点、实例生成和提交CSR充当工作节点，并最终获得集群管理员访问权限从而窃取TLS Bootstrap凭据。



## 缓解措施

在实际生产环境中，一定要保护好kubelet凭证的数据避免类似的提权事件发生，同时还可以搭配以下几点方式来加固k8s的安全。

1、保护好元数据，元数据由于其敏感性务必在服务后台加强对元数据读取的管控，避免攻击者通过元数据读取到相关凭据信息，哪怕是低权限的凭据。

2、通过更安全的网络策略避免类似提权事件发生，默认情况下拒绝所有出站通信，然后根据需要将出站流量列入白名单。在pod上应用该网络策略，因为需要访问API服务器和元数据的是node而不是pod。

3、启用类似Istio这样的服务网格并配置egress gateway，这将阻止部署在服务网格中的任何容器与任何未经授权的主机进行通信

4、限制对主节点的网络访问，如上案例基本都发生在集群，所以传统的vpn也无法阻止相关危害，用户可以直接限制对主服务器的访问来避免k8s的许多攻击。

### 参考文献

1.https://www.cnblogs.com/huanglingfa/p/13773234.html

2.https://cloud.tencent.com/developer/article/1553947

3.https://kubernetes.io/zh/docs/reference/access-authn-authz/authentication/

4.https://mritd.com/2018/01/07/kubernetes-tls-bootstrapping-note/

翻译整理自：rhino安全实验室

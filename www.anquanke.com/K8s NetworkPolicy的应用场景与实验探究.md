> 原文链接: https://www.anquanke.com//post/id/239946 


# K8s NetworkPolicy的应用场景与实验探究


                                阅读量   
                                **271038**
                            
                        |
                        
                                                                                    



[![](https://p0.ssl.qhimg.com/t01083177cc33ba7db7.jpg)](https://p0.ssl.qhimg.com/t01083177cc33ba7db7.jpg)



## 前言

现如今，K8s（Kubernetes）已经成为业界容器编排的事实标准，正推动着云原生应用、微服务架构等热门技术的普及和落地。随着分布式架构的选用，网络安全的重要性愈发明显。

本文的主要内容包括以下几部分：（1）简介K8s 容器网络面临安全考验；（2）简介可用于K8s容器网络隔离的资源对象NetworkPolicy（即，网络策略）；（3）详细讲解几个K8s NetworkPolicy的实验；（4）总结与展望。

希望本文可以帮助读者了解云原生网络安全问题以及K8s的NetworkPolicy的技术应用。也请各位读者朋友帮忙指正。



## K8s容器网络面临安全考验

在默认配置下，K8s底层网络是“全连通”的，即在同一集群内运行的所有Pod都可以自由通信。因此，存在于传统物理网络（如ARP欺骗）与传统单体应用的攻击手段（如OWASP Top10）对于容器网络仍然“有的放矢”。此外攻击者若控制了宿主机的一些容器（或可通过编排创建容器），还可对宿主机或其他容器发起云原生场景的渗透攻击。

如图2-1所示，攻击者可以立足于某个有缺陷的容器发起横向攻击。图2-2的攻防矩阵是攻击者常用的技战术。

[![](https://p1.ssl.qhimg.com/t01fde637d5edbbbe22.png)](https://p1.ssl.qhimg.com/t01fde637d5edbbbe22.png)

图2-1

[![](https://p5.ssl.qhimg.com/t019ebb154362f2f080.png)](https://p5.ssl.qhimg.com/t019ebb154362f2f080.png)

图2-2

此外，在云原生、微服务的场景下，内部网络的东西向通信流量剧增、边界变得更加模糊以及容器生命周期可能较短等特征为“网络的隔离”以及“应用程序容器和服务的保护”提出了新的考验。



## K8s NetworkPolicy简介

本章的主要内容是对K8s NetworkPolicy的概念及配置项进行简介。

### K8s NetworkPolicy助力容器网络隔离

为了实现细粒度的容器网络访问隔离策略，K8s自1.3版本起，由SCI-Network小组主导研发了NetworkPolicy机制，并已升级为稳定版本。

NetworkPolicy的设置主要用于对目标Pod的网络访问进行限制。在默认情况下，对所有Pod都是允许访问的，在设置了指向Pod的网络策略之后，到Pod的访问可被限制。

如图2-1，笔者画的网络策略功能图所示，NetworkPolicy有着较强的可定制性，它支持使用“Label标签”选定目标Pod，对该目标Pod的入站流量和出站流量做IP网段、命名空间以及应用（Pod）做端口级的网络访问控制策略。

[![](https://p0.ssl.qhimg.com/t013a7ada161c937892.png)](https://p0.ssl.qhimg.com/t013a7ada161c937892.png)

图3-1

其基于Label的管理方式贴合K8s的用习惯，有助于用户快速进行应用级或微服务级的网络隔离容器编排。以图2-2为例，编排人员可以通过Label筛选出测试环境（Label:Test）或生产环境（Label:Prod）的资源对象，并分而治之。

[![](https://p3.ssl.qhimg.com/t01086356eb344be524.png)](https://p3.ssl.qhimg.com/t01086356eb344be524.png)

图3-2

用户在做K8s编排时，仅定义一个NetworkPolicy是无法完成实际的网络隔离的，还需要一个策略控制器（Policy Controller）进行策略的实现。策略控制器须由第三方网络组件提供，目前Calico、Cilium、Kube-router、Romana、 Weave-net等开源项目均支持NetworkPolicy的实现[1]。

为了帮助暂不了解K8s的读者补充预备知识，此处对K8s中的Pod、Service以及Namespace进行补充介绍。请已经理解这些概念的读者略过这些补充介绍。

（1）Pod

Pod是K8s的最小调度单位。每个Pod都有一个独立的IP，并可以由一个或多个容器组合而成（一般把有“亲密关系”的容器放到一个Pod，使它们可以通过localhost互相访问，例如把经典的“Nginx+php-fpm”组合放在一个Pod内，调度起来更方便），同一个Pod中的容器会自动地分配到同一个物理机或虚拟机上。K8s的网络设计模型的一个基本原则是：每个Pod都拥有一个独立的IP地址，而且假定所有Pod都在一个可以互相连通、扁平的网络空间中（这会使得Pod间的网络隔离性不足）。

由于Pod是临时性的，Pod的“IP:port”也是动态变化的，这种动态变化在k8s集群中就涉及到一个问题：如果一组后端Pod作为服务提供方，供一组前端的Pod所调用，那服务调用方怎么自动感知服务提供方的变化？这就引入了k8s中的另外一个核心概念——Service。

（2）Service

Service也是k8s的核心资源对象（可将k8s里的每个Service理解为“微服务架构”中的一个微服务）Pod、RC（Replication Controller，副本控制器）、Service的逻辑关系如图2-3所示。

[![](https://p5.ssl.qhimg.com/t0129097533d69e2273.png)](https://p5.ssl.qhimg.com/t0129097533d69e2273.png)

图2-3

由图3可知，k8s的Service定义了一个服务的访问入口地址，前端的应用（Pod）通过这个入口地址访问其背后的一组由于Pod副本组成的集群实例，Service与其后端Pod之间则是通过**Label Selector**（Label键值对可以被附加到各个对象资源上，如Node、Pod、Service、RC）来实现无缝对接的。RC可声明某种Pod的副本数量在任意时刻都符合某个预期值。

RC配置文件可为所创建的Pod附加Label；Service配置文件可为所创建的Service选取所需的Pod，选取的依据是Lable，如图2-4所示。

[![](https://p2.ssl.qhimg.com/t011496fbbb18782969.png)](https://p2.ssl.qhimg.com/t011496fbbb18782969.png)

图2-4

图2-5是K8s的集群示意图， 由图可知，每一个Node节点中有多个Pod，每一个Service可能横跨多个Node，也可能一个Node里面包含多个Service（可以把Node理解为真实世界中的一台服务器，Service可以是单机或多机负载的服务，Node与Service之间没有从属关系）。

[![](https://p1.ssl.qhimg.com/t011ddfaa845226b477.png)](https://p1.ssl.qhimg.com/t011ddfaa845226b477.png)

图2-5

（3）Namespace

Namespace(命名空间)是对一组资源和对象的抽象集合，可用于实现多租户的资源隔离，比如可以用来将系统内部的对象划分为不同的项目组或用户组。常见的pods, services, replication controllers和deployments等都是属于某一个namespace的（默认是default），而node, persistentVolumes等则不属于任何namespace[3]。

### K8s NetworkPolicy配置说明

用户可以自定义的NetworkPolicy yaml格式示例如下：
<td class="ql-align-justify" data-row="1">apiVersion: networking.k8s.io/v1</td><td class="ql-align-justify" data-row="1">kind: NetworkPolicy</td><td class="ql-align-justify" data-row="1">metadata:</td><td class="ql-align-justify" data-row="1">  name: test-network-policy #网络策略的名称</td><td class="ql-align-justify" data-row="1">  namespace: default     #命名空间的名称</td><td class="ql-align-justify" data-row="1">spec:</td><td class="ql-align-justify" data-row="1">  podSelector:           #该网络策略所作用的Pod范围</td><td class="ql-align-justify" data-row="1">    matchLabels:         #本例的选择条件为包含“role=db”标签的pod</td><td class="ql-align-justify" data-row="1">      role: db</td><td class="ql-align-justify" data-row="1">  policyTypes:            #网络策略的类型</td><td class="ql-align-justify" data-row="1">  – Ingress               #入站网络限制</td><td class="ql-align-justify" data-row="1">  – Egress                #出站网络限制</td><td class="ql-align-justify" data-row="1">  ingress:                #允许访问目标Pod的入站白名单规则</td><td class="ql-align-justify" data-row="1">  – from:                 #对符合条件的客户端Pod进行网络放行</td><td class="ql-align-justify" data-row="1">    – ipBlock:             #基于客户端的IP范围</td><td class="ql-align-justify" data-row="1">        cidr: 172.17.0.0/16</td><td class="ql-align-justify" data-row="1">        except:</td><td class="ql-align-justify" data-row="1">        – 172.17.1.0/24</td><td class="ql-align-justify" data-row="1">    – namespaceSelector:   #基于客户端Pod所在的命名空间的Label</td><td class="ql-align-justify" data-row="1">        matchLabels:</td><td class="ql-align-justify" data-row="1">          project: myproject</td><td class="ql-align-justify" data-row="1">    – podSelector:         #基于客户端Pod的Label</td><td class="ql-align-justify" data-row="1">        matchLabels:</td><td class="ql-align-justify" data-row="1">          role: frontend</td><td class="ql-align-justify" data-row="1">    ports:</td><td class="ql-align-justify" data-row="1">    – protocol: TCP</td><td class="ql-align-justify" data-row="1">      port: 6379         #允许访问的目标Pod监听的端口号</td><td class="ql-align-justify" data-row="1">  egress:                #定义目标Pod允许访问的“出站”白名单规则</td><td class="ql-align-justify" data-row="1">  – to:                  #目标Pod被允许访问的满足to条件的服务端IP范围</td><td class="ql-align-justify" data-row="1">    – ipBlock:</td><td class="ql-align-justify" data-row="1">        cidr: 10.0.0.0/24</td><td class="ql-align-justify" data-row="1">    ports:</td><td class="ql-align-justify" data-row="1">    – protocol: TCP</td><td class="ql-align-justify" data-row="1">      port: 5978         #和ports定义的端口号</td>

除了用户可自定义外，K8s还在Namespace级别设置了一些默认的全局网络策略，以方便管理员对整个Namespace进行统一的网络策略设置。比如：

（1）默认禁止任何客户端访问该Namespace中的所有Pod；

（2）默认允许任何客户端访问该Namespace中的所有Pod；

（3）默认禁止该Namespace中的所有Pod访问外部服务；

（4）默认允许该Namespace中的所有Pod访问外部服务；

（5）默认禁止任何客户端访问该Namespace中的所有Pod，同时禁止访问外部服务。



## K8s NetworkPolicy实验

本章将先简单介绍“K8s NetworkPolicy应用隔离”的实验环境，接着详细介绍几个应用隔离实验，希望可以帮助读者了解K8s的NetworkPolicy的基本用法。

### 实验环境

本文实验环境是用CentOS 7搭建的一个K8s集群，集群中有1个Master节点及2个Node节点，该集群已经安装了网络插件“Calico”。

注： Calico是一个基于BGP的纯三层网络方案，与OpenStack、Kubernetes、AWS、GCE等平台都能够良好地集合，是企业级应用的主流[4]。Calico基于iptables还提供了丰富的网络策略，不仅实现了Kubernetes的NetworkPolicy策略，还可提供容器网络可达性限制的功能。参考的安装步骤可参见参考资料[5]。

### 使用“访问标签Label”限制通往某应用的流量

下面以一个提供服务的Nginx Pod为例，为两个客户端Pod设置不同的网络访问权限，允许包含Lable“role=nginxclient”的Pod访问Nginx容器，而拒绝不包含该Label的容器访问。为实现这一需求，需要通过以下步骤完成。

（1）创建Nginx Pod，并添加Label“app=nginx”。编排文件my-nginx.yaml的内容如下。
<td class="ql-align-justify" data-row="1">apiVersion: v1</td><td class="ql-align-justify" data-row="1">kind: Pod</td><td class="ql-align-justify" data-row="1">metadata:</td><td class="ql-align-justify" data-row="1">  name: nginx</td><td class="ql-align-justify" data-row="1">  labels:</td><td class="ql-align-justify" data-row="1">    app: nginx</td><td class="ql-align-justify" data-row="1">spec:</td><td class="ql-align-justify" data-row="1">  containers:</td><td class="ql-align-justify" data-row="1">  – name: nginx</td><td class="ql-align-justify" data-row="1">    image: nginx</td>

由图4-1可知，该Pod被创建成功了。

[![](https://p2.ssl.qhimg.com/t019a9b34fe4eda07a2.png)](https://p2.ssl.qhimg.com/t019a9b34fe4eda07a2.png)

图4-1

（2）为步骤1创建的Nginx Pod设置网络策略，编排文件networkpolicy-allow-nginxclient.yaml的内容如下。
<td class="ql-align-justify" data-row="1">kind: NetworkPolicy</td><td class="ql-align-justify" data-row="1">apiVersion: networking.k8s.io/v1</td><td class="ql-align-justify" data-row="1">metadata:</td><td class="ql-align-justify" data-row="1">  name: allow-nginxclient</td><td class="ql-align-justify" data-row="1">spec:</td><td class="ql-align-justify" data-row="1">  podSelector:</td><td class="ql-align-justify" data-row="1">    matchLabels:</td><td class="ql-align-justify" data-row="1">app: nginx</td><td class="ql-align-justify" data-row="1">  ingress:</td><td class="ql-align-justify" data-row="1">    – from:</td><td class="ql-align-justify" data-row="1">      – podSelector:</td><td class="ql-align-justify" data-row="1">          matchLabels:</td><td class="ql-align-justify" data-row="1">role: nginxclient</td><td class="ql-align-justify" data-row="1">      ports:</td><td class="ql-align-justify" data-row="1">      – protocol: TCP</td><td class="ql-align-justify" data-row="1">port: 80</td>

上述编排文件的关键信息包括了：目标Pod应包含Label“app=nginx”、允许访问的客户端Pod应包含Label“role=nginxclient”以及客户端所允许访问的“Nginx Pod端口”为80。

执行以下命令创建该NetworkPolicy资源对象：
<td class="ql-align-justify" data-row="1">kubectl create -f networkpolicy-allow-nginxclient.yaml</td>

由图4-2可知，该NetworkPolicy被创建成功了。

[![](https://p1.ssl.qhimg.com/t01f64a84848859c53c.png)](https://p1.ssl.qhimg.com/t01f64a84848859c53c.png)图4-2

（3）创建两个客户端Pod，一个包含Label“role=nginxclient”，而另一个无此Label。并分别进入这两个Pod中执行命令对Nginx Pod的80端口发起网络请求，以验证网络策略的效果。

busybox-client2.yaml的内容如下：
<td class="ql-align-justify" data-row="1">apiVersion: v1</td><td class="ql-align-justify" data-row="1">kind: Pod</td><td class="ql-align-justify" data-row="1">metadata:</td><td class="ql-align-justify" data-row="1">  name: busybox2</td><td class="ql-align-justify" data-row="1">  namespace: default</td><td class="ql-align-justify" data-row="1">spec:</td><td class="ql-align-justify" data-row="1">  containers:</td><td class="ql-align-justify" data-row="1">  – name: busybox2</td><td class="ql-align-justify" data-row="1">    image: busybox:1.28.4</td><td class="ql-align-justify" data-row="1">    command:</td><td class="ql-align-justify" data-row="1">      – sleep</td><td class="ql-align-justify" data-row="1">      – “3600”</td><td class="ql-align-justify" data-row="1">    imagePullPolicy: IfNotPresent</td><td class="ql-align-justify" data-row="1">  restartPolicy: Always</td>

busybox-client4.yaml的内容如下（相比于busybox-client2.yaml，它多了Label“role: nginxclient”）：
<td class="ql-align-justify" data-row="1">apiVersion: v1</td><td class="ql-align-justify" data-row="1">kind: Pod</td><td class="ql-align-justify" data-row="1">metadata:</td><td class="ql-align-justify" data-row="1">  name: busybox4</td><td class="ql-align-justify" data-row="1">  namespace: default</td><td class="ql-align-justify" data-row="1">  labels:</td><td class="ql-align-justify" data-row="1">    role: nginxclient</td><td class="ql-align-justify" data-row="1">spec:</td><td class="ql-align-justify" data-row="1">  containers:</td><td class="ql-align-justify" data-row="1">  – name: busybox4</td><td class="ql-align-justify" data-row="1">    image: busybox:1.28.4</td><td class="ql-align-justify" data-row="1">    command:</td><td class="ql-align-justify" data-row="1">      – sleep</td><td class="ql-align-justify" data-row="1">      – “3600”</td><td class="ql-align-justify" data-row="1">    imagePullPolicy: IfNotPresent</td><td class="ql-align-justify" data-row="1">  restartPolicy: Always</td>

通过以下命令创建“busybox2”与“busybox4”这两个Pod：
<td class="ql-align-justify" data-row="1">kubectl create -f busybox-client2.yaml -f busybox-client4.yaml</td>

通过以下命令登录Pod“busybox2”，以执行命令：
<td class="ql-align-justify" data-row="1">kubectl exec -ti busybox2 — sh</td>

通过以下命令尝试连接Nginx容器的80端口：
<td class="ql-align-justify" data-row="1"># wget –timeout=5 10.244.3.14</td><td class="ql-align-justify" data-row="1">Connecting to 10.244.3.14 (10.244.3.14:80)</td><td class="ql-align-justify" data-row="1">wget: download timed out</td>

终端的回显是“download timed out”，这说明NetworkPolicy生效，对没有Label“role=nginxclient”的客户端Pod拒绝访问，实验结果如图4-3所示。

[![](https://p1.ssl.qhimg.com/t01079fded8fc574563.png)](https://p1.ssl.qhimg.com/t01079fded8fc574563.png)图4-3

通过以下命令登录Pod“busybox4”，以执行命令：
<td class="ql-align-justify" data-row="1">kubectl exec -ti busybox4 –sh</td>

尝试连接Nginx容器的80端口：
<td class="ql-align-justify" data-row="1">/ # wget 10.244.3.14</td><td class="ql-align-justify" data-row="1">Connecting to 10.244.3.14 (10.244.3.14:80)</td><td class="ql-align-justify" data-row="1">wget: can’t open ‘index.html’: File exists</td>

终端的回显是“can’t open ‘index.html’: File exists”，这说明成功访问到Nginx Pod，NetworkPolicy是生效的，对有Label“role=nginxclient”的客户端允许访问。

实验结果如图4-4所示。

[![](https://p0.ssl.qhimg.com/t01ea01a75bcc0cb13e.png)](https://p0.ssl.qhimg.com/t01ea01a75bcc0cb13e.png)图4-4

注：（1）查看NetworkPolicy的实验截图如图4-5所示。

[![](https://p2.ssl.qhimg.com/t016bdca5d322d0c0a5.png)](https://p2.ssl.qhimg.com/t016bdca5d322d0c0a5.png)

图4-5

（2）查看Pod所带的Labels实验截图如图4-6所示。

[![](https://p5.ssl.qhimg.com/t01446ef325e9e83fc3.png)](https://p5.ssl.qhimg.com/t01446ef325e9e83fc3.png)

图4-6

（3）删除NetworkPolicy的实验截图如图4-7所示。

[![](https://p3.ssl.qhimg.com/t0111f6c6942e98a5d6.png)](https://p3.ssl.qhimg.com/t0111f6c6942e98a5d6.png)

图4-7

### 拒绝/允许所有通往某应用的流量

由于此处的实验与2.2较为类似，故不对实验过程做赘述。为了拒绝所有通往某应用的流量，可参照以下NetworkPolicy：
<td class="ql-align-justify" data-row="1">kind: NetworkPolicy</td><td class="ql-align-justify" data-row="1">apiVersion: networking.k8s.io/v1</td><td class="ql-align-justify" data-row="1">metadata:</td><td class="ql-align-justify" data-row="1">name: nginx-deny-all</td><td class="ql-align-justify" data-row="1">spec:</td><td class="ql-align-justify" data-row="1">  podSelector:</td><td class="ql-align-justify" data-row="1">    matchLabels:</td><td class="ql-align-justify" data-row="1">app: nginx</td><td class="ql-align-justify" data-row="1">ingress: []</td>

上述编排文件的关键信息包括了：目标Pod应包含Label“app: nginx”、ingress（允许访问目标Pod的入站白名单规则）的属性值为“[]”（[]代表拒绝所有）。

若要允许所有通往某应用的流量，可参照以下NetworkPolicy：
<td class="ql-align-justify" data-row="1">kind: NetworkPolicy</td><td class="ql-align-justify" data-row="1">apiVersion: networking.k8s.io/v1</td><td class="ql-align-justify" data-row="1">metadata:</td><td class="ql-align-justify" data-row="1">  name: nginx-allow-all</td><td class="ql-align-justify" data-row="1">spec:</td><td class="ql-align-justify" data-row="1">  podSelector:</td><td class="ql-align-justify" data-row="1">    matchLabels:</td><td class="ql-align-justify" data-row="1">      app: nginx</td><td class="ql-align-justify" data-row="1">  ingress:</td><td class="ql-align-justify" data-row="1">  – `{``}`</td>

通过观察可知，该编排文件和前一个编排文件较为类似，主要的不同点在于ingress的属性值为“`{``}`”（`{``}`代表允许所有）。

### 拒绝所有通往某命名空间的流量

实验步骤如下：

（1）创建2个命名空间（ns_01、ns_02）
<td class="ql-align-justify" data-row="1"># kubectl create -f ns01.yaml -f ns02.yaml</td><td class="ql-align-justify" data-row="1">namespace/ns01 created</td><td class="ql-align-justify" data-row="1">namespace/ns02 created</td>

（2）创建2个Pod（指定busybox-ns01的网络命名空间为ns01；指定busybox-ns02的网络命名空间为ns02），如图4-8所示。

[![](https://p0.ssl.qhimg.com/t014d691fbee1ff9bae.png)](https://p0.ssl.qhimg.com/t014d691fbee1ff9bae.png)

图4-8

（3）测试Pod“busybox-ns01”与“busybox-ns02”的连通性

实验结果如图4-9所示，由图可知，虽然这两个Pod处于不同的命名空间，但这两个Pod是网络互通的。

[![](https://p1.ssl.qhimg.com/t0124926b21db39444d.png)](https://p1.ssl.qhimg.com/t0124926b21db39444d.png)

图4-9

（4）对网络命名空间“ns01”编写网络策略

networkpolicy-ns01-ingress-deny-all.yaml的代码如下：
<td class="ql-align-justify" data-row="1">kind: NetworkPolicy</td><td class="ql-align-justify" data-row="1">apiVersion: networking.k8s.io/v1</td><td class="ql-align-justify" data-row="1">metadata:</td><td class="ql-align-justify" data-row="1">  name: networkpolicy-ns01-ingress-deny-all</td><td class="ql-align-justify" data-row="1">spec:</td><td class="ql-align-justify" data-row="1">  podSelector: `{``}`</td><td class="ql-align-justify" data-row="1">  policyTypes:</td><td class="ql-align-justify" data-row="1">  – Ingress</td>

对网络命名空间“ns01”指定该网络策略，所执行的命令如下：
<td class="ql-align-justify" data-row="1"># kubectl apply -f networkpolicy-ns01-ingress-deny-all.yaml -n ns01</td>

测试结果如图4-10所示。

[![](https://p5.ssl.qhimg.com/t01197412b99de72906.png)](https://p5.ssl.qhimg.com/t01197412b99de72906.png)

图4-10

由图可知，网络策略生效。

### 允许某网段下通往某应用的流量

（1）对网段10.244.0.0/16编写网络策略

声明的NetworkPolicy如下：
<td class="ql-align-justify" data-row="1">apiVersion: networking.k8s.io/v1</td><td class="ql-align-justify" data-row="1">kind: NetworkPolicy</td><td class="ql-align-justify" data-row="1">metadata:</td><td class="ql-align-justify" data-row="1">  name: networkpolicy-ns01-ingress-allow-ip</td><td class="ql-align-justify" data-row="1">spec:</td><td class="ql-align-justify" data-row="1">  podSelector: `{``}`</td><td class="ql-align-justify" data-row="1">  policyTypes:</td><td class="ql-align-justify" data-row="1">  – Ingress</td><td class="ql-align-justify" data-row="1">  ingress:</td><td class="ql-align-justify" data-row="1">  – from:</td><td class="ql-align-justify" data-row="1">    – ipBlock:</td><td class="ql-align-justify" data-row="1">        cidr: 10.244.0.0/16</td>

（2）对网络命名空间“ns01”指定该网络策略，执行结果如图4-11所示。

[![](https://p1.ssl.qhimg.com/t01288b870fb37722fc.png)](https://p1.ssl.qhimg.com/t01288b870fb37722fc.png)

图4-11

（3）通过ping命令进行网络联通性测试

未删除NetworkPolicy，不可以ping通，如图4-12所示。

[![](https://p5.ssl.qhimg.com/t01c91bee0dd1089d31.png)](https://p5.ssl.qhimg.com/t01c91bee0dd1089d31.png)

图4-12

删除NetworkPolicy，可以ping通，如图4-13所示。

[![](https://p4.ssl.qhimg.com/t0186b579bb881b7262.png)](https://p4.ssl.qhimg.com/t0186b579bb881b7262.png)

图4-13



## 总结与展望

经过原理分析与实验探究可见一斑，K8s的资源对象NetworkPolicy在应对容器环境下的“微服务网络隔离”挑战时可以取得不错的效果。其优点包括但不仅限于：

（1）可做应用级（Pod）防护；

（2）较贴合K8s的使用习惯（NetworkPolicy与Service资源对象均通过Lable找到目标Pod）；

（3）功能较为全面（可对以下关系产生作用： “Pod-Pod”“Pod-网段” “Pod-命名空间”）；

（4）兼容性较好（众多K8s网络插件提供了支持；受用户网络技术选型的制约较小；相较于eBPF技术，受系统内核版本影响较小）。

或许是基于对上述的优点的考虑，市面上的容器安全产品的网络隔离常常可见K8s NetworkPolicy的影子，研发人员通常立足于它做技术创新。

K8s NetworkPolicy也有一些不足，例如：

（1）满足大规模复杂网络的隔离需求（各种插件在 NetworkPolicy 的实现上，通常会采用 iptables 的方式，若流量过多，可致使 iptables不堪重负）；

（2）对网络隔离的粒度不够小；

（3）对应用安全、业务安全的保护不够到位。

总的来说，K8s NetworkPolicy有利有弊，但瑕不掩瑜。它在当下以至未来可作为K8s集群网络安全防护的一种有效方式，为保障K8s环境的网络安全发挥重要作用。



## 参考资料

[1]《Kubernetes权威指南》

[2]《十分钟带你理解Kubernetes核心概念》：http://www.dockone.io/article/932

[3]《2.Kubernetes中文社区名词解释：Namespace》：https://www.kubernetes.org.cn/名词解释：namespace

[4]《K8S 网络插件对比》：https://www.jianshu.com/p/d9330360fc8c

[5]《kubeadm快速安装kubernetes v1.14.3 – 第一章》：https://www.ziji.work/kubernetes/kubeadm-installtion-kubernetes1-14-3.html#_Calico

[6]《云原生安全技术报告》：https://www.nsfocus.com.cn/html/2021/101_0204/151.html

[7]《国内首个云上容器ATT&amp;CK攻防矩阵发布，阿里云助力企业容器化安全落地》：https://developer.aliyun.com/article/765449

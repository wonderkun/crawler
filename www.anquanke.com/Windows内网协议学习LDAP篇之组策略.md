> 原文链接: https://www.anquanke.com//post/id/203151 


# Windows内网协议学习LDAP篇之组策略


                                阅读量   
                                **401534**
                            
                        |
                        
                                                                                    



[![](https://p1.ssl.qhimg.com/t01e4bed02d4ea9a806.png)](https://p1.ssl.qhimg.com/t01e4bed02d4ea9a806.png)



## 0x00 前言

这篇文章主要介绍组策略相关的一些内容



## 0x01 组策略基本介绍

组策略可以控制用户帐户和计算机帐户的工作环境。他提供了操作系统、应用程序和活动目录中用户设置的集中化管理和配置。有本机组策略和域的组策略。本机组策略用于计算机管理员统一管理本机以及所有用户，域内的组策略用于域管统一管理域内的所有计算机以及域用户。<br>
在本文中侧重点讲的是域内的组策略。

打开组策略管理(gpms.msc)，可以看到在域林里面有一条条的组策略。如下图，我们可以看到`Default Domain Policy`、`Default Domain Controller Policy`、`财务桌面壁纸`三条组策略。其中前两条是默认的组策略，`财务桌面壁纸`那条组策略是我自己加进去。

[![](https://p3.ssl.qhimg.com/t0174e370a706263a77.png)](https://p3.ssl.qhimg.com/t0174e370a706263a77.png)

对于组策略，我们一般关心两点。
- 这条组策略链接到哪里。
- 这条组策略的内容是啥。
以`Default Domain Policy`为例。

### <a class="reference-link" name="1.%20%E7%BB%84%E7%AD%96%E7%95%A5%E9%93%BE%E6%8E%A5"></a>1. 组策略链接

[![](https://p0.ssl.qhimg.com/t014e7e92e953b0139a.png)](https://p0.ssl.qhimg.com/t014e7e92e953b0139a.png)

在右边的作用域里面，我们可以看到他链接到test.local整个域，也就是说在test.local域内的所有计算机，用户都会受到这条组策略的影响。链接的位置可以是站点，域，以及OU(特别注意，这里没有组，只有OU，至于为啥，可以返回去看组和OU的区别)。又比如说`财务桌面壁纸`这条组策略。他就链接到财务这个OU。

[![](https://p5.ssl.qhimg.com/t01a62772b02471bfff.png)](https://p5.ssl.qhimg.com/t01a62772b02471bfff.png)

加入财务这个OU的所有计算机以及用户会受到影响。

### <a class="reference-link" name="2.%20%E7%BB%84%E7%AD%96%E7%95%A5%E5%86%85%E5%AE%B9"></a>2. 组策略内容

[![](https://p1.ssl.qhimg.com/t01a0593462f7373af7.png)](https://p1.ssl.qhimg.com/t01a0593462f7373af7.png)

我们右键保存报告，可以将组策略的内容导出为htlm。对于`Default Domain Policy`这条组策略，

[![](https://p3.ssl.qhimg.com/t0195cb773145d5bf1a.png)](https://p3.ssl.qhimg.com/t0195cb773145d5bf1a.png)

我们可以看到他配置的一些内容，设置密码最长期限为42天，最短密码长度为7个字符等。如果我们想配置这条组策略的内容，在组策略条目上右键编辑，我们就可以打开组策略编辑器。

[![](https://p0.ssl.qhimg.com/t011a50860410d50e22.png)](https://p0.ssl.qhimg.com/t011a50860410d50e22.png)

我们可以看到左边分为`计算机配置`以及`用户配置`。在里面的配置分别作用于计算机和用户。

在配置底下又分为策略以及首选项。首选项是Windows Server 2008发布后用来对GPO中的组策略提供额外的功能。策略和首选项的不同之处就在于强制性。策略是受管理的、强制实施的。而组策略首选项则是不受管理的、非强制性的。

对于很多系统设置来说，管理员既可以通过**策略设置**来实现，也可以通过**策略首选项**来实现，二者有相当一部分的重叠。

大家自已自己每个条目点一点，看看组策略具体能干嘛，在后面，我们会罗列一些渗透中用于横向或者后门的条目。

### <a class="reference-link" name="3.%20%E7%BB%84%E7%AD%96%E7%95%A5%E6%9B%B4%E6%96%B0"></a>3. 组策略更新

默认情况下，客户端更新组策略的方式主要有
1. 后台轮询，查看sysvol 里面GPT.ini，如果版本高于本地保存的组策略版本，客户端将会更新本地的组策略。轮询的时间是，默认情况下，计算机组策略会在后台每隔 90 分钟更新一次，并将时间作 0 到 30 分钟的随机调整。域控制器上的组策略会每隔 5 分钟更新一次。
1. 计算机开机，用户登录时，查看sysvol 里面GPT.ini，如果版本高于本地保存的组策略版本，客户端将会更新本地的组策略。
<li>客户端强制更新，执行`gupdate /force`。<br>
域控强制客户端更新，执行 `Invoke-GPUpdate -Computer "TESTwin10" -Target "User"`<br>**如果域控制器强制客户端刷新组策略，那么不会比较域共享目录中组策略的版本**
</li>


## 0x02 组策略高级介绍

### <a class="reference-link" name="1.%20%E7%BB%84%E7%AD%96%E7%95%A5%E5%AD%98%E5%82%A8"></a>1. 组策略存储

每条组策略，可以看做是存储在域级别的一个虚拟对象。我们叫做GPO，每个GPO有唯一标志。用来标识每条组策略(或者说每个GPO)

[![](https://p3.ssl.qhimg.com/t01028d34505b4f8aeb.png)](https://p3.ssl.qhimg.com/t01028d34505b4f8aeb.png)

那GPO 在域内的怎么存储的，他分为两个部分。
- GPC
- GPT
GPC 位于LDAP中，`CN=Policies,CN=System,&lt;BaseDn&gt;`底下，每个条目对应一个GPC。

[![](https://p2.ssl.qhimg.com/t010664e0db3a670721.png)](https://p2.ssl.qhimg.com/t010664e0db3a670721.png)

其中包含GPO属性，例如版本信息，GPO状态和其他组件设置

GPC 里面的属性gPCFileSysPath链接到GPT里面。GPT 是是一个文件系统文件夹，其中包含由.adm文件，安全设置，脚本文件以及有关可用于安装的应用程序的信息指定的策略数据。GPT位于域Policies子文件夹中的SysVol中。基本上组策略的配制信息都位于GPT里面。

以`Default Domain Policy`为例。他对应的GPC是`CN=`{`31B2F340-016D-11D2-945F-00C04FB984F9`}`,CN=Policies,CN=System,DC=test,DC=local`,`displayName`是`Default Domain Policy`。

[![](https://p0.ssl.qhimg.com/t0168e6ad81bb69b815.png)](https://p0.ssl.qhimg.com/t0168e6ad81bb69b815.png)

通过`gPCFileSysPath`关联到GPT`\test.localsysvoltest.localPolicies`{`31B2F340-016D-11D2-945F-00C04FB984F9`}``这个文件夹。GPT里面包含了一些策略数据。

[![](https://p1.ssl.qhimg.com/t01fa49a15910a9ae8f.png)](https://p1.ssl.qhimg.com/t01fa49a15910a9ae8f.png)

那在LDAP 是如何体现链接呢。

在域，站点，OU上面有个属性gPLink来标识链接到这里的组策略

[![](https://p1.ssl.qhimg.com/t01cfa627ffcace0e6f.png)](https://p1.ssl.qhimg.com/t01cfa627ffcace0e6f.png)

[![](https://p1.ssl.qhimg.com/t01263a55e2576071e8.png)](https://p1.ssl.qhimg.com/t01263a55e2576071e8.png)

在域，站点，OU上面同样还有个属性gPOptions来标识组策略是否会继承。

[![](https://p5.ssl.qhimg.com/t01ad6989fd83048519.png)](https://p5.ssl.qhimg.com/t01ad6989fd83048519.png)

举个例子，财务这个OU位于test.local 这个域内， Default Domain Policy 这条组策略链接到<br>
test.local 这个域，所以默认情况底下，OU 会继承，这条组策略也同时会作用于财务这个OU，如果我在财务这边选择组织继承，就不会作用域财务这个OU，在LDAP上下的体现就是财务这个OU的属性

[![](https://p2.ssl.qhimg.com/t018e74b3c04bda44a7.png)](https://p2.ssl.qhimg.com/t018e74b3c04bda44a7.png)

### <a class="reference-link" name="2.%20WMI%E7%AD%9B%E9%80%89"></a>2. WMI筛选

在之前，我们通过链接，将组策略链接到站点，工作组，OU。然后作用于链接对象的计算机，用户。但是如果有新的需求，我要作用于部分计算机，用户。比如说作用于所有WIN7 的电脑，这个时候微软提供了另外一项技术，叫WMI筛选。他复用了windows 本身的wmic 技术，每一个建立的WMI筛选器都可以连接到不同的现有组策略对象，一旦产生关联与应用之后，只要组织单位中的目标计算机符合WMI筛选器所设置的条件，那么这项组策略对象将会生效。

举个例子，作用于所有大于Windows 8.1的电脑。

```
Select BuildNumber from Win32_OperatingSystem WHERE BuildNumber &gt;= 9200
```



## 0x03 组策略相关的ACL

我们主要关心以下权限。有个需要注意的是，底下有一些权限是对某个属性的WriteProperty，但是<br>
不管啥属性的WriteProperty，拥有(WriteDacl，WriteOwner，GenericWrite，GenericAll，Full Control)这<br>
些权限，都包括了对某个属性的WriteProperty。为了方便阐述，底下就只写对某个属性的<br>
WriteProperty。不列举出这些通用权限。建议大家对域内的ACL有一定了解，再来看这一小节

### <a class="reference-link" name="1.%20%E5%88%9B%E5%BB%BAGPO%E7%9A%84%E6%9D%83%E9%99%90"></a>1. 创建GPO的权限

创建GPO的权限其实就是对`CN=Policies,CN=System,&lt;BaseDn&gt;`具备CreateChild的权限。

我们可以用adfind 查询域内具备创建GPO的权限。

```
adfind -b CN=Policies,CN=System,DC=test,DC=local -sddl+++ -s base -sdna -sddlfilter ;;"CR CHILD";;;
```

[![](https://p2.ssl.qhimg.com/t0105ee69579827ec3a.png)](https://p2.ssl.qhimg.com/t0105ee69579827ec3a.png)

### <a class="reference-link" name="2.%20GPO%E9%93%BE%E6%8E%A5%E7%9A%84%E6%9D%83%E9%99%90%E3%80%82"></a>2. GPO链接的权限。

之前我们说到在域，站点，OU上面有个属性gPLink来标识链接到这里的组策略。所以我们只要遍历所有的域，站点，OU 上面的所有ACE，如果有对gPLink属性或者gPOpptions属性的修改权限，就可以修改这个这个域/站点/OU链接的OU。这里使用adfind 来演示枚举，其他工具可以自行考证。
1. 枚举域内的所有站点，OU- 遍历站点
在`Configuration` Naming Contex中的过滤规则是`(objectCategory=organizationalUnit)`

```
adfind -b CN=Configuration,DC=test,DC=local -f "(objectCategory=site)" -s subtree -dn
adfind -sites -f "(objectCategory=site)"  -dn
```
- 遍历OU以adfind 以例
过滤规则是`(objectCategory=organizationalUnit)`

```
adfind -b DC=test,DC=local -f "(objectCategory=organizationalUnit)" dn
```
1. 遍历所有的域，站点，OU 上面的所有ACE。这里遍历`财务`这个OU
对gLink或者gPOpptions的WriteProperty权限

```
adfind -b OU=财务,DC=test,DC=local -sddl+++ -s base  -sdna -sddlfilter ;;;gPlink;;
adfind -b OU=财务,DC=test,DC=local -sddl+++ -s base -sdna -sddlfilter ;;;gPOpptions;;
```

### <a class="reference-link" name="3.%20%E4%BF%AE%E6%94%B9%E7%8E%B0%E6%9C%89%E7%9A%84GPO%E7%9A%84%E6%9D%83%E9%99%90"></a>3. 修改现有的GPO的权限

修改现有GPO的权限。

我们主要关心两个
- GPC 链接到GPT 的权限
- 修改GPT的权限
上面提到过，GPC 与 GPT之间的关联是GPC有个属性`gPCFileSysPath`关联到GPT。

[![](https://p2.ssl.qhimg.com/t0117af0d4de9d22c74.png)](https://p2.ssl.qhimg.com/t0117af0d4de9d22c74.png)

我们只需要查找对这个属性的WriteProperty就行。

```
adfind -b CN=Policies,CN=System,DC=test,DC=local nTSecurityDescriptor -sddl+++ -s subtree -sdna -sddlfilter ;;;gPCFileSysPath;; -recmute
```

修改GPT的权限，由于GPT 是文件夹的形式，并不在LDAP里面，因此我们得使用一款能查看文件夹ACL的工具，这里我使用系统自带的icacls。

```
icacls \test.localsysvoltest.localscripts*
icacls \test.localsysvoltest.localpolicies*
```

[![](https://p0.ssl.qhimg.com/t012dd026917fc7849e.png)](https://p0.ssl.qhimg.com/t012dd026917fc7849e.png)

我们看到小明对`31B2F340-016D-11D2-945F-00C04FB984F9`这条组策略的GPT 具有完全控制的权限，前面我们又说到基本上组策略的配制信息都位于GPT里面。因为可以修改GPT，就等同于可以随意修改组策略配置。

可以使用adfind 查看这条组策略的名字

```
adfind -b CN=`{`31B2F340-016D-11D2-945F-00C04FB984F9`}`,CN=Policies,CN=System,DC=test,DC=local -s base displayName
```



## 0x04 SYSVOL 漏洞(MS14-025)

在早期的版本，某些组策略首选项可以存储加密过的密码，加密方式为AES 256，虽然目前AES 256很难被攻破，但是微软选择公开了私钥:)。

[![](https://p2.ssl.qhimg.com/t016b35d9da99ba64ad.png)](https://p2.ssl.qhimg.com/t016b35d9da99ba64ad.png)

主要存在于以下组策略首选项中
- 驱动器映射
- 本地用户和组
- 计划任务
- 服务
- 数据源
如果想复现这个漏洞，在SERVER 2008R2底下。以计划任务为例

[![](https://p0.ssl.qhimg.com/t013ef15da37c75419a.png)](https://p0.ssl.qhimg.com/t013ef15da37c75419a.png)

然后我们在普通成员机器上就可以通过查看GPT看到加密后的密码

[![](https://p5.ssl.qhimg.com/t018166a64e6bf7d1db.png)](https://p5.ssl.qhimg.com/t018166a64e6bf7d1db.png)

进行解密，解密脚本网上挺多的，大家可以自行查找

[![](https://p2.ssl.qhimg.com/t018121ca992016d3e9.png)](https://p2.ssl.qhimg.com/t018121ca992016d3e9.png)

在实际渗透，我们可以通过以下命令来快速搜索

```
findstr /S cpassword \test.orgsysvol*.xml
```



## 0x05 利用组策略扩展

在拿到域控之后，有时候可能网络ACL 到达不了目标电脑，可以通过组策略进行横向。下面列举几种横向的方法。

### <a class="reference-link" name="1.%20%E5%9C%A8%E2%80%9C%E8%BD%AF%E4%BB%B6%E5%AE%89%E8%A3%85%E2%80%9D%E4%B8%8B%E6%8E%A8%E5%87%BA.msi"></a>1. 在“软件安装”下推出.msi

[![](https://p3.ssl.qhimg.com/t0147b28fa5d10ab2b2.png)](https://p3.ssl.qhimg.com/t0147b28fa5d10ab2b2.png)

### <a class="reference-link" name="2.%20%E6%8E%A8%E5%87%BA%E7%89%B9%E5%AE%9A%E7%9A%84%E5%90%AF%E5%8A%A8%E8%84%9A%E6%9C%AC"></a>2. 推出特定的启动脚本

[![](https://p2.ssl.qhimg.com/t0152d9efcbf147d953.png)](https://p2.ssl.qhimg.com/t0152d9efcbf147d953.png)

### <a class="reference-link" name="3.%20%E8%AE%A1%E5%88%92%E4%BB%BB%E5%8A%A1"></a>3. 计划任务

[![](https://p3.ssl.qhimg.com/t014183bb7782bc4ce4.png)](https://p3.ssl.qhimg.com/t014183bb7782bc4ce4.png)



## 0x06 组策略后门的一些思路

组策略很适合用于留后门，下面列举几种留后门的方式

### <a class="reference-link" name="1.%20%E5%B0%86%E5%9F%9F%E5%B8%90%E6%88%B7%E6%B7%BB%E5%8A%A0%E5%88%B0%E6%9C%AC%E5%9C%B0%E7%AE%A1%E7%90%86%E5%91%98/%20RDP%E7%BB%84%EF%BC%8C"></a>1. 将域帐户添加到本地管理员/ RDP组，

[![](https://p2.ssl.qhimg.com/t0142daf4f6efd21bf6.png)](https://p2.ssl.qhimg.com/t0142daf4f6efd21bf6.png)

### <a class="reference-link" name="2.%20%E6%B7%BB%E5%8A%A0%E7%89%B9%E6%9D%83"></a>2. 添加特权

可以通过组策略给某个用户授予特权。<br>
我们用的比较多的有SeEnableDelegationPrivilege特权，详情可以看这个地方<br>
SeEnableDelegationPrivilege

### <a class="reference-link" name="3.%20%E9%99%8D%E7%BA%A7%E5%87%AD%E6%8D%AE%E4%BF%9D%E6%8A%A4"></a>3. 降级凭据保护

[![](https://p0.ssl.qhimg.com/t01b040ac4a8ac4178f.png)](https://p0.ssl.qhimg.com/t01b040ac4a8ac4178f.png)

### <a class="reference-link" name="4.%20%E7%94%9A%E8%87%B3%E6%9B%B4%E6%94%B9%E7%8E%B0%E6%9C%89%E7%9A%84%E5%AE%89%E5%85%A8%E7%AD%96%E7%95%A5%E4%BB%A5%E5%90%AF%E7%94%A8%E6%98%8E%E6%96%87%E5%AF%86%E7%A0%81%E6%8F%90%E5%8F%96%E3%80%82"></a>4. 甚至更改现有的安全策略以启用明文密码提取。

微软很早就更新了补丁来防止获取高版本windows的明文密码，但是可以修改注册表…<br>
使 HKEY_LOCAL_MACHINESYSTEMCurrentControlSetControlSecurityProvidersWDigest下的UseLogonCredentiald的键值为1

[![](https://p1.ssl.qhimg.com/t01b035a4eb6a185f46.png)](https://p1.ssl.qhimg.com/t01b035a4eb6a185f46.png)

### <a class="reference-link" name="5.%20%E7%BB%84%E7%AD%96%E7%95%A5ACL%20%E5%90%8E%E9%97%A8"></a>5. 组策略ACL 后门

在我们之前组策略相关的ACL里面有提到三种特权
1. 创建GPO的权限
1. GPO链接OU的权限。
1. 修改现有的GPO的权限
除了在渗透中可以用于发现域内的安全隐患，也可以用于留后门，比如赋予某个用户创建GPO ，以及链接到域的权限，那么这个用户其实就等效于域管了。或者赋予某个用户拥有对某条GPO修改的权限，比如拥有修改Default Domain Policy的权限，那么这个用户就可以授予别的用户SeEnableDelegationPrivilege的权限，这个后门相对比较灵活，大家可以自己扩展。



## 0x08 引用
- [域渗透——利用GPO中的计划任务实现远程执行](https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-%E5%88%A9%E7%94%A8GPO%E4%B8%AD%E7%9A%84%E8%AE%A1%E5%88%92%E4%BB%BB%E5%8A%A1%E5%AE%9E%E7%8E%B0%E8%BF%9C%E7%A8%8B%E6%89%A7%E8%A1%8C/)
- [域渗透-利用SYSVOL还原组策略中保存的密码](https://3gstudent.github.io/3gstudent.github.io/%E5%9F%9F%E6%B8%97%E9%80%8F-%E5%88%A9%E7%94%A8SYSVOL%E8%BF%98%E5%8E%9F%E7%BB%84%E7%AD%96%E7%95%A5%E4%B8%AD%E4%BF%9D%E5%AD%98%E7%9A%84%E5%AF%86%E7%A0%81/)
- [组策略API](https://docs.microsoft.com/en-us/previous-versions/windows/desktop/policy/group-policy-start-page)
- [https://github.com/FSecureLABS/SharpGPOAbuse](https://github.com/FSecureLABS/SharpGPOAbuse)
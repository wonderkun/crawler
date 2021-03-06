> 原文链接: https://www.anquanke.com//post/id/196510 


# Windows内网协议学习LDAP篇之域用户和计算机用户介绍


                                阅读量   
                                **1212877**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                    



[![](https://p1.ssl.qhimg.com/t01e4bed02d4ea9a806.png)](https://p1.ssl.qhimg.com/t01e4bed02d4ea9a806.png)



作者：daiker@360RedTeam

## 0x00 前言

这篇文章主要介绍AD里面的域用户，计算机用户。



## 0x01 域用户

### 1. 查询域用户

当我们拥有一个域用户的时候，想要枚举域内的所有用户，主要有两个方法。

(1) 通过SAMR 协议查询

samr 也不算是一种专门的协议，就是一个RPC接口(这里简单地提一下。后面在RPC篇里面详细介绍这个RPC接口)

我们平时使用的net user /domain就是使用samr 进行查询的。

[![](https://p2.ssl.qhimg.com/t018c6fd3bd4c6ef7a1.png)](https://p2.ssl.qhimg.com/t018c6fd3bd4c6ef7a1.png)

[![](https://p2.ssl.qhimg.com/t01d107c16808abfd22.png)](https://p2.ssl.qhimg.com/t01d107c16808abfd22.png)

在impacket 里面有一个脚本samrdump.py就是专门调用samr 去查询域用户的。

[![](https://p5.ssl.qhimg.com/t018028b408c5d194aa.png)](https://p5.ssl.qhimg.com/t018028b408c5d194aa.png)

(2) 通过Ldap 语法查询

域用户存储于活动目录数据库里面，对其他用户可见。可以通过Ldap 去查询。

过滤语法如下

```
(&amp;(objectCategory=person)(objectClass=user))
```

[![](https://p4.ssl.qhimg.com/t014941fa87a014a8c8.png)](https://p4.ssl.qhimg.com/t014941fa87a014a8c8.png)

[![](https://p2.ssl.qhimg.com/t01eb716a3d86ac3472.png)](https://p2.ssl.qhimg.com/t01eb716a3d86ac3472.png)

### 2. 域用户部分属性介绍
<li>
● 相关的用户名</li>
[![](https://p0.ssl.qhimg.com/t01e758a060febfa6d5.png)](https://p0.ssl.qhimg.com/t01e758a060febfa6d5.png)

这些属性在LDAP 里面都可以查看

（1）姓对应的属性就是sn

[![](https://p4.ssl.qhimg.com/t016c9fef00b33a758a.png)](https://p4.ssl.qhimg.com/t016c9fef00b33a758a.png)

（2） 名对应的属性是giveName

[![](https://p2.ssl.qhimg.com/t01f453345c0ad7081d.png)](https://p2.ssl.qhimg.com/t01f453345c0ad7081d.png)

（3）展示名，对应的属性是displayName。

[![](https://p4.ssl.qhimg.com/t01ea42cdbe36e24d86.png)](https://p4.ssl.qhimg.com/t01ea42cdbe36e24d86.png)

[![](https://p3.ssl.qhimg.com/t01d7a7f559f834fe2e.png)](https://p3.ssl.qhimg.com/t01d7a7f559f834fe2e.png)

值得注意的是，displayName不能用于登陆，虽然跟域用户名往往一样。但是这个不是直接用于登陆的我们登陆用的账号，在一些公司里面，displayName往往是中文，登陆的用户名是拼音。登陆的格式有以下两种格式。

[![](https://p4.ssl.qhimg.com/t0188d6994cbdbc4240.png)](https://p4.ssl.qhimg.com/t0188d6994cbdbc4240.png)

（4）第一种格式是UserPrincipalName，我们简称为UPN，一般的格式是用户名@域名这样的格式。

比如这里就是lisi@test.local

[![](https://p5.ssl.qhimg.com/t01e2811e15d3228c71.png)](https://p5.ssl.qhimg.com/t01e2811e15d3228c71.png)

[![](https://p0.ssl.qhimg.com/t01b73488011e5e86a7.png)](https://p0.ssl.qhimg.com/t01b73488011e5e86a7.png)

（5） 第二种格式是域名\sAMAccountName这种格式

比如这里就是test.local\lisi，这里的域名可以是netbios名，也可以是dns 名。

[![](https://p1.ssl.qhimg.com/t01595f47ef69ceef69.png)](https://p1.ssl.qhimg.com/t01595f47ef69ceef69.png)

[![](https://p4.ssl.qhimg.com/t011ca5405da92980fc.png)](https://p4.ssl.qhimg.com/t011ca5405da92980fc.png)


<li>
● 用户相关的一些时间
<ul data-mark="-">
- · whenCreated
- · pwdLastSet
- · Lastlogon
看名字就可以大约猜出这些字段的含义了。账号创建时间，设置密码时间，上次登录时间，这些属性任意域用户都可以看的到。

[![](https://p0.ssl.qhimg.com/t01e4f40a06b74baebe.png)](https://p0.ssl.qhimg.com/t01e4f40a06b74baebe.png)

只是这个并不直观，adfind 提供了转化。

[![](https://p4.ssl.qhimg.com/t01191e56d60c6d910b.png)](https://p4.ssl.qhimg.com/t01191e56d60c6d910b.png)

这样更直观一点

[![](https://p0.ssl.qhimg.com/t01f824a499187bbbd1.png)](https://p0.ssl.qhimg.com/t01f824a499187bbbd1.png)

值得注意的是Lastlogon这个属性值在不同的域控制器上是不会同步的。所以要查询一个用户的最后登录时间，得指定不同的域控制器来查询。

在上一篇，讲位操作的时候有简单提及到这个userAccountControl，其实这个属性至关重要。在整个系列文章里面反复提及。userAccountControl对应的位如下。

[![](https://p2.ssl.qhimg.com/t014df9519f018df4a7.png)](https://p2.ssl.qhimg.com/t014df9519f018df4a7.png)

我们可以利用ldap的位操作(关于Ldap的位操作见[Windows内网协议学习LDAP篇之组和OU介绍](https://www.anquanke.com/post/id/195737))来一个个过滤。

比如，我们想查询查询密码永不过期的用户。

[![](https://p1.ssl.qhimg.com/t01461760288349e774.png)](https://p1.ssl.qhimg.com/t01461760288349e774.png)

[![](https://p0.ssl.qhimg.com/t01a2c4d034684a042b.png)](https://p0.ssl.qhimg.com/t01a2c4d034684a042b.png)

又比如，我们想查询设置了约束委派的用户。

[![](https://p0.ssl.qhimg.com/t01e117778c9f171747.png)](https://p0.ssl.qhimg.com/t01e117778c9f171747.png)

[![](https://p5.ssl.qhimg.com/t01b5137b62844c9a49.png)](https://p5.ssl.qhimg.com/t01b5137b62844c9a49.png)

又比如，我们想查询域内设置了对委派敏感的用户。

[![](https://p5.ssl.qhimg.com/t01e07d11b4d72c67f4.png)](https://p5.ssl.qhimg.com/t01e07d11b4d72c67f4.png)

[![](https://p4.ssl.qhimg.com/t0162b49a36e774d790.png)](https://p4.ssl.qhimg.com/t0162b49a36e774d790.png)

等等等。大家可以查表，然后更改对应的十进制值来过滤。



## 0x02 机器用户

默认情况底下，加入域的机器默认在CN=Computer这个容器里面，域控默认在Domain Controllers这个OU里面。有些域内会通过redircmp进行修改

[![](https://p1.ssl.qhimg.com/t01556863664fc3e42d.png)](https://p1.ssl.qhimg.com/t01556863664fc3e42d.png)

### 1. 机器用户跟system 用户的关系

考虑到这样一个场景，如果拿到一台域内机器，然后发现没有域内用户。 这个时候有很多人用mimikatz 抓一下，没抓到域用户，就束手无策了。

我们随便点开一台Domain Computer，这里以WIN7这台机子做为测试。

[![](https://p2.ssl.qhimg.com/t01bdbdc91687c4d3d7.png)](https://p2.ssl.qhimg.com/t01bdbdc91687c4d3d7.png)

我们看他的对象类。

[![](https://p2.ssl.qhimg.com/t01aef09a6b19f7a1de.png)](https://p2.ssl.qhimg.com/t01aef09a6b19f7a1de.png)

发现他是computer 类的实例。

而computer 类的user 类的子类。域用户是user类的实例。之前我们说过类是属性的集合。子类继承了父类的所有属性，因此域用户该有的属性，计算用户都有，甚至我们可以说，机器用户就是一种域用户。

那回到之前的那个问题，如果拿到一台域内机器，然后发现没有域内用户的情况。我们上面说了，机器用户其实就是一个域用户，那我们怎么使用这个机器用户呢。其实本地用户SYSTEM就对应于域内的机器用户，在域内的用户名就是机器名+$,比如win7，他的机器名是WIN7，那他在域内的登录名就是win7$,关于sAMAccountName我们在上一小节已经讲了。

[![](https://p4.ssl.qhimg.com/t018f4edb0f65df5216.png)](https://p4.ssl.qhimg.com/t018f4edb0f65df5216.png)

所以我们可以将当前用户提到system(非管理员需要配合提权漏洞，管理员组的非administrators需要bypassuac，administrator提到system。这个网上有很多方法，psexec，mimikatz等等)。就可以在域内充当机器用户了。

[![](https://p5.ssl.qhimg.com/t01359b16a3619b6b69.png)](https://p5.ssl.qhimg.com/t01359b16a3619b6b69.png)

或者直接抓hash 也是一样的。

[![](https://p3.ssl.qhimg.com/t018ea38fc7e5c8d9cc.png)](https://p3.ssl.qhimg.com/t018ea38fc7e5c8d9cc.png)

### 2. 查找域内的所有机器

可以通过objectclass=Computer或者objectcategory=Computer查找域内的所有机器

[![](https://p0.ssl.qhimg.com/t01e35b57896aaad99b.png)](https://p0.ssl.qhimg.com/t01e35b57896aaad99b.png)

adfind 对查询计算机，提供了一些快捷方式。

[![](https://p1.ssl.qhimg.com/t011f6d61516131b3a2.png)](https://p1.ssl.qhimg.com/t011f6d61516131b3a2.png)

[![](https://p0.ssl.qhimg.com/t016d99391843f63892.png)](https://p0.ssl.qhimg.com/t016d99391843f63892.png)

域内的域控都在Domain Controller这个OU底下，可以通过查看这个OU里面的机器来找到域内的所有域控。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t0123cb663229836662.png)

adfind 对查询域控，也提供了一些快捷方式。

[![](https://p5.ssl.qhimg.com/t01a86d45d667736a9d.png)](https://p5.ssl.qhimg.com/t01a86d45d667736a9d.png)

[![](https://p2.ssl.qhimg.com/t0122e276146c7b2402.png)](https://p2.ssl.qhimg.com/t0122e276146c7b2402.png)

[![](https://p0.ssl.qhimg.com/t01a6cdd3bdf2ed54b6.png)](https://p0.ssl.qhimg.com/t01a6cdd3bdf2ed54b6.png)



## 0x03 域用户账户与机器用户的对应关系

### 1. 域用户默认能登录域内的任何一台普通机器

如果我们是自己搭建过域环境的话，应该会知道，默认情况底下，域用户是能够登录域内的任何一台机器用户的。我们在这里面探究一下原因。

在域成员机器的本地安全策略里面，默认情况底下，本地用户组允许本地登录。其中包括Users组。

[![](https://p4.ssl.qhimg.com/t01fae424a1729a3d42.png)](https://p4.ssl.qhimg.com/t01fae424a1729a3d42.png)

其中Users组包括Domain Users。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t014c059b18478db24c.png)

而域内用户默认都在Domain Users组里面。

因为域用户默认都在Domain Users组里面，而Domain Users在Users组里面。默认情况底下Users组内的成员允许本地登录。所以域内成员默认都能登录域内任何一台机器。

对于这种情况，很多域内都没有解决这个问题。而有些域内运维意识到这个问题。一般会有这两种修改方案。

(1) 在域用户这边做限制

[![](https://p4.ssl.qhimg.com/t0183042ce3b6e82148.png)](https://p4.ssl.qhimg.com/t0183042ce3b6e82148.png)

设置域用户只允许登录到某台机器。

(2) 在机器这边做限制

这个可以通过下发组策略实现。

因为一般都会把常登陆这台机器的域用户加入到Administrators组里面。不允许User组里面用户本地登录。把下图的Users删除掉。这样登陆这台机器的域用户，因为在Administrators组里面，也可以登录。而其他域用户也不能登录。

[![](https://p4.ssl.qhimg.com/t01fae424a1729a3d42.png)](https://p4.ssl.qhimg.com/t01fae424a1729a3d42.png)

### 2. 查看域用户能够登录的主机

域用户默认能本地登录域内的任何一台主机。为了缓解这个问题。上一小节我们提出了两种解决方案。也会带来新的问题。我们可以根据这个找到域用户能够登录的主机。限制了域用户只能登录到某台主机之后，在LDAP里面，会设置一个字段，userWorkStation。这个字段保存了这个域用户只能登录到某台机器。而这个字段对于域内任何用户都是可读的，我们可以通过读域用户的userWorkStation来查看域用户限制登录到那一台机子。那个用户也就能够登录那台机子。

[![](https://p3.ssl.qhimg.com/t019504263021e8e453.png)](https://p3.ssl.qhimg.com/t019504263021e8e453.png)

### 3. 查看域用户正在登陆的主机

当我们想寻找一个域用户正在登陆的主机的情况下，主要有以下几种方式
<li>检查远程机器注册表项里HKEY_USERS来查询谁正在登陆机器比如我们远程登录SERVER12的注册表，看到HKEY_USERS底下的key有S-1-5-21-1909611416-240434215-3714836602-1113，将S-1-5-21-1909611416-240434215-3714836602-1113这个sid转化为用户名是TEST\maria，就可以看到用户TEST\maria当前正在SERVER12这台机器上登录。[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0125436dc9baeaeb6d.png)远程查看注册表项这个操作可以通过API实现，我们可以遍历域内所有机器，查询机器正在登陆的用户。值得注意的有:
<ul data-mark="-">
1. (1) 默认PC机器，是没有开启注册表远程连接的。Server 机器，默认开启远程连接。
1. (2) 域内任何用户，即使配置了，不能本地登录域内机器A，但是只要域内机器A开启远程注册表连接，我们就可以连接上机器A的注册表，从而枚举正在登陆的用户
</ul>
</li>
<li>利用 NetSessionEnum 来寻找登陆的网络会话。一个win32 API，关于这个API的细节可以看官方文档[NetSessionEnum function](https://docs.microsoft.com/en-us/windows/win32/api/lmshare/nf-lmshare-netsessionenum)。
<pre class="pure-highlightjs"><code class="hljs cpp">NET_API_STATUS NET_API_FUNCTION NetSessionEnum(
  LMSTR   servername,
  LMSTR   UncClientName,
  LMSTR   username,
  DWORD   level,
  LPBYTE  *bufptr,
  DWORD   prefmaxlen,
  LPDWORD entriesread,
  LPDWORD totalentries,
  LPDWORD resume_handle
);</code></pre>
这个API 的第一个参数servername ，可以指定一个远程的机器A，会去调用远程机器A的RPC。然后返回其他用户在访问机器A的网络资源（例如文件共享）时所创建的网络会话，可以看到这个用户来自何处。比如我们访问DC2016，会看到kangkang和jane 正在连接DC2016，而kangkang来自172.16.103.131,jane来自172.16.103.128[![](https://p3.ssl.qhimg.com/t0120cc8a6465bb5758.png)](https://p3.ssl.qhimg.com/t0120cc8a6465bb5758.png)
值得注意的有:
(1) 我们指定了servername 为机器A，并不能查询谁谁登陆了机器A，但是可以看到访问机器A的网络资源（例如文件共享）时所创建的网络会话。这个网络会话可以看到哪个域用户来自哪个IP，比如kangkang来自172.16.103.131，所以我们一般指定servername为域控或者文件共享服务器。
(2) 调用此函数的用户，指定了servername 为机器A，并不需要在机器A 上有管理员权限。所以域内任何用户都可以调用此函数，指定了servername 为域控。
</li>
<li>利用NetWkstaUserEnum列出当前登录到该机器的所有用户的信息同样的，这也是一个WIN32 API，关于这个API的细节可以看官方文档[NetWkstaUserEnum function](https://docs.microsoft.com/en-us/windows/win32/api/lmwksta/nf-lmwksta-netwkstauserenum)
<pre class="pure-highlightjs"><code class="hljs cpp">NET_API_STATUS NET_API_FUNCTION NetWkstaUserEnum(
  LMSTR    servername,
  IN DWORD level,
  LPBYTE   *bufptr,
  IN DWORD prefmaxlen,
  LPDWORD  entriesread,
  LPDWORD  totalentries,
  LPDWORD  resumehandle
);</code></pre>
这个API 的第一个参数servername 可以指定一个远程的机器A，会去调用远程机器A的RPC。然后返回当前登录到机器A的所有用户的信息.值得注意的是，调用该函数的用户需要具备机器A的本地管理员权限。
</li>
有一些现有的工具用来枚举正在登陆某台机子的用户(一般称为枚举会话)，其实本质上还是利用我们上面说的方法。这里举例几个

(1) psloggedon.exe

[![](https://p4.ssl.qhimg.com/t01799916ea2ad56a53.png)](https://p4.ssl.qhimg.com/t01799916ea2ad56a53.png)

（2) netsess.exe

[![](https://p2.ssl.qhimg.com/t01c83aa26a11c85938.png)](https://p2.ssl.qhimg.com/t01c83aa26a11c85938.png)

（3） PVEFindADUser.exe

[![](https://p4.ssl.qhimg.com/t010252498e75ffad23.png)](https://p4.ssl.qhimg.com/t010252498e75ffad23.png)

(4) hunter.exe

[![](https://p3.ssl.qhimg.com/t015a5d5c875ff061d5.png)](https://p3.ssl.qhimg.com/t015a5d5c875ff061d5.png)

### 4. 查看域用户登录过的主机
<li>通过查看outlook的邮件头当用户a 在公司内部使用outlook 给你发一封邮件的时候，我们可以在改邮件的头部看到用户a的内网IP[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01d6cb7bc49c182ec0.png)
</li>
1. 导出DC日志。
这个要求我们有域控权限，比如说我们在拿到域控之后想找到域内某个用户的主机。

域内用户A在机器B正常登录的时候，由于本地没有域用户A的hash。机器B会去域控那边做验证，登录成功的话，在域控那边，会有个4624的日志，登录类型为3。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t019076f5c2131d62d9.png)

值得注意的是，在域内可能存在多台域控，日志并不同步，请将每一台域控的日志都导出来。导出日志和查看日志有很多方式，这里提供一个实现。

导出日志，wevtutil是自带的

```
wevtutil epl Security C:\Users\Administrator\Desktop\1.evtx /q:“*[System[(EventID=4624)] and EventData[Data[@Name=‘LogonType’]=‘3’]]” //导出日志
```

将日志拷贝到我们的电脑.使用LogParser开始提取日志

```
LogParser.exe -i:EVT -o:CSV "SELECT TO_UPPERCASE(EXTRACT_TOKEN(Strings,5,'|')) as USERNAME,TO_UPPERCASE(EXTRACT_TOKEN(Strings,18,'|')) as SOURCE_IP FROM 1.evtx" &gt;log.csv // 提取日志
```

[![](https://p4.ssl.qhimg.com/t0199daa16d1f50005e.png)](https://p4.ssl.qhimg.com/t0199daa16d1f50005e.png)



## 0x04 引用
- [● 域内会话收集](https://rcoil.me/2019/10/%5B%E5%9F%9F%E6%B8%97%E9%80%8F%5D%E5%9F%9F%E5%86%85%E4%BC%9A%E8%AF%9D%E6%94%B6%E9%9B%86/)
- [● 域渗透中查询域用户对域成员机器关系](https://xz.aliyun.com/t/1766)
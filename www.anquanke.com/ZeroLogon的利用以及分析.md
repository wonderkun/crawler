> 原文链接: https://www.anquanke.com//post/id/219374 


# ZeroLogon的利用以及分析


                                阅读量   
                                **241562**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">4</a>
                                </b>
                                                                                    



[![](https://p4.ssl.qhimg.com/t01cfde8fd3d83e6e15.png)](https://p4.ssl.qhimg.com/t01cfde8fd3d83e6e15.png)



作者：daiker &amp; wfox [@360Linton](https://github.com/360Linton)-Lab

在今年9月份，国外披露了CVE-2020-1472(又被叫做ZeroLogon)的漏洞详情，网上也随即公开了Exp。是近几年windows上比较重量级别的一个漏洞。通过该漏洞，攻击者只需能够访问域控的445端口，在无需任何凭据的情况下能拿到域管的权限。该漏洞的产生来源于Netlogon协议认证的加密模块存在缺陷，导致攻击者可以在没有凭证的情况情况下通过认证。该漏洞的最稳定利用是调用netlogon中RPC函数NetrServerPasswordSet2来重置域控的密码，从而以域控的身份进行Dcsync获取域管权限。



## 0x00 漏洞的基本利用

首先来谈谈漏洞的利用。

### <a class="reference-link" name="1.%20%E5%AE%9A%E4%BD%8D%E5%9F%9F%E6%8E%A7"></a>1. 定位域控

在我们进入内网之后，首先就是快速定位到域控所在的位置。下面提供几种方法

1、批量扫描389端口。

如果该机器同时开放着135,445,53有很大概率就是域控了，接下来可以通过nbtscan，smbverion，oxid，ldap来佐证

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t013f1f31eeb192f8b3.png)

2、如果知道域名的话，可以尝试通过dns查询

当然这种也有很大的偶然性，需要跟域共享一套DNS，在实战中有些企业内网会这样部署，可以试试。

Linux下命令有

```
dig 域名  ns 
dig _ldap._tcp.域名  srv
```

Windows下命令有

```
nslookup –qt=ns 域名
Nslookup -type=SRV _ldap._tcp.域名
```

[![](https://p5.ssl.qhimg.com/t011c41b4a902e83056.png)](https://p5.ssl.qhimg.com/t011c41b4a902e83056.png)

3、如果我们控制了一台域成员机器，可以直接查询。

​ 以下是一些常见的查询命令

```
net time /domain
net group "Domain controllers" /domain 
dsquery server -o rdn
adfind -sc dclist
Nltest /dclist:域名
```

### <a class="reference-link" name="2.%20%E9%87%8D%E7%BD%AE%E5%9F%9F%E6%8E%A7%E5%AF%86%E7%A0%81"></a>2. 重置域控密码

这里利用[CVE-2020-1472](https://github.com/dirkjanm/CVE-2020-1472)来重置域控密码。注意，这里是域控密码，不是域管的密码。是域控这个机器用户的密码。可能对域不是很熟悉的人对这点不是很了解。在域内，机器用户跟域用户一样，是域内的成员，他在域内的用户名是机器用户+$(如DC2016\$)，在本地的用户名是SYSTEM。

机器用户也是有密码的，只不过这个密码我们正常无感，他是随机生成的，密码强度是120个字符，高到无法爆破，而且会定时更新。

我们通过`sekurlsa::logonPasswords`就可以看到机器用户的密码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01323c1b0c6a29829b.png)

在注册表`HKLM\SYSTEM\CurrentControlSet\Services\Netlogon\Parameters`

`DisablePasswordChange`决定机器用户是否定时更新密码，默认是0，定时更新

`MaximumPasswordAge`决定机器用户更新的时间，默认是30天。

[![](https://p0.ssl.qhimg.com/t015a112ef9a10f79ac.png)](https://p0.ssl.qhimg.com/t015a112ef9a10f79ac.png)

接下来开始利用

命令在`python cve-2020-1472-exploit.py 机器名 域控IP`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t019fba9ec14543e30c.png)

这一步会把域控DC2016(即DC2016\$用户)的密码置为空，即hash为`31d6cfe0d16ae931b73c59d7e0c089c0`

接下来使用空密码就可以进行Dcsync(直接登录不行吗？在拥有域控的机器用户密码的情况下，并不能直接使用该密码登录域控，因为机器用户是不可以登录的，但是因为域控的机器用户具备Dcsync特权，我们就可以滥用该特权来进行Dcsync)

这里面我们使用impacket套件里面的`secretsdump`来进行Dcsync。

```
python secretsdump.py   test.local/DC2016\$@DC2016    -dc-ip  192.168.110.16   -just-dc-user test\\administrator -hashes 31d6cfe0d16ae931b73c59d7e0c089c0:31d6cfe0d16ae931b73c59d7e0c089c0
```

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0142bfa3c9c0ab8b19.png)

### <a class="reference-link" name="3.%20%E6%81%A2%E5%A4%8D%E8%84%B1%E5%9F%9F%E7%9A%84%E5%9F%9F%E6%8E%A7"></a>3. 恢复脱域的域控

在攻击过程中，我们将机器的密码置为空，这一步是会导致域控脱域的，具体原因后面会分析。其本质原因是由于机器用户在AD中的密码(存储在ntds.dic)与本地的注册表/lsass里面的密码不一致导致的。所以要将其恢复，我们将AD中的密码与注册表/lsass里面的密码保持一致就行。这里主要有三种方法

1、从注册表/lsass里面读取机器用户原先的密码，恢复AD里面的密码

我们直接通过`reg save`命令 将注册表里面的信息拿回本地，通过secretsdump提取出里面的hash。

[![](https://p1.ssl.qhimg.com/t01fd353a576bcbada6.png)](https://p1.ssl.qhimg.com/t01fd353a576bcbada6.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t014423ac49fbc28229.png)

或者使用mimikatz的`sekurlsa::logonpassword`从lsass里面进行抓取

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01993a0906b8d26671.png)

可以使用[CVE-2020-1472](https://github.com/dirkjanm/CVE-2020-1472)底下的restorepassword.py来恢复

[![](https://p5.ssl.qhimg.com/t017f964d76c9a8fda5.png)](https://p5.ssl.qhimg.com/t017f964d76c9a8fda5.png)

也可使用[zerologon](https://github.com/risksense/zerologon)底下的reinstall_original_pw.py来恢复，这个比较暴力，再打一次，计算密码的时候使用了空密码的hash去计算session_key。

[![](https://p2.ssl.qhimg.com/t019903ff047e8583f0.png)](https://p2.ssl.qhimg.com/t019903ff047e8583f0.png)

可以发现AD里面的密码已经恢复如初了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t015c8a30f063580826.png)

2、从ntds.dict里面读取AD历史密码，然后恢复AD里面的密码

只需要加 secretsdump里面加`-history`参数就行

这个不太稳定，我本地并没有抓到历史密码

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0188410e03bc4e1d10.png)

[![](https://p2.ssl.qhimg.com/t017114cf6196176034.png)](https://p2.ssl.qhimg.com/t017114cf6196176034.png)

3、一次性重置计算机的机器帐户密码。(包括AD，注册表，lsass里面的密码)。

这里使用一个powershell 的cmdlet`Reset-ComputerMachinePassword`,他是微软在计算机脱域的情况下给出的一种解决方案。

可以一次性重置计算机的机器帐户密码。(包括AD，注册表，lsass里面的密码)。

我们用之前dcsync获取的域管权限登录域控。

执行`powershell Reset-ComputerMachinePassword`

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0148d2d8ff673c682e.png)

可以看到三者的hash已经保持一致了

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t01382602bf894cc1c9.png)

[![](https://p4.ssl.qhimg.com/t019c34ab283781e1fe.png)](https://p4.ssl.qhimg.com/t019c34ab283781e1fe.png)

[![](https://p0.ssl.qhimg.com/t0146ad6b44447e3740.png)](https://p0.ssl.qhimg.com/t0146ad6b44447e3740.png)



## 0x01 漏洞分析

### <a class="reference-link" name="1%E3%80%81netlogon%20%E7%94%A8%E9%80%94"></a>1、netlogon 用途

Netlogon是Windows Server进程，用于对域中的用户和其他服务进行身份验证。由于Netlogon是服务而不是应用程序，因此除非手动或由于运行时错误而停止，否则Netlogon会在后台连续运行。Netlogon可以从命令行终端停止或重新启动。其他机器与域控的netlogon通讯使用RPC协议MS-NRPC。

MS-NRPC指定了Netlogon远程协议，主要功能有基于域的网络上的用户和计算机身份验证；为早于Windows 2000备份域控制器的操作系统复制用户帐户数据库；维护从域成员到域控制器，域的域控制器之间以及跨域的域控制器之间的域关系；并发现和管理这些关系。

我们在MS-NRPC的文档里面可以看到为了维护这些功能所提供的RPC函数。机器用户访问这些RPC函数之前会利用本身的hash进行校验，这次的问题就出现在认证协议的校验上。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a1658d9e1eba7894.png)

### <a class="reference-link" name="3%E3%80%81IV%E5%85%A8%E4%B8%BA0%E5%AF%BC%E8%87%B4%E7%9A%84AES_CFB8%E5%AE%89%E5%85%A8%E9%97%AE%E9%A2%98"></a>3、IV全为0导致的AES_CFB8安全问题

来看下AES_CFB8算法的一个安全问题。

首先说下CFB模式的加解密

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0134ae7013f4c14efa.jpg)

CFB是一种分组密码，可以将块密码变为自同步的流密码。

其加解密公式如下

[![](https://p5.ssl.qhimg.com/t019ba1b101ad77abf8.png)](https://p5.ssl.qhimg.com/t019ba1b101ad77abf8.png)

既将明文拆分为N份，C1，C2，C3。

每一轮的密文的计算是，先将上一轮的密文进行加密(在AES_CFB里面是使用AES进行加密)，然后异或明文，得到新一轮的密文。

这里需要用到上一轮的密文，由于第一轮没有上一轮。所以就需要一个初始向量参与运算，这个初始向量我们成为IV。

下面用一张图来具体讲解下。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0126c51140fd814ab2.png)

这里的IV是`fab3c65326caafb0cacb21c3f8c19f68`

明文是`0102030405060708`

第一轮没有上一轮，需要IV参与运算。那么第一轮的运算就是。

[![](https://p1.ssl.qhimg.com/t017d4ec99d3cb78626.png)](https://p1.ssl.qhimg.com/t017d4ec99d3cb78626.png)

E(`fab3c65326caafb0cacb21c3f8c19f68`) = `e2xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

然后e2与明文01异得到密文e3。

第二轮的密文计算是，先将第一轮的密文进行AES加密，然后异或明文，密文。

第一轮的密文就是`(没有fa了)b3c65326caafb0cacb21c3f8c19f68`+`e2`=`b3c65326caafb0cacb21c3f8c19f68e2`

E(`b3c65326caafb0cacb21c3f8c19f68e2`=`9axxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

然后91与明文异或得到密文98

我们用一个表格来表示这个过程(为什么E(fab3c65326caafb0cacb21c3f8c19f68)=`e2xxxxxxxxxxxxxxxxxxxxxxxxxxxxx？这点大家不用关心，AES key不一定，计算的结果也不一定，这里是假设刚好存在某个key使得这个结果成立)

|明文内容|参与AES运算的上一轮密文|E(参与AES运算的上一轮密文)|加密后的密文|
|------
|`01`|`fab3c65326caafb0cacb21c3f8c19f68`|`e2xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`|`01^e2=e3`|
|`02`|`b3c65326caafb0cacb21c3f8c19f68e3`|`9axxxxxxxxxxxxxxxxxxxxxxxxxxxxx`|`02^9a=98`|
|`03`|`c65326caafb0cacb21c3f8c19f68e398`|`f6xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`|`03^f6=f5`

最后就是明文是`0102030405060708`经过八轮运算之后得到`e39855xxxxxxxxxxxxxxxxxxxxxxxxx`

这里有个绕的点是，每一轮计算的值是8位，既0x01,0x02。(每个16进制数4位)。因为是AES_CFB8。

而每轮AES运算的是128位(既16字节),因为这里是AES128。

我们观察每轮`参与AES运算的上一轮密文`。

第一轮是``fab3c65326caafb0cacb21c3f8c19f68`。第二轮的时候是往后移八位，既减去`fa`得到`b3c65326caafb0cacb21c3f8c19f68`，再加上第一轮加密后的密码`e3`得到`b3c65326caafb0cacb21c3f8c19f68`。

这个时候我们考虑一种极端的情况。

当IV为8个字节的0的时候，既IV=`000000000000000000000000000000`

那么新的运算就变成

|明文内容|参与AES运算的上一轮密文|E(参与AES运算的上一轮密文)|加密后的密文|
|------
|`01`|`000000000000000000000000000000`|`a5xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`|`01^a5=a4`|
|`02`|`0000000000000000000000000000a4`|`8bxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`|`02^8b=89`|
|`03`|`00000000000000000000000000a489`|`11xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`|`03^11=12`

大家可以看到`参与AES运算的上一轮密文`的值是不断减去最前面的00，不断加入密文。

只要key固定，那么E(X)的值一定是固定的。

那么是不是在key固定的情况下，只要我保证`参与AES运算的上一轮密文`是固定的，那么`E(参与AES运算的上一轮密文)`一定是固定的。

`参与AES运算的上一轮密文`每轮是怎么变化的。

`000000000000000000000000000000` -&gt; `0000000000000000000000000000a4` -&gt; `00000000000000000000000000a489`。

前面的00不断减少，后面不断加进密文。

那么我是不是只需要保证不断加进来的值是00,`参与AES运算的上一轮密文`就一直是`000000000000000000000000000000`。也就是说现在只要保证每一轮`加密后的密文`是`00`,那么整个表格就不会变化。最后得到的密文就是`000000000000000000000000000000`.。

要保证每一轮`加密后的密文`是`00`,只需要每一轮的`明文内容`和`E(参与AES运算的上一轮密文)的前面8位`一样就行。(两个一样的的数异或为0)

我们来看下这个表格。

|明文内容|参与AES运算的上一轮密文|E(参与AES运算的上一轮密文)|加密后的密文|
|------
|`XY`|`000000000000000000000000000000`|`XYxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`|`XY^XY=00`|
|`XY`|`000000000000000000000000000000`|`XYxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`|`XY^XY=00`|
|`XY`|``000000000000000000000000000000`|`XYxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`|`XY^XY=00`

由于在key固定的情况下，E(000000000000000000000000000000)的值固定，所以`E(参与AES运算的上一轮密文)的前面8位`是固定的，而每一轮的`明文内容`和`E(参与AES运算的上一轮密文)的前面前面8位`一样。所以每一轮的明文内容就必须要一样。所以要求明文的格式就是`XYXYXYXYXYXYXY`这种格式。那么还剩下最后一个问题。假设我们可以控制明文，那么在不知道key的情况下，我们怎么保证`E(000000000000000000000000000000)`的前面8位一定和明文一样呢。

这个地方我们不敢保证，但是前面八位的可能性有2**8=256(`00-FF`)，因为每一位都可能是0或者1。那么也就是说我们运行一次，在不知道key的情况下，`E(000000000000000000000000000000)`的前面8位一定和明文一样的概率是1/256,我们可以通过不断的增加尝试次数，运行到2000次的时候，至少有一次命中的概率已经有99.6%了。(具体怎么算。文章后面会介绍)。

所以我们最后下一个结论。

在AES_CFB8算法中，如果IV为全零。只要我们能控制明文内容为XYXYXYXY这种格式(X和Y可以一样，既每个字节的值都是一样的)，那么一定存在一个key,使得AES_CFB8(XYXYXYXY)=00000000。

### <a class="reference-link" name="4%E3%80%81netlogon%20%E8%AE%A4%E8%AF%81%E5%8D%8F%E8%AE%AE%E7%BB%95%E8%BF%87"></a>4、netlogon 认证协议绕过

说完IV全为0导致的AES_CFB8安全问题，我们来看看netlogon认证协议。

继续看图

[![](https://p0.ssl.qhimg.com/t018b7c797053d32722.png)](https://p0.ssl.qhimg.com/t018b7c797053d32722.png)

1、客户端调用NetrServerReqChallenge向服务端发送一个ClientChallenge

2、服务端向客户端返回送一个ServerChallenge

3、双方都利用client的hash、ClientChallenge、ServerChallenge计算一个session_key。

4、客户端利用session_key和ClientChallenge计算一个ClientCredential。并发送给服务端进行校验。

5、服务端也利用session_key和ClientChallenge去计算一个ClientCredential，如果值跟客户端发送过来的一致，就让客户端通过认证。

这里的计算ClientChallenge使用ComputeNetlogonCredential函数。

有两种算法，分别采用DES_ECB和AES_CFB。可以通过协商flag来选择哪一种加密方式。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0181e74ae2362a1230.png)

[![](https://p2.ssl.qhimg.com/t01bda54b2b262908dd.png)](https://p2.ssl.qhimg.com/t01bda54b2b262908dd.png)

这里存在问题的是AES_CFB8。为了方便理解，我们用一串python代码来表示这个加密过程。

```
# Section 3.1.4.4.1
def ComputeNetlogonCredentialAES(inputData, Sk):
    IV='\x00'*16
    Crypt1 = AES.new(Sk, AES.MODE_CFB, IV)
    return Crypt1.encrypt(inputData)
```

使用AES_CFB8，IV是’\x00’*16，明文密码是ClientChallenge，key是session_key，计算后的密文是ClientCredential。

这里IV是’\x00’*16，我们上面一节得出一个结论。在AES_CFB8算法中，如果IV为全零。只要我们能控制明文内容为XYXYXYXY这种格式(X和Y可以一样，既每个字节的值都是一样的)，那么一定存在一个key,使得AES_CFB8(XYXYXYXY)=00000000。

这里ClientChallenge我们是可以控制的，那么一定就存在一个key，使得ClientCredential为`00000000000000`

那么我们就可以。

1、向服务端发送一个ClientChallenge`00000000000000`(只要满足XYXYXYXY这种格式就行)

2、循环向服务端发送ClientCredential为`00000000000000`，直达出现一个session_key,使得服务端生成的ClientCredential也为`00000000000000`。

还有一个需要注意的环节。

认证的整个协议包里面，默认会增加签名校验。这个签名的值是由session_key进行加密的。但是由于我们是通过让服务端生成的ClientCredential也为`00000000000000`来绕过前面的认证，没有session_key。所以这个签名我们是无法生成的。但是我们是可以取消设置对应的标志位来关闭这个选项的。

在**NegotiateFlags**中。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t0141177427e1748a97.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01a3ecc9b171b6572a.png)

所以在Poc里面作者将flag位设置为0x212fffff

[![](https://p0.ssl.qhimg.com/t0153f14799f17e8683.png)](https://p0.ssl.qhimg.com/t0153f14799f17e8683.png)

在NetrServerAuthenticate里面并没有提供传入`NegotiateFlags`的参数，因此这里我们使用NetrServerAuthenticate3。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01cd5d1f86a7893869.png)

### <a class="reference-link" name="5%E3%80%81%E9%87%8D%E7%BD%AE%E5%AF%86%E7%A0%81%E5%88%A9%E7%94%A8%E5%88%86%E6%9E%90"></a>5、重置密码利用分析

前面的认证都通过之后，我们就可以利用改漏洞来重置密码，为啥一定是该漏洞，有没有其他的方法，后面会介绍。这里着重介绍重置密码的函数。

在绕过认证之后，我们就可以调用RPC函数了。作者调用的是RPC函数NetrServerPasswordSet2。

```
NTSTATUS NetrServerPasswordSet2(
   [in, unique, string] LOGONSRV_HANDLE PrimaryName,
   [in, string] wchar_t* AccountName,
   [in] NETLOGON_SECURE_CHANNEL_TYPE SecureChannelType,
   [in, string] wchar_t* ComputerName,
   [in] PNETLOGON_AUTHENTICATOR Authenticator,
   [out] PNETLOGON_AUTHENTICATOR ReturnAuthenticator,
   [in] PNL_TRUST_PASSWORD ClearNewPassword
 );
```

调用这个函数需要注意两个地方。

1)、一个是Authenticator。

如果我们去看NRPC里面的函数，会发现很多函数都需要这个参数。这个参数也是一个校验。在前面的校验通过，建立通道之后，还会校验Authenticator。

[![](https://p2.ssl.qhimg.com/t019aa23f1e97163cbf.png)](https://p2.ssl.qhimg.com/t019aa23f1e97163cbf.png)

我们去文档看看Authenticator怎么生成的

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t013d1d9d513a059619.png)

这里面我们不可控的参数是是使用ComputeNetlogonCredential计算ClientStoreCredentail+TimeNow,这这里的ComputeNetlogonCredential跟之前一样，之前我们指定了AES_CFB8，这里也就是AES_CFB8。而ClientStoreCredentail的值我们是可控的，TimeNow的值我们也是可控的。我们只要控制其加起来的值跟我们之前指定的ClientChallenge一样(session_key 跟之前的一样，之前指定的是`00000000000000`)，就可以使得最后的Authenticator为`0000000000000000`，最后我们指定Authenticator为`0000000000000000`就可以绕过Authenticator 的校验。

2)、另外一个是ClearNewPassword

我们用一段代码来看看他是怎么计算的

```
indata = b'\x00' * (512-len(self.__password)) + self.__password + pack('&lt;L', len(self.__password))
request['ClearNewPassword'] = nrpc.ComputeNetlogonCredential(indata, self.sessionKey)
```

也是使用之前的ComputeNetlogonCredential来计算的。密码结构包含516个字节，最后的4个字节指明了密码长度。前面的512字节是填充值加密码。这里的填充值是’\x00’，事实上，这个是任意的。我们只要控制indata的值跟我们之前指定的ClientChallenge一样(session_key 跟之前的一样，其实也不是完全一样，最后的ClearNewPassword跟之前的ClientCredential长度不一样，所以indata也得是(len(ClearNewPassword)/len(ClientChallenge))**ClientChallenge,之前指定的ClientChallenge为`00000000000000`，这里也就是`‘\x00’\**516`)，就可以使得最后的ClearNewPassword全为0。



## 0x02 常见的几个问题

### <a class="reference-link" name="1%E3%80%81%20%E4%B8%BA%E4%BD%95%E6%9C%BA%E5%99%A8%E7%94%A8%E6%88%B7%E4%BF%AE%E6%94%B9%E5%AE%8C%E5%AF%86%E7%A0%81%E4%B9%8B%E5%90%8E%E4%BC%9A%E8%84%B1%E5%9F%9F"></a>1、 为何机器用户修改完密码之后会脱域

dirkjanm 在[https://twitter.com/_dirkjan/status/1306280553281449985](https://twitter.com/_dirkjan/status/1306280553281449985)已经说的很清楚了。最主要的原因是AD里面存储的机器密码跟本机的Lsass里面存储的密码不一定导致的。这里简单翻译一下。

正常情况下，AD运行正常。有一个DC和一个服务器。他们彼此信任是因为他们有一个共享的Secret：机器帐户密码。他们可以使用它彼此通讯并建立加密通道。两台机器上的共享Secret是相同的。

[![](https://p1.ssl.qhimg.com/t01ea3bc52bded1f7b1.png)](https://p1.ssl.qhimg.com/t01ea3bc52bded1f7b1.png)

尝试登录服务器的用户可以通过带有服务票证的Kerberos进行登录。该服务票证由DC使用机器帐户密码加密。

服务器具有相同的Secret，可以解密票证并知道其合法性。用户获得访问权限。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t017354f43187053b8e.png)

借助Zerologon攻击，攻击者可以更改AD中计算机帐户的密码，从而在一侧更改Secret。

现在，服务器无法再在域上登录。在大多数情况下，服务器仍将具有有效的Kerberos票证，因此某些登录仍将起作用。

[![](https://p5.ssl.qhimg.com/t0142ff4b6bfce972bf.png)](https://p5.ssl.qhimg.com/t0142ff4b6bfce972bf.png)

在漏洞利用之前发出的Kerberos票证仍然可以使用，但是新的票证将由AD使用新密钥（以蓝色显示）进行加密。服务器无法解密(因为使用了Lsass里面的密码hash去进行解密，这个加密用的不一致)这些文件并抛出错误。后续Kerberos登录也随即无效。

[![](https://p2.ssl.qhimg.com/t01627d00f90e7f4ddc.jpg)](https://p2.ssl.qhimg.com/t01627d00f90e7f4ddc.jpg)

NTLM的登录也不行，因为使用AD帐户登录已通过安全通道（通过相同的netlogon协议zerologon滥用）在DC上进行了验证。

但是无法建立此通道，因为信任中断，并且服务器再次引发错误。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014a3b7374281f7e3c.png)

但是，在最常见的特权升级中，将目标DC本身而不是另一台服务器作为目标。这很有趣，因为现在它们都在单个主机上运行。

但这并没有完全不同，因为DC也有多个存储凭据的位置。

像服务器一样，DC拥有一个带有密码的机器帐户，该帐户以加密方式存储在注册表中。引导时将其加载到lsass中。如果我们使用Zerologon更改密码，则仅AD中的密码会更改，而不是注册表或lsass中的密码。

[![](https://p3.ssl.qhimg.com/t01c19f25fd1b52ef1f.png)](https://p3.ssl.qhimg.com/t01c19f25fd1b52ef1f.png)

利用后，每当发出新的Kerberos票证时，我们都会遇到与服务器相同的问题。 DC无法使用lsass中的机器帐户密码来解密服务票证，并且无法使用Kerberos中断身份验证。

[![](https://p0.ssl.qhimg.com/t017986e590b2497f13.png)](https://p0.ssl.qhimg.com/t017986e590b2497f13.png)

对于NTLM，则有所不同。在DC上，似乎没有使用计算机帐户，但是通过另一种方式（我尚未调查过）验证了NTLM登录，该方式仍然有效。

这使您可以使用DC计算机帐户的空NT哈希值进行DCSync。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t0109d85f2dffc55967.png)

如果您真的想使用Kerberos，我想（未经测试）它可以与2个DC一起使用。 DC之间的同步可能会保持一段时间，因为Kerberos票证仍然有效。

因此，一旦将DC1的新密码同步到DC2，就可以使用DC1的帐户与DC1同步。

[![](https://p0.ssl.qhimg.com/t0107b2654802130095.png)](https://p0.ssl.qhimg.com/t0107b2654802130095.png)

之所以起作用，是因为DC2的票证已使用DC2机器帐户的kerberos密钥进行了加密，而密钥没有更改。

### <a class="reference-link" name="2%E3%80%81%20%E8%84%9A%E6%9C%AC%E9%87%8C%E9%9D%A22000%E6%AC%A1%E5%A4%B1%E8%B4%A5%E7%9A%84%E6%A6%82%E7%8E%87%E6%98%AF0.04%E6%98%AF%E6%80%8E%E4%B9%88%E7%AE%97%E7%9A%84"></a>2、 脚本里面2000次失败的概率是0.04是怎么算的

在作者的利用脚本里面，我们注意到这个细节。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01eda03db6db91dfaf.png)

作者说平均256次能成功，最大的尝试次数是2000次，失败的概率是0.04。那么这个是怎么算出来的呢。

一个基本的概率问题。每一次成功的概率都是1/256，而且每一次之间互不干扰。那么运行N次，至少一次成功的概率就是`1-(255/256)**N`

那么运行256次成功的概率就是

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01b7b7dbd4d4ad3632.png)

运行2000次成功的概率就是

[![](https://p0.ssl.qhimg.com/t011882feccc581c531.png)](https://p0.ssl.qhimg.com/t011882feccc581c531.png)

### <a class="reference-link" name="3%E3%80%81NRPC%E9%82%A3%E4%B9%88%E5%A4%9A%E5%87%BD%E6%95%B0%EF%BC%8C%E6%98%AF%E4%B8%8D%E6%98%AF%E4%B8%80%E5%AE%9A%E5%BE%97%E9%87%8D%E7%BD%AE%E5%AF%86%E7%A0%81"></a>3、NRPC那么多函数，是不是一定得重置密码

已经绕过了netlogon的权限校验，那么netlogon里面的RPC函数那么多，除了重置密码，有没有其他更优雅的函数可以用来利用呢。

我们可以在API文档里面开始寻觅。

[![](https://p3.ssl.qhimg.com/t016001b7def4de7542.png)](https://p3.ssl.qhimg.com/t016001b7def4de7542.png)

事实上，在impacket里面的`impacket/tests/SMB_RPC/test_nrpc.py`里面已经基本实现了调用的代码，我们只要小做修改，就可以调用现有的代码来做测试。

我们将认证部分，从账号密码登录替换为我们的Poc

```
def connect(self):
        if self.rpc_con == None:
            print('Performing authentication attempts...')
            for attempt in range(0, self.MAX_ATTEMPTS):
                self.rpc_con = try_zero_authenticate(self.dc_handle, self.dc_ip, self.target_computer)
                if self.rpc_con == None:
                    print('=', end='', flush=True)
                else:
                    break
        return self.rpc_con
```

将Authenticator的实现部分也替换下就行。

```
def update_authenticator(self):
        authenticator = nrpc.NETLOGON_AUTHENTICATOR()
        # authenticator['Credential'] = nrpc.ComputeNetlogonCredential(self.clientStoredCredential, self.sessionKey)
        # authenticator['Timestamp'] = 10
        authenticator['Credential'] = b'\x00' * 8
        authenticator['Timestamp'] = 0
        return authenticator
```

然后其他地方根据报错稍微修改就可以了。我们开始一个个做测试。

[![](https://p2.ssl.qhimg.com/t015024914ba832d336.png)](https://p2.ssl.qhimg.com/t015024914ba832d336.png)

这块基本是查看信息。

[![](https://p5.ssl.qhimg.com/t0126986a1f6b79db9c.png)](https://p5.ssl.qhimg.com/t0126986a1f6b79db9c.png)

虽然可以调用成功，但是对我们的利用帮助不大。

[![](https://p4.ssl.qhimg.com/t0114daef10a7063de5.png)](https://p4.ssl.qhimg.com/t0114daef10a7063de5.png)

这块基本是是建立安全通道的，设置密码已经使用了，除去认证，设置密码，还有一个查看密码。遗憾的是EncryptedNtOwfPassword是使用sesson_key 参与加密的，我们不知道sesson_key，也就无法解密。

[![](https://p5.ssl.qhimg.com/t01c33cc5fde3f4ef53.png)](https://p5.ssl.qhimg.com/t01c33cc5fde3f4ef53.png)

其他的函数整体试了下，也没有找到几个比较方便直接提升到域管权限的。大家可以自行寻觅。

事实上，dirkjanm也研究了一种无需重置密码，借助打印机漏洞relay来利用改漏洞的方法，但是由于Rlay在实战中的不方便性，整体来说并不比重置密码好用，这里不详细展开，大家可以自行查看文章[A different way of abusing Zerologon (CVE-2020-1472)](https://dirkjanm.io/a-different-way-of-abusing-zerologon/)。

### <a class="reference-link" name="4%E3%80%81%E6%98%AF%E4%B8%8D%E6%98%AF%E5%8F%AA%E6%9C%89IV%20%E5%85%A8%E4%B8%BA%E9%9B%B6%E6%89%8D%E6%98%AF%E5%8D%B1%E9%99%A9%E7%9A%84"></a>4、是不是只有IV 全为零才是危险的

在之前的分析中，只要`参与AES运算的上一轮密文`每一轮保存不变就行，第一轮的`参与AES运算的上一轮密文`就是IV。也就是说，存在一个IV，只要他能够保持最前面8位不断移到最后，如AA(XXXXXX) -&gt; (XXXXXX)AA，值保持不变，就一定存在一个key,使得AES_CFB8(XYXYXYXY)=`IV*(len(明文)/len(IV))`(这里乘以`(len(明文)/len(IV)`是因为密文长度跟明文一样，不一定跟IV一样)。显然IV 全为零满足这个条件，但是不止是IV 全为零才有这个安全问题。

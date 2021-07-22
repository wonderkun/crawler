> 原文链接: https://www.anquanke.com//post/id/245482 


# 利用MS-SAMR协议修改/重置用户密码


                                阅读量   
                                **105450**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                    



[![](https://p3.ssl.qhimg.com/t0177f12f5954fa96ad.jpg)](https://p3.ssl.qhimg.com/t0177f12f5954fa96ad.jpg)

> 本文为Windows RPC利用系列文章的第一篇，主要介绍关于MS-SAMR的部分利用，在后续的文章中将继续介绍RPC在渗透测试中的应用

作者: Loong716[@Amulab](https://github.com/Amulab)

在渗透测试过程中，经常遇到拿到用户的NTLM哈希但无法解密出明文密码的情况。本文介绍并分析一种在仅知道域用户密码哈希时修改用户密码，并在使用完后恢复用户原密码的方法。完成相应工具实现，提出检测方法和缓解措施。

PS：本文提出的场景在实战中也有很多其他的解决办法，但本文仅讨论与changentlm、setntlm相关的内容

## 0x00 利用

考虑以下几个场景：
1. 我们拿下域控后，经常要搜集目标架构内用户的各种信息来寻找靶标，比如登录邮箱服务器、OA、NAS等可能使用域身份认证的系统
1. 我们收集的攻击路径中的其中一环是利用某账户重置/修改目标账户密码
1. 我们拿到某用户hash后，同样想通过该用户账户登录某系统，但目标系统不支持pth
我们虽然拿到了修改/重置密码的权限，但我们又不想直接修改目标用户的密码，因为这样用户在登录时就会发现自己的密码被修改了，此时有两种情况：
1. 如果我们有重置密码权限就可以使用`SetNTLM`来将用户密码重置
1. 如果有hash的话可以使用`ChangeNTLM`修改
登录目标系统后，再将目标密码还原

### <a class="reference-link" name="1.%20SetNTLM"></a>1. SetNTLM

该功能的效果是直接将域用户的密码或hash重置为新的密码或hash

#### <a class="reference-link" name="(1)%20%E5%88%A9%E7%94%A8%E6%9D%A1%E4%BB%B6"></a>(1) 利用条件

当前身份对要修改的用户有`Reset Password`权限

[![](https://p1.ssl.qhimg.com/t0121d961b290dfb3a7.png)](https://p1.ssl.qhimg.com/t0121d961b290dfb3a7.png)

#### <a class="reference-link" name="(2)%20Demo"></a>(2) Demo

假设我们此时拿到域控，想修改域内用户`ntlmtest`的密码来登录某系统，先Dcsync看一下用户当前的hash：

[![](https://p0.ssl.qhimg.com/t01ee0f7772ecf2a833.png)](https://p0.ssl.qhimg.com/t01ee0f7772ecf2a833.png)

由于我们是域管了，基本上对目标用户都是有重置密码权限的，然后利用以下命令重置密码：

```
lsadump::setntlm /server:&lt;DC's_IP_or_FQDN&gt; /user:&lt;username&gt; /password:&lt;new_password&gt;
```

[![](https://p3.ssl.qhimg.com/t01d2a00b59829414c6.png)](https://p3.ssl.qhimg.com/t01d2a00b59829414c6.png)

登录目标系统以后，再通过以下命令还原密码：

```
lsadump::setntlm /server:&lt;DC's_IP_or_FQDN&gt; /user:&lt;username&gt; /ntlm:&lt;Original_Hash&gt;
```

[![](https://p3.ssl.qhimg.com/t01f47cec7305549f7f.png)](https://p3.ssl.qhimg.com/t01f47cec7305549f7f.png)

### <a class="reference-link" name="2.%20ChangeNTLM"></a>2. ChangeNTLM

#### <a class="reference-link" name="(1)%20%E5%88%A9%E7%94%A8%E6%9D%A1%E4%BB%B6"></a>(1) 利用条件

需要对目标用户有`Change Password`权限，但该权限一般是`Everyone`拥有的，所以基本上拿到目标用户的hash/密码后都可以进行密码更改

[![](https://p4.ssl.qhimg.com/t012dd34fb3341ac4c3.png)](https://p4.ssl.qhimg.com/t012dd34fb3341ac4c3.png)

（注意此处的更改密码权限并不是说可以直接任意改用户密码，而是在知道用户的密码的情况下更改一个新密码）

该方法受到域内密码策略的限制，比如域内默认的**“密码最短使用期限”**为1天，因此用户每天只能修改一次自己的密码

而且如果域内存在**“强制密码历史”**规则时，该方法在恢复原密码时便不能成功，但如果没有**“密码最短使用期限”**的限制的话，我们多修改几次密码直到原密码在历史中清除，然后再修改为原密码即可

[![](https://p4.ssl.qhimg.com/t015105183efc29dd2f.png)](https://p4.ssl.qhimg.com/t015105183efc29dd2f.png)

#### <a class="reference-link" name="(2)%20Demo"></a>(2) Demo

修改用户test2密码：

```
lsadump::changentlm /server:&lt;DC's_IP_or_FQDN&gt; /user:&lt;username&gt; /old:&lt;current_hash&gt; /newpassword:&lt;newpassword&gt;
```

[![](https://p1.ssl.qhimg.com/t01ebe80c4f1d701e07.png)](https://p1.ssl.qhimg.com/t01ebe80c4f1d701e07.png)

恢复原密码：

```
lsadump::changentlm /server:&lt;DC's_IP_or_FQDN&gt; /user:&lt;username&gt; /oldpassword:&lt;current_password_plain_text&gt; /new:&lt;original_hash&gt;
```

[![](https://p1.ssl.qhimg.com/t01983f4a57dadf8957.png)](https://p1.ssl.qhimg.com/t01983f4a57dadf8957.png)



## 0x01 原理

ChangeNTLM和SetNTLM的原理本质都是调用[MS-SAMR](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/4df07fab-1bbc-452f-8e92-7853a3c7e380)协议

不同的是ChangeNTLM是调用`SamrChangePasswordUser`这一API来修改用户密码：

[![](https://p3.ssl.qhimg.com/t010a23755c3216dc81.png)](https://p3.ssl.qhimg.com/t010a23755c3216dc81.png)

而SetNTLM是通过`SamrSetInformationUser`来重置用户密码

[![](https://p1.ssl.qhimg.com/t013b1f83f30bd3c8a6.png)](https://p1.ssl.qhimg.com/t013b1f83f30bd3c8a6.png)

大体过程是差不多的，只不过核心操作调用API不同，这也是为什么两种方法需要的参数、权限都不同，此处以分析ChangeNTLM为例

虽然原理本质是通过调用RPC，但mimikatz并不是直接调用RPC来修改，而是使用了一组以`Sam`开头的API，下图所示为部分API：

[Mimikatz – kuhl_m_lsadump.c#L2267](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_lsadump.c#L2267)

[![](https://p5.ssl.qhimg.com/t01c5a18fe4a00c4db2.png)](https://p5.ssl.qhimg.com/t01c5a18fe4a00c4db2.png)

最终调用`SamiChangePasswordUser`来修改用户的密码

[Mimikatz – kuhl_m_lsadump.c#L2171](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_lsadump.c#L2171)

[![](https://p5.ssl.qhimg.com/t0148dfcf08a3ec5b6e.png)](https://p5.ssl.qhimg.com/t0148dfcf08a3ec5b6e.png)

这些API由samlib.dll导出：

[![](https://p2.ssl.qhimg.com/t017938b565162f0bc5.png)](https://p2.ssl.qhimg.com/t017938b565162f0bc5.png)

查看`SamiChangePasswordUser`函数调用树，可以看到调用了`NdrClientCall3`，是不是很熟悉？这明显是进行RPC调用的标志（xpn在他的文章[exploring-mimikatz-part-2](https://blog.xpnsec.com/exploring-mimikatz-part-2/)里有提到过）

[![](https://p5.ssl.qhimg.com/t01b318a75b029af254.png)](https://p5.ssl.qhimg.com/t01b318a75b029af254.png)

我们再看一下调用处的反编译代码，参数刚好可以和`SamrChangePasswordUser`的操作数对应

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01f8af5cd5e550ffdb.png)

其实从流量中也可以看出调用的是MS-SAMR协议：

[![](https://p3.ssl.qhimg.com/t0166caa54b0dd04648.png)](https://p3.ssl.qhimg.com/t0166caa54b0dd04648.png)



## 0x02 实现

实现主要有两种思路，一种是跟mimikatz一样直接调用samlib.dll的导出函数，第二种是直接调用SAMR协议的API

两种方法原理一样，但前者的调用要更加简单，因为samlib里的导出函数对应了SAMR的API，其实相当于SAMR的上层实现，比如`SamiChangePasswordUser`对应`SamrChangePasswordUser`，并且参数更加简化

整个过程调用的API作用如下：
<li>
**SamrConnect5**: 获取Server对象的句柄</li>
<li>
**SamrEnumerateDomainsInSamServer**: 枚举Server上的域名</li>
<li>
**SamrLookupDomainInSamServer**: 获取域名对应域的SID</li>
<li>
**SamrOpenDomain**: 获取Domain对象的句柄</li>
<li>
**SamrLookupNamesInDomain**: 获取指定用户的RID</li>
<li>
**SamrOpenUser**: 获取User对象的句柄</li>
<li>
**SamrChangePasswordUser**: 修改用户对象的密码</li>
### <a class="reference-link" name="1.%20%E8%B0%83%E7%94%A8samlib%E7%9A%84%E5%AF%BC%E5%87%BA%E5%87%BD%E6%95%B0"></a>1. 调用samlib的导出函数

原理前面已经提过了，直接调用samlib.dll里对应的导出函数即可，~~直接嫖~~参考mimikatz的源码即可实现，[源码戳这里](https://github.com/loong716/CPPPractice/tree/master/Set_ChangeNTLM)

### <a class="reference-link" name="2.%20%E7%9B%B4%E6%8E%A5%E8%B0%83%E7%94%A8MS-SAMR"></a>2. 直接调用MS-SAMR

这里以实现changentlm为例，setntlm同理

#### <a class="reference-link" name="(1)%20C%E8%AF%AD%E8%A8%80"></a>(1) C语言

微软官方已经把MS-SAMR的IDL给我们了：[[MS-SAMR] – Appendix A: Full IDL](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/1cd138b9-cc1b-4706-b115-49e53189e32e)，直接拿下来使用midl生成.h和.c文件即可（使用时还需要稍作修改）：

[![](https://p4.ssl.qhimg.com/t010302144d36a55531.png)](https://p4.ssl.qhimg.com/t010302144d36a55531.png)

注意这里有一个坑点，如果对`SamrChangePasswordUser`只指定第5、6、7个参数的话，会产生`STATUS_LM_CROSS_ENCRYPTION_REQUIRED`错误：

[![](https://p1.ssl.qhimg.com/t0190889ca3f6b78adc.png)](https://p1.ssl.qhimg.com/t0190889ca3f6b78adc.png)

因此必须再指定`LMCross`和`NewLmEncryptedWithNewNt`这两个参数，而后者是用新密码的NTLM Hash加密新密码的LM Hash得到的，这里我一开始很疑惑：从mimikatz的功能来看，并不需要我们传递新密码LM Hash，那么它这个加密操作是怎么完成的呢？

由于LM Hash早已在高版本Windows中弃用，于是我猜测这个LM Hash可能跟新密码并没有关系（比如有些工具需要使用`LMHASH:NTHASH`的格式来指定hash，但LM Hash的值是多少并没有关系），于是我直接使用新密码的NTLM Hash来加密空密码对应的LM Hash：

```
...
unsigned char newLM[16];
PCWCHAR newLMHash = "AAD3B435B51404EEAAD3B435B51404EE";
StringToHex(newLMHash, newLM, sizeof(newLM));
status = RtlEncryptLmOwfPwdWithLmOwfPwd(newLM, newNT, &amp;NewLMEncryptedWithNewNT);
if (!NT_SUCCESS(status))
`{`
    wprintf(L"[!] Calc NewLMEncryptedWithNewNT Error: %08X\n", status);
    exit(1);
`}`
...
```

最终成功修改目标用户的密码，Demo实现效果如下，[源码戳这里](https://github.com/loong716/CPPPractice/tree/master/ChangeNTLM_SAMR)

[![](https://p5.ssl.qhimg.com/t012dcd4a64e6f20b10.png)](https://p5.ssl.qhimg.com/t012dcd4a64e6f20b10.png)

#### <a class="reference-link" name="(2)%20Impacket"></a>(2) Impacket

既然是调用RPC，而且刚好impacket对SAMR协议也有实现，所以也可以用impacket来写

完成后我向impacket项目提交了[Pull Request](https://github.com/SecureAuthCorp/impacket/pull/1097)，源码可以在commit中看到

效果如下，修改用户的密码：

[![](https://p5.ssl.qhimg.com/t0188171ca03f6f2947.png)](https://p5.ssl.qhimg.com/t0188171ca03f6f2947.png)

恢复用户原hash：

[![](https://p5.ssl.qhimg.com/t01b0a4869661e5e6b9.png)](https://p5.ssl.qhimg.com/t01b0a4869661e5e6b9.png)



## 0x03 检测与缓解

### <a class="reference-link" name="1.%20ChangeNTLM"></a>1. ChangeNTLM

#### <a class="reference-link" name="(1)%20%E4%BA%A7%E7%94%9F%E4%BA%8B%E4%BB%B6"></a>(1) 产生事件

ChangeNTLM会产生4723、4738两条日志，并且日志中的使用者和目标账户并不是同一个账户：

[![](https://p4.ssl.qhimg.com/t01bb3ce64d05e8cc46.png)](https://p4.ssl.qhimg.com/t01bb3ce64d05e8cc46.png)

[![](https://p5.ssl.qhimg.com/t01fc82fa2cf1bc7400.png)](https://p5.ssl.qhimg.com/t01fc82fa2cf1bc7400.png)

#### <a class="reference-link" name="(2)%20%E6%B5%81%E9%87%8F%E7%89%B9%E5%BE%81"></a>(2) 流量特征

在`SamrOpenUser`这个操作中（操作数为34），`Samr User Access Change Password`标志位被设置为1，在该步操作中还可以看到用户对应的RID：

[![](https://p0.ssl.qhimg.com/t016638f24fc98ebaab.png)](https://p0.ssl.qhimg.com/t016638f24fc98ebaab.png)

以及调用`SamrChangePasswordUser`（操作数为38）：

[![](https://p0.ssl.qhimg.com/t0183a1695b2d645f24.png)](https://p0.ssl.qhimg.com/t0183a1695b2d645f24.png)

### <a class="reference-link" name="2.%20SetNTLM"></a>2. SetNTLM

#### <a class="reference-link" name="(1)%20%E4%BA%A7%E7%94%9F%E4%BA%8B%E4%BB%B6"></a>(1) 产生事件

SetNTLM会产生4724、4661、4738这三条日志：

[![](https://p0.ssl.qhimg.com/t010df37f8d484ad733.png)](https://p0.ssl.qhimg.com/t010df37f8d484ad733.png)

[![](https://p0.ssl.qhimg.com/t0105e99e9c2538ecdd.png)](https://p0.ssl.qhimg.com/t0105e99e9c2538ecdd.png)

[![](https://p5.ssl.qhimg.com/t01c69270133b229ad3.png)](https://p5.ssl.qhimg.com/t01c69270133b229ad3.png)

#### <a class="reference-link" name="(2)%20%E6%B5%81%E9%87%8F%E7%89%B9%E5%BE%81"></a>(2) 流量特征

同样在`SamrOpenUser`这个操作中（操作数为34），`Samr User Access Set Password`标志位被设置为1，也可以看到用户对应的RID：

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t0181a936a003383ef8.png)

调用`SamrSetUserInformation`（操作数为37）:

[![](https://p2.ssl.qhimg.com/t0130489ae3c50d047b.png)](https://p2.ssl.qhimg.com/t0130489ae3c50d047b.png)

### <a class="reference-link" name="3.%20%E7%BC%93%E8%A7%A3%E6%8E%AA%E6%96%BD"></a>3. 缓解措施

对于ChangeNTLM，我们可以通过设置域内密码策略来增大攻击者的利用难度：
- “密码最短使用期限” &gt;= 1天
- “强制密码历史” &gt;= 5个
而对于SetNTLM，基本是攻击者拿到较高权限时才会进行的操作，因此主要靠我们前期的一些用户实体行为来检测攻击者的行为，即使其拿到高权限，我们也可以通过事件迅速检测出SetNTLM行为。



## 0x04 参考

[https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/4df07fab-1bbc-452f-8e92-7853a3c7e380](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-samr/4df07fab-1bbc-452f-8e92-7853a3c7e380)

[https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_lsadump.c#L2165](https://github.com/gentilkiwi/mimikatz/blob/master/mimikatz/modules/kuhl_m_lsadump.c#L2165)

[https://stealthbits.com/blog/manipulating-user-passwords-with-mimikatz/](https://stealthbits.com/blog/manipulating-user-passwords-with-mimikatz/)

> 原文链接: https://www.anquanke.com//post/id/249603 


# 使用PetitPotam代替Printerbug


                                阅读量   
                                **43791**
                            
                        |
                        
                                                                                    



[![](https://p2.ssl.qhimg.com/t010500b2188e8a5018.jpg)](https://p2.ssl.qhimg.com/t010500b2188e8a5018.jpg)

> 上帝关了一扇, 必定会再为你打开另一扇窗

## 0x00 前言

Printerbug使得拥有控制域用户/计算机的攻击者可以指定域内的一台服务器，并使其对攻击者选择的目标进行身份验证。虽然不是一个微软承认的漏洞，但是跟Net-ntlmV1,非约束委派，NTLM_Relay,命名管道模拟这些手法的结合可以用来域内提权，本地提权，跨域等等利用。

遗憾的是，在PrintNightmare爆发之后，很多企业会选择关闭spoolss服务，使得Printerbug失效。在Printerbug逐渐失效的今天，PetitPotam来了，他也可以指定域内的一台服务器，并使其对攻击者选择的目标进行身份验证。而且在低版本(16以下)的情况底下，可以匿名触发。

[![](https://p0.ssl.qhimg.com/t019ccf05e6d7242783.png)](https://p0.ssl.qhimg.com/t019ccf05e6d7242783.png)



## 0x01 原理

`MS-EFSR`里面有个函数EfsRpcOpenFileRaw(Opnum 0)

```
long EfsRpcOpenFileRaw(
   [in] handle_t binding_h,
   [out] PEXIMPORT_CONTEXT_HANDLE* hContext,
   [in, string] wchar_t* FileName,
   [in] long Flags
 );
```

他的作用是打开服务器上的加密对象以进行备份或还原，服务器上的加密对象由`FileName` 参数指定,`FileName`的类型是UncPath。

当指定格式为`\\IP\C$`的时候，lsass.exe服务就会去访问`\\IP\pipe\srvsrv`

[![](https://p2.ssl.qhimg.com/t0152baeae82102d1a5.png)](https://p2.ssl.qhimg.com/t0152baeae82102d1a5.png)

指定域内的一台服务器，并使其对攻击者选择的目标(通过修改FileName里面的IP参数)进行身份验证。



## 0x02 细节

### <a class="reference-link" name="1%E3%80%81%E9%80%9A%E8%BF%87lsarpc%20%E8%A7%A6%E5%8F%91"></a>1、通过lsarpc 触发

在[官方文档](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-efsr/403c7ae0-1a3a-4e96-8efc-54e79a2cc451)里面，`MS-EFSR`的调用有`\pipe\lsarpc`和`\pipe\efsrpc`两种方法，其中
<li>
`\pipe\lsarpc`的服务器接口必须是UUID [c681d488-d850-11d0-8c52-00c04fd90f7e]</li>
<li>
`\pipe\efsrpc`的服务器接口必须是UUID [df1941c5-fe89-4e79-bf10-463657acf44d]</li>
在我本地测试发现`\pipe\efsrpc`并未对外开放

[![](https://p5.ssl.qhimg.com/t0177ca7000ed39a97f.png)](https://p5.ssl.qhimg.com/t0177ca7000ed39a97f.png)

[![](https://p5.ssl.qhimg.com/t0135bc5df0c45723ea.png)](https://p5.ssl.qhimg.com/t0135bc5df0c45723ea.png)

在PetitPotam的Poc里面有一句注释`possible aussi via efsrpc (en changeant d'UUID) mais ce named pipe est moins universel et plus rare que lsarpc ;)`，翻译过来就是

`也可以通过EFSRPC（通过更改UUID），但这种命名管道的通用性不如lsarpc，而且比LSARPC更罕见`

所以PetitPotam直接是采用lsarpc的方式触发。

### <a class="reference-link" name="2%E3%80%81%E4%BD%8E%E7%89%88%E6%9C%AC%E5%8F%AF%E4%BB%A5%E5%8C%BF%E5%90%8D%E8%A7%A6%E5%8F%91"></a>2、低版本可以匿名触发

在08和12的环境，默认在`网络安全:可匿名访问的命名管道`中有三个`netlogon`、`samr`、`lsarpc`。因此在这个环境下是可以匿名触发的

[![](https://p1.ssl.qhimg.com/t0112f6116a186bc685.png)](https://p1.ssl.qhimg.com/t0112f6116a186bc685.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t014aff1b5cf87d3c5d.png)

遗憾的是在16以上这个默认就是空了，需要至少一个域内凭据。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016ae3eae71c816367.png)



## 0x03 利用

这篇文章的主题是使用`PetitPotam`代替`Printerbug`，因此这个利用同时也是`Printerbug`的利用。这里顺便梳理复习下`Printerbug`的利用。

### <a class="reference-link" name="1%E3%80%81%E7%BB%93%E5%90%88%20CVE-2019-1040%EF%BC%8CNTLM_Relay%E5%88%B0LDAP"></a>1、结合 CVE-2019-1040，NTLM_Relay到LDAP

详情见[CVE-2019-1040](https://daiker.gitbook.io/windows-protocol/ntlm-pian/7#5-cve-2019-1040),这里我们可以将触发源从`Printerbug`换成`PetitPotam`

[![](https://p0.ssl.qhimg.com/t0185776a144d49ba80.png)](https://p0.ssl.qhimg.com/t0185776a144d49ba80.png)

### <a class="reference-link" name="2%E3%80%81Relay%E5%88%B0HTTP"></a>2、Relay到HTTP

不同于LDAP是协商签名的，发起的协议如果是smb就需要修改Flag位，到HTTP的NTLM认证是不签名的。前段时间比较火的ADCS刚好是http接口，又接受ntlm认证，我们可以利用PetitPotam把域控机器用户relay到ADCS里面申请一个域控证书，再用这个证书进行kerberos认证。注意这里如果是域控要指定模板为`DomainController`

```
python3 ntlmrelayx.py -t https://192.168.12.201/Certsrv/certfnsh.asp -smb2support --adcs --template "DomainController"
```

[![](https://p3.ssl.qhimg.com/t0178f676523565f8c4.png)](https://p3.ssl.qhimg.com/t0178f676523565f8c4.png)

### <a class="reference-link" name="2%E3%80%81%E7%BB%93%E5%90%88%E9%9D%9E%E7%BA%A6%E6%9D%9F%E5%A7%94%E6%B4%BE%E7%9A%84%E5%88%A9%E7%94%A8"></a>2、结合非约束委派的利用

当一台机器机配置了非约束委派之后，任何用户通过网络认证访问这台主机，配置的非约束委派的机器都能拿到这个用户的TGT票据。

当我们拿到了一台非约束委派的机器，只要诱导别人来访问这台机器就可以拿到那个用户的TGT，在这之前我们一般用printerbug来触发，在这里我们可以用PetitPotamlai来触发。

[![](https://p0.ssl.qhimg.com/t0195923ef769049c49.png)](https://p0.ssl.qhimg.com/t0195923ef769049c49.png)

[![](https://p2.ssl.qhimg.com/t01ca45b7bbde357b1e.png)](https://p2.ssl.qhimg.com/t01ca45b7bbde357b1e.png)

域内默认所有域控都是非约束委派，因此这种利用还可用于跨域。

### <a class="reference-link" name="3%E3%80%81%E7%BB%93%E5%90%88Net-ntlmV1%E8%BF%9B%E8%A1%8C%E5%88%A9%E7%94%A8"></a>3、结合Net-ntlmV1进行利用

很多企业由于历史原因，会导致LAN身份验证级别配置不当，攻击者可以将Net-Ntlm降级为V1

[![](https://p5.ssl.qhimg.com/t018d1d629477a5b3f1.png)](https://p5.ssl.qhimg.com/t018d1d629477a5b3f1.png)

我们在Responder里面把Challeng设置为`1122334455667788`,就可以将Net-ntlm V1解密为ntlm hash

[![](https://p1.ssl.qhimg.com/t015c487497c8328f2a.png)](https://p1.ssl.qhimg.com/t015c487497c8328f2a.png)

[![](https://p1.ssl.qhimg.com/t01993318956a134c96.png)](https://p1.ssl.qhimg.com/t01993318956a134c96.png)

[![](https://p3.ssl.qhimg.com/t01e9d9d3f6fe85522c.png)](https://p3.ssl.qhimg.com/t01e9d9d3f6fe85522c.png)

### <a class="reference-link" name="4%E3%80%81%E7%BB%93%E5%90%88%E5%91%BD%E5%90%8D%E7%AE%A1%E9%81%93%E7%9A%84%E6%A8%A1%E6%8B%9F"></a>4、结合命名管道的模拟

在这之前，我们利用了printerbug放出了pipePotato漏洞。详情见[pipePotato：一种新型的通用提权漏洞](https://www.anquanke.com/post/id/204510)。

在PetitPotam出来的时候，发现这个RPC也会有之前pipePotato的问题。

[![](https://p5.ssl.qhimg.com/t0121c14068b62f3ddf.png)](https://p5.ssl.qhimg.com/t0121c14068b62f3ddf.png)

[![](https://p5.ssl.qhimg.com/t019db8d465a7b0ba81.png)](https://p5.ssl.qhimg.com/t019db8d465a7b0ba81.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01cbd3dca3b88b7170.png)



## 0x04 引用
<li>
[[MS-EFSR]: Encrypting File System Remote (EFSRPC) Protocol](https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-efsr/08796ba8-01c8-4872-9221-1000ec2eff31)–[PetitPotam](https://github.com/topotam/PetitPotam)
</li>
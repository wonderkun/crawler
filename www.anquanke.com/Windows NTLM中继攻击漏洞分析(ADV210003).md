> 原文链接: https://www.anquanke.com//post/id/250190 


# Windows NTLM中继攻击漏洞分析(ADV210003)


                                阅读量   
                                **20184**
                            
                        |
                        
                                                                                    



[![](https://p3.ssl.qhimg.com/t0177c25c37a144864b.jpg)](https://p3.ssl.qhimg.com/t0177c25c37a144864b.jpg)



作者：sidney@安恒AiLPHA

## 0x01漏洞信息

近日，安恒信息AiLPHA安全团队监测到微软发布了Windows NTLM 中继攻击漏洞（ADV210003）缓解通告。此漏洞允许攻击者强制域控制器向指定机器进行NTLM身份认证，未经身份认证的攻击者可利用此漏洞发起NTLM中继攻击并接管Windows域。

通过漏洞复现分析，可以发现漏洞本质是EfsRpcOpenFileRaw 方法用于打开服务器上的加密对象以进行备份或还原。它分配必须通过调用EfsRpcCloseRaw 方法释放的资源。当指定格式为\IP\C$的时候，lsass.exe服务就会去访问\IP\pipe\srvsrv，其中就会使域控发起对其他主机的NTLM请求认证。当域内存在Active Directory 证书服务器时，攻击者利用该漏洞发起NTLM请求认证，通过获取到的base64证书, 生成TGT从而获取到域控管理员hash,最后利用hash登录接管域控主机。

参考链接：[https://mp.weixin.qq.com/s/FDZghQ8uYgzorx_ZQRejCw](https://mp.weixin.qq.com/s/FDZghQ8uYgzorx_ZQRejCw)



## 0x02漏洞复现

[![](https://p1.ssl.qhimg.com/t01bc12b6e602e242ab.png)](https://p1.ssl.qhimg.com/t01bc12b6e602e242ab.png)

1、搭建Windows Server2012作为AD域环境，Windows Server2016作为证书服务(AD CS)器，Windows7作为域内被控主机，kali作为攻击机。

[![](https://p2.ssl.qhimg.com/t0198e1bdf53a78a268.png)](https://p2.ssl.qhimg.com/t0198e1bdf53a78a268.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01153b098109b7d083.png)

2、利用impacket中的脚本ntlmrelayx.py设置NTLM中继。将DC(Windows)的凭据中继到启用了Web 注册的Active Directory 证书服务器中。

[![](https://p4.ssl.qhimg.com/t019bbc92fe6e1d4b8e.png)](https://p4.ssl.qhimg.com/t019bbc92fe6e1d4b8e.png)

3、利用漏洞利用工具PetitPotam触发域控到监听主机的NTLM身份认证请求。

[![](https://p2.ssl.qhimg.com/t015e63e9dd4186bc17.png)](https://p2.ssl.qhimg.com/t015e63e9dd4186bc17.png)

4、执行漏洞利用工具PetitPotam后，监听主机收到NTLM身份认证请求，获取Base64 PKCS12证书。

[![](https://p4.ssl.qhimg.com/t013873a9f0e5a1dfb3.png)](https://p4.ssl.qhimg.com/t013873a9f0e5a1dfb3.png)

5、 利用Rubeus获取TGT并导入到当前进程。

[![](https://p4.ssl.qhimg.com/t01e15ba2c2fb8d3d5d.png)](https://p4.ssl.qhimg.com/t01e15ba2c2fb8d3d5d.png)

6、使用lsadump::dcsync /user:Administrator导出域控管理员NTLM哈希。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0157064a56035cab62.png)

7、 使用wmicexc.py进行连接，即可远程控制域控。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t015937aca280641ad8.png)



## 0x03 POC分析

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t017b3846e7e354ab2a.png)

通过阅读POC的说明文档，结合POC进行简要分析。可以得知POC主要有以下几部分。<br>
1、 实例化认证函数。

[![](https://p3.ssl.qhimg.com/t012028b83701337611.png)](https://p3.ssl.qhimg.com/t012028b83701337611.png)

2、远程连接，里面涉及远程rpc绑定。

[![](https://p3.ssl.qhimg.com/t018e1c26fed02e4d15.png)](https://p3.ssl.qhimg.com/t018e1c26fed02e4d15.png)

3、 发起efsrpc请求。其中根据RROR_BAD_NETPATH判断成功，错误存在则为成功。

[![](https://p1.ssl.qhimg.com/t019fab9339a536ee0d.png)](https://p1.ssl.qhimg.com/t019fab9339a536ee0d.png)

4、断开连接，完成攻击。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t0162b3e6bcc83398df.png)



## 0x04 流量分析

1、首先获取支持的认证的协议。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0194371475e32b77af.png)

2、通过应答获取到支持smb2协议。

[![](https://p0.ssl.qhimg.com/t0150c48cbfe933bfa1.png)](https://p0.ssl.qhimg.com/t0150c48cbfe933bfa1.png)

3、获取具体smb2版本，接着进行NTLM认证,type1 Negotiate协商, 客户端在发起认证时，首先向服务器发送协商消息。 协商需要认证的主体，用户，机器以及需要使用的安全服务等信息。 并通知服务器自己支持的协议内容，加密等级等等。

[![](https://p2.ssl.qhimg.com/t01c91564ffa6b10b57.png)](https://p2.ssl.qhimg.com/t01c91564ffa6b10b57.png)

[![](https://p3.ssl.qhimg.com/t01b1c2c0e96149c40a.png)](https://p3.ssl.qhimg.com/t01b1c2c0e96149c40a.png)

4、返回Type2 消息，Challenge 挑战消息。<br>
服务器在收到客户端的协商消息之后，会读取其中的内容，并从中选择出自己所能接受的服务内容，加密等级，安全服务等等。并生成一个随机数challenge, 然后生成challenge消息返回给客户端

[![](https://p1.ssl.qhimg.com/t0164c51f8acbf79d8b.png)](https://p1.ssl.qhimg.com/t0164c51f8acbf79d8b.png)

5、发出Type3 消息，Authenticate认证消息。<br>
客户端在收到服务端发回的Challenge消息之后， 读取该服务端所支持的内容，和随机数challenge。 决定服务端所支持的内容是否满足自己的要求。 如果满足，则使用自己的密码以及服务器的随机数challenge通过复杂的运算，期间可能需要自己生成一个客户端随机数client challenge也加入运算，并最终生成一个认证消息。并发回给服务器。服务器在收到 Type3的消息之后， 回经过几乎同样的运算，并比较自己计算出的认证消息和服务端发回来的认证消息是否匹配。如果匹配，则证明客户端掌握了正确的密码，认证成功。 允许客户端使用后续服务。如果不匹配，则认证失败。

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01055057ace6a4e8a2.png)

[![](https://p1.ssl.qhimg.com/t01317d0f90e1759edd.png)](https://p1.ssl.qhimg.com/t01317d0f90e1759edd.png)

6、建立远程管道，远程请求lsarpc管道。<br>
在Windows Server2008和Windows Server2012的系统环境中，默认在网络安全:可匿名访问的命名管道中有三个netlogon、samr、lsarpc。因此在该环境下是可以匿名控制域控发起NTLM认证请求的，漏洞工具中的Python脚本和exe文件的攻击方式区别在这块，Python脚本默认发起的请求中无账号相关信息。

[![](https://p0.ssl.qhimg.com/t0128201093c643106b.png)](https://p0.ssl.qhimg.com/t0128201093c643106b.png)

[![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p4.ssl.qhimg.com/t010c7b44830104aa1a.png)

7、通过dcerpc加载Efs服务。

[![](https://p4.ssl.qhimg.com/t012e3eeecb50bddd74.png)](https://p4.ssl.qhimg.com/t012e3eeecb50bddd74.png)

8、调用EfsRpcOpenFileRaw 函数发起请求，访问脚本中listener传入的中的文件。EfsRpcOpenFileRaw 方法用于打开服务器上的加密对象以进行备份或还原。它分配必须通过调用EfsRpcCloseRaw 方法释放的资源。当指定格式为\IP\C$的时候，lsass.exe服务就会去访问\IP\pipe\srvsrv，从而控制域控对外发起NTML认证请求。通过Process Moniter可以查看到lsass.exe访问\IP\pipe\srvsrv。

[![](https://p0.ssl.qhimg.com/t012d49e35a0973b711.png)](https://p0.ssl.qhimg.com/t012d49e35a0973b711.png)

[![](https://p5.ssl.qhimg.com/t0105e1962e3d074a87.png)](https://p5.ssl.qhimg.com/t0105e1962e3d074a87.png)

9、域控发起NTLM认证，即控制域控对外发起NTML认证请求。

[![](https://p2.ssl.qhimg.com/t018a4d2d84acb5e903.png)](https://p2.ssl.qhimg.com/t018a4d2d84acb5e903.png)



## 0x05 总结与防御

通过对该漏洞的复现分析，可以发现该漏洞的利用难度相对较低，其中受影响的协议是NTLM协议。目前需要对该漏洞提高防范措施。

目前鉴于微软官方暂未发布安全更新，建议用户通过临时缓解方法进行防护。

```
微软建议客户在域控制器上禁用NTLM 身份验证。
若暂时无法关闭NTLM，也可采取以下两个步骤的任意一个来缓解影响：使用组策略在域中的任何AD CS服务器上禁用NTLM；在运行Certificate Authority Web Enrollment或者Certificate Enrollment Web Service服务的域中的AD CS服务器上禁用Internet信息服务(IIS)的NTLM。
```

